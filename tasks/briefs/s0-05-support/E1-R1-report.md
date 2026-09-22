# E1-R1 — S0-05 mechanism guard repair

PIN: `953ccfe` · venue: PC, uid 1000 (no root/netns capability) · role: code-implementer · 2026-09-22.

**PROPOSAL ONLY.** The sandbox-side adversarial-verifier must grade this repair. I issue no gate verdict.

## OUTCOME

**Mechanically gated on this PC:** the checker now accepts exactly `veth-iptables` and rejects every other `gate.json` mechanism in PHASE 1, before gate state and before any canary is read (`C:78` `GATE_KEYS`, then working-tree lines 79-81 `MECHANISM`; `C:323-330` `# PHASE 1` / `read_gate` at the PIN, with the guard added immediately after it). The bare-unshare spec leg now names the class, `total-isolation: curl mechanism=netns-no-veth` (`S:33` `"leg": "negative"`, with the working-tree `failure_reason` at line 39). Six executable red-first controls became green; M1-M5 were compile-checked and killed.

**NOT run here:** the new root-only motivating-instance test through the REAL collector and checker (working-tree `T:795-862` `test_the_motivating_instance_is_a_total_isolation_class`; this range is beyond the 730-line PIN). The PC is uid 1000 and `ip netns add` fails `mkdir /var/run/netns failed: Permission denied`. The test is `NEEDS_NETNS`-skipped here. The sandbox harvest must run its red-on-PIN and green-on-repair legs.

**NOT done:** F2-F24 from VERIFY-E1 issue #13; live production units; minting/regenerating S0-05; any change to `L`, `R`, fixtures, provenance, PC runner, schemas, or attested outputs.

## 1. PREMISE — VERIFIED

### Identity before edits

| alias | file | PIN SHA-256 first 16 | lines |
|---|---|---:|---:|
| C | `proofs/S0-05/check_egress.py` | `59b884c6e60fa784` | 370 |
| T | `tests/test_s0_05_egress.py` | `6c96693ad4063c35` | 730 |
| S | `proofs/S0-05/spec.json` | `0751bf678f50349e` | 43 |
| L | `proofs/S0-05/netns_lib.sh` | `1b2bd911d54262d3` | 209 |
| R | `proofs/S0-05/run_canaries.sh` | `6f7298077aa39819` | 131 |

`git log --oneline 24e80e6..953ccfe -- proofs/S0-05 tests/test_s0_05_egress.py` was empty. HEAD was `953ccfedcaa54b2a8088d359f3d5342e91854989`; the worktree was clean.

