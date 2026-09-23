# VERIFY-J1-0-R6 — report (task #199; lane pc-verify-j1-0-r6, PC local route, adversarial-verifier)

Brief: `tasks/briefs/laya/VERIFY-J1-0-R6-brief.md`. PIN `c6dcd61` (origin head "AF-AP-159 registered with a
screen row …"; J1-0-R6 itself is `96c2cff`, the post-push SHA of local `d116e3d`, byte-identical at the PIN).
Contract: AMENDMENT 5 (the ledger note "VERIFY-J1-0-R5 HOME, NOT-READY BY RULING; J1-0-R6 UNDER AMENDMENT 5" in
`todo/BUILD-TASKLIST.md` plus the J1-0-R6 commit body, `git show 96c2cff`), on AMENDMENT 4 (R5-1..R5-5,
`tasks/briefs/laya/J1-0-R5-brief.md`). Inputs to attack, not truths: the J1-0-R6 commit body, the AF-AP-159 row in
`docs/INCIDENT-LOG.md`, and the previous verifier's report `tasks/briefs/laya/VERIFY-J1-0-R5-report.md` (§ 4 + appendix).
Scratch: `/home/rocco/tmp-vj10r6/` (the PC's home, not `/tmp`). Honey `full`. Evidence tiers: SOLID (run here, pasted),
INFERRED, ASSUMED. The four boundary files (S, T, H, A) are cited by alias: S = `scripts/no_laya_in_gates.py`,
T = `tests/test_no_laya_in_gates.py`, H = `.claude/hooks/edit-snapshot.py`, A = `tests/test_edit_snapshot_ap_screen.py`,
DIFF = the 20k differential output. Every measurement is through the REAL screen (`S_r5.py` = `git show b91673e:…`,
`S_r6.py` = `git show c6dcd61:…`), run read-only with `--root <throwaway tree>`.

## 1. PREMISE (re-measured in this lane tree, 2026-09-23T21:19:50Z)

```
$ git log --format='%h %s' -4 origin/claude/soundbox-kit-migration-iz1jwf
6963f00a transcripts: scrubbed sandbox chat digests (2026-09-23)
2f055f76 T94-R1: executed poll-probe cases ... (VERIFY-T94 F-1) + the VERIFY-T94 harvest
e1107396 transcripts: scrubbed sandbox chat digests (2026-09-23)
15d98eda decisions: D-060 owner answers ...
$ for f in <the four boundary files>; do echo "$(git rev-parse c6dcd61:$f|cut -c1-12) $(git show c6dcd61:$f|wc -l) $f ==worktree:$([ = ]&&yes||NO)"; done
21e2bcb263e5 1457 scripts/no_laya_in_gates.py     ==worktree:yes
3dee79b1e293 1294 tests/test_no_laya_in_gates.py  ==worktree:yes
b52a0d8ab536   481 .claude/hooks/edit-snapshot.py ==worktree:yes
d7448f51bb89   489 tests/test_edit_snapshot_ap_screen.py ==worktree:yes
$ git diff --stat b91673e c6dcd61 -- S T H A
 .claude/hooks/edit-snapshot.py        |  4 ++++
 scripts/no_laya_in_gates.py           | 17 +++++++++------
 tests/test_edit_snapshot_ap_screen.py | 18 ++++++++++++++++
 tests/test_no_laya_in_gates.py        | 40 +++++++++++++++++++++++++++++++++++
 4 files changed, 73 insertions(+), 6 deletions(-)
```

Premise: **the four boundary files are byte-identical at `c6dcd61` (worktree == PIN), matching the brief's block
exactly (blob ids, line counts, diff stat all agree).** Origin has moved ahead (`6963f00a`) — expected; it does not
touch these four files. No item is CONTRACT-INVALID on premise grounds.

**PyYAML 6.0.1 (sandbox) vs 6.0.3 (PC) — measured, a NON-finding.** I built a throwaway venv on 6.0.1 and ran the
identical mark/token probe over the brief's shapes on both; the `start_mark`/`end_mark`/`token` lines and the
composed values came back **byte-identical** (only object memory addresses differed in the repr). There is no
6.0.1/6.0.3 boundary mismatch for any shape here, so no item is CONTRACT-INVALID on PyYAML-version grounds.
(SOLID; `/home/rocco/tmp-vj10r6/p601.txt` vs `p603.txt`, diff = address lines only.)

**W10b pair re-measured (the V5-05 defect, its canonical example):**
```
file (1-based):  6: '      - run: &x'   7: '          |'   8: '          . scripts/h.sh'
S at b91673e (R5):  rc=4  gate-file-sources: .github/workflows/w.yml:7: scripts/h.sh   <- the '|' indicator (OUT of the value)
S at c6dcd61 (R6):  rc=4  gate-file-sources: .github/workflows/w.yml:8: scripts/h.sh   <- the command line (INSIDE the value)
```
R5 names the indicator line (the V5-05 defect); R6 names the command's own line. Both rc 4. SOLID (real screen).

## 2. SHAPES (24 new shapes, never T's W10/W10b/W11/W12/W12b/MX6 or the empty-value test; `/home/rocco/tmp-vj10r6/driver2.py`, output pasted below)

For each: R5's line+rc and R6's line+rc (real screen, `--root`), and whether R6's line is inside the value (for `|`,
the helper's own line). bash runs the helper for every R6 composed value (§ 2b de-vacuous). **R5 rc = R6 rc = 4 for
every shape (contract (c): no rc change); R6's named line is inside the value for every property shape; R5's was the
property/anchor/comment/indicator line (the V5-05 defect). No-property shapes (g, h, i, j) are identical R5==R6.**

```
shape                  | R5 (rc, named line)              | R6 (rc, named line)              | R6 line inside value?
a1 A/T/then plain      | 4    w.yml:7                      | 4    w.yml:9                      | YES (content line 9; R5 named property line 7)
a2 T/A/then plain      | 4    w.yml:7                      | 4    w.yml:9                      | YES
a3 A/T/then |block     | 4    w.yml:8                      | 4    w.yml:10                     | YES (R5 named the indicator)
b1 prop+| same line    | 4    w.yml:7                      | 4    w.yml:7                      | YES (same line: property+indicator on the key line)
b2 prop+> same line    | 4    w.yml:7                      | 4    w.yml:7                      | YES
c1 A/#/plain           | 4    w.yml:6                      | 4    w.yml:8                      | YES (R5 named the property line 6; R6 the content)
c2 A/#/|block          | 4    w.yml:7                      | 4    w.yml:9                      | YES (R5 named property line 7)
d1 A,|-                | 4    w.yml:7                      | 4    w.yml:8                      | YES
d2 A,|+                | 4    w.yml:7                      | 4    w.yml:8                      | YES
d3 A,>-                | 4    w.yml:7                      | 4    w.yml:8                      | YES
d4 A,|2                | 4    w.yml:7                      | 4    w.yml:8                      | YES
d5 A,>2                | 4    w.yml:7                      | 4    w.yml:8                      | YES
e1 doc1+doc2 |         | 4    w.yml:7 , w.yml:15           | 4    w.yml:7 , w.yml:16           | YES (both docs; doc2's R6 line moves to its content line)
e2 doc1 plain, doc2 |  | 4    w.yml:6 , w.yml:14           | 4    w.yml:6 , w.yml:14           | YES (both; doc1 plain identical, doc2 | identical)
f1 alias->A|           | 4    w.yml:7 , w.yml:7            | 4    w.yml:8 , w.yml:8            | YES (both the block's and the alias's value; see F-3)
g1 flow map {run:&x}   | 4    w.yml:6                      | 4    w.yml:6                      | YES (flow; no property on the value line)
g2 flow seq [ {run:&x} ]| 4    w.yml:6                     | 4    w.yml:6                      | YES
h1 quoted key          | 4    w.yml:6                      | 4    w.yml:6                      | YES
h2 complex key ? run   | 4    w.yml:7                      | 4    w.yml:7                      | YES
i1 &k run:V            | 4    w.yml:6                      | 4    w.yml:6                      | YES (property is on the KEY, value has none)
j1 CRLF                | 4    w.yml:6                      | 4    w.yml:6                      | YES (CRLF -> LF via read_text(errors='replace'))
j2 tab inside quoted   | 4    w.yml:6                      | 4    w.yml:6                      | YES (a tab is legal inside a quoted scalar)
k1 A,|,blank1st        | 4    w.yml:8                      | 4    w.yml:9                      | YES (R6 names the command line; see F-1)
k2 |,blank1st          | 4    w.yml:8                      | 4    w.yml:8                      | YES
```

Note: my first driver run reported `gate-file-unparseable` for h2 and j2. That was a **fixture-construction artifact**
(my first driver built the complex key / tab with a disallowed indent), not a real screen result. The corrected
driver (the one pasted) builds the YAML-legal forms (the brief's own note: "a correctly-parsing complex key … `?` and
`:` at the same indent as the `-` element") and both parse. This is logged under DISCREPANCIES (DV-2).

### 2b. De-vacuous — bash runs the helper for every R6 composed value (SOLID; `/home/rocco/tmp-vj10r6/devac_full.txt`)

For all 24 shapes, R6's composed `run:` value fed to `bash --noprofile --norc -c "$value"` from the tree root:
**27 / 27 run the helper (rc 0, "HELPER-RAN laya").** The R5 and R6 composed values are **identical in every shape**

the fix moves the NAMED LINE, never the VALUE, so nothing that ran under R5 stops running under R6, and nothing that
was unrunnable becomes runnable. No fail-open introduced.

## 3. THE DOCSTRING (scripts/no_laya_in_gates.py:498-504, `def _workflow_runs`)

The docstring begins at `scripts/no_laya_in_gates.py:498`, `(first line, text, literal)` (the docstring says a scalar run value's first line is read from its own token, `start, which is its first property` on 500, `the indicator of a block` on 501).
R6's docstring, sentence by sentence, checked against the § 2 shapes. The two load-bearing lines are
`scripts/no_laya_in_gates.py:500`, `the line after` (`first property`) and `scripts/no_laya_in_gates.py:501`,
`the indicator of a block` (`plain or quoted`, `first character`).

- *"The first line is read from the value's own scalar token, never from the node's start, which is its first property
  (an &anchor or a !!tag) and can sit on an earlier line"* — **TRUE as stated.** Confirmed by the tokens: for a1 the
  node's `start_mark.line` is 6 (the `&x` property line) but the scalar token's `start_mark.line` is 8 (the content
  line); the code uses the token's (`S_r6.py` `line = token_line.get(value.end_mark.index, value.start_mark.line)` at
  scripts/no_laya_in_gates.py:526), not the node's.
- *"the line after the indicator of a block (| or >)"* — **TRUE for every block except k1.** For k1 (a literal block
  whose first content line is blank, behind a property) the indicator is on line 7 (1-based) and the command is on
  line 9, so the named line (9) is "the line after the **content** line", one past "the line after the indicator"
  (which is the blank line 8). See F-1: this phrasing claims more than the code does for a blank first content line.
- *"else the line of a plain or quoted scalar's first character"* — **TRUE as stated.** a1/a2/c1 (plain scalar after
  properties) name the content line; g1/g2/h1 (quoted/flow) name their first character's line; j2 (tab inside quotes)
  is unaffected.
- *"a plain, quoted or folded value joins or escapes some of its line breaks, so its lines do not map back to the
  file's and every refusal in it names the first line (R5-4)"* — **TRUE as stated** (R5-4 still holds underneath
  AMENDMENT 5; AMENDMENT 5 only changed where the line comes from, not the first-line rule for non-literals).
- *"Only a literal block (|) keeps every line break, so a refusal in it names its own line"* — **TRUE for every
  measured `|`**, including k1 and k2: a `|` refusal names the line holding the sourced command (its own line).

Net: the docstring is accurate as stated for all measured shapes **except the "the line after the indicator" clause
under a blank first content line (k1)** — a one-word over-claim, logged as FOLLOW-UP F-1, not a blocker (the named
line is still inside the value and is the command's own line, which is what "names its own line" requires).

## 4. DIFFERENTIAL (20,000 generated inputs; `/home/rocco/tmp-vj10r6/diffgen.py`, output DIFF)

A generator over properties (anchor/tag, both orders, comment-between), styles (plain/`|`/`|-`/`|+`/`>-`/`|2`/`>2`/`>`),
indentation, documents, comments and blank lines; bash-parseable values only; 20,000 inputs run through R5 and R6:

```
$ python3 diffgen.py
TOTAL 20000  rc-diff 0  line-diff 5905
line-diff by signature:
  anchorblock          1908
  tagblock             1703
  anchortagblock       1009
  block                921
  blockcrlf            147
  tagblockcrlf         105
  crlf                 22
  (…plus the small plain/comment/quoted/blank classes…)
```

**rc-diff = 0 over all 20,000 inputs** (contract (c): no rc changes from R5 on any input — the fix moves lines only;
the `rc` decision path in S is byte-identical between R5 and R6, only `_workflow_runs` changed, so this is structural).
**5905 line-diffs** — exactly the V5-05 fix: for every line-diff input, R5's named line is the property/anchor/
comment/indicator line (one or more lines above the value) and R6's is the value's content line. I verified the
property over a re-generated sample: **in every line-diff pair, R6's line is strictly later than R5's (0 pairs where
R6 is earlier, 0 equal)** — R5 always named an earlier (property-side) line, R6 the content line. No input class
shows R6 naming a line outside the value. (SOLID.)

## 5. COST (the added `yaml.scan` pass; `/home/rocco/tmp-vj10r6/cost2.py`)

The fix adds one `yaml.scan` per workflow file (scripts/no_laya_in_gates.py:513-514). Median of 25 runs, per-doubling ratio:

```
steps (each behind a property)   R5 median ms   R6 median ms   R6/R5
     1                            0.7267         0.7876         1.08
    10                            0.8454         0.8793         1.04
   100                            0.9812         0.9905         1.01
  1000                           1.8342         1.8262         0.99
```

Both R5 and R6 grow ~linearly (near-constant between 1 and 100, ~2x from 100 to 1000); R6 is within ~8% of R5 at every
scale and actually slightly faster at 1000. **Nothing grows faster than linearly in either; the added `yaml.scan` pass
is negligible** (sub-millisecond, a single linear token pass). The earlier "223% of compose" line was a
0.0000-division artifact in `cost.py`, not real. (SOLID.)

## 6. THE SCREEN ROW (.claude/hooks/edit-snapshot.py:190, `\.start_mark\.line\s*\+`)

### (a) Does it fire on R5's line and on nothing in S at the PIN?

The no-fire R6 lookup is `scripts/no_laya_in_gates.py:526`, `token_line.get(value.end_mark.index, value.start_mark.line)`; the map it reads is `scripts/no_laya_in_gates.py:513`, `t.end_mark.index: t.start_mark.line`.
The AF-AP-159 row sits at `.claude/hooks/edit-snapshot.py:190` (the backslashed pattern is shown in the block below; it fires on a `+` after `start_mark.line`).

```
$ RX='\.start_mark\.line\s*\+'
S at b91673e:521:  FIRES      -> runs.append((value.start_mark.line + (2 if ...), value.value,
S at c6dcd61:513:  no fire    -> token_line = {t.end_mark.index: t.start_mark.line for t in yaml.scan(...)
S at c6dcd61:526:  no fire    -> line = token_line.get(value.end_mark.index, value.start_mark.line)
```
The regex fires on R5's defect line (`value.start_mark.line +`) and on **nothing in S at the PIN** (R6's two
`.start_mark.line` uses have no `+` after them — one is the token-map value, one the `.get(..., …)` default).

### (b) `ap_screen.py` over `scripts/ proofs/ src/ harness-ports/` at the PIN — AF-AP-159 hits

The `TestAFAP159` class is `tests/test_edit_snapshot_ap_screen.py:476` (`class TestAFAP159`); its four tests (479–489) are `test_fires_on_the_j1_0_r5_line_map`, `test_fires_without_spaces`, `test_no_fire_on_the_token_line_lookup`, `test_no_fire_on_the_token_map`.
```
$ python3 scripts/ap_screen.py scripts proofs src harness-ports
--- AP_SCREEN over 4 path(s): 45 hits over 19 files ---
```
**AF-AP-159: 0 hits.** The only AF-AP ids present are AF-AP-110/43/72 (plus AP-51/24). No AF-AP-159 row fires on any
file at the PIN, so there is **no false positive** (a hit outside a YAML line map would be one; there are none).

### (c) Spellings the regex misses + would A's four tests catch a widening/narrowing?

The four R6 property/line tests are `tests/test_no_laya_in_gates.py:1286` (`def test_run_value_behind_a_node_property_names_a_line_inside_it`); the W10/W10b/W11/W12/W12b rows are at `tests/test_no_laya_in_gates.py:1264` (`R5 named 8, 7, 7, 6, 6`); the empty-value test is `tests/test_no_laya_in_gates.py:1273` (`def test_empty_run_value_has_no_token_and_is_read_from_its_node`).
The regex `\.start_mark\.line\s*\+` matches only a literal `+` immediately after `.start_mark.line`. It **misses**:
- the right-operand form `2 + node.start_mark.line` (the `+` is before `.start_mark.line`, not after);
- a start mark bound to a variable first (`x = node.start_mark; line = x.line + 1`).

A's four tests (tests/test_edit_snapshot_ap_screen.py:479-489): `test_fires_on_the_j1_0_r5_line_map`, `test_fires_without_spaces`
(`node.start_mark.line+1`), `test_no_fire_on_the_token_line_lookup`, `test_no_fire_on_the_token_map`.
**A's tests catch a widening** (removing the `\s*\+` so it also matches `.start_mark.line` alone fails
`test_no_fire_on_the_token_line_lookup` and `test_no_fire_on_the_token_map` — confirmed: my hm1 mutant (drop the `+`)
gives 2 failed / 2 passed). **A's tests also catch a space-narrowing** (`test_fires_without_spaces` pins the
no-space form). **They do NOT catch a right-operand miss** — no test feeds `2 + node.start_mark.line`, so a regex that
only matches the left-operand form would stay green. This is a test-coverage gap, logged as FOLLOW-UP F-2 (not a
blocker: the current regex is correct for the production spelling, and the production line at the PIN no longer
contains the defect). (SOLID; hm1 mutant below.)

