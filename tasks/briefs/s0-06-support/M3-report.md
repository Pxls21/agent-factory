# M3 report — S0-06 round 3

## Outcome

PROPOSAL ONLY — this PC build lane does not issue an acceptance verdict. The revised worktree requires sandbox-side adversarial verification.

## NOT done

- No real ai-memory checkout exists on this PC venue. I did not build, clone, seed, start, or contact ai-memory; no live leg, mint, or production-tree action occurred.
- The local loopback collector result cited by VERIFY-M2 remains a filename-shape instrument only, never substrate proof.
- D-2 / ADR-0003 and the owner’s D-3 naming decision remain outside this lane.

## Premise audit

Verified against `038bc9b` source bytes saved in `../scratch/old/`:

| finding | baseline reproduction | repaired bytes |
|---|---|---|
| F-27 manifest | baseline checker accepted a repaired bundle while an allowed event leaf was absent/malformed (`rc 0`, PASS) | exact recursive regular-file manifest `def _check_expected_files` at C:634; all declared leaves required and root is closed |
| F-28 C6 | baseline mutation ran the full current suite with `214 passed in 29.66s` | reported honestly as equivalent; C6′ removes the validation guard too and is killed below |
| F-29 raw origin | baseline checker accepted a right-named foreign-origin raw URL (`rc 0`, PASS) | recorded `origin` at S:155 is parsed in C:360-367; `def _require_raw_url` at C:267-284 requires raw scheme/netloc plus exact route/project |
| F-25 query telemetry | baseline `_search` emitted the full query-bearing URL path | A:306-311 emits route-only `/api/v1/search` plus a 16-hex SHA-256 query digest; `QUERY-CANARY-4e9f1c2a` test is T:1784-1800 |

## Delivered items

| item | final location | deterministic red control / exact killer line |
|---|---|---|
| exact 48-leaf manifest, closed root, regular leaves | C:124-145, C:634-685 | `EXPECTED_FILES` exact leaves are read by `def _check_expected_files`; absent, directory, symlink, unexpected-root, and nested-extra controls run |
| every formerly unopened event/record leaf graded | C:370-438 names `event_stream` | C:530-544 names `write_record`; C:441-465 raises `event_write`; C:482-483 and C:578-581 invoke `_grade_recall_events` |
| producer-shaped deterministic negative fixtures | F:179-199, F:463-476 | `write_events`, `build_all`, and `compare_dirs`; generator check `synthetic S0-06 fixtures match the generator` |
| C6 truth and C6′ | A:154-160; T:1603-1626 | validation `row.get(f)` guard; named C6′ `AssertionError` probe |
| raw URL origin bound | S:155; C:267-284; C:360-367 | literal `origin` is parsed and `raw_origin` rejects foreign host/port under tests T:1629-1644 |
| query text scrubbed | A:306-311; T:1784-1800 | `query_sha256_16` and `QUERY-CANARY-4e9f1c2a` prove route-only event telemetry |
| live-bundle root provenance leaf | R:85-89 | `PROVENANCE.md` is written by the runner and required by the root manifest |
| write event identity fully bound | A:404-405 emits `write_noop` | A:423-424 emits `write_committed`; C:441-465 raises `event_write` |

Control tests: T:1715-1727 contains `def test_write_events_are_bound_to_the_record_key_path_scope_and_project`; T:1728-1737 contains `field,value`; T:1740-1746 contains `events-retry.jsonl`.

## Manifest and leaf evidence

`EXPECTED_FILES` declares denied 4, precedence 15, write-scope 15, leak 13 leaves: 47 leg leaves. With root `substrate.json`, total evidence leaves are 48; `PROVENANCE.md` is the separately declared root provenance leaf.

The direct standalone probes ran outside pytest under `timeout --foreground 12`, with no watcher or process left running:

- 12/12 FIFO and symlink probes across all six formerly unopened leaves returned `rc=1` and `leg: <leaf> missing or not a regular file`.
- 4/4 manifest probes returned exact failures: absent leaf, directory leaf, unexpected root file, and nested unexpected file.
- 6/6 semantic probes returned exact failures: five malformed JSONL event leaves and an empty write-record body.

Every event file is consumed by an exact event sequence and semantic fields: recall streams require authorization scopes, request ordering/routes, query digest, and no degraded scopes; write streams require the full scope allowlist, active scope/project, path, idempotency key, and GET/POST route sequence. `record.json` is re-bound to the write key and the adapter defaults/body before those write streams grade.

