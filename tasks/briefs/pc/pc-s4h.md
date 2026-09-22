# PC lane — S4H (issue #7, batch 2: the S0-04 compression checker's four un-killed guards get killing tests or a declared equivalence; a 2xx response-status assert; attested inputs → the mint re-proven)

PIN: d92bfcf

Role: code-implementer. Route: the LOCAL Qwen build route (`agentfactory-build-local`; the pc_lane.sh default — do NOT set
HERMES_MODEL). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Report: draft after EACH item at
`tasks/briefs/s0-04-support/S4H-report.md`, return it whole as your final message. THREE sibling lanes share this host
(A5q owns `tests/test_s0_01_check_acp_conformance.py`; B6 owns `tests/test_s0_02_buzz_authz.py`; K1-c owns
`scripts/vendored_manifest.py` + `tests/test_vendored_manifest.py` + `sandbox-kit/VENDORED-MANIFEST.md`) — never touch
their files or trees.

## Source (read WHOLE)
1. GitHub issue #7 (VERIFY-S004's seven follow-ups; this lane does BATCH 2 = F4 + F5 ONLY — F1/F3/F6 are EAT/document,
   F2/F7 need a PC re-capture and are NOT yours).
2. The checker `proofs/S0-04/check_compression.py` (C4) and its tests `tests/test_s0_04_compression.py` (T4, 69 tests at
   the PIN); the contract `proofs/S0-04/spec.json`, the seed's S0-04 block in `seeds/seed-stage0-v1.yaml`; the minted
   `proofs/S0-04/result.json` (env_fingerprint `sandbox:vm`) and `proofs/ledger.json`.
3. F4 — four defence-in-depth guards survive mutation with no killing test (line numbers at the PIN — re-read them):
   M4 the argv-presence guard C4:250-251 (`request-argv-absent`); M5 the sent-compression-header guard C4:253-255
   (`sent-compression-header-value` — reads `fixture["headers"]`, not `request["headers"]`, so it is redundant with
   request == fixture + the fixture carrying the header: an EQUIVALENT mutant candidate); M15 the config-header-duplicated
   guard C4:321-322; M17 the response-status isinstance guard C4:263-264 (`response-status-absent`).
4. F5 — the checker never asserts a 2xx response status: C4:263-264 only checks `status` is an int; a 5xx response still
   carrying `off; source=request-header` passes A2.

## Items (each: RED control first; paste every line)
1. PREMISE (paste): reproduce the four survivors on the PIN — on SCRATCH copies of C4 apply each mutation (M4: drop the
   argv guard; M5: drop the sent-header guard; M15: drop the duplicated-config-header guard; M17: drop the status
   isinstance guard) and run T4: each must be `69 passed` (a survivor). Then the F5 probe: a fixture leg whose
   response.json carries `"status": 503` and the compliant compression header — the current checker must PASS it (paste
   the exact PASS line). If any premise fails, stop and report.
2. F5: C4 requires `200 <= status < 300` at the A2 site, raising a NAMED `Failure(f"{leg}: response-status-not-2xx: {status}")`
   (keep `response-status-absent` for the non-int case). Test: the 503 leg → exactly that failure text; a 200 leg passes;
   de-vacuous (flip the bound → red at its own assert).
3. F4: for M4, M15 and M17 write killing tests (a bundle missing `argv` → `request-argv-absent`; a config with the
   compression header under two spellings → `config-header-duplicated: 2 keys`; a response whose `status` is the string
   `"200"` → `response-status-absent`), each red-first on the mutated scratch copy, green on the real C4. For M5: EITHER
   a killing test (a fixture whose `headers` carry a different compression value while request == fixture — if the
   checker's request==fixture check makes that unreachable, say so with the line) OR a declared EQUIVALENCE: a one-line
   comment at the guard naming it intentional defence-in-depth (AF-AP-36's "annotate as intentional hardening") plus a
   test that pins the guard's PRESENCE by behaviour where reachable. State which you did and why.
4. Mutation table: M4, M5, M15, M17 each re-applied on a scratch copy of the FINAL C4 → the named test red (or M5's
   declared equivalence); paste `1 failed` + the assertion line per row.
5. ATTESTED INPUTS (AF-AP-56): C4 is hashed by the mint. On YOUR tree prove the proof still mints: `python3
   scripts/proof-runner run --proof S0-04 --venue sandbox --root .` (rc 0; paste the summary and the classification),
   then `python3 scripts/validate-ledger integrity --root .` (S0-04 PRESENT — paste). Do NOT commit the regenerated
   `proofs/S0-04/result.json` or `proofs/ledger.json` as your deliverable: the coordinator regenerates them from the
   landing tree in the sandbox (the recorded env_fingerprint is `sandbox:vm`); list them under DISCREPANCIES if they
   changed on your tree and paste `git diff --stat -- proofs/S0-04/result.json proofs/ledger.json`.
6. Gates: `python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/<run> tests/test_s0_04_compression.py`
   TWICE on the final bytes (paste both; ZERO failed); `python -m pyflakes proofs/S0-04/check_compression.py
   tests/test_s0_04_compression.py` rc 0; `python3 scripts/ap_screen.py --tests tests/test_s0_04_compression.py` last
   line; `sha256sum` of the final C4 and T4 (FILE IDENTITY); `git status --porcelain` = C4, T4, your report (+ the two
   regenerated artifacts if the runner rewrote them — declared, not committed by you).

## Boundary
`proofs/S0-04/check_compression.py`, `tests/test_s0_04_compression.py`, your report. The evidence, fixtures, the capture
tools, `LIVE-CAPTURE-FINDINGS.md`, `spec.json` and every other proof: byte-identical to the PIN (F2/F7 are a later
re-capture; a needed change elsewhere is a FINDING). No live capture, no OmniRoute call, no git write, no outward action.

## Gate mechanics
`/home/rocco/venv-agent-factory/bin` first on PATH; `mkdir -p ../scratch/bt`; every call under Hermes's 420 s cap;
CODE INTEL FIRST (`graft skeleton` / `graft ask` before whole-file reads); `report_lint --min-refs 10`, at most THREE fix
rounds, then paste and finish.

## Report shape (DATA)
FILE IDENTITY · item 1's four survivor lines + the F5 PASS probe · per item the red-then-green lines · the mutation
table · the proof-runner + validate-ledger lines · the two pytest summaries · pyflakes/ap_screen · DISCREPANCIES ·
NOT-done (F1/F2/F3/F6/F7 by design) · GATE RECOMMENDATION (a proposal; the coordinator grades and a targeted verify
follows).
