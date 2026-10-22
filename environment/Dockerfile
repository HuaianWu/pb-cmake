# Clean-room image for the cmark task. Build from the task root:
#   docker build --platform linux/amd64 -f environment/Dockerfile -t pb-cmarkask .
#
# Stage 1: build the gold binary from the pinned upstream commit.
FROM ubuntu:22.04 AS gold
RUN apt-get update && apt-get install -y --no-install-recommends gcc libc6-dev git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/commonmark/cmark /src && git -C /src checkout --quiet eec0eeba6d31189fd828314576494566d539b1e3
COPY original/build.sh /build.sh
RUN mkdir -p /out && CC=gcc CFLAGS=-O2 /build.sh /src /out/cmark && strip /out/cmark

# Stage 2: the clean room. Only the binary and the documentation cross over:
# no source, no build tree, no git history, no upstream tests.
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc g++ make cmake python3 python3-pytest golang-go rustc cargo \
    && rm -rf /var/lib/apt/lists/*
COPY --from=gold /out/cmark /usr/local/bin/cmark
# Execute-only. This only works because the agent is not root.
RUN chown root:root /usr/local/bin/cmark && chmod 0111 /usr/local/bin/cmark
RUN useradd -m agent && mkdir -p /workspace && chown agent /workspace
COPY environment/docs/ /workspace/docs/
USER agent
WORKDIR /workspace
