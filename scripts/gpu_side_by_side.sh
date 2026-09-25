#!/usr/bin/env bash
# gpu_side_by_side.sh — ONE side-by-side configuration inside a GPU window (task #262; D-087, D-088): a TEMPORARY Qwen
# vLLM server, started from the live unit's own definition with a smaller GPU share, beside the RWKV-7 stream reader.
# Runs ON the PC as a job of scripts/gpu_window.sh, which has stopped qwen.service, seen the GPU free, and ALWAYS starts
# the service again when the jobs end. Refuses (exit 3, nothing started) outside such a window: a container named qwen
# exists, the GPU's memory.used is at or over GPU_FREE_MIB (default 1500, the runner's rule), or nvidia-smi gives no
# reading. Also exit 3 when the unit cannot be copied as it is: Image= not digest-pinned (@sha256:), ContainerName= not
# qwen, Exec= not batch, a [Container] key or a PodmanArgs token this job does not copy, no read-only key mount at
# /app/api_key.txt, or VLLM_API_KEY anywhere in it; or when the probe's Python, the probe or the key file is missing.
# Then:
#   1. starts the temporary server: the unit's volumes, environment, device and IPC arguments, plus GPU_UTIL=U,
#      published on 127.0.0.1:8081 only, command batch, --rm, named qwen (the run line says why); log DIR/qwen.log
#   2. waits up to BOOT_SECONDS (900) for /v1/models to answer 200; the key goes in a header read from the unit's own
#      key file through a process substitution, never argv or a log (gpu_window.sh's models_answer; AF-AP-39)
#   3. records the server's own sizing from `podman logs qwen` as numbers; a missing line is a recorded failure (exit 1)
#   4. runs the reader probe once (docs/research/findings/jev-pipes/rwkv_sbs_probe.py), which measures every phase
#   5. merges the configuration, the sizing and the probe's record into DIR/summary.json with an rc
# ALWAYS removes the temporary container once (podman rm -f -i qwen, bounded): on exit, on a failed phase, and on INT or
# TERM, with INT and TERM ignored while it cleans up; the runner gives a job 30 s after TERM before KILL
# (gpu_window.sh:159). Every inner timeout is --foreground: a new process group would hide its child from the window's
# TERM and KILL.
#   usage: gpu_side_by_side.sh --util U --chunk C --tokens T --load N --out DIR
#          U a decimal 0.50-0.97 · C 1024-16384 · T C-65536 · N 0-8 concurrent Qwen requests (0: no load)
#   exit: 0 every phase produced its measurement · 1 a phase failed or a measurement is missing · 3 refused, nothing
#         started · 64 usage · 130 stopped by INT or TERM
# Test seams, checked before anything starts: SBS_PORT (8081), BOOT_SECONDS (900, at most 3600), GPU_FREE_MIB (1500),
# SBS_RM_SECONDS (20, at most 20: with its 2 s KILL grace and the reader's 2 s it stays inside the runner's 30 s),
# SBS_PYTHON (~/venv-rwkv-b/bin/python), SBS_PROBE (the probe above).
set -uo pipefail
usage() { echo "usage: gpu_side_by_side.sh --util U --chunk C --tokens T --load N --out DIR" >&2; exit 64; }
UTIL="" CHUNK="" TOKENS="" LOAD="" OUT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --util|--chunk|--tokens|--load|--out)
      [ $# -ge 2 ] && [ -n "$2" ] || usage
      v="${1#--}"; v="${v^^}"                 # --util -> UTIL
      [ -z "${!v}" ] || usage                 # each flag once
      printf -v "$v" '%s' "$2"; shift 2;;
    -h|--help) sed -n '2,/^set -uo pipefail/p' "$0" | sed '$d'; exit 64;;
    *) usage;;
  esac
