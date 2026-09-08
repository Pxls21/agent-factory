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

# Hermetic: clear env vars that a parent lane or caller might export, so the
# suite's own values are never shadowed by the caller's environment.
unset LANE_ID LANE_REPORT_DRAFT TERMINAL_CWD HERMES_MODEL HERMES_REASONING 2>/dev/null || true

# Self-test mode: the hermetic-cleanup test below spawns THIS SCRIPT from a
# poisoned parent.  If the unset above worked, LANE_ID is gone; if the unset
# line is removed (the mutation), the parent's LANE_ID leaks through.
if [ "${_HERMETIC_SELF_TEST:-}" = "1" ]; then
  if [ -n "${LANE_ID:-}" ]; then echo "LEAK:$LANE_ID"; exit 99; fi
  echo "CLEAN"; exit 0
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LANE="$HERE/../bin/pc-lane.sh"
TMP="$(mktemp -d)" || { echo "FATAL: mktemp -d failed" >&2; exit 1; }
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
for test_role in adversarial-verifier researcher curator contract-runner; do
  cat > "$REPO/harness-ports/roles/$test_role.md" <<EOF
ROLE-MARKER: this is the $test_role role body.
EOF
done
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

# --- capacity refusal is retried on its exact signature, and only then --------
# TEST DOUBLE: refuses with the OmniRoute 503 line on its first call, reports on the second.
FLAKY="$TMP/flaky-harness.sh"
cat > "$FLAKY" <<'EOF'
#!/usr/bin/env bash
# TEST DOUBLE. First call: the verbatim capacity refusal Hermes prints; later calls: a report.
COUNT="${FLAKY_COUNT_FILE:?}"
n=$(( $(cat "$COUNT" 2>/dev/null || echo 0) + 1 )); echo "$n" > "$COUNT"
if [ "$n" -eq 1 ]; then
  echo "API call failed after 3 retries: HTTP 503: Structurally heavy chat request capacity is busy; retry shortly."
else
  echo "FLAKY-HARNESS-REPORT after $n attempts"; cat >/dev/null
fi
EOF
chmod +x "$FLAKY"
BRIEF8="$TMP/tests/brief-retry.md"; { echo "PIN: $SHA"; echo; echo "retry me"; } > "$BRIEF8"
export FLAKY_COUNT_FILE="$TMP/flaky-count-8"
LANE_CAPACITY_BACKOFF=0 PC_LANE_FAKE_HARNESS="$FLAKY" bash "$LANE" "$BRIEF8" codex >"$TMP/out8" 2>"$TMP/err8"; rc8=$?
LD8="$REPO/.lanes/$(ls "$REPO/.lanes" | grep '^brief-retry.md' | head -1)"
check "a capacity refusal (HTTP 503 signature) is retried and the SECOND attempt's report stands" \
  "$([ $rc8 -eq 0 ] && grep -q "after 2 attempts" "$LD8/report.md" && echo 0 || echo 1)" \
  "a transient route refusal must not cost a whole dispatch round (2026-09-03: it did, twice)"
check "the refused attempt is kept as report.attempt1.md and the retry is logged" \
  "$([ -s "$LD8/report.attempt1.md" ] && grep -q "HTTP 503" "$LD8/report.attempt1.md" && grep -q "retrying in 0s" "$TMP/err8" && echo 0 || echo 1)" \
  "evidence of the refusal survives; the launch log shows the retry"

BRIEF9="$TMP/tests/brief-noretry.md"; { echo "PIN: $SHA"; echo; echo "do not retry me"; } > "$BRIEF9"
export FLAKY_COUNT_FILE="$TMP/flaky-count-9"
LANE_CAPACITY_RETRIES=0 LANE_CAPACITY_BACKOFF=0 PC_LANE_FAKE_HARNESS="$FLAKY" bash "$LANE" "$BRIEF9" codex >"$TMP/out9" 2>"$TMP/err9"; rc9=$?
LD9="$REPO/.lanes/$(ls "$REPO/.lanes" | grep '^brief-noretry.md' | head -1)"
check "NEGATIVE CONTROL: with LANE_CAPACITY_RETRIES=0 there is ONE attempt and no retry is logged" \
  "$([ "$(cat "$FLAKY_COUNT_FILE")" = 1 ] && ! grep -q "retrying" "$TMP/err9" && echo 0 || echo 1)" \
  "a retry loop that fired on every report (not the signature) would pass the test above and mask real failures"
