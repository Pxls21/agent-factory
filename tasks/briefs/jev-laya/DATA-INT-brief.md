# DATA-INT: how good were the training labels, and what can our own records add (task #233; owner ask 2026-09-25)

Role: evidence-gatherer (the EXPLORE lane, sandbox, Opus 5.5). Honey full. Report:
`docs/research/findings/laya-ft-data/INTERNAL-LABELS-2026-09-25.md` (write it incrementally from the start). Do NOT spawn
subagents. No verdicts: you measure and tabulate; the coordinator decides.

## WHY

Laya, fine-tuned on 1,788 rows labeled by the OpenJev teacher, was rejected on every KC-J3 check
(`docs/research/findings/laya-ft-eval/2026-09-25-head-w1-cpu/evaluate-summary.json`). On J2, OpenJev itself sits under the
keyword baseline on the anti-pattern rows (`docs/research/findings/j2b-variants/openjev/ap_noul.json`). Our own records
already hold an answer for most training rows: the verifier's class of every finding, and the anti-pattern rows each
incident entry cites. The owner (2026-09-25): "if there is better labels in general, that'll be great", and "we can generate
datasets from our own chat logs". Two questions: how often did the teacher agree with our own answers, and how much more
labeled data do our records hold.

## GOAL 1: the label audit (the 1,788 training rows)

Rebuild the dataset with its own builder at the manifest's commit (`/root/venv-laya-probe/bin/python
scripts/laya_ft/build_dataset.py --out <your scratch dir> --commit <the manifest's commit>`; the builder is byte-identical
per commit, so check your `dataset.jsonl` against the manifest's sha256 before using it), join it with the labels file by
`key` (`<item_id>|<question_id>`), and recover the ground truth from each row's `sources`:
- `v1.finding_class`: the verifier's own class of the finding at `sources[].path` + `finding_id`, read with the same grammar
  J2's samples used (`docs/research/findings/j2-v1-probe/v1_probe.py` `cmd_sample`, `CLASSES`; `scripts/decide-harvest`).
  Table: OpenJev's choice versus it (accuracy, per-class confusion, class counts).
- `v1.blocking`: the truth is the class in `BLOCKING = {"BLOCKER", "CONTRACT-DEFECT"}` (`v1_probe.py:33`). Table:
  OpenJev's `noul` against it (accuracy at 0.5, the rate of each outcome, and the score distribution per truth value).
- `ap.violates_row`: the truth is whether the incident entry at `sources[].line` of `docs/INCIDENT-LOG.md` (at the
  dataset's commit) cites the candidate `row` (the AF-AP ids the entry names; the builder masked them in the state). Table:
  per entry, where the cited rows rank among its 16 candidates by OpenJev's `noul` (top-1 and top-3 hit rates), the base
  rate of positives, and the same for the lexical order (the candidates' order as ap_probe ranks them).
- For every type: how many rows have a recoverable truth, and why the rest do not.

## GOAL 2: what our own records could add (counts from commands, never estimates)

Per question type, how many NEW examples each source holds, and whether each comes with an answer our process already
reached (an incumbent label) or would need a teacher (Qwen, once QJ2 measures it):
- (a) findings in `tasks/briefs/**/VERIFY-*-report.md` and in PC lane reports `tasks/briefs/pc/report-*.md` that are not in
  the dataset (reports after its commit; formats decide-harvest's grammar does not admit, named with a count each);
- (b) incident entries and registry rows added after the dataset's commit (the registry now runs to AF-AP-201);
- (c) commit messages that carry findings or decisions (`git log` over the branch; a count by pattern, with the patterns);
- (d) the chat logs: the committed digests `transcripts/sandbox/chat-*.md`, and the raw session transcripts under
  `/root/.claude/projects/-home-user*/` (count the decisions of each kind: verifier findings with a class, coordinator
  gate recommendations, owner rulings);
- (e) what `scripts/decide-harvest` extracts today: its row kinds and the counts on the current tree (run it read-only,
  `--out` in your scratch dir).

## CONSTRAINTS

- Read-only on the repository: write only your report and files under your scratch directory (the session scratchpad).
  No commits, no stash, no checkout, no git writes of any kind in `/home/user/agent-factory`.
- No network; the PC bridge is out of scope.
- The transcripts are raw session records. Report COUNTS and structure. Quote nothing from them unless it has passed
  `scripts/transcript_export.py`'s `scrub` first, and never search them for keys, tokens or credentials.
- FAKE strings only for anything secret-shaped.
- Touch ONLY the report file (and your scratch dir). Report adjacent defects; never fix them.
- Check the report with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` (0 expected) before you finish.

## EVIDENCE DEMANDS

1. The rebuild's `dataset.jsonl` sha256 against the manifest (equal, or stop and report).
2. The three audit tables (Goal 1) with the commands that produced them, and the counts pasted.
3. The Goal 2 table: source by question type, with a count, the label origin (incumbent or teacher-needed) and the command.
4. NOT-done: anything you could not measure, and why.

## PREMISE (measured at authoring, 2026-09-25 00:4xZ, the sandbox at the local HEAD)

```
$ python3 -c "selected keys of docs/research/findings/laya-ft-labels/2026-09-24-openjev/dataset-manifest.json"
{'commit': 'eb256f49c0ee87a6ff2d122dcf13d6db6a70bc3f', 'heldout': {'incident_entries': {'excluded': 100, 'identities': 100}, 'samples': {... three samples of 100 rows ...}}, 'text_duplicates_excluded': 0, ...
$ python3 -c "count question_id in docs/research/findings/laya-ft-labels/2026-09-24-openjev/labels.jsonl"
{'ap.violates_row': 1616, 'v1.blocking': 86, 'v1.finding_class': 86}
$ grep -n '"kind": "verify_finding"\|"kind": "incident"' scripts/laya_ft/build_dataset.py
97:  items.append(("v1", qid, state, [{"kind": "verify_finding", "path": path, "finding_id": fid}]))
116: [{"kind": "incident", "line": i + 1, "heading": masked_heading, "row": rid}]))
$ grep -n "^BLOCKING" docs/research/findings/j2-v1-probe/v1_probe.py
33:BLOCKING = {"BLOCKER", "CONTRACT-DEFECT"}
$ ls transcripts/sandbox/ | wc -l; ls /root/.claude/projects/
18
-home-user  -home-user-agent-factory
$ git ls-files 'tasks/briefs/**/VERIFY-*-report.md' | wc -l; git ls-files 'tasks/briefs/pc/report-*.md' | wc -l; grep -c '^| AF-AP-' docs/INCIDENT-LOG.md
102
62
201
$ python3 scripts/decide-harvest --help | head -1
usage: decide-harvest [-h] --out OUT [--root ROOT] [sources ...]
```

A question, not a fact: the dataset directory on the PC is named `ds-0b342c7`, while the manifest names commit eb256f49;
say which commit the rows were built from, and whether both names describe the same bytes.
