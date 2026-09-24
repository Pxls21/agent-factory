# The long-input Jev plan: J4 (the test) and the RWKV-7 student (task #241, D-079)

STATUS 2026-09-24 16:3xZ: a PLAN, not built. Owner direction (D-079): Laya keeps short, high-volume decisions; a small RWKV-7
(`RWKV/RWKV7-Goose-World2.9-0.4B-HF`, revision e94655a9) trains on LONG inputs, because a fixed-size state is its strength only if
it is trained to keep what the question needs; Qwen 27B (the running vLLM, through the QJ1 adapter) teaches. This file holds the
test that decides whether that works, and the order of the steps. Every number below was measured at authoring (16:3xZ).

## J4, the long-input test (built from J2's held-out labels, so it compares with J2 directly)

| Task | Input (the state) | Question | Labels | Size measured |
|---|---|---|---|---|
| **J4-v1** | the WHOLE verify report the finding came from, class words masked as J2c masks them | "Which class did the verifier give finding <id>?" (one `choice` over J2's six classes) | the 100 rows of `j2-v1-probe/sample.json` (the J2c joins name each row's report and finding id) | 100 rows over 9 reports; the 92 verify reports: median 36,276 bytes, p90 64,023, max 88,251 (about 9k, 16k and 22k tokens) |
| **J4-ap** | the WHOLE anti-pattern registry (every `AF-AP-*` row, full text) | "Which registry row does this incident show?" (one `choice` over every row id) | the 100 incidents of `ap-hawk-probe/sample.json` (their `AF-AP` ids masked, as J2 masks them) | 191 rows, 234,905 characters (about 60k tokens); median row 1,095 characters, max 5,086 |

Why these two: the labels are real and independent (the verifier's class; the row an incident names), J2 already holds the
short-input numbers for the same rows (so J4 answers "does more context help?"), and both inputs are long for real. The first
source tried, verify findings that cite exactly one code file, was too thin: 33 findings over 11 files from 8 reports (measured).

The layout already suits an RNN: simple-jev's v1 prompt lists every question BEFORE the state (its "question briefing"), then the
state, then the one selected question. RWKV reads the briefing and the document once, keeps the state, and answers each question
from a copy of it; Qwen reuses the shared prefix the same way through vLLM's prefix cache.

Baselines, as J2: majority and the keyword heuristic (J4-v1); lexical overlap over the whole registry (J4-ap; J2's lexical top-1
was 0.59 over the lexical 16, whose ceiling is 0.85; the whole registry has no such ceiling). Candidates: Qwen 27B (QJ1; vLLM's
max model length is 131,072 tokens), OpenJev (if its context takes the input; otherwise NOT run, with the reason), Laya over
1,024-token windows (the chunked baseline RWKV must beat), RWKV-7 0.4B before and after training. Samples are committed by digest
before any scoring, as J2's were.

## Steps, in order

1. **QJ1 (running on the PC):** the Qwen 27B Jev adapter and J2 on it. Its J2 numbers decide whether Qwen 27B is a better teacher
   than OpenJev (0.54 on whole findings) or Haiku (0.60).
2. **J4 builder (next lane):** `j4.py sample|inputs|score` beside the J2 scripts, the J2c join and masks reused (loaded, never
   copied); a test that fails if a class word or an `AF-AP` id survives the mask; samples committed by digest.
3. **RWKV G0 (a probe, before any training):** load the pinned checkpoint and answer J4 zero-shot. Open question for this step: the
   HF checkpoint needs flash-linear-attention 0.3.0 (Triton, GPU) and was built for transformers 4.48; the PC has transformers
   5.17.0 and a full GPU while vLLM runs. Either a GPU window (no lanes live, vLLM stopped: the owner's rule for training) or a CPU
   path (a different runtime) is needed even for the probe. G0 measures which works, and the per-decision time at 16k and 60k tokens.
4. **Training data:** long-input items from rows outside J4's held-out samples (the other ledger rows and incidents), with the true
   labels the ledger already holds, plus Qwen 27B soft labels; FT1's builder rules apply (whole text, masked, scrubbed, held-out
   rows excluded by source identity, one resolved commit).
5. **Training in the GPU window:** Laya (FT1's trainer) and RWKV-7 (a trainer on the same answer-token objective as simple-jev's
   RFDT) on the same labels; a small timed run first, then the owner is told the real duration before a long window.
6. **Judge:** J2 (short) and J4 (long) for every candidate; the owner decides which student serves which decisions.

## Not built yet

J4, the RWKV runtime on the PC, any RWKV weights on the PC, the long-input training data, the RWKV trainer. Nothing here is a
claim of capability.
