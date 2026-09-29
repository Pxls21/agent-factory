> Coordinator note (2026-09-29 02:1xZ): the report of record, extracted by `scripts/stack.py harvest` (the lane's report-file write is refused for subagents). Served model: claude-opus-5-5 on all 495 assistant records, 0 refusal stops. `report_lint` reads 4 MISS, none an error in the report: each cites the Qwen3.8-27B model card's `README.md` on Hugging Face (lines 53, 177-180, 507-510, 514-558), which the lint resolves against this repository's README.

# K0-COMPACTION-POINT report (task #352, D-106): published evidence on how each model's work changes as the input grows

This is evidence only. It contains no verdict and no recommended compaction point; the choice stays in the main loop (design §10.2, R-A).

- **Lane:** sandbox EXPLORE (evidence-gatherer), model `claude-opus-5-5`.
- **Run:** 2026-09-29, 01:34:33Z to 02:14:02Z (`date -u`).
- **Brief:** `/home/user/agent-factory/tasks/briefs/jev-trim/K0-COMPACTION-POINT-brief.md`, now committed in 0749fe5 ("D-106 recorded (the owner re-scopes D-105); T1-LCM-AUDIT and VERIFY-SCRUB2-R1 round 3 home; K0 dispatched", 01:42:49Z).
- **Boundary kept:**
  - Read-only. No git writes, no PC bridge, no subagents, no outward action.
  - No secret source read. The premise's `env | grep -o` printed only `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`.
  - Scratch only under `/tmp/k0-ctx/`, removed at 02:10:37Z; `ls` then gave `ls: cannot access '/tmp/k0-ctx': No such file or directory`.
  - Nothing downloaded was run. PDFs, HTML and one site's JS bundles were read as text. The only code run was my own stdlib readers (PDF text and figure export, HTML-to-text) and the repo's `scripts/premise_block.sh`.
- **Main tree:** I wrote nothing there. It shows other lanes' modified proof files and a new untracked `tasks/briefs/jev-trim/K1-COMPACTION-LOSS-brief.md`; neither is mine.
- **S1 injections:** three received, each rated in its own line of text: s1-5a8f4bc3 rel=2 use=1; s1-059dbc1f rel=1 use=2; s1-bef081ff rel=1 use=0.

---

## 0. PREMISE re-run

Run at 01:35:00Z. HEAD was the local commit "I59-F landing staged (task #335): the S0-05 re-capture waits for the owner's sudo; live-state". The commands were fed verbatim to `bash scripts/premise_block.sh`. The output matches the brief's block, 9 of 9 lines.

```
$ git merge-base --is-ancestor 0e6d4a1 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ grep -n '^model:' .claude/agents/evidence-gatherer.md .claude/agents/code-implementer.md .claude/agents/adversarial-verifier.md
.claude/agents/evidence-gatherer.md:4:model: claude-opus-5-5
.claude/agents/code-implementer.md:4:model: claude-opus-5-5
.claude/agents/adversarial-verifier.md:4:model: claude-opus-5-5
$ grep -c '^| D-106 |' docs/08_DECISION_LOG.md
1
$ grep -o '^| D-097 | OWNER DIRECTION 2026-09-26 03:3xZ.\{0,150\}' docs/08_DECISION_LOG.md
| D-097 | OWNER DIRECTION 2026-09-26 03:3xZ (chat, voice-typed; transcript 03:32:41Z and 03:33:51Z): "im thinking to reduce the context to 131k instead of full 262k since 131k is a good sweet s
$ grep -n '^## 10\. \|^### 10\.2 ' docs/research/findings/jev-trim/D105-DESIGN-v1.md
235:## 10. D-106 (2026-09-29): the re-scope and the plan
251:### 10.2 Where to compact (task #352)
$ grep -n '^| A1.14 \|^| A1.15 ' docs/research/findings/jev-trim/TRIM-AUDIT-2026-09-28.md | cut -c1-40
70:| A1.14 | Auto-compaction window | Se
71:| A1.15 | Measured compaction point |
$ env | grep -o '^CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=[0-9]*'
CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=80
$ sha256sum tasks/briefs/jev-trim/k1_authoring_probe.py | cut -c1-16
a9bea1dbbd9c112a
$ ls /tmp/k0-ctx 2>&1 | head -1
ls: cannot access '/tmp/k0-ctx': No such file or directory
```

HEAD moved during the lane:
- 0749fe5 (01:42:49Z), then the local commits "Retro of the D-106 batch: …", "env-tool-quirks: a re-landed evidence set …", and "T0-REPLAY round 2 landed (task #346) …" (02:02:24Z).
- At 02:03:30Z, `git merge-base --is-ancestor 0e6d4a1 HEAD` still printed `PIN-is-an-ancestor-of-HEAD`.

---

## 1. How to read the tables

**Marks.**
- **SOLID:** I read it in the primary source: page or PDF text, a value printed on a figure, or JSON that the source's own site serves.
- **UNSURE:** a secondary source, a value read by eye from a line chart, a claim I could not open, or a mapping I derived.
- Quotes from pages first read through WebFetch were re-checked against the raw page with curl before they got SOLID.

**Who measured.**
- **vendor:** the model's maker.
- **independent:** a third party.
- **interested:** a third party measuring its own method against others.

**Token units differ across sources.** This matters for mapping any curve onto this session's ~784k.

| Unit | Who uses it | Ratio to o200k tokens on the same text (Context Arena "token efficiency", measured on MRCR text; SOLID) |
|---|---|---|
| Claude current tokenizer (Opus 4.7 and later, Sonnet 5.x, Fable 5/5.1; the docs say "introduced with Claude Opus 4.7") | this session's counts; Claude Code's 967K | 1.638 (Opus 5, Opus 4.8, Sonnet 5); 1.629 (Opus 4.7) |
| Claude older tokenizer | Opus 4.6, Sonnet 4.6, Haiku 4.5 | 1.131 |
| Qwen3.x tokenizer | Qwen lanes, vLLM `MAX_LEN` | 1.021 |
| o200k_base | MRCR bins, Context Arena bins | 1.0 |
| cl100k_base | AA-LCR (~100k per question) | not measured here |

The following is K0 arithmetic. It is UNSURE as a mapping, because the ratio was measured on MRCR's English chat text, not on code- or JSON-heavy transcripts.
- Claude-current tokens to o200k tokens:
  - 784,000 becomes about 478,632.
  - 500,000 becomes about 305,250.
  - 967,000 becomes about 590,354.
- MRCR bin edges, from o200k tokens to Claude-current tokens:
  - 131,072 becomes about 214,696.
  - 262,144 becomes about 429,392.
  - 524,288 becomes about 858,784.
  - 1,048,576 becomes about 1,717,567.
- In Qwen tokens, the 131,072 edge is about 133,825.

**PDFs.**
- Each PDF was downloaded to scratch, hashed with sha256, and read with my own stdlib text extractor. Figures were exported as PNG and viewed.
- Hashes (first 8 hex): Opus 5.5 card 7311c9c6; Opus 5 fed3c0e6; Fable 5.1 b0d59edc; Fable 5 d23b49f4; Opus 4.8 97f11ae3; Opus 4.7 a7729a0e; Opus 4.6 4db67c6b; LCM paper ff1d64c7 (the same file T1-LCM-AUDIT hashed).

**Context Arena** (`contextarena.ai/api/...`, fetched 01:48Z).
- Every row is MRCR v2 8-needle. The bins follow OpenAI's dataset card: "[4096, 8192], (8192, 16384], … (262144, 524288], (524288, 1048576]", counted in o200k_base over prompt plus answer, "100 samples per bin".
- The site's per-bin `n_tests` values are 80 to 236. The API response does not state run dates, providers or quantization.
- A null reasoning mode displays as "Reasoning: off".

---

## 2. Opus 5.5 (`claude-opus-5-5`) and its nearest measured siblings (S = sibling)

| # | Model | What was measured | Length points | Result | Source (where) | Date | By | Mark |
|---|---|---|---|---|---|---|---|---|
| O1 | Opus 5.5 | Spec | window 1M; output 128K | — | platform.claude.com/docs/en/models/overview; opus-5-5/overview.md:13 | fetched 01:46-01:51Z | vendor | SOLID |
| O2 | Opus 5.5 | Program Bench, 166 tasks, mini-SWE-agent, no 6-h limit | "episodes cover a range of context lengths up to the full 1M token window"; no per-length split | 91.2% (Fable 5.1 87.6%, Opus 5 85.4%) | Opus 5.5 system card §8.10.1, pp. 183-184 | 2026-09-22 | vendor | SOLID |
| O3 | Opus 5.5 | Capability table | "Context window sizes are evaluation dependent and do not exceed 1M tokens" | No MRCR, GraphWalks, needle, OOLONG or long-document QA row anywhere in the card (space-tolerant grep of the full text) | Table 8.1.A, p. 174 | 2026-09-22 | vendor | SOLID |
| O4 | Opus 5.5 | AA-LCR v1.1 | ~100k tokens per question | low 80.7, medium 84.3, high 82.7, xhigh 84.7, max 84.7 (runs labelled "Default Fallback") | artificialanalysis.ai model pages, embedded data (fetched 02:05Z) | release 2026-09-22 | independent | SOLID |
| O5 | Opus 5.5 | Launch post | — | No long-context statement found | anthropic.com/news/claude-opus-5-5 | 2026-09-22 | vendor | UNSURE (absence read through the WebFetch summarizer) |
| O6 | Opus 5 (S; the Opus 5.5 card calls Opus 5.5 "an upgrade to Claude Opus 5") | MRCR v2 8-needle | bins 8k, 16k, 32k, 64k, 128k, 256k, 512k; no 1M data | max: 98.7, 99.9, 99.3, 99.9, 91.3 [95% CI 85.6-96.1], 65.6 [57.7-73.0], 42.5 [36.3-48.4]; n = 80/80/136/85/103/141/236 | Context Arena API | run date not given | independent | SOLID |
| O7 | Opus 5 (S) | Program Bench, 5 episodes, each with "a fresh context budget of up to 1M tokens" | per episode | 83% after episode 1, 93% by episode 5. Opus 4.8: 80 to 90. Mythos 5: 84 to 93 | Opus 5 card §8.9.1, pp. 155-156 | 2026-07-24 | vendor | SOLID |
| O8 | Opus 5 (S) | AA-LCR v1.1 | ~100k | max 79.3 | AA leaderboard embedded data | — | independent | SOLID |
| O9 | Opus 4.8 (S) | GraphWalks F1. The card says "1M context subset results are not reproducible via the public API, as the problems exceed its 1M token limit" | 256K subset / 1M subset | Opus 4.8: BFS 85.9 / 68.1, Parents 99.3 / 83.3. Same table: Opus 4.7 76.9 / 40.3 and 93.6 / 56.6; Opus 4.6 61.1 / 16.3 and 95.4 / 48.6; GPT-5.5 73.7 / 45.4 and 90.1 / 58.5 | Opus 4.8 card §8.9, Table 8.9.A, p. 200 | 2026-05-28 (changelog 2026-06-03) | vendor | SOLID |
| O10 | Opus 4.8 (S) | MRCR v2 8-needle | 8k to 512k | max: 97.4, 96.1, 93.0, 90.7, 75.2 [66.3-82.8], 61.8 [53.5-69.6], 39.8 [33.9-46.2] | Context Arena API | — | independent | SOLID |
| O11 | Opus 4.7 (S; first model on the current tokenizer) | MRCR v2 8-needle. The card defines the bins: "256k … (128k, 256k] tokens, and 1M … (524k, 1024k]" | 256k / 1M | Opus 4.7 (max) 59.2 / 32.2. Opus 4.6 (64k extended thinking) 91.9 / 78.3. GPT-5.4 (xhigh) 79.3 / 36.6. Gemini-3.1-Pro 59.1 / 25.9 | Opus 4.7 card §8.7.2, Figs 8.7.2.A-B (values printed on bars), pp. 195-196 | 2026-04-16 | vendor; competitor values from Context Arena or self-reports | SOLID |
| O12 | Opus 4.7 (S) | GraphWalks | 256K subset; 256K-1M mix | BFS 76.91 (256K) and 58.6 (mix); Parents 93.57 and 75.1. The card says "half the problems exceed its 1M token limit" | p. 194 | 2026-04-16 | vendor | SOLID |
| O13 | Opus 4.7 (S) | MRCR v2 8-needle | 8k to 512k | xhigh: 89.0, 84.0, 46.3, 23.9, 0.8, 2.2, 8.6. high: 78.8, 86.4, 42.5, 30.8, 1.1, 1.4, 9.1. medium and low are similar. Reasoning off: 52.7 at 8k | Context Arena API | — | independent | SOLID |
| O14 | Opus 4.7 (S) | Truncation study. BABILong (0-32k splits) and GraphWalks BFS, keeping 100/75/50/25% of the context | retention fractions | BABILong, signal-aware: 0.725, 0.717, 0.713, 0.733; naive middle removal: 0.717, 0.562, 0.438, 0.283. GraphWalks, signal-aware: 0.701, 0.680, 0.680, 0.660; naive: 0.700, 0.509, 0.384, 0.293 | arXiv 2608.03297, Table 2 | 2026-08-04 | independent (1 author) | SOLID |
| O15 | Opus 4.6 (S) | MRCR v2 8-needle | 256K / 1M | 91.9 (64k thinking) and 93.0 (max) at 256K; 78.3 and 76.0 at 1M. On 1M the card says "not reproducible via the public API, as some problems exceed its 1M token limit. Performance on the <1M token subset is within 1pp". Sonnet 4.5 (64k): 10.8 / 18.5 | Opus 4.6 card §2.18, Table 2.18.A and Fig 2.18.1.A, pp. 30-32 | Feb 2026 (changelog 2026-02-06) | vendor | SOLID |
| O16 | Opus 4.6 (S) | GraphWalks. "1M" here means the whole 1M variant: 100 problems at 256k plus 100 at 1024k | 1M variant / 256K subset | BFS 41.2 (64k) and 38.7 (max) / 61.5 and 61.1. Parents 71.1 and 72.0 / 95.1 and 95.4 | pp. 30-32 | Feb 2026 | vendor | SOLID |
| O17 | Opus 4.6 (S) | MRCR v2 8-needle | 8k to 512k | high: 98.2, 84.4, 86.2, 74.3, 68.1, 69.1, 54.3. medium: 99.3, 89.2, 87.4, 79.9, 72.5, 71.8, 48.9. Reasoning off: 81.6 to 28.2 | Context Arena API | — | independent | SOLID |
| O18 | Opus 4.6 (S), raw with no scaffold | OOLONG (aggregation task), decontaminated | 8K, 16K, 32K, 65K, 131K, 256K, 512K, 1M | About 83, 59, 39, 48, 42, 48, 28, 18 (read by eye from Fig. 6). Text: "steep degradation beyond 65K tokens, falling below 20 at the largest context lengths" | LCM paper (Ehrlich and Blackman), pp. 7-8 | 2026-02-14 | interested (Voltropy) | values UNSURE (±2); quoted sentence SOLID |
| O19 | Opus 4.6, Opus 4.5, Sonnet 4.5 (S) | Fiction.LiveBench (story comprehension; "0" is the cut-down story) | 0, 400, 1k, 2k, 4k, 8k, 16k, 32k, 60k, 120k, 192k | Opus 4.6: 87.5, 94.4, 91.7, 77.8, 97.2, 100, 100, 94.4, 91.7, 93.8, 0.0. Opus 4.5: 87.5, 100, 100, 94.4, 97.2, 91.7, 94.4, 94.4, 97.2, 93.8, 0.0. Sonnet 4.5: 100, 94.4, 97.2, 91.7, 91.7, 91.7, 86.1, 91.7, 88.9, 75.0, 0.0. The 192k column is 0.0 for all three, and the page gives no reason | fiction.live story "Fiction.liveBench April 04 2026" (table image) | 2026-04-04 | independent | SOLID |
| O20 | Sonnet 5 (S) | MRCR v2 8-needle | 8k to 512k | max: 96.4, 94.9, 87.9, 68.0, 52.9, 52.2, 32.0 | Context Arena API | — | independent | SOLID |
| O21 | Sonnet 4.6 (S) | MRCR v2 8-needle | 8k to 512k | medium: 95.8, 82.0, 83.8, 81.8, 71.7, 68.5, 43.7 | Context Arena API | — | independent | SOLID |
| O22 | Sonnet 5.5 (S) | AA-LCR v1.1 | ~100k | max 82.7 | AA embedded data | release 2026-09-28 | independent | SOLID |

## 3. Fable 5 and its siblings

| # | Model | What was measured | Length points | Result | Source (where) | Date | By | Mark |
|---|---|---|---|---|---|---|---|---|
| F1 | Fable 5 (`claude-fable-5`) | Spec | "a 1M token context window by default, and up to 128k output tokens" | — | platform docs "Introducing Claude Fable 5 and Claude Mythos 5" | fetched 01:37Z | vendor | SOLID |
| F2 | Fable 5.1 (`claude-fable-5-1`, "Successor to Claude Fable 5") | Spec and claim | 1M "(default and maximum)" | Lists "Long-context work, reasoning over and connecting details across the full 1M token context window" as an improvement area, with no numbers | whats-new-fable-5-1 page; card 2026-09-01 | 2026-09-01 | vendor | SOLID |
| F3 | Fable 5 | Program Bench | no per-length split | 86.3% (Fable 5.1 87.6%, Opus 5 85.4%) | Fable 5.1 and Mythos 5.1 card §8.11.1, pp. 175-176 | 2026-09-01 | vendor | SOLID |
| F4 | Mythos 5 (S; the docs say it "Shares Claude Fable 5's capabilities without the safety classifiers") | GraphWalks F1, 5 trials | 256K subset / 1M subset | Mythos 5: BFS 91.1 / 79.4, Parents 99.96 / 97.5. Mythos Preview: 85.7 / 74.3 and 99.9 / 95.5. Opus 4.8: 85.9 / 68.1 and 99.3 / 83.3. GPT-5.5: 73.7 / 45.4 and 90.1 / 58.5 | Fable 5 and Mythos 5 card §8.13, Table 8.13.A and Figs 8.13.B-C, pp. 264-266 | 2026-06-09 | vendor | SOLID |
| F5 | Fable 5 | AA-LCR v1.1 | ~100k | max (Opus 4.8 fallback): 82.3 | AA model pages, embedded data | — | independent | SOLID |
| F6 | Fable 5.1 | AA-LCR v1.1 | ~100k | low 82.3, medium 84.7, high 83.7, xhigh 83.0, max 85.3 | same | — | independent | SOLID |
| F7 | Fable 5 | Long-session behavior notes | — | "Deep into a long session, Claude Fable 5 can occasionally end a turn with a text-only statement of intent ("I'll now run X") without issuing the corresponding tool call". Also: "In very long sessions, Claude Fable 5 can occasionally suggest a new session, offer to summarize and hand off, or trim its own work. This is most often triggered when the harness shows a remaining-token countdown to the model." No rates given | prompting-claude-fable-5.md lines 107 and 113-118 | fetched 01:51Z | vendor | SOLID |
| F8 | Fable 5 and 5.1, Opus 4.7 and later | Context awareness | — | These models "don't receive these injected tags" (the remaining-token budget tags) | context-windows.md:124 | fetched 01:46Z | vendor | SOLID |
| F9 | Fable 5 and 5.1 | Context Arena coverage | — | `anthropic/claude-fable-5` is listed with `"summaries":[]`. No `fable-5.1` or `opus-5-5` slug exists among 545 models | Context Arena API | fetched 01:48Z | independent | SOLID (absence in the API) |

## 4. Qwen3.8-27B and its siblings

| # | Model | What was measured | Length points | Result | Source (where) | Date | By | Mark |
|---|---|---|---|---|---|---|---|---|
| Q1 | Qwen3.8-27B | Spec | "Context Length: 262,144 natively and extensible up to 1,000,000 tokens." | — | HF `Qwen/Qwen3.8-27B` README.md:53 | card 2026-08-13 (per the repo's evidence row C1.11); fetched 01:52Z | vendor | SOLID |
| Q2 | Qwen3.8-27B | Guidance on extending the length | above 262,144 | "All the notable open-source frameworks implement static YaRN, which means the scaling factor remains constant regardless of input length, potentially impacting performance on shorter texts." The card advises changing the RoPE settings "only when processing long contexts is required", and a factor of 2.0 for a typical 524,288 | README.md:514-558 | — | vendor | SOLID |
| Q3 | Qwen3.8-27B | Vendor benchmark table | — | 25 rows, none of them long-context. SWE-bench Pro, DeepSWE 1.1 and QwenSWEBench were run "with the Claude Code harness … and a 256K context window" | README.md:177-180 | — | vendor | SOLID |
| Q4 | Qwen3.8-27B | Output guidance | — | Reasoning 262,144 and final response 131,072, "within the 1M context length" | README.md:507-510 | — | vendor | SOLID |
| Q5 | Qwen3.8-27B | MRCR v2 8-needle (o200k bins; Qwen tokens are about 1.021 times o200k) | 8k, 16k, 32k, 64k, 128k; no 256k data | medium: 99.3, 99.2, 96.7, 97.9, 78.9 [70.7-86.4]. xhigh: 100.0, 99.0, 92.9, 87.4, 74.3 [65.1-82.0]. low: 99.3, 95.6, 95.3, 93.3, 81.8 [74.3-88.5]. Reasoning off: 60.3, 44.1, 51.5, 42.9, 34.7. n = 80/80/136/85/103 | Context Arena API | — | independent | SOLID for the values; the provider and quantization used are not stated |
| Q6 | Qwen3.8-27B | AA-LCR v1.1 | ~100k | xhigh 82.0, medium 79.7, low 77.3, non-reasoning 69.3 | AA model pages, embedded data | release 2026-08-14 | independent | SOLID |
| Q7 | Qwen3.8-27B | Alibaba Cloud announcement | — | "native 262K-token context window that easily extends to 1 million tokens"; no long-context numbers | alibabacloud.com blog | 2026-08-17 | vendor | UNSURE (WebFetch summary only) |
| Q8 | Qwen3.8-27B as served for our lanes | Local configuration | — | vLLM `Environment=MAX_LEN=131072` (`deploy/qwen.container:29`). Served weights are `Qwen3.8-27B-W4A16-AutoRound` (PC-BRIDGE.md, "The Qwen Jev adapter's prerequisites" section, lines 190-192) | repo | 92fcd4d, 2026-09-26 | local | SOLID (repo text; not re-measured on the PC) |
| Q9 | Qwen3.8-Max (S, larger sibling) | MRCR v2 8-needle | 8k to 512k | xhigh: 98.7, 97.5, 99.3, 96.5, 92.3, 67.7, 29.7. medium: 99.3, 97.9, 98.1, 93.3, 87.3, 70.6, 25.7. low: 99.3, 96.7, 94.8, 93.3, 81.5, 71.2, 28.5 | Context Arena API | — | independent | SOLID |
| Q10 | Qwen3.6-27B, Qwen3.5-27B, Qwen3.6-35B-A3B (S) | MRCR v2 8-needle, reasoning enabled | 8k to 128k | 3.6-27B: 97.6, 94.0, 92.8, 70.5, 56.6. 3.5-27B: 100.0, 94.0, 82.9, 49.6, 42.2. 3.6-35B-A3B: 98.8, 95.1, 94.3, 70.4, 59.3 | Context Arena API | — | independent | SOLID |
| Q11 | Qwen3.6-27B and Qwen3.5-27B (S) | Vendor advice on minimum context | — | "we advise maintaining a context length of at least 128K tokens to preserve thinking capabilities" (Qwen3.6-27B README:529; Qwen3.5-27B README:907). The Qwen3.8-27B README has no such line (grep for "128K", "at least", "preserve thinking") | HF READMEs | fetched 01:52Z | vendor | SOLID |
| Q12 | Qwen3.5-27B (S) | AA-LCR and LongBench v2, vendor-reported single aggregates | — | 66.1 and 60.6 | README "Long Context" rows | — | vendor | SOLID |
| Q13 | Qwen3-Next-80B-A3B (S; "Gated DeltaNet and Gated Attention" hybrid, README:20) | RULER "1M version", YaRN, "260 samples for each length" | 4k to 1000k | 98.5, 99.0, 98.0, 98.7, 97.6 (64k), 95.0 (96k), 96.0 (128k), 94.0 (192k), 93.5 (256k), 91.7 (384k), 86.9 (512k), 85.5 (640k), 81.7 (768k), 80.3 (896k), 80.3 (1000k); average 91.8 | HF README "Long-Context Performance" | not dated in the file | vendor | SOLID for the values; date UNSURE |
| Q14 | Qwen3-235B-A22B-Instruct-2507 and Qwen3-30B-A3B-Instruct-2507 (S) | RULER 1M version with Dual Chunk Attention, full attention | 4k to 1000k | 235B: 98.5 … 93.9 (128k), 91.0 (256k), 90.9 (512k), 84.5 (1000k). 30B-A3B: 98.0 … 89.1 (128k), 82.5 (256k), 78.4 (512k), 72.8 (1000k). Older Qwen3-235B-A22B non-thinking: 97.7 … 88.5 (128k), 82.1 (256k), 74.4 (512k), 68.0 (1000k) | HF READMEs | not dated in the files | vendor | SOLID |
| Q15 | Qwen3 dense models (S) | RULER leaderboard. Numbers are author-reported from the Qwen3 technical report; the threshold is Llama-2-7B at 4K (85.6) | 4k to 128k | Qwen3-32B: 98.4 at 4k, 85.6 at 128K, effective ">128K". Qwen3-14B: 85.1, ">128K". Qwen3-8B: 77.4, "64K". Qwen3-30B-A3B: 79.2, "64K" | github.com/NVIDIA/RULER README | fetched 01:57Z | vendor numbers on an independent board | SOLID |
| Q16 | Qwen3.6-Plus, Qwen3.5-Plus, Qwen3-235B-thinking-2507 (S) | Fiction.LiveBench | 0 to 192k | qwen3.6-plus (reasoning high): 87.5, 97.2, 82.9, 61.1, 69.4, 61.1, 66.7, 61.1, 66.7, 75.0, 71.9. qwen3.5-plus-02-15 (high): 100, 100, 94.4, 83.3, 86.1, 91.7, 77.8, 80.6, 91.2, 76.2, 76.0. qwen3-235b-a22b-thinking-2507: 100, 100, 91.7, 86.1, 91.7, 97.2, 75.0, 80.6, 77.8, 68.8, blank | fiction.live table image | 2026-04-04 | independent | SOLID |
| Q17 | Qwen3 4B-32B (S) | Long-horizon execution over turns | up to 100+ turns | Per-turn accuracy falls as turns grow. There is a "self-conditioning effect": errors already in context raise the error rate. Frontier models including Qwen3-235B-2507 "largely solves long-context degradation for up to 100 turns" on an error-free history, but still degrade as injected errors rise | arXiv 2509.09677 §3 | 2025-09-11 (v3 2026-03-13) | independent | SOLID |
| Q18 | Qwen-2.5 7B/32B/72B and Llama-3.1 (S; quantization class) | Ruler, OneRuler and NoCha at 64K-128K. AWQ-int4 and GPTQ-int4 are W4A16 | 8K, 64K, 128K | 8-bit: about 0.8 point average drop. Average drops: AWQ-int4 1.8, GPTQ-int4 2.7, BNB-nf4 6.9. "4-bit quantization shows the most significant drop, with an average decrease of up to 23% across models at 128K tokens". "Qwen-2.5 72B remains robust under BNB-nf4, Llama-3.1 70B experiences a 32% performance drop" | arXiv 2505.20276 (EMNLP 2025) | 2025-05 (from the arXiv id) | independent | SOLID for the values. AutoRound was not tested, so the mapping to our quant is UNSURE |

## 5. Item 2: independent curves by length (class-level; mostly not our models)

| # | Study | Scope | Finding (quoted where marked) | Where | Date | By | Mark |
|---|---|---|---|---|---|---|---|
| I1 | RULER | 17 LMs, 13 tasks, 4K-128K; threshold Llama-2-7B at 4K = 85.6 | "only half of them can maintain satisfactory performance at the length of 32K" | arXiv 2404.06654 | 2024-04-09 | independent (NVIDIA) | SOLID |
| I2 | NoLiMa | 13 LLMs claiming at least 128K. Effective length = "the longest context where a model maintains at least 85% of its base score" | "At 32K, for instance, 11 models drop below 50% of their strong short-length baselines"; GPT-4o falls from 99.3 to 69.7. The leaderboard (last entry 2025-07-17) gives effective lengths: GPT-4.1 16K (1M claimed), GPT-4o 8K, Claude 3.5 Sonnet 4K (base 87.6; 29.8 at 32K), Gemini 2.5 Flash 2K, Llama 4 Maverick 2K | arXiv 2502.05167; github.com/adobe-research/NoLiMa README | 2025-02-07 | independent | SOLID |
| I3 | HELMET | 59 LCLMs up to 128K | "synthetic tasks like NIAH do not reliably predict downstream performance"; the open-versus-closed gap "widens as length increases" | arXiv 2410.02694 | 2024-10-03 | independent | SOLID (abstract) |
| I4 | LongBench v2 | 503 questions, 8k to 2M words | Best direct answer 50.1%, o1-preview 57.7%, humans 53.7%. No per-length rows read | arXiv 2412.15204 | 2024-12-19 | independent | SOLID (abstract) |
| I5 | Chroma "Context Rot" | 18 models (GPT-4.1, Claude 4, Gemini 2.5, Qwen3; Qwen extended by YaRN from 32,768 to 131,072) | "performance grows increasingly unreliable as input length grows". LongMemEval focused (~300 tokens) against full (~113k tokens): "Across all models, we see significantly higher performance on focused prompts". The Claude family shows "the most pronounced gap", driven by abstentions. Shuffled haystacks beat coherent ones across all 18 models | research.trychroma.com/context-rot | 2025-07-14 | independent | SOLID |
| I6 | Du et al., "Context Length Alone Hurts" | Llama-3.1-8B, Mistral-7B, GPT-4o, Claude 3.7 Sonnet, Gemini 2.0; up to about 30K | Drops of "13.9%–85%" even "when models can perfectly retrieve all relevant information"; the drop persists with whitespace padding and with masking; the frontier models "experience a smaller drop" | arXiv 2510.05381 | 2025-10-06 | independent | SOLID |
| I7 | LongMemEval | 500 questions | "long-context LLMs showing a 30% accuracy drop on memorizing information across sustained interactions" | arXiv 2410.10813 | 2024-10-14 | independent | SOLID (abstract) |
| I8 | AA-LCR (method) | 100 questions, "~100,000 tokens (measured using the cl100k_base tokenizer)" | Top of the board: Kimi K3 (max) 88.7% | artificialanalysis.ai | method 2025-08-05 | independent | UNSURE for the method details (WebFetch summary); scores SOLID |
| I9 | LoCoDiff | code-diff reconstruction by prompt length | "all drop significantly by 10k tokens … under 50% accuracy when prompts are just 25k tokens long" | abanteai.github.io/LoCoDiff-bench (search summary; site not opened) | 2025 | independent | UNSURE |
| I10 | Distractor-aware truncation (see O14) | method finding | "The naive protocol is therefore not a measurement of context-window effects; it is a measurement of how often middle-removal happens to spare the answer." | arXiv 2608.03297 | 2026-08-04 | independent | SOLID |

## 6. K0-derived table (my arithmetic on SOLID Context Arena values; not the source's own threshold)

For each curve: the first bin whose score falls below 85% of that curve's own 8k score (NoLiMa's convention), and the first below 50%. "none≤X" means no bin up to X falls below.

| Model | Reasoning mode | 8k score | First bin <85% | First bin <50% |
|---|---|---|---|---|
| Opus 5 | max | 98.7 | 256k | 512k |
| Opus 4.8 | max | 97.4 | 128k | 512k |
| Opus 4.7 | xhigh | 89.0 | 32k | 64k |
| Opus 4.6 | high | 98.2 | 64k | none≤512k |
| Opus 4.6 | medium | 99.3 | 64k | 512k |
| Sonnet 5 | max | 96.4 | 64k | 512k |
| Sonnet 4.6 | medium | 95.8 | 128k | 512k |
| Qwen3.8-27B | low | 99.3 | 128k | none≤128k |
| Qwen3.8-27B | medium | 99.3 | 128k | none≤128k |
| Qwen3.8-27B | xhigh | 100.0 | 128k | none≤128k |
| Qwen3.8-27B | off | 60.3 | 16k | none≤128k |
| Qwen3.8-Max | xhigh | 98.7 | 256k | 512k |
| Qwen3.8-Max | medium | 99.3 | 256k | 512k |
| Qwen3.6-27B | enabled | 97.6 | 64k | none≤128k |
| Qwen3.5-27B | enabled | 100.0 | 32k | 64k |

## 7. Item 3: agents at long context

| # | Source | Setup | Result | Where | Date | By | Mark |
|---|---|---|---|---|---|---|---|
| A1 | Harness design study | Three Nemotron-3 models and Mistral-Medium-3.5-128B on SWE-bench Verified and Terminal-Bench 2.1. Budgets 32k/64k/96k/128k. Compaction soft/hard thresholds 0.6/0.85 of the usable window | The success gap between managed and unmanaged context shrinks with the budget: 35.7, 15.9, 5.5, 2.7 points (SWE) and 9.5, 7.5, 4.8, 2.8 (TB). The unmanaged overflow rate falls from 78.7% to 8.7% (SWE) and 61.0% to 12.1% (TB). "context management extends execution trajectories without substantially altering agent behavior". Lossless recall is rarely used: 36 of 64 settings never call it | arXiv 2609.20804 | 2026-09-17 | independent | SOLID |
| A2 | Limits of long-context bug fixing | SWE-bench Verified, mini-SWE-agent; DeepSeek-R1-0528, GPT-5-nano, Qwen3-32B | "successful agentic trajectories typically remain under 20k-30k tokens, and … longer accumulated contexts correlate with lower success rates". Single-shot at 64k with perfect retrieval: Qwen3-Coder-30B-A3B 7%, GPT-5-nano 0% | arXiv 2602.16069 | 2026-02-17 | independent | SOLID |
| A3 | LLMs get lost in multi-turn conversation | 200,000+ simulated conversations, six tasks | "average drop of 39%"; "when LLMs take a wrong turn in a conversation, they get lost and do not recover" | arXiv 2505.06120 | 2025-05-09 | independent | SOLID |
| A4 | LoCoBench-Agent | Sonnet 4.5, Sonnet 4, GPT-5, GPT-4.1, GPT-4o, Gemini 2.5 Pro. "10K-1M" is codebase size explored through tools, not the agent's own fill | "agents exhibit remarkable long-context robustness"; comprehension 0.71-0.75; multi-session memory retention 0.32-0.37 "independent of context window size (128K to 1M tokens)"; "Models with shorter context windows (128K tokens) achieve higher multi-session memory retention than models with massive contexts (1M tokens)" | arXiv 2511.13998 | 2025-11-17 | independent (Salesforce) | SOLID |
| A5 | ProgramBench paper | 1,788 runs | Per-instance Pearson r = 0.27 (API calls) and 0.21 (cost) against pass rate; "More turns spent does not correlate with improved scores"; Opus 4.6 median 253 steps | arXiv 2605.03546, appendix | 2026-05 (from the arXiv id) | independent | SOLID |
| A6 | Anthropic BrowseComp budget scaling, with compaction "triggered at 200k tokens" | Total token limit 1M / 3M / 10M | Opus 5: 86.8 / 89.8 / 90.2. Mythos 5: 86.3 / 86.5 / 88.0. Opus 4.8: 80.6 / 84.0 / 84.3. Sonnet 5: 79.3 / 82.9 / 84.7 | Opus 5 card §8.10.2 and Fig 8.10.2.A, pp. 158-159 | 2026-07-24 | vendor | SOLID |
| A7 | Anthropic evaluation compaction triggers (configuration only; no reason stated) | — | Opus 4.6: 50k (its card, pp. 39-44). Opus 4.7, Sonnet 4.6, Mythos Preview: 200k, while Opus 4.6 in the same evaluations stayed at 50k (Opus 4.7 card pp. 198-199). Opus 4.8: 200k, orchestrators 100k (pp. 203-215). Fable 5 and Mythos 5: 200k, orchestrator 100k (pp. 268, 277). Opus 5: 200k (p. 158). Opus 5.5 OSWorld 2.0 harness: server-side compaction "once it exceeds 100k tokens" (p. 206) | system cards | 2026-02 to 2026-09-22 | vendor | SOLID |
| A8 | Anthropic context management (Sonnet 4.5) | — | "combining the memory tool with context editing improved performance by 39% over baseline"; "Context editing alone delivered a 29% improvement"; "In a 100-turn web search evaluation, context editing enabled agents to complete workflows that would otherwise fail due to context exhaustion—while reducing token consumption by 84%" | claude.com/blog/context-management | 2025-09-29 | vendor | SOLID |
| A9 | Anthropic harness post | — | "models tend to lose coherence on lengthy tasks as the context window fills"; "Some models also exhibit "context anxiety," in which they begin wrapping up work prematurely …". Sonnet 4.5 needed context resets; "Opus 4.5 largely removed that behavior on its own, so I was able to drop context resets from this harness entirely" | anthropic.com/engineering/harness-design-long-running-apps | 2026-03-24 | vendor | SOLID |
| A10 | Cognition (Sonnet 4.5) | — | "the first model we've seen that is aware of its own context window"; "taking shortcuts or leaving tasks incomplete when it believed it was near the end of its window, even when it had plenty of room left"; "enabling the 1M token beta but cap usage at 200k"; "the model consistently underestimates how many tokens it has left". No rates for these observations | cognition.com/blog/devin-sonnet-4-5-lessons-and-challenges | 2025-09-29 | independent (practitioner) | SOLID (quotes) |
| A11 | Opus 5.5 card | — | Some snapshots refused to write a compaction message in "less than 0.01% of completions". "Context compaction can further change how models act. We simulate compaction, but …" | pp. 102, 122 | 2026-09-22 | vendor | SOLID |
| A12 | Coding agents as long-context processors | — | Agents that put text in files and use tools beat "published state-of-the-art by 17.3% on average" | arXiv 2603.20432 | 2026-03-20 | independent | SOLID (abstract) |
| A13 | Agentic AI workload characteristics | Gemma and Qwen configurations | "most input tokens are reused across turns". A search snippet says successful SWE-bench Pro runs had a mean context of 82.2K against 72.3K for failures (body not read) | arXiv 2605.26297 | 2026-05-25 (v2 2026-09-21) | independent | SOLID (abstract); UNSURE (the numbers) |

## 8. Item 4: what a compaction costs, and the vendors' guidance on when to compact

**Measured loss.**

| # | Source | Setup | Result | Where | Date | By | Mark |
|---|---|---|---|---|---|---|---|
| C1 | LCM paper | Volt (LCM) against Claude Code v2.1.4, both on Opus 4.6 with Haiku 4.5 as auxiliary. OOLONG, 8K to 1M | Averages 74.8 against 70.3. Gains over raw Opus: +29.2 against +24.7. Claude Code is ahead at 8K (+13.1 vs +11.2) and 16K (+26.3 vs +25.0). Volt leads from 32K: +18.5 vs +8.5 at 256K, +42.4 vs +29.8 at 512K, +51.3 vs +47.0 at 1M. Figure values by eye: Claude Code about 94, 85, 65, 75, 64, 56.5, 58, 65; Volt about 94, 84, 68, 75.5, 70.5, 66.5, 70.5, 69 | papers.voltropy.com/LCM, pp. 7-8, 10 | 2026-02-14 | interested | SOLID (text); UNSURE (by-eye values) |
| C2 | Lost in Compaction (COMPINT) | Compactors: Recent-5, LLMLingua-2, gpt-oss-120b (Anthropic or pi-mono prompt), Qwen3-30B-A3B, Gemma-4-E4B, GPT-5.4-mini. Contexts cropped to 100K, "approximately 80% of a 128K-token context window"; N=750 | "Current compactors retain only 17% of injected SCs on average, and most perform worse than running the same task without compaction". The non-LLM compactors retain 0%. GPT-5.4-mini reaches "as high as 98%". Retention is "approximately 90% at a context length of 10K on the Hermes Agent dataset, and decline[s] as the context length increases". Compaction output is "182× shorter" at 100K; output grows only 0.84-1.28× while input grows 10× | arXiv 2608.11242 | 2026-07-31 | independent | SOLID |
| C3 | What does compression cost an agent? | 24-turn deterministic planning agent, 3 models | At 5× compression, completion is not significantly changed in any cell, but retrieval calls rise in 6 of 6 comparisons. GPT-5.5: completion 80% to 85% (p = 1.0), retrieval calls 21.0 to 63.9 (p = .002). Swapping retained state for irrelevant content: +57% retrieval (p < .001). ALFWorld sliding compression: "no retrieval surge" | arXiv 2608.16370 | 2026-08-17 | independent (1 author) | SOLID |
| C4 | Factory.ai probe evaluation | 36,611 messages, "hundreds of compression points", four probes each, GPT-5.2 judge, 0-5 scale | Overall: Factory 3.70, Anthropic (Claude SDK built-in) 3.44, OpenAI (`/responses/compact`) 3.35. Accuracy 4.04 / 3.74 / 3.43. Artifact trail 2.45 / 2.33 / 2.19, "the weakest dimension for all methods". Tokens removed: 98.6% / 98.7% / 99.3%. The fill at the compression points is not stated | factory.com/news/evaluating-compression | 2025-12-16 | interested | SOLID |
| C5 | SelfCompact | Qwen3-4B-Instruct-2507 on IMO-AnswerBench, fixed summary every 16k tokens (12 calls) | Accuracy: no compaction 38.9, fixed interval 41.4, SelfCompact 45.5, oracle "skip if correct" 52.9. After summaries: wrong-to-correct 1,486, correct-to-wrong 1,009 ("40.4% of all transitions cause degradations"). The search-agent baseline triggers at "30% of the max context window"; SelfCompact gains +8.5 / +9.2 / +5.3 over no compaction on BrowseComp-Plus | arXiv 2606.23525 | 2026-06-22 (v2 2026-07-10) | independent | SOLID |
| C6 | The Complexity Trap | SWE-agent on SWE-bench Verified, 5 model configs | Observation masking "halves cost relative to the raw agent while matching, and sometimes slightly exceeding, the solve rate of LLM summarization"; the hybrid cuts cost a further 7% / 11% | arXiv 2508.21433 | 2025-08-29 | independent | SOLID (abstract) |
| C7 | ACON | AppWorld, OfficeBench, multi-objective QA | "reduces peak token usage by 26-54% while improving task success over existing compression baselines" | arXiv 2510.00615 | 2025-10-01 | independent | SOLID (abstract) |
| C8 | Parallel compaction | 8B-120B backbones | "summarization is inherently lossy"; the information retained fluctuates "substantially from run to run" as context grows | arXiv 2605.23296 | 2026-05-22 | independent | SOLID (abstract) |

**Vendor and harness guidance on when to compact.**

| # | Source | Statement | Where | Date | Mark |
|---|---|---|---|---|---|
| G1 | Anthropic API docs | "As token count grows, accuracy and recall degrade, a phenomenon known as *context rot*." | context-windows.md:11 | fetched 01:46Z | SOLID |
| G2 | Anthropic API docs | Compaction "keeps the active context small, because response quality degrades as a conversation grows." | compaction.md:7 | same | SOLID |
| G3 | Anthropic API docs | Threshold compaction: the default trigger is `{"type": "input_tokens", "value": 150000}`, and the "`value` must be at least 50,000 tokens". Beta `compact-2026-01-12`. The default summary prompt text is given at lines 505-509 | compaction-threshold.md:284 | same | SOLID |
| G4 | Anthropic API docs | On-demand compaction (beta `compact-2026-09-04`), Opus 5.5 included; it can keep recent turns word for word | whats-new-opus-5-5.md:73-75; compaction.md:15-23 | same | SOLID |
| G5 | Anthropic engineering post | "the model's ability to accurately recall information from that context decreases"; "attention budget"; "n² pairwise relationships for n tokens"; "a performance gradient rather than a hard cliff"; "Start by maximizing recall … then iterate to improve precision"; tool result clearing is "One of the safest lightest touch forms of compaction" | anthropic.com/engineering/effective-context-engineering-for-ai-agents | 2025-09-29 | SOLID |
| G6 | Anthropic prompting guide | For 20k+ tokens, "Put longform data at the top"; "Queries at the end can improve response quality by up to 30 percent in tests". "Starting fresh versus compacting: When a context window is cleared, consider starting with a brand new context window rather than using compaction." A "Managing context limits" sample prompt is given | claude-prompting-best-practices.md:241-248, 797-840 | fetched 01:51Z | SOLID |
| G7 | Claude Code docs | The auto-compact window can be set by `/autocompact`, `--autocompact`, `autoCompactWindow` or `CLAUDE_CODE_AUTO_COMPACT_WINDOW` (the env var wins), from 100K to 1M; the doc's example value is `/autocompact 500k`. "Cloud sessions compact as the conversation approaches the model's limit". Native-1M models ("the Fable models, and Opus 4.7 and later") compact "at about 967K tokens by default" | model-config.md:742-765 (fetched 01:45:43Z) | live | SOLID |
| G8 | Claude Code docs | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`: "the variable can't raise the threshold … It applies only in sessions that compact before the model's context limit … Applies to both main conversations and subagents". `CLAUDE_CODE_AUTO_COMPACT_WINDOW`: "a value like `500k` reads as `500` and clamps to the 100K minimum … The status line's `used_percentage` always measures against the model's full context window" | env-vars.md:196, 214 | live | SOLID |
| G9 | Claude Code docs | After compaction, Claude Code re-reads up to five recently modified files; a file over 5,000 tokens returns as a path reference. Skill bodies are capped at 5,000 tokens each and 25,000 in total, oldest dropped first, and truncation "keeps the start". Hook-added context is "Summarized with the rest"; SessionStart(compact) output is added | context-window.md:1592-1615 | live | SOLID |
| G10 | Claude Code docs | "It clears older tool outputs first, then summarizes the conversation if needed. Your requests and key code snippets are preserved; detailed instructions from early in the conversation may be lost." | how-claude-code-works.md:138 | live | SOLID |
| G11 | Hermes (our lane harness), current `main` docs | Compressor `threshold: 0.50` "(floored at 0.75 below 512K windows)". Gateway hygiene is fixed at 85%, because "Setting it at 50% (same as the agent) caused premature compression on every turn in long gateway sessions". Lean tail is 2.5% of the window (10K floor, 25K cap) | raw hermes-agent `website/docs/developer-guide/context-compression-and-caching.md` lines 83-101, 236-268, 342-345 (fetched 01:58Z) | commit date unknown (the API refused) | SOLID (text at main) |
| G12 | Hermes at our pins (b3399c1, 527da60) | 0.75 floor under 512K; the trigger is computed on context_length minus max_tokens, floored at 64,000 | TRIM-AUDIT rows B5-B6, lines 104-105 | 6222e4a, 2026-09-28 | SOLID (as recorded by that lane) |
| G13 | Hermes issues #125235 and #126304 | These concern a 256,000-token `threshold_tokens` default. A snippet reads: "The 50% default was designed for 32K–128K context models … ~500K … judged too late" | search snippets only | — | UNSURE (the primary read was refused, R2) |
| G14 | Qwen Code (Alibaba's CLI) | `context.autoCompactThreshold` defaults to 0.85 and "Acts as a ceiling on the trigger: on large windows it is the effective trigger (~85%), while on smaller windows compaction may fire earlier" | qwenlm.github.io/qwen-code-docs settings page (fetched 01:59Z) | live | SOLID |
| G15 | Source-code study of 11 harnesses | Claude Code `AUTOCOMPACT_BUFFER_TOKENS = 13 000` and per-skill "25 000-token budget"; Gemini CLI at 50%, keeping the recent 30%; Pi at the window minus 16,384; Hermes "50% of context minus max-tokens, 64K floor". Seven of 11 harnesses use threshold-triggered LLM summarization | arXiv 2609.00006 §9.5 | 2026-07-15 | UNSURE (a third party's reading at its own pins) |

## 9. Item 5: where in the context the losses fall

| # | Source | Finding (quoted) | Where | Date | Mark |
|---|---|---|---|---|---|
| P1 | Lost in the Middle | "performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle" (2023 models) | arXiv 2307.03172 | 2023-07-06 | SOLID |
| P2 | Found in the Middle | "U-shaped attention bias where the tokens at the beginning and at the end of its input receive higher attention, regardless of their relevance" | arXiv 2406.16008 | 2024-06-23 | SOLID |
| P3 | Positional biases shift near the window limit (Llama-3.x-70B, Mistral-Small-24B, Qwen-2.5-32B; 8K-128K windows) | "the LiM effect is strongest when inputs occupy up to 50% of a model's context window. Beyond that, the primacy bias weakens, while recency bias remains relatively stable … a distance-based bias, where model performance is better when relevant information is closer to the end of the input" | arXiv 2508.07479 | 2025-08-10 | SOLID |
| P4 | Chroma | NIAH: "Testing across 11 needle positions, we find no notable variation in performance for this specific NIAH task". Repeated words: "Accuracy is highest when the unique word is placed near the beginning of the sequence, especially as input length increases" | context-rot report | 2025-07-14 | SOLID |
| P5 | Du et al. | The drop persists "when all relevant evidence is placed immediately before the question" | arXiv 2510.05381 | 2025-10-06 | SOLID |
| P6 | Lost in Compaction | "For LLM-based compactors, we observe that later injection locations yield higher retention rates". At 50K, "improved retention rates at the top and middle injection positions but no corresponding improvement at the bottom position relative to the 100K setting". The pattern "does not hold for Hermes-Agent" | arXiv 2608.11242 | 2026-07-31 | SOLID |
| P7 | The Position Curse | "backward retrieval substantially lags forward retrieval"; "even in a two-line code snippet, Claude Opus 4.6 misidentifies the second-to-last line most of the time" | arXiv 2605.07127 | 2026-05-08 | SOLID (abstract) |
| P8 | When Attention Closes | Attention to goal-defining tokens declines over turns. Force-closing that channel in Mistral "collapses recall from near-perfect to 11% on a 20-fact retention task" | arXiv 2605.12922 | 2026-05-13 | SOLID (abstract) |
| P9 | LLMs get lost in multi-turn conversation | "LLMs often make assumptions in early turns and prematurely attempt to generate final solutions, on which they overly rely" | arXiv 2505.06120 | 2025-05-09 | SOLID |
| P10 | Illusion of diminishing returns | "models become more likely to make mistakes when the context contains their errors from prior turns"; "thinking mitigates self-conditioning" | arXiv 2509.09677 | 2025-09-11 | SOLID |
| P11 | Anthropic prompting guide and Claude Code docs | Long data at the top and the query at the end ("up to 30 percent"). After compaction, early detailed instructions "may be lost", and truncated skill bodies keep "the start of the file" | G6, G9, G10 | — | SOLID |
| P12 | Distractor-aware truncation | Under naive middle removal, the answer-bearing content "survives in fewer than 1% of samples at 25% retention" | arXiv 2608.03297 | 2026-08-04 | SOLID |

---

## 10. What I looked for and did not find (with the queries I ran)

1. **An Opus 5.5 per-length vendor curve** (MRCR, GraphWalks, long-document QA).
   - Not in the Opus 5.5 card. I grepped its full text with space-tolerant patterns for MRCR, GraphWalks, needle, haystack, OOLONG, LongBench, RULER, context length and compaction.
   - Not in the launch post or the "what's new" page.
   - Query: `Claude Opus 5.5 system card long context MRCR 1M`.
2. **Any MRCR or GraphWalks number for Opus 5, Opus 5.5 or Fable 5.1 from Anthropic.** All three cards list only Program Bench under "Long context".
3. **Independent per-length curves for Opus 5.5 or Fable 5.x.**
   - Context Arena has no slug for Opus 5.5 or Fable 5.1, and an empty one for Fable 5.
   - Fiction.liveBench was last updated 2026-04-04, and NoLiMa on 2025-07-17.
   - The RULER leaderboard has no Claude rows.
   - Queries:
     - `"Opus 5.5" long context benchmark results 1M tokens independent evaluation MRCR GraphWalks OOLONG`
     - `contextarena.ai MRCR 8-needle results Claude Opus 5 Fable 5.1 1M bins`
     - `Fiction.LiveBench long context results September 2026 Opus 5.5 Fable`
     - `LoCoDiff benchmark long context code diff results by prompt length Claude Opus 5 2026`
4. **A Fable 5 curve under its own name.** Only Mythos 5 has one; the docs state it has the same capabilities.
   - Queries: `Anthropic "Fable 5" model context window` and `"System Card" "Claude Fable 5" "Claude Mythos 5" pdf www-cdn.anthropic.com`.
5. **A vendor long-context benchmark for Qwen3.8-27B.**
   - None in the HF card (25 rows) or the Alibaba Cloud post.
   - `qwen.ai/blog?id=qwen3.8` rendered no readable content; WebFetch returned only "Qwen".
   - Query: `Qwen3.8-27B long context benchmark RULER LongBench`.
6. **Qwen3.8-27B above 128k.** No independent data exists; Context Arena's bins stop at 128k for the 27B model.
7. **Long-context measurements of Qwen3.8-27B as W4A16 AutoRound.** None found. The nearest is 2505.20276.
   - Query: `4-bit weight quantization long-context degradation RULER measured W4A16 GPTQ AWQ context length study`.
8. **A measured comparison of Claude Code auto-compact windows** (for example 200K against 500K against 967K) on the same tasks. None found. A search summary attributes the same observation to a practitioner blog, which I did not open (UNSURE).
   - Query: `Claude Code autocompact window experiment 500k vs 967k quality measured sessions 1M context compaction earlier results`.
9. **A compaction-threshold comparison on any 1M-window model.** None found. The threshold studies found use 128K-class windows: A1, C2 and C5.
   - Query: `compaction threshold comparison agents summarization when to compact evaluation 2026`.
10. **Position-effect measurements on Opus 5.x, Fable 5.x or Qwen3.8.** None found. The nearest are Opus 4.6 (P7) and the Claude 4 family (Chroma).
    - Query: `position bias long context 2026 frontier models lost in the middle still recency primacy measured study arXiv`.
11. **HELMET and LongBench v2 per-length rows for our models or close siblings.** Not found; the Qwen3.5 cards give aggregates only.
12. **Why Anthropic's evaluations use a 50k trigger for Opus 4.6 and 200k for 4.7 and later.** The cards state the settings with no reason.
13. **Context Arena's run dates, providers and quantization.** Not in the API response.
14. **Factory's fill level at its compression points.** Not stated.
15. **NoLiMa's needle-position analysis.** Not read; I read only its README and abstract.
16. **The Hermes issues #125235 and #126304 and the Hermes doc's commit history.** Refused (R2).
17. **Qwen Code's threshold-redesign page.** `qwenlm.github.io/qwen-code-docs/en/plans/2026-05-14-auto-compaction-threshold-redesign/` returned HTTP 404 at 01:59:24Z.

## 11. DISCREPANCIES (both sides recorded; not resolved)

**Brief against what I found.**

1. **Fable version.** The brief names "Fable 5".
   - The current lineup lists Claude Fable 5.1 (`claude-fable-5-1`, "Successor to Claude Fable 5"; card dated 2026-09-01).
   - Fable 5 sits under "Legacy models (still available)".
   - Neither the brief nor CLAUDE.md's table ("Fable 5 (main loop)") states which Fable the main loop runs. I gathered both versions.
2. **Vendor MRCR and graph walks.** Item 1 expects vendor MRCR at 128k/256k/1M and graph walks.
   - The Opus 5.5 (2026-09-22), Opus 5 (2026-07-24) and Fable 5.1 (2026-09-01) cards publish none. Their "Long context" sections carry only Program Bench, with no per-length split.
   - The latest per-length vendor numbers are Fable 5/Mythos 5 (GraphWalks, 2026-06-09), Opus 4.8 (GraphWalks, 2026-05-28) and Opus 4.7 (MRCR and GraphWalks, 2026-04-16).
3. **Doc line numbers.** Item 4 cites "`model-config.md` 734-757 in the audit". The live page has the same text at 738-765: "Set the auto-compact window" at 742-756 and "Default auto-compact thresholds" at 758-765.
4. **Where a Hermes lane compresses.**
   - D-097 reads "a lane compresses near 100k (the profile's threshold 0.5)".
   - Hermes's current `main` docs say the ratio is "floored at 0.75 below 512K windows". The TRIM-AUDIT recorded the same floor at both pins (B6) and noted the contradiction (its line 123: about 150,000 at a reported 200,000, and about 98,304 at 131,072).
   - The 2026-07-15 source-code study describes Hermes as "50% of context minus max-tokens, 64K floor" and does not mention the 0.75 floor.
5. **Minimum context advice.** The Qwen3.5 and 3.6 cards advise keeping "at least 128K tokens to preserve thinking capabilities". The Qwen3.8-27B card has no such line. Our lanes serve 131,072.
6. **This session's compaction base.** The brief gives "about 784k" (A1.15). The docs say cloud sessions "compact as the conversation approaches the model's limit", and that the PCT override "applies only in sessions that compact before the model's context limit". The docs do not say what base the 80% applies to in a cloud session.

**Contradictions between sources.**

7. **Vendor against independent MRCR v2 8-needle in the same (128k, 256k] bin.**
   - Opus 4.6: vendor 91.9 (64k thinking) and 93.0 (max), against Context Arena 69.1 (high) and 71.8 (medium).
   - Opus 4.7: vendor 59.2 (max), against Context Arena 1.4 (high), 2.2 (xhigh) and 2.7 (medium).
   - The efforts and harnesses differ, and Context Arena ran no "max" for Opus 4.7.
8. **Tokenizer ratio.** The docs say the current tokenizer gives "roughly 30% more tokens" than earlier models for the same text. Context Arena's measured ratios on MRCR text are 1.638 against 1.131, which is 1.448×.
9. **GraphWalks "1M" definitions.** The Opus 4.6 card gives "BFS 1M" 38.7 and "Parents 1M" 72.0 for Opus 4.6. The Opus 4.8 card gives the "1M subset" as 16.3 and 48.6.
   - My arithmetic: (61.1 + 16.3)/2 = 38.7 and (95.4 + 48.6)/2 = 72.0. So the 4.6 card's "1M" is the whole variant, half of it 256k problems.
   - The Opus 4.7 card's "256K-1M" values fit the same split: 2×58.6 − 76.91 = 40.29, and 2×75.1 − 93.57 = 56.63.
   - The numbers are consistent once the definitions are read. I record this because comparing the rows across cards shows a drop that is not real.
10. **LCM paper at 8K.** The text says Claude Code "held a slight edge at 8K (+13.1 vs. +11.2)", which is about 96.2 against 94.3 over a raw score of about 83.1. Figure 6 draws both 8K points at about 94. The 16K, 256K, 512K and 1M gains match the figure.
11. **LCM paper's degradation wording.** The text says raw Opus 4.6 degraded "beyond 65K tokens", but the same figure shows raw at about 39 at 32K, below its about 48 at 65K.
12. **Sonnet 4.5 on MRCR.** It scores 10.8 at 256K and 18.5 at 1M, which is lower at the shorter length. The table and the figure of the Opus 4.6 card both print these values.
13. **Claude Code skill caps.** The docs cap re-injected skills at "5,000 tokens per skill and 25,000 tokens total". The source-code study says there is "a per-skill 25 000-token budget".

## 12. Refusals and tool failures (verbatim, with times)

- **R1, 01:56:33Z: transport failure.** `curl https://factory.ai/news/evaluating-compression` returned `curl: (35) Recv failure: Connection reset by peer`.
  - Proxy note: `factory.ai:443 — ws_closed_mid_exchange (the tunnel to the egress proxy closed before the exchange completed)`.
  - Proxy status at 01:56:56Z: `tunnel closed (code 1006, Connection ended) after 11s; 517 B sent, 39 B received, client reading, 0 B still queued in the relay`.
  - What I did next: one WebFetch of the same URL with the brief's named tool. It returned `307 Temporary Redirect` to `https://factory.com/news/evaluating-compression` (the server's own Location header). I read that page through WebFetch, then with curl at 02:06:09Z (HTTP 200).
  - I flag this so the coordinator can judge whether it counts as working around.
