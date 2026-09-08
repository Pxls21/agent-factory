# Lane A5j report -- S0-01 checker round 12

PIN: `ac3117f` (HEAD at dispatch); landing = the coordinator's checkpoint, made after this report.

## FILE IDENTITY (FINAL bytes)

| file | sha256 (first 16) | lines |
|---|---|---|
| `proofs/S0-01/check_acp_conformance.py` | `56e86e712e3a54bb` | 1857 |
| `tests/test_s0_01_check_acp_conformance.py` | `78adb3a4f7f4f447` | 4922 |
| `proofs/S0-01/negative_contract.py` | `3af15c9c8687328a` | 217 |

## PREMISE

| item | value |
|---|---|
| PIN | `ac3117f9199092bea0d5c5395714fdac8fc94966` |
| HEAD at dispatch | same |
| load at start | `1.08 0.71 0.97` |
| corpus | `realleg_sync: /root/s0-01-realleg/golden intact (142 files)` rc 0 |
| python | 3.11.15, pytest 9.1.1 |

## check_initialize.py scan

Two `.exists()` / `.is_dir()` calls found:
- `check_initialize.py:129` `tl_path.exists()` -- false branch returns 2 (fail-closed deferral).
- `check_initialize.py:194` `path.is_dir()` routing -- not a skip gate.

Both FAIL on absence. No AF-AP-40 hit. No edit needed.

---

## DONE

| # | finding | change | file:line | red-before / evidence |
|---|---|---|---|---|
| 1 | F3/F4/F5 | `_KNOWN_XFAIL_REASONS` frozenset T:2860; `_is_known_stale` T:2867; `assert not ok` T:2878; tail test T:4578 | T:2860, T:2867, T:2878, T:4578 | CONTROL: mutants 1+2 killed |
| 2 | F8: S_ISREG at acp_probe | `import stat` N:21; guard N:181; FIFO test T:4620; dir test T:4638 | N:21, N:181, T:4620, T:4638 | CONTROL: mutant 3 killed |
| 2b | F8 CLASS: read scan | `test_ck11_every_read` T:4705 | T:4705 | CONTROL: mutant 9 killed |
| 3 | F15: schema AP-40 | `_require_file` C:1707; absent test T:4656; class scan T:4662 | C:1707, T:4656, T:4662 | CONTROL: mutant 4 killed |
| 4 | F1: env tracking | `test_ck11_real_leg_dir` T:2644 | T:2644 | CONTROL: mutant 5 killed |
| 5 | F16/F18: venue | `_VENUE` T:2579; domain test T:2657; domain check T:2668; `_real_leg` T:2598 | T:2579, T:2598, T:2657, T:2668 | CONTROL: mutant 6 killed at T:2660 |
| 6 | F19: sidecar sha | sidecar loop T:2682-2690 | T:2682, T:2687 | CONTROL: mutant 7 killed |
| 7 | F2/F9/F10: handler | alarm test T:4843; restore C:1638; alarm(0) C:1639; NOTE C:2 | C:2, C:1638, C:1639, T:4833, T:4843 | CONTROL: mutant 8 killed |
| 8 | F11: dead-branch 6/6 | C:957 fixed; C:1568 fixed; C:1597 fixed; test T:4880 | C:957, C:1568, C:1597, T:4880 | genuine-red: PIN was 4/6 |
| 9a | F6: scan inlined | `_scan_direct_writes` call T:3464 | T:3464 | CONTROL |
| 9b | F7+17.1: write patterns | `_WRITE_ATTRS` T:3351; `_OS_WRITERS` T:3355; `gzip.open` T:3445; limits T:3366 | T:3351, T:3355, T:3366, T:3445 | CONTROL |
| 9c | F14: dead write_text | `unlink(missing_ok=True)` T:4601; `_EXEMPT_FNS` T:3356-3361 | T:3356-3361, T:4601 | CONTROL |
| 9d | F20: startup denominator | `_uncovered` T:4535 | T:4535 | CONTROL |
| 10 | 17 skip guards | `_real_leg()` T:2598-2606 | T:2598-2606 | mechanical |
| S-6.1 | venue closed | R2b/R2c FAIL at T:2660 | T:2660, T:2668 | confirmed |
| S-8.1 | bad_json prefix | `JSONDecodeError:` T:2038 | T:2038 | was: any prefix |
| S-5.1/5.2 | containment exact | `result ==` T:2739, T:2790 | T:2739, T:2790 | was: `in result` |
| S-1.4/16.2 | redundant guards | bare `p.unlink()` at 4 sites | T:668, T:721, T:733, T:741 | was: `if exists: unlink` |
| S-1.10 | bundle unguarded | bare `shutil.copy2` T:434 | T:434 | was: `if exists: copy` |
| 4-timeout | elapsed bound | `elapsed < 30` T:4634, T:4651 | T:4634, T:4651 | measured 8.49s / 8.78s |
| S-2.1 | corpus read class | `_corpus_file` helper T:2612 | T:2612-2620 | was: bare `read_text()` on corpus paths |
| S-10.2 | corpus VERSION declared | `_corpus_version()` T:2622; `_CORPUS_VERSION` T:2641; declared artifacts T:2691-2710 | T:2622-2641, T:2691-2710 | was: no version; skips by absence |
| S-10.3 | 9 skips to strict xfails | 4 process_evidence T:2799; 4 tee_status T:3993; 1 negative (already xfail) | T:2799, T:3993 | was: `pytest.skip(...)` |
| S-10.4 | tee-status parametrization | `sorted(_EXPECTED_REAL_LEGS - {"negative"})` T:3988 | T:3988 | was: `LEGS` (included absent run-2) |
| S-17.1b | `symlink_to` removed from `_WRITE_ATTRS` | creates new dirent, cannot reach shared inode; `chmod`, `hardlink_to`, `utime`, `truncate` kept | T:3351-3353 | PC gate: `symlink_to` at T:2169/2180 flagged pre-existing calls |

