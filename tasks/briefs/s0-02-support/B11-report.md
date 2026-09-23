# B11 report — S0-02's four seed negative legs (task #191)

LANE: s0-02-b11 (sandbox, shared tree, no worktree). PIN 8d8c97e. Status: **DONE** (tests green in the sandbox;
uncommitted; not live). Aliases: C = `proofs/S0-02/check_buzz_authz.py`, T2 = `tests/test_s0_02_buzz_authz.py`,
spec = `proofs/S0-02/spec.json`. `C@8d8c97e:NN` is a PIN-era line; a bare `C:NN` is the working tree after the change.

## 0. Outcome (read this first)

- DONE: `check_buzz_authz.py [--synthetic-root <dir>] --denial <fixture> <evidence-root>` grades one negative leg and prints
  `failure_reason: <the observed row's reason>`, rc 1. The spec gains the four seed legs in seed order. T2 gains 45 tests; one existing
  test's selector is narrowed (D2). T2 twice: `246 passed, 24 skipped` both runs, set `a5de0beef100`.
- **MUST LAND IN THE SAME COMMIT (D1):** `tests/test_validate_ledger.py:534` asserts the S0-02 shortfall `{"S0-02": (1, 4)}`. The spec
  change makes it red by design. It is outside my boundary, so I did not edit it. The coordinator makes the one-line edit, or CI reds.
- NOT proven: the four legs over the LIVE evidence. `proofs/S0-02/evidence` does not exist; each leg defers (rc 2) today. They run
  over live evidence only at mint time, after the capture. This lane proves them over the synthetic pass bundle and hostile copies only.
- Adjacent defect found, NOT fixed (A1): the bundle mode never grades the revoked leg's relay text. A revoked receipt that carries
  the stale text still PASSES, at the PIN and after this change.
- Mutants: m1 to m5 all killed (table in section 6), plus four extra mutants of my own, all killed.

## 1. Premise re-measurement (2026-09-23T14:36Z, sandbox @ local 905a8c7, origin fa4532e)

Boundary blobs are byte-identical at the PIN, local HEAD, origin head and the working tree:

```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short HEAD; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
2026-09-23T14:36Z
905a8c7
fa4532e
== 8d8c97e / HEAD / origin/... / working tree (all four identical)
7b875de37dce   936 proofs/S0-02/check_buzz_authz.py
5b061cd1303f    26 proofs/S0-02/spec.json
b9621c9d9398  3611 tests/test_s0_02_buzz_authz.py
c8c7ac11e2ba   314 proofs/S0-02/oracle/denial_table.py
1d67210b11b8   587 proofs/S0-02/tools/build_fixtures.py
7659e4bbc4c8    36 proofs/registry.yaml
136034643765    48 proofs/schemas/spec.schema.json
2210fbff942c   522 scripts/validate-ledger
$ git log --format="%h %s" 8d8c97e..HEAD -- proofs/S0-02 tests/test_s0_02_buzz_authz.py proofs/registry.yaml proofs/schemas scripts/validate-ledger
(end)          <- no commit since the PIN touches the boundary or its read-only inputs
$ git status --short     (at lane start)
?? tasks/briefs/laya/J1-1-R2-report.md     <- another lane's file (J1-1-R2); not touched
```

The seams sit at the brief's lines:

- `_check_named_observable` C@8d8c97e:434
- `_check_leg` C@8d8c97e:493
- `_check_replay` C@8d8c97e:653
- `_check_duplicate_receipt` C@8d8c97e:738
- `_check_bundle_uncapped` C@8d8c97e:811
- `def main` C@8d8c97e:905
- the registry row's `required_negative_controls` at proofs/registry.yaml:13
- the seed's four fixtures (`expected_failure_reason`) and the DISTINCT rule at seeds/seed-stage0-v1.yaml:376-380
- the F16 floor `negative-controls-short` at scripts/validate-ledger:312-324
- `proofs/S0-02/check_buzz_authz.py` listed as a gate file at scripts/gate_files.txt:34

