NOT-READY — recommendation only. B4-01 is a qualifying blocker: the closure parser misses a variable-root output write and stays green.

Report saved: `tasks/briefs/s0-02-support/VERIFY-B4-report.md`

VERIFY-B4 — independent adversarial grade

PIN: `95c0bb19e22fae31582e7edecb48321591225433`
Role: adversarial-verifier
Venue: PC

Outcome

B4 closes B3-02 and B3-03 and kills the named B3-01 grammar mutants. However, B4’s claimed fail-closed parser has a reproducible variable-root bypass. It misses a runner-legal output write that neither enters the closure equality nor becomes `unrecognised`. B3-01 remains open.

NOT done: live eight-leg capture; revoked-leg relay membership write; EXPIRED→mint; S0-11 re-sign; live relay, ACP, or model requests. None was attempted.

File identity and gates

Verified file identity:

- `proofs/S0-02/check_buzz_authz.py`: 762 lines, `039e4170f1d80fb397ef86d41be8daa3cacdf858`
- `tests/test_s0_02_buzz_authz.py`: 1710 lines, `b2532d08fc41eb966dd12d85444c5dd02c39f40d`
- `proofs/S0-02/tools/pc/run_s0_02_legs.sh`: 205 lines, `3b5ebf178c482d0292558269d26cf6797e8f41d1`
- `proofs/S0-02/spec.json`: 26 lines, `5b061cd1303f8d4e688ba89b69919a62555436d0`

The B4 report’s historical build PIN is `6760808`, unavailable as a local abbreviated revision. Its required check/test blobs are byte-identical to this archive.

Four-file gate, PC venue exports, absolute scratch basetemp:

```text
207 passed in 95.97s (0:01:35)
pytest-exit: 0
pytest-summary: 207 passed in 95.97s (0:01:35)
```

Second independent run:

```text
207 passed in 95.03s (0:01:35)
pytest-exit: 0
pytest-summary: 207 passed in 95.03s (0:01:35)
```

Finding inventory

1. B4-01 — BLOCKER / SOLID

Contract mapping: B3-01 and the frozen B4 brief require `_runner_output_writes` to derive the checker closure table from every runner write and refuse every unrecognised `"$out/"` write. `T:1399-1451` makes that completeness claim; `T:1454-1475` binds parsed output to `C:143-152` `_LEG_FILES_PLAIN` and `_LEG_FILES_REVOKED`.

Canonical reproduction: against a fresh scratch archive, retaining the real closure test and mutating only the runner:

```bash
f="$out"; : > "$f/x-indirect"
```

The actual scratch emitter produced the file:

```text
INDIRECT-EMITTER: rc=0; exists=True
```

Adding that line to the runner left the exact closure test green:

```text
EDGE-VARIABLE-ROOT-BYPASS: rc=0; 1 passed in 0.13s
```

Mechanism: `_runner_output_writes` only finds literal `"$out/..."` at `T:1413`. The bypass has `"$out"` followed by `"$f/x-indirect"`, so it creates neither a parsed write nor an `unrecognised` entry. It is absent from the equality at `T:1465-1466`.

Material effect: a future runner can create an output that `_leg_closure` rejects at `C:155-167`, while the claimed runner/checker-table drift guard remains green.

Suggested fix: prohibit dynamic output-path construction and reject `$out` assignments, or expand the grammar so all output-path construction is represented and checked. Commit this surviving mutant as a regression test before another closure claim.

2. B4-02 — INFO / SOLID

The four B3-01 named mutants are killed through the actual closure test on fresh archives:

- `CLOSURE-POSITIVE`: pass, `1 passed in 0.32s`
- `RUNNER-TEE-UNSEEN`: killed, rc 1
- `RUNNER-HEREDOC-UNSEEN`: killed, rc 1
- `RUNNER-PYTHON-UNSEEN`: killed, rc 1
- `RUNNER-MV-UNSEEN`: killed, rc 1

Edge probes:

- `>>`, `cp -r`, `printf >`, and `cat >>` are parsed, then fail closure equality.
- `install`, direct variable-built full paths, and `Path(...).write_bytes` become unrecognised and fail.
- The root-variable bypass above survives.

3. B4-03 — INFO / SOLID

B3-02 now uses real values:

- `C:121-127`: `RELAY_DRIFT_WINDOW_S`, `LEG_CLOCK_TOLERANCE_S`, `REPLAY_CLOCK_TOLERANCE_S`
- `T:1593-1605`: imports checker constants and parses runner `TURN_WAIT_S` from `R:34`

Archive mutations killed:

- `TOLERANCE-9000`: rc 1
- `LEG-TOLERANCE-800`: rc 1
- `RELAY-WINDOW-200`: rc 1
- `RUNNER-GAP-151`: rc 1

A fresh archive with `TURN_WAIT_S=150` passed:

```text
1 passed in 0.33s
```

That is correct: the contract permits equality with replay tolerance, `150 <= 150`.

4. B4-04 — INFO / SOLID

