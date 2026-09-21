# PC lane — VB-F12-G1 (the S0-01 golden made ORDER-FREE for asynchronous session-metadata notifications — owner decision (a), 2026-09-21)

PIN: 772ce3b

Role: code-implementer. Route: the LOCAL Qwen build route (the pc_lane.sh default for code-implementer; do NOT set
HERMES_MODEL). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Report: draft after EACH item at
`tasks/briefs/s0-01-vb-f12-support/G1-report.md`, return it whole as your final message.

## Why (the owner's decision; measured facts at the PIN)
AF-AP-107 (docs/INCIDENT-LOG.md, the 2026-09-21 entry, item 7): the pinned hermes-acp emits the `session/update`
notification whose `update.sessionUpdate == "session_info_update"` from an independent task, so it lands at a
different position in run-1 (before the first agent_message_chunk) and run-2 (after the end_turn response). The
frozen checker fails the REAL v2.4 bundle at exactly ONE check, `check_golden` (C:1533-1538):
`failure_reason: golden: golden mismatch between run-1 and run-2 at normalized line 7`; every check ahead of it
passes on the real evidence. The owner decided (a): the normalizer makes asynchronous session-metadata
notifications ORDER-FREE, the golden is regenerated from THIS bundle (no recapture) and pinned. A contract change
decided by the owner — not a round-19 bypass fix (D-034 stands).

Aliases: C=proofs/S0-01/check_acp_conformance.py · P=proofs/S0-01/pins.py · T=tests/test_s0_01_check_acp_conformance.py
· S=tests/test_s0_01_spec_runner.py · G=proofs/S0-01/evidence/golden/golden.jsonl

## The design (implement EXACTLY this; a different shape is a FINDING to report, never a choice to make)
1. P: `ASYNC_SESSION_UPDATES = ("session_info_update",)` — the CLOSED set of `sessionUpdate` kinds the pinned
   hermes-acp emits asynchronously (measured 2026-09-21 on run-1/run-2; a new kind is a pins change with its own
   measurement). Import it in C beside the other pins (the import block around C:62).
2. C `normalize_timeline` (C:794-861): every record's SHAPE stays byte-identical; change ONLY the order rule and
   the placeholder assignment:
   - An entry is ASYNC iff `dir == "a2c"`, it is a notification (`"method" in o and "id" not in o`),
     `o["method"] == "session/update"` and `params.update.sessionUpdate in ASYNC_SESSION_UPDATES`.
   - Pass 1: walk the SYNCHRONOUS entries in timeline order exactly as today (assigning `<IDn>`/`<SIDn>` on first
     sight); async entries are skipped, so the placeholder map never depends on where an async frame landed.
   - Pass 2: normalize each ASYNC entry (its `sessionId` resolves through the SAME `sid_ph`; a sid unseen in pass 1
     gets the next placeholder) and insert its record IMMEDIATELY AFTER the first synchronous record that is an
     `a2c` `resp` carrying the same `sessionId` placeholder (the session/new response that introduced the
     session); several async records for one session go in sorted order of their JSON line (stable); an async
     record whose sid no synchronous a2c resp carries goes after the LAST synchronous record (only a malformed
     capture can do that — say so in a comment).
   - Result: the SAME list of JSON lines for ANY position of an async notification in the raw timeline; the first
     line stays the c2a initialize request (C:1556) and the last line stays the end_turn terminal (C:1607-1608) —
     check both on the real run-1 after the change and paste them.
3. G regenerated from the real run-1 with the new normalizer, exactly the shape `test_golden_regen` (T:1954)
   expects: `"\n".join(normalize_timeline(_load_timeline_raw(golden/run-1, "run-1"))) + "\n"`. Then run-2's
   normalized lines MUST equal run-1's — paste `n1 == n2` and the two lines that differed at index 7 before.
4. P: `PINNED_GOLDEN_SHA256 = "<sha256 of the regenerated G>"` (paste `sha256sum G`) replacing `None` at P:130,
   with a comment naming this decision and date. Set ONCE, from the regenerated G.
5. Red-first tests in T (write each RED against the PIN's normalizer FIRST — paste the red line — then implement
   1-2 and paste the green):
   a. `test_golden_async_notification_is_order_free`: take the real run-1 entries (`_load_timeline_raw`, corpus
      or committed), locate the async `session_info_update` entry, and for EVERY index of the entry list (a loop)
      re-insert it there: `normalize_timeline` must return the identical list every time.
   b. `test_golden_async_placement_is_independent_of_the_session_new_response`: the async entry placed BEFORE the
      session/new response → the same output and the same `<SID1>` as after it (the pass-1/pass-2 property).
   c. CONTROL `test_golden_synchronous_frame_order_still_binds`: a SYNCHRONOUS a2c notification (an
      `agent_message_chunk`) moved one position → the output DIFFERS; a control that does not fail is a tautology —
      report it.
   d. CONTROL `test_golden_async_set_is_closed`: an a2c `session/update` whose `sessionUpdate` is NOT in
      `ASYNC_SESSION_UPDATES` (use `"tool_call"`) moved one position → the output DIFFERS.
