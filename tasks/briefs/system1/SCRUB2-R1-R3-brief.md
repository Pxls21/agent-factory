# SCRUB2-R1 round 3: no redaction the pinned scrubber makes is lost (task #321)

Role: the SCRUB2-R1 builder, resumed (sandbox code-implementer, Opus 5.5). Authored 2026-09-28 20:4xZ by the coordinator.

VERIFY-SCRUB2-R1-R2 returned **NOT-READY** on two blockers (`tasks/briefs/system1/VERIFY-SCRUB2-R1-R2-report.md`, N1 and
N2). Both are losses under round 2's item 4 ("no redaction the PIN makes may be lost in any view"), which that round froze,
and no ruling covers either. So the coordinator rules them CORE-BLOCKING under D-034. This round is the one focused repair,
keyed by round 2's new production code. Everything else the verifier found holds (B1, B2, B3, D2's fix, D6 and D1 as ruled,
D7, F1, F15, F2, F7, F10, F12, the value gate, test isolation, the Laya lock). Keep all of it.

## CONTRACT (this round)

1. **N1.** The pwd and credentials floors count characters where the PIN counted characters. Round 2's `_VF`/`_VU` count a
   backslash pair, an odd run or a group of escapes as ONE unit, so an 8-character value with literal backslash content now
   shows where the PIN hid it: in the digest, in `convert()`'s text events and, for a literal pair, in canonical JSON.
   The verifier's direction: the pwd floor reads characters as the PIN's did (`(?=[^\s"'&,;]{8})`); the credentials floor
   counts the value's characters before its first escape, so F15's shapes keep their next line and D1 stays as ruled. Its
   feasibility candidate is `tasks/briefs/system1/vscrub2r2/candidate_n1.diff` (a starting point, not a spec: by its
   measurement it loses no token round 2 hides, loses 110 fewer overall, and all 298 committed items pass).
2. **N2.** A head the PIN never read (an escaped-quote head, `my_cookie:`, a head after a literal `\t` or `\r`) never frees
   a later value the PIN hid. Today such a head's value can run over a later pwd, credentials or Cookie head and stop right
   before that head's value (AF-AP-157). Direction: give such a head's value a stop before a later head that stands apart,
   as D2 did for the scheme rule with `_OTHER_HEAD`; running the Cookie rule after pwd and credentials is another option.
   Measure the cost of the one you choose, as round 2's item 6 asked.
