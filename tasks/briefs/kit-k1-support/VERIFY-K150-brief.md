# VERIFY-K150 — the independent verify of the deferred kit edits (task #213 verifies task #150)

PIN: 656ddf6 (the post-push commit of the K150 landing; every boundary file is byte-identical at the shared tree's HEAD — premise
below). ROLE: adversarial-verifier (sandbox, Opus 5.5, the SHARED tree read-only, no worktree isolation). Honey `full`. Do NOT spawn
subagents.

## Why this lane exists

K150 (a sandbox Opus 5.5 build lane) landed eight skill bakes, four anti-pattern screen rows, one hook fix and three test controls,
with ten DISCREPANCIES (D-1..D-10), one of them a deviation by addition (D-5) and one a hollow mutant kill it found and fixed (D-10).
The coordinator re-ran the lane's own gates (`173 passed`, set 2a60fb528bf2); that is a second run of the builder's oracle, not a
verify (orchestration rule 0f). You are the independent hostile pass: attack each contract line with shapes the builder did not
write, reproduce its load-bearing claims, and grade its deviations.

## Read in this order

1. The contract: `tasks/briefs/kit-k1-support/K150-brief.md` §Items (a)-(n), §Order and twins, §Gates, §Boundary.
2. The builder's report: `tasks/briefs/kit-k1-support/K150-report.md` (claims to reproduce, never to trust; D-1..D-10 at its end).
3. The registry rows each item cites, in `docs/INCIDENT-LOG.md` (AF-AP-25, -44, -89, -138, -139, -140, -153, -155, -159, -162, -164,
   -170), read at the PIN (`git show 656ddf6:docs/INCIDENT-LOG.md`).
4. The code: `.claude/hooks/edit-snapshot.py` (`AP_SCREEN`, `TEST_SCREEN`, `pyflakes_delta`, `main`), `tests/test_edit_snapshot_ap_screen.py`,
   `tests/test_vendored_manifest.py`, and the READ-ONLY `scripts/vendored_manifest.py` and `scripts/ap_screen.py`.

## Items (each with the command you ran and its output pasted)

1. PREMISE: re-run the block below (`bash scripts/premise_block.sh < <file of its commands>` in the shared tree) and compare line by
   line; stop CONTRACT-INVALID on any difference you cannot explain.
2. SKILL BAKES (a), (d1), (l′), (e), (h), (i), (l), (k), (j): for each, the changed text at the PIN against the contract line (the rule
   AND its incident: date, lane or finding, AF-AP id). The twins: each `.agents/skills/<skill>/SKILL.md` carries the change in the
   twin's own Hermes/Codex wording (a byte copy of the `.claude` text is a finding); `.agents/lane-skills/` equals its twin
   (`sync-lane-skills.sh --check`); (j)'s whole recovery paragraph is in the `.agents` twin. Check each cited fact against its
   primary source (a bake that misstates its incident is a finding). D-1 and D-4 are the builder's citation notes: grade them.
3. SCREEN ROWS (d2) AF-AP-139, (g) AF-AP-25, (k′) AF-AP-89/162, (m) AF-AP-159: for each row, at the PIN, (i) does it fire on every
   instance the registry row names (paste the line and the hit); (ii) NEW near-misses the builder's fixtures do not cover — other
   spellings of the same class that it MISSES (a false negative is a finding when the registry's scope includes that spelling) and
   clean code it WRONGLY fires on; (iii) its fire count over `scripts/ src/ proofs/ harness-ports/` (and over `tests/` for a
   `TEST_SCREEN` row), each hit classified true or false positive. The builder's counts are claims to re-measure.
4. D-5 (the AF-AP-139 row also in `TEST_SCREEN`): measure whether `main` screens `/tests/` paths with `TEST_SCREEN` only, and the row's
   hits under `tests/` and `harness-ports/tests/` at the PIN. Grade the deviation: needed (an `AP_SCREEN`-only row would never run where
   the class lives) or not, and whether the twin floods. D-6 (the one reviewed-safe AF-AP-89 hit at `scripts/pc_lane.sh:292`): confirm
   or refute that the PC does not expand that heredoc body.
5. D-8: classify the unreviewed AF-AP-139 hit `tests/test_s0_05_egress.py:3506-3513` (`RELAY_LOG_SERVER`, answers 200 on every path):
   read what the test's C0 request asks and whether a real service would refuse that path (the registry's class: a stand-in that
   answers every path, so a probe of a path the real service refuses still passes). Measure from the test and the collector; no
   bridge use.