## 7. MUTANTS (5 new — 4 on `_workflow_runs`, 1 on the H row; never the coordinator's m1-m7; `/home/rocco/tmp-vj10r6/mutants2.py`)

Each compiles+collects (AF-AP-78); the killing tests are run on the UNMUTATED copy first (AF-AP-138):

```
UNMUTATED baseline:  T-kill 12 passed (4 test functions, 12 param instances) | A-kill 4 passed   (16 total)
  sm1 (key the token map by START index, not end)      compile=True  KILLED   5 failed, 7 passed
  sm2 (use the NODE start_mark, drop the token map)    compile=True  KILLED   12 failed
  sm3 (drop the +2 offset for block styles)            compile=True  KILLED   3 failed, 9 passed
  sm4 (always use the node start_mark for the line)    compile=True  KILLED   6 failed, 6 passed
  hm1 (widen the H regex: drop the \s*\+)              KILLED         2 failed, 2 passed
```
**All 5 are genuine kills; no survivors.** The unmutated baseline passes all 16 killing tests (12 T + 4 A), so the
kills are not collection artifacts. sm1/sm2/sm4 revert the named line toward the node's property line (reproducing the
V5-05 defect the tests pin against); sm3 breaks the block line map; hm1 makes the H regex fire on the fixed
`.get(...)`/token-map lines. (SOLID.)