3. **The red items.** The verifier's 16 (`tasks/briefs/system1/vscrub2r2/vscrub2r1r2_red.py`: N1 13, N2 3) go into
   `tests/test_transcript_export.py` with their bodies and assertions unchanged (adapt only the module loader and helpers to
   the file's own), and pass. At authoring they fail 16 of 16 on round 2 and pass 16 of 16 on the PIN (the premise).
4. **F-MUT.** One assertion per surviving mutant X3, X6, X7, X8, X10, X13 and X14 (the report's F-MUT table; the verifier's
   `mut.py` is under `.../scratchpad/vscrub2r2/probes/`), each killing its mutant.
5. **F-DOC.** The pwd and credentials comment (round 2's lines 191-195) states the floors' real cost.

## EVIDENCE DEMANDS

1. Premise: re-run the block below with `bash scripts/premise_block.sh` from the main tree; stop and report
   CONTRACT-INVALID on a difference in a lane file's hash.
2. The 16 red items pass; the verifier's end-to-end probes (`e2e_floor.py`, `e2e_n2.py`) and its differentials
   (`floor_units.py`, `rand_v4b.py`, `rl2_prov.py`), pointed at your code (they read the verifier's copy; adapt, never edit
   them in place), show 0 N1 and 0 N2 losses; paste the tables.
3. B1 stays linear (the verifier's `census2.py` on your code); the Laya lock: 0 of 6,220 v2 items and 0 of 1,788 v1 items
   differ from the PIN, and the dataset manifest is regenerated with the new sha256; D1 is kept as ruled.
4. Gates: round 2's floor set twice and the two changed test files, pasted with set ids; all through
   `.../scratchpad/vscrub1/masked.sh absent`.
5. NOT-done and DISCREPANCIES, first in the section.

## BOUNDARY

Your five files: `scripts/transcript_export.py`, `scripts/session_export.py`, `tests/test_transcript_export.py`,
`tests/test_session_export.py`, `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json`. Read the
verifier's scratch (`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r2/`), never write it.
Never edit `scripts/known_values_check.py` or the value gate's lines.

## STANDING RULES

- Do NOT spawn subagents. No git writes, no PC bridge, no outward-facing action (no PR, comment, issue or publish).
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables. Test secrets are fakes built at
  run time. Never read a `thinking` block's content in any transcript.
- Touch ONLY the files in the boundary; report adjacent defects, never fix them. Other lanes hold other files (`.lanes-live`).
- A private `--basetemp` outside every work tree for every pytest run (`mkdir -p` its parent); never run the whole
  `tests/test_vendored_manifest.py`. Test counts are pasted from `scripts/test_summary.sh` with their set ids
  (`scripts/pc_suite.sh set-id -- <files>`). Stamps come from `date -u`, never typed.
- Long commands in one foreground call each, under 10 minutes; kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text
  of its own.
- The harness refuses a subagent's report-file writes: return the whole round-3 section as the text of your final hand-back
  message, in full, never a summary.

## PREMISE — MEASURED at authoring (2026-09-28 20:4xZ, the main tree at the pushed head; `bash scripts/premise_block.sh`)

```
$ git rev-parse --short HEAD
0d06ae7
$ git status --porcelain -- scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
 M docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
 M scripts/session_export.py
 M scripts/transcript_export.py
 M tests/test_session_export.py
 M tests/test_transcript_export.py
$ sha256sum scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json | cut -c1-16,65-
e36f708b5515cd36  scripts/transcript_export.py
0462fe2e9bdd14bc  scripts/session_export.py
c917c5ccaf08074a  tests/test_transcript_export.py
c1bb29a1ec924a71  tests/test_session_export.py
8d5427fdac6ee5f8  docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
$ sha256sum tasks/briefs/system1/vscrub2r2/vscrub2r1r2_red.py tasks/briefs/system1/vscrub2r2/candidate_n1.diff | cut -c1-16,65-
8498307a91f35f8c  tasks/briefs/system1/vscrub2r2/vscrub2r1r2_red.py
7215866e517cc2e6  tasks/briefs/system1/vscrub2r2/candidate_n1.diff
$ rm -rf /tmp/scrub2r3-premise && mkdir -p /tmp/scrub2r3-premise/repo/tests /tmp/scrub2r3-premise/repo/scripts
$ cp scripts/transcript_export.py /tmp/scrub2r3-premise/repo/scripts/ && cp tasks/briefs/system1/vscrub2r2/vscrub2r1r2_red.py /tmp/scrub2r3-premise/repo/tests/test_vscrub2r1r2_red.py
$ cd /tmp/scrub2r3-premise/repo && python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/scrub2r3-premise/bt tests/test_vscrub2r1r2_red.py 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
16 failed
$ git -C /home/user/agent-factory show HEAD:scripts/transcript_export.py > /tmp/scrub2r3-premise/repo/scripts/transcript_export.py && cd /tmp/scrub2r3-premise/repo && python3 -m pytest -q -p no:cacheprovider --basetemp=/tmp/scrub2r3-premise/bt2 tests/test_vscrub2r1r2_red.py 2>&1 | tail -1 | sed -E 's/ in [0-9.]+s.*//'
16 passed
$ rm -rf /tmp/scrub2r3-premise
$ df -m / | tail -1
/dev/vda          258020 25790     12149  68% /
```
