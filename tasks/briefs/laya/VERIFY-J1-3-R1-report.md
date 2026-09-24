# VERIFY-J1-3-R1 — report (task #209's independent verify; sandbox adversarial verifier, Opus 5.5)

Status: DONE 2026-09-24. GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS (§10). No BLOCKER, no CONTRACT-DEFECT; seven
FOLLOW-UPs, twelve INFO items (§9).

Brief: `tasks/briefs/laya/VERIFY-J1-3-R1-brief.md`. PIN 0d62801. Scratch `/tmp/vj13r1/`.

## 1. PREMISE (item 1)

Measured 2026-09-24T03:11:27Z, sandbox, uid 0.

```
$ date -u +%Y-%m-%dT%H:%M:%SZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf; git rev-parse --short HEAD; id -u
2026-09-24T03:11:27Z
a923be5
d1463bd
0
$ git diff --stat 0d62801 origin/claude/soundbox-kit-migration-iz1jwf -- scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions src/agent_factory/decisions | wc -l
0
$ git diff --stat f772bfc 0d62801 -- scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions src/agent_factory/decisions
 scripts/decide-harvest       | 159 ++++++++----
 tests/test_decide_harvest.py | 569 ++++++++++++++++++++++++++++++++++++++++++-
 2 files changed, 680 insertions(+), 48 deletions(-)
971e38803587 918 scripts/decide-harvest
bb0187044a6a 1144 tests/test_decide_harvest.py
(tokens) 1 decision-row-duplicate / 1 harvest-output-invalid / 1 harvest-output-source-conflict / 1 harvest-source-uncommitted /
         1 harvest-source-unknown / 3 harvest-source-unparseable
(os.open count) 2
$ git diff --stat 0d62801 -- scripts/decide-harvest tests/test_decide_harvest.py tests/fixtures/decisions src/agent_factory/decisions | wc -l
0
$ git hash-object scripts/decide-harvest | cut -c1-12; git hash-object tests/test_decide_harvest.py | cut -c1-12
971e38803587
bb0187044a6a
```

HEAD moved from a923be5 (authoring) to d1463bd, then f172024 (the brief commit and a ledger commit). Neither touches the four
target paths: the working tree and HEAD are byte-identical to 0d62801 on them. No item changes. Premise HOLDS.

## 2. METHOD

