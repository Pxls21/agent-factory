#!/usr/bin/env bash
# test_context_mirrors.sh — the mechanical mirror gate for the three instruction files.
#
# CLAUDE.md is the source of truth; AGENTS.md (Codex) and .hermes.md (Hermes) are its ports.
# docs/HARNESS-PORTS.md §10 said "there is no mechanical check for it" — this is that check
# (owner 2026-09-15: "I dont think we have our claude.md properly copied in to the agents.md").
#
# What it holds, from primary sources measured 2026-09-15:
#   1. SECTION PARITY — every `## ` section of CLAUDE.md (except the four GitNexus-managed ones)
#      maps through TABLE to a heading that must exist in BOTH mirrors; a CLAUDE.md section with
#      no TABLE row FAILS ("unmapped"), so a new section cannot be added to CLAUDE.md alone.
#   2. MIRROR-ONLY MARKERS — the standing rules, ground truth, mechanism map, standing
#      instructions, chat style, and the five STANDING LANE RULES, in both mirrors.
#   3. SIZE CAPS — .hermes.md ≤ 48,000 CHARS (Hermes prompt_builder.py: the dynamic cap at a
#      200 K window is ctx×4×0.06; an over-cap file loses its MIDDLE, head 70 % + tail 20 % kept);
#      AGENTS.md ≤ 32,768 BYTES (Codex project_doc_max_bytes default).
#   4. STANDING PROJECT RULES — the fifteen numbered lines hash-identical across all three.
#   5. The GitNexus-managed block (`# GitNexus — Code Intelligence`) stays LAST: `analyze`
#      rewrites from that heading down, so a section placed after it would be clobbered.
# Then the negative controls: each check is run on a mutated scratch copy and must FAIL for
# its exact reason (a gate that passes everything is a tautology).
#
#   bash harness-ports/tests/test_context_mirrors.sh          # exit 0 only if all pass
#   MIRROR_ROOT=<dir> bash …/test_context_mirrors.sh --check  # the checker alone, on <dir>
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
HERMES_MAX_CHARS=48000
AGENTS_MAX_BYTES=32768
GITNEXUS_H1='# GitNexus — Code Intelligence'
GITNEXUS_START='<!-- gitnexus:start -->'
GITNEXUS_END='<!-- gitnexus:end -->'
MANAGED_H2='Always Do|Never Do|Resources|CLI'

# CLAUDE.md-heading pattern  |  heading pattern required in each mirror (grep -i -E on `## `/`### ` lines)
TABLE='GIT BRANCH RULES|GIT BRANCH RULES
SWARM ORCHESTRATION|orchestration & honey
NO STUBS|NO STUBS
^## Project$|^## Project$
Environment & Tools|Environment & tools
Feature Workflow|Feature workflow
Behavioral guidelines|Behavioral guidelines
build loop|build loop
deep-work protocol|deep-work protocol
^## Telemetry|^## Telemetry
SESSION-RESUME|Session-resume
incident log|Incident log
Code-intelligence|Code intelligence'
MIRROR_ONLY='STANDING PROJECT RULES
GROUND TRUTH
mechanism map
Standing instructions
Chat style'
LANE_RULES='CONTEXT BUDGET
INCREMENTAL REPORT
MECHANICAL GATES ARE BOUNDED
PREMISE CONFLICTS ARE BOUNDED
CODE INTEL FIRST'

headings() { grep -E '^#{1,3} ' "$1"; }          # H1..H3 lines
rules_hash() { sed -n '/^### STANDING PROJECT RULES/,/^###\|^## /{ /^[0-9]\+\. /p }' "$1" | md5sum | cut -d' ' -f1; }
rules_count() { sed -n '/^### STANDING PROJECT RULES/,/^###\|^## /{ /^[0-9]\+\. /p }' "$1" | wc -l; }

