# E3 — report (S0-05 live-unit launch recipe: Part X, CD1 A1-A8, D-051)

Status: COMPLETE — lane E3 built Part X, CD1 A1-A8 and D-051 in the sandbox; the pair's LIVE PASS is blocked outside
this boundary (DISCREPANCY 1). Written incrementally.
report_lint (final, round 3 of at most 3): `92 refs — OK 92, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`;
round 1 read `90 refs — OK 71, NEAR 2, MISS 13, UNCHECKABLE 4` (wrapped refs and two PIN-era refs, fixed).
Lane s0-05-e3, sandbox, root, shared tree. PIN `06828ea`; brief on origin `6914400`. Key: L = `proofs/S0-05/netns_lib.sh`, PC = `proofs/S0-05/tools/pc/run_s0_05_units.sh`,
C = `proofs/S0-05/check_egress.py`, T = `tests/test_s0_05_egress.py`. Nothing in this lane ran on the PC.

## 1. PREMISE re-measured (item 1) — MATCH, contract stands

Run 2026-09-23T05:10:28Z, sandbox root, HEAD `6914400` (= origin), working tree clean on the boundary.

```
$ git diff --stat 6f2589d 06828ea -- proofs/S0-05 tests/test_s0_05_egress.py ; echo rc=$?
rc=0                                   (empty: the PIN boundary = the E2-R1 landing)
$ git diff --stat 06828ea HEAD -- proofs/S0-05 tests/test_s0_05_egress.py proofs/S0-01/pins.py   -> rc=0, empty
$ git diff --stat HEAD -- proofs/S0-05 tests/test_s0_05_egress.py                                -> rc=0, empty
$ sha256[:16] + lines at the PIN (git show 06828ea:<f>), and the same on the working tree
234bb13ac0e475c6 320 proofs/S0-05/netns_lib.sh
4d3b917c6fd8c973 177 proofs/S0-05/tools/pc/run_s0_05_units.sh
5d9c502e862d0507 380 proofs/S0-05/check_egress.py
44b1428b431303a1 139 proofs/S0-05/run_canaries.sh
ed6edbd1c408ad83 43 proofs/S0-05/spec.json
d93b1b32d075f684 1507 tests/test_s0_05_egress.py
$ git log --format='%h %s' -3 06828ea -- netns_lib.sh run_s0_05_units.sh
6f2589d S0-05 E2-R1 landed (GATED-PENDING-VERIFY) ...   9223162 E2 landed ...   24e80e6 S0-05: the canary suite ...
$ line map (netns_lib.sh @PIN): 54:egress_ns_resolver() 77:(the -gt 65535 guard) 200:egress_ns_run() 247:EGRESS_OWNER_DIR=
  248:egress_ns_owner_file() 258:_egress_ns_teardown() 314:egress_ns_destroy()
$ runner @PIN: :52 and :54 = "/usr/bin/python3 $S0_01_TOOLS/pc_launch.py --leg run-1 --model s0-01-pong"; :74-80 cleanup
  (owner == $$); :93-97 create failure -> not-run + continue BEFORE NS_LIVE; :118 `</dev/null` into a regular file
$ pins.py @PIN :31-34, :38, :52-53, :55-62 — identical to the brief's quotation
$ bash -c '[ 99999999999999999999 -gt 65535 ]; echo "rc=$?"'
bash: line 1: [: 99999999999999999999: integer expression expected
rc=2
$ partial-state class at the PIN bytes (git show 06828ea:proofs/S0-05/netns_lib.sh; EGRESS_OWNER_DIR under the scratchpad)
capable: ok
.../netns_lib_pin.sh: line 77: [: 99999999999999999999: integer expression expected
iptables v1.8.10 (nf_tables): invalid port/service `99999999999999999999' specified
create rc=1
--- census after the refused create
netns: 1
veth host if ehec0fd5cf: 1
/etc/netns/e3-premise-a: present
claim dir: present
owner file: present (22193)
destroy rc=0
--- census after destroy
netns: 0 veth: 0 etc: absent claim: absent
$ root gate on the unchanged bytes (basetemp /tmp/e3/pre/bt)
137 passed in 60.73s (0:01:00)
pipestatus=0
$ non-root gate on the unchanged bytes (setpriv 65534, /tmp/e3nr/bt)
122 passed, 15 skipped in 4.09s
pipestatus=0
$ baseline census: ip netns list -> empty; ip -o link show type veth -> empty; iptables -t nat -S PREROUTING ->
  "-P PREROUTING ACCEPT" only; /etc/netns empty; /run/s0-05-egress empty; route_localnet all/default 0
