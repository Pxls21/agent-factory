---
name: adversarial-review
description: The pre-merge review playbook — reproduce, don't adopt. Use for any branch review; defines the minimum attack set, the verdict format, and the honesty requirements for what was and wasn't reproduced.
---

> **HARNESS PORT.** This copy is read by Codex CLI (`.agents/skills/`) and by Hermes
> (via `skills.external_dirs`). It is the same protocol as `.claude/skills/adversarial-review/SKILL.md`;
> only lines naming a Claude-Code-specific mechanism were reworded — see `docs/HARNESS-PORTS.md`.
> "the project instructions file" = `AGENTS.md` on Codex, `.hermes.md` on Hermes.
> Model-tier names below ("Fable light", "Opus 5 lane") are PROTOCOL LABELS, not routing
> instructions: these harnesses run ONE model. Where the protocol calls for an independent
> verifier, hand the work BACK to the sandbox lane — never self-accept.

# Adversarial review playbook

Your job is to try to make the change fail, not to confirm it works. The author's report is a list of claims; reproduce every claim you rely on.

## Minimum attack set

1. **Merge reality.** Fetch, then `merge-tree` against the LIVE tip (it moves during long reviews — re-check before verdict). Check file overlap with recent history for *semantic* conflicts, not just textual ones.
2. **Fresh-binary gates.** Delete the test executables, rebuild, confirm exit code AND new mtimes, then run the suites yourself. Beware false greens: a test runner whose filter matches nothing can exit 0 — verify the suite ran by its test counts.
3. **Red-green.** Reproduce the red state for new tests (revert the change, keep the tests, observe the failure). A test that was never red is a claim, not a proof. Check for tautologies — a control assertion that stays green in the red build.
4. **Hostile inputs.** Anything parsing external or untrusted bytes gets crafted-input attacks — overflowed length fields, truncation at every structural boundary, declared-size bombs, wrong-type fields — run under a watchdog. A hang is a finding, not a timeout.
5. **Threading and lifetime.** For concurrency changes: who owns destruction; what happens on the cancel, shutdown, and error paths; can a slot or lock leak or double-release; does any worker ever wait on work scheduled to its own pool; does anything publish state outside the lock its reader holds.
6. **Stale-context sweep.** Grep for comments and docs the diff falsifies. A correct fix sitting next to a contradicting comment is a future bug — require the comment fixed in the same change.
7. **Excuse verification.** When the author skipped something ("no test target exists", "not reproducible"), verify the excuse against the build system or the repro before accepting it.
8. **Deletions review.** Every removed line justified; no dead code left behind; no defense removed without an equivalent replacement.
9. **Evidence audit.** Claims must be tiered verified/inferred/assumed; measurements must exist as artifacts — spot-check that cited artifacts exist and say what the report says they say.
10. **Devex-breakage sweep** (from vendored thermo-nuclear-review, 2026-08-25). Does the diff change how the code is RUN or BUILT: secret-read locations, env var names/additions, port/network remaps, new required scripts, launcher/wrapper contract changes? In this repo that includes any flag whose live value rides the untracked PC wrapper — a rename here silently sheds the deployment (the TRADING_GPU_SIM/TRADING_OTEL flag-shedding class).
11. **Feature-gate leak check** (same source). Any capability meant to sit behind a flag/gate must be proven unreachable with the gate off — grep is not proof; demand the flag-off identity test or a runtime reachability trace (the dark-flag byte-identity discipline generalized to review time).

## Verdict

MERGE-READY or NOT-READY, with numbered findings tagged [BLOCKER] / [SHOULD-FIX] / [NIT], each with file:line and a minimal fix. State explicitly: what you reproduced vs reviewed statically, and what you deliberately skipped and why. If your verdict depends on something you did not reproduce, say so in the verdict line itself.
