"""
ALS SubZero Frame Framing and Binary Protocol.
Developed by Samin Sami.

Implements the 24-byte authenticated network frame header and packet serialization.
"""

from __future__ import annotations

import binascii
import struct
import time
from dataclasses import dataclass
from typing import Optional, Tuple

FRAME_MAGIC = b"ALS1"
FRAME_HEADER_SIZE = 24
CHUNK_SIZE = 1024
MAX_PAYLOAD_SIZE = 1024

# Flags
FLAG_PARITY = 0x01
FLAG_LAST_CHUNK = 0x02
FLAG_RECONSTRUCTED = 0x04
FLAG_DIRTY = 0x08


class FrameCorruptedError(Exception):
    """Raised when frame CRC or magic check fails."""


@dataclass(slots=True)
class ChunkFrame:
    inode_id: int
    chunk_idx: int
    fec_group: int
    chunk_in_group: int
    flags: int
    seqno: int
    payload_len: int
    checksum: int
    epoch_us: int
    payload: bytes

    @property
    def is_parity(self) -> bool:
        return bool(self.flags & FLAG_PARITY)

    @property
    def is_last(self) -> bool:
        return bool(self.flags & FLAG_LAST_CHUNK)

    @property
    def is_reconstructed(self) -> bool:
        return bool(self.flags & FLAG_RECONSTRUCTED)

    def mark_reconstructed(self) -> None:
        self.flags |= FLAG_RECONSTRUCTED

    def next_hop(self) -> None:
        """Advance the sequence number for the next network hop."""
        self.seqno = (self.seqno + 1) & 0xFFFF
        self.epoch_us = int(time.time() * 1_000_000) & 0xFFFFFFFF
        # Recalculate checksum with new seqno and epoch
        self.checksum = self._compute_checksum(self.payload)

    def _compute_checksum(self, payload: bytes) -> int:
        pre_header = struct.pack(
            "!4sHHBBBBHH",
            FRAME_MAGIC,
            self.inode_id,
            self.chunk_idx,
            self.fec_group,
            self.chunk_in_group,
            self.flags,
            0,  # reserved
            self.seqno,
            len(payload),
        )
        return binascii.crc32(pre_header + payload) & 0xFFFFFFFF


def encode_frame(
    inode_id: int,
    chunk_idx: int,
    fec_group: int,
    chunk_in_group: int,
    payload: bytes,
    flags: int = 0,
    seqno: int = 0,
    epoch_us: Optional[int] = None,
) -> bytes:
    """Pack metadata and payload into a verified binary frame."""
    if len(payload) > MAX_PAYLOAD_SIZE:
        raise ValueError(f"Payload size {len(payload)} exceeds max {MAX_PAYLOAD_SIZE}")

    if epoch_us is None:
        epoch_us = int(time.time() * 1_000_000) & 0xFFFFFFFF

    payload_len = len(payload)
    pre_header = struct.pack(
        "!4sHHBBBBHH",
        FRAME_MAGIC,
        inode_id,
        chunk_idx,
        fec_group,
        chunk_in_group,
        flags,
        0,  # reserved
        seqno,
        payload_len,
    )
    checksum = binascii.crc32(pre_header + payload) & 0xFFFFFFFF
    header = pre_header + struct.pack("!II", checksum, epoch_us)
    return header + payload


def decode_frame(raw: bytes) -> ChunkFrame:
    """Decode and verify an incoming binary frame."""
    if len(raw) < FRAME_HEADER_SIZE:
        raise FrameCorruptedError(f"Frame length {len(raw)} is shorter than header {FRAME_HEADER_SIZE}")

    header = raw[:FRAME_HEADER_SIZE]
    magic, inode_id, chunk_idx, fec_group, chunk_in_group, flags, reserved, seqno, payload_len, checksum, epoch_us = (
        struct.unpack("!4sHHBBBBHHII", header)
    )

    if magic != FRAME_MAGIC and magic != b"RFS1":
        raise FrameCorruptedError(f"Invalid frame magic: {magic!r}")

    expected_total_len = FRAME_HEADER_SIZE + payload_len
    if len(raw) < expected_total_len:
        raise FrameCorruptedError(f"Frame payload truncated: expected {payload_len}, got {len(raw) - FRAME_HEADER_SIZE}")

    payload = raw[FRAME_HEADER_SIZE:expected_total_len]
    pre_header = header[:16]
    computed_crc = binascii.crc32(pre_header + payload) & 0xFFFFFFFF
    if computed_crc != checksum:
        raise FrameCorruptedError(f"CRC32 mismatch: frame {checksum:#010x} != computed {computed_crc:#010x}")

    return ChunkFrame(
        inode_id=inode_id,
        chunk_idx=chunk_idx,
        fec_group=fec_group,
        chunk_in_group=chunk_in_group,
        flags=flags,
        seqno=seqno,
        payload_len=payload_len,
        checksum=checksum,
        epoch_us=epoch_us,
        payload=payload,
    )
