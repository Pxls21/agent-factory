#!/bin/bash
# abwin2.sh - the second GPU window of task #454 (D-127, D-129; window rules D-088).
# Usage: abwin2.sh <workload-1.json> <workload-2.json>
#   workload-1: window 1's four long chats (first prompts 57k to 87k tokens); workload-2: eight chats of lane size
#   (first prompts 20k to 58k). Both come from make_workload.py, sized with vLLM's own tokenizer while vLLM serves.
# The questions (report section J4): does a retry after OmniRoute's 80 s cut reuse the chunks the server already
# computed; does lpm scheduling stop warm turns queueing behind cold prefills; how do 6 and 8 chats fare with 4
# running slots; does a prefill chunk of 8192 without the prefill CUDA graph shorten a cold prefill.
# Arms (vLLM's numbers are window 1's; the switch stands, D-129):
#   S2  window 1's S1 (the 4-stream flags plus HiCache) with --schedule-policy lpm and --enable-cache-report
#   S3  S2 with --disable-prefill-cuda-graph and a prefill chunk of 8192
# A cut run cuts an attempt with no first event at 80 s and sends it again, up to 3 times (chat_load.py --cut-after 80
# --retries 3), as OmniRoute and Hermes do.
# Built from abwin.sh (window 1). Changed: the plan; a warm-up request after each boot, so first-use kernel builds do
# not land in a measured run; a deadline after which no run starts (lanes wait for the GPU); a cap on each run.
# vLLM is restored on every exit (the EXIT trap); the test port binds 127.0.0.1 only.
# ABWIN_ARMS (default "S2 S3") names the arms to run. Window 2 ran S2, and S3's boot failed: S2's container outlived
# two `podman rm -f` calls whose output was dropped, and `podman run` refused its name. gone() now removes the
# container and waits until podman says it is gone, with rm's error lines in the log.
set -u
WL1=${1:?usage: abwin2.sh <workload-1.json> <workload-2.json>}
WL2=${2:?usage: abwin2.sh <workload-1.json> <workload-2.json>}
for f in "$WL1" "$WL2"; do
  [ -s "$f" ] || { echo "abwin2: no workload file: $f" >&2; exit 2; }
done
ARMS=${ABWIN_ARMS-S2 S3}
for a in $ARMS; do
  case "$a" in S2|S3) ;; *) echo "abwin2: ABWIN_ARMS names an unknown arm: $a" >&2; exit 2 ;; esac
done
[ -n "${ARMS// /}" ] || { echo "abwin2: ABWIN_ARMS names no arm" >&2; exit 2; }
want() { case " $ARMS " in *" $1 "*) return 0 ;; esac; return 1; }
export XDG_RUNTIME_DIR=/run/user/$(id -u)
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT=$HOME/sglang-ab/$STAMP
mkdir -p "$OUT"
LOG=$OUT/window.log
log() { echo "$(date -u +%FT%TZ) $*" >> "$LOG"; }
KEYF=$HOME/.config/qwen-builder/api-key
CL=$(cd "$(dirname "$0")" && pwd)/chat_load.py
IMG=ghcr.io/0xsero/sglang-exl3@sha256:84f75f3424c99a3d63392a4e0348292bdeba9cf7efba2ff1aa9b85c8fc0131e8
MODEL=$HOME/models/qwen3.8-27b-exl3-3.0bpw
MNT=/models/turboderp-Qwen3.8-27B-exl3-3.00bpw
TPORT=18080
NAME=sglang-ab
DEADLINE=$(( $(date +%s) + ${ABWIN_MINUTES:-140} * 60 ))  # no run starts after it
RUN_CAP=1800  # seconds; one run's ceiling

restore() {
  trap '' INT TERM
  gone  # a GONE-TIMEOUT is logged; vLLM starts either way
  systemctl --user start qwen
  for i in $(seq 1 120); do
    if python3 - "$KEYF" <<'PY'
import sys, urllib.request
key = open(sys.argv[1]).read().strip()
req = urllib.request.Request("http://127.0.0.1:8080/v1/models", headers={"Authorization": "Bearer " + key})
try:
    ok = b"qwen3.8-27b-local" in urllib.request.urlopen(req, timeout=5).read()
except OSError:
    ok = False
sys.exit(0 if ok else 1)
PY
    then
      log "RESTORED vLLM serves qwen3.8-27b-local after ${i}0 s"; return; fi
    sleep 10
  done
  log "RESTORE-FAILED vLLM did not answer /v1/models in 20 min"
}
leave() { trap '' INT TERM; exit "$1"; }  # every exit once the traps are armed (AF-AP-145)

