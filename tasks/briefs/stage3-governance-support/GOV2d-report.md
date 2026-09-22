# GOV2d report — focused repair of VERIFY-GOV2c F1/F2

PROPOSAL: this is a build-lane result. The sandbox-side adversarial-verifier must grade it; this lane does not issue a gate verdict.

- F1: gpg is a fixed code trust decision, never resolved from the caller's PATH.
- F2: every review input is proved regular on the returned FD; a FIFO planted after the pathname pre-check is refused, never allowed to hang.

PIN `2da04bf`; lane `pc-gov2d.md--2da04bf`; PC venue; gpg 2.4.7; venv Python 3.11.14. Route: `agentfactory-build-local`; the route is HYBRID in practice because a cloud step may serve a turn after a local chat-template refusal. No claim is made about which model produced code.

## PREMISE — RE-MEASURED

Measured on the unmodified lane tree before the edit:

```
RV 010054c04f697c8c  src/agent_factory/governance/review.py
TR ea9e0a466a4807d2  tests/test_governance_review.py
RM 662fd187a827461b  docs/governance/reviews/README.md
PK 5d8cf21468adb55e  src/agent_factory/governance/packet.py
git log --oneline dab9803..2da04bf -- <RV TR RM PK> | wc -l  => 0
```

The PIN anchors reproduced:

- `def _read_no_symlink(path: Path) -> bytes:` at `RV@2da04bf:51`.
- `fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)` at `RV@2da04bf:53`.
- `if not record_path.is_file() or not sig_path.is_file():` at `RV@2da04bf:109`.
- `gpg = shutil.which("gpg")` at `RV@2da04bf:114`.
- `gpg is not on PATH` at `RV@2da04bf:116`.
- `record_bytes = _read_no_symlink(record_path)` at `RV@2da04bf:122`; `sig_bytes = _read_no_symlink(sig_path)` at `RV@2da04bf:123`; `owner_key_bytes = _read_no_symlink(owner_key)` at `RV@2da04bf:124`.
- `fubuki-review-record-invalid` maps the read OSError at `RV@2da04bf:126`.
- `os.environ.get("PATH", "/usr/bin:/bin")` forwards the caller PATH at `RV@2da04bf:136`.
- The old docstring's false F5 claim is `environment, so an ambient gpg.conf or a PATH-shadowed gpg is not a trust channel (F5).` at `RV@2da04bf:22-23`.
- GOODSIG/VALIDSIG + rc-0 acceptance spans `RV@2da04bf:156-164`.
- The old absent-gpg test uses `monkeypatch.setattr(shutil, "which", lambda name: None)` at `TR@2da04bf:264`.
- The sole production call passes no gpg argument: `verify_review(packet_hash, reviews_dir=reviews_dir, owner_key=owner_key)` at `PK@2da04bf:155`.

Code-intel: graft found `_read_no_symlink` called only by `verify_review`; ripwire independently found `load_packet` plus the test file as callers of `verify_review`. `PK@2da04bf:155` is the production call site. GitNexus against the clone index reported `Target 'verify_review' not found` / `risk: UNKNOWN`; this is disclosed, not treated as low risk. `scripts/why.sh` showed the prior GOV2b/GOV2c chronology and the false F5 rationale that this repair closes.

PIN test baselines, with both declared FUBUKI roots exported and verified to exist:

```
tests/test_governance_review.py                         16 passed in 0.68s  rc=0
the exact six-file governance set                      49 passed in 0.92s  rc=0
```

The six-file set id under the brief's stated Python formula, `sha256("\n".join(sorted(files)) + "\n")[:12]`, is `f3baa8cf79c7`.

PREMISE HOLDS. Not CONTRACT-INVALID.

## RED-first evidence at the PIN

The eight new tests were first run against the unmodified RV from a scratch test file under the lane directory. The import traceback proved the module path was the lane tree's PIN RV. First failing assertion per test:

```
test_gpg_is_never_resolved_from_the_callers_path
  Failed: DID NOT RAISE GovernanceError

test_the_child_path_is_fixed
  TypeError: verify_review() got an unexpected keyword argument 'gpg'

test_an_explicit_gpg_must_be_an_absolute_regular_file
  TypeError: verify_review() got an unexpected keyword argument 'gpg'

test_gpg_absent_raises_a_governance_error
  AttributeError: module agent_factory.governance.review has no attribute '_GPG_PATHS'

test_a_fifo_swapped_in_after_the_precheck_is_refused_not_hung
  AssertionError: assert 'hung' == 'review recor... regular file'

test_a_fifo_swapped_in_for_the_signature_is_refused_not_hung
  AssertionError: assert 'hung' == 'review recor... regular file'

test_the_read_primitive_proves_the_fd_not_the_path
  assert 'os.fstat(fd)' in '…'
```

