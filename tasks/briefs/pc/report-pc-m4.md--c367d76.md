REVIEW-PENDING: F-32 repaired and locally verified. Independent adversarial verification remains.

Report: /home/rocco/agent-factory/.lanes/pc-m4.md--c367d76/tree/tasks/briefs/s0-06-support/M4-report.md
Identity: 164 lines, SHA-256 05a0d9e59e6c742b46ee66fb5fb6b2302876c849064f1b1aa641197cbd959a79

# M4 — S0-06 round 4 build report (F-32)

PIN: `c367d76`
Role: code-implementer, PC venue (`tasks/briefs/pc/VENUE-MAP.md`).

## Outcome

**REVIEW-PENDING — GATE RECOMMENDATION: MERGE-READY for independent adversarial verification.** F-32 reproduced on the PIN and the implementation plus deterministic public-CLI controls are green locally. This single-model build lane cannot grade its own change; the coordinator owns the final decision and must send these bytes to the sandbox adversarial-verifier before acceptance or live capture.

## NOT done

- The live ai-memory leg was not run: the venue forbids it and the coordinator owns it.
- No EXPIRED→mint transition was run; nothing was minted.
- The S0-11 re-sign was not run; it is owner-owned.
- Independent adversarial verification has not run on this build lane.
- Close census found no leftover child server, pytest, or S0-06 helper. Only the lane wrapper and this Hermes process remained.
- No commit, add, stash, checkout, reset, push, bridge call, server restart, or credential read occurred.

## Contract

1. Each bindings row requires a present, list-valued, non-empty `scopes` field.
2. Every scope element is a string member of `SCOPE_ORDER`; duplicates are refused.
3. No two rows share the same `TUPLE_FIELDS` identity tuple.
4. The public recall/write CLI emits a named configuration error with a nonzero exit before authorization, and never emits `recall: complete`, for an invalid table.
5. A valid unique non-empty scope list authorizes exactly the same scopes as before.
6. Tuple values remain exact/verbatim; F-33 normalization is not added.

## FILE IDENTITY (final bytes)

- `proofs/S0-06/adapter/factory_memory.py` — 537 lines — git blob `2bee9eea7a84ae69026397104d59d4d792f26420`; SHA-256 `3cd91af9c02f244d5c61e359018c66fa8d77f950d0f10911d136c86dd5034034`.
- `tests/test_s0_06_four_scope.py` — 2157 lines — git blob `b1b3d19fab674c8e07474dc1204bd3711c3ca2e2`; SHA-256 `566d81103cc33fda71f0d777c499a6538cdf17f42b6e08a6bda677e029087d52`.
- `tasks/briefs/s0-06-support/M4-pack.md` — 234 lines — attached code-intel pack; git blob `a00b5510e87be41c5584a8c7600da5f1a63249a2`; SHA-256 `65247dd482dc3f469d4059c6a057b29cace03acaa943925d66a1e019841d4009`.
- `tasks/briefs/s0-06-support/M4-report.md` — this report; its self-referential hash is intentionally omitted. Final line count is recorded in the handoff.

## Premise and red-before proof

F-32 reproduced through the actual public `factory_memory.py recall` CLI on a `git archive c367d76` scratch copy. Missing `scopes` and `[]` returned rc 0 with `recall: complete` and `scopes_queried=[]`; `"agent"` returned rc 70 naming its characters as unknown scopes; integer `1` returned rc 70 with a bare `TypeError`; duplicate scopes were silently set-deduplicated; duplicate identity rows selected the first row and changed authorization with table order.

The final tests copied onto the unmodified PIN adapter produced `8 failed, 1 passed, 214 deselected in 2.27s`. All eight public-CLI negative rows failed; the valid-table positive row passed. This is red-before against the old production bytes without mutating the shared tree.

## Implementation

- `A:97-99` defines `_BindingsConfigurationError`, a `ValueError` subtype, so the CLI classifies table failures by type instead of by parsing messages.
- `A:120-163` validates `scopes` list type, non-empty content, string elements, unknown names, duplicate names, and duplicate identity tuples before returning the table. The identity key is constructed from `TUPLE_FIELDS` at `A:159` and checked before it enters the seen set at `A:160-162`.
- `A:516-533` maps named binding-configuration failures to rc 78 and one stderr line. Decision exits remain 0/1/3; unexpected failures remain rc 70.
- `T:579-607` copies the real stdlib-only adapter beside a scratch `bindings.json`. This preserves the production invariant that no caller-selectable `--bindings` flag exists while driving the real `load_bindings -> _bind -> recall/write` CLI path.
- `T:610-646` carries malformed-scope and duplicate-identity negative controls. They assert exact rc 78, exact named message, empty stdout, no result file, and absence of `recall: complete`.
- `T:649-657` is the positive control. It drives a valid agent+team table through the CLI and loopback recording server and asserts exactly those two queried projects.
- The existing absent-table public-CLI test now expects the same named configuration class at `T:1412-1426`; the unrelated unexpected tuple-file failure remains rc 70.