$ command -v shellcheck -> absent
```

Every premise line matches. The contract is not invalidated; building proceeds. Findings made while grounding that affect
the contract but do not invalidate it are in DISCREPANCIES (section 9), measured.

## 2. Part X — CHECKPOINT (landed first, 2026-09-23T05:4xZ): 5/5 mutants killed, 148 passed

Line numbers below are the FINAL bytes (Parts A and D moved them after the checkpoint; the checkpoint's own mutant run
is re-derived on the final bytes in section 6). What changed (L = netns_lib.sh, PC = the runner, T = the test file):

| Item | Change | Where |
|---|---|---|
| X1 (F1, AF-AP-129) | the port regex bounds the DIGIT COUNT before the arithmetic: `^[1-9][0-9]{0,4}$` then `-gt 65535` | L:83 |
| X3 (F4) | the claim IS the owner record `<ns>.owner`, installed by a link(2) of a fully written temp (atomic, with content: no window with an empty or stale owner); a dead-pid record is taken over by an atomic rename of THAT record to a unique tombstone, and a record that turns out live is linked straight back; the E2-R1 claim dir is gone | `_egress_ns_claim()` L:153-176 |
| X3 (call) | the claim runs before destroy-first and creation: `_egress_ns_claim "$ns"` | L:98 |
| X2 (partial state) | every step from `ip netns add` on (incl. `/etc/netns` and the gate) rolls back on failure: `_egress_ns_rollback` = teardown, then release the claim ONLY if the teardown left nothing alive (so a leftover stays owned by `$$`) | L:118-136, L:182 |
| X2 (release) | one helper `_egress_ns_release` drops the owner record and the E2-R1 claim dir; used by the F6 refusal, the rollback and destroy | L:185, L:111, L:399 |
| X2 (runner) | the name enters `NS_LIVE` BEFORE create and stays on a failed create; `cleanup` keeps E2-R1's owner check | PC:332-336 |

Design decision (X3, "decide the mechanism"): a link-installed owner record + a rename-to-tombstone takeover, never a
lock. Rejected: the brief's example with the E2-R1 claim dir kept (mkdir, then write the record) — it keeps a window where
a claim dir exists while the record is empty or still names the dead pid, so a second creator can read a fresh claim as
stale; the record has to be born with its content. `Declared limit` (in the code, L:148): a THIRD creator linking a
fresh claim inside the microseconds between a loser's rename and its link-back can orphan the winner's record.

Tests added (T, section "E3 — Part X"): `test_x1_port_is_digit_bounded_before_any_arithmetic` (5 entries; exact whole
stderr; census), `test_x2_create_rolls_back_a_failed_step[veth|gate-rule]` (a bash `ip` function refuses one exact step
and snapshots what already exists, so the rollback provably had work to do), `test_x2_runner_reaps_a_create_killed_midway`
(a PATH `ip` shim SIGKILLs the create's subshell at the veth add; the snapshot proves the leftover was real and owned by
the runner pid), `test_x3_stale_takeover_is_atomic` (the loser SIGSTOPs itself inside a `cat` function right after its
stale read; the winner claims and builds; the loser resumes), `test_x4_runner_cleanup_reaps_its_own_namespace_at_exit`
(SIGTERM mid-leg), `test_x4_runner_cleanup_leaves_a_live_owners_namespace` (holder + real runner; kills M14).

RED on the PIN production bytes (`git diff --stat HEAD -- proofs/S0-05` empty at the time), full log in scratch:

```
$ pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3/red/bt -k "x1_ or x2_ or x3_ or x4_"
E           AssertionError: (1, ".../netns_lib.sh: line 77: [: 99999999999999999999: integer expression expected...invalid port/service `99999999999999999999' specified
E           assert 1 == 64
E           AssertionError: {'netns': True, 'veth': False, 'etc_netns': False, 'owner_dir': ['s0-05-e3-78726a55.claim', 's0-05-e3-78726a55.owner']}
E           AssertionError: {'netns': True, 'veth': True, 'etc_netns': True, 'owner_dir': ['s0-05-e3-eca112b6.claim', 's0-05-e3-eca112b6.owner']}
E           AssertionError: ({'netns': True, 'veth': False, 'etc_netns': False, 'owner_dir': ['s0-05-hermes-acp.claim', 's0-05-hermes-acp.owner']}...
E           assert 'loser_rc=0' == 'loser_rc=65'
FAILED tests/test_s0_05_egress.py::test_x1_port_is_digit_bounded_before_any_arithmetic[overflow-20-digits]
FAILED tests/test_s0_05_egress.py::test_x1_port_is_digit_bounded_before_any_arithmetic[overflow-2^63]
FAILED tests/test_s0_05_egress.py::test_x2_create_rolls_back_a_failed_step[veth]
FAILED tests/test_s0_05_egress.py::test_x2_create_rolls_back_a_failed_step[gate-rule]
FAILED tests/test_s0_05_egress.py::test_x2_runner_reaps_a_create_killed_midway
FAILED tests/test_s0_05_egress.py::test_x3_stale_takeover_is_atomic - Asserti...
6 failed, 5 passed, 137 deselected in 3.76s
```

The 5 that pass on the PIN are expected: `65536`, `0`, `00080` were already refused (only the overflow class leaked), and
the PIN's `cleanup` is correct in both X4 cases — X4 case 2 kills M14 only once X2's early reap entry puts the refused
name into `NS_LIVE` (VERIFY-E2-R1 F8: on the PIN the refused name never reached `cleanup`, which is why M14 survived).

GREEN (after the change):

```
$ pytest ... -k "x1_ or x2_ or x3_ or x4_"            11 passed, 137 deselected in 3.15s   pipestatus=0
$ pytest tests/test_s0_05_egress.py ... (whole file)  148 passed in 63.92s (0:01:03)        pipestatus=0
census after: ip netns list / ip -o link show type veth / ls -A /etc/netns /run/s0-05-egress  -> all empty
```

Part X mutants (scratch copies under the scratchpad, harness `mutate.py`; each `bash -n` rc 0 and 148 collected):

```
M14: bash -n rc=0 | 148 tests collected | -k 'x4_ or runner_refusal_does_not_destroy_sibling' -> 2 failed, 1 passed | KILLED
    FAILED tests/test_s0_05_egress.py::test_runner_refusal_does_not_destroy_sibling
    FAILED tests/test_s0_05_egress.py::test_x4_runner_cleanup_leaves_a_live_owners_namespace
E1: bash -n rc=0 | 148 tests collected | -k 'x1_ or allow_entry_must_be_ipv4_literal' -> 2 failed, 15 passed | KILLED
    FAILED tests/test_s0_05_egress.py::test_x1_port_is_digit_bounded_before_any_arithmetic[overflow-20-digits]
    FAILED tests/test_s0_05_egress.py::test_x1_port_is_digit_bounded_before_any_arithmetic[overflow-2^63]
E2: bash -n rc=0 | 148 tests collected | -k 'x2_' -> 2 failed, 1 passed | KILLED
    FAILED tests/test_s0_05_egress.py::test_x2_create_rolls_back_a_failed_step[veth]
    FAILED tests/test_s0_05_egress.py::test_x2_create_rolls_back_a_failed_step[gate-rule]
E3: bash -n rc=0 | 148 tests collected | -k 'x2_runner or x4_' -> 1 failed, 2 passed | KILLED
    FAILED tests/test_s0_05_egress.py::test_x2_runner_reaps_a_create_killed_midway
E4: bash -n rc=0 | 148 tests collected | -k 'x3_ or race or sibling' -> 1 failed, 4 passed | KILLED
    FAILED tests/test_s0_05_egress.py::test_x3_stale_takeover_is_atomic
```

(E4 = the stale takeover back to read-then-write: `printf '%s\n' "$$" > "$owner_file"` in place of the tombstone block.)

AF-AP-129 sweep of the final boundary (every `[ x -op N ]`, `(( ))`, `$(( ))`): L:50-51 (`sha256sum`: two hex digits of a
digest), L:73 and L:217 (`"$#" -ge 1`), L:347-375 (internal counters `remaining`/`kwait`), PC:339 and PC:347 (`$? -ne 0`)
are not input-derived; L:83 is the port (`-gt 65535`), now digit-bounded first. New input-derived numbers are bounded first too: the
owner pid in `_egress_ns_claim` (`^[1-9][0-9]{0,9}$` before `kill -0`), the unit user (`S0_05_UNIT_USER` regex before any
use) and the identity file mode (`^[0-7]{1,4}$` before `$(( 8#$mode & 8#077 ))`). C is Python (`IPV4_PORT` at C:94 caps
the port at five digits before `int()`). Adjacent, OUTSIDE the boundary (reported, not fixed):
`proofs/S0-05/run_canaries.sh:29` computes `$((ALLOWED_PORT + 1))` on the third argument's port. Measured class:

```
$ bash -c 'ALLOWED_PORT="99999999999999999999"; echo "overflow: $((ALLOWED_PORT + 1))"; ALLOWED_PORT="x[\$(echo EXPANDED-INSIDE-ARITHMETIC >&2)]"; echo "expr: $((ALLOWED_PORT + 1))"'
overflow: 7766279631452241920
EXPANDED-INSIDE-ARITHMETIC
expr: 1
```

No production caller reaches it with an unvalidated entry (the runner passes only entries `egress_ns_create` accepted),
but a direct caller could; it belongs to run_canaries.sh's owner.

## 3. Part A — CD1 A1-A8 (the launch recipe)

| Item | Change | Where |
|---|---|---|
| A1 pins | every pinned value is read ONCE at run time from pins.py, `import pins` in a heredoc run as `python3 -B` (no bytecode into the owner's clone); the relay URL and the `PINNED_LAUNCH_ARGV` shape are validated | PC:79, PC:83 |
| A1 rows | `UNIT_EXE[hermes-acp]=PINNED_AGENT_REALPATH`, `UNIT_EXE[buzz-acp]=PINNED_BUZZ_ACP_EXE_REALPATH`: a row NAMES a pin, run directly from its realpath, no interpreter prefix | PC:155-156 |
| A1 on-disk check | `_pin_ok`: the file IS its realpath and carries the pinned sha256, else `unit identity mismatch` | PC:171 |
| A1 check site | `# A1: the pinned unit is on disk as pinned` (the pair checks buzz-acp, then its agent) | PC:295 |
| A1 recorded override | the input `S0_05_PIN_OVERRIDE`, its closed name set `OVERRIDABLE`, announced on stderr | PC:84 |
| A1 recorded on the row | every unit row carries it: `row["override"] = override` | PC:493 |
| A1 checker | `units-manifest-invalid: {unit} override present` for a run unit whose bundle says venue pc | C:437 |
| A2 scratch | `# A2: the unit's own scratch tree`: `<root>/<unit>/scratch/{home,hermes-home}`, owned by the unit user, 0700, writability proven as that user | PC:369 |
| A2 census | `_s0_01_census`: lstat of `<base>/.markers` + every `v2-*` dir; base = dirname of `PINNED_HERMES_HOME` | PC:194 |
| A2 compare | `census_changed` after the last unit -> `s0-01-tree-changed: $path`, exit 1, checker not run; `s0-01-census.json` recorded | PC:453, PC:503 |
| A3 | `# A3: stdin is a pipe the runner holds open`: two FIFOs in a root 0700 dir, the runner holds stdin read-write (no blocking open), a `cat` reader writes the log | PC:382 |
| A3 stop | `# A3 + F9: the stop is closing stdin`; bounded 10 s wait, the destroy is the backstop | PC:439 |
| A4 | `S0_05_UNIT_USER`, else `stat -Lc '%u:%g'` of the pinned agent; `setpriv --reuid --regid --init-groups` inside `ip netns exec` | PC:144 |
| A4 refusal | `# A4: never as root.` -> `unit would run as root` | PC:311 |
| A5 | `env -i` with `unit_env` = PATH (pinned), HOME, HERMES_HOME, LANG, PYTHONDONTWRITEBYTECODE | PC:395 |
| A6 identity | `_pair_identity`: S0-01 `.secrets` by path first, then absent, mode, owner, shape; read with `read -r`, never printed | PC:175 |
| A6 argv | the `PINNED_LAUNCH_ARGV` shape with the three substitutions | PC:109 |
| A6 key | the key reaches the pair through fd 3 and a `"$PY_BIN" -I -c` exec shim (same pid), never an argv | PC:404 |
| A7 runner | `_unit_identity`: pid, `/proc/<pid>/exe` realpath, entrypoint realpath + sha256, the four Uid-line uids, argv -> `<unit>/unit-identity.json`; every mismatch named | PC:217 |
| A7 gate | `# A7: the canaries run only if` the record matches -> else `unit identity not observed` | PC:422 |
| A7 checker | `check_unit_identity` against `pinned_identity` from pins.py loaded by `_load_pins` (the S0-03 by-path pattern) | C:346, C:127, C:110 |
| A8 | `# A8: every allow entry is formed here`: `host_ip` + a port input, never word-split; the retired `ALLOWED_HERMES` is named as ignored | PC:325 |
| docstring | the checker's order gains item `8. A LIVE CLAIM IS THE REAL UNIT` | C:41 |

Fixtures (A7; the ONLY fixture change): `proofs/S0-05/fixtures/evidence-synthetic-pass/hermes-acp/runtime.json` venue
`synthetic` -> `pc` (one token) and a new `hermes-acp/unit-identity.json` beside it, generated from pins.py (no value
retyped: exe = `PINNED_AGENT_INTERPRETER_REALPATH`, entrypoint + sha256 = the agent pins, uid `[1000]*4`); NEW
`proofs/S0-05/fixtures/evidence-synthetic-uid0/` = the same bundle with the record's uid `[0,0,0,0]` (the only diff,
asserted by a test). Why the venue changed: see DISCREPANCY 2.

Decisions made inside the contract (each measured):
- A5's environment: bash cannot build a clean one by un-exporting (measured: invalid-name entries like `A.B` pass through
  and `exec` re-exports `SHLVL`), so the runner uses `env -i` with the non-secret set on env's argv, and the pair's key
  travels on fd 3 into a `python3 -I -c` exec shim — never an argv (an argv is world-readable in /proc).
- A7's uid: the record keeps all four `Uid:` values and any 0 refuses (a setuid-root unit is root too).
- A7's order in the checker: PHASE 1b, after PHASE 1's gate and mechanism verdicts (so `egress-permitted: gate-disabled`
  stays first, the seed's pinned reason) and before any canary; the override refusal precedes the identity grade.
- A1's pair check covers BOTH executables it runs (buzz-acp, then the agent it launches).

## 4. Part D — D-051's relay reach

| Item | Change | Where |
|---|---|---|
| add | `egress_relay_reach_add`: `route_localnet=1` on the pair's host interface, then ONE `iptables -t nat -A PREROUTING -i <host_if> -p tcp -d <host_ip> --dport <port> -j DNAT --to-destination <relay>`; a failed rule add undoes the sysctl | L:307, L:311 |
| del | `egress_relay_reach_del`: every nat PREROUTING rule naming the interface, deleted by its own spec, bounded (16), then `route_localnet=0` while the interface exists | L:315, L:325 |
| teardown | `egress_relay_reach_del "$ns"` is the FIRST step of every teardown (leg teardown and `cleanup` both run `egress_ns_destroy`; create's destroy-first reaps a crashed run's rule too); its failure is loud and returns 1 | L:341 |
| runner | `# D-051: the pair reaches the pinned relay` after create, before the preflight; failure -> `relay reach not established` | PC:344 |
| allow-set | the pair's allow list is `{relay, OmniRoute}` on the veth host address (`allowed=("$host_ip:${PIN[RELAY_PORT]}" "$host_ip:$OMNI_PORT")`) | PC:330 |
| preflight | `# PREFLIGHT the exact predicate`: C0 to EVERY allowed destination, `--noproxy '*'` (the canaries scrub proxies too) | PC:354 |

The relay port and the DNAT destination come from `PINNED_RELAY_URL` (pins.py:38); no service is touched.

Tests added or changed (T):

| Test | Where | What it proves |
|---|---|---|
| `def test_runner_live_leg` (changed) | T:1071 | every E2 assertion kept (argv is now the pinned realpath); plus A1, A2, A3, A4, A5, A7, A8 on the same real run |
| `def test_shebang_matches_launch_interpreter` (changed) | T:1212 | re-targeted to the `UNIT_EXE` rows, stricter: a row is a single pin name |
| `def test_units_json_quotes_in_reason` (changed) | T:1419 | the special characters ride the port input; the exact line |
| `def test_runner_refusal_does_not_destroy_sibling` (changed) | T:1443 | the recorded-override inputs; stricter census |
| `def test_a1_unit_identity_mismatch_is_refused` ×5 | T:1996 | wrong sha, symlinked path, absent, real pins, pair wrong sha |
| `def test_a1_checker_refuses_an_override_on_a_live_claim` | T:2030 | the refusal, its pc scope, and its order before the identity grade |
| `def test_a2_s0_01_tree_change_fails_the_leg` | T:2054 | `s0-01-tree-changed:` + exit 1, and A4's default user |
| `def test_a4_a_root_unit_user_is_refused` ×2 | T:2094 | explicit 0:0 and a root-owned default |
| `def test_a4_a_malformed_unit_user_is_a_usage_error` | T:2107 | `00:0` is a usage error, nothing written |
| `def test_a6_identity_file_refusals` ×7 | T:2119 | unset, absent, mode, owner, shape, S0-01 path under an overridden base and at the real base |
| `def test_a7_a_unit_not_matching_the_pins_is_not_observed` | T:2160 | exe mismatch + uid 0 via a PATH `setpriv` shim; no canaries ran |
| `def test_a7_the_synthetic_pass_fixture_grades_its_identity` | T:2196 | the identity line is printed (the check acted) |
| `def test_a7_the_uid0_fixture_is_refused` | T:2206 | the committed twin, one field apart |
| `def test_a7_the_checker_refuses_an_identity_that_is_not_the_pin` ×9 | T:2230 | missing, digest, exe path, entrypoint path, effective uid 0, shapes |
| `def test_a7_the_identity_is_graded_only_for_a_live_claim` | T:2251 | the pc scope; a pc unit without pins |
| `def test_a8_every_allow_entry_is_formed_by_the_runner` | T:2264 | the derived entry; the planted address ignored |
| `def test_d_relay_reach_add_and_del` | T:2397 | the DNAT path, `route_localnet` load-bearing, removal while the interface lives |
| `def test_d_pair_leg_reaches_the_relay_through_the_dnat` | T:2439 | the whole pair leg: DNAT, argv, env, identity, removal census |
| `def test_d_without_the_relay_reach_the_pair_is_not_run` ×2 | T:2522 | the negative controls: rule absent, rule refused |
| the Part X tests | section 2 | X1-X4 |

The stand-ins live only in test-owned dirs: the
hermes-acp stand-in (`AGENT_STANDIN`, T:1638) does the real adapter's epoll registration of its stdio (CD1 probe 2's
crash, reproduced: `stdin /dev/null -> rc 1 | stop: crash: PermissionError(1, 'Operation not permitted')`; `stdin pipe,
EOF -> rc 0 | stop: eof`), and the buzz-acp stand-in is compiled (`PAIR_WRAPPER_C`, T:2290) because A7 grades
`/proc/<pid>/exe`. Stand-ins record env KEY NAMES only (values for the non-secret set, a digest for the pair key): the
sandbox exports real tokens, which `_secret_free_environ` removes before a runner is started, and planted fakes
(`PLANTED`, T:1622) carry the A5/A8 negative controls.

## 5. RED then GREEN (pasted)

Part X: section 2. Parts A and D: RED on a scratch tree holding the PIN's three production files byte-for-byte
(`234bb13ac0e475c6 netns_lib.sh`, `4d3b917c6fd8c973 run_s0_05_units.sh`, `5d9c502e862d0507 check_egress.py`, the
premise's digests) plus the new fixtures and the new test file:

```
$ pytest ... -k "test_a1_ or test_a2_ or test_a4_ or test_a6_ or test_a7_ or test_a8_ or runner_live_leg or quotes_in_reason or runner_refusal or shebang"
34 failed, 1 passed, 144 deselected in 7.90s
first assertion per failure (a sample; none is an import or fixture error):
test_runner_live_leg: AssertionError: curl: (7) Failed to connect to 10.201.107.1 port 1 after 0 ms: Couldn't connect to server
test_shebang_matches_launch_interpreter: AssertionError: no unit rows found
test_a1_unit_identity_mismatch_is_refused[wrong-sha]: ... 'reason': 'positive control unreachable: 10.201.107.1:1 not reachable from s0-05-hermes-acp'}
test_a1_unit_identity_mismatch_is_refused[pair-wrong-sha]: ... 'reason': 'no allowed destination configured for buzz-acp (set ALLOWED_* from the docs/05 §6 row)'}
test_a1_checker_refuses_an_override_on_a_live_claim: AssertionError: assert 0 == 1
test_a4_a_malformed_unit_user_is_a_usage_error: assert 1 == 64
test_a7_the_uid0_fixture_is_refused: AssertionError: assert 0 == 1
test_a7_the_identity_is_graded_only_for_a_live_claim: AssertionError: assert 'NOT run: buz...n the sandbox' == 'unit-identit...y.json absent'
$ pytest ... -k "test_d_"
E           AssertionError: bash: line 2: egress_relay_reach_add: command not found
E               AssertionError: assert 'no allowed d...cs/05 §6 row)' == 'positive con...0-05-buzz-acp'
4 failed, 179 deselected in 2.95s
```

Read: the PIN runner forms the unit's entry from the PLANTED operator-typed `ALLOWED_HERMES` (port 1: the A8 defect) and
has no pinned-unit, user, identity or relay logic; the PIN checker passes the uid-0 fixture, a missing record and an
override (rc 0). The one RED pass is `test_runner_refusal_does_not_destroy_sibling`, which the PIN already satisfies.

GREEN (final bytes): the gates in section 7 — `183 passed` twice as root, `140 passed, 43 skipped` as nobody.

## 6. Mutant table (final bytes; scratch copies only; harness `mutate.py`, spec `mutants-final.json` in the scratchpad)

Each mutant: the file copied into `<scratchpad>/e3/mut/<id>/` with the rest of the boundary, ONE exact replacement
(refused unless the old text occurs the stated number of times), `bash -n` / `py_compile`, the WHOLE test file collected,
then the named killers run; the tree is deleted after. Collected = `183 tests collected` for every row.

| Mutant | What it does | Compiles | Collected | Killed by |
|---|---|---|---|---|
| M14 | `cleanup` destroys every NS_LIVE name (owner check dropped) | bash -n rc=0 | 183 | `test_x4_runner_cleanup_leaves_a_live_owners_namespace`, `test_runner_refusal_does_not_destroy_sibling` |
| E1 | X1's digit bound removed (`^[1-9][0-9]*$`) | bash -n rc=0 | 183 | `test_x1_...[overflow-20-digits]`, `[overflow-2^63]` |
| E2 | create's rollback removed (`_egress_ns_rollback() { :; }`) | bash -n rc=0 | 183 | `test_x2_create_rolls_back_a_failed_step[veth]`, `[gate-rule]` |
| E3 | the runner's early reap-set entry moved after a successful create | bash -n rc=0 | 183 | `test_x2_runner_reaps_a_create_killed_midway` |
| E4 | the stale takeover back to read-then-write (`printf $$ > owner`) | bash -n rc=0 | 183 | `test_x3_stale_takeover_is_atomic` |
| E5 | the checker's override refusal removed | py_compile ok | 183 | `test_runner_live_leg`, `test_a1_checker_refuses_an_override_on_a_live_claim` |
| E6 | the runner's A7 uid check removed | bash -n rc=0 | 183 | `test_a7_a_unit_not_matching_the_pins_is_not_observed` |
| E7 | the checker's `uid 0` refusal removed | py_compile ok | 183 | `test_a7_the_uid0_fixture_is_refused`, `test_a7_the_checker_refuses_...[effective-uid-0]` |
| E8 | the relay-reach removal dropped from teardown | bash -n rc=0 | 183 | `test_d_pair_leg_reaches_the_relay_through_the_dnat`, `test_d_without_the_relay_reach_...[rule-absent]` |
| E9 | `route_localnet` left set by `egress_relay_reach_del` | bash -n rc=0 | 183 | `test_d_relay_reach_add_and_del` |
| E10 | the unit environment inherited (`env` without `-i`, both launch lines) | bash -n rc=0 | 183 | `test_runner_live_leg`, `test_d_pair_leg_reaches_the_relay_through_the_dnat` |
| E11 | stdin back to `/dev/null` (both launch lines) | bash -n rc=0 | 183 | `test_runner_live_leg` (the stand-in crashes on EPERM, as the adapter does: `launch exited within the settle window`) |
| E12 | extra: A4's root refusal removed | bash -n rc=0 | 183 | `test_a4_a_root_unit_user_is_refused[explicit]`, `[default-owner]` |
| E13 | extra: A6's S0-01 `.secrets` path refusal removed | bash -n rc=0 | 183 | `test_a6_identity_file_refusals[s0-01-path]`, `[s0-01-real-path]` |
| E14 | extra: A1's realpath check removed | bash -n rc=0 | 183 | `test_a1_unit_identity_mismatch_is_refused[symlinked-path]` |
| E15 | extra: A2's census comparison disabled | bash -n rc=0 | 183 | `test_a2_s0_01_tree_change_fails_the_leg` |
| E16 | extra: the runner's A7 gate ignored (canaries always run) | bash -n rc=0 | 183 | `test_a7_a_unit_not_matching_the_pins_is_not_observed` |

17 of 17 KILLED, 0 SURVIVED, 0 EQUIVALENT. Pasted harness lines (summaries only; the FAILED lines are in the table):

```
M14: bash -n rc=0 | 183 tests collected in 0.32s | -k 'x4_ or runner_refusal_does_not_destroy_sibling' -> 2 failed, 1 passed, 180 deselected in 3.04s | KILLED
E1: bash -n rc=0 | 183 tests collected in 0.32s | -k 'x1_ or allow_entry_must_be_ipv4_literal' -> 2 failed, 15 passed, 166 deselected in 1.03s | KILLED
E2: bash -n rc=0 | 183 tests collected in 0.30s | -k 'x2_' -> 2 failed, 1 passed, 180 deselected in 0.98s | KILLED
E3: bash -n rc=0 | 183 tests collected in 0.37s | -k 'x2_runner or x4_' -> 1 failed, 2 passed, 180 deselected in 2.80s | KILLED
E4: bash -n rc=0 | 183 tests collected in 0.31s | -k 'x3_ or race or sibling' -> 1 failed, 4 passed, 178 deselected in 2.40s | KILLED
E5: py_compile ok | 183 tests collected in 0.31s | -k 'test_a1_checker or runner_live_leg' -> 2 failed, 181 deselected in 37.59s | KILLED
E6: bash -n rc=0 | 183 tests collected in 0.31s | -k 'not_observed' -> 1 failed, 182 deselected in 30.88s | KILLED
E7: py_compile ok | 183 tests collected in 0.30s | -k 'uid0 or not_the_pin' -> 2 failed, 8 passed, 173 deselected in 0.66s | KILLED
E8: bash -n rc=0 | 183 tests collected in 0.34s | -k 'test_d_' -> 2 failed, 2 passed, 179 deselected in 42.12s | KILLED
E9: bash -n rc=0 | 183 tests collected in 0.32s | -k 'test_d_relay_reach_add_and_del' -> 1 failed, 182 deselected in 3.64s | KILLED
E10: bash -n rc=0 | 183 tests collected in 0.32s | -k 'runner_live_leg or pair_leg' -> 2 failed, 181 deselected in 74.77s (0:01:14) | KILLED
E11: bash -n rc=0 | 183 tests collected in 0.32s | -k 'runner_live_leg or x4_runner_cleanup_reaps' -> 1 failed, 1 passed, 181 deselected in 3.85s | KILLED
E12: bash -n rc=0 | 183 tests collected in 0.31s | -k 'test_a4_' -> 2 failed, 1 passed, 180 deselected in 1.21s | KILLED
E13: bash -n rc=0 | 183 tests collected in 0.30s | -k 'test_a6_' -> 2 failed, 5 passed, 176 deselected in 2.04s | KILLED
E14: bash -n rc=0 | 183 tests collected in 0.33s | -k 'test_a1_unit_identity' -> 1 failed, 4 passed, 178 deselected in 1.50s | KILLED
E15: bash -n rc=0 | 183 tests collected in 0.30s | -k 'test_a2_' -> 1 failed, 182 deselected in 37.26s | KILLED
E16: bash -n rc=0 | 183 tests collected in 0.30s | -k 'not_observed' -> 1 failed, 182 deselected in 37.08s | KILLED
```

Notes: E8 also broke `[rule-absent]` because the pair test's un-removed rule stayed on the host and gave the next leg
a path to the relay — the leak E8 represents; the `[rule-refused]` leg's explicit `egress_relay_reach_del` then removed
it (census after the batch: `-P PREROUTING ACCEPT` only). E11's mechanism was checked directly, not inferred from the kill.
Declared limit of the table: kills were proven with the named `-k` selections, not a full-file run per mutant.

## 7. Gates (pasted, each with its invocation)

```
$ date -u ; mkdir -p /tmp/e3/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3/bt ; rm -rf /tmp/e3/bt
Wed Sep 23 06:16:49 UTC 2026
183 passed in 180.06s (0:03:00)
ROOT1 pipestatus=0
Wed Sep 23 06:19:54 UTC 2026
183 passed in 180.73s (0:03:00)
ROOT2 pipestatus=0
$ rm -rf /tmp/e3nr && mkdir -p /tmp/e3nr && chmod 1777 /tmp/e3nr && setpriv --reuid=65534 --regid=65534 --clear-groups env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3nr/bt
Wed Sep 23 06:23:01 UTC 2026
140 passed, 43 skipped in 6.10s
NONROOT pipestatus=0
   (every skip carries the one declared reason — "network-namespace legs need root + iproute2 + iptables; NOT run
   here ..." — 43 of 43; exactly 43 collected items carry the NEEDS_NETNS mark: 15 existing + 28 new)
$ bash -n proofs/S0-05/netns_lib.sh ; bash -n proofs/S0-05/tools/pc/run_s0_05_units.sh
rc=0
rc=0
$ command -v shellcheck
(absent)
$ /root/venv-agent-factory/bin/python -m pyflakes proofs/S0-05/check_egress.py tests/test_s0_05_egress.py
rc=0
$ python3 scripts/ap_screen.py proofs/S0-05/check_egress.py
--- AP_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-32: 1
    proofs/S0-05/check_egress.py:222: return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()
rc=0
$ python3 scripts/ap_screen.py --tests tests/test_s0_05_egress.py
--- TEST_SCREEN over 1 path(s): 3 hits over 1 files ---
AF-AP-80: 2
    tests/test_s0_05_egress.py:1164: assert stat.S_ISREG(log.lstat().st_mode) and "stand-in: serving" in log.read_text()
    tests/test_s0_05_egress.py:2467: assert PAIR_KEY not in runner.stdout + runner.stderr + (evidence / "units.json").read_text()
AF-AP-59: 1
    tests/test_s0_05_egress.py:1138: standin_procs = subprocess.run(["pgrep", "-f", standin], capture_output=True, text=True)
rc=0
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 38 files scanned, clean
rc=0
```

Screen grades (the same screens on the PIN bytes give the baseline: AP-32 at C@06828ea:174 `return hashlib.sha256`,
and AF-AP-59 at T@06828ea:1154 `pgrep`):
- AP-32 C:222 — PRE-EXISTING, the unchanged `rules_digest` body (`return hashlib.sha256`), moved from C@06828ea:174.
- AF-AP-59 T:1138 — PRE-EXISTING: E2's `pgrep` assertion in test_runner_live_leg (T@06828ea:1154), kept because an
  existing assertion may not be weakened or deleted; its pattern is now a unique per-run path under a test-owned mkdtemp
  dir, and the owned-process fact is asserted separately (`_pid_alive(standin_pid)`).
- AF-AP-80 T:1164 (`log.read_text()`) and T:2467 (`PAIR_KEY`) — NEW, not the class: both read runtime artifacts (the unit log; the runner's stdout,
  stderr and units.json), not source text. Each has its behavioural pair: the stand-in's own record (`stdout` is `fifo`),
  and the positive `key_sha256` check that the key DID reach the pair's environment.

Census after every run of this lane (last taken 2026-09-23T06:24:22Z, pasted):

```
$ ip netns list                              ->  (empty)
$ ip -o link show type veth                  ->  (empty)
$ iptables -t nat -S PREROUTING              ->  -P PREROUTING ACCEPT
$ ls -A /etc/netns                           ->  (empty)
$ ls -A /run/s0-05-egress                    ->  (empty)
$ sysctl net.ipv4.conf.all.route_localnet net.ipv4.conf.default.route_localnet  ->  0 / 0
$ ps -eo pid,args | grep -E "[s]tandin|[l]istener\.py|[r]elay\.py|[o]mniroute\.py|[p]air_worker|[s]erver\.py"  ->  (none)
$ ls -d /tmp/e3-* /tmp/e3nr ; find /tmp -maxdepth 2 -type p -name in  ->  no such file (both); no FIFO
```

Every namespace, veth, nat rule, sysctl, claim, `/etc/netns` entry and process this lane created was destroyed by name
or pid from its own record (the tests' `finally` blocks, `egress_ns_destroy <name>`, kill by Popen pid) — never `pkill -f`.

## 8. The live-leg operator recipe (the coordinator's, on the PC; NOTHING here ran on the PC)

Run as ROOT (namespaces, nat rules and `setpriv` need it; `sudo` on the PC needs the owner's password), from the PC
clone at the landed commit:

```
EV=/home/rocco/s0-05-evidence/$(date -u +%Y%m%dT%H%M%SZ)     # fresh; traversable by uid 1000; NOT under
                                                             # /home/rocco/s0-01-pinned (the census would fail)
S0_05_PAIR_IDENTITY=/home/rocco/s0-05-identity/pair.env \
  bash proofs/S0-05/tools/pc/run_s0_05_units.sh "$EV" hermes-acp buzz-acp
```

Inputs: `S0_05_OMNIROUTE_PORT` — omit (20128, CD1 probe 1: OmniRoute on `0.0.0.0:20128`). `S0_05_UNIT_USER` — omit
(defaults to the owner of the pinned agent realpath: `rocco 755`, probe 1, i.e. 1000:1000). `S0_05_PAIR_IDENTITY` — an
S0-05 identity the relay accepts: one `BUZZ_PRIVATE_KEY=<key>` line, owner rocco, mode 0600, anywhere but
`/home/rocco/s0-01-pinned/.secrets/` (that identity does NOT exist yet: CD1's open item). `S0_05_PIN_OVERRIDE` — MUST be
unset (the runner prints `PIN OVERRIDE ACTIVE` if it is not; such a run is never evidence). `ALLOWED_HERMES`,
`ALLOWED_BUZZACP`, `S0_01_TOOLS` are retired and ignored (named on stderr if set).

Expected on success: stdout `=== hermes-acp: namespace s0-05-hermes-acp, allowed 10.201.107.1:20128 ===` and
`=== buzz-acp: namespace s0-05-buzz-acp, allowed 10.201.219.1:3999 10.201.219.1:20128 ===`, then per unit `=== <unit>:
exited 0 on stdin EOF ===`. Files: `$EV/units.json` with `{"unit": "hermes-acp", "status": "run", "note": "contained
live unit"}`, the same for buzz-acp, the six `not-run` rows (memory-adapter, ai-memory, dream-foundry, pandaprobe,
harness-router, s0-01-backend) and NO `override` key anywhere; `$EV/<unit>/{canaries.jsonl,gate.json,runtime.json,
unit-identity.json,scratch/}`, `$EV/<unit>.launch.log`, `$EV/s0-01-census.json` with `"changed": []`. After exit:
`ip netns list` empty and `iptables -t nat -S PREROUTING` without a rule naming the pair's interface `ehda7d8593`
(computed: `egress_ns_host_if s0-05-buzz-acp` -> `ehda7d8593`, host ip 10.201.219.1; hermes-acp: `eh6a87fce7`, 10.201.107.1).

What the checker can say today: hermes-acp can PASS only if OmniRoute answers an unauthenticated `GET /v1/models` with
2xx (CD1 A5 forbids a credential in the unit; unmeasured). buzz-acp CANNOT pass yet: DISCREPANCY 1
(`egress-rules-unpinned: buzz-acp ...`). So `--units hermes-acp,buzz-acp` does not PASS from this landing alone.

What each named refusal means:

| Line | Meaning / action |
|---|---|
| `not-run\|unit identity mismatch: <path>` | the file at the pinned path is absent, not its own realpath, or not the pinned sha256: stop, the pinned tree moved |
| `not-run\|unit would run as root` / `not-run\|unit user unresolved (set S0_05_UNIT_USER)` | the unit user resolved to uid 0 / could not be resolved |
| `not-run\|identity file refused: absent \| mode <octal> \| owner uid <n> \| shape \| S0-01 path <p>` | fix the pair's identity file (never S0-01's) |
| `not-run\|namespace-live: s0-05-<unit> owned by pid <p>` | another live runner holds the name; nothing of it was touched |
| `not-run\|address-plan-collision: ...` | a host interface already holds the unit's /24 |
| `not-run\|egress: allow entry must be <ip>:<port>, got '<entry>'` | a malformed `S0_05_OMNIROUTE_PORT` |
| `not-run\|relay reach not established: <detail>` | the DNAT or `route_localnet` could not be set (detail = the failing command) |
| `not-run\|positive control unreachable: <entry> not reachable from <ns>` | the service does not answer from inside the namespace: bind, host firewall, or the relay down — the preflight MEASURES the firewall |
| `not-run\|unit scratch tree not writable by uid <n>: <path>` | the evidence root is not traversable by the unit user |
| `not-run\|launch exited within the settle window; see <log>` | the unit died in its first 30 s: read `$EV/<unit>.launch.log` |
| `not-run\|unit identity not observed: <detail>` | the process in the namespace is not the pinned unit as the unit user (every mismatch named) |
| stderr `s0-01-tree-changed: <path>`, exit 1, no checker | S0-01's `.markers` tree changed during the leg: STOP and inspect before anything else |
| checker `units-manifest-invalid: <unit> override present` | a stand-in run; never evidence |
| checker `unit-identity-invalid: <unit> <detail>` | the record is missing or not the pins (or uid 0) |

Declared limits (the same four stand in the runner's header, `# DECLARED LIMITS` at PC:34):
1. The canaries share the unit's namespace; they are not the unit's own sockets (kept from E1). In the sandbox the pair
   stand-in's OWN socket did reach the relay through the DNAT, but that is a stand-in, not the real buzz-acp.
2. The relay reach makes ONE veth interface route to loopback for the pair's leg (`route_localnet=1`) and forwards ONE
   port to the pinned relay; nothing else changes on the host, and teardown removes both.
3. A wrong pair identity file only fails the pair's C0 / relay handshake; the runner checks its place, mode, owner and
   shape, never whether the relay accepts the key.
4. `unit-identity.json` is unkeyed: it binds the process that ran to the pins, not against a forger with root on the PC.

## 9. DISCREPANCIES (each measured; none invalidates an E3 contract line)

1. **The pair's bundle cannot pass the checker's rule pin (blocks the pair's LIVE PASS; the fix is outside my boundary).**
   `proofs/S0-05/run_canaries.sh:25` takes ONE allowed entry and writes `"allowed": [allowed]` (run_canaries.sh:130);
   D-051 gives the pair two. Measured on a REAL pair leg through the runner (stand-ins via the recorded override):
   ```
   gate.json allowed (written by run_canaries.sh): ['10.201.219.1:18110']
   recorded ACCEPT rules: ['-A INPUT -s 10.201.219.1/32 -p tcp -m tcp --sport 18110 -j ACCEPT', '-A INPUT -s 10.201.219.1/32 -p tcp -m tcp --sport 3999 -j ACCEPT', '-A OUTPUT -d 10.201.219.1/32 -p tcp -m tcp --dport 18110 -j ACCEPT', '-A OUTPUT -d 10.201.219.1/32 -p tcp -m tcp --dport 3999 -j ACCEPT']
   rules hash to gate digest: True
   checker's expected rules for gate.allowed hash to gate digest: False
   check_runtime_and_rules on the REAL pair bundle -> egress-rules-unpinned: buzz-acp rules are not the pinned allow-list for ['10.201.219.1:18110']
   ```
   The namespace is right (both pairs, observed); the collector's record is short. Fix (run_canaries.sh's owner): take
   every allow entry, record them all in gate.json, C0 each. The checker already derives from the full list. NOT made:
   the brief forbids editing run_canaries.sh, and rewriting gate.json from the runner would make the runner a second
   writer of the collector's record. The runner passes the OmniRoute entry to `run_canaries.sh` for both units (PC:436).
2. **Fixture relabel.** The brief says the synthetic-pass fixture "gains the record it now needs"; measured, its
   `hermes-acp/runtime.json` said venue `synthetic`, so the pc-only rule needs no record there. I changed that ONE token
   to `pc` so the committed pair (pass + uid-0 twin, one field apart) exercises the A7 rule; the curl bundle stays
   `synthetic`. Cost: that bundle loses its in-band synthetic marker (the directory name and the units.json note remain);
   S0-05's mint legs in spec.json do not use it. Reversible if the coordinator prefers two new fixtures.
3. **A5's key list plus one.** The unit environment also carries `PYTHONDONTWRITEBYTECODE=1`: the CD1 probes' own recipe
   (`CD1-probes/probe2_lifetime_isolated.sh:11`, `probe3_isolation_and_pipes.sh:10`) and pins.py's re-baseline note (a
   foreign bytecode write fails S0-01's manifest). The test asserts the exact key set; no key matches the redaction rule
   except the pair's `BUZZ_PRIVATE_KEY`.
4. **A unit refused AFTER launch leaves `<unit>/`.** The brief's A7 writes `<unit>/unit-identity.json` before deciding,
   and A2's scratch tree lives under `<unit>/`, so the checker's existing unit-set guard speaks first. Measured:
   ```
   units.json hermes-acp reason: unit identity not observed: exe /usr/bin/python3.13 is not /usr/bin/e3-not-the-interpreter
   left in <root>/hermes-acp: ['scratch', 'unit-identity.json']
   runner's checker, first line: unit-declared-absent-but-present: hermes-acp
   ```
   A FAIL either way (never a pass); the first line is not the unit's own reason. Changing that guard is the
   coordinator's call; not changed.
5. **Texts the brief did not give** (additions; no brief text changed): `not-run|unit user unresolved (set S0_05_UNIT_USER)`,
   `not-run|unit scratch tree not writable by uid <n>: <path>`, the A6 detail `S0-01 path <realpath>` (the brief named
   the refusal but no text), A7's details (runner: every mismatch `; `-joined; checker: `unit-identity.json absent`,
   `<field> <value> is not the pin`, `uid 0`, `no pinned identity for this unit`, shape details), usage exits 64 for a
   malformed `S0_05_UNIT_USER` or override, exit 2 for a pins shape the runner cannot substitute into, `no-setpriv`, the
   claim-churn suffix (`namespace-live: ... (claim churn after 10 attempts)`, only after 10 failed claim attempts; the X3
   loser returns inside the loop with the exact brief text), and `egress: relay reach of <ns> not removed`.
6. **Stricter than the letter, in three places:** the checker refuses a pc-venue run unit that has no pinned identity
   (`no pinned identity for this unit`); the runner's A1 check for the pair covers the agent it launches as well as
   buzz-acp; the A7 record keeps all four Uid-line uids and any 0 refuses.
7. **Mutant kills were proven with `-k` selections of the named killers**, after a full-file collection per mutant; the
   full file ran green twice on the unmutated bytes.
8. **One existing assertion changed shape (named in its docstring, A1).** `test_shebang_matches_launch_interpreter`
   asserted each E2 row's target script exists (`target_path.is_file()`) and that its interpreter agrees with its
   shebang. A1 retires those rows: a row now NAMES a pin whose path lives on the PC, so existence cannot be read here.
   The static test is stricter on the row (a single pin name, no interpreter token at all); existence and digest moved to
   the runtime A1 check (`test_a1_unit_identity_mismatch_is_refused[absent]`, `[real-pins]`), and the interpreter
   agreement to the live record (`/proc/<pid>/exe` is the pinned interpreter in `test_runner_live_leg`).

Adjacent defects (outside the brief's items; reported, NOT fixed):
- `run_canaries.sh:29` does `$((ALLOWED_PORT + 1))` on the entry's port: overflow wraps and a subscript runs a command
  substitution (demo pasted in section 2). No production caller reaches it with an unvalidated entry.
- The runner's `trap cleanup EXIT INT TERM` (PC:283; the same line at the PIN) runs `cleanup` on SIGINT/SIGTERM and
  then CONTINUES. Measured with one real run:
  ```
  runner exit rc=1 1.2s after SIGTERM
  hermes-acp row after SIGTERM: launch exited within the settle window; see /tmp/e3-ej635r_7/evidence/hermes-acp.launch.lo
  the runner went on to its checker after SIGTERM: True
  ```
  An operator's stop does not stop the run (with two units it would start the next leg) and the interrupted unit is
  misreported. Fix shape: `trap 'exit 130' INT; trap 'exit 143' TERM` with `cleanup` on EXIT only.
- VERIFY-E2-R1 follow-ups F3 (name validation), F5 (`NS_LIVE` substring pruning), F6 (a non-UTF-8 reason empties
  units.json), F7 (`net_ino` never asserted) are unchanged; E3 adds no new substring pruning (its own `LOG_PIDS` list is
  pruned token-wise).
- Unmeasured on the PC: whether OmniRoute answers an unauthenticated `GET /v1/models` with 2xx (the collector's C0 needs
  2xx), and whether the relay answers the preflight's plain HTTP GET at all (curl without `-f` counts any HTTP answer).

## 10. NOT-done (first-class)

- NOTHING ran on the PC: no bridge use in this lane; every live step is the coordinator's (section 8).
- The pair cannot PASS the checker until run_canaries.sh records its full allow-set (DISCREPANCY 1).
- The S0-05 pair identity the relay accepts does not exist (CD1's open item); the runner only checks the file.
- The seed's second-assertion wording is untouched (the owner's).
- No commit, stage or push (the coordinator commits); S0-05 stays unminted; spec.json and the canaries are untouched.
- `shellcheck` is absent in the sandbox; not run.

## 11. Self-attack — the three most likely ways this change is wrong

1. **The stand-ins pass where the real units would not.** Ruled out as far as the sandbox allows: the hermes-acp
   stand-in fails exactly as CD1 probe 2 measured (`PermissionError: [Errno 1] Operation not permitted` on `/dev/null`
   stdin, epoll registration) and stops on EOF as probe 3 measured; the buzz-acp stand-in is a compiled ELF so A7 grades
   a real `/proc/<pid>/exe`, and the fd-3 key shim is exercised end to end (the key's digest arrives in the pair's and
   its child's environment, and is printed nowhere). NOT ruled out: the real relay's answer to the preflight GET and
   OmniRoute's `/v1/models` status (section 9, unmeasured on the PC).
2. **The X3 claim can double-own or wedge under a race the tests did not cover.** The two-creator stale race is tested
   deterministically (the loser paused between its read and its takeover; the winner's namespace inode is unchanged);
   a fresh concurrent claim is `link(2)`'s atomicity. The 10-attempt bound stops a spin. Declared limit, stated in the
   code: a third creator inside the microseconds between a loser's rename and its link-back.
3. **The relay reach leaks on the PC.** Removal is the first step of every teardown, so the leg's teardown, `cleanup`
   and the next create's destroy-first all delete it; E8 (removal dropped) and E9 (`route_localnet` left set) are killed.
   Residual, stated: a runner killed with SIGKILL (no trap) leaves the rule until the next create or destroy of
   `s0-05-buzz-acp`.
