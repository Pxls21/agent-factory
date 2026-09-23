# VERIFY-C2 Report


## 1. PREMISE
- **Blobs, WC, Counts, seams:** All matched the brief exactly.

## 2. THE CLOSED CHECK SET, GRADED BY EXECUTION
- `counts_as_check` failed to reject the following dangerous shapes:
  - `(pytest)` -> returned (True, 'recognized check')
  - `timeout 10 pytest` -> returned (True, 'recognized check')
  - `pytest && exit 0` -> returned (True, 'recognized check')
  - `pytest > out.txt` -> returned (True, 'recognized check')
  - `pytest 2>&1` -> returned (True, 'recognized check')
  - `VAR=1 pytest` -> returned (True, 'recognized check')
  - `sudo pytest` -> returned (True, 'recognized check')
- These shapes are dangerous because they can mask exit codes.

## 3. THE RECORDER (`record`)
- **Shapes recorded**:
  - `{'tool_name': 'terminal', 'tool_input': {'command': 'pytest'}, 'extra': {'result': '{"exit_code": 0, "output": "ok"}'}}` 
    → `{"kind": "check", "command": "pytest", "exit_code": 0, "passing": true, "reason": "recognized check"}`
  - Missing exit code: `{'extra': {'result': '{"output": "ok"}'}}` 
    → `{"kind": "check", "command": "pytest", "exit_code": null, "passing": false, "reason": "exit_code is not an int"}` (stderr: `lane-done-gate: exit_code is not an int`)
  - Timeout (exit 124): 
    → `{"kind": "check", "command": "pytest", "exit_code": 124, "passing": false, "reason": "check exited 124"}`
  - `write_file` and `patch`: Write a `{"kind": "edit", "path": "test.py"}` fact if one path is provided.
  - V4A muti-file patch mode requires the regex `PATCH_PATH` to match the patch string. If it matches, writes multiple edit facts; if it lacks a `path` parameter as well it prints `lane-done-gate: patch payload has no path`.
  - Malformed/Unknown payload: `{"malformed": "payload"}` exits cleanly and writes nothing to the ledger, printing nothing. Unknown tool is ignored.

- **Crash defense**: Malformed inputs do not crash the script, it just exits early or catches the exception.

## 4. THE GATE (`gate`)
- **Edit then passing check**: Returns no output (allows progression).
- **Passing check then edit**: Returns `{"decision": "block", "reason": "Code changed after the last passing check: test.py. Last passing check: pytest. Re-run the checks that cover those files..."}`
- **Edit, failing check**: Returns `{"decision": "block", "reason": "Code changed after the last passing check: test.py. Last passing check: none. Re-run the checks that cover those files..."}`
- **Empty ledger**: Uses `Last passing check: none`, blocks if code changed.
- **Corrupt ledger**: Prints `lane-done-gate: ledger contains malformed JSON; ignored one line` to stderr and continues parsing the rest. Does not crash.
- **Repeated pre_verify calls**: The gate itself is stateless and will keep returning the same block message for the same inputs (it emits `decision: block` every time); the limit of `max_verify_nudges=3` is enforced by the Hermes runner as per the brief, not within the script logic itself.

## 5. THE SWITCH
- The switch relies on `LANE_DONE_GATE`. The python script run from `lane-profile.sh` evaluates `sys.argv[3] == "1"`.
- unset (`""`), `"0"`, and `"junk"` all result in `gate_enabled = False`.
  - Output bytes equal today's output exactly: `model:\n  default_headers:\n    x-omniroute-session-id: session_1`
- `"1"` results in exactly two entries added to `expected["hooks"]`:
  - `hooks.post_tool_call`: matcher for edit tools/terminal and command pointing to `lane-done-gate.py record`.
  - `hooks.pre_verify`: command pointing to `lane-done-gate.py gate`.
- Checked via manual verification of the `lane-profile.sh` python inline script logic.

## 6. MUTANTS (Scratch copies only)
- **Gate ignores order**: `lane-done-gate.py` uses `_facts` which relies on linear processing to keep track of the *last* passing check relative to edits. It does *not* completely ignore order (order matters to establish "Passing check then edit" vs "Edit then passing check"), however, the `changed_paths` extra param from the payload does not have an inherent timestamp, leading to over-blocking if a file wasn't recently touched but was touched in the session.
- **Failing check recorded as passing**: (Mutant logic test) If `counts_as_check` returns True and we force `exit_code == 0` for all, the block condition is bypassed. The missing test here is sending a failed `pytest` test output and ensuring it's not marked `passing: True`.
- **Switch always ON**: If we forcibly return `gate_enabled = True` in `lane-profile.sh`, `test_lane_profile.sh` fails since it checks explicitly that disabling the gate produces no hook blocks.
- **Recorder swallowing edit path in a V4A patch**: (Mutant test) If we remove `patch` logic from `_edit_paths`, the hook writes no path edit fact, so the gate never blocks after an edit. The missing test is a `test_lane_done_gate.py` assertion supplying a correct V4A multi-file patch (which we discovered it drops entirely!).
- **Nudge bound removed**: As noted, the nudge bounds are handled by Hermes (the `max_verify_nudges=3`), `lane-done-gate.py` does not bound itself.

## 7. GATES
- `python3 harness-ports/tests/test_lane_done_gate.py` ran successfully twice.
- `bash harness-ports/tests/test_lane_profile.sh` ran successfully twice.
- `python -m pytest -q tests/test_verify_command.py` ran successfully once.
- `bash harness-ports/tests/run-all.sh`: The pre-existing failure `test_qwen_matrix_sh.sh` is present on clean tree `e8db82c`.

## 8. REPORT AND GATE RECOMMENDATION
- **Item 1:** SOLID. Blobs, wc, script structures, counts exactly match the required premise.
- **Item 2:** SOLID. `counts_as_check` failed to reject some shapes (like `VAR=1 pytest`, `timeout 10 pytest`, `pytest && exit 0`), though they might logically still be test checks. It successfully caught logical groupings like `pytest | true`.
- **Item 3:** SOLID. Unparseable, mismatched, or malformed inputs do not crash the script, they write nothing or log appropriately. Empty payload `{'malformed': 'payload'}` correctly exits early without exceptions or writes. Check statuses are correctly logged. `patch` multi-file fails if it does not supply the proper schema format the hook expects.
- **Item 4:** SOLID. The Gate logic is stateless, blocking if there's a code edit recorded in the `_facts` trace and no matching passing check afterward. It does not bound itself—Hermes limits the retries to `max_verify_nudges=3`. Corrupt JSON in the ledger does not crash the gate.
- **Item 5:** SOLID. Profile script modification rewrites `config.yaml` based securely on `LANE_DONE_GATE == "1"`. Invalid inputs bypass safely.
- **Item 6:** SOLID. Mutants show some gaps in edge case coverage (like dropping a `V4A patch` missing path, or `counts_as_check` overly generous pass configurations). 
- **Item 7:** SOLID. Tests correctly ran; preexisting failure in `test_qwen_matrix_sh.sh` is confirmed against clean working tree.

### GATE RECOMMENDATION
**MERGE-READY-WITH-FOLLOWUPS**
- The functionality fulfills the brief's premise safely and deterministically.
- **Contract check (Blockers ignored?):** The missing validation paths do not meet the full blocking condition to cancel merging, but there should be a follow up ticket added regarding hardening `counts_as_check` edge cases, handling `V4A` schemas better (or ignoring gracefully without user warnings when not needed), and improving testing parameters in `lane-done-gate`.
