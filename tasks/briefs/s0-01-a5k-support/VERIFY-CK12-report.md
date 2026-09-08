# VERIFY-CK12 — adversarial grade of lane A5j (S0-01 checker, round 12), checkpoint 8x

**VERDICT: NOT-READY.** No part of this verdict rests on anything I did not reproduce myself.

**PIN graded:** `dc9f5969182fe9dda5b9eadb98c9bfc85edf773f`. Every byte read from
`git archive dc9f596 | tar -x` into `scratchpad/vck12/`. The shared tree was READ-ONLY
(`git archive`, `git show`, `git diff`, `git log`, `git status`); no
stash/checkout/restore/reset/add/commit/push, and my three scope files were never written there
(`git status --porcelain -- <the three>` empty at start and at end).

**Parent for the checker files:** `73efb9f` (checkpoint 8t) — *not* the `ac3117f` the lane's report
headers. Red-before tree = `git archive 73efb9f` + the PIN's test file, rebuilt from scratch after a
container restart and re-run (identity proved below).

**File identity (PIN bytes) — matches the lane's report:**

| file | sha256[:16] | lines |
|---|---|---|
| `proofs/S0-01/check_acp_conformance.py` | `56e86e712e3a54bb` | 1857 |
| `tests/test_s0_01_check_acp_conformance.py` | `78adb3a4f7f4f447` | 4922 |
| `proofs/S0-01/negative_contract.py` | `3af15c9c8687328a` | 217 |

Red-before tree identity: parent `check_acp_conformance.py` = `de13655acc86f5ac`, equal to
`git show 73efb9f:proofs/S0-01/check_acp_conformance.py | sha256sum`; test file
`78adb3a4f7f4f447` = the PIN's.

**Branch drift during the grade.** Other lanes landed 27 commit(s) while I worked; the shared
branch tip is now `68fb454`. `dc9f596` remains an ancestor of it, and every byte I graded came
from `git archive dc9f596`, so nothing in this report depends on the moving tip.

**Corpus:** `bash scripts/realleg_sync.sh check` → `realleg_sync: /root/s0-01-realleg/golden intact (142 files)` rc 0.

**Box.** 4 cores, no `pytest-xdist` installed. Load ran **0.89 → 9.63** with five other lanes'
suites live (S0-02, S0-03, S0-04, S0-06, S0-08). **No timing below is graded.** Mid-session the
container restarted and the shared disk hit **97 % full**; both events are accounted for under
GATES.

### BLOCKING SET

1. **F-CK12-01** — the report's `file:line` discipline failed for the fourth consecutive round: of
   23 references I resolved by symbol, **17 are wrong** (a uniform +13 drift), while the report
   states they were grep-verified on the final bytes.
2. **F-CK12-02** — the F8 read-CLASS scan asserts on **0 of the 49** read sites it finds; it was
   green on the parent, and `checked_files = []` survives.
3. **F-CK12-03** — SWEEP-prod #8's four hangs are **all still live** through the `spec.json`
   negative-leg entry point (rc 124 at 20 s each).
4. **F-CK12-04** — the AP-40 class pin catches **1 of 10** presence-gate shapes and misses the exact
   shape F15 fixed.
5. **F-CK12-05** — the AP-40 pin's exemptions are keyed by hard-coded line numbers; one added
   comment line turns it red.

Cheapest path to MERGE-READY is at the end.

---

## Item 0 — the mechanical gates, re-run (I DISAGREE with the lane's reading)

### report_lint at the PIN

```
python3 scripts/report_lint.py tasks/briefs/s0-01-a5j-support/A5j-report.md \
  --rev dc9f5969182fe9dda5b9eadb98c9bfc85edf773f \
  --map C=proofs/S0-01/check_acp_conformance.py \
  --map T=tests/test_s0_01_check_acp_conformance.py \
  --map N=proofs/S0-01/negative_contract.py
report_lint: 145 refs — OK 60, NEAR 11, MISS 50, UNCHECKABLE 21, UNRESOLVED 3   (exit 1)
```

The brief requires **MISS = 0**. It is 50. The lane's report pastes
`142 refs — OK 60, NEAR 11, MISS 50, UNCHECKABLE 21, UNRESOLVED 0 (worktree)` and declares *"Every
MISS and NEAR is a token-heuristic row… The cited lines point to the correct code — verified by
`grep -n` on the final bytes."* **That declaration is false** — see F-CK12-01.

### ap_screen — every hit classified BY RUNNING it

```
python3 scripts/ap_screen.py proofs/S0-01/check_acp_conformance.py proofs/S0-01/negative_contract.py
--- AP_SCREEN over 2 path(s): 8 hits over 2 files ---
AF-AP-40: 5   C:1488, C:1501, C:1698, C:1700, C:1713
AP-32:    3   C:167, C:175, N:39
python3 scripts/ap_screen.py --tests tests/test_s0_01_check_acp_conformance.py
AP-66: 2      T:85, T:87
```

Each AF-AP-40 hit driven through the real checker on a hostile bundle (8 probes, `8 passed in 43.78s`):

| hit | mutation | observed | my verdict |
|---|---|---|---|
| `C:1488` `if neg_dir.is_dir()` | `negative/` → a regular file | `(1, 'failure_reason: golden: unexpected file golden/negative')` | **reviewed-safe CONFIRMED** — dominated by the allowlist at `C:1698` |
| `C:1501` `if stderr_path.exists()` | delete `negative/agent-stderr.txt` | `(1, 'failure_reason: negative: negative: agent-stderr.txt absent')` | **CONFIRMED** — the name-set check fires first |
| `C:1698` `if item.is_dir()…` | add `golden/evil-dir` | `(1, 'failure_reason: golden: unexpected directory golden/evil-dir')` | **CONFIRMED** — true branch raises |
| `C:1700` `if item.is_file()…` | add `golden/evil.txt` | `(1, 'failure_reason: golden: unexpected file golden/evil.txt')` | **CONFIRMED** |
| `C:1713` `if post_sum_path.exists()` | delete `run-1/manifest-post.summary` | `(1, 'failure_reason: run-1: manifest-post.summary absent')` | **CONFIRMED** — dominated by `check_manifests` |

AP-32 (`C:167`, `C:175`, `N:39`): sha256 over raw bytes on both sides — **reviewed-safe, by
inspection only, not run.** AP-66 (`T:85`, `T:87`): identical text at `73efb9f:tests/…:85-87` —
**pre-existing**, the lane is right.

**Where I disagree:** the lane's AP-SCREEN section is incomplete for the test file. The repo's own
pre-commit delta gate, run from a clean PIN worktree, flags the lane's *added* lines:

```
python3 scripts/lint_delta.py --base 73efb9f          (rc 0)
anti-pattern screen (TELLS on added lines — advisory):
  AP-1     tests/test_s0_01_check_acp_conformance.py: env read in edited code …
  AF-AP-40 tests/test_s0_01_check_acp_conformance.py: presence-gated check … (AF-AP-40)
```

That AF-AP-40 tell is real and unreported — F-CK12-08.

---

## Item 1 — CK11 F1–F20 closure table

Red-before on `73efb9f` (parent production files + PIN test file), full file, never `-x`. **Rebuilt
from `git archive` after the restart and re-run** — identical both times:

```
5 failed, 7 passed, 357 deselected in 61.04s
FAILED test_ck11_fifo_at_tools_acp_probe_is_named
FAILED test_ck11_dir_at_tools_acp_probe_is_named
FAILED test_ck11_absent_acp_schema_is_a_failure
FAILED test_ck11_no_presence_gated_check_in_the_proof
FAILED test_ck11_dead_branch_comments_cite_a_real_guard
PASSED test_ck11_real_leg_dir_is_resolved_from_the_environment
PASSED test_ck11_venue_is_resolved_from_the_environment
PASSED test_ck11_venue_domain_is_known
PASSED test_real_leg_corpus_declared
PASSED test_ck11_known_stale_is_the_whole_reason_not_a_tail
PASSED test_ck11_every_read_is_under_the_walk_or_require_file      <-- F-CK12-02
PASSED test_ck11_alarm_inside_try_cannot_leak_the_handler
```

PIN run of the same selection: `12 passed, 357 deselected`.

