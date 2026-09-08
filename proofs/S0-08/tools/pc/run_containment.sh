#!/usr/bin/env bash
# S0-08 containment runner — PC-SIDE. NOT run in the sandbox.
#
# Builds (or consumes) the pinned Hermes image, starts it under gVisor with the
# EXACT flags PC-BRIDGE.md:135-148 verified, runs every canary inside it via
# `podman exec`, and writes an evidence bundle that
# proofs/S0-08/check_containment.py can assert.
#
# Usage:
#   run_containment.sh [--image TAG] [--runtime PATH|crun] [--out DIR]
#                      [--source DIR] [--keep]
#
#   --image    consume a prebuilt tag instead of building
#              (default: build localhost/hermes-s0-08:527da608)
#   --runtime  /usr/local/bin/runsc (default) or `crun` for the NEGATIVE bundle
#   --out      evidence directory (default: proofs/S0-08/evidence/pc-runsc,
#              or .../pc-crun when --runtime crun)
#   --source   the pinned hermes-agent checkout (default: ~/s0-01-pinned/hermes-agent)
#   --keep     do not remove the container on exit (debugging)
#
# Exit codes:
#   0  evidence written
#   2  the image could not be built or pulled (the reason is named on stderr)
#   3  the runtime refused to start the container (the reason is named on stderr)
#   4  the container started but never became ready (the reason is named)
#  64  usage error
#
# Teardown removes the container BY ID. It never matches by name and never
# calls pkill: this is the owner's shared host (PC-BRIDGE.md:164-169, AF-AP-34).
#
# UNVERIFIED ON THE PC — read a red here as an ENVIRONMENT finding, not a
# containment failure: the invocation PC-BRIDGE.md:135-136 actually verified
# carries `--runtime-flag ignore-cgroups --security-opt label=disable` and NO
# `--network` flag at all (its note records working HTTPS from inside). This
# runner adds `--network none` (CONTAINMENT-SPEC.md P7), so rootless podman +
# runsc + `none` is the first thing that can fail on the first run.
set -euo pipefail

PINNED_COMMIT="527da60844d4dced37879ea50259675371abe10e"
IMAGE_TAG="localhost/hermes-s0-08:527da608"
RUNTIME="/usr/local/bin/runsc"
SOURCE_DIR="${HOME}/s0-01-pinned/hermes-agent"
OUT_DIR=""
KEEP=0
BUILD=1

# The container's main program, and the ONE source of that string: the
# readiness gate, the identity scan and canaries/P2.sh all read it from here
# (P2 through S0_08_MAIN_CMDLINE in the exec env), so it cannot drift.
#
# NOT `sleep infinity`: the image's supervised `main-hermes` service is a root
# no-op that runs exactly `exec sleep infinity`
# (hermes-agent docker/s6-rc.d/main-hermes/run:27) and is up by default
# (docker/s6-rc.d/user/contents.d/), so that cmdline had TWO holders — the
# root sleeper and the dropped CMD — and P2's subject was decided by /proc
# glob order.
MAIN_CMD="sleep 2147483647"

# Every canary is exec'd as the image's runtime user. Without `--user`,
# `podman exec` uses the image's configured user, which is `USER root`
# (Dockerfile:298) — P4 would then observe a root exec's environment and P5
# would attempt the host read as a different subject than the security
# profile is about.
CANARY_EXEC_UID="10000"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CANARY_DIR="$(cd "${HERE}/../../canaries" && pwd)"

while [ $# -gt 0 ]; do
    case "$1" in
        --image)   IMAGE_TAG="$2"; BUILD=0; shift 2 ;;
        --runtime) RUNTIME="$2"; shift 2 ;;
        --out)     OUT_DIR="$2"; shift 2 ;;
        --source)  SOURCE_DIR="$2"; shift 2 ;;
        --keep)    KEEP=1; shift ;;
        *) echo "usage: run_containment.sh [--image TAG] [--runtime PATH] [--out DIR] [--source DIR] [--keep]" >&2; exit 64 ;;
    esac
done

if [ -z "$OUT_DIR" ]; then
    case "$RUNTIME" in
        *runsc) OUT_DIR="${HERE}/../../evidence/pc-runsc" ;;
        *)      OUT_DIR="${HERE}/../../evidence/pc-crun" ;;
    esac
