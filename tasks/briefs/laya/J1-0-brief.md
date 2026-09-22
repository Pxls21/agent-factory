# J1-0 — the never-a-gate screen (KC-J1's mechanism) — ships FIRST, before any Laya bytes exist

PIN: d66ace5 (origin head at authoring; `scripts/hooks/pre-commit` sha256[:16] 787d513897547864)
LANE: laya-j1-0 (sandbox; agent `code-implementer`)
ROLE: code-implementer (build). Contract: `seeds/seed-laya-j1-v1.yaml` (AC 5 `ac_508de0f12c24907c`, AC 6 `ac_77ae22bcda8a6aab`) + `tasks/laya-j1-breakdown.md` row J1-0 + the council verdict KC-J1 (`docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md`).
BOUNDARY (exact; nothing else): NEW `scripts/no_laya_in_gates.py`, NEW `scripts/gate_files.txt`, MODIFIED `scripts/hooks/pre-commit` (ONE appended block), NEW `tests/test_no_laya_in_gates.py`, NEW `tests/fixtures/decisions/gate_violation/` (a miniature tree). Never the ledger, the wiki, any brief, any other hook, any proof file. Do NOT commit — the coordinator commits through `scripts/safe_commit.sh`.
VENUE: sandbox. Python = `/root/venv-agent-factory/bin/python` (pytest, pyflakes installed). pytest with a SHORT basetemp: `mkdir -p /tmp/j10/bt && python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10/bt`; remove the basetemp after each run (disk discipline).

## The contract (from the interview, exact)
1. **Scanned set = the explicit committed allowlist** `scripts/gate_files.txt` — one repo-relative path per line, comments with `#`: `scripts/hooks/pre-commit`, `scripts/hooks/pre-push`, `scripts/hooks/post-commit`, every `.github/workflows/*.yml` BY NAME, `scripts/report_lint.py`, `scripts/ap_screen.py`, `scripts/lane_gate.sh`, `scripts/test_summary.sh`, `scripts/lint_delta.py`, `scripts/validate-ledger`, `scripts/proof-runner`, `scripts/ledger-gen`, `scripts/push_clean.sh`, `scripts/safe_commit.sh`, `scripts/vendored_manifest.py`, `scripts/pc_lane.sh`, `scripts/pc_suite.sh`, `scripts/check-proof-status.py`, `harness-ports/bin/pc-lane.sh`, every `proofs/*/check_*.py` BY NAME (measure the tree; the counts at authoring are pasted below). Never a glob at scan time.
2. **Completeness control:** the screen ALSO walks three structural patterns — `scripts/hooks/*`, `.github/workflows/*.yml`, `proofs/*/check_*.py` — and exits 4 with `gate-file-unlisted: <path>` for any match absent from the list (one line per path). A listed path that does not exist exits 4 with `gate-file-missing: <path>`.
3. **Vocabulary = a CLOSED token list**, no regex over prose: `laya`, `systemone`, `system_one`, `system-one`, `jev`, `jevcache`, `sieve`, `sieve-run`, `decide-harvest`, `decide_harvest`, `laya-decide`, `agent_factory.decisions`, `decisions.ledger`, `decisions.canonical`, `decisions.jsonl`. Matching: case-insensitive on identifier boundaries — a token is a maximal run of `[A-Za-z0-9_-]` (so `sieve` fires, `receives` does not; `laya_probe` fires because the run splits on nothing — state this: the maximal run is `laya_probe`, which is NOT in the list, so it does NOT fire; document that and test it). PLUS one structural check: any Python `import agent_factory.decisions` / `from agent_factory.decisions import …` / `from agent_factory import decisions` in a listed `.py` file fires as token `agent_factory.decisions`.
4. **Exit codes:** 0 clean; 3 = violation, one line per hit `<path>:<line>:<token>`; 4 = the completeness/missing control; 64 = usage. `--root <dir>` scans that tree (the fixture tree) instead of the repo; `--list <file>` overrides the allowlist path (default `scripts/gate_files.txt` under the root).
5. **Non-fires by CONSTRUCTION:** only the listed files are read, so docs prose, `tests/fixtures/decisions/`, the decisions module, `scripts/decide-harvest` and the screen's own source are outside the scanned set; the only exclusion by identity is the screen's own path if it ever appears in the list (refuse listing it: `gate-file-self: scripts/no_laya_in_gates.py`, exit 64).
6. **Pre-commit wiring:** ONE appended block in `scripts/hooks/pre-commit` runs `"$PY" "$REPO_ROOT/scripts/no_laya_in_gates.py" --staged` (`--staged` scans the STAGED content of listed files via `git show :<path>` so a violation cannot be dodged by an unstaged edit); a non-zero exit BLOCKS the commit with `COMMIT BLOCKED by the never-a-gate screen (rc=N)`; UNLIKE the other gates in that file there is NO bypass variable — do not add one, do not read one (KC-J1 is an absorbing barrier). Keep the existing gates untouched.
   **AMENDMENT 1 (J1-0-R2, coordinator 2026-09-22 20:3xZ, from VERIFY-J1-0-R1 finding R3):** a listed path must be a REGULAR file. In `--staged` mode the index mode of every listed entry must be `100644` or `100755` (read from `git ls-files --stage -- <path>`); any other mode is the completeness error `gate-file-not-regular: <path> mode=<mode>` (exit 4) — `git show :<path>` alone returned a symlink entry's LINK TEXT, so a listed gate file replaced by a `120000` symlink to an unlisted `laya`-carrying file screened clean and the commit landed (the pre-existing hole at 3bd4fbb). On disk (no `--staged`) a listed path that is a symlink is `gate-file-not-regular: <path> symlink` and any other non-regular file `gate-file-not-regular: <path> not-a-regular-file`, both exit 4, checked with `lstat` before the read. An executable regular file (`100755`) stays clean. Tests: `test_staged_symlinked_gate_file_is_not_regular` (asserts the planted index mode is `120000`, then rc 4 with the exact line), `test_worktree_symlinked_gate_file_is_not_regular`, `test_executable_regular_gate_file_stays_clean`.


