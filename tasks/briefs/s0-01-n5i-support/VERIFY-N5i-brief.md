# VERIFY-N5i — adversarial grade of lane N5i (S0-01 ACP probe round 12: the write class closed at every receiver, the probe's own file hashed once, the blocking drain named, the AST self-scan over reads and writes, the honest class table)

You are an adversarial-verifier (Opus 5 in the sandbox). Repo /home/user/agent-factory, branch claude/soundbox-kit-migration-iz1jwf.
**PIN: `628da83`** (checkpoint 9a — the commit carrying the lane's two files + its report). Grade the bytes of `git archive 628da83` from a
copy under the session scratchpad /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ (`vn5i/`; delete it when
done). Read-only git on the shared tree (other lanes hold uncommitted edits there — none in your scope); every mutant on scratch
copies; every pytest run with an explicit `--basetemp`; every FIFO/hang probe under `timeout` and standalone (never a hang shape through
pytest); kill only what you start, PID-targeted (never `pkill`/`pgrep -f`); never background a run and stop; no outward actions; NO PC
bridge except the one carve-out below; never read, print or commit a credential. Interpreter `/root/venv-agent-factory/bin/python`;
`S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden` on every pytest run. Authorization: the owner's own ACP probe
under test — defensive work on their system.

**The ONE bridge action you MAY take:** the pytest-only PC gate `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_01_acp_probe.py
tests/test_s0_01_negative_contract.py tests/test_s0_01_check_initialize.py` from a clean detached worktree of the PIN, then `wait
<RUN_ID>`. Nothing else on the bridge. The coordinator's own PC run on these bytes is pasted in the checkpoint commit — agree or disagree.

**Inputs (read in this order):** VERIFY-N5h's report `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/wf-results-r5/VERIFY-N5h.md`
(the round's contract: F1-F14, the survivors M19/M20/M21/M23) · the lane brief `tasks/briefs/s0-01-n5i-probe-the-write-class-and-the-honest-table.md`
· the lane's report `tasks/briefs/s0-01-n5i-support/N5i-report.md` (the red-before/green-after table, 33 mutants, DISCREPANCIES 1-6, the
consumer-contract correction in item 9, class 17 stated as a limit) · `proofs/S0-01/negative_contract.py` (`:82` `validate_negative_dir`,
`:103` the allowed keys, `:187` the probe_sha256 pin) · `proofs/S0-01/check_acp_conformance.py` (`:262`, `:1739`, `:1789`, `:1494`) ·
`proofs/S0-01/tools/frame_tee.py` (who else writes a timeline) · `docs/INCIDENT-LOG.md` (AF-AP-40, AF-AP-42, AF-AP-55, AF-AP-57,
AF-AP-59, AF-AP-63, AF-AP-64, AF-AP-65) · the A5k brief `tasks/briefs/s0-01-a5k-checker-consumer-of-the-pinned-list-v24-header-ck12-blockers.md`
item 8 (the lossy-line message in `check_timeline` — built on VERIFY-N5h's consumer claim).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-01-n5i-support/N5i-report.md --rev 628da83 --map probe=proofs/S0-01/tools/acp_probe.py
--map test=tests/test_s0_01_acp_probe.py` — MISS 0 or a finding; `ap_screen.py proofs/S0-01/tools/acp_probe.py` (8 hits) and `--tests`
(AF-AP-57 ×1) and `--s0-01` — classify every hit by RUN; pyflakes rc 0; the FILE IDENTITY block against the PIN (both rows).

## Items
1. **`_open_regular` (`probe:62`) — the one write primitive.** Attack the flag set: a FIFO with a live reader (O_NONBLOCK opens it —
   does `S_ISREG` on the fd refuse it, and is the fd CLOSED on refusal? count fds), a symlink to a regular file (ELOOP — the error
   text pasted), a symlink in the PARENT path (`framedir` itself a symlink into a foreign directory — O_NOFOLLOW covers the last
   component only; is the framedir's provenance the runner's or the probe's problem? rule), a directory, `/dev/null` and a socket, an
   existing regular file (O_TRUNC — fine, prove it), a HARDLINK to a foreign inode (class 17 — the lane's stated limit: reproduce the
   mirror; state whether `os.fstat(fd).st_nlink == 1` is the right one-line hardening for round 13 or whether the RUNNER's framedir
   creation makes it unreachable), an O_NONBLOCK left set (the lane clears it — on a regular file a set O_NONBLOCK is a no-op: is the
   clearing dead code or does any path write to a non-regular fd after the guard?).
2. **The eight receivers and the AST self-scan (`test:2831`, `:2839`, `:2938`).** Enumerate the write receivers on the FINAL bytes
   yourself (every `open`/`os.open`/`Path.write_*`/`fdopen`/`NamedTemporaryFile`/`shutil`/`print(file=)`/`json.dump(…, open())`) and
   compare with the scan's 13. The golden set is keyed `(function, category, receiver)` WITH COUNTS (the lane's D4): plant a FOURTH
   `os.readlink("/proc/%d/exe" % proc.pid)` in `main` and a SECOND `os.open` in `_open_regular` — does the count make the scan red?
   Plant an aliased opener (`o = open; o(p, "w")`), `io.open`, `os.fdopen(os.open(p, os.O_WRONLY|os.O_CREAT))`, `pathlib.Path(p).write_text`,
   `open(p, "a")` — which evade the scan? The coverage floor is 12 for 13 examined: delete ONE guarded receiver's call from a copy —
   does anything go red (a floor that tolerates a missing receiver tolerates the receiver the attacker removes)? The "handle bound by a
   guarded `with`" exemption: a read on a handle from an UNGUARDED opener — caught where?
3. **The cached import-time hash (`probe:95`, `:99`, `:170`, `:554`) — the lane's D1.** The mid-run swap now yields rc 0 with the
   digest of the bytes that ran. Attack: `__file__` relative + a `chdir` before the hash (`_PROBE_PATH` = `os.path.realpath(__file__)`
   — taken when?); the probe launched through a symlinked path; a stale `__pycache__` whose pyc header (mtime+size) still matches a
   swapped source — the bytecode that RAN is not the source that was HASHED: reachable by an agent (no: the probe is already
   running) or only by the framedir's owner before launch? State the trust boundary precisely and whether `python_dont_write_bytecode`
   + `-B` in the runner close it. Then `negative_contract.py:187` — a swapped probe file fails the leg at CHECK time with
   `probe_sha256 mismatch`: reproduce with the golden corpus (the 9 xfails the lane reports are that mechanism — paste the reason).
4. **The drain bound (`probe:513` `join(timeout=3)`, `:519` `is_alive()`).** A drain still alive 3 s after the agent exits is now a
   named FAILURE — a live-behaviour change on the REAL negative leg. From the pinned hermes-acp / hermes sources (READ-ONLY under
   `/home/user/nerdherderdani/`): can the agent leave a child holding its stderr after exit (a model-client subprocess, a detached
   worker)? If it can, the real capture reds and the bound is a fixture-calibrated constant (the class VERIFY-CK10 named) — rule
   whether the coordinator's PC re-capture is the only admissible calibration and say so. Attack the tests: `join(timeout=9)` — does
   any test bound the TIME (the report's `2.5 < elapsed < 10`)? `is_alive()` checked BEFORE the join; the `and drain_error[0] is None`
   guard (class 16: force the window with a drain that records and sleeps — does it protect anything?).
5. **F2/F8 appended failures (`probe:527`, `:531`), the third timeout wording (`:288`), the fake's ordinal gate (`test:1442`, `:1481`,
   `:1486`).** M23 must die on `-k early_retry_recovers` ALONE (the lane's D3: `FIRST_OK=4` does NOT kill it — the call-site
   distribution does): reproduce. Is the SITES assertion a LITERAL line-number mirror (`[308, 328, 328, 328]` typed) or structural
   (one distinct site for the retry loop)? A literal is AF-AP-64's cousin — every later edit of the probe breaks it for the wrong reason.
6. **The consumer-contract correction (report item 9) — the finding that reaches OTHER lanes.** Reproduce the chain: a PROBE capture
   goes `check_acp_conformance.py:1789` → `:1494` → `negative_contract.validate_negative_dir` (`:82`), whose key set (`:103`) allows
   `raw_b64` and which fails closed on the mangled TEXT; `check_timeline` (`:262`) is called at `:1739` only, inside the POSITIVE-leg
   loop. The coordinator's own read: the TEE writes `raw_b64` too (`proofs/S0-01/tools/frame_tee.py:356`, `:447`), so a positive leg's
   timeline CAN carry a lossy line and A5k's item 8 (the lossy-line message in `check_timeline`) is reachable for tee-captured legs —
   VERIFY-N5h's F3 named the right consumer for the WRONG producer. State precisely which consumer reads which producer's lossy line,
   whether either can silently pass a mangled frame, and what VERIFY-CK13 must check on A5k's item 8 (a finding addressed to it, with
   file:line evidence — not N5i's defect).
7. **Mutants ≥ 40.** Re-run the lane's 33 on the FINAL bytes on scratch copies (N8's survive-then-killed story reproduced: the first
   form must SURVIVE without the through-the-M3-handler case and DIE with it); add yours: APPEND-ORDER (the second failure prepended),
   HASH-NONE-AT-M3 (the M3 handler writes `probe_sha256: null` without the named error), DRAIN-BOUND-9S, ISREG-AFTER-CLOSE (the fd
   closed before the fstat), NOFOLLOW-PARENT (a symlinked framedir), the planted receivers of item 2, GOLDEN-COUNT-LOOSE (the count
   check removed). Paste every killer line; by-construction survivors stated as such.
8. **The 18-class re-scan** on the two files (the lane's table: class 17 DOCUMENTED-LIMIT, class 16 the `drain_error` guard, class 5
   the `"Traceback" not in stderr` absence, class 14 the structural flag mirror `"os.O_NOFOLLOW" in prim`) — agree or disagree per row
   by RUN; every `if <field> == <literal>:` without a raising other arm listed (AF-AP-65).
9. **The PC gate (the carve-out)**; paste beside the checkpoint's `pc_suite` line; agree.
10. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census by pid; shared-tree hygiene.
11. **The design.** Is a probe that REFUSES non-regular evidence paths the right boundary, or must the runner (`pc_negative.py`,
    `collect_leg.sh`) also pre-validate the framedir (both — say which invariant each one owns)? Is "the digest of the bytes that ran"
    the right identity for `probe_sha256`, given `negative_contract.py:187` compares it against the file ON DISK at check time (two
    different questions answered by one field — is a second field needed)?

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-N5i.md` — draft after EACH item — then return it whole. Findings: ALL, no
severity filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact red test,
SOLID/UNSURE; reproduced vs reviewed vs skipped; verdict MERGE-READY or NOT-READY with the blocking set and the cheapest path; the
items that belong to OTHER lanes (A5k/VERIFY-CK13, A5l, N5j) named as such.
