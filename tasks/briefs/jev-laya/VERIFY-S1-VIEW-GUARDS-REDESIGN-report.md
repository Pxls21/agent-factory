# VERIFY-S1-VIEW-GUARDS: round 4, the D-134 redesign at ded4af91 (task #460)

**Recommendation: MERGE-READY-WITH-FOLLOWUPS. B1 and B2 are fixed, and nothing blocks.**
- **`..` spellings:** all 35 CLI spellings with a `..` part exit 2 with "holds a '..' part". Nothing is written and no directory is made. That covers all 25 from round 3 and 10 new attack shapes.
- **Other spellings:** every spelling without a `..` part keeps its round-3 exit code and writes.
- **Q4:** only the 4 rows whose `--out` holds a `..` changed, and only their reason text.
- **Tests:** 102 passed, twice.
- **Main follow-up:** a test gap. A mutant that exempts a relative `--out` from the rule reopens both B1 and B2, and all 102 tests stay green.

Scratch root `<W>` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vfy460-wKeKV0`. Every run used Python 3.11.15 with `PYTHONDONTWRITEBYTECODE=1 S0_01_VENUE=sandbox HF_HUB_OFFLINE=1 TMPDIR=<W>/tmp`, no `-n`, and `COLUMNS=1000` for the mutant driver.

## 1. Premise

**Start (12:27:09Z).** I ran the coordinator's block verbatim (`<W>/premise4.sh`, each command echoed), and every line matched:
- the commit line;
- "6c14466f is an ancestor of the PIN";
- the diffstat: view.py 16, S1-VIEW-GUARDS brief 4, S3-5-VIEW brief 4, test 38; 4 files, 53 insertions, 9 deletions;
- `0` for both diff counts;
- sha16 values `e7bb13b4fd54016b`, `901c086a6a90f90a`, `dd05be817d6bb7e6`;
- `387: raise Refused("--out %s holds a '..' part" % out)`;
- the three test definitions at lines 1299, 1319 and 1343;
- `60` test definitions;
- `1 files set=470c76f8303f`.

HEAD was e4b894e1, the same as origin.

**End (12:41:52Z).** The same 28 lines matched again (`<W>/premise4-end.txt`). HEAD had moved to the coordinator's next local commit (task 472's harvest, ledger and report only); origin is still e4b894e1. Both zero-line diffs held, and `git status` of the three files was empty. The premise holds.

**Subject tree.** A new `git archive ded4af91` in `<W>/pded`. Its view.py, render.py and test hashes match git's blobs.

**The change, read from the diff.**
- `check_out` now begins with `if ".." in out.split("/"): raise Refused("--out %s holds a '..' part" % out)`, with a new docstring and comment. The named-entry test, the abspath test, the git walk and the D-6 test are unchanged.
- The amendments read: D-10, "first refuse (exit 2, nothing written) an `--out` with a `..` part ... Without a `..` the two rules above are exact"; D-6, "an `--out` with a `..` part is refused (exit 2)".
- The tests change in three ways: the four B1 forms now expect the new reason; m1, m4, d1 and d2 form a new parametrized test; a control writes into the parts `v..1` and `...`.

## 2. Ask 2: my full sweep at the PIN through the CLI

Command: `( cd <W> && python3 b1r4.py pded pded )`. The fixture is a real export and build, made by the PIN's own harness. Each case takes a snapshot of every path under the fixture root F before and after the run.

**Every spelling with a `..` part exits 2 with "holds a '..' part", and shows `new=[] changed=[] gone=[]`.**
- From round 3 (25 spellings): r1a, r1b, r1c, r1d, m1 to m7, d1, d2, c1, c2, c3, o1, x1, t1, t2, s1, s2, s3, s4, s6.
- New in this round (10 spellings): a1 to a5, a16, a17, a21, a22, a23 (listed in §5).

For example:
```
m1   hop/missing/../../link                   rc=2 | s1-view: refused: --out <F>/C/hop/missing/../../link holds a '..' part
       new=[] changed=[] gone=[] git=[]
