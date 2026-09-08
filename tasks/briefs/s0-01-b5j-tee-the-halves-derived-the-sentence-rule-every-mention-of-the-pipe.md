# Lane B5j — S0-01 frame tee round 15: both halves of the shutdown clause bound to derived facts, a sentence-level rule over the docstring and a proximity ban over both files, every MENTION of a tee pipe pinned, the zombie branch asserted, the OSError guard tested deterministically (build lane: PC Hermes `code-implementer` when the slot is free, else sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".) The tee's last checkpoint is 8y =
`75998e7` (pushed): `proofs/S0-01/tools/frame_tee.py` 542 lines sha `49e3cce4…`, `tests/test_s0_01_frame_tee.py` 3744 lines sha
`bd75f470…` — unchanged at HEAD; gate against HEAD.

**Why:** VERIFY-B5i (report `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/wf-results-r5/VERIFY-B5i.md`
— READ IT WHOLE FIRST; it is the contract for this round) graded round 14 NOT-READY with three blockers, each a mutant the verifier
RAN with a red-green-validated fix: **VB-F1** the equality that item 1 built is a THREE-SITE MIRROR — `test:3620-3621` hand-type the
two halves (`kill_half`, `wait_half`); only the seconds and the ORDER are derived from `acp.rs`, so swapping what the test calls the
two halves and updating the constant + the module docstring to match yields the exact order-reversed sentence B5h's F1 was opened
for, with `114 passed in 170.24s`; **VB-F2** the negative direction is a two-token blacklist (`killpg`, `5 s`) over one docstring —
a PARAPHRASED false sentence ("a grace period in which it may still flush… sends a terminate signal before that grace period
starts") beside the true clause survives (`acp.rs` has 0 `SIGTERM`; the group kill precedes the wait); **VB-F4** the structural hang
pin keys on three attribute names and one receiver — `next(iter(tee_proc.stdout), None)`, `.readlines()`, `os.read(fileno())` and an
alias all evade it, and the iteration form re-opens the F9 deadlock on the PIN's own tee (wchan `hrtimer_nanosleep` /
`anon_pipe_read`, reproduced). Also: **VB-F3** a false sentence outside the six named sites survives in either file; **VB-F5** the
zombie test discards `_kill_own_grandchild`'s branch (a LIVE grandchild passes `..._is_already_gone`); **VB-F6** the AF-AP-55 `OSError`
guard's only coverage is a race that is silent on an idle box; **VB-F9** the AF-AP-58 pin never inspects the signal's identity;
**VB-F10** the coordinator's relaxed race assertion is CORRECT (reproduced twice) but near-vacuous alone; **VB-F11** the FIFO shape is
claimed with no test; **VB-F7/F8** the report's refs after `test:3452` are +6 off and the FILE IDENTITY row stale — the
COORDINATOR's 6-line insertion at checkpoint 8y after the lane's lint run (the coordinator's lesson, baked; re-stamp at the FINAL
bytes this round). Held under attack: the census helper's branches, the kill/identity fail-closed paths, the AST kill pin as a
subtraction, the `S0_01_AGENT` domain (seven shapes), the identity re-sample (20/20 + 50 under load), the self-sweep re-runs, both
sandbox gates, the PC gate. VB-F12 (the corpus `tee_sha256` two-way accept) and VB-F13 (the PC stat) are the coordinator's.

**Inputs (read in this order):** VERIFY-B5i whole · your predecessor's report `tasks/briefs/s0-01-b5i-support/B5i-report.md` and
brief · the vendored `acp.rs` the test derives from (the path and sha the test pins — read `:422-444` and `:2323-2329`) ·
`docs/INCIDENT-LOG.md` (AF-AP-55, AF-AP-58, AF-AP-59, AF-AP-61, AF-AP-63) · the pack `scripts/lane_context.sh -q 'where does the
tee read its pipes and where does the test derive the shutdown clause' -s _read_with_deadline _kill_own_grandchild -o pack.md
proofs/S0-01/tools/frame_tee.py` (run it first; attach it).
**Scope (exactly two files + your report):** `proofs/S0-01/tools/frame_tee.py` · `tests/test_s0_01_frame_tee.py` · report
`tasks/briefs/s0-01-b5j-support/B5j-report.md`. NOT yours: `pins.py`, the probe, the checker, the PC tools, `.claude/hooks/*`, the
corpus. Shared-tree rules: never `git stash/checkout/restore/reset/add/commit/push`; every gate from a `git archive <PIN> | tar -x`
copy under /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/b5j/ with your two files copied in
(`scripts/lane_gate.sh -r <PIN> -f "proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py" -t "tests/test_s0_01_frame_tee.py"
-n 2`, ONE foreground call, ~3 min per run, `LANE_GATE_DIR` under your scratch dir); explicit `--basetemp`; every hang probe
watchdogged and standalone (a deadlocked pytest+tee pair is the failure the brief warns about — prove an evasion with the pin's own
walk and the deadlock with a bounded probe, never by running a mutated hang shape through pytest); kill only your own processes
by pid (never pkill/pgrep -f); NEVER background a run and stop; no outward actions; NO PC bridge; never read, print or commit a
credential. Interpreter `/root/venv-agent-factory/bin/python`; `S0_01_VENUE=sandbox S0_01_REAL_LEG_DIR=/root/s0-01-realleg/golden`.

