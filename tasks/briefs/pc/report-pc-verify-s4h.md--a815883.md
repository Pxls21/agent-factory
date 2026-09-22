# VERIFY-S4H report — adversarial verification of S4H (issue #7 batch 2, F4 + F5)

Lane: adversarial-verifier · PIN a815883 · tree /home/rocco/agent-factory/.lanes/pc-verify-s4h.md--a815883/tree (detached HEAD, clean at launch)

Role text + brief: tasks/briefs/pc/pc-verify-s4h.md · VENUE-MAP read at launch (pc: podman 5.7, 12 cores, local vLLM verify route; this lane runs the PC-side deterministic suites only — no proof-runner into the shared tree).

## ITEM 1 — PREMISE

Command (lane tree):

  git diff --stat d92bfcf a815883 -- proofs/ tests/

Exact output:

  proofs/S0-04/check_compression.py         |   7 +-
  proofs/S0-04/result.json                  |  14 +-
  proofs/ledger.json                        |   2 +-
  tests/test_s0_01_check_acp_conformance.py | 261 ++++++++++++++++++++++++++++--
  tests/test_s0_02_buzz_authz.py            | 171 ++++++++++++++++++++
  tests/test_s0_04_compression.py           |  79 +++++++++
  6 files changed, 510 insertions(+), 24 deletions(-)

DISCREPANCY (item 1 as worded): the range d92bfcf..a815883 names SIX files under proofs/ + tests/, not four.

The two extras are tests/test_s0_01_check_acp_conformance.py (+261/-...) and tests/test_s0_02_buzz_authz.py (+171), and they do NOT come from S4H: the landing commit a815883 has parent 7a6a75a, and `git diff --stat 7a6a75a a815883` names exactly the four S4H code/attested files (C4, T4, result.json, ledger.json) plus S4H's own brief/report/transcript artifacts. The scoped `git diff --stat 7a6a75a a815883 -- proofs/ tests/` output is exactly:

  proofs/S0-04/check_compression.py |  7 +++-
  proofs/S0-04/result.json          | 14 +++----
  proofs/ledger.json                |  2 +-
  tests/test_s0_04_compression.py   | 79 +++++++++++++++++++++++++++++++++++++++
  4 files changed, 93 insertions(+), 9 deletions(-)

The full true-parent commit range also contains only S4H's own brief/report/transcript artifacts outside `proofs/ tests/`.

d92bfcf is an ANCESTOR (git merge-base --is-ancestor: yes) of a815883 but not its parent; the intermediate commits are the sibling A5q landing (2e02afd, which touched the two S0-01/S0-02 test files) and transcript/ledger bookkeeping. The C4/T4 diff is BYTE-IDENTICAL between the two ranges (cmp of the two `git diff` outputs: IDENTICAL), so the brief's `d92bfcf` base was a stale label for "S4H's parent". Assessed against the TRUE parent: the S4H landing changes exactly C4 + T4 + the two attested artifacts.

