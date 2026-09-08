# VERIFY-M2 — adversarial grade of S0-06 round 2

PIN: `cb91edf217f1455edb9ab8063ec8c78d6bcf4301`

## Outcome

**PC-lane adversarial assessment: NOT-READY.** This is not an admission decision; a sandbox-side independent verifier remains required. The two blocking findings are a manifest that accepts ungraded hostile nodes under allowed names (F-27) and a claimed C6 mutation kill that survives (F-28). The required live ai-memory leg was deliberately not run: this host has no approved checkout/binary and the venue expressly prohibits building, cloning, or starting one. No artifact was minted.

Reproduced: the four required test files, checker/adaptor mutation matrices on scratch copies, a loopback-only collector shape exercise, FIFO refusal, and static PC-script seams. Reviewed statically: the three PC scripts and their cleanup/readiness paths. Skipped: a real ai-memory run, build, seed, capture, and mint, because the venue forbids them.

## 0. Mechanical gates

The direct venue command, with required exports and an absolute `--basetemp`, returned `236 passed in 86.99s`; the piped command's `PYTEST_PIPESTATUS=0`. This reproduces the coordinator's test count, not its 8-worker timing.

`pyflakes` on checker, adapter, seeder, and the S0-06 test file returned 0. `bash -n` returned 0 for `run_s0_06_legs.sh`, `start_ai_memory.sh`, and `collect_leg.sh`. The project-provided F-16 command inventory test returned `3 passed in 0.15s`. No collector or ai-memory process remained after the loopback exercise; the process census found none.

The M2 report lint reproduced as `8 refs — OK 8, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0`. The earlier draft's scratch-relative `--basetemp` error was verifier command construction, not a product finding; do not treat its provisional F-26 label as a defect.

## 1. Contract matrix and red/green evidence

### V matrix — all 20 killed

| row | independent scratch input | observed final result |
|---|---|---|
| V1 | per-leg digest disagrees | rc 1, `substrate: not the pinned ai-memory ...` |
| V2 | unsafe observed posture | rc 1, `substrate: unsafe posture ...` |
| V3 | bad `version_stdout` | rc 1, `version_stdout=ai-memory 0.0.1` |
| V4 | team raw hit says agent project | rc 1, raw provenance refusal |
| V5 | raw hits say another workspace | rc 1, raw provenance refusal |
| V6 | winner carries team title/snippet | rc 1, winner-content refusal |
| V7 | written page has note/episodic type | rc 1, write-content refusal |
| V8 | forged page path | rc 1, re-derived path refusal |
| V9 | changed idempotency key | rc 1, re-derived path refusal |
| V10 | authorized tokens only in recall note | rc 1, `leak_empty` |
| V11 | authorized tokens only in `scopes_queried` | rc 1, `leak_empty` |
| V12 | forbidden token in debug field | rc 1, leak refusal |
| V13 | `http-request` event | rc 1, denied allowlist refusal |
| V14 | nested event object | rc 1, denied allowlist refusal |
| V15 | `HTTP_REQUEST` event | rc 1, denied allowlist refusal |
| V16 | empty denied events | rc 1, missing denial refusal |
| V17 | unknown direct sibling | rc 1, `leg: unexpected evidence file denied/recall-real.json` |
| V18 | `NaN` evidence | rc 1, non-RFC-8259 refusal |
| V19 | empty precedence records | rc 1, agent-winner refusal |
| V20 | duplicate written page | rc 1, idempotency refusal |

### H/L/G matrices — all requested hostile values fail closed

H1–H10 malformed evidence shapes each returned rc 1 with one named `... evidence shape invalid (...)` line; H11 a symlinked evidence root returned rc 1, `evidence: ... is not a plain directory`. L1 version bump, L2 renamed lock section, L3 renamed commit field, L4 duplicate `ai-memory` block, and L5 absent lock each returned rc 1 with a named substrate-pin line. Six malformed loopback search bodies (missing rank, missing path, object, string array, null, non-finite rank) each returned adapter rc 3 with `recall: degraded: agent,company,project,team` and named per-scope degradation events. The requested G family is therefore covered, including the non-finite extension.

The direct hostile subset independently returned `9 passed in 3.39s`, covering malformed response degradation, both `allow_nan=False` sinks, unknown binding scopes, and a symlinked evidence root.

I did not independently reconstruct the separate predecessor M01–M28 driver. Its results are not used for this assessment; the 51 V/H/L/G/C cases below are the fresh mutations and hostile inputs I actually ran.

### C matrix — nine killed; C6 survives

