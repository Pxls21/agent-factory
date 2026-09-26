# HCTX1-R1: a relaunched PC lane gets the current profile config, and the lane helper's repo root is right (tasks #316, #317)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/HCTX1-R1-report.md` (write
it incrementally from the start). PIN: origin 2a50a65. Source findings: HCTX1's report `tasks/briefs/system1/HCTX1-report.md`
(its D-1 and A-1) and AF-AP-226 in `docs/INCIDENT-LOG.md`.

## WHY

- **#316 (D-1).** `lane-profile.sh create` on an EXISTING lane profile only verifies it. A profile cloned before HCTX1 has no
  per-model `context_length`, so relaunching that lane id fails verify with "context override missing". The same holds for
  any later change to the rewrite: an existing profile keeps the rewrite it was born with.
- **#317 (A-1, AF-AP-226).** The helper computes the repo root as `$(dirname "${BASH_SOURCE[0]}")/../../..`: one directory
  too high (`bin` to `harness-ports` to the repo is `../..`, as every other script in `harness-ports/bin/` spells it). With
  `LANE_DONE_GATE=1`, the lane hooks then name a `lane-done-gate.py` that does not exist. Its test computes the expected
  path the same wrong way, so it passes: a mirrored oracle.

## CONTRACT

1. **Refresh on relaunch.** When the lane profile exists, `create` rewrites its `config.yaml` from the SOURCE profile's
   `config.yaml` by the same rule a new clone gets: chain removal, the lane header, the context block and, when enabled, the
   done-gate hooks. It keeps everything else in the profile: `state.db` and its sessions, `.env`, and any other file or
   directory. Then it verifies. A profile that is not a directory, or has no `config.yaml`, fails with a named reason; no
   silent re-clone.
2. **Idempotent.** A second `create` on a current profile leaves `config.yaml` byte-identical.
3. **The root.** Both sites compute the repo root as `../..` from `bin/`. The test states the expected hook path as a
   literal built from the test's own known layout, never with the helper's formula. A negative control on the PIN's helper
   reds.
4. **Nothing else changes.** The byte-preservation rule, `verify`, `remove`, and the base profile are never written. The
   PC runner `harness-ports/bin/pc-lane.sh` is not edited: say whether it needs a change for this to reach a relaunch.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Tests in `harness-ports/tests/test_lane_profile.sh`, in its fixture style (a fake `hermes`, fixture profiles):
   - an old-style profile (no context block) relaunched: `create` rewrites it, keeps a planted `state.db` and a planted
     extra file byte-identical, and verify passes;
   - a second `create` is a no-op on `config.yaml`;
   - a non-directory profile, or one with no `config.yaml`, fails with its reason;
   - the done-gate hook path is the literal expected path.
   A named mutant reds each, as a FAILED check (AF-AP-223).
3. `bash harness-ports/tests/test_lane_profile.sh` and `bash harness-ports/tests/test_pc_lane.sh`, twice each, pasted;
   `bash harness-ports/tests/run-all.sh` once; `bash -n` on the helper; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints
   0 for every file you write.
4. The coordinator's PC check, written out as commands, and not run by you. It creates a lane profile the old way (a
   plain clone), then runs `create` on it through the new helper, shows the per-model `context_length` resolved by
   Hermes's own code (the HCTX1 report section 6 probe), and removes the profile.
5. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `harness-ports/bin/lane-profile.sh`, `harness-ports/tests/test_lane_profile.sh`. CREATE: your report. READ
everything else.

## STANDING RULES

- No git writes, no PC bridge, no outward-facing action.
- Never read a real secret source (`.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`, the GH_TOKEN
  and GITHUB_TOKEN variables). Fixtures use fake keys made at run time.
- Other lanes hold this tree: SYNTH1 (`scripts/s1_synth.py`, `tests/test_s1_synth.py`, its report) and VERIFY-I59-A (its
  report). Never touch their files.
- The disk is shared (about 1.7G free): scratch under 100 MB in
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/hctx1r1/`, deleted as you go.
- Test counts are pasted from the test output. Stamps are substituted from `date -u`, never typed.
- Run long commands in one foreground call. Kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text of
  its own (under 200 characters; a note only for a 0).

## PREMISE — MEASURED at authoring (2026-09-26 06:2xZ, the sandbox tree; HEAD's code = origin 2a50a65)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-60
2a50a65 I59-A round 1 home (task #312; held for the issue #5
$ grep -n -E '^create_lane|if \[ -e "\$target" \]; then|verify_lane "\$lane"|/\.\./\.\./\.\.' harness-ports/bin/lane-profile.sh
84:  verdict="$(python3 - "$target/config.yaml" "$lane" "$SOURCE/config.yaml" "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)" \
188:create_lane() {
194:  if [ -e "$target" ]; then
195:    verify_lane "$lane"
216:  python3 - "$target/config.yaml" "$lane" "${LANE_DONE_GATE:-0}" "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)" \
453:  verify_lane "$lane"
$ grep -n -E 'lane-done-gate|\.\./\.\./\.\.' harness-ports/tests/test_lane_profile.sh | head -6
284:python3 - "$TMP/source-config.yaml" "$GATE_ON" "$(cd "$HERE/../../.." && pwd)" gateon <<'PY'
296:helper = f"{root}/harness-ports/bin/lane-done-gate.py"
333:    "lane-done-gate.py gate", "lane-done-gate.py changed"
$ ls harness-ports/bin/lane-done-gate.py
harness-ports/bin/lane-done-gate.py
$ bash harness-ports/tests/test_lane_profile.sh | tail -1; bash harness-ports/tests/test_pc_lane.sh | tail -1
lane profile: 24 passed, 0 failed
67 passed, 0 failed
```
