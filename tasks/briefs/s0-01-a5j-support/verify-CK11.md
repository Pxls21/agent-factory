# VERIFY-CK11 — round-11 adversarial grade of lane A5i (S0-01 checker)

*Complete. Every number below was pasted from a run in this session; the verdict is at the end.*

## PREMISE

| item | observed |
|---|---|
| PIN | `73efb9f663f4509f17145b2bbde2de918a122934` — `git cat-file -e` exits 0; subject `S0-01 WIP checkpoint 8t: checker claims that hold …` |
| PIN parent | `77546be2a05208b2d9b03aeeae7cec6c3a3448b8` (checkpoint 8u, lane D5j backend) |
| local HEAD | `24e0961…` at the start, `934dec1…` at the end (it moved under me — see *Hygiene at close*). `git diff --stat 73efb9f <HEAD>` over the two scope files + `test_s0_01_pc_post_scan.py` + `realleg_sync.sh` + `pc_suite.sh` + `test_summary.sh` + `negative_contract.py` is **EMPTY at both** — every graded byte is identical at the PIN and at current HEAD |
| shared-tree dirt | `git status --porcelain` = **empty** at the start (no lane held the tree) and **empty** again at close; mid-review it briefly carried six other-lane files (tee/backend). None of mine, none graded. |
| graded from | `git archive 73efb9f \| tar -x -C <scratch>/ck11/pin` — the shared tree was never edited, staged, stashed, checked out or reset by me |
| `check_acp_conformance.py` @ PIN | sha256 `de13655acc86f5ac7a2a7ae772f9a9e58a5696cd978e25bf0cba1ff128b0093d`, **1854** lines — matches the lane report's FILE IDENTITY table verbatim |
| `test_s0_01_check_acp_conformance.py` @ PIN | sha256 `da1ce46654675f497d7e80ffc31814fba229fc7c73379a8f02d8f31b2d338f1c`, **4677** lines — matches |
| parent scope shas | `3edd8a20…` (1840 lines) / `5b192f83…` (4426 lines) — these are CK10's PIN shas, i.e. the checker/test bytes did not move between 9b2803c and 77546be |
| tee at the PIN | `proofs/S0-01/tools/frame_tee.py` sha256 `2f0666c2b2a91a025aaf3dad3be06e6f38b9dce8244d325258ec12d347416ac2` (last touched by `0f2606d`, checkpoint 8s) |
| declared corpus | `/root/s0-01-realleg/golden` — 5 legs, **142 files**; `bash scripts/realleg_sync.sh check` → `realleg_sync: /root/s0-01-realleg/golden intact (142 files)` rc 0; independently recomputed manifest `== golden.pc.sha256` |
| corpus PC twin | `realleg-sync/pc.sha` and `realleg-sync/sb.sha` are byte-identical (both sha256 `dc33039b1dbfbdb3a95189266c31b0f3ff5bd55df833f1a77500e6b0e75ea1e7`) and equal `golden.pc.sha256`. `realleg-sync/diff.txt` is a **stale** artifact of an intermediate ordering-only comparison, not a live discrepancy. |
| python | 3.11.15, pytest 9.1.1 |
| load at start | `load average: 1.35, 1.63, 1.94` (two other verifiers running scratch suites on this box) |
| PC leg | **NOT run by me** — no bridge action taken, per the brief. The PC gate line `364 passed, 9 skipped, 1 xfailed in 134.10s` is CARRIED, not measured. |

### Collection from the FINAL (PIN) bytes — measured

```
374 tests collected in 0.47s
tests/test_s0_01_check_acp_conformance.py : 360
tests/test_s0_01_audit_cp5_controls.py    : 3
tests/test_s0_01_pc_post_scan.py          : 11
```
360 + 3 + 11 = 374 = 364 passed + 9 skipped + 1 xfailed. **Reconciles with the gate of record.**
`-k "real_leg or corpus"` collects **52/360**; `-k real_leg` alone also **52** (the declaration test's
name contains `real_leg`); `-k corpus` alone **1**. So the real-producer population is **51** + 1 declaration test.

---

## ITEM 8 (taken first — the coordinator's three explicit questions ride on it)

### The four configurations, all executed on the PIN copy

| # | configuration | measured summary |
|---|---|---|
| 1 | both vars unset | `52 skipped, 308 deselected in 0.16s` — reason on all 51: `S0_01_REAL_LEG_DIR unset (real-leg corpus not declared for this venue)`; the declaration test skips with `S0_01_REAL_LEG_DIR unset and S0_01_VENUE is not sandbox/pc` |
| 2 | `S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden` | `42 passed, 9 skipped, 308 deselected, 1 xfailed in 8.08s` |
| 3 | venue=sandbox, dir = an EMPTY dir | `1 failed, 51 skipped, 308 deselected in 0.26s` |
| 4 | venue=sandbox, `S0_01_REAL_LEG_DIR` **unset** | `1 failed, 51 skipped, 308 deselected in 0.27s` |

All four match the lane report's PROBE table exactly. The tests that RUN in config 2 are the same
population that skips in config 1 (same `-k` selection, same 52 node ids, 51 + declaration).

### Coordinator question (a) — does `1 FAILED (incomplete), 51 skipped` meet the contract?

The pinned design (brief item 9) says an absent or incomplete corpus "FAILS loudly, never skips".
Measured behaviour, four corpus shapes:

| corpus shape | result | who fails |
|---|---|---|
| empty dir | `1 failed, 51 skipped` | only `test_real_leg_corpus_declared` (missing legs) |
| 5 leg dirs present but **empty of files** | `41 failed, 1 passed, 10 skipped` | the **producers**; the declaration test PASSES |
| full corpus minus the `negative` leg | `1 failed, 41 passed, 10 skipped` | declaration test; `negative`'s 10 tests skip |
| full corpus, `cancel` gutted of files | `10 failed, 32 passed, 9 skipped, 1 xfailed` | the `cancel` producers |

**Ruling: the contract's operative requirement is MET; its literal wording is not, and the wording is
the part that is wrong, not the build.** In every incomplete shape the *suite* goes RED — there is no
green-by-skip. The 51 skips in the empty-dir case are the per-leg guards doing exactly what they should
(a test cannot assert over a leg that is not there); the loudness comes from the declaration test, which
is selected by every `-k` expression that selects any producer (`real_leg` matches its name) and is a
plain module-level test in the 3-file gate set. I would not add a red test for this. **Not a finding**,
with one residual recorded below as **F19** (the declaration test checks directory NAMES only — a corpus
with the right five directory names and drifted contents passes it, and nothing at gate time checks
content; a badly-broken corpus is caught only because the producers then fail, which is adequate but it
is the producers, not the declaration, doing the work).

### Coordinator question (b) — CORPUS-UUID-LITERAL under venue=sandbox with the var unset

Mutation applied on a scratchpad copy (`ck11/mut`), reverting `T:2579` to the container-UUID literal
`Path("/tmp/claude-0/-home-user/bdab799a-.../scratchpad/realleg/golden")`:

```
env -u S0_01_REAL_LEG_DIR S0_01_VENUE=sandbox pytest -k "real_leg or corpus"
  → 42 passed, 9 skipped, 308 deselected, 1 xfailed in 8.37s
env -u S0_01_REAL_LEG_DIR S0_01_VENUE=sandbox pytest -k test_real_leg_corpus_declared
  → 1 passed, 359 deselected in 0.12s
```

**CORPUS-UUID-LITERAL SURVIVES the exact configuration the brief named as its killer.** The old
scratchpad corpus still exists and I verified it is byte-identical to the declared one (142 files,
manifest diff empty), so the mutant's run is indistinguishable from the honest one. The lane's
"survives in THIS container" claim is **confirmed and correct** — and the mutant is a **live survivor,
not a conditional pass**: nothing in the suite pins `_REAL_LEG_DIR` to the environment. See F1.

### Coordinator question (c) — is the handler-leak test vacuous?

`T:4625 test_ck10_sigalrm_handler_restored_after_a_bad_cap` calls `cc.check_bundle(Path("/tmp"),
timeout_s=2**31)`. At `C:1645-1647` the domain gate raises `ValueError` **before** `_check_with_timeout`
is entered, so `signal.signal(SIGALRM, …)` is never called and there is nothing to restore.

- **It is not vacuous**: on the parent bytes the same call installs the handler and `alarm(2**31)`
  raises `OverflowError` outside the try, leaking it. The test is a genuine red-before for the *domain
  gate*.
- **It is mislabelled**: it proves "a rejected cap installs no handler", not "the alarm is inside the
  try". Measured — the `ALARM-OUTSIDE-TRY` mutant (alarm moved back above the `try:`) passes
  `test_ck10_sigalrm_handler_restored_after_a_bad_cap` (`1 passed`) and passes the whole cap family
  (`16 passed, 344 deselected in 3.91s`).
- **The mutant is killable, so "N/A" is wrong.** I wrote the killer and reproduced both states (F2).

---

## ITEM 2 — B1, "the strict xfail is what it says"

`T:2819-2846` (`test_real_leg_negative`). Anchor: `tail = result.rsplit(": ", 1)[-1]`, then
`request.node.add_marker(pytest.mark.xfail(strict=True, raises=AssertionError, reason=…))`
**inside the `if not ok:` branch**, immediately followed by `assert False`.

### The three states, executed on scratch copies of the corpus (`ck11/corp`, `ck11/corp2`)

| state | how produced | PIN result |
|---|---|---|
| stale sha | the declared corpus as shipped | `XFAIL … real v2.2 sample: probe_sha256 mismatch (capture predates current probe)` — `359 deselected, 1 xfailed in 0.23s` |
| **repaired sha** | `runtime-identity.json.probe_sha256` set to the live `tools/acp_probe.py` sha `b9eb56dd…` | **`1 passed, 359 deselected in 0.13s`** — NOT "FAILED unexpectedly passing" |
| unrelated failure | `agent_exit_code = 3` | `AssertionError: unexpected failure: negative: negative: negative: agent_exit_code is 3, expected 0` — full reason, correct |

### F3 (SOLID, BLOCKING) — `strict=True` is structurally dead; a repaired capture passes silently

The marker is added **after** the check has already failed and one line before `assert False`, so the
test can only ever be XFAIL — XPASS is unreachable and `strict=True` can never fire. The pinned design
says the marker goes on "**before running the check**, so a repaired capture turns the xfail into a
FAILURE by design"; `T:2822-2824` asserts that behaviour in prose. **Measured: a repaired capture gives
`1 passed`.** This is F-R10-13's defect class (a docstring describing a mechanism that does not exist)
surviving the round that was raised to close it — the anchoring half of B1 landed, the strictness half
did not.

*Minimal fix + exact red test* (both verified on `ck11/fix`): replace the `if not ok:` guard with an
unconditional assertion before the xfail branch —
```python
ok, result = _run_check_safe(cc.check_negative, neg_dir)
assert not ok, ("check_negative PASSES on the real negative leg — the known-stale reasons "
                f"{sorted(_KNOWN_XFAIL_REASONS)} no longer reproduce; retire them (B1)")
```
Measured: repaired corpus → `1 failed, 360 deselected in 0.23s`; honest stale corpus still `1 xfailed`.
`strict=`/`raises=` then become dead ornament and should be dropped (they claim a mechanism the code
does not use).

### F4 (SOLID, BLOCKING) — the anchor still fails open on a tail collision, from corpus-controlled data

`negative_contract.py:173` raises `NegativeFailure(f"probe reported an error: {shown}")` where `shown`
is `runtime-identity.json["probe_error"]` — **a value read out of the evidence under test**.
`check_negative` wraps it as `f"{leg}: negative: {f}"`, so the reason becomes
`negative: negative: probe reported an error: <probe_error>` and `rsplit(": ", 1)[-1]` is exactly
`<probe_error>`.

Executed attack (`ck11/corp`, `probe_error = "probe_sha256 mismatch"`, an entirely different cause —
the probe itself reported an error):
```
XFAIL tests/test_s0_01_check_acp_conformance.py::test_real_leg_negative
  - real v2.2 sample: probe_sha256 mismatch (capture predates current probe)
359 deselected, 1 xfailed in 0.23s
```
**A broken capture is accepted as the known-stale xfail.** The gate is narrower than CK10's substring
gate but still not keyed on the reason; one evidence-controlled string reopens it.