m4   hop/missing/../../link_ne (E2 full)      rc=2 | s1-view: refused: --out <F>/C/hop/missing/../../link_ne holds a '..' part
       new=[] changed=[] gone=[] git=[]
d1   missing/../E (E full)                    rc=2 | s1-view: refused: --out <F>/missing/../E holds a '..' part
       new=[] changed=[] gone=[] git=[]
d2   Wd/missing/.. (Wd full)                  rc=2 | s1-view: refused: --out <F>/Wd/missing/.. holds a '..' part
       new=[] changed=[] gone=[] git=[]
m6   hop/missing/../../dang                   rc=2 | s1-view: refused: --out <F>/C/hop/missing/../../dang holds a '..' part
       new=[] changed=[] gone=[] git=[]
```
m6 left a stray directory in round 3; it leaves none now.

**Every round-3 spelling without a `..` part keeps its round-3 result.** I re-ran each one through 6c14466f's CLI (`python3 b1r4.py p6c p6c ...`) for the comparison:

| key | --out | 6c14466f | ded4af91 |
|---|---|---|---|
| l1 | `B/loop` | rc=2 "is a symbolic link" | the same |
| l2 | `B/loop/x` | rc=2 `[Errno 40]` at write, nothing written | the same |
| n1 | `missing2/.` | rc=0, writes `missing2/` | the same |
| e1 | `''` | rc=2 `[Errno 2]` | the same |
| e2, e3 | `.` and `./` (cwd an empty dir) | rc=0, writes there | the same |
| e4 | `/` | rc=2 "exists and is not an empty directory" | the same |
| s5 | `B/l2` (a link to a link) | rc=2 "is a symbolic link" | the same |

**Answer: no spelling does otherwise.**

## 3. Ask 3: the Q4 table at the PIN

Commands: `TREE=<W>/pded python3 q4.py` and `TREE=<W>/p6c python3 q4.py`, both run now. Then I ran `diff` on the two 17-row outputs:
```
14,17c14,17
< .. climbing into a work tree         rc=2 landed=[] | s1-view: refused: --out <Q>/outside/../repo/zq-out2 lies inside a git work tree (<Q>/repo/.git)
< hop/../link -> empty dir outside     rc=2 landed=[] | s1-view: refused: --out <Q>/C/hop/../link_empty is a symbolic link
< hop/../link -> empty dir in repo     rc=2 landed=[] | s1-view: refused: --out <Q>/C/hop/../link_repo is a symbolic link
< hop/../link/ (trailing /)            rc=2 landed=[] | s1-view: refused: --out <Q>/C/hop/../link_empty2/ is a symbolic link
---
> .. climbing into a work tree         rc=2 landed=[] | s1-view: refused: --out <Q>/outside/../repo/zq-out2 holds a '..' part
> hop/../link -> empty dir outside     rc=2 landed=[] | s1-view: refused: --out <Q>/C/hop/../link_empty holds a '..' part
> hop/../link -> empty dir in repo     rc=2 landed=[] | s1-view: refused: --out <Q>/C/hop/../link_repo holds a '..' part
> hop/../link/ (trailing /)            rc=2 landed=[] | s1-view: refused: --out <Q>/C/hop/../link_empty2/ holds a '..' part
```
- **The four changed rows:** each `--out` holds a `..` part, and the new rule runs before the link and git tests. All four still exit 2 and land nothing; only the reason changed.
- **The other 13 rows are identical**, including:
  - the six direct-link forms;
  - `dangling link, /x below`;
  - the five work-tree rows;
  - `parent link out of a work tree`: rc=0, landed in `outside/out/view.jsonl`, git "no". D-10 allows a link in a parent.

## 4. Ask 4: the tests at the PIN, twice

```
( cd <W>/pded && bash scripts/test_summary.sh tests/test_s1_train_view.py --basetemp <W>/bt )   # twice
pytest-summary: 102 passed in 13.51s
pytest-summary: 102 passed in 14.16s
bash scripts/pc_suite.sh set-id -- tests/test_s1_train_view.py
1 files set=470c76f8303f
```

## 5. Ask 5: attacks on the new rule (through the CLI unless marked)

**Fixture additions:** `B/uplink` → `../T` (relative target text); `C/up` → `..`; `B/tricky` → `../nowhere_dir/../T`.

| key | --out | ded4af91 | 6c14466f (round 3) | verdict |
|---|---|---|---|---|
| a1 | `E/..` (trailing `..`) | rc=2 `..` rule | rc=2 D-6 | refused |
| a2 | `F//..//E` (doubled slashes) | rc=2 `..` rule, nothing written anywhere | rc=0, wrote a new `<base>/E` outside F (§8, I7) | refused |
| a3 | `E//..` | rc=2 `..` rule | rc=2 D-6 | refused |
| a4 | `../Z0new` (relative, cwd Z0) | rc=2 `..` rule | rc=0, wrote `Z0new/` | refused (by design) |
| a5 | `..` (cwd Z0) | rc=2 `..` rule | rc=2 D-6 | refused |
| a16 | `F/..x/..` | rc=2 `..` rule | **rc=0, wrote view.jsonl and summary.json into F itself (a full directory)** | closed |
| a23 | `F/..../..` | rc=2 `..` rule | **rc=0, wrote into F itself** | closed |
| a17 | `E/./..` | rc=2 `..` rule | rc=2 D-6 | refused |
| a21 | `missing/../E` (relative, cwd F) | rc=2 `..` rule | **rc=0, E's view.jsonl and summary.json replaced (B2, relative)** | closed |
| a22 | `C/hop/missing/../../link` (relative, cwd F) | rc=2 `..` rule | **rc=0, written through B/link into T (B1, relative)** | closed |
| a6 | `B/uplink` (target text `../T`) | rc=2 "is a symbolic link" | the same | refused |
| a7 | `B/uplink/new` | rc=0, writes `T/new/` | the same | a parent link, outside git: allowed by D-10 |
| a8 | `C/up/E` (`C/up` → `..`) | rc=2 D-6 (E is full) | the same | refused |
| a9 | `C/up/B/link` | rc=2 "is a symbolic link" | the same | refused |
| a10 | `C/up/newdir` | rc=0, writes `F/newdir/` | the same | a parent link: allowed |
| a11 | `B/tricky/x` (target: a missing part, then `..`) | rc=2 at write `[Errno 2]`, nothing written | the same | refused |
| a18 | `B/tricky` | rc=2 "is a symbolic link" | the same | refused |
| a12, a13 | parts `...` and `a..b` | rc=0, writes there | the same | ordinary names |
| a14, a20 | parts `.. ` and ` ..` | rc=0, writes there | the same | ordinary names |
| a15 | the part U+2025 (`‥`) | rc=0, writes there | the same | an ordinary name |
| a19 | `./E/.` (no `..`, E full) | rc=2 D-6 | the same | refused |

