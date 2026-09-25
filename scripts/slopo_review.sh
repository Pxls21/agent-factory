#!/usr/bin/env bash
# slopo_review.sh: slopo (semantic duplicates; ADVISORY, never a gate) over this repository in one command.
#   scripts/slopo_review.sh <base-ref>   sync, then `slopo review --base <base-ref>`: the units the working tree changed
#                                        since <base-ref> that look like other code here. The verdict is the last line;
#                                        clusters go to slopo-report/ (the directory `slopo analyze` uses; a review that
#                                        finds nothing leaves it as it was)
#   scripts/slopo_review.sh --sync       sync only: `slopo index`, then `slopo embed` (the post-commit hook runs this)
# `slopo index` runs through scripts/slopo_run.py: slopo's own CLI with a walk that skips the directories
# slopo.conf.yaml excludes whole (slopo's own walk reads every file under source_dir first: 23 minutes on the PC).
# `index` is the only command that walks the tree; `embed` reads the database and `review` stats only the changed
# files, so both stay on bin/slopo (the SLOPO2 report).
# slopo refuses a review until the index is fresh and every unit is embedded, and an embed needs the local embedding
# server (scripts/slopo_embed_server.py). So the sync starts one, on the port slopo.conf.yaml's api_base names, when a
# unit waits for its embedding and no server answers /health; it stops the one it started on every exit. One slopo run
# at a time (flock on $SLOPO_LOCK): --sync skips while another run holds the lock, a review waits for it. No network:
# LITELLM_LOCAL_MODEL_COST_MAP=True stops LiteLLM fetching its price list. slopo and the server run from the slopo venv
# ($SLOPO_VENV, default ~/venv-slopo) and the model under .slopo-runtime/model/, both from scripts/setup.sh;
# slopo.conf.yaml sets the scope. Exit: 2 usage, 3 not installed, 4 the server did not start, 5 the lock wait timed
# out; otherwise slopo's own code.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${SLOPO_VENV:-$HOME/venv-slopo}"
LOCK="${SLOPO_LOCK:-/tmp/slopo-sync.lock}"
SERVER_LOG="${SLOPO_SERVER_LOG:-/tmp/slopo-embed-server.log}"
MODEL_ID="jina-embeddings-v2-base-code-onnx-q8"      # what scripts/slopo_embed_server.py's /health names
# The one server setting that moves a vector (threads and workers do not: INSTALL1 report, section 3). A running
# server is reused only when its /health reports this cap, so one DB never mixes vectors from two caps (AF-AP-33).
MAX_TOKENS=1024
export LITELLM_LOCAL_MODEL_COST_MAP=True

usage() { echo "usage: scripts/slopo_review.sh <base-ref> | --sync" >&2; exit 2; }
[ $# -eq 1 ] || usage
case "$1" in
  --sync) mode=sync ;;
  -*|"") usage ;;
  *) mode=review; base="$1" ;;
esac
for f in "$VENV/bin/slopo" "$VENV/bin/python"; do
  [ -x "$f" ] || { echo "slopo_review: $f is missing; run scripts/setup.sh" >&2; exit 3; }
done
for f in slopo.conf.yaml .slopo-runtime/model/model_quantized.onnx .slopo-runtime/model/tokenizer.json; do
  [ -f "$ROOT/$f" ] || { echo "slopo_review: $ROOT/$f is missing; run scripts/setup.sh" >&2; exit 3; }
done
cd "$ROOT" || exit 3
PORT="$(sed -n 's#^ *api_base: *http://127\.0\.0\.1:\([0-9][0-9]*\)/v1 *$#\1#p' slopo.conf.yaml)"
[ -n "$PORT" ] || { echo "slopo_review: slopo.conf.yaml names no http://127.0.0.1:<port>/v1 api_base" >&2; exit 3; }

exec 9>"$LOCK"
if [ "$mode" = sync ]; then
  flock -n 9 || { echo "slopo_review: another slopo run holds $LOCK; this sync skipped"; exit 0; }
else
  flock -w 1800 9 || { echo "slopo_review: no turn at $LOCK within 1800 s" >&2; exit 5; }
fi

# The server this run started is stopped on every exit, a second signal included (AF-AP-145's shape: the cleanup and
# each handler open by ignoring INT and TERM, and every exit after this point goes through leave).
SERVER=""
kill_server() { if [ -n "$SERVER" ]; then kill "$SERVER" 2>/dev/null; wait "$SERVER" 2>/dev/null; SERVER=""; fi; }
cleanup() { trap '' INT TERM; kill_server; }
leave() { trap '' INT TERM; exit "$1"; }
trap cleanup EXIT
trap 'trap "" INT TERM; exit 130' INT
trap 'trap "" INT TERM; exit 143' TERM
health() { curl -fsS -m 2 "http://127.0.0.1:$PORT/health" 2>/dev/null; }
up() { grep -Eq "\"model\": ?\"$MODEL_ID\".*\"max_tokens\": ?$MAX_TOKENS[,}]" <<<"$(health)"; }   # no pipe: pipefail

"$VENV/bin/python" scripts/slopo_run.py index || leave $?
# slopo's own count (the one `slopo embed` starts from); an unreadable count starts the server anyway.
waiting="$("$VENV/bin/python" -c 'from pathlib import Path
from slopo.config import load_config
from slopo.db import open_db
from slopo.embedding.db import count_unembedded_units
print(count_unembedded_units(open_db(load_config(Path("slopo.conf.yaml")))))' 2>/dev/null)"
if [ "$waiting" != 0 ]; then
  if ! up; then
    if health >/dev/null; then
      echo "slopo_review: :$PORT answers /health, but not as a $MODEL_ID server with max_tokens $MAX_TOKENS" >&2
      leave 4
    fi
    "$VENV/bin/python" scripts/slopo_embed_server.py --port "$PORT" --max-tokens "$MAX_TOKENS" \
      >>"$SERVER_LOG" 2>&1 </dev/null 9>&- &
    SERVER=$!
    for _ in $(seq 600); do up && break; kill -0 "$SERVER" 2>/dev/null || break; sleep 0.1; done
    up || { echo "slopo_review: the embed server did not answer /health on :$PORT (log: $SERVER_LOG)" >&2; leave 4; }
  fi
  "$VENV/bin/slopo" embed || leave $?
  kill_server
fi
[ "$mode" = sync ] && leave 0
"$VENV/bin/slopo" review --base "$base"
leave $?
