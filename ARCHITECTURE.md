# ALS SubZero Architecture and Design Specifications

Designed and built by Samin Sami.
ALS stands for "Al Sami", taken from the first three letters of my last name: Samin Yasar **AL S**ami.

This document describes how I built ALS SubZero, including its mathematical foundations, network framing, and software architecture.

## 1. Network delay-line storage theory

In standard computing systems, files sit on physical drives like NVMe SSDs or mechanical hard drives, and temporary files sit in RAM chips. I replaced both with network delay lines.

The storage capacity $C$ of a network link equals its Bandwidth-Delay Product (BDP):

$$C = \text{Bandwidth} \times \text{RTT}$$

For example, a standard 1 Gbps fiber link with a round-trip time (RTT) of 40 milliseconds holds an in-flight capacity of:

$$C = 10^9 \text{ bits/s} \times 0.040 \text{ s} = 40,000,000 \text{ bits} = 5.0 \text{ MB}$$

When my system streams packets to network reflectors and catches their echoes, those bits live inside network routers, switch buffers, and fiber optic lines while in transit.

## 2. Binary frame protocol (ALS1)

Every chunk in ALS SubZero travels inside a 24-byte big-endian binary frame:

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   'A'   |   'L'   |   'S'   |   '1'   |        Inode ID       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Chunk Index          |  FEC Group    | Chunk in Grp  |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Flags     |   Reserved    |        Sequence Number        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|        Payload Length         |        CRC32C Checksum        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                           (cont.)                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     Microsecond Epoch (us)                    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                 Payload Bytes (0 to 1024 bytes)               |
|                               ...                             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Field breakdown

- Magic (4 bytes): ASCII bytes `ALS1`.
- Inode ID (2 bytes): Identifies the file (1 to 65535).
- Chunk Index (2 bytes): Contiguous index of the block within the file.
- FEC Group (1 byte): Index of the Reed-Solomon coding block.
- Chunk in Group (1 byte): Position within the group (0 to K-1 for data, K to K+M-1 for parity).
- Flags (1 byte):
  - Bit 0 (`0x01`): `FLAG_PARITY` (set for parity blocks).
  - Bit 1 (`0x02`): `FLAG_LAST_CHUNK` (marks the last chunk of a file).
  - Bit 2 (`0x04`): `FLAG_RECONSTRUCTED` (set when recovered by the FEC engine).
  - Bit 3 (`0x08`): `FLAG_DIRTY` (marks pending write operations).
- Reserved (1 byte): Set to zero for alignment.
- Sequence Number (2 bytes): Increments by 1 on every network hop.
- Payload Length (2 bytes): Length of payload in bytes (0 to 1024).
- Checksum (4 bytes): CRC32C over the first 16 bytes and payload.
- Epoch (4 bytes): Microsecond timestamp modulo $2^{32}$, used to track hop latency.

## 3. Cauchy Reed-Solomon erasure coding

Early network delay-line projects lost files whenever a single packet dropped. I implemented an erasure coding engine over Galois Field $GF(2^8)$ to stop this problem.

### Galois Field math

The field $GF(2^8)$ uses the irreducible primitive polynomial:

$$P(x) = x^8 + x^4 + x^3 + x^2 + 1 \quad (0x11D = 285)$$

- Addition and subtraction are bitwise XOR (`^`).
- Multiplication and division use precomputed logarithm (`GF_LOG`) and exponential (`GF_EXP`) tables:

$$a \times b = \text{GF\_EXP}[(\text{GF\_LOG}[a] + \text{GF\_LOG}[b]) \pmod{255}]$$

$$a \div b = \text{GF\_EXP}[(\text{GF\_LOG}[a] - \text{GF\_LOG}[b] + 255) \pmod{255}]$$

### Cauchy generator matrix

For a code where $N = K + M$, I construct the generator matrix $G$ as:

$$G = \begin{bmatrix} I_K \\ C \end{bmatrix}$$

Here $I_K$ is the $K \times K$ identity matrix, and $C$ is an $M \times K$ Cauchy matrix with elements:

$$C_{i, j} = \frac{1}{X_i \oplus Y_j}$$

Where $X = \{0, 1, \dots, M-1\}$ and $Y = \{M, M+1, \dots, M+K-1\}$ are disjoint sets in $GF(2^8)$.

Every square submatrix of a Cauchy matrix is non-singular. Any $K$ rows chosen from $G$ create an invertible $K \times K$ matrix. When routers drop up to $M$ packets, my decoder selects the surviving rows, computes their inverse using Gauss-Jordan elimination, and recovers the exact original bytes.

## 4. Recirculation pacer and rate regulation

When packets return over low-latency connections like local loopback or a 1 Gbps office network (round-trip time below 0.5 ms), sending them right back out creates an uncontrolled packet storm. That storm overflows operating system socket buffers (`ENOBUFS`) and drops packets.

My pacer prevents this with a scheduled departure queue:

1. When a packet returns, the engine checks its round-trip time:

$$\Delta t = t_{\text{arrival}} - t_{\text{epoch}}$$

2. If $\Delta t < T_{\text{target}}$ (by default 30 ms), the engine holds the frame in a min-heap until its release time:

$$t_{\text{release}} = t_{\text{now}} + (T_{\text{target}} - \Delta t)$$

3. A worker thread releases frames at their exact scheduled timestamps.
4. An inter-packet gap of 100 microseconds prevents bursts from bunching together.

## 5. Autonomous parity scrubber

I built a background scrubbing thread that runs every 100 milliseconds:

1. It checks all active files in the inode table.
2. For every chunk, it checks when that chunk was last seen.
3. If $(t_{\text{now}} - t_{\text{last\_seen}}) > 2.5 \times T_{\text{target}}$, the engine marks that packet as lost.
4. The scrubber recovers the lost chunk from surviving blocks using matrix inversion, updates its sequence counter, and sends it back into circulation.

## 6. Virtual filesystem (VFS) operations

The VFS maintains an in-memory directory tree with standard POSIX operations:

- `lookup(path)`: Walks directory components to find an inode.
- `create_file(path)`: Allocates an inode and sets up chunk tracking.
- `write_file(path, data)`: Slices bytes into 1024-byte chunks, computes parity blocks, and passes them to the pacer.
- `read_file(path, offset, size)`: Intercepts arriving packets from the network and returns the requested byte range.
- `unlink(path)`: Removes the inode from the tree. Because the system stops recirculating those chunks, they leave the network and disappear naturally.
