# VERIFY-JT1: the independent verify of the Jev client and the hiccup tracker (task #224, rule 0f)

Role: adversarial-verifier (sandbox, Opus 5.5). PIN: 7d73932 (the local HEAD that carries JT1's commit).
Report: `tasks/briefs/jev-laya/VERIFY-JT1-report.md` (write it incrementally from the start).

JT1 was built by a sandbox lane and re-run only by the coordinator, so it is GATED-PENDING-VERIFY. Attack it against its own
contract (`tasks/briefs/jev-laya/JT1-brief.md`: pinned decisions D-1 to D-12, contract A1 to A8) with NEW shapes, never only the
lane's cases; the lane's report is `tasks/briefs/jev-laya/JT1-report.md`. Report every meaningful observation with no severity
filter, then apply the blocking predicate (contract-mapped, reproduced through the real path, materially effective, a concrete
discriminator, in-boundary) and give ONE gate recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID.

## The files

`scripts/jev.py`, `scripts/jev_local.sh`, `scripts/hiccup_scan.py`, `scripts/hiccup_families.tsv`, `tests/test_jev_client.py`,
`tests/test_hiccup_scan.py`, `docs/HICCUPS.md` (a generated page, committed).

## Suspicions to test (not a limit)

- Secrets: can any state, query or chunk reach the endpoint (local or through the bridge) unscrubbed, for example a secret split by
  the cap, a secret inside a nested dict or list state, a key in a dict KEY rather than a value, bytes that are not valid UTF-8?
  Does the PC venue ever put the bridge token or link into argv, the environment of a child, the call log or an error line?
- Fail-open: every failure mode exits 3 with one line and the import API returns None; look for an exception that escapes the
  import API (a malformed JSON body, a 200 with the wrong shape, a `fan_out` that differs, a hung endpoint, a bridge reply with the
  `bind: warning` text in odd places).
- The call log: never the state text (check nested states and the `answers` field: can an answer echo the state?); modes 0700/0600
  when the directory already exists with other modes; concurrent writers.
- `jev_local.sh`: start when the port holds another process; stop when the pidfile names a reused pid; the snapshot check.
- `hiccup_scan.py`: determinism (same inputs, same bytes) across locale or time-zone changes; a transcript line that is huge, not
  JSON, or JSON of the wrong type; the D-11 normalization and scrub against secrets of every class `transcript_export.scrub`
  knows (fake strings only) placed in error text, in agent descriptions and in tool names; the 40,000-byte cap; the `--jev` column
  never changing any other number (KC-J1b).
- Whether any gate file imports or runs these files (`scripts/gate_files.txt`; `python3 scripts/no_laya_in_gates.py`).

## Evidence rules

Reproduce every claim you rely on; paste counts and outputs from commands you ran. Mutants on scratch copies ONLY (never edit,
stash, restore or check out a tracked file in this tree). Record which model served your turns if you can see it. Use a short
`--basetemp` (for example `/tmp/vjt1/bt`; make the parent first); the sandbox venv has no pytest-xdist, so never pass `-n`.
The local Laya server for tools is 127.0.0.1:47411 (use it; never stop it); 127.0.0.1:47412 runs the J2 probe (do not use it).
Never call the bridge yourself: for the PC venue, test with an injected runner, and read the coordinator's live result in the
ledger note of 2026-09-24 13:3xZ.

## Standing rules

Do not spawn subagents. No outward actions (no pushes, PRs, comments, GitHub writes). Do not commit. Other lanes are editing
`src/agent_factory/decisions/volatile.py`, `tests/test_decisions_*.py`, `scripts/jev_context.py`, `scripts/jev_locate.py`,
`scripts/jev_echo.py`, `.claude/hooks/search-intercept.py`, `scripts/install_session_hooks.py`, `.claude/settings.json`,
`tests/test_session_hooks.py`, `scripts/mojev_probe.py` and their tests: never touch or run those. Never print a secret; test
secrets are fake strings. Check every file you write with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`.

## PREMISE — MEASURED at authoring (2026-09-24 13:3xZ, /home/user/agent-factory at 7d73932)

```
$ for f in ...; do git rev-parse --short=12 HEAD:$f; done
e2d02c35ecc8 scripts/jev.py
91ff34e0d914 scripts/jev_local.sh
b1eb74892575 scripts/hiccup_scan.py
e70eb70948f4 scripts/hiccup_families.tsv
9491dbc0f81c tests/test_jev_client.py
e37a5a228cb0 tests/test_hiccup_scan.py
45d4f7ebf6fc docs/HICCUPS.md
$ bash scripts/test_summary.sh tests/test_jev_client.py tests/test_hiccup_scan.py --basetemp /tmp/jt1c/bt
pytest-exit: 0
pytest-summary: 77 passed in 20.46s
$ python3 scripts/jev.py rank --venue pc --query "pytest fails: FileNotFoundError for the --basetemp directory" --chunk ... (three chunks)
{"cmd": "rank", "fan_out": 3, "latency_ms": 1638.7, "ranking": [["c0", 0.46], ["c1", 0.1935], ["c2", 0.191]], "server_latency_ms": 875.2, "venue": "pc"}
```