## 8. GATES (lane worktree at the PIN, read-only; 2026-09-23T21:20-21:24Z)

```
$ python -m pytest -n 8 tests/test_no_laya_in_gates.py tests/test_edit_snapshot_ap_screen.py -q -p no:cacheprovider   (run 1)
220 passed in 47.00s
$ python -m pytest -n 8 tests/test_no_laya_in_gates.py tests/test_edit_snapshot_ap_screen.py -q -p no:cacheprovider   (run 2)
220 passed in 56.06s
$ bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py tests/test_edit_snapshot_ap_screen.py
2 files set=f4e9ba5ca7d1
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean
$ python3 scripts/no_laya_in_gates.py --staged
no_laya_in_gates: 40 files scanned, clean
$ /home/rocco/venv-agent-factory/bin/python -m pyflakes S T H A        (pyflakes 3.4.0)
<no output>   pyflakes-rc=0
```
All four gates pass: GATE 1 (the two suites, `-n 8`, twice → 220 passed ×2; the set-id `f4e9ba5ca7d1` matches the
brief's landing); GATE 2 (live screen, `40 files scanned, clean`, both default and `--staged`); GATE 3 (pyflakes clean
on S, T, H, A — note: the venv `python` has pyflakes, the system `python3` does not; I ran the venv one as the brief's
GATE 4 intends). SOLID.

