# PC lane — T91: the dispatcher's harvest line carries the lane's MEASURED provider mix, and the model-provider safety-block family is a FAILED lane

PIN: 93faca0

Role: code-implementer. Route: the LOCAL build route (`agentfactory-build-local`; the effort is the server default on the vLLM route —
say so in the report header). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Honey mode: ultra Lever-2 — the report is DATA
(files:lines, verbatim test counts, discrepancies, NOT-done).

## WHY (two incidents, one window)

1. **AF-AP-111 — a route claim stated from config, not from the egress log.** Every harvest line this week said "the local-Qwen lane"
   because the combo was `agentfactory-*-local`; the OmniRoute call log says the combo's step 2 (the cloud codex chain) served a large
   share of the turns — on the VERIFY-GOV2c-A lane EVERY local call returned `400 System message must be at the beginning` and the
   cloud served all of it. The provider mix is a MEASUREMENT the dispatcher must print at harvest, never a name it repeats.
2. **The VERIFY-GOV2c death (07:09Z).** The lane's context passed the local model's limit, the cloud fallback's SAFETY FILTER refused
   the brief, and the dispatcher brought a 439-byte refusal home as `report-pc-verify-gov2c.md--4cc3fe2.md` and printed
   `pc_lane: report -> …` — a refusal graded as a report. The family is in NONE of the PC side's regexes (`CAPACITY_RX`, `QUOTA_RX`,
   `PERSIST_RX`, `^API call failed`) and in none of the sandbox poller's probe arms.

## PREMISE — MEASURED at authoring (2026-09-22 09:1xZ, the sandbox clone at 93faca0 = the T90 landing; re-measure as item 1)

```
sha256 (first 16) at 93faca0: scripts/pc_lane.sh e761855ad95f0088 (410 lines) · harness-ports/bin/pc-lane.sh 4d8eb3af3b900c8c (494 lines)
scripts/pc_lane.sh (sandbox dispatcher): section headers  148/214 '# --- 1. ship the brief', 161 '# --- 0a. premise gate', 193 '# --- 0.
  headroom', 222 '# --- 1b. ship an optional patch', 243 '# --- 1c. … effort', 305 '# --- 2. launch DETACHED', 322 '# --- 3. poll LOCALLY',
  367 '# --- 4. bring the report home'; knobs :119 POLL_SECONDS=15, :120 MAX_POLLS=240; the probe :343
    probe="$(bridge "test -f $PC_AF_REPO/.lanes/$LANE_ID/FAILED && echo FAILED || (test -s $REMOTE_REPORT && grep -Eq '^API call failed|^(⚠️ )?No reply: ' $REMOTE_REPORT && ! kill -0 … && echo FAILED-UNRETRIED …
  arms :344-357: *FAILED-UNRETRIED* (exit 70) · *FAILED* (exit 70) · *READY* · *RUNNING* · *GONE*; timeout :362; harvest :369-400
  (LOCAL_REPORT :369, 'report ->' :373, the patch in 40,000-char slices :383-397, 'patch  ->' :398, 'no changes' :400)
harness-ports/bin/pc-lane.sh (PC side): CAPACITY_RX :269 '^API call failed after [0-9]+ retries: ' · PERSIST_RX :300 '^(⚠️ )?No reply: ' ·
  the retry decision :435-449 (grep CAPACITY_RX|PERSIST_RX → report.attempt$N.md, report.md emptied, backoff, continue) ·
  the FAILED sweep :455-459 (grep CAPACITY_RX|QUOTA_RX|PERSIST_RX|^API call failed → $LANE_DIR/FAILED, report.md removed, exit 70) ·
  the draft promotion :461-464 (empty report.md + a draft → 'DRAFT REPORT — … PARTIAL')
the specimen (tasks/briefs/pc/report-pc-verify-gov2c.md--4cc3fe2.md, 439 bytes, the dead lane's whole "report"), first line:
  ⚠️  The model provider's safety filter blocked this request (not a Hermes/gateway failure).
  then: 'Provider message: This content was flagged for possible cybersecurity risk. …' and 'Try rephrasing the request, narrowing the
  context, or adding a fallback provider with `hermes fallback add`.'
tests: harness-ports/tests/test_pc_lane.sh (53 passed at 93faca0; a fake harness echoes its stdin; the families covered: capacity 503
  retry :199, exhausted → FAILED :213, 429 cooldown :236, quota :255/:279/:291, 'No reply' :317/:320/:328, draft promotion :401/:412,
  a non-applying patch :427) · harness-ports/tests/test_pc_lane_dispatcher.sh (19 passed; a fake `bridge()` at :40 records calls;
  `run_gate` :72; the poll loop is NOT exercised — every case exits before section 3)
OmniRoute call log: /home/rocco/.omniroute-migrated/storage.sqlite, table call_logs; columns include timestamp (ISO, 'YYYY-MM-DDTHH:MM:SS.sssZ'),
  combo_name, combo_step_id, provider, status, tokens_in, tokens_out, error_summary, session_tag, correlation_id, api_key_name
  ('hermes' for every lane row). session_tag = 'conv_<uuid>' per Hermes conversation; it is NOT in the Hermes state.db sessions table
  (no column holds it; grep of the lane dir and the db for the uuid: 0 hits) — the lane→tag link is TEMPORAL: the tag whose first row
  falls in the lane's launch window. Measured at 09:15-09:19Z on the verify combo: the GOV2c-B launch (09:15Z) → conv_18f4982b… first
  row 09:15:46 (11 rows by 09:18Z) while GOV2c-A's conv_73cba6b2… continued and a THIRD tag conv_8b703011… appeared at 09:15:37
  (3 rows) — a lane may own MORE than one tag over its life (a Hermes compression or sub-session?): item 3 measures this.
provider-mix query shape (measured, the E1-R1 window 07:20-08:25Z, combo agentfactory-build-local):
  select provider-class, status, count(*), max(tokens_in) … group by 1,2 →
  agentfactory-build-local:499=2 codex:200=15 qwen:200=64 qwen:400=13 qwen:499=2 qwen:504=1
  (provider class: 'openai-compatible-chat-…' → qwen, 'codex' → codex, the combo's own name → the combo layer's 499 'Request aborted')
sqlite over the bridge: ship the SQL as a base64-decoded script file (CLAUDE.md: a double-quoted string inside the bridge command is an
  IDENTIFIER to SQLite) — the dispatcher already ships the brief that way (:214-221).
```

