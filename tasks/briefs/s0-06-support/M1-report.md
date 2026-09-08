# S0-06 lane M1 — the four-scope adapter over real ai-memory — LANE REPORT

**Outcome line:** `Built + sandbox-gated; NOT run against a real ai-memory instance.` The adapter,
its checker, the spec, two committed hostile evidence bundles and a PC runner are on disk and
green; the proof's own positive leg **defers** here by design (exit 2), so no artifact is minted
and no claim is made that the four scopes were demonstrated on a live substrate.

| | |
|---|---|
| brief | `tasks/briefs/stage0-parallel-support/material-S0-06.md` + the lane brief; PIN `773091c` |
| gate (PIN, final bytes) | `RESULT: rev=773091c1a196 files=56 runs=2 identical=yes rc=0 summary="95 passed in 15.28s 95 passed in 15.49s"` |
| gate (HEAD, final bytes) | `RESULT: rev=4b62a9d785aa files=56 runs=2 identical=yes rc=0 summary="95 passed in 14.94s 95 passed in 13.03s"` |
| mutants | 28 mutants, **19/19 REASONS rows reached, unreached: NONE** |
| defects found in my own work | **4** (2 production, 2 test-vacuity) + 1 provably-dead guard, all fixed this round, 2 with a red control |
| NOT done | read contract 5 (Fubuki bounds + token budget); the live PC leg; artifact mint; the whole tree EXECUTED (collection-only proven: `1688 tests collected`, no errors) |

---

## 1. WHAT WAS BUILT (verified)

| file | sha256 | lines |
|---|---|---|
| `proofs/S0-06/adapter/factory_memory.py` | `fd8f827eab4c20567a712fde3ad3f68ff2250a00a4e76415b21be07c17e7bc8d` | 451 |
| `proofs/S0-06/adapter/bindings.json` | `fe4f014a593fdb51b554a82167c35ab6ee737b7a934926cd962f67ede618d8eb` | 27 |
| `proofs/S0-06/check_four_scope.py` | `53554ee13c06d4f086abf3484bf616e034d37813258f0179fa0102520b4ca9a2` | 272 |
| `proofs/S0-06/spec.json` | `39505b32ceb1dca357ff475c2e4334829e31ccfd8caf32752e15ce1dda85bf19` | 44 |
| `proofs/S0-06/fixtures/honeytokens.json` | `16c76841929c35e94101ac90269a603d8c3fbd3015f3644859b5eae57add2a1d` | 6 |
| `proofs/S0-06/fixtures/records-precedence.json` | `3fcdf6776b3b1f219a47cdb6f3f052302d914a143c94c71e8774a35a8f3c7359` | 31 |
| `proofs/S0-06/tools/pc/start_ai_memory.sh` | `326ec8da92b45d2f96214691f01c9897b38cc187f6b853b7077b581bb95f2e26` | 136 |
| `proofs/S0-06/tools/pc/seed_scopes.py` | `95e17bca596eb86172b83e850b13709673589a0c7af7c5bfb8ee8188d5971d6c` | 115 |
| `proofs/S0-06/tools/pc/collect_leg.sh` | `e32a4d430fbae5affe4b1dfc179d345ef5c894a8e703778bbda0b0fb3e227141` | 132 |
| `proofs/S0-06/tools/pc/run_s0_06_legs.sh` | `b9516e30d796d7a2c93c48458bffbde9186bc60a17e28dd4d2af31b802efad4f` | 63 |
| `fixtures/s0-06/neg-unauthorized-tuple.json` | `a6012f29fcd48c68f6a0317e658ed505b51a850dc2173b8273d9f08e985ea7d2` | 6 |
| `tests/test_s0_06_four_scope.py` | `a20c319be3513df46c9204991f5a534e4387b9997025a22793af2c86b10a57f8` | 1012 |

Plus the two committed hostile bundles (44 files) under `proofs/S0-06/fixtures/evidence-leak/`
and `proofs/S0-06/fixtures/evidence-wrong-scope-write/`, each with a `PROVENANCE.md`. 56 lane
files total.

### 1.1 The seams, read from the pinned ai-memory source (not from the plan docs)

Every seam below was read at `/home/user/nerdherderdani/ai-memory`, `git rev-parse HEAD` =
`73715b6f1b2f0abb0a8b0ed47c1f69b1bd1b806e` — the `upstream.lock.yaml:33-38` pin, confirmed in
this session.

