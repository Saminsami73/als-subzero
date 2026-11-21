/*
 * ALS SubZero - Raw Socket Network Transport Header
 * Developed by Samin Sami.
 * ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).
 */

#ifndef SUBZERO_NET_H_
#define SUBZERO_NET_H_

#include "host.h"
#include <stdint.h>
#include <sys/types.h>

int net_open_sockets();
void net_send(struct host *host, uint16_t id, uint16_t seqno, const uint8_t *data, size_t len);

typedef void (*net_recv_fn_t)(void *userdata, struct sockaddr_storage *addr,
	size_t addrlen, uint16_t id, uint16_t seqno, uint8_t **data, size_t len);

int net_recv(struct timeval *tv, net_recv_fn_t recv_fn, void *recv_data);
void net_inc_rx(int packetsize);
void net_start();
void net_stop();

#endif /* SUBZERO_NET_H_ */
