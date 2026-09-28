# VERIFY-LS-B9 report: the stack runner, its nine stacks and the round-2 items (task #339, D-103, D-104)

Written 2026-09-28 from 19:5xZ by the sandbox adversarial-verifier lane (Opus 5.5). Brief:
`tasks/briefs/labeling/VERIFY-LS-B9-brief.md`. Written incrementally; the verdict is at the end.

## Premise re-run (`bash scripts/premise_block.sh`, the main tree, 19:49Z)

Every line matches the brief's block: HEAD `ca29894`, the same status (one ` M`, seven `??`), the same seven sha256
prefixes and line counts, the same five instruments (no code-review-graph on the PATH), the same two `baseline.json`
files and mtimes, the same nine-stack catalog, `pytest-summary: 147 passed`. Only `df` moved: 12157 MB free against
12158. No CONTRACT-INVALID stop. (Run with `PYTHONDONTWRITEBYTECODE=1` so the pytest line wrote no bytecode into the
main tree; the commands are the block's own.)

## Scratch and what each instrument writes (measured before any main-tree run)

Scratch: `/tmp/vlsb9/repo` = `git archive HEAD` (ca29894) made a git repository of its own (one commit, `4cd3a27`),
with the seven lane files copied on top, untracked as in the main tree (sha256 prefixes identical to the premise).
281 MB with its `.git`.

What each step program writes, and where (measured by a marker-file scan around a run, or read from the source):
- `stack.py`: `<log dir>/runs.jsonl`, `<log dir>/.lock`, `<log dir>/<run id>/<step>.out`; `{tmp}` =
  `/tmp/stack-<run id>` only when a selected step names it (the gate's `run` step, `mode=run` only).
- ripwire (through `scripts/ripwire_review.sh`): one cache file per root, `/tmp/ripwire-0/<2 hex>/ripwire-<hash>-lean.bin`
  (measured: a run in the scratch copy created `/tmp/ripwire-0/20/`). Nothing inside the tree. The premise's own pytest
  line over the real tree left `/tmp/ripwire-0/66/` at 19:50 (the sandbox-only ripwire test runs on ROOT).
- sentrux (through `scripts/sentrux_review.sh`): `${SENTRUX_RUNTIME_DIR:-<script root>/.sentrux-runtime}`: `rm -rf` and a
  fresh copy of `tree/` on EVERY mode, `last-<mode>.txt`, and on `save` the shared `baseline.json` (wrapper lines 28-38).
- `pc_suite.sh set-id`: a transient self-copy `/tmp/pc_suite.sh.XXXXXX`, removed by its EXIT trap; it never calls
  `bridge()`, so no bridge env is read.
- `gate_files.py`, `gate_union.py`, `report_lint.py`, `ap_screen.py`, `owner_rulings.py`, git read commands: no file
  write, except Python bytecode when `gate_union.py` imports `gate_files` (`scripts/__pycache__/`, gitignored).
  Every main-tree run below carries `PYTHONDONTWRITEBYTECODE=1` so it writes none.
- `hiccup_scan.py` and `handback_extract.py`: only their `--out` / `--report-out` files (inside the run dir).
- graft, code-review-graph, GitNexus: `graft/`, `.code-review-graph/` inside the tree (builder's D16). I never ran
  `ctx`, `impact` or `find` against the main tree.

Main-tree runs in this lane: `list`, `explain`, `premise` and `gate mode=plan`, each with `--log-dir` under
`/tmp/vlsb9/` and `PYTHONDONTWRITEBYTECODE=1`. Everything else ran with `--tree /tmp/vlsb9/repo`.

## Control

`bash scripts/test_summary.sh --basetemp=/tmp/vlsb9/bt/c1 tests/test_stack.py` in the scratch copy:
`1 files set=2ac01abb1067` · `pytest-summary: 147 passed in 41.42s` (the builder's set id and count).

## Area 1: the runner's argv discipline (contract items 3-5) — HOLDS

Probe `/tmp/vlsb9/probe/argv_probe.py`: a temporary git tree and a registry of ten one-parameter stacks (path, paths,
text, word, words, symbol, symbols, int, agent, choice), each with a `marker` step and a step that prints its argv as
JSON. 56 hostile values per type: `;`, `a;b`, `$(touch X)`, backticks, a space, `-x`, `--x`, a comma in a path,
U+2028, U+2029, full-width digits, U+017F, `\n`, `\r`, ESC, VT, NEL, a symlink out of the tree, `..` forms, a symlink to
`.pc-bridge.env`, `.git/config`, `./.git/config`, `sub/../.git/config`, `.git`, a symlink to `.git/config`, `x/.git`,
`.GIT/config`, a symlink loop, a hardlink, `/proc/self/cwd/a.txt`, `.env`, `X.ENV`, the empty value, the length edges
(500/501, 64/65, 128/129), `+1`, `1e3`, Arabic-Indic and full-width digits for `int`, `YES`, `yes `.

- 560 runs: 382 refused with exit 2, every one before any step (no MARKER) and with no log dir; 178 accepted; no other
  exit code. No shell side effect (`X`, `Y` never created).
- Every accepted scalar reached the program as one literal argv element, equal to the value. List types split on
  commas only. Each deny and containment refusal names its rule (`.pc-bridge.env`, `.git/`, `*.env`, "is outside the
  tree", "resolves outside the tree (to /etc/hostname)").
- A NUL cannot be tested on the command line (the OS refuses it in argv); it can only arrive through a chained line,
  which the builder's `line-nul` case covers.
- `{transcript}`: the agent type is `^a[0-9a-f]{16}$`, so a crafted id carries no path character or glob metachar;
  zero or two matches exit 2 from `build_plan`, before the log dir is made (code order at `cmd_run`, lines 1167-1182).

Observations (not contract violations; see the inventory): `path` and `text` accept ESC, VT, NEL, U+2028 and U+2029, and
these reach the one-line print raw (F-9); a hardlink, `.pc-bridge.env.bak` and `.GIT/config` pass the deny list (F-10).

## Area 2: gate completeness (the headline risk) — ONE BLOCKER

### F-1 BLOCKER: the gate runs a script-style `harness-ports/tests/test_*.py` through pytest, which collects nothing; the print reads green

`gate_files.py` lists every file under `harness-ports/tests/` that names the path, and `gate_union.py` keeps in the run
list every one whose name matches `test_*.py`. But those `.py` files are scripts: `harness-ports/tests/run-all.sh`
(lines 12-14 and 46-47) runs each with `python3`, and five of them define no pytest test and keep their checks under
`if __name__ == "__main__":` (`test_codex_hook_adapter.py`, `test_hermes_hook_adapter.py`,
`test_hermes_session_export.py`, `test_hermes_spool.py`, `test_pc_bridge_exec.py`). pytest imports such a file and
collects nothing from it, so its checks never run, and neither the run step nor `sources` says so.

Reproduction (scratch copy, the real registry and scripts, the default `graph=yes`):
1. Control: `python3 harness-ports/tests/test_pc_bridge_exec.py` → `test_pc_bridge_exec: 8 checks passed`, rc 0.
2. One-line break of the change under gate: in `scripts/pc_bridge_exec.py`, the non-JSON reply
   `return {"rc": 3, ...}` becomes `return {"rc": 0, ...}` (a failed bridge call now reads as success).
3. The project's own run of the test (`run-all.sh`'s form): `python3 harness-ports/tests/test_pc_bridge_exec.py` →
   rc 1, `AssertionError: (0, '')`.
4. The production gate over the same tree:
   `python3 scripts/stack.py --tree /tmp/vlsb9/repo --log-dir /tmp/vlsb9/logs/hg gate paths=scripts/pc_bridge_exec.py mode=run runs=1`
   → `stack gate · run s-20260928T200926Z-abd5d5 · exit 0`; the run list is `test_bridge_token_handling.py`,
   `test_pc_bridge_exec.py`, `tests/test_jev_context.py` (`3 files set=1c4a5efeca8e`); `sources` marks each
   `gate_files` with no "not run"; `## run · ok · rc 0` · `pytest-summary: 49 passed in 8.60s`.
5. Where the 49 come from (`pytest --collect-only -q`): `tests/test_jev_context.py: 49 tests collected`;
   `harness-ports/tests/test_pc_bridge_exec.py: no tests collected`; `test_bridge_token_handling.py: no tests
   collected` (its asserts run at import). `grep -c "not run"` over the whole print: 0.
   `tests/test_jev_context.py` names the helper only inside graft-output fixture text (its lines 129, 213, 217).

So the gate printed a green count while the one test that exercises the changed file, and fails against the change,
never ran. The print gives no sign of it. The brief names exactly this as the headline risk.

Reach measured with the literal rule over every tracked non-vendored path: `scripts/pc_bridge_exec.py`,
`harness-ports/tests/test_hermes_spool.py` (a change to the test itself) and `wiki/topics/live-state.md` can gate
green over a never-run script. `harness-ports/bin/codex-hook-adapter.py`, `harness-ports/tests/test_codex_hook_adapter.py`
and `harness-ports/tests/test_hermes_hook_adapter.py` gate red instead (their run list holds only the script, pytest
exit 5 "no tests ran"), which is fail-closed but still never runs the test. The same holds for any future
`harness-ports/tests/test_*.py` script. CI runs `bash harness-ports/tests/run-all.sh` (`stage0-ci.yml:72`), so CI would
catch this break after the push. The stack's commit-time evidence is still false.

Blocking predicate: (1) contract mapping: contract item 7 makes `gate_files.py` "the project rule 'a changed file's
gate includes every test that names its path'"; round 2 item 1 makes the run list the union; the builder's deviation 3
promises "Every file left out is named on stderr and in `sources`, never dropped silently"; the repository-wide
anti-hollow-green invariant ("green without the claimed part actually running = capability does not exist") applies
to every gate. (2) Canonical: the production `gate` stack at the pinned lane files (hashes as in the premise).
(3) Material: the stack's green count is false evidence for the change. (4) Discriminator: the one-line break above,
rc 1 under `run-all.sh`'s form against rc 0 under `gate`. (5) Ownership: the fix sits in `scripts/gate_union.py` and
`scripts/stacks.toml`. For example, class `harness-ports/tests/*` as run by `run-all.sh`: name it "not run" like the
shell tests, or add a `run-all.sh` step when the union holds one. Or name any run-list file from which pytest collects
nothing. D-034: this is the headline capability of `gate` shown fake for a change class, so it is CORE-BLOCKING.

### F-1, second face (same root cause): a module-level `sys.exit` in a listed script aborts the whole pytest session

`harness-ports/tests/test_omniroute_local_builder.py` runs its checks at import and ends in a module-level
`sys.exit(1 if failed else 0)`. pytest 9.1.1 then stops the whole session with rc 3 and "no tests ran", the other
listed files included. I measured it first on a synthetic module of the same shape (`sys.exit(0)` beside a real
passing and failing file: rc 3, "no tests ran"). Then on the real file: importing it reads no secret, because the key
file is read only inside `main()` (`omniroute_local_builder.py:324`, in `def main` at 317), which the test never
calls. Results:
- `gate paths=harness-ports/bin/omniroute_local_builder.py mode=run runs=1 graph=no` → `exit 1 — required, not ok:
  run` · `## run · FAILED · rc 3` · `no tests ran`.
- `bash scripts/test_summary.sh --basetemp=... harness-ports/tests/test_omniroute_local_builder.py tests/test_jev_context.py`
  → `pytest-exit: 3` · `no tests ran`: the 49 real tests beside it did not run either.
- With the default `graph=yes`, ripwire links all nine `harness-ports/tests/*.py` files, this one included, to a change
  to `scripts/stack.py` alone (plan: `gate_files 1 · ripwire 105 · union 105 · run list 101`) and to the lane's
  own seven files (run list 102). So `gate mode=run` over the stack runner's own code can never pass. The builder
  never ran it (its NOT-done 1).
Fail-closed, so not a hollow green on its own. It is the same defect as F-1 and has the same fix.

### Other area-2 results
- **The comma join (deviation 1) is right and needed.** Measured with ripwire 0.4.0 directly on the scratch copy:
  `--test-gate=A` → `changed="1" tests="2"`; `--test-gate=B` → `changed="1" tests="12"`; `--test-gate=A,B` →
  `changed="2" tests="13"`; `--test-gate=A --test-gate=B` → `changed="1" tests="12"` (B only);
  `--test-gate=B --test-gate=A` → `changed="1" tests="2"` (A only). The wrapper's one-flag-per-file form keeps the last
  file only. The same measurement confirms the builder's D26(b): `lane_context.sh` passes files as separate
  arguments, so `ctx`'s test-gate section gates only the last file (F-6).
- **Deleted path.** `gate paths=scripts/owner_rulings.py` with the file moved away: `graph=yes` → `exit 1 — required,
  not ok: graph` (ripwire rc 1; union falls back to gate_files' 2 tests and says so); `graph=no` → exit 0,
  `gate_files 2 · run list 2`. As the builder's D32 says.
- **Width (D24) is unbounded, and stated only in the plan's own lines.** Plans with `graph=yes`: `scripts/report_lint.py`
  → run list 6; `scripts/hiccup_scan.py` → 15; `scripts/test_summary.sh` → 8; `scripts/stack.py` alone → 101, holding
  `tests/test_vendored_manifest.py` (the brief: a whole-file run copies about 3.4 GB) and all nine harness scripts. No
  cap and no refusal exist; `mode=run` plans and runs in one call. The only signs are `sources`' summary, `setid`'s
  `N files` and a registry comment ("read the plan first") (F-2).
- **"Not run" under the print cap.** The seven-file plan print is exactly 9,000 characters (9,028 bytes; the cap counts
  characters, as the contract says). `sources` was middle-cut: its summary line with the counts was lost. Of the four
  "not run" fixture rows, one survived, plus the stderr note in the tail. The header never states a not-run count
  (F-3).
- `tests/conftest.py` has no collection hook; no pytest-shaped file lies outside `tests/` and `harness-ports/tests/`,
  and none is named `*_test.py`.

## Area 3: a missing instrument never reads ok (round-2 item 3) — HOLDS for a missing binary

CI shape reproduced (not assumed): uid 1000 (`ubuntu`) through `setpriv`, Python 3.12.3 (an offline uv venv with CI's
install line), a PATH with none of rg, node, graft, ripwire, sentrux or code-review-graph, git trusting the scratch
repository through `GIT_CONFIG_*`, and NO `RIPWIRE_BIN`/`SENTRUX_BIN` (runner: `/tmp/vlsb9/asci.sh`).
- `bash scripts/test_summary.sh --basetemp=/tmp/vlsb9/ci/bt tests/test_stack.py` → `1 files set=2ac01abb1067` ·
  `pytest-summary: 145 passed, 2 skipped in 40.57s`; the two skips are the ripwire and rg reasons. So the builder's
  inferred claims hold as non-root: the deny-list cases through symlinks into `/root` pass (realpath's EACCES path).
- The real stacks in that shape, wrappers finding their own binary: `review files=scripts/gate_union.py` → exit 1;
  `## sentrux · unmapped — sentrux unavailable (not required)` and `## ripwire · unmapped — ripwire unavailable`, each
  with the wrapper's line `…/root/.local/bin/<tool> missing — run scripts/setup.sh (pinned install)`.
  `review mode=compare` → exit 0 (its only step is advisory and reads unmapped). `gate paths=scripts/report_lint.py`
  → exit 1, `graph · unmapped`. `impact sym=build_page` → exit 1, all four steps unmapped: gitnexus as `node`,
  both crg steps as `code-review-graph` (the `/root/venv-crg` candidate is unreadable to uid 1000).
  The builder's "assumed" item (NOT-done 6) is now verified.
- False positives: none reachable today. ripwire `edit-check` and `callers` for `MISSING_TEXT`, the test symbol whose
  value IS the sentence, quote it 0 times (6,181 and 3,874 bytes); the `impact` ripwire step reads ok for it.
  A symbol, word or path value cannot carry the sentence's space and dash.
- False negatives (F-4): a binary that is present but fails, or answers nothing, reads ok.
  `SENTRUX_BIN=/bin/false review mode=check` → exit 0, `## sentrux · ok · rc 0`, body `sentrux check: tool exit 1`
  (the wrapper always exits 0 without `--strict`). `RIPWIRE_BIN=/bin/true gate paths=scripts/report_lint.py` → exit
  0, `## graph · ok · rc 0`, union `ripwire no answer` (gate_files' list only). Round-2 item 3 names the missing
  binary, which holds. A failing or mute binary is outside its words: FOLLOW-UP (task #345 owns the wrapper; the stack
  can fail `union` when `--graph yes` meets no element).
- `ctx` (F-6, the builder's D26(c)): `lane_context.sh` keeps only ripwire's XML rows, so with ripwire missing its
  ripwire sections are blank and the `pack` step reads ok. It gates only the last file too (D26(b), measured above).
  The fix sits in `lane_context.sh`, outside the lane's boundary: FOLLOW-UP for #345.

## Area 4: `{tmp}`, the kill and the cap (round-2 items 4 and 6) — HOLDS as contracted, two disk hazards

Probes: `/tmp/vlsb9/probe/tmp_probe.py`, `tmp_adopt.py`, `cap_probe.py`, run against a temporary tree and registry.
- `{tmp}` seen from inside a step: mode `0o700`, `git rev-parse --show-toplevel` rc 128 (outside every work tree), owner
  uid 0; removed after an exit-0 run and after an exit-1 run; the header says `tmp /tmp/stack-<run id> · removed
  after the run`.
- The runner's signals, sent while a step slept inside `{tmp}`: SIGINT → rc 130, SIGTERM → rc 143, SIGHUP → rc 129.
  Each time the step is dead, `{tmp}` is removed, no record is written, and stderr says `interrupted by signal N; the
  live steps were killed, no record written`. SIGKILL → rc -9: the step lives on and `{tmp}` stays (as the builder
  documents); I killed the step by pid and removed the dir.
- Adoption (fault injection into the real `main()`: `utc_now` and `secrets.token_hex` pinned so the run id is known):
  a pre-created dir, a symlink to a victim dir and a dangling symlink at `/tmp/stack-<run id>` each give exit 3
  `{tmp} …: [Errno 17] File exists`, no step runs, the victim's files are untouched, and the pre-existing entry is left
  alone (`made` stays empty). The name is not practically predictable: the suffix is 24 bits from `secrets`. Residue:
  an empty `<log dir>/<run id>/` stays after that exit 3, with no record (INFO).
- The cap, a writer that ignores SIGTERM (`save_cap_mb = 1`, the writer self-bounded at 120 MB): the step is killed
  (`FAILED · rc -9 … killed: its saved output passed the 1 MB cap`, `truncated: true`, 1,048,652 bytes saved), but it
  wrote all 120 MB before the SIGKILL, 3 s after the SIGTERM. The saved file is capped; disk use during the grace is
  not. An unbounded writer at disk speed writes gigabytes in those 3 s plus the 0.1 s poll (F-7).
- A child left behind by a leader that exits at once: the stack exits 0 with the step `ok`, and the child goes on
  writing to the step's now-unlinked stdout after the stack is gone (3 MB → 10 MB in 1.5 s, measured). Neither the
  cap nor the timeout reaches it, and `du` cannot show the space (F-8; the builder's round-1 NOT-done names this
  child, but not the cap bypass).
- A truncated source feeds no chain: covered by the builder's R23 (reproduced under area 8).

## Area 5: `harvest` (round-2 item 7) — HOLDS on both real lanes; one multi-round edge

Independent oracle `/tmp/vlsb9/probe/hb_oracle.py`: streams the JSONL, reads only assistant records' `text` blocks and
`SubagentHandback` inputs (never a thinking field), neutralizes tags by a character scan (not a regex), and prints
line numbers, lengths and hashes only.

| lane | oracle | `harvest` (scratch, real transcript) |
|---|---|---|
| LS-B9 `ac753871198ee8cfd` (827 assistant records, 1 block each) | calls at lines 825 (40,436 ch) and 1863 (43,948 ch); long texts at 828 (2,643) and 1866 (3,995, after the last call); hand-back sha256 `e652a7022cde…`; no text longer before the last call | exit 0; `handback: found calls=2 chars=43948 … sha256=e652a7022cde`; `report: none longer than the hand-back (… 2643 …)`; lint on `handback.md` (MISS 2, advisory, `(not required)`) |
| scrubber repair `a88c7c57f2fa2a96b` (1131 records, 1 block each) | calls at 1136 (11,539) and 2496 (3,568); long texts at 2495 (63,540) and 2499 (2,910, the epilogue); report candidate sha256 `e692c1c6f80c…` | exit 0; hand-back `34835ad37c4d…` (3,568 ch); `report: saved chars=63540 … sha256=e692c1c6f80c`; the epilogue is not taken; lint on `report.md` (OK 1) |

Every saved file's full sha256 equals the oracle's. The report of record agrees too: the round-2 section of
`tasks/briefs/labeling/LS-B9-report.md` equals the last hand-back exactly, and its round-1 body equals the first
(sha256 prefix `43e02e6aa903`, 40,600 bytes, as the coordinator's note says).

Synthetic edges (`hb_edges.py`, `hb_edges2.py`; my own records only):
- a long text between two calls → saved as the report ✓; a long text only after the last call → no report (the
  builder's "before the last call" rule, deviation 6) ✓; 999 characters → none, 1,000 → saved ✓;
- a `tool_result` holding a hand-back-shaped JSON string (and the bytes `"assistant"`), and a `user` record carrying an
  assistant-shaped hand-back → neither taken ✓;
- tags: `<SyStEm-ReMiNdEr>`, `</FUNCTION_CALLS>`, `<parameter/>` and four `antml:` forms (the prefix built in code;
  typed literally it is stripped on the way in, the builder's D18) → neutralized; `<invoke_x>`, `<invoke-x>`, and an
  already-neutralized `<\system-reminder>` → left alone ✓; `<function_results>` and `<result>` are not in the
  contract's list and are left alone (INFO);
- thinking: from the code, `scan()` reads a block's `type`, then only `text` or a SubagentHandback `input.message`; a
  `thinking` field is never accessed. Synthetic thinking blocks holding `"SubagentHandback"`, 5,000 characters, sit
  before and after the call: no thinking text in any written file (`"THINK" in` every output → False). Two byte scans
  do touch the raw line, thinking bytes included: the `"assistant"` pre-filter, and the `unparsable` counter. A broken
  line whose only `"SubagentHandback"` bytes are its thinking text prints `unparsable=1` (measured). A count can
  move; no text is extracted (F-12, INFO).
- **F-11 (FOLLOW-UP): a stale earlier-round text is saved as the report.** A resumed lane that wrote a long report
  before its FIRST call and only a short summary at its LAST call: `report.md` holds the round-1 text
  (`ROUND1-REPORT …`, 5,600 characters, against an 80-character round-2 hand-back), and stdout points the lint at it.
  Both the contract's words ("the lane's last long assistant text block") and the builder's rule pick it, so it is no
  implementation deviation. But harvest then offers a previous round's text as this round's report of record. Fix:
  bound the search to text after the previous call.

## Area 6: ratings, records and the print (round-2 item 5, contract items 5-6) — HOLDS

Probe `/tmp/vlsb9/probe/rate_probe.py` (a registry with a `plain` stack, a `rated = true` stack `good`, and a foreach
stack over 300 files):
- Refusals, each exit 2, with 0 lines appended and 0 run dirs made: `rate <plain run>`; `good --rate <plain run>` (and
  the `good` step never ran, its marker unchanged); `rate <good run> <plain run>` (all or nothing: the valid half is
  not appended); `rate <good run>.nostep`; `rate …=3/4`; `plain --rate …=9/9`.
- `plain --rate <good run>=2/1` is accepted: a rated run's rating may ride on any run. That is the builder's flagged
  reading of "refuse any other run" (the rated run decides). It fits the words; INFO.
- 20 concurrent `good --rate …` runs into one log dir: all exit 0; 44 lines, every one whole JSON (21 ratings, 23
  run records). The flock serializes, and no line interleaves. (The mutation pass below shows no test holds the lock.)
- The print cap: the seven-file gate plan printed exactly 9,000 characters. When the section headers alone pass the cap
  (300 foreach sections), the print is cut at 9,000 with the marker `… the print is cut at 9,000 characters (the
  headers alone are over the cap)`. The first line keeps `exit N` and any `required, not ok:` list. But its
  `print capped … shortened <names>` line lists all 300 names, so no step status survives in the print (F-13, INFO: a
  count instead of the names would leave room).
- The header states: the exit code and the required steps not ok; tree and HEAD; the params; the output dir and the
  record path; the `{tmp}` line; `not selected:` with each reason; `print capped … shortened …`.

## Area 7: `review` and sentrux (round-2 item 2) — HOLDS; the shared baseline is a documented hazard

- **Which baseline `scripts/sentrux_review.sh` reads and writes:** `RT = ${SENTRUX_RUNTIME_DIR:-<script root>/.sentrux-runtime}`
  (line 28; the script root is the tree the wrapper lives in, so a worktree has its own). Every mode deletes and
  re-copies `RT/tree` (line 29) and copies `RT/baseline.json` into `RT/tree/.sentrux/baseline.json` (line 32). `save`
  writes the tree's baseline, then copies it to `RT/baseline.json` and writes `last-save.txt` (line 36). `compare`
  refuses with "no baseline" (exit 0) when `RT/baseline.json` is absent, else reads the tree copy just made from it
  (lines 37-38). Measured in scratch (`SENTRUX_RUNTIME_DIR=/tmp/vlsb9/srt`): after `save`, I overwrote the tree copy with
  `{"corrupted": true}`. `compare` still read `7140 -> 7140 · No degradation detected`, and afterwards the tree copy's
  sha256 again equalled `RT/baseline.json`'s (`ad71ba0cf04f462b`). So the only state a `compare` carries between runs
  is `RT/baseline.json`.
- **The lane's 18:3xZ smoke (D30) changed nothing a later `compare` reads.** In the main tree (read only), the two
  `baseline.json` files have the same sha256 prefix, `a7572c403775349b`. The 18:34 file under `tree/.sentrux/` is
  line 32's copy, and `RT/baseline.json` still has its 2026-09-07 22:57:01Z mtime. The smoke rewrote `tree/` and
  `last-check.txt` (18:34:17Z); `compare` reads neither across runs.
- **`review mode=save` with no `SENTRUX_RUNTIME_DIR`, in the main tree,** overwrites `.sentrux-runtime/baseline.json`
  (the one shared baseline, 2026-09-07), `last-save.txt` and `tree/`. The stack's own guidance ("`review mode=save`
  before a build lane, `compare` after") then lets two lanes clobber each other's baseline. So do two concurrent
  `review` runs of any mode (each `rm -rf RT/tree` under the other's scan). The builder's D27; the registry has no
  per-run env to separate them (F-5, FOLLOW-UP, a pre-wiring note).
- **`lint_files.py` (deviation 4) against `lint_delta.py`'s rule on the same inputs** (scratch: a new unused import in
  `scripts/ci_gate.py`, a new undefined name in `scripts/owner_rulings.py`, an untracked `scripts/zz_probe_new.py`):
  `lint_delta.py --base HEAD --no-ap` → `2 .py changed, 2 NEW pyflakes hit(s), 0 removed`, rc 1.
  `lint_files.py` on the same files plus the untracked one → the same two NEW lines word for word, plus the untracked
  file's `'os' imported but unused (untracked: every hit is new)`, `0 removed`, rc 1. Through the `review` stack the
  `lint` step is `FAILED · rc 1` and the run exits 1. They agree where both see the file; `lint_files.py` also sees
  untracked files.

### F-1, third face (same root cause, the strongest reproduction): pytest runs a harness test whose checks never raise

`harness-ports/tests/test_lane_done_gate.py` has eight `test_*` functions, and pytest collects and runs them. But they
test through `check()` (lines 26-32), which counts `FAIL` and prints, and never raises (22 `check(` calls, one bare
`assert`). Under pytest a failing check passes; under `run-all.sh` its `main()` returns 1.
ripwire links this file to a change to `harness-ports/bin/lane-done-gate.py` (the Hermes lane done gate).
1. Plan: `gate paths=harness-ports/bin/lane-done-gate.py` → run list `harness-ports/tests/test_lane_done_gate.py
   ripwire` (the shell test `test_lane_profile.sh` is named "not run").
2. Control, `run-all.sh`'s form: `python3 harness-ports/tests/test_lane_done_gate.py` → `lane done gate: 19 passed,
   0 failed`, rc 0.
3. Break: `lane-done-gate.py:167` `passing = counts and exit_code == 0` → `exit_code in (0, 1)` (a check that exits 1
   now counts as passing: the done gate itself fails open).
4. `run-all.sh`'s form → `lane done gate: 18 passed, 1 failed`, rc 1.
5. `python3 scripts/stack.py --tree /tmp/vlsb9/repo --log-dir /tmp/vlsb9/logs/ldg gate paths=harness-ports/bin/lane-done-gate.py mode=run runs=1`
   (default `graph=yes`) → `stack gate · run s-20260928T203902Z-ce9af4 · exit 0` · `## run · ok · rc 0` ·
   `pytest-summary: 8 passed in 3.23s`.
Restored after; `git status` of the file is clean.

F-1's class, then: every `harness-ports/tests/*.py` is a `run-all.sh` script, and pytest is the wrong runner for all
nine. It silently skips five (`__main__`-guarded, no test function). It swallows the failures of one
(`test_lane_done_gate.py`, a non-raising `check()`; `test_qwen_matrix.py` is fine: 56 plain asserts, no counting
helper). It aborts the whole session on one (`test_omniroute_local_builder.py`, module-level `sys.exit`). The
builder's run-list rule (deviation 3) keys on the file name alone. No test covers this class: mutant V12 below moves
every `harness-ports/tests/` file out of the run list, and all existing tests stay green.

Canonical-tree check (allowed main-tree run, `--log-dir` in scratch, `PYTHONDONTWRITEBYTECODE=1`): `gate
paths=scripts/pc_bridge_exec.py` plan on `/home/user/agent-factory` at HEAD `0d06ae7` gives the same union
(`test_bridge_token_handling.py`, `test_pc_bridge_exec.py`, `tests/test_jev_context.py`, all `gate_files`, no "not
run"; `3 files set=1c4a5efeca8e`). The main tree's `git status` line count is unchanged by my runs. HEAD moved from the
premise's `ca29894` through `c13b9a1` and `0d06ae7`, which touch none of the lane files or F-1's inputs.

## Area 8: mutation — the builder's mutants reproduce; six contract clauses are not held by any test

Driver `/tmp/vlsb9/mut/driver.py`: one exact-anchor replacement per mutant (each anchor matched exactly once),
`py_compile`, then the named test functions with `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider` and a private
`--basetemp`. A kill counts only on a `FAILED`/`ERROR tests/test_stack.py::` line. The file is restored from a
pristine copy after each mutant, and its sha256 is re-checked. Control first: `CONTROL rc=0 79 passed in 23.31s`.
Summary: `TOTAL=21 KILLED=12 SURVIVED=9 INVALID=0`. Afterwards the seven lane files carry the premise hashes.

The builder's mutants (9 of 100 reproduced; the brief asked for at least 6, one per area):
| mutant | area | first FAILED line |
|---|---|---|
| R8-union-ignores-ripwire | gate union | `test_gate_union_unites_gate_files_and_ripwires_rows` |
| R2-unmapped-if-ignored | `unmapped_if` | `test_unmapped_if_turns_a_wrappers_missing_line_into_unmapped[required-out]` |
| R16b-tmp-removal-not-in-finally | `{tmp}` | `test_a_signal_to_the_runner_removes_its_tmp` |
| R18b-tmp-default-mode | `{tmp}` | `test_tmp_is_a_private_dir_outside_every_work_tree_removed_after_the_run[success]` |
| R20-no-size-check-while-running | the cap | `test_a_steps_saved_output_is_capped_and_a_truncated_source_feeds_no_chain` |
| R23-truncated-source-feeds-chain | the cap | the same test |
| R19-rated-unchecked | the rating refusal | `test_only_a_rated_stack_takes_ratings` |
| R25-report-last-long-overall | the extractor | `test_handback_extract_saves_the_lanes_longer_text_report` |
| MH1-first-call | the extractor | `test_handback_extract_writes_the_last_calls_message_with_its_tags_neutralized` |

My mutants for clauses the builder's set does not name:
| mutant | clause | result |
|---|---|---|
| V6 `start_new_session=False` | item 5, own session | KILLED (the timeout group test) |
| V10 record `head` → None | item 6, record fields | KILLED |
| V11 tag regex case-sensitive | item 7, neutralize | KILLED |
| V1 `fcntl.flock` removed | item 6, "under flock" | **SURVIVED** (no test holds the lock; my 20-process probe shows the real code serializes) |
| V2 handlers for SIGTERM only | round-2 item 4, "signal alike" | **SURVIVED** (tests send SIGTERM only; my live probe shows INT and HUP work) |
| V3 text accepts `\r` | item 4, text "no newline" | **SURVIVED** (no test sends `\r`; the real code refuses it, area 1) |
| V4 timeout bound 1..999999 | item 2, timeout 1 to 3600 | **SURVIVED** (only `timeout = 0` is tested) |
| V5 label regex → `.+` | item 2, the label regex | **SURVIVED** |
| V9 print cap checked at 9,100 | item 5, 9,000 characters | **SURVIVED** (the boundary is not probed) |
| V7 deny check on the realpath only | item 4 (defence in depth) | SURVIVED; not material (the program opens the realpath) |
| V8 `*_test.py` dropped from the run-list rule | deviation 3 | SURVIVED; not material today (no such file) |
| V12 every `harness-ports/tests/` file out of the run list | F-1's fix direction | SURVIVED: the fix breaks no existing test, and no test pins or catches F-1 |

## Gate B, fresh (scratch)

`bash scripts/test_summary.sh --basetemp=… tests/test_stack.py tests/test_no_laya_in_gates.py tests/test_s0_01_spec_runner.py tests/test_s0_11_eval_hardening.py tests/test_search_intercept.py`
→ `5 files set=2804489b9d6b` · `pytest-summary: 1 failed, 430 passed in 124.51s (0:02:04)`. The one failure is
`tests/test_search_intercept.py::test_semantic_grep_is_answered_once_then_the_identical_repeat_passes`, which expects a
graft answer. The archive copy has no `graft/INDEX.md` (gitignored), and the test fails the same way with the seven
lane files moved aside: an artifact of my copy, independent of the lane. I did not run that file in the main tree (its
hook can write the main tree's `.jev/`), so the builder's `431 passed` there is not re-run by me. `tests/test_stack.py`
alone: `147 passed` (premise and control). CI shape: `145 passed, 2 skipped`.

Evidence audit: the two `report_lint` MISS lines in the builder's round-2 hand-back are the pasted pytest lines
`SKIPPED [1] tests/test_stack.py:1464` and `:1610` (the decorator lines; my CI rehearsal printed the same two).
They are linter false positives. The `file:line` citations I opened (`ripwire_review.sh:36`, `:64`,
`sentrux_review.sh:37`, `stack.py:63`, `:65`, `:1141`, `handback_extract.py:51`, `:86`) say what the report says.
`gate_files.py` against an independent `grep -rlIF` oracle over 137 paths (`scripts/`, `src/`,
`harness-ports/bin/`, the lane files): 0 disagreements.

## Finding inventory (no severity filter)

Evidence: R = reproduced here; S = read from source; B = the builder's claim, checked.

| # | class | finding | evidence | contract mapping | canonical path | material effect | reproduction | suggested fix |
|---|---|---|---|---|---|---|---|---|
| F-1 | **BLOCKER** | `gate` feeds `harness-ports/tests/*.py` (`run-all.sh` scripts) to pytest: 5 are silently not run, 1 has its failures swallowed, 1 aborts the session; the print reads green or red and never says "not run" | R (three faces) | item 7 (the project rule), round-2 item 1 (the union runs), deviation 3's own "never dropped silently", the repo-wide anti-hollow-green invariant | production `gate` stack at the pinned lane files (scratch of HEAD) + a plan on the main tree | false green on a real break: `49 passed` over a broken bridge helper, `8 passed` over a fail-open lane done gate | area 2, F-1 steps 1-5 and the third face's steps 1-5 | in `gate_union.py`: treat `harness-ports/tests/*` as `run-all.sh` tests (name them "not run", or add a `run-all.sh`/`python3 FILE` step when the union holds one); a test with a guarded script, a non-raising check and a module-level exit |
| F-2 | FOLLOW-UP | `graph=yes` width unbounded: `scripts/stack.py` alone → 101 files, with `test_vendored_manifest.py` (3.4 GB whole-file run); `mode=run` plans and runs in one call | R | none (no bound in the contract) | production plan | disk/time risk; a wide run is always red today through F-1's abort | area 2, "Width" | refuse or confirm `mode=run` above N files; name known-heavy tests |
| F-3 | INFO | the print cap can middle-cut `sources`' summary and "not run" rows; the header has no not-run count | R | item 5 (cap holds) | production plan | "not run" can shrink to a fragment | seven-file plan print | put the summary first, or "not run: N" in the header |
| F-4 | FOLLOW-UP | a present-but-failing sentrux reads `ok` (wrapper exits 0); a mute ripwire (rc 0, no element) leaves `graph · ok` and the gate exits 0 on gate_files' list | R | round-2 item 3 names the missing binary only | production `review`, `gate` | an instrument failure reads ok | `SENTRUX_BIN=/bin/false review mode=check`; `RIPWIRE_BIN=/bin/true gate paths=scripts/report_lint.py` | `gate_union.py` exits non-zero on `--graph yes` with no element; #345 for the wrapper |
| F-5 | FOLLOW-UP | `review mode=save` overwrites the main tree's one shared `.sentrux-runtime/baseline.json`; concurrent reviews race on `rm -rf RT/tree` (D27) | R + S | none | wrapper lines 28-38 | a lane's compare can read another lane's baseline | area 7 | per-lane `SENTRUX_RUNTIME_DIR` (a step env field, or `{tmp}`-style dirs) |
| F-6 | FOLLOW-UP | `ctx` with ripwire missing: blank ripwire sections, `pack · ok`, exit 0; its test-gate gates only the last file (D26 b, c) | R | round-2 item 3 arguably ("every ripwire step"); D-104's record says ctx shows unmapped | production `ctx` | an unmapped area reads as "none found" | `RIPWIRE_BIN=/nonexistent/ripwire ctx files=scripts/gate_union.py sym=ripwire_tests` (PATH without graft) | #345 (`lane_context.sh`); or a dedicated `ripwire` step in `ctx` with `{files,}` and `unmapped_if` |
| F-7 | FOLLOW-UP | the cap kill gives a SIGTERM-deaf writer the 3 s grace: 120 MB written past a 1 MB cap (self-bounded writer) | R | round-2 item 6 caps the saved file (holds) | runner | disk fill during the grace | `cap_probe.py` flood | SIGKILL at once on a cap breach |
| F-8 | FOLLOW-UP | a child left behind by a leader that exits keeps writing to the unlinked stdout after the stack exits; no cap or timeout reaches it | R | none (item 5 covers the timeout only) | runner | unbounded, invisible disk use | `cap_probe.py` orphan | `killpg` the step's group after its leader exits |
| F-9 | INFO | `path`/`text` accept ESC, VT, NEL, U+2028, U+2029; they reach the print raw | R | item 4 holds (no NUL, no \\n, no \\r) | runner | a terminal or a Unicode line splitter can show forged lines | `argv_probe.py` | refuse C0/C1 and Unicode line separators, or escape them in the print |
| F-10 | INFO | deny list: a hardlink (B), `.pc-bridge.env.bak`, `.GIT/config` pass; `{transcript}` is not deny-checked (by design) | R | item 4 list holds | runner | none today | `argv_probe.py` | extend by pattern if wanted |
| F-11 | FOLLOW-UP | `harvest`: a stale earlier-round long text becomes `report.md` and the lint target when the last round wrote none | R (synthetic) | round-2 item 7(b) wording picks it too | `handback_extract.py` | a previous round's text offered as this round's report | `hb_edges.py` "stale-round1-report" | search only after the previous call |
| F-12 | INFO | the extractor's two byte scans touch thinking bytes; one can set `unparsable=1`; no thinking text is extracted | R (synthetic) | item 7 holds for text | `handback_extract.py` | a count only | `hb_edges2.py` | none needed |
| F-13 | INFO | headers-over-cap fallback: `shortened <all names>` crowds out every step status; the first line keeps the exit | R | item 5 holds | runner | detail lost | `rate_probe.py` 300 sections | print a count, not the names |
| F-14 | FOLLOW-UP | test gaps: V1 flock, V2 SIGINT/SIGHUP, V3 `\r`, V4 timeout bound, V5 label regex, V9 cap boundary survive (the code is right in each; verified live where noted) | R | items 2, 4, 5, 6; round-2 item 4 | tests | a regression there would pass the suite | area 8 | one test each |
| F-15 | INFO | `review` exits 0 when its only step, sentrux, is unmapped or has no baseline (advisory) | R | round-2 item 2 (advisory) | production `review` | a skipped save reads green | CI shape `review mode=compare` | say it in the catalog |
| F-16 | INFO | `find`'s chat step searches thinking blocks (`chat_find`'s `DEFAULT_KINDS` includes `thinking`); it prints locations only | S (not run) | none | — | none printed | `chat_find.py:67-69` | `--kind` without thinking, if wanted |
| F-17 | INFO | a setup refusal (exit 3, e.g. a `{tmp}` collision) leaves an empty `<log dir>/<run id>/` | R | item 6 (no record: holds) | runner | clutter | `tmp_adopt.py` | remove the run dir on a setup refusal |
| F-18 | INFO | `gate`'s default `graph=yes` exits 1 on any venue without ripwire (CI, a PC without it) and for a deleted path (D32) | R (CI shape) | round-2 item 1 default | production `gate` | pass `graph=no` there | area 3 | catalog note |
| F-19 | INFO | a rated run's rating may ride on an unrated stack's run (the builder's flagged reading) | R | round-2 item 5 wording fits | runner | none | `rate_probe.py` | none |
| F-20 | INFO | verified builder claims: comma join (deviation 1), the CI-shape assumption, `lint_files` = `lint_delta` on tracked files, harvest on both lanes = oracle, the report of record = the hand-backs, `.lanes-live` now lists the two helpers (the builder's NOT-done 9 is resolved) | R | — | — | — | areas 2-7 | — |

## What must hold before the stacks are wired into CLAUDE.md, the output styles and the SessionStart catalog

1. F-1 fixed. Until then, the catalog must say that `gate` never runs `harness-ports/tests/` and that
   `bash harness-ports/tests/run-all.sh` runs whenever `sources` lists one.
2. A green `gate` is read with its `sources` section; `gate` runs in plan mode first, and a wide plan (or one listing
   `tests/test_vendored_manifest.py`) is not run whole (F-2).
3. `graph=no` on any venue without ripwire (CI, a PC without it) and for a deleted path (F-18).
4. `review mode=save` overwrites the shared sentrux baseline. Either a per-lane `SENTRUX_RUNTIME_DIR` is set, or the
   save-before, compare-after routine is not put in the output styles as it stands (F-5).
5. The catalog must not say `ctx` shows a missing ripwire as unmapped (F-6). D-104's record says so for all four
   stacks; it holds for `gate`, `impact` and `review` only.
6. `review`'s sentrux section is advisory, and its `tool exit N` line is the only sign of a failed run (F-4, F-15).

## Reproduced, reviewed statically, skipped

- **Reproduced here:** the premise; the control; area 1 (560 runs); F-1's three faces through the production `gate`
  (scratch) and its plan on the main tree; the comma join; the deleted path; the width; the print cap; the CI shape;
  `unmapped_if` false positives and negatives; `ctx`'s blank sections; `{tmp}` mode, removal, the four signals and
  adoption; the cap overshoot and the orphan; `harvest` on both lanes against an oracle, and the report of record;
  the extractor's edges; ratings, the lock and the print; the sentrux baseline; `lint_files` against `lint_delta`;
  21 mutants; gate B once; `gate_files` against `grep`.
- **Read from source only:** `chat_find`'s default kinds (F-16); `pc_suite.sh`'s `set-id` arm (no bridge);
  `omniroute_local_builder.py`'s key read inside `main()` (why importing its test reads no secret);
  `tests/conftest.py` (no collection hook).
- **Skipped, and why:** running `find` (it scans every transcript's thinking blocks) and `ci` (a network call); both
  are unchanged in round 2 and explain-pinned. `gate mode=run` over wide plans (`test_vendored_manifest.py`, and the
  S0-05 egress tests as root). `test_search_intercept.py` in the main tree. Gate B's second run.
- **Standing rules:** no git write in the main tree; no bridge; no subagent; no outward action; no secret source read;
  no thinking block's content read (my oracle never touches the field; my synthetic thinking text is my own); other
  lanes' files untouched. The main tree was written only in this report.

## Gate recommendation

**NOT-READY** — F-1 meets the whole blocking predicate and is CORE-BLOCKING under D-034. It shows the headline
capability of `gate` fake for a change class: a real one-line break in `scripts/pc_bridge_exec.py` gates green
(`49 passed`), and so does one in `harness-ports/bin/lane-done-gate.py` (`8 passed`), while the test that names the
path and fails against the break never runs, or runs with its failures swallowed. Reproduction: area 2, F-1 steps 1-5
and the third face's steps 1-5 (scratch copy of HEAD plus the seven lane files at the premise hashes; the commands are
pasted there). The fix is inside the lane's boundary (`scripts/gate_union.py`, `scripts/stacks.toml`, one test).
Everything else is FOLLOW-UP or INFO. This recommendation rests on my reproductions; none of it depends on anything
unreproduced. Written by 20:4xZ.

## Cleanup (20:4xZ)

`/tmp/vlsb9/` (the scratch repo, the venv, the probes, the logs) is removed, and so are the three ripwire cache dirs
my scratch runs created (`/tmp/ripwire-0/20`, `35`, `4f`; the main tree's `66` is left). No `/tmp/stack-*` dir
remains. Disk: 12,147 MB free. In the main tree the only new file is this report. The seven lane files keep the
premise hashes and status. `.jev/stacks`, `.sentrux-runtime/` and `scripts/__pycache__` carry no mtime from my runs.

## Round 3

Written 2026-09-28 from 22:1xZ by the same verifier, resumed. Brief: `tasks/briefs/labeling/VERIFY-LS-B9-R3-brief.md`
(read in full). The contract under test: `tasks/briefs/labeling/LS-B9-R3-brief.md` items 1-7. The builder's account is
the `## Round 3` section of `tasks/briefs/labeling/LS-B9-report.md` (read in full); its claims are hypotheses here.

### Premise and control

`bash scripts/premise_block.sh` over the brief's block, from the main tree, with `PYTHONDONTWRITEBYTECODE=1`. The seven
lane files are untracked, with the brief's hashes (`a3a24981247588c7` … `96c44e0a388ca856`) and line counts. The
`stacks.toml` field lines match, and `pytest-summary: 177 passed`. Two lines moved, both expected: HEAD is now
`1cdbde5`, and `LS-B9-report.md` no longer shows ` M`, because the coordinator committed the round-3 report (origin's
`a430de7`, `82a0686`); `df` shows more space. No lane-file difference, so no CONTRACT-INVALID stop.

Scratch: `/tmp/vlsb9r3/repo` = `git archive HEAD` (`1cdbde5`) as its own git repository (`f5c4e48`), with the seven
lane files on top, untracked, at the premise hashes. Control: `1 files set=2ac01abb1067` ·
`pytest-summary: 177 passed in 60.70s (0:01:00)`.

### R3 area 1: F-1 through my own reproductions — FIXED

Each face through the production `gate` stack in the scratch copy (the default `graph=yes` unless stated; each break
made in scratch only and restored, `git status` clean after):

| face | round 2 | round 3 |
|---|---|---|
| `scripts/pc_bridge_exec.py`: non-JSON reply `rc 3` → `rc 0` | exit 0, `49 passed` | `exit 1 — required, not ok: scripts`; headline `pytest 1 · python3 2 · bash 0 · not run 0`; `run · ok` (`49 passed`); `scripts[1/2] · ok` (`test_bridge_token_handling: 9 checks passed`); `scripts[2/2] · FAILED · rc 1` (`AssertionError: (0, '')`) |
| `harness-ports/bin/lane-done-gate.py:167`: `exit_code == 0` → `in (0, 1)` | exit 0, `8 passed` | `exit 1 — required, not ok: scripts`; `pytest 0 · python3 1 · bash 1`; `scripts[1/1] · FAILED · rc 1` with the script's own `lane done gate: 18 passed, 1 failed`; `shells[1/1] · ok` (`test_lane_profile.sh`) |
| `omniroute_local_builder.py`, no edit, `graph=no` | pytest rc 3, "no tests ran" | exit 0; `scripts[1/1] · ok`, the script's own `test_omniroute_local_builder: 24 checks passed` |
| NEW: the omniroute builder broken (`NODE_NAME` default changed), `graph=no` | — | `exit 1 — required, not ok: scripts`; `scripts[1/1] · FAILED · rc 1` |

Hunting the class further:
- **The classifier against an independent oracle.** I parsed `harness-ports/tests/run-all.sh` itself: its loop's
  `python3 "$HERE/$t"` list and every `python3|bash "$HERE/<file>"` line. That gives each harness file's real runner. I
  compared it with `gate_union.runner_of` for all 19 files in `harness-ports/tests/`: 0 disagreements (18 run by
  `run-all.sh`; `run-all.sh` itself goes to bash, as CI runs it at `stage0-ci.yml:72`).
- **No script-style `test_*.py` under `tests/`:** an AST scan of every `tests/**/test_*.py` and `*_test.py` finds each
  with a module-level `test*` function or `Test*` class (0 candidates). So the pytest route has no F-1 hole today.
- **A runner failure that still reads ok:** each runner's own exit code decides (`ok_rc [0]`), as in `run-all.sh`. A
  script that is gone at run time reads `unmapped` (required, exit 1). None found.
- **A file dropped without a "not run" line:** every union file gets a runner or a reason, and gone rows get their
  own line (the builder's unit test). None found.
- **A headline that disagrees with what ran:** the four faces' headlines match the calls made. With `runs=2`, pytest
  ran twice (`run[1/2]`, `run[2/2]`) and each harness script once (`scripts[1/2]`, `scripts[2/2]` are file 1 and 2 of
  2). The shared `[k/N]` notation reads the same for "run k" and "file k" (INFO).
- **Does the new stray kill cut an instrument's helper?** `graft ask` on a tiny repo through a stack step: `ok · rc 0 ·
  0.40 s`, no `strays_killed`, and none of my graft processes remain. GitNexus and code-review-graph have no index in
  scratch, so they were not tested.

### R3 area 2: the four new runner features and the changed semantics — HOLD; two INFO

Probe `/tmp/vlsb9r3/probe/feat.py`:
- `foreach = "@step"`: 300 lines → 300 calls, exit 0, 1.4 s. The print is capped at 9,000 characters with its first
  line intact (F-13's fallback). A line outside the tree skips the step (the builder's test). A blank line is dropped.
  A line that passes the checks reaches the program as `{tree}/<line>`, one argv element.
- `empty_ok` hides no failure: a source that fails silently (rc 3, no output) still skips its `empty_ok` consumer
  (`SKIPPED — its input step src failed (rc 3)`), exit 1. Only "ok and printed nothing" becomes "not selected".
- `needs`: a prerequisite that failed, timed out, or was unmapped each skips the dependent step with that reason
  (`failed (rc 1)`, `timed out`, `was unmapped`), exit 1.
- `headline`: a 600-character first line is cut to `HEADLINE_MAX` (500) plus `…` (header line length 506). The first
  line is copied raw, though: the header's bytes were `hl · COUNTS ok\rFORGED exit 0`, and in a terminal the CR lets
  the forged text overwrite the line (F-9's class; INFO: the gate's own headline is `gate_union.py`'s computed line).
- Discrepancy 2 (an empty pytest list no longer fails the gate) is right: the done-gate face ran with `pytest 0` and
  was decided by `scripts` and `shells`. An all-empty run list still fails (`NOTHING TO RUN`, the builder's tests).
  NOT-done 2 (harness tests run once while pytest runs `runs` times) is as described (above).

### R3 area 3: F-2 and F-3 — HOLD; one gap in F-3's "never"

- The bound, `gate paths=scripts/pc_bridge_exec.py mode=run runs=1 graph=no` (a run list of 3): `max_files=2` → exit 1,
  headline `… · REFUSED: mode=run runs at most max_files=2 files; pass max_files=3 …`, nothing ran; `max_files=3` →
  exit 0, all three ran; `max_files=4` → exit 0.
- The heavy file: `gate paths=scripts/vendored_manifest.py` (plan): `run list 5 of union 6 · … · not run 1`, and
  `tests/test_vendored_manifest.py  ripwire · not run: a whole-file run copies about 3.4 GB …; run its one relevant
  test: python3 -m pytest tests/test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation …`. That
  test exists (`tests/test_vendored_manifest.py:187`).
- The headline's counts match the actual calls on every face (area 1).
- **F-3 residual (FOLLOW-UP, R3-F1):** the header can itself pass the cap. `gate paths=scripts/report_lint.py,<180 more
  paths>` (a `paths` value of 9,562 characters; `graph=no`, plan) printed exactly 9,000 characters in 4 lines: the
  first line (`exit 0`), the tree line, the cut `params:` line and the fallback marker. The `sources ·` counts line
  was gone; the record's saved output held `run list 4 of union 4: pytest 3 · python3 0 · bash 1 · not run 0`. So
  contract item 2's "so the print cap can never cut them" fails past about 180 paths: `params:` precedes the
  headline, and the fallback cuts from the end. Fix: put the headline lines before `params:`, or cut `params:` first.

### R3 area 4: F-7, F-8, F-11, F-14 — HOLD; two residuals

- **F-7** (`/tmp/vlsb9r3/probe/cap3.py`, a writer at full speed that records any SIGTERM, self-bounded at 150 MB,
  `save_cap_mb = 1`): `FAILED · rc -9`, `truncated: true`, no SIGTERM received, 16 MB written before the kill (round
  2's grace: 120 MB). What is left is the 0.1 s poll times the write speed (INFO).
- **F-8:** a same-group child left writing by a leader that exits: the step reads `ok`, `strays_killed: true`, and the
  child is dead after the run (its output stopped at 4 MB). **Residual (FOLLOW-UP, R3-F2):** a child that starts its
  own session (`start_new_session=True`, as `setsid` does) escapes. The step reads `ok` with no strays recorded, and
  after the stack exits the child writes on to the unlinked stdout (9 → 19 MB, measured); I killed it by pid. Under a
  1 MB cap such a child also escapes the cap kill (7 → 16 MB). This is the builder's round-1 "a step that calls
  setsid". Contract item 5 names the process group, which this child has left.
  The pid-reuse window was reviewed statically. After the reap, `killpg(leader pid)` targets the group. Linux does
  not reuse a pid while any process still holds it as a group id, so a live stray keeps the id safe. An empty group
  gives ESRCH and nothing is sent. The only race is a full pid-space wrap plus a new group leader, inside the
  microseconds between the reap and the `killpg`. The timeout path shares it. INFO.
- **F-11 on real transcripts** (oracle `hb_oracle3.py`, round 3's rule): the LS-B9 lane (3 calls, at lines 825, 1863
  and 2373) → hand-back 33,227 characters, sha256 `620593bc072e` (the coordinator's recorded hash), no report. The
  scrubber lane, live (SCRUB2-R1 round 3 is running in the same agent; its transcript was 13.6 MB and still growing at
  22:21Z), gives `report: saved chars=63540 … sha256=e692c1c6f80c`, as in round 2. `harvest` matches the oracle on
  both.
  **Residual (FOLLOW-UP, R3-F3): the previous round's epilogue lies inside the new round's window.** In the LS-B9
  transcript (record types and timestamps only), round 2's call is at line 1863 (19:39:31Z). Its 3,995-character
  epilogue text is at 1866 (19:39:47Z), and round 3's resume message is at 1867-1868 (20:46:55Z). So 1866 falls
  between the previous call and the last, and round 3 escaped only because its hand-back was longer. Synthetic
  (`R1 report, call 1, R1 epilogue (4,000 ch), resume, a short text, call 2 (160 ch)`): `report.md` holds
  `ROUND1-EPILOGUE …` and stdout points the lint at it. The control, where round 2 writes its own long text, picks
  `ROUND2-REPORT`. So contract item 6's "an earlier round's text is never this round's report" fails for the epilogue.
  Fix: start the window at the first user record after the previous call (the resume message).
- **F-14:** my six round-2 mutants against the new tests (area 6): each is now KILLED — V1 by
  `test_the_record_waits_for_the_log_lock`, V2 by `[INT]`, V3 by `[text-cr]`, V4 by `[timeout-3601]`, V5 by
  `[label-uppercase]`, V9 by `test_the_print_cap_holds_at_exactly_9000_characters`.

### R3 area 6: mutation — the builder's reproduce; four new survivors, all test gaps

Driver `/tmp/vlsb9r3/mut/driver.py` (round 2's design: one exact anchor each, all 24 matched once; restore and re-hash
after each). Control: `CONTROL rc=0 76 passed in 20.61s`. Summary: `TOTAL=24 KILLED=20 SURVIVED=4 INVALID=0`. The seven
lane files carry the premise hashes afterwards.

- **The builder's r3 mutants, 10 reproduced as FAILED tests** (the brief's five marked \*):
  - T1\* (harness scripts to pytest): `…[counting-check]`;
  - W1\* (no width bound): `…refuses_a_run_list_wider_than_max_files[run-over]`;
  - W5 (the manifest run whole): `…gives_each_file_its_runner_or_says_why_not`;
  - W6 (nothing to run exits 0): `…fails_when_nothing_runs[nothing-names-it]`;
  - K1\* (grace at the cap): `…save_cap_gets_sigkill_at_once`;
  - S1\* (strays left running): `…loses_what_it_left_running`;
  - B1\* (the search not bounded): `…takes_the_report_only_from_the_last_round`;
  - H1 (headline ignored), E1 (`empty_ok` ignored) and W4 (`needs` ignored): each fails its test.
- **F-14:** V1, V2, V3, V4, V5 and V9 are KILLED (area 4).
- **Mine, one per round-3 clause no row names:**
  - KILLED: X4 (`shells` fed the python3 list): `…[module-exit]`; X5 (`scripts` without `needs`): the refused-run
    test; X7 (the `max_files` default 40 → 4000): the `gate` explain pin; X8 (`setid` without `empty_ok`): the
    nothing-to-run test.
  - **SURVIVED X1** (item 5): the stray kill sends SIGTERM, not SIGKILL. The test's child dies of either signal; a child
    that ignores SIGTERM would write on.
  - **SURVIVED X2** (headline): no cut at `HEADLINE_MAX`. No test gives a long first line; the code does cut (area 2).
  - **SURVIVED X3** (item 1): `run-all.sh` no longer routed to bash. No test gates a path that only `run-all.sh` names
    (e.g. `harness-ports/bin/build-roles.py`, its line 72); with the mutant such a gate is NOTHING TO RUN, a false red.
  - **SURVIVED X6** (item 3): `shells` without `needs`. The refused-run test has no `.sh` test, so a REFUSED run could
    still run every shell test. The code is right today.

### R3 fresh gates

- `tests/test_stack.py` (scratch, `test_summary.sh`): `1 files set=2ac01abb1067` · `pytest-summary: 177 passed in
  60.70s (0:01:00)`.
- CI shape (uid 1000, Python 3.12.3 offline venv, no instrument on the PATH, no `*_BIN` variable):
  `1 files set=2ac01abb1067` · `pytest-summary: 175 passed, 2 skipped in 55.23s` (the ripwire and rg skips).
- Gate B (scratch; a direct `python3 -m pytest -q -rf` run, to name the failure, not `test_summary.sh`): `5 files
  set=2804489b9d6b` → `1 failed, 460 passed in 132.10s`. The failure is round 2's archive-copy artifact,
  `test_search_intercept.py`'s graft test, which needs `graft/INDEX.md`.
- Not re-run by me: `run-all.sh` whole. In the archive copy, `test_lane_context.sh` would build a graft index of the
  whole copy. The gate itself ran five of its scripts above, and my oracle checked the routing.
- Evidence audit of the round-3 hand-back (my harvest's lint: `48 refs — OK 44, NEAR 1, MISS 3`). The NEAR and the
  first MISS cite the right test functions (`tests/test_stack.py:941`, `:973`) in words the linter does not match; the
  other two MISS are pasted pytest `SKIPPED` lines, as in round 2. The eight citations I opened say what the report
  says (`gate_union.py:78`; `stack.py:92`, `:93`, `:815`, `:887`, `:892`, `:992`; `handback_extract.py:88`).

### R3 area 5: the pre-wiring list of six, now

1. F-1 fixed — **holds now.** Keep two catalog notes: `runs=2` re-runs the pytest files only (harness scripts and
   shell tests run once), and `setid` covers the pytest files only.
2. Read the counts; plan first; nothing wide or heavy runs whole — **holds**: the counts are in the header, `mode=run`
   refuses more than `max_files` (40), and the manifest test is named "not run" with its `-k` command. One note stays:
   past about 180 paths, `params:` pushes the counts out of the print (R3-F1); read `sources.out` then.
3. `graph=no` where ripwire is missing and for a deleted path — **still a catalog note** (unchanged; the builder's CI
   run shows `gate rc 1 · graph=unmapped`).
4. `review mode=save` overwrites the shared sentrux baseline — **still a note** (unchanged; task #345).
5. `ctx` does not show a missing ripwire as unmapped — **still a note**; the catalog must not claim it (task #345).
6. `review`'s sentrux section is advisory; `tool exit N` is the only sign of a failed run — **still a note**.
7. New: for a resumed lane, check `harvest`'s `report:` line. A report that is the previous round's epilogue text
   (R3-F3) is not this round's report; use the hand-back.

### R3 finding inventory

| # | class | finding | evidence | contract mapping | canonical path | material effect | reproduction | suggested fix |
|---|---|---|---|---|---|---|---|---|
| F-1 | CLOSED | every union file under its own runner, or named "not run" | R (4 faces + the `run-all.sh` oracle) | item 1 | production `gate` | — | area 1 | — |
| R3-F1 | FOLLOW-UP | past ~9,000 characters of `paths`, the header passes the cap and the counts line is cut | R | item 2's "never" | production `gate` | counts invisible for a very wide change; exit code intact | area 3 | headline lines before `params:`, or cut `params:` first |
| R3-F2 | FOLLOW-UP | a child in its own session escapes the stray kill (and the cap and timeout kills), writing after the stack exits | R | item 5 names the group (holds) | runner | unbounded writes from such a child | `cap3.py` setsid case | a cgroup or `PR_SET_CHILD_SUBREAPER` sweep |
| R3-F3 | FOLLOW-UP | the previous round's epilogue sits in the new round's report window | R (synthetic + real transcript's shape) | item 6's "never" | `handback_extract.py` via `harvest` | an old epilogue offered as this round's report | area 4 | bound the window at the resume record |
| R3-F4 | FOLLOW-UP | test gaps: X1, X2, X3, X6 survive | R | items 1, 3, 5; the headline | tests | a regression there passes the suite | area 6 | one test each |
| R3-F5 | INFO | a headline's first line enters the header raw (CR, ESC) | R | none | runner | terminal overwrite in a contrived stack | `feat.py` headcr | escape control characters |
| R3-F6 | INFO | the cap kill's overshoot is the 0.1 s poll times the write speed (16 MB measured) | R | item 4 holds | runner | small | `cap3.py` flood | a shorter poll, if wanted |
| R3-F7 | INFO | `[k/N]` reads alike for repeat and foreach; `setid` omits the harness files; harness tests run once | R | NOT-done 2 | print | reader confusion | area 1 | name the axis ("file k of N") |
| R3-F8 | INFO | the stray kill was not tried against GitNexus or code-review-graph helpers (no index in scratch); graft leaves none | R (graft only) | — | — | unknown for two instruments | — | check on the main tree |

Every round-2 follow-up not named in round 3's contract stands as filed (F-4, F-5, F-6, F-9, F-10, F-12, F-13,
F-15 to F-19).

### R3 gate recommendation

**MERGE-READY-WITH-FOLLOWUPS.** F-1, the round-2 blocker, is fixed and verified. Each face of mine now fails or passes
on the right test's own verdict. The routing agrees with `run-all.sh`'s own text for all 19 harness files. No script
test hides under `tests/`. Contract items 1-7 hold on their main paths, each with a killed mutant. Two residuals
contradict an item's "never": R3-F1 (item 2, past ~180 paths) and R3-F3 (item 6, the previous round's epilogue). With
R3-F2 and the four test gaps they are not CORE-BLOCKING under D-034: none shows a headline capability fake, the
gate's exit code and the hand-back stay right, and each needs an edge input. Filed as follow-ups with the fixes named.
Before wiring: the notes in R3 area 5. Items 1 and 2 are settled, apart from the notes kept under them; items 3-6 are
unchanged from round 2; item 7 is new.
This recommendation rests on my own reproductions; nothing in it depends on an unreproduced claim. Written by 22:3xZ.

### R3 cleanup (22:3xZ)

`/tmp/vlsb9r3/` (the scratch repo, the probes, the mutation driver, the logs) is removed. So is the ripwire cache dir
my scratch runs created (`/tmp/ripwire-0/1c`); `66` (the main tree's) and the 17:3x dirs are not mine and are left.
No `/tmp/stack-*` dir remains, and no probe process is alive (`pgrep -f '[v]lsb9r3'` rc 1). The setsid child from
R3-F2's probe was killed by pid during the probe. Disk: 12,025 MB free. In the main tree the only change is this report;
the seven lane files keep the premise hashes and status (re-checked at the end).
