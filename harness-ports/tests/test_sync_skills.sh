#!/usr/bin/env bash
# Plumbing proof for harness-ports/bin/sync-skills.sh.
#
# Builds a throwaway repo with .claude/skills and .agents/skills, then verifies:
#   - --check detects drift and exits 1
#   - copy mode fixes drift and exits 0
#   - a re-check after copy exits 0
#   - NEW and STALE dirs are reported
#   - the gitnexus parent dir is excluded
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC="$HERE/../bin/sync-skills.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0; fail=0
check() {
  if [ "$2" -eq 0 ]; then pass=$((pass+1)); echo "[PASS] $1"; else fail=$((fail+1)); echo "[FAIL] $1"; fi
  echo "         because: $3"
}

# --- build a fake repo -------------------------------------------------------
REPO="$TMP/repo"
mkdir -p "$REPO"
git -C "$REPO" init -q
git -C "$REPO" config user.email t@t; git -C "$REPO" config user.name t
echo x > "$REPO/f.txt"; git -C "$REPO" add -A; git -C "$REPO" commit -qm base

# source skills
mkdir -p "$REPO/.claude/skills/alpha"
echo "alpha-content" > "$REPO/.claude/skills/alpha/SKILL.md"
mkdir -p "$REPO/.claude/skills/beta"
echo "beta-content" > "$REPO/.claude/skills/beta/SKILL.md"
mkdir -p "$REPO/.claude/skills/gamma"
echo "gamma-content" > "$REPO/.claude/skills/gamma/SKILL.md"
# the gitnexus parent dir (should be excluded)
mkdir -p "$REPO/.claude/skills/gitnexus"

# destination: alpha in sync, beta drifted, gamma missing (NEW)
mkdir -p "$REPO/.agents/skills/alpha"
echo "alpha-content" > "$REPO/.agents/skills/alpha/SKILL.md"
mkdir -p "$REPO/.agents/skills/beta"
echo "WRONG-content" > "$REPO/.agents/skills/beta/SKILL.md"
# gamma not present = NEW
# stale dir: exists in .agents but not .claude
mkdir -p "$REPO/.agents/skills/old-thing"
echo "stale" > "$REPO/.agents/skills/old-thing/SKILL.md"

export AF_REPO="$REPO"

# --- --check should find drift and exit 1 ------------------------------------
out="$(bash "$SYNC" --check 2>&1)"; rc=$?
check "--check exits 1 when drift exists" "$([ $rc -eq 1 ] && echo 0 || echo 1)" \
  "exit 1 means drift was found"
echo "$out" | grep -q "DRIFT" && d=0 || d=1
check "--check reports DRIFT" "$d" "beta has wrong content"
echo "$out" | grep -q "NEW" && n=0 || n=1
check "--check reports NEW" "$n" "gamma is in source but not destination"
echo "$out" | grep -q "STALE" && s=0 || s=1
check "--check reports STALE" "$s" "old-thing is in destination but not source"
echo "$out" | grep -q "gitnexus" && g=1 || g=0
check "gitnexus parent dir is excluded" "$g" "the empty gitnexus dir is not a skill"

# --- copy mode should fix drift and exit 0 -----------------------------------
out2="$(bash "$SYNC" 2>&1)"; rc2=$?
check "copy mode exits 0" "$([ $rc2 -eq 0 ] && echo 0 || echo 1)" \
  "new + drifted dirs were copied"
cmp -s "$REPO/.claude/skills/beta/SKILL.md" "$REPO/.agents/skills/beta/SKILL.md"; c=$?
check "beta content fixed after copy" "$([ $c -eq 0 ] && echo 0 || echo 1)" \
  "drifted file replaced with source content"
[ -f "$REPO/.agents/skills/gamma/SKILL.md" ] && gm=0 || gm=1
check "gamma (NEW) copied to destination" "$gm" \
  "new skills are added"

# --- re-check should be clean ------------------------------------------------
out3="$(bash "$SYNC" --check 2>&1)"; rc3=$?
check "re-check after copy exits 0" "$([ $rc3 -eq 0 ] && echo 0 || echo 1)" \
  "no drift remains"

# --- stale dir left in place --------------------------------------------------
[ -d "$REPO/.agents/skills/old-thing" ] && st=0 || st=1
check "stale dir left in place (not deleted)" "$st" \
  "stale dirs may be tool-managed; removal is the owner's call"

# NEGATIVE CONTROL: gitnexus not copied to destination
[ ! -d "$REPO/.agents/skills/gitnexus" ] && gx=0 || gx=1
check "gitnexus dir NOT copied" "$gx" \
  "gitnexus is the empty parent dir, not a skill — copying it would be noise"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
