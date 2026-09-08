# VERIFY-B5i — adversarial grade of lane B5i (S0-01 frame tee, round 14) at PIN `75998e7`

**VERDICT: NOT-READY.** Three findings block: the equality that item 1 exists to build is a **three-site
mirror** — the exact order-reversed sentence B5h's F1 was opened for is back in the tee's constant and module
docstring with **`114 passed in 170.24s`** (VB-F1); a **paraphrased** false shutdown sentence beside the true
clause in that same docstring survives (VB-F2, the SEVENTH-SITE class re-opened by paraphrase); and the
structural hang pin **misses four read shapes**, one of which reproduces the identical deadlock on the PIN's
own tee (VB-F4). All three have a red-green-validated minimal fix below. The committed report also fails its
own mechanical gate at the PIN (`MISS 18`, VB-F7) — caused by the coordinator's 6-line insertion, not by the
lane.

Everything else in the contract held under attack and is reproduced here: the census helper's branches, the
kill/identity fail-closed paths, the AST kill pin as a subtraction (four scopes, two of them new), the
`S0_01_AGENT` domain (seven shapes), the identity re-sample (20/20 + 50 trials under load), the self-sweep
re-runs (R19, R18, R12/SIGUSR1), both sandbox gates and the PC `-n 8` gate of record.

**Venue.** Every measurement below ran from `git archive` copies of the PIN (`75998e7`) and of the TRUE parent
for the two scope files (`63b582c`; verified: `git diff 63b582c 75998e7^ -- <the two files>` is empty) under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vb14/`. Every mutant on a scratch
copy; every pytest run with an explicit `--basetemp` under that dir; every process I started killed by pid;
no `pkill`/`pgrep`; no `git stash/checkout/restore/reset/add/commit/push`. Interpreter `python3` = 3.11.15
(byte-identical to `/root/venv-agent-factory/bin/python`, both pytest 9.1.1), `S0_01_VENUE=sandbox`,
`S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden`. Load pasted beside every timing.

---

## ITEM 0 — the mechanical gates, pasted

```
$ python3 scripts/report_lint.py tasks/briefs/s0-01-b5i-support/B5i-report.md --rev 75998e7 \
      --map tee=proofs/S0-01/tools/frame_tee.py --map test=tests/test_s0_01_frame_tee.py
report_lint: 159 refs — OK 127, NEAR 4, MISS 18, UNCHECKABLE 7, UNRESOLVED 3 (at 75998e7)
```
→ **VB-F7** below. All 18 MISS and all 4 NEAR are `test:` refs at or after `test:3486` `if lost:`, each **exactly +6 lines**
off (verified by `sed -n` on the PIN: the report's `test:3649` `cites_shutdown.append((name, int(match.group(1)), int(match.group(2))))` content sits at
`test:3655` `assert (start, end) == (sd_start, sd_end), (`; its `test:3619` `# --- (c) EQUALITY: the sentence is BUILT from the derived facts ---`
at `test:3625` `assert PINNED_SHUTDOWN_CLAUSE == expected_clause, (`; its `test:3486` `if lost:` at `test:3492` `"trial %d: no marker on stderr, so the resample ran -- it must "`). The 3 UNRESOLVED are the string `acp.rs :421-444` inside mutant NAMES
(`CITE-421`) that the linter cannot resolve — not references the lane typed as fact.

```
$ python3 scripts/ap_screen.py --tests tests/test_s0_01_frame_tee.py      # PIN bytes
--- TEST_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-66: 1
    tests/test_s0_01_frame_tee.py:1039: timer.daemon = True

$ python3 scripts/ap_screen.py proofs/S0-01/tools/frame_tee.py            # PIN bytes
--- AP_SCREEN over 1 path(s): 13 hits over 1 files ---
AP-24: 4 (:368 :376 :395 :473)   AP-1: 3 (:116 :126 :259)   AF-AP-55: 2 (:244 :284)
AP-51: 2 (:6 :7)   AF-AP-58: 1 (:229)   AP-32: 1 (:67)
```
**AF-AP-59 produces ZERO hits on the test file** — reproduced. The lane's pin reads the REGISTRY ROW, not a
copy: `test:42` `_es_spec.loader.exec_module(_es_mod)` loads `.claude/hooks/edit-snapshot.py` and
`test:43` `AP_SCREEN = _es_mod.AP_SCREEN + _es_mod.TEST_SCREEN`; `scripts/ap_screen.py:26` `spec = importlib.util.spec_from_file_location("es", ROOT / ".claude" /`
loads the same file the same way, so tool and test read one source. `git diff 75998e7^ 75998e7 --
.claude/hooks/` is **empty** — the lane did not patch the hook. Every other screen hit classified by running
it (below, item 9).

Gates I re-ran myself, verbatim, on the PIN copy:
```
# run 1   LOAD-BEFORE 0.47 3.04 4.30
114 passed in 170.88s (0:02:50)          pytest-exit: 0
# run 2   LOAD-BEFORE 1.76 2.33 2.27
114 passed in 169.81s (0:02:49)          pytest-exit: 0
# PC gate of record (the carve-out), clean detached worktree at 75998e7, patch 0B, -n 8
pytest-summary: 114 passed in 41.66s     pytest-exit: 0     RUN_ID 20260908T041241Z-75998e7
$ python3 -m pyflakes proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py     rc=0 (no output)
```
Counts agree across two sandbox runs and the 8-worker PC run: **114**.

---

## ITEM 1 — B5h F1-F16 closure table (every row reproduced by me unless the cell says otherwise)

