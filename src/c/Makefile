CC ?= gcc
OBJS = icmp.o host.o fs.o net.o chunk.o fec.o als_subzero.o
LDFLAGS = -lanl -lrt `pkg-config fuse --libs`
CFLAGS += --std=c99 -Wall -Wshadow -pedantic -g `pkg-config fuse --cflags`
CFLAGS += -D_GNU_SOURCE -D_POSIX_C_SOURCE=200809 -D_XOPEN_SOURCE

all: als-subzero

als-subzero: $(OBJS)
	$(CC) $(OBJS) -o $@ $(LDFLAGS)

fec.o: fec.c fec.h
	$(CC) $(CFLAGS) -c fec.c

clean:
	rm -f *.o als-subzero

.PHONY: all clean
