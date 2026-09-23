# J1-2-R1 — ledger.py: the ONE focused repair of VERIFY-J1-2 (F7, the short write reported as success, plus the same-seam items)

PIN: 6bf2522 (origin head at authoring; the decisions boundary is byte-identical to the J1-2 landing 9d11c25, measured below).
LANE: laya-j1-2-r1 (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation — `isolation: "worktree"` fails
on this tree). Honey `ultra` Lever-2: your report is DATA — files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn
subagents.

D-031 KEY: component J1-2 `src/agent_factory/decisions/ledger.py` · frozen contract `tasks/briefs/laya/J1-2-brief.md` items 1-7 +
AMENDMENT J1-A1, amended below by J1-A2…J1-A6 · production-code digest `803197133f2e2f6e` (ledger.py at 9d11c25). This is the ONE
focused repair. A NOT-READY after it goes back to the coordinator, never to an "R2".

CONTRACT SOURCES: the J1-2 brief (above) · `tasks/briefs/laya/VERIFY-J1-2-report.md` (the findings; an INPUT, its fixes are
suggestions — this brief decides) · `seeds/seed-laya-j1-v1.yaml` AC 1 and AC 2 (unchanged).

BOUNDARY (exact): MODIFY `src/agent_factory/decisions/ledger.py`, MODIFY `tests/test_decisions_ledger.py`, CREATE
`tasks/briefs/laya/J1-2-R1-report.md` (write it incrementally from the start). Read anything. Do NOT modify
`src/agent_factory/decisions/__init__.py`, `canonical.py` or `volatile.py` (J1-1's: its verify VERIFY-J1-1 is running on the PC
against those bytes, and J1-1-R1 will touch `volatile.py`), `tests/test_decisions_canonical.py`, the goldens under
`tests/fixtures/decisions/`, anything under `scripts/`, `proofs/`, `.github/`, `.claude/`, `sandbox-kit/`, any hook, or
`pyproject.toml`. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push` here. No
outward-facing action of any kind (no issues, PRs, comments). The sandbox has about 2 GB free: keep scratch small, under
`/tmp/j12r1/` or `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/j12r1/`, and delete it at the end.
Unmount every tmpfs you mount (`grep -c <your dir> /proc/mounts` must print 0 at the end, pasted). No model, no network, no Laya
call anywhere (KC-J1).

CODE INTEL FIRST: a pack is ready at `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/j12r1/pack.md`
(`scripts/lane_context.sh` over ledger.py + its test, symbols append/replay/make_row/_validate_row; 211 lines). Read it first;
code questions go to `graft ask` before any grep.

## Why

VERIFY-J1-2 (sandbox Opus 5 verifier, PIN 9d11c25) returned NOT-READY on ONE blocker, reproduced independently by the
coordinator: `append` ignores `os.write`'s byte count (L:256), so on a full filesystem it returns the row_id while the file holds a
torn partial line, and from then on every `replay` and every `append` is refused. J1-3's harvest would count a row that is not
there. The same verify found, in the same four functions, bare exceptions where the contract names refusals, an open row shape, a
path check that lets equivalent spellings mint new identities, a FIFO that hangs both functions, symlinks followed, and an
untyped `ledger_path` that turns a corrupt ledger into `[]`. One focused repair closes them together (D-031). F17 (J1-1's
`normalize` is not idempotent) is NOT yours: it goes to J1-1-R1. Everything else the verify listed is issue #30.

## The contract (coordinator, decided; do not re-litigate — a line you cannot meet is a DISCREPANCY with its measurement, never a silent change)

Items 1-7 of the J1-2 brief and J1-A1 stand, except where amended here. Error class stays `DecisionStateError` from
`agent_factory.decisions.volatile` (`str(e) == f"{reason}: {detail}"`), no new exception class. FOUR NEW REASONS, exactly these
spellings: `decision-ledger-short-write`, `decision-ledger-not-regular`, `decision-ledger-path-invalid`,
`decision-row-unknown-field`.

**R1 — write-all-or-refuse (F7; item 4 (g) clarified).** `append` returns the row_id ONLY after `os.write` reported every byte of
`canonical(row) + "\n"` and `os.fsync` returned. Record the file size from `os.fstat(fd)` after the open and before the write. If
the one `os.write` returns fewer bytes than the line, truncate the file back to that size (`os.ftruncate` on the same fd — it
removes only this call's bytes, never existing ones), `os.fsync`, and raise `decision-ledger-short-write: <path>:<written>/<expected>`
(for example `…/ledger.jsonl:50/693`). If the truncate itself fails, raise the same reason with the detail
`<path>:<written>/<expected> truncate-failed`, chained from the OSError. Never complete a partial line with a second write. An
`OSError` from `os.write` (ENOSPC with nothing written, EIO) or from `os.fsync` propagates unchanged: loud, and the declared limits
say what it leaves.

**R2 — J1-A6: no bare exception from content.** For ANY row content or ledger-line content, `make_row`, `append` and `replay`
raise only `DecisionStateError` (filesystem `OSError` from open/read/write/fsync is the one exception class that may still
propagate, per R1 and R6). Concretely:
- `replay`: every exception from parsing a line (`json.loads`) or re-encoding it (`canonical(parsed).encode("utf-8")`) —
  `ValueError` and its subclasses (`JSONDecodeError`, `UnicodeError`), `RecursionError`, `TypeError`, and J1-1's own
  `DecisionStateError` — becomes `decision-ledger-unparseable: <path>:<lineno>`; so does a line whose JSON value is not an object.
  A row-level refusal from (a)-(d) on a well-formed line keeps ITS reason (never re-labelled unparseable — mutant M19 below).
- `_validate_row` on a dict raises only `DecisionStateError`. In step (b), each top-level field's value (and each `source_ref`
  sub-field) must canonicalize and encode as UTF-8: a J1-1 canonical refusal propagates unchanged (item 6); any other exception
  becomes `decision-row-invalid: <field>=<ExceptionClassName>` (e.g. `incumbent_answer=UnicodeEncodeError`,
  `state=RecursionError`), with `<field>` the top-level name or `source_ref.<sub>`. A row that is not a dict:
  `decision-row-invalid: row=<type name>` (e.g. `row=int`, `row=NoneType`).
- `make_row`: see R7.

**R3 — J1-A2: the row shape is closed (F5).** Right after (a), a top-level key outside the ten fields is refused
`decision-row-unknown-field: <key>`, a `source_ref` key outside its four `decision-row-unknown-field: source_ref.<key>`; with
several, the first in sorted order. And, as the structural half: `append` writes only a line that `replay`'s own per-line check
accepts. Factor replay's per-line check (parse, canonical byte equality, object check, (a)-(d)) into ONE helper and run it on the
exact bytes `append` is about to write before the write; a refusal there raises that reason and writes nothing. If no test can
reach this second guard once R3's first half exists, say so and mark its mutant EQUIVALENT with the reason.

**R4 — J1-A3: one spelling per path (F3).** `source_ref.path`, beyond item 1's three rules (no leading `/`, no `..` segment, no
`\`), must satisfy: `posixpath.normpath(path) == path`; not `.`; no character below U+0020, no U+007F, U+0085, U+2028 or U+2029;
no leading or trailing whitespace; no leading `~`; no drive prefix (`^[A-Za-z]:`). Else
`decision-row-invalid: source_ref.path=<str(path)[:80]>` (the existing detail format). Positive controls that stay ACCEPTED:
`docs/INCIDENT-LOG.md`, `a/..b` (not a `..` segment), `%2e%2e/a` (a literal name on POSIX), `a/b.c`.

**R5 — J1-A4: `ledger_path` is `str | os.PathLike[str]` (F11).** Both functions resolve it ONCE with `os.fspath` at entry and use
that string everywhere (the open, every `<path>` detail). Refused `decision-ledger-path-invalid: <detail>`: a type `os.fspath`
rejects or a `bytes` result → the detail is `type(ledger_path).__name__` (`NoneType`, `int`, `bytes`); the empty string → `empty`;
a string holding NUL → `nul`. An `os.DirEntry` resolves to its real path (so a corrupt ledger reached through one is refused, not
`[]`). `pathlib.Path` and relative strings behave exactly as today (the existing `<path>:<lineno>` tests stay green unchanged).

**R6 — J1-A5: the ledger is a regular file (F8, F9, F10).** Decided on the opened FD, never by a check on the name before the open
(AF-AP-70). `replay` opens with `os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC`, `os.fstat`s the fd, refuses anything
but `S_ISREG` as `decision-ledger-not-regular: <path>`, and reads the bytes through that same fd. `append` (after its replay)
opens with `os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, 0o644` and makes the same
`fstat` check before writing. An open that fails with `ELOOP` (the final component is a symlink — dangling or not) is
`decision-ledger-not-regular: <path>` too; a missing file stays the empty ledger `[]` for `replay` (`FileNotFoundError` only). A
FIFO, a directory, a socket or a device at the path is refused by both functions and never blocks. A dangling symlink: `replay`
refuses and `append` creates NOTHING.

**R7 — `make_row` refuses by name and validates its own output (F12; item 3 made true).** Before any J1-1 call, `make_row` checks
its row-field inputs in `_ROW_FIELDS` order with step (a)'s reasons: `incumbent_answer` and `producer` must be non-empty `str`
(`decision-row-incomplete: missing <field>`); `source_ref` must be a dict (`decision-row-incomplete: missing source_ref.kind` —
(a)'s existing wording for a non-dict, kept) holding the four sub-fields as non-empty `str` (`missing source_ref.<sub>`). Then
`schema_keys` and the J1-1 calls exactly as today (J1-1's refusals pass through unchanged, item 6); a NON-`DecisionStateError`
exception from those calls (today a lone surrogate in `raw_state` escapes as `UnicodeEncodeError`) becomes
`decision-row-invalid: state=<ExceptionClassName>`. Then `_validate_row(row)` on the finished row before returning it, so a row
`make_row` returns is always one `append` accepts (the kind set, the path rules, the hex shapes, the per-field encode rule).

**R8 — the tests pin the contract's own words (F25).** The eight mutants below survive the PIN's suite (measured). Each must be
killed by a named test after your change: exact-string assertions in `test_tamper_detected` (each file flip →
`decision-row-digest-mismatch: <the row_id the tampered line carries>`; never `decision-ledger-unparseable`),
`test_invalid_fields` (each → `decision-row-invalid: <field>=<value>` exactly), `test_relanding_same_row_id` and
`test_state_not_canonical` (exact strings); plus new tests for an uppercase hex digest in each of `source_ref.source_digest`,
`state_digest` and `row_id`; an invalid value of exactly 80 and exactly 81 characters (the detail carries the first 80); the same
valid line twice in one file (`decision-row-duplicate: <row_id>` from `replay`); a complete valid row as the last line without
its `\n` (`decision-ledger-unparseable: <path>:<n>`); one `os.fsync` call on the ledger's fd per successful append, after the
write (a spy that records the calls and changes nothing).

**Declared limits** (the module docstring and the report; keep the three existing ones): an unkeyed digest stops accidental or
naive mutation, not a forger who recomputes every digest · deleting a whole row is not detected · one writer at a time · NEW:
`O_NOFOLLOW` covers the final path component only (a symlinked parent directory is followed) · NEW: `ENOSPC` with nothing
written raises `OSError` and leaves the file unchanged · NEW: an `os.fsync` error after a full write raises `OSError` with the
line in place (a later `replay` shows whether it landed) · NEW: `make_row` refuses a lone surrogate anywhere in `raw_state`, even
in a field `normalize` would drop.

## The hostile table (every row is a test assertion; the PIN column is MEASURED — see the PREMISE)

| # | input | PIN today | required after R1-R8 |
|---|---|---|---|
| 1 | `append` with `os.write` forced to write the first 50 of 693 bytes for real (a spy that calls the real `os.write` on `data[:50]`) onto a 2-row ledger | returns the row_id; 50 bytes of a torn line left (measured on an empty ledger) | `decision-ledger-short-write: <path>:50/693`; the file's bytes == the 2-row bytes before; `replay` returns the 2 rows; the next good append succeeds |
| 2 | the same with `os.write` returning 0 and writing nothing | returns the row_id | `decision-ledger-short-write: <path>:0/<len>`; bytes unchanged |
| 3 | a real 4 KiB tmpfs (root only: `mount -t tmpfs -o size=4k`; skip with a named reason when not root or the mount fails), appended until a row only partly fits | returns the row_id at +651 of 689 bytes; the next append and `replay` refused | the partial append refused `decision-ledger-short-write: <path>:<n>/<len>`; bytes unchanged; `replay` OK; umount verified in a `finally` |
| 4 | the same tmpfs filled to the byte, one more append | `OSError` ENOSPC, file unchanged | unchanged (declared limit) |
| 5 | `replay`, line 2 = `1` / `"calibration_state"` / `[]` | `TypeError` / `TypeError` / `decision-row-incomplete: missing calibration_state` | `decision-ledger-unparseable: <path>:2` each |
| 6 | `replay`, line 2 with a `\ud800` escape, and with raw bytes ED A0 80 inside a string | `UnicodeEncodeError` | `decision-ledger-unparseable: <path>:2` |
| 7 | `replay`, line 2 = 600-deep and 100000-deep nesting | `RecursionError` | `decision-ledger-unparseable: <path>:2` |
| 8 | `replay` / `append` on a FIFO (the test must fail in ≤ 10 s if it would block: a subprocess with a timeout, or `signal.alarm`) | blocks forever | `decision-ledger-not-regular: <path>`, returns at once |
| 9 | a symlink to a valid ledger; a dangling symlink | followed (1 row); `[]` and `append` CREATES the target | `decision-ledger-not-regular: <path>` for both functions; the dangling target does not exist afterwards |
| 10 | a directory at the path | `IsADirectoryError` | `decision-ledger-not-regular: <path>` |
| 11 | `replay(os.DirEntry)` of a 2-line ledger whose line 2 is garbage | `[]` | `decision-ledger-unparseable: <entry.path>:2` |
| 12 | `replay` / `append` with `None`, `1`, `b"sub/rel.jsonl"`, `""`, `"a\x00b"` | `[]`, `[]`, `[]`, `[]`, `ValueError`; `append(None, row)` writes `./None` | `decision-ledger-path-invalid: NoneType` / `int` / `bytes` / `empty` / `nul`; nothing created |
| 13 | `append(DirEntry)` of a DUPLICATE of a ledger's row | accepted into a junk file named `<DirEntry 'x'>` | `decision-row-duplicate: <row_id>`; no junk file |
| 14 | `append(path, 1)`, `append(path, None)` | `TypeError` | `decision-row-invalid: row=int` / `row=NoneType` |
| 15 | `append` of a row + an extra top-level key `zz_extra`, digests recomputed | accepted; `replay` returns it | `decision-row-unknown-field: zz_extra`; nothing written |
| 16 | the same with an extra `source_ref` key | accepted | `decision-row-unknown-field: source_ref.zz_extra` |
| 17 | `make_row` with `source_ref` missing `kind` / `path` / `locator` | `KeyError` | `decision-row-incomplete: missing source_ref.kind` / `.path` / `.locator` |
| 18 | `make_row(source_ref=None)` | `TypeError` | `decision-row-incomplete: missing source_ref.kind` |
| 19 | `make_row(producer="")`, `make_row(producer=None)` | a row / `decision-canonical-float: $.producer` | `decision-row-incomplete: missing producer` both |
| 20 | `make_row(incumbent_answer=5)`, `make_row(incumbent_answer="")` | a row (which `append` refuses) | `decision-row-incomplete: missing incumbent_answer` both |
| 21 | `make_row` with `source_ref.kind="bogus"` / `source_ref.path="/etc/passwd"` | a row | `decision-row-invalid: source_ref.kind=bogus` / `source_ref.path=/etc/passwd` |
| 22 | `make_row` with a lone surrogate in `source_ref.locator` / `incumbent_answer` / `raw_state["file"]` | `UnicodeEncodeError` ×3 | `decision-row-invalid: source_ref.locator=UnicodeEncodeError` / `incumbent_answer=UnicodeEncodeError` / `state=UnicodeEncodeError` |
| 23 | paths `./docs/INCIDENT-LOG.md`, `docs//INCIDENT-LOG.md`, `docs/./INCIDENT-LOG.md`, `docs/INCIDENT-LOG.md/`, `~/x`, ` docs/x `, `.`, `C:/x`, `a\tb`, `a\u2028b`, `a\x00b` | accepted, each with its own row_id | `decision-row-invalid: source_ref.path=<value[:80]>` each, from `make_row` AND from `append` of a hand-built row |
| 24 | paths `docs/INCIDENT-LOG.md`, `a/..b`, `%2e%2e/a`, `a/b.c` | accepted | still accepted (positive controls) |
| 25 | J1-1's refusals through `make_row` (`test_j1_1_refusals_propagate`) | named | unchanged |

