# PC lane — VERIFY-S4H (targeted adversarial verification of ONE repair: issue #7 batch 2, the S0-04 checker hardening F4 + F5)

PIN: a815883

Role: adversarial-verifier. Route: the LOCAL Qwen verify route (`agentfactory-verify-local`, the pc_lane.sh default for
adversarial-verifier — do NOT set HERMES_MODEL; the effort is the vLLM server's default, D-028's xhigh is not
verifiable on this route). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Report: draft after EACH item at
`tasks/briefs/s0-04-support/VERIFY-S4H-report.md`, return it whole as your final message. You VERIFY; you never fix.
A finding is file:line-bounded, reproduced through the real path, and graded by the blocking predicate
(contract-mapped · reproduced canonically · materially effective · a concrete discriminator · in-boundary). Emit a GATE
RECOMMENDATION (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID), never a verdict — the
coordinator decides; under D-034 a non-blocking finding becomes a `verify-followup` issue. THREE sibling lanes may share
this host (K1-c, B7, VERIFY-A5q) — never touch their files or trees. Owner authorization: defensive proof-checker work
on the owner's own repository.

## Scope — one repair, nothing else
Issue #7 (GitHub, VERIFY-S004's seven non-blocking follow-ups on the S0-04 compression-off proof) batch 2 = F4 (four
defense-in-depth guards with no killing test: M4 argv presence, M5 the fixture's sent-compression-header pin, M15 the
duplicated config header, M17 the response-status type) + F5 (no 2xx assertion on the response status). The repair
S4H (brief `tasks/briefs/pc/pc-s4h.md`, report `tasks/briefs/s0-04-support/S4H-report.md`, built on d92bfcf, landed at
the PIN) touched C4 = `proofs/S0-04/check_compression.py` (C4:252-253 a comment; C4:265-269 `status` read once,
`type(status) is not int` → `response-status-absent`, `not 200 <= status < 300` → `response-status-not-2xx: <status>`,
both BEFORE A2's header parse) and T4 = `tests/test_s0_04_compression.py` (five tests: T4:301-331
`test_response_status_must_be_2xx` + `test_response_status_requires_an_integer`, T4:425-437
`test_duplicated_config_header_is_refused`, T4:523-532 `test_request_argv_is_required`, T4:535-551
`test_fixture_compression_header_is_pinned_after_request_equivalence`), and REGENERATED the attested mint
`proofs/S0-04/result.json` + `proofs/ledger.json` on the sandbox (AF-AP-56; C4 is an attested input). Batches 1 and 3
of issue #7 (F2/F7 the PC re-capture, F1/F3/F6 eat/document) are NOT in scope. The coordinator re-ran the lane's suite
and three of its mutants — that is NOT independent verification (orchestration rule 0f); THIS lane is the independent
hostile pass, with NEW shapes, never the builder's own cases.

## Items (each: what you did · the exact command · the exact output · SOLID/UNSURE · blocking? each predicate clause)
1. PREMISE (first; stop on failure): `git diff --stat d92bfcf a815883 -- proofs/ tests/` must name exactly C4, T4 and
   `proofs/S0-04/result.json` + `proofs/ledger.json`; `git diff d92bfcf a815883 -- proofs/S0-04/check_compression.py`
   must be the two hunks above (paste it whole — it is 7 lines); `sha256sum` C4 =
   fa39bb78c7d589cc678af163075393244ec5ab7894e8a9917ac4af5363610981, T4 =
   2085b90bdde03c1b605a8e3d61a06f178e122327e9001d04ecd9a7342b7a5404; `git diff d92bfcf a815883 --
   proofs/S0-04/result.json` must change ONLY timestamps, the C4 attested hash and the digest (paste the `-`/`+` lines).
   Anything else: CONTRACT-INVALID and stop.
