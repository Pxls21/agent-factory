# VERIFY-J1-3-R1 — the independent verify of the harvester's one focused repair (task #209; D-031, D-063, D-064, D-066)

PIN: 0d62801 (the post-push commit of the J1-3-R1 landing; `scripts/decide-harvest`, its tests, its fixtures and
`src/agent_factory/decisions/` are byte-identical at the origin head a923be5 — premise below).
ROLE: adversarial-verifier (sandbox, Opus 5.5, the SHARED tree read-only, no worktree isolation). Honey `full`. Do NOT spawn subagents.

## Why this lane exists

J1-3-R1 is the ONE focused repair of J1-3 under D-031, after VERIFY-J1-3-R2 returned NOT-READY (F-01..F-04 blockers, F-05 a contract
defect settled as D-063). The builder (a sandbox Opus 5.5 lane) reports every contract line built, 67 tests passing, 28 of 28 mutants
killed, 0 of 40 corrupt ledgers, and a real run that moved exactly the three predicted records. The coordinator re-ran its gates
(`67 passed`, the J1 suites `240 passed`); that is a second run of the builder's own oracle, not a verify (orchestration rule 0f). You
are the independent hostile pass: attack the CONTRACT with shapes the builder did not write, and reproduce its load-bearing claims
through the real script.

## Read in this order

1. The contract: `tasks/briefs/pc/pc-j1-3-r1.md` §"The contract — AMENDMENT 2 to J1-3" (R1-R6, S1-S6) and its WHY; D-063, D-064 and
   D-066 in `docs/08_DECISION_LOG.md` (D-066 is the coordinator's ruling on the builder's D-1: the write-delegation test narrowed to
   two pinned `os.open` calls).
2. The previous verify: `tasks/briefs/laya/VERIFY-J1-3-R2-report.md` (the findings F-01..F-26 this repair answers; issue #61 holds
   the ones outside it).
3. The builder's report: `tasks/briefs/laya/J1-3-R1-report.md` (claims to reproduce, never to trust).
4. The code: `scripts/decide-harvest`, `tests/test_decide_harvest.py`, and the ledger it writes through
   (`src/agent_factory/decisions/ledger.py`).

## Items (each with the command you ran and its output pasted)

