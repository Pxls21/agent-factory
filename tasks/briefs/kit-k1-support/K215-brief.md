# K215 — the registry's owed screens and bakes (task #215): nine screen rows, three skill bakes, five VERIFY-K150 follow-ups

PIN: 942ad5e (the shared tree's HEAD and origin at authoring; every boundary file's blob is in the premise block). LANE: k215 (sandbox;
agent `code-implementer`, in the SHARED tree, no worktree isolation). Honey `ultra` Lever-2: your report is DATA: files:lines, pasted
counts, discrepancies, NOT-done. Do NOT spawn subagents.

WHY. Nine registry rows promised a screen line or a skill bake to task #150, which never carried them (VERIFY-K150 F-01); task #215 owns
them now, with the AF-AP-175 and AF-AP-177 screens, and issue #63's follow-ups on the same files. The registry (`docs/INCIDENT-LOG.md`,
the ANTI-PATTERN REGISTRY table) is the evidence: READ each row named below before you write its rule or its pattern, and write from the
row, never from this brief's one-line summary.

## Items (the contract; each is DONE only with the evidence its line names)

SCREEN ROWS (`.claude/hooks/edit-snapshot.py`, `AP_SCREEN`; tests in `tests/test_edit_snapshot_ap_screen.py`). Each new row cites its
AF-AP id and gets a positive fixture (the row fires) and a negative fixture (a near miss that must not fire), in the file's existing
pattern. Read the row's "greppable signature" column first. If the signature cannot be written as a line pattern without flooding clean
code, say so as a DISCREPANCY with the flood count measured over `scripts/ src/ proofs/ harness-ports/ .claude/hooks/`, and ship the
narrowest pattern that still fires on the registry's own instance (or none, with the reason). Put a row in `TEST_SCREEN` too only when
the class lives in tests, and say why.
- (s132) AF-AP-132: a line number computed with `str.splitlines()` in a tool that reports `file:line`. The registry's open sites are in
  the premise block (`scripts/no_laya_in_gates.py`, `scripts/vendored_manifest.py`): the row must fire on the `enumerate(….splitlines(),
  …)` form there.
- (s141) AF-AP-141: a `merge-base --is-ancestor` exit code compared as a boolean without its stderr read; the row's scope also names
  `cat-file -e`. Instance: `scripts/check-proof-status.py:164`.
- (s144) AF-AP-144: a raw parse call (`json.loads(`, `yaml.safe_load(`, `.decode(`, `.read_text()`) in a `proofs/*/check_*.py` module
  whose `main` catches only named failure types. If only a path-scoped line pattern is possible, scope it and say so.
- (s145) AF-AP-145: an EXIT-trap cleanup that a second signal can abort (a shell class: the row reaches `.sh` files only through
  `scripts/ap_screen.py` / `scripts/lane_context.sh` when a path is named, as the AF-AP-87 comment says; carry the same comment).
- (s149) AF-AP-149: a private-key block pattern written for one label spelling.
- (s152) AF-AP-152: a scrubber regex whose cost grows faster than its input (a quantified group over a quantified group that can match
  the separator; an unanchored `[class]*literal` alternative).
- (s175) AF-AP-175: a moving ref resolved per read. The registry asks for a per-file COUNT screen (two or more `HEAD` reads in one file).
  The hook screens hunks line by line: if a count screen cannot live there, write the line form (a `HEAD` literal passed to a git call)
  with the count condition in the row's message, and say so.
- (s177) AF-AP-177: a parsed JSON value used as a hash key before its type is checked, including the variable-held form the registry
  names (`scripts/decide-harvest:691`). Instances in the premise block: `scripts/decide-harvest:686`, `:691`,
  `harness-ports/bin/qwen_matrix.py:263`.
- AF-AP-153 has no line signature: it is bake (b153) below, not a row. Say so in the report.

SKILL BAKES. Each edit lands in `.claude/skills/<skill>/SKILL.md` AND in its hand-ported twin `.agents/skills/<skill>/SKILL.md`, ported
by hand in the twin's own words (never copy the `.claude` file over it). Keep each bake short: the rule, the incident that proved it
(date, lane or finding, AF-AP id), nothing more.
- (b150) `deep-work`, the `/bug-echo` paragraph (`.claude/skills/deep-work/SKILL.md:195`): AF-AP-150's rule.
- (b151) `build-loop`, the pre-commit paragraph (`.claude/skills/build-loop/SKILL.md:81`): AF-AP-151's gate rule (a change to the
  pre-commit hook, a script it runs or `scripts/gate_files.txt` also runs `tests/test_shell_syntax.py`; a fixture derives its lists
  from the committed config).
