# PC-J1-1 — J1-1 (canonical.py + volatile.py: normalize → redact → canonical → sha256, the seven closed state schemas, the committed golden digests) on the PC local build lane

PIN: 330803c (origin head; the tree you start from). THE FULL CONTRACT IS `tasks/briefs/laya/J1-1-brief.md` — read it first and build exactly its boundary; this wrapper carries only the PC deltas and the re-measured premise. Its "DISPATCH RULE" line is the coordinator's, already satisfied (VERIFY-J1-0 graded; the J0 sandbox probe is not your concern).
LANE: pc-j1-1
ROLE: code-implementer (build) — the local route (`HERMES_MODEL=qwen-local/qwen3.8-27b-local`). The agentfactory profile's `fallback_providers` chain may re-route your turns to a cloud model after a local error (AF-AP-118) — nothing you can change; say nothing about it in the report, the harvest measures it.
COMPONENT (boundary, exactly the original brief's): NEW `src/agent_factory/decisions/__init__.py`, NEW `src/agent_factory/decisions/canonical.py`, NEW `src/agent_factory/decisions/volatile.py`, NEW `tests/test_decisions_canonical.py`, NEW `tests/fixtures/decisions/golden/` (seven fixture files). NOT `ledger.py` (J1-2), NOT `scripts/decide-harvest` (J1-3), nothing under `scripts/`, no hook. Do NOT commit, do NOT push, no outward action.
BUDGET: one build round; report DATA, not prose; every count and digest pasted from the run.

## PC deltas (these override the original brief's sandbox paths; everything else is the original brief, verbatim)
- Interpreter: `/home/rocco/venv-agent-factory/bin/python` (the sandbox path `/root/venv-agent-factory` does not exist here).
- Gates: `mkdir -p /home/rocco/tmp-j11 && /home/rocco/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/home/rocco/tmp-j11/bt` TWICE, `rm -rf /home/rocco/tmp-j11/bt` between the runs, counts bitwise; NEVER a basetemp under `/tmp` on the PC (AF-AP-112). Every gate call stays under the 420 s terminal cap (this suite is seconds).
- `/home/rocco/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/*.py tests/test_decisions_canonical.py` (0 hits), `python3 scripts/ap_screen.py --tests src/agent_factory/decisions/canonical.py src/agent_factory/decisions/volatile.py tests/test_decisions_canonical.py` (the FLAG form, every hit graded), `python3 scripts/no_laya_in_gates.py` (rc 0; the never-a-gate screen must stay clean — your files are not gate files and must not be listed).
- The seed's AC 1 and AC 3 `verify_command`s from `seeds/seed-laya-j1-v1.yaml`, run verbatim with the interpreter above: AC 1 imports `agent_factory.decisions.ledger`, which is J1-2's — report it RED-until-J1-2 honestly; never create `ledger.py`, never stub it.
- `scripts/pc_suite.sh` does not work for a PC-resident lane — never call it; `scripts/lane_context.sh` and the code-intel CLIs work in the lane tree (the dispatcher builds the graft index at launch).
- Mutants: the six rows of the original brief (m1-m6), each on a SCRATCH COPY of the file (`cp` to a scratch dir under `/home/rocco/tmp-j11/`, edit, run, restore; sha-verify the restore), the failing test NAMED per row; a mutant must compile and collect (AF-AP-78).
- Report: `tasks/briefs/laya/J1-1-report.md` — files:lines, the RED→GREEN pairs, the six mutant rows, both gate runs, the seven golden digests pasted, DISCREPANCIES / NOT-done (AC 1's ledger import); `python3 scripts/report_lint.py --min-refs 10 tasks/briefs/laya/J1-1-report.md --root .` (≤ 3 fix rounds, then paste and finish).

## PREMISE — MEASURED at authoring (2026-09-22T20:47:50Z, sandbox @ 330803c; the PC clone is ff-synced to the same SHA before dispatch)
```
$ git rev-parse --short HEAD; git log --oneline -1 origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-60
330803c
330803c VERIFY-K1-g home: MERGE-READY-WITH-FOLLOWUPS, the K1
$ git diff --stat HEAD origin/claude/soundbox-kit-migration-iz1jwf | wc -l   (0 = the same tree)
0
$ ls src/agent_factory/ && ls src/agent_factory/decisions 2>&1 | head -2
__init__.py
__pycache__
audit
governance
ls: cannot access 'src/agent_factory/decisions': No such file or directory
$ grep -n 'pythonpath' pyproject.toml
15:pythonpath = ["src"]
$ ls tests/fixtures/decisions/
gate_violation
probe
$ ls tests/ | grep -c decisions   (0 = no J1 test yet)
0
$ python3 scripts/no_laya_in_gates.py; echo rc=$?
no_laya_in_gates: 33 files scanned, clean
rc=0
$ grep -c 'decision-state-unknown-key\|decision-row-incomplete' tasks/laya-j1-breakdown.md
4
$ grep -n 'ac_bdaf2f13a1cee8c9\|ac_348ab0ae10309609' seeds/seed-laya-j1-v1.yaml | head -2
102:  semantic_ac_key: ac_bdaf2f13a1cee8c9
120:  semantic_ac_key: ac_348ab0ae10309609
$ PYTHONPATH=src python3 -c 'import agent_factory, sys; print(agent_factory.__file__)'
/home/user/agent-factory/src/agent_factory/__init__.py
```
