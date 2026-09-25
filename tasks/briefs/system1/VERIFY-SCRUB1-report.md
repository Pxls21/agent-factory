# VERIFY-SCRUB1 report (task #301): the transcript scrubber's glued-key rules and its value gate

Lane: adversarial-verifier (sandbox, Opus 5.5). Started 2026-09-25T22:11:33Z (bucket 22:1xZ). Written incrementally.
Target: 49bf75e (SCRUB1 landed, task #280). PIN 2dbf1f4 (origin). Local HEAD at start f6f199f (two local commits ahead of
origin, neither touching the target files). Contract: `tasks/briefs/system1/SCRUB1-brief.md` items 1-4, the lane's report
`tasks/briefs/system1/SCRUB1-report.md`, AF-AP-224 (`docs/INCIDENT-LOG.md:765` at the PIN; 767 in the tree now).
Scratch: `<scratch>/vscrub1/` (`<scratch>` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad`).

## STATUS

DONE. **MERGE-READY-WITH-FOLLOWUPS.** Every contract item reproduced through the real code with fake keys and fixture
sources only (the committed tests themselves read the real sources, so they ran in a private mount namespace: F1). No
blocker. Follow-ups: F1, F8 (test gaps around the production source list), F2/F3/F12 (#292 sharpened: a key or a
40+ token next to a non-ASCII letter survives at real length, the opaque rule included), F5 (#291 confirmed), F6 (#293
confirmed; `docs/HICCUPS.md` is a committed writer with no value gate), F7, F10.

## 1. PREMISE, re-measured (22:1xZ)

| # | Premise line | Measured now | Verdict |
|---|---|---|---|
| P1 | origin = 2dbf1f4 | `git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf` = 2dbf1f4 | holds |
| P2 | 49bf75e's stat: 6 files, 632+/16- | identical stat | holds |
| P3 | 0 commits on the three target files after 49bf75e | 0 to origin; 0 to local HEAD; `git diff 49bf75e` on them empty; sha256 prefixes: exporter 2136062e0af69815, test file 2067ae7e642fb919 (the lane's final bytes) | holds |
| P4 | the four rules at lines 84-87; KNOWN_VALUE_SOURCES 237; defs 250/284/296/319 | identical grep output | holds |
| P5 | 18 digests, 3.5M; labels.jsonl 5301 lines; the lane's scratch holds 8 files | identical | holds |
| P6 | set id 73755bb9fbbf; `174 passed` | set id computed with pc_suite.sh's own one-liner (not run: the script is a bridge tool): `1 files set=73755bb9fbbf`. The count, see below | holds, with a caveat (F1) |

**Caveat that shapes this whole lane (F1).** The committed test file cannot be run as it stands without exercising the
exporter's DEFAULT value-gate sources: 30+ of its tests run the real CLI (`_run`, `_export_one`, the glued-key and
the exit-4 tests), and `main()` always calls `export(path, out, cap)` with the default `sources=KNOWN_VALUE_SOURCES`,
bound when `export` is defined. The committed tests never replace `KNOWN_VALUE_SOURCES` (it appears once, in a
membership assert on the `TYPESAFE_BASE_URL` entry, `tests/test_transcript_export.py:837`); the exit-4 test replaces only GH_TOKEN in the child's
environment. So every run of this file reads `.pc-bridge.env`, `/root/.codiv/api.env`, the pseudonym key and both
token variables of the machine it runs on. This lane never does: every run of the committed tests below happens in a
PIN copy (`git archive 2dbf1f4` of the exporter, `known_values_check.py`, the test file, `tests/conftest.py`,
`pyproject.toml`, `scripts/test_summary.sh`) inside a private mount namespace (`<scratch>/vscrub1/masked.sh`): tmpfs
over `/root/.codiv` and `/root/.config/session-export`, `/dev/null` bound over the shared tree's `.pc-bridge.env`,
`GH_TOKEN`/`GITHUB_TOKEN` unset; a guard prints booleans only before the command runs. Two venues: **absent** (every
default source missing, CI's shape) and **fakes** (all five present at their production paths as FAKES made with
`secrets.token_hex` inside the namespace: the sandbox's shape without a real value).

```
$ cd <scratch>/vscrub1/pin && masked.sh absent <pin> -- bash scripts/test_summary.sh tests/test_transcript_export.py --basetemp=<scratch>/vscrub1/bt   (twice)
pytest-summary: 174 passed in 2.52s
pytest-summary: 174 passed in 2.50s
$ ... masked.sh fakes ...   (twice)
pytest-summary: 174 passed in 2.25s
pytest-summary: 174 passed in 2.34s
1 files set=73755bb9fbbf
```
Verdict: the premise holds. No CONTRACT-INVALID.

## 2. Attack item 1: the four rules, hostile shapes, every writer (22:2xZ)

Instruments (scratch, fake keys from `secrets.token_hex` / `secrets.choice` at run time, nothing but context names and
flags printed): `<scratch>/vscrub1/rules_probe.py` (the PIN copy's `scrub`, `scrub_payload`, `scrub_strict` and the
pre-SCRUB1 `scrub` of `49bf75e^`; 14 keys: short keys under the opaque rule's 40 and real-length ones, per family; 48
left contexts, 17 right contexts; plus the canonical-JSON view session_export's tool_call event scrubs) and
`<scratch>/vscrub1/e2e_probe.py` (a fixture transcript whose records copy the real ENVELOPE and block shapes, measured on
the main transcript by `shapes.py`, counts only: user records with str content (1,415 real), user text blocks (51),
assistant text/thinking/tool_use blocks (6,693/16,684/20,990), tool results (20,984), an attachment and a system record;
one distinct key per record; the PIN copy's `export(..., sources=())`, the old `export()`, and the PIN copy's
`session_export.convert()` with a fake 32-byte key).

**Left side, decoded text (`scrub`, what `export()` writes).** Keys glued after `_` and `__` are taken for all four
families (the contract); every ASCII punctuation context tested is taken (`-` `.` `/` `:` `=` `"` `'` `\` `` ` `` `(`
`@` `#` `$` `%` `&` `+` `,` `;` `?` `|` `~` `*` `<`, URL path and query, line start and end, after a real newline or tab);
a key after a non-ASCII letter, a non-ASCII digit or a fullwidth letter is taken now and was not before (after NBSP
or a zero-width space it was taken before too). A short key after an ASCII letter or digit survives (the lane's measured design choice, M16). A short key after a
LITERAL JSON escape inside the decoded text (`\n`, `\r`, `\t`, `\u0022`, `\u003d`) survives; after `\"`, `\\`, `\/` it is
taken. Real-length keys (sk legacy 51, sk-proj with `-`/`_`, ghp 40, AIza 39, xoxb 56) are taken in EVERY left context
(the opaque rule covers what the provider rule refuses). Old to new: 23 (context, family) pairs newly caught, **0 newly
missed** on either side.

End to end through `export()`: only user str content, user text blocks and assistant text reach a digest (a marker per
kind: thinking, tool_use input and tool results never do). Per kind the outcome matches the rule-level table: after `_`
and `__` caught (the old exporter leaked all four families after `_`, three after `__`); after a letter, a digit or a
literal `\n`, and before `_` (gh, xox) or `é` (all four), a short key survives in both exporters.

**Right side (not in the contract; #292).** The trailing `\b` is unchanged, so the old and new rules agree (42 of 238
right-side cases survive in both). Sharper than the lane's A1: **a key followed directly by a non-ASCII letter survives
at REAL length in every family** (sk legacy and proj, ghp 40, AIza 39, xoxb 56), because the opaque rule's trailing `\b`
fails the same way: `\b` between an ASCII alphanumeric and `é` or `の` (both word characters) never holds. Text in
Japanese or Chinese writes no space between a token and the next word (`…ghp_XXXX…です`). A real-length xoxb token
followed by `_` leaks its last segment (the 24-character secret part: the rule stops at the last hyphen, the remainder is
under 40). 0 instances in the lane's corpora (its A1).

**Which text each writer scrubs.** `export()`: the DECODED turn text (`json.loads`, then the text of the turn). 
`session_export`: decoded text for text, thinking and tool results, but a tool_use input as CANONICAL JSON
(`canon(inp)`, `json.dumps(..., ensure_ascii=False)`: a newline is the two characters `\n`, a control character
`\u00XX`). Through the PIN copy's real `convert()`: a short key at a LINE START inside a Bash command reaches the session
export's event text for all four families (the `n` of `\n` is a letter to the anchor); after `_`/`__` it is caught.
`scrub_strict` (strict results) takes all but a 17-character xoxb after `\n`/`\t` (raw) or before `_`/`é`.

**Ordinary text.** Kept by the new rules: the lane's ten words, `whisk-…`, `ask-…`, `tsk-…`, `mask-…`, `brisk-…`,
`<task-notification>`, prose about the prefixes (`` The `sk-` prefix ``, `ghp_ is GitHub's prefix`), `task-301`. Newly
redacted (the intended reach of the `_` anchor): identifiers that put a prefix after `_` with a long enough tail
(`use_sk-learn-pipeline-for-this` → `use_sk-<redacted>`, `models/my_sk-learn-classifier-v2.pkl`,
`config_ghp_placeholderValueForDocs`, `slack_xoxb-not-a-real-token-at-all`). The lane measured 0 such words in its
corpora; section 4 re-checks the digests byte for byte.

### 2b. The lane's measurement table, re-counted without the known-value split (22:4xZ)

`<scratch>/vscrub1/measure_v.py` (it asserts the old and new files' rules are the four bodies with `\b` and
`(?<![A-Za-z0-9])`): every string of every record, decoded; scrub's first three rules first; each candidate anchor's
matches at positions the PIN's `\b` refuses; "newly redacted" = the matched text survives the old full scrub. It cannot
split known from not known (this lane reads no real source), so it checks the counts, not the "no known secret" half.
```
18 digests (3,537,139 bytes now):   S1 0 | S1digit 0 | S2 sk 1 (the word `task`; the digests grew since the lane's run)
main transcript + second root:      S1 0 | S1digit 0 | S2 sk 15,460 (task 15,282, ask 76, desk 58, flask 29, disk 7, risk 6, subtask 2), gh 2, AIza 1
                                    raw lines, S1e only: sk 8, all inside a run the opaque rule takes
340 subagent transcripts:           S1 sk 15, gh 8, xox 8 newly, AIza 3 hidden; S1digit = S1 (0 digit glue); S2 sk 2,799 (task 2,398 ...)
                                    raw lines, S1e only: sk 1 newly visible, gh 1 hidden
```
Attributed per file (`attrib.py`): the S1 hits beyond two sit in ONE transcript, this lane's own (agent-af77651c, first
record 22:10Z: the ordinary-word probe of section 2 typed `use_sk-learn-...`, `config_ghp_...`, `slack_xoxb-...`); the
other two are agent-a2fe7fa5 (09-24 05:10Z) and agent-ac927ed4 (09-25 16:45Z), with the lane's exact shapes (sk after `_`,
len 15, tail U L D -; sk after `__`, len 27, tail U). **So the lane's S1 row reproduces: 2 new redactions, both
underscore-glued key shapes; digit glue 0; the no-anchor option adds roughly 18,000, `task` first** (18,260 now against
the lane's 17,692: the corpus grew by about 9 MB of main transcript and 6 subagent files). One small difference: the
lane called its raw-line `gh` case visible; this probe finds the opaque rule takes it in the raw line (a probe-method
difference on 1 instance).

## 3. Attack item 2: the value gate, through fixture sources only (22:2xZ)

Instrument: `<scratch>/vscrub1/gate_probe.py`, run inside `masked.sh fakes`: the production paths hold FAKE files
(`.pc-bridge.env` beside the PIN copy with `PC_BRIDGE_URL`/`PC_BRIDGE_TOKEN`, `/root/.codiv/api.env` in the private tmpfs
with a fake key and a fake `TYPESAFE_BASE_URL`, a fake 32-byte pseudonym key, fake `GH_TOKEN`/`GITHUB_TOKEN`), so the REAL
CLI and `main()` run with the production `KNOWN_VALUE_SOURCES` tuple unchanged and never meet a real value. The probe
refuses to start unless `/proc/self/mountinfo` shows both tmpfs mounts (checked outside: it exits before any read). Every
stderr line is matched against the three allowed shapes and checked for any 8-byte piece of every fake before it is shown.

**A. The real CLI, production source list (all as the contract wants).** Each planted fake refuses with exit 4, stdout
empty, NO output directory and nothing else in its parent (no partial or temporary file); an out directory that already
held a digest keeps its bytes. Lines seen (names and counts only; no fake piece in any):
```
REFUSED, nothing written: .pc-bridge.env:PC_BRIDGE_TOKEN value whole=1 windows=25/25
REFUSED, nothing written: .pc-bridge.env:PC_BRIDGE_URL host whole=1 windows=0/0      <- a bare bridge host: scrub keeps it (no scheme)
REFUSED, nothing written: api.env:ZQ_FAKE_API_KEY value whole=1 windows=25/25
REFUSED, nothing written: pseudonym.key:raw hex whole=0 windows=23/57                  <- a 30-hex cut copy
REFUSED, nothing written: env:GH_TOKEN value whole=1 windows=17/17                     (GITHUB_TOKEN the same)
REFUSED, nothing written: .pc-bridge.env:PC_BRIDGE_TOKEN value whole=0 windows=18/25    <- split across two days' files
REFUSED, nothing written: .pc-bridge.env:PC_BRIDGE_TOKEN value whole=0 windows=2/25     <- cut by the 4000 cap, 9 chars kept
```
Passes, as designed: a clean transcript (rc 0, no stderr); the whole bridge link (the link rule redacts it first); the
`TYPESAFE_BASE_URL` value and its host; the 64-hex pseudonym key whole (the opaque rule redacts it first).

**B. Encoded forms (api.env's fake: 32 hex with digits).** Refused: URL-encoded and JSON-escaped (identical bytes for hex),
a zero-width joiner inside (windows 18/25), upper case (windows 3/25, by the all-digit windows of a hex value). PASS the
gate and reach the digest: base64 of the value (24 chars), hex of its ASCII (16 chars), every character spaced, reversed.
The raw key's default `xxd` layout (4-hex groups) passes too: no 8-byte window survives the spaces (known_values_check's
docstring says "an `xxd` column" still counts; true for `xxd -p` only). In process with a fixture value holding `+ / =`:
URL-encoded (windows 10/24), `\/`-escaped (17/24) and a 14-char cut copy (7/24) are all refused.

**C. Missing, unreadable, odd sources (production path, fakes swapped inside the tmpfs).** Missing: one stderr line, rc 0.
A directory: `REFUSED, nothing written: value gate: cannot read the source api.env (IsADirectoryError)`, rc 4. A dangling
symlink and an EMPTY file: skipped as "missing or empty" with one line (known_values_check's own CLI exits 2 on a source
with no value; the gate skips it). A FIFO source (in process, fixture): the export HANGS at `open()` (killed by a 10 s
timeout; nothing written).

**D. `main()` in process and the brief's question.** Replacing the module attribute `KNOWN_VALUE_SOURCES` does NOT reach
`main()`: `export`'s default was bound when `export` was defined (`export.__defaults__[0]` is still the original tuple
after the replacement). With only the attribute replaced by a fixture source whose fake value is planted, `main()`
returned 0 and WROTE the digest (it read the production paths, here fakes); with `export.__defaults__` replaced it
returned 4 and wrote nothing. The committed tests never replace the attribute (F1), so no committed test drives `main()`
with fixture sources; the one exit-4 CLI test swaps only `GH_TOKEN` and reads the other four real sources.

