# T268-269 report (tasks #268 and #269)

**TL;DR: DONE in the sandbox. Both tools are built, installed in `scripts/` by one atomic rename each, and gated on the
installed files: `248 passed` twice (set `cef2ce39b9ab`). Red first on the PIN: `21 failed, 20 passed, 55 errors`.
Mutation audit: 23 of 24 mutants killed; the one survivor is declared. Nothing is committed (the coordinator commits).
The gate recommendation is not mine.**

Lane: code-implementer (sandbox, Opus 5.5). Started 2026-09-25 11:2xZ, finished 2026-09-25 12:0xZ (both from `date -u`).
PIN 157ddd6; local head at start feeaea5. No subagent, no git write, no fetch or push, no PC bridge, no secret file read;
`push_clean.sh` and `ci_gate.py` were never run for real (only the existing `tests/test_ci_gate.py` suite, which drives
push_clean against a throwaway origin, as the brief's gate list demands).

WARNING for the coordinator: this report names the tokens literally. Do not run `scripts/stamp_fill.py` on it, and do
not paste the literal tokens into a `safe_commit.sh -m` message or an `anchor_edit.py` NEW/TEXT value: both are always
filled (section 7, DEV-4).

## 0. The brief's question: how the temp-repo test runs the real hook against the real checker

In `tests/test_safe_commit.py`, fixture `def repo` (tests/test_safe_commit.py:43):
- the throwaway repo's `core.hooksPath` (tests/test_safe_commit.py:55) is a temp dir that holds only `commit-msg`, a
  `symlink_to` the tree's own `scripts/hooks/commit-msg` (tests/test_safe_commit.py:46);
- the throwaway repo holds `scripts/stamp_check.py`, a `symlink_to` the tree's own checker (tests/test_safe_commit.py:50),
  hidden by `.git/info/exclude`. The hook computes `git rev-parse --show-toplevel` (scripts/hooks/commit-msg:6) and runs
  `$REPO_ROOT/scripts/stamp_check.py` (scripts/hooks/commit-msg:13), so it reaches the real checker through that link.

Symlinks, not copies: the bytes under test are the tree's own and cannot drift from them. Only `commit-msg` is installed,
because the real pre-commit and post-commit hooks would run lint_delta and the re-index inside the throwaway repo.
Both instruments are proven to have fired. The negative control asserts the checker's own line
(`stamp_check: the commit message: '<stamp>' is `), then the hook's line, and that HEAD did not move:
`COMMIT BLOCKED by the future-stamp gate on the message` (tests/test_safe_commit.py:88).
The paired positive (a past stamp) commits.
Mutant M8 (`git commit --no-verify`) turns the negative control red.

The typed stamp is a DATED bucket a day ahead, not a bare subject bucket like the brief's `wiki 12:0xZ` example. The
checker places a bare subject stamp on the clock's own date:
`now.replace`, then `timedelta(days=1)` (scripts/stamp_check.py:95-97).
So from 23:40Z to midnight, no bare bucket at least ten minutes ahead exists, and a bare
control would fail on the clock. A dated stamp is refused at any hour. `tests/test_stamp_check.py` covers the
bare-subject rule itself with a fixed `--now`.

## 1. Premise re-measure

MATCHES the brief (verified, this session, 2026-09-25 11:2xZ):

```
git show 157ddd6:<f> | sha256sum | cut -c1-16  -> 7e940ee7e8f53ccc safe_commit.sh, c100403a513613a5 anchor_edit.py,
                                                  c009e29845a85781 stamp.sh, 8d7c68441d4cd9c3 tests/test_anchor_edit.py
working copy of the same four files             -> identical hashes
git diff --quiet 157ddd6 HEAD -- <4 files> ci_gate.py push_clean.sh   -> rc 0
git diff --quiet HEAD -- <same 6>                                       -> rc 0
grep -c STAMP safe_commit.sh anchor_edit.py     -> 0, 0
bash scripts/stamp.sh                           -> 2026-09-25 11:2xZ
gitnexus markers                                -> CLAUDE.md lines 765 and 809, AGENTS.md lines 375 and 419
sed -n 33p scripts/ci_gate.py                   -> Exit codes: 0 allow . 1 refused ... 2 cannot decide . 64 usage . 75 wait
scripts/push_when_green.sh, scripts/stamp_fill.py -> absent
```

Facts read for the design (verified by reading, this session):
- `scripts/safe_commit.sh` is listed in `scripts/gate_files.txt:24`, so `no_laya_in_gates.py` screens its text on every
  commit (vocabulary, no `source` or `.` command, shell that parses in sync). The new lines pass it (section 5).
- The completeness walk of `no_laya_in_gates.py` covers only hooks, workflows and proof checkers
  (`def _glob_structural`), so the two new scripts need no listing.
- Scratch and `scripts/` sit on one filesystem (device 65024), so a `mv` from scratch into `scripts/` is one rename(2).
- The banner guard's premise is VERIFIED from primary source. GitNexus 1.6.10 (lines 239-300 of
  dist/cli/ai-context.js in the installed package) rewrites a file as `before + section + after`, where `before` and
  `after` are the text outside the markers, then applies `.trim() + '\n'` to the whole file. Both real files start with
  `#` and end with exactly one newline after `<!-- gitnexus:end -->`, so that trim changes nothing outside the block.
  History: commit 6289ab6 changed only the AGENTS.md block. Most commits that touch the two files mix rule edits with
  the churn, so history alone does not isolate the churn shape.