| B5h | claim | closed by | red-before I reproduced | green I reproduced | verdict |
|---|---|---|---|---|---|
| F1 BLOCK | constant is a token check | equality at `test:3625` `assert PINNED_SHUTDOWN_CLAUSE == expected_clause` | B5h's own FALSECONST-ORDER on the parent: `2 passed, 99 deselected in 0.23s` | same mutant on the PIN: `1 failed, 1 passed, 112 deselected in 0.35s` at `test:3625` | **PARTLY CLOSED — VB-F1: relocated into the test's two hand-typed halves** |
| F2 BLOCK | AP_SCREEN lost the double-quoted spelling | coordinator's registry row | (in the PIN) | CENSUS-PKILL-DQ / -PGREP-A / -WORLD all die at `test:3014` `assert not hits` | CLOSED |
| F3a MED | one CENSUS spelling survived | coordinator's registry row | — | as above | CLOSED |
| F3b MED | AST pin was an inclusion form | subtraction at `test:3017` `def test_kill_calls_only_at_allowed_sites` | KILL-MODULE-LEVEL and KILL-LAMBDA both **survive on the parent** (`2 passed, 99 deselected`) | both die on the PIN at `test:3059` `assert not violations`; my two NEW scopes (class body, comprehension) die too | CLOSED |
| F4 BLOCK | `range(6000)` cannot work; silent skip | branch return + per-site assertion | site 3 on the parent: `1 passed, 100 deselected in 61.57s` | site 3 on the PIN: `1 passed, 113 deselected in 31.00s`; GRANDCHILD-UNKILLED dies at sites 1/2 (`test:171`), survives at site 3 by construction | CLOSED — **but VB-F5: a 4th call site still discards the branch** — src `assert gone, "grandchild pid %d still alive after kill" % gc_pid` |
| F5 MED | citations unasserted | `test:3655` `assert (start, end) == (sd_start, sd_end)` | CITE-421 survived on the parent (B5h) | CITE-421 / CITE-421-TEST / CITE-KPG-2324 all die | CLOSED |
| F6 MED | kill lost its `ProcessLookupError` guard | `test:152` `os.kill(gc_pid, sig.SIGKILL)` inside `try` | PROCESSLOOKUP-UNGUARDED → `ProcessLookupError` at `test:152` `os.kill(gc_pid, sig.SIGKILL)` | four-path driver green; PERMISSION-UNGUARDED dies at `test:3337` | CLOSED — src `try:` `with pytest.raises(AssertionError) as excinfo:` |
| F7 MED | killer line named from memory | pasted killers | — | I re-derived every killer line from my own runs; all pre-`test:3452` refs verify | CLOSED (see VB-F7 for the post-3452 shift) — src `def test_resample_that_loses_the_race_is_loud_not_silent(self, tmp_path):` |
| F8 MED | wrong `file:line` refs | — | — | 36 refs spot-checked by `sed -n` on the PIN: all correct below `test:3452` | CLOSED / superseded by VB-F7 — src `def test_resample_that_loses_the_race_is_loud_not_silent(self, tmp_path):` |
| F9 BLOCK | hang class not closed | `test:3062` `def test_no_unbounded_tee_pipe_reads` + `test:175` `def _read_with_deadline` | structural walk on the parent flags **6** sites (`:407 :459 :515 :1785 :2209 :2607`); deadlock reproduced on the parent tee with the wchan/fd table | 0 sites on the PIN; `test:3110` `def test_a_silent_agent_cannot_wedge_a_bounded_read` green; HANG-REINTRODUCED-STDIN dies at `test:2772` `tee_proc.wait(timeout=30)` in 75.47 s | **PARTLY CLOSED — VB-F4: four read shapes evade the pin** |
| F10 LOW | stale 30 s comment | `test:2703` `# grandchild streams a2c frames for 30 s` above `test:2706` `"for i in range(3000):\n"` | — | comment and code agree | CLOSED — src `"for i in range(3000):\\n"` |
| F11 LOW | `_KILL_SITES` dead code | removed | — | `grep -c _KILL_SITES` = 0 on the PIN (parent had it at `:49`) | CLOSED |
| F12 LOW | false sentence beside the clause | residue guard `test:3667` `assert token not in residue` | B5h's SEVENTH-SITE text | that text dies at `test:3667` | **RE-OPENED BY PARAPHRASE — VB-F2** |
| F13 LOW | file-wide COUNT, not per-site | `test:3639` `assert clause_norm in doc_norm` | SITECOUNT-DUP survived on the parent (B5h) | SITECOUNT-DUP dies at `test:3639` | CLOSED |
| F14 INFO | module imported at collection | `tee:34` `# imported by tests/test_s0_01_frame_tee.py` | — | line present | CLOSED |
| F15 INFO | disk pressure | — | — | `df -h /` was 85 % / 5.7 G free when I started; 79 % / 7.9 G free after I deleted my 2.0 G of venues | noted |
| F16 INFO | B5h's own instrument error | — | — | n/a | noted |

---

## FINDINGS

### VB-F1 [BLOCKING] SOLID — the equality is a THREE-SITE MIRROR: B5h's F1 sentence is back, with the full suite green

`test:3620` `kill_half = "SIGKILLs the group (killpg)"` and
`test:3621` `wait_half = "waits up to %d s for the child to exit" % wait_secs` are **hand-typed strings**. Only two things about the sentence are derived from
`acp.rs`: the seconds (`wait_secs`) and which half comes first (`kill_line < wait_line`). The CONTENT assigned
to each ordinal is not derived at all — so swapping what the test calls the two halves, and updating the
constant and module docstring to match, produces the exact order-reversed sentence F1 was opened for.

- **Failing input** (mutant MIRROR-3SITE-ORDER, three edits): at `test:3620-3621` swap the two half strings (src `kill_half = "SIGKILLs the group (killpg)"`)
  (`kill_half` becomes the wait text, `wait_half` becomes the kill text); set `tee:51-54` (src `PINNED_SHUTDOWN_CLAUSE = (`)
  `PINNED_SHUTDOWN_CLAUSE = (` to `"buzz-acp waits up to 5 s for the child to exit first and then" " SIGKILLs
  the group (killpg)"`; rewrite the same sentence in the module docstring at `tee:15-16` `buzz-acp SIGKILLs the group (killpg) first and then waits up to 5 s`.
- **Observed:** the tee's docstring now reads *"buzz-acp waits up to 5 s for the child to exit first and then
  SIGKILLs the group (killpg)"* — false against the source I re-derived below — and

```
LOAD-BEFORE 1.05 1.35 2.85
114 passed in 170.24s (0:02:50)
pytest-exit: 0
```
- **Expected:** a sentence contradicting the derived `kill_line < wait_line` cannot be stated in the repo.
- **Why this is F1 and not a new class:** B5h's F1 was "a false constant consistent across every site passes".
  The lane closed the two-site version; the three-site version costs one more line of the same edit and the
  reader of the tee still budgets a 5 s grace period that does not exist.
- **Minimal fix** (2 assertions, immediately after `test:3621`), red-green validated by me:
```python
        assert "SIGKILL" in kill_half and "killpg" in kill_half, (
            "the kill half must name the signal and helper the source uses")
        assert ("%d s" % wait_secs) in wait_half and "waits" in wait_half, (
            "the wait half must name the derived bound")
```
- **Exact red test:** with the fix applied to the clean PIN → `2 passed, 112 deselected in 0.37s`; with the
  fix applied to MIRROR-3SITE-ORDER → `1 failed, 1 passed, 112 deselected in 0.34s`, at the inserted assertion
  (it lands where `test:3622` `first_half, second_half = ((kill_half, wait_half) if kill_line < wait_line` sits
  on the PIN).
- Weaker sibling, also measured: MIRROR-3SITE (change "for the child to exit" → "for the socket to close" in
  the constant, the docstring and `test:3621`) → `2 passed, 112 deselected in 0.35s`. (src `wait_half = "waits up to %d s for the child to exit" % wait_secs`)

### VB-F2 [BLOCKING] SOLID — a PARAPHRASED false sentence beside the true clause in the module docstring survives (B5h F12 re-opened)

The negative direction is a two-token blacklist: `test:3667` `assert token not in residue` over
`("killpg", "5 s")`, plus `test:3673` `assert "SIGTERM" not in head`. A paraphrase evades all three.

- **Failing input** (mutant SEVENTH-SITE-PARAPHRASE), appended to the module docstring right after
  `tee:18` `leg's evidence is its last RUNNING status (A21d).`:
  *"A wedged leg therefore gets a grace period in which it may still flush, and buzz-acp sends a terminate
  signal before that grace period starts."*
