# J1-3 — `scripts/decide-harvest`: the strict grammars, the committed-source rule, the harvest line (the KC-J7 measurement)

PIN: c6dcd61 (the origin head at authoring; the four READ-ONLY `src/agent_factory/decisions/` files are byte-identical in the worktree
and at origin, blob ids in the premise block; re-measure them first). LANE: laya-j1-3 (sandbox; agent `code-implementer`, in the SHARED
tree, no worktree isolation). Honey `ultra` Lever-2: your report is DATA: files:lines, pasted counts, discrepancies, NOT-done. Do NOT
spawn subagents.

CONTRACT: `seeds/seed-laya-j1-v1.yaml` AC 4 (`ac_bcb7dcea98dac36d`: "decide-harvest produces the ledger from the committed sandbox
transcript JSONL and PC lane reports, and rejects uncommitted or unknown sources with its exact declared error strings"; verify_command
`python -m pytest tests/test_decide_harvest.py -q`) · `tasks/laya-j1-breakdown.md` row J1-3 and the pinned decision "Harvest reads only
COMMITTED sources through STRICT grammars" · `docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md` J1 acceptance test 4 ("a malformed return is
refused by name, never silently dropped"; the harvest line, pasted verbatim) and KC-J7 (under 200 labels for the highest-volume type by
2026-11-03 → stop at the ledger) · D-046 (3) and D-047 (2) in `docs/08_DECISION_LOG.md` (the two capture-only types). Where this brief is
more specific than those texts, this brief is the frozen contract; a contradiction you find is STOP-and-report, never a self-accepted
change.

WHY THIS LANE EXISTS. J1-1 (canonical + volatile) and J1-2 (the append-only ledger) have landed and been verified. Nothing yet turns the
project's committed record of past decisions into ledger rows. J1-3 is that harvest, and its one printed line is the label-yield
measurement the council's KC-J7 reads. The premise block below measured the corpus at authoring: the yield will be SMALL (no committed
hive-scout or hive-reviewer return exists anywhere; the finding and incident shapes give roughly one hundred rows each). That is the
finding this increment exists to produce honestly. Never widen a grammar to raise a count.

## BOUNDARY (exact)
- CREATE `scripts/decide-harvest` (an executable Python 3 script, `#!/usr/bin/env python3`, no `.py` suffix; it puts its own repository's
  `src/` on `sys.path` so `agent_factory.decisions` imports from THIS repository whatever `--root` says).
- CREATE `tests/test_decide_harvest.py`.
- CREATE `tests/fixtures/decisions/sources/` (a miniature source tree, below).
- CREATE `tasks/briefs/laya/J1-3-report.md` (write it incrementally from the start).
- READ-ONLY: everything else, in particular `src/agent_factory/decisions/{__init__,canonical,volatile,ledger}.py` (J1-1's and J1-2's
  verified contracts) and `scripts/gate_files.txt`. If the harvest cannot be built without changing a decisions module (for example a
  source kind missing from `ledger._VALID_KINDS`), STOP-and-report; never edit it.
- `scripts/decide-harvest` is NOT a gate file and must never be named in one: `decide-harvest` is on the never-a-gate screen's token list
  (`scripts/no_laya_in_gates.py`). Add no reference to it in any file under `scripts/hooks/`, `.github/workflows/` or `scripts/gate_files.txt`.

## The contract

### 1. Command line
`scripts/decide-harvest --out <ledger.jsonl> [--root <dir>] [SOURCE ...]`
- `--root` defaults to the repository that holds the script. It must be a git work tree; the harvest reads source bytes ONLY from its
  `HEAD` commit (`git cat-file`/`git show HEAD:<path>`), never from the working tree.
- With no SOURCE argument the harvest DISCOVERS its sources: every path in `git ls-tree -r --name-only HEAD` that the kind table (§2)
  classifies, sorted bytewise. With SOURCE arguments it harvests exactly those (repo-relative paths), after the admission checks (§3).
