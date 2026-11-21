"""
ALS SubZero Forward Error Correction (FEC) & Galois Field Erasure Engine.
Developed by Samin Sami.

Provides Reed-Solomon erasure coding over GF(2^8) with Cauchy distribution matrices.
Recovers from up to M chunk losses within any (K, M) group.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

PRIMITIVE_POLYNOMIAL = 0x11D  # x^8 + x^4 + x^3 + x^2 + 1 (standard 285)

# Precomputed log and exp tables for GF(2^8)
GF_EXP = [0] * 512
GF_LOG = [0] * 256


def _init_gf_tables() -> None:
    x = 1
    for i in range(255):
        GF_EXP[i] = x
        GF_EXP[i + 255] = x
        GF_LOG[x] = i
        x <<= 1
        if x & 0x100:
            x ^= PRIMITIVE_POLYNOMIAL
    GF_LOG[0] = 0


_init_gf_tables()


def gf_add(a: int, b: int) -> int:
    """Addition in GF(2^8) is bitwise XOR."""
    return a ^ b


def gf_sub(a: int, b: int) -> int:
    """Subtraction in GF(2^8) is also bitwise XOR."""
    return a ^ b


def gf_mul(a: int, b: int) -> int:
    """Multiplication in GF(2^8) via log tables."""
    if a == 0 or b == 0:
        return 0
    return GF_EXP[GF_LOG[a] + GF_LOG[b]]


def gf_div(a: int, b: int) -> int:
    """Division in GF(2^8)."""
    if b == 0:
        raise ZeroDivisionError("Division by zero in GF(2^8)")
    if a == 0:
        return 0
    return GF_EXP[(GF_LOG[a] - GF_LOG[b] + 255) % 255]


def gf_inv(a: int) -> int:
    """Multiplicative inverse in GF(2^8)."""
    if a == 0:
        raise ZeroDivisionError("Zero has no multiplicative inverse in GF(2^8)")
    return GF_EXP[255 - GF_LOG[a]]


class CauchyErasureCodec:
    """
    Reed-Solomon erasure coding using Cauchy generator matrices over GF(2^8).
    Takes K data fragments and produces M parity fragments.
    Can reconstruct all K original data fragments from any K surviving fragments.
    """

    def __init__(self, k: int = 4, m: int = 2) -> None:
        if k < 1 or m < 1:
            raise ValueError("K and M must be at least 1")
        if k + m > 256:
            raise ValueError("Total fragments (K + M) cannot exceed 256 in GF(2^8)")
        self.k = k
        self.m = m
        self.n = k + m
        self.matrix = self._build_cauchy_matrix(k, m)

    @staticmethod
    def _build_cauchy_matrix(k: int, m: int) -> List[List[int]]:
        """
        Build an M x K Cauchy matrix where entry (i, j) = 1 / (X_i ^ Y_j).
        X and Y are disjoint sets in GF(2^8).
        """
        x = [i for i in range(m)]
        y = [m + j for j in range(k)]
        matrix: List[List[int]] = []
        for xi in x:
            row: List[int] = []
            for yj in y:
                denom = gf_add(xi, yj)
                row.append(gf_inv(denom))
            matrix.append(row)
        return matrix

    def encode(self, data_chunks: List[bytes]) -> List[bytes]:
        """
        Given K data chunks of uniform length, generate M parity chunks.
        If chunk lengths differ, they are padded with zeros to max length.
        """
        if len(data_chunks) != self.k:
            raise ValueError(f"Expected {self.k} data chunks, got {len(data_chunks)}")

        max_len = max(len(c) for c in data_chunks)
        padded_data = [c.ljust(max_len, b"\x00") for c in data_chunks]

        parity_chunks: List[bytearray] = [bytearray(max_len) for _ in range(self.m)]

        for p_idx in range(self.m):
            row = self.matrix[p_idx]
            for byte_pos in range(max_len):
                val = 0
                for d_idx in range(self.k):
                    coeff = row[d_idx]
                    data_byte = padded_data[d_idx][byte_pos]
                    val = gf_add(val, gf_mul(coeff, data_byte))
                parity_chunks[p_idx][byte_pos] = val

        return [bytes(p) for p in parity_chunks]

    def decode(
        self,
        available_chunks: List[Tuple[int, bytes]],
        target_len: Optional[int | List[int]] = None,
    ) -> List[bytes]:
        """
        Reconstruct all K data chunks from any K available (index, payload) pairs.
        Index 0 .. K-1: data chunks.
        Index K .. K+M-1: parity chunks.
        target_len can be an int or a list of ints specifying lengths for each data chunk.
        """
        if len(available_chunks) < self.k:
            raise ValueError(
                f"Cannot reconstruct: need at least {self.k} chunks, but only {len(available_chunks)} provided"
            )

        # Select first K available chunks
        survivors = available_chunks[: self.k]
        indices = [idx for idx, _ in survivors]
        chunks = [data for _, data in survivors]

        chunk_len = max(len(c) for c in chunks)
        padded_survivors = [c.ljust(chunk_len, b"\x00") for c in chunks]

        # Construct submatrix of size K x K from generator matrix
        # Generator matrix G has top K rows as identity, bottom M rows as Cauchy matrix
        submatrix: List[List[int]] = []
        for idx in indices:
            if idx < self.k:
                # Identity row
                row = [0] * self.k
                row[idx] = 1
                submatrix.append(row)
            else:
                # Parity row from Cauchy matrix
                p_idx = idx - self.k
                submatrix.append(list(self.matrix[p_idx]))

        # Invert the submatrix using Gauss-Jordan elimination over GF(2^8)
        inverted = self._invert_matrix(submatrix)

        # Multiply inverted matrix by survivor chunk bytes to obtain original K data chunks
        recovered_data: List[bytearray] = [bytearray(chunk_len) for _ in range(self.k)]
        for r in range(self.k):
            inv_row = inverted[r]
            for byte_pos in range(chunk_len):
                val = 0
                for c in range(self.k):
                    coeff = inv_row[c]
                    data_byte = padded_survivors[c][byte_pos]
                    val = gf_add(val, gf_mul(coeff, data_byte))
                recovered_data[r][byte_pos] = val

        result: List[bytes] = []
        for i in range(self.k):
            raw_bytes = bytes(recovered_data[i])
            if target_len is None:
                result.append(raw_bytes)
            elif isinstance(target_len, list):
                result.append(raw_bytes[: target_len[i]])
            else:
                result.append(raw_bytes[: target_len])

        return result

    @staticmethod
    def _invert_matrix(matrix: List[List[int]]) -> List[List[int]]:
        """Compute the matrix inverse over GF(2^8) via Gauss-Jordan elimination."""
        n = len(matrix)
        # Augment with identity matrix
        aug = [list(matrix[r]) + [1 if r == c else 0 for c in range(n)] for r in range(n)]

        for col in range(n):
            # Pivot selection
            pivot_row = -1
            for row in range(col, n):
                if aug[row][col] != 0:
                    pivot_row = row
                    break
            if pivot_row == -1:
                raise ValueError("Matrix is singular over GF(2^8), reconstruction impossible")

            if pivot_row != col:
                aug[col], aug[pivot_row] = aug[pivot_row], aug[col]

            # Scale pivot row to 1
            pivot_val = aug[col][col]
            inv_pivot = gf_inv(pivot_val)
            for j in range(col, 2 * n):
                aug[col][j] = gf_mul(aug[col][j], inv_pivot)

            # Eliminate column in other rows
            for row in range(n):
                if row != col and aug[row][col] != 0:
                    factor = aug[row][col]
                    for j in range(col, 2 * n):
                        aug[row][j] = gf_sub(aug[row][j], gf_mul(factor, aug[col][j]))

        # Extract inverse matrix from augmented side
        return [[aug[r][c + n] for c in range(n)] for r in range(n)]