fi

CID=""
SENTINEL=""
cleanup() {
    # Remove the container BY ID only. Never by name, never pkill.
    if [ -n "$CID" ] && [ "$KEEP" -eq 0 ]; then
        podman rm -f "$CID" >/dev/null 2>&1 || true
    fi
    [ -n "$SENTINEL" ] && rm -f "$SENTINEL" 2>/dev/null || true
}
trap cleanup EXIT

# --- 0. The pinned-source preflight -----------------------------------------
# Evidence from a different checkout is evidence about a different system, so
# the build refuses one. It lives in a function taking BOTH the directory and
# the expected commit so a test can drive it against a scratch repository
# without having to forge a sha.
s0_08_require_pinned_source() {
    local dir="$1"
    local expected="$2"
    local actual
    if [ ! -f "${dir}/Dockerfile" ]; then
        echo "s0-08: no Dockerfile at ${dir} — cannot build the pinned image" >&2
        exit 2
    fi
    actual="$(git -C "$dir" rev-parse HEAD 2>/dev/null || echo unknown)"
    if [ "$actual" != "$expected" ]; then
        echo "s0-08: ${dir} is at ${actual}, expected the pinned ${expected}" >&2
        exit 2
    fi
}

# --- 1. The image -----------------------------------------------------------
if [ "$BUILD" -eq 1 ]; then
    s0_08_require_pinned_source "$SOURCE_DIR" "$PINNED_COMMIT"
    echo "s0-08: building ${IMAGE_TAG} from ${SOURCE_DIR} (Dockerfile as-is)" >&2
    if ! podman build -t "$IMAGE_TAG" "$SOURCE_DIR" >&2; then
        echo "s0-08: podman build failed for ${IMAGE_TAG}" >&2
        exit 2
    fi
fi

if ! podman image exists "$IMAGE_TAG"; then
    echo "s0-08: image ${IMAGE_TAG} is not present and was not built" >&2
    exit 2
fi

# --- 2. The host sentinel (the P5 positive control) -------------------------
# Written on the HOST, mounted NOWHERE. The runner proves it is readable here;
# the canary proves it is not readable inside. Neither half alone is evidence.
NONCE="$(od -An -N8 -tx1 /dev/urandom | tr -d ' \n')"
SENTINEL="${HOME}/s0-08-host-sentinel-${NONCE}"
printf 's0-08-host-sentinel %s\n' "$NONCE" > "$SENTINEL"
SENTINEL_READABLE=false
if [ -r "$SENTINEL" ] && [ -n "$(cat "$SENTINEL")" ]; then
    SENTINEL_READABLE=true
fi
if [ "$SENTINEL_READABLE" != true ]; then
    echo "s0-08: the host sentinel is not readable on the host — the P5 control is void" >&2
    exit 4
fi

# --- 3. Start the container -------------------------------------------------
# The flags are EXACTLY the two PC-BRIDGE.md:141-148 verified as required:
#   --runtime-flag ignore-cgroups   rootless runsc cannot set up cgroups here
#   --security-opt label=disable    runsc refuses an OCI spec with an SELinux label
# --network none: S0-08 asserts no egress property (that is S0-05's proof) and
# the production compose file's `network_mode: host` must NOT be inherited by a
# containment run. See CONTAINMENT-SPEC.md P7.
RUN_ARGV=(podman run -d
          --runtime "$RUNTIME"
          --security-opt label=disable
          --network none
          "$IMAGE_TAG" $MAIN_CMD)
if [ "${RUNTIME##*/}" = "runsc" ]; then
    RUN_ARGV=(podman run -d
              --runtime "$RUNTIME"
              --runtime-flag ignore-cgroups
              --security-opt label=disable
              --network none
              "$IMAGE_TAG" $MAIN_CMD)
fi

set +e
CID="$("${RUN_ARGV[@]}" 2>/tmp/s0-08-run.err)"
run_rc=$?
set -e
if [ "$run_rc" -ne 0 ] || [ -z "$CID" ]; then
    echo "s0-08: the runtime refused to start the container:" >&2
    sed -e 's/^/s0-08:   /' /tmp/s0-08-run.err >&2 || true
    CID=""
    exit 3
fi