| CK11 | closed by (line verified on the PIN) | what I reproduced | verdict |
|---|---|---|---|
| F1 corpus path tracks env | `T:2580`; test `T:2644` | M09b with the var **unset** (the brief's config) → `1 failed`; with it **set**, M09 → `2 passed` | **CLOSED**; the lane's mutant row omits the killing config |
| F2 alarm inside try | `C:1632` inside `try:` | M10 ALARM-OUTSIDE-TRY → `1 failed` | **CLOSED** |
| F3/F4/F5 B1 as a property | `T:2878` `assert not ok` before the marker; `T:2860`; `T:2867` | all four states reproduced (Item 4) | **CLOSED** |
| F6 scan inlined | `T:3465` | M17 → `1 failed`; M18 → `1 failed` | **CLOSED** |
| F7 write patterns | `T:3356` (`truncate`), gzip branch `T:3446`, self-test `T:3499` | M18 category drop → `1 failed` | **CLOSED** |
| F8 (a) probe S_ISREG | `N:181` | FIFO/dir at `tools/acp_probe.py`, **both** entry points | **CLOSED (the instance)** |
| F8 (b) the read CLASS | `T:4718` | 0 of 49 sites asserted; 10 of 15 valid plants missed; green on the parent | **NOT CLOSED — F-CK12-02** |
| F9 restore before `alarm(0)` | `C:1638-1639` | M11 F9-ORDER-SWAP → `15 passed`, **survivor** | **inspection only — F-CK12-13** |
| F10 NOTE states the domain | `C:2-3` | read; consistent with the `--timeout-s` behaviour | **CLOSED (static)** |
| F11 dead-branch pin | `T:4893` | M12/M13 → killed; M15 move-the-raise → killed; **M14** and **M16** → survivors; `C:1605` has no citation | **PARTIAL — F-CK12-07** |
| F12 report discipline | — | 17 of 23 references wrong | **NOT CLOSED — F-CK12-01** |
| F13 unset venue = sandbox | `T:2579` | `env -u S0_01_VENUE` → `4 passed`; both unset → `1 failed` | **CLOSED** |
| F14 dead `write_text("placeholder")` | removed | `grep` finds only the comment | **CLOSED** |
| F15 presence-gate (instance) | `C:1707` `_require_file(schema_path, …)` | parent → byte-identical PASS; PIN → `failure_reason: golden: fixtures/acp-schema-v1.json absent`; M04 → `1 failed` | **CLOSED (the instance)** |
| F15 the CLASS | `T:4675` | 1 of 10 shapes caught | **NOT CLOSED — F-CK12-04/05** |
| F16 venue domain | `T:2657`, `T:2668` | 6 hostile values → `2 failed` each | **CLOSED** |
| F17 corpus is a directory | `T:2674` | corpus = `/etc/hostname` → `1 failed` | **CLOSED** |
| F18 one resolution point | `T:2579-2580` | the only reads of the two vars outside the tracking tests | **CLOSED** |
| F19 corpus CONTENT verified | `T:2684`, `T:2689` | drift → named; sidecar gone → named + remedy | **CLOSED**, two gaps (F-CK12-09) |
| F20 startup denominator | `T:4547` | M19b drop `"typing"` → `1 failed` | **CLOSED** |

---

## Item 2 — the read CLASS (F8): attacked, measured, then RUN

### 2a. 17 planted read vectors, one at a time (re-run after the restart)

```
P01 Path.open().read()            **MISSED**      P10 read in a class body        invalid plant (import error)
P02 io.open                       **MISSED**      P11 read in negative_contract   CAUGHT
P03 os.open                       **MISSED**      P12 read in check_initialize    CAUGHT
P04 json.load(open())             **MISSED**      P13 _require_file in a COMMENT  **MISSED**
P05 gzip.open                     **MISSED**      P14 receiver contains 'sp'      **MISSED**
P06 bare read_bytes               CAUGHT          P15 os.stat then read           CAUGHT
P07 receiver contains 'path'      **MISSED**      P16 os.readlink                 MISSED (benign — not a content read)
P08 read in a lambda              CAUGHT          P17 receiver contains 'golden'  **MISSED**
P09 module-scope read             invalid plant (import error)
```

15 valid plants: **5 caught, 10 missed** (9 substantive). P09/P10 executed at import and produced a
collection error, so they are **not** scan detections — my earlier note that they were "caught" was
wrong and is corrected here.

Root causes, on the PIN's bytes:
- `T:4728` `READ_ATTRS = {"read_text", "read_bytes"}` — `Path.open`, `io.open`, `os.open`,
  `gzip.open`, `json.load` are not categories at all; only the **builtin** `open` is.
- `T:4767` `walked = ("golden", "_fixtures", "leg_dir", … "sp", … "rp", "item", "fpath", "path")`
  — a **substring** test against the unparsed receiver; `sp`, `rp`, `path`, `item` match inside
  almost any identifier.
- `T:4763` `if "_require_file" in context or "S_ISREG" in context: continue` — a raw text search
  over the previous 5 source lines, **comments included**, with no tie to the receiver.
- `T:4775` `if fn == "_sha256_file": continue` — a whole-function exemption.

### 2b. The measurement that settles it

Re-implementing the scan's own logic over the PIN's three files (re-run after the restart):

```
read sites found by the scan: 49
  exempt by 5-line proximity TEXT: 25
  exempt by receiver NAME-SUBSTRING: 24
  exempt by fn==_sha256_file:        0
  actually asserted (would fail):    0
```

**The scan's assertion is unreachable on the current tree.** It is green because it examines
nothing — anti-hollow-green tactic 7. Mutation agrees:

- **M06 READ-SCAN-OFF** — `checked_files = []` → `1 passed, 368 deselected`. **SURVIVOR.** The
  brief's "READ-SCAN-OFF must die" is not met.
- **M21 READSCAN-ALLOWLIST-WIDEN** — prepend `"e"` to `walked` → `1 passed`. **SURVIVOR.**
- **M05 PROBE-EXISTS-ONLY** — revert the `N:181` guard → the scan still **passes** (the FIFO/dir
  tests kill it, not the scan).

And it was **green on the parent**: `negative_contract.py:187` reads through `_sha256_file(probe_file)`,
whose parameter is named `path`.

### 2c. RUNNING the class

**(i) Through the checker entry point**, 14 probes:

| path | FIFO | directory |
|---|---|---|
| `golden/negative/timeline.jsonl` | 0.00 s, rc 1, `golden: non-regular entry in evidence tree: negative/timeline.jsonl` | 8.13 s, rc 1, **unnamed** `malformed evidence: IsADirectoryError: [Errno 21] Is a directory: '<abs path>'` |
| `golden/negative/runtime-identity.json` | 0.00 s, rc 1, named | 7.97 s, unnamed |
| `golden/negative/env.json` | 0.00 s, rc 1, named | 8.36 s, unnamed |
| `golden/negative/agent-stderr.txt` | 0.00 s, rc 1, named | 8.87 s, unnamed |
| `fixtures/neg-malformed-initialize.json` | 0.00 s, rc 1, named | 8.53 s, unnamed |
| `fixtures/acp-schema-v1.json` | 0.00 s, rc 1, named | 0.00 s, rc 1, `golden: fixtures/acp-schema-v1.json is not a regular file` (the new F15 `_require_file`) |
| `fixtures/identities.json` | 0.00 s, rc 1, named | 0.00 s, rc 1, named |

No hangs here — the FIFO class is closed by the **pre-existing** evidence-tree walk
(`golden: non-regular entry in evidence tree`), which runs before any read, **not** by the new
guard. The directory sub-class falls through to `C:1851` `except Exception as exc`: fail-closed, but
unnamed and carrying an absolute machine-specific path.

**(ii) Through the `spec.json` negative leg** — `python3 proofs/S0-01/check_initialize.py request <negdir>`,
the command `spec.json` actually runs (`expect {"exit_code": 1, "failure_reason": "protocol-violation: missing required initialize field"}`,
`timeout_s: 60`). Re-run after the restart on a repaired corpus copy:

```
CONTROL (pristine)                  rc=1    0.13 s   protocol-violation: missing required initialize field
FIFO timeline.jsonl                 rc=124  20.01 s  (no output)
FIFO runtime-identity.json          rc=124  20.01 s  (no output)
FIFO env.json                       rc=124  20.01 s  (no output)
FIFO fixtures/neg-malformed-initialize.json  rc=124  20.02 s  (no output)
FIFO tools/acp_probe.py  (control)  rc=1    0.13 s   failure_reason: negative: tools/acp_probe.py is not a regular file
```

**SWEEP-prod #8 is entirely OPEN on the PIN.** Only the fifth site (`tools/acp_probe.py`) is closed —
and it is closed on both entry points. Every scratch fixture was restored byte-identically
(`db136158249e85b3`, `b9eb56dd9a75cb34`, both equal to `git show dc9f596:<path> | sha256sum`).

---

## Item 3 — the presence-gated CLASS (F15 / AF-AP-40)

### 3a. 10 planted gate shapes (re-run after the restart)

```
B01 if exists / else default    **MISSED**    B06 os.access                 **MISSED**
B02 os.path.exists              **MISSED**    B07 ternary (the F15 shape)   **MISSED**
B03 is_dir / default            **MISSED**    B08 negated, no raise         **MISSED**
B04 try/except FileNotFound     **MISSED**    B09 is_file / else default    **MISSED**
B05 glob truthiness             **MISSED**    B10 if exists, NO else        CAUGHT
```

**1 of 10.** `T:4704` `startswith("not ")` skips every negated gate without checking that its body
raises (B08); the pattern list is only `.exists()`/`.is_file()` (B02-B06 invisible);
`if "raise " in body_code` is a text search; and `T:4713` `if not node.orelse` means an **explicit
`else:` default is never flagged** — the canonical AP-40 shape (B01, B09). B07 is the shape the schema line carried on the parent
(`73efb9f:proofs/S0-01/check_acp_conformance.py:1704` — at the PIN that line number holds unrelated code), so **the class scan would not have caught the very defect F15 fixed**.
The lane documents the ternary limit but not the `else:` limit, which is larger.

M04 (revert `C:1707` to the parent's ternary) → `absent_acp_schema` fails,
`no_presence_gated_check` **passes**: the instance test is the only killer.

### 3b. Exemptions keyed by hard-coded line numbers

`T:4686`:

```
_REVIEWED_SAFE = {
    ("check_initialize.py", 129), ("check_initialize.py", 194),
    ("check_acp_conformance.py", 1713),
}
```

**Control mutant (semantics-free), re-run after the restart:** insert one `# shift` comment as line 1
of `check_acp_conformance.py` → `1 failed, 368 deselected`,
`AssertionError: AP-40 hits: ['check_acp_conformance.py:1717 affirmative presence gate with no else (AF-AP-40)']`.
Any edit above `C:1713` turns the pin red for a non-defect. **M20** (append a fourth tuple) →
`1 passed`: the exemption list has no guard of its own.

### 3c. The exemplar, and SWEEP-prod #3d

| run | parent `73efb9f` | PIN `dc9f596` |
|---|---|---|
| delete `fixtures/acp-schema-v1.json` | `(0, 'PASS: S0-01 acp-conformance - 63 checks executed over 5 legs; …')` byte-identical PASS | `(1, 'failure_reason: golden: fixtures/acp-schema-v1.json absent')` |

**SWEEP-prod #3d is OPEN** (carry-forward, outside this brief). Re-run after the restart:

```
VCK12-SWEEP3D-NAIVE        (1, "failure_reason: malformed evidence: KeyError: '$defs'")
VCK12-SWEEP3D-PERMISSIVE   (0, 'PASS: S0-01 acp-conformance - 63 checks executed over 5 legs;
                               golden x2 identical (11 normalized lines, sha256 e088d7827be7); …')
```

The naive `{"type":"object"}` substitution now fails only because the loader wants `$defs`; a
substitution that keeps that shape (`InitializeRequest`/`InitializeResponse` → `True`) passes
**byte-identically to the baseline**. `dir(pins)` holds no `*SCHEMA*` symbol — the fixture is
present-checked, never content-pinned.

---

## Item 4 — B1 as a property (F3/F4/F5)

`T:2878` `assert not ok` runs **before** any marker is added; `T:2867` `_is_known_stale` is
whole-reason equality; the inert `strict=`/`raises=` are gone. Four states, all reproduced on real
corpus copies:

| state | how built | observed |
|---|---|---|
| 1 stale (as shipped) | declared corpus | `1 xfailed` — `real v2.2 sample: negative: negative: probe_sha256 mismatch (capture predates current probe)` |
| 2 repaired capture | corpus copy with `probe_sha256` ← real sha of `tools/acp_probe.py` and `agent_interpreter_realpath` ← `pins.PINNED_AGENT_INTERPRETER_REALPATH` | **FAILED** at `T:2878`: `check_negative PASSES on the real negative leg — the known-stale reasons [...] no longer reproduce; retire them (B1)` — not xfailed |
| 3 unrelated failure | same path as 4 | **FAILED** at `T:2886` |
| 4 tail collision | `probe_error = "probe_sha256 mismatch"` planted | **FAILED**, `unexpected failure: negative: negative: negative: probe reported an error: probe_sha256 mismatch` — hard fail, never xfail |

M01 (rsplit-tail equality) → `1 failed`; M02 (substring accept) → `1 failed`. Both **KILLED** by
`test_ck11_known_stale_is_the_whole_reason_not_a_tail`, which is at **`T:4591`**, not the `T:4578`
the report cites.

**M03 B1-ORDER** (fold the assertion into the xfail condition — the pre-fix shape) → `1 xfailed`,
**SURVIVOR**: on the stale declared corpus the two shapes are indistinguishable. The fix is real —
I reproduced state 2 by hand — but has **no in-gate killer** (F-CK12-06).

---

## Item 5 — the declared corpus (F1/F13/F16/F17/F18/F19)

| configuration | result |
|---|---|
| `S0_01_VENUE=sanbox` / `SANDBOX` / `'sandbox '` / `prod` / `0` / `''` | `2 failed, 2 passed` each — `S0_01_VENUE=… is not a known venue` |
| venue UNSET (= sandbox), corpus set | `4 passed` |
| venue UNSET, corpus UNSET | `1 failed, 3 passed` |
| `S0_01_VENUE=ci`, corpus UNSET | `3 passed, 1 skipped` (declared) |
| corpus = a regular file (`/etc/hostname`) | `1 failed` — not a directory |
| corpus = an empty directory | `1 failed` — incomplete, missing legs |

Sidecar / content (F19), each on a scratch copy:

| mutation | observed |
|---|---|
| flip one corpus file | `AssertionError: corpus drift at ./negative/runtime-identity.json` |
| delete `golden.pc.sha256` | `AssertionError: <path>/golden.pc.sha256 absent — run scripts/realleg_sync.sh pull` |
| delete a declared artifact (`run-1/argv.txt`) | `FileNotFoundError: [Errno 2] … '<abs>/run-1/argv.txt'` — **raw, unnamed** (F-CK12-09b) |
| **ADD** a file not in the sidecar (`run-1/evil.txt`) | **`1 passed` — no signal** (F-CK12-09a) |

**Real-leg set twice on the declared corpus:**

```
run1: 53 passed, 307 deselected, 9 xfailed in 35.45s
run2: 53 passed, 307 deselected, 9 xfailed in 31.40s
```

Counts identical, and identical to the lane's paste. Elapsed differs (load 9.03) — not graded.

M09b (corpus var unset) → `1 failed` **KILLED**; M09 (var set) → `2 passed` **SURVIVOR**.
M07c (hostile venue) → `1 failed` **KILLED** by `test_ck11_venue_domain_is_known`; M07b (lane's
form, valid venue) → `2 passed` **SURVIVOR**. M08 SIDECAR-UNCHECKED on the **clean** declared
corpus → `1 passed`: the sidecar loop has no committed killer (F-CK12-14, F-CK12-09c).

---

## Item 6 — alarm handler, dead-branch pin, F6/F7/F14/F20, the skip helper

- **Alarm.** `C:1632` `_signal.alarm(timeout_s)` inside the `try`; `C:1638-1639` restore then
  `alarm(0)`. M10 ALARM-OUTSIDE-TRY **killed**. **M11 F9-ORDER-SWAP survives** (`15 passed`) — the
  monkeypatched `alarm` throws only for a non-zero argument, so `alarm(0)` never raises and the
  order is unobservable; the code comment concedes as much (F-CK12-13).
- `test_ck10_rejected_cap_installs_no_handler` is renamed as the brief asked.
- **Dead-branch pin** (`T:4893`). It **does** parse and enforce: M12 (`C:742-743`→`C:747-749`) and
  M13 (`C:893-893`→`C:894-895`) each `1 failed`; **M15 move-the-raise** (`raise Failure` →
  `raise ValueError` at `C:743`) `1 failed` — `line 1568 cites C:742-743, which contains no guard`.
  Gaps: `T:4918` `m = re.search(...)` + `T:4919` `if m:` take only the **first** citation, so
  **M14** (mutate the second citation `C:905-905`) → `1 passed` **SURVIVOR**, and **M16** (delete a
  citation) → `1 passed` **SURVIVOR**. Enumeration on the PIN bytes:

```
comment@946 : C:922-925   -> raise Failure at [923]
comment@956 : C:893-893, C:905-905    (only the first is checked)
comment@1552: C:1533-1535 -> raise Failure at [1533, 1535]
comment@1568: C:742-743   -> raise Failure at [743]
comment@1597: C:742-743   -> raise Failure at [743]
comment@1605: (no citation) -> nothing checked
```

  The lane's DONE row claims "F11: dead-branch 6/6". It is **5 of 6 comments, 5 of 7 citations**.
- **F6/F7**: M17 F43-SCAN-OFF → `1 failed`; M18 category drop → `1 failed`. Solid.
- **F14**: the dead `write_text("placeholder")` is gone.
- **F20**: `T:4547` `_uncovered` against `cc._EXPECTED_STARTUP_KEYS`; M19b (drop `"typing"`) →
  `1 failed, 15 passed`.
- **The one skip helper**: `_real_leg` at `T:2598`, 17 call sites. Only four `pytest.skip` remain:
  `T:2602`, `T:2605` (inside the helper), `T:2709` (the declared `ci` skip), and **`T:2784`
  `pytest.skip("baseline manifest absent")`** — a residual presence-gated silent skip outside the
  helper (F-CK12-10).

---

## Item 7 — the PC gate (the one sanctioned bridge action)

From a **clean detached worktree of the PIN** (`git worktree add -q --detach <tmp> dc9f596`,
`git status --porcelain` empty), `scripts/pc_suite.sh launch -n 8 -- <3 files>` then `log`. The
launch line proves tree identity: `base dc9f5969… + patch 0B (sha e3b0c44298fc)` — exactly the PIN
bytes, no working-tree overlay.

```
RUN_ID 20260908T003842Z-dc9f596
468 passed, 9 xfailed in 146.55s (0:02:26)
```

The worktree was removed afterwards (`git worktree remove --force` + `prune`). Nothing else on the
bridge was touched: no `scripts/pc.sh`, no lane dispatch, no server touch, no PC file writes.

---

## Item 8 — class status over SWEEP-prod's checker rows (carry-forward)

| # | class | status on the PIN | the run |
|---|---|---|---|
| 2 | symlinked walk roots | **OPEN** | `golden/` → symlink: `(0, 'PASS: S0-01 …')` byte-identical; fixtures root → symlink: identical |
| 3 | presence-gated / unpinned schema | **3a CLOSED by A5j** (`C:1707`); **3d OPEN** | Item 3c |
| 4 | every `_fixtures()` input unpinned | **OPEN** | no `*SCHEMA*` in `dir(pins)`; permissive-schema PASS |
| 5 | `pinned_present` header vs body | **N-A** — `pc_post.sh` is outside the lane's files and is held dirty in the shared tree by another lane | not run |
| 8 | four hangs in `negative_contract.py` | **OPEN ×4** | rc 124 at 20.01/20.01/20.01/20.02 s |
| 9 | `N:87-93` name-set with no type check | **PARTIAL** | a dir or FIFO named `agent-stderr.txt` still passes the name-set; only `tools/acp_probe.py` gained `S_ISREG` |
| 17 | `C:1501` redundant guard | **EQUIVALENT (confirmed by run)** | `negative: negative: agent-stderr.txt absent` |
| 18 | `C:1713` redundant guard | **EQUIVALENT (confirmed by run)** | `run-1: manifest-post.summary absent` |
| 19 | `C:525-528` dead fallback | **EQUIVALENT — reviewed statically, not re-run** | — |
| 20 | `C:1140-1151` dominated argv block | **EQUIVALENT — reviewed statically, not re-run** | — |
| 21 | `C:1488` redundant guard | **EQUIVALENT (confirmed by run)** | `golden: unexpected file golden/negative` |
| 22 | `N:185` `endswith` tail anchor | **OPEN** — untouched; the new `S_ISREG` sits above it at `N:181` | not re-run; the sweep's collision run stands |
| 29 | `check_initialize.py:194` wrong-reason gate | **OPEN** — and it is one of the two entries the AP-40 pin exempts by line number | not re-run |
| 30 | non-regular golden root → deferral | **OPEN** | FIFO at `golden`: `rc=2 deferred: v2 evidence not captured`; regular **file** at `golden`: `rc=2` same |
| 37 | `C:1849` `int(se.code or 0)` + exit-code-only grading | **OPEN — highest severity in the checker** | bare `raise SystemExit()` inside `check_runtime_identity` → **`rc=0`, stdout EMPTY**; control on the same bundle → `rc=0` with the real PASS line |
| 38 | `_run_check` proves invocation only | **DOCUMENTED-LIMIT, unchanged** | not re-run |
| 46-51 | `[-1]` idioms, negative-acceptance forms, one-sided bound, screen anchors | **SAFE/EQUIVALENT, unchanged** — reviewed statically against the PIN bytes | — |

---

## Item 9 — the real-corpus end-to-end truth (SWEEP-prod #1)

`python3 proofs/S0-01/check_acp_conformance.py <root>` with `<root>/golden` a copy of
`/root/s0-01-realleg/golden` (re-run after the restart):

```
rc=1   failure_reason: golden: manifests/ absent          (from C:1690 _require_dir)
```

Behind that first stop, the exact set difference against `C:1718` `_LEG_REQUIRED_FILES` +
`C:1726` `_LEG_OPTIONAL_DIRS`:

```
run-1     rejected-by-allowlist = [backend-healthz-after.json, backend-healthz-before.json,
                                   hermes-config.sha256, launch.exited, launch.ready,
                                   manifest-post.done, manifest-pre.done, teardown.txt]   (8)
run-1     required-never-produced = [agent-stderr.txt, tee-status.json]                    (2)
cancel    8 / 2      shutdown  7 (no teardown.txt) / 2      two-users  8 / 2
negative  [agent-stderr.txt, env.json, runtime-identity.json, timeline.jsonl]
golden.jsonl present: False        manifests/ present: False
```

**Direction for the next brief:** the allowlist rejects 7-8 producer-written names per positive leg,
requires 2 names the producer never writes, and the corpus lacks the top-level `golden.jsonl` and
`manifests/` the checker demands first. The checker cannot run end-to-end over the real corpus today.

---

## Item 11 — the design

**Is an AST self-scan written as an inclusion walk the right shape?** No, and the measurement is the
argument. `T:4718` is written as *"find reads, then subtract everything that looks allowed"*, but the
subtraction is three text heuristics and they subtract 49 of 49. The right shape is a
**subtraction over a closed set**: enumerate every read call (`open`, `io.open`, `os.open`,
`gzip.open`, `Path.open`, `read_text`, `read_bytes`, `json.load`), subtract the calls whose first
argument is syntactically the return value of `_require_file(...)`, and assert the remainder equals a
**committed explicit list of (file, line, receiver)** — a golden set, not a name-substring rule.
Then the scan has a coverage floor by construction: a new read is a diff against the committed list,
and `checked_files = []` or a widened allowlist changes the list and goes red. `T:3499`, the F43
self-test's exact category set, already demonstrates the pattern; the read scan should borrow it.

**Is `_require_file` the right primitive, one copy or three?** The right primitive — `C:192-200` is
exactly what the class needs, and every use produced a deterministic named reason (7 probes in
Item 2c(i)). **One copy in `pins.py`, not three.** Today the checker has it, `negative_contract.py`
has a hand-inlined two-line variant at `N:181-182` for exactly one path, and `check_initialize.py`
has none — that asymmetry is why the four hangs survive. `pins.py` is already imported by all three
and carries no heavy dependencies; the sweep's own suggestion for #8 was a local `_require_regular`,
which would be a third copy. Put `require_regular_file(path, leg, name) -> Path` in `pins.py` and
route `N:59`, `N:97`, `N:160`, `N:207` plus `check_initialize.py`'s reads through it.

**Where I would still change it:** (1) the directory sub-class should not land in `C:1851`
`except Exception` — `_require_file` on the last five unguarded reads turns five
`IsADirectoryError: '<abs path>'` strings into five named reasons a test can pin; (2) the AP-40 pin
should key exemptions on `(file, enclosing function, unparsed test)`, never a line number; (3) the
sidecar check should be **bidirectional**.

---

## FINDINGS — all of them, no severity floor

Every line number below re-derived by `grep -n` on `git show dc9f596:<file>` after the restart.

### F-CK12-01 — BLOCKING. The report's file:line references are wrong for the fourth round, and the report claims they were grep-verified.
*Where:* `tasks/briefs/s0-01-a5j-support/A5j-report.md:37-96`, claim at `:119-123`.
*Expected:* every reference resolves to the symbol its row names on the FINAL bytes (CK11 F12,
"third time"); `report_lint` MISS = 0.
*Observed:* of 23 references I resolved by symbol, **17 wrong, 4 near, 2 OK** — and the wrong ones
are not random: the whole `T:45xx-47xx` block is short by exactly **13**:

```
WRONG report:37  T:4578  cited=|# F28: the default timeout is 90|          test_ck11_known_stale_… at 4591   delta=+13
WRONG report:38  T:4620  cited=|assert (rc, out) == (1, "failure_reason:…| test_ck11_fifo_at_tools_… at 4633  delta=+13
WRONG report:38  T:4638  cited=|monkeypatch.setattr(nc, "HERE", tmp_path)| test_ck11_dir_at_tools_… at 4651   delta=+13
WRONG report:39  T:4705  cited=|continue|                                  test_ck11_every_read_… at 4718     delta=+13
WRONG report:40  T:4656  cited=|tools.mkdir(parents=True, exist_ok=True)|  test_ck11_absent_acp_schema at 4669 delta=+13
WRONG report:40  T:4662  cited=|rc, out = _check(bundle, timeout_s=30)|    test_ck11_no_presence_gated at 4675 delta=+13
WRONG report:44  T:4843  cited=|assert r.stderr.strip() == "usage: --tim…| test_ck11_alarm_inside_try at 4856 delta=+13
WRONG report:44  T:4833  cited=|"""R10-F03: timeout_s=2**31 is rejected…|  test_ck10_rejected_cap_… at 4846   delta=+13
WRONG report:45  T:4880  cited=|def test_ck10_teardown_zombies_plus_pres…| dead_branch pin at 4893           delta=+13
WRONG report:96  T:4673  cited=||                                          _REVIEWED_SAFE at 4686            delta=+13
WRONG report:49  T:4535  cited=|lp = bundle / "golden" / "run-1" / "buzz…| _uncovered at 4547-4548           delta=+12
WRONG report:41  C:1629  cited=|try:|                                      alarm(timeout_s) at 1632          delta=+3
WRONG report:48  T:4601 · report:59 T:3993 · report:60 T:3988 · report:74 T:4581 · report:75 T:4582   (symbol elsewhere entirely)
NEAR  report:46  T:3464 (→3465) · report:47 T:3355 (→3356) · report:47 T:3445 (→3446) · report:48 T:3356 (→3357)
checked 23 references: OK 2, NEAR 4, WRONG 17
```

`C:1629` shows the drift is not confined to the test file. `report_lint` independently reports
`MISS 50` and, at the PIN, `UNRESOLVED 3` (`A5j-report.md:26,27` cite `check_initialize.py:NNN` with
a basename outside the `--map` set; `:118` self-references `report:37`).
*Minimal fix:* regenerate every reference with `grep -n` on the committed bytes; re-run
`report_lint --rev <checkpoint>` until MISS = 0; delete the "verified by grep -n" sentence unless it
is true. *Exact red test:* the gate exists and exits 1 today. **SOLID.**

### F-CK12-02 — BLOCKING. The F8 read-class scan asserts on zero of the 49 read sites it finds.
*Where:* `tests/test_s0_01_check_acp_conformance.py:4718`; exemptions at `T:4763`, `T:4767`,
`T:4775`; categories at `T:4728`.
*Expected:* every read either resolves under a walked root or is wrapped in `_require_file` /
preceded by an `S_ISREG` on the same receiver; anything else FAILS naming `file:line` — and the scan
RED on the parent before the fix.
*Observed:* 49 sites, 25 exempted by a 5-line raw-text search, 24 by receiver-name substring,
**0 asserted**; **green on the parent**; M06 and M21 both survive; 10 of 15 valid plants invisible;
a `_require_file` mention **in a comment** disarms it.
*Failing input:* append to `check_acp_conformance.py`
`def _v(p):\n    evil_path = HERE / "sekrit.bin"\n    return evil_path.read_text()` → `1 passed, 368 deselected`.
*Minimal fix:* the committed-golden-set shape in Item 11; at minimum assert a coverage floor
(`len(examined) >= 40`) and that the module list is exactly the three names; add
`open`/`io.open`/`os.open`/`gzip.open`/`Path.open`/`json.load` to the category set; require the
guard token to name the **same receiver**.
*Exact red test:* `test_ck12_read_scan_examines_the_whole_read_set`. **SOLID.**

### F-CK12-03 — BLOCKING. SWEEP-prod #8's four hangs are live through the spec.json entry point.
*Where:* `proofs/S0-01/negative_contract.py:59`, `:97`, `:160`, `:207` — the module has no
`_require_file`.
*Expected:* a named refusal within seconds.
*Observed:* `check_initialize.py request <negdir>` with a FIFO at each → **rc 124 after 20.01 s,
20.01 s, 20.01 s, 20.02 s** (my cap; unbounded without it). The spec leg's own `timeout_s` is 60.
The read-class scan exempts all four by receiver-name substring.
*Failing input:* `mkfifo <negdir>/timeline.jsonl`.
*Minimal fix:* one `require_regular_file` in `pins.py`, all four reads routed through it, raising
`NegativeFailure(f"{name} is not a regular file")`.
*Exact red test:* `test_negative_contract_refuses_a_fifo_at_each_required_file`, parametrised over
the four names, asserting the reason and elapsed < 5 s. **SOLID — reproduced 4/4 twice.**

### F-CK12-04 — BLOCKING. The AP-40 class pin catches 1 of 10 shapes and misses the shape F15 fixed.
*Where:* `T:4704` (`startswith("not ")`), `T:4706` (patterns limited to `.exists()`/`.is_file()`),
`T:4711` (`"raise " in body_code`), `T:4713` (`if not node.orelse`).
*Observed:* the `else:`-default form is **never flagged** — a violation is appended only when there
is **no** `orelse`. Nine of ten planted shapes pass, including the ternary the schema line used at
`73efb9f:proofs/S0-01/check_acp_conformance.py:1704`.
*Failing input:* `def _v(p):\n    if p.exists():\n        return p.read_text()\n    else:\n        return "{}"` → `1 passed`.
*Minimal fix:* flag whenever the false path (explicit `else` or fall-through) can yield a value
without raising; add `os.path.exists`, `.is_dir()`, `os.access`, glob truthiness,
`try/except FileNotFoundError`, and `IfExp`.
*Exact red test:* `test_ck12_ap40_pin_flags_an_else_default`. **SOLID.**

### F-CK12-05 — BLOCKING. The AP-40 pin's exemptions are keyed by hard-coded line numbers.
*Where:* `T:4686-4690`.
*Observed:* one `# shift` comment prepended to `check_acp_conformance.py` →
`AssertionError: AP-40 hits: ['check_acp_conformance.py:1717 …']`. Every mutant I planted above
`C:1713` tripped this before its real signal could be read. M20 shows the list itself is unguarded.
*Failing input:* `sed -i '1i # shift' proofs/S0-01/check_acp_conformance.py`.
*Minimal fix:* key on `(file, enclosing function, ast.unparse(node.test))`.
*Exact red test:* `test_ck12_ap40_exemptions_survive_a_line_shift`. **SOLID.**

### F-CK12-06 — The B1 ordering fix has no in-gate killer.
*Where:* `T:2878`. *Observed:* M03 → `1 xfailed`, indistinguishable from baseline on the stale
declared corpus; a re-introduction would ship green.
*Minimal fix:* extract the branch into `_grade_negative(ok, result) -> str` and unit-test its three
outputs, or stub `cc.check_negative` to succeed and assert the retire message.
*Exact red test:* `test_ck12_b1_a_passing_negative_leg_is_a_hard_failure`. **SOLID.**

### F-CK12-07 — The dead-branch pin covers 5 of 6 comments and 5 of 7 citations, and is opt-out.
*Where:* `T:4918` `m = re.search(...)` + `T:4919` `if m:`. `C:1605` carries no citation; `C:957`
carries two and only the first is checked.
*Observed:* M14 → `1 passed`; M16 → `1 passed`. The lane's DONE row claims 6/6.
*Minimal fix:* `re.findall` and enforce every match; `assert m` so a citation-less comment fails.
*Exact red test:* `test_ck12_every_dead_branch_comment_cites_at_least_one_range` — red today.
**SOLID.**

### F-CK12-08 — The lane's own new code carries the AF-AP-40 shape it was closing, unreported.
*Where:* `T:2629`, `T:2632`, `T:2635`, `T:2637` — `_corpus_version()` (`T:2622`) returns the default
`"v2.2"` on every absence.
*Observed:* `_CORPUS_VERSION` (`T:2641`) silently downgrades and flips 9 tests from real assertions
to xfails. `scripts/lint_delta.py --base 73efb9f` raises `AF-AP-40` on the lane's added lines; the
report's AP-SCREEN lists only AP-66. Related: `test_real_leg_process_evidence` adds a `strict=True`
xfail marker **before** its `pytest.fail("corpus v2.2: … absent")` calls, so those failures are
swallowed as expected failures.
*Minimal fix:* make `_corpus_version` raise on a malformed corpus; move the `pytest.fail` guards
above `add_marker`.
*Exact red test:* `test_ck12_corpus_version_fails_on_a_missing_scan_header`. **SOLID.**

### F-CK12-09 — The sidecar verification is one-directional; its declared-artifact list is unreachable; and it has no killer.
*Where:* `T:2684`, `T:2689` (sha loop) and `T:2700-2706` (declared artifacts).
*Observed:* (a) adding `run-1/evil.txt` → `1 passed`, no signal; (b) deleting a declared artifact
raises `FileNotFoundError` from `_sha256_file` inside the sha loop, so the intended
`corpus <leg>/<fn> absent -- declared artifact missing` never renders; (c) M08 leaves the
clean-corpus gate green.
*Minimal fix:* compare the sidecar's relative-path set against the corpus walk **both ways**; guard
`_sha256_file` with a named `pytest.fail`; commit a tiny drifted fixture corpus so the loop has a
real regression test.
*Exact red test:* `test_ck12_corpus_rejects_an_unlisted_file` + `test_ck12_missing_declared_artifact_is_named`.
**SOLID.**

### F-CK12-10 — A residual presence-gated silent skip and an accept-any-pass assertion in the real-leg set.
*Where:* `T:2779` `test_real_leg_manifests`; `T:2784` `pytest.skip("baseline manifest absent")`; the
`if ok: pass  # no failure — acceptable` arm below it.
*Observed:* the baseline exists today (`4 passed`), so nothing is skipped; but the shape is the same
fail-open the round closed for `test_real_leg_negative`, and the AP-40 class scan at `T:4675` covers
production files only, never the test module.
*Minimal fix:* give the baseline declaration semantics (fail, not skip) and decide the manifest
expectation the way B1 was decided.
*Exact red test:* `test_ck12_no_presence_gated_skip_in_the_test_module`. **SOLID.**

### F-CK12-11 — The directory sub-class produces an unnamed, non-portable reason.
*Where:* `C:1851` `except Exception as exc`, reached from the five unguarded reads.
*Observed:* five directory probes → `failure_reason: malformed evidence: IsADirectoryError: [Errno 21] Is a directory: '<absolute tmp path>'`.
Fails closed (rc 1) — **no hollow green** — but the reason cannot be asserted and the sub-class is
untestable at the contract level.
*Minimal fix:* the `require_regular_file` from F-CK12-03 turns all five into named reasons.
**SOLID.**

### F-CK12-12 — The `_corpus_file` guard added this round has no killer.
*Where:* `T:2612-2618`. *Observed:* M23 (`return p` as the first statement) →
`43 passed, 317 deselected, 9 xfailed` — no test notices.
*Minimal fix:* one negative control — `mkfifo` a corpus file in a scratch corpus copy, assert the
`pytest.fail` message. *Exact red test:* `test_ck12_corpus_file_names_a_non_regular_artifact`.
**SOLID.**

### F-CK12-13 — F9 has no killer, and the report presents it as covered.
*Where:* `C:1638-1639`; test at `T:4856`. *Observed:* M11 → `15 passed`. The monkeypatched `alarm`
raises only for a non-zero argument, so the ordering is unobservable — as the code comment concedes.
*Minimal fix:* none in the code; state in the report that F9 is inspection-only, or make the
monkeypatched `alarm` raise for `0` too and assert the handler is still restored. **SOLID.**

### F-CK12-14 — Three mutant rows in the lane's report are not reproducible as written.
*Where:* `A5j-report.md:78`, `:79`, `:80`.
*Observed:* under the gate's own default exports, mutant 5 gives `2 passed` (M09) and mutant 6 gives
`2 passed` (M07b). They die only with `S0_01_REAL_LEG_DIR` **unset** (M09b) and with a **hostile
venue** (M07c) — configurations the report does not state; the brief demanded exactly the unset
configuration. Mutant 7's row is a control demonstration on a hostile corpus, not a kill by a
committed test.
*Minimal fix:* state the environment on every mutant row; label control demonstrations as such.
**SOLID.**

### F-CK12-15 — The report's headline gate number predates the bytes it is attached to.
*Where:* `A5j-report.md:132-136` (`373 passed, 9 skipped, 1 xfailed in 1070.87s`) vs `:157` NOT_DONE
*"Full re-gate on sweep-amended bytes: NOT run."*
*Observed:* the pasted headline gate is not a gate on the committed bytes. My own two runs on the
PIN give `374 passed, 9 xfailed`. The lane is honest in NOT_DONE, but the number sits under **GATES**
as if it were the checkpoint's.
*Minimal fix:* re-run and re-paste, or move the stale number under NOT_DONE with its rev. **SOLID.**

### F-CK12-16 — The report's PIN header names a commit that is not the checker's parent.
*Where:* `A5j-report.md:3` `PIN: ac3117f (HEAD at dispatch)`.
*Observed:* `ac3117f` is *"transcripts: scrubbed sandbox chat digests"*; the checker files' true
parent is `73efb9f` and the landed checkpoint is `dc9f596`.
*Minimal fix:* header the report with the parent the red-before was run against.
**SOLID on identity, UNSURE on intent.**

### F-CK12-17 — `symlink_to` was dropped from the write-scan family because it flagged existing calls.
*Where:* `T:3351` `_WRITE_ATTRS`; report row S-17.1b names the trigger (*"PC gate: symlink_to at
T:2169/2180 flagged pre-existing calls"*).
*Observed:* the two sites create **new** dirents (`999999.json`, `manifest-evil.txt.gz`) and cannot
reach a shared inode, so the removal is harmless today and the stated reason is sound. But the
remedy was to drop a whole detection family rather than exempt two sites — the "loosen the gate to
go green" shape.
*Minimal fix:* keep `symlink_to` in `_WRITE_ATTRS` and add the two enclosing test functions to
`_EXEMPT_FNS` (`T:3357`); the F43 self-test's category set gains `.symlink_to`. **SOLID.**

### F-CK12-18 — Cosmetic: the B1 hard-failure message triples the `negative:` prefix.
*Where:* `T:2886` `f"unexpected failure: negative: {result}"` on a `result` that already carries
`negative: negative: `. Observed:
`unexpected failure: negative: negative: negative: probe reported an error: probe_sha256 mismatch`.
*Minimal fix:* drop the literal prefix. **SOLID.**

### Carry-forward (SWEEP-prod rows I re-ran on the PIN; outside A5j's brief)

- **SWEEP #37 — highest severity found.** Bare `raise SystemExit()` inside a check → `rc=0`, stdout
  **empty**. `C:1849` `except SystemExit as se: return int(se.code or 0)`; `spec.json`'s positive leg
  expects only `{"exit_code": 0}` → mints a green with no PASS line. Fix:
  `return 70 if se.code is None else int(se.code)` plus `"stdout_contains": "PASS: S0-01"` on the leg.
- **SWEEP #2.** `golden/` or the fixtures root replaced by a symlink → byte-identical PASS, rc 0.
- **SWEEP #3d/#4.** Permissive schema substitution → byte-identical PASS; no schema pin in `pins.py`.
- **SWEEP #30.** FIFO **or** a regular file at the `golden` root → `rc=2 deferred: v2 evidence not captured`.
- **SWEEP #1.** The real corpus cannot be checked end-to-end (Item 9).

---

## MUTANT TABLE — 24 mutants + 27 planted variants, every one EXECUTED, all on scratch copies

Restore after each is `cp -a` from `scratchpad/vck12/` — never git. The eleven survivors and both
kill-controls were **re-run from scratch after the container restart** and gave identical verdicts.

| # | mutant | target | selection | result | verdict |
|---|---|---|---|---|---|
| M01 | XFAIL-SUBSTRING (rsplit tail) | `T:2869` | `known_stale` | `1 failed` | KILLED — `T:4591` |
| M02 | XFAIL-TAIL-COLLISION (substring accept) | `T:2869` | `known_stale` | `1 failed` | KILLED |
| M03 | B1-ORDER | `T:2878` | `real_leg_negative` | `1 xfailed` | **SURVIVOR** (F-CK12-06) |
| M04 | SCHEMA-PRESENCE-GATED (revert the ternary) | `C:1707` | `absent_acp_schema or no_presence_gated` | `1 failed, 1 passed` | KILLED by the instance test only |
| M05 | PROBE-EXISTS-ONLY (delete `N:181-182`) | `N:181` | fifo/dir/every_read | `2 failed, 1 passed` | KILLED; read-scan blind |
| M06 | READ-SCAN-OFF (`checked_files = []`) | `T:4723` | `every_read_is_under` | `1 passed` | **SURVIVOR** (F-CK12-02) |
| M07 | VENUE-LOOSE (both asserts removed) | `T:2657`,`T:2668` | venue/corpus | `2 passed` | **SURVIVOR** (test-only property) |
| M07b | VENUE-LOOSE (lane form, venue=sandbox) | `T:2668` | same | `2 passed` | **SURVIVOR** (F-CK12-14) |
| M07c | VENUE-LOOSE (lane form, venue=`sanbox`) | `T:2668` | same | `1 failed, 1 passed` | KILLED — `T:2657` |
| M08 | SIDECAR-UNCHECKED (`for line in []`) | `T:2684` | `corpus_declared`, clean corpus | `1 passed` | **SURVIVOR** (F-CK12-09c) |
| M09 | CORPUS-UUID-LITERAL (var SET) | `T:2580` | real_leg_dir/corpus | `2 passed` | **SURVIVOR** |
| M09b | CORPUS-UUID-LITERAL (var UNSET) | `T:2580` | same | `1 failed, 1 passed` | KILLED — `T:2644` |
| M10 | ALARM-OUTSIDE-TRY | `C:1632` | alarm/cap | `1 failed, 1 passed` | KILLED — `T:4856` |
| M11 | F9-ORDER-SWAP | `C:1638-1639` | alarm/timeout/cap (15 tests) | `15 passed` | **SURVIVOR** (F-CK12-13) |
| M12 | DEADCOMMENT-WRONG-LINE | `C:1568`,`C:1597` | `dead_branch_comments` | `1 failed` | KILLED |
| M13 | DEADCOMMENT-WRONG-LINE-2 | `C:957` | same | `1 failed` | KILLED |
| M14 | DEADCOMMENT-SECOND-CITATION | `C:957` | same | `1 passed` | **SURVIVOR** (F-CK12-07) |
| M15 | MOVE-THE-RAISE (`C:743`) | `C:743` | same | `1 failed` | KILLED |
| M16 | DEADCOMMENT-DROP-CITATION | `C:1568` | same | `1 passed` | **SURVIVOR** (F-CK12-07) |
| M17 | F43-SCAN-OFF | `T:3367` | `f43_no_direct_writes` | `1 failed` | KILLED — `T:3465` |
| M18 | F43-CATEGORY-DROP (`truncate`) | `T:3356` | same | `1 failed` | KILLED — `T:3499` |
| M19b | STARTUP-CHECKS-TRIM (drop `typing`) | `T:4521` | `startup` | `1 failed, 15 passed` | KILLED — `T:4547` |
| M20 | AP40-EXEMPTION-WIDEN | `T:4686` | `no_presence_gated` | `1 passed` | **SURVIVOR** (F-CK12-05) |
| M21 | READSCAN-ALLOWLIST-WIDEN | `T:4767` | `every_read_is_under` | `1 passed` | **SURVIVOR** (F-CK12-02) |
| M22 | REQUIRE-FILE-SISREG-OFF | `C:198` | fifo/dir/absent/every_read | `2 failed, 3 passed` | KILLED |
| M23 | CORPUSFILE-GUARD-OFF | `T:2613` | `real_leg or corpus` | `43 passed, 9 xfailed` | **SURVIVOR** (F-CK12-12) |
| CTRL | LINE-SHIFT (one comment as line 1) | `C:1` | `no_presence_gated` | `1 failed` | control — proves F-CK12-05 |

**13 killed / 11 survivors.** Plants: 17 read vectors (5 caught, 10 missed, 2 invalid) and 10 gate
shapes (1 caught, 9 missed). Every survivor is attached to a numbered finding. The rig is proven to
kill when it should: M01 and M15 were re-run as controls after the restart and both went red.

---

## GATES I RAN

| gate | command | result |
|---|---|---|
| report_lint (the lane's report) | `--rev dc9f596 --map C/T/N` | `145 refs — OK 60, NEAR 11, MISS 50, UNCHECKABLE 21, UNRESOLVED 3` (exit 1) |
| ap_screen (prod) | `ap_screen.py C N` | `8 hits over 2 files` — all five AF-AP-40 classified by running |
| ap_screen (tests) | `ap_screen.py --tests T` | `AP-66: 2` — pre-existing on the parent |
| pyflakes | `python3 -m pyflakes C N T` | rc 0, no output |
| lint_delta | clean PIN worktree, `--base 73efb9f` | rc 0; **AF-AP-40 + AP-1 tells on the lane's added test lines** |
| red-before (parent `73efb9f` + PIN tests) | full file, no `-x` | `5 failed, 7 passed, 357 deselected in 61.04s` |
| PIN targeted | full file, no `-x` | `12 passed, 357 deselected` |
| real-leg ×2 | declared corpus | `53 passed, 307 deselected, 9 xfailed` both runs |
| **PC (the carve-out)** | clean detached worktree of the PIN, `pc_suite.sh launch -n 8` → `log` | **`468 passed, 9 xfailed in 146.55s`**, run `20260908T003842Z-dc9f596`, `patch 0B` |
| **sandbox 3-file gate, run 1** | single process, `--basetemp scratchpad/bt/gate1` | **`374 passed, 9 xfailed in 1098.87s (0:18:18)`** |
| **sandbox 3-file gate, run 2** | 4 foreground calls over deterministic node-ID chunks | **`374 passed, 9 xfailed`** — see below |

**On the two sandbox gate runs.** Run 1 completed before the container restart; its log is intact,
carries all six progress lines through `[100%]`, its final summary line, and zero
`Terminated`/`KeyboardInterrupt`/`INTERNALERROR` markers — a finished run, not a truncated one.
Run 2 was done after the restart as instructed. There is no `pytest-xdist` in this sandbox and a
serial pass takes ~18 min, longer than one foreground call allows, so I partitioned the 369 collected
node IDs of the checker file into three chunks (`split -n l/3`) plus the two companion files, and ran
each as its own foreground call with its own `--basetemp`:

```
chunk 1 (137 ids)   137 passed                      in 392.34s
chunk 2 (124 ids)   119 passed,  5 xfailed          in 311.56s
chunk 3 (108 ids)   104 passed,  4 xfailed          in 475.59s
companions (14)      14 passed                      in   2.71s
                    ---------------------------------------
total               374 passed,  9 xfailed          = 383 collected
```

383 is exactly the `--collect-only` total for the three files, so every collected test ran, and the
two independent runs agree on both counts.

**One environment incident, isolated, not a code defect.** Chunk 3's first attempt returned
`1 failed, 74 passed, 4 xfailed, 29 errors` with an `OSError` raised inside CPython's `tempfile` module. `df -h /` showed the
shared disk at **97 % (1.3 G free)** — each bundle fixture costs ~28 MB of `basetemp`. I re-ran two
of the failing tests in isolation and both passed (`1 passed in 2.68s`, `1 passed in 10.62s`), freed
**only my own** scratch directories, and re-ran chunk 3 clean at 80 % disk. The 29 errors were
ENOSPC, not the code.

## WHAT I REPRODUCED vs REVIEWED vs SKIPPED

**Reproduced by running (SOLID).** The red-before on `73efb9f` (rebuilt from `git archive` after the
restart, identity proved by sha) and all five red tests plus seven controls; all four B1 states on
repaired and poisoned corpus copies; 14 checker-path and 5 spec-entry FIFO/dir probes; the 49-site
coverage measurement; 17 read plants; 10 gate plants; the line-shift control; 24 mutants (all 11
survivors and 2 kill-controls re-run post-restart); the 11-configuration venue/corpus matrix; four
corpus/sidecar mutations; the five AF-AP-40 classifications; the naive and permissive schema
substitutions; SWEEP #2, #30, #37; the real-corpus end-to-end failure and its set differences;
report_lint, ap_screen, pyflakes, lint_delta; the PC gate; both sandbox gate runs.

**Reviewed statically, no run.** AP-32 at `C:167`, `C:175`, `N:39`; SWEEP rows #19, #20, #22, #29,
#38, #46-#51 (no A5j edit touches them, and the sweep's own runs stand); `C:2-3`'s NOTE.

**Deliberately skipped, with the reason.** SWEEP #5 (`pc_post.sh` header/body counters) and SWEEP #7 (the probe's own
fixture read in `proofs/S0-01/tools/acp_probe.py`) — both files are outside the lane's boundary **and** held dirty in the
shared tree by other lanes, so I could not grade their committed bytes without touching that work.

## SHARED-TREE HYGIENE AND PROCESS CENSUS

`git -C /home/user/agent-factory status --porcelain -- proofs/S0-01/check_acp_conformance.py
proofs/S0-01/negative_contract.py tests/test_s0_01_check_acp_conformance.py` → **empty**, at start
and at end: I never wrote to my three scope files in the shared tree. The tree's overall dirty set
grew during the session (`pins.py`, `tools/build_capture_record.py`, `tools/pc/pc_launch.py`,
`tools/pc/pc_negative.py`, `tools/pc/pc_post.sh`, `tests/test_s0_01_pc_post_scan.py`, plus untracked
`proofs/S0-02/`, `S0-04/`, `S0-05/`, `fixtures/`) — other lanes' work, none of it mine. No
`stash/checkout/restore/reset/add/commit/push`. One `git worktree add --detach`, used for the PC
gate and removed afterwards with `worktree remove --force` + `prune`. Two fixtures inside **my own
scratch copy** were briefly replaced by FIFOs and restored byte-identically
(`db136158249e85b3`, `b9eb56dd9a75cb34`, both equal to `git show dc9f596:<path> | sha256sum`).

Processes: only ones I started — one detached pytest for gate run 1 (killed by the container
restart, after it had already written its summary) and short-lived foreground `pytest`/`python3`
children. Five other lanes' suites (S0-02, S0-03, S0-04, S0-06, S0-08) were live on the box and were
**not** touched: no `pkill`, no `killall`, no signal to any PID I did not start. No PC process was
started or stopped beyond the one sanctioned `pc_suite.sh` run.

---

## REPORT_LINT ON THIS REPORT — and what it does and does not prove

```
python3 scripts/report_lint.py <this report> --rev dc9f596 --map C/T/N
report_lint: 249 refs — OK 59, NEAR 11, MISS 113, UNCHECKABLE 39, UNRESOLVED 27   (exit 1)
```

**My MISS is not zero, and I am not going to wave it away the way F-CK12-01 faults the lane for
doing.** Here is the accounting, and the evidence behind it.

- **UNRESOLVED 27** is structural: every one is a citation of `A5j-report.md:NN` or of a
  `report:NN` line inside my quoted F-CK12-01 evidence block. The tool maps only `C`/`T`/`N` to
  pinned source files, so a citation of a *document* cannot resolve. Nothing to fix.
- **MISS 113** is the token heuristic: the tool asks whether a claim token on the report line
  appears at the cited source line. On a mutant table the claim token is a mutant NAME
  (`READSCAN`, `MOVE`, `RAISE`), on a probe table it is an observed output (`1 passed`, `FIFO`) —
  by construction none of those live in the source. That is the same shape of excuse the lane
  made; the difference is that **I ran the symbol audit instead of asserting the conclusion.**
- **The audit.** `scratchpad/selfaudit.py` extracts every distinct `C:`/`T:`/`N:` reference in this
  report, resolves each against `git show dc9f596:<file>`, and prints the line it actually lands
  on — 98 distinct references, all listed. Reading that output found **four of my own drifted
  references**, which I corrected before returning this report:

```
F17 corpus-is-a-directory      T:2673 -> T:2674   (assert _REAL_LEG_DIR.is_dir())
M01/M02 mutation target        T:2868 -> T:2869   (return result in _KNOWN_XFAIL_REASONS)
negative name-set check        N:85-91 -> N:87-93 (present = {...}; if present != set(...))
the parent's schema ternary    C:1704 -> 73efb9f:proofs/S0-01/check_acp_conformance.py:1704
                                                  (a PARENT-rev line; at the PIN it is unrelated code)
```

  The last one is the instructive case: `C:1704` was not a typo, it was a **parent-rev line number
  presented as a PIN line number** — the same class of error as F-CK12-01, caught in my own text by
  running the check rather than trusting it.

Two further references resolve only against the parent by design and are labelled as such in place:
`73efb9f:tests/…:85-87` (AP-66 pre-existing) and the parent schema line above.

## THE CHEAPEST PATH TO MERGE-READY

Four edits and one re-paste, in this order:

1. **`negative_contract.py` (F-CK12-03).** Add `require_regular_file(path, leg, name)` to `pins.py`;
   route `N:59`, `N:97`, `N:160`, `N:207` through it. Ship the parametrised FIFO test. This closes
   the only finding that hangs a production entry point, and it also closes F-CK12-11.
2. **The read scan (F-CK12-02).** Replace the three heuristics with the committed golden set, or at
   minimum add the coverage floor plus the five missing read categories. The pass bar is M06 and M21
   both going red.
3. **The AP-40 pin (F-CK12-04, F-CK12-05).** Invert the `orelse` logic and re-key the exemptions on
   `(file, function, unparsed test)`. The pass bar is B01/B07/B09 going red and the LINE-SHIFT
   control staying green.
4. **The report (F-CK12-01, F-CK12-14, F-CK12-15, F-CK12-16).** Regenerate every reference by
   `grep -n` on the committed bytes until `report_lint --rev <checkpoint>` reports MISS 0; state the
   environment on each mutant row; head the report with `73efb9f`; move the stale `373 passed` under
   NOT_DONE and paste a real gate.

F-CK12-06, F-CK12-07, F-CK12-09, F-CK12-10, F-CK12-12, F-CK12-13, F-CK12-17 and F-CK12-18 are each
a few lines and can ride the same checkpoint; none of them alone blocks. The SWEEP carry-forwards
(#37 first — it mints a silent green) belong to the next brief, not this one.
