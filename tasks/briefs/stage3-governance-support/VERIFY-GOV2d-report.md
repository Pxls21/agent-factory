# VERIFY-GOV2d — independent adversarial verification

Outcome: NOT-READY recommendation. The production default trust root and all FD regular-file checks survived adversarial tests. One frozen explicit-`gpg=` requirement fails: an absolute symlink to a regular file passes `gpg_path.is_file()` at `RV:137`, runs its target, and is not refused before process execution.

- Role: `adversarial-verifier`. Route: `agentfactory-verify-local`; it is HYBRID in practice because a cloud step can serve after a local chat-template refusal. This report makes no claim about the producing model.
- PIN: `d116cbc1c6d289b217edf999bdd846a97a3aa795`, committed `2026-09-22T14:02:26Z`.
- Venue: PC lane. `gpg (GnuPG) 2.4.7` measured. All GnuPG work used fresh throwaway ed25519 keyrings in lane scratch. No production service, worktree production byte, private key, commit, push, or host configuration was changed.
- Contract: `tasks/briefs/pc/pc-gov2d.md`, VERIFY-GOV2c-B F1/F2. GR (`tasks/briefs/stage3-governance-support/GOV2d-report.md`) was treated as a claim, never an oracle.

## 1. Premise

```
HEAD=d116cbc1c6d289b217edf999bdd846a97a3aa795 committed=2026-09-22T14:02:26Z
RV 06da43e1024e548b / 211 lines / d116cbc
TR 1ec52c579c7b4558 / 476 lines / d116cbc
RM 20be44677047f037 / 74 lines / d116cbc
PK 5d8cf21468adb55e / 156 lines / 756d516
GR bcf94e032571c4e2 / 231 lines / d116cbc
FUBUKI_OS_ROOT=/home/rocco/fubuki-pin/fubuki-os
FUBUKI_OTHER_ROOT=/home/rocco/fubuki-pin/fubuki-os-other
```

Every frozen hash, line count, and named RV/TR/PK anchor matched. `shutil` and `which` have no RV code occurrence. The bare word `environment` occurs in three comments (`RV:49`, `RV:114`, `RV:164`); GR's actual invariant, `shutil\|os.environ`, is zero and holds.

## 2. Trust root and child environment

Production reaches `verify_review` once at `PK:155`; it supplies neither `gpg=` nor caller PATH. The default path choice is fixed at `RV:143-145`, and the subprocess environment is the literal at `RV:168`.

Fresh real-`verify_review` probes:

```
valid fresh owner signature, caller PATH=''                    NONE; 0.014s
hostile first-PATH fake gpg + 8-byte unsigned signature        fubuki-review-signature-invalid; 0.013s
  hostile fake sentinel                                         False
hostile first-PATH fake gpg + valid owner signature             NONE; 0.014s
explicit gpg bare name / relative-existing / directory / missing fubuki-review-gpg-unavailable; each 0.0s
explicit gpg absolute regular scratch double                    fubuki-owner-key-invalid; 0.002s; sentinel=True
explicit gpg absolute symlink -> regular scratch double         fubuki-owner-key-invalid; 0.002s; sentinel=True
```

The first three results prove the claimed production default: empty caller PATH cannot affect `/usr/bin/gpg`; the shaped hostile `GOODSIG`/`VALIDSIG` script neither ran nor authorized an unsigned record; a valid signature still accepts under hostile caller PATH.

The final symlink row is the blocker in Finding 1. `Path.is_file()` at `RV:137` dereferences symlinks. It therefore accepts an absolute symlink and invokes its target. The target sentinel proves execution happened before the returned `fubuki-owner-key-invalid`. The frozen contract requires refusal as `fubuki-review-gpg-unavailable` before any process starts.

`strace` is unavailable. Under the exact `RV:168` environment (`env -i GNUPGHOME=<scratch> PATH=/usr/bin:/bin LC_ALL=C`), GnuPG debug output shows `/usr/bin/gpg-agent` starts for public-key import and the subsequent verification emits real `GOODSIG` and `VALIDSIG`. It shows no dirmngr, pinentry, shell, or executable outside `/usr/bin:/bin`. This is a bounded GnuPG self-report, not an exhaustive kernel exec census.

The `/usr/bin/gpg`-absent branch was not host-tested: doing so would change host paths. Its fail-closed `_GPG_PATHS` selection is visible at `RV:143-145`; mutation m5 below gives its concrete discriminator.

## 3. Regular-file proof on the FD