*Minimal fix + exact red test* (verified on `ck11/fix`): pin the WHOLE reason and match by equality —
```python
_KNOWN_XFAIL_REASONS = frozenset({
    "negative: negative: probe_sha256 mismatch",
    "negative: negative: agent_interpreter_realpath mismatch",
    "negative: negative: spawned_at_utc is later than the first frame",
})
def _is_known_stale(result): return result in _KNOWN_XFAIL_REASONS

def test_ck11_known_stale_is_the_whole_reason_not_a_tail():
    assert _is_known_stale("negative: negative: probe_sha256 mismatch")
    assert not _is_known_stale("negative: negative: probe reported an error: probe_sha256 mismatch")
```
Measured with the fix: honest stale corpus `1 passed, 359 deselected, 1 xfailed in 0.56s` (the xfail
survives, reason now the full string); tail-collision corpus `1 failed, 360 deselected in 0.24s`.

### F5 (SOLID, BLOCKING) — B1 has NO committed test; XFAIL-SUBSTRING survives

`T:4525-4526` is a **comment**, not a test:
```
# B1: xfail anchored match — verifier's three states are reproduced on scratch copies
# of the corpus by the gate run (see the report's PROBE table).
```
Mutant **XFAIL-SUBSTRING** (revert the anchor to the parent's `[r for r in _KNOWN_XFAIL_REASONS if r ==
result or r in result]`), measured A/B on the declared corpus, `-k "real_leg or corpus or negative or
xfail"`:

```
PIN     : 52 passed, 9 skipped, 298 deselected, 1 xfailed in 86.18s (0:01:26)
MUTANT  : 52 passed, 9 skipped, 298 deselected, 1 xfailed in 87.61s (0:01:27)
```
**Identical — SURVIVES.** The mutation touches only `test_real_leg_negative`, which is inside that
selection, so no wider run can change the verdict. The brief's mutant list required this one to die.
This is an AF-AP-36 shape: a reviewer-reported blocker was closed by a code change carrying zero
committed regression coverage. The `_is_known_stale` regression test above kills it.

## ITEM 3 — B2, the F43 direct-write scan

### The category self-test kills every pattern family (8 mutants, `-k f43`, PIN baseline `1 passed, 359 deselected in 0.23s`)

| mutant | mutation | result | verdict |
|---|---|---|---|
| F43-SHUTIL-OFF | `_SHUTIL_WRITERS = set()` (T:**3317**) | `1 failed, 359 deselected in 0.65s` | **KILLED** |
| F43-OSW-OFF | `_OS_WRITERS = set()` (T:**3318**) | `1 failed, 359 deselected in 0.64s` | **KILLED** |
| F43-JSONDUMP-OFF | `if False and … func.attr == "dump"` | `1 failed, 359 deselected in 0.62s` | **KILLED** |
| F43-ATTRS-OFF | `_WRITE_ATTRS = set()` | `1 failed, 359 deselected in 0.62s` | **KILLED** |
| F43-TOUCH-OFF (mine) | drop only `"touch"` from `_WRITE_ATTRS` | `1 failed, 359 deselected in 0.60s` | **KILLED** |
| F43-IOOPEN-OFF (mine) | `if False and …` on the `io.open` branch | `1 failed, 359 deselected in 0.58s` | **KILLED** |
| F43-MODEKW-OFF (mine) | delete the `.open(mode=…)` keyword branch | `1 failed, 359 deselected in 0.61s` | **KILLED** |
| **F43-SCAN-OFF (mine)** | `violations = _scan_direct_writes(src)` → `violations = []` | **`1 passed, 359 deselected in 0.41s`** | **SURVIVES** → F6 |

CK10's B2 (the slack `>= 6` threshold) is **closed**: the set-equality over ten category strings kills
every single-family deletion, including two families the round added.

### The equivalence class, planted one at a time through `_scan_direct_writes` (29 vectors)

CAUGHT (13): `.touch`, `.rename`, `p.open(mode="w")`, `io.open(p,"w")`, `pl.Path(q).write_bytes(...)`
(alias-blind but attribute-keyed, so it fires), `open(p,"a")`, `shutil.copyfile`, `Path(p).open("w")`,
`open(p,"r+")`, a write inside a nested class method, a write inside an inner function, plus
`.write_text` / `.write_bytes`.

MISSED and **documented** in the T:3333-3336 limits (honest): `os.open`+`os.write`, variable mode
(`m="w"; open(p,m)`), `shutil.copytree`, `shutil.move`, `subprocess` `cp`, module-level writes.

MISSED and **undocumented** — findings:

| vector | measured | why it matters |
|---|---|---|
| `os.fdopen(os.open(p, O_WRONLY), "w")` | `MISSED []` | the docstring names `os.open+os.write`; `os.fdopen` is the same family under another name — a one-word widening makes the limit honest |
| `tempfile.NamedTemporaryFile(dir=bundle, delete=False)` | `MISSED []` | the brief's own vector; adds an unexpected entry to the bundle |
| `gzip.open(p, "wb")` | `MISSED []` | **writes through the hardlink** — the exact corruption `_rewrite` exists to prevent (`_rewrite` = `unlink(missing_ok=True)` then write, "to preserve the hardlinked pristine copy") |
| `os.truncate(p, 0)` | `MISSED []` | same — truncates through the hardlink |
| `os.remove` / `os.link` / `os.mkfifo` / `os.chmod` / `Path.mkdir` / `Path.unlink` / `Path.symlink_to` / `Path.hardlink_to` | `MISSED []` | do not clobber the pristine copy (they break or re-point the link), so out of the guard's stated purpose — recording for completeness, not as defects |

### F6 (SOLID, non-blocking) — the real-source arm of the F43 test has no mutation coverage

`T:3407-3408` claims: *"The real assertion and the self-test BOTH call `_scan_direct_writes` so the
scan cannot be disabled without the self-test also going red."* Measured: replacing the real
assertion's input (`violations = _scan_direct_writes(src)` → `violations = []`, T:3411) leaves
`1 passed`. The claim holds only for gutting the *function*; it does not hold for gutting the *call on
the real file*, which is the arm that actually protects the suite.
*Minimal fix*: inline the call so there is no rebindable local —
`assert _scan_direct_writes(src) == [], f"F43: direct writes outside _rewrite: {_scan_direct_writes(src)}"`.

### F7 (SOLID, low) — two genuine hardlink-clobbering vectors are outside the documented limits

`gzip.open(p, "wb")` and `os.truncate(p, 0)` both write through the hardlink that `_rewrite` exists to
protect, and neither is caught nor listed as a known limit at `T:3333-3336`.
*Minimal fix*: add `"truncate"` to `_OS_WRITERS`, add a `gzip.open`/`os.fdopen` branch beside the
`io.open` one, or — cheaper and in the AF-AP-30 spirit — extend the documented-limits sentence to name
`os.fdopen`, `gzip.open`, `os.truncate`, `tempfile.NamedTemporaryFile`. *Exact red test*: append to the
self-test source `def test_z():\n    gzip.open(p, "wb")\n` and assert `"gzip.open"` in the category set.

## ITEM 4 — B3, every read path under the walk / `_require_file` rule (the CLASS)

### The enumeration (AST, not grep): 40 read sites in `check_acp_conformance.py`

Every `open(...)`, `.read_text()`, `.read_bytes()` call, resolved to its enclosing function and its
receiver expression (`ck11/readmap.py`). Classification by path provenance:

| class | count | guard |
|---|---|---|
| receiver under `golden/` (leg dirs, `golden/manifests`, `golden/negative`) | 36 | the `os.walk` at C:1666-1681 (`walk_roots = [(golden,…), (_fixtures(),…)]`), plus `_require_file` on 14 of them |
| receiver under `_fixtures()` (`identities.json`, `upstream-token.fingerprint`, `acp-schema-v1.json`) | 3 | walked **and** `_require_file`'d |
| **outside both roots** | **1** — `HERE/"tools"/"frame_tee.py"` at **C:416** | `_require_file` — **this is the B3 fix, and it holds** |

The only `HERE /` file reads in the whole chain are C:416 (guarded) and one in a callee, below.
`pins.py` reads no files. `check_initialize.py`'s reads all resolve under `_fixtures()` or a leg dir.
The C:1660-1664 comment enumerates exactly this and is **honest** (it does not claim universality).

### The 20 directory-named files — executed, all 20

`test_ck11_dir_named_leg_file` parametrised over the full `_LEG_REQUIRED_FILES` set, fresh bundle each:
**`20 passed, 380 deselected in 48.36s`**, and every one produced the EXACT reason
`failure_reason: run-1: <name> is not a regular file` (`exact=True` on all 20 — `manifest-post.summary`
included, so F-R10-07 is closed at the class, not just at its instance).

### The 20 FIFO-named files — executed, all 20

`20 passed, 380 deselected in 2.46s`; every one named in **0.00 s** by the walk with
`failure_reason: golden: non-regular entry in evidence tree: run-1/<name>`. No blocking.

### The FIFO at `tools/frame_tee.py` — committed test + its mutants

PIN baseline `-k "fifo_at_tools or dir_named_manifest"`: `2 passed, 358 deselected in 2.31s`.

| mutant | result | verdict |
|---|---|---|
| TEE-FILE-EXISTS-ONLY (C:416 → bare `.exists()`) | `1 failed, 1 passed, 358 deselected in **12.48s**` (the FIFO blocked to the 10 s cap) | **KILLED** |
| PRE-READ-BARE (delete the `_require_file(post_sum_path…)` line at C:1711) | `1 failed, 1 passed, 358 deselected in 2.52s` | **KILLED** |

### F8 (SOLID, BLOCKING) — the read CLASS is still open: `proofs/S0-01/tools/acp_probe.py` is guarded by `.exists()` only

`proofs/S0-01/negative_contract.py:177-184`, reached from the checker's own entry point
(`_check_bundle_uncapped` → `check_negative` at C:1786 → `nc.validate_negative_dir`):
```python
probe_file = HERE / "tools" / "acp_probe.py"
if not probe_file.exists():
    raise NegativeFailure("tools/acp_probe.py absent")
...
if rid.get("probe_sha256") != _sha256_file(probe_file):
```
`_sha256_file` is `with open(path, "rb")`. In a real CLI run `negative_contract.HERE` and
`check_acp_conformance.HERE` are the **same** directory — the bundle fixture patches only `cc.HERE`,
so I restored that production identity by patching `nc.HERE` to the same `tmp_path`.

**Both CK9-F2 and R9-CK-F27 symptoms reproduce, executed:**
```
CK11-FIFO-ACP-PROBE elapsed=10.00s rc=70 out='failure_reason: checker timed out'
CK11-DIR-ACP-PROBE  rc=1 out="failure_reason: malformed evidence: IsADirectoryError:
                              [Errno 21] Is a directory: '…/tools/acp_probe.py'"
```
This is the exact F-R10-02 hang and the exact F-R10-07 generic reason, at the **sibling file in the
same directory** as the one B3 just fixed. B3 fixed the two instances CK10 named; the class it was
raised for is still open one file over.

