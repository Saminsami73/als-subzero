/*
 * ALS SubZero - FUSE Filesystem Operations Header
 * Developed by Samin Sami.
 * ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).
 */

#ifndef SUBZERO_FS_H_
#define SUBZERO_FS_H_

#define FUSE_USE_VERSION 26

#include <sys/types.h>
#include <sys/stat.h>
#include <fuse.h>

extern const struct fuse_operations fs_ops;

#endif /* SUBZERO_FS_H_ */
