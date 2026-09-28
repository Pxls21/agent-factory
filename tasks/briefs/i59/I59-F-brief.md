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

## ROUND 2 (the fold of A-1..A-4): the message sent to the resumed lane, 2026-09-28 14:5xZ, verbatim

The lane's round-1 report (`tasks/briefs/i59/I59-F-report.md`, in the worktree until it lands) found A-1 to A-5. The
coordinator folded A-1 to A-4 into this lane before the verify round, so the owner signs once (D-101 (5)); A-5 is task
#343.

> I59-F round 2 (task #335): fold your adjacent defects A-1, A-2, A-4 and A-3 into this lane before the verify round; the owner signs once, so every small proof fix lands before the re-mint.
>
> What changed while you ran: nothing inside your boundary. Your report is harvested. The main tree moved (two local doc commits); the worktree is yours as before. The coordinator accepts D3 (the shim resets five signals) and keeps D5 (mapping keys may print; values never). D4 stays as is.
>
> Boundary (the worktree's .lanes-live, updated): your seven files, plus proofs/S0-04/check_compression.py (CC), tests/test_gpu_window.py (GW) and your report file. Nothing else. Same rules as round 1: no git writes, no PC bridge, no subagents, no outward action; no stub, fake or shortcut; fake secret-shaped values are built at run time.
>
> Items, each with a red test before the fix (on the current bytes) and a green after, plus at least one named mutant that the new test kills:
>
> 1. A-1 (S0-05 containment). S0_05_UNIT_USER is refused with exit 64, before anything is written and before any unit launches, unless it is `<uid>:<gid>` in canonical decimal (no sign, no leading zero, no empty part) with each id in [1, 4294967294]. 4294967295 is (uid_t)-1, which leaves root in place, so it is refused. If the current code deliberately allows gid 0, stop and report that before changing it. The post-launch root check compares numerically, never as a string. Rows through the real runner: 4294967296:4294967296, 4294967295:4294967295, 0:0, 00:00, 01:1, -1:1, :1, 1:, 1x:1, and one over ten digits; each asserts exit 64, the exact message, and that no unit ran. Positive control: 65534:65534 proceeds.
> 2. A-2 (S0-04). Every CC message that prints a profile or config value prints its shape instead: `absent`, or `<type>, <n> characters, sha256 <8 hex>` (the same format as C's `_shape`). Mapping keys may print. New T4 rows mirror T3:971: the fake value is built at run time, there is no case-folded 4-character run of it in stdout or stderr, the exact stdout line is pinned, and stderr is empty. List every CC message that reads the profile or config, with its disposition, as you did for C.
> 3. A-4 (S0-05). First prove it: a red test through the real runner shows the pair identity path losing a trailing newline at R:272. If it proves, apply B-1's treatment (sentinel read, newline refusal, exit 73, `printf %q`) with mutants. If it does not prove, report the evidence and change nothing.
> 4. A-3 (test harness). GW's INT_DEFAULT restores SIGPIPE and SIGXFSZ for the script under test, as T's SIGNALS_DEFAULT does. A test shows the child's SigIgn for those signals is 0 (red before, green after).
>
> Out of scope: A-5 (the -rs in scripts/test_summary.sh); the coordinator registers it as its own task. Do not touch it.
>
> Gates: gate every test that names each file you change. Compute the list yourself with grep -l over tests/*.py and harness-ports/tests/*. Run each gate twice, and paste each summary line verbatim from scripts/test_summary.sh with its set id. The validate-ledger and proof-status reds stay expected, and S0-04 joins S0-03 and S0-05 in them once CC changes: name each red and its cause.
>
> Disk: the container has about 1.6 GB free, and lane_gate.sh refuses below 1,500 MB. Make no large copies. Delete any tree copy a red run leaves behind (about 218 MB each) once you have read its log. If the floor stops a gate, stop and report it; do not work around it.
>
> Report: append a section "## Round 2 (the fold of A-1..A-4)" to tasks/briefs/i59/I59-F-report.md, in the same form as round 1: per item, gates twice, the mutation table, static checks, host state, final sha256 prefixes of every file you changed, discrepancies, NOT-done. Return that section as your hand-back message. If the report-file write is refused, the hand-back message is the report of record.

## ROUND 3 (D-R2-2 and D-R2-3): the message sent to the resumed lane, 2026-09-28 15:5xZ (15:51:20Z), verbatim

Round 2 (appended to the lane's report) folded A-1 to A-4 with 15 of 15 mutants killed. Two of its discrepancies were
folded before the verify round; this is the last pre-verify round.

> I59-F round 3 (task #335): two small folds from your round-2 discrepancies, then the verify round. This is the last pre-verify round.
>
> What changed while you ran: nothing inside your boundary. Round 2 is accepted as reported. Same boundary and rules as round 2.
>
> 1. D-R2-2 (S0-04's api_mode observation). The mode name is an enum the owner reads, not a secret (task #35, decided 2026-09-08: chat_completions is the live transport). The observation prints the name when it is one of the known modes, and the shape otherwise. Take the known set from the checkers' own permitted set, not from a new list: C's transport set, or CC's own if it has one; say which you used. Failure messages keep printing the shape. Tests: a known mode prints its name (pin the exact line); an unknown fake value built at run time prints only its shape, with no case-folded 4-character run of it in stdout or stderr. Name a mutant for each.
> 2. D-R2-3 (VERIFY-E3 F11, both halves).
>    - A unit identity resolved from the default (a pinned agent owned by <uid>:0) is refused with gid 0, as an explicit one is: exit 64, before anything is written and before any unit launches.
>    - A7 records the unit's Gid line beside its Uid line and compares it numerically with the wanted gid.
>    - Tests through the real runner: the <uid>:0 default is refused; the A7 record carries the gid; the positive control proceeds with 65534:65534.
>    - Keep the committed evidence's shape readable by the validators: find every reader of unit-identity.json (grep) and state that each still reads the new record. If one would break, stop and report instead.
>    - Name a mutant for each half.
>
> Gates as in round 2: every test that names a changed file, twice each, summary lines pasted with their set ids. The expected reds stay the same three: S0-03, S0-04 and S0-05 attestation mismatches.
>
> Report: append "## Round 3 (D-R2-2 and D-R2-3)" to tasks/briefs/i59/I59-F-report.md, in the same form, with the final sha256 prefixes of every file you changed. Return that section as your hand-back message.

## ROUND 3, ITEM 1: THE ROUTE RULING, 2026-09-28 16:4xZ (16:43:56Z), verbatim

Round 3 stopped item 1 (D-R2-2) on a boundary conflict: CC has no mode set of its own, and reading C's set at run time reds S0-04's drift guard unless S0-04's registry row attests C (route A). The coordinator chose route B.

> I59-F round 3, item 1 (D-R2-2): take route B. Your stop was right.
>
> The ruling: CC keeps its own copy of the two mode names. A T4 test pins that copy equal to C's PERMITTED_API_MODES, reading C as data in the test only, never from CC. This is a deliberate deviation from my "no new list" line. Route A would make S0-04's attestation cover S0-03's checker, so every later change to C would invalidate S0-04 too. A pinned copy keeps the two proofs independent and still catches drift.
>
> Build item 1 as the round-3 message says:
> - a known mode prints its name, with the exact line pinned;
> - an unknown fake value, built at run time, prints only its shape, with no case-folded 4-character run of it in stdout or stderr;
> - failure messages keep printing the shape;
> - a named mutant for each, plus one for the pin (a CC copy that differs from C's set reds the pin test).
>
> Leave CE alone. Its gid grading (your D-R3-4) goes to the verify round as a question. Your other round-3 work stands as reported.
>
> Gates as before: every test that names CC or T4, twice each, with set ids. Also run the S0-04 and S0-05 rows of TA's drift guard, to show S0-04 reads no new repo file.
>
> Append your results to the round-3 section under a subheading "Item 1, route B", with the final sha256 prefixes. Return that subsection as your hand-back message.

## ROUND 4 (the verify fold and task #344): the message sent to the resumed lane, 2026-09-28 18:1xZ (18:13:31Z), verbatim

VERIFY-I59-F graded rounds 1-3 MERGE-READY-WITH-FOLLOWUPS (`tasks/briefs/i59/VERIFY-I59-F-report.md`); the owner ruled one re-mint with S0-01 (D-104 (3)).

> I59-F round 4 (task #335, plus task #344): fold VERIFY-I59-F's findings and the S0-01 parse fix before the one re-mint. The owner ruled "just do the fix first and then re-mint everything at once", so this is the last build round before the re-mint of S0-01, S0-03, S0-04 and S0-05.
>
> VERIFY-I59-F graded your patch MERGE-READY-WITH-FOLLOWUPS. Its report of record is /home/user/agent-factory/tasks/briefs/i59/VERIFY-I59-F-report.md; read its findings F-1 to F-16 (lines 384-481) first. Nothing changed inside your boundary while you were idle. Same rules as before: no git writes, no PC bridge, no subagents, no outward action; no stub, fake or shortcut; fake values are built at run time.
>
> Boundary (the worktree's .lanes-live, updated). Your nine files, plus:
> - proofs/S0-05/check_egress.py (CE);
> - the two synthetic fixtures proofs/S0-05/fixtures/evidence-synthetic-pass/ and evidence-synthetic-uid0/;
> - proofs/S0-01/check_acp_conformance.py and proofs/S0-01/tools/build_capture_record.py;
> - a NEW test file tests/test_s0_01_manifest_parse_linear.py (do not edit tests/test_s0_01_check_acp_conformance.py; it is 6,641 lines).
> Each item below needs a red before the fix on the current bytes, a green after, and a named mutant its test kills.
>
> 1. F-1: route B's known set is the wrong vocabulary. S0-04 observes the provider block's Hermes `transport` (capture_leg.py:121; `openai_chat` in the committed real evidence). Widen CC's known set to the Hermes provider transport names as well as S0-03's two api_modes. Take each name from a pinned source in the repo, as data: at least proofs/S0-03/hermes/config.yaml and the committed real S0-04 evidence. Cite each source file:line in the comment. Pin the set with a T4 test that reads those sources as data. The real bundle must then print `openai_chat` by name: pin that line against proofs/S0-04/evidence. An unknown value still prints only its shape.
> 2. F-2: a provider block that is not a JSON object fails with `provider block is not a JSON object` and prints nothing of it. Add T4 rows for an array and a string.
> 3. F-3 and F-8 (tests): add the asymmetric rows to T's BAD_UNIT_USERS (4294967296:65534, 65534:4294967296, 4294967295:65534, 65534:4294967295, 0:65534, 65534:0), and a non-string row to T3's PROFILE_VALUE_PATHS and T4's CONFIG_VALUE_PATHS. The verifier's surviving mutants N1 to N5 must then die.
> 4. F-4 and F-12 (R's walk): every climb checks that the walk is still inside the root (compare with the root's device and inode), and the walk stops loudly when it is not. Correct the comment "It changes nothing outside the root" to state what holds. Word the stop line apart for "moved" and "a mount appeared on a parent".
> 5. F-7 (R's launch and A7): launch units with an explicit group list, so no supplementary group is inherited (for example `--clear-groups`, or `--groups=<gid>`; verify what setpriv supports here). A7 also records the Groups line and refuses a 0 in it. Update the record's readers as in round 3.
> 6. F-11 (CE): grade the gid. A unit-identity record without a gid key, or with a 0 in it, fails CE with an exact reason. Add the gid key to both synthetic fixtures (uid0 keeps its uid 0). The committed real evidence will fail CE until the PC re-capture at the re-mint, which records the gid through round 3's A7. Name that red as expected, with its one cause.
> 7. F-9 (C): an unhashable api_mode and a recursive alias end in a failure_reason line, never a traceback. A read error is named as a read error, not "not valid YAML".
> 8. F-10 (CC): the observation text says task #35 was decided by D-021 on 2026-09-08. Drop "open decision" and "ADR 0002 deviation". Update T4's pin.
> 9. F-13 and F-14 (R): id patterns use explicit character lists (`[123456789][0123456789]…`), as netns_lib.sh's rule X1 does. The refusal quotes the value with printf %q.
> 10. F-6: `_shape`'s docstring in C and CC says it protects high-entropy values, not short guessable ones.
> 11. Task #344 (S0-01): `_parse_manifest_body` (check_acp_conformance.py:1066) and tools/build_capture_record.py:44 build each digest by `+=` on a dict value, which is quadratic. Collect each section's lines in a list and join once. The output must be byte-identical: check on every committed golden manifest that the digests equal the old code's, with the old code run from a scratch copy. The new test file proves linear time: a 200,000-line manifest parses under a wall bound the old code misses, with the old code as the red. Also report tests/test_s0_01_check_acp_conformance.py's wall time before and after, run alone with a private --basetemp.
>
> Out of scope: F-5 (a unit that leaves its namespace survives the teardown; pre-existing, no egress) becomes a follow-up issue, and F-15 and F-16 are notes.
>
> Gates: every test that names each changed file, twice each, pasted with set ids, and TA's drift guard rows for S0-01, S0-04 and S0-05. The expected reds are the attestation mismatches: now S0-01, S0-03, S0-04 and S0-05. Name any other red and its cause.
>
> Disk: about 1.3 GB free. Keep scratch small and deleted, and use a private --basetemp outside any work tree.
>
> Report: append "## Round 4 (the verify fold and task #344)" to tasks/briefs/i59/I59-F-report.md, in the same form as before, with the final sha256 prefixes of every changed file. Return that section as your hand-back message.