## Mutation table

| family / mutant | result | exact killer / disposition |
|---|---|---|
| F-27 six leaves × absent | killed | `leg: <leaf> missing or not a regular file` |
| F-27 six leaves × directory | killed | `leg: <leaf> missing or not a regular file` |
| F-27 six leaves × symlink | killed standalone | `leg: <leaf> missing or not a regular file` |
| F-27 event leaves × malformed JSON | killed | `<leg>: <name> event stream invalid (JSONDecodeError)` |
| F-27 record body empty | killed | `write: record.json content/type ...` |
| F-27 unexpected root | killed | `leg: unexpected evidence file opaque-root.bin` |
| F-27 nested unexpected leaf | killed | `leg: unexpected evidence file precedence/events-1.jsonl.extra/opaque` |
| C6 `row[f] -> row.get(f)` | equivalent survivor | validation `row.get(f)` at A:154-160 makes it unreachable as a semantic distinction; full suite `214 passed in 29.66s` |
| C6′ validation removed + `row.get` | killed | `AssertionError`, `rc=1`, from the `test_c6_is_equivalent_but_the_compound_c6_prime_is_killed` probe at T:1603-1626 |
| F-29 foreign host | killed | `precedence: raw agent origin http://foreign.invalid:8765, expected http://127.0.0.1:8765` |
| F-29 foreign port | killed | `precedence: raw agent origin http://127.0.0.1:9999, expected http://127.0.0.1:8765` |
| F-29 right-name foreign route | killed | `precedence: raw agent was fetched from .../foreign/api/v1/search..., expected factory/agent--a-alpha` |
| F-25 query canary | killed | `QUERY-CANARY-4e9f1c2a` test at T:1784-1800 checks canary absence from every event and digest presence on all search events |
| write stream scope/project | killed | `field,value` parameterization is at T:1728-1732; T:1735-1736 checks `write-scope: events-write.jsonl write identity`. The retry scope mutation is `events-retry.jsonl` at T:1740-1746 |

The predecessor V1–V20, H1–H11, L1–L5, and C1–C10 claims are not re-claimed as this lane’s fresh mutation campaign. The final direct suite exercises their deterministic regressions; a sandbox verifier must independently re-run the requested external matrices before any admission decision.

## 18-class self-sweep

| class | count / method | result |
|---|---|---|
| 1 presence | 49-file fixtures, explicit manifest walk | closed: absence is named failure |
| 2 unsafe reads | all manifest leaves `lstat`/`S_ISREG`; 12 standalone FIFO/symlink controls | closed |
| 3 lossy output | checker returns one stdout reason line; direct suite exercises hostile shapes | closed in exercised paths |
| 4 negative acceptance | exact named rc/reason assertions, not `rc != 0` | closed for M3 controls |
| 5 substring/tail verdicts | full exact reason comparisons on M3 standalone probes | closed for M3 controls |
| 6 environment domains | no new environment domain introduced | inherited / not re-audited |
| 7 lossy decode | JSONL uses RFC-8259 parser and malformed JSONL controls | closed |
| 8 broad catches | M3 event/record parsing maps expected hostile shape errors to named reasons | closed in changed checker paths |
| 9 waits/polls | no new wait/poll path | not applicable to M3 edits |
| 10 skips/xfails | no skips or xfails added | empty |
| 11 world enumeration | recursive exact walk over every leg/root member | closed by manifest; unexpected root/nested probes run |
| 12 provenance/origin | scheme/netloc plus exact endpoint route/project | closed by host/port/route controls |
| 13 event names | exact ordered event sets | closed |
| 14 event semantic binding | scopes, request paths, digest, write identity | closed |
| 15 query telemetry | canary absence across emitted events | closed |
| 16 fixture drift | generator byte-comparison for both negative bundles | closed |
| 17 output-form values | record body/type and event sequence type checks | closed in M3 additions |
| 18 malformed authorization row | C6 equivalent noted; C6′ null-tuple mutation killed | honest equivalent survivor plus compound kill |

## Final byte identity

The static-copy gate’s final identity table included these primary bytes:

