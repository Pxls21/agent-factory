#!/usr/bin/env bash
# collect_leg.sh — SANDBOX side: bring one leg's evidence home into proofs/S0-01/evidence/golden/<leg>/.
#   proofs/S0-01/tools/pc/collect_leg.sh <leg>          (legs: run-1 run-2 cancel shutdown two-users negative)
# Small files travel as one tar.gz through scripts/pc_fetch.sh (size-verified chunks). The manifest
# bodies (1 MB each) are compared BY SHA256 ON THE PC against the committed baseline gz; an identical
# body is materialised from the committed baseline (same bytes), a differing body is fetched.
# Excluded on purpose: buzzacp.raw.log (unmasked), manifest logs, launch log.
set -euo pipefail
LEG=${1:?leg}
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"; cd "$ROOT"
DST=proofs/S0-01/evidence/golden/$LEG; FD=/home/rocco/s0-01-pinned/.markers/v2-$LEG
BASE_GZ=proofs/S0-01/evidence/golden/manifests/manifest-baseline.txt.gz
BASE_SHA=$(sha256sum "$BASE_GZ" | cut -d" " -f1)
S=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/collect; mkdir -p "$S"
bash scripts/pc.sh "cd $FD && tar czf /tmp/s0-01-$LEG.tgz --exclude=buzzacp.raw.log --exclude='manifest-*.txt.gz' --exclude='manifest-*.log' --exclude='*.launch.log' . && ls -la /tmp/s0-01-$LEG.tgz && for p in pre post; do [ -f manifest-\$p.txt.gz.sha256 ] && echo \"MANIFEST \$p \$(cat manifest-\$p.txt.gz.sha256)\"; done" | tee "$S/$LEG.pack.log"
bash scripts/pc_fetch.sh "/tmp/s0-01-$LEG.tgz" "$S/$LEG.tgz"
rm -rf "$DST"; mkdir -p "$DST"; tar xzf "$S/$LEG.tgz" -C "$DST"
for p in pre post; do
  SHA=$(grep "^MANIFEST $p " "$S/$LEG.pack.log" | awk '{print $3}' || true)
  [ -z "$SHA" ] && continue
  if [ "$SHA" = "$BASE_SHA" ]; then cp "$BASE_GZ" "$DST/manifest-$p.txt.gz"; echo "manifest-$p: identical to the committed baseline (sha $SHA) — materialised from it"
  else echo "manifest-$p DIFFERS from baseline ($SHA) — fetching the body"; bash scripts/pc_fetch.sh "$FD/manifest-$p.txt.gz" "$DST/manifest-$p.txt.gz"; fi
  [ "$(sha256sum "$DST/manifest-$p.txt.gz" | cut -d' ' -f1)" = "$SHA" ] || { echo "sha mismatch after materialisation"; exit 7; }
done
find "$DST" -type f | sort | xargs ls -la | awk '{print $5, $9}'