| seam | what the source says | file:line |
|---|---|---|
| **ai-memory has no per-project RBAC** | "ai-memory's wiki is single-tenant (no per-page RBAC; everyone with auth sees the same pages)"; "Attribution records *who* did a write; it does not gate *whether* they could do it." | `crates/ai-memory-core/src/actor.rs:2-3`, `:27-29` |
| auth rungs | anonymous / root bearer / `api_credentials` row / trusted proxy — a token authenticates a SERVER, never a project | `crates/ai-memory-core/src/actor.rs:11-24`; `crates/ai-memory-mcp/src/auth.rs:1-17` |
| **read surface** | `GET /api/v1/search` accepts `q`, `workspace`, `project`, `scope[]`, `limit` | `crates/ai-memory-web/src/routes/api.rs:41-45`, parser `:1074-1129` |
| scoped read is exactly one scope | `(Some(workspace), Some(project))` → `SearchMode::Scoped(vec![one])`; `search_scopes` loops only the scopes it was given — **no `_global` union** | `api.rs:352-360`, `:388-405` |
| hit shape | `ApiSearchHit` = exactly `{workspace, project, path, title, kind, snippet, rank}`, built by `enrich_hits` | `api.rs:1254-1263`, `:1009-1030` |
| page-list shape | `PageSummary` = exactly `{path, title, kind, tier, updated_at}` | `crates/ai-memory-store/src/reader.rs:1174-1185`; route `api.rs:33-36` |
| **write surface** | `POST /admin/write-page`, body `WritePageAdminRequest` `{workspace, project, path, body, title?, kind?, tier, tags, pinned}`, response `{page_id, path, checkpoint?}` | `crates/ai-memory-mcp/src/admin.rs:636`, `:6332-6358`, `:6366-6374` |
| …is the route ai-memory's own CLI uses | "`ai-memory write-page` — write or update a wiki page via the server. Sends a `POST /admin/write-page`" | `crates/ai-memory-cli/src/commands/write_page.rs:1-5`, `:61-74` |
| `_global` is a real reserved constant | `pub const GLOBAL_SCOPE_PROJECT: &str = "_global";` | `crates/ai-memory-core/src/lib.rs:41` |
| posture env nesting is real | `figment.merge(Env::prefixed("AI_MEMORY_").split("__"))` | `crates/ai-memory-cli/src/config.rs:937` |
| `require_approval` defaults **false** | field `:702`, default `:812` — the posture pin is load-bearing, not decorative | `crates/ai-memory-cli/src/config.rs:702`, `:812` |
| page-path validation | rejects empty / leading slash / drive prefix / backslash / dot segments | `crates/ai-memory-core/src/ids.rs:138-170`, portability `:130-135` |

### 1.2 The adapter (`proofs/S0-06/adapter/factory_memory.py`)

- `scopes_for` (`factory_memory.py:104`) is the mapping table whose first row is
  `(factory, _global)` and whose last is `(factory, agent--<agent-id>)`
  (`docs/03_INTEGRATION_CONTRACTS.md:78-81`), with the workspace fixed to `factory`.
- `authorize` (`factory_memory.py:123`) matches the caller's tuple **verbatim** against the committed
  `bindings.json`; the request body is never an authorization input, and the CLI has **no
  `--bindings` flag** (`test_cli_has_no_bindings_override_flag`, `tests/test_s0_06_four_scope.py:256`).
- `merge` (`factory_memory.py:170`) — Agent→Project→Team→Company, dedup on the page path (the part of ai-memory's
  `(workspace, project, path)` identity that is stable across scopes), shadowed scopes recorded,
  output sorted by `(precedence rank, stable id)`. **No clock, no randomness anywhere in the
  module** — asserted structurally by `test_the_adapter_uses_no_clock_and_no_randomness`, `tests/test_s0_06_four_scope.py:562`.
- `recall` (`factory_memory.py:289`) queries every AUTHORIZED scope and returns an explicit status; a failing scope
  yields `degraded` **naming the scope**, never a silent partial (`docs/04` §4).
- `write` (`factory_memory.py:328`) refuses any scope outside the binding's authorized set, refuses an incomplete
  record before any request, derives the page path from `(session, turn, event_id)`
  (`idempotency_path`, `factory_memory.py:201`), emits the durable **intent before** the side effect, and reports a
  retry as `write: idempotent no-op` without a POST.
- Public surface is exactly `recall` and `write` (`test_public_adapter_surface_is_recall_and_write_only`, `tests/test_s0_06_four_scope.py:356`); no module-level name matches
  delete/purge/promote/approve/forget/reset, and no admin mutation route other than
  `/admin/write-page` appears in the source (`test_no_module_level_mutation_entry_point_exists`, `tests/test_s0_06_four_scope.py:361`).

### 1.3 The checker (`proofs/S0-06/check_four_scope.py`)

Substrate identity first (`check_substrate`, `check_four_scope.py:128`): commit against `upstream.lock.yaml`
(`_pinned_commit`, `check_four_scope.py:121`), version `EXPECTED_VERSION` = `1.39.0` (`check_four_scope.py:39`), a 64-hex binary digest, and the four safe-posture variables
`AI_MEMORY_AUTO_IMPROVE__REQUIRE_APPROVAL=true` … (`docs/04_MEMORY_AND_GOVERNANCE.md:101-104`;
the same block at `.env.example:40-43`). The pinned SHA is **not** hardcoded in the checker:
`def test_the_pinned_commit_comes_from_upstream_lock_not_the_checker` (`tests/test_s0_06_four_scope.py:953`).
Then the four seed assertions,
each with **two instruments** — the adapter's own output AND a raw `/api/v1` read that bypasses
the adapter:

| seed `assertions` (`seeds/seed-stage0-v1.yaml:450-453`) | leg | adapter instrument | independent instrument |
|---|---|---|---|
| auth tuple validated outside model control | `denied/` | `recall.json` is the denial | `events.jsonl` carries **zero** `http_request` events |
| Agent→Project→Team→Company precedence, byte-identical twice | `precedence/` | `recall-1.json` vs `recall-2.json` byte compare; winner + shadowed scopes | four `raw-<scope>.json` searches must carry the same path with **four distinct titles** |
| writes land only in the authorized active scope | `write-scope/` | `write.json` / `retry.json` | four `raw-<scope>.json` page listings: present in `agent--A` exactly once, absent from the other three |
| a honeytoken never crosses a scope | `leak/` | `recall.json` text | `raw-team`/`raw-company` must CARRY their own token (else the absence is vacuous) |

`deferred:` (exit 2) when the evidence root is absent; `S_ISREG` on the `lstat` of every read
(`def _read_text` … `stat.S_ISREG`, `check_four_scope.py:92-101`).

