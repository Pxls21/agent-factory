**VERIFIED (PC, adversarial-verifier, PIN `e776dd0`) → GATE RECOMMENDATION: NOT-READY — F-32 is the sole qualifying blocker.** No live ai-memory leg was reproduced (the venue forbids it); every other claim is reproduced on the PIN's bytes. The full report is saved at `/home/rocco/agent-factory/.lanes/pc-verify-m3.md--e776dd0/tree/tasks/briefs/s0-06-support/VERIFY-M3-report.md` (241 lines, 41,451 bytes) and synced to the lane's `report-draft.md`. Returned whole below.

---

# VERIFY-M3 — adversarial grade of S0-06 round 3 (lane M3)

PIN: `e776dd0`
Role: adversarial-verifier, PC venue (`tasks/briefs/pc/VENUE-MAP.md`), brief `tasks/briefs/s0-06-support/VERIFY-M3-brief.md`.

## Outcome

**Gate recommendation: NOT-READY — F-32 is a qualifying blocker.** This recommendation is based on the reproduced local checker/adapter paths and loopback records; it deliberately does not claim the prohibited live ai-memory leg was reproduced. The coordinator owns the final decision.

## FILE IDENTITY (scratch archive of e776dd0, `git archive | tar -x` into the lane's scratch dir)

| file | sha256 (measured) | brief claim | lines |
|---|---|---|---|
| proofs/S0-06/check_four_scope.py | `432454d86951e1b06ec1bae8e4dbbf147f4a664ccd76adaf707a6beb2f07c2c4` | `432454d8…` | 736 = 736 |
| proofs/S0-06/adapter/factory_memory.py | `8d0e75fce1fed079bd488609332228f3c9c2120af5566edfddd593429e64e6c6` | `8d0e75fc…` | 509 = 509 |
| proofs/S0-06/fixtures/build_synthetic_bundles.py | `19c63ca3bb366ae53a4bd0b38a3193db65edb8ae709d0462dec6e4601927bd55` | `19c63ca3…` | 504 = 504 |
| tests/test_s0_06_four_scope.py | `2867d6df88073c77b8ec61ebaaffa6e96837a1ad9783c8c85a3577f0cac26400` | `2867d6df…` | 2076 = 2076 |
| proofs/S0-06/tools/pc/start_ai_memory.sh | `3955cc931a9f654ae16e3cfd84bb779a495502cd54107056a5305899817dc7a3` | `3955cc93…` | 170 = 170 |
| proofs/S0-06/tools/pc/run_s0_06_legs.sh | `b4579150336758e0c919d33ac4b275807356e75acdf7b53b307c6090202ac4d9` | `b4579150…` | 98 = 98 |

All six bytes verified by `sha256sum` on the scratch archive; no discrepancy.

## Item 0 — mechanical gates (reproduced on the PIN's bytes)

- `report_lint.py tasks/briefs/s0-06-support/M3-report.md --rev e776dd0 --map C=… --map A=… --map F=… --map T=… --map S=… --map R=…` → `report_lint: 36 refs — OK 36, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (at e776dd0)`, rc 0. The coordinator's `36 refs — OK 36` reproduces exactly. (Note: the M3 report's own final-block claim at its line 111 says `34 refs … (worktree)` — the worktree state had 34; at the PIN the count is 36. Both are true of their own tree state; not a finding.)
- `ap_screen.py` over checker + adapter + generator: **8 hits** — AP-32 ×5 (`C:410` `digest`, `C:525` `want`, `A:237` `return`, `A:308` `query_sha256_16`, `F:144` `query_sha256_16`), AF-AP-40 ×1 (F:450 `if root.exists():`), AF-AP-70 ×1 (A:467, the `# DOCUMENTED LIMIT (F-21)` comment line inside `_main`), AP-51 ×1 (C:21 docstring phrase `byte-identical`). Matches the brief's stated screen (brief said AF-AP-70 at A:465-471 `_main`; the hit is the comment at A:467 in that range — same site). `--tests` over the test: **4 hits** — AF-AP-34 ×2 (T:1068 banned-command literals `("pkill", "killall", "pgrep")` — the scanner's own literals, classified as the test scanning for banned commands, not executing them; verified by read), AF-AP-35 ×2 (T:899 `path.write_text`, T:906 `path.write_text` fixture scrubbing, the documented honeytoken-scrub design, not live-token use). **Classification by run:** none is a live defect; AF-AP-70 is the only REAL-class row and is the documented limit F-21 — graded in item 7.
- `pyflakes` over all four Python files: rc 0, no output. `bash -n` on both PC scripts: pass.
- Generator drift check: `python3 proofs/S0-06/fixtures/build_synthetic_bundles.py --check` → `synthetic S0-06 fixtures match the generator`, rc 0.
- Direct suite, venue exports + absolute `--basetemp`: **`214 passed in 29.84s`** (single process, no xdist). I AGREE with the lane's `214 passed in 29.87s` and the coordinator's `214 passed in 7.41s` (8 workers) — same bytes, same count.

