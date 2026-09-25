# SLOPO2 report (task #285): slopo's index walks only what it can index

Lane: code-implementer (sandbox, Opus 5.5). Tree: /home/user/agent-factory, started at HEAD 37f720a (PIN cac6fe6);
HEAD is 58a9c6f at hand-back (16 coordinator commits, none touching this lane's five files). No git writes, no PC
bridge, no outward-facing action. Final write: 2026-09-25 20:5xZ.

**TL;DR - DONE (tests green, measured in the sandbox); the PC is NOT run (no bridge in this lane): the coordinator's
`--compare` on the PC is the last proof.** `scripts/slopo_run.py` runs slopo's own CLI with ONE name replaced (the
`scan_directory` that `slopo.indexing.sync` calls) by a walker that yields slopo's scanner's exact list (same paths,
same order) without entering a directory the config excludes whole. `scripts/slopo_review.sh` runs `index` through it.

- [x] Premise holds (section 0).
- [x] Order MATTERS for slopo's report bytes (15 of 19 cluster files differ when the scan is reversed; clusters and
      hashes do not): the walker keeps rglob's order, 3.12 and 3.13 each (section 3).
- [x] Equality on this tree, end to end: slopo and the launcher index 117 files into two scratch DBs with identical
      rows (ids included); after embed + analyze, the same 18 clusters, the same 18 hashes, 0 of 18 cluster files
      differ in any byte (section 4). Walks: slopo 0.33-0.35 s, walker 0.02-0.03 s (3 runs).
- [x] Tests: `pytest-summary: 88 passed in 131.80s (0:02:11)` and `pytest-summary: 88 passed in 130.15s (0:02:10)`,
      set `2 files set=820a7a9214e7`, 0 skipped; 11 launcher mutants all killed (sections 2 and 5).
- [ ] PC `--compare` (NOT run: no bridge; section 8).
- [!] Deviations, flagged: a third seam check (`interpreter`), a witness fallback, and the real-pipeline fixture in
      tests/test_slopo.py now copies the launcher and the lock (section 9).

## Hand-back (the brief's list)

- Built (each ref beside the identifier it names):
  - `R:139` `rglob_entries`: rglob's walk and order, minus pruned directories
  - `R:224` `Pruner`: the pruning rule and the witness check
  - `R:265` `walk_paths`: slopo's file decision, made with slopo's own parts
  - `R:65` `seam_problem`; `R:280` `install`; `R:298` `compare`; `R:347` `main`
  - `W:67` `"$VENV/bin/python" scripts/slopo_run.py index || leave $?`
  - `TS:291` the lock test now records `python scripts/slopo_run.py index`
  - `TS:316` `RecordingRoot`; `TS:352` `test_wrapper_runs_index_through_the_launcher_and_embed_and_review_on_bin_slopo`
  - `TS:372` `test_wrapper_leaves_with_the_launcher_s_exit_code`
  - `TS:418` `SlopoRepo` copies `LAUNCHER`; `TS:420` and `LOCK`
  - `T:341` `test_walker_equals_slopo_scanner`, and 15 more test functions in T (42 collected; section 2)
- Gate lines (verbatim): see section 5.
- Equality evidence: sections 2 and 4. Order evidence: sections 1 (interpreters) and 3 (slopo).
- NOT-done: section 8. Discrepancies: section 10. Upstream issue text: section 7.

## 0. Premise re-measure (written 19:5xZ, sandbox; the PC lines are the brief's, not re-measured: no bridge in this lane)