## 2. #268: what was built (files and lines, as installed)

- `scripts/stamp.sh` (MODIFY):
  - A new `-b` arm prints the bare bucket: `date -u '+%H:%M'` read once (scripts/stamp.sh:12).
  - The default arm now reads the clock once: `date -u '+%Y-%m-%d %H:%M'` (scripts/stamp.sh:13). It used to make
    three `date` calls (date, hour, minute). Its output format is unchanged.
  - The exact mode (-x) is unchanged: `date -u +%Y-%m-%dT%H:%M:%SZ` (scripts/stamp.sh:11).
  - The header names the two tokens (section 7, DEV-1).
- `scripts/stamp_fill.py` (CREATE, 77 lines, mode 755) holds the one Python computation:
  - `def clock` (scripts/stamp_fill.py:30), `def stamps` (scripts/stamp_fill.py:35).
  - `def fill` (scripts/stamp_fill.py:41), `def main` (scripts/stamp_fill.py:50).
  - The CLI reads and decodes (UTF-8) every FILE before it writes any: `for path in paths:` (scripts/stamp_fill.py:57)
    feeds `planned.append` (scripts/stamp_fill.py:64).
  - A file with no token is never written: `if not count:` (scripts/stamp_fill.py:67).
  - It prints one line per file with its count. rc 2: refused, nothing written. rc 64: usage.
  - It does binary I/O, so the bytes around a token (line endings included) stay as they are.
- `scripts/anchor_edit.py` (MODIFY):
  - It loads `stamp_fill.py` from beside itself with `spec_from_file_location` (scripts/anchor_edit.py:27), the way
    ap_screen.py loads its hook.
  - One `stamp_fill.clock()` read serves every token of a run (scripts/anchor_edit.py:60).
  - Only NEW and TEXT are filled, through `stamp_fill.fill` (scripts/anchor_edit.py:67), after the `@file` read.
    OLD and PREFIX go through `anchor = _val(argv[i + 1])` (scripts/anchor_edit.py:66) and are never filled.
  - When at least one token was filled, it prints one more line, `N stamp token(s) filled from the clock (<dated>)`,
    under `if filled:` (scripts/anchor_edit.py:84).
  - `plan()` and the all-or-nothing path are unchanged.
