# SCRUB2 report (task #292 widened by VERIFY-SCRUB1; lane opened 23:2xZ, 2026-09-25)

Status: DONE, NOT LANDABLE ALONE. Items 1-5, 7 and 8 built and tested in the four boundary files (52 of 52 mutants
killed, the touch proof 0 opens and 0 lookups, the Laya lock 0 changed items, the recorded manifest's code hash
regenerated). Landing needs three edits OUTSIDE the boundary in the same commit (section 7: set A 8 failed without them,
746 passed, 1 skipped with them, twice), prepared as patches in scratch and not applied. The OpenJev manifest is left as it
is (section 7, a deviation).

## 1. Premise re-measured (23:2xZ, local HEAD 83e806c "SCRUB2 briefed ..."; the PIN 4b3b699 is its parent)

- Ids: the PIN is 4b3b699 ("ledger: the S1-RATE entry counted 202 injection records...") and the brief's commit 83e806c ("SCRUB2 briefed ..."), their origin ids after the 23:2xZ push rewrote the local ones the dispatch named (identical trees; this report cites origin ids only).
- `git diff --stat 4b3b699..HEAD`: docs/INCIDENT-LOG.md, the SCRUB2 brief, todo/BUILD-TASKLIST.md only; no file in this
  lane's boundary changed after the PIN.
