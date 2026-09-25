# Council brief: the System 1 (Jev) program — go ahead as planned? What exactly should it do first?

> STATUS 2026-09-25: stopped at the owner's word after Round 1 (AF-AP-203). The design audit JEV-FIT replaced it
> (`tasks/briefs/jev-laya/JEV-FIT-brief.md`; plan `docs/research/findings/jev-fit/PLAN-2026-09-25.md`).

Written 2026-09-25 03:4xZ by the coordinator for the owner's council (owner: "might be worth running a council on this one ... then an
interview afterwards to get the specifics down ... There's a few things that are worrying me, but I can't put my finger on it"). The
owner's own questions: what will the Jev models do; what do they do today; how will they save tokens; how will they improve our setup
(accuracy, quality, efficiency); how do the 35 decision points connect. Facts below are measured; each names its source file. Read the
sources when a claim matters to your argument.

## 1. What this is about, in plain words

- **The setup.** A coordinator model (Claude, "System 2") runs this build: it plans, writes briefs, dispatches agents, reviews their work,
  commits and pushes. Hooks and scripts gate its actions deterministically (commit gates, a push gate, a stop gate). Build and verify
  lanes run on the owner's PC with a local Qwen3.8-27B on an RTX 3090 (vLLM). The product being built, the "agent factory", is meant to
  run the same workflows and tools for other users later.
- **A Jev** is a small model that answers ONE typed question with probabilities: yes/no, a choice among fixed options, or a score. It
  writes no free text. Project rule: a Jev never decides a gate (no LLM judge in the gate spine); it can warn, rank, route or point.
- **The two candidate Jevs.** Laya (0.4B; reads one block of 512 to 1,024 tokens; about 1 s per question on CPU). An RWKV-7 student
  (0.4B, from the G0 checkpoint): its fixed-size recurrent state can read a whole session as a stream; on the 3090 it read 61,440 tokens
  in 1.17 s and answered a question from a copied state in about 0.046 s
  (`docs/research/findings/j2b-variants/rwkv7-g0/2026-09-24-window2/README.md`). A teacher (Qwen3.8-27B through simple-jev) may label
  examples that have no recorded answer.
- **The owner's direction** (`docs/08_DECISION_LOG.md` D-084, D-086): our own session records are the primary training data ("3 birds,
  1 stone": better data, better tools for this session, and the factory reuses the same workflows); by the end, all session data should
  be usable, because the RWKV version will process session data alongside Laya.

## 2. CURRENT-STATE CAPABILITY LEDGER (2026-09-25 03:4xZ)

