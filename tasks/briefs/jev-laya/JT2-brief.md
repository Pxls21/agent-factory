# JT2: the Jev bug locator and Jev-assisted bug-echo (tasks #227, #229; D-072 item 4)

Role: code-implementer (sandbox, Opus 5.5). PIN: the local HEAD named in the dispatch message.
Report: `tasks/briefs/jev-laya/JT2-report.md` (write it incrementally from the start).

## Why

The owner (D-072): most of the work after a bug is gathering the right context, and most of those steps are System-1
decisions. Every code-intel instrument already runs from one script (`scripts/lane_context.sh`), but it cuts each output at
a fixed line count and never ranks anything (evidence E3 row P3 in `docs/research/findings/JEV-LEVERAGE-EVIDENCE-2026-09-24.md`).
This lane builds the tool the owner described: give it a bug, it runs all the instruments, Jev ranks what they found, and it
hands back the files, lines and records to read, under a budget. The same machinery makes bug-echo cheap: Jev scores the
candidate sites so the model reads the top ten, not every match. Read `docs/research/findings/JEV-LEVERAGE-AUDIT-2026-09-24.md`
section 3 first: Jev finds; the model and deterministic code decide.

## Boundary

- CREATE: `scripts/jev_context.py` (the shared library), `scripts/jev_locate.py`, `scripts/jev_echo.py`,
  `tests/test_jev_context.py`, `tests/test_jev_locate_echo.py`, `docs/research/findings/jev-locate-bench/` (the benchmark
  script, its committed case list and its results), the report.
- MODIFY: nothing. READ: everything else. `scripts/jev.py` belongs to the JT1 lane (still open): import it, never edit it.

## Pinned decisions (a conflict with the tree is a STOP-and-report)

- **D-1 Instruments, each optional and fail-open** (an absent or failing one prints `unmapped — <tool> unavailable`, never a
  silent blank; per-instrument timeout 30 s): `graft ask "<question>" [--in <path>]`; GitNexus `node .gitnexus/run.cjs query
  "<question>" --repo .` (and `context <symbol>` for identifiers found in the question); codebase-memory
  (`/root/.local/bin/codebase-memory-mcp cli ...`, the exact invocation from `.claude/skills/code-intel-trio/SKILL.md`);
  code-review-graph (`/root/venv-crg/bin/code-review-graph query callers_of <symbol>`); `rg` for the question's distinctive
  tokens (identifiers, quoted strings, error class names, `file.py:NN` references) over `proofs/ spikes/ scripts/ src/
  harness-ports/ tests/`; the registry rows of `docs/INCIDENT-LOG.md` and the CLAUDE.md quirk lines (the `bit 2026-` markers),
  lexical top 8 each; `git log -S<token> --oneline -5` for the two most distinctive tokens. Read the exact CLI shapes from
  `scripts/lane_context.sh` and the skill; never guess a flag.
- **D-2 Chunks.** Every hit becomes `{id, instrument, path, line, text}` with `text` at most 400 characters; hits on the same
  path within 5 lines merge and keep every instrument that found them (agreement between instruments is evidence).