# check_mirrors <dir> → prints FAIL lines, returns their count
check_mirrors() {
  local d="$1" fails=0 c="$1/CLAUDE.md" a="$1/AGENTS.md" h="$1/.hermes.md"
  for f in "$c" "$a" "$h"; do [ -f "$f" ] || { echo "FAIL missing $f"; return 1; }; done
  # 1. section parity, driven by CLAUDE.md's own H2 list
  while IFS= read -r line; do
    local title="${line#\#\# }"
    echo "$title" | grep -qE "^($MANAGED_H2)$" && continue
    local found=0 row
    while IFS='|' read -r cpat mpat; do
      [ -n "$cpat" ] || continue
      if echo "$line" | grep -qiE -- "$cpat"; then
        found=1
        for m in "$a" "$h"; do
          headings "$m" | grep -qiE -- "$mpat" || { echo "FAIL section '$title' of CLAUDE.md has no heading matching /$mpat/ in $(basename "$m")"; fails=$((fails+1)); }
        done
        break
      fi
    done <<< "$TABLE"
    [ $found -eq 1 ] || { echo "FAIL unmapped CLAUDE.md section '$title' — add a TABLE row here and the section to both mirrors"; fails=$((fails+1)); }
  done < <(grep -E '^## ' "$c")
  # 2. mirror-only markers + the five standing lane rules
  for m in "$a" "$h"; do
    while IFS= read -r mk; do
      [ -n "$mk" ] || continue
      headings "$m" | grep -qiF -- "$mk" || { echo "FAIL $(basename "$m") lacks the heading marker '$mk'"; fails=$((fails+1)); }
    done <<< "$MIRROR_ONLY"
    # whitespace-normalized: a rule name wrapped across a line break still counts (the gate's first run
    # flagged exactly such a wrap in AGENTS.md; the layout is not the rule)
    local flat; flat="$(tr -s '[:space:]' ' ' < "$m")"
    while IFS= read -r r; do
      [ -n "$r" ] || continue
      printf '%s' "$flat" | grep -qF -- "$r" || { echo "FAIL $(basename "$m") does not name the standing lane rule '$r'"; fails=$((fails+1)); }
    done <<< "$LANE_RULES"
  done
  # 3. size caps — chars for Hermes (len(content)), bytes for Codex (project_doc_max_bytes)
  local hchars abytes
  hchars="$(python3 -c 'import sys; print(len(open(sys.argv[1], encoding="utf-8").read()))' "$h")"
  abytes="$(wc -c < "$a")"
  [ "$hchars" -le "$HERMES_MAX_CHARS" ] || { echo "FAIL .hermes.md is $hchars chars > $HERMES_MAX_CHARS (Hermes truncates the MIDDLE of an over-cap context file)"; fails=$((fails+1)); }
  [ "$abytes" -le "$AGENTS_MAX_BYTES" ] || { echo "FAIL AGENTS.md is $abytes bytes > $AGENTS_MAX_BYTES (Codex project_doc_max_bytes)"; fails=$((fails+1)); }
  # 4. the standing project rules: fifteen lines, byte-identical across the three
  local hc ha hh
  hc="$(rules_hash "$c")"; ha="$(rules_hash "$a")"; hh="$(rules_hash "$h")"
  [ "$(rules_count "$c")" -eq 15 ] || { echo "FAIL CLAUDE.md STANDING PROJECT RULES count is $(rules_count "$c"), expected 15"; fails=$((fails+1)); }
  [ "$hc" = "$ha" ] || { echo "FAIL STANDING PROJECT RULES differ between CLAUDE.md and AGENTS.md (md5 $hc vs $ha)"; fails=$((fails+1)); }
  [ "$hc" = "$hh" ] || { echo "FAIL STANDING PROJECT RULES differ between CLAUDE.md and .hermes.md (md5 $hc vs $hh)"; fails=$((fails+1)); }
  # 5. the GitNexus-managed REGION (<!-- gitnexus:start --> … <!-- gitnexus:end -->, where present) holds only the
  #    managed headings and is last. The boundary is the MARKER, not the visible H1: on 2026-09-15 a section placed
  #    between the start marker and the H1 was silently deleted by the next `analyze` (this check had anchored on the H1).
  for m in "$c" "$a"; do
    if grep -qF -- "$GITNEXUS_START" "$m"; then
      local inside after
      grep -qF -- "$GITNEXUS_END" "$m" || { echo "FAIL $(basename "$m") has $GITNEXUS_START without $GITNEXUS_END"; fails=$((fails+1)); continue; }
      inside="$(sed -n "/^$GITNEXUS_START\$/,/^$GITNEXUS_END\$/p" "$m" | grep -E '^#{1,2} ' | grep -vE "^## ($MANAGED_H2)$|^$GITNEXUS_H1\$" || true)"
      [ -z "$inside" ] || { echo "FAIL $(basename "$m") has a project heading INSIDE the GitNexus region (analyze deletes it): $inside"; fails=$((fails+1)); }
      after="$(sed -n "/^$GITNEXUS_END\$/,\$p" "$m" | tail -n +2 | grep -E '^#{1,3} ' || true)"
      [ -z "$after" ] || { echo "FAIL $(basename "$m") has a heading after the GitNexus region (the region must be last): $after"; fails=$((fails+1)); }
    fi
  done
  return $fails
}

if [ "${1:-}" = "--check" ]; then
  check_mirrors "${MIRROR_ROOT:-$ROOT}"; rc=$?
  [ $rc -eq 0 ] && echo "context-mirrors: OK ($(basename "${MIRROR_ROOT:-$ROOT}"))"
  exit $rc
