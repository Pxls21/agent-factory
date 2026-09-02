# Council Verdict — Stage 0 execution strategy (2026-09-02)

> Produced by `/council` (full mode, debugging triad) on `FINDINGS-STAGE0-v1.md`. Chairman
> synthesis verbatim below; coordinator reproduced both Chairman probes before committing
> (see findings §6a). Feeds the Ouroboros interview as the constraint set.

## Council Verdict

### Problem
Stage 0 execution strategy for `agent-factory` (governed, memory-aware agent system; planning docs complete, zero application code). Three questions: (1) proof ordering/parallelism across S0-01…S0-12 given the probed environment; (2) which proofs may accept spec+fixture evidence with deferred live execution vs must block on real execution; (3) the biggest hollow-green risks and the negative controls that kill them. Factual base: `docs/research/FINDINGS-STAGE0-v1.md` (probed capability ledger + environment table), cross-read this session against `docs/07_BUILD_PLAN.md:5-20`.

### Council Composition
- **council-feynman** (sonnet, 1.5× domain-weight seat) — empirical-verification epistemology; "physical fact decides sequence."
- **council-socrates** (opus) — dialectical falsification; "a proof pack is a falsification budget."
- **council-ada** (sonnet) — systems mechanization; DAG modelling, what is and isn't automatable.

Round 2 was anonymized to the members (A/B/C); names restored in the transcript for audit. Three rounds plus an enforcement round of counterfactuals.

### Chairman
Synthesizer only — did not deliberate, cast no vote, and holds no seat weight. Independent verification performed this session: read the findings doc in full; confirmed Ada's structural claim that `docs/07_BUILD_PLAN.md` Stage 0 is a flat `ID | Proof | Exit evidence` table with **no dependency column** (her reconstruction is therefore genuinely a hypothesis, as Socrates charged); confirmed `upstream.lock.yaml` and `LICENSE-DECISION.md` exist as S0-12 cites; reproduced the mid-deliberation netns probe and extended it with a selective-egress leg the panel never ran.

### Provider Routing
All three seats and the Chairman ran on Anthropic models (opus for Socrates, sonnet for Feynman and Ada). **Single provider — no cross-provider routing.** Model-tier diversity (opus/sonnet) is not epistemic diversity; it is a capability gradient within one training lineage. This is the scorecard's binding weakness and should be read as a caveat on the unanimity, not a feature of it.

### Acceptable Compromises
1. **S0-08's live run is deferred; its resolution is not.** Spec + fixture + a machine-checkable `NOT run here: <reason>` marker is accepted evidence *only* when paired with procurement of a real gVisor host as a named Wave-0 action item. Socrates' distinction — deferring the run ≠ deferring the resolution — carried unopposed.
2. **S0-04's deterministic upstream stub stands as the one sanctioned instrument**, because the plan itself specifies it at the boundary behind real OmniRoute (findings §4). This is a boundary instrument, not a spine stub.
3. **S0-09 / S0-10 / S0-12 are accepted as decisions with falsifiable conformance shells**, not execution proofs — admissible only in a separate ledger column, never in an execution denominator.
4. **S0-05 ships split**: mechanism in Wave 0, full architectural proof in Wave 2, labelled verbatim *"mechanism proven, containment unproven."*
5. **Verification-batching is accepted as a subordinate parallel measurement**, not a competing schedule axis — Ada herself agreed it does not override absent flip evidence.

### Kill Criteria
1. **If, within the first Wave-0 execution session, the S0-05 mechanism spike cannot demonstrate *selective* egress — a contained unit reaching OmniRoute while failing to reach a model endpoint** — then the verdict's Wave-0 placement of S0-05's mechanism is invalidated, and S0-05 must be re-scoped as an egress-broker design proof (veth/proxy) *before* any canary is authored. (Chairman probe evidence: the currently-proven mechanism blocks both legs.)
2. **If no named owner and date for a real upstream credential exists by the close of the first Wave-1 execution session**, S0-03 must be marked RED-pending and Stage 1 must not open. Running S0-03 against S0-04's stub invalidates the verdict outright.
3. **If the Wave-0 Rust spike shows `ai-memory` builds on the installed 1.94.1 or that 1.95 is fetchable**, Ada's "blocked-but-procurable" label for S0-06 is falsified — reclassify it as an execution proof and re-issue the denominators in the same session.
4. **If any Stage 0 status line published during Wave 1 reads as a flat "N/12"**, the three-way classification has failed in practice; halt and re-issue the ledger with separate denominators before further proof work.
5. **If two or more Wave-1 proofs pass without a negative control that fails for a named exact reason**, negative-control discipline has decayed — halt Wave 2 until the passing proofs are mutation-audited.
6. **If the dockerd-in-sandbox Wave-0 spike succeeds**, the process-level-first premise weakens — within that session, re-test whether S0-08 is procurement-blocked or merely container-blocked.
7. **If the S0-07 pilot clearance measurement shows adversarial-verification time exceeding the wall-clock saved by parallelism by more than 2×**, Ada's counterfactual is confirmed and the waves must be re-cut by verification technique.