**On the "no request was made" instrument.** ai-memory's `/admin/audit-log`
(`crates/ai-memory-mcp/src/admin.rs:617`, handler `:1033-1052`) lists **store audit events**
filtered by workspace/project/op — mutations, not `/api/v1` reads. There is therefore no
request-level access log artifact to grade, and the checker uses the adapter's own event stream,
hardened by the `denied: event stream unreadable` row so a corrupted stream cannot pass as "no
requests".

### 1.4 The PC runner (`proofs/S0-06/tools/pc/`) — **NOT run here**

`bash -n` clean on all three shell scripts (`test_pc_runner_scripts_are_syntactically_valid`, `tests/test_s0_06_four_scope.py:983`), pyflakes clean on `seed_scopes.py`.

- `start_ai_memory.sh` — port preflight that **refuses** rather than squatting (`:33-38`,
  `exit 65`, pinned by `test_pc_runner_refuses_a_bound_port`, `tests/test_s0_06_four_scope.py:1004`); idempotent clone + `--detach` to the pinned commit with a
  SHA equality check; `cargo +1.95.0 build --release -p ai-memory-cli --bin ai-memory`; a
  run-scoped token written 0600 and **never echoed**; the token reaches curl through a 0600
  `--config` file so it never enters argv (AF-AP-39); a fresh temp data dir; the four posture
  variables; a **failure-aware** readiness wait that exits on the child dying, not only on
  timeout (`:98-110`); a `--version` check against `1.39.0`; then `substrate.json`.
- `seed_scopes.py` — stages the four scopes through `POST /admin/write-page` and **imports
  nothing from the adapter**, so the seeding instrument is independent of the subject.
- `collect_leg.sh` — copies `substrate.json` **first**, then captures one leg; the raw
  instruments are plain `curl` reads of `/api/v1`.
- `run_s0_06_legs.sh` — start → seed → four legs → stop → grade. The stop path reads the pid from
  the pidfile this run wrote and confirms `/proc/$pid/exe` before signalling; **no `pkill`,
  `killall` or `pgrep` appears in any script's code** (comments stripped before the scan —
  `test_pc_runner_never_kills_by_name`, `tests/test_s0_06_four_scope.py:990`).

External commands the runner uses, enumerated: `bash, git, cargo, curl, python3, ss, sha256sum,
install, mkdir, mktemp, kill, readlink, cp, sed, awk, cat, chmod, seq, sleep, date, tr, cut`.

---

## 2. GATES (verbatim)

Static copy = `git archive <rev> | tar -x` + exactly the 56 lane working-tree files, run by
`scripts/lane_gate.sh`, every pytest invocation carrying an explicit `--basetemp` under the lane
scratchpad.

```
lane_gate: archive of 773091c1a196 at …/scratchpad/m1-lane/gate-pin2; 2026-09-08T03:12:27Z
== run 1/2 == 95 passed in 15.28s   (pytest-exit: 0)
== run 2/2 == 95 passed in 15.49s   (pytest-exit: 0)
RESULT: rev=773091c1a196 files=56 runs=2 identical=yes rc=0 summary="95 passed in 15.28s 95 passed in 15.49s"
```

```
lane_gate: archive of 4b62a9d785aa at …/scratchpad/m1-lane/gate-head2; 2026-09-08T03:13:11Z
== run 1/2 == 95 passed in 14.94s   (pytest-exit: 0)
== run 2/2 == 95 passed in 13.03s   (pytest-exit: 0)
RESULT: rev=4b62a9d785aa files=56 runs=2 identical=yes rc=0 summary="95 passed in 14.94s 95 passed in 13.03s"
```

Two revisions because **the brief's PIN is not on the branch** — see DISCREPANCY D-1. Counts are
pasted from `scripts/test_summary.sh`, never typed (AF-AP-37).

Other gates: `python3 -m pyflakes` rc 0 on all four Python files; `bash -n` rc 0 on all three
shell scripts; `report_lint: 56 refs — OK 56, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0` on this
report; `jsonschema.validate(spec, proofs/schemas/spec.schema.json)` passes
(`test_spec_validates_against_the_committed_schema`, `tests/test_s0_06_four_scope.py:913`).

---

## 3. THE MUTANT TABLE — every REASONS row, killer line pasted from the run

Driver: a lane scratch script that repairs the committed wrong-scope bundle into a PASSING bundle,
applies ONE mutation, and runs the checker. Baseline (no mutation):

```
PASS: S0-06 four-scope - 4/4 assertions, substrate ai-memory 1.39.0@73715b6f      exit 0
```