- `scripts/safe_commit.sh` (MODIFY): the new block applies only when the message holds a token:
  `case "$MSG" in` (scripts/safe_commit.sh:17).
  - It runs stamp.sh once, `DS=$(bash "$(dirname "$0")/stamp.sh")` (scripts/safe_commit.sh:19).
  - A format check refuses with rc 1 and `nothing staged` (scripts/safe_commit.sh:20-21).
  - It fills `{DATESTAMP}`, then fills `{STAMP}` with the time part of the same stamp (scripts/safe_commit.sh:22-23).
  - It prints one line, `stamp tokens filled from the clock` (scripts/safe_commit.sh:24).
  - The block runs before the staged-index guard and before `git add`, so a refusal leaves the index as it was.
  - A message without a token never runs stamp.sh, so a broken stamp.sh cannot stop an ordinary commit (test pinned).

Diff stat of the four MODIFY files (verbatim):
```
 scripts/anchor_edit.py    | 20 ++++++++++-
 scripts/safe_commit.sh    | 14 ++++++++
 scripts/stamp.sh          | 10 ++++--
 tests/test_anchor_edit.py | 84 ++++++++++++++++++++++++++++++++++++++++++++++-
 4 files changed, 124 insertions(+), 4 deletions(-)
```

## 3. #269: what was built

`scripts/push_when_green.sh` (CREATE, 132 lines, mode 755):
- The header (lines 1-28) states the contract, the exit codes and the background use. In Claude Code: the Bash tool
  with `run_in_background: true`. In a shell: `setsid nohup bash scripts/push_when_green.sh > /tmp/push_when_green.log
  2>&1 < /dev/null &`.
- Arguments: `WAIT=1700` (scripts/push_when_green.sh:35). `--wait` takes whole seconds only; at most one mode flag;
  anything else exits 64.
- The script moves to the top of the tree: `git rev-parse --show-toplevel` (scripts/push_when_green.sh:47).
- A detached HEAD with no PUSH_BRANCH refuses with rc 64: `HEAD is detached` (scripts/push_when_green.sh:49).
- Step 1: `ci_gate.py` with `--branch "$B" --wait "$WAIT"` (scripts/push_when_green.sh:53). rc 0 goes on. Any other rc
  is the script's exit, and nothing is fetched or pushed.
- Step 2, the banner guard:
  - `BANNER_PY` (scripts/push_when_green.sh:66) compares the text outside the block byte for byte, so a trailing
    newline counts.
  - HEAD is resolved once, `HEAD^{commit}` (scripts/push_when_green.sh:84), the fix shape of AF-AP-175.
  - Both files are judged before either is restored.
  - A refusal prints one line per file, restores nothing, and exits with `exit 65` (scripts/push_when_green.sh:94).
  - The restore is `git checkout --` (scripts/push_when_green.sh:97). It restores from the index and never changes the
    index.
- Step 3, the mode: a flag wins. With no flag, `--lanes-live` is chosen only when two things hold. First, the awk count
  over `.lanes-live` (scripts/push_when_green.sh:108) finds at least one path; it reads the set push_clean reads
  (lines that are not empty and do not start with `#`, a last line without a newline included). Second, `git status
  --porcelain --untracked-files=no` is not empty. Otherwise the mode is `--no-delegates-live`, and the line names the
  reason.
- Step 4: `git fetch -q origin` (scripts/push_when_green.sh:123); a failed fetch exits with its rc.
  Then `push_clean.sh` with `PUSH_BRANCH="$B"` and the mode (scripts/push_when_green.sh:126).
  Its rc is the exit: `exit "$rc"` (scripts/push_when_green.sh:132).
- It sets none of CI_FIX, CI_WAIT_SKIP or CI_GATE_OFFLINE. A caller's own values reach both calls unchanged (test
  pinned; `ci_gate.py --wait` ignores them).

