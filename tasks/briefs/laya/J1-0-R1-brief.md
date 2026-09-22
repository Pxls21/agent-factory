# J1-0-R1 — the ONE focused repair of VERIFY-J1-0's two blockers on the never-a-gate screen (D-031)

PIN: 3bd4fbb (origin; the VERIFY-J1-0 harvest commit — `scripts/no_laya_in_gates.py` sha256[:16] 5b5f6bbdb82c5a32, `tests/test_no_laya_in_gates.py` ec18351df3e077ae, both byte-identical to 98a604a)
LANE: laya-j1-0-r1 (sandbox; agent `code-implementer`)
CONTRACT REVISION (frozen): `tasks/briefs/laya/VERIFY-J1-0-report.md` §B1 + §B2 (+ §F, the predicate applied) and the original contract `tasks/briefs/laya/J1-0-brief.md` items 2 and 6. BUDGET: one repair round; B1 + B2 ONLY — the 19 non-blocking findings are GitHub issue #24 (not this lane's; do not fix them, do not widen).
BOUNDARY (exact): MODIFIED `scripts/no_laya_in_gates.py`, MODIFIED `tests/test_no_laya_in_gates.py`, and (only if a fixture is needed) NEW files under `tests/fixtures/decisions/gate_violation/`. NOTHING else: not the hook, not the allowlist, not other lanes' files (`src/agent_factory/decisions/`, `scripts/laya_probe.py`, `tests/test_laya_probe_report.py`, `tests/fixtures/decisions/probe/`). Do NOT commit.

## The two blockers (verbatim mechanism; re-verify at the PIN before editing and paste)
- **B1** `scripts/no_laya_in_gates.py:210` `if not args.staged:` runs the required-file control ONLY in worktree mode — in `--staged` (the only production mode, the hook's) a listed gate file absent from the INDEX is never reported; `:230` `if content is None: continue` then drops a file whose `git show :<path>` failed (`:100-106` maps the failure to `None`), and `:242` prints `N files scanned, clean`, rc 0. Reproduction (the verifier's, through the real hook): `git mv scripts/report_lint.py scripts/report_lint_v2.py` + a planted `laya` + `git add` + `git commit` → `32 files scanned, clean`, the commit lands.
- **B2** `:187`/`:193` read `scripts/gate_files.txt` from the WORKTREE even in `--staged`: stage `laya` into a listed file, delete that line from the allowlist UNSTAGED → `32 files scanned, clean`, rc 0, while the committed allowlist still lists the file.

## The repair (exactly this)
1. **Index-consistent `--staged` mode.** In `--staged`: (a) the allowlist is read from the INDEX (`git show :scripts/gate_files.txt`; absent from the index → `gate-file-missing: scripts/gate_files.txt` exit 64 — never a worktree fallback); (b) the required-file control ALWAYS runs: a listed path absent from the index (`git cat-file -e :<path>` false, or `git show` failing) → `gate-file-missing: <path>` exit 4 — the `if not args.staged:` guard is removed and the control's existence check is index-backed in staged mode, disk-backed in worktree mode; (c) a `None` content is IMPOSSIBLE after (b) — replace the silent `continue` with a hard failure `gate-file-unreadable: <path>` exit 4 so the fail-open path cannot return; (d) the structural walk in `--staged` mode enumerates the INDEX (`git ls-files --cached -- 'scripts/hooks/*' '.github/workflows/*.yml' 'proofs/*/check_*.py'`) instead of the worktree, so a staged new checker is caught and an untracked one is not the hook's concern (issue #24 row 9 — say in the report whether this closes it). Worktree mode keeps its current disk-backed behavior. The scanned-file COUNT printed on success must equal the number of listed entries (so "32 of 33" can never read as clean).
2. **Tests** (RED at the PIN, GREEN after; paste both), each through a throwaway git repository fixture that copies the fixture tree, commits it, then stages the hostile change and runs the REAL script with `--staged` from inside that repo (the verifier's harness shape; never the shared tree): `test_staged_renamed_gate_file_is_missing_not_clean` (B1: `git mv` a listed file + plant `laya` in it → rc 4 naming `gate-file-missing: <old path>`); `test_staged_deleted_gate_file_is_missing` (rc 4); `test_staged_allowlist_is_read_from_index` (B2: an unstaged deletion of the line → rc 3 with the violation, the index's list wins); `test_staged_allowlist_absent_from_index_refused` (rc 64); `test_scanned_count_equals_listed_count` (the success line's N == the list's length); the nine frozen tests stay green.
3. **Mutants** (scratch-copy restore; paste the failing test name per row): m6 restore the `if not args.staged:` guard → the rename test red; m7 restore `if content is None: continue` → the delete test red; m8 read the allowlist from the worktree in staged mode → the allowlist test red; m9 walk the worktree in staged mode → state which test discriminates (if none, say EQUIVALENT-FOR-THE-FROZEN-TESTS and leave it to issue #24 row 9).

## Gates (paste verbatim)
`mkdir -p /tmp/j10r/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r/bt` twice (rm -rf after each); `python -m pyflakes scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py`; the live tree in BOTH modes (`python3 scripts/no_laya_in_gates.py` and `--staged`: rc 0, the count pasted — with the repair the staged count must read 33); the seed's AC 5/AC 6 commands; `python3 scripts/ap_screen.py --tests scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py` (the FLAG form; the report notes the AF-AP-40 signature is known-noisy on this file, issue #24 row 10). Code intel first: `graft ask "who calls _read_staged and _load_allowlist in scripts/no_laya_in_gates.py"` (fallback: grep) — paste.

## Report (`tasks/briefs/laya/J1-0-R1-report.md`)
DATA: files:lines changed; the RED→GREEN pairs for the five tests; the mutant rows m6-m9; the two gate runs; the live-tree lines in both modes; DISCREPANCIES / NOT-done (issue #24's rows are NOT this lane's — say so). `report_lint --min-refs 10` (≤ 3 rounds).

## PREMISE — MEASURED at authoring (2026-09-22T17:41:09Z, sandbox @ 3bd4fbb)
```
$ sed -n '210p;230p' scripts/no_laya_in_gates.py
    if not args.staged:
        if content is None:
$ sed -n '187p;193p' scripts/no_laya_in_gates.py
        list_path = root / "scripts" / "gate_files.txt"
    entries = _load_allowlist(list_path)
$ grep -c 'def test_' tests/test_no_laya_in_gates.py
9
$ python3 scripts/no_laya_in_gates.py --staged 2>&1; echo rc=$?
no_laya_in_gates: 33 files scanned, clean
rc=0
```