| # | mutant | REASONS row | killer line (verbatim) | exit |
|---|---|---|---|---|
| M01 | evidence root never captured | `deferred` | `deferred: S0-06 evidence not captured` | 2 |
| M02 | delete `precedence/recall-1.json` | `file` | `leg: precedence/recall-1.json missing or not a regular file` | 1 |
| M03 | `substrate.json` removed | `file` | `leg: substrate.json missing or not a regular file` | 1 |
| M04 | FIFO in place of `leak/raw-team.json` | `file` | `leg: leak/raw-team.json missing or not a regular file` | 1 |
| M05 | directory in place of `write-scope/raw-project.json` | `file` | `leg: write-scope/raw-project.json missing or not a regular file` | 1 |
| M06 | malformed JSON in `leak/honeytokens.json` | `file` | `leg: leak/honeytokens.json missing or not a regular file` | 1 |
| M07 | precedence recall status → degraded | `status` | `leg: precedence/recall-1.json status degraded, expected ok` | 1 |
| M08 | `write-scope/retry.json` status → degraded | `status` | `leg: write-scope/retry.json status degraded, expected ok` | 1 |
| M09 | substrate commit → 40 zeros | `substrate_pin` | `substrate: not the pinned ai-memory (commit=0000000000000000000000000000000000000000)` | 1 |
| M10 | substrate version → 1.38.0 | `substrate_pin` | `substrate: not the pinned ai-memory (version=1.38.0)` | 1 |
| M11 | `binary_sha256` → short hex | `substrate_pin` | `substrate: not the pinned ai-memory (binary_sha256=deadbeef)` | 1 |
| M12 | `require_approval` → false | `posture` | `substrate: unsafe posture AI_MEMORY_AUTO_IMPROVE__REQUIRE_APPROVAL=false` | 1 |
| M13 | maintenance key absent | `posture` | `substrate: unsafe posture AI_MEMORY_MAINTENANCE__ENABLED=<absent>` | 1 |
| M14 | `recall-2` confidence perturbed | `nondet` | `merge: nondeterministic` | 1 |
| M15 | collide id removed from `precedence/raw-team` | `collision` | `precedence: raw scopes carry 0 four-way collisions, expected 1` | 1 |
| M16 | `raw-team` title == `raw-agent` title | `variants` | `precedence: raw scopes do not carry four distinct variants` | 1 |
| M17 | merged winner scope → team | `winner` | `precedence: notes/deploy-window.md resolved to team, expected agent` | 1 |
| M18 | `shadowed_scopes` drops team | `shadow` | `precedence: notes/deploy-window.md provenance missing shadowed scope team` | 1 |
| M19 | written page also in `project--p-atlas` (**committed bundle**) | `write_found` | `write: record found in project` | 1 |
| M20 | written page removed from `write-scope/raw-agent` | `write_absent` | `write: record absent from agent` | 1 |
| M21 | written page duplicated in `write-scope/raw-agent` | `write_retry` | `write: idempotent retry produced 2 records` | 1 |
| M22 | team honeytoken in an agent+project recall (**committed bundle**) | `leak` | `leak: honeytoken HT-team-c52e6f04 surfaced from team` | 1 |
| M23 | team honeytoken scrubbed from its OWN raw read | `leak_vacuous` | `leak: honeytoken absent from its own scope` | 1 |
| M24 | authorized agent honeytoken scrubbed from the recall | `leak_empty` | `leak: authorized honeytoken HT-agent-3f1c9a2e absent from recall` | 1 |
| M25 | `denied/recall.json` status → ok | `denied_status` | `denied: leg did not record the tuple denial` | 1 |
| M26 | denial event replaced by an authorization event | `denied_status` | `denied: leg did not record the tuple denial` | 1 |
| M27 | an `http_request` event appended to the denied leg | `denied_request` | `denied: adapter recorded a request for the unauthorized tuple` | 1 |
| M28 | junk line in the denied event stream | `denied_stream` | `denied: event stream unreadable` | 1 |

```
REASONS rows: 19 | rows reached: 19 | unreached: NONE
```

M23 and M24 are the **oracle self-tests**: the leak assertion fails closed both when a forbidden
token is missing from its own scope (the absence would prove nothing) and when an authorized token
is missing from the recall (the recall was empty, so every absence is vacuous).

---

## 4. NEGATIVE CONTROLS

The seed's `negative_control` block requires 1 (`seeds/seed-stage0-v1.yaml:456-458`). This proof commits **3**, all in
`spec.json` and all reproduced by
`def test_spec_negative_legs_reproduce_their_pinned_reason_exactly` (`tests/test_s0_06_four_scope.py:933`), which runs each leg's real command and compares stdout's last line to the pinned
`failure_reason` **exactly** (AF-AP-29 — the canonical contract is as strong as the strongest test):

| # | command | pinned `failure_reason` | exit |
|---|---|---|---|
| 1 | `factory_memory.py recall --tuple-file fixtures/s0-06/neg-unauthorized-tuple.json --query x` | `denied: scope-tuple-unauthorized` | 1 |
| 2 | `check_four_scope.py proofs/S0-06/fixtures/evidence-leak` | `leak: honeytoken HT-team-c52e6f04 surfaced from team` | 1 |
| 3 | `check_four_scope.py proofs/S0-06/fixtures/evidence-wrong-scope-write` | `write: record found in project` | 1 |

Negative control 1 is the seed's own fixture at the seed's literal path. It is a **real-looking
tuple with exactly one wrong field**: `a-alpha` is a real agent, `svc-agent-runner` a real actor,
`p-atlas` a real project, and `t-platform` a real team — but `t-platform` is bound to `a-gamma`,
not to `a-alpha`
(`def test_seed_negative_fixture_is_a_real_looking_tuple_with_one_wrong_field`, `tests/test_s0_06_four_scope.py:266`). It makes **no network call**: against a closed loopback port the denial arrives in
bounded time and the event stream contains exactly one event, `scope_tuple_denied`, and no
`http_request` (`test_the_negative_control_denies_without_a_network_call`, `tests/test_s0_06_four_scope.py:570`).

The positive leg is `check_four_scope.py proofs/S0-06/evidence`. In this venue it **defers**
(exit 2) — the proof-runner reads exit 2 as Deferred and mints nothing
(`test_spec_positive_leg_defers_in_this_venue`, `tests/test_s0_06_four_scope.py:945`).

---

## 5. DEFECTS FOUND IN MY OWN WORK THIS ROUND (4 + 1 dead guard, all fixed)