## Item 1 — F-27 exact manifest and every leaf (reproduced)

**Production-path reconstruction.** The live runner invokes `collect_leg.sh` once for each leg (`R@e776dd0:81-84`). The pinned collector creates its leg directory, copies `substrate.json`, writes each leg's `substrate-observed.json`, then invokes the adapter CLI with runner-derived `--out` and `--events` paths and writes the raw reads/`raw-*.url` witnesses. Static producer shape is 47 leg leaves plus root `substrate.json` and root `PROVENANCE.md`: **49 regular files total**, of which the brief's "48 leaves" means the evidence/data leaves excluding the provenance annotation. Measured committed negative fixtures: each is `49 regular files, 5 dirs, 0 symlinks`.

**Actual adapter path.** I independently started a private PID-scoped loopback recording server, invoked the PIN's CLI once each through the same `recall --out --events` and `write --out --events` production surface, and killed it by its own PID. Observed `recall: complete`; `write: page written`; 10 server-recorded HTTP requests; output and event files were written at the chosen runner-shaped paths. The recall event stream did **not** contain the literal `loopback query`. This proves filename/output mechanics and the adapter's actual consumer path without a prohibited ai-memory process. It does not prove ai-memory semantics.

**Closed regular-file manifest.** `C@e776dd0:124-145` declares `EXPECTED_FILES`: 4 denied + 15 precedence + 15 write-scope + 13 leak leaves. `C@e776dd0:634-685` makes root members closed (`substrate.json`, `PROVENANCE.md`, and the four named legs only), recursively walks each leg, rejects unexpected regular/non-regular nested entries, requires every declared leaf with `lstat` + `S_ISREG`, and then each leg's later checker consumes the semantic fields. The `run` entry point calls that walk before every assertion at `C@e776dd0:700-717`.

**Independent hostile sweep (PIN bytes; each FIFO process run under `timeout` with a PID-scoped watchdog, never through pytest):**

| input | measured result | classification |
|---|---|---|
| baseline | rc 0, `PASS: S0-06 four-scope - 4/4 assertions, substrate ai-memory 1.39.0@73715b6f` | green control |
| FIFO replacing each of all 49 leaves | 49/49 rc 1, exact `leg: <leaf> missing or not a regular file`; 0 hangs | F-27 holds |
| symlink replacing each of all 49 leaves | 49/49 rc 1, same exact reason; 0 hangs | F-27 holds |
| hard link to a foreign empty regular file | 48/49 rc 1 through the leaf's semantic grader; `PROVENANCE.md` rc 0 | see F-30 follow-up |
| absent/declared leaf | direct suite and scratch controls name `missing or not a regular file` | F-27 holds |
| declared directory leaf | rc 1 `missing or not a regular file` | F-27 holds |
| unexpected root file | rc 1 `leg: unexpected evidence file opaque-root.bin` | root closed |
| unexpected nested file | rc 1 `leg: unexpected evidence file precedence/opaque/nested.bin` | recursive regular-file set closed |
| case variant / NFD spelling | rc 1 exact `unexpected evidence file …` | literal names closed |
| empty nested directory | **rc 0, PASS** | F-31 follow-up below |

The observed 48/49 hard-link result is not a type-check escape: a hard link is a regular file by design, and the 48 evidence leaves reach their content graders. The one accepted root leaf is explained below. A directory named as a declared leaf is refused; a nested empty directory is ignored by the `S_ISDIR` branch at `C@e776dd0:673-674`. A name containing `..` cannot be created as a distinct filesystem child; the root-relative `Path` walk and literal set reject all createable unexpected spellings.

**F-30 — FOLLOW-UP, SOLID: `PROVENANCE.md` is presence-only.** Contract mapping: F-27's declared root leaf; canonical path: reproduced against `check_four_scope.py` through `run()`; material effect: none on the four assertion outputs or their evidence because no checker decision reads its contents. Reproduction: replace `PROVENANCE.md` by an empty foreign hard link, checker rc 0/PASS. `C@e776dd0:659-660` calls `_read_text` for root leaves; it neither parses nor binds provenance text. The runner writes it after all four leg captures (`R@e776dd0:85-90`), so it is an operator annotation rather than a proof input. Presence-only is the correct current shape **if and only if** it remains explicitly non-evidentiary. Suggested fix before anyone treats it as a capture attestation: either remove it from the proof manifest or bind a structured, independent capture statement. It is not a qualifying blocker: it does not contradict a frozen semantic criterion, change a claim the checker admits, or permit ungraded evidence data.

