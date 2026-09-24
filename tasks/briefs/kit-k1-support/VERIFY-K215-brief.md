# VERIFY-K215 — the independent verify of the registry's owed screens and bakes (task #219 verifies tasks #215 and #218)

PIN: bfe66ec (the post-push commit that carries K215's landing and the coordinator's anti-hollow-green bake; every boundary file is
byte-identical at the shared tree's HEAD — premise below). ROLE: adversarial-verifier (sandbox, Opus 5.5, the SHARED tree read-only,
no worktree isolation). Honey `full`. Do NOT spawn subagents.

## Why this lane exists

K215 (a sandbox Opus 5.5 build lane) added eight AP_SCREEN rows to `.claude/hooks/edit-snapshot.py` (AF-AP-132, 141, 144, 145, 149,
152, 175, 177), two new screen classes (`_PathScoped`, `_ExitTrapCleanup`), three skill bakes (AF-AP-150 deep-work, AF-AP-151
build-loop, AF-AP-153 anti-hollow-green 3e) and five VERIFY-K150 follow-ups (F-03, F-04, F-06, F-07, F-08), with ten DISCREPANCIES
(D-1..D-10). The coordinator then baked two more rules into anti-hollow-green (task #218: tactic 2(g) for AF-AP-179 and 3f, "a measured
zero states its generator's alphabet"), marked eleven registry rows LANDED, and added a CLAUDE.md quirk line from K215's tooling finding.
The only gates so far are the builder's and the coordinator's re-run of the builder's own tests (`226 passed`, set 2a60fb528bf2): a
second run of the builder's oracle, not a verify (orchestration rule 0f). You are the independent hostile pass: attack each contract
line with shapes the builder did not write, reproduce its load-bearing claims, and grade its deviations.

## Read in this order

1. The contract: `tasks/briefs/kit-k1-support/K215-brief.md` (§Items, §Gates, §Boundary).
2. The builder's report: `tasks/briefs/kit-k1-support/K215-report.md` (claims to reproduce, never to trust; D-1..D-10 and NOT-done at
   its end).
3. The registry rows each item cites, in `docs/INCIDENT-LOG.md` (AF-AP-89, -132, -138, -139, -141, -144, -145, -149, -150, -151, -152,
   -153, -175, -177, -179), read at the PIN (`git show bfe66ec:docs/INCIDENT-LOG.md`), and the 2026-09-24 06:1xZ incident entry
   (the source of the 3f bake).
4. The code: `.claude/hooks/edit-snapshot.py` (`_PathScoped`, `_ExitTrapCleanup`, `AP_SCREEN`, `TEST_SCREEN`, `pyflakes_delta`, `main`),
   `tests/test_edit_snapshot_ap_screen.py`, `tests/test_vendored_manifest.py`, and the READ-ONLY consumers `scripts/ap_screen.py`,
   `scripts/lint_delta.py`, `scripts/lane_context.sh`.
5. The skills at the PIN: `.claude/skills/{deep-work,build-loop,anti-hollow-green}/SKILL.md`, their `.agents/skills/` twins and
   `.agents/lane-skills/` copies; `harness-ports/hand-ported.sha256`.

## Items (each with the command you ran and its output pasted)

1. PREMISE: re-run the block below (`bash scripts/premise_block.sh < <file of its commands>` in the shared tree) and compare line by
   line; stop CONTRACT-INVALID on any difference you cannot explain.
