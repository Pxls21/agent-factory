# VERIFY-B5j — adversarial grade of lane B5j (S0-01 frame tee round 15: both shutdown-clause halves derived, one sentence structurally, every tee-pipe mention pinned, the zombie branch asserted, the OSError guard deterministic, the SIGTERM identity, the race aggregate, the FIFO domain)

You are an adversarial-verifier (the PC Hermes verify lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo
agent-factory, branch claude/soundbox-kit-migration-iz1jwf. **PIN: `01499e7`** (checkpoint 9b — the commit carrying the lane's two
files `proofs/S0-01/tools/frame_tee.py` (567 lines, sha `990a2ad2…`) and `tests/test_s0_01_frame_tee.py` (3950 lines, sha
`bbdd7cdb…`) + its report `tasks/briefs/s0-01-b5j-support/B5j-report.md`). Grade the bytes of `git archive 01499e7` from a scratch copy
under your lane's scratch dir; every mutant on scratch copies; every pytest run with an explicit `--basetemp` and the venue exports
(`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`); every hang probe standalone under `timeout` with a
watchdog (never a hang shape through pytest — a deadlocked pytest+tee pair is the failure this file exists to prevent); kill only what
you start, by pid; never background a run and stop; no outward actions; never read, print or commit a credential. Authorization: the
owner's own ACP frame tee under test on the owner's system.

**Inputs (read in this order):** VERIFY-B5i's report `tasks/briefs/s0-01-b5j-support/VERIFY-B5i-report.md` (the round's contract:
VB-F1..F14) · the lane brief `tasks/briefs/s0-01-b5j-tee-the-halves-derived-the-sentence-rule-every-mention-of-the-pipe.md` · the
lane's report (its DONE table, the 12 required mutants, the 51-harness discrepancy with SEVEN rows it declared malformed, the
self-attack, D1-D4) · the vendored `acp.rs` the test derives from (sha `44e82861…`; `:422-444`, `:2323-2329`) · `docs/INCIDENT-LOG.md`
(AF-AP-55, AF-AP-58, AF-AP-59, AF-AP-61, AF-AP-63, AF-AP-64).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-01-b5j-support/B5j-report.md --rev 01499e7 --map tee=proofs/S0-01/tools/frame_tee.py
--map test=tests/test_s0_01_frame_tee.py` — the lane's report claims `28 refs — OK 28, MISS 0`; the coordinator's run on the same
bytes read `OK 24, NEAR 2, MISS 2` (report line 45: `test:3871` and `test:3895-3898` do not carry the tokens `re.split`,
`len(buzz_sentences) == 2`, `clause_rx`). Resolve which is right and what the two misses are (a stale citation after the last edit, or
a claim about lines that do not exist — a finding either way). `ap_screen.py` on the tee (13 hits) and `--tests` (AP-66 ×1) —
classify by RUN; pyflakes; the FILE IDENTITY table against the PIN.

## Items
1. **VB-F1 — the halves derived (`test:3752-3779`).** Reproduce that `SIGKILL`, `killpg`, `child`, `wait`, the order and the seconds
   come from the pinned `acp.rs` range and not from typed literals: mutate the vendored file's range (a scratch copy) — does the test
   follow the SOURCE (red for the right reason) or its own constants? Then the three-site mirror the round was opened for
   (MIRROR-3SITE, MIRROR-3SITE-ORDER): reconstruct both on scratch copies and paste the killer lines.
2. **VB-F2/F3 — one sentence structurally (`test:3869-3922`).** Attack the docstring rule: a second buzz-acp sentence spelled
   `buzz_acp`, `buzz‑acp` (U+2011), `Buzz-ACP`, or "the client" with no name at all; a paraphrase in a `#` comment inside the
   module (not the docstring); a false sentence split across three lines so no two-line window holds both the kill token and the
   seconds; the derived seconds spelled `five seconds` / `5s` / `5.0 s`; the tokens inside a string literal the tee prints. Which
   evade the proximity rule, and does any evasion matter (would a reader be misled)? SEVENTH-SITE-PARAPHRASE and both SIXTH-SITE
   mutants re-run.
