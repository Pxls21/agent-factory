# PC lane SCRUB2-R1 round 5: close the K-chain with a collision-proof shield (task #321, D-112)

PIN: 238fcf2 (the origin head at authoring). Role: code-implementer. Route: the LOCAL build route
(`agentfactory-build-local`; D-061/D-062 keep PC lanes local; D-112: the owner asked for the local Qwen model).
Claim nothing about which model you are. Venue: `tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey ultra, Lever-2:
the report is DATA (files:lines, pasted outputs, discrepancies, NOT done). Do NOT spawn subagents. Keep your context
small: read the files named here by line range, not whole.

AUTHORIZATION AND LIMITS: first-party security work on the owner's own transcript scrubber. Every secret in a test is a
FAKE built at run time (as the red file does with `secrets.token_hex`). Never read a real secret: no `.env`, no key
file, nothing under `~/.hermes/`, `/root/`, `~/.config/`. No network beyond your model route. No outward-facing action.
Change only the files in YOUR TREE listed under BOUNDARY.

## YOUR TREE AT START

The dispatcher applied `tasks/briefs/system1/SCRUB2-R1-R5-lane.patch` on the PIN before you started (`git apply
--index`; 6 files). It is rounds 3 and 4 of this repair (the five files of `tasks/briefs/system1/SCRUB2-R1-R4.patch`)
plus one new file: `tasks/briefs/system1/vscrub2r4/vscrub2r1r4_red.py`, the verifier's 12 red items for R4V-1.
Check it first: `git diff --cached --stat` names those 6 files. If it does not, stop and report CONTRACT-INVALID.

## WHY

Round 4 (the order: every rule that reads a head the PIN never read runs after every rule that reads a head the PIN
reads) closed its target. Its verifier found one new loss, R4V-1, the K-chain, and the coordinator upheld it
(`tasks/briefs/system1/VERIFY-SCRUB2-R1-R4-report.md`: read the coordinator note at its top, then the section
`### R4V-1 (BLOCKER, the ruling decides): the K-chain` and its `**Fix options:**`; skip the rest). In `scrub_payload`, D1 keeps a refused credentials value whole
(`_credentials_or_same`, `scripts/transcript_export.py:162`; `_CRED_FLOOR` at :132). A head INSIDE that kept value is
then read by a rule that runs after stage 1's credentials rule (a key rule, the link rule, or a PAYLOAD rule), its token
runs on and eats the NAME of a later head, and that later value, which the PIN hid, shows. `scrub()` is not affected.

The verifier measured a fix, "the shield" (feasibility only, not a patch to copy). Its hunk, on round 4's
`scrub_payload` (`scripts/transcript_export.py:372`):

```
kept = []
def shield(m):
    if m.group("value") is not None:
        return m.group(1) + "<redacted>"
    kept.append(m.group(0)[len(m.group(1)):])
    i = len(kept) - 1
    return m.group(1) + "<" + "".join(chr(0xE000 + ((i >> (4 * k)) & 15)) for k in range(8)) + ">"
after = False
late = []
for pat, rep in STAGE1_PATTERNS:
    if rep is _credentials_or_same:
        text = pat.sub(shield, text)
        after = True
        continue
    text = pat.sub(rep, text)
    if after:
        late.append((pat, rep))
for pat, rep in PAYLOAD_PATTERNS:
    text = pat.sub(rep, text)
for i, v in enumerate(kept):
    text = text.replace("<" + "".join(chr(0xE000 + ((i >> (4 * k)) & 15)) for k in range(8)) + ">", v)
for pat, rep in late + list(PAYLOAD_PATTERNS) + list(STAGE2_PATTERNS):
    text = pat.sub(rep, text)
# then the opaque rule, as today
```

