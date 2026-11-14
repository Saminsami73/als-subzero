# ALS SubZero Protocol and Framing Specification (ALS1)

Specification Version: 1.0.0
Author: Samin Sami (ALS = Al Sami)

## 1. Scope

This document specifies the ALS1 binary packet encapsulation protocol used by ALS SubZero to maintain authenticated delay-line storage over IP networks.

## 2. Byte ordering

All multi-byte numeric fields in the ALS1 frame header use Network Byte Order (Big Endian).

## 3. Frame structure

Each frame consists of a fixed 24-byte header followed by variable-length data:

```
Total Frame Size = 24 + Payload Length (bytes)
```

| Offset (Bytes) | Field Name | Type | Description |
| :--- | :--- | :--- | :--- |
| 0 to 3 | Magic | ASCII char[4] | Must match `ALS1` (`0x41, 0x4C, 0x53, 0x31`) |
| 4 to 5 | Inode ID | uint16 | Inode identifier (1 to 65535) |
| 6 to 7 | Chunk Index | uint16 | Logical block offset within file |
| 8 | FEC Group | uint8 | FEC block grouping identifier |
| 9 | Chunk in Group | uint8 | Position in coding block: `0..K-1` (data), `K..K+M-1` (parity) |
| 10 | Flags | uint8 | Bitmask defining frame properties |
| 11 | Reserved | uint8 | Transmitted as `0x00` |
| 12 to 13 | Sequence Number | uint16 | Incremented on each transmission hop |
| 14 to 15 | Payload Length | uint16 | Payload length in bytes (0 to 1024) |
| 16 to 19 | CRC32C | uint32 | CRC32 checksum over header bytes 0..15 and payload |
| 20 to 23 | Epoch (us) | uint32 | Transmission timestamp in microseconds |
| 24 to End | Payload | uint8[] | Raw block content or parity bytes |

## 4. Flag definitions

The Flags byte at offset 10 contains bitwise indicators:

- `0x01` (`FLAG_PARITY`): The frame holds a Cauchy Reed-Solomon parity payload rather than original file data.
- `0x02` (`FLAG_LAST_CHUNK`): Indicates the final block of a regular file.
- `0x04` (`FLAG_RECONSTRUCTED`): Marked by the scrubber when a chunk has been recovered from an erasure.
- `0x08` (`FLAG_DIRTY`): Reserved for write synchronizations.
- Bits 4 through 7: Reserved for future extensions. Transmitted as 0.

## 5. Checksum calculation

The CRC32C field at offset 16 uses the Castagnoli polynomial:

$$P_{\text{CRC32C}} = 0x1EDC6F41$$

Calculation scope:

1. Bytes 0 through 15 of the frame header (Magic, Inode, Chunk Index, FEC Group, Chunk in Group, Flags, Reserved, Sequence Number, Payload Length).
2. The entire payload slice (bytes 24 through $24 + \text{Payload Length}$).

Frames that fail the checksum check are dropped immediately upon reception to protect in-flight files from corrupted packets.

## 6. Sequence numbering and rollover

The sequence counter starts at 0 when a file is first written and increments by 1 on every network reflection hop. When the counter reaches 65535 (`0xFFFF`), it rolls over to 0.

## 7. Transport layers

### Raw ICMP transport

Frames travel as the data payload of standard ICMP Echo Requests (Type 8, Code 0) defined in RFC 792. Reflectors echo the payload back inside an ICMP Echo Reply (Type 0).

### UDP echo transport

Frames travel as UDP datagrams to configured reflector ports. Compatible reflectors return incoming datagrams back to the sender port without modification.
