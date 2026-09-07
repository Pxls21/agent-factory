#!/usr/bin/env bash
# ripwire_review.sh — the SIXTH, ADVISORY code-intel instrument (owner ask 2026-09-07; same
# standing as slopo/sentrux: never a gate). ripwire maps a codebase by Personalized PageRank,
# exposes a static call graph, and answers structural questions in deterministic XML.
#
#   scripts/ripwire_review.sh map [--top-k=N]     # ranked symbol map (default top-k=200)
#   scripts/ripwire_review.sh for "<question>"     # BM25 routed semantic lookup
#   scripts/ripwire_review.sh callers SYM          # 1-hop callers of SYM
#   scripts/ripwire_review.sh impact SYM           # transitive impact of SYM
#   scripts/ripwire_review.sh exercises TESTFILE   # what TESTFILE exercises
#   scripts/ripwire_review.sh test-gate FILE...    # test coverage gate for FILE(s)
#   scripts/ripwire_review.sh edit-check SYM       # pre-edit blast radius for SYM
#   scripts/ripwire_review.sh skipped              # files the parser could not index
#   RIPWIRE_BIN=/path/to/ripwire                   # override binary (default /root/.local/bin/ripwire)
#   RIPWIRE_LIMIT=N                                # override --limit for flat verbs (default 20)
#
# Excludes: sandbox-kit, .claude, graft, .agents, harness-ports/ports (vendored/generated trees).
# Flat verbs (callers/impact/exercises/test-gate/edit-check/skipped) use --limit, never --top-k
# (the tool rejects --top-k on them with exit 1). map uses --top-k. for ignores --top-k.
# Pins: binary digest in upstream.lock.yaml (`advisory_tooling.ripwire`); setup.sh installs it.
# Telemetry: none found (no outbound URLs, no analytics subcommands, documented offline binary).
# KNOWN BLIND SPOT: subprocess-exercised tools (e.g. Popen([sys.executable, ...])) produce zero
# call edges — ripwire reports tests="0" impacted="0" for them. A ripwire zero is "none found",
# never "none exists". The two-instrument rule for DORMANT claims stands regardless.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE=${1:-}
# Usage errors are venue-independent: validate the mode BEFORE the binary probe (the sentrux
# lesson, 2026-09-06: CI has no binary and reported "missing"/exit 0 for a bogus mode).
case "$MODE" in
  map|for|callers|impact|exercises|test-gate|edit-check|skipped) ;;
  *) echo "usage: ripwire_review.sh map|for|callers|impact|exercises|test-gate|edit-check|skipped [args]"; exit 64 ;;
esac
BIN="${RIPWIRE_BIN:-}"; for c in "$HOME/.local/bin/ripwire" /root/.local/bin/ripwire; do [ -z "$BIN" ] && [ -x "$c" ] && BIN="$c"; done
[ -z "$BIN" ] && BIN="$(command -v ripwire 2>/dev/null || echo /root/.local/bin/ripwire)"  # sandbox: /root; PC: $HOME (pc-setup.sh)
[ -x "$BIN" ] || { echo "ripwire_review: $BIN missing — run scripts/setup.sh (pinned install)"; exit 0; }
EXCLUDES=(--exclude=sandbox-kit --exclude=/.claude --exclude=/graft --exclude=/.agents --exclude=harness-ports/ports)
LIMIT=${RIPWIRE_LIMIT:-20}
shift
case "$MODE" in
  map)
    exec "$BIN" "$ROOT" "${EXCLUDES[@]}" "$@"
    ;;
  for)
    [ $# -ge 1 ] || { echo "usage: ripwire_review.sh for \"<question>\""; exit 64; }
    exec "$BIN" "$ROOT" "${EXCLUDES[@]}" --for="$1"
    ;;
  callers)
    [ $# -ge 1 ] || { echo "usage: ripwire_review.sh callers SYMBOL"; exit 64; }
    exec "$BIN" "$ROOT" "${EXCLUDES[@]}" --callers="$1" --limit="$LIMIT"
    ;;
  impact)
    [ $# -ge 1 ] || { echo "usage: ripwire_review.sh impact SYMBOL"; exit 64; }
    exec "$BIN" "$ROOT" "${EXCLUDES[@]}" --impact="$1" --limit="$LIMIT"
    ;;
  exercises)
    [ $# -ge 1 ] || { echo "usage: ripwire_review.sh exercises TESTFILE"; exit 64; }
    exec "$BIN" "$ROOT" "${EXCLUDES[@]}" --exercises="$1" --limit="$LIMIT"
    ;;
  test-gate)
    [ $# -ge 1 ] || { echo "usage: ripwire_review.sh test-gate FILE..."; exit 64; }
    # test-gate takes multiple files as separate --test-gate args
    ARGS=()
    for f in "$@"; do ARGS+=(--test-gate="$f"); done
    exec "$BIN" "$ROOT" "${EXCLUDES[@]}" "${ARGS[@]}" --limit="$LIMIT"
    ;;
  edit-check)
    [ $# -ge 1 ] || { echo "usage: ripwire_review.sh edit-check SYMBOL"; exit 64; }
    exec "$BIN" "$ROOT" "${EXCLUDES[@]}" --edit-check="$1" --limit="$LIMIT"
    ;;
  skipped)
    exec "$BIN" "$ROOT" "${EXCLUDES[@]}" --skipped --limit="$LIMIT"
    ;;
esac