- **R2, 01:59:06Z: refusal.** `https://api.github.com/repos/NousResearch/hermes-agent/commits?path=website/docs/developer-guide/context-compression-and-caching.md&per_page=5` returned HTTP 403 with this body: `{"message":"GitHub access to this repository is not enabled for this session. Use add_repo to request access. If add_repo answers that read access is already available and you need GitHub API or write access, call add_repo again with access:\"push\" to attach the repository with credentials.","documentation_url":"https://docs.anthropic.com/en/docs/claude-code/github-actions"}`. Not worked around: I made no add_repo call, and I opened issues #125235 and #126304 by no other route.
- **R3, command start 02:03:58Z: rate limit.** The arXiv export API (`id_list=2605.03546`) returned the body `Rate exceeded.` I did not retry. The ProgramBench HTML page, fetched in the same command, was read.
- **R4, about 01:38Z: tool limit.** WebFetch of the Opus 5.5 system card PDF failed with `maxContentLength size of 10485760 exceeded`. I read the PDF with a curl download and my own parser.
- **Pages with no data in the fetched HTML.** WebFetch of `contextarena.ai` and `fiction.live` returned only page shells. I then read the data those pages load from each site's own public endpoints (`contextarena.ai/api/...`, `fiction.live/api/...`). WebFetch of `qwen.ai/blog?id=qwen3.8` returned no readable content, and I made no further attempt.

