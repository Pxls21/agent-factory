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
# FAIL-CLOSED NEGATIVE CONTROLS: each sort/comm guard independently exits 65
# =============================================================================
# sync-skills.sh has two sort guards (src line 103, dst line 104) and three comm
# guards (new-list, stale-list, common-list).  An always-failing stub triggers
# all guards at once, so removing any ONE guard leaves the others to produce
# exit 65.  These call-counting stubs fail on exactly ONE invocation, proving
# each guard independently.  Removing a single guard breaks its specific test.

GUARD_REPO="$TMP/guard-repo"
mkdir -p "$GUARD_REPO"
git -C "$GUARD_REPO" init -q
git -C "$GUARD_REPO" config user.email t@t; git -C "$GUARD_REPO" config user.name t
echo x > "$GUARD_REPO/f.txt"; git -C "$GUARD_REPO" add -A; git -C "$GUARD_REPO" commit -qm base
mkdir -p "$GUARD_REPO/.claude/skills/alpha"
echo "a" > "$GUARD_REPO/.claude/skills/alpha/SKILL.md"
mkdir -p "$GUARD_REPO/.agents/skills/alpha"
echo "a" > "$GUARD_REPO/.agents/skills/alpha/SKILL.md"
export AF_REPO="$GUARD_REPO"

REAL_SORT="$(command -v sort)"
REAL_COMM="$(command -v comm)"

# mk_counting_stub <real-binary> <fail-on-call-N> <counter-file> <stub-path>
mk_counting_stub() {
  cat > "$4" <<STUBEOF
#!/usr/bin/env bash
n=\$((\$(cat "$3" 2>/dev/null || echo 0) + 1))
echo "\$n" > "$3"
[ "\$n" -eq $2 ] && exit 3
exec "$1" "\$@"
STUBEOF
  chmod +x "$4"
}

# --- sort guard: src (call 1) -------------------------------------------------
rm -f "$TMP/ctr-sort-src"
FBIN_SS="$TMP/fbin-sort-src"; mkdir -p "$FBIN_SS"
mk_counting_stub "$REAL_SORT" 1 "$TMP/ctr-sort-src" "$FBIN_SS/sort"
out_ss="$(PATH="$FBIN_SS:$PATH" bash "$SYNC" --check 2>&1)"; rc_ss=$?
check "GUARD: src sort fails → exit 65" \
  "$([ $rc_ss -eq 65 ] && echo 0 || echo 1)" \
  "sort failing on call 1 must trigger the src-list guard (got rc=$rc_ss)"
echo "$out_ss" | grep -q "src skill-list generation failed" && ss_d=0 || ss_d=1
check "GUARD: src sort diagnostic names the src list" "$ss_d" \
  "must print 'src skill-list generation failed'"
echo "$out_ss" | grep -q "in sync" && ss_i=1 || ss_i=0
check "GUARD: src sort does NOT print 'in sync'" "$ss_i" \
  "false 'in sync' with a broken src sort is the failure this gate prevents"

# --- sort guard: dst (call 2) -------------------------------------------------
rm -f "$TMP/ctr-sort-dst"
FBIN_SD="$TMP/fbin-sort-dst"; mkdir -p "$FBIN_SD"
mk_counting_stub "$REAL_SORT" 2 "$TMP/ctr-sort-dst" "$FBIN_SD/sort"
out_sd="$(PATH="$FBIN_SD:$PATH" bash "$SYNC" --check 2>&1)"; rc_sd=$?
check "GUARD: dst sort fails → exit 65" \
  "$([ $rc_sd -eq 65 ] && echo 0 || echo 1)" \
  "sort failing on call 2 must trigger the dst-list guard (got rc=$rc_sd)"
echo "$out_sd" | grep -q "dst skill-list generation failed" && sd_d=0 || sd_d=1
check "GUARD: dst sort diagnostic names the dst list" "$sd_d" \
  "must print 'dst skill-list generation failed'"