The log of a green run, one line per step (verbatim, pinned by
`test_green_pushes_exactly_once_after_the_fetch_with_one_line_per_step`):
```
push_when_green: [1/4] ci_gate.py --wait allows the push of feat (rc 0)
push_when_green: [2/4] banner guard: AGENTS.md and CLAUDE.md match HEAD
push_when_green: [3/4] mode --no-delegates-live (auto: no .lanes-live)
push_when_green: [4/4] fetched origin/feat; push_clean.sh --no-delegates-live exited rc 0
```

## 4. Tests: red first, then green

New test files: `tests/test_stamp_sh.py` (4 tests), `tests/test_stamp_fill.py` (16), `tests/test_safe_commit.py` (10),
`tests/test_push_when_green.py` (50). `tests/test_anchor_edit.py` gains 6, for 17 in all. All of them are
deterministic and LLM-free. The git repos live under pytest's tmp_path. Every git call runs with all `GIT_*` variables
dropped and the global and system config off, so no case can reach this repo's index.

The push_when_green tests put fake `ci_gate.py` and `push_clean.sh` files beside a copy of the real script in a temp
repo: `FAKE_GATE` (tests/test_push_when_green.py:26) and `FAKE_PUSH` (tests/test_push_when_green.py:32). The script
resolves both from its own directory, so production code carries no seam. Before each run a second clone moves origin
ahead: `origin moves ahead` (tests/test_push_when_green.py:76). The fake push_clean records `refs/remotes/origin/feat` at call time, which
proves the fetch ran before the push.

The clock oracle is `date -u` piped through the rule's own formula. It is read before and after each run, and the tool's
bucket must equal one of the two readings.

RED on the PIN's files. The scratch copy `t268/lane/red` is `git archive 157ddd6 scripts tests pyproject.toml` plus the
five new or changed test files. Its three live scripts were byte-compared equal to the repo's:

```
$ bash scripts/test_summary.sh tests/test_anchor_edit.py tests/test_stamp_sh.py tests/test_stamp_fill.py tests/test_safe_commit.py tests/test_push_when_green.py
pytest-exit: 1
pytest-summary: 21 failed, 20 passed, 55 errors in 3.22s
```

Why each red is red (from `pytest -rfE` on the same copy):
- anchor_edit fill tests (2): the file keeps the literal tokens. The one-clock-read test fails with
  `AttributeError: module 'anchor_edit' has no attribute 'stamp_fill'`.
- stamp.sh `-b` tests (2): the PIN's `-b` falls to the default arm and prints `2026-09-25 11:4xZ`.
- safe_commit: the message kept `wiki {STAMP}: the tokens`. The five bad-stamp.sh cases committed (`== staged set ==`,
  rc 0), because the PIN never reads stamp.sh.
- stamp_fill (all) and push_when_green (all): `No such file or directory` for the two new scripts.

The 20 that pass on the PIN are the 11 existing anchor_edit tests and 9 regression guards, green by design:
- anchor_edit: OLD and PREFIX never filled; a refused run writes nothing; a run with no token reports no fill.
- stamp.sh: the default mode and `-x`.
- safe_commit: a typed future stamp refused by the real gate; file content never filled; a token-free message committed
  as given; the staged-index guard.

GREEN on my files, before installing: the same PIN copy plus the five dev scripts and the tests gave `96 passed in
7.91s` (pytest -q). One test was added after that, because mutant M20 needs it:
`test_two_blocks_in_head_are_ambiguous_and_refuse` (tests/test_push_when_green.py:175).
Then `50 passed in 6.91s` for that file on the copy. That test is red on the PIN copy too (`1 error`, the missing
script). The same five-file set (`5 files set=014297013fab`) on the installed files: `pytest-summary: 97 passed in
7.56s` (96 in the red run plus that test).

