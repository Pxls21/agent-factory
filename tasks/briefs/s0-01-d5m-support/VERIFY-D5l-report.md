# VERIFY-D5l — adversarial grade of lane D5l (S0-01 scripted backend, round 15)

**PIN graded:** `2199747c179c61a051073db853294e9ad072cb70` (checkpoint 8aa), branch
`claude/soundbox-kit-migration-iz1jwf`. Every byte graded from `git archive 2199747 | tar -x -C
.../scratchpad/vd15/pin`, never from the shared working tree. Parent for the scope files =
`8695636` (checkpoint 8w), extracted the same way into `vd15/parent`.

**Verdict: NOT-READY** — 4 blockers, all small fixes. Details at the end.

**Shared-tree discipline.** Read-only git only (`rev-parse`, `cat-file`, `log`, `archive`, `diff`,
`status --porcelain`, `merge-base`, `worktree add/remove`). No stash / checkout / restore / reset /
add / commit / push. `git status --porcelain` on the three scope files was **empty before and after**
every step. Every mutant ran on a scratch copy (`vd15/pin` → `vd15/work`, re-copied per mutant, with
`__pycache__` purged). Every pytest run carried an explicit `--basetemp` under `vd15/`. The one
`git worktree add --detach` (the documented PC-gate recipe; temp index only, the real index untouched)
was removed afterwards — `git worktree list` shows only the repo. Backends: only ones I started, all
reaped; final `/proc/<pid>/cmdline` census (no `pgrep`/`ps | grep`) shows **no live `scripted_backend`
of mine** — the two argv matches are other lanes' bash wrappers (pids 8882, 9733, scratch dirs
`vb14/`, `p5b/`).

**Self-check (item 11).** `report_lint.py` on **this** report at the same `--rev`:
`99 refs — OK 35, NEAR 3, MISS 36, UNCHECKABLE 25, UNRESOLVED 0`. I opened every one of the 36 MISSes:
**all are the tool's token heuristic**, not a wrong ref — a verifier's rows carry mutant names, test
ids, counts and quoted prose in backticks on the same line as the reference, and those are the tokens
the tool then fails to find at the cited line. In each case the cited line's *content* is exactly what
I claim (e.g. `report:181 backend:533` → `rec_body = body`; `report:342 main:342` → the exact-stderr
assertion; `report:397 backend:806` → `server = ThreadingHTTPServer(...)`). Five drafting errors were
caught this way and corrected before submission: four refs that were **parent-** or **mutant-tree**
line numbers rather than PIN lines (the parent's 1190 / 1191 / 1077 / 81, and the EVADE mutant's
`red:1217`, which is `red:1215` on PIN numbering), and one span off by one (`main:77` / `red:53` →
`main:77-78` / `red:53-54`). One UNRESOLVED ref (`run_s0_04_legs.sh:100`, a file that landed after the
PIN) was rewritten to say so. Every `file:line` below was additionally re-derived by `sed -n`/`grep -n`
on the PIN's bytes.

**Load discipline.** Three other verifier lanes ran scratch suites on this 4-core box throughout;
`/proc/loadavg` is pasted beside every timing (it ranged 0.40 → 7.42).

---

## Premise table (verified first-hand)