- `--out` is appended through `agent_factory.decisions.ledger.append` only (the ledger's own writer; never an open-and-write of your own).
- Usage errors: exit 64 with one line on stderr.

### 2. The kind table (closed, root-anchored; `<d>` = one directory level, `<x>` = any file-name text)
| path shape | source kind (`source_ref.kind`) | grammar |
|---|---|---|
| `docs/INCIDENT-LOG.md` | `incident_log` | incident-log (§4.1) |
| `tasks/briefs/<d>/VERIFY-<x>-report.md` and `tasks/briefs/<d>/report-pc-verify-<x>.md` | `verify_report` | report-finding (§4.2) |
| `tasks/briefs/<d>/<x>-report.md` (not `VERIFY-`) and `tasks/briefs/<d>/report-pc-<x>.md` (not `report-pc-verify-`) | `lane_report` | lane-report (§4.3) |
| `transcripts/<d>/<x>.jsonl` | `transcript_jsonl` | transcript-return (§4.4) |
Anything else is not a source. Declared exclusions (measured at authoring, premise block): the committed chat digests
`transcripts/sandbox/chat-*.md` and `transcripts/pc/*.md` (markdown; the exporter strips tool results, so no record shape of §4 can occur
in them: 0 hive returns, 0 rating tables); `docs/research/bug-echo/*.md` (a bug-echo report is none of the five kinds `ledger._VALID_KINDS`
allows; one committed file). The kind `registry` is not a row source in J1-3: the registry table inside `docs/INCIDENT-LOG.md` is read only
as the lookup of §4.1.

### 3. Admission (whole-run refusals: nothing is read further, nothing is written, the ledger file is not created or changed)
- A SOURCE argument the kind table does not classify → stderr `harvest-source-unknown: <path>`, exit 5.
- A SOURCE argument that is not a blob in `HEAD`, or ANY source (argument or discovered) whose working-tree bytes differ from its `HEAD`
  blob (modified, deleted, or replaced by a non-regular file) → stderr `harvest-source-uncommitted: <path>`, exit 4.
- Check every source before reading any; report the FIRST refusal in sorted path order.

### 4. The grammars (strict; a record is found by an exact ANCHOR, then its body must parse completely)
A record whose anchor matches but whose body does not parse is REFUSED BY NAME: one stderr line
`harvest-source-unparseable: <path>:<line> (<reason>)` (`<line>` = the 1-based line of the anchor in the committed blob; for JSONL the
1-based line of the record holding the `tool_result`; `<reason>` = a short closed token you define and list in the report, for example
`bad-json`, `n-mismatch`, `unknown-role`, `bad-class`, `no-registry-row`, `unterminated-heading`, `state:<DecisionStateError code>`).
The refused record contributes no row; every other record is still harvested; the run ends with exit 3 (§5). A source with no anchor at all
contributes zero rows and is counted in the sources line (§5), never refused. Every row is built by `ledger.make_row` (never by hand) with
`root=<--root>`; a `DecisionStateError` from `make_row` is a refusal of that record with reason `state:<code>`.

**4.1 incident-log** (`docs/INCIDENT-LOG.md`) → `ap.violates_row`, answer `yes`, producer `coordinator`.
- Anchors: a line beginning `**YYYY-MM-DD` (the block form) or `- **YYYY-MM-DD` (the one-line form). The HEADING is the bold text from the
  opening `**` to the next `**`, which may sit on a later line; no closing `**` within 10 lines → refused (`unterminated-heading`).
- One row per DISTINCT `AF-AP-<n>` id in the HEADING (first-appearance order); ids in the entry's body are not attributions and are not read.
  An entry whose heading names no id yields no row.
- The registry: the table under `## ANTI-PATTERN REGISTRY` with the exact header row `| id | mechanism | greppable signature | proven
  instance | status |`; `row_title` = the row's mechanism cell (unescaped `|` splits cells; `\|` does not). An id with no registry row →
  refused (`no-registry-row`).
- state: `action_kind` = `report`, `action_target` = `docs/INCIDENT-LOG.md` (an incident entry is the written report of the action; declared,
  see §7), `action_excerpt` = the heading text, `row_id` = the id, `row_title` as above.
- locator: the heading text, whitespace-collapsed, first 200 characters.

**4.2 report-finding** (verify reports) → `v1.finding_class` (producer `adversarial-verifier`) and `ap.violates_row`.
- Record shape B (bullet): a line matching `^- \*\*<ID> <CLASS>\b` where `<ID>` = `[A-Za-z0-9][A-Za-z0-9._-]*` and `<CLASS>` is one of
  `BLOCKER`, `FOLLOW-UP`, `INFO`, `UNVERIFIED`, `CONTRACT-DEFECT`, `KNOWN`; the TITLE is the bold text after `<CLASS> — ` up to the closing `**`
  (it may wrap; 10-line limit as in 4.1). The record's text runs to the next anchor or the next markdown heading.
- Record shape T (class table): a table whose header row's first cell is `#` or `id` and second cell is `class` (case-insensitive), with the
  markdown separator row directly under it; each following row until the table ends is a record. The CLASS cell (asterisks stripped) must be
  exactly one `<CLASS>` token, optionally followed by `, SOLID`, `, UNSURE` or ` (<qualifier>)`; anything else (for example `FOLLOW-UP /
  UNVERIFIED`) → refused (`bad-class`). The TITLE is the first cell whose header (case-insensitive) starts with `finding` or equals `what`;
  a class table with no such column → each of its rows refused (`no-title-column`).
- `v1.finding_class` state: `lane` = the file name without `-report.md` (shape `VERIFY-<x>-report.md` → `VERIFY-<x>`) or without the leading
  `report-` (shape `report-pc-verify-<x>.md--<pin>.md` → `pc-verify-<x>.md--<pin>.md`; J1-1's normalizer strips the pin), `finding_id` = `<ID>`,
  `title`, `paths` = the sorted distinct backticked tokens in the record's text of the form `<path>` or `<path>:<digits>…` whose `<path>` is a
  blob in `HEAD` (line suffix dropped), `disposition` = `BLOCKING` for `BLOCKER`/`CONTRACT-DEFECT`, `NON-BLOCKING` otherwise. Answer = the
  `<CLASS>` token exactly.
- `ap.violates_row` from the same record: one row per distinct `AF-AP-<n>` id in the TITLE (shape B) or anywhere in the row (shape T); answer
  `yes`, producer `adversarial-verifier`, state `action_kind` = `report`, `action_target` = the report path, `action_excerpt` = the title,
  `row_id`, `row_title` from the §4.1 registry (read from `HEAD`'s `docs/INCIDENT-LOG.md` even when that file is not itself a harvested source;
  no registry row → refused).
- locator: `<ID> @ <the nearest preceding markdown heading text>`.

**4.3 lane-report** (builder lane reports) → `wf.drift` and `d1.bug_echo_scores`, producer `code-implementer` and `bug-echo`.
- `wf.drift` record: a line matching (case-insensitive on the two words) `^(?:- \*\*|\d+\. )BOUNDARY DEVIATION\b` followed by `—`, `:` or
  `**`; the OBSERVED text = the rest of the line and its continuation lines to the next blank line, list item or heading. State: `step_id`
  = `boundary-respected`, `drift_kind` = `out-of-boundary` (a boundary-deviation record is that drift by definition), `expected` = the
  fixed text `touch only the files the brief names`, `observed`; answer `yes`. The 60 NOT-done and 258 skipped lines D-047 counted are NOT
  harvested: mapping them onto the ten steps is J2's hand-labelling, not a grammar.
- `d1.bug_echo_scores` record: a row of a table whose header row is exactly one of the two bug-echo forms
  `| # | Finding | Urgency | Risk: Fix | Risk: No Fix | ROI | Blast Radius | Fix Effort | Status |` or
  `| # | Finding | Urgency | Risk: Fix | Risk: No Fix | ROI | Blast | Effort | Status |` (`.claude/skills/bug-echo/SKILL.md`, Step 5).
  State: `class_slug` = the first `AF-AP-<n>` id in the nearest preceding markdown heading (none → refused, `no-class-slug`),
  `finding_title` = the Finding cell. Each rating cell is read after stripping a leading emoji and whitespace, case-insensitively, against
  the skill's closed vocabularies (Urgency CRITICAL/HIGH/MEDIUM/LOW; Risk: Fix LOW/MEDIUM/HIGH/CRITICAL; Risk: No Fix LOW/MEDIUM/HIGH/CRITICAL;
  ROI EXCELLENT/GOOD/MARGINAL/POOR; Blast `1 file` → `1-file`, `<n> files` → `n-files`, `<n>+ files` → `n-plus-files`; Effort
  TRIVIAL/SMALL/MEDIUM/LARGE); a value outside → refused (`bad-rating`). Answer =
  `urgency=<u>;risk_fix=<f>;risk_no_fix=<n>;roi=<r>;blast=<b>;effort=<e>`, every level lower-case.
- locator: `BOUNDARY DEVIATION @ <nearest heading>` / `<#> @ <nearest heading>`.

**4.4 transcript-return** (committed Claude Code transcript JSONL) → `b2.hit_role` (producer `hive-scout`) and `b1.finding_sev` +
`b1.finding_kind` (producer `hive-reviewer`).
- Anchor: an assistant record whose `message.content` holds a `tool_use` block with `name` `Agent` or `Task` and `input.subagent_type`
  `hive-scout` or `hive-reviewer`. Its return is the later user record holding a `tool_result` block with the same `tool_use_id`; no such
  record → refused (`no-result`) at the anchor's line. A line of the file that is not valid JSON → refused (`bad-json`) at that line.
- The payload = the concatenated `text` blocks of the `tool_result` content, EXCEPT a final text block that starts with `agentId:` (the
  harness trailer; premise block: 7 of 209 results carry it as a separate block). The payload must parse as JSON of the producer's declared
  shape (`.claude/agents/hive-scout.md`, `.claude/agents/hive-reviewer.md`): scout `{"hits":[{"id","sym","file","line","role"[,"note"]}],"n":N}`,
  reviewer `{"c":["id","sev","file","line","kind","msg"],"r":[[…]],"n":N}`; `n` must equal the row count (`n-mismatch`); an ESON payload, an
  async-launch acknowledgement or any other text → refused (`bad-payload`).
- scout, one row per hit: state `sym`, `file`, `snippet` = the hit's `note` or the empty string (the scout's return carries no hit-line text:
  declared, §7); answer = `role` ∈ {def, caller, config, test, other} (else `unknown-role`).
