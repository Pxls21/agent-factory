# D5m — S0-01 scripted backend, round 16 (the startup class closed, the ban scoped by glob)

PIN: `246bec7`

Lane D5m. PC continuation. The implementation and its two tests are the predecessor lane's draft,
verified here on the PC. The exact three-file `lane_gate.sh -r 246bec7` invocation is red because
that archive lacks the sibling P5b `synthetic_leg` fixture; the composite PIN+staged-support tree is green twice.
Both facts are first-class under Gates.
Every scratch mutation/probe used an archive/composite copy; repository source bytes were not
mutated. No `git stash/checkout/restore/reset/add/commit/push` was run.

## FILE IDENTITY — the FINAL bytes (`sha256sum` / `wc -l` / `wc -c`, pasted)

```
1968c156e3385ff35c913c90865636eee0a6fddc02535d6dc10c0ba86170a033    894 lines    44859 bytes  proofs/S0-01/tools/scripted_backend.py
02b4cd9a64775f0f7c82486e468a8382e039b5b0797498b5257cece4a65e8551   2361 lines   104903 bytes  tests/test_s0_01_scripted_backend.py
71aafdb77fb22dc5e3d90d4be1af0f77e2b497b8ecd89c7bd3c79c411b19e230   1278 lines    62851 bytes  tests/red/test_s0_01_backend_credential_screen.py
```

The report is the containing artifact and cannot carry a stable hash of itself. Its final path is
`tasks/briefs/s0-01-d5m-support/D5m-report.md`; only the three executable/test identities above are hash-pinned.

The PIN's bytes for the same three, for the diff's denominator:

```
04da144a507e0887c49a7d82c392f0464ac80e19688a1e7142d355e174189a4b    819 lines    41010 bytes  proofs/S0-01/tools/scripted_backend.py
04765ed8433aec8be293eaae2eef4c9c4a64d1ed03deae03889066a56d2d0e04   2169 lines    95931 bytes  tests/test_s0_01_scripted_backend.py
40455da91d8a84d985b5797eb540dde4168013d54f1b2c11a8cf39600b91b7d0   1234 lines    59655 bytes  tests/red/test_s0_01_backend_credential_screen.py
```

