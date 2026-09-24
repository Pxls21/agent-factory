# MOJEV-G0-S: build the MoJev Gate 0 probe in the sandbox; the coordinator runs it on the PC (task #230; D-072 item 3)

Role: code-implementer (sandbox, Opus 5.5). PIN: the local HEAD named in the dispatch message.
Report: `tasks/briefs/jev-laya/MOJEV-G0-S-report.md` (write it incrementally from the start).

## What changed

`tasks/briefs/pc/pc-mojev-g0.md` was written for a PC Hermes lane. The owner moved all Jev work to sandbox Opus 5.5 lanes
(D-072); the PC's local lane stays on the main project. The weights and MoJev's pinned code live only on the PC
(`~/mojev-pin` at a74d58cd19ec, `~/mojev-snapshot/0c8695b6252f/`; the sandbox disk has under 1 GB free, the model file is
1,710,234,304 bytes). So this lane BUILDS the probe and its tests here, and the coordinator runs the matrix on the PC over the
bridge and files the findings.

## Your contract

Read `tasks/briefs/pc/pc-mojev-g0.md` in full. Build exactly its `scripts/mojev_probe.py` and `tests/test_mojev_probe.py`, to its
PINNED DECISIONS D-1 to D-4, its CONTRACT G0-1 to G0-6 (the code that produces each JSON block) and its TESTS section. Changes to
that brief, and only these:

- The tests run in the sandbox with `/root/venv-agent-factory/bin/python` (no MoJev package, no weights, no torch needed): every
  MoJev and torch import stays lazy, inside the functions that load or score.
- You never load the model and never touch the PC or the bridge. Where the PC brief asks for a live number (latency, memory,
  probabilities), your job is the code path that measures it plus a test that drives that path with a test double for the
  scorer; the double is never the source of any number in the findings (the coordinator's PC run is).
- Add a `--dry-run` flag that runs the whole matrix plan with no model (it prints the cells, the token cuts and the candidate
  sets it would run, and exits 0), so the coordinator can check the plan on the PC before a long run.
- The probe must run on the PC as `~/venv-mojev/bin/python scripts/mojev_probe.py ...` from the PC clone at the pushed PIN, with
  `--pin ~/mojev-pin --snapshot ~/mojev-snapshot/0c8695b6252f` (paths as arguments, never hard-coded), at most 6 threads, nice 10,
  offline (`HF_HUB_OFFLINE=1`), stopping a cell above 32 GB resident.
- Boundary: CREATE `scripts/mojev_probe.py`, `tests/test_mojev_probe.py` and the report. Nothing else.

## Gates

`python -m pytest tests/test_mojev_probe.py -q --basetemp /tmp/mj/bt` twice (make the parent first), counts pasted;
`python3 scripts/mojev_probe.py --dry-run ...` output pasted; `python3 scripts/lint_delta.py --base HEAD` with no new hit;
`python3 scripts/no_laya_in_gates.py` rc 0 (the screen's vocabulary includes `mojev` and `packedscorer`: your files are not
gate files, and no gate file may import them).

## Standing rules

Do not spawn subagents. No outward actions (no push, PR, comment, bridge call). Do not commit. Touch only the boundary; report
adjacent defects. Other agents edit the J1-1-R4 files (`src/agent_factory/decisions/volatile.py`, `tests/test_decisions_*.py`),
the JT1 files (`scripts/jev.py`, `scripts/jev_local.sh`, `scripts/hiccup_scan.py`, their tests), the JT2 files
(`scripts/jev_context.py`, `scripts/jev_locate.py`, `scripts/jev_echo.py`, their tests) and the JT3 files
(`.claude/hooks/search-intercept.py`, `scripts/install_session_hooks.py`, `.claude/settings.json`, `tests/test_session_hooks.py`):
never touch those. Never print a secret. No `-n` for pytest. Kill by pid only. Check every written file with
`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`.

## PREMISE — MEASURED at authoring (2026-09-24 13:0xZ, /home/user/agent-factory at eb52e9b)

```
$ grep -n -E '^## ' tasks/briefs/pc/pc-mojev-g0.md
20:## WHY (read first)
32:## BOUNDARY
43:## PINNED DECISIONS
60:## CONTRACT (each item is a JSON block and a report section)
82:## TESTS (`tests/test_mojev_probe.py`; no model load, run with `/home/rocco/venv-agent-factory/bin/python`)
92:## GATES
98:## REPORT (`tasks/briefs/jev-laya/MOJEV-G0-report.md`)
105:## PREMISE — MEASURED at authoring (2026-09-24 11:4xZ; the sandbox tree at 200ed95 over origin 8c684be, and the PC over the bridge)
$ git ls-files scripts/mojev_probe.py tests/test_mojev_probe.py | wc -l
0
$ df -h / | tail -1
/dev/vda        252G   37G  957M  98% /
```