1. PREMISE. Re-measure the block below. A mismatch that changes an item is CONTRACT-INVALID for that item; say which.
2. EACH CONTRACT LINE, ATTACKED WITH NEW SHAPES (at least three hostile inputs per line, never only the builder's cases), through the
   real script as a subprocess on scratch repositories:
   - R1 wrapped headings: 2-, 3- and 5-line wraps; mixed indentation; trailing spaces; a heading ending at EOF; a blank line inside;
     a list item right after.
   - R2 the drift anchor: every contract delimiter (`—`, `:`, `**`) and near misses (`–`, `-`, `;`, none, `BOUNDARY DEVIATIONS`,
     lower and mixed case, mid-line, inside a code fence, inside a table cell); multi-digit numbering (`10.`); whitespace between the
     words and the delimiter (D-064 (1)).
   - R3 one commit: a commit landing between reads (a background committer loop on a scratch repo during a run). Does any row mix
     paths or blobs from two commits?
   - R4 the `\n`-only splitter: U+2028, U+2029, U+0085, `\x0b`, `\x0c`, `\x1c`-`\x1e`, `\r\n`, a lone `\r`, at each of the five former
     `splitlines` sites.
   - R5 the output ledger: `--out` as a symlink, a dangling symlink, a FIFO, a directory (the builder's D-5), a path in a missing
     directory; a pre-existing file with a truncated last line, invalid JSON, valid JSON of the wrong shape, a bad digest, a
     hand-duplicated row (D-063 (1)); a held lock (exit 6 `locked`, non-blocking; D-064 (4)); concurrent runs (reproduce the 40-pair
     measurement at 20 pairs or more); a foreign writer that ignores the lock at a point the builder did not use (its D-6 says no git
     call falls between two appends: find another injection point, or show there is none); the created file's mode.
   - R6 the class cell: inner, doubled, escaped and bold-italic asterisks; underscores.
   - S1 sources that are a FIFO, a device and a socket: none may block or be read. S5: absolute paths in reports. S6: RecursionError
     and ValueError refused by name.
3. D-066, ATTACKED. Write mutants that write to `--out` without going through `append`: builtin `open(out, "a")`, `io.open`,
   `os.fdopen` on the claimed fd, `os.write` on it, `pathlib.Path.write_text`, `shutil.copyfile`, a third `os.open` with
   `O_WRONLY|O_APPEND`, a subprocess shell redirect. For each, say whether `test_script_delegates_every_write_to_ledger_append` (or any
   test) reds, and paste the output. A bypass that no test catches is a finding.
4. THE BUILDER'S CLAIMS, GRADED. Reproduce and mark REPRODUCED / REFUTED / UNVERIFIABLE: RED at the PIN's script (`30 failed, 37
   passed`); GREEN twice (`67 passed`, set 87e28761f102); the PIN's own test file against the repaired script (`2 failed`, both named);
   at least ten of its 28 mutants including m5a-m5d, X1-X5 and B-m5b, each with its killing test; the AF-AP-138 baseline (each killer
   passes on the unmutated copy); the concurrency result; the real run below.
5. YOUR OWN MUTANTS: at least eight that the builder did not list, each compiled and collected (AF-AP-78), each killing test run on the
   unmutated copy first (AF-AP-138). Paste the table: mutant, diff line, killing test, reason.
6. THE REAL RUN at f772bfc, in a private clone (`git clone -q --no-checkout /home/user/agent-factory /tmp/vj13r1/clone && git -C
   /tmp/vj13r1/clone checkout -q f772bfc`), twice into fresh files with the PIN's script (0d62801's `scripts/decide-harvest`, run from
   outside the clone): both harvest lines, the rc, `cmp` of the pair. The builder measured `harvest: 235 rows`, `refused: 39 records`,
   and exactly three records moved against the unfixed run (V5-05, P5c:13, REPIN-a-R1:550). Reproduce it and account for any
   difference record by record.
7. ADJACENT CONSUMERS: the J1 suites (`tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/test_no_laya_in_gates.py`,
   the builder's `240 passed`, set 70db5efe1e9b); `python3 scripts/no_laya_in_gates.py`; pyflakes on the two files.

## Venue and boundary

- Scratch: `/tmp/vj13r1/` (clones, mutants, fixtures); remove clones at the end. The sandbox had 3.5 GB free at authoring; one clone
  at a time (~200 MB).
- Python: `/root/venv-agent-factory/bin/python`; pytest `-p no:cacheprovider --basetemp=/tmp/vj13r1/bt<n>` (make the parent first).
  pytest-xdist is not installed: run serially. `bash scripts/pc_suite.sh set-id -- <files>` works here; no other pc_* script, no bridge.
- CREATE only `tasks/briefs/laya/VERIFY-J1-3-R1-report.md` (write it incrementally from the start). Never edit anything else in the
  repository. Another sandbox agent (J1-1-R3) works in a private clone at `/tmp/j113s/` and in `/tmp/vj11r2/`: never touch either.
  The coordinator commits ledger-plane files. Never run `git stash`, `checkout`, `restore`, `add`, `commit`, `worktree` or `push` in
  the shared tree. No outward-facing action. Never read `~/.hermes/`.
- CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
  `scripts/lane_context.sh -q 'how does decide-harvest claim its output file and append rows' -s _claim_output -s append -o /tmp/vj13r1/pack.md scripts/decide-harvest tests/test_decide_harvest.py`.

PREDICATE: a finding blocks only if it is contract-mapped, reproduced on the real path, materially effective (a row minted from
prose, bytes read after admission, a duplicate or corrupt ledger, a refusal that is not a refusal, a write that bypasses `append`),
with a concrete discriminator, and in-boundary. Report EVERY meaningful observation, with no severity filter, then apply the
predicate. Emit ONE `GATE RECOMMENDATION:` line — `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`.
The coordinator owns the gate. This is the ONE focused repair of J1-3: a NOT-READY goes to the owner with the contract question, not to
a second repair round.

Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-3-R1-report.md --root .`; apply its `fix:`
hints for at most three rounds, then paste and finish. The report ends with DISCREPANCIES and NOT-done, and states which items you ran
fully, partly or not at all (AF-AP-170: a recommendation over un-run items is void).

## PREMISE — MEASURED at authoring (2026-09-24 03:10Z, sandbox, uid 0; every command echoed exactly as it ran)
```
$ date -u +%Y-%m-%dT%H:%M:%SZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf; git rev-parse --short HEAD; id -u
2026-09-24T03:10:05Z
a923be5
a923be5
0
$ git diff --stat 0d62801 origin/claude/soundbox-kit-migration-iz1jwf -- scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions src/agent_factory/decisions | wc -l
0
$ git diff --stat f772bfc 0d62801 -- scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions src/agent_factory/decisions
 scripts/decide-harvest       | 159 ++++++++----
 tests/test_decide_harvest.py | 569 ++++++++++++++++++++++++++++++++++++++++++-
 2 files changed, 680 insertions(+), 48 deletions(-)
$ for f in scripts/decide-harvest tests/test_decide_harvest.py; do echo "$(git rev-parse 0d62801:$f | cut -c1-12) $(git show 0d62801:$f | wc -l) $f"; done
971e38803587 918 scripts/decide-harvest
bb0187044a6a 1144 tests/test_decide_harvest.py
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decide_harvest.py -q -p no:cacheprovider --basetemp=/tmp/vj13r1p/bt 2>&1 | tail -1 | sed -E "s/ in [0-9.]+s.*//"
67 passed
$ bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py
1 files set=87e28761f102
$ git show 0d62801:scripts/decide-harvest | grep -o -E "harvest-[a-z-]+|decision-row-[a-z-]+" | sort | uniq -c
      1 decision-row-duplicate
      1 harvest-output-invalid
      1 harvest-output-source-conflict
      1 harvest-source-uncommitted
      1 harvest-source-unknown
      3 harvest-source-unparseable
$ git show 0d62801:scripts/decide-harvest | grep -c "os\.open("
2
$ grep -n "^## " tasks/briefs/laya/J1-3-R1-report.md | head -20
8:## 0. Premise
199:## 1. Relaunch state and plan (2026-09-24T02:25Z)
227:## 2. Per contract line: the hunk, file:line, the reason
248:## 3. Tests: every new test RED at the PIN, GREEN after
303:## 4. Mutation audit (scratch copies under `/tmp/j13r1/mut/`; the shared tree was never mutated)
362:## 5. The concurrency measurement (D-063's motivating case)
427:## 6. Gates (sandbox; `/root/venv-agent-factory/bin/python` = Python 3.11.15; pytest-xdist is not installed, so every run is serial)
491:## 7. THE REAL RUN (the deliverable KC-J7 reads)
643:## 8. Declared limits (measured in scratch, `/tmp/j13r1/limits/limits.py`, 2026-09-24T02:55:44Z; not committed tests)
695:## 9. Self-attack: the three likeliest ways this change is wrong
718:## Evidence tiers
731:## DISCREPANCIES
772:## NOT-done
793:## Report lint (two runs; one fix round of three allowed)
$ grep -n -o -E "harvest: [0-9]+ rows|refused: [0-9]+ records" tasks/briefs/laya/J1-3-R1-report.md | head -6
1:harvest: 235 rows
1:refused: 39 records
139:harvest: 232 rows
141:refused: 41 records
177:harvest: 0 rows
181:harvest: 2 rows
$ df -h / | tail -1
/dev/vda        252G   34G  3.5G  91% /
```
Not measured at authoring, and so written as questions: whether any hostile shape in item 2 mints a row or corrupts a ledger, whether
any write in item 3 bypasses `append` unseen, whether any new mutant survives, and whether the real run reproduces 235 / 39 with the
same three moved records.