- **Observed:** `2 passed, 112 deselected in 0.38s`. **Expected:** dead.
- Both halves are false against the source: `acp.rs` contains **0** occurrences of `SIGTERM` (the test itself
  derives this at `test:3546` `assert oracle.count("SIGTERM") == 0`), and the group kill precedes the wait, so
  there is no pre-kill grace period. This is the same reader-harm B5h F12 measured, at the canonical site.
- The lane's own literal version does die — I reproduced it: B5h's SEVENTH-SITE text (which contains `5 s`)
  fails at `test:3667`, and SWEEP-tests R14's sentence (which contains `killpg`) fails at `test:3667`. Only (src `assert token not in residue, (`)
  the token list is holding.
- **Minimal fix:** make the residue guard structural instead of a blacklist — after building `residue`, split
  the module docstring into sentences and require every sentence naming `buzz-acp` outside the parenthetical
  `(client)` introduction to be exactly `PINNED_SHUTDOWN_CLAUSE`'s sentence:
```python
        for sent in re.split(r"(?<=\.)\s+", doc_norm):
            if "buzz-acp" in sent and "(client)" not in sent:
                assert clause_norm in sent, (
                    "a second sentence in the module docstring speaks for buzz-acp: %r" % sent)
```
- **Exact red test:** that assertion over the mutated docstring; the clean PIN passes it (the only other
  `buzz-acp` mention in the docstring is `tee:2` `stdio proxy: preserve raw ACP JSON-RPC frames between
  buzz-acp (client) and hermes-acp (agent).`). *(fix drafted, not run — I validated the fixes for VB-F1,
  VB-F4 and VB-F5 by execution and say so; this one is reviewed only.)*

### VB-F3 [MED] SOLID — a false shutdown sentence OUTSIDE the five named sites survives, in either file

The lane's SELF-ATTACK 2 concedes the named-list limit but states the wrap-tolerant regex at `test:3741` (src `assert not re.search(`)
`assert not re.search(` is the guard that runs over both files. Measured: that regex matches only the literal
`SIGKILLs the group after 5 s`, so a paraphrase passes.

- **Failing inputs** (both on the PIN): SIXTH-SITE-TESTDOC — add to `test:3169` (src `"""F14/B5e: after SIGTERM, the agent child pid is gone within 2 s."""`)
  `"""F14/B5e: after SIGTERM, the agent child pid is gone within 2 s."""` the sentence *"buzz-acp gives a
  wedged leg a 5 s grace period before it SIGKILLs anything, so a late flush is still recorded."* →
  `2 passed, 112 deselected in 0.35s`. SIXTH-SITE-TEECOMMENT — the same sentence as a comment above
  `tee:476` `# stdin pump: use raw fd to avoid BufferedReader lock SIGABRT at shutdown (V-c F1)` →
  `2 passed, 112 deselected in 0.41s`.
- **Expected:** the increment's stated goal is "one sentence in the repo"; a second, false one is admissible
  anywhere outside six enumerated places.
- **Minimal fix:** replace the two literal regexes with one derived ban over both files — for the derived
  `wait_secs`, no line outside `PINNED_SHUTDOWN_CLAUSE`'s own sites may contain both a kill token
  (`SIGKILL`/`killpg`) and the seconds token (`%d s` % wait_secs) within a two-line window.

### VB-F4 [MED] SOLID — the structural hang pin misses four read shapes; the iteration form reproduces the identical deadlock on the PIN's tee

`test:3062` `def test_no_unbounded_tee_pipe_reads` keys on `node.func.attr not in ("read", "readline",
"communicate")` (`test:3089` `if node.func.attr not in ("read", "readline", "communicate"):`) with the receiver NAME `tee_proc` (`test:3098` `if base != "tee_proc":`). Its
docstring documents **only** the alias limit ("a pipe bound to another local is out of its reach").

Measured on the PIN, each mutation applied to `test:3145` `line = _read_with_deadline(tee_proc.stdout, 5)`
inside the committed hang test:

| shape | the pin's own walk | `test_no_unbounded_tee_pipe_reads` | documented? |
|---|---|---|---|
| `next(iter(tee_proc.stdout), None)` | `UNBOUNDED-TEE-PIPE-READS: 0` | `1 passed` | **no** |
| `tee_proc.stdout.readlines()` | `0` | `1 passed` | **no** |
| `os.read(tee_proc.stdout.fileno(), 65536)` | `0` | `1 passed` | **no** |
| `_p = tee_proc.stdout; _p.readline()` | `0` | `1 passed` | yes |

The first shape is not academic — it re-opens the F9 deadlock on the PIN's OWN tee:
```
HANG: bare readline still blocked at 12.0 s   (next(iter(tee.stdout), None), PIN tee)
  tee pid 7671 state=S threads=['7671', '7674']
    tid 7671 wchan=hrtimer_nanosleep        <- the tee's drain loop
    tid 7674 wchan=anon_pipe_read           <- the c2a reader on the tee's stdin
PROBE RESULT: DEADLOCK REPRODUCED (tee SIGKILLed by pid)
```
- **Minimal fix** (red-green validated by me): pin every MENTION of a tee pipe, not three call spellings —
  collect `Attribute(value=Name('tee_proc'), attr in ('stdout','stderr'))`, skip those enclosed in `BOUNDED`,
  and allow only four parents: an argument to a `BOUNDED` helper, `.close()`, a keyword argument (handing the
  pipe to another `Popen`, which `test:1449` `stdin=tee_proc.stdout,` legitimately does), or a read carrying
  its own `timeout=`.
- **Exact red test:** with that fix on the clean PIN → `1 passed, 113 deselected in 0.44s`; with it on each of
  the four shapes above → `1 failed` in every case (iteration, readlines, os.read/fileno, alias).

### VB-F5 [MED] SOLID — a fourth `_kill_own_grandchild` call site discards its branch, so the zombie test does not test the zombie semantic

Item 2 of the brief required each site to state the branch it can produce. Three do
(`test:653` and `test:1268` `assert _kill_own_grandchild(framedir) == "live"`, and
`test:2788` `assert _kill_own_grandchild(framedir) == "gone"`). The fourth, at `test:2857` `_kill_own_grandchild(framedir)`
inside `test:2802` `def test_zombie_grandchild_is_already_gone`, throws the return value away.

- **Failing input** (mutant ZOMBIE-BRANCH-LIVE): change that test's grandchild from
  `time.sleep(0.3)` to `time.sleep(30)` so it is **alive** at census time → the helper takes the LIVE branch
  and kills it → `1 passed, 113 deselected in 1.88s`. The test named `..._is_already_gone` passes while the
  grandchild was never gone.
- **Minimal fix:** make `test:2857` `_kill_own_grandchild(framedir)` read `assert _kill_own_grandchild(framedir) == "gone"`.
- **Exact red test, run:** clean PIN + fix → `1 passed, 113 deselected in 1.77s`; ZOMBIE-BRANCH-LIVE + fix →
  `1 failed, 113 deselected in 1.93s`.

### VB-F6 [MED] SOLID — the AF-AP-55 `OSError` guard has no deterministic test; its only coverage is a race that is silent when the box is idle

