# MoJev as Laya's long-context partner: findings and options (2026-09-24)

> Coordinator synthesis for task #210 (owner ask 2026-09-24). Evidence: `docs/research/findings/jev-audit/mojev-evidence.md`
> (commit 7ca569a; 250 rows; a static reading of MoLeMo-Lab/mojev at a74d58c and of the Hub snapshot at revision 0c8695b;
> nothing from the repo was executed). Numbers like (2.12) point to rows in that file. Measured by the coordinator on
> 2026-09-24 03:1xZ: the hook facts in §7. **Nothing here is built.** The owner decides (§6).

## 1. The answer

- **MoJev does not read and summarize. It scores.** You give it a state (text) and typed questions with candidate
  answers. It returns a probability for each candidate. It writes no text (`output_tokens: 0`, 1.25).
- **The "1 million tokens" belongs to the Qwen3.5 backbone, not to MoJev.** MoJev was trained with the state cut at
  16,384 tokens. Nothing is measured above that, and no YaRN configuration is published (2.11, 2.18-2.20). A longer
  state is cut silently: no refusal and no flag in the response (2.12-2.13).
- **A whole session does not fit.** Our sessions reach about 787k tokens before each compaction (median over 112
  compactions, 10d). That is 48 times MoJev's trained window. At that length the packing mask alone needs about 2.5 TB
  (4·L² bytes, 2.17). A whole Hermes lane does not fit either: its 57-90k-token prompts need up to 32 GB of mask.
- **What does fit: typed questions over a state of up to 16k tokens.** That is 32 times Laya's 512-token window. It
  suits two of the owner's ideas well: bug localization (pick the faulty function among candidates) and a context
  manager (rank candidate snippets). It suits a third in part: hygiene nudges. In every case MoJev ranks or picks. It
  never writes and never decides a gate.
- **Our own reminder and context hooks do not fire in this session (§7).** The context-manager and hygiene ideas have
  no working seam today.
- **Recommendation:** fix the hooks first (no model needed; the owner picks which). Then option B (§6): one bounded
  probe on the PC's CPU, bug localization first, because it has a real independent oracle: the fix commit.

## 2. What MoJev is

| Aspect | Fact | Rows |
|---|---|---|
| Kind | A typed-decision scorer on the TypeSafe `system_one` wire shape (`noul`, `choice`, `score`). Each question becomes one softmax over the candidates the caller supplies. No text generation. The request and response are close to our Laya endpoint's; a thin adapter would bridge the differences (confidence fields, error shape, no per-chunk fan-out). | 1.25, 6.16-6.26 |
| Size | Qwen3.5-0.8B base (Apache-2.0), 854,036,544 parameters; bf16 encoder, fp32 readout. | §1 |
| Layers | 24: 18 Gated DeltaNet (linear attention) and 6 full attention. | 1.16-1.17 |
| Context | Trained at a 16,384-token state. The config has `rope_type: default` and no YaRN. No code checks an upper bound. An over-long state is truncated silently; which end is kept is not settled (probably the start). | 2.2, 2.10-2.14, 2.18-2.20 |
| Packing | Packed input = state + one prompt of at most 32 tokens per question + every candidate's tokens, untruncated. No cap on packed length, candidate count or question count. The mask is built dense: 4·L² bytes for its float32 copy alone, and the code builds two more L² tensors. | 2.16-2.17, 13.25, 13.27 |
| Candidates | Trained with at most 16 per question by default (mean 4.7; 0.4% of rows have more than 16; sets over 64 are dropped at conversion). | 13.26 |
| Independence | The docstrings say a candidate never sees another candidate. The tree mask reaches only the 6 full-attention layers; the 18 linear layers get no mask. So candidate order can move scores. The code sorts candidates by text to stay deterministic. | 1.15-1.17 |
| Accuracy claim | 93.23% top-1 and 0.79% ECE on 12,000 rows of their own synthetic mixture. Marked `verified: false`. No committed outputs. Three different statements of which split was used. | 4.1-4.4 |
| Calibration | Per-cardinality temperatures exist, but nothing calls them. The server returns a plain softmax. | 1.27 |
| Training data | 18 synthetic Open-Jev generators (games, navigation, documents, agent traces, palettes). No code, stack-trace or program-repair domain. | 8.1-8.2, 11.25-11.28 |
| Speed | "34.5 ms" per packed batch of 8 and "77 ms" HTTP p50. No hardware, context length or candidate count is stated for any number. | 5.1-5.11 |
| Server | wsgiref, one request at a time. No body cap, no timeouts. The API key is off by default and compared as a plain string. Any host is accepted. The image loader opens any path written after `<\|image_pad\|>`. Errors return the exception text. `trust_remote_code` for the processor. Hub loads are unpinned. | 6.1-6.13, 7.13 |
| Tests | No test builds a linear-attention layer. No HTTP test. No long-context test. | 9.1 |
| Licence | Code MIT. The checkpoint falls under Qwen's Apache-2.0, while the card's YAML says MIT (a contradiction). Dataset asset licences are unstated. | 1.3, 8.6 |