check "an exhausted refusal is a FAILED lane: rc 70, the reason in FAILED, and NO report.md to grade (2026-09-07: B5i's 503 stood as a report)" \
  "$([ $rc9 -eq 70 ] && grep -q "HTTP 503" "$LD9/FAILED" && [ ! -f "$LD9/report.md" ] && grep -q "pc-lane: FAILED" "$TMP/err9" && echo 0 || echo 1)" \
  "the sandbox poller printed 'report -> …' and exited 0 for a lane the route never admitted"

# --- the 429 COOLDOWN is the same transient class; the 429 QUOTA is not (2026-09-06) ----
# TEST DOUBLE: refuses with the Ollama Cloud cooldown 429 on its first call, reports on the second.
COOL="$TMP/cool-harness.sh"
cat > "$COOL" <<'EOF'
#!/usr/bin/env bash
# TEST DOUBLE. First call: the verbatim per-credential cooldown line; later calls: a report.
COUNT="${FLAKY_COUNT_FILE:?}"
n=$(( $(cat "$COUNT" 2>/dev/null || echo 0) + 1 )); echo "$n" > "$COUNT"
if [ "$n" -eq 1 ]; then
  echo "API call failed after 3 retries: HTTP 429: All credentials for model kimi-k3 are cooling down"
else
  echo "COOL-HARNESS-REPORT after $n attempts"; cat >/dev/null
fi
EOF
chmod +x "$COOL"
BRIEF11="$TMP/tests/brief-retry429.md"; { echo "PIN: $SHA"; echo; echo "retry me on cooldown"; } > "$BRIEF11"
export FLAKY_COUNT_FILE="$TMP/flaky-count-11"
LANE_CAPACITY_BACKOFF=0 PC_LANE_FAKE_HARNESS="$COOL" bash "$LANE" "$BRIEF11" codex >"$TMP/out11" 2>"$TMP/err11"; rc11=$?
LD11="$REPO/.lanes/$(ls "$REPO/.lanes" | grep '^brief-retry429.md' | head -1)"
check "a 429 per-credential COOLDOWN refusal is retried and the second attempt's report stands" \
  "$([ $rc11 -eq 0 ] && grep -q "after 2 attempts" "$LD11/report.md" && grep -q "HTTP 429" "$LD11/report.attempt1.md" && echo 0 || echo 1)" \
  "2026-09-06: two concurrent Kimi lanes tripped the cooldown and the second lane died through the exhausted fallback chain — a transient, retry it"

# TEST DOUBLE: the codex QUOTA 429 — not transient; must NOT be retried even with retries enabled.
QUOTA="$TMP/quota-harness.sh"
cat > "$QUOTA" <<'EOF'
#!/usr/bin/env bash
# TEST DOUBLE. Every call: the verbatim quota-exhausted line.
COUNT="${FLAKY_COUNT_FILE:?}"
n=$(( $(cat "$COUNT" 2>/dev/null || echo 0) + 1 )); echo "$n" > "$COUNT"
echo "API call failed after 3 retries: HTTP 429: [codex/gpt-5.5-xhigh] All codex accounts have exhausted their quota (reset after 32h 19m 41s)"
cat >/dev/null
EOF
chmod +x "$QUOTA"
BRIEF12="$TMP/tests/brief-quota429.md"; { echo "PIN: $SHA"; echo; echo "do not retry a quota"; } > "$BRIEF12"
export FLAKY_COUNT_FILE="$TMP/flaky-count-12"
LANE_CAPACITY_BACKOFF=0 PC_LANE_FAKE_HARNESS="$QUOTA" bash "$LANE" "$BRIEF12" codex >"$TMP/out12" 2>"$TMP/err12"
LD12="$REPO/.lanes/$(ls "$REPO/.lanes" | grep '^brief-quota429.md' | head -1)"
check "NEGATIVE CONTROL: the codex QUOTA 429 is NOT retried (one attempt) and the lane is FAILED, not reported" \
  "$([ "$(cat "$FLAKY_COUNT_FILE")" = 1 ] && grep -q "exhausted their quota" "$LD12/FAILED" && [ ! -f "$LD12/report.md" ] && ! grep -q "retrying" "$TMP/err12" && echo 0 || echo 1)" \
  "a quota reset is hours away; retrying it three times with backoff would only delay the fallback"

