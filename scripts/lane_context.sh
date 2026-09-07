#!/usr/bin/env bash
# lane_context.sh — the code-intel tool pass for ONE brief, in ONE command (owner mandate 2026-09-07: the graph
# instruments run on EVERY build and verify loop, not when someone remembers — they gather context faster and
# cheaper than reading files whole). Produces the context pack a brief attaches and a verifier starts from:
#   - graft skeleton of every changed file (symbols + line ranges, ~5% of the tokens of the file)
#   - graft ask for the question the brief poses (structural answer: callers / seams / resolution)
#   - per symbol: GitNexus impact (blast radius + risk), code-review-graph callers_of + tests_for,
#     ripwire callers (a second, independent instrument — two instruments for any reachability claim)
#   - ripwire test-gate over the files (the tests to run + the UNTESTED blast radius)
#   - the anti-pattern registry screen over the WHOLE files (production → AP_SCREEN, tests → TEST_SCREEN)
#
#   scripts/lane_context.sh [-q "<question>"] [-s SYMBOL]... [-o out.md] FILE...
#
# Symbols: every -s, plus the `def` names in the working-tree diff of each FILE against HEAD (a lane's live edit)
# — so a verifier's pass sees exactly the symbols the lane touched. Every instrument is optional and tolerant: an
# absent or failing one prints "unmapped — <tool> unavailable" (never a silent blank, never a claim it did not make).
# Advisory, never a gate (owner decision 2026-09-05 for sentrux/slopo/ripwire; the same standing here).
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
Q=""; OUT=""; SYMS=()
while [ $# -gt 0 ]; do
  case "$1" in
    -q) Q="$2"; shift 2;;
    -s) SYMS+=("$2"); shift 2;;
    -o) OUT="$2"; shift 2;;
    -h|--help) sed -n '2,16p' "$0"; exit 0;;
    *) break;;
  esac
done
[ $# -gt 0 ] || { echo "usage: lane_context.sh [-q question] [-s SYMBOL]... [-o out.md] FILE..." >&2; exit 64; }
FILES=("$@")
T=90
# venue-neutral instrument paths: the sandbox keeps venvs/binaries under /root, the PC under $HOME (harness-ports/bin/pc-setup.sh)
CRG="${CRG_BIN:-}"; for c in "$HOME/venv-crg/bin/code-review-graph" /root/venv-crg/bin/code-review-graph; do [ -z "$CRG" ] && [ -x "$c" ] && CRG="$c"; done
[ -z "$CRG" ] && CRG="$(command -v code-review-graph 2>/dev/null || true)"
have() { command -v "$1" >/dev/null 2>&1; }
run() { # run <label> <cmd...> — bounded, tolerant, never silent
  local label="$1"; shift
  if out=$(timeout "$T" "$@" 2>&1); then printf '%s\n' "$out"; else printf 'unmapped — %s unavailable or failed (rc %s): %s\n' "$label" "$?" "$(printf '%s' "$out" | tail -1 | cut -c1-160)"; fi
}
emit() {
  echo "# lane context pack — $(git rev-parse --short HEAD) $(date -u +%Y-%m-%dT%H:%MZ)"
  echo "files: ${FILES[*]}"
  # symbols the lane touched: -s plus the def names in each file's working-tree diff against HEAD
  for f in "${FILES[@]}"; do
    while read -r s; do [ -n "$s" ] && SYMS+=("$s"); done < <(git diff -U0 HEAD -- "$f" 2>/dev/null | grep -oE '^\+[[:space:]]*(async[[:space:]]+)?def[[:space:]]+[A-Za-z_][A-Za-z0-9_]*' | sed -E 's/.*def[[:space:]]+//')
  done
  mapfile -t SYMS < <(printf '%s\n' "${SYMS[@]:-}" | awk 'NF && !seen[$0]++')
  echo "symbols: ${SYMS[*]:-(none — pass -s, or edit first)}"
  echo
  for f in "${FILES[@]}"; do
    echo "## $f"
    echo "### graft skeleton"
    if have graft; then run "graft skeleton" graft skeleton "$f" | grep -v '^\[graft\] tokens saved' | head -80; else echo "unmapped — graft unavailable"; fi
    echo "### anti-pattern screen (whole file)"
    case "$f" in tests/*) python3 scripts/ap_screen.py --tests "$f" --limit 6;; *) python3 scripts/ap_screen.py "$f" --limit 6;; esac
    echo
  done
  if [ -n "$Q" ]; then
    echo "## graft ask — $Q"
    if have graft; then run "graft ask" graft ask "$Q" --in "$(dirname "${FILES[0]}")" | grep -v '^\[graft\] tokens saved' | head -60; else echo "unmapped — graft unavailable"; fi
    echo
  fi
  for s in "${SYMS[@]:-}"; do
    [ -n "$s" ] || continue
    echo "## symbol $s"
    echo "### GitNexus impact (upstream)"
    if [ -f .gitnexus/run.cjs ]; then run "gitnexus impact" node .gitnexus/run.cjs impact "$s" --direction upstream --repo . | grep -E '"impactedCount"|"risk"|"epistemic"|"direct"|"processes_affected"|riskNote' | head -8; else echo "unmapped — GitNexus index absent"; fi
    echo "### code-review-graph callers_of / tests_for"
    if [ -n "$CRG" ] && [ -x "$CRG" ] && [ -f .code-review-graph/graph.db ]; then
      # a bare name that several files define answers "matches N node(s), re-run with a qualified_name" — qualify it
      # with the first FILE that defines it (crg's node id is <abs path>::<name>); the bare name stays the fallback
      q=""; for f in "${FILES[@]}"; do grep -qE "^[[:space:]]*(async[[:space:]]+)?(def|class)[[:space:]]+$s\b" "$f" 2>/dev/null && { q="$ROOT/$f::$s"; break; }; done
      run "crg callers_of" "$CRG" query callers_of "${q:-$s}" | grep -E '"summary"|"name"' | head -12
      run "crg tests_for" "$CRG" query tests_for "${q:-$s}" | grep -E '"summary"|"name"' | head -12
    else echo "unmapped — code-review-graph graph absent (run: ${CRG:-code-review-graph} build)"; fi
    echo "### ripwire callers"
    if [ -x scripts/ripwire_review.sh ]; then run "ripwire callers" bash scripts/ripwire_review.sh callers "$s" | grep -oE '<callers[^>]*>|<c [^>]*/>' | head -12; else echo "unmapped — ripwire wrapper absent"; fi
    echo
  done
  echo "## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')"
  if [ -x scripts/ripwire_review.sh ]; then run "ripwire test-gate" bash scripts/ripwire_review.sh test-gate "${FILES[@]}" | grep -oE '<test-gate [^>]*>|<t [^>]*/>|<u [^>]*/>' | sed -E 's/ graph_[a-z]+="[^"]*"//g' | head -40; else echo "unmapped — ripwire wrapper absent"; fi
}
if [ -n "$OUT" ]; then emit > "$OUT" 2>&1; echo "lane_context: pack written to $OUT ($(wc -l < "$OUT") lines)"; else emit; fi
