#!/usr/bin/env bash
# PARKED 2026-09-25 (AF-AP-207): the fork's RWKV7 path needs FlashRWKV, which refuses to build below SM90; the 3090 is SM86.
# Kept as the record; see docs/research/findings/jev-pipes/VLLM-RWKV-2026-09-25.md.
# Build the vllm-rwkv image (pinned) for the RTX 3090 (sm_86). Runs detached on the PC; log: ~/vllm-rwkv-build/build.log.
# Every step's rc is checked explicitly: `set -e` is ignored inside a block on the left of `||` (the first run printed
# "BUILD OK" after podman failed). Base images are fully qualified: podman refuses short names without a TTY.
set -uo pipefail
PIN=67f0c5996c50dca0ad779da545cb491527de988f
D=~/vllm-rwkv-build
LOG=$D/build.log
mkdir -p "$D"
say() { echo "== $(date -u +%FT%TZ) $*" >> "$LOG"; }
fail() { say "BUILD FAILED: $*"; exit 1; }
: > "$LOG"
say "fetch $PIN"
if [ ! -d "$D/src/.git" ]; then git init -q "$D/src" && git -C "$D/src" remote add origin https://github.com/rwkv-rs/vllm-rwkv || fail "git init"; fi
git -C "$D/src" fetch -q --depth 1 origin "$PIN" >> "$LOG" 2>&1 || fail "git fetch rc=$?"
git -C "$D/src" checkout -q --detach FETCH_HEAD >> "$LOG" 2>&1 || fail "git checkout rc=$?"
[ "$(git -C "$D/src" rev-parse HEAD)" = "$PIN" ] || fail "pin mismatch"
# LOCAL PATCH (recorded in docs/research/findings/jev-pipes/VLLM-RWKV-2026-09-25.md): at the pin the csrc-build stage copies
# setup.py but not tools/build_profiles.py, which setup.py loads at import (setup.py:36-37); the first real build failed there
# with FileNotFoundError. Restore the file first so a rerun patches a clean copy.
git -C "$D/src" checkout -q -- docker/Dockerfile || fail "restore Dockerfile"
python3 - "$D/src/docker/Dockerfile" <<'PY' >> "$LOG" 2>&1 || fail "patch Dockerfile"
import sys
p = sys.argv[1]
s = open(p).read()
a = "COPY tools/build_rust.py tools/build_rust.py\nCOPY cmake cmake/\n"
assert s.count(a) == 1, s.count(a)
s = s.replace(a, "COPY tools/build_rust.py tools/build_rust.py\nCOPY tools/build_profiles.py tools/build_profiles.py\nCOPY cmake cmake/\n")
open(p, "w").write(s)
print("patched: COPY tools/build_profiles.py")
PY
say "podman build"
( cd "$D/src" && podman build -f docker/Dockerfile --target vllm-openai \
    --build-arg BUILD_BASE_IMAGE=docker.io/nvidia/cuda:13.0.3-devel-ubuntu22.04 \
    --build-arg FINAL_BASE_IMAGE=docker.io/nvidia/cuda:13.0.3-base-ubuntu22.04 \
    --build-arg torch_cuda_arch_list='8.6' --build-arg max_jobs=6 --build-arg nvcc_threads=2 \
    --build-arg RUN_WHEEL_CHECK=false -t localhost/vllm-rwkv:67f0c59 . ) >> "$LOG" 2>&1
rc=$?
[ "$rc" -eq 0 ] || fail "podman build rc=$rc"
podman image inspect localhost/vllm-rwkv:67f0c59 --format '{{.Id}} {{.Size}}' >> "$LOG" 2>&1 || fail "image missing after build"
say "BUILD OK"