### F43 self-test (symlink_to fix)
`test_f43_no_direct_writes_outside_rewrite`: `1 passed, 368 deselected in 0.56s`.
Category set: 15 families (`.write_text`, `.write_bytes`, `open`, `json.dump`, `shutil.copy`, `os.replace`, `.touch`, `.rename`, `.open`, `io.open`, `.chmod`, `.hardlink_to`, `os.truncate`, `os.utime`, `gzip.open`).
R7a negative control: `tgt.chmod(0o400)` + `os.utime(tgt)` both caught as `.chmod()` and `os.utime()`.

## MUTANT TABLE

All on scratchpad copies. `git status --porcelain` on the 3 scope files: clean after each.

| # | mutant | mutation | selection | result | verdict |
|---|---|---|---|---|---|
| 1 | XFAIL-SUBSTRING | `_is_known_stale` reverted to rsplit tail | `known_stale` (1 passed) | `1 failed` | **KILLED** T:4581 `_is_known_stale` |
| 2 | XFAIL-TAIL-COLLISION | extra collision reason added | `known_stale` (1 passed) | `1 failed` | **KILLED** T:4582 `_is_known_stale` |
| 3 | READ-UNGUARDED-PROBE | `S_ISREG` at N:181 deleted | `fifo_at_tools or dir_at_tools` (2 passed) | `2 failed` | **KILLED** T:4620 T:4638 |
| 4 | SCHEMA-PRESENCE-GATED | `_require_file` at C:1707 reverted | `absent_acp` (1 passed) | `1 failed` | **KILLED** T:4656 `_require_file` |
| 5 | CORPUS-UUID-LITERAL | `_REAL_LEG_DIR` hardcoded | `ck11_real_leg_dir` (1 passed) | `1 failed` | **KILLED** T:2648 `_REAL_LEG_DIR` |
| 6 | VENUE-LOOSE | domain check removed from `corpus_declared` | `venue_domain or corpus_declared` | `1 failed, 1 passed` | **KILLED** T:2661 `_VENUE` |
| 7 | SIDECAR-SKIPPED | `return` before sha loop | `corpus_declared` with corrupt corpus | base: `corpus drift`; mutant: passed | **KILLED** T:2689 `_sha256_file` |
| 8 | ALARM-OUTSIDE-TRY | `_signal.alarm` moved above `try:` | `ck11_alarm` (1 passed) | `1 failed` | **KILLED** T:4852 `LEAKED` |
| 9 | AST-SCAN-NEGATIVE | planted `open(HERE/"planted_file.txt","rb")` | `ck11_every_read` (1 passed) | `1 failed` | **KILLED** T:4756 `_require_file` |

**9/9 KILLED. No survivors.**

## AP SCREEN

### Production (C + N)

| hit | line | classification |
|---|---|---|
| AF-AP-40 | C:1488 `if neg_dir.is_dir()` | reviewed-safe: routing gate; check_negative runs only if neg dir exists; NegativeFailure raised inside on every missing file |
| AF-AP-40 | C:1501 `if stderr_path.exists()` | reviewed-safe: optional evidence; `_require_file` inside the true branch |
| AF-AP-40 | C:1698 `if item.is_dir()` | reviewed-safe: REJECTS unexpected dirs (true branch raises Failure) |
| AF-AP-40 | C:1700 `if item.is_file()` | reviewed-safe: REJECTS unexpected files (true branch raises Failure) |
| AF-AP-40 | C:1713 `if post_sum_path.exists()` | reviewed-safe: optional per-leg; `_require_file` inside. In `_REVIEWED_SAFE` at T:4673 |
| AP-32 | C:167, C:175, N:39 | reviewed-safe: sha256 content verification hashing |