echo "$out_sd" | grep -q "in sync" && sd_i=1 || sd_i=0
check "GUARD: dst sort does NOT print 'in sync'" "$sd_i" \
  "false 'in sync' with a broken dst sort is the failure this gate prevents"

# --- comm guard: new-list (call 1) --------------------------------------------
rm -f "$TMP/ctr-comm-new"
FBIN_CN="$TMP/fbin-comm-new"; mkdir -p "$FBIN_CN"
mk_counting_stub "$REAL_COMM" 1 "$TMP/ctr-comm-new" "$FBIN_CN/comm"
out_cn="$(PATH="$FBIN_CN:$PATH" bash "$SYNC" --check 2>&1)"; rc_cn=$?
check "GUARD: new-list comm fails → exit 65" \
  "$([ $rc_cn -eq 65 ] && echo 0 || echo 1)" \
  "comm failing on call 1 must trigger the new-list guard (got rc=$rc_cn)"
echo "$out_cn" | grep -q "new-list comparison failed" && cn_d=0 || cn_d=1
check "GUARD: new-list comm diagnostic names the new-list comparison" "$cn_d" \
  "must print 'new-list comparison failed'"
echo "$out_cn" | grep -q "in sync" && cn_i=1 || cn_i=0
check "GUARD: new-list comm does NOT print 'in sync'" "$cn_i" \
  "false 'in sync' with a broken new-list comm is the failure this gate prevents"

# --- comm guard: stale-list (call 2) ------------------------------------------
rm -f "$TMP/ctr-comm-stale"
FBIN_CS="$TMP/fbin-comm-stale"; mkdir -p "$FBIN_CS"
mk_counting_stub "$REAL_COMM" 2 "$TMP/ctr-comm-stale" "$FBIN_CS/comm"
out_cs="$(PATH="$FBIN_CS:$PATH" bash "$SYNC" --check 2>&1)"; rc_cs=$?
check "GUARD: stale-list comm fails → exit 65" \
  "$([ $rc_cs -eq 65 ] && echo 0 || echo 1)" \
  "comm failing on call 2 must trigger the stale-list guard (got rc=$rc_cs)"
echo "$out_cs" | grep -q "stale-list comparison failed" && cs_d=0 || cs_d=1
check "GUARD: stale-list comm diagnostic names the stale-list comparison" "$cs_d" \
  "must print 'stale-list comparison failed'"
echo "$out_cs" | grep -q "in sync" && cs_i=1 || cs_i=0
check "GUARD: stale-list comm does NOT print 'in sync'" "$cs_i" \
  "false 'in sync' with a broken stale-list comm is the failure this gate prevents"

# --- comm guard: common-list (call 3) -----------------------------------------
rm -f "$TMP/ctr-comm-common"
FBIN_CC="$TMP/fbin-comm-common"; mkdir -p "$FBIN_CC"
mk_counting_stub "$REAL_COMM" 3 "$TMP/ctr-comm-common" "$FBIN_CC/comm"
out_cc="$(PATH="$FBIN_CC:$PATH" bash "$SYNC" --check 2>&1)"; rc_cc=$?
check "GUARD: common-list comm fails → exit 65" \
  "$([ $rc_cc -eq 65 ] && echo 0 || echo 1)" \
  "comm failing on call 3 must trigger the common-list guard (got rc=$rc_cc)"
echo "$out_cc" | grep -q "common-list comparison failed" && cc_d=0 || cc_d=1
check "GUARD: common-list comm diagnostic names the common-list comparison" "$cc_d" \
  "must print 'common-list comparison failed'"
echo "$out_cc" | grep -q "in sync" && cc_i=1 || cc_i=0
check "GUARD: common-list comm does NOT print 'in sync'" "$cc_i" \
  "false 'in sync' with a broken common-list comm is the failure this gate prevents"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
