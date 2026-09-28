# I59-F: the proof-code follow-ups before the owner's re-sign (task #335)

Authored 2026-09-28 13:2xZ by the coordinator. Lane: sandbox `code-implementer` (Opus 5.5), root-only work (S0-05's
netns and sudo tests), so the sandbox is the venue by rule. Work tree: `/home/user/i59-landing` at the PIN below, NOT the
main tree (another lane holds five files there).

## WHY

VERIFY-I59-BCE (`tasks/briefs/i59/VERIFY-I59-BCE-report.md`) and VERIFY-I59-LANDING
(`tasks/briefs/i59/VERIFY-I59-LANDING-report.md`) graded the issue #59 batch MERGE-READY-WITH-FOLLOWUPS. The follow-ups
below change files that S0-03, S0-04 and S0-05 attest, so each one forces a re-mint and a new signature. Landing them
before the owner signs means the owner signs the twelve proofs once.

## CONTRACT

1. **E-1 (S0-03).** No failure message of `proofs/S0-03/check_omniroute_roundtrip.py` (C) prints a value read from the
   profile. Today three do: `key_env` (C:808), the compression header (C:800), and `api_mode` through the `transport`
   template (C:148, raised at C:789). Print a shape instead (for example a length and a short hash prefix, like S0-04's
   `_short()`), never the value. Check every other message in C for the same class; fix each one that prints a profile
   value, and list the ones you checked. A test per path: a fake value with no `sk-`, `bearer ` or `basic ` prefix, built
   at run time, never appears in stdout or stderr, not even as a 4-character run.
2. **B-1 (S0-05).** `proofs/S0-05/tools/pc/run_s0_05_units.sh` (R) refuses an evidence root whose path contains a newline,
   with exit 73 and nothing written (today `$(readlink -m …)` and `$(dirname …)` strip it; R:95-110). Test through the
   real runner, with the verifier's reproduction.
3. **B-2 (S0-05).** The handback does not descend into a mount point on the same filesystem, as R's comment (R:517-524)
   says. Compare mount ids (statx `STATX_MNT_ID`, or `/proc/self/mountinfo`), or open children with `openat2` and
   `RESOLVE_NO_XDEV`. If no way works on this kernel, make the comment true instead and say why. A root-only test: a bind
   mount under the root; the owner of the file outside does not change.
4. **B-3 (S0-05).** The handback walks iteratively: an explicit stack, one directory descriptor open at a time. It hands
   back every entry of a 1,100-level tree, also under `RLIMIT_NOFILE` 1024, and its summary counts every entry it left.
5. **B-4 (S0-05).** R refuses a SUDO_UID or SUDO_GID above 4294967294 (exit 64, before anything is written; R:118), and
   the handback passes ids as `c_uint` after a range check. Tests for 4294967295, 4294967296 and 4294967297.
6. **B-6 (S0-05).** A root-only test covers the other-filesystem branch: a tmpfs under the root is left as it is and is
   named on stderr. The verifier's mutant X6 (`if st.st_dev != dev:` becomes `if False:`) reds it as a FAILED test.
7. **Task #331, AF-AP-234 (S0-05 tests).** The signal tests start the runner with SIGINT, SIGHUP and SIGQUIT at SIG_DFL,
   through the exec shim `tests/test_gpu_window.py:313-317` already uses (extended to the three signals). Show the four
   tests the verifier named passing when the gate itself runs with INT and HUP ignored (its `nohup bash -c '… & wait'`
   form), and what they did before the shim.
8. **C-1 and C-2 (S0-04 tests).** In `tests/test_s0_04_compression.py`: one test per read error of `do_config` pins its
   exact line (a non-UTF-8 file; a file unreadable to uid 65534); the tests whose contract names stderr only assert
   `proc.stdout == ""`. The verifier's mutants C-X4 and C-X6 red.
9. **E-2 (S0-03 tests).** In `tests/test_s0_03_omniroute.py`: assert `result.stderr == ""` where the failure goes to
   stdout. The verifier's mutant E-X7 reds.
10. **F2 (CI).** The pytest line of `.github/workflows/stage0-ci.yml` uses `-rfEs` (FAILED, ERROR and SKIPPED in the
    short summary), and the pin in `tests/test_no_laya_in_gates.py` matches it exactly.

