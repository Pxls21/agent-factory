# REPIN-a-R1 report — the ONE focused repair of VERIFY-REPIN-a (task #169)

STATUS: COMPLETE — R1-R5 built, 16 passed x2 on set bbc177a039e2, 28/28 brief-class mutants killed, 8 DISCREPANCIES (§6), NOT-done in §7.
LANE: repin-a-r1 (sandbox, `code-implementer`, shared tree, no worktree). PIN: 1978e55. Measured at: b511e4a (sandbox HEAD = origin).
Aliases (for `scripts/report_lint.py --map`): T = `tests/test_upstream_lock_lane_runtime.py`, L = `upstream.lock.yaml`,
H = `docs/HARNESS-PORTS.md`.

## 0. PREMISE — re-measured (2026-09-23 09:42Z, before any edit)

```
$ date -u; git rev-parse --short HEAD; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
Wed Sep 23 09:42:46 UTC 2026
b511e4a
b511e4a
$ git diff 1978e55 b511e4a -- tests/test_upstream_lock_lane_runtime.py upstream.lock.yaml docs/HARNESS-PORTS.md | wc -l
0
$ for f in <boundary>; do sha256 (first 16 hex) of the PIN blob, of the worktree file, lines; done
529261bd7488126f 529261bd7488126f   173 upstream.lock.yaml
b663bcd87b960cff b663bcd87b960cff   121 tests/test_upstream_lock_lane_runtime.py
3d90882e2d58fe43 3d90882e2d58fe43   743 docs/HARNESS-PORTS.md
$ grep -n "^  hermes-agent:$" upstream.lock.yaml; grep -c "^  hermes-agent:" upstream.lock.yaml
10:  hermes-agent:
1
$ sed -n "10,15p" upstream.lock.yaml | cat -A
  hermes-agent:$
    repository: https://github.com/NousResearch/hermes-agent.git$
    commit: 527da60844d4dced37879ea50259675371abe10e$
    observed_version: 0.21.0$
    license: MIT$
    role: main_production_workhorse_and_native_acp_server$
$ sed -n "173p" upstream.lock.yaml
    verified: "harness-ports/tests/run-all.sh (sandbox) + 43 PC-lane HOME/LANDED notes since 2026-09-08 14:2xZ"
$ grep -n "^## 12\. Lane runtime pin$" docs/HARNESS-PORTS.md; wc -l < docs/HARNESS-PORTS.md
728:## 12. Lane runtime pin
743
$ sed -n "1,4p" harness-ports/tests/run-all.sh
#!/usr/bin/env bash
# Run every harness-port test. Deterministic, LLM-free, no network, no harness
# binary required. Exit 0 only if all suites pass.
#
$ bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py --basetemp /tmp/rr1/bt   (PIN bytes, before any edit)
pytest-exit: 0
pytest-summary: 8 passed in 0.17s
$ bash scripts/pc_suite.sh set-id -- tests/test_upstream_lock_lane_runtime.py
1 files set=bbc177a039e2
```

PREMISE RESULT: HOLDS. The three boundary files are byte-identical to the PIN, with the same sha16 values as the
brief's premise. Origin moved 1978e55 → b511e4a without touching them. The six `selected_core.hermes-agent` lines
carry no trailing whitespace, and the floor is `8 passed` on set `bbc177a039e2`. Piece (a) of R3 rests on the suite's
own header: "no harness / `binary required`" (`harness-ports/tests/run-all.sh:2-3`), so the suite does not run Hermes.

Seams read before design (code intel first: the `scripts/lane_context.sh` pack at `/tmp/rr1/pack.md`, rc 0):
- `_load_lock` has 8 callers, all inside T (code-review-graph `callers_of`). GitNexus `impact` says UNKNOWN (no
  edges), so I confirmed by text search: nothing imports T (`git grep -n test_upstream_lock_lane_runtime -- ':!*.md'`
  is empty).
- The lock's live line reader refuses a 4-space line with no colon, `line.startswith("    ")` (`scripts/vendored_manifest.py:613`).
- It matches only `repository|commit|binary_sha256|asset_sha256` (`scripts/vendored_manifest.py:610`), so the new
  `verified:` value must stay ONE physical line.
- S0-12 reads L with `yaml.safe_load` (`proofs/S0-12/check_pin_diff.py:34`).
- The root L is NOT an attested input: `proofs/S0-12/result.json` hashes only its fixture copy
  `proofs/S0-12/fixtures/mutated-root/upstream.lock.yaml`, so a `verified:` edit cannot make a minted result INVALID.
- S0-08 cites L lines 10-15 by number beside `run_containment.sh` (`proofs/S0-08/check_containment.py:51`). The edit
  is on line 173 only, so no line moves.

## 1. Per contract line — what changed, where, and the tests that pin it

Diff shape (pasted, final, 10:00:13Z): `git diff --numstat` → H `2 0`, T `160 28`, L `1 1`. Final sha256 (first 16 hex):
L `df5bad5949ab61bb` (173 lines), T `013d7fd55610685c` (253 lines), H `66e71ccb36c886dd` (745 lines).
L changes on line 173 only; H gains two lines after line 736 and changes none; `parse_lock` returns the same 24
entries as at the PIN; the lane-runtime key set is the same eight keys (§5).

