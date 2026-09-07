# VERIFY-B5h — round-13 adversarial grade of lane B5h (S0-01 frame tee: the vendored pinned source as the prose oracle, an own-pid census that cannot hang, the zombie semantic, the AF-AP-59 class)

**PIN graded: `63b582c3476aaf93a99f43f69957954467f8aeaf`** (checkpoint 8v, `Mon Sep 7 21:36:16 2026 +0000`), resolved by
`git rev-parse 63b582c` on `claude/soundbox-kit-migration-iz1jwf`. Graded from `git archive 63b582c | tar -x` under the
session scratchpad; the shared tree was read only (`git status --porcelain` empty at start; no stash/checkout/restore/
reset/add/commit/push at any point). **The lane's report header names dispatch `3167608` and says "landing = the
coordinator's checkpoint, made after this report" — F14 is MET this round** (the header no longer claims a commit that
contains the work).

**Box:** 4 cores, shared. **Two other verifiers ran pytest against `tests/test_s0_01_*.py` throughout my grade** (pids
17656/17658 and 18367 observed); load is stated next to every timing. **The PC leg was NOT run by me** — my
non-negotiables forbid the bridge; no BRIDGE READY banner was in scope. This is a sandbox-only, single-worker grade.

---

# PREMISE (every row reproduced by me)

| row | claim | my measurement |
|---|---|---|
| PIN resolves | `63b582c` | `63b582c3476aaf93a99f43f69957954467f8aeaf` ✔ |
| `frame_tee.py` sha256 | `8dfdeb7f…` | `8dfdeb7f704dfd5955cd789a3b8aa8adee5b9aedf71c90bf6cafe03b240cda1e`, 482 lines ✔ |
| `tests/test_s0_01_frame_tee.py` sha256 | `d1be6adf…` | `d1be6adf7ff3bce…` = `d1be6adf7ff3bce4…`, 3144 lines ✔ |
| vendored `acp.rs` sha256 | `44e82861…` | `44e82861763694d2b82d02b15ee100ffd6c78874a2b2282865e6656c539c38f1`, 5030 lines ✔ |
| the two scope files are the only code changed | — | `git show --stat 63b582c` = `frame_tee.py` (25 ±), `B5h-report.md` (81 +), `test_s0_01_frame_tee.py` (505 ±) ✔ |
| the PIN's parent for these two files | 8695636 (D5k) | D5k touched `scripted_backend.py` + backend tests only; `pins.py`, `.claude/hooks/edit-snapshot.py` and `acp.rs` are byte-identical at `934dec1`, `8695636` and `63b582c`, so my `git archive 63b582c` venue and the gates-of-record venue (`934dec1` + two lane files) are equivalent for this suite ✔ |
| parent tee (checkpoint 8s) | `0f2606d` | blob `9df06ad2…`, sha256 `2f0666c2b2a9…` — matches VERIFY-B5g's PIN tee ✔ |
| test count | 101 passed / 93 defs | `101 passed`, `grep -c 'def test_'` = 93 ✔ |

## GATE LINES — mine, verbatim, on my venues

```
# PIN, full suite, static copy of 63b582c            LOAD-BEFORE 0.39 1.22 1.38 / AFTER 0.65 0.93 1.23
101 passed in 187.65s (0:03:07)                      PYTEST_RC=0

# RED venue: PIN tree + parent tee 0f2606d + a one-line PINNED_SHUTDOWN_CLAUSE shim, no -x
#                                                    LOAD-BEFORE 0.51 0.88 1.21 / AFTER 0.56 0.71 1.07
1 failed, 100 passed in 187.62s (0:03:07)            PYTEST_RC=1
FAILED tests/test_s0_01_frame_tee.py::TestDocstringAnchor::test_shutdown_prose_matches_the_pinned_source
E   AssertionError: PINNED_SHUTDOWN_CLAUSE appears 0 times in frame_tee.py, expected >= 3
```

Gates of record I was given and did **not** contradict: sandbox `101 passed in 186.93s`; PC `-n 8` run
`20260907T213117Z-934dec1` `101 passed in 72.81s`; the lane's own `187.47s` / `187.23s`. My `187.65s` at load 0.39
reproduces the sandbox figure.

---

# ITEM 0 — the mechanical checkers (coordinator's mid-task instruction)

## `scripts/report_lint.py` on `B5h-report.md` at `63b582c`

```
report_lint: 26 refs — OK 12, NEAR 4, MISS 10, UNCHECKABLE 0, UNRESOLVED 0 (at 63b582c)
```

Ten MISSes, classified by hand against the PIN's bytes:

| report ref | verdict | evidence |
|---|---|---|
| `test:863`, `test:1028`, `test:1472` (DONE row 2, "docstrings", claimed "by grep on FINAL bytes") | **LANE ERROR ×3** | These are the **parent's** (`0f2606d`) line numbers — `git show 0f2606d:… \| sed -n 863p` = `5 s for it to exit (acp.rs:421-444…` , and F-B5g-11 cites exactly `:863 / :1029 / :1473`. On the FINAL bytes those three docstrings are at **908-909, 1076-1077, 1489-1490**. The report's own header says the refs are by grep on FINAL bytes; for these three it is false. |
| `test:2880` (CENSUS-PGREP-TIGHT killer) | **LANE ERROR** | The AP_SCREEN assertion is at **test:2875** (message 2876). `2880` is a docstring line of the *next* test. |
| `test:2916` (CENSUS-PGREP-X killer) | **LANE ERROR** | The AST-pin assertion is at **test:2904** (message 2905). `2916` is `import sys, json, time` inside a dedent string. |
| `test:600-607`, `test:1145-1152`, `test:2645-2652` (DONE row 3, the inner try/finally) | **NEAR-MISS ×3, typed not pasted** | Actual blocks: **599-608**, **1142-1151**, **2643-2652**. Each is off by 1-3 lines at one or both ends. |
| `test:3122` (old pin, scope fixed) | **heuristic** | 3122 *is* `def test_docstring_pins_the_meaning_not_the_tokens` — a correct def ref the token heuristic cannot see. |
| `test:2862` (AP_SCREEN test) | **heuristic** | 2862 *is* the `def` line. Correct. |