### Tests (T)

| hit | line | classification |
|---|---|---|
| AP-66 | T:85, T:87 | reviewed-safe: pre-existing BIP-340 speed cache. Not my change |

## GATES

### pyflakes
```
pyflakes rc=0
```

### report_lint (final)
```
report_lint: 142 refs -- OK 60, NEAR 11, MISS 50, UNCHECKABLE 21, UNRESOLVED 0 (worktree)
```
Every MISS and NEAR is a token-heuristic row. The lint extracts words from description/verdict columns (evidence types like `CONTROL`/`KILLED`, run output like `1 failed`, pytest args, classification words `SAFE`/`CLOSED`) and expects them literally at the cited source line. The cited lines point to the correct code -- verified by `grep -n` on the final bytes. 0 UNRESOLVED.

Report-lint heuristic rows: report:37, 38, 39, 40, 42, 43, 44, 46, 47, 48, 49, 50, 51, 56, 58, 59, 60, 74, 75, 76, 77, 81, 82, 96 -- the cited lines read `def test_*`, `_KNOWN_XFAIL_REASONS = frozenset`, `assert _VENUE in`, `sha, rel = line.split`, `_signal.signal`, `_WRITE_ATTRS =`, `p.unlink()`, `_CORPUS_VERSION`, `sorted(_EXPECTED_REAL_LEGS` -- all correct references whose description-column tokens are evidence classifications or run output, not source identifiers.

### Full 3-file gate (test_summary.sh defaults)
```
373 passed, 9 skipped, 1 xfailed in 1070.87s (0:17:50)
pytest-exit: 0
```

### CI venue
```
331 passed, 52 skipped in 1058.32s (0:17:38)
```

### Real-leg selection (with corpus, -rsxX)
```
S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden
-k "real_leg or corpus or ck11 or ck12 or ck8_real_leg_tee"
53 passed, 307 deselected, 9 xfailed in 27.56s
```
9 xfailed: 4 process_evidence (v2.2 scan) + 4 tee_status (v2.2 tee) + 1 negative (stale probe). 0 skipped.

### FIFO/dir elapsed
FIFO: 8.49s. Dir: 8.78s. Both under the 30s cap.

### Sweep 6.1 R2b/R2c
R2b ("sandbox "): `2 failed` -- `not a known venue`.
R2c ("Sandbox"): `2 failed` -- `not a known venue`.

## Sweep SAFE confirmations

- **3.1** (T:1220 `sorted(rd.glob("*.json"))[-1]`): AGREE SAFE. Expected-reason covers the method attribute.
- **5.3** (T:2867 `_is_known_stale`): CLOSED by item 1. Whole-reason equality, not tail matching.
- **10.6** (T:2872 `test_real_leg_negative`): CLOSED by item 1. `assert not ok` at T:2878 fires first; xfail marks known-stale reasons only.
- **12.2, 14.3, 15.1**: AGREE SAFE. Pre-existing test infrastructure, not my changes.
- **11.x**: No rows for my file; 11.x targets `test_s0_01_frame_tee.py`.

## NOT_DONE

- **PC leg**: NOT run here (no bridge).
- **Combined guard mutant**: NOT re-run (unchanged by these edits).
- **Full re-gate on sweep-amended bytes**: NOT run. The 373-passed gate was before sweep fixes. Pyflakes clean; targeted tests pass.

## DISCREPANCIES

- Item 5: `_VENUE` defaults to `"sandbox"` when unset. Brief says "UNSET venue means sandbox." Old behavior defaulted to `""` (silent skip). Gate flow unchanged (test_summary.sh exports venue).
- Item 8: C:957 originally cited "C:894-895 and C:906-907" (no guard). Fixed to "C:893-893 and C:905-905". Brief said "fix to C:742-743" -- that applies to C:1568 and C:1597, both fixed.
- Item 2 (F8 elapsed): checker processes 5 legs before negative. Measured 8.49s/8.78s. Elapsed bound set to 30s per coordinator item 4.

## SELF-ATTACK

1. `_real_leg()` is a single point of failure for 17 tests. Mitigated by `test_ck11_real_leg_dir_is_resolved_from_the_environment`.
2. AST read-site scan uses variable-name allowlist. A new non-walked variable could be missed. Mitigated by the negative control (mutant 9).
3. AP-40 class scan misses ternary expressions (`x if cond else default`). The schema gate WAS a ternary and was caught by the specific test, not the scan. Documented limit.
4. `_corpus_file` guards reads the TESTS do. It does not guard reads inside the checker functions called via `_run_check_safe` -- those rely on the checker's own `_require_file` and the os.walk. A FIFO in a corpus artifact not read by the test directly would block inside the checker.
