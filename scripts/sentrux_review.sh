#!/usr/bin/env bash
# sentrux_review.sh — the FIFTH, ADVISORY code-intel instrument (owner decision 2026-09-05; same
# standing as slopo: never a gate). sentrux scores architecture health (cycles, coupling, complexity,
# function length, god files) and compares a lane's before/after.
#
#   scripts/sentrux_review.sh check            # rules report over the project code
#   scripts/sentrux_review.sh save             # save the baseline BEFORE a build lane
#   scripts/sentrux_review.sh compare          # after the lane: quality/coupling/cycles delta vs baseline
#   scripts/sentrux_review.sh check --strict   # pass the tool's own exit code through (CI use only)
#   SENTRUX_RUNTIME_DIR=<dir>                  # where the composed tree/baseline/reports live (default .sentrux-runtime/)
#
# Why a composed copy: sentrux walks a directory (hidden dirs and .gitignore honoured, symlinks NOT
# followed, no custom ignore file), so scanning the repo root would score the vendored trees. The
# script copies ONLY the project code dirs into .sentrux-runtime/tree and scans that.
# Pins: binary + grammar tarball digests live in upstream.lock.yaml (`sentrux`); setup.sh installs
# them. Telemetry: `sentrux analytics off` (setup.sh) and SENTRUX_DEV=1 (no update check).
# Known blind spot (2026-09-05): Python import resolution on this tree is weak (4/390 specs), so the
# dependency-graph metrics (coupling, cycles) are near-empty here; complexity/length are the live signal.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE=${1:-check}; STRICT=0; [ "${2:-}" = "--strict" ] && STRICT=1
# Usage errors are venue-independent: validate the mode BEFORE the binary probe (CI has no binary and
# reported "missing"/exit 0 for a bogus mode — the 2026-09-06 run on 79f8f5b).
case "$MODE" in check|save|compare) ;; *) echo "usage: sentrux_review.sh check|save|compare [--strict]"; exit 64 ;; esac
BIN=${SENTRUX_BIN:-/root/.local/bin/sentrux}
[ -x "$BIN" ] || { echo "sentrux_review: $BIN missing — run scripts/setup.sh (pinned install)"; exit 0; }
RT="${SENTRUX_RUNTIME_DIR:-$ROOT/.sentrux-runtime}"; TREE="$RT/tree"; mkdir -p "$RT"
rm -rf "$TREE"; mkdir -p "$TREE/.sentrux"
for d in proofs scripts tests harness-ports spikes src; do [ -d "$ROOT/$d" ] && cp -a "$ROOT/$d" "$TREE/"; done
cp "$ROOT/.sentrux/rules.toml" "$TREE/.sentrux/rules.toml"
[ -f "$RT/baseline.json" ] && cp "$RT/baseline.json" "$TREE/.sentrux/baseline.json"
export SENTRUX_DEV=1 SENTRUX_SKIP_GRAMMAR_DOWNLOAD=1
case "$MODE" in
  check)   "$BIN" check "$TREE" 2>&1 | grep -v '^\[' | sed "s#$TREE/##g" | tee "$RT/last-check.txt"; rc=${PIPESTATUS[0]} ;;
  save)    "$BIN" gate --save "$TREE" 2>&1 | grep -v '^\[' | tee "$RT/last-save.txt"; rc=${PIPESTATUS[0]}; cp "$TREE/.sentrux/baseline.json" "$RT/baseline.json" && echo "baseline kept at $RT/baseline.json (untracked)" ;;
  compare) [ -f "$RT/baseline.json" ] || { echo "sentrux_review: no baseline — run 'save' before the lane"; exit 0; }
           "$BIN" gate "$TREE" 2>&1 | grep -v '^\[' | tee "$RT/last-compare.txt"; rc=${PIPESTATUS[0]} ;;
esac
echo "sentrux $MODE: tool exit $rc (advisory — never a gate; --strict passes it through)"
[ "$STRICT" = 1 ] && exit "$rc"
exit 0
