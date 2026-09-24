# J2 — THE SIGNAL PROBE ON THE TWO LABELED QUESTION TYPES (task #226, D-072 item 1)

| Field | Value |
|---|---|
| Date | 2026-09-24, both runs 13:0xZ-13:4xZ |
| Model | Laya `typed-decisions`, revision `1c5edc17a7acd8701df6fc341c0d179f1c62c982`, FP32 on the sandbox CPU (2 threads), a second local server on 127.0.0.1:47412 |
| Rule | the council's J2 shape (`docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md`): each sample committed by digest BEFORE scoring, baselines printed beside Laya; KC-J3: if Laya's accuracy is at or under max(majority, heuristic), the type is rejected |
| Owner ruling | D-072: J2 runs on `ap.violates_row` and `v1.finding_class` in place of B2 hit-role (0 harvested rows) |

## Verdict

**Laya has no usable signal on either type. Both are rejected by KC-J3.** Plain word overlap beats it on registry matching by
a factor of twelve, and always answering the most common class beats it on finding classes. No method found a single BLOCKER.

## 1. `ap.violates_row` (which registry row does this incident show?)

- Probe: `docs/research/findings/ap-hawk-probe/ap_probe.py`; sample `sample.json` (sha256
  `c07c581ad74201e19efe8b9da61eedd4a4cfcc81c3c10f7036ba20da3aaa2044`, committed 2ea5f62 before scoring): 100 incident headings
  from `docs/INCIDENT-LOG.md` that name 90 of the 184 registry rows, with every `AF-AP-<n>` masked.
- Method: a lexical stage ranks all 184 rows by token overlap and keeps 16; Laya scores those 16 with one `noul` question per
  row through the server's per-chunk fan-out. Results: `results.json` (1,951 s).

| Method | Top 1 | Top 3 |
|---|---:|---:|
| Majority label (AF-AP-30) | 0.09 | - |
| Random within the lexical 16 (expected) | 0.061 | - |
| Lexical overlap | **0.59** | **0.69** |
| Laya reranking of the lexical 16 | 0.05 | 0.22 |
| Ceiling: the label is in the lexical 16 | 0.85 | |

Laya's top picks cluster on a few rows (AF-AP-76 seven times, AF-AP-114 and AF-AP-116 six times each, AF-AP-162 and AF-AP-109
five times each) with scores of 0.68 to 0.84 whatever the heading. It scores the row text itself, not the row's fit to the
incident.

## 2. `v1.finding_class` (which class did the verifier give this finding?)

- Probe: `docs/research/findings/j2-v1-probe/v1_probe.py`; sample `sample.json` (sha256
  `b1cf7867f5995280f1c9298fa48e024b3039ee50ddca1e3626367717c9f27fc9`, committed 14add38 before scoring): 100 of the 144 v1 rows
  a real `scripts/decide-harvest` run produced from the 89 committed verify reports (in a clean sparse worktree at HEAD).
  Stratified: every rare-class row (BLOCKER 7, KNOWN 3, UNVERIFIED 2, CONTRACT-DEFECT 2) plus 43 INFO and 43 FOLLOW-UP. The
  keyword baseline was fixed in the script before scoring. Results: `results.json` (471 s).

| Method | Accuracy | Balanced accuracy | Blocking split | BLOCKER recall |
|---|---:|---:|---:|---:|
| Majority (FOLLOW-UP) | **0.43** | 0.167 | **0.91** | 0/7 |
| Keyword heuristic | 0.41 | 0.159 | 0.78 | 0/7 |
| Laya `choice` over the six classes | 0.21 | 0.133 | 0.82 | 0/7 |
| Laya per-class `noul`, argmax | 0.03 | 0.194 | 0.58 | 0/7 |

The per-class `noul` answers almost always name a rare class (KNOWN 2 of 3, UNVERIFIED 1 of 2, and 0 of 86 on INFO and
FOLLOW-UP); its balanced accuracy edges the majority only because of that. The blocking split (is this finding blocking?) is
best answered by "never", which is the majority's 0.91.

## 3. What this changes

