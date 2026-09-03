#!/usr/bin/env bash
# Plumbing proof for harness-ports/bin/sync-skills.sh.
#
# Builds a throwaway repo with .claude/skills and .agents/skills, then verifies:
#   - --check detects drift and exits 1
#   - copy mode fixes drift and exits 0
#   - a re-check after copy exits 0
#   - NEW and STALE dirs are reported
#   - the gitnexus parent dir is excluded
#   - hand-ported (allowlisted) intentional drift with matching hash → --check exit 0
#   - hand-ported dir whose base changed → exit 1 with STALE-BASE
#   - non-allowlisted drift → exit 1 with DRIFT
#   - plain run does NOT overwrite an allowlisted dir
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

# =============================================================================
# HAND-PORT-AWARE TESTS (allowlist + base hash)
# =============================================================================

# --- set up a hand-ported skill -----------------------------------------------
REPO2="$TMP/repo2"
mkdir -p "$REPO2"
git -C "$REPO2" init -q
git -C "$REPO2" config user.email t@t; git -C "$REPO2" config user.name t
echo x > "$REPO2/f.txt"; git -C "$REPO2" add -A; git -C "$REPO2" commit -qm base

# source skill: hp-skill (will be hand-ported) and plain-skill (normal)
mkdir -p "$REPO2/.claude/skills/hp-skill"
echo "base-content" > "$REPO2/.claude/skills/hp-skill/SKILL.md"
mkdir -p "$REPO2/.claude/skills/plain-skill"
echo "plain-content" > "$REPO2/.claude/skills/plain-skill/SKILL.md"

# destination: hp-skill has intentional rewording, plain-skill drifted
mkdir -p "$REPO2/.agents/skills/hp-skill"
echo "HARNESS PORT rewording" > "$REPO2/.agents/skills/hp-skill/SKILL.md"
mkdir -p "$REPO2/.agents/skills/plain-skill"
echo "WRONG-plain" > "$REPO2/.agents/skills/plain-skill/SKILL.md"

# allowlist and hash file
mkdir -p "$REPO2/harness-ports"
echo "hp-skill" > "$REPO2/harness-ports/hand-ported.txt"
# Record the current .claude base hash
hp_hash=$(sha256sum "$REPO2/.claude/skills/hp-skill/SKILL.md" | cut -d' ' -f1)
printf '%s  %s\n' "$hp_hash" "hp-skill" > "$REPO2/harness-ports/hand-ported.sha256"

export AF_REPO="$REPO2"

# --- POSITIVE: allowlisted intentional drift with matching hash → exit 0 ------
# (only hp-skill differs, and its hash matches — plain-skill also differs but it's non-allowlisted)
# We need plain-skill to be in sync for this test to isolate the allowlist behavior.
cp "$REPO2/.claude/skills/plain-skill/SKILL.md" "$REPO2/.agents/skills/plain-skill/SKILL.md"

out4="$(bash "$SYNC" --check 2>&1)"; rc4=$?
check "allowlisted intentional drift → --check exit 0" "$([ $rc4 -eq 0 ] && echo 0 || echo 1)" \
  "only difference is the allowlisted hp-skill whose base hash matches"
echo "$out4" | grep -q "INTENTIONAL: hp-skill" && ip=0 || ip=1
check "--check prints INTENTIONAL: hp-skill" "$ip" \
  "exact line INTENTIONAL: hp-skill must appear"

# --- NEGATIVE: allowlisted dir whose .claude base changed → exit 1 + STALE-BASE
echo "CHANGED base-content" > "$REPO2/.claude/skills/hp-skill/SKILL.md"
out5="$(bash "$SYNC" --check 2>&1)"; rc5=$?
check "stale-base allowlisted → --check exit 1" "$([ $rc5 -eq 1 ] && echo 0 || echo 1)" \
  "exit 1 because the .claude twin changed since the port"
echo "$out5" | grep -q "STALE-BASE: hp-skill" && sb=0 || sb=1
check "--check prints STALE-BASE: hp-skill" "$sb" \
  "exact line STALE-BASE: hp-skill must appear"

