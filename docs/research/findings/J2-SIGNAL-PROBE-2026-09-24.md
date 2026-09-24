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
