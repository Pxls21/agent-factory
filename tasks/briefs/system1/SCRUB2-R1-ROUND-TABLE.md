# SCRUB2-R1: the round table (D-115), report of record

> **Coordinator note (2026-09-30 03:4xZ).** The hand-back of a read-only sandbox evidence-gatherer lane, saved verbatim
> below (harvest: every assistant turn on its pinned model, no refusal stop; hand-back sha256 prefix e01e1e97b03a). It is
> evidence only. The review that draws the conclusions is `tasks/briefs/system1/SCRUB2-R1-D115-REVIEW.md`. Two reading
> notes:
> - "D1" in §3 names a CLASS (AF-AP-157: a head's value or token runs over the next head's name). "D1" in RP2 (§1b, §2,
>   and step 1 of R4V-1) names a builder DECISION (a refused credentials value is kept whole). They are not the same.
> - A reference such as VR1:74 is a line of the file the Sources table names, at its committed bytes.

---

# SCRUB2-R1 round table (task #321, D-115): evidence only

This report has no verdict, recommendation, root cause or fix. The coordinator draws the conclusions.

**Sources.** All briefs and reports are under `/home/user/agent-factory/tasks/briefs/system1/`. Short names used below, with each file's first commit (`git log`). `git status` is clean for every file.

| Short | File | First commit |
|---|---|---|
| BR0 | SCRUB2-brief.md | 83e806c 2026-09-25T23:27Z (last 6f7a925 23:29Z) |
| RP0 | SCRUB2-report.md | cdbc1b8 2026-09-26T01:42Z |
| VR0 | VERIFY-SCRUB2-report.md | 67f1043 2026-09-26T06:25Z |
| BR1 | SCRUB2-R1-brief.md | 128430e 2026-09-26T06:43Z (last 9ecaeff 07:53Z) |
| RP1 | SCRUB2-R1-report.md | 818bbc2 2026-09-26T10:50Z |
| VR1 | VERIFY-SCRUB2-R1-report.md | 7df5f03 2026-09-28T12:49Z |
| BR2 | SCRUB2-R1-R2-brief.md | 7df5f03 2026-09-28T12:49Z |
| RP2 | SCRUB2-R1-R2-report.md | a774e6f 2026-09-28T18:22Z |
| VR2 | VERIFY-SCRUB2-R1-R2-report.md | 2d46ba8 2026-09-28T20:51Z |
| BR3 | SCRUB2-R1-R3-brief.md | 2d46ba8 2026-09-28T20:51Z |
| RP3 | SCRUB2-R1-R3-report.md | bfd8f59 2026-09-28T23:50Z |
| VR3 | VERIFY-SCRUB2-R1-R3-report.md | 0749fe5 2026-09-29T01:42Z |
| BR4 | SCRUB2-R1-R4-brief.md | 9dabbef 2026-09-29T10:57Z |
| RP4 | SCRUB2-R1-R4-report.md | 77e5a16 2026-09-29T15:59Z |
| VR4 | VERIFY-SCRUB2-R1-R4-report.md | 7cb1475 2026-09-29T19:06Z |
| BR5 | SCRUB2-R1-R5-brief.md | 30f002f 2026-09-29T20:30Z |
| RP5 | SCRUB2-R1-R5-report.md | 4618be3 2026-09-29T23:48Z |
| BR5Q | SCRUB2-R1-R5Q-brief.md | 4618be3 2026-09-29T23:48Z |

Other sources:
- **LEDGER** = `/home/user/agent-factory/todo/BUILD-TASKLIST.md`. Only the lines that name #321 were read. All are committed except :1827 (this dispatch), which is uncommitted in the working tree.
- **DLOG** = `/home/user/agent-factory/docs/08_DECISION_LOG.md`. D-115 is at :126 (commit f8f1350, 2026-09-30T03:06Z). D-031 :42, D-034 :45, D-108 :119, D-112 :123 and D-114 :125 were read for budget context.
- **CG** = `/home/user/agent-factory/.claude/skills/contract-gate/SKILL.md` §4, deadlock break at :79-95.

**What "the PIN" means (SOLID).**
- For rounds 1 to 5, the PIN is SCRUB2's landed exporter: cdbc1b8, sha256 prefix 6ad316dc (BR1:4; BR4:121; BR5Q:143-144).
- `git log cdbc1b8..HEAD -- scripts/transcript_export.py` gives 0 commits at HEAD baf8b5c, which equals origin.
- The five scrubber files have no working-tree change (run 2026-09-30).
- VR0 measured F1, F7 and F15 on those same bytes (VR0:4).
- LEDGER:1792 says "the tree keeps the PIN's scrubber (F1 and F15 open, no K-chain)". It does not name F7. F7's rule is in the same unchanged bytes. I did not re-time it.

---

## 1. The round table

### 1a. One row per verify round