| # | where | class | how it was found | red control |
|---|---|---|---|---|
| 1 | `check_four_scope.py` `Fail.__init__(self, key, **fields)` | emitted-but-unreachable check | the **posture mutant** crashed: `TypeError: Fail.__init__() got multiple values for argument 'key'` — the `posture` template's own field is named `key` and collided with the selector. The guard existed and could never report. | fixed by a positional-only parameter (`reason_key, /`); M12/M13 now produce their reasons |
| 2 | `factory_memory.py` `authorize` used `row.get(f)` | class-18 fail-open | the 18-class sweep: a bindings row missing a field returns `None` for it, so a presented tuple carrying JSON `null` **matched**. Reproduced: `assert {'actor': 'svc-agent-runner', 'agent': 'a-alpha', 'team': 't-core'} is None` — `authorize` **returned the malformed row** | `test_a_malformed_table_row_can_never_authorize_a_null_tuple` (`tests/test_s0_06_four_scope.py:243`) — run RED against the pre-fix code, then green |
| 3 | the checker's stdout read with `splitlines()[-1]` everywhere | class-3 | the sweep: a verdict preceded by a noise line would be invisible | `test_the_checker_prints_exactly_one_stdout_line` (`tests/test_s0_06_four_scope.py:653`) — run RED with an extra `print` in the checker: `assert 2 == 1 … ['note: checking bundle', 'PASS: S0-06 four-scope …']` |
| 4 | `test_every_reasons_row_is_asserted_by_a_mutant_in_this_module` positive control | self-satisfying control | running it: the planted template `"nothing in this module asserts {this} row"` sat inside the very assert it was testing and matched its own pattern, so the control reported `[]`. Fixed by joining the template at runtime so no literal exists. | the test failed until fixed |

Defect 1 was fail-**loud** (an uncaught exception exits 1 with no PASS line), so it could not have
minted a false green — but the row was unreachable in practice, which is the class the mutant
table exists to catch.

Also removed: a **provably dead** guard in `check_precedence` (`if ids else []` where `ids` is
built from the non-empty constant `SCOPE_ORDER`) — class 16, no behavioural test possible because
the branch cannot be taken.

---

## 6. 18-CLASS PREFLIGHT over MY OWN files (`material-S0-02.md` §7)

Files swept: `factory_memory.py`, `check_four_scope.py`, `seed_scopes.py`, the three PC shell
scripts, `test_s0_06_four_scope.py`.