*How far I drove it, honestly*: the hang is reproduced at **`cc.check_bundle`** — the same function
`main()` calls (C:1838), which adds only argv parsing. I tried the CLI **subprocess** boundary too
(`_run(bundle, fixtures_dir=…)` with the FIFO planted in the tree's own
`proofs/S0-01/tools/acp_probe.py`) and it stops earlier at `failure_reason: golden: golden not pinned`
— a synthetic bundle needs the in-process `PINNED_GOLDEN_SHA256` monkeypatch, and the committed
evidence root returns `deferred: v2 evidence not captured`. So the process-boundary run is **not**
reproduced; the function-boundary run is, twice, and the CLI would return the same rc 70 by the same
path. I restored `acp_probe.py` afterwards and re-verified its sha (`b9eb56dd…`, equal to the PIN's).

**Provenance, measured**: `git log -S 'if not probe_file.exists():'` dates the guard to checkpoint 4
(`b60f02a`) — it predates CK9-F2 and CK10-F-R10-02, both of which fixed the same class elsewhere.

*Attribution, stated fairly*: the lane made **no** universality claim — its DONE row 3 names the two
paths it fixed, and the C:1662-1664 comment enumerates rather than generalises (I checked; it is
honest). `negative_contract.py` is READ-ONLY for A5i, so the lane could not have fixed this inside
its boundary. The defect belongs to the **design**: B3 was pinned to two named instances instead of
the invariant (item 12 §3), which is AF-AP-30 — and this is now the **third round** in which the
same class is fixed at one path and left open at another (CK9-F2 at `identities.json`,
CK10-F-R10-02 at `frame_tee.py`, CK11 here). It blocks because the checker can still be hung to its
cap by a file placed in the repo's own `tools/` directory, not because the lane misreported. The
coordinator owns the call: widen the scope for the next round, or record it as an accepted residual
in writing.

*Minimal fix* (2 lines, `negative_contract.py:178`):
```python
import stat as _stat
if not probe_file.exists():
    raise NegativeFailure("tools/acp_probe.py absent")
if not _stat.S_ISREG(probe_file.lstat().st_mode):
    raise NegativeFailure("tools/acp_probe.py is not a regular file")
```
*Exact red test* (the one I ran, minus the print):
```python
def test_ck11_fifo_at_tools_acp_probe_is_named(bundle, tmp_path, monkeypatch):
    import time, importlib
    monkeypatch.setattr(importlib.import_module("negative_contract"), "HERE", tmp_path)
    probe = tmp_path / "tools" / "acp_probe.py"; probe.unlink(); os.mkfifo(probe)
    t0 = time.monotonic(); rc, out = _check(bundle, timeout_s=10)
    assert time.monotonic() - t0 < 5
    assert (rc, out) == (1, "failure_reason: negative: negative: tools/acp_probe.py is not a regular file")
```

## ITEMS 5 + 6 — B4/B5 and the cap's domain

### B4 — one default-cap literal: **confirmed**

`grep -n "\b90\b"` over the checker returns exactly three lines: C:12 (docstring), **C:1639
`def check_bundle(root: Path, timeout_s: int = 90)`** and C:1641 (comment). `main()` is C:1811
`timeout_s = None  # R8-CK-F2: let check_bundle's signature default apply` and C:1837
`kwargs = {"timeout_s": timeout_s} if timeout_s is not None else {}`. **MAIN-DEFAULT-900 is genuinely
N/A** — there is no second literal to mutate. `spec.json` `legs[0].timeout_s` = **120**, and
`test_ck10_cli_default_cap_is_below_the_runner_timeout` reads it from the file (not a literal).

### B5 — the two-users pin is consumed: **confirmed** (C:490 `PINNED_STARTUP_RESPOND_TO_TWO_USERS.split("(")[0]`)

### The cap domain — 17 CLI values, executed against the real CLI

Every value out of `0 < int <= 2**31-1` returns **rc 64** with the exact line
`usage: --timeout-s must be a positive integer` on stderr, stdout empty:
`0`, `-1`, `-90`, `2147483648`, `9223372036854775808`, `"90.0"`, `"0x5a"`, `"1e2"`, `"nan"`, `"inf"`,
`""`, `"abc"`. Accepted (rc 2 `deferred: v2 evidence not captured`): `1`, `90`, `2147483647`, `" 90"`,
`"+90"` — the last two are `int()`-valid positive integers, so acceptance is correct.
**No fail-open in the CLI domain.**

### The cap domain — 17 in-process values, with `signal.alarm` instrumented

`ValueError: timeout_s must be a positive integer`, **`alarm_calls=[]`** (nothing installed) and
**SIGALRM disposition unchanged**, for: `True`, `False`, `nan`, `inf`, `-inf`, `1.0`, `90.0`, `"90"`,
`"5"`, `0`, `-1`, `2**31`, `2**63`, `Decimal(90)`. Accepted: `2**31-1` (`alarm_calls=[2147483647, 0]`),
`90` (`[90, 0]`), `None` (uncapped, `[]`). **CK10's F-R10-03 / F-R10-05 / F-R10-04 are closed.**

### Cap and handler mutants

| mutant | selection | result | verdict |
|---|---|---|---|
| SIG-DEFAULT-900 | `default_timeout or cli_default_cap` (base `2 passed`) | `2 failed, 358 deselected in 0.35s` | **KILLED** ×2 |
| LITERAL-PINS-2U | `two_users or twousers or env_respond` (base `8 passed`) | `1 failed, 7 passed, 352 deselected in 19.81s` | **KILLED** |
| CAP-BOOL (`<= 0` revert) | `cap_rejects or out_of_range or sigalrm` (base `8 passed`) | `5 failed, 3 passed, 352 deselected in 1.12s` | **KILLED** ×5 |
| CAP-NAN (allow floats) | same | `1 failed, 7 passed, 352 deselected in 0.51s` | **KILLED** |
| CAP-OVERFLOW-AS-EVIDENCE | same | `1 failed, 7 passed, 352 deselected in 0.44s` | **KILLED** |
| **ALARM-OUTSIDE-TRY** | same | **`16 passed, 344 deselected in 3.91s`** over `cap or timeout or sigalrm or alarm` | **SURVIVES** → F2 |

### F2 (SOLID, non-blocking but the lane's "N/A" is wrong) — ALARM-OUTSIDE-TRY is killable and unkilled

The lane declared it N/A "defense-in-depth". It is not: the property is testable with one monkeypatch,
and the test is red on the mutant and green on the PIN. Verified both ways:
```
PIN     : 1 passed in 0.07s
MUTANT  : AssertionError: LEAKED: before=0, after=<function _check_with_timeout.<locals>._raise_timeout …>
          1 failed in 0.08s
```
*Exact red test to add*:
```python
def test_ck11_alarm_inside_try_cannot_leak_the_handler(monkeypatch, tmp_path):
    import signal as _s
    real = _s.alarm
    monkeypatch.setattr(_s, "alarm", lambda n: (_ for _ in ()).throw(OverflowError()) if n else real(0))
    before = _s.getsignal(_s.SIGALRM)
    with pytest.raises(OverflowError):
        cc.check_bundle(tmp_path, timeout_s=90)
    assert _s.getsignal(_s.SIGALRM) is before
```
`test_ck10_sigalrm_handler_restored_after_a_bad_cap` should be renamed to what it proves — *a rejected
cap installs no handler* — since it never enters `_check_with_timeout`.

### F9 (SOLID, low) — the `finally` restores in the wrong order, so the C:1630-1631 claim overstates

`C:1635-1636`: `finally: _signal.alarm(0); _signal.signal(_signal.SIGALRM, old)`. If `alarm(0)` raises,
the restore never runs. Measured on the **PIN** with `alarm` patched to raise unconditionally:
`AssertionError: LEAKED: before=…SIG_DFL…, after=…_raise_timeout…`. Unreachable in CPython (a literal
`0` cannot overflow), so this is a comment-accuracy defect, not an exploit.
*Minimal fix*: swap the two lines (restore the handler first), or say "a raising `alarm(timeout_s)`".

### F10 (SOLID, low) — the module docstring NOTE now understates the domain

`C:2-3` says a **non-positive** value is refused with 64. After this round, bool / float / NaN / inf /
str / `> 2**31-1` are also refused with 64. F-R10-21 asked for a NOTE that states current behaviour;
it states a strict subset of it. *Fix*: "a value that is not a positive `int` in `[1, 2**31-1]`".

## ITEM 7 — the zombies invariant and the dead-branch comments

### Zombies — both scans, mutants

Baseline `-k zombies`: `5 passed, 355 deselected in 44.55s`.

| mutant | result | verdict |
|---|---|---|
| ZOMBIES-HALF (drop `+ owned_present`, C:1260) | `1 failed, 4 passed, 355 deselected in 44.96s` | **KILLED** |
| ZOMBIES-TEARDOWN-UNREAD (`if False:` at C:1347) | `1 failed, 4 passed, 355 deselected in 44.25s` | **KILLED** |

The impossible header `owned=3 owned_present=3 owned_zombies=3` is rejected with the exact reason
`failure_reason: run-1: process-scan-after.txt owned_present=3+owned_zombies=3 exceeds owned=3`
(T:4636), and the teardown twin at T:4647. C:1256-1258 states the disjointness premise the invariant
rests on. **F-R10-11 closed.**

### F-R10-16 / 14 / 23 / 24 — each verified by its test (read on the PIN bytes)

- F-R10-16: `T:4484 assert len(ran) == len(checks), f"only {len(ran)}/{len(checks)} keys ran: …"` ✓
- F-R10-14: `T:4440-4443` builds the expected string from `cc.EXPECTED_CHECK_SEQUENCE` — exact `==` ✓
- F-R10-23: `T:4363 assert out == "failure_reason: run-1: process-scan-after.txt has no enumeration header"` ✓
- F-R10-24: `test_ck9_startup_missing_keys_exact` computes `missing = sorted(cc._EXPECTED_STARTUP_KEYS - present)` from the surviving tokens and asserts the exact list ✓

### F11 (SOLID, non-blocking) — F-R10-10 is 4/6 pinned, and two comments cite lines that hold no guard

`grep -n "R9-CK-F6:"` finds **six** comments (C:946, 956, 1552, 1568, 1597, 1605).
`test_ck10_dead_branch_comments_cite_a_real_guard` asserts `len(checks) == 4` — C:1552 and C:1605 are
**not pinned at all**, though the brief said "the SIX dead-branch comments".

Worse, the two it does pin at C:1568 and C:1597 both cite **`check_prompt_turn C:747-749`**. Measured
line-by-line, C:747-749 is:
```
747:    notifs = [o for o in a2c if "method" in o and "id" not in o]
748:    prompt_seq = next(e["seq"] for e in entries if …)
749:    term_entries = [e for e in entries if …]
```
— three assignments, **no `raise`, no guard**. The guard that actually makes `new_resp_idx` / `sid1` /
`sid2` non-None is **C:742-743** (`if not new_resp or "error" in new_resp or not (…).get("sessionId"):
raise Failure(f"{leg}: session/new has no sessionId response")`). This is F-R10-10's own defect shape
(a comment citing something that enforces nothing) surviving the round raised to close it.

And the pin cannot catch it — measured:

| mutant | result | verdict |
|---|---|---|
| DEADCOMMENT-WRONG-FN (`check_two_users` → `check_initialize_frames` in the C:946 block) | `1 failed, 359 deselected in 0.26s` | **KILLED** |
| DEADCOMMENT-DROPPED (delete the C:1597 comment) | `1 failed, 359 deselected in 0.25s` | **KILLED** |
| **DEADCOMMENT-WRONG-LINE** (`C:922-925` → `C:9999-9999`) | **`1 passed, 359 deselected in 0.15s`** | **SURVIVES** |

The pin's assertion is `fn in "\n".join(src[idx-1:idx+3])` — the comment it matched already contains
that function name, so only a wholesale name swap can fail it. Line references are unpinned.
*Minimal fix + exact red test*: parse the cited `C:<a>-<b>` out of each comment and assert the range
contains a `raise Failure` inside the named function —
```python
m = re.search(r"C:(\d+)-(\d+)", block)
a, b = int(m.group(1)), int(m.group(2))
assert any("raise Failure" in src[k - 1] for k in range(a, b + 1)), \
    f"{block!r} cites C:{a}-{b}, which contains no guard"
```
That is RED on the PIN today (C:747-749 holds no `raise`) and kills DEADCOMMENT-WRONG-LINE.
Cover all six by dropping the `len(checks) == 4` literal for `== 6` and adding the two patterns.

## ITEM 8 (continued) — the coordinator's own hunk, `tests/test_s0_01_pc_post_scan.py`

PIN baseline: **`11 passed in 0.98s`**.

### Ruling on the rejection of CK10's `if not foreign: assert pinned_present == "0"` — **the rejection is CORRECT, and on stronger grounds than the flake argument**

`pc_post.sh:74` counts `pinned_present` over the **full** `ps` table; `pc_post.sh:67,70` filter the
**body** (helper-shaped rows naming a pinned path are dropped unless owned). The two numbers are counts
over **different populations**, so `foreign == [] ⇒ pinned_present == 0` asserts a relation the
producer does not maintain — and it fails **deterministically**, no sibling worker required. I built
the counterexample through the same `ps` shim (`ck11/pcps`), one owned row + one helper-shaped
pinned row + one unpinned foreign row:
```
CK11-PP rows=3 owned_present=1 pinned_present=1 body={4242} foreign=[]
4 passed, 8 deselected in 0.13s
```
So CK10's proposal was not merely an AF-AP-59 flake shape — it was **wrong**. The coordinator's
replacement (`test_pinned_present_is_exact_over_a_synthetic_table`, EXACT over a synthetic world;
`assert int(m.group(7)) >= len(foreign)`, BOUNDED over the live one) is the correct form and matches
the tactic added at `9da1041`. The two `_split_world` controls are committed and both real.

### The producer mutants the coordinator named — plus two of mine

| mutant | result | verdict |
|---|---|---|
| PINNED-OVER-BODY (`pinned_present` counted over `keep`) | `2 failed, 9 passed in 0.95s` | **KILLED** |
| HELPER-FILTER-OFF (delete pc_post.sh:70) | `2 failed, 9 passed in 0.94s` | **KILLED** |
| UNPARSABLE-ROW-SOFT (mine: `sys.exit` → `continue`) | `1 failed, 10 passed in 0.87s` | **KILLED** |
| OWNED-PRESENT-BODY (mine: `owned_present` counted over `keep`) | `11 passed in 0.88s` | **SURVIVES — EQUIVALENT**: both `keep` filters retain every `r[0] in owned` row, so `owned & table_pids == owned & {r[0] for r in keep}` by construction. The pc_post.sh:68-69 comment states exactly this; the mutant confirms the comment. |

## ITEM 1 — the closure table, with every red-before reproduced on the parent

Method: `ck11/parentmix` = the PIN tree with the **parent's** checker blob
(`3edd8a20…`, 1840 lines) and the **PIN's** test file (`da1ce466…`, 4677 lines); the 3-file set,
no `-x`, selection = the 16 NEW + 23 CHANGED test functions (derived by AST diff, not by eye).

**Measured: `14 failed, 9 passed, 337 deselected in 57.07s`** — the "14 failed" in the lane report's
B1 row reproduces exactly.

### Genuine RED on the parent (14)

`test_ck9_owned_zombies_exceeds_owned` · `test_ck10_fifo_at_tools_frame_tee_is_named` ·
`test_ck10_dir_named_manifest_post_summary` · `test_ck10_cap_rejects_bool` · `_nan` · `_inf` ·
`_float` · `_string` · `_overflow` · `test_ck10_timeout_arg_out_of_range_is_a_usage_error` ·
`test_ck10_sigalrm_handler_restored_after_a_bad_cap` ·
`test_ck10_owned_zombies_plus_present_exceeds_owned` ·
`test_ck10_teardown_zombies_plus_present_exceeds_owned` ·
`test_ck10_dead_branch_comments_cite_a_real_guard`

### GREEN on the parent = CONTROL (9), each with the mutant that is its real evidence

`test_real_leg_corpus_declared` (CORPUS-UUID-LITERAL — **survives**, F1) ·
`test_f43_no_direct_writes_outside_rewrite` (F43-SHUTIL/OSW/JSONDUMP/ATTRS/TOUCH/IOOPEN/MODEKW-OFF — all die) ·
`test_ck9_owned_zombies_abc` · `test_ck9_env_respond_to_from_pin` · `test_ck9_a25_reorder_diagnostic` ·
`test_ck9_startup_wrong_value_parametrised` · `test_ck9_startup_missing_keys_exact` ·
`test_ck10_cli_default_cap_is_below_the_runner_timeout` (SIG-DEFAULT-900 — dies) ·
`test_ck10_env_respond_to_two_users_from_pin` (LITERAL-PINS-2U — dies)

### Closure table (one row per B/F item)

| item | closed by | red-before (measured) | verdict |
|---|---|---|---|
| **B1** F-R10-13 xfail strict | *nothing* — `T:4525` is a comment | `test_real_leg_negative` **XFAILS on the parent too** = CONTROL; XFAIL-SUBSTRING survives | **NOT CLOSED** (F3, F4, F5) |
| **B2** F-R10-08 F43 categories | `test_f43_no_direct_writes_outside_rewrite` (T:3445 cats set) | CONTROL — 7 family mutants are the evidence, all die | **CLOSED** |
| **B3** F-R10-02/07 read paths | `test_ck10_fifo_at_tools_frame_tee_is_named`, `test_ck10_dir_named_manifest_post_summary` | genuine RED ×2 | **instances CLOSED, CLASS OPEN** (F8) |
| **B4** F-R10-06 one default | `test_ck10_cli_default_cap_is_below_the_runner_timeout` | **CONTROL** (green on parent) — SIG-DEFAULT-900 is the evidence | **CLOSED** (report mislabels the row "genuine-red", F12) |
| **B5** F-R10-12 two-users pin | `test_ck10_env_respond_to_two_users_from_pin` | CONTROL (lane says so — correct) | **CLOSED** |
| **B6** report corrections | the report itself | — | **NOT CLOSED** (F12) |
| F-R10-03/04/05 cap domain | 6 `cap_rejects` + `timeout_arg_out_of_range` | genuine RED ×7 | **CLOSED** |
| F-R10-15 handler leak | `test_ck10_sigalrm_handler_restored_after_a_bad_cap` | genuine RED | **CLOSED for the domain gate; the alarm-in-try half is unpinned** (F2) |
| F-R10-11 zombies | `test_ck10_owned_zombies_plus_present_exceeds_owned` + teardown twin | genuine RED ×2 (+ the changed ck9 test) | **CLOSED** |
| F-R10-10 dead-branch comments | `test_ck10_dead_branch_comments_cite_a_real_guard` | genuine RED | **PARTLY** — 4 of 6 pinned; 2 cite a guard-free range (F11) |
| F-R10-16 key count | `T:4484 assert len(ran) == len(checks)` | CONTROL | **CLOSED** |
| F-R10-14 A25 exact | `T:4441` built from `cc.EXPECTED_CHECK_SEQUENCE` | CONTROL | **CLOSED** |
| F-R10-23 T:4363 exact | `assert out == "…has no enumeration header"` | CONTROL | **CLOSED** |
| F-R10-24 startup keys exact | `T:4511` exact computed list | CONTROL | **CLOSED** |
| F-R10-21 docstring NOTE | C:2-3 | — | **PARTLY** — now understates the domain (F10) |
| F-R10-20 `_split_world` control | `test_split_world_rejects_an_unexplained_foreign_row` + the positive twin + the synthetic-`ps` exact test | committed | **CLOSED** (coordinator's hunk) |
| F-R10-25 corpus declared | `test_real_leg_corpus_declared` + 51 skip guards + the two scripts | CONTROL | **CLOSED for the gate venues; open for any bare `pytest`** (F1, F13) |
| F-R10-09/17/18/19 report | — | — | **F-R10-09 and F-R10-17 REPEAT** (F12) |

## ITEM 11 — report discipline

### PIN wording — correct

The lane report's `PIN: af154ab` is the dispatch HEAD and it says "Landing = the coordinator's
checkpoint, made after this report." `git merge-base --is-ancestor af154ab 73efb9f` → **YES**. The
FILE IDENTITY shas and line counts (`de13655a…`/1854, `da1ce466…`/4677) match the PIN's bytes exactly.

### Collection block — correct, and from the FINAL bytes

I re-measured `374 tests collected in 0.47s`, `360 / 3 / 11`; 360+3+11 = 374 = 364+9+1. ✓

### The 99-failure run — the report does not mention it. B6 allowed "or not at all". ✓

### F12 (SOLID, BLOCKING) — B6 is not closed: 17 of 35 `file:line` refs are wrong, and two red-before rows are still mislabelled

The brief's own instruction: *"Every number and `file:line` in the report is PASTED from a tool run on
the FINAL tree (F-R10-17/18)."* Measured by `sed -n <N>p` on the PIN bytes:

| report ref | what the report says is there | what is actually at that line | true line |
|---|---|---|---|
| C:490 | the two-users pin (LITERAL-PINS-2U target) | `raise Failure(… should be {_expected_rt_env!r} …)` | **C:488** |
| C:1644 | the `check_bundle` signature (SIG-DEFAULT-900 target) | `# values >= 2**31 overflow signal.alarm's C int …` (a comment) | **C:1639** |
| C:1652 | "comment fixed" (the walk comment) | **a blank line** — 1652 is the *parent's* number | **C:1660-1664** |
| C:1823 | the CLI range check | `return 64` | **C:1829** |
| C:958 | a dead-branch comment | `if new_seqs[1]["seq"] < term_seqs[0]["seq"]:` (code) | **C:956-957** |
| C:1599 | a dead-branch comment | `if sid1 == sid2:` (code) | **C:1597-1598** |
| T:2815 | `test_real_leg_negative` | a line inside `test_real_leg_two_users` | **T:2819** |
| T:3313 | `_WRITE_ATTRS` | `# cannot be disabled without the self-test also going red.` | **T:3315** |
| T:3315 | `_SHUTIL_WRITERS = set()` | `_WRITE_ATTRS = {…}` | **T:3317** |
| T:3316 | `_OS_WRITERS = set()` | `_WRITE_MODES = set("wa+")` | **T:3318** |
| T:3383 | the `json.dump` branch | `if kw.arg == "mode" …` | **T:3387** |
| T:3395-3401 | the `io.open` branch | starts on the `_OS_WRITERS` branch | **T:3399-3407** |
| T:4359 | "exact" (ck9 owned_zombies_abc) | `_rewrite(sp, old.replace(…))` | **T:4363** |
| T:4368 | "exact" (ck9 env_respond_to_from_pin) | the test's docstring | **T:4372** |
| T:4438 | "A25 exact" | `rc, out = _check(bundle)` | **T:4441** |
| T:4479 | "startup parametrised **count**" | the per-key value assertion | **T:4484** |
| T:4503 | "startup missing keys exact" | `log_text = lp.read_text()` | **T:4511** |

Correct (18): C:416, C:1258-1261, C:1346-1348, C:1628-1632, C:1645-1647, C:1646, C:1711, C:1811,
C:1838, C:948, C:1568, T:2579, T:2597, T:3445, T:4562, T:4573, T:4636, T:4647.

**17 wrong of 35 — more than CK10's 13.** Two of them (C:1652, and the C:490/C:1644 mutant targets)
are *parent-tree* numbers, the exact F-R10-18 shape the brief named. Four point at code where the
report claims a comment, or at a different test function.

Red-before mislabels (F-R10-09 repeat): DONE row 4 (B4) says `genuine-red: MAIN-DEFAULT-900 survived
on PIN` — but the test is **green on the parent** (CONTROL) and MAIN-DEFAULT-900 is N/A, not a
red-before. DONE row 2 (B2) likewise says `genuine-red:` where the evidence is mutant survival, not a
parent-red. DONE row 1 (B1) attributes the collective "14 failed" to B1, though B1's own test
**xfails on the parent** and is not one of the 14.

*Minimal fix*: regenerate every ref with `grep -n` on the FINAL tree (one pass), relabel rows 1/2/4
CONTROL with the mutant named as the evidence.

Two further B6 gaps in the same report:
- **The 16-value CLI cap probe is claimed but not pasted.** The PROBE table's "Cap domain -- CLI (16
  values)" row says only *"Tested via test_ck10_timeout_arg_out_of_range_is_a_usage_error (rc 64) +
  existing ck9 tests"* — no values, no rc column, no usage line. The brief asked for the 16 values and
  their exact outcomes. (I ran 17; all correct — the probe's *conclusion* holds, its *evidence* was
  not shown.)
- **NOT_DONE says "None"** while the brief's gate list included *"the real tee under SIGTERM and clean
  exit through the checker"*, which the GATES section does not contain. I ran it and it passes, so
  this is a reporting gap, not a build gap.

## ITEM 8 (closing) — the corpus contract as a WHOLE

### The coordinator's side, verified here

- `bash scripts/realleg_sync.sh check` → `realleg_sync: /root/s0-01-realleg/golden intact (142 files)` rc 0.
  I also recomputed the manifest independently (`find … | sort | xargs sha256sum`) — identical to
  `golden.pc.sha256`.
- The PC twin: `realleg-sync/pc.sha` and `realleg-sync/sb.sha` are **byte-identical**
  (`dc33039b1dbf…`) and equal `golden.pc.sha256`. `realleg-sync/diff.txt` is a stale intermediate
  artifact — it does NOT describe the current pair. (Recommend deleting it; a reader will take it for
  a live discrepancy.)
- `scripts/pc_suite.sh:67` puts `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=$PC_REAL_LEG_DIR` **on the pytest
  line itself** ✓. `scripts/test_summary.sh` and `scripts/relaunch-suite.sh` export the sandbox pair
  as `${VAR:-default}` ✓ (I ran gate 1 with both vars explicitly unset and the defaults resolved).

### F1 (SOLID, BLOCKING) — CORPUS-UUID-LITERAL survives; nothing pins `_REAL_LEG_DIR` to the environment

Measured above under the brief's own killer configuration. The mutant's verdict depends on a directory
**outside the repository** (`<scratchpad>/realleg/golden`, which I verified is byte-identical to the
declared corpus, 142 files, manifest diff empty) — so it is not a mutation test at all in this
container. *Exact red test, verified green on the PIN in BOTH configurations and red on the mutant in
BOTH:*
```python
def test_ck11_real_leg_dir_is_resolved_from_the_environment():
    want = os.environ.get("S0_01_REAL_LEG_DIR")
    assert _REAL_LEG_DIR == (Path(want) if want else None), (
        f"_REAL_LEG_DIR={_REAL_LEG_DIR} does not track S0_01_REAL_LEG_DIR={want!r}")
```
```
PIN   var unset : 1 passed in 0.08s      PIN   var set : 1 passed in 0.08s
MUT   var unset : 1 failed in 0.12s      MUT   var set : 1 failed in 0.09s
```

### F13 (SOLID, non-blocking — a design call, not a build defect) — the green-by-skip path is still the DEFAULT for every invocation that is not one of the three wrapper scripts

`test_real_leg_corpus_declared` only bites when `S0_01_VENUE in ("sandbox", "pc")`. Nothing in the repo
sets it except `test_summary.sh`, `relaunch-suite.sh` and `pc_suite.sh`. Measured: with both vars unset
the checker suite reports **`52 skipped, 308 deselected in 0.16s`** and rc 0.
`.github/workflows/stage0-ci.yml:21` runs exactly `python -m pytest tests/ -q` with no venue, so **CI
runs zero real-producer coverage and is green** — by declaration, per the design, but the declaration
is the *absence* of a variable, which is the same shape F-R10-25 was raised against.
*Minimal fix*: invert the default — `venue = os.environ.get("S0_01_VENUE", "sandbox")` (or require an
explicit `S0_01_VENUE=ci`), and add `S0_01_VENUE: ci` to the CI workflow env. Then forgetting to
declare is loud.

## ITEM 12 — the design itself, where I would have designed differently (with evidence)

1. **Design item 1 is self-contradictory as pinned.** "Add `pytest.mark.xfail(strict=True)` *before*
   running the check" cannot coexist with state 3 ("an unrelated failure → FAILED with the full
   reason") — an unconditional xfail marker swallows *every* failure. The lane resolved the conflict by
   moving the marker after the check, which makes `strict=True` structurally dead (F3). The property
   the design wanted needs no marker at all: `assert not ok, "…retire _KNOWN_XFAIL_REASONS"`. I built
   it and it produces all three states (measured). **Specify the property, not the API call.**
2. **Anchoring on the reason's LAST segment buys nothing over the whole reason** and leaves an
   evidence-controlled string in the gate (F4: `probe_error` flows into the tail verbatim). The full
   reason is equally stable and closes it.
3. **B3 was scoped to two named instances instead of the invariant.** Evidence: F8 — the same class was
   still open one file over, in a callee the checker reaches on its own entry path. The enforcing form
   is an AST self-scan (the file already uses exactly this technique for F43): assert that every
   `open`/`read_text`/`read_bytes` receiver in the checker **and its callees** is either under
   `golden/`/`_fixtures()` or wrapped in `_require_file`. That test would have named `acp_probe.py`.
4. **"Structural pin" was specified as "the comment names its guard".** The lane implemented exactly
   that, and it is near-tautological (DEADCOMMENT-WRONG-LINE survives, F11). The pin that bites is
   "the cited `C:a-b` range contains a `raise Failure` inside the named function" — which is RED on the
   PIN today.
5. **CORPUS-UUID-LITERAL is not a mutation test.** Its verdict depends on a path outside the repo
   (F1). The design should have demanded the env-tracking assertion instead; the mutant then dies in
   any container.
6. **The corpus declaration defaults to silent.** See F13 — the safe default is "declare or fail".
7. **17 copies of the same 2-line skip guard** (T:2618-19, 2631-32, 2645-46, … 51 tests). One
   `skipif` marker or one fixture is one place to get wrong instead of seventeen; the round's whole
   purpose is shrinking the claim surface.

## F14 (SOLID, low) — one dead line is the only reason `_EXEMPT_FNS` grew a third entry

`_EXEMPT_FNS` went 17 → 20; the additions are `test_golden_run_eq`, `test_golden_distinctness_all`
(both do a legitimate directory `.rename()` after `copytree`+`rmtree`) and
`test_ck10_fifo_at_tools_frame_tee_is_named`. The last one is exempt solely because of **T:4542**:
```python
tee.write_text("placeholder")  # _session_bundle wrote a copy; overwrite with FIFO
tee.unlink()
os.mkfifo(tee)
```
The `write_text` is immediately unlinked and the bundle fixture already created the file
(`shutil.copytree(P / "tools", dest_tools, copy_function=shutil.copy2)`), so it does nothing.
Measured: deleting that line **and** the `_EXEMPT_FNS` entry → `pyflakes rc=0`,
`2 passed, 358 deselected in 2.92s` on `-k "f43 or fifo_at_tools"`. Shrinking the exemption list is
the opposite of the AF-AP-30 drift the lane flagged in its own SELF-ATTACK.

## F15 (SOLID, BLOCKING) — AF-AP-40 fail-open at C:1704: deleting the ACP schema makes the checker PASS with a byte-identical PASS line

```python
C:1703  schema_path = _fixtures() / "acp-schema-v1.json"
C:1704  schema = ci.load_schema(schema_path) if schema_path.exists() else None
```
This is the registered `AF-AP-40` signature verbatim (`if\s+\w[\w.]*\.(exists|is_dir|is_file)\(\)`
guarding an assertion in `proofs/**/check_*.py`). The schema is the *only* JSON-Schema validation the
checker performs on the ACP initialize request/response (`check_initialize.py:110-120`, wired at
C:1734 `_run_check(check_initialize_frames, …, schema=schema)`), and nothing requires the file:
`_require_file` guards `identities.json` and `upstream-token.fingerprint` but not this one, and the
per-leg allowlist at C:1729-1731 rejects *unexpected* entries, never a missing required one.

**Executed on a fresh bundle (`ck11/ap40`), deleting `tmp_path/fixtures/acp-schema-v1.json`:**
```
CK11-AP40-BASELINE rc=0 out='PASS: S0-01 acp-conformance - 63 checks executed over 5 legs;
                             golden x2 identical (11 normalized lines, sha256 e088d7827be7); …'
CK11-AP40-SCHEMA   rc=0 out='PASS: S0-01 acp-conformance - 63 checks executed over 5 legs;
                             golden x2 identical (11 normalized lines, sha256 e088d7827be7); …'
```
**The two PASS lines are byte-identical** — the check count does not move, so nothing distinguishes a
schema-validated run from an unvalidated one. That is anti-hollow-green tactic 7 exactly: green
without the claimed part running.

For contrast, the two other presence gates are safe: deleting `manifest-post.summary` →
`rc=1 failure_reason: run-1: manifest-post.summary absent`; deleting the negative leg's
`agent-stderr.txt` → `rc=1 failure_reason: negative: negative: agent-stderr.txt absent`.

**Provenance, measured**: `git log -S` dates the line to checkpoint 5 (`541648c`), i.e. it was added
**after** AF-AP-40 was registered at checkpoint 4 (`b60f02a`, "incidents AF-AP-39..43"). So it is an
unexploded sibling of a class this project had already written down — exactly what the bug-echo rule
exists to sweep. Not this round's edit, but it sits in the lane's own scope file and this round's
brief is "every guard pinned".

*Minimal fix (1 line), verified*:
```python
schema = ci.load_schema(_require_file(schema_path, "golden", "fixtures/acp-schema-v1.json"))
```
```
CK11-AP40-SCHEMA rc=1 out='failure_reason: golden: fixtures/acp-schema-v1.json absent'
CK11-AP40-BASELINE rc=0 out='PASS: … 63 checks executed over 5 legs; …'   (unchanged)
4 passed, 360 deselected in 21.42s
```
*Exact red test*:
```python
def test_ck11_absent_acp_schema_is_a_failure(bundle, tmp_path):
    (tmp_path / "fixtures" / "acp-schema-v1.json").unlink()
    assert _check(bundle) == (1, "failure_reason: golden: fixtures/acp-schema-v1.json absent")
```

## ITEM 9 — THE MUTANT TABLE

All mutants on scratchpad copies (`ck11/mut`, `ck11/comb`, `ck11/mutpc`, `ck11/fix`, `ck11/exmp`,
`ck11/ap40`). `git status --porcelain` on `/home/user/agent-factory` asserted **empty** before, during
and after; the shared tree was never edited, staged, stashed, checked out or reset.

| # | mutant | file:line | selection (baseline) | result | verdict |
|---|---|---|---|---|---|
| 1 | F43-SHUTIL-OFF | T:3317 `set()` | `f43` (`1 passed 0.23s`) | `1 failed, 359 deselected in 0.65s` | KILLED |
| 2 | F43-OSW-OFF | T:3318 `set()` | `f43` | `1 failed, 359 deselected in 0.64s` | KILLED |
| 3 | F43-JSONDUMP-OFF | T:3387 `if False and` | `f43` | `1 failed, 359 deselected in 0.62s` | KILLED |
| 4 | F43-ATTRS-OFF | T:3315 `set()` | `f43` | `1 failed, 359 deselected in 0.62s` | KILLED |
| 5 | F43-TOUCH-OFF | T:3315 drop `"touch"` | `f43` | `1 failed, 359 deselected in 0.60s` | KILLED |
| 6 | F43-IOOPEN-OFF | T:3400 `if False and` | `f43` | `1 failed, 359 deselected in 0.58s` | KILLED |
| 7 | F43-MODEKW-OFF | T:3381-3386 deleted | `f43` | `1 failed, 359 deselected in 0.61s` | KILLED |
| 8 | **F43-SCAN-OFF** | T:3411 `violations = []` | `f43` | **`1 passed, 359 deselected in 0.41s`** | **SURVIVES — real (F6)** |
| 9 | MAIN-DEFAULT-900 | — | — | no second literal exists (`grep -n "\b90\b"` = C:12, C:1639, C:1641) | **N/A, confirmed** |
| 10 | SIG-DEFAULT-900 | C:1639 `90`→`900` | `default_timeout or cli_default_cap` (`2 passed 0.13s`) | `2 failed, 358 deselected in 0.35s` | KILLED ×2 |
| 11 | LITERAL-PINS-2U | C:488 → `"allowlist"` | `two_users or twousers or env_respond` (`8 passed 19.32s`) | `1 failed, 7 passed, 352 deselected in 19.81s` | KILLED |
| 12 | CAP-BOOL | C:1646 → `timeout_s > 0` | `cap_rejects or out_of_range or sigalrm` (`8 passed 0.28s`) | `5 failed, 3 passed, 352 deselected in 1.12s` | KILLED ×5 |
| 13 | CAP-NAN | C:1646 allow floats | same | `1 failed, 7 passed, 352 deselected in 0.51s` | KILLED |
| 14 | CAP-OVERFLOW-AS-EVIDENCE | C:1828-1831 deleted | same | `1 failed, 7 passed, 352 deselected in 0.44s` | KILLED |
| 15 | **ALARM-OUTSIDE-TRY** | C:1632 above the `try:` | `cap or timeout or sigalrm or alarm` | **`16 passed, 344 deselected in 3.91s`** | **SURVIVES — real (F2)** |
| 16 | ZOMBIES-HALF | C:1260 drop `+ owned_present` | `zombies` (`5 passed 44.55s`) | `1 failed, 4 passed, 355 deselected in 44.96s` | KILLED |
| 17 | ZOMBIES-TEARDOWN-UNREAD | C:1346 `if False:` | `zombies` | `1 failed, 4 passed, 355 deselected in 44.25s` | KILLED |
| 18 | TEE-FILE-EXISTS-ONLY | C:416 → bare `.exists()` | `fifo_at_tools or dir_named_manifest` (`2 passed 2.31s`) | `1 failed, 1 passed, 358 deselected in 12.48s` | KILLED |
| 19 | PRE-READ-BARE | C:1711 deleted | same | `1 failed, 1 passed, 358 deselected in 2.52s` | KILLED |
| 20 | **XFAIL-SUBSTRING** | T:2838-2840 → parent's substring form | `real_leg or corpus or negative or xfail` (`52 passed, 9 skipped, 1 xfailed in 86.18s`) | **`52 passed, 9 skipped, 298 deselected, 1 xfailed in 87.61s`** | **SURVIVES — real (F5)** |
| 21 | **CORPUS-UUID-LITERAL** | T:2579 → the container literal | `real_leg or corpus`, `S0_01_VENUE=sandbox`, var UNSET | **`42 passed, 9 skipped, 308 deselected, 1 xfailed in 8.37s`** | **SURVIVES — real (F1)** |
| 22 | DEADCOMMENT-WRONG-FN | C:946 `check_two_users`→`check_initialize_frames` | `dead_branch` (`1 passed 0.13s`) | `1 failed, 359 deselected in 0.26s` | KILLED |
| 23 | DEADCOMMENT-DROPPED | C:1597-1598 deleted | `dead_branch` | `1 failed, 359 deselected in 0.25s` | KILLED |
| 24 | **DEADCOMMENT-WRONG-LINE** | `C:922-925`→`C:9999-9999` | `dead_branch` | **`1 passed, 359 deselected in 0.15s`** | **SURVIVES — real (F11)** |
| 25 | PINNED-OVER-BODY | `pc_post.sh:74` count over `keep` | whole `pc_post_scan` file (`11 passed 0.98s`) | `2 failed, 9 passed in 0.95s` | KILLED |
| 26 | HELPER-FILTER-OFF | `pc_post.sh:70` deleted | same | `2 failed, 9 passed in 0.94s` | KILLED |
| 27 | UNPARSABLE-ROW-SOFT | `pc_post.sh:39` `sys.exit`→`continue` | same | `1 failed, 10 passed in 0.87s` | KILLED |
| 28 | OWNED-PRESENT-BODY | `pc_post.sh:73` count over `keep` | same | `11 passed in 0.88s` | **SURVIVES — EQUIVALENT** (both `keep` filters retain every owned row, so the two counts are equal by construction; the pc_post.sh:68-69 comment says so) |
| 29 | **24-guard COMBINED** (27 `if` lines, re-derived at the PIN by CONTENT match from CK10's parent line list — all 27 mapped 1:1, `pyflakes rc=0`) | see below | CK10's 32-name killer set (baseline **`33 passed, 327 deselected in 216.39s`**) | **`32 failed, 1 passed, 327 deselected in 245.85s (0:04:05)`** | **32/32 KILLED, name for name = CK10's list** |

PIN guard lines for #29: `338 340 356 362 950 958 1282 1286 1307 1315 1330 1335 1337 1339 1342 1417
1421 1423 1435 1440 1451 1458 1473 1481 1539 1599 1601`.
(The 33rd collected id is `test_proc_closure_seed`, pulled in by substring match on
`test_proc_closure`; it is a bystander, not a guard killer, and passes under the mutant. All
**32 named** killers fail.)

**Killers reproduced: 21 single-mutant kills + the 32 of the combined mutant. Survivors: 5** — four
real (F1, F2, F5, F6, F11 → CORPUS-UUID-LITERAL, ALARM-OUTSIDE-TRY, XFAIL-SUBSTRING, F43-SCAN-OFF,
DEADCOMMENT-WRONG-LINE) and one equivalent (OWNED-PRESENT-BODY). Every row ran > 0 tests.

## F16 (SOLID, BLOCKING) — the declared-input contract fails open on the whole unusable `S0_01_VENUE` domain

`T:2600-2601`: `venue = os.environ.get("S0_01_VENUE", ""); if venue in ("sandbox", "pc"):`. Any value
outside that two-element set — including a typo, wrong case, or stray whitespace — takes the `elif
_REAL_LEG_DIR is None: pytest.skip(...)` path and the whole contract evaporates. Executed, with
`S0_01_REAL_LEG_DIR` unset:

| `S0_01_VENUE` | result |
|---|---|
| `sanbox` (typo) | `52 skipped, 308 deselected in 0.15s` — **rc 0, green** |
| `SANDBOX` | `52 skipped, 308 deselected in 0.15s` — **rc 0, green** |
| `sandbox ` (trailing space) | `52 skipped, 308 deselected in 0.16s` — **rc 0, green** |
| `sandbox` (correct) | `1 failed, 51 skipped` — loud, as designed |

A one-character slip in a wrapper script or a CI env block silently removes the entire real-producer
gate and the suite still reports green. This is the fail-open class the anti-hollow-green rule names:
reject the WHOLE unusable domain, not only the known-bad value.

*Minimal fix + exact red test*:
```python
venue = os.environ.get("S0_01_VENUE", "").strip().lower()
assert venue in ("", "ci", "sandbox", "pc"), f"S0_01_VENUE={venue!r} is not a known venue"
if venue in ("sandbox", "pc"):
    ...
```
```python
@pytest.mark.parametrize("v", ["sanbox", "SANDBOX", "sandbox ", "prod", "0"])
def test_ck11_unknown_venue_is_rejected(v, monkeypatch):
    monkeypatch.setenv("S0_01_VENUE", v)
    with pytest.raises(AssertionError, match="not a known venue"):
        test_real_leg_corpus_declared()
```
(`.strip().lower()` also makes `SANDBOX` and `sandbox ` work rather than merely fail loudly — pick
one; failing loudly is the safer default.)

Two smaller observations from the same sweep, both executed:
- **F17 (SOLID, low)** — `T:2605-2606` reports a path that exists but is a regular file as
  `S0_01_REAL_LEG_DIR=<path> does not exist`. Measured with the var pointing at a file. It is an
  exact-reason assertion, so it should say `is not a directory`.
- `S0_01_REAL_LEG_DIR=""` correctly behaves as unset (`1 failed` under venue=sandbox); a relative
  path resolves against the cwd and passes (`1 passed`) — acceptable, but the two wrapper scripts
  should keep passing absolute paths.

## F18 (SOLID, low) — the two env reads in the same hunk resolve at different times

`_REAL_LEG_DIR` is bound at **import** (T:2579); `S0_01_VENUE` is read at **call** time (T:2600). So
`monkeypatch.setenv("S0_01_VENUE", …)` changes the declaration test's behaviour while
`monkeypatch.setenv("S0_01_REAL_LEG_DIR", …)` cannot change anything. `scripts/lint_delta.py` flagged
the AP-1 tell on this file and the lane ruled only the first read ("this IS the single resolution
point"); the second read is unruled. *Fix*: resolve the venue beside `_REAL_LEG_DIR` at module scope,
or state the asymmetry in the docstring.

## GATES I RAN

### pyflakes (PIN bytes)
```
python3 -m pyflakes proofs/S0-01/check_acp_conformance.py tests/test_s0_01_check_acp_conformance.py
pyflakes rc=0
```

### lint_delta (read-only on the shared tree)
```
lint_delta (worktree vs af154ab): 8 .py changed, 0 NEW pyflakes hit(s), 0 removed
anti-pattern screen (TELLS on added lines — verify each, advisory):
  AP-1  tests/test_s0_01_check_acp_conformance.py: env read in edited code …
  AP-1  tests/test_s0_01_frame_tee.py: env read in edited code …
  AP-32 tests/test_s0_01_frame_tee.py: hashing in edited code …
```
The two `frame_tee` tells belong to another lane. The checker-suite AP-1 tell is ruled in F18.

### The real tee through the PIN checker — the gate the lane's GATES section omitted

The brief's gate list ends with *"the real tee under SIGTERM and clean exit through the checker
(`ck10/` has the harness)"*. The lane report's GATES section pastes pyflakes, lint_delta, collection
and two suite runs — **no tee run** — while NOT_DONE says "None." I ran it (CK10's harness re-pointed
at `ck11/pin`), against the CURRENT tee `2f0666c2b2a91a02…` (checkpoint 8s, not CK10's `061dd10c…`):
```
--- SIGTERM: tee rc=70
    status = {… "final": false, "forwarded_a2c": 1, "recorded_a2c": 1, "stdin_reader_done": false,
              "updated_seq": 2, "write_errors": ["terminated: SIGTERM"]}
    check_tee_status(SIGTERM) -> ACCEPTED
--- CLEAN-EXIT: tee rc=0
    status = {… "final": true, "stdin_reader_done": true, "write_errors": [], "exit_code": 0,
              "agent_returncode": 0 …}
    check_tee_status(CLEAN-EXIT) -> ACCEPTED
SUMMARY: {'SIGTERM': 'ACCEPTED', 'CLEAN': 'ACCEPTED'}
```
`pgrep -fc '[f]rame_tee.py'` = **2 before, 2 after** (both other lanes'); I killed nothing I did not
start. **The gate passes** — but "NOT_DONE: None" was wrong: this gate was not run by the lane.

### The checker writes nothing — the F43 scan being test-file-only is correct

`grep` for `write_text|write_bytes|json.dump(|.touch(|os.replace|os.rename|shutil.|open(...,"w"/"a"/"r+")`
over `check_acp_conformance.py`, `check_initialize.py`, `negative_contract.py`, `pins.py` returns **one
docstring mention and nothing else**. The evidence tree is read-only to the checker, so scanning only
the test file is the right scope.

### The handler on every exit path — executed, six paths

`_check_bundle_uncapped` swapped for a synthetic body, `signal.getsignal(SIGALRM)` compared to the
pre-call disposition and `signal.alarm(0)` read for a left-armed alarm:

| exit path | outcome | handler | pending alarm |
|---|---|---|---|
| normal PASS | `returned 'PASS: synthetic'` | RESTORED | 0 |
| `Failure` | `Failure: synthetic failure` | RESTORED | 0 |
| `Deferred` | `Deferred: synthetic deferral` | RESTORED | 0 |
| other exception | `RuntimeError: boom` | RESTORED | 0 |
| **timeout** (`cap=1`, body sleeps 3) | prints `failure_reason: checker timed out after 1s`, `SystemExit: 70` | RESTORED | 0 |
| uncapped (`timeout_s=None`) | `returned 'PASS: synthetic'` | RESTORED | 0 |

No path leaks the handler and none leaves an alarm armed. The one property the try/finally does NOT
cover is a raising `alarm()` itself — F2 (the mutation) and F9 (the `finally` ordering).

### The `_require_file` class at the B3 fix site — six hostile shapes, all named in 0.01 s

| shape planted at `HERE/tools/frame_tee.py` | elapsed | rc | reason |
|---|---|---|---|
| symlink to a real regular file | 0.01s | 1 | `run-1: tools/frame_tee.py is not a regular file` |
| dangling symlink | 0.01s | 1 | `run-1: tools/frame_tee.py absent` |
| symlink to `/dev/null` | 0.01s | 1 | `run-1: tools/frame_tee.py is not a regular file` |
| unix socket | 0.01s | 1 | `run-1: tools/frame_tee.py is not a regular file` |
| absent | 0.01s | 1 | `run-1: tools/frame_tee.py absent` |
| the whole `tools/` dir removed | 0.01s | 1 | `run-1: tools/frame_tee.py absent` |
| FIFO (the committed test) | **0.01s** (`--durations`: `0.01s call`; the 2.16 s is bundle setup) | 1 | `run-1: tools/frame_tee.py is not a regular file` |

`6 passed, 360 deselected in 2.70s`. **The B3 fix holds across the whole non-regular class, not just
the FIFO instance.** The same class at `negative_contract.py:177` does not — F8.

## F19 (SOLID, non-blocking) — "byte-identical corpora on both venues" is enforced by nothing at gate time

The checkpoint message states: *"both venues now prove the same predicate over byte-identical
corpora."* Today that is **true** — I recomputed the sandbox manifest and it equals
`golden.pc.sha256`, and `realleg-sync/pc.sha` == `realleg-sync/sb.sha` byte for byte. But nothing in
any gate checks it:

- `test_real_leg_corpus_declared` verifies **five directory names** and nothing about content
  (`grep -c "golden.pc.sha256"` in the test file = **0**).
- `grep -n "realleg_sync\|golden.pc.sha256"` over `test_summary.sh`, `relaunch-suite.sh`,
  `pc_suite.sh` and both CI workflows finds only **comments** — no gate runs `realleg_sync.sh check`.

So a sandbox corpus that has silently drifted from the PC tree passes the declaration, and the two
venues can report the same summary line over different bytes. The claim is a prose assertion about a
property the artifact does not hold itself to.

*Minimal fix*: extend the declaration test — when the sidecar exists beside the corpus, verify every
sha in it:
```python
manifest = _REAL_LEG_DIR.parent / "golden.pc.sha256"
assert manifest.is_file(), f"{manifest} absent — run scripts/realleg_sync.sh pull"
for line in manifest.read_text().splitlines():
    sha, rel = line.split(None, 1)
    p = _REAL_LEG_DIR / rel.strip().lstrip("./")
    assert _sha256_file(p) == sha, f"corpus drift at {rel.strip()}"
```
and have `pc_suite.sh` publish the same sidecar next to `PC_REAL_LEG_DIR` so the PC venue gets the
identical assertion. *Exact red test*: flip one byte in any corpus file and require the declaration
test to fail with `corpus drift at ./<leg>/<file>`.

## WHAT I REPRODUCED · WHAT I REVIEWED STATICALLY · WHAT I DELIBERATELY SKIPPED

### Reproduced (executed this session, on `git archive 73efb9f` copies under the session scratchpad)

- The PIN's file identity (both shas, both line counts), the parent's, the tee's, and the
  PIN-vs-HEAD diff over all six graded files (empty).
- Collection: 374 = 360 + 3 + 11; `-k "real_leg or corpus"` = 52; `-k corpus` = 1.
- All four corpus configurations, plus four more corpus shapes (5 empty leg dirs; corpus minus one
  leg; one leg gutted; a file instead of a directory) and four `S0_01_VENUE` hostile values.
- B1's three states on scratch corpus copies (`ck11/corp`, `ck11/corp2`) **and** the tail-collision
  attack, **and** the minimal fix (`ck11/fix`) in all four states.
- The F43 scan over 29 planted vectors, and 8 F43 mutants.
- 40 checker read sites enumerated by AST; the 20 directory-named and 20 FIFO-named leg files
  (40 executed cases); 6 hostile shapes at the tee path; the FIFO and directory at
  `tools/acp_probe.py`.
- The cap domain: 17 CLI values through the real CLI, 17 in-process values with `signal.alarm`
  instrumented, and the handler on 6 exit paths.
- 29 mutants (28 single + the 27-line combined), each with its own baseline; `git status --porcelain`
  on the shared tree asserted empty throughout.
- The red-before run: parent checker + PIN tests, `14 failed, 9 passed, 337 deselected in 57.07s`,
  and each of the 9 controls named individually with `-rA`.
- The coordinator's hunk: the 11 pc_post tests, 4 producer mutants, and a deterministic
  counterexample to CK10's `pinned_present == "0"` proposal.
- `realleg_sync.sh check` + an independent recomputation of the corpus manifest.
- pyflakes, `lint_delta.py --base af154ab` and `--base 77546be`, and the real tee (checkpoint-8s
  bytes) through the PIN checker under SIGTERM and clean exit.
- The AF-AP-40 schema probe and its one-line fix.
- 35 `file:line` refs from the lane report checked by `sed -n <N>p` on the PIN bytes.

### Reviewed statically (traced from primary source, not executed)

- That the guards cited at C:922-923, C:894-895 and C:906-907 enforce what the comments claim
  (read; the C:747-749 refs I checked line-by-line and they do **not** — F11).
- `.github/workflows/stage0-ci.yml:21` runs `python -m pytest tests/ -q` with no venue (read, not
  run — I have no CI access).
- The `_split_world` / `pinned_present` mechanism in `pc_post.sh:67-74` (read, then confirmed by
  executing the shim counterexample).

## F20 (SOLID, non-blocking) — F-R10-16's count is taken over the test's OWN list, so trimming the list is invisible

`T:4484 assert len(ran) == len(checks)` closes the `continue` skip the finding named — but `checks`
(T:4465-4482) is a **hand-copied duplicate** of the checker's local dict at C:1114-1132, and nothing
ties it to `cc._EXPECTED_STARTUP_KEYS` (21 keys, module-level and already asserted importable at
T:4488). So the denominator is the test's own list.

Mutant **STARTUP-CHECKS-TRIM** (drop `"memory": cc.PINNED_STARTUP_MEMORY` from the **test's** dict),
`-k startup`:
```
PIN    : 16 passed, 344 deselected in 5.06s
MUTANT : 16 passed, 344 deselected in 5.29s   ← SURVIVES
```
The `memory` pin silently loses its wrong-value test. This is the mirror problem in its purest form:
the test asserts against a copy of the thing under test.

*Minimal fix + exact red test* (verified — green intact, red trimmed):
```python
_elsewhere = {"pubkey", "respond_to"}          # format-only / leg-dependent, tested separately
_uncovered = sorted(cc._EXPECTED_STARTUP_KEYS - set(checks) - _elsewhere)
assert not _uncovered, f"wrong-value dict does not cover the checker key set: {_uncovered}"
```
```
FIX + intact dict : 16 passed, 344 deselected in 5.37s
FIX + TRIM        : 1 failed, 15 passed, 344 deselected in 5.65s   ← KILLED
```

## ITEM 10 — DETERMINISM

### What the 3-file set actually consumes — proved, not assumed

- `ROOT = Path(__file__).resolve().parents[1]` (T:26) and `PC_POST/CHECKER = ROOT/…` — **the graded
  copy**, never the shared tree. `grep -n "/home/user/agent-factory"` over all three test files:
  **no hits**.
- It hashes `P/"tools"/"frame_tee.py"` (T:160) and spawns `proofs/S0-01/tools/pc/pc_post.sh` and the
  checker — all from the copy. `grep -c scripted_backend` over the three files = **0 / 0 / 0**, so the
  backend lane's file cannot affect these runs.
- The copy is a `git archive 73efb9f` extract; nothing in the run writes to it. I recorded the tee's
  sha before and after each gate run.
- `git status --porcelain` on `/home/user/agent-factory` was **empty** at the start of this review and
  at every check during it — no lane held the tree, so there were no uncommitted backend edits to be
  affected by even if the suite had reached them.

### GATE RUN 1 — `bash scripts/test_summary.sh <the 3 files>` from `ck11/pin`, both env vars explicitly UNSET at entry (the defaults resolved the corpus, exactly as the gate of record was taken)

```
load-before: 1.33 1.02 1.00
tee-sha: 2f0666c2b2a91a02
env S0_01_VENUE=<unset> S0_01_REAL_LEG_DIR=<unset>
...
SKIPPED [4] tests/test_s0_01_check_acp_conformance.py:2744: real leg predates scan v2.3 (no enumeration header)
SKIPPED [1] tests/test_s0_01_check_acp_conformance.py:3949: tee-status.json absent in run-1 (corpus predates the tee status)
SKIPPED [1] tests/test_s0_01_check_acp_conformance.py:3949: tee-status.json absent in run-2 (corpus predates the tee status)
SKIPPED [1] tests/test_s0_01_check_acp_conformance.py:3949: tee-status.json absent in cancel (corpus predates the tee status)
SKIPPED [1] tests/test_s0_01_check_acp_conformance.py:3949: tee-status.json absent in shutdown (corpus predates the tee status)
SKIPPED [1] tests/test_s0_01_check_acp_conformance.py:3949: tee-status.json absent in two-users (corpus predates the tee status)
364 passed, 9 skipped, 1 xfailed in 1040.08s (0:17:20)
pytest-exit: 0
pytest-summary: 364 passed, 9 skipped, 1 xfailed in 1040.08s (0:17:20)
load-after: 1.74 1.64 1.48
tee-sha-after: 2f0666c2b2a91a02
```
**Reproduces the gate of record** (`364 passed, 9 skipped, 1 xfailed in 1045.30s (0:17:25)`) — same
counts, same skip reasons, same tee sha before and after. The 9 skips decompose 4 + 5 and the
1 xfailed is `test_real_leg_negative`; both are properties of the declared corpus, and both are now
declared rather than accidental (which is the round's real gain).

### The real-leg selection three times, with the corpus set

```
real-leg run 1: 42 passed, 9 skipped, 308 deselected, 1 xfailed in 7.87s
real-leg run 2: 42 passed, 9 skipped, 308 deselected, 1 xfailed in 7.79s
real-leg run 3: 42 passed, 9 skipped, 308 deselected, 1 xfailed in 7.86s
```
And at node-id granularity: two `-rA` runs, outcome lines sorted and diffed — **identical**, 49 report
lines (42 `PASSED` + 6 aggregated `SKIPPED [n]` lines covering the 9 skips + 1 `XFAIL`).

### Deliberately skipped, with reasons

- **The PC leg.** Not run by me, per the brief's non-negotiables — no bridge action was taken at all.
  The PC gate line `364 passed, 9 skipped, 1 xfailed in 134.10s (0:02:14)` (run
  `20260907T200337Z-77546be`) is **carried, not measured**. Cross-check available to me: the sandbox
  collection is 374 and the sandbox result is the same 364/9/1, and the PC corpus manifest is
  byte-identical to the sandbox one — consistent, but not reproduced. **No finding below depends on
  it.**
- **The 27-line combined mutant over the FULL 3-file suite.** CK10 ran that shape
  (`36 failed, 309 passed, 9 skipped, 1 xfailed in 1063.87s`). I ran the targeted 32-name killer set
  instead (`245.85s`), which is what "the 24 guards still die" actually asks; a full-suite run adds
  ~18 min and no additional guard evidence.
- **XFAIL-SUBSTRING over the whole file.** I started a broad run, then killed it (PID-targeted, my own
  process, rc 143) because the mutation touches only `test_real_leg_negative`, which was inside the
  selection I did run — no wider run can change that verdict.
- **CI execution.** `.github/workflows/stage0-ci.yml` was read, not run; I have no CI access. F13's
  claim about CI rests on reading line 21 plus the measured local behaviour of the same command.
- **The CLI-subprocess boundary for F8.** Attempted and reported as not reproduced (see the honesty
  note in F8) — the synthetic bundle cannot pass the golden pin in a subprocess.

### Hygiene at close

`/home/user/agent-factory` was **never** edited, staged, committed, stashed, checked out or reset by
me; the only git commands I ran there were `cat-file`, `rev-parse`, `log`, `show`, `status`, `diff`,
`merge-base`, `ls-files`. Every mutation ran on a scratchpad copy.

The shared tree **moved during this review**: HEAD went `24e0961` → `934dec1` → `e86b1b8` (two
transcript scrubs, an INCIDENT-LOG row for VERIFY-B5g F-B5g-9, the B5h/D5k briefs, and further lane
commits), and mid-review it carried other lanes' uncommitted work (`proofs/S0-01/tools/frame_tee.py`,
`proofs/S0-01/tools/scripted_backend.py`, `tasks/briefs/s0-01-d5j-support/cost_probe.py`,
`tests/red/test_s0_01_backend_credential_screen.py`, `tests/test_s0_01_frame_tee.py`,
`tests/test_s0_01_scripted_backend.py`). **None of it is mine and none of it is a graded file** —
`git diff --stat 73efb9f HEAD` over all six graded paths (both scope files,
`test_s0_01_pc_post_scan.py`, `realleg_sync.sh`, `pc_suite.sh`, `test_summary.sh`) plus
`negative_contract.py` is **empty at `24e0961`, at `934dec1` and at the final `e86b1b8`**, so everything
I measured is still current at HEAD. `git status --porcelain` was empty again at close.

My graded copies re-verified at close: `de13655a…`, `da1ce466…`, `74dc0621…` (pc_post_scan) and
`b9eb56dd…` (`tools/acp_probe.py`, restored after the F8 CLI attempt) — all equal to
`git show 73efb9f:<path> | sha256sum`.

Processes: `ps -eo cmd | grep '[f]rame_tee'` and `grep '[a]cp_probe'` both empty at close. I killed
exactly one process, my own broad XFAIL-SUBSTRING run, by PID. No `pkill`. No outward action, no
network beyond localhost, no bridge call.

---

## FINDINGS — all of them, no severity filtering

| # | conf | blocking? | one line | file:line |
|---|---|---|---|---|
| F1 | SOLID | **YES** | CORPUS-UUID-LITERAL survives under the brief's own killer configuration; nothing pins `_REAL_LEG_DIR` to the environment, so the mutant's verdict depends on a directory outside the repo | T:2579 |
| F2 | SOLID | no (but "N/A" is wrong) | ALARM-OUTSIDE-TRY is killable and unkilled; the committed handler test never enters `_check_with_timeout` | C:1632, T:4625 |
| F3 | SOLID | **YES** | `strict=True` is structurally dead — the marker is added after the failure, so a **repaired capture passes silently** (`1 passed`), contradicting T:2822-2824 and the pinned design | T:2819-2846 |
| F4 | SOLID | **YES** | the xfail anchor still fails open on a tail collision fed by corpus-controlled `probe_error` — a broken capture is accepted as the known-stale xfail | T:2838-2840, `negative_contract.py:173` |
| F5 | SOLID | **YES** | B1 has **no committed test** (T:4525 is a comment); mutant XFAIL-SUBSTRING survives — AF-AP-36 | T:4525-4526 |
| F6 | SOLID | no | the real-source arm of the F43 test has no mutation coverage: `violations = []` leaves it green, contradicting T:3407-3408 | T:3411 |
| F7 | SOLID | no (low) | `gzip.open(p,"wb")` and `os.truncate(p,0)` clobber through the hardlink, are missed, and are not in the documented limits | T:3333-3336 |
| F8 | SOLID | **YES** | the read CLASS is still open — a FIFO at `tools/acp_probe.py` hangs to the cap (rc 70) and a directory there gives the generic `IsADirectoryError`; AF-AP-30 | `negative_contract.py:177-184` |
| F9 | SOLID | no (low) | the `finally` calls `alarm(0)` before restoring the handler, so a raising `alarm()` there still leaks — the C:1630-1631 claim overstates | C:1635-1636 |
| F10 | SOLID | no (low) | the module docstring NOTE describes only the non-positive half of the refused domain | C:2-3 |
| F11 | SOLID | no | F-R10-10 is 4/6 pinned, and the two pinned `C:747-749` citations point at three assignments — the real guard is C:742-743; DEADCOMMENT-WRONG-LINE survives | C:1568, C:1597, T:4660-4677 |
| F12 | SOLID | **YES** | B6 not closed — **17 of 35** `file:line` refs wrong (two are parent-tree numbers), two red-before rows still labelled "genuine-red" where the test is a CONTROL, the 16-value CLI probe claimed but not pasted, NOT_DONE "None" while a required gate was not run | `A5i-report.md` |
| F13 | SOLID | no (design) | with `S0_01_VENUE` unset — the default for every invocation that is not one of the three wrapper scripts, CI included — the checker suite is `52 skipped`, rc 0 | T:2600, `stage0-ci.yml:21` |
| F14 | SOLID | no (low) | one dead `tee.write_text("placeholder")` is the sole reason `_EXEMPT_FNS` grew a third entry | T:4542 |
| F15 | SOLID | **YES** | AF-AP-40: deleting `fixtures/acp-schema-v1.json` makes the checker **PASS** with a byte-identical PASS line — the only JSON-Schema validation is presence-gated | C:1704 |
| F16 | SOLID | **YES** | a typo / wrong case / trailing space in `S0_01_VENUE` silently disables the whole declared-input contract → `52 skipped`, rc 0 | T:2600-2601 |
| F17 | SOLID | no (low) | a corpus path that exists but is a file is reported as "does not exist" | T:2605-2606 |
| F18 | SOLID | no (low) | `_REAL_LEG_DIR` resolves at import, `S0_01_VENUE` at call time — the lane ruled only the first AP-1 tell | T:2579 vs T:2600 |
| F19 | SOLID | no | "byte-identical corpora on both venues" is asserted in prose and enforced by nothing at gate time | `A5i` commit msg, T:2597 |
| F20 | SOLID | no | F-R10-16's count is taken over the test's own hand-copied dict; STARTUP-CHECKS-TRIM survives | T:4465-4484 |

**Nothing is UNSURE.** Every finding above was executed, most of them with the fix verified as well.

## WHAT THIS ROUND GOT RIGHT — on the record before the verdict

This is a real advance and most of the brief landed:

- **The cap's domain is completely closed.** 17 CLI values and 17 in-process values, every out-of-domain
  one refused with the exact message, nothing installed, no handler leak on any of six exit paths.
  F-R10-03/04/05 are gone.
- **B2 is closed at the class**: seven pattern-family mutants die, including two families this round
  added; the documented limits are honest for all six things they name.
- **B3's two instances are closed and hold across the whole non-regular class** at the tee path
  (symlink, dangling symlink, `/dev/null`, socket, absent, missing dir — all named in 0.01 s), and all
  20 directory-named and 20 FIFO-named leg files give exact reasons.
- **F-R10-11 is closed on both scans**; **B4** genuinely has one literal; **B5**'s pin is consumed.
- **The 24 A5e guards still all die** — 32/32, name for name, on the re-derived combined mutant.
- **The corpus really is a declared input on the two gate venues**, restorable in one command, with a
  PC twin I verified byte-identical; the sandbox and PC runs now execute the same 51 tests.
- **The coordinator's own hunk is sound**, and its rejection of my predecessor's `pinned_present == 0`
  proposal is correct on stronger grounds than the one it gave — I built the deterministic
  counterexample.
- **The suite is deterministic** and reproduces the gate of record.

### Env-as-config-channel discipline — clean on the production side

`grep -n "os.environ\|getenv"` over `check_acp_conformance.py`, `negative_contract.py`,
`check_initialize.py` and `pins.py`: **no hits**. The checker takes no configuration from the
environment; the two new variables are test-side only (T:2579, T:2600), and `_run` (T:496) hands the
subprocess `os.environ.copy()` which the checker ignores. The CLAUDE.md "`os.environ` is NOT a config
channel" rule holds where it matters.

### GATE RUN 2 — same command, same copy, both env vars UNSET at entry

```
load-before: 1.68 1.63 1.48
tee-sha: 2f0666c2b2a91a02
env S0_01_VENUE=<unset> S0_01_REAL_LEG_DIR=<unset>
...
SKIPPED [4] tests/test_s0_01_check_acp_conformance.py:2744: real leg predates scan v2.3 (no enumeration header)
SKIPPED [1] tests/test_s0_01_check_acp_conformance.py:3949: tee-status.json absent in run-1 (corpus predates the tee status)
SKIPPED [1] tests/test_s0_01_check_acp_conformance.py:3949: tee-status.json absent in run-2 (corpus predates the tee status)
SKIPPED [1] tests/test_s0_01_check_acp_conformance.py:3949: tee-status.json absent in cancel (corpus predates the tee status)
SKIPPED [1] tests/test_s0_01_check_acp_conformance.py:3949: tee-status.json absent in shutdown (corpus predates the tee status)
SKIPPED [1] tests/test_s0_01_check_acp_conformance.py:3949: tee-status.json absent in two-users (corpus predates the tee status)
364 passed, 9 skipped, 1 xfailed in 1018.82s (0:16:58)
pytest-exit: 0
pytest-summary: 364 passed, 9 skipped, 1 xfailed in 1018.82s (0:16:58)
load-after: 2.57 1.99 1.62
tee-sha-after: 2f0666c2b2a91a02
```

### Determinism verdict

```
run 1 : pytest-exit: 0 · 364 passed, 9 skipped, 1 xfailed in 1040.08s (0:17:20)
run 2 : pytest-exit: 0 · 364 passed, 9 skipped, 1 xfailed in 1018.82s (0:16:58)
record: pytest-exit: 0 · 364 passed, 9 skipped, 1 xfailed in 1045.30s (0:17:25)
```
**Identical outcomes, identical skip reasons, identical tee sha before and after each run, both runs
with the two variables explicitly unset so `test_summary.sh`'s new defaults did the resolving — which
is exactly how the gate of record was taken.** Wall clock differs by 21 s across runs (load 1.3→2.6),
which is the expected variance and touches no assertion: nothing timed is near its bound (the FIFO
test's own call is 0.01 s against a 5 s assertion). **The suite is deterministic and reproduces the
gate of record.** Also relevant to CK10's F-R10-22: I ran two full suites plus ~30 mutant runs on a
contended box and saw zero load-induced failures, so the 60 s helper cap is not biting today.

---

## VERDICT

**NOT-READY.**

This round moved the artifact a long way — the cap's whole domain is closed on both entry paths, the
F43 self-test kills every pattern family, the tee path is hardened across the entire non-regular
class, the zombies invariant is complete on both scans, the 24 A5e guards all still die, the corpus is
a genuinely declared input on both gate venues over byte-identical trees, and the suite is
deterministic. Eight things nonetheless fail the round's own standard — *claims that hold, guards that
are pinned* — and every one of them was executed here, with the fix verified in six of the eight.

### BLOCKING SET

| # | id | one-line statement | fix size |
|---|---|---|---|
| B1' | **F3** | `strict=True` is structurally dead (the marker goes on *after* the failure, so XPASS is unreachable): a **repaired capture passes silently** — `1 passed` — while T:2822-2824 and the pinned design both say it must FAIL. F-R10-13's exact defect class, in the round raised to close it. | 3 lines + drop the inert `strict=`/`raises=` |
| B1'' | **F4** | the xfail anchor still fails open: `probe_error`, a value read out of the evidence under test, flows into the reason's last segment verbatim, so a **broken capture is accepted as the known-stale xfail** (`1 xfailed`). | pin the whole reason; 5 lines |
| B1''' | **F5** | B1 has **no committed test** — T:4525 is a comment — and mutant XFAIL-SUBSTRING survives (`52 passed, 9 skipped, 1 xfailed` identical to the PIN). AF-AP-36. | 1 test (given F4's fix, 3 lines) |
| B3' | **F8** | the read CLASS is still open: a FIFO at `proofs/S0-01/tools/acp_probe.py` hangs the checker to its cap (`rc 70`), a directory there gives `malformed evidence: IsADirectoryError` — the CK9-F2 and R9-CK-F27 symptoms at the sibling file of the one B3 just fixed. AF-AP-30, third round running. | 2 lines + 1 test (out of A5i's scope — a coordinator call) |
| B6' | **F12** | B6 is not closed and is measurably worse than CK10's: **17 of 35** `file:line` refs are wrong (two are *parent-tree* numbers, four point at code where the report says comment, one points into a different test), two red-before rows are still labelled "genuine-red" where the test is green on the parent, the 16-value CLI probe is claimed without evidence, and NOT_DONE says "None" while a required gate was never run. | report edit only |
| — | **F1** | CORPUS-UUID-LITERAL **survives** the exact configuration the brief named as its killer, because its verdict depends on a directory outside the repo. Nothing pins `_REAL_LEG_DIR` to the environment. | 1 test (verified: green on the PIN in both configurations, red on the mutant in both) |
| — | **F16** | the declared-input contract fails open on the whole unusable `S0_01_VENUE` domain: `sanbox`, `SANDBOX`, `sandbox ` each give `52 skipped`, rc 0 — a one-character slip removes the entire real-producer gate silently. | 2 lines + 1 parametrised test |
| — | **F15** | AF-AP-40 in the checker: deleting `fixtures/acp-schema-v1.json` makes the checker **PASS** with a **byte-identical PASS line**. The only JSON-Schema validation in the proof is presence-gated. Inherited (checkpoint 5) but added *after* AF-AP-40 was registered (checkpoint 4). | 1 line + 1 test (both verified) |

### NON-BLOCKING, all real, all reproduced

F2 (ALARM-OUTSIDE-TRY is killable and unkilled — the lane's "N/A" is wrong; killer verified both
ways) · F6 (`violations = []` leaves the F43 real-source arm green, contradicting T:3407-3408) ·
F7 (`gzip.open(p,"wb")` and `os.truncate` clobber through the hardlink, missed and undocumented) ·
F9 (the `finally` restores after `alarm(0)`, so the C:1630-1631 claim overstates) · F10 (the docstring
NOTE describes a strict subset of the refused domain) · F11 (F-R10-10 is 4/6 pinned and the two pinned
`C:747-749` citations point at three assignments; DEADCOMMENT-WRONG-LINE survives) · F13 (venue unset
— the default everywhere except three scripts, CI included — is `52 skipped`, rc 0) · F14 (a dead
`write_text` is the sole reason `_EXEMPT_FNS` grew) · F17 (a corpus path that is a file is reported as
"does not exist") · F18 (the two env reads resolve at different times) · F19 ("byte-identical corpora"
is prose, enforced by nothing at gate time) · F20 (F-R10-16's count is over the test's own hand-copied
dict; STARTUP-CHECKS-TRIM survives).

### THE COORDINATOR'S THREE QUESTIONS, ANSWERED

**(a) Does `1 FAILED (incomplete), 51 skipped` meet the contract?** **Yes on substance, no on wording
— and the wording is what should change, not the build.** Every incomplete corpus shape I built goes
RED (empty dir → the declaration test; five empty leg dirs → 41 producer failures; a gutted leg → 10;
a missing leg → the declaration test). There is no green-by-skip. The per-leg skips are correct: a
test cannot assert over a leg that is not there. **No red test needed.** The two residuals worth
recording are F13 (the venue switch, not the corpus, is what can silently go quiet) and F19 (nothing
checks corpus *content*).

**(b) CORPUS-UUID-LITERAL under `S0_01_VENUE=sandbox` with the var unset:** **it SURVIVES** —
`42 passed, 9 skipped, 1 xfailed`, and the declaration test alone `1 passed`. The lane's claim is
correct and its cause is exactly what it said: the old scratchpad corpus still exists here and I
verified it byte-identical to the declared one. But that makes the row a **live survivor, not a
conditional pass**: a mutant whose verdict depends on a directory outside the repository is not a
mutation test. The container-independent killer is in F1 and I verified it red on the mutant and green
on the PIN in both configurations.

**(c) Is the handler-leak test vacuous?** **Not vacuous, but mislabelled — and the "N/A" is wrong.**
It is genuinely red on the parent, so it is a real red-before *for the domain gate*: it proves "a
rejected cap installs no handler". It never enters `_check_with_timeout`, so it proves nothing about
the alarm's position — measured: ALARM-OUTSIDE-TRY passes it and the whole cap family
(`16 passed, 344 deselected`). The property IS testable with one monkeypatch; my killer is red on the
mutant (`LEAKED: before=0, after=<_raise_timeout>`) and green on the PIN. Rename the existing test to
what it proves and add the killer (F2). While there: the `finally` restores the handler *after*
`alarm(0)`, so the comment's claim is broader than the code (F9).

### WHAT THIS VERDICT DEPENDS ON THAT I DID NOT REPRODUCE

**Nothing.** Every blocking item was executed here on `git archive 73efb9f` copies, most of them with
the proposed fix verified as well. The one carried number is the PC gate line
(`364 passed, 9 skipped, 1 xfailed in 134.10s`) — no bridge action was taken, per the brief — and **no
finding above depends on it**. The one repro I could not drive to the outermost process boundary is
F8's FIFO (stated inside the finding); it is reproduced at `check_bundle`, the function `main()` calls.
