# VERIFY-H1a: attack the LCM-X lane mode as landed, the D-110 lock move included (task #365)

Role: adversarial-verifier, a fresh lane (sandbox, Opus 5.5). Do NOT spawn subagents. Report:
`tasks/briefs/jev-trim/VERIFY-H1A-report.md` (write it incrementally). If the harness refuses a report-file write, return
the WHOLE report as your final message and as your hand-back message (not a summary); never work around the refusal.

Authored 2026-09-29 by the coordinator.

The change under test: the commit "H1a landed (task #365; GATED-PENDING-VERIFY): the LCM-X lane mode, its pins in
pc-lane.lock.yaml (D-110)" (its origin id is the brief's PIN), eight files: `harness-ports/bin/lane-profile.sh`,
`harness-ports/bin/pc-lane.sh`, `scripts/pc_lane.sh`, the three suites `harness-ports/tests/test_lane_profile.sh`,
`test_pc_lane.sh` and `test_pc_lane_dispatcher.sh`, `docs/HARNESS-PORTS.md` section 7 and the new `pc-lane.lock.yaml`.
It is the builder's patch (`tasks/briefs/jev-trim/H1A-LCM-PROFILE.patch`) plus one rework in the coordinator's hands: the
owner ruled (D-110, `docs/08_DECISION_LOG.md`) that the PC-lane tool pins live in `pc-lane.lock.yaml`, never in
`upstream.lock.yaml` (which S0-06 and S0-12 attest; the owner signed both, D-107), so the lock entry moved, `verify` reads
the new file, and the lane-profile suite gained one control (the lock FILE absent). Contract:
`tasks/briefs/jev-trim/H1A-LCM-PROFILE-brief.md`, items 2 to 7, with D-110 replacing `upstream.lock.yaml` by
`pc-lane.lock.yaml` in items 2 and 3a. The builder's report: `tasks/briefs/jev-trim/H1A-report.md`; read its section 10
(D1 to D10; D1 is what D-110 settled) and its self-attack (section 11) first. The T1 audit behind the five conditions:
`tasks/briefs/jev-trim/T1-LCM-AUDIT-report.md`. Every claim in those reports, and in the landing commit's message, is a
hypothesis.