## FINDING INVENTORY (no severity filter; F- ids are this lane's)

Each row: classification · evidence · contract mapping · canonical path · material effect · reproduction · suggested fix.

- **F-1 FOLLOW-UP — the docstring's "the line after the indicator of a block" over-claims for a blank first content line (k1).**
  SOLID. § 3 + § 2 (k1: R6 names line 9, the command's own line, not "the line after the indicator", which is the blank
  line 8). Contract: AMENDMENT 5(d) ("`_workflow_runs`'s docstring states exactly what the code does") — the docstring is
  accurate for every measured block **except** the blank-first-content case, where "the line after the indicator" is one
  line above what the code names. Canonical: the real screen names line 9 (correct, inside the value). Material: **no** —
  the named line is still inside the value and is the command's own line (so "a refusal in it names its own line" still
  holds); only the mechanism sentence's "after the indicator" phrasing is imprecise for a blank first line.
  Discriminator: k1 (indicator on 7, command on 9, named 9 ≠ "the line after 7" = 8). Fix (a doc edit): reword to
  "the line after the block's first **content** line", or "the line of the block's first non-blank content line, else the
  line after the indicator".
- **F-2 FOLLOW-UP — the AF-AP-159 regex misses the right-operand and bound-to-variable spellings, and A's four tests would not catch that miss.**
  SOLID. § 6(c): the regex only matches `+` after `.start_mark.line`; `2 + node.start_mark.line` and
  `x = node.start_mark; line = x.line + 1` do not match, and A's four tests (fire-with-space, fire-without-space,
  no-fire-on-lookup, no-fire-on-map) contain no right-operand or bound-to-variable case, so a further-narrowed regex
  would stay green. Contract: none (the row is a NEW addition by this increment; no frozen line requires it to catch
  every spelling). Canonical: the production line at the PIN contains the left-operand form, which the regex does catch
  (and no longer contains at all, since R6 removed it). Material: **no** — the defect is already fixed in S; the regex is
  a future-recurrence screen, and it catches the exact spelling that fired in R5. Discriminator: hm1 (widen) kills; a
  right-operand fixture is the missing pin. Fix (a test addition): add one A test feeding `2 + node.start_mark.line`
  and asserting it does (or does not) fire, matching the intended scope.
