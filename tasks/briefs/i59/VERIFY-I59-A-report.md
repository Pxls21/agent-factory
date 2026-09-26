# VERIFY-I59-A report: the attested-inputs change attacked against its contract (task #312, issue #59 F-1)

Lane: adversarial-verifier (sandbox, Opus 5.5). Brief: `tasks/briefs/i59/VERIFY-I59-A-brief.md`. PIN: origin 2a50a65.
Change under test: `tasks/briefs/i59/I59-A.patch`. Frozen contract: `tasks/briefs/i59/I59-A-brief.md` (CONTRACT 1-5,
EVIDENCE DEMANDS). Started 2026-09-26 06:1xZ. Written incrementally; sections fill as the work lands.

## 0. Premise check (the brief's first action)

Re-measured at 06:1xZ in the shared tree (HEAD 8a92179, origin 2a50a65), every line identical to the brief's block:
- `git log -1 origin/...`: `2a50a65 I59-A round 1 home (task #312; held for the issue #5`.
- `git diff --stat origin/... HEAD -- scripts/ proofs/ tests/ | tail -1`: empty (HEAD's code = the PIN's).
- `sha256sum tasks/briefs/i59/I59-A.patch | cut -c1-16`: `8e83b983e966ce2b`; `grep -c '^diff --git'`: 4.
- `git apply --check -v`: the four files checked, rc 0.
- The builder report's section headings: the same 16 lines (0 to 15).
- `df -h /`: 1.7G free.
Verdict: premise HOLDS. Not CONTRACT-INVALID.

## 1. Scratch worktree and the PIN baseline (06:1xZ)

