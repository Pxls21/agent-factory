# T91 build report — provider mix and safety-filter FAILED family

## Header

- PIN: `93faca0`.
- Venue/route: PC code-implementer, `agentfactory-build-local`. The dispatcher role default is medium; on the vLLM route the effort is the server default and cannot be set per request.
- Proposal status: self-validated build output only. The sandbox-side adversarial-verifier has not graded it.
- File identity:

| File | Before (sha256 first 16) | After (sha256 first 16) |
|---|---:|---:|
| `scripts/pc_lane.sh` | `e761855ad95f0088` | `a5a48539e40313b` |
| `harness-ports/bin/pc-lane.sh` | `4d8eb3af3b900c8c` | `0e000f53ef6d3899` |

## Item 1 — premise

Verified at `2026-09-22T09:36:03Z`:

- Identity and size matched: dispatcher 410 lines; PC-side runner 494 lines.
- Dispatcher section headers, `POLL_SECONDS`, `MAX_POLLS`, the one-line probe, and harvest seam matched.
- PC-side `CAPACITY_RX`, `QUOTA_RX`, `PERSIST_RX`, retry classification, FAILED sweep, and draft promotion matched behavior.
- Baseline: `53 passed, 0 failed`, rc 0.
- Baseline: `pc_lane dispatcher: 19 passed, 0 failed`, rc 0.

Discrepancy: the brief placed the PC-side final FAILED sweep at lines 455-459 and draft promotion at 461-464. At the PIN, the executable blocks were lines 462-466 and 468-471. The bytes and behavior matched; those two sub-line references drifted by seven lines.

## Item 2 — PC-side safety refusal

Production changes:

- In `harness-ports/bin/pc-lane.sh`, the new `SAFETY_RX` definition follows the persistence-refusal documentation and accepts the measured two-space warning-glyph line, one-space and zero-space renderings, or no glyph.
- In the new first-non-empty-line classification block before the capacity retry branch, the runner prefixes FAILED evidence with `safety-filter: `, removes `report.md`, optionally promotes the incremental draft to `report.partial.md`, and exits 70.
- Capacity and quota matching remain in their existing later arms.

Red first: `54 passed, 3 failed`, rc 1. The three reds were terminal classification, partial-draft preservation, and no-glyph matching. The quoted-report control was green before the fix.

Tests added in the safety-refusal section of `harness-ports/tests/test_pc_lane.sh`:

- `a safety-filter refusal is FAILED after exactly one attempt: prefixed reason, rc 70, no report and no retry artifact`.
- `a safety-refused lane promotes its draft only to report.partial.md under a PARTIAL header`.
- `NEGATIVE CONTROL: safety text quoted inside the first non-empty report line remains a real report`.
- No-glyph, one-space, and zero-space warning-glyph family cases.

## Item 3 — sandbox poller and partial harvest

Production changes:

- In `scripts/pc_lane.sh`, the existing `*FAILED*` arm now reads the FAILED file once. A `safety-filter: ` reason prints the required terminal guidance.
- The same arm fetches `report.partial.md` as `$OUT/report-$LANE_ID.partial.md` and prints `pc_lane: partial -> ...`; it never creates a normal report.

Red first: the dispatcher suite reported `pc_lane dispatcher: 19 passed, 5 failed`, rc 1 across the poll/harvest and provider-mix cases.

The minimal test seam is `POLL_SECONDS=0 MAX_POLLS=1`; no poll-loop restructuring was needed. The safety poll test covers the prescribed message, rc 70, FAILED reason, and partial fetch. The READY negative control proves the ordinary harvest still exits 0.

## Item 4 — measured provider mix at harvest

Production changes:

- In the launch block of `scripts/pc_lane.sh`, `LAUNCH_AT` and the one-minute candidate-tag lead window are recorded before launch.
- In the harvest block of `scripts/pc_lane.sh`, the code selects the role-default combo unless `HERMES_MODEL` is explicit, base64-ships one SQL script, opens the OmniRoute DB with SQLite read-only URI mode, and queries launch minus 60 seconds through harvest.
- The SQL groups provider class by status and emits every distinct tag's first/last time and count. It emits metadata for an empty window and for conversations outside the launch-candidate interval.
- The default database path is the PC-owned `/home/rocco/.omniroute-migrated/storage.sqlite`, not `$HOME`, because the dispatcher runs on the sandbox and `$HOME` would select the wrong host. `OMNIROUTE_CALL_LOG_DB` remains the explicit override.

Tests in the T91 poll/harvest section of `harness-ports/tests/test_pc_lane_dispatcher.sh` cover:

- READY harvest plus one-tag no-caveat negative control.
- Hostile explicit combo text escaped as a SQL literal; the captured generated SQL pins `api_key_name = 'hermes'`, combo filtering, and the provider-class rule.
- Two-provider output and query-derived one-other-conversation caveat.
- Empty result.
- Bridge/SQLite failure with unchanged rc 0.

Instrument check: the same five-column UNION query shape executed against `/home/rocco/.omniroute-migrated/storage.sqlite` in read-only mode for a measured build-combo window and returned six Codex status-200 rows and six Qwen status-400 rows, one TAG row, rc 0. An earlier probe found a UNION arity error; the final query corrected every arm to five columns before gates.

## Item 5 — tag-to-lane measurement

Instrument: read-only SQLite query, filtered by `api_key_name='hermes'`, combo, and each stated lane lifetime.

| Lane | Combo | Window UTC | Distinct tags in combo window |
|---|---|---:|---:|
| K1-d | `agentfactory-build-local` | 05:58:00-09:36:21 | 11 |
| GOV2c-A | `agentfactory-verify-local` | 08:55:00-09:24:28 | 4 |
| GOV2c-B | `agentfactory-verify-local` | 09:15:00-10:29:59 sample | 8 |
| B8 | `agentfactory-build-local` | 08:17:00-10:29:59 sample | 13 |

Measured tag table, shortened UUIDs but exact intervals/counts:

- K1-d: `conv_daffd349(06:04:30-07:05:13,n=37)`, `conv_4b4a3921(07:13:56-09:27:49,n=11)`, `conv_38d788c(07:15:06-07:59:43,n=20)`, `conv_97798c68(07:19:51-08:06:38,n=50)`, `conv_6af33255(08:09:42-09:03:25,n=38)`, `conv_5425621d(08:09:44-08:09:50,n=3)`, `conv_075e7e36(08:09:45-08:09:45,n=1)`, `conv_0b16dfb2(08:09:50-09:36:21,n=151)`, `conv_ca2de368(08:18:21-09:35:14,n=34)`, `conv_728e81bd(09:28:07-09:36:09,n=13)`, `conv_4e232ff5(09:34:24-09:34:24,n=1)`.
- GOV2c-A: `conv_73cba6b2(08:55:57-09:15:52,n=82)`, `conv_8b703011(09:15:37-09:16:00,n=3)`, `conv_18f4982b(09:15:46-09:24:28,n=33)`, `conv_b73b6efb(09:23:37-09:24:09,n=2)`.
- GOV2c-B: `conv_73cba6b2(09:15:07-09:15:52,n=3)`, `conv_8b703011(09:15:37-09:38:55,n=6)`, `conv_18f4982b(09:15:46-09:24:28,n=33)`, `conv_b73b6efb(09:23:37-09:43:37,n=73)`, `conv_1f5df66f(09:38:25-10:09:55,n=40)`, `conv_928c131c(09:54:14-10:25:04,n=49)`, `conv_1f202a7a(09:54:25-09:54:25,n=1)`, `conv_9d37fa42(10:11:02-10:29:38,n=52)`.
- B8: `conv_6af33255(08:18:18-09:03:25,n=28)`, `conv_ca2de368(08:18:21-10:29:41,n=65)`, `conv_0b16dfb2(08:18:27-09:36:23,n=148)`, `conv_4b4a3921(09:26:45-09:27:49,n=6)`, `conv_728e81bd(09:28:07-09:44:12,n=22)`, `conv_4e232ff5(09:34:24-09:34:24,n=1)`, `conv_beae8a82(09:44:19-10:09:50,n=44)`, `conv_c411ed1(10:03:58-10:13:35,n=4)`, `conv_05b29770(10:10:25-10:12:57,n=10)`, `conv_acb1998f(10:13:02-10:19:52,n=14)`, `conv_0f86f45(10:20:02-10:28:28,n=20)`, `conv_0e002b6a(10:28:42-10:29:33,n=4)`, `conv_2503759f(10:29:41-10:29:41,n=1)`.

Result: every combo window contains several overlapping conversation tags. `call_logs` carries no lane identifier, and the completed lane `usage.json` session IDs had zero substring matches in `correlation_id`, `session_tag`, `request_summary`, or `combo_execution_key`. Therefore this measurement cannot prove whether one lane owns one tag or several. A future version cannot attribute by tag alone from current data. The implemented harvest line is deliberately per combo and labels non-candidate tags as other conversations.

## Mutation audit

Every mutant lived in a scratch copy and passed `bash -n` before its test ran.

