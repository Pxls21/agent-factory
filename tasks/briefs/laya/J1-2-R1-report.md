# J1-2-R1 report

PIN: 6bf2522 (decisions boundary byte-identical at ea9538a)

## PREMISE re-measured

- HEAD = ea9538a, origin = ea9538a (decisions boundary byte-identical to PIN 6bf2522 and J1-2 landing 9d11c25: `git diff --stat 9d11c25 ea9538a -- src/agent_factory/decisions tests/test_decisions_ledger.py tests/test_decisions_canonical.py tests/fixtures/decisions` = empty)
- File digests match the brief exactly:
  - `803197133f2e2f6e` 333 `src/agent_factory/decisions/ledger.py`
  - `bc9cb1d03fdb77a4` 77 `src/agent_factory/decisions/canonical.py`
  - `b48899c883c7231f` 295 `src/agent_factory/decisions/volatile.py`
  - `2aec3875f71213e4` 21 `src/agent_factory/decisions/__init__.py`
  - `787f08043ca086a1` 634 `tests/test_decisions_ledger.py`
  - `48fdf09e8038a146` 340 `tests/test_decisions_canonical.py`
- Baseline: 27 passed in 0.13s (root), 27 passed in 0.13s (nobody)
- No later repair commits on ledger.py or test_decisions_ledger.py
- PREMISE VALID

## What changed

**L: `src/agent_factory/decisions/ledger.py`** (333 -> 617 lines)

- **R1** short write refused: inside `def append` (L:433), after `written = os.write(fd, line_bytes)` (L:485), the `if written < expected` check (L:487) truncates back with `os.ftruncate` and raises `decision-ledger-short-write`.
- **R2** no bare exception from content: `def _validate_row` (L:128) checks `not isinstance(row, dict)` (L:131). Step (b) per-field `canonical` + `.encode("utf-8")` (L:188, L:198). `def replay` (L:508) broadens `json.loads` except (L:575), adds `not isinstance(parsed, dict)` (L:582), broadens `canonical` except to `except (ValueError, RecursionError, TypeError, UnicodeError)` (L:596). Row-level `_validate_row(parsed)` (L:605) keeps its own reason.
- **R3** closed row shape: `def _validate_row` (L:128) refuses `key not in _ROW_FIELDS` (L:138), `skey not in _SOURCE_REF_FIELDS` (L:155). `def _check_line` (L:308) is the factored per-line check. `def append` runs `_check_line` (L:465) before writing.
- **R4** one spelling per path: `def _validate_path` (L:106) checks `posixpath.normpath(path) != path` (L:108), `path == "."` (L:111), `_PATH_BAD_CHARS` (L:114), `path.strip()` (L:117), `path.startswith("~")` (L:120), drive prefix `path[1] == ":"` (L:123). Called at `_validate_path(path)` (L:240).
- **R5** `ledger_path` resolved once: `def _resolve_ledger_path` (L:285) calls `os.fspath(ledger_path)` (L:288), refuses `isinstance(resolved, bytes)` (L:293), empty `if not resolved` (L:297), NUL `"\x00" in resolved` (L:301). Called at `path_str = _resolve_ledger_path(ledger_path)` in `append` (L:447) and `replay` (L:517).
- **R6** regular file on fd: `def append` opens with `os.O_NOFOLLOW` (L:470), checks `not stat.S_ISREG(st.st_mode)` (L:477). `def replay` opens with `os.O_NOFOLLOW` (L:523), catches `exc.errno == errno.ELOOP` (L:530), checks `S_ISREG` (L:538), reads via `os.read(fd, 65536)` (L:543).
- **R7** `def make_row` (L:336) checks `not isinstance(incumbent_answer, str)` (L:356), `not isinstance(producer, str)` (L:360), source_ref sub-fields with `canonical(val).encode("utf-8")` (L:380). Non-DSE from `redact(normalize(question_id, raw_state, root))` wrapped (L:405). Final `_validate_row(row)` (L:428).
- **R8** (T:296-327, T:1331-1468): `def test_tamper_detected` (T:296) tightened to `== "decision-row-digest-mismatch"` (T:323). New: `def test_tamper_exact_strings` T:1331, `def test_uppercase_hex_refused` T:1366, `def test_value_80_and_81_chars` T:1396, `def test_duplicate_in_file` T:1421, `def test_unterminated_last_line` T:1435, `def test_fsync_called_once_per_append` T:1450.
- **Docstring** declared limits (L:14): four new limits added.

