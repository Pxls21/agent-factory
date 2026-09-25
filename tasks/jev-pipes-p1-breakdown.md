# Task breakdown: Jev pipeline P1, the jev-pruner at our scale (2026-09-25)

> **STATUS 2026-09-25 08:2xZ:** P1-1 to P1-4 landed (the P1 harvest commit); the replay verdict is FAIL (0 pruned of 3,153; `docs/research/findings/jev-pipes/P1-replay-2026-09-25.md`). P1-5, the verify round, is owed (task #260). P1-6 is not taken (FAIL).

Source: the seed `seeds/seed-jev-pipes-p1-v1.yaml` (Ouroboros seed_5aa221965993 from interview `interview_20260925_043820`,
ambiguity 0.12), the owner's direction D-087, and `docs/research/findings/jev-fit/PLAN-2026-09-25.md` (version 2, pipeline P1).
The seed is the contract; this file is the decomposition.

## Increments

| # | Increment | Task | Lane | Done when |
|---|---|---|---|---|
| P1-1 | Vendor the jev-pruner at `vendor/jev-pruner/` (commit 47d017c, MIT, provenance, `upstream.lock.yaml`), plus one local change: a lower floor only through an explicit option, default unchanged | #231 | sandbox build lane (brief `tasks/briefs/jev-pipes/P1-brief.md`) | AC3 passes; the default floor test passes |
| P1-2 | The replay harness `scripts/jev_pipes/replay_pruner.py` with a Node bridge to the vendored `trimOutput`, the decision log, the accounting and the one-command verdict | #231 | same lane | AC1 prints PASS or FAIL |
| P1-3 | Tests: recorded scorer answers, the accounting fixture, fail-open for every trip condition, the floor option | #231 | same lane | AC2 and AC5 pass, twice |
| P1-4 | The replay run and the committed report `docs/research/findings/jev-pipes/P1-replay-2026-09-25.md` | #231 | same lane | AC4: counts, rates, verdict, NOT-run |
| P1-5 | VERIFY-P1: an independent adversarial round on the harness, tests and report | #260 | sandbox verifier | AC7: a gate recommendation recorded |
| P1-6 | Only on PASS: P1 goes live in the hook (the vendored pruner installed at the new floor, extended to Read, Grep and agent hand-backs, with the present step) | #261 | a new brief after the verdict | the live miss rate and savings measured |

## Pinned decisions (with the rejected alternative)

- **Run the pruner's own code** (vendored, called through its exported `trimOutput` with an injected scorer). Rejected: rewriting its
  chunking and keep rules in Python, which would be a mirror of the thing under test (AF-AP-42).
- **The floor drops only through an explicit option**, default unchanged. Rejected: changing `MIN_OUTPUT_TOKENS`, which would change
  the installed plugin for every caller.
- **Bash results are the verdict set** (the pruner's domain); Read and Grep are a secondary table. Rejected: one verdict over all
  tools, since the pruner's rules target command output.
- **A deterministic stratified sample of at least 300 results first**, the full set only if throughput allows within 4 hours.
  Rejected: the full 3,688 up front, with a 2-thread CPU scorer of unmeasured speed.
- **A miss is measured, not judged:** a dropped chunk's distinctive tokens used in the next 20 tool inputs or assistant texts, or a
  re-run of the same command within 20 calls. Rejected: an LLM deciding whether a chunk was needed (no LLM judge in a gate).
- **Scoring on the sandbox's CPU Laya server only.** No GPU beside vLLM (the seed's constraint; a GPU scorer waits for an
  owner-approved window).

## Order

P1-1 to P1-4 run as one lane with one boundary. P1-5 follows the harvest. P1-6 is written only after the verdict. The session
export (task #252) runs in parallel: its stream feeds later pipelines and the RWKV student (D-086).
