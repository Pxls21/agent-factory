# H1a: an opt-in LCM-X mode for one PC lane profile, pinned and off by default (task #365, D-108 item 7)

Role: a new sandbox code-implementer lane (Opus 5.5). Authored 2026-09-29 11:1xZ by the coordinator.

The owner: "Yes, ... for Hermes, yes, install ... LCM" (D-108 item 7), after D-106 ("if it's good enough, then just use
that"). T1-LCM-AUDIT (`tasks/briefs/jev-trim/T1-LCM-AUDIT-report.md`, READ §3 and §5 in full) found LCM-X
(`electricsheephq/lcm-x` at 601a9cc, v0.24.3) the one live candidate, and the coordinator read it as good enough for the
PC lanes under five conditions: pinned in `upstream.lock.yaml` and installed into ONE cloned lane profile, never the
owner's own profiles; summaries only through OmniRoute; no download at start (the tokenizer pre-seeded, embeddings off);
the cross-session tools off; one lane beside a control lane, compared. T1 also found that whether LCM-X loads on our
Hermes lane runtime (b3399c1) is UNTESTED, and that a failed load falls back to the built-in compressor with only a
warning (§3, "Engine selection").

This lane builds the TOOLING half. The coordinator does the PC half (the clone on the PC, the tokenizer pre-seed, a smoke
run that proves the engine loaded and that egress stays on OmniRoute, then the lane pair). Nothing here runs LCM-X code
or touches the PC.

Why tooling at all: a relaunch re-derives a lane profile's `config.yaml` from the source profile
(`harness-ports/bin/lane-profile.sh`, its create path), so a hand edit to one profile does not survive. The mode must be
applied by the profile script on every create.

## CONTRACT

1. **Premise.** Re-run the block below; on a difference, stop and report CONTRACT-INVALID.
2. **The pin.** `upstream.lock.yaml` gains an lcm-x entry in the file's own format: the URL, the full commit
   (601a9ccb3d5fefbe242a453e57ed2c8196bf33c3), the version (`plugin.yaml`), the license, the commit date, its role (the
   H1 trial on one PC lane profile; not production), and the fact that upstream tests no Hermes pin of ours (T1 §5 row 2).
   Verify each field from your own read-only clone at the pin under your scratch. Never install it and never run its code.
3. **The opt-in, `LANE_CONTEXT_ENGINE`,** read by `harness-ports/bin/lane-profile.sh` as it reads `LANE_DONE_GATE`.
   - Unset or empty: every profile the script writes is byte-identical to today's; a test proves it on the existing
     fixtures.
   - `lcm-x`: the profile it creates or re-derives gets all of a to e. Any other value fails loud.
   - a. **The plugin:** the profile's user-plugin directory holds the plugin, pointing at the pinned clone at `LCM_X_DIR`
     (a default path under the PC user's home that the coordinator creates). `verify` refuses when the clone's HEAD is
     not the lock file's commit, read from `upstream.lock.yaml`, never from a second copy of the SHA.
   - b. **The config:** `plugins.enabled` includes the plugin's name (other entries kept), and the context engine is set
     to `lcm-x`, using the keys Hermes b3399c1 reads. Find them in `/home/user/nerdherderdani/hermes-agent` at b3399c1
     (`agent/agent_init.py:1746` `_select_context_engine`; `hermes_cli/plugins.py`'s user-plugin discovery and
     `plugins.enabled`), and cite the lines. Where a profile's user plugins live (relative to which home) is a question
     for your read, not a premise.
   - c. **The five conditions' settings,** given to the lane's hermes process as environment, never written into the
     profile's `.env` (a copy of the owner's secrets file; never read it, never print it). A separate non-secret file
     the runner exports is one way. The settings: the cross-session tools off (`LCM_DISABLED_TOOLS`, naming
     `lcm_recall`, `lcm_load_session`, `lcm_grep`, and any other tool your read of the pin shows reaching another
     session); the store inside the profile (`LCM_DATABASE_PATH`); embeddings off (the pin's default; name the variable
     that keeps them off); no download at start (`TIKTOKEN_CACHE_DIR` at a pre-seeded directory whose `cl100k_base` file
     the coordinator places: find the file name and the sha256 tiktoken expects, cite the source, and make `verify`
     refuse an absent or altered file).
   - d. **Summaries through OmniRoute only.** From the pin's code and Hermes b3399c1's auxiliary client, state which
     route LCM-X's `call_llm(task="compression")` takes in a lane profile whose main provider is the OmniRoute endpoint,
     and what falls back where (T1 §3, the "auxiliary model route" row). If the profile holds any other provider
     credential that the fallback chain would use, `verify` reports it by NAME only, never a value. The coordinator's
     egress watch on the PC is the live check.
   - e. **`verify`** checks a to d and fails loud, naming the failed item.
4. **The pass-through.** `scripts/pc_lane.sh`'s env list (its line 346) and `harness-ports/bin/pc-lane.sh` carry
   `LANE_CONTEXT_ENGINE` and `LCM_X_DIR` to the profile script and to the lane's process, as `HERMES_MODEL` travels. A
   lane launched without them runs exactly as today.
5. **The pair.** Nothing to build: the same brief launched without the opt-in is the control. The report gives the two
   launch commands the coordinator runs, one after the other (ONE long-context local lane at a time, D-061).
6. **Tests.** `harness-ports/tests/test_lane_profile.sh`, `test_pc_lane.sh` and `test_pc_lane_dispatcher.sh` stay green
   and gain: off gives byte-identical profiles; on gives a to d; `verify` fails on each wrong item (the clone at another
   commit; the tokenizer file absent or altered; a cross-session tool left on; the engine key absent; an unknown engine
   value); the pass-through carries the variables. Each check with a named mutant it kills; `bash
   harness-ports/tests/run-all.sh` passes; every test that names a changed path passes (the gate stack in plan mode
   lists them: `python3 scripts/stack.py gate paths=<paths> mode=plan`).
7. **Docs.** The runbook section that covers lane profiles (`PC-BRIDGE.md` or `docs/HARNESS-PORTS.md`) states the mode,
   the five conditions, the steps the coordinator runs on the PC before a first launch, and what is NOT done (nothing
   run on the PC; production is a later decision with its own proof: standing rules 10 and 11, T1 §5 row 7).

## WHERE YOU WORK: a worktree, never the shared tree (orchestration 0p)

The coordinator's own tool calls run `scripts/pc_lane.sh`, and its commits run the hooks that read the tree. Make a
detached worktree at the PIN under your scratch (`git -c core.hooksPath=/dev/null worktree add -q --detach <W> <PIN>`),
build and test there, and deliver ONE file in the shared tree: `tasks/briefs/jev-trim/H1A-LCM-PROFILE.patch` (the
`git -C <W> diff` against the PIN), proven with `git apply --check` on a fresh worktree at the PIN where the tests above
pass again. Remove every worktree and clone you made before you report.

## BOUNDARY

- MODIFY (in your worktree only): `harness-ports/bin/lane-profile.sh`, `harness-ports/bin/pc-lane.sh`,
  `scripts/pc_lane.sh`, `upstream.lock.yaml`, `harness-ports/tests/test_lane_profile.sh`,
  `harness-ports/tests/test_pc_lane.sh`, `harness-ports/tests/test_pc_lane_dispatcher.sh`, and the runbook section.
- CREATE (in the shared tree): `tasks/briefs/jev-trim/H1A-LCM-PROFILE.patch`.
- READ: T1's report; the hermes-agent clone at b3399c1 (never modify it); your own lcm-x clone at the pin.
- Other lanes: SCRUB2-R1 round 4 (`scripts/transcript_export.py` and its tests, in its own worktree) and LS-B10 (new
  `scripts/ls_req.py`, `tests/test_ls_req.py`). Touch none of their files.

## REPORT

Return the whole report as your final message: the premise re-run; files with line counts and sha256; per contract item
its evidence (the cited Hermes and lcm-x lines, the pasted test output); the gates; the mutants; the patch's proof; the
two launch commands; the PC steps the coordinator must run first, in order, each idempotent (a re-run skips what is
done: AF-AP-244); NOT done, first-class; DISCREPANCIES; your self-attack (how could a lane still run without LCM-X, or
with a cross-session tool on, and pass `verify`?).

## STANDING RULES

- Do NOT spawn subagents. No git write in the shared tree; no outward action; no PC bridge.
- Never read a secret file (`.pc-bridge.env`, any `*.env`, any key file). A test secret is a fake built at run time.
- Never install or run LCM-X code; read it.
- Counts pasted from the tests' own summary lines (and from `scripts/test_summary.sh` with set ids for any pytest run);
  `--basetemp` as a pytest ARGUMENT outside every work tree; a long gate in ONE foreground call; stamps from `date -u`;
  commits cited by origin id or subject.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Stop every process you start before you report.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin bef1e9e)