**T: `tests/test_decisions_ledger.py`** (634 -> 1460 lines)

26 new tests added. 13 existing tests unchanged except `test_tamper_detected` assertion tightened (R8 amendment).

## Hostile table results

| # | input | observed |
|---|---|---|
| 1 | short write 50/693 on 2-row ledger | `decision-ledger-short-write: <path>:50/693`; bytes restored; replay OK; next append OK |
| 2 | short write 0 bytes | `decision-ledger-short-write: <path>:0/<len>`; bytes unchanged |
| 3 | 4 KiB tmpfs, append until partly fits | `decision-ledger-short-write: <path>:<n>/<len>`; bytes unchanged; replay OK |
| 4 | tmpfs filled to byte, one more | `OSError` ENOSPC (declared limit) |
| 5 | replay scalar 1 / "calibration_state" / [] | `decision-ledger-unparseable: <path>:2` each |
| 6 | replay lone surrogate escape / raw bytes | `decision-ledger-unparseable: <path>:2` |
| 7 | 600-deep / 100000-deep nesting | `decision-ledger-unparseable: <path>:2` |
| 8 | FIFO replay/append | `decision-ledger-not-regular: <path>`, returns at once |
| 9 | symlink / dangling symlink | `decision-ledger-not-regular: <path>`; target not created |
| 10 | directory at path | `decision-ledger-not-regular: <path>` |
| 11 | replay(DirEntry) of corrupt ledger | `decision-ledger-unparseable: <entry.path>:2` |
| 12 | None/1/bytes/empty/NUL path | `decision-ledger-path-invalid: NoneType/int/bytes/empty/nul` |
| 13 | append(DirEntry) duplicate | `decision-row-duplicate: <row_id>`; no junk file |
| 14 | append(path, 1) / append(path, None) | `decision-row-invalid: row=int` / `row=NoneType` |
| 15 | extra top-level key zz_extra | `decision-row-unknown-field: zz_extra` |
| 16 | extra source_ref key | `decision-row-unknown-field: source_ref.zz_extra` |
| 17 | make_row missing source_ref.kind/path/locator | `decision-row-incomplete: missing source_ref.<sub>` |
| 18 | make_row(source_ref=None) | `decision-row-incomplete: missing source_ref.kind` |
| 19 | producer="" / None | `decision-row-incomplete: missing producer` |
| 20 | incumbent_answer=5 / "" | `decision-row-incomplete: missing incumbent_answer` |
| 21 | kind="bogus" / path="/etc/passwd" | `decision-row-invalid: source_ref.kind=bogus` / `source_ref.path=/etc/passwd` |
| 22 | lone surrogate in locator/incumbent/state | `decision-row-invalid: source_ref.locator=UnicodeEncodeError` / `incumbent_answer=UnicodeEncodeError` / `state=UnicodeEncodeError` |
| 23 | bad path spellings (11 values) | `decision-row-invalid: source_ref.path=<value[:80]>` from make_row AND append |
| 24 | good paths docs/INCIDENT-LOG.md, a/..b, %2e%2e/a, a/b.c | still accepted |
| 25 | J1-1 refusals through make_row | unchanged |

## RED then GREEN

RED (PIN code, excluding FIFO which blocks forever = correct RED behavior):
```
18 failed, 20 passed, 1 deselected in 0.55s
```
All 18 failures are the new tests, failing for the reasons from the hostile table's PIN column (bare TypeError, UnicodeEncodeError, KeyError, DID NOT RAISE).

