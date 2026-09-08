#!/usr/bin/env bash
# lane_gate.sh — the STATIC-COPY gate of a lane's files in ONE command (the pattern every S0-01 checkpoint repeated by hand):
#   a `git archive <rev>` copy under the session scratchpad + EXACTLY the lane's working-tree files on top, the identity table
#   (sha256 + lines) of those files, then `scripts/test_summary.sh <tests>` N times (default 2) — the counts must agree run to run
#   (the wall time is stripped before the comparison). Prints a final RESULT line the checkpoint commit can paste verbatim.
#
#   scripts/lane_gate.sh -r <rev> -f "<lane file> [<lane file>…]" -t "<pytest path> [<path>…]" [-n RUNS] [-o OUTDIR]
#
# Runs long (the checker set is ~17 min per run): launch it DETACHED (`nohup … > gate.log 2>&1 &`) and read gate.log / RESULT;
# each run's full pytest output is kept at <OUTDIR>.run<N>.log (a red run prints its failure headers + E-lines inline);
# never wait on it inside a Bash call. The corpus env comes from test_summary.sh's declared defaults (S0_01_VENUE=sandbox,
# S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden) unless exported. The archive is never the shared tree: mutants and lanes
# cannot touch it mid-run. Exit 0 only when every run's pytest rc is 0 AND the counts agree.
# bash reads a script LAZILY, so an edit to this file while a gate is running corrupts that run at a byte offset
# (2026-09-08: B5i's run 2 finished `114 passed` and the RESULT line never printed — "syntax error near ')'"). Run from a
# private copy of these bytes so the file on disk can change underneath a live gate; ROOT is resolved from the ORIGINAL path.
if [ -z "${LANE_GATE_SELF_COPY:-}" ]; then
  _self="$(mktemp "${TMPDIR:-/tmp}/lane_gate.XXXXXX")" && cp "$0" "$_self" \
    && LANE_GATE_SELF_COPY="$_self" LANE_GATE_ORIG="$0" exec bash "$_self" "$@"
fi
trap 'rm -f "$LANE_GATE_SELF_COPY"' EXIT
set -u
ROOT="$(cd "$(dirname "$LANE_GATE_ORIG")/.." && pwd)"; cd "$ROOT"
REV=HEAD; FILES=""; TESTS=""; RUNS=2; OUT=""
while getopts "r:f:t:n:o:h" o; do case "$o" in
  r) REV="$OPTARG";; f) FILES="$OPTARG";; t) TESTS="$OPTARG";; n) RUNS="$OPTARG";; o) OUT="$OPTARG";;
  h|*) sed -n '2,13p' "$LANE_GATE_ORIG"; exit 64;; esac; done
[ -n "$FILES" ] && [ -n "$TESTS" ] || { echo "usage: lane_gate.sh -r <rev> -f \"<files>\" -t \"<tests>\" [-n RUNS] [-o OUTDIR]" >&2; exit 64; }
SHA="$(git rev-parse --verify "$REV^{commit}" 2>/dev/null)" || { echo "lane_gate: rev $REV does not resolve" >&2; exit 65; }
SP="${LANE_GATE_DIR:-/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad}"
[ -n "$OUT" ] || OUT="$SP/gate-${SHA:0:7}-$(date -u +%H%M%S)"
mkdir -p "$OUT" && git archive "$SHA" | tar -x -C "$OUT" || { echo "lane_gate: archive of $SHA failed" >&2; exit 66; }
echo "lane_gate: archive of ${SHA:0:12} at $OUT; $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "== identity (working-tree bytes copied over the archive) =="
for f in $FILES; do
  [ -f "$f" ] || { echo "lane_gate: lane file $f absent in the working tree" >&2; exit 67; }
  mkdir -p "$OUT/$(dirname "$f")" && cp "$f" "$OUT/$f"
  printf '%s  %s  %s lines\n' "$(sha256sum "$f" | cut -d' ' -f1)" "$f" "$(wc -l < "$f")"
done
cd "$OUT" || exit 66
rc_all=0; prev=""; same=yes; summaries=()
for i in $(seq 1 "$RUNS"); do
  echo "== run $i/$RUNS: bash scripts/test_summary.sh $TESTS  (load $(cut -d' ' -f1-3 /proc/loadavg)) =="
  out="$(bash scripts/test_summary.sh $TESTS 2>&1)"; rc=$?
  # the FULL pytest output of every run is kept beside the archive (test_summary.sh prints only the counts; a red run
  # with no failing-test name forced a blind re-run on 2026-09-08 — a gate that cannot say WHAT failed is half a gate)
  printf '%s\n' "$out" > "$OUT.run$i.log"
  summary="$(printf '%s\n' "$out" | grep '^pytest-summary:' | tail -1 | sed 's/^pytest-summary: //')"
  echo "$summary   (pytest-exit: $rc)"
  [ "$rc" -eq 0 ] || { echo "   full output: $OUT.run$i.log"; printf '%s\n' "$out" | grep -E '^_{3,} .* _{3,}$|^E  ' | head -12; }
  counts="$(printf '%s' "$summary" | sed -E 's/ in [0-9.]+s( \([0-9:]+\))?//')"
  [ "$rc" -eq 0 ] || rc_all=1
  [ -n "$prev" ] && [ "$counts" != "$prev" ] && same=no
  prev="$counts"; summaries+=("$summary")
done
echo "RESULT: rev=${SHA:0:12} files=$(echo $FILES | wc -w) runs=$RUNS identical=$same rc=$rc_all summary=\"${summaries[*]}\""
# the archive is a whole-tree copy (hundreds of MB with the vendored trees); eight of them filled the temp filesystem on
# 2026-09-08. The run logs beside it are the record; the archive itself is deleted unless LANE_GATE_KEEP=1 (a red run keeps
# it too, so the failing bytes can be inspected).
if [ "$rc_all" -eq 0 ] && [ "$same" = yes ] && [ -z "${LANE_GATE_KEEP:-}" ]; then cd / && rm -rf "$OUT"; echo "lane_gate: archive removed (LANE_GATE_KEEP=1 keeps it)"; fi
[ "$rc_all" -eq 0 ] && [ "$same" = yes ]