- reviewer, TWO rows per finding: `b1.finding_sev` and `b1.finding_kind`, both with state `file`, `kind`, `msg`; answers `sev` ∈ {H, M, L}
  (else `unknown-sev`) and the `kind` slug (`^[a-z0-9]+(?:-[a-z0-9]+)*$`, else `bad-kind`).
- locator: `<the tool_result record's uuid>#<hit or finding id>`.

### 5. Output, exit codes, determinism
- stdout, exactly three lines, in this order (a whole-run refusal prints none of them):
  `harvest: <n> rows, per question type: ap.violates_row=<a>, b1.finding_kind=<b>, b1.finding_sev=<c>, b2.hit_role=<d>, d1.bug_echo_scores=<e>, v1.finding_class=<f>, wf.drift=<g>`
  `negatives: 0 (hand-labeled in J2)`
  `sources: <s> read (incident_log=<i>, lane_report=<l>, transcript_jsonl=<t>, verify_report=<v>), <z> with no records; refused: <r> records; skipped: <k> duplicates`
  `<n>` = rows appended by THIS run; all seven types always printed, zeros included, in that order.
- Duplicates: `ledger.append` refuses an existing row id (`decision-row-duplicate`); the harvest prints that line on stderr, counts it in
  `skipped`, and continues (the breakdown's "printed skip").
- Exit 0 = no refusal; exit 3 = at least one record refused (the rows of every other record ARE appended); 4 / 5 / 64 as above.
- Order: sources in sorted path order, records in file order, rows per record in the order of §4. Two runs over the same commit into two
  fresh `--out` files → byte-identical files. A second run into the SAME `--out` → exit 0, `harvest: 0 rows`, every row a printed skip,
  the file byte-identical to before.
- The real run is NOT committed as data (the J1 boundary holds no ledger file); its three lines are pasted in the report.

## Tests (`tests/test_decide_harvest.py`; normal, failure, boundary; each run through the REAL script as a subprocess)
The fixture tree `tests/fixtures/decisions/sources/` holds, at the kind table's own paths: `docs/INCIDENT-LOG.md` (block and one-line
entries naming ids, one entry naming none, a registry table), `tasks/briefs/x/VERIFY-X-report.md` (shape B and shape T findings, one with an
`AF-AP-<n>` id in its title, backticked paths some of which exist in the fixture commit), `tasks/briefs/x/X-report.md` (one boundary
deviation, one bug-echo rating table under a heading naming an id), `transcripts/x/t.jsonl` (one hive-scout and one hive-reviewer
dispatch with their results, one with the `agentId:` trailer block). Each test copies the tree into its tmp dir, `git init`s it, commits it
with a fixed author, date and message, and runs the script against it. Fake strings only (a planted secret looks like
`sk-QZJ8fake0123456789abcdef`, never a real one). At least:
(a) the fixture harvest: the exact per-type counts (compute them by hand from YOUR fixture and write them in the test), the three stdout
lines exactly, exit 0, and `ledger.replay` of the output returns the rows with the expected `question_id`, `incumbent_answer`,
`source_ref.kind/path/locator` for one row per type;
(b) determinism: two runs into two files → identical bytes; a re-landing variant (a blank line inserted at the top of every source,
committed as a second commit) → identical `row_id`s and `state_digest`s, only `source_ref.source_digest` differs;
(c) the duplicate re-run into the same file (the printed skips, exit 0, the file unchanged);
(d) one malformed record per grammar (at least: an incident heading with no closing `**`; a class-table row with `FOLLOW-UP / UNVERIFIED`;
an id with no registry row; a reviewer payload whose `n` disagrees; a scout hit with role `helper`; a rating cell outside the vocabulary) →
exit 3, the exact stderr line, `refused: <k>`, and every OTHER row still present;
(e) admission: an untracked SOURCE argument and a modified tracked source → `harvest-source-uncommitted: <path>`, exit 4, no `--out` file
created; an existing `--out` untouched; a committed path outside the kind table given as SOURCE → `harvest-source-unknown: <path>`, exit 5;
(f) the seven-type line with some types absent (a fixture subset) prints them as `=0`;
(g) security boundary: a planted fake secret in a finding title and in a hive `msg` is absent from the `--out` bytes (J1-1's redaction,
reached through `make_row`);
(h) the working-tree independence: a tracked source's HEAD bytes are what is harvested when the tree is clean (a control for (e)).
Run the new file twice; the counts must match.