GREEN (repaired code):
```
53 passed in 0.27s   (root, run 1)
53 passed in 0.27s   (root, run 2)
52 passed, 1 skipped in 0.29s   (nobody; tmpfs test SKIPS: "not root, cannot mount tmpfs")
```

## Mutant table

| mutant | compiles | collected | result | killed-by |
|---|---|---|---|---|
| M0 (self-check) | yes | 52 | 31 failed | 31 tests (harness verified) |
| BASE | yes | 52 | 52 passed | - |
| M11 `_is_hex64` accepts ABCDEF | yes | 52 | 1 failed | test_uppercase_hex_refused |
| M12 `os.fsync(fd)` -> pass | yes | 52 | 1 failed | test_fsync_called_once_per_append |
| M13 `)[:80]` -> `)[:79]` | yes | 52 | 1 failed | test_value_80_and_81_chars |
| M14 duplicate check -> if False | yes | 52 | 1 failed | test_duplicate_in_file |
| M15b final-newline check -> if False | yes | 52 | 1 failed | test_unterminated_last_line |
| M18 mismatch detail = recomputed id | yes | 52 | 1 failed | test_tamper_exact_strings |
| M19 re-raise row refusals as unparseable | yes | 52 | 2 failed | test_tamper_detected, test_tamper_exact_strings |
| M20 calibration_state detail truncated | yes | 52 | 1 failed | test_value_80_and_81_chars |
| N1 written-count check removed | yes | 52 | 2 failed | test_short_write_spy, test_short_write_real_tmpfs |
| N2 truncate removed | yes | 52 | 2 failed | test_short_write_spy, test_short_write_real_tmpfs |
| N3 O_NOFOLLOW dropped from replay | yes | 52 | 1 failed | test_symlink_refused |
| N4 S_ISREG check dropped | yes | 52 | 1 failed | test_directory_refused |
| N5 os.fspath -> str | yes | 52 | 3 failed | test_path_types_refused, test_direntry_corrupt_ledger, test_direntry_duplicate_refused |
| N6 closed-shape check removed | yes | 52 | 1 failed | test_extra_top_level_key_refused |
| N7 normpath rule removed | yes | 52 | 1 failed | test_path_spellings_refused |
| N8 make_row's _validate_row removed | yes | 52 | 2 failed | test_make_row_invalid_kind_and_path, test_path_spellings_refused |
| N9 replay except narrowed back | yes | 52 | 1 failed | test_replay_content_exceptions |
| N10 replay object check removed | yes | 52 | 1 failed | test_replay_content_exceptions |
| N11 append pre-write line check removed | yes | 52 | 52 passed | **EQUIVALENT**: R3's closed-shape check in `_validate_row` runs before the write via `_validate_row(row)` at L:451; the pre-write `_check_line` on the serialized bytes is structurally unreachable for any row that passes `_validate_row` — every refusal it could produce is already produced by the earlier call |

Summary: 18 killed / 0 survived / 1 EQUIVALENT (N11, with reason)

## Gates

```
$ rm -rf /tmp/j12r1/bt && mkdir -p /tmp/j12r1/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/j12r1/bt
53 passed in 0.27s   (root, run 1)
53 passed in 0.27s   (root, run 2)

$ rm -rf /tmp/j12r1nr && mkdir -p /tmp/j12r1nr && chmod 1777 /tmp/j12r1nr && setpriv --reuid=65534 --regid=65534 --clear-groups env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/j12r1nr/bt
52 passed, 1 skipped in 0.29s   (nobody; tmpfs test skips: not root)

$ /root/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/ledger.py tests/test_decisions_ledger.py
(clean)

$ /root/venv-agent-factory/bin/python -c "import agent_factory.decisions as d, agent_factory.decisions.canonical, agent_factory.decisions.ledger; print('OK')"
OK

$ python -m pytest tests/test_decisions_ledger.py -q --basetemp=/tmp/j12r1/bt
39 passed in 0.22s

$ python3 scripts/ap_screen.py src/agent_factory/decisions/ledger.py
AP-32: 1 (sha256 encode — pre-existing, unchanged)

$ python3 scripts/ap_screen.py --tests tests/test_decisions_ledger.py
AP-70: 1 (bare except in test_path_spellings_refused catch-all for canonical recomputation — test-only, no production path)

$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 38 files scanned, clean

$ grep -c j12r1 /proc/mounts
0
```

