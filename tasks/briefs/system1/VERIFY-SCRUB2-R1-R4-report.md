> **Coordinator note (2026-09-29 18:5xZ):** extracted by `scripts/stack.py harvest` (run s-20260929T185614Z-d7ba2a; hand-back sha256 prefix f1ac979c792b, 27,043 characters). Served model: claude-opus-5-5 on all 1,137 assistant records, 0 refusal stops, 3 compactions, 10 tool errors. `report_lint`: 0 refs; no local ids.
>
> **Ruling on R4V-1, the K-chain: a new loss, so round 4 does not land.** "D1's K class" in the round-4 brief was the coordinator's shorthand, copied from the round-3 verifier's class K. That class was counterfactual and too broad (R4V-10). D1 as ruled keeps ONE value: a decoded credentials value with an escape among its first 8 characters. The K-chain frees OTHER values, ones the PIN hid with other rules, and they reach `session_export.convert()` and the relay's upstream. That is a loss against the PIN on the canonical payload path, the class that blocked round 3 (R3V-1). So the verifier's NOT-READY stands under D-034: it contradicts a frozen criterion (item 2, 0 losses against the PIN). The real corpus holds no affected secret (90 positions, all the word "Negotiate"), and the shape is narrow. A known leak in a security scrubber still does not land on a reading of a shorthand.
>
> **State.** Round 4 stays a patch (`tasks/briefs/system1/SCRUB2-R1-R4.patch`), NOT applied. The tree keeps the PIN's scrubber, which does not have this leak; F1 and F15 stay open there. The relay (task #373) and the fast-jev-output plugin stay unwired, and VERIFY-JEV-RELAY waits.
>
> **The fix is measured, and it is a fifth round.** The verifier's shield changes 24 lines in `scrub_payload`: it masks the kept value, runs the rules that read heads inside it, restores the value and runs them again. It passes all three red files and keeps every probe the verifier ran. `scrub_payload` runs x1.62 slower; `scrub()` is unchanged. Its sentinel needs a collision-proof form, and sch3, r3d4, pos4 and the census were not measured on it. The owner authorized one more round (D-108 item 3), which was round 4, so a round 5 needs the owner's word; the question is in the coordinator's reply.
>
> **Follow-ups:** R4V-2 to R4V-5, R4V-8 and R4V-9 (two chains on the PIN itself, one of which the relay sends upstream) are issue #86 (D-108 item 2). They belong to whichever round lands.

# VERIFY-SCRUB2-R1-R4: report (task #321)

- **Verifier:** the sandbox adversarial verifier (Opus 5.5), round 3's verifier, resumed.
- **Change under test:** `tasks/briefs/system1/SCRUB2-R1-R4.patch` (sha256 f18f85c9b0abaf7b…, rounds 3 and 4 together).
  - It was applied only in a `git archive` of the PIN in my scratch. I made no worktree.
  - The patched `scripts/transcript_export.py` has sha256 8c0b66b6fa41f8c8c18e432023ecebc1177748560d104b4f3d05bec4dafabfd2.
- **PIN:** origin 0ab1df7.
  - These files did not change from 0ab1df7 to origin a3e23d8 ("transcripts: scrubbed sandbox chat digests (2026-09-29)"): the five patched files, `scripts/jev_relay.py` and `tests/test_jev_relay.py`. `git diff --stat` was empty at 18:4xZ.
- **Window:** from the premise at 16:38:13Z to my last clock read at 18:49:10Z.
- **Contract:**
  - my brief `tasks/briefs/system1/VERIFY-SCRUB2-R1-R4-brief.md`, items 1-10 and GATE;
  - the builder's `tasks/briefs/system1/SCRUB2-R1-R4-brief.md`, items 1-7.
- **Report file:** the harness forbids report `.md` writes by this agent. This message is the whole report.

## 0. Gate recommendation

**NOT-READY on R4V-1, the K-chain.**
- R4V-1 meets the whole blocking predicate if "D1's K class" means what the D1 ruling says.
- This rests on a contract reading, not on evidence I did not reproduce.
- **If the coordinator rules the K-chain into "D1's K class", my recommendation is MERGE-READY-WITH-FOLLOWUPS.** That broad reading comes from my own round-3 class definition.