Mutation audit (scratch copies of the green tree only, driver `t268/lane/mutate.py`). An anchor that does not match
exactly once voids its mutant. Result: **23 killed of 24, 0 void.**
- anchor_edit: M1 fills OLD/PREFIX too; M2 reads the clock per op; M3 leaves insert TEXT unfilled.
- stamp_fill: M4 rewrites a token-free file; M5 writes while still reading; M6 keeps the minute digit.
- stamp.sh: M7 `-b` cuts two characters.
- safe_commit: M8 `--no-verify`; M9 fills file content; M10 drops the stamp format check; M11 fills {STAMP} with the
  dated form.
- push_when_green: M12 pushes on rc 75; M13 compare blind to the final newline; M14 restores before judging both
  files; M15 auto mode ignores the tracked-change condition; M16 counts untracked files; M17 picks the mode before the
  guard; M18 no fetch; M19 sets CI_WAIT_SKIP; M20 accepts any marker count; M21 judges identical files; M22 no cd to
  the top; M23 wait default 1800.

**SURVIVED (expected, declared): M24, a guard that names HEAD in each read instead of the one resolved SHA.** No test
moves HEAD between the guard's reads (that needs a PATH shim or a hook into the script), so the single snapshot is
verified by reading only (section 6).

## 5. Gates on the installed files (verbatim)

After each install (section 10), I re-ran that file's tests on the INSTALLED file. The scratch tree `t268/lane/inst`
holds the dev tests, with `scripts/` entries symlinked to the repo's installed files:
- `stamp.sh`: `4 passed`
- `stamp_fill.py`: `20 passed` (with test_stamp_sh)
- `anchor_edit.py`: `17 passed`, plus one live fill: `row one {STAMP} {DATESTAMP}` became `row one 11:5xZ
  2026-09-25 11:5xZ`
- `safe_commit.sh`: `10 passed`
- `push_when_green.sh`: `50 passed`

Then the brief's gate in the repo, twice, in one foreground call:
```
$ bash scripts/pc_suite.sh set-id -- tests/test_anchor_edit.py tests/test_stamp_check.py tests/test_ci_gate.py tests/test_stamp_sh.py tests/test_stamp_fill.py tests/test_safe_commit.py tests/test_push_when_green.py
7 files set=cef2ce39b9ab
== run 1 11:58:38Z ==
pytest-exit: 0
pytest-summary: 248 passed in 21.20s
== run 2 11:58:59Z ==
pytest-exit: 0
pytest-summary: 248 passed in 21.27s
```
Cross-check with the premise's own set (162 at the premise, plus the 6 new anchor_edit tests):
```
3 files set=c49303b1b136
pytest-summary: 168 passed in 13.66s
```
Adjacent consumers: `test_lane_context_output.py` feeds `scripts/anchor_edit.py` to lane_context; `test_search_intercept`
matches the safe_commit command string; `test_no_laya_in_gates` and `test_shell_syntax` cover the gate list:
```
4 files set=86bd591356a9
pytest-exit: 0
pytest-summary: 229 passed in 49.00s
```
Static checks:
- pyflakes on `scripts/stamp_fill.py`, `scripts/anchor_edit.py` and the five test files: rc 0.
- `bash -n` on `scripts/stamp.sh`, `scripts/safe_commit.sh`, `scripts/push_when_green.sh`: rc 0 each.
- The U+2028/U+2029 byte check (`LC_ALL=C grep -c` for the byte pairs e2 80 a8 and e2 80 a9) printed 0 for each of the
  eleven files I wrote, this report included.
- `python3 scripts/no_laya_in_gates.py` over the real tree, on disk: `no_laya_in_gates: 41 files scanned, clean`,
  rc 0. The new `safe_commit.sh` alone, in a one-entry list: `1 files scanned, clean`.
- `python3 scripts/report_lint.py` on this report with `--min-refs 20`, two rounds: `54 refs — OK 54, NEAR 0, MISS 0,
  UNCHECKABLE 0, UNRESOLVED 0 (worktree)`, rc 0.