# --- 4. Wait for s6 readiness ----------------------------------------------
# Derived from the image's own ordering (hermes-agent Dockerfile:441-444):
# /init runs cont-init.d, starts the s6-rc services, and only THEN exec's the
# main program. So the main program existing at uid 10000 means the whole
# supervised boot completed.
# The wait's exit condition includes the FAILURE signature: a container that
# has stopped ends the loop loudly instead of timing out in silence.
ready=0
for _ in $(seq 1 60); do
    state="$(podman inspect --format '{{.State.Status}}' "$CID" 2>/dev/null || echo missing)"
    if [ "$state" != "running" ]; then
        echo "s0-08: the container stopped before becoming ready (state=${state})" >&2
        podman logs "$CID" 2>&1 | tail -20 | sed -e 's/^/s0-08:   /' >&2 || true
        exit 4
    fi
    # POSIX /proc scan for the EXACT main-program cmdline. No pgrep: procps is
    # not guaranteed inside the image, and a name match is not an identity.
    if podman exec "$CID" sh -c 'for d in /proc/[0-9]*; do p=${d#/proc/}; c=$(tr "\0" " " < /proc/$p/cmdline 2>/dev/null | sed -e "s/ *$//"); [ "$c" = "'"$MAIN_CMD"'" ] && exit 0; done; exit 1' >/dev/null 2>&1; then
        ready=1
        break
    fi
    sleep 1
done
if [ "$ready" -ne 1 ]; then
    echo "s0-08: the container never started its main program within 60s" >&2
    podman logs "$CID" 2>&1 | tail -20 | sed -e 's/^/s0-08:   /' >&2 || true
    exit 4
fi

# --- 5. Record the runtime identity ----------------------------------------
mkdir -p "$OUT_DIR"

runsc_version=""
runsc_sha256=""
if [ -x "$RUNTIME" ]; then
    runsc_version="$("$RUNTIME" --version 2>/dev/null | head -n 1 | sed -e 's/^runsc version //')"
    runsc_sha256="$(sha256sum "$RUNTIME" | cut -d' ' -f1)"
elif [ -x /usr/local/bin/runsc ]; then
    # The negative (crun) bundle still records the runsc binary INSTALLED on the
    # host: the checker must catch a bundle whose identity looks right but whose
    # observations were taken outside gVisor.
    runsc_version="$(/usr/local/bin/runsc --version 2>/dev/null | head -n 1 | sed -e 's/^runsc version //')"
    runsc_sha256="$(sha256sum /usr/local/bin/runsc | cut -d' ' -f1)"
fi

podman_version="$(podman --version 2>/dev/null | head -n 1)"
image_digest="$(podman image inspect --format '{{.Digest}}' "$IMAGE_TAG" 2>/dev/null || echo unknown)"
host_kernel="$(uname -r)"
ps_tree="$(podman exec "$CID" sh -c 'ps -eo pid,user,comm,args 2>/dev/null || ps aux' 2>/dev/null || echo unavailable)"
main_id="$(podman exec "$CID" sh -c 'for d in /proc/[0-9]*; do p=${d#/proc/}; c=$(tr "\0" " " < /proc/$p/cmdline 2>/dev/null | sed -e "s/ *$//"); [ "$c" = "'"$MAIN_CMD"'" ] && id -u -n $(awk "/^Uid:/{print \$2; exit}" /proc/$p/status) 2>/dev/null && exit 0; done' 2>/dev/null || echo unknown)"
mainhermes_id="$(podman exec "$CID" sh -c 'command -v s6-svstat >/dev/null 2>&1 && s6-svstat /run/service/main-hermes 2>/dev/null || echo "s6-svstat unavailable"' 2>/dev/null || echo unknown)"

