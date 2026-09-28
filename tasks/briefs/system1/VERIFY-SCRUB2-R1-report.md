> **COORDINATOR NOTE (2026-09-26 12:2xZ):** the verifier returned this report as its final message: the harness refused report-file writes to it, and it did not work around the refusal. The coordinator saved the text as the report of record, extracted from the verifier's transcript, never retyped.

# VERIFY-SCRUB2-R1 report (task #321): the scrubber repair, attacked

**Gate recommendation: NOT-READY.** Three findings meet the whole blocking predicate:
- **B1:** a new quadratic class in the three rewritten value classes.
- **B2:** a Cookie value on the line after its head is now lost in canonical JSON and in pasted JSON.
- **B3:** the new Negotiate rule swallows the next header's name.

I reproduced all three through `export()` and `convert()` at the PIN plus the patch, and each has a red test that fails on the new code and passes on the PIN. The recommendation depends on nothing I did not reproduce.

These hold, all reproduced: F1, F15, F2 as the contract words them; the lenient key-block rule (F7) is linear and gives the PIN's exact output; F10; F12 (11 of 11 killed); the value gate; test isolation; the Laya lock.

Lane: sandbox Opus 5.5, no subagents. The stamp was substituted from `date -u` at 2026-09-26 12:24:31Z (bucket 12:2xZ).
- **No report file.** The harness's instructions forbid writing report `.md` files, so I did not write `tasks/briefs/system1/VERIFY-SCRUB2-R1-report.md`. This message is the whole report.
- **Scratch:** `V=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r1`, 12 MB. `S` = the scratchpad root.

## 1. Premise, re-measured (11:24Z)

| Premise line | Measured | Verdict |
|---|---|---|
| `git log cdbc1b8..HEAD -- <3 scrubber files> \| wc -l` | 0 | holds |
| Scrubber blobs | Equal at eb48880, HEAD (f1a6682) and origin (8992772): 2c09a5e2bf, 256db40106, bfcc4b88e2, 5d3abecdd2, 6f34bc74ab, 88f85d3736. These match the patch's `index` lines | holds |
| Patch | sha256 prefix `e72a85cca2a3382d`, 5 diffs | holds |
| Patch applied in `$V/new` (a `git archive HEAD` copy + `patch -p1`) | transcript_export.py 014439fb2694d273, session_export.py 0462fe2e9bdd14bc, test_transcript_export.py 00e7e9f80aedf16f, test_session_export.py c1bb29a1ec924a71, manifest 449811004a7abed8 | holds (all five equal the premise) |
| Manifest hash vs file | The manifest's new exporter hash equals the new file's full sha256 | holds |
| Free disk | 1235 MB at start, 852 to 909 MB during | the premise said 1313 MB |

No CONTRACT-INVALID.

## 2. Gates, pasted

Every run was inside `masked.sh absent` in the patched scratch copy.

```
12-file floor (set=27f27a25516b), twice:
pytest-exit: 0
pytest-summary: 841 passed in 125.44s (0:02:05)
pytest-exit: 0
pytest-summary: 841 passed in 115.86s (0:01:55)

Red run (the two changed test files on the PIN's scripts):
pytest-exit: 1
pytest-summary: 12 failed, 272 passed in 60.25s (0:01:00)

Set A's six other consumers (6 files set=d11be22044d4):
pytest-exit: 0
pytest-summary: 96 passed, 1 skipped in 26.09s   (the skip: tests/test_qwen_jev.py:37 LOUD SKIP)

This verifier's red tests ($V/probes/test_vscrub2r1_red.py, copied into the copy's tests/ for the run):
new code:            pytest-exit: 1  pytest-summary: 6 failed in 60.11s (0:01:00)
PIN exporter swapped in: pytest-exit: 0  pytest-summary: 6 passed in 0.21s
```

- **Floor venue note:** the first floor run gave 1 failure at `tests/test_jev_context.py:719`. The copy had no `CLAUDE.md` (a venue artifact). I added it from `git archive HEAD`; the two runs above are after that.
- **Red run:** every one of the 12 reds fails for the reason the builder states. The timing child stalled at `60,000 dashes|scrub|33.1313`.
- **Static checks:** pyflakes gives rc 0 on the four code files. `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` gives 0 for all five patched files and the builder's report.

