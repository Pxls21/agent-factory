# PC lane — R1-STRICT (D-039(a): the dispatcher's `LANE_ROUTE=strict` knob — a lane on the RAW local model id, no cloud fallback, every refusal LOUD; the harvest keyed on `requested_model` for strict lanes)

PIN: af56ef9  (RE-PIN RULE: this brief edits `scripts/pc_lane.sh`; if VERIFY-T90 produces a repair on that file, the coordinator re-measures this premise on the repair's landing SHA before dispatch)

Role: code-implementer. Route for THIS lane: the LOCAL build route (`agentfactory-build-local`, HYBRID in practice — the cloud
step serves a turn when the local step refuses with the chat-template 400 — say so in the report header). Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first. Honey mode: ultra Lever-2 — the report is DATA. Keep your context small.

AUTHORIZATION: defensive tooling on the owner's own lane dispatcher. Every test runs through the harness's FAKE bridge
(`harness-ports/tests/test_pc_lane_dispatcher.sh:40`; `PC_AF_REPO=/fake PC_LANE_SKIP_ADMIT=1 LANE_SET_SERVER_EFFORT=0
POLL_SECONDS=0 MAX_POLLS=1`) or a lane id that exists NOWHERE — a dispatcher reproduction NEVER names a real brief or a live
lane. No OmniRoute config change (D-039(a) is met by the RAW model id, which OmniRoute already routes: 1,817 rows today
requested `qwen-local/qwen3.8-27b-local`), no server touch, no commit, no push.

## THE CONTRACT

D-039 (owner 2026-09-22, "do both, not either"): (a) a strict no-cloud-fallback local route that fails LOUDLY when the local
step refuses — the `400 System message must be at the beginning` refusals become visible failures instead of silent cloud
turns; (b) the fallback combos relabelled HYBRID (landed: T91 + T90-R1). The strict route needs NO new OmniRoute combo: the
combos' local step IS the raw model id `qwen-local/qwen3.8-27b-local` (provider `openai-compatible-chat-98fcb302-…`), and a
request for that id directly has no fallback member. What is MISSING is on the dispatcher side:

1. a NAMED knob — `LANE_ROUTE=strict|hybrid` (default `hybrid`, byte-identical behavior to today): `strict` sets
   `HERMES_MODEL=qwen-local/qwen3.8-27b-local` for every role unless `HERMES_MODEL` is set explicitly (explicit wins, and an
   explicit COMBO name under `LANE_ROUTE=strict` is a refusal with rc 64 and one stderr line — a strict lane never rides a
   fallback combo by accident); the launch line pastes `route=strict model=<id>` into `lane.log` and the sandbox log;
2. the harvest keyed for strict lanes: today `MIX_COMBO="${HERMES_MODEL:-}"` (D:432) and the SQL filters
   `combo_name = '$MIX_COMBO_SQL'` (D:466) — a raw-id lane's rows carry an EMPTY `combo_name` and `requested_model = <raw
   id>`, so the harvest reads "no call_logs rows" and is BLIND on exactly the lanes D-039(a) wants observed. Under `strict`
   the SQL filters `requested_model = '<raw id>' AND COALESCE(combo_name,'') = ''` (the window bounds unchanged) and the
   line is labelled `strict-route provider mix (no fallback; every row the local provider)`: a status histogram per
   provider (200 / 400 / 499 / 504 measured today) — the aggregate/UNVERIFIED sentence of the hybrid label does NOT apply
   and must not print; the tag list stays;
3. LOUD failure on the lane side: on a strict lane a chat-template 400 ends the Hermes turn with `API call failed after N
   retries: … 400 …`; `harness-ports/bin/pc-lane.sh` must classify it as a ROUTE REFUSAL of the STRICT class (a new named
   line `pc-lane: strict-route refusal (HTTP 400 chat-template) — resuming from the draft`, counted separately from the
   capacity 503 family in `usage`/the report), still resumed from the draft under the existing retry budget; the count of
   strict refusals is pasted into the harvest line beside the mix;
4. tests through the fake bridge (T): the default is byte-identical (a golden of the shipped env for `hybrid` vs today);
   `strict` ships the raw id for each of the four roles; an explicit combo under `strict` refuses rc 64 with no ship write;
   the strict SQL text your double receives (the two predicates, the escaping of a raw id containing `'`); the strict label
   present and the hybrid aggregate sentence absent; the TB suite (pc-lane.sh) gains the strict-refusal classification
   case (a scripted report whose only output is the 400 family line → the new line, the draft promoted, the retry taken).

Files: D `scripts/pc_lane.sh` (WRITE), B `harness-ports/bin/pc-lane.sh` (WRITE, item 3 only), T
`harness-ports/tests/test_pc_lane_dispatcher.sh` (WRITE), TB `harness-ports/tests/test_pc_lane.sh` (WRITE, item 3's case),
`docs/LOCAL-MODEL-GUIDE.md` (WRITE: one paragraph on the knob + the measured route facts). Report:
`tasks/briefs/pc-t90-support/R1-STRICT-report.md`. Nothing else.

## PREMISE — MEASURED at authoring (2026-09-22T14:33:48Z, the sandbox clone at the PIN = origin head after the T90-R1 harvest; the PC clone ff-synced to the same head); re-measure as item 1

```
PIN af56ef9; date 2026-09-22T14:33:48Z
scripts/pc_lane.sh sha256[:16]=309d5cabe68ab150 lines=555 last-commit=c49880c
harness-ports/bin/pc-lane.sh sha256[:16]=0e000f53ef6d3899 lines=512 last-commit=9ca3279
harness-ports/tests/test_pc_lane_dispatcher.sh sha256[:16]=186601fb81b0a167 lines=303 last-commit=c49880c
harness-ports/tests/test_pc_lane.sh sha256[:16]=83bf3932ce70259d lines=619 last-commit=9ca3279
docs/LOCAL-MODEL-GUIDE.md sha256[:16]=b92cf6e680058aaf lines=104 last-commit=a58a1b9
--- D anchors (grep -n)
170:server_effort_for_role() { # role [HERMES_MODEL] [HERMES_REASONING] -> the server effort, or "" for a cloud route
178:SERVER_EFFORT="${LANE_SERVER_EFFORT:-$(server_effort_for_role "${ROLE:-}" "${HERMES_MODEL:-}" "${HERMES_REASONING:-}
340:for v in HERMES_MODEL HERMES_REASONING HERMES_PROFILE HERMES_TOOLSETS LANE_BRANCH LANE_CAPACITY_RETRIES LANE_CAPACIT
432:  MIX_COMBO="${HERMES_MODEL:-}"
435:          code-implementer) MIX_COMBO=agentfactory-build-local;;
436:          adversarial-verifier) MIX_COMBO=agentfactory-verify-local;;
437:          researcher|evidence-gatherer) MIX_COMBO=agentfactory-research;;
438:          curator|echo-sweeper|contract-runner) MIX_COMBO=agentfactory-sweep;;
439:          *) MIX_COMBO=agentfactory-build;;
448:  MIX_COMBO_SQL="$(printf '%s' "$MIX_COMBO" | sed "s/'/''/g")"
466:    AND combo_name = '$MIX_COMBO_SQL'
512:    echo "pc_lane: combo-window provider mix (per-lane provenance UNVERIFIED) $MIX_COMBO $MIX_FROM..$MIX_TO: $MIX_CO
514:      echo "pc_lane: the mix is a COMBO-WINDOW aggregate — $MIX_OTHER conversation tag(s) shared it; per-lane exec
--- B anchors (grep -n)
260:: "${LANE_CAPACITY_RETRIES:=3}"     # extra attempts after a capacity refusal; 0 disables
267:# this regex — O2 died un-retried eight minutes into an admitted session. Any `API call failed after N retries:` l
268:# transient unless QUOTA_RX says otherwise.
269:CAPACITY_RX='^API call failed after [0-9]+ retries: '
270:QUOTA_RX='exhausted their quota'
304:SAFETY_RX="^(⚠️[[:space:]]*)?The model provider's safety filter blocked"
418:    code-implementer)     DEF_MODEL="agentfactory-build-local"; DEF_EFFORT="medium";;
419:    adversarial-verifier) DEF_MODEL="agentfactory-verify-local"; DEF_EFFORT="xhigh";;
420:    evidence-gatherer|researcher) DEF_MODEL="agentfactory-research"; DEF_EFFORT="high";;
421:    curator|echo-sweeper|contract-runner) DEF_MODEL="agentfactory-sweep"; DEF_EFFORT="medium";;
422:    *)                    DEF_MODEL="agentfactory-build";    DEF_EFFORT="ultra";;
424:  RUN_MODEL="${HERMES_MODEL:-$DEF_MODEL}"; RUN_EFFORT="${HERMES_REASONING:-$DEF_EFFORT}"
426:    agentfactory-*-local|qwen-local/*)
439:if grep -Eq "$QUOTA_RX" "$REPORT" 2>/dev/null; then quota_wait=$(quota_wait_s "$REPORT") || quota_wait=""; fi
443:if printf '%s\n' "$first_nonempty" | grep -Eq "$SAFETY_RX"; then
453:if [ "$attempt" -le "$LANE_CAPACITY_RETRIES" ] && grep -Eq "$CAPACITY_RX|$PERSIST_RX" "$REPORT" 2>/dev/null \
--- T anchors (the raw id already accepted by the effort resolver)
8:unset HERMES_MODEL HERMES_REASONING LANE_SERVER_EFFORT ROLE PC_LANE_TEST_POLL_STATE PC_LANE_TEST_PROVIDER_MIX PC_LANE_
41:run "<cloud route>" HERMES_MODEL=agentfactory-build -- code-implementer
43:run xhigh HERMES_MODEL=qwen-local/qwen3.8-27b-local HERMES_REASONING=max -- researcher
86:      [ "${PC_LANE_TEST_PROVIDER_MIX_RC:-0}" -eq 0 ] || { echo "${PC_LANE_TEST_PROVIDER_MIX_ERROR:-sqlite failed}" >&
87:      printf '%s' "${PC_LANE_TEST_PROVIDER_MIX:-}";;
162:PC_LANE_TEST_TERMINAL=applied run_dispatch HERMES_MODEL=agentfactory-build; rc=$?
253:run_poll PC_LANE_TEST_POLL_STATE=READY "PC_LANE_TEST_REPORT_B64=$READY_B64" "PC_LANE_TEST_PROVIDER_MIX=$MIX_ONE" HER
269:run_poll PC_LANE_TEST_POLL_STATE=READY "PC_LANE_TEST_REPORT_B64=$READY_B64" "PC_LANE_TEST_PROVIDER_MIX=$MIX_TWO" "PC
--- OmniRoute facts (read-only, 2026-09-22 14:3xZ): combos.data local step = {model: qwen-local/qwen3.8-27b-local, providerId: openai-compatible-chat-98fcb302-795d-4db5-baee-2754a5723a39, weight 0} followed by the cloud steps (codex/gpt-5.6-sol-ultra or codex/gpt-5.6-terra-xhigh, ollama-cloud/kimi-k3, …); today's hermes-key rows: requested_model=qwen-local/qwen3.8-27b-local under combo agentfactory-build-local: 200=545 400=646 499=16 504=15; under agentfactory-verify-local: 200=298 400=275; raw-id rows today (any combo): 1817 (00:16:50Z..14:31:45Z); rows with an EMPTY combo_name exist today for raw cloud ids (codex/gpt-5.6-terra-ultra 630, codex/gpt-5.6-sol-xhigh 387) — a raw id routes without a combo; 14 rows read requested_model = provider = combo_name = agentfactory-build-local with status 499 (the combo itself as the model; a class for the verifier, not this brief)
--- the suites at the PIN (sandbox)
dispatcher: pc_lane dispatcher: 32 passed, 0 failed
pc-lane: 59 passed, 0 failed
```

## ITEMS (in order; the report drafted after each)

1. **Re-measure the premise** (the same commands; paste). A differing sha → STOP, first section = the discrepancy.
2. **The knob** in D (contract item 1) — read D's env-forward list (D:340) and the effort resolver (D:170-178) first: the raw
   id already resolves as a local route for the effort clamp (T:43); ship `LANE_ROUTE` too so `pc-lane.sh` can print it.
3. **The strict harvest** in D (contract item 2): the two-predicate SQL, the strict label, the hybrid sentence suppressed.
4. **The strict refusal class** in B (contract item 3): the named line, the separate count, the draft resume; the existing
   `QUOTA_RX` / capacity / `SAFETY_RX` classifications untouched (a 400 is neither).
5. **Tests** (contract item 4) in T and TB; every case through the fake bridge; the hybrid golden byte-identical.
6. **Docs**: one paragraph in `docs/LOCAL-MODEL-GUIDE.md` (the knob, the measured facts, what strict does NOT fix: the
   compression no-user 400s and any handoff-free first turn are unchanged; the T93 evidence names the seams).
7. **Mutants** (in place, scratch-copy restore, killing test named): m1 `strict` still ships the combo; m2 the explicit combo
   under strict accepted; m3 the strict SQL keeps `combo_name = <raw id>`; m4 the hybrid aggregate sentence printed on strict;
   m5 the 400 family classified as capacity (the wrong counter); m6 `LANE_ROUTE` unset behaves as strict (the default flipped).
8. **Gates** (pasted): `bash -n` on D and B; T ×2, TB ×2, `harness-ports/tests/run-all.sh` ALL SUITES PASSED; `git diff
   --check`; `python3 scripts/ap_screen.py --tests D T B TB`; `python3 scripts/report_lint.py --min-refs 10` on the report.
9. **Report** with file:line refs, verbatim outputs, the mutant table, NOT-done (no live strict lane is run by this lane — the
   coordinator dispatches the first strict lane and reads its harvest line), RETRO.

## RULES THAT SURVIVE EVERYTHING

- CODE INTEL FIRST; every count pasted; the default route byte-identical; no reproduction names a real brief or lane.
- No commit, no push, no outward action; the coordinator harvests, grades, and VERIFY-R1-STRICT follows.
