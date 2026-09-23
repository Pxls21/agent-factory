# VERIFY-J1-2-R1 report — the targeted adversarial verify of the J1-2-R1 ledger repair

Lane: VERIFY-J1-2-R1 (task #152), sandbox `adversarial-verifier`, root. PIN `8a7c7f0` (decisions boundary byte-identical to
the J1-2-R1 landing `d4f4698`). Brief: `tasks/briefs/laya/VERIFY-J1-2-R1-brief.md` (origin `2de4aad`). Frozen contract:
`tasks/briefs/laya/J1-2-R1-brief.md` R1-R8 + its hostile table + its mutant list; `tasks/briefs/laya/J1-2-brief.md` items 1-7 +
J1-A1; the declared limits in L's docstring. Scratch: `$SP/vj12r1/` (a `git archive 8a7c7f0` of `src/`, `tests/`, `scripts/`
and `pyproject.toml`), removed at the end. Cites: `L:` = `src/agent_factory/decisions/ledger.py`, `T:` =
`tests/test_decisions_ledger.py`, `C:` = `src/agent_factory/decisions/canonical.py`, `V:` = `src/agent_factory/decisions/volatile.py`.

**GATE RECOMMENDATION: `NOT-READY`** — four findings meet the whole blocking predicate: F1, F5, F6, F7 (§2). All four are
in-boundary (L + T), small, and carry a red discriminator (§5). None of them corrupts ledger bytes at the PIN. Everything
below was reproduced in this session; nothing in the recommendation rests on an unreproduced claim.

## 1. PREMISE — re-measured at 8a7c7f0 (2026-09-23T05:30:57Z, sandbox, root) — MATCHES

```
$ git diff --stat d4f4698 8a7c7f0 -- src/agent_factory/decisions tests/test_decisions_ledger.py tests/test_decisions_canonical.py tests/fixtures/decisions tasks/briefs/laya/J1-2-R1-report.md
(rc=0; empty = byte-identical)
$ identities at 8a7c7f0 (git object) | worktree
c5c15240fdc4d9eb 617 src/agent_factory/decisions/ledger.py | wt c5c15240fdc4d9eb 617
bc9cb1d03fdb77a4 77 src/agent_factory/decisions/canonical.py | wt bc9cb1d03fdb77a4 77
b48899c883c7231f 295 src/agent_factory/decisions/volatile.py | wt b48899c883c7231f 295
2aec3875f71213e4 21 src/agent_factory/decisions/__init__.py | wt 2aec3875f71213e4 21
fed3ea5c7f1b8005 1468 tests/test_decisions_ledger.py | wt fed3ea5c7f1b8005 1468
48fdf09e8038a146 340 tests/test_decisions_canonical.py | wt 48fdf09e8038a146 340
9dcec5fe8e1ca75d 186 tasks/briefs/laya/J1-2-R1-report.md | wt 9dcec5fe8e1ca75d 186
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_ledger.py tests/test_decisions_canonical.py
2 files set=16a7b628685e
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/vj12r1p/bt   (root, run 1)
53 passed in 0.25s
$ (the same, root, run 2)
53 passed in 0.24s
$ setpriv --reuid=65534 --regid=65534 --clear-groups env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/vj12r1nr/bt -rs
SKIPPED [1] tests/test_decisions_ledger.py:707: test_short_write_real_tmpfs: not root, cannot mount tmpfs   <- `test_short_write_real_tmpfs`
52 passed, 1 skipped in 0.24s
$ python3 scripts/report_lint.py --min-refs 12 --map L=src/agent_factory/decisions/ledger.py --map T=tests/test_decisions_ledger.py tasks/briefs/laya/J1-2-R1-report.md --root .
report_lint: 57 refs — OK 47, NEAR 8, MISS 0, UNCHECKABLE 2, UNRESOLVED 0 (worktree)
$ python3 scripts/ap_screen.py --tests tests/test_decisions_ledger.py
AP-70: 1
    tests/test_decisions_ledger.py:1292: except Exception:   <- `except Exception:`
$ python3 scripts/ap_screen.py src/agent_factory/decisions/ledger.py
AP-32: 1
    src/agent_factory/decisions/ledger.py:77: return hashlib.sha256(text.encode("utf-8")).hexdigest()
$ grep -n 'split\|splitlines' src/agent_factory/decisions/ledger.py
236:    if ".." in path.split("/"):
554:    parts = data.split(b"\n")
$ _PATH_BAD_CHARS (imported from the tree): 36 members, sha256(repr(sorted(set)))[:16] = 9323478b39b9d6e1
$ literal bytes in L and T: 0 x U+2028, 0 x U+2029, 0 x U+0085, 0 x CR (touch 2 holds)
```

Mutant re-runs of the premise, on scratch copies. The harness self-check M0 comes first: `24 failed, 29 passed`, which
proves the scratch copy is the one imported. BASE: `53 passed`.

```
N1    | 53 collected | 2 failed, 51 passed | failed: test_short_write_real_tmpfs test_short_write_spy          (premise: same)
N6    | 53 collected | 1 failed, 52 passed | failed: test_extra_top_level_key_refused                         (premise: same)
N5pre (touch 1 reverted: both monkeypatch.chdir lines -> pass), cwd = a fresh empty dir, -k direntry:
      2 failed, 51 deselected | failed: test_direntry_corrupt_ledger test_direntry_duplicate_refused
      cwd contents: ["<DirEntry 'ledger.jsonl'>"] sizes: [723]                                            (premise: same)
N5    (touch 1 present), same cwd mode, -k direntry:
      2 failed, 51 deselected | cwd contents: [] | junk: bt/test_direntry_duplicate_refuse0/<DirEntry 'ledger.jsonl'> 723  (premise: same)
N5 over the FULL two-file set (not -k): 3 failed, 50 passed — the third red is test_path_types_refused (str(None) = "None")
```

Premise verdict: every identity, count, gate line and mutant row reproduces. One wording difference: the premise's
"2 failed" for N5 counts only the two DirEntry tests. The full set reds a third test, `test_path_types_refused`, exactly as
the lane's own report lists. That is a test SELECTION difference, not a byte difference, so it is INFO-1 and not a
CONTRACT-INVALID stop.

## 2. Finding inventory (no severity filter)

Evidence levels:
- REPRODUCED: a command in this session through the real function at the PIN bytes.
- STATIC: read, not run.
- INFERRED: reasoned from other evidence.

Canonical path means the real `make_row` / `append` / `replay`, imported from `$SP/vj12r1/pin/src`. That copy is
byte-identical to the tree; sha256[:16] `c5c15240fdc4d9eb` is asserted at import. A literal sweep finds no production
importer of the ledger module (only its tests and `scripts/no_laya_in_gates.py`). The public API is therefore the live entry
point, and J1-3 will be its first consumer. This is one instrument and not a DORMANT claim.

### F1 — BLOCKER — `make_row` returns a row that `append` refuses; the lane's N11 "EQUIVALENT" is false (the pre-write guard is live, load-bearing and unpinned)