**NUL cases, run in-process through `main`, since argv cannot carry a NUL; cwd an empty directory:**
```
nul-a in-process rc=2 stdout='' | s1-view: refused: --out <F>/x/..<NUL>: embedded null byte | new=[]
nul-b in-process rc=2 stdout='' | s1-view: refused: --out <F>/<NUL>/../x holds a '..' part | new=[]
nul-c in-process rc=2 stdout='' | s1-view: refused: --out <F>/x<NUL>/.. holds a '..' part | new=[]
nul-d in-process rc=2 stdout='' | s1-view: refused: --out ..<NUL>: embedded null byte | new=[]
```
`..<NUL>` is not a `..` part, so `realpath`'s ValueError refuses it. At 6c14466f all four gave "embedded null byte".

**Wrong refusals:** none outside the amendment's own scope. Every refusal of a legitimate spelling holds a `..` part, which the amendment refuses by design (§8, I2).

**Misses:** none. The amendment says that without a `..` part, the text names the entry the kernel opens. That holds on every shape I tried:
- **Why it holds:** without `..`, the path only walks down. Every part that does not exist yet comes after the last part that exists. So any link on the path already exists at check time and resolves the same way at write time. `os.makedirs` creates only parts named in the `--out` text, never a part inside a link's target.
- **Links whose target text holds `..`** (a6 to a11, a18): the tests saw the entry the kernel opened.
- **a11's target holds a missing part, then `..`:** the kernel cannot resolve it, so the write fails and nothing is written.
- **"A `..` that only a later link would introduce"** therefore needs the link to change between check and write. That is the race in §8, I8.

