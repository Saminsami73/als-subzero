/*
 * ALS SubZero - Chunk Management and Recirculation Interface
 * Developed by Samin Sami.
 * ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).
 */

#ifndef SUBZERO_CHUNK_H_
#define SUBZERO_CHUNK_H_

#include <stdint.h>
#include <sys/socket.h>

#define CHUNK_SIZE 1024
#define DEFAULT_PACER_GAP_US 500

struct host;
struct io;

struct chunk {
	struct chunk *next_active;
	struct chunk *next_file;
	struct host *host;
	struct io *io;
	uint16_t id;
	uint16_t seqno;
	uint16_t len;
	uint32_t crc32;
	uint64_t last_tx_us;
};

/* Set timeout (seconds) waiting for packets */
void chunk_set_timeout(int t);

/* Set target pacing interval in microseconds */
void chunk_set_pacing_us(int us);

/* Allocate chunk and assign identification */
struct chunk *chunk_create();
void chunk_free(struct chunk *c);

/* Add/remove chunk from active recirculation list */
void chunk_add(struct chunk *c);
void chunk_remove(struct chunk *c);

/* Handle ICMP Echo Reply */
void chunk_reply(void *userdata, struct sockaddr_storage *addr,
	size_t addrlen, uint16_t id, uint16_t seqno, uint8_t **data, size_t len);

/* Intercept chunk from network for filesystem I/O */
int chunk_wait_for(struct chunk *c, uint8_t **data);
void chunk_done(struct chunk *c, uint8_t *data, size_t len);

#endif /* SUBZERO_CHUNK_H_ */