No fixture file changed. `_bind`, raw-origin, query scrub, file manifest, and telemetry behavior are untouched.

## Green-after evidence

Focused F-32 plus adjacent bindings/exit controls: `15 passed, 208 deselected in 1.98s`.

Full S0-06 file, direct final run: `223 passed in 30.32s`.

Machine-counted full S0-06 file:

```text
pytest-summary: 223 passed in 30.32s
```

Canonical static-copy gate, the exact brief command and final bytes:

```text
RESULT: rev=c367d76a1676 files=2 deleted=0 runs=2 tests=0b96e6ceb879 identical=yes rc=0 summary="291 passed in 46.23s 291 passed in 46.02s"
```

Static checks:

```text
pyflakes rc=0
git diff --check rc=0
```

## Named mutant table

| ID | hostile table / positive | observed final result | killer |
|---|---|---|---|
| M1 | `scopes` absent | KILLED, rc 78, `scopes must be a list` | `T:613`, `T:623-632` |
| M2 | `scopes="agent"` | KILLED, rc 78, `scopes must be a list` | `T:614`; `test_malformed_binding_scopes_fail_closed_through_the_public_cli` at `T:623-632` |
| M3 | `scopes=1` | KILLED, rc 78, `scopes must be a list` | `T:615`; `test_malformed_binding_scopes_fail_closed_through_the_public_cli` at `T:623-632` |
| M4 | `scopes=[]` | KILLED, rc 78, `scopes must be non-empty` | `T:616`; `test_malformed_binding_scopes_fail_closed_through_the_public_cli` at `T:623-632` |
| M4b | `scopes=[1]` | KILLED, rc 78, `scopes must contain only strings` | `T:617-618`; `test_malformed_binding_scopes_fail_closed_through_the_public_cli` at `T:623-632` |
| M5 | `scopes=["agent","agent"]` | KILLED, rc 78, `scopes has duplicates` | `T:619-632` |
| M6 | duplicate `TUPLE_FIELDS` rows | KILLED on recall and write, rc 78, exact tuple named | `T:635-646` |
| P1 | valid unique `["agent"]` | accepted at load; normal post-auth degraded result against closed port; queried scope is `agent` | scratch driver; stronger loopback positive at `T:649-657` |

Scratch driver final line:

```text
SUMMARY: mutants=6 killed=6 positive=1 failures=0
```

## Anti-pattern screens

Adapter:

```text
--- AP_SCREEN over 1 path(s): 3 hits over 1 files ---
AP-32: 2
    proofs/S0-06/adapter/factory_memory.py:261: return "observations/" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16] + ".md"
    proofs/S0-06/adapter/factory_memory.py:332: query_sha256_16 = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]
AF-AP-70: 1
    proofs/S0-06/adapter/factory_memory.py:491: # DOCUMENTED LIMIT (F-21): every READ path in this module is lstat+S_ISREG guarded, but these
```

Classification: both AP-32 rows are pre-existing deterministic SHA-256 path/query-digest derivations. AF-AP-70 is the pre-existing documented F-21 runner-owned output-sink limit. None is introduced by F-32.

Tests:

```text
--- TEST_SCREEN over 1 path(s): 13 hits over 1 files ---
AF-AP-80: 9
AF-AP-34: 2
AF-AP-35: 2
```

Classification: AF-AP-80 rows are source-contract assertions; AF-AP-34 is the banned-process-command scanner's own literal tuple; AF-AP-35 is deterministic synthetic honeytoken scrubbing. None is introduced by F-32.

## Code intelligence

Attached final pack: `tasks/briefs/s0-06-support/M4-pack.md`.

Pre-edit GitNexus resolved `load_bindings -> _bind -> recall/write` with exact LOW risk, but named its clone index as 233 commits stale. Ripwire independently found `_bind` as the production caller and recall/write upstream. `scripts/why.sh` tied `load_bindings` to the cb91edf/e776dd0 S0-06 history. Post-edit `detect-changes` reported 2 changed files, four affected Recall/Write→Authorize/Load_bindings flows, and medium risk. The pack records GitNexus/code-review-graph as unavailable in its own lane invocation and carries the ripwire results rather than implying a graph result it did not obtain.

