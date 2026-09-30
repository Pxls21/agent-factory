# PC lane SCRUB2-A: the PIN's scrubber first, the new rules after it (task #321, D-117; the D-115 review's option A)

PIN: 631dc86 (CI run #1181 passed). Role: code-implementer. Route: the raw local id `qwen-local/qwen3.8-27b-local`
(D-114: the local model only, no cloud fallback). Claim nothing about which model you are. Venue:
`tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey ultra, Lever-2: the report is DATA (files:lines, pasted outputs,
discrepancies, NOT done). Do NOT spawn subagents. Authored 2026-09-30 10:4xZ by the coordinator.

AUTHORIZATION AND LIMITS: first-party security work on the owner's own transcript scrubber. Every secret in a test or a
probe is a FAKE built at run time (`secrets.token_hex`). Never read a real secret: no `.env`, no key file, nothing under
`~/.hermes/`, `/root/`, `~/.config/`. No network beyond your model route. No outward-facing action. Change only the
files listed under BOUNDARY, in your lane tree.

## KEEP YOUR CONTEXT SMALL

Your model's window is 131,072 tokens. Read files by line range or with `grep -n`, never whole (the exporter is 383
lines: read it in two ranges). Cap each command's output (`| tail -40`, `grep -c`, `wc -l`). Run each test gate with
`-q` and read only its summary lines. Append each finished section to `$LANE_REPORT_DRAFT` as you go (VENUE-MAP), so a
resume can finish from it. If a request fails for its length, finish the draft's NOT done and stop.

## YOUR TREE AT START

The dispatcher applied `tasks/briefs/system1/SCRUB2-A-lane.patch` on the PIN (`git apply --index`; 3 new files):
- `tasks/briefs/system1/vscrub2r4/vscrub2r1r4_red.py`: VERIFY-SCRUB2-R1-R4's 12 red items (R4V-1);
- `tasks/briefs/system1/scrubA/f1probe.py`: F1's 28 cells, one fake each; it prints `hid` or `LEAK` per cell;
- `tasks/briefs/system1/scrubA/f7time.py`: `scrub()`'s time on a dash run and on BEGIN heads with no END.

Check first: `git diff --cached --stat` names those 3 files. If it does not, stop and report CONTRACT-INVALID.

## WHY

Five verify rounds of this repair were NOT-READY, and one class of blocker came back four times: a change to where one
rule's value ends left a later rule's head unread, and a value the PIN hid showed. The owner chose the review's option A
(D-117, `docs/08_DECISION_LOG.md`). Read `tasks/briefs/system1/SCRUB2-R1-D115-REVIEW.md`, its sections "The assumption
that failed" and "A. REDESIGN" (about 45 lines). Do not read the round patches whole.

The construction in one line: the PIN's scrubber runs first and whole, and the new rules run after it, on its output. A
substitution writes a marker or keeps text; it never writes text that was not in its input. So a new rule can hide more,
but it can never show a value the PIN hid.

The PIN's scrubber is `scripts/transcript_export.py` at the PIN (sha256 prefix 6ad316dc, last changed by cdbc1b8).

## CONTRACT

1. **Premise.** Re-run the block at the end from your lane tree; on any difference, stop and report CONTRACT-INVALID
   with the diff. Then the check in YOUR TREE AT START.

2. **The construction.**
   - `scrub(text)`: the PIN's `SECRET_PATTERNS`, all of them, in the PIN's order (`scripts/transcript_export.py:70-126`),
     then the new rules, each over that output. The PIN's entries keep their bytes, except F7's one rule (item 3).
   - `scrub_payload(text, opaque=None)`: the PIN's whole body (`:182-194`: the named rules, `PAYLOAD_PATTERNS`, then the
     opaque rule), unchanged, then the new rules.
   - `scrub_strict` calls `scrub_payload` and needs no change; `RUN_SHAPES` stays as it is.
   - Put the new rules in a list of their own (for example `LATE_PATTERNS`), as `(re.Pattern, replacement)` pairs like
     every other list: tests and `scripts/session_export.py` read the lists' entries (`tests/test_transcript_export.py:693`,
     `:734`, `:1140`; `scripts/session_export.py:803-806`).
   - Nothing else from rounds 1 to 5: no stops, no order inside the PIN's rules, no keep branch, no shield.
   - Write, in a comment above the new list and in your report, why no loss can happen.
   - Add a test that fails when the new rules run BEFORE the PIN's rules (mutant M1 below): pick a red item or a case
     of your differential (item 6) that M1 fails on, and show M1 failing it.

3. **F7: the lenient private-key rule becomes linear (the one PIN rule that changes).** It is the second entry of
   `SECRET_PATTERNS` (`:81-83`). On a run of dashes, and on BEGIN heads with no END, it is quadratic. Measured at
   authoring with `python3 tasks/briefs/system1/scrubA/f7time.py scripts/transcript_export.py` at the PIN (the time goes
   up four times when the size doubles):
   ```
   dashes   5000: 0.200 s
   dashes  10000: 0.801 s
   no-END heads  1000: 0.198 s
   no-END heads  2000: 0.753 s
   ```
   - Make it linear on both shapes. It stays one compiled `re.Pattern` with the same replacement, in the same place.
   - It hides every span the PIN's rule hides. Prove it with a differential test: generated texts (dash runs of many
     lengths; BEGIN and END lines with 3 to 6 dashes; spaces and tabs beside the dashes; `PRIVATE` or `SECRET`; `KEY` or
     `KEY BLOCK`; two blocks in a row; a BEGIN with no END; text around them), a fixed seed, at least 5,000 texts. For
     each text, every character the PIN's rule replaces is replaced by yours.
   - A timing test on both shapes at a size where the PIN's rule takes over 1 s (for example 20,000 dashes and 4,000
     heads), with a bound that the PIN's rule fails and yours passes by a wide margin. Show the PIN's rule failing it.
     The test file already has tests of this kind (`test_r1_rules_stay_linear_on_long_runs`, `:655`): follow them.

4. **The new rules: F1's contexts.** `python3 tasks/briefs/system1/scrubA/f1probe.py scripts/transcript_export.py`
   prints 28 cells. At the PIN, measured at authoring, 17 are `LEAK`:
   - `pwd=`, `credentials=` and `Cookie: sid=`: at a line start and after a tab in canonical JSON (the escape's letter
     `n` or `t` comes right before the name), in a JSON document inside a tool input (escaped quotes), and after a
     literal backslash-n in chat text, in both writers;
   - `Cookie: sid=` right after a non-ASCII letter (`caféCookie: sid=...`);
   - `Authorization: Token` in a JSON document inside a tool input.

   The first verify's evidence is `tasks/briefs/system1/VERIFY-SCRUB2-report.md:159-190` (its section 5a). The
   mechanism: the Cookie rule's `\b` and the pwd and credentials rules' `(?<![A-Za-z0-9])` fail after an escape's
   letter or a non-ASCII letter, and these rules take a bare quote only, where the provider rules have `_KEY_L`'s escape
   lookbehinds (`:67`) and the payload rules take `\\*["']`.
   - After your change, all 28 cells read `hid`. Put the 28 cells in `tests/test_transcript_export.py` as one
     parametrized test (red first: show it failing at the PIN). Also end to end: through `export()` with `sources=()`
     (the digest writer) and through `session_export.convert()` (the session writer), as the PIN's
     `test_scrub2_shapes_never_reach_the_session_export` (`:1255`) does.
   - Keep the PIN rules' floors: a value needs 8 characters, and a pwd or credentials value that starts with one of
     `/ ~ . $ \` stays (a path or a reference).
   - Rounds 1 to 4 wrote rules for these heads (`tasks/briefs/system1/SCRUB2-R1-R4.patch`; READ it with `grep -n`, never
     whole). Take what serves; leave the stops, the order, the keep branch and the shield.
   - Every new rule's value class is linear (item 5).

5. **Linear time on backslash rows (B1's class).** For each new rule, a timing test on its head followed by a long run
   of backslash content: a run of backslashes; a run of backslash-quote pairs; a run of backslash-letter pairs (the two
   characters `\n`). Take 64,000 characters, double it once, and show the time about doubles, not four times. Pick the
   bound so that a quadratic class fails it, and show one such class failing.

6. **Zero losses against the PIN.**
   - Move the items of the three red files into `tests/test_transcript_export.py` with their bodies and assertions
     unchanged; adapt only the module loader and the helpers to the file's own:
     `tasks/briefs/system1/vscrub2r2/vscrub2r1r2_red.py` (16 items), `tasks/briefs/system1/vscrub2r3/vscrub2r1r3_red.py`
     (11) and `tasks/briefs/system1/vscrub2r4/vscrub2r1r4_red.py` (12). Measured at authoring: all 39 pass on the PIN's
     scrubber (a scratch copy of the three files beside a link to `scripts/`: `39 passed`). All 39 pass on yours.
   - A differential test with a fixed seed, at least 10,000 texts. Each text: a fake value after a head the PIN reads
     (each `_NAME` and `_WORD` name, Bearer, Cookie, the Authorization schemes, pwd, credentials, the provider keys, a
     bridge link, and each `PAYLOAD_PATTERNS` head: the escaped-quote credential, URL userinfo, curl `-u`, a PASS name),
     in one of these contexts: plain, line start, after a tab, after a JSON escape, in canonical JSON, behind escaped
     quotes, after a non-ASCII letter, glued to the text before. Each text also holds one of your new rules' heads in an
     F1 context, before or around the PIN's head. Run each through `scrub`, `scrub_payload`, and `scrub_payload` to a
     fixed point on canonical JSON (the red files' `_settle`). Assert that every value the PIN hides stays hidden. Report
     the counts: texts, values the PIN hides, losses (must be 0), values only yours hides.
   - A loss is never repaired inside this lane. If you find one, report its text (fakes only) and stop: one loss against
     the PIN means the construction is wrong at its root (the review), and the owner decides.

7. **Measure and paste.**
   - (a) The ordinary-text cost. `scrub()` over each `transcripts/sandbox/*.md` at the PIN (22 files), before and after
     your change: the files and regions that change, and for each region its head and whether the value is
     secret-shaped. Then the same over each tracked `*.md` file (`git ls-files '*.md'`). Paste each region as
     `<file>:<line> <head> <value shape>` (a masked shape, never the value).
   - (b) Time `scrub()` and `scrub_payload()` over the 22 digests, best of 3, at the PIN and after.
   - (c) The dataset manifest `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json` records
     the sha256 of `scripts/transcript_export.py` (one line). Set that line to your final file's sha256; no other line
     changes. Then run `tests/test_laya_ft.py` and `tests/test_s1_synth.py`. The Laya lock itself (the dataset's items
     rebuilt and compared) is the coordinator's landing step in the sandbox, not yours.

8. **session_export.** `gate_patterns()` (`scripts/session_export.py:803-806`) zips `PATTERN_NAMES` with
   `SECRET_PATTERNS + PAYLOAD_PATTERNS` and falls back to `pattern-N` names when the counts differ. Add your list to the
   gate, with one name per new rule in `PATTERN_NAMES`. `tests/test_session_export.py` keeps passing, and a test pins
   each new name to a probe its rule changes.

9. **Mutants.** Your driver's control first (the unmutated file kills nothing), bytecode off, a fresh copy per mutant.
   Each must be killed by your tests: M1 the new rules run before the PIN's; M2 F7's rule back to the PIN's bytes; M3
   each new rule removed, one at a time; M4 each new rule's left anchor back to `\b` or `(?<![A-Za-z0-9])`; M5 a new
   value class that also takes a quote. Paste the table.

10. **Gates.** Every test file that names the scrubber, run twice with `python -m pytest -n 8 -q -p no:cacheprovider
    --basetemp ../scratch/bt<N>`, each call under the 420 s terminal cap (split the list across calls):
    `tests/test_transcript_export.py tests/test_session_export.py tests/test_jev_relay.py tests/test_jev_client.py
    tests/test_jev_context.py tests/test_jev_locate_echo.py tests/test_decisions_canonical.py
    tests/test_edit_snapshot_ap_screen.py tests/test_push_clean_lock.py tests/test_s1_rate.py tests/test_s1_synth.py
    tests/test_laya_ft.py`. Paste each summary line. Known: on the PC, `tests/test_push_clean_lock.py` gives `1 passed,
    23 errors` at the PIN (the lane's hook refuses `git push`; round 5Q proved it at the PIN); report the same count. Any
    other red test you did not cause: prove it red at the PIN too (a clean worktree at the PIN, `git worktree add
    --detach`), then report it. Never change a test to make it pass unless you prove the test was wrong.

## BOUNDARY

- MODIFY: `scripts/transcript_export.py` (F7's rule, the new list, `scrub`, `scrub_payload`), `scripts/session_export.py`
  (`PATTERN_NAMES` and `gate_patterns` only), `tests/test_transcript_export.py`, `tests/test_session_export.py`, and the
  dataset manifest's one line.
- READ: every other file. Leave the three files of the lane patch as they are.
- Not in this contract: F15 (the PIN's credentials rule takes the next line in the raw view; it stays, a stated
  over-redaction with no leak); F2 (the Negotiate scheme); the value gate (`known_values`, `value_hits`, `export()`'s
  refusal); gitleaks (task #403, after this lands and its verify passes).

## REPORT

Your final message is the report: the premise re-run; the construction and why no loss can happen; F7's form, its
differential counts and its timing table; each new rule (head, contexts, value class, floor), with f1probe's 28 cells
after; the red items; the differential's counts; item 7's measurements; the gate summaries; the mutant table;
DISCREPANCIES; NOT done, first-class. The dispatcher fetches your tree's diff; commit nothing.

## PREMISE — MEASURED at authoring (2026-09-30, sandbox main tree; PIN origin 631dc86)

Printed by `bash scripts/premise_block.sh` from the sandbox main tree. Every line reads committed objects at the PIN, so
it reads the same in your lane tree. Expected to differ: nothing. On any difference, stop and report CONTRACT-INVALID with
the diff.

```
$ git merge-base --is-ancestor 631dc86 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ for f in scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json; do printf '%s %s\n' "$(git show 631dc86:$f | sha256sum | cut -c1-16)" "$f"; done
6ad316dccfca0147 scripts/transcript_export.py
68c712893ffed4e9 scripts/session_export.py
5b22cc0040767dc7 tests/test_transcript_export.py
101298e96f776997 tests/test_session_export.py
a2e6143c0543f640 docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
$ git log -1 --format=%h 631dc86 -- scripts/transcript_export.py
cdbc1b8
$ git show 631dc86:scripts/transcript_export.py | grep -n '^SECRET_PATTERNS = \|^def scrub(\|^PAYLOAD_PATTERNS = \|^def scrub_payload(\|^def scrub_strict(\|^RUN_SHAPES = \|^_KEY_L = '
67:_KEY_L = r"(?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])|(?<=\\u[0-9A-Fa-f]{4}))"
70:SECRET_PATTERNS = [
129:def scrub(text: str) -> str:
142:PAYLOAD_PATTERNS = [
182:def scrub_payload(text: str, opaque=None) -> str:
211:RUN_SHAPES = tuple([p for p, r in SECRET_PATTERNS if r == OPAQUE_MARK] + [_KEY_RUN, re.compile(_TOKEN + r"{12,}")])
228:def scrub_strict(text: str, opaque=None, keep=()) -> str:
$ git show 631dc86:scripts/transcript_export.py | grep -n 'BEGIN \[A-Z0-9 \]\|(?i:\\b(?:set-)?cookie)\|(?i:pwd)\|(?i:credentials)\|(?i:authorization)\[' | cut -c1-90
75:    (re.compile(r"-----BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?-----.*?"
81:    (re.compile(r"-{3,}[ \t]*BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?[ \t]*-{3
95:    (re.compile(r"((?i:\b(?:set-)?cookie)[\"']?\s*:\s*[\"']?)(?=[^\r\n\"']*=[^\s;\"']{8
98:    (re.compile(r"((?i:authorization)[\"']?\s*:\s*[\"']?(?i:token|basic|bearer|digest|n
103:    (re.compile(r"((?<![A-Za-z0-9])(?i:pwd)[\"']?\s*[:=]\s*[\"']?)(?![/~.$\\])(?=[^\s\
105:    (re.compile(r"((?<![A-Za-z0-9])(?i:credentials)(?:[\"']\s*:|\s*=)\s*[\"']?)(?![/~.
$ git show 631dc86:scripts/session_export.py | grep -n '^PATTERN_NAMES = \|^def gate_patterns'
136:PATTERN_NAMES = ("private-key", "private-key-malformed", "credential", "bearer", "cookie", "authorization-scheme", "pwd",
803:def gate_patterns():
$ for f in tasks/briefs/system1/vscrub2r2/vscrub2r1r2_red.py tasks/briefs/system1/vscrub2r3/vscrub2r1r3_red.py tasks/briefs/system1/SCRUB2-R1-D115-REVIEW.md tasks/briefs/system1/SCRUB2-R1-R4.patch; do printf '%s %s\n' "$(git show 631dc86:$f | sha256sum | cut -c1-16)" "$f"; done
8498307a91f35f8c tasks/briefs/system1/vscrub2r2/vscrub2r1r2_red.py
10fac0733a8cbfb0 tasks/briefs/system1/vscrub2r3/vscrub2r1r3_red.py
f373783f9fb67394 tasks/briefs/system1/SCRUB2-R1-D115-REVIEW.md
f18f85c9b0abaf7b tasks/briefs/system1/SCRUB2-R1-R4.patch
$ git show 631dc86:tasks/briefs/system1/vscrub2r2/vscrub2r1r2_red.py | grep -c '^def test_'
4
$ git show 631dc86:tasks/briefs/system1/vscrub2r3/vscrub2r1r3_red.py | grep -c '^def test_'
3
$ git show 631dc86:docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json | grep -c 'scripts/transcript_export.py'
1
$ git ls-tree --name-only 631dc86 transcripts/sandbox/ | wc -l
22
```
