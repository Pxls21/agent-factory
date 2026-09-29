# SCRUB2-R1 round 4: new heads run last, so no value the PIN hid can show (task #321, D-108)

Role: the SCRUB2-R1 builder, resumed (sandbox code-implementer, Opus 5.5). Authored 2026-09-29 10:5xZ by the coordinator.
The owner authorized this fourth round (D-108 item 3: "Do one more round for Scrubber. See if you can fix it."), past
D-031's repair budget. It is the last one: if its verify is NOT-READY, the owner decides what happens next.

VERIFY-SCRUB2-R1-R3 (`tasks/briefs/system1/VERIFY-SCRUB2-R1-R3-report.md`, READ it in full) returned **NOT-READY** on one
blocker, R3V-1 (N2R): a head the PIN never read can free a later value that `scrub_payload`'s PAYLOAD rules hid on the
PIN (the R1 escaped-quote credential, the PASS rule, curl's `-u "user:pass"`), and the value shows in
`session_export.convert()`'s events. Everything else it attacked holds (its list after the reproduction block). Your round
3 is held as `tasks/briefs/system1/SCRUB2-R1-R3.patch`; the shared tree is back at the PIN.

## Why a structural fix this time

Rounds 2 and 3 added stops, each naming the heads a new head's value must not run over, and each round's verifier found a
head the list missed: N2 in round 2, N2R in round 3 (the heads of the rules that run AFTER the new-head values in
`scrub_payload`). A stop list must name every later head, and three rounds show that list drifting. An ORDER needs no
list: once every rule that reads a head the PIN reads has run, the values those rules hide are already markers, so a new
head's value can run over a marker but can never free a value the PIN hid.

## CONTRACT (this round)

1. **The order (closes R3V-1 by construction).** In `scrub()` and in `scrub_payload()`, every rule or branch that reads a
   head the PIN never read runs AFTER every rule that reads a head the PIN reads, the PAYLOAD rules included. Round 3's
   new heads, as your round-3 report and the verifier name them: an escaped-quote head; a head after a literal `\t` or
   `\r`; `my_cookie:`-style names; a Cookie line after an escaped line end in canonical JSON (the Cookie rule's
   `(?(new)...)` branch: split it out of the PIN branch's regex); the pwd and credentials values of heads the PIN never
   read (`_LATER_PWD`, `_LATER_CRED`); the scheme token after an escaped quote. Round 3's changes to heads the PIN reads
   (the N1 floors, F15's value extent, D1 and D6 as ruled) stay where the PIN's rules run. Name the two stages in the
   code, and add a test that fails when a new-head rule is moved before a PIN-head rule.
   - The verifier's other route (stops before every later PAYLOAD head: `[:=]\s*\\+["']` after a `_NAMES` or `_PASS`
     name, `_PASS` names with `=` or `:`, `(?<![A-Za-z0-9_.\-])curl\b`) is the fallback, only for a shape where the
     order breaks a frozen item and a stop keeps it. Report each such shape with its measurement.
   - Is the order enough by itself? Measure it; do not assume it. The chains in R3V-1's mechanism point 4 (a freed head
     taking an R1 head as its value; the `<redacted>` marker's `>` satisfying `_KEY_L`) are the cases to check first.
2. **0 losses against the PIN, measured.** Point the verifier's probes at your code. They import the verifier's copies
   by fixed paths: adapt COPIES in your own scratch, never edit the originals. `e2e_n2r.py`; `rand_n2c.py` with seeds
   20260929 and 11 (4,000 texts x 6 views); `sch3.py` (the LATER and TOKEN classes); `r3d4.py`. Paste each table. Lost
   characters are 0 in every view, except the classes ruled before (F15's over-redactions, D1's K class, D6's name
   shown), each counted on its own row.
3. **The red items.** The verifier's 11 (`tasks/briefs/system1/vscrub2r3/vscrub2r1r3_red.py`, committed with this
   brief, sha256 prefix 10fac0733a8cbfb0) go into `tests/test_transcript_export.py` with their bodies and assertions
   unchanged (adapt only the module loader and helpers to the file's own), and pass. Round 2's 16 red items stay passing.
4. **R3V-2, the tail residual.** Re-measure it after the order (`r3d4.py`, `sch3.py`'s TOKEN class). If the PIN's Basic
   and bearer payload rules now hide those tails first, say so with the numbers. If a residual remains, report it per
   shape; the verifier's candidate (`_KEY_L` before the name in the scheme stop) is yours to try and measure.
5. **R3V-3.** Kill mutants V12 and V14 with the verifier's two examples (its R3V-3 section), each assertion named with
   its mutant.
6. **R3V-4.** The three comments the verifier lists state the invariant the code keeps after this round.
7. **Keep everything else** the verifier found holding: N1 closed; V4 per position; R3-D1, and R3-D3 in isolation; B1
   linear to 512,000 characters (`census3.py` with `retime3.py`); B2, B3; D2's fix; F1, F15, F2, F7, F10, F12; D1 and D6
   as ruled; the value gate byte-identical to the PIN's; test isolation; the Laya lock (0 of 6,220 v2 items and 0 of
   1,788 v1 items differ from the PIN, twice, with the controls firing); digest identity (21 of 21); the dataset
   manifest regenerated with the new sha256.

## WHERE YOU WORK: a worktree, never the shared tree (orchestration 0p)

The coordinator's pushes run `scripts/transcript_export.py` from the shared tree (the scrubbed transcript digests), so
a half-edited scrubber there would scrub a push. Your round 3 predates that rule; this round follows it.
- Make a detached worktree at the PIN under your own scratch: `git -c core.hooksPath=/dev/null worktree add -q --detach
  <W> <PIN>`. Apply round 3 there: `git -C <W> apply /home/user/agent-factory/tasks/briefs/system1/SCRUB2-R1-R3.patch`.
- Build on it there. Run every test and probe there through the masking runner:
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/masked.sh absent <W> -- ...` (the worktree holds no `.pc-bridge.env`).
- Your one deliverable in the shared tree: `tasks/briefs/system1/SCRUB2-R1-R4.patch`, the `git -C <W> diff` of the five
  files against the PIN (round 3 and round 4 together). Prove it applies (`git apply --check`) on a fresh worktree at the
  PIN, and that the red file and the two changed test files pass there.
- Remove every worktree you made, and stop every process you started, before you report.

## BOUNDARY

- MODIFY, in your worktree only: `scripts/transcript_export.py`, `scripts/session_export.py`,
  `tests/test_transcript_export.py`, `tests/test_session_export.py`,
  `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json`.
- CREATE, in the shared tree: `tasks/briefs/system1/SCRUB2-R1-R4.patch`. Nothing else in the shared tree.
- READ: the verifier's report and scratch (`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r3/`; never write it); your round-3 report
  (`tasks/briefs/system1/SCRUB2-R1-R3-report.md`); round 2's red items (`tasks/briefs/system1/vscrub2r2/`).
- Never edit `scripts/known_values_check.py` or the value gate's lines.

## EVIDENCE DEMANDS

1. Premise: re-run the block below with `bash scripts/premise_block.sh` from the main tree; stop and report
   CONTRACT-INVALID on a difference.
2. Red first: the 11 red items fail on round 3's code in your worktree before your change and pass after, each run
   pasted with its set id.
3. The tables for items 2 and 4; the order test failing on its mutant (a new-head rule moved first).
4. Gates, each twice, in your worktree through `masked.sh absent`, with `--basetemp` as a pytest ARGUMENT outside every
   work tree and counts pasted from `scripts/test_summary.sh` with set ids from `bash scripts/pc_suite.sh set-id --
   <files>`: round 2's floor set and the two changed test files. The mutation summary on your final bytes, the control
   first (AF-AP-223: check that the `--basetemp` parent exists before you count a kill).
5. The patch's proof (the worktree section).
6. NOT-done and DISCREPANCIES first in the report.

## STANDING RULES

- Do NOT spawn subagents. No git writes in the shared tree, no PC bridge, no outward-facing action (no PR, comment,
  issue or publish).
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables. Test secrets are fakes built
  at run time. Never read a `thinking` block's content in any transcript.
- A private `--basetemp` outside every work tree for every pytest run (`mkdir -p` its parent); never run the whole
  `tests/test_vendored_manifest.py`. Stamps come from `date -u`, never typed.
- Long commands in one foreground call each, under 10 minutes; kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- The harness refuses a subagent's report-file writes: return the whole round-4 report as the text of your final
  hand-back message, in full, never a summary.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin bef1e9e)

Printed by `bash scripts/premise_block.sh` from the main tree at the PIN, before this brief's commit. The PIN's scrubber
passes the verifier's 11 red items; round 3's scrubber (the patch applied to a copy; sha256 prefix f6fe76b2, the bytes the
verifier attacked) fails all 11. The last lines check that the verifier's probes and the masking runner exist in the
scratch. Expected to differ: nothing.

```
$ git merge-base --is-ancestor bef1e9e HEAD && echo bef1e9e-is-an-ancestor-of-HEAD
bef1e9e-is-an-ancestor-of-HEAD
$ git status --porcelain -- scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json | wc -l
0
$ sha256sum scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json | cut -c1-16,65-
6ad316dccfca0147  scripts/transcript_export.py
68c712893ffed4e9  scripts/session_export.py
5b22cc0040767dc7  tests/test_transcript_export.py
101298e96f776997  tests/test_session_export.py
a2e6143c0543f640  docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
$ sha256sum tasks/briefs/system1/SCRUB2-R1-R3.patch tasks/briefs/system1/vscrub2r3/vscrub2r1r3_red.py | cut -c1-16,65-
9a88a600e0afe2fd  tasks/briefs/system1/SCRUB2-R1-R3.patch
10fac0733a8cbfb0  tasks/briefs/system1/vscrub2r3/vscrub2r1r3_red.py
$ git apply --check tasks/briefs/system1/SCRUB2-R1-R3.patch && echo round-3-patch-applies-at-HEAD
round-3-patch-applies-at-HEAD
$ rm -rf /tmp/s4p && mkdir -p /tmp/s4p/pin/scripts /tmp/s4p/pin/tests /tmp/s4p/r3/scripts /tmp/s4p/r3/tests && echo scratch-ready
scratch-ready
$ cp scripts/transcript_export.py /tmp/s4p/pin/scripts/ && cp scripts/transcript_export.py /tmp/s4p/r3/scripts/ && echo pin-scrubber-copied
pin-scrubber-copied
$ (cd /tmp/s4p/r3 && git apply --include=scripts/transcript_export.py /home/user/agent-factory/tasks/briefs/system1/SCRUB2-R1-R3.patch) && sha256sum /tmp/s4p/r3/scripts/transcript_export.py | cut -c1-16
f6fe76b2b67d316a
$ cp tasks/briefs/system1/vscrub2r3/vscrub2r1r3_red.py /tmp/s4p/pin/tests/test_vscrub2r1r3_red.py && cp tasks/briefs/system1/vscrub2r3/vscrub2r1r3_red.py /tmp/s4p/r3/tests/test_vscrub2r1r3_red.py && echo red-file-copied
red-file-copied
$ (cd /tmp/s4p/pin && python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/s4p/bt-pin tests/test_vscrub2r1r3_red.py 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//')
11 passed
$ (cd /tmp/s4p/r3 && python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/s4p/bt-r3 tests/test_vscrub2r1r3_red.py 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//')
11 failed
$ rm -rf /tmp/s4p && echo scratch-removed
scratch-removed
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r3/probes/e2e_n2r.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r3/probes/rand_n2c.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r3/probes/sch3.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r3/probes/r3d4.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r3/probes/census3.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r3/probes/retime3.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/masked.sh | wc -l
7
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py tests/test_session_export.py | tail -1
2 files set=e8f27bcb91e7
```
