# PIJEV-ORDER-PROBE-1 — does our Laya endpoint shift its choice answers with option order? (2026-09-23)

**Answer: yes, mildly.** On two three-option cases, one option's probability moved by up to 6.2 points across the six option orders. The winner held in every order. A batch of all six orders in ONE request returned exactly the per-order answers of six separate requests. The math that removes the shift (pijev's permutation averaging) runs on our own endpoint with no hosted API and no key. Decision: D-050 (the averaging becomes a scored arm of J2, not an assumption).

## Sources
- **pijev** — `TypeLLM/pijev` @ `bca3a73d6419b794d63cd780ba4a0254579d7ccc` (2026-09-22, 3 commits, v0.1.0, Apache-2.0), cloned to `/home/user/typellm/pijev` for STATIC READING ONLY: nothing from it was installed, imported or run. `pijev/__init__.py` sha256[:16] `5e2d79b6070ccaad`, 178 lines. It subclasses the hosted TypeSafe SDK client (`from typesafe_sdk import TypeSafeClient`, `pyproject.toml` depends on `typesafe-sdk>=0.7.1,<0.8`).
- **Our probe** — `docs/research/findings/pijev-order-probe/order_probe.py` (sha256[:16] `3c8ff2a7e2c8cd42`; stdlib only; written by the coordinator), run on the PC as user rocco against the live loopback endpoint `http://127.0.0.1:47411/v1/systemone` (the PCJ1 unit `laya-systemone.service`: Laya `1c5edc17`, `typed-decisions`, CPU, 8 threads). Raw output `docs/research/findings/pijev-order-probe/probe-2026-09-23.json` (sha256[:16] `05ae4974c3dbe411`, equal on both hosts). The endpoint's `calls` counter read 10 before the run.

## What pijev does (static reading, `pijev/__init__.py`)
- `_prepare` (:23-62): each Choice question becomes M copies whose `criteria` are re-ordered (all K! orders when the budget covers them, else a seeded sample without replacement); Noul and Score pass through unchanged; at most 720 expanded questions.
- `_aggregate` (:65-103): each copy's answer must carry exactly the requested labels, finite probabilities in [0, 1] summing to 1 within 1e-3; each row is renormalized, the rows are averaged per label, the winner is the highest mean (ties broken by the sorted label order), and `confidence` becomes the winner's mean probability (not Jev's native confidence).
- The guarantee it claims (README) is Jensen's inequality: the averaged prediction's convex loss (log loss, Brier) is never worse than the mean loss of the included orders — i.e. never worse than a randomly chosen order. It is not a guarantee against the best order, and not an accuracy guarantee.

## Measurement (2026-09-23 ~01:3xZ; separate = one request per order; batch = all six orders as questions of one request)

| Case | Option | Min over 6 orders | Max over 6 orders | Spread | Mean (the averaged answer) |
|---|---|---:|---:|---:|---:|
| ticket (pijev's README example) | billing | 0.5272 | 0.5893 | 0.0621 | **0.5584** |
| | technical | 0.2127 | 0.2693 | 0.0566 | 0.2394 |
| | account | 0.1763 | 0.2293 | 0.0530 | 0.2022 |
| lane (our routing example) | evidence-gatherer | 0.4922 | 0.5420 | 0.0498 | **0.5097** |
| | adversarial-verifier | 0.2655 | 0.3088 | 0.0433 | 0.2854 |
| | code-implementer | 0.1926 | 0.2161 | 0.0235 | 0.2049 |

| Property | ticket | lane |
|---|---|---|
| Winner in all six orders | billing (6 of 6) | evidence-gatherer (6 of 6) |
| Mean squared disagreement = the Brier gain of the average over a random order | 0.00115 | 0.00061 |
| Batch vs separate, largest per-order difference | 0.0000 | 0.0000 |
| One question per request, seconds | 0.28-0.31 | 0.31-0.32 |
| Six orders in one batch, seconds | 1.11 | 1.41 |
| HTTP status of every request | 200 | 200 |

For comparison, pijev's README reports the hosted `jev-1.13.0` giving `billing` 0.46-0.64 across the same six orders of the same ticket (an 18-point spread). Laya's spread on that case is about a third of it.

Laya's choice answer carries `choice`, `probabilities` (per label, summing to 1), a native `confidence` (0.057-0.126 here — not the winning probability) and `action.act_probability` (1.0 here).

## Reading
- The order effect is real on Laya but small on these cases; it matters where a Laya probability feeds a threshold or where two options are within a few points. Two hand-picked cases cannot say how often a winner flips: that needs the labeled set.
- Batching the orders is exact on Laya (each question of a batch is answered independently of its neighbours), so the averaged answer costs one request. On CPU the six-order batch took about four times one question's time.
- The council's multiple-choice decision points are B2 hit-role (5 options, 120 orders) and B1 finding severity/kind (3 options). The first place Laya answers them against real labels is J2 (the 100 hand-labeled B2 cases, KC-J3, due 2026-10-20). D-050 puts the averaging there as a scored arm across permutation budgets, so the gain per budget is measured under the KC-J2 latency ceiling instead of assumed.

## NOT done here
- No sweep over J0's fixture set (how often the winner flips at scale) and no 5-option case (cost and spread at K = 5).
- Yes/no (noul) questions were not probed for sensitivity to the order of their `true`/`false` criteria; pijev does not average them either.
- No accuracy or calibration claim: no labels were involved.