| class | instances | verdict | the run / the guard |
|---|---|---|---|
| 1 presence-gated | 6: `if any(not isinstance(row.get(f), str)` (`factory_memory.py:139`), `row.get("scopes", [])` (`factory_memory.py:254`), `not record.get(k)` (`factory_memory.py:347`), `retry.get("page_path")` (`check_four_scope.py:192`), `recall.get("status")` (`check_four_scope.py:222`), `if not root.is_dir()` (`check_four_scope.py:242`) | SAFE | each is followed by a NAMED refusal; the deferral boundary `if not root.is_dir()` is pinned by M01 |
| 2 reads outside walk / no `S_ISREG` | 5 guarded read paths (`factory_memory.py:117`, `:393`, `:403`; `check_four_scope.py:96-100`; `seed_scopes.py:40`, `:86`) | SAFE | M04 (FIFO) and M05 (directory) prove the guard load-bearing and bounded-time |
| 3 stale `[-1]` / `tail -n 1` | 4, all reading checker/adapter stdout in tests | **DEFECT — FIXED** | closed by `test_the_checker_prints_exactly_one_stdout_line`; the adapter's single-line stdout was already pinned by `test_the_cli_denial_line_is_exactly_the_seed_reason`, `tests/test_s0_06_four_scope.py:590` |
| 4 negative acceptance | 22 | SAFE | every family now has a positive control on the SAME fixture: `server.calls == []` ↔ a recorded POST; `"team--t-core" not in …` ↔ a non-empty project set; token-absence ↔ `"agent--a-alpha" in text`; banned-name list ↔ the matcher firing on `delete_page`; unreached-rows ↔ a planted row. **4 of these controls were added this round** |
| 5 substring / tail anchors | 20 | SAFE | every outcome is classified by an EXACT `returncode` **and** an exact full-line equality; substrings only name reasons (`"unrecognized arguments"` rides on an asserted exit 2) |
| 6 env-domain fail-opens | 3, all PC-only (`run_s0_06_legs.sh:24-27` scope ids, `:30` `TMPDIR`, `start_ai_memory.sh` `S0_06_SRC`/`S0_06_TOOLCHAIN`) | DOCUMENTED-LIMIT | defaults are the committed table's own identities; **NOT executed here** — PC-only |
| 7 lossy decodes | 0 | — | **empty class**: every decode is strict `decode("utf-8")`; no `errors=` anywhere |
| 8 broad catches | 12 | SAFE | none is `except Exception`; each converts a named failure into a NAMED status/`Fail`. `except OSError` on a read becomes `leg: … missing or not a regular file` (M02/M03) |
| 9 waits / polls | 1 — `for _ in $(seq 1 120)` (`start_ai_memory.sh:98`) | DOCUMENTED-LIMIT | failure-aware: exits 68 the moment the child dies, 69 on timeout. **NOT executed here** — PC-only |
| 10 skips / xfails | 0 | — | **empty class**: no `skip`, `xfail` or `importorskip`; `jsonschema` and `yaml` are module-scope imports, matching CI's declared deps (`.github/workflows/stage0-ci.yml:19`) |
| 11 world-scoped enumerations | 2 (`glob("*.sh")` over the proof's own `tools/pc`) | SAFE | proof-owned directory; the glob makes a NEW script automatically subject to the `bash -n` and no-`pkill` gates rather than escaping them |
| 12 signal installs | 1 — `trap stop_instance EXIT` (`run_s0_06_legs.sh:46`) | SAFE | installed AFTER `RUNDIR` is assigned, and the handler returns early when the pidfile is absent, so it cannot trip `set -u` (AF-AP-58) |
| 13 `/proc/<pid>/exe` races | 1 (`run_s0_06_legs.sh:40`) | DOCUMENTED-LIMIT | a pid-reuse window exists between `readlink` and `kill`; the pid is our own child's from our own pidfile and the `exe` check is strictly safer than the name-based kill it replaces. **NOT executed here** |
| 14 mirrors | 2 | EQUIVALENT | `test_committed_bundle_recall_records_match_the_adapters_own_shape` calls `fm.merge` — a consistency check, **named as such**, not an oracle; the checker's precedence assertions rest on the raw reads instead. `test_merge_output_is_sorted_by_precedence_then_stable_id` asserts the property, not the implementation |
| 15 two counters, different populations | 0 | — | **empty class**: `len(negatives) == 3` and `len(set(tokens.values())) == 4` are same-population cross-checks |
| 16 provably redundant guards | 1 | **DEFECT — FIXED** | `if ids else []` in `check_precedence` was unreachable (`ids` derives from the constant `SCOPE_ORDER`); removed |
| 17 hardlink-clobbering writes | 0 | — | **empty class**: adapter writes go only to caller-named `--out`/`--events` paths inside a bundle the runner creates; tests write only under `tmp_path` |
| 18 other families | 1 | **DEFECT — FIXED** | the `authorize` null/missing-field fail-open (§5 row 2) |

**Empty classes (a result): 7, 10, 15, 17.** Three DEFECTs in my own files, all fixed this round.

### 6.1 Anti-pattern screen

`scripts/ap_screen.py proofs/S0-06 proofs/S0-06/adapter proofs/S0-06/tools/pc` → 2 hits;
`--tests tests/test_s0_06_four_scope.py` → 4 hits. All four classified, none a defect:

| hit | classification |
|---|---|
| AP-32 `hashlib.sha256` (`factory_memory.py:210`) | SAFE — the hashed form IS what the store holds: the same `idempotency_path` derivation runs on the write, on the existence pre-check and on the read-back, proven end-to-end by `test_a_retry_with_the_same_key_is_a_recorded_no_op` |
| AP-51 `byte-identical` (`check_four_scope.py:21`) | SAFE — the claim is exactly what the `nondet` row enforces (byte compare of `recall-1` vs `recall-2`), killed by M14. No dataclass/`asdict` sink exists in this proof |
| AF-AP-34 ×2 (`tests/test_s0_06_four_scope.py:995`) | SAFE — inverted match: the hit is the test that BANS `pkill`/`killall`/`pgrep` |
| AF-AP-35 ×2 (`tests/test_s0_06_four_scope.py:826, 833`) | SAFE — wrong-class match on the identifier `tokens`. These are **honeytokens**: synthetic canaries committed in `proofs/S0-06/fixtures/honeytokens.json` and quoted in `spec.json` by design. The one real secret in this proof (the bearer token) is never used to build a redaction; its absence is asserted, not filtered (`test_the_token_never_reaches_the_event_stream`, `tests/test_s0_06_four_scope.py:546`) |

---

## 7. DISCREPANCIES

### D-1 — the brief's PIN `773091c` is not on the branch

`git merge-base --is-ancestor 773091c… HEAD` → **rc 1**; `git branch -a --contains 773091c…` →
empty. PIN and HEAD share merge-base `8a978fe`; the PIN is `2026-09-08 00:47:44 +0000
"briefs: S0-03 lane O1 … + S0-06 lane M1 …"`, and the branch moved on (HEAD was `545a9ff`, then
`6bf4be3`, then `4b62a9d` during this lane). The object is still in the DB so `git archive` works.
`git diff --stat 773091c HEAD` touches nothing S0-06 depends on (no `proofs/schemas/`, no
`upstream.lock.yaml`, no conftest) — `scripts/lane_gate.sh` itself is the only shared tool that
moved. **I gated at both revisions**; the results agree. Coordinator action: confirm which
revision this lane should be committed onto.

### D-2 — TWO accepted ADRs numbered 0003, in direct conflict

Both files exist, both `Status: accepted`, both `Date: 2026-09-02`. Headers verbatim:

`# ADR 0003 — Four logical memory scopes over ai-memory` — `docs/adr/0003-four-logical-memory-scopes.md:1-19`
```
# ADR 0003 — Four logical memory scopes over ai-memory

- Status: accepted
- Date: 2026-09-02

## Context

Agent Factory requires Company, Team, Project, and Agent memory. ai-memory natively scopes records by `(workspace, project)` and reserves `_global`; per-user slots are injection constraints, not page-level RBAC. Dropping Team and Agent would discard intended behavior, while presenting path conventions as native isolation would be inaccurate.

## Decision

Retain all four logical scopes behind one first-party composite Hermes provider:

- Company: `(factory, _global)`
- Team: `(factory, team--<team-id>)`
- Project: `(factory, project--<project-id>)`
- Agent: `(factory, agent--<agent-id>)`

The adapter authenticates the actor/agent/team/project binding, reads with Agent→Project→Team→Company precedence, applies Fubuki bounds, and writes only to the authorized active scope. Promotion is a separate reviewed one-level workflow.
```

`# ADR 0003 — Two durable memory scopes in v1` — `docs/adr/0003-two-durable-memory-scopes.md:1-16`
```
# ADR 0003 — Two durable memory scopes in v1

- Status: accepted
- Date: 2026-09-02

## Context

The original Agent→Project→Team→Company hierarchy was mapped onto ai-memory as if those were native security scopes. Current ai-memory is fundamentally scoped by workspace and project; per-user slots affect injection but are not page RBAC.

## Decision

Use the active project plus the reserved global project as project and company memory. Hermes owns session/local state. Team and durable per-agent scopes are deferred. Company promotion is an explicit operator workflow.

## Consequences

The provider and authorization model remain understandable and testable. Some desired hierarchy is postponed, but no path-name convention is misrepresented as isolation.
```

**I did not resolve this.** I built the FOUR-scope ADR, because that is what the brief, the seed
(`assertions`, `seeds/seed-stage0-v1.yaml:450-453`), `## 4. Composite memory provider` (`docs/03_INTEGRATION_CONTRACTS.md:70-98`) and
`docs/01_ARCHITECTURE.md` §6 all specify. If the two-scope ADR is the live decision, this lane's
Team and Agent scopes are out of scope and `bindings.json` shrinks — a coordinator decision, not
mine. The number collision alone is a defect: two ADRs cannot share `0003`.

### D-3 — the plan's Company mapping is NOT ai-memory's reserved `_global`

`docs/03` maps Company to `(factory, _global)`. ai-memory's reserved global scope is resolved
**only inside the default workspace**: `lookup_global_scope` looks up
`DEFAULT_WORKSPACE_NAME` then `GLOBAL_SCOPE_PROJECT`
(`crates/ai-memory-store/src/scope.rs:254-271`), and `create_global_scope` creates
`("default", "_global")` (`:277-292`); `DEFAULT_WORKSPACE_NAME = "default"`
(`crates/ai-memory-core/src/lib.rs:28`). So `(factory, _global)` is an **ordinary project named
`_global` in the `factory` workspace**, not the reserved scope. Consequences, all verified in
source: the MCP `scope: "global"` argument cannot address it (and refuses to combine with
`workspace`/`project` — `crates/ai-memory-mcp/src/server.rs:6859-6866`); the default
`memory_query` union of the reserved scope does **not** union `(factory, _global)`; and nothing
refuses to create it (`create_explicit_scope` has no reserved-name check,
`scope.rs:231-244`). The adapter therefore addresses Company by explicit
`workspace=factory&project=_global` on both surfaces. **This is a plan-vs-substrate naming
collision worth an ADR line** — a future reader will assume `_global` means the reserved scope.

### D-4 — `ApiSearchHit` carries no timestamp, so read contract 4 needs a second call

`docs/03` §4 read contract 4 requires scope, stable ID, **timestamp**, confidence and provenance.
`ApiSearchHit` has exactly seven fields and no date (`api.rs:1254-1263`). The adapter therefore
joins the project's page listing (`PageSummary.updated_at`,
`crates/ai-memory-store/src/reader.rs:1184`) for the timestamp — two GETs per authorized scope.
`confidence` is the substrate's own FTS5 `rank`, carried verbatim. Proven by
`def test_the_record_timestamp_comes_from_the_page_listing` (`tests/test_s0_06_four_scope.py:511`).