## Mutants (each on a scratch copy under `/tmp/j13/mut/`; never in the shared tree; each must red a NAMED test for the stated reason)
m1 a malformed record skipped silently (no stderr line, not counted) → (d) red · m2 the committed check removed (an untracked source read) →
(e) red · m3 one question type dropped from the harvest line → (a)/(f) red · m4 the duplicate skip made silent → (c) red · m5 the source read
from the working tree instead of `HEAD` → (e) or (h) red · m6 the `n` checksum not checked → (d) red · m7 a missing registry row given a
placeholder title → (d) red · m8 `--out` written by the script's own `open()` instead of `ledger.append` → a named test red (state which, or
say why none can see it). Paste the table: mutant, the diff line, the failing test, the reason in its output.

## Gates (paste verbatim)
- `mkdir -p /tmp/j13/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_decide_harvest.py -q -p no:cacheprovider --basetemp=/tmp/j13/bt` twice (rm -rf the basetemp between runs); the counts must agree.
- The J1 suites unchanged: `/root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j13/bt2` once, pasted.
- `python -m pyflakes scripts/decide-harvest tests/test_decide_harvest.py`; `python3 scripts/no_laya_in_gates.py` (exit 0);
  `python3 scripts/ap_screen.py --tests scripts/decide-harvest tests/test_decide_harvest.py`.
