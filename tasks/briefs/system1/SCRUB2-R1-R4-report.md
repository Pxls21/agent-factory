# SCRUB2-R1 round 4 report (task #321)

> **Coordinator note (2026-09-29 15:4xZ):** extracted by `scripts/stack.py harvest` (run s-20260929T154009Z-74cfbb; hand-back sha256 prefix 156861497c37, 31,715 characters). Served model: claude-opus-5-5 on all 2,215 assistant records, 0 refusal stops, 6 compactions. `report_lint`: 1 MISS and 1 UNCHECKABLE, at `tests/test_transcript_export.py:2027` and `:2030`, lines of the PATCHED file (the shared tree holds the PIN's file until the patch lands). Local ids: `ace09da` is origin 5f1bd90 (the shared tree's HEAD while the lane ran; the push rewrote it); `eb256f49c0` is a pre-rewrite id that the Laya lock probe's own pins carry, not a commit the lane made. The patch: `tasks/briefs/system1/SCRUB2-R1-R4.patch`, sha256 f18f85c9b0abaf7b43c06ed4726671c781b9b44390268210e4de7d23aa4b8020, 1,172 lines, 5 files; it applies at the shared HEAD of this note's time (the commit "anti-hollow-green: a key's public prefix is a window hit ..."); NOT applied.

