> **COORDINATOR NOTE (2026-09-28 12:4xZ):** the verifier returned this report as its final message (its resume message kept it out of the shared tree, and the harness refuses subagent report files). The coordinator saved the text as the report of record, extracted from the verifier's transcript (its SubagentHandback call at 12:44:58Z), never retyped.

# VERIFY-I59-BCE: report (the whole report; written 2026-09-28 12:4xZ)

I wrote no report file. Your resume message forbids touching the shared tree, the brief's report path is inside it, and the harness refuses subagent report files. This message is the whole report.

## TL;DR: three gate recommendations

No finding meets the whole blocking predicate. Each change has real follow-ups.

- **I59-B (S0-05 runner, task #313): MERGE-READY-WITH-FOLLOWUPS.**
  - B-1 to B-4 all map to the contract and all reproduce, but each needs an input no real run makes:
    - B-1: a clone whose directory name ends in a newline.
    - B-2: a bind mount that root made under the evidence root.
    - B-3: a unit that writes a directory tree about 1000 levels deep.
    - B-4: a SUDO_UID that sudo cannot set.
  - B-5 has no frozen clause, and the runner is correct.
- **I59-C (S0-04 `do_config`, task #314): MERGE-READY-WITH-FOLLOWUPS.** Two test-strength gaps (C-1, C-2).
- **I59-E (S0-03 `_read_yaml`, task #327): MERGE-READY-WITH-FOLLOWUPS.** E-1 is outside the change's boundary; E-2 is test strength.
- **Brief item 3 is answered: neither load nor a runner race.** The four "load" failures come from how the gate was launched. It left SIGINT and SIGHUP set to "ignored", and bash cannot trap a signal that was ignored when it started. I reproduced the coordinator's four failures exactly with no load, and got zero failures under 8 and 24 CPU hogs (B-5). **Task #331's planned fix (wait on a readiness marker) would not fix this.**
- **What the recommendations rest on:** every sandbox claim above is reproduced by me. The item-6 PC shapes (2c, 2i, 2j) are the coordinator's measurements; I did not re-run them (no bridge).

## Pin and setup

- I made a worktree at the landing commit (`/tmp/vbce-wt`, detached, parent 8992772).
- The landed bytes match each lane's final hashes:
  - R `b6780a867b67aceb`
  - T `cf0ba1cd5f359124`
  - `capture_leg.py` `f2e5d54c80343e61`
  - S0-03 checker `3dbf485fc95ca591`
- R's census function is byte-identical at the parent and the landing: 134 lines, sha256 `3f02ca397d32092d…`.
- The landing does not change `check_egress.py`, `run_canaries.sh` or S0-05's evidence.
- At the end: worktree removed with `git worktree remove --force`, all `/tmp/vbce-*` scratch deleted, no mount left, `ip netns list` empty.

## Gates (pasted from `scripts/test_summary.sh`)

**I59-B: `tests/test_s0_05_egress.py`, 1 files set=9f0502080347** (2026-09-26 11:31:55Z–11:36:00Z)
```
pytest-exit: 0
pytest-summary: 297 passed in 244.50s (0:04:04)
```

**I59-B: `tests/test_edit_snapshot_ap_screen.py` + `tests/test_s0_05_egress.py`, 2 files set=c05fbc3b558e**
- First run, 2026-09-26 12:24:38Z–12:28:43Z. It did return on my side just before the stop.
```
pytest-exit: 0
pytest-summary: 494 passed in 244.84s (0:04:04)
```
- The re-run you asked for, one foreground call, 2026-09-28 12:28:27Z–12:33:32Z:
```
pytest-exit: 0
pytest-summary: 494 passed in 298.98s (0:04:58)
```
- After the gates: `ip netns list` has 0 lines. The iptables stable form is `0528d077bca3781a` before and after (comments dropped, counters masked, the builder's DISCREPANCY-1 form).

**I59-C: `tests/test_s0_04_compression.py`, 1 files set=2e5825a9019e**
```
pytest-exit: 0
pytest-summary: 178 passed in 12.83s
pytest-exit: 0
pytest-summary: 178 passed in 13.07s
```

**I59-E: `tests/test_s0_03_omniroute.py`, 1 files set=696563f67d3c**
```
pytest-exit: 0
pytest-summary: 209 passed in 26.17s
pytest-exit: 0
pytest-summary: 209 passed in 26.59s
```

**Red states** (direct pytest, parent file put back into my worktree):
- I59-C: `22 failed, 156 passed in 12.67s` (the builder's figure).
- I59-E: `12 failed, 195 passed, 2 skipped in 26.00s`. The 12 are the builder's. The 2 skips (T:1609, T:2124, "S0_01_REAL_LEG_DIR unset") are my instrument: direct pytest does not get `test_summary.sh`'s export.

**Non-root venue** (uid 65534, direct pytest):
- `-k i59b`: `8 passed, 14 skipped, 275 deselected in 1.72s`.
- S0-04 new rows: `50 passed, 128 deselected in 5.44s`.
- S0-03 `-k profile_parse`: `14 passed, 195 deselected in 2.86s`.

**Static checks:**
- `bash -n` R: rc 0.
- pyflakes over the six changed files: rc 0.
- `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`: 0 for all six.
- `no_laya_in_gates: 41 files scanned, clean`.

## Item 3: the signal tests (VERIFIED)

**The launch form, from the session transcript.** The coordinator's loaded gate was started as `(setsid nohup bash -c "cd /home/user/agent-factory && bash scripts/test_summary.sh tests/test_s0_05_egress.py > $SC/i59b-gate.log 2>&1; …" </dev/null >/dev/null 2>&1 &)`.
- Replaying that form, the child ignores SIGHUP, SIGINT and SIGQUIT. The background job inside a subshell runs without job control, so it also ignores INT and QUIT.
- The landing suite's form was `setsid nohup bash $SC/landing-suite.sh … &` in the tool shell, which has job control on. Replaying it, the child ignores SIGHUP only.
- The tool's own foreground and background modes ignore nothing.

**Why that matters.** bash cannot trap a signal that was ignored when it started. In a script's background job, `trap … INT` leaves `trap -p INT` as `trap -- '' SIGINT`, and a SIGINT then does nothing (measured).

**Reproduction with no load.** Selection `-k 'x4_runner_cleanup or e3b_r4 or e3r1_r1 or i59b_the_handback_runs_when_a_signal'` (15 tests):

| launch | result |
|---|---|
| default dispositions | `15 passed, 282 deselected in 41.17s` |
| INT and HUP ignored (`nohup bash -c '… & wait'`) | `4 failed, 11 passed, 282 deselected in 203.46s (0:03:23)` |
| HUP only ignored (`nohup` in the foreground) | `1 failed, 14 passed, 282 deselected in 77.05s (0:01:17)`: `test_i59b_the_handback_runs_when_a_signal_stops_the_run[HUP]`, the landing suite's 10th failure |

The four failures are exactly the coordinator's, with the same lines (T:3084, T:1880, T:4236 twice) and the same symptom: rc 1 after a complete run, or "timed out waiting for cleanup's SIGTERM to reach the unit". The four are `test_e3b_r4_sigint_stops_the_runner_with_130`, `test_e3r1_r1_b[int-then-term-to-the-group]`, `…signal_stops_the_run[INT]` and `[HUP]`.

**The load control never failed** (default dispositions):
- 8 hogs: `15 passed, 282 deselected in 54.80s`.
- 24 hogs: `15 passed, 282 deselected in 70.84s (0:01:10)`.
- All of T under 8 hogs: `297 passed in 341.46s (0:05:41)`.
- The hogs were started and killed by pid; 0 were left.

**Pattern:** every failing test sends INT or HUP first. Every TERM-first test passes in every launch form.

## Finding inventory

### I59-B

**B-1 FOLLOW-UP: the guard misses a work tree whose directory name ends in a newline.**
- VERIFIED through the real runner. Contract 4a (and 4b under sudo). Canonical path: yes.
- Mechanism: `$(readlink -m -- …)` and `$(dirname -- …)` both strip trailing newlines. The walk then checks `…/nlrepo/.git`, not `…/nlrepo\n/.git`.
- Why not a blocker: only a hypothetical path has such a name (predicate condition 3).
- Under sudo, a root whose last component ends in a newline makes the existence check and the handback use the stripped path. The run prints `handback: nothing handed back: …/new: No such file or directory`, and the evidence stays `root:root`.
- Reproduction (verified as printed, as root, from a tree at the landing commit):
  ```
  W=$(mktemp -d); git init -q "$W/nlrepo"$'\n'; env -i PATH="$PATH" HOME="$W" bash proofs/S0-05/tools/pc/run_s0_05_units.sh "$W/nlrepo"$'\n'"/evidence" not-a-unit; echo rc=$?; ls "$W/nlrepo"$'\n'"/evidence"
  ```
  Result: rc=1 (not 73), then `s0-01-census.json` and `units.json` inside the work tree (git: `true`).
- Fix: refuse any root that contains a newline (`case $EVIDENCE_ROOT in *$'\n'*) … exit 73`), or keep the newline with a sentinel.

**B-2 FOLLOW-UP: the handback descends a same-filesystem bind mount; R:522-523 says a mount point is not descended.**
- VERIFIED on R's own handback code. It is cut from the landing's bytes by `awk '/^_handback\(\) \{/{f=1;next} f&&/<<.PY.$/{p=1;next} p&&/^PY$/{exit} p' proofs/S0-05/tools/pc/run_s0_05_units.sh > handback.py` (48 lines, sha256 `b5662ea9cc1a9258`).
- Contract 4b: "changes nothing outside the evidence root".
- Why not a blocker: the runner's own actors cannot make this state. Only root can mount under the root, and the unit user cannot make a mount the runner sees.
- Mechanism: the only mount check is `st.st_dev != dev`, and a same-filesystem bind mount has the same `st_dev`. A tmpfs mount is left as the comment says.
- Reproduction (verified, as root):
  ```
  S=/tmp/r; mkdir -p $S/root/mnt $S/out && echo o > $S/out/f && chown 65534:65534 $S/out/f && mount --bind $S/out $S/root/mnt && python3 -B handback.py $S/root 4242 4243; stat -c %u:%g $S/out/f; umount $S/root/mnt
  ```
  Result: `4242:4243`. A file outside the root changed owner.
- Fix: compare mount ids (statx `STATX_MNT_ID`), or open children with `openat2` and `RESOLVE_NO_XDEV`; or reword the comment.

**B-3 FOLLOW-UP (the strongest): a deep tree is not handed back, and the summary understates what was left.**
- VERIFIED through the real runner under the sudo variables, using T's helpers (`_sudo`, `_runner_env`, `_invoker_dir`, `_listener`, `_run_runner`). A stand-in unit made a 1100-level chain in its HOME (the scratch tree).
- Result:
  - rc 1 (the normal end).
  - One summary: `1001 entries … now belong to 4242:4243; 1 left as they are`.
  - 107 entries are not the invoker's.
  - `rm -rf` as the invoker fails (rc 1, Permission denied).
- Mechanism: `hand()` recurses once per level, so RecursionError hits near level 997, and the whole subtree below is dropped with one stderr line. It also holds 2 descriptors per level: with `RLIMIT_NOFILE` 1024, EMFILE hits at 511 levels ("511 entries … 1 left", 190 entries not handed back). The sandbox's limit is 20000. The PC root's limit is INFERRED to be 1024.
- Contract 4b: "every entry … so the invoking user can delete the whole evidence root without sudo". Canonical path: yes.
- Why not a blocker: only a unit that writes a very deep tree triggers it. The failure is loud and safe: nothing outside the root changes.
- Reproduction (verified):
  ```
  S=/tmp/r; mkdir -p $S/deep && (cd $S/deep && for i in $(seq 1100); do mkdir d && cd d; done) && chown -R 65534:65534 $S/deep && python3 -B handback.py $S/deep 4242 4243 2>&1 | tail -1; find $S/deep ! -uid 4242 | wc -l
  ```
  Result: `997 entries … 1 left as they are`, then `104`.
- Fix: walk iteratively with an explicit stack, one directory descriptor open at a time, and count every entry that is left.

**B-4 FOLLOW-UP: out-of-range SUDO ids are accepted and silently masked.**
- VERIFIED. R's check `^(0|[1-9][0-9]{0,9}):…$` accepts 4294967296.
- The handback passes an untyped Python int through ctypes, which truncates it to 32 bits:
  - 4294967296 hands everything to `0:0`.
  - 4294967295 changes nothing (it is `(uid_t)-1`).
  - 4294967297 hands everything to `1:1`.
  - Each time the summary says "now belong to 4294967296:4294967296", which is false.
- Contract 4b. Why not a blocker: sudo never sets such ids (misuse only). It is the class of anti-hollow-green tactic 1: a numeric guard must reject the whole unusable class.
- Reproduction (verified):
  ```
  mkdir -p /tmp/r/t/sub && chown -R 65534:65534 /tmp/r/t && python3 -B handback.py /tmp/r/t 4294967296 4294967296; stat -c %u:%g /tmp/r/t /tmp/r/t/sub
  ```
  Result: `0:0` twice.
- Fix: reject ids above 4294967294, or set `argtypes` to `c_uint` and check the range.

**B-5 FOLLOW-UP: the signal tests depend on how the gate is launched; re-scope task #331.**
- VERIFIED (see Item 3). No frozen clause requires independence from the launch form. The runner is POSIX-correct.
- The E3-era tests already had this dependency; I59-B adds `[INT]` and `[HUP]` to it.
- The result is a false red, never a false green. But it happens under the repo's own detached-gate recipe (env-tool-quirks: `nohup … > gate.log 2>&1 &`).
- Fix: start the runner with default signal handling in the signal tests, for example `preexec_fn` resetting SIGINT, SIGHUP and SIGQUIT to `SIG_DFL` in `_runner_session` and the other signal tests' Popen calls. Or assert the handling first and fail with a named reason.

**B-6 FOLLOW-UP: no test covers the other-filesystem branch.**
- My mutant X6 (`if st.st_dev != dev:` becomes `if False:`) SURVIVED: `6 passed in 7.03s`. The builder's DEVIATION-8 already flags this.
- Fix: a root-only test with a tmpfs under the root.

**B-7 INFO: the guard holds for 13 hostile shapes.** Each exits 73 with nothing written:
- relative roots (two working directories);
- `..` inside the clone;
- `..` after a symbolic link (the physical parent is the clone);
- a lexical `..` out of a directory not made yet;
- inside `.git`;
- deep under `.git/objects`;
- a symbolic link to the clone's top;
- a trailing newline on the last component only;
- T's five cases, and the dubious-ownership case.

Exit 73 is the only way out, except B-1.

**B-8 INFO: Unicode lookalikes are not holes.**
- A lookalike of a clone's name is a different directory, and a `.gіt` directory (Cyrillic і) is not a repository to git either. Both run normally.
- Case-insensitive filesystems were not tested (none in the sandbox).

**B-9 INFO: `readlink -m` succeeds on a symbolic-link loop.** It returns rc 0 and the unresolved path, so the guard's "cannot resolve" exit is never reached for loops. `mkdir` then fails with ELOOP and nothing is written (rc 1). Harmless.

**B-10 INFO: hostile entry types are handed back correctly.**
- Handed back, with nothing outside changed: a socket, a character device, a FIFO, links to an outside file and directory, a name with a newline, a non-UTF-8 name, and a setuid file of the unit user.
- The kernel clears the setuid bit on the chown (4755 becomes 0755), so no privilege moves to the invoker.
- A hard link with both names inside the root is left as it is, and the invoker can still delete it.

**B-11 INFO: a symbolic link swapped in during the walk changes nothing.** 300 handback runs against a live process that swapped a directory under the root for a link to an outside tree: the outside tree never changed (9.5 s).

**B-12 INFO: without SUDO_UID the runner behaves as at the parent (item 4c, behaviour diff).**
- Same inputs to the parent's R and the landing's R, with pids, digests and paths normalized.
- rc, stdout, stderr and the evidence tree are identical for:
  - a full leg (rc 1);
  - a census failure (rc 1);
  - an existing root (rc 1);
  - SIGINT mid-leg (rc 130);
  - a non-root run (rc 2).
- The one difference is the intended one: a root inside a clone. The parent writes three root-owned entries into the clone (rc 1); the landing refuses with rc 73.

**B-13 INFO: every exit path runs the handback exactly once** (real runner, sudo variables): INT (rc 130), TERM (rc 143), HUP (rc -1), census failure (rc 1), census changed (rc 1), and the natural end each print exactly one summary line. The census-changed run is the builder's NOT-done item: 8 entries were handed back, and the invoker deleted the root.

**B-14 INFO: limit 8's words match the census (items 1-2).**
- R:63-74 and R:280-291 match `appended()` at R:400-407: the same holders (pid and start time) at both snapshots, a regular file on both sides, the same mode, uid and gid, and the same sha256 over the first `was.size` bytes.
- "Larger" is not checked directly. It follows from the entry differing plus the head check, except in a race inside the compare itself (census code unchanged by I59-B).
- T:3610 and T:3622 agree.
- M1 and M4 are killed as FAILED tests.

**B-15 INFO: DEVIATION-1 (exit 74 on an existing root under sudo) does not break the recorded PC commands.** Their root is a new dated path under `sudo env`. The refusal also applies to SUDO_UID=0 (sudo from a root shell).

### I59-C

**C-1 FOLLOW-UP: the read-error path is not pinned by a test.**
- Mutant C-X4 moves `read_regular` back inside the broad `try`. It SURVIVED: 178 of 178 pass.
- That mutant turns a read error (non-UTF-8, unreadable file) into "not valid YAML (<Class>)", which breaks "nothing else in the tool changes".
- The landed code is right. My parent-vs-landing diff is byte-identical (rc, stdout, stderr and artifact) on 10 non-parse paths: missing, directory, FIFO, non-UTF-8, top-level list, empty, provider absent, success, a date in the headers, and unreadable as uid 65534.
- Fix: one test per read error, pinning the exact line.

**C-2 INFO: stdout is guarded only by the 8-character window.** Mutant C-X6 (print the last 7 characters of the message to stdout) SURVIVED: 178 of 178. stderr is pinned exactly, so any stderr leak fails; the contract speaks of stderr only. Fix: assert `proc.stdout == ""`.

**C-3 INFO: hostile profiles leak nothing (VERIFIED).**
- 20 shapes, and a MemoryError under a 90 MB address-space limit: no 4-character run of the value in stdout or stderr; class and position only.
- The shapes: the `!!int`, `!!float`, `!!bool` and bad `!!timestamp` tags; a custom tag and a tag named by the value; invalid `!!binary`; `!!set` and `!!omap` on a scalar; `!!python/object`; a hex `!!int` and a `!!float` with underscores; a merge of a scalar; an unhashable key; two documents; `%YAML 1.3`; a NUL; bad UTF-8; `!!str` on a mapping; a duplicate anchor.
- Bad UTF-8 in the value goes through the unchanged read path. It prints one non-ASCII byte and an offset.
- Under a 140 MB limit the interpreter aborts (rc -6, "Fatal Python error … MemoryErrors") with no value printed; the parent does the same.

**C-4 INFO: the de-vacuous preconditions hold.** They are checked in process before each CLI run, and the stderr assertions are exact. G6 pins 4 segments caught and 5 passing in both files, with `API_KEY_ENV=` as an ordinary control in both.

### I59-E

**E-1 FOLLOW-UP: other S0-03 paths print a value read from the profile (item 6's question: yes).**
- Verified through the real CLI on a passing bundle. These paths print the value whole on stdout:
  - `key_env` (C:808);
  - `api_mode` (the C:148 template);
  - the compression header (C:800).
- A value starting with `sk-` in `key_env` is caught first by `_walk_credentials` and printed without the value. A key with no `sk-`, `bearer ` or `basic ` prefix is not.
- Outside I59-E's boundary ("nothing else in the checker changes"). It widens the AF-AP-232 class to "a failure message that quotes a profile value".
- Reproduction (verified, in a tree at the landing commit, with `PYTHONDONTWRITEBYTECODE=1`): load `tests/test_s0_03_omniroute.py` through importlib, copy `FIXTURES/"evidence-stub-route"` with `provider="codex"` (the `passing` fixture's steps), and replace `key_env: OMNIROUTE_API_KEY` with `key_env: Zq0FAKE9a8b7C6d5E4f3`. Then `run_checker(root).stdout` prints:
  ```
  failure_reason: bundle: profile.yaml key_env is 'Zq0FAKE9a8b7C6d5E4f3', expected 'OMNIROUTE_API_KEY'
  ```
- Fix: print a shape (a length or a hash prefix, like `_short()` in S0-04's checker), never the value.

**E-2 INFO: stderr is guarded only by the 8-character window**, which is the contract's own bound. Mutant E-X7 (write the last 7 characters of the message to stderr) SURVIVED: 209 of 209. stdout is pinned exactly. Fix: assert `result.stderr == ""`.

**E-3 INFO: `from None` is complete for a printed traceback.** K4 (drop it) and my E-X1 (`from exc`) are both killed. `__context__` still references the quoting error, as the builder states; nothing in the repo walks it.

**E-4 INFO: hostile profiles leak nothing.** 13 shapes, and a MemoryError under a 160 MB limit, each exit 1 with the exact `bundle: hermes/profile.yaml is not valid YAML (<Class>)` line. No 4-character run of the value in stdout or stderr.

## Mutation tables

All I59-B verdicts are FAILED tests with no errors (junit). R was edited in place and restored by sha after each mutant; the worktree ended clean.

**I59-B**

| mutant | source | verdict | failures |
|---|---|---|---|
| M1 | builder | KILLED | 1 (F-2) |
| M4 | builder | KILLED | 1 (F-3) |
| G1 | builder | KILLED | 6 |
| G2 | builder | KILLED | 1: only the dubious-ownership boundary test |
| H1 | builder | KILLED | 5 |
| H2 | builder | KILLED | 1 |
| H3 | builder | KILLED | 1 |
| P1 | builder | KILLED | 3 |
| E1 | builder | KILLED | 1 |
| X1: handback at the natural end only | mine (4b, every exit path) | KILLED | 4 |
| X2: no `readlink -m` | mine | KILLED | 1 |
| X3: `.git` directory only | mine | KILLED | 1 |
| X4: no ancestor walk | mine | KILLED | 5 |
| X8: handback without SUDO_UID | mine (4c) | KILLED | 2 |
| X6: no other-filesystem check | mine | SURVIVED | 0 |

**I59-C** (the whole file per mutant; total 178 each)
- The builder's six:
  - G2-OLD: KILLED, 10 failed.
  - G2-VK: KILLED, 4.
  - G5-D5: KILLED, 16.
  - G6-B3: KILLED, 2.
  - G6-B5: KILLED, 2.
  - G6-ENV: KILLED, 2. I made the `_env` exclusion case-sensitive, the A10 shape.
- Mine:
  - C-X1, the message carries `str(exc)`: KILLED, 22.
  - C-X2, no class: KILLED, 22.
  - C-X3, `context_mark` read first: KILLED, 4.
  - C-X5, exit 2: KILLED, 22.
  - C-X4: SURVIVED (see C-1).
  - C-X6: SURVIVED (see C-2).

**I59-E** (total 209 each)
- The brief's three:
  - K1 is the parent's handler: the red state, 12 failed.
  - K2: KILLED, 4 failed.
  - K3: KILLED, 14.
  - K4: KILLED, 7.
- Mine:
  - E-X1, `from exc`: KILLED, 7.
  - E-X4, every class except RecursionError: KILLED, 2.
  - E-X6, `_require_file` inside the `try`: KILLED, 2 (the FIFO and missing-file tests).
  - E-X7: SURVIVED (see E-2).

## Reproduced vs static vs skipped

**Reproduced:** everything above except these:
- **Static only:** the limit-8 words against the predicate. I read them against the code and checked M1 and M4.
- **On R's extracted handback code, not through the runner:**
  - B-2 (the runner cannot produce its trigger);
  - B-4;
  - the 1024-descriptor case of B-3.

**Skipped, and why:**
- The PC and the item-6 shapes: no bridge, as the brief says.
- The full suite: VERIFY-I59-LANDING's scope.
- The builders' extra mutants: I59-C's D4, D7, D8, G5-ISO, G6-B2, G6-ENV0 and per-file rows; I59-E's K5, K6 and EQUIV. I ran well over three per builder.
- Case-insensitive filesystems: none in the sandbox.

## NOT-done

- No report file (see the first paragraph).
- No PC run.
- The deep-tree case under a 1024-descriptor limit did not go through the runner. The runner hit RecursionError first, at the sandbox's limit of 20000.
- No commits, pushes or subagents, and nothing written in the shared tree or in `/home/user/i59-landing`.

## DISCREPANCIES

- **D1:** Task #331 and the brief's premise call the signal failures load-sensitive. They depend on how the gate was launched (B-5). The ledger's own words ("the runner finished before the test's signal landed") describe the symptom, not the cause.
- **D2:** The builder's DISCREPANCY-5 says R's usage exit is 127. Here (bash 5.2.21) it is 1, with no argument and with an empty argument.
- **D3:** The builder's report says R has 848 lines. It has 847 (the parent's 737 is right).
- **D4:** The brief's PIN paragraph gives the landing's parent as origin eb48880. It is 8992772 after the rebase, as your message and the premise block say.
- **D5:** R's comment at R:522-523 overclaims about mount points (B-2).
- **D6:** The handback summary "1 left as they are" understates a deep tree (B-3).
- **D7:** The first combined I59-B gate did return on my side (494 passed, 2026-09-26 12:28:43Z). You saw no return, so I pasted both runs.
