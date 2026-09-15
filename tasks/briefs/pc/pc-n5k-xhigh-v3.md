# PC lane — N5k-XHIGH-v3 — ARM B of the effort A/B (the same brief as N5k, at `xhigh`; N5k at `medium` is arm A) — (S0-01 ACP probe round 14: the two surviving flags made load-bearing, the READ side open-then-fstat, the serial four-file run)

V3 NOTE (2026-09-15 00:0xZ): this lane REPLACES `pc-n5k-xhigh-v2.md` (stopped by the coordinator at 2 h 05 m: 96 tool calls, 284k output tokens, ONE line of code — two investigation loops on item 2's premise, the second after it had already decided to build; its lane dir and Hermes session are the A/B record, never a tree to resume). The governing brief now carries TWO amendments at its top — AMENDMENT 1 (the `report_lint` gate is BOUNDED) and AMENDMENT 2 (item 2's premise CORRECTED from a measurement at the real emitter: CPython's `os.open` is close-on-exec by default and the Popen launch keeps `close_fds=True`, so the CLOEXEC-DROPPED mutant does not leak at the real emitter; the replacement negative control is the isolated F_SETFD-controlled census + the structural pin + ONE DISCREPANCIES line; NO interpreter archaeology, no prctl, no C programs, no web search). The dispatcher also injects the standing rule PREMISE CONFLICTS ARE BOUNDED. Take the amendments as settled facts and BUILD: items 3, 4, 1, 2, 5-10 in that order; at most three experiments on any conflict, then a DISCREPANCIES line and build-or-stop. A new lane id because the PC-side replay guard keys on the brief filename + PIN and the brief changed.


PIN: c6c384a

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-01-n5k-probe-the-flags-load-bearing-the-read-side-atomic-the-serial-run.md` — READ IT WHOLE and follow it
item by item (1-10). Your worktree IS `git archive c6c384a` plus the lane patch (the brief + this file); VERIFY-N5j's report, the N5j report and the
9d probe bytes are all in the archive. Save your report at `tasks/briefs/s0-01-n5j-support/N5k-xhigh-report.md` inside your tree, draft after EACH item
(the incremental rule), and return it whole as your final message.

Venue notes specific to this build:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; an absolute `--basetemp` under your lane's scratch dir; venue exports on every pytest run:
  `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`.
- Every FIFO/hang probe standalone under `timeout` with a PID-scoped watchdog — never a hang shape through pytest; kill only what you start, by pid.
- The serial four-file run (item 5) may exceed one tool call's ceiling: split it into two foreground calls, paste both; never background a run and stop.
- No live buzz-acp / hermes-acp / Hermes / tee / relay / model execution; the probe's real leg is NOT run here (F4 is the coordinator's).
- Other lanes may share this host: never touch `proofs/` or `tests/` outside your own private copy; every mutant on a scratch copy of your archive.
- ARM B NOTE: you are the `xhigh` arm of a medium-vs-xhigh comparison (FINDINGS-LOCAL-BUILDER-QWEN38 §6 step 5). Work the brief exactly as
  written — never mention or look for the other arm's tree or report; the comparison is the coordinator's. Your report's final section
  states wall clock per item as you observed it (the incremental rule's draft timestamps are the source).