- `git log --format=%h 49bf75e..HEAD -- <the five files>` | wc -l: 0 (matches).
- The five rule lines at `transcript_export.py@4b3b699:84-87` and `@4b3b699:91` (`sk-<redacted>` ... `<opaque-redacted>`): identical to the brief's grep (matches).
- `def export` at `transcript_export.py@4b3b699:296` with `sources=KNOWN_VALUE_SOURCES`; `written = export(path, a.out, a.cap)` at `transcript_export.py@4b3b699:333` (matches).
- `KNOWN_VALUE_SOURCES` and `GH_TOKEN` refs at `test_transcript_export.py@4b3b699:837`, :850, :855, :857, :861 (matches).
- Callers of export/main among tests/*.py and harness-ports/tests/*.py: only tests/test_transcript_export.py calls=9 (matches).
- The two dataset manifests exist (matches). VERIFY-SCRUB1's scratch holds the 14 entries listed (matches).
- Disk: 1.8G free on / at the start.

Verdict: the premise holds. No CONTRACT-INVALID. This lane's own transcript is `subagents/agent-af05ca4736ed56c8c.jsonl`
(its meta.json says "SCRUB2"); every corpus count below excludes it, because it holds this lane's own fake-key probes.

## 2. The brief's question: which writers scrub raw JSON text (23:3xZ)

Traced from each call site (a literal sweep of `scrub(`, `scrub_payload(`, `scrub_strict(`, `_scrub(` outside tests, after
`graft ask` gave the lexical start list):

| Writer | What it scrubs | Raw JSON? |
|---|---|---|
| `transcript_export.export` (the committed digests) | the decoded turn text (`json.loads`, then the text blocks) | no |
| `session_export.convert` (the event stream shipped to the PC) | `canon(obj)` = `json.dumps(sort_keys, ensure_ascii=False)` for tool_use inputs (`text = canon(inp)`, session_export.py:512), unknown assistant blocks (:519), hooks and notices (:588-592) and system records (:595); decoded text for text, thinking and tool results | **yes** |
| `harness-ports/bin/hermes-session-export.py` (PC) | each Hermes message's stored `content`; tool-result bodies when `--tool-body-cap` > 0 | **yes, inferred**: Hermes stores tool results as JSON strings (not verifiable here: no Hermes source in this sandbox) |
| `harness-ports/bin/qwen_matrix.py` | the messages parsed from that export (`_scrub_messages`) | **yes, inferred** (the same bodies) |
| `chat_find.py` (`window`, `hit_row`) | `flatten()` joins a tool input's decoded strings with newlines; names | no |
| `hiccup_scan.py` (`excerpt`, `_plain`, `_jev_cell`) → `docs/HICCUPS.md` | decoded result text and names | no |
| `jev.py`, `jev_context.py`, `laya_ft/teacher_label.py`, `openjev_j2.py` | each decoded string, THEN `json.dumps` of the request | no (the escapes are added after the scrub) |
| `laya_ft/build_dataset.py`, `common.py` | committed markdown text | no |

**Does any keep an escape the exporter's own writes drop?** Yes. The digests are decoded: a JSON `\n` is a real newline
there, a `\u00e9` is the letter. `session_export`'s canonical JSON keeps `\n`, `\r`, `\t`, `\b`, `\f` and `\u00XX`
(Python's short escapes and its escape for every other control character; `ensure_ascii=False` keeps non-ASCII literal).
Hermes' stored JSON (inferred: Python's default `ensure_ascii=True`) would also keep `\uXXXX` for every non-ASCII letter,
so a key glued after `é` in the decoded text (taken since SCRUB1) sits after `\u00e9` (a hex digit or letter) in that raw
view and is not taken. That is the reason to extend the escape anchor to `\uXXXX` (item 2).

## 3. Measurement, item 6 (00:2xZ on 2026-09-26)

**Instruments** (scratch `<scratch>/scrub2/`, never committed; `<scratch>` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad`):
`cands.py` builds each candidate as the PIN's own `SECRET_PATTERNS` with ONE change (it asserts that the rebuilt PIN rules,
the credential rule included, equal the PIN's patterns byte for byte); `measure2.py` runs each candidate over the corpora
in process, and for any text a candidate scrubs differently it re-runs both scrubs with CHARACTER PROVENANCE (which
original characters each hides; asserted equal to the real `re.sub` output), so NEW (hidden now, visible under the PIN)
and LOST (hidden by the PIN, visible now) are exact, not inferred from an output diff. It prints masked shapes only
(length, character classes, a provider prefix, the class of the neighbouring characters). `probe_new.py` lists one
candidate's NEW regions by record time, the head before the value (a credential name, or an Authorization scheme from a
fixed list), the value's casing pattern, a hash (repeats show) and whether the exact value occurs in a tracked file
(`committed`, checked in memory, transcripts/ excluded). Self-test first on a fake-key fixture: every predicted NEW region
appeared, and a LOST region built on purpose (a `ghp_` key glued to a 39-character `_` tail) was found and classed.

**Corpora** (the PIN = 4b3b699's exporter, identical to the tree's): the 18 committed digests (3,577,907 bytes); the main
transcript fixed at its last complete line (744,582,551 bytes, 141,717 lines, 3,996,325 strings); 303 subagent
transcripts (509,612,596 bytes, 122,698 lines, 3,231,206 strings; this lane's own excluded); the second project root
(3,074,681 bytes, 519 lines, 13,731 strings). Views: `dec` = every string of every record, decoded (the digests' view);
`raw` = the raw JSONL line (the raw-JSON writers' view; an upper bound of what `session_export` scrubs as JSON).
Commands: `python3 measure2.py <out>.json [--cands ...] <files>` per corpus; `python3 probe_new.py <cands> dec|raw <files>`.

Cells: texts changed / NEW regions / LOST regions.

| Change (candidate) | digests | main dec | main raw | subagents dec | subagents raw | root2 | Laya v2 / v1 items changed | Decision |
|---|---|---|---|---|---|---|---|---|
| R: provider right anchor `(?![A-Za-z0-9])` | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 | 0/0/0 | 0 | 0 / 0 | **take** |
| EALL: left anchor also after `\[nrtbf]` or `\uXXXX` | 0/0/0 | 0/0/0 | 6/0/8 | 0/0/0 | 1/1/0 | 0 | 0 / 0 | **take** |
| (E3 `\[nrt]` = E5 `\[nrtbf]` = EALL on these corpora; EU `\uXXXX` alone: 0 everywhere) | | | | | | | | |
| OU: opaque rule, `\b` or ASCII `\b` on each side | 0/0/0 | 0/0/0 | 0/0/0 | 1/2/0 | 1/2/0 | 0 | 0 / 0 | **take** |
| (OA: ASCII `\b` only: the same counts here; OU keeps every PIN match by construction, OA can drop a dash) | | | | | | | | |
| `passphrase` in the credential names | 0 | 0 | 0 | 1/1/0 | 1/1/0 | 0 | 0 / 0 | **take** |
| `pwd` in the credential names (N-pwd) | 0 | 14/15/0 | 7/13/0 | 5/5/0 | 4/4/0 | 0 | **16** / 0 | reject: every value a path (`PWD=`, `pwd=/home/...`) |
| PWD2: own rule, value not a path or reference | 0 | 0 | 0 | 2/2/0 | 2/2/0 | 0 | 0 / 0 | **take** |
| `credentials` in the credential names (N-credentials) | 0 | 5/7/0 | 9/19/0 | 65/65/0 | 55/65/0 | 0 | 0 / 0 | reject: 61 of 65 are `credentials: LoginRequest`, a Python annotation in a vendored example |
| CRED2: own rule, `=` or a quoted key, not a path | 0 | 0 | 5/10/0 | 1/1/0 | 1/1/0 | 0 | 0 / 0 | **take** |
| COOKIE: `Cookie:`/`Set-Cookie:` with a `name=value` of 8+ | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | **take** (0 cost) |
| AUTH: `Authorization: <any word> <token>` | 1/1/0 | 41/41/0 | 24/41/0 | 60/77/0 | 35/58/0 | 0 | 0 / 0 | reject: takes a word after this repo's `AUTHORIZATION:` brief headings |
| AUTH2: the same after a known scheme (Token, Basic, Bearer any case, Digest, Negotiate, NTLM, ApiKey, Key, SSWS) | 1/1/0 | 23/23/0 | 13/23/0 | 38/55/0 | 27/50/0 | 0 | 0 / 0 | **take** |
| P3: PEM header lines with 3+ dashes, to END or the end of the text | 0 | 1/1/0 | 1/1/0 | 12/16/0 | 8/14/0 | 0 | 0 / 0 | reject: no END line, it hides the rest of a tool result (up to 15,522 characters) |
| (P2: 2+ dashes: the same counts) | | | | | | | | |
| P3E: 3+ dashes, END line required (the PIN's rule unchanged before it) | 0 | 0 | 0 | 4/4/0 | 2/4/0 | 0 | 0 / 0 | **take** |
| **FINAL** (every **take** row) | 1/1/0 | 23/23/0 | 24/33/8 | 45/65/0 | 33/61/0 | 0 | **0 of 6,220 / 0 of 1,788 (both v1 commits)** | |

**What the NEW regions of FINAL are** (`probe_new.py`, masked):
- AUTH2: every value is committed text or a one-off token after `Bearer`: the documented example in
  `docs/INCIDENT-LOG.md:648` (`secret123`; line 646 before the 00:15 commit added lines above it)
  and `tasks/briefs/pc/pc-o4.md:10` (`secret123`), a documented fake: `Token` + 9 characters, 19 regions in main, the one
  digest region, `chat-2026-09-17.md` line 1430, inside backticks), the documented fake in
  `tasks/briefs/continuity/S198A-report.md:420` (`Basic` + 16), the fixtures of the session-export tests (lower-case
  `bearer` and `Basic` values, 5-11 repeats each), and 2 uncommitted values after `Authorization: Bearer` that the
  Bearer rule's class stops at (they start with `~+/=` characters). 0 prose.
- CRED2 raw: 5 distinct uncommitted values behind a JSON key `credentials` in the record structure (the decoded view
  yields values, not keys, so it never sees them). That is the shape the rule is for.
- PWD2, CRED2, `passphrase`, P3E: VERIFY-SCRUB1's own probe lines (its F14 shapes) and malformed-PEM probe strings of two
  scrubber lanes (09-23, 09-25); one uncommitted 13-character `pwd` value starting with punctuation.
- OU: one 41-character run of mixed case and digits glued after a non-ASCII letter (09-24, uncommitted): F12's class.
- EALL: one committed placeholder-shaped `sk-` string at a raw line start (already hidden in the decoded view).

**LOST (old-to-new)**: FINAL loses 0 regions in every decoded view and in the digests. In the main raw view it shows 8
one-character regions, each the `n` of a JSON `\n` escape: the PIN's opaque rule hid `n` + a 40+ key run, and FINAL's
provider rule now takes the key itself (`\nsk-<redacted>`). The key stays hidden; the letter must stay, or the escape
breaks (`\sk-` is not a JSON escape, and session_export's canonical JSON must stay valid: its R1 test parses it).
Built by hand, one more LOST class exists (the self-test): a `ghp_`/`xox` key glued to a `_` tail of under 40
characters; the tail (not the key) was hidden by the opaque rule, and now shows. 0 instances in any corpus.

**The Laya lock, pre-fit** (`python3 laya2.py <cands>`: `collect_v2` / `collect` with `common.scrub` bound to the PIN's
scrub and to each candidate, whole items compared): v2 at 434b727 6,220 items, v1 at eb256f4 (the OpenJev manifest's
commit) and at 0b342c7 (the v1 test's) 1,788 items each; FINAL and every **take** row: 0 differing. The check is not blind:
N-pwd changes 16 v2 items.

**Known values** (not checkable here: this lane reads no real source): the new exporter's digests of this session's
transcript, written with `sources=()`, are listed in section 7 for the coordinator's known-value check at landing.

## 4. What changed (00:4xZ)

`scripts/transcript_export.py` (the rules are the measured FINAL set, one pattern tightened: see below):
- Items 1-2: the four provider rules use `_KEY_L` = `(?:(?<![A-Za-z0-9])|(?<=\\[nrtbf])|(?<=\\u[0-9A-Fa-f]{4}))` and `_KEY_R` =
  `(?![A-Za-z0-9])`; the opaque rule's ends are `(?:\b|(?a:\b))`; the comment above the providers says why; the stale
  "32+" comment (F17) now says 40+.
- Item 3: `passphrase` joins `_NAME` and `_WORD`; four rules after the Bearer rule (Cookie, Authorization after a known
  scheme, `pwd` and `credentials` with a value that is not a path); a lenient private-key rule (3+ dashes, END line
  required) right after the PIN's own, which is unchanged. Its header spaces are `[ \t]*`, not the measured `\s*`: a header
  is one line (a narrower language than the measured one; section 7 re-measures the landed file itself).
- Item 4: `known_values(sources)` and `export(..., *, sources)` have no default; `main(argv=None)` passes
  `KNOWN_VALUE_SOURCES` as it finds it when it runs; the gate comment says why (F1).
- Item 5: a source kind other than env, env-file, raw-file refuses before any source is read; the raw key is read through
  `known_values_check._read_regular`; the docstring's exit-4 line names both.

`scripts/known_values_check.py`: `_read_regular` (one `O_RDONLY|O_NONBLOCK` open, `fstat`: a directory raises
IsADirectoryError, any other non-regular file `NotRegularFile`, an OSError; links are followed) for every source read
(env, token and raw files); `_env_values` prints a name only when it matches `[A-Za-z_][A-Za-z0-9_]*`, else
`<malformed line N>`, N counted on "\n" as grep counts (the edit-snapshot screen flagged `splitlines` numbering, AF-AP-132;
a lone \r still ends an entry, so parsing is unchanged). Docstring updated.

`tests/test_transcript_export.py`: the CLI helpers run `main()` in process with fixture sources (fakes beside the output);
an autouse fixture sets `MOD.KNOWN_VALUE_SOURCES` to a tripwire (a kind the gate refuses before any read) in every test;
`PRODUCTION_SOURCES` is taken at import for the pin; the exit-4 CLI test uses fixture sources (an env file and a
variable); 21 new tests (the item 4 pins, item 5, the F9 pins, the right-side and escape grid with its SCRUB1 negative
control, the xox tail, the opaque grid with both one-boundary controls, the item 3 shapes and 23 ordinary texts, and the
end-to-end runs through `main()` and `session_export.convert()`). `tests/test_known_values_check.py`: `run()` takes a
timeout; 2 new tests (a FIFO, a device and a directory through all three file flags; a malformed name and its line).

## 5. Tests red first, then mutation (00:4xZ)

All runs of `tests/test_transcript_export.py` so far are inside VERIFY-SCRUB1's `masked.sh absent` (a private mount
namespace, every production source unreachable), on copy roots built by `<scratch>/scrub2/sync_tree.sh`.

Green on this lane's files: `207 passed in 2.30s` (both changed test files).

**Red run: the new tests against the PIN's scripts** (`sync_tree.sh <dest> pin`: 4b3b699's exporter and value check, this
lane's tests): `41 failed, 166 passed in 41.79s`. Each new rule or gate test reds for its own reason:
`_misses2` lists the escape and right-side contexts; the xox test shows the last segment; the opaque test fails at
"after é"; the shapes test at `passphrase=`; the passphrase chain test shows `password=<redacted>` swallowing the name;
the convert() test lists leaked `sk-`/`ghs_` keys (F3); both FIFO tests hit their 20 s timeout (F10's hang); the
malformed-name tests print the part before `=` (F13); the kind typo exits 0 with no refusal. Five tests red only on the
API change (`main()` takes no argv on the PIN: `_run`, the main-reads test, the tripwire test, the --help test, the
end-to-end digest test): their exact-reason controls are the mutants below. Tests that pass on the PIN by design: the
production pin, the letter pin, the floor, the TYPESAFE scope (each a regression guard, killed by its V-mutant), the
two negative-control tests (they assert the old rules' misses), the ordinary-text test.

**Mutation** (`<scratch>/scrub2/mutate2.py`, inside `masked.sh absent`; the unmutated control first, KILLED only on a
FAILED test, an error-only run INVALID, every edit's anchor exactly once; 52 mutants in two runs):
```
CONTROL (unmutated): rc=0 207 passed in 2.27s                                  (both runs)
mutants 0-25:  TOTAL {'KILLED': 26, 'SURVIVED': 0, 'INVALID': 0}
mutants 26-51: TOTAL {'KILLED': 26, 'SURVIVED': 0, 'INVALID': 0}
```
Rules: R1-R5 (each right anchor back to \b; `_` glues on the right), E1-E3 (no \uXXXX; no \b\f; no escape anchor), L1-L5
(`_` glues on the left; each rule's left anchor dropped; L4/L5 are VERIFY-SCRUB1's surviving V5/V6), O1-O4 (\b only;
ASCII only; the union on one end only), N1-N2, P1-P2, C1-C2, K1-K2, A1-A2, M1-M2 (each item 3 shape widened to its
rejected form, or removed). Sources: S1 (the definition-time default restored), S2 (the gate off by default), S3 (an
environment switch), S4 (a CLI option), S5 (known_values keeps a default). Reads: F1-F7 (no regular-file check; a plain
open in _env_values, for the raw key, in the CLI; the malformed name verbatim; splitlines numbering; no kind check).
VERIFY-SCRUB1's V12, V13, V15-V20, V23 and the lane's M1/M9 on the new code. Every one killed by a FAILED test.

## 6. Item 4's proof: no committed test touches a real source (00:4xZ)

Two instruments, one run of both changed test files under each (`<scratch>/scrub2/touch_proof.sh`, inside `masked.sh`):
`strace -f -qq -e trace=%file` (every syscall that names a file, in every process the run starts), counted per source
path; and a `sitecustomize` (`<scratch>/scrub2/envlog/`) that logs each lookup of `GH_TOKEN` or `GITHUB_TOKEN` in
`os.environ`, present or not, with its caller (names only). The copy root's `.pc-bridge.env` is the path the exporter
resolves (beside the repo root of the script).
```
(c) negative control: the PIN's tests and scripts (4b3b699), fakes venue (all five sources present as fakes)
184 passed in 6.62s
syscalls naming <copy>/.pc-bridge.env: 61 (opens: 30) | /root/.codiv/api.env: 60 (opens: 30) | .../pseudonym.key: 60 (opens: 30)
GH_TOKEN/GITHUB_TOKEN lookups: 94  (30 + 30 transcript_export.py@4b3b699:264, the gate's `os.environ.get`;
                                    15 + 15 test_known_values_check.py@4b3b699:22, its `dict(os.environ)`;
                                    2 + 2 test_transcript_export.py@4b3b699:855 and :861, the exit-4 test's `GH_TOKEN=fake`)
(a) this lane's tests and scripts, fakes venue:   207 passed in 4.86s
syscalls naming <copy>/.pc-bridge.env: 1 (opens: 0) | /root/.codiv/api.env: 0 | .../pseudonym.key: 0 | the tree's .pc-bridge.env: 0
GH_TOKEN/GITHUB_TOKEN lookups: 0
(b) this lane's tests and scripts, absent venue:  207 passed in 4.60s
every source path: 0 syscalls (opens: 0); GH_TOKEN/GITHUB_TOKEN lookups: 0
```
The one syscall in (a) is pytest's collection walk: a `newfstatat` of each entry of the rootdir (after probing
`<entry>/pyvenv.cfg`), never an open; it exists only because the fakes venue writes a `.pc-bridge.env` into the copy root.
To reach 0 lookups, `tests/test_known_values_check.py`'s `run()` now copies the environment without the two token
variables (its children never need them); before, its `dict(os.environ)` read both values for every CLI child.
Structural guard beside the proof: the autouse tripwire (any `main()` call without fixture sources refuses on an unknown
kind, before any read), `test_export_and_known_values_take_their_sources_from_the_caller` and
`test_nothing_outside_the_process_can_replace_the_sources` (no CLI option, no environment read but the env-kind branch, one
assignment of the tuple). Mutants S1-S5 are killed by them.

## 7. The landed file measured, the Laya lock, the digests, the gates (01:1xZ)

**The landed exporter as its own candidate** (`cands.py` LANDED = the tree's file; `measure2.py --cands LANDED` over the
same corpora): digests 1/1/0, main dec 23/23/0, main raw 24/33/8 (the 8 escape letters), subagents dec 45/65/0, raw
33/61/0, root2 0: equal to the measured FINAL in every cell (the `[ \t]*` tightening changed nothing here).

**Item 8, the Laya lock** (the builder's pre-fit comparison, `python3 laya2.py --module scripts/transcript_export.py`):
```
v2 collect_v2 at 434b727dfd: PIN scrub 6220 items | landed exporter: 6220 items, differing from the PIN scrub: 0
v1 collect at eb256f49c0:    PIN scrub 1788 items | landed exporter: 1788 items, differing from the PIN scrub: 0
v1 collect at 0b342c7a29:    PIN scrub 1788 items | landed exporter: 1788 items, differing from the PIN scrub: 0
```
0 changed items, so K265's step (SCRUB1-report.md section 6):
`HF_HUB_OFFLINE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --version 2 --commit 434b727dfd2b6daa5aa3cf4d638e706f5dfa59cb --out <scratch>/scrub2/v2new --model-dir /root/hf-laya-probe/hub/models--convaiinnovations--laya/snapshots/1c5edc17a7acd8701df6fc341c0d179f1c62c982/typed-decisions`
(39 s, rc 0): `dataset.jsonl` sha256 99070c33830832ca11e64226eddac1934ccd300c73b4d5d8d8c7bf5a36271f9d, 12,800,855 bytes = the
record's; the manifest differs from the record in one line, the exporter's hash (2136062e... to 6ad316dc...). Copied over
`docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json` (git diff: 1 insertion, 1 deletion).
Then `bash scripts/test_summary.sh tests/test_laya_ft.py -k "version_2_record or version_1_is_byte"` (shared tree; these
tests build at recorded commits and need .git; they never reach the gate): `pytest-summary: 2 passed, 42 deselected in 107.76s (0:01:47)`.

**The OpenJev (v1) manifest: NOT regenerated (a deviation from item 8's "each manifest").** v1 rebuilt with the new code
at its commit (eb256f4) and at the v1 test's (0b342c7): `dataset.jsonl` sha256 d7cd9b49abac267bb9b5290641ea353180a9a61047ce6c590809520b085cea1c
both times = the record's, so its data is locked. But its manifest is a historical record of the 09-24 build: four of its
code hashes differ from today's files (`decide-harvest`, `build_dataset.py`, `common.py`, the exporter), today's builder
adds a `fit.py` entry and a `repeated_finding_ids` field, and no lane regenerated it after SESSION-EXPORT, SESSION-EXPORT-R1
or SCRUB1 changed the exporter (its one commit is 1958d59). Changing only its exporter line would record a code state that
never built it; K265's step would rewrite five code entries and a field. Its test compares the dataset hash only. The
rebuilt manifest is at `<scratch>/scrub2/v1-eb256f4/manifest.json` if the coordinator wants the wholesale refresh.

**The digests for the known-value check** (`<scratch>/scrub2/digests.py`): this session's main transcript fixed at
744,747,851 bytes, exported by the landed exporter and by the PIN's, both `sources=()` (no real source read):
`files new=19 pin=19 same set=True`, `identical: 18 of 19; differ: [('chat-2026-09-17.md', 1, 230227, 230228)]` (the
documented `Authorization: Token` example, one line). **The new digests are in `<scratch>/scrub2/digests-new/`** (19 files,
3,582,072 bytes); the coordinator's known-value check runs there (`known_values_check.py --env-file .pc-bridge.env
--env-file /root/.codiv/api.env --skip TYPESAFE_BASE_URL --raw-file /root/.config/session-export/pseudonym.key --env GH_TOKEN
--env GITHUB_TOKEN <scratch>/scrub2/digests-new/`). Every new redaction only hides more: nothing the PIN hid is shown.

**Set A** (the 15 files of SCRUB1-report.md section 5), static copy (`git archive HEAD` of scripts tests harness-ports src docs
.claude/hooks .claude/skills wiki and the top-level context files, 65 MB; this lane's four files on top), `masked.sh absent`:
```
this lane's four files only:                      pytest-summary: 8 failed, 738 passed, 1 skipped in 94.83s (0:01:34)
                                                  pytest-summary: 8 failed, 738 passed, 1 skipped in 94.34s (0:01:34)
plus the three proposed patches below (scratch): pytest-summary: 746 passed, 1 skipped in 97.91s (0:01:37)
                                                  pytest-summary: 746 passed, 1 skipped in 96.25s (0:01:36)
15 files set=271f9e77620b
```
**The 8 failures are consumers that pin the old rule set, in three files outside this lane's boundary (orchestration 0j's
class: a file this lane changes is hashed or pinned by another's):**
1. `scripts/session_export.py` `PATTERN_NAMES` (7 of the 8): a positional list of 18 names for `SECRET_PATTERNS` +
   `PAYLOAD_PATTERNS`; `gate_patterns()` falls back to `pattern-N` names when the count differs, and the leak gate's two
   exemptions (a tool or call id, a committed run) are keyed by the name `opaque-run`, so they stopped applying. Patch:
   `<scratch>/scrub2/patches/session_export-PATTERN_NAMES.patch` (5 names in place: private-key-malformed, cookie,
   authorization-scheme, pwd, credentials; 23 names for 23 patterns). No committed file pins `session_export.py`'s hash
   (`git grep`: two reports and a digest's text); `code_hashes()` records it, with the exporter's, in each session export's
   own manifest at run time, as it did for SCRUB1's change.
2. `tests/test_session_export.py` (2 of the 8 after patch 1): its oracle's typed copy of the opaque rule
   (`ORACLE_SHAPES[0]`, compared with `RUN_SHAPES` by design) and the leak-gate test's pinned total (10: the lower-case
   `authorization: bearer` fixture row is now also the `authorization-scheme` shape, 11). Patch:
   `<scratch>/scrub2/patches/test_session_export-oracle-and-gate-total.patch`.
3. `tests/test_jev_locate_echo.py` (1 of the 8): its de-vacuous sweep needs 3 unstable tails, and one was built as
   `chr(0xe9) + "A" * 1100`, commented "a run the whole-text scrub leaves": F12's leak itself, which item 1 closes (with the
   union boundary no 40+ run of word characters is left). Patch: `<scratch>/scrub2/patches/test_jev_locate_echo-third-glued-key.patch`
   (a third letter-glued fake key, `xoxb-` + 20; the comment corrected). Its docstring still says "tail cuts on a run".
These edits were made ONLY in the scratch gate copy; the shared tree's three files are untouched. **The exporter must not
land without all three in the same commit.**

Also run once: `tests/test_decisions_canonical.py` (it cites the exporter in a comment) `136 passed in 7.94s` (gate copy,
masked); S1-RATE's untracked `tests/test_s1_rate.py` (its scorer imports `scrub`) `15 passed in 1.31s` (shared tree, read-only).

(The LANDED runs read slightly larger corpora than FINAL's: main 744,747,851 bytes, 141,780 lines; subagents 510,683,893
bytes, 122,987 lines, as live transcripts grew. Same counts in every cell.)

## 8. Adjacent findings (not fixed; outside the boundary) (01:2xZ)

- A1. **The three consumer couplings of section 7** (session_export's positional `PATTERN_NAMES`, test_session_export's
  oracle copy and gate total, test_jev_locate_echo's fixture built on F12). Two registry classes the coordinator may want
  rows for: a positional name list aligned to another file's rule list (a count change silently renames every rule and
  drops name-keyed exemptions), and a test fixture that encodes a known leak as its construction (the fix reds the test).
- A2. Three consumer test files copy the whole environment, token values included, into their child processes (267, 44 and
  5 lookups of each variable in set A under the logger, plus urllib's proxy scan once):
  `tests/test_push_clean_lock.py:51` (`os.environ.items()`),
  `tests/test_jev_locate_echo.py:101` (`dict(os.environ)`),
  `tests/test_ship_to_pc.py:153` (`os.environ.items()`). They are not gate reads; whether a child uses a
  token was not measured. The same set-A strace run shows 0 opens of the three source files (the other 28 syscalls that
  name a `.pc-bridge.env` are the ship_to_pc fixture repos' own files under the tests' basetemp, their cleanup unlinks
  included, checked with `strace -y`).
- A3. `tests/test_decisions_canonical.py:627`'s comment (`transcript scrubber's floor`) cites the exporter's line 33 for the
  floor: already stale before this lane (that line was the `_NAME` comment), and the lines moved again.
- A4. Known edges of the new named rules, 0 instances in the corpora: `pwd = os.getcwd()` and `credentials = get_credentials()`
  (a code variable assigned a call) are taken; `oldpwd = ...` is not (the left anchor); `Authorization: Basic authentication`
  (prose after a scheme word) would be taken.
- A5. Inferred, not measured: a key right after an ANSI colour code (`\x1b[0m` + key) is glued to the letter `m` and not
  taken (the letter decision, F4's class).
- A6. The OpenJev manifest's recorded `commit` (eb256f4) is not on origin: a local id its 09-24 build froze; the v1 test
  builds at 0b342c7 instead (the same dataset bytes).

## 9. Self-attack: the three likeliest ways this is wrong

1. **A new rule redacts ordinary text these corpora do not hold.** The measurement is one session (1.26 GB of JSONL and the
   18 digests); another genre (CJK prose with long identifiers, Python that assigns `pwd`, API docs about Basic auth) could
   pay a cost not seen here. Checked: every NEW region of every rule classified (committed fixture, documented fake, probe
   string or key-shaped value; 0 prose); the wide forms that did cost (pwd, credentials, any-scheme AUTH, PEM to \Z) were
   rejected by count; 23 ordinary texts are pinned in `test_the_shape_gaps_leave_ordinary_text` and each narrowing has a
   mutant that reds it. Residual: A4's edges.
2. **Something the PIN hid is now shown.** Checked by provenance, not by output diff: 0 LOST regions in every decoded view
   and the digests; the only LOST class is 8 JSON escape letters in the raw view, which must stay for the JSON to parse;
   the built "tail after a key" class has 0 instances; the union boundary keeps every `\b` match by construction (the
   dash-after-é test; mutant O2 killed). The digests of this session differ from the PIN's in one line, and it hides more.
3. **Production loses its gate, or a test still reaches a real source.** Checked: `main()` passes the tuple it finds when it
   runs (S1, S2 killed), no CLI option or environment switch exists (S3, S4 killed, pinned by a test), no default binds
   (S5 killed), the touch proof reads 0 opens and 0 lookups in both venues against 30 and 30 on the PIN, and an autouse
   tripwire refuses any `main()` call a future test makes without fixture sources. Residual: the new exporter has not run
   against the REAL sources (this lane may not read them). Item 5 also changes production behaviour: a real source that is
   not a regular file (a FIFO, a device, a directory) now refuses the whole export where it used to hang or be skipped, and
   push_clean's sync hides a refusal (#291, F5). The coordinator should run the exporter by hand once at landing and read
   its stderr.

## 10. Evidence tiers, files

- Verified here: the premise; the writers table (from the code; Hermes' side inferred); the measurement and its self-test;
  the Laya pre-fit comparison (v2, v1 at two commits); the v2 rebuild and the recorded manifest's one-line change; the v1
  rebuilds; the red run; 52 of 52 mutants killed; the touch proof (two venues and the PIN control; set A too); set A red
  without the patches and green with them, twice each; the two Laya record tests twice; pyflakes, the screens, report_lint.
- Inferred: what Hermes stores in a tool result (JSON with `ensure_ascii=True`); the edges in A4 and A5.
- Assumed: that the real value-gate sources are regular files (never checked: this lane does not touch them).

Files (sha256 prefix, lines; changed ranges from `git diff -U0`):
- `scripts/transcript_export.py` 6ad316dccfca0147, 383 lines: docstring 20-22; `_NAME` 36; `_WORD` 40-41; `_KEY_L`/`_KEY_R` 65-69;
  lenient PEM rule 78-83; cookie, authorization, pwd, credentials rules 93-106; provider anchors and comment 111-119; opaque
  rule 122-125; gate comment 269-271; `known_values` 286, 290-294, 312; `export` 335; `main` 358, 363, 372.
- `scripts/known_values_check.py` cfdf2ffec10e6d10, 188 lines: docstring 19-21; imports 25, 28; `ENV_NAME`, `NotRegularFile`,
  `_read_regular`, `_env_values` 35-79; the CLI's token and raw reads 141, 147.
- `tests/test_transcript_export.py` 5b22cc0040767dc7, 1289 lines: imports 4-8, 15; `_fixture_sources`/`_run` 58-78;
  `_export_one` 113; `PRODUCTION_SOURCES`, `TRIPWIRE`, the autouse fixture 391-401; 870; the exit-4 test 882-898; the SCRUB2
  tests 900-1289.
- `tests/test_known_values_check.py` f5ad1fc62a39c969, 152 lines: import 7; `run()` 21-25; two tests 124-152.
- `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json` a2e6143c0543f640: line 10 only.
- `tasks/briefs/system1/SCRUB2-report.md`: this report.
Scratch kept for the coordinator (4.2 MB, `<scratch>/scrub2/`): `digests-new/` (the known-value check's input),
`patches/` (the three consumer patches and the files they apply to), `v2new/manifest.json` (the manifest copied over the
record), `v1-eb256f4/manifest.json` (the OpenJev refresh, not applied), the instruments and every log quoted here.

## 11. NOT done

- N1. **The three consumer patches are NOT applied** (outside the boundary): the exporter must not land without them in the
  same commit (set A: 8 failed without, 746 passed with).
- N2. The OpenJev (v1) manifest not regenerated (section 7).
- N3. No real source read: the known-value check of `digests-new/` and the gate's run on the real sources are the
  coordinator's.
- N4. No git write, no push, no PC bridge, no registry or ledger edit (A1's rows and the bug-echo registration are the
  coordinator's; this lane ran a read-only grep sweep of F1's class: 3 defaults found, none naming a secret source).
- N5. Of the Laya pair only the two record tests ran (twice); the other 42 tests of `tests/test_laya_ft.py` and
  `tests/test_laya_systemone_server.py` did not (the pre-fit comparison answers the lock question).
- N6. The full suite not run: set A, the Laya record tests, `test_decisions_canonical.py` and `test_s1_rate.py` only.
- N7. hermes-session-export and qwen_matrix not run against real Hermes JSON (PC).

## 12. DISCREPANCIES

- D1. The PIN: the dispatch named local 4b3b699's pre-push id; the 23:2xZ push rewrote it (identical trees for this lane's
  files) and 6f7a925 edited the brief to the origin id mid-lane. This report cites origin ids only.
- D2. Item 8 says "each manifest": only the recorded one is regenerated (section 7 gives the reasons and the data proof).
- D3. The boundary: three files outside it must change with the exporter (A1). The brief did not list them.
- D4. Item 3 as landed differs from the brief's wording: `pwd` and `credentials` are their own rules, not credential-rule
  names (as names they cost path and annotation redactions, and `pwd` 16 Laya items); `Authorization: Token` became a
  known-scheme list (Token, Basic, a bearer in any case, Digest, Negotiate, NTLM, ApiKey, Key, SSWS); the lenient PEM rule
  requires its END line; the Cookie rule hides the header's whole remainder, cookie names included.
- D5. Item 1's "a quote" case: a key before a quote was already taken except for a trailing `-` that `\b` left; now whole.
- D6. Item 2: `\uXXXX` (and `\b`, `\f`) added; alone it found 0 instances in this session (the harness writes JSONL with
  non-ASCII literal); the reason is the raw-JSON writers' view (section 2).
- D7. The lenient PEM header takes `[ \t]*`, not the measured `\s*` (re-measured as LANDED: identical counts).
- D8. `tests/test_known_values_check.py`'s `run()` now leaves the two token variables out of its children's environment
  (they never need them), so the touch proof reads 0 lookups.
- D9. The S1-RATE lane stopped mid-way (the 00:15 commit, a content safeguard); its files stay modified in the tree; its test
  passes with this scrubber (15 passed).
- D10. Landing changes one committed digest line on the next sync: `transcripts/sandbox/chat-2026-09-17.md` hides the documented
  `Authorization: Token` example's value.
- D11. The mutation pass (section 5) ran before D8's change to `run()` (a child-environment filter only; no test logic moved);
  every other run quoted here is on the final bytes.

## 13. Final gate lines (the final bytes; 01:2xZ on 2026-09-26)

```
$ masked.sh absent <copy> -- bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_known_values_check.py --basetemp=...
pytest-summary: 207 passed in 2.27s
pytest-summary: 207 passed in 2.05s
2 files set=f3473b81d07d
$ set A (section 7), with the three proposed patches:  pytest-summary: 746 passed, 1 skipped (twice)  15 files set=271f9e77620b
$ set A, this lane's files alone:                     pytest-summary: 8 failed, 738 passed, 1 skipped (twice)
$ tests/test_laya_ft.py -k "version_2_record or version_1_is_byte": 2 passed, 42 deselected (twice)
$ pyflakes on the four files: rc 0;  report_lint: 15 refs, OK 15, MISS 0;  U+2028/U+2029 in every file written: 0
```