**The brief's question, answered.** Yes: `main()` → `export()` with the production list is a path no committed test
can reach without the real sources. In process a test reaches it only by replacing `export.__defaults__` (not the
attribute); through the CLI only by the two token variables, a copy of the script placed elsewhere (the bridge env is
resolved beside the script) or a mount namespace. It matters for one reason: the production list itself is then
untested for three of its five entries (F8), and a wrong entry fails SILENTLY in production (its skip line is
discarded by push_clean, F5). The refusal and write logic behind it is fully reached by the fixture tests.

**The gate's cost, re-measured with FAKE sources of the production shape** (`cost.py` in `masked.sh fakes`; the lane's
figure was with the real ones): `committed digests 18 bytes 3561429`; `run 1: load 3.2 ms, count 744.7 ms, forms 12,
windows 344, hits 0`; runs 2 and 3: 724.5 and 742.5 ms. The lane's 0.69 s (12 forms, 327 windows) holds in shape.

**E. In process, fixture sources (`export(..., sources=...)`).** Under the floor (7 chars): not a value, passes. 8 chars
pasted whole: refused (`whole=1 windows=0/0`). Not windowed, so a CUT copy passes: a 15-char value (windows need 16+) and
a 32-letter value with no digit (windows need a digit); either one pasted whole is refused. A URL's host: refused; the
same host in upper case passes; a host under 8 characters is no form. `TYPESAFE_BASE_URL` skipped in its own source only:
the same URL under another name in the same file refuses (`e.env:ZQ_OTHER host whole=1 windows=0/0`), and the name in a
source with no skip refuses. `export KEY="v"` is parsed; `KEY=v # comment` is NOT (the comment becomes part of the value,
so the real value never matches). A source kind typo (`env_file`) is silently read as a raw file (its values never
checked). An env line whose part before `=` holds secret text (`zq <20 chars of the value>=<value>`) refuses, and the
refusal line PRINTS that name verbatim (a 20-char piece of the fake value in stderr): "names only" holds only for
well-formed env files.

