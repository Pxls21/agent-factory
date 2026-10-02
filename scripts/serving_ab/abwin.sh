#!/bin/bash
# abwin.sh - the GPU window of task #454 (D-127, D-128 item 3; window rules D-088).
# Usage: abwin.sh <workload.json> (make_workload.py's file, sized with vLLM's own tokenizer; every arm replays it).
# Arms, each at 2, 3 and 4 long chats (first prompts 57k to 87k tokens, 4 turns):
#   V0  today's vLLM unit as it runs (the baseline the owner lives with)
#   S0  the SGLang recipe as published (one running request)
#   S1  SGLang with the recipe author's 4-stream flags plus HiCache (host-memory KV tier)
#   S1b S1 without HiCache, only if S1 does not boot
# vLLM is restored on every exit (the EXIT trap); the test port binds 127.0.0.1 only.
# The first window (2026-10-02 00:28:52Z) ran a scratch copy of this file. Task #462 moved it here with three changes:
# chat_load.py is found beside this file; the traps are armed where the window starts; and every exit after them goes
# through leave(), with the signal handler ignoring INT and TERM first (AF-AP-145, as scripts/gpu_window.sh does).
set -u
WL=${1:?usage: abwin.sh <workload.json>}
[ -s "$WL" ] || { echo "abwin: no workload file: $WL" >&2; exit 2; }
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

restore() {
  trap '' INT TERM
  podman rm -f "$NAME" >/dev/null 2>&1
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

load() { # arm base_url keyfile-or-empty chats
  local arm=$1 url=$2 kf=$3 c=$4
  log "LOAD $arm chats=$c start"
  python3 "$CL" --arm "$arm" --base-url "$url" --model qwen3.8-27b-local ${kf:+--api-key-file "$kf"} \
    --workload "$WL" --chats "$c" --stagger-s 20 --timeout 600 --nvsmi \
    --out "$OUT/$arm-c$c" > "$OUT/$arm-c$c.stdout" 2>&1
  log "LOAD $arm chats=$c rc=$? $(tail -1 "$OUT/$arm-c$c.stdout" | cut -c1-600)"
}

over_half() { # true when more than half the requests of a run missed the first-token limit
  python3 - "$1/summary.json" <<'PY'
import json, sys
try:
    s = json.load(open(sys.argv[1]))
except (OSError, ValueError):
    sys.exit(0)
sys.exit(0 if s["requests"] and s["missed_80s"] * 2 > s["requests"] else 1)
PY
}

sgl_up() { # name of the arm; the rest are extra launch flags; env pairs go first as -e args via ENVS
  local arm=$1; shift
  podman rm -f "$NAME" >/dev/null 2>&1
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
  grep -ciE 'out of memory|CUDA error|Traceback' "$OUT/$1-server.log" | sed "s/^/error-lines /" >> "$LOG"
  podman rm -f "$NAME" >/dev/null 2>&1
}

trap restore EXIT
trap 'trap "" INT TERM; log "signal; restoring"; exit 1' INT TERM  # the ignore first (AF-AP-145)
log "WINDOW start; workload $WL $(sha256sum "$WL" | cut -c1-16); out $OUT; gpu: $(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader | tr '\n' ' ')"

# V0: today's vLLM, untouched
for c in 2 3 4; do load V0 http://127.0.0.1:8080/v1 "$KEYF" $c; done

# the window proper: vLLM stops here and comes back in restore()
systemctl --user stop qwen
for i in $(seq 1 30); do
  nvidia-smi --query-compute-apps=pid --format=csv,noheader | grep -q . || break
  [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)" -lt 1500 ] && break
  sleep 5
done
log "vLLM stopped; gpu: $(nvidia-smi --query-gpu=memory.used --format=csv,noheader)"

# S0: the recipe as published
if sgl_up S0 --context-length 204800 --mem-fraction-static 0.80 --max-running-requests 1 \
     --max-mamba-cache-size 5 --cuda-graph-max-bs-decode 1 --chunked-prefill-size 1024 --max-prefill-tokens 1024; then
  for c in 2 3 4; do
    load S0 http://127.0.0.1:$TPORT/v1 "" $c
    if over_half "$OUT/S0-c$c"; then log "S0 chats=$c: over half missed the limit; higher counts skipped"; break; fi
  done
  sgl_down S0
fi

# S1: the author's 4-stream flags (registry C4 candidate) plus HiCache
C4="--context-length 131072 --mem-fraction-static 0.80 --max-running-requests 4 --max-mamba-cache-size 12
    --cuda-graph-max-bs-decode 4 --chunked-prefill-size 4096 --max-prefill-tokens 4096 --prefill-decode-interval 16
    --mamba-radix-cache-strategy no_buffer --disable-overlap-schedule"
ENVS="-e SGLANG_OPT_MAMBA_SKIP_DECODE_LOCK=1 -e PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True"
if sgl_up S1 $C4 --enable-hierarchical-cache --hicache-size 24 --hicache-write-policy write_through; then
  for c in 2 3 4; do load S1 http://127.0.0.1:$TPORT/v1 "" $c; done
  sgl_down S1
elif sgl_up S1b $C4; then
  for c in 2 3 4; do load S1b http://127.0.0.1:$TPORT/v1 "" $c; done
  sgl_down S1b
fi
ENVS=""

log "WINDOW arms done"
leave 0