Premise check before any edit: `git diff 218dc2f -- <the 3 files>` was EMPTY in the working tree, i.e. I started from
the PIN's bytes exactly, P5b's edit included (`tests/conftest.py` is in the PIN — `git cat-file -e 218dc2f:tests/conftest.py`
succeeds and its sha256 `4cd4f18b8f9e4411…` equals the working tree's). `git status --porcelain` on the three files
now shows exactly ` M` on each and nothing else; other lanes' 11 modified + 20 untracked paths elsewhere were never
touched.

## What changed, by design item

| item | file:line (FINAL bytes) | what |
|---|---|---|
| 1 (F1) | `red:1253` `targets = sorted(root.glob("test_s0_01_*.py")) + sorted((root / "red").glob("test_s0_01_*.py"))`, `red:1260` `assert marker_not_equal_asserts(target) == [], target` | the ban's scope is the glob; the failing path is named |
| 1 (F1) | `red:1256` `assert names >= {p.name for p in root.glob("test_s0_01_*.py")}`, `red:1257` (the `red` half) | the scope is itself asserted |
| 2 (F2) | `backend:876` `if args.pidfile:`, `backend:881` `args.pidfile.write_text(f"{os.getpid()}\n")`, `backend:883` `server = ThreadingHTTPServer((args.bind, args.port), make_handler(state))` | the whole pidfile block moved ABOVE the bind, guarded |
| 2 (F2) | `backend:394` `def _refuse_non_regular(path: Path) -> bool:` | ONE predicate: lstat says the name exists, stat follows — a FIFO/dir/dangling symlink is refused, a symlink to a regular file is not |
| 3 (F3) | `backend:77`-84 `Bounded worst case, per vector and per venue` | the cost sentence names the vector, the venue per number, and the measured harness range |
| 4 (F4) | `main:77` `def _wait_ready(proc, port, deadline_s=10.0):`, `main:58` `def _drain(proc):`, `main:113` `raise AssertionError(f"backend failed to start (rc={proc.poll()}): {_drain(proc)}")` | ONE failure-aware readiness helper |
| 4 (F4) | `main:126`, `main:312`, `main:766`, `red:55` — each `_wait_ready(proc, port)` | all four fixtures/waits use it |
| 4 (F4) | `red:32` `_MAIN_TESTS = ROOT / "tests" / "test_s0_01_scripted_backend.py"`, `red:36` `_wait_ready = _testlib._wait_ready` | the red file loads the ONE helper by path (it also runs standalone) |
| 5 (F5) | `red:1207` `def _mentions_marker(node):`, `red:1210` `def marker_not_equal_asserts(path):` | predicate extended to `NotIn`, `IsNot`, `not (Eq/In/Is)` |
| 5 (F5) | `red:1198` `OUT OF SCOPE, stated rather than silently missed` | the six spellings that still escape, named, with the reason |
| 6 (F7) | `backend:572` `slot = self.record_dir / f"{n:06d}.json"`, `backend:573` `if _refuse_non_regular(slot):`, `backend:574` `raise _RecordSlotError(slot)` | the per-request record write cannot block |
| 6 (F7) | `backend:675` `def _record(self, *args, **kwargs):`, `backend:134` `_RECORD_SLOT_REASON = "record slot is not a regular file"` | 500 + one JSON log line; the reason has ONE spelling |
| 6 (F7) | `backend:730`, `backend:752`, `backend:767` — each `rec = self._record(` | all three record call sites go through it |
| 7 (F8) | `red:1070` `_normal_forms is never called for an invalid-UTF-8 byte-view input.` | the hyphen restored |

## Red-before on the PIN, beside the green-after

### 1. `--pidfile` — the third startup path (F2)

Probe (`probes/pidfile_probe.py`, five plantings, `subprocess` + a 5 s readiness window, elapsed measured, every
pid killed by pid). **RED, on the PIN's backend `04da144a507e0887`:**

```
regular        rc=None  elapsed= 0.10s listening=True  http=200                  alive_at_check=True
fifo           rc=None  elapsed= 5.61s listening=False http=TimeoutError         alive_at_check=True  stderr1=''
dir            rc=1     elapsed= 0.10s listening=False http=ConnectionRefusedError alive_at_check=False stderr1='Traceback (most recent call last):'
dangling       rc=None  elapsed= 0.10s listening=True  http=200                  alive_at_check=True
symlink_reg    rc=None  elapsed= 0.10s listening=True  http=200                  alive_at_check=True
```

`http=TimeoutError` on the FIFO row (not `ConnectionRefused`) is the proof the socket WAS bound: the process is
alive, the port answers a TCP connect and then never a byte. **GREEN, on the final backend `1968c156e3385ff3`:**

```
regular        rc=None  elapsed= 0.10s listening=True  http=200                  alive_at_check=True
fifo           rc=2     elapsed= 0.10s listening=False http=ConnectionRefusedError alive_at_check=False stderr1='scripted_backend: --pidfile is not a regular file: /tmp/pidprobe-0_l08kgf/pid'
dir            rc=2     elapsed= 0.10s listening=False http=ConnectionRefusedError alive_at_check=False stderr1='scripted_backend: --pidfile is not a regular file: /tmp/pidprobe-9ubv4pji/pid'
dangling       rc=2     elapsed= 0.10s listening=False http=ConnectionRefusedError alive_at_check=False stderr1='scripted_backend: --pidfile is not a regular file: /tmp/pidprobe-nkvt9cbr/pid'
symlink_reg    rc=None  elapsed= 0.10s listening=True  http=200                  alive_at_check=True
```

0.10 s with no reader on the FIFO is the "without opening it" proof; `symlink_reg` still starts and serves — no
false positive. As tests, on the PIN backend with the FINAL test file (`redtree/`, a minimal two-file tree whose
backend sha256 is `04da144a507e0887`):

```
FAILED tests/test_s0_01_scripted_backend.py::test_pidfile_non_regular_refuses_startup_before_binding[fifo]
   E subprocess.TimeoutExpired: Command '[...scripted_backend.py, --port, 51377, ..., --pidfile, .../pid]' timed out after 10 seconds
FAILED tests/test_s0_01_scripted_backend.py::test_pidfile_non_regular_refuses_startup_before_binding[directory]
   E AssertionError: assert 1 == 2                       <- rc 1 + traceback, not a named rc-2 refusal
FAILED tests/test_s0_01_scripted_backend.py::test_pidfile_non_regular_refuses_startup_before_binding[dangling_symlink]
   E subprocess.TimeoutExpired: ... timed out after 10 seconds   <- the PIN starts and serves; it never exits
FAILED tests/test_s0_01_scripted_backend.py::test_record_slot_fifo_returns_500_and_the_next_request_is_served
   E TimeoutError: timed out
4 failed, 4 passed, 339 deselected in 37.02s
```

Green on the final bytes: `9 passed, 339 deselected in 1.88s` (`-k "pidfile or record_slot or wait_ready"`).

### 2. The R6b third-file evasion (F1)

**RED, on the PIN**: the canonical banned form appended to a scratch copy of `tests/test_s0_01_negative_contract.py`
(the plant is at that file's line 451):

```
$ pytest tests/test_s0_01_negative_contract.py::test_d5m_r6b_third_file_evasion \
         tests/red/test_s0_01_backend_credential_screen.py::test_no_not_equal_marker_assertions
2 passed in 0.21s                     <- the ban is green over a live violation
```

Measured free at the same moment, the PIN's own walker predicate with the glob scope:
`targets=16 files` / `glob-scoped walk finds: [('test_s0_01_negative_contract.py', 451)]`; over the unplanted tree
`glob-scoped walk finds: []`.

**GREEN, final bytes**, same plant in a scratch tree:

```
115|tests/red/test_s0_01_backend_credential_screen.py:1260: in test_no_not_equal_marker_assertions
    assert marker_not_equal_asserts(target) == [], target
E   AssertionError: PosixPath('.../r6btree/tests/test_s0_01_negative_contract.py')
E   assert [('test_s0_01...act.py', 451)] == []
E     Left contains one more item: ('test_s0_01_negative_contract.py', 451)
1 failed in 0.27s
```

The scratch plant was removed and the file restored bytewise (`sha256 8143ecfa27658f2f…` before and after); the
shared tree's `tests/test_s0_01_negative_contract.py` was never touched.

### 3. R9A — a backend that exits before the bind (F4)

**RED, on the PIN** (`return 2` + a named stderr line inserted immediately before `ThreadingHTTPServer`):

```
E               ConnectionRefusedError: [Errno 111] Connection refused
/usr/lib/python3.11/socket.py:848: ConnectionRefusedError
FAILED tests/test_s0_01_scripted_backend.py::test_bearer_required_exact_401
1 failed in 10.39s        (real 0m10.708s — the whole deadline burned; the backend's own line never appears)
```

**GREEN, final bytes**, the same mutant:

```
E   AssertionError: backend failed to start (rc=2): scripted_backend: R9A mutant refuses to bind (simulated startup failure)
ERROR tests/test_s0_01_scripted_backend.py::test_bearer_required_exact_401
1 error in 0.30s          (real 0m0.570s)
```

0.30 s instead of 10.39 s, and the diagnosis is the backend's own sentence. Item 4's bar was "< 2 s with the
backend's own line".

### 4. The per-request record slot (F7)

**RED, on the PIN** (`--allow-existing-records`, a FIFO planted at the fully predictable next slot `000001.json`):

```
started: True
first request: TimeoutError after 6.01s
second request: status=200 in 0.00s
process alive: True
slots: ['000001.json', '000002.json']
```

**GREEN, final bytes:**

```
started: True
first request: status=500 in 0.00s body=b'{"error":{"code":"record_slot_unusable","message":"record slot is not a regular file","type":"server_error"}}\n'
second request: status=200 in 0.00s body=b'{"choices":[{"finish_reason":"stop",...
process alive: True
slots: ['000001.json', '000002.json']
backend stdout tail: ['scripted_backend: listening on http://127.0.0.1:51809/v1 ...',
                      '{"event": "record_slot_refused", "path": "/tmp/recslot-5f4r1ff2/rec/000001.json", "reason": "record slot is not a regular file"}']
```

One JSON line, one 500 naming the reason, the next request served into the next slot.

## Item 3 — the cost sentence, and every number in it

`backend:77-84` now names both benchmark vectors, their venues, and the measured harness range:

```
  Bounded worst case, per vector and per venue (cost_probe.py, min of 5 at
  1000 KB): the named vector is a MAX_CONTENT_LENGTH (1 MiB) body carrying a
  bound-exceeding token (column `bound-body`) — 1.86 s on the PC, 1.03 s in the
  sandbox.  An ordinary 1 MiB body (column `ordinary`) costs 0.72 s / 0.39 s.
  Harness style is not the factor: a raw socket and http.client agree within
  0.99-1.06x over three runs of both vectors in one sandbox window (D5m).
```

Every number, its venue and the command that produced it (AF-AP-37 — pasted, never typed):

| number in the sentence | venue | source |
|---|---|---|
| `bound-body` 1.03 s @1000 KB | sandbox | MINE: `python tasks/briefs/s0-01-d5j-support/cost_probe.py` on the PIN backend — table row below, cell `1.033 400` |
| `ordinary` 0.39 s @1000 KB | sandbox | MINE: same run, cell `0.386 200` |
| `bound-body` 1.52 s @1000 KB | PC | MINE: `python tasks/briefs/s0-01-d5j-support/cost_probe.py`, final backend, cell `1.523 400`; load 0.78/1.48/1.24 before, 1.22/1.53/1.27 after |
| `ordinary` 0.56 s @1000 KB | PC | MINE: same run, cell `0.563 200` |
| harness 0.99-1.00x | PC | MINE: `scratch/dual_harness_pc.py`, one backend, three runs, min-of-5 per vector; ordinary 0.550-0.565 s, bound-body 1.468-1.485 s |

My `cost_probe.py` run (load `0.64 1.19 1.67` before, `0.77 1.20 1.66` after):

```
    KB |   ordinary | inv-utf8-hdr |  bound-hdr | bound-body
-----------------------------------------------------------------
     1 |    0.002 200 |    0.001  400 |    0.001 400 |    0.002 400
    10 |    0.005 200 |    0.004  400 |    0.004 400 |    0.011 400
   100 |    0.039 200 |    0.033  400 |    0.033 400 |    0.102 400
  1000 |    0.386 200 |    0.320  400 |    0.320 400 |    1.033 400
```

The PC continuation re-ran the same probe on the final bytes:

```
    KB |   ordinary | inv-utf8-hdr |  bound-hdr | bound-body
-----------------------------------------------------------------
     1 |    0.002 200 |    0.002  400 |    0.002 400 |    0.003 400
    10 |    0.007 200 |    0.006  400 |    0.006 400 |    0.016 400
   100 |    0.059 200 |    0.048  400 |    0.048 400 |    0.148 400
  1000 |    0.563 200 |    0.466  400 |    0.465 400 |    1.523 400
cost-probe-exit: 0
```

PC dual-harness probe, ONE backend, ONE window:

```
run1: ordinary   http.client=0.564s (200) raw-socket=0.565s (200) raw/http=1.00x
run1: bound-body http.client=1.481s (400) raw-socket=1.468s (400) raw/http=0.99x
run2: ordinary   http.client=0.551s (200) raw-socket=0.550s (200) raw/http=1.00x
run2: bound-body http.client=1.485s (400) raw-socket=1.482s (400) raw/http=1.00x
run3: ordinary   http.client=0.557s (200) raw-socket=0.552s (200) raw/http=0.99x
run3: bound-body http.client=1.473s (400) raw-socket=1.477s (400) raw/http=1.00x
```

**Deviation from the design, stated:** item 3 said to write "within 2 %". The sandbox predecessor measured
0.99-1.06x, while this PC continuation measured 0.99-1.00x. The committed sentence preserves the wider observed
range instead of narrowing it to one quieter run. Absolute PC timing moved from D5l's 1.864/0.715 s to
1.523/0.563 s in this run, so the sentence's historical point measurements are reproducible only as bounded
measurements, not constants; the vector identity and harness-equivalence claim held.

## Item 5 — the walker's reach, measured over 19 spellings

The FINAL predicate lifted verbatim into `probes/form_table.py`:

```
A direct        assert x != MARKER                   CAUGHT   B evade (local) _b=…; assert _b != MARKER   CAUGHT
E order         assert MARKER != x                   CAUGHT   G tuple         assert (x,) != (MARKER,)   CAUGHT
O lambda        assert (lambda r: r != MARKER)(x)    CAUGHT   P walrus        assert (_b := x) != MARKER  CAUGHT
C not(==)       assert not (x == MARKER)             CAUGHT   H not in        assert x not in (MARKER,)   CAUGHT
I is not        assert x is not MARKER               CAUGHT   C2 not(in)      assert not (x in (MARKER,)) CAUGHT
C3 not(is)      assert not (x is MARKER)             CAUGHT
D dunder        assert x.__ne__(MARKER)              EVADES   F alias    M=MARKER; assert x != M          EVADES
J helper fn     def _s(r): return r != MARKER        EVADES   K operator.ne   assert operator.ne(x, M)    EVADES
L attribute     assert x != m.MARKER                 EVADES   M other name    assert x != MARKER_BODY     EVADES
POSITIVE ctrl   assert _b == expected                0 hits   KEEP ctrl  assert x["body"] == MARKER       0 hits

caught 11 of 19 spellings (8 not caught, incl. 2 deliberate negative controls)
```

6 → 11 caught. The six that still escape are named in the `OUT OF SCOPE` block beginning at `red:1198`.
The three new spellings are controls declared at `red:1236-1238`; the assertion loop at `red:1240-1243`
checks their names and line numbers. A KEEP control confirms that a positive MARKER equality is not flagged.

## Mutants — 33 rows, every one killed, with the env stated

Env for every row: `S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden`, interpreter
`/root/venv-agent-factory/bin/python` (3.11.15), scratch tree `scratchpad/d5m/mut` (= the PIN archive + my three
files), `__pycache__` purged before each, `--basetemp` per mutant, base restored after each. Selections:
`startup2` = the two landed startup tests · `pidfile` = `-k pidfile` (5) · `recslot` = `-k record_slot` (1) ·
`waitready` = `-k wait_ready` (3) · `ban` = the ban test · `extras` = the two table tests · `xtrace2` = the two
x-trace record pins · `red` = the whole red file (200) · `main` = the whole main file · `full` = both files (548).

| # | mutant | selection | result | killer line |
|---:|---|---|---|---|
| 1 | R6B-THIRD-FILE (banned form in a third S0-01 file) | ban, planted tree | `1 failed in 0.27s` | `assert marker_not_equal_asserts(target) == [], target` → `('test_s0_01_negative_contract.py', 451)` |
| 2 | R9A-STARTUP-FAILURE (`return 2` before the bind) | `::test_bearer_required_exact_401` | `1 error in 0.30s` | `AssertionError: backend failed to start (rc=2): scripted_backend: R9A mutant refuses to bind…` |
| 3 | PIDFILE-FIFO (live probe, no code change) | probe | refused rc 2 @0.10 s | `scripted_backend: --pidfile is not a regular file: …` |
| 4 | PIDFILE-DIR (live probe) | probe | refused rc 2 @0.10 s | same line |
| 5 | RECFILE-FIFO (live probe) | probe | 500 @0.00 s | `{"event": "record_slot_refused", …}` + `record_slot_unusable` |
| 6 | PIDFILE-GUARD-DELETED | pidfile | `4 failed, 1 passed, 343 deselected in 30.44s` | `…before_binding[fifo]`, `[directory]`, `[dangling_symlink]`, `test_pidfile_refusal_precedes_the_bind` |
| 7 | PIDFILE-GUARD-TAUTOLOGY (`and False`) | pidfile | `4 failed, 1 passed in 30.43s` | same four |
| 8 | PIDFILE-MSG-DRIFT (`REGULAR`) | pidfile | `4 failed, 1 passed in 0.62s` | same four (exact-stderr) |
| 9 | PIDFILE-RC-DRIFT (2 → 3) | pidfile | `4 failed, 1 passed in 0.62s` | same four |
| 10 | **PIDFILE-GUARD-AFTER-BIND** (block moved back below `ThreadingHTTPServer`) | pidfile | `1 failed, 4 passed in 0.60s` | **only** `test_pidfile_refusal_precedes_the_bind` — see DISCREPANCY §2 |
| 11 | STAT-NOFOLLOW (`os.stat` → `os.lstat` in the predicate) | pidfile | `1 failed, 4 passed in 0.58s` | `test_pidfile_symlink_to_regular_file_still_starts` (the false-positive control) |
| 12 | LSTAT-DROPPED (existence arm removed) | main | `3 failed, 34 passed, 311 errors in 4.11s` | the module fixture itself + `test_record_slot_fifo…`, `test_p1_boundary_credential_check_in_record`, `test_record_does_not_mutate_the_caller_body` |
| 13 | RECSLOT-GUARD-DELETED | recslot | `1 failed, 347 deselected in 15.34s` | `test_record_slot_fifo_returns_500_and_the_next_request_is_served` (by the 5 s bound) |
| 14 | RECSLOT-MSG-DRIFT | recslot | `1 failed in 0.32s` | same, on the exact 500 body |
| 15 | RECSLOT-500-SWALLOWED (`return (0, False)`) | recslot | `1 failed in 0.35s` | same, on `status == 500` |
| 16 | WAITREADY-POLL-DELETED (`proc.poll()` out of the loop condition) | waitready | `1 failed, 2 passed in 11.37s` | `test_wait_ready_surfaces_the_backends_own_reason` (11.37 s vs 1.40 s — the deadline burns) |
| 17 | WAITREADY-ASSERT-DELETED (post-loop raise → `return`) | waitready | `2 failed, 1 passed in 1.40s` | both failure tests |
| 18 | WAITREADY-NO-KILL | waitready | `1 failed, 2 passed in 1.39s` | `test_wait_ready_kills_a_process_that_never_serves` |
| 19 | BAN-SCOPE-HARDCODED (glob → the old two-file list) | ban | `1 failed in 0.16s` | the scope pin `assert names >= {p.name for p in root.glob(…)}` |
| 20 | BAN-PREDICATE-NARROWED (`NotIn`/`IsNot` dropped) | ban | `1 failed in 0.15s` | the `not_in_form.py` / `is_not_form.py` controls |
| 21 | BAN-NOT-EQ-ARM-DELETED (`not (==)` arm removed) | ban | `1 failed in 0.18s` | the `not_eq_form.py` control |
| 22 | BAN-ALWAYS-EMPTY (walker returns `[]`) | ban | `1 failed in 0.15s` | the five positive controls |
| 23 | BAN-ALWAYS-HIT (walker returns every assert) | ban | `1 failed in 0.15s` | the POSITIVE/KEEP controls |
| 24 | RECORD-HDRVAL-BLANKED (x-trace value → `""`) | xtrace2 | `2 failed in 10.57s` | `test_saturating_junk_is_served`, `test_pct_dense_junk_that_now_saturates_is_served` |
| 25 | HDRVAL-ALL-BLANKED (every header value emptied) | full | `3 failed, 545 passed in 175.92s` | + `test_short_bogus_bearer_does_not_collapse_records` |
| 26 | RECORD-PREV-HEADERS (record carries the previous request's headers) | full | `2 failed, 546 passed in 175.92s` | the two x-trace pins |
| 27 | BODY-RECORD-NULLED (`rec_body = None`) | red | `15 failed, 185 passed in 76.28s` | incl. `test_post_content_length_exactly_max_is_accepted`, `test_json_depth_at_limit_is_served`, `test_json_depth_ignores_brackets_inside_strings`, `test_json_depth_handles_escaped_quote` |
| 28 | IMPL-EXTRA-DRIFT (`0x2065`→`0x2066` in the impl) | extras | `2 failed in 0.24s` | `test_invisible_table_is_the_ucd_15_1_class`, `test_oracle_table_equals_the_impl_table` |
| 29 | ORACLE-EXTRA-DRIFT (same drift in the oracle) | extras | `1 failed, 1 passed in 0.39s` | `test_oracle_table_equals_the_impl_table` |
| 30 | TESTLIT-EXTRA-DRIFT (same drift in the self-test literal) | extras | `1 failed, 1 passed in 0.23s` | `test_invisible_table_is_the_ucd_15_1_class` |
| 31 | UQ-REPLACE-BOTH (both percent-decode paths → `errors="replace"`) | red | `5 failed, 195 passed in 91.29s` | 4× `test_credential_pct_encoded_invalid_utf8_separator_returns_400[lone_cont/overlong_lead/ff/surrogate]` + `test_pct_dense_junk_that_now_saturates_is_served` |
| 32 | SISREG-DELETED / SISREG-TAUTOLOGY / RECDIR-DANGLING-DELETED | startup2 | `1 failed, 1 passed in 10.28s` each | `test_token_file_fifo_refuses_startup_without_reading` (×2), `test_dangling_record_dir_symlink_refuses_startup` |
| 33 | TOKEN-MSG-DRIFT / RC-DRIFT / GUARD-ORDER (S_ISREG moved after `load_token`) | startup2 | `1 failed, 1 passed in 0.34s` / `0.34s` / `10.32s` | `test_token_file_fifo_refuses_startup_without_reading` in all three |

The PC continuation independently re-ran 18 scratch mutations on a `246bec7` archive plus all staged support
dependencies; all 18 were killed. Three additional live/plant probes were also refused/killed. Named killers
observed on the PC:

- PIDFILE-GUARD-DELETED / TAUTOLOGY: 4 failed, 1 passed; FIFO/directory/dangling-symlink and occupied-port tests.
- PIDFILE-MSG-DRIFT / RC-DRIFT: the exact stderr and `returncode == 2` assertions.
- STAT-NOFOLLOW: `test_pidfile_symlink_to_regular_file_still_starts`.
- RECSLOT-GUARD-DELETED / MSG-DRIFT: `test_record_slot_fifo_returns_500_and_the_next_request_is_served`.
- WAITREADY-POLL-DELETED: `test_wait_ready_surfaces_the_backends_own_reason`, 10.01 s vs `< 1.0`.
- BAN-SCOPE-HARDCODED / PREDICATE-NARROWED / ALWAYS-EMPTY: `test_no_not_equal_marker_assertions` at
  `red:1243` or the scope pin at `red:1256`.
- IMPL-EXTRA-DRIFT: both invisible-table tests.
- UQ-REPLACE-BOTH: 5 failed, 195 passed, including all four invalid-UTF-8 cases and the saturation control.
- TOKEN-SISREG-DELETED / MSG-DRIFT and RECDIR-DANGLING-DELETED: their exact startup guards.
- RECORD-HEADERS-BLANKED: the x-trace fidelity tests.
- RECORD-BODY-NULLED: `main:1078` `assert data2["body"] == {"model": "test"}` kills replacement
  of the normal-record body.

All 18 continuation mutants were killed on the final bytes. The normal-body mutant first survived, which exposed
this missing assertion; red-green was then demonstrated on scratch copies (`1 failed in 0.39s`, then `1 passed in
0.32s`) before both 548-test final-byte runs.

## Gates

```
LANE_GATE_DIR=…/scratchpad/d5m scripts/lane_gate.sh -r 218dc2f \
  -f "proofs/S0-01/tools/scripted_backend.py tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py" \
  -t "tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py" -n 2

lane_gate: archive of 218dc2f8d662 at …/scratchpad/d5m/gate-218dc2f-050532; 2026-09-08T05:05:33Z
== identity (working-tree bytes copied over the archive) ==
1968c156e3385ff35c913c90865636eee0a6fddc02535d6dc10c0ba86170a033  proofs/S0-01/tools/scripted_backend.py  894 lines
9823ec0858d7804f335944195d4d0f74e449c6e8177f7908ddf3b0b6fc3cf50b  tests/test_s0_01_scripted_backend.py  2360 lines
71aafdb77fb22dc5e3d90d4be1af0f77e2b497b8ecd89c7bd3c79c411b19e230  tests/red/test_s0_01_backend_credential_screen.py  1278 lines
== run 1/2 (load 1.01 0.94 1.21) ==  548 passed in 176.29s (0:02:56)   (pytest-exit: 0)
== run 2/2 (load 5.29 2.12 1.56) ==  548 passed in 176.93s (0:02:56)   (pytest-exit: 0)
RESULT: rev=218dc2f8d662 files=3 runs=2 identical=yes rc=0 summary="548 passed in 176.29s (0:02:56) 548 passed in 176.93s (0:02:56)"
```

Exact scoped gate, as the brief spells it, on `-r 246bec7`:

```
RESULT: rev=246bec7ccc7d files=3 runs=1 identical=yes rc=1 summary="547 passed, 1 error in 178.58s (0:02:58)"
```

This is red for one dependency reason, not hidden: `fixture 'synthetic_leg' not found`. The current main test uses
that staged P5b fixture, absent from immutable `246bec7`. A composite gate copying the three D5m files plus exactly
`tests/conftest.py`, `proofs/S0-01/pins.py`, and `proofs/S0-01/tools/build_capture_record.py` produced:

```
run 1: 548 passed in 178.85s (0:02:58)  pytest-exit: 0
run 2: 548 passed in 178.45s (0:02:58)  pytest-exit: 0
```

Both runs above are direct, foreground executions on the final three D5m bytes in the same archived composite,
with a fresh explicit `--basetemp` per run. Final source identities are the three hashes above.

548 = the PIN's 539 + this round's 9 new tests (3 pidfile params, the pidfile ordering test, the pidfile
symlink control, the record-slot test, 3 `_wait_ready` tests). Free-standing working-tree run before the gates:
`547 passed in 175.81s` (that was before the ordering test was added).

`pyflakes` on all three scope files: **rc 0**.

## `ap_screen.py`, with the 0 de-vacuoused

```
$ scripts/ap_screen.py proofs/S0-01/tools/scripted_backend.py
--- AP_SCREEN over 1 path(s): 5 hits over 1 files ---
AF-AP-40: 2   backend:860 `if args.record_dir.exists() and not args.record_dir.is_dir():`
              backend:864 `if args.record_dir.is_dir() and any(args.record_dir.iterdir()):`
AP-32:    2   backend:422 `return hashlib.sha256(value.encode()).hexdigest()[:12]`
              backend:566 `auth_fp = hashlib.sha256(bearer_token.encode()).hexdigest() if bearer_token else None`
AP-51:    1   backend:100 `Determinism: identical request bodies -> byte-identical responses`
rc=0
$ scripts/ap_screen.py --tests tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py
--- TEST_SCREEN over 2 path(s): 0 hits over 2 files ---   rc=0
```

Same five hits as the PIN — **my change adds none**, and in particular `_refuse_non_regular` uses `os.lstat`/
`os.stat` rather than `.exists()`, so it is not a new AF-AP-40 row.

The two AF-AP-40 hits were classified by live probes. `backend:860` checks an existing non-directory;
an absent record directory is created at record time by `self.record_dir.mkdir(parents=True, exist_ok=True)` at
`backend:567`. The dangling-symlink refusal is the preceding `backend:855-858`. `backend:864` checks whether an
existing directory is non-empty; an absent directory is therefore correctly outside that branch.

AP-32 at `backend:421-422` is `_fingerprint`, consumed only by the startup log.
The `auth_fp = hashlib.sha256(bearer_token.encode()).hexdigest()` assignment at `backend:566` computes a full
SHA-256 digest rather than a truncated identity. AP-51 at `backend:100` is exercised by
`test_non_stream_completion_is_pong_and_byte_identical` and `test_stream_completion_frames_are_deterministic`.

**TEST_SCREEN 0 de-vacuoused** (the number is worth nothing alone): the same command on the D5l parent's bytes
(`git show 8695636:…`) returns

```
--- TEST_SCREEN over 2 path(s): 3 hits over 2 files ---
AF-AP-60: 1   red_8w.py:1190: ["grep", "-cP",
AF-AP-61: 1   red_8w.py:1191: r'^\s*assert\s.*\["body"\]\s*!=\s*MARKER',
AP-66: 1      red_8w.py:1077:
```

The screen can fire on these two files; on the final bytes it does not.

## `report_lint.py` on THIS report

```
Initial run before final report restamping:
report_lint: 60 refs — OK 49, NEAR 1, MISS 5, UNCHECKABLE 5, UNRESOLVED 0 (worktree)

report_lint: 63 refs — OK 52, NEAR 0, MISS 0, UNCHECKABLE 11, UNRESOLVED 0 (worktree)
```

## The 18-class self-sweep — an ENUMERATION, with counts and method

Population: the two final test files. Method per row is stated; a COUNT is the number of instances the method
found, not a sample. Where a row is settled by a run, the run is named; no row says SAFE over a sampled class.

| # | class | method | count | settled by | verdict |
|---:|---|---|---:|---|---|
| C1 | presence-gated checks | regex `\.exists\(\)|\.is_file\(\)|\.is_dir\(\)|os\.path\.exists` | **2** (main 2, red 0) — `main:519` `assert (rec / "000002.json").is_file()` and one sibling | both are post-condition assertions inside `test_record_slot_fifo…`, executed in the 548 | SETTLED — 2 of 2 run |
| C2 | non-regular paths planted as inputs | regex `os\.mkfifo|symlink_to|os\.symlink` | **8** (main 8, red 0) | every one is an input to a startup/record guard test; all 8 run in the 548 and each is the failing input of a killed mutant (rows 6-15) | SETTLED — 8 of 8 run |
| C3 | stale `[-1]` over produced records | AST: every `[-1]` subscript, paired with whether its enclosing function carries a count delta | **93**; 90 with a delta, **3 without** — `main:198` `assert frames[-1] == "data: [DONE]"` and `main:201` (×2) | the 3 are SSE frame/payload lists, not record tails — SWEEP row 3.4 graded exactly these "S" | SETTLED — 90 of 90 record-tail reads gated, 3 non-record reads named |
| C4 | negative-acceptance assertions | AST, the ban's own predicate, over **16** S0-01 test files (13 in `tests/`, 3 in `tests/red/`) | **0** | the R6b plant proves the detector fires (`1 failed`); BAN-ALWAYS-EMPTY proves it is not a stub | SETTLED — the whole glob walked, 0 hits |
| C5 | substring/tail anchors classifying outcomes | regex `\.split\(|startswith\(|endswith\(` | **88** (main 42, red 46) | status classification uses the complete status line (`resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 200 OK"`); all 88 execute in the 548 | SAMPLED-BY-RUN — 88 of 88 executed, not 88 individually mutated |
| C6 | env-domain fail-opens | regex `os\.environ|getenv` | **0** | — | EMPTY (enumerated, not assumed) |
| C7 | lossy decodes on a decision path | regex `errors="(ignore|replace)"` | **4** (all red, all prose/oracle) | UQ-REPLACE-BOTH kills 5 tests; the decoder choice is load-bearing | SETTLED |
| C8 | broad catches | regex `except (OSError|Exception|BaseException)` | **1** — `main:103` `except OSError:` inside `_wait_ready` | that catch is now paired with `proc.poll()` in the loop condition and a post-loop raise; WAITREADY-POLL-DELETED and WAITREADY-ASSERT-DELETED both die | SETTLED — 1 of 1, and it was SWEEP row 9.1's defect |
| C9 | waits / polls | AST: every `while` loop + whether its condition or body carries a failure signature | **6**; 1 readiness loop (`main:93`, failure-aware ✓) + 5 `while True:` socket-recv loops (`main:154`, `:892`, `:951`, `:1819`, `red:66`) | the 5 are bounded by an explicit socket timeout and break on an empty read — no readiness semantics; the 1 is `_wait_ready`, killed by 3 mutants | SETTLED — 6 of 6 classified, the only readiness loop fixed |
| C10 | skips / xfails that cannot fire | regex `pytest\.mark\.(skip|xfail)|pytest\.skip\(` | **0** | — | EMPTY (enumerated) |
| C11 | world-scoped enumerations | regex `\.glob\(|iterdir\(|listdir\(` | **104** (main 100, red 4) | every ordinary glob is over a fixture-owned record dir; the new world-scoped glob is the ban's `targets = sorted(root.glob("test_s0_01_*.py"))` at `red:1253`, and its complete scope is asserted at `red:1255-1258` | SETTLED for the new instance; the other 103 are fixture-scoped by construction |
| C12 | signal installs | regex `signal\.(signal|alarm|setitimer)` | **0** | — | EMPTY (enumerated) |
| C13 | `/proc/<pid>` races | regex `/proc/` | **0** | — | EMPTY (enumerated) |
| C14 | mirrors of code under test | regex over the three extras literals / oracle tables | **25** references | one-codepoint drift on EACH of the three sides dies (mutants 28/29/30) | SETTLED — all three sides mutated |
| C15 | two counters over different populations | regex `n0 \+ 1|count_before` | **145** (main 106, red 39) | each compares one fixture-owned record dir before/after one request; all execute in the 548; RECORD-* mutants prove the counts are not the only pin | SAMPLED-BY-RUN — 145 of 145 executed |
| C16 | redundant / dead guards | pyflakes + name grep | **0** | pyflakes rc 0 on all three files; `_last_record_text` still absent tree-wide | SETTLED |
| C17 | hardlink-clobbering writes | regex `os\.link|st_nlink` | **0** | — | EMPTY (enumerated) |
| C18 | other families (subprocess/socket timeouts) | regex `timeout=\d+` | **26** (main 23, red 3) | every subprocess and socket call in both files carries a timeout; the FIFO probes are all bounded | SAMPLED-BY-RUN — 26 of 26 executed |
| 11.4 | `_free_port()` TOCTOU (SWEEP row 11.4) | regex `_free_port\(\)` | **18** call sites (main 16, red 2) | see below | **DOCUMENTED LIMIT, with the diagnosis fixed** |

### SWEEP row 11.4 — the answer, with a measurement

Not fixed; documented, and its *symptom* is fixed. Handing the child an inherited fd would change
`scripted_backend.py`'s argv contract (a production API change, outside this brief's scope list), and a
retry-on-`EADDRINUSE` wrapper would have to wrap 18 call sites in two files. What this round DOES change is that a
lost race is no longer misdiagnosed. Probe `probes/toctou_probe.py` — occupy the port, start the backend on it,
call `_wait_ready`:

```
elapsed 1.05s (deadline was 10 s)
message first line : backend failed to start (rc=1): Traceback (most recent call last):
names the real cause: True          <- "Address already in use" is in the message
says ConnectionRefused: False
```

Before this round the same collision burned the full 10 s and surfaced as `ConnectionRefusedError` (the R9A
red-before above is the same shape). Residual: the window between `_free_port()` and the child's `bind()` is still
open, and a collision is still a failure — it is now a failure that names itself in ~1 s.

## Self-attack — the three most likely ways this change is wrong

1. **"The port-unbound assertion proves the guard runs before the bind."** It does not, and I proved that:
   mutant 10 (PIDFILE-GUARD-AFTER-BIND) leaves all three `ConnectionRefusedError` assertions **passing**, because a
   process that binds, refuses and exits also leaves nothing listening. Ruled out by adding
   `test_pidfile_refusal_precedes_the_bind` (`main:433`), which holds the port so an after-bind guard dies on
   `EADDRINUSE` (rc 1) before it can print anything — it is the ONLY killer of mutant 10.
2. **"`_wait_ready` could hang or hide a failure."** Three ways it could: reading a live child's PIPE (blocks) —
   `_drain` (`main:58`) refuses to read while `proc.poll() is None`; a success-only exit (the defect being fixed) —
   WAITREADY-POLL-DELETED dies; a silent return on failure — WAITREADY-ASSERT-DELETED dies with 2 killers. A fourth,
   leaking a child when the raise happens before a fixture's `yield`, is covered by WAITREADY-NO-KILL.
3. **"The record-slot guard could refuse a legitimate slot, or swallow the error."** A symlink-to-regular slot is
   accepted (`os.stat` follows — STAT-NOFOLLOW dies on exactly that control for the pidfile twin, same predicate);
   an absent slot is created as before (LSTAT-DROPPED dies with 311 errors, i.e. the existence arm is load-bearing
   for every normal request); and the 500 is not a silent skip — RECSLOT-500-SWALLOWED dies.

The remaining packaging risk is first-class in NOT DONE §1: the literal `-r 246bec7` three-file package omits the
staged sibling fixture. Two final-byte composite runs reached and passed all 548 tests; the exact command is still
red and is not presented as accepted.

## DISCREPANCIES

1. **The brief's Scope names `proofs/S0-01/tools/cost_probe.py`; that path does not exist.** `cost_probe.py` lives
   at `tasks/briefs/s0-01-d5j-support/cost_probe.py` (`git ls-tree -r --name-only 218dc2f | grep cost_probe`). I ran
   the committed file read-only and did **not** modify it — the F3 re-measurement needed no new column (the
   `bound-body` column already is the sentence's vector), so nothing outside my three files changed.
2. **The design's "connect → `ConnectionRefusedError`" check does not discriminate ordering** (see Self-attack §1).
   I kept it — it is a cheap "nothing was left listening" control — and added the occupied-port test that actually
   does the work. Reported rather than left as a decorative assertion.
3. **Item 2 said "a dangling symlink" refused with "the exact stderr line", and the PIN accepted one.** On the PIN a
   dangling `--pidfile` symlink STARTED and served (probe row 4); the final bytes refuse it with the same single
   message. That is a behaviour change beyond "fix the hang", pinned by the design and by the test.
4. **Item 4's literal shape was `assert ready and proc.poll() is None, f"…{stdout}"`.** An f-string interpolating
   `proc.stdout.read()` evaluates on SUCCESS too and would block on a live child, so the helper raises
   `AssertionError` with the identical message text after draining only an exited child (`main:113`). Same
   observable message, no hang.
5. **Item 3's "within 2 %" became "0.99-1.06x"** — see Item 3 above. I write what I measured.
6. **The design said "move the pidfile block above `ThreadingHTTPServer`"; I moved the whole block, write
   included.** Checked both consumers first: `run_s0_04_legs.sh:100` waits on `/healthz` and reads the pidfile only
   as a failure-aware liveness check (so an earlier write makes that check *better*), and `pc_backend_restart.sh:10`
   sleeps then curls. The one new residual: a backend that fails to bind now leaves a pidfile behind; the S0-04
   runner already handles a stale pidfile (`[ -d "/proc/$pid" ]` then `/healthz` 200), and the pre-existing
   SIGKILL case leaves the same artefact.
7. **My `[-1]` population (93) is larger than VERIFY-D5l's (82)** because my detector counts every `[-1]` subscript,
   not only record-source ones. Same conclusion, wider net: 3 non-record tails named.
8. **Two imports were removed from the red file** (`http.client`, `time`) — orphaned by replacing its readiness
   loop with the shared helper; pyflakes flagged both. Nothing else in that file's import block changed.

## NOT DONE — first-class

1. **The exact `-r 246bec7`, three-file gate is red** because the archived PIN lacks the staged sibling P5b
   `synthetic_leg` fixture used by this test file. The explicit composite gate is 548 ×2 green; a future checkpoint
   should pin the fixture support so the literal command is self-contained.
2. **SWEEP row 11.4 is not fixed** — documented limit with a measurement (above).
3. **Six `!= MARKER` spellings still evade the walker** (alias, helper function, `operator.ne`, `__ne__`, attribute,
   a differently-named constant). The `OUT OF SCOPE` block at `red:1198-1203` documents these; closing them needs
   data-flow or import resolution.
4. **The AST-backed `AF-AP-61b` TEST_SCREEN row is not mine** (the brief assigns it to the coordinator); I did not
   touch `scripts/ap_screen.py` or `.claude/hooks/`.
5. **`cost_probe.py` untouched** (see DISCREPANCY §1); no new column was needed.
6. **The pidfile guard is check-then-use**: an attacker who replaces the path between `_refuse_non_regular` and
   `write_text` can still land a FIFO there. Closing it structurally needs `os.open(..., O_NONBLOCK)` semantics,
   which the design did not pin and which would change the write path; named here rather than done silently.
7. **The PC continuation re-ran 18 mutants plus three live/plant probes.** Every one was killed/refused on final
   bytes; the inherited report preserves the predecessor's complete 33-row evidence.

## Process census (no `pgrep`, no `ps | grep` — `/proc/<pid>/cmdline` read directly)

```
count=1
2725343 /usr/bin/python3 /home/rocco/agent-factory/proofs/S0-01/tools/scripted_backend.py --bind 127.0.0.1 --port 20201 ...
```

The sole match is the owner's pre-existing PC production backend. It was not started, killed, restarted or
reconfigured by this lane. No scratch D5m backend, pytest process or lane gate remained after verification.

## The pack

`scripts/lane_context.sh -q 'where does the backend open a path at startup or per request' -s main -s _open_record
-s _fingerprint -o …/d5m/pack.md proofs/S0-01/tools/scripted_backend.py` → 141 lines, at
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/d5m/pack.md`. What it changed in the
work: its `graft skeleton` gave the three record call sites and `main`'s span in one read, and its whole-file AP
screen showed the two AF-AP-40 rows BEFORE I wrote the guard, which is why `_refuse_non_regular` uses
`os.lstat`/`os.stat` rather than `.exists()` (a third AF-AP-40 row avoided). Its `graft ask` answer named
`proofs/S0-01/tools/acp_probe.py:L62-L84 _open_regular` — a sibling of exactly this guard elsewhere in S0-01,
which is where the lstat-then-stat shape comes from. `ripwire callers` reported `count=0` for `main`
(subprocess-blind, as documented) and `count=1` for `_fingerprint`; GitNexus `impact` on `main` returned
`"risk": "UNKNOWN"` with `impactedCount: null` — treated as unresolved, not as an all-clear, and the reachability
question was answered instead by `grep -rn pidfile` over `proofs/ scripts/ tests/` (two production launchers +
both fixtures).
