# VERIFY-FT1: the independent verify of the Laya fine-tune tooling (task #233; rule 0f)

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: the content of the files hashed below (commit "laya_ft: FT1 lands").
Report: `tasks/briefs/jev-laya/VERIFY-FT1-report.md` (write it incrementally from the start).

FT1 was built by a sandbox lane and re-run only by the coordinator, so it is GATED-PENDING-VERIFY. Its tools will produce the training
data and the checkpoints the owner's GPU window trains (D-075, D-078, D-079), so a wrong green here trains a model on wrong data.
Attack it against its own contract (`tasks/briefs/jev-laya/FT1-brief.md`: pinned decisions D-1 to D-8 and the evidence demands) with
NEW shapes, never only the lane's cases; the lane's report is `tasks/briefs/jev-laya/FT1-report.md`. Report every meaningful
observation with no severity filter, then apply the blocking predicate (contract-mapped, reproduced through the real path,
materially effective, a concrete discriminator, in-boundary) and give ONE gate recommendation: MERGE-READY /
MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID.

## The files

`scripts/laya_ft/__init__.py`, `scripts/laya_ft/common.py`, `scripts/laya_ft/build_dataset.py`, `scripts/laya_ft/teacher_label.py`,
`scripts/laya_ft/train.py`, `scripts/laya_ft/evaluate.py`, `tests/test_laya_ft.py`.

## Suspicions to test (not a limit)

- D-3, held-out rows: can any row of the three committed samples reach the dataset under another identity (a finding re-worded,
  re-classed or moved to another report; an incident heading edited; a table row versus a bullet)? Is the count check a real
  check or equal by construction? Does the second guard (text equality) compare the same normalized text the sample holds?
- AF-AP-193 (a cut taken before a length-changing transform): the builder cuts states to Laya's window; the teacher client scrubs
  every string before it leaves. Does the teacher label the SAME text the student trains and is evaluated on? Where does each
  cut and each scrub happen, in what order, and what does a scrub that lengthens text do to a state already cut to the window?
- AF-AP-189: can the v1 ledger's `disposition` field, or any field derived from the label, reach an input? Do the masks leave a
  class word, a class-like word (for example "blocks", "non-blocking") or an `AF-AP` id in any stored state?
- D-5, the teacher client: the key never in argv, a log, an error line, a stored label or the manifest (a FAKE key file; the lane
  once passed the real key to `grep`'s argv through a command substitution: say whether the TOOL itself ever does); resume keyed by
  (item id, question id) across a changed dataset; the 60-per-minute limit under retries; a 200 whose answer shape is wrong; the
  stored distribution's option order against the dataset's option order.
- D-1 and D-7, the trainer: the loss is the negated `laya.common.proper_reward` over the right mask; head mode leaves the encoder
  bitwise unchanged; the act head never moves; the free-space check (a checkpoint larger than the free space is refused before any
  byte is written); determinism with the fixed seed; a checkpoint from one mode loaded into the other.
- D-8, the evaluator: is the no-checkpoint positive control a real oracle (recomputed predictions compared with the committed
  per-row predictions) or a reading of committed numbers? Does the KC-J3 line compare against the right baselines?
- AF-AP-192: the lane's mutation audit ran stale bytecode once (M11). Re-run at least three of its mutants yourself with
  `PYTHONDONTWRITEBYTECODE=1` and a fresh copy per mutant; add your own.
- Whether any gate file imports or runs these files (`scripts/gate_files.txt`; `python3 scripts/no_laya_in_gates.py`).

## Evidence rules

Reproduce every claim you rely on; paste counts and outputs from commands you ran. Mutants on scratch copies ONLY (never edit,
stash, restore or check out a tracked file in this tree). The Laya venv is `/root/venv-laya-probe` (CPU torch) and the snapshot is
under `/root/hf-laya-probe`; the local Laya server for tools is 127.0.0.1:47411 (never stop it). Use a short `--basetemp` (for
example `/tmp/vft1/bt`; make the parent first); never pass `-n`. DISK: a full-encoder checkpoint is about 1.6 GB and the lane filled
the disk once; read `df -h /` before any run that saves a checkpoint, keep at most one checkpoint on disk, and delete it once its
hash is recorded. Record which model served your turns if you can see it.

## Standing rules

No outward actions (no commits, pushes, PRs, comments, GitHub writes, bridge calls). NO third-party API: never call codiv.ai; test
the teacher client against a local stand-in server only. Do not spawn subagents. Other lanes: JT3-R1 edits
`.claude/hooks/search-intercept.py`, `tests/test_search_intercept.py`, `tests/test_session_hooks.py`; JT2-R1 edits
`scripts/jev_context.py`, `scripts/jev_locate.py`, `scripts/jev_echo.py`, `tests/test_jev_context.py`, `tests/test_jev_locate_echo.py`:
never touch those. Never create or remove `.jev/intercept-off`. Test secrets are FAKE strings (QZJ8... and X4Z9... style). Kill by pid
only. Check every file you write with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`.

## PREMISE — MEASURED at authoring (2026-09-24 17:1xZ, /home/user/agent-factory at local HEAD)

```
$ for f in scripts/laya_ft/__init__.py scripts/laya_ft/common.py scripts/laya_ft/build_dataset.py scripts/laya_ft/teacher_label.py scripts/laya_ft/train.py scripts/laya_ft/evaluate.py tests/test_laya_ft.py; do echo "$(git rev-parse --short=12 HEAD:$f) $f"; done
9266ba11b501 scripts/laya_ft/__init__.py
63f15afdb090 scripts/laya_ft/common.py
9ecf61065267 scripts/laya_ft/build_dataset.py
0af5dea65676 scripts/laya_ft/teacher_label.py
8d03bef2a83b scripts/laya_ft/train.py
96b0a2024012 scripts/laya_ft/evaluate.py
20409b3606f5 tests/test_laya_ft.py
$ bash scripts/pc_suite.sh set-id -- tests/test_laya_ft.py
1 files set=8b147318aa48
$ bash scripts/test_summary.sh tests/test_laya_ft.py --basetemp=/tmp/ft1c/bt   (coordinator, 17:0xZ)
pytest-exit: 0
pytest-summary: 22 passed in 124.36s (0:02:04)
$ env -u S0_01_VENUE /root/venv-agent-factory/bin/python -m pytest tests/test_laya_ft.py -q -rs --basetemp=/tmp/ft1d/bt -p no:cacheprovider
18 passed, 4 skipped in 4.44s
```
