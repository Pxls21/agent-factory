# VERIFY-B8 — independent targeted adversarial verify of B8

Route: LOCAL verify route `agentfactory-verify-local`; the route is HYBRID in practice. A cloud step can serve a turn when the local step refuses with the chat-template 400. This report does not claim which model served a turn.

Role: adversarial-verifier. PIN: `b3eba6a`. Venue: `tasks/briefs/pc/VENUE-MAP.md`. Authorization: owner-authorized S0-02 test exercise only. All execution used lane-local scratch paths, closed loopback listeners, labelled launcher/delivery doubles, and `bwrap --unshare-all`; no live capture, relay, host launcher, container, or host secret file was touched. No commit, push, or repair.

## NOT-DONE

- No live Buzz → ACP → Hermes → OmniRoute capture ran. That remains prohibited by the brief.
- The two real AP/report findings below are follow-ups. They do not satisfy the B8 blocking predicate.
- This is a gate recommendation, not the coordinator's final decision.

## PREMISE — RE-MEASURED

| item | re-measured at b3eba6a |
|---|---|
| HEAD | `b3eba6ab79900c58529ff593031c34cf297aa014` |
| R | sha256[:16] `2f301973ee198a35`, 253 lines |
| D | sha256[:16] `9fdf8f3a87fa96b3`, 234 lines |
| T2 | sha256[:16] `3f341399d0cb4f1d`, 2437 lines |
| PP | sha256[:16] `92bf9609f54652d3`, 155 lines |
| test set | `1 files set=a5de0beef100` |

All four identities, every listed R/D/T2/PP anchor, and the set ID match the brief. Confirmed anchors include R:41/44/60/76/81/91/99/107/111/113/119/127/144/158/159/171/251, D:74/80/87/93/100/105/178, T2:2135/2190/2246/2280/2317/2354/2371/2414, and PP:107.

Initial gate on the PIN, PC declared inputs:

```
162 passed in 22.39s
pytest-exit: 0
pytest-summary: 162 passed in 22.39s
```

Result: premise reproduced. The brief's 70.82s is sandbox timing; same 162-count and set ID on PC.

## FINDING INVENTORY

### F-01 — FOLLOW-UP, SOLID — D2 postcondition guard lacks a behavioral negative control

- Contract mapping: pc-b8.md:21-23 requires both post-step conditions. The landing guard at R:105 implements that condition.
- Canonical path: exact R helper and an unshared full `main()` flow reproduce the discriminator. The unmodified producer does not exhibit marker loss.
- Material effect: with an injected external post-producer marker-loss fault, R landed returns rc=9 and copies nothing; mutant R copies the log and returns rc=0.
- Reproduction: postcondition mutant (`[ ! -f "$FD/buzzacp.exit" ] || …` → log-only) passes whole T2: `162 passed in 23.25s`. In a contained full-main control where exact PP masks then a labelled wrapper deletes only the exit marker, landed R gives `rc=9, masked=no`; mutant gives `rc=0, masked=yes`.
- Classification: no B8 blocker. The fault is injected into an external post-producer event, not reproduced from unmodified PP. The current task owns the missing behavioral regression test, so D-034 should add `masked log present + exit marker absent → rc 9, no copy`.

### F-02 — FOLLOW-UP, SOLID — builder report missed a new test-double AP row

- Contract mapping: none in frozen B8 criteria; report accuracy is still meaningful evidence hygiene.
- Canonical path: not applicable; test double only.
- Material effect: B8-report.md's combined AP claim is inaccurate, but evidence remains interpretable.
- Reproduction: `scripts/ap_screen.py R D T2` changes 889f1cc → b3eba6a from 9 to 10 rows. New row: AF-AP-40 at T2:2103, `if Path(os.environ['B8_TRACE']).exists() else 'deliver'`.
- Classification: no B8 blocker. This local test double controls trace-file append/init, not a production required-artifact check. D-034 should correct the report and classify this row explicitly.

### F-03 — FOLLOW-UP, SOLID — builder report misattributes m5/m6 killers

- Contract mapping: none in frozen B8 functionality; report accuracy only.
- Canonical path: N/A, mutation accounting.
- Material effect: named test attribution is false; current behavioral discrimination exists.
- Reproduction: whole-T2 m5 and m6 runs fail at T2:1725 `test_pc_runner_preflights_and_selects_the_s0_02_env_set` plus real-run T2:2394 `test_real_runner_rejects_commented_pin_before_creating_dest`. `test_main_orders_stop_post_and_masked_collection` does not kill either mutant, contrary to B8-report.md:86-94.
- Classification: no B8 blocker. D-034 should correct the mutation table.

### F-04 — FOLLOW-UP, SOLID — D1 substring counter differs from checker semantics

- Contract mapping: D1 freezes numeric `grep -c` repair, not JSON root-method parsing.
- Canonical path: helper only; no live emitter creates this nested shape.
- Material effect: a `session/update` JSON line with nested params `"method":"session/prompt"` makes R:81 count one and return success for `wait_turn_window 1`; S0-02 checker parses root `frame.method` at `proofs/S0-02/check_buzz_authz.py:178-190`.
- Reproduction: contained helper with nested object: grep count=1, `wait_turn_window 1` rc=0. Missing file, zero match, CRLF 3-match, and directory all remain numeric/fail-safe with no integer-expression error at want=0.
- Classification: no B8 blocker. Decide in D-034 whether runner observation must match checker identity; if yes, replace literal grep with intentional JSONL root-frame counting and add this negative control.