## Design (pinned — build it, do not redesign it; line numbers are `75998e7`'s)
1. **VB-F1 — both halves bound to derived facts.** After `test:3621`: the kill half must carry the tokens the DERIVED kill range
   carries (`SIGKILL` and the group-kill helper name read from `acp.rs:2323-2329`, not typed) and the wait half must carry
   `"%d s" % wait_secs` and `waits`; the verifier's four lines are the floor — derive the kill tokens from the source range rather
   than typing them if the range names them (it does: read it). Mutants MIRROR-3SITE-ORDER (three edits) and MIRROR-3SITE ("for the
   socket to close") must DIE; paste both runs (red on `75998e7`, green after).
2. **VB-F2 + VB-F3 — one sentence in the repo, structurally.** (a) Over the module docstring: every sentence naming `buzz-acp`
   outside the `(client)` introduction must be exactly `PINNED_SHUTDOWN_CLAUSE`'s sentence — SEVENTH-SITE-PARAPHRASE dies. (b) Over
   BOTH files whole: outside the clause's own sites, no two-line window may carry both a kill token (`SIGKILL`/`killpg`) and the
   derived seconds token — SIXTH-SITE-TESTDOC and SIXTH-SITE-TEECOMMENT die; the existing literal regexes at `test:3741` go. If the
   `start_kill()` fallback nuance (the direct child when the group kill fails) is worth a line, put it in the R1 comment block
   beside the derived ranges, phrased so rule (b) holds — never in the module docstring.
3. **VB-F4 — every MENTION of a tee pipe is pinned.** Replace the three-spelling walk at `test:3062` with a walk over
   `Attribute(value=Name('tee_proc'), attr in ('stdout', 'stderr'))` (and any alias assigned from one, tracked through simple
   `Name = tee_proc.stdout` assignments in the same function) that allows exactly four parents: an argument to a `BOUNDED` helper,
   `.close()`, a keyword argument to a `Popen`, or a read call carrying its own `timeout=`. PIPEREAD-ITERATION, -READLINES, -OSREAD,
   -ALIAS all die; the pin walk over the PIN's real file stays at 0; paste the standalone watchdogged deadlock probe for the
   iteration shape (wchan lines) as the red-before evidence, never a pytest hang.
4. **VB-F5** — `assert _kill_own_grandchild(framedir) == "gone"` at `test:2857`; ZOMBIE-BRANCH-LIVE dies.
5. **VB-F6** — lift the readlink+hash of the re-sample into a module-level `_reread_interpreter(pid) -> (realpath, sha) | None`;
   a deterministic test with a pid above `/proc/sys/kernel/pid_max` returns `None` and the stderr line
   `agent interpreter re-sample: exited before identity`; RESAMPLE-NO-OSERROR-GUARD dies on an IDLE box (paste with the load).
6. **VB-F9** — the AF-AP-58 pin asserts the installed handler's signal is `SIGTERM` (`stmt.value.args[0].attr == "SIGTERM"`).
7. **VB-F10** — in the race test's lost branch, also assert at least one of the 20 trials WON (`any(...)`), so an always-losing
   tee (RESAMPLE-ALWAYS-FAILS) dies on this test alone, not only on its sibling.
8. **VB-F11** — the FIFO case added to `test_non_executable_agent` (rc 64, the exact stderr line).
9. **Mutants:** the verifier's 51 re-run at the FINAL bytes — the ten survivors (MIRROR-3SITE, MIRROR-3SITE-ORDER,
   SEVENTH-SITE-PARAPHRASE, SIXTH-SITE-TESTDOC, SIXTH-SITE-TEECOMMENT, ZOMBIE-BRANCH-LIVE, PIPEREAD-ITERATION/-READLINES/-OSREAD/
   -ALIAS, RESAMPLE-NO-OSERROR-GUARD idle, RESAMPLE-ALWAYS-FAILS on the race test) must DIE with the killer line pasted; the two
   by-construction survivors (GRANDCHILD-UNKILLED-S3, the documented alias limit if any remains) stated as such.
10. **18-class self-sweep** as an enumeration (counts + method); SWEEP-tests rows 12.1, 14.1, 14.2 show CLOSED with the run.
11. **Report discipline:** FILE IDENTITY of the FINAL bytes (both rows re-stamped); every `file:line` from `grep -n` on the FINAL
    bytes and `python3 scripts/report_lint.py <report> --map tee=proofs/S0-01/tools/frame_tee.py --map test=tests/test_s0_01_frame_tee.py`
    pasted with MISS 0 (run it LAST, after the last edit); the two `lane_gate.sh` RESULT lines pasted; `ap_screen.py` on the tee (13
    hits) and `--tests` (AP-66 ×1) classified by run; pyflakes rc 0; the process census; NOT-done first-class. NOT this lane's:
    VB-F12 (the corpus `tee_sha256` re-capture + the version-gated acceptance — A5l/the coordinator), VB-F13 (the PC stat), VB-F14.
