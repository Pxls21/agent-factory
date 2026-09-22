# J1-0-R1 report -- B1 + B2 repair of `scripts/no_laya_in_gates.py`

PIN: 3bd4fbb. Script sha256[:16] at PIN: `5b5f6bbdb82c5a32`. Test sha256[:16] at PIN: `ec18351df3e077ae`.

## Files:lines changed

| File | Lines (PIN -> fixed) | Nature |
|---|---|---|
| `scripts/no_laya_in_gates.py` | 248 -> 296 (+48) | see hunk inventory below |
| `tests/test_no_laya_in_gates.py` | 188 -> 346 (+158) | 5 new tests + 2 helpers |

### Hunk inventory (`scripts/no_laya_in_gates.py`)

1. `scripts/no_laya_in_gates.py:120` -- `_parse_allowlist` extracted from `_load_allowlist` (text-based, no file path); `scripts/no_laya_in_gates.py:131` -- `_load_allowlist` now delegates to `_parse_allowlist`.
2. `scripts/no_laya_in_gates.py:162` -- `_glob_structural_staged()` added: enumerates `git ls-files --cached` with the three structural pathspecs instead of walking the worktree.
3. `scripts/no_laya_in_gates.py:182` -- `_exists_staged(path)` added: wraps `git cat-file -e :<path>`.
4. `scripts/no_laya_in_gates.py:217` -- `# Determine allowlist path and load entries`: `--list` explicit path (`:218-223`), `--staged` reads from index via `_read_staged` at `:225`, else worktree (`:230-235`). B2 fix.
5. `scripts/no_laya_in_gates.py:245` -- `if args.staged:` dispatches to `_glob_structural_staged()`, else `_glob_structural(root)`.
6. `scripts/no_laya_in_gates.py:254` -- `# Check listed paths exist` comment; the loop at `:255` runs in BOTH modes: `_exists_staged(entry)` at `:257`, `fp.exists()` at `:261`. B1 fix: the `if not args.staged:` guard is removed.
7. `scripts/no_laya_in_gates.py:278` -- `if content is None:` now prints `gate-file-unreadable: <path>` to stderr and returns 4 (`:279-280`), replacing the silent `continue`. Defense-in-depth.

### Hunk inventory (`tests/test_no_laya_in_gates.py`)

- `tests/test_no_laya_in_gates.py:192` -- `def _git_env():` helper.
- `tests/test_no_laya_in_gates.py:202` -- `def _init_repo(tmp_path, gate_files_txt, files, env):` helper.
- `tests/test_no_laya_in_gates.py:224` -- `def test_staged_renamed_gate_file_is_missing_not_clean`.
- `tests/test_no_laya_in_gates.py:251` -- `def test_staged_deleted_gate_file_is_missing`.
- `tests/test_no_laya_in_gates.py:272` -- `def test_staged_allowlist_is_read_from_index`.
- `tests/test_no_laya_in_gates.py:298` -- `def test_staged_allowlist_absent_from_index_refused`.
- `tests/test_no_laya_in_gates.py:327` -- `def test_scanned_count_equals_listed_count`.

No new fixture files under `tests/fixtures/decisions/gate_violation/`.

## Code-intel

`_read_staged` callers: `scripts/no_laya_in_gates.py:225` and `scripts/no_laya_in_gates.py:275` (no external callers). `_load_allowlist` callers: `scripts/no_laya_in_gates.py:223` and `scripts/no_laya_in_gates.py:235` (no external callers). Instrument: grep (graft fallback).

## RED at PIN -> GREEN after fix

| Test | RED (PIN, `5b5f6bbdb82c5a32`) | GREEN (fix) |
|---|---|---|
| `test_staged_renamed_gate_file_is_missing_not_clean` | `assert 0 == 4` -- rc=0, stderr `1 files scanned, clean` | rc=4, stderr `gate-file-missing: scripts/report_lint.py` |
| `test_staged_deleted_gate_file_is_missing` | `assert 0 == 4` -- rc=0, stderr `1 files scanned, clean` | rc=4, stderr `gate-file-missing: scripts/report_lint.py` |
| `test_staged_allowlist_is_read_from_index` | `assert 0 == 3` -- rc=0, stderr `1 files scanned, clean` | rc=3, stdout reports violation in `report_lint.py` line 1 |
| `test_staged_allowlist_absent_from_index_refused` | `assert 0 == 64` -- rc=0, stderr `1 files scanned, clean` | rc=64, stderr `gate-file-missing: scripts/gate_files.txt` |
| `test_scanned_count_equals_listed_count` | `assert 0 != 0` -- rc=0, stderr `1 files scanned, clean` | rc=4, stderr `gate-file-missing: scripts/report_lint.py` |