Worktree: `git worktree add --detach /tmp/v59a/wt 2a50a65` (under `/tmp` with mode 755, not the scratchpad: S0-11's
uid 65534 child must traverse the path, as the builder found; 214 MB). All runs below use `PYTHONDONTWRITEBYTECODE=1`
for the caller (the runner's clean environment does not pass it to the legs; see INFO I-5).

The PIN's code, before the patch (pasted):
- `validate-ledger integrity --root . --ledger proofs/ledger.json`: S0-01 ... S0-12 PRESENT, rc 0.
- One byte of `proofs/S0-01/pins.py` (offset 1190, `-` to `X`): only `S0-01 INVALID`
  (`attestation-mismatch: S0-01 proofs/S0-01/pins.py`); S0-02, S0-03, S0-05 PRESENT. Issue #59 F-1 as filed, reproduced.
- One byte of `proofs/S0-08/fixtures/malformed-marker/blocked.json`: S0-08 PRESENT, rc 0 (the A1 gap, reproduced).
- One byte of `docs/adr/0005-foundry-host.md`: S0-09 PRESENT. One byte of `upstream.lock.yaml`: S0-06, S0-12 PRESENT.
Each file restored byte-identical (sha checked).

Patch applied in the worktree only (`git apply`): sha256 prefixes `1fe875ebbcbdd2b9` validate-ledger,
`ad9a8d7721078062` registry.yaml, `dae0cd1c8a4c2798` test_validate_ledger.py, `2bce9a2e97c95764` test_attested_inputs.py:
all four equal the brief's premise.

Key sets before any re-mint (the patched `proof_attestation` over the worktree vs each committed `result.json`,
`scratchpad/verify-i59a/keydiff.py`): S0-01 247, S0-04 44, S0-07 14, S0-11 13 keys, identical sets, and every hash
identical except `scripts/validate-ledger` and `proofs/registry.yaml` (the two changed closure files). S0-08 29 to 30:
the one added key is `proofs/S0-08/fixtures/malformed-marker/blocked.json` (round 2). Each declaring proof adds exactly
its declared paths, removes none: S0-02 208 to 214, S0-03 91 to 96, S0-05 62 to 63, S0-06 166 to 168, S0-09 11 to 12,
S0-10 11 to 12, S0-12 14 to 16.

## 2. The landing, section 5 steps 1-2, dry-run in the worktree (06:18Z)

The builder's step 1 verbatim (root = the worktree): no `FAILED` line; the twelve result.json files (pasted summary):
```
S0-01 pc-bridge:vm attested=247  S0-02 pc-bridge:vm attested=214  S0-03 sandbox:vm attested=96   S0-04 sandbox:vm attested=44
S0-05 pc-bridge:vm attested=63   S0-06 sandbox:vm attested=168    S0-07 sandbox:vm attested=14   S0-08 sandbox:vm attested=30
S0-09 sandbox:vm attested=12     S0-10 sandbox:vm attested=12     S0-11 sandbox:vm attested=13   S0-12 sandbox:vm attested=16
```
Step 2: `integrity --root .` twelve PRESENT, `conformance_checked_decision numerator=3 denominator=3`,
`execution_proof numerator=9 denominator=9`, rc 0. `ledger-gen --root .`: 12 insertions, 12 deletions (the twelve
normalized digests); a second run `cmp` rc 0 (idempotent). `integrity --ledger proofs/ledger.json` rc 0.
`stage1-gate --root .` rc 0. `check-proof-status.py .` (the worktree shares the repo's `accepted/*` refs): twelve
`... changed since accepted/S0-NN (regenerated after acceptance) ...` lines, rc 1, every tag stale as expected.

One-byte and replacement demonstrations on the re-minted worktree (`integrity --ledger`, pasted; each restored and
re-checked twelve PRESENT):
- D1 one byte of `proofs/S0-01/pins.py`: S0-01, S0-02, S0-03, S0-05 INVALID, each `attestation-mismatch: S0-0N
  proofs/S0-01/pins.py`; `S0-09 PRESENT`; 8 PRESENT; rc 1. (On the PIN's code the same byte left S0-02/03/05 PRESENT.)
- D2 one byte of `proofs/S0-08/fixtures/malformed-marker/blocked.json`: `S0-08 INVALID`, `attestation-mismatch: S0-08
  proofs/S0-08/fixtures/malformed-marker/blocked.json`, rc 1.
- D3 one byte of `docs/adr/0005-foundry-host.md`: `S0-09 INVALID`, `attestation-mismatch: S0-09 docs/adr/0005-foundry-host.md`.
- D4 one byte of `upstream.lock.yaml`: S0-06 and S0-12 INVALID, each `attestation-mismatch: ... upstream.lock.yaml`.
- D5 `docs/adr/0006-gbrain-seam.md` deleted: `S0-10 INVALID`, `attestation-mismatch: S0-10 docs/adr/0006-gbrain-seam.md`,
  `registry-schema: S0-10 extra_attested_inputs docs/adr/0006-gbrain-seam.md is not a regular file`.
- D6 `SBOM.yaml` replaced by a symlink to a byte-identical copy: `S0-12 INVALID`, `attestation-mismatch: S0-12
  SBOM.yaml`, `registry-schema: S0-12 extra_attested_inputs SBOM.yaml is not a regular file`.

## 3. An independent enumeration of the checkers' reads (strace, contract item 3; brief attack 4)

Instrument (mine, not the builder's audit hook): each proof re-minted through the canonical `scripts/proof-runner run`
under `strace -f -ff -y` (openat/open/creat, the stat family, readlink, getdents64, execve, chdir, the write calls, the
clone family), `scratchpad/verify-i59a/st_mint.sh`; classified by `st_parse.py` over every pid but the runner's own
(the legs and all their descendants, S0-11's `unshare`/`setpriv` uid 65534 children and `nsenter` probes included:
root traces them). A `.pyc` read under `__pycache__` is mapped to its source. All twelve minted rc 0 under strace.

Result: for every proof the repo files its legs OPEN outside `proofs/<id>/` and the closure equal the registry's
declaration exactly: S0-02 the six S0-01 files, S0-03 the five, S0-05 `pins.py`, S0-06 the root fixture and the lock,
S0-09 and S0-10 their ADRs, S0-12 `SBOM.yaml` and the lock; S0-01, S0-04, S0-07, S0-08, S0-11 none. No leg opens a
repo file its re-minted attestation lacks (the own `result.json` aside: S0-11 reads it, A2). S0-11's isolated children
read only `proofs/S0-11/fixtures/*.py` (attested), so the named S0-11 blind spot hides no read today. The builder's
section 1 table is CONFIRMED for opens.

What the opens do not show (the builder's named blind spots, measured):
- S0-12 STATS two repo files it never opens: `LICENSE-DECISION.md` and `THIRD-PARTY-NOTICES.md`
  (`check_pin_diff.py:23-24`, `if not (root / name).exists(): ... return 1`). Its verdict depends on them; they are not
  attested. See finding F-1 below.
- Directory listings outside the proof's directory are import-machinery only: S0-02 and S0-03 list `proofs/S0-01` and
  `proofs/S0-01/tools` (their `sys.path` entries); S0-11's `python3 -c` nsenter probes list the repo root (`''` on
  their `sys.path`, cwd = the root). No verdict reads a listing's content; a shadowing module could (INFO I-3).
- Non-Python children: S0-11 only (`unshare`, `setpriv`, `nsenter`), no repo reads of their own.
- Writes into the tree while grading: only `__pycache__` (S0-01's legs and S0-02's write `proofs/S0-01/__pycache__/*.pyc`,
  S0-02 writes `proofs/S0-02/oracle/__pycache__/`), excluded from every attestation.

## 4. The declaration check and the attestation, attacked through the real validator CLI (06:2xZ)

Harness: `scratchpad/verify-i59a/hostile.py` (a minimal root built with the builder's own `_copy_contract`, the value
declared on S0-05, `validate-ledger integrity` run as a subprocess before and after S0-05 is minted with the real
`proof_attestation`). Every case below is reproduced; findings quoted verbatim.

Refused by name at the registry check (contract item 1): a trailing slash `docs/adr/` and the empty string (`is not in
canonical form`); a dict, `null`, `true` (`must be a non-empty list of paths`); a nested list and a `null` item
(`item N is not a string`); `scripts/validate-ledger` and `proofs/registry.yaml` (`is in the attestation closure
(already attested)`, the two closure members the builder's tests do not name); the bare own directory `proofs/S0-05`
(`is inside proofs/S0-05/ (already attested)`); `.` and a FIFO (`is not a regular file`, no hang: the check stats,
never opens). The closed key set holds: `extra_attested_input`, `Extra_Attested_Inputs` and a key with a trailing
space each read `registry-schema: S0-05 unknown key(s) ... — every registry key must bind a gate`.

Absent spellings pass the registry check and are refused where they bind a verdict (the builder's deviation X1): a
backslash path, a fullwidth solidus, a Unicode hyphen in the own-directory prefix (`proofs/S0<U+2010>05/spec.json`), a
lowercase `proofs/s0-05/spec.json` and a NUL byte each give rc 0 with no result, and `S0-05 INVALID` with `... is not a
regular file` once a result exists. No false PRESENT: an absent declared file is never hashed.

Through the canonical runner (worktree, S0-04 given `extra_attested_inputs: ["docs/absent-input.md"]` for the run, then
restored): `proof-runner run` rc 0, the key not recorded (44 keys); integrity `S0-04 INVALID`, `registry-schema: S0-04
extra_attested_inputs docs/absent-input.md is not a regular file`; the file created afterwards: `attestation-mismatch:
S0-04 docs/absent-input.md`. The contract's "a result minted while a declared file was absent" holds on the real path.

Accepted, as the contract allows (INFO I-1): another proof's artifact `proofs/S0-01/result.json`, the ledger
`proofs/ledger.json` (a cycle with `ledger-gen`), `.git/HEAD`, a `__pycache__` file, `proofs/schemas/sub/x.json` (correctly
outside the closure). A path segment over 255 bytes crashes the validator and `proof_attestation` with
`OSError: [Errno 36] File name too long` (a traceback, no finding, no states printed; fail-closed; FOLLOW-UP FU-2). A
newline in a declared path splits its finding over lines, so a crafted value can print a line such as `S0-09 PRESENT`
inside a failing (rc 1) integrity run (INFO I-2).

## 5. The drift guard attacked (contract item 4; brief attack 3)

The builder's guard (`_observe` + `_verdict`, imported from the worktree's `tests/test_attested_inputs.py`) over its own
scratch copy of S0-09 with one more planted read each (`scratchpad/verify-i59a/planted_more.py`), pasted:
```
open_computed    target=docs/planted_d.md  RED names-target=True   (open() on an os.path.join built at run time; brief shape)
helper_module    target=docs/planted_e.md  RED names-target=True   (read inside proofs/S0-09/planted_helper.py, imported; brief shape)
os_open          target=docs/planted_f.md  RED names-target=True
io_open_code     target=docs/planted_g.md  RED names-target=True
runpy_run_path   target=lib/planted_h.py   RED names-target=True
subprocess_cat   target=docs/planted_d.md  RED (unnamed child process)
sqlite3_connect  target=docs/planted_i.db  GREEN (not caught)
ctypes_fopen     target=docs/planted_k.md  GREEN (not caught)
stat_exists      target=docs/planted_j.md  GREEN (not caught; a named blind spot)
listdir          target=docs               GREEN (not caught; a named blind spot)
```
The five read shapes the contract and the brief name all red with exactly the planted path. Two reads the builder's
docstring does not name escape the hook: a C-level open (`sqlite3.connect` raises `sqlite3.connect`, not `open`;
`ctypes`). No current checker imports `sqlite3`, `ctypes`, `zipimport`, `runpy`, `mmap`, `shelve` or `dbm` (grep over
`proofs/`, rc 1), so no current verdict hides behind them (FU-5: name them in the docstring).

The stat blind spot is live today: see F-1.

## 6. Mutation (brief attack 7; 06:2xZ)

My harness `scratchpad/verify-i59a/mutate_v.py` (AF-AP-223 rules: the unmutated control first, every mutant compiled, a
kill = every named test FAILED with no ERROR, a literal denominator, each file restored and sha-checked; run in the
worktree against the round-2 files, whose sha256 prefixes were equal before and after). Pasted:
```
CONTROL (unmutated, 44 named tests): rc=0 44 passed in 6.75s
KILLED  B-V3 absolute 1/1 · B-V4 dotdot 1/1 · B-V5 glob 3/3 · B-V6 canonical 2/2 · B-V7 duplicate 1/1 · B-V8 own directory 1/1
KILLED  B-V10 registry not-regular 4/4 · B-V11 no resolve check 3/3 · B-V12 verdict absence 2/2 · B-V13 extras not hashed 3/3
KILLED  B-V14 key not allowed 2/2 · B-M1 skip-anywhere 4/4 · B-M2 skip nothing 1/1 · B-G1 hook never installed 2/2
KILLED  B-G2 outside rule off 3/3 · B-G4 spawn rule off 1/1 · B-G5 inside rule off 1/1 · B-G7 own-script check off 1/1
KILLED  B-G8 no bytecode prefix 2/2 · B-G9 deferral widened 1/1
SURVIVED       N1 closure refusal covers scripts/proof-runner only: 0/2 named FAILED; 2 passed in 0.36s
SURVIVED       N2 own-directory refusal covers direct children only: 0/1 named FAILED; 1 passed in 0.20s
KILLED         N3 undeclaring proofs gain a key: 5/5 named FAILED
KILLED         N4 attestation hashes through a symlink: 1/1 named FAILED
SURVIVED       N5 verdict binding tests existence only: 0/2 named FAILED; 2 passed in 0.59s
KILLED         N6 declarations read from the wrong entry: 3/3 named FAILED
SURVIVED       N7 the verdict binding skipped when the recorded attestation is absent: 0/1 named FAILED; 1 passed in 0.27s
EXPECTED=27 KILLED=23 SURVIVED=4 INVALID=0
```
The builder's claim holds: 20 of its mutants (B-*, ids from its `scratchpad/i59a/mutate.py` and `mutate2.py`), each
re-run here, are KILLED as FAILED tests. Live differentials of my survivors (`survivor_diff.py`, the original validator vs
a scratch mutant copy, one minimal root each):
- N1: `proofs/registry.yaml` declared: original rc 1 with `... is in the attestation closure (already attested)`; mutant
  rc 0. Non-equivalent: no test declares `scripts/validate-ledger` or `proofs/registry.yaml` (FU-3).
- N2: `proofs/S0-05/fixtures/x.json` declared on S0-05: original rc 1 `... is inside proofs/S0-05/ (already attested)`;
  mutant rc 0. Non-equivalent: the own-directory test uses a direct child only (FU-3).
- N5: a result minted while its declared input was a symlink: original `S0-05 INVALID`, mutant `S0-05 PRESENT` (rc 1 in
  both: the registry-level finding stays). Non-equivalent in the state `ledger-gen` writes; no test mints over a
  declared symlink (FU-3).
- N7: EQUIVALENT (my design error): the result schema requires `attestation` (an object), so a result without one is
  INVALID by the schema before the binding matters.
None of the survivors changes a verdict the contract's gates read (every one keeps integrity at rc 1 or changes only a
finding): test gaps, FOLLOW-UP.

## 7. The landing, section 5 steps 1-6, in a tag-free clone (06:4xZ)

Clone: `git clone -q --no-tags --shared --no-checkout /home/user/agent-factory /tmp/v59a/clone`, detached at 2a50a65,
`git tag -l` empty, `remote.origin.tagOpt=--no-tags` (the CI shape: `git ls-remote --tags origin 'refs/tags/accepted/*'`
prints nothing, so CI's `fetch-tags: true` fetches no anchor either). Patch applied, the four sha256 prefixes equal.

- Step 1, re-mint (re-run, not copied): all twelve rc 0. Each attestation equals the worktree mint's, and the recorded runs
  are equal for eleven proofs; S0-07's differ (its stdout prints absolute paths: the builder's A3, reproduced).
- Step 2: integrity rc 0 (12 PRESENT, 9/9 and 3/3); `ledger-gen` twice, `cmp` rc 0; `integrity --ledger` rc 0;
  `stage1-gate` rc 0.
- Step 3: `git rm -q` of the twelve tag files; `git tag -d` prints `error: tag 'accepted/S0-NN' not found.` twelve times
  (no refs in the clone; harmless here, it deletes the owner's local refs in the real tree). Twelve `PROOF-ANCHOR: S0-NN =
  PENDING-OWNER-TAG (...)` lines inserted under the twelve `PROOF-STATUS` lines (the section 5 template, one line each).
- Step 4: `EXPECTED_PENDING` = the twelve.
- Step 5: `python3 scripts/check-proof-status.py .` rc 0; its output is exactly twelve `proof-status: WARNING S0-NN:
  ACCEPTED with the anchor PENDING the owner's signed tag accepted/S0-NN (declared in the ledger) — not owner-verifiable
  yet` lines and nothing else.
- Step 6, `bash scripts/test_summary.sh --basetemp=<short>` (pasted; set ids by pc_suite's `set_id` formula, computed locally):
```
4 files set=379203742124 (test_validate_ledger, test_proof_status, test_s0_11_eval_hardening, test_attested_inputs)
  run 1: pytest-exit: 0  pytest-summary: 175 passed in 40.64s
  run 2: pytest-exit: 0  pytest-summary: 175 passed in 42.17s
6 files set=63923f3a5a15 (test_proof_runner, test_ledger_gen, test_no_laya_in_gates, test_s0_01_spec_runner,
  test_system1_context, test_s0_08_containment)   pytest-exit: 0  pytest-summary: 444 passed in 66.84s (0:01:06)
4 files set=f5fcca671f19 (test_s0_02_buzz_authz, test_s0_03_omniroute, test_s0_05_egress, test_s0_06_four_scope)
                                                   pytest-exit: 0  pytest-summary: 971 passed in 427.65s (0:07:07)
5 files set=f63a056b995b (tests/red/test_s0_01_adversarial, tests/red/test_s0_01_round4,
  tests/red/test_s0_01_backend_credential_screen, test_edit_snapshot_ap_screen, test_stage0_ci_workflow)
                                                   pytest-exit: 0  pytest-summary: 415 passed in 79.43s (0:01:19)
```
The floor's thirteen files plus the new one are all green in the landed state (175 + 444 + 971; the ten other floor
files split in two runs to stay under the 10-minute cap). The last set is the derived one (every test file naming the
validator, the registry, the runner or check-proof-status, grep over `tests/`), beyond the floor.
In the worktree before the anchor step (tags shared): the 4-file set read `3 failed, 172 passed`, the three
`tests/test_proof_status.py` committed-state tests on the stale tags, as the builder reported.

Red-green of the new file (a `git archive 2a50a65` mirror of `proofs scripts tests/conftest.py pyproject.toml docs/adr
SBOM.yaml upstream.lock.yaml fixtures` and the two root files, plus the new file alone): `44 failed, 19 passed`, 0 errors.
The 19 green in the red build are the eleven attestation-equality tests without a nested fixture (an invariant, green on
both sides by design), the guard over the four non-consuming proofs S0-01/S0-04/S0-07/S0-11, the guard's own-helper
controls (did-not-grade, hook-saw-nothing, the skip helpers) and `test_a_declared_symlink_is_never_hashed` (green on the PIN,
which hashes no declaration; it discriminates mutant N4). No tautology among the discriminating tests.

## 8. CI after the landing (brief attack 6)

What runs where (`.github/workflows/stage0-ci.yml`): `tests` (ubuntu, Python 3.12, a non-root runner user,
`fetch-tags: true`, `pytest tests/ -q` then pyflakes over `scripts/validate-ledger scripts/proof-runner` and
`proofs/S0-01 tests/`); `ledger-integrity` (`ledger-gen`, `git diff --exit-code proofs/ledger.json`, `integrity --ledger`);
`stage1-gate` (continue-on-error); `planning` (`scripts/verify-planning-repo.sh`); `harness-suites`
(`harness-ports/tests/run-all.sh`).

CI emulation in the landed clone (uid 65534 via `setpriv`, a Python 3.12.3 venv holding exactly the `tests` job's
pip set `pyflakes pytest jsonschema==4.25.1 rfc3339-validator==0.1.4 PyYAML>=6.0`, `S0_01_VENUE=ci`, no tags, and
`/home/user/nerdherderdani` hidden under a tmpfs in a private mount namespace so S0-07's checkout is absent as on CI):
- `tests`, the 4-file set: `pytest-exit: 0`, `pytest-summary: 163 passed, 12 skipped in 43.75s`. The guard skips
  exactly two, with their reasons: S0-07 (`leg(s) grade paths outside the repo that this venue lacks ...
  /home/user/nerdherderdani/fubuki-os`) and S0-11 (`leg(s) deferred with exit 2 ... isolation-capability-unavailable:
  nsenter-unavailable` on legs 0 and 2); the other ten proofs' legs grade on 3.12 non-root and pass. The other ten skips
  are S0-11's own pre-existing root-venue skips. (Without the tmpfs, S0-07 is not skipped: the path exists in this sandbox.)
- Lint, the two pyflakes steps: rc 0.
- `ledger-integrity`: `ledger-gen --output` on 3.12 non-root is byte-identical to the landed ledger (`cmp` rc 0);
  `integrity --ledger` rc 0, 12 PRESENT. The eleven declared inputs and the two S0-12 stat inputs are byte-identical
  to the PIN's blobs in the shared tree (no `.gitattributes`, no autocrlf), so CI's checkout hashes as the sandbox does.
- `stage1-gate`: rc 0. `planning`: `verify-planning-repo.sh` rc 0 in the landed clone (it prints the twelve WARNINGs).
- `harness-suites`: not run; its suites name no attested path (grep: two string fixtures under `proofs/S0-01`), so this
  change cannot move it.
- Not run: the whole `tests/` (5766 tests collected); every file that names a touched symbol or file is in section 7.

Are the guard's CI skips correct and visible? Correct: each fires only on its named cause (S0-07's absent absolute
path, S0-11's exit 2), and a real failure is never a skip (the builder's G9/G10 mutants, killed here as B-G9). Visible:
only as a count. CI runs `pytest tests/ -q` without `-rs`, so the two reasons never print in the CI log; the sandbox's
`test_summary.sh` passes `-rs` and shows them (FU-4).

## 9. Finding inventory (no severity filter; 06:5xZ)

**F-1 CONTRACT-DEFECT — S0-12's verdict rests on two repo files its attestation does not bind.**
`proofs/S0-12/check_pin_diff.py:23-24` returns 1 unless `LICENSE-DECISION.md` and `THIRD-PARTY-NOTICES.md` exist. It stats
them and never opens them, so the builder's audit hook (`open` events) and its enumeration missed them; the registry
declares only `SBOM.yaml` and `upstream.lock.yaml` for S0-12.
- Evidence: VERIFIED. strace sees the two `newfstatat` calls and no open (section 3). In the re-minted worktree,
  `LICENSE-DECISION.md` moved away: `integrity --root . --ledger proofs/ledger.json` prints `S0-12 PRESENT`, rc 0, while
  `python3 proofs/S0-12/check_pin_diff.py .` exits 1 with `sbom-missing-file: LICENSE-DECISION.md does not exist`.
- Red test: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-i59a/redtest/test_f1_s0_12_stat_inputs.py` (mints S0-12 with the canonical runner in a minimal root, removes
  the file, asserts the leg now fails, then asserts `S0-12 INVALID`). On the patched tree: `1 failed` at the last
  assertion. With `F1_REGISTRY=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-i59a/redtest/registry-fixed.yaml` (S0-12 declares the two files as well): `1 passed`.
  The new test file stays `63 passed` with that registry.
- Contract mapping: the frozen WHY ("a proof's attestation covers every repo file its verdict depends on") covers it.
  Item 3's text ("every repo file its checker reads while it grades") does not, since an existence test is not a read.
  The builder named the class ("a verdict that rests on ... a stat", N4) and did not measure whether a current proof has
  one. Under the frozen items 1-5 it is therefore not a qualifying blocker. It does demonstrably falsify evidence on the
  exact production path, so it is RETURNED for an explicit amendment, not expanded by me.
- Material effect: after the batch, the owner re-signs a S0-12 PRESENT that stays PRESENT when a verdict-determining
  input disappears: issue #59 F-1's own class, on the proof the patch already touches.
- Fix (in the builder's boundary, one registry line): S0-12 `extra_attested_inputs: ["LICENSE-DECISION.md", "SBOM.yaml",
  "THIRD-PARTY-NOTICES.md", "upstream.lock.yaml"]`; the guard's docstring names existence tests as a class the guard
  cannot see and that is declared by hand. Timing: before the landing. After it, the fix costs a second re-mint and a
  second owner re-sign of S0-12.

FOLLOW-UP:
- FU-1 The stale attestation description inside an ATTESTED file: `proofs/schemas/result.schema.json` says the
  attestation maps "every input file under the proof directory". It was already incomplete (the closure) and now omits
  the declared inputs. Fix it in this batch: any later edit of a schema re-mints all twelve again. Same for the
  ATTESTED INPUTS line in `.claude/skills/env-tool-quirks/SKILL.md:98`, which lists the closure and "the proof's own
  files" only (see I-7).
- FU-2 A declared path segment over 255 bytes: `OSError: [Errno 36] File name too long` in the validator (a traceback, no
  finding, no states) and in `proof_attestation`. Through the runner that exception DELETES the previously minted
  `result.json` (reproduced: first mint rc 0; re-mint with the long path rc 1, the result gone). Fail-closed; the trigger
  is a malformed registry edit. Fix: treat `OSError` in `_is_regular_file` as not regular, or refuse such a path by
  name in `_extra_inputs`.
- FU-3 Test gaps from the surviving mutants (section 6): declare `scripts/validate-ledger` and `proofs/registry.yaml` in
  the closure refusal (N1), a nested own-directory path (N2), and a result minted while its declared input was a
  symlink (N5, state INVALID vs PRESENT).
- FU-4 CI runs `pytest tests/ -q` without `-rs`: the guard's two CI skips (S0-07, S0-11) print only as a count.
- FU-5 The guard's docstring names children, stats and listings, not C-level readers: `sqlite3.connect` and a `ctypes`
  `fopen` escape the hook (section 5). No current checker uses them.
- FU-6 S0-07 attests nothing of the Fubuki checkout it imports: strace shows 8 modules executed from the checkout
  (`lint/persona_lint`, `src/fubuki_os/{__init__,errors,memory/{__init__,bounds,models},release/{__init__,hashing}}`, via
  the checkout's own `__pycache__`) and no read of `upstream.lock.yaml`. Already registered (builder N3, task #320).

INFO:
- I-1 Accepted by the declaration check, as the contract allows: another proof's artifact (`proofs/S0-01/result.json`:
  a re-mint of S0-01 would then invalidate the declarer), `proofs/ledger.json` (a cycle with `ledger-gen`), `.git/HEAD`,
  a `__pycache__` file (the own-directory walk excludes these; a declaration does not).
- I-2 A newline in a declared path splits its finding over lines: a crafted value can print `S0-09 PRESENT` as its own
  line inside a run that still exits 1.
- I-3 Directory-listing dependencies are import machinery only: S0-02/S0-03 put `proofs/S0-01` and `proofs/S0-01/tools`
  on `sys.path`, and S0-11's `python3 -c` nsenter probes run with cwd = the repo root (`''` on `sys.path`). A new module
  there named like one they import (`socket.py` at the root, for the probes) would shadow it without touching an
  attested file. Hypothetical today.
- I-4 The runner mints (rc 0) a result whose declared input is absent, which the validator then refuses (section 4).
- I-5 The landing's `export PYTHONDONTWRITEBYTECODE=1` does not reach the legs (`_clean_env` passes PATH, HOME, LANG);
  S0-01's and S0-02's legs write `__pycache__` into `proofs/S0-01/` and `proofs/S0-02/oracle/`. Excluded from every
  attestation and ignored by git: harmless.
- I-6 Contract item 2's literal "a proof with no declaration gets exactly today's key set" does not hold for S0-08 (29 to
  30, the nested fixture): the coordinator's round-2 request (AF-AP-228), wanted, but not written into the frozen contract
  or the plan. S0-01, S0-04, S0-07, S0-11 are exact (section 1).
- I-7 After the landing, an edit to any declared input invalidates its declarers: `upstream.lock.yaml` (S0-06, S0-12),
  `SBOM.yaml` (S0-12), either ADR (S0-09, S0-10), `fixtures/s0-06/neg-unauthorized-tuple.json` (S0-06), S0-01's modules
  and `identities.json` (S0-02, S0-03, S0-05 as well as S0-01). A routine pin bump in the lock file will need a re-mint
  and an owner re-sign of two proofs. By design; worth saying where lanes will read it (FU-1).
- I-8 S0-07's recorded stdout (hence its normalized digest) depends on the checkout path (the builder's A3): reproduced,
  the clone's S0-07 runs differ from the worktree's while the attestation is equal.
- I-9 S0-11 reads its own previous `result.json` while it grades (the builder's A2): confirmed by strace.
- I-10 The landing's `git tag -d accepted/S0-NN` deletes the owner's twelve local signed refs in the sandbox tree; needed for
  `check-proof-status.py` there (a ref beside a PENDING line is an error). The objects stay recoverable from the committed
  tag files in history.
- I-11 Proof directories: a checker that rejects an unexpected (empty) directory (`check_acp_conformance.py:1776`) depends
  on a state the file-only attestation cannot see. Pre-existing; git cannot carry an empty directory, so CI is unaffected.
- I-12 The builder's deviation X1 holds with no material effect: an absent declared path passes the registry check
  (rc 0 in a root where the proof has no result) and is refused by name wherever it could bind a verdict (every proof
  in the real tree has a result). No false PRESENT can come from it; a BLOCKED proof carries no attestation at all.

## 10. What I reproduced, what I reviewed statically, what I skipped

Reproduced (run here): the premise; the PIN baseline and issue #59 F-1 as filed; the patch hashes; the key-set diff; the landing
steps 1-6 in a worktree and in a tag-free clone; the one-byte, delete and symlink demonstrations; an independent
strace enumeration of every leg's reads, stats, listings, writes and children; hostile declarations through the CLI;
the guard over ten planted shapes; 27 mutants (20 of the builder's, 7 mine) with live differentials of the survivors;
the red state of the new file on the PIN; the floor plus the new file plus the derived extra set in the landed clone; a
CI emulation (uid 65534, Python 3.12, CI's pip set, no tags, S0-07's path hidden) of the 4-file set, the lint steps,
`ledger-gen`, `integrity`, `stage1-gate`, and `verify-planning-repo.sh`.
Reviewed statically: the patch line by line; the checkers' stat and listing sites (grep); the CI workflow; the
harness suites' references.
Skipped, deliberately: the whole `tests/` (5766 tests; every file naming a touched symbol ran); the harness suites (no
attested path named); `tests/test_vendored_manifest.py` (forbidden); the PC; real CI; the combined batch with #313 and
#314 (not in this patch); the builder's report tooling (`report_lint`, `ap_screen`: unchanged machinery).

## 11. Gate recommendation

**MERGE-READY-WITH-FOLLOWUPS** against the contract as frozen (items 1-5): no finding meets the whole blocking predicate
there. **Plus one CONTRACT-DEFECT, F-1, returned for the coordinator's ruling.** Recommended: amend item 3 to "every repo
file its checker reads or tests for existence" and take the one-line S0-12 declaration before the batch landing. Under
that amendment F-1 meets every condition (contract-mapped, canonical path, material, red test, in boundary) and the
recommendation becomes NOT-READY until the declaration lands. Nothing in this recommendation rests on a claim I did
not reproduce, except real CI (emulated) and the whole `tests/` suite (the affected files ran).

## 12. Cleanup and boundary (06:5xZ)

`git worktree remove --force /tmp/v59a/wt` (after section 6); the tag-free clone, the Python 3.12 venv and every
`/tmp/v59a` path removed; `git worktree list` shows only the main tree and `git worktree prune --dry-run` prints nothing.
Shared tree: no `proofs/*/result.json`, ledger, tag object or tag ref written (`git diff HEAD -- proofs/
docs/governance/` empty; under `scripts/` and `tests/` the only changes are SYNTH1's `scripts/s1_synth.py` and
`tests/test_s1_synth.py`, another lane's files I never opened; twelve `refs/tags/accepted/*` still present); the only
file of mine is this report. Scratch
kept (552 KB) under `scratchpad/verify-i59a/`: the harnesses named above, `redtest/` (the F-1 red test and the fixed
registry), the parsed strace summaries (`st/S0-NN/parsed.json`) and the re-minted artifacts' copies (`reminted/`).
No subagent, no PC bridge, no outward-facing action; the network reads were `git ls-remote --tags origin
'refs/tags/accepted/*'` (empty) and a pip download of CI's five test dependencies into the scratch venv.

## 13. Round 2 (2026-09-26 07:1xZ): the builder's round-3 delta, against the amended contract

The coordinator's ruling amends contract item 3: a repo file whose existence or type a checker tests while it grades is
an input, so F-1 was blocking; the builder's round 3 (`tasks/briefs/i59/I59-A-report.md` section 16) answers it and
FU-1, FU-2, FU-3, FU-5. Written incrementally from here.

Premise, re-measured at 07:1xZ:
- HEAD c15a46e; origin 626fc4c; `git diff --stat origin HEAD -- scripts/ proofs/ tests/` empty (HEAD's code = origin's).
- `git diff --stat 2a50a65 626fc4c` over every attested area (`proofs/`, the validator, the runner, `ledger-gen`,
  `check-proof-status.py`, the two test files, `docs/adr`, `SBOM.yaml`, `upstream.lock.yaml`, the two root files,
  `fixtures/`): empty. Round 1's PIN baseline (issue #59 F-1 as filed, section 1) still describes this base.
- `tasks/briefs/i59/I59-A.patch`: sha256 prefix `988261b5dc447fce`, five diffs (the four of round 2 plus
  `proofs/schemas/result.schema.json`), `git apply --check -v` rc 0 on HEAD. The round-2 patch (`8e83b983e966ce2b`) is
  read back from 6af9f03 for the delta.
- My round-1 report is committed (096e564); this section appends to it.
Verdict: premise HOLDS.

### 13.1 The delta (07:4xZ)

A tag-free clone at 626fc4c (`/tmp/v59b/clone`, the round-1 recipe) with the round-3 patch applied; sha256 prefixes
`e392a7f46661963c` registry.yaml, `4252d5e1569a23ea` result.schema.json, `f1eb20ff26c87939` validate-ledger,
`dae0cd1c8a4c2798` test_validate_ledger.py, `c70c7a50981844a2` test_attested_inputs.py. Against the round-2 files
(the round-2 patch applied to the same base): `test_validate_ledger.py` unchanged; the registry changes S0-12's list
only; the validator changes in three places only (the long-segment refusal in `_extra_inputs`, the `OSError` guard in
`_is_regular_file`, `os.path.lexists` in the registry-level presence test, plus `import os`); the test file gains the
second instrument, the new tests and the docstring (232 changed lines).

### 13.2 Attack 1: does the stat instrument catch the class? (`scratchpad/verify-i59a/planted_stats.py`)

Fifteen existence and type tests of my own, each planted in the builder's scratch S0-09 copy and judged by its round-3
`_observe` + `_verdict`, pasted:
```
isdir_on_a_file  target=docs/v_a.md       RED names-target=True   (os.path.isdir on a FILE: a type test)
os_access        target=docs/v_b.md       RED names-target=True
path_is_file     target=docs/v_c.md       RED names-target=True
islink_lstat     target=docs/v_d.md       RED names-target=True
lexists          target=docs/v_e.md       RED names-target=True
getsize          target=docs/v_f.md       RED names-target=True
samefile         target=docs/v_g.md       RED names-target=True
shutil_which     target=docs/v_h.md       RED names-target=True
isdir_on_a_dir   target=docs/vdir         GREEN (not caught)      named: a test of a DIRECTORY
absent_file      target=docs/v_absent.md  GREEN (not caught)      named: a file's ABSENCE
posix_stat       target=docs/v_k.md       GREEN (not caught)      named: a stat below the os module
find_spec        target=lib/v_mod.py      GREEN (not caught)      named: the import system's own posix.stat
scandir_is_file  target=docs/v_m.md       GREEN (not caught)      named: a directory listing
stat_dir_fd      target=docs/v_i.md       GREEN (not caught)      NOT named: the wrapper skips calls with dir_fd
readlink_type    target=docs/v_l.md       GREEN (not caught)      NOT named: os.readlink is not wrapped
```
Every file test through `os.stat`, `os.lstat` or `os.access` reds with exactly its target: the class the amended item 3
names is caught for Python-level code. The five named blind spots behave as the docstring says. Two minor ones are not
named (INFO I-14).

Does a CURRENT verdict depend on a blind spot? No. The round-3 strace run (13.3) sees, outside each proof's directory, no
absence probe but S0-02's own bytecode-cache miss and no directory test or listing but the import machinery's
(`proofs/S0-01`, `proofs/S0-01/tools`, `proofs/S0-01/__pycache__` for S0-02 and S0-03, whose files there are declared).
A grep over every checker finds `dir_fd` nowhere, `os.readlink` only on `/proc` (S0-11), and every
`iterdir`/`glob`/`listdir`/`rglob` on the proof's own evidence directories, whose files the directory walk attests.

### 13.3 Attack 2: the strace enumeration re-run on round 3 (`st_mint.sh`, `st_parse.py`, `st_compare.py`)

All twelve re-minted through `scripts/proof-runner run` under `strace -f -ff -y` with `newfstatat`, `stat`, `lstat`,
`statx`, `access`, `faccessat`, `faccessat2` and `readlink` traced beside the opens; every leg rc 0. Per proof, the regular
repo files its legs OPEN or STAT outside its directory, the closure, the schemas and `__pycache__`, against its
`extra_attested_inputs`, pasted:
```
S0-01 MATCH declared=0   S0-02 MATCH declared=6   S0-03 MATCH declared=5   S0-04 MATCH declared=0
S0-05 MATCH declared=1   S0-06 MATCH declared=2   S0-07 MATCH declared=0   S0-08 MATCH declared=0
S0-09 MATCH declared=1   S0-10 MATCH declared=1   S0-11 MATCH declared=0
S0-12 MATCH declared=4 opened=['SBOM.yaml', 'upstream.lock.yaml'] stat-only=['LICENSE-DECISION.md', 'THIRD-PARTY-NOTICES.md']
ALL MATCH
```
The declared set now matches my instrument exactly, stat-only files included, for all twelve. The builder's claim ("those
two were the only undeclared outside stats") holds.

### 13.4 Attack 3: FU-2 through the validator CLI and the canonical runner (`fu2.py`)

Each case: S0-04 minted by the runner in a minimal root, the path declared, a re-mint, then `integrity` (pasted):
```
long-segment           uid=0      re-mint rc=0 result-kept=True  integrity rc=1 stderr=EMPTY  S0-04 PRESENT + "has a segment over 255 bytes"
long-segment-multibyte uid=0      re-mint rc=0 result-kept=True  integrity rc=1 stderr=EMPTY  S0-04 PRESENT + "has a segment over 255 bytes"
over-path-max          uid=0      re-mint rc=0 result-kept=True  integrity rc=1 stderr=EMPTY  S0-04 INVALID + "is not a regular file"
nul-byte               uid=0      re-mint rc=0 result-kept=True  integrity rc=1 stderr=EMPTY  S0-04 INVALID + "is not a regular file"
eacces-dir             uid=65534  re-mint rc=0 result-kept=True  integrity rc=1 stderr=EMPTY  S0-04 INVALID + "is not a regular file"
unreadable-file        uid=65534  re-mint rc=1 result-kept=False (PermissionError)   integrity: S0-04 ABSENT
```
The three changes hold: a long segment (by bytes: 128 two-byte characters are refused too) is refused by name before any
filesystem call; an `OSError` in `_is_regular_file` (ENAMETOOLONG as root, EACCES on a parent as uid 65534) reads as not
regular; `os.path.lexists` keeps the registry check from crashing on a path over PATH_MAX. In none of those cases does a
re-mint delete the result. The last row is a different trigger, outside FU-2: a declared file that is itself unreadable
(mode 000, non-root) passes `_is_regular_file` and fails at `read_bytes()`, so the runner still deletes the result, and
the validator exits with a `PermissionError` traceback. The same happens today for an unreadable file inside a proof's own
directory (measured: the same traceback), so it is pre-existing, not a regression (INFO I-13).

### 13.5 Attack 4: the schema edit

Parsed old (round 2 = the base) and new `proofs/schemas/result.schema.json`: identical once
`properties.attestation.description` is removed from both; the description differs; `Draft202012Validator.check_schema`
passes; 67 lines each, trailing newline kept. Only the description changed. Its new text lists the closure, the schemas,
the directory minus the own artifacts and `__pycache__`, and the declared inputs, which matches the code. One overclaim:
it opens "Binds this artifact to every input that produced or checks it" and ends "so ... a changed input ... no longer
validates". S0-07's Fubuki checkout (8 modules executed, FU-6) is such an input, and a change to it still validates (FU-7).

### 13.6 Attack 5: the landing on round 3 (tag-free clone)

- Step 1, the section 5 re-mint verbatim: no `FAILED`; attested counts S0-01 247, S0-02 214, S0-03 96, S0-04 44, S0-05 63,
  S0-06 168, S0-07 14, S0-08 30, S0-09 12, S0-10 12, S0-11 13, S0-12 18 (its outside keys: `LICENSE-DECISION.md`,
  `SBOM.yaml`, `THIRD-PARTY-NOTICES.md`, `upstream.lock.yaml`).
- Step 2: integrity rc 0, 12 PRESENT; `ledger-gen` twice, `cmp` rc 0; `integrity --ledger` rc 0; `stage1-gate` rc 0.
- S0-12's part (`integrity --ledger`, each restored to 12 PRESENT): `LICENSE-DECISION.md` removed: `S0-12 INVALID`,
  `attestation-mismatch: S0-12 LICENSE-DECISION.md`, `... LICENSE-DECISION.md is not a regular file`, and the leg exits 1
  (`sbom-missing-file`); the same for `THIRD-PARTY-NOTICES.md`. One byte of `LICENSE-DECISION.md`: `S0-12 INVALID` (its
  content is bound too, stricter than the checker, which reads none of it). Replaced by a directory: `S0-12 INVALID`
  while the checker still passes (`exists()` is true for a directory): fail-closed.
- The pins.py demonstration: one byte turns S0-01, S0-02, S0-03, S0-05 INVALID (`attestation-mismatch: S0-0N
  proofs/S0-01/pins.py`), `S0-09 PRESENT`, 8 PRESENT; one byte of the S0-08 nested fixture turns S0-08 INVALID.
- Steps 3-5: `check-proof-status.py .` rc 0, exactly twelve `proof-status: WARNING S0-NN: ACCEPTED with the anchor PENDING
  ...` lines.
- Step 6, `bash scripts/test_summary.sh --basetemp=<short>` in the landed clone (pasted):
```
4 files set=379203742124  run 1: pytest-exit: 0  pytest-summary: 190 passed in 46.22s
                          run 2: pytest-exit: 0  pytest-summary: 190 passed in 48.59s
1 files set=96d60da64331  run 1: pytest-summary: 78 passed in 32.68s    run 2: pytest-summary: 78 passed in 32.14s
6 files set=63923f3a5a15  pytest-exit: 0  pytest-summary: 444 passed in 70.95s (0:01:10)
4 files set=f5fcca671f19  pytest-exit: 0  pytest-summary: 971 passed in 422.71s (0:07:02)
5 files set=f63a056b995b  pytest-exit: 0  pytest-summary: 415 passed in 80.14s (0:01:20)
```
  The floor's thirteen files plus the new one: 190 + 444 + 971, all green in the landed state; the derived extras green.
- CI emulation (uid 65534, a Python 3.12.3 venv with the `tests` job's pip set, `S0_01_VENUE=ci`, no tags, the Fubuki path
  hidden in a private mount namespace): the 4-file set `pytest-exit: 0`, `178 passed, 12 skipped in 51.39s`, the guard
  skipping exactly S0-07 and S0-11 with their reasons, the other ten graded under both instruments. The pyflakes steps
  rc 0; `ledger-gen` on 3.12 byte-identical to the landed ledger; `integrity --ledger` rc 0; `stage1-gate` rc 0;
  `verify-planning-repo.sh` rc 0. The separator grep prints 0 for the five changed files.

### 13.7 Attack 6: the new mutants (`scratchpad/verify-i59a/mutate_r3.py`, AF-AP-223 rules as round 1)

The builder's ten round-3 mutants and its two re-run guard mutants, reconstructed from its section 16 (its harness file
now holds only the last two), plus six of mine against the round-3 code; each file sha-checked after restore (equal
prefixes before and after: `f1eb20ff26c87939`, `c70c7a50981844a2`, `e392a7f46661963c`). Pasted:
```
CONTROL (unmutated, 18 named tests): rc=0 18 passed in 4.51s
KILLED  B-M-F1 S0-12 back to its round-2 list 3/3 · B-S1 stat instrument never installed 3/3 · B-S2 stat rule off 3/3
KILLED  B-S3 __pycache__ stat exemption removed 1/1 · B-L1 long-segment refusal removed 1/1 · B-L2 no OSError guard 1/1
KILLED  B-L3 registry presence test back to exists() or is_symlink() 1/1 · B-N1 closure refusal covers scripts/proof-runner only 2/2
KILLED  B-N2 own-directory refusal covers direct children only 1/1 · B-N5 verdict binding tests existence only 1/1
KILLED  B-G2 outside rule off (re-run) 3/3 · B-G5 inside rule off (re-run) 1/1
SURVIVED       V-S4 only os.stat wrapped (lstat, access unwatched): 0/4 named FAILED; 4 passed in 0.99s
KILLED         V-S6 stats filed as reads: 3/3 named FAILED; 3 failed in 0.70s
SURVIVED       V-L4 long-segment check counts characters, not bytes: 0/1 named FAILED; 1 passed in 0.21s
KILLED         V-L5 OSError guard narrowed to FileNotFoundError: 1/1 named FAILED; 1 failed in 0.12s
KILLED         V-L6 registry presence test follows symlinks (exists): 1/1 named FAILED; 1 failed in 0.21s
KILLED         V-M-F2 S0-12 drops THIRD-PARTY-NOTICES.md: 2/2 named FAILED; 2 failed in 0.71s
EXPECTED=18 KILLED=16 SURVIVED=2 INVALID=0
```
All twelve of the builder's are KILLED as FAILED tests, reproducing its `EXPECTED=10 KILLED=10` and `EXPECTED=2 KILLED=2`;
round 1's surviving N1, N2 and N5 are now killed. Live differentials of my two survivors:
- V-S4: with only `os.stat` wrapped, my `os_access`, `islink_lstat` and `lexists` plants go GREEN; the original reds all
  three. Non-equivalent: `PLANTED_STATS` holds three shapes, all through `os.stat` (FU-8).
- V-L4: a 128-character, 256-byte segment: the mutant loses the by-name refusal and the path falls to the `OSError` guard
  (`S0-04 INVALID`, `... is not a regular file`); the original refuses it by name (`S0-04 PRESENT` plus the finding).
  rc 1 and no crash in both; a missing multibyte case (FU-8).

### 13.8 The inventory after round 3 (07:4xZ)

- F-1 (CONTRACT-DEFECT, blocking under the amended item 3): FIXED and VERIFIED. S0-12 declares the two files; strace
  matches the declarations for all twelve proofs; removing either file turns the re-minted S0-12 INVALID on the real path;
  the guard reds the class (eight shapes) and the builder's version of my red test is committed in the new file
  (`test_removing_a_file_s0_12_tests_for_invalidates_its_minted_result[*]`, killed by B-M-F1 and V-M-F2).
- FU-1: the schema half DONE (description only, 13.5); the `.claude/skills/env-tool-quirks/SKILL.md:98` half still open
  (outside the builder's boundary). FU-2: DONE for its trigger class (13.4). FU-3: DONE (N1, N2, N5 killed). FU-5: DONE.
  FU-4 (CI `-rs`) and FU-6 (S0-07's checkout, task #320): open, as the coordinator scoped them.
- FU-7 (new) The schema description overclaims in an ATTESTED file: "Binds this artifact to every input that produced or
  checks it ... so ... a changed input ... no longer validates" is false for S0-07, whose checkout (8 executed modules) is
  unattested. Suggested: "Binds this artifact to the repo files that produced or check it: ..." and a closing sentence
  "Inputs outside the repository (S0-07's Fubuki checkout; the interpreter and its packages) are not attested (task #320)."
  Timing: before the landing, or the fix re-mints all twelve again. Prose, not behaviour, so not blocking.
- FU-8 (new) Test gaps from V-S4 and V-L4: add an `os.access` and an `os.lstat` (`os.path.lexists`/`islink`) shape to
  `PLANTED_STATS`, and a multibyte long segment to the refusal table.
- I-13 (new) An unreadable declared file (mode 000, non-root) crashes the validator (`PermissionError` traceback) and makes
  the runner delete the result: the same as an unreadable file in a proof's own directory today (measured). Pre-existing.
- I-14 (new) Two blind spots the docstring does not name: a stat with `dir_fd` (the wrapper skips it) and an `os.readlink`
  type test (not wrapped). No checker uses either on a repo path. One line each in the docstring would close the naming.
- I-7 (updated) After the landing, S0-12 also binds the CONTENT of `LICENSE-DECISION.md` and `THIRD-PARTY-NOTICES.md`
  (a one-byte edit turns it INVALID though its checker only tests existence): stricter than the verdict, fail-closed, and
  one more pair of files whose routine edits need a re-mint and a re-sign.
- I-15 (new) The `tests` job is red on the base itself (626fc4c: SYNTH1's skip guard on the non-root runner, per the
  coordinator's c15a46e; its fix rides SYNTH1 round 2). The landing's CI verdict needs that fix too; this change is not
  its cause (the CI emulation above is green on the attested-inputs set).
- Round 1's other INFO items (I-1 to I-6, I-8 to I-12) are unchanged by round 3.

### 13.9 Gate recommendation for the whole change (round 3, against the amended contract)

**MERGE-READY-WITH-FOLLOWUPS.** F-1 is fixed and reproduced fixed on the real path; no other finding meets the whole
blocking predicate (the new ones are test gaps, prose or pre-existing). Take FU-7 (the schema wording) in this batch if
at all: after the landing it costs another re-mint of all twelve. Not reproduced here: real CI (emulated) and the whole
`tests/` suite (every file naming a touched symbol ran green in the landed state).

### 13.10 Cleanup (07:4xZ)

The tag-free clone, the Python 3.12 venv, the uid 65534 scratch roots and every `/tmp/v59b` path removed (this round used
no linked worktree; `git worktree list` shows only the main tree, `git worktree prune --dry-run` prints nothing). Shared
tree: my only change is this report; nothing under `proofs/` or `docs/governance/` changed (`git diff HEAD` empty there),
twelve `refs/tags/accepted/*` present, no git write. The other dirty files are SYNTH1's (`scripts/s1_synth.py`,
`tests/test_s1_synth.py`, its report), untouched. Scratch kept (944 KB) under `scratchpad/verify-i59a/`: this round's
harnesses (`planted_stats.py`, `st_compare.py`, `fu2.py`, `mutate_r3.py`), the parsed strace summaries (`st3/S0-NN/parsed.json`)
and both patches (`r2.patch`, `r3.patch`). No subagent, no PC bridge, no outward-facing action; one pip download of CI's
five test dependencies into the (removed) scratch venv.
