/*
 * ALS SubZero - Dynamic Delay-Line Network Memory Filesystem
 * Developed by Samin Sami.
 *
 * ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).
 * Mounts a POSIX filesystem whose contents circulate continuously
 * across network reflector hosts via ICMP delay lines.
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <netdb.h>
#include <pwd.h>
#include <arpa/inet.h>

#include "host.h"
#include "fs.h"
#include "net.h"
#include "chunk.h"
#include "fec.h"

#define DEFAULT_TIMEOUT_S 1
#define DEFAULT_PACER_US 500

struct arginfo {
	char *hostfile;
	char *mountpoint;
	int num_args;
	int timeout;
	int pacer_us;
};

enum {
	KEY_HELP,
	KEY_ASUSER,
	KEY_TIMEOUT,
	KEY_PACER,
};

static const struct fuse_opt subzero_opts[] = {
	FUSE_OPT_KEY("-h",  KEY_HELP),
	FUSE_OPT_KEY("-u ", KEY_ASUSER),
	FUSE_OPT_KEY("-t ", KEY_TIMEOUT),
	FUSE_OPT_KEY("-p ", KEY_PACER),
	FUSE_OPT_END,
};

static int read_hostnames(const char *hfile, struct gaicb **list[])
{
	int h = 0;
	FILE *file;

	if (strcmp("-", hfile) == 0) {
		file = stdin;
	} else {
		file = fopen(hfile, "r");
		if (!file) {
			perror("Failed to read reflector hostfile");
			return h;
		}
	}

	h = host_make_resolvlist(file, list);
	fclose(file);
	return h;
}

static int resolve_names(struct gaicb **list, int names, struct host **hosts)
{
	int ret;
	int hostcount;
	int i;

	fprintf(stderr, "Resolving %d reflector targets... ", names);
	fflush(stderr);

	ret = getaddrinfo_a(GAI_WAIT, list, names, NULL);
	if (ret != 0) {
		fprintf(stderr, "DNS resolution failed: %s\n", gai_strerror(ret));
		return -1;
	}

	fprintf(stderr, "done.\n");

	hostcount = 0;
	for (i = 0; i < names; i++) {
		ret = gai_error(list[i]);
		if (ret) {
			fprintf(stderr, "Skipping unreachable host %s: %s\n", list[i]->ar_name, gai_strerror(ret));
		} else {
			struct addrinfo *result = list[i]->ar_result;
			do {
				hostcount++;
				result = result->ai_next;
			} while (result);
		}
	}
	if (!hostcount) {
		fprintf(stderr, "No usable hosts found in target list.\n");
		return -1;
	}

	*hosts = host_create(list, names);
	host_free_resolvlist(list, names);

	if (*hosts == NULL) {
		fprintf(stderr, "Failed to create reflector host list.\n");
		return -1;
	}

	return hostcount;
}

static void print_usage(char *progname)
{
	fprintf(stderr,
		"ALS SubZero - Dynamic Delay-Line Network Filesystem\n"
		"Developed by Samin Sami (ALS = Al Sami)\n\n"
		"Usage: %s [options] hostfile mountpoint\n"
		"Options:\n"
		" -h            : Print this help message and exit\n"
		" -u username   : Mount filesystem with UID/GID of specified user\n"
		" -t timeout    : Max time to wait for ICMP echo reply (seconds, default 1)\n"
		" -p pacing_us  : Inter-packet rate pacing interval in microseconds (default 500)\n",
		progname);
}

static int subzero_opt_proc(void *data, const char *arg, int key, struct fuse_args *outargs)
{
	struct arginfo *arginfo = (struct arginfo *) data;
	struct passwd *pw;
	int res;

	switch (key) {
	case FUSE_OPT_KEY_NONOPT:
		arginfo->num_args++;
		if (!arginfo->hostfile) {
			arginfo->hostfile = strdup(arg);
			return 0;
		} else if (!arginfo->mountpoint) {
			arginfo->mountpoint = strdup(arg);
		}
		break;
	case KEY_HELP:
		print_usage(outargs->argv[0]);
		exit(0);
	case KEY_ASUSER:
		pw = getpwnam(&arg[2]);
		if (pw) {
			char userarg[64];
			snprintf(userarg, sizeof(userarg), "-ouid=%d,gid=%d", pw->pw_uid, pw->pw_gid);
			fuse_opt_add_arg(outargs, userarg);
			return 0;
		} else {
			fprintf(stderr, "Invalid username provided.\n");
			print_usage(outargs->argv[0]);
			exit(1);
		}
		break;
	case KEY_TIMEOUT:
		res = sscanf(arg, "-t%d", &arginfo->timeout);
		if (res == 1 && arginfo->timeout > 0 && arginfo->timeout < 60) {
			return 0;
		} else {
			fprintf(stderr, "Invalid timeout parameter.\n");
			print_usage(outargs->argv[0]);
			exit(1);
		}
	case KEY_PACER:
		res = sscanf(arg, "-p%d", &arginfo->pacer_us);
		if (res == 1 && arginfo->pacer_us >= 0 && arginfo->pacer_us <= 100000) {
			return 0;
		} else {
			fprintf(stderr, "Invalid pacing parameter.\n");
			print_usage(outargs->argv[0]);
			exit(1);
		}
	}
	return 1;
}

int main(int argc, char **argv)
{
	struct gaicb **list;
	struct host *hosts = NULL;
	struct host *h;
	int hostnames;
	int host_count;
	struct fuse_args args = FUSE_ARGS_INIT(argc, argv);
	struct arginfo arginfo;
	struct stat mountdir;
	int res;

	memset(&arginfo, 0, sizeof(arginfo));
	arginfo.timeout = DEFAULT_TIMEOUT_S;
	arginfo.pacer_us = DEFAULT_PACER_US;

	if (fuse_opt_parse(&args, &arginfo, subzero_opts, subzero_opt_proc) == -1) {
		fprintf(stderr, "Error parsing command line options.\n");
		print_usage(argv[0]);
		return EXIT_FAILURE;
	}

	if (arginfo.num_args != 2) {
		fprintf(stderr, "Missing required arguments: hostfile and mountpoint required.\n");
		print_usage(argv[0]);
		return EXIT_FAILURE;
	}

	res = stat(arginfo.mountpoint, &mountdir);
	if (res) {
		perror("Mountpoint validation failed");
		return EXIT_FAILURE;
	}
	if (!S_ISDIR(mountdir.st_mode)) {
		fprintf(stderr, "Mountpoint must be an existing directory.\n");
		return EXIT_FAILURE;
	}
	free(arginfo.mountpoint);

	hostnames = read_hostnames(arginfo.hostfile, &list);
	free(arginfo.hostfile);
	if (!hostnames) {
		fprintf(stderr, "No reflector hosts configured in hostfile.\n");
		return EXIT_FAILURE;
	}

	if (net_open_sockets()) {
		fprintf(stderr, "Failed to open raw ICMP sockets. Root/CAP_NET_RAW capabilities required.\n");
		return EXIT_FAILURE;
	}

	host_count = resolve_names(list, hostnames, &hosts);
	if (host_count < 0) {
		return EXIT_FAILURE;
	}

	host_count = host_evaluate(&hosts, host_count, arginfo.timeout);
	if (!host_count) {
		fprintf(stderr, "None of the reflector hosts passed responsiveness validation.\n");
		return EXIT_FAILURE;
	}

	chunk_set_timeout(arginfo.timeout);
	chunk_set_pacing_us(arginfo.pacer_us);
	host_use(hosts);

	fuse_opt_add_arg(&args, "-f");
	fuse_opt_add_arg(&args, "-s");
	fuse_opt_add_arg(&args, "-odefault_permissions,allow_other");
	fuse_opt_add_arg(&args, "-odirect_io");

	printf("Mounting ALS SubZero delay-line filesystem...\n");
	fuse_main(args.argc, args.argv, &fs_ops, NULL);

	fuse_opt_free_args(&args);
	h = hosts;
	while (h) {
		struct host *host = h;
		h = h->next;
		free(host);
	}
	return EXIT_SUCCESS;
}