# restore for next test
echo "base-content" > "$REPO2/.claude/skills/hp-skill/SKILL.md"

# --- NEGATIVE: non-allowlisted drift → exit 1 with DRIFT ---------------------
echo "WRONG-plain" > "$REPO2/.agents/skills/plain-skill/SKILL.md"
out6="$(bash "$SYNC" --check 2>&1)"; rc6=$?
check "non-allowlisted drift → --check exit 1" "$([ $rc6 -eq 1 ] && echo 0 || echo 1)" \
  "exit 1 because plain-skill drifted and is not allowlisted"
echo "$out6" | grep -q "DRIFT" && dr=0 || dr=1
check "--check prints DRIFT for non-allowlisted" "$dr" \
  "DRIFT line must appear for plain-skill"

# --- POSITIVE: plain run does NOT overwrite an allowlisted dir ----------------
before_hp=$(cat "$REPO2/.agents/skills/hp-skill/SKILL.md")
bash "$SYNC" >/dev/null 2>&1
after_hp=$(cat "$REPO2/.agents/skills/hp-skill/SKILL.md")
[ "$before_hp" = "$after_hp" ] && noc=0 || noc=1
check "plain run does NOT overwrite allowlisted dir" "$noc" \
  "hp-skill content must be byte-identical before and after plain run"

# --- --record refreshes the hash file -----------------------------------------
echo "NEW base" > "$REPO2/.claude/skills/hp-skill/SKILL.md"
bash "$SYNC" --record >/dev/null 2>&1
new_hash=$(sha256sum "$REPO2/.claude/skills/hp-skill/SKILL.md" | cut -d' ' -f1)
rec_hash=$(grep 'hp-skill' "$REPO2/harness-ports/hand-ported.sha256" | cut -d' ' -f1)
[ "$new_hash" = "$rec_hash" ] && rr=0 || rr=1
check "--record refreshes base hash" "$rr" \
  "recorded hash must match current .claude twin after --record"

# =============================================================================
# FAIL-CLOSED NEGATIVE CONTROL: a broken comm must exit 65, never "in sync"
# =============================================================================

REPO3="$TMP/repo3"
mkdir -p "$REPO3"
git -C "$REPO3" init -q
git -C "$REPO3" config user.email t@t; git -C "$REPO3" config user.name t
echo x > "$REPO3/f.txt"; git -C "$REPO3" add -A; git -C "$REPO3" commit -qm base
mkdir -p "$REPO3/.claude/skills/alpha"
echo "a" > "$REPO3/.claude/skills/alpha/SKILL.md"
mkdir -p "$REPO3/.agents/skills/alpha"
echo "a" > "$REPO3/.agents/skills/alpha/SKILL.md"

FAKE_COMM="$TMP/comm-stub"
cat > "$FAKE_COMM" <<'STUBEOF'
#!/usr/bin/env bash
exit 3
STUBEOF
chmod +x "$FAKE_COMM"
FAKE_BIN="$TMP/fake-bin"
mkdir -p "$FAKE_BIN"
cp "$FAKE_COMM" "$FAKE_BIN/comm"

export AF_REPO="$REPO3"
out7="$(PATH="$FAKE_BIN:$PATH" bash "$SYNC" --check 2>&1)"; rc7=$?
check "NEGATIVE CONTROL: broken comm → exit 65 (fail-closed)" \
  "$([ $rc7 -eq 65 ] && echo 0 || echo 1)" \
  "exit code 65 means comm failed and the script refused to guess (got rc=$rc7)"
echo "$out7" | grep -q "comparison failed" && cf=0 || cf=1
check "broken comm prints failure diagnostic" "$cf" \
  "stderr must name the failure so the CI log explains the exit"
echo "$out7" | grep -q "in sync" && is=1 || is=0
check "broken comm does NOT print 'in sync'" "$is" \
  "a false 'in sync' with a broken comparator is the failure this gate prevents"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
