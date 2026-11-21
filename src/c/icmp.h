/*
 * ALS SubZero - ICMP Packet Encoding and Parsing Header
 * Developed by Samin Sami.
 * ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).
 */

#ifndef SUBZERO_ICMP_H_
#define SUBZERO_ICMP_H_

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define ICMP_ADDRFAMILY(pkt) ((pkt)->peer.ss_family)
#define ICMP_HDRLEN 8

enum icmp_type {
	ICMP_REQUEST,
	ICMP_REPLY,
};

struct icmp_packet {
	struct sockaddr_storage peer;
	socklen_t peer_len;
	enum icmp_type type;
	uint16_t id;
	uint16_t seqno;
	uint8_t *payload;
	uint32_t payload_len;
};

extern int icmp_parse(struct icmp_packet *pkt, uint8_t *data, int len);
extern void icmp_dump(struct icmp_packet *pkt);
extern int icmp_send(int socket, struct icmp_packet *pkt);

#endif /* SUBZERO_ICMP_H_ */