## Self-attack

1. **The test could bypass the public CLI.** Ruled out: `_run_with_bindings` executes the copied real script with `recall` or `write` in a subprocess (`T:579-607`); red-before on PIN production bytes failed eight rows, and green-after runs the same tests.
2. **A configuration failure could still write a false-success artifact.** Ruled out: every negative asserts rc 78, empty stdout, no `recall: complete`, and no `--out` file (`T:628-632`, `T:642-646`).
3. **Duplicate tuples could remain order-dependent on one verb.** Ruled out locally: the duplicate control is parametrized over recall and write (`T:635-646`), and validation executes before either verb's authorization/network path. Independent verifier still must attack this claim.

## Evidence tiers

- **Verified:** PIN red-before behavior; final focused and full tests; exact two-run archive gate; pyflakes/diff checks; six hostile table classes and one positive control; final line identities; direct production caller path.
- **Inferred:** no external consumer requires configuration failures to remain rc 70. A literal sweep found the proof spec pins only decision rc 1 and `collect_leg.sh` relies on generic nonzero under `set -e`; the independent verifier should confirm outside this component.
- **Assumed:** none about live ai-memory semantics. No live substrate claim is made.

## Discrepancies

1. The first archive-gate attempt inherited `/usr/bin/python3`, which lacks `rfc3339-validator`, and produced `33 failed, 258 passed`. This was a venue-instrument PATH error, not a product failure. Exporting `PATH=/home/rocco/venv-agent-factory/bin:$PATH` made `python3` resolve to the mandated interpreter; the final canonical `-n 2` gate is green above.
2. The brief's pack command wrote `-s load_bindings authorize _bind`; this script requires repeated flags. The literal form treated `authorize` as a file and exited 64. `-s load_bindings -s authorize -s _bind` produced the attached pack.
3. An initial `ripwire_review.sh edit-check` call omitted the required symbol and returned usage rc 64. Re-running `ripwire_review.sh edit-check load_bindings` produced `status="unchanged" callers="10" incompatible="0"`; the final pack supplies per-symbol callers and GitNexus `detect-changes` supplies the post-edit blast radius.
4. Final report lint, worktree mode after one hint round: `report_lint: 29 refs — OK 24, NEAR 1, MISS 0, UNCHECKABLE 4, UNRESOLVED 0 (worktree)`. The brief-required PIN-mode invocation, which cannot resolve new worktree lines, produced `report_lint: 29 refs — OK 3, NEAR 1, MISS 21, UNCHECKABLE 4, UNRESOLVED 0 (at c367d76)`; those misses are the new F-32 code/tests and are resolved by the worktree-mode run.

## Recommendation

**MERGE-READY for independent adversarial verification.** This is a build-lane recommendation, not a final verdict. The verifier should especially attack exception classification, duplicate-tuple identity coverage, and whether any external CLI consumer hardcodes rc 70 for table failures.

## Reasoning record for coordinator commit

Rejected alternative: silently deduplicate scope lists or pick a deterministic duplicate tuple row. That preserves ambiguous policy and leaves authorization dependent on an arbitrary conflict rule. Ordering rationale: validate every row and table uniqueness in `load_bindings` before `authorize`, so recall and write share one fail-closed choke point. Primary source: the public CLI reproduction of F-32 at c367d76 plus `load_bindings -> _bind -> recall/write` from the adapter and two code-intel instruments. Logical hunks: (1) typed table/schema validation and rc 78 configuration surface; (2) public-CLI negative and positive controls.

## Retro

F-32 is the already-registered malformed-policy-table fail-open class from VERIFY-M3. No new bug class was found, so no new anti-pattern registry row or skill update is proposed. The only tooling wrinkles are recorded in DISCREPANCIES. Retro: nothing else to bake.

## Final mechanical records

- Worktree report lint after one bounded hint round: `report_lint: 29 refs — OK 24, NEAR 1, MISS 0, UNCHECKABLE 4, UNRESOLVED 0 (worktree)`.
- Brief-required PIN lint: `report_lint: 29 refs — OK 3, NEAR 1, MISS 21, UNCHECKABLE 4, UNRESOLVED 0 (at c367d76)`; all 21 misses target new worktree lines and therefore cannot exist at the PIN.
- Canonical archive gate: `RESULT: rev=c367d76a1676 files=2 deleted=0 runs=2 tests=0b96e6ceb879 identical=yes rc=0 summary="291 passed in 46.23s 291 passed in 46.02s"`.

🌱 graft saved at least ~43,636 tokens this turn.