## 3. Findings (no severity filter)

Evidence: R = reproduced here through the named path. S = read from source. U = not verified.

### V1 — BLOCKER (B1): new super-linear class in the rewritten value classes

**What:** the pair alternative `\\\\(?!\\*[\"'])` appears in `_VE`, `_CV` and `_CL` (`scripts/transcript_export.py:76-78` in the new file). At every backslash pair, its lookahead re-scans the rest of the backslash run. It sits inside `_VE+`, `_CL+`, `_CL*` and the Cookie no-value loop, so a long backslash run after a Cookie, pwd or credentials head costs quadratic time.

**Measured (R):**
- Each rule alone at 64,000 backslashes: Cookie 29.32 s, pwd 14.49 s, credentials 14.64 s. The cost grows about 4 times per doubling. The PIN takes 0.003 s at 16,000.
- End to end, a Cookie head plus 32,000 backslashes: `export()` 7.92 s, `convert()` 15.77 s. The PIN takes 0.02 s and 0.16 s.
- pwd and credentials at 16,000: about 1 s in `export()` and 2 s in `convert()`, against 0.00 s and 0.02 s on the PIN.
- **Cause, confirmed:** mutant M17 drops the lookahead, and the pwd rule then takes 0.0059 s at 64,000.

**Blocking predicate:**
1. **Contract mapping:** AF-AP-152, which the coordinator ruled blocking for this file ("every rule in it runs in linear time"), and SCRUB2-R1 item 2 ("Check every rule in the file for the same class"). The builder's section 3 says "every secret rule linear, no flag". That is false.
2. **Canonical path:** `export()` and `convert()`.
3. **Material effect:** one line stalls the push-time digest export and the session export. Exposure today is 0: one scan (counts only) found no run of 32 or more backslashes in 1,352,316,327 bytes of transcripts. F7 had the same zero exposure and still blocked.
4. **Discriminator:** red test `test_b1_the_named_rules_run_in_linear_time_on_a_backslash_run`. On the new code it fails with "a scrub stalled ... Cookie head|scrub|26.1667"; on the PIN it passes.
5. **Ownership:** the three classes are this round's code.

**Why the builder's census missed it:** its "pwd backslashes" family starts the value with a backslash. The `(?![/~.$\\])` start guard rejects that before the value loop runs, and there was no Cookie backslash family (tactic 3f).

**Fix:** drop or atomize the lookahead in all three classes. Add backslash texts to `LINEAR_CHILD`. Correct the Cookie rule's comment "it runs in linear time".

**Reproduce:**
- `cd $V/probes && python3 bs_timing.py "pwd+bs,cred+bs,cookie+bs" 8000,16000,32000,64000 scrub new,pin 60`
- `$S/vscrub1/masked.sh absent $V/probes -- python3 $V/probes/e2e_bs.py 32000 cookie new,pin all`

### V2 — BLOCKER (B2): a Cookie value on the line after its head is lost in JSON

**What:** after the colon, the Cookie head's `\s*` (line 143) crosses a real line end but not an escaped one (`\n`, `\r\n`), and `_CL` stops at the escape. So `Cookie:` + escaped newline + `session=<v>` finds no value. The PIN's lookahead read across the escape and hid the value. The decoded reading hides it in both the PIN and the new code. So under item 1's own model this is the cookie's value, not an over-redaction.

**Measured (R):**
- `lost_shapes.py`: the raw view is LOST for "cookie yaml next line", its CRLF form and "colon then newline"; the decoded view hid all three.
- `e2e_yaml.py` through `convert()`: new gives "Write yaml LEAK, Bash heredoc Set-Cookie LEAK"; the PIN hid both.
- A pasted JSON line through `scrub()` (the digest): new LEAK, PIN hid.

**Blocking predicate:**
1. **Contract mapping:** item 5 ("No redaction the PIN makes may be lost, except the over-redactions F15 names").
2. **Canonical path:** `convert()` with Write and Bash inputs, and `export()` with pasted JSON.
3. **Material effect:** a cookie session value reaches the session export and the digest.
4. **Discriminator:** red test `test_b2_...`, 3 cases.
5. **Ownership:** the Cookie head and `_COOKIE_X`.