In words: while the rules after the credentials rule run the first time, a kept value is a stand-in of the marker's
length, so they see what the PIN saw and hide the later values the PIN hid. Then the kept value comes back and those
rules run again, so the heads inside it are read too (round 4's gains stay). The verifier's numbers on this prototype:
all three red files pass (R4V-1's 12, R3's 11, R2's 16); `scrub_payload` takes x1.62 round 4's time on the 21 digests.
Its flaw: the stand-in is private-use characters, and a text that already holds them can collide with it.

## CONTRACT

1. **Premise.** Re-run the block at the end from your lane tree; on any difference, stop and report CONTRACT-INVALID
   with the diff. Then the check in YOUR TREE AT START.
2. **The shield, collision-proof, in `scrub_payload` only.** Implement the order above so that NO input text can make
   the restore put a kept value in the wrong place, drop one, or leave a stand-in in the output. You choose the form
   (for example: record each kept value's span and never let a later rule's match cross a stand-in; or pick stand-in
   characters proven absent from this input before you use them). Write, in a comment at the site and in your report,
   why your form cannot collide. `scrub()` does not change.
3. **The red items.** Move the 12 items of `tasks/briefs/system1/vscrub2r4/vscrub2r1r4_red.py` into
   `tests/test_transcript_export.py` with their bodies and assertions unchanged; adapt only the module loader and the
   helpers to the file's own. All 12 pass. The strict xfail at `tests/test_transcript_export.py:2052`
   (`reason="SCRUB2-R1 round 4: the K-chain residual of D1 and F15, left for a ruling"`) loses its marker and passes.
   Every other test in the file still passes (round 3's 11 and round 2's 16 red items among them).
4. **The collision test.** Add a test whose input holds the prototype's stand-in text (`<` + eight U+E000 characters +
   `>`) next to a refused credentials value and a later head, for example `x <stand-in> credentials=Z\tBearer
   k1a2b3c4d5e6f+X_PASS = V end` (`\t` a literal backslash and `t`; V a fake). It asserts V is hidden and the input's
   own stand-in text comes out unchanged. Measured at authoring: the PIN and round 4 keep the stand-in text; the
   verifier's prototype replaces it with the kept value (its output began `x Z\tBearer <redacted>`), so the test fails
   on the prototype. Show it failing on the prototype form (paste the run) and passing on yours.
5. **R4V-2 (a missing order test).** Add a test that fails when stage 1's credentials rule is moved after PAYLOAD in
   `scrub_payload` (the verifier's mutant A7). Its text is
   `credentials = jHAoL\fx9y8z7w6https://q1.trycloudflare.com/k6rMS4AuzM5y2,api_key=\"V\"`, where `\f` and `\"` are a
   literal backslash followed by `f` or by a quote (the red file's `B` helper builds them), and V is a fake built at run
   time. The test puts the text inside an event, writes it as canonical JSON (the red file's `_canon`), scrubs it to a
   fixed point (the red file's `_settle`) and asserts V is hidden (the red file's `_hidden`). The verifier measured
   this view on round 4's code: the PIN hides V, round 4 hides V, A7 shows V. Does your test fail with A7 applied to
   your final `scrub_payload`? Paste the run either way; if it does not fail, say why and what text would. The same text scrubbed as plain decoded text is an R4V-1 case (round 4 shows V there, the PIN hides
   it): after your shield it is hidden too; assert that in the same test.
6. **Measure and paste.** (a) `scrub()` output on every `transcripts/sandbox/*.md` at the PIN is byte-identical before
   and after your change (21 of 21). (b) Time `scrub()` and `scrub_payload()` over those 21 files, best of 3, before
   (round 4, your tree at start) and after. (c) The dataset manifest
   `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json` records the sha256 of
   `scripts/transcript_export.py`; set that one line to your final file's sha256 (round 4 changed only that line; no
   other line changes) and run the tests that check it (`tests/test_laya_ft.py`, `tests/test_s1_synth.py`).
7. **Gates.** Every test file that names the scrubber, run twice with `python -m pytest -n 8 -q -p no:cacheprovider`,
   each call under the 420 s terminal cap (split the list across calls if one call would pass it):
   `tests/test_transcript_export.py tests/test_session_export.py tests/test_jev_relay.py tests/test_jev_client.py
   tests/test_jev_context.py tests/test_jev_locate_echo.py tests/test_decisions_canonical.py
   tests/test_edit_snapshot_ap_screen.py tests/test_push_clean_lock.py tests/test_s1_rate.py tests/test_s1_synth.py
   tests/test_laya_ft.py`. Paste each summary line. A red test you did not cause: prove it red at the PIN too (a clean
   worktree at the PIN, `git worktree add --detach`), then report it; never change a test to make it pass unless you
   prove the test was wrong.

## BOUNDARY

MODIFY: `scripts/transcript_export.py` (`scrub_payload` and what it needs), `tests/test_transcript_export.py`,
`docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json` (the one sha256 line). READ: every
other file. Leave `tasks/briefs/system1/vscrub2r4/vscrub2r1r4_red.py` as it is.

## REPORT

Your final message is the report: the premise re-run; your shield's form and why it cannot collide; each test you
added, with the failing run for items 4 and 5; the measurements of item 6; the gate summaries of item 7;
DISCREPANCIES; NOT done, first-class. The dispatcher fetches your tree's diff; commit nothing.

## PREMISE — MEASURED at authoring (2026-09-29, sandbox main tree; PIN origin 238fcf2)

Printed by `bash scripts/premise_block.sh` from the sandbox main tree. Every line reads committed objects at the PIN, so
it reads the same in your lane tree, where the lane patch has changed the working files. `^### R4V-1` counts 2 because
`### R4V-10` shares the prefix. Expected to differ: nothing; on any difference, stop and report CONTRACT-INVALID with
the diff.

```
$ git merge-base --is-ancestor 238fcf2 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ git show 238fcf2:scripts/transcript_export.py | sha256sum | cut -c1-16
6ad316dccfca0147
$ git show 238fcf2:tests/test_transcript_export.py | sha256sum | cut -c1-16
5b22cc0040767dc7
$ git show 238fcf2:tasks/briefs/system1/SCRUB2-R1-R4.patch | sha256sum | cut -c1-16
f18f85c9b0abaf7b
$ git show 238fcf2:tasks/briefs/system1/SCRUB2-R1-R4.patch | grep -c '^diff --git'
5
$ git show 238fcf2:tasks/briefs/system1/VERIFY-SCRUB2-R1-R4-report.md | grep -c '^### R4V-1'
2
$ git ls-tree --name-only 238fcf2 transcripts/sandbox/ | wc -l
21
$ git show 238fcf2:docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json | grep -c 'scripts/transcript_export.py'
1
```