## Declared limits (from docstring L:13-25)

1. An unkeyed digest catches accidental or naive mutation, not a forger who recomputes every digest.
2. Deleting a whole row is not detected (no hash chain in J1).
3. One writer at a time.
4. `O_NOFOLLOW` covers the final path component only (a symlinked parent directory is followed).
5. `ENOSPC` with nothing written raises `OSError` and leaves the file unchanged.
6. An `os.fsync` error after a full write raises `OSError` with the line in place (a later `replay` shows whether it landed).
7. `make_row` refuses a lone surrogate anywhere in `raw_state`, even in a field `normalize` would drop.

## DISCREPANCIES

None.

## TOUCHPOINTS

- J1-1's `canonical()` does not refuse a lone surrogate by name — it produces a str that `.encode("utf-8")` rejects. The `UnicodeEncodeError` is caught by R2's per-field encode check in `_validate_row` and by R7's make_row pre-checks. That is J1-1-R1's, not this repair's.
- The AP-70 hit in the test file is a bare `except Exception` in `test_path_spellings_refused`'s canonical recomputation block — test-only, no production path, harmless.

## NOT-done

- F17 (normalize idempotence) is J1-1-R1's boundary.
- Issue #30 items beyond R1-R8 are not touched.
- The FIFO test uses `signal.SIGALRM` as a 10 s watchdog. If the platform does not support SIGALRM, the test would block. In practice all Linux targets support it.

## COORDINATOR TOUCH at landing (2026-09-23 05:2xZ)

1. **The stray repo-root file.** `<DirEntry 'ledger.jsonl'>` (723 bytes, one ledger row, written 05:04:37Z) came
   from the N5 mutant run: `str(DirEntry)` resolves against the process working directory, the repo root, while the
   junk check in `test_direntry_duplicate_refused` lists `tmp_path` and so could never see it. Reproduced on a
   scratch copy under N5: the 723-byte file appeared in the scratch working directory. Fix: `monkeypatch.chdir(tmp_path)`
   at the top of both DirEntry tests. Under N5 after the fix, both tests still fail, the working directory stays
   empty, and the junk lands in `tmp_path` (`test_direntry_duplicate_refuse0/<DirEntry 'ledger.jsonl'> 723`), where
   the check sees it. The stray file was removed.
2. **Two invisible separators.** `ledger.py` held a literal U+2028 and U+2029 inside `_PATH_BAD_CHARS`; they are
   now written as the escapes `\u2028` and `\u2029`. The set is unchanged: 36 members, sha256 of the sorted repr
   `9323478b39b9d6e1` before and after.
3. **Citations.** Those two characters made `scripts/report_lint.py` (`str.splitlines()`) read every line after
   them two lines late. That caused most of this report's 28 MISS; git and grep agreed with the lane. The lint now
   numbers lines on newlines only (AF-AP-132, its own commit). The `T:` refs moved with touch 1's eight inserted
   lines (+4 after the first test, +8 after the second), and six remaining refs were corrected from `grep -n`.
4. **Gates on the landed bytes, run by the coordinator:** root `53 passed in 0.23s` and `53 passed in 0.24s`;
   uid 65534 `52 passed, 1 skipped in 0.25s` (the tmpfs test needs root); pyflakes clean; the screen's one hit is
   the unchanged AP-32 line. Mutants N1 (2 failed: test_short_write_spy, test_short_write_real_tmpfs) and N6
   (1 failed: test_extra_top_level_key_refused) re-run on a scratch copy: killed by the named tests.
