# K150 — the kit edits that waited for VERIFY-K1-h (task #150): eight skill bakes, four screen rows, two test controls, one hook fix

PIN: 033a9b0 (the shared tree's HEAD at authoring; every boundary file is byte-identical at origin f772bfc — premise below). LANE:
k150 (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation). Honey `ultra` Lever-2: your report is DATA:
files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

WHY. VERIFY-K1-h came home MERGE-READY-WITH-FOLLOWUPS (issue #60), so the `.claude/` tree is free again. Task #150 collected the
edits that had to wait: lessons from the registry (`docs/INCIDENT-LOG.md`, the ANTI-PATTERN REGISTRY table) that belong in the skills,
and screen rows that belong in the edit-snapshot hook. The rows are the evidence; READ each row named below before you write its rule,
and write the rule from the row, never from this brief's one-line summary.

## Items (the contract; each is DONE only with the evidence its line names)

SKILL BAKES. Each edit lands in `.claude/skills/<skill>/SKILL.md` AND in its twin `.agents/skills/<skill>/SKILL.md` (all three skills
are hand-ported: the twin carries Hermes/Codex wording, so port the change by hand in the twin's own words, never by copying the
`.claude` file over it). Keep each bake short: the rule, the one incident that proved it (date, lane or finding, AF-AP id), nothing more.
- (a) `build-loop`: the paragraph at `.claude/skills/build-loop/SKILL.md:78` ("A pushed head is green only when ITS CI run has been
  read") names the instrument: `scripts/ci_gate.py` (push_clean runs it; `--wait 1800` waits for a verdict).
- (d1) `anti-hollow-green`: AF-AP-139's rule.
- (l′) `anti-hollow-green`: AF-AP-162's rule — a test double for a remote command RUNS the command against a fake remote root that no
  local path matches, and never answers from the command's text; a lane that adds a case arm for its own new string has written the
  test's answer.
- (e) `orchestration`, section `## Parallel agents, liveness, coordinator economy` (`.claude/skills/orchestration/SKILL.md:241`):
  AF-AP-140's rule.
- (h) `orchestration`: AF-AP-155's brief-time grep (a lane's planned inputs recorded only in prose: grep the ledger and every
  PROVENANCE file for the lane's name at authoring).
- (i) `orchestration` 0d″ (`:59`): a verifier's PROPOSED FIX is a hypothesis too — before a brief adopts it, measure it against a
  control with a real value for each condition under which it SKIPS a redaction or a refusal (VERIFY-J1-1-R1's option B; AF-AP-153's
  class).
- (l) `orchestration` 0d′ (`:50`): a premise command's output carries no volatile field — strip pytest's ` in N.NNs` timing with `sed`
  inside the echoed command itself, never by hand, because a lane re-measures and stops CONTRACT-INVALID on any difference (VERIFY-J1-3's
  first stop; AF-AP-164).
- (k) `orchestration` 0f (`:84`): two partial-verify rules. A verify lane served entirely by a low-tier fallback with REASONED, not
  executed, mutants is a partial verify, and the landing stays GATED-PENDING-VERIFY (VERIFY-C2, issue #56). A MERGE-READY over un-run
  items is void: a partial verify's recommendation is never counted, and the completion verify grades the first pass claim by claim
  (VERIFY-J1-3's first pass, refuted by VERIFY-J1-3-R2; AF-AP-170).
- (j) `orchestration`, the recovery paragraph that contains "A container RESTART is the same shape" (`.claude/…/SKILL.md:429-435`): add
  the QUOTA STOP form — a lane killed by the sandbox's usage limit is never resumed in the sandbox; it continues on the PC with a
  continuation brief and a `LANE_PATCH` of its uncommitted work; a lane that died AFTER its final gates, with only a comment edit after
  them, is LANDED, not relaunched: prove the final blob AST-identical (docstrings kept) to the blob its gates ran on, re-run the gates,
  land it GATED-PENDING-VERIFY, and send the verify to the PC (S198A, 2026-09-23). Word the route neutrally (the PC's cloud route is
  suspended while D-061 holds). The `.agents` twin does not carry the recovery paragraph at all (premise: 0 matches): port the WHOLE
  paragraph plus the new form into the twin, in the twin's words.

SCREEN ROWS AND TESTS (`.claude/hooks/edit-snapshot.py` `AP_SCREEN` at `:63`; tests in `tests/test_edit_snapshot_ap_screen.py`). Each new
row cites its AF-AP id, and each gets a positive fixture (the row fires) and a negative fixture (a near miss that must not fire), in the
file's existing pattern. Read the row's "greppable signature" column first; if the registry's signature cannot be written as a line
pattern without flooding clean code, say so as a DISCREPANCY with the flood count measured over `scripts/ src/ proofs/ harness-ports/`.
- (d2) AF-AP-139's signature.
- (g) AF-AP-25's line-parser signature.
- (k′) AF-AP-162 and AF-AP-89's doubled escape: `\\$(` or `\\\"` inside a double-quoted `bridge "…"` or `scripts/pc.sh "…"` argument.
- (m) issue #57 F-2: the AF-AP-159 row gains a right-operand fixture (`2 + node.start_mark.line`); if the row does not fire on it and the
  registry row's scope includes that form, widen the row and say so; if the scope excludes it, say why and add the fixture as a negative.

HOOK FIX AND MANIFEST CONTROL
- (f) AF-AP-44, the hook instance: in a bare PC shell with no `AF_VENV`, `pyflakes_delta` (`.claude/hooks/edit-snapshot.py:297`) crashed
  on a `PermissionError` while probing `/root`, and three harness suites went red (the ledger note of 2026-09-23 09:1xZ). The function's
  own contract is "a tell, never a blocker": every probe failure returns `[]`. Fix it at its root (find every probe of the venv path in
  the hook, not only the one that crashed) and add a test that raises `PermissionError` from the probe and asserts `[]`, RED before your
  fix and GREEN after.
- (b) AF-AP-138's baseline control in `tests/test_vendored_manifest.py`: each mutation test runs its killing check on the UNMUTATED
  module first and asserts it passes, so a kill cannot come from a broken harness. Read the row, then the file's mutant tests.

OUT OF SCOPE: issue #57 F-1 (a docstring in `scripts/no_laya_in_gates.py`, which rides with the next J1-0 touch); task #183.

## Order and twins (load-bearing)

1. Edit the `.claude` files. 2. Port each skill change into `.agents/skills/<skill>/SKILL.md`. 3. `bash harness-ports/bin/sync-skills.sh
--record` (refreshes the hand-port base hashes), then `--check` (rc 0). 4. `bash harness-ports/bin/sync-lane-skills.sh` (copies the three
twins into `.agents/lane-skills/`), then `--check` (rc 0). 5. `python3 scripts/vendored_manifest.py --write`, then `--check` (PASS). Paste
the diff of `sandbox-kit/VENDORED-MANIFEST.md` and `sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv`; a class that changes is a DISCREPANCY to
explain (all four `.claude` files are `kit-adapted` at the PIN).

## Gates (paste every command with its output)

- `/root/venv-agent-factory/bin/python -m pytest tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py -q -p no:cacheprovider`
  twice; the counts must agree (the PIN: `152 passed`, set `2a60fb528bf2`); your new tests add to it.
- `/root/venv-agent-factory/bin/python -m pytest tests/test_hooks_worktree.py -q -p no:cacheprovider` once.
- `bash harness-ports/tests/run-all.sh` once (the harness suites, including the mirror gate); paste its last lines.
- `/root/venv-agent-factory/bin/python -m pyflakes .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py`
- `python3 scripts/no_laya_in_gates.py` (the hook is a listed gate file; exit 0).
- `python3 scripts/ap_screen.py .claude/hooks/edit-snapshot.py` (the hook screens itself: list any new hit your rows cause in it).
- For each new screen row: the count of lines it fires on across `scripts/ src/ proofs/ harness-ports/` at your final tree, pasted.

## Boundary and standing do-nots

MODIFY ONLY: `.claude/skills/{build-loop,anti-hollow-green,orchestration}/SKILL.md`, their `.agents/skills/` and `.agents/lane-skills/`
twins, `.claude/hooks/edit-snapshot.py`, `tests/test_edit_snapshot_ap_screen.py`, `tests/test_vendored_manifest.py`,
`harness-ports/hand-ported.sha256` (through `--record` only), `sandbox-kit/VENDORED-MANIFEST.md` and `sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv`
(through `--write` only). CREATE `tasks/briefs/kit-k1-support/K150-report.md` (write it incrementally from the start). READ-ONLY:
everything else, including `docs/INCIDENT-LOG.md` (the coordinator owns it), `CLAUDE.md`, `AGENTS.md`, `.hermes.md`. Report adjacent
defects; never fix them. Never run git add, commit, stash, checkout, restore, reset or clean in the shared tree: mutants and red runs go
in a scratch copy (`git archive HEAD | tar -x -C /tmp/k150/work`). No PC or bridge use. Take no outward-facing action. Paste every count
and timestamp from command output. Long gates in ONE foreground call. A deviation from any line above is STOP-and-report.

## Report (`tasks/briefs/kit-k1-support/K150-report.md`)

DATA: per item (a)-(m) the file:line of each change and the registry row it came from; the RED→GREEN pair per new test; the screen
rows' fire counts; the twin and manifest steps with their outputs; the gate outputs; DISCREPANCIES; NOT-done.
`python3 scripts/report_lint.py --min-refs 15 tasks/briefs/kit-k1-support/K150-report.md` (at most three fix rounds, then paste and
finish).

## PREMISE — MEASURED at authoring (2026-09-24 01:34Z, /home/user/agent-factory@033a9b0; generated by `scripts/premise_block.sh`, every command echoed exactly as it ran)
```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short HEAD; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
2026-09-24T01:34Z
033a9b0
f772bfc
$ git status --short -- .claude .agents harness-ports tests sandbox-kit scripts | wc -l
0
$ for f in .claude/skills/build-loop/SKILL.md .agents/skills/build-loop/SKILL.md .claude/skills/anti-hollow-green/SKILL.md .agents/skills/anti-hollow-green/SKILL.md .claude/skills/orchestration/SKILL.md .agents/skills/orchestration/SKILL.md .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py; do echo "$(git rev-parse HEAD:$f | cut -c1-12) $(wc -l < $f) $f"; done
b33bb80b73ee 276 .claude/skills/build-loop/SKILL.md
db4f9e65a4f5 279 .agents/skills/build-loop/SKILL.md
e6438ca6442c 281 .claude/skills/anti-hollow-green/SKILL.md
58a351bc0f33 270 .agents/skills/anti-hollow-green/SKILL.md
2315dc9f5723 547 .claude/skills/orchestration/SKILL.md
ed3c231ce795 536 .agents/skills/orchestration/SKILL.md
b52a0d8ab536 481 .claude/hooks/edit-snapshot.py
d7448f51bb89 489 tests/test_edit_snapshot_ap_screen.py
74b02f869df5 1246 tests/test_vendored_manifest.py
$ for s in build-loop anti-hollow-green orchestration; do cmp -s .agents/skills/$s/SKILL.md .agents/lane-skills/$s/SKILL.md && echo "$s: twins identical"; grep -qx $s harness-ports/hand-ported.txt && echo "$s: hand-ported"; grep -qx $s harness-ports/lane-skills.txt && echo "$s: in lane-skills.txt"; done
build-loop: twins identical
build-loop: hand-ported
build-loop: in lane-skills.txt
anti-hollow-green: twins identical
anti-hollow-green: hand-ported
anti-hollow-green: in lane-skills.txt
orchestration: twins identical
orchestration: hand-ported
orchestration: in lane-skills.txt
$ bash harness-ports/bin/sync-skills.sh --check > /dev/null; echo "sync-skills --check rc=$?"
sync-skills --check rc=0
$ bash harness-ports/bin/sync-lane-skills.sh --check > /dev/null; echo "sync-lane-skills --check rc=$?"
sync-lane-skills --check rc=0
$ python3 scripts/vendored_manifest.py --check
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
$ grep -n -E 'skills/(orchestration|anti-hollow-green|build-loop)/SKILL.md|hooks/edit-snapshot.py' sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv
41:hooks/edit-snapshot.py	kit-adapted
350:skills/anti-hollow-green/SKILL.md	kit-adapted
501:skills/build-loop/SKILL.md	kit-adapted
1827:skills/orchestration/SKILL.md	kit-adapted
$ grep -n -E '^\*\*A pushed head is green' .claude/skills/build-loop/SKILL.md | cut -c1-120
78:**A pushed head is green only when ITS CI run has been read (2026-09-06, checkpoints 4-5).** Local summaries prove th
$ grep -n -E '^   \*\*0d′|^   \*\*0d″|^0f\. |^## Parallel agents, liveness|A container RESTART is the same' .claude/skills/orchestration/SKILL.md | cut -c1-110
50:   **0d′ — EVERY premise is a MEASUREMENT pasted at authoring (2026-09-22; three stale premises in one 
59:   **0d″ — a flip or mutant the brief DEMANDS a result of is RUN at authoring (2026-09-22, VERIFY-B67 i
84:0f. **Coordinator re-execution of a builder's gate is NOT independent verification (audit
241:## Parallel agents, liveness, coordinator economy
429:re-dispatch ONLY the residual — never a fresh full brief. **A container RESTART is the same
$ grep -c 'RESTART is the same' .agents/skills/orchestration/SKILL.md
0
[rc=1]
$ grep -n -E '^AP_SCREEN = \[|^def pyflakes_delta|^def _pyflakes_msgs' .claude/hooks/edit-snapshot.py
63:AP_SCREEN = [
284:def _pyflakes_msgs(py: str, text: str) -> dict:
297:def pyflakes_delta(fp: str, src: str) -> list[str]:
$ for n in 25 44 89 138 139 140 153 155 159 162 164 170; do printf 'AF-AP-%s: registry rows %s, hook lines naming it %s\n' $n "$(grep -c "^| AF-AP-$n |" docs/INCIDENT-LOG.md)" "$(grep -c -E "AF-AP-$n\b" .claude/hooks/edit-snapshot.py)"; done
AF-AP-25: registry rows 1, hook lines naming it 0
AF-AP-44: registry rows 1, hook lines naming it 3
AF-AP-89: registry rows 1, hook lines naming it 0
AF-AP-138: registry rows 1, hook lines naming it 0
AF-AP-139: registry rows 1, hook lines naming it 0
AF-AP-140: registry rows 1, hook lines naming it 0
AF-AP-153: registry rows 1, hook lines naming it 0
AF-AP-155: registry rows 1, hook lines naming it 0
AF-AP-159: registry rows 1, hook lines naming it 3
AF-AP-162: registry rows 1, hook lines naming it 0
AF-AP-164: registry rows 1, hook lines naming it 0
AF-AP-170: registry rows 1, hook lines naming it 0
$ /root/venv-agent-factory/bin/python -m pytest tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py -q -p no:cacheprovider 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
152 passed
$ bash scripts/pc_suite.sh set-id -- tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py
2 files set=2a60fb528bf2
```