Not in this round: the re-mint (the coordinator does it after the verify), F3 and AF-AP-234's skill lines (the
coordinator's), I-1 (S0-07's path-dependent stdout hash), I-3 (task #320), `harness-ports/tests/test_qwen_matrix_sh.sh`.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. For every item, a red-to-green pair: the test fails on the PIN's bytes (pasted) and passes on yours.
3. Each new test has a named mutant that reds it as a FAILED test (AF-AP-223); the verifier's X6, C-X4, C-X6 and E-X7
   are killed.
4. `bash scripts/test_summary.sh` twice on each touched test file, with its set id (the floors are in the premise).
5. `bash -n` on R, pyflakes rc 0 on every changed Python file, `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints
   0 for every file you write.
6. After the gates: `ip netns list` is empty and the iptables stable form equals its value before (the verifier's
   `0528d077bca3781a` form: comments dropped, counters masked).
7. NOT-done and DISCREPANCIES.

## BOUNDARY

- MODIFY: `proofs/S0-03/check_omniroute_roundtrip.py`, `tests/test_s0_03_omniroute.py`,
  `proofs/S0-05/tools/pc/run_s0_05_units.sh`, `tests/test_s0_05_egress.py`, `tests/test_s0_04_compression.py`,
  `.github/workflows/stage0-ci.yml` (the one pytest line), `tests/test_no_laya_in_gates.py` (the one pin).
- CREATE: your report, `tasks/briefs/i59/I59-F-report.md`.
- READ everything else. Never re-mint a proof, and never touch `proofs/*/result.json` or `proofs/ledger.json`.

## STANDING RULES

- No git writes, no PC bridge, no subagents, no outward-facing action.
- Never read a real secret source. Test secrets and ids are fake values built at run time.
- Work only in `/home/user/i59-landing`. Never touch `/home/user/agent-factory` (another lane holds files there).
- A commit in this worktree would start a 740 MB re-index (task #332): you make no commits anyway.
- The disk is shared: about 1.6 GB free. Scratch under 200 MB in `.../scratchpad/i59f/`, deleted as you go.
- Run a gate that sends signals in a FOREGROUND call (AF-AP-234), each call under 10 minutes. Kill by pid only.
- Counts are pasted from `scripts/test_summary.sh`. Stamps are substituted from `date -u`, never typed.
- If the harness refuses your report-file write, return the whole report as your final message.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.

## PREMISE — MEASURED at authoring (2026-09-28 13:2xZ; PIN = c32ac3f (origin, the pushed landing chain))

```
$ git -C /home/user/i59-landing rev-parse --short HEAD ; git status --porcelain | wc -l
c32ac3f
0
$ sha256sum <the seven boundary files> | cut -c1-16,65-
3dbf485fc95ca591  proofs/S0-03/check_omniroute_roundtrip.py
dc541933f0209d50  tests/test_s0_03_omniroute.py
b6780a867b67aceb  proofs/S0-05/tools/pc/run_s0_05_units.sh
cf0ba1cd5f359124  tests/test_s0_05_egress.py
16f8e425dace7457  tests/test_s0_04_compression.py
a76ac2136095c8a0  .github/workflows/stage0-ci.yml
64c6043337ec9362  tests/test_no_laya_in_gates.py
$ grep -n "key_env is\|COMPRESSION_REQUEST_HEADER} is\|profile api_mode {!r}" proofs/S0-03/check_omniroute_roundtrip.py ; grep -n '_fail("transport", api_mode)' proofs/S0-03/check_omniroute_roundtrip.py
148:    "transport": "transport: profile api_mode {!r} is not in the permitted set",
800:            f"bundle: profile.yaml {COMPRESSION_REQUEST_HEADER} is {value!r}, expected 'off'"
808:            f"bundle: profile.yaml key_env is {block.get('key_env')!r}, expected 'OMNIROUTE_API_KEY'"
789:        _fail("transport", api_mode)
$ grep -n 'readlink -m\|dirname --\|\[1-9\]\[0-9\]{0,9}\|_handback() {\|def hand\|st_dev != dev\|RecursionError' proofs/S0-05/tools/pc/run_s0_05_units.sh
95:# submodule) in the root or in any directory above it, after `readlink -m` resolves every symbolic link
99:EVIDENCE_REAL=$(readlink -m -- "$EVIDENCE_ROOT") && [ -n "$EVIDENCE_REAL" ] \
109:  _dir=$(dirname -- "$_dir")
118:  if ! [[ "$SUDO_UID:${SUDO_GID:-}" =~ ^(0|[1-9][0-9]{0,9}):(0|[1-9][0-9]{0,9})$ ]]; then
219:if [ -n "$UNIT_USER" ] && ! [[ "$UNIT_USER" =~ ^(0|[1-9][0-9]{0,9}):(0|[1-9][0-9]{0,9})$ ]]; then
252:  real=$(readlink -m -- "${file:-/nonexistent}")
525:_handback() {
535:def hand(fd, where, dev):
538:    if st.st_dev != dev:
554:                except (OSError, RecursionError) as exc:
$ grep -n "\-rs" .github/workflows/stage0-ci.yml tests/test_no_laya_in_gates.py
.github/workflows/stage0-ci.yml:46:        run: python -m pytest tests/ -q -rs   # -rs: every skip prints its reason (FU-4, VERIFY-I59-A)
tests/test_no_laya_in_gates.py:873:    run_at = lines.index("        run: python -m pytest tests/ -q -rs   # -rs: every skip prints its reason (FU-4, VERIFY-I59-A)")
$ grep -n "SIG_DFL" tests/test_gpu_window.py ; grep -c -E 'SIG_DFL|preexec_fn' tests/test_s0_05_egress.py
317:               "import os, signal, sys; signal.signal(signal.SIGINT, signal.SIG_DFL); os.execvp(sys.argv[1], sys.argv[1:])"]
0
$ bash scripts/test_summary.sh tests/test_s0_03_omniroute.py   (1 files set=696563f67d3c)
pytest-exit: 0
pytest-summary: 209 passed in 36.26s
$ bash scripts/test_summary.sh tests/test_s0_04_compression.py   (1 files set=2e5825a9019e)
pytest-exit: 0
pytest-summary: 178 passed in 19.39s
$ bash scripts/test_summary.sh tests/test_no_laya_in_gates.py   (1 files set=e3695f80792b)
pytest-exit: 0
pytest-summary: 121 passed in 14.62s
$ df -m / | tail -1
/dev/vda          258020 36285      1654  96% /
```

Quoted, not re-run at authoring; your item 1 re-measures them. From VERIFY-I59-BCE, on the same bytes (R and T equal the
hashes above): `tests/test_s0_05_egress.py` alone `297 passed in 244.50s` (1 files set=9f0502080347); mutants X6, C-X4,
C-X6 and E-X7 SURVIVED (its mutation tables); the four signal tests fail with INT and HUP ignored at launch
(`4 failed, 11 passed, 282 deselected`, its item 3) and pass with default dispositions.
