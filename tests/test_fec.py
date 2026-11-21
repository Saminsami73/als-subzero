"""
Unit tests for Galois Field GF(2^8) arithmetic and Cauchy Reed-Solomon Codec.
ALS SubZero - Developed by Samin Sami.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from als_subzero.fec.parity import (
    CauchyErasureCodec,
    gf_add,
    gf_div,
    gf_inv,
    gf_mul,
    gf_sub,
)


class TestGaloisFieldAndFEC(unittest.TestCase):
    def test_gf_arithmetic(self):
        # Addition and subtraction in GF(2^8) are bitwise XOR
        self.assertEqual(gf_add(0x57, 0x83), 0x57 ^ 0x83)
        self.assertEqual(gf_sub(0x57, 0x83), 0x57 ^ 0x83)

        # Multiplicative identity and inverse
        self.assertEqual(gf_mul(0x53, 1), 0x53)
        self.assertEqual(gf_mul(0x53, 0), 0)

        for b in range(1, 256):
            inv = gf_inv(b)
            self.assertEqual(gf_mul(b, inv), 1)
            self.assertEqual(gf_div(b, b), 1)

    def test_fec_encode_single_loss(self):
        codec = CauchyErasureCodec(k=4, m=2)
        data = [
            b"Alpha fragment data content",
            b"Beta  fragment data content",
            b"Gamma fragment data content",
            b"Delta fragment data content",
        ]
        parity = codec.encode(data)
        self.assertEqual(len(parity), 2)

        # Lose chunk 1
        survivors = [(0, data[0]), (2, data[2]), (3, data[3]), (4, parity[0])]
        recovered = codec.decode(survivors, target_len=len(data[0]))
        for i in range(4):
            self.assertEqual(recovered[i], data[i])

    def test_fec_encode_double_loss(self):
        codec = CauchyErasureCodec(k=4, m=2)
        data = [
            b"Fragment one: 1024 bytes padding...",
            b"Fragment two: 1024 bytes padding...",
            b"Fragment three: 1024 bytes pad...",
            b"Fragment four: 1024 bytes padd..",
        ]
        parity = codec.encode(data)

        # Lose chunk 0 and chunk 3, reconstruct from chunk 1, chunk 2, parity 0, parity 1
        survivors = [(1, data[1]), (2, data[2]), (4, parity[0]), (5, parity[1])]
        recovered = codec.decode(survivors, target_len=[len(d) for d in data])
        for i in range(4):
            self.assertEqual(recovered[i], data[i])

    def test_insufficient_survivors_raises(self):
        codec = CauchyErasureCodec(k=4, m=2)
        data = [b"a", b"b", b"c", b"d"]
        parity = codec.encode(data)
        survivors = [(0, data[0]), (1, data[1]), (4, parity[0])]  # Only 3 chunks, need 4
        with self.assertRaises(ValueError):
            codec.decode(survivors, target_len=1)


if __name__ == "__main__":
    unittest.main()