- The seed's AC 4 verify_command, pasted.
- THE REAL RUN (the deliverable KC-J7 reads): in a clean detached worktree of the current origin head
  (`git worktree add --detach /tmp/j13/wt origin/claude/soundbox-kit-migration-iz1jwf`; paste its SHA), run
  `/root/venv-agent-factory/bin/python scripts/decide-harvest --root /tmp/j13/wt --out /tmp/j13/real.jsonl` from the shared tree, paste
  the exit code, the three stdout lines and EVERY stderr line; run it a second time into `/tmp/j13/real2.jsonl` and paste `cmp` of the two
  files; then `git worktree remove /tmp/j13/wt`. For every refusal, say whether the record is genuinely malformed or the grammar is too
  narrow for a legitimate shape — and do NOT widen the grammar (that is a contract change: report it).

## Report (`tasks/briefs/laya/J1-3-report.md`)
DATA: files:lines of every grammar; the reason tokens; the fixture's hand-computed counts; the RED→GREEN pair for each test; the mutant
table; the gate outputs; the real run (exit code, the three lines, all refusals classified); DISCREPANCIES; NOT-done.
`python3 scripts/report_lint.py --min-refs 10 tasks/briefs/laya/J1-3-report.md` (at most three fix rounds, then paste and finish).