6. THE HOOK FIX (f), AF-AP-44: list every probe of the venv path in the hook at the PIN and confirm each sits inside a `try` that
   returns `[]` (or the hook's documented no-op). Attack with probe failures the builder's tests do not raise (other `OSError`
   subclasses, a dangling symlink, a directory where the interpreter should be, an interpreter that exits non-zero or hangs), and run
   the hook's `main` on a real Edit payload as an unprivileged user in a scratch copy (the builder: `rc=1` with HEAD's hook, `rc=0` with
   the fix, uid 65534) — reproduce both. D-9 (`gitnexus_impact`'s unguarded `/tmp` probe) is adjacent: report, do not fix.
7. THE BASELINE CONTROL (b), AF-AP-138: confirm every mutation row's killer runs on the UNMUTATED module first and must pass. Build a
   hollow killer (one that fails on the unmutated module) in a scratch copy and paste the harness refusing it. Reproduce D-10 (the
   `unsorted-tree-digest` killer failed on the unmutated module before the fix) at `656ddf6^`'s bytes, and the fix at the PIN.
8. PARSE_CLASSES (n): rebuild the builder's mutants v-D (the refusal swallowed) and v4 (`parse_classes` a no-op) in a scratch copy;
   paste each RED against the new test. Add your own: a wrong line number in the refusal, a wrong rc, a refusal on the first malformed
   row only.
9. YOUR MUTANTS: at least eight more across the changed code (each screen row's regex, `pyflakes_delta`, the baseline check), each
   through the real test files in a scratch copy, each KILLED by a named test or reported as a SURVIVOR finding. A mutant must compile
   and be collected (AF-AP-78).
10. GATES at the PIN, in a private clone: the two test files twice (counts agree; `173 passed`, set 2a60fb528bf2);
    `tests/test_hooks_worktree.py` once; `bash harness-ports/tests/run-all.sh` once (its last lines); pyflakes on the three files;
    `python3 scripts/no_laya_in_gates.py`; `python3 scripts/ap_screen.py .claude/hooks/edit-snapshot.py`.
11. ADJACENT CONSUMERS: `scripts/ap_screen.py` and `scripts/lint_delta.py` load the hook in-process; `scripts/lane_context.sh`'s screen
    section runs `ap_screen.py`. Show each still runs on a real file at the PIN (rc and first lines), and that a new row's regex
    cannot raise on any file under `scripts/ src/ proofs/ harness-ports/ tests/` (a catastrophic-backtracking or compile error is a
    finding: time the AF-AP-89 row over the largest `.sh`/`.py` files).

## Venue and boundary

- Scratch: `/tmp/vk150/`. A private clone at the PIN when a command needs a repository: `git clone -q --shared /home/user/agent-factory
  /tmp/vk150/clone && git -C /tmp/vk150/clone checkout -q --detach 656ddf6` (about 600 MB of working tree; the sandbox had 3.4 GB free
  at authoring; one clone at a time; remove it at the end). Run pytest from the clone's root (its pyproject puts `src` first).
- Python: `/root/venv-agent-factory/bin/python`; pytest `-p no:cacheprovider --basetemp=/tmp/vk150/bt<n>` (make the parent first).
  pytest-xdist is not installed: run serially. `bash scripts/pc_suite.sh set-id -- <files>` works here; no other pc_* script, no bridge.
- CREATE only `tasks/briefs/kit-k1-support/VERIFY-K150-report.md` (write it incrementally from the start). Never edit anything else in
  the repository. Two other sandbox agents are live: J1-1-R3 in `/tmp/j113s/` and VERIFY-J1-3-R1 in `/tmp/vj13r1/`; never touch either.
  Never run `git stash`, `checkout`, `restore`, `add`, `commit`, `worktree` or `push` in the shared tree. No outward-facing action.
  Never read `~/.hermes/`.
- CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
  `scripts/lane_context.sh -q 'how does the edit-snapshot hook screen a file and probe the venv' -s pyflakes_delta -s main -o /tmp/vk150/pack.md .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py`.

PREDICATE: a finding blocks only if it is contract-mapped, reproduced on the real path, materially effective (a row that never fires
where its class lives, a row that floods clean code, a hook crash on a probe failure, a mutation row whose kill is hollow, a bake
that states a false fact), with a concrete discriminator, and in-boundary. Report EVERY meaningful observation, with no severity
filter, then apply the predicate. Emit ONE `GATE RECOMMENDATION:` line — `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` /
`CONTRACT-INVALID`. The coordinator owns the gate.

Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/kit-k1-support/VERIFY-K150-report.md --root .`; apply its
`fix:` hints for at most three rounds, then paste and finish. The report ends with DISCREPANCIES and NOT-done, and states which items
you ran fully, partly or not at all (AF-AP-170: a recommendation over un-run items is void).

## PREMISE — MEASURED at authoring (2026-09-24 03:2xZ, sandbox, uid 0; generated by `scripts/premise_block.sh`, every command echoed exactly as it ran)
```
$ git rev-parse --short '656ddf6^{commit}'
656ddf6
$ git merge-base --is-ancestor 656ddf6 origin/claude/soundbox-kit-migration-iz1jwf && echo pin-is-on-origin
pin-is-on-origin
$ git show --stat --format='%h %s' 656ddf6 | tail -1
 15 files changed, 899 insertions(+), 155 deletions(-)
$ git diff --quiet 656ddf6 HEAD -- .claude/hooks/edit-snapshot.py .claude/skills/build-loop .claude/skills/anti-hollow-green .claude/skills/orchestration .agents/skills/build-loop .agents/skills/anti-hollow-green .agents/skills/orchestration .agents/lane-skills harness-ports/hand-ported.sha256 sandbox-kit/VENDORED-MANIFEST.md sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py scripts/vendored_manifest.py scripts/ap_screen.py && echo boundary-identical-to-pin || echo BOUNDARY-CHANGED-SINCE-PIN
boundary-identical-to-pin
$ git ls-tree 656ddf6 -- .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py scripts/vendored_manifest.py scripts/ap_screen.py | awk '{print substr($3,1,12), $4}'
2f968c6f5bb3 .claude/hooks/edit-snapshot.py
eb20dde7e198 scripts/ap_screen.py
4a4ed0fece0b scripts/vendored_manifest.py
c33aa104023a tests/test_edit_snapshot_ap_screen.py
365a71f820ad tests/test_vendored_manifest.py
$ /root/venv-agent-factory/bin/python -m pytest tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py -q -p no:cacheprovider 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*$//'
173 passed
$ bash scripts/pc_suite.sh set-id -- tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py
2 files set=2a60fb528bf2
$ python3 scripts/vendored_manifest.py --check 2>&1 | tail -2
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
$ bash harness-ports/bin/sync-skills.sh --check >/dev/null 2>&1; echo sync-skills-check rc=$?
sync-skills-check rc=0
$ bash harness-ports/bin/sync-lane-skills.sh --check >/dev/null 2>&1; echo sync-lane-skills-check rc=$?
sync-lane-skills-check rc=0
$ grep -n -E '_AF_AP_139|AF-AP-25|AF-AP-89|AF-AP-159|AF-AP-162|def pyflakes_delta|_VENV_PY' .claude/hooks/edit-snapshot.py | cut -c1-100
65:_AF_AP_139 = (
203:    # AF-AP-159 (2026-09-23, VERIFY-J1-0-R5 V5-05): a PyYAML node's start_mark is its first PROP
206:    ("AF-AP-159", re.compile(r"""\.start_mark\.line\s*\+|\+\s*[\w.\[\]]*\bstart_mark\.line\b""")
207:     "a line number computed from a node's start_mark — a YAML node starts at its first proper
210:    _AF_AP_139,
211:    # AF-AP-25, the line-parser form (2026-09-23, VERIFY-REPIN-a F11): `parse_lock` / `parse_sbo
215:    ("AF-AP-25", re.compile(r"""\bfor\s+[\w, ]+\s+in\s+[^\n]*(?:\.splitlines\(\)|\.readlines\(\)
216:     "a line loop that regex-matches each line of a structured file (a lock, an SBOM, a config, 
217:    # AF-AP-89's doubled escape (2026-09-23, the T94 landing; AF-AP-162): T94's poll probe in sc
219:    # the PC received a syntax error; the text-matching test double never ran the probe (AF-AP-1
221:    ("AF-AP-89", re.compile(r"""(?:\bbridge|\bpc\.sh)[ \t]+"(?:[^"\\]|\\[\s\S])*?\\\\(?:\$\(|\\"
222:     r'''a doubled escape (`\\$(` or `\\\"`) inside a double-quoted `bridge` / `scripts/pc.sh` a
297:    _AF_AP_139,  # the same row as in AP_SCREEN: the registry's instance was a test stand-in (te
311:_VENV_PY = os.environ.get("AF_VENV", "/root/venv-agent-factory") + "/bin/python"  # PC lanes exp
327:def pyflakes_delta(fp: str, src: str) -> list[str]:
333:        if not Path(_VENV_PY).exists():
340:        base = _pyflakes_msgs(_VENV_PY, shown.stdout) if shown.returncode == 0 else {}
341:        now = _pyflakes_msgs(_VENV_PY, src)
$ grep -c -E '^def test_' tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py
tests/test_edit_snapshot_ap_screen.py:3
tests/test_vendored_manifest.py:42
$ python3 scripts/ap_screen.py .claude/hooks/edit-snapshot.py 2>&1 | head -12
--- AP_SCREEN over 1 path(s): 19 hits over 1 files ---
AF-AP-40: 3
    .claude/hooks/edit-snapshot.py:133: # `else\b` added 2026-09-08 (VERIFY-P5a F7): the TERNARY form `v = read(p) if p.exists() else {}`
    .claude/hooks/edit-snapshot.py:135: # build_capture_record.py's `receipt = json.loads(rp.read_text()) if rp.exists() else {}`, which
    .claude/hooks/edit-snapshot.py:430: if Path("/tmp/gitnexus-analyze.lock").exists():
AF-AP-118: 2
    .claude/hooks/edit-snapshot.py:195: # AF-AP-118 (2026-09-22, VERIFY-K1-g's route measurement): a harness-level fallback chain (Hermes `f
    .claude/hooks/edit-snapshot.py:209: "a harness fallback chain (`fallback_providers`) written into a lane/profile config — the chain IS a
AF-AP-127: 2
    .claude/hooks/edit-snapshot.py:200: # exporters did `scrub(text[:cap])`; the J1-1 contract truncated inside normalize before redact.
    .claude/hooks/edit-snapshot.py:202: "a redaction/scrub applied to an already-capped slice (`scrub(x[:cap])`) — a secret straddling the c
AP-51: 2
```