```
$ python3 -c (spec legs)
[('positive', {'exit_code': 0}), ('negative', {'exit_code': 1, 'failure_reason': "blanket-rejection: reasons ['delivery::restricted: not a channel member'] not distinct — 6 negative legs collapsed to 1 observable(s)"})]
$ python3 proofs/S0-02/check_buzz_authz.py --denial neg-stale proofs/S0-02/fixtures/evidence-pass/legs; echo rc=$?
rc=64
usage: check_buzz_authz.py [--synthetic-root <dir>] <evidence-root>
SEED_REASONS ('denied: sender-not-in-allowlist', 'denied: signature-invalid', 'denied: event-replayed', 'denied: event-stale')
NEGATIVE_FIXTURES ('neg-unauthorized', 'neg-bad-signature', 'neg-replayed', 'neg-stale', 'neg-self-authored', 'revoked', 'neg-not-allowlisted')
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
```

Premise verdict: MATCH. No CONTRACT-INVALID stop.

Re-checked at lane end (2026-09-23T15:15:54Z): HEAD moved to 1e1f1df during the lane (the coordinator landed J1-1-R2 and two briefs).
C, spec and T2 at that HEAD are still the PIN blobs (7b875de37dce, 5b061cd1303f, b9621c9d9398), so this diff sits on the same base.
`tests/test_validate_ledger.py` is unchanged (6c537845963a at both), so D1's line 534 still needs the edit.

## 2. Grounding (before any edit)

- Pack: `scripts/lane_context.sh ... -o /tmp/b11/pack.md` rc 0, 268 lines. Each graded seam has ONE static caller,
  `_check_bundle_uncapped` (crg `callers_of` and ripwire agree).
- GitNexus `impact _check_bundle_uncapped` (upstream) returned `risk: UNKNOWN`, 0 callers resolved. A text search resolves it: the one
  caller is `check_bundle` (`_check_with_timeout(90, _check_bundle_uncapped` at C@8d8c97e:902, a reference the index does not record);
  `check_bundle` is called by `main` (`print(check_bundle(root, anchors))`, C@8d8c97e:925) and by T2's `_run_checker` (T2@8d8c97e:75).
  Nothing outside `proofs/S0-02/` and T2 calls into C.
- The consumer contract (read-only): `observed_reason` in scripts/proof-runner:192-203 accepts a negative leg when ANY stdout/stderr
  line CONTAINS the spec's `failure_reason`. So a failure line that quotes evidence text reads as a proven denial when the evidence
  carries the reason. C quotes evidence in failures: `_read_receipt` (`extra` key names, C@8d8c97e:311-316); `_check_leg`
  (`fixture.get('fixture')!r`, C@8d8c97e:502-505); `_check_delivered_event` (`delivered['kind']`, C@8d8c97e:232-233);
  `_check_one_process` (`seq!r`, C@8d8c97e:625-631); `_check_duplicate_receipt` (`delivery['message']!r`, C@8d8c97e:771-777); the
  leg closure and the root closure (`sorted(extra)`, C@8d8c97e:170 and C@8d8c97e:833). Item 4's "never contains the named leg's
  `denied:` text" closes this: the denial mode escapes `denied:` in every failure line.
- `runs-spec-mismatch` binds the recorded runs to the spec legs by index (scripts/validate-ledger:297-311),
  and `runs-spec-reason-mismatch` by substring reason. The floor counts every negative leg, the blanket leg included.

Constraints in T2 that bind C's new code (all pre-existing):

- `test_no_llm_or_network_in_the_gate_spine` (T2@8d8c97e:2146-2153) bans `socket.`, `subprocess.run`, `LLM` and five more words in C.
- `test_synthetic_root_is_a_command_line_parameter_not_an_env_channel` (T2@8d8c97e:2160-2166) bans `os.environ` and `getenv` in C.
- Executable lines that name `timeline.jsonl` are screened (T2@8d8c97e:2107-2143).
- `removal_line = removal_note` must stay literal in C (T2@8d8c97e:912-914). `test_checker_exits_64_on_a_usage_error` pins rc 64 and
  `usage:` on stderr for no arguments (T2@8d8c97e:2156-2159).
- `python3 --version` = 3.11.15: no backslash inside an f-string expression.

## 3. Changed files and line ranges (working tree)

| file | before → after | changes |
|---|---|---|
C, blob 7b875de37dce → 612c6143ec53, 936 → 1037 lines:

- C:5 the second synopsis line (`--denial <fixture>`); C:9-14 the docstring paragraph with the denial exit contract (`--denial <fixture>`)
- C:672 the `_check_replay` docstring: "spec.json's negative" became `spec.json's blanket` (item 5 falsified the singular)
- C:818-845 `_open_bundle`: the root guard, deferral gate, identity anchor and root closure, moved VERBATIM, plus `return root, identities`
- the moved statements' source: `_check_bundle_uncapped` C@8d8c97e:811-833; now C:848-849 `_check_bundle_uncapped` calls `_open_bundle`
- C:921-940 `_observed_row`; C:943-968 `_check_denial_uncapped`; C:971-974 `check_denial`
- C:977 `USAGE`; C:980-998 `_denial_main`; C:1001-1033 `main` (the `--denial` parse and dispatch)

spec, blob 5b061cd1303f → 777faffb017e, 26 → 66 lines: the four seed legs appended in seed order, their `--denial` cmds at
spec:28, spec:38, spec:48, spec:58 (`neg-unauthorized`, `neg-bad-signature`, `neg-replayed`, `neg-stale`). The positive and blanket
legs are unchanged, and the file still has no final newline.

T2, blob b9621c9d9398 → 5e11a6fbf8f3, 3611 → 3874 lines:

- T2:964-967 D2's narrowed selector (`--synthetic-root`)
- T2:3618-3874 section 8, `B11 (task #191)`: the helpers and 45 tests

`tasks/briefs/s0-02-support/B11-report.md`: new, this report.

## 4. Design decisions (with the rejected alternatives)

- **P1 — one shared root guard.** `_open_bundle` is used by both modes. Rejected: a second copy of the 20-line containment guard in the
  denial path, because two copies drift and a fix to one would leave a hole in the other. The move is behavior-preserving: after the
  extraction alone, the PASS stdout sha256 was unchanged, the blanket output was `cmp`-identical, and all 201 pre-existing T2 tests pass.
- **P2 — the reason comes from the observation.** `_observed_row` reads the one oracle row whose `evidence::observable` key the leg's
  `found` set carries. A row other than the argument's is a Failure. neg-unauthorized and revoked share one key by design (see the
  oracle's revoked row). They are separated by the membership receipt's presence (`os.path.lexists(leg_dir / "membership.json")`),
  which `_check_leg` verified on the revoked leg and the leg closure forbids on every other leg. Rejected: printing
  `oracle.row(fixture_name)["reason"]`, which is mutant m1.