### D-5 — the wave-0 spike records a FALSE fact about `rust-toolchain.toml`

`spikes/rust-ai-memory/result.json` `facts.rust_toolchain_file` says
`"ABSENT (no rust-toolchain.toml in repo)"`. At the pinned commit the file **is tracked**:
`git ls-files --error-unmatch rust-toolchain.toml` succeeds and
`git show 73715b6f…:rust-toolchain.toml` returns `[toolchain] channel = "1.95"`. This matters for
that spike's own open question: it recorded `pc_default_stable: rustc 1.93.0` and a successful
"default stable toolchain" build, but a tracked toolchain file pinning 1.95 means rustup would
have selected 1.95 inside the clone regardless — so the "default toolchain succeeded" run is very
likely 1.95, not 1.93. **I did not touch that artifact** (outside my file boundary); my runner
passes an explicit `+1.95.0` override, so the ambiguity does not affect this proof.

### D-6 — my own first draft carried two unverified environment claims

The checker's docstring initially asserted "the sandbox toolchain is 1.94.1 < the crate's MSRV
1.95" and cited a non-existent `seed S0-06 venue: pc`. Both were inferred, not probed. Corrected
after checking: `cargo 1.95.0 (f2d3ce0bd 2026-03-21)` resolves in this sandbox, and the seed says
`"(cargo build from the pinned commit; spike decides venue)"`
(`spike decides venue`, `seeds/seed-stage0-v1.yaml:449`) with the spike's `env_fingerprint` naming the PC. Recording
it because it is exactly the Phase-0 class (an environment claim read off memory rather than a
probe), caught in my own work.

---

## 8. NOT DONE — stated first-class

1. **The live PC leg was NOT run.** No ai-memory instance was started, no scope was seeded, no
   evidence bundle was captured, and `proofs/S0-06/evidence/` does not exist. Every claim about
   the four scopes on a real substrate is therefore **unproven**; what is proven is the adapter's
   behaviour against a local recording server and the checker's behaviour against synthetic
   bundles. Reason: the seed defers the venue to the wave-0 spike (`spike decides venue`, `seeds/seed-stage0-v1.yaml:449`), which ran on the PC; this
   sandbox has ~3 GB free on `/` against the spike's measured 618 MB + 306 MB of built binaries
   plus a full `target/`. **The toolchain is not the obstacle** (D-6). Next step: run
   `proofs/S0-06/tools/pc/run_s0_06_legs.sh` over the bridge, then
   `scripts/proof-runner run --proof S0-06 --venue pc-bridge`.