So of the 10 MISSes: **5 are genuine lane errors** (three parent-era docstring refs + two wrong killer lines), 3 are
typed-not-pasted near-misses, 2 are heuristic. **This is the AF-AP-37 class for the third consecutive round** (B5f's F7,
B5g's F-B5g-12, now here) — and the lane brief's own item 8 said "every killer line is the pytest tail".

## `scripts/ap_screen.py` — whole-file screens

`proofs/S0-01/tools/frame_tee.py`: **8 hits over 1 file.** `tests/test_s0_01_frame_tee.py --tests`: **1 hit.**
**None of the nine sits on a line this delta added or changed** (the delta touches `frame_tee.py:16-23`, `:46-53`,
`:428-441` only, plus test-file regions with no hits). Every hit classified:

| AP | site | class | the guard, named |
|---|---|---|---|
| AP-1 ×3 | `frame_tee.py:115` `S0_01_FRAMEDIR`, `:125` `S0_01_AGENT`, `:246` `PYTHONDONTWRITEBYTECODE` | **reviewed-safe** | Both config reads resolve **once at the top of `main()`** into locals and fail closed immediately — `:116-123` exits 64 on unset / empty / not-a-directory, `:126-128` exits 64 on unset. `:246` is an identity-record field, not a config channel. This is exactly the AP-1 remedy ("resolve ONCE at construction, thread explicitly"). |
| AP-32 ×1 | `frame_tee.py:66` `hashlib.sha256()` in `_sha256_file` | **reviewed-safe** | Hashes the interpreter binary for `runtime-identity.json`; there is no store whose form could mismatch. |
| AP-51 ×2 | `frame_tee.py:6-7` "byte-identical relay c2a/a2c" | **reviewed-safe** | Docstring prose, not a dataclass/asdict sink; the byte-identity claim is gated by the relay tests. |
| AF-AP-55 ×1 | `frame_tee.py:231` `os.readlink("/proc/%d/exe")` | **documented limit, pre-existing** | The identity is sampled right after `Popen`; the multi-stage-exec fixture the row asks for is **not** in this suite. Not this lane's scope — carry-forward. |
| AF-AP-58 ×1 | `frame_tee.py:221` `signal.signal(SIGTERM, …)` | **reviewed-safe** | The `try:` begins on the very next statement (`:222`), every local the except path reads is pre-initialised above `:221`, and both properties are pinned by `test_no_statement_between_signal_and_try` and `test_preinit_before_handler_install`; the deterministic long-window test is `test_sigterm_during_sha256_produces_status`. |
| AP-66 ×1 | `tests/test_s0_01_frame_tee.py:920` `timer.daemon = True` | **reviewed-safe** | The attribute belongs to a `threading.Timer` **created two lines above inside the test's own agent-code string**; nothing outside the test can observe it. |

**No defect hit.** No new hit introduced by the delta.

---

# ITEM 1 — F-B5g-1..14 CLOSURE TABLE (one row each)

Legend for "red state": the RED venue is the PIN tree with the parent tee (`0f2606d`) restored **plus a one-line shim
`PINNED_SHUTDOWN_CLAUSE = (…)` at module scope** so the test module still imports. **What the shim hides:** the
constant's own definition site, its wording and its position in `frame_tee.py`. The constant's truth is the oracle
test's job, and I graded that separately (item 2c) — the shim only lets the other 100 tests run against the parent tee.

| # | finding (VERIFY-B5g) | closed? | by what, measured |
|---|---|---|---|
| F-B5g-1 | prose pinned to a token set; DOCSTRING-ORDER / -WRONGEVENT survive | **PARTLY — the hole is still open** | Both of the predecessor's mutants now die (item 2b). **But a false-ORDER constant that satisfies every assertion survives the full suite** — `FALSECONST-ORDER`, `101 passed in 187.90s`. The mechanism (token check on the constant) is unchanged; only its location moved. See **F1**. |
| F-B5g-2 | `test:1517` "buzz-acp's shutdown responsibility" | **CLOSED** | The line now reads `# R1: SIGTERM it (an operator/systemd TERM; buzz-acp SIGKILLs the group instead).` at `test:1534-1535`; the ban regex now runs over `tee_src + test_src` (`test:3118-3120`). `TESTDOC-TERM` dies. |
| F-B5g-3 | AF-AP-59 class not pinned, only one spelling | **PARTLY, and one spelling REGRESSED** | AP_SCREEN import kills CENSUS-WORLD/-PGREP-TIGHT/-PS-E/-PGREP-SHELL; the AST pin kills -PGREP-X/-PROC-WALK. **CENSUS-PGREP-A and CENSUS-PKILL-DQ survive** — and `pkill` double-quoted was killed by the *old* hand-typed pin. See **F2**, **F3**. |
| F-B5g-4 | zombie = false failure | **CLOSED for the zombie; a NEW uncaught path introduced** | Zombie → "already gone", measured; live foreign pid → hard failure, measured. **But the `except ProcessLookupError` the parent had around `os.kill` was dropped** — see **F6**. |
| F-B5g-5 | AP-screen gate block did not describe the delta | **CLOSED** | The report's `lint_delta --base 3167608` line reproduces (item 6). |
| F-B5g-6 | F14: header names a commit without the work | **CLOSED** | Header names `3167608` as *dispatch* and says landing = the coordinator's checkpoint. |
| F-B5g-7 | pipe closes after the assertions | **CLOSED — measured, not argued** | PIDFILE-ABSENT at all three sites: PIN `LEAKED=[]`, parent `LEAKED=[(13,pipe:…),(15,pipe:…)]`. Item 3a. |
| F-B5g-8 | site 3's kill path unreachable | **NOT CLOSED — the fix cannot work by construction** | `GRANDCHILD-UNKILLED-S3` still **SURVIVES** on the PIN (`1 passed in 61.61s`), and instrumentation shows the site-3 grandchild is `state=Z` at census time even with `range(6000)`. See **F4**. |
| F-B5g-9 | the census can hang | **see item 5** | |
| F-B5g-10 | F4 test's docstring misstates its scope | **CLOSED** | Docstring now says "BOTH scope files (tee source + this test file)"; the code reads `all_src = src + "\n" + Path(__file__).read_text()` at `test:3139`. |
| F-B5g-11 | `:421` off by one; "for it to exit" | **CLOSED IN THE BYTES, NOT PINNED** | All six sites now read `:422-444` / "for the child to exit". **But `CITE-421`, `CITE-421-TEST` and `CITE-KPG-2324` all survive the full suite** — nothing asserts the citations. The brief required exactly this pin. See **F5**. |
| F-B5g-12 | killer lines wrong / red-before misattributed | **NOT CLOSED** | 5 genuine wrong refs this round (item 0), plus **DOCSTRING-ORDER's killer line is wrong in kind** — see **F7**. |
| F-B5g-13 | premise shift (INFO) | n/a | My own premise held: `git status --porcelain` empty at start and at every checkpoint. |
| F-B5g-14 | carry-forwards (INFO) | untouched | F16 / F18 / F-B5e-18 remain out of scope; AF-AP-55 at `frame_tee.py:231` (item 0) is the same family. |

## Every new/changed test on the RED venue (parent tee + shim), individually

| test | on the parent tee | label |
|---|---|---|
| `test_shutdown_prose_matches_the_pinned_source` (NEW) | **RED** — `PINNED_SHUTDOWN_CLAUSE appears 0 times in frame_tee.py, expected >= 3` (test:3104) | **genuine-red** |
| `test_docstring_pins_the_meaning_not_the_tokens` (CHANGED: `all_src`) | GREEN | **CONTROL** — its genuine-red is the mutant `TESTDOC-TERM` (killed, test:3141) |
| `test_grandchild_cleanup_is_own_pid_scoped` (CHANGED: AP_SCREEN import) | GREEN | **CONTROL** — genuine-red = `CENSUS-WORLD` / `-PGREP-TIGHT` / `-PS-E` / `-PGREP-SHELL` (killed, test:2875) |
| `test_kill_calls_only_at_allowed_sites` (NEW) | GREEN | **CONTROL** — genuine-red = `CENSUS-PGREP-X` / `-PROC-WALK` (killed, test:2904) |
| `test_zombie_grandchild_is_already_gone` (NEW) | GREEN | **CONTROL vs the tee; genuine-red vs the parent HELPER** — reverting the helper to the F13 semantic gives `AssertionError: pid 20979 is not the grandchild (cmdline: )`, `1 failed in 1.83s`; PIN control `1 passed in 1.71s` |
| `test_never_reading_client`, `test_grandchild_never_closes_sigterm_required`, `test_stdin_reader_done_false_when_client_never_closes` (docstrings only) | GREEN | **CONTROL** (prose-only change) |
| `test_grandchild_keeps_tee_alive`, `test_concurrent_main_thread_status_vs_pump` (census refactor + `range(6000)`) | GREEN | **CONTROL** — genuine-red = `PIDFILE-ABSENT-S1/-S3` (killed, test:117) |

**The red state is one test, not a suite.** Nothing about the parent *tee* makes the census, AST, AP_SCREEN or zombie
work go red — those are test-file-only changes whose red-before can only be a mutant, and I ran every one.

---

# ITEM 2 — THE ORACLE TEST ATTACKED

## 2(a) ORACLE-SHA-MISMATCH — the premise fires FIRST, never a silent pass

Two byte changes in a **scratch copy** of the vendored `acp.rs` (the repo's copy was never touched):

```
ORACLE-SHA-MISMATCH    KILLED  0.5s   (one added space inside a comment)
E   AssertionError: vendored acp.rs sha256 mismatch:
    7447887286ed62ddfbd76e9518d31e552b7e41339f27bb84b5ff10c47010997d != 44e82861763694d2b8…
    tests/test_s0_01_frame_tee.py:3013

ORACLE-SHA-LOUD        KILLED  0.3s   (a byte change that ALSO breaks a derived fact: adds `// SIGTERM SIGTERM SIGTERM`)
E   AssertionError: vendored acp.rs sha256 mismatch:
    21d15a0d71bf9b5605ec05d3208e3e771ef334f94bb1e5db81cb2a6736e46404 != 44e82861763694d2b8…
    tests/test_s0_01_frame_tee.py:3013
```

The second is the one that matters: even when the mutation would *also* trip `oracle.count("SIGTERM") == 0`,
the **sha assertion at `test:3013` is what fires** — the premise is genuinely first. **PASS.**

The derived facts themselves I re-derived independently (my own reader, three interpreters, §item 6):
`SIGTERM` count **0** · `fn kill_process_group` at **:2323** · `pub async fn shutdown` at **:422** ·
kill line **< ** `from_secs(5)` line · exactly **one** `from_secs(5)` before `#[cfg(test)] mod tests`. The
lane's derivation reproduces.

## 2(b) The five docstring mutants — each MEASURED (the lane ran two, inferred three)

| mutant | what | result | killer (line = the mutated file's) |
|---|---|---|---|
| DOCSTRING-ORDER | the predecessor's false-ORDER *docstring* (SIGTERM first, killpg after 5 s) | **KILLED** | `PINNED_SHUTDOWN_CLAUSE appears 2 times in frame_tee.py, expected >= 3` (`test:3104`) — **not** the line the lane's table names |
| DOCSTRING-WRONGEVENT | the bound on the wrong event, in the *docstring* | **KILLED** | same assertion, `test:3104` |
| DOCSTRING-HYBRID | killpg present, "the SIGTERM path is what bounds a wedged leg" | **KILLED ×2** | `test:3104` + `module docstring does not state SIGKILL cannot be handled` (`test:3132`) |
| COMMENT-TERM | both R1 comments → "SIGKILLs the group after 5 s" | **KILLED ×2** | `source says 'SIGKILLs the group after 5 s'` (`test:3141`) + the oracle test |
| TESTDOC-TERM | one *test* docstring → "SIGKILLs the group after 5 s" | **KILLED ×2** | `test:3141` (the `all_src` extension — this is F-B5g-10's fix doing real work) + the oracle test |
| DOCSTRING-TERM (B5f row 27) | the pre-F3 wording restored | **KILLED ×2** | `test:3104` + `module docstring does not name killpg` (`test:3131`) |

**Both mutants the lane "inferred" are in fact killed — but by a different assertion than the report names.**
See **F7**.

## 2(c) The constant's binding to the source — **it is a token check in disguise**

The tie is five `in` tests on the string (`test:3081-3095`):

```python
assert "SIGKILL" in PINNED_SHUTDOWN_CLAUSE
assert "killpg"  in PINNED_SHUTDOWN_CLAUSE
assert "first" in PINNED_SHUTDOWN_CLAUSE and "then waits" in PINNED_SHUTDOWN_CLAUSE
assert "5 s" in PINNED_SHUTDOWN_CLAUSE
assert "for the child to exit" in PINNED_SHUTDOWN_CLAUSE
```

**Nothing joins the clause to the derived `kill_line < wait_line`.** The derived order is computed at
`test:3068-3076` and then never compared to the prose. So I wrote the false constant the design was supposed
to make impossible — **FALSECONST-ORDER**, the order REVERSED (wait first, then kill), propagated to all six
sites so the count assertions still hold:

```python
PINNED_SHUTDOWN_CLAUSE = (
    "buzz-acp waits up to 5 s for the child to exit first and then waits"
    " no more before it SIGKILLs the group (killpg)"
)
```
Contains `SIGKILL` ✔ `killpg` ✔ `first` ✔ `then waits` ✔ `5 s` ✔ `for the child to exit` ✔; trips neither
blacklist regex.

```
FALSECONST-ORDER       survived-named    0.4s | 2 passed, 99 deselected in 0.22s
FALSECONST-ORDER       FULL-SUITE SURVIVED  188.1s | 101 passed in 187.90s (0:03:07)
```

It is false in the same maximal way DOCSTRING-ORDER was: `grep -c SIGTERM acp.rs` is 0 and the source kills
*before* it waits. A reader of the mutated tee budgets a 5 s grace period that does not exist. **This is
F-B5g-1, unchanged in mechanism and merely relocated from the docstring to the constant.** → **F1.**

Related shape, also measured: **SITECOUNT-DUP** — the pin is a *file-wide count* (`>= 3`), not a per-site
presence check. Deleting the clause from the module docstring (replacing it with false SIGTERM-first prose)
and duplicating the clause into a third comment keeps `tee_count == 3`:
```
SITECOUNT-DUP          FULL-SUITE SURVIVED  188.0s | 101 passed in 187.79s (0:03:07)
```
→ **F13.**

Positive controls that the constant check *does* bite when the constant alone changes:
```
CONST-ORDER        KILLED 0.5s | PINNED_SHUTDOWN_CLAUSE does not state 'first ... then waits'  test:3086
CONST-WRONGEVENT   KILLED 0.3s | same assertion, test:3086
```

## 2(d) A SEVENTH site — a false sentence beside the correct clause: **nothing catches it**

Added to the tee's module docstring, immediately after the (correct) clause:

> `A wedged leg therefore gets a 5 s grace period in which it may still flush, and buzz-acp sends SIGTERM
> before that grace period starts.`

```
SEVENTH-SITE           survived-named 0.3s | 2 passed, 99 deselected in 0.07s
UNION-DOCROT           FULL-SUITE SURVIVED 188.1s | 101 passed in 187.91s (0:03:07)   (SEVENTH-SITE + the three citation mutants together)
```
**Residual, honestly:** the design is *additive* — it pins that the true clause is present N times, never that
nothing false is present. Only two blacklist regexes ("SIGKILLs the group after 5 s", "buzz-acp's shutdown
responsibility") guard the negative direction, and the sentence above matches neither. → **F12.**

## 2(e) The derived citations — `:422` → `:421` does **NOT** die

```
CITE-421        (tee docstring   :422-444 -> :421-444)  survived-named  | 2 passed
CITE-421-TEST   (test docstring  :422-444 -> :421-444)  survived-named  | 2 passed
CITE-KPG-2324   (tee docstring   :2323-2328 -> :2324-…) survived-named  | 2 passed
UNION-DOCROT (all three + SEVENTH-SITE) FULL SUITE      SURVIVED 101 passed in 187.91s
```

The test derives `sd_start`/`kpg_start` and asserts **the derived values** (`sd_start == 422` at `test:3078`,
`kpg_start == 2323` at `test:3079`) — it never checks that any docstring **cites** them. The comment at
`test:3077` says *"The docstrings/comments cite acp.rs:422-444 and :2323-2328"*; that is a claim the code does
not check. The lane brief required precisely this ("assert every docstring/comment citation in BOTH scope
files cites exactly those ranges — this fixes F-B5g-11's `:421` **by construction**") and the DONE table
repeats the claim. **The bytes are right today; nothing holds them right.** → **F5.**

---

# ITEM 3 — THE CENSUS HELPER `_kill_own_grandchild`

## 3a. PIDFILE-ABSENT at all three sites, with the fd listing (F-B5g-7)

Instrument: a `pytest_runtest_call` **hookwrapper** in the venue's `conftest.py` that snapshots
`/proc/self/fd` pipe links before and after the test's call phase and appends the delta to a log. Run
individually per site, PIN venue and PARENT venue (`0f2606d` test file + tee, sha256 `b046bc24a6ee…` /
`2f0666c2b2a9…`), each with its own `--basetemp`.

```
PIDFILE-ABSENT-S1 [pin] rc=1    3.6s | E AssertionError: agent never wrote grandchild.pid  (test:117)
    FD-CENSUS test_grandchild_keeps_tee_alive              pipes_before=3 pipes_after=3 LEAKED=[]
PIDFILE-ABSENT-S2 [pin] rc=1   15.7s | E AssertionError: agent never wrote grandchild.pid  (test:117)
    FD-CENSUS test_grandchild_never_closes_sigterm_required pipes_before=3 pipes_after=3 LEAKED=[]
PIDFILE-ABSENT-S3 [pin] rc=1   61.6s | E AssertionError: agent never wrote grandchild.pid  (test:117)
    FD-CENSUS test_concurrent_main_thread_status_vs_pump    pipes_before=3 pipes_after=3 LEAKED=[]

PIDFILE-ABSENT-S1 [par] rc=1    3.6s | same assertion
    FD-CENSUS test_grandchild_keeps_tee_alive              pipes_before=3 pipes_after=5 LEAKED=[('13','pipe:[457218]'),('15','pipe:[457219]')]
PIDFILE-ABSENT-S2 [par] rc=1   15.6s | same assertion
    FD-CENSUS test_grandchild_never_closes_sigterm_required pipes_before=3 pipes_after=5 LEAKED=[('13','pipe:[456532]'),('15','pipe:[456533]')]
PIDFILE-ABSENT-S3 [par] rc=1   45.6s | same assertion
    FD-CENSUS test_concurrent_main_thread_status_vs_pump    pipes_before=3 pipes_after=5 LEAKED=[('13','pipe:[459016]'),('15','pipe:[459017]')]
```

**F-B5g-7 is CLOSED, measured at the fd table, not argued.** All three sites die at `test:117` (the lane's
cited line is exact); the PIN leaks nothing where the parent leaks the tee's two pipes every time.
*(Correction I owe: my first version of this conftest used a plain `pytest_runtest_call` hook, which runs the
test body twice; the failing runs above are unaffected because the assertion aborts the hook chain, but I
re-took the passing control with a `hookwrapper` — see F16.)*

## 3b. GRANDCHILD-UNKILLED — sites 1 and 2 die, **site 3 still does not**

```
GRANDCHILD-UNKILLED       KILLED  5.6s | grandchild pid 2306 still alive after kill  test:156   (site 1)
GRANDCHILD-UNKILLED-S2    KILLED 17.6s | grandchild pid 2330 still alive after kill  test:156   (site 2)
GRANDCHILD-UNKILLED-S3 [pin] rc=0 61.8s | 1 passed, 100 deselected in 61.61s        <-- SURVIVES
GRANDCHILD-UNKILLED-S3 [par] rc=0 45.6s | 1 passed,  97 deselected in 45.36s        <-- survives, as F-B5g-8 found
```

Instrumented branch trace (a logging line inserted at the top of the helper, all three sites in one run):
```
BRANCH pid=21816 cmdline='/usr/local/bin/python3 -c import time; t' state=S  t=34758.6   site 1  (LIVE)
BRANCH pid=21822 cmdline='/usr/local/bin/python3 -c import time; t' state=S  t=34773.8   site 2  (LIVE)
BRANCH pid=21867 cmdline=''                                        state=Z  t=34835.2   site 3  (ZOMBIE)
```
**Site 3's grandchild is a zombie at census time even with `range(6000)`**, so the helper takes the
already-gone branch and the kill is never reached. The reason is structural and cannot be fixed by
lengthening: the test cannot reach its `finally` until `tee_proc.wait(timeout=30)` returns, the tee cannot
exit until its a2c pump sees EOF, and a2c EOF *is* the grandchild's death. **The grandchild is guaranteed
dead before the census at this site.** → **F4.** (Cost of the change that bought nothing: site 3 alone
45.4 s → 61.4 s; the three grandchild tests 65 s → 84 s per round over 20+20 rounds.)

## 3c. The zombie red test, and its NEGATIVE

```
ZOMBIE-OLDSEMANTIC (helper reverted to the F13 assert)  rc=1 2.0s
    E AssertionError: pid 20979 is not the grandchild (cmdline: )     1 failed, 100 deselected in 1.83s
ZOMBIE control [PIN as-is]                              rc=0 2.0s   1 passed, 100 deselected in 1.71s
```
Genuine-red reproduced, exactly the message the lane reports. *(The lane calls this a "standalone repro
against parent tee 736bb94"; the tee is irrelevant — it is the parent HELPER's semantic, and 736bb94 is
B5g's parent, not this lane's. Mislabel only.)*

**The negative direction, constructed as the brief asks** (driver imports the real `_kill_own_grandchild`;
every process is one I spawned and is killed by pid):
```
1 LIVE-FOREIGN: AssertionError: refusing to kill a foreign pid 22309 (cmdline: sleep 30 , state: S)
   victim 22309 still alive after the helper ran: True          <-- the foreign pid was NOT signalled
2 ZOMBIE (state=Z): no exception (already gone) -- CORRECT
3 PROCESSLOOKUP: UNCAUGHT ProcessLookupError: [Errno 3] No such process
4 PERMISSIONERROR: UNCAUGHT PermissionError: [Errno 13] Permission denied
```
Rows 1-2 are the fix working. Rows 3-4 are **F6**: the parent wrapped the kill in `except
ProcessLookupError: pass` (`0f2606d` test:544-546); the PIN's helper has **no guard at all** around
`os.kill(gc_pid, sig.SIGKILL)` (`test:141`), so the benign race the whole finding was about — grandchild
alive at the cmdline read, reaped before the kill — now raises instead of passing. `PermissionError` on the
identity read (`test:120`) is uncaught as it was before (F-B5g-4's second half, not fixed). Rows 3-4 are
**SIMULATED** (a narrowly-patched `open`); the mechanism is primary-source visible at `test:118-141` and the
patch only supplies the timing I cannot force on this box.

---

# ITEM 4 — THE AF-AP-59 CLASS

Registry signature, read from primary source (`.claude/hooks/edit-snapshot.py:179`):
```
["']pgrep["']\s*,\s*["']-f["']|\bpgrep\s+-f\b|["']ps["']\s*,\s*["']-e[a-z]*["']
```
**There is no `pkill` alternative in it.** The pin the delta deleted (`needle_pkill = '"pki' + 'll"'`) had one.

## All six CENSUS spellings + two of mine, each MEASURED

| mutant | census it reintroduces | result | pin that fired |
|---|---|---|---|
| CENSUS-WORLD | `subprocess.run(["pgrep", "-f", …])` | **KILLED** | AP_SCREEN, `test:2875` |
| CENSUS-PGREP-TIGHT | same, two spaces removed | **KILLED** | AP_SCREEN, `test:2875` |
| CENSUS-PS-E | `ps -eo pid,args` + filter | **KILLED** | AP_SCREEN, `test:2875` |
| CENSUS-PGREP-SHELL (mine) | `subprocess.run("pgrep -f time.sleep", shell=True)` | **KILLED** | AP_SCREEN 2nd alternative, `test:2875` |
| CENSUS-PGREP-X | `pgrep -x python3` + `/proc` filter + `os.kill` | **KILLED** | AST pin, `test:2904` |
| CENSUS-PROC-WALK | `os.listdir("/proc")` + `os.kill` | **KILLED** | AST pin, `test:2904` |
| **CENSUS-PGREP-A** | `subprocess.run(["pgrep", "-a", "-f", "time.sleep"])` | **SURVIVES** | none — the `-a` between `pgrep` and `-f` breaks alternative 1, and there is no literal `pgrep -f` for alternative 2 |
| **CENSUS-PKILL-DQ** (mine) | `subprocess.run(["pkill", "-f", "import time; time.sleep"])` | **SURVIVES** | none — **and the deleted hand-typed pin killed exactly this** |
| CENSUS-PKILL-SQ | single-quoted `pkill` | **SURVIVES** | none (it survived before too) |
| CENSUS-ENUM-ONLY | `/proc` walk, **no kill** | **SURVIVES** | none — the documented limit |

**The lane's report asserts "CENSUS-PGREP-A … AP_SCREEN (regex matches `"pgrep"` + `"-f"`)" as an INFERENCE.
Measured, the inference is false.** → **F3.** And **CENSUS-PKILL-DQ is a coverage REGRESSION**: a
world-scoped `pkill -f` — which *kills* every matching process on the box, the worst member of the class —
was caught by the old two-literal pin and is not caught now. → **F2.**

**The ENUMERATE-only limit is documented** — `test:2867-2869` ("Limit: a census that only ENUMERATES the
world without killing is out of the AST pin's reach"), report SELF-ATTACK #2, and the lane brief. Confirmed
present and accurate.

## The AST pin attacked — **every evasion I tried passes**

| mutant | shape | result |
|---|---|---|
| KILL-ALIAS | `from os import kill as _k` … `_k(pid, SIGKILL)` | **SURVIVES** — the pin matches only `ast.Attribute` on `Name('os')` |
| KILL-PTHREAD | `sig.pthread_kill(...)` | **SURVIVES** |
| KILL-SUBPROC | `subprocess.run(["kill", "-0", …])` | **SURVIVES** |
| KILL-SENDSIGNAL | `Popen(...).send_signal(SIGKILL)` on a process the census did not identify | **SURVIVES** |
| **KILL-MODULE-LEVEL** | `os.kill(...)` at **module scope** | **SURVIVES** — the pin walks only `FunctionDef`/`AsyncFunctionDef` bodies (`test:2886-2903`); module-level, class-body and comprehension-scope code is never examined |
| **KILL-LAMBDA** | `os.kill` inside a `lambda` at class scope | **SURVIVES** — same hole |

The first four are the same class as the documented limit (an evasion by spelling), and the lane brief itself
said "the class cannot be closed by text". **KILL-MODULE-LEVEL and KILL-LAMBDA are different**: they are
holes in the *implementation* of the pin, not in its concept — an `os.kill` written literally as `os.kill`
escapes simply by not living inside a `def`. Not documented anywhere. → **F3**.

`_KILL_SITES` itself (`test:49-54`) is dead and its comment is self-contradictory:
```python
_KILL_SITES = frozenset({
    "_kill_own_grandchild",
    # …
    # Only these two functions in the file use bare os.kill:
})
```
The set holds one name, the comment promises two and names none, and the pin hard-codes
`fname == "_kill_own_grandchild"` separately at `test:2891`, so the allow-list can never change the verdict.
→ **F11.**

---

# ITEM 5 — F-B5g-9, THE HANG

## The mechanism is REPRODUCED — and it is **still live on the PIN**

A bounded probe with the verifier's exact shape (agent consumes the handshake frame, closes its a2c side with
nothing written, exits; the test holds the tee's stdin write end and blocks on `stdout.readline()` — site 3's
shape at `test:2606-2607`), 12 s watchdog, tee SIGKILLed by pid afterwards:

```
### PIN tee ###
PIN      HANG: readline still blocked at 12 s
         tee pid 23544 state=S threads=[23544, 23547]
           tid 23544 wchan=hrtimer_nanosleep      <- the `while ti.is_alive(): time.sleep(0.1)` drain loop
           tid 23547 wchan=anon_pipe_read         <- the c2a reader, blocked on the tee's stdin
           TEST holds fd 4 -> pipe:[466837]
           TEE  fd 0 -> pipe:[466837]             <- the SAME pipe: the test holds the write end
           TEE  fd 1 -> pipe:[466838]
### parent tee ###
PARENT   HANG: readline still blocked at 12 s     (identical wchan/fd table, pipe:[466911])
```

This is F-B5g-9's cycle, byte for byte against its fd/wchan evidence, and it forms on the PIN exactly as on
the parent. **The delta does not close the hang class.** → **F9.**

## The structural pin the design mandated was not built

Lane brief item 4: *"add a structural pin: no `.stdout.read`/`.stderr.read`/`.readline(` on a tee `Popen`
outside a bounded reader helper"*, and *"close `tee_proc.stdin` BEFORE any wait on the tee's exit or output
where the test no longer writes"*. Mechanical enumeration of every test that reads its own source:

```
reads Path(__file__).read_text():
   test_docstring_pins_the_meaning_not_the_tokens      (line 3140)
   test_grandchild_cleanup_is_own_pid_scoped           (line 2870)
   test_kill_calls_only_at_allowed_sites               (line 2885)
   test_shutdown_prose_matches_the_pinned_source       (line 3101)
occurrences in the file: `.stdout.read` 16, `.readline(` 27, `communicate(` 2
inside any assert statement: False for every one of them
the words "blocking" and "bounded reader" occur 0 times in the file
```

So the brief's three probe shapes — `tee_proc.communicate()` without timeout, `wait()` while stdin is open,
`stdout.read()` in a fixture — **all pass, because there is nothing to pass**. And site 3 still holds stdin
open across `tee_proc.stdout.readline()` at `test:2606-2607` and across the whole 45 s spin loop: the exact
configuration the probe above deadlocks. The report's DONE row 4 ("No blocking reads on tee_proc.stdout/
stderr **inside the census**. stdin closed in finally") is true and beside the point — the deadlock is
upstream of the census, which is what F-B5g-9's own "minimal fix (code)" said. **The pin is not in the
report's NOT_DONE either.** → **F9.**

## The 20 + 20 pytest rounds the brief asked for

Three grandchild tests, 4 concurrent, per-run hard timeout (a TIMEOUT would be reported as a hang and the
process SIGKILLed by pid):

```
PARENT venue (0f2606d)  LOAD-BEFORE 3.09 2.74 2.11 / AFTER 7.94 6.31 3.95
   rounds 1-20 all rc=0, 63.8-67.0 s each
   SUMMARY vb13par: 20 rounds, 0 hang(s), 0 non-hang failure(s), wall 330s
PIN venue               LOAD-BEFORE 7.18 6.20 3.94 / AFTER 6.04 6.71 5.06
   rounds 1-20 all rc=0, 81.3-87.8 s each
   SUMMARY vb13mut: 20 rounds, 0 hang(s), 0 non-hang failure(s), wall 423s
```

**Neither venue hangs at the pytest level in 20 rounds** — because the tests' own agents always write the
handshake before exiting, so the tee always has something to send. The hazard needs an agent that dies
before writing (which a mutant, or a real hermes-acp failure, supplies), and my probe shows the cycle closes
instantly when it does. I therefore do **not** grade the fix on "no hang observed"; I grade it on the direct
reproduction above. *(Also visible here: the PIN's three-test round costs +19 s over the parent's — the
`range(6000)` change of F4.)*

---

# ITEM 6 — THE GATES THE LANE SKIPPED

## Cost probe — 15 reps × 3 batches, PIN and PARENT tee back-to-back in one window

11-frame real-leg shape (3 c2a in, 8 a2c out), full spawn→exit wall clock.
```
PIN     sha256 8dfdeb7f704dfd59        PARENT  sha256 2f0666c2b2a91a02
LOAD-BEFORE 2.77 5.29 4.73             LOAD-AFTER  2.73 5.19 4.70
PIN     batch0 {"reps": 15, "median": 0.0591, "min": 0.0545, "max": 0.1618}
PARENT  batch0 {"reps": 15, "median": 0.0592, "min": 0.0545, "max": 0.1621}
PIN     batch1 {"reps": 15, "median": 0.0585, "min": 0.0549, "max": 0.1815}
PARENT  batch1 {"reps": 15, "median": 0.0631, "min": 0.0541, "max": 0.0721}
PIN     batch2 {"reps": 15, "median": 0.0654, "min": 0.0535, "max": 0.1743}
PARENT  batch2 {"reps": 15, "median": 0.0637, "min": 0.0560, "max": 0.1715}
```
Per-batch PIN/PARENT ratio **1.00× / 0.93× / 1.03×**; median-of-medians 0.0591 vs 0.0631 = **0.94×**.
**No measurable tee-runtime cost** — the lane's inference is correct, now measured. **The SUITE cost is a
different story:** site 3 alone 45.4 s → 61.4 s, the three grandchild tests 65 s → 84 s per round, the full
suite ~170 s (B5g, 98 tests) → ~188 s (101 tests). Essentially all of the +16 s buys nothing (F4).

## 3.12 / 3.13 standalone pins + the SIGTERM window

The PIN's own assertions re-implemented standalone (`vb13py.py`), and the tee's real SIGTERM behaviour
(`vb12win.py`, 6 reps per mode), on all three interpreters:
```
3.11.15  ORACLE sha_ok=True sigterm=0 kpg=2323 sd=422 kill<wait=True from_secs5_prod=1 | CONST ok=True tee_sites=3 test_sites=3 | ASTpin viol=[] | AP59 hits=[] | F4 killpg=True cannot=True running=True neg_all=True
3.12.3   identical
3.13.12  identical

3.11.15  poll n=6 rc={70: 6} status_present=6/6  write_errors=['terminated: SIGTERM'] final=False updated_seq=2
3.11.15  t0   n=6 rc={-15: 6} status_present=0/6
3.12.3   poll n=6 rc={70: 6} status_present=6/6  (identical status object)   3.12.3  t0 n=6 rc={-15: 6} 0/6
3.13.12  poll n=6 rc={70: 6} status_present=6/6                              3.13.12 t0 n=6 rc={-15: 6} 0/6
```
The docstring's "the only uncovered SIGTERM window is Python interpreter startup before the handler install
(default disposition: rc −15, no status file)" reproduces **6/6 on all three**. **Could not run:** the pytest
suite on 3.12/3.13 — pytest is installed for 3.11 only; no install attempted.

## The tripwire through the PIN's committed checker

```
checker in my git-archive venue: de13655acc86f5ac7a2a7ae772f9a9e58a5696cd978e25bf0cba1ff128b0093d
checker in the SHARED tree now : 56e86e712e3a54bb1e96ac55cc2a6b206076a7966688b142a629b2428eb4bf0a  (another lane's live edit)
$ pytest -k test_sigterm_status_satisfies_check_tee_status      1 passed, 100 deselected in 0.23s   rc=0
```
It really reaches the checker: `cc._load_timeline_raw(...)` at `test:2370`, `cc.check_tee_status(...)` at
`test:2372`. Its negative control also bites: `NC-TRIPWIRE-LOOPONLY` → `KILLED 10.6s | no recorded frame: the
wait for updated_seq >= 1 timed out (test:2358)`.

## pyflakes and `lint_delta` — the TOOL's output, pasted

```
$ python3 -m pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py     rc=0     (no output)

$ python3 scripts/lint_delta.py --base HEAD          # scratch repo: 3167608's two scope files as base, PIN's as worktree
lint_delta (worktree vs HEAD): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed
anti-pattern screen (TELLS on added lines — verify each, advisory):
  AP-1  tests/test_s0_01_frame_tee.py: env read in edited code — config channel? resolve ONCE at construction, thread explicitly
  AP-32 tests/test_s0_01_frame_tee.py: hashing in edited code — is the hashed form EXACTLY what the store holds? (stamp-store mismatch class)
lint_delta rc=0
```
Identical to the report's PROBE row. Both tells are false positives as the lane classified them: AP-1 is the
zombie fixture's `os.environ.copy()` / the agent string's `os.environ.get("S0_01_FRAMEDIR")`; AP-32 is
`hashlib.sha256(VENDORED_ACP_RS.read_bytes())` — the oracle's own premise, with no store to mismatch.
**F-B5g-5 is CLOSED.** (The scope files are byte-identical at `3167608`, `0f2606d` and `8695636`, so
`--base 3167608` and `--base 8695636` are the same delta — verified by blob id.)

## Process census across two full suites, own-venue scoped

```
LOAD 2.27 4.17 4.38
IDLE SUITE RUN 1 (PIN venue)   101 passed in 193.43s (0:03:13)   rc=0
IDLE SUITE RUN 2 (PIN venue)   101 passed in 195.49s (0:03:15)   rc=0
LOAD 2.25 3.68 4.20
census (argv[0] is a python/sleep binary AND the cmdline names my venue or a time.sleep grandchild):
    candidate own/related processes: 0
orphaned `time.sleep` grandchildren anywhere on the box: none
```
**Zero live leaks of mine after everything.** One orphan did exist mid-grade: `pid 2330 ppid 1
python3 -c import time; time.sleep(120)` — my own `GRANDCHILD-UNKILLED-S2` mutant's grandchild, by design of
that mutant; it self-exited inside its own sleep and was gone at the POST census. I signalled no process I
did not start, and used no `pkill` anywhere.

**Environment note for the coordinator:** `df -h /` reports **95-96 % used, ~1.8-2.1 G free**. My venues are
~400 MB after cleanup. Also: two verifiers running pytest as root share `/tmp/pytest-of-root/`, and pytest's
numbered-tmpdir allocation is a TOCTOU race between processes — I hit one (`FileExistsError` on
`framedir.mkdir()`), which is why every measurement above uses an explicit `--basetemp`.

---

# ITEM 7 — REPORT DISCIPLINE

**Header:** correct this round. `Dispatched at 3167608fab244cb52f3434b5569eaee635ca1f75; landing = the
coordinator's checkpoint, made after this report.` **F-B5g-6 / F14 CLOSED.**

**FILE IDENTITY:** both sha256s and both line counts match the PIN's bytes exactly. **Test counts:** 90 defs
before / 93 after (`grep -c 'def test_'` on `0f2606d` and the PIN), 98 → 101 collected. Correct.

## The 10+ `file:line` spot-checks, by `sed -n` on the PIN's bytes

| ref | reads | verdict |
|---|---|---|
| `tee:50-52` constant | `PINNED_SHUTDOWN_CLAUSE = (` | ✔ (the closing `)` is at :53) |
| `test:42` import | `AP_SCREEN = _es_mod.AP_SCREEN + _es_mod.TEST_SCREEN` | ✔ |
| `test:49` `_KILL_SITES` | `_KILL_SITES = frozenset({` | ✔ |
| `test:104` helper | `def _kill_own_grandchild(framedir):` | ✔ |
| `test:117` pidfile assert | `assert gc_pid_path.exists(), "agent never wrote grandchild.pid"` | ✔ |
| `test:119-131` zombie logic | the try/stat/assert block | ✔ |
| `test:2579` `range(6000)` | `"for i in range(6000):\n"` | ✔ |
| `test:2663` zombie test | `def test_zombie_grandchild_is_already_gone(self, tmp_path):` | ✔ |
| `test:2862` AP_SCREEN test | `def test_grandchild_cleanup_is_own_pid_scoped(self, tmp_path):` | ✔ |
| `test:2878` AST pin | `def test_kill_calls_only_at_allowed_sites(self, tmp_path):` | ✔ |
| `test:2999` oracle test | `def test_shutdown_prose_matches_the_pinned_source(self, tmp_path):` | ✔ |
| `test:1534-1535` R1 comment | `# R1: SIGTERM it (an operator/systemd TERM; buzz-acp` / `# SIGKILLs the group instead).` | ✔ |
| `test:3086` / `test:3107` / `test:3013` killer lines | the three assertions named | ✔ |
| `test:863` | `f = {"jsonrpc": "2.0", "method": "c", "params": {"i": i}}` | ✘ **parent-era ref** (real site 908-909) |
| `test:1028` | `framedir.mkdir()` | ✘ **parent-era ref** (real site 1076-1077) |
| `test:1472` | `status = json.loads((framedir / "tee-status.json").read_text())` | ✘ **parent-era ref** (real site 1489-1490) |
| `test:2880` | `sits inside _kill_own_grandchild or inside a function named in the` | ✘ (real: 2875) |
| `test:2916` | `import sys, json, time` | ✘ (real: 2904) |
| `test:600-607` / `1145-1152` / `2645-2652` | census blocks | ~ off by 1-3 (real: 599-608 / 1142-1151 / 2643-2652) |

**15 correct, 5 wrong, 3 near.** → **F8.**

## Every DONE row that claims a kill — reproduced

| row | claim | my reproduction |
|---|---|---|
| 1 | "DOCSTRING-ORDER mutant dies on `PINNED_SHUTDOWN_CLAUSE does not state 'first ... then waits'` at test:3086" | **verdict right, mechanism wrong.** The *docstring* mutant dies at `test:3104` (site count). `test:3086` is what fires when the **constant** is mutated (CONST-ORDER). The lane ran a constant mutation and labelled it DOCSTRING-ORDER. → **F7** |
| 2 | "TESTDOC-TERM dies on both `…appears 2 times in test file…` (test:3107) AND old regex pin" | **reproduced** (`test:3141` regex + the oracle test) |
| 3 | "CONTROL: pipe closes run even when census assertions fail" | **reproduced at the fd table** (item 3a) |
| 4 | "CONTROL: no blocking read of tee_proc.stdout/stderr in the census path" | **true and insufficient** — no pin enforces it, and the hang is upstream of the census (**F9**) |
| 5 | zombie red `pid 1813 is not the grandchild (cmdline: '')` | **reproduced** (`pid 20979 …`); the label "against parent tee 736bb94" is wrong (it is the parent HELPER) |
| 6 | "CENSUS-PGREP-TIGHT killed by AP_SCREEN (`AF-AP-59 match: ['"pgrep","-f"']`)"; "CENSUS-PGREP-X killed by AST pin" | **both reproduced** (`test:2875` / `test:2904`) |
| 7 | "CONTROL: grandchild now outlives the 45 s census deadline" | **FALSE as measured** — it does not; state `Z` at census (**F4**) |

## The NOT_DONE list — every inferred claim measured

| lane's inferred claim | measured verdict |
|---|---|
| DOCSTRING-WRONGEVENT dies "same assertion (constant check)" | **KILLED — but by `test:3104`, not the constant check** |
| CENSUS-PS-E dies on AP_SCREEN | **TRUE** (`test:2875`) |
| **CENSUS-PGREP-A dies on AP_SCREEN** | **FALSE — SURVIVES** (**F3**) |
| CENSUS-PROC-WALK dies on the AST pin | **TRUE** (`test:2904`) |
| PIDFILE-ABSENT ×3 "byte-identical assertion at line 117, all 3 sites call it" | **TRUE** — all three die at `test:117`, with no pipe leak |
| **GRANDCHILD-UNKILLED-S3 "structurally exercised, not timing-marginal"** | **FALSE — SURVIVES; the grandchild is a zombie at census** (**F4**) |
| red state on the parent via the full suite "not run" | **run by me: 1 failed, 100 passed** — only the oracle test is red |
| cost probe "not run … the tee's runtime behavior is unchanged" | **run by me: 0.94×, no measurable cost — the inference holds** |
| 3.12/3.13 "not run" | **run by me: identical on 3.11/3.12/3.13** |
| tripwire "not run" | **run by me: 1 passed, and it reaches the checker** |
| **F-B5g-9 hang reproduction "not attempted … the fix is structural"** | **run by me: the deadlock reproduces on the PIN, deterministically** (**F9**) |

---

# ITEM 8 — THE MUTANT TABLE

Protocol: restore all three files from the pristine archive → apply → `ast.parse` both Python files → run the
named killer → escalate a survivor to the full suite, no `-x` → restore → re-assert sha256
(`8dfdeb7f704d` / `d1be6adf7ff3` / `44e828617636`, printed after every batch). A 28-mutant anchor dry-run
confirmed **APPLY-OK 28/28, 0 PATCH-FAILED, 0 NO-OP, 0 SyntaxError** before any pytest ran. Every mutant lived
on scratchpad copies; `git status --porcelain` on the shared tree was empty at every check.

## Rows the delta can move (the predecessor's 48, re-anchored) — 8 rows

| id | result on the PIN | killer |
|---|---|---|
| DOCSTRING-TERM (row 27) | **KILLED ×2** | `test:3104` + `module docstring does not name killpg` (`test:3131`) |
| DOCSTRING-HYBRID (30) | **KILLED ×2** | `test:3104` + `test:3132` |
| COMMENT-TERM (31) | **KILLED ×2** | `test:3141` + oracle |
| PIDFILE-ABSENT (32), all 3 sites | **KILLED ×3** | `test:117`, no pipe leak |
| GRANDCHILD-UNKILLED (28), sites 1 & 2 | **KILLED ×2** | `grandchild pid N still alive after kill` (`test:156`) |
| CENSUS-WORLD (33) | **KILLED** | AP_SCREEN `test:2875` |
| MIRROR-SNAPSHOT (36) | **KILLED** | `state/seq read outside 'with lock:' at [183…189]` (`test:2560`) |
| MIRROR-PREINIT (37) / NO-PREINIT (25) | **KILLED ×2** | `proc is rebound to a non-None value before the handler install` (`test:2857`) |
| NC-TRIPWIRE-LOOPONLY | **KILLED** 10.6 s | `no recorded frame: the wait for updated_seq >= 1 timed out` (`test:2358`) |
| NC-FLAG-LOOPONLY-S1 | **KILLED** 10.6 s | `no a2c frame recorded before the liveness window` (`test:593`) |

## New rows (mine + the brief's) — 21 rows

| id | result | killer / note |
|---|---|---|
| ORACLE-SHA-MISMATCH | KILLED | `test:3013` (premise first) |
| ORACLE-SHA-LOUD | KILLED | `test:3013` (premise still first) |
| DOCSTRING-ORDER | KILLED | `test:3104` |
| DOCSTRING-WRONGEVENT | KILLED | `test:3104` |
| TESTDOC-TERM | KILLED | `test:3141` + oracle |
| CONST-ORDER | KILLED | `test:3086` |
| CONST-WRONGEVENT | KILLED | `test:3086` |
| **FALSECONST-ORDER** | **SURVIVED — FULL SUITE `101 passed in 187.90s`** | **F1** |
| **SITECOUNT-DUP** | **SURVIVED — FULL SUITE `101 passed in 187.79s`** | **F13** |
| **SEVENTH-SITE** | **SURVIVED** (full suite via UNION-DOCROT) | **F12** |
| **CITE-421 / CITE-421-TEST / CITE-KPG-2324** | **SURVIVED ×3** | **F5** |
| UNION-DOCROT (the four above together) | **SURVIVED — FULL SUITE `101 passed in 187.91s`** | |
| CENSUS-PGREP-TIGHT / -PS-E / -PGREP-SHELL | KILLED ×3 | AP_SCREEN `test:2875` |
| CENSUS-PGREP-X / -PROC-WALK | KILLED ×2 | AST pin `test:2904` |
| **CENSUS-PGREP-A** | **SURVIVED** | **F3** |
| **CENSUS-PKILL-DQ** | **SURVIVED (regression — the deleted pin killed it)** | **F2** |
| CENSUS-PKILL-SQ | SURVIVED | pre-existing, unchanged |
| CENSUS-ENUM-ONLY | SURVIVED | documented limit ✔ |
| **KILL-ALIAS / -PTHREAD / -SUBPROC / -SENDSIGNAL** | **SURVIVED ×4** | spelling evasions; concept limit |
| **KILL-MODULE-LEVEL / KILL-LAMBDA** | **SURVIVED ×2** | **implementation holes in the AST pin — F3** |
| **GRANDCHILD-UNKILLED-S3** | **SURVIVED `1 passed in 61.61s`** | **F4** |
| ZOMBIE-OLDSEMANTIC (the red state) | KILLED | `pid N is not the grandchild (cmdline: )` |

```
TOTALS over the 39 mutants I ran:
  KILLED-BY-NAMED   23
  SURVIVED (real)   16   of which 6 are documented/conceptual limits (CENSUS-ENUM-ONLY, -PKILL-SQ,
                         KILL-ALIAS/-PTHREAD/-SUBPROC/-SENDSIGNAL) and 10 are findings F1-F5, F12, F13
  PATCH-FAILED 0    SYNTAX-ERROR 0    NO-OP 0
```
**MIRROR-STALE** is unmoved by this delta (`_write_status` is untouched); the predecessor's measurement stands
— the pin accepts it, eleven exact-value assertions kill it in the full suite.

---

# FINDINGS

**F1 [BLOCKING] SOLID — the constant is a token check in disguise; the DOCSTRING-ORDER class survives the
whole suite, unchanged in mechanism.**
`tests/test_s0_01_frame_tee.py:3081-3095` (the five `in` assertions) vs `:3068-3076` (the derived order,
never compared to the prose).
*Observed vs expected:* expected a pin where a false ORDER "requires changing the constant, which the source
assertion rejects" (the lane brief's own words). Observed: the source assertion checks that the *source* has
the right order; the *constant* is checked only for six substrings. **FALSECONST-ORDER** — the clause
reversed to wait-then-kill, propagated to all six sites — is `101 passed in 187.90s`.
*Failing input:*
```python
PINNED_SHUTDOWN_CLAUSE = (
    "buzz-acp waits up to 5 s for the child to exit first and then waits"
    " no more before it SIGKILLs the group (killpg)")
```
*Minimal fix:* compare the clause to the derived order instead of to a word list — e.g. build the expected
clause from the derived facts and assert **equality**:
```python
expected = ("buzz-acp SIGKILLs the group (killpg) first and then waits up to %d s"
            " for the child to exit" % secs)            # secs parsed from the from_secs(N) at wait_line
assert PINNED_SHUTDOWN_CLAUSE == expected, ...
assert kill_line < wait_line                            # already present; now it is load-bearing
```
plus an order check on the clause itself: `clause.index("SIGKILL") < clause.index("waits up to")` iff
`kill_line < wait_line`.
*Exact red test to add:* the equality above — RED on FALSECONST-ORDER, GREEN on the PIN.

**F2 [BLOCKING] SOLID — replacing the hand-typed literals with `AP_SCREEN` REMOVED coverage: a double-quoted
world-scoped `pkill -f` is no longer caught, and `pkill` is the member of the class that actually kills.**
`tests/test_s0_01_frame_tee.py:2870-2876`; the deleted pin was `0f2606d` `test:2811-2816`
(`needle_pkill = '"pki' + 'll"'`); the registry row is `.claude/hooks/edit-snapshot.py:179` and contains no
`pkill` alternative.
*Observed vs expected:* expected the registry signature to be "strictly stronger than two hand-typed
literals" (F-B5g-3's words). Observed **CENSUS-PKILL-DQ SURVIVES** where the old pin killed it.
*Failing input:* `subprocess.run(["pkill", "-f", "import time; time.sleep"], capture_output=True, text=True)`
inside any of the three `finally` blocks.
*Minimal fix:* keep the AP_SCREEN import **and** add the missing alternative to the AF-AP-59 row in
`edit-snapshot.py` (`|["']pkill["']|\bpkill\s+-f\b`) so the registry — not this test — carries it; the test
then inherits it for free, which was the point of the import.
*Exact red test to add:* none new — `test_grandchild_cleanup_is_own_pid_scoped` becomes the red test once the
registry row is extended; assert it RED against the failing input above.

**F3 [MED] SOLID — one of the six named CENSUS spellings survives (the lane inferred it dies), and the AST
pin has two implementation holes on top of its documented concept limit.**
`tests/test_s0_01_frame_tee.py:2870-2876` (AP_SCREEN) and `:2886-2903` (the AST walk).
*Observed vs expected:* (a) **CENSUS-PGREP-A** `subprocess.run(["pgrep", "-a", "-f", "time.sleep"])`
**SURVIVES** — the report's NOT_DONE asserts it dies "AP_SCREEN (regex matches `"pgrep"` + `"-f"`)"; the
regex requires the two tokens to be *adjacent*. (b) The AST pin iterates `ast.walk(tree)` for
`FunctionDef`/`AsyncFunctionDef` and inspects only those bodies, so **an `os.kill` written literally as
`os.kill` at module scope, in a class body, or inside a `lambda` is never examined** — `KILL-MODULE-LEVEL`
and `KILL-LAMBDA` both survive. (c) Four spelling evasions also survive (`from os import kill as k`,
`signal.pthread_kill`, `subprocess.run(["kill",…])`, `Popen.send_signal`) — these are the concept limit the
brief acknowledged, and I list them for completeness, not as a charge.
*Failing input (b):* `os.kill(int(os.environ['X']), sig.SIGKILL)` at module scope.
*Minimal fix:* (a) extend the registry row: `["']pgrep["'](\s*,\s*["']-[a-z]+["'])*\s*,\s*["']-f["']`.
(b) walk the module tree once, tracking the enclosing `FunctionDef` for every `Call` (or simply: collect all
`os.kill`/`os.killpg` Calls in the file, then subtract those whose enclosing function is allowed) so
module-level and lambda-scope calls are violations by default.
*Exact red test to add:* `KILL-MODULE-LEVEL` as a committed regression fixture string that
`test_kill_calls_only_at_allowed_sites` must reject.

**F4 [BLOCKING] SOLID — F-B5g-8 is NOT closed; the `range(6000)` fix cannot work by construction, and the
DONE/DISCREPANCIES claim that it does is false.**
`tests/test_s0_01_frame_tee.py:2579` (the change), `:2637-2642` (`tee_proc.wait(timeout=30)`), `:104-157`
(the helper).
*Observed vs expected:* the report says "site 3's grandchild now 60 s > 45 s deadline … the kill path is now
structurally exercised". Observed: **GRANDCHILD-UNKILLED-S3 `1 passed, 100 deselected in 61.61s`** and the
instrumented branch trace `BRANCH pid=21867 cmdline='' state=Z` — the grandchild is a **zombie** when the
census runs. Mechanism: the test's `finally` cannot run until `tee_proc.wait(timeout=30)` returns; the tee
cannot exit until its a2c pump sees EOF; a2c EOF *is* the grandchild's exit. So the grandchild is
**guaranteed** dead before the census at this site, for any lifetime.
*Failing input:* `-k test_concurrent_main_thread_status_vs_pump` with `os.kill(gc_pid, sig.SIGKILL)` deleted
from the helper.
*Minimal fix:* pick one and say so in the DONE table — (i) accept it: state that site 3 contributes the
pid-file and identity assertions only (the brief's other branch), **and revert `range(6000)` to
`range(3000)`** to give back the 16 s; or (ii) make the kill reachable by spawning a second, independent
grandchild at site 3 that does *not* hold the agent's stdout (so the tee's exit does not depend on it).
*Exact red test to add:* assert in the helper's own coverage that at least one site takes the **live** branch
and one takes the **already-gone** branch — e.g. have the helper return the branch taken and assert the set
of branches across the three sites is `{"live", "gone"}`, which turns today's silent skip into a stated fact.

**F5 [MED] SOLID — nothing asserts the acp.rs citations; `:422`→`:421` survives the full suite, and the DONE
row's "fixes F-B5g-11's `:421` by construction" is false.**
`tests/test_s0_01_frame_tee.py:3077-3079` (derives and asserts the values, never the citations);
the citation sites are `frame_tee.py:20`, `:431`, `:439` and `test:910`, `:1078`, `:1490`.
*Observed vs expected:* the brief required "assert every docstring/comment citation in BOTH scope files cites
exactly those ranges". Observed: `CITE-421`, `CITE-421-TEST`, `CITE-KPG-2324` all pass, and the union passes
the full suite (`101 passed in 187.91s`).
*Failing input:* change `acp.rs:422-444` to `acp.rs:421-444` in the tee's module docstring.
*Minimal fix:*
```python
cite = "acp.rs:%d-444" % sd_start          # 444 likewise derived from the fn's closing brace
for name, text in (("frame_tee.py", tee_src), ("test file", test_src)):
    for m in re.finditer(r"acp\.rs:(\d+)-(\d+)", _ws_norm(text)):
        assert int(m.group(1)) == sd_start, "%s cites acp.rs:%s, shutdown() opens at :%d" % (name, m.group(1), sd_start)
    for m in re.finditer(r"[`\s]:(\d{4})-2328", _ws_norm(text)):
        assert int(m.group(1)) == kpg_start
```
*Exact red test to add:* the loop above — RED on CITE-421, GREEN on the PIN.

**F6 [MED] SOLID — the helper dropped the parent's `except ProcessLookupError` around the kill, re-opening
the fail-loud-on-benign-race class F-B5g-4 was opened for; `PermissionError` on the identity read is still
uncaught.**
`tests/test_s0_01_frame_tee.py:139-141` (`if gone_or_foreign: … else: os.kill(gc_pid, sig.SIGKILL)`, no
guard) vs `0f2606d` `test:544-546` (`except ProcessLookupError: pass`); `:120` (the `open` catches
`FileNotFoundError` only).
*Observed vs expected:* measured against the real helper — `3 PROCESSLOOKUP: UNCAUGHT ProcessLookupError:
[Errno 3] No such process`; `4 PERMISSIONERROR: UNCAUGHT PermissionError: [Errno 13] Permission denied`.
*Failing input:* a grandchild that is alive when `/proc/<pid>/cmdline` is read and reaped before `os.kill`
(SIMULATED with a narrowly-patched `open`; the window is microseconds on this box and I did not force it
naturally — the missing guard is primary-source visible).
*Minimal fix:*
```python
    else:
        try:
            os.kill(gc_pid, sig.SIGKILL)
        except ProcessLookupError:
            gc_pid = None            # raced us to exit; that is the success condition
```
and widen the identity read: `except FileNotFoundError:` → `except (FileNotFoundError, PermissionError, ProcessLookupError):`
(with the `PermissionError` arm treated as "cannot identify — do not kill", which is the fail-closed direction).
*Exact red test to add:* a unit test that calls `_kill_own_grandchild` with a pid file naming a reaped pid and
a monkeypatched `/proc` read — RED today, GREEN after.

**F7 [MED] SOLID — the DONE table's headline killer line belongs to a different mutant than the one it names
(AF-AP-37, third consecutive round).**
`tasks/briefs/s0-01-b5h-support/B5h-report.md:19` and the MUTANT table's DOCSTRING-ORDER row.
*Observed vs expected:* the row says DOCSTRING-ORDER "dies on `PINNED_SHUTDOWN_CLAUSE does not state 'first
... then waits'` at test:3086". Measured: the *docstring* mutant dies at **test:3104** (`appears 2 times in
frame_tee.py`); **test:3086 is what the CONSTANT mutation triggers**. The lane ran a constant mutation under
the docstring mutant's name — which matters, because the two probe different things and only the docstring
form is the F-B5g-1 counter-example.
*Minimal fix:* paste the pytest tail for the mutant actually run, and run both forms.
*Exact red test to add:* none (report artifact).

**F8 [MED] SOLID — five `file:line` refs are wrong; three of them are the PARENT's line numbers pasted into a
table whose header claims "by grep on FINAL bytes".**
`B5h-report.md:19` (`test:863`, `test:1028`, `test:1472`), `:35` (`test:2880`), `:36` (`test:2916`).
*Observed vs expected:* on the PIN those lines read `f = {"jsonrpc": …}`, `framedir.mkdir()`,
`status = json.loads(...)`, a docstring line, and `import sys, json, time`. The three docstring sites are at
**908-909 / 1076-1077 / 1489-1490**; the two killer assertions are at **2875** and **2904**. The three
parent-era refs are exactly F-B5g-11's `:863 / :1029 / :1473`.
*Minimal fix:* re-grep on the final bytes; paste. `scripts/report_lint.py` catches all five in one call.
*Exact red test to add:* none (report artifact) — but `report_lint.py` is now the mechanical gate for it.

**F9 [BLOCKING] SOLID — the hang class is NOT closed: the F-B5g-9 deadlock reproduces on the PIN's tee
deterministically, the structural pin the design mandated was not built, and neither fact is in NOT_DONE.**
`tests/test_s0_01_frame_tee.py:2606-2607` (`tee_proc.stdout.readline()` with `tee_proc.stdin` open, no
deadline) and `:2618-2637` (the 45 s spin loop, stdin still open); no pin anywhere.
*Observed vs expected:* the lane brief required "give each [blocking read] a deadline … and close
`tee_proc.stdin` BEFORE any wait on the tee's exit or output where the test no longer writes; add a
structural pin: no `.stdout.read`/`.stderr.read`/`.readline(` on a tee `Popen` outside a bounded reader
helper". Observed: 16 `.stdout.read`, 27 `.readline(`, 2 `communicate(` in the file, **none inside any
assertion**; the words "blocking" and "bounded reader" appear **0 times**; only four tests read
`Path(__file__)` and none looks at pipe reads. And the cycle itself:
```
PIN  HANG at 12 s | tee tid(main) wchan=hrtimer_nanosleep, tid(c2a) wchan=anon_pipe_read
                  | TEST holds fd 4 -> pipe:[466837] == TEE fd 0
```
*Failing input:* the probe in item 5 — an agent that consumes the handshake and closes stdout without
writing, while the test holds the tee's stdin and calls `tee_proc.stdout.readline()`.
*Minimal fix (code):* at site 3, move `tee_proc.stdin.close()` to immediately after the last
`tee_proc.stdin.write(...)`/`flush()` — the test writes nothing after the late frames — and give the
handshake `readline()` a deadline (a reader thread joined with a timeout).
*Exact red test to add (the structural pin, ~15 lines):*
```python
def test_no_unbounded_tee_pipe_reads(self):
    """Every read of a tee Popen's stdout/stderr sits inside a bounded helper."""
    tree = ast.parse(Path(__file__).read_text())
    BOUNDED = {"_drain", "_read_with_deadline"}          # the drainer threads + any future helper
    bad = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        if fn.name in BOUNDED: continue
        for c in ast.walk(fn):
            if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                    and c.func.attr in ("read", "readline", "communicate")
                    and isinstance(c.func.value, ast.Attribute)
                    and c.func.value.attr in ("stdout", "stderr")
                    and getattr(c.func.value.value, "id", "") == "tee_proc"
                    and not any(k.arg == "timeout" for k in c.keywords)):
                bad.append("%s at line %d in %s" % (c.func.attr, c.lineno, fn.name))
    assert not bad, "unbounded read of a tee pipe outside a bounded helper: %s" % bad
```
RED on the PIN today (it flags `test:2607` and `test:2209`, `test:1785`, `test:459`, `test:515`), GREEN once
each is given a deadline or moved into the drainer.
*Also charged as a report claim:* NOT_DONE says the hang was "not attempted … the fix is structural". The
fix is not structural — there is no structure.

**F10 [LOW] SOLID — a stale comment inside the very hunk this increment changed, in an increment about prose
that matches the artifact.**
`tests/test_s0_01_frame_tee.py:2576`: `# grandchild streams a2c frames for 30 s`, three lines above the
`range(6000)` the lane wrote (60 s). Same file, `:2564` docstring is unaffected.
*Minimal fix:* `# grandchild streams a2c frames for 60 s`. *Exact red test to add:* none proportionate.

**F11 [LOW] SOLID — `_KILL_SITES` is dead code and its comment contradicts itself.**
`tests/test_s0_01_frame_tee.py:49-54`. The frozenset holds one name; the comment says *"Only these two
functions in the file use bare os.kill:"* and then names none; and `test:2891` already hard-codes
`fname == "_kill_own_grandchild"`, so the set can never change a verdict.
*Minimal fix:* delete `_KILL_SITES` and the comment, or make the pin read `fname in _KILL_SITES` only.

**F12 [LOW] SOLID — a false sentence added beside the correct clause survives everything (the pin is
additive; the negative direction is a two-entry blacklist).**
`proofs/S0-01/tools/frame_tee.py:22-23` (the site I extended). SEVENTH-SITE survives the full suite via
UNION-DOCROT (`101 passed in 187.91s`).
*Failing input:* "A wedged leg therefore gets a 5 s grace period in which it may still flush, and buzz-acp
sends SIGTERM before that grace period starts."
*Minimal fix:* the cheap general guard is `assert "SIGTERM" not in doc.split("The SIGTERM path")[0]`
(the predecessor's own proposal at F-B5g-1) — it kills this sentence and every "buzz-acp sends SIGTERM"
variant, and costs one line. *Exact red test to add:* that assertion, RED on SEVENTH-SITE.

**F13 [LOW] SOLID — the six-site pin is a file-wide COUNT, not a per-site presence check.**
`tests/test_s0_01_frame_tee.py:3104-3110`. SITECOUNT-DUP (delete the clause from the module docstring, add a
third copy to a comment) is `101 passed in 187.79s`.
*Minimal fix:* assert the clause is present in the module docstring specifically
(`assert clause_norm in _ws_norm(ast.get_docstring(ast.parse(tee_src)))`) in addition to the counts.

**F14 [INFO] SOLID — the test module now imports the production module at collection time.**
`tests/test_s0_01_frame_tee.py:34-35` (`sys.path.insert` + `from frame_tee import PINNED_SHUTDOWN_CLAUSE`).
Safe today (`frame_tee.py:481` has the `if __name__ == "__main__"` guard), but any future import-time side
effect in the tee now breaks the whole suite at collection rather than one test. Worth one line in the tee:
`# imported by tests/test_s0_01_frame_tee.py — keep this module import-side-effect free`.

**F15 [INFO] SOLID — environment, for the coordinator.** `df -h /` = **95-96 % used, ~1.8-2.1 G free** on this
box while three lanes hold scratch venues. And two verifiers running pytest as root share
`/tmp/pytest-of-root/`; pytest's numbered-tmpdir allocation races between processes and I hit it once
(`FileExistsError` on `framedir.mkdir()` at `test:2688`). Every measurement above uses an explicit
`--basetemp`. The suite's ubiquitous `framedir.mkdir()` (no `exist_ok`) is the amplifier; it is pre-existing,
not this lane's.

**F16 [INFO] — my own instrument error, corrected.** My first fd-census `conftest.py` defined
`pytest_runtest_call` as a plain hook, so the test body ran twice and the zombie test failed with
`FileExistsError`. I diagnosed it (the test's own artifacts were already in the tmp dir), rewrote the hook as
a `hookwrapper`, and re-took the control: `1 passed in 1.71s`. The PIDFILE-ABSENT rows are unaffected (an
assertion aborts the hook chain before the second call), and I re-ran the zombie control under the fixed
instrument. Recorded because a verifier's instrument is a hypothesis like any other (AF-AP-36).

---

# ITEM 9 — THE DESIGN ITSELF

## The vendored-oracle approach: right idea, half-wired

**Keep it.** Vendoring `crates/buzz-acp/src/acp.rs@1c8321cd` (217 424 bytes, 5030 lines) is the correct
answer to F-B5g-1 and it is done well: the file is verbatim and never edited, the sha256 premise fires
*first* on any tamper (measured twice), the provenance file beside it
(`proofs/S0-01/vendor/buzz-acp/VENDORED-FROM.md`) names source repo, commit, path, digest, fetch route,
**independent confirmation by a second party**, purpose and a never-edit rule — that is a model provenance
record, better than most of the repo. 228 KB in a tree that already carries `sandbox-kit/` is not a cost
worth arguing about, and the alternative (a committed "facts" file derived once) would be an oracle that
re-implements the source instead of *being* it — the exact hollow-green the tactic set forbids.

**But as built, the oracle contributes almost no failing power.** Every derived-fact assertion in
`test_shutdown_prose_matches_the_pinned_source` — `oracle.count("SIGTERM") == 0`, `killpg(` + `Signal::SIGKILL`
in `kill_process_group`, `kill_line < wait_line`, the unique `from_secs(5)`, `sd_start == 422`,
`kpg_start == 2323` — is a **pure function of the file's bytes**, and the bytes are pinned by the sha
assertion three lines earlier. So while the sha holds, none of them can go red; and when the sha fails, none
of them is reached. They are unfalsifiable today **by construction** (this is analytic, not a mutant result —
no mutant can separate them, which is the point). Their real value arrives only on an upstream bump, when the
sha constant is updated and they become the semantic guard on the new file. That is a legitimate purpose and
should be **said in the test's docstring**, because right now the test reads as though the derivation is
guarding the prose. It is not: the derivation and the prose are joined by five `in` checks on a hand-written
string (**F1**), and no assertion joins the derived *order* to the clause's order or the derived *line
numbers* to the cited ones (**F5**). Wire those two joins and the oracle earns its 217 KB; without them the
vendored file is an expensive way to assert one sha256.

**One thing I would add now:** the digest lives in two places — `VENDORED-FROM.md:8` and
`tests/test_s0_01_frame_tee.py:46` — with nothing asserting they agree, and `upstream.lock.yaml` records only
the buzz **commit**, not the file digest. One line in the oracle test
(`assert VENDORED_ACP_RS_SHA256 in (VENDORED_ACP_RS.parent / "VENDORED-FROM.md").read_text()`) removes the
drift, and adding a `files:` digest under the `buzz` entry in `upstream.lock.yaml` would put it where project
rule 13 expects it.

## Is the constant-at-six-sites pin the right shape?

**The "one place that can be wrong" instinct is right; the enforcement is the wrong shape twice over.**

* It enforces a **file-wide count** (`tee_count >= 3`, `test_count >= 3`), not per-site presence — so
  SITECOUNT-DUP deletes the clause from the site a reader actually reads (the module docstring) and keeps the
  count by duplicating a comment (**F13**).
* It is **additive only** — it proves the true sentence is present N times and says nothing about false
  sentences beside it (**F12**).

Two designs I would prefer, in order:

1. **Don't repeat the prose at all.** Keep `PINNED_SHUTDOWN_CLAUSE` as the single sentence, and have the
   other five sites say *"buzz-acp's shutdown bound: see `PINNED_SHUTDOWN_CLAUSE` in `frame_tee.py`"*. Then
   there is exactly one sentence in the repo that can be false, the count pin becomes unnecessary, and F12
   and F13 dissolve. The cost is a little local readability, which is what a one-line reference buys back.
2. If the prose stays in six places: replace the count with an **explicit site list** — the module docstring
   (via `ast.get_docstring`), the two R1 comments (anchored on `while to.is_alive()` / `while ti.is_alive()`),
   and the three test docstrings (by test name, via `ast.get_docstring` on each `FunctionDef`) — plus the
   negative guard `assert "SIGTERM" not in doc.split("The SIGTERM path")[0]`. Six named sites, each proven
   individually, and one sentence that cannot be false without failing the equality in **F1**'s fix.

## Two more design calls I would make differently

* **The AST kill-site pin should be written as a subtraction, not an inclusion** (F3b): collect every
  `os.kill`/`os.killpg` `Call` in the module, then remove those whose enclosing `FunctionDef` is allowed.
  Written the way it is — iterate functions, look inside — everything that is not inside a function is
  invisible, which is a hole a reviewer will not see by reading the test.
* **`range(6000)` was the wrong lever for F-B5g-8** (F4). The site-3 test *cannot* hold a live grandchild at
  census, because it waits for a tee whose exit depends on that grandchild's death. The honest options were
  "state that site 3 contributes the pid-file assertion only" (which the brief offered) or a second,
  independent grandchild. Choosing the lever that cannot work, and then reporting it as a closure, cost
  16 s per suite run and left the finding open.

## What would still make a MERGE-READY verdict unsafe

1. **F1** — the increment exists to close the false-ORDER class, and a false-ORDER artifact still passes the
   whole suite. Merging would record "the prose is now checked against the source" in the ledger when it is
   not.
2. **F2** — a *world-scoped killer* (`pkill -f`) that the previous round's pin caught is now uncaught. A
   round that closes a class must not open a hole in it.
3. **F4** and **F9** — two DONE-table closures that measurement refutes. Their danger is not the code; it is
   that the ledger would inherit two false "closed" rows, and the next round would not re-test them.
4. Three consecutive rounds of wrong `file:line` refs (**F7**, **F8**) mean the report's numbers are not
   usable as evidence without `report_lint.py`. That is now cheap to fix and should simply be a gate.

---

# WHAT I REPRODUCED vs REVIEWED STATICALLY vs DELIBERATELY SKIPPED

**Reproduced (my own runs this session, on `git archive 63b582c` / `git show 0f2606d:` copies under the
session scratchpad; load stated at every timing):** the PIN full suite ×4 (`187.65s` idle, `193.43s`,
`195.49s` under other lanes' load, plus 3 more inside mutant escalations); the full no-`-x` red state on the
parent tee (`1 failed, 100 passed in 187.62s`); **39 distinct mutants** over ~55 pytest invocations with 4
full-suite escalations, every one applied to a scratchpad copy and restored with a sha256 assertion; the
28-mutant anchor dry-run (28/28 apply, 0 no-op, 0 syntax error); PIDFILE-ABSENT at all three sites on **both**
venues with a `/proc/self/fd` pipe census per test; GRANDCHILD-UNKILLED at all three sites plus the
instrumented branch trace showing site 3's zombie; the zombie red state and its GREEN control; the
live-foreign / zombie / ProcessLookupError / PermissionError paths against the real helper; the deadlock
cycle reproduced deterministically against **both** tees with the wchan/fd table; 20 + 20 pytest rounds of
the three grandchild tests at 4-way concurrency with hard timeouts; the cost probe 15 reps × 3 batches on
both tees back-to-back in one window; the pins and the tee's real SIGTERM window on 3.11, 3.12 **and** 3.13;
the tripwire through the PIN's own checker and its loop-only negative control; `pyflakes`; `lint_delta` from
a reconstructed base; `report_lint.py` and both `ap_screen.py` screens; 21 `file:line` spot-checks by
`sed -n`; the AF-AP-59 regex read from `edit-snapshot.py`; the process census before and after two full
suites.

**Reviewed statically only:**
* That `acp.rs::shutdown()` is a *production* path. I hold only `acp.rs`; its sole `.shutdown()` call is
  inside `#[cfg(test)] mod tests`. Inherited from B5f (≥20 call sites in `lib.rs`/`pool.rs`), **not
  re-derived by me** — and unchanged by this lane.
* The claim that the oracle test's derived-fact assertions are unfalsifiable while the sha holds. That is an
  analytic argument from the code, not a mutant result — no mutant can separate the two.
* F6 rows 3-4 (`ProcessLookupError`, `PermissionError`) were **SIMULATED** with a narrowly-patched `open`;
  the missing guard is primary-source visible at `test:139-141` and `test:118-121`, but I did not force the
  race or a restricted procfs naturally.

**Deliberately skipped, with reason:**
* **The PC leg** (`scripts/pc_suite.sh`, 8 xdist workers). My non-negotiables forbid the bridge and no
  BRIDGE READY banner was in scope. **NOT run by me.** Two findings would read differently there: **F2/F3**
  (a world-scoped `pkill`/`pgrep -a` sweep is far more likely to misfire under 8 workers — that is what
  AF-AP-59 was logged for) and **F15** (tmp-dir contention). The `-n 8` gate of record (`101 passed in
  72.81s`) is the coordinator's, not mine.
* **A network re-fetch of `acp.rs@1c8321cd`.** Network beyond localhost is forbidden to me. I used the
  vendored file under its sha256 identity chain and VERIFY-B5f's recorded independent GitHub fetch.
* **The pytest suite on 3.12 / 3.13** — pytest is installed for 3.11 only; no install attempted. The pins and
  the tee's real SIGTERM behaviour ran there standalone instead.
* **`pytest -n 4`** — xdist is not installed here; substituted 4 concurrent pytest processes × 5 waves, twice.
* **Any mutant that signals a pid it did not spawn.** Two other lanes are live on this box. Every CENSUS-*
  variant of mine is enumerate-only or leaves the own-pid kill intact; every kill I issued was
  `os.kill(<pid I started>, 9)`; no `pkill` anywhere.
* **Forcing pid reuse** — the predecessor's arithmetic (32768 pid_max, ~5 pids/s vs ~728/s needed) answers it
  and nothing in this delta changes it.
* **PIPECLOSE-OUTER** (reverting F-B5g-7's inner `finally` as a mutant). Superseded: the direct fd census on
  both venues is stronger evidence than a mutant would have been.
* **A restricted-procfs fixture** for the real `PermissionError` — no way to restrict `/proc` for one process
  here without touching the box.

**Shared-tree hygiene:** `git status --porcelain` empty at the start; at the end the shared tree carries
another lane's work (`M proofs/S0-01/check_acp_conformance.py`, `M proofs/S0-01/negative_contract.py`,
`M tests/test_s0_01_check_acp_conformance.py`, `?? tasks/briefs/s0-01-a5j-support/A5j-report.md` — lane A5j).
**`git status --porcelain` on my three graded paths is EMPTY at every checkpoint including the last**
(`proofs/S0-01/tools/frame_tee.py`, `tests/test_s0_01_frame_tee.py`,
`proofs/S0-01/vendor/buzz-acp/acp.rs`). No
`stash/checkout/restore/reset/add/commit/push`; the vendored `acp.rs` in the repo was never written (only
scratch copies); all three graded files re-hashed to `8dfdeb7f704d` / `d1be6adf7ff3` / `44e828617636` after
every mutant batch (the runner asserts it on restore). Zero live processes of mine at the end; zero orphaned
`time.sleep` grandchildren anywhere on the box.

---

# VERDICT

# NOT-READY

**This round did real work and closed five of the predecessor's findings for good** — F-B5g-2 (the `:1517`
comment plus a regex that now runs over both files), F-B5g-5 (the AP-screen block reproduces exactly),
F-B5g-6 / F14 (the header is finally honest), **F-B5g-7 (proved at the fd table on both venues, not argued)**
and F-B5g-10. The vendored oracle is the right instrument with an exemplary provenance record; the zombie
semantic is correct in both directions and its "refusing to kill a foreign pid" negative genuinely refuses;
the AP_SCREEN import kills four spellings including a `shell=True` form the hand-typed pin never would have;
the AST pin kills the two `/proc`-walk censuses; the cost is 0.94× the parent; the pins are identical on
three interpreters; 23 of 39 mutants die to a named test.

**It is NOT-READY because four of the closures do not hold, and two of them are the closures the round was
opened for.**

**Blocking set:**

| # | finding | one-line reason |
|---|---|---|
| **F1** | the constant is a token check in disguise | `FALSECONST-ORDER` (order reversed, all six sites consistent) → **`101 passed in 187.90s`**. F-B5g-1's class is open, relocated not closed. |
| **F2** | AF-AP-59 coverage **regressed** | `CENSUS-PKILL-DQ` — a double-quoted world-scoped `pkill -f`, the member of the class that actually kills — **survives**; the deleted hand-typed pin caught it. |
| **F4** | F-B5g-8 reported closed, is not | `GRANDCHILD-UNKILLED-S3` **survives** (`1 passed in 61.61s`); site 3's grandchild is `state=Z` at census. `range(6000)` cannot work by construction and costs 16 s a run. |
| **F9** | F-B5g-9 reported structurally fixed, is not | the deadlock cycle **reproduces deterministically on the PIN's tee** (wchan/fd table); the mandated structural pin does not exist (`"blocking"` and `"bounded reader"` occur 0 times in the file) and its absence is not in NOT_DONE. |

**Non-blocking but must be answered in the next round's report:** F3 (CENSUS-PGREP-A survives — an inferred
claim that is false when measured; plus the AST pin's module-scope/lambda holes), F5 (the citations are not
asserted although the brief mandated it and the DONE table claims it "by construction"), F6 (the parent's
`except ProcessLookupError` was dropped), F7 and F8 (a killer line attributed to the wrong mutant and five
wrong `file:line` refs, three of them the parent's — third round running; `report_lint.py` now makes this a
one-command gate), F10-F13 (stale `30 s` comment, dead `_KILL_SITES` with a self-contradicting comment, the
seventh-site residual, the count-not-presence shape).

**Cheapest path to MERGE-READY:** F1 and F5 are the same fifteen lines (build the expected clause and the
expected citations from the derived facts and compare by equality); F2 and F3a are one alternative each added
to the AF-AP-59 row in `edit-snapshot.py`, which the test then inherits; F4 is a two-line DONE-table
correction plus reverting `range(6000)`; F9 is the ~15-line structural pin printed in the finding plus moving
one `stdin.close()`. None of the four blockers needs a redesign — F1 is the only one that needs thought, and
its fix is the one the design was already reaching for.

**Caveat on the verdict:** this is a **sandbox-only, single-worker grade with two other lanes on the box**;
the PC `-n 8` leg was **not run by me**, and F2/F3 are precisely the findings a multi-worker venue would
sharpen. Nothing in my blocking set depends on a claim I did not reproduce myself.
