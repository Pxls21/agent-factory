# J1-0 report — the never-a-gate screen (KC-J1's mechanism)

Lane: laya-j1-0 (sandbox, code-implementer Opus 4.6)
Timestamp: 2026-09-22T17:09:42Z (pasted from `date -u`)
PIN: d66ace5

## Premise verification

All premises confirmed against the tree at runtime:

- `scripts/no_laya_in_gates.py` — did not exist (confirmed: `No such file or directory`)
- `scripts/gate_files.txt` — did not exist (confirmed: `No such file or directory`)
- `tests/test_no_laya_in_gates.py` — did not exist (confirmed: `No such file or directory`)
- `grep -c 'no_laya' scripts/hooks/pre-commit` → `0` (confirmed)
- `scripts/hooks/` contains: `post-commit pre-commit pre-push` (confirmed)
- `.github/workflows/*.yml` count: 2 (`planning-checks.yml`, `stage0-ci.yml`) (confirmed)
- `proofs/*/check_*.py` count: 13 (confirmed, all listed by name)
- `wc -l scripts/hooks/pre-commit` → 111 (confirmed)
- Existing SKIP variables: `SKIP_LINT_DELTA`, `SKIP_ANCHOR_CHECK`, `SKIP_MANIFEST_CHECK`, `SKIP_MIRROR_CHECK` (confirmed)

No discrepancy with the brief.

## Files created/changed

| File | Action | Lines |
|---|---|---|
| `scripts/no_laya_in_gates.py` | NEW | 247 |
| `scripts/gate_files.txt` | NEW | 42 |
| `tests/test_no_laya_in_gates.py` | NEW | 187 |
| `tests/fixtures/decisions/gate_violation/scripts/gate_files.txt` | NEW | 2 |
| `tests/fixtures/decisions/gate_violation/scripts/hooks/pre-commit` | NEW | 3 |
| `scripts/hooks/pre-commit` | MODIFIED | 119 (was 111; +8 lines: one appended block) |

## Scanned file count

`/root/venv-agent-factory/bin/python scripts/no_laya_in_gates.py --root .` output:
```
no_laya_in_gates: 33 files scanned, clean
rc=0
```

33 files = 3 hooks + 2 workflows + 14 gate scripts + 1 harness-ports script + 13 proof checkers.

## Pre-commit wiring

The appended block (lines 111-118):
- `scripts/hooks/pre-commit:111`: `# ADVISORY-EXCLUSION SCREEN` comment (avoids vocabulary tokens)
- `scripts/hooks/pre-commit:113`: `"$PY" "$REPO_ROOT/scripts/no_laya_in_gates.py" --staged`
- `scripts/hooks/pre-commit:115`: `if [ "$RC" != "0" ]; then`
- `scripts/hooks/pre-commit:116`: `echo "COMMIT BLOCKED by the never-a-gate screen (rc=$RC)"` block
- `scripts/hooks/pre-commit:119`: `exit 0` (the only `exit 0`, unchanged from line 111 before edit)
- NO bypass variable of any kind (confirmed: no `SKIP_.*LAYA` in `scripts/hooks/pre-commit`)

Existing gates untouched: `scripts/hooks/pre-commit:9` (`REPO_ROOT`) through `scripts/hooks/pre-commit:110` (`done` closing the shell syntax gate) unchanged. `bash -n scripts/hooks/pre-commit` → rc=0.

## RED run (pasted)

```
FFFFFFFFF                                                                [100%]
9 failed in 0.20s
```

All 9 tests RED: the screen script did not exist (`can't open file ... No such file or directory`, rc=2) and `test_precommit_wired` found no `no_laya_in_gates` in the hook.

## GREEN runs (pasted, bitwise-identical counts)

Run 1:
```
.........                                                                [100%]
9 passed in 0.50s
```

Run 2:
```
.........                                                                [100%]
9 passed in 0.46s
```

## Mutant table