## 13. Local files cited, with git dates

At 02:03Z all were clean in the working tree. Commits are cited by origin id where they are on origin, and by subject where they are local only.

| File | Lines used | Last commit |
|---|---|---|
| `tasks/briefs/jev-trim/K0-COMPACTION-POINT-brief.md` | whole | 0749fe5, 2026-09-29T01:42:49Z |
| `docs/research/findings/jev-trim/D105-DESIGN-v1.md` | §10-10.2, lines 235-280 | 0749fe5 |
| `docs/research/findings/jev-trim/TRIM-AUDIT-2026-09-28.md` | 70-71 (A1.14, A1.15), 104-105 (B5, B6), 123 (contradiction) | 6222e4a, 2026-09-28T22:57:26Z |
| `tasks/briefs/jev-trim/T1-LCM-AUDIT-report.md` | §8, 237-252 | 0749fe5 |
| `docs/08_DECISION_LOG.md` | D-097 row, 108 | 0749fe5 |
| `PC-BRIDGE.md` | vLLM Qwen container section (~157-175); served folder 190-192 | 92fcd4d, 2026-09-26T08:12:14Z |
| `deploy/qwen.container` | 29 (`MAX_LEN=131072`) | 92fcd4d |
| `docs/research/FINDINGS-LOCAL-BUILDER-QWEN38.md` | 3-4, 16-18 | d201f8a, 2026-09-15T07:16:48Z |
| `docs/research/evidence/qwen38-local-builder-evidence-2026-09-14.md` | 59 (C1.11) | 27d7dab, 2026-09-14T12:14:53Z |
| `harness-ports/bin/qwen-server.sh` | 33 (`QWEN_CTX` default 262144, the llama.cpp fallback path) | a670c80, 2026-09-16T23:36:22Z |
| `scripts/premise_block.sh` | whole | a81c034, 2026-09-23T21:17:17Z |

The premise ran at local HEAD "I59-F landing staged (task #335): the S0-05 re-capture waits for the owner's sudo; live-state". That commit is not on origin; its id was rewritten at push.
