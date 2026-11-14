"""
Unit tests for ALS SubZero binary framing and CRC integrity.
Developed by Samin Sami.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from als_subzero.core.framing import (
    CHUNK_SIZE,
    FLAG_LAST_CHUNK,
    FLAG_PARITY,
    FLAG_RECONSTRUCTED,
    FRAME_HEADER_SIZE,
    FRAME_MAGIC,
    ChunkFrame,
    FrameCorruptedError,
    decode_frame,
    encode_frame,
)


class TestFraming(unittest.TestCase):
    def test_encode_decode_roundtrip(self):
        payload = b"Hello, ALS SubZero delay-line memory!"
        raw = encode_frame(
            inode_id=42,
            chunk_idx=7,
            fec_group=1,
            chunk_in_group=3,
            payload=payload,
            flags=FLAG_LAST_CHUNK,
            seqno=100,
        )
        self.assertEqual(len(raw), FRAME_HEADER_SIZE + len(payload))

        frame = decode_frame(raw)
        self.assertEqual(frame.inode_id, 42)
        self.assertEqual(frame.chunk_idx, 7)
        self.assertEqual(frame.fec_group, 1)
        self.assertEqual(frame.chunk_in_group, 3)
        self.assertEqual(frame.flags, FLAG_LAST_CHUNK)
        self.assertEqual(frame.seqno, 100)
        self.assertEqual(frame.payload, payload)
        self.assertTrue(frame.is_last)
        self.assertFalse(frame.is_parity)

    def test_crc_tamper_detection(self):
        payload = b"Immutable network flight data"
        raw = bytearray(encode_frame(inode_id=1, chunk_idx=0, fec_group=0, chunk_in_group=0, payload=payload))

        # Tamper with payload byte
        raw[-1] ^= 0xFF
        with self.assertRaises(FrameCorruptedError):
            decode_frame(bytes(raw))

    def test_invalid_magic_rejection(self):
        payload = b"Test"
        raw = bytearray(encode_frame(inode_id=1, chunk_idx=0, fec_group=0, chunk_in_group=0, payload=payload))
        raw[0:4] = b"BAD!"
        with self.assertRaises(FrameCorruptedError):
            decode_frame(bytes(raw))

    def test_truncated_frame(self):
        with self.assertRaises(FrameCorruptedError):
            decode_frame(b"short")

    def test_sequence_hop_increment(self):
        frame = decode_frame(encode_frame(inode_id=2, chunk_idx=1, fec_group=0, chunk_in_group=1, payload=b"hop", seqno=10))
        self.assertEqual(frame.seqno, 10)
        frame.next_hop()
        self.assertEqual(frame.seqno, 11)


if __name__ == "__main__":
    unittest.main()
