# VERIFY-J1-3-R2 — completing the verify of `scripts/decide-harvest` (task #120) in the sandbox

PIN: ff7a671 (the origin head). `scripts/decide-harvest`, its tests, its fixtures and `src/agent_factory/decisions/` are
byte-identical at a78bdca (the first pass's PIN), at ff7a671 and at the shared tree's HEAD (premise below).
ROLE: adversarial-verifier (sandbox, agent on the D-054 pin, SHARED tree, no worktree isolation). Honey `full`. Do NOT spawn subagents.

## Why this lane exists

VERIFY-J1-3 (the PC local verify route, lane `pc-verify-j1-3.md--a78bdca`) came home 2026-09-23 23:5xZ with `GATE RECOMMENDATION:
MERGE-READY`, served HYBRID (qwen-local 18 x 200, antigravity/gemini-3.1-pro-low 17 x 200). Its report,
`tasks/briefs/laya/VERIFY-J1-3-report.md` (4.7 KB), skipped most of what its brief demanded: item 2 ran no FIFO, symlink swap or
background writer; item 3 wrote four hostile inputs in total; item 5 pasted no harvest lines, `cmp` or sampled rows; item 6 ran two
mutants, not the lane's plus five; item 7 ran the test file once and no pyflakes. The coordinator ruled it a PARTIAL verify: J1-3
stays GATED-PENDING-VERIFY. You finish the job.

**The first pass's brief governs:** `tasks/briefs/pc/pc-verify-j1-3.md`. READ IT WHOLE. Its "What landed, and the contract" section
(the frozen contract and its reading order: `seeds/seed-laya-j1-v1.yaml`, `tasks/laya-j1-breakdown.md`, `tasks/briefs/pc/pc-j1-3.md`
with AMENDMENT A1, the lane's report `tasks/briefs/laya/J1-3-report.md`), items 1-8, the "Known and out of scope" list and the
standing do-nots apply unchanged, with the venue mapping below. Attack the CONTRACT, never the builder's own cases alone.

## Items

1. PREMISE. Re-measure the block below. A mismatch that changes an item is CONTRACT-INVALID for that item; say which.
2. THE FIRST PASS, GRADED. For every claim in `tasks/briefs/laya/VERIFY-J1-3-report.md` (sections 1-7), reproduce it and mark it
   REPRODUCED / REFUTED / UNVERIFIABLE with your command and output. Its line cites are claims too.
3. ITEMS 2-7 OF THE FIRST BRIEF, IN FULL, as that brief states them: the committed-source rule under the three worktree races (a
   FIFO, a file swapped for a symlink, a background rewriter) with the deciding line for each; at least three hostile inputs per
   grammar with every named shape (prose that looks like records, a table without the declared columns, a duplicated header, a
   Unicode lookalike pipe or dash, a finding row split across lines, valid JSON of the wrong shape); identity and duplicates on a
   scratch repository; the real run (below); the lane's mutants plus the five named ones, each with its diff line, count and
   killing test; the gates.
4. THE REAL RUN, TWO PINS. In two private clones (below), one at a78bdca and one at ff7a671: the harvester twice each into fresh
   files, both harvest lines, the rc, `cmp` of each pair, three sampled rows with their `source_ref`. At a78bdca the first pass's
   brief measured `harvest: 214 rows` / `refused: 39 records` (premise below): reproduce it. At ff7a671 explain every difference
   from those numbers by source (the new reports and incident entries between the two pins; `git diff --stat a78bdca ff7a671`).

## Venue mapping (this lane only)

- `../scratch/` in the first brief is `/tmp/vj13r2/` here. The real run's "this PC clone at the PIN" is a PRIVATE clone per PIN:
  `git clone -q --no-checkout /home/user/agent-factory /tmp/vj13r2/clone-<pin>` then `git -C /tmp/vj13r2/clone-<pin> checkout -q
  <pin>` (never the shared tree: its HEAD moves while you work, and the harvester reads committed HEAD blobs).
- Python: `/root/venv-agent-factory/bin/python` if present, else `python`. pytest: `-p no:cacheprovider --basetemp=/tmp/vj13r2/bt<n>`
  (create the parent first). There is no 420 s cap here; a command still runs in ONE foreground call.
- The first brief's `scripts/pc_suite.sh set-id` works here as written.

## Boundary

CREATE `tasks/briefs/laya/VERIFY-J1-3-R2-report.md` (write it incrementally from the start); nothing else in the repository. Every
clone, mutant and scratch file lives under `/tmp/vj13r2/` and is removed at the end (the sandbox had 2.0 GB free at authoring: one
clone at a time if space is short). Another sandbox agent (VERIFY-S0-05) works under `/tmp/vs05/` and writes
`tasks/briefs/s0-05-support/VERIFY-S0-05-report.md`; the coordinator commits ledger-plane files (`todo/`, `docs/`, `wiki/`,
`STATUS.md`, `tasks/briefs/pc/`, `transcripts/`): never touch, run a writer against, or revert any of them. Never edit
`scripts/decide-harvest`, `tests/test_decide_harvest.py`, the fixtures or `src/agent_factory/decisions/` in the shared tree (a PC lane,
J1-1-R3, is changing the last on the PC; read it, never change it). Never run `git stash`, `git checkout` or `git restore` in the
shared tree, `git add`, `git commit`, `git worktree` or `git push`. No outward-facing action. Never read `~/.hermes/`.

CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
`scripts/lane_context.sh -q 'how does decide-harvest admit a source and parse each grammar' -s make_row -s append -o /tmp/vj13r2/pack.md scripts/decide-harvest tests/test_decide_harvest.py`.

PREDICATE (as in the first brief): a finding blocks only if it is contract-mapped, reproduced on the real path, materially
effective (a row minted from prose, bytes read after admission, a duplicate row written, a refusal that is not a refusal), with a
concrete discriminator, and in-boundary. Emit ONE GATE RECOMMENDATION: `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` /
`CONTRACT-INVALID`. The coordinator owns the final gate.

Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-3-R2-report.md --root .`; apply its `fix:`
hints for at most three rounds, then paste and finish. The report ends with DISCREPANCIES and NOT-done.

## PREMISE — MEASURED at authoring (2026-09-24 00:12Z, sandbox, uid 0; generated by `scripts/premise_block.sh`, every command echoed exactly as it ran)
```
$ date -u +%Y-%m-%dT%H:%M:%SZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf; git rev-parse --short HEAD; id -u
2026-09-24T00:12:35Z
ff7a671
bfc7687
0
$ git diff --stat a78bdca ff7a671 -- scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions src/agent_factory/decisions | wc -l
0
$ git diff --stat ff7a671 HEAD -- scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions src/agent_factory/decisions | wc -l
0
$ for f in scripts/decide-harvest tests/test_decide_harvest.py; do echo "$(git rev-parse ff7a671:$f | cut -c1-12) $(git show ff7a671:$f | wc -l) $f"; done
22b63bc47e7c 849 scripts/decide-harvest
2cace4741511 581 tests/test_decide_harvest.py
$ python -m pytest tests/test_decide_harvest.py -q -p no:cacheprovider --basetemp=/tmp/vj13r2p/bt | tail -1
33 passed in 10.05s
$ bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py
1 files set=87e28761f102
$ grep -o -E 'harvest-[a-z-]+|decision-row-[a-z-]+' scripts/decide-harvest | sort | uniq -c
      1 decision-row-duplicate
      1 harvest-output-source-conflict
      1 harvest-source-uncommitted
      1 harvest-source-unknown
      3 harvest-source-unparseable
$ grep -n '^## \|^GATE RECOMMENDATION' tasks/briefs/laya/VERIFY-J1-3-report.md
3:## 1. PREMISE
14:## 2. THE COMMITTED-SOURCE RULE
20:## 3. THE GRAMMARS, HOSTILE INPUTS
27:## 4. IDENTITY AND DUPLICATES
32:## 5. THE REAL RUN ON THIS PIN
37:## 6. MUTANTS
42:## 7. GATES
48:## 8. REPORT AND GATE RECOMMENDATION
49:GATE RECOMMENDATION: MERGE-READY
$ grep -n 'harvest: [0-9]* rows\|refused: [0-9]* records' tasks/briefs/pc/pc-verify-j1-3.md
147:harvest: 214 rows, per question type: ap.violates_row=115, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=97, wf.drift=2
149:sources: 252 read (incident_log=1, lane_report=148, transcript_jsonl=0, verify_report=103), 241 with no records; refused: 39 records; skipped: 0 duplicates
158:harvest: 207 rows, per question type: ap.violates_row=108, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=97, wf.drift=2
159:sources: 235 read (incident_log=1, lane_report=141, transcript_jsonl=0, verify_report=93), 224 with no records; refused: 39 records; skipped: 0 duplicates
$ df -h / | tail -1
/dev/vda        252G   36G  2.0G  95% /
```
The last `grep` pastes the first brief's own real run at a78bdca (its lines 147-159: the run on the PIN, then the lane's feb26d7
numbers it compared against). Not measured at authoring, and so written as questions: whether any race in item 3 lets bytes read
after admission into a row, whether any hostile input mints a row, whether any mutant survives, and what the real run gives at
ff7a671.
