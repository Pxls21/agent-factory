# SCRUB2-R1: the scrubber repair wave after VERIFY-SCRUB2 (task #321)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/SCRUB2-R1-report.md` (write
it incrementally from the start). PIN: origin 7a050b6 (re-pinned at dispatch from 626fc4c; the scrubber files are SCRUB2's bytes, unchanged since cdbc1b8).
The contract: `tasks/briefs/system1/SCRUB2-brief.md`. Its items 1-8 hold in full, and this round leaves every one of them
true. The findings: `tasks/briefs/system1/VERIFY-SCRUB2-report.md`, section 14 (the inventory) and section 15 (the gate).
The verifier's reproduction scripts sit in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2/`.
Run anything that could reach a real secret source through the masking runner `.../scratchpad/vscrub1/masked.sh`, as the
verifier did.

## WHY

VERIFY-SCRUB2 returned NOT-READY on three blockers, each reproduced through the production writers. The coordinator
confirms both readings the verifier left open. F7 blocks: AF-AP-152 names this file, and every rule in it runs in linear
time. F15 blocks: item 3's cost rule makes a rule's ordinary-text cost part of the evidence, and the stated cost was false.
The scrubber runs on every push's transcript sync and on every session export. SYNTH1's candidates (`scripts/s1_synth.py`,
landed) scrub every item with it before a Laya dataset is committed.

## CONTRACT (this round)

1. **F1 and F15, one root.** The three named rules (`Cookie:`, `pwd=`, `credentials=`, lines 95, 103 and 105 at the PIN):
   - They treat a JSON escape as an escape before the name, as `_KEY_L` does for the provider rules (line 67).
   - Inside the value, an escaped newline or tab is not a value character.
   - They take an escaped quote as the payload rules do, and never the backslash of a closing `\"` (F5).
   Every context F1 lists redacts, through `export()` and `convert()`: a line start, after a tab, after a literal `\n`,
   after a non-ASCII letter, and a JSON document inside a tool input with escaped quotes. F15's shapes stop
   over-redacting: `Client(credentials=None)` keeps the next line's text. Each changed rule's ordinary-text cost on the
   corpus goes in the report with its count and your reason (item 3).
2. **F7.** The lenient private-key rule (line 81) runs in linear time: a start guard, and a bound for BEGIN heads with no
   END. A timing test runs a long dash run (at least 60,000 dashes) and many BEGIN heads with no END. It has a wall-time
   bound that the PIN's rule fails and the new rule passes with a wide margin. Check every rule in the file for the same
   class, and say why AF-AP-152's edit screen did not fire on line 81 (report it; the screen is not in your boundary).
3. **Cheap folds, all in the boundary:**
   - F2: `Authorization: Negotiate <token>` redacts the token, so the report's D4 becomes true.
   - F10: a test maps each `session_export.PATTERN_NAMES` name to a probe its rule changes.
   - F12: one assertion per surviving mutant W1-W5, W7, W8, W10, W13-W15.
4. **Not in this round:** F3's shapes, the AWS and JWT shapes of task #319 (the next increment), F8, F16, F17.
5. **Everything else stays true:**
   - Item 6: re-run the measurement rows for each changed rule. No redaction the PIN makes may be lost, except the
     over-redactions F15 names.
   - Item 5: the value gate.
   - Item 4: test isolation (no committed test opens a real source).
   - Item 8: the Laya lock (the builder's pre-fit comparison again). Report the item counts.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. For F1, F7 and F15: the verifier's reproduction command, run before and after the change (LEAK or STALL before, none
   after), pasted.
3. The tests for items 1-3, each with a named mutant that reds it as a FAILED test (AF-AP-223). The verifier's 28 mutants
   (`mutate3.py`) re-run: the eleven survivors of F12 now killed.
4. `bash scripts/test_summary.sh` twice on the floor's set below (12 files; the set id is in the premise), with its set id. Every red is fixed, or named with its
   cause.
5. pyflakes rc 0; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
6. NOT-done and DISCREPANCIES.

## BOUNDARY

- MODIFY: `scripts/transcript_export.py`, `tests/test_transcript_export.py`.
- MODIFY only if needed: `scripts/known_values_check.py` and `tests/test_known_values_check.py`; `scripts/session_export.py`
  and `tests/test_session_export.py` (only the `PATTERN_NAMES` order and names, and the F10 test).
- MODIFY by the builder's step: the two `docs/research/findings/laya-ft-labels/*/dataset-manifest.json`, their code hash only.
- CREATE: your report.
- READ everything else.

## STANDING RULES

- No git writes, no PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables. The exporter's default sources
  are never exercised. Test secrets are fake strings built at run time.
- No other sandbox lane holds this tree at dispatch (the lanes named at authoring are home). If the coordinator dispatches
  one later, its files are listed in `.lanes-live`; never touch them. Touch only your boundary.
- The disk is shared (about 1.8G free at dispatch): scratch under 200 MB in `.../scratchpad/scrub2r1/`, deleted as you go; a short
  `--basetemp`; never run the whole `tests/test_vendored_manifest.py`.
- Test counts are pasted from `scripts/test_summary.sh`. Stamps are substituted from `date -u`, never typed.
- Run long commands in one foreground call, each under 10 minutes. Kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text of
  its own (under 200 characters; a note only for a 0).

## PREMISE — MEASURED at authoring (2026-09-26 06:4xZ, the sandbox tree; HEAD's code = origin 626fc4c)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-60
626fc4c SYNTH1 report: two commit ids that the push rewrites
$ git log --oneline cdbc1b8..HEAD -- scripts/transcript_export.py scripts/known_values_check.py scripts/session_export.py | wc -l   (0 = the scrubber files are SCRUB2's bytes)
0
$ sed -n '64,70p;78,106p' scripts/transcript_export.py   (the rules the findings name: _KEY_L, the lenient PEM 81, the credential rule 88, the Cookie rule 95, pwd 103, credentials 105)

# The provider-key rules' anchors (their comment below says why): before a key no ASCII letter or digit, unless it is a
# JSON escape's own letter; after it no ASCII letter or digit.
_KEY_L = r"(?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])|(?<=\\u[0-9A-Fa-f]{4}))"
_KEY_R = r"(?![A-Za-z0-9])"

SECRET_PATTERNS = [
    # the same block with malformed header lines (3 or more dashes, spaces beside them; VERIFY-SCRUB1 F14), from BEGIN
    # through END. Unlike the rule above it needs the END line: without one, a line of prose about these headers hid
    # the rest of a tool result (SCRUB2 measured up to 15,522 characters on this session's transcripts).
    (re.compile(r"-{3,}[ \t]*BEGIN [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?[ \t]*-{3,}.*?"
                r"-{3,}[ \t]*END [A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?[ \t]*-{3,}", re.S),
     "<private-key-redacted>"),
    # explicit credential assignments / headers: the head is kept, the value (_VALUE) replaced. The 8-character floor reads
    # the whole run after the separator (the lookahead). Every piece of the value is redacted whatever its length: the run
    # was one value before AF-AP-157, so a floor on a piece would show bytes that were hidden. A head that is not in-run
    # ends the match before its name; the next match takes it with its own floor.
    (re.compile(r"(" + _NAME + r"[\"']?\s*[:=]\s*[\"']?)(?=" + _V + r"{8})(" + _VALUE + r")", re.I), _redact_run),
    # a Bearer token (case as written): the floor reads the whole run; the token stops before a following Bearer match and
    # a bridge link, which their rules take (a token that ate `Bearer` or `https` freed what followed: AF-AP-157)
    (re.compile(r"(Bearer\s+)(?=[A-Za-z0-9._\-]{8})(?:(?!" + _BEARER + r"|" + _LINK + r")[A-Za-z0-9._\-])+"),
     r"\1<redacted>"),
    # SCRUB2 (VERIFY-SCRUB1 F14), each shape measured on this session's transcripts before it went in (SCRUB2-report.md):
    # a Cookie header, from its head to the end of the line or a quote, when a `name=value` of 8+ characters is in it
    (re.compile(r"((?i:\b(?:set-)?cookie)[\"']?\s*:\s*[\"']?)(?=[^\r\n\"']*=[^\s;\"']{8})[^\r\n\"']+"), r"\1<redacted>"),
    # an Authorization header's credential after a known scheme (a bearer in any case too). Any word as the scheme took
    # prose after this repo's `AUTHORIZATION:` brief headings.
    (re.compile(r"((?i:authorization)[\"']?\s*:\s*[\"']?(?i:token|basic|bearer|digest|negotiate|ntlm|apikey|api-key|key"
                r"|ssws)\s+)(?=[A-Za-z0-9._~+/=\-]{8})[A-Za-z0-9._~+/=\-]+"), r"\1<redacted>"),
    # `pwd` and `credentials` assigned a value that is not a path or a reference (it starts with none of / ~ . $ \). As
    # names of the credential rule both took paths (`PWD=/home/...`), and `credentials` took Python annotations
    # (`credentials: LoginRequest`), so `credentials` needs `=` or a quoted key.
    (re.compile(r"((?<![A-Za-z0-9])(?i:pwd)[\"']?\s*[:=]\s*[\"']?)(?![/~.$\\])(?=[^\s\"'&,;]{8})[^\s\"'&,;]+"),
     r"\1<redacted>"),
    (re.compile(r"((?<![A-Za-z0-9])(?i:credentials)(?:[\"']\s*:|\s*=)\s*[\"']?)(?![/~.$\\])(?=[^\s\"'&,;]{8})"
                r"[^\s\"'&,;]+"), r"\1<redacted>"),
$ grep -n 'PATTERN_NAMES' scripts/session_export.py | head -2
136:PATTERN_NAMES = ("private-key", "private-key-malformed", "credential", "bearer", "cookie", "authorization-scheme", "pwd",
805:    names = PATTERN_NAMES if len(PATTERN_NAMES) == len(pats) else tuple("pattern-%d" % i for i in range(len(pats)))
$ ls <scratch>/vscrub2/*.py | xargs -n1 basename | tr '\n' ' '
agg.py anchors.py cred_convert.py cred_raw.py digests_at.py e2e.py e2e_timing.py escape_committed.py escape_corpus.py escape_named.py escape_nonascii.py exposure.py f6_aws_jwt.py frozen.py gate2.py gate3.py jsonbreak.py laya_run.py laya_v.py lost.py measure_v2.py mutate2_lane.py mutate3.py negotiate.py pemfix.py reasons.py reasons2.py shapes2.py timing.py timing_run.py 
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/masked.sh
$ grep -l -E 'transcript_export|known_values_check|session_export' tests/*.py | tr '\n' ' '
tests/test_decisions_canonical.py tests/test_edit_snapshot_ap_screen.py tests/test_jev_client.py tests/test_jev_context.py tests/test_jev_locate_echo.py tests/test_known_values_check.py tests/test_push_clean_lock.py tests/test_s1_rate.py tests/test_s1_synth.py tests/test_session_export.py tests/test_ship_to_pc.py tests/test_transcript_export.py 
$ bash scripts/test_summary.sh tests/test_decisions_canonical.py tests/test_edit_snapshot_ap_screen.py tests/test_jev_client.py tests/test_jev_context.py tests/test_jev_locate_echo.py tests/test_known_values_check.py tests/test_push_clean_lock.py tests/test_s1_rate.py tests/test_s1_synth.py tests/test_session_export.py tests/test_ship_to_pc.py tests/test_transcript_export.py   (the floor at the PIN; SYNTH1 landed, its round-2 edits not yet begun)
pytest-exit: 0
pytest-summary: 822 passed in 122.39s (0:02:02)
$ bash scripts/pc_suite.sh set-id -- <the same 12 files>
12 files set=27f27a25516b
```

## PREMISE — RE-MEASURED at dispatch (2026-09-26 07:5xZ, the sandbox tree; HEAD = origin 7a050b6, the tree clean)

The origin moved from 626fc4c to 7a050b6 (SYNTH1 round 2, HCTX1-R1, the I59-A reports). No scrubber file changed; the
floor's test set is the same 12 files, and `tests/test_s1_synth.py` gained tests, so the floor is now 824.

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-60
7a050b6 VERIFY-I59-A report: three commit ids that the push 
$ git log --oneline cdbc1b8..origin/claude/soundbox-kit-migration-iz1jwf -- scripts/transcript_export.py scripts/known_values_check.py scripts/session_export.py | wc -l
0
$ grep -l -E 'transcript_export|known_values_check|session_export' tests/*.py | tr '\n' ' '
tests/test_decisions_canonical.py tests/test_edit_snapshot_ap_screen.py tests/test_jev_client.py tests/test_jev_context.py tests/test_jev_locate_echo.py tests/test_known_values_check.py tests/test_push_clean_lock.py tests/test_s1_rate.py tests/test_s1_synth.py tests/test_session_export.py tests/test_ship_to_pc.py tests/test_transcript_export.py 
$ bash scripts/test_summary.sh <the same 12 files>   (the floor at 7a050b6)
pytest-exit: 0
pytest-summary: 824 passed in 122.05s (0:02:02)
$ bash scripts/pc_suite.sh set-id -- <the same 12 files>
12 files set=27f27a25516b
```