fi

pass=0; fail=0
ok()   { pass=$((pass+1)); echo "ok   $1"; }
bad()  { fail=$((fail+1)); echo "FAIL $1"; }

# --- positive: the repo's own three files -------------------------------------------------------
out="$(check_mirrors "$ROOT")"; rc=$?
if [ $rc -eq 0 ]; then ok "repo mirrors: section parity, markers, caps, rules hash, block order"; else bad "repo mirrors:"; printf '%s\n' "$out"; fi

# --- negative controls: mutated scratch copies, each must FAIL for its exact reason ---------------
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fresh() { rm -rf "$TMP/$1"; mkdir -p "$TMP/$1"; cp "$ROOT/CLAUDE.md" "$ROOT/AGENTS.md" "$ROOT/.hermes.md" "$TMP/$1/"; echo "$TMP/$1"; }
expect_fail() { # name dir needle
  local out; out="$(check_mirrors "$2")"; local rc=$?
  if [ $rc -ne 0 ] && printf '%s\n' "$out" | grep -qF -- "$3"; then ok "$1"; else bad "$1 (rc=$rc; wanted '$3'; got: $(printf '%s' "$out" | head -3 | tr '\n' '|'))"; fi
}
d="$(fresh n1)"; sed -i 's/^## Feature workflow (summary)$/## Pipeline order (summary)/' "$d/.hermes.md"
expect_fail "n1 a mirror missing a CLAUDE.md section is red, naming the section and the file" "$d" "section 'Feature Workflow (summary)' of CLAUDE.md has no heading matching /Feature workflow/ in .hermes.md"
d="$(fresh n2)"; python3 -c 'import sys; open(sys.argv[1],"a",encoding="utf-8").write("x"*6000)' "$d/.hermes.md"
expect_fail "n2 an over-cap .hermes.md is red on CHARS" "$d" "chars > $HERMES_MAX_CHARS"
d="$(fresh n3)"; sed -i 's/^3\. OmniRoute is the sole model API egress\./3. OmniRoute is the main model API egress./' "$d/AGENTS.md"
expect_fail "n3 a reworded standing rule in one mirror is red on the hash" "$d" "STANDING PROJECT RULES differ between CLAUDE.md and AGENTS.md"
d="$(fresh n4)"; printf '\n## Brand New Section\n\ntext\n' >> "$d/CLAUDE.md"
expect_fail "n4 a new CLAUDE.md section with no mirror rule is red as unmapped" "$d" "unmapped CLAUDE.md section 'Brand New Section'"
d="$(fresh n5)"; python3 -c 'import sys; open(sys.argv[1],"a",encoding="utf-8").write("y"*1000)' "$d/AGENTS.md"
expect_fail "n5 an over-budget AGENTS.md is red on BYTES" "$d" "bytes > $AGENTS_MAX_BYTES"
d="$(fresh n6)"; printf '\n## Telemetry\n\nmoved here\n' >> "$d/AGENTS.md"
expect_fail "n6 a heading after the GitNexus region is red" "$d" "after the GitNexus region"
d="$(fresh n10)"; python3 - "$d/AGENTS.md" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text(encoding="utf-8")
s = s.replace("<!-- gitnexus:start -->\n", "<!-- gitnexus:start -->\n## Planted inside the region\n\ntext\n\n", 1)
p.write_text(s, encoding="utf-8")
PY
expect_fail "n10 a project heading between the start marker and the H1 is red (the 2026-09-15 clobber shape)" "$d" "INSIDE the GitNexus region"
d="$(fresh n7)"; sed -i 's/CODE INTEL FIRST/CODE INTEL LATER/g' "$d/.hermes.md"
expect_fail "n7 a missing standing lane rule is red by name" "$d" "does not name the standing lane rule 'CODE INTEL FIRST'"
d="$(fresh n9)"; sed -i 's/CONTEXT BUDGET/CONTEXT\nBUDGET/' "$d/.hermes.md"
if out="$(check_mirrors "$d")"; then ok "n9 a rule name wrapped across a line break still counts (layout is not the rule)"; else bad "n9 wrapped rule name rejected: $(printf '%s' "$out" | head -2 | tr '\n' '|')"; fi
d="$(fresh n8)"; sed -i '/^3\. OmniRoute is the sole model API egress/d' "$d/CLAUDE.md"
expect_fail "n8 a dropped standing rule in CLAUDE.md is red on the count" "$d" "STANDING PROJECT RULES count is 14, expected 15"

echo; echo "$pass passed, $fail failed"
[ $fail -eq 0 ]