Item 6 of the brief required "a `try/except OSError` that records *exited before identity* rather than
crashing". The guard exists at `tee:284-289` `rp = os.readlink("/proc/%d/exe" % proc.pid)`. Removing the
`try`/`except` around it (mutant RESAMPLE-NO-OSERROR-GUARD) is:

```
idle       (load 1.1)  2 passed, 112 deselected in 6.18s        <- SURVIVES
under load (load 2.7)  1 failed,  113 deselected in 5.04s at test:3491   <- dies
```
- **Expected:** a committed guard has a test that fails without it, on any box.
- **Minimal fix:** lift the readlink+hash out of the closure into a module-level
  `_reread_interpreter(pid)` returning `(realpath, sha) | None`, and unit-test it with a pid above
  `/proc/sys/kernel/pid_max` — the same deterministic trick `test:3312` (src `def test_pid_that_raced_us_to_exit_reports_gone(self, tmp_path, monkeypatch):`)
  `def test_pid_that_raced_us_to_exit_reports_gone` already uses for `ProcessLookupError`.
- **Exact red test:** `assert _reread_interpreter(pid_max + 1) is None` plus a capsys assertion on
  `agent interpreter re-sample: exited before identity`; delete the `except` → `AttributeError/OSError`.

### VB-F7 [MED] SOLID — the report committed in the PIN fails `report_lint --rev 75998e7`: `MISS 18, NEAR 4`

Every failing ref is a `test:` ref at or after `test:3486`, off by exactly **+6** lines. Mechanism: the
coordinator's 6-line docstring insertion into `test:3452`
`def test_resample_that_loses_the_race_is_loud_not_silent` landed after the lane's `report_lint` run, so every
later reference in the committed report now points into the wrong statement (e.g. the report's line 103 cites
`test:3619` for `assert PINNED_SHUTDOWN_CLAUSE == expected_clause`; at the PIN that line reads (src `# --- (c) EQUALITY: the sentence is BUILT from the derived facts ---`)
`# --- (c) EQUALITY: the sentence is BUILT from the derived facts ---` and the assertion is at `test:3625`). (src `assert PINNED_SHUTDOWN_CLAUSE == expected_clause, (`)
- **Minimal fix:** add 6 to the 22 flagged `test:` refs (or re-run the lane's harvest at the PIN) and paste
  `report_lint --rev <PIN>` with `MISS 0` in the checkpoint.
- Brief item 0 says "MISS 0 **or a finding**" — this is the finding.

### VB-F8 [LOW] SOLID — the report's FILE IDENTITY table is stale for the test file at the PIN

`B5i-report.md` FILE IDENTITY claims `tests/test_s0_01_frame_tee.py` = `2b5479158898710a…` / **3738** lines.
At the PIN it is `bd75f470d039a7c9…` / **3744** lines. (The tee row is correct:
`49e3cce4b280a1273cf39a60f6d137c41c9f779cb4c61de1b69e9b84684f5801` / 542 lines, matching the PIN exactly.)
Same cause as VB-F7. **Fix:** re-stamp the row from the PIN bytes.

### VB-F9 [LOW] SOLID — SWEEP-tests row 12.1 is NOT fixed: the AF-AP-58 pin is still blind to the signal's identity

The brief's item 9 named 12.1 among the rows the lane "must have found and fixed". The lane's table classes it
**S** ("the SIGUSR1 mutant dies ten times over in neighbours"). Reading `test:2955` (src `def test_no_statement_between_signal_and_try(self, tmp_path):`)
`def test_no_statement_between_signal_and_try`, the pin matches any `signal.signal` call
(`test:2975` `and func.attr == "signal"`) and never inspects the first argument.
- The lane's escape claim is **true, and I measured it**: swapping `tee:229`
  `signal.signal(signal.SIGTERM, _sigterm_handler)` to `signal.SIGUSR1` gives
  `10 failed, 104 passed in 176.38s (0:02:56)` — first failure `assert -15 == 70` at `test:3247`. (src `assert tee_proc.returncode == 70`)
- Residual: the pin itself would not notice, so the class rests entirely on the SIGTERM behaviour tests.
- **Minimal fix (1 line)** beside `test:2978` `assert signal_idx is not None, "signal.signal call not found in main()"`:
  `assert stmt.value.args and getattr(stmt.value.args[0], "attr", "") == "SIGTERM", "handler installed for the wrong signal"`.

### VB-F10 [LOW] SOLID — the coordinator's relaxed race assertion is CORRECT but pins almost nothing on its own

Graded as instructed. **The diagnosis in the docstring is right, and I reproduced it twice:**
1. Parent tee, two-stage agent, 20 trials, block shape: **19 × `/usr/bin/bash`, 1 × `/usr/bin/python3.11`** —
   the SPAWN-TIME readlink already raced the child's `exec` and won once, with no re-sample in that tee at all.
2. PIN tee, exit shape (agent answers and exits at once), **50 trials under load 2.7**: the stderr marker
   appeared **6/50**, and in **6 of 6** of those the record already said `/usr/bin/python3.11`; **0** said
   bash. Idle (load 1.1), 20 trials: marker 0/20, python 20/20.
   So the original "lost ⇒ bash" assertion was false and would flake exactly as trial 11 did.
**But** with a bash→python agent the recorded path can only ever be one of those two images, so
`assert seen in (bash_real, python_real)` in the lost branch is near-vacuous. Measured: a tee whose re-sample
ALWAYS fails (mutant RESAMPLE-ALWAYS-FAILS, `raise OSError` before the readlink) passes
`test_resample_that_loses_the_race_is_loud_not_silent` and is killed only by the sibling
`test:3383` `def test_interpreter_is_resampled_at_the_first_a2c_byte` (`1 failed, 1 passed, 112 deselected in
11.75s`). What the relaxed test still pins by itself: the sha coherence
`identity["agent_interpreter_sha256"] == _sha256_file(seen)` in both branches, `rc == 0`, and the won branch's
`seen == python_real`. **Suggested strengthening (not a blocker):** in the lost branch also assert that at
least one trial WON across the 20 (`assert any(...)`), so an always-losing tee cannot ride this test at all.

### VB-F11 [INFO] SOLID — the FIFO shape is claimed in the report but has no committed test

The report's item-7 green cell says rc 64 "in all four shapes" and its prose adds "(directory, plain file and
FIFO)". There is no `mkfifo` anywhere in the test file. I verified the behaviour independently (below): a
0755 FIFO does give `rc=64` + `frame_tee: S0_01_AGENT is not an executable file`. **Fix:** add the FIFO case
to `test:874` `def test_non_executable_agent`, or drop the claim.

### VB-F12 [INFO] SOLID — item 16 answered: the corpus `tee_sha256` mismatch is DECLARED, but as an unconditional two-way accept, and the mint WILL hit it

