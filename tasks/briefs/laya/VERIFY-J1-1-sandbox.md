# VERIFY-J1-1 — the sandbox continuation (task #130)

PIN: 52c02ee (the J1-1 boundary; byte-identical at the sandbox HEAD 3d89549, pasted below).
ROLE: adversarial-verifier, sandbox Opus (the fallback venue; the PC lane could not finish).

## Why this lane runs in the sandbox

The PC lane `pc-verify-j1-1.md--52c02ee` (local Qwen, xhigh) ran 8 hours over three attempts:
- attempt 1: 02:45Z-04:32Z, ended on a route refusal;
- attempt 2: 04:39Z-09:57Z, ended on a route refusal;
- attempt 3: from 10:04Z; its last response streamed for 36 minutes (above 30k tokens, more than any other response today).

The lane's draft stopped changing at 05:47Z. The coordinator stopped the lane at 10:50:18Z (one TERM to its own pid). The draft holds items 1-3 in part. It is committed as `tasks/briefs/laya/VERIFY-J1-1-pc-draft-PARTIAL.md` (sha256 `0c47dc115480d9999382ba1d3b4b315bbb4a116d6519d47148bf03e9e0cac536`). Its lines are HYPOTHESES to reproduce, never evidence. Anything you take from it you re-run yourself, and you cite your own run.

## The contract is unchanged

Carry out `tasks/briefs/pc/pc-verify-j1-1.md` in full. That means its COMPONENT + CONTRACT, the coordinator's findings C-F1..C-F7, BUDGET, items 1-10, its Report section and its PREMISE block. The report path stays `tasks/briefs/laya/VERIFY-J1-1-report.md`, and so does its lint line (`--min-refs 15`, no `--map`).

## Venue substitutions (these replace the PC brief's PC-only lines)

- **Interpreter:** `/root/venv-agent-factory/bin/python`. pytest reads `pythonpath = ["src"]` from `pyproject.toml`. A bare `python -c` import needs `PYTHONPATH=src`.
- **Scratch:** every probe, mutant and ledger file goes under `/tmp/vj11s/`, never `$HOME/tmp-vj11/`.
  - pytest runs with `-p no:cacheprovider --basetemp=/tmp/vj11s/bt`.
  - Remove `/tmp/vj11s` at the end.
  - The sandbox has about 1.5 GB of free disk, so keep copies small (`git archive 52c02ee -- src tests pyproject.toml` is enough for mutants).
- **The tree:** the working tree is SHARED with other live lanes. Read-only, except your report. No `git add`, `stash`, `checkout -- …`, `restore`, commit or push.
- **No PC, bridge, network or outward action.** The PC brief's server do-nots stand as written.
- **The golden fixtures carry `root = /home/rocco/agent-factory`.** It is data: the suite passes in the sandbox (pasted below).

## What changed since the PIN (read it; do not assume)

J1-2 (`9d11c25`) and J1-2-R1 (`d4f4698`) have landed. `src/agent_factory/decisions/ledger.py` now exists, and it calls `normalize` then `redact` (VERIFY-AF-AP-127 cited `ledger.py:274` and `:405`; re-measure them).

Two consequences:
1. **Item 1's AC 1 line.** The PC brief expects AC 1 RED on the ledger import "by design". At HEAD that premise no longer holds. Run AC 1 verbatim at HEAD and paste what it prints. It is a question, not an expectation.
2. **Item 8's "materially effective" conjunct.** It can now be MEASURED through the real append path. Write a ledger under `/tmp/vj11s/` through `ledger.py`'s public API with each C-F input, and grep the written bytes for the secret. The ledger is NOT in this lane's boundary: its defects are adjacent observations, never J1-1 blockers.

The planned repair of C-F1 is task #139 (J1-1-R1, "bound after redact"). It is not built. Grade C-F1 as the PC brief asks and name the smallest amendment. Do not assume #139's shape.

## Standing rules (non-negotiable)

- Do NOT spawn subagents. Touch only your report.
- Mutants run in the scratch copy under AF-AP-78: paste the `py_compile` rc and the collected count per row. A syntax kill is INVALID.
- Test secrets are FAKE, invented strings only. Never read, print or paste a real key, token or `*.env` file (AF-AP-39).
- Write the report incrementally from the start, so a lost session still leaves evidence.
- Long gates run in ONE foreground call.
- Counts and timestamps are pasted from command output, never typed.

## PREMISE — MEASURED at authoring (2026-09-23T10:54:12Z, sandbox @ 3d89549)
```
$ date -u; git rev-parse --short HEAD; git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-70
2026-09-23T10:54:12Z
3d89549
3d89549 transcripts: scrubbed sandbox chat digests (2026-09-23)
$ for f in <boundary>; do sha256(PIN) sha256(HEAD) lines; done
2aec3875f71213e4 2aec3875f71213e4   21 src/agent_factory/decisions/__init__.py
bc9cb1d03fdb77a4 bc9cb1d03fdb77a4   77 src/agent_factory/decisions/canonical.py
b48899c883c7231f b48899c883c7231f  295 src/agent_factory/decisions/volatile.py
48fdf09e8038a146 48fdf09e8038a146  340 tests/test_decisions_canonical.py
59fb4a16b20ffb1c 59fb4a16b20ffb1c   19 tests/fixtures/decisions/golden/ap.violates_row.json
fd8d0b3e63e26505 fd8d0b3e63e26505   15 tests/fixtures/decisions/golden/b1.finding_kind.json
19d9938ddf81e0bd 19d9938ddf81e0bd   15 tests/fixtures/decisions/golden/b1.finding_sev.json
f955714a99c6ad99 f955714a99c6ad99   15 tests/fixtures/decisions/golden/b2.hit_role.json
9013f618e3976149 9013f618e3976149   13 tests/fixtures/decisions/golden/d1.bug_echo_scores.json
ef01963a2041265a ef01963a2041265a   25 tests/fixtures/decisions/golden/v1.finding_class.json
e0dc010dc24c50ca e0dc010dc24c50ca   17 tests/fixtures/decisions/golden/wf.drift.json
$ ls src/agent_factory/decisions/  (HEAD)
__init__.py __pycache__ canonical.py ledger.py volatile.py 
$ git log --format="%h %s" 52c02ee..HEAD -- src/agent_factory/decisions/ | cut -c1-90
d4f4698 J1-2-R1 landed (GATED-PENDING-VERIFY): the decision ledger refuses short writes, c
9d11c25 Laya J1-2 landed (GATED-PENDING-VERIFY): the append-only decision ledger with mand
$ python -m pytest -q -p no:cacheprovider --basetemp=/tmp/vj11pre/bt tests/test_decisions_canonical.py | tail -1
14 passed in 0.03s
$ sha256sum tasks/briefs/laya/VERIFY-J1-1-pc-draft-PARTIAL.md
0c47dc115480d9999382ba1d3b4b315bbb4a116d6519d47148bf03e9e0cac536
```