| Round | Report | Build under test | Recommendation | Blockers | FOLLOW-UP count | Coordinator ruling | Row |
|---|---|---|---|---|---|---|---|
| R0 | VR0 | SCRUB2 as landed, cdbc1b8 (VR0:4) | NOT-READY (VR0:11, :512) | F1, F7, F15 | 3: F2 (:493), F10 (:501), F12 (:503) | Confirmed F7 and F15 as blockers. The verifier had left both readings open (VR0:513-515; LEDGER:1644) | SOLID |
| R1 | VR1 | Round-1 patch, exporter 014439fb (VR1:25) | NOT-READY (VR1:5-8) | B1, B2, B3 | 4 as labeled: V4 "needs your ruling" (:131), V5 (:143), V11 pre-existing (:190), V12 pre-existing (:194). 3 left after the ruling | Ruled V4 BLOCKING under item 5 (LEDGER:1670; BR2:9-10). 4 blockers as ruled | SOLID |
| R2 | VR2 | Round 2, exporter e36f708b (VR2:26) | NOT-READY (VR2:6) | N1, N2 | 2: F-MUT (:146), F-DOC (:164) | CORE-BLOCKING under D-034 (LEDGER:1697; BR3:5-7) | SOLID |
| R3 | VR3 | Round 3, exporter f6fe76b2 (VR3:55) | NOT-READY (VR3:11-13, :100) | R3V-1 | 3: R3V-2 (:101), R3V-3 (:102), R3V-4 (:103) | CORE-BLOCKING. Same entry: "THE D-031 REPAIR BUDGET IS SPENT" (LEDGER:1724) | SOLID |
| R4 | VR4 | Rounds 3+4 patch, exporter 8c0b66b6 (VR4:14-16) | NOT-READY, "the ruling decides" (VR4:27-30, :59) | R4V-1 | 4: R4V-2 (:60), R4V-3 (:61), R4V-4 (:62), R4V-5 (:63). The coordinator's note files 6 as issue #86, adding INFO rows R4V-8 and R4V-9 (VR4:9) | Upheld: "a new loss, so round 4 does not land" (VR4:3; LEDGER:1792) | SOLID |
| R5 | none | RP5, built on the cloud route; "kept as a record and not applied" (RP5:1-11; LEDGER:1810) | no verify | – | – | – | SOLID |
| R5Q | none | Running; no report yet (LEDGER:1812; DLOG:126) | – | – | – | – | SOLID |

### 1b. Each blocker

"Code lines" are in that round's bytes, as the report cites them.

| Id | Round | Mechanism in plain words | Report lines | Code lines | Exposure the report states |
|---|---|---|---|---|---|
| F1 | R0 | The new Cookie, pwd and credentials rules miss a name in these contexts: after a JSON escape letter (a line start or a tab in canonical JSON), after a literal `\n`, after a non-ASCII letter (Cookie), and inside escaped quotes | VR0:492 (detail :159-190) | 95, 103, 105 | "0 uncommitted instances" |
| F7 | R0 | The lenient private-key rule takes quadratic time on a long dash run and on BEGIN heads with no END | VR0:498 (detail :249-284) | 81 | "0 present exposure (longest dash run 278)" |
| F15 | R0 | The credentials rule's ordinary-text cost was reported as none. In the raw view, escapes count as value characters, so ordinary code passes the floor and the redaction eats the next line | VR0:506 (detail :237-247) | the CRED2 rule | over-redaction, "no leak" |
| B1 | R1 | The new pair lookahead in `_VE`, `_CV` and `_CL` re-reads a backslash run at every pair, so time is quadratic | VR1:63-86 | 76-78 | 0; "no run of 32 or more backslashes in 1,352,316,327 bytes" (VR1:76) |
| B2 | R1 | A Cookie value on the line after its head, after an escaped newline, is no longer hidden in canonical or pasted JSON | VR1:88-108 | 143, `_COOKIE_X` | not stated |
| B3 | R1 | The new Negotiate rule's `\s+` crosses a newline and takes the next header's name as its token, so that header's credential shows | VR1:110-129 | 127-128 | "the shape is uncommon"; 22 losses in the random differential (VR1:114, :125) |
| V4 | R1 (by ruling) | A literal two-character backslash escape in decoded text now cuts a pwd or credentials value, or ends a Cookie line | VR1:131-141 | – | 93 of 10,595 fake tokens (VR1:137) |
| N1 | R2 | The pwd and credentials floors count a backslash pair, an odd run or an escape group as ONE unit. An 8-character value with backslash content falls under the floor and shows | VR2:70-115 | `_VF`/`_VU` 86-87; floors 196, 199 | 0 in the main transcript; 13 subagent regions, all probe or test code (VR2:92) |
| N2 | R2 | A head the PIN never read (an escaped-quote key, `my_cookie:`, a head after a literal `\t` or `\r`) runs its value over a later pwd, credentials or Cookie head and frees that head's value | VR2:117-144 | 90-102, 166-199 | 16 subagent regions, all probe texts; 0 in main (VR2:133) |
| R3V-1 | R3 | N2's shape again ("N2R"), but the freed later head belongs to a PAYLOAD rule (the R1 escaped-quote credential, PASS, curl `-u`). The value shows in `convert()` only | VR3:112-176 | new-head branch 213, `_cookie_or_same` 155, `_LATER_*`, the scheme stop | corpus REAL 0 (VR3:169); generated: 923 and 1,001 per 4,000 texts × 6 views (VR3:160-161) |
| R4V-1 | R4 | "K-chain". D1 keeps a refused credentials value whole. A stage-1 or PAYLOAD rule then reads a head inside it, and that rule's token eats a later head's name. The later value, which the PIN hid, shows in `convert()` and at the relay's upstream | VR4:70-209 | `_credentials_or_same` 162, `_CRED_FLOOR` 132 (BR5Q:37) | 498 planted values per 8,000 generated texts; corpus 90 positions, all the word "Negotiate", REAL 0 (VR4:45-46, :111-115) |

