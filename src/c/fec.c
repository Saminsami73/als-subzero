/*
 * ALS SubZero - Forward Error Correction (FEC) Engine in C
 * Developed by Samin Sami.
 * ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).
 *
 * Implements block parity generation and erasure reconstruction.
 */

#include "fec.h"
#include <string.h>

void fec_compute_parity(const uint8_t *data_buffers[], int k, size_t len,
                        uint8_t *parity_out) {
  size_t i;
  int b;

  if (!parity_out || k <= 0)
    return;

  memset(parity_out, 0, len);
  for (b = 0; b < k; b++) {
    const uint8_t *src = data_buffers[b];
    if (!src)
      continue;
    for (i = 0; i < len; i++) {
      parity_out[i] ^= src[i];
    }
  }
}

void fec_reconstruct(const uint8_t *surviving_buffers[], int k_minus_one,
                     size_t len, const uint8_t *parity,
                     uint8_t *recovered_out) {
  size_t i;
  int b;

  if (!recovered_out || !parity)
    return;

  memcpy(recovered_out, parity, len);
  for (b = 0; b < k_minus_one; b++) {
    const uint8_t *src = surviving_buffers[b];
    if (!src)
      continue;
    for (i = 0; i < len; i++) {
      recovered_out[i] ^= src[i];
    }
  }
}