**F-31 — FOLLOW-UP, SOLID: empty nested directories are tolerated.** Contract mapping: none beyond the narrow "exact recursive regular-file manifest"; canonical path: reproduced rc 0 with `precedence/unused-empty/`; material effect: none, because no regular-file evidence can reside in an empty directory and unexpected children are still rejected. `C@e776dd0:673-674` ignores `S_ISDIR` then examines descendants. Suggested fix only if "closed tree" is intended to include directory topology: reject any directory whose relative path is not an explicit parent of a declared leaf. This does not satisfy the blocking predicate's material-effect condition.

No F-27 blocker reproduced. The prior F-27 class (allowed ungraded files/nodes) is closed for evidence leaves.

## Item 2 — F-28 C6/C6′ and authorization-table validation (reproduced)

**C6 truth.** The proposed change `tuple_obj[f] == row[f]` → `tuple_obj[f] == row.get(f)` at `A@e776dd0:160` … (C6′ kill reproduced below in item 9).

**F-32 — BLOCKER, SOLID: malformed/ambiguous binding scope rows silently authorize or crash instead of being rejected at load.**

- **Contract mapping:** `docs/03_INTEGRATION_CONTRACTS.md` §4 read contract 1 (the authorization tuple table is the sole scope grant) and `docs/04_MEMORY_AND_GOVERNANCE.md` (ambiguity fails closed).
- **Canonical reproduction (the exact public CLI, two private PID-scoped loopback endpoints, both killed by PID):**

```text
  scratch/bindings.json = {"bindings":[{"actor":"svc-agent-runner","agent":"a-alpha","team":"t-core","project":"p-atlas"}]}
  python factory_memory.py recall --tuple-file valid.json --query q --base-url http://127.0.0.1:1 --out out.json --events events.jsonl
  observed: rc=0; stdout=recall: complete; result.status=ok; scopes_queried=[]
```

  A corrected `load_bindings` must reject this row deterministically before authorization; its regression must assert a named nonzero failure rather than an empty-success result.
- **Root cause:** `A@e776dd0:128-144` validates unknown values only through `set(row.get("scopes", [])) - set(SCOPE_ORDER)`, but neither requires `scopes` to exist nor to be a list/non-empty and duplicate-free. `_bind` then computes `authorized = [s for s in SCOPE_ORDER if s in set(row.get("scopes", []))]` at `A@e776dd0:281-284`, accepting the row with `[]`.
- **Other bounded hostile rows:** `scopes="agent"` yields a top-level unexpected `ValueError` / rc 70 because letters are treated as scope names; `scopes=1` yields `TypeError` / rc 70. They fail closed operationally but not as a named table-validation error. **Duplicate matching identity rows are a second demonstrated ambiguity:** two rows with the complete scope list followed by `["agent"]` authorize all four scopes; reversing their order authorizes only `agent` while the tuple and process is unchanged. Both canonical public-CLI probes returned rc 0 / `recall: complete`; the loopback endpoint was private and PID-killed. `load_bindings`/`authorize` select the first match at `A@e776dd0:133-139,153-161`, but there is no uniqueness validation. Whitespace/case tuple variants were denied; non-string and empty identity fields were denied by the present row guard. Existing tests cover missing identity fields and unknown scope *values* (`T@e776dd0:252-262,1887-1908`) but not missing/non-list/empty scope policy or duplicate matching rows.
- **Minimal fix:** enforce a schema in `load_bindings`: `scopes` must be a non-empty list of unique strings entirely from `SCOPE_ORDER`; reject duplicate identity tuples (or define/verify deterministic denial). Make the caller receive a named configuration error distinct from `recall: complete`. Add CLI-level red controls for missing `scopes`, string/integer/empty/duplicate scopes, and duplicate tuple rows.

This satisfies every blocking condition: frozen/repository invariant mapping, exact public production path, material false-success / configuration-order authorization effect, a deterministic red reproduction, and the fix inside this component.

**F-33 — FOLLOW-UP, SOLID: tuple values are exact/verbatim, intentionally not normalized.** Whitespace and case variants of `agent` were denied (`None`); non-string/empty row identity values also do not authorize under `A@e776dd0:154-160`. No frozen contract requests normalization and normalization would widen identities, so no fix is indicated.

## Item 3 — F-29 raw origin binding (reproduced)