- **D-3 Ranking through `scripts/jev.py` only** (`from jev import rank`; the server's per-chunk contract: one `noul` per chunk).
  At most 48 chunks go to Jev per call (lexical pre-filter by token overlap with the question first). Jev unavailable: the pack
  is still produced, ordered by instrument agreement then lexical score, with the line `Jev unavailable: <reason> (unranked)`.
- **D-4 The pack** (markdown, or JSON with `--json`): the question; the top K items (default 12: score, instruments, `path:line`,
  snippet); "files to read" aggregated by file (summed scores, best line); the unmapped instruments; the whole under `--budget`
  characters (default 6,000; hard cap 9,000, AF-AP-183). Deterministic for a fixed input and fixed instrument outputs (sorted
  ties).
- **D-5 `jev_locate.py "<bug text>" [--from-file PATH] [--in PATH] [--top K] [--budget N] [--json]`**: the bug text can be an
  error trace, a failing test's output or a sentence; `--from-file` reads it (the last 4,000 characters when larger).
- **D-6 `jev_echo.py --diff <commit | patch file> [--top K]`**: the removed lines are the anti-pattern, the added lines the fix,
  the diff's file and hunk the fixed site. Candidates: `rg` for the removed lines' distinctive tokens and shape across the code
  dirs (the fixed site excluded) plus `graft ask "code like: <removed snippet>"`; each candidate carries 3 lines of context;
  Jev scores each against "the defect: <removed>; fixed as: <added>" ("Does this code show the same defect as the one fixed?").
  Output: the top K sites with scores and a note that the BUG/WATCH/OK call stays with the model (KC-J1b's spirit).
- **D-7 Standard library only**, plus the instruments' CLIs. No network except the local Jev endpoint through `jev.py`.

## Contract

- **A1** `jev_locate.py` live on three real questions (for example an error line from `docs/INCIDENT-LOG.md`, a failing-test
  shape, a "where is X decided" question): paste each pack's top 5, the instruments that answered and the wall time.
- **A2** Fail-open: every instrument absent (PATH stripped) still yields a pack of `unmapped` lines and exit 0; Jev down yields the
  unranked pack with its reason line.
- **A3** The retrospective benchmark (the one real measure of value): 20 past fixes from `git log` whose commit names an AF-AP
  row and touches one or two production files; the input is the registry row's first cell or the incident heading with the fix
  commit's own words removed; the target is the fixed files. Report recall at 5 of the "files to read" list, Jev-ranked against
  unranked, with the case list committed before the run (digest in the report). Caveat to state: the tree is HEAD, where the fix
  is already in.
- **A4** `jev_echo.py` on two real fix commits from today's history (for example the AF-AP-181 race fix de06db6 and the
  AF-AP-184 guard in 40543ab's parent chain): paste the top sites and say which are true echoes (your reading).
- **A5** Budget and size: a pack never exceeds 9,000 characters (a test with oversized instrument output).
- **A6** Mutants on scratch copies: (1) drop the ranking (the benchmark's ranked column equals unranked); (2) drop the merge
  of same-site hits; (3) exceed the budget. Each turns a named test red; paste the kill table.
- **Gates:** `python -m pytest tests/test_jev_context.py tests/test_jev_locate_echo.py -q --basetemp /tmp/jt2/bt` twice (make the
  parent first); `python3 scripts/lint_delta.py --base HEAD` with no new hit; `python3 scripts/no_laya_in_gates.py` rc 0.

## Standing rules

Do not spawn subagents. No outward actions (no push, PR, comment, bridge call). Do not commit. Touch only the boundary; report
adjacent defects. Other agents edit `src/agent_factory/decisions/volatile.py`, `tests/test_decisions_*.py` (J1-1-R4), the JT1
files (`scripts/jev.py`, `scripts/jev_local.sh`, `scripts/hiccup_scan.py`, `tests/test_jev_client.py`,
`tests/test_hiccup_scan.py`, `docs/HICCUPS.md`) and the JT3 files (`.claude/hooks/search-intercept.py`, `scripts/install_session_hooks.py`
and their tests): never touch those. Two local Laya servers run (127.0.0.1:47411 for tools, 47412 for the J2 probe): use 47411
through `jev.py`; never stop either. Never print a secret. No `-n` for pytest. Kill by pid only. Check every written file with
`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` (a typed backslash-u escape can become literal bytes).

## PREMISE — MEASURED at authoring (2026-09-24 13:0xZ, /home/user/agent-factory at eb52e9b)

```
$ grep -n -E '^def (health|ask|rank|classify)\b' scripts/jev.py
446:def health(**opts):
450:def ask(state, instructions, qtype="noul", criteria=None, **opts):
454:def rank(query, chunks, instructions=RANK_INSTRUCTIONS, **opts):
458:def classify(state, labels, instructions=CLASSIFY_INSTRUCTIONS, **opts):
$ timeout 60 graft ask "who calls merged in install_session_hooks" --in scripts     (2,656 ms, 201 bytes)
graft ask — "who calls merged in install_session_hooks"  (structural)
callers / references of merged
- main  scripts/install_session_hooks.py:L83-L126  (calls) — def main(argv: list[str]) -> int
$ grep -n -E 'graft|run.cjs|code-review-graph|ripwire' scripts/lane_context.sh | head -4
61:    if have graft; then run "graft skeleton" graft skeleton "$f" | grep -v '^\[graft\] tokens saved' | head -80; ...
68:    if have graft; then run "graft ask" graft ask "$Q" --in "$(dirname "${FILES[0]}")" | grep -v ... | head -60; ...
75:    if [ -f .gitnexus/run.cjs ]; then run "gitnexus impact" node .gitnexus/run.cjs impact "$s" --direction upstream --repo . | ...
81:      run "crg callers_of" "$CRG" query callers_of "${q:-$s}" | grep -E '"summary"|"name"' | head -12
$ measured 12:17Z on the local server (tasks/briefs/jev-laya/JT1-brief.md premise): 8 notes ranked per chunk in 3.4 s; the right
  quirk note first (0.5643) for a pytest --basetemp error; chunks must be a LIST of {id, text} or the server does not fan out.
```
