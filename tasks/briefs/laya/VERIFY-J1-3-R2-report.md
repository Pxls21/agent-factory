# VERIFY-J1-3-R2 — report (task #208)

Lane: VERIFY-J1-3-R2 (sandbox adversarial verifier, Opus 5.5, shared tree, no worktree isolation).
Brief: `tasks/briefs/laya/VERIFY-J1-3-R2-brief.md`; governing brief: `tasks/briefs/pc/pc-verify-j1-3.md`.
PIN: ff7a671 (second real-run pin a78bdca). Scratch: `/tmp/vj13r2/` (removed at the end).
Started: 2026-09-24T00:13:45Z (date -u).

STATUS: COMPLETE. GATE RECOMMENDATION: NOT-READY (blockers F-01, F-02, F-03, F-04; CONTRACT-DEFECT F-05 returned for amendment).

TL;DR: the harvester is deterministic and its worktree admission holds. No worktree race leaked a byte in 720 dynamic runs, and every
lane mutant is killed. Two defects change the real KC-J7 line at both pins:
- a wrapped bold title loses a line, so the valid V5-05 BLOCKER is refused (F-01);
- the drift anchor is narrower than the contract, so P5c's boundary deviation is silently skipped (F-02).

Two more meet the frozen criteria on scratch repositories:
- `HEAD` is re-read after admission, so 45 of 300 racer runs mint rows mixing two commits (F-03);
- `str.splitlines()` (AF-AP-132) mints rows from prose and silently drops rows (F-04).

The true line at ff7a671 is `harvest: 224 rows … v1.finding_class=102, wf.drift=3`, `refused: 40`, not 222 and 41.

## 1. PREMISE

Re-measured 2026-09-24T00:14:16Z (sandbox, uid 0). Every line below is pasted from this session's output.

```
$ date -u; origin; HEAD; id -u
2026-09-24T00:14:16Z
ff7a671
efda000
0
$ git diff --stat a78bdca ff7a671 -- <boundary> | wc -l
0
$ git diff --stat ff7a671 HEAD -- <boundary> | wc -l
0
$ blob ids at ff7a671
22b63bc47e7c 849 scripts/decide-harvest
2cace4741511 581 tests/test_decide_harvest.py
$ refusal census
      1 decision-row-duplicate
      1 harvest-output-source-conflict
      1 harvest-source-uncommitted
      1 harvest-source-unknown
      3 harvest-source-unparseable
$ python -m pytest tests/test_decide_harvest.py -q -p no:cacheprovider --basetemp=/tmp/vj13r2/p/bt | tail -1
33 passed in 9.26s
$ bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py
1 files set=87e28761f102
```

- P-1 MATCH (SOLID): the blob ids, line counts, test count, set id, refusal census, first-pass headings (3/14/20/27/32/37/42/48/49) and the
  first brief's lines 147-159 all equal the premise block. The fixture blobs (`fd49ef926dbb`, `00c5b96540ad`, `84534293a9ff`,
  `3ad1434c5717`, `5b5ddb0ca78d`) and the four decisions-package blobs (`377ccd53da0c`, `607b65b613e2`, `bf04415d72c1`, `71fc398a5340`)
  are identical at a78bdca and ff7a671.
- P-2 DRIFT, no item changed (SOLID): the shared tree's HEAD moved from bfc7687 (authoring) to efda000 (this brief's own commit). The
  boundary diff ff7a671..HEAD is still 0 lines. No item is CONTRACT-INVALID.
- P-3 (SOLID): `python` here is `/usr/local/bin/python` 3.11.15, and so is `/root/venv-agent-factory/bin/python`. The seed says
  "Python >= 3.12" (`seeds/seed-laya-j1-v1.yaml:69`). The suite runs green on 3.11; I note it as an environment fact only.
- P-4 (SOLID): the lane report's identity table (`tasks/briefs/laya/J1-3-report.md:200-207`, for example `befe924d3656`) lists sha256
  prefixes of the committed bytes, not git blob ids. I checked all seven: each equals `sha256` of the ff7a671 blob. Consistent.
- P-5 CODE INTEL (SOLID): the pack (`/tmp/vj13r2/pack.md`, 163 lines) reads `no definitions indexed for this file` for
  `scripts/decide-harvest` (graft skips a file with no `.py` suffix), and GitNexus `impact` on `make_row` returns `risk: UNKNOWN`. The
  script is unmapped by the quartet. The named fallback: I read `scripts/decide-harvest:1-849` whole and ran it as a subprocess.

## 2. THE FIRST PASS, GRADED

Every claim in `tasks/briefs/laya/VERIFY-J1-3-report.md` §1-§8, reproduced on the ff7a671 bytes (clone `/tmp/vj13r2/clone-ff7a671`) or
on scratch repositories through the real script. Line cites were read with `sed -n '<n>p'` at the pin.

| # | first-pass claim (report line) | grade | my evidence |
|---|---|---|---|
| G-1 | `__init__.py:18` blob `377ccd53da0c` (24 lines), "`DecisionStateError` is imported" (line 5) | blob REPRODUCED; line cite REFUTED | line 18 is `    decision_state,`; `DecisionStateError,` is line 17 |
| G-2 | `canonical.py:27-31` blob `607b65b613e2` (78 lines), "The `canonical` function is correct" (line 6) | blob REPRODUCED; cite REFUTED; "correct" UNVERIFIABLE | lines 27-31 are `def _canon_str` (NFC + newline refusal), not `canonical`; "correct" is a judgment with no command |
| G-3 | `volatile.py:142-143` blob `bf04415d72c1` (395), `_strip_pin_suffix` (line 7) | REPRODUCED | line 142 `def _strip_pin_suffix(value: str) -> str:` |
| G-4 | `ledger.py:335-336` blob `71fc398a5340` (616), `make_row` (line 8) | REPRODUCED | line 335 `def make_row(` |
| G-5 | `scripts/decide-harvest:824-825` "checks duplicates and correctly emits `decision-row-duplicate` before calling append" (line 9) | REFUTED | :824-825 is the `except DecisionStateError` branch that runs AFTER `append` raised; nothing is checked before append. "Correctly" is also refuted: the same branch swallows a corrupt-ledger refusal (finding F-05) |
| G-6 | `tests/test_decide_harvest.py:368-372` enforces `"lane"` (line 10) | REPRODUCED | :368 `assert {row["state"]["lane"] for row in rows} == {"pc-verify-k1.md"}`; mutant L-m9 is killed by it (§3.4) |
| G-7 | "The file counts and contents identically match the contract block measurements" (line 12) | conclusion REPRODUCED by me; the claim's evidence UNVERIFIABLE | the first pass re-measured the four decisions files, which are not in the first brief's premise block; it pasted none of the block's own lines (the two script blobs, the census, the seam greps). My §1 re-measure matches |
| G-8 | "Untracked file read attempt correctly yielded `harvest-source-unknown:` via :173 with rc 5" (line 16) | REFUTED as a committed-source claim | an untracked KNOWN-kind path gives `4 harvest-source-uncommitted: tasks/briefs/x/NEW-report.md`; only an unknown-kind path (`notes.txt`) gives `5 harvest-source-unknown`, which tests the kind table, not the committed rule. :173 does hold that string |
| G-9 | a modified tracked file gives `harvest-source-uncommitted` via :182, rc 4, no rows (line 17) | REPRODUCED | :182 `return None, (4, f"harvest-source-uncommitted: {path}")`; R3 below: 101 of 120 runs refused rc 4 |
| G-10 | an after-admission swap does not affect parsing, via `_head_blob` :151 (line 18) | conclusion REPRODUCED (my races: 0 leaks in 720 runs); the cited evidence is weaker than claimed | the probe it cites (`tests/test_decide_harvest.py:300-356`) checks only `source_digest`; mutant B-m5b (parse the worktree text, keep the HEAD digest) survives it (F-07) |
| G-11 | hostile inputs tested "via :372-373 `_finding_candidates`" (line 21) | REPRODUCED (cite) | :372 `def _finding_candidates(` |
| G-12 | an unclosed heading gives `unterminated-heading` via :248 (line 22) | REPRODUCED | :248 `return None, "unterminated-heading"`; the lane's test (d) and my runs agree |
| G-13 | a table with duplicated headers "(`class \| class`)" gives `bad-finding-id` via :424 (line 23) | REFUTED for the stated input | `\| # \| class \| class \|` gives `no-title-column` (no title column). A duplicated `#` header ROW gives `bad-finding-id` (V-f2); a duplicated `id` header row gives `bad-class` (V-f) |
| G-14 | a bullet with `FOLLOW-UP / UNVERIFIED` is refused "via regex rejection at :354" (line 24) | REFUTED (mechanism and line) | the bullet IS an anchor (`BULLET_FINDING_RE` matches `FOLLOW-UP\b`) and is refused `bad-title` at :387-389: `3 harvest-source-unparseable: tasks/briefs/x/VERIFY-X-report.md:10 (bad-title)`. :354 is the TABLE class-cell regex |
| G-15 | "Hive scout format with the wrong `n` … `n-mismatch` via :605 in reviewer_rows" (line 25) | behaviour REPRODUCED; line cite REFUTED | :605 is `_reviewer_rows`; the scout's `n-mismatch` is :624. Both refuse (the lane's test (d) mutates the scout `n`) |
| G-16 | two PIN files give one lane with separate `source_ref`s, via :450 (line 29) | REPRODUCED | identity (c): `lanes=['pc-verify-q7.md']`, two paths, 4 distinct row ids; :450 `"lane": lane,` |
| G-17 | a re-run into the same JSONL prints `decision-row-duplicate` skips and keeps the file, via :824 (line 30) | REPRODUCED for a clean ledger | identity (b): `harvest: 0 rows`, `skipped: 10 duplicates`, 10 stderr lines, file unchanged. Not "accurate" for a corrupt ledger (F-05) |
| G-18 | real run `harvest: 214 rows`, `refused: 39` (line 34) | REPRODUCED | §4, a78bdca: `harvest: 214 rows`, `refused: 39 records` |
| G-19 | the re-run is identical, rc 3, `cmp` 0 (line 35) | REPRODUCED | §4: `cmp-jsonl rc=0`, `cmp-stderr rc=0`, `cmp-stdout rc=0`, rc 3 twice |
| G-20 | worktree-read mutant killed by `test_source_bytes_come_from_head_after_admission` :300, exit 99 (line 39) | REPRODUCED | L-m5 KILLED by that test (`1 failed, 32 passed`); :300 is its `def` |
| G-21 | silent-duplicate mutant killed by `test_duplicate_rerun_prints_every_skip_and_preserves_bytes` :181 (line 40) | REPRODUCED | L-m4 and N5 KILLED by that test; :181 is its `def` |
| G-22 | test file `33 passed` (line 44) | REPRODUCED | §3.5: `33 passed in 8.82s`, `33 passed in 9.11s` |
| G-23 | "Suites … `120 passed, 1 skipped` (non-root)" (line 45) | REPRODUCED (consistent) | the two-file set collects 67 + 54 = 121 tests; as root I get `121 passed in 3.56s`. The one skip is the root-only tmpfs test |
| G-24 | the screen "at :1 ran clean without detecting terms past `#!/usr/bin/env`" (line 46) | screen REPRODUCED; the cite UNVERIFIABLE | `no_laya_in_gates: 40 files scanned, clean`, rc 0; line 1 is the shebang, which is not evidence of anything |
| G-25 | `GATE RECOMMENDATION: MERGE-READY`; "NO qualifying blockers"; "tracks strict grammar definitions"; "protects head reads correctly during admission" (lines 49-50) | REFUTED | F-01, F-02, F-03 and F-04 (§5) each meet the whole predicate; F-03 shows rows carrying registry bytes read after admission from a later commit |