| premise | how checked | result |
|---|---|---|
| PIN exists / is checkpoint 8aa | `git log -1 2199747` | "S0-01 checkpoint 8aa: the BACKEND landed again (lane D5l, round 15, the PC Hermes lane)" |
| checkpoint scope files == PIN-parent + the PC patch | `git diff 8695636 2199747 -- <3 files>` vs `patch-d5l.diff`, index lines stripped | **IDENTICAL** — 261 lines both |
| FILE IDENTITY (report's table) | `sha256sum` / `wc -l` / `wc -c` on the archive | `scripted_backend.py` `04da144a…89a4b` / 819 / 41010 · `test_s0_01_scripted_backend.py` `cd51ed65…1ef67`… /2177/95972 · `tests/red/…credential_screen.py` `40455da9…b7b03`…/1234/59655 · `cost_probe.py` `a1b86008…5b3ef`/128/4478 — **all four match** |
| the PIN is on origin | `git branch -r --contains 2199747` | **not pushed**; origin head `68fb454` carries the three scope files **byte-identical** (`git diff --stat 68fb454 2199747 -- <3 files>` empty) — the PC gate therefore ran on `68fb454` |
| shared tree state | `git status --porcelain -- <4 scope files>` | **empty** (other lanes hold 11 modified + 20 untracked paths elsewhere; untouched) |
| interpreters | `python3 -c` | venv `/root/venv-agent-factory/bin/python` 3.11 / UCD 14.0.0 · `/usr/bin/python3.13` UCD 15.1.0 |

---

## Item 0 — the mechanical gates, pasted

```
$ report_lint.py tasks/briefs/s0-01-d5l-support/D5l-report.md --rev 2199747… \
    --map backend=proofs/S0-01/tools/scripted_backend.py \
    --map main=tests/test_s0_01_scripted_backend.py \
    --map red=tests/red/test_s0_01_backend_credential_screen.py
report_lint: 34 refs — OK 34, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (at 2199747…)   rc=0
```
**MISS 0 — the lane's claim reproduces exactly.** Red-before, same tool on the previous round's report
at the parent: `37 refs — OK 23, NEAR 5, MISS 6, UNCHECKABLE 1, UNRESOLVED 2 (at 8695636)` rc=1.
Four rounds of this class end here.

```
$ ap_screen.py proofs/S0-01/tools/scripted_backend.py
--- AP_SCREEN over 1 path(s): 5 hits over 1 files ---
AF-AP-40: 2   backend:796 `if args.record_dir.exists() and not args.record_dir.is_dir():`
              backend:800 `if args.record_dir.is_dir() and any(args.record_dir.iterdir()):`
AP-32:    2   backend:390 `return hashlib.sha256(value.encode()).hexdigest()[:12]`
              backend:534 `auth_fp = hashlib.sha256(bearer_token.encode()).hexdigest() …`
AP-51:    1   backend:98  determinism claim
$ ap_screen.py --tests tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py
--- TEST_SCREEN over 2 path(s): 0 hits over 2 files ---   rc=0
```
Every production hit classified **by running it**:

| hit | classification | the run |
|---|---|---|
| AF-AP-40 `backend:796` | **reviewed-safe** — absent record-dir is a genuine no-op (`mkdir(parents=True, exist_ok=True)` at record time). The dangling-symlink hole D5k-F11 named is now closed one line above. | startup class sweep: `record-dir = regular file` → rc 2 `exists but is not a directory`; `record-dir = FIFO` → rc 2 same; `record-dir = dangling symlink` → rc 2 named; `record-dir = symlink → existing dir` → starts and serves |
| AF-AP-40 `backend:800` | **reviewed-safe** — an absent dir is an empty dir; nothing to refuse. | same sweep |
| AP-32 `backend:390` | **reviewed-safe** — `_fingerprint`'s only consumer is the startup log line (`token_fp=5b5d285721a4` in my live start); never compared, never an identity key. | live start, stdout pasted below |
| AP-32 `backend:534` | **screen false positive** — full 64-hex digest, not truncated. | source read |
| AP-51 `backend:98` | **reviewed-safe, guard named** — `test_non_stream_completion_is_pong_and_byte_identical`, `test_stream_completion_frames_are_deterministic`, both in the 539. | full gate |

**TEST_SCREEN de-vacuoused** (the number 0 is worth nothing without it): the same command on the
**parent** bytes returns `3 hits over 2 files` — `AF-AP-60: 1` (the `["grep", "-cP",` argv), `AF-AP-61: 1`
(the source-text regex) and `AP-66: 1` (the direct `sb._normal_forms =` reassignment) — at the
PARENT's lines 1190, 1191 and 1077, which are not PIN lines. All three are gone at the PIN. The screen can fire; it does not.

---

## Gates — reproduced first-hand

```
sandbox, scratch copy of the PIN, /root/venv-agent-factory/bin/python 3.11
  run 1 (load 7.38 → 7.42):  539 passed in 175.19s (0:02:55)   rc 0
  run 2 (load 1.12 → 2.27):  539 passed in 174.01s (0:02:54)   rc 0
red file standalone (inside the mutant campaign, behaviourally identical tree): 200 passed
pyflakes on the three scope files: rc 0
```
Both runs agree; they reproduce the checkpoint's own sandbox lines (`175.08s` / `174.73s`) and the
lane's PC lines (`176.44s` / `176.48s`) within 1.5 s at comparable load.

**PC gate (the one bridge action, item 9).** Clean detached worktree of `68fb454` (scope files
sha256-identical to the PIN, `git status --porcelain` empty, patch **0 B**):
```
$ scripts/pc_suite.sh launch -n 8 -- tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py
launched 20260908T034447Z-68fb454 — base 68fb454… + patch 0B (sha e3b0c44298fc), -n 8
$ scripts/pc_suite.sh wait 20260908T034447Z-68fb454 10
pytest-exit: 0
pytest-summary: 539 passed in 46.50s
```
**Agrees with the checkpoint's PC line** (`539 passed in 46.30s`, run `20260908T025251Z-545a9ff`).
Worktree removed; nothing else touched on the bridge.

---

## Item 1 — D5k F1-F8 closure table

| D5k finding | closed by | red-before I reproduced | the green I reproduced | verdict |
|---|---|---|---|---|
| **F1** file:line discipline (MISS 6) | `report_lint.py` run before submission | `37 refs — OK 23, NEAR 5, MISS 6 … (at 8695636)` rc 1 | `34 refs — OK 34, MISS 0 (at 2199747…)` rc 0 | **CLOSED** |
| **F2** mutant `failed` cells under-report | the table's UQ / RECORDLESS rows re-counted | — | `UQ-REPLACE-BOTH` re-run by me over the red file: **`5 failed, 195 passed in 91.30s`**, all five killers exactly the lane's list (4× `test_credential_pct_encoded_invalid_utf8_separator_returns_400[lone_cont/overlong_lead/ff/surrogate]` + `test_pct_dense_junk_that_now_saturates_is_served`) | **CLOSED** |
| **F3** grep ban fail-open (rc never read) | AST walk, no subprocess (`red:1188-1201`) | parent `TEST_SCREEN`: `AF-AP-60: 1` (parent line 1190) | PIN `TEST_SCREEN 0 hits`; MARKER-GUARD-BREAK → `1 failed` at `red:1215` | **CLOSED** |
| **F4** ban covers one spelling | the AST walk catches any left-hand expression | mutant MARKER-GUARD-EVADE (`_b = …["body"]` / `assert _b != MARKER` at `red:1140,1157`) | **`1 failed in 0.24s`** (the mutant shifts the file +2, so the failing assertion is `red:1215` on PIN numbering) | **CLOSED for the two named spellings; the CLASS is not closed — see F1/F5 below** |
| **F5** served test does not pin the record | `assert json.loads(recs[-1].read_text())["headers"]["x-trace"] == vec` (`red:1233`) | RECORD-HDRVAL-BLANKED passed 537 on the parent (D5k's run, reviewed) | RECORD-HDRVAL-BLANKED (x-trace only) → **`2 failed in 10.62s`**, killers `test_saturating_junk_is_served` + `test_pct_dense_junk_that_now_saturates_is_served` | **CLOSED** |
| **F6** three unlinked extras literals | `assert sb._INVISIBLE_EXTRA == extra` (`main:2100`) + `{ord(c) for c in red._INVISIBLE_EXTRA} == sb._INVISIBLE_EXTRA` (`main:2172`) | — | one-codepoint drift on **each** of the three literals dies: IMPL **2 failed**, ORACLE **1 failed** (`main:2172`), TEST-LITERAL **1 failed** (`main:2100`) | **CLOSED** |
| **F7** cost mechanism falsified | docstring rewritten (`backend:77-82`) | — | harness-equivalence half now TRUE and measured (raw/http 0.97-1.02× over 3 runs); **the NUMBER is still wrong** | **NOT CLOSED — finding F3 below** |
| **F8** `_last_record_text` dead | deleted | parent audit fires (`NO-DELTA in _last_record_text`, parent line 81) | PIN: **0** stale `[-1]`, 82/82 record-tail reads carry a count delta; `grep -rn _last_record_text tests/ proofs/ scripts/` → nothing | **CLOSED** |

---

## Item 2 — the structural `!= MARKER` ban, attacked

The ban is an AST walk (`red:1188-1201`): `ast.Assert` → `ast.walk(node.test)` → `ast.Compare` with an
`ast.NotEq` op and the `Name` `MARKER` anywhere in the comparison. **No subprocess, no regex over
source; the exit code is pytest's own assertion.** The three scratch controls at `red:1203-1211` are
two-sided (a walker that always returns `[]` fails BREAK/EVADE; one that always returns everything
fails POSITIVE) and pin the **line number**, so an off-by-one in reporting dies too.

Real mutant runs (scratch copies):
```
MARKER-GUARD-BREAK  (red:1140  == MARKER -> != MARKER)                 1 failed in 0.18s
MARKER-GUARD-EVADE  (red:1140,1157 -> `_b = …["body"]` / `_b != MARKER`) 1 failed in 0.24s
POSITIVE control (the PIN itself, no mutation)                          1 passed in 0.20s
```
Both failures land on the `assert marker_not_equal_asserts(red_file) == []` line (`red:1215` on PIN
numbering; the EVADE mutant shifts the file by +2).

**Form coverage, measured** (the walker lifted verbatim into a scratch harness, 16 spellings):

| form | caught? |
|---|---|
| `assert json.loads(x)["body"] != MARKER` (BREAK) | **CAUGHT** |
| `_b = …["body"]` / `assert _b != MARKER` (EVADE) | **CAUGHT** |
| `assert MARKER != …` (operand order) | **CAUGHT** |
| `assert (x,) != (MARKER,)` (tuple) | **CAUGHT** |
| `assert (lambda r: r != MARKER)(x)` | **CAUGHT** |
| `assert (_b := …) != MARKER` (walrus) | **CAUGHT** |
| `assert _b == expected` (positive control) | correctly **0 hits** |
| `assert not (x == MARKER)` | **EVADES** |
| `assert x.__ne__(MARKER)` | **EVADES** |
| `M = MARKER` / `assert x != M` (aliasing) | **EVADES** |
| `assert x not in (MARKER,)` | **EVADES** |
| `assert x is not MARKER` | **EVADES** |
| `def _served(r): return r != MARKER` / `assert _served(x)` | **EVADES** |
| `assert operator.ne(x, MARKER)` | **EVADES** |
| `assert x != m.MARKER` (attribute) | **EVADES** |
| `assert x != MARKER_BODY` (a different name) | **EVADES** |

The brief's six named attacks land exactly as it predicted: order and tuple are caught, `not (==)`,
`__ne__`, aliasing and `not in` are not. **Nothing in the file documents the eight that escape** —
finding **F5**.

---

## Item 3 — every served/verbatim path pins the positive record VALUE

Served paths that write a record (`backend:529-536`): `GET /v1/models`, `POST /v1/chat/completions`
(normal and streaming). Record fields: `seq, method, path, headers, body, received_at, t_mono_ns,
remote_addr, authorization_fingerprint`.

Field-by-field pins found by AST/grep on the PIN (all reproduced by mutants below):
`method` `main:183`, `:538` · `path` `main:183`, `:886`, `:1030` · `headers` values `main:1033`,
`main:2041`, `red:1233` · `body` `red:295`, `:445`, `:479-480`, `:668`, `:680`, `:943` · `remote_addr`
`main:197`, `:539` · `authorization_fingerprint` `main:191`.

**The three record-fidelity mutants (the brief's two plus the D5k one), full two-file runs:**

| mutant | ran | failed | killers |
|---|---:|---:|---|
| **RECORD-HDRVAL-BLANKED** (`backend:531`, x-trace value → `""`) | 2 | 2 | `test_saturating_junk_is_served`, `test_pct_dense_junk_that_now_saturates_is_served` |
| **HDRVAL-ALL-BLANKED** ("header NAME kept, value emptied" — the brief's mutant) | 539 | **3** | + `test_short_bogus_bearer_does_not_collapse_records` (`main:1033`) |
| **RECORD-PREV-HEADERS** ("the record carries the previous request's value" — the brief's mutant) | 539 | **2** | `test_saturating_junk_is_served`, `test_pct_dense_junk_that_now_saturates_is_served` (`KeyError: 'x-trace'`) |
| **BODY-RECORD-NULLED** (`backend:533` `rec_body = None`) | 200 (red) | **15** | includes all four NEW body pins: `test_post_content_length_exactly_max_is_accepted`, `test_json_depth_at_limit_is_served`, `test_json_depth_ignores_brackets_inside_strings`, `test_json_depth_handles_escaped_quote` — each fails **only** on the new pin (status and count assertions are unaffected by a nulled body), so all four are load-bearing, not decorative. Run twice: 15 both times. |

**Both brief-mandated mutants die.** One informational gap: `test_get_content_length_zero_accepted_and_recorded`
(`main:1369`) asserts `200 OK` + a record delta and pins nothing of the record's content — outside the
lane brief's literal enumeration (its name is not served/verbatim and its vector is not
credential-shaped) and the GET record's fields are pinned by `main:538` / `main:1030` / `main:1033`,
which the mutants above prove. Not a defect; noted so the audit list is honest.

---

## Item 4 — ONE extras literal

Three copies remain by design (impl `backend:145-152`, oracle `red:90-96`, self-test `main:2096-2098`),
now cross-pinned by two assertions. Regeneration check, run under `/usr/bin/python3.13` (UCD 15.1.0)
with the generator **extracted verbatim from `_parse_invis_ranges`'s docstring**:
```
regenerated == committed range string: True
len(_INVIS_PINNED) = 4315
ten reserved slots [0x2065, 0xFFF0..0xFFF8] all in pinned: True
_INVISIBLE_EXTRA size: 16
```
One-codepoint drift (`0x2065` → `0x2066`) on **each side**, targeted runs:
```
IMPL-EXTRA-DRIFT     (backend:149)  2 failed in 0.31s  — test_invisible_table_is_the_ucd_15_1_class + test_oracle_table_equals_the_impl_table
ORACLE-EXTRA-DRIFT   (red:93)       1 failed in 0.40s  — main:2172
TESTLIT-EXTRA-DRIFT  (main:2098)    1 failed in 0.26s  — main:2100   (my own third-side mutant; the lane ran only two)
```
Item 4 holds in all three directions.

---

## Item 5 — startup refusals, and the CLASS

**The two landed guards are real and exactly pinned.** Live class sweep on the PIN backend
(subprocess, `timeout=10`, elapsed measured):
```
token-file = FIFO                   -> rc=2 elapsed=0.07s  "token file is not a regular file: …"
token-file = directory              -> rc=2 elapsed=0.06s  same message
token-file = dangling symlink       -> rc=2 elapsed=0.06s  "token file not found: …"
token-file = symlink -> FIFO        -> rc=2 elapsed=0.06s  "token file is not a regular file: …"
record-dir = dangling symlink       -> rc=2 elapsed=0.06s  "--record-dir … is a dangling symlink"
record-dir = FIFO                   -> rc=2 elapsed=0.06s  "exists but is not a directory"
record-dir = regular file           -> rc=2 elapsed=0.06s  "exists but is not a directory"
record-dir = symlink -> existing dir-> starts and serves (correct)
```
The FIFO refusal at **0.07 s with no reader on the FIFO** is the proof of "without reading": an
`open()` for read would block forever.

**No false positive:** a `--token-file` that is a *symlink to a regular file* still starts —
`rc=124` at a 3 s timeout, stdout `scripted_backend: listening on http://127.0.0.1:43357/v1 … token_fp=5b5d285721a4`,
stderr empty.

**Red-before reproduced** on the parent backend (sha `660f9941cd96c089…`, the D5k PIN blob) with the
PIN's test files:
```
FAILED tests/test_s0_01_scripted_backend.py::test_token_file_fifo_refuses_startup_without_reading
FAILED tests/test_s0_01_scripted_backend.py::test_dangling_record_dir_symlink_refuses_startup
2 failed in 20.44s          (both by `subprocess.TimeoutExpired … after 10 seconds`)
```
(the lane's line was `2 failed in 20.95s` — agrees.)

**Six surgical mutants prove the guards, their messages, their exit code and their ORDER are all
load-bearing** (each run over the two startup tests):
```
SISREG-DELETED           1 failed, 1 passed in 10.43s   (FIFO test, by timeout)
SISREG-TAUTOLOGY (`and False`) 1 failed, 1 passed in 10.49s
RECDIR-DANGLING-DELETED  1 failed, 1 passed in 10.45s   (symlink test, by timeout)
TOKEN-MSG-DRIFT ("FILE") 1 failed, 1 passed in 0.48s    (exact-stderr assertion)
RC-DRIFT (2 -> 3)        2 failed in 0.47s
GUARD-ORDER (S_ISREG moved after load_token)  1 failed, 1 passed in 10.52s
```

**The CLASS is NOT closed — two members remain, both reproduced: findings F2 and F7 below**
(`--pidfile`, and the per-request record write).

---

## Item 6 — cost prose

`backend:77-82` now reads: *"Bounded worst case: MAX_CONTENT_LENGTH (1 MiB) body with a bound-exceeding
token costs ~0.4 s on the measured PC in both the http.client and raw-socket harnesses (0.378 s each at
1000 KB in one window)"*.

`cost_probe.py`'s **fourth** column is exactly that vector (`cost_probe.py:118-124`: `body_be =
padding + '-%25252541"}'`). Numbers:

| vector @1000 KB | lane's PC run (in the same report) | my sandbox re-runs |
|---|---:|---|
| `ordinary` (200) | **0.715 s** (table) / 0.731 s (dual probe) | 0.377 s (committed harness) · 0.402 / 0.394 / 0.384 s (dual probe ×3) |
| `bound-body` (400) — **the sentence's vector** | **1.864 s** | **1.027 s** (committed harness) · 1.074 / 1.063 / 1.035 s (dual probe ×3) |

Dual-harness check, one backend, one window, 3 runs (load 0.40 → 1.20):
```
run1: ordinary   http.client=0.402s  raw-socket=0.394s  raw/http=0.98x
run2: ordinary   http.client=0.394s  raw-socket=0.384s  raw/http=0.97x
run3: ordinary   http.client=0.384s  raw-socket=0.393s  raw/http=1.02x
run1: bound-body http.client=1.074s  raw-socket=1.061s  raw/http=0.99x
run2: bound-body http.client=1.063s  raw-socket=1.054s  raw/http=0.99x
run3: bound-body http.client=1.035s  raw-socket=1.054s  raw/http=1.02x
```
The **harness half of the claim is true and now measured** (0.97-1.02×, both vectors, three runs).
The **number is not** — finding **F3**.

---

## Item 7 — dead helper, stale `[-1]`

`_last_record_text` is absent from the whole tree (`grep -rn` over `tests/ proofs/ scripts/`: nothing).
AST audit of every `[-1]` subscript over a record source in both files: **82 sites, 82 with a count
delta in the enclosing function, 0 without**. The detector is de-vacuoused — run against the **parent**
it fires exactly once — `NO-DELTA in _last_record_text`, at the parent's line 81. F6/F7 of D5k closed, and DONE row 6's
"[-1] audit" line now holds unconditionally.

---

## Item 8 — the 18-class self-sweep vs SWEEP-tests' backend rows

SWEEP-tests graded the **parent** bytes (`eb07b809…` for main — the D5k PIN blob). Its rows over the two
D5l scope files, and their state at the PIN:

| SWEEP row | verdict there | state at the PIN | lane's self-sweep row |
|---|---|---|---|
| 3.2 / 16.1 `_last_record_text` dead | **E — delete** | **closed** (deleted) | C3/C16 — agrees |
| 3.3 the other 77 `[-1]` (BCS ×52, main ×25) | S — count delta | **holds** (82/82 by my audit) | C3 — agrees |
| 3.4 `frames[-1]`, `payloads[-1]` main:150,153 | S | holds | (not tabled; harmless) |
| 4.3 `!= MARKER` live instances | S (0) | **holds** — 0 across all 15 S0-01 test files (my glob-scoped AST walk) | C4 — agrees |
| **4.4 + 18.1** the lint's file list is hard-coded | **D** (R6b: a third file evades) | **STILL OPEN — reproduced** | C4 says **SAFE**; 18.1 has no row | 
| 7.2 `errors="ignore"` in the oracle | S by design | holds | C7 — agrees |
| **9.1** module-scoped `backend` readiness loop is success-only | **D** (R9a) | **STILL OPEN — reproduced** | C8/C9 say **SAFE** |
| **11.4** `_free_port()` TOCTOU | **D (weak)**, static | **STILL OPEN** (static; I did not reproduce it either) | no row |
| 18.2 module-scoped accumulating fixture state | S today, named residual | holds; the residual (nothing enforces the `n0` idiom) is still unenforced | C15 — agrees |

Three DEFECT rows the sweep found are absent from (or contradicted by) the lane's table. By the brief's
rule that is a blocker — findings **F1** and **F4**, plus the weak **F6b** note.

**The lane's EMPTY-class claims verify** (C6 env-domain, C10 executable skip/xfail, C12 signal installs,
C13 `/proc/<pid>/exe`, C17 hardlink): grep over both files returns **zero** occurrences of
`os.environ|getenv`, `signal.signal|alarm|setitimer`, `/proc/`, `os.link|st_nlink`, and the only
skip-word hit is prose at `red:3`. C8's "broad catches" class is **not** empty in substance: the sole
broad catch is the `except OSError:` of the readiness loop (`main:77`, `red:53`) — which is the 9.1 defect.

---

## Item 10 — mutant table (mine; `ran` = tests EXECUTED, killers from the run)

| # | mutant | ran | failed | killer / qualification |
|---:|---|---:|---:|---|
| 1 | MARKER-GUARD-BREAK (`red:1140`) | 1 | 1 | `test_no_not_equal_marker_assertions` |
| 2 | MARKER-GUARD-EVADE (`red:1140,1157`) | 1 | 1 | same |
| 3 | RECORD-HDRVAL-BLANKED (`backend:531`, x-trace) | 2 | 2 | `test_saturating_junk_is_served`, `test_pct_dense_junk_that_now_saturates_is_served` |
| 4 | HDRVAL-ALL-BLANKED (`backend:531`, every value) | 539 | 3 | + `test_short_bogus_bearer_does_not_collapse_records` |
| 5 | RECORD-PREV-HEADERS (`backend:531`, previous request's headers) | 539 | 2 | the two x-trace pins (`KeyError: 'x-trace'`) |
| 6 | BODY-RECORD-NULLED (`backend:533`) | 200 | 15 | the four NEW body pins + 11 pre-existing; run twice, identical |
| 7 | IMPL-EXTRA-DRIFT (`backend:149`) | 2 | 2 | `test_invisible_table_is_the_ucd_15_1_class`, `test_oracle_table_equals_the_impl_table` |
| 8 | ORACLE-EXTRA-DRIFT (`red:93`) | 2 | 1 | `main:2172` |
| 9 | TESTLIT-EXTRA-DRIFT (`main:2098`) | 2 | 1 | `main:2100` — the third literal, which the lane did not mutate |
| 10 | UQ-REPLACE-BOTH (`backend:320,324`) | 200 | 5 | 4× `…invalid_utf8_separator_returns_400[lone_cont/overlong_lead/ff/surrogate]` + `test_pct_dense_junk_that_now_saturates_is_served` — the lane's row reproduces exactly |
| 11 | PARENT-BACKEND (both startup guards absent) | 2 | 2 | both new startup tests, by `TimeoutExpired` |
| 12 | SISREG-DELETED | 2 | 1 | `test_token_file_fifo_refuses_startup_without_reading` |
| 13 | SISREG-TAUTOLOGY (`and False`) | 2 | 1 | same |
| 14 | RECDIR-DANGLING-DELETED | 2 | 1 | `test_dangling_record_dir_symlink_refuses_startup` |
| 15 | TOKEN-MSG-DRIFT | 2 | 1 | exact-stderr assertion at `main:342` |
| 16 | RC-DRIFT (2 → 3) | 2 | 2 | both startup tests |
| 17 | GUARD-ORDER (S_ISREG after `load_token`) | 2 | 1 | FIFO test, by timeout — ordering is load-bearing |
| 18 | **R6B-THIRD-FILE** (canonical banned form in `tests/test_s0_01_negative_contract.py`) | 2 | **0** | **SURVIVOR — DEFECT (F1)**: `2 passed`, ban green over a live violation |
| 19 | **R9A-STARTUP-FAILURE** (backend exits 2 before `serve_forever`) | 1 | 1 | **SURVIVOR-in-substance — DEFECT (F4)**: dies in 10.41 s with `ConnectionRefusedError`, not the backend's named reason |
| 20 | **PIDFILE-FIFO** (live probe, no code change) | — | — | **DEFECT (F2)**: no listening line, HTTP `TimeoutError` on a bound port, process alive indefinitely |
| 21 | **PIDFILE-DIR** (live probe) | — | — | **DEFECT (F2)**: uncaught `IsADirectoryError`, rc 1, not a named rc-2 refusal |
| 22 | **RECFILE-FIFO** (live probe, planted `000001.json` FIFO) | — | — | **DEFECT (F7)**: handler thread blocks forever, client `TimeoutError` after 6 s, second request 200 |
| 23-30 | walker-form attacks C, D, F, H, I, J, K, L (`not (==)`, `__ne__`, aliasing, `not in`, `is not`, helper fn, `operator.ne`, attribute) | 8 | 0 | **SURVIVORS — documented-limit gap (F5)**: none is caught, none is documented |
| 31-36 | walker-form controls A, B, E, G, O, P (direct, evade, order, tuple, lambda, walrus) | 6 | 6 | all caught with the correct line number |
| 37 | POSITIVE control (`assert _b == expected`) | 1 | 0 | correctly 0 hits — the walker is not a blanket |
| 38 | TOKEN-SYMLINK-TO-REGULAR (false-positive probe) | — | — | correctly **accepted** (starts, serves, empty stderr) |

**38 rows, ≥30 asked. 22 killed with named killers, 11 survivors all classed, 5 live probes.**
Every one on a scratch copy; `git status --porcelain` on the scope files asserted **empty after each**.

---

## FINDINGS — all of them, no severity filtering

### F1 — BLOCKING — SOLID — the `!= MARKER` ban still scopes to two hard-coded files; the sweep's R6b evasion is live at the PIN

- **file:line** `tests/red/test_s0_01_backend_credential_screen.py:1213-1216` —
  `red_file = pathlib.Path(__file__)` / `main_file = red_file.parents[1] / "test_s0_01_scripted_backend.py"`.
- **expected** SWEEP-tests rows 4.4 and 18.1 state the fix in one sentence: *"Replace the regex+2-file
  grep with an AST walk over `tests/test_s0_01_*.py` + `tests/red/test_s0_01_*.py`"*. The lane applied the
  AST half and kept the two-file list; its self-sweep C4 row records the class as **SAFE**.
- **observed / reproduced** — planted the canonical banned form in a third S0-01 test file:
  ```python
  # tests/test_s0_01_negative_contract.py (appended)
  MARKER = {"credential_in_unexpected_location": True}
  def test_vd5l_r6b_third_file_evasion(tmp_path):
      import json
      rec = json.loads('{"body": {"model": "s0-01-pong"}}')
      assert rec["body"] != MARKER
  ```
  `pytest …::test_vd5l_r6b_third_file_evasion …::test_no_not_equal_marker_assertions` → **`2 passed in 0.13s`**.
  The same walker with the sweep's glob scope finds it: `glob-scoped walk finds: [('test_s0_01_negative_contract.py', 451)]`.
- **failing input** the plant above.
- **minimal fix** two lines at `red:1213-1216`:
  ```python
  root = pathlib.Path(__file__).parents[1]
  targets = sorted(root.glob("test_s0_01_*.py")) + sorted((root / "red").glob("test_s0_01_*.py"))
  for p in targets:
      assert marker_not_equal_asserts(p) == [], p
  ```
  **Measured free:** the glob-scoped walk over all 15 S0-01 test files at the PIN returns **0** hits, so
  widening costs nothing today.
- **exact red test** the plant above must make `test_no_not_equal_marker_assertions` fail with
  `('test_s0_01_negative_contract.py', <lineno>)`.

### F2 — BLOCKING — SOLID — `--pidfile` is the third path the backend opens at startup and has no guard: a FIFO there hangs the process forever, after the listening socket is bound

- **file:line** `proofs/S0-01/tools/scripted_backend.py:807-808` —
  `if args.pidfile:` / `args.pidfile.write_text(f"{os.getpid()}\n")`, executed **after**
  `server = ThreadingHTTPServer(...)` at `backend:806` and **before** the listening line at `backend:809`.
- **expected** the round's item 4 closed exactly this class for `--token-file` and `--record-dir`
  (SWEEP-prod #43, the AF-AP-30 read class); the verify brief widens it by name to *"every path the
  backend opens at startup or per request … a FIFO/dir/dangling symlink at EACH — bounded and named, or
  a finding"*. The lane's self-sweep C2 row calls the class **SAFE** on the strength of the token file alone.
- **observed / reproduced** (instrumented probe, control first):
  ```
  pidfile = regular path      listening=True  http_get=200            alive=True  pidfile_exists=True
  pidfile = FIFO              listening=False http_get=ERR TimeoutError alive_after_5.0s=True
  pidfile = dangling symlink  listening=True  http_get=200            alive=True  pidfile_exists=True
  ```
  `TimeoutError` rather than `ConnectionRefused` proves the socket **is** bound — the worst shape: a
  supervisor waiting on the port or the pidfile waits forever, and no request is ever served. A
  directory at `--pidfile` gives an uncaught `IsADirectoryError` traceback, `rc=1`, no named reason
  (`rc=1 elapsed=0.08s stderr='Traceback (most recent call last): …'`).
- **reachability — the flag is passed in production**: `proofs/S0-01/tools/pc/pc_backend_restart.sh:10`,
  `run_s0_04_legs.sh` line 100 (an S0-04 file that landed after the PIN), and both test fixtures (`main:65`, `red:41`).
- **failing input** `--pidfile <path to a FIFO with no reader>`.
- **minimal fix** at `backend:807`, mirroring the token guard the lane just wrote:
  ```python
  if args.pidfile:
      if args.pidfile.exists() and not args.pidfile.is_file():
          print(f"scripted_backend: --pidfile is not a regular file: {args.pidfile}", file=sys.stderr)
          return 2
      args.pidfile.write_text(f"{os.getpid()}\n")
  ```
  (moving the block above `backend:806` as well would keep the port unbound on refusal).
- **exact red test** the sibling of `main:330`:
  ```python
  def test_pidfile_fifo_refuses_startup(tmp_path):
      ...
      os.mkfifo(tmp_path / "pid", 0o600)
      proc = subprocess.run([...,"--pidfile", str(tmp_path/"pid")], capture_output=True, text=True, timeout=10)
      assert proc.returncode == 2
      assert proc.stderr == f"scripted_backend: --pidfile is not a regular file: {tmp_path/'pid'}\n"
  ```
  On the PIN it must fail by `TimeoutExpired`.

### F3 — BLOCKING — SOLID — the cost prose is still wrong: the number belongs to a different vector **and** a different venue than the sentence claims (fourth round of the D5k-F7 class)

- **file:line** `proofs/S0-01/tools/scripted_backend.py:77-82`.
- **expected** D5k-F7's fix: state the measured fact for the vector the sentence names.
- **observed** the sentence describes *"MAX_CONTENT_LENGTH (1 MiB) body with a bound-exceeding token"*
  — `cost_probe.py`'s fourth column — and attaches **0.378 s / "~0.4 s on the measured PC"**:
  - the lane's **own** probe in the **same report** measures that vector at **1.864 s** on the PC
    (min of 5 iterations — a best case, not a load-inflated one): **4.7× the stated number**;
  - my sandbox re-runs of the same vector: **1.027 s** (committed harness) and **1.074 / 1.063 / 1.035 s**
    (dual probe ×3): **2.7×**;
  - **0.378 s is the ordinary 200-serving vector measured in the SANDBOX** — I reproduce it at
    **0.377 s** (committed harness) and 0.384-0.402 s (dual probe) — while the lane's own **PC** number
    for that same ordinary vector is **0.715-0.731 s**. So the venue attribution is wrong too.
  - the superseded parent sentence (*"~2 s on a quiet 4-core box"*) was accurate to **7 %** of the lane's
    own PC measurement of the named vector. This edit made the docstring **less** true, and it
    understates a DoS budget by 4.7×.
- **failing input** `cost_probe.py`, `bound-body` column, 1000 KB row, either venue.
- **minimal fix** replace `backend:78-80` with the measured cells, naming vector and venue:
  *"costs 1.86 s on the PC and 1.03 s in the sandbox (min of 5, `cost_probe.py` column `bound-body` at
  1000 KB); an ordinary 1 MiB body costs 0.72 s / 0.38 s. Harness style is not a factor — http.client
  and a raw socket are within 2 % of each other on both vectors (measured 3× in one window)."*
- **exact red test** none needed (prose): the check is `cost_probe.py` + a diff of the docstring number
  against the `bound-body` 1000 KB cell. A cheap standing gate would be a test that runs the probe at
  100 KB and asserts the docstring's ratio, but that is a design call, not a fix requirement.

### F4 — BLOCKING — SOLID — the module-scoped `backend` fixtures are success-only waits; the sweep's row 9.1 is unfixed and the lane's table records the class as SAFE

- **file:line** `tests/test_s0_01_scripted_backend.py:67-78` and
  `tests/red/test_s0_01_backend_credential_screen.py:43-54` (same shape again at `main:265-277` and
  `main:562-574`). The exit condition is `while time.time() < deadline:` with `except OSError: time.sleep(0.05)`
  (`main:77-78`, `red:53-54`) and **no** `proc.poll()` check, **no** post-loop readiness assertion; the yield at
  `main:79` / `red:55` hands out a possibly-dead backend, and the process's own stderr goes into a
  `stdout=PIPE` nothing ever reads.
- **expected** the repo's own meta-rule — *a wait's exit condition includes failure signatures, never
  success-only silence* — and SWEEP-tests row 9.1, which is a **D** with a reproduction.
- **observed / reproduced (R9a)** — backend made to print a named reason and `return 2` immediately
  before `ThreadingHTTPServer`:
  ```
  FAILED tests/test_s0_01_scripted_backend.py::test_bearer_required_exact_401
  E  ConnectionRefusedError: [Errno 111] Connection refused
  1 failed in 10.41s      (real 0m10.730s — the whole deadline burned)
  ```
  The backend's own message never surfaces. Under the PC `-n 8` gate the `_free_port()` TOCTOU
  (SWEEP 11.4, `main:52,100,654,721,1598`, `red:28`) makes this reachable as a flake whose diagnosis
  points at the client socket.
- **failing input** any startup failure of the backend subprocess (port collision, bad argv, import error).
- **minimal fix** (the sweep's, two lines per fixture):
  ```python
  while time.time() < deadline and proc.poll() is None:
      ...
  assert ready and proc.poll() is None, f"backend failed to start (rc={proc.poll()}): {proc.stdout.read()}"
  ```
- **exact red test** the R9a mutant must fail with that message, not `ConnectionRefusedError`.

### F5 — SOLID — the AST ban catches 6 of 14 spellings and documents none of the 8 it misses, while the report calls the class closed

- **file:line** `red:1188-1201` (the walker) and `red:1185` (its docstring, *"no test uses MARKER != or
  != MARKER as an acceptance check"*); the report's DONE row 1 and SELF-ATTACK §1 say the class is closed
  and "AF-AP-60/61 closed for this component".
- **observed** the 16-form table above: `assert not (x == MARKER)`, `assert x.__ne__(MARKER)`,
  `M = MARKER; assert x != M`, `assert x not in (MARKER,)`, `assert x is not MARKER`, a
  `def _served(r): return r != MARKER` helper, `operator.ne(x, MARKER)` and `x != m.MARKER` all pass.
- **why it is not a live hollow green today** measured: **0** NotEq asserts of any kind in the two files
  and **0** MARKER-named NotEq asserts across all 15 S0-01 test files. This is a documentation defect,
  not an open hole.
- **minimal fix** either one sentence in the test docstring naming what is in and out of scope, or four
  lines extending the predicate to `ast.NotIn`, `ast.IsNot`, and `ast.UnaryOp(ast.Not, ast.Compare(Eq))`
  (aliasing and helper-function forms stay honestly out of scope).
- **exact red test** the C/D/H/I forms as scratch modules must each report ≥ 1 once claimed.

### F6 — SOLID — the 18-class self-sweep is a SAMPLE presented as an enumeration

- **file:line** `D5l-report.md` § "18-class self-sweep", column header *"file:line sample"*.
- **expected** the lane brief item 9: *"…over your test files by AST or grep, **RUN every instance**
  (a mutant or a planted input), and table them"*.
- **observed** every row carries exactly one sample site and, for most rows, the run column is the full
  two-file gate ("539 passed") rather than a per-instance exercise. No row carries an instance COUNT or
  the enumeration method. The parallel sweep lane, over the same two files, enumerates 52 + 25 `[-1]`
  sites, 14 poll loops, 67 presence-gated forms. Consequence: rows **C8** and **C9** assert SAFE over a
  class that contains the reproduced 9.1 defect (F4), and **C4** asserts SAFE over the class that
  contains the reproduced R6b evasion (F1).
- **minimal fix** add a COUNT and the enumeration method to each row, and mark sampled rows
  "sampled N of M" instead of SAFE.
- **F6b (weak, not reproduced by me or by the sweep)** SWEEP row 11.4's `_free_port()` TOCTOU has no row
  in the lane's table at all.

### F7 — SOLID (minor) — the per-request record write is the same unguarded-path class, undocumented

- **file:line** `backend:535-536` — `self.record_dir.mkdir(parents=True, exist_ok=True)` /
  `(self.record_dir / f"{n:06d}.json").write_text(...)`.
- **observed / reproduced** with `--allow-existing-records` and a FIFO planted at the (fully predictable)
  next slot `000001.json`:
  ```
  started: True
  first request: TimeoutError after 6.01s   <-- handler thread blocked on the FIFO
  second request status: 200 (0.00s)
  process alive: True
  ```
  Bounded by `ThreadingHTTPServer` (other requests still served) but the client never gets a response,
  the record is never written, and the sequence numbers show a gap. Named nowhere.
- **minimal fix** one line before the write — `if p.exists() and not p.is_file(): raise OSError(...)` —
  or a sentence in the docstring's startup-guard paragraph declaring it a documented limit.
- **exact red test** plant the FIFO, send one request, assert a response within 5 s.

### F8 — SOLID (nit) — an unexplained docstring edit in the patch

- **file:line** `red:1069` — *"…never called for an invalid-**UTF8** byte-view input"*, changed from
  `invalid-UTF-8`. The file spells it `UTF-8` **20** times and `UTF8` exactly **once** (this line).
- **observed** the same hunk's real change (`monkeypatch.setattr` at `red:1082`, closing an AP-66
  TEST_SCREEN hit at the parent's line 1077) is justified and correct; the hyphen removal traces to no brief
  item and to no registry row. Surgical-changes rule: every changed line should trace to the request.
- **minimal fix** restore the hyphen.

### F9 — SOLID (informational) — what in the report I reviewed but could not reproduce

- The GitNexus `detect_changes` summary (12 symbols / 3 files / risk low) — MCP call on the PC, not
  reproducible from here; not load-bearing for any claim.
- The PC-side process census and its "foreign production `scripted_backend.py` under
  `/home/rocco/agent-factory/…`" note — one bridge action only; reviewed, not reproduced.
- The lane's PC gate lines (`539 passed in 176.44s` / `176.48s`) — I reproduced an equivalent PC run
  (`539 passed in 46.50s` at `-n 8`) and two sandbox runs; the serial PC numbers themselves are reviewed.
- The report's DISCREPANCIES §1-§5 (PIN wording, duplicated load lines, `/tmp` inode exhaustion, the
  skill-reload process deviation, the GitNexus CLI fallback) — all internally consistent and none
  affects a graded claim. §1 is correct: the in-repo brief says `13c1bd2`, the live worktree HEAD was
  `58741bb`; the scope files are byte-identical at both and at `8695636`.

---

## Item 12 — the design question (where the ban belongs), from what I measured

**Both, with the registry screen carrying the class.** Measured basis:

1. The AST walk is the right *mechanism* (it survived BREAK and EVADE where the regex did not) but the
   wrong *home for scope*: its file list is a literal two-path expression inside one component's test
   file, which is precisely the shape SWEEP row 18.1 registers as a class ("a lint whose scope is a
   hard-coded file list") and which F1 reproduces.
2. `scripts/ap_screen.py` already supports non-regex matchers: `screen()` branches on
   `getattr(row[1], "finditer", None)` and falls back to a `.search(text)`-only object — the existing
   `_EmitNoneKwarg` class in `.claude/hooks/edit-snapshot.py:28-57` is exactly that shape, written
   because a regex could not express the tell. So a TEST_SCREEN row can carry an **AST-backed**
   negative-acceptance detector **without** regressing into AF-AP-61 (a source-text pattern).
3. The widening is free and the row would not be noisy: my glob-scoped walk over all 15 S0-01 test files
   returns **0** hits, and the two backend files contain **0** NotEq asserts of any kind.
4. Today's split leaves the two enforcement mechanisms covering disjoint things: TEST_SCREEN bans the
   two *bad implementations of a ban* (AF-AP-60 grep-guard, AF-AP-61 source-regex) but not the
   *assertion class itself*; the in-file test bans the assertion class but only in two files.

**Recommendation:** (a) fix F1 now with the two-line glob — it is the cheap half and it closes the
reproduced evasion; (b) add an AST-backed `AF-AP-61b` TEST_SCREEN row for the negative-acceptance
assertion so every component inherits it, with the in-file test retained as the *executable* gate for
this component (the screen is advisory by design, exit 0 — it can never be the only enforcement).

---

## What I reproduced vs reviewed statically vs deliberately skipped

**Reproduced first-hand (executed or live):** both sandbox gates (539 passed ×2) · the PC gate over the
bridge (539 passed in 46.50s, `-n 8`, clean detached worktree, 0 B patch) · `report_lint.py` on the D5l
report at the PIN (MISS 0) **and** its red-before on the D5k report at the parent (MISS 6) ·
`ap_screen.py` on the backend and both test files, every production hit classified by running it, and the
TEST_SCREEN 0 de-vacuoused against the parent (3 hits) · pyflakes on the three scope files · the
checkpoint-vs-patch byte identity · the FILE IDENTITY table · **38 mutants/probes**, each on a scratch
copy with the shared tree asserted clean after every one · the red-before for both new startup tests on
the parent backend (`2 failed in 20.44s`, both `TimeoutExpired`) · the full startup-path class sweep (11
plantings, elapsed measured) · the pidfile hang with a listening/served control · the record-file FIFO
hang · the 4315-member table regenerated byte-identically from the docstring generator under
`/usr/bin/python3.13` · one-codepoint drift on all three extras literals · the `[-1]` audit (82/82) with
its detector de-vacuoused on the parent · `cost_probe.py` in the sandbox and a 3-run dual-harness probe ·
the R6b third-file evasion and the R9a readiness-loop defect · a false-positive control on the new
S_ISREG guard.

**Reviewed statically, not reproduced:** the lane's PC serial gate lines and its PC process census · the
GitNexus `detect_changes` summary · the lane's `lint_delta --base 58741bb` line (the shared tree carries
other lanes' edits, so re-running it here measures a different delta; pyflakes on the three scope files
is the substantive check and is rc 0) · SWEEP row 11.4's TOCTOU (static in the sweep too).

**Deliberately skipped, with the reason:** the 72-code-point × 2-sink sweep and the 30 000-vector
oracle-vs-impl leak sweep (D5k reproduced both at 432/432 and 0; nothing in this round's diff touches the
screen's algorithm — the diff is a docstring, an import, two startup guards, and test-side assertions) ·
the live redaction/streaming controls (the lane pasted them; the record-fidelity mutants I ran exercise
the same sinks harder) · anything further on the PC beyond the single sanctioned pytest gate.

---

## Shared-tree hygiene (final state)

```
git status --porcelain -- <the 4 scope files>  (at grade start)  -> empty
git status --porcelain -- <the 4 scope files>  (at grade end)    ->  M tests/test_s0_01_scripted_backend.py
git worktree list                                                -> /home/user/agent-factory  02f534d [claude/…iz1jwf]
/proc/<pid>/cmdline census                                       -> no scripted_backend of mine alive
```
**Not mine, and it matters for whoever re-runs this.** Between my first and last `git status`, HEAD moved
`7165157 → 7a848cd → 02f534d` and **another lane put an uncommitted edit into one of the D5l scope files**:
`tests/test_s0_01_scripted_backend.py` now carries a P5b-shaped rewrite of
`test_build_capture_record_roundtrip_check` (it cites *VERIFY-P5a F1*, imports the shared `synthetic_leg`
fixture from `tests/conftest.py` and `pins.PINNED_LEG_FILES` — none of which is in my scope or my
vocabulary). Everything I graded came from `git archive 2199747`, so no finding is affected; but **a
working-tree re-run of the two-file gate right now is not grading the D5l bytes** — use
`git archive 2199747` (or `git show 2199747:<path>`) as this checkpoint's source of truth. This is the
same cross-lane collision the checkpoint message already flags for `test_build_capture_record_roundtrip_check`.

Scratch copies under `vd15/` are removed (only this report remains, under `wf-results-r5/`); no repo file
was written, staged, or committed by me.

---

## VERDICT — **NOT-READY**

Four blockers, none of them in the credential screen itself and none of them expensive:

| # | blocker | fix size |
|---|---|---|
| **F1** | the `!= MARKER` ban still scopes to two hard-coded files — the sweep's R6b evasion reproduces at the PIN (`2 passed` over a live violation) | 2 lines (`red:1213-1216` → the glob), 0 new hits today |
| **F2** | `--pidfile` has no guard: a FIFO there hangs the backend forever with the socket already bound; a directory gives a traceback, not a named refusal. The flag is passed by two production launchers | 4 lines at `backend:807` + one test |
| **F3** | the cost docstring's number is the wrong vector **and** the wrong venue — 4.7× low against the lane's own PC measurement of the vector the sentence names | one sentence at `backend:78-80` |
| **F4** | the module-scoped `backend` fixtures are success-only waits; SWEEP row 9.1 reproduces (10.41 s burned, `ConnectionRefusedError` instead of the backend's reason) and the lane's table calls the class SAFE | 2 lines per fixture + one test |

**Cheapest path to MERGE-READY:** F1 and F4 are literally the two edits SWEEP-tests already wrote out;
F2 is a copy of the token guard the lane just landed, one flag over; F3 is a sentence rewritten from a
number already in the lane's own report. Roughly 15 lines of production/test code, two new tests, one
docstring sentence — then re-run the two-file gate in both venues and re-run `report_lint.py`.

**What is genuinely closed and I could not break:** the AST ban kills both named evasions and its scratch
controls are two-sided · every served/verbatim path pins the record and three independent record-fidelity
mutants die (`3`, `2`, `15` failures with named killers) · the three extras literals are cross-pinned and
a one-codepoint drift on **any** of them dies · the 4315-member table regenerates byte-identically ·
the two new startup guards are exactly pinned in message, exit code and ordering (six mutants), with a
reproduced red-before and no false positive · the dead helper is gone and 82/82 record-tail reads carry
deltas · TEST_SCREEN 0 with a working negative control · `report_lint` MISS 0 · 539 green in two venues,
three runs.

**Nothing in this verdict depends on anything I did not reproduce.**
