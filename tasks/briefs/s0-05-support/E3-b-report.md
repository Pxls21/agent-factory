# E3-b — report (S0-05: collector allow-set, per-service C0 paths, preflight = checker predicate, a stop stops)

Status: COMPLETE — G, A, P, C and R1-R4 built and gated in the sandbox; RED on the PIN, GREEN `251 passed` twice as root and
`204 passed, 47 skipped` as nobody on the final bytes; 18 of 18 mutants killed (B1-B14 + 4 extras). Nothing ran on the PC.
report_lint (final, round 3 of at most 3): `87 refs — OK 85, NEAR 0, MISS 0, UNCHECKABLE 2, UNRESOLVED 0 (worktree)`;
round 1 read `94 refs — OK 50, NEAR 5, MISS 25, UNCHECKABLE 14` (refs without a backticked identifier on their line, E3-era
lines written bare, and two RED-run line numbers the R2 fixture moved), round 2 `87 refs — OK 82, NEAR 0, MISS 2, UNCHECKABLE 3`.
The two UNCHECKABLE are the premise probe's own printed label `(netns_lib.sh:83)`, the PIN's line, pasted verbatim.
Lane s0-05-e3b, sandbox, root, shared tree. PIN `148e38d`. Key: RC = `proofs/S0-05/run_canaries.sh`,
C = `proofs/S0-05/check_egress.py`, PC = `proofs/S0-05/tools/pc/run_s0_05_units.sh`, L = `proofs/S0-05/netns_lib.sh`,
CAN = `proofs/S0-05/canaries/c0_allowed_target.sh`, T = `tests/test_s0_05_egress.py`. Nothing in this lane ran on the PC.

## 1. PREMISE re-measured (item 1) — MATCH, contract stands

Run 2026-09-23 07:13Z, sandbox root. Origin tip `bee499f` (the dispatch named 05c90dc; one more transcripts commit
landed since), local HEAD `7fc99c8` (a coordinator wiki commit). `git diff --name-only 148e38d HEAD`: docs/INCIDENT-LOG.md,
tasks/briefs/ci/VERIFY-CI-GATE-brief.md, tasks/briefs/s0-05-support/E3-b-brief.md, todo/BUILD-TASKLIST.md,
transcripts/sandbox/chat-2026-09-23.md, wiki/topics/live-state.md — none in this boundary.

```
$ git diff --stat 148e38d HEAD -- proofs/S0-05 tests/test_s0_05_egress.py | wc -l        -> 0
$ git diff --stat HEAD -- proofs/S0-05 tests/test_s0_05_egress.py | wc -l                 -> 0
$ sha256[:16] lines, PIN bytes (git show 148e38d:<f>) | the working tree
44b1428b431303a1 139 proofs/S0-05/run_canaries.sh | worktree 44b1428b431303a1 139
df3ad6fed3aa5067 485 proofs/S0-05/check_egress.py | worktree df3ad6fed3aa5067 485
ffb3453a17427a63 508 proofs/S0-05/tools/pc/run_s0_05_units.sh | worktree ffb3453a17427a63 508
2710a809b664ea7d 15 proofs/S0-05/canaries/c0_allowed_target.sh | worktree 2710a809b664ea7d 15
87e6044a0567a15f 2550 tests/test_s0_05_egress.py | worktree 87e6044a0567a15f 2550
ece94bc0789863d4 401 proofs/S0-05/netns_lib.sh | worktree ece94bc0789863d4 401
$ the brief's grep line maps (run_canaries.sh, runner, checker, c0, test call sites, test pins, lib, checker grammar)
  -> every line identical to the brief's block (the same line numbers, all at the PIN 148e38d: run_canaries.sh 25-130,
     the runner 283-508, the checker 94-444, c0 9 and 15, the test file 261-1571, netns_lib.sh 82-200)
digest(one entry) : d251ea78bc708b35
digest(two entries): e086277caab22ed3
equal: False
check_positive_control params: ['records', 'unit']
seven committed bundles: allowed == C0 targets, one entry each (bare-unshare, gate-off, mechanism-sandbox: 10.201.136.1:12800;
  synthetic-pass curl + hermes-acp, synthetic-uid0 curl + hermes-acp: 10.201.7.1:20128)
+ ALLOWED_PORT=9223372036854775807
+ BLOCKED=10.201.130.1:-9223372036854775808
rc=64
$ trap cleanup EXIT INT TERM; kill -TERM $$  -> cleanup-ran / continued-after-TERM / cleanup-ran / rc=0
$ run_canaries.sh u s0-05-e3b-none '10.0.0.1:a[$(touch …)]'     -> line 29: a: unbound variable, rc=1, did not run, no evidence dir
$ run_canaries.sh u s0-05-e3b-none '10.0.0.1:NS[$(touch …)]'    -> line 29: s0: unbound variable, rc=1, the injected command RAN, no evidence dir
$ run_canaries.sh u s0-05-e3b-none '10.0.0.1:VENUE[$(touch …)]' -> line 29: VENUE: unbound variable, rc=1, did not run, no evidence dir
$((010 + 1)) = 9
bash: line 1: 08: value too great for base (error token is "08")
checker _split_ip_port: ('10.201.7.1', '٢٠١٢٨')
bash[C] library port regex (netns_lib.sh:83): no match
bash[C.UTF-8] library port regex (netns_lib.sh:83): no match
183 tests collected in 0.09s
$ locale -a -> C, C.utf8, POSIX (the only locales this sandbox has)
```

The two PC probes (OmniRoute `/api/health` 200 application/json, `/v1/models` 401; the relay `/health` 200 text/plain,
`/v1/models` 404; 2026-09-23 06:55-06:57Z) are the coordinator's, quoted from the brief, not re-run (no bridge use here).
`proofs/S0-05/__pycache__/` (gitignored) predates this lane (05:53Z); every later Python run here uses `-B`.

## 2. Design decisions made inside the contract (measured first)

- R4 trap semantics, measured in this sandbox (bash 5.2.21): a probe with `trap cleanup EXIT; trap 'exit 130' INT;
  trap 'exit 143' TERM` and a foreground `sleep` loop, signalled BY PID: SIGTERM -> `rc=143`, SIGINT -> `rc=130`, each
  printing `cleanup-ran` once and never `continued-to-end` (a `false` as cleanup's last command does not change the
  status). So a pid-directed stop is enough for the tests; the trap runs once the foreground child returns.
