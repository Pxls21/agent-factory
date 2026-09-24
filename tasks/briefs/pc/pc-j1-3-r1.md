# PC lane J1-3-R1 (task #209; D-031, the ONE focused repair of J1-3; D-063 + D-064): wrapped titles, the drift anchor, one commit, `\n` lines, a guarded output ledger

PIN: f772bfc (the post-push origin head; `scripts/decide-harvest`, `tests/test_decide_harvest.py` and the fixture tree are unchanged since the J1-3 landing 379f277, so they are byte-identical at both verify pins a78bdca and ff7a671 — premise below)

Role: code-implementer. Route: the LOCAL build route (`agentfactory-build-local`, medium; D-061: local Hermes only while the owner's cloud
subscription is out). Claim nothing about which model wrote the code; the harvest measures the provider mix. Venue:
`tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey ultra, Lever-2: the report is DATA. Keep your context small: `| tail -n 40` on long
output, `sed -n` ranges instead of whole-file reads; the corpus files are large, so read them through your own scripts, never whole. Do NOT
spawn subagents.

AUTHORIZATION: a read-only harvester over the owner's own committed reports and logs. It writes only the ledger files you name under your
scratch directory; no credential, server or network is touched. Test secrets are fake strings only (`sk-QZJ8fake0123456789abcdef` style).

## WHY (read first)

VERIFY-J1-3-R2 (`tasks/briefs/laya/VERIFY-J1-3-R2-report.md`, a sandbox adversarial-verifier) returned J1-3 NOT-READY: four blockers in
`scripts/decide-harvest` (F-01..F-04) and one contract defect (F-05), which the coordinator amended as D-063. The coordinator reproduced
F-01, F-02 and the F-19 reading at the PIN, and measured a fifth `splitlines` site the verifier did not name (premise). This is the ONE
focused repair (D-031); no second round is pre-authorized. A contract line you cannot meet is a DISCREPANCY with its measurement, never a
silent change, and never a widened grammar.

CONTRACT SOURCES (read whole before you design): `tasks/briefs/laya/J1-3-brief.md` (the frozen J1-3 contract; it still governs except
where this brief amends it) · `tasks/briefs/pc/pc-j1-3.md` AMENDMENT A1 (still in force) · D-063 in `docs/08_DECISION_LOG.md` · D-064
(quoted in full below; it lands in the decision log after your PIN) · the R2 report's §3.2 (the hostile-input table: rebuild the named
cases from its text; the verifier's scratch tools are gone), §3.4 (the mutants X1-X8, B-m5b, N1-N3), §4 (the real run at two pins) and
§5 (every finding, each with a suggested fix).

## The contract — AMENDMENT 2 to J1-3 (decided; do not re-litigate)

D-064 (the coordinator's readings, 2026-09-24): (1) §4.3's "followed by `—`, `:` or `**`" allows whitespace between `DEVIATION` and the
delimiter (the implementation's own `\s*`). (2) §4.2's "The CLASS cell (asterisks stripped)" removes every `*` from the cell before the
token match, not only its ends. (3) "within 10 lines" is the anchor line and the nine lines after it (the implementation's `range(10)`).
(4) D-063's `harvest-output-invalid` exits 6; the lock is taken non-blocking, and a held lock is refused with the reason `locked`.

MUST:

R1 (F-01) — **a wrapped heading or title keeps every line.** The bold text runs from the opening `**` to the first closing `**` in the
window (D-064 (3)); every line's piece is kept, joined with one space and whitespace-collapsed, exactly as a one-line heading is. This
holds for the incident heading (§4.1) and the shape-B title (§4.2): fix the join (`_heading_text`, `scripts/decide-harvest:230-248`) and
every path that reads a wrapped bold text. Cases I-k, I-l, V-k and V-l (R2 §3.2) give the contract rows; for I-k the verifier's corrected
copy gave two `ap.violates_row` rows, each with the locator `2026-01-11 — AF-AP-1 first line continues with AF-AP-2 here`. On the real
corpus, `tasks/briefs/laya/VERIFY-J1-0-R5-report.md:466` (V5-05 BLOCKER; refused `bad-title` at the PIN) is harvested.

R2 (F-02) — **the drift anchor is the contract's.** `BOUNDARY_RE` (`:46-50`) matches exactly
`^(?:- \*\*|\d+\. )BOUNDARY DEVIATION\b\s*(?:—|:|\*\*)`, case-insensitive on the two words (D-064 (1)); the OBSERVED text stays §4.3's
(the rest of the line after the delimiter, plus its continuation lines). L-c, L-c2 and L-c3 each yield a row; a numbered line with no
delimiter (`1. BOUNDARY DEVIATION touched …`) yields none. `test_boundary_deviation_requires_the_declared_delimiter`
(`tests/test_decide_harvest.py:466`) pins the narrowed reading: its `- **BOUNDARY DEVIATION** touched …` case must now expect a row, and
its no-delimiter negative stays. On the real corpus the premise census finds three contract anchors in lane reports: the two
byte-identical B7 copies (harvested at the PIN, `wf.drift=2`) and `tasks/briefs/s0-01-p5c-support/P5c-report.md:13` (skipped silently
at the PIN); after the repair, `wf.drift=3`.

R3 (F-03) — **one commit per run.** Resolve `git rev-parse --verify HEAD^{commit}` ONCE, before admission, and name that commit id in
every later git read: the tree listing (`_tree_paths`, `:141`), every blob (`_head_blob`, `:152`), the admission comparison, and the
registry read from `docs/INCIDENT-LOG.md`. No git argument after the resolve names the symbolic `HEAD`. A test moves `HEAD` to a second
commit between admission and the later reads and asserts a CONTENT-BEARING field of the rows (a title, a `row_title` or a locator) comes
from the first commit; a digest-only assertion does not count (F-07). The verifier's deterministic control was a `git` wrapper first on
`PATH` that commits the second version at the harvester's N-th call; its no-wrapper racer gave 45 mixed rows in 300 runs at the PIN.

R4 (F-04) — **`\n` lines, at every site.** One helper splits text into lines on `\n` only; it drops the final empty piece and one trailing
`\r` per line. Every `splitlines` call in the file uses it. There are FIVE at the PIN (premise: `:260` `_registry`, `:303`
`_parse_incident`, `:375` `_finding_candidates`, `:515` `_parse_lane_report`, `:642` `_parse_transcript`); the verifier's report names
four, and `:260` is the fifth. After the repair `grep -c splitlines scripts/decide-harvest` prints 0. `<line>` in every refusal is the
1-based `\n` line of the committed blob. Cases I-j, V-m, V-n, L-k and T-g give the contract outcome, and so does the registry case the
premise measured: one U+2028 inside a registry cell refuses both fixture entries `no-registry-row` at the PIN, and fixing `:260` alone
harvests both rows.

R5 (D-063; F-05 and F-12) — **the output ledger is locked, replayed once, and refused by name.**
(a) After admission and before any source is parsed, open `--out` with `O_RDWR|O_CREAT|O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC` (mode 0644),
prove a regular file on the fd (`fstat`, `S_ISREG`; anything else is the reason `decision-ledger-not-regular`, the ledger's own code),
and take `fcntl.flock(fd, LOCK_EX|LOCK_NB)`; hold the fd and the lock until the process exits.
(b) Then replay `--out` once through `agent_factory.decisions.ledger.replay`.
(c) During the run, a `decision-row-duplicate` from `append` is a printed skip ONLY when `exc.detail == row["row_id"]`.
Any failure in (a) or (b), and any other `append` refusal in (c) (a duplicate that names another id, a `decision-ledger-*` code, a short
write), is ONE stderr line `harvest-output-invalid: <path> (<reason>)` and exit 6, with no stdout line. `<reason>` = `locked`, the
`DecisionStateError` code, or the errno name of an `OSError` (for example `ENOENT` for a missing parent directory, `ELOOP` for a
symlink). After a failure in (a) or (b), no row is appended and the existing bytes are unchanged. After a failure in (c), the run stops at
once and the rows already appended stay (the ledger is append-only; say so in the report). A `DecisionStateError` from `make_row` stays a
record refusal `state:<code>` (§4). Whole-run refusals 4, 5 and 64 still come first and never create or change `--out`. A run that
appends no row may leave the empty `--out` that (a) created (declared: `replay` reads an empty file as an empty ledger).

R6 (F-19; D-064 (2)) — **the class cell loses every asterisk.** The CLASS cell (`:352`) drops every `*` before the token match; the
rating cells (`:484`, another rule) are unchanged. V-r (`**CONTRACT-DEFECT** (x)`) is a valid CONTRACT-DEFECT row. On the real corpus,
`tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md:550` (refused `bad-class` at the PIN) is harvested.

SHOULD (this round, each with its own test; one you cannot meet is a NOT-done with its reason):

S1 (F-06) — the admission read of a working-tree file (`_regular_worktree_bytes`, `:156-163`) becomes one
`os.open(path, O_RDONLY|O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC)` and an `fstat` `S_ISREG` check on that fd (the ledger's own pattern,
`src/agent_factory/decisions/ledger.py:519-540`); a FIFO or a symlink is `harvest-source-uncommitted`, never a hang (the verifier's
racer hung 72 of 300 runs at the PIN). The test is RED at the PIN as a timeout-bounded hang (force the window deterministically, for
example load the script with `importlib` and make the old pre-check pass for a FIFO) and GREEN after.
S2 (F-07) — `test_source_bytes_come_from_head_after_admission` (`tests/test_decide_harvest.py:300`) also asserts a content-bearing field
(for example the `wf.drift` locator `BOUNDARY DEVIATION @ Build`, not `@ Changed`); the verifier's mutant B-m5b must red it.
S3 (F-08) — tests for `no-title-column` (a class table with no `finding…`/`what` column; 27 real refusals at the PIN), `bad-table-row`
(a short row), and the registry's exact header rule (a table with another header is not the registry); mutant N3 dies in all three forms.
S4 (F-09) — one test each for the numbered drift form (X2), the ` (<qualifier>)` class form (X3) and the emoji strip in a rating cell
(X5). X1 (wrapping) is R1's; X4 is S5's.
S5 (F-15) — `paths` counts only repo-relative tokens that are blobs of the resolved commit: remove the absolute-path branch
(`:365-366`). A test: the same commit harvested at two roots gives byte-identical ledgers. The verifier counted 0 absolute tokens in the
real verify reports at ff7a671; count them at the PIN and paste the count.
S6 (F-11) — a JSONL line or a payload whose parse raises `RecursionError` or `ValueError` is refused by name (`bad-json` for a line,
`bad-payload` for a payload), never a traceback: T-l and T-m (nesting 100000 deep).

OUT OF SCOPE (issue #61, the coordinator's): F-10, F-13, F-14, F-16, F-17, F-20. F-18's rows-by-construction are declared limits: state
them in the report, never "fix" them by narrowing a grammar.

## Tests (`tests/test_decide_harvest.py`)

Every new test is RED at the PIN and GREEN after; paste both runs. Every test runs the REAL script as a subprocess, except S1's
forced-window test. Fixtures follow the J1-3 brief's rules (a copied tree, `git init`, a fixed author, date and message). No existing test
is skipped or deleted; the one R2 inverts is named in the report with its old and new assertion.

## Mutation audit (scratch copies only; never `git checkout`, `git restore` or `git stash` in your tree)

Each mutant compiles and collects (AF-AP-78), and before you count a kill you run the killing test on the UNMUTATED copy and paste that
it passes (AF-AP-138). At least:
- m1: R1 reverted (the join drops the last collected piece again).
- m2: `BOUNDARY_RE` back to the PIN's pattern.
- m3a: the registry read names the symbolic `HEAD` again. m3b: the tree listing names `HEAD` again.
- m4a..m4e: each `splitlines` site restored ALONE (five mutants, five named tests).
- m5a: the up-front replay removed (a hand-duplicated row in `--out` must then red). m5b: every `decision-row-duplicate` counted as a
  skip (the kill needs a foreign writer that ignores the advisory lock and appends a copy of an existing line between two appends, for
  example the `git` wrapper at a chosen call; the next `append` names another row's id). m5c: the lock removed (the test holds
  `LOCK_EX` on `--out` itself). m5d: `LOCK_NB` removed (the held-lock test must then fail on its timeout).
- m6: the class cell stripped only at its ends again.
- The verifier's survivors rebuilt on your code: X1-X5, B-m5b and N3 (R2 §3.4).
Paste the table: mutant, the diff line, the killing test, the reason in its output. A survivor is reported with its reason, never hidden.

## The concurrency measurement (D-063's motivating case)

Re-run the verifier's case with your code: 40 pairs of runs started together, each pair into its own fresh `--out`, each run bounded by
a timeout. Paste the outcome per run (exit 0, or exit 6 `locked`) and, per final ledger, whether `replay` accepts it. The bar is 0
corrupt ledgers (32 of 40 at the PIN).

## Gates (paste every command with its output; each terminal call under the 420 s cap)

- `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/j13r1/bt/r<n> tests/test_decide_harvest.py` twice
  (`rm -rf` the basetemp between runs); the counts must agree; `bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py`
  (the PIN: `33 passed`, set `87e28761f102`).
- The PIN's own test file against your script (for example a scratch copy of your tree with `git show f772bfc:tests/test_decide_harvest.py`
  in place): every test passes except the one R2 inverts; paste the run.
- The J1 suites once: `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/j13r1/bt/j1 tests/test_decisions_canonical.py
  tests/test_decisions_ledger.py tests/test_no_laya_in_gates.py`, with its set id.
- `python -m pyflakes scripts/decide-harvest tests/test_decide_harvest.py`; `python3 scripts/no_laya_in_gates.py` (exit 0);
  `python3 scripts/ap_screen.py --tests scripts/decide-harvest tests/test_decide_harvest.py` (list the hits that are new against the PIN);
  `grep -c splitlines scripts/decide-harvest` (0); `grep -n HEAD scripts/decide-harvest` (only the one resolve and comments).
- The seed's AC 4 verify_command: `python -m pytest tests/test_decide_harvest.py -q`.

## THE REAL RUN (the deliverable KC-J7 reads)

In a private clone at the PIN (venue notes), run `python scripts/decide-harvest --root ../scratch/j13r1/wt --out ../scratch/j13r1/real.jsonl`
from your tree, then a second time into `real2.jsonl`; paste each exit code, the three stdout lines, EVERY stderr line and `cmp` of the
two files. Account for EVERY count that differs from the premise's unfixed run (`harvest: 232 rows`, `ap.violates_row=121`,
`v1.finding_class=109`, `wf.drift=2`, `refused: 41 records` = 3 `bad-class` + 11 `bad-title` + 27 `no-title-column`) by naming each
record that moved and the contract line that moved it. The verifier's corrected copy (F-01 + F-02 + F-19 together) moved exactly three
records at ff7a671: V5-05 (refused → a row), P5c:13 (silent → a row), REPIN-a-R1:550 (refused → a row). Explain any other movement record
by record. Classify every remaining refusal as a genuinely malformed record or a grammar limit, reading each record (F-22: the J1-3 lane
misclassified five of its nine `bad-title` lines). The first line after the real run states the measured yield against KC-J7's 200 per
type.

## Boundary and standing do-nots

MODIFY ONLY: `scripts/decide-harvest`, `tests/test_decide_harvest.py`, and files under `tests/fixtures/decisions/sources/` if a fixture
needs a new record (the existing tests stay green; name each fixture line you add). CREATE `tasks/briefs/laya/J1-3-R1-report.md` (write it
incrementally from the start). READ-ONLY: everything else, in particular `src/agent_factory/decisions/**` (J1-1 and J1-2, verified;
another lane edits `volatile.py` in ITS OWN tree on this host, and your tree keeps the PIN's bytes), `scripts/gate_files.txt` and the
never-a-gate token list: `scripts/decide-harvest` stays off every gate file (`scripts/no_laya_in_gates.py`). If a fix needs a decisions
module change, STOP and report. Never run git add, commit, stash, checkout, restore, reset or clean in your tree. Take no outward-facing
action. Paste every count and timestamp from command output. Long gates in ONE foreground call. A deviation from any contract line is
STOP-and-report; report adjacent defects, never fix them.

## Report (`tasks/briefs/laya/J1-3-R1-report.md`)

DATA: per contract line (R1-R6, S1-S6) the diff hunk with file:line and its reason; the RED→GREEN pair per new test; the mutant table;
the concurrency numbers; the gate outputs with set ids; the real run with the record-level accounting; the declared limits (F-18's rows
by construction, the empty `--out` from a zero-row run, the rows kept after a mid-run `harvest-output-invalid`); DISCREPANCIES; NOT-done.
`python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/J1-3-R1-report.md` (at most three fix rounds, then paste and finish).

## VENUE NOTES (this lane only)

- Every `/tmp/j13r1/…` path maps to `../scratch/j13r1/…` beside your tree. `/root/venv-agent-factory/bin/python` maps to
  `/home/rocco/venv-agent-factory/bin/python`; paste `python -V` and `python -c 'import sys; print(sys.executable)'` once.
- THE REAL RUN: never `git worktree add` on this host (your tree is itself a worktree of the main clone). Use a private clone:
  `git clone -q --no-checkout --shared /home/rocco/agent-factory ../scratch/j13r1/wt && git -C ../scratch/j13r1/wt checkout -q --detach f772bfc`,
  paste `git -C ../scratch/j13r1/wt rev-parse HEAD`, run, then `rm -rf ../scratch/j13r1/wt`.
- The other lane on this host: `pc-j1-1-r3.md--ff7a671` (J1-1-R3, editing `src/agent_factory/decisions/volatile.py` and two decisions
  test files in its own tree). Your edits stay in your tree.

## PREMISE — MEASURED at authoring (2026-09-24 01:23Z and 01:2xZ, /home/user/agent-factory@f772bfc == origin; generated by `scripts/premise_block.sh`, every command echoed exactly as it ran)
```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf; git rev-parse --short HEAD
2026-09-24T01:23Z
f772bfc
f772bfc
$ git log --format='%h %s' f772bfc -- scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions/sources | cut -c1-110
379f277 J1-3: scripts/decide-harvest + 33 tests + fixture sources (lane pc-j1-3.md--feb26d7), GATED-PENDING-VE
$ for f in scripts/decide-harvest tests/test_decide_harvest.py src/agent_factory/decisions/__init__.py src/agent_factory/decisions/canonical.py src/agent_factory/decisions/volatile.py src/agent_factory/decisions/ledger.py; do echo "$(git rev-parse f772bfc:$f | cut -c1-12) $(git show f772bfc:$f | wc -l) $f"; done
22b63bc47e7c 849 scripts/decide-harvest
2cace4741511 581 tests/test_decide_harvest.py
377ccd53da0c 24 src/agent_factory/decisions/__init__.py
607b65b613e2 78 src/agent_factory/decisions/canonical.py
bf04415d72c1 395 src/agent_factory/decisions/volatile.py
71fc398a5340 616 src/agent_factory/decisions/ledger.py
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
$ mkdir -p /tmp/j13r1p && /root/venv-agent-factory/bin/python -m pytest tests/test_decide_harvest.py -q -p no:cacheprovider --basetemp=/tmp/j13r1p/bt | tail -1
33 passed in 11.53s
$ bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py
1 files set=87e28761f102
$ git clone -q --no-checkout --shared /home/user/agent-factory /tmp/j13r1p/wt && git -C /tmp/j13r1p/wt checkout -q --detach f772bfc && git -C /tmp/j13r1p/wt rev-parse --short HEAD
f772bfc
$ /root/venv-agent-factory/bin/python scripts/decide-harvest --root /tmp/j13r1p/wt --out /tmp/j13r1p/real.jsonl > /tmp/j13r1p/real.out 2> /tmp/j13r1p/real.err; echo rc=$?; cat /tmp/j13r1p/real.out; grep -c . /tmp/j13r1p/real.err
rc=3
harvest: 232 rows, per question type: ap.violates_row=121, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=109, wf.drift=2
negatives: 0 (hand-labeled in J2)
sources: 261 read (incident_log=1, lane_report=148, transcript_jsonl=0, verify_report=112), 248 with no records; refused: 41 records; skipped: 0 duplicates
41
$ sed -E 's/.*\(([^()]*)\)$/\1/' /tmp/j13r1p/real.err | sort | uniq -c
      3 bad-class
     11 bad-title
     27 no-title-column
$ grep -E 'VERIFY-J1-0-R5-report.md:466|P5c-report|VERIFY-REPIN-a-R1-report.md:550' /tmp/j13r1p/real.err; echo "P5c lines in stderr: $(grep -c P5c-report /tmp/j13r1p/real.err)"
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
$ rm -rf /tmp/j13r1p/wt /tmp/j13r1p/bt; ls /tmp/j13r1p
real.err
real.jsonl
real.out
```

The fifth `splitlines` site (`:260`, the registry parse), measured as a one-site flip on a scratch copy of the fixture tree:
```
$ rm -rf /tmp/j13r1p/reg && mkdir -p /tmp/j13r1p/reg && cp -a tests/fixtures/decisions/sources /tmp/j13r1p/reg/src && cp scripts/decide-harvest /tmp/j13r1p/reg/pin.py && sed '260s/text.splitlines()/text.split("\\n")/' scripts/decide-harvest > /tmp/j13r1p/reg/fix260.py && diff /tmp/j13r1p/reg/pin.py /tmp/j13r1p/reg/fix260.py
260c260
<     lines = text.splitlines()
---
>     lines = text.split("\n")
[rc=1]
$ python3 -c 'import pathlib; p = pathlib.Path("/tmp/j13r1p/reg/src/docs/INCIDENT-LOG.md"); t = p.read_text(encoding="utf-8"); o = "| AF-AP-1 | uncommitted source accepted |"; assert t.count(o) == 1; p.write_text(t.replace(o, "| AF-AP-1 | uncommitted source\u2028accepted |"), encoding="utf-8")' && grep -c "$(printf '\342\200\250')" /tmp/j13r1p/reg/src/docs/INCIDENT-LOG.md
1
$ git -C /tmp/j13r1p/reg/src init -q && git -C /tmp/j13r1p/reg/src add -A && git -C /tmp/j13r1p/reg/src -c user.name=f -c user.email=f@f commit -q -m f && echo committed
committed
$ for v in pin fix260; do PYTHONPATH=/home/user/agent-factory/src /root/venv-agent-factory/bin/python /tmp/j13r1p/reg/$v.py --root /tmp/j13r1p/reg/src --out /tmp/j13r1p/reg/$v.jsonl docs/INCIDENT-LOG.md > /tmp/j13r1p/reg/$v.out 2> /tmp/j13r1p/reg/$v.err; echo "== $v rc=$?"; head -1 /tmp/j13r1p/reg/$v.out | cut -c1-60; cat /tmp/j13r1p/reg/$v.err; done
== pin rc=3
harvest: 0 rows, per question type: ap.violates_row=0, b1.fi
harvest-source-unparseable: docs/INCIDENT-LOG.md:11 (no-registry-row)
harvest-source-unparseable: docs/INCIDENT-LOG.md:15 (no-registry-row)
== fix260 rc=0
harvest: 2 rows, per question type: ap.violates_row=2, b1.fi
$ rm -rf /tmp/j13r1p; ls -d /tmp/j13r1p 2>&1 | cut -c1-60
ls: cannot access '/tmp/j13r1p': No such file or directory
```