**Is `export()` the only writer in this file?** Yes: `export()` is the file's one `open(..., "wb")`; `main()` prints
paths; `scrub`, `scrub_payload`, `scrub_strict`, `known_values`, `value_hits` return values. The other writers import
the rules (section 6, #293).

## 4. Attack item 3: the byte-identity claims (22:3xZ)

**The 18 digests.** `<scratch>/vscrub1/bytecmp.py`: the PIN copy's `export(..., sources=())` (no real source read) and
the pre-SCRUB1 `export()` (`49bf75e^`, no gate) over the SAME bytes of this session's main transcript (the file is live,
so both read it through a reader that stops at the end of its last complete line when the run started; the modules'
`open` is wrapped for that one path, the exporters' code is unchanged), into two scratch folders:
```
transcript bytes read: 742803433 (fixed at start); new 5.52 s, old 5.55 s
files new=18 old=18 same set=True
identical by sha256: 18 of 18; differ: []
committed digests: 18; same names as the new set: True
committed == new: 17 of 18
  chat-2026-09-25.md committed 407619 bytes, new 428934 bytes; committed body a prefix of the new body: True
```
Reproduced: byte-identical. The committed `transcripts/sandbox/` (2dbf1f4) equals the new export for 17 days; today's file
differs only because the transcript grew since the 21:50Z sync (the committed body, after the header line with its turn
count, is a prefix of the new one). Both syncs after the landing (5eda746 20:27Z, 2dbf1f4 21:50Z) ran the NEW exporter
with the gate on the real sources and wrote files, so the real gate passed the real transcript then (indirect: this lane
never reads the real sources; the lane's own run with them is its claim, not reproduced here).

**The Laya records.** `<scratch>/vscrub1/laya_rescrub.py` on the recorded dataset (a copy another lane left in the
session scratch, sha256 checked equal to the manifest's `99070c33…`, 12,800,855 bytes; read only):
```
rows 6196: state str 1652, dict {query, chunk} 4544; by question {'v1.finding_class': 826, 'v1.blocking': 826, 'ap.violates_row': 4544}
re-scrub of the stored states: {'new(stored) != stored': 0, 'old(stored) != stored': 0, 'new(stored) != old(stored)': 0}
labels 5301 (distinct item+question 5301) by question {'v1.finding_class': 826, 'v1.blocking': 826, 'ap.violates_row': 3649};
  label->row by item_id+question 5301, by sent_state_sha 5301, both on the same row 5301; rows with no label {'ap.violates_row': 895}
collect_v2 at 434b727dfd with the old scrub: 6220 items in 3.7 s
collect_v2 at 434b727dfd with the new scrub: 6220 items in 3.6 s
pre-fit items whose state differs between the old and the new scrub: 0 of 6220
```
Reproduced: 0 of 6,196. **How the two counts relate:** the 6,196 are the dataset's ROWS (every row's `state`: 1,652
strings for the two v1 questions, 4,544 `{query, chunk}` dicts for `ap.violates_row`); `labels.jsonl`'s 5,301 lines are
teacher LABELS with no state text, one per labelled row, each joined to exactly one row by `item_id`+`question_id` and by
`sent_state_sha` alike: all 1,652 v1 rows plus 3,649 of the 4,544 ap rows (895 ap rows carry no label). So the labels
are a subset of the rows and hold nothing the scrubber shapes.

A method note (INFO, F11): re-scrubbing a STORED state is a proxy that can miss a change. Where the old opaque rule had
taken a glued key's whole 40+ run (`<opaque-redacted>`), the new rules write `…_sk-<redacted>` instead, and a re-scrub of
the stored text sees nothing to change. The exact check is the builder itself: `collect_v2` at the recorded commit with
the old and the new `common.scrub` gives 6,220 pre-fit items (6,196 rows after the manifest's 24 merged duplicates)
with 0 differing states, so the fit and the dataset bytes cannot differ; the lane's rebuild (not repeated here, optional)
is the same conclusion by a third route. The manifest's code hash for the exporter is the PIN file's sha256
(`2136062e0af69815…`).

## 5. Attack item 4: mutation (22:3xZ)

Harness: `<scratch>/vscrub1/mutate_v.py` = the lane's `<scratch>/scrub1/mutate.py` adapted: its 24 mutants imported
verbatim from the lane's file, the tree copied from the PIN copy (`git archive 2dbf1f4`: the exporter,
`known_values_check.py`, the test file, `tests/conftest.py`, `pyproject.toml`), run INSIDE `masked.sh` (the committed CLI
tests would otherwise read the real sources, F1), then 24 of this lane's own. KILLED only on a FAILED test (AF-AP-223);
each anchor must occur once. Two venues, the same verdict in both:
```
absent venue:  CONTROL (unmutated): rc=0 174 passed in 2.53s   ...   TOTAL {'KILLED': 39, 'SURVIVED': 9, 'INVALID': 0}
fakes venue:   CONTROL (unmutated): rc=0 174 passed in 2.59s   ...   TOTAL {'KILLED': 39, 'SURVIVED': 9, 'INVALID': 0}
```
The lane's 24 reproduce exactly: 23 killed, M16 (digits glue, sk) survives. (M6 fails 26 tests in the absent venue and 1
in the fakes venue: with every default source present only the in-process missing-source test reaches that branch.)

Mine, killed (16): `_` no longer separating in each of the four rules (V1-V4); the sk anchor written as a lookahead
(V7); `ghr` or `xoxs` dropped from a family (V8, V9); whole counted in the first file only (V10); a window required in
every file (V11); host forms dropped everywhere (V14); the api.env path typo (V19, by the membership assert at test
line 837); main exiting 1 (V20); the full source path in the refusal (V21); an unreadable source unnamed (V22); export
swallowing the refusal (V23); a raw-file floor of 64 bytes (V24).

Mine, SURVIVED (8), each a hole in what the tests pin, none a defect in the code as it stands:
| Mutant | What it means |
|---|---|
| V5, V6 | the AIza and xox anchors dropped (a letter glues): the ordinary-word guard pins the letter decision for sk and gh only; no ordinary word puts a letter before `AIza` or `xox?-`, so no measured cost |
| V12 | an 8-character variable not counted: the env-kind floor's boundary is not pinned |
| V13 | `TYPESAFE_BASE_URL` skipped in EVERY source: "its own source only" is not pinned |
| **V15** | **the bridge env read from `scripts/.pc-bridge.env` instead of the repo root** |
| **V16** | **the bridge env read as a raw file (its token never checked as a value)** |
| **V17** | **the pseudonym key path typo** |
| **V18** | **`GITHUB_TOKEN` dropped from the sources** |

V15-V18 (F8): of the five production sources only `api.env` (the membership assert) and `GH_TOKEN` (the exit-4 CLI test)
are pinned by a test; a regression in the other three entries passes all 174 tests, and in production it would disable
that part of the gate SILENTLY: the skip line goes to stderr, which push_clean discards (#291). The current five entries
are correct (they equal the premise's known_values_check invocation, and `.pc-bridge.env` resolves to the repo root).

## 6. Attack item 5: the siblings (22:3xZ)

**#291 (push_clean hides a refused sync): CONFIRMED.** Read: the `TRANSCRIPT_SYNC` block, `scripts/push_clean.sh:184-195` (sha256 prefix
e75dc227675dcb67, unchanged since 2dbf1f4). Reproduced in a scratch git repo (no remote) with a FAKE exporter that prints
one REFUSED line on stderr and exits 4, running the verbatim block (`sed -n 184,195p`), never push_clean itself:
```
--- refusal case:                  transcript sync: nothing new (or export unavailable)    block rc=0   stderr lines: 0
--- a clean run with nothing new:  transcript sync: nothing new (or export unavailable)    block rc=0   stderr lines: 0
```
The two cases print the same stdout line, rc 0, no stderr (`>/dev/null 2>&1` at line 185 drops the exporter's REFUSED
lines), nothing committed. `--lanes-live` pushes run with `TRANSCRIPT_SYNC=0` (line 64), so they never sync. The
protection holds (nothing is written); the refusal is invisible, and so is every "missing source, skipped" line (F8).

**#292 (the right side and the JSON-escape context): CONFIRMED and sharpened** (section 2): a key followed by a
non-ASCII letter survives at REAL length in all four families, because the opaque rule's trailing `\b` fails the same
way; a real-length xoxb followed by `_` leaks its last (secret) segment; through session_export's real `convert()`, a
short key at a line start inside a Bash command survives for all four families (canonical JSON writes `\n`). All
pre-existing (the old rules behave the same: 0 newly missed contexts).

**#293 (the other writers have no value gate): CONFIRMED.** None of the 11 importers of the rules calls the gate
(`known_values|value_hits|KnownValueRefusal|known_values_check`: 0 hits in each; `src/agent_factory/decisions/volatile.py`
names the file in comments only, it imports nothing). Through the real code (`<scratch>/vscrub1/writers_probe.py`, inside
`masked.sh absent`, fixture projects folder, outputs in scratch), a fake known value planted in the input:

| Writer | Output | 32-hex value | 16 letters, no digit | 14 chars with `!#` |
|---|---|---|---|---|
| `transcript_export.export` (control) | the digests | REFUSED, nothing written | REFUSED | REFUSED |
| `session_export.convert` (PIN copy) | event stream shipped to the PC | reaches it | reaches it | reaches it |
| `hiccup_scan.py` CLI | `docs/HICCUPS.md` (a COMMITTED file) | normalized away (a 20+ run becomes `T`) | reaches it (error first line) | reaches it |
| `chat_find.py --excerpt` CLI | stdout | normalized away | reaches it | reaches it |
| `jev.py`, `jev_context.py`, `laya_ft/teacher_label.py`, `harness-ports/bin/qwen_matrix.py`, `openjev_j2.py` | HTTP requests (and result files) | NOT run (an outward request): the payload is `scrub(text)`, and `scrub` keeps the value (shown) | same | same |
| `harness-ports/bin/hermes-session-export.py` | a file on the PC | NOT run (PC) | | |
| `laya_ft/build_dataset.py` | dataset.jsonl from committed text | a value must be committed first | | |

The committed page `docs/HICCUPS.md` is the one writer besides the digests whose output reaches origin with no value
gate.

## 7. Attack item 6: the other rules in the file, with fake inputs (22:5xZ)

SCRUB1 did not change these rules; every result below is identical under the old `scrub` (checked per case). Fake
values from `secrets` at run time; LEAKS = an 8-byte piece of the fake survives.

| Rule | Input | `scrub` (export's) | `scrub_payload` |
|---|---|---|---|
| opaque (40+) | a 48-hex token after a space, or glued after a letter | hidden | hidden |
| opaque (40+) | a 48-hex token glued AFTER or BEFORE a non-ASCII letter (`é`, `です`) | LEAKS | LEAKS |
| credential | `passphrase=`, `pwd=`, `credentials=`, `Cookie: session=` + 16 hex | LEAKS | LEAKS |
| credential | `access_token=`, `client_secret:` | hidden | hidden |
| credential | `{\"token\": \"<v>\"}` (escaped quotes inside decoded text) | LEAKS | hidden (R1 rule) |
| Bearer | `Authorization: Bearer <v>` | hidden | hidden |
| Bearer | `authorization: bearer <v>` (lower case) | LEAKS | hidden |
| Authorization | `Authorization: Token <v>`, `Authorization: Basic <b64>` | LEAKS, LEAKS | LEAKS, hidden |
| private key | a well-formed PEM block | hidden | hidden |
| private key | a PEM with 4-dash BEGIN/END lines; a key body with no header | LEAKS | LEAKS |
| bridge link | `https://<sub>.trycloudflare.com/exec` | hidden | hidden |
| bridge link | with userinfo (`https://zq:<v>@<sub>.trycloudflare.com/x`); a bare host | LEAKS | hidden |

The finding that matters (F12): the opaque rule, the backstop for every generic token (the bridge token, a key's hex),
uses `\b` on BOTH sides, so a 40+ run touching a non-ASCII letter on either side is never taken; this is #292's class
on the rule that catches everything else. The value gate still refuses such a run when it holds a KNOWN value (a
bridge-host test in section 3 shows the gate catching what `scrub` keeps). `scrub` (the digests' scrubber) lacks five
shapes that `scrub_payload` takes (lower-case bearer, Basic auth, escaped-quote credentials, URL userinfo, a bare bridge
host): by design (D-086 kept `scrub`'s output stable for its importers). The stale comment the lane found (A3) holds:
`scripts/transcript_export.py:90` says "32+ url-safe chars", the rule is `{40,}`.

## 8. Fresh gates, stale context, evidence audit (22:5xZ)

**The consumer set (contract item 4), re-run** in a static PIN copy (`git archive 2dbf1f4` of `scripts tests
harness-ports src docs .claude/hooks .claude/skills wiki` and the top-level context files, 65 MB, deleted after), inside
`masked.sh absent`:
```
15 files set=271f9e77620b
pytest-summary: 723 passed, 1 skipped in 89.65s (0:01:29)
pytest-summary: 723 passed, 1 skipped in 87.53s (0:01:27)
SKIPPED [1] tests/test_qwen_jev.py:37: LOUD SKIP: ... runs only in the PC's qwen-jev venv
```
Matches the lane's and the coordinator's counts. The Laya pair (`tests/test_laya_ft.py`,
`tests/test_laya_systemone_server.py`, 74 tests, 7-9 minutes, dataset rebuilds) was NOT re-run: section 4's exact
pre-fit comparison answers the question it guards.

**Stale context.** The new comment at `scripts/transcript_export.py:80-83` and the gate comment at 230-235 are accurate
(section 2b reproduces their numbers within corpus growth). The docstring's exit codes hold (0, 3, 4; an absent
`known_values_check.py` would exit 1 with a traceback before any write, the lane's own note). `AF-AP-224`'s row
(`docs/INCIDENT-LOG.md:765` at the PIN) reads PARTLY FIXED with #291-#293 open, as landed. `scripts/ap_screen.py` over the two
copies: the AF-AP-224 screen fires on the old exporter and 0 times on the new one (it still flags AF-AP-204a at
`scripts/transcript_export.py:327`, the `-home-user`-only transcript glob, the lane's A4, and AP-1 at 264, the token
variable read). Pre-existing and stale: the `32+` comment at line 90 (A3).

**Evidence audit.** The lane's scratch artifacts exist at the stated paths (`<scratch>/scrub1/`: `measure.py`,
`mutate.py`, `probe_fixture.py`, `probe_other.py`, four `m-*.json`). Re-derived from primary source: the mechanism of
#291 (`scripts/push_clean.sh:185-193`, reproduced), of A1's xoxb case (the rule stops at the last hyphen, the remainder under
40, reproduced), and of the byte identity (reproduced by file hash). Every count the lane reports that this lane could
measure without a real source reproduced: 174; 723/1; 23 of 24 mutants with M16 the survivor; 18 of 18 digests; 0 of
6,196 records; S1's 2 new redactions; digit glue 0. Not reproducible here by rule: the "known secret" column (0 known
secrets among the new redactions), the gate's cost with the real sources (0.69 s; 0.72-0.74 s with fakes of that shape), and the real
gate passing the real transcript (indirect evidence: the 20:27Z and 21:50Z syncs ran the new exporter and wrote files).
Chance matches of the raw key's hex windows (the lane's residual risk 1): the 18 digests hold 2,075 lower-case and 198
upper-case hex 8-grams, so about 3e-5 expected chance matches per export for a 32-byte key.

## 9. FINDING INVENTORY (no severity filter) (22:5xZ)

Evidence level: R = reproduced here through the named path; S = read from source; U = not verifiable by this lane.
Canonical path = the production consumer at the PIN (the PIN copy's bytes).

| # | Class | Finding | Evidence | Contract mapping | Canonical path | Material effect | Reproduction | Suggested fix |
|---|---|---|---|---|---|---|---|---|
| F1 | FOLLOW-UP | The committed test file reads the machine's REAL value-gate sources: 30+ CLI tests run `main()`, which always calls `export()` with the default `sources`, bound at definition time; the tests never replace `KNOWN_VALUE_SOURCES` (only a membership assert, `tests/test_transcript_export.py:837`); the exit-4 test swaps only `GH_TOKEN` (`:855`). Replacing the attribute does not reach `main()` (the brief's premise "the committed tests replace the sources" does not hold) | R (section 3 D) + S | none (item 3's gate tests use fixture sources in process, as asked) | yes | every run of the file, in CI, a coordinator gate or a lane, reads `.pc-bridge.env`, `api.env`, the pseudonym key and both token variables in the child; a delegate under "never read a real source" cannot run it unmasked; the production list is untestable (F8) | `masked.sh fakes` + `gate_probe.py` section D | resolve the list at call time (`sources=None` → read `KNOWN_VALUE_SOURCES` then) and drive `main()` in process with a fixture list in the CLI-shaped tests |
| F2 | FOLLOW-UP (#292) | A key followed DIRECTLY by a non-ASCII letter survives at REAL length in all four families (sk legacy/proj, ghp 40, AIza 39, xoxb 56), because the opaque rule's trailing `\b` fails too; a real xoxb followed by `_` leaks its last (secret) segment | R | none (the contract defines glue on the preceding side) | yes, `export()` → digest | a credential in CJK or accented text reaches origin unless the value gate knows it; pre-existing, 0 instances measured | `rules_probe.py` (right side), `e2e_probe.py` (`before é`, `before _`) | right anchor `(?![A-Za-z0-9])` on the four rules and the opaque rule, with a Laya re-check |
| F3 | FOLLOW-UP (#292) | JSON-escape context: through session_export's real `convert()`, a short key at a LINE START inside a tool input survives in all four families (canonical JSON writes `\n`); also after a literal `\n`/`\t`/`\r`/`\uXXXX` inside decoded text in every writer | R | none (letter glue was the lane's measured choice) | yes, `convert()` | short keys only: a 40+ run is taken by the opaque rule (8 raw-line instances, all taken) | `e2e_probe.py` (`tool_use input / line start`) | the lane's S1e anchor `(?:(?<![A-Za-z0-9])\|(?<=\\[nrt]))` |
| F4 | INFO | A short key glued after an ASCII letter or digit survives (`zqx<key>`, `zq1<key>`) | R | item 1 (decided by measurement; M16 survives by design) | yes | none measured (0 digit glue; letter glue = `task-` 15k+) | `rules_probe.py` | none; `(?<![A-Za-z])` stays the coordinator's option |
| F5 | FOLLOW-UP (#291) | push_clean hides a refused sync: `>/dev/null 2>&1` then "nothing new (or export unavailable)", rc 0; it also hides every "missing source, skipped" line; `--lanes-live` never syncs | R (verbatim block, fake exporter) | none (push_clean outside SCRUB1's boundary) | yes (the `TRANSCRIPT_SYNC` block, `scripts/push_clean.sh:184-195`) | the protection holds; a refusal or a silently skipped source is invisible | section 6 | test for exit 4 and print a REFUSED line on stderr; keep the exporter's stderr |
| F6 | FOLLOW-UP (#293) | No other writer has a value gate: session_export's events carry any fake known value; `hiccup_scan`'s page `docs/HICCUPS.md` (COMMITTED) and chat_find's excerpts carry one that survives their normalization (under 20 characters with no digit, or with symbols); five network writers send `scrub(text)` | R (4 writers) + S (the rest) | none (item 2 covers transcript_export.py) | yes | `docs/HICCUPS.md` is a second origin-bound writer with no value gate | `writers_probe.py` (3 value shapes) | the same gate on HICCUPS.md's write first, then session_export's ship |
| F7 | FOLLOW-UP | Value-gate blind spots inherited from known_values_check (per contract): a CUT copy of a non-windowed value (8-15 chars, or no digit, or a character outside TOKENISH), base64/hex of an env value, a case change, the raw key in default `xxd` layout (4-hex groups) or an upper-case host. known_values_check's docstring says "an `xxd` column" still counts: true for `xxd -p` only | R | item 2 (the logic of known_values_check, by design) | yes | a known value in these forms reaches the digest | `gate_probe.py` sections A, B, E | fix the docstring; windows for 8-15 char values; the raw form's 4-hex grouping |
| F8 | FOLLOW-UP | The production source list is pinned only for `api.env` and `GH_TOKEN`: mutants V15 (bridge env read from `scripts/`), V16 (bridge env read as raw), V17 (pseudonym key path typo), V18 (`GITHUB_TOKEN` dropped) pass all 174 tests; in production such a regression silently disables that source (the skip line is discarded, F5). The five entries are correct today | R (mutation, both venues) | none | yes | a future regression goes unseen | `mutate_v.py` | a test asserting the exact five-entry tuple with `.pc-bridge.env` resolved to the repo root |
| F9 | INFO | Other survivors: V5/V6 (AIza and xox letter anchors unpinned; no ordinary word at stake), V12 (the 8-char env floor boundary), V13 (TYPESAFE skipped in every source: "own source only" unpinned) | R | none | yes | none today | `mutate_v.py` | pin with one assertion each if wanted |
| F10 | INFO / U | Env parsing edges (known_values_check's parser): `KEY=v # comment` keeps the comment in the value, so the value never matches; a source-kind typo is read as a raw file silently; a FIFO source HANGS the export at `open()`; an empty or dangling-symlink source is "missing" (known_values_check's CLI exits 2 on a valueless source). Whether the REAL env files use inline comments is not verifiable here | R (fixtures) / U (real files) | item 2 (inherited logic) | yes | if a real file had an inline comment, that value would be unprotected | `gate_probe.py` sections C, E, F | the coordinator can print, per key, only whether the parsed value holds whitespace or `#`; validate the kind |
| F11 | INFO | The lane's Laya re-scrub of STORED states is a proxy that can miss a change where the old opaque rule had taken a glued key's whole run; the exact check agrees (0 of 6,220 pre-fit items differ; 0 of 6,196 rows) | R | item 4 | yes (`collect_v2`) | none (the claim holds) | `laya_rescrub.py` | use the builder's pre-fit comparison in future lock checks |
| F12 | FOLLOW-UP (#292) | The opaque rule (the generic backstop) has `\b` on BOTH sides: a 40+ token glued to a non-ASCII letter on either side is never taken | R | none | yes | an unknown generic token next to CJK/accented text reaches the digest | section 7 | as F2, for the opaque rule |
| F13 | INFO | A refusal line prints an env line's "name" verbatim: a malformed line whose part before `=` holds secret text puts it on stderr | R (fixture) | item 2 ("names and counts only") holds for well-formed files | yes | hypothetical (a malformed env file) | section 3 E | print the name only when it matches `[A-Za-z_][A-Za-z0-9_]*` |
| F14 | INFO | `scrub` (the digests') lacks shapes `scrub_payload` takes (lower-case bearer, Basic, escaped-quote credentials, URL userinfo, bare bridge host) by design (D-086); both lack `passphrase=`, `pwd=`, `credentials=`, `Cookie: session=`, `Authorization: Token`, a PEM with malformed header lines | R | none | yes | pre-existing shape gaps; the gate covers known values only | section 7 | a later scrubber increment |
| F15 | INFO | Identifiers with a prefix after `_` are now redacted (`use_sk-learn-pipeline-for-this` → `use_sk-<redacted>`): the contract's intended reach; 0 such words in the measured corpora apart from this lane's own probe strings | R | item 1 | yes | none measured | section 2, 2b | none |
| F16 | INFO | The lane's table reproduces as counts: S1 2 new redactions outside this lane's transcript, both underscore-glued key shapes of the lane's lengths; digit glue 0; no anchor adds 18,260 now (17,692 then; the corpus grew). One raw-line `gh` case the lane called visible, this probe finds taken by the opaque rule | R | item 1 | yes | none | `measure_v.py`, `attrib.py` | none |
| F17 | INFO | Stale comment `scripts/transcript_export.py:90-91` ("32+"; the rule is `{40,}`), the lane's A3, pre-existing, listed in #292 | S | none | n/a | none | read | fix with #292 |
| F18 | INFO | `main()` exports only the newest transcript under `-home-user` (AF-AP-204's tell, `:327`); this session's `-home-user-agent-factory` transcript is never exported (the lane's A4, in #291's text) | S | none | yes | a transcript is never digested | read | glob every project folder |
| F19 | INFO | Chance matches of the raw key's hex windows: 2,075 lower-case and 198 upper-case hex 8-grams in the 18 digests, about 3e-5 expected per export for a 32-byte key | R (counts, no secret) | none | yes | negligible false-refusal risk | section 8 | none |

## 10. GATE RECOMMENDATION

**MERGE-READY-WITH-FOLLOWUPS** (depends on two things this lane could not reproduce by rule: that none of the new
redactions is a known secret, and that the real gate passes the real transcript today; the lane measured both with the
real sources, and the 20:27Z and 21:50Z syncs are indirect evidence for the second).

Blocking predicate applied: a finding blocks only if it (1) contradicts a frozen criterion of `SCRUB1-brief.md` items
1-4 or an applicable repository-wide invariant, (2) reproduces through the exact production path at the PIN, (3) changes
the claimed output, state, evidence, determinism or integration behaviour, (4) has a deterministic discriminator, and (5)
belongs inside SCRUB1's boundary. No finding meets all five. Every contract criterion reproduced: item 1 (`_`/`__` glue
taken in all four rules, in decoded text and in canonical JSON; the measured choice of no letter/digit anchor holds;
0 old-to-new regressions), item 2 (exit 4, nothing written, names and counts only, sources named once, a missing source
skipped with one line, the TYPESAFE host not blocking, the bridge host still counting), item 3 (174 tests in two
venues; mutation 23/24 of the lane's plus 16/24 of mine killed), item 4 (723 passed, 1 skipped twice; 18 of 18 digests
byte-identical; 0 of 6,196 Laya rows, exact pre-fit check). F2/F3/F12 reach a digest or the session export through the
real path, but they are pre-existing, outside the contract's definition of glue, and already registered (#292); F1 and
F8 are test gaps, not defects in the shipped code; F5 and F6 are outside the boundary and registered (#291, #293). No
CONTRACT-DEFECT: nothing falsifies evidence, corrupts state or loses data.

## 11. NOT done

- No real secret source read, in process or by the CLI: the "known secret" column of the lane's table, the gate's cost
  with the real sources (0.69 s, 12 forms, 327 windows; re-measured with fakes of that shape only) and the real gate's
  pass on the real transcript are the lane's, not reproduced here.
- push_clean not run (its sync block ran verbatim in a scratch repo with a fake exporter). No PC bridge.
- The Laya pair (74 tests) and the dataset rebuild not run (optional; the exact pre-fit check answers the question).
- The network writers (jev, jev_context's model calls, teacher_label, qwen_matrix, openjev_j2) and
  hermes-session-export (PC) not run: their payload is `scrub(text)`, shown to keep a 32-hex value.
- No git write; no tracked file touched; the only file in the tree is this report. Scratch: `<scratch>/vscrub1/`
  (the instruments, 664 KB, kept for a rerun; every build and output folder deleted). A bytecode cache this lane's import
  wrote into `<scratch>/scrub1/__pycache__` was removed.