**R1 (F1, the golden is the entry's LINES).**
- T:25-32 `HERMES_AGENT_GOLDEN_LINES`: the six committed lines, copied from the premise's `cat -A` block.
- T:93-114 `_hermes_agent_entry`: splits the text on "\n" only (T:100 `text.split`), so a trailing space, a tab or a CR stays in its line.
- T:101 `line == "  hermes-agent:"`: exactly one such line; the message gives the count, the line numbers and the whitespace-only near misses.
- T:108-111 `selected_core:`: the nearest top-level key above that line must be `selected_core:`.
- T:112 `re.match`: the entry ends at the next line that starts with two spaces and a non-space, or with a top-level key.
- T:200-210 `test_hermes_agent_entry_lines_golden`: reads L's raw bytes (T:203 `read_bytes`) and compares the lines byte for byte.
- T:206 `assert entry == golden`: the failure message names the first differing entry line and its lock line.
- T:185-197 `test_hermes_agent_entry_unchanged`: kept as the second view (parsed dict); its docstring no longer claims byte identity.
- Killed: G1-G7 each red by name through `test_hermes_agent_entry_lines_golden`; G8 red on both views (§3).

**R2 (F2, a live negative control).**
- T:85-90 `_check_lane_runtime_commit`: the ONE helper that decides validity.
- T:88 `isinstance(commit, str)`: a non-string is refused before the pattern is tried.
- T:89 `commit is not 40 lowercase hex`: the exact `ValueError` text, with the value's repr.
- T:138-140 `test_lane_runtime_commit_is_40_hex`: the positive test calls the helper on L as committed.
- T:227-234 `BAD_COMMITS`: `b3399c1` (7 hex), 39 hex, 41 hex, 40 uppercase hex, and a YAML integer (40 decimal digits: its str() WOULD pass the pattern).
- T:237-253 `test_bad_lane_runtime_commit_rejected`: writes a copy of L with the one committed lane-commit line replaced.
- T:243-245 `text.count(committed_line)`: the line must occur exactly once before it is replaced.
- T:248 `_load_lock(copy)`: the copy goes through the SAME loader as the positive test.
- T:250 `== loaded`: de-vacuous: the copy carries the bad value with the type PyYAML gives it.
- T:252 `pytest.raises(ValueError, match=`: the exact anchored message; no copy of the check's regex in the control.
- Killed: T1 by [7-hex] and [39-hex]; T2 by all five cases; T3* (extra, str() coercion) by [yaml-integer] (§3).

**R3 (F3 + F4, `verified:` says what each piece proves).**
- L:173 `verified`: one double-quoted string on ONE physical line (`parse_lock` refuses a 4-space line with no colon).
- The three pieces appear in the brief's order, separated by "; ".
- T:50-60 `LANE_RUNTIME_VERIFIED`: the same three pieces.
- T:51 `(a) the harness adapters`: piece (a) proves the adapters on the PC's shell and Python; the suite runs no Hermes binary.
- T:54 `(b) the lane runtime's identity`: piece (b) is the identity probe.
- T:57 `(c) the lanes launched since the update`: piece (c) is the lane record.
- T:177-182 `test_lane_runtime_verified_value`: asserts the exact committed value.
- Every number is copied from the premise or the lane record: the context-anchored check in §4 reads `BAD: 0 of 16`.
- Wording deviation in piece (c): see DISCREPANCY D1.
- Killed: 15 mutants (one changed digit in each number of each piece), plus one extra (the record path), each red by name (§3).

**R4 (F7, every value pinned).**
- T:62-71 `LANE_RUNTIME_EXPECTED`: all eight keys' exact values.
- L:166-172 `diff_from_proof_pin`: the seven unchanged values are copied from these lines; `verified` comes from R3.
- T:166-174 `test_lane_runtime_entry_values`: dict equality; the message names every differing key.
- Killed: R4-python, R4-role, R4-reason and R4-diff, each red with `differs at <key>` (§3).

**R5 (F5, §12 says what is NOT enforced).**
- H:737-738 `HERMES_BIN`: the one sentence, as the last sentence of the "What this pin covers" paragraph (F5's overclaim site).
- H's diff is two added lines; no line changes.
- T:74-78 `SECTION_12_UNENFORCED`: the sentence, as the test expects it.
- T:213-222 `test_harness_ports_section_12_says_the_pin_is_unenforced`: exactly one `## 12. Lane runtime pin` line.
- It reads §12 from that heading to the next `## ` line or EOF, normalizes whitespace, and requires the sentence inside.
- Killed: H0 (the PIN H) red; H1* (extra: the sentence moved above the heading, into §11) red (§3).

## 2. RED on the PIN bytes, then GREEN (pasted)

RED in the tree: the new T, with L and H still at the PIN bytes (the sha check is in the same call). The only later
change to T (the control's precondition message after `text.count(committed_line)`, T:243-245) does not touch the three red tests. The driver's `RED-PIN`
row in §3 repeats this run with the FINAL T on the PIN's L and H: `3 failed, 13 passed`, the same three names.

```
Wed Sep 23 09:48:07 UTC 2026
$ L and H at the PIN bytes? (sha16 of the PIN blob vs the worktree file)
529261bd7488126f 529261bd7488126f upstream.lock.yaml
3d90882e2d58fe43 3d90882e2d58fe43 docs/HARNESS-PORTS.md
$ bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py --basetemp /tmp/rr1/bt   (final T; L, H = PIN bytes)
rc=1
________________________ test_lane_runtime_entry_values ________________________
E       AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got 'harness-ports/tests/run-all.sh (sandbox) + 43 PC-lane HOME/LANDED notes since 2026-09-08 14:2xZ', expected "har
_______________________ test_lane_runtime_verified_value _______________________
E       AssertionError: verified mismatch: got 'harness-ports/tests/run-all.sh (sandbox) + 43 PC-lane HOME/LANDED notes since 2026-09-08 14:2xZ', expected "harness-ports/tests/run-all.sh on the PC at
___________ test_harness_ports_section_12_says_the_pin_is_unenforced ___________
E       AssertionError: docs/HARNESS-PORTS.md §12 (lines 728-743) lacks the sentence 'Until REPIN-b lands, nothing reads `lane_runtime`, so a `hermes update` or a `HERMES_BIN` override moves the lane
pytest-exit: 1
pytest-summary: 3 failed, 13 passed in 0.23s
```

Note on the paste: its echo label "(final T; ...)" was typed at 09:48Z and is stale. T changed once more at 09:52:47Z
(the precondition message only). The `RED-PIN` row in §3, run at 09:52:57Z, is the run with the final T.

R1's and R2's tests are GREEN on the PIN bytes by construction: the PIN's L carries the six golden lines and a valid
lane commit. Their RED is on the PIN bytes MUTATED (G1-G7 on the PIN's lines 10-15, which this lane does not change;
T1, T2), and the before state is in §3: the PIN's T lets G1-G7, T1 and T2 through (rows `P-*`). See DISCREPANCY D2.

GREEN, the brief's gate on the final tree: twice, with `rm -rf /tmp/rr1/bt` between. The same call also ran S0-12, the
manifest and the ledger; all four are pasted in §5.

## 3. The mutation table (scratch copies only; `/tmp/rr1/mut.py`, pasted)

Method: each row builds `/tmp/rr1/m/<row>/` holding T, L, H, the inert `tests/conftest.py` and `pyproject.toml`, and
applies ONE mutation. Each mutation's anchor is asserted unique first. Each row runs `py_compile` (its cfile under
`/tmp/rr1/mbt`), then `--collect-only`, then the suite, then deletes the copy and its basetemp. The driver
ran at 09:52:57Z with the final T. AF-AP-138: the baselines ran first. `M0` (new T, edited L and H) is `16 passed`,
so every killer named below passes on the unmutated copy. `P0` (the PIN's T, L and H) is `8 passed`. AF-AP-78: every
row compiles and collects (16 for the new T; 8 for the PIN T, 6 for P-T2 which deletes two tests by design). Rows marked `*` go beyond
the brief. `pin` rows are the BEFORE state (the PIN's T), not mutants of this change.

| row | T | mutant | compiles | collected | result | failing tests (the first message, cut) |
|---|---|---|---|---|---|---|
| M0 | new | baseline: new T on the edited L and H, unmutated | yes | 16 | 16 passed | none |
| P0 | pin | baseline: PIN T on the PIN L and H, unmutated | yes | 8 | 8 passed | none |
| RED-PIN | new | the final T on the PIN L and the PIN H (R3, R4, R5 red) | yes | 16 | 3 failed, 13 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got 'harness-ports/tests/run-all.sh (sandbox) + 43 PC-lane HOME/LANDED not; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got 'harness-ports/tests/run-all.sh (sandbox) + 43 PC-lane HOME/LANDED notes since 2026-09-08 14:2xZ', expected "ha; `test_harness_ports_section_12_says_the_pin_is_unenforced` — AssertionError: docs/HARNESS-PORTS.md §12 (lines 728-743) lacks the sentence 'Until REPIN-b lands, nothing reads `lane_runtime`, so a `hermes update`  |
| G1 | new | one trailing space after `  hermes-agent:` | yes | 16 | 1 failed, 15 passed | `test_hermes_agent_entry_lines_golden` — AssertionError: upstream.lock.yaml has 0 lines equal to '  hermes-agent:' (at []); lines that differ from it only in whitespace: [10] |
| P-G1 | pin | one trailing space after `  hermes-agent:` (PIN T, the before state) | yes | 8 | 8 passed | none |
| G2 | new | a trailing space on each of the five value lines | yes | 16 | 1 failed, 15 passed | `test_hermes_agent_entry_lines_golden` — AssertionError: selected_core.hermes-agent differs from its golden at entry line 2 (upstream.lock.yaml line 11): expected '    repository: https://git |
| P-G2 | pin | a trailing space on each of the five value lines (PIN T, the before state) | yes | 8 | 8 passed | none |
| G3 | new | the five value lines re-indented 4 -> 6 | yes | 16 | 1 failed, 15 passed | `test_hermes_agent_entry_lines_golden` — AssertionError: selected_core.hermes-agent differs from its golden at entry line 2 (upstream.lock.yaml line 11): expected '    repository: https://git |
| P-G3 | pin | the five value lines re-indented 4 -> 6 (PIN T, the before state) | yes | 8 | 8 passed | none |
| G4 | new | the commit value quoted | yes | 16 | 1 failed, 15 passed | `test_hermes_agent_entry_lines_golden` — AssertionError: selected_core.hermes-agent differs from its golden at entry line 3 (upstream.lock.yaml line 12): expected '    commit: 527da60844d4dce |
| P-G4 | pin | the commit value quoted (PIN T, the before state) | yes | 8 | 8 passed | none |
| G5 | new | the five keys reordered (sorted by key) | yes | 16 | 1 failed, 15 passed | `test_hermes_agent_entry_lines_golden` — AssertionError: selected_core.hermes-agent differs from its golden at entry line 2 (upstream.lock.yaml line 11): expected '    repository: https://git |
| P-G5 | pin | the five keys reordered (sorted by key) (PIN T, the before state) | yes | 8 | 8 passed | none |
| G6 | new | a comment line inside the entry (lines 13-15 shift down) | yes | 16 | 1 failed, 15 passed | `test_hermes_agent_entry_lines_golden` — AssertionError: selected_core.hermes-agent differs from its golden at entry line 4 (upstream.lock.yaml line 13): expected '    observed_version: 0.21. |
| P-G6 | pin | a comment line inside the entry (lines 13-15 shift down) (PIN T, the before state) | yes | 8 | 8 passed | none |
| G7 | new | line 12 = the LANE sha; a second `commit: 527da60...` after `role:` | yes | 16 | 6 failed, 10 passed | `test_hermes_agent_entry_lines_golden` — AssertionError: selected_core.hermes-agent differs from its golden at entry line 3 (upstream.lock.yaml line 12): expected '    commit: 527da60844d4dce; `test_bad_lane_runtime_commit_rejected[7-hex]` — AssertionError: the lane-runtime commit line occurs 2 times, not once: '    commit: b3399c139624a0081d70397741a5b45f60fbe1f4\n'; `test_bad_lane_runtime_commit_rejected[39-hex]` — AssertionError: the lane-runtime commit line occurs 2 times, not once: '    commit: b3399c139624a0081d70397741a5b45f60fbe1f4\n'; `test_bad_lane_runtime_commit_rejected[41-hex]` — AssertionError: the lane-runtime commit line occurs 2 times, not once: '    commit: b3399c139624a0081d70397741a5b45f60fbe1f4\n'; `test_bad_lane_runtime_commit_rejected[40-uppercase-hex]` — AssertionError: the lane-runtime commit line occurs 2 times, not once: '    commit: b3399c139624a0081d70397741a5b45f60fbe1f4\n'; `test_bad_lane_runtime_commit_rejected[yaml-integer]` — AssertionError: the lane-runtime commit line occurs 2 times, not once: '    commit: b3399c139624a0081d70397741a5b45f60fbe1f4\n' |
| P-G7 | pin | line 12 = the LANE sha; a second `commit: 527da60...` after `role:` (PIN T, the before state) | yes | 8 | 8 passed | none |
| G8 | new | control: `observed_version: 0.21.1` | yes | 16 | 2 failed, 14 passed | `test_hermes_agent_entry_unchanged` — AssertionError: hermes-agent entry differs from golden: {'repository': 'https://github.com/NousResearch/hermes-agent.git', 'commit': '527da60844d4dced; `test_hermes_agent_entry_lines_golden` — AssertionError: selected_core.hermes-agent differs from its golden at entry line 4 (upstream.lock.yaml line 13): expected '    observed_version: 0.21. |
| P-G8 | pin | control: `observed_version: 0.21.1` (PIN T, the before state) | yes | 8 | 1 failed, 7 passed | `test_hermes_agent_entry_unchanged` — AssertionError: hermes-agent entry differs from golden: {'repository': 'https://github.com/NousResearch/hermes-agent.git', 'commit': '527da60844d4dced |
| G9* | new | extra: a CR at the end of `  hermes-agent:` (CRLF) | yes | 16 | 1 failed, 15 passed | `test_hermes_agent_entry_lines_golden` — AssertionError: upstream.lock.yaml has 0 lines equal to '  hermes-agent:' (at []); lines that differ from it only in whitespace: [10] |
| P-G9* | pin | extra: a CR at the end of `  hermes-agent:` (CRLF) (PIN T, the before state) | yes | 8 | 8 passed | none |
| G10* | new | extra: a top-level key `other_section:` inserted above the entry | yes | 16 | 2 failed, 14 passed | `test_hermes_agent_entry_unchanged` — AssertionError: hermes-agent entry missing from selected_core; `test_hermes_agent_entry_lines_golden` — AssertionError: '  hermes-agent:' (line 11) is not under 'selected_core:' but under 'other_section:' |
| P-G10* | pin | extra: a top-level key `other_section:` inserted above the entry (PIN T, the before state) | yes | 8 | 1 failed, 7 passed | `test_hermes_agent_entry_unchanged` — AssertionError: hermes-agent entry missing from selected_core |
| G11* | new | extra: a second `  hermes-agent:` block appended (under lane_runtime) | yes | 16 | 1 failed, 15 passed | `test_hermes_agent_entry_lines_golden` — AssertionError: upstream.lock.yaml has 2 lines equal to '  hermes-agent:' (at [10, 174]); lines that differ from it only in whitespace: [] |
| P-G11* | pin | extra: a second `  hermes-agent:` block appended (under lane_runtime) (PIN T, the before state) | yes | 8 | 8 passed | none |
| T1 | new | the helper's pattern weakened {40} -> {7,40} | yes | 16 | 2 failed, 14 passed | `test_bad_lane_runtime_commit_rejected[7-hex]` — Failed: DID NOT RAISE ValueError; `test_bad_lane_runtime_commit_rejected[39-hex]` — Failed: DID NOT RAISE ValueError |
| T2 | new | the helper's check removed (the `if ...: raise` deleted) | yes | 16 | 5 failed, 11 passed | `test_bad_lane_runtime_commit_rejected[7-hex]` — Failed: DID NOT RAISE ValueError; `test_bad_lane_runtime_commit_rejected[39-hex]` — Failed: DID NOT RAISE ValueError; `test_bad_lane_runtime_commit_rejected[41-hex]` — Failed: DID NOT RAISE ValueError; `test_bad_lane_runtime_commit_rejected[40-uppercase-hex]` — Failed: DID NOT RAISE ValueError; `test_bad_lane_runtime_commit_rejected[yaml-integer]` — Failed: DID NOT RAISE ValueError |
| T3* | new | extra: the isinstance check replaced by str() coercion | yes | 16 | 1 failed, 15 passed | `test_bad_lane_runtime_commit_rejected[yaml-integer]` — Failed: DID NOT RAISE ValueError |
| P-T1 | pin | VERIFY's T1 on the PIN T: its positive regex {40} -> {7,40}; real PIN L | yes | 8 | 8 passed | none |
| P-T2 | pin | VERIFY's T2 on the PIN T: both commit tests deleted; L carries a 7-hex commit | yes | 6 | 6 passed | none |
| K6* | new | extra: new T on an L whose lane commit is 7 hex | yes | 16 | 8 failed, 8 passed | `test_lane_runtime_commit_is_40_hex` — ValueError: commit is not 40 lowercase hex: 'b3399c1'; `test_lane_runtime_commit_value` — AssertionError: commit mismatch: got 'b3399c1', expected 'b3399c139624a0081d70397741a5b45f60fbe1f4'; `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at commit: got 'b3399c1', expected 'b3399c139624a0081d70397741a5b45f60fbe1f4'; `test_bad_lane_runtime_commit_rejected[7-hex]` — AssertionError: the lane-runtime commit line occurs 0 times, not once: '    commit: b3399c139624a0081d70397741a5b45f60fbe1f4\n'; `test_bad_lane_runtime_commit_rejected[39-hex]` — AssertionError: the lane-runtime commit line occurs 0 times, not once: '    commit: b3399c139624a0081d70397741a5b45f60fbe1f4\n'; `test_bad_lane_runtime_commit_rejected[41-hex]` — AssertionError: the lane-runtime commit line occurs 0 times, not once: '    commit: b3399c139624a0081d70397741a5b45f60fbe1f4\n'; `test_bad_lane_runtime_commit_rejected[40-uppercase-hex]` — AssertionError: the lane-runtime commit line occurs 0 times, not once: '    commit: b3399c139624a0081d70397741a5b45f60fbe1f4\n'; `test_bad_lane_runtime_commit_rejected[yaml-integer]` — AssertionError: the lane-runtime commit line occurs 0 times, not once: '    commit: b3399c139624a0081d70397741a5b45f60fbe1f4\n' |
| R4-python | new | python 3.11.15 -> 3.13.11 (the proof runtime's) | yes | 16 | 1 failed, 15 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at python: got '3.13.11', expected '3.11.15' |
| R4-role | new | role: `NOT the S0-01 proof runtime` -> `the S0-01 proof runtime` | yes | 16 | 1 failed, 15 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at role: got 'lane-runtime (scripts/pc_lane.sh -> hermes on the PC); the S0-01 proof ru |
| R4-reason | new | reason: SQLite >= 3.51.3 -> >= 3.51.2 | yes | 16 | 1 failed, 15 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at reason: got 'SQLite >= 3.51.2 for WAL on the shared profile state.db (VERIFY-B5j); o |
| R4-diff | new | diff_from_proof_pin: 31816 -> 31817 commits | yes | 16 | 1 failed, 15 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at diff_from_proof_pin: got '31817 commits, 3939 files', expected '31816 commits, 3939  |
| R3a-1 | new | (a) 2ebd486 -> 2ebd487 | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd487, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd487, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3a-2 | new | (a) Python 3.13.11 -> 3.13.12 | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.12: a |
| R3a-3 | new | (a) rc 0 -> rc 1 | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3a-4 | new | (a) 2026-09-23 09:08Z -> 2026-09-24 09:08Z | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3a-5 | new | (a) 09:08Z -> 09:09Z | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3b-1 | new | (b) 2026-09-23 08:58Z -> 2026-09-24 08:58Z | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3b-2 | new | (b) 08:58Z -> 08:59Z | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3b-3 | new | (b) b3399c1 -> b3399c2 | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3b-4 | new | (b) v0.21.1 -> v0.21.2 | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3b-5 | new | (b) Python 3.11.15 -> 3.11.16 | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3b-6 | new | (b) SQLite 3.53.1 -> 3.53.2 | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3c-1 | new | (c) 110 -> 111 lanes | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3c-2 | new | (c) 2026-09-08 -> 2026-09-09 | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3c-3 | new | (c) 14:22:00Z -> 14:22:01Z | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3c-4 | new | (c) 98 -> 97 with a report | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| R3c-5* | new | extra: (c) the record path R1 -> R2 | yes | 16 | 2 failed, 14 passed | `test_lane_runtime_entry_values` — AssertionError: lane_runtime.hermes-agent-lane-runtime differs at verified: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone w; `test_lane_runtime_verified_value` — AssertionError: verified mismatch: got "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: a |
| H1* | new | extra: the §12 sentence moved above the §12 heading (into §11) | yes | 16 | 1 failed, 15 passed | `test_harness_ports_section_12_says_the_pin_is_unenforced` — AssertionError: docs/HARNESS-PORTS.md §12 (lines 731-746) lacks the sentence 'Until REPIN-b lands, nothing reads `lane_runtime`, so a `hermes update`  |
| H0 | new | the PIN H (the sentence absent) | yes | 16 | 1 failed, 15 passed | `test_harness_ports_section_12_says_the_pin_is_unenforced` — AssertionError: docs/HARNESS-PORTS.md §12 (lines 728-743) lacks the sentence 'Until REPIN-b lands, nothing reads `lane_runtime`, so a `hermes update`  |

Tally (the brief's classes, new T): G1-G7 7/7 killed · T1, T2 2/2 killed · R4 value mutants 4/4 killed · R3, one
changed digit per number of each piece, 15/15 killed. That is 28 killed, 0 SURVIVED, 0 EQUIVALENT. G8 (the control)
stays red: 2 failed on the new T, 1 on the PIN T. Extras (G9*, G10*, G11*, T3*, K6*, R3c-5*, H1*): 7/7 red. Before
state (PIN T): P-G1 to P-G7, P-G9*, P-G11*, P-T1 and P-T2 all pass. These are VERIFY-REPIN-a's G1-G7, T1 and T2,
reproduced. P-G8 and P-G10* are red only through the dict view.

Row notes:
- G7 also reds the five control cases. The cause is the control's precondition, not the helper: the mutation writes
  the LANE sha into line 12, so the committed lane-commit line occurs twice and the anchored replace would be
  ambiguous. The message reads `the lane-runtime commit line occurs 2 times, not once` (fail-closed).
- K6* shows the same precondition at 0 occurrences. It also shows the positive test naming the defect:
  `ValueError: commit is not 40 lowercase hex: 'b3399c1'`.

## 4. Every number in `verified:` is copied (context-anchored, pasted)

Each fragment of the committed value must occur in the value AND match its measured source line by regex (a
substring check proved too weak here: `110` also hit the brief's `cut -c1-110` on premise line 82).

```
OK  'at 2ebd486'                           in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-brief.md:[147]
OK  'Python 3.13.11'                       in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-brief.md:[148]
OK  'all suites passed'                    in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-brief.md:[149]
OK  'rc 0'                                 in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-brief.md:[150]
OK  '2026-09-23 09:08Z'                    in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-brief.md:[151]
OK  'identity probe 2026-09-23 08:58Z'     in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-brief.md:[168]
OK  'b3399c1'                              in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-brief.md:[154]
OK  'Hermes Agent v0.21.1'                 in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-brief.md:[159]
OK  'venv Python 3.11.15, SQLite 3.53.1'   in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-brief.md:[163]
OK  'shared state.db WAL'                  in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-brief.md:[165]
OK  '110 PC lanes'                         in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md:[12]
OK  '110 PC lanes'                         in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-brief.md:[170]
OK  'at or after 2026-09-08 14:22:00Z'     in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md:[8, 9]
OK  'at or after 2026-09-08 14:22:00Z'     in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md:[19]
OK  '(98 with a report)'                   in value=True  tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md:[12]
OK  '(binary-free by its header)'          in value=True  harness-ports/tests/run-all.sh:[2, 3]
BAD: 0 of 16
```

## 5. Gates (every command with its output, pasted)

```
Wed Sep 23 09:54:15 UTC 2026
$ mkdir -p /tmp/rr1/bt && bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py --basetemp /tmp/rr1/bt   (run 1)
rc=0
pytest-exit: 0
pytest-summary: 16 passed in 0.19s
$ rm -rf /tmp/rr1/bt
$ mkdir -p /tmp/rr1/bt && bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py --basetemp /tmp/rr1/bt   (run 2)
rc=0
pytest-exit: 0
pytest-summary: 16 passed in 0.20s
$ rm -rf /tmp/rr1/bt
$ bash scripts/pc_suite.sh set-id -- tests/test_upstream_lock_lane_runtime.py
1 files set=bbc177a039e2
$ mkdir -p /tmp/rr1/bt && bash scripts/test_summary.sh tests/test_s0_12_license_sbom.py --basetemp /tmp/rr1/bt
rc=0
pytest-exit: 0
pytest-summary: 5 passed in 0.24s
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_12_license_sbom.py
1 files set=4c820c35fdc9
$ python3 scripts/vendored_manifest.py --check
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
rc=0
$ python3 scripts/validate-ledger integrity --root .  (whole output)
rc=0
S0-01 PRESENT
S0-02 ABSENT
S0-03 PRESENT
S0-04 PRESENT
S0-05 ABSENT
S0-06 PRESENT
S0-07 PRESENT
S0-08 PRESENT
S0-09 PRESENT
S0-10 PRESENT
S0-11 PRESENT
S0-12 PRESENT
blocked_credential numerator=0 denominator=1
blocked_host numerator=0 denominator=1
conformance_checked_decision numerator=3 denominator=3
execution_proof numerator=7 denominator=9
INVALID lines: 0
Wed Sep 23 09:54:26 UTC 2026
$ bash scripts/verify-planning-repo.sh
rc=0
planning repository verification passed
$ /root/venv-agent-factory/bin/python -m pyflakes tests/test_upstream_lock_lane_runtime.py
rc=0
$ python3 scripts/ap_screen.py --tests tests/test_upstream_lock_lane_runtime.py   (the edited T)
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---
rc=0
$ python3 scripts/ap_screen.py --tests /tmp/rr1/pinT/tests/test_upstream_lock_lane_runtime.py   (the PIN T, for the delta)
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---
rc=0
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 39 files scanned, clean
rc=0
```

Extra, beyond the brief's list (Phase 6: adjacent readers of L). Pasted:
```
$ python3 -m pytest tests/test_s0_06_four_scope.py -q -p no:cacheprovider --basetemp /tmp/rr1/bt -k "upstream_lock or ai_memory_blocks or substrate_pin or pinned"
4 passed, 219 deselected in 0.50s
rc=0
$ git diff -U0 -- upstream.lock.yaml | grep "^[-+@]" | cut -c1-120   (and H, and the parse checks)
@@ -173 +173 @@ lane_runtime:
-    verified: "harness-ports/tests/run-all.sh (sandbox) + 43 PC-lane HOME/LANDED notes since 2026-09-08 14:2xZ"
+    verified: "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13
@@ -736,0 +737,2 @@ commit.
+Until REPIN-b lands, nothing reads `lane_runtime`, so a `hermes update` or a `HERMES_BIN`
+override moves the lanes with no check failing.
$ git diff --check -- upstream.lock.yaml docs/HARNESS-PORTS.md tests/test_upstream_lock_lane_runtime.py
rc=0
lane_runtime keys: ['commit', 'diff_from_proof_pin', 'python', 'reason', 'role', 'sqlite', 'verified', 'version']
top-level keys equal to PIN: True
lane-runtime keys whose value changed: ['verified']
every other section equal to PIN: True
parse_lock(now) == parse_lock(PIN): True entries: 24
```

Disk: `/dev/vda … 1.6G` available before and after the runs; `/tmp/rr1/m` and `/tmp/rr1/mbt` are gone; every
basetemp was removed after its run.

## 6. DISCREPANCIES (each flagged; none resolved by an edit outside the boundary)

- **D1: wording of R3 piece (c). DEVIATION, deliberate.**
  - The brief's words: "110 PC lanes first launched after 2026-09-08 14:22Z".
  - Committed: "110 PC lanes first launched at or after 2026-09-08 14:22:00Z".
  - Reason: the lane record counts a lane "at or after 2026-09-08T14:22:00Z" (its script tests `-ge "$CUT"`). The
    first counted lane launched at 14:22:32Z, inside the minute "14:22Z". Read as "after the minute 14:22", the
    brief's words would exclude that lane and make the 110 false (109).
  - The words and the time are copied from the lane record (§4), not typed.
  - To take the brief's literal words, change T:58 `at or after` and L:173 `verified` together; the R3 and R4 tests
    hold them equal.
- **D2: "Every contract line has a test that is RED on the PIN bytes" holds literally for R3, R4 and R5 only.**
  - R1's golden IS the PIN's six lines, and R2's positive test reads the PIN's valid commit. Both are green there by
    construction; making them red on the unmutated PIN bytes would make them wrong.
  - Their RED is shown on mutated PIN bytes (G1-G7 applied to the PIN's L; T1, T2), with the PIN T's before state
    beside it (§3).
- **D3: the S0-12 gate ran with `--basetemp /tmp/rr1/bt`.** The brief's literal command has none; its hard rule puts
  every basetemp under `/tmp/rr1/`.
- **D4: the control was renamed.** The old name is `test_short_commit_rejected`, one case; the new name is
  `test_bad_lane_runtime_commit_rejected`, five cases. The brief's pack command names the old symbol, which existed
  at the PIN. The count moved from `8 passed` to `16 passed` on the SAME set id `bbc177a039e2` (the id hashes the
  path list, not the content).
- **D5: the positive test has no `assert` statement (T:140 `_check_lane_runtime_commit`).** It relies on the ONE
  helper's raise, by R2's design; K6* shows it red by name.
- **D6: three old per-field tests are kept.** `test_lane_runtime_commit_value`, `test_lane_runtime_version` and
  `test_lane_runtime_sqlite` are subsumed by R4's whole-dict test but still correct, so they stay unchanged
  (surgical). A future value change must update both places.
- **D7: G7's and K6*'s extra reds come from the control's precondition, not the helper.** This is fail-closed (§3,
  row notes).
- **D8, outside the boundary.** The ledger note at `todo/BUILD-TASKLIST.md:156` (`REPIN-a LANDED`) still repeats the
  old count ("43 PC-lane HOME/LANDED notes"). It is the coordinator's to amend; this lane did not touch it.

## 7. NOT-done (first-class)

- F6: duplicate `lane_runtime:` blocks stay invisible to PyYAML-based tests (VERIFY K7). It is REPIN-b's, by the brief.
- F8 (the SQLite 3.47.2 wording in the REPIN brief and D-048) and F10 (typed numbers in `REPIN-a-report.md`) belong
  to issue #36, by the brief.
- F9 and F11 are the coordinator's, already handled per the ledger note "F4 DECIDED; D-048's PC COMPATIBILITY RUN
  DONE" (F11 is task #170).
- The pin is still UNENFORCED: nothing reads `lane_runtime` until REPIN-b. H §12 now says so; no code enforces it.
- No line-number pin for L lines 10-15. S0-08 cites those lines, and VERIFY F1 marks the pin "optional"; R1's
  contract does not require it. A new `selected_core` entry inserted above `hermes-agent` moves them with no test red.
- No PC re-measurement (no bridge, by the brief). Every PC value is copied from the brief's premise or the lane
  record, and inherits the lane record's stated limit: no lane records its Hermes sha, so a `HERMES_BIN` override
  would be counted.
- No commit, push, ledger, wiki, task-DB or registry edit (all outside the boundary; the coordinator commits).
- No `/bug-echo` report file and no registry row for the F1/F2 classes: both would be files outside the boundary.
  The read-only sweep result is in §8.

## 8. Self-attack — the three likeliest ways this change is wrong, and how each was ruled out

1. The line golden could pass a changed entry, if the extraction stopped early or normalized the bytes.
   - Ruled out: G1-G7 and the extras G9* (a CR), G10* (another parent key) and G11* (a second header) are each red
     by name.
   - The read is `read_bytes().decode()` split on "\n" only; M0 is green.
2. The negative control could be green for a reason other than the helper (vacuous).
   - Ruled out: the copy's value and YAML type are asserted before the check, and the message match is anchored and
     exact.
   - T1, T2 and T3* are each red. P-T1 and P-T2 show that the PIN control's blindness is gone.
3. The new `verified:` could carry a typed number, or break a reader of L.
   - Ruled out: the 16 context-anchored checks read OK. `parse_lock` returns the PIN's 24 entries unchanged.
   - The manifest check PASSes, S0-12 is `5 passed` and S0-06's lock tests are `4 passed`. Only L line 173 changed,
     and the key set is unchanged.
   - R4's seven literal values equal the committed bytes: GREEN, with each value mutant red.

Read-only echo sweep for the fixed classes. It is not the `/bug-echo` skill (that would write outside the boundary).
A zero means "none found", never "none exists":
- F1 class (a byte-identity claim checked by a weaker view): one UNSURE candidate.
  - `tests/test_s0_01_pc_tools.py:1106` `PINNED_ENV_KEYS`: the docstring says the default env is "byte-identical" to
    the pre-extension launcher.
  - The asserts check the key set and two absences; they do not compare the s0-01 values with the old launcher's
    values. The docstring defines its own meaning, hence UNSURE.
  - Every other "byte-identical" hit in `tests/` and `harness-ports/tests/` compares bytes or files.
- F2 class (a control asserting NOT on a value it set itself, with its own regex copy): no sibling found by the
  signature `assert not re.(fullmatch|match|search)(`. Its 8 hits all scan real content (source text, a config blob,
  a doc), not a self-set constant.

## 9. Lint

```
$ python3 scripts/report_lint.py --min-refs 10 --map T=tests/test_upstream_lock_lane_runtime.py --map L=upstream.lock.yaml --map H=docs/HARNESS-PORTS.md tasks/briefs/hermes-repin/REPIN-a-R1-report.md --root .   (round 1)
report_lint: 43 refs — OK 42, NEAR 0, MISS 1, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
rc=1
$ (round 1 fix: the one MISS, report line 125, carried only the token RED-PIN for the control's precondition lines; the fix hint's backticked identifier from the cited line was added)
$ python3 scripts/report_lint.py --min-refs 10 --map T=tests/test_upstream_lock_lane_runtime.py --map L=upstream.lock.yaml --map H=docs/HARNESS-PORTS.md tasks/briefs/hermes-repin/REPIN-a-R1-report.md --root .   (round 2)
report_lint: 43 refs — OK 43, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
rc=0
```

Freeze check before closing (pasted; the boundary files are the ones the 09:54Z gates ran on: T last written 09:52:47,
L 09:48:24, H 09:48:31):
```
Wed Sep 23 10:00:13 UTC 2026
$ git diff --numstat -- upstream.lock.yaml docs/HARNESS-PORTS.md tests/test_upstream_lock_lane_runtime.py
2	0	docs/HARNESS-PORTS.md
160	28	tests/test_upstream_lock_lane_runtime.py
1	1	upstream.lock.yaml
$ sha256 (first 16 hex) of the final boundary files
df5bad5949ab61bb   173 upstream.lock.yaml
013d7fd55610685c   253 tests/test_upstream_lock_lane_runtime.py
66e71ccb36c886dd   745 docs/HARNESS-PORTS.md
09:48:31 docs/HARNESS-PORTS.md
09:52:47 tests/test_upstream_lock_lane_runtime.py
09:48:24 upstream.lock.yaml
$ mkdir -p /tmp/rr1/bt && bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py --basetemp /tmp/rr1/bt   (freeze check)
pytest-exit: 0
pytest-summary: 16 passed in 0.19s
```

STATUS: COMPLETE (2026-09-23 10:0xZ). Nothing committed or pushed; the coordinator commits T, L, H and this report.
