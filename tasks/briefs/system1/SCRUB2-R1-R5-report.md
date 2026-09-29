> **Coordinator note (2026-09-29 23:0xZ, at harvest; the route is the coordinator's measurement, AF-AP-111).** This
> round ran on the HYBRID combo `agentfactory-build-local` (D-039), not on the raw Qwen id, so most of it is the
> cloud model's work, and it does not meet D-112 (a round built and tested on the local Qwen model). OmniRoute's
> call log for the lane (read-only; session tag `SCRUB2-R1-R5-brief.md--238fcf2`): Qwen served 50 turns from 20:40Z
> to 21:57Z, the main prompt growing to 99,232 tokens; at 21:57Z the combo moved the lane to
> `codex/gpt-5.6-sol-ultra` with a context handoff, and every later Qwen attempt carried a handoff as its first
> system message, which Qwen's chat template refuses (126 refusals); each refusal fell to codex, which served 127
> turns to 22:45Z (prompts 95k to 194k). Hermes never shrank the context (0 compacted messages). The owner's answer
> (D-114): the local model only. This patch is kept as a record and not applied; round 5 runs again on the raw id
> (`SCRUB2-R1-R5Q-brief.md`). The claims below are the builder's hypotheses; `scrub_payload` measured 1.52x slower
> (MEASUREMENTS).

NOT done: no commit or push. This build is a proposal pending the sandbox adversarial-verifier.

PREMISE

- All eight premise commands matched exactly:
  - `PIN-is-an-ancestor-of-HEAD`
  - SHA prefixes: `6ad316dccfca0147`, `5b22cc0040767dc7`, `f18f85c9b0abaf7b`
  - Counts: R4 patch files `5`, R4V-1 headings `2`, transcripts `21`, manifest entries `1`
- The staged tree contained exactly the six dispatched files.
- R4V-1 reproduced:
  - Round 4: `10 failed, 2 passed in 0.13s`
  - PIN: `12 passed in 0.06s`

IMPLEMENTATION

- `scripts/transcript_export.py:377`: implemented a collision-proof, span-tracked shield in `scrub_payload`.
  - Refused credentials values temporarily become ordinary `<redacted>` markers.
  - Only marker spans inserted by the shield are tracked. Identical text already present in the input is never treated as a stand-in.
  - Remaining stage-1 and first PAYLOAD substitutions run in the gaps around tracked spans.
  - Replacement-length deltas relocate each span.
  - Restore uses span identity, not marker text. No input can redirect a kept value, drop one, or leave a tracked stand-in.
  - Late stage-1, PAYLOAD, and stage-2 rules then run again, preserving round 4’s gains.
- `tests/test_transcript_export.py:2052`:
  - Removed the strict K-chain xfail.
  - Moved all 12 verifier red items with unchanged bodies and assertions, using the file’s existing loader and helpers.
  - Added the prototype-collision test.
  - Added the canonical and decoded R4V-2 order assertions.
- `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json:10` now records:
  - `81233a4092b2ea48a240157ee0e70176942c0288aeb1bbff3d460ee0ddf07072`
  - The live file hash matches.
- Only the three permitted boundary files received this round’s changes. `scrub()` and the dispatched red file remain unchanged.

NEGATIVE CONTROLS

- Prototype private-use stand-in:
  - Prototype: `value_hidden=True prototype_unchanged=False`, rc `1`
  - Its output began `x Z\tBearer credentials=Z\tBearer <redacted> = <redacted> end`
  - Final implementation: `value_hidden=True prototype_unchanged=True`, rc `0`
- R4V-2:
  - Production: `R4V-2 canonical and decoded assertions passed`, rc `0`
  - Mutant A7 applied to the final module: canonical assertion raised `AssertionError`, rc `1`
- Final R4V-1 scratch red file: `12 passed in 0.05s`
- Final standalone integrated scrubber file: `278 passed in 4.42s`

MEASUREMENTS

- `scrub()` output is byte-identical on all `21/21` committed sandbox digests.
- Interleaved best of three over the preloaded 21 digests:
  - `scrub before=3.3032s after=3.3597s ratio=1.017`
  - `scrub_payload before=5.2283s after=7.9375s ratio=1.518`

REQUIRED TEST EXECUTIONS

Split A, transcript/session/Jev files:

- `504 passed, 16 skipped in 19.92s`
- `504 passed, 16 skipped in 22.21s`

Split B, remaining six files:

- `422 passed, 17 skipped in 8.80s`
- `422 passed, 17 skipped in 9.33s`

Laya pair explicitly after the final hash:

- `50 passed, 17 skipped in 5.35s`
- Its second required execution is also included in each Split B run.

Static checks:

- Pyflakes rc `0`
- `git diff --check` rc `0`
- Manifest hash check: `True`
- AP screen:
  - Production: three pre-existing hits, AF-AP-204 x2 and AP-1 x1
  - Tests: three pre-existing hits, AP-66 x2 and AF-AP-80 x1
  - No hit is in this round’s hunks.
- `report_lint: 3 refs — OK 3, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`

DISCREPANCIES

- A long lane-local `--basetemp` made one git-probing session-export test fail on both final and clean PIN. Short `/tmp/scrub2-r5-*` paths made both required Split A runs pass. This matches the documented short-basetemp constraint.
- The lane git shim initially blocked nested fixture pushes, producing 23 errors. A focused clean-PIN test passed with its expected environment: `1 passed in 0.79s`. Using `/usr/bin/git` only inside fixture gates produced `24 passed in 3.79s`; no lane-repo push occurred.
- Seventeen Laya tests are sandbox-only and skipped loudly under the required PC venue. No real secret source was read.
- Final GitNexus `detect-changes` became unavailable because GitNexus 1.6.12 loaded Ladybug storage version 42 against index version 43. A second run reproduced it. I did not rebuild the read-only clone index. An earlier run reported 6 files, 22 changed symbols, 17 affected processes, and CRITICAL impact for `scrub_payload`.
- Ripwire `edit-check scripts/transcript_export.py` was ambiguous between two manifest definitions. `exercises scrub_payload` expected a path rather than a symbol.

SELF-ATTACK

- Wrong restore target: ruled out structurally by tracked inserted spans and the prototype-collision negative control.
- A regex crossing a shield: ruled out by gap-bounded matching and all 12 K-chain cases.
- Order regression: mutant A7 kills the canonical R4V-2 assertion; both final production views hide the fake value.

EVIDENCE TIERS

- VERIFIED: commands, counts, timings, hashes, file lines, negative controls, and test summaries above.
- INFERRED: collision impossibility follows from out-of-band span identity, gap-bounded matching, and deterministic span relocation.
- ASSUMED: none.

Retro: nothing additional to bake. The short-basetemp and lane git-shim constraints already exist in project instructions.
