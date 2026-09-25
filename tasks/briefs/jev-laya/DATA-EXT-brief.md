# DATA-EXT: public datasets that could train or test our System 1 Jevs (task #233; owner ask 2026-09-25)

Role: evidence-gatherer (the EXPLORE lane, sandbox, Opus 5.5). Honey full: line-bounded findings, a source for every
claim. Report: `docs/research/findings/laya-ft-data/EXTERNAL-DATASETS-2026-09-25.md` (write it incrementally from the
start). Do NOT spawn subagents. No verdicts: you collect and tabulate; the coordinator ranks and decides.

## WHY

The owner (2026-09-25, voice-typed): "might be worth doing a bit of research. There might be existing datasets, there might
be more relevant [ones], or we can generate datasets from our own chat logs ... if there is better labels in general, that'll
be great." Our first fine-tune of Laya (a small typed-decision model) on 1,788 teacher-labeled examples was rejected on every
check, and the teacher (OpenJev) is itself under a keyword baseline on the dominant question type. A second research lane
audits our OWN records; you cover PUBLIC data.

## OUR THREE QUESTION TYPES (what a dataset must map to)

- `ap.violates_row` (yes/no, asked once per candidate): given an incident or bug note and ONE row of our anti-pattern registry
  (a mechanism in words plus a greppable signature), does the note show that anti-pattern? Scored as a ranking over 16
  candidates. Nearest public relatives: code-smell or anti-pattern detection, bug-cause or root-cause classification,
  static-analysis warning actionability, CWE classification of a vulnerability description.
- `v1.finding_class` (one choice of six): classify a code-review or verification finding as BLOCKER, CONTRACT-DEFECT,
  FOLLOW-UP, INFO, KNOWN or UNVERIFIED. Nearest relatives: code-review comment category and severity, issue or bug severity
  and priority, review comment usefulness.
- `v1.blocking` (yes/no): does the finding block the merge (a contract break reproduced through the real path)? Nearest
  relatives: merge-blocking review comments, "request changes" versus "approve", release-blocker flags, severity cut-offs.

## GOAL

An evidence table of public datasets, broad first and then deep on the most relevant ones. Search at least these families:
code-review comments with category, severity or usefulness labels; issue and bug-report triage (severity, priority, type,
release-blocker); code smells and anti-patterns; static-analysis warning actionability (actionable versus false positive);
vulnerability and CWE classification; CI-failure and flaky-test triage; agent trajectories with step or outcome labels
(SWE-bench-style runs); code-review preference or judge datasets. Prefer human labels; say how each dataset's labels were made.

Columns per dataset: name; URL (the dataset card or paper); license, and whether commercial use is allowed; size (rows)
and download size; the unit (a comment, an issue, a code change, a trajectory step); the label set; how the labels were
made (human, heuristic, mined from later events, model); language(s); format; which of our three types it maps to and
HOW (an exact mapping, a proxy, or input text only, for a teacher to label); known quality problems that the dataset's
own paper or card reports. Mark each field SOLID (read on the dataset's own page, card or paper) or UNSURE.

## CONSTRAINTS

- Read-only research: WebSearch, WebFetch and the Exa tools. Read cards, papers and small samples; no downloads beyond a
  README, a card or a sample of a few rows; no accounts, no sign-ups, no forms, no comments, no stars, nothing that writes
  anywhere outside this repository's report file.
- Cite a URL for every claim. A number you did not read on a primary page is UNSURE.
- Touch ONLY the report file. Report adjacent observations; never act on them.
- The PC bridge is out of scope (no `scripts/pc.sh`).
- FAKE strings only for anything secret-shaped.
- Check the report with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` (0 expected) before you finish.

## EVIDENCE DEMANDS

1. The table (at least 15 candidates across the families, if that many exist).
2. The five closest fits, each with its first 3 rows or a schema excerpt quoted from the card, and the exact mapping onto our
   label set (which of their labels becomes which of ours; what is left without a mapping).
3. What you searched and found nothing for (queries that returned nothing relevant), so absence is visible.
4. NOT-done: anything you could not read (paywalls, gated datasets), named.

## PREMISE (measured at authoring, 2026-09-25 00:4xZ, the sandbox at the local HEAD)

```
$ python3 -c "count question_id in docs/research/findings/laya-ft-labels/2026-09-24-openjev/labels.jsonl"
{'ap.violates_row': 1616, 'v1.blocking': 86, 'v1.finding_class': 86}
$ git ls-files 'tasks/briefs/**/VERIFY-*-report.md' | wc -l; grep -c '^| AF-AP-' docs/INCIDENT-LOG.md
102
201
```