- G, ASCII under any locale: every class in the bash predicate is an explicit list (`[0123456789]`), never a range, so
  no locale can widen it; the checker uses `[0-9]` (a code-point range in Python) with `fullmatch` (Python's `$` also
  matches before a trailing newline — the NL-at-the-end row). Port grammar in the checker is `(0|[1-9][0-9]{0,4})` so
  port 0 keeps today's `out of range` text; a leading-zero octet or port reads `is not <ipv4>:<port>`.
- C: two independent halves — every allowed entry appears EXACTLY once among the C0 targets (`targets.count(a) == 1`),
  and every C0 target is an allowed entry — plus today's per-record predicate on every C0 record, factored into
  `c0_proves(record)` so the runner's preflight grades with the checker's own predicate (R2). Comparison by `==` over
  lists (no hashing, no sorting), so any JSON value in `allowed` or `target` compares without a crash.
- R2: the preflight runs the REAL `canaries/c0_allowed_target.sh` inside the namespace, wrapped with the canaries' scrub
  list read from `canaries/_emit.sh` (the same `env -u …` wrapper `run_canaries.sh` applies), and grades its record with
  `check_egress.c0_proves`. Not 2xx = rc 0 with an HTTP code outside 2xx; anything else that fails is "no HTTP answer"
  (today's unreachable texts, fail closed).
- Two existing tests whose FIXTURES item C makes invalid (assertions kept, fixtures adapted, item C named at the site):
  T `test_a_widened_allow_list_changes_the_expected_digest` (a second allowed entry with no C0: under C the positive
  control fails first, so the fixture gains the C0 for it and still reads `egress-rules-unpinned`), and
  T `test_the_pass_line_counts_units_not_records` (its duplicated C0 is now one of C's refusal shapes; the fixture is a
  real two-entry unit, still `positive controls 1/1`). See DISCREPANCIES.

## 3. RED — the new and changed tests against the PIN production bytes (pasted)

The five production files were byte-identical to the PIN (digests in section 1) when these ran; only T had changed.

```
$ date -u; pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3b/red/bt -rf --tb=line \
    -k "e3b or test_runner_live_leg or test_x4_runner_cleanup_reaps or pair_leg or pass_line_counts or widened_allow_list"
2026-09-23T07:32:17Z
63 failed, 10 passed, 178 deselected in 125.57s (0:02:05)
pipestatus=1
```

The first assertion that failed, per test (from `--tb=line`; `...` = cut by pytest, nothing edited):

| Test (T) | Failure on the PIN | Which measured PIN behaviour |
|---|---|---|
| `test_runner_live_leg` (the `asked` assertion) | `T:1217: AssertionError: ['10.201.107.2 /v1/models', '10.201.107.2 /v1/models']` | #2 C0 and the preflight ask `/v1/models` (a real-shaped OmniRoute answers 401 there) and the preflight still passed |
| `test_d_pair_leg_reaches_the_relay_through_the_dnat` (the `sorted(seen)` assertion) | `T:2519: AssertionError: ['10.201.219.2 /v1/models', '10.201.219.2 /pair-own-socket']` | #2 the relay was asked `/v1/models` (the real relay answers 404) |
| `test_x4_runner_cleanup_reaps_its_own_namespace_at_exit` (`runner.returncode == 143`) | `T:1942: AssertionError: (1, '=== hermes-acp: namespace s0-05-hermes-acp, allowed 10.201.107.1:18092 ===` | #4 rc 1: after SIGTERM the runner went on to its checker |
| `test_e3b_r4_sigint_stops_the_runner_with_130` (now T:2946, `runner.returncode == 130`) | at the RED run's line 2945: `AssertionError: (1, '=== hermes-acp: namespace s0-05-hermes-acp, allowed 10.201.107.1:18124 ===` | #4 the same for SIGINT |
| `test_e3b_r4_a_stop_in_the_first_leg_starts_no_second_leg` (now T:2985, `runner.returncode == 143`) | at the RED run's line 2984: `AssertionError: (1, '=== hermes-acp: namespace s0-05-hermes-acp, allowed 10.201.107.1:18125 ===` | #4 a two-unit run went on after the stop |
| `test_e3b_r2_a_health_path_answering_401_launches_nothing` | (rerun `-vv`, stand-in 401 on BOTH paths) `{'status': 'run'} != {'status': 'not-run'}` / `{'note': 'contained live unit'}` | #3 the preflight passed an HTTP 401 and the unit launched |
| `test_e3b_a_a_two_entry_run_records_the_whole_allow_set` | `T:2813: AssertionError: {'allowed': ['10.201.193.1:18120/health,10.201.193.1:18130'], 'gate': 'enabled', ...}` | #1 the whole list recorded as ONE allowed entry |
| `test_e3b_p_the_c0_record_carries_the_path_it_asked` | `T:2844: AssertionError: {'canary': 'C0', 'detail': 'curl exit 0, HTTP 200', 'http_status': 200, 'kind': 'http-get', ...}` | P: the record carries no path |
| `test_e3b_c_the_positive_control_is_per_allowed_entry` ×3 (`allowed-entry-without-c0`, `c0-target-outside-the-allow-set`, `two-c0-for-one-target`; `result.returncode == 1`) | `T:2893: AssertionError: NOT run: buzz-acp — live unit runs on the PC ...` (the checker's stdout of an rc-0 PASS) | C: only the per-record predicate was graded; all three shapes PASSED |
| `test_e3b_a_an_injected_port_never_runs` (the `_NOT_ENTRY` assertion) | `T:2768: ... returncode=1, ... stderr='.../run_canaries.sh: line 29: s0: unbound variable` | #5 the arithmetic ran on the raw port (section 1: the command RAN) |
| `test_e3b_a_a_bad_argument_is_refused_before_anything` ×22 | e.g. `line 25: 3: allowed ip:port` (empty), `returncode=3 ... cannot read the OUTPUT DROP counter` (leading comma, overflow, duplicates, blocked entries, 65536), `operand expected (error token is ",")` (trailing comma), `value too great for base (error token is "080")`, `line 29: health: unbound variable` (paths), `venue must be sandbox or pc, got 'x'` (the order rows) | #5 arithmetic on the raw input, no list, no validation of 5, venue checked before 5 could fail |
| `test_e3b_a_a_valid_argument_list_reaches_the_namespace` ×2 (`two-entries-a-path`, `path-of-63-chars`) | `line 29: health: unbound variable` / `... (error token is "...~._-/aZ09")` | #5 a VALID path broke the PIN's arithmetic |
| `test_e3b_g_one_allow_entry_rule_in_the_library_and_the_checker` ×29 | every row: `'library[C]': "rc=127 ... egress_allow_entry_ok: command not found"`; and the checker half diverged on 5 rows: `('010.201.7.1:20128', {'checker': True, ...`, `('10.201.7.1:080', {'checker': True, ...`, `('10.201.7.1:٢٠١٢٨', {'checker': True, ...`, `('١٠.201.7.1:20128', {'checker': True, ...`, and nl-end `{'checker': True} != {'checker': False}` | #6 no shared predicate; the checker's `\d` and `$` accepted Arabic-Indic digits, leading zeros and a trailing newline |

The 10 that pass on the PIN, by design: `test_e3b_g_egress_ns_create_checks_every_entry_by_the_one_rule` ×4 (the B14 guard: the
PIN's inline rule already checked every entry), `test_e3b_a_a_bad_argument_is_refused_before_anything[order-6-last]` (the venue
text is kept), `test_e3b_a_a_valid_argument_list_reaches_the_namespace[one-entry]` and `[paths-explicit-blocked]` (no
arithmetic when argument 5 is given), `test_e3b_c_the_positive_control_is_per_allowed_entry[second-c0-not-2xx]` (the PIN graded
every record's predicate), and the two fixture-adapted tests `test_the_pass_line_counts_units_not_records` and
`test_a_widened_allow_list_changes_the_expected_digest`. None is an import or collection error: the file collected 251.

## 4. What changed per item (final bytes)

| Item | Change | Where |
|---|---|---|
| G | `egress_allow_entry_ok <entry>`: the one rule as a SILENT predicate; explicit ASCII lists (`[0123456789]`), the port digit-bounded (`^[1-9][0-9]{0,4}$`) before `[ -le 65535 ]`; `egress_allow_entry_ok()` | L:77 (API line L:18) |
| G | `egress_ns_create` calls it for every entry (`egress_allow_entry_ok "$entry"`), same text, status 64 and position (before the claim) | L:97 |
| G | checker grammar: `_OCTET` + `IPV4_PORT` with `[0-9]`, matched by `fullmatch` (was `\d` + `$`); both refusal texts kept | C:101-102, C:207 |
| C | `c0_proves(record)`: today's per-record predicate, factored out (the runner's preflight grades with it) | C:273 |
| C | `check_positive_control(records, unit, allowed)`: every allowed entry exactly once (C:296, `targets.count(entry)`), nothing else (C:298, `target not in allowed`), every record `c0_proves` (C:301) | C:284 |
| C | PHASE 2's call passes `gates[unit]["allowed"]`; docstring step 2 says "per entry" (the phase order unchanged) | C:470, C:22-24 |
| A | header: `<allowed>` = the whole allow-set, entries `<ip>:<port>[<path>]`, `[blocked]` default | RC:5-13 |
| A | validation of 3, 5, 6 in that order before any arithmetic, namespace access, file or canary: `refuse` (exit 64), the entry loop (empty / rule / path / listed twice), blocked explicit or default (65536 refusal), blocked-in-set, then the venue | RC:39-62 |
| A | C0 once per entry, in order, its ip:port as target and its path passed explicitly (`/v1/models` when none): `for i in "${!ALLOWED[@]}"` | RC:116-117 |
| A | gate.json `allowed` = every ip:port in order, no paths | RC:159, RC:166 |
| P | the C0 record carries `path=<path>` (the one change in the file): `emit_canary C0` | CAN:15 |
| R1 | `OMNI_PROBE_PATH=/api/health`, `RELAY_PROBE_PATH=/health`, the PC measurement cited; `probe_paths[i]` rides beside `allowed[i]` (create still gets ip:port only) | PC:81-82, PC:384-386 |
| R2 | `_c0_preflight`: the real C0 canary in the namespace under the canaries' scrub (read from `_emit.sh`, fail-loud if unreadable), graded by `check_egress.c0_proves`; `ok` / `not-2xx <code>` / `unreachable` | PC:274-298 |
| R2 | the preflight loop (`_c0_preflight`); the new `positive-control-not-2xx` stderr and row; the unreachable texts kept | PC:410-432 |
| R3 | the collector gets every entry with its path, comma-joined in the runner's order (`"$entries"`) | PC:505-506 |
| R4 | `trap cleanup EXIT`, `trap 'exit 130' INT`, `trap 'exit 143' TERM` | PC:334-336 |
| limits | DECLARED LIMITS 5 (the probe paths are facts about the PC today; fail closed; one-line constant) and 6 (a health 2xx proves reach, not the model API: S0-03); the PREFLIGHT paragraph names the not-2xx row | PC:49-54, PC:12-13 |

Tests (T), one per line:
- `_listener` gains the per-path `status` map: `def _listener` T:1589, `STATUS.get(self.path, 200)` T:1604.
- new `test_e3b_g_one_allow_entry_rule_in_the_library_and_the_checker` ×29 T:2663 (table `_G_ROWS` T:2617).
- new `test_e3b_g_egress_ns_create_checks_every_entry_by_the_one_rule` ×4 T:2677.
- new `test_e3b_a_a_bad_argument_is_refused_before_anything` ×23 T:2746 (table `_A_REFUSALS` T:2706).
- new `test_e3b_a_an_injected_port_never_runs` T:2760.
- new `test_e3b_a_a_valid_argument_list_reaches_the_namespace` ×4 T:2780.
- new `test_e3b_a_a_two_entry_run_records_the_whole_allow_set` T:2792.
- new `test_e3b_p_the_c0_record_carries_the_path_it_asked` T:2832.
- new `test_e3b_c_the_positive_control_is_per_allowed_entry` ×4 T:2872 (fixture `_two_entry_bundle` T:2849).
- new `test_e3b_r2_a_health_path_answering_401_launches_nothing` T:2898.
- new `test_e3b_r4_sigint_stops_the_runner_with_130` T:2929.
- new `test_e3b_r4_a_stop_in_the_first_leg_starts_no_second_leg` T:2958.
- changed `test_runner_live_leg` T:1078: a real-shaped OmniRoute stand-in (401 on `/v1/models`); the two requests asked
  `/api/health`, and C0's target, path, rc and 2xx (the `asked` assertion T:1217).
- changed `test_x4_runner_cleanup_reaps_its_own_namespace_at_exit` T:1916: exit 143, no checker, no units.json, no census file
  (`runner.returncode == 143` T:1942).
- changed `test_d_pair_leg_reaches_the_relay_through_the_dnat` T:2467: real-shaped relay and OmniRoute stand-ins; the relay-log
  expectation `/v1/models` -> `/health` (`sorted(seen)` T:2519, the one CHANGED expectation, R1); plus gate.json allowed, two C0
  with paths, `check_positive_control` and `check_runtime_and_rules` on the real bundle.
- fixture-adapted (section 2): `test_a_widened_allow_list_changes_the_expected_digest` T:427.
- fixture-adapted (section 2): `test_the_pass_line_counts_units_not_records` T:621.
No existing assertion was removed or weakened.

## 5. GREEN (pasted)

```
$ date -u; pytest ... -k "e3b or test_runner_live_leg or test_x4_runner_cleanup_reaps or pair_leg or pass_line_counts or widened_allow_list"
2026-09-23T07:40:46Z
73 passed, 178 deselected in 89.24s (0:01:29)
pipestatus=0
$ census (between runs): ip netns list -> (empty); ip -o link show type veth -> (empty);
  iptables -t nat -S PREROUTING -> -P PREROUTING ACCEPT; ls -A /etc/netns -> (empty); ls -A /run/s0-05-egress -> (empty)
$ date -u; pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3b/green/bt2   (the whole file, root)
2026-09-23T07:42:22Z
251 passed in 201.94s (0:03:21)
pipestatus=0
$ pytest ... -k pair_leg -rP        (the captured stdout of the real pair leg)
the full checker's first line on the pair bundle: units-manifest-invalid: buzz-acp override present
1 passed, 250 deselected in 37.91s
```

What that first line is, and why: it is the runner's own `check_egress.py` run on the evidence root the pair leg wrote. The bundle
says venue `pc` and its units.json row records the pin OVERRIDE the sandbox used to put stand-ins in place of the pinned binaries
(E3 A1), so PHASE 1b refuses it as a live claim — by design, a stand-in run can never pass as the live leg. PHASE 2 is therefore
never reached on this bundle by the full checker, which is why the test also calls the two PHASE 2 checks directly on the same
bundle: `check_positive_control(..., gate["allowed"]) == 1` (both entries, one C0 each, both 2xx) and `check_runtime_and_rules`
returned `gate-fired: buzz-acp ...` (the recorded two-entry rules hash to the checker's derivation from `[relay, OmniRoute]`) —
the `egress-rules-unpinned` E3 measured on this leg (its section 9, DISCREPANCY 1) is gone.

## 6. Mutant table (scratch copies only; harness `mutate.py` + spec `mutants.json` in the scratchpad's `e3b-lane/`)

Each mutant: the base tree (the 51 tracked inputs — `proofs/S0-05`, `proofs/schemas`, `proofs/S0-01/pins.py`, the test file,
`tests/conftest.py`, `pyproject.toml` — copied from the working tree, the six changed files byte-checked against it) copied
to `mut/<id>/`, ONE exact replacement (refused unless the old text occurs exactly once), `bash -n` or `ast.parse`, the WHOLE
test file collected (must read `251 tests collected`), the named killers run, the tree deleted. The shared tree was never
mutated. AF-AP-138 first — every killer on the UNMUTATED base:

```
$ mutate.py base      (2026-09-23T07:49:17Z)
base: 51 files copied from the working tree
UNMUTATED base, every killer: 67 passed, 184 deselected in 88.81s (0:01:28) | rc=0
```

(A first batch run at 07:50:53Z read `INVALID` for all 11 of its mutants: the harness's collection check matched the test
NAME `test_a_required_unit_that_was_never_collected_is_red` instead of the summary line. It failed closed — nothing was
counted — and was fixed to match `^\d+ tests? collected` before the batch was rerun.)

| Mutant | What it does | Compiles | Collected | Killed by (the pasted assertion) |
|---|---|---|---|---|
| B1 | gate.json records only the first entry (`allowed.split(",")[:1]`) | bash -n rc=0 | 251 | `test_d_pair_leg_reaches_the_relay_through_the_dnat` (`{'allowed': ['10.201.219.1:3999'], ...}`), `test_e3b_a_a_two_entry_run_records_the_whole_allow_set` |
| B2 | C0 only for the first entry (`for i in 0`) | bash -n rc=0 | 251 | `test_d_pair_leg_...` (`['10.201.219.2 /api/health'] == ...`: OmniRoute asked once), `test_e3b_a_a_two_entry_run_...` (one C0) |
| B3 | the path not passed to C0 (the canary's default asked) | bash -n rc=0 | 251 | `test_runner_live_leg` (`['10.201.107.2 /api/health', '10.201.107.2 /v1/models']`), `test_e3b_a_a_two_entry_run_...` |
| B4 | the collector's validation removed, the raw arithmetic back | bash -n rc=0 | 251 | `test_e3b_a_an_injected_port_never_runs`, `test_e3b_a_a_bad_argument_is_refused_before_anything` ×22 (rc 3 / wrong text) |
| B5 | the duplicate refusal removed | bash -n rc=0 | 251 | `...refused_before_anything[listed-twice]`, `[listed-twice-other-path]` (rc 3) |
| B6 | the blocked-in-set refusal removed | bash -n rc=0 | 251 | `...[blocked-explicit-in-set]`, `[blocked-default-in-set]` (rc 3) |
| B7 | the checker's "nothing else" half removed | ast.parse rc=0 | 251 | `test_e3b_c_the_positive_control_is_per_allowed_entry[c0-target-outside-the-allow-set]` (rc 0 PASS) |
| B8 | the checker's "every allowed entry exactly once" half removed | ast.parse rc=0 | 251 | `test_e3b_c_...[allowed-entry-without-c0]`, `[two-c0-for-one-target]` (rc 0 PASS) |
| B9 | the checker's grammar back to `\d` (the PIN regex; fullmatch kept) | ast.parse rc=0 | 251 | `test_e3b_g_one_allow_entry_rule_...[leading-zero-octet]`, `[leading-zero-port]`, `[arabic-indic-port]`, `[arabic-indic-octet]` (`{'checker': True, 'library[C]': False, ...}`) |
| B10 | the preflight back to any HTTP answer (rc 0 passes) | bash -n rc=0 | 251 | `test_e3b_r2_a_health_path_answering_401_launches_nothing` (the row) |
| B11 | the trap back to `EXIT INT TERM` | bash -n rc=0 | 251 | `test_x4_runner_cleanup_reaps_its_own_namespace_at_exit`, `test_e3b_r4_sigint_stops_the_runner_with_130`, `test_e3b_r4_a_stop_in_the_first_leg_starts_no_second_leg` (each `(1, '=== hermes-acp: ...`: rc 1, went on) |
| B12 | the runner passes only the OmniRoute entry (the PIN's :436) | bash -n rc=0 | 251 | `test_runner_live_leg` (C0 asked `/v1/models`), `test_d_pair_leg_...` (`['10.201.219.2 /health', '10.201.219.2 /pair-own-socket']`: the relay never got its C0) |
| B13 | C0's `path=` removed from its record | bash -n rc=0 | 251 | `test_e3b_p_the_c0_record_carries_the_path_it_asked`, `test_e3b_a_a_two_entry_run_...` |
| B14 | `egress_ns_create` checks only its FIRST entry with the shared predicate (the condition: any entry after the first is never checked) | bash -n rc=0 | 251 | `test_e3b_g_egress_ns_create_checks_every_entry_by_the_one_rule` ×4 (iptables `invalid port/service`, and rc 0 with a namespace BUILT for `010.201.1.1:80`) |
| X1 (extra) | P's path grammar not applied | bash -n rc=0 | 251 | `...refused_before_anything[path-with-space]`, `[path-64-chars]`, `[path-non-ascii]`, `[path-query]` |
| X2 (extra) | the default-blocked 65536 guard removed | bash -n rc=0 | 251 | `...[default-blocked-65536]` (rc 3) |
| X3 (extra) | the preflight asks the canary's default path | bash -n rc=0 | 251 | `test_runner_live_leg` (`stand-in record not found`: the real-shaped 401 refused it), `test_e3b_r2_...` (`['10.201.107.2 /v1/models'] == ['10.201.107.2 /api/health']`) |
| X4 (extra) | the venue checked BEFORE argument 3 (order 3, 5, 6 broken) | bash -n rc=0 | 251 | `...[order-3-before-5-and-6]`, `[order-5-before-6]`, `[order-default-5-before-6]` |

18 of 18 KILLED (14 of 14 required), 0 SURVIVED, 0 EQUIVALENT, 0 INVALID in the counted runs. Pasted harness summaries:

```
B4: bash -n rc=0 | 251 tests collected in 0.37s | -k 'test_e3b_a_an_injected_port_never_runs or test_e3b_a_a_bad_argument_is_refused_before_anything' -> 23 failed, 1 passed, 227 deselected in 0.93s | KILLED
B5: bash -n rc=0 | 251 tests collected in 0.35s | -k 'listed-twice' -> 2 failed, 249 deselected in 0.46s | KILLED
B6: bash -n rc=0 | 251 tests collected in 0.35s | -k 'blocked-explicit-in-set or blocked-default-in-set' -> 2 failed, 249 deselected in 0.41s | KILLED
B7: ast.parse rc=0 | 251 tests collected in 0.35s | -k 'test_e3b_c_the_positive_control_is_per_allowed_entry' -> 1 failed, 3 passed, 247 deselected in 0.55s | KILLED
B8: ast.parse rc=0 | 251 tests collected in 0.37s | -k 'test_e3b_c_the_positive_control_is_per_allowed_entry' -> 2 failed, 2 passed, 247 deselected in 0.56s | KILLED
B9: ast.parse rc=0 | 251 tests collected in 0.36s | -k 'test_e3b_g_one_allow_entry_rule_in_the_library_and_the_checker' -> 4 failed, 23 passed, 224 deselected in 0.56s | KILLED
B13: bash -n rc=0 | 251 tests collected in 0.37s | -k 'test_e3b_p_the_c0_record_carries_the_path_it_asked or test_e3b_a_a_two_entry_run_records_the_whole_allow_set' -> 2 failed, 249 deselected in 7.14s | KILLED
B14: bash -n rc=0 | 251 tests collected in 0.38s | -k 'test_e3b_g_egress_ns_create_checks_every_entry_by_the_one_rule' -> 4 failed, 247 deselected in 1.46s | KILLED
X1: bash -n rc=0 | 251 tests collected in 0.42s | -k 'path-with-space or path-64-chars or path-non-ascii or path-query' -> 4 failed, 247 deselected in 0.48s | KILLED
X2: bash -n rc=0 | 251 tests collected in 0.36s | -k 'default-blocked-65536' -> 1 failed, 250 deselected in 0.41s | KILLED
X4: bash -n rc=0 | 251 tests collected in 0.44s | -k 'order-3-before-5-and-6 or order-5-before-6 or order-default-5-before-6' -> 3 failed, 248 deselected in 0.41s | KILLED
B1: bash -n rc=0 | 251 tests collected in 0.36s | -k 'test_e3b_a_a_two_entry_run_records_the_whole_allow_set or test_d_pair_leg_reaches_the_relay_through_the_dnat' -> 2 failed, 249 deselected in 44.50s | KILLED
B2: bash -n rc=0 | 251 tests collected in 0.37s | -k 'test_e3b_a_a_two_entry_run_records_the_whole_allow_set or test_d_pair_leg_reaches_the_relay_through_the_dnat' -> 2 failed, 249 deselected in 44.27s | KILLED
B3: bash -n rc=0 | 251 tests collected in 0.37s | -k 'test_e3b_a_a_two_entry_run_records_the_whole_allow_set or test_runner_live_leg' -> 2 failed, 249 deselected in 44.34s | KILLED
B10: bash -n rc=0 | 251 tests collected in 0.41s | -k 'test_e3b_r2_a_health_path_answering_401_launches_nothing' -> 1 failed, 250 deselected in 37.39s | KILLED
B11: bash -n rc=0 | 251 tests collected in 0.35s | -k 'test_x4_runner_cleanup_reaps_its_own_namespace_at_exit or test_e3b_r4_sigint_stops_the_runner_with_130 or test_e3b_r4_a_stop_in_the_first_leg_starts_no_second_leg' -> 3 failed, 248 deselected in 6.23s | KILLED
B12: bash -n rc=0 | 251 tests collected in 0.35s | -k 'test_d_pair_leg_reaches_the_relay_through_the_dnat or test_runner_live_leg' -> 2 failed, 249 deselected in 76.14s (0:01:16) | KILLED
X3: bash -n rc=0 | 251 tests collected in 0.39s | -k 'test_runner_live_leg or test_e3b_r2_a_health_path_answering_401_launches_nothing' -> 2 failed, 249 deselected in 2.89s | KILLED
```

Census after the mutant runs: `ip netns list` empty, `ip -o link show type veth` empty, `iptables -t nat -S PREROUTING` ->
`-P PREROUTING ACCEPT`, `/etc/netns` and `/run/s0-05-egress` empty, route_localnet all/default 0, no stand-in or listener
process, `mut/` holds only `base`. Declared limit: kills were proven with the named `-k` selections, not a full-file run per mutant.

## 7. Gates (pasted, each with its invocation; ALL on the final bytes)

The final bytes (a comment-only edit to the runner's declared limit 6 landed after a first full gate round, so every gate was
run again on these):

```
5241b539c50a98b8 175 proofs/S0-05/run_canaries.sh
d39bb7b2665c6413 511 proofs/S0-05/check_egress.py
07a274102b1abf2a 578 proofs/S0-05/tools/pc/run_s0_05_units.sh
d2837c4d073bf398 410 proofs/S0-05/netns_lib.sh
888e9f3ebf27fb2e 15 proofs/S0-05/canaries/c0_allowed_target.sh
3050c242f33d38ee 2999 tests/test_s0_05_egress.py

$ mkdir -p /tmp/e3b/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3b/bt ; rm -rf /tmp/e3b/bt
Wed Sep 23 08:07:16 UTC 2026
ROOT1 pytest rc=0
251 passed in 195.02s (0:03:15)
Wed Sep 23 08:10:38 UTC 2026
ROOT2 pytest rc=0
251 passed in 198.19s (0:03:18)

$ rm -rf /tmp/e3bnr && mkdir -p /tmp/e3bnr && chmod 1777 /tmp/e3bnr && setpriv --reuid=65534 --regid=65534 --clear-groups env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3bnr/bt   (-rs added to read the skip reasons)
Wed Sep 23 08:14:08 UTC 2026
NONROOT pytest rc=0
204 passed, 47 skipped in 8.36s
     29 1x network-namespace legs need root + iproute2 + iptables; NOT run here — they run on a capable venue (this sandbox has them; CI does not)
      3 2x network-namespace legs need root + iproute2 + iptables; NOT run here — ...
      1 5x network-namespace legs need root + iproute2 + iptables; NOT run here — ...
      1 7x network-namespace legs need root + iproute2 + iptables; NOT run here — ...
   (29 + 6 + 5 + 7 = 47 skips, every one the declared NEEDS_NETNS reason: E3's 43 plus this lane's 4 namespace tests)

$ bash -n (the four shell files)
rc=0 proofs/S0-05/run_canaries.sh
rc=0 proofs/S0-05/netns_lib.sh
rc=0 proofs/S0-05/tools/pc/run_s0_05_units.sh
rc=0 proofs/S0-05/canaries/c0_allowed_target.sh
$ command -v shellcheck
(absent)
$ /root/venv-agent-factory/bin/python -m pyflakes proofs/S0-05/check_egress.py tests/test_s0_05_egress.py
rc=0
$ python3 scripts/ap_screen.py proofs/S0-05/check_egress.py
--- AP_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-32: 1
    proofs/S0-05/check_egress.py:230: return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()
rc=0
$ python3 scripts/ap_screen.py --tests tests/test_s0_05_egress.py
--- TEST_SCREEN over 1 path(s): 24 hits over 1 files ---
AF-AP-33: 21      (all 21 listed with --limit 30; every one a line of this lane naming /health or /api/health)
AF-AP-80: 2
    tests/test_s0_05_egress.py:1173: assert stat.S_ISREG(log.lstat().st_mode) and "stand-in: serving" in log.read_text()
    tests/test_s0_05_egress.py:2501: assert PAIR_KEY not in runner.stdout + runner.stderr + (evidence / "units.json").read_text()
AF-AP-59: 1
    tests/test_s0_05_egress.py:1147: standin_procs = subprocess.run(["pgrep", "-f", standin], capture_output=True, text=True)
rc=0
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 38 files scanned, clean
rc=0
```

Screen grades:
- AP-32 C:230 (`return hashlib.sha256`) — PRE-EXISTING, the unchanged `rules_digest` body, moved from C@148e38d:222 (E3's grade)
  by the lines G and C added above it.
- PRE-EXISTING, E3's three, moved by this lane's insertions above them:
  - AF-AP-80 T:1173 (`log.read_text()`; E3 graded it at T@148e38d:1164);
  - AF-AP-80 T:2501 (`PAIR_KEY not in`; E3 graded it at T@148e38d:2467);
  - AF-AP-59 T:1147 (`pgrep`; E3 graded it at T@148e38d:1138).
- AF-AP-33 ×21 — NEW, by design, not the class's defect. AF-AP-33 is "health-200 is not the right instance" (a squatting
  process answers health while the real service is wrong). R1 DECIDES that the preflight and C0 ask the health paths; these 21
  lines are the tests pinning that contract (which path was asked, which record carries it). The class's caveat is carried as
  declared limit 6 in the runner header (PC:52-54, now naming AF-AP-33): a health 2xx proves the namespace REACHES that
  ip:port — S0-05's positive-control claim — and says nothing about which instance answers or whether the model API behind it
  would serve the unit (S0-03). The production screen over the four shell files shows only the 8 hits the E3 pack showed at
  the start of this lane (AP-32 ×5, AF-AP-39, AF-AP-45, AP-2), line numbers moved.

Census, final (2026-09-23T08:14:24Z):

```
$ ip netns list                         -> (empty)
$ ip -o link show type veth             -> (empty)
$ iptables -t nat -S PREROUTING         -> -P PREROUTING ACCEPT
$ ls -A /etc/netns                      -> (empty)
$ ls -A /run/s0-05-egress               -> (empty)
$ sysctl -n net.ipv4.conf.{all,default}.route_localnet -> 0 / 0
$ stand-ins, listeners, runners, the trap probe (ps) -> (none)
$ ls -d /tmp/e3-* /tmp/e3bnr            -> No such file or directory (both)
```

Every namespace, veth, nat rule, sysctl, claim, `/etc/netns` entry and process this lane created was destroyed by name or pid
from its own record (the tests' `finally` blocks: `egress_ns_destroy <name>`, `_stop(<Popen>)`), never `pkill -f`.

## 8. The live-leg delta for the coordinator's operator recipe (E3 section 8 stands; NOTHING here ran on the PC)

- The invocation does not change: `bash proofs/S0-05/tools/pc/run_s0_05_units.sh "$EV" hermes-acp buzz-acp` with the same
  inputs. The stdout lines `=== <unit>: namespace <ns>, allowed <ip:port...> ===` are unchanged (ip:port only).
- The entries the runner now forms, with their probe paths (R1), which the preflight asks and the collector receives (R3):
  hermes-acp `10.201.107.1:20128/api/health`; buzz-acp `10.201.219.1:3999/health,10.201.219.1:20128/api/health` (relay, then
  OmniRoute). `egress_ns_create` still gets `10.201.219.1:3999 10.201.219.1:20128`. The C6 default for the pair is now
  `10.201.219.1:4000` (the FIRST entry's port + 1; it was `:20129` when the collector saw only OmniRoute).
- Expected evidence changes: `<unit>/gate.json` `allowed` = every ip:port (the pair: two); `canaries.jsonl` holds one C0 per
  entry, in order, each with `"path"`; for the pair the rule pin now holds (the PC:505-506 call carries the whole list).
- The new refusal row: `not-run|positive control not 2xx: <ip:port><path> answered HTTP <code> from <ns>` with stderr
  `positive-control-not-2xx: <unit> <ip:port><path> HTTP <code>` — the service answered, but not 2xx, on the probe path: a
  health path that moved (update `OMNI_PROBE_PATH` / `RELAY_PROBE_PATH`, PC:81-82) or a service refusing the probe. The
  namespace is destroyed and no unit launches. `not-run|positive control unreachable: <ip:port> not reachable from <ns>` keeps
  its meaning (no HTTP answer: bind, host firewall, relay down or the relay reach missing).
- Exit 143 (SIGTERM) / 130 (SIGINT): the operator stopped the run. `cleanup` ran once (the runner's own namespaces, relay reach,
  log readers and pipes gone); no further unit started; NO units.json, NO s0-01-census.json, NO checker. Whatever unit
  directories the evidence root holds are partial and never evidence: start again from a fresh `$EV`.
- What the checker can now say on the live leg: both units' C0 ask health paths the coordinator measured 200 from the host
  (06:57Z); whether they answer 200 FROM the namespaces (host firewall, the DNAT) is what the preflight measures. The pair can
  pass the positive control and the rule pin; the pair's relay handshake still needs the S0-05 identity (CD1's open item).

## 9. DISCREPANCIES (each measured; none changes a contract line)

1. **Two existing tests' FIXTURES are invalid under item C; their assertions are kept.** The brief says the seven committed
   bundles keep their verdicts (true: all seven have one allowed entry and one C0 equal to it, and every existing test on them is
   green), but two tests build their own mutated fixtures that item C now refuses:
   - `test_a_widened_allow_list_changes_the_expected_digest` (T:427) adds a second allowed entry with NO C0 for it. Under C the
     positive control refuses that first (`positive-control-failed: curl`, PHASE 2 runs the positive control before the rules),
     so the test no longer reached its subject. Fixed in the FIXTURE: the widened entry gets its passing C0 record; the
     assertion (`egress-rules-unpinned: curl rules are not the pinned allow-list`) is byte-identical.
   - `test_the_pass_line_counts_units_not_records` (T:621) duplicated the ONE C0 record: that is now C's refusal shape "two C0
     records for one target" (`test_e3b_c_...[two-c0-for-one-target]`). Fixed in the FIXTURE: a real two-entry unit
     (`_two_entry_bundle`); the assertions (rc 0, `1 units,`, `positive controls 1/1`) are unchanged.
   Both name item C at the site. Coordinator: if either adaptation is not wanted, the alternative is to change the expectation
   instead, which would be weaker; I did not.
2. **One changed expectation (R1, the brief anticipated it):** the pair leg's relay log asserted `/v1/models` (`sorted(seen)`, T:2519 at the
   final bytes); it now asserts `/health` twice (preflight + C0) plus the pair's own request, sorted-equal (stricter: the whole
   log, not membership).
3. **A MISSING argument 3** (a collector call with only `<unit> <ns>`) now reads as an empty argument: exit 64,
   `run_canaries: allowed entry '' is not <ip>:<port>[/<path>]`. On the PIN it was bash's `${3:?}` usage error, exit 1. The
   brief names "an empty argument"; I read an absent one the same way (the first failure of argument 3 exits 64). `<unit>` and
   `<ns>` keep their `:?` usage errors (exit 1). The collector's own `:?` usage text (RC:31) now names the new grammar.
4. **R2 "no HTTP answer" is read as "anything that fails the predicate and is not an HTTP answer outside 2xx"**: curl rc != 0
   with a status (a transfer cut after the headers), or no record at all (the canary could not run), both take today's
   `unreachable` texts. Fail closed; the contract names only the two shapes.
5. **The runner reads the canaries' scrub list from `canaries/_emit.sh`** (PC:274-276, exit 2 `cannot read the canaries' scrub
   list` if it cannot) so the preflight's wrapper cannot drift from the canaries'. `run_canaries.sh`'s own literal copy of the
   list (`SCRUBBED=`, RC:77, pre-existing) was not touched.
6. **Declared limit 6 names AF-AP-33** (`the AF-AP-33 class`, PC:52-54): the brief's text is kept whole and a clause added, because the test screen
   flags every health-path line as that class (section 7).
7. **Origin's head at measurement was `bee499f`** (the dispatch said 05c90dc; one transcripts commit later), and the local HEAD
   moved again during the lane (coordinator commits touching CLAUDE.md, briefs, the ledger, the incident log and the wiki,
   none in this boundary; the boundary diff PIN..HEAD read 0 lines at the start).
8. **The test count grew 183 -> 251** (68 items: G 29 + 4, A 23 + 1 + 4 + 1, P 1, C 4, R 3); `NEEDS_NETNS` items 43 -> 47.
9. **Kills proven with the named `-k` selections**, after the whole file collected per mutant (as in E3); the whole file ran
   green twice as root on the final bytes.

Adjacent defects (found while reading, OUTSIDE the items; reported, NOT fixed):
- **A non-string allow entry crashes the checker** (pre-existing, measured on the PIN bytes): `read_gate` does not type-check
  the list's elements, and `_split_ip_port(20128)` raises `TypeError: expected string or bytes-like object, got 'int'`. The PIN
  checker on the mechanism bundle with `"allowed": [20128]`: `rc 1 | stdout '' | stderr last: TypeError: ...` (fail closed, but
  no named reason). With E3-b the same bundle reads `positive-control-failed: curl` first; the crash stays reachable only
  through a bundle whose C0 target is the same non-string.
- **Today's C0 predicate accepts `rc: false`** (AF-AP-26's class on `rc`): `record["rc"] != 0` is False for `False` (and `0.0`).
  Measured on the PIN: `check_positive_control` with `"rc": False` returned `1`. The contract keeps today's predicate, so
  `c0_proves` keeps it too.
- **`c0_allowed_target.sh:2-5`** still says the unit "must REACH its one allowed target"; with C0 per entry it is one target
  per run. Not changed: the brief allows one change in that file.
- **`run_canaries.sh:77` (`SCRUBBED=`) duplicates `_emit.sh`'s scrub list** (pre-existing; the runner now reads the list from `_emit.sh`).
- VERIFY-E2-R1 follow-ups F3, F5, F6, F7 (E3 section 9) are unchanged by this lane.

## 10. NOT-done (first-class)

- NOTHING ran on the PC (no bridge use in this lane). Whether the real OmniRoute and relay answer their health paths FROM the
  namespaces (the host firewall, the DNAT) is the coordinator's live leg; the two bridge probes in the brief were run from the
  host, not from a namespace.
- The S0-05 pair identity the relay accepts still does not exist (CD1's open item); the health-path C0 does not need it, the
  pair's own relay handshake does.
- `shellcheck` is absent in the sandbox: not run.
- No commit, stage or push (the coordinator commits); S0-05 stays unminted; `spec.json`, the committed bundles, the other
  canaries and `_emit.sh` are untouched.
- VERIFY-E3 (grading E3 and this lane together) is not part of this lane.
- A pid-directed SIGINT is what the tests drive; a terminal's group SIGINT was measured only on the trap probe (rc 130, one
  cleanup), not on the real runner.

## 11. Self-attack — the three most likely ways this change is wrong

1. **The preflight and the collector's C0 could still grade differently.** Ruled out as far as the sandbox allows: the
   preflight runs the SAME script (`canaries/c0_allowed_target.sh`) inside the same namespace, under the same `env -u` scrub
   list (read from `_emit.sh`, which the canary also sources), with the same path, and grades with the checker's own function
   (`c0_proves`, which `check_positive_control` also calls). Measured: the real-shaped stand-ins saw exactly two requests per
   entry, the preflight's and C0's, on the same path (`test_runner_live_leg` T:1217 `asked`, the pair leg T:2519-2520 `sorted(seen)`); B10 (any HTTP
   answer passes) and X3 (the preflight asks another path) are killed. Residual, by nature: the preflight precedes C0 by the
   30 s settle window, so a service that falls over in between fails C0 and the checker refuses the unit (fail closed).
2. **The two grammars could still disagree on an input outside the table.** Beyond the 29-row parity table (both locales), a
   differential fuzz of 10,000 entries (ASCII, Arabic-Indic, fullwidth, superscript and Devanagari/Bengali zero digits, dots,
   colons, whitespace, brackets): `locale C: 10000 entries, 10000 bash verdicts, accepted by both 1002, mismatches 0` and the
   same for `C.UTF-8`. The bash classes are explicit ASCII lists (no range a locale can widen); the checker uses `[0-9]` with
   `fullmatch`. B9 (the PIN's `\d`) and B14 (a skipped entry) are killed. Residual: only the two locales this sandbox has were
   exercised; a locale whose regex engine treats the listed bytes differently is not known to exist.
3. **The new traps could skip `cleanup` or run it twice, or a stop could still start a leg.** `cleanup` is on EXIT only and both
   signal traps `exit`, so it runs once through the EXIT trap (measured on a probe: SIGTERM rc 143, SIGINT rc 130, group SIGINT
   rc 130, one `cleanup-ran` each). On the real runner: X4 case 1 (SIGTERM: 143, census clean, no units.json, no census file, no
   checker), the SIGINT test (130, the same), and the two-unit test, whose `ip` shim log shows exactly ONE `netns del
   s0-05-hermes-acp` after the stop and no call naming `s0-05-buzz-acp` at all. B11 dies on all three. Residual: subshells and
   command substitutions reset traps (bash semantics), which is what keeps the unit's launch subshell from running the
   runner's `cleanup`; a SIGKILL of the runner (no trap at all) still leaves its namespaces for the next create or destroy, as
   E3 stated.
