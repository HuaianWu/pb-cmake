#!/bin/sh
# Build the gold binary of cmark 0.31.2 without cmake.
# Usage: build.sh <source-dir> <output-path>     (extra flags via CFLAGS / LDFLAGS)
# The source dir is a checkout of https://github.com/commonmark/cmark at the commit in task.yaml.
set -e
SRC="$1"; OUT="$2"
GEN=$(mktemp -d)
cat > "$GEN/cmark_version.h" <<'H'
#ifndef CMARK_VERSION_H
#define CMARK_VERSION_H
#define CMARK_VERSION ((0 << 16) | (31 << 8) | 2)
#define CMARK_VERSION_STRING "0.31.2"
#endif
H
cat > "$GEN/cmark_export.h" <<'H'
#ifndef CMARK_EXPORT_H
#define CMARK_EXPORT_H
#define CMARK_EXPORT
#define CMARK_NO_EXPORT
#endif
H
${CC:-cc} ${CFLAGS:--O2} -std=c99 -I"$GEN" -I"$SRC/src" -o "$OUT" "$SRC"/src/*.c ${LDFLAGS}
rm -rf "$GEN"