## Tests (`tests/test_decisions_ledger.py`)

Every row of the table above is asserted with the EXACT refusal string (or the exact accepted outcome). Write each new test RED
first against the PIN's `ledger.py` and paste the RED run (the failures must be the table's PIN column — a test that fails for
another reason is not a RED control), then GREEN. The existing 13 tests stay; an existing assertion may only be made STRICTER
(R8), never weaker or deleted; a changed expectation names its amendment in a comment. Every secret-like string in a test is an
INVENTED value. Paste the whole-file RED list and the GREEN run.

## Mutants (scratch-copy restore only — never a git restore in this shared tree; each mutant compiles and collects, AF-AP-78; a harness self-check row M0 first proves the mutated copy is the one imported)

The eight SURVIVORS at the PIN (measured below), each now killed by a named test: M11 `_is_hex64` accepts `ABCDEF` · M12
`os.fsync(fd)` → `pass` · M13 every `)[:80]` → `)[:79]` · M14 replay's in-file duplicate check → `if False:` · M15b the final-newline
check → `if False:` and the unterminated last part kept · M18 the row_id mismatch detail names the recomputed id, not the carried
one · M19 replay re-raises every row refusal as `decision-ledger-unparseable` · M20 `f"calibration_state={v}"` →
`f"calibration_state="`. And the new code's own mutants: N1 the written-count check removed · N2 the truncate removed (refuse,
but leave the partial line) · N3 `O_NOFOLLOW` dropped from `replay`'s open · N4 the `S_ISREG` check dropped · N5 `os.fspath` →
`str` · N6 the closed-shape check removed · N7 the `normpath` rule removed · N8 `make_row`'s `_validate_row(row)` call removed ·
N9 replay's broadened `except` narrowed back to `(json.JSONDecodeError, ValueError)` · N10 replay's object check removed · N11
append's pre-write line check removed (EQUIVALENT allowed with the reason, per R3). One row each: mutant · compiles · collected
count · killed-by (test id) / SURVIVED / EQUIVALENT with the reason.