| row | observed result |
|---|---|
| C1 leak check tautologied | rc 1, 3 failed / 167 passed |
| C2 denied event allowlist removed | rc 1, 5 failed / 165 passed |
| C3 posture loop emptied | rc 1, 4 failed / 166 passed |
| C4 nondeterminism check tautologied | rc 1, 1 failed / 169 passed |
| C5 wrong-scope write loop emptied | rc 1, 2 failed / 168 passed |
| C6 final equality changed to `row.get(f)` | **rc 0, 170 passed / survives** |
| C7 write-scope check tautologied | rc 1, 6 failed / 164 passed |
| C8 precedence reversed | rc 1, 6 failed / 164 passed |
| C9 tuple-shape gate tautologied | rc 1, 2 failed / 168 passed |
| C10 bindings `S_ISREG` guard removed | rc 1, the bounded directory member failed |

The historical red is real but is a different mutant: an archived scratch copy with the malformed-row guard reverted failed `test_a_malformed_table_row_can_never_authorize_a_null_tuple` (`1 failed in 0.57s`). It must not be used to claim the current C6 operator was killed.

## 2. FINDING F-27 — the “exact” manifest is only a direct-entry allowlist

**SOLID — blocking.** `proofs/S0-06/check_four_scope.py:116` is the `EXPECTED_FILES` declaration; `_check_expected_files` at `:490-501` computes only direct directory-entry names and rejects the extra-name set. It neither requires declared names to exist nor requires an allowed entry to be a regular file. The six allowed names the checker never reads are `precedence/events-1.jsonl`, `precedence/events-2.jsonl`, `write-scope/events-retry.jsonl`, `write-scope/events-write.jsonl`, `leak/events.jsonl`, and `write-scope/record.json`.

Expected: a closed manifest should require every producer-emitted evidence leaf to be present, regular, and semantically graded or intentionally removed from the collection contract.

Observed on repaired, independently passing scratch bundles:

- malformed content in allowed-but-unopened `precedence/events-1.jsonl`: rc 0, PASS;
- a directory named allowed `precedence/events-1.jsonl`: rc 0, PASS;
- a symlink named allowed `precedence/events-2.jsonl` pointing to `/dev/null`: rc 0, PASS;
- an unlisted `denied/opaque.bin`: rc 1, `leg: unexpected evidence file denied/opaque.bin`.

The loopback collector shape exercise, run solely to observe `collect_leg.sh` output, produced exactly 48 files, exactly matching `EXPECTED_FILES`. Conversely, `proofs/S0-06/fixtures/evidence-wrong-scope-write` has 43 expected leaves: it lacks all six names above, and its root-level `PROVENANCE.md` is ignored because the root itself is not closed. The sibling `evidence-leak` fixture is likewise a deliberately negative bundle, not a collector-shaped positive artifact. Thus neither negative fixture represents the full producer shape, while a hostile allowed node is accepted.

Minimal fix: make the checker compare each leg's complete relative-file set to the declared set; require every declared leaf through the existing `lstat`/`S_ISREG` discipline; and either grade the six event/record files or stop producing and listing them. Regenerate fixtures from the producer shape. Add red tests for an absent expected file, malicious content, directory, and symlink for every previously unopened allowed name, plus an unexpected root file.

Exact red controls: the three rc-0 inputs above must become rc 1 before this finding is closed.

## 3. FINDING F-28 — C6's reported mutation kill is false

**SOLID — blocking evidence defect.** The C6 mutator changes only `proofs/S0-06/adapter/factory_memory.py:160` from `row[f]` to `row.get(f)`. The preceding row validation at `:154-159` already rejects any row missing a field or carrying a non-string/empty field. Therefore that one-line C6 mutation is equivalent on the reachable domain.

Expected: the claimed complete C-matrix in `tasks/briefs/s0-06-support/M2-report.md:51` must be independently reproducible.

Observed: the reconstructed C6 scratch tree ran the complete S0-06 file at rc 0, `170 passed in 30.14s`; its named malformed-row test alone also passed. The historical failure only returns when the row-validity guard and the `row.get` equality are jointly reverted.

Minimal fix: correct the report to mark this C6 operator as an equivalent survivor, or define a compound mutant that deletes the row-validity guard and changes the equality. Re-run it and record the exact red test. Until then the mutation campaign cannot support its advertised all-killed claim.

## 4. FINDING F-29 — raw URL provenance does not bind the raw instrument to the captured instance

**SOLID — non-blocking hardening, but material to F-5.** `_url_names` at `check_four_scope.py:232-243` checks only whether workspace/project names occur in a parsed URL. `_require_raw_url` at `:259-263` never checks scheme, hostname, or port against the run's private instance.

Expected: the raw read that serves as the independent instrument must be bound to the recorded run endpoint.

Observed: changing a repaired passing bundle's `precedence/raw-agent.url` to a foreign host and port while retaining `workspace=factory` and `project=agent--a-alpha` returned rc 0, PASS. Changing the project name returned rc 1, as expected. A foreign endpoint can therefore supply a correctly labelled but unrelated raw response.