**Round 4 is ready for verify, with four findings. The order closes R3V-1, but it was not enough by itself:**
- **One residual needs a ruling:** the cross-rule K-chain, held by a strict xfail test.
- **Three frozen items no longer hold as the verifier stated them.** The losses against the PIN are 0 in each (only D6's guard moved; the other two now match the PIN):
  - B1: two census families are quadratic, as on the PIN;
  - D2: the Negotiate-next column now equals the PIN;
  - D6: its start guard left stage 1.
- **Measured on the final bytes:** 0 lost value characters against the PIN in every item-2 and item-4 probe, in all 6 views. The verifier's 11 red items fail on round 3 and pass on round 4.

- **Stamp:** 2026-09-29 15:34:07Z (`date -u`).
- **Builder:** sandbox code-implementer, Opus 5.5.
- **PIN:** bef1e9e.
- **Deliverable:** `/home/user/agent-factory/tasks/briefs/system1/SCRUB2-R1-R4.patch` (sha256 prefix f18f85c9b0abaf7b, 1,172 lines). It is `git diff` of the five brief files against the PIN, rounds 3 and 4 together: 5 files, 1,040 insertions, 29 deletions. It applies at the PIN and at the shared tree's HEAD ace09da.
- **Final bytes (sha256 prefixes):**

| file | sha256 prefix |
|---|---|
| `scripts/transcript_export.py` | 8c0b66b6fa41f8c8 |
| `scripts/session_export.py` | 7f677858457724f6 |
| `tests/test_transcript_export.py` | 4dabcc4f1bd3a69b |
| `tests/test_session_export.py` | def83555e7297dc1 |
| `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json` | b94a836b8c896f9c |

---

## 1. NOT-done

1. **The cross-rule K-chain residual is not fixed. It needs a ruling** (DISC-4).
2. **B1 fails for 2 of 97 census families in `scrub_payload`.** The cause is two PAYLOAD rules that are unchanged from the PIN. I did not fix it (DISC-5).
3. **Start-of-round premise output was lost.** I ran `bash scripts/premise_block.sh` from the main tree at the start. There was no difference, so no CONTRACT-INVALID. The verbatim output did not survive two context compactions. At 15:09Z I re-ran the premise's five read-only lines (pasted in §4). I did not re-run its pytest lines at the end.
4. **The verifier's `_KEY_L` candidate for R3V-2 was not tried.** The R3V-2 residual now measures 0 (§6, item 4).
5. **`tests/test_laya_ft.py` did not run to completion.** It is a consumer test outside the brief's gates, and it did not finish in 280 s in the sandbox. The Laya lock probe covers the dataset identity (§6, item 7).
6. **The red-green run of the 11 red items as copied into `test_transcript_export.py` (`-k n2r`) used pytest's own last line, not `test_summary.sh`.** The verifier's red file itself ran through `test_summary.sh` with set ids (§5).
7. **`v13chk.py` (the verifier's V13 probe) was not re-run.** It loads the verifier's `mutdiff.py` and `mut3v.py` from fixed paths that do not exist in my copy. V13 is not a frozen item.
8. **Two sandbox reboots killed commands.** They happened at 14:09:29Z and at about 14:20:10Z. They killed floor pass 1 (started 14:08:02Z; void, not red) and a read-only scratch listing. I re-ran the floor twice afterwards (§7).

## 2. DISCREPANCIES and DEVIATIONS

- **DISC-1. DEVIATION from contract item 1: D6's start guard is out of stage 1.** Item 1 says "D1 and D6 as ruled stay where the PIN's rules run". The guard now runs in stage 2 only.
  - **Why (verified):** with the guard in stage 1, stage 1's credentials rule reads a head that sits inside a pwd value the PIN took. The PIN never read that head.
  - **Shape** `pwd="credentials": cookie:credentials =  <v>` (fake v, views dig/txt/call/call2/pdig/ptxt; S = the value shows):
    - PIN `......`
    - final `......`
    - G1 (the guard back in stage-1 pwd) `SS....`
    - G2 (the guard back in stage-1 credentials) `......`
    - G1+G2 `SS....`
    - Tool: `g_shape.txt`.
  - **Generators with G1+G2:** REAL 0 in the chain soup (3 seeds) and in rl2; rand_n2c 0. The loss is in this constructed shape only. D6's shown names grow: rl2 decoded NAME goes from 571 to 28,398 positions.
  - **Mutants:** G1 and G2 are KILLED.
  - **Effect:** for PIN heads, a pwd or credentials value starts where the PIN's did. d6chk has 0 LOST rows.
- **DISC-2. DEVIATION: `_LATER_PWD` and `_LATER_CRED` are out of stage 1.** They stay in stage 2.
  - **Why (verified):** mutants L1 and L2 put the stops back in stage 1, and both are KILLED. A value the PIN hid shows.
  - **Effect:** round 3's gains on PIN heads are given up, back to the PIN's behaviour. Example: `pwd=abcd_pwd: <v>` shows v, as the PIN does; round 3 hid it.
  - **Round-3 test rewritten:** `test_r3_a_value_stops_only_before_a_head_that_a_later_rule_reads`.
    - Its PIN-head assertions moved to stage-2 heads (a literal `\t` prefix).
    - Six PIN-head texts now assert equality with SCRUB2's rule forms (`_scrub_with_scrub2s_forms`). One of them is DISC-1's shape.
    - It gained the X9 and X12 assertions.
- **DISC-3. A new branch beyond the order: `_credentials_or_same` (verified).**
  - **What it does:** stage 1's credentials rule has a keep-as-is branch. When the credentials floor refuses a value and the PIN's floor takes it (D1, and F15's shapes in raw JSON), the rule matches the value whole and keeps it. A credentials head inside the value then waits for stage 2.
  - **Why:** without it, the same rule read that inner head in stage 1, and the head's value ran over a later head whose value the PIN hid.
  - **Chain-soup K-chain positions before and after:**
    - seed 2: 11 to 0 (call and ptxt);
    - seed 3: 27 to 0 (txt);
    - seed 1: 9 before and after (see DISC-4).
  - **Pinned by** 3 red-then-green cases in `test_r4_a_credentials_head_inside_a_refused_value_waits_for_stage_2`. Mutant N0 is KILLED.
- **DISC-4. RESIDUAL that needs a ruling: the cross-rule K-chain.**
  - **Mechanism:** a refused credentials value (D1 or F15) now shows. A head inside it that another stage-1 or PAYLOAD rule reads is one the PIN never read. That rule's value can run over a later head whose value the PIN hid.
  - **Constructed example** (verified on the final bytes rebuilt from the patch). In canonical JSON (a tool_call), the text is ``credentials=x<TAB>abcdefgh\tAuthorization: \"Basic <c>token=\"<v>\"``, where `\t` is a literal backslash-t.
    - The Basic PAYLOAD rule's token takes the glued `token=`, so R1 finds no head and v shows.
    - The PIN hides v.
    - The decoded view is equal to the PIN.
  - **Size:**
    - chain soup, 9,000 texts × 6 views: 9 characters in each of call and ptxt, seed 1 only; they are the word `Negotiate`, and no planted value is among them;
    - corpus: KCHAIN 0 in both modes.
  - **Classification (inferred):** the verifier's classifier puts these positions in K, the class hidden when the credentials floor counts escapes (D1's class). D1's ruling text may not name chains.
  - **Held by** the strict xfail `test_r4_a_head_inside_a_refused_credentials_value_frees_no_later_value` (`tests/test_transcript_export.py`, line 2053). It turns red (XPASS strict) when someone fixes it.
- **DISC-5. Frozen item B1 fails for 2 of 97 families, in the payload target only.**
  - **The two families:**
    - `r3 sch esc names`: 0.1363 / 0.649 / 2.4007 / 8.2887 s at 8k / 16k / 32k / 64k;
    - `r3 sch esc sq`: 0.039 / 0.0998 / 0.2537 / 0.8196 s.
  - **Cause (verified):** PAYLOAD rules #13 (the trycloudflare bridge host) and #17 (the userinfo URL) are unchanged from the PIN, and they are quadratic on long dotted runs.
  - **Equal to the PIN:** at 32k, the PIN takes 2.239 s and round 4 2.134 s; #13 alone takes 1.908 s and 1.735 s. A headless dotted run is quadratic in the PIN, round 3 and round 4 (2.027 / 1.969 / 1.891 s at 32k).
  - **Why round 3 was linear here:** only because its escaped-quote scheme rule ran before the PAYLOAD rules and turned the run into a marker. The order forbids that.
  - **Fix?** A stop cannot fix a rule's own cost. The other 24 re-timed rows are linear to 512k.
- **DISC-6. Frozen item "D2's fix" (the verifier's words: round 3 equals round 2 in every cell, and every cell ≤ the PIN's).**
  - **Changed:** the first half fails in the Negotiate-next column. Round 4 shows the second value in 208 view-texts where round 3 hid it; the PIN shows all 208 (d2_lost: "LOST (round 4 shows, PIN hid): 0").
  - **Still holds:** every cell ≤ the PIN's.
  - **Cause:** the Negotiate token rule is a stage-2 rule. Mutant O1 (that rule moved first) frees a PAYLOAD value. Stage 1's scheme rule is the PIN's, and its `\s+` takes the next line's `Authorization` as the token, as on the PIN.
- **DISC-7. R3-D2's plain-head promise no longer holds in 3 texts.** This is a verifier-found holding item, not on the brief's frozen list.
  - **Count:** 3 of 3,000 sch3 texts differ from round 2 in `scrub()`.
  - **Each is equal to the PIN** on the planted value. In one of them round 4 also hides the Negotiate token, which the PIN shows. Tool: `sch3_diff`.
- **DISC-8. Contract item 5: I adapted the verifier's two examples.**
  - **V12:** the text is the verifier's, but I assert it in `scrub()` (the digest), not `settle()`. In `scrub_payload` the PAYLOAD Basic rule now runs before stage 2 and ends the token at `.`, so `settle()` no longer tells V12 apart.
  - **V14:** the example starts with a stage-2 head (``x\tpwd=q1w2e3r4\tPWD: <v>``). The verifier's own text ``pwd=<v1>\tPWD: <v2>`` starts at a PIN head. That head is now stage 1's, with the PIN's value extent, so v2 shows, as on the PIN (round 3 hid it).
  - **Result:** both mutants are KILLED by the named test alone (§8).
- **DISC-9. `session_export`'s pattern gate changed.**
  - **Names:** PATTERN_NAMES goes from 24 names (round 3) to 28 (the PIN had 23). `authorization-negotiate` moves from position 3 to position 14. New names: `stage2-cookie`, `stage2-authorization-scheme`, `stage2-pwd`, `stage2-credentials`.
  - **Count:** stage 2 reads the PIN's heads again, so one lower-case bearer header counts under two names. The fixture's gate total goes from 11 to 12 (`test_gate_counts_patterns_and_canaries_and_prints_none`).
  - **Other readers:** a literal sweep finds none outside the two session_export files.
- **DISC-10. Stage 2 reads the PIN's heads again, which is redundant for them.** In `scrub()`, a single-stage mutant can be masked by the other stage. I pinned each stage alone with `_one_stage` (mutants W1b, W3, W3b, Y33 and others are KILLED).
- **DISC-11. X13 is an equivalent mutant.** The stage-2 Negotiate rule's `_BEARER` and `_LINK` stops never fire, because stage 1 has already turned those shapes into markers.
  - **Measured on the final bytes:** 0 of 20,000 texts × 6 views differ with either stop removed, or both (15:34Z).
  - **Kept:** the comment's claim stays literally true. A follow-up could remove the two stops.
- **DISC-12. D7: the constant factor is higher.** Best of 3 over the 21 committed digests (4,086,435 characters), with other lanes loading the box:

| version | scrub | scrub_payload |
|---|---|---|
| PIN | 2.829 s | 5.531 s |
| round 3 | 3.911 s | 6.477 s |
| round 4 | 4.635 s | 6.993 s |

  Round 4 against round 3 is +18.5% for `scrub` and +8.0% for `scrub_payload`.
- **DISC-13. Test changes to rounds 2 and 3, beyond DISC-2.**
  - Four round-3 tests gained assertions, and none lost one: the Cookie differential, the 8/7 floor test (per stage, plus the escaped-quote Token case and Y33), the new-head segment floor (Y30), and the R3V-3 pins.
  - The `_payload_with` helper, which models SCRUB2's order, now runs stage 1, then PAYLOAD, then opaque, with no stage 2.
  - `_gate_probes` in `test_session_export.py` gained 4 stage-2 probes.
- **DISC-14. INFO (unchanged):** the stage-2 Cookie comment quotes round 3's census, "at most 0.06 s". My single census pass read 0.0714 s. The re-timed minimum at 64k is 0.0570 s. This is R3V-10's noise, and I left the comment as it is.

## 3. The change (files:lines, final `scripts/transcript_export.py`)

- **Two stages, named in the code.**
  - `STAGE1_PATTERNS` (line 186) holds the PIN's rules for the heads it reads, in its order. 9 of its 13 rules are byte-identical to PIN rules. The other 4 carry only ruled changes: the lenient key block (F7), the Cookie rule (`_COOKIE_PIN` heads, N1 floor, F5, linear), pwd (the N1 floor and `_VU` extent), and credentials (`_CRED_FLOOR` for D1 and F15, plus DISC-3's branch).
  - `STAGE2_PATTERNS` (line 274) holds round 3's rules for heads the PIN never read: the Negotiate token, then the Cookie, scheme, pwd and credentials rules.
  - `SECRET_PATTERNS` = stage 1 + stage 2 + opaque (line 311).
  - `scrub()` (line 319) runs stage 1, stage 2, then opaque.
  - `scrub_payload()` (line 372) runs stage 1, then `PAYLOAD_PATTERNS` (byte-identical to the PIN's), then stage 2, then opaque.
- **The stage block comment (lines 171-185)** states the invariant and names its exception, DISC-4.
- **`_credentials_or_same`** is at lines 162-167. The stage-1 pwd and credentials comment (lines 238-251) records DISC-1 and DISC-3.
- **R3V-4 (contract item 6).** The three comments now state the invariant the code keeps:
  1. `_LATER_PWD` and `_LATER_CRED` (lines 105-111): "These stops guard only the heads stage 2 reads: a head that a stage-1 or PAYLOAD rule reads (R1, PASS and curl's among them) has its value hidden before stage 2 runs, so a stage-2 value that runs over that head runs over a marker".
  2. `_COOKIE_PIN` (lines 115-122): "stage 2's Cookie rule reads it after every stage-1 and PAYLOAD rule, so each value those rules hide is a marker by then".
  3. The pwd and credentials rule comment is now the stage-2 block comment (lines 271-273): "the stops … keep a later head that a stage-2 rule still reads. A head a stage-1 or PAYLOAD rule reads needs no stop here: its value is a marker".
  - The stage-2 Negotiate comment (lines 275-285) names which heads stage 2 reads.
- **`scripts/session_export.py`:** only PATTERN_NAMES changed. All 47 defs are byte-identical to the PIN's.
- **The value gate is byte-identical to the PIN's.**
  - `scripts/known_values_check.py` is not in the patch.
  - In `transcript_export.py`, 10 of the 12 top-level defs the PIN has are byte-identical: `turns`, `known_values`, `value_hits`, `export`, `main`, `KnownValueRefusal` and the others. Changed: `scrub` and `scrub_payload`. New: three replacement callables. At module level, only `SECRET_PATTERNS` changed, plus new constants.
- **Tests** (`tests/test_transcript_export.py`):
  - the 11 red items: lines 1940-1981 (their bodies and parametrize lists are AST-identical to the verifier's file);
  - the order test: lines 2009-2019;
  - the R3V-3 test: lines 2022-2030 (V12 at 2027, V14 at 2030);
  - the refused-value test: lines 2042-2046;
  - the strict xfail: line 2053.
- **Manifest:** one line differs from the PIN: `"scripts/transcript_export.py": "8c0b66b6fa41f8c8c18e432023ecebc1177748560d104b4f3d05bec4dafabfd2"`, the full sha256 of the final file.
- **Pyflakes:** 0 lines on all four Python files, both at the PIN and in round 4.

## 4. Premise

At the start I ran `premise_block.sh` from the main tree. There was no difference (the output did not survive, see NOT-done 3). The end re-run of the read-only lines, 15:09Z, from the main tree:
```
$ git merge-base --is-ancestor bef1e9e HEAD && echo bef1e9e-is-an-ancestor-of-HEAD
bef1e9e-is-an-ancestor-of-HEAD
$ git status --porcelain -- <the five files> | wc -l
0
$ sha256sum <the five files> | cut -c1-16,65-
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
```
The shared tree's five files are still the PIN's. I never edited them.

## 5. Red first (in my worktree, through `masked.sh absent`, `--basetemp` outside every work tree)

```
W scrubber now: f6fe76b2b67d316a (round 3)
== round 3 code, tests/test_vscrub2r1r3_red.py (1 files set=8d2adae291be)
pytest-exit: 1
pytest-summary: 11 failed in 0.11s
== round 3 code, tests/test_vscrub2r1r2_red.py (1 files set=bcd44bc128b4)
pytest-exit: 0
pytest-summary: 16 passed in 0.07s
W scrubber now: 8c0b66b6fa41f8c8 (round 4, final)
== round 4 code, tests/test_vscrub2r1r3_red.py (1 files set=8d2adae291be)
pytest-exit: 0
pytest-summary: 11 passed in 0.10s
== round 4 code, tests/test_vscrub2r1r2_red.py (1 files set=bcd44bc128b4)
pytest-exit: 0
pytest-summary: 16 passed in 0.07s
```
- **The integrated copies** (`-k n2r` on `test_transcript_export.py`; pytest's own line): round 3 gives `11 failed, 253 deselected in 1.08s`; round 4 gives `11 passed, 253 deselected in 0.46s`.
- **Helpers:** `_settle` and `_hidden` are identical to the verifier's. `_v` uses the file's `token_hex` import. `_canon` is the file's own, with the same `json.dumps` arguments.

## 6. Contract items

**Item 1: the order, and whether it is enough by itself (measured).**
- **The order test fails when a new-head rule moves first.** The runner is `okill.py`: each mutant against the order test alone (`-k`), the control first, KILLED only on a FAILED test.
  - Controls: `1 passed, 263 deselected`, for the order test and for the R3V-3 test.
  - O1 to O6 (each stage-2 rule run first in `scrub_payload`, or stage 2 before the PAYLOAD rules) fail at line 2016, where the value shows.
  - O7 (stage 2 before stage 1 in `scrub`) fails at line 2012, the list-structure assertion.
- **The test's own control:** each stage-2 rule, moved first by the test itself, shows the value.
- **Is the order enough by itself? No (measured).**
  - Two ruled stage-1 changes read heads the PIN never read: D6's guard (DISC-1) and the credentials floor's refusal (DISC-3 and DISC-4).
  - The same-rule share is closed; the cross-rule share is the residual.
  - The chains of R3V-1's mechanism point 4:
    - (a) A freed head that takes an R1 head as its value. R1 now runs before stage 2, so such a value runs over R1's marker. The red items and the order test's Negotiate case hold this (verified).
    - (b) The marker's `>` satisfying `_KEY_L`. The chain soup's glue `""` puts heads right after values that become markers, and REAL is 0 in 9,000 texts × 6 views (verified). That this case is covered is inferred from the generator; I did not count it separately.
- **The verifier's stop list (the fallback) was not used.** No frozen item that the order breaks could be kept by a stop. B1's cost is inside the PAYLOAD rules. DISC-6 and DISC-7 equal the PIN. A stage-1 stop would itself read a head the PIN never read (inferred, from L1 and G1).

**Item 2: 0 losses against the PIN (the verifier's probes, adapted copies, final bytes 8c0b66b6 checked at batch start).**

| probe | round 4 | round 3 (my run; matches the verifier's) |
|---|---|---|
| e2e_n2r, 5 shapes, digest / convert | hid / hid in all 5; one digest LEAK (user turn, `curl -u`), which the PIN also LEAKs in the digest; cookie values digest 0, convert 0 (PIN 1 / 5) | convert LEAK in 5 of 5 |
| rand_n2c, seed 20260929, 4,000 × 6 | `LOST later values by view: {} \| total 0` | 923 (call 280, call2 278, ptxt 280, txt 85) |
| rand_n2c, seed 11, 4,000 × 6 | `{} \| total 0` | 1,001 |
| sch3, seed 42, 3,000 × 6: LATER / TOKEN / OTHER | 0 / 0 / 0 (`total lost value characters: 0`) | LATER 1,400 / TOKEN 3,573 / OTHER 2,561 (7,534) |
| r3d4, seed 9, 3,000 × 5: BODY / TAIL | 0 / 0 | 0 / 24,817 |

The ruled classes, each on its own row. Real value characters (REAL) are 0 everywhere.

| source | ESC (no value) | K-direct (D1 or F15's refused extent) | K-chain | NAME (D6) | REAL |
|---|---|---|---|---|---|
| pos3 v4b, 4,000 × 6 | dig 3,447, txt 3,447, call 5,406, call2 18,449, pdig 5,406, ptxt 5,406 | dig 3,489, txt 3,489 | 0 | dig 94, txt 94 | 0 |
| pos3 rl2, 20,000, decoded | 719 | 359 | 0 | 571 (round 3: 30,646) | 0 |
| pos3 rl2, 20,000, raw | 1,655 | 229 | 0 | 316 (round 3: 17,958) | 0 |
| chain soup, seeds 1/2/3 × 3,000 × 6 | e.g. seed 1: call 2,552, call2 5,813, dig 1,108 | seed 1: call 2,589, dig 2,660, pdig 2,708, ptxt 2,589, txt 2,541 | seed 1: call 9, ptxt 9 (the word `Negotiate`); seeds 2 and 3: 0 | seed 1: call 2,553, dig 1,903 | 0 |
| ck3 (R3-D3 in isolation), seed 5 × 3,000 and seed 6 × 6,000, × 6 | 24,120 / 48,532 | 0 | 0 | 0 | 0 |
| corpus, main transcript (convert() and digest modes) | none | 0 | 0 | 0 | 0 |
| corpus, 372 subagent files | call 43; dec 725 (per mode) | 377 (per mode) | 0 | 100 (per mode) | 0 |

- **pos3 rl2, values after lost names:** decoded HID 6, LOSS 19, NOVALUE 25, PINSHOW 14; raw HID 7, LOSS 10, NOVALUE 7, PINSHOW 13. Every LOSS value is made of K, NAME or ESC characters (chains of names).
- **Corpus detail:**
  - main: 163,679 lines and 57,259 texts. 13 / 14 / 14 texts changed (call/settle, dec/scrub, dec/settle), and in each round 4 hides more.
  - subagents: 164,955 lines and 88,411 texts. The values after lost names are HID 1, LOSS 4 and PINSHOW 6; the LOSS values are names, K+NAME.
  - Thinking blocks are never read; the probes print masked shapes and counts only.

**Item 3: the red items.** All 11 are in the file, with their bodies and assertions unchanged, and they pass. Round 2's 16 pass (§5, §7, §9).

**Item 4: R3V-2, the tail residual.** It is 0.
- r3d4 gives BODY 0 and TAIL 0 (round 3: TAIL 24,817), because stage-1 pwd and credentials values keep the PIN's extent (DISC-2).
- sch3's TOKEN class is 0 (round 3: 3,573). In `scrub_payload` the PIN's Basic and bearer payload rules now take those tokens whole, tails included, before stage 2 runs. In `scrub()` the PIN showed those tokens.
- So I did not need the verifier's `_KEY_L` candidate.

**Item 5: V12 and V14 are KILLED, each assertion named with its mutant.** See DISC-8 and §8.
- V12: `tests/test_transcript_export.py:2027` asserts `'Authorizatio...ed>token=zq12' == 'Authorizatio...ic <redacted>'`.
- V14: `tests/test_transcript_export.py:2030`.

**Item 6: R3V-4.** See §3.

**Item 7: everything else, on the final bytes.**
- **N1 closed:**
  - floor_units2 shows only D1's 7 cells per credentials head, in dig and txt (`credentials=` and `"credentials": "`, 28 cells);
  - e2e_floor: all hid (the PIN LEAKs the Write convert);
  - e2e_n2: all hid, cookie values 0 / 0 (PIN 2 / 4).
- **V4 per position:** item 2's table.
- **R3-D1 and R3-D3 in isolation:** ck3 gives REAL 0, K 0, NAME 0. rl2 has no REAL.
- **B1:**
  - worst at 64k: pemL1 0.0054, cookie1 0.0437, scheme1 0.0037, pwd1 0.0311, cred1 0.0337, neg2 0.0515, cookie2 0.0714, scheme2 0.0509, pwd2 0.0398, cred2 0.0416, scrub 0.1594 s, payload 8.2887 s (DISC-5);
  - 24 rows re-timed from 64k to 512k (the flagged rows and the worst per target, minimum of 3): every row grows ×1.3 to ×3.23 per doubling, and no ×3 step comes after 128k;
  - worst at 512k: payload `auth bs` 0.8884 s, scrub `ck heads esc` 0.8756 s.
- **B2 and B3:** LOST 0 in all 6 views (B2 n=455, B3 n=672).
- **D2:** DISC-6. **D6:** d6chk has 0 LOST rows (10 shapes × 6 views); see DISC-1.
- **F1:** escape_named 30 of 30 hid/hid; escape_nonascii 12 of 12 hid/hid.
- **F15:** cred_convert gives "T redacted: False | ordinary words gone: []" (D1 as ruled).
- **F2:** negotiate, 11 of 11 schemes "token survives in: none".
- **F7:** pemL worst 0.0054 s.
- **F10:** mutant N1 KILLED by `test_each_gate_pattern_name_labels_its_own_rule`.
- **F12:** W-group 20 of 20 KILLED.
- **Value gate:** §3.
- **Test isolation** (strace on file syscalls plus a GH_TOKEN/GITHUB_TOKEN lookup logger; the two changed files):
  - absent: `336 passed, 1 xfailed in 54.60s`; 0 syscalls and 0 opens on all four source paths; 0 token lookups;
  - fakes: `336 passed, 1 xfailed in 52.01s`; 0 opens; 3 stat-only syscalls on the copy's FAKE `.pc-bridge.env` (Python start-up probes); 0 lookups;
  - control: `1 passed in 0.22s`; opens 1 / 1 / 1; 1 GH_TOKEN lookup (`tests/test_zz_trace_control.py:11`, a scratch control file I deleted after the run).
- **Laya lock,** twice (13:53:41Z and 13:54:23Z):
  - v2 `collect_v2` at 434b727dfd: new differs from the PIN in 0 of 6,220 items;
  - v1 `collect` at eb256f49c0: 0 of 1,788;
  - v1 `collect` at 0b342c7a29: 0 of 1,788;
  - controls: N-pwd differs in 16 on v2 ("new equals PIN on 16 of them") and 0 on v1; E differs in every item.
- **Digest identity:** "fixed at 808446565 bytes; digests pin 21 new 21 ; identical 21 ; differ []". 20 of 21 are byte-equal to the committed digests; `chat-2026-09-29.md` has grown since the last export.
- **Manifest:** regenerated (§3).

## 7. Gates (my worktree, through `masked.sh absent`, `--basetemp` as a pytest argument outside every work tree)

```
floor pass 1 (start 14:11:59Z)
pytest-exit: 0
pytest-summary: 893 passed, 1 xfailed in 190.32s (0:03:10)
12 files set=27f27a25516b
floor pass 2 (start 14:15:20Z)
pytest-exit: 0
pytest-summary: 893 passed, 1 xfailed in 183.18s (0:03:03)
12 files set=27f27a25516b
two files pass 1 (start 14:18:32Z)
pytest-exit: 0
pytest-summary: 336 passed, 1 xfailed in 32.01s
2 files set=e8f27bcb91e7
two files pass 2 (start 14:19:04Z)
pytest-exit: 0
pytest-summary: 336 passed, 1 xfailed in 31.94s
2 files set=e8f27bcb91e7
```
- **The floor count:** round 3's 877, plus 16 new passing tests (the 11 red items, the order test, the R3V-3 test and 3 refused-value cases), plus the strict xfail.
- **By file:** `test_transcript_export.py` has 263 passed and 1 xfailed; `test_session_export.py` has 73 passed.

## 8. Mutation on the final bytes

**Setup:** four worker copies of the final files. The control passes whole first in each copy. KILLED counts only on a FAILED test, never on an error. The runner creates the `--basetemp` parent (`mbt/`) before the controls (AF-AP-223).

| group | mutants | KILLED | SURVIVED | INVALID | controls |
|---|---|---|---|---|---|
| r4 (O1-O7, N0, G1, G2, L1, L2, V12, V14, S1-S4, NEG) + w (F12's 20) | 39 | 39 | 0 | 0 | 4 × `263 passed, 1 xfailed` |
| x (VERIFY-SCRUB2-R1-R2's set) + rep (round 2's) | 28 | 27 | 1: X13, equivalent (DISC-11) | 0 | 4 × `73 passed`; 4 × `263 passed, 1 xfailed` |
| y (round 3's clauses; Y30 and Y33 are now pinned) | 39 | 39 | 0 | 0 | 4 × `263 passed, 1 xfailed` |

**Total:** 106 mutants, 105 KILLED, 1 equivalent survivor. S1 to S4 pin each stage-1 rule to the PIN's head set:
- S1: the stage-1 Cookie rule reading every Cookie head;
- S2: the stage-1 scheme rule reading an escaped quote;
- S3 and S4: `_KEY_L` in stage-1 pwd and credentials.

Round 3's y-group survivors Y30 and Y33 are now KILLED (by the Y30 assertion and the Y33 assertion).

## 9. Patch proof (a fresh detached worktree at the PIN)

```
git worktree add -q --detach <scratch>/proof bef1e9e      -> rc 0, HEAD bef1e9ed1199…, 0 porcelain lines
git -C <proof> apply --check tasks/briefs/system1/SCRUB2-R1-R4.patch   -> patch-applies-check-ok
git -C <proof> apply ...                                  -> the five sha256 prefixes equal the worktree's
== proof worktree: tests/test_vscrub2r1r3_red.py
pytest-exit: 0
pytest-summary: 11 passed in 0.07s
1 files set=8d2adae291be
== proof worktree: tests/test_vscrub2r1r2_red.py
pytest-exit: 0
pytest-summary: 16 passed in 0.12s
1 files set=bcd44bc128b4
== proof worktree: tests/test_transcript_export.py tests/test_session_export.py
pytest-exit: 0
pytest-summary: 336 passed, 1 xfailed in 33.55s
2 files set=e8f27bcb91e7
```
Also, at the shared tree's HEAD ace09da, `git apply --check` prints `round-4-patch-applies-at-HEAD`.

## 10. Beyond the brief: consumers at HEAD ace09da plus the patch (masked, one file at a time)

Fourteen scripts import `transcript_export`. The relay (task #373) landed after the PIN, so its re-PIN is the coordinator's call.

| test file | result | set id |
|---|---|---|
| `tests/test_jev_relay.py` | 24 passed | 27cdda9dfd9c |
| `tests/test_chat_find.py` | 40 passed | fd6179308190 |
| `tests/test_hiccup_scan.py` | 41 passed | 12ed0f84ee40 |
| `tests/test_jev_trim_compaction.py` | 99 passed | 7f396804fe23 |
| `tests/test_jev_trim_replay.py` | 68 passed | 1bb7608ed22a |
| `tests/test_laya_ft.py` | not finished in 280 s | 8b147318aa48 |

The six files together also ran past a 580-s limit, with no result.

## 11. Self-attack: the three likeliest ways this is wrong

1. **The K-chain residual is a loss that D1's ruling does not cover.**
   - **Not ruled out.** It is measured (DISC-4): a constructed text only; 9 name characters in 9,000 × 6 soup views; corpus 0.
   - A strict xfail holds it.
   - If the ruling says it is not D1's class, a structural fix is needed. The stage-1 rules and the PAYLOAD rules would have to leave a refused credentials extent alone until stage 2.
   - This is the likeliest NOT-READY.
2. **A stage-1 rule still reads a head the PIN never read, and the order test cannot see it.**
   - **Ruled out:**
     - 9 of the 13 stage-1 rules are byte-identical to PIN rules;
     - the PAYLOAD rules and the opaque rule are byte-identical;
     - the other 4 carry ruled changes only, and the S1-S4 mutants pin their head sets to the PIN's;
     - the D6 guard and `_LATER_*` stops that did read such heads are gone from stage 1, and G1, G2, L1 and L2 are KILLED.
   - **Residue:** DISC-3's keep-as-is branch reads the PIN's head, and the refused value's extent is the PIN's.
3. **The tables come from stale bytes.**
   - The earlier round-4 probe outputs ran on e86e4060, which differs from the final bytes by one comment.
   - **Ruled out:** I re-ran every probe, the Laya lock, the digests, the corpus, the census and D7 on 8c0b66b6 (hash checked at batch start). The outputs equal the earlier ones where both exist.
   - The two reboots killed only a void gate and a listing.

**Also checked:**
- A hollow order test: its control fails when a rule moves first, and O1-O7 are KILLED by it alone.
- A weakened old test: no round-2 or round-3 assertion was dropped. DISC-2's moved assertions are listed, and the PIN-head texts are now held to exact equality with SCRUB2's forms.

## 12. Evidence tiers

- **Verified (measured, pasted):** §4-§10, DISC-1 to DISC-3 and DISC-5 to DISC-13, and DISC-4's example and size.
- **Inferred:**
  - DISC-4's class is D1's K (by the verifier's classifier);
  - that stops could not keep DISC-5, DISC-6 or DISC-7 (§6, item 1);
  - the soup's coverage of the `>`-after-marker case.
- **Assumed:** none.

## 13. Paths and cleanup

- **Shared tree:** I created one file, `tasks/briefs/system1/SCRUB2-R1-R4.patch` (untracked). No git write in the shared tree; the only git metadata I touched was worktree add and remove.
- **Worktrees:** I made three: `scrub2r4/wt`, `scrub2r4/proof`, `scrub2r4/headwt`. All are removed (`git worktree list` shows none), and no `.pc-bridge.env` remains in scratch.
- **Processes:** none of mine is running. The pytest processes running now belong to other lanes.
- **Scratch** (`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/scrub2r4/`, 7.4 MB):
  - outputs: `fin_*.txt`, `g_*.txt`, `okill.txt`, `mut4_final_{r4w,xrep,y}.txt`, `corpus/fin_{main,sub}.json`, `progress.txt`;
  - probe copies: `vp/`. Their `new` root points at the removed worktree. To re-run them, apply the patch to copies of the PIN's two scripts, as I did with `trees/fin` for `kx_run.py`.
  - `SCRUB2-R1-R4.patch` is the same bytes as the deliverable.
- **Verifier's scratch:** read only, never written.