## 6. Ask 6: new mutants

Each mutant is one exact edit in a full scratch copy of the PIN (`<W>/mut4`), restored from `pded` between runs. The final restore is checked by hash: `end: view.py restored e7bb13b4fd54016b == pded e7bb13b4fd54016b`. Scoring follows AF-AP-223: KILLED needs a FAILED test at a total of 102.

**The baseline is 102 passed.** The red control puts 6c14466f's `view.py` under the new tests: 8 failed, 94 passed. The 8 are the four `dotdot` forms of `test_an_out_that_is_a_link_after_a_dotdot_is_refused` and the `m1`, `m4`, `d1`, `d2` cases of `test_an_out_with_a_missing_part_before_a_dotdot_is_refused`. The dots control passes on the old view, as a control on over-refusal should.

| id | edit | result | what kills it, or why it survives |
|---|---|---|---|
| X1 | delete the rule | KILLED: 8 failed, 94 passed | the same 8 |
| X2 | `".." in out` (substring) | KILLED: 2 failed, 100 passed | the dots control: `[v..1]`, `[...]` |
| X3 | `out.split("/")[-1] == ".."` | KILLED: 7 failed, 95 passed | the four `dotdot` forms; m1, m4, d1 |
| X4 | `".." in out.split("/")[:-1]` | KILLED: 1 failed, 101 passed | d2 |
| X5 | the rule moved after the link tests | KILLED: 4 failed, 98 passed | the four `dotdot` forms (now "is a symbolic link") |
| X6 | the rule moved after the D-6 test | KILLED: 4 failed, 98 passed | the four `dotdot` forms |
| X7 | `split(os.sep)` | SURVIVED: 102 passed | equivalent: `os.sep` is `/` |
| X8 | `"."` in place of `".."` | KILLED: 7 failed, 95 passed | `symbolic_link[link-dot]`; `dotdot`, `dotdot-slash`; m1, m4, d1, d2 |
| X9 | `not in` | INVALID (error-only): 26 passed, 76 errors | every normal `--out` is refused, so the shared `world` fixture errors at setup |
| X10 | parts stripped of blanks | SURVIVED: 102 passed | **real survivor:** a14 (`.. `) and a20 (` ..`) go from rc=0 to rc=2, an over-refusal |
| X11 | `rstrip("/")` before the split | SURVIVED: 102 passed | equivalent: a trailing `""` part is never `..` |
| X12 | `normpath` before the split | KILLED: 8 failed, 94 passed | the same 8 |
| X13 | the rule for an absolute `--out` only | SURVIVED: 102 passed | **real survivor:** reopens B2 and B1 for relative paths (below) |
| X14 | skip the first part (`[1:]`) | SURVIVED: 102 passed | **real survivor:** a4 (`../Z0new`) goes from rc=2 to rc=0 |
| X15 | `count("..") > 1` | KILLED: 6 failed, 96 passed | the four `dotdot` forms; d1, d2 |
| X16 | (old line) drop the abspath test | SURVIVED: 102 passed | equivalent while the rule stands (below) |
| X17 | (old line) drop the named-entry test | SURVIVED: 102 passed | equivalent while the rule stands (below) |

