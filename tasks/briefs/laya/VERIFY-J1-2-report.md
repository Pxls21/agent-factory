# VERIFY-J1-2 report: the targeted adversarial verify of the J1 decision ledger

LANE: VERIFY-J1-2 (sandbox, adversarial-verifier). PIN: `9d11c25`. BRIEF: `tasks/briefs/laya/VERIFY-J1-2-brief.md` (origin a4dafd1).
Aliases: L = `src/agent_factory/decisions/ledger.py`, V = `src/agent_factory/decisions/volatile.py`,
C = `src/agent_factory/decisions/canonical.py`, T = `tests/test_decisions_ledger.py`.
Scratch root: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vj12/` (a `git archive 9d11c25` copy; removed at the end).

## OUTCOME

**GATE RECOMMENDATION: NOT-READY.** One finding meets the whole blocking predicate. **F7**: `append` returns the row_id after a
short write. Reproduced on a real 4 KiB tmpfs through the production `append`: `os.write` put 96 of 741 bytes, `append`
returned `6ae071dc…` as success, and the ledger was left torn, so every later `append` is refused. L:256 (`os.write`) discards the byte count.
The fix sits inside L; a checked-write copy refuses by name instead. This rests on reading item 4 (g) ("ONE `canonical(row) +
"\n"` written") as requiring that a success return means the whole line landed. If the coordinator rules a full disk an edge case
under D-034, the recommendation becomes MERGE-READY-WITH-FOLLOWUPS. Everything else in the frozen contract held under attack. Row
identity follows J1-A1 and is byte-stable across four hash seeds. All nine hand-written non-canonical line shapes are refused
`decision-ledger-unparseable` at the right 1-based line. All six named reasons are reachable, with the exact detail formats (80-cut,
carried row_id, the path as given). A duplicate leaves the bytes unchanged. A corrupt ledger is never appended to. There is no
configuration channel and no Laya call. The required gates reproduce: `27 passed` twice, and RED `13 failed` without `ledger.py`.
Two **CONTRACT-DEFECTs** go back for amendment: **F11** (`str(ledger_path)`: an `os.DirEntry` makes `replay` return `[]` for a
corrupt ledger and lets `append` put a duplicate into a junk file; the contract never types the path) and **F17** (J1-1's
`normalize` is not idempotent on its own output, so `append` refuses 41 of 287 long real `docs/INCIDENT-LOG.md` lines that
`make_row` built; the fix lies in `volatile.py`, outside J1-2). The mutation audit killed M8, M9 and M10. M11, M12 and M13 survived,
with five more of my extras (test gaps, F25). The follow-ups (F1-F6, F8, F9, F12-F15, F18, F22, F25, F26) are D-034 issues. If the
one focused repair opens for F7, F12 (make_row validates its own output) and F4 (replay's bare exceptions) are small
changes in the same file. Reproduced vs read: every finding marked "reproduced" ran in this session at the PIN bytes. F20
(durability after a crash) is UNVERIFIED.

## IDENTITY

Measured 2026-09-23 in the sandbox. `git diff --stat 9d11c25 HEAD -- src/agent_factory/decisions tests/test_decisions_ledger.py
tests/test_decisions_canonical.py` printed nothing, and `git status --short` on the same paths printed nothing: the tree's
decisions boundary is byte-identical to the PIN. sha256[:16] and line counts, PIN blob vs working tree:

```
803197133f2e2f6e 333 src/agent_factory/decisions/ledger.py      tree: 803197133f2e2f6e 333
bc9cb1d03fdb77a4 77 src/agent_factory/decisions/canonical.py    tree: bc9cb1d03fdb77a4 77
b48899c883c7231f 295 src/agent_factory/decisions/volatile.py    tree: b48899c883c7231f 295
2aec3875f71213e4 21 src/agent_factory/decisions/__init__.py     tree: 2aec3875f71213e4 21
787f08043ca086a1 634 tests/test_decisions_ledger.py              tree: 787f08043ca086a1 634
48fdf09e8038a146 340 tests/test_decisions_canonical.py           tree: 48fdf09e8038a146 340
```

All six match the brief's PREMISE table. SOLID.

Scratch-copy note: the venv holds an editable install of the repo (`__editable__.agent_factory-0.1.0.pth` → `/home/user/agent-factory`).
Every scratch run sets `PYTHONPATH=<scratch>/src`; a probe printed the imported module path as the scratch copy
(`.../vj12/base/src/agent_factory/decisions/ledger.py`), so the scratch module, not the tree's, is the one exercised.

## ITEMS

Probe harness: `vj12/probe/common.py` imports `agent_factory.decisions.ledger` from the scratch copy (asserted on
`L.__file__`), builds rows through `make_row` from the goldens, and wraps each call so a `DecisionStateError` prints as
`DSE <str(e)>` and any other exception as `BARE <type>: <msg>`. Outputs below are pasted from the runs; long values are cut
with an ellipsis, scratch paths are shortened to `…/`, a raw newline or CR is shown as <newline> or <CR>, and a few rows merge
several printed lines (joined with ' / ').

### Item 1 — identity (J1-A1)

Reproduced (`vj12/probe/item1.py`, via `make_row` + `append` + `replay`):
```
1a row_id equal: True | row_digest equal: False
1a append r1: OK 'c651c0c3d63ef3c64b072bd5a4a213ec38b095d22398d3c13033ee294d952aea'
1a append r2: DSE decision-row-duplicate: c651c0c3d63ef3c64b072bd5a4a213ec38b095d22398d3c13033ee294d952aea
1a file unchanged: True
1a ledger answer now: ['HIGH']
1a true dup   : DSE decision-row-duplicate: c651c0c3d63ef3c64b072bd5a4a213ec38b095d22398d3c13033ee294d952aea
1b row_id equal: True
1b append a: OK 'e6aff537c5cdfa004521d3078c80386516043bb6fe1f2ea09399c17a52dd6667'
1b append b: DSE decision-row-duplicate: e6aff537c5cdfa004521d3078c80386516043bb6fe1f2ea09399c17a52dd6667
1b' state equal: True row_id equal: True
1d path 'docs/INCIDENT-LOG.md'     row_id=c651c0c3d63ef3c6
1d path './docs/INCIDENT-LOG.md'   row_id=b355738fed17948f
1d path 'docs//INCIDENT-LOG.md'    row_id=8ac95474bed86679
1d path 'docs/./INCIDENT-LOG.md'   row_id=c56b9f3f043a0ec1
```

- **F1 — FOLLOW-UP. A revised incumbent answer is refused with the same text as a true duplicate; the ledger keeps the stale
  answer.** Evidence: reproduced (1a). `_compute_row_id` (L:70) hashes `producer`, `question_id`, `state_digest` and
  `source_ref` {kind, path, locator} only, so the same entry re-harvested after an in-place edit ("HIGH" → "LOW", new
  `source_digest`) gets the same row_id; `append` (L:247, `seen_ids`) refuses it `decision-row-duplicate: <row_id>`, byte for byte the
  text a true duplicate gets, and `replay` still returns `HIGH`. Expected per contract: exactly this. Item 2 (J1-A1) fixes the
  identity to those fields, and the breakdown pins "duplicate append is a NAMED refusal … the harvest counts it as a printed
  skip". So the behaviour matches the frozen contract. But the refusal cannot tell "the same decision again" from "the same
  decision point, answer changed", and J1-3 will fold a revised answer into its skip count. Predicate: contract-mapped NO
  (the code follows item 2). Touchpoint J1-3 / contract: compare the stored row's `incumbent_answer` on a duplicate, or amend
  the contract with a separate reason (e.g. `decision-row-conflict: <row_id>`). The same holds forward: `checkpoint_digest`
  and `calibration_state` are outside the identity, so a J2/J3 calibrated row for an incumbent's decision point will collide
  (INFO; both are literals in J1).
- **F2 — FOLLOW-UP (touchpoint J1-3, J1-1). Two different decisions that share producer, question, state and locator
  collide; the second is refused and lost.** Evidence: reproduced (1b, 1b'). Two findings under one heading with the same
  `b1.finding_sev` state and the same locator but answers HIGH/LOW: one row_id, the second refused as a duplicate. Because
  J1-1 bounds `msg` to 200 characters (`MSG_LIMIT`, V:27), two messages that differ only after character 200 normalize to the
  same state (1b': state equal True, row_id equal True). Contract: the locator is "a finding id + heading", so J1-3 must
  emit a locator unique per decision; the ledger cannot tell them apart. Predicate: not contract-mapped for J1-2; ownership is
  J1-3's grammar. Fix: J1-3 locators carry the finding id (or an ordinal) for every decision.
- F3 (path spelling and identity) is filed under item 5.

### Item 2 — the canonical line

Reproduced (`vj12/probe/item2.py`). Line 1 is a valid `b2.hit_role` row; the hostile variant of a valid
`b1.finding_sev` row (answer `café accepted`, NFC) is line 2, except the BOM case (line 1). Paths shortened here to
`…/work/`; the run printed the full scratch path.
```
control canonical 2 lines         OK [{'calibration_state': 'incumbent', ...
keys-out-of-order                  DSE decision-ledger-unparseable: …/work/k1.jsonl:2
extra-whitespace                   DSE decision-ledger-unparseable: …/work/k2.jsonl:2
leading-space                      DSE decision-ledger-unparseable: …/work/k2b.jsonl:2
\u00e9-escape-vs-literal      DSE decision-ledger-unparseable: …/work/k3.jsonl:2
NFD-vs-NFC                         DSE decision-ledger-unparseable: …/work/k4.jsonl:2
float 1.0 (incumbent_answer)       DSE decision-ledger-unparseable: …/work/k5.jsonl:2
int 1 (canonical, wrong type)      DSE decision-row-incomplete: missing incumbent_answer
-0 (incumbent_answer)              DSE decision-ledger-unparseable: …/work/k6.jsonl:2
duplicate key in one object        DSE decision-ledger-unparseable: …/work/k7.jsonl:2
trailing \r\n                      DSE decision-ledger-unparseable: …/work/k8.jsonl:2
UTF-8 BOM on line 1                DSE decision-ledger-unparseable: …/work/k9.jsonl:1
--- beyond the brief's list ---
NaN (incumbent_answer)             DSE decision-ledger-unparseable: …/work/x1.jsonl:2
5000-digit int                     DSE decision-ledger-unparseable: …/work/x2.jsonl:2
scalar line: 1                     BARE TypeError: argument of type 'int' is not iterable
scalar line: "calibration_state"   BARE TypeError: string indices must be integers, not 'str'
scalar line: []                    DSE decision-row-incomplete: missing calibration_state
lone surrogate escape \ud800       BARE UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 80: surrogates not allowed
raw bytes ED A0 80 (CESU surrogate) BARE UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 83: surrogates not allowed
deep nesting 100000                BARE RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string
deep nesting 600                   BARE RecursionError: maximum recursion depth exceeded
final row without trailing \n      DSE decision-ledger-unparseable: …/work/x9.jsonl:2
empty line mid-file                DSE decision-ledger-unparseable: …/work/x10.jsonl:2
utf-16 line                        DSE decision-ledger-unparseable: …/work/x11.jsonl:2
extra top-level key (forged)       OK [{'calibration_state': 'incumbent', ...
extra source_ref key (forged)      OK [{'calibration_state': 'incumbent', ...
```

Every shape the brief names is refused `decision-ledger-unparseable: <path>:<lineno>` with the right 1-based line. None of
them is accepted. The byte comparison at L:316 (`raw_line != expected_bytes`) does the work for all of them. SOLID.


- **F4 — FOLLOW-UP. Six corrupt-line shapes escape `replay` as bare exceptions, not `decision-ledger-unparseable`.**
  Evidence: reproduced (table above; the same exceptions come out of `append`, which replays first:
  `append onto ledger with line '1' → BARE TypeError: argument of type 'int' is not iterable`, and the lone-surrogate
  ledger → `BARE UnicodeEncodeError`). Mechanisms, read at the PIN: a canonical scalar line (`1`) passes the line check and
  reaches `_validate_row`, whose `if field not in row` (L:94) raises `TypeError` on an int; a JSON string containing
  `calibration_state` passes L:94 (`field not in row`) as a substring test and fails at `val = row[field]` (L:119); a `\ud800` escape (or raw bytes
  ED A0 80, which `json.loads` decodes with `surrogatepass`) parses, then `canonical(parsed).encode("utf-8")` (L:311) raises
  `UnicodeEncodeError`, which the `except DecisionStateError` at L:312 does not catch; 100000 nested brackets raise
  `RecursionError` inside `json.loads` (the `except` at L:304 catches only `JSONDecodeError`/`ValueError`), and 600 nested brackets pass
  `json.loads` but overflow `canonical()`. Expected (item 5 + item 6): `decision-ledger-unparseable: <path>:<lineno>` as a
  `DecisionStateError`. Fail-closed holds in every case: no rows are returned and nothing is appended. What changes is the
  exception class and the lost `<path>:<lineno>`, so a J1-3 caller that catches `DecisionStateError` would crash instead of
  naming the line. `append` itself can never write any of these lines. Predicate: contract-mapped (items 5, 6), reproduced,
  discriminator yes, in boundary; material effect NO under D-034 (no state or evidence changes, the ledger is refused either
  way; hand-corrupted input). Fix: in `replay`, treat any exception from the parse and canonical steps (`ValueError`,
  `RecursionError`, `UnicodeError`, `TypeError`) as unparseable, and refuse a parsed value that is not a dict before
  `_validate_row`.
- **F5 — FOLLOW-UP. The row shape is open: extra top-level and `source_ref` keys are accepted; colliding extra keys let
  `append` write a line that `replay` refuses.** Evidence: reproduced. A row with an extra key (`zz_extra`) or an extra
  `source_ref` key, all digests recomputed, replays OK (table above). `_validate_row` checks the presence of the ten fields
  (L:93, `_ROW_FIELDS`) and never refuses an unknown one; `_compute_row_id` (L:70) ignores extra `source_ref` keys, and `row_digest` covers
  them. Worse: extra keys that canonicalize to the same text (int `1` + str `"1"`, or NFC + NFD `é`) are written by `append`
  with a success return; the written line holds a duplicate key, so the next `replay` refuses the whole ledger:
  ```
  int 1 + str '1'        append -> OK 'c651c0c3d63ef3c64b072bd5a4a213ec38b095d22398d3c13033ee294d952aea'
                         replay -> …/work/ck.jsonl:1        (decision-ledger-unparseable)
                         next append -> DSE decision-ledger-unparseable: …
  NFC + NFD 'e-acute'    append -> OK 'c651c0c3…'   replay -> …/work/ck.jsonl:1   next append -> DSE decision-ledger-unparseable: …
  ```
  Contract: item 1 lists the fields but names no refusal for an extra one; item 3 says "No caller assembles a digest by hand",
  and `make_row` cannot produce extra keys. So this needs a hand-assembled row. Predicate: not contract-mapped (no
  unknown-field rule), misuse outside item 3. Fix: refuse any key outside `_ROW_FIELDS` / `_SOURCE_REF_FIELDS` in step (a)
  (a closed row, as the seed's closed-schema principle asks), or re-parse the line in `append` before the write.
- **F6 — INFO. A present field of the wrong type is reported as `missing`.** Evidence: reproduced. `incumbent_answer: 1` in a
  canonical line → `decision-row-incomplete: missing incumbent_answer`; `producer=7` → `missing producer`; `source_ref` as `""`,
  `[]` or `{}` → `missing source_ref.kind` (not `missing source_ref`). The contract's (a) names only "present and non-empty";
  the wording misleads a reader but no row gets through. Fix (optional): report a wrong type under `decision-row-invalid`.

### Item 3 — the append path's failure modes

(a) **Short write** — reproduced on a real 4 KiB tmpfs mounted under the scratch root (`mount -t tmpfs -o size=4k,mode=0700`;
unmounted after, `/proc/mounts` count 0). Row 1 was padded through its free-text answer so the ledger is 4000 bytes; row 2's
line is 741 bytes. Run with a transparent `os.write` spy (it records the return value and changes nothing), then again with
no spy, then against a scratch copy whose L:256 (`os.write`) checks the count (`vj12/fixw/`, the candidate fix, never the tree):
```
=== CASE A: ledger 4000 bytes in a 4096-byte tmpfs (row 2 only partly fits)
append r1: OK 'c651c0c3d63ef3c64b072bd5a4a213ec38b095d22398d3c13033ee294d952aea' | ledger bytes: 4000
tmpfs blocks total/free: 1 0 | bsize 4096
row 2 line length: 741
append r2 returned: OK '6ae071dcda86e640eb274f6a75212d24cadb644c2508e4933fdf833c2ae5e48c'
os.write(len, returned): [(741, 96)]
ledger bytes now: 4096 | ends with newline: False
next replay: DSE decision-ledger-unparseable: …/vj12/tmpfs/ledger.jsonl:2
next append (wf.drift): DSE decision-ledger-unparseable: …/vj12/tmpfs/ledger.jsonl:2
=== CASE B: ledger exactly 4096 bytes (no byte of row 2 fits)
append r2 returned: BARE OSError: [Errno 28] No space left on device
ledger bytes now: 4096 | ends with newline: True
=== PIN code (no spy)
append r2 (no spy): OK '6ae071dcda86e640eb274f6a75212d24cadb644c2508e4933fdf833c2ae5e48c'
ledger bytes: 4096 | ends with newline: False
=== candidate fix (checked os.write)
append r2 (no spy): DSE decision-ledger-short-write: …/vj12/tmpfs/ledger.jsonl:96/741
```
- **F7 — BLOCKER. `append` returns the row_id after a short write; the row is not in the ledger and the file is left torn.**
  Evidence: reproduced through the production `append` on a real tmpfs at the PIN, with and without the observation spy.
  L:256 `os.write(fd, line.encode("utf-8"))` discards the byte count; the kernel wrote 96 of 741 bytes and `append` returned
  `6ae071dc…` as success. The next `replay` refuses the ledger (`:2`, the torn last line), and every later `append` is refused
  too. The contract forbids rewriting existing bytes, so nothing in J1 can repair the file. Expected: item 4 returns the row_id
  only after (g) wrote ONE `canonical(row) + "\n"`; the declared limits (unkeyed digest, row deletion, one writer) do not cover
  a partial write. A full disk is not hypothetical here: this sandbox has about 2 GB free, and AF-AP-125 filled its disk on
  2026-09-23. CASE B (nothing fits) raises `OSError` ENOSPC loudly and leaves the ledger intact, so only the partial case lies.
  Predicate: (1) contract-mapped — item 4 (g) and the return value; (2) canonical — real tmpfs, the real `append`, no spy;
  (3) material — a false success: J1-3's `harvest: <n> rows` would count a row that is not there, and the ledger stops
  accepting appends; (4) discriminator — the tmpfs command above: the PIN copy prints `OK <row_id>`, the checked-write copy
  prints `decision-ledger-short-write`; (5) in boundary — L:256 (`os.write`). All five hold. Fix: `n = os.write(fd, data)`; if
  `n != len(data)`, raise a named `DecisionStateError` (optionally `os.ftruncate` back to the pre-write size, which removes only
  this call's bytes, never existing ones); add a test that forces a short write (a tiny tmpfs, or `os.write` patched to
  return fewer bytes).
- **F8 — FOLLOW-UP. A FIFO at the ledger path hangs `replay` and `append` forever.** Evidence: reproduced
  (`timeout 10 … replay(fifo)` → rc 124; `append(fifo)` → rc 124: `open(path_str, "rb")` at L:274 blocks until a writer
  appears). The contract names no file-type rule. Predicate: not contract-mapped; needs a FIFO planted at the path. Fix:
  open with `O_RDONLY|O_NONBLOCK`, `fstat`, refuse anything but a regular file by name.
- **F9 — FOLLOW-UP. Symlinks are followed by both `replay` and `append`; a dangling symlink makes `append` create the link's
  target.** Evidence: reproduced: `replay(link) rows: 1`, `append(link)` OK, `target rows now: 2`; dangling link: `replay → OK []`,
  `append → OK … | target created: True`. L:252 (`os.open`) opens without `O_NOFOLLOW`. The contract is silent. Fix (optional hardening):
  `O_NOFOLLOW` on both opens, or a documented limit.
- **F10 — INFO. A directory at the path raises a bare `IsADirectoryError` from both functions.** Reproduced. An OS error, loud,
  not one of the contract's named refusals.
- **F11 — CONTRACT-DEFECT (returned for an amendment). `str(ledger_path)` (L:253, L:272) turns ANY object into a path:
  an `os.DirEntry` (an `os.PathLike`, the type the builder annotated) makes `replay` return `[]` for a non-empty corrupt ledger
  and makes `append` accept a DUPLICATE into a junk file; `None` writes `./None`.** Evidence: reproduced:
  ```
  os.DirEntry isinstance PathLike: True | str(entry) = <DirEntry 'rel.jsonl'>
  os.DirEntry -> replay                        OK []            (the file holds a good row and a garbage line)
  bytes b'sub/rel.jsonl' -> replay             OK []
  replay(None)                                 OK []
  real ledger rows: 2
  append(DirEntry) of a DUPLICATE of row 1: OK 'c651c0c3d63ef3c64b072bd5a4a213ec38b095d22398d3c13033ee294d952aea'
  files in cwd now: ["<DirEntry 'real.jsonl'>", …, 'real.jsonl', …]
  append(None): OK '5fdbe7c7…' | ./None exists: True
  ```
  This falsifies evidence (a corrupt ledger verifies as empty) and puts state in the wrong place (a duplicate lands in a junk
  file). It goes through the public functions with a type the signature invites. The frozen contract never types
  `ledger_path`, so item 1 of the predicate cannot map; hence CONTRACT-DEFECT, not BLOCKER. Proposed amendment: "`ledger_path` is
  `str | os.PathLike`, resolved once with `os.fspath`; any other type is refused". Fix: `os.fspath(ledger_path)` in both
  functions (a one-line change each; `None` then raises `TypeError` instead of writing `./None`).

### Item 4 — named refusals through the public functions

Reproduced (`vj12/probe/item4.py`, `item4b.py`):
```
absent producer / state / state_digest / row_id / row_digest / source_ref → DSE decision-row-incomplete: missing <field>  (each exact)
state={}                                     DSE decision-row-digest-mismatch: c651c0c3…   (a dict, so (a) passes; (c) fires)
calibration_state len 79 -> detail value len 79
calibration_state len 80 -> detail value len 80
calibration_state len 81 -> detail value len 80
newline value -> 'DSE decision-row-invalid: calibration_state=incumbent\nsecond line'
kind 81 -> KKKKKKKKKKKK | len 80
source_digest uppercase                      DSE decision-row-invalid: source_ref.source_digest=AAAA…
row_id flipped to 0*64 -> DSE decision-row-digest-mismatch: 000000 ... carried? True
answer tampered -> carried? True / state tampered -> carried? True
unnormalized -> DSE decision-row-state-not-canonical carried? True
unknown question_id (forged)                 DSE decision-row-state-not-canonical: 75c4cbdf…
dup                                          DSE decision-row-duplicate: c651c0c3…
relative str 'sub/rel.jsonl'                 DSE decision-ledger-unparseable: sub/rel.jsonl:2
pathlib.Path('sub/rel.jsonl')                DSE decision-ledger-unparseable: sub/rel.jsonl:2
'./sub/../sub/rel.jsonl'                     DSE decision-ledger-unparseable: ./sub/../sub/rel.jsonl:2
```
All six contract reasons are reachable through `append`/`replay`, and the detail formats hold: `missing source_ref.<sub>`,
`<field>=<value>` cut at 80 (79 → 79, 80 → 80, 81 → 80, `[:80]` at L:127), the CARRIED row_id on every digest mismatch
(L:164, L:169, L:174 raise with `row["row_id"]`), and `<path>:<lineno>` 1-based with the path as given (str, `pathlib.Path`, an
unnormalized relative path). SOLID.

`make_row` with bad input (item 3: "refuses bad input by name (items 4-6)"):
```
source_ref missing kind                  BARE KeyError: 'kind'
source_ref missing path                  BARE KeyError: 'path'
source_ref missing locator               BARE KeyError: 'locator'
source_ref missing source_digest         OK {...}          -> append: DSE decision-row-incomplete: missing source_ref.source_digest
source_ref None                          BARE TypeError: 'NoneType' object is not iterable
producer ''                              OK {...}          -> append: DSE decision-row-incomplete: missing producer
producer None                            DSE decision-canonical-float: $.producer
incumbent_answer ''                      OK {...}
incumbent_answer None                    DSE decision-canonical-float: $.incumbent_answer
incumbent_answer 5                       OK {...}
incumbent_answer with \n                 DSE decision-canonical-newline: HIGH<newline>sk-qqqqqqqqqqqqqqqqqqqq
kind 'bogus'                             OK {...}          -> append: DSE decision-row-invalid: source_ref.kind=bogus
path '/etc/passwd'                       OK {...}          -> append: DSE decision-row-invalid: source_ref.path=/etc/passwd
locator with \n                          DSE decision-canonical-newline: F1<newline>F2
locator lone surrogate                   BARE UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 123: surrogates not allowed
answer lone surrogate                    BARE UnicodeEncodeError: 'utf-8' codec can't encode character '\ud83d' in position 85: surrogates not allowed
raw_state not a dict                     DSE decision-state-not-mapping: b1.finding_sev
root omitted                             BARE TypeError: make_row() missing 1 required keyword-only argument: 'root'
append(path, 1) / append(path, None)     BARE TypeError: argument of type 'int' / 'NoneType' is not iterable
```
- **F12 — FOLLOW-UP (a contract item 3 deviation; fold into F7's repair if one opens). `make_row` does not refuse bad input by
  name.** Evidence: reproduced (above). `make_row` (L:191) never runs `_validate_row`: three missing `source_ref` sub-fields
  raise a bare `KeyError` from `_compute_row_id` (L:76-78, `row["source_ref"]["kind"]`), `source_ref=None` a bare `TypeError` at `dict(source_ref)` (L:221),
  lone surrogates a bare `UnicodeEncodeError` from `_sha256_hex` (L:60-61), and six bad inputs come back as a row that only
  `append` refuses. The contract says `make_row` "refuses bad input by name (items 4-6)". Nothing invalid can land: `append`
  re-validates every row, so the ledger stays fail-closed by name. Predicate: contract-mapped (item 3), reproduced, discriminator
  yes, in boundary; material effect NO under D-034 (no invalid row lands, no state or evidence changes; only where and how the
  refusal surfaces). Fix: check the four `source_ref` sub-fields before `_compute_row_id`, and call `_validate_row(row)`
  before `return row` (L:227). This also moves F17's refusal to `make_row`.
- **F13 — INFO. Refusal details can carry a raw newline and unredacted text.** Evidence: reproduced: `decision-row-invalid:
  calibration_state=incumbent\nsecond line` is a two-line message; J1-1's `decision-canonical-newline` detail is the first 32
  characters of the offending string, so an invented `sk-qqq…` secret in `incumbent_answer` appeared verbatim in the error. The
  contract only fixes the 80-character cut. Fix (optional): `repr()`-escape the value and redact it before the cut. Touchpoint
  J1-1 (the canonical detail).
- **F14 — INFO. Misleading reason names.** `make_row(producer=None)` → `decision-canonical-float: $.producer` (J1-1 names a None
  "float", touchpoint C-F6); a forged row with an unknown `question_id` → `decision-row-state-not-canonical` (step (b) has no
  question check, and (d) maps every J1-1 refusal from `normalize` to state-not-canonical, L:179-184). Both match the contract's
  letter.

### Item 5 — path and kind validity

Reproduced (`vj12/probe/item5.py`, each path through `make_row` → `append` → `replay`):
```
'./a' 'a/./b' 'a//b' 'a/..b' '%2e%2e/a' 'a/' 'a\x00b' '~/x' ' docs/x ' '.' 'C:/x'   append -> OK, replay -> OK   (11 accepted)
''        DSE decision-row-incomplete: missing source_ref.path
'..'      DSE decision-row-invalid: source_ref.path=..
'a/../b'  DSE decision-row-invalid: source_ref.path=a/../b
'a\\b'    DSE decision-row-invalid: source_ref.path=a\b
'/a'      DSE decision-row-invalid: source_ref.path=/a
'a\nb'    make_row -> DecisionStateError: decision-canonical-newline: a<newline>b
\r         make_row -> DSE decision-canonical-newline: F1<CR>F2
U+2028     append -> OK   raw bytes in line: b'F1\xe2\x80\xa8F2'    str.splitlines() lines: 2 | replay rows: 1
U+2029     append -> OK   raw bytes in line: b'F1\xe2\x80\xa9F2'    str.splitlines() lines: 2 | replay rows: 1
NEL U+0085 append -> OK   raw bytes in line: b'F1\xc2\x85F2'        str.splitlines() lines: 2 | replay rows: 1
VT \x0b    append -> OK   raw bytes in line: b'F1\x0bF2'            str.splitlines() lines: 1 | replay rows: 1
```
- **F3 — FOLLOW-UP. `source_ref.path` is checked for three shapes only, so equivalent spellings mint new row_ids and some
  non-paths pass.** Evidence: reproduced (above, and item 1's 1d rows: `./docs/INCIDENT-LOG.md`, `docs//INCIDENT-LOG.md`,
  `docs/./INCIDENT-LOG.md` each give a different row_id from `docs/INCIDENT-LOG.md`). L:139-147 (`path.startswith("/")`) refuse a leading `/`, a `\`
  and a `..` segment, exactly the contract's three rules, so the 11 accepted shapes are contract-conforming. But the path is
  inside the identity (L:78, `row["source_ref"]["path"]`), so a re-landing under another spelling appends a second row. That is the class J1-A1 fixed for
  `source_digest`. A NUL byte, a lone dot, a tilde path (J1-1's `_path` refuses a leading tilde, V:103 `s.startswith("~")`), padded spaces and `C:/x` are not
  repo-relative file paths. Predicate: not contract-mapped (item 1 lists three rules). Fix: refuse any path whose
  `posixpath.normpath` differs from itself, or that holds control characters, whitespace at the ends, or a leading `~` or
  drive letter; touchpoint J1-3 (emit normalized paths).
- **F15 — FOLLOW-UP. U+2028, U+2029 and NEL pass into the line raw; `str.splitlines()` splits such a ledger line in two.**
  Evidence: reproduced (above). `canonical()` refuses only LF and CR (C:29-30, `decision-canonical-newline`), and `json.dumps(ensure_ascii=False)` leaves
  these three unescaped. `replay` splits on `b"\n"` only, so the ledger itself is unaffected (replay rows: 1). A downstream
  reader using `str.splitlines()` sees two broken lines. `\r` is refused, by J1-1's `decision-canonical-newline` rather than by
  a `decision-row-invalid: source_ref.locator=…` refusal. The contract says "locator newline-free" without defining newline.
  Fix: refuse these in `locator` (and any row string), or escape them in the canonical form (a J1-1 touchpoint, C).

### Item 6 — configuration channel

- **F16 — INFO (clean). No configuration channel.** Evidence: read + reproduced. `make_row`'s `root` is a required keyword
  (`root omitted → TypeError: make_row() missing 1 required keyword-only argument: 'root'`), threaded to `normalize` and
  `state_digest` (L:212-213); step (d) passes `None` explicitly (L:180). L reads no `os.environ`, no `os.getcwd`, no default root.
  The literal sweep `grep -n "environ\|getcwd\|cwd\|expanduser\|getenv" src/agent_factory/decisions/*.py` printed nothing. A
  relative `ledger_path` resolves against the process cwd, which is inherent to a relative path ("the path as given").

### J1-1 touchpoint that changes J1-2's round trip (item 9: noted, not re-litigated)

Reproduced (`vj12/probe/item_rt.py`, `item_rt2.py`), `make_row` → `append` on LEGITIMATE raw states:
```
msg cut right after a space (200th char is ' '): DSE decision-row-state-not-canonical: 15c3d5f9e22fb285309d0cb0
lane cut so a --<hex> suffix is exposed        : DSE decision-row-state-not-canonical: ab9b328a46d2e6d62003f1d2
kind: a sk- key in the last 12 of 80 chars      : DSE decision-row-state-not-canonical: a1fd45d19c92f93765a5eccd
over-limit lines: 287
  DSE decision-row-state-not-canonical         41
  OK (appended)                                246
not a fixed point: 41 of 287
  stored msg ends with a space; re-normalize strips it    40
  stored msg longer than 200 (redaction grew it)          1
```
- **F17 — CONTRACT-DEFECT (returned; the fix is outside J1-2's boundary). `append` refuses about one in seven long real-text
  rows that `make_row` built from legitimate input.** Evidence: reproduced over the 287 lines of `docs/INCIDENT-LOG.md` (a
  committed harvest source) longer than 200 characters, each used as a `b1.finding_sev` msg: 41 are refused
  `decision-row-state-not-canonical`. Mechanism, re-derived from source: `_normalize_field` collapses and strips whitespace
  (V:138, `_nfc_collapse`) BEFORE the bound (V:143 `s = s[: f.limit]`), so a cut that lands just after a space stores a trailing space; step (d)
  (L:180, `restate`) re-normalizes, strips it, and the state is no longer a fixed point. 40 of the 41 are this; 1 is the known redaction
  growth past the bound (C-F1's family). A `--<hex>` suffix exposed by the cut (`strip_pin` runs before the bound, V:139-143)
  does the same. The J1-2 contract's (d) premise was measured on the 14 golden states only. The trailing-space case is not among
  C-F1 to C-F7, and C-F1's planned repair ("bound after redact") keeps the strip-then-cut order, so it will not close this.
  Consequence for J1: J1-3's real harvest loses roughly one in seven rows whose bounded text field overflows, each refused by
  name. Ownership: `volatile.py` (J1-1-R1). Amendment asked: J1-1-R1 makes `normalize` idempotent on its own output (strip and
  PIN-strip after the bound, and the bound after redaction), and J1-2 gains a round-trip test (every `make_row` output passes
  `append`'s (d)) over over-limit text with a space, a PIN suffix and a secret at the cut.

### Other observations

- **F18 — INFO. Replay on every append makes a harvest quadratic.** Reproduced (indicative timings on a shared 4-core box, load
  0.45): `append  100 rows into one ledger: 0.83s (replay-per-append validates 4950 rows in total)`; `append  400 rows into one
  ledger: 12.68s (replay-per-append validates 79800 rows in total)`. Step (e) requires the replay, so this is by contract.
  Touchpoint J1-3: a real harvest of ~700 rows costs tens of seconds, 2000 rows several minutes; a batch append that replays
  once would keep (e)'s guarantee.
- **F19 — INFO. Determinism holds across hash seeds.** Reproduced: the 7-golden ledger hashes to `3fcbba6bac4bae49` under
  `PYTHONHASHSEED` 0, 1, 12345 and random.
- **F20 — INFO. Durability of a NEW ledger.** L:257 (`os.fsync(fd)`) fsyncs the file, not its directory, so after a crash the first append's
  directory entry can be lost; `replay` then reads a missing file as `[]`. The contract asks only for `os.fsync`, and "a deleted
  row is not detected" covers the effect in spirit. Not reproduced (needs a crash). UNVERIFIED on disk.
- **F21 — INFO. A non-NFC in-memory row round-trips as NFC.** `canonical()` NFC-normalizes every string, so `replay` returns an
  NFC dict that is not equal to an appended NFD dict (the digests agree). Read at C:28 (`unicodedata.normalize`); T:104 (`test_replay_byte_identical_x2`) compares only NFC goldens.

- **F22 — FOLLOW-UP. Free-text row fields go into the ledger unredacted.** Evidence: reproduced: `make_row(incumbent_answer='HIGH
  sk-INVENTED…', locator='F9 token: AAAA…')` → `append` OK, and the invented secret and the 40-character token run are in the
  ledger bytes (`True`, `True`); the same secret in `state.msg` is stored as `x <redacted:sk>`. Step (d) (L:177-188, `restate`) checks that
  `state` is redacted; `incumbent_answer`, `producer` and `source_ref.locator` are never passed through `redact`. The contract
  defines redaction for `state` only, so this is not contract-mapped. Touchpoint J1-3: feed closed-vocabulary answers and
  secret-free locators, or run `redact` over the free-text fields and refuse a row whose free text changes under it.
- **F23 — INFO. Refusal order.** Reproduced: a ledger whose line 1 is tampered and whose line 3 is torn reports
  `decision-ledger-unparseable` (the torn-final-line check at L:284 (`parts[-1]`) runs before the per-line loop). Otherwise the first bad line
  wins, and per line the parse, canonical and row checks interleave (L:294-331, `raw_line`). Item 5 reads "every line must parse … then
  (a)-(d)". Either reading refuses the ledger; only the reported reason can differ.
- **F24 — INFO. No production consumer exists yet.** Two instruments: the literal sweep over non-test `*.py` for
  `decisions.ledger` finds only the vocabulary token in `scripts/no_laya_in_gates.py:56`; `graft ask "who calls make_row …"`
  lists only `tests/test_decisions_ledger.py` callers; `scripts/decide-harvest` does not exist. So every "integration" effect
  above (F4, F7, F12) is prospective, J1-3's.

### Item 7 — new mutants

See MUTATION TABLE. Summary: of the six required mutants, M8, M9 and M10 are killed; M11, M12 and M13 SURVIVE. Of my extras, M15, M16
and M17 are killed (only through T:387's hand-built identity, `test_state_not_canonical`), and M14, M15b, M18, M19 and M20 SURVIVE.
- **F25 — FOLLOW-UP. Eight surviving mutants mark contract lines no test pins.** Evidence: reproduced (MUTATION TABLE; each
  mutant compiled, collected 27, ran the two files, and imported the mutated copy; M0 proves the harness imports it).
  M11 (uppercase hex accepted): only `_is_hex64`'s lowercase rule refuses an uppercase `source_digest` (probe:
  `decision-row-invalid: source_ref.source_digest=AAAA…` at the PIN), and no test tries one. M12 (`os.fsync` gone): no test can
  see durability; a test that records `os.fsync` calls would kill it. It is not a declared limit, so it is a gap, not an
  equivalent. M13 (cut at 79): no test value is longer than 64 characters. M14 (replay's in-file duplicate check gone): item 5's
  "a row_id seen twice in the file" is never tested (probe at the PIN: same row twice in the file gives DSE decision-row-duplicate:
  c651c0c3…). M15b (a final row without its newline kept): T:470's (`test_unparseable_lines`) torn line is also bad JSON, so the JSON check at the same
  line number masks the newline rule (probe x9: the PIN refuses a complete final row without `\n`). M18 (the mismatch detail names
  the recomputed row_id) and M19 (every row refusal reported as unparseable): T:296 (`test_tamper_detected`) accepts `decision-ledger-unparseable` for
  file tampers and never checks the detail. The contract's test spec says "replay refuses `decision-row-digest-mismatch: <stored
  row_id>`", and the PIN does exactly that for all five flips (measured below), so the test is weaker than its spec. M20 (the
  invalid detail drops the value): T:507 (`test_invalid_fields`) checks only `<field>=`. D-034 names "test-strength on a pinned artifact" a non-core
  finding. Fix: exact-string assertions in T:296, T:507, T:124 and T:387 (`test_tamper_detected`, `test_invalid_fields`, `test_relanding_same_row_id`, `test_state_not_canonical`), plus one test each for an uppercase digest, an 81-character
  value, a duplicated line in the file, a final line without `\n`, and `os.fsync` being called.

### Item 8 — the builder's report (`tasks/briefs/laya/J1-2-report.md`)

Checked against the PIN:
```
$ python3 scripts/report_lint.py --min-refs 10 --map L=src/agent_factory/decisions/ledger.py --map T=tests/test_decisions_ledger.py tasks/briefs/laya/J1-2-report.md --root .
report_lint: 30 refs — OK 30, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
$ git log --since=2026-09-22T00:00:00Z --format=%h f949974 -- docs/INCIDENT-LOG.md | wc -l      → 39
$ git log --oneline -1 f949974 -- src/agent_factory/decisions/                               → 01ca7d5 J1-1 landed …
$ python3 -c "import agent_factory.decisions as d, …ledger; print('OK')"   (system /usr/local/bin/python3)
ModuleNotFoundError: No module named 'agent_factory'
file flips (T:296's five targets, `test_tamper_detected`) at the PIN:
incumbent_answer           DSE decision-row-digest-mismatch | detail is the stored row_id: True
state.file                 DSE decision-row-digest-mismatch | detail is the stored row_id: True
source_ref.locator         DSE decision-row-digest-mismatch | detail is the stored row_id: True
source_ref.source_digest   DSE decision-row-digest-mismatch | detail is the stored row_id: True
row_id                     DSE decision-row-digest-mismatch | detail is the stored row_id: True
```
Supported: every line cite (30 OK), the premise numbers, the RED (13 failed with `ModuleNotFoundError`; reproduced below) and
GREEN counts, the file sizes, `__init__.py` untouched (its last commit is still 01ca7d5), the T:296 (`test_tamper_detected`) behaviour claim, and the m1-m7
table (re-run below: all seven killed; m1 by a `KeyError`, as the builder wrote; m6 = M9, killed because the exact-string
assertion sees `decision-row-duplicate`). `PIN: f949974` is the commit that carries the J1-2 brief, which is how that brief defines
its PIN; the landing is 9d11c25.
- **F26 — FOLLOW-UP (report accuracy). "DISCREPANCIES: None. All contract lines met." is not supported.** F7 (item 4 (g): a
  short write returns success) and F12 (item 3: `make_row` refuses bad input by name) are contract lines the code does not meet.
  Also INFO: the AC 1 paste gives the command as `python3 -c …`, which fails with the system interpreter; it passes with the venv
  (reproduced in GATES) or `PYTHONPATH=src`, as the coordinator's premise already noted. The RED/GREEN pastes carry no
  invocation lines.
- AP-32 at L:61 (`hashlib.sha256` in `_sha256_hex`): reviewed. The screen asks "is the hashed form EXACTLY what the store holds?".
  Yes: both digests hash `canonical()` text, and `replay` proves each stored line equals `canonical(parsed)` (L:316, `expected_bytes`) before it
  recomputes. The builder's "intentional" is right. INFO.

### Item 9 — out of scope, touchpoints only

- J1-1: F17 (normalize is not idempotent on its own output: strip before the bound, PIN-strip before the bound; returned as a
  CONTRACT-DEFECT); F13 (the canonical newline detail carries 32 raw characters); F14 (None named "float", C-F6); F15 (U+2028,
  U+2029 and NEL pass `canonical()` raw); F2 (the 200-character msg bound merges distinct findings).
- J1-3: F1, F2, F3, F18, F22, F24.
- Laya: none. `python3 scripts/no_laya_in_gates.py` → `38 files scanned, clean`. No probe here imported or called a model, and no
  probe used the network.

## MUTATION TABLE

Harness `vj12/probe/run_mutants.sh` + `mutants.py`: each mutant is an exact-text replacement (the expected occurrence count
asserted) on a fresh `cp -a` of the PIN copy, then `py_compile`, `pytest --collect-only`, and a full run of
`tests/test_decisions_ledger.py tests/test_decisions_canonical.py` with `--basetemp` under the scratch root. The copy is deleted after
each row; the tree is never touched. The `module:` column is the imported `ledger.py`, printed by the same interpreter.
```
BASE | compiles | collected: 27 tests collected in 0.06s | 27 passed in 0.11s | module: mut/BASE/src/agent_factory/decisions/ledger.py
M0 | compiles | collected: 27 tests collected in 0.06s | 10 failed, 17 passed in 0.17s | module: mut/M0/src/agent_factory/decisions/ledger.py
M8 | compiles | collected: 27 tests collected in 0.06s | 2 failed, 25 passed in 0.15s   failed: test_source_digest_not_in_identity test_state_not_canonical
M9 | compiles | collected: 27 tests collected in 0.06s | 1 failed, 26 passed in 0.14s   failed: test_unparseable_lines
M10 | compiles | collected: 27 tests collected in 0.06s | 3 failed, 24 passed in 0.14s  failed: test_relanding_same_row_id test_source_digest_not_in_identity test_duplicate_refused_bytes_unchanged
M11 | compiles | collected: 27 tests collected in 0.06s | 27 passed in 0.11s
M12 | compiles | collected: 27 tests collected in 0.06s | 27 passed in 0.11s
M13 | compiles | collected: 27 tests collected in 0.06s | 27 passed in 0.14s
M14 | compiles | collected: 27 tests collected in 0.07s | 27 passed in 0.11s
M15 | compiles | collected: 27 tests collected in 0.06s | 1 failed, 26 passed in 0.14s  failed: test_unparseable_lines (Failed: DID NOT RAISE)
M15b compiles … 27 passed in 0.16s
M16 | compiles | collected: 27 tests collected in 0.06s | 1 failed, 26 passed in 0.15s  failed: test_state_not_canonical
M17 | compiles | collected: 27 tests collected in 0.06s | 1 failed, 26 passed in 0.13s  failed: test_state_not_canonical
M18 | compiles | collected: 27 tests collected in 0.05s | 27 passed in 0.11s
M19 | compiles | collected: 27 tests collected in 0.06s | 27 passed in 0.12s
M20 | compiles | collected: 27 tests collected in 0.07s | 27 passed in 0.11s
m1 | compiles | collected: 27 tests collected in 0.06s | 1 failed, 26 passed in 0.14s   failed: test_missing_provenance_each (KeyErro…)
m2 | compiles | collected: 27 tests collected in 0.06s | 3 failed, 24 passed in 0.13s   failed: test_relanding_same_row_id test_source_digest_not_in_identity test_duplicate_refused_bytes_unchanged
m3 | compiles | collected: 27 tests collected in 0.06s | 2 failed, 25 passed in 0.13s   failed: test_tamper_detected test_corrupt_ledger_not_appended
m5 | compiles | collected: 27 tests collected in 0.06s | 1 failed, 26 passed in 0.14s   failed: test_state_not_canonical
m7 | compiles | collected: 27 tests collected in 0.07s | 2 failed, 25 passed in 0.11s   failed: test_replay_byte_identical_x2 test_append_only_prefix
M9 kill:  E  - decision-ledger-unparseable: …/test_unparseable_lines0/nc.jsonl:2   E  + decision-row-duplicate: c651c0c3…
M16 kill: E  Expected regex: 'decision-row-state-not-canonical'  Actual message: 'decision-row-digest-mismatch: a7ef30d0…'
```

| # | mutant (exact replacement in L) | compiles | collected | result |
|---|---|---|---|---|
| M0 | `append` raises at entry (harness self-check) | yes | 27 | killed: 10 tests (proves the mutated copy is imported) |
| M8 | `source_digest` back into `_compute_row_id` (L:70) | yes | 27 | killed: T:165 `test_source_digest_not_in_identity`, T:387 `test_state_not_canonical` |
| M9 | `if raw_line != expected_bytes:` → `if False:` (L:316) | yes | 27 | killed: T:470 `test_unparseable_lines` (exact string) |
| M10 | append's `if row["row_id"] in seen_ids:` → `if False:` (L:247) | yes | 27 | killed: T:124 `test_relanding_same_row_id`, T:165 `test_source_digest_not_in_identity`, T:278 `test_duplicate_refused_bytes_unchanged` |
| M11 | `_is_hex64` accepts `ABCDEF` (L:67) | yes | 27 | SURVIVED |
| M12 | `os.fsync(fd)` → `pass` (L:257) | yes | 27 | SURVIVED (not equivalent: durability changes; an `os.fsync` call spy would kill it) |
| M13 | every `)[:80]` → `)[:79]` (L:127) | yes | 27 | SURVIVED |
| M14 | replay's `if parsed["row_id"] in seen_ids:` → `if False:` (L:325) | yes | 27 | SURVIVED |
| M15 | `if parts[-1] != b"":` → `if False:` (L:284; the torn part is then dropped) | yes | 27 | killed: T:470 `test_unparseable_lines` (DID NOT RAISE) |
| M15b | as M15, and `lines = parts[:-1]` keeps a final unterminated part (L:290) | yes | 27 | SURVIVED |
| M16 | `"path"` dropped from the identity (L:78) | yes | 27 | killed: T:387 `test_state_not_canonical` only (its hand-built identity) |
| M17 | `"question_id"` dropped from the identity (L:74) | yes | 27 | killed: T:387 `test_state_not_canonical` only |
| M18 | the row_id mismatch names `expected_rid`, not the carried id (L:167-170) | yes | 27 | SURVIVED |
| M19 | replay wraps `_validate_row(parsed)` (L:322) and re-raises as unparseable | yes | 27 | SURVIVED |
| M20 | `f"calibration_state={v}"` → `f"calibration_state="` (L:132) | yes | 27 | SURVIVED |
| m1 | builder m1: `"producer"` out of `_ROW_FIELDS` (L:48) | yes | 27 | killed: T:222 `test_missing_provenance_each` (`KeyError`) |
| m2 | builder m2: the duplicate `raise` → `return row["row_id"]` (L:248) | yes | 27 | killed: T:124 `test_relanding_same_row_id`, T:165 `test_source_digest_not_in_identity`, T:278 `test_duplicate_refused_bytes_unchanged` |
| m3 | builder m3: replay's `_validate_row(parsed)` → `pass` (L:322) | yes | 27 | killed: T:296 `test_tamper_detected`, T:584 `test_corrupt_ledger_not_appended` |
| m4 | builder m4 = M8 | — | — | killed (M8) |
| m5 | builder m5: `if restate != row["state"]:` → `if False:` (L:185) | yes | 27 | killed: T:387 |
| m6 | builder m6 = M9 | — | — | killed (M9) |
| m7 | builder m7: `O_TRUNC` for `O_APPEND` (L:253) | yes | 27 | killed: T:104 `test_replay_byte_identical_x2`, T:562 `test_append_only_prefix` |

No mutant was a syntax kill (AF-AP-78): every row compiled and collected 27.

## GATES

One foreground call, 2026-09-23T04:25:34Z → 04:25:36Z, in the tree (read-only; `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`,
`--basetemp` under the scratch root). `git status --short` printed the same four untracked files (other lanes') before and
after, plus this report.
```
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=<scratch>/vj12/gate/bt
27 passed in 0.14s
rc=0
$ (the same, run 2, after rm -rf of the basetemp)
27 passed in 0.14s
rc=0
$ /root/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/ledger.py tests/test_decisions_ledger.py
rc=0
$ /root/venv-agent-factory/bin/python -c "import agent_factory.decisions as d, agent_factory.decisions.canonical, agent_factory.decisions.ledger; print('OK')"
OK
$ python -m pytest tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=<scratch>/vj12/gate/bt2      (python = /usr/local/bin/python)
13 passed in 0.13s
$ python3 scripts/ap_screen.py src/agent_factory/decisions/ledger.py
--- AP_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-32: 1
    src/agent_factory/decisions/ledger.py:61: return hashlib.sha256(text.encode("utf-8")).hexdigest()
$ python3 scripts/ap_screen.py --tests tests/test_decisions_ledger.py
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 38 files scanned, clean
$ RED — the PIN tests with ledger.py removed (a scratch copy): PYTHONPATH=<copy>/src … -m pytest tests/test_decisions_ledger.py -q
FAILED tests/test_decisions_ledger.py::test_import_ac1 … (13 names, as the builder listed)
13 failed in 0.17s
rc=1
grep -c "ModuleNotFoundError: No module named 'agent_factory.decisions.ledger'"  → 13
$ python3 scripts/report_lint.py --min-refs 12 --map L=src/agent_factory/decisions/ledger.py --map V=src/agent_factory/decisions/volatile.py --map C=src/agent_factory/decisions/canonical.py --map T=tests/test_decisions_ledger.py tasks/briefs/laya/VERIFY-J1-2-report.md --root .
report_lint: 99 refs — OK 99, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```
The lint needed three fix rounds (OK 53 with MISS 32, then OK 91 with MISS 6, then OK 99 with MISS 0); the last run above is
after the final text edits.

The coordinator's premise (27/27, 13 passed, pyflakes, screens) reproduces exactly. The scratch-copy baseline also printed
`27 passed in 0.11s` (MUTATION TABLE, BASE).

## FOLLOW-UPS (non-blocking; one line each, for D-034 issues)

- F1: a revised incumbent answer is refused as a plain duplicate and the stale answer stays; add a distinct conflict reason or a J1-3 check.
- F2: J1-3 locators must be unique per decision (two findings under one heading collide; the 200-character msg bound merges them).
- F3: normalize or refuse non-canonical `source_ref.path` spellings (`./a`, `a//b`, `a/./b`, `a/`, NUL, `~/x`, padded spaces, `.`, `C:/x`).
- F4: `replay` should map every parse/canonical failure (TypeError, UnicodeEncodeError, RecursionError) to `decision-ledger-unparseable: <path>:<lineno>`.
- F5: close the row shape (refuse unknown top-level and `source_ref` keys); colliding extra keys let `append` write a line `replay` refuses.
- F8: refuse a non-regular file at the ledger path (a FIFO hangs both functions).
- F9: decide on symlinks (`O_NOFOLLOW`, or document that they are followed; a dangling link makes `append` create its target).
- F12: `make_row` should validate its own output (`_validate_row`) and pre-check `source_ref` sub-fields (bare `KeyError` today).
- F15: refuse or escape U+2028, U+2029 and NEL in row strings (they split a line for `str.splitlines()` readers).
- F22: redact or refuse secret-shaped text in `incumbent_answer`, `producer` and `source_ref.locator`.
- F25: pin the eight surviving mutants' contract lines with tests (exact T:296 `test_tamper_detected` and T:507 `test_invalid_fields` strings, uppercase hex, 81-char cut, in-file duplicate, final line without newline, fsync).
- F26: correct the builder report's "DISCREPANCIES: None" and state the AC 1 interpreter.
- F18: a batch append (one replay per batch) before J1-3's real harvest (400 appends took 12.68 s; quadratic).
- F6/F13/F14/F21/F23: wording and detail polish (wrong type reported as `missing`; newline and raw text in details; reason names; NFC round trip; refusal order).

## NOT-done (first-class)

- No crash or power-loss test: the durability of `os.fsync` and of a new ledger's directory entry (F20) is UNVERIFIED.
- No concurrent-writer probe: one writer at a time is a declared limit, so concurrency was out of scope.
- The short-write probe used tmpfs only (the brief's venue). ext4/xfs short-write behaviour on a full disk was not measured.
- J1-1's internals were not re-litigated (item 9). F17 measures only their effect on the J1-2 round trip.
- No PC run and no bridge use: this is a sandbox lane. No `pc_suite.sh` was used.
- The full repo suite was not run; only the two brief-named files, the seed's AC 1/AC 2, and the screens.
- No prism or slopo/sentrux pass: advisory tools, not asked for. The boundary is three files read whole; graft was used for the
  one reachability claim (F24), together with a literal sweep.
- Timings (F18) are indicative only, taken on a shared 4-core box while another verifier ran.
- The scratch root `vj12/` (the PIN copy, the probe scripts `common.py`, `item1.py` … `item_rt2.py`, `run_mutants.sh`,
  `mutants.py`, the hostile ledgers and the candidate-fix copy) was removed at the end, as the brief requires. Only the
  pasted outputs in this report remain; each probe is described here closely enough to rebuild.