6. T's now-dead artifice: delete `_ASYNC_UPDATES`, `_session_update_kind`, `_align_async_order` (T:114-145) and
   the `if leg == "run-2": a2c = _align_async_order(...)` at T:481-482 — the production normalizer now owns the
   order; if the synthetic bundle then fails, that is a FINDING (paste it; do not re-add the artifice). Flip the
   race pins: remove the `@pytest.mark.xfail` (T:567) from `test_real_bundle_cli` (its body already asserts the
   PASS line); replace `test_real_bundle_fails_only_at_the_golden_race` (T:579-590) by
   `test_real_bundle_passes_every_check` asserting rc 0 and the EXACT PASS line pasted from item 8.
   `test_cli_pass_path_fails_on_golden_pin` (T:598-604): the subprocess now sees a SET pin, so the synthetic
   bundle's golden fails with the sha-mismatch text (C:1545) — update the expected string to the exact text and
   the docstring to what it now proves (the pin binds the REAL golden; the synthetic golden is not it). Every
   other T test that goes red after 1-4 is either a premise-changed test (update it, the reason in its docstring)
   or a FINDING (paste it) — never a skip/xfail. The PC corpus `/home/rocco/s0-01-pinned/realleg/golden` is
   READ-ONLY and still carries the OLD golden.jsonl: a `test_real_leg_*` test that binds it to the new pin is
   expected RED here — paste it under DISCREPANCIES (the coordinator rebuilds the corpus at harvest).
7. S, ONLY IF item 8 is a PASS: `test_committed_bundle_runner_reports_leg_exit_mismatch_not_a_result`
   (S:107-130) flips to `test_committed_bundle_runner_mints_a_result` — the real runner on the unstripped copy →
   rc 0, `proofs/S0-01/result.json` present in the COPY, stdout/stderr pasted exact; keep
   `test_committed_negative_leg_cmd_reports_the_protocol_violation` (its behaviour is unchanged); rewrite the
   module docstring lines 9-17 (no more "neither mints nor defers"). De-vacuous the flipped test (one character
   of the expected string → red at its own assert → restore). If 8 is NOT a PASS, leave S untouched and say so.
8. The checker CLI on the real bundle from your tree root (`python C proofs/S0-01/evidence`, the §Gate env
   exported): paste the whole stdout + rc. Expected: rc 0, `PASS: S0-01 acp-conformance …`. A failure PAST the
   golden is a FINDING (a check that has never run on real evidence): paste the `failure_reason`, STOP that
   item and report — never fix a check outside this brief's design.
9. C6 (AF-AP-36, the pre-mint gate) on SCRATCH copies of the real bundle through the CLI: (i) run-2's first
   agent_message_chunk moved before the session/prompt request → the golden mismatch names its line; (ii) run-2's
   session_info_update `update` payload altered (one key changed, position kept) → mismatch; (iii) G with one byte
   changed → `golden.jsonl sha256 … != pinned …`; (iv) the pin set to the PIN's OLD G sha on a copy of P →
   mismatch; (v) control: the untouched copy → PASS. Paste each `failure_reason` line.

## Boundary (touch ONLY these five paths)
C (only `normalize_timeline` + the import line), P (the constant + the pin), G (regenerated bytes), T, S.
`proofs/S0-01/evidence/golden/**` other than G, `scripts/proof-runner`, `proofs/schemas/*`, every other file:
BYTE-IDENTICAL to the PIN (`git status --porcelain` lists exactly these five). Never edit a leg's timeline.

## Gate (paste every line verbatim; each call under Hermes's 420 s terminal cap)
- `export S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`;
  `/home/rocco/venv-agent-factory/bin` first on PATH; `mkdir -p ../scratch/bt`; an absolute SHORT `--basetemp`.
- T runs ~15 min SERIAL: the pytest gate is `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_01_check_acp_conformance.py
  tests/test_s0_01_spec_runner.py` then `wait <RUN_ID>` (xdist, ~3 min) — NEVER `lane_gate.sh -n`. Run it TWICE on
  the final bytes; paste both `pytest-summary:` lines and the `pytest-set:` line. Expected: `N passed`, ZERO
  failed/xfailed except the corpus-bound reds of item 6 (named).
- `python -m pyflakes` on C P T S (rc 0); `python3 scripts/ap_screen.py --s0-01 proofs/S0-01/check_acp_conformance.py`
  and `python3 scripts/ap_screen.py --tests tests/test_s0_01_check_acp_conformance.py tests/test_s0_01_spec_runner.py`
  (paste the last lines); `sha256sum` of the five paths = FILE IDENTITY.
- CODE INTEL FIRST: `graft skeleton` / `graft ask` before any whole-file read (T is 6187 lines — read by range);
  `bash scripts/ripwire_review.sh callers normalize_timeline` once. `report_lint` gates on a FLOOR (`--min-refs 12`);
  apply its `fix:` hints for at most THREE rounds, then paste and finish; paste its summary as PLAIN text (no
  backticks around the numbers — T2's self-referential-count lesson).
- Attack through SCRATCH COPIES only — never git-restore/stash/checkout the shared tree; never `git add/commit/push`.
  Other lanes may run on this host in their own trees — never touch their files, the model server, or any unit.

## Report shape (DATA, not prose)
FILE IDENTITY (five sha256) · the red-first lines for 5a-5d then green · the `n1 == n2` proof + the old index-7 pair ·
the CLI verdict on the real bundle (rc + whole stdout) · the C6 table (i-v) · the two pytest summary lines + the set
line · pyflakes/ap_screen lines · the S flip's de-vacuous lines · DISCREPANCIES · NOT-done · GATE RECOMMENDATION
(a proposal: the coordinator mints and the verify lane grades).