## CONTRACT (build these; each with a deterministic test; the two files below are the boundary)

1. **PREMISE first (stop on failure):** re-run the sha/line-map commands above on your worktree; a different hunk set or identity →
   CONTRACT-INVALID, stop. Run `bash harness-ports/tests/test_pc_lane.sh` and `bash harness-ports/tests/test_pc_lane_dispatcher.sh`
   once each and paste the two summary lines (expected `53 passed, 0 failed` and `19 passed, 0 failed`).
2. **The safety-block family is a FAILED lane on the PC side (`harness-ports/bin/pc-lane.sh`).** Add `SAFETY_RX` matching the
   specimen's first line (`^(⚠️ *)?The model provider's safety filter blocked` — the two spaces after the glyph in the specimen must
   match, and so must one or none). In the end-of-attempt classification: a report matching `SAFETY_RX` is NEVER retried (the refusal
   is deterministic for the same context — a retry from the draft replays the same context into the same filter) and NEVER stands as
   report.md: the line goes to `$LANE_DIR/FAILED` with the prefix `safety-filter: `, report.md is removed, the draft (if any) is
   promoted the way :461-464 promotes it but into `$LANE_DIR/report.partial.md` (never report.md — the poller must not read a
   PARTIAL as READY), rc 70. The QUOTA and CAPACITY paths are untouched. Tests in `test_pc_lane.sh` (the fake harness prints the
   specimen): (a) FAILED written with the `safety-filter: ` prefix, no report.md, rc 70, NO backoff sleep (`LANE_CAPACITY_BACKOFF=0`
   is not enough evidence — assert attempt count 1 via the absence of `report.attempt1.md`); (b) with a draft present, `report.partial.md`
   holds the draft under the PARTIAL header and report.md is absent; (c) NEGATIVE CONTROL: the specimen text appearing INSIDE an
   otherwise real report (a lane quoting it) is NOT the family — the match is anchored to the report's FIRST non-empty line.
3. **The sandbox poller reads it (`scripts/pc_lane.sh` section 3).** The probe at :343 gains the FAILED-file case it already has
   (the PC side writes FAILED) — verify that a `safety-filter: ` FAILED comes home through the existing `*FAILED*` arm with the
   reason printed, and add the poller-side message `pc_lane: LANE FAILED — the model provider's safety filter refused the request
   (a re-dispatch replays the same refusal; split the brief or change the route)`; if `report.partial.md` exists, bring it home as
   `$OUT/report-$LANE_ID.partial.md` and print `pc_lane: partial -> …`. The poll loop is not reachable in `test_pc_lane_dispatcher.sh`
   today (item 1 measured it): add the minimal seam — `POLL_SECONDS=0 MAX_POLLS=1` + the fake `bridge()` answering the probe with
   `FAILED` and the FAILED file's text — and test (a) the message and rc 70, (b) the partial brought home, (c) NEGATIVE CONTROL: a
   READY probe still harvests as before. If the seam needs a structural change larger than an env-guarded early return, STOP and
   report the shape you would need (the coordinator decides) rather than restructuring section 3.
4. **The provider mix at harvest (`scripts/pc_lane.sh` section 4).** Record the launch instant (`LAUNCH_AT=$(date -u +%FT%TZ)`,
   already computable at :305) and at harvest run ONE bridge sqlite query (a base64-shipped script, read-only `file:…?mode=ro`) over
   `[LAUNCH_AT - 60 s, now]` for the lane's combo (`agentfactory-build-local` for code-implementer, `agentfactory-verify-local` for
   adversarial-verifier, the cloud combos by `HERMES_MODEL` when set), grouped by provider class × status, plus the distinct
   `session_tag`s in the window with each tag's first/last timestamp and row count. Print ONE line:
   `pc_lane: provider-mix <combo> <from>..<to>: qwen:200=N qwen:400=N codex:200=N … | tags: conv_xxxx(09:15:46-09:31:02,n=41) …`
   and a second line ONLY when the window holds more than one tag: `pc_lane: provider-mix is per COMBO — N other conversation(s)
   shared it; the lane's own share is the tag(s) starting at launch`. An empty result prints `pc_lane: provider-mix: no call_logs rows
   in the window (db=<path>)` — never silence. A bridge or sqlite failure prints `pc_lane: provider-mix unavailable: <reason>` and does
   not change the harvest's exit code. Tests (`test_pc_lane_dispatcher.sh`, the fake bridge returning canned sqlite output): the
   line's shape for a two-provider window; the multi-tag caveat line present exactly when >1 tag; the empty case; the failure case.
5. **The tag→lane relation, measured (item 3's question):** on the PC, for the lanes alive during your run, list the distinct
   `session_tag`s per combo over each lane's lifetime (K1-d since 05:58Z, GOV2c-A since 08:55Z, GOV2c-B since 09:15Z, B8 since 08:17Z;
   the launch times are in `.lanes/<id>/launch.log`'s mtime) and say whether a lane owns ONE tag or several — paste the table. This
   decides whether a future version can attribute by tag alone; it changes nothing in this increment's code.
6. **Gates:** `bash harness-ports/tests/test_pc_lane.sh` ×2 (identical summaries), `bash harness-ports/tests/test_pc_lane_dispatcher.sh`
   ×2, `bash harness-ports/tests/run-all.sh` once (one foreground call each, under the 420 s cap); `bash -n` both scripts; one
   mutant per new branch on a scratch copy (SAFETY_RX deleted → the family retried/reported again; the anchor dropped → the
   quoting-lane control goes red; the caveat condition inverted → the caveat test red), each compiled with `bash -n` and its killing
   test NAMED (AF-AP-78). Every count PASTED beside `date -u`.
7. **NOT in scope:** the OmniRoute config or combos, the owner's routing decision, `CLAUDE.md`/`.hermes.md`/`AGENTS.md` (the mirror
   lines are the coordinator's), any lane's `.lanes/<id>` directory on this host (tests use temp dirs), the three GOV2c briefs.

## DELIVERABLE

`tasks/briefs/pc-t91-support/T91-report.md`: header (PIN, sha of both files before/after, the effort note); item 1 pastes; per item
the file:line spans (in words, no revision-less bare line numbers for new code), the tests added by name, the mutants with their
killing tests; item 5's table; DISCREPANCIES (anything the premise block got wrong — say so, as T90 did); NOT-done first-class.
Lint: `python3 scripts/report_lint.py tasks/briefs/pc-t91-support/T91-report.md --rev 93faca0` — at most three fix rounds, then paste
and finish (AF-AP-76). Commit nothing, push nothing, post nothing.

**Authorization:** the dispatcher and lane scripts are this project's own tooling on the owner's own host; the call log is read
read-only; no server is touched.
