> **Coordinator's note (2026-10-02 07:5xZ).** The verifier's final message for round 3 of task #460 (the B1 re-check at PIN 6c14466f), whole, saved from its transcript by the harvest (run s-20261002T075348Z-68c775; the hand-back was absent, task #426). Two edits: the message's first line, the lane's own S1-RATE score line, is dropped; and the coordinator's local retro commit, which the push rewrote, is cited as "the retro commit" (subject: "Retro: a CI quirk baked (an interpreter's error text can change inside one Python minor); task 460: the B1 re-check dispatched at 6c14466f"). Served model: one, on all 282 assistant records of the lane's transcript (both rounds); 0 refusal stops. The coordinator's gate and the D-115 deadlock review are in the ledger (2026-10-02, TASK #460 HOME).

# VERIFY-S1-VIEW-GUARDS: B1 re-check at 6c14466f (task #460, round 3)

**Verdict: NOT-READY. B1 is not fixed, and a second blocker (B2) shares its cause.**
- **What the repair fixes:** the four `hop/../link` spellings, and every other spelling I tried whose parts all exist. All exit 2 and write nothing.
- **B1, still open:** a path with a missing directory before `..` still gets through. `--out <C>/hop/missing/../../link` exits 0 and writes `view.jsonl` and `summary.json` through the link.
- **B2, new to the inventory:** the same cause breaks D-6. `--out <F>/missing/../E`, where E is a full directory, exits 0 and replaces E's older `view.jsonl` and `summary.json`. This gap has existed since 92d74958.
- **The git rule holds** on every spelling I tried.
- **One fix in `check_out` closes both.** A candidate tested in scratch is in §7.

Scratch root `<W>` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vfy460-wKeKV0`. All runs used Python 3.11.15 with `PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1 TMPDIR=<W>/tmp` and no `-n`.

## 1. Premise

**At the start (07:24:28Z) all four premise commands matched:**
- `origin/claude/soundbox-kit-migration-iz1jwf~1` = `6c14466f6b68e9ba06fea2bd639860bcf6d647a8`.
- The diffstat from 0555298e to 6c14466f: view.py 10 (+8 −2), test 34 (+29 −5); 2 files, 37 insertions, 7 deletions.
- sha256[:16]: view.py `4629e0c720edaa82`, test `08b027e5a3972651`.
- origin = HEAD = 1ffee610.

**At the end (07:45:19Z), pasted:**
```
HEAD the retro commit  origin 1ffee610  origin~1 6c14466f6b68e9ba06fea2bd639860bcf6d647a8
6c14466f is an ancestor of HEAD
 scripts/s1_train/view.py    | 10 ++++++++--
 tests/test_s1_train_view.py | 34 +++++++++++++++++++++++++++++-----
 2 files changed, 37 insertions(+), 7 deletions(-)
scripts/s1_train/view.py git@6c14466f 4629e0c720edaa82 archive 4629e0c720edaa82 HEAD-diff-lines 0
tests/test_s1_train_view.py git@6c14466f 08b027e5a3972651 archive 08b027e5a3972651 HEAD-diff-lines 0
status of the two files: []
```
HEAD moved to the retro commit during the round. That commit is local; origin is still 1ffee610. Both subject files are byte-identical at 6c14466f and at HEAD, so the premise holds.

**The trees I ran:**
- **Subject:** a new `git archive 6c14466f` in `<W>/p6c`.
- **Comparison:** `<W>/pin`, the round-2 archive of 0555298e (view.py `9ca2bece43af9a9f`), and a whole-tree archive of 92d74958 (view.py `16f1905ce72aee78`), deleted after use.
- Each view.py matched `git show <commit>:scripts/s1_train/view.py | sha256sum`.

## 2. R1: the four spellings through the CLI at 6c14466f

**Fixture:** `<W>/b1r2.py` builds a real export with the new archive's exporter, then a build from it. It sets `F/C/hop` → `F/B/sub` and `F/B/link` → `F/T` (empty). Each case takes a snapshot of every path under F before and after the run.

Command: `( cd <W> && python3 b1r2.py p6c r1a r1b r1c r1d )`
```
r1a R1 hop/../link        rc=2 | s1-view: refused: --out <F>/C/hop/../link is a symbolic link
      new=[] changed=[] gone=[] git=[]
