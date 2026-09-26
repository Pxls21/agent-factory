# Interference Search: an assessment for Agent Factory (2026-09-26 10:4xZ)

Asked by the owner (chat, 2026-09-26): "I found this interesting repo that we might be able to leverage in our setup",
https://github.com/Badtheorylabs/interference-search. Read by the coordinator at commit afedcc2 (2026-09-25 23:09 +0100, a
shallow read-only clone); nothing of it was run here.

## What it is

A research repo (one author, Bad Theory Labs, Apache-2.0 with a NOTICE file, first public commit 2026-09-25). The method: keep
explicit states instead of one line of reasoning; each round, expand every live state, let the environment execute the moves,
merge the states that share a key (their parents' votes add up), rank what is left with a judge, and keep the best `width`
for the next round. `interference_search/core.py` is 112 lines: a beam search with a transposition table and vote pooling,
plus a one-line baseline over the same parts. Dependencies: torch and numpy; the language-model experiments need Apple MLX.

## What it shows (its own numbers, one seed each)

- Countdown, 30 hard four-number problems: 30/30 with a 100k-parameter trained judge in 3 sequential steps, against 21/30 for
  the same judge in one line and 3/30 for Qwen3-1.7B thinking in text. Countdown has an exact solver, so every state can be
  labelled without a model: the judge learns from that oracle.
- Code, 30 MBPP problems Qwen3-1.7B fails first: 9/30 against 8/30 for best-of-N, which the author calls within noise. 83% of
  the programs the model wrote repeated behaviour already seen.
- Negative results kept: listing failed attempts in the prompt made the model repeat them more; resampling the same context
  regenerated the same line.

## Where it could fit here

1. **The Harness Foundry** (`docs/10_HARNESS_FOUNDRY.md`, a later phase): generating and comparing harness candidates. Merging
   candidates that behave the same on the evaluation suite, and advancing the best few per round, is a clean shape for that
   loop, and its judge can be the deterministic evaluator (standing rule 12).
2. **A question for our build lanes, not code to adopt:** do our local-model repair rounds repeat behaviour they have already
   shown, and do the "prior mistakes as do-nots" lines in briefs cause repeats? Measurable from the lane transcripts.

## What stops a direct use

- `interference_search/program_domain.py` runs model-written programs with `subprocess.run([sys.executable, "-c", RUNNER])`,
  a 2 s alarm and a 10 s timeout: no network cut, no filesystem limit, the same user. Standing rules 9 and 11 require the
  fail-closed policy gate and gVisor containment; a Foundry use supplies its own execution (the evaluation sandbox, docs/10).
- The language-model path is MLX (Apple silicon); ours is vLLM behind OmniRoute (standing rule 3).
- The evidence is thin: one seed, 30 problems per benchmark, the code result within noise, no agent-task results yet (the
  author's next step is SWE-bench and Terminal-Bench).

## Recommendation

Record it as an open implementation choice for the Foundry (`docs/08_DECISION_LOG.md`, X-008), pinned at afedcc2 in any
later use (standing rule 13; its LICENSE and NOTICE go into the third-party notices). No build now: Stage 0's closure comes
first. Cheap checks that need no decision: reproduce its Countdown numbers on the PC in its own Docker image (its
`scripts/reproduce_countdown.sh`, about 10 minutes on a CPU), and measure repeated behaviour in our lanes' repair rounds.