**Why the differential missed it:** the builder's differential draws no backslash.

**Fix:** after the colon, accept an escaped `\n`, `\r` or `\t` as whitespace, for example `(?:\s|\\[nrt])*`. Let `_COOKIE_X` also stop at a colon followed by `\\[nr]`.

**Reproduce:** `$S/vscrub1/masked.sh absent $V/probes -- python3 $V/probes/e2e_yaml.py`

### V3 — BLOCKER (B3): the Negotiate rule swallows the next header's name

**What:** the new Negotiate rule (lines 127-128) takes as its token the next word after `(?i:negotiate)\s+`, and `\s+` crosses a newline. So in `Authorization: Negotiate\nAuthorization: Basic <b64>`, the token is the second header's name. The scheme rule then never sees that header.

**Measured (R):** the Basic value and the Token value leak in `scrub`, `scrub_payload`, the digest and `convert()`'s text events. The PIN hid both: its credential rule took the 9-letter word `Negotiate`. The control (Token alone) is hidden in all four paths. The random differential found 22 such losses.

This is AF-AP-157's class. The rule's comment claims AF-AP-157 coverage, but the token stops only before a Bearer match and a link.

**Blocking predicate:**
1. **Contract mapping:** item 5, and AF-AP-157 (task #198's invariant for this file).
2. **Canonical path:** all four paths.
3. **Material effect:** a Basic credential or token reaches the committed digest and the session export.
4. **Discriminator:** red test `test_b3_...`, 2 cases.
5. **Ownership:** the new rule, added for F2.

**Materiality note:** the shape is uncommon, and the same shape already leaks on the PIN for 7 other schemes (V11). Only Negotiate regressed. This is the weakest of the three blockers.

**Fix:** `(?i:negotiate)[ \t]+`, or stop the token before `authorization` or `_HEAD`.

**Reproduce:** `$S/vscrub1/masked.sh absent $V/probes -- python3 $V/probes/e2e_neg.py`

### V4 — FOLLOW-UP, needs your ruling: literal escapes in decoded text (R)

**What:** in the digest and in `convert()`'s decoded events, a literal backslash-n, -r, -t or -f (two characters) now reads as an escape. The effects:
- A pwd or credentials value is cut there, and the part after it shows. A head under 8 characters shows whole.
- A Cookie line ends at a literal `\n` or `\r`. So `Cookie: path=C:\new\x; sid=<v>` shows a clean `sid` value that the PIN hid.

**Measured:** `lost_shapes` shows 10 decoded LOST cells. `rand_lost2` shows 93 of 10,595 fake tokens. The builder's self-attack 1 names only the short-head case.

**Why not a blocker:** the contract does not say which view item 1 bullet 2 governs.
- Under a literal reading, this is a lost PIN redaction outside F15's exception, because F15 said the decoded digests are unaffected.
- Under the builder's model, a literal `\n` in decoded text is pasted JSON, and the behaviour is consistent.

### V5 — FOLLOW-UP: surviving mutants are test gaps (R)

Each survivor is non-equivalent: a live differential shows it changes output.

| Mutant | What it changes | Texts that differ (of 20,000) |
|---|---|---|
| M2 | `_VE` takes an escaped CR | 230 |
| M3 | `_CV` takes an escaped tab | 250 |
| M17 | `_VE` pair without its lookahead | 620 |
| M20 | no `\b` or `\f` escape before pwd | 126 |
| M21 | Negotiate floor 8 to 12 | 11 |
| M22 | Negotiate token without `+/=` | 2 |

M22 matters because a real SPNEGO token is base64, and the committed test's fakes are hex. Fix: one assertion each.

### V6 — INFO: W6, W11 and W28 are equivalent (R)

- Each differs from the new code in 0 of 20,000 texts, through scrub, scrub_payload and canonical JSON. For W11 the logic agrees too: the added alternative implies the first.
- M5 (bare quotes only in the Negotiate rule) also differs in 0 of 20,000. The scheme rule's `negotiate` alternative backs it up. So the "dead code" W6 names is redundant rather than dead: removing both would leak.

### V7 — INFO: F1, F15 and F2 reproduced with VERIFY-SCRUB2's own scripts (R)

I ran `escape_named.py`, `escape_nonascii.py`, `cred_convert.py` and `negotiate.py` twice: BEFORE as they are, and AFTER with `$V/probes/after_v.py`, which swaps in the patched root.
- **BEFORE:** they print the LEAK cells the builder quotes.
- **AFTER:** 30 of 30 and 12 of 12 cells hid/hid, no ordinary word lost, and Negotiate prints "none".

### V8 — INFO: the lenient key-block rule and the Cookie rule are output-identical to the PIN's on plain text (R)

- I ran two 30,000-text differentials with wider alphabets than the builder's. The key-block alphabet added 5-dash heads, lower case, a lone CR, SECRET and BLOCK. The Cookie alphabet added a lone CR, `\v`, `\f`, U+2028, NEL, Cookie2 and upper case. Both show 0 differences.
- D1's shrunk cases give equal output.
- Both rules are linear on 12 hostile families each: worst 0.0024 s and 0.0221 s at 64,000 characters.

### V9 — INFO: the builder's D7 numbers confirmed (R)

| Rule | Input | Time | Growth | PIN |
|---|---|---|---|---|
| P00 | 32,000 characters of `a.` labels | 5.93 s | about 4 times per doubling | 1.57 s at 16,000 |
| P04 | 64,000 characters (three families) | 2.51 s, 2.62 s, 1.77 s | about 4 times per doubling | – |
| `_ASSIGN_LINE` | 16,000 spaces | 5.75 s; over 20 s at 32,000 | about 4 times per doubling | 5.67 s at 16,000 |
| P06 (curl-user) | 64,000 characters of `curl ` | 0.52 s | linear, but costly | – |

The three quadratic rules predate SCRUB2 and stay FOLLOW-UP (task #333), as the builder says.

### V10 — INFO: AF-AP-152's screen misses V1 too (R)

`scripts/ap_screen.py` fires on neither the PIN exporter nor the new one. It also misses V1's shape: a lookahead that re-scans a run inside a quantified alternation. The screen is outside this boundary.

### V11 — FOLLOW-UP, pre-existing (R)

`Authorization: <scheme>` with no token, a newline, then another Authorization header: the second header's credential leaks on both the PIN and the new code for Token, Basic, Digest, NTLM, Key, SSWS and Bearer (AF-AP-157).

### V12 — FOLLOW-UP, pre-existing (R)

In canonical JSON, a value on the line after `pwd:`, `"credentials":` or `Authorization:` leaks on both the PIN and the new code. The decoded reading hides it. This is item 1's model not yet applied to the heads.

### V13 — INFO: cost (R synthetic; the corpus not re-measured)

The builder's D14 classes reproduce. Two classes it does not name:
- The decoded view now hides `my_cookie: jar=...`, because the Cookie rule's left anchor (`_KEY_L`, not `\b`) now accepts `_`.
- Raw line-start texts are now hidden where the decoded view already hid them.

The builder's decoded and digest cells show 0 of the first class in the corpus.

### V14 to V16 — INFO: test isolation, the Laya lock and the value gate hold (R)

- **V14, test isolation:** I ran the two changed test files under strace, every process included.
  - `masked.sh absent`: 284 passed, 0 syscalls on any source path, 0 token lookups.
  - `masked.sh fakes`: 284 passed; the copy's `.pc-bridge.env` shows 1 syscall and 0 opens.
  - Control (a scratch-only test that opens the planted fakes): 1 open each and 1 lookup counted, so the instrument sees opens.
- **V15, Laya lock:**
  - `collect_v2` at 434b727dfd: 0 of 6,220 items differ. Controls: N-pwd changes 16 items (the new scrub equals the PIN on all 16), and E changes all 6,220.
  - `collect` at eb256f49c0 and at 0b342c7a29: 0 of 1,788 each.
  - I rebuilt v2 with the Laya venv (git reads only). `dataset.jsonl` sha256 is 99070c33..., equal to the record's. The rebuilt manifest is byte-identical to the patched record.
- **V16, value gate:** the diff touches no line of the gate. `scripts/known_values_check.py` is unchanged (blob bfcc4b88e2), and its tests are in the floor.

### V17 to V19 — INFO: red run, mutation, and robustness (R)

- **V17, red run:** matches the builder's; counts in section 2.
- **V18, mutation:** 18 of the builder's mutants are killed by a FAILED test. That includes all eleven F12 survivors: W1-W5, W7, W8, W10, W13-W15. Of my 14 mutants, one per clause the builder's set does not cover, 7 are killed and 7 survive (M5 equivalent; the other six are V5).
- **V19, robustness:**
  - 0 of 20,000 texts fail to settle in 4 passes (both rule sets, both views).
  - 0 exceptions in 50,000 fuzz texts (lone surrogates, NUL, partial `\u` escapes).
  - Degenerate inputs give the PIN's outputs.

### V20 — UNVERIFIED: the measurement rows and the 19-of-19 digest identity

The harness's classifier refused a second read of the transcripts (PII data handling), and I did not work around it. As a proxy, I re-scrubbed the 19 committed digests at HEAD (3,693,721 characters) with both rule sets: they differ in 0 files for both scrub and scrub_payload.

### V21 — INFO: false or stale context (S)

- The Cookie rule's comment "it runs in linear time" is false (V1).
- The Negotiate rule's comment implies AF-AP-157 coverage the rule lacks (V3).
- The builder's section 3 and its self-attack 3 are falsified by V1.

### V22 — INFO: a fix is feasible inside the boundary (R, scratch only)

`$V/candidate_te.py` makes six one-line edits: drop the three pair lookaheads, let the Cookie head and `_COOKIE_X` read escaped line breaks, and use `[ \t]+` after `negotiate`. With it, the two changed test files plus the 6 red tests give `290 passed in 20.68s`. I did not measure its item-6 rows.

### V23 — INFO: my process slips (none touched the shared tree)

- I ran a stray `git init` inside my scratch copy and removed it at once.
- The BEFORE runs of the earlier verifier's scripts made and deleted their own work dirs under `vscrub2/`. Nothing is left there.
- A gitignored `scripts/__pycache__/transcript_export.cpython-311.pyc` in the shared tree has mtime 11:26:10Z, during this lane. It is most likely a harness hook's import. `git status` shows 0 lines.

## 4. Contract status

| Item | Status |
|---|---|
| 1 | Contexts, F15 and the cost report hold. But V2 is a loss from the same rewrite, and V4 needs your ruling. |
| 2 | The lenient rule is linear, and the timing test's texts and 2 s bound hold. "Check every rule" fails (V1). |
| 3 | F10 and F12 hold. F2 holds, except V3. |
| 4 | Untouched. |
| 5 | Value gate, test isolation and the Laya lock hold. The measurement rows are unverified (V20). "No lost PIN redaction" fails (V2, V3). |

## 5. NOT done

- The measurement rows and the digest identity from the transcripts (classifier refusal, V20).
- The whole of `tests/test_laya_ft.py`. My copy is not a git repo, which the record tests' `--repo` default needs. The direct rebuild in V15 covers their byte check.
- The full suite, and GitNexus `detect-changes` (the patch is not in the tree).
- The PC: no bridge, by rule.

## 6. DISCREPANCIES

- The brief asks for a report file; the harness forbids one, so this message is the report.
- Free disk differs from the premise (section 1).
- The builder's claim that "every secret rule [is] linear" is false (V1).
- The builder's corpus shows no secret among its LOST regions, but V2 and V3 are loss classes that the corpus and its generators could not draw.
- My first class-N run reused one fake across two cases, which spoiled one digest cell. The V3 table is from a clean re-run with distinct fakes.

## 7. Files

All are in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub2r1/`:
- `probes/test_vscrub2r1_red.py` — the 6 red tests, ready for a repair brief.
- `probes/` — every probe named above.
- `results.txt` — the raw numbers.
- `candidate_te.py` — the V22 feasibility copy.
- `new/` — the patched copy: scripts, tests and the Laya manifests only.
- `pin/` and `pinfiles/` — the PIN's files.
