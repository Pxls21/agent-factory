# J1-0-R3 — the never-a-gate screen follows its in-process include edges (AMENDMENT 2; AF-AP-120)

PIN: the origin head that carries this brief (read it with `git log -1 --format=%h origin/claude/soundbox-kit-migration-iz1jwf`; the brief commit is the only change since 9097ab3).
ROLE: a sandbox BUILD lane (`code-implementer`). You work in your own worktree. You do NOT commit, push, open PRs or comment anywhere. Leave every change uncommitted in the worktree and end with the report.
BOUNDARY (exact; nothing else): MODIFIED `scripts/no_laya_in_gates.py`, MODIFIED `scripts/gate_files.txt`, MODIFIED `tests/test_no_laya_in_gates.py`, NEW fixture trees under `tests/fixtures/decisions/` (only new directories; do not edit existing fixtures), NEW `tasks/briefs/laya/J1-0-R3-report.md`. Read anything; write nothing else.

## Why (the finding this closes)

`scripts/no_laya_in_gates.py` proves the TEXT of the files listed in `scripts/gate_files.txt` carries none of the closed vocabulary. It follows no include edge. On 2026-09-22 a repair moved banned wiring out of a listed gate file into an unlisted helper that the gate file `source`d: the screen read clean while the banned code still ran inside the gate's process (AF-AP-120, `docs/INCIDENT-LOG.md`). The same hole exists for Python: listed checkers import first-party helper modules that are not listed and are never screened (measured below). Both are latent today (no vocabulary in any helper), which is exactly when a barrier should be closed.

## The contract — AMENDMENT 2 (coordinator, 2026-09-23; decided, do not re-litigate)

Two new completeness rules, both exit 4 (the completeness family), both in the worktree mode AND in `--staged` mode (in `--staged`, candidate files come from the index, `git ls-files`, and texts from `git show :<path>`, exactly like the existing staged reads):