- Scripts under test, extracted by `git archive` (the shared tree is never run against a scratch mutation):
  `/tmp/vj13r1/x-0d62801/scripts/decide-harvest` (sha256 `7022dd819436`, blob `971e38803587`, `cmp` equal to the shared tree's file) and the
  unfixed `/tmp/vj13r1/x-f772bfc/scripts/decide-harvest` (sha256 `befe924d3656`) as the red control. `src/` is identical at both pins
  (`diff -r` empty).
- Harness `/tmp/vj13r1/h/h.py`: copy the pinned fixture tree, apply the edit, `git init` + commit (fixed author and date), run the REAL
  script as a subprocess with `--root <scratch repo>`, read the ledger with the pinned `ledger.replay`.
- Python `/root/venv-agent-factory/bin/python` = 3.11.15. strace is present; `cap_mknod` is in the bounding set (device sources ran).
- Code intel: the pack (`/tmp/vj13r1/pack.md`, 174 lines) is blind to the suffix-less script, as R2's P-5 said: `graft skeleton` reads
  "no definitions indexed for this file", GitNexus `impact` returns `risk: UNKNOWN`. code-review-graph names `main` as the one caller of
  `_claim_output`. Every claim below rests on reading the script and running it.
- Where each contract line lives in the PIN script (each line read this session):

| contract line | file:line | the code there |
|---|---|---|
| R3 the one resolve | `scripts/decide-harvest:145` | `"HEAD^{commit}"` |
| R3 the admission comparison | `scripts/decide-harvest:204` | `_head_blob(root, commit, path)` |
| S1 one open, then the type check | `scripts/decide-harvest:172`, `scripts/decide-harvest:176` | `os.O_NOFOLLOW`; `stat.S_ISREG` |
| R4 the one splitter | `scripts/decide-harvest:254` | `def _lines` |
| R1 / D-064 (3) the window | `scripts/decide-harvest:269` | `range(10)` |
| R6 / D-064 (2) | `scripts/decide-harvest:382` | `cell.replace("*", "")` |
| R5 (a) the claim open and lock | `scripts/decide-harvest:804`, `scripts/decide-harvest:808` | `os.O_RDWR`; `fcntl.LOCK_NB` |
| R5 (b) the one replay | `scripts/decide-harvest:811` | `replay(path)` |
| R5 (c) the own-id skip | `scripts/decide-harvest:897` | `exc.detail == row["row_id"]` |
| R5 (c) an `append` `OSError` | `scripts/decide-harvest:903` | `_errno_name(exc)` |
| `append` replays per row, writes `O_APPEND` | `src/agent_factory/decisions/ledger.py:452`, `src/agent_factory/decisions/ledger.py:470` | `replay(path_str)`; `os.O_APPEND` |

## 3. ITEM 2 — EACH CONTRACT LINE, ATTACKED WITH NEW SHAPES

### 3.1 R1 wrapped headings (`/tmp/vj13r1/h/r1r2.py`, 2026-09-24T03:20:22Z; each shape appended to the fixture file, that file harvested alone)

Contract: §4.1 "the next `**`, which may sit on a later line; no closing `**` within 10 lines → refused"; R1 "every line's piece is kept,
joined with one space and whitespace-collapsed"; D-064 (3) the window is the anchor line plus nine.

| shape | PIN 0d62801 (pasted) | f772bfc | verdict |
|---|---|---|---|
| I-2wrap-tab (continuation indented by a tab) | rc 0, 2 new rows, locator `2026-02-02 — AF-AP-1 first AF-AP-2 second` | 1 row `AF-AP-2 second` | ✓ contract |
| I-3wrap | 2 rows `…AF-AP-1 one two three AF-AP-2` | `one three` (middle lost) | ✓ |
| I-5wrap | 2 rows `…AF-AP-1 a b c d e AF-AP-2` | `a b c e` | ✓ |
| I-mixed-indent (tab + spaces) | `…AF-AP-1 x y z` | `x z` | ✓ |
| I-trailing-spaces (spaces before the newline and after the close) | `…AF-AP-1 x y` | no row | ✓ |
| I-eof-unterminated (no close, file ends) | rc 3, the scratch log's line 20 `(unterminated-heading)` | same | ✓ |
| I-eof-close-no-nl (close on the last line, no final newline) | row `…AF-AP-1 closes at EOF` | no row | ✓ |
| I-10lines (close on the anchor's 10th line) | row `… l1 l2 … l9 l10` | `l9` lost | ✓ window = anchor + 9 |
| I-11lines (close on the 11th line) | rc 3, line 20 `(unterminated-heading)` | same | ✓ |
| I-crlf-wrap (`\r\n` endings) | 2 rows `…AF-AP-1 crlf one crlf two AF-AP-2` | 1 row `crlf two AF-AP-2` | ✓ |
| I-blank-inside (a blank line inside the bold) | 2 rows `…before blank after blank AF-AP-2` | same (the dropped piece was the blank) | ✓ literal ("the next `**`") |
| I-list-after (unclosed bold, next line `- **2026-02-12 — AF-AP-2 next**`) | 2 new rows: AF-AP-1 with locator `2026-02-11 — AF-AP-1 unterminated -`, AF-AP-2 `2026-02-12 — AF-AP-2 next` | AF-AP-1 dropped SILENTLY | by construction (INFO-1) |
| V-5wrap | `F-21 BLOCKER` title `p1 p2 p3 p4 p5` | `p1 p2 p3 p5` | ✓ |
| V-mixed-indent | `F-22 INFO` `a b c` | `a c` | ✓ |
| V-trailing-spaces | `F-23 INFO` `a b` | rc 3 `bad-title` | ✓ |
| V-eof-unterminated | rc 3, the scratch report's line 10 `(unterminated-heading)` | same | ✓ |
| V-blank-inside | `F-25 BLOCKER` `before after` | same | ✓ literal |
| V-wrap-dash-on-2nd (`- **F-29 BLOCKER` / `— title on line two**`) | `F-29 BLOCKER` `title on line two` | rc 3 `bad-title` | ✓ (the joined heading holds `F-29 BLOCKER — `) |
| V-close-triple (`*emph` / `wrapped***`) | `F-31 INFO` `*emph wrapped` | rc 3 `bad-title` | ✓ literal |
| V-list-after (unclosed `- **F-26 BLOCKER — unterminated`, next line `- **F-27 INFO — second**`) | rc 0: `F-26 BLOCKER` title `unterminated -` AND `F-27 INFO` `second` | rc 3 `:10 (bad-title)` | by construction (INFO-1) |
| V-prose-bold-after (unclosed F-28, next line `prose naming AF-AP-2 then **bold** word`) | rc 0: `F-28 BLOCKER` title `unterminated prose naming AF-AP-2 then` plus an `ap.violates_row` row for AF-AP-2 | rc 3 `bad-title` | by construction (INFO-1) |

R1 holds on every wrap shape. The last three rows are new behaviour with R1: an unclosed bold now closes at the next `**` substring,
even the opening of the next list item or of an unrelated bold word, so a malformed record that f772bfc refused (or dropped silently)
becomes a row. That is the literal contract (§4.1 "the next `**`"; R1 "the first closing `**` in the window"). It is a grammar-by-
construction row of the F-18 class that the builder's §8 item 3 does not list.

### 3.2 R2 the drift anchor (same script; each line replaces the fixture's `- **BOUNDARY DEVIATION** — touched an extra fixture`, its continuation line kept)

| shape | expect row | PIN | f772bfc |
|---|---|---|---|
| `- **BOUNDARY DEVIATION — x` / `: x` / `** x` | yes | 1 row each, observed `x because the contract required it` | 0 (silent) |
| `- **BOUNDARY DEVIATION**: x` | yes | 1 row | 1 row |
| `– x` (en dash) / `- x` (hyphen) / `; x` / no delimiter | no | 0 | 0 |
| `- **BOUNDARY DEVIATIONS: x` | no | 0 (`\b`) | 0 |
| lower case `- **boundary deviation: x`, mixed `- **BoUnDaRy DeViAtIoN — x` | yes (D-064 (1)) | 1 row each | 0 |
| mid-line `Note - **BOUNDARY DEVIATION: x`; table cell `\| - **BOUNDARY DEVIATION: x** \|` | no | 0 | 0 |
| `10. BOUNDARY DEVIATION: x`, `123. BOUNDARY DEVIATION — x` | yes | 1 row each | 1 row each |
| `1. BOUNDARY DEVIATION x` (no delimiter), `10.BOUNDARY DEVIATION: x` (no space) | no | 0 | 0 |
| whitespace before the delimiter: `   :`, `\t—`, `7. … DEVIATION    ** x`, NBSP before `:` | yes (D-064 (1)) | 1 row each | 1 of 4 (`7.` form) |
| NBSP or two spaces BETWEEN the words | no (literal single space) | 0 | 0 |
| indented `  - **BOUNDARY DEVIATION: x`, `* **BOUNDARY DEVIATION: x` | no (column 0, `- ` only) | 0 | 0 |
| `- **BOUNDARY DEVIATION:**` (empty tail) | yes | 1 row, observed `because the contract required it` | 0 |

All 26 R2 shapes give the contract outcome on the PIN. The near misses are silent (no row, no refusal), which is the contract: a line that
is not an anchor is not a record.

### 3.3 R4 the `\n`-only splitter (`/tmp/vj13r1/h/r4.py`, 2026-09-24T03:22:17Z; 10 separators × 6 site cases × 2 scripts = 120 runs)

Separators: U+2028, U+2029, U+0085, `\x0b`, `\x0c`, `\x1c`, `\x1d`, `\x1e`, `\r\n`, a lone `\r`. Each case also ends with a refusal (an
AF-AP-9 entry, a title with no ` — `, a bad rating or a `not json` line) so the printed `<line>` is checked against `git`'s count.

| site (former `splitlines` line) | the 8 text separators + lone `\r` on the PIN (pasted) | `\r\n` on the PIN | f772bfc, text separators |
|---|---|---|---|
| `_registry` (U+… inside the AF-AP-1 cell) | rc 3, both rows, `row_title` `uncommitted source accepted`; only the scratch log's line 20 `(no-registry-row)` (the blob has 20 `\n` lines) | the table really breaks: `:11`, `:15`, `:21 (no-registry-row)` | 0 rows; `:11`, `:15`, `:21` |
| `_parse_incident` (`See the entry below.<SEP>**2026-01-10 — AF-AP-1 …**`) | 2 rows (no mid-line row); `:21 (no-registry-row)` | the anchor starts a `\n` line: 3 rows, `:22` | 3 rows (minted mid-line), `:22` |
| `_finding_candidates` mid-line (`Context sentence.<SEP>- **F-13 BLOCKER …`) | `["F-1", "F-2"]`; `:11 (bad-title)` | F-13 is a row; `:12` | F-13 minted; `:12` |
| `_finding_candidates` table cell (`quotes a<SEP>b payload`) | F-14 `quotes a b payload` and F-15 kept; `:12 (bad-title)` | the row really breaks: F-14, F-15 not rows; `:13` | F-14, F-15 lost silently; `:13` |
| `_parse_lane_report` (`Context.<SEP>1. BOUNDARY DEVIATION: …`) | 1 drift row (no mid-line row); `:18 (bad-rating)` | 2 rows; `:19` | mid-line row minted; `:19` |
| `_parse_transcript`, raw separator inside the payload string | U+2028/2029/0085 (valid JSON): the new hit is a row, snippet `a b`; only `:7 (bad-json)` | `:6`, `:7`, `:8 (bad-json)`, `:5 (no-result)` | U+2028: `:6`, `:7`, `:8 (bad-json)` + `:5 (no-result)`; the file has 7 lines |
| `_parse_transcript`, control separators (`\x0b`…`\x1e`, lone `\r`: invalid JSON by RFC 8259) | `:6 (bad-json)`, `:7 (bad-json)`, `:5 (no-result)` | — | the same plus `:8 (bad-json)`, a line that does not exist |

Every one of the 60 PIN runs gives the contract outcome: no row from mid-line text, no valid row lost, and every `<line>` equals the
`\n` line of the committed blob. The `\r\n` column is the control: a real line break still breaks the line.

### 3.4 R3 one commit (`/tmp/vj13r1/h/r3race.py`, 2026-09-24T03:28:34Z; a real background loop, no shim)

Two real commits: B changes AF-AP-2's registry title and deletes `src/existing.py`. The harvested source
`tasks/briefs/x/VERIFY-X-report.md` is byte-identical in both, so admission passes whichever commit is resolved. A thread runs
`git update-ref HEAD B; git update-ref HEAD A` in a loop while the real script runs. A row set is MIXED when F-1's `paths` (the tree
listing) and the AF-AP-2 row's `row_title` (the registry read) come from different commits.
```
pin: runs=300 flips=8674 outcomes={'rc=0 consistent-A': 138, 'rc=0 consistent-B': 162} first-mixed-run=None
old: runs=150 flips=4664 outcomes={'rc=0 MIXED paths-from-A title-from-B': 53, 'rc=0 consistent-B': 18, 'rc=0 MIXED paths-from-B title-from-A': 70, 'rc=0 consistent-A': 9} first-mixed-run=0
```
R3 holds: 0 of 300 runs mix commits on the PIN; the control mixes 123 of 150. `grep -nw HEAD` finds only the resolve (§8 gates).

### 3.5 R5 the output ledger (`/tmp/vj13r1/h/r5.py` 03:30:41Z; `/tmp/vj13r1/h/conc.py` 03:31:26Z)

(A) `--out` shapes, fixture repo, discovery (each pasted):
```
dangling-symlink                   rc=6 stdout_lines=0 stderr='harvest-output-invalid: /tmp/vj13r1/w5/dangling.jsonl (ELOOP)\n'
dangling-symlink-creatable         rc=6 stdout_lines=0 stderr='harvest-output-invalid: /tmp/vj13r1/w5/dangling2.jsonl (ELOOP)\n'   (target not created)
symlink-to-dev-null                rc=6 … (ELOOP)
char-device (mknod c 1 3)          rc=6 … (decision-ledger-not-regular)
socket                             rc=6 … (ENXIO)
empty-string                       rc=6 stdout_lines=0 stderr='harvest-output-invalid:  (ENOENT)\n'
name-too-long                      rc=6 … (ENAMETOOLONG)
repo-root-dir                      rc=6 … (EISDIR)
hardlink-to-committed-source       rc=6 … (decision-ledger-unparseable) bytes-unchanged=True; `git status --porcelain` of the repo: ''
symlinked-parent (declared)        rc=0 stdout_lines=3 (the ledger is written through the symlinked directory)
```
(B) 13 corrupt pre-existing ledgers, each run twice: into the clean fixture and into a repo holding a malformed record. The second run
checks that the claim precedes parsing, since no `harvest-source-unparseable` line may appear. All 26 runs: `rc=6 stdout_lines=0`, EXACTLY ONE stderr line
`harvest-output-invalid: <path> (<reason>)`, `bytes-unchanged=True`. Reasons: `decision-ledger-unparseable` (truncated last line, a row cut
mid-way, invalid JSON, a JSON list, a JSON string, a blank line, a CRLF row, a BOM), `decision-row-incomplete` (`{}`),
`decision-row-digest-mismatch` (one hex digit of `state_digest` flipped), `decision-row-duplicate` (a MIDDLE row and the LAST row copied;
the builder copied the first), `decision-row-invalid` (a `row_id` cut by four characters).

(C) Held locks, pasted: `LOCK_EX held, same path rc=6 … (locked) bytes-unchanged=True secs=0.08`; the same through a HARD LINK (same inode):
`(locked) secs=0.08`; `LOCK_SH` held, both paths: `(locked) secs=0.08`. A POSIX `lockf` held instead of `flock`: `rc=0`, ten printed
skips, bytes unchanged (Linux keeps the two lock kinds apart; the contract names `flock`).

(D) Mode: umask 022 → `0o644`, 000 → `0o644`, 002 → `0o644`, 077 → `0o600`; a pre-existing 0600 file stays `0o600`.

(E) Whole-run refusals never create `--out`: `4 uncommitted`, `5 unknown`, `64 not a work tree`, `3 bad-utf8`, `4 output-source-conflict`
all `out-created=False`; usage (no `--out`) rc 64.

(F) R5 (c)'s two untested branches, forced through the kernel's `RLIMIT_FSIZE` on the harvester process (CPython ignores SIGXFSZ, so an
over-limit `write` is short or raises EFBIG; measured first: `800`, `200`, `err 27`). Fixture row sizes `[759, 765, 731, 715, 770, 766, 726, 621, 641, 650]`:
```
short write on append #2   limit=1141 pin: rc=6 stdout_lines=0 stderr='harvest-output-invalid: …/fsz-1141-pin.jsonl (decision-ledger-short-write)' ledger=rows=1 size=759
short write on append #2   limit=1141 old: rc=3 stdout_lines=3 stderr='…:4 (state:decision-ledger-short-write)' ledger=rows=1 size=759
EFBIG on append #3         limit=1524 pin: rc=6 stdout_lines=0 stderr='harvest-output-invalid: …/fsz-1524-pin.jsonl (EFBIG)' ledger=rows=2 size=1524
EFBIG on append #3         limit=1524 old: rc=1 … OSError: [Errno 27] File too large
short write on append #1   limit=379  pin: rc=6 stdout_lines=0 stderr='…(decision-ledger-short-write)' ledger=rows=0 size=0
```
Both branches work on the PIN: one named line, exit 6, no stdout, and the rows already appended stay intact (`append` truncated the
partial line). The builder's NOT-done says neither branch "can be forced without a decisions-module change or a fault injector"; this
limit forces both with no code change (FOLLOW-UP-3: make it a committed test).

(G) Concurrency, pasted:
```
pin-pairs: groups=25 width=2 run-outcomes={'6 locked)': 21, '0 harvest: 10 rows': 25, '0 harvest: 0 rows': 4} ledgers={'accepted rows=10': 25}
pin-triples: groups=6 width=3 run-outcomes={'0 harvest: 10 rows': 6, '6 locked)': 8, '0 harvest: 0 rows': 4} ledgers={'accepted rows=10': 6}
pin-hardlinked-pairs: groups=6 width=2 run-outcomes={'0 harvest: 0 rows': 1, '0 harvest: 10 rows': 6, '6 locked)': 5} ledgers={'accepted rows=10': 6}
old-pairs (control): groups=10 width=2 run-outcomes={'0 harvest: 0 rows': 8, '0 harvest: 10 rows': 9, '0 harvest: 1 rows': 2, '0 harvest: 4 rows': 1} ledgers={'accepted rows=10': 8, 'corrupt:decision-row-duplicate': 2}
```
0 corrupt of 37 PIN groups (the `harvest: 0 rows` runs started after their partner finished: a clean re-run, ten printed skips). The
control corrupts 2 of 10 with every run rc 0.

(H) A lock-ignoring writer at an injection point the builder did not use: BETWEEN two appends. The builder's D-6 is right that no git call
falls there, so a shim cannot reach it. An asynchronous racer process can: it polls the ledger and, as soon as it holds K complete lines,
appends one line with `O_APPEND` and no lock (K = 1..9, three repetitions each):
```
racer copy-first: {'6 decision-row-duplicate) | corrupt:decision-row-duplicate': 27}
racer copy-next: {'6 decision-row-duplicate) | corrupt:decision-row-duplicate': 2, '0 harvest: 9 rows | accepted rows=10': 25}
racer partial: {'6 decision-ledger-unparseable) | corrupt:decision-ledger-unparseable': 27}
```
Every foreign write that lands before the last append stops the run by name. A copy of the row the harvester appends NEXT is that row's
own id, so it is a printed skip and the ledger stays valid (10 distinct rows): D-063 (2)'s rule, correct. The two `copy-next` refusals
landed after that row was appended, so the copy named another id. The residual is the builder's §8 item 4: a foreign write after the
LAST append is not seen by this run.

### 3.6 R6 the class cell (`/tmp/vj13r1/h/r6s.py`, 03:25:25Z; the F-2 row's class cell replaced)

| cell | PIN | f772bfc | contract (D-064 (2): every `*` removed) |
|---|---|---|---|
| `BLOC*KER` (inner) | BLOCKER row | `bad-class` | BLOCKER ✓ |
| `****BLOCKER****` (doubled), `***FOLLOW-UP***` (bold-italic), `BLOCKER*`, `KNOWN (a*b)` | rows | rows | ✓ |
| `**BLOCKER**, SOLID`, `*INFO* (*qualified*)` | rows | `bad-class` | ✓ |
| `\*BLOCKER\*` (escaped: the backslashes stay) | `bad-class` | `bad-class` | ✓ (not a token) |
| `__BLOCKER__`, `_INFO_` (underscores), `****`, `**blocker**` | `bad-class` | `bad-class` | ✓ |
| rating cell `HI*GH` (control: another rule) | `:10 (bad-rating)` | same | ✓ unchanged |

### 3.7 S1, S5, S6 and the exploratory transcript shape

- S1 static (`r6s.py`): a FIFO, a `/dev/zero` char device (`mknod c 1 5`, which never ends if read), a `/dev/null` device, a bound Unix
  socket, a directory and a symlink to identical bytes, each in place of a tracked source, in discovery and SOURCE modes on both scripts:
  all 24 runs `rc=4 stderr='harvest-source-uncommitted: tasks/briefs/x/X-report.md' out-exists=False`, none near the 20 s timeout.
- S1 dynamic (`/tmp/vj13r1/h/s1race.py`, 03:26:17Z): a thread swaps a FIFO and the regular source with `renameat2(RENAME_EXCHANGE)` in a
  tight loop. PIN `runs=200 swaps=4404510 outcomes={'rc=0 rows=10 drift-observed-ok=True': 89, 'rc=4': 111}`: 0 hangs, and every
  admitted run carries the committed text. Control `old: runs=60 … 'rc=TIMEOUT': 9`. S1 holds.
- S5: the absolute token, `/src/existing.py`, `./src/existing.py` and `src/../src/existing.py` never enter `paths`; `src/existing.py:7-9`
  and `:7:3` do (`[["src/existing.py"]]`). The builder's two-root test is the discriminating one (its X4 kill, re-run in §5).
- S6 new shapes: an OBJECT nested 50000 deep on a JSONL line → `transcripts/x/t.jsonl:5 (bad-json)`, rc 3, harvest line printed (f772bfc:
  `RecursionError`, rc 1); a 5000-digit `n` inside a payload → `:6 (bad-payload)` (f772bfc: `ValueError … 4300 digits`, rc 1); an array
  payload nested 60000 deep → `:6 (bad-payload)`; a lone surrogate `\ud800` in a note → `:6 (state:decision-row-invalid)` on both.
- EXPLORATORY (not an S6 line): a `tool_use` block whose `name` is the JSON list `["Agent"]`, or whose `input.subagent_type` is a JSON
  object, crashes BOTH scripts: `rc=1 stdout_lines=0 stderr_tail="TypeError: unhashable type: 'list'"` (and `'dict'`),
  `ledger_rows=2` (the incident log's rows were appended before the transcript was reached).
  `scripts/decide-harvest:686` (`block.get("name")` tested with `not in {"Agent", "Task"}`) and
  `scripts/decide-harvest:691` (`role in {"hive-scout", "hive-reviewer"}`) test an unhashable value for set membership. It is a sibling of F-11 that S6 did not cover (FOLLOW-UP-1).
- R2 inside a code fence: the anchor is a row and the closing fence joins `observed` (`inside a fence** ````); a grammar-by-construction
  row of the F-18 V-o class.

## 4. ITEM 3 — D-066, ATTACKED (`/tmp/vj13r1/h/spec_d066.py` + driver `/tmp/vj13r1/h/mutdrive.py`, 2026-09-24T03:34:16Z)

Each mutant writes the SAME canonical line `append` would write (a local `replay` duplicate check + `canonical(row) + "\n"`), without
calling `append` on the live path. A dead `if False: append(args.out, row)` keeps the AST's `append` count at 1. Each is copied from the
PIN tree, compiled (`py_compile`), and the WHOLE test file runs against it (`DECIDE_HARVEST_TEST_ROOT=<mutant>`). Baseline on the
unmutated copy: `BASELINE (unmutated PIN copy) rc=0 summary='67 passed' failed=[] crash=[]`.

| mutant | the write (live path) | whole file | killed by |
|---|---|---|---|
| D1 builtin `open(out, "a")` | `print(line, file=open(path, "a"))` | `1 failed, 66 passed` | `test_script_delegates_every_write_to_ledger_append` only |
| D2 `io.open` | `print(line, file=io.open(path, "a"))` | `1 failed, 66 passed` | the same test only |
| D3 `os.fdopen` on the claimed fd | `print(line, file=os.fdopen(os.dup(<claim fd>), "a"), flush=True)` | **`67 passed`** | none: SURVIVES |
| D4 `os.write` on the claimed fd | `os.lseek(fd, 0, SEEK_END); os.write(fd, line)` | `1 failed, 66 passed` | the same test only |
| D4b `os.write` through an alias | `_ow = os.write` … `_ow(fd, line)` | **`67 passed`** | none: SURVIVES |
| D5 `pathlib.Path.write_text` | `target.write_text(old + line)` | `1 failed, 66 passed` | the same test only |
| D6 `shutil.copyfile` | `tempfile.mkstemp` + `os.pwritev(tfd, [old + line], 0)` + `shutil.copyfile(tmp, path)` | **`67 passed`** | none: SURVIVES (rewrites the file) |
| D7 a third `os.open(O_WRONLY\|O_APPEND)` | `os.pwritev(fd, [line], 0)` | `1 failed, 66 passed` | the same test only (the flag list has three entries) |
| D8 a subprocess shell redirect | `subprocess.run(["sh", "-c", 'cat >> "$1"', "sh", path], input=line)` | **`67 passed`** | none: SURVIVES |
| D9 a temp ledger, then `os.replace` | `shutil.copyfile(path, tmp)`; `_ledger.append(tmp, row)` (attribute call); `os.replace(tmp, path)` | **`67 passed`** | none: SURVIVES (a new inode per row: the lock and append-only are both gone) |

Five of ten bypasses pass all 67 tests. The narrowed test is a denylist of call names (`open`, `write`, `write_text`, `write_bytes`,
`ftruncate`, `truncate`, `pwrite`, `writev`, and exactly two `os.open`). `fdopen`, `pwritev`, `copyfile`, `subprocess.run`, `os.replace`,
an alias, and an attribute call `module.append` are not on it, and no behavioural test checks where the ledger's bytes come from.

The production code does NOT bypass: strace of the real PIN script on the fixture (`strace -f -e trace=openat,…,write,pwrite64,writev,
ftruncate,rename…,flock`), pasted:
```
fresh opens of --out by flag set: {'O_RDWR|O_CREAT|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC': 1, 'O_RDONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC': 11, 'O_WRONLY|O_CREAT|O_APPEND|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC': 10}
fresh writes on --out fds by (syscall, the fd's open flags): {('write', 'O_WRONLY|O_CREAT|O_APPEND|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC'): 10}
fresh rename/unlink/link/copy/truncate of --out, and flock calls: ['27923 flock(3, LOCK_EX|LOCK_NB)         = 0']
rerun opens of --out by flag set: {'O_RDWR|O_CREAT|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC': 1, 'O_RDONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC': 11}
rerun writes on --out fds by (syscall, the fd's open flags): {}
```
Every byte of `--out` is written by `append`'s own `O_WRONLY|O_APPEND` fd; the claim fd is never written; nothing renames or truncates
the file. So the gap is the TEST's strength, not the script's behaviour (FOLLOW-UP-2). D-066's accepted premise ("its ast-write and
ast-trunc mutants show the narrowed test still bites") holds for the name-listed writers and fails for five others.

## 5. ITEM 4 — THE BUILDER'S CLAIMS, GRADED

| claim (`tasks/briefs/laya/J1-3-R1-report.md`) | my command | pasted result | grade |
|---|---|---|---|
| RED: the new test file against f772bfc's script, `30 failed, 37 passed` | `DECIDE_HARVEST_TEST_ROOT=/tmp/vj13r1/x-f772bfc pytest /tmp/vj13r1/x-0d62801/tests/test_decide_harvest.py …` (03:39:48Z) | `30 failed, 37 passed`; the 30 = the 29 new behavioural cases of its §3 table + `test_script_delegates_every_write_to_ledger_append` | REPRODUCED |
| GREEN twice, `67 passed`, set `87e28761f102` | `pytest tests/test_decide_harvest.py -q -p no:cacheprovider --basetemp=/tmp/vj13r1/bt/g<n>` in the shared tree (`PYTHONDONTWRITEBYTECODE=1`), twice; `bash scripts/pc_suite.sh set-id -- tests/test_decide_harvest.py` | `67 passed` / `67 passed`; `1 files set=87e28761f102` | REPRODUCED |
| the PIN's own test file against the repaired script: `2 failed`, both named | f772bfc's test file (blob `2cace4741511`) in a copy of the PIN tree | `test_decide_harvest.py:477: assert False`; `:528: AssertionError: assert {'append', 'm...ow', 'replay'} == {'append', 'make_row'}`; `FAILED …::test_boundary_deviation_requires_the_declared_delimiter`, `FAILED …::test_script_delegates_every_write_to_ledger_append`; `2 failed, 31 passed` | REPRODUCED |
| AF-AP-138 baseline: each killer passes on the unmutated copy | the whole file on the unmutated PIN copy (03:34:16Z) | `BASELINE (unmutated PIN copy) rc=0 summary='67 passed' failed=[] crash=[]` | REPRODUCED |
| 28 of 28 mutants killed | 15 rebuilt from its diff-line column (`/tmp/vj13r1/h/spec_builder.py`), each compiled, the whole file run (03:41:55Z, 03:44:47Z) | table below: 15 of 15 KILLED, the same counts and killing tests as its §4 | REPRODUCED (15 of 28) |
| concurrency: 0 corrupt of 40 overlapping pairs | 25 pairs + 6 triples + 6 hard-linked pairs (§3.5 G) | 0 corrupt of 37 groups; 21 of 25 pairs overlapped (its run: 40 of 40); the control rate differs (mine 2 of 10, its 37 of 40, R2's 32 of 40: timing) | REPRODUCED (the bar); the overlap rate is timing |
| the real run: 235 rows, refused 39, exactly three moved records | §7 | see §7 | see §7 |
| NOT-done: "No test drives a short write … or an OSError from append … Neither can be forced without a decisions-module change or a fault injector" | `RLIMIT_FSIZE` (§3.5 F) | both forced with no code change; both branches behave per R5 (c) | REFUTED (the "cannot be forced" part); the behaviour is correct |

The builder's mutants, rebuilt (whole file per mutant; `compiled=ok`, `crash=[]` for each):

| mutant | diff line (as the builder's §4) | whole file | killing test(s) |
|---|---|---|---|
| m1 | `return _collapse(" ".join(pieces[:-1] + [piece[:close]])), None` | `4 failed, 63 passed` | `test_wrapped_incident_heading_keeps_every_line[I-k]`, `[I-l]`, `test_wrapped_bullet_title_keeps_every_line[V-k]`, `[V-l]` |
| m2 | `BOUNDARY_RE` back to `r"^(?:- \*\*BOUNDARY DEVIATION\*\*\|\d+\. BOUNDARY DEVIATION)"` | `4 failed, 63 passed` | `test_boundary_deviation_requires_the_declared_delimiter`, `…contract_anchor_forms[L-c]`, `[L-c2]`, `[L-c3]` |
| m3a | `incident_data = _head_blob(root, "HEAD", "docs/INCIDENT-LOG.md")` | `1 failed, 66 passed` | `test_head_moved_after_admission_rows_come_from_the_resolved_commit` |
| m3b | `_git(root, "ls-tree", "-r", "--name-only", "-z", "HEAD")` | `1 failed, 66 passed` | the same |
| m5a | `replay(path)` → `pass` | `1 failed, 66 passed` | `test_corrupt_output_ledger_is_refused_before_any_append` |
| m5b | `if exc.reason == "decision-row-duplicate":` | `1 failed, 66 passed` | `test_foreign_append_during_the_run_stops_it_by_name[copy-decision-row-duplicate]` |
| m5c | the `flock` line → `pass` | `1 failed, 66 passed` | `test_held_output_lock_is_refused_by_name_without_waiting` |
| m5d | `fcntl.flock(fd, fcntl.LOCK_EX)` | `1 failed, 66 passed` (the run took 42 s: the test's 20 s timeout) | the same |
| m6 | `raw = cell.strip().strip("*").strip()` | `1 failed, 66 passed` | `test_class_cell_loses_every_asterisk` |
| X1 | `for offset in range(1):` | `4 failed, 63 passed` | the four wrap cases |
| X2 | `r"^(?:- \*\*)BOUNDARY DEVIATION\b"` | `1 failed, 66 passed` | `test_boundary_deviation_numbered_form_is_an_anchor` |
| X3 | `r"(?:, (?:SOLID\|UNSURE))?",` | `2 failed, 65 passed` | `test_class_cell_loses_every_asterisk`, `test_class_cell_qualifier_form_is_a_valid_class` |
| X4 | the absolute branch restored through a module global | `1 failed, 66 passed` | `test_paths_ignore_absolute_tokens_same_commit_at_two_roots` |
| X5 | the emoji strip → `pass` | `1 failed, 66 passed` | `test_rating_cell_leading_emoji_is_stripped` |
| B-m5b | `_wt = (root / source.path).read_bytes()`; `source = Source(…, _wt, _wt.decode("utf-8"), source.digest)` | `1 failed, 66 passed` | `test_source_bytes_come_from_head_after_admission` |

Not re-run: m4a-m4e, N3a-N3c, s1, s6a, s6b, ast-write, ast-trunc (13 of 28). My §3.3 R4 table is the behavioural red for every
`splitlines` site, and the D-066 table (§4) covers the AST test.

## 6. ITEM 5 — MY OWN MUTANTS (`/tmp/vj13r1/h/spec_own.py`; none is in the builder's list; 03:48:57Z-03:56:55Z)

Each is compiled and collected (`compiled=ok`, `crash=[]`), and the whole file runs against it. The baseline (every test passes on the
unmutated copy) is §5's `67 passed`. A survivor then gets a discriminating probe through the REAL mutant script
(`/tmp/vj13r1/h/probes.py`), so a survivor is shown to be a test gap, not an equivalent mutant.

| mutant | diff line | whole file | killing test / the probe that tells PIN from mutant (pasted) |
|---|---|---|---|
| N05 a held lock ignored | `except BlockingIOError: pass` | `1 failed, 66 passed` | KILLED: `test_held_output_lock_is_refused_by_name_without_waiting` |
| N06 the claim's `S_ISREG` proof removed | `if False: return "decision-ledger-not-regular"` | `67 passed` | EQUIVALENT: `--out fifo` and `--out chardev` give the same `rc=6 … (decision-ledger-not-regular)` on both, because `replay` refuses them itself |
| N07 a fixed reason in R5 (c) | `_output_invalid(args.out, "decision-row-duplicate")` | `1 failed, 66 passed` | KILLED: `test_foreign_append_during_the_run_stops_it_by_name[garbage-decision-ledger-unparseable]` |
| N09 an `append` `OSError` swallowed | `except OSError: continue` | **`67 passed`** | SURVIVES. EFBIG on append #3: PIN `rc=6 … (EFBIG) ledger=rows=2`; mutant `rc=0 'harvest: 2 rows' 'skipped: 0 duplicates' stderr_tail=''`: eight rows lost with exit 0 |
| N10 a short write counted as a skip | `… or exc.reason == "decision-ledger-short-write":` | **`67 passed`** | SURVIVES. PIN `rc=6 … (decision-…short-write) ledger=rows=1`; mutant `rc=0 … 'skipped: 9 duplicates' ledger=rows=1`: nine rows reported as present duplicates that are absent |
| N11 the window widened to 11 lines | `for offset in range(11):` | **`67 passed`** | SURVIVES. 11-line heading: PIN `rc=3`, the scratch log's line 20 `(unterminated-heading)`; mutant `rc=0 'harvest: 3 rows'` |
| N13 no whitespace before the delimiter | `r"(?:—\|:\|\*\*)(?P<tail>.*)$",` | `1 failed, 66 passed` | KILLED: `test_boundary_deviation_contract_anchor_forms[L-c2]` |
| N14 only DOUBLE asterisks removed | `raw = cell.replace("**", "").strip()` | **`67 passed`** | SURVIVES. `*INFO* (*qualified*)`: PIN `rc=0 'harvest: 3 rows'`; mutant `rc=3 … :8 (bad-class)` |
| N15 `O_NOFOLLOW` dropped from the admission open | `os.open(root / path, os.O_RDONLY \| os.O_NONBLOCK \| os.O_CLOEXEC)` | `1 failed, 66 passed` | KILLED, but only by the STATIC flag pin in `test_script_delegates_every_write_to_ledger_append`; no behavioural test holds a symlinked source |
| N16 the admission `S_ISREG` check removed | `if False: return None` | **`67 passed`** | SURVIVES. `/dev/zero` device as a source: PIN `rc=4 … (0.08 s)`; mutant `TIMEOUT after 15s` (it reads zeros forever). An EMPTY committed source replaced by a FIFO: PIN `rc=4`; mutant `rc=0 'harvest: 10 rows'` (the FIFO reads as `b""` = the empty blob) |
| N18 the admission comparison names `HEAD` | `data = _head_blob(root, "HEAD", path)` | **`67 passed`** | SURVIVES. HEAD moved at the harvester's FIRST `cat-file` (during admission) to B, whose blob equals the dirty worktree: PIN `rc=4 harvest-source-uncommitted`; mutant `rc=0 'harvest: 5 rows'`, `drift-observed=['text only in commit B because the contract required it']` with `ap-row_titles=['malformed record silently dropped']` (commit A's registry): a MIXED run |
| N19 the claim moved before admission | early `_claim_output`, the later call removed | `4 failed, 63 passed` | KILLED: the admission tests (`--out` must not be created by a whole-run refusal) |
| N22 "non-blocking" weakened to a 3 s retry | a 30 × 0.1 s `LOCK_NB` retry loop | **`67 passed`** | SURVIVES. Held lock: PIN `secs=0.08`; mutant `secs=3.09`, the same line (INFO: no test pins the latency) |

TALLY: 13 own mutants; 5 KILLED (N05, N07, N13, N19; N15 only statically), 1 EQUIVALENT (N06), 7 SURVIVE as real test gaps (N09, N10,
N11, N14, N16, N18, N22). An N19 first form was discarded: it claimed twice in one process, and the second `flock` refused the first
(`(locked)`, 58 failed): flock is per open file description, even within one process. A note, not a harvester behaviour.

## 7. ITEM 6 — THE REAL RUN AT f772bfc (private clone; 2026-09-24T03:58:21Z)

```
$ git clone -q --no-checkout /home/user/agent-factory /tmp/vj13r1/clone && git -C /tmp/vj13r1/clone checkout -q f772bfc && git -C /tmp/vj13r1/clone rev-parse HEAD
f772bfc492fe65353cd63754dabd9f91e2c06490
status-before=0      (466M on disk)
$ for n in real real2; do python /tmp/vj13r1/x-0d62801/scripts/decide-harvest --root /tmp/vj13r1/clone --out /tmp/vj13r1/real/$n.jsonl …; done
== real rc=3
harvest: 235 rows, per question type: ap.violates_row=121, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=111, wf.drift=3
negatives: 0 (hand-labeled in J2)
sources: 261 read (incident_log=1, lane_report=148, transcript_jsonl=0, verify_report=112), 247 with no records; refused: 39 records; skipped: 0 duplicates
stderr lines: 39
== real2 rc=3
harvest: 235 rows, per question type: ap.violates_row=121, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=111, wf.drift=3
negatives: 0 (hand-labeled in J2)
sources: 261 read (incident_log=1, lane_report=148, transcript_jsonl=0, verify_report=112), 247 with no records; refused: 39 records; skipped: 0 duplicates
stderr lines: 39
cmp-jsonl rc=0
cmp-stderr rc=0
cmp-stdout rc=0
== unfixed (f772bfc script) rc=3
harvest: 232 rows, per question type: ap.violates_row=121, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=109, wf.drift=2
sources: 261 read (…), 248 with no records; refused: 41 records; skipped: 0 duplicates
status-after=0
sha256(real.jsonl) 16b35d5268478c80
```
Measured yield against KC-J7's 200 per type: every type is below 200 (`ap.violates_row` 121, `v1.finding_class` 111, `wf.drift` 3, the
four others 0), as the builder reported.

Record-level diff against the unfixed run, pasted:
```
--- stderr only in unfixed:
harvest-source-unparseable: tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md:550 (bad-class)
harvest-source-unparseable: tasks/briefs/laya/VERIFY-J1-0-R5-report.md:466 (bad-title)
--- stderr only in repaired:
rows unfixed 232 repaired 235 common 232
--- only in unfixed 0
  + v1.finding_class ans=CONTRACT-DEFECT path=tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md loc='F2 @ FINDING INVENTORY (no severity filter; each with the blocking predicate applied)'
  + wf.drift ans=yes path=tasks/briefs/s0-01-p5c-support/P5c-report.md loc='BOUNDARY DEVIATION @ DEVIATIONS (flagged loudly, first-class)'
  + v1.finding_class ans=BLOCKER path=tasks/briefs/laya/VERIFY-J1-0-R5-report.md loc="V5-05 @ FINDING INVENTORY (no severity filter; V5- ids are this lane's)"
common ids with different row bytes: 0
$ diff <(sort builder.err) <(sort real.err)      (the builder's 39 pasted refusal lines, from its report's lines 520-562)
IDENTICAL: the builder's 39 refusal lines == mine
```
Exactly the three predicted records moved, each read at its source line:
- `tasks/briefs/laya/VERIFY-J1-0-R5-report.md:466` `- **V5-05 BLOCKER — R5-4: a node property … and shifts a` / `:467` `  literal block's line map.** SOLID.`,
  a bold title wrapped once. It was refused `bad-title` and is now a BLOCKER row whose title carries `:467`'s text (`… shifts a literal
  blo`, cut by J1-1's field limit). R1.
- `tasks/briefs/s0-01-p5c-support/P5c-report.md:13` `- **BOUNDARY DEVIATION — \`tests/conftest.py\` was patched** …`, a contract
  anchor. It was silent and is now a `wf.drift` row. R2 / D-064 (1).
- `tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md:550` `| F2 | **CONTRACT-DEFECT** (part of F1) |`. It was refused `bad-class`
  and is now a CONTRACT-DEFECT row, `disposition` `BLOCKING`. R6 / D-064 (2).

All 232 unfixed rows are byte-identical in the repaired ledger. Count check: 232 + 3 = 235; refused 41 − 2 = 39; "with no records" 248 − 1
= 247. The census over the clone's 261 sources (`runpy` of the PIN script's own `_kind`, `_lines`, `_heading_text`) explains why nothing
else moved:
```
files holding each separator: {'U+2028': 1, 'U+2029': 0, 'U+0085': 0, 'x0b': 0, 'x0c': 0, 'x1c': 0, 'x1d': 0, 'x1e': 0} {'U+2028': ['tasks/briefs/laya/VERIFY-J1-1-report.md']}
files with a lone CR: 0 files with CRLF: 0
anchors whose bold does not close on the anchor line: 1
  closes later: tasks/briefs/laya/VERIFY-J1-0-R5-report.md:466 -> 'V5-05 BLOCKER — R5-4: a node property on the line before a `run:` scalar moves t'
```
R4 has one text-separator file and it holds no record; R1 has one wrapped anchor (V5-05) and no unclosed bold, so INFO-1's shape has no
real instance; R3 and S1 need a moving tree (the clone was static, `status` 0 before and after); S6 needs a transcript (0 committed).
The builder's refusal classification (its §7.2: 2 genuinely malformed, 37 grammar limits) was not re-read record by record here; the
39 lines are identical to its list.

## 8. ITEM 7 — ADJACENT CONSUMERS AND THE STATIC GATES (shared tree, `PYTHONDONTWRITEBYTECODE=1`, 2026-09-24T04:00:15Z)

```
$ python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/vj13r1/bt/j1
240 passed
rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/test_no_laya_in_gates.py
3 files set=70db5efe1e9b
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean
no_laya rc=0
$ python -m pyflakes scripts/decide-harvest tests/test_decide_harvest.py
pyflakes rc=0
$ python3 scripts/ap_screen.py --tests scripts/decide-harvest tests/test_decide_harvest.py
--- TEST_SCREEN over 2 path(s): 1 hits over 2 files ---
AP-66: 1
    tests/test_decide_harvest.py:980: pathlib.Path.is_file = lambda self: self == fifo or real_is_file(self)
$ grep -c splitlines scripts/decide-harvest
0
$ grep -nw HEAD scripts/decide-harvest
145:    result = _git(root, "rev-parse", "--verify", "HEAD^{commit}")
$ grep -l decide-harvest scripts/gate_files.txt .github/workflows/* scripts/hooks/* | wc -l
0
```
All REPRODUCED: `240 passed` on set `70db5efe1e9b` (as root the tmpfs test runs), the never-a-gate screen clean, pyflakes clean. The
one AP-66 hit is the builder's declared D-11: the reassignment sits inside the source string of a probe run in its own subprocess.

Exploratory R3 residual (`/tmp/vj13r1/wg/`, a shim at the harvester's second `ls-tree`: `update-ref HEAD <amended B>`, `reflog expire
--expire=now --all`, `gc --prune=now`), pasted:
```
pin: rc=1 stdout_lines=0 stderr_tail='AssertionError' commit-A-still-readable=False out-exists=True ledger=rows=0
old: rc=0 stdout_lines=3 stderr_tail='' commit-A-still-readable=False out-exists=True ledger=rows=10
```
The builder's §9 item 3 residual ("git objects of a resolved commit stay readable while the run holds no reference (inferred, not
measured)") is REFUTED by measurement: a concurrent rewrite plus an immediate prune deletes the pinned commit, and the PIN then stops
on `assert tree_paths is not None` (`scripts/decide-harvest:851`): exit 1, a traceback, an empty `--out`. It is loud, not silent, and
the trigger is exotic: default `gc` keeps unreachable objects for two weeks (FOLLOW-UP-7).

Exploratory R5 (`/tmp/vj13r1/whl/`): `--out` as a HARD LINK to an EMPTY committed file, pasted:
```
rc=0 harvest='harvest: 10 rows' stderr=''
tracked src/empty.py size now: 7144 | git status: M src/empty.py
```
`harvest-output-source-conflict` compares resolved PATHS (`scripts/decide-harvest:834-839`), so a hard link is not seen, and `replay` accepts
the empty file: ten rows land in a tracked file. A non-empty tracked file is refused by `replay` (§3.5 A, `decision-ledger-unparseable`).
It is the same at f772bfc, and it needs an operator to hard-link a tracked file (INFO-12).

## 9. FINDING INVENTORY (no severity filter)

Evidence: SOLID = reproduced this session through the real script; the command or file is named.

**No BLOCKER. No CONTRACT-DEFECT.** Every R1-R6 and S1-S6 line gives the contract outcome on every hostile shape I built (§3), the
real run reproduces exactly (§7), and every write to `--out` is `append`'s own (§4 strace).

**FOLLOW-UP-1 — a transcript anchor with an unhashable `name` or `subagent_type` crashes the run** (`scripts/decide-harvest:686`
`block.get("name") not in {"Agent", "Task"}`; `:691` `role in {"hive-scout", "hive-reviewer"}`). SOLID.
- Reproduction: `/tmp/vj13r1/h/r6s.py`, cases `list-name-anchor` and `dict-subagent-type`. PIN `rc=1 stdout_lines=0
  stderr_tail="TypeError: unhashable type: 'list'"` (and `'dict'`), `ledger_rows=2`. The same at f772bfc (pre-existing).
- Contract: J1-3 §4.4 (an anchor is a `tool_use` block whose `name` is `Agent` or `Task`, so a list name is no anchor: no row and no
  refusal) and §5 (exits 0/3/4/5/64, plus 6). Not an AMENDMENT 2 line: S6 names parse errors only.
- Material: for a hostile committed transcript, a traceback and no KC-J7 line, with the rows of earlier sources left in the ledger
  (valid rows, not corrupt). On the real corpus, none (`transcript_jsonl=0`).
- Why not a blocker: pre-existing, outside the amendment's lines, no corpus instance. It is the sibling of R2's F-11, which R2 disposed
  FOLLOW-UP on the same ground. Fix: `isinstance(..., str)` before both set tests, plus two tests. For the coordinator's issue #61.

**FOLLOW-UP-2 — the narrowed D-066 test misses five write-bypass shapes** (`tests/test_decide_harvest.py:574-619`). SOLID (§4).
- D3 `os.fdopen` on the claim fd + `print`, D4b an aliased `os.write`, D6 `shutil.copyfile`, D8 a subprocess `cat >>`, and D9 a temp
  ledger written by `_ledger.append` then `os.replace`d over `--out` each pass all 67 tests. D9 silently drops the lock's inode binding
  and append-only.
- Production: no bypass (strace, §4). Contract: J1-3 §1 holds; the frozen m8 (`open()`) is caught (D1). Material: test strength only.
- Fix: a behavioural delegation test. A `runpy` probe that wraps `ledger.append` and asserts the ledger's `st_ino` is unchanged and
  that every size change of `--out` happens inside an `append` call; or a `sys.addaudithook` probe asserting every `open` of `--out`
  carries one of the three flag sets, and that no `os.rename`/`os.replace`/`shutil.copyfile`/`subprocess.Popen` event names it.

**FOLLOW-UP-3 — R5 (c)'s short-write and `OSError` branches are untested; the builder's "cannot be forced" is refuted.** SOLID (§3.5 F, §6).
- `RLIMIT_FSIZE` forces both through the real script. The PIN gives `(decision-ledger-short-write)` and `(EFBIG)`, exit 6, no stdout,
  rows kept.
- Mutants N09 (`except OSError: continue`: eight rows lost with rc 0) and N10 (a short write counted as a skip: `skipped: 9
  duplicates` with one row present) pass all 67 tests.
- Fix: one parametrized test with `preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_FSIZE, (limit, limit))` at 1141 and 1524 bytes.

**FOLLOW-UP-4 — D-064's window edge and single asterisks are not pinned.** SOLID (§6: N11 and N14 survive). An 11-line heading must be
`unterminated-heading` (PIN `:20`); `*INFO* (*qualified*)` must be INFO (PIN row). Fix: two small tests.

**FOLLOW-UP-5 — S1's fd-type check is not pinned by behaviour.** SOLID (§6).
- N16 (the `S_ISREG` check removed) passes all 67 tests: the forced-window FIFO reads as `b""`, which already differs from the
  non-empty blob.
- Without the check, a `/dev/zero` device source hangs the run (`TIMEOUT after 15s`), and an empty committed source replaced by a FIFO
  is admitted (`rc=0 'harvest: 10 rows'`).
- N15 (`O_NOFOLLOW` dropped) is caught only by the AST flag pin.
- Fix: a device or empty-source-FIFO case, plus a symlinked-source case, in the S1 test.

**FOLLOW-UP-6 — R3's admission leg has no behavioural test.** SOLID (§6).
- N18 (`_head_blob(root, "HEAD", path)` in `_admit`) passes all 67 tests.
- Under a HEAD move at the FIRST `cat-file` it mixes commits: `drift-observed=['text only in commit B …']` with commit A's
  `row_title`. The PIN refuses with rc 4.
- Only the static gate (`grep -nw HEAD`) sees it. Fix: the R3 shim test, moved to the first `cat-file`.

**FOLLOW-UP-7 — a pruned resolved commit stops the run on a bare `assert`** (`scripts/decide-harvest:851`). SOLID (§8). An exotic
trigger; a loud failure. Fix: a named whole-run refusal in place of the assert (and of the silent `registry = {}` when the resolved tree
lists `docs/INCIDENT-LOG.md` but its blob cannot be read).

**INFO-1** — R1's literal "the next `**`" lets an unclosed bold absorb the following line up to the next `**`: `F-26 BLOCKER` title
`unterminated -`, an `ap.violates_row` row for AF-AP-2 minted from an absorbed prose line, AF-AP-1 `… unterminated -` (§3.1). f772bfc
refused these (`bad-title`) or dropped them silently. 0 real instances (census, §7). Contract-literal (§4.1, R1, D-064 (3)); not in the
builder's §8 item 3. A contract question for J2, not a repair: may a bold close cross a list-item start or a blank line?
**INFO-2** — a drift anchor inside a code fence is a row whose `observed` ends in the closing fence (F-18 V-o class).
**INFO-3** — `BLOC*KER` is a BLOCKER row (D-064 (2) literal).
**INFO-4** — `--out` under a symlinked parent directory is followed (the ledger's declared limit; the builder's §8 item 5).
**INFO-5** — a POSIX `lockf` holder does not exclude a harvest (flock only, as the contract names).
**INFO-6** — the created mode is `0o600` under umask 077 (`0o644` is passed; the umask applies, as for `append`).
**INFO-7** — N06 is an equivalent mutant: the claim's `S_ISREG` proof is masked by `replay`'s own check.
**INFO-8** — no test pins the `locked` latency (PIN 0.08 s; N22's 3 s retry passes).
**INFO-9** — `--out ''` prints `harvest-output-invalid:  (ENOENT)` (an empty `<path>`).
**INFO-10** — flock is per open file description: a second claim in the same process refuses itself `locked`.
**INFO-11** — my concurrency overlap was 21 of 25 pairs and my control corrupted 2 of 10 (the builder: 40 of 40 and 37 of 40; R2: 32
of 40). Timing; the bar holds.
**INFO-12** — a hard link to an EMPTY tracked file as `--out` receives the rows (§8); pre-existing, needs deliberate misuse. An inode
check (`st_dev`, `st_ino` of `--out` against the tracked worktree files) would close it.

Reproduced vs static: every item above ran through the real script, except the INFO-7 equivalence reasoning (confirmed by the paired
probe). Deliberately skipped: the builder's 13 other mutants (m4a-m4e, N3a-c, s1, s6a, s6b, ast-write, ast-trunc: my R4 table and §4
cover the same lines); a record-by-record re-read of the 39 refusal classifications (the lines are identical to the builder's; item 6
asks for the moved records); any PC run; any run with `--root /home/user/agent-factory`.

## 10. GATE RECOMMENDATION

The blocking predicate, applied to the three strongest candidates:

| finding | 1 contract | 2 canonical path | 3 material | 4 discriminator | 5 in-boundary | blocks? |
|---|---|---|---|---|---|---|
| FOLLOW-UP-1 TypeError crash | J1-3 §4.4 / §5 (not an AMENDMENT 2 line) | yes (real script, scratch repo) | only for a hostile transcript; 0 in the corpus | yes | yes | no: pre-existing, outside the repair's lines; F-11 precedent |
| FOLLOW-UP-2 D-066 bypasses | §1 behaviour holds; m8 caught | the production path does not bypass (strace) | no (test strength) | yes (5 mutants) | yes | no |
| FOLLOW-UP-3/5/6 untested branches | R5 (c), S1, R3 hold on the PIN | the PIN is correct on each probe | no (test strength) | yes (N09, N10, N16, N18) | yes | no |

GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS. No finding meets the whole predicate: the real script meets every R1-R6 and S1-S6 line
on every hostile shape I built; the real run reproduces (235 rows, 39 refusals, the same three moved records); every write to `--out`
goes through `append`. The follow-ups are one pre-existing crash sibling (FOLLOW-UP-1), five test-strength gaps (FOLLOW-UP-2 to -6)
and one exotic loud failure (FOLLOW-UP-7). This recommendation rests on items run fully; the partial parts (13 of the builder's 28
mutants not re-run; the 39 classifications not re-read) do not bear on it.

## DISCREPANCIES

- D-1: HEAD moved during this lane: a923be5 (authoring) → d1463bd → f172024 → a8b4927 (== origin at 04:01:45Z). The boundary diff
  against 0d62801 stayed 0 lines at 03:11Z and 04:01Z, and the script blob stayed `971e38803587`. No item changed.
- D-2: three untracked 0-byte files appeared in the shared tree's root at 03:44:11Z: `r_medium.txt`, `r_unq.txt`, `r_xhigh.txt`. They
  are not mine: at that minute my only process was the m5c mutant's pytest run, with its cwd under `/tmp/vj13r1/mut/`, and no command of
  mine names them. Left untouched. Another untracked file, `tasks/briefs/kit-k1-support/VERIFY-K150-report.md`, is another verifier's.
- D-3: my own process: the first N19 form claimed twice in one process and was discarded (§6); the `r4.py` first run failed on an
  f-string backslash and was fixed before any result was read; my first extraction of the builder's 39 lines stopped at a fence (0
  lines) and was redone by line range; the `/proc/self/status` probe's `bytes-unchanged=False` is my probe's artifact (`/proc/self`
  is a different process at each read), not a write (strace shows no write outside `append`).
- D-4: my S5 probe (§3.7) does not discriminate PIN from f772bfc (the relative tokens in the same record also yield `src/existing.py`);
  the discriminating check is the builder's two-root test, re-run as X4 (§5).
- D-5: the builder's report says its concurrency "Every pair overlapped". Mine overlapped 21 of 25 (timing, INFO-11).
- D-6: the brief's item 4 asks for "at least ten" of the 28 mutants; 15 were run. Its item 2 R5 asks for "20 pairs or more"; 25 pairs, 6
  triples and 6 hard-linked pairs were run.
- D-7: no step was refused by a filter.

## NOT-done

- Items run: 1 FULLY; 2 FULLY (every shape the brief lists, plus my own); 3 FULLY (all eight shapes plus two); 4 FULLY for the claims,
  with 15 of 28 mutants (the brief's floor is ten); 5 FULLY (13 own mutants, seven surviving, each probed); 6 FULLY (the builder's
  refusal classification was not re-read, which item 6 does not ask); 7 FULLY.
- No `/bug-echo` and no AF-AP registry row: this lane writes only this report. Classes for the coordinator: FOLLOW-UP-1 (a set-membership
  test on an unvalidated JSON value; a sibling of F-11); FOLLOW-UP-2 (a denylist AST test standing in for a behavioural delegation test);
  FOLLOW-UP-7 (a bare `assert` on external state).
- No PC run (the venue is the sandbox). No run with `--root /home/user/agent-factory`.
- The quartet cannot see the suffix-less script: `graft skeleton` indexes no definitions and GitNexus `impact` returns `risk: UNKNOWN`.
  No DORMANT or reachability claim is made. Every claim rests on reading the script and running it.
- Scratch: the clone (466 MB), the mutant trees and every scratch repository were removed at 04:0xZ. `/tmp/vj13r1/` keeps 1.6 MB to
  re-run any table: the harnesses (`/tmp/vj13r1/h/*.py`), the pasted outputs (`*.out`), the two pinned extracts (`x-0d62801`, `x-f772bfc`)
  and the real run's stdout/stderr (`real/`). `/tmp/vj13r1p/` is the brief author's premise directory, not mine.

## Report lint (three rounds, the bound)

- Round 1: `report_lint: 16 refs — OK 9, NEAR 0, MISS 3, UNCHECKABLE 4, UNRESOLVED 0 (worktree)` and `FLOOR — OK 9 < --min-refs 15`.
  Two MISS lines cited the SCRATCH copy's `INCIDENT-LOG.md` line 20 as if it were the repository's (real errors, now written in
  words); one cited line 686 without a token from it. I added the §2 table of where each contract line lives.
- Round 2: `report_lint: 28 refs — OK 24, NEAR 0, MISS 1, UNCHECKABLE 3, UNRESOLVED 0 (worktree)`. The `:691` ref sat on the line
  before its token; moved.
- Round 3: `report_lint: 28 refs — OK 25, NEAR 0, MISS 0, UNCHECKABLE 3, UNRESOLVED 0 (worktree)`, rc 0, above the `--min-refs 15`
  floor. The three UNCHECKABLE refs are inside pasted command output, left verbatim.