**X13 through the CLI** (`python3 mut4.py apply X13`, then `python3 b1r4.py pded mut4 ...`):
```
a21  rel missing/../E, cwd F                  rc=0 |
       new=['missing'] changed=['E/summary.json', 'E/view.jsonl'] gone=[] git=[('E/view.jsonl', 'no')]
a22  rel C/hop/missing/../../link, cwd F      rc=0 |
       new=['B/sub/missing', 'T/summary.json', 'T/view.jsonl'] changed=[] gone=[] git=[('T/view.jsonl', 'no')]
a4   rel ../Z0new, cwd Z0                     rc=0 |
       new=['Z0new', 'Z0new/summary.json', 'Z0new/view.jsonl'] changed=[] gone=[] git=[('Z0new/view.jsonl', 'no')]
```
m1, d1, m7 and s4 stay at rc=2 under X13.

**X14 through the CLI:** a4 exits 0 and writes `Z0new/`. a5, s4, a21 and m1 stay at rc=2.

**X16 and X17 through the CLI.** On l1, l2, s5, a6 to a11, a18, e2 and n1, each gives the same exit code and writes as the PIN. The reason: with no `..` part, `abspath` only removes `.` and `//` parts, and `getcwd` is physical. So `islink(named)` equals `islink(abspath(out))`.

## 7. Finding inventory

**F1. FOLLOW-UP: no test runs a relative `--out` with a `..` part.**
- Evidence: reproduced (§6, X13).
- Contract: the D-10 and D-6 amendments (the rule's own tests).
- Canonical path: the CLI.
- Effect: with relative paths exempt, a relative `missing/../E` replaces a full directory's `view.jsonl` and `summary.json` (B2), and a relative `C/hop/missing/../../link` writes through a link (B1). All 102 tests still pass.
- Fix: add a relative case to `test_an_out_with_a_missing_part_before_a_dotdot_is_refused`, for example cwd `tmp_path` with `--out f/missing/../e`.
- Why it does not block: the code at the PIN refuses both shapes (a21, a22).

**F2. FOLLOW-UP: no test has a leading `..` part.**
- X14 survives: `../x` is accepted.
- The kernel resolves a leading `..` exactly (the cwd is physical and exists), so the effect is small. But it breaks the amended text: "an `--out` with a `..` part".
- Fix: add a4's shape (`../new` from a cwd). That case also kills X13.

**F3. FOLLOW-UP (minor): no test that `.. ` or ` ..` is an ordinary name.**
- X10 survives and over-refuses them (fail-closed).
- Fix: add both to the dots control's parameters.

**F4. FOLLOW-UP (minor): stale text.**
- The `--out` help at view.py:425 ("a new or empty directory, not a symbolic link, outside git") and the module docstring's usage at view.py:44-45 do not mention the `..` rule.
- The refusal reason itself is clear.

**I1. INFO: the two link tests now duplicate each other** (X16 and X17 are equivalent). Either test, or round 3's named-entry loop, can go with no change in behaviour. Keeping both is harmless.

**I2. INFO: refusals by design.** Every legitimate spelling with a `..` part now exits 2: relative `../x`, `x/..`, `link/..`, o1 and s4. The amendment chose this. The reason names the part.

**I3. INFO: links whose target text holds `..` are outside the rule's text scope.** I measured them consistent (a6 to a11, a18, and §5's argument). The parent-link writes (a7, a10) land where D-10 allows.

**I4. INFO: NUL cases.** All exit 2 with nothing written. The reason depends on the part (§5). On Python 3.11 the interpreter's text is "embedded null byte"; the NUL tests match "embedded null".

**I5. INFO: X9 is INVALID (error-only), not a survivor.**