`tests/test_s0_01_check_acp_conformance.py:2732-2739` `def test_real_leg_runtime_identity` accepts either
outcome: `if ok: pass  # no failure at all — acceptable` else it requires the failure string to be exactly
`f"{leg}: tee_sha256 mismatch"`. That is **not** a `_CORPUS_VERSION == "v2.2"` xfail (the process-evidence and
tee-status tests at `:2795-2809` and `:4003-4007` use strict `_CORPUS_VERSION` xfails; this one does not), so
it will never retire itself. Run at the PIN against the declared corpus:
```
repo tee sha (PIN): 49e3cce4b280a1273cf39a60f6d137c41c9f779cb4c61de1b69e9b84684f5801
  run-1     check_runtime_identity: FAIL -> run-1: tee_sha256 mismatch
  cancel    check_runtime_identity: FAIL -> cancel: tee_sha256 mismatch
  shutdown  check_runtime_identity: FAIL -> shutdown: tee_sha256 mismatch
  two-users check_runtime_identity: FAIL -> two-users: tee_sha256 mismatch
```
The corpus records `ed1c38f100af22cc…`, which matches neither the parent's tee (`8dfdeb7f704dfd59…`) nor the
PIN's — the lane is right that it predates them and right not to touch it. **Owner action, out of B5i's
scope:** re-capture the corpus with the current tee before any S0-01 mint, and make that acceptance
version-gated so it cannot outlive the capture.

### VB-F13 [INFO] SOLID/static — item 17: no `S0_01_AGENT` producer is broken by the new check

