#!/usr/bin/env bash
# pc_mention.sh — send one relay mention as owner|user2 and capture receipt + the signed event.
# Env params: WHO=owner|user2  TEXT  WAIT_FOR=end_turn|cancelled|chunk|none  REPLY_TO=<event id>  TAG
# The sender's BUZZ_PRIVATE_KEY is sourced from the secret file inside a subshell and exported —
# it never appears in any argv. The event is fetched back BY ID so the committed copy is the relay's.
set -u
BASE=/home/rocco/s0-01-pinned; L=$BASE/.markers; SEC=$BASE/.secrets; BZ=$BASE/buzz/target/release/buzz
FD=$(cat $L/current-framedir); CHAN=$(cat $L/channel_id); AGENT=$(cat $SEC/agent.pub)
WHO=${WHO:-owner}; TEXT=${TEXT:-"Reply with exactly the single word: pong"}; WAIT_FOR=${WAIT_FOR:-end_turn}; WAIT_COUNT=${WAIT_COUNT:-1}; REPLY_TO=${REPLY_TO:-}; TAG=${TAG:-$WHO}
[ -f "$FD/launch.ready" ] || { echo "leg not ready ($FD/launch.ready absent)"; exit 3; }
RT=(); [ -n "$REPLY_TO" ] && RT=(--reply-to "$REPLY_TO")
T0=$(date +%s)
( set -a; . "$SEC/$WHO.env"; BUZZ_RELAY_URL=ws://127.0.0.1:3999; set +a
  exec "$BZ" messages send --channel "$CHAN" --mention "$AGENT" "${RT[@]}" --content "$TEXT" ) \
  > "$FD/mentions/$TAG.receipt.json" 2> "$FD/mentions/$TAG.receipt.err"
EID=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["event_id"])' "$FD/mentions/$TAG.receipt.json")
echo "send($WHO,$TAG) accepted=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("accepted"))' "$FD/mentions/$TAG.receipt.json") id=${EID:0:12} err_bytes=$(wc -c < "$FD/mentions/$TAG.receipt.err")"
case "$WAIT_FOR" in
  none) ;;
  chunk) for i in $(seq 1 20); do grep -q '"sessionUpdate":"agent_message_chunk"' "$FD/timeline.jsonl" 2>/dev/null && break; sleep 2.5; done ;;
  *) for i in $(seq 1 20); do N=$(grep -c "\"stopReason\":\"$WAIT_FOR\"" "$FD/timeline.jsonl" 2>/dev/null); [ "${N:-0}" -ge "$WAIT_COUNT" ] && break; sleep 5; done ;;
esac
( set -a; . "$SEC/owner.env"; BUZZ_RELAY_URL=ws://127.0.0.1:3999; set +a
  exec "$BZ" messages get --channel "$CHAN" --since $((T0-5)) --kinds 9 --limit 50 ) 2>/dev/null \
  | python3 -c 'import json,sys; evs=json.load(sys.stdin); eid=sys.argv[1]; m=[e for e in evs if e.get("id")==eid]; assert len(m)==1, ("event not found", len(evs)); open(sys.argv[2],"w").write(json.dumps(m[0], indent=1, sort_keys=True)+"\n"); print("event fetched: kind", m[0]["kind"], "from", m[0]["pubkey"][:8], "created_at", m[0]["created_at"])' "$EID" "$FD/mentions/$TAG.event.json"
python3 - "$FD" <<'PY'
import json, sys, collections
tl = [json.loads(l) for l in open(sys.argv[1] + "/timeline.jsonl")]
kinds = collections.Counter((e["frame"].get("params") or {}).get("update", {}).get("sessionUpdate") for e in tl if e["dir"] == "a2c" and e["frame"] and "method" in e["frame"])
print("timeline:", len(tl), "frames; seq ok:", [e["seq"] for e in tl] == list(range(1, len(tl) + 1)),
      "| c2a:", [(e["frame"].get("id"), e["frame"].get("method")) for e in tl if e["dir"] == "c2a"],
      "| kinds:", dict(kinds),
      "| terminals:", [(e["frame"]["id"], e["frame"]["result"]["stopReason"]) for e in tl if e["dir"] == "a2c" and e["frame"] and "id" in e["frame"] and isinstance(e["frame"].get("result"), dict) and "stopReason" in e["frame"]["result"]])
PY
echo "EID=$EID"