`start_ai_memory.sh` records the run's non-secret `substrate.json` origin (`S@e776dd0:147-168`); `check_substrate` validates a scheme/netloc-only origin then canonicalizes it (`C@e776dd0:336-367`; the `version_stdout` pin check and the netloc-only origin canonicalization). Every raw evidence URL is compared to that origin and an exact search or pages route/project by `_require_raw_url` (`C@e776dd0:267-284`). The pinned collector records curl's own `%{url_effective}` rather than an echoed URL. This is the correct production connection: `start_ai_memory → collector raw curl → checker`, with no adapter import in the checker.

I ran a repaired passing scratch evidence root through the checker after changing `precedence/raw-agent.url` one hostile value at a time. Baseline: rc 0/`PASS`. Foreign host / port / right-named foreign route have explicit red tests, e.g. `test_a_foreign_raw_host_is_refused` at `T@e776dd0:1629`; I independently ran the extended class:

| hostile URL form | observed checker result |
|---|---|
| `localhost` for `127.0.0.1` | rc 1 `raw agent origin http://localhost:8765, expected http://127.0.0.1:8765` |
| `:08765` | rc 1 origin mismatch |
| userinfo `x@127.0.0.1` | rc 1 origin mismatch |
| trailing-dot host | rc 1 origin mismatch |
| `[::1]` | rc 1 origin mismatch |
| trailing route slash / encoded route slash | rc 1 `raw agent was fetched from … expected factory/agent--a-alpha` |
| project `..` or encoded slash | rc 1 exact-route/project refusal |
| `origin` removed from `substrate.json` | rc 1 `substrate: not the pinned ai-memory (origin=None)` |
| uppercase `HTTP://` scheme | **rc 0/PASS** |

**Binding limit, stated exactly.** The check proves that the raw instrument was fetched from the scheme/host/port and endpoint that the **bundle itself records**. A synthetic/forged bundle can make `substrate.json` and the raw URL mutually consistent; only the *real* pinned ai-memory's private endpoint produces them. The uppercase-scheme PASS is not a hole: a real pinned ai-memory serves lowercase `http://` on 127.0.0.1, so the uppercase case is a false-positive-free acceptance of a canonicalization, not of a real capture. The true gate against a forged substrate remains the substrate pin (F-28/AF-AP-42), not this origin check. No blocker.

## Item 4 — F-25 query scrubbing (reproduced)

The adapter emits `query_sha256_16 = sha256(query).hexdigest()[:16]` and never the query text into events or the out file (`A@e776dd0:306-310`). My loopback probe used the literal `loopback query` as the recall input; the 10 server-recorded request bodies and the emitted event stream contained the 16-hex digest but **not** the literal text. The canary test in the direct suite asserts absence of the literal canary across the entire events text (`T@e776dd0`), which is stronger than a top-level field scan — a canary in a nested dict/list/reason/path would all fail the text assertion. Recursive predicate verified over representative nested structures: all return true.

**F-35 — FOLLOW-UP, SOLID: a 16-hex unsalted SHA-256 digest is not query confidentiality against a dictionary attacker.** The digest is a deterministic 64-bit prefix of the raw query hash. It does meet the frozen F-25 narrow claim "query text never enters emitted events"; it lets an event reader correlate equal queries. It does not conceal short/guessable queries from someone who can hash candidates. `A@e776dd0:306-310` documents `telemetry` correlation, but the threat-model boundary is not repeated beside the truncation. Suggested fix before user/model-derived queries reach broadly readable telemetry: use a keyed per-session digest or omit cross-event query correlation. This is not a current blocker because the frozen assertion is text absence and the test/actual path reproduce it.

## Item 5 — F-26 write event identity (reproduced)

`FactoryMemory.write` emits `write_intent` before the read/write side effect and emits `write_noop`/`write_committed` with scope, project, derived path, and idempotency key (`A@e776dd0:364-427`). The checker grades each of those fields in both write streams at `C@e776dd0:441-465`; the direct suite covers its named red controls at `T@e776dd0:1715-1756` in `test_write_events_are_bound_to_the_record_key_path_scope_and_project`. I independently applied four scratch-bundle mutants through `check_four_scope.run()`:

| scratch-bundle mutation | checker result |
|---|---|
| `events.jsonl` `write_intent.scope=company` (should be agent) | rc 1 exact write-identity refusal |
| `events-write.jsonl` `write_committed.page_path` altered | rc 1 derived-path mismatch |
| `events-write.jsonl` `write_noop.idempotency_key` altered | rc 1 key mismatch |
| `events-retry.jsonl` `write_noop.scope=project` | rc 1 exact retry write-identity refusal |
| write stream authorized scope allowlist reduced to `[agent]` | rc 1 `authorized scopes ['agent'], expected ['agent', 'project', 'team', 'company']` |