## Gates (paste verbatim, each with its invocation)

`mkdir -p /tmp/j12r1/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/j12r1/bt`
twice as root (`rm -rf /tmp/j12r1/bt` after each; the tmpfs test RUNS) · the same two files once as `nobody` (the CI-like venue;
the tmpfs test SKIPS with its named reason, everything else passes): `rm -rf /tmp/j12r1nr && mkdir -p /tmp/j12r1nr && chmod 1777
/tmp/j12r1nr && setpriv --reuid=65534 --regid=65534 --clear-groups env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest
tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/j12r1nr/bt` ·
`/root/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/ledger.py tests/test_decisions_ledger.py` · the seed's
AC 1 (`/root/venv-agent-factory/bin/python -c "import agent_factory.decisions as d, agent_factory.decisions.canonical,
agent_factory.decisions.ledger; print('OK')"`) and AC 2 (`python -m pytest tests/test_decisions_ledger.py -q`, basetemp under
/tmp/j12r1) · `python3 scripts/ap_screen.py src/agent_factory/decisions/ledger.py` and `python3 scripts/ap_screen.py --tests
tests/test_decisions_ledger.py` · `python3 scripts/no_laya_in_gates.py` (must stay clean) · the census: `grep -c j12r1
/proc/mounts` → 0.