Why it matters: `harness-ports/bin/pc-lane.sh` is the runner of EVERY PC lane, and `lane-profile.sh` writes every lane
profile. A defect in the default (off) path changes every lane; a hole in the lcm-x path lets a lane run with a
cross-session tool on, a summary route off OmniRoute (standing rule 3), or LCM-X not actually loaded while `verify` says
it is (a hollow green, the #1 rule). Nothing of H1a has run on the PC yet: H1b, the PC half, is the coordinator's, after
your verdict.

## WHAT TO ATTACK (report every observation; no severity filter)

1. **Off is unchanged.** With `LANE_CONTEXT_ENGINE` unset or empty, every profile `lane-profile.sh` writes (create,
   re-derive, both base profiles, the gate on and off) is byte-identical to the parent commit's output, and `pc-lane.sh`
   hands the lane's hermes the same environment as before. Prove it against the PIN's parent, not against the builder's
   goldens alone.
2. **The lock move (D-110).** The pins come only from `pc-lane.lock.yaml` (no second copy of the revision, the wheel or
   the tokenizer digest anywhere a check reads); `verify` fails closed when the file is absent, empty, not YAML, or holds
   the entry with a field missing or of the wrong shape; `upstream.lock.yaml` is byte-identical to the PIN's parent and
   `python3 scripts/validate-ledger integrity --root . --ledger proofs/ledger.json` reads rc 0 at the PIN; no proof, no
   SBOM pin-diff (`proofs/S0-12/check_pin_diff.py`) and no vendored-manifest check reads the new file (grep every reader).
3. **Conditions a to d, and e.** Can a lane in lcm-x mode pass `verify` while LCM-X is not the engine Hermes b3399c1 will
   load, while a tool that reaches another session is on, while the store sits outside the profile, while embeddings or a
   download at start are possible, or while a summary can leave OmniRoute? Try shapes beyond the builder's: another clone
   at the same commit, a dirty clone, a second LCM plugin under another name, `plugins.enabled` and `context` blocks in
   other YAML layouts (flow style, anchors, duplicate keys), an inherited `LCM_*` variable, `PYTHONPATH` ordering, other
   hermes shebang forms. Read Hermes b3399c1 and LCM-X 601a9cc from clones you make yourself under your scratch (URLs from
   `upstream.lock.yaml` and `pc-lane.lock.yaml`; never `git remote -v` in any clone; never `git grep` or `git show` in the
   shared partial clone `/home/user/nerdherderdani/hermes-agent`, which fetches blobs lazily, builder's D9). Never
   install either and never run their code; a read and a byte comparison only.
4. **The tokenizer and the runtime import.** The digest comparison form (AP-32: the exact `sha256:<hex>` form), the cache
   file name (`sha1(url)`), the deps directory checks (`realpath`, the version, a tiktoken found only outside the deps
   directory), and the probe that blocks `requests` and `blobfile`. The fake tiktoken in the suite is a labelled test
   double; say what only the PC preflight (H1b) can prove.
5. **Secrets.** `verify` reads the profile's `.env` for KEY NAMES only, in the shape of Hermes's own scanner (builder's
   D8). Prove with FAKE values built at run time that no value reaches stdout, stderr, a log or the lane's environment,
   including on each failure path.
6. **The pass-through.** `scripts/pc_lane.sh` forwards the mode and its paths quoted, only with the opt-in; the runner
   strips inherited `LCM_*` settings except `LCM_X_*`; `LCM_X_PYTHON` is not forwarded (builder's D7): what fails, and how
   loudly, if the PC's `hermes` is not a plain-shebang Python script?
7. **The adjacent items** the builder left (D5: off mode keeps a legacy `fallback_model`; D6: a stale header comment):
   judge each as blocking or follow-up.
8. **Mutation.** The coordinator's grading killed 58 of 58 (the builder's 56 plus M32b, the file-absent control, and
   M40-old-lock-path, the pre-D-110 path). Reproduce at least six as FAILED checks through the real suites, and add a
   mutant for each clause the set does not cover (start with the lock reader's `except Exception` scope and the
   off-path byte identity).
9. **The gates.** Re-run the three suites, `bash harness-ports/tests/run-all.sh`, and every test that names a changed path
   (`python3 scripts/stack.py gate paths=<the eight paths> mode=plan` lists them; it writes a run record under the live
   `.jev/stacks/`, which is expected), plus `tests/test_shell_syntax.py` and `tests/test_attested_inputs.py`.

## GATE

Apply the blocking predicate of skill `contract-gate` and D-034 (a finding re-opens the build only if it is
CORE-BLOCKING; the rest become follow-ups, which the owner routes to GitHub issues, D-108 item 2). One recommendation:
MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID, each blocking finding with its reproduction
command. Say what H1b must prove on the PC before a first lcm-x launch.

## BOUNDARY

READ everything. WRITE only your report and scratch under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vh1a/`. Work in a detached worktree at the PIN
with hooks off (`git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add -q --detach <dir> <PIN>`), never
in the shared tree; remove every worktree you make before you report. The builder's mutation driver is
`.../scratchpad/h1a/mutants.py`; the coordinator's adapted one is `.../scratchpad/h1a-r1/mutants.py` (its log:
`.../scratchpad/h1a-r1/run.log`); run either in your copy.

## STANDING RULES

- No git writes (a worktree add and remove, hooks off, is the one exception), no PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, `~/.hermes/profiles/*/.env`, and the GH_TOKEN and GITHUB_TOKEN variables.
  Test secrets are FAKE strings built at run time.
- Other lanes (VERIFY-LS-B10, VERIFY-SCRUB2-R1-R4) may run beside you; touch no file of theirs.
- The disk is shared: scratch under 300 MB (the two clones included), deleted as you go; a private `--basetemp` outside
  any work tree for every pytest run, passed as a pytest ARGUMENT (never through `PYTEST_ADDOPTS`, AF-AP-237); never run
  the whole `tests/test_vendored_manifest.py`.
- The sandbox VM rebooted twice today while tests ran (14:09:29Z, about 14:20:10Z; cause open, memory looked small): run
  `free -m` before a heavy command, keep each run's evidence on disk as you go, and say in the report which runs a reboot
  voided.
- Test counts are pasted from `scripts/test_summary.sh` (pytest) or the suite's own last line (bash), with their set ids.
  Stamps are substituted from `date -u`, never typed.
- Long commands in one foreground call, each under 10 minutes; kill by pid only; a process you start, you stop.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Cite commits by subject or by an origin id; the coordinator's local ids change on the push.

## PREMISE — MEASURED at authoring (2026-09-29, main tree@0ab1df7; PIN origin 42a4a1d)

Printed by `bash scripts/premise_block.sh` from the main tree at origin 0ab1df7, after the push. The PIN is origin 42a4a1d, the H1a landing; its parent is the D-110 commit. The sha256 lines read the main tree, which equals the PIN for these files. The coordinator's pytest count on the last line's set was `957 passed` (sandbox, before the push); it was not re-run at authoring: re-measure it. Re-run every `$` line from `/home/user/agent-factory`; on any difference, stop and report CONTRACT-INVALID with the diff.

```
$ git merge-base --is-ancestor 42a4a1d HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git log -1 --format=%s 42a4a1d
H1a landed (task #365; GATED-PENDING-VERIFY): the LCM-X lane mode, its pins in pc-lane.lock.yaml (D-110)
$ git diff --name-only 42a4a1d~1 42a4a1d
docs/HARNESS-PORTS.md
harness-ports/bin/lane-profile.sh
harness-ports/bin/pc-lane.sh
harness-ports/tests/test_lane_profile.sh
harness-ports/tests/test_pc_lane.sh
harness-ports/tests/test_pc_lane_dispatcher.sh
pc-lane.lock.yaml
scripts/pc_lane.sh
todo/BUILD-TASKLIST.md
$ git diff --quiet 42a4a1d~1 42a4a1d -- upstream.lock.yaml && echo upstream-lock-unchanged-by-the-landing
upstream-lock-unchanged-by-the-landing
$ sha256sum pc-lane.lock.yaml harness-ports/bin/lane-profile.sh harness-ports/bin/pc-lane.sh scripts/pc_lane.sh harness-ports/tests/test_lane_profile.sh harness-ports/tests/test_pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh docs/HARNESS-PORTS.md | cut -c1-16,65-
e717400c2ec4f3d3  pc-lane.lock.yaml
ea884902f57fd601  harness-ports/bin/lane-profile.sh
b48bceaab26d4c18  harness-ports/bin/pc-lane.sh
5dbfb535dcb3c99a  scripts/pc_lane.sh
cf28a3dfc7a9803d  harness-ports/tests/test_lane_profile.sh
8856fbe21351a2a4  harness-ports/tests/test_pc_lane.sh
8144bfc4e1e704c9  harness-ports/tests/test_pc_lane_dispatcher.sh
43d46428d1cf0b4b  docs/HARNESS-PORTS.md
$ python3 scripts/validate-ledger integrity --root . --ledger proofs/ledger.json > /dev/null 2>&1; echo "ledger-integrity rc=$?"
ledger-integrity rc=0
$ bash harness-ports/tests/test_lane_profile.sh 2>/dev/null | tail -1
lane profile: 70 passed, 0 failed
$ bash harness-ports/tests/test_pc_lane.sh 2>/dev/null | tail -1
70 passed, 0 failed
$ bash harness-ports/tests/test_pc_lane_dispatcher.sh 2>/dev/null | tail -1
pc_lane dispatcher: 53 passed, 0 failed
$ bash scripts/pc_suite.sh set-id -- tests/test_edit_snapshot_ap_screen.py tests/test_no_laya_in_gates.py tests/test_stack.py tests/test_system1_context.py tests/test_transcript_export.py tests/test_upstream_lock_lane_runtime.py tests/test_shell_syntax.py tests/test_attested_inputs.py | tail -1
8 files set=f7d8d61400d8
```
