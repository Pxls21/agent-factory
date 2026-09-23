# VERIFY-J1-3 — the targeted independent adversarial verify of `scripts/decide-harvest` (task #120)

PIN: e8db82c
ROLE: adversarial-verifier (read-only against production; every mutation on a scratch copy under `../scratch/`)
REPORT: write `tasks/briefs/laya/VERIFY-J1-3-report.md` (untracked is fine) and paste its summary as your final answer.

## What landed, and the contract

J1-3 (commit "J1-3: scripts/decide-harvest + 33 tests …", GATED-PENDING-VERIFY) is the passive decision-ledger harvester:
strict grammars for the incident log, verify/lane-report finding tables and transcript tool returns; sources admitted from
committed HEAD blobs before any row is built; `make_row` then `append` (from `agent_factory.decisions.ledger`) as the only
write path; PIN normalization left to J1-1 (AMENDMENT A1). The frozen contract, read in this order:
`seeds/seed-laya-j1-v1.yaml` (J1-3's acceptance criteria), `tasks/laya-j1-breakdown.md` (the pinned decisions, lines 14-20, and
the J1-3 row, line 32), the build brief `tasks/briefs/pc/pc-j1-3.md` (AMENDMENT A1 included), then the lane's own report
`tasks/briefs/laya/J1-3-report.md`. Attack the CONTRACT, never the builder's own cases alone.

## Items (report EVERY observation; no severity filter; SOLID/UNSURE per observation)

1. PREMISE. Re-measure the block below (blob ids, line counts, the test count, the refusal-name census, the seam lines).
   A mismatch is CONTRACT-INVALID: stop and report it.
