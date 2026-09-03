#!/usr/bin/env bash
# Plumbing proof for harness-ports/bin/pc-lane.sh.
#
# WHAT THIS DOES AND DOES NOT PROVE. It runs pc-lane.sh against a FAKE HARNESS —
# a stub that echoes its stdin. That stand-in is deliberate and is the ONLY one
# this port permits: it isolates the plumbing (worktree creation, SHA pinning,
# role prepending, report capture, replay guard, push refusal) from the model, so
# a failure here is a script bug and not a model mood.
#
# It proves NOTHING about whether Codex or Hermes actually runs a lane well. That
# needs the owner-run smoke on the PC — see docs/HARNESS-PORTS.md.
#
# Runs entirely in a throwaway git repo under $TMPDIR. Touches nothing real.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LANE="$HERE/../bin/pc-lane.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0; fail=0
check() { # check <label> <cond-rc> <why>
  if [ "$2" -eq 0 ]; then pass=$((pass+1)); echo "[PASS] $1"; else fail=$((fail+1)); echo "[FAIL] $1"; fi
  echo "         because: $3"
}

# --- a throwaway repo standing in for the PC clone --------------------------
REPO="$TMP/agent-factory"
mkdir -p "$REPO"
git -C "$REPO" init -q
git -C "$REPO" config user.email t@t; git -C "$REPO" config user.name t
mkdir -p "$REPO/harness-ports/roles"
cat > "$REPO/harness-ports/roles/code-implementer.md" <<'EOF'
ROLE-MARKER: this is the code-implementer role body.
EOF
echo hello > "$REPO/file.txt"
git -C "$REPO" add -A >/dev/null
git -C "$REPO" commit -qm base
SHA="$(git -C "$REPO" rev-parse HEAD)"

# --- the FAKE HARNESS (test double, labelled) -------------------------------
FAKE="$TMP/fake-harness.sh"
cat > "$FAKE" <<'EOF'
#!/usr/bin/env bash
# TEST DOUBLE. Echoes stdin so the test can assert what the lane was given.
echo "FAKE-HARNESS-REPORT"
cat
EOF
chmod +x "$FAKE"

mkdir -p "$TMP/tests"
BRIEF="$TMP/tests/brief-demo.md"
{ echo "PIN: $SHA"; echo; echo "BRIEF-MARKER: summarize the tree."; } > "$BRIEF"

export AF_REPO="$REPO" PC_LANE_FAKE_HARNESS="$FAKE"
OUT="$(bash "$LANE" "$BRIEF" codex code-implementer 2>"$TMP/err")"; rc=$?

check "lane exits 0 on a clean run" "$([ $rc -eq 0 ] && echo 0 || echo 1)" \
  "exit code is the harness's; the double exits 0 (stderr: $(head -c 120 "$TMP/err" | tr '\n' ' '))"

LANE_ID="$(ls "$REPO/.lanes" 2>/dev/null | head -1)"
LD="$REPO/.lanes/$LANE_ID"
check "lane directory created under .lanes/" "$([ -n "$LANE_ID" ] && echo 0 || echo 1)" \
  "lanes are disjoint by directory, like the sandbox's agent worktrees"

check "worktree checked out at the PINNED sha" \
  "$([ "$(git -C "$LD/tree" rev-parse HEAD 2>/dev/null)" = "$SHA" ] && echo 0 || echo 1)" \
  "a lane on the wrong tree produces confident wrong work"

check "report.md captured" "$([ -s "$LD/report.md" ] && echo 0 || echo 1)" \
  "the final message is the lane's deliverable"

grep -q "ROLE-MARKER" "$LD/report.md" 2>/dev/null; check "role file was PREPENDED to the brief" $? \
  "Hermes has no role mechanism, so prepending is how a lane gets its role at all"

grep -q "BRIEF-MARKER" "$LD/report.md" 2>/dev/null; check "brief body reached the harness" $? \
  "role must not displace the brief"

