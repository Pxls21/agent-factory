# PC lane — VERIFY-VB-F12 (adversarial verification of the S0-01 mint: the v2.4 capture + the order-free golden, owner decision (a))

PIN: 955ab74

Role: adversarial-verifier. Route: the LOCAL Qwen verify route (`agentfactory-verify-local`, xhigh — the pc_lane.sh
default for adversarial-verifier; do NOT set HERMES_MODEL). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first.
Report: draft after EACH item at `tasks/briefs/s0-01-vb-f12-support/VERIFY-VB-F12-report.md`, return it whole as your
final message. You VERIFY; you never fix. A finding is file:line-bounded, reproduced through the real path, and graded
by the blocking predicate (contract-mapped · reproduced canonically · materially effective · a concrete discriminator ·
in-boundary). Emit a GATE RECOMMENDATION (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID),
never a verdict — the coordinator decides; under D-034 a non-blocking finding becomes a `verify-followup` issue.

## What is under verification (read WHOLE, in this order)
1. `tasks/briefs/s0-01-vb-f12-support/G1-report.md` (the build lane's proposal) and its brief
   `tasks/briefs/pc/pc-vb-f12-g1.md`; `tasks/briefs/s0-01-vb-f12-support/T2-report.md`; the capture run plan + log
   `tasks/briefs/s0-01-vb-f12-recapture-v24.md`.
2. The FROZEN CONTRACT: `seeds/seed-stage0-v1.yaml` (the S0-01 block), `proofs/S0-01/spec.json`,
   `proofs/S0-01/check_acp_conformance.py` (C; `EXPECTED_CHECK_SEQUENCE`, `check_golden` C:1533-1660,
   `normalize_timeline` C:795-887), `proofs/S0-01/pins.py` (P; `ASYNC_SESSION_UPDATES`, `PINNED_GOLDEN_SHA256`,
   `PINNED_BASELINE_*`), `proofs/S0-01/negative_contract.py`, `docs/INCIDENT-LOG.md` (the 2026-09-21 entry, AF-AP-107/108).
3. The MINTED artifact `proofs/S0-01/result.json` + `proofs/ledger.json` (S0-01 PRESENT) and the evidence bundle
   `proofs/S0-01/evidence/golden/` (run-1, run-2, cancel, shutdown, two-users, negative; `golden.jsonl`; manifests).

## Attack list (each item: what you did, the exact command, the exact output, SOLID/UNSURE)
V1 The golden decision's REACH. `normalize_timeline` makes exactly `ASYNC_SESSION_UPDATES` order-free. Attack it: (a) can a
   DIFFERENT payload of `session_info_update` in run-2 pass? (the sorted-JSON-line multiset must catch it — reproduce
   the lane's C6(ii) yourself); (b) can a SECOND async notification (duplicate) in run-2 pass? (count must bind); (c)
   can an async notification carrying ANOTHER session's id be re-homed silently? (d) an async frame BEFORE the
   initialize request or AFTER the end_turn terminal — does the first/last-line rule (C:1556, C:1607-1608) still hold
   and does the golden still bind? (e) does any OTHER check in EXPECTED_CHECK_SEQUENCE consume raw order for the async
   frame (route windows, seq, tee splits) — i.e. is the raw timeline still bound elsewhere, so nothing is lost?
V2 The seed's intent. The seed says "golden ×2 identical". State whether decision (a) satisfies the seed's WORDS or
   REQUIRES an amendment note in `tasks/stage0-breakdown.md`/the decision log — cite the seed lines. Not a blocker
   either way; a precise finding.
V3 The evidence bundle's integrity, independently: manifests pre == post == `PINNED_BASELINE_*` (recompute the digests
   from the committed manifest bytes; reproduce one leg's `build_capture_record.py --check`); the mention receipts
   bound to the relay; the negative leg's probe sha/interpreter/observed error; the leak guard; `tee-status.json`;
   `buzz-acp.pid` present in every positive leg (AF-AP-62 sibling, fixed in .gitignore — prove the committed tree
   carries them: `git ls-files proofs/S0-01/evidence/golden | grep buzz-acp.pid`).
V4 The mint's attested inputs (AF-AP-56): `python3 scripts/validate-ledger integrity --root .` = PRESENT; re-run
   `python3 scripts/proof-runner run --proof S0-01 --venue pc-bridge --root <scratch copy>` and diff the result
   against the committed result.json (name every differing key and why); `python3 scripts/ledger-gen --root <copy>`
   reproduces `proofs/ledger.json`.
V5 The meta-tests as gates, not mirrors: pick FIVE of the golden/async tests (T:1913-2060, the flipped race pins
   T:523-580, `test_golden_regen` T:2074) and MUTATE the production code on a SCRATCH COPY (e.g. widen
   `ASYNC_SESSION_UPDATES` to every kind; drop the sort; slot async records at the END; skip pass-1/pass-2 separation)
   — each mutant must be killed by a NAMED test; a survivor is a finding. Note that `test_golden_regen`'s assertion
   changed from a regen-path check to a sha-mismatch check — decide whether the C:1578 branch keeps an independent
   test (`test_golden_frozen_lines` T:1872) and whether the regen path lost coverage.
V6 The T2/G1 runner pins (`tests/test_s0_01_spec_runner.py:102-139`): are they gates (would a broken checker or a
   deleted leg make them red?) — mutate on a copy.
V7 The PASS line carries `negative: observed: observed: …` (a doubled prefix) — locate the producer in C, state whether
   any consumer (spec.json failure_reason matching, the runner, the ledger) depends on the exact text, and grade it.
V8 The lane process claims: reproduce the G1 report's `n1 == n2` proof, its 5a red line against the PIN's OLD
   normalizer (`git show 772ce3b:proofs/S0-01/check_acp_conformance.py` on a scratch copy) and its C6 (i)-(v) table.
V9 Anything else you find. Exhaustive discovery; disciplined disposition.

## Boundary
READ-ONLY on the tree: attack through SCRATCH COPIES only (`../scratch`); never git-restore/stash/checkout the shared
tree; never `git add/commit/push`; never touch the corpus `/home/rocco/s0-01-pinned/realleg/golden`, the model server,
any unit, or another lane's tree. No live captures, no relay deliveries.

## Gate mechanics (each call under Hermes's 420 s terminal cap)
- `export S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`;
  `/home/rocco/venv-agent-factory/bin` first on PATH; `mkdir -p ../scratch/bt`; an absolute SHORT `--basetemp`.
- pytest on this host: `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/bt <files>` DIRECTLY
  (pytest-xdist is installed here; `scripts/pc_suite.sh` is the SANDBOX's launcher and cannot run on the PC). T alone
  is ~15 min serial — always `-n 8`.
- CODE INTEL FIRST: `graft skeleton` / `graft ask` before any whole-file read (T is >6,000 lines — read by range);
  `bash scripts/ripwire_review.sh callers normalize_timeline` once. `report_lint` gates on a FLOOR (`--min-refs 15`);
  apply its `fix:` hints for at most THREE rounds, then paste and finish; paste its summary as PLAIN text.

## Report shape (DATA)
Per item: command · exact output · SOLID/UNSURE · blocking? (the predicate, each clause answered) · the file:line.
Then: the mutant table (V5/V6), DISCREPANCIES, NOT-done, GATE RECOMMENDATION. Never a fix, never a verdict.
