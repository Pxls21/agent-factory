#!/usr/bin/env bash
# pc_manifest.sh — recursive sha256 manifest of the three pinned trees (contract v2.1 §14).
# Env: PHASE=pre|post FD=<leg dir> [BASE=/home/rocco/s0-01-pinned]. Detached by the caller.
# Body: `## <tree>` header then `sha256sum` lines (`<hex>  ./path`), trees in the pinned order.
# Summary: `<tree> <sha256-of-section-text>` x3 + one UTC timestamp line. Then gzip -9 -n.
set -u
BASE=${BASE:-/home/rocco/s0-01-pinned}
: "${FD:?}" "${PHASE:?}"
OUT=$FD/manifest-$PHASE.txt
{ for t in hermes-agent buzz acp; do echo "## $t"; (cd "$BASE/$t" && find . -path ./.git -prune -o -type f -print0 | LC_ALL=C sort -z | xargs -0 sha256sum); done; } > "$OUT"
python3 - "$OUT" "$FD/manifest-$PHASE.summary" <<'PY'
import sys, hashlib, datetime
body = open(sys.argv[1], "rb").read()
assert body.startswith(b"## hermes-agent\n"), "manifest body must open with the hermes-agent header"
out = []
for part in body.split(b"## ")[1:]:
    name, _, text = part.partition(b"\n")
    out.append(f"{name.decode()} {hashlib.sha256(text).hexdigest()}")
out.append(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
open(sys.argv[2], "w").write("\n".join(out) + "\n")
PY
gzip -9 -n -f "$OUT"
sha256sum "$OUT.gz" | cut -d" " -f1 > "$OUT.gz.sha256"
touch "$FD/manifest-$PHASE.done"