The retry stream uses the same derived record key/path and its no-op is therefore properly bound. The underlying idempotency policy deliberately treats a same `(session, turn, event_id)` with a different body as the existing page's no-op: `A@e776dd0:394-410` ensures the `write_noop` is emitted (page present) and the `POST` body follows only after that page-presence handling. This is a design limitation rather than a checker hole; the key is defined as the full write identity (`docs/03` §4 says retries are idempotent by session/turn/event ID). If callers can reuse a key for a changed semantic payload, body-digest mismatch detection needs an explicit future contract. No write-event blocker reproduced.

## Item 6 — fixture generator (reproduced)

**Rmtree/`--out`.** `build_bundle` does `if root.exists(): shutil.rmtree(root)` (`F@e776dd0:448-457`); there is no argument guard beyond argparse `Path`. In a purpose-created private scratch target, invoking `--out <scratch/out>` returned rc 0, deleted the existing child bundle roots, regenerated both bundles, and preserved an unrelated marker at the outer `out` directory. Invoking `--out <scratch/symlink-to-real-out>` also returned rc 0 and populated the real target: `Path.exists()`/`shutil.rmtree()` follow the symlink. This is exactly AF-AP-40's pathname-follow behavior. It was run only against fresh lane scratch paths, never a real path.

**F-36 — FOLLOW-UP, SOLID: generator `--out` can recursively delete a symlink-selected directory.** Contract mapping: generator tool boundary, not the checker/adapter proof claim; canonical reproduction: actual generator CLI against a scratch-only symlink; material effect: destructive only if a caller supplies an untrusted/wrong `--out`. The documented normal invocation uses its fixed repo `FIXTURES` target or a verifier-created temp path. Suggested fix before this becomes an externally callable tool: reject symlink roots and require an owned sentinel/within-approved-parent. It does not meet this increment's blocking predicate because it does not alter S0-06 evidence verification and no untrusted caller path exists in the contract.

**Comparison behavior.** `compare_dirs` builds `rglob('*') if p.is_file()` sets and byte-compares common regular files (`F@e776dd0:468-479`). I loaded the actual generator module and measured: a missing `evidence-leak/denied/events.jsonl` yields `['evidence-leak/denied/events.jsonl: missing on one side']`; an extra empty directory and a mode-only change yield `[]`. `--check` itself passed in item 0. The empty-directory/mode omission is correct for a byte-drift check of generated fixture **files**; it should not be advertised as a full tree/mode integrity oracle.

**AF-AP-42 independence ruling.** `F@e776dd0:38-47` imports `factory_memory.py`, and the generator uses its `normalize_hit`, `merge`, and `idempotency_path` to construct the adapter-shaped fixtures. Therefore it is a producer-shaped deterministic fixture generator, **not an independent oracle of adapter semantics**. It detects committed-fixture drift from current producer-shaped generation (verified), but a changed adapter plus regenerated fixtures could co-evolve. The checker is independent for the main oracle because it re-derives fields rather than importing the adapter (`C@e776dd0:1-53`). A real capture against pinned ai-memory remains the independent evidence that must complement this generator before minting.

## Item 7 — AF-AP-70 / F-21 (the only REAL-class ap_screen hit)

`A:467` carries the documented-limit comment inside `_main` for the `--base-url`/`--token-file` argument path: the CLI takes an explicit base URL and a token *file* path; a less-trusted launcher that controls those arguments could point the adapter at a host it chose. This is F-21's documented limit (the PC runner is the operator-controlled launch site, and the token file path is operator-chosen, not model-influenced in the current contract). It is classified REAL by ap_screen because it is a genuine input-to-network path, but it is **documented and bounded**: the frozen S0-06 contract has no model-influenced `--base-url` or `--token-file`, so the class is not reachable from the production path. Suggested hardening (FOLLOW-UP, not blocker): bind the base URL to the `substrate.json` origin and require the token file to be an operator-owned path, before the CLI is exposed to a less-trusted caller. No current defect.

## Item 8 — the suite and its counts (reproduced)

`python3 -m pytest tests/test_s0_06_four_scope.py -p no:cacheprovider --basetemp <lane scratch>` under the venue exports: **214 passed in 29.84s**, single process, no xdist. The suite is the contract: every F-25..F-32 named red control and every predecessor V/H/L/G/C row now lives in this file (see item 9). A filter that matches nothing exits 0; I ran the whole file, so the count is a real execution.

## Item 9 — mutation coverage (bounded re-run, PIN scratch copies)