done
[ -n "$UTIL" ] && [ -n "$CHUNK" ] && [ -n "$TOKENS" ] && [ -n "$LOAD" ] && [ -n "$OUT" ] || usage
num() {                                     # num VAR LABEL LO HI: VAR a whole number in LO-HI, read as decimal (a
  local v="${!1}"                           # leading zero is not octal; gpu_window.sh F-7)
  case "$v" in ''|*[!0-9]*) echo "gpu_side_by_side: $2 needs a whole number" >&2; exit 64;; esac
  [ "${#v}" -le 6 ] || { echo "gpu_side_by_side: $2 is too large" >&2; exit 64; }
  v=$((10#$v))
  [ "$v" -ge "$3" ] && [ "$v" -le "$4" ] || { echo "gpu_side_by_side: $2 must be $3-$4" >&2; exit 64; }
  printf -v "$1" '%d' "$v"
}
[[ "$UTIL" =~ ^0\.([0-9]{1,3})$ ]] || { echo "gpu_side_by_side: --util needs a decimal such as 0.90" >&2; exit 64; }
milli="${BASH_REMATCH[1]}00"; milli=$((10#${milli:0:3}))
[ "$milli" -ge 500 ] && [ "$milli" -le 970 ] || { echo "gpu_side_by_side: --util must be 0.50-0.97" >&2; exit 64; }
num CHUNK --chunk 1024 16384
num TOKENS --tokens "$CHUNK" 65536
num LOAD --load 0 8
PORT="${SBS_PORT:-8081}"; num PORT SBS_PORT 1024 65535
BOOT_S="${BOOT_SECONDS:-900}"; num BOOT_S BOOT_SECONDS 0 3600
FREE_MIB="${GPU_FREE_MIB:-1500}"; num FREE_MIB GPU_FREE_MIB 1 99999
RM_S="${SBS_RM_SECONDS:-20}"; num RM_S SBS_RM_SECONDS 1 20
mkdir -p -- "$OUT" 2>/dev/null && [ -w "$OUT" ] || { echo "gpu_side_by_side: cannot write --out $OUT" >&2; exit 64; }
OUT="$(cd -- "$OUT" && pwd)"
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${SBS_PYTHON:-$HOME/venv-rwkv-b/bin/python}"
PROBE="${SBS_PROBE:-$ROOT/docs/research/findings/jev-pipes/rwkv_sbs_probe.py}"
UNIT_FILE="$HOME/.config/containers/systemd/qwen.container"
MODELS_URL="http://127.0.0.1:$PORT/v1/models"

gpu_used() {                                # memory.used in MiB, bounded; only a first line that is a number is a
  local out                                 # reading, never the digits of an error line (gpu_window.sh F-10)
  out="$(timeout --foreground -k 2 10 nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)"
  [[ "$out" =~ ^[[:space:]]*([0-9]+)[[:space:]]*$ ]] && echo "${BASH_REMATCH[1]}"
}
timeout --foreground -k 2 20 podman container exists qwen > /dev/null 2>&1; ex=$?
[ "$ex" != 0 ] || { echo "gpu_side_by_side: refusing, a container named qwen exists: not inside a GPU window" >&2; exit 3; }
[ "$ex" = 1 ] || { echo "gpu_side_by_side: refusing, podman cannot tell whether a container named qwen exists (rc $ex)" >&2
  exit 3; }
used="$(gpu_used)"
[ -n "$used" ] || { echo "gpu_side_by_side: refusing, nvidia-smi gives no reading" >&2; exit 3; }
[ "$used" -lt "$FREE_MIB" ] || { echo "gpu_side_by_side: refusing, the GPU holds $used MiB (at or over $FREE_MIB): not inside a GPU window" >&2
  exit 3; }

# The unit's [Container] section, parsed with systemd's quoting; the copied arguments come back one per line. Messages
# never echo an Environment= value.
unit="$(python3 - "$UNIT_FILE" <<'PY'
import re, shlex, sys
COPIED = {"ContainerName", "Image", "Exec", "PublishPort", "Volume", "Environment", "PodmanArgs"}


def refuse(why):
    sys.stderr.write("gpu_side_by_side: refusing, %s\n" % why)
    sys.exit(3)


try:
    with open(sys.argv[1], encoding="utf-8") as fh:
        lines = fh.read().splitlines()
except OSError as e:
    refuse("cannot read the unit %s (%s)" % (sys.argv[1], e.strerror))
section, items = None, []
for n, raw in enumerate(lines, 1):
    s = raw.strip()
    if not s or s[0] in "#;":
        continue
    if s.startswith("[") and s.endswith("]"):
        section = s[1:-1]
        continue
    if section != "Container":
        continue
    if "VLLM_API_KEY" in s:
        refuse("the unit's line %d names VLLM_API_KEY: copying it would put the key in podman's argv" % n)
    if s.endswith("\\"):
        refuse("the unit's line %d continues on the next line, which this job does not parse" % n)
    key, eq, value = s.partition("=")
    if not eq or key.strip() not in COPIED:
        refuse("the unit's [Container] key %r is not one this job copies; extend the job first" % key.strip())
    items.append((key.strip(), value.strip()))


def one(key):
    vals = [v for k, v in items if k == key]
    if len(vals) != 1:
        refuse("the unit needs exactly one %s= (it has %d)" % (key, len(vals)))
    return vals[0]


def words(key, value):
    try:
        return shlex.split(value)
    except ValueError:
        refuse("a %s= line of the unit does not parse" % key)


if one("ContainerName") != "qwen":
    refuse("the unit's ContainerName= is not qwen, so its --replace would not remove a leftover of this job")
if one("Exec") != "batch":
    refuse("the unit's Exec= is not batch, the command this job runs")
image = one("Image")
cport = one("PublishPort").split("/")[0].rsplit(":", 1)[-1]
if not cport.isdigit():
    refuse("the unit's PublishPort= names no container port")
args, keys = [], []
for k, v in items:
    if k == "Volume":
        parts = v.split(":")
        if len(parts) < 2 or not parts[0] or not parts[1]:
            refuse("the unit's Volume=%s is not source:target" % v)
        if parts[1] == "/app/api_key.txt":
            if "ro" not in (parts[2].split(",") if len(parts) > 2 else []):
                refuse("the unit's key mount at /app/api_key.txt is not read-only")
            keys.append(parts[0])
        args += ["-v", v]
    elif k == "Environment":
        for i, w in enumerate(words(k, v)):
            if not re.match(r"[A-Za-z_][A-Za-z0-9_]*=", w):
                refuse("word %d of an Environment= line of the unit is not NAME=value" % (i + 1))
            args += ["-e", w]
    elif k == "PodmanArgs":
        toks, i = words(k, v), 0
        while i < len(toks):
            if re.fullmatch(r"--(ipc|device)=\S+", toks[i]):
                args.append(toks[i])
                i += 1
            elif toks[i] in ("--ipc", "--device") and i + 1 < len(toks):
                args += toks[i:i + 2]
                i += 2
            else:
                refuse("the unit's PodmanArgs token %s is not a device or IPC argument this job copies"
                       % toks[i].split("=", 1)[0])
if len(keys) != 1:
    refuse("the unit needs exactly one read-only key mount at /app/api_key.txt (it has %d)" % len(keys))
print("\n".join([keys[0], image, cport] + args))
PY
)" || exit 3
mapfile -t U <<< "$unit"
KEY_FILE="${U[0]}" IMAGE="${U[1]}" CPORT="${U[2]}"
UARGS=("${U[@]:3}")
[[ "$IMAGE" =~ ^[^@[:space:]]+@sha256:[0-9a-f]{64}$ ]] || {
  echo "gpu_side_by_side: refusing, the unit's Image= is not digest-pinned (@sha256:): $IMAGE" >&2; exit 3; }
[ -r "$KEY_FILE" ] || { echo "gpu_side_by_side: refusing, the unit's key file is not readable here: $KEY_FILE" >&2; exit 3; }
[ -x "$PY" ] || { echo "gpu_side_by_side: refusing, no Python at $PY" >&2; exit 3; }
[ -f "$PROBE" ] || { echo "gpu_side_by_side: refusing, no probe at $PROBE" >&2; exit 3; }

models_answer() {                           # the key goes through a pipe as a header file, never argv (AF-AP-39)
  curl -s -m 5 --noproxy '*' -o /dev/null -w '%{http_code}' \
    -H @<(printf 'Authorization: Bearer %s\n' "$(cat "$KEY_FILE")") "$MODELS_URL" 2>/dev/null | grep -qx 200
}
alive() {                                   # a zombie holds nothing: kill -0 alone would call it alive
  local s; s="$(sed 's/.*) //' "/proc/$1/stat" 2>/dev/null | cut -d' ' -f1)"
  [ -n "$s" ] && [ "$s" != Z ]
}
STARTED_AT="$(date -u +%FT%TZ)"
cleaned=0 probepid="" followpid="" BOOT_TOOK="" RM_RC="" PROBE_RC=""
cleanup() {                                 # once; INT and TERM stay ignored from here to the exit (AF-AP-145)
  trap '' INT TERM
  [ "$cleaned" = 1 ] && return
  cleaned=1
  if [ -n "$probepid" ]; then               # a background job ignores INT, and a TERM sent to this shell alone never
    kill -TERM "$probepid" 2>/dev/null      # reaches it: an orphaned reader would hold GPU memory the service needs
    local i; for i in 1 2 3 4 5 6 7 8 9 10; do alive "$probepid" || break; sleep 0.2; done
    kill -KILL "$probepid" 2>/dev/null
  fi
  timeout --foreground -k 2 "$RM_S" podman rm -f -i qwen >> "$OUT/cleanup.log" 2>&1; RM_RC=$?
  [ -z "$followpid" ] || kill "$followpid" 2>/dev/null
}
# summary RC WHY: writes DIR/summary.json and prints the final rc. RC 0 stays 0 only when the sizing and every phase
# say ok and the removal worked.
summary() {
  python3 - "$OUT" "$1" "$2" "$UTIL" "$CHUNK" "$TOKENS" "$LOAD" "$PORT" "$IMAGE" "$STARTED_AT" "$BOOT_TOOK" \
    "$RM_RC" "$PROBE_RC" <<'PY'
import json, os, sys, time
out, rc, why, util, chunk, tokens, load, port, image, started, boot, rm_rc, probe_rc = sys.argv[1:14]
rc = int(rc)


def read(name):
    try:
        with open(os.path.join(out, name), encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as e:
        return {"unreadable": "%s: %s" % (type(e).__name__, e)}


def whole(s):
    return int(s) if s.isdigit() else None


sizing, probe = read("sizing.json"), read("probe.json")
if rc == 0:
    bad = [p for p in ("alone", "qwen_idle_rwkv", "together")
           if not (isinstance(probe, dict) and isinstance(probe.get(p), dict) and probe[p].get("ok") is True)]
    if not (isinstance(sizing, dict) and sizing.get("ok") is True):
        rc, why = 1, "sizing: a line is missing or invalid, or the share is not the configured one"
    elif bad:
        rc, why = 1, "probe: no measurement from " + ", ".join(bad)
    elif whole(rm_rc) != 0:
        rc, why = 1, "cleanup: podman rm -f -i qwen returned rc %s" % rm_rc
rec = {"job": "gpu_side_by_side", "rc": rc, "reason": why or None, "started": started,
       "finished": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "config": {"util": float(util), "chunk": int(chunk), "tokens": int(tokens), "load": int(load), "port": int(port),
                  "image": image},
       "boot_seconds": whole(boot), "sizing": sizing, "probe_rc": whole(probe_rc), "probe": probe,
       "cleanup": {"podman_rm_rc": whole(rm_rc)}}
tmp = os.path.join(out, "summary.json.tmp")
with open(tmp, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
os.replace(tmp, os.path.join(out, "summary.json"))
print(rc)
PY
}
leave() { trap '' INT TERM; exit "$1"; }    # every exit once the traps are armed ignores INT and TERM first (AF-AP-145)
finish() {                                  # $1 rc, $2 why (empty when every step ran): cleanup, summary, exit
  cleanup
  local final; final="$(summary "$1" "$2")"
  [[ "$final" =~ ^[0-9]+$ ]] || final=1
  leave "$final"
}
on_signal() { cleanup; summary 130 "stopped by $1" > /dev/null; leave 130; }
on_exit() { [ "$cleaned" = 1 ] || { cleanup; summary "$1" "exited unexpectedly (rc $1)" > /dev/null; }; }
trap 'on_exit $?' EXIT
trap 'trap "" INT TERM; on_signal INT' INT  # the ignore first: a second signal must not re-run the handler
trap 'trap "" INT TERM; on_signal TERM' TERM

# The temporary server is named qwen ON PURPOSE: the unit's ExecStart runs `podman run --name qwen --replace`, so the
# runner's restore removes a leftover of this job even when the job was killed before its own cleanup ran. The key
# reaches the server only through the unit's read-only file mount, never -e VLLM_API_KEY (that is podman's argv).
# --pull=never: the digest is the one the live unit runs, so it is here already; a pull would spend the window.
timeout --foreground -k 5 120 podman run -d --rm --pull=never --name qwen -p "127.0.0.1:$PORT:$CPORT" "${UARGS[@]}" \
  -e "GPU_UTIL=$UTIL" "$IMAGE" batch > "$OUT/podman-run.log" 2>&1; rc=$?
[ "$rc" = 0 ] || finish 1 "podman run: rc $rc (see podman-run.log)"
podman logs -f qwen > "$OUT/qwen.log" 2>&1 < /dev/null &   # the whole log survives the --rm of a crashed server
followpid=$!
t0=$SECONDS
until models_answer; do
  [ $((SECONDS - t0)) -lt "$BOOT_S" ] || finish 1 "boot: $MODELS_URL did not answer 200 within ${BOOT_S}s"
  timeout --foreground -k 2 20 podman container exists qwen || finish 1 "boot: the server exited (see qwen.log)"
  sleep 5
done
BOOT_TOOK=$((SECONDS - t0))

timeout --foreground -k 2 30 podman logs qwen > "$OUT/qwen-boot.log" 2>&1
python3 - "$OUT/qwen-boot.log" "$UTIL" > "$OUT/sizing.json" <<'PY'
import json, math, re, sys
text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
util = float(sys.argv[2])
NUM = r"([0-9][0-9,]*(?:\.[0-9]+)?)"
REQUIRED = {                                           # name: (pattern, type); the last match counts
    "available_kv_gib": (r"Available KV cache memory:\s*%s\s*GiB" % NUM, float),
    "kv_tokens": (r"GPU KV cache size:\s*%s\s*tokens" % NUM, int),
    "max_concurrency": (r"Maximum concurrency for\s*[0-9][0-9,]*\s*tokens per request:\s*%sx" % NUM, float),
    "desired_util": (r"Desired GPU memory utilization is \(%s," % NUM, float),
    "desired_gib": (r"Desired GPU memory utilization is \([0-9.]+,\s*%s\s*GiB\)" % NUM, float),
}
OPTIONAL = {
    "max_concurrency_tokens_per_request": (r"Maximum concurrency for\s*%s\s*tokens per request" % NUM, int),
    "startup_free_gib": (r"Free memory on device \(%s/" % NUM, float),
    "startup_total_gib": (r"Free memory on device \([0-9.]+/%s\s*GiB\)" % NUM, float),
    "consumed_gib": (r"%s GiB for consumed memory" % NUM, float),
    "peak_activation_gib": (r"%s GiB for peak activation" % NUM, float),
    "cudagraph_gib": (r"%s GiB for CUDAGraph memory" % NUM, float),
    "model_loading_gib": (r"Model loading took\s*%s\s*GiB" % NUM, float),
}


def parse(pattern, kind):
    found = re.findall(pattern, text)
    if not found:
        return None, "missing"
    try:
        v = kind(found[-1].replace(",", ""))
    except ValueError:
        return None, "invalid"
    return (v, None) if math.isfinite(v) and v > 0 else (None, "invalid")   # never a zero, never NaN


rec, missing, invalid = {}, [], []
for name, (pattern, kind) in REQUIRED.items():
    rec[name], bad = parse(pattern, kind)
    if bad == "missing":
        missing.append(name)
    elif bad == "invalid":
        invalid.append(name)
for name, (pattern, kind) in OPTIONAL.items():
    rec[name] = parse(pattern, kind)[0]
rec["util_applied"] = rec["desired_util"] is not None and abs(rec["desired_util"] - util) < 1e-6
rec["lines"] = {}
for phrase in ("Available KV cache memory", "GPU KV cache size", "Maximum concurrency for",
               "Desired GPU memory utilization is", "Model loading took"):
    hits = [ln.strip() for ln in text.splitlines() if phrase in ln]
    rec["lines"][phrase] = hits[-1][:500] if hits else None
rec.update(missing=missing, invalid=invalid, ok=not missing and not invalid and rec["util_applied"])
print(json.dumps(rec, indent=1, sort_keys=True))
sys.exit(0 if rec["ok"] else 1)
PY
SIZING_RC=$?

"$PY" "$PROBE" --tokens "$TOKENS" --chunk "$CHUNK" --load "$LOAD" --url "http://127.0.0.1:$PORT/v1/chat/completions" \
  --key-file "$KEY_FILE" --out "$OUT/probe.json" > "$OUT/probe.log" 2>&1 < /dev/null &
probepid=$!
wait "$probepid"; PROBE_RC=$?; probepid=""
[ "$PROBE_RC" = 0 ] || finish 1 "probe: rc $PROBE_RC (see probe.log)"
[ "$SIZING_RC" = 0 ] || finish 1 "sizing: a line is missing or invalid, or the share is not the configured one"
finish 0 ""