- **The AP-hawk (#115) is not built on Laya.** If it is built, it is lexical: word overlap alone names the right row first 59%
  of the time and within three 69% of the time, deterministically and with no model.
- **Every Jev tool keeps a non-model default order.** The two lanes that rank (JT2's bug locator, JT3's search intercept) were
  told at 13:3xZ: their unranked order is the default unless their own benchmarks show Laya helping, and no Laya score may
  decide what is dropped (KC-J5).
- **The capture plane keeps its value.** KC-J3's own consequence: "only the ledger survives, as a corpus for a possible future
  fine-tune". The J1 ledger now holds the labels a fine-tune, or a better model, would be measured against; this probe is the
  first consumer it has had.
- **MoJev is the next candidate, not a replacement by assumption.** Its Gate 0 (#230) measures whether it fits the PC's CPU; if it
  does, these two samples and scripts rerun against it unchanged, with the same baselines.
- **The one-anecdote trap is recorded** (deep-work Phase 2, 2026-09-24): the single 8-note test at 12:17Z, where Laya put the
  right note first, predicted nothing.

## 4. Limits of this probe

- The `ap.violates_row` inputs are incident headings, a proxy for the AP-hawk's real input (a code hunk, which has no labels).
  The headings were written by the same author who named the row, which favours the lexical baseline; a negative on this easier
  proxy is still strong evidence.
- The v1 sample comes from 11 of the 89 verify reports (the only ones with the grammar), so the rows are correlated by lane.
- One model, one revision, FP32, 2 threads on a shared CPU (timings are not measurements; accuracies are).
- Laya's input window is 1,024 tokens; every state here is far shorter.

## 5. Addendum (14:0xZ): the question, the model, or the task? (J2b, POST-HOC)

The owner asked whether Laya fails or the way we asked fails. Two probes answer it: Laya asked three other ways, and a much
larger general model on the same inputs. Both were chosen after §1-§4, so a win here would be a hypothesis to re-confirm on
rows the samples never used. None won.

### 5.1 Laya asked three other ways (`j2b-variants/j2b.py`; `results.json`; same samples, same server revision)

| Variant | What changed | Result | Best plain baseline |
|---|---|---|---|
| `ap_choice` | one `choice` over the lexical 16: Laya's own coarse-to-fine shape (`laya/shortlist.py`) | top-1 0.22, top-3 0.50 | lexical 0.59, 0.69 |
| `v1_choice_rich` | fuller class definitions; the state keyed as a finding | accuracy 0.14; blocking split 0.63; BLOCKER 0/7 | majority 0.43; 0.91 |
| `v1_blocking` | one yes/no question: does this finding block the merge? | blocking split 0.87; blocking recall 0/9; false alarms 4/91 | "never" 0.91 |

### 5.2 A much larger general model on the same inputs (`j2b-variants/haiku_compare.py`)

Haiku 4.5 as a sandbox agent (37 assistant turns, all Haiku, 0 refusals) read label-free inputs only: the masked heading
with the lexical 16 (each row's first 260 characters, in lexical order), and the v1 state alone. Its answers are recorded
as data (`haiku_ap.json`, `haiku_v1.json`, one run); `haiku_compare.py inputs` rebuilds the exact inputs from the committed
samples and `score` reproduces the numbers.

| `ap.violates_row` | Top 1 | Top 3 |
|---|---:|---:|
| Lexical overlap | **0.59** | **0.69** |
| Haiku 4.5, reranking the lexical 16 | 0.39 | 0.48 |
| Laya `choice` (5.1) | 0.22 | 0.50 |
| Laya per-row `noul` (§1) | 0.05 | 0.22 |

Haiku left the lexical first pick in 42 of 100 rows. It was right in 2 of them; the lexical pick was right in 22.

| `v1.finding_class` | Accuracy | Balanced accuracy | Blocking split | BLOCKER recall |
|---|---:|---:|---:|---:|
| Majority (FOLLOW-UP) | 0.43 | 0.167 | **0.91** | 0/7 |
| Haiku 4.5 | **0.45** | **0.278** | 0.88 | 0/7 |
| Laya `choice` (§2) | 0.21 | 0.133 | 0.82 | 0/7 |

### 5.3 Two input limits, found while reading the inputs

1. **The v1 state is a 120-character title.** The `v1.finding_class` schema caps `title` at 120 characters
   (`SCHEMAS` in `src/agent_factory/decisions/volatile.py`); 59 of the 100 sampled states are exactly 120 characters, cut
   mid-sentence. The class depends on reproduction, contract mapping and materiality, which live in the finding's body.
   No model saw them.
2. **Laya gives each option a few tokens.** The question and all its options share `head_max_len` = 256 tokens
   (`typed-decisions/rl_agent_config.json` at the pinned revision; `build_sequence` in `laya/common.py`). With 16 options,
   each keeps at most 15 tokens, its marker included: the row id and a few words. Laya's own `shortlist` module says so
   ("a large label set leaves only a few tokens per label"). The design fits short labels over a long state, not long
   registry rows as labels.

### 5.4 What this says

- Laya is the weakest model on every shape tried. It never beat a plain baseline, and it trailed Haiku on both tasks.
- The two tasks, as posed, are also weak tests of any model. In registry matching the heading and the row share their
  author's words, so word overlap is the strongest signal and a model that leaves it is usually wrong. In finding class
  the input is a 120-character title.
- So the evidence rejects Laya as it ships, on these inputs. It does not show that no model can help, and it does not
  test Laya's design shape (short typed questions over a long state).

### 5.5 Open paths that keep a model in the loop (owner, 2026-09-24 13:48Z: a non-model version "defeats the purpose")

1. The locator benchmark (JT2, `jev-locate-bench`) measures Laya on the owner's main use: ranking files for a bug from
   all the tools' output. It reads the same KC-J3 rule.
2. Re-ask v1 with the whole finding (the report paragraph, class words masked) to Laya and Haiku. If accuracy rises, the
   capture schema's 120-character title is the limit to fix, through the redaction layer.
3. Use a model beside the plain order, not in place of it (the model reorders only lexical ties, or a measured blend).
4. Fine-tune Laya on the ledger's labels (the council's KC-J3 consequence). The package ships no training code, and the
   labels are few today (144 v1 rows).
5. MoJev (Gate 0, task #230), the hosted Laya model (needs the owner's key through OmniRoute), or the local Qwen through
   OmniRoute where a few seconds per call is acceptable.

## 6. J2c (15:1xZ): the whole finding, not its title (POST-HOC; `j2c-fulltext/`)

The same 100 v1 rows, each re-joined to its verify report through decide-harvest's own parsing helpers (82 exact joins,
18 on a unique 40-character prefix where the ledger had redacted or normalized the title). A bullet finding keeps its whole
paragraph; a table row keeps its full title cell (its other cells carry the verifier's class notation). J2's MASK hides the
class words, and a parenthesised qualifier after a masked word is dropped. State length: median 258 characters, maximum
2,071 (was 120). The sample was committed by digest before scoring (`sample.json`, sha256
`af469599e3e1054241c75f7b81eec5ae0214136d88fbbbbf6b8701e404b44df3`); Laya was scored by the UNCHANGED J2 scorer
(`v1_probe.py score`, 533.5 s); Haiku 4.5 read label-free inputs only (13 turns, all Haiku, 0 refusals; its answers are
`haiku_v1_full.json`, scored by `j2c.py score-answers`).

| `v1.finding_class`, whole finding | Accuracy | Balanced accuracy | Blocking split | BLOCKER recall |
|---|---:|---:|---:|---:|
| Majority (FOLLOW-UP) | 0.43 | 0.167 | **0.91** | 0/7 |
| Keyword heuristic | 0.32 | 0.223 | 0.66 | 1/7 |
| **Haiku 4.5** | **0.60** | **0.364** | 0.85 | **4/7** (blocking recall 5/9, false alarms 11/91) |
| Laya `choice` | 0.17 | 0.209 | 0.59 | 2/7 |
| Laya per-class `noul` | 0.10 | 0.242 | 0.59 | 1/7 |

Beside the title-only numbers (§2, §5.2): Haiku 0.45 to 0.60 accuracy and 0/7 to 4/7 blockers; Laya `choice` 0.21 to 0.17
accuracy and 0/7 to 2/7 blockers.

**What this says.** The 120-character title capped every model: from titles no model found a blocker. With the whole
finding, a general model beats the plain baseline for the first time on either J2 task, so the task is learnable from this
text. Laya stays below the majority even with the whole finding, so its limit is the model (training and capacity), not
only the input. Two consequences for the fine-tune (task #233, D-075): train and evaluate on whole findings, never on
ledger titles (and fix the capture schema's 120-character cap with AF-AP-189's `disposition` leak, task #238); and the
teacher must be a model that can do the task (Haiku reached 0.60 here; OpenJev is untested pending the owner's data OK).

Limits: POST-HOC; 76 of the 100 rows are table rows whose "whole finding" is only their full title cell; the verifier's
own reasoning words (for example "reproduced", "blocks") stay in the text, as they would for any reader; one run each.

## 7. OpenJev 0.1 on the same samples and scripts (16:3xZ; task #234, D-078; `j2b-variants/openjev_j2.py`)

J2's rule for a new candidate (§3): the same samples and scripts, unchanged, with the same baselines. `openjev_j2.py` loads the
committed probe scripts and swaps only their `post`: model `openjev-latest` on codiv.ai, every string through
`transcript_export.scrub` first, one chunk per request for fan-out questions, at most one request per 1.05 s. The run
(15:1xZ-16:3xZ) sent 3,300 requests and 851,486 input tokens and finished all six variants; the outputs are
`j2b-variants/openjev/*.json` (`usage.json` holds the per-variant counts and times).

| `v1.finding_class` | Input | Accuracy | Balanced accuracy | Blocking split | BLOCKER recall |
|---|---|---:|---:|---:|---:|
| Majority (FOLLOW-UP) | either | 0.43 | 0.167 | **0.91** | 0/7 |
| Haiku 4.5 (§6) | whole finding | **0.60** | **0.364** | 0.85 | 4/7 |
| **OpenJev `choice`** | whole finding | 0.54 | 0.341 | 0.83 | 4/7 |
| OpenJev per-class `noul` | whole finding | 0.14 | 0.253 | 0.32 | 6/7 |
| Laya `choice` (§6) | whole finding | 0.17 | 0.209 | 0.59 | 2/7 |
| Haiku 4.5 (§5.2) | title | 0.45 | 0.278 | 0.88 | 0/7 |
| OpenJev `choice` | title | 0.45 | 0.226 | 0.80 | 0/7 |
| OpenJev per-class `noul` | title | 0.10 | 0.150 | 0.26 | 3/7 |
| OpenJev `choice`, rich definitions (J2b) | title | 0.49 | 0.242 | 0.76 | 0/7 |

The one yes/no question on the title (`v1_blocking`): OpenJev blocking split 0.89, blocking recall 1/9, false alarms 3/91;
Laya 0.87, 0/9, 4/91; "never block" 0.91. OpenJev's per-class recall on whole findings: FOLLOW-UP 39/43, INFO 10/43,
BLOCKER 4/7, KNOWN 1/3, CONTRACT-DEFECT 0/2, UNVERIFIED 0/2.

| `ap.violates_row` | Top 1 | Top 3 |
|---|---:|---:|
| Lexical overlap | **0.59** | 0.69 |
| **OpenJev `choice` over the lexical 16** | 0.58 | **0.74** |
| OpenJev per-row `noul` | 0.20 | 0.40 |
| Haiku 4.5 reranking (§5.2) | 0.39 | 0.48 |
| Laya `choice` (§5.1) | 0.22 | 0.50 |
| Laya per-row `noul` (§1) | 0.05 | 0.22 |
| Ceiling: the label is in the lexical 16 | 0.85 | |

**What this says.** (1) OpenJev reads whole findings nearly as well as Haiku (0.54 against 0.60, the same 4 of 7 blockers)
and far better than Laya (0.17), so it can teach this question; it is not a strong teacher (balanced accuracy 0.34; it
calls most INFO findings FOLLOW-UP), and its soft labels carry that bias. (2) The shape matters as much for OpenJev as for
Laya: one `choice` question beats one `noul` per class (0.54 against 0.14) and one `noul` per row (0.58 against 0.20). The
per-class `noul` finds 6 of 7 blockers only by flagging most findings (blocking split 0.32). (3) On registry matching,
OpenJev is the first model to reach the lexical baseline: level at top 1 (0.58 against 0.59), ahead at top 3 (0.74 against
0.69). It does not beat it at top 1, so the lexical order stays the default there (§3; D-077 for the locator). (4) The title
still caps every model (no blocker found from titles by any model).

Limits: POST-HOC; one run; a hosted model whose weights and revision are not pinned (`openjev-latest` served as
`openjev-0.1`), so a rerun may differ; the same sample limits as §6 (76 of the 100 v1 rows are table rows).