The reader uses `O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC` at `RV:63`, proves `os.fstat(fd)` at `RV:65`, and rejects non-regular modes with `stat.S_ISREG(st.st_mode)` at `RV:66-67`. The explicit `_read_regular_file(record_path)`, signature, and owner-key calls at `RV:152-154` put all three review inputs through that primitive.

Actual t0 classification:

```
record FIFO at pathname precheck      fubuki-packet-unreviewed; 0.0s
signature FIFO at pathname precheck   fubuki-packet-unreviewed; 0.0s
owner-key FIFO at pathname precheck   fubuki-owner-key-missing; 0.0s
```

For record, signature, and owner key, a test-only `Path.is_file` override returned true at t0 then replaced that target with a FIFO before RV's real open. Each FIFO had a live non-blocking writer holding 31 attacker bytes. Each ran under a 10-second SIGALRM and returned in 0.0 seconds:

```
fubuki-review-record-invalid: review record is not a regular file
race armed=True; os.read on the opened t1 FIFO=[]
```

I separately tracked reads of preceding regular inputs, so those cannot be mistaken for a read from the t1 FIFO FD. Every target also returned the same exact S_ISREG detail in 0.0 seconds for a no-writer FIFO, directory, and `/dev/zero` injected only at the open call. The `/dev/zero` result identifies the S_ISREG branch rather than `_MAX_RECORD_BYTES` at `RV:75`.

Additional shapes:

- Post-t0 symlink to regular file and symlink to FIFO: `fubuki-review-record-invalid: [Errno 40] Too many levels of symbolic links ...`; `O_NOFOLLOW` refuses before an FD exists.
- Live UNIX socket (short `/tmp` scratch root because the lane path exceeds AF_UNIX `sun_path`): record/signature give `fubuki-packet-unreviewed`; owner key gives `fubuki-owner-key-missing`.
- Regular hard-linked signed record: accepted (`NONE`, 0.014s), as intended because the opened FD is regular.

Result: SOLID. The t1 guard refuses every tested non-regular input without a hang or attacker-FIFO read.

## 4. Alarm guards and PC gpg-agent census

Declared Fubuki inputs were exported for every test run.

```
review suite -n 4, run 1   24 passed in 7.41s; rc=0
review suite -n 4, run 2   24 passed in 8.83s; rc=0
review suite serial         24 passed in 1.70s; rc=0
review suite serial census  24 passed in 1.81s; rc=0
```

`TR:316` installs the SIGALRM handler in the test body. Both xdist runs and the serial run completed without a non-main-thread `ValueError`. They are not timing-only greens: m3 below returns the deterministic 10-second `hung` discriminator.

Census delta:

```
before suite              live=8 defunct=0 total=8
after suite               live=8 defunct=0 total=8
after ten verify_review   live=8 defunct=0 total=8
```

All ten direct real `verify_review` calls accepted. The sandbox's reported `0 -> 25 [gpg-agent] <defunct>` versus this PC delta cannot be explained causally from this lane. PID-1/reaping is only an inference.

A read-only scratch copy adding `--no-autostart` to both GnuPG base invocations accepted on gpg 2.4.7 (`rc=0`, `scratch no-autostart verifier accepted`). It is follow-up data only: it does not prove sandbox 2.4.4 behavior, portability, or a cleanup requirement.

## 5. Mutation audit

Every mutant was a scratch package copy. Each `review.py` compiled and `pytest --collect-only` collected 24 tests before its selected execution. The first mutation-rig attempt allowed pytest to put the worktree test directory before PYTHONPATH, so it could import the non-mutant module. I rejected that output, copied the test/lock/fixtures into each scratch root, and reran every row below. These are the isolated rerun results.