# Values are handed to Python through FILES, never interpolated into Python
# source: ps output and podman errors carry quotes and backslashes that would
# otherwise break (or inject into) the generated program.
META="$(mktemp -d)"
printf '%s' "$runsc_version"   > "$META/runsc_version"
printf '%s' "$runsc_sha256"    > "$META/runsc_sha256"
printf '%s' "$podman_version"  > "$META/podman_version"
printf '%s' "$image_digest"    > "$META/image_digest"
printf '%s' "$host_kernel"     > "$META/host_kernel"
printf '%s' "$ps_tree"         > "$META/ps_tree"
printf '%s' "$main_id"         > "$META/main_program_user"
printf '%s' "$mainhermes_id"   > "$META/main_hermes_service"
printf '%s' "$SENTINEL"        > "$META/sentinel_path"
printf '%s' "$SENTINEL_READABLE" > "$META/sentinel_readable"
printf '%s' "$CANARY_EXEC_UID" > "$META/canary_exec_user"
printf '%s' "$CID"             > "$META/container_id"
printf '%s' "$IMAGE_TAG"       > "$META/image"
printf '%s' "$RUNTIME"         > "$META/runtime"
printf '%s' "$PINNED_COMMIT"   > "$META/image_source_commit"
printf '%s' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$META/captured_at"
: > "$META/run_argv"
for arg in "${RUN_ARGV[@]}"; do printf '%s\0' "$arg" >> "$META/run_argv"; done

python3 - "$META" "$OUT_DIR/runtime-identity.json" <<'PYIDENT'
import json, sys
from pathlib import Path

meta, out = Path(sys.argv[1]), Path(sys.argv[2])


def val(name):
    return meta.joinpath(name).read_text(encoding="utf-8", errors="replace").strip()


argv_raw = meta.joinpath("run_argv").read_bytes().decode("utf-8", "replace")
run_argv = [a for a in argv_raw.split("\0") if a]

identity = {
    "venue": "pc-bridge:fedora",
    "captured_at": val("captured_at"),
    "runtime": val("runtime"),
    "runsc_version": val("runsc_version"),
    "runsc_sha256": val("runsc_sha256"),
    "runsc_path": val("runtime"),
    "podman_version": val("podman_version"),
    "image": val("image"),
    "image_digest": val("image_digest"),
    "image_source_commit": val("image_source_commit"),
    "run_argv": run_argv,
    "host_kernel": val("host_kernel"),
    "container_id": val("container_id"),
    "main_program_user": val("main_program_user"),
    "main_hermes_service": val("main_hermes_service"),
    "ps_tree": meta.joinpath("ps_tree").read_text(encoding="utf-8", errors="replace"),
    "canary_exec_user": val("canary_exec_user"),
    # The MEASURED host read (run_containment.sh SENTINEL_READABLE), never a
    # typed literal: a positive control the producer asserts about itself is
    # not a control.
    "sentinel_host_read": {"path": val("sentinel_path"),
                           "readable": val("sentinel_readable") == "true"},
}
out.write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PYIDENT
rm -rf "$META"
# --- 6. Run every canary inside the container ------------------------------
# The scripts are piped in on stdin: nothing is mounted into the container, so
# the canary directory itself never becomes a bind mount P4 would have to
# excuse.
: > "$OUT_DIR/canaries.jsonl"
for canary in P1 P2 P3 P4 P5 P6 P7 P8; do
    script="${CANARY_DIR}/${canary}.sh"
    if [ ! -f "$script" ]; then
        echo "s0-08: canary ${canary} is missing at ${script}" >&2
        exit 4
    fi
    # No pipeline between `podman exec` and `$?`: a piped status is `tail`'s,
    # which is always 0, so a canary that died after printing would be
    # indistinguishable from one that succeeded.
    set +e
    raw="$(podman exec -i --user "$CANARY_EXEC_UID" \
              -e S0_08_SENTINEL_PATH="$SENTINEL" \
              -e S0_08_MAIN_CMDLINE="$MAIN_CMD" \
              "$CID" sh -s < "$script" 2>/tmp/s0-08-canary.err)"
    exec_rc=$?
    set -e
    if [ "$exec_rc" -ne 0 ]; then
        echo "s0-08: canary ${canary} exec failed (rc ${exec_rc}):" >&2
        sed -e 's/^/s0-08:   /' /tmp/s0-08-canary.err >&2 || true
        exit 4
    fi
    line="$(printf '%s\n' "$raw" | tail -n 1)"
    if [ -z "$line" ]; then
        echo "s0-08: canary ${canary} produced no output" >&2
        exit 4
    fi
    printf '%s\n' "$line" >> "$OUT_DIR/canaries.jsonl"
done

echo "s0-08: evidence written to ${OUT_DIR}" >&2
echo "s0-08: now run: python3 proofs/S0-08/check_containment.py ${OUT_DIR}" >&2
exit 0
