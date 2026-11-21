# ALS SubZero: Architecture

Built by Samin Sami.  
ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).

ALS SubZero keeps files alive in motion across network links. No hard drives, SSDs, or local RAM chips hold the file payload. When packets stop looping, the files disappear.

---

## 1. How It Works (Delay-Line Storage)

Early computers like EDSAC (1949) used mercury tubes to bounce sound waves back and forth as memory. ALS SubZero uses IP networks the same way:

1. You write a file.
2. The engine splits it into 4096-byte blocks and computes parity blocks using Cauchy Reed-Solomon coding.
3. Each block gets a 24-byte header with a CRC32C checksum and timestamp.
4. Packets are transmitted across UDP or ICMP reflectors.
5. As packets return, the engine reads them, checks their checksums, fixes any dropped packets, paces departures, and sends them back out.

Storage capacity follows the Bandwidth-Delay Product (BDP):

$$\text{Capacity} = \text{Bandwidth} \times \text{RTT}$$

A 1 Gbps link with a 40 ms round trip holds about 5.0 MB in flight ($40{,}000{,}000$ bits).

---

## 2. Packet Format (ALS1)

Every chunk travels inside a 24-byte binary header:

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
|                 Payload Bytes (0 to 4096 bytes)               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Fields:
- **Magic (4 bytes):** ASCII `ALS1`.
- **Inode ID (2 bytes):** File identifier.
- **Chunk Index (2 bytes):** Sequential block number.
- **FEC Group & Chunk in Group (2 bytes):** Stripe group and position ($0..K-1$ data, $K..K+M-1$ parity).
- **Flags (1 byte):** `0x01` = Parity, `0x02` = Last chunk, `0x04` = Reconstructed chunk, `0x08` = Dirty.
- **Sequence Number (2 bytes):** Increments on every reflection hop.
- **Payload Length (2 bytes):** Number of payload bytes (up to 4096).
- **CRC32C Checksum (4 bytes):** Castagnoli CRC32C over header bytes 0..15 plus payload.
- **Epoch (4 bytes):** Microsecond timestamp to track loop delay.

---

## 3. Error Correction (Cauchy Reed-Solomon)

Routers drop packets. To avoid file loss, ALS SubZero uses Cauchy Reed-Solomon coding over Galois Field $GF(2^8)$:

- Field polynomial: $P(x) = x^8 + x^4 + x^3 + x^2 + 1$ ($0\text{x}11\text{D} = 285$).
- Addition and subtraction: bitwise XOR (`^`).
- Multiplication and division: precomputed log/exp lookup tables.
- Default stripe: $K=4$ data chunks, $M=2$ parity chunks.
- Generator matrix: Cauchy layout $a_{i,j} = \frac{1}{x_i \oplus y_j}$.
- Any $K$ surviving chunks out of $K+M$ can invert the submatrix via Gauss-Jordan elimination and reconstruct all lost bytes.

---

## 4. Departure Pacer

On fast local networks, packets return in under a millisecond. Blasting them straight back out overwhelms socket buffers (`ENOBUFS`).

The pacer holds packets in a priority queue and releases them at a steady rate:
- Measures actual round-trip time: $\Delta t = t_{\text{arrival}} - t_{\text{epoch}}$.
- If $\Delta t < T_{\text{target}}$ (e.g. 30 ms), holds the packet until release time:
$$t_{\text{release}} = t_{\text{now}} + (T_{\text{target}} - \Delta t)$$
- Enforces an inter-packet gap (minimum 100 microseconds) to eliminate packet bunching.

---

## 5. Background Scrubber

A background thread runs every 100 ms:
1. Scans active chunks in the VFS table.
2. If a chunk hasn't been seen in $2.5 \times T_{\text{target}}$, marks it as lost.
3. Reconstructs missing chunks from surviving stripe members using Cauchy inversion.
4. Hands the reconstructed packets back to the pacer to re-enter flight.

---

## 6. Virtual Filesystem (VFS)

The in-memory VFS supports standard POSIX calls:
- `lookup(path)`: Finds the directory inode.
- `create_file(path)`: Allocates an inode and initializes chunk tables.
- `write_file(path, data)`: Chunks data, generates parity, and injects packets into flight.
- `read_file(path)`: Captures circulating packets and returns the assembled byte array.
- `unlink(path)`: Removes the inode. Packets for that file stop being refreshed and drop off the wire.