- (b153) `anti-hollow-green`: AF-AP-153's rule (a parser, lexer or screen rewrite feeds the previous version's refusals and new hostile
  variants to both versions; every old refusal stays a refusal or is named as a change). Orchestration 0d″ already carries the
  "proposed fix is a hypothesis" half (`.claude/skills/orchestration/SKILL.md:70`): do not repeat it; point to it.

ISSUE #63 FOLLOW-UPS (VERIFY-K150's report, `tasks/briefs/kit-k1-support/VERIFY-K150-report.md`, FINDING INVENTORY)
- (f03) F-03: the AF-AP-138 baseline control (`tests/test_vendored_manifest.py`, in `test_required_mutants_are_killed`) gets a
  committed negative control: a row that feeds the harness a killer that fails on the unmutated module and asserts the `AF-AP-138:`
  failure. RED proof: delete the control on a scratch copy and paste the new row going red.
- (f04) F-04: the AF-AP-89 row gets the AF-AP-87-style comment line (it reaches `.sh` files only when a path is named).
- (f06) F-06: the AF-AP-139 row gets a negative fixture (an always-401 rejecting handler) and positives for `-> None` and
  `HTTPStatus.OK`; if the row misses a positive and the registry row's scope includes it, widen the row and say so.
- (f07) F-07: `pyflakes_delta` gets controls that raise `OSError(errno.ENAMETOOLONG)` from the venv probe and
  `subprocess.TimeoutExpired` from the run, and an absent-venv case that asserts `[]`. Each RED on a scratch copy with the catch narrowed
  to `PermissionError` (paste it), GREEN on the PIN's code.
- (f08) F-08: `parse_classes` gets `bad-header` and `extra-cell` shapes in the malformed-row parametrize, each asserting its named
  refusal. `scripts/vendored_manifest.py` itself stays READ-ONLY.

## Order and twins (load-bearing)

1. Edit the `.claude` files. 2. Port each skill change into `.agents/skills/<skill>/SKILL.md`. 3. `bash harness-ports/bin/sync-skills.sh
--record`, then `--check` (rc 0). 4. `bash harness-ports/bin/sync-lane-skills.sh`, then `--check` (rc 0). 5. `python3
scripts/vendored_manifest.py --write`, then `--check` (PASS). Paste the diff of `sandbox-kit/VENDORED-MANIFEST.md` and
`sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv`; a class that changes is a DISCREPANCY to explain (the three skills and the hook are
`kit-adapted` at the PIN).

## Gates (paste every command with its output)

- `/root/venv-agent-factory/bin/python -m pytest tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py -q -p no:cacheprovider`
  twice; the counts must agree (the PIN: `173 passed`, set `2a60fb528bf2`); your new tests add to it.
- `/root/venv-agent-factory/bin/python -m pytest tests/test_hooks_worktree.py -q -p no:cacheprovider` once.
- `bash harness-ports/tests/run-all.sh` once; paste its last lines.
- `/root/venv-agent-factory/bin/python -m pyflakes .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py`
- `python3 scripts/no_laya_in_gates.py` (the hook is a listed gate file; exit 0).
- `python3 scripts/ap_screen.py .claude/hooks/edit-snapshot.py` (list any new hit your rows cause in the hook itself).
- For each new row: the count of lines it fires on across `scripts/ src/ proofs/ harness-ports/ .claude/hooks/` at your final tree,
  pasted, each hit classified (real instance, known site, false hit).

## Boundary and standing do-nots

