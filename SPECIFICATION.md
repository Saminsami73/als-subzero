# ALS SubZero: Protocol Specification (ALS1)

Version: 1.0.0  
Author: Samin Sami (ALS = Al Sami)

This document defines the ALS1 binary packet structure used to circulate files over IP network links.

---

## 1. Byte Order

All multi-byte numeric fields are Big Endian (Network Byte Order).

---

## 2. Header Layout

Each packet has a 24-byte header followed by the chunk payload:

```
Total packet size = 24 + Payload Length (bytes)
```

| Offset | Field Name | Type | Description |
|---|---|---|---|
| 0..3 | Magic | char[4] | ASCII string `ALS1` (`0x41 0x4C 0x53 0x31`) |
| 4..5 | Inode ID | uint16 | File inode number (1 to 65535) |
| 6..7 | Chunk Index | uint16 | Block index within file |
| 8 | FEC Group | uint8 | Stripe group index |
| 9 | Chunk in Group | uint8 | Position in stripe: `0..K-1` (data), `K..K+M-1` (parity) |
| 10 | Flags | uint8 | Bitmask flags |
| 11 | Reserved | uint8 | Set to `0x00` |
| 12..13 | Sequence Number | uint16 | Increments by 1 on each reflection hop |
| 14..15 | Payload Length | uint16 | Payload size in bytes (0 to 4096) |
| 16..19 | Checksum | uint32 | CRC32C over header (bytes 0..15) + payload |
| 20..23 | Epoch | uint32 | Microsecond timestamp modulo $2^{32}$ |
| 24..End | Payload | bytes | Data or parity bytes |

---

## 3. Flags

The `Flags` byte at offset 10:

- `0x01` (`FLAG_PARITY`): Set for parity chunks.
- `0x02` (`FLAG_LAST_CHUNK`): Marks the last chunk of a file.
- `0x04` (`FLAG_RECONSTRUCTED`): Set when recovered by the FEC scrubber.
- `0x08` (`FLAG_DIRTY`): Reserved for write synchronizations.
- Bits 4 to 7: Reserved (set to 0).

---

## 4. Integrity (CRC32C)

The checksum uses the Castagnoli polynomial:

$$P = 0\text{x}1\text{EDC}6\text{F}41$$

Scope:
1. Header bytes 0 to 15.
2. The payload bytes.

Any packet failing the checksum check is dropped immediately. The FEC engine then reconstructs the lost chunk from surviving parity.

---

## 5. Hop Sequence Counter

The sequence number starts at 0 on file creation and increments on each reflection hop. If it hits 65535 (`0xFFFF`), it wraps back to 0.

---

## 6. Transports

- **UDP Echo**: Frames travel inside standard UDP datagrams to configured reflector ports.
- **Raw ICMP**: Frames travel inside ICMP Echo Requests (RFC 792 Type 8) and return inside ICMP Echo Replies (Type 0).
- **Simulated**: In-memory ring buffer with configurable drop rate and artificial RTT delay for unit tests and offline demos.
