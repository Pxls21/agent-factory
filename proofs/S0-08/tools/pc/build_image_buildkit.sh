#!/usr/bin/env bash
# S0-08 — build the pinned Hermes image with rootless BuildKit, for run_containment.sh --image.
# PC-SIDE. NOT run in the sandbox.
#
# WHY THIS EXISTS (three environment findings, 2026-09-18; the pinned Dockerfile is UNMODIFIED):
#   1. run_containment.sh's default `podman build` CANNOT build this image: Dockerfile line 286 is
#      `COPY --link --chmod=a+rX,go-w . .` — a BuildKit-only symbolic --chmod. podman 5.7/buildah
#      AND buildkit's built-in `dockerfile.v0` frontend are both OCTAL-chmod-only and reject it
#      ("invalid chmod parameter"). Symbolic chmod needs the EXTERNAL `docker/dockerfile:1` frontend
#      (what a modern `docker build` pulls by default). We select it at INVOCATION time via
#      gateway.v0 --opt source=..., without editing the pinned source — provenance preserved.
#   2. The PC has no running docker daemon (only docker.socket, disabled), so `docker buildx` is
#      unavailable; rocco is in the docker group but nothing listens. Standalone rootless BuildKit
#      (buildctl + `rootlesskit buildkitd`) needs no daemon and no sudo — SINGLE-level rootless,
#      the same privilege podman already uses here.
#   3. The PC's ONLY global IPv6 route is a black-holing Tailscale ULA (fd7a:115c:a1e0::/…,
#      pref low). playwright's bundled node downloader (Dockerfile line 199,
#      `npx playwright install --with-deps chromium`) prefers the AAAA address and STALLS 30s,
#      failing the build; curl -L uses Happy-Eyeballs and is fine over IPv4 (~6 MB/s). We give the
#      build an IPv4-ONLY network namespace via `rootlesskit --net=slirp4netns` so node uses IPv4.
#
# The resulting image is provenance-equivalent to a `docker build`: same pinned source (git archive
# of the pin), same unmodified Dockerfile, same HERMES_GIT_SHA build-arg; the baked
# /etc/hermes/image-provenance.json and /opt/hermes/.hermes_build_sha both carry the pinned commit,
# which run_containment.sh (and check_containment.py) verify independently.
#
# Usage: build_image_buildkit.sh [--source DIR]   (default source ~/s0-01-pinned/hermes-agent)
# Exit: 0 built+loaded; 2 pinned-source/build failure; 3 buildkitd failed to start; 5 load failed.
set -uo pipefail
export XDG_RUNTIME_DIR="/run/user/$(id -u)"

PINNED_COMMIT="527da60844d4dced37879ea50259675371abe10e"
IMAGE_TAG="localhost/hermes-s0-08:527da608"
SOURCE_DIR="${HOME}/s0-01-pinned/hermes-agent"
FRONTEND="docker/dockerfile:1"          # external frontend: supports symbolic --chmod
BK_VERSION="v0.19.0"                     # pinned buildkit release (buildkitd + buildctl)
BK_DIR="${HOME}/s0-08-buildkit"
BK_ADDR="tcp://127.0.0.1:1234"
BK_PIDF="${HOME}/s0-08-buildkitd.pid"
BK_LOG="${HOME}/s0-08-buildkitd.log"
WORK="${HOME}/s0-08-realbuild"
LOCKD="${HOME}/s0-08-build.lockd"

while [ $# -gt 0 ]; do
    case "$1" in
        --source) SOURCE_DIR="$2"; shift 2 ;;
        *) echo "usage: build_image_buildkit.sh [--source DIR]" >&2; exit 64 ;;
    esac
done
step() { echo "=== [$(date -u +%H:%M:%S)] $* ==="; }

# Single-build lock (atomic mkdir): a re-entrant launcher must not run concurrent builds — the
# playwright download splits bandwidth and times out (2026-09-18).
if ! mkdir "$LOCKD" 2>/dev/null; then
    holder="$(cat "$LOCKD/pid" 2>/dev/null || echo unknown)"
    if kill -0 "$holder" 2>/dev/null; then echo "build already running (pid $holder)"; exit 0; fi
    rm -rf "$LOCKD"; mkdir "$LOCKD" 2>/dev/null || { echo "cannot acquire build lock"; exit 1; }
fi
echo $$ > "$LOCKD/pid"
trap 'rm -rf "$LOCKD"' EXIT

# --- pinned-source preflight (mirror of run_containment.sh s0_08_require_pinned_source) ---
[ -f "$SOURCE_DIR/Dockerfile" ] || { echo "s0-08: no Dockerfile at $SOURCE_DIR"; exit 2; }
actual="$(git -C "$SOURCE_DIR" rev-parse HEAD 2>/dev/null || echo unknown)"
[ "$actual" = "$PINNED_COMMIT" ] || { echo "s0-08: $SOURCE_DIR at $actual, expected $PINNED_COMMIT"; exit 2; }
dirty="$(git -C "$SOURCE_DIR" status --porcelain=v1 --untracked-files=all 2>/dev/null || echo unknown)"
[ -z "$dirty" ] || { echo "s0-08: $SOURCE_DIR is dirty; refusing a non-canonical source"; exit 2; }
echo "s0-08: pinned source OK: $SOURCE_DIR @ $actual"