Printed by `bash scripts/premise_block.sh` from the main tree, before this brief's commit. The `[rc=1]` after the four
zero counts is grep's exit code when nothing matches: no LCM entry anywhere yet. Expected to differ: nothing.

```
$ git merge-base --is-ancestor bef1e9e HEAD && echo bef1e9e-is-an-ancestor-of-HEAD
bef1e9e-is-an-ancestor-of-HEAD
$ sha256sum harness-ports/bin/lane-profile.sh harness-ports/bin/pc-lane.sh scripts/pc_lane.sh upstream.lock.yaml harness-ports/tests/test_lane_profile.sh harness-ports/tests/test_pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh | cut -c1-16,65-
9b2aa796197009da  harness-ports/bin/lane-profile.sh
fd281439ea3b5aaf  harness-ports/bin/pc-lane.sh
984fdda57951e54b  scripts/pc_lane.sh
8990e5f12dbdb6a7  upstream.lock.yaml
cfbed752380da49c  harness-ports/tests/test_lane_profile.sh
bce3c4ff9bf83979  harness-ports/tests/test_pc_lane.sh
5ff87dffc893d133  harness-ports/tests/test_pc_lane_dispatcher.sh
$ grep -c -i 'lcm' upstream.lock.yaml harness-ports/bin/lane-profile.sh harness-ports/bin/pc-lane.sh scripts/pc_lane.sh
upstream.lock.yaml:0
harness-ports/bin/lane-profile.sh:0
harness-ports/bin/pc-lane.sh:0
scripts/pc_lane.sh:0
[rc=1]
$ grep -n 'for v in HERMES_MODEL' scripts/pc_lane.sh | cut -c1-70
346:for v in HERMES_MODEL HERMES_REASONING HERMES_PROFILE HERMES_TOOLS
$ grep -n 'LANE_DONE_GATE' harness-ports/bin/lane-profile.sh | cut -c1-70
221:  python3 - "$from" "$target/config.yaml" "$lane" "${LANE_DONE_GAT
$ git -C /home/user/nerdherderdani/hermes-agent cat-file -t b3399c1
commit
$ git -C /home/user/nerdherderdani/hermes-agent show b3399c1:agent/agent_init.py | grep -n 'def _select_context_engine'
1746:def _select_context_engine(_agent_cfg):
$ bash harness-ports/tests/test_lane_profile.sh 2>&1 | tail -1
lane profile: 30 passed, 0 failed
$ bash harness-ports/tests/test_pc_lane.sh 2>&1 | tail -1
67 passed, 0 failed
$ bash harness-ports/tests/test_pc_lane_dispatcher.sh 2>&1 | tail -1
pc_lane dispatcher: 51 passed, 0 failed
```