1. **Shell include edges are refused outright.** In every listed gate file that is not Python (not `*.py` and no `python` shebang on line 1), any line whose first non-blank token is `source` or `.` followed by whitespace is the error `gate-file-sources: <path>:<lineno>`. No resolution, no allowance: a gate file never sources anything (zero such lines exist today). YAML workflow files are scanned the same way (a `run:` block that sources is refused too).
2. **Python import edges are closed-world.** For every listed Python gate file (`*.py` or a `python` shebang on line 1), parse the text with `ast` (a SyntaxError is `gate-file-unparseable: <path>`, exit 4). For every `import X…` and `from X… import …` (absolute; take the top-level name) and every relative import (`level > 0`, resolved against the importing file's directory), classify the module:
   - in `sys.stdlib_module_names` (or `__future__`) → allowed;
   - in the closed constant `EXTERNAL_MODULES = frozenset(["fubuki_os", "jsonschema", "lint", "pyflakes", "yaml"])` (measured below; a new third-party import in a gate must extend this constant in a reviewable change) → allowed;
   - otherwise resolve it to repo files: candidates are `<name>.py` and `<name>/__init__.py` under the importing file's own directory and its subdirectories to depth 2, then under `scripts/` and `src/` (top level of each). Exactly one candidate → that path must be LISTED in `scripts/gate_files.txt`, else `gate-file-import-unlisted: <gate> imports <name> -> <path>`; zero candidates → `gate-file-import-unresolved: <gate> imports <name>`; two or more → `gate-file-import-ambiguous: <gate> imports <name> -> <p1>,<p2>…`.
   A listed helper is itself a listed Python gate file, so its own imports are checked by the same rule (the closure is the list; no recursion code needed beyond the list).
3. `scripts/gate_files.txt` gains the four first-party helpers the listed checkers import today (measured below): `proofs/S0-01/pins.py`, `proofs/S0-01/negative_contract.py`, `proofs/S0-01/tools/nostr_verify.py`, `proofs/S0-02/oracle/denial_table.py`. Add any further helper the rule surfaces on the real tree, and list each addition in the report with the import that pulled it in.
4. **Exec edges are OUT of scope (a declared limit, not a silent one).** A gate file that EXECUTES another repo script (`bash harness-ports/bin/x.sh`, `python3 "$AF_REPO/scripts/y.py"`) runs it in another process; many such paths are built from variables no lexical screen can resolve, and a fail-closed rule on them would block every commit. Add ONE docstring paragraph to the screen stating: the screen follows in-process include edges (source refused, Python imports closed) and does NOT follow exec edges; the measured count at this amendment (26 literal exec edges from listed shell gate files, 12 distinct unlisted targets, premise below). Do not implement exec-edge following.
5. Nothing else changes: the vocabulary, the exit codes 0/3/64, the existing completeness errors, the SELF refusal, the no-bypass rule, the output line format (`no_laya_in_gates: N files scanned, clean`).

## Tests (each RED before the code, GREEN after; paste both runs)

New fixture trees, one per rule (each a minimal tree with its own `scripts/gate_files.txt`, run with `--root <tree>`):
- `test_sourced_helper_refused`: a listed `scripts/hooks/pre-commit` containing `. scripts/helper.sh` and, in a second case, `  source "$ROOT/scripts/helper.sh"` → exit 4, the exact lines `gate-file-sources: scripts/hooks/pre-commit:<n>`. The helper itself contains `laya` and is NOT listed — the test proves the refusal fires on the edge, independent of the helper's text.
- `test_unlisted_import_refused`: a listed `proofs/x/check_y.py` with `import helper` and `proofs/x/helper.py` present but unlisted → exit 4 `gate-file-import-unlisted: proofs/x/check_y.py imports helper -> proofs/x/helper.py`.
- `test_listed_import_screened`: the same tree with `proofs/x/helper.py` listed and containing `laya` on a known line → exit 3 `proofs/x/helper.py:<line>:laya` (the closure-by-listing actually screens the helper).
- `test_subdir_import_resolved`: `proofs/x/tools/helper2.py` imported as `import helper2` resolves (depth-2 search) and, listed and clean, exits 0.
- `test_unresolved_import_refused`: `import not_a_module_anywhere` → exit 4 `gate-file-import-unresolved: … imports not_a_module_anywhere`.
- `test_ambiguous_import_refused`: `proofs/x/helper.py` and `scripts/helper.py` both present → exit 4 `gate-file-import-ambiguous: …`.
- `test_stdlib_and_external_allowed`: `import os, json` + `import yaml` + `from jsonschema import validate` → exit 0.
- `test_relative_import`: a listed package module with `from . import sibling` resolves against its own directory.
- `test_unparseable_python_gate`: a listed `.py` with a syntax error → exit 4 `gate-file-unparseable: <path>`.
- `test_staged_import_closure`: in a throwaway git repo, the helper is staged as unlisted while the worktree list has it → `--staged` exits 4 (the index is authoritative); the reverse → `--staged` exits 0.
- `test_external_modules_locked`: `EXTERNAL_MODULES` equals exactly `{"fubuki_os", "jsonschema", "lint", "pyflakes", "yaml"}` (a vocabulary lock; widening it is a reviewed change).
- `test_live_tree_clean` (existing): still exit 0 on the real repo; paste the new scanned-file count.

Mutants (scratch-copy restore only, never `git checkout`/`stash` the shared tree; every mutant must COMPILE and COLLECT — AF-AP-78; paste each run's failing test name): m1 the source rule removed → `test_sourced_helper_refused` red; m2 the unlisted-import rule removed → `test_unlisted_import_refused` red; m3 subdirectory search removed → `test_subdir_import_resolved` red; m4 `EXTERNAL_MODULES` widened by one name → `test_external_modules_locked` red; m5 `--staged` resolves candidates from the worktree → `test_staged_import_closure` red; m6 the ambiguity branch returns the first match → `test_ambiguous_import_refused` red.

## Gates (paste verbatim)

`python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r3/bt` TWICE (counts bitwise-identical; `mkdir -p /tmp/j10r3` first); `python3 scripts/no_laya_in_gates.py` on the real tree (exit 0; paste the line); `python3 scripts/no_laya_in_gates.py --staged` after `git add -N` of nothing (paste; the index equals HEAD plus your worktree is unstaged, so it screens HEAD's index — exit 0); `python -m pyflakes scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py`; `bash -n scripts/hooks/pre-commit`; the seed's AC 5 verify_command from `seeds/seed-laya-j1-v1.yaml` (`python -m pytest tests/test_no_laya_in_gates.py -q`); `python3 scripts/ap_screen.py scripts/no_laya_in_gates.py` and `python3 scripts/ap_screen.py --tests tests/test_no_laya_in_gates.py` (paste; explain each hit in one line).

## Report (`tasks/briefs/laya/J1-0-R3-report.md`)

DATA, not prose: every file:line created or changed; each RED→GREEN pair pasted; the six mutant rows; the gate runs; the real tree's scanned-file count before (33) and after; every helper added to the list with the import that pulled it in; DISCREPANCIES / NOT-done. Then `python3 scripts/report_lint.py --min-refs 10 tasks/briefs/laya/J1-0-R3-report.md` — at most three fix rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23, sandbox @ 9097ab3)

```
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 33 files scanned, clean
$ (listed shell gate files) grep -cE '^\s*(\.|source)\s' <each>
0 in every listed non-Python gate file (13 files)
$ (listed Python gate files) non-stdlib top-level imports, ast walk
scripts/lint_delta.py: ['pyflakes']
scripts/validate-ledger: ['jsonschema']        scripts/proof-runner: ['jsonschema']
proofs/S0-01/check_acp_conformance.py: ['check_initialize', 'negative_contract', 'nostr_verify', 'pins'] sys.path=yes
proofs/S0-01/check_initialize.py: ['jsonschema', 'negative_contract', 'pins'] sys.path=yes
proofs/S0-02/check_buzz_authz.py: ['denial_table'] sys.path=yes
proofs/S0-03/check_omniroute_roundtrip.py: ['yaml']   proofs/S0-06/check_four_scope.py: ['yaml']
proofs/S0-07/check_fubuki_corrections.py: ['fubuki_os', 'lint'] sys.path=yes (the pinned fubuki-os checkout, outside the repo)
proofs/S0-11/check_eval_hardening.py: ['yaml']        proofs/S0-12/check_pin_diff.py: ['yaml']
(the other listed Python gate files: none)
$ git ls-files | grep the first-party names
pins -> proofs/S0-01/pins.py
negative_contract -> proofs/S0-01/negative_contract.py
nostr_verify -> proofs/S0-01/tools/nostr_verify.py
check_initialize -> proofs/S0-01/check_initialize.py (already listed)
denial_table -> proofs/S0-02/oracle/denial_table.py
lint, fubuki_os -> no repo file (external)
$ vocabulary hits in the four unlisted helpers (the screen's own _check_line)
proofs/S0-01/negative_contract.py hits: []   proofs/S0-01/pins.py hits: []
proofs/S0-01/tools/nostr_verify.py hits: []  proofs/S0-02/oracle/denial_table.py hits: []
$ literal exec edges from listed shell gate files (interpreter + repo path)
26 edges; 12 distinct UNLISTED targets: harness-ports/bin/sync-skills.sh, harness-ports/tests/test_context_mirrors.sh,
harness-ports/bin/sync-lane-skills.sh, scripts/fubuki_pin_sync.sh, harness-ports/tests/run-all.sh, scripts/realleg_sync.sh,
scripts/transcript_export.py, scripts/pc_bridge_exec.py, harness-ports/bin/qwen-server.sh, scripts/ripwire_review.sh,
scripts/lane_context.sh, harness-ports/bin/hermes-session-export.py
```