# --- a Hermes session-storage failure is the HARNESS failing, not a report (2026-09-08 13:3xZ) ----
# TEST DOUBLE: prints the verbatim `⚠️ No reply:` line Hermes emits on session_persistence_failed on its first call
# (after leaving a draft section), reports on the second — the retry must be a RESUME (the note in attempt 2's prompt).
NOREPLY="$TMP/noreply-harness.sh"
cat > "$NOREPLY" <<'EOF'
#!/usr/bin/env bash
# TEST DOUBLE. First call: a draft section + the verbatim Hermes persistence-failure line; later calls: a report.
COUNT="${FLAKY_COUNT_FILE:?}"
n=$(( $(cat "$COUNT" 2>/dev/null || echo 0) + 1 )); echo "$n" > "$COUNT"
if [ "$n" -eq 1 ]; then
  printf 'item 5 PASS\n' >> "${LANE_REPORT_DRAFT:?}"
  echo "⚠️ No reply: the turn was stopped because session storage could not be written (the transcript would have been lost on restart). This is often a full disk — free some space (or fix state.db permissions), then send your message again."
  cat >/dev/null
else
  echo "NOREPLY-HARNESS-REPORT after $n attempts"; cat >/dev/null
fi
EOF
chmod +x "$NOREPLY"
BRIEF14="$TMP/tests/brief-noreply.md"; { echo "PIN: $SHA"; echo; echo "retry me after a storage failure"; } > "$BRIEF14"
export FLAKY_COUNT_FILE="$TMP/flaky-count-14"
LANE_CAPACITY_BACKOFF=0 PC_LANE_FAKE_HARNESS="$NOREPLY" bash "$LANE" "$BRIEF14" codex >"$TMP/out14" 2>"$TMP/err14"; rc14=$?
LD14="$REPO/.lanes/$(ls "$REPO/.lanes" | grep '^brief-noreply.md' | head -1)"
check "a Hermes 'No reply: … session storage' line is retried like a refusal and the SECOND attempt's report stands" \
  "$([ $rc14 -eq 0 ] && grep -q "after 2 attempts" "$LD14/report.md" && grep -q "No reply" "$LD14/report.attempt1.md" && grep -q "session-storage failure" "$TMP/err14" && echo 0 || echo 1)" \
  "VERIFY-B5j died at item 5 on the shared state.db and the line came home as its report"
