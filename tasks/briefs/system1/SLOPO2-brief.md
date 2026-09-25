# SLOPO2: slopo's index walks only what it can index (task #285; the PC's first sync took 23 min)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/SLOPO2-report.md` (write it
incrementally from the start). PIN: cac6fe6 (origin; `scripts/slopo_review.sh` and `slopo.conf.yaml` unchanged since
INSTALL1, `tests/test_slopo.py` changed once by the coordinator's CI fix, measured below). Evidence: INSTALL1's report
(`tasks/briefs/system1/INSTALL1-report.md`) and the premise block below.

## WHY

The owner (D-091) asked whether the PC's slopo index is still slow. It is: the first sync on the PC took 1,389 s (23 min),
against 130 s in the sandbox. slopo's scanner walks every file under `source_dir` (`root.rglob("*")`) and only then drops
the excluded ones, and the PC clone holds 18.1 million files in `.lanes/` and 1.7 million in `.suite/`, all of them
excluded by `slopo.conf.yaml`. The index needs 116 files. slopo is AGPL and pinned: we never copy, vendor or edit its
code. The fix lives on our side of the seam: a launcher that runs slopo's own CLI with the one walking function
replaced by a walker that never enters a directory whose every file the config excludes.

## CONTRACT

1. **The launcher.** `scripts/slopo_run.py <slopo args>` runs slopo's own CLI (the `slopo.cli` entry point the venv's
   `bin/slopo` runs) in the same process, with `slopo.indexing.sync.scan_directory` (the name `sync.py` imported, which
   is the one it calls) replaced by our walker. Before it replaces anything it checks the seam: the installed slopo is
   the version `upstream.lock.yaml` pins, and `slopo.indexing.sync.scan_directory` is slopo's scanner function. When a
   check fails it runs slopo unchanged and prints one line to stderr naming the check: the results stay slopo's own,
   only the speed is lost, and the log says why. Write the walker from this contract, never from slopo's code.
2. **The walker yields exactly what slopo's scanner yields.** Same paths, same form (relative, forward slashes), and
   the same file-level decision: the extension set and the exclude match are slopo's own (call them; do not
   re-implement them). The one new thing is pruning: a directory is skipped only when every file beneath it would be
   excluded whatever its name, and on any doubt the walker descends. Symlinks, hidden entries and case behave as
   `Path.rglob("*")` does on the interpreter running it: the sandbox venv is Python 3.12, the PC venv is Python 3.13,
   and `/usr/bin/python3.13` exists here for measuring pathlib's behavior on 3.13 (the stdlib only; do not build a
   second slopo venv, the disk will not hold it).
3. **Order.** Measure whether slopo's results depend on the order `scan_directory` yields: index the same tree twice
   into two scratch databases, once in the scanner's order and once reversed, then compare what `slopo analyze` and
   `slopo review` produce (the clusters and the ignore-file hashes). If the order matters, the walker keeps the
   scanner's order on both interpreters; if it does not, say so with the evidence.
4. **The wrapper uses it.** `scripts/slopo_review.sh` runs `index` through the launcher. Route `embed` and `review`
   through it too only if you find they walk the tree (the premise says only `index` reaches the scanner). Keep every
   exit code, the lock and the server handling as they are; update the tests in `tests/test_slopo.py` that record the
   wrapper's calls.
5. **A compare mode for the coordinator.** `scripts/slopo_run.py --compare` runs slopo's own scanner and the walker over
   the configured `source_dir` with the configured excludes and prints, on one line each: the two counts, the paths in
   one and not the other (counts, then at most 20 paths each), whether the orders agree, and both wall times. Exit 0
   only when the sets are equal (and the orders, if item 3 says the order matters). The coordinator runs it on the PC,
   where slopo's own walk takes about 20 minutes; nothing else in the lane touches the PC.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Tests in `tests/test_slopo_run.py`: the walker equals slopo's scanner on this repository and on synthetic trees built
   to break a pruning walker (a negation that brings back a deep directory, an unanchored negation, a `**/` exclude
   inside a brought-back root, an excluded directory holding a brought-back name, a file at the root, hidden files and
   directories, a symlink to a directory and to a file, a directory named like a file pattern, mixed-case extensions);
   the pruning really prunes (a tree with a large excluded directory, where the walker reads none of it; show how you
   know); the seam checks (a wrong version or a moved function runs slopo unchanged and says so); the compare mode's
   exit codes; the wrapper's call record. A negative control reds for each: a walker that prunes one directory too many
   must fail the equality tests.