TALLY (25 graded claims): REPRODUCED 14 (G-3, G-4, G-6, G-9, G-11, G-12, G-16, G-17, G-18, G-19, G-20, G-21, G-22, G-23) ·
partly REPRODUCED 5 (G-1, G-2, G-7, G-10, G-15, where the substance holds and a cite or the evidence fails) · REFUTED 5 (G-5, G-8, G-13,
G-14, G-25) · screen reproduced, cite UNVERIFIABLE 1 (G-24). The first pass also did NOT run what the coordinator listed: no FIFO,
symlink or background writer; 4 hostile inputs in total; no harvest lines, sampled rows or `cmp` pasted; 2 mutants; one test run and no
pyflakes. §3 runs all of it.

## 3. ITEMS 2-7 OF THE FIRST BRIEF

Method (all SOLID unless marked): every case builds a scratch git repository from the pinned fixture tree
(`tests/fixtures/decisions/sources/` at ff7a671), commits it with a fixed author and date, and runs the REAL pinned script
`/tmp/vj13r2/clone-ff7a671/scripts/decide-harvest` as a subprocess (it imports `agent_factory.decisions` from its own clone's `src/`).
Harness: `/tmp/vj13r2/h/harness.py`; case scripts `g1_incident.py`, `g2_verify.py`, `g3_lane.py`, `g4_transcript.py`, `races.py`,
`headmove.py`, `headflip.py`, `identity.py` (all under `/tmp/vj13r2/h/`, removed at the end; their outputs are pasted here).

### 3.1 Item 2 — the committed-source rule under the three worktree races (and one HEAD race)

| case | runs | outcome (pasted) | rows carrying non-HEAD bytes | deciding line |
|---|---|---|---|---|
| modified tracked source | lane test + R3 | `harvest-source-uncommitted`, rc 4, no `--out` | 0 | `scripts/decide-harvest:181` compares the worktree bytes with the HEAD blob; `:182` refuses |
| untracked known-kind path | 1 | `4 harvest-source-uncommitted: tasks/briefs/x/NEW-report.md` | 0 | `:180` (`_head_blob` is `None`) then `:182` |
| R1 FIFO in place of a tracked source | 1 + discovery 1 | `rc=4 stderr='harvest-source-uncommitted: tasks/briefs/x/X-report.md' out-exists=False secs=0.07` (both modes) | 0 | `:159` `not target.is_file()` returns `None`; `:181` |
| R2 symlink (identical bytes) in place | 1 | `rc=4 … harvest-source-uncommitted … out-exists=False` | 0 | `:159` `target.is_symlink()` |
| R3 background rewriter (HEAD bytes ⇄ `# Leaked`) | 120 | `rc-tally={0: 19, 4: 101} rows-carrying-non-HEAD-bytes=0` | 0 | `:181` admits only equal bytes; `:184-193` build `Source` from the HEAD blob `data` (`:180`); `:801` parses only that `Source` |
| R4 FIFO ⇄ regular, atomic `renameat2(RENAME_EXCHANGE)` | 300 | `rc-tally={'TIMEOUT': 72, 0: 75, 4: 153} rows-carrying-non-HEAD-bytes=0` | 0 | HANG: `:159` checks the path, `:161` `read_bytes()` opens it again; a FIFO swapped in between blocks the open (process in kernel wait `wait_for_partner`, `ps` at run 262). F-06 |
| R5 symlink (other bytes) ⇄ regular, atomic exchange | 300 | `rc-tally={0: 128, 4: 172} rows-carrying-non-HEAD-bytes=0` | 0 | `:159-161`; row bytes come only from `:180` |
| HEAD flips A ⇄ B (`git update-ref`, worktree stays A), no shim | 300 | `outcomes={'rc=0 MIXED': 45, 'rc=0 consistent': 184, 'rc=4 ': 71}`; first MIXED run #3: `action_excerpt='AF-AP-2 follow-up vA' row_title='malformed record silently dropped vB' source_digest=a00856ac9a92` | **45** | `:141` and `:152` resolve the symbolic ref `HEAD` in every git call; `:787` (tree) and `:790-791` (registry) are read AFTER admission. F-03 |
| same, deterministic control (a PATH `git` wrapper commits B at the harvester's 2nd `ls-tree`, the call at `:787`) | 1 | `rc=0 … ls-tree calls=2 -> ['MIXED title vA / row_title vB']`; no-shim control `-> ['consistent']` | 1 | as above |
| same racer against the corrected copy (HEAD pinned once, `/tmp/vj13r2/fix`) | 300 | `outcomes={'rc=0 consistent': 235, 'rc=4 ': 65}` | 0 | discriminator for F-03 |
| porcelain committer (`write` + `commit -a`, random 0-120 ms pause) | 400 | `{'rc=4': 219, 'rc=0 consistent': 172, …}`: 0 MIXED | 0 | negative result: a porcelain commit's own dirty-worktree window is wider than the harvest window. The 7 `rc=4 consistent` and 2 double-row outcomes in this tally came from MY harness reusing out-file names left by an earlier round (discarded; not a harvester behaviour) |

The brief's question, answered: no WORKTREE race lets bytes read after admission into a row (0 in 3 static and 720 dynamic runs). A
HEAD race does: the registry title in `row_title` is read after admission from whatever commit `HEAD` names at that moment (F-03). A
FIFO swapped in at the right moment hangs the run indefinitely (F-06).

### 3.2 Item 3 — hostile inputs, four grammars, 62 inputs (each appended to the matching fixture file, the file harvested alone)

Legend: ✓ = the contract outcome (a refusal by name or no record); **✗** = a contract violation; (G) = a row the grammar mints by
construction (the contract's own anchor matches; a design limit, F-18).

**Incident log** (`docs/INCIDENT-LOG.md`, baseline 2 rows)

| id | named shape | outcome (pasted) | verdict |
|---|---|---|---|
| I-a | prose: a bold date mid-line | `harvest: 2 rows` (new 0) | ✓ |
| I-b | prose: `**2026-01-05** — AF-AP-1 did not recur.` | new 0 | ✓ |
| I-c | prose: `**2026-01-06 — AF-AP-1 did not recur this week**` | new 1: `ap.violates_row ans='yes'` | (G) |
| I-d | registry table without the declared columns | rc 3, two `no-registry-row` refusals at the fixture copy's lines 10 and 14 (both entries) | ✓ |
| I-e | registry header duplicated under the separator | `harvest: 2 rows`, rc 0 | ✓ |
| I-f | lookalike pipe U+FF5C opening a registry row | rc 3, two `no-registry-row` (the registry parse stops at the row) | ✓ |
| I-g | lookalike hyphen U+2010 in the date | new 0 | ✓ |
| I-h | fullwidth digits in the date | new 1: `loc='２０２６-０１-０８ — AF-AP-1 fullwidth digits'` | **✗** F-10 |
| I-i | lookalike hyphen U+2010 in the id | new 0 | ✓ |
| I-j | `See the entry below.` + U+2028 + `**2026-01-10 — AF-AP-1 minted from mid-line**` (ONE git line) | new 1: `loc='2026-01-10 — AF-AP-1 minted from mid-line'` | **✗** F-04 |
| I-k | heading wrapped over 2 lines (`… AF-AP-1 first line` / `continues with AF-AP-2 here**`) | new 1: `loc='continues with AF-AP-2 here'`; the AF-AP-1 row is lost | **✗** F-01 |
| I-l | heading wrapped over 3 lines | new 1: `loc='2026-01-12 — AF-AP-1 line one line three'`; the middle line and the AF-AP-2 row are lost | **✗** F-01 |
| I-m | registry id duplicated with another title | `row_title: "a SECOND title for AF-AP-1"` (last wins, silently) | INFO F-20 |

**Verify-report finding** (`tasks/briefs/x/VERIFY-X-report.md`, baseline 3 rows)

| id | named shape | outcome (pasted) | verdict |
|---|---|---|---|
| V-a | prose: a bullet-shaped finding mid-line | new 0 | ✓ |
| V-b | prose: `- **F-9 BLOCKER** was retracted after re-running.` | rc 3, `VERIFY-X-report.md:10 (bad-title)` | ✓ |
| V-c | prose shaped as a bullet: `- **Note INFO — this bullet is prose, not a finding**` | new 1: `v1.finding_class ans='INFO' loc='Note @ Findings'` | (G) |
| V-d | a table without the declared columns (`\| # \| severity \| finding \|`) | new 0 | ✓ |
| V-e | a class table without a title column | rc 3, `:12 (no-title-column)` | ✓ |
| V-f | the `id` header duplicated under the separator | rc 3, `:12 (bad-class)`; the next real row F-5 is harvested | ✓ |
| V-f2 | the `#` header duplicated | rc 3, `:12 (bad-finding-id)`; F-5b harvested | ✓ |
| V-g | lookalike pipes U+FF5C | new 0 | ✓ |
| V-h | lookalike dash (en dash U+2013) before the title | rc 3, `:10 (bad-title)` | ✓ |
| V-i | Cyrillic `Е` in the class | new 0 | ✓ |
| V-j | a class-table row split across two lines | new 0 (the table ends) | ✓ |
| V-j2 | a split row whose second half has the header's cell count | new 2, one with id `cont` | (G) |
| V-k | a bullet title wrapped over 2 lines (the contract: "it may wrap") | rc 3, `:10 (bad-title)`: a VALID record refused | **✗** F-01 |
| V-l | a bullet title wrapped over 3 lines | new 1: `ans='BLOCKER' … "title": "part one part three"` (middle line dropped) | **✗** F-01 |
| V-m | `Context sentence.` + U+2028 + `- **F-13 BLOCKER — minted from mid-line**` (one git line) | new 1: `v1.finding_class ans='BLOCKER' loc='F-13 @ Findings'` | **✗** F-04 |
| V-n | U+2028 inside a class-table cell (`\| F-14 \| INFO \| quotes a<U+2028>b payload \|`), then a valid F-15 row | new 0, rc 0, `refused: 0`: both valid rows silently lost | **✗** F-04 |
| V-o | a bullet anchor inside a code fence | new 1: `ans='BLOCKER' loc='F-16 @ Findings'` | (G) |
| V-p | an unescaped pipe in a title cell | new 1: `"title": "title with a"` | (G) |
| V-q | an empty title cell | new 1: `ans='BLOCKER' … "title": ""` | (G) |
| V-r | a bold class cell with a qualifier (`**CONTRACT-DEFECT** (x)`) | rc 3, `:12 (bad-class)` | F-19 (reading) |

**Lane report** (`tasks/briefs/x/X-report.md`, baseline 2 rows: 1 `wf.drift`, 1 `d1.bug_echo_scores`)

| id | named shape | outcome (pasted) | verdict |
|---|---|---|---|
| L-a | prose: `We saw no BOUNDARY DEVIATION: all files named.` | `wf.drift=1` (new 0) | ✓ |
| L-b | prose: `- **BOUNDARY DEVIATION**: none — only the named files changed.` | `wf.drift=2`; the new row's `observed` is `"none — only the named files changed."` | (G) |
| L-c | the contract anchor `- **BOUNDARY DEVIATION: touched scripts/x.py**` (`:` right after DEVIATION) | `wf.drift=1`: no row, no refusal | **✗** F-02 |
| L-c2 | the real P5c form `- **BOUNDARY DEVIATION — \`tests/conftest.py\` was patched** (fixture).` | `wf.drift=1`: no row, no refusal | **✗** F-02 |
| L-c3 | `- **BOUNDARY DEVIATION** touched scripts/z.py` (DEVIATION followed by `**`) | `wf.drift=1`: no row, no refusal | **✗** F-02 |
| L-d | dotless `ı` (U+0131): `1. BOUNDARY DEVıATıON: lookalike dotless i` | `wf.drift=2`, observed `"lookalike dotless i"` | **✗** F-10 |
| L-e | Arabic-Indic digit: `١. BOUNDARY DEVIATION: arabic-indic one` | `wf.drift=2`, observed `"arabic-indic one"` | **✗** F-10 |
| L-f | a bug-echo table without the declared columns | new 0 | ✓ |
| L-g | the bug-echo header duplicated under the separator | rc 3, `:16 (bad-rating)`; the real row harvested | ✓ |
| L-h | lookalike pipes | new 0 | ✓ |
| L-i | the rating `Hıgh` (dotless ı) | accepted: `urgency=high` | F-10 |
| L-j | a bug-echo row split across lines | new 0 | ✓ |
| L-k | `Context.` + U+2028 + `1. BOUNDARY DEVIATION: minted from mid-line` (one git line) | `wf.drift=2`, observed `"minted from mid-line"` | **✗** F-04 |
| L-l | a bug-echo table under a heading with no AF-AP id | rc 3, `:16 (no-class-slug)` | ✓ |
| L-m | the rating `-- HIGH` (punctuation, not an emoji) | accepted: `urgency=high` | F-10 (INFO) |

**Transcript JSONL** (`transcripts/x/t.jsonl`, baseline 3 rows)

| id | named shape | outcome (pasted) | verdict |
|---|---|---|---|
| T-a / T-a2 | valid JSON of the wrong shape: a list line / a string line | rc 3, `t.jsonl:5 (bad-json)` | ✓ |
| T-b | a valid JSON object with no `message` | new 0 | ✓ |
| T-c | prose that looks like a dispatch (a text block naming `hive-scout`) | new 0 | ✓ |
| T-d | payload: valid JSON, wrong shape (`hits` an object) | rc 3, `:6 (bad-payload)` | ✓ |
| T-e | payload: a JSON list | rc 3, `:6 (bad-payload)` | ✓ |
| T-f | the result line before the dispatch | rc 3, `:6 (no-result)` | ✓ |
| T-g | a VALID result record whose note holds a raw U+2028 | rc 3, `:6 (bad-json)`, `:7 (bad-json)`, `:5 (no-result)`: a valid record refused, and line 7 does not exist (the file has 6 git lines) | **✗** F-04 |
| T-h | `NaN` as `n` | rc 3, `:6 (bad-payload)` | ✓ |
| T-i | text after the payload JSON | rc 3, `:6 (bad-payload)` | ✓ |
| T-j | a dispatch inside a `user` record | new 0 | ✓ |
| T-k | a lower-case `sev` | rc 3, `:6 (unknown-sev)` | ✓ |
| T-l | a valid JSON line nested 100000 deep | rc 1, `RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string` | **✗** F-11 |
| T-m | a valid record whose payload is nested 100000 deep | rc 1, the same `RecursionError`; in discovery mode the crash leaves `ledger rows left behind: 7` and prints no harvest line | **✗** F-11 |

The corrected copy (`/tmp/vj13r2/fix`: the heading join keeps every piece, the contract's own drift anchor, `\n` lines, HEAD pinned
once; 38 changed lines, pyflakes rc 0) gives the contract outcome for I-j, I-k, I-l, V-k, V-l, V-m, V-n, L-c, L-c2, L-c3, L-k and T-g,
for example I-k `harvest: 4 rows` with `loc='2026-01-11 — AF-AP-1 first line continues with AF-AP-2 here'` twice, V-n F-14 and F-15
harvested, T-g `b2.hit_role … "snippet": "a b"`. Every other case is unchanged.

### 3.3 Item 4 — identity and duplicates (scratch repositories, `/tmp/vj13r2/h/identity.py`)

| id | check | pasted result | verdict |
|---|---|---|---|
| (a) | two runs, same commit, two fresh files | `rc=0,0 rows=10,10 sha=b9cd7b6f577eb069,b9cd7b6f577eb069 cmp=0` | ✓ SOLID |
| (b) | a second run into the SAME ledger | `rc=0 line1='harvest: 0 rows, …' … skipped: 10 duplicates' stderr-lines=10 all-duplicate=True file-unchanged=True` | ✓ SOLID |
| (c) | two reports of one lane at two PINs (AMENDMENT A1) | `v1 rows=4 lanes=['pc-verify-q7.md'] paths=['report-pc-verify-q7.md--1234abc.md', 'report-pc-verify-q7.md--89abcdef0123.md'] distinct row_ids=4 distinct state_digests=2` | ✓ SOLID |
| (d) | the same commit (`50be79d == 50be79d`) harvested at two roots into ONE ledger; F-30 cites `` `<rootA>/src/existing.py:1` `` | run@A `harvest: 4 rows`; run@B `harvest: 1 rows … skipped: 3 duplicates`; `F-30 rows in the ledger=2 paths=[['src/existing.py'], []]` | **✗** F-15 (a duplicate decision under a new row id) |
| (e) | a ledger with one row duplicated by hand, then a harvest of 2 NEW rows into it | `rc=0 line1='harvest: 0 rows, …' … skipped: 2 duplicates'`, stderr twice `decision-row-duplicate: a5db82c6…115e` (`distinct-ids-in-stderr=1`), `ledger-unchanged=True` | **✗** F-05 |
| (e') | two CONCURRENT harvests into one fresh `--out` (40 pairs) | `concurrent pairs=40 ledgers left corrupt=32`; pair #0 `both rc=[0, 0]`, both `harvest: 1 rows`; replay → `decision-row-duplicate: a5db82c6…115e`; `file lines=2`; a THIRD harvest into it: `rc=0 'harvest: 0 rows' … skipped: 10 duplicates'`, 1 distinct id in stderr | **✗** F-05 |
| (f) | `--out` is a directory | `rc=3 … refused: 2 records`; `X-report.md:3 (state:decision-ledger-not-regular)`, `:10 (…)` | F-12 |
| (g) | `--out` under a missing directory | `rc=1 stdout-lines=0 last-stderr="FileNotFoundError: [Errno 2] No such file or directory: …"` | F-12 |
| (h) | one committed latin-1 report beside good sources, discovery | `rc=3 stdout-lines=0 stderr='harvest-source-unparseable: tasks/briefs/x/Latin-report.md:1 (bad-utf8)' out-exists=False` | F-13 |
| (i) | SOURCE args: untracked `tasks/briefs/x/A-report.md` (sorts first) and `zz/unknown.txt` | `rc=5 stderr='harvest-source-unknown: zz/unknown.txt'` | F-14 |
| (j) | the same record committed twice in one file | `harvest: 3 rows … skipped: 2 duplicates` on a FRESH ledger | INFO (a printed skip; correct) |

Identity key (re-derived from primary source): `_compute_row_id` (`src/agent_factory/decisions/ledger.py:85-97`) hashes producer,
question_id, `source_ref.{kind, locator, path}` and state_digest; `source_digest` is excluded (Amendment J1-A1). Evidence: all 214 a78bdca
row ids survive at ff7a671 although `docs/INCIDENT-LOG.md` changed between the pins (`rows at a78bdca whose row_id is absent at
ff7a671: 0`).

### 3.4 Item 6 — mutants (scratch workspace `/tmp/vj13r2/mut/ws`, a copy of the pinned bytes; baseline `33 passed in 8.73s`; after every mutant the script was restored and checked at sha256 `befe924d3656`)

| mutant | diff line (the replacement) | count | killing test | verdict |
|---|---|---|---|---|
| L-m1 unparseable stderr print removed | `pass` | 10 failed, 23 passed | `test_malformed_record_refused_by_name_and_other_rows_survive[…]` | KILLED |
| L-m2 admit without comparing worktree bytes | `if data is None:` | 3 failed, 30 passed | `test_admission_untracked_modified_unknown_and_existing_out_untouched` | KILLED |
| L-m3 an undeclared type added to the printed set | `"wf.drift",` + `"x.extra",` | 2 failed, 31 passed | `test_fixture_harvest_exact_rows_and_provenance` | KILLED |
| L-m4 the duplicate stderr print removed | `pass` | 1 failed, 32 passed | `test_duplicate_rerun_prints_every_skip_and_preserves_bytes` | KILLED |
| L-m5 parse a later worktree read, digest from it too | `_wt = (root / source.path).read_bytes()` … `hashlib.sha256(_wt)` | 1 failed, 32 passed | `test_source_bytes_come_from_head_after_admission` | KILLED |
| L-m6 reviewer `n` equality disabled | `if False:` | 1 failed, 32 passed | `test_reviewer_n_mismatch_is_refused` | KILLED |
| L-m7 missing registry row → placeholder title | `title = registry.get(row_id, "unknown")` | 1 failed, 32 passed | `test_malformed_record_refused_by_name_and_other_rows_survive[…no-registry-row]` | KILLED |
| L-m8 `--out` written by `open()` | `open(args.out, 'a').write(json.dumps(row) + '\n')` | 24 failed, 9 passed | `test_fixture_harvest_exact_rows_and_provenance` | KILLED |
| L-m9 the A1 final `.md` removal dropped | `if False:` | 2 failed, 31 passed | `test_pc_report_lane_pin_is_normalized_only_by_decision_state` | KILLED |
| L-x1 class-table ID regex disabled | `if False:` | 1 failed, 32 passed | `test_class_table_rejects_invalid_finding_id` | KILLED |
| L-x2 missing tool-use id ignored | `if False:` | 1 failed, 32 passed | `test_hive_anchor_with_missing_tool_id_is_refused` | KILLED |
| L-x3 committed-output guard disabled | `if False:` | 1 failed, 32 passed | `test_committed_output_path_is_refused_before_harvest` | KILLED |
| L-x4 drift delimiter made optional | `r"\s*(?:—\|:\|\*\*)?(?P<tail>.*)$",` | 1 failed, 32 passed | `test_boundary_deviation_requires_the_declared_delimiter` | KILLED |
| B-m1 (the J1-3 brief's m1) a malformed record skipped silently, not counted | `continue` before `refusal = Refusal(` | 10 failed, 23 passed | `test_malformed_record_refused_by_name_and_other_rows_survive[…]` | KILLED |
| B-m2 (brief m2) an untracked source read from the worktree | `if data is None: data = _regular_worktree_bytes(root, path)` | 3 failed, 30 passed | `test_admission_untracked_modified_unknown_and_existing_out_untouched` | KILLED |
| B-m3 (brief m3) one type dropped from the harvest line | `… for question_id in QUESTION_IDS if question_id != "b2.hit_role")` | 2 failed, 31 passed | `test_fixture_harvest_exact_rows_and_provenance` | KILLED |
| B-m5b parse the worktree text after admission, keep the HEAD digest | `source = Source(source.path, source.kind, _wt, _wt.decode('utf-8'), source.digest)` | 33 passed | none | **SURVIVED** (F-07) |
| N1 admission after parsing (the worktree check moved after the appends) | `if data is None:` at admission + `for _s in sources: if _regular_worktree_bytes(root, _s.path) != _s.data: … return 4` before the harvest line | 2 failed, 31 passed | `test_admission_untracked_modified_unknown_and_existing_out_untouched`, `test_all_requested_sources_are_admitted_before_any_rows_are_written` | KILLED |
| N2 the worktree read used instead of the HEAD blob | `data = _regular_worktree_bytes(root, path)` | 3 failed, 30 passed | `test_admission_untracked_modified_unknown_and_existing_out_untouched` | KILLED |
| N3a a class table with no title column accepted (last column used) | `title_index = len(headers) - 1 if title_index is None else title_index` | 33 passed | none | **SURVIVED** (F-08) |
| N3b a class-table row with a missing column accepted (padded) | `cells = cells + [""] * (len(headers) - len(cells))` | 33 passed | none | **SURVIVED** (F-08) |
| N3c the registry accepts a table missing the declared columns (first two cells) | `if (_split_table_row(lines[index]) or [])[:2] != header_cells[:2] or` | 33 passed | none | **SURVIVED** (F-08) |
| N4 `append` without `make_row` (raw state, digests by hand) | `row = _r if True else make_row(` | 2 failed, 31 passed | `test_secret_text_is_redacted_through_make_row`, `test_pc_report_lane_pin_is_normalized_only_by_decision_state` | KILLED |
| N5 the duplicate refusal made a silent skip that prints nothing | `if exc.reason == "decision-row-duplicate": continue` | 1 failed, 32 passed | `test_duplicate_rerun_prints_every_skip_and_preserves_bytes` | KILLED |
| X1 a heading may NOT wrap (anchor line only) | `for offset in range(1):` | 33 passed | none | **SURVIVED** (F-01, F-09) |
| X2 the numbered `BOUNDARY DEVIATION` form removed | `r"^(?:- \*\*BOUNDARY DEVIATION\*\*)"` | 33 passed | none | **SURVIVED** (F-09) |
| X3 the class qualifier ` (<qualifier>)` no longer accepted | `r"(?:, (?:SOLID\|UNSURE))?",` | 33 passed | none | **SURVIVED** (F-09) |
| X4 absolute-path relativization in `paths` removed | `if False:` | 33 passed | none | **SURVIVED** (F-09, F-15) |
| X5 the rating emoji strip removed | `pass` | 33 passed | none | **SURVIVED** (F-09) |
| X6 the first duplicate registry id wins | `rows.setdefault(cells[0], cells[1])` | 33 passed | none | **SURVIVED** (F-20) |
| X7 the incident one-line `- **` form dropped | `INCIDENT_ANCHOR_RE = re.compile(r"^\*\*\d{4}-\d{2}-\d{2}\b")` | 4 failed, 29 passed | `test_fixture_harvest_exact_rows_and_provenance` | KILLED |
| X8 the `bad-utf8` whole-run refusal made a skip | `continue` | 33 passed | none | **SURVIVED** (F-13) |
| X9 the unknown-source check removed | `if False:` | 3 failed, 30 passed | `test_admission_untracked_modified_unknown_and_existing_out_untouched` | KILLED |
| X10 scout `n` equality disabled | `if False:` | 1 failed, 32 passed | `test_malformed_record_refused_by_name_and_other_rows_survive[…n-mismatch]` | KILLED |
| X11 the `agentId:` trailer kept in the payload | `if False:` | 11 failed, 22 passed | `test_fixture_harvest_exact_rows_and_provenance` | KILLED |
| X12 `wf.drift` not counted in the harvest line | `counts[…] += 0 if candidate.question_id == 'wf.drift' else 1` | 1 failed, 32 passed | `test_fixture_harvest_exact_rows_and_provenance` | KILLED |

TALLY: 36 mutants, 25 KILLED, 11 SURVIVED. The lane's 13 (m1-m9 and its four §3 controls): 13/13 KILLED on the PIN's bytes, so the
lane's table reproduces. The J1-3 brief's own m1/m2/m3 wording (it differs from the lane's m1 and m3): 3/3 KILLED. The five named
mutants: N1, N2, N4 and N5 KILLED; N3 SURVIVED in all three forms. (A first N1 attempt only removed the check, which equals L-m2; I
redefined it as the two-site mutant above and discarded that run.) The corrected copy fails exactly one lane test,
`test_boundary_deviation_requires_the_declared_delimiter` (`1 failed, 32 passed in 8.87s`), the test that asserts the narrowed drift anchor
(F-02).

### 3.5 Item 7 — gates (clone `/tmp/vj13r2/clone-ff7a671` at ff7a671, clean before and after; `/root/venv-agent-factory/bin/python`)

```
$ pytest tests/test_decide_harvest.py  (run 1)
33 passed in 8.82s
$ pytest tests/test_decide_harvest.py  (run 2)
33 passed in 9.11s
$ set ids
1 files set=87e28761f102      (tests/test_decide_harvest.py)
2 files set=16a7b628685e      (tests/test_decisions_canonical.py tests/test_decisions_ledger.py)
3 files set=70db5efe1e9b      (the two above + tests/test_no_laya_in_gates.py)
$ J1 suites, the 2-file set (the first brief's item 7), once
121 passed in 3.56s
$ J1 suites, the 3-file set (the J1-3 brief's gate), once
240 passed in 12.70s
$ python -m pyflakes scripts/decide-harvest tests/test_decide_harvest.py
pyflakes rc=0
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean
rc=0
$ python3 scripts/ap_screen.py --tests scripts/decide-harvest tests/test_decide_harvest.py
--- TEST_SCREEN over 2 path(s): 0 hits over 2 files ---
$ seed AC 4 verify_command (python -m pytest tests/test_decide_harvest.py -q)
33 passed in 8.91s
```
All gates green (SOLID). As root the tmpfs test runs, so there is no skip: 240 = the lane's `239 passed, 1 skipped`. A green gate does not
clear F-01 to F-04: mutants X1 and X2 show the suite never exercises a wrapped heading or the numbered drift form, and no test holds a
U+2028 or a moving HEAD.

## 4. THE REAL RUN, TWO PINS

Private clones, made exactly as the venue mapping says (`git clone -q --no-checkout /home/user/agent-factory /tmp/vj13r2/clone-<pin>`
then `git -C … checkout -q <pin>`); each clone's own script (sha256 `befe924d3656` in both) run twice with `--root <clone>` into fresh
files under `/tmp/vj13r2/real/`. Both clones read `git status --porcelain | wc -l` = 0 before and after.

**a78bdca** (`git rev-parse HEAD` = `a78bdca1ddb00b3008ca1d7856916d37ce7a4322`)
```
run 1 rc=3 secs=7.980353401
run 2 rc=3 secs=7.955326787
harvest: 214 rows, per question type: ap.violates_row=115, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=97, wf.drift=2
negatives: 0 (hand-labeled in J2)
sources: 252 read (incident_log=1, lane_report=148, transcript_jsonl=0, verify_report=103), 241 with no records; refused: 39 records; skipped: 0 duplicates
(run 2 prints the same three lines)
/tmp/vj13r2/real/a7-1.jsonl:214   /tmp/vj13r2/real/a7-2.jsonl:214   a7-1.err:39   a7-2.err:39
cmp-jsonl rc=0   cmp-stderr rc=0   cmp-stdout rc=0   sha256 21b0658515687a3a (both)
```
REPRODUCES the first brief's premise lines 147-149 exactly (214 rows; ap 115, v1 97, wf 2; 252 read; 241 no records; refused 39; rc 3;
39 stderr lines). The 39 refusal lines are line-for-line identical to the lane's 39 at feb26d7 (`diff` of the sorted lists: `IDENTICAL
39 lines`).

**ff7a671** (`git rev-parse HEAD` = `ff7a671ef7de584e4b16923e16b560c0f994167f`)
```
run 1 rc=3 secs=8.492097506
run 2 rc=3 secs=8.416148031
harvest: 222 rows, per question type: ap.violates_row=119, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=101, wf.drift=2
negatives: 0 (hand-labeled in J2)
sources: 256 read (incident_log=1, lane_report=148, transcript_jsonl=0, verify_report=107), 244 with no records; refused: 41 records; skipped: 0 duplicates
(run 2 prints the same three lines)
/tmp/vj13r2/real/ff-1.jsonl:222   ff-2.jsonl:222   ff-1.err:41   ff-2.err:41
cmp-jsonl rc=0   cmp-stderr rc=0   cmp-stdout rc=0   sha256 f94048dc21f4fdd0 (both)
```

Three sampled rows per pin (the first row of each harvested type, `source_ref` pasted):
```
a78bdca  ap.violates_row  answer='yes' row_id=ea8d17efd7c4a152 source_ref={"kind": "incident_log", "locator": "2026-09-23 21:3xZ — A CHECK THAT NEVER RAN COUNTS AS A PASSING CHECK (AF-AP-165; found while grading VERIFY-C2).", "path": "docs/INCIDENT-LOG.md", "source_digest": "7e3c9385345b7f192215391639c4cb9dffcb8f82bdfffbd4846a52647b97327c"}
a78bdca  v1.finding_class answer='FOLLOW-UP' row_id=4a075474cc62c355 source_ref={"kind": "verify_report", "locator": "A-1 @ FINDING INVENTORY", "path": "tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md", "source_digest": "4f4d8fb52b632a8150d203b373b790c967d7b5cd4c1a3cdbf0e87448523385d0"}
a78bdca  wf.drift         answer='yes' row_id=f90538046023f5b0 source_ref={"kind": "lane_report", "locator": "BOUNDARY DEVIATION @ document", "path": "tasks/briefs/pc/report-pc-b7.md--c439580.md", "source_digest": "2ded9f3aa8130f2e3bb49069358da0cf8893516a353c2097b1a3f8b1dbf98eab"}
ff7a671  ap.violates_row  answer='yes' row_id=381fa98345706e1c source_ref={"kind": "incident_log", "locator": "2026-09-23 23:5xZ — S0-05'S THIRD LIVE RUN FAILED ON CURL'S SPELLING, NOT ON EGRESS (AF-AP-168).", "path": "docs/INCIDENT-LOG.md", "source_digest": "f04518b867330eb073b6569713dddc95c8323b1056a614d27b42f4a26d161d0c"}
ff7a671  v1.finding_class answer='FOLLOW-UP' row_id=4a075474cc62c355 (the same row as at a78bdca, same source_ref)
ff7a671  wf.drift         answer='yes' row_id=f90538046023f5b0 (the same row as at a78bdca, same source_ref)
```

**Every difference a78bdca → ff7a671, by source** (`git diff --stat a78bdca ff7a671`: `35 files changed, 10376 insertions(+), 54
deletions(-)`; the harvest-relevant paths from `git diff --name-status`):

| source (status) | kind | rows / refusals delta | explains |
|---|---|---|---|
| `docs/INCIDENT-LOG.md` (M) | incident_log | `ap.violates_row: 109 -> 112 (+3)`: the new entries AF-AP-168 (`2026-09-23 23:5xZ — S0-05'S THIRD LIVE RUN FAILED ON CURL'S SPELLING…`) and AF-AP-166 + AF-AP-167 (one heading naming two ids) | ap +3 |
| `tasks/briefs/laya/VERIFY-J1-0-R6-report.md` (A) | verify_report | `ap.violates_row: 0 -> 1 (+1)`, `v1.finding_class: 0 -> 4 (+4)`, `(bad-title): 0 -> 2 (+2)` at `:280` (`- **F-3 INFO (KNOWN V-18) — …`) and `:287` (`- **F-5 INFO (confirmations).**`), both correct qualifier refusals | ap +1, v1 +4, refused +2, verify +1 |
| `tasks/briefs/pc/report-pc-verify-j1-0-r6.md--c6dcd61.md` (A) | verify_report | 0 rows, 0 refusals | verify +1, no-records +1 |
| `tasks/briefs/pc/report-pc-verify-s0-02.md--a78bdca.md` (A) | verify_report | 0 rows, 0 refusals | verify +1, no-records +1 |
| `tasks/briefs/s0-02-support/VERIFY-S0-02-report.md` (A) | verify_report | 0 rows, 0 refusals | verify +1, no-records +1 |
| `tasks/briefs/pc/patch-*.diff`, `tasks/briefs/pc/pc-verify-*.md` (A/M), `transcripts/pc/*.md`, `transcripts/sandbox/chat-*.md` | not in the kind table (briefs, patches, the declared-excluded digests) | none | nothing |

Sum: rows 214 + 3 + 1 + 4 = 222 ✓; ap 115 + 4 = 119 ✓; v1 97 + 4 = 101 ✓; verify_report 103 + 4 = 107 ✓; read 252 + 4 = 256 ✓; no
records 241 + 3 = 244 ✓; refused 39 + 2 = 41 ✓; lane_report 148 = 148 ✓. No a78bdca row id is missing at ff7a671.

**What the real run SHOULD read under the frozen contract** (the corrected copy on the same clone, `/tmp/vj13r2/real/fix-ff.*`):
```
harvest: 224 rows, per question type: ap.violates_row=119, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=102, wf.drift=3
sources: 256 read (incident_log=1, lane_report=148, transcript_jsonl=0, verify_report=107), 243 with no records; refused: 40 records; skipped: 0 duplicates
--- stderr lines only in the pinned run:
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R5-report.md:466 (bad-title)
rows only in the pinned run: 0 | rows only in the corrected run: 2
  + wf.drift ans=yes path=tasks/briefs/s0-01-p5c-support/P5c-report.md loc='BOUNDARY DEVIATION @ DEVIATIONS (flagged loudly, first-class'
  + v1.finding_class ans=BLOCKER path=tasks/briefs/laya/VERIFY-J1-0-R5-report.md loc='V5-05 @ FINDING INVENTORY (no severity filter; V5- ids are t'
```
With the all-asterisks reading of F-19 as well: `harvest: 225 rows … v1.finding_class=103, wf.drift=3` and `refused: 39 records` (the
`VERIFY-REPIN-a-R1-report.md:550 (bad-class)` refusal becomes a CONTRACT-DEFECT row). Every type stays below KC-J7's 200 under every
reading (max 119), so the KC-J7 verdict is unchanged. The printed numbers are not the contract's numbers.

Known and out of scope, confirmed at both pins (SOLID): 0 `b1`/`b2`/`d1` rows; 0 PC `v1.finding_class` rows, with
`report-pc-verify-m3.md--e776dd0.md` refused 10 times as `no-title-column`; all incident rows `action_kind=report`,
`action_target=docs/INCIDENT-LOG.md` (109 at a78bdca, 112 at ff7a671).

## 5. FINDING INVENTORY (no severity filter; every item reproduced through the real pinned script unless marked)

**F-01 BLOCKER — a wrapped heading or title loses a line** (`scripts/decide-harvest:230-248`, `_heading_text`). SOLID.
- Mechanism: `joined` holds the anchor-line piece and each later line that has no closing `**` (`:246-247`). When the close is found at
  offset k, `prefix = joined[:-1] if offset else []` (`:244`) drops the LAST collected piece. So a 2-line heading keeps only its second
  line, and a 3-line heading loses its middle line.
- Contract: `tasks/briefs/laya/J1-3-brief.md:76` ("the next `**`, which may sit on a later line") and `:89` ("it may wrap; 10-line limit
  as in 4.1").
- Canonical path: the real run refuses `tasks/briefs/laya/VERIFY-J1-0-R5-report.md:466 (bad-title)` (`V5-05 BLOCKER`) at BOTH pins. That line is
  `- **V5-05 BLOCKER — R5-4: a node property … and shifts a` / `  literal block's line map.** SOLID.`, a valid BLOCKER finding whose bold
  title wraps once (the wrap census over both pins' corpus finds exactly this one wrapped anchor). Scratch: I-k, I-l, V-k, V-l (§3.2).
- Material: the KC-J7 line is wrong (`v1.finding_class=101`, should be 102; `refused: 41`, should be 40); a valid BLOCKER is reported
  malformed; rows are minted with a line missing from their state (V-l `"part one part three"`, I-l); ap rows are lost (I-k, I-l).
- Discriminator: `g1_incident.py` / `g2_verify.py` cases I-k, I-l, V-k, V-l. The corrected join yields the contract rows, and on the
  real corpus it harvests V5-05. Mutant X1 (no wrap at all) survives the suite: no test holds a wrapped heading.
- Ownership: in-boundary (`scripts/decide-harvest` + `tests/test_decide_harvest.py`).
- Suggested fix: collect every piece up to the closing line (`pieces.append(piece)` for each offset without a close; return
  `" ".join(pieces + [piece[:close]])`); add 2- and 3-line wrap tests for both the incident heading and the bullet title.

**F-02 BLOCKER — the drift anchor is narrower than the contract, and one real deviation is silently skipped**
(`scripts/decide-harvest:46-50`, `BOUNDARY_RE`; the lane test `tests/test_decide_harvest.py:466-477`, `test_boundary_deviation_requires_the_declared_delimiter`). SOLID; the P5c instance is UNSURE
only on reading "followed by" as whitespace-tolerant, the reading the implementation itself uses (`\s*` at `:48`).
- Mechanism: the bullet alternative is `- \*\*BOUNDARY DEVIATION\*\*` and then a SECOND delimiter is required. The contract anchor has no
  closing `**` inside it.
- Contract: `tasks/briefs/laya/J1-3-brief.md:107` (`^(?:- \*\*|\d+\. )BOUNDARY DEVIATION\b` followed by `—`, `:` or `**`);
  `tasks/laya-j1-breakdown.md:19` ("never a silent skip").
- Canonical path: at both pins `tasks/briefs/s0-01-p5c-support/P5c-report.md:13` (`- **BOUNDARY DEVIATION — \`tests/conftest.py\` was
  patched** …`) yields no row and no refusal. The only two `wf.drift` rows come from ONE deviation committed twice:
  `tasks/briefs/s0-02-support/B7-report.md` and `tasks/briefs/pc/report-pc-b7.md--c439580.md` are byte-identical (`cmp rc=0`). The J1-3
  brief's own premise counted 3 boundary-deviation record lines (`J1-3-brief.md:265`); the lane printed 2 and never explained the gap.
- Material: a contract record is silently dropped, and the KC-J7 `wf.drift` number (the D-047 drift-hawk's input) reads 2 rows for 1
  decision while missing a second decision.
- Discriminator: L-c (`- **BOUNDARY DEVIATION: touched scripts/x.py**`: `:` directly after DEVIATION, a contract anchor under every
  reading) yields no row; so does L-c3 (DEVIATION followed by `**`). The contract's own regex yields a row for L-c, L-c2 and L-c3, and
  `wf.drift=3` on the real corpus. The lane test `test_boundary_deviation_requires_the_declared_delimiter` asserts the narrowed reading and
  is the only lane test the corrected copy fails. Mutant X2 (the numbered form removed) survives: the only form that yields real rows is
  untested.
- Ownership: in-boundary. Suggested fix: `^(?:- \*\*|\d+\. )BOUNDARY DEVIATION\b\s*(?:—|:|\*\*)`. Invert the lane test for
  `- **BOUNDARY DEVIATION** touched …` (DEVIATION IS followed by `**`), keep a no-delimiter negative (`1. BOUNDARY DEVIATION touched`),
  and add a numbered-form test and a `—`-inside-the-bold test.

**F-03 BLOCKER — `HEAD` is re-resolved in every git call, so rows can carry bytes read after admission from a later commit**
(`scripts/decide-harvest:141` `_git(root, "ls-tree", … "HEAD")`, `:152`, `:787`, `:790-791`). SOLID on mechanism and reproduction; UNSURE on how often a real run overlaps a
commit (not measured; a run takes about 8.5 s).
- Mechanism: `_tree_paths` and `_head_blob` name the symbolic ref `HEAD` in each subprocess. After admission, `main` re-reads the tree
  (`:787`, used for `paths`) and the registry (`:790-791`, used for `row_title`) from whatever commit `HEAD` names then.
- Contract: `tasks/briefs/pc/pc-verify-j1-3.md:23` ("no row can carry bytes read after admission"); `J1-3-brief.md:39-40` ("reads source
  bytes ONLY from its `HEAD` commit"); `seeds/seed-laya-j1-v1.yaml:94` (replay of the same committed sources gives the identical ledger).
- Canonical path, no shim: `git update-ref` flips `HEAD` between two real commits while the real script runs. 45 of 300 runs exit 0 with
  `action_excerpt='AF-AP-2 follow-up vA' row_title='malformed record silently dropped vB'`.
- Material: bytes read after admission land in a row. That row matches neither commit, so a later harvest of either commit writes a
  second row for the same decision, with exit 0 and no warning. The default `--root` is the script's own repository, the live shared tree,
  whose HEAD moves (the R2 brief says so at its line 41).
- Discriminator: the deterministic control (a PATH `git` wrapper commits at the harvester's second `ls-tree`) gives
  `['MIXED title vA / row_title vB']`, while the no-shim control gives `['consistent']`. The corrected copy, with HEAD resolved once, gives
  0 MIXED in 300 racer runs.
- Ownership: in-boundary. Suggested fix: resolve `git rev-parse --verify HEAD^{commit}` once, use `ls-tree <rev>` and
  `cat-file blob <rev>:<path>` everywhere, including the registry; add a test that moves HEAD between admission and the registry read.

**F-04 BLOCKER — `str.splitlines()` is the line model (AF-AP-132)** (`scripts/decide-harvest:303` `lines = source.text.splitlines()`, `:375`, `:515`, and `:642`
`enumerate(source.text.splitlines(), 1)`, the registry's exact greppable signature, `docs/INCIDENT-LOG.md@ff7a671:561` `AF-AP-132`, line 563 at HEAD efda000). SOLID on mechanism; UNSURE
on materiality at this pin (today's printed output is unchanged).
- Mechanism: `splitlines()` also breaks on U+2028, U+2029, U+0085, `\x0b`, `\x0c` and `\x1c`-`\x1e`. Git and the contract count `\n`
  lines.
- Contract: `J1-3-brief.md:67` (`<line>` = "the 1-based line of the anchor in the committed blob") and the anchors "a line beginning …"
  (`:75`, `:107`); `tasks/briefs/pc/pc-verify-j1-3.md:28-29` ("never a row"; "A row minted from prose is a blocker").
- Canonical path, scratch repos:
  - V-m: a BLOCKER row is minted from a blob line that begins `Context sentence.`; I-j and L-k do the same for the other markdown grammars.
  - V-n: one U+2028 inside a class-table cell silently drops that row and every later row of the table (rc 0, `refused: 0`).
  - T-g: a VALID JSONL record is refused `bad-json` at `:6` and at `:7`, in a file of 6 git lines, plus `no-result`.
  - Real corpus: one U+2028 at `tasks/briefs/laya/VERIFY-J1-1-report.md:243` (the row `U+2028, U+0085`), in a non-class table. Every later line of that file is
    numbered one high; the file yields no rows or refusals at either pin.
- Material: rows minted from prose, valid rows silently lost, and refusal evidence that points at wrong or nonexistent lines. The
  character already occurs in a committed verify report.
- Discriminator: V-m, V-n and T-g. The corrected copy (`\n` lines) gives the contract outcome in each and changes nothing else on the
  real corpus.
- Ownership: in-boundary. Suggested fix: one `_lines(text)` helper that splits on `\n` only (dropping the final empty piece and a
  trailing `\r`), used at all four sites; tests with U+2028 in a table cell, mid-line before an anchor, and inside a JSONL string.

**F-05 CONTRACT-DEFECT — a corrupt ledger is reported as clean duplicate skips, with exit 0** (`scripts/decide-harvest:823-827`, `except DecisionStateError as exc`; the rule
it follows, `J1-3-brief.md:145-147`; `src/agent_factory/decisions/ledger.py:452` `append` calls `replay`, which raises the SAME reason
`decision-row-duplicate` for a row id that appears twice in the file, `:608-611`). SOLID. Returned to the coordinator for an explicit
amendment.
- Canonical path:
  - Two CONCURRENT harvests into one fresh `--out` leave 32 of 40 ledgers corrupt. Both runs exit 0 with `harvest: 1 rows`.
  - A third harvest into such a ledger prints `harvest: 0 rows`, `skipped: 10 duplicates`, rc 0, and one repeated id in stderr. The ledger
    holds 1 of the 10 rows.
  - A hand-duplicated row gives the same result (identity (e)).
- Effect: falsified evidence (exit 0 is defined as "no refusal"; the skipped rows are not in the ledger) and silent data loss. Any later
  harvest into that ledger reports success forever.
- Why CONTRACT-DEFECT and not BLOCKER: the frozen §5 text literally says to count `decision-row-duplicate` from `ledger.append` as a skip.
  The trigger is a corrupt ledger, reached by violating J1-2's single-writer precondition (`ledger.py:439` "Single writer by contract (no
  lock)") that nothing enforces.
- Suggested amendment: count a skip only when `exc.detail == row["row_id"]`. Make any other `append` refusal a whole-run failure with a
  named `harvest-output-*` line. Take an exclusive lock on `--out` for the run.

**F-06 FOLLOW-UP — the admission check can hang forever on a FIFO swapped in mid-check** (`scripts/decide-harvest:156-163`, `_regular_worktree_bytes`). SOLID.
- R4 racer: 72 of 300 runs hit the 10 s timeout, the process in kernel wait `wait_for_partner`.
- Contract `J1-3-brief.md:62` says a "non-regular file" is refused. Reaching the hang needs a concurrent adversarial swap.
- Fix: `os.open(O_RDONLY|O_NOFOLLOW|O_NONBLOCK)` and `fstat` `S_ISREG` on the fd, the J1-2 ledger's own pattern
  (`ledger.py:519-540`).

**F-07 FOLLOW-UP — the HEAD-after-admission test is blind to content** (`tests/test_decide_harvest.py:300-356`). SOLID.
- Mutant B-m5b survives: parse the worktree text after admission, keep the HEAD digest.
- Missing test: after the swap, assert a content-bearing field, for example the `wf.drift` locator `BOUNDARY DEVIATION @ Build` (not
  `@ Changed`).

**F-08 FOLLOW-UP — the named mutant N3 survives in all three forms.** SOLID.
- `no-title-column` (a contract refusal, `J1-3-brief.md:93-94`, behind 27 real-run refusals), `bad-table-row`, and the registry's exact
  header rule have no test.
- Missing tests: a class table with no `finding…`/`what` column; a short row; a registry table with another header.

**F-09 FOLLOW-UP — untested grammar branches** (probe mutants X1-X5 survive). SOLID.
- X1 wrapping, X2 the numbered drift form, X3 the ` (<qualifier>)` class form (the real corpus relies on it), X4 the absolute-path branch,
  X5 the emoji strip.
- One test each.

**F-10 FOLLOW-UP — Unicode-aware `\d`, `re.IGNORECASE` and `.upper()` admit lookalike anchors and ratings**
(`scripts/decide-harvest:41` `INCIDENT_ANCHOR_RE`, `:46-50`, `:486`, `:498`). SOLID.
- I-h (fullwidth date), L-d (dotless ı) and L-e (Arabic-Indic digit) each mint a row; L-i accepts `Hıgh`; L-m accepts `-- HIGH` (any
  leading punctuation is stripped, not only an emoji).
- No real-corpus instance. The rows are faithful to their text, so I do not call them "minted from prose".
- Fix: `[0-9]` and `re.ASCII`.

**F-11 FOLLOW-UP — a deeply nested JSON line crashes the run** (`scripts/decide-harvest:643-648`, `:686-689` catch only
`JSONDecodeError`). SOLID.
- T-l and T-m: `RecursionError`, rc 1, no harvest line. A discovery run leaves 7 rows in the ledger.
- Contract: `J1-3-brief.md:127` ("not valid JSON → refused (`bad-json`)"). No transcript JSONL is committed today.
- Fix: also catch `RecursionError` and `ValueError` and refuse by name.

**F-12 FOLLOW-UP — `--out` failures are misreported** (`scripts/decide-harvest:813-834` wraps `append` in the `make_row` handler). SOLID.
- A directory `--out` reports every SOURCE record as `harvest-source-unparseable: …:<line> (state:decision-ledger-not-regular)`, rc 3.
- A missing parent directory gives a `FileNotFoundError` traceback, rc 1.
- The contract sanctions `state:<code>` only for `make_row` (`J1-3-brief.md:71-72`).
- Fix: check `--out` up front; exit 64 or a named refusal.

**F-13 FOLLOW-UP — `bad-utf8` stops the whole run with exit 3 and no stdout** (`scripts/decide-harvest:183-186`). SOLID.
- Exit 3 is defined as "the rows of every other record ARE appended" (`J1-3-brief.md:147`); here no row is appended.
- Non-UTF-8 sources are undefined by the contract; the branch is untested (X8 survives).

**F-14 FOLLOW-UP — refusal order** (`scripts/decide-harvest:170-182`, `if requested:` then `unknown`). SOLID behaviour; UNSURE reading of `J1-3-brief.md:63` ("report the
FIRST refusal in sorted path order").
- Every unknown path is refused before any committed check. Identity (i): rc 5 for `zz/unknown.txt`, while the first path in order is
  the untracked `tasks/briefs/x/A-report.md` (rc 4). Nothing is written either way.

**F-15 FOLLOW-UP — `paths` depends on where the checkout lives** (`scripts/decide-harvest:365-366`, `candidate.startswith(str(root) + os.sep)`). SOLID.
- An absolute path under `--root` is relativized; under any other root it is dropped. Identity (d): the same commit harvested at two roots
  writes F-30 twice.
- `J1-3-brief.md:97-98` counts only tokens whose `<path>` is a HEAD blob, which is never absolute.
- The census finds 0 such tokens in the real verify reports at ff7a671, so the pinned output is unaffected.

**F-16 FOLLOW-UP — quadratic `MARKDOWN_HEADING_RE`** (`scripts/decide-harvest:51`). SOLID.
- A heading with a long whitespace run: n=5000 0.39 s, 10000 0.92 s, 20000 3.36 s. Hostile only.

**F-17 FOLLOW-UP — `append` replays the whole ledger per row** (`src/agent_factory/decisions/ledger.py:452`, a J1-2 design). INFO-level.
- The real run takes 8.5 s for 222 rows and grows quadratically with the corpus. The harvester could replay once.

**F-18 INFO — rows the grammar mints by construction** (design, not a deviation; for J2's labelling).
- I-c and L-b: a negation inside the anchor gives a `yes` row.
- V-c: a word as a finding id. V-o: an anchor inside a code fence. V-j2: a split row whose second half has the header's cell count.
- V-p: an unescaped pipe truncates the title. V-q: an empty title gives a BLOCKER row with `title: ""`.
- `_nearest_heading` (`:251-256`) also reads `#` lines inside code fences as headings.

**F-19 FOLLOW-UP (UNSURE reading) — the class cell's asterisks** (`scripts/decide-harvest:352` `cell.strip().strip("*").strip()` strips
only the ends; `J1-3-brief.md:91` says "The CLASS cell (asterisks stripped)").
- The real run refuses `tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md:550 (bad-class)`, cell `'**CONTRACT-DEFECT** (part of F1)'`.
- With all asterisks removed it is a valid CONTRACT-DEFECT record: `harvest: 225 rows … v1.finding_class=103` and `refused: 39` together
  with F-01 and F-02. It is a blocker if the coordinator reads the rule that way.

**F-20 INFO** — a duplicated registry id: the last title wins silently (I-m; X6 survives). The contract is silent.

**F-21 INFO** — the two B7 reports are byte-identical, so the real `wf.drift=2` is one decision counted twice. Identity includes `path` by
design (`ledger.py:85-97`).

**F-22 INFO — the lane report misstates its refusals.**
- It explains all 9 `bad-title` refusals as "parenthetical qualifiers" (`tasks/briefs/laya/J1-3-report.md:193`). That holds for 4 of them
  (R4 :749, :751; R5 :505, :525).
- R4 :760, :762, :764 and :765 put the title OUTSIDE the bold (`- **V-15 INFO** — …`).
- R5 :466 is valid (F-01).
- Its `bad-class` explanation "bold `CONTRACT-DEFECT`" is F-19.

**F-23 INFO** — the lane's m1 and m3 differ from the J1-3 brief's m1 and m3. All four are KILLED (§3.4).

**F-24 INFO** — the known limits are confirmed at both pins (§4).

**F-25 INFO** — `/root/venv-agent-factory` is Python 3.11.15, while the seed says ">= 3.12" (`seeds/seed-laya-j1-v1.yaml:69`). The
quartet is blind to the suffix-less script (P-5).

**F-26 INFO** — the 10-line window is the anchor line plus 9 (`:237`, `range(10)`). "Within 10 lines" is ambiguous by one line.

Reproduced vs static: every F-item above was run through the real script except F-17 (read from `ledger.py`; timing measured on the real
run) and the mechanism sentences, which I re-derived from the source lines cited. Deliberately skipped: the full `tests/` suite (seed AC
10, other components), any PC run, a run with `--root /home/user/agent-factory` (forbidden; F-15 was measured by census instead), and the
real-world frequency of F-03.

## 6. GATE RECOMMENDATION

The blocking predicate, per blocker:

| finding | 1 contract-mapped | 2 canonical path at the PIN | 3 material | 4 discriminator | 5 in-boundary |
|---|---|---|---|---|---|
| F-01 heading join (`_heading_text`) | `J1-3-brief.md:76`, `:89` | real run (`VERIFY-J1-0-R5-report.md:466`) + scratch | KC-J7 line wrong; valid BLOCKER refused; corrupted row state | I-k/I-l/V-k/V-l; corrected join; X1 survives | `scripts/decide-harvest:230-248` |
| F-02 drift anchor | `J1-3-brief.md:107`; breakdown `:19` | real run (`P5c-report.md:13` silently skipped) + scratch | a contract record silently dropped; KC-J7 `wf.drift` wrong | L-c/L-c3; contract regex gives wf.drift=3 | `:46-50` + the lane test `:466-477` |
| F-03 HEAD re-resolved | `pc-verify-j1-3.md:23`; `J1-3-brief.md:39-40`; seed `:94` | real script, real commits, no shim: 45/300 | bytes read after admission in a row; replay not a function of one commit | shim control; corrected copy 0/300 | `:141`, `:152`, `:787-791` |
| F-04 splitlines | `J1-3-brief.md:67`, `:75`, `:107`; `pc-verify-j1-3.md:28-29`; AF-AP-132 | real script on scratch repos; the character exists in the real corpus | rows minted from prose; valid rows silently lost; false `<line>` evidence (UNSURE at this pin: today's output unchanged) | V-m/V-n/T-g; corrected copy | `:303`, `:375`, `:515`, `:642` |

GATE RECOMMENDATION: NOT-READY — blockers F-01 (`scripts/decide-harvest:244`, `prefix = joined[:-1]`), F-02 (`scripts/decide-harvest:46-50`, `BOUNDARY_RE`, and
`tests/test_decide_harvest.py:466-477`), F-03 (`scripts/decide-harvest:141,152,787-791`), F-04 (`scripts/decide-harvest:303,375,515,642`);
CONTRACT-DEFECT F-05 returned for amendment. All four blockers were reproduced through the real pinned script; F-01 and F-02 also on the
real corpus at both pins. Not reproduced, and so UNSURE: how often a real run overlaps a commit (F-03), and whether synthetic-only row
minting counts as material for F-04 at this pin.

The repair fits one focused round (D-031), all inside the J1-3 boundary. The scratch corrected copy that served as the discriminator
changed 38 lines and failed only the one lane test that encodes F-02. Its tests should cover F-07, F-08 and F-09 in the same round.

## DISCREPANCIES

- D-1 (SOLID): the shared tree's HEAD moved from bfc7687 (the R2 premise) to efda000 (this brief's commit). The boundary diff
  ff7a671..HEAD stays 0 lines, so no item changed.
- D-2 (SOLID): the J1-3 brief's premise counted `boundary-deviation record lines={'lane': 3}` (`J1-3-brief.md:265`). The lane printed
  `wf.drift=2` and did not explain the difference, which `J1-3-brief.md:283-284` required. The missing record is P5c (F-02).
- D-3 (SOLID): the lane's refusal classification (`J1-3-report.md:192-194`) is wrong for 5 of the 9 `bad-title` lines and for the `bad-class`
  line at `VERIFY-REPIN-a-R1-report.md:550` (F-22, F-19). Its self-attack #2 (`J1-3-report.md:214`, "broad markdown patterns could mint
  rows from prose … Ruled out") is refuted by F-04 and by F-01's V-l.
- D-4 (SOLID): the first brief's item 7 names the 2-file J1 set, and the J1-3 brief's gate names 3 files. I ran both: 121 and 240
  passed as root. The lane's `239 passed, 1 skipped` equals 240 on a non-root host.
- D-5 (SOLID): the first pass cited the J1-3 build brief's premise files (the decisions package), not its own brief's premise block (G-7).
- D-6, my own process (SOLID):
  - The R4/R5 racer outlived the tool's 600 s foreground cap and was moved to the background by the harness. Each harvester run inside it
    was bounded by its own 10 s timeout, and I waited for the completion notice before reading the result.
  - The porcelain committer race reused out-file names from an earlier round (the 7 `rc=4 consistent` and 2 double-row outcomes). I
    discarded them.
  - My first N1 mutant equalled L-m2; I redefined it as a two-site mutant.
- D-7 (SOLID): the free space on `/` was 2.0 GB at authoring and 1.3 GB at the peak of this lane. All scratch is removed at the end.

## NOT-done

- No PC run; the venue is the sandbox by the brief. No run with `--root /home/user/agent-factory` (the shared tree is forbidden), so
  F-15's real-corpus exposure was measured by census (0 tokens), not by a run.
- F-03: the real-world frequency of a commit overlapping a harvest was not measured.
- The seed's other acceptance criteria were not re-run, including the full `tests/` suite (AC 10). Only AC 4 and the J1 suites were run.
- No `/bug-echo` run and no AF-AP registry row. This lane may write only this report. The coordinator owns `docs/INCIDENT-LOG.md`:
  F-01, F-02, F-03 and F-05 are new classes, and F-04 is a new instance of AF-AP-132.
- The scratch corrected copy was a discriminator only. It is not proposed as the patch, and it is deleted with the rest of
  `/tmp/vj13r2/`.
- No DORMANT or reachability claim is made. The quartet cannot see the suffix-less script (P-5); every claim here rests on reading
  `scripts/decide-harvest` and running it.
- Report lint (two rounds of `fix:` hints, the bound is three): round 1 `report_lint: 47 refs — OK 25, NEAR 2, MISS 15, UNCHECKABLE 5,
  UNRESOLVED 0 (worktree)`. Two of the MISS lines were real errors, both now corrected: an I-d cite that named the fixture copy's line as the
  real log's, and the AF-AP-132 row cited at its ff7a671 line (561) where HEAD has 563. Round 2 `report_lint: 46 refs — OK 39, NEAR 2,
  MISS 0, UNCHECKABLE 5, UNRESOLVED 0 (worktree)`. The floor `--min-refs 15` holds.