Minimal fix: record a non-secret run origin in `substrate.json`, then require raw URLs to use its scheme/netloc and the exact expected route/project. Add an rc-1 foreign-host/foreign-port test. This is a real origin-binding gap, not a failure of the current project-name check.

## 5. Socket witness, substrate, leak, and filesystem attacks

The socket witness uses `set(after) - set(before)` at `check_four_scope.py:285-297`, so duplicate sightings of one 4-tuple do not inflate the count. A synthetic duplicate passed, as it should. A foreign new 4-tuple on the instance port produces a conservative refusal rather than a false green; a precedence positive control with exactly one new connection produced rc 1, `denied: the socket witness never fired (1 new connections on the precedence leg)`. The `WITNESS_CONTROL_FLOOR=4` at `:77-80` is a liveness floor, not a request count. This witness cannot attribute a connection to the adapter, but foreign traffic fails closed.

The per-leg digest agreement and posture drift checks work: V1 and V2 were killed. A deliberately consistent alternate 64-hex digest across startup and every leg passed. This is the explicitly documented provenance-only design in `proofs/S0-06/check_four_scope.py:306`, not a binary identity pin. It must remain described as such; it cannot prove an arbitrary hand-authored bundle came from the pinned executable.

The leak oracle caught a forbidden synthetic canary placed in a record title, snippet, nested value, and key name, each with rc 1. The denied event allowlist caught a second `harmless_event` with rc 1 and the exact event name. The standalone FIFO probe used `timeout --foreground 6`, never pytest, and returned rc 1 without hanging: `leg: leak/raw-team.json missing or not a regular file`. A symlinked root and expected-file symlinks were separately exercised above.

## 6. F-25 remains a documented, unmitigated telemetry limit

**SOLID — non-blocking for this fixed-query proof, not suitable as a generic production telemetry path.** `factory_memory.py:296` emits the full request `path`; `_search` at `:301-309` puts the caller's query into that path. The H/L/G loopback run recorded `/api/v1/search?q=x...` events. The source comment at `:302-305` admits this limit, and `tests/test_s0_06_four_scope.py:1791-1798` tests the presence of that documentation rather than a scrubber.

Minimal fix before model- or user-derived recall queries share a sink: emit a route-only path or a deterministic query digest, never the query text. This is reported separately because the present PC proof only uses fixed literals.

## 7. PC runner static trace

`run_s0_06_legs.sh` starts the private process, seeds both agents, captures four legs, runs cleanup, then grades. The second seed resolves VERIFY-M1's F-1 static omission. `start_ai_memory.sh:29` contains `SRC="${S0_06_SRC:-$RUNDIR/src/ai-memory}"`, so its default stays inside the run directory. Its readiness loop exits on child death (`:106-112`) or timeout (`:120`). Its cleanup path begins with `stop_instance()` at `run_s0_06_legs.sh:35`, verifies `/proc/<pid>/exe` at `:41-45`, then `shred_credentials()` removes token and curl configuration at `:51-56`.

These are static observations only. I did not assert source-level ai-memory idempotency or exercise a real live leg, because doing so would violate the venue rule. The loopback collector exercise verifies producer filename shape, not ai-memory semantics.

## 8. 18-class re-scan

The final parser, malformed-response, NaN, denial-event, unknown-scope, root-symlink, command-inventory, and non-regular-file controls all have executable coverage in the runs above. The class-11/world-enumeration row is **not closed**: F-27 shows its fixed manifest is an optional direct-entry allowlist, not a complete regular-file schema. The class-18 malformed-row implementation is fail-closed, but its claimed C6 mutation evidence is not. Broad top-level adapter exceptions produce one stderr line and rc 70; a directory tuple-file probe returned rc 70 with exactly one stderr line and no stdout.

No new production-code field-equality branch without a fail-closed other arm was identified in the inspected checker, adapter, or three scripts. That is a static review result, not a substitute for the two blocking red controls.

## 9. Handoff and cheapest path

1. Fix F-27: enforce exact regular-file manifests, consume or delete the six unused files, regenerate the fixtures from a collector run shape, and add the hostile-node tests.
2. Fix F-28's evidence: mark C6 equivalent or construct the real compound regression mutant; do not retain a “10/10 killed” claim contradicted by rc 0.
3. Bind raw URL origin to the recorded private instance before treating raw output as an independent provenance instrument.
4. Hand the revised bytes to the sandbox-side adversarial verifier. Only after that, and after the owner's unresolved D-2/ADR decision, may the permitted PC live leg be considered. The coordinator owns the live-leg decision; the owner owns D-2 and ADR-0003 resolution.