**Why:**
- **Round 4 closes R3V-1 by the order.** Every R3V-1 probe reads 0 lost, and the 11 red items pass.
- **R4V-1, how it works:**
  1. D1 keeps a refused `credentials` value whole.
  2. A stage-1 or PAYLOAD rule then reads a head inside that value. The PIN never read that head, because its credentials value hid it.
  3. That rule's token eats the name of a later head.
  4. The later value, which the PIN hid with its own rule, shows.
- **Where it shows:** in `session_export.convert()`'s events, and at the relay's upstream.
- **What the builder did:**
  - found the mechanism (DISC-4);
  - pinned it with a strict xfail marked "left for a ruling";
  - sized it on the corpus only ("9 chars, no planted value").
- **Size:**
  - A targeted generator loses 498 planted values (6,972 characters) per 8,000 texts, in three `scrub_payload` views.
  - The real corpus loses no secret value. It has 90 positions, and all of them are the word "Negotiate".
- **A fix is feasible and measured** (the "shield", R4V-1 below). It closes the chain and keeps every probe I ran. It makes `scrub_payload` x1.62 slower on the 21 committed digests.
- **Everything else** holds, or is a follow-up (R4V-2 to R4V-5).

## 1. Premise

- I re-ran every `$` line of the brief's premise at 16:38:13Z. Every line matched, so there is no CONTRACT-INVALID.
- **No reboot voided a run of mine.** `uptime -s` reads 14:36:27, before my first command at 16:38Z.

## 2. Finding inventory

