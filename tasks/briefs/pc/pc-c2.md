# C2 — the lane done-gate on Hermes `pre_verify` (task #148; Canny port, option 1 of the owner's decision #129)

PIN: 4a38190 (the origin head; every boundary file below is byte-identical there — premise below). Confirm with `git log --format='%h %s' -2 4a38190`.
LANE: pc-c2
ROLE: code-implementer. Route: the CLOUD build route (`HERMES_MODEL=agentfactory-build`, reasoning ultra). Venue:
`tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey `ultra` Lever-2: your report is DATA — files:lines, pasted counts, discrepancies,
NOT-done. Do NOT spawn subagents.

WHY THIS LANE EXISTS. Lanes report done while their last edit was never re-checked. Canny's done-gate predicate ("a code file changed and
no check has passed since that edit", `docs/research/findings/CANNY-AUDIT-2026-09-23.md` §4 item 2) is the fix the owner chose (option 1:
port the deterministic core, no Jev). C1 (`scripts/verify_command.py`, the check classifier) landed and was verified (VERIFY-C1-R1:
MERGE-READY-WITH-FOLLOWUPS). C2 wires a done-gate into PC lanes through Hermes's own hooks. THE MEASUREMENT THAT SHAPES THIS LANE (premise
below): C1's classifier accepts 0 of the 109 terminal commands two recent PC lanes actually ran, because our lanes run their gates as
`bash harness-ports/tests/*.sh`, `bash scripts/lane_gate.sh`, `bash scripts/test_summary.sh`, `python3 harness-ports/tests/test_*.py`, or
wrap pytest in `set -o pipefail; … | tee …; rc=${PIPESTATUS[0]}; …; exit "$rc"`. A done-gate built on C1's default list would nudge every
lane. The project check list, graded against bash, is the heart of this lane.

## The contract

1. **Premise first.** Re-measure the block below (blob ids, test baselines, the classifier table). A mismatch is STOP CONTRACT-INVALID.
   The Hermes excerpts and the 109-command corpus are the coordinator's read-only measurements of `~/.hermes/`, which you may not read:
   take them as given, say so in the report, and build your fixtures from exactly these shapes.
2. **The project check list (`CHECKS`), graded against bash (AF-AP-133).** From the measured corpus below, define the CLOSED set of command
   shapes that count as a passing check in our lanes: at least pytest in any interpreter form C1 already accepts; `bash
   harness-ports/tests/<name>.sh`; `python3 harness-ports/tests/test_<name>.py`; `bash scripts/lane_gate.sh …`; `bash scripts/test_summary.sh
   …`; and the pipefail-tee idiom `set -o pipefail; <check> | tee <file>; rc=${PIPESTATUS[0]}; …; exit "$rc"` only in the exact shapes the
   bash grade proves. Decide about `bash -n` (a syntax check) and state why. Reuse C1: `is_verify(command, patterns)` REPLACES the default
   list, so pass C1's `VERIFY` patterns (their `.pattern` strings) plus yours; add a narrow recognizer only where a shape cannot be a
   pattern (the rc idiom), and never modify `scripts/verify_command.py` (if C1 must change, STOP and report). THE GRADE, for every shape you
   accept AND for at least 12 near-miss shapes you reject (`rc=${PIPESTATUS[1]}`, `exit 0`, `; true`, `|| true`, `&` background, a trailing
   `echo`, a missing `set -o pipefail`, …): run the shape through `bash` with the check replaced by a stub that fails (exit 1) and by one
   that passes, in a scratch directory, and assert that every ACCEPTED shape exits non-zero with the failing stub and zero with the passing
   stub. A shape that fails the grade is rejected, whatever its look. Deliverable: the 109-command corpus re-classified (before/after counts,
   and the table of what counts now, what does not, and why).
3. **`harness-ports/bin/lane-done-gate.py record` — the post_tool_call observer.** Input: the stdin payload in the MEASURED shape (premise):
   `{hook_event_name, tool_name, tool_input, session_id, cwd, extra}` with `extra.result`, `extra.status`, `extra.tool_call_id`, … Record one
   JSON line per fact into a per-session ledger OUTSIDE the repository (the OS temp directory, the name keyed by sha256 of the repository
   root's first 12 hex digits plus the sanitized session id — the same scheme as `spool_file` in `harness-ports/bin/hermes-hook-adapter.py`,
   reimplemented, not imported):
   - `write_file` {path} and `patch` {path} (replace mode) → an `edit` fact per path; `patch` in V4A mode {mode:"patch", patch:"…"} → an
     `edit` fact for every path named on a `*** Add File: `, `*** Update File: `, `*** Delete File: ` or `*** Move to: ` line.
   - `terminal` {command} → a `check` fact: the command, its `exit_code` parsed from `extra.result` (a JSON string carrying `output`,
     `exit_code`, `error`; premise), and `passing` = the command counts under item 2 AND `exit_code` is an `int` (not `bool`) equal to 0.
     A result that does not parse, or carries no int `exit_code`, is recorded as not passing with the reason.
   Observer contract: stdout stays EMPTY (Hermes discards it anyway), the exit code is always 0, and any error is ONE line on stderr. Never
   write inside the repository or the lane tree.
4. **`harness-ports/bin/lane-done-gate.py gate` — the pre_verify directive.** Input: the pre_verify payload (premise: `extra.changed_paths`,
   `extra.attempt`, `extra.final_response`, `extra.coding`). Nudge when a CODE-file `edit` fact comes after the last `passing` check fact
   (sequence order in the ledger). A code path in `changed_paths` with no `edit` fact (an edit made through the terminal) has an unknown
   order: it triggers the nudge only when the ledger holds no passing check at all; otherwise name it in one stderr line. The nudge is exactly
   one JSON object `{"decision": "block", "reason": "<text>"}` (≤ 1,500 bytes) naming at most 5 paths plus "and N more", the last passing
   check (or "none"), and the instruction: re-run the checks that cover those files, then print the COMPLETE final report again, because the
   harness keeps only the last message. No nudge → print nothing. Never log or echo `final_response` (it is the lane's report); its length
   only. **The code-file rule (closed):** a path counts when its suffix is one of `.py .sh .bash .js .mjs .cjs .ts .rs .go .toml .yaml .yml
   .json .sql .c .h`, or it has no suffix and its first two bytes are `#!`; `*.md`, `*.txt` and anything under `transcripts/` never count.
   The lane's own report and draft are Markdown, so a report written after the last check never triggers the gate.
5. **The wiring, in the lane's cloned profile only — `harness-ports/bin/lane-profile.sh`.** When `LANE_DONE_GATE=1` is set in its
   environment at `create`, the clone's `config.yaml` gains EXACTLY two hook entries: `hooks.post_tool_call` gets `{matcher:
   "terminal|patch|write_file", command: "python3 <repo>/harness-ports/bin/lane-done-gate.py record", timeout: 20}` appended after the
   existing entries, and `hooks.pre_verify` becomes `[{command: "python3 <repo>/harness-ports/bin/lane-done-gate.py gate", timeout: 20}]`
   (the source profile has no pre_verify today; premise). `<repo>` is the helper's own repository root (the main clone), never the lane
   tree: a lane must not be able to edit its own gate (AF-AP-148). Extend the existing semantic-delta guard so the rewrite is refused
   unless the delta is exactly the current one plus these entries; `verify` accepts a clone with or without exactly these two entries and
   refuses any other hooks delta. With the switch OFF, the clone's `config.yaml` is BYTE-IDENTICAL to today's output (a regression test
   compares bytes). Lanes run Hermes with `--accept-hooks` (premise), so no allowlist edit is needed; say so in the report. Forwarding
   `LANE_DONE_GATE` from the dispatcher (`scripts/pc_lane.sh`) is OUT of this lane (that file is under VERIFY-T94).
6. **Tests.** CREATE `harness-ports/tests/test_lane_done_gate.py` (run by `python3`, printing a `N passed, M failed` summary like its
   neighbours), extend `harness-ports/tests/test_lane_profile.sh`, and add the new test to `harness-ports/tests/run-all.sh`. At least:
   (a) edit → passing check → gate silent; (b) passing check → edit → nudge naming the path and the last check; (c) a check that exits 0 but
   does not count (`echo ok`, `pytest -q | tail -1`) → nudge; (d) `exit_code` 1, missing, `"0"` (string), `true` (bool) → not passing;
   (e) `extra.result` not JSON → not passing + one stderr line; (f) a `.md` edit after the check → silent; an extensionless `#!` file → code;
   (g) a V4A multi-file patch → one edit fact per named file; (h) two session ids never share a ledger; the ledger never lands under the repo
   root; (i) malformed stdin → exit 0, stdout empty, one stderr line; (j) the terminal-only edit rule of item 4 (both branches); (k) the bash
   grade of item 2 as data-driven cases; (l) lane-profile: switch OFF byte-identical, switch ON exactly the two entries, `verify` refuses a
   third entry and a changed command. Every existing test stays green.
7. **Mutants (each on a scratch copy under `../scratch/mut/`, never in your tree).** At least: the gate ignores order (any passing check
   anywhere silences it); `passing` without the exit-code test; `bool` accepted as an exit code; the code-file rule counting `.md`; the
   ledger keyed by repository only (sessions share); the recorder writing inside the repo root; lane-profile adding the hooks with the switch
   OFF; the semantic guard not extended (an extra key passes); one of your accepted shapes widened past its bash grade. Each must red a named
   test for the stated reason; paste the table.
8. **Gates (each call under the 420 s cap).** The new test twice with identical counts; `bash harness-ports/tests/test_lane_profile.sh`
   twice (baseline `lane profile: 9 passed, 0 failed`); `bash harness-ports/tests/run-all.sh` once, pasted; `python -m pytest -q -p
   no:cacheprovider --basetemp ../scratch/bt tests/test_verify_command.py` once (C1 untouched; paste the count).

BOUNDARY (exact). CREATE `harness-ports/bin/lane-done-gate.py`, `harness-ports/tests/test_lane_done_gate.py`,
`tasks/briefs/canny/C2-report.md` (write it incrementally from the start). MODIFY `harness-ports/bin/lane-profile.sh`,
`harness-ports/tests/test_lane_profile.sh`, `harness-ports/tests/run-all.sh`. READ-ONLY: everything else — in particular
`scripts/verify_command.py`, `harness-ports/bin/pc-lane.sh`, `scripts/pc_lane.sh`, `harness-ports/bin/hermes-hook-adapter.py`, `.claude/`,
`sandbox-kit/`. Standing rules: touch ONLY the boundary files; report adjacent defects, never fix them. Never run git add, commit, stash,
checkout, restore, reset or clean. Never read `~/.hermes/` (the Hermes facts you need are pasted below) and never run `hermes` itself: the
live check of the gate in a real lane is the coordinator's, after landing. Never touch the clone's `.lanes/` outside your own lane directory.
No bridge tools. Take no outward-facing action. Fake strings only. Paste every count and timestamp from command output. A deviation from any
contract line is STOP-and-report, never a self-accepted change.

## PREMISE — MEASURED at authoring (2026-09-23 19:04Z; /home/user/agent-factory@4a38190 and, read-only, the PC's Hermes lane runtime)
```
$ for f in <boundary + C1>; do echo "$(git rev-parse 4a38190:$f | cut -c1-12) $(git show 4a38190:$f | wc -l) $f"; done
145d8c40abcb 209 harness-ports/bin/lane-profile.sh
02bc97314c56 152 harness-ports/tests/test_lane_profile.sh
6c45009c3486 78 harness-ports/tests/run-all.sh
daf605f480a0 351 scripts/verify_command.py
6af9a516adf5 490 tests/test_verify_command.py
$ ls harness-ports/bin/lane-done-gate.py harness-ports/tests/test_lane_done_gate.py tasks/briefs/canny/C2-report.md
ls: cannot access 'harness-ports/bin/lane-done-gate.py': No such file or directory
ls: cannot access 'harness-ports/tests/test_lane_done_gate.py': No such file or directory
ls: cannot access 'tasks/briefs/canny/C2-report.md': No such file or directory
$ bash harness-ports/tests/test_lane_profile.sh 2>/dev/null | tail -1
lane profile: 9 passed, 0 failed
$ sed -n '89,91p' scripts/verify_command.py; grep -n '^def is_verify' -A2 scripts/verify_command.py
VERIFY = [
    re.compile(
        r"\b(pytest|vitest|jest|mocha|ava|cypress|playwright test|go test"
178:def is_verify(
179-    command: str, patterns: Optional[List[str]] = None
180-) -> bool:
   (docstring: "*patterns* replaces the built-in VERIFY list when given (it does not add to it)"; len(VERIFY) = 3)

# Hermes lane runtime b3399c1 (~/.hermes/hermes-agent on the PC; upstream.lock.yaml lane_runtime), read-only excerpts:
agent/shell_hooks.py:3     Wire: stdin JSON {hook_event_name, tool_name, tool_input, session_id, cwd, extra}
agent/shell_hooks.py:84-91 "tool_name": kwargs.get("tool_name"), "tool_input": kwargs.get("args") if isinstance(kwargs.get("args"), dict) else None,
                           "session_id": kwargs.get("session_id") or kwargs.get("parent_session_id") or "", "cwd": cwd,
                           "extra": {k: v for k, v in kwargs.items() if k not in _TOP_LEVEL_PAYLOAD_KEYS}
agent/shell_hooks.py:50    _TOP_LEVEL_PAYLOAD_KEYS = {"tool_name", "args", "session_id", "parent_session_id"}
agent/shell_hooks.py:384   json.dumps({"hook_event_name": event, **_payload_fields(kwargs)}, ensure_ascii=False, default=str)
model_tools.py:632-636     invoke_hook("post_tool_call", tool_name=function_name, args=function_args, result=result, <task_id, session_id,
                           tool_call_id, turn_id, api_request_id>, duration_ms=..., status=..., error_type=..., error_message=...,
                           middleware_trace=[...])
tools/terminal_tool.py:1258/1263  "name": "terminal" … "command": {…}
tools/terminal_tool.py:787-789    the terminal result envelope: body = {"output": "", "exit_code": exit_code, "error": error}; a timeout
                                  gives exit_code=124 (:1090)
tools/file_tools.py:1043-1056     write_file: required ["path", "content"]
tools/file_tools.py:1079-1101     patch: required ["path", "old_string", "new_string"] (+ replace_all); the handler also accepts V4A
                                  {mode: "patch", patch: "<V4A text>"} from any model and advertises it to OpenAI-family mains (our cloud lanes)
hermes_cli/plugins.py:1883-1903   pre_verify kwargs: session_id, platform, model, coding, attempt, final_response, changed_paths (sorted list);
                                  a result {"decision": "block", "reason": msg} or {"action": "continue", "message": msg} continues the turn
agent/turn_stop_gates.py:49-75    pre_verify fires only when the turn's _turn_file_mutation_paths is non-empty, a pre_verify hook exists and
                                  attempt < max_verify_nudges() (agent.max_verify_nudges; unset in the lane profiles -> the default)
agent/shell_hooks.py:139-176      a hook runs only if allowlisted or accepted; harness-ports/bin/pc-lane.sh:463 passes --accept-hooks

# The lane clone's hooks today (read-only, aflanepcverifyt94md4a38190/config.yaml, 18:5xZ; identical in the source profile agentfactory):
hooks: on_session_start [hook-shim.sh session-start.sh]; pre_llm_call [hermes-hook-adapter.py wiki-context.py … --spool];
       post_tool_call [matcher "patch|write_file": … edit-snapshot.py post_tool_call --spool; matcher "search_files": … graft-first-nag.py …]
       (no pre_verify; hooks_auto_accept unset; agent.max_verify_nudges unset); its agent.log: 4 × "shell hook registered: …"

# C1 against the real corpus: every terminal command of two PC lanes (T94's and VERIFY-S198A's cloned profiles, read-only state.db):
aflanepct94mdfeb26d7 terminal calls: 69
aflanepcverifys198amd750699a terminal calls: 40
is_verify True: 0 of 109
- bash harness-ports/tests/test_pc_lane.sh
- bash harness-ports/tests/test_pc_lane.sh > ../scratch/t1-redfix.out 2>&1; rc=$?; tail -40 ../scratch/t1-redfix.out; echo rc=$rc
- set -o pipefail; bash harness-ports/tests/test_pc_lane.sh | tee ../scratch/t1-first.log; rc=${PIPESTATUS[0]}; printf 'T1_RC=%s\n' "$rc"; exit "$rc"
- set -o pipefail; bash harness-ports/tests/run-all.sh | tee ../scratch/run-all-final.log; rc=${PIPESTATUS[0]}; printf 'RUN_ALL_RC=%s\n' "$rc"; exit "$r…
- set -o pipefail; LANE_GATE_DIR="$(pwd)/../scratch/lane-gate-a" bash scripts/lane_gate.sh -r feb26d7 -f "harness-ports/bin/pc-lane.sh scripts/pc_lane.s…
- bash -n harness-ports/bin/pc-lane.sh scripts/pc_lane.sh harness-ports/tests/test_pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh && echo 'ba…
- python3 harness-ports/tests/test_hermes_session_export.py && python3 harness-ports/tests/test_qwen_matrix.py
- bash scripts/test_summary.sh tests/test_transcript_export.py harness-ports/tests/test_hermes_session_export.py
- timeout 180 /home/rocco/venv-agent-factory/bin/python -m pytest -vv -p no:cacheprovider -k test_value_head_check_stays_linear_on_a_long_run tests/test…
- mkdir -p ../scratch/bt && S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz /home…
- /home/rocco/venv-agent-factory/bin/python -m pyflakes scripts/transcript_export.py …; python3 scripts/ap_screen.py …; python3 scripts/report_lint.py …
  (the other 60-odd commands are reads: git status/log/diff, graft, lane_context.sh, why.sh, sha256sum, printf, python3 heredocs)
$ python3 -c '<is_verify probes, sandbox, this PIN>'
V pytest -q tests/test_x.py                           V python -m pytest -q tests/test_x.py
V python3 -m pytest -n 8 -q tests/test_x.py           V /home/rocco/venv-agent-factory/bin/python -m pytest -q tests/test_x.py
V timeout 180 python -m pytest -q tests/test_x.py     V S0_01_VENUE=pc python -m pytest -q tests/test_x.py
- bash harness-ports/tests/test_pc_lane.sh            - python3 harness-ports/tests/test_hermes_spool.py
- bash scripts/lane_gate.sh -r abc -f x -t y          - bash scripts/test_summary.sh tests/test_x.py
- bash -n harness-ports/bin/pc-lane.sh                - python -m pyflakes scripts/x.py
- set -o pipefail; bash harness-ports/tests/test_pc_lane.sh | tee ../scratch/t1.log; rc=${PIPESTATUS[0]}; exit "$rc"
V cargo test   V npm test   V make test   V ruff check .
```