3. **VB-F4 — every mention of a tee pipe pinned (`test:3147-3188`).** Attack the walker: `getattr(tee_proc, "stdout")`,
   `tee_proc.__dict__["stdout"]`, `p = tee_proc; p.stdout.read()` (the lane DECLARES the process alias out of reach — measure the
   cost: is any such alias in the PIN's real file?), an alias assigned in a nested function or a lambda, a helper that receives the
   pipe as an argument and iterates it (is the BOUNDED-helper allowlist checked by name only?). The floor of 50 mentions: a walker
   that counts 50 and classifies none as unbounded — plant an unbounded read inside a `with` or a comprehension. Reproduce the
   standalone hang proof for PIPEREAD-ITERATION with your own watchdog (wchan lines pasted).
4. **VB-F5 — the zombie branch (`test:2879`, `:653`, `:1287`, `:2807`).** ZOMBIE-BRANCH-LIVE re-run; the lane's D2 on
   GRANDCHILD-UNKILLED-S1/S2 (it says the harness's deletion mutants could not distinguish — is the corrected branch flip the
   right killer, and does site 3's by-construction survivor hide a real gap?).
5. **VB-F6 — `_reread_interpreter` (`tee:81-98`, `test:3599`).** The impossible pid (`pid_max + 1`) exercises `FileNotFoundError`;
   attack the OTHER OSError shapes: a pid that exists but whose `/proc/<pid>/exe` is unreadable (EACCES — another user's process
   on this host: pick one by `ps -eo pid,user` and read it as uid 1000), a pid that dies between the readlink and the hash (a race —
   is the hash side guarded too?), a `/proc/<pid>/exe` that is a deleted binary (`(deleted)` suffix). Which raise out and which
   return `None` with the named stderr line?
6. **VB-F9 — the SIGTERM pin (`test:3005`).** Attack: `from signal import SIGTERM` + `signal.signal(SIGTERM, h)`; `signal.signal(15, h)`;
   `signal.SIGTERM` behind an alias; a handler installed for SIGINT as well. Which install shapes pass the pin?
7. **VB-F10/F11 — the race aggregate (`test:3554-3586`) and the FIFO domain (`test:893-900`).** RESAMPLE-ALWAYS-FAILS re-run; the
   `any(not lost …)` — on a loaded box could all 20 trials legitimately LOSE (a flake in the other direction)? Measure the win rate on
   this host under `stress`-like load (a busy loop on N cores) and state the margin. The FIFO case: rc 64 and the exact stderr line —
   attack with an executable FIFO (chmod +x), a symlink to a FIFO, a directory.
8. **The 51-harness discrepancy.** The lane excluded SEVEN rows as malformed and replaced them with corrected mutants (3/3 census,
   the branch flips, the third exact sentence). Reconstruct each of the seven CORRECTLY yourself (do not reuse the lane's driver)
   and run them: a survivor among them is a finding; agree or disagree with each exclusion by RUN. Then `R19-COLLECTOR`.
9. **D4 — the corrected source comment (`tee:49-52`).** Is the comment the lane rewrote still the contract the test enforces (five
   reference sites carrying only the constant's NAME)? Count the sites on the PIN mechanically; a sixth site or a site that restates
   the clause is a finding.
10. **Mutants ≥ 40** (the 12 required + your reconstructions of the seven + the attacks above), pasted with killer lines; by-construction
    survivors stated as such.
11. **The 18-class re-scan** on the two files by RUN; every `if <field> == <literal>:` without a raising other arm listed (AF-AP-65);
    the report's class table agreed or disagreed per row.
12. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census by pid.
13. **The design.** Is a whole-file two-line proximity ban the right shape, or does it forbid legitimate prose (a comment that
    explains the kill-before-wait order IS the clause's meaning — can a maintainer write it anywhere but the constant)? Is the
    50-mention floor a real floor or a number that happens to match today's file? What would the round after this one have to do to
    make the tee MERGE-READY, and is there anything left that is not the coordinator's (VB-F12 corpus re-capture, VB-F13 the PC stat,
    VB-F14)?

## Report
Write it to `tasks/briefs/s0-01-b5j-support/VERIFY-B5j-report.md` inside your tree, draft after EACH item, and return it whole as your
final message. Findings: ALL, no severity filtering, each with file:line on the PIN, expected vs observed, the failing input, the
minimal fix, the exact red test, SOLID/UNSURE; reproduced vs reviewed vs skipped; verdict MERGE-READY or NOT-READY with the blocking
set and the cheapest path; the items that are the coordinator's named as such.