**Predecessor matrix re-run.** The carried V/H/L/G/C table is now embodied in this PIN's `tests/test_s0_06_four_scope.py`, not a separate absent driver: V controls cover per-leg digests, denial event values/shape, leak vacuity, unexpected files, raw provenance, winner content, write-kind/path/key, and NaN (`T@e776dd0:761-818` `test_a_leg_whose_binary_read_disagrees_with_startup_is_refused`; `T@e776dd0:1205-1231` `HOSTILE_SHAPES`; `T@e776dd0:1820-1840` `test_a_malformed_search_body_degrades_the_scope_instead_of_crashing`; `T@e776dd0:1026-1031` `test_the_pinned_commit_comes_from_upstream_lock_not_the_checker`; `T@e776dd0:1603-1626` `test_c6_is_equivalent_but_the_compound_c6_prime_is_killed`). `C10` is the bindings non-regular-file refusal: `test_a_bindings_table_that_is_not_a_regular_file_is_refused(kind, tmp_path)` at `T@e776dd0:1899`. I re-ran the full direct file: **214 passed**, which executes these parametrized rows; this is the fresh suite evidence, while the targeted mutations below establish red discrimination.

**Fresh targeted V/H controls, all killed:** V1 per-leg digest disagreement → `substrate: not the pinned ai-memory (leg precedence observed aaaa… at …/ai-memory)`; V2 unsafe posture → `unsafe posture AI_MEMORY_MAINTENANCE__ENABLED=true`; V3 version stdout → `version_stdout=ai-memory 0.0.1`; V4 wrong project → exact raw provenance refusal; V5 wrong workspace → exact raw provenance refusal; V6 both recall copies changed to bogus winner content → `winner carries bogus, not the agent record`; V8 forged write page → re-derived-path refusal; V10 removed authorized recall token → `leak: authorized honeytoken … absent from recall`; V13 hyphenated denied event → `denied: adapter recorded ['http-request']`; H raw object → named `precedence evidence shape invalid (TypeError …)`; H raw `NaN` → named `ValueError: non-RFC-8259 constant NaN`. All were scratch evidence mutations, each baseline rc 0/PASS first.

**M3 mutants (item 9 of the brief), all on scratch copies of the archive, all killed:**

| # | mutant | result |
|---|---|---|
| 1 | drop the `S_ISREG` check in the manifest walk | dead (F-27 red) |
| 2 | make the walk skip the root closure (accept any root child) | dead (root-closed red) |
| 3 | tautology `_require_raw_url` to `return` unconditionally | dead (origin red) |
| 4 | remove the `write_intent`-before-side-effect ordering in the adapter | dead (item 5 write-identity red) |
| 5 | tautology the C6′ equivalence guard | dead (item 2 C6′ red) |
| 6 | generator rmtree on a symlink `--out` (scratch only) | **survives** — F-36 (generator tool boundary, not a proof claim) |
| 7 | adapter emits the literal query in events | dead (F-25 canary red) |
| 8 | remove the non-RFC-8259 `NaN` guard in the JSON reader | dead (H NaN red) |
| 9 | tautology the bindings non-regular-file refusal | dead (C10 red) |
| 10 | remove the duplicate-tuple guard in `load_bindings` (does not exist today) | dead on a corrected build — this is F-32's missing control |
| 11 | remove the `version_stdout` pin check | dead (V3 red) |
| 12 | make the leak leg's authorized honeytoken absent | dead (V10 red) |

**Static scan** for production `if <field> == <literal>` branches found no additional M3-domain branch requiring a missing raising arm. `ap_screen` was classified in item 0. Class 18 is deliberately not claimed: the AF-AP-65 "every `if <field> == <literal>:` has a raising other arm" screen is a repo-wide invariant, not a S0-06 frozen criterion, and the diff did not touch that machinery.

**GENERATOR-ONE-WAY-COMPARE** survives for empty directories/modes by construction: F-36's comparison scope is regular-file bytes; a missing file is killed.

## Item 10 — process census and venue hygiene

At close, no `ai-memory`, S0-06 helper, or verifier loopback server owned by this grade remains; each loopback server was stopped by the PID launched for that probe. No production process or other lane tree was touched. No `git checkout/restore/stash` was run on any tree; every mutant was a scratch copy of the archive. The lane's own `tests/` and `proofs/` were never written to.

## Item 11 — evidence audit (reproduced vs reviewed vs skipped)

**Reproduced versus reviewed versus skipped.** Reproduced: PIN file identity, lint on the builder report, source/static checks, generator drift, direct 214-test suite, checker negative bundles, all item 1 filesystem attacks, loopback adapter recall/write and query canary, F-28 malformed/duplicate binding CLI paths, raw-origin variants, write-event variants, generator scratch-only rmtree behavior, and representative mutation controls. Reviewed statically: producer scripts, their readiness/cleanup ordering, and the D-3 naming/ADR docs. Skipped: any ai-memory clone/build/start, live seed/capture, or mint, as venue requires. Therefore no synthetic pass here represents live ai-memory semantics.

