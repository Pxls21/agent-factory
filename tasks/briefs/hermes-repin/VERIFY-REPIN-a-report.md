# VERIFY-REPIN-a report — adversarial verify of the Hermes lane-runtime pin (task #156)

STATUS: COMPLETE — gate recommendation NOT-READY (§10); written incrementally.
ROLE: adversarial-verifier, sandbox, read-only on the tree; every mutation ran in a scratch copy under /tmp.
PIN: 905bb1d (the REPIN-a landing). Measured at: c269263 (sandbox HEAD = local origin ref).

## 0. Premise — re-measured (item 1's precondition)

```
$ date -u
Wed Sep 23 08:29:50 UTC 2026

$ git rev-parse --short HEAD ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
c269263
c269263

$ git merge-base --is-ancestor 905bb1d HEAD; echo rc=$?
rc=0

$ git diff --stat 905bb1d HEAD -- upstream.lock.yaml tests/test_upstream_lock_lane_runtime.py | wc -l
0

$ git status --short        (the whole tree, read-only)
(empty)

$ git diff 905bb1d HEAD -- docs/HARNESS-PORTS.md | grep '^@@'
@@ -361,10 +361,21 @@ own git worktree, and leaves the final message in `report.md`.
@@ -384,6 +395,7 @@ starting a second one. Keyed on the STATE it intends to create, not on mutual ex
@@ -442,6 +454,38 @@ restart-when-idle --max-wait 1800`, then polls the deferred log for the exact pe

