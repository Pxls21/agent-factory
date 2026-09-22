# PC lane — B6 (issue #3: S0-02's F3 pre-network key refusal EXECUTED through the real CLI against an owned local listener)

PIN: 236bec7

Role: code-implementer. Route: the LOCAL Qwen build route (`agentfactory-build-local`; the pc_lane.sh default — do NOT set
HERMES_MODEL). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Report: draft after EACH item at
`tasks/briefs/s0-02-support/B6-report.md`, return it whole as your final message. THREE sibling lanes share this host
tonight (VERIFY-G2 and A5q own `tests/test_s0_01_check_acp_conformance.py`; K1-c owns `scripts/vendored_manifest.py` +
`tests/test_vendored_manifest.py` + `sandbox-kit/VENDORED-MANIFEST.md`) — never touch their files or trees. Owner
authorization: defensive test work on the owner's own repository; the listener you bind is yours, on 127.0.0.1 only.

## Source (read WHOLE)
1. GitHub issue #3 (reproduced here): VERIFY-B4 finding B4-05/F3 — the F3 test at `tests/test_s0_02_buzz_authz.py:1802`
   (`F3`: "whitespace-only and malformed-shape keys die in `_privkey`, BEFORE the …") asserts the CODE SHAPE of the refusal;
   a scratch shape-guard mutation survived it while the real downstream still refused. The BEHAVIOUR is correct: a
   malformed 64-char non-hex key reaches `nv.sign_event` (`proofs/S0-02/tools/pc/deliver_event.py:96` / `:194`) and raises
   BEFORE `_post` (`:106`, `urllib.request.urlopen` at `:112`) — no connection is attempted. The suggested fix: execute
   the actual CLI against an OWNED local listener or a deterministic post-sink and assert no connection is attempted.
2. `proofs/S0-02/tools/pc/deliver_event.py` (221 lines; READ-ONLY — production), its `main` (`:165`) argument surface and
   exit codes (read them from the source, never from memory), and the existing F3 test region T2:1790-1812.
3. The S0-02 contract: `proofs/S0-02/spec.json`, `seeds/seed-stage0-v1.yaml` (the S0-02 block).

## Items (RED control first for every new assertion; paste every line)
1. PREMISE: reproduce the finding on the PIN — apply VERIFY-B4's shape-guard mutation (or an equivalent: weaken the
   refusal's source shape while keeping the behaviour) on a SCRATCH copy of the production file and show the current F3
   test still passes (`1 passed`) — the test is source-shape-only. Paste. If it is already red, stop and report.
2. Build the BEHAVIOURAL test in `tests/test_s0_02_buzz_authz.py`: bind an owned listener on `127.0.0.1:0` (a thread
   accepting connections and counting them; answer a minimal HTTP response so a connecting client completes), run the REAL
   CLI (`sys.executable proofs/S0-02/tools/pc/deliver_event.py …`, a subprocess with a closed environment, relay URL =
   the listener) with a malformed 64-char NON-hex key: assert the exit code the source names for the refusal, the exact
   refusal text on stderr, and `connections == 0`.
3. The PAIRED POSITIVE CONTROL in the same test module: the same CLI with a WELL-FORMED key (a throwaway secp256k1 key
   generated in-test, never a real one) against the same listener: `connections == 1` and the request reaches the
   listener — proving the listener WOULD observe a connection (a zero that cannot become a one is a tautology).
4. Kill the mutant of item 1 with the new test (paste `1 failed` + the assertion); the old shape assertions stay as they
   are (drop nothing, rewrite nothing).
5. De-vacuous each new assertion (flip the expected count / exit code / text by one → red at its own assert; restore).
6. Boundary check: `git status --porcelain` lists exactly `tests/test_s0_02_buzz_authz.py` and your report;
   `git diff --quiet 236bec7 -- proofs/` rc 0.

## Boundary
`tests/test_s0_02_buzz_authz.py` + your report ONLY. `proofs/S0-02/**` is READ-ONLY production (a defect there is a
FINDING). No relay delivery, no network beyond 127.0.0.1, no git write, no outward action.

## Gate (every call under Hermes's 420 s terminal cap; paste verbatim)
- `export S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`;
  `/home/rocco/venv-agent-factory/bin` first on PATH; `mkdir -p ../scratch/bt`; an absolute SHORT `--basetemp`.
- `python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/<run> tests/test_s0_02_buzz_authz.py` TWICE on
  the final bytes (paste both summaries; ZERO failed); `python -m pyflakes tests/test_s0_02_buzz_authz.py` rc 0;
  `python3 scripts/ap_screen.py --tests tests/test_s0_02_buzz_authz.py` last line; `sha256sum` of the final file.
- CODE INTEL FIRST: `graft skeleton` / `graft ask` before any whole-file read. `report_lint --min-refs 10`, at most THREE
  fix rounds, then paste and finish.

## Report shape (DATA)
FILE IDENTITY · item 1's surviving-mutant line · the behavioural test's red-then-green lines · the positive control ·
the mutant kill · the de-vacuous lines · the two pytest summaries · pyflakes/ap_screen · DISCREPANCIES · NOT-done ·
GATE RECOMMENDATION (a proposal; the coordinator grades).