### Concrete Next Step
**Write a Chairman-verified addenda section into `docs/research/FINDINGS-STAGE0-v1.md`** recording, with the exact probe commands and outputs: (a) the reproduced positive/negative netns pair; (b) the new selective-egress result showing the bare netns also blocks a host-local listener; (c) the S0-03 classification gap; (d) the S0-06 class disagreement. The interview and the seed both read this file as their constraint set — shipping them without (b) bakes a vacuous S0-05 negative control into the seed. *(Executed: findings §6a, same commit as this verdict.)*

### Unresolved Questions
1. **Who supplies S0-03's real upstream credential, and by when?** Open in findings §5 PATH-2 #3 *before* the council convened, and still open after three rounds. Socrates' closing question is the sharpest form: if no credential exists when Wave 2 opens, does S0-03 block RED-pending, or run against S0-04's stub — and if the latter, **what assertion distinguishes a real model answer from the stub?** No member offered one. If none exists, Stage 0's most load-bearing green is hollow by construction.
2. **Which class does S0-03 occupy?** The crystallized three-way split enumerates 7 + 3 + 1 = **11 of 12**. S0-03 is unenumerated. It appears to need a fourth class — *execution proof blocked on an external input* — structurally distinct from S0-08's *blocked on a kernel feature*, because a credential is procurable on a different timescale and by a different owner than a host.
3. **Is S0-06 an execution proof or procurement-blocked?** Feynman lists it among the 7; Ada's R2 concession moves it to blocked-but-procurable pending exact-1.95. Both agree the *action* is a Wave-0 cargo spike; they disagree on the *label*, which matters only because the label sets the honest denominator.
4. **Can S0-05's mechanism be made selective?** Unexamined by the panel. Chairman probe: a bare `unshare --net` netns blocks a host-local OmniRoute as thoroughly as it blocks the internet. Necessary for containment, insufficient for the architecture.
5. **Does a real gVisor host exist to procure?** Socrates demanded a named owner and date. The transcript contains no owner. Procurement is asserted as possible, never as available.
6. **Ada's verification-scheduling counterfactual is unmeasured.** The panel agreed the S0-07 pilot measurement is cheap and worth running; nobody ran it. It remains a live alternative, not a rejected one.
7. **Can S0-11 run on process-level primitives?** Ada speculated `unshare` suffices since it is distinct from S0-08's kernel requirement. Untested. Relatedly, what "rubric isolation proof" concretely asserts was never pinned to an assertion.
8. **Nobody argued the cost side.** No seat held the view that twelve gating proofs before any feature work is itself the dominant schedule risk. That position was structurally absent, not defeated.

