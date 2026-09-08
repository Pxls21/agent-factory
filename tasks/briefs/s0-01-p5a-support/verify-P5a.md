# VERIFY-P5a — adversarial grade of lane P5a (S0-01 PC capture tools, round 1)

PIN `582ada4ca1b50deb4c8cc8e15c7f0980831653f4` (detached; parent `6a41bd2`). Every file:line below is
`sed -n` on `git archive 582ada4c` unless it says SHARED TREE (a live lane's uncommitted bytes) or HEAD.
Branch head while grading: `42d92b6`. Clock: `2026-09-08T03:0x`–`03:2xZ` (run stamps inline).

## VERDICT: NOT-READY

Blocking set: **F1, F2, F3, F4**. (F1 is the red lane C1 and the coordinator hit from the
shared tree; I found and reproduced it independently before that message — see the dedicated section at
the end for the fixture-vs-gate ruling the coordinator asked for.) F1 and F2 are regressions the lane's report does not name and that
lane A5k's checker adoption does NOT fix. F3 is a hollow green inside the lane's own headline gate
(mutant survived). F4 is the #6 fix not actually closing its class, reproduced with a real process.
The verdict does not depend on anything I failed to reproduce: F1-F4 are all reproduced runs.

Everything else — the v2.4 two-counter header, the six `pc_launch` fail-loud helpers, the exit-code
propagation, the `collect_leg` agreement tests, the mutant table, the report's file identity — is real,
and the lane's 16 mutants I spot-checked are genuinely killed. This is a good lane with four holes.

---

## GATES I RAN (pasted)

```
sandbox, PIN copy, the lane's two files:
  55 passed in 1.50s                                   (rc 0)

PC gate (the brief's carve-out; clean detached worktree of pushed 6a41bd2 + the PIN's nine files):
  RUN_ID 20260908T030130Z-6a41bd2   base 6a41bd2c6c3613cc00e0810dcb578bfc7d85bb80 + patch 78308B
  pytest-exit: 0
  pytest-summary: 55 passed in 1.70s
  -> AGREES with the lane's sandbox line. Item 10 satisfied.

ADJACENT CONSUMERS (the gate the lane did NOT run) — same six files, PIN vs parent:
  PIN     6a41bd2+P5a : 3 failed, 599 passed in 358.82s   (rc 1)
  PARENT  6a41bd2     : 602 passed in 337.31s             (rc 0)
  files: test_s0_01_frame_tee.py test_s0_01_acp_probe.py test_s0_01_negative_contract.py
         test_s0_01_check_initialize.py test_s0_01_audit_cp5_controls.py test_s0_01_scripted_backend.py

report_lint on the LANE's report, the brief's exact invocation, at the PIN rev:
  report_lint: 40 refs — OK 22, NEAR 2, MISS 0, UNCHECKABLE 8, UNRESOLVED 8 (at 582ada4c)
  -> MISS 0. Gate met.

ap_screen production (proofs/S0-01/tools/pc, build_capture_record.py, pins.py):
  AP_SCREEN over 3 path(s): 21 hits over 4 files      (identical to the lane's line)
```

FILE IDENTITY — all seven sha256[:16] match the lane's report table exactly:
`974b86f2445d239f` pins.py · `682cf587fa95e1d9` pc_launch.py · `8db8caeaf5e56f28` pc_post.sh ·
`8fd321169d9fe769` pc_negative.py · `aa250e3da7d42536` build_capture_record.py ·
`acc7d226357c3278` test_s0_01_pc_post_scan.py · `468107ff49d1a1a2` test_s0_01_pc_tools.py.

---

## FINDINGS (all of them, no severity filter)

### F1 — BLOCKING. The PIN turns a green adjacent test RED, and the report does not name it. SOLID.
**Where:** `proofs/S0-01/tools/build_capture_record.py:63-69` (the new required-list gate) breaks
`tests/test_s0_01_scripted_backend.py:894 test_build_capture_record_roundtrip_check` — a file OUTSIDE the
lane's scope and outside the four files the lane re-ran.
**Expected** (lane's NOT_DONE 2): exactly one adjacent file goes red — `test_s0_01_audit_cp5_controls.py`,
2 of 3, "a sequencing dependency" that lands with A5k.
**Observed:** three tests go red. The third is unaccounted for and A5k cannot fix it: the checker's
adoption of the v2.4 header has nothing to do with `build_capture_record.py`'s required list.
**Failing input:** the synthetic 7-file leg that test builds.
```
PIN:    AssertionError: build failed: test-leg: missing required leg files: argv.txt,
        backend-healthz-after.json, ... tee-status.json, upstream-records   (21 names)  -> rc 1
PARENT: 1 passed in 0.37s
```
**Minimal fix (A5k or a P5a round 2):** rebuild that test's leg through the same helper the lane already
wrote — `tests/test_s0_01_pc_tools.py:285 _synthetic_leg` — or make the strictness explicit
(`--require-complete`, default on for the pipeline, off for the round-trip unit test). Do NOT weaken the
gate; the gate is right, the caller is stale.
**Exact red test:** `pytest tests/test_s0_01_scripted_backend.py::test_build_capture_record_roundtrip_check`
— green at `6a41bd2`, red at the PIN.

### F2 — BLOCKING. `build_capture_record.py` can no longer process ANY real corpus leg. SOLID.
**Where:** `proofs/S0-01/tools/build_capture_record.py:63-64` requires every `required` name including
`tee-status.json` (`pins.py:223`), and **never consults `pins.PINNED_LEG_FILES_SINCE` (`pins.py:231`)**.
The corpus-version rule the lane built lives only in the TEST (`tests/test_s0_01_pc_tools.py:81-87
_required_for`), not in the tool.
**Expected:** the ONE list's own version rule applies wherever the list is consumed.
**Observed** (run on a copy of `/root/s0-01-realleg/golden/run-1`, corpus intact, 142 files):
```
PIN bytes:    run-1: missing required leg files: tee-status.json    rc=1
PARENT bytes: run-1: 9 raw files, 11 timeline entries               rc=0
```
Every one of the four positive corpus legs is v2.2 and fails the same way. The report's self-attack A2
concedes the corpus is v2.2, but frames it as "direction (b) grades 25 of 26" — it does not notice that
the TOOL, unlike the test, hard-fails on it.
**Failing input:** any v2.2 leg, i.e. every leg that exists today.
**Minimal fix:** give the tool the same rule — resolve `required` through a shared helper in `pins.py`
(`pins.required_files(version)`) and have `build_capture_record.py`, the test, and A5k's checker all call
it; detect the version from `process-scan-after.txt`'s header, exactly as both mirrors already do.
**Exact red test:** a new `test_build_capture_record_accepts_a_v2_2_corpus_leg` that runs the tool over
`S0_01_REAL_LEG_DIR/run-1` (copied to tmp_path) and asserts rc 0.

### F3 — BLOCKING. The producer-subset gate is blind to the exact idiom the lane's own new helpers use. MUTANT SURVIVED. SOLID.
**Where:** `tests/test_s0_01_pc_tools.py:105` — `_PY_JOIN` anchors on `os.path.join(FD|framedir, "…")`
only. The six helpers the lane extracted all take a lowercase `fd`:
`pc_launch.py:88`, `:89` (`manifest-{phase}.done/.log`) and `pc_launch.py:118`
(`runtime-identity.json`, written back at `pc_launch.py:318`).
**Expected** (report DONE 1, and the mapping comment at `pins.py:175-177`): "a producer that starts
writing a new framedir name must add it here … the test parses the producers and fails on a name that is
not in this mapping".
**Observed:** the refactor SHRANK the gate. PIN's parser over the parent's `pc_launch.py` sees 18 names;
over the PIN's, 16. Lost: `manifest-pre.done`, `runtime-identity.json`.
**Mutant V1 (PRODUCER-UNLISTED, in the lane's own new code):** insert one line AFTER `pc_launch.py:118`
`open(os.path.join(fd, "leak-report-v1.json"), "w").write("{}")` →
```
tests/test_s0_01_pc_tools.py :  42 passed in 0.50s     (rc 0 — SURVIVED)
```
The lane's own mutant #2 (the same class, in `pc_post.sh`, which uses `$FD/`) IS killed — so the table
proves the gate for the files that happen to use a recognised idiom, and not for the file the lane rewrote.
**Minimal fix:** `_PY_JOIN = re.compile(r"""os\.path\.join\(\s*(?:FD|fd|framedir)\s*,\s*['"]([^'"\n]+)['"]""")`
(one token). Then `test_every_producer_write_lands_in_the_pinned_mapping[pc_launch.py]` must be re-run —
it stays green on the real bytes (both new names are already in the mapping) and kills V1.
**Exact red test:** apply V1 above; with the fix the parametrised producer test fails with
`proofs/S0-01/tools/pc/pc_launch.py: writes names outside pins.PINNED_LEG_FILES: ['leak-report-v1.json']`.

### F4 — BLOCKING. `is_pinned`'s "ENTRY POINT" is argv[1] equality, so any command whose FIRST OPERAND is a pinned script counts as pinned. Reproduced with a real live process. SOLID.
**Where:** `proofs/S0-01/tools/pc/pc_post.sh:47`
`return argv[:1] == [PINNED_BINARY] or (len(argv) > 1 and argv[1] in PINNED_SCRIPTS)`.
**Expected** (docstring `pc_post.sh:37-45`, report DONE 3 and A3): "a row is pinned by its ENTRY POINT,
never by a substring"; "exact token equality against an absolute pinned path kills the substring defect
completely"; the three listed shapes are all `python3 <script>`.
**Observed:** argv[0] is never examined for the script arm. A REAL process, no shim, real producer:
```
$ /usr/bin/cat <PINNED_TEE_PATH> -            # blocks on stdin; argv[1] is the pinned tee
# process-scan v2.4 mode=after rows=2 ... pinned_present=1 ... table_rows=133
7085 7084 0 /usr/bin/cat /home/rocco/agent-factory/proofs/S0-01/tools/frame_tee.py -
```
The bystander is counted pinned AND written into the leg's evidence body. Through the real producer over
a synthetic `ps` table, `cat <tee>`, `vim <tee>` and `sha256sum <agent>` together move
`pinned_present` from 1 to 4 and add three rows to the body.
**Does an oracle catch it?** No oracle contradicts the header — the checker's F17
(`check_acp_conformance.py:1249-1253`) recomputes by substring and AGREES; after A5k adopts the same
entry-point rule it still agrees. `pc_post.sh:120`'s `readlink` only covers the one pidfile pid;
`runtime-identity.json` only covers our own three pids. The failure is **fail-closed but wrong-reasoned**:
on a shutdown leg the extra row hits `check_acp_conformance.py:1263-1265` → `process 7085 … survived
shutdown`; on a non-shutdown leg it hits A20e at `:1325-1330` → `not in buzz-acp descendant tree`. So an
owner opening `frame_tee.py` in an editor during a capture fails the leg for a bystander. Given the PC is
the owner's live box, that is a real robustness defect, not a theoretical one.
**Failing input:** `/usr/bin/cat <PINNED_TEE_PATH> -` (or `less`, `vim`, `md5sum`, `cp`, `grep`).
**Minimal fix** (`pc_post.sh:46-47`):
```python
argv = cmd.split()
if argv[:1] == [PINNED_BINARY]:
    return True
return (len(argv) > 1 and argv[1] in PINNED_SCRIPTS
        and os.path.basename(argv[0]).startswith("python"))
```
(`import os` at the top of the heredoc.) This still matches all three real corpus rows — verified against
`/root/s0-01-realleg/golden/run-1/process-scan-after.txt`, whose tee row is `python3 <tee>` and whose
agent row is `<venv>/python3 <agent>`.
**Exact red test:** add to the shim in `tests/test_s0_01_pc_post_scan.py:344
test_pinned_present_is_exact_over_a_synthetic_table` a row
`echo '5007 1 7 S /usr/bin/cat {tee}'` and assert `5007 not in {row[0] for row in rows}` and
`m.group(7) == "3"` (unchanged). Red today, green after the fix.

### F5 — `is_pinned` misses a pinned BINARY invoked by any other path (false negative). SOLID, reviewed + probed.
`pc_post.sh:47`'s binary arm is `argv[0] == PINNED_BUZZ_ACP_EXE_REALPATH`. Through the real producer:
a row `/home/rocco/s0-01-pinned/buzz/bin/buzz-acp --relay-url ws://x` (e.g. a symlink or bind path) is
**not** counted pinned and is dropped from the body entirely, while the realpath row is kept. A leaked
foreign buzz-acp started that way is invisible to the evidence and to both oracles.
Bounded in practice: `pc_launch.py:62-71 alive_pinned_buzz` reads `/proc/<pid>/exe` (which resolves the
realpath whatever the invocation) and refuses to launch over a live pinned buzz-acp — so the escape needs
the pidfile to be gone. Report as a known limit, or resolve argv[0] via `/proc/<pid>/exe` for the binary
arm only (where it works — the lane's own D1 argument).
**Minimal fix / red test:** shim row `6004 1 7 S <alt-path>/buzz-acp --relay-url ws://x`; decide and pin.

### F6 — the #27 defect survives in a narrower form: an EMPTY required file is still "a record of nothing, green". SOLID.
**Where:** `build_capture_record.py:64` tests `is_file()` only; `:75` then reads the file.
**Failing input:** a complete leg with `timeline.jsonl` truncated to 0 bytes (a tee that died before its
first frame, or a truncated collect).
```
run-1: 9 raw files, 0 timeline entries      rc=0
capture.json -> "timeline": {"entries": 0, "c2a": 0, "a2c": 0, "sessions": [], "terminals": [], ...}
```
The sweep's own words for the defect were "a record of nothing, green". Presence is now proven; content
is not. **Minimal fix:** after the required gate, `if (d / "timeline.jsonl").stat().st_size == 0: print(...);
return 1`. **Exact red test:** `test_build_capture_record_fails_on_an_empty_timeline` — truncate
`timeline.jsonl` in `_synthetic_leg`, assert rc 1 naming it.

### F7 — `build_capture_record.py:128` is an UNDOMINATED presence gate, and `ap_screen.py` cannot see it. SOLID.
The report classifies all AF-AP-40 hits as "now DOMINATED. Every one of those `.exists()` / `.is_dir()`
names is `required` in the mapping". I re-derived domination BY RUNNING — dropping each of the 13 gated
names in turn gives `rc 1` naming exactly that name, so the claim holds for the ten hits the screen found.
It does not hold for the eleventh gate the screen misses:
```python
build_capture_record.py:128:   receipt = json.loads(rp.read_text()) if rp.exists() else {}
```
`mentions/<tag>.receipt.json` is not in `PINNED_LEG_FILES` at all (only the `mentions` DIR is), so nothing
dominates it. Run: a leg whose `mentions/tag1.event.json` exists with no receipt →
`rc=0`, `"mentions": {"tag1": {"accepted": None, ...}}` — a silent "unknown" recorded as evidence.
Bounded: the checker never trusts `capture.json` (`build_capture_record.py:2`). **Two fixes, both wanted:**
(a) make it loud — `accepted: "receipt-absent"` or a non-zero exit; (b) extend the AP screen's AF-AP-40
signature to the ternary form `if X.exists() else`, per the registry's own "every new mechanical signature
extends AP_SCREEN in the same increment" rule.

### F8 — `pc_negative.py` does not normalise a SIGNAL death, and no test can see a regression there. MUTANT SURVIVED. SOLID.
`pc_negative.py:34,42,46`: `subprocess.run(...).returncode` is `-9` for a SIGKILLed probe; `main()` returns
`-9`; `raise SystemExit(-9)` gives the wrapper OS status **247**, not 137. Run:
```
probe rc -9 ; main() returned: -9 ; OS exit status of the wrapper: 247
```
Fail-loud holds (non-zero, `run_leg.sh` `set -e` stops). But the class is untested:
`tests/test_s0_01_pc_tools.py:506` parametrises `rc ∈ [3, 1, 0]` only.
**Mutant V7 (NEG-RC-CLAMPED):** `return rc` → `return max(rc, 0)` →
```
tests/ : 55 passed in 1.39s   (rc 0 — SURVIVED)
```
That mutant makes a SIGKILLed probe report SUCCESS, and the suite cannot tell.
**Minimal fix:** `return rc if rc >= 0 else 128 - rc` (128+signal), and extend the parametrisation with a
probe that `os.kill(os.getpid(), SIGKILL)`s, asserting `main() == 137`.
**Exact red test:** `test_pc_negative_propagates_a_signal_death` with that stub probe.

### F9 — the `is_file()` / `is_dir()` strictness is unpinned. MUTANT SURVIVED. SOLID.
I verified the good behaviour by running: a DIRECTORY named `owned-pids.json` → `rc 1 missing required
leg files: owned-pids.json`; a FIFO named `env.json` → `rc 1` (no hang, timeout 20 s not reached). That is
the right answer for the whole non-regular-file class.
**Mutant V8 (EXISTS-NOT-ISFILE):** `not (d / n).is_file()` → `not (d / n).exists()` (and the dir arm) →
```
tests/ : 55 passed in 1.36s   (rc 0 — SURVIVED)
```
because `test_build_capture_record_takes_its_required_list_from_pins` only ever *removes* names.
**Minimal fix:** add a `shape` parametrisation to that test — `dir`, `fifo` — asserting rc 1 naming the name.

### F10 — `transient` is a status the lane's own tar test contradicts, and the window is live. SOLID.
`pins.py:167` defines `transient` = "an intermediate the producer replaces in place before the leg closes;
never collected", for `manifest-pre.txt` / `manifest-post.txt` (`pins.py:211`, `:217`).
Nothing enforces it. `collect_leg.sh:15` excludes `buzzacp.raw.log`, `manifest-*.txt.gz`, `manifest-*.log`,
`*.launch.log` — **none of which matches `manifest-post.txt`**. The lane's own end-to-end tar test has to
add the transient names back to the expected set to pass:
`tests/test_s0_01_pc_tools.py:605` — `assert got | restored == expected | {… if s == "transient"}`.
So the real `tar` proves the opposite of the status name.
**Reachable:** `pc_manifest.sh` writes `$OUT` at `:26-57`, runs a summary step that can `assert`-fail at
`:61`, and only gzips at `:69`. For the POST phase the crash is not fatal to the leg —
`pc_post.sh:155-157` waits 120 s and then prints "post manifest still running" and exits 0, after which
`run_leg.sh:68` collects. The collected leg then carries `manifest-post.txt`, which a consumer's entry
allowlist (`required | optional | dirs`) rejects as an unexpected entry.
**Minimal fix (pick one, and say which in `pins.py`):** add `--exclude='manifest-*.txt'` to
`collect_leg.sh:15` and a `"manifest-*.txt": "dropped"` row to `_EXCLUDE_DISPOSITION`
(`tests/test_s0_01_pc_tools.py:526`) — then `transient` becomes a fact; or delete the status and call the
two names `excluded_on_collect`. **Exact red test:** put `manifest-post.txt` in the framedir of
`test_the_collected_shape_is_the_mapping_minus_what_collect_drops` and assert it is NOT unpacked, with the
`| transient` escape hatch removed from `:605`.

### F11 — the report mis-attributes one of the two `audit_cp5` reds. SOLID.
Report NOT_DONE 2: "Both fail on the same cause — the checker's `_parse_scan_v23` rejects a v2.4 header".
Reproduced: only `test_shutdown_owned_survivor_is_named_whatever_its_command` fails that way.
`test_clean_shutdown_empty_after_scan_passes` fails on the TEST FILE's own literal:
```
tests/test_s0_01_audit_cp5_controls.py:110
  assert body[0].startswith("# process-scan v2.3 mode=after ") and " owned_present=0 " in body[0]
E  ... '# process-scan v2.4 mode=after rows=0 ... owned_zombies=2 table_rows=131'.startswith
```
Consequence: A5k's work is not confined to `check_acp_conformance.py`. See the A5k list below.

### F12 — the A5k site list is incomplete: four more sites, two of them in a second and third file. SOLID (reviewed from primary source; the v2.4-corpus one is reasoned, not run — no v2.4 corpus exists).
Detailed in "CHECKER CHANGES FOR A5k" below: the checker's five OTHER substring predicates, the
unconditional `agent-stderr.txt` read at `:1748`, `tests/test_s0_01_audit_cp5_controls.py:110`, and
`tests/test_s0_01_check_acp_conformance.py:2632` + `:2805` (a strict-xfail trap on the first v2.4 capture).

### F13 — the pasted `report_lint` line is from worktree mode, not the PIN. Cosmetic.
Report DONE 7 pastes `39 refs — OK 29 … UNRESOLVED 0 (worktree)`. At the PIN rev the same invocation gives
`40 refs — OK 22, NEAR 2, MISS 0, UNCHECKABLE 8, UNRESOLVED 8 (at 582ada4c)`. **MISS 0 either way**, so the
gate is met; but the `(worktree)` tag is doing real work in that line and a reader could take it for a
PIN-rev check. Paste the `--rev` line, or say why worktree mode was used.

### F14 — `wait_for_manifest`'s failure signature needs a NON-EMPTY log; an empty one still burns 300 s. Observation, not a defect.
`pc_launch.py:93` requires `os.path.getsize(log) > 0`. With an empty `manifest-pre.log` and no `.done`:
```
SystemExit: pc_launch: pre manifest did not finish within 300 s   (virtual seconds slept: 300.0)
```
Honest and bounded — it names the budget, it does not blame the wrong thing. Worth one line in the
docstring so a future reader does not read #32 as covering the silent-death case too.

### F15 — three more parser blind idioms, one already live in-tree. SOLID (mutants run).
Beyond F3, `tests/test_s0_01_pc_tools.py:105-110` also cannot see:
| mutant | idiom planted | result |
|---|---|---|
| V2 | `echo "{}" > "$FD"/leak-report-v2.json` in `pc_post.sh` | **42 passed — SURVIVED** |
| V3 | `Path(framedir, "tee-heartbeat-v3.json").write_text(...)` in `frame_tee.py` | **42 passed — SURVIVED** |
| V4 | `echo x > "${FD}"/mention-audit-v4.json` in `pc_mention.sh` | **42 passed — SURVIVED** |
The quoted-variable shell form is **already in the tree** at `pc_post.sh:115`
(`"$FD"/upstream-records/*.json`) — a read, not a write, but it proves the idiom is in the producers'
vocabulary today. The brief's rule ("a blind spot is a finding, not a blocker, unless a CURRENT producer
uses that idiom") is therefore satisfied for F3 (three live write/read sites in `pc_launch.py`) and F15
is the residual class.
**Minimal fix:** `_SH_FD = re.compile(r"""["']?\$\{?FD\}?["']?/([A-Za-z0-9._${}-]+)""")` and a
`_PY_PATH = re.compile(r"""\bPath\(\s*(?:FD|fd|framedir)\s*,\s*['"]([^'"\n]+)['"]""")`; then assert the
parser's own coverage does not shrink — e.g. pin the per-producer name COUNT, so a refactor that hides a
write fails loudly the way F3 did not.

### F16 — the required gate also dominates `--check`, which downgrades that mode's diagnosis. SOLID.
`build_capture_record.py:63-69` runs before the `check_mode` branch at `:163`, so it guards BOTH modes.
`--check`'s contract is byte-identity of a re-derivation ("does the committed record still re-derive"),
not completeness. Run over the COMMITTED golden leg `proofs/S0-01/evidence/golden/cancel` (v1-shaped, D4):
```
PARENT bytes: cancel: capture.json differs from re-derived content (--check)          rc=1
PIN    bytes: cancel: missing required leg files: backend-healthz-after.json, ... (17) rc=1
```
Both red — so this is not a new red — but the PIN can no longer distinguish a TAMPERED record from an
INCOMPLETE leg. That is the diagnosis `--check` exists to give.
**Minimal fix:** gate `build_capture_record.py:67` on `not check_mode` as well, or add an explicit `--partial`. See the ruling
in the coordinator's item below. **Exact red test:** `--check` over a leg with a tampered `capture.json`
and one required name absent must say `differs from re-derived content`, not `missing required leg files`.

---

## ITEM-BY-ITEM (0-13)

**0. Mechanical gates.** report_lint MISS 0 (F13 on the mode). ap_screen production `21 hits over 4 files`
and `--tests … 0 hits over 2 files` — both reproduced identical to the lane's. Re-classified the 21 BY
RUNNING: the ten AF-AP-40 hits (`:75, :99, :104, :110, :117, :122, :137, :143, :148, :157`) are all
dominated — I dropped each of the 13 names those gates read (including **both required DIRS**, `mentions`
and `upstream-records`) and got `rc 1` naming exactly that entry, 13/13. The lane's residual fix at `:65-66`
is real. The AP-32 / AF-AP-45 / AF-AP-55 / AF-AP-41 classifications hold on review; `pc_launch.py:68,134`
AF-AP-55 is genuinely single-stage (buzz-acp is a native binary launched from `PINNED_LAUNCH_ARGV`, and
`runtime-identity.json`'s `buzz_acp_exe_sha256 = a5a17ffc…` equals `pins.PINNED_BUZZ_ACP_SHA256` in the
real corpus — I checked the corpus file). **The screen misses an eleventh AF-AP-40 gate — F7.**

**1. The ONE list.** 35 names / four statuses.
(a) corpus ⊆ mapping — green, and the lane's LIST-DRIFT mutant is the right shape. I planted a NEW file
in a scratch copy of a corpus leg by a different route (mutant V10 emptying `PINNED_LEG_FILES_SINCE`,
killing `test_every_required_name_is_present_in_every_corpus_positive_leg`) — the corpus direction bites.
(b) producers ⊆ mapping — **F3 / F15: hollow for the lane's own file.**
(c) mapping ⊆ producers — `test_every_pinned_name_has_a_producer` is real; the lane's MAPPING-ORPHAN
mutant is credible and the parse is the same one F3 undermines, so this direction inherits the blind spot.
(d) the four statuses: `excluded_on_collect` (3) is proven by the real `tar` test in both directions and
earns its keep; `transient` (2) is **F10** — contradicted by that same tar test. `optional` and `required`
are fine.

**2. The v2.4 header.** `rows = len(keep)` / `table_rows = len(rows)` / `pinned_present` over `keep`
(`pc_post.sh:87,93-97`) is exactly what #5 asked for, and I killed both counter mutants
(V5 `table_rows=99` → 1 failed; V6 counters swapped → 7 failed). Attacks: argv[1]-without-python → **F4**;
symlinked argv[0] → **F5**; `readlink /proc/$PID/exe` at `pc_post.sh:120` before the signal — reviewed, not
reproduced (it needs a live pinned buzz-acp on the PC and the brief forbids running the capture tools there;
stated as a gap, not a pass). D5 (the retired v2.3 property): confirmed by reading the parent's
`pc_post.sh` — v2.3's `rows` was `len(rows)` (full table), so a dropped helper row really did leave a
`pinned_present` vs body inconsistency, and under v2.4 that is gone by construction. The CHECKER can still
tell "a foreign helper row was dropped" from "nothing was there" — but only through `table_rows > rows`,
which is a weak signal (`table_rows > rows` is true on every real scan, since the full table is ~130 rows).
So the honest statement is: the v2.3 signal is retired and **not replaced**. That is a defensible trade
(the v2.3 signal was itself the AF-AP-59 flakiness source), but the report's D5 should say "not replaced"
rather than "visible only as table_rows > rows", which reads as a substitute.

**3. D1.** SOLID, verified from primary source. `/root/s0-01-realleg/golden/run-1/process-scan-after.txt`
row 3 is `/home/rocco/s0-01-pinned/.venv-hermes/bin/python3 /home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp`
and `runtime-identity.json` records `agent_interpreter_realpath: /usr/bin/python3.13`. The exe rule cannot
identify the agent — the brief's own mechanism was wrong and the lane was right to replace it. The
replacement's weakness: **F4** is exactly the "spoofed argv makes pinned_present wrong AND no oracle
catches it" path, reproduced with a real process. It is fail-closed at the checker but for the wrong reason.

**4. `capture.json` fail-loud.** Empty dir → `rc 1` naming 26 files: reproduced. The twelve gates:
ten dominated (measured, 13/13 names), one undominated (**F7**), and the domination is unpinned (**F9**).
Three shapes run: EMPTY required file → **F6**; directory-in-place-of-file → correctly rejected; FIFO →
correctly rejected, no hang.

**5. `pc_launch.py`.** Six helpers, all reachable from `main()`. Red-before: the helpers are new, so I took
the parent's inline code as the red state — `wait_for_manifest`'s three arms, `summary_tail`'s
`<empty summary>`, `wait_for_tee_identity`'s named exit, `buzz_identity`'s `OSError` guard, and
`session_closure`'s `ps -s` all correspond to parent code that has the named defect, and the lane's four
mutants I re-ran (L14 WORLD-CLOSURE, L16 FINGERPRINT, plus L6/L9 below) are all genuinely killed.
Empty `.log` for the whole window → **F14**. D6 narrowing: confirmed against the SHARED TREE's B5i bytes —
SHARED TREE `proofs/S0-01/tools/frame_tee.py:232` (B5i's uncommitted bytes; the PIN's line 232 is a
different statement) is `subprocess.Popen([agent], stdin=subprocess.PIPE, stdout=subprocess.PIPE)` with **no**
`start_new_session`, so the pinned tree cannot produce the escaping shape; the lane's `:232` citation is
correct at the shared tree. `redact_environ` on a lone `\xff` re-run — green, and L16 kills the
fingerprint-on-replaced mutant with `assert 7 == 8`.

**6. `pc_negative.py`.** rc 0/1/3 propagate. Signal death → **F8**.

**7. D2 — `agent-stderr.txt`.** Confirmed by grep over the SHARED tree: the only writers are SHARED TREE
`proofs/S0-01/tools/acp_probe.py:283` and `:507` (N5h's uncommitted bytes), both into the negative leg. **My verifier ruling for A5k:
make F20 negative-leg-only; do NOT make the tee write the file.** The evidence is not missing — it is
already collected. `frame_tee.py:232` gives the agent no stderr pipe, so the agent's stderr is INHERITED
down to buzz-acp's, which `pc_launch.py:278-279` redirects into `buzzacp.raw.log`, masked into
`buzzacp.log` at `pc_post.sh:106,109`. Measured in the corpus: `/root/s0-01-realleg/golden/run-1/buzzacp.log`
(68 lines) interleaves buzz_acp rows with the AGENT's own —
`acp_adapter.entry: Starting hermes-agent ACP adapter`, `run_agent: No .env file found`,
`hermes_cli.plugins: Plugin 'deepinfra' registered …`. Making the tee drain a separate file would duplicate
those bytes, add a drain thread to B5i's hot path, and require re-capturing all four legs before the checker
could pass. **But the secret screen must MOVE, not vanish:** `check_acp_conformance.py:1747-1750`'s
`_STDERR_LEAK_RE` screen should run over `buzzacp.log` for positive legs, since that is where the agent's
stderr actually is. Dropping F20 without moving the screen loses a real control.

**8. Sequencing.** 2-of-3 RED in `tests/test_s0_01_audit_cp5_controls.py` reproduced; the attribution is
wrong for one of them (**F11**). Full A5k list below (**F12** — the lane's five, plus four).

**9. Forward drift.** Ran the PIN's `tests/test_s0_01_pc_tools.py` with the SHARED TREE's B5i `frame_tee.py`
and N5h `acp_probe.py` copied over the PIN: **42 passed**. The parser's name sets are unchanged
(`frame_tee` → frames-*.jsonl, runtime-identity.json, tee-status.json, timeline.jsonl; `acp_probe` →
agent-stderr.txt, env.json, runtime-identity.json, timeline.jsonl). No new non-dot name;
`.runtime-identity.tmp` is skipped by the dot rule at `tests/test_s0_01_pc_tools.py:141`; N5h's `raw_b64`
is a timeline field, not a file. NOT_DONE 4 holds — **but weigh it against F3**: this green is the same
gate whose coverage I just showed is idiom-dependent, so "green" here means "no new name in a recognised
idiom", not "no new name".

**10. The PC gate.** `pytest-exit: 0` / `55 passed in 1.70s`, RUN_ID `20260908T030130Z-6a41bd2`, from a
clean detached worktree of pushed `6a41bd2` + the PIN's nine files (identity table verified before launch,
all seven sha match). Agrees with the lane's sandbox `55 passed` ×2. Worktree removed afterwards; no PC
capture tool was run.

**11. Mutants.** Lane 16 + mine 10 = **26**. Mine:
| # | mutant | file:line | result |
|---|---|---|---|
| V1 | PRODUCER-UNLISTED via lowercase `fd` | pc_launch.py:118 | **SURVIVED** (42 passed) — F3 |
| V2 | write via `"$FD"/name` | pc_post.sh | **SURVIVED** (42 passed) — F15 |
| V3 | write via `Path(framedir, …)` | frame_tee.py | **SURVIVED** (42 passed) — F15 |
| V4 | write via `"${FD}"/name` | pc_mention.sh | **SURVIVED** (42 passed) — F15 |
| V5 | TABLE-ROWS-LITERAL `table_rows=99` | pc_post.sh:96 | KILLED — `test_pinned_present_is_exact_over_a_synthetic_table` |
| V6 | COUNTERS-SWAPPED (`rows`↔`table_rows`) | pc_post.sh:93,96 | KILLED — 7 failed, incl. `test_after_scan_persists_the_owned_closure_and_the_header` |
| V7 | NEG-RC-CLAMPED `max(rc, 0)` | pc_negative.py:42 | **SURVIVED** (55 passed) — F8 |
| V8 | EXISTS-NOT-ISFILE | build_capture_record.py:64,66 | **SURVIVED** (55 passed) — F9 |
| V9 | ARGV1-ARM-DROPPED | pc_post.sh:47 | KILLED — `test_pinned_present_is_exact_over_a_synthetic_table` |
| V10 | SINCE-EMPTIED | pins.py:231 | KILLED — `test_every_required_name_is_present_in_every_corpus_positive_leg` |
Lane mutants I re-ran to audit the table (4 of 16, all genuinely killed by the test the lane named):
L6 SUBSTRING-PINNED → 2 failed; L9 CAPTURE-GREEN-ON-NOTHING → 5 failed; L16 FINGERPRINT-ON-REPLACED →
1 failed (`test_env_redaction_fingerprints_the_raw_bytes`); L14 WORLD-CLOSURE → 2 failed, including the
detached-grandchild test the lane rewrote after its own hollow green. **Six survivors, all classed above.**

**12. Discipline.** Every file:line by `sed -n` on the PIN (spot-verified 21 refs). `report_lint` on this
report: pasted below. Process census: 110 processes on the box; **0 rows** match any signature I spawned
(`cat /home/rocco`, `time.sleep(120)`, `time.sleep(60)`, `pc_post.sh`) and **0 rows** name
`vp5a/basetemp`. Every process I started was killed by pid in its own `finally`.

**13. Design.**
*Home:* `pins.py` is the right home and is measurably inert for existing consumers — the checker already
does `from pins import (…)` at `check_acp_conformance.py:36`, and the parent-vs-PIN adjacent run shows the
`pins.py` addition breaks nothing (`602 passed` → the 3 reds are all `build_capture_record`/`pc_post`
consumers, none of them a `pins` import failure). Keep it. One improvement: export the derived sets as
FUNCTIONS (`pins.required_files(version)`, `pins.entry_allowlist()`) rather than raw dicts, so the
version rule cannot be re-implemented three times — which is exactly how **F2** happened.
*Four statuses vs two:* `required`/`optional`/`excluded_on_collect` earn their keep — the third lets the
mapping describe framedir names without polluting a consumer's entry allowlist, and it is proven in both
directions by the real `tar` test. `transient` does not (**F10**): its claim is contradicted by the lane's
own tar test and its window is reachable. Three statuses, not four.
*Entry-point identity for a SCAN:* right idea, under-implemented. The scan's job is ENUMERATION — produce a
candidate set — while identity is proven elsewhere (`runtime-identity.json`'s exe sha vs
`PINNED_BUZZ_ACP_SHA256`, and `pc_post.sh:120`'s readlink before signalling). Given that division, the
producer-side rule should be as NARROW as it can be without losing a real row, because every false row
becomes a checker Failure (`:1263`, `:1325-1330`). `argv[1] ∈ scripts` is not narrow enough (**F4**);
`basename(argv[0]).startswith("python") and argv[1] ∈ scripts` is, and still matches all three real corpus
rows. That one-line change makes the docstring's "ENTRY POINT" claim true.

---

## CHECKER CHANGES FOR A5k (the exact list; the lane's five, corrected, plus four)

All line numbers read at branch HEAD this session.

1. `proofs/S0-01/check_acp_conformance.py:152-155` — `_SCAN_HDR_RE`: `v2\.3` → `v2\.4`, and insert
   `table_rows=(\d+) ` before `utc=`. Safe: the highest group any caller reads today is 8, so new group 9
   (`table_rows`) and the shifted group 10 (`utc`) collide with nothing (verified by grepping every
   `hdr.group(` / `td_hdr.group(` use).
2. `:1153-1156` — `_parse_scan_v23` name + docstring (the name becomes a lie; cosmetic but load-bearing
   for the next reader).
3. `:1233-1234` — `if int(hdr.group(2)) == 0: raise "enumeration did not run"` → read `table_rows`
   (group 9). Under v2.4 `rows` is the BODY count and a clean shutdown legitimately has `rows=0`.
   Reproduced: `# process-scan v2.4 mode=after rows=0 … owned_zombies=2 table_rows=131`.
4. `:1337-1338` — the same for the teardown scan. Note this one is WORSE than the after-scan: the teardown
   body is required to be EMPTY by `:1357-1359`, so `rows=0` is the NORMAL outcome for every leg. Today it
   is an unconditional Failure.
5. `:1249-1253` — F17 `body_pinned` substring → the entry-point rule. **Fix `pc_post.sh:47` first (F4)**,
   then have both sides call ONE helper (put it in `pins.py` so the producer's heredoc can import it too —
   that removes the AF-AP-42 hand copy at `tests/test_s0_01_pc_post_scan.py:91-100` as well).
6. **NEW — the checker's five OTHER substring predicates over the same body**, which the lane's list does
   not mention. If only F17 adopts the entry-point rule, the checker computes two different pinned-ness
   predicates over one body: `:1284-1286` (A20a "not owned and cmd names no pinned path"), `:1296`
   (`tee_pids` selection), `:1298` (agent parented by a tee), `:1310-1318` (`PINNED_TEE_PATH not in
   tee_lines[0][3]` and the agent twin), `:1325-1330` (A20e). All must use the same helper.
7. `:1718-1726` — `_LEG_REQUIRED_FILES` / `_LEG_OPTIONAL_DIRS` → `pins.PINNED_LEG_FILES` /
   `PINNED_LEG_DIRS`; allowlist = `required | optional | dirs`; required = `required` minus
   `PINNED_LEG_FILES_SINCE` on an older corpus. **Route this through a `pins` function (F2).**
8. `:1736-1737` — F20 `_require_file(d / "agent-stderr.txt")`: drop for positive legs (D2 confirmed).
9. **NEW — `:1747-1750`**, the UNCONDITIONAL `(d / "agent-stderr.txt").read_text()` secret screen. If F20
   is dropped and this is left, every positive leg raises `FileNotFoundError`. Per my item-7 ruling, do not
   just delete it: point `_STDERR_LEAK_RE` at `buzzacp.log`, which is where the agent's stderr actually
   lands (measured in the corpus).
10. **NEW — `tests/test_s0_01_audit_cp5_controls.py:110`**, the test's own
    `"# process-scan v2.3 mode=after "` literal (plus the v2.3 wording at `:7`, `:11`, `:133`, `:141`).
    This is one of the two reds the lane attributed to the checker (F11) and it is in a different file.
11. **NEW — `tests/test_s0_01_check_acp_conformance.py:2632` and `:2805`**, both hard-coding
    `"# process-scan v2.3 "`. On the FIRST v2.4 re-capture `_corpus_version()` returns `"v2.2"`, the
    `pytest.mark.xfail(strict=True)` at `:2799-2801` is applied, `check_process_evidence` then PASSES →
    XPASS → **strict xfail = FAILURE** on all four positive legs. Accept `("# process-scan v2.3 ",
    "# process-scan v2.4 ")` there, exactly as the lane already did in its own mirror
    (`tests/test_s0_01_pc_tools.py:74`). Reasoned from primary source, not run — no v2.4 corpus exists yet.
12. **NEW (not a checker change but it lands with A5k) — `tests/test_s0_01_scripted_backend.py:894`**
    must be repaired or the branch stays red (F1).

Also for whoever fixes P5a's own files: F3 (`_PY_JOIN`), F4 (`is_pinned`), F2 (the tool's SINCE rule),
F6, F7, F8, F9, F10.

---

## COORDINATOR'S EXTRA ITEM (2026-09-08 03:1xZ, via lane C1) — the backend suite red

**Independently found and reproduced before the message arrived; it is F1 above.** Reproduced again at the
coordinator's exact framing, on my scratch copy of the PIN with
`S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden`:
```
tests/test_s0_01_scripted_backend.py::test_build_capture_record_roundtrip_check
  E  AssertionError: build failed: test-leg: missing required leg files: argv.txt, ... (21 names)
  E  assert 1 == 0
  tests/test_s0_01_scripted_backend.py:895: AssertionError
  1 failed, 336 deselected in 0.14s
```
(The coordinator's line 927 is the fixture's last `write_text`; the assertion that fails is `:895`
`assert r1.returncode == 0`. The deselect count differs only because I filtered with `-k build_capture`.)
Green at the parent `6a41bd2`: `1 passed in 0.37s`. In the full six-file adjacent run: PIN
`3 failed, 599 passed`, parent `602 passed`.

### The ruling asked for: is the fixture wrong, or is the check too strict?

**Neither, on its own. The gate is in the wrong PLACE.** P5a attached a COLLECTED-LEG completeness
precondition to the tool's entry point, where it now dominates two contracts that were never about
completeness.

**The fixture is legitimate and was never "a real leg" pretending to be one.** Its docstring states its
contract — V-d F12, "build a capture.json from a synthetic leg, then `--check` round-trips" — and it
asserts nothing about leg shape. Its seven files are exactly the inputs the record's semantic keys are
built from: `build_capture_record.py:74` timeline · `:98` runtime identity · `:103` env · `:109` startup ·
`:116` model · `:147` exit, plus `buzz-acp.pid` for the `:153-155` digest list. It is minimally complete
FOR THE FUNCTION UNDER TEST. It is a unit test of a pure function that stayed correct until the entry
point grew a second contract.

**The check is right and must not be weakened.** It closes SWEEP-prod #27 (`<empty-dir>` → rc 0, "a record
of nothing"), and the lane's parametrised `test_build_capture_record_takes_its_required_list_from_pins`
proves the ONE list really drives it. Relaxing the list, or making the tool tolerant of absences, re-opens
a real defect.

**Which side must change: BOTH, and both must land in the same commit as A5k — the branch is red until
they do.**

1. **P5a's side (required):** move the completeness gate onto the BUILD path only —
   change `build_capture_record.py:67` (which today reads `if missing:`) to gate on `not check_mode` as well. Rationale from measurement, not
   taste: `--check`'s only job is byte-identity of a re-derivation, and the gate has already cost that
   mode its diagnosis (F16 — over the committed golden `cancel` leg the parent says "capture.json differs
   from re-derived content" and the PIN says "missing required leg files"). `--check` is invoked in
   exactly one place in the tree (`tests/test_s0_01_scripted_backend.py:932`), so the blast radius of this
   change is that one test. This alone does NOT fix the roundtrip test, because it calls the BUILD mode
   first — which is why item 2 is also required.
2. **The test's side (required):** rebuild its leg through the helper P5a already wrote —
   `tests/test_s0_01_pc_tools.py:285 _synthetic_leg` — **imported, never copied**. If the fixture instead
   grows its own list of the 21 missing names, it becomes a second copy of the leg list, which is exactly
   the drift the ONE list exists to end — the reason is written into the mapping's own header comment. The cleanest shape: lift `_synthetic_leg` into a
   shared `tests/conftest.py` fixture that reads `pins.PINNED_LEG_FILES`, and have both test files use it.
   Then a future change to the list moves both fixtures at once.
3. **Do NOT "fix" this by adding the 21 names to the fixture by hand**, and do not add
   `pytest.mark.xfail` — the first re-creates the drift, the second hides a red the branch owns.

**If A5k can only carry one:** carry item 2 (the test), because it is what makes the branch green.
Item 1 is still required independently — it is the same defect as F2 (the tool consuming the ONE list
without the ONE list's own version rule), and F2 blocks the real corpus regardless.

**One more consumer to check when this lands:** the same required gate makes the tool reject every v2.2
corpus leg (F2). Item 1 does not fix that — `--check` and BUILD both need
`pins.required_files(version)`, resolving `PINNED_LEG_FILES_SINCE` (`pins.py:231`), which today exists
only in the test mirror at `tests/test_s0_01_pc_tools.py:81-87`.

---

## REPRODUCED vs REVIEWED vs SKIPPED

**Reproduced (ran it):** the 55-test baseline (sandbox and PC); the 3-red/599-pass vs 602-pass adjacent
comparison; F1; F2 (both PIN and parent bytes over a real corpus leg); F3 and F15 (four mutants);
F4 (real process AND `ps` shim through the real producer); F5 (shim); F6, F7, F9 (three input shapes plus
the 13-name domination sweep); F8 (`main()` return and OS status); F11 (the two `audit_cp5` reds with
their distinct causes); F10's tar/exclusion reasoning is read from `collect_leg.sh:15` and the lane's own
`:605` assertion — I did NOT stage a crashed `pc_manifest.sh`; D1 (corpus scan + identity file);
D6's `frame_tee.py:232` citation (shared tree); item 7's `buzzacp.log` evidence; item 9; report_lint;
ap_screen; four of the lane's sixteen mutants; the process census.

**Reviewed statically (not run):** `pc_post.sh:120`'s `readlink` refusal on a foreign pid — it needs a live
pinned buzz-acp and the brief forbids running the capture tools on the PC; the checker's `:1284-1330`
substring siblings; A5k site 11's strict-xfail trap (no v2.4 corpus exists to run it against); the twelve
`pc_launch` PC-only end-to-end paths, which the lane already declares NOT run (NOT_DONE 1) and which I did
not attempt.

**Deliberately skipped:** any run of `pc_launch.py` / `pc_post.sh` (full mode) / `run_leg.sh` /
`pc_negative.py` on the PC — forbidden by the brief and by the owner's live relay stack; the full `tests/`
tree in one run — the checker file alone is ~17 min, and I ran the six files that actually consume the
lane's symbols instead, which is the gate that found F1; `slopo` / `sentrux` / `ripwire` deltas — advisory
only and not requested by this brief.

## SHARED-TREE HYGIENE

No `git stash/checkout/restore/reset/add/commit/push` was run. `git status --porcelain` at the end is the
same set as at the start: P5a's six `M` + its `??` report and test file, plus the other live lanes'
(`frame_tee.py`, `scripted_backend.py`, `probe_omniroute.py`, `pc_lane.sh`, `pc_suite.sh`,
`tests/test_s0_01_frame_tee.py`, `tests/test_s0_01_scripted_backend.py`, `tests/red/…`, and the untracked
S0-02…S0-08 trees). Every mutant and every reproduction ran on copies under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vp5a/`; every pytest run carried
an explicit `--basetemp` under that directory. The one worktree I created
(`…/scratchpad/vp5a/wt-pc`, detached at `6a41bd2`, for the sanctioned PC gate) was removed with
`git worktree remove --force` and `git worktree prune`; `git worktree list` now shows only the main
checkout and another lane's `pc-gate-b5i.wt`. Mid-run I filled the scratchpad disk with full-tree copies
and cleaned it up (`1.3G` free after); no repo file was touched. Bridge use: exactly one
`pc_suite.sh launch` + one `wait`. No outward-facing action.

## report_lint ON THIS REPORT (item 12, honest)

```
report_lint: 80 refs — OK 21, NEAR 0, MISS 32, UNCHECKABLE 20, UNRESOLVED 7 (at 582ada4c)
```
**MISS 32 is not 32 wrong references, and I checked that claim rather than asserting it.** The linter
pairs each `file:line` with the nearest backticked token and requires the token to appear ON that line.
A review report violates that shape by construction in three places, and all 32 MISSes are one of them:
1. **Mutant rows** cite the line a mutant was applied to and quote the MUTATED text
   (`pc_post.sh:96` + `table_rows=99`; `pc_negative.py:42` + `max(rc, 0)`). The token cannot be on the line —
   that is the point of a mutant.
2. **Proposed fixes** cite the line to change and quote the replacement
   (`build_capture_record.py:64` + `EXISTS`/`ISFILE`).
3. **Adjacency**: a sentence naming two files puts the wrong token next to the ref
   (`tests/test_s0_01_check_acp_conformance.py:2632` + `:2805`).

The linter prints `cited line reads: '<actual content>'` for every MISS, so its output is itself a
verification of all 80 references — I read every one, and none contradicts what this report says about it.
Two loose citations that review found were TIGHTENED before this run: a mutant insertion point stated as
`:119` when `:118` is the anchor, and two SHARED-TREE line numbers (`frame_tee.py:232`,
`acp_probe.py:283`/`:507`) that are correct for the live lane bytes and NOT for the PIN — both are now
tagged `SHARED TREE` inline. The 7 UNRESOLVED are files outside the `--map` set that the linter cannot
address at a rev (`check_acp_conformance.py`, `frame_tee.py`) — the same limitation that moved the lane's
own numbers between worktree and rev mode (F13).