r1b R1 hop/../link/       rc=2 | s1-view: refused: --out <F>/C/hop/../link/ is a symbolic link
      new=[] changed=[] gone=[] git=[]
r1c R1 hop/../link/.      rc=2 | s1-view: refused: --out <F>/C/hop/../link/. is a symbolic link
      new=[] changed=[] gone=[] git=[]
r1d R1 hop/../link/./.    rc=2 | s1-view: refused: --out <F>/C/hop/../link/./. is a symbolic link
      new=[] changed=[] gone=[] git=[]
```
**R1 holds.** All four exit 2 with the D-10 reason, and no path under F is new, changed or gone.

## 3. R2: other spellings

**Fixture additions:**
- `B/hop2` → `X/sub2`, and `X/link` → `T2`.
- `B/dang` → `nowhere` (a dangling link).
- `B/l2` → `B/l1` → `L1T` (a link to a link).
- `R/repo` is a git repo holding `empty/`; `B/link_repo` → `R/repo/empty`.
- `C/clink` → `C/clink_target`.
- `B/link_ne` → `E2`.
- `B/loop` → itself.
- `AP/x` → `AQ/inner`; `AP/y` → `T3`; `AQ/y` is a real, empty directory.
- `E`, `Wd` and `E2` each hold `keep.txt` plus an older `view.jsonl` and `summary.json`.
- `Z0` is empty.

In the tables, "Names" is the entry the kernel resolves once `write()`'s `os.makedirs` has created the missing parts.

### 3a. Missed: these break D-10 or D-6

| key | --out (C = F/C) | names | at 6c14466f | rule |
|---|---|---|---|---|
| m1 | `C/hop/missing/../../link` | B/link → T | rc=0; new `T/view.jsonl` and `T/summary.json`; stray `B/sub/missing` | D-10 broken |
| m2 | `C/missing/../hop/../link` | B/link → T | rc=0; writes into T; stray `C/missing` | D-10 broken |
| m3 | `C/hop/../link/missing/..` | T through B/link (same as `link/.`) | rc=0; writes into T; new `T/missing` | D-10 broken |
| m4 | `C/hop/missing/../../link_ne` | B/link_ne → E2 (full) | rc=0; **E2's `view.jsonl` and `summary.json` replaced**; stray `B/sub/missing` | D-10 and D-6 broken |
| m5 | `C/hop/a/b/../../../link` | B/link → T | rc=0; writes into T; strays `B/sub/a` and `B/sub/a/b` | D-10 broken |
| m6 | `C/hop/missing/../../dang` | B/dang (a dangling link) | rc=2 at write with `[Errno 17] File exists`; stray `B/sub/missing` left behind | D-10 "nothing written" broken |
| d1 | `F/missing/../E` | E (full) | rc=0; **E's `view.jsonl` and `summary.json` replaced**; stray `F/missing` | D-6 broken |
| d2 | `F/Wd/missing/..` | Wd (full) | rc=0; **Wd's `view.jsonl` and `summary.json` replaced**; stray `Wd/missing` | D-6 broken |

Pasted from `python3 b1r2.py p6c`:
```
m1  hop/missing/../../link                 rc=0 | 
      new=['B/sub/missing', 'T/summary.json', 'T/view.jsonl'] changed=[] gone=[] git=[('T/view.jsonl', 'no')]
m4  hop/missing/../../link_ne (E2 full)    rc=0 | 
      new=['B/sub/missing'] changed=['E2/summary.json', 'E2/view.jsonl'] gone=[] git=[('E2/view.jsonl', 'no')]
m6  hop/missing/../../dang                 rc=2 |  refused: --out <F>/C/hop/missing/../../dang: [Errno 17] File exists: '<F>/C/hop/missing/../../dang'
      new=['B/sub/missing'] changed=[] gone=[] git=[]