Command: git diff d92bfcf a815883 -- proofs/S0-04/check_compression.py (identical to the 7a6a75a version; pasted whole, 7 +/- lines):

  diff --git a/proofs/S0-04/check_compression.py b/proofs/S0-04/check_compression.py
  index 0328c41..5e78c23 100644
  --- a/proofs/S0-04/check_compression.py
  +++ b/proofs/S0-04/check_compression.py
  @@ -249,6 +249,8 @@ def check_request_leg(leg: str, leg_dir: Path, fixtures_dir: Path, observations:
       raise Failure(f"{leg}: request-url-unexpected: {_short(url)}")
   if not isinstance(request.get("argv"), list) or not request["argv"]:
       raise Failure(f"{leg}: request-argv-absent")
  +    # A1 compares request and fixture, but `--fixtures-dir` can supply a self-consistent alternate
  +    # pair; pin the fixture directive here so it cannot change from compression-off.
   sent = {k.lower(): v for k, v in fixture["headers"].items()}
   if sent.get(COMPRESSION_HEADER) != COMPRESSION_VALUE:
       raise Failure(f"{leg}: sent-compression-header-value: "
  @@ -260,8 +262,11 @@ def check_request_leg(leg: str, leg_dir: Path, fixtures_dir: Path, observations:
   # structural signature that the OFF came from our directive, not an OmniRoute default —
   # anti-hollow-green #7). Parameters are `;`-separated and stripped; the state is the first.
   response = _read_json(leg_dir / "response.json", leg, "response.json")
  -    if not isinstance(response.get("status"), int):
  +    status = response.get("status")
  +    if type(status) is not int:
       raise Failure(f"{leg}: response-status-absent")
  +    if not 200 <= status < 300:
  +        raise Failure(f"{leg}: response-status-not-2xx: {status}")
   values = [v for name, v in _header_values(response.get("headers"), leg, "response.json")
             if name.lower() == COMPRESSION_HEADER]
   if not values:

sha256sum (measured, both match the brief):

  fa39bb78c7d589cc678af163075393244ec5ab7894e8a9917ac4af5363610981  proofs/S0-04/check_compression.py
  2085b90bdde03c1b605a8e3d61a06f178e122327e9001d04ecd9a7342b7a5404  tests/test_s0_04_compression.py

C4 = 408 lines (403 at the parent, +5 net), T4 = 1026 lines (947, +79). Both match S4H-report's FILE IDENTITY.

result.json diff — verified: every `-`/`+` line (3 hunk headers + 14 lines) is one of: recorded_at, started_at/finished_at × 4 legs, the C4 attested hash (2a380c93... -> fa39bb78..., which equals my measured sha256 of the PIN's C4), or the digest (f125a45e... -> abc00645...). `env_fingerprint: "sandbox:vm"` UNCHANGED (present in both sides of every context; grep for non-pasted `-`/`+` lines returned nothing). No other field touched.

ledger.json diff: exactly one changed line — the S0-04 row's normalized_digest ca6c4660... -> 74fd294a..., state stays "PRESENT".

SOLID: the literal frozen premise FAILED. Item 1 says that any output other than exactly C4 + T4 + result.json + ledger.json for the command `git diff --stat d92bfcf a815883 -- proofs/ tests/` requires `CONTRACT-INVALID and stop`. The command names six files. The true-parent comparison explains the stale base and shows that S4H itself changed only the intended four files, but it cannot satisfy or amend the frozen command retroactively. Under the brief's explicit exception, this defeats the contract rather than proving a production-code blocker.

Contract-invalid mapping: criterion = item 1's exact diff boundary; canonical reproduction = git on the current PIN; material effect = the mandatory premise evidence is false and its scope cannot be interpreted literally; discriminator = the six-file output versus the required four-file output; task ownership = coordinator/brief amendment, not C4/T4 repair.

I incorrectly continued after this stop condition while applying the general "build on measured truth" premise-conflict rule. Items 2-8 below are therefore ANCILLARY evidence only. They do not cure item 1 or change the required recommendation.

## ITEM 2 — survivors at the parent + killers at the PIN

Parent scratch = `git archive d92bfcf` → `scratch/parent`; the suite there collects 74 tests (69 per the brief is STALE; measured 74). Each of the four guards deleted one at a time on the PARENT C4 (mutant compiles + collects, AF-AP-78), suite run:

  `python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/… tests/test_s0_04_compression.py`

  PARENT M4 (delete `if not isinstance(request.get("argv"),…)`): `74 passed in 1.77s`
  PARENT M5 (delete the `sent`/sent-compression-header-value block): `74 passed in 1.63s`
  PARENT M15 (delete `if len(hits) > 1: … config-header-duplicated`): `74 passed in 1.54s`
  PARENT M17 (delete `if not isinstance(response.get("status"), int): … response-status-absent`): `74 passed in 1.66s`

All four SURVIVE the parent suite exactly as the brief/lane claimed (74 passed each). Confirmed: the parent had no killing tests.

PIN scratch = `git archive a815883` → `scratch/pin`; same four deletions applied to the PIN's C4, run against the PIN's T4 (79 tests). Each DIES at its NAMED killer:

  PIN M4 → `1 failed, 78 passed` — FAILED tests/test_s0_04_compression.py:531 `assert code == 1, out` in `test_request_argv_is_required`; the runtime assertion reads `assert 0 == 1` (mutant prints the PASS line, i.e. it ACCEPTED a bundle with no argv).

  PIN M5 → `1 failed, 78 passed` — FAILED tests/test_s0_04_compression.py:550 `assert code == 1, out` in `test_fixture_compression_header_is_pinned_after_request_equivalence`; the runtime assertion reads `assert 0 == 1` (mutant accepts the self-consistent `on` fixture).

  PIN M15 → `1 failed, 78 passed` — FAILED tests/test_s0_04_compression.py:436 `assert code == 1, out` in `test_duplicated_config_header_is_refused`; the runtime assertion reads `assert 0 == 1` (mutant accepts the two-spelling config).

  PIN M17 → `1 failed, 78 passed` — FAILED tests/test_s0_04_compression.py:331 `assert "failure_reason: off: response-status-absent" in out, out` in `test_response_status_requires_an_integer`; the mutant instead reports TypeError.

M17-on-PIN kill CLASSIFICATION (the brief's question): the killer reds at the NAMED assertion (T4:331 `assert "failure_reason: off: response-status-absent" in out, out`), but the red is an INCIDENTAL TypeError, not the guard's own Failure. Mechanism: the mutant deletes only the `type(status) is not int` guard and keeps the bound; for `status="200"` the string now reaches the bound `200 <= status` at C4:268 and raises `TypeError: '<=' not supported between instances of 'int' and 'str'` (int-constant vs str operand), which the catch-all `except Exception` in main() (C4:401-403) re-emits as `failure_reason: malformed evidence: TypeError: …`. The test still fails because the expected `response-status-absent` is ABSENT from that output. So: it IS a real red-green discriminator (red in the mutant build, green in the real build — not a tautology; the green build positively emits `response-status-absent` for "200"/True, re-confirmed in item 3), but the red is kill-by-named-reason-ABSENCE mediated by an incidental TypeError at C4:268 `if not 200 <= status < 300:`, not kill-by-the-guard-firing at C4:266-267 `if type(status) is not int:` / `raise Failure(f"{leg}: response-status-absent")`; the guard itself is exercised on green.

The guard's own line is C4:266-267; the bound's line is C4:268. Not a blocker either way; the positive emission is independently verified green.

## ITEM 3 — new hostile shapes (F5 bound + M17 type guard)

Run method for each: a scratch copy of the committed PASS bundle (`proofs/S0-04/evidence`) with `off/response.json` mutated (one field changed, rest byte-identical), then the real CLI `python3 proofs/S0-04/check_compression.py <bundle>` from the PIN tree (cwd = PIN). Expected reason stated BEFORE the run; observed from stdout.

shape · expected (stated first) · observed · grade

  status=200.0 (float) · expect response-status-absent · `failure_reason: off: response-status-absent` (rc 1) · SOLID — `type(200.0) is int` is False

  status=False · expect response-status-absent · `failure_reason: off: response-status-absent` (rc 1) · SOLID — `type(False) is int` is False (bool excluded, the whole M17 point)

  status=None · expect response-status-absent · `failure_reason: off: response-status-absent` (rc 1) · SOLID

  status key ABSENT · expect response-status-absent · `failure_reason: off: response-status-absent` (rc 1) · SOLID — `.get()`→None→type not int

  status=-200 · expect response-status-not-2xx: -200 · `failure_reason: off: response-status-not-2xx: -200` (rc 1) · SOLID — below the lower bound

  status=2000 · expect response-status-not-2xx: 2000 · `failure_reason: off: response-status-not-2xx: 2000` (rc 1) · SOLID — above the upper bound (no 2xx/3xx/4xx/5xx classing needed; the bound is a hard 200-299 window)

  status=204 · expect PASS (2xx) · rc 0, PASS line · SOLID — 204 is in-window, a legitimate pass (see below)

  status=206 · expect PASS (2xx) · rc 0, PASS line · SOLID — 206 is in-window

  status=201 · expect PASS (2xx) · rc 0, PASS line · SOLID

  status=10**30 (huge int) · expect response-status-not-2xx: … · `failure_reason: off: response-status-not-2xx: 1000000000000000000000000000000` (rc 1) · SOLID — big int is a real int, out of window, no overflow (Python int is unbounded, so 200<=10**30<300 is a clean False; no NaN/inf wormhole in the int domain)

  status nested under headers · expect response-status-absent · `failure_reason: off: response-status-absent` (rc 1) · SOLID — the top-level key is gone, so `.get("status")`→None

  NaN literal in file · expect malformed-evidence (NaN) · `failure_reason: off: malformed-evidence: NaN or Infinity in response.json` (rc 1) · SOLID — the `_loads` parse_constant=_reject (C4:121-126) fires BEFORE the type/bound check; NaN never reaches the bound

  DUPLICATED top-level status (503 then 200, JSON last-wins) · see below · rc 0, PASS line · SEE GRADING BELOW

Is a 204/206 with a compliant compression header a hollow green for A2/A3, or a legitimate pass? LEGITIMATE PASS.

A2 (C4:262-282) grades the RESPONSE header (`x-omniroute-compression: off; source=request-header`) — it does NOT read the response body or status. A3 (C4:285-311) byte-compares the UPSTREAM-RECORD request body (`_canon(record["body"])` vs the fixture body, C4:298-302) and the content-length; it never touches response.status. The F5 2xx bound (C4:268-269) is an INDEPENDENT third check on the status scalar. So a 204/206 that also carries the compliant off-header and a byte-matched upstream record is exactly the "successful chat-completion that honoured the off directive" the proof is meant to certify — not a hollow green. The bound's job is only to reject a 5xx/3xx that STILL echoes the off header (the F5 premise); 204/206 are in-window successes. SOLID.

Grading the DUPLICATED `status` (503 then 200) by the blocking predicate, AF-AP-41 in view:

  The raw JSON `{"…","status": 503, "status": 200}` is parsed by default `json.loads` (C4:126, `_loads`) to a single `{"status": 200}` (last-wins); the checker then sees 200 and PASSES (rc 0, observed). This is a real observation. But:

  (1) CONTRACT MAPPING — the frozen S4H contract (brief pc-s4h.md item 3) requires only "200<=status<300 … 503 → that failure; 200 → passes". It does NOT require a duplicate-KEY refusal for the scalar `status`. AF-AP-41's stated scope is "last-wins parse of a CONFIG ECHO / two terminal responses for one request id collapsing to the last" — i.e. multi-occurrence tokens in an echo line or a per-request-id sequence, which the S0-04 checker DID guard where it applies (the compression HEADER, both legs: `compression-header-duplicated` in the response leg, `config-header-duplicated` in the config leg — the case-different multi-key shape that survives JSON). A scalar JSON value's duplicate is collapsed by `json.loads` itself and is unrecoverable post-parse; it is a different mechanism than the AF-AP-41 echo/response-id collapse, so mapping AF-AP-41 to the scalar status is a stretch.

  (2) CANONICAL REPRODUCTION — the live consumer is `proof-runner` executing `spec.json`'s argv `python3 proofs/S0-04/check_compression.py proofs/S0-04/evidence` (NO `--fixtures-dir`, and it reads the COMMITTED bundle). The committed `evidence/off/response.json` has exactly ONE status key, and the producer `capture_leg.py` writes it as a dict entry `"status": status` (C-capture L219, json.dumps of a dict) — it structurally CANNOT emit a duplicate status key. So the dup-key shape is reachable only by manually FORGING the evidence file, i.e. a surrogate, not the production path at the PIN.

  (3) MATERIAL EFFECT — it does not change the stated F5 protection: a REAL 5xx is a single-key `{"status": 503}` and is correctly refused; a forger who can rewrite response.json already has the strictly-simpler single-key `{"status": 200}` pass, so the dup-key adds no new attack the 2xx bound (or the hash-pinned attestation) doesn't already cover.

  Verdict: all three of clauses 1-3 of the predicate FAIL (contract not mapped, not a canonical production-path repro, not a material change to the stated protection). → FOLLOW-UP (a "require the status key exactly once by raw-byte scan" hardening in the AF-AP-41 class), NOT a blocker. I did not fix it (role = verify only).

## ITEM 4 — M5 reachability (is `--fixtures-dir` on the production path?)

Through the REAL CLI, on a scratch copy:

  M5 guard DELETED (C4 sent-header block removed), a request+fixture pair where BOTH carry `x-omniroute-compression: on` under `--fixtures-dir <alt>`, run:

    `python3 check_compression.py --fixtures-dir <alt-fixtures> <bundle>`

    → rc 0, `PASS: S0-04 compression-contract - 3 assertions over 3 legs`

    This is the HOLLOW GREEN the guard prevents: the self-consistent alternate fixture + matching request pass A1 (request==fixture) AND the sent-header check is gone, so `on` slips through.

  M5 guard PRESENT (the real PIN C4), same alt-fixture bundle:

    → rc 1, `failure_reason: off: sent-compression-header-value: on`

    The guard catches it.

Both pasted. So the guard is REACHABLE and NON-REDUNDANT via `--fixtures-dir`: with a self-consistent alternate fixture, the request==fixture equality (A1, C4:239-241) is satisfied by the alternate, and only the M5 pin of the fixture directive stops `on` from passing. This CONFIRMS the lane's correction of issue #7 (which had called M5 an equivalent mutant) — it is NOT equivalent; it is reachable and load-bearing for the `--fixtures-dir` path.

Is `--fixtures-dir` on the PRODUCTION (mint) path? NO.

  `proofs/S0-04/spec.json` positive leg: `cmd: ["python3","proofs/S0-04/check_compression.py","proofs/S0-04/evidence"]` — no `--fixtures-dir`. Negative leg: `… fixtures/evidence-header-missing` — no `--fixtures-dir`. `scripts/proof-runner` (grep for "fixtures": zero hits) executes exactly the spec's argv and never injects `--fixtures-dir`. So on the mint the checker uses its default `fixtures_dir = Path(__file__).parent/"fixtures"` (C4:391-392), i.e. the COMMITTED `proofs/S0-04/fixtures/`, and the M5 guard's only live discriminator is the committed fixture (which carries `off`, so the guard is a no-op there — it only fires if the fixture's compression directive ever changed to non-`off`).

  Honest grade of "materially effective": on the MINT path the M5 guard is HARDENING (defence-in-depth against a future committed fixture being edited to a non-`off` directive), NOT a contract gate the mint exercises. Its real teeth are on the `--fixtures-dir` CLI path, which the tests use (T4:535-551 `def test_fixture_compression_header_is_pinned_after_request_equivalence(tmp_path):`) but the mint never uses. This matches the S4H report's own framing (C4:252-253 comment: "`--fixtures-dir` can supply a self-consistent alternate pair; pin the fixture directive").

  The guard is a legitimate, correctly-killed hardening; it is not load-bearing for the mint's actual pass. No defect.

## ITEM 5 — the regenerated mint (READ-ONLY, scratch copies only)

On `git archive a815883` → `scratch/pin` (never run proof-runner into the shared tree):

  `python3 scripts/validate-ledger integrity --root .` → rc 0; output includes `S0-04 PRESENT` (full line set: S0-01 PRESENT, S0-02 ABSENT, S0-03 PRESENT, S0-04 PRESENT, S0-05 ABSENT, S0-06..S0-12 PRESENT; execution_proof numerator=7 denominator=9; conformance_checked_decision numerator=3 denominator=3).

  `python3 scripts/ledger-gen --root .` → `ledger-gen: wrote …/scratch/pin/proofs/ledger.json (12 proofs)`, rc 0.

  sha256 of `proofs/ledger.json` BEFORE = `58f39e2ab4e28ffad05675b253797e5925216d55d7f1cda16db4176c83d65984`

  sha256 AFTER regen = `58f39e2ab4e28ffad05675b253797e5925216d55d7f1cda16db4176c83d65984` (IDENTICAL).

  → the committed ledger.json is a NO-OP regeneration: it exactly matches what `ledger-gen` derives from the pinned result.json, i.e. the committed ledger is consistent with its inputs (the `normalized_digest` 74fd294a… is reproducible). SOLID.

  `env_fingerprint` in the PIN's `result.json` (line 5): `"sandbox:vm"` — names the SANDBOX venue, never this host (`pc:…`). The S4H lane's own PC proof-runner run had produced `sandbox:fedora` and was correctly NOT landed; the landed/regenerated mint at the PIN is the sandbox one. SOLID — the attested artifact is sandbox-provenance as required.

  `scripts/ledger-gen` `_normalized_digest` (L51-57) = sha256 of the result with `volatile_paths` (the timestamps) stripped; so the digest changes only when a non-timestamp field (the C4 attested hash) changes — consistent with item 1's finding that the result.json diff was only timestamps + the C4 hash + the digest.

## ITEM 6 — de-vacuous pass on the five new tests + the bound's two edges independently

De-vacuous (flip each expected outcome in a fresh `git archive a815883` scratch copy of T4; the real C4 is unchanged; the flipped test must red at its OWN assert). Each produced rc 1 (red) on its own test:

  test_response_status_must_be_2xx — flipped the 503 tuple from expected `(1, not-2xx)` to `(0, PASS)`: RED at `assert code == expected_code`, `AssertionError: (503, 'failure_reason: off: response-status-not-2xx: 503')`, `assert 1 == 0`, `1 failed in 0.38s`. SOLID.

  test_response_status_requires_an_integer — flipped its expected code from 1 to 0: RED at `assert code == 0, out`, `AssertionError: failure_reason: off: response-status-absent`, `assert 1 == 0`, `1 failed in 0.25s`. SOLID.

  test_duplicated_config_header_is_refused — flipped `assert code == 1` to `assert code == 0`: RED at that own assert, `AssertionError: failure_reason: config: config-header-duplicated: 2 keys`, `assert 1 == 0`, `1 failed in 0.25s`. SOLID.

  test_request_argv_is_required — flipped `assert code == 1` to `assert code == 0`: RED at that own assert, `AssertionError: failure_reason: off: request-argv-absent`, `assert 1 == 0`, `1 failed in 0.27s`. SOLID.

  test_fixture_compression_header_is_pinned_after_request_equivalence — flipped `assert code == 1` to `assert code == 0`: RED at that own assert, `AssertionError: failure_reason: off: sent-compression-header-value: on`, `assert 1 == 0`, `1 failed in 0.26s`. SOLID.

These are outcome-flips; the brief's stronger ask is the bound-edge mutants below, which I also ran.

The bound's two edges INDEPENDENTLY (C4 bound mutated on a fresh `git archive a815883` tree, run through the real T4 test `test_response_status_must_be_2xx`, which exercises 200/299/503/199/300):

  MUTANT `200 <= status < 301` (admits 300): the test REDS on the 300 case — `AssertionError: (300, '…PASS: S0-04…')`, `assert 0 == 1` (the checker now returns 0/PASS for 300, the test expected 1/not-2xx). `1 failed in 0.49s`. SOLID — the upper edge is independently pinned (the lane's own `< 5000` mutant covered only the far-upper region, not the 300 boundary).

  MUTANT `199 <= status < 300` (admits 199): the test REDS on the 199 case — `AssertionError: (199, '…PASS: S0-04…')`, `assert 0 == 1`. `1 failed in 0.40s`. SOLID — the lower edge is independently pinned.

Both edges red on their OWN case, confirming the `200 <= status < 300` window is not a single-sided tautology.

## ITEM 7 — gates on the PIN's bytes + INFO sweep

On the shared PIN tree (four lanes share the 12 cores; `-n 4`, short absolute `--basetemp`, `--basetemp` parent pre-mkdir'd):

  `python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/v1 tests/test_s0_04_compression.py`
  → `79 passed in 1.17s`

  `python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/v2 tests/test_s0_04_compression.py`
  → `79 passed in 1.21s`

  Both `79 passed`; the suite is deterministic — matches the lane's pasted 79×2. SOLID.

  `python -m pyflakes proofs/S0-04/check_compression.py tests/test_s0_04_compression.py`
  → rc 0 (clean). SOLID.

  `python3 scripts/ap_screen.py proofs/S0-04/check_compression.py`
  → `AP_SCREEN over 1 path(s): 0 hits over 1 files`. SOLID (0 at the PIN, as the brief expected).

  `python3 scripts/ap_screen.py --tests tests/test_s0_04_compression.py`
  → `TEST_SCREEN over 1 path(s): 3 hits over 1 files`:

    AF-AP-34 ×2 and AF-AP-59 ×1, ALL at tests/test_s0_04_compression.py:905 (`for banned in ("pkill","killall","pgrep -f"):` in `test_runner_never_kills_by_name`). These are the three pre-existing source-string hits the brief named; none are in the S4H hunks (301-331/425-437/523-551). SOLID — nothing new.

INFO sweep (report, never fix) — `grep -n "isinstance(.*, *int)" proofs/*/check_*.py proofs/*/tools/*.py`:

Every sibling status/count guard ALREADY excludes bool the way M17 now does. There is NO sibling that admits bool the way the OLD M17 (`isinstance(x, int)`) did:

  proofs/S0-01/check_acp_conformance.py:216
  `return isinstance(v, int) and not isinstance(v, bool)`

  proofs/S0-03/check_omniroute_roundtrip.py:488
  `isinstance(value, bool) or not isinstance(value, int) or value != expected`

  proofs/S0-03/check_omniroute_roundtrip.py:845
  `isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0`

  proofs/S0-03/check_omniroute_roundtrip.py:849
  `if (isinstance(agent_child_pid, bool) or not isinstance(agent_child_pid, int)`

  proofs/S0-05/check_egress.py:97-98
  `isinstance(value, int) and not isinstance(value, bool)` (docstring cites AF-AP-26)

  proofs/S0-08/check_containment.py:156
  `not isinstance(rc, int) or isinstance(rc, bool)`

  proofs/S0-11/check_eval_hardening.py:410
  `isinstance(node.value, int) and not isinstance(node.value, bool)`

→ FOLLOW-UP candidate list is EMPTY: the AF-AP-26 (isinstance(True,int) is True) class was already closed in every sibling checker; S0-04's M17 was the LAST one still using bare `isinstance(x,int)`, and S4H closed it. The INFO sweep confirms the fix brought S0-04 in line with the established repo convention (AF-AP-26). No follow-up needed.

NOTE: S0-04's own new idiom `type(status) is not int` (C4:266) is a fourth spelling of the same check (distinct from the siblings' `isinstance(x,int) and not isinstance(x,bool)`), but it is behaviourally equivalent and is what the T4 tests pin; I do not flag it as a defect — it is a deliberate, tested choice (S4H report self-attack).

## ITEM 8 — anything else INSIDE the S4H hunks (exhaustive discovery, disciplined disposition)

Hunks examined: C4:249-273 (M4 argv 249-251; M5 comment 252-253 + sent guard 255-257; A2 comment 258-264; status 265-269), T4:301-331 (the two status tests), T4:425-437 (config dup), T4:523-551 (argv + fixture-pin tests).

  - Ordering (C4:265-269): `status` is read once into a local, the type guard (266-267) and the 2xx bound (268-269) both run BEFORE the A2 header parse (270+). This is the correct fail-fast order: a non-int or non-2xx status is named before the header is even read, so a bad-status bundle fails at the status and never reaches (and never masks) a bad header. SOLID.

  - The 2xx bound message `response-status-not-2xx: {status}` (C4:269) interpolates the raw status; for a huge int it prints the full value (item 3, 10**30) — no truncation, no overflow, no NaN (Python int is unbounded). SOLID.

  - The two T4 status tests are cleanly split: `test_response_status_must_be_2xx` pins the BOUND (200/299 pass, 503/199/300 fail with the exact reason), `test_response_status_requires_an_integer` pins the TYPE guard ("200"/True → absent). They are not tautological with each other (a bound-only mutant does not break the integer test, a type-only mutant does not break the bound test) — verified by the item-2/6 mutants. SOLID.

  - `test_duplicated_config_header_is_refused` (T4:425-437) uses two DIFFERENT-CASE spellings (lower + upper) that both survive JSON; the guard (C4:327) counts case-folded hits, so `len(hits) > 1` fires before the value check — it pins the "last-wins config pass" (a same-key duplicate would collapse in JSON and be a non-issue, same as the status case in item 3). SOLID and correctly scoped to the realistic multi-key shape.

  - `test_request_argv_is_required` (T4:523-532) pops `argv` from a real bundle copy; the guard (C4:250-251) requires a non-empty list. This is a genuine identity check (request identity includes the capture argv, not just the wire fields), not a vacuous presence test — the bundle's other fields are byte-identical to the fixture, so only argv's absence is what fails it. SOLID.

  - `test_fixture_compression_header_is_pinned_after_request_equivalence` (T4:535-551) is the M5 killer and (item 4) is reachable only via `--fixtures-dir`; it is a hardening pin, correctly documented by the C4:252-253 comment. No defect.

  - No stale comment/doc inside these hunks is falsified by the diff: the A2 comment (258-264) still accurately describes the header check that follows the new status checks; the M5 comment (252-253) accurately describes the `--fixtures-dir` self-consistency the pin guards against. SOLID.

No in-boundary defects found in the hunks beyond the FOLLOW-UP (dup-key) already recorded in item 3.

## Finding inventory

F-01 — FOLLOW-UP — duplicate scalar `status` keys collapse last-wins. Evidence level: SOLID (real checker CLI on a hostile scratch bundle). Contract mapping: none; AF-AP-41 is analogous hardening, not a frozen S4H criterion. Canonical-path status: NOT canonical (the producer emits one dict key and cannot produce this raw shape). Material effect: none for the production path; a single forged `status: 200` is already simpler, and the attestation pins the file. Reproduction: item 3's `503` then `200` raw JSON → rc 0/PASS. Suggested fix: if desired, reject duplicate `status` keys during JSON load by preserving key pairs; file a D-034 `verify-followup`, not a repair blocker.

F-02 — INFO — M5 is real CLI hardening but not mint-path load-bearing. Evidence level: SOLID. Contract mapping: F4's killing-test demand. Canonical-path status: `--fixtures-dir` is a real checker CLI flag but is absent from S0-04 `spec.json` and `scripts/proof-runner`. Material effect: deletes a hollow green on the alternate-fixture CLI path; no effect on today's mint pass. Reproduction: item 4, M5 deleted → PASS; present → `sent-compression-header-value: on`. Suggested fix: none; retain test/comment and document the reachability distinction.

F-03 — INFO — the brief's premise range is stale; this causes CONTRACT-INVALID rather than a code blocker. Evidence level: SOLID (git ancestry + scoped diff). Contract mapping: item 1's exact command and explicit stop condition. Canonical-path status: repository git history. Material effect: the frozen premise is false, so its evidence boundary is unusable literally; no S4H production byte escaped. Reproduction: item 1, d92bfcf..a815883 shows two sibling A5q tests; true-parent 7a6a75a..a815883 names exactly C4/T4/result/ledger in `proofs/ tests/`, and the C4/T4 deltas are byte-identical. Suggested fix: coordinator corrects the frozen base to 7a6a75a and redispatches/regrades item 1; no C4/T4 repair.

F-04 — INFO — M17 mutant's named test kills through incidental TypeError. Evidence level: SOLID. Contract mapping: item 2 requires the distinction. Canonical-path status: real checker CLI through T4. Material effect: none; final code emits the exact named `response-status-absent`, and hostile float/bool/null/absent shapes independently confirm the guard. Reproduction: item 2, delete M17's type guard → `TypeError` at the bound and T4:331 reds. Suggested fix: none.

No BLOCKER or UNVERIFIED findings. F-03 is a contract-defeating premise error; it maps to the separate CONTRACT-INVALID recommendation, not to a production-code BLOCKER.

## DISCREPANCIES

- Item 1 as worded (`git diff --stat d92bfcf a815883 -- proofs/ tests/` "must name exactly C4, T4, result.json, ledger.json") does NOT reproduce: that range names SIX files under proofs/+tests/ (the four S4H files PLUS tests/test_s0_01_check_acp_conformance.py and tests/test_s0_02_buzz_authz.py). Root cause: d92bfcf is an ANCESTOR of the PIN but not its PARENT — the true parent is 7a6a75a, and the intermediate commits are the sibling A5q landing (2e02afd, which is the only thing that touched the two S0-01/S0-02 test files) plus transcript/ledger bookkeeping. The C4/T4 diff is BYTE-IDENTICAL between the two ranges (cmp: IDENTICAL), and the true-parent range `git diff --stat 7a6a75a a815883` names exactly the four S4H code/attested files (+ S4H's own brief/report/transcript artifacts). Measured truth: the S4H landing is exactly C4 + T4 + the two attested artifacts; the brief's `d92bfcf` base is a stale label for "S4H's parent". This is a contract defect under item 1's explicit `Anything else: CONTRACT-INVALID and stop` instruction, even though the measured code boundary is clean.

- The brief/lane both call the parent suite "69 tests"; measured 74 at d92bfcf and 79 at the PIN (the lane's own report flags the same 69→74 discrepancy; the +5 are the S4H additions). I verified 74 (parent) and 79 (PIN) by direct collect+run.

- S4H's own report is honest and accurate on everything I re-derived (parent 74×4 survivors, PIN 1-failed×4 killers, M17 TypeError, 79×2, pyflakes 0, ap_screen 0/3, `sandbox:vm` vs the un-landed `sandbox:fedora`). No false claim found in it.

- One bounded scratch-tooling retry: the first canonical bound-mutant helper attempted `git archive` with the pipe as a literal argv element and failed before creating a mutant; the corrected shell pipeline ran both mutants canonically. One earlier bound-direct-CLI run placed the mutated checker outside `proofs/S0-04`, so its default fixture path was wrong; rerun with explicit `--fixtures-dir` and then through fresh archive copies produced the item-6 canonical reds. No source-tree effect.

- `scripts/report_lint.py` bounded result before final prose: `report_lint: 43 refs — OK 32, NEAR 2, MISS 0, UNCHECKABLE 9, UNRESOLVED 0 (worktree)` (the floor 10 is met; the remaining UNCHECKABLE/NEAR rows are range-only context citations, and MISS is zero).

## NOT-done

- Did NOT run the proof-runner or ledger-gen against the shared tree (read-only boundary); ran them only on scratch `git archive` copies. Did NOT touch the model server, OmniRoute, any unit, the S0-04 evidence, or any other lane's tree.

- Batches 1 and 3 of issue #7 (F1/F3/F6 eat/document, F2/F7 PC re-capture) are out of scope by the brief; not assessed.

- Did NOT fix the dup-key FOLLOW-UP (role = verify only); returned it to the coordinator.

- The three sibling-lane trees (K1-c, B7, VERIFY-A5q) were not touched; all my writes are under `../scratch/` and `/tmp`.

- Did not re-verify the S0-01/S0-02 test files the range diff named (they belong to A5q, out of my scope; I only confirmed they are not part of the S4H landing).

## GATE RECOMMENDATION

CONTRACT-INVALID.

The frozen item-1 premise is already defeated: its literal command names six files, while the contract says it must name exactly four and commands `CONTRACT-INVALID and stop` for anything else. The true parent is 7a6a75a, not d92bfcf. The correct scoped parent diff names exactly C4, T4, result.json and ledger.json, and the C4/T4 delta is byte-identical to the stale-base delta; there is no production-code blocker in S4H. But a verifier cannot silently amend the frozen command to make it pass.

Ancillary evidence after the required stop condition found the S4H code repair technically sound: both file hashes match; the mint is internally consistent (ledger no-op, `env_fingerprint: sandbox:vm`, attested C4 hash = measured sha256); all four formerly-un-killed guards die at their named PIN tests; both 2xx edges are independently red-green; all five new tests are de-vacuous; hostile shapes behave as expected; and the gates pass (79×2, pyflakes 0, ap_screen 0/3). This evidence may support a corrected redispatch, but it cannot turn this frozen contract green.

Follow-ups after contract correction:

  - F-01: scalar-`status` duplicate-key raw-JSON hardening (D-034 `verify-followup`; not a code blocker, producer cannot emit it).

  - F-02: retain M5 as `--fixtures-dir` CLI hardening and document that the mint does not use that flag.

  - No sibling bool-guard follow-up: every sibling checker already excludes bool.

This is a RECOMMENDATION, not a verdict; the coordinator owns the gate.

retro: the brief-specific `CONTRACT-INVALID and stop` clause governs over the general "build on measured truth" premise-conflict rule; no repository lesson was baked because this verifier lane is read-only.

graft saved ~12,891 tokens this turn.