## §7 Known limits to state in the report (report them, never fix them here)
- `b1.finding_kind`'s state carries `kind`, which is its own answer (J1-1's schema); `v1.finding_class`'s `disposition` is derived from its
  answer. Both make the J2 question trivial for those types. A J1-1 schema follow-up, not this lane's.
- `b2.hit_role`'s `snippet` is empty unless the scout adds a `note`: the producer's return has no hit-line text.
- `ap.violates_row` rows from the incident log all carry `action_kind=report` and `action_target=docs/INCIDENT-LOG.md`: the hawk's real
  inputs (an edit, a command, a brief paragraph) will not look like them. J2 labels on that basis.
- The measured yield is below KC-J7's 200 for every type (premise block); say so in the report's first line after the real run.

Standing rules: touch ONLY the boundary files; report adjacent defects, never fix them. Never run git add, commit, stash, checkout,
restore, reset or clean in the shared tree (`git worktree add/remove` for the real run only, under `/tmp/j13/`). Other lanes are live in the
tree: S198A on `scripts/transcript_export.py` and `tests/test_transcript_export.py`; B12 on `proofs/S0-02/` and
`tests/test_s0_02_buzz_authz.py`; a verifier writing `tasks/briefs/laya/VERIFY-J1-1-R2-report.md`; possibly T94 on
`harness-ports/bin/pc-lane.sh`, `scripts/pc_lane.sh` and `harness-ports/tests/test_pc_lane*.sh`. Never touch their files. Take no
outward-facing action. Paste every count and timestamp from command output. Long gates in ONE foreground call.