3. The real index through the launcher on this tree: the same 116 files, the same clusters as slopo's own walk (count
   and hashes), and the wall time of each walk.
4. The measurement for item 3 (the order), with its commands.
5. `bash scripts/test_summary.sh` twice on `tests/test_slopo_run.py tests/test_slopo.py` with the set id; pyflakes rc 0;
   `bash -n scripts/slopo_review.sh`; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
6. NOT-done and DISCREPANCIES; the text of an upstream issue for slopo (the walk before the exclude, with the numbers),
   ready for the coordinator to file. Do not file it.

## BOUNDARY

CREATE: `scripts/slopo_run.py`, `tests/test_slopo_run.py`, your report. MODIFY: `scripts/slopo_review.sh`,
`tests/test_slopo.py` (only the tests that record the wrapper's calls, and new ones for item 4). READ everything else.
Other lanes are live in this tree: SCRUB1 (`scripts/transcript_export.py`, `tests/test_transcript_export.py`, the Laya
dataset manifest) and L2a (`scripts/codemap.py`, `tests/test_codemap.py`, `scripts/hooks/post-commit`): touch none of
their files. `scripts/hooks/post-commit` calls `slopo_review.sh --sync`; if the hook needs a change, write it in your
report and stop there.

## STANDING RULES

No git writes in this tree (throwaway repositories in your scratch are fine); no PC bridge; no outward-facing action.
slopo's database, report directory and model under this tree are shared: point your experiments at scratch databases
(a copied `slopo.conf.yaml` in scratch with its own `db_file`), never at `slopo.db`. Only one slopo run may hold
`/tmp/slopo-sync.lock`; your experiments use their own `SLOPO_LOCK`. The disk is shared (1.8G free): scratch under
150 MB in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/slopo2/`, deleted as you go; a short
`--basetemp` there with its parent created first. Test counts pasted from `scripts/test_summary.sh`; stamps from
`date -u`. Long commands in one foreground call; kill by pid, never by name.

## PREMISE — MEASURED at authoring (2026-09-25 19:4xZ, /home/user/agent-factory at HEAD over the PIN)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf
cac6fe6 transcripts: scrubbed sandbox chat digests (2026-09-25)
$ (PC) tail -n 2 /tmp/pc-slopo-first-sync.log   (the first sync on the PC, niced, 2026-09-25)
Embedded 1362/1362 code units... | Done | SYNC_RC=0 WALL_S=1389
$ (PC) files per top-level folder of ~/agent-factory (find -type f | wc -l)
18082835 .lanes | 1728373 .suite | 3108 .claude | 3083 .agents | 2763 .git | 1151 sandbox-kit | 860 tasks | 844 proofs
$ (sandbox) slopo's own scan_directory over this tree with the config's excludes: count, seconds, per root
files 116 seconds 0.39 {'scripts': 50, 'src': 13, 'proofs': 36, 'harness-ports': 17}
$ find . -type f | wc -l; find . -type l | wc -l   (the sandbox tree)
36018
1
$ sed -n '15,24p' slopo/indexing/scanner.py   (slopo 0.6.0, /root/venv-slopo)
def scan_directory(root: Path, exclude: list[str]) -> Iterator[str]:
    extensions = supported_extensions()
    spec = PathSpec.from_lines("gitignore", exclude)
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in extensions:
            relative = path.relative_to(root)
            if not spec.match_file(relative):
                # Normalize to forward slashes so relative paths have consistent format
                # in generated reports and cluster hashes used in the ignore file.
                yield relative.as_posix()
$ grep -rn -E 'scan_directory|rglob|os\.walk|\.glob\(' --include=*.py slopo/   (every tree walk in the package)
./result/report/filesystem.py:77:    for path in output_dir.glob(CLUSTER_FILE_GLOB):
./indexing/sync.py:15:from slopo.indexing.scanner import filter_units, parse_file, scan_directory
./indexing/sync.py:39:    for path_str in scan_directory(directory, exclude):
./indexing/scanner.py:15:def scan_directory(root: Path, exclude: list[str]) -> Iterator[str]:
./indexing/scanner.py:18:    for path in root.rglob("*"):
$ grep -n -E 'sync_index|def run_index' slopo/indexing/command.py
4:from slopo.indexing.sync import sync_index
8:def run_index(
16:        stats = sync_index(
$ grep -n -E '^def (index|embed|analyze|review)|^def main|^    app\(\)' slopo/cli.py
109:def index(ctx: typer.Context) -> None:
126:def embed(ctx: typer.Context) -> None:
138:def analyze(ctx: typer.Context) -> None:
148:def review(
172:def main() -> None:
173:    app()
$ sed -n '12,26p' slopo/result/review/index_check.py   (review checks the changed files' mtimes; no walk)
def verify_index_fresh(
    conn: sqlite3.Connection,
    changed_files: list[ChangedFile],
    source_dir: Path,
) -> None:
    db_mtimes = load_mtimes_by_paths(conn, [cf.path_db for cf in changed_files])
    for cf in changed_files:
        db_mtime = db_mtimes.get(cf.path_db)
        if db_mtime is None:
            continue
        disk_path = source_dir / cf.path_db
        if not disk_path.is_file():
            continue
        if db_mtime != disk_path.stat().st_mtime:
            raise StaleIndexError
$ head -8 /root/venv-slopo/bin/slopo
#!/root/venv-slopo/bin/python3.12
# -*- coding: utf-8 -*-
import re
import sys
from slopo.cli import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
$ /root/venv-slopo/bin/python -c 'import sys, pathspec; print(sys.version.split()[0], pathspec.__version__)'
3.12.3 1.1.1
$ grep -n -E 'bin/slopo" (index|embed|review)' scripts/slopo_review.sh
63:"$VENV/bin/slopo" index || leave $?
82:  "$VENV/bin/slopo" embed || leave $?
86:"$VENV/bin/slopo" review --base "$base"
$ sed -n '/^source_dir_exclude:/,/^db_file/p' slopo.conf.yaml | grep -E '^  -'
  - "/*"
  - "/*/"
  - "!/scripts/"
  - "!/src/"
  - "!/proofs/"
  - "!/harness-ports/"
  - "**/vendor/"
  - "/proofs/S0-01/tools/archive/"
$ grep -n -E 'slopo (index|embed|review)' tests/test_slopo.py   (the tests that record the wrapper's calls)
289:    assert r2.returncode == 0 and record.read_text().splitlines()[0] == "slopo index"
$ grep -n 'slopo_review' scripts/hooks/post-commit   (L2a's working copy; the hook is L2a's file)
178:# passes, since no root holds one and slopo parses no Markdown), `scripts/slopo_review.sh --sync`
197:elif [ ! -x "${SLOPO_VENV:-$HOME/venv-slopo}/bin/slopo" ] || [ ! -x "$REPO_ROOT/scripts/slopo_review.sh" ]; then
202:  ( cd "$REPO_ROOT" && nice -n 19 ionice -c 3 "$REPO_ROOT/scripts/slopo_review.sh" --sync ) >>"$T/slopo-sync.log" 2>&1 </dev/null & ;;
$ ls /usr/bin/python3.13 && /usr/bin/python3.13 -c 'import sys; print(sys.version.split()[0])'
/usr/bin/python3.13
3.13.12
$ git log --format='%ci %s' cac6fe6..HEAD -- scripts/slopo_review.sh slopo.conf.yaml tests/test_slopo.py | cut -c1-110
2026-09-25 19:41:28 +0000 CI fix (run #1087 red on c0d01e7, task #286): the slopo lock test builds its own roo
$ git diff --stat cac6fe6 HEAD -- scripts/slopo_review.sh slopo.conf.yaml tests/test_slopo.py
 tests/test_slopo.py | 22 ++++++++++++++++++++--
 1 file changed, 20 insertions(+), 2 deletions(-)
$ grep -n -E 'slopo (index|embed|review)' tests/test_slopo.py   (after the CI fix)
289:    assert r2.returncode == 0 and record.read_text().splitlines()[0] == "slopo index"
```

Two questions for you, not facts: (1) `pathspec` is 1.1.1 in the sandbox venv; the PC venv's version is not measured.
Does anything in your walker depend on the pathspec version? (2) The PC walk is 20 minutes today; after the fix, what
does the index still read on the PC besides the four roots (the root directory's own listing, `.git`)?