---

## 2. The fix tried for each blocker, and whether its kind came back

| Blocker | Next brief asked | Next builder did | Next verify said | Later verify blocker of the same kind | Row |
|---|---|---|---|---|---|
| F1 | BR1 item 1: treat a JSON escape as an escape before the name (as `_KEY_L` does); an escaped newline or tab is not a value character; take escaped quotes (BR1:21-28) | Added classes `_Q`, `_VE`, `_CV`, `_CL`, `_COOKIE`, `_COOKIE_X`. The Cookie, pwd and credentials heads take `_KEY_L` and `_Q`, and the scheme rule takes `_Q` (RP1:144-148, :160-166; D3 at :456-458) | holds (VR1:12; V7 at :163-167) | No later blocker of F1's kind. **Link:** N2's mechanism starts in this fix: "round 1 (F1) gave the Cookie head `_KEY_L` … and `_Q` escaped quotes. pwd and credentials got the same" (VR2:119). RP2 D2 also traces a B3-class leak to round 1's `_Q` in the scheme rule (RP2:782-786) | SOLID |
| F7 | BR1 item 2: a start guard, a bound for BEGIN heads with no END, a timing test; check every rule (BR1:29-32) | A `(?<!-)` start guard; END read by its last three dashes; a head with no END matches to the end and is returned unchanged (RP1:151-156; D13 at :485-487). The Cookie rule was also made linear (D6 at :466-468). Three older quadratic rules were left (D7 at :469-472) | holds (VR1:12; V8 at :169-173) | Yes: B1 in R1, "new super-linear class", AF-AP-152 (VR1:63, :74). After R1, none as a blocker. R4V-4 is a FOLLOW-UP on the PIN's P0/P4 path (VR4:62, :242-253) | SOLID |
| F15 | BR1 item 1 ("F1 and F15, one root") (BR1:21-28) | An escaped `\n`, `\r`, `\t` or `\f` ends a value (RP1:144-148; D5 at :462-465) | holds (VR1:12, :167) | No later blocker named F15. **Links in the reports:** V4 is the loss side of the same change: "a literal backslash-n … now reads as an escape" (VR1:133). RP2 D1: "V4 and F15 conflict on one shape, and F15 wins" (RP2:771-780). VR4 fix option 2: undoing D1 "re-opens F15's over-redaction" (VR4:207) | SOLID |
| B1 | BR2 item 1: drop or atomize the pair lookahead; add backslash rows to the timing test; check every changed rule on backslash runs (BR2:14-19) | Rewrote the classes (`_PAIRS`, `_ODD`, `_ESC`, `_LODD`, `_LESC`, `_VF`, `_VU`, `_LF`, `_CL`) so each reads a run whole and checks one character after it (RP2:94-101). At 32,000 backslashes: 4.38 / 4.71 / 9.49 s became 0.029 / 0.029 / 0.040 s (RP2:183-189) | holds (V-B1 at VR2:171-179) | No later blocker. R4V-4 is a FOLLOW-UP (the PIN's path). **Builders hit the kind in their own candidates:** RP2 D4 (the brief's `_COOKIE_X` form, 1.9 s, x3.9 per doubling; RP2:803-809) and RP3 R3-D3 (candidate 1, x4 per doubling; RP3:58-61, :225-230) | SOLID |
| B2 | BR2 item 2: after the Cookie colon, an escaped `\n`, `\r` or `\t` counts as whitespace; a `_COOKIE_X` stop (BR2:20-22) | `(?:\s\|\\[nrt])*` after the colon; `_COOKIE_X` in a narrower form than the brief's (RP2:103-105, :116-120; D4 at :803-809) | holds (V-B2 at VR2:188-193) | **Same contract item ("no redaction the PIN makes may be lost"):** N1 and N2 (VR2:6), R3V-1 (VR3:20), R4V-1 (VR4:149). **Same escape sub-kind:** N1 (VR2:70-85) | SOLID |
| B3 | BR2 item 3: the Negotiate token never takes a word from the next line (BR2:23-25) | `[ \t]+` after `negotiate`; stops before `_BEARER`, `_LINK` and `_OTHER_HEAD`; `=` only as end padding (RP2:111-114; D5 at :811-814). Also D2: the scheme rule was split, and after an escaped quote its token must stay on its own line (RP2:782-794) | holds (V-B3 at VR2:195-199; V-D2 at :201-203) | **Yes, the AF-AP-157 class:** N2 (VR2:117); R3V-1 ("item 2 (N2), word for word", VR3:20; BR3:22 labels N2 AF-AP-157); R4V-1 ("That rule's token eats the name of a later head", VR4:37; "R3V-1 is the same class", VR4:167). **Note:** B3's rule was new in R1, added for the folded FOLLOW-UP F2 (BR1:34; RP1:157-159; VR1:123) | SOLID |
| V4 (ruled) | BR2 item 4: no PIN redaction lost in any view. Over-redaction may be added: "a literal escape followed by value characters continues the value". F15's named over-redactions stay removed (BR2:26-32) | "An escape stays in a value only when a value unit follows it" (RP2:94-97). The pwd floor `_VU` counts escapes; the credentials floor `_VF` counts none (RP2:126-128). Kept class D1 (RP2:771-780). Names shown, D6 (RP2:816-825). Raw over-redaction is back for pwd and Cookie (D12 at RP2:858-864) | fails: N1, N2 (VR2:289) | **Yes:** N1 and N2, "Both are V4 losses" (VR2:6); R3V-1 maps to V4 (VR3:20, :119); R4V-1 is counted per position under V4 (VR4:106) and under item 2 (VR4:149) | SOLID |
| N1 | BR3 item 1: floors count characters; the credentials floor counts characters before the first escape (BR3:13-19) | `_PWD_FLOOR = (?=[^\s"'&,;]{8})`; `_CRED_FLOOR` = that, plus no escape backslash at offsets 0-7 (RP3:190-198) | closed (VR3:36, :260-262) | No later blocker is a floor defect. **Link:** R4V-1's first step is `_CRED_FLOOR` refusing a value that has an escape in its first 8 characters (VR4:85). That floor is the one N1's fix defined (RP3:193-198) | SOLID |
| N2 | BR3 item 2: a new head never frees a later value the PIN hid. Direction: a stop before a later head that stands apart, or run the Cookie rule after pwd and credentials (BR3:20-24) | Three stops: the Cookie new-head segment stops before `_APART` or `_COOKIE`; the scheme token after an escaped quote stops before `_APART`; pwd and credentials values stop before `_LATER_PWD` / `_LATER_CRED` (RP3:13-16, :200-222). Rejected by measurement: moving the Cookie rule after pwd and credentials (RP3:231-233) | not closed in `convert()` (VR3:84, :263-264) | **Yes:** R3V-1, "N2R" (VR3:13, :20); R4V-1 (VR4:167) | SOLID |
| R3V-1 | BR4 item 1, THE ORDER: every rule that reads a head the PIN never read runs after every PIN-head rule, PAYLOAD included (BR4:13-30). A stop list only as a fallback (BR4:31-33) | `STAGE1_PATTERNS` (the PIN's heads) and `STAGE2_PATTERNS` (new heads). `scrub()` runs stage 1, stage 2, opaque. `scrub_payload()` runs stage 1, PAYLOAD, stage 2, opaque (RP4:122-129). Added the keep branch `_credentials_or_same` (DISC-3 at RP4:61-68). Moved D6's guard and `_LATER_*` out of stage 1 (DISC-1 and DISC-2 at RP4:42-60). Builder's own words: "Is the order enough by itself? No (measured)" (RP4:201-203) | closed (VR4:33, :316-322) | **Yes:** R4V-1, "the class that blocked round 3 (R3V-1)" (VR4:3, :167) | SOLID |
| R4V-1 | BR5 and BR5Q item 2: the verifier's "shield" in a collision-proof form, in `scrub_payload` only (BR5Q:41-75, :81-85) | R5 (cloud route, a record only): a span-tracked shield (RP5:28-34). R5Q: no report | none yet | unknown: no verify after R4 | SOLID |

**Where each fix direction came from (SOLID):**
- R2: VR1's V22 candidate (VR1:237-239) was passed on as "a feasibility copy, not a spec" (BR2:45-46).
- R3: VR2's N2 direction (VR2:142) became BR3's direction (BR3:22-24). VR2's N1 candidate was passed on as "a starting point, not a spec" (BR3:18-19).
- R4: two sources became BR4's order (BR4:13-19). One is VR3's "alternative to measure, not recommend: run the PAYLOAD heads' rules before the new-head values" (VR3:176). The other is the coordinator's proposal "the committed rules run first and the new rules after them … in place of a fourth set of stops" (LEDGER:1724).
- R5: VR4 listed four fix options: the shield, measured; undo D1; reorder, measured worse; a stop list, not measured (VR4:187-209). The shield became BR5 and BR5Q.

---

## 3. Class index

The kinds below use the reports' own words. D1, D2 and D3 are sub-kinds of D, and one blocker can sit in more than one. The kinds are listed in order of first appearance, not ranked.

| Kind (the reports' words) | Blockers | R0 | R1 | R2 | R3 | R4 | Builder found in its own round (not a verify blocker) | Follow-ups of this kind |
|---|---|---|---|---|---|---|---|---|
| A. A context or spelling the rules miss; "Not a regression" (VR0:178-179, :492) | F1 | 1 | 0 | 0 | 0 | 0 | – | F2 (VR0:493); V11 and V12, pre-existing (VR1:190-196) |
| B. Super-linear time, AF-AP-152's class (VR0:498; VR1:63, :74) | F7, B1 | 1 | 1 | 0 | 0 | 0 | RP1 found the Cookie rule in the class (RP1:122; D6 at :466-468); RP2 D4 (:803-809); RP3 R3-D3 (:58-61) | R4V-4 (VR4:62) |
| C. A rule's ordinary-text cost misstated (VR0:506; the rule is BR0:29-30) | F15 | 1 | 0 | 0 | 0 | 0 | – | – |
| D. A redaction the PIN makes is lost. This is the frozen no-loss item in every brief (BR0:48; BR1:39-40; BR2:26-27; BR3:1; BR4:36-40) | B2, B3, V4, N1, N2, R3V-1, R4V-1 | 0 | 3 (2 from the verifier, V4 by ruling) | 2 | 1 | 1 | RP2 D2 (:782-794); RP3 R3-D2 (:50-56); RP4 DISC-3 and DISC-4 (:61-79) | R3V-2 "needs a ruling" (VR3:185) |
| D1. A head's value or token runs over the next head's name and frees its value; "AF-AP-157" (VR1:116; VR2:117; BR3:22) | B3, N2, R3V-1, R4V-1 | 0 | 1 | 1 | 1 | 1 | the same three | V11 (VR1:192) |
| D2. "A head the PIN never read" (VR2:8; VR3:15; VR4:36, :150) | N2, R3V-1, R4V-1 | 0 | 0 | 1 | 1 | 1 | RP2 D2: "The PIN's `[\"']?` never did" (RP2:785) | – |
| D3. Escape or backslash content moves where a value ends, or changes the floor's count (VR1:90, :133; VR2:72-77) | B2, V4, N1 | 0 | 2 | 1 | 0 | 0 | – | R4V-1's first step is a value refused for an escape (VR4:85); it is not counted here |
| E. A clause no test pins; surviving mutants (VR0:503; VR1:143; VR2:146; VR3:193; VR4:211) | none | 0 | 0 | 0 | 0 | 0 | – | F10 and F12 (R0), V5 (R1), F-MUT (R2), R3V-3 (R3), R4V-2 (R4) |
| F. Comments state what the code does not do (VR1:231-235; VR2:164; VR3:203) | none | 0 | 0 | 0 | 0 | 0 | – | V21 INFO (R1), F-DOC (R2), R3V-4 (R3) |
| G. Constant-factor slowdown (VR2:181-186; VR4:255-267) | none | – | – | – | – | – | – | V-D7 INFO (R2), R4V-5 (R4) |

**Why the builder's own evidence missed each blocker, in the verifier's words (SOLID):**

| Blocker | The verifier's words |
|---|---|
| B1 | "its 'pwd backslashes' family starts the value with a backslash … there was no Cookie backslash family (tactic 3f)" (VR1:80) |
| B2 | "the builder's differential draws no backslash" (VR1:104) |
| V4 | "The builder's self-attack 1 names only the short-head case" (VR1:137) |
| N1 | the instruments "always put a 12- to 32-character fake after the escape, so the unit count always clears 8" (VR2:91) |
| N1, N2 | "those instruments cannot draw short values or newly read heads" (VR2:317) |
| R3V-1 | the builder's N2 probes put only pwd, credentials or Cookie heads after the new head; "rand_v4b and rl2 generate no PAYLOAD heads"; the corpus scan ran `scrub` only (VR3:84-87; R3V-9 at :239-241) |
| R4V-1 | "DISC-4's size comes from the corpus only; contract item 1 said 'Measure it; do not assume it'" (VR4:64, :269-278) |

**Blockers first reported one round after the code that already had them (SOLID):**
- R3V-1's red file gives "round 2 `11 failed`" (VR3:124), and its differential loses 1,024 and 1,130 on round 2 (VR3:162).
- R4V-1: "Round 3 had the same chain" (VR4:116); round 3 fails 10 of the 12 red items (VR4:160); the round-3 verifier's own words: "my round-3 report did not name it" (VR4:311).
- VR2's 16-item red file on round 1 gives "11 failed, 5 passed" (VR2:61). Which items fail is not stated.

---

## 4. Blocker count per round, and repairs that created blockers

| Round | From the verifier | As ruled | Change against the round before (as ruled) | Follow-ups |
|---|---|---|---|---|
| R0 | 3 (VR0:11) | 3 (LEDGER:1644) | – | 3 |
| R1 | 3 (VR1:5) | 4, V4 added (LEDGER:1670) | +1 | 4 as labeled, 3 after the ruling |
| R2 | 2 (VR2:6) | 2 (LEDGER:1697) | −2 | 2 |
| R3 | 1 (VR3:13) | 1 (LEDGER:1724) | −1 | 3 |
| R4 | 1 (VR4:27) | 1 (VR4:3) | 0 | 4 |

**Did a repair create a blocker in code it changed?** Only where a report says so:

- **Round 1's repair.**
  - B1: "Ownership: the three classes are this round's code" (VR1:78).
  - B2: "Ownership: the Cookie head and `_COOKIE_X`" (VR1:102); "V2 is a loss from the same rewrite" (VR1:251).
  - B3: "Ownership: the new rule, added for F2" (VR1:123).
  - V4 comes from round 1's escape reading (VR1:133).
- **Round 2's repair.**
  - N1: "Ownership: the classes and floors are this round's code" (VR2:99); "Round 1 counted per pair and hid these, so here round 2 regressed from round 1" (VR2:85).
  - N2: "Ownership: the heads and values are this round's code (lines 90-102 and 166-199)" (VR2:140). Its mechanism begins in round 1's F1 change (VR2:119).
- **Round 3's repair.**
  - R3V-1 was present in round 2 too (VR3:124, :162). Round 3's own segment marker takes part: "The segment's marker removes the name of a later R1, PASS or curl head" (VR3:88); mechanism point 1 sits on round 3's new-head branch (VR3:146).
  - FOLLOW-UP R3V-2: "This is new in round 3; round 2 had no TOKEN class" (VR3:183).
- **Round 4's repair.**
  - R4V-1 was present in round 3 (VR4:116, :160). Its step 2 is round 4's keep branch `_credentials_or_same` (VR4:86; RP4:61-68).
  - FOLLOW-UPs caused by the order: R4V-3, "Round-3 gains given back, each equal to the PIN" (VR4:61); R4V-4, "round 3's side-effect linear time on those families is gone" (VR4:62).

**Budget and authorization, as the sources state them (SOLID):**
- D-031 allows one focused repair, a second only with coordinator authorization, and no automatic third wave (DLOG:42).
- R1 was registered after VR0 (LEDGER:1644). R2 followed VR1: "NOT-READY, SO SCRUB2-R1 GOES TO ROUND 2" (LEDGER:1670).
- R3: "This round is the one focused repair, keyed by round 2's new production code" (BR3:7-8).
- After R3: "rounds 2 and 3 were the two repairs, so a fourth round is the owner's call" (LEDGER:1724).
- R4: D-108 item 3, "Do one more round for Scrubber", past D-031's budget (DLOG:119; BR4:4-5).
- R5: D-112, "past D-108 item 3's one more round" (DLOG:123). R5Q: D-114 (DLOG:125).
- D-115: "a NOT-READY verify then triggers the review, never a sixth repair" (DLOG:126).

---

## 5. The design each brief described

**What each brief asked for (quotes with file:line):**

- **BR0 (SCRUB2).**
  - Right anchor: "For example an ASCII-only right anchor such as `(?![A-Za-z0-9])`; choose by measurement" (BR0:23-24).
  - Escape context: "SCRUB1 measured one candidate, `(?:(?<![A-Za-z0-9])|(?<=\\[nrt]))`; extend it to `\uXXXX`" (BR0:27).
  - Shape gaps: "`passphrase`, `pwd` and `credentials` as credential-assignment names; a `Cookie:` session value; `Authorization: Token <v>`; a PEM block whose header lines are malformed … a shape that costs ordinary-text redactions goes in only with its count and your reason" (BR0:28-30).
  - Value gate: a non-regular source "refuses at once"; "a source kind outside the known three is an error" (BR0:39-41).
  - "Old-to-new: no redaction the PIN makes may be lost" (BR0:48).
  - **Landed:** `_KEY_L`/`_KEY_R`; "four rules after the Bearer rule (Cookie, Authorization after a known scheme, `pwd` and `credentials` with a value that is not a path); a lenient private-key rule (3+ dashes, END line required) right after the PIN's own" (RP0:124-130). pwd and credentials became their own rules, not names; a known-scheme list replaced `Token` alone (D4 at RP0:374-377).
- **BR1.**
  - Escapes: "They treat a JSON escape as an escape before the name, as `_KEY_L` does … Inside the value, an escaped newline or tab is not a value character. They take an escaped quote as the payload rules do, and never the backslash of a closing `\"`" (BR1:22-24).
  - F7: "a start guard, and a bound for BEGIN heads with no END" (BR1:29-30).
  - No-loss item: "No redaction the PIN makes may be lost, except the over-redactions F15 names" (BR1:39-40).
  - The PIN's rules are quoted at BR1:88-124: the credential rule with `_NAME` and an 8-character lookahead floor (:102-106); the Cookie rule (:113); the known-scheme list (:116-117); pwd and credentials with a not-a-path guard `(?![/~.$\\])` (:118-124).
- **BR2.**
  - B1: "Drop it or make it atomic in all three classes … The class is a lookahead or an alternation that re-scans a run inside a quantified group" (BR2:14-18).
  - B2: "After the Cookie head's colon, an escaped `\n`, `\r` or `\t` counts as whitespace" (BR2:20-21).
  - B3: "`[ \t]+` after `negotiate`, or a stop at a header name" (BR2:23-24).
  - V4: "You may add over-redaction … a literal escape followed by value characters continues the value … F15's named over-redactions stay removed" (BR2:29-32).
- **BR3.**
  - N1: "The pwd and credentials floors count characters where the PIN counted characters" (BR3:13); "the credentials floor counts the value's characters before its first escape" (BR3:16-18).
  - N2: "give such a head's value a stop before a later head that stands apart … running the Cookie rule after pwd and credentials is another option" (BR3:22-24).
- **BR4.**
  - "A stop list must name every later head, and three rounds show that list drifting. An ORDER needs no list" (BR4:15-19).
  - "every rule or branch that reads a head the PIN never read runs AFTER every rule that reads a head the PIN reads, the PAYLOAD rules included" (BR4:23-25).
  - "Round 3's changes to heads the PIN reads (the N1 floors, F15's value extent, D1 and D6 as ruled) stay where the PIN's rules run" (BR4:28-29).
  - "Is the order enough by itself? Measure it; do not assume it" (BR4:34).
- **BR5 and BR5Q.**
  - The shield: "a kept value is a stand-in of the marker's length … Then the kept value comes back and those rules run again" (BR5Q:71-73).
  - Its known flaw: "the stand-in is private-use characters, and a text that already holds them can collide with it" (BR5Q:75).
  - The pass order in code: stage 1 with the shield, PAYLOAD, restore, then the late stage-1 rules, PAYLOAD and stage 2 (BR5Q:54-67).

**What stayed the same in every round (SOLID):**
- **The reference:** the PIN is SCRUB2's exporter 6ad316dc (BR1:4; BR4:121; BR5Q:144).
- **The no-loss-against-the-PIN item:** in every brief (see D in §3).
- **The value gate is untouched.**
  - `known_values_check.py` keeps hash cfdf2ffec10e6d10 (RP1:423; RP2:171; RP3:135), and RP4 reports the value gate byte-identical to the PIN's (RP4:138-140).
  - "Never edit … the value gate's lines" (BR3:50; BR4:77).
- **The PAYLOAD rules** are byte-identical to the PIN's (RP4:129; VR4:244).
- **The Laya lock item** is in every brief (BR0:50-54; BR1:43; BR2:39-40; BR4:52-54).
- **No view flag:** "`scrub()` and `scrub_payload()` each run on both views, so no view flag exists inside the boundary". A caller-supplied view flag "is outside this boundary" (RP2:775, :778; also :583-586).
- **Allow-style guards present from R0/R1 onward:**
  - the known-scheme list (BR1:116-117);
  - the not-a-path start guard (BR1:118-121);
  - `--skip TYPESAFE_BASE_URL` in the gate call (RP0:246);
  - `session_export`'s gate exemptions, keyed on the name `opaque-run` (VR0:338-341).
  - D6's `_APART` start guard was added in R2 (RP2:816-818).

**What changed, measured (SOLID):**

| Measure | PIN | R1 | R2 | R3 | R4 |
|---|---|---|---|---|---|
| Diff size | exporter 383 lines (RP0:339) | exporter 434 lines; 5 files +401/−18 (RP1:501, :505) | exporter +74/−32 against R1 (RP2:91) | exporter +72/−27 against R2; rounds 1-3: 5 files +805/−19 (RP3:121, :136) | rounds 3+4 against the PIN: 5 files +1,040/−29 (RP4:16) |
| `PATTERN_NAMES` | 23 (VR0:322) | 24 (RP1:168) | 24 | 24 | 28 (RP4:100) |
| Floor test count | 824 (BR1:154) | 841 (RP1:11) | 855 (RP2:33) | 877 (RP3:142) | 893 + 1 xfailed (RP4:287) |
| Mutants on the final bytes | R0: 52 (RP0:172-173) | 19 + 28 + 8 (RP1:15-16) | 5 groups (RP2:42-47) | 81 (RP3:159) | 106 (RP4:315) |
| `scrub` / `scrub_payload` against the PIN | – | – | 1.13x / 1.11x (VR2:184-185) | – | 1.71x / 1.22x (VR4:265) |

Later cost figures: the shield prototype is x1.62 on `scrub_payload` against R4 (VR4:203); RP5 claims 1.518x (RP5:62).

---

## 6. What the round 5Q brief asks for (BR5Q)

1. **Premise:** re-run the block, then check that the dispatched tree has the 6 lane-patch files (BR5Q:79-80, :24-29).
2. **The shield**, collision-proof, in `scrub_payload` only: no input may misplace, drop or leave a stand-in. Write why it cannot collide. `scrub()` does not change (BR5Q:81-85).
3. **The red items:** the verifier's 12 R4V-1 items move into `tests/test_transcript_export.py` unchanged and pass. The strict xfail at :2052 loses its marker and passes. The R3 (11) and R2 (16) red items stay green (BR5Q:86-90).
4. **A collision test:** an input that holds the prototype's stand-in text beside a refused value and a later head. It must fail on the prototype and pass on the new form (BR5Q:91-96).
5. **R4V-2:** an order test that fails under mutant A7, plus the same text asserted hidden in the decoded view (BR5Q:97-105).
6. **Measure:** `scrub()` byte-identical on 21 of 21 digests; `scrub()` and `scrub_payload()` timed best of 3, before and after; the manifest's one sha256 line updated, with its tests run (BR5Q:106-111).
7. **Gates:** the 12 named test files, run twice with `-n 8`, each call under 420 s. A red test the lane did not cause is proved red at the PIN (BR5Q:112-119).
8. **Run limits (THIS RUN):** raw Qwen id only; keep the context small; append each section to `$LANE_REPORT_DRAFT` (BR5Q:3-4, :14-22).
9. **Boundary:** the exporter, its test file and the manifest line (BR5Q:121-125). **Report:** the final message is the report (BR5Q:127-131).

---

## 7. Contradictions (both sides recorded) and gaps

**Contradictions:**

- **C1, budget count (UNSURE).** LEDGER:1724 says "rounds 2 and 3 were the two repairs". BR3:7-8 says round 3 is "the one focused repair, keyed by round 2's new production code". The files I read do not say how round 1 counts under D-031 (DLOG:42).
- **C2, V4's class.** VR1 files V4 as a FOLLOW-UP (VR1:131, :139-141). The coordinator ruled it BLOCKING (LEDGER:1670).
- **C3, blocking rested on readings in all five rounds, each ruled by the coordinator:**
  - R0: VR0:513-515, ruled at LEDGER:1644;
  - R2: VR2:12 ("If you judge them edge cases under D-034 … MERGE-READY-WITH-FOLLOWUPS"), ruled at LEDGER:1697;
  - R3: VR3:47, ruled at LEDGER:1724;
  - R4: VR4:28-30, ruled at VR4:3;
  - R1: V4, see C2.
- **C4, what D2 used.** BR3:22-23 says "as D2 did for the scheme rule with `_OTHER_HEAD`". RP3 R3-D7 says D2 used `[ \t]+`, and `_OTHER_HEAD` is the Negotiate stop (RP3:91-93).
- **C5, where round 3's changes to PIN heads run.** BR4:28-29 says they "stay where the PIN's rules run". RP4 DISC-1 and DISC-2 moved D6's guard and `_LATER_*` out of stage 1 (RP4:42-60).
- **C6, the "D1's K class" exemption.** BR4 item 2 exempts "D1's K class" (BR4:39-40). The coordinator: that was shorthand from VR3's class K, "counterfactual and too broad" (VR4:3; R4V-10 at VR4:308-312).
- **C7, the builders' closure claims, each falsified by the next verifier:**
  - RP1 "every secret rule linear, no flag" (RP1:114-115) against VR1:74;
  - RP2 "V4 is closed except the kept classes" (RP2:63) against VR2:317;
  - RP3 "N2 is closed" (RP3:13) against VR3:84;
  - RP4 sized DISC-4 "on the corpus only" (RP4:69-79) against VR4:64.
- **C8, the round-1 folds.** LEDGER:1644 lists folds "F2, F5, F10, F12". BR1:33-36 lists F2, F10 and F12, with F5 inside item 1 (BR1:24).
- **C9, what is open at the PIN.** LEDGER:1792 names F1 and F15 as open there. F7's measured bytes are the same committed file (see "What the PIN means" at the top).

**Gaps, marked unknown:**

- **G1.** B2's corpus exposure: not stated in VR1.
- **G2.** Which 11 of VR2's 16 red items fail on round 1: not stated (VR2:61).
- **G3.** VR1 V20 is UNVERIFIED: the measurement rows and the 19-of-19 digest identity. The harness's classifier refused the verifier's second transcript read (VR1:227-229).
- **G4.** The round-5 cloud report's claims are unverified (RP5:1-13). Round 5Q has no report.
- **G5.** The shield prototype was not measured on sch3, r3d4, pos4 or the census (VR4:206, :442).
- **G6.** R3V-2 needed a ruling (VR3:185). R4 then measured it at 0 (RP4:239-242; VR4:374). I found no ruling on it in the files read.

I made no writes, no git writes, no bridge use and no outward action, and I read no secret file or transcript. The one S1 injection (s1-ea83f800) was rated in its own line: rel=1 use=0.