### Recommended Next Steps
1. Execute the Concrete Next Step above; commit before any further dispatch (the repo's own incident log records an agent lost to an uncommitted-doc dispatch on day one).
2. Run the Wave-0 spike matrix as four independent, parallel, minutes-scale probes: Rust-1.95 availability · dockerd-in-sandbox · runsc static install · **selective**-egress netns (veth/proxy, not bare `unshare`). Each returns a fact that reorders the plan; none depends on another.
3. Resolve the classification arithmetic to a **four-way** ledger — execution / conformance-checked decision / blocked-on-external-input (S0-03) / blocked-on-capability (S0-08, provisionally S0-06) — with separate denominators and no flat "N/12" anywhere.
4. Put question 1 to the owner as a PATH-2 text question *now*, in parallel with Wave 0, rather than at Wave 2's opening — the answer has a procurement lead time the schedule cannot absorb late.
5. Author every proof's negative control at spec time, before its positive leg, each naming the exact expected error or exit code. Feynman's four kills are the seed set: S0-05 asserts the exact denial reason and dies when the gate is mutated off; S0-04 dies when OmniRoute's real header-set code is mutated; S0-02 demands four *distinct* error reasons, not four failures; S0-08's `NOT run here` marker is grep-checked and gates Stage 1.
6. Run the S0-07 clearance-time pilot alongside Wave 1 so Kill Criterion 7 is decidable.
7. Carry this verdict plus the amended findings into the Ouroboros interview as the constraint set, per the repo's pipeline order (interview → seed → task breakdown → build).

### Consensus & Agreement
Unanimous adoption of **wave-plan-v2**, all three at high confidence, no dealbreakers. Four load-bearing agreements:
- **Three-way classification replaces a flat proof count.** Originated with Socrates' denominator-inflation argument, corrected by Feynman's conformance-shell distinction, adopted by all three. Status lines never read "N/12."
- **Capability facts are logically prior to schedule.** Wave-0 spikes precede proof work, because you cannot schedule — or batch-audit — a proof that cannot yet execute.
- **Falsification power, not throughput, is the sort key.** Ada conceded her topological sort optimized the wrong objective.
- **S0-03 blocks on a real credential, and a pass must assert upstream model identity — never a 200.** Socrates held this from R1 through R3 unopposed; it is the pack's single most important assertion.

### Vote Tally
> wave-plan-v2 — 3.5 (Feynman [1.5×, domain], Socrates, Ada) ✅ cleared 2.333 threshold (W_total 3.5). Unanimous. No dealbreakers.

### Key Insights by Member
- **Feynman** — *the mechanism/proof split.* His enforcement-round counterfactual refused the consensus's wholesale deferral of S0-05 and separated its containment *mechanism* (zero-dependency, minutes) from its *architectural proof* (needs a live OmniRoute-fronted unit), with an explicit flip condition. The probe ran, the mechanism worked, and the plan changed. This is the only position in the deliberation decided by measurement rather than argument. His self-indictment of his own 8/12 tally — bucketing S0-09/10/12 as "real-here" without separating decision content from checkable artifact — is what made the three-way split possible.
- **Socrates** — *stub-drift as the pack's characteristic hollow green.* S0-03 and S0-04 both terminate at OmniRoute's upstream edge; if S0-03 runs against the sanctioned S0-04 instrument, the instrument silently becomes the spine and S0-03 proves only that Hermes reaches OmniRoute — never that a model answered. The remedy (assert upstream model identity, with a credential-disable kill switch) is the strongest single control the council produced. Equally sharp: a gate that cannot fail is not a proof, and counting it inflates the denominator.
- **Ada** — *the plan has no stated dependency edges.* Verified: `docs/07_BUILD_PLAN.md` Stage 0 is a flat three-column table; all precedence in circulation is reconstructed from narrative. This is a concrete defect in a ground-truth document, found by reading rather than reasoning. Her R2 correction of Socrates — that S0-05's under-instrumentation is a *fixture* problem, not a *venue* problem, so his own remedy is executable here — is what unblocked S0-05 and set up Feynman's split.

### Points of Disagreement
1. **S0-06's class — unresolved.** Feynman: execution proof. Ada (R2): blocked-but-procurable pending Rust 1.95. Round 3 locked the wave plan without reconciling it. The disagreement is about the label, not the action — both want a Wave-0 cargo spike — but the label sets a denominator, so it must be settled by Kill Criterion 3 rather than by preference.
2. **Are Ada's dependency edges constraints or hypotheses?** Socrates: her own caveat concedes S0-03 may be fixture-testable without live S0-01, so the edge is a hypothesis. Ada conceded the *objective* (falsification over throughput) but never retracted the edges. Unresolved, and it matters: if S0-01→S0-03 is not forcing, the spine sequence can be partly parallelized.
3. **Throughput logic survives inside the falsification frame.** The council rejected throughput as the sort key, yet Wave 0's four-spikes-in-parallel and Wave 1's six-proof batch are throughput moves. Nobody named the tension; it is benign here only because Wave-0 spikes are independent by construction.
4. **Verification-batching's status.** Feynman: a real secondary axis that optimizes review of a wave plan, and cannot replace it. Ada: an open cheap measurement to run in parallel. Compatible in practice, but not the same claim — Feynman subordinates it permanently, Ada subordinates it pending a measurement.

### Minority Report
No member dissented and no dealbreaker was raised, so there is no minority position in the voting sense. Two items are nonetheless held open rather than defeated, and should not be recorded as settled:

- **Ada's verification-scheduling alternative.** Stage 0 may be verification-scheduling rather than execution-scheduling, with reviewer bandwidth — not wall clock — as the binding constraint. It was explicitly preserved as an open measurement with a stated flip condition, never argued down. Socrates' counter (reviewer bandwidth is reschedulable, a falsified architecture is not) is a priority argument, not a refutation.
- **Chairman's reservation — not a member position, recorded so it is not mistaken for one.** The unanimity settled proof *ordering* while leaving both of Stage 0's genuine external dependencies unowned: S0-03's credential and S0-08's host. A plan can be perfectly ordered and still stall on inputs nobody was assigned to procure. I would not treat the unanimous verdict as authorizing Wave 1 until question 1 has a named owner.

### Epistemic Diversity Scorecard
- **Perspective spread: 3/5.** Three genuinely distinct methods — empirical measurement, dialectical falsification, systems mechanization — that produced different first moves and caught each other's errors. But all three share a verification-first epistemology. No seat argued schedule, cost, or the possibility that the proof pack is over-engineered; that view lost by absence, not by argument.
- **Provider spread: 1/5.** Single provider (Anthropic), two tiers. Model-tier variation is a capability gradient within one lineage, not independent epistemics. Correlated blind spots are expected and were observed — see convergence risk.
- **Evidence mix (approximate): ~45% primary-source document reading** (findings ledger, `docs/07`, per-proof constraints traced to `docs/02`/`03`/`05`); **~30% live probe/measurement** (the environment table, the mid-deliberation netns probe, and the Chairman's two reproductions); **~25% analytical reasoning without direct measurement** (dependency edges, class assignments, hollow-green taxonomy). The measured fraction is unusually high for a planning council and is the main reason the verdict is trustworthy on ordering.
- **Convergence risk: moderate (3/5) — the unanimity is substantially earned, and blind on the axes nobody was seated to argue.** Earned, on evidence: each member named a *specific* flaw in their own prior position and updated on it — Feynman that his 8/12 tally conflated decision content with checkable artifact; Socrates that he sorted by deliverable type rather than machine-checkable conformance; Ada that her topological sort optimized the wrong objective and that "S0-08 exits the graph" was wrong, since capability absence is mutable by procurement. The enforcement round then produced a falsifiable flip test that was actually executed, and the result *moved* the consensus (S0-05's mechanism from Wave 2 to Wave 0). Convergence that survives a run probe is not conformity. Against that: three seats, one provider, one epistemology, and a unanimous verdict that nonetheless missed an unclosed 11-of-12 classification and a selective-vs-total egress distinction — both of which surfaced within minutes of independent probing. Read the unanimity as strong on *how to order proofs* and weak on *whether the inputs exist*.

### Follow-Up
Re-convene only on a Kill Criterion firing, or on either of two triggers. **Trigger A:** the Wave-0 spike matrix returns — if the selective-egress spike fails (KC-1) or dockerd succeeds (KC-6), the wave plan's premises changed and the panel should re-cut Waves 1-2 on the new capability table, with a seat added to argue schedule cost. **Trigger B:** the owner answers the S0-03 credential question — if the answer is "no credential available," the council must return to design the identity assertion Socrates demanded, or formally re-scope S0-03, before Wave 2 opens. Absent those, no re-convening: the plan is executable and its open questions are owner-decisions, not council-decisions.

---

### Session Metadata

```
schema_version: 1
mode: full (auto-selected debugging triad)
panel_size: 3
rounds_run: 4   # restate gate + R1 + R2 + enforcement counterfactuals + R3; R1 partially re-run after a container restart
chairman_failed_fallback: no
tools_used: yes   # members read findings/docs; coordinator and Chairman ran live netns/listener probes
input_tokens_estimate: ~700k (subagent total)
output_tokens_estimate: ~20k
duration_seconds: ~2600 (wall, including one container restart + agent recovery)
provider_count: 1
fallbacks_triggered: none (provider-level); 2 agents re-dispatched after container restart (Ada R1, Feynman/Socrates R2 as fresh instances; Socrates R1 recovered from transcript)
```