```
m1 restore shutil.which("gpg")
  test_gpg_is_never_resolved_from_the_callers_path
  1 failed, 23 deselected; DID NOT RAISE GovernanceError — KILLED
m2 forward caller PATH
  test_the_child_path_is_fixed
  1 failed, 23 deselected; hostile PATH != /usr/bin:/bin — KILLED
m3 drop O_NONBLOCK
  two FIFO race tests
  2 failed, 22 deselected in 20.32s; detail=hung — KILLED
m4 drop S_ISREG
  two FIFO race tests
  2 failed, 22 deselected; signature-invalid replaces record-invalid — KILLED
m5 _GPG_PATHS=("gpg",)
  hostile-PATH test
  1 failed, 23 deselected; gpg-unavailable replaces signature-invalid — KILLED
m6 drop is_absolute()
  explicit-gpg test
  1 failed, 23 deselected; existing relative gpg DID NOT RAISE — KILLED
m7 drop O_NOFOLLOW
  symlinked-record test
  1 failed, 23 deselected; DID NOT RAISE — KILLED
m8 fstat(fd) -> stat(path)
  AF-AP-80 source pin
  1 failed, 23 deselected; `assert "os.fstat(fd)" in src` at TR:475 — KILLED (source shape only)
v1 swap tuple order to (/usr/bin/gpg2, /usr/bin/gpg)
  valid signed review: 1 passed, 23 deselected — SURVIVED / equivalent here
v2 remove explicit-gpg is_file() half
  new directory-no-subprocess control: clean 1 passed; mutant 1 failed (directory reached subprocess) — KILLED
v3 drop O_CLOEXEC
  normal fake-gpg FD census has no review-input FD in clean or mutant — SURVIVED / declared limit
v4 change S_ISREG refusal detail
  two FIFO race tests: 2 failed, 22 deselected; detail mismatch — KILLED
```

v1 is equivalent on this PC: `/usr/bin/gpg` is a regular executable; `/usr/bin/gpg2` is a symlink resolving to `/usr/bin/gpg`, and both have inode 9640.

v3 is a real limit, not a false kill. A scratch hook recorded `FD_CLOEXEC=True` at close in clean and in the source mutation that deletes the explicit flag. This Python/OS sets it by default (PEP 446), and Python subprocess defaults close non-stdio FDs. The source still names `O_CLOEXEC` at `RV:63`, but no independent behavioral discriminator was found on this venue. The frozen contract does not require the static flag.

`TR:423` and `TR:453` each use `assert excinfo.value.detail == "review record is not a regular file"`; those S_ISREG-detail assertions pin the v4 mutation.

## 6. Builder-report evidence and screens

The builder report lint reproduced at its parent revision and at the PIN:

```
report_lint at 2da04bf: 27 refs — OK 27, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0; rc=0
report_lint at d116cbc: 27 refs — OK 27, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0; rc=0
```

Two of GR's seven red-first claims were independently rerun against a scratch module made from `git show 2da04bf:src/agent_factory/governance/review.py`; the import path was outside the worktree:

```
current PIN against fresh controls: 2 passed in 0.09s
parent scratch control 1: expected signature-invalid DID NOT RAISE
parent scratch control 2: 10-second alarm -> fubuki-review-record-invalid: hung
parent result: 2 failed in 10.20s
```

The first failed assertion was `Failed: DID NOT RAISE GovernanceError`; the second failed the expected detail check because actual detail was `hung`. These reproduce the stated pre-fix security defects, then pass at the PIN.

Screens:

```
RV: AP-32 x2 (hash validation), AF-AP-110 x1 (`env = {"GNUPGHOME": home, "PATH": "/usr/bin:/bin", "LC_ALL": "C"}` at RV:168)
TR: AF-AP-80 x2 (`assert "os.fstat(fd)" in src` at TR:475-476)
RM: AP-32 x1 (`governance_hash` owner-step example at RM:48)
```

All hits are classified as intended. `python3 -m pyflakes RV TR` could not run: `/usr/bin/python3: No module named pyflakes`; this is a venue/tooling discrepancy, not a code pass. GitNexus `detect-changes` said `No changes detected` against its clone index. The worktree was confirmed clean at close and `git diff --check` returned zero output.

## 7. Finding inventory

1. BLOCKER — explicit absolute symlink gpg is executed.
   - Evidence: VERIFIED, direct production-component call to current-PIN `verify_review`.
   - Contract mapping: frozen item 2(d) explicitly requires an absolute symlink to a regular file to refuse as `fubuki-review-gpg-unavailable` before any process runs.
   - Canonical path: YES for real `verify_review` and its explicit test-only executable interface; production `load_packet` does not use this kwarg (`verify_review(packet_hash, reviews_dir=reviews_dir, owner_key=owner_key)` at PK:155).
   - Material effect: YES. The claimed executable-boundary validation accepts a filesystem indirection and starts its target. The target sentinel proves execution.
   - Concrete discriminator: scratch absolute symlink target sentinel `True`; actual result `fubuki-owner-key-invalid` rather than pre-exec `fubuki-review-gpg-unavailable`.
   - Task ownership: YES, `if not gpg_path.is_absolute() or not gpg_path.is_file():` at RV:137-139 and its test boundary.
   - Suggested fix: reject `gpg_path.is_symlink()` before `is_file()`, then add the actual symlink target/sentinel regression. Do not rely on the regular-file reader; it is not used for executable selection.