MODIFY ONLY: `.claude/skills/{deep-work,build-loop,anti-hollow-green}/SKILL.md`, their `.agents/skills/` and `.agents/lane-skills/`
twins, `.claude/hooks/edit-snapshot.py`, `tests/test_edit_snapshot_ap_screen.py`, `tests/test_vendored_manifest.py`,
`harness-ports/hand-ported.sha256` (through `--record` only), `sandbox-kit/VENDORED-MANIFEST.md` and
`sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv` (through `--write` only). CREATE `tasks/briefs/kit-k1-support/K215-report.md` (write it
incrementally from the start). READ-ONLY: everything else, including `docs/INCIDENT-LOG.md` (the coordinator owns it; say in the report
which rows your change settles), `scripts/ap_screen.py`, `scripts/vendored_manifest.py`, `CLAUDE.md`, `AGENTS.md`, `.hermes.md`. Another
lane is live in the tree (VERIFY-J1-1-R3, writing `tasks/briefs/laya/VERIFY-J1-1-R3-report.md` and reading `src/agent_factory/decisions/`
and its tests): never touch its files. Report adjacent defects; never fix them. Never run git add, commit, stash, checkout, restore,
reset or clean in the shared tree: mutants and red runs go in a scratch copy (`git archive HEAD | tar -x -C /tmp/k215/work`). A command
with a trailing `&` runs in the background in its own directory; never let one create files in the tree root (VERIFY-K150 F-20). No PC
or bridge use. Take no outward-facing action. Paste every count and timestamp from command output. Long gates in ONE foreground call. A
deviation from any line above is STOP-and-report.

## Report (`tasks/briefs/kit-k1-support/K215-report.md`)

DATA: per item the file:line of each change and the registry row it came from; the RED→GREEN pair per new test; each row's fire count
and hit classification; the twin and manifest steps with their outputs; the gate outputs; DISCREPANCIES; NOT-done.
`python3 scripts/report_lint.py --min-refs 15 tasks/briefs/kit-k1-support/K215-report.md` (at most three fix rounds, then paste and
finish).

## PREMISE — MEASURED at authoring (2026-09-24 05:1xZ, /home/user/agent-factory@942ad5e; generated by scripts/premise_block.sh)