## 3. Fit, per owner idea

### 3a. Laya's long-context partner: a whole session or a Hermes lane in one go

**Verdict: no, as asked.** Three independent reasons. It writes nothing, so it cannot summarize. It was trained and
measured only up to 16k tokens. The dense mask makes long packs impossible on our hardware.

What can work: split a session into windows of at most 16k tokens, ask each window narrow typed questions ("does this
window record a defect with no registry row?"), and combine the answers with code. The Laya findings already name this
chunk-and-aggregate pattern for narrow per-chunk signals (13.22). It is a different product from "reads the whole
session": it cannot link a cause in window 3 to an effect in window 40.

A tiering that does make sense: Laya (0.4B, 512 tokens, about 1 s per question on CPU, measured, 10.9) for per-block
judgments; MoJev (0.85B, up to 16k tokens) for the rarer questions whose evidence does not fit in 512 tokens.

### 3b. Bug localization

**Fits the shape.** The state holds the failing test's output, the trace and the relevant code-intel sections (up to
16k tokens). The candidates are the functions the trace names or the recent diff touched (at most 16). The question:
"which of these functions holds the defect?".

**Why it is the best first probe:** it has an independent, deterministic oracle, the function the fix commit changed.
Labels can be mined from git history instead of invented. The incident log already records 14 defects with both the
failure and the fix (11.11-11.24). That is a seed set, far short of the at least 100 blind labels the Laya council
requires before any claim (13.12, Gate 1).

**Caveats:** MoJev never saw code or traces in training (11.25-11.28), so zero-shot may fail. The baseline to beat is
deterministic: the deepest project frame in the traceback, and the most recently changed function. The code-intel pack
carries no failure output today (11a), so the input has to be built.

### 3c. Workflow hygiene: when to update the wiki, prune, bake a skill, add a registry row

**The premise needs a correction first.** The reminder that follows almost every turn ("There are untracked files …")
comes from the harness's own Stop hook, `~/.claude/stop-hook-git-check.sh` (834 recorded Stop runs). Our turn-end
retro checklist has not fired once in this session's main transcript (0 of 834, 12.14). See §7.

A model trigger fits as three yes/no questions per landed batch, over the batch's diff and commit message (up to 16k
tokens): "needs a wiki delta?", "needs a registry row?", "needs a skill bake?". Advisory nudges only (KC-J1): a nudge
never blocks and never writes.

**The hard part is the oracle.** Labels mined from our own past batches would teach the model our forgetting, the very
thing the owner wants fixed. It needs labels a person sets on a sample of batches. A cheaper first step: the
deterministic trigger we already have (the post-commit wiki-stale marker, 12.7-12.10), once the hook that reads it runs.

### 3d. Context manager: Laya finds what to search, MoJev picks what to show

**The strongest fit.** Picking among candidates against a long shared state is MoJev's native job. Shape: deterministic
retrieval (lexical match, graft, the wiki index) produces at most 16 candidate snippets; MoJev ranks them against the
current task state (the recent turns, up to 16k tokens); the top few are injected. Retrieval-then-rank matches D-046's
two-stage design for large option sets.

Rules it must keep: **additive only** (the injection adds a pointer or an excerpt and hides nothing, so the needle-loss
barrier KC-J5 is not engaged); fail open with a visible marker; the calibration state shown with every score (13.13).

**Two gaps before it can help.** First, the seam does not fire. The council rejected model ranking for injected
context because "a deterministic lexical score already does it" (`wiki-context.py`, 13.15), and that script has not run
in this session's main transcript (§7). Second, nothing in MoJev's evidence covers retrieval or reranking (13.23), so
it needs our own labels. At 16k tokens on CPU it is not a per-prompt tool (§4, item 3); at 2-4k it may be.

## 4. Hard limits and risks

1. **Context.** Trained at 16k, silent truncation, nothing measured above 16k, no YaRN configuration published.
2. **Mask memory** (computed, 4·L² bytes for the float32 copy alone): 1.07 GB at 16,384 tokens; 32.4 GB at 90k;
   275 GB at 262,144; about 2.5 TB at 787k.
3. **Compute on our hardware.** The 3090 is held by the vLLM `qwen` container that runs our build and verify lanes
   (10.13-10.14); freeing GPU memory is the owner's call. So MoJev would run on the PC's CPU (Ryzen 5 5600X, AVX2,
   125 GB RAM). Upstream never tested CPU bf16; fp32 weights are about 3.4 GB. Whether the Gated DeltaNet layers have a
   fast CPU path is unknown. **Estimate, not measured:** about a minute per 16k-token decision and about 20 s at 4k,
   from our measured Laya CPU rate (1.0-1.25 s per question for a 0.4B model at up to 512 tokens, 10.9) scaled by
   parameters and tokens. Gate 0 measures it.
