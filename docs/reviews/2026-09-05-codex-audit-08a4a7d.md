<!-- Provenance: the owner's external audit (Codex) of branch commit 08a4a7d, delivered 2026-09-05 as an upload; body verbatim below. Filed by the coordinator; the responses live in the S0-01 repair rounds (todo/BUILD-TASKLIST.md, proofs/S0-01/GROUNDING.md). -->

# Agent Factory branch audit — 5 September 2026

**Decision: the repairs are substantial, but S0-01 is not ready for acceptance or a replacement proof artifact.** The published checkpoint is correctly marked unfinished. Several invalid evidence bundles still pass the complete checker, and two capture producers can report success without satisfying their consumers.

Audited branch: `Pxls21/agent-factory`, `claude/soundbox-kit-migration-iz1jwf`, at [08a4a7dbf90786defd2d79923f34c02046f340ba](https://github.com/Pxls21/agent-factory/commit/08a4a7dbf90786defd2d79923f34c02046f340ba). Fresh branch-ref checks confirmed this SHA at both the start and end of this review. The scope includes the supplied summary, the repairs since `0dbea1e`, the checkpoint-three changes since `ef441ef`, relevant tests, canonical seed, integration contracts, runner, schema/registry/ledger, and GitHub Actions. All 20 files changed since `ef441ef` matched their immutable GitHub blob identities in the isolated review copy, including after testing.

The uncommitted round-four edits and the PC's current services were not inspected or changed. Reported PC dry runs, hidden verifier reports, and mutation-kill totals remain unverified unless specifically reproduced below. No implementation checkout, remote repository, workflow, or PC service was modified. Tests and mutations ran in isolated scratch copies.

**Verification results.**

| Check | Result | Interpretation |
|---|---|---|
| [GitHub Actions run #66](https://github.com/Pxls21/agent-factory/actions/runs/33991085457), created 5 September at 20:46:13 UTC | 580 passed, 1 failed, 14 skipped | Published branch is red. The failed test is the one acknowledged in the checkpoint. |
| Complete local `pytest tests/` | 576 passed, 5 failed, 14 skipped in 174.54 seconds | Same S0-01 failure, plus four existing S0-11 fixtures that require `/tmp`, which does not exist in this venue. Those four are not classified as new branch regressions. |
| Broad Python lint over S0-01, scripts, tests and the edited hook | Exit 0 | No reported pyflakes errors. |
| Ledger generation followed by committed-file comparison | Exit 0; no difference | The former silent ledger-drift gap is materially repaired. |
| Canonical ledger integrity | Exit 0 | S0-01 `ABSENT`; execution artifacts 1/7; conformance decisions 3/3. |
| Proof-status validator | Exit 0 | S0-01 remains `REVIEW-PENDING`. |
| Correct canonical S0-01 runner invocation | Exit 2, explicit deferral; no result produced | Missing v2 capture is not being presented as successful execution. |
| Baseline archive and all three section hashes | Re-derived and matched pins | 11,340 Hermes entries, 11,612 Buzz entries, 269 ACP entries. This verifies the committed manifest bytes, subject to the coverage defect below. |

The CI test fails because `test_cli_pass_path_fails_on_golden_pin` expects `failure_reason: golden: golden not pinned`, but the actual CLI stops earlier at `failure_reason: run-1: env BUZZ_ACP_AGENT_OWNER mismatch`. Ledger, harness and planning jobs pass. Stage 1 remains intentionally failing and is configured with `continue-on-error`; that is separate from the unexpected test-job failure. [Workflow](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/.github/workflows/stage0-ci.yml), [failing test](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/tests/test_s0_01_check_acp_conformance.py#L399).

**What is demonstrably better.** The checker now consumes signed relay events, checks identities and thread references, enforces an interleaved timeline and cancel ordering, re-derives committed manifest bodies, and compares exact `900s/3600s` configuration values. The BIP-340 vector tests and the corresponding checker tests pass. The backend rejects the originally reported group/other-readable token file and nonempty record directory by default. The test-summary script, pre-mint rules and CI ledger comparison now exist. These are useful implementation and test improvements; they do not independently reproduce a new PC run. [Checker](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/check_acp_conformance.py), [pins](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/pins.py), [test summary](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/scripts/test_summary.sh).

**How the adversarial checks were run.** Full-bundle mutations used the repository's own passing synthetic five-leg fixture and its standard test overrides for fixture location and the golden digest. Each baseline passed before mutation. These tests establish what the checker accepts; they do not assert that the real PC produced the altered records. The production golden pin remains `None`, and no replacement `result.json` exists.

**P1 — Negative execution can be absent or explicitly failed while the proof checker passes.**

Replacing the negative initialize response with an agent-to-client request carrying the same ID was accepted:

```json
{"jsonrpc":"2.0","id":0,"method":"session/request_permission","params":{}}
```

The complete checker returned exit 0 with `PASS: S0-01 acp-conformance — 16 checks executed over 5 legs` and `negative: observed: none: no parseable response`. The standalone negative command also returned its expected exit 1 and exact seed reason despite reporting no parseable response.

A separate complete-bundle mutant set `delivered=false`, `probe_error="BrokenPipeError: request not delivered"`, `agent_exit_code=-9`, `agent_argv=["/usr/bin/true"]`, and `agent_child_pid=-1`. Retaining the four expected identity strings was enough for another PASS.

Both consumers match an ID without requiring a valid response envelope or a successful probe. The expected failure reason is derived from the local malformed fixture, so it does not demonstrate rejection by the pinned runtime. Tests check missing/wrong IDs but omit a same-ID agent request and explicit failed-delivery evidence. **Repair:** share a strict negative-capture validator between both consumers; require delivery, valid request/response shape, no probe failure, executed argv/probe identity, and the documented runtime rejection. [Negative consumer](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/check_acp_conformance.py#L1020), [standalone consumer](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/check_initialize.py#L191), [spec](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/spec.json).

**P1 — Source manifests omit symlinks that can change executed code.**

Using the actual manifest producer, retargeting `active.py` from `version_a.py` to `version_b.py` changed executed output from `VERSION_A` to `VERSION_B`. Both manifest commands exited 0 and produced byte-identical compressed manifests. Neither manifest contained `active.py`.

The producer uses `find … -type f`, so committing and re-deriving its output does not make it a complete source-tree manifest. Tests protect digest agreement and regular-file content, not the omitted filesystem state. **Repair:** define and hash entry types, symlink targets, relevant modes and regular-file contents; reject or explicitly account for links outside the pinned tree. Add a symlink-retarget control through the actual producer and consumer. [Manifest producer](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/tools/pc/pc_manifest.sh#L10).

**P1 — Process cleanup and runtime identity are not bound completely.**

The full checker accepted a cancel capture whose raw process records explicitly showed a child surviving teardown:

```text
before teardown: 54321 12346 /usr/bin/sleep 60
after teardown:  54321 1     /usr/bin/sleep 60
```

It also accepted `tee_pid=77777` and `agent_child_pid=88888` in runtime identity while the process scan continued to describe a different process tree. The producer filters `ps` output by tool-name substrings; the consumer rejects surviving named tools but ignores a previously observed generic descendant, and does not join the identity PIDs to the scan PIDs. Existing tests predominantly inject named Buzz/tee/Hermes processes.

**Repair:** preserve a complete observation of owned descendants, bind PID and process birth identity across artifacts, and verify that every owned descendant is absent after teardown, including after reparenting. Keep actual cleanup restricted to verified owned processes. The synthetic mutation proves an acceptance gap, not that an orphan currently exists on the PC. [Process producer](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/tools/pc/pc_post.sh#L9), [consumer](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/check_acp_conformance.py#L916), [seed requirement](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/seeds/seed-stage0-v1.yaml#L354).

**P1 — A malformed POST bypasses credential redaction.**

A local backend test placed a dummy bearer token in the request URL and an ordinary header. With valid JSON, the backend returned 400 without persisting the token. Changing only the body to malformed JSON still returned 400 but wrote the token into the request record.

The JSON-error handler calls `state.record()` before the credential-location check. Rejection status therefore does not prove that the secret stayed out of evidence. **Repair:** put secret filtering at the common recording boundary, including exceptions; add malformed-body controls with the sentinel in URL, headers and body. Only a dummy credential was used. [Backend](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/tools/scripted_backend.py#L210).

**P1 — Two sequential users satisfy a concurrent-user requirement.**

The existing passing synthetic bundle's prompt windows are `09:00:00.500–09:00:01.100` and `09:00:01.400–09:00:02.000`: they do not overlap. The entire checker accepts them. Distinct signed identities and distinct sessions are valuable, but they do not exercise concurrency or catch state collisions under overlap.

**Repair:** drive and assert an overlapping two-user interval with session-specific chunks and terminals. The motivating seed explicitly requires two concurrent fixture users; the checker and its positive fixture should enforce that assertion. [Two-user checker](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/check_acp_conformance.py#L722), [seed](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/seeds/seed-stage0-v1.yaml#L356).

**P1 — Conflicting terminal responses are silently collapsed.**

Adding an error response immediately before the successful `end_turn` response, with the same request ID and a consistent timeline/directional split, still yields full PASS. Response dictionaries overwrite the earlier response with the later one. Request-method counts and response-ID membership checks do not reject duplicate or contradictory responses.

**Repair:** validate request IDs and response cardinality before building lookup maps; require exactly one terminal response per request and reject conflicting result/error envelopes. [Prompt checks](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/check_acp_conformance.py#L550).

**P2 — The tee can lose output and still exit successfully.**

With a fake local agent emitting 1,000 JSON lines and a client delaying reads for 6.3 seconds, the tee exits 0 before all output is forwarded. A separate injected recording failure also produced ENOSPC, zero forwarded bytes, and exit 0.

The tee joins its output worker for five seconds, then calls `os._exit(child_rc)` even if that worker remains blocked. Worker exceptions likewise do not determine the exit status. The timeout test deliberately expects success but does not assert complete drainage. **Repair:** distinguish clean drain from timeout/write failure and surface an unsuccessful capture status. This is a producer-fidelity failure; the reproduction does not establish that the downstream checker accepts the truncated bundle. [Tee completion](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/tools/frame_tee.py#L220), [timeout test](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/tests/test_s0_01_frame_tee.py#L378).

**P2 — The executed-check guard cannot detect an omitted leg.**

A control first changed run-2's `HERMES_HOME`, which correctly failed. Omitting only the run-2 environment-check invocation then restored PASS and the same “16 checks executed over 5 legs” message. The guard records function and leg but removes leg information and deduplicates before comparing.

**Repair:** compare the complete ordered `(check, leg)` sequence or explicit required matrix. This is a mutation of the guard's coverage claim, not a claim that the shipped code currently omits that call. [Dispatcher](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/check_acp_conformance.py#L149), [comparison](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/check_acp_conformance.py#L1280).

**Previously acknowledged gaps still present.** The probe reads `/proc/<pid>/exe` after `wait()` reaps the child, leaving required interpreter fields null. The alleged canonical-runner negative test omits the required `run` verb and `--root`; it accepts argparse's exit 2 as evidence of deferral. Even after fixing its invocation, it must demonstrate that the intended negative leg is actually reached, rather than stopping at the positive leg's current deferral. The supplied summary already lists these and the red CLI test as unfinished; this audit does not classify them as undisclosed completion claims. [Probe](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/proofs/S0-01/tools/acp_probe.py#L215), [runner test](https://github.com/Pxls21/agent-factory/blob/08a4a7dbf90786defd2d79923f34c02046f340ba/tests/test_s0_01_spec_runner.py#L53).

**Recurring signatures and the best prevention targets.** Counts below are conservative observed examples, not one incident per mutation and not new closure cycles for this honestly unfinished checkpoint.

| Signature and supported recurrence | Concrete evidence | Impact and why checks miss it | Best target |
|---|---|---|---|
| Incomplete evidence treated as complete provenance; at least 2 implementations | S0-11 `1720044`, `scripts/validate-ledger` omitted tooling; S0-01 `08a4a7d`, `pc_manifest.sh` omits symlinks | Hash agreement can coexist with a changed execution boundary; tests mutate only included inputs | AF-AP-31 and existing `anti-hollow-green`: enumerate the complete dependency/entry set and test omitted classes |
| A proxy substitutes for the required negative mechanism; 2 S0-01 generations | `91991f6` schema-only negative; `08a4a7d` `check_negative`/`check_initialize` accept a non-response or failed delivery | A local classification can stand in for runtime rejection; tests model expected IDs rather than valid transport outcomes | AF-AP-30/31 and existing `anti-hollow-green`: one strict shared producer-to-consumer contract |
| Cleanup evidence covers selected examples, not all owned processes; 2 S0-01 generations | `91991f6` authored cleanup facts; `08a4a7d` `pc_post.sh`/`check_process_evidence` filter named processes | Generic or reparented children escape the assertion; fixtures inject only named tools | AF-AP-31/34 and existing `anti-hollow-green`: full owned-descendant observations and lifecycle mutants |
| Producer tests assert a weaker condition than the consumer; 2 concrete tools | `167e063` `acp_probe.py` yields null interpreter identity; `08a4a7d` `frame_tee.py` can exit 0 before output drains | Tooling cannot reliably generate admissible evidence; tests check key presence or bounded exit, not usable values and complete output | Existing `anti-hollow-green`: real producer output must satisfy the complete consumer predicate |
| Presence/count substitutes for exact contract semantics; at least 2 current manifestations | `08a4a7d` `check_two_users` and executed-check sequence guard | Two sessions can be serial, and a check can be missing from one leg; fixtures model counts rather than required relationships | AF-AP-25 and existing `anti-hollow-green`: overlap and full `(check, leg)` mutations |

No new skill is needed. The existing rules have the right intent; the missing piece is enforcement at these specific boundaries.

**Repair order before recapture.** First close negative-response/delivery validation, credential recording, complete manifests, process identity/cleanup, concurrency and terminal cardinality. Then fix probe identity timing, tee completion and the two misleading harness checks. Require a green full suite, broad lint, canonical-runner tests that actually reach every leg, and ledger comparison. Capture with the final committed tools, pin the new golden, rerun the adverse controls against the actual bundle, run the canonical runner and ledger validation, and submit that concrete artifact for review.

The current 1/7 ledger figure measures artifacts, not independently certified execution or whole-project readiness. The withdrawn S0-01 artifact, unpinned golden and explicit review-pending status are the correct state while these repairs remain open.