- **P3 — the revoked leg mirrors the bundle.** The bundle skips `_check_named_observable` for revoked:
  `if fixture_name == "revoked"` (C@8d8c97e:867-871). So the denial mode skips it too. Item 3 says "exactly as the bundle check grades it". The alternative (applying
  `_check_named_observable` to revoked, following the parenthetical's literal list) differs on ONE input only: a revoked leg whose log
  ALSO carries the replay's defense-in-depth drop line. My choice proves that leg; the alternative refuses it. revoked is NOT a spec
  leg. **FLAGGED for the coordinator.**
- **P4 — escape every `denied:` in a failure line.** In the denial mode, `denied:` becomes the visible escape `denied\x3a` in every
  failure line, not only in lines that quote the named reason. The invariant is simple: only a proven denial line carries `denied:`.
  Rejected: rewriting the existing failure messages not to quote evidence, because that changes bundle-mode output.
- **P5 — one usage line.** Every usage refusal prints one `USAGE` line that names the flag (item 2). Consequence, **FLAGGED as an
  interpretation:** a refusal WITHOUT `--denial` (for example, no arguments) still exits 64, but its usage text now names `--denial`.
  Every verdict line without `--denial` (PASS / `failure_reason:` / `deferred:`) is byte-unchanged. Rejected: two usage lines.
- **P6 — grammar.** `--synthetic-root` comes first, then `--denial`, in the brief's synopsis order. The reverse order is a usage refusal.
  I used `len(args) < 3` in place of `!= 3` for `--synthetic-root`. Every argv without `--denial` keeps its old exit code.
- **P7 — what "reads no sibling leg" means.** The shared root guard still reads the ROOT: the root closure (an extra root entry
  fails) and the deferral rule (defer only when no leg anywhere carries a timeline). Those are item 3's "anchors, root closure". The
  CONTENT of a sibling leg is never read. The independence test deletes every sibling's receipt and the verdict is byte-identical.
- **P8 — per-leg means per-leg.** Over the committed BLANKET bundle, `--denial neg-unauthorized` is proven. By construction
  (`tools/build_fixtures.py:477-478` writes that leg the same way in both bundles), its evidence genuinely shows its own class. The
  other three seed legs are not proven. Distinctness is a cross-leg property. Only the bundle mode grades it, and the spec keeps it
  twice: through the positive leg (no PASS without six distinct reasons) and the blanket leg. At mint the runner stops on the positive
  leg (leg 0) first, so the per-leg legs never mint over a blanket capture.

## 5. Gates (every command pasted with its output)

Red-green, tests first (section 8 of T2 written before any C/spec edit):

```
RED 2026-09-23T14:56:05Z, C 7b875de37dce + spec 5b061cd1303f (unmodified), the 45 new tests + the narrowed one
$ python3 -m pytest tests/test_s0_02_buzz_authz.py -q -p no:cacheprovider --basetemp /tmp/b11/bt -k "<the 46>"; echo rc=${PIPESTATUS[0]}
rc=1
44 failed, 2 passed, 224 deselected in 6.45s
PASSED ...::test_spec_negative_leg_reason_is_the_exact_observed_line     <- the narrowed D2 test: green before and after
PASSED ...::test_bundle_mode_stdout_is_unchanged_byte_for_byte          <- the PASS-bytes golden predates the change
failure reasons (grep -E "^E  +(assert|AssertionError)" | sort | uniq -c): rc 64 or the old usage text on every denial
test ("assert (64 == 1)" x11, "assert 64 == 1" x4, the usage-text mismatch x9 ...); "assert (2, 'deferred...') == (64, ...)" x2
(the old C read a bare "--denial" as an evidence root); the spec tests: "assert 1 >= 4", "assert 0 == 4", "assert [] == [{'leg': 'neg...}]"
GREEN 2026-09-23T14:57:56Z, the same selection on the change
rc=0
46 passed, 224 deselected in 8.70s
```

Gate 1 — the four denial commands over the pass bundle (2026-09-23T14:58:26Z):

```
$ python3 proofs/S0-02/check_buzz_authz.py --synthetic-root proofs/S0-02/fixtures/evidence-pass --denial neg-unauthorized proofs/S0-02/fixtures/evidence-pass/legs
failure_reason: denied: sender-not-in-allowlist
rc=1
$ python3 proofs/S0-02/check_buzz_authz.py --synthetic-root proofs/S0-02/fixtures/evidence-pass --denial neg-bad-signature proofs/S0-02/fixtures/evidence-pass/legs
failure_reason: denied: signature-invalid
rc=1
$ python3 proofs/S0-02/check_buzz_authz.py --synthetic-root proofs/S0-02/fixtures/evidence-pass --denial neg-replayed proofs/S0-02/fixtures/evidence-pass/legs
failure_reason: denied: event-replayed
rc=1
$ python3 proofs/S0-02/check_buzz_authz.py --synthetic-root proofs/S0-02/fixtures/evidence-pass --denial neg-stale proofs/S0-02/fixtures/evidence-pass/legs
failure_reason: denied: event-stale
rc=1
```

Gate 2 — the bundle mode on the pass bundle, and the spec's blanket leg verbatim (2026-09-23T14:58:35Z):

```
$ python3 proofs/S0-02/check_buzz_authz.py --synthetic-root proofs/S0-02/fixtures/evidence-pass proofs/S0-02/fixtures/evidence-pass/legs
rc=0
PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; replay refused by the relay's duplicate: receipt (buzz-acp drop line absent, defense-in-depth only); +1 revocation leg (assertion 2); removal evidence: coordinator-supplied receipt (unauthenticated; ordering and fields verified; not an end-to-end revocation proof)
stderr bytes: 0
stdout sha256: 74efad21affc2ea55f28aa0155f3e1bfacd88cb529a4009d562f81881a0b9e6d (pre-change: 74efad21affc2ea55f28aa0155f3e1bfacd88cb529a4009d562f81881a0b9e6d)
--- the spec's blanket leg, cmd read from spec.json and run verbatim
$ python3 proofs/S0-02/check_buzz_authz.py --synthetic-root proofs/S0-02/fixtures/evidence-blanket proofs/S0-02/fixtures/evidence-blanket/legs
failure_reason: blanket-rejection: reasons ['delivery::restricted: not a channel member'] not distinct — 6 negative legs collapsed to 1 observable(s)
rc=1
runner match (exact line): True | rc matches spec: True
```

Gate 3 — T2 twice, with the brief's exact command, counts identical:

```
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100
2026-09-23T14:58:47Z
run1 rc=0
246 passed, 24 skipped in 147.98s (0:02:27)
2026-09-23T15:01:16Z
run2 rc=0
246 passed, 24 skipped in 148.89s (0:02:28)
```

Baseline at the PIN (from the brief): `201 passed, 24 skipped` in the same one-file set. 246 = 201 + 45 new tests. The 24 skips are
unchanged, and no existing test was skipped or deleted. The set id names the file list, not its content: the same file now holds 270 tests.

Gate 4 — lint delta and ledger integrity (2026-09-23T15:03:54Z / 15:04:05Z):

```
$ python3 scripts/lint_delta.py
usage: lint_delta.py [-h] (--staged | --base BASE) [--no-ap]
lint_delta.py: error: one of the arguments --staged --base is required
rc=2                                  <- D3: the brief's command does not run as written
$ python3 scripts/lint_delta.py --base HEAD
lint_delta (worktree vs HEAD): 5 .py changed, 0 NEW pyflakes hit(s), 0 removed
anti-pattern screen (TELLS on added lines — verify each, advisory):
  AF-AP-39tests/test_decisions_canonical.py: secret interpolated into a command line ... (AF-AP-39)   <- J1-1-R2's file, not mine
  AP-51 tests/test_s0_02_buzz_authz.py: byte/bitwise-identity claim — if this diff adds a dataclass field feeding an asdict sink, ...
rc=0
$ python3 scripts/lint_delta.py --base 8d8c97e
lint_delta (worktree vs 8d8c97e): 7 .py changed, 0 NEW pyflakes hit(s), 0 removed
rc=0
$ python3 scripts/validate-ledger integrity --root .
rc=0
S0-01 PRESENT
S0-02 ABSENT
S0-03 PRESENT
...
execution_proof numerator=7 denominator=9
```

The "5 .py changed" are my C and T2 plus J1-1-R2's three files. The AP-51 tell does not apply: T2's "byte for byte" and
"byte-identical" claims are `==` comparisons of process bytes or the `(rc, stdout, stderr)` tuple, with no dataclass or `asdict` sink.

Gate 5 — the never-a-gate screen (C is a gate file). I added no import and no dynamic load (2026-09-23T15:04:16Z):

```
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean
rc=0
```

Gate 6 — `git status --short` (2026-09-23T15:04:22Z):

```
 M proofs/S0-02/check_buzz_authz.py                 <- mine
 M proofs/S0-02/spec.json                           <- mine
 M src/agent_factory/decisions/volatile.py          <- J1-1-R2 (not touched)
 M tests/test_decisions_canonical.py                <- J1-1-R2 (not touched)
 M tests/test_decisions_ledger.py                   <- J1-1-R2 (not touched)
 M tests/test_s0_02_buzz_authz.py                   <- mine
?? tasks/briefs/laya/J1-1-R2-report.md              <- J1-1-R2 (not touched)
?? tasks/briefs/laya/VERIFY-J1-0-R5-report.md       <- the verifier (not touched)
?? tasks/briefs/s0-02-support/B11-report.md         <- mine
```

Further checks:

```
$ python3 -c "jsonschema.validate(spec, spec.schema.json)"
spec.json validates against proofs/schemas/spec.schema.json; 6 legs: [('positive', 'proofs/S0-02/evidence', '-'), ('negative', 'proofs/S0-02/fixtures/evidence-blanket/legs', "blanket-rejection: reasons ['delivery::r"), ('negative', 'neg-unauthorized', 'denied: sender-not-in-allowlist'), ('negative', 'neg-bad-signature', 'denied: signature-invalid'), ('negative', 'neg-replayed', 'denied: event-replayed'), ('negative', 'neg-stale', 'denied: event-stale')]
$ node .gitnexus/run.cjs detect-changes --scope all --repo .
Changes: 3 files, 28 symbols / Affected processes: 1 / Risk level: medium
Affected execution flows: • Main → Default (4 steps) — changed: main
$ python3 scripts/ap_screen.py proofs/S0-02/check_buzz_authz.py tests/test_s0_02_buzz_authz.py
--- AP_SCREEN over 2 path(s): 10 hits over 2 files ---      <- 0 in C; 9 pre-existing T2 lines; 1 new: AP-51 on the
                                                                "byte-identical" docstring at T2:3764 (not applicable, above)
$ python3 scripts/ap_screen.py --tests tests/test_s0_02_buzz_authz.py      -> 11 hits; the PIN's T2 -> 11 hits (none added)
$ python3 scripts/report_lint.py tasks/briefs/s0-02-support/B11-report.md --map C=proofs/S0-02/check_buzz_authz.py --map T2=tests/test_s0_02_buzz_authz.py --map spec=proofs/S0-02/spec.json --min-refs 20
report_lint: 53 refs — OK 53, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)      rc=0 (two fix rounds: refs re-wrapped beside their tokens)
$ git hash-object C spec T2      (after every gate; equal to the gate-time blobs)
612c6143ec53 / 777faffb017e / 5e11a6fbf8f3
```

## 6. Mutant table (scratch copy `/tmp/b11/mut` = `git archive HEAD` + my three files; the unmutated copy is green first: `46 passed, 224 deselected in 8.31s`)

Each mutant: an exact-count anchor replace (count 1 asserted), `py_compile`, then the 46-test B11 selection. The pristine file was
restored after each mutant, and equality was asserted at the end (`restored: scratch C and spec equal the pristine copies`).

| id | mutant | result | killing T2 test → failure line (pasted) |
|---|---|---|---|
| m1 | reason taken from the argument (`row = oracle.row(fixture_name)`) | KILLED, 2 failed | `test_revoked_denial_is_read_from_the_observation` → `E   AssertionError: failure_reason: denied: membership-revoked`; `test_denial_reason_never_comes_from_the_argument` → `E   AssertionError: failure_reason: denied: event-stale` |
| m2 | the denial mode requires the whole bundle (`_check_bundle_uncapped(root, anchors)` first) | KILLED, 10 failed | `test_a_broken_sibling_leg_does_not_change_the_denial_verdict[neg-stale-...]` → `E   assert (1, "failure_...json']\n", '') == (1, 'failure_...-stale\n', '')` (x4); the mismatch tests → `E   AssertionError: failure_reason: blanket-rejection: reasons [...]` (x4); blanket[neg-unauthorized]; the white-box test |
| m3a | spec: one seed leg dropped (4 negative legs incl. blanket) | KILLED, 3 failed | `test_spec_negative_legs_meet_the_registry_floor_with_the_seed_reasons` → `E   AssertionError: assert ['blanket-rej...ture-invalid'] == ['blanket-rej...ture-invalid']`; `test_spec_denial_legs_run_verbatim_and_reach_the_checker` → `E   AssertionError: assert 3 == 4`; `test_spec_gains_one_denial_leg_per_seed_fixture_in_seed_order` |
| m3b | spec: three negative legs in all (2 seed + blanket) | KILLED, 3 failed | `test_spec_negative_legs_meet_the_registry_floor_with_the_seed_reasons` → `E   AssertionError: (3, 4)`; the verbatim test → `E   AssertionError: assert 2 == 4`; the shape test |
| m4 | exit 0 on a proven denial | KILLED, 12 failed | `test_denial_mode_proves_each_negative_leg_of_the_pass_bundle[neg-stale]` → `E   AssertionError: assert (0, 'failure_...-stale\n', '') == (1, 'failure_...-stale\n', '')` (all 7 fixtures), the 4 independence tests, blanket[neg-unauthorized] |
| m5 | `pos-allowed` accepted by `--denial` (`not in LEG_NAMES`) | KILLED, 2 failed | `test_denial_usage_refusals_exit_64[pos-allowed]` → `E   AssertionError: assert (1, 'failure_...d.json\n', '') == (64, '', 'usa...ence-root>\n')`; `[anchored-pos-allowed]` → `E   TypeError: argument of type 'NoneType' is not iterable` |
| m6 (extra) | the `denied:` escape removed | KILLED, 5 failed | the 4 `test_a_failure_line_never_carries_the_named_reason[...]` + `test_a_replay_receipt_quoting_the_reason_is_not_a_proven_denial` |
| m7 (extra) | `_check_named_observable` skipped in the denial mode | KILLED, 3 failed | `test_denial_mode_refuses_another_classes_observable[neg-unauthorized/neg-bad-signature/neg-stale]` (the leg still fails at `_observed_row`, so no reason prints; the test pins WHICH gate fires) |
| m8 (extra) | `_check_duplicate_receipt` skipped in the denial mode | KILLED, 2 failed | `test_denial_mode_refuses_another_classes_observable[neg-replayed-...]`, `test_a_replay_receipt_quoting_the_reason_is_not_a_proven_denial` |
| m9 (extra) | the membership-receipt tie-break inverted | KILLED, 5 failed | `test_denial_mode_proves_each_negative_leg_of_the_pass_bundle[neg-unauthorized]`, `[revoked]`, the white-box test, independence[neg-unauthorized], blanket[neg-unauthorized] |

A note on m1. Over the four SEED legs alone, m1 is black-box equivalent: `_check_named_observable` / `_check_duplicate_receipt`
already bind the observation to the named row before the reason is read. Two tests kill it. The first is black-box, through the
revoked leg: the bundle never reads revoked's relay text, so only `_observed_row` catches a stale text there. The second isolates the
gate: it patches `_check_named_observable` out on neg-stale.

## 7. DISCREPANCIES

- **D1 — item 5 turns an out-of-boundary test red by design. The coordinator's same-commit edit is required.**
  `test_spec_negative_leg_counts_meet_the_registry_floor_except_the_declared_shortfall` in tests/test_validate_ledger.py:521-534 asserts
  `short == {"S0-02": (1, 4)}`. Its docstring names this landing ("When they land this table becomes empty by a deliberate edit —
  never by a skip"). Evidence on the changed spec:
  ```
  $ python3 -m pytest "tests/test_validate_ledger.py::test_spec_negative_leg_counts_meet_the_registry_floor_except_the_declared_shortfall" -q
  rc=1
  E       AssertionError: {}
  E       assert {} == {'S0-02': (1, 4)}
  ```
  The fix is outside my boundary and NOT made: `assert short == {}, short` at line 534, plus the docstring's tense. Without it, the
  stage0-ci `tests` job goes red (AF-AP-126).
- **D2 (resolved in boundary).** `test_spec_negative_leg_reason_is_the_exact_observed_line` asserted
  `assert len(neg) == 1` over ALL negative legs (T2@8d8c97e:964-965). Its selector is narrowed to the blanket leg (`"--synthetic-root" in leg["cmd"]`, T2:964-967). The
  `assert len(neg) == 1` and every other line are kept. Not skipped, not deleted.
- **D3 — the brief's lint gate does not run as written.** `python3 scripts/lint_delta.py` exits 2 (it requires `--staged` or `--base`).
  I ran `--base HEAD` and `--base 8d8c97e` (pasted above); `--staged` is not available to a lane that may not `git add`.
- **D4 — two interpretations, FLAGGED, not blocking:** P3 (revoked mirrors the bundle's skip of the named-observable check) and P5 (the
  one usage line names `--denial` for every refusal, including refusals without `--denial`). Neither touches a spec leg or a verdict line.

## 8. Adjacent defects (reported, NOT fixed)

- **A1 — the bundle mode never grades the revoked leg's relay text.** In `_check_bundle_uncapped`, revoked is excluded from the
  distinctness keys (`DISTINCT_FIXTURES`) and skipped by the named-observable loop. `_observe_all` only needs SOME known observable. So
  a revoked receipt that carries another class's text passes. Verified on a scratch copy at both revisions:
  ```
  $ (bundle mode) revoked receipt carries the STALE text
  PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; ...        rc=0   (the PIN's C, run from the scratch copy)
  PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; ...        rc=0   (the changed C)
  $ (denial mode) --denial revoked on the same copy
  failure_reason: revoked: the observed denial matches the oracle's neg-stale row, not revoked's     rc=1
  ```
  Consequence: assertion 2 (revocation) can PASS at mint with a relay refusal that is not the membership refusal. The four new spec legs
  do not include revoked, so they do not close this. Fix candidate, for a later brief: grade revoked's text in the bundle mode, for
  example with `_observed_row` or `_check_named_observable` for revoked.
- **A2 — the echo sweep for the class "a failure line that quotes evidence, graded by a substring matcher".** Across every
  `proofs/S0-*/spec.json`, the four new S0-02 legs are the ONLY negative legs that read live, not-yet-captured evidence
  (`proofs/S0-02/evidence`). Every other negative leg reads committed fixtures. The exception is the S0-01 golden negative
  (`proofs/S0-01/evidence/golden/negative`), which is committed and attested, so its exposure is at review time, not at mint time. Not
  checked: whether S0-01's failure lines quote evidence text. Proposed registry row (I cannot write `docs/INCIDENT-LOG.md`): *a
  negative leg graded by `proof-runner`'s substring match over output that quotes attacker-influenced evidence can read a planted
  reason as a proven denial. Signature: a spec negative leg over a non-fixture path whose checker interpolates evidence into its
  `failure_reason:` line. Fix: escape the reason token in failure lines (B11, `_denial_main`).*

## 9. What this does NOT prove, and NOT done

- **NOT proven: the four legs over live evidence.** They run over the live evidence only at mint time, after the capture. Today
  `proofs/S0-02/evidence` is absent and each spec leg defers (`test_spec_denial_legs_run_verbatim_and_reach_the_checker`: rc in (1, 2),
  empty stderr). Proven here: the synthetic pass bundle (each seed reason printed, rc 1) and hostile copies (mismatch, quoting,
  independence, blanket).
- NOT done: D1's edit (outside my boundary). No commit and no push (lane rule; the coordinator commits through `safe_commit.sh`).
- NOT run: the full tree, the PC gate (no bridge use in this lane), the advisory instruments (sentrux, slopo), and a GitNexus reindex.
  Run: T2 twice, the single D1 test, and the B11 selections.
- NOT written: the A2 registry row (`docs/INCIDENT-LOG.md` is outside my boundary). The `/bug-echo` skill was not invoked; the sweep in
  A2 was done by hand over every spec.
- NOT fixed: A1.
- `--denial` also accepts `neg-self-authored`, `revoked` and `neg-not-allowlisted` (item 2). They are tested over the pass bundle only,
  plus the revoked mismatch test. They are not spec legs.

## 10. Evidence tiers

- VERIFIED (a primary source or a probe from this session, pasted): the premise; the red-green; gates 1-6; the schema check;
  `detect_changes`; both screens; mutants m1-m9; D1's red; A1 at both revisions; the A2 sweep.
- INFERRED (read from code, not executed end to end): `proof-runner` records each new leg's line as
  `observed_reason` (scripts/proof-runner:192-203), and validate-ledger binds it (`negative-controls-short`, scripts/validate-ledger:297-324). No mint was run. A live-evidence mint yields the same
  per-leg verdict as these synthetic runs, because the functions are shared.
- ASSUMED: the PC venue has PyYAML for T2's module-level seed read (`_seed_denials`). CI installs `PyYAML>=6.0`
  (`.github/workflows/stage0-ci.yml:40`), and four other test files import yaml at module level. The PC venv was not probed.

## 11. Self-attack — the three likeliest ways this change is wrong

1. **The extraction changed the bundle mode.** Ruled out: the moved statements are verbatim (the diff shows only the new `def` line, the
   docstring and `return root, identities`). The pass-bundle stdout sha256 is identical before and after (`74efad21…`), the blanket
   output is `cmp`-identical, the 201 pre-existing T2 tests pass, and `test_bundle_mode_stdout_is_unchanged_byte_for_byte` was green
   BEFORE the change (its golden predates it).
2. **The denial mode proves a denial it should not (a hollow green).** Checked with mutants m1 and m6-m9 (all killed) and with hostile
   controls: another class's text on each seed leg, the reason planted where a failure quotes it, the committed blanket bundle, and
   every sibling broken. Residual: the mode is only as strong as `_check_leg` / `_check_replay`, and a gap there passes through, as A1
   shows for the bundle. The denial mode's `_observed_row` closes A1 for `--denial revoked` only. A second residual, INFERRED and not
   probed exhaustively: an UNCAUGHT exception exits 1 with a traceback on stderr that is not escaped. That traceback would need an
   exception message quoting evidence that holds the reason text. I traced the exception paths I could find (type errors, index
   errors, JSON and Unicode errors); none quotes evidence strings, but the list is not proven complete.
3. **The spec legs misbehave under the real runner.** Mitigated: the verbatim-argv test runs the spec's exact argv from the repo root
   (no usage refusal, empty stderr). The proven line equals `failure_reason: <spec reason>` exactly, which is what
   `observed_reason` matches. C reads no environment (T2 bans `os.environ`), so `_clean_env` cannot change the verdict. Each leg takes
   about 1.1 s under its `timeout_s` 120 (the checker's own cap is 90 s). The leg order means the four legs execute only after a
   passing positive leg over the same evidence.
