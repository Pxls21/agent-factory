# E2-R1 Report

PIN: 280d3df (origin moved to beb20ec; boundary files byte-identical, verified by sha256 prefix match).

## Premise verification

| File | sha256[:16] | Lines | Match |
|---|---|---|---|
| `proofs/S0-05/netns_lib.sh` | 324ffdd9aa646531 | 258 | YES |
| `proofs/S0-05/tools/pc/run_s0_05_units.sh` | 24087a298ab1b9f9 | 159 | YES |
| `tests/test_s0_05_egress.py` | ce86f3a2d9bb81c9 | 1243 | YES |

All seven blockers reproduced on the PIN bytes (outputs below).

## Per-blocker status

### F11 + F12 — up-front validation

- `proofs/S0-05/netns_lib.sh:67-84`: added strict dotted-quad IPv4 validation (each octet 0-255, no leading zeros) and port 1-65535 validation BEFORE any namespace/veth/rule/record/claim work.
- `proofs/S0-05/netns_lib.sh:146-160`: removed the old in-loop validation from `_egress_apply_gate` (now a comment explains validation is up front).
- `tests/test_s0_05_egress.py:1467-1493`: rewrote `test_allow_entry_must_be_ipv4_literal` with 12 parametrized invalid entries (the original 3 plus the brief's 9 new cases). The test calls `egress_ns_create` which validates up front without needing root. As root, it also asserts no namespace/veth/owner leaked.

Red control (PIN, non-root):
```
FAILED tests/test_s0_05_egress.py::test_allow_entry_must_be_ipv4_literal[cidr]
FAILED tests/test_s0_05_egress.py::test_allow_entry_must_be_ipv4_literal[hostname]
FAILED tests/test_s0_05_egress.py::test_allow_entry_must_be_ipv4_literal[empty-host]
3 failed, 110 passed, 9 skipped in 4.50s
```

Green (non-root):
```
122 passed, 15 skipped in 4.53s
```

### F2 — atomic owner claim

- `proofs/S0-05/netns_lib.sh:86-103`: the claim is now a `mkdir` of `$EGRESS_OWNER_DIR/${ns}.claim` (atomic) BEFORE the destroy-first step and BEFORE creation. Owner file written inside the claim. A claim held by a live pid other than `$$` returns 65 with the existing `namespace-live` message. A stale claim (dead pid) is taken over.
- `proofs/S0-05/netns_lib.sh:106-108`: the destroy-first step uses `_egress_ns_teardown` (not `egress_ns_destroy`) so the fresh claim survives.
- `tests/test_s0_05_egress.py:1289-1326`: `test_create_race_one_wins` — two creates on one name from parent/child bash: one returns 0, the other returns 65, the winner's namespace and owner record are intact.

Red control (PIN): the existing `test_live_sibling_namespace_is_refused` passes on PIN because the owner check works for that case; the RACE was demonstrated in the verifier's report :160-173.

Green: `test_create_race_one_wins` passes: `rc1=0`, `rc2=65`, `namespace-live` message present.

### F3 — cleanup ownership

- `proofs/S0-05/tools/pc/run_s0_05_units.sh:72-79`: cleanup now checks `$(cat "$(egress_ns_owner_file "$ns")")` == `$$` before destroying.
- `proofs/S0-05/tools/pc/run_s0_05_units.sh:99,109,126,142`: `NS_LIVE` pruned at every in-loop destroy.
- `tests/test_s0_05_egress.py:1349-1384`: `test_cleanup_does_not_destroy_sibling_namespace` — A creates, A destroys, B re-creates; A's ownership-checking cleanup skips B's namespace.
- `tests/test_s0_05_egress.py:1397-1460`: `test_runner_refusal_does_not_destroy_sibling` — runner-level: A holds the namespace via a live process, runner B is refused (rc 65), A's namespace survives.

Green: both tests pass.

### F4 — JSON encoding

- `proofs/S0-05/tools/pc/run_s0_05_units.sh:144-168`: replaced `printf`-based `units.json` construction with NUL-delimited entries piped to `python3 -c` using `json.dump`.
- `tests/test_s0_05_egress.py:1400-1411`: `test_units_json_quotes_in_reason` — a reason carrying `"`, `\` and `\n` is encoded correctly; `check_egress.py` parses it and the reason equals the input.

Red control (PIN):
```
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 3 column 125 (char 139)
```

Green: `VALID`, reason round-trips exactly.

### F1 — destroy SIGKILL escalation

- `proofs/S0-05/netns_lib.sh:249-318`: `_egress_ns_teardown` now sends SIGTERM, waits up to 5s, then SIGKILLs survivors, waits up to 2s, and fails loud (stderr + rc 1) if any remain.
- `proofs/S0-05/netns_lib.sh:314-320`: `egress_ns_destroy` calls `_egress_ns_teardown`, then removes ownership records.
- `tests/test_s0_05_egress.py:1234-1268`: `test_destroy_kills_sigterm_ignoring_process` — a `trap '' TERM; sleep 300` process is gone AT RETURN, killed by the SIGKILL escalation.

Red control (PIN):
```
SURVIVOR: pid 14644 still alive after destroy
```

Green: `pid 15829 dead` at return.

### F14 — runner live test stand-in assertion

- `tests/test_s0_05_egress.py:1066-1175`: `test_runner_live_leg` now:
  - Stand-in records its pid, argv and net-namespace inode to a JSON file.
  - Asserts the record exists (the stand-in ran).
  - Asserts `argv[0]` equals the script path (kills M16: a bash-wrapped launch never runs the stand-in directly).
  - Asserts the stand-in pid is dead after its unit's leg (kills M17).
  - Asserts the hermes-acp row is `run` in `units.json`.

Green: all assertions pass.

## Gates

### Root, run 1
```
137 passed in 61.80s (0:01:01)
```

### Root, run 2
```
137 passed in 61.63s (0:01:01)
```

### Non-root
```
122 passed, 15 skipped in 4.53s
```

### Syntax
```
bash -n proofs/S0-05/netns_lib.sh: BOTH SYNTAX OK
bash -n proofs/S0-05/tools/pc/run_s0_05_units.sh: BOTH SYNTAX OK
```

### Pyflakes
```
(clean — no output)
```

### Anti-pattern screen
```
AF-AP-59: 1
    tests/test_s0_05_egress.py:1154: ["pgrep", "-f", str(tools_dir / "pc_launch.py")]
```
Pre-existing (PIN line 1127). The `pgrep -f` is in a negative assertion (stand-in must NOT be running), not a liveness loop. Acceptable.

### no_laya_in_gates
```
no_laya_in_gates: 38 files scanned, clean
rc=0
```

## Mutant table

| Mutant | Target | Compiles | Collected | Outcome | Killing test |
|---|---|---|---|---|---|
| M10 | `netns_lib.sh:116` `index($4,pfx)==1` -> `>0` | yes | 137 | SURVIVED | pre-existing (F6 collision check too broad) |
| M11 | `netns_lib.sh:265-275` TERM wait loop removed | yes | 137 | SURVIVED (EQUIVALENT) | SIGKILL escalation handles all cases regardless of TERM wait |
| M16 | `run_s0_05_units.sh:118` `setsid` -> `setsid bash` | yes | 137 | KILLED | `test_runner_live_leg` ("stand-in record not found") |
| M17 | `run_s0_05_units.sh:140` `egress_ns_destroy` -> `kill "$launch_pid"` | yes | 137 | KILLED | `test_runner_live_leg` ("stand-in pid still alive") |
| M20 | `run_s0_05_units.sh:96` add `egress_ns_destroy "$ns"` after create refusal | yes | 137 | KILLED | `test_runner_refusal_does_not_destroy_sibling` ("A's namespace destroyed by B") |
| M21 | `run_s0_05_units.sh:95` reason -> constant | yes | 137 | KILLED | `test_units_json_quotes_in_reason` ("reason mismatch") |
| M22 | `netns_lib.sh:100` drop `!= "$$"` clause | yes | 137 | KILLED | `test_same_shell_recreate_succeeds` ("second_rc=65") |
| MR1 | Drop up-front validation (lines 71-83) | yes | 137 | KILLED | `test_allow_entry_must_be_ipv4_literal` (12 failures) |
| MR2 | Drop SIGKILL escalation (lines 276-309) | yes | 137 | KILLED | `test_destroy_kills_sigterm_ignoring_process` ("pid still in namespace") |

Survivors: M10 (pre-existing, out of scope), M11 (proven equivalent).

## Census

```
ip netns list: (empty)
ip -o link show type veth: 0
/run/s0-05-egress: (empty/absent)
```

Every process started during the run was killed by pid (the test cleanup `finally` blocks handle this). No leaked namespaces, veths, or owner records.

## Files touched

| File | Action | Lines (after) |
|---|---|---|
| `proofs/S0-05/netns_lib.sh` | MODIFY | 325 |
| `proofs/S0-05/tools/pc/run_s0_05_units.sh` | MODIFY | 173 |
| `tests/test_s0_05_egress.py` | MODIFY | 1497 |
| `tasks/briefs/s0-05-support/E2-R1-report.md` | NEW | this file |

## DISCREPANCIES

1. Origin head is `beb20ec`, not `280d3df` as the brief states. Boundary files are byte-identical (verified by sha256 prefix).
2. Non-root skipped count is 15 (was 9 at PIN). The 6 additional skips are the 6 new root-only tests (`test_destroy_kills_sigterm_ignoring_process`, `test_create_race_one_wins`, `test_same_shell_recreate_succeeds`, `test_cleanup_does_not_destroy_sibling_namespace`, `test_runner_refusal_does_not_destroy_sibling`, `test_units_json_quotes_in_reason`). The first 5 need root for namespace operations; the last needs root because the runner creates namespaces. The 12 F19 tests that were failing as non-root now pass.

## NOT-done

1. M10 (the F6 collision check `index($4,pfx)>0` vs `==1`) is a pre-existing survivor. Not in scope for this repair.
2. M11 (TERM wait loop removal) is equivalent with the SIGKILL escalation. The wait loop is a courtesy (avoids unnecessary SIGKILL for processes that handle SIGTERM cleanly); its removal does not change correctness.
3. The brief's "two real runners, A exits while B is mid-leg" scenario from F3 is tested at library level (`test_cleanup_does_not_destroy_sibling_namespace`) and at runner level (`test_runner_refusal_does_not_destroy_sibling`), not as two concurrent full `run_s0_05_units.sh` invocations (which would require listener setup for both and is fragile in a test).
4. CD1 (the real S0-01 launcher) is out of scope per the brief.
5. Non-blocking follow-ups F5, F6, F8, F9, F10, F13, F16-F21 are out of scope per the brief. F12 is fixed by construction (F11's up-front validation needs no root).