- `python3 scripts/ap_screen.py` (advisory): one AF-AP-175 hit at scripts/push_when_green.sh:84 (`HEAD^{commit}`),
  which is the row's own fix shape (section 7, ADJ-2); 0 hits on the two Python files.

## 6. NOT-done (first-class)

1. No test moves HEAD between the banner guard's reads (mutant M24 survives). The single snapshot is verified by
   reading only.
2. No live run of push_when_green against the real origin and CI; the brief forbids it. Its first real use is the
   coordinator's.
3. The background-use instructions in the header are written, not exercised. A test pins only their presence.
4. stamp.sh's single clock read: its format is tested against the clock. Freedom from the boundary race is by
   construction, not tested (no clock seam, by design).
5. No bare-subject future-stamp control through the real hook (section 0 explains why).
6. The proposed anti-pattern registry row for the stamp.sh defect is NOT written: `docs/INCIDENT-LOG.md` is outside
   my boundary (section 7, DEV-1).
7. No commit, no ledger or wiki update, no CLAUDE.md or AGENTS.md text: the coordinator's, per the brief.

## 7. DISCREPANCIES, deviations and adjacent findings

- **DEV-1 (in boundary, beyond the contract's letter): stamp.sh's default mode now reads the clock once;** its output
  format is unchanged.
  - The defect: the old default arm made three `date` calls (date, hour, minute). At an hour or day boundary the parts
    could come from two instants, and the stamp could be up to a day in the past. It could never be ahead, so the
    future-stamp gate cannot see it.
  - Why I fixed it: every filler takes its text from this script, so I fixed it with the new bare mode.
  - bug-echo pass: by hand, no subagents; its report is not written to `.agents/research/` (outside the boundary).
    The pattern validated against the PIN's `stamp.sh` line 7. A broadened sweep over `scripts/`, `harness-ports/`,
    `proofs/`, `src/` and `.claude/hooks/` found 7 candidates. I read every site; all 7 are OK, with no echo:
    - `date -u +%Y%m%dT%H%M%SZ` (scripts/gpu_window.sh:65): one read.
    - `MIX_FROM` (scripts/pc_lane.sh:479-480): a from/to range; FROM derives from the stored launch time.
    - `STALE_FAILED` (harness-ports/bin/pc-lane.sh:136): the file mtime, or one clock read as a fallback.
    - `time.time()` (scripts/gn_mcp.py:40 and scripts/ooo_mcp.py:49): poll deadlines, not stamps.
    - `date -u '+%H:%M'` (scripts/stamp.sh:11-12): the fixed site itself.
  - PROPOSED registry row, for the coordinator to write: "A STAMP BUILT FROM SEPARATE CLOCK READS: date, hour and
    minute read by separate calls straddle a boundary and print a stamp up to a day old, never ahead, so the
    future-stamp gate cannot see it. Signature: two or more `date` or `now()` calls whose fields form one stamp. Fix:
    read the clock once and format once (scripts/stamp.sh, 2026-09-25, T268)."
- **DEV-2: safe_commit takes BOTH texts from ONE stamp.sh run.** `{STAMP}` is the time part of the dated stamp, not a
  second `stamp.sh -b` run: two runs could straddle a ten-minute boundary and give one message two buckets.
  `test_b_is_the_time_part_of_the_default` holds `-b` equal to that time part, and mutant M11 proves the fill test tells
  the two forms apart.
- **DEV-3: anchor_edit.py now loads stamp_fill.py at import.** A copy of anchor_edit.py without its sibling fails at
  import for every use, with or without a token. I chose this over a second Python copy of the computation (the brief
  allows either). For the same reason, stamp_fill.py was installed before anchor_edit.py.
- **DEV-4, a gap in the contract (not a code defect): a literal token can no longer pass through safe_commit's message
  or anchor_edit's NEW/TEXT.** Both are always filled, and no escape exists: none was specified, so none was added. The
  harvest commit message and any ledger text that documents these tools must spell the tokens another way (for
  example "the STAMP token", without braces), or they will be filled. stamp_fill fills only files named by hand.
- **DEV-5: the banner guard is conservative.** It refuses (rc 65) whenever AGENTS.md or CLAUDE.md carries any edit
  outside the block, including one a declared lane owns under `--lanes-live` (the contract: "a difference anywhere else
  REFUSES"). It also refuses a CRLF marker line and a file with two marker pairs, where GitNexus would take the first
  pair. The rule is: ambiguous means refuse, and nothing is restored.
- **DEV-6: two waits follow the contract's order and are narrowed, not closed.**
  - The fetch (step 4) runs after the banner guard. A GitNexus re-index that lands between the guard and push_clean's
    clean check still makes push_clean refuse: fail-closed, the race CLAUDE.md already documents.
  - `ci_gate.py --wait` reads the local origin ref and never fetches. After the wait, the fetch and push_clean's own
    gate decide, and a 75 there exits 75.
- **ADJ-1 (pre-existing, adjacent, NOT fixed):** after a commit that a hook refuses (for example the stamp gate),
  safe_commit leaves the named paths staged. The next safe_commit run then refuses with `REFUSED: index already carries
  staged entries (a delegate's?)`, naming the coordinator's own paths. Clear them with `git reset -q -- <paths>`; my
  test does exactly that between its negative and its positive control.
- **ADJ-2 (advisory screen):** the one AF-AP-175 hit, `HEAD^{commit}` (scripts/push_when_green.sh:84), is
  the registry's own recommended fix. The pre-commit hook will print it (advisory, never blocking). This is the line-form limit already
  noted under issue #65.
- **ADJ-3 (inferred by reading, NOT reproduced):** with a detached HEAD and no PUSH_BRANCH, push_clean.sh computes
  `PUSH_BRANCH` or else `git rev-parse --abbrev-ref HEAD` (scripts/push_clean.sh:14), which prints `HEAD`, so the
  branch it fetches and pushes is named `HEAD`. push_when_green refuses that case itself (rc 64). push_clean.sh is
  untouched (outside the boundary).

## 8. Self-attack: the three most likely ways this change is wrong

1. **The banner guard discards an unsaved edit.** The restore is the only destructive act in #269. Ruled out:
   - The comparison is byte-exact over the text outside the block; M13 (blind to the final newline) is killed.
   - Both files are judged before either is restored (M14 killed), and the guard needs exactly one marker pair (M20
     killed).
   - Eight outside-edit shapes on each of the two files are covered, plus a deleted file and two blocks in HEAD.
   - The restore is `git checkout --` from the index and never changes the index. The guard has already proven that
     the working copy equals HEAD outside the block, so the restore can only drop in-block churn.
   - The churn premise is verified from GitNexus's own writer.
   - Residuals, declared: a ms window between the judgment and the checkout (an edit saved exactly then would be
     lost), and the single HEAD snapshot, verified by reading only (M24).
2. **safe_commit's fill lets a future stamp through, or breaks ordinary commits.** safe_commit is used many times a day.
   Ruled out:
   - The negative control runs the REAL hook against the REAL checker (refused, HEAD unchanged; M8 killed).
   - A message with no token is committed byte for byte and never runs stamp.sh.
   - The fill runs before staging, so a refusal leaves the index clean.
   - The format check refuses five kinds of bad stamp.sh output (M10 killed).
   - The quoted pattern substitution was measured on this bash (5.2.21, `patsub_replacement` on): `&`, backslashes
     and newlines pass through.
   - The never-a-gate screen is clean over all 41 listed files.
3. **The install left a live tool half-written, or changed behavior for existing callers.** Ruled out:
   - Before each install, a compare-and-swap check confirmed the repo file still held the PIN's bytes.
   - Each install was one rename(2), proven by the kept inode.
   - The existing 11 anchor_edit tests and the stamp_check and ci_gate suites pass on the installed files (168 and 248
     passed).
   - A run with no token keeps its output byte for byte: `test_a_run_without_a_token_reports_no_fill` pins stdout.

## 9. Evidence tiers

- **Verified (this session):**
  - the premise;
  - red first on the PIN copy: `21 failed, 20 passed, 55 errors`;
  - green on the copies: `96 passed`;
  - mutation audit: 23 of 24 killed;
  - the tests after each install;
  - the gate: `248 passed` twice (set `cef2ce39b9ab`); the premise set `168 passed` (`c49303b1b136`); the adjacent
    suites `229 passed` (`86bd591356a9`);
  - pyflakes and `bash -n` rc 0; the separator bytes 0;
  - the never-a-gate screen clean;
  - the atomic renames (inodes kept);
  - GitNexus's writer read from its source;
  - the bug-echo sweep: 7 sites read, 0 echoes.
- **Inferred:**
  - that stamp.sh's single read removes the boundary race;
  - the guard's single HEAD snapshot;
  - ADJ-3;
  - that the background recipes work as written.
- **Assumed:** that the coordinator runs push_when_green from a clone whose `origin` is the GitHub remote. ci_gate reads
  the Actions API only for a github.com origin.

## 10. Install record (the ORDERING section)

Every change was developed and tested on scratch copies (`t268/lane/dev`, `green`). Each install then ran the same
five steps:
1. check that the repo file still held the PIN's bytes (or was absent);
2. stage the new file with its mode in scratch;
3. make ONE `mv`, a rename(2) on the same filesystem;
4. check that the installed file kept the staged file's inode;
5. `cmp` the installed file against the dev copy, then re-run its tests on the installed file.

The installed files were never in a half-written state.

```
installed scripts/stamp.sh: c009e29845a85781 -> 1e4f26cf694182b9, mode 755, inode 3179554 kept (one rename)
installed scripts/stamp_fill.py: absent -> ed5ac2e73e71d6e9, mode 755, inode 3179955 kept (one rename)
installed scripts/anchor_edit.py: c100403a513613a5 -> 29407ca33556c939, mode 755, inode 3178624 kept (one rename)
installed scripts/safe_commit.sh: 7e940ee7e8f53ccc -> 0b9d99b8d0b4388d, mode 755, inode 3179051 kept (one rename)
installed scripts/push_when_green.sh: absent -> 510692b0dbd0bf11, mode 755, inode 3180739 kept (one rename)
installed tests/test_anchor_edit.py: 8d7c68441d4cd9c3 -> aaa296d1e5c8b19d (one rename)
installed tests/test_stamp_sh.py: absent -> fde979b55f866224 (one rename)
installed tests/test_stamp_fill.py: absent -> b47c0e26f0bf9cac (one rename)
installed tests/test_safe_commit.py: absent -> 7afc7f41fa98de32 (one rename)
installed tests/test_push_when_green.py: absent -> 5b04a5cdbdd5817c (one rename)
```

The order was stamp.sh, then stamp_fill.py (anchor_edit.py loads it), then anchor_edit.py, then safe_commit.sh, then
push_when_green.sh, then the five test files. The scripts went in first, so no installed test ever pointed at a script
still in its PIN state.

Files for the coordinator's commit (my boundary only; the other modified files in `git status` belong to other lanes):
`scripts/stamp.sh` `scripts/anchor_edit.py` `scripts/safe_commit.sh` `scripts/stamp_fill.py`
`scripts/push_when_green.sh` `tests/test_anchor_edit.py` `tests/test_stamp_sh.py` `tests/test_stamp_fill.py`
`tests/test_safe_commit.py` `tests/test_push_when_green.py` `tasks/briefs/jev-pipes/T268-269-report.md`