2. The premise's survivors at the parent: on a scratch `git archive d92bfcf` copy, delete each of the four guards
   (M4 C4:250-251 at d92bfcf, M5 :252-255, M15 :321-322, M17 :263-264 — read them there, the lines are the PIN's
   parent's) one at a time (a mutant must COMPILE and collect — AF-AP-78) and run the suite: the lane pasted
   `74 passed` for each. Then the same four mutants on a scratch copy of the PIN's C4 with the PIN's T4: each must
   die at its NAMED killer — paste the `1 failed` line and the assertion. M17's mutant on the PIN reaches the bound
   comparison first (`'<=' not supported between instances of 'int' and 'str'`): state whether that is a kill at the
   named assertion or an incidental TypeError kill, and which line the killer actually reds on.
3. NEW HOSTILE SHAPES for F5's bound and M17's type guard — you design them; this list is the floor. For each: the
   expected named reason BEFORE running, the real CLI run (`run_checker` shape or `python3
   proofs/S0-04/check_compression.py <bundle>`), the observed reason, the grade. `status` = 200.0 (a float that looks
   right — expect `response-status-absent`), `False`, `None`, the key ABSENT, `-200`, `2000`, `204` and `206` (2xx —
   expect PASS: state whether a 204/206 chat-completion response carrying a compliant compression header is a hollow
   green for A2/A3 or a legitimate pass, from what A3's byte-compare needs), a DUPLICATED top-level `status` key in
   `response.json` (JSON last-wins — does `_read_json` refuse duplicate keys the way the config-header path does
   (`config-header-duplicated`)? If a duplicated `status` with values 503 then 200 PASSes, grade it by the predicate
   with the AF-AP-41 class in view), and `status` nested under `headers`.
4. M5's REACHABILITY (the lane corrected issue #7, which called M5 an equivalent mutant): through the REAL CLI with the
   M5 guard deleted on a scratch copy, a request+fixture pair that BOTH carry `x-omniroute-compression: on` under
   `--fixtures-dir <alt>` must PASS (the hollow green the guard prevents) and must fail
   `sent-compression-header-value: on` with the guard present — paste both. Then settle whether `--fixtures-dir` is on
   the PRODUCTION path: read `proofs/S0-04/spec.json` (the proof-runner's argv for the positive leg) and
   `scripts/proof-runner`; if the runner never passes `--fixtures-dir`, the guard's reachability is CLI-only — say so
   and grade "materially effective" honestly (a guard on a flag the mint never uses is hardening, not a contract gate).
5. The regenerated mint (READ-ONLY — never run the proof-runner INTO the shared tree): on a scratch `git archive
   a815883` copy, `python3 scripts/validate-ledger integrity --root <copy>` must report S0-04 PRESENT; `python3
   scripts/ledger-gen --root <copy>` followed by `git -C <copy> diff` is impossible (no .git) — instead compare the
   regenerated `proofs/ledger.json` bytes to the PIN's with `cmp`/`sha256sum` before and after: a no-op means the
   committed ledger matches its inputs. Confirm `env_fingerprint` in the PIN's result.json names the sandbox venue
   (`sandbox:vm`), never this host. Paste.
6. De-vacuous pass on the five new tests (scratch copies of T4): flip each expected outcome → red at its OWN assert
   (paste each). And the bound's two edges independently: a mutant `200 <= status < 301` must red on the 300 case and a
   mutant `199 <= status < 300` on the 199 case — name the failing case each time (the lane's `< 5000` mutant covers only
   the upper edge).
7. Gates on the PIN's bytes (four lanes share the 12 cores): `python -m pytest -n 4 -q -p no:cacheprovider --basetemp
   ../scratch/bt/<run> tests/test_s0_04_compression.py` TWICE (the lane pasted `79 passed` ×2 — paste yours);
   `python -m pyflakes proofs/S0-04/check_compression.py tests/test_s0_04_compression.py` rc 0; `python3
   scripts/ap_screen.py proofs/S0-04/check_compression.py` (0 hits at the PIN) and `python3 scripts/ap_screen.py --tests
   tests/test_s0_04_compression.py` (three pre-existing hits at T4:905 — anything else is a finding). INFO sweep
   (report, never fix): `grep -n "isinstance(.*, int)" proofs/*/check_*.py proofs/*/tools/*.py` — every sibling status
   or count guard that admits `bool` the way M17 did; list them as follow-up candidates with file:line.
8. Anything else INSIDE the S4H hunks (C4:249-273, T4:298-333, T4:422-440, T4:520-552). Exhaustive discovery;
   disciplined disposition.

## Boundary
READ-ONLY on the tree: attack through SCRATCH COPIES only (`../scratch`); never git-restore/stash/checkout the shared
tree; never `git add/commit/push`; never run the proof-runner or ledger-gen against the shared tree; never touch the
model server, OmniRoute, any unit, the S0-04 evidence, or another lane's tree. No live captures, no outward action.

## Gate mechanics (each call under Hermes's 420 s terminal cap)
- `export S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`;
  `/home/rocco/venv-agent-factory/bin` first on PATH; `mkdir -p ../scratch/bt`; an absolute SHORT `--basetemp`.
- pytest on this host: `python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt <files>` DIRECTLY
  (`scripts/pc_suite.sh` is the SANDBOX's launcher and cannot run here). The S0-04 suite runs in seconds.
- CODE INTEL FIRST: `graft skeleton` / `graft ask` before any whole-file read. `report_lint` gates on a FLOOR
  (`--min-refs 10`, maps `C4=proofs/S0-04/check_compression.py` `T4=tests/test_s0_04_compression.py`); apply its
  `fix:` hints for at most THREE rounds, then paste and finish; paste its summary as PLAIN text.

## Report shape (DATA)
Per item: command · exact output · SOLID/UNSURE · blocking? (the predicate, each clause answered) · the file:line.
Then: the shape table (item 3: shape · expected · observed · grade), the mutant table (items 2 and 6: mutant · killer ·
assertion · `N failed` or SURVIVES), the M5 reachability verdict (item 4), DISCREPANCIES, NOT-done, GATE
RECOMMENDATION. Never a fix, never a verdict.
