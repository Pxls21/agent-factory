STATUS: COMPLETE 2026-09-24T03:03Z (lane J1-3-R1, task #209, sandbox venue; started 2026-09-24T02:02:30Z, relaunched 02:17Z). R1-R6 and S1-S6 built; `67 passed` twice on set `87e28761f102`; 28 of 28 mutants killed; 0 of 40 concurrent ledgers corrupt; real run `harvest: 235 rows`, `refused: 39 records`, yield below KC-J7's 200 for every type. LOUD: DISCREPANCY D-1 (a second existing test changed). Not committed; the coordinator commits.

# J1-3-R1 report — the ONE focused repair of J1-3 (D-031; D-063 + D-064)

Brief: `tasks/briefs/pc/pc-j1-3-r1.md`. PIN f772bfc. Venue: the sandbox shared tree `/home/user/agent-factory` (the coordinator's
dispatch message replaces the brief's VENUE NOTES).

## 0. Premise

```
$ date -u
Thu Sep 24 02:02:30 UTC 2026
$ git rev-parse HEAD
48e81f0c8eac13ccacb01dd6929ce0b1e2ac3730
$ git diff --stat f772bfc HEAD -- scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions/ src/agent_factory/decisions/; echo "rc=$?"
rc=0
```
(no diff lines: the boundary files are byte-identical to the PIN.)

The brief's PREMISE block, re-run command by command in the sandbox (script `/tmp/j13r1/p/premise.sh`; the brief's `/tmp/j13r1p/…`
paths mapped to `/tmp/j13r1/p/…`), verbatim:

```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf; git rev-parse --short HEAD
2026-09-24T02:11Z
8ea2932
0f75750
$ git log --format='%h %s' f772bfc -- scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions/sources | cut -c1-110
379f277 J1-3: scripts/decide-harvest + 33 tests + fixture sources (lane pc-j1-3.md--feb26d7), GATED-PENDING-VE
$ for f in scripts/decide-harvest tests/test_decide_harvest.py src/agent_factory/decisions/__init__.py src/agent_factory/decisions/canonical.py src/agent_factory/decisions/volatile.py src/agent_factory/decisions/ledger.py; do echo "$(git rev-parse f772bfc:$f | cut -c1-12) $(git show f772bfc:$f | wc -l) $f"; done
22b63bc47e7c 849 scripts/decide-harvest
2cace4741511 581 tests/test_decide_harvest.py
377ccd53da0c 24 src/agent_factory/decisions/__init__.py
607b65b613e2 78 src/agent_factory/decisions/canonical.py
bf04415d72c1 395 src/agent_factory/decisions/volatile.py
71fc398a5340 616 src/agent_factory/decisions/ledger.py
$ for f in scripts/decide-harvest tests/test_decide_harvest.py src/agent_factory/decisions/__init__.py src/agent_factory/decisions/canonical.py src/agent_factory/decisions/volatile.py src/agent_factory/decisions/ledger.py; do echo "$(git hash-object $f | cut -c1-12) $(wc -l < $f) $f (worktree)"; done
22b63bc47e7c 849 scripts/decide-harvest (worktree)
2cace4741511 581 tests/test_decide_harvest.py (worktree)
377ccd53da0c 24 src/agent_factory/decisions/__init__.py (worktree)
607b65b613e2 78 src/agent_factory/decisions/canonical.py (worktree)
bf04415d72c1 395 src/agent_factory/decisions/volatile.py (worktree)
71fc398a5340 616 src/agent_factory/decisions/ledger.py (worktree)
$ git ls-tree -r --name-only f772bfc -- tests/fixtures/decisions/sources
tests/fixtures/decisions/sources/docs/INCIDENT-LOG.md
tests/fixtures/decisions/sources/src/existing.py
tests/fixtures/decisions/sources/tasks/briefs/x/VERIFY-X-report.md
tests/fixtures/decisions/sources/tasks/briefs/x/X-report.md
tests/fixtures/decisions/sources/transcripts/x/t.jsonl
$ git status --short -- scripts tests src | wc -l
0
$ grep -n 'splitlines' scripts/decide-harvest
260:    lines = text.splitlines()
303:    lines = source.text.splitlines()
375:    lines = source.text.splitlines()
515:    lines = source.text.splitlines()
642:    for line_number, raw in enumerate(source.text.splitlines(), 1):
$ grep -n '"HEAD"' scripts/decide-harvest
141:    result = _git(root, "ls-tree", "-r", "--name-only", "-z", "HEAD")
$ sed -n 46,51p scripts/decide-harvest
BOUNDARY_RE = re.compile(
    r"^(?:- \*\*BOUNDARY DEVIATION\*\*|\d+\. BOUNDARY DEVIATION)"
    r"\s*(?:—|:|\*\*)(?P<tail>.*)$",
    re.IGNORECASE,
)
MARKDOWN_HEADING_RE = re.compile(r"^#{1,6}\s+(?P<text>.+?)\s*$")
$ sed -n 236,248p scripts/decide-harvest
    joined.append(first[opening + 2 :])
    for offset in range(10):
        index = start + offset
        if index >= len(lines):
            break
        piece = joined[0] if offset == 0 else lines[index]
        close = piece.find("**")
        if close >= 0:
            prefix = joined[:-1] if offset else []
            return _collapse(" ".join(prefix + [piece[:close]])), None
        if offset:
            joined.append(piece)
    return None, "unterminated-heading"
$ grep -n 'strip("\*")' scripts/decide-harvest
352:    raw = cell.strip().strip("*").strip()
484:    value = value.strip().strip("*").strip()
$ sed -n 360,367p scripts/decide-harvest

def _report_paths(text: str, root: Path, tree: set[str]) -> list[str]:
    found: set[str] = set()
    for token in BACKTICK_RE.findall(text):
        candidate = re.sub(r":\d+(?:(?:-|–)\d+)?(?:[,:].*)?$", "", token)
        if candidate.startswith(str(root) + os.sep):
            candidate = os.path.relpath(candidate, root).replace(os.sep, "/")
        if candidate in tree:
$ sed -n 156,165p scripts/decide-harvest
def _regular_worktree_bytes(root: Path, path: str) -> bytes | None:
    target = root / path
    try:
        if not target.is_file() or target.is_symlink():
            return None
        return target.read_bytes()
    except OSError:
        return None


$ sed -n 818,834p scripts/decide-harvest
                    incumbent_answer=candidate.answer,
                    source_ref=_source_ref(source, candidate.locator),
                    root=root,
                )
                append(args.out, row)
            except DecisionStateError as exc:
                if exc.reason == "decision-row-duplicate":
                    skipped += 1
                    print(str(exc), file=sys.stderr)
                    continue
                reason = f"state:{exc.reason}"
                refused.append(Refusal(source.path, candidate.line, reason))
                print(
                    f"harvest-source-unparseable: {source.path}:{candidate.line} ({reason})",
                    file=sys.stderr,
                )
                continue
$ grep -n -E 'JSONDecodeError|RecursionError' scripts/decide-harvest
645:        except json.JSONDecodeError:
688:        except json.JSONDecodeError:
$ grep -n -E 'def test_boundary_deviation_requires_the_declared_delimiter|def test_.*head|def test_.*admission' tests/test_decide_harvest.py
136:def test_registry_heading_accepts_the_committed_qualified_form(tmp_path):
233:def test_admission_untracked_modified_unknown_and_existing_out_untouched(tmp_path):
291:def test_clean_tree_harvests_head_bytes(tmp_path):
300:def test_source_bytes_come_from_head_after_admission(tmp_path):
466:def test_boundary_deviation_requires_the_declared_delimiter(tmp_path):
$ mkdir -p /tmp/j13r1/p && /root/venv-agent-factory/bin/python -m pytest tests/test_decide_harvest.py -q -p no:cacheprovider --basetemp=/tmp/j13r1/p/bt | tail -1
33 passed in 9.00s
$ bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py
1 files set=87e28761f102
$ git clone -q --no-checkout --shared /home/user/agent-factory /tmp/j13r1/p/wt && git -C /tmp/j13r1/p/wt checkout -q --detach f772bfc && git -C /tmp/j13r1/p/wt rev-parse --short HEAD
f772bfc
$ /root/venv-agent-factory/bin/python scripts/decide-harvest --root /tmp/j13r1/p/wt --out /tmp/j13r1/p/real.jsonl > /tmp/j13r1/p/real.out 2> /tmp/j13r1/p/real.err; echo rc=$?; cat /tmp/j13r1/p/real.out; grep -c . /tmp/j13r1/p/real.err
rc=3
harvest: 232 rows, per question type: ap.violates_row=121, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=109, wf.drift=2
negatives: 0 (hand-labeled in J2)
sources: 261 read (incident_log=1, lane_report=148, transcript_jsonl=0, verify_report=112), 248 with no records; refused: 41 records; skipped: 0 duplicates
41
$ sed -E 's/.*\(([^()]*)\)$/\1/' /tmp/j13r1/p/real.err | sort | uniq -c
      3 bad-class
     11 bad-title
     27 no-title-column
$ grep -E 'VERIFY-J1-0-R5-report.md:466|P5c-report|VERIFY-REPIN-a-R1-report.md:550' /tmp/j13r1/p/real.err; echo "P5c lines in stderr: $(grep -c P5c-report /tmp/j13r1/p/real.err)"
harvest-source-unparseable: tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md:550 (bad-class)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R5-report.md:466 (bad-title)
P5c lines in stderr: 0
$ git grep -n -P -i '^(?:- \*\*|\d+\. )BOUNDARY DEVIATION\b\s*(?:—|:|\*\*)' f772bfc -- 'tasks/briefs/*/*-report.md' 'tasks/briefs/*/report-pc-*.md' | grep -v -E '/VERIFY-[^/]*-report\.md:|/report-pc-verify-' | cut -c1-150
f772bfc:tasks/briefs/pc/report-pc-b7.md--c439580.md:100:9. Boundary deviation: `test:807-816` also had to change because the new evidence root is part
f772bfc:tasks/briefs/s0-01-p5c-support/P5c-report.md:13:- **BOUNDARY DEVIATION — `tests/conftest.py` was patched** (`synthetic_leg` fixture). The br
f772bfc:tasks/briefs/s0-02-support/B7-report.md:100:9. Boundary deviation: `test:807-816` also had to change because the new evidence root is partial 
$ git grep -l "$(printf '\342\200\250')" f772bfc -- docs tasks transcripts
f772bfc:tasks/briefs/laya/VERIFY-J1-1-report.md
f772bfc:tasks/briefs/laya/VERIFY-J1-2-R1-brief.md
```

The fifth `splitlines` site (`:260`, the registry parse), the brief's one-site flip, re-run verbatim (`/tmp/j13r1/p/premise2.sh`):

```
$ rm -rf /tmp/j13r1/p/reg && mkdir -p /tmp/j13r1/p/reg && cp -a tests/fixtures/decisions/sources /tmp/j13r1/p/reg/src && cp scripts/decide-harvest /tmp/j13r1/p/reg/pin.py && sed '260s/text.splitlines()/text.split("\\n")/' scripts/decide-harvest > /tmp/j13r1/p/reg/fix260.py && diff /tmp/j13r1/p/reg/pin.py /tmp/j13r1/p/reg/fix260.py
260c260
<     lines = text.splitlines()
---
>     lines = text.split("\n")
[rc=1]
$ python3 -c 'import pathlib; p = pathlib.Path("/tmp/j13r1/p/reg/src/docs/INCIDENT-LOG.md"); t = p.read_text(encoding="utf-8"); o = "| AF-AP-1 | uncommitted source accepted |"; assert t.count(o) == 1; p.write_text(t.replace(o, "| AF-AP-1 | uncommitted source\u2028accepted |"), encoding="utf-8")' && grep -c "$(printf '\342\200\250')" /tmp/j13r1/p/reg/src/docs/INCIDENT-LOG.md
1
[rc=0]
$ git -C /tmp/j13r1/p/reg/src init -q && git -C /tmp/j13r1/p/reg/src add -A && git -C /tmp/j13r1/p/reg/src -c user.name=f -c user.email=f@f commit -q -m f && echo committed
committed
[rc=0]
$ for v in pin fix260; do PYTHONPATH=/home/user/agent-factory/src /root/venv-agent-factory/bin/python /tmp/j13r1/p/reg/$v.py --root /tmp/j13r1/p/reg/src --out /tmp/j13r1/p/reg/$v.jsonl docs/INCIDENT-LOG.md > /tmp/j13r1/p/reg/$v.out 2> /tmp/j13r1/p/reg/$v.err; echo "== $v rc=$?"; head -1 /tmp/j13r1/p/reg/$v.out | cut -c1-60; cat /tmp/j13r1/p/reg/$v.err; done
== pin rc=3
harvest: 0 rows, per question type: ap.violates_row=0, b1.fi
harvest-source-unparseable: docs/INCIDENT-LOG.md:11 (no-registry-row)
harvest-source-unparseable: docs/INCIDENT-LOG.md:15 (no-registry-row)
== fix260 rc=0
harvest: 2 rows, per question type: ap.violates_row=2, b1.fi
[rc=0]
```

PREMISE VERDICT: MATCH on every line. The blob ids and line counts (`22b63bc47e7c 849`, `2cace4741511 581`, the four decisions files), the
fixture listing, the five `splitlines` sites (`scripts/decide-harvest@f772bfc:260`, `:303`, `:375`, `:515`, `:642`), the one `"HEAD"` at `:141`,
the `BOUNDARY_RE` at `:46-50`, the join at `:236-248`, the two `strip("*")` sites (`:352`, `:484`), `_report_paths` (`:361-369`),
`_regular_worktree_bytes` (`:156-163`), the append branch (`:818-834`), the two `JSONDecodeError` sites (`:645`, `:688`), the test
definitions (`tests/test_decide_harvest.py@f772bfc:300` `test_source_bytes_come_from_head_after_admission`, `:466`), `33 passed` on set `87e28761f102`, the unfixed real run (rc 3, `harvest: 232 rows`,
`ap.violates_row=121`, `v1.finding_class=109`, `wf.drift=2`, `refused: 41 records` = 3 `bad-class` + 11 `bad-title` + 27
`no-title-column`), the V5-05 and REPIN-a-R1:550 refusals, P5c's silence, the three contract drift anchors and the two U+2028 files all
equal the brief. The registry flip reproduces (`pin rc=3`, two `no-registry-row` at `:11` and `:15`; `fix260 rc=0`, `harvest: 2 rows`).
The `:11`/`:15` numbers are themselves F-04: the fixture's two entries sit at `\n` lines 10 and 14, and the U+2028 at line 7 shifts every
later `splitlines` index by one.

Venue drift (not a mismatch): the shared tree's HEAD moved during the lane (48e81f0 at 02:02:30Z, 0f75750 at 02:11Z; origin 8ea2932). The
boundary diff `f772bfc..HEAD` stayed 0 lines at both reads.

## 1. Relaunch state and plan (2026-09-24T02:25Z)

Relaunch after the owner's stop at about 02:13Z. Re-checked at 02:17:23Z: `git diff --stat f772bfc HEAD -- <boundary>` printed nothing (rc 0);
the working-tree blobs of `scripts/decide-harvest` and `tests/test_decide_harvest.py` are `22b63bc47e7c…` and `2cace4741511…`, equal to
the PIN's. `git status --porcelain` showed neither file modified. The §0 premise rows above are kept; they need no re-run.

Code intel: `node .gitnexus/run.cjs impact _heading_text --direction upstream --repo .` returned `"error": "Target '_heading_text' not
found"`, `"risk": "UNKNOWN"`. The suffix-less script is unmapped by the quartet (VERIFY-J1-3-R2 P-5 said so too). Fallback instrument:
the whole file read (`scripts/decide-harvest@f772bfc:1-849`, from `#!/usr/bin/env python3` on) and a literal-token sweep, `git grep -n decide-harvest`. The script's only code
consumers are `tests/test_decide_harvest.py` (subprocess and `runpy`) and the never-a-gate token list at `scripts/no_laya_in_gates.py:66` (`"decide-harvest", "decide_harvest"`).

Seam facts read from primary source before any edit:
- `append` (`src/agent_factory/decisions/ledger.py:432-504`) replays the file (`:452`), refuses a duplicate id (`:456-457`), and opens by
  path with `O_WRONLY|O_APPEND|O_CREAT|O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC` (`:468-473`). It never calls `flock`, so a lock that the
  harvester holds on its own fd cannot block its own appends.
- `replay` (`ledger.py:507-616`) reads a missing or empty file as `[]` (`:524-525`, `:550-551`) and raises `decision-row-duplicate` for an
  id seen twice (`:608-611`).
- `DecisionStateError` carries `.reason` and `.detail` (`src/agent_factory/decisions/volatile.py:124-128`), so R5(c)'s
  `exc.detail == row["row_id"]` is available.
- `volatile.py` spawns no subprocess, so no git call falls between two appends inside one run. A foreign writer that R5's m5b kill
  needs can only fire at a git read after the lock and the replay and before the first append. The existing lines it copies therefore
  come from a pre-seeded `--out`.
- `_nfc_collapse` (`volatile.py:151-154`) collapses `\s+` to one space. U+2028 is `\s`, so a state cell `a<U+2028>b` is stored as `a b`.

Plan (each step verified before the next): script edits for R1-R6 and S1, S5, S6 → new tests + the R2 inversion + S2 → the RED run
(the new test file against the PIN's script, `DECIDE_HARVEST_TEST_ROOT=/tmp/j13r1/pintree`) and the GREEN run → mutants → concurrency →
gates → the real run → the report.

## 2. Per contract line: the hunk, file:line, the reason

Diff against the PIN: `git diff --stat f772bfc -- scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions/` →
`scripts/decide-harvest | 159`, `tests/test_decide_harvest.py | 569`, `2 files changed, 680 insertions(+), 48 deletions(-)`. No fixture file
changed: every new record is appended inside the test's own copied tree. Lines below are the working tree's (sha256 `7022dd819436…`);
PIN lines are written `@f772bfc`.

| line | hunk (working tree) | what changed and why |
|---|---|---|
| R1 (F-01) | `scripts/decide-harvest:263-278`, `_heading_text` | `pieces` keeps every line that has no closing double asterisk; the close returns `" ".join(pieces + [piece[:close]])` whitespace-collapsed (`:276`). The PIN's `prefix = joined[:-1]` (`scripts/decide-harvest@f772bfc:244`) dropped the last collected piece. The window is still `range(10)` (`:269`, D-064 (3)). `_heading_text` is the only bold-span reader (`find("**")` occurs only at `:265` and `:274`); it serves the incident heading (`:338`) and the shape-B title (`:409`). |
| R2 (F-02) | `scripts/decide-harvest:49-53`, `BOUNDARY_RE` (one line, `:50`) | The pattern is now `^(?:- \*\*\|\d+\. )BOUNDARY DEVIATION\b\s*(?:—\|:\|\*\*)` with `re.IGNORECASE` (D-064 (1)). The `observed` extraction (`:548-554`) is unchanged: the rest of the line, left-stripped of ` —:*`, plus continuation lines. |
| R3 (F-03) | `_resolve_commit` `scripts/decide-harvest:143-149`; `_tree_paths(root, commit)` `:152-160`; `_head_blob(root, commit, path)` `:163-165`; `_admit(root, commit, …)` `:190-191`, `:204`; `main` `:830`, `:837`, `:840`, `:850`, `:853` | `git rev-parse --verify HEAD^{commit}` runs once (`:145`), right after `_repo_root` and before the output-conflict check and admission; its 40- or 64-hex id is the only rev any later git argument names: the tree listing (`:153`), every blob (`:164`), the admission comparison (`:204`), the conflict check (`:837`) and the registry read (`:853`). An unresolvable HEAD keeps the PIN's outcome (`return 64`, `:833`). `grep -nw HEAD` prints only `:145`. |
| R4 (F-04) | `_lines` `scripts/decide-harvest:254-260`; the five sites `:290` (`_registry`), `:333` (`_parse_incident`), `:403` (`_finding_candidates`), `:543` (`_parse_lane_report`), `:670` (`_parse_transcript`) | One helper splits on `"\n"` only, drops the final empty piece and one trailing `"\r"` per line. `grep -c splitlines scripts/decide-harvest` prints `0`. |
| R5 (D-063; F-05, F-12) | `_errno_name` `scripts/decide-harvest:788-789`; `_output_invalid` `:792-794`; `_claim_output` `:797-816`; `main` `:846-848`; the append split `:876-903` | (a) `os.open(--out, O_RDWR\|O_CREAT\|O_NOFOLLOW\|O_NONBLOCK\|O_CLOEXEC, 0o644)` (`:804`), `fstat` `S_ISREG` else `decision-ledger-not-regular`, `fcntl.flock(fd, LOCK_EX\|LOCK_NB)` (`:808`) whose `BlockingIOError` alone is `locked`; the fd is never closed, so the lock lives until the process exits. (b) `replay(path)` once (`:811`). Any failure is `harvest-output-invalid: <path> (<reason>)`, exit 6, no stdout (`:792-794`). (c) `make_row` and `append` now sit in two `try` blocks: a `make_row` refusal stays `state:<code>` (`:885-891`); a `decision-row-duplicate` from `append` is a skip only when `exc.detail == row["row_id"]` (`:897`); any other `DecisionStateError` or `OSError` from `append` returns exit 6 at once (`:901`, `:903`). Whole-run refusals 4/5/64 still run first (`:833`, `:837-839`, `:840-844`). |
| R6 (F-19) | `_parse_class` `scripts/decide-harvest:382` | `raw = cell.replace("*", "").strip()` (D-064 (2)); the rating cells (`_strip_rating`, `:512`) are unchanged. |
| S1 (F-06) | `_regular_worktree_bytes` `scripts/decide-harvest:168-187` | One `os.open(root / path, O_RDONLY\|O_NOFOLLOW\|O_NONBLOCK\|O_CLOEXEC)` (`:172`), `fstat` `S_ISREG` on that fd (`:176`), an `os.read` loop, `close` in `finally`. A FIFO, a symlink or a directory is `None`, so admission refuses `harvest-source-uncommitted`. |
| S5 (F-15) | `_report_paths` `scripts/decide-harvest:391-397` | The absolute-path branch (`scripts/decide-harvest@f772bfc:365-366`) is removed. The `root` parameter it orphaned is removed from `_report_paths`, `_finding_candidates` (`:400-402`) and `_candidates` (`:769`), and from their calls (`:481`, `:773`, `:864`). |
| S6 (F-11) | `scripts/decide-harvest:673` (a JSONL line), `:716` (a payload) | `except (ValueError, RecursionError)` in place of `except json.JSONDecodeError` (a `JSONDecodeError` is a `ValueError`). A line refuses `bad-json`; a payload refuses `bad-payload`. |
| S2 (F-07) | `tests/test_decide_harvest.py:393-395` | `test_source_bytes_come_from_head_after_admission` also asserts the `wf.drift` locator `BOUNDARY DEVIATION @ Build` (not `@ Changed`). |
| S3, S4 | tests only (§3) | No script change. |

## 3. Tests: every new test RED at the PIN, GREEN after

34 new test cases (23 new `def test_` functions: 26 at the PIN, 49 now) under the header comment `J1-3-R1` in `tests/test_decide_harvest.py:656-1144`; two new helpers, `_append_and_commit` (`:99-102`) and
`_git_shim` (`:105-126`); `_run` gained `env` and `timeout` keyword arguments (`:78-88`). Every new test runs the real script as a
subprocess, except the S1 forced-window test (a `runpy` probe, itself run as a subprocess with a 20 s timeout).

RED: the NEW test file against the PIN's script (`/tmp/j13r1/pintree`, a `git archive f772bfc` extract, script sha256 `befe924d3656`),
`DECIDE_HARVEST_TEST_ROOT=/tmp/j13r1/pintree … --tb=line -rf`, 2026-09-24T02:35:02Z:
```
30 failed, 37 passed in 37.46s
```
GREEN: the same file against my script, 02:50Z: `67 passed in 18.11s` and `67 passed in 18.42s` (§6).

| test (`tests/test_decide_harvest.py:<def>`) | line | RED at the PIN (the failure line, pasted) | GREEN |
|---|---|---|---|
| `test_wrapped_incident_heading_keeps_every_line[I-k]`, `[I-l]` (`:674`) | R1 | `AssertionError: assert [] == ['AF-AP-1', 'AF-AP-2']` (both) | passed |
| `test_wrapped_bullet_title_keeps_every_line[V-k]`, `[V-l]` (`:694`) | R1 | V-k `assert (3, 'harvest-...bad-title)\n') == (0, '')`; V-l `assert [('BLOCKER', ... part three')] == [('BLOCKER', ... part three')]` (the PIN's title is `part one part three`) | passed |
| `test_boundary_deviation_contract_anchor_forms[L-c]`, `[L-c2]`, `[L-c3]` (`:723`) | R2 | `assert [] == [('BOUNDARY D...required it')]` (all three) | passed |
| `test_boundary_deviation_requires_the_declared_delimiter` (`:505`, INVERTED, below) | R2 | `assert [] == ['touched an ... required it']` | passed |
| `test_head_moved_after_admission_rows_come_from_the_resolved_commit` (`:738`) | R3 | `assert {'a title fro...econd commit'} == {'malformed r...ntly dropped'}` (its shim assertions, `ls-tree` calls `2` and HEAD moved, passed first) | passed |
| `test_registry_line_separator_is_text_and_refusal_lines_count_newlines` (`:770`) | R4 `_registry` | `assert (3, 'harvest-...istry-row)\n') == (0, '')` | passed |
| `test_line_separator_before_an_incident_anchor_is_mid_line` (`:795`) | R4 `_parse_incident` (I-j) | `assert ['2026-01-01 ...rom mid-line'] == ['2026-01-01 ...P-2 happened']` | passed |
| `test_line_separator_in_a_verify_report_is_text[V-m]`, `[V-n]` (`:821`) | R4 `_finding_candidates` | V-m `assert ['F-1', 'F-2', 'F-13'] == ['F-1', 'F-2']`; V-n `assert ['F-1', 'F-2'] == ['F-1', 'F-2', 'F-14', 'F-15']` | passed |
| `test_line_separator_before_a_boundary_anchor_is_mid_line` (`:835`) | R4 `_parse_lane_report` (L-k) | `assert ['touched an ...rom mid-line'] == ['touched an ... required it']` | passed |
| `test_line_separator_inside_a_jsonl_string_is_one_record` (`:850`) | R4 `_parse_transcript` (T-g) | `assert (3, 'harvest-...no-result)\n') == (0, '')` | passed |
| `test_held_output_lock_is_refused_by_name_without_waiting` (`:871`) | R5 (a) | `assert (0, 'harvest:...duplicates\n') == (6, '')` | passed |
| `test_corrupt_output_ledger_is_refused_before_any_append` (`:888`) | R5 (b) | `assert (0, 'harvest:...duplicates\n') == (6, '')` | passed |
| `test_foreign_append_during_the_run_stops_it_by_name[copy-decision-row-duplicate]`, `[garbage-decision-ledger-unparseable]` (`:907`) | R5 (c) | copy `assert (0, 'harvest:...duplicates\n') == (6, '')`; garbage `assert (3, 'harvest:...duplicates\n') == (6, '')` | passed |
| `test_output_path_failures_are_one_named_refusal[missing-parent]`, `[symlink]`, `[fifo]`, `[directory]` (`:925`) | R5 (a), F-12 | missing-parent `assert (1, '') == (6, '')` (a traceback); symlink, fifo, directory `assert (3, 'harvest:...duplicates\n') == (6, '')` (`state:` record refusals) | passed |
| `test_class_cell_loses_every_asterisk` (`:949`) | R6 (V-r) | `assert (3, 'harvest-...bad-class)\n') == (0, '')` | passed |
| `test_admission_refuses_a_fifo_in_the_check_window_without_blocking` (`:962`) | S1 | `subprocess.TimeoutExpired: Command '[…/fifo_probe.py']' timed out after 20 seconds` (the hang) | passed |
| `test_paths_ignore_absolute_tokens_same_commit_at_two_roots` (`:1096`) | S5 | `assert b'{"calibrati...58f4b6c69"}\n' == b'{"calibrati...525bd5c77"}\n'` | passed |
| `test_json_parse_errors_beyond_decode_errors_are_refused_by_name[T-l]`, `[huge-int]`, `[T-m]` (`:1134`) | S6 | T-l `assert (1, 'Tracebac...ode string\n') == …`; huge-int `assert (1, 'Tracebac... the limit\n') == …`; T-m `assert (1, 'Tracebac...ode string\n') == …` | passed |
| `test_class_table_without_a_title_column_refuses_each_row` (`:1000`), `test_class_table_short_row_is_refused` (`:1015`), `test_registry_requires_the_exact_header` (`:1033`) | S3 | GREEN at the PIN by design; RED leg = mutants N3a, N3b, N3c (§4) | passed |
| `test_boundary_deviation_numbered_form_is_an_anchor` (`:1052`), `test_class_cell_qualifier_form_is_a_valid_class` (`:1070`), `test_rating_cell_leading_emoji_is_stripped` (`:1083`) | S4 | GREEN at the PIN by design; RED leg = mutants X2, X3, X5 (§4) | passed |
| `test_source_bytes_come_from_head_after_admission` (`:336`, extended, `:393-395`) | S2 | GREEN at the PIN by design; RED leg = the verifier's B-m5b (§4: `assert ['BOUNDARY DE...ON @ Changed'] == ['BOUNDARY DEVIATION @ Build']`) | passed |

The RED run's 37 passes are the 31 unchanged PIN tests plus the three S3 and three S4 tests (DISCREPANCY D-2).

The inverted test, `test_boundary_deviation_requires_the_declared_delimiter` (`tests/test_decide_harvest.py:505-532`):
- OLD (`tests/test_decide_harvest.py@f772bfc:466-477`): after `- **BOUNDARY DEVIATION** touched an extra fixture`,
  `assert all(row["question_id"] != "wf.drift" for row in replay(out))`.
- NEW: the same mutation yields exactly one row: `[row["state"]["observed"] for row in drift] == ["touched an extra fixture because the
  contract required it"]` (`:518-520`). The negative stays as the brief's own no-delimiter form, `1. BOUNDARY DEVIATION touched an extra
  fixture`, which yields no `wf.drift` row (`:522-532`). The PIN's test had only the one case (D-9).

The second changed existing test, `test_script_delegates_every_write_to_ledger_append` (`tests/test_decide_harvest.py:574-619`; D-1):
- OLD (`tests/test_decide_harvest.py@f772bfc:519-546`): the ledger import is `{"append", "make_row"}`, and there is no call to `open`, and
  no `.open`, `.write`, `.write_text` or `.write_bytes` attribute call.
- NEW: the import is `{"append", "make_row", "replay"}` (`:583`). Exactly two `os.open` calls exist, with their flag sets pinned
  (`:616-619`: the lock `O_CLOEXEC, O_CREAT, O_NOFOLLOW, O_NONBLOCK, O_RDWR` and the admission read `O_CLOEXEC, O_NOFOLLOW, O_NONBLOCK,
  O_RDONLY`). Every other write is still forbidden, and the list now also bans `ftruncate`, `truncate`, `pwrite` and `writev`
  (`:604-612`), the fd-level writers an `O_RDWR` fd would add. The mutants `ast-write` (an `os.write` on the lock fd) and `ast-trunc`
  (`O_TRUNC` added to the lock open) are killed by it (§4).

## 4. Mutation audit (scratch copies under `/tmp/j13r1/mut/`; the shared tree was never mutated)

Driver `/tmp/j13r1/mut/driver.py`. For each mutant it copies the base tree (my script, sha256 `7022dd819436`, equal to the working tree's),
applies each edit EXACTLY once (count asserted), proves the bytes differ, and runs `py_compile` (AF-AP-78). It then runs the WHOLE test
file against the mutant with `DECIDE_HARVEST_TEST_ROOT=<mutant>` (so the file collects and every test runs) and reads each named
killer's `FAILED` line. No mutant printed a `SyntaxError`, `ImportError`, `NameError` or `IndentationError` line (`crash=[]` in all 28).
Baseline (AF-AP-138), every named killer on the UNMUTATED base copy, 2026-09-24T02:49:00Z:
```
{"baseline_rc": 0, "killers": 32, "summary": ["32 passed in 9.84s"]}
```
Batches ran 02:38:11Z-02:48:55Z. TALLY: 28 mutants, 28 KILLED, 0 SURVIVED. The brief's list is m1, m2, m3a, m3b, m4a-m4e, m5a-m5d,
m6, the verifier's survivors X1-X5, B-m5b and N3 (three forms). I added s1, s6a, s6b (each S-line reverted alone) and ast-write,
ast-trunc (the D-1 test still bites).

| mutant | diff line (mutant's `scripts/decide-harvest:<n>`) | whole file | killing test | the reason in its output |
|---|---|---|---|---|
| m1 | `:276` `return _collapse(" ".join(pieces[:-1] + [piece[:close]])), None` | 4 failed, 63 passed | test_wrapped_incident_heading_keeps_every_line[I-k]<br>test_wrapped_incident_heading_keeps_every_line[I-l]<br>test_wrapped_bullet_title_keeps_every_line[V-k]<br>test_wrapped_bullet_title_keeps_every_line[V-l] | AssertionError: assert [] == ['AF-AP-1', 'AF-AP-2']<br>AssertionError: assert [] == ['AF-AP-1', 'AF-AP-2']<br>AssertionError: assert (3, 'harvest-...bad-title)\n') == (0, '')<br>AssertionError: assert [('BLOCKER', ... part three')] == [('BLOCKER', ... part three')] |
| m2 | `:50` `r"^(?:- \*\*BOUNDARY DEVIATION\*\*\|\d+\. BOUNDARY DEVIATION)"` | 4 failed, 63 passed | test_boundary_deviation_contract_anchor_forms[L-c]<br>test_boundary_deviation_contract_anchor_forms[L-c2]<br>test_boundary_deviation_contract_anchor_forms[L-c3]<br>test_boundary_deviation_requires_the_declared_delimiter | AssertionError: assert [] == [('BOUNDARY D...required it')]<br>AssertionError: assert [] == [('BOUNDARY D...required it')]<br>AssertionError: assert [] == [('BOUNDARY D...required it')]<br>AssertionError: assert [] == ['touched an ... required it'] |
| m3a | `:853` `incident_data = _head_blob(root, "HEAD", "docs/INCIDENT-LOG.md")` | 1 failed, 66 passed | test_head_moved_after_admission_rows_come_from_the_resolved_commit | AssertionError: assert {'a title fro...econd commit'} == {'malformed r...ntly dropped'} |
| m3b | `:153` `result = _git(root, "ls-tree", "-r", "--name-only", "-z", "HEAD")` | 1 failed, 66 passed | test_head_moved_after_admission_rows_come_from_the_resolved_commit | AssertionError: assert [] == ['src/existing.py'] |
| m4a | `:290` `lines = text.splitlines()` | 1 failed, 66 passed | test_registry_line_separator_is_text_and_refusal_lines_count_newlines | AssertionError: assert (3, 'harvest-...istry-row)\n') == (0, '') |
| m4b | `:333` `lines = source.text.splitlines()` | 2 failed, 65 passed | test_line_separator_before_an_incident_anchor_is_mid_line | AssertionError: assert ['2026-01-01 ...rom mid-line'] == ['2026-01-01 ...P-2 happened'] |
| m4c | `:403` `lines = source.text.splitlines()` | 2 failed, 65 passed | test_line_separator_in_a_verify_report_is_text[V-m]<br>test_line_separator_in_a_verify_report_is_text[V-n] | AssertionError: assert ['F-1', 'F-2', 'F-13'] == ['F-1', 'F-2']<br>AssertionError: assert ['F-1', 'F-2'] == ['F-1', 'F-2', 'F-14', 'F-15'] |
| m4d | `:543` `lines = source.text.splitlines()` | 1 failed, 66 passed | test_line_separator_before_a_boundary_anchor_is_mid_line | AssertionError: assert ['touched an ...rom mid-line'] == ['touched an ... required it'] |
| m4e | `:670` `for line_number, raw in enumerate(source.text.splitlines(), 1):` | 1 failed, 66 passed | test_line_separator_inside_a_jsonl_string_is_one_record | AssertionError: assert (3, 'harvest-...no-result)\n') == (0, '') |
| m5a | `:811` `pass` | 1 failed, 66 passed | test_corrupt_output_ledger_is_refused_before_any_append | AssertionError: assert 'decision-row...-duplicate)\n' == 'harvest-outp...-duplicate)\n' |
| m5b | `:897` `if exc.reason == "decision-row-duplicate":` | 1 failed, 66 passed | test_foreign_append_during_the_run_stops_it_by_name[copy-decision-row-duplicate] | AssertionError: assert (0, 'harvest:...duplicates\n') == (6, '') |
| m5c | `:808` `pass` | 1 failed, 66 passed | test_held_output_lock_is_refused_by_name_without_waiting | AssertionError: assert (0, 'harvest:...duplicates\n') == (6, '') |
| m5d | `:808` `fcntl.flock(fd, fcntl.LOCK_EX)` | 1 failed, 66 passed | test_held_output_lock_is_refused_by_name_without_waiting | subprocess.TimeoutExpired: Command '['/root/venv-agent-factory/bin/python', '/tmp/j13r1/mut/m5d/scripts/decide-harvest', '--root', '/tmp/j13r1/mut/bt/ |
| m6 | `:382` `raw = cell.strip().strip("*").strip()` | 1 failed, 66 passed | test_class_cell_loses_every_asterisk | AssertionError: assert (3, 'harvest-...bad-class)\n') == (0, '') |
| X1 | `:269` `for offset in range(1):` | 4 failed, 63 passed | test_wrapped_incident_heading_keeps_every_line[I-k]<br>test_wrapped_bullet_title_keeps_every_line[V-k] | AssertionError: assert (3, 'harvest-...d-heading)\n') == (0, '')<br>AssertionError: assert (3, 'harvest-...d-heading)\n') == (0, '') |
| X2 | `:50` `r"^(?:- \*\*)BOUNDARY DEVIATION\b"` | 1 failed, 66 passed | test_boundary_deviation_numbered_form_is_an_anchor | AssertionError: assert [] == ['touched an ... required it'] |
| X3 | `:385` `r"(?:, (?:SOLID\|UNSURE))?",` | 2 failed, 65 passed | test_class_cell_qualifier_form_is_a_valid_class | AssertionError: assert (3, 'harvest-...bad-class)\n') == (0, '') |
| X4 | `:391` `_X4_ROOT = None`<br>`:392` ``<br>`:393` ``<br>`:398` `if _X4_ROOT is not None and candidate.startswith(str(_X4_ROOT) + os.sep):`<br>`:399` `candidate = os.path.relpath(candidate, _X4_ROOT).replace(os.sep, "/")`<br>`:835` `globals()["_X4_ROOT"] = root` | 1 failed, 66 passed | test_paths_ignore_absolute_tokens_same_commit_at_two_roots | assert b'{"calibrati...58f4b6c69"}\n' == b'{"calibrati...525bd5c77"}\n' |
| X5 | `:513` `pass` | 1 failed, 66 passed | test_rating_cell_leading_emoji_is_stripped | AssertionError: assert (3, 'harvest-...ad-rating)\n') == (0, '') |
| B-m5b | `:863` `_wt = (root / source.path).read_bytes()`<br>`:864` `source = Source(source.path, source.kind, _wt, _wt.decode("utf-8"), source.digest)` | 1 failed, 66 passed | test_source_bytes_come_from_head_after_admission | AssertionError: assert ['BOUNDARY DE...ON @ Changed'] == ['BOUNDARY DEVIATION @ Build'] |
| N3a | `:439` `title_index = len(headers) - 1 if title_index is None else title_index` | 1 failed, 66 passed | test_class_table_without_a_title_column_refuses_each_row | AssertionError: assert (0, '') == (3, 'harvest-...le-column)\n') |
| N3b | `:444` `cells = cells + [""] * (len(headers) - len(cells))` | 1 failed, 66 passed | test_class_table_short_row_is_refused | AssertionError: assert (0, '') == (3, 'harvest-...table-row)\n') |
| N3c | `:296` `if (_split_table_row(lines[index]) or [])[:2] != header_cells[:2] or not _is_separator(_split_t` | 1 failed, 66 passed | test_registry_requires_the_exact_header | AssertionError: assert (0, '') == (3, 'harvest-...istry-row)\n') |
| s1 | `:171` `target = root / path`<br>`:172` `try:`<br>`:173` `if not target.is_file() or target.is_symlink():`<br>`:174` `return None`<br>`:175` `return target.read_bytes()`<br>`:176` `except OSError:`<br>`:177` `return None` | 1 failed, 66 passed | test_admission_refuses_a_fifo_in_the_check_window_without_blocking | subprocess.TimeoutExpired: Command '['/root/venv-agent-factory/bin/python', '/tmp/j13r1/mut/bt/s1/test_admission_refuses_a_fifo_0/fifo_probe.py']' tim |
| s6a | `:673` `except json.JSONDecodeError:  # JSONDecodeError is a ValueError; deep nesting recurses (S6)` | 2 failed, 65 passed | test_json_parse_errors_beyond_decode_errors_are_refused_by_name[T-l]<br>test_json_parse_errors_beyond_decode_errors_are_refused_by_name[huge-int] | AssertionError: assert (1, 'Tracebac...ode string\n') == (3, 'harvest-...(bad-json)\n')<br>AssertionError: assert (1, 'Tracebac... the limit\n') == (3, 'harvest-...(bad-json)\n') |
| s6b | `:716` `except json.JSONDecodeError:` | 1 failed, 66 passed | test_json_parse_errors_beyond_decode_errors_are_refused_by_name[T-m] | AssertionError: assert (1, 'Tracebac...ode string\n') == (3, 'harvest-...d-payload)\n') |
| ast-write | `:812` `os.write(fd, b"")` | 1 failed, 66 passed | test_script_delegates_every_write_to_ledger_append | assert [<ast.Call ob...7f40cd530160>] == [] |
| ast-trunc | `:804` `fd = os.open(path, os.O_RDWR \| os.O_CREAT \| os.O_TRUNC \| os.O_NOFOLLOW \| os.O_NONBLOCK \| os.O_C` | 6 failed, 61 passed | test_script_delegates_every_write_to_ledger_append | AssertionError: assert [['O_CLOEXEC'..., 'O_RDONLY']] == [['O_CLOEXEC'..., 'O_RDONLY']] |

Notes:
- m3a and m3b fail on different fields of the same test. m3a gets `row_title` from the second commit. m3b gets `paths` `[]` from the
  second commit's tree, which lacks `src/existing.py`. So the two reads are pinned separately.
- m4b also fails the registry test's second step (`<line>` `:11` in place of `:10`), so the `\n`-line numbering of refusals is
  pinned too.
- m5a dies only on the exact-stderr assertion. Its run also exits 6, through (c), but first prints a skip line. Measured in scratch
  (§8 (c)): `stderr='decision-row-duplicate: a5db82c6380f…115e\nharvest-output-invalid: …/c.jsonl (decision-row-duplicate)\n'`.
  An append-time replay alone reads a duplicate of the row it appends FIRST as that row's own skip; only the up-front replay
  refuses it before any line is printed.
- m5d and s1 die on their 20 s timeouts (the blocking `flock`; the FIFO open), as the brief requires.
- ast-trunc also reds five behavioral tests (`6 failed`): `O_TRUNC` empties an existing ledger.
- X4 on my code is the PIN's branch restored. `root` reaches `_report_paths` through a module global set in `main`, because S5
  removed the parameter.

## 5. The concurrency measurement (D-063's motivating case)

Driver `/tmp/j13r1/conc/conc.py`. It builds one fixture repo (the committed fixture tree, fixed author and date, 10 rows). For each of 40
pairs, it starts two `Popen` harvests back to back into the pair's own fresh `--out`. Each run is bounded by a 60 s timeout. Then it
runs `ledger.replay` on the final ledger. The repaired script ran at 2026-09-24T02:49:41Z; per run, pasted verbatim:
```
pair 00: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 01: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 02: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 03: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 04: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 05: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 06: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 07: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 08: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 09: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 10: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 11: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 12: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 13: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 14: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 15: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 16: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 17: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 18: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 19: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 20: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 21: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 22: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 23: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 24: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 25: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 26: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 27: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 28: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 29: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 30: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 31: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 32: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 33: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 34: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 35: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 36: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 37: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
pair 38: run A [6 (locked)] | run B [0 rows=10 skipped=0] | replay OK rows=10
pair 39: run A [0 rows=10 skipped=0] | run B [6 (locked)] | replay OK rows=10
mine: pairs=40 run outcomes={'0': 40, '6 (locked)': 40} ledgers={'accepted': 40}
```
RESULT: 80 runs = 40 × exit 0 (`harvest: 10 rows`) + 40 × exit 6 `(locked)`; 0 TIMEOUT. Every pair overlapped (in each pair one run was
refused `locked`). Ledgers: 40 of 40 accepted by `replay`, 10 rows each. **0 corrupt** (the bar; 32 of 40 at the PIN per R2).

Paired control, the same driver with the PIN's script (`/tmp/j13r1/pintree/scripts/decide-harvest`), 02:49:51Z, to show the instrument
produces the failure (first two and last two pairs, then the summary):
```
pair 00: run A [0 rows=2 skipped=8] | run B [0 rows=1 skipped=9] | replay REFUSED decision-row-duplicate lines=3
pair 01: run A [0 rows=10 skipped=0] | run B [0 rows=1 skipped=9] | replay REFUSED decision-row-duplicate lines=11
...
pair 38: run A [0 rows=2 skipped=8] | run B [0 rows=1 skipped=9] | replay REFUSED decision-row-duplicate lines=3
pair 39: run A [0 rows=2 skipped=8] | run B [0 rows=1 skipped=9] | replay REFUSED decision-row-duplicate lines=3
pin: pairs=40 run outcomes={'0': 80} ledgers={'accepted': 3, 'corrupt': 37}
```
37 of 40 PIN ledgers are corrupt, and every one of the 80 PIN runs exited 0. The verifier measured 32 of 40: the same class, at a rate
that depends on timing. A corrupt PIN pair such as `pair 00` reports `rows=2` + `rows=1` with 17 skips, while the file holds 3 lines and
2 distinct rows (F-05, reproduced).

## 6. Gates (sandbox; `/root/venv-agent-factory/bin/python` = Python 3.11.15; pytest-xdist is not installed, so every run is serial)

```
$ /root/venv-agent-factory/bin/python -V; /root/venv-agent-factory/bin/python -c 'import sys; print(sys.executable)'
Python 3.11.15
/root/venv-agent-factory/bin/python
$ rm -rf /tmp/j13r1/bt/r1 && python -m pytest -q -p no:cacheprovider --basetemp /tmp/j13r1/bt/r1 tests/test_decide_harvest.py   (2026-09-24T02:50:07Z)
67 passed in 18.11s
$ rm -rf /tmp/j13r1/bt/r1 /tmp/j13r1/bt/r2 && python -m pytest -q -p no:cacheprovider --basetemp /tmp/j13r1/bt/r2 tests/test_decide_harvest.py
67 passed in 18.42s
$ bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py
1 files set=87e28761f102
```
The counts agree (67 = 67). The PIN was `33 passed` on the same set id, which hashes the path list, not the file's bytes.

The PIN's own test file against my script. `/tmp/j13r1/pinfile` holds my script, `git show f772bfc:tests/test_decide_harvest.py` (blob
`2cace4741511`), the fixtures, `src/` and `tests/conftest.py`; 2026-09-24T02:50:56Z:
```
/tmp/j13r1/pinfile/tests/test_decide_harvest.py:477: assert False
/tmp/j13r1/pinfile/tests/test_decide_harvest.py:528: AssertionError: assert {'append', 'm...ow', 'replay'} == {'append', 'make_row'}
FAILED tests/test_decide_harvest.py::test_boundary_deviation_requires_the_declared_delimiter - assert False
FAILED tests/test_decide_harvest.py::test_script_delegates_every_write_to_ledger_append - AssertionError: assert {'append', 'm...ow', 'replay'} == {'append', 'make_row'}
2 failed, 31 passed in 9.44s
```
The first failure is the one R2 inverts. The second is D-1: R5 (a), R5 (b) and S1 require `os.open` and `replay`, which the PIN's AST
test forbids by name.

```
$ python -m pytest -q -p no:cacheprovider --basetemp /tmp/j13r1/bt/j1 tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/test_no_laya_in_gates.py   (02:51:15Z)
240 passed in 12.29s
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/test_no_laya_in_gates.py
3 files set=70db5efe1e9b
$ python -m pyflakes scripts/decide-harvest tests/test_decide_harvest.py; echo "pyflakes rc=$?"
pyflakes rc=0
$ python3 scripts/no_laya_in_gates.py; echo rc=$?
no_laya_in_gates: 40 files scanned, clean
rc=0
$ python3 scripts/ap_screen.py --tests scripts/decide-harvest tests/test_decide_harvest.py
--- TEST_SCREEN over 2 path(s): 1 hits over 2 files ---
AP-66: 1
    tests/test_decide_harvest.py:980: pathlib.Path.is_file = lambda self: self == fifo or real_is_file(self)
$ (the same screen over the PIN's two files, /tmp/j13r1/pintree)
--- TEST_SCREEN over 2 path(s): 0 hits over 2 files ---
$ grep -c splitlines scripts/decide-harvest
0
$ grep -n HEAD scripts/decide-harvest
54:MARKDOWN_HEADING_RE = re.compile(r"^#{1,6}\s+(?P<text>.+?)\s*$")
57:BUG_ECHO_HEADERS = (
145:    result = _git(root, "rev-parse", "--verify", "HEAD^{commit}")
283:        match = MARKDOWN_HEADING_RE.match(lines[index])
421:            if BULLET_FINDING_RE.match(lines[later]) or MARKDOWN_HEADING_RE.match(lines[later]):
551:                if not lines[later].strip() or MARKDOWN_HEADING_RE.match(lines[later]) or re.match(r"^(?:[-*+] |\d+\. )", lines[later]):
575:        if headers in BUG_ECHO_HEADERS and _is_separator(_split_table_row(lines[index + 1])):
$ grep -nw HEAD scripts/decide-harvest
145:    result = _git(root, "rev-parse", "--verify", "HEAD^{commit}")
$ python -m pytest tests/test_decide_harvest.py -q     (the seed's AC 4 verify_command, run literally with /usr/local/bin/python 3.11.15; 02:51:48Z)
67 passed in 19.53s
```
- New `ap_screen` hit against the PIN: exactly one, `AP-66` at `tests/test_decide_harvest.py:980` (`pathlib.Path.is_file = lambda`). It is
  by design. The line sits inside the source string of `fifo_probe.py`, which runs in its own subprocess, so the reassignment cannot
  outlive that process or leak into a later test. The test was not edited to silence the screen.
- `grep -n HEAD`: the only git argument is the resolve at `:145`. The other six lines are the identifiers `MARKDOWN_HEADING_RE` and
  `BUG_ECHO_HEADERS`, substring matches that were there at the PIN too (D-3).

## 7. THE REAL RUN (the deliverable KC-J7 reads)

Private clone at the PIN (the dispatch's venue fact; no `git worktree add`), 2026-09-24T02:52:28Z:
```
$ git clone -q --no-checkout --shared /home/user/agent-factory /tmp/j13r1/wt && git -C /tmp/j13r1/wt checkout -q --detach f772bfc && git -C /tmp/j13r1/wt rev-parse HEAD
f772bfc492fe65353cd63754dabd9f91e2c06490
$ git -C /tmp/j13r1/wt status --porcelain | wc -l      (before; the same 0 after all three runs)
0
$ for n in real real2; do /root/venv-agent-factory/bin/python scripts/decide-harvest --root /tmp/j13r1/wt --out /tmp/j13r1/$n.jsonl > /tmp/j13r1/$n.out 2> /tmp/j13r1/$n.err; echo "== $n rc=$?"; cat /tmp/j13r1/$n.out; echo "stderr lines: $(grep -c '' /tmp/j13r1/$n.err)"; done
== real rc=3
harvest: 235 rows, per question type: ap.violates_row=121, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=111, wf.drift=3
negatives: 0 (hand-labeled in J2)
sources: 261 read (incident_log=1, lane_report=148, transcript_jsonl=0, verify_report=112), 247 with no records; refused: 39 records; skipped: 0 duplicates
stderr lines: 39
== real2 rc=3
harvest: 235 rows, per question type: ap.violates_row=121, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=111, wf.drift=3
negatives: 0 (hand-labeled in J2)
sources: 261 read (incident_log=1, lane_report=148, transcript_jsonl=0, verify_report=112), 247 with no records; refused: 39 records; skipped: 0 duplicates
stderr lines: 39
$ cmp /tmp/j13r1/real.jsonl /tmp/j13r1/real2.jsonl; echo "cmp-jsonl rc=$?"; cmp …real.err …real2.err; cmp …real.out …real2.out
cmp-jsonl rc=0
cmp-stderr rc=0
cmp-stdout rc=0
$ rm -rf /tmp/j13r1/wt      (02:55:15Z, after the refusal reads below)
```

**Measured yield against KC-J7 (200 labels per type): every type is below 200. The highest-volume type is `ap.violates_row` at 121. Then
come `v1.finding_class` 111 and `wf.drift` 3; `b1.finding_kind`, `b1.finding_sev`, `b2.hit_role` and `d1.bug_echo_scores` are 0.**

Every stderr line of the repaired run (`/tmp/j13r1/real.err`, 39 lines; `real2.err` is byte-identical):
```
harvest-source-unparseable: tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md:725 (bad-class)
harvest-source-unparseable: tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md:743 (bad-class)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R4-report.md:749 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R4-report.md:751 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R4-report.md:760 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R4-report.md:762 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R4-report.md:764 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R4-report.md:765 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R5-report.md:505 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R5-report.md:525 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R6-report.md:280 (bad-title)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R6-report.md:287 (bad-title)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:209 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:210 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:211 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:212 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:213 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:214 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:215 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:216 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:217 (no-title-column)
harvest-source-unparseable: tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:218 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:428 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:429 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:430 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:431 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:432 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:433 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:434 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:435 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:436 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:437 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:438 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:439 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:440 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:441 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:442 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:443 (no-title-column)
harvest-source-unparseable: tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:444 (no-title-column)
```

### 7.1 Record-level accounting against the premise's unfixed run

Baseline: the clone's own PIN script, run once more on the same clone, reproduces the premise exactly:
```
== PIN baseline rc=3
harvest: 232 rows, per question type: ap.violates_row=121, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=109, wf.drift=2
negatives: 0 (hand-labeled in J2)
sources: 261 read (incident_log=1, lane_report=148, transcript_jsonl=0, verify_report=112), 248 with no records; refused: 41 records; skipped: 0 duplicates
stderr lines: 41
```
The diff, computed over refusal lines (`comm` of the sorted stderr files) and over rows (by `row_id`, then bytes):
```
--- stderr only in PIN:
harvest-source-unparseable: tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md:550 (bad-class)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R5-report.md:466 (bad-title)
--- stderr only in repaired:
rows pin 232 mine 235 common 232
--- only in PIN 0
--- only in repaired 3
  v1.finding_class ans=CONTRACT-DEFECT path=tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md loc='F2 @ FINDING INVENTORY (no severity filter; each with the blocking predicate applied)'
  v1.finding_class ans=BLOCKER path=tasks/briefs/laya/VERIFY-J1-0-R5-report.md loc="V5-05 @ FINDING INVENTORY (no severity filter; V5- ids are this lane's)"
  wf.drift ans=yes path=tasks/briefs/s0-01-p5c-support/P5c-report.md loc='BOUNDARY DEVIATION @ DEVIATIONS (flagged loudly, first-class)'
common ids with different row bytes: 0
```
Exactly three records moved, the same three the verifier's corrected copy moved at ff7a671. All 232 PIN rows are present,
byte-identical:

| record | PIN | repaired | the contract line that moved it |
|---|---|---|---|
| `tasks/briefs/laya/VERIFY-J1-0-R5-report.md:466` `V5-05 BLOCKER`, a bold title wrapped onto `:467` | refused `bad-title` | a `v1.finding_class` BLOCKER row. Its `title` carries text from `:467` (`… and shifts a literal blo`, cut by J1-1's own field limit); `paths` = `["scripts/no_laya_in_gates.py"]` | R1 |
| `tasks/briefs/s0-01-p5c-support/P5c-report.md:13` `- **BOUNDARY DEVIATION — …` | silent (no row, no refusal) | a `wf.drift` row, locator `BOUNDARY DEVIATION @ DEVIATIONS (flagged loudly, first-class)`; `observed` is 400 characters (J1-1's limit) and starts with the `tests/conftest.py` patch sentence | R2 (D-064 (1)) |
| `tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md:550` `**CONTRACT-DEFECT** (part of F1)` | refused `bad-class` | a `v1.finding_class` CONTRACT-DEFECT row, `finding_id` `F2`, `disposition` `BLOCKING` | R6 (D-064 (2)) |

Count check: rows 232 + 3 = 235 (`v1.finding_class` 109 + 2 = 111; `wf.drift` 2 + 1 = 3; `ap.violates_row` 121 = 121). Refused 41 − 2 =
39. "With no records" 248 − 1 = 247 (P5c now has a record). No other count moved. R3, R4, S1, S5 and S6 change nothing on this corpus:
- R3: the clone's HEAD did not move during the run.
- R4: the corpus's one U+2028 in a report, `tasks/briefs/laya/VERIFY-J1-1-report.md:243` (the row `U+2028, U+0085`), sits in a table that is not a class table, and
  that file yields no record either way.
- S1: the clone is clean, so admission reads only regular files.
- S5: see the count below.
- S6: no transcript JSONL is committed (`transcript_jsonl=0`).

S5's count, as the brief asks: backticked tokens in the 112 verify reports at the PIN, over whole files (a superset of the record texts),
through the script's own `BACKTICK_RE` and line-suffix strip:
```
verify reports: 112
  /home/rocco/agent-factory/: 12
  /home/user/agent-factory/: 2
  absolute tokens: 510
```
Of the 14 tokens under either repo root, 0 name a blob at the PIN (twelve are `.lanes/…` scratch paths; two are `sandbox-kit/…/plugin/…`
elisions). So the removed branch could not have added a path at any root on this corpus, which matches the verifier's 0 at ff7a671.

### 7.2 Every remaining refusal, read and classified (39)

Each record was read at the PIN (`sed -n '<n>p'` on the clone, before its removal):

| refusal | the record (pasted, cut) | classification |
|---|---|---|
| `tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md:725` (bad-class) | `\| A-4 \| FOLLOW-UP / UNVERIFIED \| PC transcripts harvested under the old rule …` | genuinely malformed by the contract: one cell names two classes, the exact example §4.2 refuses |
| `…/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md:743` (bad-class) | `\| B-6 \| FOLLOW-UP / UNVERIFIED \| The implicature that the other 109 directories ran Hermes …` | genuinely malformed by the contract (as above) |
| `tasks/briefs/laya/VERIFY-J1-0-R4-report.md:749` (bad-title) | `- **V-11 FOLLOW-UP (KNOWN class F-B4)** — \`sys.path\` shadowing …` | grammar limit: a qualifier after the class, and the title outside the bold |
| `…/VERIFY-J1-0-R4-report.md:751` (bad-title) | `- **V-12 FOLLOW-UP (KNOWN class F-B3)** — \`coproc . x\` …` | grammar limit: a qualifier, and the title outside the bold |
| `…/VERIFY-J1-0-R4-report.md:760` (bad-title) | `- **V-15 INFO** — …` (the title that follows the bold opens with a `lint_delta.py` citation) | grammar limit: the title outside the bold |
| `…/VERIFY-J1-0-R4-report.md:762` (bad-title) | `- **V-16 INFO** — a Python gate whose \`ast.parse\` raises RecursionError …` | grammar limit: the title outside the bold |
| `…/VERIFY-J1-0-R4-report.md:764` (bad-title) | `- **V-17 INFO** — quadratic cost in a run of leading keywords …` | grammar limit: the title outside the bold |
| `…/VERIFY-J1-0-R4-report.md:765` (bad-title) | `- **V-18 INFO** — a YAML alias yields the anchor's refusal line twice …` | grammar limit: the title outside the bold |
| `tasks/briefs/laya/VERIFY-J1-0-R5-report.md:505` (bad-title) | `- **V5-01 KNOWN (issue #37, class F-B3) — the command word spelled in ANSI-C or locale quoting.**` | grammar limit: a qualifier between the class and the ` — ` |
| `…/VERIFY-J1-0-R5-report.md:525` (bad-title) | `- **V5-12 INFO (KNOWN, V-14) — the recursion guard refuses bash-valid deep nests**` | grammar limit: a qualifier |
| `tasks/briefs/laya/VERIFY-J1-0-R6-report.md:280` (bad-title) | `- **F-3 INFO (KNOWN V-18) — an alias \`run: *x\` names the anchor's line, twice (f1).**` | grammar limit: a qualifier |
| `…/VERIFY-J1-0-R6-report.md:287` (bad-title) | `- **F-5 INFO (confirmations).**` | grammar limit: a qualifier, and no ` — ` title at all |
| `tasks/briefs/pc/report-pc-verify-m3.md--e776dd0.md:209-218` (10 × no-title-column) | header `:207` `\| ID \| class \| evidence \| contract mapping \| canonical path / effect \| reproduction \| minimal fix \|`; for example `\| F-32 \| **BLOCKER, SOLID** \| …` | grammar limit: 10 real findings (all 10 class cells parse, for example `**BLOCKER, SOLID**` → BLOCKER under R6) whose title column is named `canonical path / effect`, not `finding…`/`what` |
| `tasks/briefs/s0-01-a5k-support/VERIFY-CK12-report.md:428-444` (17 × no-title-column) | header `:426` `\| # \| class \| status on the PIN \| the run \|` under `## Item 8 — class status over SWEEP-prod's checker rows`; for example `\| 2 \| symlinked walk roots \| **OPEN** \| …` | grammar limit of the ANCHOR: not a finding table. 0 of 17 class cells parse; `class` there names an anti-pattern class. Refusing is the right outcome; no finding is lost |

Tally: 2 genuinely malformed; 37 grammar limits = 10 `bad-title` + 10 m3 rows + 17 CK12 rows. So 20 real findings are lost to the
strict grammar (the 10 `bad-title` bullets and the 10 m3 rows), and 17 refusals are a false anchor with nothing lost. F-22 check, line by
line: six `bad-title` lines carry a qualifier (R4 `:749`, `:751`; R5 `:505`, `:525`; R6 `:280`, `:287`) and four put the title outside the
bold (R4 `:760`, `:762`, `:764`, `:765`); R4 `:749` and `:751` have both. The PIN's eleventh `bad-title`, V5-05, was a valid wrap and is now
a row (R1). No grammar was widened.

## 8. Declared limits (measured in scratch, `/tmp/j13r1/limits/limits.py`, 2026-09-24T02:55:44Z; not committed tests)

```
(a) a run that appends no row
    rc=0 stdout[0]='harvest: 0 rows, per question type: ap.violates_row=0, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=0, wf.drift=0' stderr=''
    --out exists=True size=0 replay=[]
(b) the rows already appended stay after a mid-run harvest-output-invalid (in-process forced window)
    rc=6 stdout='' stderr='harvest-output-invalid: /tmp/j13r1/limits/work/b.jsonl (decision-row-duplicate)\n'
    appends before the failure=3 ledger lines=4 (3 harvester rows + 1 foreign copy) replay refuses decision-row-duplicate
(c) m5a (the up-front replay removed) on a ledger whose FIRST row is duplicated by hand
    repaired: rc=6 stdout='' stderr='harvest-output-invalid: /tmp/j13r1/limits/work/c.jsonl (decision-row-duplicate)\n'
    m5a: rc=6 stdout='' stderr='decision-row-duplicate: a5db82c6380f4b1b2e4a9888d3442a28d9f767b89b78c953d25c82e5b100115e\nharvest-output-invalid: /tmp/j13r1/limits/work/c.jsonl (decision-row-duplicate)\n'
(d) F-18 rows by construction, re-run on the repaired script (each appended to the matching fixture file)
    I-c: rc=0 new rows=1 [('ap.violates_row', 'yes', '2026-01-06 — AF-AP-1 did not recur this week', {'action_excerpt': '2026-01-06 — AF-AP-1 did not recur this week'})]
    L-b: rc=0 new rows=1 [('wf.drift', 'yes', 'BOUNDARY DEVIATION @ AF-AP-1 bug echo', {'observed': 'none — only the named files changed.'})]
    L-b2: rc=0 new rows=1 [('wf.drift', 'yes', 'BOUNDARY DEVIATION @ AF-AP-1 bug echo', {'observed': 'none**'})]
    V-c: rc=0 new rows=1 [('v1.finding_class', 'INFO', 'Note @ Findings', {'title': 'this bullet is prose, not a finding'})]
    V-o: rc=0 new rows=1 [('v1.finding_class', 'BLOCKER', 'F-16 @ Findings', {'title': 'inside a code fence'})]
    V-p: rc=0 new rows=1 [('v1.finding_class', 'BLOCKER', 'F-17 @ Findings', {'title': 'title with a'})]
    V-q: rc=0 new rows=1 [('v1.finding_class', 'BLOCKER', 'F-18 @ Findings', {'title': ''})]
```
(The block above is a re-run made while writing this section. Every line reads the same as the 02:55:44Z run in the lane transcript;
row ids are deterministic over the fixed fixture.)

1. **A run that appends no row leaves the empty `--out` that R5 (a) created** ((a) above: rc 0, `harvest: 0 rows`, size 0, `replay` → `[]`).
   Declared by the brief; `replay` reads an empty file as an empty ledger (`src/agent_factory/decisions/ledger.py:550-551`, `if not data:`).
2. **After a failure in R5 (c), the rows already appended stay** ((b) above: 3 harvester rows plus the foreign line; exit 6, one stderr
   line). The ledger is append-only, so the harvester never truncates. That ledger is now corrupt (the foreign copy), and every later
   harvest into it refuses at (b) with `decision-row-duplicate` until a human repairs it. The window was forced in-process, because no
   git call falls between two appends inside one run (D-6).
3. **F-18's rows by construction are unchanged, and R2 adds one form** ((d) above, repaired script):
   - I-c: a negation inside the incident heading gives a `yes` row.
   - L-b: a negation after `**BOUNDARY DEVIATION**:` gives a `yes` row.
   - NEW with R2: L-b2, `- **BOUNDARY DEVIATION: none**`, gives a `yes` row with `observed` `none**`. The contract anchor (D-064 (1))
     admits the colon inside the bold.
   - V-c: a prose word as a finding id. V-o: an anchor inside a code fence. V-p: an unescaped pipe cuts the title (`title with a`).
     V-q: an empty title gives a BLOCKER row with `title` `""`.
   - `_nearest_heading` (`scripts/decide-harvest:281-286`) also reads `#` lines inside code fences.
   These are grammar-by-construction rows for J2's labelling. None was "fixed" by narrowing a grammar.
4. **The lock is advisory and binds the inode opened at (a).** A writer that ignores `flock` is not stopped. It is detected at the next
   `append` (the m5b test). A process that renames another file over the path defeats the lock, because `replay` and `append` reopen
   by path. Residual of D-063 (2)'s rule: a foreign copy of exactly the row this run appends LAST, written after (b), reads as that row's
   own skip, so the run ends rc 0; the next run's (b) refuses the ledger.
5. **A directory `--out` refuses as `EISDIR`**: the declared `O_RDWR|O_CREAT` open fails before `fstat` can run. A FIFO or a device
   opens and refuses as `decision-ledger-not-regular` (the test's `fifo` case). `O_NOFOLLOW` covers the final path component only,
   the same limit `ledger.py` declares for itself (`src/agent_factory/decisions/ledger.py:18-19`).
6. **An `OSError` with no errno** would be named by its class (`_errno_name`, `scripts/decide-harvest:788-789`). No reachable call
   raises one.
7. **Repo shapes** (scratch, both scripts, identical outcomes): an unborn HEAD gives rc 64 `decide-harvest: --root is not a git work
   tree` and no `--out`; a `--object-format=sha256` repo gives rc 0 and 10 rows (the 64-hex id); a linked `git worktree` as `--root`
   gives rc 0 and 10 rows.

## 9. Self-attack: the three likeliest ways this change is wrong

1. **The lock does not really serialize writers.** Possible causes: `flock` held on another open file description than the appends,
   an early release by `close_fds`, or a child that inherits the fd.
   Ruled out:
   - (i) 40 of 40 overlapping pairs gave one `locked` refusal and 0 corrupt ledgers, while the same driver on the PIN corrupted 37
     of 40 (§5).
   - (ii) The held-lock test kills m5c (no lock) and m5d (a blocking lock, on its timeout) (§4).
   - (iii) `append` never calls `flock` (`ledger.py:432-504`), so the harvester's own lock cannot block its own appends. The fd is
     `O_CLOEXEC`, and `subprocess.run` closes fds by default, so no git child holds the lock after the harvester exits.
   Residual: the inode binding in §8 item 4.
2. **The `\n` line model moves rows or refusal lines on ordinary files** (a CRLF file, no final newline, trailing blank lines).
   Ruled out on the real corpus: all 232 PIN rows are byte-identical in the new ledger, and the 39 remaining refusal lines are the PIN's
   own lines (`comm` shows only the two moved records) (§7.1). The 33 PIN-era tests stay green. One trailing `\r` is dropped per line,
   which equals the old behavior for `\r\n` files. A lone `\r` is now text, by contract (R4).
3. **The single resolve changes admission or breaks a legitimate root.** Ruled out:
   - the fixture suite (67 passed) and the real run on a DETACHED clone (rc 3, the expected lines);
   - the unborn, SHA-256 and linked-worktree shapes behave as at the PIN (§8 item 7);
   - m3a and m3b are killed separately (§4);
   - `grep -nw HEAD` shows the one resolve (§6).
   Residual: a ref or tree that another process rewrites while its objects are GC-pruned is not covered; git objects of a resolved
   commit stay readable while the run holds no reference (inferred, not measured).

## Evidence tiers

| claim | tier |
|---|---|
| RED 30/67 at the PIN for the reasons pasted; GREEN 67/67 twice; seed AC 4 67 passed; J1 suites 240 passed; the PIN's test file 2 failed (R2 inversion + D-1) | verified (commands this session, §3, §6) |
| 28/28 mutants killed; 32/32 killers pass on the unmutated base; no mutant crashed | verified (§4) |
| 0 corrupt ledgers in 40 overlapping pairs; the PIN control 37/40 corrupt | verified (§5) |
| the real run: 235 rows, refused 39, deterministic (`cmp` 0 ×3); exactly three records moved; 232 PIN rows byte-identical | verified (§7) |
| every remaining refusal classified by reading the record | verified (§7.2) |
| the declared limits (a)-(d) and the repo shapes | verified in scratch (§8) |
| `flock` on the harvester's fd cannot block `append`'s own writes (per-description semantics) | inferred from `ledger.py:432-504` + measured indirectly (§5: the lock-holder appended 10 rows every time) |
| a resolved commit's objects stay readable for the run | inferred (§9 item 3) |

## DISCREPANCIES

- **D-1 (LOUD): a second existing test had to change, so the PIN's test file shows 2 failures, not 1.**
  - The brief's gate expects "every test passes except the one R2 inverts". But `test_script_delegates_every_write_to_ledger_append`
    (`tests/test_decide_harvest.py@f772bfc:519-546`) forbids every `os.open` call (an `.open` attribute call) and pins the ledger
    import to `{"append", "make_row"}`.
  - R5 (a) requires `os.open(--out, O_RDWR|O_CREAT|…)`, R5 (b) requires `ledger.replay`, and S1 requires `os.open(path, O_RDONLY|…)`.
    No script that meets R5 and S1 can pass that test unchanged.
  - Measured: the PIN's test file against my script gives `2 failed, 31 passed` (§6).
  - I narrowed the test; I did not delete it or game it. Exactly two `os.open` calls are admitted, each with its flag set pinned. The
    ledger import may add `replay`. The forbidden-writer list grew by `ftruncate`, `truncate`, `pwrite` and `writev`.
  - Mutants ast-write (`os.write` on the lock fd) and ast-trunc (`O_TRUNC`) prove it still bites (§4).
  - Old and new assertions are in §3. The coordinator may reject this change; the alternative is to amend R5 or S1.
- D-2: "Every new test is RED at the PIN" cannot hold for the S3 tests (3), the S4 tests (3) and S2's extension. They cover behavior
  the PIN already had right (the PIN's weakness there was a blind test, F-07/F-08/F-09). Their red leg is their mutant: N3a, N3b, N3c,
  X2, X3, X5 and B-m5b, all killed (§4). Measured: the RED run's 37 passes = the 31 unchanged PIN tests + these six (§3).
- D-3: `grep -n HEAD scripts/decide-harvest` also prints six lines for the identifiers `MARKDOWN_HEADING_RE` and `BUG_ECHO_HEADERS`
  (substring matches, present at the PIN). `grep -nw HEAD` prints only the resolve at `:145` (§6).
- D-4: the concurrency control at the PIN measured 37 of 40 corrupt ledgers; the verifier's R2 measured 32 of 40. Same class, a
  timing-dependent rate; the bar (0 corrupt with the repair) is met (§5).
- D-5: a directory `--out` is refused as `EISDIR`, not as `decision-ledger-not-regular`. The brief's own flags (`O_RDWR|O_CREAT`) make
  the open fail before `fstat` runs, and the brief's reason rule names an `OSError` by its errno (§8 item 5). The test pins `EISDIR`.
- D-6: the m5b kill writes the foreign line after the up-front replay and before this run's FIRST append, not "between two appends" of
  one run. No git call falls between two appends inside one run (`volatile.py` spawns no subprocess), so the `git` shim cannot fire
  there. The "existing line" therefore comes from a pre-seeded `--out`, and the next `append` names that other row's id. "The rows
  already appended stay" was shown with an in-process forced window in scratch (§8 item 2), not in a committed test.
- D-7: the R3 test moves HEAD with `git update-ref HEAD <second>` to a second commit it built beforehand, not a `git commit` run at the
  trigger. It builds that commit in its own pytest repo, then `git reset --hard` back to the first commit, IN THAT TEMP REPO ONLY. The
  effect the brief asks for is the same: HEAD names another commit between admission and the later reads.
- D-8: the brief says the inverted test's "no-delimiter negative stays". The PIN's test had one case only, and under D-064 (1) that
  case is a delimiter form. I added the brief's own no-delimiter form (`1. BOUNDARY DEVIATION touched …`) as the negative (§3).
- D-9: the contract anchor (R2) also mints `yes` rows from a negation written in the new forms: L-b2 gives `observed` `none**` (§8
  item 3). This is by construction (the F-18 class); I did not narrow the anchor.
- D-10: the venue.
  - The shared tree's HEAD moved during the lane (48e81f0 → 0f75750 → 247a39a → b74b63b); `git diff --stat f772bfc HEAD -- <boundary>`
    printed nothing at every read (02:02Z, 02:17Z, 02:57Z).
  - pytest-xdist is not installed, so every pytest run was serial (the dispatch's venue fact).
  - Every `../scratch/j13r1` path is `/tmp/j13r1`.
- D-11: one new `ap_screen` hit, AP-66, at `tests/test_decide_harvest.py:980` (`pathlib.Path.is_file`). It is by design (inside a subprocess probe's source
  string) and is not silenced (§6).

## NOT-done

- No commit and no push: the coordinator commits. The working tree holds `M scripts/decide-harvest`, `M tests/test_decide_harvest.py`
  and this report (`??`). No fixture file changed.
- No `/bug-echo` and no AF-AP registry row: `docs/INCIDENT-LOG.md` is outside this boundary. Classes for the coordinator:
  - F-01, a join that drops a collected piece;
  - F-02, an anchor narrower than its contract (a silent skip);
  - F-03, a symbolic ref re-resolved in each git call;
  - F-05, a duplicate refusal read as a skip on a corrupt ledger;
  - F-06, a path check followed by a second open;
  - F-04, an instance of AF-AP-132.
- No test drives a short write (`decision-ledger-short-write`) or an `OSError` from `append` in R5 (c). Neither can be forced without a
  decisions-module change or a fault injector. Both reach the same two return lines as the tested `decision-ledger-unparseable` case
  (`scripts/decide-harvest:901`, `:903`, both `_output_invalid`).
- The declared limits (§8) were measured by scratch probes, not committed tests.
- Out of scope by the brief (issue #61): F-10, F-13, F-14, F-16, F-17, F-20.
- GitNexus `detect_changes` was not run: the suffix-less script is not indexed (§1), so a zero would mean unseen, not unaffected. The
  quartet did not map this change. Its blast radius comes from the literal-token sweep (§1).
- No PC run (sandbox venue by dispatch). The seed's other acceptance criteria and the full `tests/` suite were not run; only the named
  gates were.

## Report lint (two runs; one fix round of three allowed)

- Round 1: `report_lint: 91 refs — OK 33, NEAR 0, MISS 9, UNCHECKABLE 49, UNRESOLVED 0 (worktree)`. All nine MISS lines cited the right line but carried no token copied from it. One was a pairing artifact: a two-character backtick span is below the lint's four-character token minimum, which shifted every later pair on that line. One was a citation inside a pasted record, which is now cut. Each fix added a copied identifier or reworded the line; no number changed.
- Round 2: `report_lint: 90 refs — OK 41, NEAR 0, MISS 0, UNCHECKABLE 49, UNRESOLVED 0 (worktree)`, rc 0, above the `--min-refs 15` floor. The 49 UNCHECKABLE refs are bare continuation refs (`:NNN`) and refs inside pasted command output.