The seed says bare unshare is total-block and not acceptable evidence (the seed's lines 434-435, including the literal `and is NOT acceptable evidence`). The library truthfully emits `veth-iptables` or `netns-no-veth` (`L:147-154`), and the collector records the observed value (`R:108-117`). At the PIN, `GATE_KEYS` required `mechanism`, but neither `read_gate` nor `check` asserted its value.

### Hollow green reproduced on the PIN

A copy of `evidence-mechanism-sandbox` with only `curl/gate.json` changed to `mechanism=netns-no-veth`:

```text
patched mechanism -> netns-no-veth
NOT run: buzz-acp — live unit runs on the PC (proofs/S0-05/tools/pc/run_s0_05_units.sh); NOT run in the sandbox
NOT run: hermes-acp — live unit runs on the PC (proofs/S0-05/tools/pc/run_s0_05_units.sh); NOT run in the sandbox
NOT run: memory-adapter — unit does not exist
NOT run: ai-memory — unit does not exist
NOT run: dream-foundry — unit does not exist
recorded: curl C4 example.com port 443 denied rc=7 — OSError [Errno 101] Network is unreachable
gate-fired: curl OUTPUT policy DROP 0 -> 10 packets
PASS: S0-05 no-direct-egress - 1 units, 11 canaries failed as required, positive controls 1/1
rc=0
Tue Sep 22 07:26:34 AM UTC 2026
```

Baseline on this PC: `98 tests collected in 0.10s`; `94 passed, 4 skipped in 2.60s`.

## 2. CHANGE

### Production guard

`MECHANISM = "veth-iptables"` is a one-value allow-list, tied to the producer's observed vocabulary (`C:78-81`, `L:147-154`). `check()` reads each gate, compares exact equality, and raises the class reason before testing `gate` state (`C:326-333`). PHASE 2 remains after it; `check_positive_control` and all later evidence checks are untouched (`C:335-340`). A non-string mechanism uses Python's string form in the reason.

Rejected alternative: a blacklist of only `netns-no-veth`. It would accept unknown or padded values and violate AF-AP-47. Ordering rationale: PHASE 1 must reject the inadmissible mechanism before the `gate-disabled` verdict and before PHASE 2 can report a downstream symptom.

### Tests and canonical spec

- Bare-unshare now fails by class while retaining the committed C0 rc-7 shape assertion (working-tree `T:138-146` `test_bare_unshare_bundle_is_red_as_total_isolation`; at the PIN this symbol had its old name).
- Fixture-mutation controls cover wrong, empty, list, and trailing-space values; exact equality and string rendering are pinned (working-tree T lines 149-165, `test_a_mechanism_mutation_is_rejected_by_class`; new after the PIN).
- The ORDER control combines wrong mechanism plus disabled gate and pins total-isolation first (working-tree `T:168-176` `test_total_isolation_precedes_a_disabled_gate`; new after the PIN).
- The canonical bare-unshare leg pins the new complete first line (`S:33` `"leg": "negative"`, with the working-tree `failure_reason` at line 39), consumed by `test_every_spec_leg_behaves_exactly_as_declared` (working-tree T lines 637-650; the same symbol is at PIN `T:605-618` `test_every_spec_leg_behaves_exactly_as_declared`).
- The live motivating-instance test creates the exact F1 class: isolated namespace, one internal addressed veth pair, loopback stand-in inside the namespace, REAL collector, REAL checker, PID-scoped listener cleanup, namespace destroy-by-name and final census (working-tree `T:754-862` `_in_ns_listener` / `test_the_motivating_instance_is_a_total_isolation_class`; new after the PIN). It asserts the collector observed `netns-no-veth`, gate enabled, and a successful C0 before asking the checker for the class reason (working-tree `T:838-852` `run_canaries.sh` / `run_checker`; new after the PIN).

## 3. RED-FIRST EVIDENCE

The new (a)/(b) controls were run against the unmodified PIN checker:

```text
FAILED tests/test_s0_05_egress.py::test_bare_unshare_bundle_is_red_as_total_isolation
  observed positive-control-failed: curl
FAILED tests/test_s0_05_egress.py::test_a_mechanism_mutation_is_rejected_by_class[wrong-mechanism]
FAILED tests/test_s0_05_egress.py::test_a_mechanism_mutation_is_rejected_by_class[empty-mechanism]
FAILED tests/test_s0_05_egress.py::test_a_mechanism_mutation_is_rejected_by_class[list-mechanism]
FAILED tests/test_s0_05_egress.py::test_a_mechanism_mutation_is_rejected_by_class[trailing-space-mechanism]
  observed rc 0 PASS
FAILED tests/test_s0_05_egress.py::test_total_isolation_precedes_a_disabled_gate
  observed egress-permitted: gate-disabled
6 failed, 98 deselected in 0.50s
PYTEST_RC=1
Tue Sep 22 08:08:06 AM UTC 2026
```

After the C guard:

```text
......                                                                   [100%]
6 passed, 98 deselected in 0.24s
PYTEST_RC=0
Tue Sep 22 08:11:00 AM UTC 2026
```

Spec-leg targeted run after the working-tree `failure_reason` change (S line 39):

```text
2 passed, 102 deselected in 0.22s
PYTEST_RC=0
Tue Sep 22 08:12:11 AM UTC 2026
```

The live (c) test cannot run on this host:

```text
SKIPPED [1] the new live test: network-namespace legs need root + iproute2 + iptables; NOT run here — they run on a capable venue (this sandbox has them; CI does not)
1 skipped, 103 deselected in 0.11s
PYTEST_RC=0
Tue Sep 22 08:15:09 AM UTC 2026
```

## 4. MUTATION AUDIT — scratch copy only

Scratch root: `/tmp/e1r1/mutant/repo`. Each mutant compiled with `python3 -m py_compile` before its named tests. Source checker SHA before and after the matrix: `5b766582a9a03f916201102d8b1f46dec4ce9bb294981bf17cb33be1eaaed0e6` — byte-identical restored.

| mutant | compile | killer output |
|---|---:|---|
| M1 delete guard | rc 0 | `6 failed, 98 deselected in 0.36s`; bare-unshare, four mechanism mutations, ORDER all red |
| M2 widen tuple to include `netns-no-veth` + `not in` | rc 0 | `2 failed, 3 passed, 99 deselected in 0.28s`; bare-unshare + wrong-mechanism red |
| M3 move guard after `check_positive_control` | rc 0 | `2 failed, 102 deselected in 0.19s`; bare-unshare regressed to `positive-control-failed`, ORDER regressed to `gate-disabled` |
| M4 rename reason to `mechanism-invalid` | rc 0 | `6 failed, 98 deselected in 0.50s`; (a), four (b) values and spec-leg consumer red |
| M5 `!=` → `is not` | rc 0 | **Killed**, not survived: `2 failed, 4 passed, 98 deselected in 0.32s`; both committed positive bundles falsely rejected as `total-isolation: curl mechanism=veth-iptables` |

M5 note: the brief allowed that it might survive, but this interpreter materialized distinct equal strings across module/JSON boundaries. The positive bundle tests killed it.

## 5. GATES ON FINAL BYTES

Set: `tests/test_s0_05_egress.py`; order-blind one-file set id equivalent: `9f0502080347`; collection: `104 tests collected in 0.05s`.

Run 1:

```text
Tue Sep 22 08:19:14 AM UTC 2026
99 passed, 5 skipped in 2.81s
Tue Sep 22 08:19:17 AM UTC 2026
PYTEST_RC=0
```

Run 2:

```text
Tue Sep 22 08:19:36 AM UTC 2026
99 passed, 5 skipped in 2.76s
Tue Sep 22 08:19:39 AM UTC 2026
PYTEST_RC=0
```

Mechanical count from `scripts/test_summary.sh`:

```text
Tue Sep 22 08:19:53 AM UTC 2026
pytest-exit: 0
pytest-summary: 99 passed, 5 skipped in 2.73s
Tue Sep 22 08:19:56 AM UTC 2026
TEST_SUMMARY_RC=0
```

The five skips are the four pre-existing root-gated namespace tests plus the new motivating instance. Other gates:

```text
PY_COMPILE_RC=0
PYFLAKES_RC=0
DIFF_CHECK_RC=0

python3 scripts/ap_screen.py proofs/S0-05
--- AP_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-32: 1
    working-tree C line 174: `return hashlib.sha256` over the canonical rule lines

python3 scripts/ap_screen.py proofs/S0-05 proofs/S0-05/canaries
--- AP_SCREEN over 2 path(s): 3 hits over 2 files ---
AF-AP-72: 2  canaries/connect_probe.py line 48
AP-32: 1     working-tree C line 174

python3 scripts/ap_screen.py --tests tests/test_s0_05_egress.py
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---
```

Classification by RUN: AP-32 is the pre-existing rules digest contract; the three-way digest behavior remains covered by the unchanged suite. AF-AP-72 is two pre-existing scanner matches on the one connect_probe.py line 48 numeric parse line; the file is untouched. No new screen hit.

Code-intel after the batch: GitNexus `detect-changes` reports 3 files, 7 symbols, risk medium, 2 affected processes. The lane context pack is `/tmp/e1r1/context-pack.md` (222 lines); GitNexus/CRG inside the lane wrapper were unmapped in this lane tree, while graft and ripwire ran. The pre-edit targeted GitNexus query for `Function:proofs/S0-05/check_egress.py:check` reported 2 upstream impacts, risk LOW, exact; the clone index was 439 commits stale, so that risk is advisory only.

## 6. FILE IDENTITY AFTER EDITS

| alias | file | final SHA-256 first 16 | lines |
|---|---|---:|---:|
| C | `proofs/S0-05/check_egress.py` | `5b766582a9a03f91` | 375 |
| T | `tests/test_s0_05_egress.py` | `7545714460183c94` | 873 |
| S | `proofs/S0-05/spec.json` | `ed6edbd1c408ad83` | 43 |
| L | `proofs/S0-05/netns_lib.sh` | `1b2bd911d54262d3` | 209 |
| R | `proofs/S0-05/run_canaries.sh` | `6f7298077aa39819` | 131 |

`git diff --exit-code 953ccfe -- proofs/S0-05/netns_lib.sh proofs/S0-05/run_canaries.sh proofs/S0-05/fixtures proofs/S0-05/fixtures/PROVENANCE.md proofs/S0-05/tools proofs/schemas` → rc 0. Only C, S, and T are modified. No fixture bytes, L, R, PC runner, provenance, schema, or attested output changed.

## 7. SELF-ATTACK

1. **Most likely wrong: the root-only live topology does not reproduce F1.** Ruled out only structurally here: it uses the verifier's observed link names (`ve1a`/`ve1b`), both ends inside one namespace with an on-link `/31`, the stand-in inside the namespace, and the REAL collector/checker. Not empirically ruled out on this PC. Sandbox execution is mandatory before acceptance.
2. **Mechanism rejection happens too late and another reason wins.** Ruled out by the combined wrong-mechanism + disabled-gate ORDER control, M3, and the source ordering at working-tree `C:326-335` `# PHASE 1` / `# PHASE 2` (at the PIN the same region starts at C:323).
3. **A malformed or merely padded mechanism slips through.** Ruled out by exact equality to one scalar and executable empty/list/trailing-space controls at working-tree `T:149-165` `test_a_mechanism_mutation_is_rejected_by_class`; M2 proves widening to `netns-no-veth` is detected.

## 8. DISCREPANCIES

- The brief names `tasks/briefs/s0-05-support/VERIFY-E1-report.md`; that file is not present at PIN 953ccfe. It exists in git commit `df04e61` (a later coordinator commit). I read that immutable object only to recover the exact F1 topology; I did not modify or copy it into the lane tree.
- The brief says the PIN baseline was `98 passed` with four root tests running in the sandbox. This PC baseline is `94 passed, 4 skipped`; after adding six collected controls (the four-value parameterization counts as four, plus ORDER, plus live (c)), final collection is 104 and this PC result is `99 passed, 5 skipped`.
- `scripts/pc_suite.sh set-id` is a sandbox bridge command and is forbidden on this PC by VENUE-MAP. I report the one-file list and its equivalent order-blind SHA first 12 (`9f0502080347`) instead.
- The brief expected `python3 scripts/ap_screen.py proofs/S0-05` to show all three known hits. The exact command scans one file and prints only AP-32. Passing both `proofs/S0-05` and `proofs/S0-05/canaries` reproduces the three known hits. No new hit exists.
- First `lane_context.sh` invocation used repeated symbols after one `-s`; its parser treated later symbols as FILE paths and refused rc 64. Corrected invocation repeated `-s` and wrote the 222-line pack. This is a command-shape discrepancy only.
- M5 did not survive; it was killed by both positive-bundle tests as above.
- `report_lint.py` final summary (bounded to two rounds): 19 refs — OK 13, NEAR 0, MISS 6, UNCHECKABLE 0, UNRESOLVED 0 (at 953ccfe). The six MISS are working-tree-only T ranges/symbols checked against the required PIN revision: `T:795-862` twice, `T:754-862`, `T:838-852`, and renamed/new symbols at `T:138-146`, `T:168-176`, `T:149-165`. The min-ref floor 12 passed (OK 13); rc remains 1 because the PIN cannot contain new working-tree lines. Per AF-AP-76, no third round.

## 9. HYGIENE / NOT-DONE

Final census on this PC: `ip netns list` produced no output, rc 0; `pgrep -af '[l]oopback_standin.py'` found none, rc 1. No root namespace was created by this lane. No server, container, owner process, bridge, secret, main clone, or other lane tree was touched. No commit, stage, push, reset, checkout, stash, tag, issue, comment, or proof-runner operation occurred.

NOT-done first-class: sandbox execution of the live test on both PIN and repaired checker; independent adversarial grade; F2-F24; live-unit legs; minting. Retro: the lane-context CLI quirk is already captured in DISCREPANCIES; no general project lesson to bake from this bounded repair.