| Mutant | Killing test | Result |
|---|---|---|
| M1 delete `SAFETY_RX` | `a safety-filter refusal is FAILED after exactly one attempt...` | `54 passed, 5 failed`, rc 1 |
| M2 drop regex start anchor | `NEGATIVE CONTROL: safety text quoted inside the first non-empty report line remains a real report` | `58 passed, 1 failed`, rc 1 |
| M3 invert provider-caveat condition | READY one-tag negative control and two-provider query-derived caveat | `pc_lane dispatcher: 22 passed, 2 failed`, rc 1 |

## Gates

- `2026-09-22T12:22:53Z`: final focused PC runner `59 passed, 0 failed`, rc 0.
- `2026-09-22T12:23:03Z`: repeat PC runner `59 passed, 0 failed`, rc 0. Identical.
- `2026-09-22T12:23:14Z`: final focused dispatcher `pc_lane dispatcher: 24 passed, 0 failed`, rc 0.
- `2026-09-22T12:23:15Z`: repeat dispatcher `pc_lane dispatcher: 24 passed, 0 failed`, rc 0. Identical.
- `2026-09-22T12:23:38Z`: final `ALL SUITES PASSED`; `test_pc_lane.sh 59 passed, 0 failed`; `test_pc_lane_dispatcher.sh pc_lane dispatcher: 24 passed, 0 failed`; all other suite lines green.
- `2026-09-22T12:30:26Z`: outer dispatcher smoke with a local bridge seam returned rc 0 and printed the provider-mix harvest line for `agentfactory-build-local`. The captured generated SQL executed independently against the real read-only DB with rc 0 and returned three status-200 rows for the Qwen provider class plus one tag row. This exercised the production `LAUNCH_AT`/`MIX_CAVEAT` path that the focused fake bridge does not run.
- `2026-09-22T12:22:30Z`: final `bash -n` both production scripts rc 0; `git diff --check` rc 0.
- Final sha256: dispatcher `a5a48539e40313b438707db4f7e1aa3dee6986188a31a849dbf248a8a1199148`; PC runner `0e000f53ef6d3899fb148b243ee5215bd36e9ab962bfc0ffbdb7e1cdcd4a2ceb`.
- Final AP screen: one pre-existing AF-AP-45 hit in `harness-ports/bin/pc-lane.sh` at its process-session census; zero in `scripts/pc_lane.sh`. Final test screen: one pre-existing AF-AP-87 fixture hit in the session-stop control; zero new.
- GitNexus `detect-changes` reported `No changes detected` because its clone index is 501 commits stale and does not see this detached worktree. This is unresolved instrument risk, not a low-risk result. The final `lane_context.sh` pack is at `../scratch/t91-final-pack.md`.

## Self-attack

1. **Wrong provider attribution.** Ruled out only to the available limit: output says per combo, prints all tags, and the query marks tags outside the one-minute launch-candidate interval as other conversations. Exact lane attribution remains NOT built.
2. **Safety text inside a real report becomes a false FAILED.** The first-non-empty-line rule plus the anchor-drop mutant and quoted-report control distinguish it.
3. **Query failure silently changes harvest.** Empty, malformed/failure, and successful canned outputs have separate tests; the real read-only query shape executed rc 0. The harvest tests assert rc stays 0 on query failure.

## Discrepancies

- Two PC-side line ranges in the premise drifted by seven lines; behavior and identity matched.
- `scripts/lane_context.sh` initially returned rc 64 because `../scratch` did not exist; creating the required scratch parent fixed the invocation.
- The first exact-SQL probe found a real UNION arity defect; corrected before gates.
- The first `run-all` exposed stale `/tmp` SQL-capture state in the new test; the test now cleans its owned capture before and after use. No production behavior was changed for this test defect.
- The item-5 data cannot answer “one tag or several owned by a lane.” It shows several tags in each shared combo window but no lane↔tag key. This is stated as unresolved rather than inferred.
- Report lint: `report_lint: 0 refs — OK 0, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (at 93faca0)`. The report uses file names plus enclosing blocks/test names because all changed-line references are post-PIN.

## NOT done

- No OmniRoute config/combo change.
- No routing decision.
- No edits to `CLAUDE.md`, `.hermes.md`, `AGENTS.md`, any lane directory, or GOV2c brief.
- No tag-to-lane correlation field was added; exact per-lane provider attribution remains NOT built.
- No commit, push, PR, comment, publish, service restart, or server reconfiguration.
- Independent adversarial verification has not run. This proposal requires the sandbox verify lane.