gone() { # the test container is removed, and podman says so, within 180 s; rm's error lines go to the log
  local i
  for i in $(seq 1 36); do
    podman container exists "$NAME"; [ $? = 1 ] && return 0  # 1: no such container (125, an error, is not gone)
    podman rm -f "$NAME" 2>&1 >/dev/null | sed 's/^/podman rm: /' >> "$LOG"
    sleep 5
  done
  log "GONE-TIMEOUT: the container $NAME is still there after 180 s"; return 1
}

load() { # arm workload chats label [chat_load flags]; returns 1 when the deadline has passed
  local arm=$1 wl=$2 c=$3 label=$4 dir
  shift 4
  dir=$OUT/$arm-$label
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then
    log "SKIP $arm $label: past the window's deadline"; return 1; fi
  log "LOAD $arm $label chats=$c start"
  timeout "$RUN_CAP" python3 "$CL" --arm "$arm" --base-url "http://127.0.0.1:$TPORT/v1" --model qwen3.8-27b-local \
    --workload "$wl" --chats "$c" --stagger-s 20 --timeout 600 --nvsmi "$@" --out "$dir" > "$dir.stdout" 2>&1
  log "LOAD $arm $label chats=$c rc=$? $(tail -1 "$dir.stdout" | cut -c1-600)"
}

unanswered_over_half() { # run dir; true when more than half its requests had no first event on any attempt
  python3 - "$1/summary.json" <<'PY'
import json, sys
try:
    s = json.load(open(sys.argv[1]))
except (OSError, ValueError):
    sys.exit(0)  # no summary: the run hit its cap or died
sys.exit(0 if s["requests"] and s["unanswered"] * 2 > s["requests"] else 1)
PY
}

warmup() { # arm; one short request after a boot (its own run id, so it shares no cache with a measured run)
  log "WARMUP $1 $(python3 - "$WL1" "$TPORT" <<'PY'
import json, sys, time, urllib.request
wl = json.load(open(sys.argv[1]))
system = wl["system"].replace(wl["run_id_line"], "Run id: warm-up.", 1)
body = {"model": "qwen3.8-27b-local", "max_tokens": 16, "temperature": 0,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": "Say OK."}],
        "chat_template_kwargs": {"enable_thinking": False}}
req = urllib.request.Request(f"http://127.0.0.1:{sys.argv[2]}/v1/chat/completions", data=json.dumps(body).encode(),
                             headers={"Content-Type": "application/json"})
t0 = time.monotonic()
try:
    urllib.request.urlopen(req, timeout=600).read()
    print(f"answered in {time.monotonic() - t0:.1f} s")
except OSError as e:
    print(f"failed: {type(e).__name__}")
PY
)"
}

sgl_up() { # name of the arm; the rest are extra launch flags; env pairs go first as -e args via ENVS
  local arm=$1 rc; shift
  gone || { log "BOOT-FAILED $arm: the previous $NAME container is still there"; return 1; }
  podman run -d --name "$NAME" --device nvidia.com/gpu=all --ipc=host \
    -p 127.0.0.1:$TPORT:30000 \
    -e CUDA_DEVICE_ORDER=PCI_BUS_ID -e HF_HUB_OFFLINE=1 -e SGLANG_EXL3_EMBED_HOST=1 -e SGLANG_EXL3_KERNEL=auto \
    -e SGLANG_EXL3_MODEL_PATH=$MNT ${ENVS:-} \
    -v "$MODEL:$MNT:ro" --entrypoint /opt/entrypoint.sh "$IMG" \
    python3 -m sglang.launch_server --model-path $MNT --quantization exl3 --trust-remote-code \
    --host 0.0.0.0 --port 30000 --served-model-name qwen3.8-27b-local \
    --kv-cache-dtype fp8_e4m3 --mamba-ssm-dtype bfloat16 \
    --reasoning-parser qwen3 --tool-call-parser qwen3_coder \
    --speculative-algorithm NEXTN --speculative-num-steps 3 --speculative-eagle-topk 1 \
    --speculative-num-draft-tokens 4 --speculative-token-map /opt/sglang-exl3/tokenmaps/qwen38_hot32k_v2.pt \
    --enable-metrics "$@" >> "$LOG" 2>&1
  rc=$?
  [ "$rc" = 0 ] || { log "BOOT-FAILED $arm: podman run exited $rc"; return 1; }
  for i in $(seq 1 150); do
    if ! podman ps --format '{{.Names}}' | grep -qx "$NAME"; then
      log "BOOT-FAILED $arm: the container exited"; podman logs --tail 60 "$NAME" > "$OUT/$arm-boot.log" 2>&1; return 1; fi
    if curl -s -m 5 http://127.0.0.1:$TPORT/v1/models | grep -q qwen3.8-27b-local; then
      log "UP $arm after ${i}0 s; $(nvidia-smi --query-gpu=memory.used --format=csv,noheader)"
      podman logs "$NAME" 2>&1 | grep -iE 'KV Cache is allocated|Mamba Cache|max_total_num_tokens|max_running_requests|hicache|Capture' \
        | tail -12 > "$OUT/$arm-boot-facts.txt"
      return 0; fi
    sleep 10
  done
  log "BOOT-TIMEOUT $arm after 25 min"; podman logs --tail 60 "$NAME" > "$OUT/$arm-boot.log" 2>&1; return 1
}

