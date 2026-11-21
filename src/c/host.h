/*
 * ALS SubZero - Reflector Host Resolution and Evaluation Header
 * Developed by Samin Sami.
 * ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).
 */

#ifndef SUBZERO_HOST_H_
#define SUBZERO_HOST_H_

#include <stdio.h>
#include <string.h>
#include <netdb.h>
#include <stdlib.h>

struct host {
	struct host *next;
	struct sockaddr_storage sockaddr;
	socklen_t sockaddr_len;
};

int host_make_resolvlist(FILE *hostfile, struct gaicb **list[]);
void host_free_resolvlist(struct gaicb *list[], int length);

struct host *host_create(struct gaicb *list[], int listlength);
int host_evaluate(struct host **hosts, int length, int timeout);
void host_use(struct host* hosts);
struct host *host_get_next();

#endif /* SUBZERO_HOST_H_ */