| id | class | finding |
|---|---|---|
| R4V-1 | **BLOCKER** (the ruling decides) | K-chain: a head inside a credentials value that D1 keeps frees a later value the PIN hid (`convert()`, relay) |
| R4V-2 | FOLLOW-UP | Mutant A7 survives: no test pins stage-1 credentials before the link rule and PAYLOAD in `scrub_payload` |
| R4V-3 | FOLLOW-UP | Round-3 gains given back, each equal to the PIN (DISC-6, DISC-7, DISC-2's shapes); no cell hides less than the PIN |
| R4V-4 | FOLLOW-UP | DISC-5 is the PIN's P0/P4 quadratic path (task #333); round 3's side-effect linear time on those families is gone |
| R4V-5 | FOLLOW-UP | D7: `scrub()` x1.71 and `scrub_payload()` x1.22 the PIN's time on the 21 digests |
| R4V-6 | INFO (evidence audit) | DISC-4's size comes from the corpus only; contract item 1 said "Measure it; do not assume it" |
| R4V-7 | INFO | DISC-10 and DISC-11 confirmed with my own mutants; K3 is equivalent |
| R4V-8 | INFO | The linear-time test failed once under heavy load (1 of 12 control runs); round 4's worst call is 0.240 s of the 2.0 s bound |
| R4V-9 | INFO | PIN behaviours seen, not changed by round 4 |
| R4V-10 | INFO | My round-3 K class was too broad: round 3 had the same chain, and I did not report it |

### R4V-1 (BLOCKER, the ruling decides): the K-chain

**Evidence level:** reproduced through:
- the red file;
- end to end through `export()` and `convert()`;
- a relay round trip;
- two generators;
- the corpus.

**Mechanism.** I re-derived it from the patched source. The stage comment above `STAGE1_PATTERNS` states it too.
- **Example text:** `credentials=Z\tBearer k1a2b3c4d5e6f+X_PASS = V`, decoded. Here `\t` is a literal backslash and `t`.
- **On the PIN:**
  1. The credentials value `Z\tBearer` (9 characters) is hidden, so the word `Bearer` is gone.
  2. The PAYLOAD PASS rule reads `X_PASS = V` and hides V.
- **On round 4:**
  1. `_CRED_FLOOR` refuses the value, because an escape is among its first 8 characters (D1).
  2. `_credentials_or_same` keeps the value whole.
  3. Stage 1's Bearer rule reads `Bearer k1a2b3c4d5e6f` and stops at `+`.
  4. PAYLOAD's Bearer-tail rule takes `+X_PASS` as the token's tail.
  5. The PASS rule finds no head, so V shows.
- **In canonical JSON** (`convert()`'s tool_call), F15's shape does the same: `credentials=ab`, then a real line end, which JSON writes as `\n`.
- **Inner head (H1):** Bearer and its tail, Basic, bearer, the R1 escaped quote, PASS, the key rules, the bridge link.
- **Eaten head (H2):** an R1 name, a PASS name, curl's `-u`, a URL userinfo, a lower-case bearer.
- **scrub() is not affected:** 0 in the dig and pdig views. No PIN-head rule runs after those rules in `scrub()`.

**Extent** (`probes/kchain.py 8000 new 405`, 8,000 texts × 6 views, `out/kchain_new_405_8k.txt`). KC = a lost value character outside the kept value that undoing D1 would hide.

| view | planted values lost (KC) | value characters |
|---|---|---|
| txt (decoded, settle) | 224 | 3,136 |
| call (canonical JSON, settle) | 137 | 1,918 |
| ptxt (pasted JSON, settle) | 137 | 1,918 |
| dig, pdig, call2 | 0 | 0 |
| **total** | **498** | **6,972** |

- **Inside the kept value** (KD, D1 as ruled): dig 275, pdig 199, txt 33, call 24, ptxt 24.
- **The flip side:** round 4 hides H1 tokens that the PIN showed, in 10,980 view-texts. V4 counts per position, so these gains do not offset the losses.
- **String level** (`probes/vdiff.py kchain 8000 405 new,shield`, `out/vdiff_kchain_405_io.txt`):
  - round 4 LOST_PIN outside the refused value: 532 (call 150, ptxt 150, txt 232);
  - round 4 LOST_PIN inside it: 489;
  - UNSETTLED: 0.
- **Corpus** (`probes/corpus_n2r4.py`, `out/scan4_*.txt`):
  - subagents, first half: KC 90 positions in 10 regions. All are the word "Negotiate" after an escaped-quote `Authorization` in probe texts.
  - subagents, second half: ESC 12 only.
  - main transcript (818,493,191 bytes, 4 ranges): 0 in every class.
  - REAL 0 everywhere.
- **Round 3 had the same chain** (`out/kchain_r3_404_2k.txt`; e2e: round 3's `convert()` shows all 5 values).

**End to end** (`probes/e2e_kchain.py`; runs at 17:29:02Z and again at 18:44:25Z from the final scratch). Five shapes, through `export(sources=())` and `session_export.convert()` with a fake key:

| version | digest | convert |
|---|---|---|
| round 4 | 4 hid, 1 LEAK | **5 LEAK** |
| PIN | 4 hid, 1 LEAK | 5 hid |
| shield | 4 hid, 1 LEAK | 5 hid |
| round 3 | 4 hid, 1 LEAK | 5 LEAK |

The one digest LEAK is the same shape on every version, the PIN included (R4V-9).

**Relay** (`probes/relay_rt.py`, 17:30:35Z).
- **Setup:**
  - `scripts/jev_relay.py serve` on loopback;
  - a fake upstream thread;
  - a fake key file;
  - `--no-default-sources` and a fake value file;
  - inside `masked.sh absent`.
- **Results:**

| version | R4V-1 fakes sent upstream | R4V-1 fakes in its data log |
|---|---|---|
| round 4 | 3 of 3 | 3 |
| PIN | 1 of 3 | 1 |
| shield | 1 of 3 | 1 |

  - The one fake that the PIN and the shield send is the PIN's own chain (R4V-9).
  - On all three versions, the value gate refused the fake known value: 422, and it did not reach the upstream.
  - A scrub-changed object key also gave 422 on all three.

**Contract mapping.**
- **Builder's item 2:** "0 losses against the PIN … except the classes ruled before (F15's over-redactions, D1's K class, D6's name shown)".
- **The principle of item 1:** every rule that reads a head the PIN never read runs after every PIN-head rule. The inner heads here are heads the PIN never read.
- **The exemption is ambiguous. Two readings:**
  - **D1 as ruled** (SCRUB2-R1-R2-report D1, restated at `_CRED_FLOOR`): "a decoded credentials value with a literal `\n`, `\r`, `\t` or `\f` among its first 8 characters stays". The K-chain's lost characters lie OUTSIDE that value, in values that other rules (R1, PASS, curl, URL, bearer) hid on the PIN. **On these words, this is a new loss.**
  - **My round-3 class K** ("hidden when the credentials floor counts escapes: D1 undone", VERIFY-SCRUB2-R1-R3-report line 267) is counterfactual, so it includes the K-chain. The builder's code comment uses this reading ("D1's K class").

**The rest of the predicate:**
- **Canonical path:** yes. `session_export.convert()`'s settle views, and `jev_relay.py` to the upstream.
- **Material effect:** a value the PIN hid leaves the machine (the relay) and enters the session-export events.
- **Discriminator:** `probes/test_vscrub2r1r4_red.py` (sha256 2006770787f4ead0: 5 canonical-JSON items, 5 decoded items, 2 controls), 1 files set=b530580ec13c. Its results:
  - round 4: `10 failed, 2 passed in 0.17s` (again at 18:44:25Z: `10 failed, 2 passed in 0.13s`);
  - round 3: `10 failed, 2 passed`;
  - PIN: `12 passed in 0.04s`;
  - shield: `12 passed in 0.06s`.
- **Ownership:** the scrubber. The fix sits in `scrub_payload`.

**D-034.**
- **For blocking:**
  - By this task's own precedent: R3V-1 is the same class (a head the PIN never read, read before a PIN-head rule, frees a value the PIN hid in `convert()`), and it blocked round 3.
  - D-057 and D-059 blocked J1-1 regressions that put a PIN-redacted value through the real path.
- **Against blocking:**
  - The corpus has 0 secret values affected.
  - The shape needs a credentials value of 1 to 7 characters, an escape among its first 8, and two glued heads.
  - D-034 lists edge cases as follow-ups.
- The owner said round 4 is the last round. The owner's ruling decides.

**Reproduction:**
```
W4=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r4
M=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/masked.sh
cd $W4/red_new && $M absent $W4/vt -- bash /home/user/agent-factory/scripts/test_summary.sh tests/test_vscrub2r1r4_red.py -p no:cacheprovider --basetemp=$W4/bt/r4v1
#   the same in $W4/red_pin and $W4/red_shield gives 12 passed
cd $W4 && VSCRUB_EXTRA_ROOTS=shield=$W4/var_shield $M absent $W4/vt -- python3 $W4/probes/e2e_kchain.py new,pin,shield
cd $W4 && $M absent $W4/vt -- python3 $W4/probes/relay_rt.py new=$W4/new pin=$W4/pintree shield=$W4/var_shield
cd $W4 && python3 $W4/probes/kchain.py 8000 new 405 4
cd $W4 && VSCRUB_EXTRA_ROOTS=shield=$W4/var_shield python3 $W4/probes/vdiff.py kchain 8000 405 new,shield 4
```

**Fix options:**

1. **The shield** (measured; feasibility only, not a proposed patch).
   - **File:** `$W4/var_shield/scripts/transcript_export.py` (sha256 b4b694c54688c436). It changes 24 lines, all in `scrub_payload`.
   - **What it does:**
     1. In `scrub_payload`, the refused credentials value becomes a sentinel of the marker's length.
     2. The stage-1 rules after the credentials rule, then PAYLOAD, run.
     3. The kept value is restored.
     4. Those rules and PAYLOAD run again, then stage 2 and the opaque rule.
   - This is item 1's order applied to the heads inside a kept value.
   - **Measured results:**
     - the R4V-1 red file: `12 passed`; the R3 red file: `11 passed in 0.09s` (set=8d2adae291be); the R2 red file: `16 passed in 0.06s` (set=bcd44bc128b4), all at 18:40:09Z;
     - e2e_kchain: `convert()` hid 5 of 5; `e2e_n2r` is identical to round 4 (18:40:47Z);
     - the relay: equal to the PIN;
     - kchain LOST outside the kept value: 0; LOST_NEW against round 4: 0; rand_n2c seeds 11 and 20260929: LOST_PIN 0;
     - the builder's two test files: `1 failed, 336 passed in 41.66s` (the 2-file set e8f27bcb91e7, log time 17:27:10). The one failure is the builder's strict xfail turning XPASS(strict), which is expected when the residual closes.
   - **Cost:** D7 `scrub_payload` 11.863 s against round 4's 7.344 s (x1.62). The PIN's P0/P4 families run about x2 (`out/disc5.txt`).
   - **Caveats:**
     - The private-use sentinel needs a collision-proof form in a real design, for example span bookkeeping.
     - Not measured on the shield: sch3, r3d4 and pos4 (they need provenance, which the prototype does not keep), and the census.
2. **Undo D1:** the credentials floor counts characters again. This closes the chain but re-opens F15's over-redaction, and F15 is frozen by item 7.
3. **Reorder** (stage-1 credentials after PAYLOAD; `var_credlate`, the same shape as mutant A7): worse. kchain 8k gives LOST_PIN 1,541 (round 4: 1,021) and LOST_NEW 520.
4. **A stop list:** not measured.

### R4V-2 (FOLLOW-UP): mutant A7 survives; no test pins stage-1 credentials before the link rule and PAYLOAD

- **Evidence level:** reproduced.
  - Mutant A7 moves the stage-1 credentials rule to after PAYLOAD in `scrub_payload`.
  - It SURVIVED: `263 passed, 1 xfailed`.
- **Not equivalent** (`probes/mutdiff4.py`, `out/mutdiff4_2929.txt`, K-chain generator, 8,000 texts):
  - 1,902 texts differ;
  - LOSS against round 4: 530;
  - LOSS against the PIN: 1,503 (round 4: 973).
- **Concrete killing text:** `credentials = jHAoL\fx9y8z7w6https://q1.trycloudflare.com/k6rMS4AuzM5y2,api_key=\"V\"` in the call view (canonical JSON). The PIN and round 4 hide V; A7 shows it (`out/a7_example.txt`).
- **The same text in the txt view is also an R4V-1 case:** round 4 shows V there, and the PIN hides it.
- **Contract mapping:** builder's item 1 ("D1 and D6 as ruled stay where the PIN's rules run") and item 7. The production order is right; only the test is missing.
- **Material effect:** on the tests' power only.
- **Fix:** add the call-view assertion above as a test.

### R4V-3 (FOLLOW-UP): round-3 gains given back, each equal to the PIN

- **DISC-6** (`probes/d2_sib4.py`):
  - LOST against the PIN: 0.
  - Round 4 shows the second value in 208 view-texts where round 3 hid it, all in the Negotiate-next column. The PIN shows all 208.
- **Do the contract's words hold?** "D2's fix" holds as round 2's verify measured it: 0 lost against the PIN, and the escaped-quote scheme token stays on its own line. My round-3 wording "round 3 equals round 2 in every cell" fails in that column.
- **Does any cell hide less than the PIN?** No.
- **DISC-7:** 3 plain-head texts show V, as on the PIN. Rounds 2 and 3 hid it. R3-D2 is not on the frozen list.
- **DISC-2** (`probes/disc123.py`): 0 LOST against the PIN. Five shapes go from round 3's gain back to the PIN's behaviour:
  - `pwd=abcd_pwd: <v>`
  - `pwd=abcd/pwd = <v>`
  - `pwd=x\tpwd: <v>`
  - `credentials=ab\tpwd: <v>`
  - `pwd=q1w2e3r4\tPWD: <v>`
- **Fix:** an owner call. These are gains beyond the PIN; V4 holds.

### R4V-4 (FOLLOW-UP): DISC-5 is the PIN's path

- **The rules:** the PAYLOAD list is byte-identical to the PIN's. The cost sits in P0 (the bridge-host rule) and P4 (the URL-password rule), task #333's class.
- **Timings** (`probes/disc5.py`, 17:43:56Z, `out/disc5.txt`):

| family | size | PIN | round 4 | round 3 | shield |
|---|---|---|---|---|---|
| "r3 sch esc names" | 64k | 7.798 s | 7.623 s | 0.074 s | 15.301 s |
| "r4 dotted" | 32k | 10.044 s | 10.48 s | 10.192 s | — |

- **Round 3's linear time** on the first family was a side effect: its rules hid those heads before P0 ran.
- **Fix:** task #333. If the shield lands, fix P0/P4 first, or run the second PAYLOAD pass only over the kept spans.

### R4V-5 (FOLLOW-UP): the constant factor, D7

Measured by `probes/d7v.py` at 17:53:02Z over the 21 digests (4,138,166 characters):

| version | scrub | scrub_payload |
|---|---|---|
| PIN | 2.877 s | 5.999 s |
| round 3 | 4.224 s | 6.637 s |
| round 4 | 4.930 s | 7.344 s |

- Round 4 against the PIN: x1.71 and x1.22.
- Round 4 against round 3: +16.7% and +10.7%. The builder measured +18.5% and +8.0% (DISC-12).
- This is linear cost, not growth.

### R4V-6 (INFO): evidence audit of DISC-4

- The builder's size, "9 chars, no planted value", is right for the corpus.
- Contract item 1 said: "Measure it; do not assume it … the chains … are the cases to check first."
- A targeted generator finds 498 planted values per 8,000 texts.
- The builder's other claims reproduce. Each of these matched:
  - DISC-1's table;
  - the r4 mutant table;
  - DISC-2, DISC-5, DISC-6, DISC-7 and DISC-9;
  - DISC-11.

### R4V-7 (INFO): DISC-10 and DISC-11 confirmed

- **DISC-10:** 12 single-stage mutants of mine, each KILLED by a FAILED test (§5). The per-stage pins work, `test_each_named_rule_takes_8_characters_and_leaves_7` among them.
- **DISC-11:** X13, X13b (no Bearer stop) and X13c (neither stop) SURVIVE.
  - My differential: 0 of 44,000 texts × 6 views differ from round 4. 20,000 of those texts aim at the stops: Negotiate tokens glued to Bearer or bridge links, in cases, whitespace, JSON escapes and multi-label hosts.
  - This matches the argument: stage 1's Bearer and link rules turn every `_BEARER` and `_LINK` match into a marker first.
  - X13e (no stop at all) is KILLED.
- **K3** (the keep branch without its 8-character floor): 0 texts differ, so it is equivalent. A run under 8 characters cannot hold a credentials head.

### R4V-8 (INFO): a wall-clock test under load

- My first run of the v group stopped at its control at 18:19:28Z. The run is void by its own rule.
  - Worker w1 gave `1 failed, 205 passed in 31.01s`.
  - Test 206 in collection order is `test_the_key_block_and_cookie_rules_run_in_linear_time`. Its bound is 2.0 s per call.
  - The box ran 4 session_export controls of about 92 s each, next to other lanes' pytest runs.
- **Unloaded, best and worst of 3** (`out/linear_child.txt`):
  - round 4: worst call 0.240 s best / 0.306 s worst;
  - round 3: 0.207 s best / 0.294 s worst.
- The re-run passed all 4 controls. Across my runs, 1 of 12 transcript-export control runs failed.
- This is not round 4's cost. A wall-clock bound fails closed.

### R4V-9 (INFO): PIN behaviours seen, not changed by round 4

- The relay scrubs each string once (no settle).
- The PIN's PAYLOAD chain: P5's bearer class takes `~`, so it eats `~curl`, and curl's `-u` value shows. The relay sends it upstream on the PIN too.
- The digest (`scrub()`) shows V in `set credentials=y\rtoken=\"<tok>;DB_PASS = V` on every version.
- A credentials head after a canonical-JSON `\n` is not read by the PIN or by stage 1. Stage 2 reads it.

### R4V-10 (INFO): my round-3 error, stated plainly

- My round-3 class K was counterfactual, so it folded K-chain positions into D1's class.
- Round 3 had this chain, and my round-3 report did not name it.
- The ambiguity in the round-4 contract comes from that definition.

## 3. The brief's items

1. **R3V-1 is closed.**
   - My R3 red file on the patched bytes: `11 passed` (PIN `11 passed`, round 3 `11 failed`; set=8d2adae291be; 17:07:58Z).
   - Round 2's red file: `16 passed` on all three (set=bcd44bc128b4).
   - e2e_n2r: `convert()` hid 5 of 5. Round 3 and round 2 LEAK 5 of 5. The one digest LEAK (curl) equals the PIN's.
   - rand_n2c: 0 on seeds 20260929 and 11 (round 3: 923).
   - sch3: 0 (round 3: 7,534). r3d4: 0 / 0.
   - New shapes of the class: R4V-1, in the txt, call and ptxt views only.
2. **DISC-4:** see R4V-1.
3. **DISC-1, DISC-2, DISC-3** (my own classifier, `probes/pos4.py` and `probes/pos4helpers.py`):
   - v4b, 4,000 texts × 6 views: REAL 0, KC 0, KD 3,489 (dig and txt), NAME 94.
   - rl2: REAL 0, KC 0.
   - `d6chk`: 0 LOST rows. `disc123`: 0 LOST against the PIN.
   - DISC-1's G1 shape, confirmed (`out/g1_shape.txt`; S = V shows; views dig, txt, call, call2, pdig, ptxt):

| version | result |
|---|---|
| PIN | `......` |
| round 4 | `......` |
| G1 | `SS....` |
| G2 | `......` |
| G1+G2 | `SS....` |

   - Corpus: see R4V-1.
4. **DISC-5:** see R4V-4.
5. **DISC-6 and DISC-7:** see R4V-3.
6. **DISC-10 and DISC-11:** see R4V-7.
7. **Linear time.**
   - `probes/census4v.py`: 110 families (the builder's 97 and 13 of mine), at 17:40Z to 17:42Z.
     - Worst stage-rule call at 64k: 0.0898 s.
     - Worst `scrub()` call: 0.2074 s.
     - Only the P0/P4 families are super-linear (10.79 s at 32k, the PIN's).
   - `probes/retime4v.py`: every flagged stage-rule and `scrub()` row grows about x2 per doubling up to 512k. Example: cookie2 on "r3 new seg eq" takes 0.4028 s at 512k.
   - D7: see R4V-5.
8. **Earlier rounds hold.**
   - F1, F15, F2: `after_v3.py` output is identical to round 3's.
   - F7: the lenient PEM rule's worst call is 0.0039 s at 64k.
   - F10: Na and Nb are KILLED.
   - F12: per-stage floor mutants are KILLED.
   - B2 and B3: LOST 0 (`out/item8.txt`).
   - D1: only D1's 7 cells per credentials head (dig, txt).
   - D2: see R4V-3. D6: 0.
   - N1: every pwd floor cell is hidden; e2e_floor hides all.
   - The value gate: `session_export.py` differs from the PIN only in `PATTERN_NAMES` (7 diff lines). The relay is unchanged.
   - Isolation (18:03:24Z):
     - absent: `336 passed, 1 xfailed in 51.66s`, with 0 source syscalls or opens and 0 token lookups;
     - fakes: `336 passed, 1 xfailed in 53.24s`, with 0 opens;
     - control: `1 passed in 0.20s`, with opens 1/1/1 and 1 lookup.
   - The Laya lock: 0 of 6,220 (v2) and 0 of 1,788 (v1, twice). Control E fires everywhere.
   - Digests: 21 of 21 are identical to the PIN's. 20 of 21 are byte-equal to the committed files (chat-2026-09-29.md grew since).
   - The manifest: only line 10 changed, to the full sha.
   - `tests/test_laya_ft.py`, the rebuild tests with `GIT_DIR` set to the main repo: `2 passed, 42 deselected in 203.08s (0:03:23)` (set=8b147318aa48).
9. **The relay.**
   - `tests/test_jev_relay.py`: `24 passed in 11.69s` (1 files set=27cdda9dfd9c).
   - The loopback round trip: see R4V-1.
10. **Mutation:** see §5.

The builder's items 3 to 6 hold:
- item 3: the 11 red items pass;
- item 4: R3V-2 measures 0;
- item 5: V12 and V14 are KILLED;
- item 6: the three R3V-4 comments now state what the code keeps.

## 4. Gates, with counts pasted from `scripts/test_summary.sh`

All runs used `masked.sh absent`, with `--basetemp` as a pytest argument.

**The floor** (13 files set=4ff48355bfb0):

| pass | start | result |
|---|---|---|
| 1 | 17:01:47Z | `917 passed, 1 xfailed in 171.34s (0:02:51)` |
| 2 | 17:04:39Z | `917 passed, 1 xfailed in 172.71s (0:02:52)` |

- An earlier attempt at 16:58:21Z read `6 failed, 911 passed, 1 xfailed`, all in `tests/test_s1_synth.py`.
- Its cause was my archive: it held 4 of the 417 skills. I added `.claude/skills` from 0ab1df7. This was a copy artifact, not a patch defect.

**Other sets** (17:08:11Z):

| files | set | result |
|---|---|---|
| 2 | e8f27bcb91e7 | `336 passed, 1 xfailed in 33.24s` |
| 3 | fe0d5d434040 | `360 passed, 1 xfailed in 45.25s` |

- The one xfail in each is the builder's strict xfail on the K-chain: "left for a ruling".

## 5. Mutation

**Driver:** `probes/mut4v.py` (sha256 39d125933f5236d6).
- It runs inside `masked.sh absent`, with 4 worker copies of the patched files.
- The control runs first in every worker. KILLED counts only a FAILED test. `-x`.
- The counts are the driver's captured pytest tail lines.

| group | run | controls | result |
|---|---|---|---|
| br: the builder's r4 group, anchors read from its `mut4_list.py` (O1-O7, N0, G1, G2, L1, L2, V12, V14, S1-S4, NEG) | 18:16:48Z to 18:19:15Z | 4 × `263 passed, 1 xfailed` | **19 of 19 KILLED**, the same killing tests as the builder's table |
| a: the stage order, first | 18:25:33Z to 18:28:10Z | 4 × `263 passed, 1 xfailed` | A1-A6, A8, A9 KILLED; **A7 SURVIVED** (R4V-2) |
| k: the keep branch | same run | same | K1 (always hides) and K2 (8 characters only) KILLED; K3 SURVIVED, equivalent |
| d: DISC-10 | same run | same | D1-D11 and D13 (12 mutants) all KILLED |
| x: DISC-11 | same run | same | X13, X13b, X13c SURVIVED, equivalent (0 of 44,000 × 6 differ); X13e KILLED |
| n: DISC-9 | 18:28:31Z to 18:30:58Z | 4 × `73 passed` | Na and Nb KILLED by `test_each_gate_pattern_name_labels_its_own_rule` |

- **Group a:**
  - A1-A5: `scrub()` with each stage-2 rule moved to the front of stage 1.
  - A6: PAYLOAD before stage 1.
  - A7 and A8: stage-1 credentials, or pwd, after PAYLOAD.
  - A9: `scrub()` with stage-1 credentials after stage 2.
- **Group d:**
  - D1-D9: each stage's rule, or the rule's PIN branch, reads nothing.
  - D10 and D11: the stage-1 or stage-2 pwd floor 8 to 12, that stage alone.
  - D13: the stage-2 credentials floor as `_PWD_FLOOR`.
- **Total of mine:** 30 mutants, 25 KILLED, 4 equivalent survivors and 1 real survivor (A7).
- **Differential:** `probes/mutdiff4.py` (sha256 fefc7f4936f902c1), 18:32:27Z to 18:37:27Z. It covers A7, K3, X13, X13b and X13c.

## 6. Reproduced, static and skipped

- **Reproduced:** everything in §2 to §5, except the items below.
- **Static only:**
  - the three R3V-4 comments (read; accurate);
  - the stage comment that discloses the K-chain (accurate, but its size claim relies on the report's corpus figure);
  - the argument that `scrub()` is immune to R4V-1 (backed by 0 in dig, pdig and call2).
- **Skipped, with reasons:**
  - the builder's x, rep, w and y groups: the builder's table reads 105 of 106 KILLED; I re-ran its r4 group and added 30 mutants of mine;
  - the 42 deselected `test_laya_ft.py` tests (the builder's NOT-done 5, too);
  - `v13chk` (not frozen);
  - the strict pass (`scrub_strict`) on K-chain shapes;
  - a stop-list fix for R4V-1;
  - the shield on sch3, r3d4, pos4 and the census;
  - non-ASCII hostile input for the round-4 clauses (the keep branch reads ASCII classes; `after_v3` is identical to round 3).
- **NOT-done:** none of the brief's items is left open. The skips are listed above.

## 7. Scratch, processes, git

- **Scratch:** `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r4/`, 4.6 MB after cleanup (18:49:10Z). It keeps:
  - `out/`: the evidence;
  - `probes/`;
  - `new/`: the patched `scripts/`, the four test files and `pyproject.toml`;
  - `pintree/`, `r3tree/`;
  - `red_*/`;
  - `var_shield/`, `var_credlate/`;
  - `vt/`.
- **To rebuild the full tree** for a floor re-run: `git archive 0ab1df7` plus `.claude/skills`, then apply the patch.
- **Other rounds' scratch:** vscrub2r2 and vscrub2r3 stay. The boundary does not let me write there.
- **Processes:** none of mine are left (pgrep).
- **Git:** no worktree made; no git write.
- **Main tree:** the uncommitted files there (`scripts/ls_req.py` and others) belong to other lanes.