2. THE COMMITTED-SOURCE RULE. Show, with a scratch git repository you build (never this tree's history), that a source whose
   worktree bytes differ from HEAD is refused as `harvest-source-uncommitted`, that an untracked path is refused, and that
   no row can carry bytes read after admission (edit the worktree between admission and parsing: a FIFO, a file swapped for a
   symlink, a file rewritten by a background writer). Name the exact line that decides each case.
3. THE GRAMMARS, HOSTILE INPUTS. For each grammar (incident log, verify-report finding table, lane-report finding table,
   transcript JSONL tool return), write at least three inputs that LOOK like records but are prose, a table without the
   declared columns, a duplicated header, a Unicode lookalike pipe or dash, a finding row split across lines, and a JSONL
   line that is valid JSON of the wrong shape. The contract is refusal: every such input yields
   `harvest-source-unparseable: <path>:<line>` or no record, never a row. A row minted from prose is a blocker.
4. IDENTITY AND DUPLICATES. Two runs over the same committed tree produce byte-identical ledgers; a second run over the same
   ledger path prints skips, never duplicate rows (`decision-row-duplicate` counted as a skip); two sources that differ only
   in a PIN suffix normalize to the same lane state with distinct `source_ref`s (the lane's D-1 fixture). Show each on a
   scratch repository.
5. THE REAL RUN ON THIS PIN. Run the harvester twice over this PC clone at the PIN into two fresh files under `../scratch/`;
   paste both harvest lines, the rc, `cmp` of the two files, and three sampled rows with their `source_ref`. Compare with the
   lane's numbers below and explain any difference (the PIN is later than the lane's feb26d7).
6. MUTANTS (scratch copies only). Re-run the lane's mutants (its report section 5) on the PIN's bytes and add at least five of
   your own: admission after parsing; the worktree read used instead of the HEAD blob; a grammar that accepts a missing
   column; `append` without `make_row`; the duplicate refusal turned into a silent skip that prints nothing. Paste each
   diff line, the count and the killing test. A survivor is a finding: name the missing test.
7. GATES (each call under the 420 s cap). `python -m pytest -q tests/test_decide_harvest.py` twice with the count and set id
   (`scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py` prints it locally; here paste the file list); the J1 suites
   `tests/test_decisions_canonical.py tests/test_decisions_ledger.py` once; `python -m pyflakes scripts/decide-harvest
   tests/test_decide_harvest.py`; `python3 scripts/no_laya_in_gates.py` (the never-a-gate screen).
8. REPORT AND GATE RECOMMENDATION. Every finding with file:line, the reproduction command and SOLID/UNSURE. End with
   `GATE RECOMMENDATION: MERGE-READY | MERGE-READY-WITH-FOLLOWUPS | NOT-READY | CONTRACT-INVALID` and the blocking predicate
   applied to each blocker (contract-mapped, reproduced on the real path, material, a concrete discriminator, in-boundary).

Known and out of scope (the lane's own NOT DONE list): zero b1/b2/d1 rows on the real corpus; the PC finding table without
a declared title column is refused (zero PC `v1.finding_class` rows); incident rows model the report action. Confirm each is
as stated; do not re-litigate the design.

## Standing do-nots

- Never edit `scripts/decide-harvest`, `tests/test_decide_harvest.py`, the fixtures or `src/agent_factory/decisions/` in your
  tree; every mutation lives under `../scratch/`. Another lane (J1-1-R3) is editing `src/agent_factory/decisions/`: read it,
  never change it.
- Never read `~/.hermes/`; never touch any `.lanes/` directory other than your own; never kill a process you did not start.
- No outward-facing actions (no PRs, issues, comments, pushes). Do not spawn subagents.
- Bound the report lint: apply its `fix:` hints for at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 21:1xZ, /home/user/agent-factory@e8db82c, the blobs identical to local da79e93)

```
$ git log --oneline -3 HEAD
b6f4b77 lane_gate.sh: make the archive directory absolute before the cd (AF-AP-163; J1-3 D-2)
da79e93 J1-3: scripts/decide-harvest + 33 tests + fixture sources (lane pc-j1-3.md--feb26d7), GATED-PENDING-VERIFY
41154a1 VERIFY-T94-R1 brief (PIN 6963f00) + ledger/wiki: the re-verify dispatched on the cloud verify route
$ for f in (the J1-3 files): git rev-parse --short=12 HEAD:<f>; wc -l
22b63bc47e7c 849 scripts/decide-harvest
2cace4741511 581 tests/test_decide_harvest.py
fd49ef926dbb 18 tests/fixtures/decisions/sources/docs/INCIDENT-LOG.md
00c5b96540ad 2 tests/fixtures/decisions/sources/src/existing.py
84534293a9ff 8 tests/fixtures/decisions/sources/tasks/briefs/x/VERIFY-X-report.md
3ad1434c5717 10 tests/fixtures/decisions/sources/tasks/briefs/x/X-report.md
5b5ddb0ca78d 4 tests/fixtures/decisions/sources/transcripts/x/t.jsonl
$ /root/venv-agent-factory/bin/python -m pytest -q -p no:cacheprovider tests/test_decide_harvest.py | tail -1   (set 87e28761f102)
33 passed in 12.09s
$ grep -o -E 'harvest-[a-z-]+|decision-row-[a-z-]+' scripts/decide-harvest | sort | uniq -c
      1 decision-row-duplicate
      1 harvest-output-source-conflict
      1 harvest-source-uncommitted
      1 harvest-source-unknown
      3 harvest-source-unparseable
$ grep -n -E '^def |make_row|\.append\(|cat-file|ls-tree|show HEAD' scripts/decide-harvest | head -40
19:from agent_factory.decisions.ledger import append, make_row  # noqa: E402
99:def _git(root: Path, *args: str, input_data: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
108:def _repo_root(raw_root: str) -> Path | None:
120:def _kind(path: str) -> str | None:
140:def _tree_paths(root: Path) -> list[str] | None:
141:    result = _git(root, "ls-tree", "-r", "--name-only", "-z", "HEAD")
151:def _head_blob(root: Path, path: str) -> bytes | None:
152:    result = _git(root, "cat-file", "blob", f"HEAD:{path}")
156:def _regular_worktree_bytes(root: Path, path: str) -> bytes | None:
166:def _admit(root: Path, requested: list[str]) -> tuple[list[Source] | None, tuple[int, str] | None]:
199:def _split_table_row(line: str) -> list[str] | None:
222:def _is_separator(cells: list[str] | None) -> bool:
226:def _collapse(text: str) -> str:
230:def _heading_text(lines: list[str], start: int) -> tuple[str | None, str | None]:
251:def _nearest_heading(lines: list[str], before: int) -> str:
259:def _registry(text: str) -> dict[str, str]:
279:def _unique_ap_ids(text: str) -> list[str]:
283:def _ap_candidate(
302:def _parse_incident(source: Source, registry: dict[str, str]) -> list[Candidate]:
331:def _report_lane(path: str) -> str:
343:def _title_column(headers: list[str]) -> int | None:
351:def _parse_class(cell: str) -> str | None:
361:def _report_paths(text: str, root: Path, tree: set[str]) -> list[str]:
372:def _finding_candidates(
483:def _strip_rating(value: str) -> str:
489:def _rating_answer(headers: tuple[str, ...], cells: list[str]) -> str | None:
514:def _parse_lane_report(source: Source) -> list[Candidate]:
582:def _content_blocks(record: dict) -> list[dict]:
587:def _tool_result_payload(block: dict) -> str | None:
599:def _reviewer_rows(payload: object) -> tuple[list[list[object]] | None, str | None]:
618:def _scout_rows(payload: object) -> tuple[list[dict] | None, str | None]:
639:def _parse_transcript(source: Source) -> list[Candidate]:
741:def _candidates(source: Source, *, root: Path, tree: set[str], registry: dict[str, str]) -> list[Candidate]:
751:def _source_ref(source: Source, locator: str) -> dict:
760:def _parse_args(argv: list[str]) -> argparse.Namespace:
768:def main(argv: list[str] | None = None) -> int:
814:                row = make_row(
$ grep -n -E 'import|from ' scripts/decide-harvest | head -12
3:from __future__ import annotations
5:import argparse
6:import hashlib
7:import json
8:import os
9:from pathlib import Path, PurePosixPath
10:import re
11:import subprocess
12:import sys
13:from dataclasses import dataclass
18:from agent_factory.decisions import DecisionStateError  # noqa: E402
19:from agent_factory.decisions.ledger import append, make_row  # noqa: E402
$ grep -c 'decide-harvest' scripts/gate_files.txt
0
$ (the lane's real run, pasted from its report section 7: private clone feb26d7, twice, cmp rc 0, rc 3)
harvest: 207 rows, per question type: ap.violates_row=108, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=97, wf.drift=2
sources: 235 read (incident_log=1, lane_report=141, transcript_jsonl=0, verify_report=93), 224 with no records; refused: 39 records; skipped: 0 duplicates
```
