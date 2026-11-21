/*
 * ALS SubZero - Forward Error Correction (FEC) Engine in C
 * Developed by Samin Sami.
 * ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).
 *
 * Implements block parity generation and erasure reconstruction.
 */

#ifndef SUBZERO_FEC_H_
#define SUBZERO_FEC_H_

#include <stdint.h>
#include <stddef.h>

#define FEC_DEFAULT_K 4

/* Compute XOR parity across k data buffers */
void fec_compute_parity(const uint8_t *data_buffers[], int k, size_t len, uint8_t *parity_out);

/* Reconstruct single missing chunk from surviving data and parity */
void fec_reconstruct(const uint8_t *surviving_buffers[], int k, size_t len, const uint8_t *parity, uint8_t *recovered_out);

#endif /* SUBZERO_FEC_H_ */