RED run: `5 failed, 9 passed in 0.91s`. GREEN run 1: `14 passed in 0.81s`. GREEN run 2: `14 passed in 0.82s`.

## Mutant table (m6-m9)

Every mutant on a scratch-copy-restored file (`/tmp/j10r/mutant/no_laya_in_gates.py.pristine`, sha256[:16] `ec9e510e09a47182`); restore + sha256 verified between each row.

| Mutant | Mutation | Result | Killed by |
|---|---|---|---|
| m6 | Restore `if not args.staged:` guard around existence check (PIN form) | `2 failed, 12 passed` | `test_staged_renamed_gate_file_is_missing_not_clean`, `test_staged_deleted_gate_file_is_missing` |
| m7 | Restore `if content is None: continue` (PIN form) | `14 passed` -- SURVIVES | EQUIVALENT: the `_exists_staged` check (B1 fix) catches missing files before the scan loop reaches `content is None`; the hard-failure line is defense-in-depth with no reachable path |
| m8 | Read allowlist from worktree in staged mode (PIN form) | `2 failed, 12 passed` | `test_staged_allowlist_is_read_from_index`, `test_staged_allowlist_absent_from_index_refused` |
| m9 | Walk worktree in staged mode (use `_glob_structural(root)` instead of `_glob_structural_staged()`) | `14 passed` -- SURVIVES | EQUIVALENT-FOR-THE-FROZEN-TESTS: the structural walk difference (index vs worktree enumeration) is not exercised by any test; a test staging a new structural file absent from the worktree would discriminate -- that is issue #24 row 9 (F15), not B1/B2 |

## Gate runs (pasted)

```
$ /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r/bt
14 passed in 0.92s
$ /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r/bt
14 passed in 0.86s
$ /root/venv-agent-factory/bin/python -m pyflakes scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py
(clean, rc=0)
```

## Live-tree lines (both modes)

```
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 33 files scanned, clean
rc=0
$ python3 scripts/no_laya_in_gates.py --staged
no_laya_in_gates: 33 files scanned, clean
rc=0
```

Staged count reads 33, matching the 33 entries in `scripts/gate_files.txt`.

## Seed AC verification

```
$ python -m pytest tests/test_no_laya_in_gates.py -q
14 passed in 0.85s  (AC 5, rc=0)
$ python3 -c "... assert 'no_laya_in_gates' in t; print('WIRED')"
WIRED  (AC 6, rc=0)
```

## AP screen

```
$ python3 scripts/ap_screen.py --tests scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py
--- TEST_SCREEN over 2 path(s): 0 hits over 2 files ---
```

The AF-AP-40 signature is known-noisy on `scripts/no_laya_in_gates.py` (`scripts/ap_screen.py scripts/no_laya_in_gates.py` reports `AF-AP-40: 7` at `:136-152`); the `--tests` flag filters those. Issue #24 row 10.

## Issue #24 row 9 (F15) status

The `_glob_structural_staged()` function enumerates the INDEX (`git ls-files --cached`) in `--staged` mode. An untracked structural file (e.g. `proofs/S0-13/check_x.py` sitting in the worktree but never staged) no longer blocks commits through the hook. This CLOSES the mechanism described in F15 (issue #24 row 9). However, m9 shows no test discriminates the index-vs-worktree walk, so the closure is by code inspection, not by a killing test.

## DISCREPANCIES

- **m7 SURVIVES** where the brief predicted it would kill `test_staged_deleted_gate_file_is_missing`. Root cause: the B1 existence check (`_exists_staged`) runs BEFORE the scan loop and catches missing files at the completeness-control stage. The `content is None` path is structurally unreachable after the existence check. The hard failure is defense-in-depth: it prevents fail-open if the existence check is ever weakened or bypassed, but no current test reaches it.
- **m9 SURVIVES** as the brief's alternative predicted (EQUIVALENT-FOR-THE-FROZEN-TESTS).

## NOT-done

- The 19 non-blocking findings (F3-F21) are issue #24, not this lane's boundary.
- No commit, push, or outward action taken.
- No files outside the boundary touched: not `scripts/hooks/pre-commit`, not `scripts/gate_files.txt`, not `src/agent_factory/decisions/`, not `scripts/laya_probe.py`, not `tests/test_laya_probe_report.py`, not `tests/fixtures/decisions/probe/`, not the ledger, wiki, or CLAUDE.md.
- No bug-echo signature added for B1/B2 (AF-AP-40 already covers the class; extending the AP_SCREEN is outside the boundary).