4. **Accuracy is unproven for us.** Their number is on their own synthetic data, unverified, with contradicting split
   statements, and their training has no code domain.
5. **Candidate order.** The linear-attention layers see candidates in sequence. Our wrapper must fix the order, and the
   probe must measure order sensitivity.
6. **Server.** We would not run theirs. Our own loopback wrapper (`scripts/laya_systemone_server.py` already has an
   8 MiB body cap, a loopback-only bind and a lock around the forward pass, 6.25) plus: the image marker refused, a
   packed-length cap, a candidate cap, an offline pinned snapshot, and no `trust_remote_code` without a vetted pinned
   processor.
7. **Calibration.** We fit our own temperatures on our labels. Their server applies none.
8. **Screen.** Our never-a-gate screen does not match `mojev`, `MoJev` or `PackedScorer` (10.5). Its vocabulary must
   grow before any MoJev code enters the tree.
9. **Licence.** Fine for internal use. Settle the checkpoint licence before redistributing anything.

## 5. Constraints any adoption keeps

- No MoJev value reaches a gate, a verdict, the promotion service or `pre_tool_call` (KC-J1). A MoJev score is never
  the sole evidence for a registry row or a verifier class (KC-J1b).
- Additive only; nothing is hidden (KC-J5).
- Self-hosted on the PC, loopback only. The model revision and file hashes pinned in `upstream.lock.yaml` (rule 13).
  Offline loading.
- Errors never hidden; a fail-open marker on any failure.
- Measure before use: Gate 0 (latency and memory on the PC), Gate 1 (at least 100 blind labels; beat the majority
  baseline and a deterministic heuristic).
- It stands where Laya stands: a local scorer outside OmniRoute. That standing needs the same answer as Laya's (D-058
  notes the tension with the dream phase's §7).

## 6. Options for the owner

- **A. Park MoJev.** Fix the hooks (§7). Revisit when someone publishes a measured long-context result.
- **B. (Recommended) A bounded probe, after the hook fix, in this order:**
  1. Pin the snapshot (revision + sha256) and grow the never-a-gate screen's vocabulary.
  2. Gate 0 on the PC's CPU through our wrapper: latency and peak memory at 2k, 4k, 8k and 16k-token states with 5,
     10 and 16 candidates; the truncation check and the order-sensitivity check.
  3. Gate 1 on bug localization: mine at least 100 cases (failing test + trace → the function the fix changed) from our
     history. Score MoJev zero-shot against the deepest-frame baseline and a majority baseline.
  4. Only if it beats both: a shadow context-manager ranker on the same service (additive and logged; nothing injected
     until its own labels show it helps).

  Needs from the owner: a yes to running MoJev's code and weights on the PC (the sandbox refuses to execute external
  repo code, and the PC is the owner's machine), and CPU time there. No GPU unless the owner chooses to free it.
- **C. Wait** for MoLeMo-Lab, or anyone, to publish a measured long-context result. Then revisit.

## 7. Side finding: our project hooks do not fire in this session

- The five project hooks (session start, per-prompt wiki excerpts, edit snapshot, graft nag, turn-end retro) are
  registered in `agent-factory/.claude/settings.json` as `$CLAUDE_PROJECT_DIR/.claude/hooks/…`. That file loads only
  when the session is rooted in `agent-factory`.
- This session is rooted in `/home/user`: its transcript lives under `~/.claude/projects/-home-user/`, and
  `/home/user/.claude/` does not exist (measured 2026-09-24 03:1xZ).
- In the `/home/user`-rooted transcript: 834 Stop runs, none of them ours; no UserPromptSubmit hook record; zero
  `wiki-context.py` trailers (12.14, 13.11). In the slice of the same session that ran rooted in `agent-factory`
  (2026-09-02 to 2026-09-22, 1.58 MB, counted 03:1xZ), they did fire: SessionStart 4, UserPromptSubmit 2, turn-end
  retro 3.
- Two of the five (`edit-snapshot.py`, `graft-first-nag.py`) print plain text and exit 0. Under the harness's hook
  contract that output reaches the transcript view, not the model. The user-scope hooks that do reach the model use the
  JSON `additionalContext` form (66 recorded, 13.11). Not probed live.
- So the per-turn reminder is the harness's git check, and the context and hygiene machinery that CLAUDE.md describes
  has been silent for most of this session. The fix is deterministic and needs no model. Restored hooks cost tokens,
  so which ones to restore is the owner's choice (incident entry 2026-09-24 03:2xZ, AF-AP-172).
