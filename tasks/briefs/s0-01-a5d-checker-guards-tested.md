# BRIEF — S0-01 lane A5d: every checker guard gets a killing test, the A20 v2.3 shutdown/teardown rules are enforced, the evidence walk is closed (47 VERIFY-CK7 findings)
PIN: (set at dispatch — scripts/pc_lane.sh refuses to run without a full SHA here)

You are the BUILD lane (Hermes on the PC, role code-implementer). honey: ultra. `.hermes.md` carries the project rules.
Your output is a PROPOSAL graded by the sandbox adversarial verifier; never self-accept. CONTEXT BUDGET: this brief +
the verify report + your three files fit one context — load no skills; read `docs/INCIDENT-LOG.md` only for the
2026-09-06 A21d/A20 rulings if a seam below needs them. Write `report-draft.md` in your lane dir as you go (AF-AP-16).

FIRST ACTION (halt loud on any mismatch): `git rev-parse HEAD` equals the PIN; `git log --oneline -1` subject starts
`S0-01 WIP checkpoint 7:`; tree clean. Reproduce the headline before changing anything: build the verifier's combined
mutant (24 guards each disabled with `if False and …` — the list is in `tasks/briefs/s0-01-a5d-support/verify-CK7.md`
§MUTATION AUDIT and §FINDINGS F1-F9) on a scratch copy and run the lane suite with xdist:
`$HOME/venv-agent-factory/bin/python -m pytest tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py tests/test_s0_01_pc_post_scan.py -q -p no:cacheprovider -n 8 --basetemp=<scratch>/tmp`.
The premise is `3 failed` (only the three A20a closure guards are gated). If more fail, STOP and report.

## What this lane is for
VERIFY-CK7 returned NOT-READY: 21 of 24 guards can be disabled with the suite green (the audit's own P1 repairs for
two-users concurrency, response cardinality and frame classes have NO regression test — F1-F9); the A20 v2.3 rules 4/5
are unenforced (a live pinned-tee process after shutdown or teardown is ACCEPTED, an empty declared owned set makes the
shutdown proof vacuous — F10-F17); a FIFO in the evidence tree hangs the checker forever (F19); leg directories have no
entry allowlist and the secret screen is presence-gated (F20-F21); blank lines are filtered instead of failed (F18);
records/receipts/startup lines are under-constrained (F22-F26, F30-F32); fixtures diverge from the producer (F33-F35);
~30 substring assertions violate A28 (F36-F37); dead guards (F40-F41); A26 residue (F42); the suite writes 4.7 GB of temp
per run (F43). Read the report in full; every finding id below maps to its section there.

## Coordinator rulings (binding)
- RED FIRST. For every guard the verifier disabled (F1-F9) write the test BEFORE touching the checker, using the
  verifier's attack and the EXACT reason it observed (the report pastes them); prove it red against the guard-disabled
  copy and green against the shipped checker. A test that cannot red on the disabled guard is not a test.