## Tests (each RED before the code exists, GREEN after; paste both runs)
- `test_live_tree_clean`: the screen over the repo root exits 0 (paste the count of scanned files).
- `test_planted_violation_in_real_gate_path`: fixture tree `tests/fixtures/decisions/gate_violation/` holds `scripts/gate_files.txt` listing `scripts/hooks/pre-commit` and that file containing the token `laya` on a known line → exit 3, the exact line `scripts/hooks/pre-commit:<line>:laya`.
- `test_planted_violation_stripped_is_clean` (the positive control): the same tree with the token removed → exit 0.
- `test_unlisted_structural_match`: a fixture tree with `proofs/x/check_y.py` not in its list → exit 4 `gate-file-unlisted: proofs/x/check_y.py`.
- `test_identifier_boundary`: a listed fixture file containing `receives` and `laya_probe` → exit 0; containing `Laya` → exit 3 (case-insensitive).
- `test_import_check`: a listed fixture `.py` with `from agent_factory.decisions import ledger` → exit 3 naming token `agent_factory.decisions`.
- `test_no_bypass`: with `SKIP_LAYA_GATE_CHECK=1` and `SKIP_ALL=1` in the environment the planted violation STILL exits 3.
- `test_staged_mode`: in a throwaway git repo (fixture), a listed file staged WITH the token while the worktree copy is clean → `--staged` exits 3; the reverse (worktree dirty, index clean) → exits 0.
- `test_precommit_wired`: `scripts/hooks/pre-commit` contains the block (seed AC 6's check) and contains no line matching `SKIP_.*LAYA`.
Mutants (scratch-copy restore only; paste each run's failing test name): m1 drop the completeness walk → `test_unlisted_structural_match` red; m2 substring match instead of boundary → `test_identifier_boundary` red; m3 the pre-commit block removed → `test_precommit_wired` red; m4 a bypass env var honored → `test_no_bypass` red; m5 `--staged` reads the worktree → `test_staged_mode` red.

## Gates (paste verbatim)
`python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10/bt` TWICE (counts bitwise-identical); `python -m pyflakes scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py`; `bash -n scripts/hooks/pre-commit`; the seed's AC 5 and AC 6 verify_commands (from `seeds/seed-laya-j1-v1.yaml`) run and pasted; `python3 scripts/ap_screen.py scripts/no_laya_in_gates.py --tests tests/test_no_laya_in_gates.py` (paste the hit table). Code intel FIRST: `graft ask` / `scripts/lane_context.sh` on `scripts/hooks/pre-commit` before editing it (paste the pack's blast-radius line).

## Report (`tasks/briefs/laya/J1-0-report.md`)
DATA, not prose: files:lines created/changed; the RED→GREEN pairs pasted; the five mutant rows; the two gate runs; the scanned-file count; DISCREPANCIES / NOT-done. `python3 scripts/report_lint.py --min-refs 10 tasks/briefs/laya/J1-0-report.md` — at most three fix rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-22T17:00:25Z, sandbox @ d66ace5)
```
$ ls scripts/no_laya_in_gates.py scripts/gate_files.txt tests/test_no_laya_in_gates.py 2>&1 | head -3
ls: cannot access 'scripts/no_laya_in_gates.py': No such file or directory
ls: cannot access 'scripts/gate_files.txt': No such file or directory
ls: cannot access 'tests/test_no_laya_in_gates.py': No such file or directory
$ grep -c 'no_laya' scripts/hooks/pre-commit
0
$ grep -n 'SKIP_[A-Z_]*' -o scripts/hooks/pre-commit | sort -u | head
29:SKIP_ANCHOR_CHECK
32:SKIP_ANCHOR_CHECK
33:SKIP_ANCHOR_CHECK
47:SKIP_MANIFEST_CHECK
48:SKIP_MANIFEST_CHECK
61:SKIP_MANIFEST_CHECK
62:SKIP_MANIFEST_CHECK
77:SKIP_MIRROR_CHECK
78:SKIP_MIRROR_CHECK
8:SKIP_LINT_DELTA
$ ls scripts/hooks/ | tr '\n' ' '
post-commit pre-commit pre-push 
$ ls .github/workflows/*.yml | wc -l; ls .github/workflows/*.yml | tr '\n' ' '
2; .github/workflows/planning-checks.yml .github/workflows/stage0-ci.yml 
$ ls proofs/*/check_*.py | wc -l
13
$ wc -l scripts/hooks/pre-commit
111 scripts/hooks/pre-commit
```