The two expected PIN greens also reproduced:

- `test_a_hostile_path_does_not_break_the_real_gpg` returned. At the PIN this was a tautological green: the hostile fake itself was the verifier because `shutil.which("gpg")` at `RV@2da04bf:114` selected it. After the repair, `/usr/bin/gpg` is the only possible executor.
- `test_a_fifo_at_the_record_path_is_unreviewed` refused at the unchanged pre-check: `fubuki-packet-unreviewed` from `RV@2da04bf:109-110`.

The two FIFO REDs were caught by the 10-second SIGALRM guard. `TimeoutError("hung")` is an OSError, so the existing PIN mapping `raise GovernanceError("fubuki-review-record-invalid", str(exc)) from exc` at `RV@2da04bf:126` turned it into a GovernanceError whose detail was `hung`; the pinned detail assertion then failed. The old open therefore hung until the guard fired, rather than returning naturally.

## FILES / HUNKS

### RV — `src/agent_factory/governance/review.py`

Digest `010054c04f697c8c` → `06da43e1024e548b`; 179 → 211 lines.

Post-edit plain-path lines (new code does not exist at the PIN and is therefore described rather than aliased under the report lint's `--rev 2da04bf` mode):

- RV line 32 imports `stat`; `shutil` leaves RV.
- RV lines 48-51 define `_GPG_PATHS: tuple[str, ...] = ("/usr/bin/gpg", "/usr/bin/gpg2")` as THE code trust root.
- RV lines 58-80 replace `_read_no_symlink` with `_read_regular_file`.
- RV line 63 opens with `O_RDONLY | O_NOFOLLOW | O_NONBLOCK | O_CLOEXEC`.
- RV lines 65-67 perform `os.fstat(fd)`, require `stat.S_ISREG(st.st_mode)`, and raise the exact `review record is not a regular file` detail.
- RV lines 101-116 add `gpg: str | Path | None = None`; the docstring states that production never passes it and tests may pass a deliberate absolute path.
- RV lines 134-145 validate an explicit path with `is_absolute()` + `is_file()`, or choose the first regular file in `_GPG_PATHS`. Neither branch reads the environment.
- RV lines 152-156 read record, signature, and owner key through `_read_regular_file` and preserve the OSError → `fubuki-review-record-invalid` mapping.
- RV line 168 sets the exact child env `{"GNUPGHOME": home, "PATH": "/usr/bin:/bin", "LC_ALL": "C"}`.
- RV lines 22-25 rewrite the F5 docstring claim to the fixed trust decision and fixed child PATH.

Removed PIN behavior: `shutil.which("gpg")` at `RV@2da04bf:114`; `os.environ.get("PATH", "/usr/bin:/bin")` at `RV@2da04bf:136`; `_read_no_symlink` at `RV@2da04bf:51-68`.

Post-edit invariant:

```
grep -n 'shutil\|os.environ' src/agent_factory/governance/review.py
=> 0 lines (grep rc 1)
```

Taxonomy:

- A missing or non-regular pathname at the unchanged pre-check remains `fubuki-packet-unreviewed`; the PIN equivalent is `RV@2da04bf:109-110`.
- A non-regular FD opened after that pre-check now returns `fubuki-review-record-invalid: review record is not a regular file` via the new `_read_regular_file` + unchanged mapping class.

### TR — `tests/test_governance_review.py`

Digest `ea9e0a466a4807d2` → `1ec52c579c7b4558`; 279 → 476 lines. All 16 existing tests remain.

New/rewritten post-edit lines:

- TR lines 264-271 rewrite `test_gpg_absent_raises_a_governance_error` to monkeypatch `review._GPG_PATHS` instead of the old `monkeypatch.setattr(shutil, "which", lambda name: None)` at `TR@2da04bf:264`.
- TR lines 290-307 add the hostile PATH helper. Its fake writes the specified `fake-bin/RAN` sentinel and shapes import/list/verify output.
- TR lines 332-343 add `test_gpg_is_never_resolved_from_the_callers_path`; the `.asc` file is exactly 8 bytes of garbage; it asserts signature-invalid and absent `RAN`.
- TR lines 346-353 add the hostile-PATH positive control through real gpg.
- TR lines 356-374 add the exact child PATH dump (`/usr/bin:/bin`) through explicit scripted gpg.
- TR lines 377-394 reject the brief's three explicit-gpg values plus an existing relative file. The fourth call is the live discriminator for the `is_absolute()` half: `Path("gpg").is_file()` is true after chdir, but the production guard still refuses it.
- TR lines 397-424 / 427-454 add record/signature FIFO race regressions, each with a 10-second SIGALRM and <5-second wall assertion.
- TR lines 457-467 pin that a plain FIFO at t0 is unreviewed.
- TR lines 470-476 add the AF-AP-80 source-shape pin requiring `os.fstat(fd)` and excluding `os.stat(`.

`shutil` stays imported because the key fixture still calls `shutil.rmtree` at `TR@2da04bf:71` (post-edit line 75); only the old `shutil.which` test use is deleted.

### RM — `docs/governance/reviews/README.md`

Digest `662fd187a827461b` → `20be44677047f037`; 59 → 74 lines.

RM lines 19-33 add `## What the verifier trusts`: fixed `_GPG_PATHS`, fixed child PATH, tests-only explicit `gpg=`, and the two-level non-regular-file taxonomy. The unchanged PIN owner step is `## Owner step — sign a review record` at `RM@2da04bf:19` and shifts down.

PK stays byte-identical. Its production call remains `verify_review(packet_hash, reviews_dir=reviews_dir, owner_key=owner_key)` at `PK@2da04bf:155` and passes no gpg.

## MUTATION AUDIT — 8/8 killed

Each mutant was a scratch copy under the lane dir, never the worktree RV. Every copy compiled first. The test rig injected the matching scratch path as `agent_factory.governance.review`; a proof file recorded each imported `__file__` (`mut/m1-review.py` through `mut/m8-review.py`).

| mutant | full relevant subset | named isolate / discriminator | first failing line | result |
|---|---:|---:|---|---|
| m1 restore `shutil.which("gpg")` | `4 failed, 6 passed, 14 deselected in 0.65s` | `1 failed, 23 deselected in 0.10s` | `Failed: DID NOT RAISE GovernanceError` | KILLED |
| m2 forward caller PATH | `1 failed, 9 passed, 14 deselected in 0.65s` | `1 failed, 23 deselected in 0.13s` | hostile PATH != `/usr/bin:/bin` | KILLED |
| m3 drop `O_NONBLOCK` | `2 failed, 8 passed, 14 deselected in 20.65s` | `2 failed, 22 deselected in 20.16s` | detail was `hung` | KILLED by guards |
| m4 drop `S_ISREG` check | `2 failed, 8 passed, 14 deselected in 0.67s` | `2 failed, 22 deselected in 0.16s` | reason became signature-invalid | KILLED |
| m5 `_GPG_PATHS = ("gpg",)` | `5 failed, 5 passed, 14 deselected in 0.63s` | `1 failed, 23 deselected in 0.09s` | `fubuki-review-gpg-unavailable: no gpg at gpg` | KILLED |
| m6 drop `is_absolute()` | `1 failed, 9 passed, 14 deselected in 0.65s` | `1 failed, 23 deselected in 0.10s` | existing relative gpg: `Failed: DID NOT RAISE` | KILLED |
| m7 drop `O_NOFOLLOW` | `1 failed, 9 passed, 14 deselected in 0.66s` | `1 failed, 23 deselected in 0.11s` | symlink: `Failed: DID NOT RAISE` | KILLED |
| m8 `os.fstat(fd)` → `os.stat(path)` | `1 failed, 9 passed, 14 deselected in 0.65s` | `1 failed, 23 deselected in 0.06s` | source pin lacks `os.fstat(fd)` | KILLED by shape pin only |

Declared limit: m8 is the AF-AP-80 pairing, not a behavioral proof. The t1→t2 window is not forced; the source-shape pin kills the path-stat mutant.

m4 discrepancy: the brief predicted a JSON/detail failure. On gpg 2.4.7 the empty FIFO snapshot reaches gpg first; gpg rejects the signature before JSON parse, so the failing assertion is the reason (`fubuki-review-signature-invalid`), not an `Expecting value` detail. The mutant is still killed.

m6 discrepancy/fix: the brief's original three values do not discriminate `is_absolute()` from `is_file()`; all three fail `is_file()` too. An existing relative file under a chdir'd cwd does discriminate the halves. That fourth call is now committed in the named test, and the m6 isolate is red for the exact expected reason.

## SCREENS

```
AF-AP-115 count in RV: 0
RV whole-file remaining hit: AF-AP-110: 1 (same as PIN)
TR screen: AF-AP-80: 2 (the paired source-shape assertions)
pyflakes RV + TR: 0 lines, rc 0
```

At the PIN, the screen found `AF-AP-115: 2` and `AF-AP-110: 1`. The two AF-AP-115 triggers were the resolved/forwarded caller PATH paths now removed.

## PC GATES

Declared inputs existed and were exported on every run:

```
FUBUKI_OS_ROOT=/home/rocco/fubuki-pin/fubuki-os
FUBUKI_OTHER_ROOT=/home/rocco/fubuki-pin/fubuki-os-other
```

Direct PC gates, xdist installed, lane-local `--basetemp` (not `/tmp`):

```
(a) review suite, -n 4, run 1   24 passed in 0.81s   rc=0
(a) review suite, -n 4, run 2   24 passed in 0.81s   rc=0
(b) review suite, serial        24 passed in 1.71s   rc=0
(c) exact six-file set, -n 4    57 passed in 1.08s   rc=0
(d) lane-basetemp gpg-agent     0 before -> 0 after
```

The alarm-guard tests therefore pass both xdist and main-thread serial shapes. The exact six-file set id is `f3baa8cf79c7` under the brief's stated Python formula. A pristine-PIN cross-check in a temporary detached worktree returned `49 passed in 0.88s`, rc 0; the +8 is exactly this lane's eight new tests.

## NOT-DONE

- Issue #18 is untouched: the C-lane six surviving mutants, duplicate JSON members, owner-key deployment path, and gpg-agent cleanup remain outside GOV2d.
- No gpg-agent cleanup was built; this lane measured 0→0 only.
- PK is not edited.
- No load_packet-level duplicate of the hostile-PATH unit regression was added; `verify_review(packet_hash, reviews_dir=reviews_dir, owner_key=owner_key)` at `PK@2da04bf:155` is the sole production call and structurally takes the default fixed tuple.
- No commit, push, stash, checkout, reset, tag, production service change, or credential access occurred.

## SELF-ATTACK

1. Fixed paths could miss a distro's gpg location. This is a visible, fail-closed code decision: both absent paths produce `fubuki-review-gpg-unavailable`; this PC's `/usr/bin/gpg` is real gpg 2.4.7.
2. The FIFO tests could pass from timing. m3 removes `O_NONBLOCK` and restores the 10-second guard failures in both record/signature tests; serial and xdist shapes pass only with the fix.
3. Relative explicit gpg could evade the guard. The committed fourth explicit-gpg call creates a relative regular file after chdir; production refuses it, while m6 returns and is killed.

## DISCREPANCIES

1. `scripts/pc_suite.sh` uses locale-sensitive shell `sort`; on this six-file set it yields `892ef4ebb5b8` because `pin.py` / `pin_enforcement.py` order differs from Python byte sorting. The brief's stated Python formula yields `f3baa8cf79c7`, matching the C-lane id; this report uses that value.
2. GitNexus's clone index did not resolve the symbols (`risk: UNKNOWN`). Graft + ripwire supplied the caller evidence; `lane_context.sh` refreshed graft and wrote the final pack. GitNexus `detect-changes` against the clone index reported `No changes detected` because the lane is detached from that clone index; it is disclosed, not treated as an absence of impact.
3. The final lane-context screen reports generic `AP-32: 2` on `_is_governance_hash` plus `AF-AP-110: 1`; item 7's named AF-AP-115 result remains 0. No AP-32 behavior was changed.
4. Report lint is run with `--rev 2da04bf`; therefore only PIN-era lines can be machine-checked. New lines are cited by plain path/in words as the brief requires; PIN lines use `alias@2da04bf:NN`.
5. Final report lint: `report_lint: 27 refs — OK 27, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (at 2da04bf)`; rc 0.

## FILE IDENTITY

```
PIN:
RV 010054c04f697c8c  TR ea9e0a466a4807d2  RM 662fd187a827461b  PK 5d8cf21468adb55e
FINAL:
RV 06da43e1024e548b  TR 1ec52c579c7b4558  RM 20be44677047f037  PK 5d8cf21468adb55e
```

Only RV, TR, RM, and this required report are modified in the lane worktree. Scratch red/mutation rigs stay outside the worktree.

## RETRO

The brief's m6 mutation case did not distinguish `is_absolute()` from `is_file()`. The repair is in the committed test: an existing relative file is the missing discriminator. Coordinator action: run `/bug-echo` and decide whether this earns an ANTI-PATTERN REGISTRY row. No other lesson to bake.