## Report (`tasks/briefs/laya/J1-2-R1-report.md`, written incrementally)

Sections: PREMISE re-measured (item 1 of your work: re-run the premise commands below on the PIN and stop CONTRACT-INVALID on a
mismatch that changes the contract) · what changed (L:/T: refs per R1-R8) · the hostile table with the observed result per row ·
RED then GREEN (pasted) · the mutant table · gates (pasted) · the declared limits as written in the docstring · DISCREPANCIES
(every contract line you could not meet, with its measurement — "None" only if true) · TOUCHPOINTS (one line each; e.g. J1-1's
`canonical()` does not refuse a lone surrogate by name — that is J1-1-R1's, not yours) · NOT-done. Lint floor:
`python3 scripts/report_lint.py --min-refs 12 --map L=src/agent_factory/decisions/ledger.py --map T=tests/test_decisions_ledger.py
tasks/briefs/laya/J1-2-R1-report.md --root .` — cite `L:<line>` / `T:<line>`; apply its `fix:` hints for at most three rounds,
then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 04:3x-04:5xZ, sandbox @ 9ca6d09 → 6bf2522; the decisions boundary unchanged between them)

```
$ git rev-parse --short HEAD; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
6bf2522
6bf2522
$ git diff --stat 9d11c25 6bf2522 -- src/agent_factory/decisions tests/test_decisions_ledger.py tests/test_decisions_canonical.py tests/fixtures/decisions
(empty = byte-identical)
$ sha256[:16] + lines
803197133f2e2f6e 333 src/agent_factory/decisions/ledger.py
bc9cb1d03fdb77a4 77 src/agent_factory/decisions/canonical.py
b48899c883c7231f 295 src/agent_factory/decisions/volatile.py
2aec3875f71213e4 21 src/agent_factory/decisions/__init__.py
787f08043ca086a1 634 tests/test_decisions_ledger.py
48fdf09e8038a146 340 tests/test_decisions_canonical.py
$ git log --format='%h %s' -- src/agent_factory/decisions/ledger.py tests/test_decisions_ledger.py      (ancestry: no later repair)
9d11c25 Laya J1-2 landed (GATED-PENDING-VERIFY): the append-only decision ledger with mandatory provenance, row identity
$ grep -n (the line map, ledger.py)
36:_VALID_KINDS = frozenset({        44:_ROW_FIELDS = (        57:_SOURCE_REF_FIELDS = ("kind", "path", "source_digest", "locator")
60:def _sha256_hex   64:def _is_hex64   70:def _compute_row_id   85:def _compute_row_digest   90:def _validate_row
127:        v = str(row["checkpoint_digest"])[:80]        (9 occurrences of ")[:80]" in the file)
191:def make_row      227:    return row
230:def append       240:    _validate_row(row)      246:    seen_ids = {r["row_id"] for r in existing}
252:    fd = os.open(    253:        str(ledger_path), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644
256:        os.write(fd, line.encode("utf-8"))      257:        os.fsync(fd)
264:def replay       272:    path_str = str(ledger_path)       274:        with open(path_str, "rb") as fh:
284:    if parts[-1] != b"":      303:            parsed = json.loads(raw_line)     304:        except (json.JSONDecodeError, ValueError):
311:            expected_bytes = canonical(parsed).encode("utf-8")      312:        except DecisionStateError:
316:        if raw_line != expected_bytes:      322:        _validate_row(parsed)      325:        if parsed["row_id"] in seen_ids:
$ grep -n '^def test_' tests/test_decisions_ledger.py
70 test_import_ac1 · 104 test_replay_byte_identical_x2 · 124 test_relanding_same_row_id · 165 test_source_digest_not_in_identity ·
222 test_missing_provenance_each · 278 test_duplicate_refused_bytes_unchanged · 296 test_tamper_detected · 387
test_state_not_canonical · 470 test_unparseable_lines · 507 test_invalid_fields · 562 test_append_only_prefix · 584
test_corrupt_ledger_not_appended · 609 test_j1_1_refusals_propagate
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/j12r1p/bt
27 passed in 0.14s
$ (as nobody, system python3 = pytest 9.1.1, PYTHONPATH=src) the same two files, --basetemp=/tmp/j12r1nr/bt
27 passed in 0.13s
$ the coordinator's probe at the PIN ($SP/j12r1_premise.py + j12r1_premise2.py; golden b1.finding_kind, raw state keys ['file', 'kind', 'msg'])
=== F7 forced short write (os.write writes k=50 bytes for real, returns 50)
append (short write)                         OK 0c142e19683b63aff41e225f60fcb335c2b6e018898aeff9ec5dcf42511171d8
ledger bytes 50 | ends with newline False | line length 693
next replay                                  DSE decision-ledger-unparseable: <scratch>/f7.jsonl:1
=== F7 real 4 KiB tmpfs (append until the fs is full)
append 0: returned 6ba6c04d2791 | +689 bytes (line 689)
append 1: returned cf5f4cc42582 | +689 bytes (line 689)
append 2: returned cdeb4f4e4f70 | +689 bytes (line 689)
append 3: returned 1759978a601e | +689 bytes (line 689)
append 4: returned f492943084fc | +689 bytes (line 689)
append 5: returned db8649da9bc2 | +651 bytes (line 689)
append 6: refused decision-ledger-unparseable: <scratch>/tmpfs/ledger.jsonl:6
replay                                       DSE decision-ledger-unparseable: <scratch>/tmpfs/ledger.jsonl:6
tmpfs mounts left: 0
=== F4 replay of corrupt lines (line 2)
replay scalar 1                              BARE TypeError: argument of type 'int' is not iterable
replay scalar "calibration_state"            BARE TypeError: string indices must be integers, not 'str'
replay []                                    DSE 'decision-row-incomplete: missing calibration_state'
replay lone surrogate escape                 BARE UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 80
replay raw bytes ED A0 80 in a string        BARE UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 80
replay 600-deep nesting                      BARE RecursionError: maximum recursion depth exceeded
replay 100000-deep nesting                   BARE RecursionError: maximum recursion depth exceeded while decoding a JSON array
=== F8 FIFO / F9 symlink / F10 directory
replay(fifo)                                 BARE TimeoutError: blocked 3 s
# (the probe's own SIGALRM fired after 3 s; without it the open blocks until a writer appears)
replay(symlink)                              OK 1
replay(dangling)                             OK []
append(dangling)                             OK 0c142e19683b
dangling target created: True
replay(directory)                            BARE IsADirectoryError: [Errno 21] Is a directory: '<scratch>/adir'
=== F11 path types
replay(DirEntry of a corrupt ledger)         OK []
append(None)                                 OK 0c142e19683b
./None exists: True
replay(None) OK []
replay(1) OK []
replay(b'...')                               OK []
replay('')                                   OK []
replay('a\x00b')                             BARE ValueError: embedded null byte
append(path, 1)                              BARE TypeError: argument of type 'int' is not iterable
append(path, None)                           BARE TypeError: argument of type 'NoneType' is not iterable
=== F12 make_row bad input
source_ref missing kind                      BARE KeyError: 'kind'
source_ref missing path                      BARE KeyError: 'path'
source_ref missing locator                   BARE KeyError: 'locator'
source_ref None                              BARE TypeError: 'NoneType' object is not iterable
producer ''                                  OK True
# (the probe printed make_row(producer='')['producer'] == '': a row came back)
producer None                                DSE 'decision-canonical-float: $.producer'
incumbent_answer 5 -> make_row               OK 5
incumbent_answer 5 -> append                 DSE decision-row-incomplete: missing incumbent_answer
kind 'bogus' -> make_row                     OK bogus
path '/etc/passwd' -> make_row               OK /etc/passwd
locator lone surrogate                       BARE UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 123
incumbent_answer lone surrogate              BARE UnicodeEncodeError: 'utf-8' codec can't encode character '\ud83d' in position 84
raw_state['file'] lone surrogate             BARE UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800' in position 10
=== F5 extra keys, digests recomputed
append(row + zz_extra)                       OK 0c142e19683b
replay                                       OK zz_extra
# (the probe printed the last sorted key of the replayed row)
append(source_ref + zz_extra)                OK 0c142e19683b
=== F3 path spellings (make_row + append, each into a fresh ledger; the printed rows joined with ·, row_id[:16])
'docs/INCIDENT-LOG.md' OK 0c142e19683b63af · './docs/INCIDENT-LOG.md' OK ae9666aae632ae85 · 'docs//INCIDENT-LOG.md' OK 5ad1432c96bf2c5a
'docs/./INCIDENT-LOG.md' OK 96e1fd1badef9428 · 'docs/INCIDENT-LOG.md/' OK 8630e40557bf1603 · '~/x' OK 353e1ee83b331ab1
' docs/x ' OK 8dd56a2d1efc6d4e · '.' OK 2af2fa61574fe55e · 'C:/x' OK 3009a9d7351931b6 · 'a\tb' OK 91cc1c85b6764b03
'a\u2028b' OK 4218dad00b0addbe · 'a/..b' OK 23ca83d93b05e483 · '%2e%2e/a' OK 9f8f971201308896
$ the eight survivors re-run at the PIN ($SP/j12r1_mutants.py: git archive 9d11c25 into scratch, exact-text replacement with the
  count asserted, py_compile, --collect-only, the two files; the copy deleted after each row)
M0    | compiles | 27 tests collected in 0.06s | 10 failed, 17 passed in 0.22s | failed: test_append_only_prefix test_corrupt_ledger_not_appended test_duplicate_refused_bytes_unchanged test_invalid_fields test_missing_provenance_each test_relanding_same_row_id test_replay_byte_identical_x2 test_source_digest_not_in_identity test_state_not_canonical test_tamper_detected
BASE  | compiles | 27 tests collected in 0.06s | 27 passed in 0.16s | failed: -
M11   | compiles | 27 tests collected in 0.06s | 27 passed in 0.18s | failed: -
M12   | compiles | 27 tests collected in 0.06s | 27 passed in 0.16s | failed: -
M13   | compiles | 27 tests collected in 0.06s | 27 passed in 0.17s | failed: -
M14   | compiles | 27 tests collected in 0.06s | 27 passed in 0.16s | failed: -
M15b  | compiles | 27 tests collected in 0.06s | 27 passed in 0.17s | failed: -
M18   | compiles | 27 tests collected in 0.07s | 27 passed in 0.18s | failed: -
M19   | compiles | 27 tests collected in 0.06s | 27 passed in 0.16s | failed: -
M20   | compiles | 27 tests collected in 0.06s | 27 passed in 0.17s | failed: -
```

The mutant runner and both probes are in the scratchpad (`$SP` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad`):
`j12r1_mutants.py`, `j12r1_premise.py`, `j12r1_premise2.py`. Reuse them; they never touch the tree.