$ section 12 (heading line; sha256 of the text from the heading to EOF, first 16 hex)
905bb1d heading-line=684 section-sha=d06447ac04c3ccd4 total-lines=699
HEAD    heading-line=728 section-sha=d06447ac04c3ccd4 total-lines=743
WT      heading-line=728 section-sha=d06447ac04c3ccd4
```

PREMISE RESULT: HOLDS (SOLID). The component is byte-identical to the PIN at c269263: no diff in
`upstream.lock.yaml` or the test file since 905bb1d, a clean working tree, and §12 of
`docs/HARNESS-PORTS.md` unchanged (same section sha) but moved from line 684 to line 728 by three
hunks above it. 143 commits lie between the PIN and c269263; none touches the component.

## 1. Item 1 — the gates, reproduced (PYTHONDONTWRITEBYTECODE=1; the tree stayed clean)

```
$ date -u
Wed Sep 23 08:31:20 UTC 2026
$ bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py      (run 1)
8 passed in 0.13s
pytest-exit: 0
$ bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py      (run 2)
8 passed in 0.17s
pytest-exit: 0
$ bash scripts/pc_suite.sh set-id -- tests/test_upstream_lock_lane_runtime.py
1 files set=bbc177a039e2
$ bash scripts/verify-planning-repo.sh
planning repository verification passed        rc=0
$ python3 scripts/validate-ledger integrity --root .
S0-01 PRESENT  S0-02 ABSENT  S0-03 PRESENT  S0-04 PRESENT  S0-05 ABSENT  S0-06..S0-12 PRESENT
INVALID lines: 0        rc=0
$ bash scripts/test_summary.sh tests/test_s0_12_license_sbom.py
5 passed in 0.22s
pytest-exit: 0
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_12_license_sbom.py
1 files set=4c820c35fdc9
```

Result: SOLID. 8/8 twice (the same eight names, all PASSED), the set id matches the premise
(`bbc177a039e2`), the planning check passes, no proof is INVALID, S0-12 is 5/5. S0-02 and S0-05 read
ABSENT; neither is in this component (S0-05 is another lane's live work) — INFO only.

Re-check at 08:45Z: HEAD moved to af03aee during this lane; the component is still unchanged (0 diff lines
in the lock and the test since 905bb1d; §12 still at line 728 with section sha `d06447ac04c3ccd4`).

## 2. Item 2 — the golden of `selected_core.hermes-agent` (SOLID)

Mechanism: the golden is a parsed dict, not the entry's lines.
- `tests/test_upstream_lock_lane_runtime.py:18` defines `HERMES_AGENT_GOLDEN` as a Python dict of five values.
- `tests/test_upstream_lock_lane_runtime.py:35` loads the lock with `yaml.safe_load`.
- `tests/test_upstream_lock_lane_runtime.py:99` compares `entry == HERMES_AGENT_GOLDEN` (dict equality: blind to whitespace, quoting, key order, comments; PyYAML resolves a duplicate key last-one-wins).
- Its docstring at `tests/test_upstream_lock_lane_runtime.py:93` still calls this `byte-identical`.

Contract: `tasks/briefs/hermes-repin/REPIN-brief.md:13` requires the entry to be `byte-identical` to its
committed value, checked by "a golden of that entry's lines". Byte identity is in the contract, explicitly.

Mutation runs. Each mutant is a scratch copy under the session scratchpad (`m/<name>/`, driver `mut.py`); the
REAL test file runs under pytest, and the two real lock consumers run against the same mutant copy.

| mutant (lock lines 10-16 only) | the 8 tests | S0-12 `check_pin_diff.py` | `parse_lock` / `validate_pin_agreement` |
|---|---|---|---|
| G0 baseline | 8 passed | PASS | hermes-agent pin keyed `selected_core.hermes-agent`; ACP present; 24 entries; OK |
| G1 one trailing space after `  hermes-agent:` (whitespace only) | 8 passed — NOT caught | PASS | hermes-agent's pin re-keyed `selected_core.agent-client-protocol`; ACP DROPPED (23 entries); OK, silently |
| G2 trailing spaces on the five value lines | 8 passed — NOT caught | PASS | unchanged |
| G3 indentation 4 → 6 on the five value lines (whitespace only) | 8 passed — NOT caught | PASS | hermes-agent DROPPED (23 entries); OK, silently |
| G4 the commit value quoted | 8 passed — NOT caught | PASS | unchanged |
| G5 the five keys reordered | 8 passed — NOT caught | PASS | unchanged |
| G6 a comment line inside the entry (lines 13-15 shift down) | 8 passed — NOT caught | PASS | unchanged |
| G7 line 12 set to the LANE sha, a second `commit: 527da60…` added after `role:` | 8 passed — NOT caught | PASS (last wins) | unchanged (last wins) |
| G8 control: `observed_version: 0.21.1` | 1 failed (`test_hermes_agent_entry_unchanged`) | PASS | unchanged |

Answer to item 2: the test asserts a parsed dict. A whitespace-only edit is NOT caught (G1, G2, G3). Byte
identity is in contract. G8 shows the golden is not vacuous — it catches a value change — but it is weaker than
the contract, and the gap is material, not cosmetic:
- G1 and G3 are whitespace-only, yet they change a real consumer's output: `scripts/vendored_manifest.py:605` matches a component line with an exact `re.fullmatch`, and a line that does not match is skipped with no error (the fail-open itself is outside this boundary — F11).
- `scripts/vendored_manifest.py:610` requires exactly four spaces before `repository|commit`; G3's six spaces drop the hermes-agent pin from the SBOM agreement set, and `validate_pin_agreement` still passes.
- G7 moves the S0-01 commit on the line a reader sees (line 12) while PyYAML returns the later duplicate. The repository already guards this exact class for ai-memory at `proofs/S0-06/check_four_scope.py:217` (`text.count("\n  ai-memory:")`, its F-12).
- Proof artifacts cite this entry by LINE: `proofs/S0-08/check_containment.py:51` and `proofs/S0-08/CONTAINMENT-SPEC.md:3` (both name `upstream.lock.yaml` lines 10-15). A value golden does not hold those lines in place (G6).

## 3. Item 3 — the key set and the 40-hex control

Key set — CLOSED (SOLID). `tests/test_upstream_lock_lane_runtime.py:54` asserts `actual_keys == LANE_RUNTIME_EXPECTED_KEYS`.
- K1 an extra `foo: bar` → 1 failed (`test_lane_runtime_has_exact_keys`, message names `extra={'foo'}`).
- K8 the `verified:` line removed → 1 failed (the same test).
- K2 an extra `repository:` key → 1 failed (the same test). The closed set is load-bearing: with a `repository:` key, `parse_lock` maps the hermes-agent repository to the LANE pin (key `lane_runtime.hermes-agent-lane-runtime`) and `validate_pin_agreement` raises `pin disagreement` (F12, positive).

A bad commit IN THE FILE goes red by name (SOLID). A 39-hex, a 41-hex, an uppercase and a 7-hex commit each give
`2 failed, 6 passed`: `test_lane_runtime_commit_is_40_hex` and `test_lane_runtime_commit_value`. The messages name
the value (7-hex file, pasted):
```
AssertionError: commit is not 40 lowercase hex: 'b3399c1'
AssertionError: commit mismatch: got 'b3399c1', expected 'b3399c139624a0081d70397741a5b45f60fbe1f4'
```
The first message comes from `tests/test_upstream_lock_lane_runtime.py:64-65` (`commit is not 40 lowercase hex`).

The committed negative control is a constant, not a control (SOLID).
- `tests/test_upstream_lock_lane_runtime.py:113` overwrites the in-memory commit with the literal `"b3399c1"`.
- `tests/test_upstream_lock_lane_runtime.py:119` then asserts `not re.fullmatch(r"[0-9a-f]{40}", str(commit))` with its OWN copy of the regex. It never reads the file's commit and never calls the check it claims to control, so it cannot fail.
- On the K6 file (the file carries exactly the defect the control names), `test_short_commit_rejected` PASSED while the two positive tests failed.
- Mutant T1 — the positive regex weakened to `{7,40}` → on the real lock `8 passed`: the mutant SURVIVES; the negative control does not kill it.
- Mutant T2 — both commit checks deleted → a lock with a 7-hex commit gives `6 passed`, the negative control green. The control cannot see the loss of the guard it controls.
- Contract `tasks/briefs/hermes-repin/REPIN-brief.md:13`: "the negative control: an entry with a 7-hex commit → red by name". The committed test is never red and names nothing.
- The builder's claim at `tasks/briefs/hermes-repin/REPIN-a-report.md:98` ("The test passes, confirming the negative control is live") is false.

Further mutants (SOLID): K9 (`python` swapped to the proof runtime's 3.13.11) and K10 (`diff_from_proof_pin`
changed) → `8 passed` — these values are not pinned by any test; the contract did not require it (F7). K7 (a
second full `lane_runtime:` block appended, the first block's commit drifted to another 40-hex) → `8 passed`:
PyYAML returns the last block, while a first-match reader would read the drifted commit (F6).

## 4. Item 4 — consumers; the pin is UNENFORCED (SOLID)

Two instruments, both empty outside the test:
- graft (CLI, index present): `graft ask "who reads or parses upstream.lock.yaml …"` → `_lock` (S0-06), `parse_lock` (vendored_manifest), `main` (S0-12); two more asks on `lane_runtime` → no reader.
- grep: `grep -rln lane_runtime scripts proofs tests harness-ports .github` → only the test and its `.pyc`; over src, spikes, deploy, config, .claude, .agents → only the lock; `git grep -ln hermes-agent-lane-runtime` → docs, briefs, ledger, test and lock only.
- Every lock reader selects a named section: `proofs/S0-12/check_pin_diff.py:37` (`selected_core` and three more), `scripts/vendored_manifest.py:620` (`if repository and pin`), `proofs/S0-06/check_four_scope.py:213` (`upstream.lock.yaml`, ai-memory only), `scripts/fubuki_pin_sync.sh:23` (`fubuki-os`).
- A fifth reader the builder's table omits: `src/agent_factory/governance/pin.py:59` (`fubuki-os` only) — no effect on the conclusion.

Stated plainly: the pin is UNENFORCED until REPIN-b lands. Nothing reads `lane_runtime`. A `hermes update` on the
PC would move the lanes off b3399c1 and no check would fail. REPIN-b has not landed at af03aee (no reader in
`scripts/pc_lane.sh`). The dispatcher's binary is chosen at `harness-ports/bin/pc-lane.sh:71` (`HERMES_BIN:=hermes`,
from PATH, overridable).

§12 honesty:
- `docs/HARNESS-PORTS.md@c269263:742` names the drift check as `REPIN-b, pending` and says it "will" refuse. The gap is named, but only by implication.
- `docs/HARNESS-PORTS.md@c269263:734` opens with `What this pin covers` and names every `scripts/pc_lane.sh` dispatch. A record that nothing reads, for a binary any launch can override, is described as coverage.
- The ledger says it plainly (`todo/BUILD-TASKLIST.md@af03aee:156`: `the pin BINDS NOTHING until REPIN-b`); §12 does not.
- Verdict: not a hollow green (the pending check is named), but an overclaim of scope in the operator doc (F5).

## 5. Item 5 — internal consistency against the repository's primary sources

| fact | component | primary source | verdict |
|---|---|---|---|
| lane commit `b3399c1` | `upstream.lock.yaml:166` | `tasks/briefs/hermes-repin/REPIN-brief.md:12` (the measured full sha) | consistent (SOLID) |
| lane commit `b3399c1` | `upstream.lock.yaml:166` | D-043, `docs/08_DECISION_LOG.md@c269263:54` | consistent (SOLID) |
| lane `3.53.1` / `3.11.15` / 0.21.1 | `upstream.lock.yaml:167-169` | D-043, `docs/08_DECISION_LOG.md@c269263:54` | consistent (SOLID) |
| diff from the proof pin, `3939 files` | `upstream.lock.yaml:172` | D-043, `docs/08_DECISION_LOG.md@c269263:54` (31,816 commits) | consistent; not re-measured (no bridge) |
| proof pin `527da60`, observed 0.21.0 | `upstream.lock.yaml:12-13` | D-043, `docs/08_DECISION_LOG.md@c269263:54` (dist 0.21.0) | consistent (SOLID) |
| the `hermes update` of 2026-09-08, window from 14:2xZ | `upstream.lock.yaml:171` | `docs/INCIDENT-LOG.md@c269263:274` (repair 14:19Z; first new-runtime lane 14:22:31Z) | consistent (SOLID) |
| WAL needs SQLite `3.51.3` | `upstream.lock.yaml:171` | `docs/INCIDENT-LOG.md@c269263:273` (errors.log: 'Upgrade to SQLite 3.51.3+') | consistent (SOLID) |

Contradiction in the CONTRACT SOURCES (SOLID; not repeated by the component):
- `tasks/briefs/hermes-repin/REPIN-brief.md:8` says `The lanes left the pin on 2026-09-08` to escape "the SQLite 3.47.2 WAL-reset bug".
- `docs/INCIDENT-LOG.md@c269263:273` says the running lane Hermes (`~/.hermes/hermes-agent`) was at `58472d8` before the update, and `the linked SQLite 3.49.1` carried the bug.
- `spikes/hermes-lane-trial/result.json:24` records the lane Hermes on 2026-09-03 as `upstream 58472d80` (v0.21.0, 2026.8.31).
- So the lanes never ran the pin 527da60. They ran 58472d8 (the same 0.21.0 version string) until 14:19Z on 09-08, then b3399c1. VERIFY-B5j died on 3.49.1; 3.47.2 is the proof venv's SQLite (D-043).
- D-048 item 3 (`docs/08_DECISION_LOG.md@c269263:59`) rejects option (a) because "the pinned venv's SQLite 3.47.2 carries the WAL-reset bug that killed lanes". D-043 (`docs/08_DECISION_LOG.md@c269263:54`) is more careful: `NOT measured on 3.47.2`. The rejection may still stand (the errors.log asks for 3.51.3+), but the lanes were killed on 3.49.1. UNSURE whether 3.47.2 carries the bug: no repository source measures it.
- The component does not repeat this history: lock lines 162-173 and §12 say nothing about 3.47.2 or "left the pin" (F8, INFO + escalation).

Stale context (SOLID, outside the boundary):
- `CLAUDE.md@c269263:77` still says the shared state.db runs `journal_mode=DELETE` and names `hermes update` as the owner's pending lever.
- The incident log measured the switch to WAL (`docs/INCIDENT-LOG.md@c269263:274`, `journal_mode` read `wal`), and so did D-043. The new pin record now contradicts CLAUDE.md (F9).

## 6. Item 6 — the `verified:` field (`upstream.lock.yaml:173`)

The count reproduces (SOLID). The report's grep, run on the ledger at the PIN's parent (9c0a8adf5), prints 43,
identical line by line to the builder's `/tmp/repin/pc_stamps_final.txt`. At 905bb1d it prints 44; at HEAD 52.
The builder also left `pc_lane_stamps.txt` (30 entries) and `all_stamps.txt` (44): three variants, one pasted.

The grep does not count what `tasks/briefs/hermes-repin/REPIN-brief.md:12` defines ("ledger notes … `whose lane ran on the PC`"):
- The PC filter tests the whole ledger line, not the stamp. `todo/BUILD-TASKLIST.md@9c0a8adf5:76` (VERIFY-E1) is `the sandbox Opus 5 adversarial-verifier`; it passes only because the same line mentions E1-R1's PC brief.
- `todo/BUILD-TASKLIST.md@9c0a8adf5:96` (VERIFY-E1-R1, `a sandbox Opus 5`) is excluded because its line has no PC word. The same lane class goes in or out by accident.
- A non-lane note is counted: `todo/BUILD-TASKLIST.md@9c0a8adf5:127` (`AUDIT LANDED`, the findings document).
- A non-lane note is counted: `todo/BUILD-TASKLIST.md@9c0a8adf5:149` (`COUNCIL VERDICT LANDED`).
- A non-lane note is counted: `todo/BUILD-TASKLIST.md@9c0a8adf5:152` (`J1 SEED LANDED`, the Ouroboros seed).
- `todo/BUILD-TASKLIST.md@9c0a8adf5:38` (`RECAPTURE LANDED`) is the S0-01 v2.4 live capture: it runs the PROOF runtime 527da60 (D-043), so it is no evidence for b3399c1.
- `todo/BUILD-TASKLIST.md@9c0a8adf5:124` (`EVIDENCE LANES HOME`) is one note for four lanes whose venue the line does not state (UNSURE).
- PC lanes are missed when a parenthetical stands between the id and HOME: `todo/BUILD-TASKLIST.md@9c0a8adf5:324` (`VERIFY-O3 (S0-03 round 3 grade, local Qwen verify route`).
- Missed the same way: `todo/BUILD-TASKLIST.md@9c0a8adf5:339` (`VERIFY-B4 (S0-02 round 4 grade, local Qwen verify route`).
- Missed the same way: `todo/BUILD-TASKLIST.md@9c0a8adf5:343` (`VERIFY-M4 (S0-06 round 4 grade, local Qwen verify route`).
- Missed the same way: `todo/BUILD-TASKLIST.md@9c0a8adf5:347` (`VERIFY-O4 (S0-03 round 4 grade, local Qwen verify route`). The extraction holds no stamp at all for 2026-09-16..20 (by day: 09-08 3, 09-14 4, 09-15 2, 09-21 4, 09-22 30).
- The token `2` enters twice ("round 2 LANDED"): real PC lanes (O2, B2), but the id is lost and dedup keys on the hour.
- The date pattern has a hard upper bound (2026-09-22) and the field carries no ledger revision, so the same words re-run at HEAD give 52: the count does not carry its set (the AF-AP-73 rule).

Result: at least 5 of the 43 are not PC-lane notes (VERIFY-E1, AUDIT, VERDICT, SEED, RECAPTURE) and at least 4 PC
verify notes are missed. "43 PC-lane HOME/LANDED notes" is a stamp-format artifact under a PC label — a typed
number in disguise, by the brief's own test (F3). The builder's self-attack at
`tasks/briefs/hermes-repin/REPIN-a-report.md:108` says the count is `conservative because it deduplicates`; dedup
removes neither non-lane nor sandbox notes.
The ledger note repeats the number: `todo/BUILD-TASKLIST.md@af03aee:156` (`43 PC-lane HOME/LANDED notes`).

The field's first half (SOLID). `verified:` names `harness-ports/tests/run-all.sh (sandbox)`:
- `harness-ports/tests/run-all.sh:2-3` declares the suites need no Hermes: `LLM-free, no network, no harness` binary.
- CI runs the suite on a stock runner with only `pyflakes` and PyYAML: `.github/workflows/stage0-ci.yml:65` (`Run harness suites`).
- The sandbox has no Hermes (`which hermes` prints nothing; no `~/.hermes`). The suite cannot exercise b3399c1.
- D-048 item 3 (`docs/08_DECISION_LOG.md@c269263:59`) asks for `the harness-ports compatibility suite on the PC`; the REPIN brief (`tasks/briefs/hermes-repin/REPIN-brief.md:12`) prescribes `run-all.sh (sandbox)` instead. No REPIN increment runs anything on the PC against b3399c1, and neither the builder's report nor the landing commit pastes a run-all.sh run. This is a contract conflict the builder cannot repair (F4, CONTRACT-DEFECT).

## 7. Item 7 — report lint of the builder's report (pasted)

```
$ python3 scripts/report_lint.py tasks/briefs/hermes-repin/REPIN-a-report.md --root .
report_lint: 8 refs — OK 8, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
$ python3 scripts/report_lint.py --min-refs 8 --rev 905bb1d tasks/briefs/hermes-repin/REPIN-a-report.md --root .
report_lint: 8 refs — OK 8, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (at 905bb1d)
```
The 8 refs are the consumer-table citations and all resolve. The lint checks references, not claims. Claim audit:
- `tasks/briefs/hermes-repin/REPIN-a-report.md:12` says the test file has `103 lines`; it has 121 at 905bb1d (typed number, INFO).
- `tasks/briefs/hermes-repin/REPIN-a-report.md:13` says §12 took the doc `682 → 697`; it is 682 → 699 (typed number, INFO).
- `tasks/briefs/hermes-repin/REPIN-a-report.md:32` says the golden `independently asserts byte-identity` — false (F1).
- The claims at report lines 98 (negative control live) and 108 (count conservative) are false (F2, F3).
- Correction to my own first pass: I first read `/tmp/repin/pc_stamps_final.txt` as absent; my listing was cut by `head -5`. The file exists and matches my reproduction.

## 8. Finding inventory (no severity filter; the blocking predicate applied to each)

Predicate columns: (1) contract · (2) canonical path · (3) material · (4) discriminator · (5) in boundary.

**F1 — BLOCKER. The S0-01 golden compares parsed values, not the entry's lines.** SOLID.
- (1) `tasks/briefs/hermes-repin/REPIN-brief.md:13`: `byte-identical` (a golden of that entry's lines).
- (2) The real test file under pytest. The test finds the lock from its own location, so a scratch copy with the same layout is the production path.
- (3) The test's `byte-identical` claim (`tests/test_upstream_lock_lane_runtime.py:93`) and the builder's claim (`tasks/briefs/hermes-repin/REPIN-a-report.md:32`, `independently asserts byte-identity`) are false. Whitespace-only edits the golden misses change a real consumer (G1, G3 via `parse_lock`). A changed commit on line 12 hides behind a duplicate key (G7, the S0-06 F-12 class).
- (4) G1, G3 and G7 pass now; a lines golden turns them red. G8 stays red either way.
- (5) The test file.
- Fix: compare the entry's raw lines (from `  hermes-agent:` under `selected_core:` to the next two-space key) with a golden list of the six committed lines, byte for byte. Assert exactly one `  hermes-agent:` line in the file (the F-12 pattern at `proofs/S0-06/check_four_scope.py:217`, `ai-memory`). Keep the dict check as a second view. Optionally pin lines 10-15, which S0-08 cites.

**F2 — BLOCKER. The committed negative control is a constant.** SOLID.
- (1) `tasks/briefs/hermes-repin/REPIN-brief.md:13`: `the negative control` must make a 7-hex entry red by name.
- (2) The real test file under pytest; K6, T1 and T2.
- (3) The builder's evidence claim (`tasks/briefs/hermes-repin/REPIN-a-report.md:98`, "The test passes, confirming the negative control is live") is false. The control reads a literal (`tests/test_upstream_lock_lane_runtime.py:113`, `"b3399c1"`), not the file, and uses its own regex copy. It cannot fail, and it cannot detect the loss of the check it names.
- (4) T1 (the positive regex weakened) survives the suite. T2 (both commit checks deleted) lets a 7-hex lock pass 6/6 with the control green. A real control kills both.
- (5) The test file.
- Weight: the PROPERTY holds today through the positive tests (K3-K6 are red by name). F2 is about the committed control and its false evidence claim, not a live exposure. It is the most arguable of the three blockers; the coordinator may weigh it.
- Fix: one helper, used by both the positive test and the control, that raises `commit is not 40 lowercase hex: <value>`. The control writes a lock copy with `commit: b3399c1` and asserts the named failure with `pytest.raises(..., match=...)`. Add 39-hex, 41-hex, uppercase and non-string cases.

**F3 — BLOCKER. The `verified:` count is a stamp-format artifact under a PC-lane label.** SOLID.
- (1) `tasks/briefs/hermes-repin/REPIN-brief.md:12` defines the count as notes `whose lane ran on the PC`. D-048 item 3 asks for "the lanes' record".
- (2) The builder's exact grep, on the ledger at the PIN's parent 9c0a8adf5. It gives 43, identical to the builder's own file.
- (3) The pin's only durable evidence line states a false number: at least 5 of the 43 are not PC-lane notes, and at least 4 PC-lane notes are missed (§6). The landing commit and the ledger (`todo/BUILD-TASKLIST.md@af03aee:156`, `43 PC-lane HOME/LANDED notes`) repeat it.
- (4) The member list: ledger lines 38, 76, 127, 149 and 152 at 9c0a8adf5 are counted; lines 324, 339, 343 and 347 are missed.
- (5) The lock value at `upstream.lock.yaml:173` (`verified:`).
- Fix: a count whose rule matches the definition (a venue marker per note: a `pc-*.md` lane name, "local-Qwen", "PC Hermes lane", "cloud build/verify route"). Paste it with its ledger revision and member list. Or relabel the field truthfully, e.g. "43 ledger stamps matching <grep> at 9c0a8adf5, venue not classified". Coordinate the wording with F4's amendment: both touch the same field.

**F4 — CONTRACT-DEFECT (returned to the coordinator for an amendment; not the builder's to repair).** SOLID.
- `upstream.lock.yaml:173` records `harness-ports/tests/run-all.sh (sandbox)` as verification. That suite needs no Hermes binary (`harness-ports/tests/run-all.sh:2-3`, `LLM-free, no network, no harness`), and CI runs it on a stock runner (`.github/workflows/stage0-ci.yml:65`, `Run harness suites`). The sandbox has no Hermes. The suite cannot exercise b3399c1.
- The two frozen sources disagree. D-048 item 3 (`docs/08_DECISION_LOG.md@c269263:59`) asks for `the harness-ports compatibility suite on the PC`. The REPIN brief (`tasks/briefs/hermes-repin/REPIN-brief.md:12`) prescribes `run-all.sh (sandbox)`. No REPIN increment runs anything on the PC against b3399c1, and no run of run-all.sh is pasted anywhere in REPIN-a.
- Amendment options: (a) add a PC step: run a compatibility check against the real `~/.hermes/hermes-agent` at b3399c1 on the PC, paste it, and cite it in `verified:`; or (b) amend D-048 item 3 and the REPIN brief to drop the PC suite, and relabel the field truthfully (the dispatcher's unit suite, no Hermes binary, not runtime evidence).

**F5 — FOLLOW-UP. §12 overclaims scope.** SOLID (static reading plus the two-instrument reachability in §4).
- `docs/HARNESS-PORTS.md@c269263:734` (`What this pin covers`) presents a record that nothing reads as covering every dispatch. The pending drift check is named at `docs/HARNESS-PORTS.md@c269263:742` (`REPIN-b, pending`), so this is not a hollow green. The contract's three §12 elements are present (`tasks/briefs/hermes-repin/REPIN-brief.md:14`, `Lane runtime pin`).
- Fix: one sentence: "Until REPIN-b lands, the pin is a record only: nothing reads `lane_runtime`, and a `hermes update` or a `HERMES_BIN` override moves the lanes with no check failing."

**F6 — FOLLOW-UP (for REPIN-b's brief). Duplicate blocks are invisible to the tests.** SOLID (K7; G7 for the S0-01 entry, covered by F1's fix).
- PyYAML returns the last `lane_runtime:` block; a first-match reader returns the first. REPIN-b's drift check must read the lock the same way the test does, and refuse a second block (the F-12 precedent).

**F7 — FOLLOW-UP. Five of the eight values are unpinned.** SOLID (K9 and K10 pass 8/8).
- `python`, `role`, `reason`, `diff_from_proof_pin` and `verified` have no value test. The contract required keys, 40-hex, the golden and the control only. Fix: assert the whole expected dict.

**F8 — INFO (escalation for a wording correction in the contract sources).** SOLID; the 3.47.2 bug status is UNSURE.
- `tasks/briefs/hermes-repin/REPIN-brief.md:8` (`The lanes left the pin on 2026-09-08`, "the SQLite 3.47.2 WAL-reset bug") and D-048's rationale ("the pinned venv's SQLite 3.47.2 carries the WAL-reset bug that killed lanes", `docs/08_DECISION_LOG.md@c269263:59`) contradict `docs/INCIDENT-LOG.md@c269263:273` (lane Hermes at `58472d8`, `the linked SQLite 3.49.1`) and `spikes/hermes-lane-trial/result.json:24` (`upstream 58472d80`). The lanes never ran 527da60. The component does not repeat the error.

**F9 — FOLLOW-UP (outside the boundary; stale since 2026-09-08 14:22Z).** SOLID.
- `CLAUDE.md@c269263:77` still says the shared state.db is `journal_mode=DELETE` and that `hermes update` is the owner's pending lever. The incident log and D-043 measured WAL. The new pin record contradicts it.

**F10 — INFO. The builder's report carries typed numbers.** SOLID.
- `tasks/briefs/hermes-repin/REPIN-a-report.md:12` says `103 lines` (the file has 121). `tasks/briefs/hermes-repin/REPIN-a-report.md:13` says `682 → 697` (it is 682 → 699). Three grep variants (30, 43, 44 entries) exist in `/tmp/repin/`; one is pasted. Lint is 8/8 OK; lint checks references, not claims.

**F11 — FOLLOW-UP (outside the boundary; a real pre-existing defect found on a gate path).** SOLID.
- `parse_lock` skips a line it does not recognize, with no error (`scripts/vendored_manifest.py:605`, `re.fullmatch`). G1 dropped ACP and G3 dropped hermes-agent from `validate_pin_agreement`, which still returned OK. `vendored_manifest.py --check` runs in the pre-commit and pre-push hooks.
- S0-12 (`proofs/S0-12/check_pin_diff.py:34`, `yaml.safe_load`) still covers the SBOM pins for its four sections, so the exposure is partial.
- Needs its own task, `/bug-echo` and a registry row (the coordinator's call). Not caused by REPIN-a.

**F12 — INFO (positive). The closed key set is load-bearing.** SOLID (K2).
- A `repository:` key would make `parse_lock` take b3399c1 as the hermes-agent pin, and `validate_pin_agreement` would raise.

**F13 — INFO.** `validate-ledger integrity` reads S0-02 and S0-05 ABSENT. Neither is in this component (S0-05 is another lane's live work).

**F14 — INFO.** `upstream.lock.yaml:2` (`snapshot_date`) predates the lane entry, and the entry has no measured-at field. The measurement time (2026-09-22 17:0xZ) lives only in the REPIN brief. Adding a key needs a contract change (the key set is closed).

**F15 — INFO.** `upstream.lock.yaml:170-171` use ASCII arrows and comparisons (`scripts/pc_lane.sh -> hermes on the PC`, `SQLite >= 3.51.3`) where the brief wrote → and ≥. No consumer reads these values.

**F16 — INFO.** The entry has no `repository:` key, by the contract's key list. The repository is implied by the name and by D-043. This is deliberate (F12).

**F17 — INFO.** The premise holds, and item 1's gates are green (§0, §1).

## 9. What I reproduced, what I read statically, what I skipped

- Reproduced: item 1 (all gates); item 2 (G0-G8 through the real test file and both real consumers); item 3 (K1-K10, T1, T2); item 4 (graft three times, grep over the named directories and wider); item 6 (the exact grep at three revisions, identical to the builder's file; every member classified from its ledger line); item 7 (lint at the worktree and at 905bb1d).
- Read statically: item 5 (consistency against D-043, D-048, the incident log and the spike record); §12 honesty; the stale-context sweep.
- Skipped, and why: PC-side re-measurement (no bridge, by the brief; the values agree with every repository source but are not re-measured). Running `run-all.sh` (its own header and CI's definition show it needs no Hermes; a run here could write into the tree and would not change F4). REPIN-b (not landed). A full-stack thermo-nuclear review (not asked for a single-increment verify). Writing a registry row or a bug-echo for F11 (outside my boundary).
- Mutation hygiene: every mutant ran in the scratchpad (`m/<name>/`); the tree is untouched except this report (`git status --short` shows only this file).

## 10. GATE RECOMMENDATION

**NOT-READY.** F1, F2 and F3 each meet the whole blocking predicate:
- F1: the golden compares values, where the contract says bytes and lines.
- F2: the negative control is a constant.
- F3: the `verified:` count is mislabeled.

All three fixes are small and sit inside the landed files: the test file for F1 and F2, one lock value for F3. That fits ONE focused repair under D-031. F4 goes back to the coordinator as a CONTRACT-DEFECT: the frozen sources disagree on the compatibility suite (D-048 says on the PC; the REPIN brief says sandbox). The builder should not repair F4 alone. Decide F4's amendment before or with F3's repair, since both change `verified:`.

This recommendation does not depend on anything I did not reproduce. The PC-side values (the commit, 0.21.1, 3.11.15, 3.53.1, 31,816 commits, 3939 files) agree with every repository source but were not re-measured.

STATUS: COMPLETE (2026-09-23; measured at c269263; the component re-checked unchanged at af03aee and at 2407b68).

Lint (round 2 of at most 3): `python3 scripts/report_lint.py --min-refs 8 tasks/briefs/hermes-repin/VERIFY-REPIN-a-report.md --root .` → `report_lint: 95 refs — OK 95, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`, rc 0. Round 1 had 5 MISS and 2 NEAR: `docs/INCIDENT-LOG.md` moved two lines during this lane (fixed by pinning moving-doc refs to c269263), and two report lines lacked a same-line token.