2. FOLLOW-UP — RM over-generalizes the t0 reason for the owner-key path.
   - Evidence: VERIFIED.
   - Contract mapping: none that requires the owner-key reason to be packet-unreviewed.
   - Canonical path: YES; actual owner-key FIFO is rejected by `if not owner_key.is_file():` at RV:131-132.
   - Material effect: no fail-open behavior; the code remains fail-closed as `fubuki-owner-key-missing`.
   - Reproduction: owner-key FIFO at t0 -> `fubuki-owner-key-missing`; RM says generic non-regular names are `fubuki-packet-unreviewed` at `RM:28-32`.
   - Suggested fix: clarify RM's sentence to distinguish record/signature from owner key in a later bounded documentation update.

3. FOLLOW-UP — explicit `O_CLOEXEC` has no independent behavioral kill on this Python venue.
   - Evidence: VERIFIED venue limitation.
   - Contract mapping: none; the frozen contract does not require the static flag.
   - Canonical path: normal fake-gpg child census and direct source-open probe.
   - Material effect: not observed; Python's default non-inheritable descriptors and `close_fds=True` close the tested class even when the source token is deleted.
   - Reproduction: v3 audit in section 5.
   - Suggested fix: retain the explicit flag for defense-in-depth; add a deterministic portability test only if a supported non-PEP-446 environment enters scope.

4. FOLLOW-UP — `--no-autostart` works on PC gpg 2.4.7; sandbox-agent cleanup remains unproven.
   - Evidence: VERIFIED on this PC; UNSURE across venues.
   - Contract mapping: none in GOV2d.
   - Canonical path: scratch copy only, intentionally outside production bytes.
   - Material effect: no PC defunct delta; no basis for a cleanup change.
   - Suggested fix: track under D-034/GOV2e with the original sandbox 2.4.4 venue.

5. INFO — `gpg2`-first tuple mutation is equivalent on this PC.
   - Evidence: VERIFIED (`gpg2` resolves to gpg; identical inode).
   - Contract mapping: none.
   - Suggested fix: none.

6. INFO — `strace` and pyflakes are unavailable in this lane environment.
   - Evidence: VERIFIED command absence/module error.
   - Contract mapping: none.
   - Suggested fix: provision only if the coordinator requires exhaustive child-exec or pyflakes evidence.

## 8. Gate recommendation

GATE RECOMMENDATION: NOT-READY — Finding 1 satisfies the complete blocking predicate. It maps to an explicit frozen criterion, reproduces in the real current-PIN verifier with a concrete sentinel discriminator, materially executes a symlink target rather than refusing pre-exec, and belongs to RV/TR within GOV2d.

This is a recommendation, not a final gate verdict. The coordinator owns the gate and any one-focused repair. The repair must include a committed failing regression that creates an absolute symlink to a sentinel double, proves zero invocation, and asserts the exact unavailable reason.

## 9. Deliberately skipped / not done

- No host mutation to make `/usr/bin/gpg` absent; branch assessed by source plus m5 only.
- No `strace` (not installed) and no exhaustive kernel exec trace.
- No generated repair, production source/test/doc edit, commit, push, or ledger edit. The only worktree write is this required verifier report.
- No conclusion about the sandbox 2.4.4 gpg-agent defunct behavior.
- No final acceptance verdict.

## 10. Discrepancies and retro

- Initial mutation execution was invalid because pytest imported the worktree module; all such output was discarded and every mutant reran from isolated scratch roots. This is a verification-rig defect, not a change defect.
- The `pyflakes` module is absent from the lane Python.
- An intermediate draft line was content-safeguard transformed to `defensive *** only`; the final report restores the intended phrase, `defensive verification only`. No source or test artifact was affected.
- Report-lint final pass is `27 refs — OK 27, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`; the required 12-reference floor is met.
- Retro: nothing to bake beyond the coordinator's existing repair discipline. The concrete lesson for GOV2e is already represented by Finding 1: `Path.is_file()` follows symlinks and cannot prove the executable pathname itself is regular.

FILE IDENTITY:

```
PIN RV 06da43e1024e548b  TR 1ec52c579c7b4558  RM 20be44677047f037  PK 5d8cf21468adb55e
PC close timestamp 2026-09-22T15:30:35Z
```