2. **No artifact minted.** `proofs/S0-06/result.json` does not exist and `proofs/ledger.json` was
   not touched. The spec's positive leg defers (exit 2) by design, so a mint attempt here would
   be refused rather than fabricated.
3. **Read contract 5 is NOT implemented** — `Apply Fubuki bounds and a hard token/character budget.` (`docs/03_INTEGRATION_CONTRACTS.md:89`).
   The adapter has no Fubuki dependency and no budget. That seam belongs with S0-07's Fubuki work and is outside this lane's file boundary.
4. **`memory_required` pre-dispatch health check** (read contract 6, second clause) is not
   implemented; the adapter returns `degraded` with the failing scopes named, which is the first
   clause only.
5. **The full `tests/` suite was NOT executed.** My attempt on the PIN static copy was killed by
   my own 25-minute cap (`timeout 1500` → SIGTERM, exit 143); `test_summary.sh` buffers its
   output into a variable and echoes at the end, so the killed run produced **zero counts** —
   there is nothing partial to report, and the 35 bytes it left are `Terminated` plus the exit
   line. What I ran instead on the SAME static copy carrying the final bytes, in 1.85 s:
   `python3 -m pytest tests/ --collect-only -q` → `1688 tests collected`, **no collection
   errors**; with my module moved aside, `1593 tests collected`; my module alone,
   `95 tests collected`; 1593 + 95 = 1688. That rules out the only realistic way purely-additive
   files break a tree — an import error, a duplicate module basename, or a fixture/name collision
   — and shows my files change no other module's collection. What remains **unmeasured** is the
   whole tree EXECUTED with the final bytes. Recommend the coordinator's PC suite
   (`scripts/pc_suite.sh`, 8 xdist workers) over the committed head.
6. **The ADR 0003 conflict is reported, not resolved** (D-2), and the `_global` naming collision
   (D-3) has no ADR line yet.
7. **Nothing was committed or pushed.** No outward-facing action was taken.

---

## 9. SELF-ATTACK — the three most likely ways this is wrong

**A. "The checker passes bundles that no real ai-memory could produce, so a hand-written bundle
could mint the proof."** Ruled out by construction and by run: `check_substrate` runs first and
requires the `upstream.lock.yaml` commit, version `1.39.0`, a 64-hex binary digest and the four
posture values — M09/M10/M11/M12/M13 all kill. The tests' recording server carries no
`substrate.json` at all, so a bundle captured against it cannot be graded. What this does **not**
rule out: someone who runs the real instance and then edits the bundle by hand. The checker's two
independent instruments per assertion raise the cost (a forger must edit the adapter output AND
the raw `/api/v1` reads consistently), but the honest limit is that **evidence integrity rests on
the runner, not on the checker** — and the runner has not been run.

**B. "The record shapes are invented, so the checker greens on fixtures that do not match what
ai-memory returns."** Ruled out at the key-set level: `SEARCH_HIT_KEYS` and `PAGE_SUMMARY_KEYS`
are transcribed from `ApiSearchHit` (`api.rs:1254-1263`) and `PageSummary`
(`reader.rs:1174-1185`), the committed bundles are asserted to carry **exactly** those key sets
(`test_committed_bundles_carry_the_real_ai_memory_record_shapes`, `tests/test_s0_06_four_scope.py:602`), and the recording server's own responses are asserted against the same sets
(`test_the_recording_server_answers_with_the_real_ai_memory_shapes`, `tests/test_s0_06_four_scope.py:493`) so the test double cannot drift either. Residual risk: field **semantics**. I
verified `rank` is an `f64` and `updated_at` an ISO-8601 string from the source, but I have never
seen a real response body — the values in the fixtures are synthetic and `PROVENANCE.md` says so
explicitly for each one.

**C. "The precedence result is an artifact of the fixture rather than of `merge`."** Ruled out
three ways: the collision id must appear in **all four** raw reads with **four distinct titles**
(M15, M16), so a merged agent-scoped record is a genuine choice among four candidates; `merge` is
proven order-independent on shuffled scope and record order (`test_merge_is_independent_of_input_order`, `tests/test_s0_06_four_scope.py:311`) and non-mutating
(`test_merge_does_not_mutate_its_input`, `tests/test_s0_06_four_scope.py:335`); and the shadowed-scope list is asserted against the exact expected triple
(M17, M18). Residual: the deterministic-merge property is proven over **synthetic** records; the
byte-identity of two real recalls is a checker row (`nondet`, M14) that has never run against a
live substrate.

---

## 10. HANDOFF — what the next lane needs

- Run order on the PC: `bash proofs/S0-06/tools/pc/run_s0_06_legs.sh` (optional args: bundle root,
  port; default port 48606, default bundle `proofs/S0-06/evidence`). It starts its own instance,
  seeds, captures all four legs, stops its own pid, and grades. Then mint with
  `python3 scripts/proof-runner run --proof S0-06 --venue pc-bridge --root .`.
- The run dir (`mktemp -d …/s0-06-run-XXXXXX`) is deliberately **kept** after the run: it holds
  the 0600 token and `serve.log`. Delete it when done. It must never be committed.
- The identities are in `proofs/S0-06/adapter/bindings.json`, not in the scripts: `a-alpha`
  (all four scopes), `a-beta` (agent+project — the leak leg's binding), `a-gamma` (the team the
  negative fixture borrows).
- If the coordinator settles D-2 toward the **two-scope** ADR, this lane's Team and Agent scopes
  and two of the three bindings rows come out, and the `leak` leg loses its point — stop before
  running the PC leg in that case.