# --- buildkit binaries (download the pinned release if absent) ---
if [ ! -x "$BK_DIR/bin/buildkitd" ] || [ ! -x "$BK_DIR/bin/buildctl" ]; then
    step "download buildkit $BK_VERSION"
    mkdir -p "$BK_DIR"
    url="https://github.com/moby/buildkit/releases/download/${BK_VERSION}/buildkit-${BK_VERSION}.linux-amd64.tar.gz"
    curl -fSL -o "$BK_DIR/buildkit.tar.gz" "$url" || { echo "s0-08: buildkit download failed"; exit 2; }
    echo "s0-08: buildkit.tar.gz sha256 $(sha256sum "$BK_DIR/buildkit.tar.gz" | cut -d' ' -f1)"
    tar -xzf "$BK_DIR/buildkit.tar.gz" -C "$BK_DIR" || { echo "s0-08: buildkit extract failed"; exit 2; }
fi

# --- git-archive build context (identical to run_containment.sh's build context) ---
rm -rf "$WORK"; mkdir -p "$WORK/ctx"
git -C "$SOURCE_DIR" archive "$PINNED_COMMIT" -o "$WORK/src.tar" || { echo "s0-08: archive failed"; exit 2; }
tar -xf "$WORK/src.tar" -C "$WORK/ctx" || { echo "s0-08: extract failed"; exit 2; }
rm -f "$WORK/src.tar"

# --- rootless buildkitd on an IPv4-only slirp4netns netns (finding #3) ---
if ! { [ -f "$BK_PIDF" ] && kill -0 "$(cat "$BK_PIDF")" 2>/dev/null \
       && "$BK_DIR/bin/buildctl" --addr "$BK_ADDR" debug workers >/dev/null 2>&1; }; then
    [ -f "$BK_PIDF" ] && kill "$(cat "$BK_PIDF")" 2>/dev/null || true; sleep 1
    step "launch rootless buildkitd (slirp4netns IPv4-only + port-forward)"
    nohup rootlesskit \
        --net=slirp4netns --mtu=65520 --disable-host-loopback \
        --copy-up=/etc --copy-up=/run \
        --port-driver=builtin -p 127.0.0.1:1234:1234/tcp \
        "$BK_DIR/bin/buildkitd" --addr tcp://0.0.0.0:1234 \
        --root "$HOME/.local/share/buildkit" > "$BK_LOG" 2>&1 &
    echo $! > "$BK_PIDF"
    ready=0
    for _ in $(seq 1 20); do
        "$BK_DIR/bin/buildctl" --addr "$BK_ADDR" debug workers >/dev/null 2>&1 && { ready=1; break; }
        kill -0 "$(cat "$BK_PIDF")" 2>/dev/null || { echo "s0-08: buildkitd died"; tail -20 "$BK_LOG"; exit 3; }
        sleep 1
    done
    [ "$ready" = 1 ] || { echo "s0-08: buildkitd not ready"; tail -20 "$BK_LOG"; exit 3; }
fi

# --- build (external frontend for symbolic chmod; finding #1), OCI out, load into podman ---
step "buildctl build $IMAGE_TAG (frontend=$FRONTEND, HERMES_GIT_SHA=$PINNED_COMMIT)"
"$BK_DIR/bin/buildctl" --addr "$BK_ADDR" build \
    --frontend gateway.v0 --opt source="$FRONTEND" \
    --opt build-arg:HERMES_GIT_SHA="$PINNED_COMMIT" \
    --local context="$WORK/ctx" --local dockerfile="$WORK/ctx" \
    --output type=oci,dest="$WORK/image.tar",name="$IMAGE_TAG" >&2
rc=$?
[ "$rc" -eq 0 ] || { echo "s0-08: buildctl build failed (rc $rc)"; exit 2; }

podman rmi -f "$IMAGE_TAG" >/dev/null 2>&1 || true
podman load -i "$WORK/image.tar" || { echo "s0-08: podman load failed"; exit 5; }
rm -rf "$WORK/ctx" "$WORK/image.tar"

# --- verify the baked provenance == the pin (fail loud) ---
cid="$(podman create "$IMAGE_TAG" 2>/dev/null)" || { echo "s0-08: podman create failed"; exit 5; }
prov="$(podman cp "$cid:/etc/hermes/image-provenance.json" - 2>/dev/null | tar -xO 2>/dev/null || echo '')"
podman rm -f "$cid" >/dev/null 2>&1 || true
echo "s0-08: baked provenance: $prov"
printf '%s' "$prov" | python3 -c 'import json,sys
try: v=json.load(sys.stdin)
except Exception: raise SystemExit("s0-08: provenance not JSON")
raise SystemExit(0 if v.get("revision")=="'"$PINNED_COMMIT"'" else "s0-08: provenance revision != pin")' \
    || exit 2
echo "s0-08: built and loaded $IMAGE_TAG (provenance revision == $PINNED_COMMIT)"
echo "s0-08: now run: bash proofs/S0-08/tools/pc/run_containment.sh --image $IMAGE_TAG"