d1  missing/../E (E full)                  rc=0 | 
      new=['missing'] changed=['E/summary.json', 'E/view.jsonl'] gone=[] git=[('E/view.jsonl', 'no')]
d2  Wd/missing/.. (Wd full)                rc=0 | 
      new=['Wd/missing'] changed=['Wd/summary.json', 'Wd/view.jsonl'] gone=[] git=[('Wd/view.jsonl', 'no')]
```
m2, m3 and m5 printed the same shape as m1; their stray directories are in the table.

**Mechanism, re-derived from view.py at 6c14466f:**
1. `check_out` (view.py:376-400) tests the `--out` text three ways: `os.path.islink("/".join(named) or "/")`, `os.path.islink(os.path.abspath(out))` and `os.path.lexists(out)`. All three use lstat.
2. When a part before a `..` does not exist yet, lstat fails with ENOENT. `islink` and `lexists` swallow that error and return False.
3. `abspath` collapses `missing/..` as text only, so it sees `C/link`, which does not exist.
4. `write()` (view.py:407) then calls `os.makedirs(out, exist_ok=True)`. That creates the missing part as a real directory. The kernel now resolves the same string through the link, or to the full directory, and `exist_ok=True` accepts that target.
5. The repair's comment, "a '..' stays for the kernel to resolve", holds only when every part before the `..` exists at check time.

**Pre-existence (same fixture, older CLIs):**
- **0555298e** (`python3 b1r2.py pin r1a m1 m3 m4 d1 d2 c1`): r1a, m1, m3, m4, d1 and d2 exit 0 with the same writes; c1 exits 2.
- **92d74958** (`python3 b1r2.py p92 r1a m1 m4 d1 d2 n1`): all exit 0 with the same writes. That version's `check_out` was the D-6 lexists test alone, and its `write()` comment says "nothing is written over another output".
- So both gaps were already present in the round-2 subject (0555298e), and the D-6 gap dates from task #444's landing.

### 3b. Refused or correct

| key | --out | names | at 6c14466f | met? |
|---|---|---|---|---|
| s1 | `C/hop/../hop2/../link` | X/link (a link) | rc=2 "is a symbolic link" | D-10 met |
| s2 | `C/hop/./../link` | B/link | rc=2, same reason | met |
| s3 | `C/hop//../link` | B/link | rc=2, same reason | met |
| s4 | `../link`, cwd `C/hop` (physically B/sub) | B/link | rc=2, same reason | met |
| s5 | `B/l2` (→ B/l1 → L1T) | a link to a link | rc=2, same reason | met |
| s6 | `C/hop/../dang` | a dangling link | rc=2, same reason | met |
| t1 | `B/link/..` | F (T's parent: not a link, not empty) | rc=2 "exists and is not an empty directory" | D-6 met; D-10 not at stake |
| t2 | `B/dang/..` | does not resolve | rc=2 at write, `[Errno 2]` | met |
| x1 | `C/missing/../clink` | C/clink (a link) | rc=2, caught by the abspath test | met |
| c1 | `B/link/missing/..` | T through B/link | rc=2, caught by the abspath test | met |
| m7 | `missing/../../link`, cwd `C/hop` | B/link | rc=2, caught by the abspath test (getcwd gives the physical path) | met |
| c2 | `F/R/repo/missing/..` | R/repo | rc=2 "lies inside a git work tree" | met |
| c3 | `C/hop/missing/../../link_repo` | R/repo/empty | rc=2, the git rule | met |
| l1 | `B/loop` | a self-loop | rc=2 "is a symbolic link" | met |
| l2 | `B/loop/x` | does not resolve | rc=2 at write, `[Errno 40]` | met |
| n1 | `F/missing2/.` | a new directory | rc=0, writes there | correct |
| e1 | `''` (cwd Z0) | none | rc=2, `[Errno 2]` | correct |
| e2, e3 | `.` and `./` (cwd Z0, empty) | Z0 | rc=0, writes there | correct |
| e4 | `/` | / (not empty) | rc=2 under D-6 | correct |
| o1 | `AP/x/../y` | AQ/y, a real empty directory | rc=2 "is a symbolic link" | over-refusal (I3) |

- **Nothing written:** every refused row in this table showed `new=[] changed=[] gone=[]`.
- **Git:** no spelling put an output in a work tree. Git's own verdict on every `view.jsonl` that landed was "no".

## 4. R3: the Q4 table at the new PIN

Commands: `TREE=<W>/p6c python3 q4.py` and `TREE=<W>/pin python3 q4.py`. I re-ran both now; each has 17 rows.

**14 rows are identical at both PINs** (same exit code, same reason):
- The six direct-link forms (empty dir, `/`, `/.`, full dir, file, dangling) exit 2 with "is a symbolic link".
- `dangling link, /x below` exits 2 at write with `[Errno 2]`.
- The five work-tree rows and `.. climbing into a work tree` exit 2 with "lies inside a git work tree".
- `parent link out of a work tree` exits 0 and lands in `outside/out/view.jsonl` (git "no"). D-10's text allows a link in a parent when the output ends up outside git.

**Three rows changed:**

| row | 0555298e | 6c14466f |
|---|---|---|
| hop/../link → empty dir outside | rc=0, landed in `T2_empty/view.jsonl` | rc=2 "is a symbolic link" |
| hop/../link → empty dir in repo | rc=2 "lies inside a git work tree" | rc=2 "is a symbolic link" (the link test now runs first) |
| hop/../link/ (trailing /) | rc=0, landed in `T3_empty/view.jsonl` | rc=2 "is a symbolic link" |

**No regression.**

## 5. R4: the new test and the mutants

**Red control.** I made a full scratch copy of p6c (`<W>/mut6`) and swapped in 0555298e's view.py:
```
baseline baseline   | 96 passed in 11.01s
old      old        | 4 failed, 92 passed in 11.80s
   FAILED test_an_out_that_is_a_link_after_a_dotdot_is_refused[dotdot]
   FAILED test_an_out_that_is_a_link_after_a_dotdot_is_refused[dotdot-slash]
   FAILED test_an_out_that_is_a_link_after_a_dotdot_is_refused[dotdot-dot]
   FAILED test_an_out_that_is_a_link_after_a_dotdot_is_refused[dotdot-dot-dot]
```
- The new test fails on 0555298e's view.py, and no other test does.
- Its shape check, `islink(named) and not islink(abspath(named))`, protects the fixture.

**Mutants.**
- **Method:** one exact edit per mutant, with a restore from p6c between runs. The restore is checked by hash: `end: view.py restored 4629e0c720edaa82 == p6c 4629e0c720edaa82`.
- **Scoring (AF-AP-223):** KILLED needs a FAILED test, with the total still 96.

| id | edit | result | failed |
|---|---|---|---|
| N1 | drop the named-entry test | KILLED: 4 failed, 92 passed | all four |
| N2 | drop the abspath test | SURVIVED: 96 passed | none |
| N3 | the loop drops `..` too | SURVIVED: 96 passed | none |
| N4 | `or "/"` → `or "."` | SURVIVED: 96 passed | none |
| N5 | remove `or "/"` | SURVIVED: 96 passed | none |
| N6 | `len(named) > 1` → `> 0` | SURVIVED: 96 passed | none |
| N7 | `while` → `if` | KILLED: 1 failed, 95 passed | dotdot-dot-dot |
| N8 | drop `"."` from the tuple | KILLED: 2 failed, 94 passed | dotdot-dot, dotdot-dot-dot |
| N9 | drop `""` from the tuple | KILLED: 1 failed, 95 passed | dotdot-slash |
| N10 | `normpath` before the split | KILLED: 4 failed, 92 passed | all four |
| N11 | drop the trailing-part loop | KILLED: 3 failed, 93 passed | dotdot-slash, dotdot-dot, dotdot-dot-dot |

**Survivors through the CLI** (`python3 mut6.py apply <id>`, then `python3 b1r2.py mut6 <cases>`):
- **N2 is a real survivor.** m7, c1 and x1 go from exit 2 to exit 0 and write through a link. No test covers a spelling that only the abspath test catches. Pasted:
  ```
  m7  rel missing/../../link, cwd C/hop      rc=0 | new=['B/sub/missing', 'T/summary.json', 'T/view.jsonl']
  c1  B/link/missing/.. (abspath = link)     rc=0 | new=['T/missing', 'T/summary.json', 'T/view.jsonl']
  x1  missing/../clink (abspath-only catch)  rc=0 | new=['C/clink_target/summary.json', 'C/clink_target/view.jsonl', 'C/missing']
  ```
- **N3 is equivalent in effect.** On r1a, c1, t1 and t2 it gives the same exit codes and writes. Only the reason text changes: t1 goes from "exists and is not an empty directory" to "is a symbolic link", and t2 from `[Errno 2]` to "is a symbolic link".
- **N4, N5 and N6 are equivalent.** Each changes only what `islink` sees for the entries `""`, `"."` and `"/"`, and `islink` is False for all three. I reproduced this on e1 to e4: the exit codes and writes match the PIN.

## 6. R5

```
( cd <W>/p6c && bash scripts/test_summary.sh tests/test_s1_train_view.py --basetemp <W>/bt2 )    # run twice
pytest-summary: 96 passed in 11.34s
pytest-summary: 96 passed in 11.04s
bash scripts/pc_suite.sh set-id -- tests/test_s1_train_view.py
1 files set=470c76f8303f
```
`set-id` is a local hash of the file list. I read that branch before running it: it calls no bridge and sources no env file.

## 7. Discriminator: one candidate correction (scratch only)

`<W>/cand.py` puts this into the scratch copy's `check_out`. No tracked file changed.
```python
        named = []
        for part in out.split("/"):
            if part in ("", ".") and named:
                continue
            if part == ".." and named and named[-1] not in ("", ".", "..") and not os.path.lexists("/".join(named)):
                named.pop()
                continue
            named.append(part)
        entry = "/".join(named) or ("/" if out.startswith("/") else ("." if out else ""))
        if os.path.islink(entry) or os.path.islink(os.path.abspath(out)):
        # ... the git walk is unchanged ...
        if os.path.lexists(entry) and not (os.path.isdir(entry) and not os.listdir(entry)):
```
- **The idea:** it drops each `x/..` pair whose `x` does not exist yet. `makedirs` will create `x` as a real directory, so `x/..` is just the directory before `x`.
- **Tests:** `candidate tests: 96 passed in 11.25s []`.
- **CLI results:**
  - m1 to m7 exit 2 with "is a symbolic link". m6 is now refused before any write, with no stray directory.
  - d1 and d2 exit 2 with "exists and is not an empty directory".
  - Every §3b case keeps its exit code, and n1, e2 and e3 still write.
- **What it shows:** the defect can be fixed inside `check_out` with the suite green. It is a candidate for the builder to judge, not a design ruling. It closes every spelling I tried; I do not claim it is complete.

## 8. Finding inventory

**B1. BLOCKER (still open). D-10: a missing part before `..` gets past the link rule.**
- **Evidence:** reproduced through the 6c14466f CLI (m1 to m6), and also on 0555298e and 92d74958.
- **Contract:** D-10: "Refuse (exit 2, nothing written) an `--out` that is a symbolic link, to anything, an empty directory included". The CLI help also says "not a symbolic link".
- **Canonical path:** yes: `main` → `check_out` → `write` in `scripts/s1_train/view.py`.
- **Material effect:**
  - The run exits 0 and writes `view.jsonl` and `summary.json` through the link into its target, leaving stray directories.
  - With a link to a full directory (m4), it replaces that directory's older outputs.
  - m6 exits 2 but leaves a directory behind, against "nothing written".
- **Reproduction:** `( cd <W> && python3 b1r2.py p6c m1 m2 m3 m4 m5 m6 )`.
- **Discriminator:** the §7 candidate refuses all six, with 96 passed.
- **Suggested fix:** pick one:
  - resolve the named entry the way the kernel will after `makedirs` (§7);
  - refuse a `..` that follows a part that does not exist;
  - refuse any `..` in `--out`.

  Then add tests for the m1, m3 and m4 shapes; each fails at 6c14466f.

**B2. BLOCKER (new to the inventory; present since 92d74958). D-6: a missing part before `..` gets past "must not exist, or be an empty directory".**
- **Evidence:** reproduced through the 6c14466f CLI (d1, d2, and m4), and also on 0555298e and 92d74958.
- **Contract:** D-6: "`--out` must not exist, or be an empty directory (else exit 2)". `write()`'s own comment also says "nothing is written over another output".
- **Canonical path:** yes.
- **Material effect:** exit 0. The full directory's `view.jsonl` and `summary.json` are replaced, so an older output is lost, and a stray directory is left.
- **Reproduction:** `( cd <W> && python3 b1r2.py p6c d1 d2 )`.
- **Discriminator:** §7 runs the D-6 test on the resolved entry, and refuses both.
- **Suggested fix:** the same fix as B1, because the cause is the same: the check-time lstat and lexists tests cannot see what `makedirs` will create. Add a test.

**F1. FOLLOW-UP. Test gap: mutant N2 survives.**
- **Evidence:** reproduced (§5).
- **Contract:** the D-10 tests (S1-VIEW-GUARDS demand 4).
- **Effect:** with the abspath test dropped, all 96 tests pass, yet x1, c1 and m7 write through a link.
- **Fix:** add those three spellings as test cases.
- **Why not blocking:** the code at the PIN refuses all three.

**I1. INFO. Equivalent mutants.**
- N3 changes only reason text.
- N4, N5 and N6 are fully equivalent: the `or "/"` fallback and the `len(named) > 1` floor reach only `""`, `"."` and `"/"`. Both pieces have no effect and could be removed.
- Reproduced (§5).

**I2. INFO. The git rule holds.**
- `realpath` resolves existing parts physically and drops a missing part before `..`, just as the kernel does after `makedirs`.
- No spelling put an output in a work tree: c2, c3, the Q4 work-tree rows, and git's "no" on every file that landed.

**I3. INFO. Over-refusal of o1.**
- `AP/x/../y` is refused as "is a symbolic link". But the entry the kernel resolves (AQ/y) is not a link; the abspath test reads only the text.
- The refusal is fail-closed and writes nothing; only the reason is false.
- No D-rule requires accepting this path. The §7 candidate keeps this behaviour.

**I4. INFO. Stale text.**
- The repair's comment ("a '..' stays for the kernel to resolve") and the docstring hold only when every part before `..` exists. The fix should correct them.
- The 6c14466f commit subject says "B1 repaired", and B1 still holds. The ledger text is the coordinator's.

**I5. INFO. A gap in my own round 2.**
- B1's missing-part spellings and B2 were already present at 0555298e.
- My round-2 Q4 table had no spelling with a missing part before `..`. So round 2's D-6 and Q4 verdicts were incomplete for this class.

**I6. INFO. The NUL tests (36c67018).**
- They now assert exit 2, the input's name, "embedded null", and one line of output.
- Both interpreter wordings I measured in round 2 contain "embedded null": 3.11 says "embedded null byte"; 3.13 says "lstat: embedded null character in path".
- I did not re-run them under 3.13, because this sandbox has no pytest for 3.13. I did not check CI run #1231 (no network).

**I7. INFO (static, not reproduced). A race window.**
- `check_out` and `write()` test a path and then open it by name. Between the two, a concurrent writer could swap a part for a link, or plant a `view.jsonl.part` link, which `open` would follow. This is AF-AP-70's class.
- It needs a concurrent actor on the owner's machine, so it is hypothetical misuse and not a blocker. AF-AP-70's answer (one open, then checks on the open file descriptor) may be worth weighing in I8's review.

**I8. INFO, for the coordinator's D-115 review.**
- **The class recurs:** round 2's B1 and this round's B1 and B2 share one failing assumption. The assumption is that a check of the `--out` text, or an lstat at check time, predicts what the kernel will resolve after `os.makedirs`.
- **Why it matters:** D-115 lists a recurring blocker class as a stop signal.
- **Options with evidence:**
  - ONE MORE ROUND with the §7 shape. Its convergence reason: it closes all ~35 spellings tried, with 96 passed.
  - A stricter, simpler rule, such as "no `..` part in `--out`" or "no link anywhere on the resolved path". Either would amend D-10, so it is a RE-SCOPE.
- The choice is the coordinator's.

## 9. Blocking predicate (demand 5)

Demand 5 says a finding BLOCKS when it shows the headline claim false, or when it "contradicts a frozen D-rule (D-1 to D-12)".

- **B1 meets every condition.**
  - It contradicts D-10: exit 0 and files written for an `--out` that names a link, and a directory created on m6's refusal.
  - It runs through the canonical CLI at the PIN.
  - Its effect is material: writes through a link, and replaced older outputs (m4).
  - It has a deterministic command plus the §7 discriminator.
  - It sits inside the builder's boundary (`check_out` and `write` in view.py).
- **B2 meets every condition.** It contradicts D-6 (exit 0 into a full directory), with the same path, a material effect (an older output replaced), a command, a discriminator and the same boundary.
- **Hypothetical misuse, weighed:**
  - Both blockers need an unusual spelling: a part that does not exist, followed by `..`.
  - But a script that builds `--out` as `<new dir>/..` or `<new>/../<name>` produces exactly that.
  - The effects are concrete, and D-6 and D-10 exist to govern such operator input.
  - Round 2's B1 was the same kind of spelling and was accepted as a blocker. I apply the same standard.
- **The headline claim is not shown false.** No row was written with unseen text. No candidate, label or split was wrong. No output was written in a git work tree, and no secret reached an output.
- **Not blocking:** F1 and I1 to I8.
- **No CONTRACT-DEFECT and no CONTRACT-INVALID.** D-6 and D-10 are clear and measurable, and §7 shows both are achievable.

## 10. Gate recommendation

- **B1: NOT FIXED.**
  - **Refused, nothing written:** the four `hop/../link` spellings, and every spelling whose parts all exist.
  - **Still broken:**
    - m1 to m5: a missing part before `..` still writes through the link.
    - m6: the refusal leaves a directory behind.
- **The round: NOT-READY, on B1 (still open) and B2 (D-6).**
  - **Evidence:** I reproduced both through the CLI at 6c14466f. The recommendation depends on nothing I did not reproduce.
  - **Fix:** one change in `check_out` closes both; §7 is a tested candidate.
  - **Not blocking:** F1 is a follow-up, and I1 to I8 are observations.

## 11. What I did not do, and hygiene

**Not done:**
- Run the suite under Python 3.13 (no pytest for it here).
- Check CI run #1231 (no network).
- Use the PC or the bridge.
- Reproduce I7's race.
- Test parts with denied permissions (the sandbox runs as root).
- Grade F1 to F6 or task #468.

**Repo hygiene:**
- I touched no tracked file in `/home/user/agent-factory`; `git status` of both subject files is empty. No commit, stash, checkout or reset.
- No network, bridge, subagent or background job.
- I read nothing in `.jev/`, no env file, no pseudonym key, no real export and no real transcript.
- All fixture text is fake and built at run time.
- **Rule breach:** one read-only grep command ran a top-level `cd /home/user/agent-factory` before its subshell, against the rule "never `cd` at a command's top level". It changed nothing.

**Scratch:**
- **Kept** so every probe can be re-run: `<W>/p6c` (the new archive) and `<W>/pin` (0555298e).
- **Deleted:** `<W>/mut6`, the 92d74958 archive, the `bt2` and `mbt6` basetemps, and the run directories. `mut6.py` re-creates its copy from p6c when needed.

**Probe files:**
- `<W>/b1r2.py`: R1, R2, the survivors and pre-existence; its first argument names the CLI tree.
- `<W>/b1r.py`: the first R1/R2 pass.
- `<W>/q4.py`: R3.
- `<W>/mut6.py`: R4.
- `<W>/cand.py`: §7.
- `<W>/h.py`: the fixture harness.