| State | Item | Source |
|---|---|---|
| Proven live | RWKV-7 G0 long-input mechanics on the 3090 (vLLM stopped during that GPU window) | `docs/research/findings/j2b-variants/rwkv7-g0/2026-09-24-window2/README.md` |
| Proven live | The direct vLLM token-id path for the Qwen teacher, exact against the prompt compiler (D-082) | `docs/research/findings/j2b-variants/qwen27b/TRANSPORT-2026-09-24.md` |
| Built, never used in daily work | A Laya endpoint on the PC (2 requests answered in 16 hours, both a smoke test); nothing reads a Jev answer in daily work | `docs/research/findings/JEV-LEVERAGE-AUDIT-2026-09-24.md` section 1 |
| Built, never used | `scripts/decide-harvest` (the decision ledger): no consumer | same, item 3 |
| Built, pending verify | Dataset v2: 6,196 examples, 5,301 labels taken from answers our records hold (the verifier's class of a finding; the registry rows an incident or commit cites) | `docs/research/findings/laya-ft-labels/2026-09-25-recorded/summary.json`, `tasks/briefs/jev-laya/DSV2-report.md` |
| Rejected | Laya fine-tuned on 1,788 OpenJev-teacher labels: failed every KC-J3 line; the labels were worse than trivial baselines (finding class 38/86 vs the majority class's 49/86) | `docs/research/findings/laya-ft-data/INTERNAL-LABELS-2026-09-25.md`, D-083 |
| Rejected | RWKV-7 G0 zero-shot on the J2 test: failed every KC-J3 line | the window-2 README |
| Ruled out | MoJev (a 16k-token scorer) as a whole-session reader | `docs/research/findings/MOJEV-AUDIT-2026-09-24.md` |
| In progress | QJ2: the Qwen teacher's J2 score (a PC lane running since 00:35Z) | `tasks/briefs/pc/pc-qj2.md` |
| In progress | SESSION-EXPORT: every transcript as a scrubbed stream of calls and results (paused at a container restart; held for this council) | `tasks/briefs/jev-laya/SESSION-EXPORT-brief.md` |
| Absent | Any Jev wired into a hook, gate or script | JEV-LEVERAGE |
| Absent | A training pipeline for the RWKV student on streams | — |
| Absent | Any measured token saving or quality gain from a Jev | — |
| Absent | RWKV running on the GPU beside live vLLM lanes (contention not measured) | JEV-MAP section 3 |
| Absent | A held-out test for any decision type beyond J2's three (anti-pattern match, finding class, blocking) | — |

## 3. The 35 decision points (JEV-MAP, `docs/research/findings/laya-ft-data/JEV-INTEGRATION-MAP-2026-09-25.md`)

Grouped by where they would sit:
- **Before a tool call (PreToolUse), D01-D08:** will this Bash call fail; will the harness block it; will it be denied; will this Edit
  apply; does it need a Read first; will the search intercept stop it; is this Read redundant; will this test run be green.
- **After a tool call (PostToolUse), D09-D12:** which known error family; which anti-pattern rows an edit hunk resembles (202 registry
  rows); which chunks of a large output to keep; was the file changed outside the model.
- **At a turn's end and a prompt's start, D13-D17:** will the stop check fire; bake a lesson or not; which wiki or registry section the
  turn will need; how the owner will answer; which files and tasks matter after a context compaction.
- **Commit, push and CI, D18-D21:** will the commit pass its gates; will the push go; what will the CI gate say; will CI pass.
- **Dispatch and lanes, D22-D26:** will a background command or an agent succeed; how will a PC lane end; is a lane stuck, looping or
  starved; which agent type and model tier.
- **Verify lane and harvest, D27-D32:** the gate recommendation; a finding's class; a repair round; one model or a switch; a refusal;
  the registry class of a defect.
- **The factory's runtime, D33-D35:** an advisory note on a Hermes tool call; dream-phase triage; is a Hermes lane done, stuck or failing.

## 4. Measured facts the panel should weigh

- **Base rates are lopsided:** 97.6% of Bash calls exit 0 (33,454 of 34,272); 4,108 of 4,173 edits apply; 704 of 965 turn ends pass
  the stop check (`docs/research/findings/laya-ft-data/SESSION-DECISIONS-2026-09-25.md`).
- **The stream often holds the cause** (JEV-MAP section 2, a frozen snapshot of 298 files): a re-run test repeats its outcome 86 of 89
  times with no write in between, 60 of 104 with one; an "unpushed" stop block follows a commit since the last push 17 of 18 times;
  10 of 13 failed agents had a sibling fail in the prior 15 minutes, against 0 of 215 completed agents.
- **Labels can lie:** 887 of 938 red test runs still exit 0 (piped output); 18 of 93 verifiers wrote their recommendation into a file
  before their final message (the answer sits in the input unless the example is cut before it); 126 anti-pattern examples carry an
  unmasked registry id.
- **Recorded behaviour is not always right behaviour:** 82 agent dispatches omitted the model (a known habit, against a written rule);
  the coordinator misjudged the session data's value once today and the owner corrected it within the hour (D-086).
- **Context size:** a median of 785,712 tokens of API context at each of 126 compactions; the main session is about 20.1M tokens.
- **Latency:** a PC round trip took 0.62 s and 1.64 s (two samples); the median gap between session records is 1.0 s.
- **Label counts where they exist:** anti-pattern match 3,649 labeled (226 yes); finding class 826; blocking 826 (77 yes).

## 5. The owner's unnamed worries — try to name them

Candidates the coordinator sees (not a limit; find better ones):
1. A feedback loop: a model trained on our sessions then shapes our sessions, which become its next training data.
2. Labels record what happened, not what should have happened.
3. Base-rate traps: "always fine" scores 97% and helps no one.
4. Complexity on the hot path: each hook integration adds latency and new ways to fail.
5. GPU contention with the vLLM lanes the build depends on.
6. Privacy and secrets in a full session export.
7. Evaluation coverage: 3 of 35 decision types have a held-out test.
8. Sunk cost and momentum: many audits, lanes and findings, and no integrated value yet.

## 6. What the verdict must give

A go, a no-go or a changed plan; the first one to three decision points to build, and why; the case for token savings and for quality,
each with how it will be MEASURED against a baseline; kill criteria; and what to stop doing.