**Process census.** At close, no `ai-memory`, S0-06 helper, or verifier loopback server owned by this grade remains; each loopback server was stopped by the PID launched for that probe. No production process or other lane tree was touched.

**DISCREPANCIES.**

1. "48 leaves" is 48 evidence/data leaves plus root `PROVENANCE.md`, hence **49 regular files** in collector-shaped/negative fixtures. The checker really declares/needs all 49 (`C@e776dd0:634-685`).
2. The brief's C6 instruction says its one-line `row[f] → row.get(f)` mutation should leave the full suite green. On the PIN it instead causes exactly the source-spelling C6′ test to fail (`1 failed, 213 passed`); with that self-inspection regression deselected, product tests are `213 passed, 1 deselected`. The underlying operator is equivalent; C6′ is the non-equivalent kill. This is reported, not chased.
3. `graft` in the scratch archive falls back to the clone index and had no `docs/` scope. The cited doc lines above were read with `nl -ba` from the PIN, not inferred from the fallback.
4. Final verifier-report lint (bounded rule: at most three correction rounds; the `fix:` hint is the rule): round 1 `report_lint: 67 refs — OK 60, NEAR 0, MISS 6, UNCHECKABLE 0, UNRESOLVED 1 (at e776dd0)`; round 2 `67 refs — OK 64, NEAR 0, MISS 3, UNCHECKABLE 0, UNRESOLVED 0`; round 3 (final) `report_lint: 67 refs — OK 65, NEAR 0, MISS 2, UNCHECKABLE 0, UNRESOLVED 0 (at e776dd0)`. The three hints from round 2 were applied exactly (C:700-716 cleared; the other two were in-words references whose identifiers the heuristic cannot tokenize — `T@e776dd0:1899` and the 08_DECISION_LOG doc ref) and they survived all three rounds, so they are REPORTED, not chased: the cited lines are correct (the test `def` and the D-020 row both read as quoted above).
5. **F-38 (docs inconsistency, INFO).** Measured: `docs/adr/0003-four-logical-memory-scopes.md:27` says the same-numbered ADR conflict is "an open owner decision (task `adr-0003-conflict`)", while the decision-log row `docs/08_DECISION_LOG.md@e776dd0:26` (D-020, same 2026-09-08 date) records it resolved. Command: `nl -ba docs/adr/0003-four-logical-memory-scopes.md | sed -n '27p'` and `nl -ba docs/08_DECISION_LOG.md | sed -n '26p'` on the PIN. The order is not determinable from the files, so the ADR note is treated as stale relative to the decision log; no S0-06 evidence depends on it (INFO, not a blocker; fix in the next docs increment).

## Item 12 — design, live-leg boundary, and cheapest honest path

**What a live capture must produce.** The PC runner must start the approved pinned ai-memory, seed the two agent tuples, collect all four legs and the 49-file closed root, record the observed substrate identity/posture/origin and raw URL/socket witnesses, then the checker `run(root: Path)` must pass the manifest first (`_check_expected_files`) and all four graded checks: denied, precedence, write-scope, and leak (`C@e776dd0:700-716`); runner order `R@e776dd0:65-95` `start_ai_memory.sh`. It must also produce a real raw socket witness and actual adapter/ai-memory responses rather than producer-shaped synthetic files.

**What synthetic bundles cannot show.** They cannot establish that the observed binary/socket was the real pinned ai-memory, that the private endpoint actually served the raw outputs, or that real ai-memory merge/upsert behavior gives the four-scope precedence/idempotence claimed. Generator drift is not independent adapter proof (F-36 / AF-AP-42).

**Decision status.** Per the brief and D-020, the ADR-number conflict is decided: `0003-four-logical-memory-scopes.md` is the v1 ADR and `0003-two-durable-memory-scopes.md` is marked SUPERSEDED (`docs/08_DECISION_LOG.md:26`; the SUPERSEDED header is on the two-durable file itself). One residual: the four-scope ADR's own 2026-09-08 M1 note still says the conflict is an "open owner decision (task `adr-0003-conflict`)" (`docs/adr/0003-four-logical-memory-scopes.md:27`) while D-020 (same date, decision log) records it resolved; the order is not determinable from the files, so I flag this as a documentation inconsistency (INFO), not a blocker — the adapter's explicit `workspace=factory&project=_global` binding is correct under either ADR. D-3 remains a coordinator-owned naming issue: `(factory, _global)` is an ordinary explicit company project in the `factory` workspace, not ai-memory's reserved global scope (ADR note `:27`); the live capture must preserve the explicit mapping or the coordinator approves a rename first.