## PREMISE — MEASURED at authoring (2026-09-23 16:1xZ, /home/user/agent-factory, the decisions package worktree == origin c6dcd61)
```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
2026-09-23T16:11Z
c6dcd61
$ ls scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions/sources
  ls: cannot access 'scripts/decide-harvest': No such file or directory
  ls: cannot access 'tests/test_decide_harvest.py': No such file or directory
  ls: cannot access 'tests/fixtures/decisions/sources': No such file or directory
$ for f in src/agent_factory/decisions/{__init__,canonical,volatile,ledger}.py; do echo "$(git rev-parse origin/...:$f | cut -c1-12) $(wc -l < $f) $f"; done
377ccd53da0c 24 src/agent_factory/decisions/__init__.py
607b65b613e2 78 src/agent_factory/decisions/canonical.py
bf04415d72c1 395 src/agent_factory/decisions/volatile.py
71fc398a5340 616 src/agent_factory/decisions/ledger.py
$ grep -n '^def make_row\|^def append\|^def replay\|^_VALID_KINDS' src/agent_factory/decisions/ledger.py; (the _VALID_KINDS set, joined)
46:_VALID_KINDS = frozenset({
335:def make_row(
432:def append(ledger_path, row: dict) -> str:
507:def replay(ledger_path) -> list[dict]:
_VALID_KINDS = frozenset({    "transcript_jsonl",    "lane_report",    "verify_report",    "incident_log",    "registry",})
$ grep -n '^    "[a-z0-9]*\.[a-z_]*": {' src/agent_factory/decisions/volatile.py
211:    "b2.hit_role": {
216:    "b1.finding_sev": {
221:    "b1.finding_kind": {
226:    "d1.bug_echo_scores": {
230:    "v1.finding_class": {
242:    "ap.violates_row": {
254:    "wf.drift": {
$ git ls-files "tasks/briefs/**" | grep -i report | awk -F/ '{print NF}' | sort | uniq -c   (every committed report sits at tasks/briefs/<d>/<file>)
    232 4
$ (the kind table over git ls-files "tasks/briefs/*/*")
verify(VERIFY-*-report.md)=72 verify(report-pc-verify-*)=20 lane(*-report.md)=113 lane(report-pc-*)=27
$ git ls-files "transcripts/" | sed -E "s#/[^/]*$##" | sort | uniq -c; git ls-files "transcripts/**/*.jsonl" | wc -l
    105 transcripts/pc
     16 transcripts/sandbox
0
$ grep -l "hive-scout\|hive-reviewer" transcripts/sandbox/*.md transcripts/pc/*.md | wc -l; (committed digests carrying a bug-echo rating-table header)
1
0
$ python3 /tmp/j13/measure.py   (verify-report finding shapes at HEAD; class-table = a table whose header row starts "| # |" or "| id |" then "| class |")
verify reports=92 | bullet anchors=31 in 2 reports {'FOLLOW-UP': 17, 'INFO': 11, 'BLOCKER': 1, 'KNOWN': 1, 'UNVERIFIED': 1} | class-table rows=88 in 5 reports, class cell in the closed set=47 {'FOLLOW-UP': 22, 'INFO': 21, 'BLOCKER': 1, 'UNVERIFIED': 2, 'CONTRACT-DEFECT': 1}, outside it=41
  class-table header (first 4 cells): ('#', 'class', 'finding (file:line)', 'evidence') x 1
  class-table header (first 4 cells): ('#', 'class', 'comp.', 'finding (file:line)') x 1
  class-table header (first 4 cells): ('id', 'class', 'where', 'what') x 1
  class-table header (first 4 cells): ('id', 'class', 'evidence', 'contract mapping') x 1
  class-table header (first 4 cells): ('#', 'class', 'status on the pin', 'the run') x 1
AF-AP ids in bullet finding titles=0; in class-table rows (whole row)=4
lane reports=140 | boundary-deviation record lines={'lane': 3} | bug-echo rating-table headers in lane+verify reports=0
$ python3 /tmp/j13/measure.py | grep outside   (class cells outside the closed token set: the token plus a qualifier; first six)
  outside: ('report-pc-verify-m3.md--e776dd0.md', 'FOLLOW-UP, SOLID') x 7
  outside: ('VERIFY-AF-AP-127-report.md', 'FOLLOW-UP (adjacent)') x 3
  outside: ('VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md', 'FOLLOW-UP / UNVERIFIED') x 2
  outside: ('VERIFY-REPIN-a-R1-report.md', 'FOLLOW-UP (outside)') x 2
  outside: ('VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md', 'FOLLOW-UP (adjacent)') x 1
  outside: ('VERIFY-AF-AP-127-report.md', 'INFO (adjacent, known)') x 1
$ python3 /tmp/j13/measure2.py   (docs/INCIDENT-LOG.md at HEAD; heading = the bold part of the entry line, to its closing **)
bold entries=117 naming>=1 AF-AP id in the heading=58
dash entries=53 naming>=1 AF-AP id in the heading=22
(entry,id) pairs=102 | headings with no closing ** within 10 lines=0 | entries below the registry heading=0
registry heading line=391 header lines=[401] registry rows=159 | ids named in headings but absent from the registry={}
$ python3 <census of this session's raw transcript JSONL — NOT committed>   (Agent tool_use subagent_type; the tool_result content shape)
Agent dispatches: 210 | hive-scout: 0 | hive-reviewer: 0
tool_result content shapes (blocks, last text block starts "agentId:"): {(2, True): 7, (1, False): 202}
```
The two measurement scripts are the coordinator's (`/tmp/j13/measure.py`, `/tmp/j13/measure2.py`); they approximate the grammars above and
are NOT the contract. Your item 1 re-measures the file identities and the kind-table counts; where your grammar's counts on the real tree
differ from these, say by how much and why in the report (a difference is expected where §4 is stricter, for example the qualifier rule).
