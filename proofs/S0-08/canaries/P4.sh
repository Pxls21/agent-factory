#!/bin/sh
# S0-08 canary P4 — narrow mounts and no provider secrets in the runtime env.
#
# docs/05_SECURITY.md:56-72 requires "narrow mounts, no Docker socket/home/
# provider secrets". The secret pattern is the one S0-01 already pins,
# proofs/S0-01/pins.py:50 REDACTED_ENV_KEY_RE = (?i)(KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV).
# The pinned image sets NO env key matching it (Dockerfile ENV lines 57-428),
# so the expected count is 0 with an EMPTY allowlist.
#
# Emits ONE JSON line of OBSERVATIONS. The checker decides PASS/FAIL.
set -u

esc() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | tr -d '\000-\037'
}

# --- Docker socket ---
docker_sock="absent"
[ -e /var/run/docker.sock ] && docker_sock="present"
[ -e /run/docker.sock ] && docker_sock="present"

# --- Secret-bearing env keys in the RUNTIME env (this process's own) ---
# Names only. Values are NEVER printed or hashed (`env` output is cut at the first '=' before anything
# else sees it). The canary is exec'd inside the container as the runtime user — `podman exec --user 10000`
# (tools/pc/run_containment.sh), NOT the image's default `USER root` (Dockerfile:298) — so its own
# environment IS the env the main program inherits. Why `env` and not procfs: /proc/1/environ is
# root-owned 0400 (unreadable to uid 10000 in the container and to the owner's user on the PC — the
# 2026-09-08 PC gate hit that: rc 1, "did not complete its observation"), and under gVisor a shell
# redirect of /proc/self/environ read EMPTY in the sandbox (measured 2026-09-08: `tr < /proc/self/environ`
# 0 lines, `cat /proc/self/environ | tr` 2 lines, `env` 2 lines) — the libc environment is the surface
# that is the same everywhere.
secret_keys=$(env 2>/dev/null \
    | cut -d= -f1 \
    | grep -Ei 'KEY|TOKEN|SECRET|PASSWORD|NSEC|PRIV' \
    | sort \
    | tr '\n' ',' \
    | sed -e 's/,$//')
if [ -z "$secret_keys" ]; then
    secret_count=0
else
    secret_count=$(printf '%s' "$secret_keys" | tr ',' '\n' | grep -c .)
fi

# --- Mount census: record every mount SOURCE the container carries ---
mount_count=$(grep -c . /proc/self/mountinfo 2>/dev/null) || mount_count=0
# Bind mounts whose root is not "/" name a host subtree handed to the container.
host_binds=$(awk '{print $4}' /proc/self/mountinfo 2>/dev/null \
    | grep -v '^/$' \
    | sort -u \
    | tr '\n' ',' \
    | sed -e 's/,$//')

rc=0
command -v env >/dev/null 2>&1 || rc=1

printf '{"canary":"P4","expect":"no docker socket; 0 env keys matching the redaction pattern (allowlist empty)","observed":{"docker_sock":"%s","secret_env_count":"%s","secret_env_keys":"%s","mount_count":"%s","host_bind_roots":"%s"},"rc":%d}\n' \
    "$(esc "$docker_sock")" "$(esc "$secret_count")" "$(esc "$secret_keys")" \
    "$(esc "$mount_count")" "$(esc "$host_binds")" "$rc"