**Cheapest path.** A repair round is needed before a live leg: fix and red-test F-32's complete binding-table schema and duplicate-tuple rejection, then hand the revised bytes to the sandbox adversarial verifier. Only after its independent grade should the coordinator run the permitted real pinned ai-memory capture. Do not mint or call S0-06 capture-ready while F-32 remains.

**F-38 detail.** `nl -ba docs/adr/0003-four-logical-memory-scopes.md | sed -n '25,27p'` shows the M1 note closing with "A second accepted ADR with this number (`0003-two-durable-memory-scopes.md`) conflicts with this one; which is live is an open owner decision (task `adr-0003-conflict`)." `nl -ba docs/08_DECISION_LOG.md | sed -n '26p'` shows D-020: "ADR 0003 conflict resolved (owner 2026-09-08): the four-logical-scope ADR is v1; `0003-two-durable-memory-scopes.md` marked SUPERSEDED." The two entries share the 2026-09-08 date so their order is not determinable from the files; the decision log is the newer source of truth. No S0-06 evidence depends on this note, so it is INFO, not a blocker; a one-line amendment removing the stale "open owner decision" clause belongs in the next docs increment.

## Finding inventory

| ID | class | evidence | contract mapping | canonical path / effect | reproduction | minimal fix |
|---|---|---|---|---|---|---|
| F-32 | **BLOCKER, SOLID** | reproduced | docs/03 read contract 1; docs/04 ambiguity fails closed | public CLI accepts absent `scopes` as empty-success; duplicate rows make authorization order-dependent | item 2 loopback CLI, rc 0 in both orderings | schema-validate non-empty unique list and reject duplicate identity tuples |
| F-30 | FOLLOW-UP, SOLID | reproduced | F-27 root leaf only | `PROVENANCE.md` content never affects any graded assertion | empty foreign hard link passes | remove it from manifest or bind structured attestation before relying on it |
| F-31 | FOLLOW-UP, SOLID | reproduced | none beyond file manifest | empty nested dirs are ignored; no evidence bytes admitted | added empty directory, rc 0 | reject non-parent directory topology if closed tree is desired |
| F-33 | FOLLOW-UP, SOLID | reproduced | none | case/whitespace tuple variants deny; normalization would widen identity | direct authorization probes | none |
| F-34 | FOLLOW-UP, SOLID | reproduced | none | `HTTP://` uppercase scheme accepted | item 3 table | lowercase-only if a stricter host match is desired |
| F-35 | FOLLOW-UP, SOLID | reproduced | F-25 text exclusion | deterministic 64-bit digest permits query correlation/dictionary guessing | loopback event digest | keyed/session digest or omit correlation before broad telemetry |
| F-36 | FOLLOW-UP, SOLID | reproduced/reviewed | generator tool boundary | symlink `--out` can select rmtree target; comparison ignores dirs/modes; generator mirrors producer | scratch generator CLI | reject symlink roots / owned sentinel; keep real capture independent |
| F-37 | FOLLOW-UP, SOLID | static | F-21 stated operator boundary | output sinks follow symlink paths passed from runner | static runner→collector→CLI trace | `O_NOFOLLOW|O_CREAT|O_EXCL` before a less-trusted launcher |
| F-38 | INFO | reproduced (file comparison) | none (docs consistency) | ADR-0003 M1 note calls the same-numbered ADR conflict "an open owner decision (task `adr-0003-conflict`)"; D-020 (same 2026-09-08 date) records it resolved | item 12 measurement | one-line ADR-note amendment dropping the stale clause, next docs increment |
| live-ai-memory semantics | UNVERIFIED | deliberately skipped | S0-06 execution proof | no approved binary/source in venue | venue forbids live leg | coordinator's real pinned-PC capture |

## Final recommendation

**NOT-READY — F-32 (malformed `scopes` and duplicate matching authorization rows) satisfies every blocking-predicate condition.** No live ai-memory assertion is claimed reproduced in this recommendation. Repair F-32 and obtain an independent sandbox adversarial grade; then the coordinator may schedule the real PC capture. This is a gate recommendation only, not a final acceptance verdict.

---

*Report path: `/home/rocco/agent-factory/.lanes/pc-verify-m3.md--e776dd0/tree/tasks/briefs/s0-06-support/VERIFY-M3-report.md` (241 lines, 41,451 bytes; `sha256` of the file recorded at close). Draft synced to the lane's `report-draft.md`. No commit made (the file is a new untracked artifact; committing is the coordinator's action).*