2. SCREEN ROWS, one sub-section per row (AF-AP-132, 141, 144, 145, 149, 152, 175, 177): (i) does it fire on every instance its registry
   row names (paste the line and the hit); (ii) NEW near misses the builder's fixtures do not cover — other spellings of the same class
   that it MISSES (a false negative is a finding when the registry's scope includes that spelling) and clean code it WRONGLY fires on;
   (iii) its fire count over `scripts/ src/ proofs/ harness-ports/ .claude/hooks/` at the PIN, each hit classified true or false (the
   builder's section-7 counts are claims to re-measure). The builder declared gaps (D-2, D-3, D-4, D-9, D-10 and NOT-done): grade each
   one — an acceptable, documented limit, or a hole the contract did not allow.
3. THE TWO NEW CLASSES. `_PathScoped` (AF-AP-144): the scope is applied only in the hook's `main`; `scripts/ap_screen.py` and
   `scripts/lint_delta.py` pass no path, so the row never fires there (D-3(b)). The pre-commit hook runs `lint_delta.py`: measure whether
   AF-AP-144 can EVER fire at commit time, and grade that against the contract's "if only a path-scoped line pattern is possible, scope it
   and say so". Attack the path test with the path shapes `main` really receives (absolute, relative, a `proofs/<id>/check_*.py` under a
   worktree or a scratch copy, a nested `proofs/x/tools/check_y.py`). `_ExitTrapCleanup` (AF-AP-145): the builder claims linear cost
   (a lookahead version took 0.68 s on 2,000 definitions) and that it sees a trap placed above its function. Time it on your own hostile
   texts (tens of thousands of definitions, one very long line, many traps) and attack its correctness with shell forms the fixtures do
   not use: `function name {`, `name ()` with a space, a trap naming two functions, `trap -- 'cleanup' EXIT`, a quoted handler with
   arguments, a handler that opens with a comment line before the ignore, a `trap '' INT TERM` that appears after other commands. For
   BOTH classes: list every place that iterates `AP_SCREEN` or `TEST_SCREEN` (the hook, `scripts/ap_screen.py`, `scripts/lint_delta.py`,
   the harness-ports adapters, any test) and show that each consumer calls only methods the class implements — a consumer that calls
   another method on a row object crashes on these rows.
4. F-06 (AF-AP-139 widened to `-> None` and the ten 2xx `HTTPStatus` members): reproduce the two new positives and the new negative; try
   one spelling inside the registry's scope the widening still misses. D-8's list (the message argument, delegation, an alias,
   `send_response_only`, bodies over 1,000 characters) is declared out of this contract: confirm it is recorded, do not grade it.
5. F-03 (AF-AP-138, `assert_mutant_killed`): show that the moved harness body is unchanged apart from `run_killer(` → `run(`
   (`git show` both versions, diff them), that `test_required_mutants_are_killed` still kills every required mutant, and that a hollow
   killer (one that fails on the unmutated module) is refused by the new row
   `test_af_ap_138_control_refuses_a_killer_that_fails_on_the_unmutated_module`. Build the hollow killer yourself in a scratch copy.
6. F-07 (three `pyflakes_delta` controls) and F-08 (two manifest refusal rows): for each, a mutant of the guarded code that the control
   must kill, run in a scratch copy. Reproduce D-1 (the absent-venv control cannot red under the `PermissionError`-narrowing mutant, and
   reds under VERIFY-K150's K16 mutant).
7. SKILL BAKES. K215's three (AF-AP-150 deep-work, AF-AP-151 build-loop, AF-AP-153 anti-hollow-green 3e) and the coordinator's two
   (anti-hollow-green 2(g) and 3f). For each: the text at the PIN against its registry row or incident entry (the rule AND its facts —
   dates, lanes, AF-AP ids, numbers; a bake that misstates its incident is a finding). The twins: each `.agents/skills/` copy carries the
   rule in its own wording (a byte copy of the `.claude` text is a finding) and says nothing the `.claude` text does not; each
   `.agents/lane-skills/` copy equals its twin (`sync-lane-skills.sh --check`). `harness-ports/hand-ported.sha256`: `--record` rewrites
   the base hash of EVERY hand-ported skill, so show that the PIN's file differs from the pre-K215 file only on the three K215 skills and
   that anti-hollow-green's line moved once more for #218 (`git log -p` on the file) — a masked drift in any other skill is a finding.
   2(g) makes checkable claims about Python: run each in a scratch directory with a `sitecustomize.py` blocker on `PYTHONPATH` and paste
   the result — a child started with `-I`, with `-S`, with `-E`, or with an `env=` that drops `PYTHONPATH` escapes it; a `sys.meta_path`
   finder sees `importlib.import_module`; a `builtins.__import__` hook does not.
8. THE LEDGER-PLANE CHANGES. (a) The eleven registry rows that now say LANDED (grep `task #215` at the PIN): each LANDED claim matches what
   landed (for example AF-AP-144's "path-scoped, without the main and reader conditions", AF-AP-153's "no screen line", AF-AP-175's "LINE
   form"). (b) The CLAUDE.md quirk line (the Edit and Write tools turn a typed U+2028/U+2029 escape into the literal bytes): you have the
   Write tool — reproduce or refute the quirk with a scratch file (type the two escapes and `\u0085`, then read the bytes back with
   `od -c` or Python), and run the line's byte check on a file with a separator and on one without.
9. YOUR MUTANTS: at least ten across the changed code (each new row's regex, `_PathScoped`, `_ExitTrapCleanup`, the scope lines in
   `main`, the F-06 widening), each through the real test files in a scratch copy, each KILLED by a named test or reported as a SURVIVOR
   finding. A mutant must compile and be collected (AF-AP-78); paste the assertion line of each kill.
10. REGEX COST: for each new row, a hostile text you designed for that row (AF-AP-152's class: a long run of what a quantified class
    matches, without the terminator; a line of 100,000 characters; 50,000 lines) and its time. The builder's worst row was 0.0271 s
    (AF-AP-177) on texts up to 160,000 characters; a row over 1 s on a text a real file could hold is a finding.
11. GATES at the PIN, in a private clone: the two test files twice (counts agree; `226 passed`, set 2a60fb528bf2);
    `tests/test_hooks_worktree.py` once; `bash harness-ports/tests/run-all.sh` once (its last lines); pyflakes on the three code files;
    `python3 scripts/no_laya_in_gates.py`; `python3 scripts/ap_screen.py .claude/hooks/edit-snapshot.py` (the builder: 20 hits);
    `python3 scripts/vendored_manifest.py --check`; `bash harness-ports/bin/sync-skills.sh --check`.
12. ADJACENT CONSUMERS: `scripts/ap_screen.py` and `scripts/lint_delta.py` load the hook in-process; `scripts/lane_context.sh`'s screen
    section runs `ap_screen.py`; the pre-commit hook runs `lint_delta.py`. Show each still runs on a real file at the PIN (rc and first
    lines). In the private clone (never the shared tree), stage a small change that holds one instance of each new row's class and run the
    pre-commit screen the way the hook runs it: which rows fire at commit time and which cannot. Show that no new row raises on any file
    under `scripts/ src/ proofs/ harness-ports/ tests/ .claude/hooks/` (a compile error or an exception is a finding).

## Venue and boundary

- Scratch: `/tmp/vk215/`. A private clone at the PIN when a command needs a repository: `git clone -q --shared /home/user/agent-factory
  /tmp/vk215/clone && git -C /tmp/vk215/clone checkout -q --detach bfe66ec` (about 600 MB of working tree; the sandbox had 2.4 GB free at
  authoring; one clone at a time; remove it at the end). Run pytest from the clone's root (its pyproject puts `src` first); commits in the private clone are allowed, never in
  the shared tree.
- Python: `/root/venv-agent-factory/bin/python`; pytest `-p no:cacheprovider --basetemp=/tmp/vk215/bt<n>` (make the parent first).
  pytest-xdist is not installed: run serially, never `-n`. `bash scripts/pc_suite.sh set-id -- <files>` works here; no other pc_* script,
  no bridge.
- CREATE only `tasks/briefs/kit-k1-support/VERIFY-K215-report.md` (write it incrementally from the start). Never edit anything else in
  the repository. No other sandbox agent is live at authoring; a PC lane (VERIFY-J1-45) runs over the bridge, which you never use.
  Never run `git stash`, `checkout`, `restore`, `add`, `commit`, `worktree` or `push` in the shared tree. No outward-facing action.
  Never read `~/.hermes/`.
- CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
  `scripts/lane_context.sh -q 'how does the edit-snapshot hook screen an edited file, and which consumers iterate AP_SCREEN' -s main -s _PathScoped -s _ExitTrapCleanup -o /tmp/vk215/pack.md .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py scripts/ap_screen.py scripts/lint_delta.py`.

PREDICATE: a finding blocks only if it is contract-mapped (the K215 brief's items, the registry row a screen or bake cites, or the #218
bake's source rows), reproduced on the real path, materially effective (a row that never fires where its class lives when the contract
required it to, a row that floods clean code, a screen or consumer crash, a mutation or control whose kill is hollow, a bake that states
a false fact, a masked twin drift), with a concrete discriminator, and in-boundary. Report EVERY meaningful observation, with no
severity filter, then apply the predicate. Emit ONE `GATE RECOMMENDATION:` line — `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` /
`NOT-READY` / `CONTRACT-INVALID`. The coordinator owns the gate.

Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/kit-k1-support/VERIFY-K215-report.md --root .`; apply its
`fix:` hints for at most three rounds, then paste and finish. The report ends with DISCREPANCIES and NOT-done, and states which items
you ran fully, partly or not at all (AF-AP-170: a recommendation over un-run items is void).

## PREMISE — MEASURED at authoring (2026-09-24 06:4xZ, sandbox, uid 0; generated by `scripts/premise_block.sh`, every command echoed exactly as it ran)
```
$ git rev-parse --short 'bfe66ec^{commit}'
bfe66ec
$ git merge-base --is-ancestor bfe66ec origin/claude/soundbox-kit-migration-iz1jwf && echo pin-is-on-origin
pin-is-on-origin
$ git log --format='%h %s' -3 bfe66ec | cut -c1-110
bfe66ec anti-hollow-green bake (task #218): AF-AP-179's closure rule as tactic 2(g) and "a measured zero state
b318135 K215 landed (task #215, GATED-PENDING-VERIFY): the owed AP_SCREEN rows and three skill bakes; registry
ef21f88 VERIFY-J1-1-R3 home: NOT-READY (two leaks, reproduced); D-067 void, no revert; the redaction pass goes
$ git diff --quiet bfe66ec HEAD -- .claude/hooks/edit-snapshot.py .claude/skills/deep-work .claude/skills/build-loop .claude/skills/anti-hollow-green .agents/skills/deep-work .agents/skills/build-loop .agents/skills/anti-hollow-green .agents/lane-skills harness-ports/hand-ported.sha256 sandbox-kit/VENDORED-MANIFEST.md sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py scripts/ap_screen.py scripts/lint_delta.py scripts/vendored_manifest.py CLAUDE.md && echo boundary-identical-to-pin || echo BOUNDARY-CHANGED-SINCE-PIN
boundary-identical-to-pin
$ git ls-tree bfe66ec -- .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py scripts/ap_screen.py scripts/lint_delta.py .claude/skills/anti-hollow-green/SKILL.md .agents/skills/anti-hollow-green/SKILL.md harness-ports/hand-ported.sha256 | awk '{print substr($3,1,12), $4}'
48961572d31b .agents/skills/anti-hollow-green/SKILL.md
b2d45cd607a4 .claude/hooks/edit-snapshot.py
b7be8931bafd .claude/skills/anti-hollow-green/SKILL.md
07fb493f2776 harness-ports/hand-ported.sha256
eb20dde7e198 scripts/ap_screen.py
1f16b01f1923 scripts/lint_delta.py
192bef4da9c1 tests/test_edit_snapshot_ap_screen.py
f7eee9a93c0c tests/test_vendored_manifest.py
$ /root/venv-agent-factory/bin/python -m pytest tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py -q -p no:cacheprovider 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*$//'
226 passed
$ bash scripts/pc_suite.sh set-id -- tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py
2 files set=2a60fb528bf2
$ python3 scripts/vendored_manifest.py --check 2>&1 | tail -1
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
$ bash harness-ports/bin/sync-skills.sh --check >/dev/null 2>&1; echo sync-skills-check rc=$?
sync-skills-check rc=0
$ bash harness-ports/bin/sync-lane-skills.sh --check >/dev/null 2>&1; echo sync-lane-skills-check rc=$?
sync-lane-skills-check rc=0
$ grep -n -E 'class _PathScoped|class _ExitTrapCleanup|\("AF-AP-(132|141|144|145|149|152|175|177)"|isinstance\(rx, _PathScoped\)|^def main|^AP_SCREEN|^TEST_SCREEN|^def pyflakes_delta' .claude/hooks/edit-snapshot.py | cut -c1-90
76:class _PathScoped:
95:class _ExitTrapCleanup:
122:AP_SCREEN = [
273:    ("AF-AP-132", re.compile(r"""\benumerate\(\s*[^\n]*?\.splitlines\(\)|^[ \t]*(\w+)[
280:    ("AF-AP-141", re.compile(r"""^(?=[^\n]*?(?:["']--is-ancestor["']|["']cat-file["'][
289:    ("AF-AP-144", _PathScoped(re.compile(r"""(?:^|/)proofs/[^/]+/check_[^/]+\.py$"""),
301:    ("AF-AP-145", _ExitTrapCleanup(),
308:    ("AF-AP-149", re.compile(r"""-----BEGIN (?=[^\n]*?(?:\.\*|\.\+|\[\\s\\S\]|\[A-Z|\[
316:    ("AF-AP-152", re.compile(r"""\(\?:[^()\n]*?(?:\[(?!\^)[^\]\n]*?([\w-])[^\]\n]*\][*
327:    ("AF-AP-175", re.compile(r"""["']HEAD(?=["':^~@{])"""),
337:    ("AF-AP-177", re.compile(r"""^(?=[^\n]*?\.get\()(?![^\n]*\bisinstance\([^\n]*?,[ \
351:TEST_SCREEN = [
446:def pyflakes_delta(fp: str, src: str) -> list[str]:
554:def main() -> int:
617:        if isinstance(rx, _PathScoped):  # only here is the edited file's path known
$ grep -n -E '^class TestAFAP|def test_af_ap_144_the_hook_applies|def test_pyflakes_delta_is_empty_when|def test_fires_on_a_handler_annotated|def test_fires_on_an_http_status|def test_no_fire_on_a_handler_that_always' tests/test_edit_snapshot_ap_screen.py | cut -c1-100
29:class TestAFAP33:
48:class TestAFAP34:
66:class TestAFAP35:
81:class TestAFAP36:
97:class TestAFAP37:
116:class TestAFAP38:
142:class TestAFAP39:
172:class TestAFAP40:
204:class TestAFAP41:
222:class TestAFAP43:
241:class TestAFAP44:
256:class TestAFAP45:
284:class TestAFAP55:
302:class TestAFAP57:
331:class TestAFAP58:
349:class TestAFAP59:
370:class TestAFAP70:
391:class TestAFAP71:
409:class TestAFAP72:
441:class TestAFAP115:
462:class TestAFAP127:
480:class TestAFAP159:
516:class TestAFAP139:
541:    def test_fires_on_a_handler_annotated_to_return_none(self):
545:    def test_fires_on_an_http_status_member(self):
549:    def test_no_fire_on_a_handler_that_always_refuses(self):
557:class TestAFAP25:
587:class TestAFAP89:
610:class TestAFAP132:
655:class TestAFAP141:
681:class TestAFAP144:
718:def test_af_ap_144_the_hook_applies_the_path_scope(monkeypatch, capsys, tmp_path):
753:class TestAFAP145:
781:class TestAFAP149:
807:class TestAFAP152:
832:class TestAFAP175:
864:class TestAFAP177:
898:def test_pyflakes_delta_is_empty_when_the_venv_probe_raises(monkeypatch, tmp_path):
913:def test_pyflakes_delta_is_empty_when_running_the_venv_python_raises(monkeypatch, tmp_path):
933:def test_pyflakes_delta_is_empty_when_the_venv_path_is_too_long(monkeypatch, tmp_path):
949:def test_pyflakes_delta_is_empty_when_the_venv_python_times_out(monkeypatch, tmp_path):
966:def test_pyflakes_delta_is_empty_when_the_venv_is_absent(monkeypatch, tmp_path):
$ grep -n -E 'def assert_mutant_killed|def test_required_mutants_are_killed|def test_af_ap_138_control_refuses|bad-header|extra-cell' tests/test_vendored_manifest.py | cut -c1-100
662:        ("bad-header", lambda lines: (1, ["path\tKLASS", *lines[1:]])),
664:        ("extra-cell", lambda lines: (2, [lines[0], lines[1] + "\textra", *lines[2:]])),
1276:def assert_mutant_killed(tmp_path: Path, mutant_name: str, mutate, killer: str, run=run_killer)
1305:def test_required_mutants_are_killed(
1314:def test_af_ap_138_control_refuses_a_killer_that_fails_on_the_unmutated_module(tmp_path: Path) 
$ python3 scripts/ap_screen.py .claude/hooks/edit-snapshot.py 2>&1 | head -1
--- AP_SCREEN over 1 path(s): 20 hits over 1 files ---
$ python3 scripts/ap_screen.py --limit 100000 $(git ls-files scripts src proofs harness-ports .claude/hooks) 2>&1 | grep -E '^--- |^AF-AP-(132|139|141|144|145|149|152|175|177):'
--- AP_SCREEN over 960 path(s): 385 hits over 960 files ---
AF-AP-132: 13
AF-AP-175: 12
AF-AP-145: 7
AF-AP-141: 5
AF-AP-177: 4
AF-AP-139: 1
AF-AP-152: 1
$ grep -c 'task #215' docs/INCIDENT-LOG.md
11
$ grep -n -E '^   \*\*\(g\) A "runs without X"|^   \*\*3e\. |^   \*\*3f\. ' .claude/skills/anti-hollow-green/SKILL.md | cut -c1-90
50:   **(g) A "runs without X" closure blocks X in EVERY process of the run and counts ATT
104:   **3e. A rewrite of a parser, lexer or screen keeps every refusal the old version ma
111:   **3f. A measured zero states its generator's alphabet (VERIFY-J1-1-R3, 2026-09-24; 
$ git log --format='%h %s' -3 -- harness-ports/hand-ported.sha256 | cut -c1-100
bfe66ec anti-hollow-green bake (task #218): AF-AP-179's closure rule as tactic 2(g) and "a measured 
b318135 K215 landed (task #215, GATED-PENDING-VERIFY): the owed AP_SCREEN rows and three skill bakes
f83aa36 Kit: AF-AP-171 baked into orchestration (task #211); evidence-gatherer re-pinned to Opus 5.5
$ df -h /tmp | tail -1
/dev/vda        252G   35G  2.4G  94% /
```