```
$ git rev-parse --short '942ad5e^{commit}'
942ad5e
$ git merge-base --is-ancestor 942ad5e origin/claude/soundbox-kit-migration-iz1jwf && echo pin-is-on-origin
pin-is-on-origin
$ git ls-tree 942ad5e -- .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py scripts/vendored_manifest.py scripts/ap_screen.py .claude/skills/deep-work/SKILL.md .claude/skills/build-loop/SKILL.md .claude/skills/anti-hollow-green/SKILL.md | awk '{print substr($3,1,12), $4}'
2f968c6f5bb3 .claude/hooks/edit-snapshot.py
86a2d657e65d .claude/skills/anti-hollow-green/SKILL.md
ad8f20500fae .claude/skills/build-loop/SKILL.md
3c4987a07e64 .claude/skills/deep-work/SKILL.md
eb20dde7e198 scripts/ap_screen.py
4a4ed0fece0b scripts/vendored_manifest.py
c33aa104023a tests/test_edit_snapshot_ap_screen.py
9737b4919c95 tests/test_vendored_manifest.py
$ /root/venv-agent-factory/bin/python -m pytest tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py -q -p no:cacheprovider 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*$//'
173 passed
$ bash scripts/pc_suite.sh set-id -- tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py
2 files set=2a60fb528bf2
$ python3 scripts/vendored_manifest.py --check 2>&1 | tail -1
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
$ bash harness-ports/bin/sync-skills.sh --check >/dev/null 2>&1; echo sync-skills-check rc=$?
sync-skills-check rc=0
$ bash harness-ports/bin/sync-lane-skills.sh --check >/dev/null 2>&1; echo sync-lane-skills-check rc=$?
sync-lane-skills-check rc=0
$ for id in 132 141 144 145 149 150 151 152 153 175 177; do printf 'AF-AP-%s registry-rows=%s hook-mentions=%s\n' $id "$(grep -c "^| AF-AP-$id |" docs/INCIDENT-LOG.md)" "$(grep -c "AF-AP-$id\b" .claude/hooks/edit-snapshot.py)"; done
AF-AP-132 registry-rows=1 hook-mentions=0
AF-AP-141 registry-rows=1 hook-mentions=0
AF-AP-144 registry-rows=1 hook-mentions=0
AF-AP-145 registry-rows=1 hook-mentions=0
AF-AP-149 registry-rows=1 hook-mentions=0
AF-AP-150 registry-rows=1 hook-mentions=0
AF-AP-151 registry-rows=1 hook-mentions=0
AF-AP-152 registry-rows=1 hook-mentions=0
AF-AP-153 registry-rows=1 hook-mentions=0
AF-AP-175 registry-rows=1 hook-mentions=0
AF-AP-177 registry-rows=1 hook-mentions=0
$ grep -n -E '^AP_SCREEN|^TEST_SCREEN|^_AF_AP_139 = \(|def pyflakes_delta|def main\(' .claude/hooks/edit-snapshot.py
65:_AF_AP_139 = (
78:AP_SCREEN = [
232:TEST_SCREEN = [
327:def pyflakes_delta(fp: str, src: str) -> list[str]:
435:def main() -> int:
$ grep -n -E 'def parse_classes|def main\(' scripts/vendored_manifest.py
574:def parse_classes(text: str) -> dict[str, str]:
1153:def main(argv: list[str] | None = None) -> int:
$ grep -n -E 'AF-AP-138 baseline control|def test_required_mutants_are_killed|def run_killer' tests/test_vendored_manifest.py
1132:def run_killer(killer: str, module, work: Path, label: str) -> None:
1273:def test_required_mutants_are_killed(
1285:    # AF-AP-138 baseline control: the killer runs on the UNMUTATED module first and must pass there. A killer that
$ grep -n -E '^def test_' tests/test_edit_snapshot_ap_screen.py
422:def test_af_ap_80_flags_source_text_pins_and_spares_behavioral_asserts():
597:def test_pyflakes_delta_is_empty_when_the_venv_probe_raises(monkeypatch, tmp_path):
612:def test_pyflakes_delta_is_empty_when_running_the_venv_python_raises(monkeypatch, tmp_path):
$ grep -n -i 'inline equivalent: derive the' .claude/skills/deep-work/SKILL.md
195:  wrinkle or weird pattern — run `/bug-echo` (or its inline equivalent: derive the
$ grep -n 'scripts/hooks/pre-commit. (pyflakes DELTA' .claude/skills/build-loop/SKILL.md
81:   `scripts/hooks/pre-commit` (pyflakes DELTA vs HEAD on staged .py — NEW hits block; the
$ grep -n -E 'splitlines' scripts/no_laya_in_gates.py scripts/vendored_manifest.py | cut -c1-120
scripts/no_laya_in_gates.py:1249:    for line in text.splitlines():
scripts/no_laya_in_gates.py:1299:        for line in r.stdout.splitlines():
scripts/no_laya_in_gates.py:1443:        for lineno, line in enumerate(content.splitlines(), 1):
scripts/vendored_manifest.py:402:    lines = data.decode("utf-8").splitlines()
scripts/vendored_manifest.py:477:        for line_number, line in enumerate(text.splitlines(), start=1):
scripts/vendored_manifest.py:575:    lines = text.splitlines()
scripts/vendored_manifest.py:653:    lines = path.read_text(encoding="utf-8").splitlines()
scripts/vendored_manifest.py:759:    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), s
scripts/vendored_manifest.py:798:    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), s
scripts/vendored_manifest.py:1142:    expected_lines = expected.splitlines()
scripts/vendored_manifest.py:1143:    actual_lines = actual.splitlines()
$ grep -n -E 'merge-base.*--is-ancestor|is-ancestor' scripts/check-proof-status.py | cut -c1-120
164:    if _git(repo_root, "merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
$ grep -n -E 'in \{' scripts/decide-harvest harness-ports/bin/qwen_matrix.py | cut -c1-140
scripts/decide-harvest:434:            and headers[0].strip().lower() in {"#", "id"}
scripts/decide-harvest:686:            if not isinstance(block, dict) or block.get("type") != "tool_use" or block.get("name") not in {"Agent
scripts/decide-harvest:691:            if role in {"hive-scout", "hive-reviewer"}:
harness-ports/bin/qwen_matrix.py:166:        if message["role"] in {"user", "tool"}:
harness-ports/bin/qwen_matrix.py:263:            and message.get("role") in {"system", "user", "assistant", "tool"}
$ ls tests/test_shell_syntax.py scripts/gate_files.txt scripts/hooks/pre-commit
scripts/gate_files.txt
scripts/hooks/pre-commit
tests/test_shell_syntax.py
```