B3-03’s fallback deletion is safe for the declared graded set.

`LEG_NAMES` includes revoked at `C:135`. `_check_bundle_uncapped` calls `_check_leg` for every non-replay leg at `C:677-685`. A missing revoked directory fails through `_require_real_dir` at `C:460-464`, before `removal_line` at `C:717`.

Controls:

- Missing revoked leg fails at `T:691-698`.
- Forced `None` note emits `; None` at `T:701-714`.
- Restoring the source fallback fails at `T:697`.
- Restoring fallback behavior fails at `T:714`.

No declared `S:6-25` `legs` entry supports a legitimate graded no-revocation path.

5. B4-05 — INFO / SOLID

Earlier B3 controls still hold:

- F1 real-directory guard: mutating `_require_real_dir` to `if False` is killed by `T:1349-1357`.
- F2 receipt truthiness mutation is killed by `T:1666-1696`.
- F3 has a test-strength gap: its current test ends at `T:1710` and is source-shape only.

A scratch F3 shape-guard bypass survived that source-only test. Direct constrained CLI execution then showed malformed 64-character nonhex input reaches `nv.sign_event` and raises before `_post` at `D:203`; no connection attempt appeared.

This is FOLLOW-UP only. The downstream signing consumer preserves pre-network refusal, but the test should execute the actual CLI against an owned local listener or deterministic post sink.

Named mutant disposition

| Mutant/control | Result | Killer/survivor |
| --- | --- | --- |
| CLOSURE-POSITIVE | PASS, rc 0 | `T:1454-1483` |
| RUNNER-TEE-UNSEEN | KILLED, rc 1 | `T:1465-1466` |
| RUNNER-HEREDOC-UNSEEN | KILLED, rc 1 | `T:1460`, `T:1465-1466` |
| RUNNER-PYTHON-UNSEEN | KILLED, rc 1 | `T:1465-1466` |
| RUNNER-MV-UNSEEN | KILLED, rc 1 | `T:1465-1466` |
| EDGE-APPEND | KILLED, rc 1 | `T:1465-1466` |
| EDGE-CP-R | KILLED, rc 1 | `T:1465-1466` |
| EDGE-INSTALL | KILLED, rc 1 | `T:1460` |
| EDGE-PRINTF-REDIRECT | KILLED, rc 1 | `T:1465-1466` |
| EDGE-VARIABLE-REQUESTED | KILLED, rc 1 | `T:1460` |
| EDGE-WRITE-BYTES | KILLED, rc 1 | `T:1460` |
| EDGE-CAT-APPEND | KILLED, rc 1 | `T:1465-1466` |
| EDGE-VARIABLE-ROOT-BYPASS | SURVIVED, rc 0 | parser blind at `T:1413` |
| TOLERANCE-9000 | KILLED, rc 1 | `T:1595-1598` |
| RUNNER-GAP-151 | KILLED, rc 1 | `T:1599-1604` |
| LABEL-FALLBACK-DROPPED source | KILLED, rc 1 | `T:697-698` |
| LABEL-FALLBACK-DROPPED behavior | KILLED, rc 1 | `T:701-714` |
| F1 real-dir tautology | KILLED, rc 1 | `T:1349-1357` |
| F2 accepted-truthiness | KILLED, rc 1 | `T:1666-1696` |
| F3 key-shape bypass | Survives source-only test | downstream `nv.sign_event` aborts before `_post` |

Verification and hygiene

- `python3 -m pyflakes proofs/S0-02/check_buzz_authz.py tests/test_s0_02_buzz_authz.py`: rc 0
- `bash -n proofs/S0-02/tools/pc/run_s0_02_legs.sh`: rc 0
- `git diff --check`: rc 0
- Production anti-pattern screen: 0 hits.
- Test anti-pattern screen: 11 documented source-shape and process-safety hits.
- No server actions, bridge calls, relay delivery, role-key reads, membership writes, process kills, shared-tree resets, checkouts, stashes, commits, or pushes.

Discrepancies

- First archive-copy mutation harness hit dangling vendored skill symlinks. Replaced with a fresh archive and runner-only mutations.
- Initial grammar-edge script had a Python multiline quoting error. Its output was discarded.
- A parallel boundary command used a directory before the terminal launcher could create it. It did not run; the isolated `TURN_WAIT_S=150` archive rerun passed.
- Final bounded report-lint output:

```text
report_lint: 55 refs — OK 34, NEAR 2, MISS 15, UNCHECKABLE 4, UNRESOLVED 0 (at 95c0bb1)
```

This was the final bounded round. Remaining heuristic misses are reported, not chased.

Gate recommendation

NOT-READY — B4-01 satisfies the full blocking predicate: frozen-contract conflict, canonical current-path reproduction, material false-green effect, deterministic surviving mutation, and current-component ownership.

Retro: verified defect. Run `/bug-echo` and add an anti-pattern registry row for literal-only parser coverage that does not reject variable-root propagation before another B3-01 closure claim.