check "the retry after a storage failure is a RESUME: attempt 2's prompt carries the note and the draft survived" \
  "$([ -s "$LD14/prompt.attempt2.md" ] && grep -q "^RESUME (attempt 2" "$LD14/prompt.attempt2.md" && grep -q "item 5 PASS" "$LD14/report-draft.md" && echo 0 || echo 1)" \
  "a fresh session that does not know about the draft redoes finished items"

BRIEF15="$TMP/tests/brief-noreply-noretry.md"; { echo "PIN: $SHA"; echo; echo "storage failure, no retries"; } > "$BRIEF15"
export FLAKY_COUNT_FILE="$TMP/flaky-count-15"
LANE_CAPACITY_RETRIES=0 LANE_CAPACITY_BACKOFF=0 PC_LANE_FAKE_HARNESS="$NOREPLY" bash "$LANE" "$BRIEF15" codex >"$TMP/out15" 2>"$TMP/err15"; rc15=$?
LD15="$REPO/.lanes/$(ls "$REPO/.lanes" | grep '^brief-noreply-noretry.md' | head -1)"
check "NEGATIVE CONTROL: with no retries the storage-failure line is a FAILED lane (rc 70, reason in FAILED) and never report.md" \
  "$([ $rc15 -eq 70 ] && grep -q "No reply" "$LD15/FAILED" && [ ! -f "$LD15/report.md" ] && [ "$(cat "$FLAKY_COUNT_FILE")" = 1 ] && echo 0 || echo 1)" \
  "the sandbox poller read the line as READY and brought it home (VERIFY-B5j, 2026-09-08 13:30Z)"

# --- a lane that dies before its final report still leaves its draft ------------
# TEST DOUBLE: writes two sections to $LANE_REPORT_DRAFT, then exits with an EMPTY report.
DRAFTY="$TMP/drafty-harness.sh"
cat > "$DRAFTY" <<'EOF'
#!/usr/bin/env bash
# TEST DOUBLE. Appends sections to the draft path the lane exported, then dies silently.
printf 'C1 PASS rc=0\n' >> "${LANE_REPORT_DRAFT:?}"
printf 'C2 PASS rc=2\n' >> "${LANE_REPORT_DRAFT:?}"
cat >/dev/null
exit 137
EOF
chmod +x "$DRAFTY"
BRIEF10="$TMP/tests/brief-drafty.md"; { echo "PIN: $SHA"; echo; echo "die after two sections"; } > "$BRIEF10"
PC_LANE_FAKE_HARNESS="$DRAFTY" bash "$LANE" "$BRIEF10" codex >"$TMP/out10" 2>"$TMP/err10"; rc10=$?
LD10="$REPO/.lanes/$(ls "$REPO/.lanes" | grep '^brief-drafty.md' | head -1)"
check "an empty final report is replaced by the promoted draft, marked PARTIAL, harness rc kept" \
  "$([ $rc10 -eq 137 ] && head -1 "$LD10/report.md" | grep -q "^DRAFT REPORT" && grep -q "C2 PASS rc=2" "$LD10/report.md" && grep -q "promoted report-draft.md" "$TMP/err10" && echo 0 || echo 1)" \
  "2026-09-03: a 167-call verify lane died mid-stream and 66 minutes of grading came home only via state.db forensics"
grep -q "INCREMENTAL REPORT" "$LD10/prompt.md"; check "the standing incremental-report rule is in every lane prompt" $? \
  "a rule the lane never sees cannot be followed"
grep -q "CONTEXT BUDGET" "$LD10/prompt.md"; check "the standing context-budget rule (no skill reloads) is in every lane prompt" $? \
  "2026-09-03: a lane reloaded 75 KB of skills after each of eight compactions and lost its brief"
check "NEGATIVE CONTROL: a lane with a real final report keeps it (no draft promotion)" \
  "$(grep -q "^FAKE-HARNESS-REPORT" "$LD/report.md" && ! grep -q "^DRAFT REPORT" "$LD/report.md" && echo 0 || echo 1)" \
  "the fallback must key on an EMPTY report, never overwrite a delivered one"

# --- an optional lane patch is applied on the PIN before the harness starts (2026-09-08) --------
# scripts/pc_lane.sh ships LANE_PATCH to .lanes/<id>/lane.patch; pc-lane.sh applies it ONCE on the pinned tree so the PC
# can continue a sandbox lane whose files never reached a commit (the quota stop of 2026-09-08 left five such lanes).
mkdir -p "$REPO/.lanes/lanepatch-ok" "$REPO/.lanes/lanepatch-bad"
printf 'diff --git a/patched.txt b/patched.txt\nnew file mode 100644\n--- /dev/null\n+++ b/patched.txt\n@@ -0,0 +1 @@\n+patched\n' > "$REPO/.lanes/lanepatch-ok/lane.patch"
LANE_ID=lanepatch-ok PC_LANE_FAKE_HARNESS="$FAKE" bash "$LANE" "$BRIEF" codex code-implementer >"$TMP/out13" 2>"$TMP/err13"; rc13=$?
check "a lane patch is applied in the lane worktree before the harness runs (file present, applied line logged, rc 0)" \
  "$([ $rc13 -eq 0 ] && [ -f "$REPO/.lanes/lanepatch-ok/tree/patched.txt" ] && grep -q 'lane patch applied' "$TMP/err13" && echo 0 || echo 1)" \
  "a PC lane continuing sandbox work must start from PIN + the shipped bytes (rc=$rc13; stderr: $(head -c 160 "$TMP/err13" | tr '\n' ' '))"
printf 'diff --git a/nope.txt b/nope.txt\n--- a/nope.txt\n+++ b/nope.txt\n@@ -1 +1 @@\n-x\n+y\n' > "$REPO/.lanes/lanepatch-bad/lane.patch"
LANE_ID=lanepatch-bad PC_LANE_FAKE_HARNESS="$FAKE" bash "$LANE" "$BRIEF" codex code-implementer >"$TMP/out14" 2>"$TMP/err14"; rc14=$?
check "NEGATIVE CONTROL: a patch that does not apply is a FAILED lane — rc 70, the reason in FAILED, NO report.md" \
  "$([ $rc14 -eq 70 ] && [ -s "$REPO/.lanes/lanepatch-bad/FAILED" ] && [ ! -e "$REPO/.lanes/lanepatch-bad/report.md" ] && echo 0 || echo 1)" \
  "a lane on the wrong bytes would produce confident wrong work (rc=$rc14; FAILED: $(head -c 120 "$REPO/.lanes/lanepatch-bad/FAILED" 2>/dev/null | tr '\n' ' '))"

# --- Hermes role defaults select the live OmniRoute combos -----------------
# (ported 2026-09-03 from the owner's Codex edit of the PC checkout — same mapping, kept its test)
FAKE_HERMES="$TMP/fake-hermes.sh"
unset PC_LANE_FAKE_HARNESS FLAKY_COUNT_FILE
cat > "$FAKE_HERMES" <<'EOF'
#!/usr/bin/env bash
# TEST DOUBLE. Captures Hermes argv so route/effort selection can be asserted.
printf '%s\n' "$@" > "${HERMES_ARGS_FILE:?}"
echo "FAKE-HERMES-REPORT"
EOF
chmod +x "$FAKE_HERMES"

assert_role_route() { # role expected-model expected-effort
  role="$1" expected_model="$2" expected_effort="$3"
  export HERMES_ARGS_FILE="$TMP/hermes-args-$role"
  LANE_ID="route-$role" HERMES_BIN="$FAKE_HERMES" \
    bash "$LANE" "$BRIEF" hermes "$role" >/dev/null 2>"$TMP/route-$role.err"
  awk -v m="$expected_model" -v e="$expected_effort" '
    prev=="-m" && $0==m { found_model=1 }
    prev=="--reasoning" && $0==e { found_effort=1 }
    { prev=$0 }
    END { exit !(found_model && found_effort) }
  ' "$HERMES_ARGS_FILE"
  check "$role selects $expected_model at $expected_effort" $? \
    "role intent is stable while OmniRoute owns paid-first/free-last failover"
}
assert_role_route code-implementer agentfactory-build ultra
assert_role_route adversarial-verifier agentfactory-verify xhigh
assert_role_route researcher agentfactory-research high
assert_role_route curator agentfactory-sweep medium
assert_role_route contract-runner agentfactory-sweep medium

export HERMES_ARGS_FILE="$TMP/hermes-args-override"
LANE_ID="route-override" HERMES_MODEL="manual/override" HERMES_REASONING="low" HERMES_BIN="$FAKE_HERMES" \
  bash "$LANE" "$BRIEF" hermes code-implementer >/dev/null 2>"$TMP/route-override.err"
grep -Fxq "manual/override" "$HERMES_ARGS_FILE"; override_model_rc=$?
grep -Fxq "low" "$HERMES_ARGS_FILE"; override_effort_rc=$?
check "NEGATIVE CONTROL: explicit model and effort override the role combo" \
  "$([ $override_model_rc -eq 0 ] && [ $override_effort_rc -eq 0 ] && echo 0 || echo 1)" \
  "a hard-wired role route would block measured per-lane experiments and emergency step-downs"

# --- MUTATION-KILLING: parent-environment poison for LANE_ID -----------------
# pc-lane.sh adopts inherited LANE_ID by design (the sandbox launcher sets it).
# These tests launch pc-lane.sh under real subprocess environments using `env`,
# NOT export/unset in the same shell. This proves pc-lane.sh's actual behavior
# under both poisoned and clean parent environments.
BRIEF_ROBUST="$TMP/tests/brief-robust.md"; { echo "PIN: $SHA"; echo; echo "robustness check"; } > "$BRIEF_ROBUST"
BRIEF_ROBUST2="$TMP/tests/brief-robust2.md"; { echo "PIN: $SHA"; echo; echo "robustness isolated"; } > "$BRIEF_ROBUST2"

# Test 1: externally poisoned parent → pc-lane.sh adopts it (propagation)
env LANE_ID=parent-poison HERMES_BIN="$FAKE_HERMES" HERMES_ARGS_FILE="$TMP/hermes-args-robust" \
  bash "$LANE" "$BRIEF_ROBUST" hermes code-implementer >/dev/null 2>"$TMP/err-robust1"
check "MUTATION: externally poisoned LANE_ID IS adopted by pc-lane.sh (propagation)" \
  "$([ -d "$REPO/.lanes/parent-poison" ] && echo 0 || echo 1)" \
  "env LANE_ID=parent-poison creates a real poisoned parent — pc-lane.sh inherits it by design"

# Test 2: clean parent (env -u) → pc-lane.sh derives its own (isolation)
env -u LANE_ID HERMES_BIN="$FAKE_HERMES" HERMES_ARGS_FILE="$TMP/hermes-args-robust2" \
  bash "$LANE" "$BRIEF_ROBUST2" hermes code-implementer >/dev/null 2>"$TMP/err-robust2"
LD_ROBUST="$REPO/.lanes/$(ls -t "$REPO/.lanes" | grep '^brief-robust2' | head -1)"
check "MUTATION: clean parent → LANE_ID derived from brief (isolation)" \
  "$([ -n "$LD_ROBUST" ] && [ "$(basename "$LD_ROBUST")" != "parent-poison" ] && [ -s "$LD_ROBUST/report.md" ] && echo 0 || echo 1)" \
  "env -u LANE_ID creates a clean parent process — pc-lane.sh derives from the brief filename"

# --- MUTATION-KILLING: parent-environment poison for LANE_REPORT_DRAFT -------
# pc-lane.sh sets its own LANE_REPORT_DRAFT. This test launches under a parent
# that has a bogus draft path and proves the harness writes to the lane-local
# path, not the parent's. Kills the mutation "remove the LANE_REPORT_DRAFT
# assignment".
BRIEF_DRAFT="$TMP/tests/brief-draftpoison.md"; { echo "PIN: $SHA"; echo; echo "draft poison"; } > "$BRIEF_DRAFT"
env LANE_REPORT_DRAFT="$TMP/parent-poison-draft.md" PC_LANE_FAKE_HARNESS="$DRAFTY" \
  bash "$LANE" "$BRIEF_DRAFT" hermes code-implementer >/dev/null 2>"$TMP/err-draftpoison"
LD_DRAFT="$REPO/.lanes/$(ls -t "$REPO/.lanes" | grep '^brief-draftpoison' | head -1)"
check "MUTATION: parent LANE_REPORT_DRAFT does NOT poison the lane's draft path" \
  "$([ ! -s "$TMP/parent-poison-draft.md" ] && [ -s "$LD_DRAFT/report-draft.md" ] && echo 0 || echo 1)" \
  "env LANE_REPORT_DRAFT=... creates a poisoned parent — pc-lane.sh sets its own path"

# --- MUTATION-KILLING: line-17 hermetic cleanup (self-invocation) -------------
# The blanket `unset LANE_ID ...` at line 17 prevents a parent's exported vars
# from leaking into the suite.  The `env` tests above prove pc-lane.sh's own
# behavior but do NOT test line 17 — removing it still passes in clean CI.
#
# This test spawns THIS SCRIPT from a poisoned parent.  The self-test guard
# near the top checks whether LANE_ID survived the unset:
#   - line 17 present  → unset fires → CLEAN → exit 0  → PASS
#   - line 17 removed  → LANE_ID leaks → LEAK:… → exit 99 → FAIL
hermetic_out="$(env _HERMETIC_SELF_TEST=1 LANE_ID=suite-level-poison bash "${BASH_SOURCE[0]}" 2>&1)"
hermetic_rc=$?
check "MUTATION: line-17 unset prevents parent LANE_ID leak into suite" \
  "$([ $hermetic_rc -eq 0 ] && echo 0 || echo 1)" \
  "self-invocation with LANE_ID=suite-level-poison: line 17 must unset it (got rc=$hermetic_rc, out=$hermetic_out)"

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