sgl_down() { # arm
  podman logs "$NAME" > "$OUT/$1-server.log" 2>&1
  grep -ciE 'retract' "$OUT/$1-server.log" | sed "s/^/retract-lines /" >> "$LOG"
  grep -ciE 'abort' "$OUT/$1-server.log" | sed "s/^/abort-lines /" >> "$LOG"
  grep -ciE 'out of memory|CUDA error|Traceback' "$OUT/$1-server.log" | sed "s/^/error-lines /" >> "$LOG"
  gone
}

trap restore EXIT
trap 'trap "" INT TERM; log "signal; restoring"; exit 1' INT TERM  # the ignore first (AF-AP-145)
log "WINDOW start; arms $ARMS; workloads $WL1 $(sha256sum "$WL1" | cut -c1-16) $WL2 $(sha256sum "$WL2" | cut -c1-16); out $OUT; deadline $(date -u -d @$DEADLINE +%TZ); gpu: $(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader | tr '\n' ' ')"

# the window proper: vLLM stops here and comes back in restore()
systemctl --user stop qwen
for i in $(seq 1 30); do
  nvidia-smi --query-compute-apps=pid --format=csv,noheader | grep -q . || break
  [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)" -lt 1500 ] && break
  sleep 5
done
log "vLLM stopped; gpu: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader)"

CUT="--cut-after 80 --retries 3"
BASE="--context-length 131072 --mem-fraction-static 0.80 --max-running-requests 4 --max-mamba-cache-size 12
    --cuda-graph-max-bs-decode 4 --prefill-decode-interval 16 --mamba-radix-cache-strategy no_buffer
    --disable-overlap-schedule --enable-hierarchical-cache --hicache-size 24 --hicache-write-policy write_through
    --schedule-policy lpm --enable-cache-report"
ENVS="-e SGLANG_OPT_MAMBA_SKIP_DECODE_LOCK=1 -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"

# S2: S1 with lpm and the cache report; the cut run first, it answers the question the switch depends on
if want S2 && sgl_up S2 $BASE --chunked-prefill-size 4096 --max-prefill-tokens 4096; then
  warmup S2
  load S2 "$WL1" 4 w1-c4-cut $CUT
  load S2 "$WL1" 4 w1-c4
  if load S2 "$WL2" 6 w2-c6-cut $CUT; then
    if unanswered_over_half "$OUT/S2-w2-c6-cut"; then
      log "S2 w2-c6-cut: over half unanswered; 8 chats skipped"
    else
      load S2 "$WL2" 8 w2-c8-cut $CUT
    fi
  fi
  sgl_down S2
fi

# S3: S2 with a prefill chunk of 8192; the prefill CUDA graph (S1: 252 s and 2.27 GB at boot) gives way to it
if ! want S3; then
  :
elif [ "$(date +%s)" -ge "$DEADLINE" ]; then
  log "SKIP S3: past the window's deadline"
elif sgl_up S3 $BASE --chunked-prefill-size 8192 --max-prefill-tokens 8192 --disable-prefill-cuda-graph; then
  warmup S3
  load S3 "$WL1" 4 w1-c4-cut $CUT
  load S3 "$WL2" 8 w2-c8-cut $CUT
  sgl_down S3
fi
ENVS=""

log "WINDOW arms done"
leave 0