### F-05 — INFO, SOLID — preflight pins may be symlinks

- Contract mapping: none. Frozen contract requires exact content, not canonical file containment.
- Canonical path: real R main against scratch pins symlink.
- Material effect: exact pins via symlink passes and reaches labelled delivery.
- Reproduction: wrapper matrix below.
- Classification: INFO. Add root/canonical containment only if a future contract requires it.

## G1 — EXACT-VALUES PREFLIGHT

Real R:144 `main()` ran against scratch `S0_02_REPO` / `S0_02_PINNED`, a labelled launcher, and labelled delivery. No real host path was addressed.

| values-file shape | landed R:159 `grep -Fqx` | m5 `grep -Fq` |
|---|---|---|
| exact mapping plus trailing comment | rc=3, BLOCKER, DEST absent | rc=1 labelled refusal, DEST created |
| exact mapping plus extra key | rc=3, BLOCKER, DEST absent | rc=3, BLOCKER, DEST absent |
| leading `#` before exact mapping | rc=3, BLOCKER, DEST absent | rc=1 labelled refusal, DEST created |

T2:2394 already behaviorally kills m5 for commented suffix. Extra-key and leading-comment variants lack named tests, but frozen B8 requires one commented arm only. Follow up if preflight semantics are widened from exact line to exact mapping.

## MUTATION TABLE

Every mutation used only `../scratch/mutants/repo`, passed syntax/compile first, then ran whole T2 with PC declared inputs. Clean scratch baseline: `162 passed in 22.43s`.

| mutation | full T2 result | actual killer(s) | result |
|---|---|---|---|
| D1 old `grep … || echo 0` | 1 failed, 161 passed | T2:2135 `test_wait_turn_window_handles_absent_zero_and_n_matches` | KILLED |
| D2 old collector | 1 failed, 161 passed | T2:2190 `test_collect_leg_succeeds_before_masked_log_exists` | KILLED |
| D3 no marker cleanup | 1 failed, 161 passed | T2:2317 `test_launch_leg_removes_only_stale_owned_markers_before_launcher` | KILLED |
| scalar guard `if False` | 2 failed, 160 passed | T2:2345 `test_privkey_refuses_scalar_outside_range_before_signing`; T2:2371 `test_cli_refuses_empty_and_out_of_range_keys_before_connecting` | KILLED |
| m4 no `.strip()` | 3 failed, 159 passed | T2:1823; T2:2354 `test_cli_normalises_padded_and_uppercase_keys_before_connecting`; T2:2371 `test_cli_refuses_empty_and_out_of_range_keys_before_connecting` | KILLED |
| m5 exact-values grep mutant | 2 failed, 160 passed | T2:1725 `test_pc_runner_preflights_and_selects_the_s0_02_env_set`; T2:2394 `test_real_runner_rejects_commented_pin_before_creating_dest` | behavioral discriminator |
| m6 preflight ordering mutant | 2 failed, 160 passed | T2:1725 `test_pc_runner_preflights_and_selects_the_s0_02_env_set`; T2:2394 `test_real_runner_rejects_commented_pin_before_creating_dest` | behavioral discriminator |
| no `n=${n:-0}` | 1 failed, 161 passed | T2:2135 `test_wait_turn_window_handles_absent_zero_and_n_matches` | KILLED |
| invert 64-hex refusal | 2 failed, 160 passed | source-table attribution; T2:2207 `test_collect_masked_waits_for_post_step_and_keeps_refusal` | refusal discriminator |
| `rm -rf "$FD"` | 2 failed, 160 passed | T2:2317 `test_launch_leg_removes_only_stale_owned_markers_before_launcher`; T2:2414 `test_real_runner_passes_exact_pins_then_stops_at_labelled_deliver` | KILLED |
| scalar `< 1` → `< 0` | 2 failed, 160 passed | T2:2345 `test_privkey_refuses_scalar_outside_range_before_signing`; T2:2371 `test_cli_refuses_empty_and_out_of_range_keys_before_connecting` | scalar-bound discriminator |
| no `.lower()` | 2 failed, 160 passed | T2:1823; T2:2354 `test_cli_normalises_padded_and_uppercase_keys_before_connecting` | KILLED |
| remove loop-condition exit check only | 162 passed | R:105 still fails closed | equivalent |
| remove R:105 exit check | 162 passed | none | F-01 survivor |

## D2 REAL PRODUCER CHAIN

Contained `R:99 collect_masked` ran after exact PP: PP:107 `mask "$FD/buzzacp.raw.log" > "$FD/buzzacp.log"` turned two lowercase throwaway 64-hex strings into two `<HEX>` placeholders; `collect_masked` copied `buzzacp.log` and a 64-hex scan found zero raw tokens.