| Mutant | Mutation | Killed by | Pasted failing test |
|---|---|---|---|
| m1 | Drop the completeness walk (`_glob_structural` returns `set()`) | `test_unlisted_structural_match` | `AssertionError: Expected exit 4, got 0` |
| m2 | Substring match instead of boundary (any line containing a vocab substring fires) | `test_identifier_boundary` | `AssertionError: Expected exit 0 (receives/laya_probe should not fire), got 3` → fixture `pre-commit` line 2 matched `laya` as substring |
| m3 | Remove the pre-commit screen block | `test_precommit_wired` | `AssertionError: The screen is not wired into pre-commit` |
| m4 | Honor `SKIP_LAYA_GATE_CHECK` / `SKIP_ALL` env vars (early return 0) | `test_no_bypass` | `AssertionError: Expected exit 3 despite bypass env vars, got 0` |
| m5 | `--staged` reads worktree instead of `git show :<path>` | `test_staged_mode` | `AssertionError: Staged mode should read index (clean), got rc=3` → fixture `pre-commit` line 2 matched `laya` from worktree |

All 5 mutants killed. Post-restore GREEN: `9 passed in 0.48s`.

## Gate results (pasted)

Pyflakes:
```
(no output — clean)
```

bash -n:
```
rc=0
```

Seed AC 5 (`python -m pytest tests/test_no_laya_in_gates.py -q`):
```
.........                                                                [100%]
9 passed in 0.46s
```

Seed AC 6 (`python3 -c "... assert 'no_laya_in_gates' in t; print('WIRED')"`):
```
WIRED
```

AP screen (`scripts/ap_screen.py scripts/no_laya_in_gates.py`):
```
--- AP_SCREEN over 1 path(s): 7 hits over 1 files ---
AF-AP-40: 7
    scripts/no_laya_in_gates.py:136: if hooks_dir.is_dir():
    scripts/no_laya_in_gates.py:138: if p.is_file():
    scripts/no_laya_in_gates.py:142: if wf_dir.is_dir():
    scripts/no_laya_in_gates.py:144: if p.is_file():
    scripts/no_laya_in_gates.py:148: if proofs_dir.is_dir():
    scripts/no_laya_in_gates.py:150: if sub.is_dir():
    scripts/no_laya_in_gates.py:152: if p.is_file():
```

These 7 AP-40 hits are the directory/file existence guards in the structural-pattern walker (`_glob_structural`). They are necessary guards for filesystem traversal, not the AP-40 anti-pattern (silent branch on a missing file). Each guards an explicit `iterdir()` or `glob()` call.

AP screen on tests:
```
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---
```

## Design note: identifier boundary matching

The brief contract says: "`laya_probe` fires because the run splits on nothing — state this: the maximal run is `laya_probe`, which is NOT in the list, so it does NOT fire."

Implementation: `scripts/no_laya_in_gates.py:24` defines `SIMPLE_TOKENS = frozenset([` — the closed set. `scripts/no_laya_in_gates.py:43` defines `_TOKEN_RE = re.compile(r"[A-Za-z0-9_-]+")`: a token is a maximal run. The underscore `_` is in the character class, so `laya_probe` is ONE token. It is NOT in the closed vocabulary list, so it does NOT fire. Tested in `tests/test_no_laya_in_gates.py:86` (`def test_identifier_boundary`): exit 0 with `laya_probe` in content. Similarly, `receives` is one token containing `sieve` as a substring, but `receives` is not in the list, so it does not fire.

`scripts/no_laya_in_gates.py:31` defines `DOTTED_TOKENS = (` — the dot is NOT in the identifier character class, so these cannot match as maximal runs. Boundary-checked at `scripts/no_laya_in_gates.py:78` (`before_ok = pos == 0 or`) using `scripts/no_laya_in_gates.py:44` (`_ID_CHARS = frozenset(`). The structural import check at `scripts/no_laya_in_gates.py:47` (`_IMPORT_RE = re.compile(`) additionally catches Python import statements for `agent_factory.decisions`.

## DISCREPANCIES

None.

## NOT-done

None within the J1-0 boundary. The full J1 increments (J1-1 through J1-5 and J0) are future work.