- **Evidence (REPRODUCED).** Take a plain `str` `source_ref.path` whose first letter is DECOMPOSED and followed by `:`.
  It passes `_validate_row` on the in-memory row, because the drive rule reads `path[1] == ":"` (L:123) and there it sees
  the combining mark. The ledger, however, stores the NFC form (`unicodedata.normalize("NFC"`, C:28), and in NFC form the
  path hits the drive rule. Origin frames: `_check_line(path_str` (L:466) → `_validate_row(parsed)` (L:333) →
  `_validate_path(path)` (L:240) → the raise `source_ref.path={v}` at L:125. Through the real functions:
  ```
  path 'e\u0301:x'        make_row=OK | append=DSE decision-row-invalid: source_ref.path=é:x | file exists after: False
  path 'A\u030a:notes.md' make_row=OK | append=DSE decision-row-invalid: source_ref.path=Å:notes.md | file exists after: False
  _validate_row(row)=OK | _check_line(canonical bytes)=DSE decision-row-invalid: source_ref.path=é:x   (also 'K\u0301:x')
  ```
- **The guard is load-bearing.** The refusal above comes from append's pre-write check
  `parsed_check = json.loads(line_bytes)` (L:465), which the lane called "structurally unreachable". Remove it (the
  lane's N11 mutant, on a scratch copy) and the same row is WRITTEN, which poisons the ledger:
  `append make_row('e\u0301:x') OK aa86f8eda4308113` → `replay DSE decision-row-invalid: source_ref.path=é:x`
  → `next good append DSE decision-row-invalid: source_ref.path=é:x`.
  This is the failure class of VERIFY-J1-2's original blocker (its F7): every later replay and append is refused. N11 over the two-file set gives `53 passed`, so
  it SURVIVES and no test reaches the guard.
- **Structural, not only the drive rule (REPRODUCED).** The drive rule uses `path[0].isalpha()` (L:123), which is wider
  than R4's `^[A-Za-z]:`. So it also refuses the contract-legal composed `é:x` and `Å:notes.md`. On a scratch copy with an
  R4-faithful ASCII rule, NFD and composed `é:x` are accepted by both functions, but KELVIN SIGN `\u212a:x` still gives
  `make_row=OK` and `append=DSE decision-row-invalid: source_ref.path=K:x`. The root cause is structural:
  `_validate_row(row)` (L:428) judges the caller's raw row, while the ledger stores its canonical projection. The rule
  that R7 prescribes cannot deliver R7's property on its own. A repair brief should say that the "finished row" is its
  canonical form.
- **Contrived extras (REPRODUCED).** Two hostile objects also pass `_validate_row` and are refused by `_check_line`: a `str`
  subclass with a lying `__ne__` as `checkpoint_digest`, and a `dict` subclass with a lying `__eq__` as a non-fixed-point
  `state`.
- **Tried, and not discriminators.** Accepted by both checks: non-NFC `producer`, `incumbent_answer`, `locator` and `path`
  (without a drive shape), U+2028 / U+2029 in values, and reversed key order. Refused by `_validate_row` itself, so they
  never reach `_check_line`: floats `-0.0`, `1e-7`, `1e16`, `1.0`, and 4300-digit and 4000-digit ints.
- **Contract mapping.** R7 says "so a row `make_row` returns is always one `append` accepts"; that is falsified. R3 and
  the mutant list allow N11 to be "EQUIVALENT with the reason" only "If no test can reach this second guard"; a test can
  reach it, so the report's N11 row (report line 106) is false required evidence. R4's drive prefix is `^[A-Za-z]:`, and
  the code over-refuses beyond it.
- **Canonical path:** yes. **Material effect:** the claimed output changes (R7's guarantee does not hold), and so does the
  evidence (a live guard is reported as dead, and the guard that prevents a poisoned ledger is unpinned). Ledger bytes at
  the PIN are intact, because the guard works. **Discriminator:** `test_f1_make_row_output_is_appendable` (RED at the PIN)
  and `test_f1_append_never_leaves_an_unreplayable_ledger` (GREEN at the PIN, RED under N11). **Ownership:** L + T.
- **Suggested fix.**
  1. In `make_row`, validate and return the canonical row: `row = json.loads(canonical(row))`, then `_validate_row(row)`
     (or `_check_line` on the line), so the returned row equals what `replay` yields.
  2. Make the drive rule ASCII-only, per R4.
  3. Add the two tests in §5.
  4. Correct the report's N11 row to "killed-by".

### F2 — FOLLOW-UP — `truncate-failed` leaves a torn line that blocks the ledger; not declared

- **Evidence (REPRODUCED).** A spy makes `os.ftruncate` raise `OSError(EIO)` during a 50-byte short write through the real
  `append`. The call raises `DSE decision-ledger-short-write: <P>/w2/d.jsonl:50/741 truncate-failed`, which is R1's exact
  reason. The file keeps a 50-byte tail with no `\n`. Then `replay after truncate-failed DSE
  decision-ledger-unparseable: <P>/w2/d.jsonl:3`, and every later append is refused the same way.
- **Chaining.** The `raise DecisionStateError(` at L:493 has no `from`: `__cause__: None | __context__: OSError(5, 'injected EIO')`. R1 says
  "chained from the OSError".
- **Contract mapping.** R1 defines the refusal, and it is met. The residual state (the ledger stays stuck until a person
  truncates it) is a hazard the declared limits do not name. **Material effect:** none beyond R1's own design; the refusal
  is loud and named.
- **Suggested fix.** Declare it in the docstring and name the manual repair (truncate to the last `\n`). Use
  `raise … from exc` after `except OSError:` (L:492).

### F3 — INFO — a second writer's acknowledged row is destroyed by the truncate (a declared limit)

- **Evidence (REPRODUCED, a spy standing in for a concurrent process).** "Writer B" appends a full, fsynced line through
  its own `O_APPEND` fd. It does so between A's `st = os.fstat(fd)` (L:476) and A's
  `written = os.write(fd, line_bytes)` (L:485). A's own write is short (50 bytes), and A then truncates back to
  `size_before = st.st_size` (L:483). Result:
  `writer B wrote 676/676 bytes and fsynced`; A raises `…:50/741`; `B's line present: False`; replay OK;
  `B's row present: False`. B's `append` would have returned its row_id, yet the row is gone.
- **Disposition.** The limit is declared (`One writer at a time`, L:17), so by the brief's rule the declared limit decides:
  INFO. R1's "it removes only this call's bytes, never existing ones" holds only under that limit. Optional: say so in the
  docstring. If writers are ever concurrent, add `fcntl.flock`.

### F4 — INFO — `fsync` failing after a successful truncate is reported as `truncate-failed`

- REPRODUCED: `os.ftruncate` runs for real, then `os.fsync(fd)` (L:491) raises. The call reports `…:50/741
  truncate-failed`, yet the file bytes equal the pre-write bytes and replay returns 2 rows. The detail names the wrong
  step. Suggested: split the `try`, or use the detail `fsync-failed`.

### F5 — BLOCKER — bare `TypeError` from row content through `make_row` and `append` (R2 / R7 not met)

- **Evidence (REPRODUCED, with origin frames).**
  ```
  append(row + {1:'x'})           TypeError: '<' not supported between instances of 'int' and 'str'   ledger.py:450 in append -> ledger.py:137 in _validate_row   # `_validate_row(row)` `sorted(row)`
  append(row + {None:'x'})        TypeError: '<' not supported between instances of 'NoneType' and 'str'
  append(row, source_ref+{1:'x'}) TypeError (same)
  make_row(source_ref + {1:'x'})  TypeError: '<' not supported …   ledger.py:428 in make_row -> ledger.py:155 in _validate_row   # `_validate_row(row)` `sorted(row["source_ref"])`
  make_row(question_id=[])        TypeError: unhashable type: 'list'   ledger.py:401 in make_row -> volatile.py:237 in schema_keys   # `schema_keys(question_id)` `question_id not in SCHEMAS`
  make_row(question_id={} / set()) TypeError: unhashable type
  ```
- **Where each comes from.** The closed-shape scan sorts the raw keys with `for key in sorted(row):` (L:137) and
  `for skey in sorted(row["source_ref"]):` (L:155); a non-str key mixed with str keys cannot be ordered. `make_row` calls
  `schema_keys(question_id)` (L:401) outside the R7 wrapper, whose `except Exception as exc:` sits at L:409, and J1-1
  runs `if question_id not in SCHEMAS:` (V:237) on an unhashable value. Nothing is written in any of these cases.
- **Contract mapping.**
  - R2: "`_validate_row` on a dict raises only `DecisionStateError`" and "For ANY row content … `make_row`, `append` and
    `replay` raise only `DecisionStateError`".
  - R7: "a NON-`DecisionStateError` exception from those calls [`schema_keys` and the J1-1 calls] becomes
    `decision-row-invalid: state=<ExceptionClassName>`".

  This is the exact class that J1-A6 was written to close (hostile-table row 14: `append(path, 1)` → `row=int`).
- **Canonical path:** yes. **Material effect:** integration behaviour. A caller's `except DecisionStateError` misses these
  exceptions, so the harvest crashes instead of refusing by name. **Discriminator:**
  `test_f5_non_str_keys_and_unhashable_question_id_refused_by_name`, RED at the PIN. **Ownership:** L.
- **Suggested fix.** Before sorting, refuse a non-str key by name: `decision-row-unknown-field: <repr>`, or sort with
  `key=str`. Move `schema_keys(question_id)` inside the R7 wrapper, or check `isinstance(question_id, str)` first.

### F6 — BLOCKER — a UNIX socket at the path escapes both functions as a bare `OSError` (R6 not met)

- **Evidence (REPRODUCED).**
  ```
  UNIX socket (bound, not listening)  replay BARE OSError: [Errno 6] No such device or address | append BARE OSError: [Errno 6] …
  UNIX socket (listening)             replay BARE OSError: [Errno 6] …                         | append BARE OSError: [Errno 6] …
  origin: ledger.py:521 in replay (`fd = os.open(`); append reaches it through ledger.py:453 (`existing = replay(path_str)`)
  ```
  `open(2)` on a socket fails with ENXIO before any `fstat`. Replay maps only `if exc.errno == errno.ELOOP:` (L:530);
  every other `except OSError as exc:` (L:527) is re-raised.
- **Contract mapping.** R6 says: "A FIFO, a directory, a socket or a device at the path is refused by both functions and
  never blocks". The refusal R6 defines is `decision-ledger-not-regular: <path>`. The frozen table shows the intent:
  row 10 replaced a directory's bare `IsADirectoryError` (also an OSError from open) with the named refusal. R2's OSError
  carve-out covers real filesystem failures, not file-type decisions.
- **Material effect:** exception class only. It never blocks and never writes. **Discriminator:** `test_f6_socket_refused`,
  RED at the PIN. **Ownership:** L.
- **Suggested fix.** Map `errno.ENXIO` from the open to `decision-ledger-not-regular`. `append` reaches the socket only
  through `existing = replay(path_str)` (L:453), so one mapping in replay closes both functions. F13 covers `append`'s own
  open.

### F7 — BLOCKER — the frozen test requirements are unmet and the lane report says "DISCREPANCIES: None"

- **Evidence (REPRODUCED).** The contract says "Every row of the table above is asserted with the EXACT refusal string",
  and R8 names exact-string assertions for four existing tests plus an fsync spy "on the ledger's fd …, after the write".
  At the PIN:
  - `test_invalid_fields` checks the reason plus `expected_field in str(exc.value)` (T:519).
  - `test_relanding_same_row_id` uses `match="decision-row-duplicate"` (T:156).
  - `test_state_not_canonical` uses `match="decision-row-state-not-canonical"` (T:426).
  - Table row 23 accepts any of three reasons via `"decision-row-invalid" in err_str` (T:1254), and from `append` via
    `"decision-row-invalid" in str(exc.value)` (T:1298).
  - The uppercase-hex tests check substrings, e.g. `"source_ref.source_digest=" in str(exc.value)` (T:1379) and
    `"row_id=" in str(exc.value)` (T:1393).
  - `def test_fsync_called_once_per_append` (T:1450) asserts only `len(fsync_calls) == 1` (T:1468).
  - Also weaker than exact: row 10 append, `exc.value.reason == "decision-ledger-not-regular"` (T:906);
    row 3, `f"/{expected_len}" in detail` (T:737); and the state flip and the row_id flip in
    `test_tamper_exact_strings` (`if not is_row_id:`, T:1355).
- **Discriminators.** Ten detail/order mutants SURVIVE the suite (`53 passed` each, §3): V9, V32, V33, V34, V40, V42, V43,
  V45, V46, V48. V48 moves the one `fsync` BEFORE the write, so `append` returns a row_id for an unsynced line; that breaks
  R1's core guarantee, and the R8 spy was meant to catch exactly this. Each is killed by the §5 F7 tests, which are GREEN at
  the PIN: the production strings and order are right (§2 INFO-4, §5).
- **Report defect.** The lane report states "13 existing tests unchanged except test_tamper_detected" and "DISCREPANCIES:
  None", beside three unmet R8 items. Per skill `contract-gate`, a "none" beside an unmet item is itself a report defect.
- **Material effect:** evidence. The gate cannot detect a regression that the contract says it pins. **Ownership:** T and the
  report. **Suggested fix:** tighten the named assertions as in §5 (test-only; no production change), then correct the
  DISCREPANCIES line.

### F8 — FOLLOW-UP — the declared limit on lone surrogates is false (benign direction)

- The docstring says "`make_row` refuses a lone surrogate anywhere in `raw_state`" (L:24) and "even in a field
  `normalize` would drop" (L:25). This text comes from the frozen brief's declared limits.
- REPRODUCED, real `make_row`: a surrogate past `b1.finding_sev.msg`'s 200-character limit, where
  `s = s[: f.limit]` (V:143) truncates it away, gives `OK row 9b92035b7494`. A surrogate in the dropped tail of `ap.violates_row.action_target`,
  where only `s.split()[0]` is kept (V:147), gives `OK row 8cb93b7b264b`. A surrogate that survives normalize is refused
  as `decision-row-invalid: state=UnicodeEncodeError`.
- The code is SAFER than declared: the stored state never carries the surrogate. This is a hollow claim in prose.
  **Suggested:** "…refuses a lone surrogate in any value that reaches the stored state; one that normalize truncates or
  drops is not refused".

### F9 — FOLLOW-UP — R5 detail for a bytes-returning PathLike is `bytes`, not the argument's type name

- REPRODUCED:
  - `os.DirEntry` from `os.scandir(b"…")` gives `decision-ledger-path-invalid: bytes`.
  - A PathLike returning bytes gives `…: bytes`.
- R5 says: "a `bytes` result → the detail is `type(ledger_path).__name__`". That would be `DirEntry` and the class name.
- The code hard-codes `"bytes"` after `if isinstance(resolved, bytes):` (L:293). The detail differs, but it sits within
  the right reason.

### F10 — INFO — a `__fspath__` that raises a non-TypeError escapes bare

- REPRODUCED: `PathLike raising ValueError` gives `BARE ValueError: v`, and `…RuntimeError` gives `BARE RuntimeError: r`,
  from both functions.
- Only `except TypeError:` (L:289) is mapped.
- R5 names "a type `os.fspath` rejects". A raising `__fspath__` is hostile misuse and is not contract-mapped.

### F11 — INFO — a `str` subclass that lies in `__str__`/`__format__` makes the detail name a path other than the one opened

- REPRODUCED: a corrupt ledger passed as such a subclass gives `decision-ledger-unparseable: /nonexistent/LIE:2`.
- `os.fspath` returns the subclass object itself. The f-string uses its `__format__`, while `os.open` uses the real bytes.
- This is hostile, and R5's "use that string everywhere" holds only for honest strings. Suggested: `str.__str__(resolved)`.

### F12 — FOLLOW-UP — contract behaviours that no test pins (production correct at the PIN; live differentials)

Each mutant below SURVIVES the PIN suite, and each is killed by a §5 FOLLOW-UP test. That test is GREEN at the PIN.

- **V7, a single `chunk = os.read(fd, 65536)` (L:544) with no loop.** At the PIN, a 70,691-byte ledger of 101 rows gives
  `replay OK list[101]`. Under V7, any ledger over 64 KiB (about 93 rows) reads as torn and is refused forever. This is the
  most practical gap.
- **V5b, AF-AP-132 in production code.** `data.split(b"\n")` (L:554) is replaced by a surrogate-safe `splitlines()` that
  keeps the trailing-element convention. A row carrying raw U+2028 / U+2029 / U+0085 in a value round-trips at the PIN;
  under V5b it would be split. The literal form V5a is killed, but only because it drops the trailing element (every file
  reads as torn), not because of AF-AP-132.
- **V2, no `os.fsync(fd)` after the truncate (L:491).** The PIN sequence is `['write', 'ftruncate(1439)', 'fsync']`.
- **V10.** The `truncate-failed` branch is never exercised.
- **V13.** "the first in sorted order" (R3): `zz_b`, `zz_a` gives `decision-row-unknown-field: zz_a`.
- **V14.** "in `_ROW_FIELDS` order" (R7): producer and answer both empty give `missing incumbent_answer`.
- **V17.** A 65-character lowercase-hex `source_digest` is refused at the PIN; `source_digest` is never recomputed, so only
  the shape check stands.
- **V27-V29.** Step (b)'s R2 wrappers (`except Exception as exc:`, L:191) through `append` of a hand-built row with a
  lone surrogate are named at the PIN (`state=`, `incumbent_answer=`, `producer=`, `source_ref.locator=UnicodeEncodeError`),
  but every surrogate test goes through `make_row`'s own pre-checks.

### F13 — INFO — append's own open is reachable only through a path swap; at the PIN it then raises bare OSErrors

- REPRODUCED: a replay wrapper swaps the path after the real replay has run, for each of these shapes:
  - FIFO → `BARE OSError: [Errno 6]`
  - symlink → `[Errno 40]`
  - directory → `BARE IsADirectoryError`
  - socket → `[Errno 6]`

  The symlink target is never written (`victim bytes after the symlink race: 0`).
- `append` has no ELOOP mapping. R6's "An open that fails with ELOOP … is `decision-ledger-not-regular`" is honoured only
  by replay.
- `if not stat.S_ISREG(st.st_mode):` in append (L:477) fires only for a FIFO with a reader or a device. So V3 (drop
  `O_NONBLOCK`), V36 (drop append's `S_ISREG`) and V37 (drop append's `O_NOFOLLOW`) are equivalent without a concurrent
  path change.
- Under a race, V3 would block and V37 would write through the symlink. This is covered by the "one writer" limit in
  spirit. The lane's N4 row ("S_ISREG check dropped → test_directory_refused") can only be replay's check.

### F14 — INFO — `make_row` returns the raw row; the ledger stores and `replay` returns NFC

- REPRODUCED: for the NFD path `cafe\u0301.md`, the returned path does not equal the replayed path, and the returned row
  does not equal the replayed row. The `row_id` is equal.
- `line = canonical(row) + "\n"` (L:461) NFC-folds. F1's fix (return the canonical row) closes this too.

### F15 — INFO — invisible format characters make distinct identities for visually identical paths

- REPRODUCED, all accepted by both functions: a leading U+FEFF, a trailing U+200B, U+200D, U+202E and the full-width
  solidus U+FF0F.
- These are POSIX-distinct names, so R4's "one spelling per path" is not violated. The residual risk is look-alike
  provenance.

### F16 — INFO — NFC folding merges POSIX-distinct NFC/NFD file names into one identity

- REPRODUCED: `NFC vs NFD same row_id: True`, and the NFC twin is refused as `decision-row-duplicate`.
- This follows from J1-1's canonical NFC rule (`unicodedata.normalize("NFC"`, C:28). At the identity level it is the
  intended "one spelling per path".

### F17 — INFO — `\r` / `\n` in a path get J1-1's refusal, with a raw CR/LF in the detail

- REPRODUCED: `make_row` gives `decision-canonical-newline: a\rb` (and `…a\nb`), not R4's `decision-row-invalid:
  source_ref.path=…`.
- Step (b)'s per-field canonical check runs before the path rules, and R2 lets a J1-1 canonical refusal propagate
  unchanged. The two rules overlap, so this is ambiguous.
- J1-1's detail carries the raw control character (`if "\n" in s or "\r" in s:`, C:29), which produces a multi-line error
  message. That is J1-1's.

### F18 — INFO — other filesystem OSErrors propagate (R2 carve-out)

- REPRODUCED: `append` into a missing directory gives `BARE FileNotFoundError` from its `os.open` with `O_CREAT`.
  `replay`/`append` on `file/` or `file/x` give `BARE NotADirectoryError`.
- Only `except FileNotFoundError:` (L:525) maps to `[]`. R2 allows filesystem OSErrors from open.

### F19 — FOLLOW-UP — item 10: the AF-AP-58 screen hit is not that class, but the watchdog kills the whole run

- **STATIC and REPRODUCED.** `old_handler = signal.signal(signal.SIGALRM, signal.SIG_DFL)` (T:837) installs the DEFAULT
  action, which terminates the process. It does not RAISE. The alarm is armed with `signal.alarm(10)` (T:838), one
  statement before the `try:` (T:839).
- Wherever the alarm fires (in that window, inside the try block, or before `signal.alarm(0)` (T:849)), the process dies, and
  the `finally` never runs. No catching scope exists that the alarm could escape. The window holds no blocking call and
  would need 10 s to elapse.
- The finally's order is right: `signal.alarm(0)` cancels first (T:849), then
  `signal.signal(signal.SIGALRM, old_handler)` restores (T:850). So the window does not matter, and AF-AP-58 (a RAISING
  handler installed before its `try`) does not apply.
- **The real cost (REPRODUCED).** Mutant V25 drops `O_NONBLOCK` from replay's open, and the FIFO test then blocks. The
  whole pytest process dies with `rc=-14` after 10.5 s. Stdout shows only `................` with no summary line, so every
  other result is lost; `pc_suite.sh wait` would print its "no passed count" RED. Under xdist, a worker dies instead.
- `signal.alarm(10)`'s return value (a pending outer alarm) is discarded. pytest-timeout is not installed here, so this
  is INFO.
- **Suggested:** run the blocking call in a subprocess with a timeout (the contract's first option), or install a RAISING
  handler with the arm inside the `try`.

### F20 — FOLLOW-UP — `except Exception:` (T:1292, the AP-70 screen hit) is dead today and a silent skip tomorrow

- It sits in `test_path_spellings_refused`'s hand-built-row loop, and no current bad path makes `canonical` refuse.
- If one ever did, that path's `append` check would be skipped without a sound.
- Suggested: narrow the handler and assert, or delete it. The §5 F7 test replaces the loop.

### F21 — INFO — touch 1 attacked: it keeps junk out of the repo; its junk check is never reached

- REPRODUCED: with touch 1 reverted (N5pre), a 723-byte `<DirEntry 'ledger.jsonl'>` lands in the cwd. With the touch
  (`monkeypatch.chdir(tmp_path)`, T:920 and T:989), the cwd stays empty and the file lands under `tmp_path`.
- Under N5, `pytest.raises` fails before `files = os.listdir(str(tmp_path))` (T:1005). So `assert files ==
  ["ledger.jsonl"]` (T:1006) is never the assertion that catches it.
- Touch 1's real value, keeping the repo root clean, holds.

### F22 — INFO — stale docstring

- `append`'s docstring still says "(g) write with `O_WRONLY|O_APPEND|O_CREAT`" (L:438). The open now also uses
  `O_NOFOLLOW`, `O_NONBLOCK` and `O_CLOEXEC`, plus an `fstat` check.

### F23 — INFO — lane-report citation drift

- The report's N11 reason puts the call at line 451 of L. The call `_validate_row(row)` is at L:450; the lint read
  it as NEAR.
- The report's T line count "634 -> 1460" predates touch 1's eight lines; the file is now 1468.

### F24 — INFO — cost shape

- `data += chunk` (L:547) copies quadratically for very large ledgers.
- `existing = replay(path_str)` (L:453) re-reads the whole file on every append, which the contract prescribes (item
  4(e)).
- Negligible at J1 scale.

### F25 — INFO — J1-1 touchpoint: wrong-typed `raw_state` values are coerced, not refused

- REPRODUCED: `msg` set to a list, a dict, `None` or `1.5` gives `make_row` → a row (J1-1's `normalize` `str()`s the
  value).
- This is J1-1's schema behaviour, not this boundary's.

### INFO-1..INFO-7 — what holds (REPRODUCED through the real functions)

- **INFO-1 (premise).** See §1; the N5 count difference is test selection.
- **INFO-2 (R1).**
  - Spy 50/741 onto a 2-row ledger: `decision-ledger-short-write: <P>/w2/a.jsonl:50/741`; the bytes equal the pre-write
    bytes; replay returns 2 rows; the next append succeeds (3 rows).
  - Spy writing 0 bytes: `…:0/741`, bytes unchanged.
  - Short-write call order: `write`, `ftruncate(1439)`, `fsync`.
  - Real 4 KiB tmpfs (root; mount, fill and umount in `finally`; 0 mounts left): after 4 x 699 + 650 bytes, a 701-byte row
    gives `decision-ledger-short-write: <V>/mnt/t1/ledger.jsonl:650/701` with the bytes equal to the pre-write bytes and
    replay returning 5 rows. The next append, a row sized to the free 650 bytes, succeeds (size 4096, replay 6 rows). One
    more append raises `OSError [Errno 28] No space left on device` with the bytes unchanged (declared).
  - ENOSPC with nothing written (spy) and an fsync error after a full write both raise `OSError`, as declared; in the
    fsync case the line stays in place (replay 3 rows).
  - A short write into an ABSENT ledger is refused and leaves a 0-byte file that replays as `[]`: content-equal, but its
    existence has changed.
- **INFO-3 (R2).** 44 hostile lines placed as line 2 behind a valid line 1 give 0 non-`DecisionStateError` outcomes.
  - `decision-ledger-unparseable: <W>/l.jsonl:2` for: a BOM before a valid row, CRLF, trailing spaces, `NaN`, `Infinity`,
    `-Infinity`, `1e999`, `NaN` inside a valid row, 5000-digit and 4301-digit ints, 100000-deep arrays and objects,
    600-deep arrays, NUL (inside a string, outside one, alone), `\xff` (in a string, alone), a lone `\r` (alone, mid-line,
    in a string), an escaped `\u2028` in a valid row, `\ud800` and raw ED A0 80, UTF-16-LE and UTF-32-BE objects (json's
    byte sniffing), a duplicate key, an NFD key, `[]`, `1`, a string, `null`, `true`, an empty line, and a `state` turned
    into a string.
  - Named row refusals on lines that parse and are canonical: a 4300-digit int → `decision-row-unknown-field: a`; raw
    U+2028 / U+2029 / U+0085 in a non-row object → same; `{}` → `decision-row-incomplete: missing calibration_state`; a
    digest flip → `decision-row-digest-mismatch: <carried row_id>`; `source_ref` as a list → `missing source_ref.kind`.
  - Positive controls: raw U+2028 / U+2029 / U+0085 in values → append OK, replay OK, and the raw character is present in
    the file.
- **INFO-4 (R4).** Every refused spelling in the brief's list and in the lane's 11 gives exactly `decision-row-invalid:
  source_ref.path=<value[:80]>` from `make_row` AND from `append`: `a//b`, `a/./b`, `a/b/`, `./a`, `a\b`, `a\u2028b`,
  `a\u2029b`, `a\x7fb`, `a\x85b`, `a\x1fb`, `a/..`, `../a`, `a:b`, an NBSP lead, an ideographic-space tail, and an
  81-character value cut to 80. Accepted, as the contract intends: `a/...`, `...`, `1:x`, a 4096-character path and a
  300-component path.
- **INFO-5 (R5).**
  - `str`, `pathlib.Path`, `PurePosixPath`, a `str` subclass and a `str` `DirEntry` resolve; a corrupt ledger reached
    through a `DirEntry` gives `…corrupt.jsonl:2`.
  - `None`, `int`, `float`, `bytes`, `bytearray`, `memoryview`, `''`, NUL, a PathLike returning an int, and a PathLike
    raising TypeError are refused by type name, `empty` or `nul`.
  - With the cwd pinned to a fresh dir, the only file created was the relative ledger that was actually named (`x.jsonl`).
- **INFO-6 (R6).** Each of these gives `decision-ledger-not-regular: <path>` from both functions in 0.00 s: a FIFO (with
  and without a reader), a symlink to the ledger, a symlink to `/dev/null`, a dangling symlink (the target is not
  created), a directory, a symlink to a directory, `/dev/zero`, `/dev/null`, `/dev/urandom`, and a regular file swapped
  for a symlink between two appends (the target is unchanged). A symlinked PARENT is followed, as declared.
- **INFO-7 (R7).** `question_id` as `5`, `None`, a tuple, `''`, an unknown id or bytes gives
  `decision-question-unknown: …`. `raw_state` as `None`, a list, a str or an int gives `decision-state-not-mapping`;
  missing and extra keys are named by J1-1. `source_digest` as `abc`, 64 x `A`, 64 x `g`, 63 or 65 chars, or with a
  leading space gives `decision-row-invalid: source_ref.source_digest=…`; an int gives `missing source_ref.source_digest`.
  A `source_ref` with an extra str key gives `decision-row-unknown-field: source_ref.zz`.

## 3. Mutant table

Harness: a fresh copy of the PIN per row, exact-text replacement with its count asserted, `py_compile`, then
`--collect-only`, then the two files, then the copy deleted.

| mutant (NEW unless noted) | compiles | collected | result (two-file set) | killed-by / disposition |
|---|---|---|---|---|
| M0 harness self-check | yes | 53 | 24 failed, 29 passed | proves the copy is imported |
| BASE | yes | 53 | 53 passed | — |
| N1, N6, N5, N5pre (lane's, premise re-run) | yes | 53 | see §1 | as the premise |
| N11 (lane's; append's pre-write check removed) | yes | 53 | **53 passed** | SURVIVED — not EQUIVALENT (F1); killed by `test_f1_append_never_leaves_an_unreplayable_ledger` |
| V1 truncate to `size_before + 1` | yes | 53 | 2 failed | test_short_write_real_tmpfs, test_short_write_spy |
| V2 the `os.fsync` after the truncate removed | yes | 53 | 53 passed | SURVIVED (F12); killed by `test_fu_short_write_fsyncs_after_truncate` |
| V3 `O_NONBLOCK` dropped from append's open | yes | 53 | 53 passed | race-only EQUIVALENT (F13): replay refuses a FIFO first; under a path swap the PIN raises ENXIO and V3 blocks |
| V4 `"\u2028"` removed from `_PATH_BAD_CHARS` | yes | 53 | 1 failed | test_path_spellings_refused |
| V5a replay split → `data.decode("utf-8").splitlines()` encoded back (literal) | yes | 53 | 12 failed | killed, but for another reason: the trailing `b""` is dropped, so every file reads as torn |
| V5b the same, surrogate-safe and keeping the trailing element (AF-AP-132 isolated) | yes | 53 | 53 passed | SURVIVED (F12); killed by `test_fu_line_separators_in_values_round_trip` |
| V6 `_resolve_ledger_path` accepts bytes (`os.fsdecode`) | yes | 53 | 1 failed | test_path_types_refused |
| V7 a single `os.read(fd, 65536)` | yes | 53 | 53 passed | SURVIVED (F12); killed by `test_fu_ledger_over_64k_replays` |
| V9 `_validate_path` details drop the value | yes | 53 | 53 passed | SURVIVED (F7); killed by `test_f7_row23_exact_from_make_row_and_append` |
| V10 the `truncate-failed` suffix dropped | yes | 53 | 53 passed | SURVIVED (F12); killed by `test_fu_truncate_failed_named` |
| V13 unknown-key scan unsorted | yes | 53 | 53 passed | SURVIVED (F12); killed by `test_fu_unknown_keys_first_in_sorted_order` |
| V14 `make_row` producer/answer check order swapped | yes | 53 | 53 passed | SURVIVED (F12); killed by `test_fu_make_row_checks_in_row_field_order` |
| V17 `_is_hex64` accepts `len >= 64` | yes | 53 | 53 passed | SURVIVED (F12); killed by `test_f7_invalid_fields_and_hex_exact` |
| V23 `size_before = 0` | yes | 53 | 2 failed | test_short_write_real_tmpfs, test_short_write_spy |
| V25 `O_NONBLOCK` dropped from replay's open | yes | 53 | **rc=-14 after 10.5 s, no summary** | killed only by SIGALRM killing the whole run (F19) |
| V27 / V28 / V29 step (b) R2 wrappers removed (state / top-level / source_ref) | yes | 53 | 53 passed each | SURVIVED (F12); killed by `test_fu_b_step_wrappers_on_append` |
| V32 / V33 / V34 `\x85` / `\u2029` / `\x7f` removed from the set | yes | 53 | 53 passed each | SURVIVED (F7); killed by `test_f7_row23_…[a\x85b]` / `[a\u2029b]` / `[a\x7fb]` |
| V36 append's own `S_ISREG` check removed | yes | 53 | 53 passed | race-only EQUIVALENT (F13) |
| V37 `O_NOFOLLOW` dropped from append's open | yes | 53 | 53 passed | race-only EQUIVALENT (F13): under a path swap V37 writes through the symlink; the PIN raises ELOOP |
| V40 state-not-canonical detail emptied | yes | 53 | 53 passed | SURVIVED (F7); killed by `test_f7_invalid_fields_and_hex_exact` |
| V42 / V43 / V45 / V46 `checkpoint_digest=` / `state_digest=` / `source_ref.source_digest=` / `row_id=` details drop the value | yes | 53 | 53 passed each | SURVIVED (F7); killed by `test_f7_invalid_fields_and_hex_exact` |
| V44 append's duplicate detail emptied | yes | 53 | 1 failed | test_direntry_duplicate_refused |
| V48 the one `fsync` moved BEFORE the write | yes | 53 | 53 passed | SURVIVED (F7); killed by `test_f7_fsync_on_the_ledger_fd_after_the_write` |

Tally over the 30 NEW mutants:
- 7 are killed by the PIN suite. That count includes V25, killed only by the process kill, and V5a, killed for an
  unrelated reason.
- 23 survive. Of these, 20 have a live discriminator, and each is killed by a §5 test (the run below). The other 3 are
  race-only equivalents: V3, V36, V37.

The lane's N11 survives and is not equivalent.

§5's module run over the survivors (`RED=1`, 30 tests). At the PIN it gives `4 failed, 26 passed`; the four are F1 x2, F5
and F6. Under each mutant, the extra failures are:

```
N11 → test_f1_append_never_leaves_an_unreplayable_ledger[e\u0301:x] [A\u030a:notes.md]
V2 → test_fu_short_write_fsyncs_after_truncate      V5b → test_fu_line_separators_in_values_round_trip
V7 → test_fu_ledger_over_64k_replays                V9 → 14 x test_f7_row23_exact_from_make_row_and_append
V10 → test_fu_truncate_failed_named                 V13 → test_fu_unknown_keys_first_in_sorted_order
V14 → test_fu_make_row_checks_in_row_field_order    V17, V40, V42, V43, V45, V46 → test_f7_invalid_fields_and_hex_exact
V27, V28, V29 → test_fu_b_step_wrappers_on_append   V32/V33/V34 → test_f7_row23_…[a\x85b]/[a\u2029b]/[a\x7fb]
V48 → test_f7_fsync_on_the_ledger_fd_after_the_write, test_fu_short_write_fsyncs_after_truncate
```

## 4. Gates — run by this lane (item 11), pasted verbatim (2026-09-23T05:54:46Z, the tree at 8a7c7f0's boundary bytes)

```
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/vj12r1g/bt   (root, run 1)
53 passed in 0.25s
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/vj12r1g/bt   (root, run 2)
53 passed in 0.23s
$ setpriv --reuid=65534 --regid=65534 --clear-groups env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/vj12r1nr/bt
52 passed, 1 skipped in 0.25s
$ /root/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/ledger.py tests/test_decisions_ledger.py
rc=0 (no output = clean)
$ AC 1: /root/venv-agent-factory/bin/python -c "import agent_factory.decisions as d, agent_factory.decisions.canonical, agent_factory.decisions.ledger; print('OK')"
OK
$ AC 2: python -m pytest tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/vj12r1a/bt
39 passed in 0.25s
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 38 files scanned, clean
$ grep -c vj12r1 /proc/mounts
0
```

The set is `2 files set=16a7b628685e`. The gates are green on the PIN bytes. The blockers are not gate failures: they are
contract behaviour and evidence that the gate does not pin.

## 5. Red tests (proposed for `tests/test_decisions_ledger.py`; run here as a scratch module; invented values only)

At the PIN, the F1 (appendable), F5 and F6 tests are RED, for the reasons below. The F1 guard test, the F7 tests and the
FU tests are GREEN at the PIN and RED under the mutants named in §3.

```
E  agent_factory.decisions.volatile.DecisionStateError: decision-row-invalid: source_ref.path=é:x        (F1, from append)
E  agent_factory.decisions.volatile.DecisionStateError: decision-row-invalid: source_ref.path=Å:notes.md (F1)
E  TypeError: '<' not supported between instances of 'int' and 'str'                                    (F5)
E  OSError: [Errno 6] No such device or address: 'sock.jsonl'                                            (F6)
4 failed, 26 deselected
```

```python
"""VERIFY-J1-2-R1 discriminators (scratch only; proposed for tests/test_decisions_ledger.py). Invented values only."""
from __future__ import annotations

import hashlib
import json
import os
import socket
from unittest.mock import patch

import pytest

from agent_factory.decisions.canonical import canonical
from agent_factory.decisions.volatile import DecisionStateError

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "decisions", "golden")


def _g(qid):
    with open(os.path.join(GOLDEN_DIR, qid + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def _sr(**kw):
    d = {"kind": "incident_log", "path": "docs/INCIDENT-LOG.md", "source_digest": "a" * 64,
         "locator": "AF-AP-76: mech-bar three-round cap"}
    d.update(kw)
    return d


def _row(qid="b1.finding_sev", **kw):
    from agent_factory.decisions.ledger import make_row
    g = _g(qid)
    a = dict(producer="decide-harvest/incident-log", question_id=qid, raw_state=g["state"],
             incumbent_answer="accepted", source_ref=_sr(), root=g.get("root"))
    a.update(kw)
    return make_row(**a)


def _rehash(row):
    sha = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()  # noqa: E731
    row = dict(row)
    row["state_digest"] = sha(canonical(row["state"]))
    ident = {"producer": row["producer"], "question_id": row["question_id"], "state_digest": row["state_digest"],
             "source_ref": {k: row["source_ref"][k] for k in ("kind", "locator", "path")}}
    row["row_id"] = sha(canonical(ident))
    row["row_digest"] = sha(canonical({k: v for k, v in row.items() if k != "row_digest"}))
    return row


# F1 — R7: a row make_row returns is always one append accepts (RED at 8a7c7f0: make_row OK, append refuses).
@pytest.mark.parametrize("path", ["e\u0301:x", "A\u030a:notes.md"])
def test_f1_make_row_output_is_appendable(tmp_path, path):
    from agent_factory.decisions.ledger import append
    try:
        row = _row(source_ref=_sr(path=path))
    except DecisionStateError:
        return  # make_row refused by name: R7 holds
    append(tmp_path / "l.jsonl", row)


# F1 — R3: append writes only a line replay accepts (GREEN at 8a7c7f0; RED under N11 — kills the lane's "EQUIVALENT").
@pytest.mark.parametrize("path", ["e\u0301:x", "A\u030a:notes.md", "\u212a:x"])
def test_f1_append_never_leaves_an_unreplayable_ledger(tmp_path, path):
    from agent_factory.decisions.ledger import append, replay
    ledger = tmp_path / "l.jsonl"
    append(ledger, _row())
    try:
        append(ledger, _rehash(dict(_row("b1.finding_kind"), source_ref=_sr(path=path))))
    except DecisionStateError:
        pass
    replay(ledger)


# F5 — R2/R7: no bare exception from content (RED at 8a7c7f0: TypeError).
def test_f5_non_str_keys_and_unhashable_question_id_refused_by_name(tmp_path):
    from agent_factory.decisions.ledger import append
    ledger = tmp_path / "l.jsonl"
    base = _row()
    sr_int = _sr()
    sr_int[1] = "x"
    cases = [
        lambda: append(ledger, {**base, 1: "x"}),
        lambda: append(ledger, {**base, None: "x"}),
        lambda: append(ledger, {**base, "source_ref": {**base["source_ref"], 1: "x"}}),
        lambda: _row(source_ref=sr_int),
        lambda: _row(question_id=[]),
        lambda: _row(question_id={}),
    ]
    for i, call in enumerate(cases):
        with pytest.raises(DecisionStateError):
            call()
    assert not ledger.exists()


# F6 — R6: a socket at the path is refused by both functions (RED at 8a7c7f0: OSError ENXIO).
def test_f6_socket_refused(tmp_path, monkeypatch):
    from agent_factory.decisions.ledger import append, replay
    monkeypatch.chdir(tmp_path)  # a relative bind keeps the AF_UNIX path short
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.bind("sock.jsonl")
        for call in (lambda: replay("sock.jsonl"), lambda: append("sock.jsonl", _row())):
            with pytest.raises(DecisionStateError) as exc:
                call()
            assert str(exc.value) == "decision-ledger-not-regular: sock.jsonl"
    finally:
        s.close()


# F7 — the frozen EXACT-string requirement (GREEN at 8a7c7f0; each RED under the named detail mutant).
@pytest.mark.parametrize("path", ["./docs/INCIDENT-LOG.md", "docs//INCIDENT-LOG.md", "docs/./INCIDENT-LOG.md",
                                  "docs/INCIDENT-LOG.md/", "~/x", " docs/x ", ".", "C:/x", "a\tb", "a\u2028b", "a\x00b",
                                  "a\x7fb", "a\x85b", "a\u2029b"])
def test_f7_row23_exact_from_make_row_and_append(tmp_path, path):  # kills V9, V32, V33, V34
    from agent_factory.decisions.ledger import append
    want = f"decision-row-invalid: source_ref.path={path[:80]}"
    with pytest.raises(DecisionStateError) as exc:
        _row(source_ref=_sr(path=path))
    assert str(exc.value) == want
    with pytest.raises(DecisionStateError) as exc:
        append(tmp_path / "l.jsonl", _rehash(dict(_row(), source_ref=_sr(path=path))))
    assert str(exc.value) == want


def test_f7_invalid_fields_and_hex_exact(tmp_path):  # kills V42, V43, V45, V46, V40, V17
    from agent_factory.decisions.ledger import append
    ledger = tmp_path / "l.jsonl"
    base = _row()
    for mut, want in [
        (dict(base, checkpoint_digest="abc123"), "decision-row-invalid: checkpoint_digest=abc123"),
        (dict(base, state_digest="zzzz" + "0" * 60), "decision-row-invalid: state_digest=zzzz" + "0" * 60),
        (dict(base, state_digest="B" * 64), "decision-row-invalid: state_digest=" + "B" * 64),
        (dict(base, source_ref=_sr(source_digest="A" * 64)), "decision-row-invalid: source_ref.source_digest=" + "A" * 64),
        (_rehash(dict(base, source_ref=_sr(source_digest="a" * 65))), "decision-row-invalid: source_ref.source_digest=" + "a" * 65),
        (dict(base, row_id="C" * 64), "decision-row-invalid: row_id=" + "C" * 64),
    ]:
        with pytest.raises(DecisionStateError) as exc:
            append(ledger, mut)
        assert str(exc.value) == want
    bad = _rehash(dict(base, state=dict(base["state"], msg="a  double  space")))
    with pytest.raises(DecisionStateError) as exc:
        append(ledger, bad)
    assert str(exc.value) == f"decision-row-state-not-canonical: {bad['row_id']}"


def test_f7_fsync_on_the_ledger_fd_after_the_write(tmp_path):  # kills V48 (and M12)
    from agent_factory.decisions import ledger as L
    seq = []
    rw, rf = os.write, os.fsync
    with patch.object(L.os, "write", side_effect=lambda fd, d: (seq.append(("write", fd)), rw(fd, d))[1]), \
            patch.object(L.os, "fsync", side_effect=lambda fd: (seq.append(("fsync", fd)), rf(fd))[1]):
        L.append(tmp_path / "l.jsonl", _row())
    assert [k for k, _ in seq] == ["write", "fsync"] and seq[0][1] == seq[1][1]


# FOLLOW-UP discriminators (GREEN at 8a7c7f0; each RED under the named mutant)
def test_fu_ledger_over_64k_replays(tmp_path):  # kills V7
    from agent_factory.decisions.ledger import append, replay
    ledger = tmp_path / "big.jsonl"
    n = 0
    while not ledger.exists() or ledger.stat().st_size <= 70000:
        append(ledger, _row(producer=f"p/{n}"))
        n += 1
    assert len(replay(ledger)) == n


def test_fu_line_separators_in_values_round_trip(tmp_path):  # kills V5b (AF-AP-132 in production code)
    from agent_factory.decisions.ledger import append, replay
    ledger = tmp_path / "l.jsonl"
    for i, ch in enumerate(("\u2028", "\u2029", "\x85")):
        append(ledger, _row(incumbent_answer=f"a{ch}b", source_ref=_sr(locator=f"loc{i}{ch}")))
    assert len(replay(ledger)) == 3


def test_fu_short_write_fsyncs_after_truncate(tmp_path):  # kills V2
    from agent_factory.decisions import ledger as L
    p = tmp_path / "l.jsonl"
    L.append(p, _row())
    seq = []
    rw, rt, rf = os.write, os.ftruncate, os.fsync
    with patch.object(L.os, "write", side_effect=lambda fd, d: (seq.append("write"), rw(fd, d[:50]))[1]), \
            patch.object(L.os, "ftruncate", side_effect=lambda fd, n: (seq.append("ftruncate"), rt(fd, n))[1]), \
            patch.object(L.os, "fsync", side_effect=lambda fd: (seq.append("fsync"), rf(fd))[1]):
        with pytest.raises(DecisionStateError):
            L.append(p, _row("b1.finding_kind"))
    assert seq == ["write", "ftruncate", "fsync"]


def test_fu_truncate_failed_named(tmp_path):  # kills V10
    import errno
    from agent_factory.decisions import ledger as L
    p = tmp_path / "l.jsonl"
    L.append(p, _row())
    line = (canonical(_row("b1.finding_kind")) + "\n").encode()
    with patch.object(L.os, "write", side_effect=lambda fd, d: 50), \
            patch.object(L.os, "ftruncate", side_effect=OSError(errno.EIO, "injected")):
        with pytest.raises(DecisionStateError) as exc:
            L.append(p, _row("b1.finding_kind"))
    assert str(exc.value) == f"decision-ledger-short-write: {p}:50/{len(line)} truncate-failed"


def test_fu_unknown_keys_first_in_sorted_order(tmp_path):  # kills V13
    from agent_factory.decisions.ledger import append
    r = dict(_row())
    r["zz_b"] = "1"
    r["zz_a"] = "1"
    with pytest.raises(DecisionStateError) as exc:
        append(tmp_path / "l.jsonl", r)
    assert str(exc.value) == "decision-row-unknown-field: zz_a"


def test_fu_make_row_checks_in_row_field_order():  # kills V14
    with pytest.raises(DecisionStateError) as exc:
        _row(producer="", incumbent_answer="")
    assert str(exc.value) == "decision-row-incomplete: missing incumbent_answer"


def test_fu_b_step_wrappers_on_append(tmp_path):  # kills V27, V28, V29
    from agent_factory.decisions.ledger import append
    base = _row()
    for mut, want in [
        (dict(base, state=dict(base["state"], msg="x\ud800y")), "decision-row-invalid: state=UnicodeEncodeError"),
        (dict(base, incumbent_answer="x\ud800y"), "decision-row-invalid: incumbent_answer=UnicodeEncodeError"),
        (dict(base, source_ref=_sr(locator="x\ud800y")), "decision-row-invalid: source_ref.locator=UnicodeEncodeError"),
    ]:
        with pytest.raises(DecisionStateError) as exc:
            append(tmp_path / "l.jsonl", mut)
        assert str(exc.value) == want
```

## 6. Reproduced vs reviewed statically vs skipped

- **Reproduced.** Items 1-9 and 11 ran through the real functions at the PIN bytes: the premise, R1 (spies and a real
  4 KiB tmpfs), R2 (44 lines), R3/N11, R4 (46 spellings), R5 (23 argument shapes), R6 (16 file shapes), R7, 30 new mutants
  plus N11, the red module under 21 mutants, and every gate. Every origin frame in F1, F5 and F6 was read from a
  traceback.
- **Reproduced through a surrogate mechanism (said so).** F3's concurrent writer and F13's path swaps use in-process spies
  that make the kernel calls deterministically, not a second process. Both are inside declared limits.
- **Static.** Item 10's window argument, reinforced by V25's run. The docstring review (F8, F22). The cost shape (F24).
- **Skipped, and why.** The lane's M11-M20 and N-mutants other than N1, N5, N6 and N11 were not re-run (the brief allows
  only NEW mutants; N11 was item 4's question). There was no PC bridge (forbidden). No power-loss test for fsync
  durability was run (not possible here). The code-intel quartet and a `lane_context.sh` pack were not used: the boundary
  is three files, read whole, and the one reachability statement rests on a literal grep, named in §2.
- **Hygiene.** The tree was touched only by this report. All git reads used `GIT_OPTIONAL_LOCKS=0`. No
  stash/checkout/restore/add/reset/commit was run. No S0-05 file was touched. The tmpfs was unmounted (0 vj12r1 mounts),
  and the scratch tree `$SP/vj12r1` was removed at the end (§7).
- **Registry candidate for the coordinator.** This lane writes no registry row. The candidate class is: "a validator judges
  the caller's raw object while the store keeps its canonical projection" (F1). The sibling sweep inside
  `agent_factory.decisions` found only the path rules sensitive to NFC; the literals, kinds and hex checks are NFC-stable
  (no canonical mapping yields lowercase ASCII).

## 7. Gate recommendation

`NOT-READY` — F1 (R7's make_row→append guarantee falsified; the lane's N11 "EQUIVALENT" is false and the guard it names is
live, load-bearing and unpinned), F5 (R2/R7: bare `TypeError` from content via `sorted(row` at L:137 and L:155 and the unwrapped
`schema_keys(question_id)` at L:401), F6 (R6: a socket escapes both functions as a bare `OSError` from the `fd = os.open(` at L:521),
F7 (the frozen exact-string and fsync-after-the-write test requirements unmet, ten detail/order mutants survive, and the lane
report says "DISCREPANCIES: None"). Every item was reproduced in this session. Each has a §5 discriminator. All fixes stay
inside L + T and are small. None changes ledger bytes at the PIN. F1's repair brief should define the "finished row" as its
canonical form, because the rule R7 prescribes (`_validate_row(row)` on the raw row) cannot meet R7's property on its own
(KELVIN SIGN, §2 F1).