| contained frame state | R:99 result | copy |
|---|---|---|
| both `buzz-acp.exit` and masked log | rc=0 | masked copy, zero raw tokens |
| masked log, no exit | rc=9 `post step incomplete` | no |
| exit, no masked log | rc=9 `post step incomplete` | no |
| unmasked log with both files | rc=7 `REFUSING to keep` | deleted |
| neither post condition | rc=9 | no |

Full contained `R:144 main()` also ran with byte-identical R and PP: `main` returned `rc=0 dest=yes timeline=yes masked=yes hex=0 deliver=yes`. Its real `post_leg` and `collect_masked` order is `launch → deliver → wait → collect → stop → post_leg → collect_masked`; PP and R were production bytes.

## WRAPPER / D3 / ISSUE #15

Wrapper matrix:

| shape | rc | DEST | result |
|---|---:|---|---|
| keys present, values absent | 3 | absent | exact BLOCKER |
| exact values before keys | 1 | created | labelled delivery refusal |
| exact pins symlink | 1 | created | labelled delivery refusal |
| scratch repository without pins module | 3 | absent | grep missing-file then BLOCKER |
| sourced R | 0 | n/a | helpers defined; main not executed |

`S0_02_REPO` unset was deliberately skipped: R:22 defaults outside the lane (`/home/rocco/agent-factory`) and executing it violates pc-b8.md:11-12/93-95. The scratch missing-module case proves the same fail-closed property.

D3 hostile cases:

- A scratch pidfile naming verifier-owned `sleep 30`: R:60 `stop_leg` returned rc=5, refused `/usr/bin/sleep`, process stayed alive; verifier then terminated its own process.
- All three stale markers as symlinks to scratch sentinels plus a 150ms labelled launcher: R:41 `launch_leg` returned rc=0, fresh readiness appeared, and all targets survived.

Issue #15 real D CLI plus verifier-owned 127.0.0.1 listener:

| key | rc | connections | result |
|---|---:|---:|---|
| `0`×64, `f`×64, `nv.n` | 1 each | 0 | exact `SCALAR_REFUSE_TEXT` |
| `nv.n - 1` | 0 | 1 | accepted |
| padded uppercase valid scalar | 0 | 1 | normalized and accepted |
| 63 / 65 chars / nonhex final char | 1 each | 0 | exact shape refusal |

## GATES

```
2026-09-22T15:53:16Z
162 passed in 22.66s
pytest-exit: 0
pytest-summary: 162 passed in 22.66s

2026-09-22T15:53:44Z
162 passed in 22.40s
pytest-exit: 0
pytest-summary: 162 passed in 22.40s
```

Set beside both: `1 files set=a5de0beef100`.

```
bash -n R: rc=0
/home/rocco/venv-agent-factory/bin/python -m pyflakes D T2: rc=0
git diff --check: rc=0
```

AP screens:

- R/D/T2 combined: 10 rows: AP-1 ×7, AP-32 ×2, new test-double AF-AP-40 ×1 (F-02).
- T2 `--tests`: 11 unchanged rows at both pins: AF-AP-80 ×7 and AF-AP-34 ×4.
- R: 0 rows. D: AP-1 D:87, AP-32 D:108.

Discrepancy: system `python3` lacks pyflakes (`/usr/bin/python3: No module named pyflakes`); venue-map Python `/home/rocco/venv-agent-factory/bin/python` passed. This is an environment/tooling mismatch, not a code failure.

## ITEMS DELIBERATELY SKIPPED

- Live capture, live relay/launcher/container/secret paths: prohibited by the brief.
- `S0_02_REPO` unset path: defaults outside lane; prohibited.
- No speculative adjacent-component review.

## RETRO

F-01 is an AF-AP-80 pairing gap: a source/structure guard exists without the missing postcondition behavioral control. Coordinator should run `/bug-echo` and record the D-034 test addition; no skill change is proposed from this lane. F-02/F-03 are report-accuracy corrections, not new production bug classes.

## FOLLOW-UPS FOR D-034

1. Add F-01 behavioral test: R:99 `collect_masked` with masked log present and exit marker absent must return 9 and copy nothing.
2. Correct B8-report AP delta: combined screen gained test-double AF-AP-40 at T2:2103 `if Path(os.environ['B8_TRACE']).exists()`.
3. Correct B8-report mutation killer attribution: m5/m6 behavioral killer is T2:2394 `test_real_runner_rejects_commented_pin_before_creating_dest`, not ordering test T2:2280 `test_main_orders_stop_post_and_masked_collection`.
4. Decide whether R:81 `grep -c` must parse root-frame method identity; add nested-method negative control if yes.
5. Consider extra-key and leading-comment exact-value preflight cases if contract means exact mapping rather than exact line.

## GATE RECOMMENDATION

`MERGE-READY-WITH-FOLLOWUPS` — no finding satisfies all five blocker conditions. F-01 has a concrete, material mutation but relies on an injected external marker-loss fault not reproduced on unmodified PP; F-02/F-03 are report accuracy issues; F-04 is outside frozen D1 semantics. Recommendation is based on reproduced PC runs and contained production R/PP paths.
