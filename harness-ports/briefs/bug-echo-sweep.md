# BRIEF — bug-echo sweep for a fixed defect (role: echo-sweeper)
PIN: {PIN}

Read-only. No edits, no commits, no subagents. First action: `pwd && git rev-parse HEAD` equals the PIN.

The defect just fixed: {DEFECT_ONE_LINE}. Its anti-pattern (mechanism): {MECHANISM}. Its greppable signature(s): {SIGNATURES}. The fix diff to learn the shape from: `git show {FIX_SHA} -- {FIX_PATHS}`.

Sweep the repo's OWN code only — `scripts/`, `proofs/`, `spikes/`, `tests/`, `.claude/hooks/`, `harness-ports/` — never `.claude/skills`, `.agents/`, `sandbox-kit/`, `graft/`, `wiki/`. Use `rg` for the literal signatures AND `graft ask` for the semantic form ("where else does <mechanism> happen"); paste the exact commands. Rate EVERY hit: DEFECT (the same failure mechanism applies here — say how it would fail) / BENIGN (pattern present, mechanism cannot apply — say why) / UNSURE. Report ALL hits; do not filter.

Report: the sweep table (file:line · matching line verbatim · rating · reason), the commands run, counts per rating, and NOT-done. A DEFECT with no reproducing thought is UNSURE.