VERDICT: the premise holds. Every sandbox line re-measured matches; the only drift is the tree's file count (lanes wrote
26 files since authoring), which does not touch the scanner's result.

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-60
37f720a SLOPO2 brief (task #285, D-091 item 5): a launcher that
$ git diff --stat cac6fe6 HEAD -- scripts/slopo_review.sh slopo.conf.yaml tests/test_slopo.py
 tests/test_slopo.py | 22 ++++++++++++++++++++--          (the coordinator's CI fix dae1510, as the brief says)
$ (slopo venv) scan_directory over this tree with the config's excludes
files 116 seconds 0.46 {'scripts': 50, 'src': 13, 'proofs': 36, 'harness-ports': 17}      (brief: 116, 0.39 s, same roots)
$ find . -type f | wc -l; find . -type l
36044                                                        (brief: 36018)
./sandbox-kit/codebase-memory-mcp/Formula                    (the one symlink: -> pkg/homebrew/Formula, a directory)
$ grep -rn -E 'scan_directory|rglob|os\.walk|\.glob\(|iterdir|scandir|os\.listdir' --include=*.py slopo/   (wider than the brief's grep)
result/report/filesystem.py:77  output_dir.glob(CLUSTER_FILE_GLOB)   (the report dir only)
indexing/sync.py:15,39 / indexing/scanner.py:15,18                  (the scanner; no other walk)
$ /root/venv-slopo/bin/python -c 'import sys, pathspec; ...'   ->  3.12.3 1.1.1
$ /usr/bin/python3.13 -c ...                                    ->  3.13.12
$ grep -n -E 'slopo (index|embed|review)' tests/test_slopo.py   ->  289 (the lock test's call record), as the brief says
$ grep -n 'slopo_review' scripts/hooks/post-commit              ->  178, 197, 202 (L2a's file; not touched)
$ upstream.lock.yaml advisory_tooling.slopo.version             ->  '0.6.0' (a string); slopo-0.6.0.dist-info METADATA:
  Requires-Dist: pathspec~=1.1.1 (so a pip install of the pinned wheel resolves pathspec >=1.1.1,<1.2)
```

Facts found while reading (they shape the design; each is re-proved by a test or a measurement below):
- `python3` on PATH is /usr/local/bin/python3 **3.11.15**: pytest runs on 3.11 here (CI pins 3.12). The walker is
  exercised through the slopo venv (3.12) and /usr/bin/python3.13 as subprocesses, never in the pytest process.
- pathspec 1.1.1: `PathSpec.from_lines("gitignore", ...)` builds `GitIgnoreBasicPattern`s; `PathSpec.match_file` is
  last-match-wins over the patterns whose `include` is not None, and a pattern matches when `pattern.regex.search(path)`
  finds a match (`search`, not `match`: only a start-anchored regex pins a prefix).
- CPython's `Path.rglob("*")` yields the same SET on 3.12 and 3.13 (every entry, hidden ones too; a symlinked directory
  is yielded but never entered), in a DIFFERENT ORDER: 3.12 lists each directory's child directories when `walk()`
  visits it and visits the first child first; 3.13 pushes the child directories on a stack and visits the LAST first.
  (Read from /usr/lib/python3.12/pathlib.py and /usr/lib/python3.13/glob.py; measured in section 3.)

## 1. What was built (contract items 1, 2, 4, 5) - written 20:4xZ

- `scripts/slopo_run.py` (NEW, 361 lines; alias R). `main` (`R:347`) checks the seam, then `install` (`R:280`)
  replaces ONE name, `slopo.indexing.sync.scan_directory`, and runs `slopo.cli:main` in this process with
  `sys.argv = ["slopo", *argv]` (click's program name stays `slopo`; the exit code is slopo's own).
  - Seam checks, `seam_problem` (`R:65`); a failing check prints one stderr line naming it and slopo runs unchanged:
    `version` (installed slopo == upstream.lock.yaml advisory_tooling.slopo.version, the lock read beside the
    launcher's own repository root); `scanner` (sync's `scan_directory` IS the scanner's, defined there under that
    name, `sync_index` still calls it by name, its code still names the ten parts the walker mirrors plus the "*" and
    "gitignore" constants, and the scanner module still exposes `supported_extensions` and `PathSpec`); `interpreter`
    (3.12 or 3.13, the two orders measured; `LIFO_BY_INTERPRETER` at `R:57`). **The `interpreter` check is an
    ADDITION to the contract's two: DEVIATION 1.** The fingerprint (co_names and string co_consts of the scanner) was
    measured identical under 3.12 and 3.13 by compiling the installed scanner.py with each interpreter.
  - The walk, `rglob_entries` (`R:139`): the entries `Path.rglob("*")` yields, in the running interpreter's order,
    each directory listed twice as CPython lists it (once for its entries, `_listing` `R:112`; once for its
    subdirectories, `_child_dirs` `R:123`); a symlinked directory is yielded, never entered; an unreadable directory
    is skipped as rglob skips it.
  - The file decision, `walk_paths` (`R:265`): slopo's own parts, called: `scanner.supported_extensions()`,
    `scanner.PathSpec.from_lines("gitignore", exclude)`, and the scanner's per-path test (`is_file`, lower-cased
    suffix, `spec.match_file(path.relative_to(root))`, `as_posix()`).
  - The pruning rule, `Pruner` (`R:224`, with `_tree` `R:166`, `_monotone` `R:178`, `_anchored_prefix` `R:204`):
    prune D only when an excluding pattern's regex finds a match in "D/" and is monotone (no end anchor, boundary,
    lookaround, conditional, scoped flag or unknown node, read with CPython's own `re._parser`; a regex with any flag
    but re.UNICODE is unreadable), and no LATER "!" pattern can match below D (it is start-anchored and its literal
    prefix neither starts with "D/" nor is a prefix of "D/"); anything unreadable = may match = descend. A pruned
    directory must also have pathspec itself exclude 20 witnesses (x<ext> and x/x<ext> for slopo's 10 extensions);
    a disagreement raises `ModelDisagrees` and the installed walker returns slopo's own scan with one stderr line
    (`scan_directory` inside `install`, `R:285`). The walk is collected in full before it is returned, so a fallback
    never follows a partial walk. **The witness fallback is not in the contract: DEVIATION 2.**
  - `--compare [--config PATH]`, `compare` (`R:298`): the walker first, then slopo's scanner; six lines (counts,
    only-in-slopo, only-in-walker with at most 20 paths each, the order, both wall times, directories read and pruned).
    Exit 0 only for the same paths in the same order (item 3 says the order matters); 1 on a difference or a rule
    disagreement; 2 on usage or a config slopo refuses; 3 on a failed seam check.
- `scripts/slopo_review.sh` (MODIFIED, `git diff --numstat`: 5 1; alias W):
  - `W:67` now reads `"$VENV/bin/python" scripts/slopo_run.py index || leave $?`
  - W:8 opens a 4-line header note (it names `slopo_run.py`): why, and why `embed` and `review` stay on
    bin/slopo. Exit codes, the lock and the server handling are untouched. `bash -n` rc 0.
- `tests/test_slopo.py` (MODIFIED, numstat 93 3; alias TS): the lock test's recorded first call is now
  `python scripts/slopo_run.py index` (`TS:291`); NEW `RECORDING_VENV`, `HEALTHY`, `RecordingRoot` (`TS:316`) and two
  tests: `test_wrapper_runs_index_through_the_launcher_and_embed_and_review_on_bin_slopo` (`TS:352`, the call record in
  `--sync` and review modes, with the pre-SLOPO2 wrapper line as the in-test negative control) and
  `test_wrapper_leaves_with_the_launcher_s_exit_code` (`TS:372`, exit 7 through the launcher, no call after it).
  `SlopoRepo` (the real-pipeline fixture) now also copies `LAUNCHER` and `LOCK` (`TS:418`, `TS:420`): **outside "the
  tests that record the wrapper's calls": DEVIATION 3**. The module docstring's group 2 names the new tests.
- `tests/test_slopo_run.py` (NEW, 595 lines; alias T): 7 groups, listed in its docstring; section 2.

## 2. Tests and the mutation audit (EVIDENCE 2) - written 20:4xZ

The equality oracle is slopo's own `scan_directory` (the LIST: paths and order), imported from the pinned install;
the walker is never compared with itself. A DRIVER (a JSON request on stdin, `T:61`) runs every check in the slopo venv
(3.12) or in /usr/bin/python3.13 (stdlib-only ops), since pytest here is 3.11. Groups:
1. order vs CPython's own `rglob("*")` on 3.12 and 3.13, unpruned and with two prune sets, on a tree with symlinks (to
   a dir, a file, nowhere, and `..`), hidden entries, a directory named `x.py`, mixed case; the other interpreter's
   order must NOT match (6 tests: `test_walk_order_is_rglob_order`, `T:262`);
2. equality on this repository (`test_walker_equals_slopo_scanner_on_this_repository`, `T:370`; retried while the tree
   moves; `.git` pruned and never listed; SKIPPED with the reason past `TREE_BUDGET` = 200,000 entries, where
   slopo's own walk takes minutes: the PC's tree; `tree_larger_than` and its test at
   `T:364` `test_tree_probe_stops_at_its_budget`) and on 17 built trees (`test_walker_equals_slopo_scanner`, `T:341`;
   `CASES` at `T:273`): deep negation, unanchored negation, `**/` exclude inside a brought-back root, excluded dirs
   holding an anchored and an unanchored brought-back name, root files, `/*` alone, hidden, symlinks (to a dir, a
   file, nowhere, out of the root into an excluded dir, a root-level link), a directory named like a file pattern, mixed-case
   extensions, regex metacharacters and a space, a wildcard negation, a negation before its exclude, non-ASCII,
   `*` + `!*.py`, the real config on the PC's shape. Each case pins the directories the walker must prune (12 pin a
   non-empty set) and carries the negative control: the walker's own rule plus ONE directory too many must lose
   exactly that directory's files;
3. `test_the_walker_reads_nothing_inside_a_large_excluded_directory` (`T:389`): every `os.scandir` call recorded; over
   a 221-directory excluded `big/` the walker lists 0 of them; the recorder's positive controls, slopo's rglob and an
   unpruned walker, list 442 each (measured: walker 6 calls in all, slopo 448);
4. `test_the_rule_reads_the_config_s_regexes_alike_on_3_12_and_3_13` (`T:418`): pathspec 1.1.1's regex for each
   config line (`RULE_EXPECTED`) and 5 edge regexes read identically by both interpreters' `re._parser`;
5. seam checks: `test_seam_checks_pass_on_the_pinned_install`, interpreters 3.14 and 3.11 refused, a wrong pin (a
   copied launcher beside its own lock: `test_wrong_pinned_version_runs_slopo_unchanged_and_says_so`, `T:456`), a
   foreign `scan_directory`, a `sync_index` that no longer calls it, a scanner whose code changed
   (`test_a_moved_or_changed_scanner_runs_slopo_unchanged_and_says_so`, `T:479`): each gives exactly one stderr line
   naming the check, slopo unchanged and still indexing;
   `T:493` `test_a_rule_pathspec_contradicts_falls_back_to_slopo_s_scan` gives the fallback line and slopo's result;
6. `test_launcher_and_slopo_write_the_same_index` (`T:517`): identical `files` and `code_units` rows (ids, paths,
   mtimes, hashes) in two scratch DBs; the flipped order writes the same files under other ids (the control);
   `test_launcher_exits_with_slopo_s_code` (`T:536`): exit 1 and slopo's stderr through the launcher, the seam line
   first when a check fails;
7. `--compare`: exit 0 on a PC-shaped tree (`test_compare_exits_0_on_equal_lists`, `T:559`; the read line says 12
   directories read, 9 pruned);
   `T:577` `test_compare_exits_1_when_the_walker_is_wrong`: 1 for one directory too many, the flipped order, a rule
   disagreement; `T:584` `test_compare_exits_2_on_usage_and_3_on_a_failed_seam_check`: 2 on usage and on a missing
   config, 3 on a wrong pin.

Red-green. The tests were written after the launcher, so each group was proved red by MUTATING the launcher: eleven
mutants, each applied by exact replacement, the file restored and its sha256 checked after each. Final run, on the
final launcher (sha256 prefix `2150d006573cedc7` before and after) and the final test file (42 tests), verbatim:
```
M1 ignore-negations      rc=1 | 23 failed, 19 passed in 6.84s
M2 one-sided-prefix      rc=1 | 3 failed, 39 passed in 7.82s    (only equality sees it: the witnesses pass)
M3 flip-lifo             rc=1 | 12 failed, 30 passed in 7.79s   (all 6 order tests, repository, DB, compare, 2 cases)
M4 follow-symlinks       rc=1 | 7 failed, 35 passed in 8.45s
M5 end-anchor-monotone   rc=1 | 3 failed, 39 passed in 7.91s
M6 skip-hidden           rc=1 | 8 failed, 34 passed in 8.70s
M7 no-witness            rc=1 | 2 failed, 40 passed in 8.11s    (the two fallback tests)
M8 suffix-case           rc=1 | 1 failed, 41 passed in 8.05s    (mixed-case)
M9 version-ignored       rc=1 | 3 failed, 39 passed in 7.41s
M11 never-prune          rc=1 | 17 failed, 25 passed in 9.44s   (the 12 pinned-prune cases, repository, reads, 3 more)
M10 no-fingerprint       rc=1 | 1 failed, 41 passed in 8.11s    (changed-scanner)
restored, sha256 2150d006573cedc7
```
The size guard's skip branch is not reached here (39,671 entries); run once with `TREE_BUDGET = 10` it skipped with
its reason (`this tree holds more than 10 entries: slopo's own walk takes minutes here ...`).
The two new tests in tests/test_slopo.py carry their own negative control (the pre-SLOPO2 wrapper line, whose record
starts `slopo index`); they were not separately mutated. The per-case pruned sets were derived by hand from the rule and
then matched the run: they pin intended pruning (a never-pruning walker fails 12 cases, M11); correctness rests on the
independent oracle, slopo's scanner. Two expectations I first typed wrong were caught by deriving them before the run
(a sorted name list, the first witness `x.cs`), and a third by enumerating the tree before the run (12 directories
read, first typed as 10).

## 3. The order question (contract item 3; EVIDENCE 4) - written 20:0xZ

VERDICT: **the order matters.** slopo's clusters and their ignore-file hashes do not depend on the order
`scan_directory` yields, but the bytes of `slopo analyze`'s cluster files do: in 15 of 19 cluster files the members
appear in another order, and in 1 of them another member's raw body is the one printed. So the walker keeps the
scanner's order, on 3.12 and on 3.13 (section 1).

Why, from slopo's own code (read, not copied): `sync_index` inserts files and units in scan order, so unit ids follow
it; `sort_cluster` orders a two-unit cluster by ascending id and breaks ties by id; the report groups a cluster's units
by body hash in that order and prints each group's first unit's raw body. `cluster_hash` sorts (path, body hash)
pairs and the report sorts clusters by (rounded score, hash): both order-free.

The measurement (scratch, never slopo.db): the scanner's 116 files copied from this tree at 19:5xZ into a throwaway
git repo; two configs = slopo.conf.yaml with their own db_file, report_dir, ignore_file and a free port for my own
embed server. Review changes made first: a verbatim copy of `plan` (scripts/anchor_edit.py) in a new untracked file, and
a near copy of `flatten` (scripts/chat_find.py) appended to scripts/slopo_embed_server.py (tracked). Then per arm, from
fresh databases, slopo's own CLI in-process (`run.py` below; `--reverse` makes sync.py's `scan_directory` yield slopo's
own scan reversed):

```
# run.py: import slopo.indexing.sync as sync; from slopo.cli import main
#         with --reverse: orig = sync.scan_directory; sync.scan_directory = lambda r, e: iter(list(orig(r, e))[::-1])
#         sys.argv[0] = "slopo"; sys.exit(main())
$ scripts/slopo_embed_server.py --port 47803 --max-tokens 1024 &      (killed by pid at the end)
for arm in fwd rev: run.py [--reverse] --config ../conf-$arm.yaml index; ... embed; ... analyze; cp report;
                    ... review --base HEAD; cp report
fwd: index/embed/analyze/review rc=0 0 0 0, wall 166.0 s | rev: rc=0 0 0 0, wall 116.9 s
Indexed 1425 code units from 117 files (0 unchanged, 0 removed).     (both arms)
```

Results:
```
databases     units equal (path, name, lines, body hash, body): True 1425
              embeddings: same keys True | byte-identical vectors True 1419
              file id order: fwd == reversed(rev): True
analyze       stdout: SAME (the report path aside); report: 20 vs 20 files, same names
              index.md SAME (the Generated line aside): the same 19 clusters, hashes, scores, unit and file counts
              cluster files differing: 15 of 19
                14: the same lines permuted (member order); 1 (cluster-02, hash 016fac482a47): the printed body of
                the group {proofs/S0-05/check_egress.py 158-160, scripts/ci_gate.py 157-158} (one body hash, two raw
                bodies) carries a whitespace-only line in rev, not in fwd
review        stdout: SAME ("1 of 2 changed units look similar to other code."); report: 2 vs 2 files, index.md SAME,
              cluster files differing: 0 of 1 (its one cluster is an exact copy: one group, sorted by path)
```
A first attempt is recorded for honesty: with a RENAMED copy of `plan` as the only change, review printed "No similar
code involving the changes." in both arms: the pair scores 0.909 (cosine, from the stored vectors), under slopo's
0.92 threshold, so that arm tested nothing and was redone with the changes above.

## 4. The real index through the launcher on this tree (EVIDENCE 3) - written 20:4xZ

Two copies of slopo.conf.yaml in scratch (their own db_file, report_dir, ignore_file; a free port for my own embed
server), cwd = this repository root, run back to back at 20:30Z; slopo.db never touched:
```
$ ~/venv-slopo/bin/python ~/venv-slopo/bin/slopo --config $R/conf-slopo.yaml index
Indexed 1437 code units from 117 files (0 unchanged, 0 removed).
slopo index rc=0 wall 1.285984668 s
$ ~/venv-slopo/bin/python scripts/slopo_run.py --config $R/conf-launcher.yaml index
Indexed 1437 code units from 117 files (0 unchanged, 0 removed).
launcher index rc=0 wall .963339291 s
files 117 117 | units 1437 1437 | files rows identical: True | unit rows identical: True     (ids included)
per root: {'scripts': 51, 'src': 13, 'proofs': 36, 'harness-ports': 17}
$ slopo embed (each DB; 98.2 s and 98.3 s) ; slopo analyze (each DB)
analyze stdout SAME        (Exact copies: 10 of 1437 units; 41/1427 and 51/1437 units flagged)
files: 19 vs 19 | index.md SAME (Generated line aside) | cluster files differing: 0 of 18
18 clusters, hashes (both arms, same order): 36ee701b3fa9 016fac482a47 e7ca78b96f3f 4f8d02f71358 82c95d5fd39a
  fb186028ebb0 a914f2147d52 d2c782fec22d 7991c0eed94a afac20a77af4 982bf42b0863 7b57e7b2faf0 fadf03baafd1
  9b529167d3b1 b898a7acc7c8 35f5105465b2 d8f0553c6ade 6f5e4c9a07ed
$ ~/venv-slopo/bin/python scripts/slopo_run.py --compare    (three runs; the walk alone, the walker first)
slopo_run compare: count slopo 117 walker 117
slopo_run compare: only in slopo 0 []
slopo_run compare: only in walker 0 []
slopo_run compare: order same
slopo_run compare: wall slopo 0.35 s walker 0.03 s    | 0.33 s 0.03 s | 0.33 s 0.02 s ; rc=0 each
slopo_run compare: walker read 232 directories, pruned 31 ['.gitnexus', 'graft', 'config', ...]
```
**117, not the brief's 116:** the 117th file is this lane's own `scripts/slopo_run.py` (untracked, under a root). The
brief's 116 already counted L2a's untracked `scripts/codemap.py` (scanned-but-untracked now: those two). With the
order kept, even the member order inside every cluster file is byte-identical, which section 3's reversed arm is not.

## 5. Gates (EVIDENCE 5), verbatim - written 20:4xZ

```
$ bash scripts/pc_suite.sh set-id -- tests/test_slopo_run.py tests/test_slopo.py
2 files set=820a7a9214e7
$ sha256sum (first 16) before and after both runs: 2150d006573cedc7 scripts/slopo_run.py, 1909f74a535ac9ec
  tests/test_slopo_run.py, f3302dff4f0b4d4f tests/test_slopo.py, c3e383773b9ca17e scripts/slopo_review.sh
$ bash scripts/test_summary.sh tests/test_slopo_run.py tests/test_slopo.py --basetemp=<scratch>/bt/g3   (20:50:19Z)
pytest-exit: 0
pytest-summary: 88 passed in 131.80s (0:02:11)
$ bash scripts/test_summary.sh tests/test_slopo_run.py tests/test_slopo.py --basetemp=<scratch>/bt/g4   (20:52:36Z)
pytest-exit: 0
pytest-summary: 88 passed in 130.15s (0:02:10)
$ grep -c SKIPPED gate3.log gate4.log        -> 0 and 0 (the slopo venv, the model and /usr/bin/python3.13 are here)
$ python3 -m pyflakes scripts/slopo_run.py tests/test_slopo_run.py tests/test_slopo.py ; echo rc=$?
pyflakes rc=0
$ bash -n scripts/slopo_review.sh ; echo rc=$?
bash -n rc=0
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>      (re-run on the final report at hand-back, section 13)
scripts/slopo_run.py: 0 | tests/test_slopo_run.py: 0 | scripts/slopo_review.sh: 0 | tests/test_slopo.py: 0
```
Two earlier pairs on the same set, before the size probe test was added, read `87 passed in 134.84s (0:02:14)` and
`87 passed in 132.26s (0:02:12)`.
88 = 42 in tests/test_slopo_run.py + 46 in tests/test_slopo.py (43 before + 3 new: two parametrized modes and the
exit-code test). In CI (no slopo venv, no python3.13) the new file's slopo-dependent tests SKIP by declaration, as
test_slopo.py's already do; the two new test_slopo.py tests use fakes and run everywhere curl and python are.

## 6. The brief's two questions - written 20:4xZ

(1) **Does anything in the walker depend on the pathspec version?** The file decision does not: it calls the installed
pathspec exactly as slopo's scanner does, so both sides move together. The PRUNING depends on three things, each
guarded: (a) pathspec's public shape: `PathSpec.patterns`, each pattern's `include` and compiled `regex` (anything else
-> the rule reads it as "may match" and descends); (b) its semantics: `PathSpec.match_file` = the last pattern whose
`regex.search(path)` matches decides (read in 1.1.1: `GitIgnoreBasicPattern.match_file is RegexPattern.match_file`
is True, `regex.search`; `util.check_match_file`); (c) the regex FORMS 1.1.1 produces (pinned by
`test_the_rule_reads_the_config_s_regexes_alike_on_3_12_and_3_13`). A version whose forms the rule cannot read only
loses speed. A version whose semantics changed so that pathspec keeps a path the rule would skip is caught by the
20-witness check (fallback to slopo's own scan, one stderr line), except for a name-specific keep no witness hits,
which only the PC `--compare` would show. Also: pathspec picks `re2` or `hyperscan` as its backend when either is
importable (`_backends/agg.py`); the sandbox venv has neither (backend `SimplePsBackend`); the rule models Python
`re`, and the witness check compares against whatever backend the spec really uses. The PC's pathspec is not
measured: both setup scripts `pip install` the pinned wheel, whose METADATA says `pathspec~=1.1.1` (>=1.1.1,<1.2).
(2) **After the fix, what does the index still read on the PC?** The walker opens: the repository root (listed twice,
as rglob lists it), and every directory under the four roots except `**/vendor/` directories and
`proofs/S0-01/tools/archive/` (each listed twice), plus one stat per entry in those directories (the same `is_file`
stats slopo's scan makes there). It opens nothing inside `.git`, `.lanes`, `.suite`, `.claude`, `.agents`,
`sandbox-kit`, `tasks` or any other root-level directory: each is pruned by its name alone (`/*/` covers it and no `!`
pattern's prefix fits it). In the sandbox that is 232 directories and 464 scandir calls ('.': 2, src 20, proofs 412,
scripts 14, harness-ports 16), 31 pruned (`.git` among them, measured never listed). Beyond the walk, `slopo index`
stats each yielded file and parses the changed ones; `embed` and `review` do not walk. The PC's four roots are not
measured here: `--compare` prints `walker read N directories, pruned M` on the PC.

## 7. Upstream issue for slopo (ready to file; NOT filed) - written 20:4xZ

Title: `slopo index` walks every file under source_dir before it applies source_dir_exclude

> **slopo 0.6.0** (the PyPI wheel), Python 3.13 on Linux, pathspec 1.1.x.
>
> `scan_directory` (slopo/indexing/scanner.py) iterates `root.rglob("*")` and tests each path against
> `source_dir_exclude` only afterwards. A directory the excludes cover completely is still walked, entry by entry.
>
> Numbers: our repository root holds about 18.1 million files under `.lanes/` and 1.7 million under `.suite/` (lane
> worktrees and test scratch), all excluded. The first `slopo index` there took **1,389 s** (23 minutes). The index
> needs about 116 files, under four directories. On a clone without those two directories (36,044 files) the full
> walk takes 0.33-0.35 s and a walk that skips the excluded directories 0.02-0.03 s, with the same result.
>
> Config (excerpt): `source_dir: .`; `source_dir_exclude: ["/*", "/*/", "!/scripts/", "!/src/", "!/proofs/",
> "!/harness-ports/", "**/vendor/", "/proofs/S0-01/tools/archive/"]`.
>
> Suggestion: prune while walking (for example `os.walk` top-down, dropping a directory from `dirnames` when the spec
> excludes every path below it). With pathspec's file-by-file, last-match-wins semantics a directory can only be
> skipped when no later `!` pattern could match below it, so a conservative check is needed; an explicit
> `source_dirs` list (several roots) would also solve our case.
>
> Related: the report bytes depend on the walk order. Unit ids follow the scan order, `sort_cluster` orders a
> two-unit cluster by id, and a group of same-body-hash units prints its first unit's raw body. Reversing the scan
> order changed 15 of 19 cluster files on the same index (member order in 14, the printed body in 1); the clusters
> and their ignore-file hashes did not change. If the walk changes, sorting by path would keep reports stable.
>
> We work around it locally by running the CLI with a pruning walk in place of `scan_directory`; the files, their
> order and the clusters are identical to slopo's own walk.

## 8. NOT done (first-class) - written 20:4xZ

1. **The PC `--compare` was NOT run** (no bridge in this lane, by the brief). So on 3.13 the walker is proven equal
   to CPython 3.13.12's `rglob` order (sandbox, stdlib only), not to slopo's scanner itself (no 3.13 slopo venv, by
   the brief), and the PC's exact Python 3.13.x and pathspec 1.1.x are unmeasured. Command for the coordinator (the PC
   clone, the slopo venv; about 20 minutes, dominated by slopo's own walk; exit 0 = the same paths in the same order):
   `cd ~/agent-factory && ~/venv-slopo/bin/python scripts/slopo_run.py --compare`
   A cheaper PC check the coordinator may add: `tests/test_slopo_run.py` through `scripts/pc_suite.sh`. There the
   slopo venv is 3.13, so its 17 hostile-tree cases compare the walker with slopo's own scanner ON 3.13 in seconds
   (the on-this-repository test skips there by its size guard; `--compare` covers the real tree).
2. Nothing committed: no git writes in this tree (the brief); the coordinator commits the five paths:
   `scripts/slopo_run.py`, `tests/test_slopo_run.py`, `scripts/slopo_review.sh`, `tests/test_slopo.py`, this report.
3. The upstream issue is drafted, not filed (section 7).
4. `scripts/hooks/post-commit` needs no change (it calls the wrapper; the wrapper calls the launcher). Not touched.
5. No incident-log or ledger entry (outside the boundary). For the coordinator: the trailing-`&` quirk guard
   (search-intercept, rule trailing-amp) blocked one of my commands at 19:5xZ before it ran (a `&&` list ending in
   `&` would have backgrounded the whole list and `$!` would have been the subshell's pid); the guard worked, nothing
   ran. One defect was found in existing code, a test hazard (section 10 item 7). It is not fixed (outside the
   boundary), so no bug-echo run and no registry row. A literal sibling sweep of tests/ for whole-tree walks of the live
   repository (`ROOT.rglob(`, `os.walk(ROOT`, `scan_directory(`) finds only test_slopo.py's two `scanned()` callers;
   tests/test_slopo_run.py's own repository test carries the size guard.

## 9. Deviations from the brief (flagged) - written 20:4xZ

1. **A third seam check, `interpreter`** (3.12 or 3.13), beyond the contract's two. The walker reproduces rglob's order
   only for the two interpreters measured; on any other it runs slopo unchanged and says so.
2. **A witness fallback** the contract does not ask for: before pruning, pathspec itself must exclude 20 witnesses
   below the directory; if not, the whole walk is slopo's own scan (one stderr line). It turns a rule error into lost
   speed instead of lost files. The `scanner` check also goes beyond "is slopo's scanner function": `sync_index`
   must still call the name, and the scanner's code must still name the ten parts the walker mirrors.
3. **`SlopoRepo` in tests/test_slopo.py** (the real-pipeline fixture, not a call-recording test) now copies
   `scripts/slopo_run.py` and `upstream.lock.yaml` (`TS:418` `LAUNCHER`, `TS:420` `LOCK`): its copied wrapper
   calls the launcher, so without them the real-pipeline tests fail (python cannot open the file). Also the module
   docstring's group 2.
4. `--compare` exits 2 on a config slopo refuses (a missing `--config` file), not only on usage.
5. The walker returns a list (iterated) rather than a lazy generator: sync_index consumes it fully either way; the
   stat and parse of each file now happen after the whole walk instead of between its steps.
6. The wrapper gained a 4-line header note (W:8, naming `slopo_run.py`); the brief asked only for the call.
7. The on-this-repository equality test SKIPS (with its reason) on a tree past 200,000 entries: on the PC slopo's own
   walk is 20 minutes, twice per test run, past the driver's 300 s timeout; `--compare` is that venue's check.

## 10. Discrepancies - written 20:4xZ

1. The index is 117 files, not 116: the 117th is `scripts/slopo_run.py` itself (section 4).
2. `find . -type f` 36,044 now vs 36,018 at authoring; slopo's scan 0.33-0.46 s vs 0.39 s: lanes writing, noise.
3. `python3` on PATH is 3.11.15, so pytest here is 3.11 (CI pins 3.12); all walker checks run in subprocesses.
4. The brief's "(symlinks, hidden entries and case) behave as rglob does on the interpreter running it": measured,
   the SET is the same on 3.11, 3.12 and 3.13 (27 entries on the probe tree); only the ORDER differs by version.
5. The brief's question 2 lists `.git` as maybe still read: the walker never lists it (`/*/` covers it, no `!` fits).
6. CPython lists each directory twice during rglob (entries, then subdirectories); the walker does the same, so its
   "read 232 directories" is 464 scandir calls.
7. **Adjacent defect, not fixed (outside the boundary):** two tests in tests/test_slopo.py,
   `test_scope_is_the_four_roots_without_vendored_or_archived_code` and
   `test_scope_negative_control_without_the_dir_pattern_the_scope_leaks`, run slopo's own `scan_directory` over the
   REAL tree through `scanned()` with `timeout=120`. On the PC that walk is about 20 minutes, so both would fail by
   timeout in any PC run of test_slopo.py (inferred from the PC's first sync; not run on the PC). They could scan
   through the walker, or skip past a size budget as tests/test_slopo_run.py's repository test now does.
8. HEAD moved during the lane, 37f720a -> 58a9c6f (L2a and SCRUB1 landed, among 16 commits); `git log 37f720a..HEAD`
   over the five files prints nothing, and the hook still calls `scripts/slopo_review.sh --sync` (no hook change
   needed). The gates ran on the working tree as it stood at 20:50Z-20:54Z.
9. Adjacent observation, not fixed: if `scripts/slopo_run.py` were missing, python exits 2 and the wrapper leaves 2,
   the same code as its usage error (the embed server script has no presence check either).

## 11. Self-attack: the three likeliest ways this is wrong - written 20:4xZ

1. **The PC's 3.13.x or pathspec 1.1.x differs from what I measured**, so the order or the pruning drifts there.
   Ruled out as far as the sandbox allows: the order model is the one in CPython 3.13's own glob code
   (`_Globber.recursive_selector`, a stack) and matches /usr/bin/python3.13 (3.13.12) on a tree that tells the orders
   apart; regex-shape drift can only reduce pruning; a semantic drift trips the witness check. Residual: closed only by
   `--compare` on the PC (NOT-done 1), which exits 0 only for the identical list.
2. **The rule prunes a directory that holds a file slopo keeps.** Ruled out by the argument (a start-anchored regex's
   literal prefix begins every match under `search`; flags refused; monotone allow-list), 17 hostile trees plus this
   repository against slopo's scanner, the witness check, and M1/M2/M5/M7/M11 all killed. Residual: a wrong prune that
   all 20 witnesses miss; I found no pattern shape that produces one (an anchored `!` keeps its whole prefix path open;
   an unanchored one blocks all pruning).
3. **A slopo change keeps the names but changes the scan's meaning.** Ruled out by the `version` check against the
   digest-pinned wheel (a change needs a new version, which the check refuses) and the `scanner` fingerprint (M9 and
   M10 killed). Residual: a patched install that keeps the version string; out of scope (the wheel digest is checked
   at install by both setup scripts).

## 12. Screen tells, resolved by class - written 20:4xZ

`python3 scripts/ap_screen.py` over my four code files: 14 hits, 9 of them already in HEAD's tests/test_slopo.py
(its screen alone: 9 hits) and 5 on my lines, each read and resolved by class:
- AF-AP-40 at `R:273` (`path.is_file()`): the file decision the contract says must mirror slopo's, not a
  presence-gated check;
- AF-AP-40 at `TS:341` and `TS:344` (`self.record.exists()`): clearing and reading the call record; an absent record
  reads as `[]` and FAILS the assertion;
- AF-AP-175 at `TS:351` (a `parametrize`): the literal "HEAD" handed to a recording fake; no git read;
- AP-1 at `T:38` (`SLOPO_VENV`): the same lookup test_slopo.py makes at `TS:48` (`SLOPO_VENV`, one of HEAD's 9),
  read once at import.
The edit-snapshot tells while writing: AF-AP-11 (fixed: bin/slopo now runs as `[SLOPO_PY, SLOPO_BIN]`), AF-AP-44
(fixed: `present()` never raises), AP-66 (the patches live in the DRIVER string, which runs in a throwaway subprocess,
so nothing leaks).

## 13. Evidence tiers and the final checks - written 20:4xZ

- VERIFIED (measured here, pasted): the premise lines (section 0); rglob's order and set on 3.11, 3.12, 3.13; the order
  experiment (section 3); equality on this tree incl. DB rows and cluster files (section 4); the gates (section 5);
  eleven mutants killed; the sandbox read set (section 6).
- INFERRED: that the walker equals slopo's scanner on the PC's 3.13 (composition: the traversal equals 3.13.12's
  rglob, and the file decision is the scanner's own calls); what the PC walk reads (the config and the rule, not a
  PC measurement).
- ASSUMED: the PC venv is 3.13 and holds slopo 0.6.0 with pathspec 1.1.x (the brief and the setup scripts; not
  measured); the PC's Python 3.13.x keeps 3.13.12's glob order.
- The report itself, last: `python3 scripts/report_lint.py <this report> --map R=scripts/slopo_run.py --map
  T=tests/test_slopo_run.py --map TS=tests/test_slopo.py --map W=scripts/slopo_review.sh` printed
  `report_lint: 62 refs — OK 62, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`; the U+2028/U+2029 grep
  printed 0 for all five files (the four code files and this report). Scratch deleted; both embed servers I started
  were stopped by pid (their ports answer nothing).