- F10/F11/F13/F14 (A20 v2.3 rules 4-5): on the SHUTDOWN leg the after-scan body must be EMPTY (any row = Failure
  naming pid + cmd) and `buzz_present=0` on BOTH scans (F12: read the teardown header's `buzz_present`); on EVERY leg
  the teardown body must be empty and `owned_present=0`; `owned-pids.json` has the exact shape `{buzz_acp_pid:int,
  owned:[int…], taken_at:str}` (F15), `owned` is non-empty and contains `buzz-acp.pid`, rid `tee_pid` and rid
  `agent_child_pid` on every leg (the shutdown leg included — F13/F14); the header's `buzz_acp_pid` equals
  `buzz-acp.pid` (F16); `pinned_present` equals the count of body rows whose cmd names a pinned path (F17).
- F18 (A8): blank or whitespace-only lines are a Failure in `timeline.jsonl`, `golden.jsonl` and scan bodies — remove
  the `if line.strip()` filters; the reason names file + line number, as the frames loader already does.
- F19: the evidence walk rejects any entry that is not a regular file or a directory (`stat.S_ISREG/S_ISDIR` on
  `lstat`; FIFOs, sockets, devices, symlinks → Failure naming the path) BEFORE any read; the CLI gets a wall-clock cap
  (`--timeout-s`, default 120, exit 70 with `checker timed out`), tested with a FIFO.
- F20/F21: each leg directory has an ENTRY ALLOWLIST (the required files + the optional ones the contract names;
  anything else → `<leg>: unexpected entry <name>`); `agent-stderr.txt` is REQUIRED in every positive leg (absent =
  Failure) and the secret screen runs on every leg unconditionally.
- F22-F26/F30-F32: upstream POST records accept ONLY the pinned body keys (extra keys → Failure); message roles are
  pinned (system/user/assistant in the fixture shape the real legs carry — read the real corpus under
  `proofs/S0-01/fixtures` or the committed legs for the shape and pin it, name the sample); GET records'
  `authorization_fingerprint` equals the pinned fingerprint; the startup line is matched EXACTLY against the pinned
  token set (unknown tokens → Failure); `mention_pubkeys` equals exactly the expected set (no extras, never empty);
  duplicate scan rows for one pid → Failure; `final` must be a bool (`is True`/`is False`); `stdin_reader_done` must be
  `True` when `final` is true. F27-F29 are contract-permitted boundaries: document them in the checker docstring.
- F28: `buzz-acp.exit` is pinned to `"0"` on every leg, not only shutdown (a non-zero exit is a Failure naming the leg).
- F33/F34/F35 (A27): the synthetic scan header is produced by RUNNING `proofs/S0-01/tools/pc/pc_post.sh scan` on a
  spawned process tree (see `tests/test_s0_01_pc_post_scan.py` for the pattern) — never hand-written; `_TEE_STATUS_KEYS`
  is replaced by `pins.PINNED_TEE_STATUS_KEYS` (already in `proofs/S0-01/pins.py`) and a test binds the committed
  `frame_tee.py`'s emitted key set to it by RUNNING the tee once; `check_tee_status` gets a real-leg test that skips
  with the exact reason `real leg predates tee-status.json (v2.2 capture)` until the corpus is re-captured.
- F36/F37 (A28): every reason assertion in the three test files is an exact full-line equality; the three real-leg
  `ok or <substring>` shapes become two-sided (assert the exact excused reason string, or ok, never a substring set).
- F38: the sequence-guard test omits a real (check, leg) invocation at the dispatcher (never a rename) and asserts the
  exact `first missing:` pair.
- F39: `_run_check` records the pair only when the check returned normally AND called at least one assertion helper —
  add a per-check assertion counter (`_asserted()` increments; a check that returns with zero assertions is a Failure
  `<check>:<leg>: check asserted nothing`). This is what makes F13's vacuous branch impossible by construction.
- F40/F41: delete the six dead presence gates (or convert each into a hard requirement with its own Failure reason and
  test); the `check_two_users` mentions guard keeps ONE reachable Failure site (in `check_mentions`).
- F42 (A26): the remaining startup literals (`mcp_cmd`, `permission_mode`, `expected_rt`) move to `pins.py` — but
  `pins.py` is coordinator-owned: PUT the three constants in your report as a proposed hunk and consume them from a
  local `_PINS_PENDING` dict with a TODO naming this ruling; the coordinator lands the pins hunk at the boundary.
- F43/F44 (suite economics): the `bundle` fixture builds ONE pristine bundle per session and gives each test a
  `cp -al` hardlink overlay (or a per-test `copytree` of ONLY the leg it mutates); target < 1 GB of temp per run;
  the suite must be xdist-safe (`-n 8` on the PC) — report wall time serial and with `-n 8`.
- Producer/consumer latent mismatch (report §FIXTURE-VS-PRODUCER): the consumer computes `owned_present` from body
  rows while the producer counts over the full table — the PRODUCER side is coordinator-owned (`pc_post.sh`); the
  checker keeps its body-row definition; report it, do not touch `pc_post.sh`.

## Deliverables (boundary — touch ONLY these paths)
1. MODIFY `proofs/S0-01/check_acp_conformance.py`.
2. MODIFY `tests/test_s0_01_check_acp_conformance.py`.
3. MODIFY `tests/test_s0_01_audit_cp5_controls.py` (only if a control's exact reason changes — say which).
`proofs/S0-01/pins.py`, `proofs/S0-01/tools/pc/pc_post.sh`, `tests/test_s0_01_pc_post_scan.py`, `negative_contract.py`
are READ-ONLY.

## Acceptance bar (the verifier's set is the bar)
The verifier's combined 24-guard mutant → 24/24 guards each killed by a NAMED test (paste the per-guard table: guard
→ test → exact red); every hostile bundle in F10-F32 → the exact Failure reason (paste the table); the FIFO hang → the
timeout/Failure within the cap; the real corpus subset (`-k real_leg`) → the same outcome table as the report's,
with the process-evidence skip and the negative skip unchanged; zero `in`/`startswith`/`or` reason assertions left
(grep and paste the count).

## Gate (paste verbatim into the report AND the commit body)
- `$HOME/venv-agent-factory/bin/python -m pyflakes proofs/S0-01/check_acp_conformance.py tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_audit_cp5_controls.py`
- The lane suite (three files) with the venv python, `-q -p no:cacheprovider`, TWICE serial and TWICE with `-n 8`,
  each with a dedicated `--basetemp` you delete afterwards; paste all four summary lines and the temp footprint (`du -sh`).
- Report fields: done (finding → test → red before / green after), the guard table, mutants killed/total, not_done
  (→ reason; an empty not_done beside any unmet item reopens the lane), files, summaries, pyflakes, discrepancies,
  adjacent defects (report only), the proposed `pins.py` hunk (F42).

Standing rules: no subagents; no outward-facing actions; long runs in ONE foreground call; never `git stash`/reset the
worktree; tests write only under tmp_path; every exact-text claim above is a hypothesis — verify at your PIN and STOP
LOUD on contradiction. Authorization context: defensive verification tooling on the owner's own system; the checker
grades the owner's own ACP evidence; no credentials are involved.