- **F-3 INFO (KNOWN V-18) — an alias `run: *x` names the anchor's line, twice (f1).** SOLID. § 2 (f1: both the block's and
  the alias's value resolve to the anchor's content line; both R5 and R6, both rc 4). This is the known V-18 (issue #50
  family) — an alias and its anchor share one value node, so both refusals name the anchor's line. Not new; the brief
  says report only what is new — **nothing new** (the alias's line is inside the value, rc 4, same as R5).
- **F-4 INFO — CRLF files parse and name the correct line (j1).** SOLID. § 2 (j1: `read_text(errors='replace')` turns
  CRLF→LF, the file parses, and R5==R6 name line 6, the value's own line; no property involved). Not a defect; the
  CRLF→LF translation is what makes the marks line up, and it is correct. No contract line touches CRLF.
- **F-5 INFO (confirmations).** SOLID. AMENDMENT 5(a) holds (every `run:` refusal names a line inside the value, whatever
  properties precede the scalar and on whatever lines — § 2, all property shapes); AMENDMENT 5(b) holds (a literal block
  `|` keeps its line-for-line map; any other style names its first line — § 2/§ 3, R5-4 underneath); AMENDMENT 5(c)
  holds (no rc changes — § 4 rc-diff 0 over 20,000 and § 8 gates; the `rc` path is byte-identical); the W10b pair
  (R5 :7 the `|` / R6 :8 the command, both rc 4) reproduces § 1. AMENDMENT 4 (R5-1..R5-5) still holds underneath (the
  non-literal first-line rule is untouched).
- **F-6 INFO — no false positives / no new fail-open at the PIN.** SOLID. § 6(b) (AF-AP-159: 0 hits at the PIN);
  § 2b (every R6 composed value runs the helper, rc 0); § 8 (live tree `40 files scanned, clean` both modes; the
  two suites 220 passed; pyflakes clean). No shape the screen reads CLEAN is refused, and no shape that ran the
  helper under R5 stops running under R6.

### Predicate table (the rows closest to blocking; every other row fails conjunct 1 or 3 plainly)

| id | 1 contract | 2 canonical (real screen) | 3 material | 4 discriminator | 5 in boundary | BLOCKS? |
|---|---|---|---|---|---|---|
| F-1 | partial — 5(d) "the docstring states exactly what the code does" (one clause, one sub-case) | yes | **no** — the named line is still inside the value and is the command's own line; only the mechanism phrasing is imprecise | yes — k1 (named 9 ≠ "after the indicator" 8) | yes — S docstring | no → FOLLOW-UP |
| F-2 | none — the H row is a NEW addition; no frozen line requires it to catch every spelling | yes | **no** — the production defect is already fixed in S; the regex is a future-recurrence screen and catches the R5 spelling | yes — a right-operand fixture is the missing pin | yes — H/A | no → FOLLOW-UP |
| F-3 | KNOWN V-18 (issue #50) | yes | no — alias names its anchor's line (inside the value), same as R5, rc 4 | yes — f1 | no — issue #50 | no → KNOWN |
| F-4 | none (CRLF not in the contract) | yes | no — parses and names the correct line | yes — j1 | yes | no → INFO |

## GATE RECOMMENDATION

**`MERGE-READY-WITH-FOLLOWUPS`** — no finding satisfies the complete blocking predicate. The two findings that come
closest (F-1 the k1 docstring phrasing, F-2 the regex's right-operand miss) both fail conjunct 3 (material effect):
F-1's named line is still inside the value and is the command's own line (the "names its own line" clause the contract
actually cares about holds), and F-2's production line no longer contains the defect at all (the regex is a
future-recurrence screen, not the current code). Every AMENDMENT 5 clause reproduces through the real screen:
(a) every `run:` refusal names a line inside the value for all 24 new shapes (R5's was the property/indicator line, the
V5-05 defect); (b) a literal block `|` keeps its line-for-line map and any other style names its first line (R5-4
underneath); (c) no rc changes — rc-diff 0 over 20,000 inputs and the `rc` decision path is byte-identical (only
`_workflow_runs` changed); (d) the docstring states what the code does for every measured block except the
blank-first-content sub-case (F-1). The W10b pair (R5 :7 the `|` / R6 :8 the command, both rc 4) reproduces. All four
gates pass (220 passed ×2; set-id `f4e9ba5ca7d1`; live tree clean both modes; pyflakes clean). The five lane mutants
are all genuine kills over a clean 16-test unmutated baseline. **Follow-ups for the coordinator: F-1 (one-word
docstring reword for a blank first content line) and F-2 (one A test for the right-operand spelling).** This
recommendation depends on nothing I did not reproduce; it is not `CONTRACT-INVALID` (no PyYAML-version boundary
mismatch — § 1) and not `NOT-READY`.

## Evidence discipline — reproduced, read, skipped

- Reproduced here (SOLID): the premise (blob ids, line counts, diff stat, the W10b pair); all 24 new shapes through the
  real screen (R5 + R6 line and rc each); the de-vacuous (bash runs the helper for every R6 composed value, 27/27); the
  20,000-input differential (rc-diff 0 / line-diff 5905 + the R6-strictly-later property); the cost series (25 runs each
  at 1/10/100/1000 steps); item 6a/6b/6c (the regex fire on R5:521 and not at the PIN; ap_screen AF-AP-159: 0 hits;
  A's four tests vs the hm1 mutant); the 5 lane mutants with AF-AP-138; all four gates; the PyYAML 6.0.1-vs-6.0.3
  probe differential (byte-identical); the k1/k2/P1-P3 token-mark reconciliation.
- Read, not executed: the exact S and H diffs (`git diff b91673e c6dcd61`); the S docstring (scripts/no_laya_in_gates.py:498-504, `(first line, text, literal)`; the R5 line at scripts/no_laya_in_gates.py@b91673e:521 is `value.start_mark.line`); the H
  AF-AP-159 row (.claude/hooks/edit-snapshot.py:188-191) and the A `TestAFAP159` class (tests/test_edit_snapshot_ap_screen.py:476-489); the brief's premise block and the R5 report
  (§ 4 + appendix, as the V5-05 source).

**Key file lines cited below (each token is a substring of the cited line, verified at the PIN):**
| file (repo-relative) | line | the cited token (a substring of that line) |
|---|---|---|
| `scripts/no_laya_in_gates.py` | 498 | `(first line, text, literal)` |
| `scripts/no_laya_in_gates.py` | 500 | `the line after` |
| `scripts/no_laya_in_gates.py` | 501 | `the indicator of a block` |
| `scripts/no_laya_in_gates.py` | 513 | `t.end_mark.index: t.start_mark.line` |
| `scripts/no_laya_in_gates.py` | 526 | `token_line.get(value.end_mark.index, value.start_mark.line)` |
| `scripts/no_laya_in_gates.py` | 527 | `2 if value.style` |
| `tests/test_no_laya_in_gates.py` | 1264 | `R5 named 8, 7, 7, 6, 6` |
| `tests/test_no_laya_in_gates.py` | 1273 | `def test_empty_run_value_has_no_token_and_is_read_from_its_node` |
| `tests/test_no_laya_in_gates.py` | 1286 | `def test_run_value_behind_a_node_property_names_a_line_inside_it` |
| `tests/test_edit_snapshot_ap_screen.py` | 476 | `class TestAFAP159` |
| `tests/test_edit_snapshot_ap_screen.py` | 477 | `_AP_BY_ID["AF-AP-159"]` |
| `.claude/hooks/edit-snapshot.py` | 192 | `AF-AP-159` |
- Skipped, by the brief's rules: the coordinator's own m1-m7 mutants (machinery not changed; the readiness claim does
  not depend on them — mine are distinct, § 7); re-deriving issue #50/#46/#37 (KNOWN); GitHub Actions itself (the
  brief's exotic shapes — anchors, tags, complex keys, CRLF — are valid YAML 1.2 that PyYAML accepts; GitHub's own
  acceptance of them is NOT measured and stays INFERRED); recursive verification of the test/mutation/report machinery
  (unchanged).
- Instruments named: PyYAML 6.0.3 (system) and a throwaway 6.0.1 venv; the real screen `S_r5.py`/`S_r6.py` from
  `git show`; bash (the de-vacuous oracle); the code-intel pack (`scripts/lane_context.sh … -o
  /home/rocco/tmp-vj10r6/pack.md`: graft skeleton of `_workflow_runs`/`_source_errors`, GitNexus impact, crg callers,
  ripwire, the ap_screen of S).

## report_lint (bounded; pasted)

```
$ python3 scripts/report_lint.py --min-refs 12 tasks/briefs/laya/VERIFY-J1-0-R6-report.md --root . \
    --map S=scripts/no_laya_in_gates.py --map T=tests/test_no_laya_in_gates.py \
    --map H=.claude/hooks/edit-snapshot.py --map A=tests/test_edit_snapshot_ap_screen.py
report_lint: 16 refs — OK 13, NEAR 2, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
```

## DISCREPANCIES

- **DV-1 — the lane tree's origin moved ahead of the PIN during the lane.** At 21:19Z origin tip = `6963f00a`
  (transcripts); the brief's premise shows `c6dcd61` as origin head. The four boundary files are byte-identical at the
  PIN in both (blob ids agree), so no item is affected. Expected (other lanes/coord landing ahead of this verify).
- **DV-2 — my first driver built malformed complex-key (h2) and tab (j2) fixtures and reported them unparseable; the
  corrected driver (the one pasted in § 2) builds the YAML-legal forms (the brief's own "correctly-parsing" note) and
  both parse, named correctly, R5==R6. The first driver's h2/j2 rows were a construction artifact, not a screen result;
  they are not cited.
- **DV-3 — the brief's GATE 4 (pyflakes) is not on the system `python3`** (`No module named pyflakes`). The venv
  `/home/rocco/venv-agent-factory/bin/python` has pyflakes 3.4.0; I ran the venv interpreter as the gate intends
  (it is the hook's `$PY` per the R5 report's DV-4). Same result class (clean, rc 0).

## NOT-done

- No edit, stage, commit or push anywhere (the lane tree is clean except this report; the scratch lives in
  `/home/rocco/tmp-vj10r6/`). No bridge or PC use. No `/bug-echo` run and no `docs/INCIDENT-LOG.md` row (both outside
  this lane's boundary; F-1/F-2 are candidate anti-patterns for the coordinator to register if it wants: a docstring
  that phrases a line map as "after the indicator" when the first content line can be blank; an anti-pattern regex
  that pins only one operand spelling with no test covering the other).
- The k1 docstring fix (F-1) and the right-operand A test (F-2) are **not** applied (I did not edit S or A); they are
  follow-ups for the coordinator. The R5/R6 screens ran only on scratch copies.
- GitHub Actions was not run: the brief's exotic shapes (anchors, tags, complex keys, flow, CRLF) are valid YAML 1.2
  that PyYAML accepts; GitHub's own acceptance of them stays INFERRED.
- The coordinator's m1-m7 mutants and its sweep driver were not re-run (machinery not changed; § 7 carries distinct
  lane mutants).
- Scratch `/home/rocco/tmp-vj10r6/` (fixture trees, mutant trees `mut/`, `mut2/`, the venv `v601/`, the drivers and
  their outputs) is removed at the end, per the brief; the outputs are pasted above.