**I6. INFO: the redesign also closes four more round-3 writes** that my round-3 report did not list:
- a16 and a23 wrote into a full directory with no link at all (B2's shape);
- a21 and a22 are B2 and B1 through relative paths.

**I7. INFO: a limit of my own probe.** At 6c14466f, a2 (`F//..//E`) wrote into a new directory `<base>/E`, outside the snapshot root F. I confirmed it with `ls` (it holds `summary.json` and `view.jsonl`). The snapshot alone did not show it. At the PIN, a2 is refused before any write, and no `<base>/E` exists in that run.

**I8. INFO (static): the race window is unchanged.** `check_out` tests the path and then opens it by name, the AF-AP-70 class. A link swapped in between the two would get through. That needs a concurrent actor, so it is hypothetical; I did not reproduce it.

**I9. INFO: HEAD moved twice during my rounds** (e4b894e1, then the coordinator's next local commit, both after the PIN). The three subject files stayed byte-identical to the PIN.

**I10. INFO, for the D-115 round table.** Round 4 closes the class by construction: one text rule replaces the path-walk emulation. No blocker remains within D-134's one-round budget.

## 8. Blocking predicate (demand 5)

**No finding contradicts a frozen D-rule as amended (D-6, D-10):**
- every `..` spelling exits 2 with nothing written and no directory made;
- without a `..` part, the link, git and emptiness checks held on every shape tried.

**No finding shows the headline claim false.** No output went inside a git work tree; git said "no" for every output that landed. This round did not touch the D-8 rows, the candidate, or the label and split.

**F1 to F4 are follow-ups:**
- F1 to F3 are test gaps. The code at the PIN refuses or accepts each of those shapes correctly.
- F4 is documentation text.

There is no CONTRACT-DEFECT and no CONTRACT-INVALID.

## 9. Gate recommendation

- **B1: FIXED.** The four `hop/../link` forms, every round-3 B1 spelling (m1 to m7, the s rows, x1, c1, c3) and the relative variant a22 exit 2 with nothing written.
- **B2: FIXED.** d1, d2, m4, a16, a23 and the relative variant a21 exit 2, and the older outputs are untouched.
- **The round: MERGE-READY-WITH-FOLLOWUPS.** Follow-ups F1 (the important one), F2, F3 and F4. I reproduced everything this verdict depends on. I did not check CI for ded4af91 (no network); that gate is the coordinator's.

## 10. What I did not do, and hygiene

**Not done:**
- Check CI (no network).
- Run under Python 3.13 (no pytest for it here).
- Use the PC or the bridge.
- Reproduce I8's race.
- Test write failures after `makedirs` has made a parent: a too-long final name could leave that parent behind. That is outside this diff and untested.
- Grade task #468.

**Repo hygiene:**
- I touched no tracked file in `/home/user/agent-factory`; `git status` of the three subject files is empty. No commit, stash, checkout or reset.
- No network, bridge, subagent or background job.
- I read nothing forbidden. A hook pushed a summary of a `.jev` filepack into my context; I did not open the file.
- All fixture text is fake and built at run time.

**Scratch:**
- **Kept:** `<W>/pded` (the PIN), `<W>/p6c` (6c14466f) and `<W>/pin` (0555298e).
- **Deleted:** `<W>/mut4`, `mbt4`, `bt`, and the run directories.

**Files:**
- `<W>/b1r4.py`: the sweep, the attacks and the NUL cases; `b1r4.py <fixture tree> <cli tree> [keys]`.
- `<W>/mut4.py`: the mutants; it re-creates its copy when needed.
- `<W>/q4.py`: the Q4 table.
- `<W>/premise4.sh`: the premise block.
- Outputs: `<W>/premise4-end.txt`, `<W>/q4-pded.txt`, `<W>/q4-p6c.txt`, `<W>/mut4-first.log`.
- `<W>/h.py`: the fixture harness.

## Coordinator's harvest notes (2026-10-02 12:4xZ)

- The report is the lane's final message for round 4, whole (the harvest's report window opens at the resume message). The hand-back was absent (task #426), so the local-id, known-value and canary checks ran by hand: no known value, no canary.
- Two citations of the coordinator's local commit, which `scripts/push_clean.sh` rewrites at the push, are rephrased without its id (sections 1 and 7, I9).