Producers at the PIN: `proofs/S0-01/tools/pc/pc_launch.py:162` and `proofs/S0-01/tools/pc/pc_negative.py:25`,
both `"S0_01_AGENT": pins.PINNED_AGENT_REALPATH` = `/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp`
(`proofs/S0-01/pins.py:14`) — absolute, a venv console script, never a shell string and never relative. The
tee is genuinely on that path: buzz-acp is launched with `--agent-command PINNED_TEE_PATH`
(`proofs/S0-01/pins.py:39`). Measured behaviour change on all seven domain shapes (parent → PIN): rc 1 +
traceback → rc 64 + named line, including a shell string `"<python> <script>"` (rc 64, "not an executable
file"). No shape regresses. **Residual (UNSURE, static only):** I did not stat the PC file — the one bridge
action I was allowed was the pytest gate. Cheap confirmation for the coordinator:
`ls -l /home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp` (must be a regular file with an execute bit for
the buzz-acp service user).

### VB-F14 [INFO] SOLID — the hang class is closed TEST-SIDE only; the tee still wedges any unbounded reader

The same probe deadlocks against BOTH tees with the identical signature (parent tee, pid 6044: main thread
`hrtimer_nanosleep`, c2a reader `anon_pipe_read`, `TEST fd 4 -> pipe:[256104]` == `TEE fd 0 -> pipe:[256104]`;
PIN tee, pid 6423: same). That is the documented design (drain to EOF, no stall timeout, buzz-acp's killpg is
the real bound) — recorded so "the hang class is closed" is not read as a tee fix.

### VB-F15 [INFO] — my own instrument error, corrected before it became a finding

My first KILL-MODULE-LEVEL / KILL-LAMBDA / CENSUS-PGREP-X insertions went in at list index 62, which is
**inside** the `FAKE_AGENT_CODE` triple-quoted string that starts at `test:62` `FAKE_AGENT_CODE =
textwrap.dedent("""\`. They parsed, ran, and appeared to SURVIVE. Re-inserted at true module scope (after
`test:60` `_DEV_FULL = "/dev/full"`), all of them die. The survivals in the table below are only the ones I
re-confirmed at module scope.

---

## MUTANT TABLE — 51 runs, 51 ran

On the PIN: **38 killed, 12 survive** — 2 of those declared (GRANDCHILD-UNKILLED-S3 by construction,
PIPEREAD-ALIAS as the pin's documented limit) and **10 are the findings above**. Three further runs are
red-before evidence on the PARENT, where the mutant survives by design (FALSECONST-ORDER, KILL-MODULE-LEVEL,
KILL-LAMBDA). `ran` = executed; every killer line below is from the run, re-anchored to the PIN's bytes where
the mutation itself shifted the file.

| # | mutant | venue | result | killer / evidence (from the run) |
|---|---|---|---|---|
| 1 | FALSECONST-ORDER (B5h text, 7 sites) | parent | **SURVIVES** (red-before) | `2 passed, 99 deselected in 0.23s` |
| 2 | FALSECONST-ORDER (2 sites) | PIN | KILLED | `test:3625` equality, `1 failed, 1 passed, 112 deselected in 0.35s` — src `assert PINNED_SHUTDOWN_CLAUSE == expected_clause, (` |
| 3 | CONST-ORDER | PIN | KILLED | `test:3625`, `0.40s` — src `assert PINNED_SHUTDOWN_CLAUSE == expected_clause, (` |
| 4 | CONST-WRONGEVENT | PIN | KILLED | `test:3625`, `0.36s` — src `assert PINNED_SHUTDOWN_CLAUSE == expected_clause, (` |
| 5 | DOCSTRING-ORDER | PIN | KILLED | `test:3639` `assert clause_norm in doc_norm` |
| 6 | DOCSTRING-WRONGEVENT | PIN | KILLED | `test:3639` — src `assert clause_norm in doc_norm, (` |
| 7 | DOCSTRING-HYBRID | PIN | KILLED | `test:3639` — src `assert clause_norm in doc_norm, (` |
| 8 | SITECOUNT-DUP | PIN | KILLED | `test:3639` — src `assert clause_norm in doc_norm, (` |
| 9 | SEVENTH-SITE-LITERAL (B5h text) | PIN | KILLED | `test:3667` `assert token not in residue` |
| 10 | **SEVENTH-SITE-PARAPHRASE** | PIN | **SURVIVES** | `2 passed, 112 deselected in 0.38s` → VB-F2 |
| 11 | CITE-421 | PIN | KILLED | `test:3655` `assert (start, end) == (sd_start, sd_end)` |
| 12 | CITE-421-TEST | PIN | KILLED | `test:3655` `assert (start, end) == (sd_start, sd_end), (` (the run named its message line :3657) |
| 13 | CITE-KPG-2324 | PIN | KILLED | `test:3659` `assert (start, end) == (kpg_start, kpg_end)` |
| 14 | COMMENT-TERM (both R1 comments) | PIN | KILLED | `test:3703` `assert ref_norm in _ws_norm(text)` |
| 15 | TESTDOC-TERM | PIN | KILLED | `test:3703` — src `assert ref_norm in _ws_norm(text), (` |
| 16 | **MIRROR-3SITE** ("socket to close") | PIN | **SURVIVES** | `2 passed, 112 deselected in 0.35s` → VB-F1 |
| 17 | **MIRROR-3SITE-ORDER** | PIN | **SURVIVES, FULL SUITE** | `114 passed in 170.24s (0:02:50)` → VB-F1 |
| 18 | **SIXTH-SITE-TESTDOC** | PIN | **SURVIVES** | `2 passed, 112 deselected in 0.35s` → VB-F3 |
| 19 | **SIXTH-SITE-TEECOMMENT** | PIN | **SURVIVES** | `2 passed, 112 deselected in 0.41s` → VB-F3 |
| 20 | ACPRS-SECS9 (`from_secs(5)`→`(9)` on a scratch acp.rs) | PIN | KILLED **first, by the premise** | `test:3540` sha256 mismatch `44e82861… != 053a8cd4…` — src `assert oracle_sha == VENDORED_ACP_RS_SHA256, (` |
| 21 | ACPRS-SECS9-SHAPATCH (premise updated too) | PIN | KILLED | `test:3625` — the derived `9 s` ≠ the constant's `5 s`: the seconds ARE joined — src `assert PINNED_SHUTDOWN_CLAUSE == expected_clause, (` |
| 22 | R14-FALSE-SENTENCE (SWEEP 14.1) | PIN | KILLED | `test:3667` — src `assert token not in residue, (` |
| 23 | GRANDCHILD-UNKILLED — site 1 | PIN | KILLED | `test:171` `assert gone, "grandchild pid %d still alive after kill"`, `5.47s` |
| 24 | GRANDCHILD-UNKILLED — site 2 | PIN | KILLED | `test:171`, `17.49s` — src `assert gone, "grandchild pid %d still alive after kill" % gc_pid` |
| 25 | GRANDCHILD-UNKILLED — site 3 | PIN | SURVIVES — declared by construction | `1 passed, 113 deselected in 31.00s` |
| 26 | **ZOMBIE-BRANCH-LIVE** | PIN | **SURVIVES** | `1 passed, 113 deselected in 1.88s` → VB-F5 |
| 27 | PROCESSLOOKUP-UNGUARDED | PIN | KILLED | uncaught `ProcessLookupError` in `test:3312` `def test_pid_that_raced_us_to_exit_reports_gone(self, tmp_path, monkeypatch):` — the raising call is `test:152` `os.kill(gc_pid, sig.SIGKILL)` (:151 in the mutated file, where the `try` is gone) |
| 28 | PERMISSION-UNGUARDED | PIN | KILLED | `test:3337` DID NOT RAISE — src `with pytest.raises(AssertionError) as excinfo:` |
| 29 | KILL-MODULE-LEVEL | parent / PIN | SURVIVES / KILLED | parent `2 passed, 99 deselected in 0.33s`; PIN `test:3059` `assert not violations, (` with `kill at line 63 in <module scope>` |
| 30 | KILL-LAMBDA (class-body lambda) | parent / PIN | SURVIVES / KILLED | parent `2 passed`; PIN `test:3059` `assert not violations, (` |
| 31 | KILL-CLASSBODY (new) | PIN | KILLED | `test:3060` `"os.kill/os.killpg outside _kill_own_grandchild: %s" % violations)` (:3062 in the mutated file) |
| 32 | KILL-COMPREHENSION (new) | PIN | KILLED | `test:3060` `"os.kill/os.killpg outside _kill_own_grandchild: %s" % violations)` (:3060 in the mutated file) |
| 33 | CENSUS-PKILL-DQ | PIN | KILLED | `test:3014` `assert not hits, (` / `test:3015` `"AF-AP-59 match in test file: %s (%s)" % (hits, msg))` |
| 34 | CENSUS-PGREP-A | PIN | KILLED | `test:3015` `"AF-AP-59 match in test file: %s (%s)" % (hits, msg))` |
| 35 | CENSUS-WORLD | PIN | KILLED | `test:3015` `"AF-AP-59 match in test file: %s (%s)" % (hits, msg))` |
| 36 | CENSUS-PGREP-X | PIN | KILLED | the AST kill pin `test:3059` `assert not violations, (` (:3063 in the mutated file, which is 4 lines longer) |
| 37 | PIPEREAD-UNBOUNDED | PIN | KILLED | `test:3107` `assert not bad, (` |
| 38 | HANG-REINTRODUCED-STDIN | PIN | KILLED | `TimeoutExpired` at `test:2772` `tee_proc.wait(timeout=30)`, `75.47s` |
| 39 | **PIPEREAD-ITERATION** | PIN | **SURVIVES** | pin walk `0`; `1 passed` → VB-F4 |
| 40 | **PIPEREAD-READLINES** | PIN | **SURVIVES** | pin walk `0`; `1 passed` → VB-F4 |
| 41 | **PIPEREAD-OSREAD** | PIN | **SURVIVES** | pin walk `0`; `1 passed` → VB-F4 |
| 42 | PIPEREAD-ALIAS | PIN | SURVIVES — documented limit | pin walk `0`; `1 passed` |
| 43 | IDENTITY-EARLY-ONLY | PIN | KILLED | both identity tests, `10.47s` |
| 44 | RESAMPLE-ALWAYS-SHORTCIRCUIT | PIN | KILLED | both identity tests, `10.46s` |
| 45 | RESAMPLE-ALWAYS-FAILS (new) | PIN | KILLED by the SIBLING only | `test:3421`; the race test passes → VB-F10 — src `assert seen == python_real, (` |
| 46 | **RESAMPLE-NO-OSERROR-GUARD** | PIN | **SURVIVES idle**, dies under load | `2 passed` idle; `test:3491` under load → VB-F6 — src `assert seen == python_real, (` |
| 47 | AGENT-EMPTY-UNGUARDED | PIN | KILLED | `test:870` `assert proc.stderr.decode().strip() == "frame_tee: S0_01_AGENT is empty"` |
| 48 | AGENT-NONEXEC-UNGUARDED | PIN | KILLED | `test_non_executable_agent` + `test_directory_agent` |
| 49 | R19-COLLECTOR (SWEEP 1.1/1.2) | PIN | KILLED | `30 failed, 56 passed, 28 errors in 171.26s (0:02:51)` |
| 50 | R18-DEVFULL (SWEEP 10.5) | PIN | KILLED | `test:921` `assert os.path.exists(_DEV_FULL), (`; `1 failed, 22 passed, 4 skipped` |
| 51 | SIGUSR1-SWAP (SWEEP 12.1) | PIN | KILLED by neighbours | `10 failed, 104 passed in 176.38s (0:02:56)` |

Three additional fix-validation runs (red-green for the fixes in VB-F1, VB-F4, VB-F5) are pasted inside those
findings.

---

## PROBES

### The structural pin, RED on the TRUE parent (`63b582c`), GREEN on the PIN — verbatim
```
=== PARENT ===                              === PIN ===
UNBOUNDED-TEE-PIPE-READS: 6                 UNBOUNDED-TEE-PIPE-READS: 0
  readline at line 407 in test_late_client_frame_recorded_or_exit_70
  readline at line 459 in test_late_frame_agent_stdin_closed_before_handshake
  readline at line 515 in test_agent_stdin_closed_before_handshake_exit_code
  readline at line 1785 in test_agent_exits_without_consuming_stdin_exit_70
  readline at line 2209 in test_late_frame_after_agent_death_recorded
  readline at line 2607 in test_concurrent_main_thread_status_vs_pump
```
The lane's DISCREPANCY 1 is **correct**: `:407` is a sixth site the B5h verdict's list of five missed.

### The deadlock, reproduced on both tees (bounded probe, tee SIGKILLed by pid)
```
PARENT tee: HANG at 12.0 s; tid 6044 wchan=hrtimer_nanosleep, tid 6047 wchan=anon_pipe_read
            TEST fd 4 -> pipe:[256104]   TEE fd 0 -> pipe:[256104]      DEADLOCK REPRODUCED
PIN    tee: HANG at 12.0 s; tid 6423 wchan=hrtimer_nanosleep, tid 6426 wchan=anon_pipe_read
            TEST fd 4 -> pipe:[252519]   TEE fd 0 -> pipe:[252519]      DEADLOCK REPRODUCED
```

### Interpreter identity — two-stage agent (bash `exec`s python)
```
PARENT tee, block shape, 20 trials:  19 x /usr/bin/bash   1 x /usr/bin/python3.11   marker 0/20
PIN    tee, block shape, 20 trials:  20 x /usr/bin/python3.11                        marker 0/20
PIN    tee, exit  shape, 20 idle  :  20 x /usr/bin/python3.11                        marker 0/20
PIN    tee, exit  shape, 50 @load 2.7: 50 x /usr/bin/python3.11   marker 6/50
        lost-the-race trials whose record is already PYTHON: 6 [13, 16, 17, 21, 34, 47]
        lost-the-race trials whose record is BASH:           0
PIN    tee, bash-exec-bash (same realpath), 10 trials: 10 x /usr/bin/bash, marker 8/10 — record still correct
```

### `S0_01_AGENT` domain — seven shapes, parent vs PIN
```
PARENT:  every shape rc=1, traceback, framedir empty
   A empty  PermissionError: [Errno 13] Permission denied: ''      B directory / C plain file / D fifo: same
   E absent / F bad shebang / G shell string: FileNotFoundError
PIN:     every shape rc=64, NO traceback, framedir empty
   A frame_tee: S0_01_AGENT is empty
   B/C/D/E/G frame_tee: S0_01_AGENT is not an executable file: <path>
   F frame_tee: cannot spawn S0_01_AGENT <path>: [Errno 2] No such file or directory
```

### Cost — 15 reps × 3 batches, both tees back to back in one window (load 1.09 1.26 1.78)
```
PARENT sha256 8dfdeb7f704dfd59        PIN sha256 49e3cce4b280a127
PARENT batch0 {"reps":15,"median":0.0536,...}   PIN batch0 {"reps":15,"median":0.0548,...}
PARENT batch1 {"reps":15,"median":0.0543,...}   PIN batch1 {"reps":15,"median":0.0542,...}
PARENT batch2 {"reps":15,"median":0.0529,...}   PIN batch2 {"reps":15,"median":0.0537,...}
per-batch PIN/PARENT: 1.02x / 1.00x / 1.02x     median-of-medians 0.0536 vs 0.0542 = 1.01x
```
The lane's 2.9× regression is gone; DISCREPANCY 5 confirmed.

### Site-3 cost (item 3's "+16 s must be gone")
```
PARENT test_concurrent_main_thread_status_vs_pump: 1 passed, 100 deselected in 61.57s (0:01:01)
PIN    same test:                                   1 passed, 113 deselected in 31.00s
```

### Standalone pins on 3.11 / 3.12 / 3.13 (my own re-derivation, not the lane's script)
```
3.11.15  {'sha_ok': True, 'sigterm': 0, 'kpg': (2323, 2329), 'sd': (422, 444), 'kill<wait': True,
          'secs': 5, 'equality': True, 'doc_carries_clause': True, 'residue_clean': True,
          'head_clean': True, 'cites': ([(422, 444)], [(2323, 2329)]), 'cites_ok': True}
3.12.3   identical      3.13.12  identical
```

### The mechanism, re-derived from primary source (`acp.rs`, sha `44e82861…` verified first)
`fn kill_process_group` opens at **:2323** and its closing brace is at **:2329**; `pub async fn shutdown`
opens at **:422**, closes at **:444**; inside it the group kill (`kill_process_group` / `start_kill`) precedes
`tokio::time::timeout(std::time::Duration::from_secs(5), self.child.wait())`; the file contains **0**
`SIGTERM`. So the lane's DISCREPANCY 4 is **right** — `:2323-2328` stopped one line short of the closing brace
— and `PINNED_SHUTDOWN_CLAUSE` is factually true of this source. One nuance worth a line in the prose: the
source falls back to `start_kill()` (direct child only) when the group kill fails or the child is already
reaped; the clause states only the group-kill path.

### DISCREPANCY 3, verified
```
PARENT  SIGTERM count before "The SIGTERM path": 2   (the B5h F12 guard would FAIL on the parent's own bytes)
PIN     SIGTERM count before "The SIGTERM path": 0   (PASS)
```
The lane said three; `ast.get_docstring` gives two. The substance — that the guard could not be implemented
without moving the paragraph — holds.

### Process census after every run (own-venue scoped, `/proc` walk, no `pgrep`/`pkill`)
```
processes naming my scratch venue (vb14): 1   <- the census command's own shell (pid 11989)
processes with a time.sleep cmdline:      1   <- the same shell (the pattern is in its script text)
live frame_tee.py processes:              1   <- the same shell
```
Zero orphaned `time.sleep` grandchildren, zero live tees, zero pytest of mine. My GRANDCHILD-UNKILLED runs at
sites 1 and 2 do create one un-killed sleeper each by design (30 s and 120 s lifetimes); both had self-exited
by the census.

---

## ITEM 9 — the self-sweep, graded against SWEEP-tests

| row | class | lane's verdict | my re-run | agree? |
|---|---|---|---|---|
| 1.1 / 1.2 | collector defaults; 7 tests green on nothing | D → FIXED | R19-COLLECTOR on the PIN: `30 failed, 56 passed, 28 errors in 171.26s`; the four assertions `test:230 test:237 test:241 test:245` are `is_file()` (S_ISREG), not `exists()` | **yes** |
| 1.3 | trial-loop `results.append(None)` gates | D → FIXED | `test:2245` and siblings are now `trial %d: tee wrote no …` assertions; the `None` branch is gone from the trial loop | yes (static + R19) — src `assert tl_path.is_file(), "trial %d: tee wrote no timeline.jsonl" % trial` |
| 1.6 / 10.5 | eight `/dev/full` skips, undeclared | D → FIXED | R18-DEVFULL: `test:921` `assert os.path.exists(_DEV_FULL), (` FAILS — `1 failed, 22 passed, 4 skipped, 87 deselected in 65.71s`. Four skips remain (`:1096 :1299 :1926 :1947`), but the declaration is now the loud gate | yes, with the note that "no skips" is not literally achieved |
| 1.7 / 1.8 / 1.11 / 9.4 / 9.5 / 11.2 / 11.3 | bounded polls, `/proc` reads, own-pid scoping | S | unchanged this round; the AF-AP-59 screen is empty and `test:3001` `def test_grandchild_cleanup_is_own_pid_scoped` reads the registry row | yes |
| 7.1 | lossy decode on a decision path | S | unchanged | yes |
| 12.1 | AF-AP-58 pin blind to the signal | S (covered by neighbours) | measured: SIGUSR1 swap → `10 failed, 104 passed`. Claim true; the pin is still blind → **VB-F9** | partly |
| 14.1 | docstring token mirror | D → FIXED | R14's exact sentence dies at `test:3667`; a paraphrase does not → **VB-F2/VB-F3** | partly — src `assert token not in residue, (` |
| 14.2 | the oracle test | S | it derives rather than mirrors for the seconds and the order — but the two half-strings are a mirror → **VB-F1** | **no** |

No DEFECT row from SWEEP-tests is missing from the lane's table. The three classes it under-graded (14.2, 12.1,
14.1-by-paraphrase) are VB-F1, VB-F9 and VB-F2/F3.

---

## ITEM 13 — the design, from what I measured

1. **Is "one sentence in the repo" enforced structurally?** No — it is enforced at six enumerated places by
   wording plus a two-token blacklist over one docstring. Measured: a false sentence is admissible in a test
   docstring outside the three named ones (VB-F3), in a tee comment outside the two R1 blocks (VB-F3), and
   even inside the canonical module docstring if it paraphrases (VB-F2). The shape that would be structural is
   the derived two-token proximity ban over both files whole (VB-F3's fix) plus VB-F2's sentence-level rule;
   both are ~6 lines.
2. **Is the bounded reader the right primitive?** Yes for the read itself — `test:175`
   `def _read_with_deadline` turns the wedge into `None` and every call site asserts the line arrived. It is
   the wrong primitive for the PIN: keying on three attribute names and one receiver name leaves four working
   evasions (VB-F4), and the allow-list is by FUNCTION NAME, so any function called `_drain` is trusted
   whether or not its thread is ever joined with a timeout. Moving the reads into the fixture would not fix
   that; pinning every MENTION of the pipe (VB-F4's fix) does, in ~15 lines, and it is what makes the property
   ("no unbounded read of a tee pipe") true rather than "no read spelled these three ways".
3. **The equality's shape.** Deriving the seconds and the order was the right call and it works
   (mutant 21 proves the seconds are joined). The remaining weakness is that the sentence's WORDS are a second
   hand-written copy; binding each half to a fact already derived (VB-F1's fix, 4 lines) closes it without
   changing the design.

---

## What I reproduced vs reviewed vs skipped

**Reproduced by execution (all numbers above are from my own runs):** both sandbox gates; the PC `-n 8` gate;
51 mutant runs; the structural walk on parent and PIN; the deadlock on both tees with the wchan/fd table; the
identity probes (20 + 20 + 20 + 50-under-load + 10 bash-exec-bash); the `S0_01_AGENT` domain on 7 shapes ×
2 tees; the cost probe 15×3; the site-3 cost on both venues; R19/R18/SIGUSR1; the standalone pins on three
interpreters; `check_runtime_identity` against the real corpus; the acp.rs derivation from primary source;
three red-green fix validations; `report_lint`, `ap_screen`, `pyflakes`.

**Reviewed statically, not executed:** VB-F2's proposed fix (drafted, not run — stated as such); the PC-side
mode of `/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp` (VB-F13); SWEEP rows 1.7/1.8/1.11/7.1/9.4/9.5/
11.2/11.3 (unchanged by this delta — I read them, did not re-run their instruments).

**Deliberately skipped:** running a mutated hang shape THROUGH pytest (a deadlocked pytest+tee pair is the
failure the brief warns about — I proved the evasion statically with the pin's own walk and the deadlock with
a watchdogged standalone probe instead); `pytest -n 4`/xdist in the sandbox (not installed — the PC leg covers
8 workers); a real `PermissionError` from a restricted `/proc`; anything on the bridge beyond the one
sanctioned pytest gate.

## Shared-tree hygiene

No `git stash/checkout/restore/reset/add/commit/push`. One `git worktree add --detach 75998e7` into my
scratchpad for the sanctioned PC gate, removed afterwards with `git worktree remove --force` — I removed only
the worktree I created; `git worktree list` now shows only the main checkout. `git status --short` on the shared tree shows only
other lanes' edits (`.claude/hooks/edit-snapshot.py`, `proofs/S0-01/pins.py`, `tools/acp_probe.py`,
`tools/pc/*`, `proofs/S0-08/*`, several test files) — none of them mine; I wrote nothing into
`/home/user/agent-factory`. Every mutant lived under `…/scratchpad/vb14/`, every pytest run carried
`--basetemp` under it, and the whole tree (2.0 G) is deleted — `df -h /` went from 85 % to **79 % used,
7.9 G free**, which matters given B5h F15. Every process I started was
killed by pid (`os.kill(<pid>, 9)` / `Popen.kill()`); the eight CPU spinners for the load runs were killed by
their recorded pids; no `pkill`, no `pgrep`, no name-matched signal. Final census: zero processes of mine
alive (the only pytest pair on the box, 11193/11194 on `tests/test_s0_01_acp_probe.py`, is another lane's and
I did not touch it).

## `report_lint` on THIS report

```
$ python3 scripts/report_lint.py <this file> --rev 75998e7 \
      --map tee=proofs/S0-01/tools/frame_tee.py --map test=tests/test_s0_01_frame_tee.py
report_lint: 132 refs — OK 120, NEAR 0, MISS 0, UNCHECKABLE 12, UNRESOLVED 0 (at 75998e7)
```
The 12 UNCHECKABLE lines carry a reference with no backticked claim token for the linter to test — ten are
inside the pasted `ap_screen.py` output block (the tool prints `<path>:<line>: <text>` itself), one is the
`test:175` reference in the design section, and one is this block's own summary line.

## Verdict

**NOT-READY.** Blocking set:
1. **VB-F1** — the equality is a three-site mirror; the order-reversed sentence passes the full suite
   (`114 passed`). Fix: 4 lines after `test:3621` `wait_half = "waits up to %d s for the child to exit" % wait_secs`,
   validated red-green.
2. **VB-F2** — a paraphrased false shutdown sentence in the tee's module docstring survives (B5h F12
   re-opened). Fix: ~6 lines, sentence-level rule over the module docstring.
3. **VB-F4** — the structural hang pin misses four read shapes; the iteration form re-opens the F9 deadlock on
   the PIN's own tee. Fix: ~15 lines, validated red-green.

**Cheapest path to MERGE-READY** (one lane, two files, no redesign): apply VB-F1's two assertions, VB-F2's
sentence rule, VB-F4's mention-pin, VB-F5's one-word assertion at `test:2857` `_kill_own_grandchild(framedir)`,
VB-F9's one-line signal assertion, and re-stamp the report (VB-F7/VB-F8) with `report_lint --rev <new PIN>` at
`MISS 0`. Then re-run
the six mutants that currently survive (MIRROR-3SITE-ORDER, SEVENTH-SITE-PARAPHRASE, SIXTH-SITE-TESTDOC,
SIXTH-SITE-TEECOMMENT, ZOMBIE-BRANCH-LIVE, PIPEREAD-ITERATION/-READLINES/-OSREAD) plus one full-file gate on
each venue. VB-F6 (deterministic test for the `OSError` guard) and VB-F10 (the "at least one trial won"
assertion) are cheap and belong in the same round; VB-F12 and VB-F13 are for the coordinator, not this lane.

My verdict does not depend on anything I did not reproduce: each blocking finding is a mutant I ran, with the
pasted result, and each fix is one I ran red and green — except VB-F2's fix, which I drafted and did not
execute (the FINDING itself is executed and pasted).
