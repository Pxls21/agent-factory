# PC lane H1B-SMOKE (task #365, D-108 item 7): does LCM-X load in a real lane, and which of its tools does the lane see

PIN: 03ad1b6 (the origin head at authoring). Role: code-implementer. Route: the LOCAL build route
(`agentfactory-build-local`, medium; D-061/D-062: local only). Claim nothing about which model you are; the harvest
measures it. Venue: `tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey ultra, Lever-2: the report is DATA. Keep your
context small. Do NOT spawn subagents. This lane changes NO file: it is a smoke run that gathers evidence.

AUTHORIZATION AND LIMITS: first-party work on the owner's PC. The owner asked for LCM-X in the Hermes lanes (D-108 item
7). This lane runs with the LCM-X context engine (`LANE_CONTEXT_ENGINE=lcm-x`); the coordinator watches its egress from
outside. Never read a secret, a real profile's `.env`, `~/.hermes/` or any `*.env`. No network beyond your model route.
No server touch. No outward-facing action. Write only your report.

## WHY

H1a built an opt-in lane mode that gives ONE lane profile the LCM-X context engine (`docs/HARNESS-PORTS.md` §7, "LCM-X
lane mode"). VERIFY-H1a (`tasks/briefs/jev-trim/VERIFY-H1A-report.md`) found it sound in the sandbox but could not run
Hermes or LCM-X. This lane is the first real load: the coordinator needs to know what the lane itself sees.

## CONTRACT (evidence only; change nothing)

1. **Premise.** Re-run the block below; stop and report on any mismatch.
2. **Your LCM tools.** List, by exact name, every tool in your own tool list whose name starts with `lcm_`, and nothing
   else. The mode means to leave ON `lcm_status`, `lcm_inspect` and `lcm_recent`, and OFF these twelve: `lcm_grep`,
   `lcm_recall`, `lcm_load_session`, `lcm_describe`, `lcm_expand`, `lcm_expand_query`, `lcm_evidence_pack`,
   `lcm_compile_evidence`, `lcm_compute`, `lcm_query_state`, `lcm_retrieve`, `lcm_doctor`. Report what you actually see;
   do not infer it from this list. If you have no `lcm_` tool at all, say so plainly: that is a finding, not a failure.
3. **`lcm_status`.** If you have it, call it once and paste its whole output verbatim. If you do not, write "no
   lcm_status tool".
4. **A little real work, so the engine has turns to ingest.** Run `wc -l pc-lane.lock.yaml
   harness-ports/bin/lane-profile.sh docs/HARNESS-PORTS.md` and `git -C . log -1 --format=%h` in your lane tree, and paste
   both outputs.
5. **`lcm_status` again** after item 4, if you have it; paste it verbatim.

## REPORT

Your final message is the report: the premise re-run, items 2 to 5 with their pasted outputs, and anything unexpected
you saw (a warning about a context engine or a plugin, a refused tool call). NOT done, first-class.

## PREMISE — MEASURED at authoring (2026-09-29, sandbox main tree@03ad1b6; PIN origin 03ad1b6)

Printed by `bash scripts/premise_block.sh` from the sandbox main tree at origin 03ad1b6. Re-run every `$` line from your
lane tree (it is checked out at the PIN). Expected to differ: nothing; on any difference, stop and report
CONTRACT-INVALID with the diff.

```
$ git rev-parse --short=7 HEAD
03ad1b6
$ git log -1 --format=%s -- harness-ports/bin/lane-profile.sh | cut -c1-70
H1a landed (task #365; GATED-PENDING-VERIFY): the LCM-X lane mode, its
$ sha256sum pc-lane.lock.yaml harness-ports/bin/lane-profile.sh harness-ports/bin/pc-lane.sh scripts/pc_lane.sh | cut -c1-16,65-
e717400c2ec4f3d3  pc-lane.lock.yaml
ea884902f57fd601  harness-ports/bin/lane-profile.sh
b48bceaab26d4c18  harness-ports/bin/pc-lane.sh
dbe4b983157c7581  scripts/pc_lane.sh
$ grep -n '^LCM_X_TOOLS_OFF=' harness-ports/bin/lane-profile.sh
33:LCM_X_TOOLS_OFF="lcm_grep,lcm_recall,lcm_load_session,lcm_describe,lcm_expand,lcm_expand_query,lcm_evidence_pack"
34:LCM_X_TOOLS_OFF="$LCM_X_TOOLS_OFF,lcm_compile_evidence,lcm_compute,lcm_query_state,lcm_retrieve,lcm_doctor"
$ grep -c 'lcm_' harness-ports/bin/lane-profile.sh
16
```
