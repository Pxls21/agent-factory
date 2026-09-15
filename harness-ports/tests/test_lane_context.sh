#!/usr/bin/env bash
# test_lane_context.sh — the pack tool refuses a nonexistent FILE (rc 64, message on stderr, NO output file) and still
# produces a pack for a real file. Born 2026-09-15: a brief path typed from memory produced a hollow pack with no marker.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; ROOT="$(cd "$HERE/../.." && pwd)"; cd "$ROOT" || exit 1
pass=0; fail=0; ok() { pass=$((pass+1)); echo "ok   $1"; }; bad() { fail=$((fail+1)); echo "FAIL $1"; }
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
# negative: a nonexistent path → rc 64, the message names the path, no output file is written
err="$(bash scripts/lane_context.sh -q x -o "$TMP/hollow.md" proofs/S0-01/tools/does-not-exist.py 2>&1 >/dev/null)"; rc=$?
[ $rc -eq 64 ] && ok "missing FILE → rc 64" || bad "missing FILE → rc $rc (wanted 64)"
printf '%s' "$err" | grep -qF 'FILE absent: proofs/S0-01/tools/does-not-exist.py' && ok "message names the absent path" || bad "message: $err"
[ ! -e "$TMP/hollow.md" ] && ok "no output file written for a hollow pack" || bad "hollow pack file was written"
# positive: a real file → rc 0 and a pack with the header + a skeleton section (instruments may be unmapped, never absent)
out="$(bash scripts/lane_context.sh -q x -o "$TMP/pack.md" scripts/lane_context.sh 2>&1)"; rc=$?
[ $rc -eq 0 ] && ok "real FILE → rc 0" || bad "real FILE → rc $rc: $(printf '%s' "$out" | tail -2)"
grep -q '^# lane context pack' "$TMP/pack.md" 2>/dev/null && grep -q '^### graft skeleton' "$TMP/pack.md" && ok "pack written with header + skeleton section" || bad "pack shape: $(head -3 "$TMP/pack.md" 2>/dev/null)"
echo; echo "$pass passed, $fail failed"; [ $fail -eq 0 ]
