#!/usr/bin/env bash
# realleg_sync.sh — the S0-01 real-leg corpus as a DECLARED input on both venues (VERIFY-CK10 F-R10-25:
# the checker's 51 real-producer tests used to skip green on every container but one).
#
#   scripts/realleg_sync.sh pc-build   materialise /home/rocco/s0-01-pinned/realleg/golden/<leg> on the PC from the
#                                      captured framedirs .markers/v2-<leg> with collect_leg.sh's exclusions plus the
#                                      manifest sidecars (which the graded sandbox corpus never carried); prints the
#                                      tree's sha256 manifest
#   scripts/realleg_sync.sh pull       bring that tree home to ${S0_01_REAL_LEG_DIR:-/root/s0-01-realleg/golden}: one
#                                      tar.gz WITHOUT the 1.5 MB manifest bodies (each is byte-identical to the
#                                      committed baseline gz — checked by sha256, materialised from it), then EVERY
#                                      file's sha256 checked against the PC manifest fetched in the same run
#   scripts/realleg_sync.sh check      the local corpus against the manifest saved by the last pull (5 legs, every sha)
#
# The sandbox copy is session-scoped by nature (a fresh container has none): `pull` is the restore. With
# S0_01_REAL_LEG_DIR set to an absent or incomplete corpus the checker's real-leg tests FAIL — never skip.
# scripts/pc_suite.sh exports S0_01_VENUE=pc + S0_01_REAL_LEG_DIR=<the PC tree>; scripts/test_summary.sh the sandbox pair.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
G=/home/rocco/s0-01-pinned/realleg/golden; M=/home/rocco/s0-01-pinned/.markers
LEGS="cancel negative run-1 shutdown two-users"
DST="${S0_01_REAL_LEG_DIR:-/root/s0-01-realleg/golden}"
BASE_GZ=proofs/S0-01/evidence/golden/manifests/manifest-baseline.txt.gz
pc() { bash scripts/pc.sh "$1" 2> >(grep -v "bind: warning" >&2); }
manifest() { (cd "$1" && LC_ALL=C find . -type f | LC_ALL=C sort | xargs sha256sum); }

case "${1:-}" in
pc-build)
  pc "set -e; for leg in $LEGS; do rm -rf $G/\$leg; mkdir -p $G/\$leg; (cd $M/v2-\$leg && tar cf - --exclude=buzzacp.raw.log --exclude='manifest-*.log' --exclude='*.launch.log' --exclude='manifest-*.txt.gz.sha256' .) | tar xf - -C $G/\$leg; done; cd $G && LC_ALL=C find . -type f | LC_ALL=C sort | xargs sha256sum" ;;
pull)
  S=$(mktemp -d)
  pc "cd $G && tar czf /tmp/s0-01-realleg.tgz --exclude='manifest-*.txt.gz' . && LC_ALL=C find . -type f | LC_ALL=C sort | xargs sha256sum > /tmp/s0-01-realleg.sha256 && wc -c /tmp/s0-01-realleg.tgz /tmp/s0-01-realleg.sha256"
  bash scripts/pc_fetch.sh /tmp/s0-01-realleg.tgz "$S/corpus.tgz"
  bash scripts/pc_fetch.sh /tmp/s0-01-realleg.sha256 "$S/pc.sha256"
  rm -rf "$DST"; mkdir -p "$DST"; tar xzf "$S/corpus.tgz" -C "$DST"
  BASE_SHA=$(sha256sum "$BASE_GZ" | cut -d' ' -f1)
  while read -r sha path; do
    case "$path" in
      */manifest-*.txt.gz)
        [ "$sha" = "$BASE_SHA" ] || { echo "realleg_sync: $path on the PC ($sha) is not the committed baseline — fetch that body by hand (scripts/pc_fetch.sh)" >&2; exit 7; }
        cp "$BASE_GZ" "$DST/$path" ;;
    esac
  done < "$S/pc.sha256"
  cp "$S/pc.sha256" "$DST/../golden.pc.sha256"
  if manifest "$DST" | diff - "$S/pc.sha256"; then
    echo "realleg_sync: $DST == the PC tree ($(wc -l < "$S/pc.sha256") files, every sha256 equal)"
  else
    echo "realleg_sync: the pulled corpus differs from the PC manifest (diff above)" >&2; exit 8
  fi
  rm -rf "$S" ;;
check)
  [ -f "$DST/../golden.pc.sha256" ] || { echo "realleg_sync: no PC manifest beside $DST — run pull" >&2; exit 5; }
  for leg in $LEGS; do [ -d "$DST/$leg" ] || { echo "realleg_sync: leg $leg absent under $DST" >&2; exit 6; }; done
  manifest "$DST" | diff - "$DST/../golden.pc.sha256" && echo "realleg_sync: $DST intact ($(wc -l < "$DST/../golden.pc.sha256") files)" ;;
*) echo "usage: realleg_sync.sh pc-build | pull | check" >&2; exit 64 ;;
esac