# role BEFORE brief
awk '/ROLE-MARKER/{r=NR} /BRIEF-MARKER/{b=NR} END{exit !(r && b && r<b)}' "$LD/report.md"
check "role comes BEFORE the brief" $? "the role frames the brief, not the reverse"

# --- replay guard: a second run must NOT re-run ------------------------------
cp "$LD/report.md" "$TMP/first-report"
OUT2="$(bash "$LANE" "$BRIEF" codex code-implementer 2>"$TMP/err2")"; rc2=$?
grep -q "already produced a report" "$TMP/err2"; check "replay is a no-op, not a second lane" $? \
  "a timed-out bridge call gets REPLAYED; a bare relaunch would spawn a duplicate lane"
cmp -s "$TMP/first-report" "$LD/report.md"; check "replay leaves the report byte-identical" $? \
  "state guard keyed on the artifact it intends to create, per the bridge runbook"

# --- SHA pin is mandatory ----------------------------------------------------
NOPIN="$TMP/tests/brief-nopin.md"; echo "no pin here" > "$NOPIN"
bash "$LANE" "$NOPIN" codex >/dev/null 2>"$TMP/err3"; rc3=$?
grep -q "pins no SHA" "$TMP/err3"; g=$?
check "a brief with no PIN is REFUSED" "$([ $rc3 -ne 0 ] && [ $g -eq 0 ] && echo 0 || echo 1)" \
  "refusing to guess a base commit is the whole point of the pin"

# --- wrong tree is refused ---------------------------------------------------
echo second > "$REPO/file2.txt"; git -C "$REPO" add -A >/dev/null; git -C "$REPO" commit -qm second
SHA2="$(git -C "$REPO" rev-parse HEAD)"
BR2="$TMP/tests/brief-two.md"; { echo "PIN: $SHA2"; echo "BRIEF-MARKER: x"; } > "$BR2"
bash "$LANE" "$BR2" codex >/dev/null 2>"$TMP/err4"; rc4=$?
LD2="$REPO/.lanes/$(ls -t "$REPO/.lanes" | head -1)"
check "a second, differently-pinned lane gets its OWN worktree" \
  "$([ "$(git -C "$LD2/tree" rev-parse HEAD 2>/dev/null)" = "$SHA2" ] && echo 0 || echo 1)" \
  "lane id includes the pin, so two pins never share a tree"

# --- the no-push shim --------------------------------------------------------
SHIMGIT="$LD/shim/git"
check "git shim exists" "$([ -x "$SHIMGIT" ] && echo 0 || echo 1)" \
  "the no-push limit is enforced, not merely documented"
"$SHIMGIT" push origin main >/dev/null 2>"$TMP/err5"; rcp=$?
grep -qi "refused" "$TMP/err5"; g5=$?
check "git push is REFUSED by the shim" "$([ $rcp -ne 0 ] && [ $g5 -eq 0 ] && echo 0 || echo 1)" \
  "a lane that could push would bypass the sandbox-side review"
"$SHIMGIT" remote add x y >/dev/null 2>"$TMP/err6"; rcr=$?
check "git remote add is REFUSED" "$([ $rcr -ne 0 ] && echo 0 || echo 1)" \
  "adding a remote is push by another route"
"$SHIMGIT" status >/dev/null 2>&1; rcs=$?
check "ordinary git still works through the shim" "$([ $rcs -eq 0 ] && echo 0 || echo 1)" \
  "NEGATIVE CONTROL: a shim that blocked everything would pass the two tests above and be useless"

# --- the double cannot be pointed at a real brief ----------------------------
REALBRIEF="$TMP/real-brief.md"; { echo "PIN: $SHA"; echo "x"; } > "$REALBRIEF"
bash "$LANE" "$REALBRIEF" codex >/dev/null 2>"$TMP/err7"; rc7=$?
grep -q "non-test brief" "$TMP/err7"; g7=$?
check "fake harness REFUSED for a non-test brief" \
  "$([ $rc7 -ne 0 ] && [ $g7 -eq 0 ] && echo 0 || echo 1)" \
  "the one permitted stand-in must never be usable to fake a real lane"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