- `432454d86951e1b06ec1bae8e4dbbf147f4a664ccd76adaf707a6beb2f07c2c4` — `proofs/S0-06/check_four_scope.py`, 736 lines
- `8d0e75fce1fed079bd488609332228f3c9c2120af5566edfddd593429e64e6c6` — `proofs/S0-06/adapter/factory_memory.py`, 509 lines
- `19c63ca3bb366ae53a4bd0b38a3193db65edb8ae709d0462dec6e4601927bd55` — `proofs/S0-06/fixtures/build_synthetic_bundles.py`, 504 lines
- `2867d6df88073c77b8ec61ebaaffa6e96837a1ad9783c8c85a3577f0cac26400` — `tests/test_s0_06_four_scope.py`, 2076 lines
- `3955cc931a9f654ae16e3cfd84bb779a495502cd54107056a5305899817dc7a3` — `proofs/S0-06/tools/pc/start_ai_memory.sh`, 170 lines
- `b4579150336758e0c919d33ac4b275807356e75acdf7b53b307c6090202ac4d9` — `proofs/S0-06/tools/pc/run_s0_06_legs.sh`, 98 lines

## Final deterministic runs

- Direct venue suite: `214 passed in 29.87s`.
- Generator drift check: `synthetic S0-06 fixtures match the generator`.
- Static checks: Python compile, `bash -n` on all three PC scripts, pyflakes, and `git diff --check` returned rc 0.
- Report reference lint: `report_lint: 34 refs — OK 34, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.
- Process census: `process-census helper matches=0` for ai-memory / S0-06 helper probes.
- Static-copy gate:

    RESULT: rev=038bc9b4807b files=108 deleted=0 runs=2 identical=yes rc=0 summary="214 passed in 29.26s 214 passed in 29.43s"

The first gate construction was red before product execution because `lane_gate.sh -f` accepts files only; passing the fixture directory itself returned `lane file proofs/S0-06/fixtures absent in the working tree`. The final gate enumerated its 102 fixture files explicitly and ran the archive copy correctly.

## Screens and impact

`ap_screen.py` production result: 5 classified hits. AP-32: four required SHA-256 derivations, including the specified query digest and independent write-path derivation. AP-51: one `byte-identical` precedence documentation phrase. Test result: AF-AP-34: two banned-command scanner literals; AF-AP-35: two synthetic honeytoken scrubs. No screen hit is an unclassified production defect.

GitNexus impact before edits was available only from `/home/rocco/agent-factory` and stale by 18 commits: `_check_expected_files` mapped to `run`/`main`; `_search` mapped to `recall`/CLI. `detect-changes` after the batch reported 41 files / 36 symbols / 13 affected flows, with the expected checker and adapter flows. Its high aggregate risk is a stale-index conservative result, not a gate verdict.

## Discrepancies

- The brief says “full 48-leaf producer shape.” The collector/checker shape is 48 evidence leaves plus declared root `PROVENANCE.md`, making 49 regular files in each committed fixture. This report states both counts explicitly rather than hiding the provenance leaf.
- The direct M3 implementation initially omitted `scope` from generated/runtime `write_noop` and `write_committed` events. Tightening grading exposed it immediately as the first refusal. The adapter, generator, regenerated fixtures, and tests now bind those fields; final direct suite and static-copy gate passed.
- The named generator was initially untracked. It is present in the worktree and was included explicitly in the final static-copy gate; coordinator harvesting must retain it with the generated files.

## Self-attack

1. Fixture generator could mirror a collector mistake. Ruled down only for byte drift and declared shape, not real substrate semantics. A real ai-memory capture remains required.
2. Origin comparison can bind a URL to a recorded but forged synthetic origin. It closes F-29’s foreign-instance hole within a captured bundle, but does not turn a synthetic bundle into proof; substrate identity/provenance limits remain first-class.
3. Event sequence grading could become stale if adapter telemetry intentionally changes. It fails closed by exact sequence/path fields; any legitimate change must update the producer, checker, generator, and red controls together.

## Evidence tiers

- Verified: all commands and results in “Final deterministic runs,” standalone hostile probes, C6/C6′ probes, final source locations, fixture file counts, and no live process started by this lane.
- Inferred from predecessor evidence: the loopback collector’s measured 48 evidence-leaf shape; no ai-memory source derivation was re-verified on this venue.
- Assumed only for future work: a live runner will continue to emit the collector contract represented by the exact manifest. The required live leg is the independent way to test that assumption.

## Handoff

Sandbox adversarial verification must grade the exact worktree bytes, rerun the external mutation families, inspect the 49-file-versus-48-evidence-leaf accounting, and decide whether a permitted real PC leg is ready after D-2 / ADR-0003. No acceptance verdict is supplied here.
