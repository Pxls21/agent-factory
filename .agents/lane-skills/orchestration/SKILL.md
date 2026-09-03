---
name: orchestration
description: Delegation and coordination for multi-agent builds, any project — Claude-5 brief-writing, the ORCHESTRATOR protocol (disjoint boundaries, worktree pins, push-reviewed-SHA, vocabulary locks), parallel-agent meta-rules, coordinator token economy, and SUCCESSION (no-Fable operation). Load before authoring any delegate brief, dispatching parallel agents, reviewing/pushing delegate work, or coordinating a multi-agent wave. the project instructions file carries the routing table and non-negotiables — this skill is the authoritative expansion.
---

> **HARNESS PORT.** This copy is read by Codex CLI (`.agents/skills/`) and by Hermes
> (via `skills.external_dirs`). It is the same protocol as `.claude/skills/orchestration/SKILL.md`;
> only lines naming a Claude-Code-specific mechanism were reworded — see `docs/HARNESS-PORTS.md`.
> "the project instructions file" = `AGENTS.md` on Codex, `.hermes.md` on Hermes.
> Model-tier names below ("Fable light", "Opus 5 lane") are PROTOCOL LABELS, not routing
> instructions: these harnesses run ONE model. Where the protocol calls for an independent
> verifier, hand the work BACK to the sandbox lane — never self-accept.

# Orchestration — briefs, delegation, coordination

the project instructions file carries the model-routing table, FABLE-SAFEGUARD, MAIN-LOOP FOCUS and explicit-model
rules (always in context). This skill is the full expansion of everything else about running
delegates well.

## CLAUDE-5 PROMPTING & DELEGATION (2026-07-27 — source: Anthropic model docs, primary)

The Claude 5 family (Fable 5, Opus 5) is tuned for goal-level prompting; prompts written for
prior models are often TOO PRESCRIPTIVE and REDUCE output quality. Cross-checked against two
owner-supplied third-party repos (Archive228/adversarial-contract-gate — the "agents that run
for hours" webinar distillation; Lunarsong/Claude-Opus-5-tools) — both consistent with, and
subordinate to, the Anthropic docs.

0. **Absence claims and new names are verified AT BRIEF TIME (AP-43, 2026-08-27).** Any
   "no X exists / not built / no consumer" premise a brief consumes gets its own
   named-instrument verification (grep/graft the exact identifier) IN the brief; every new
   env-var or telemetry-event name is repo-grepped before the brief ships. The incident: a
   findings doc's false "no generic battery selector exists" was adopted unverified → a
   delegate built a colliding duplicate of the live GA_OBJECTIVES seam whose own gate files
   were in the session's known-failing list the whole time.
0a. **Every path a brief names carries CREATE / MODIFY / READ (2026-09-03, agent-factory).** A
   deliverable written as "`proofs/<id>/spec.json` (schema `proofs/schemas/spec.schema.json`: …)"
   read as "that schema exists"; the lane's premise check found no such file and halted (correctly,
   AP-43 shape) — one dispatch round for a missing tag. New schemas/contracts a lane must create
   are given IN FULL in the brief ("copy, do not redesign"); a lane never invents an authoritative
   shape.
0b. **A research doc's FORMULA is a paraphrase, not a spec (2026-08-28).** Before a brief
   adopts a metric/threshold formula from findings prose, check its grain and units against a
   KNOWN MEASURED instance of the same quantity; where prose and prior measured values imply
   different definitions, the measured values' implied definition wins. The incident: RP-30's
   "DC = median(r_cand|bear)/median(r_ETH|bear)" was copied verbatim into the scorer brief —
   at hourly grain that is noise division (healthy tokens scored 9.5/−3.5); the council's own
   measured down-captures (BTC 0.54-0.67) were cumulative episode-return ratios all along.
   One comparison against a known number at brief time beats a build-run-repair round.
1. **Briefs state GOAL + CONSTRAINTS + EVIDENCE DEMANDS, not enumerated steps.** Let the model
   derive the how — that is what the reasoning is for. Enumerate steps ONLY where ordering is
   load-bearing (mutation-restore discipline, record-before-side-effect, safety carve-outs).
   Do-nots, seams, and gate demands are constraints, not steps — they stay.
2. **Opus 5 delegate tuning (measured behavioral shifts, per Anthropic):**
   - It over-verifies unprompted — DELETE "double-check/verify N ways" scaffolding from briefs;
     the deterministic gates remain the only verification that counts, and the coordinator
     re-runs them regardless (self-verification prose just burns delegate tokens).
   - It delegates readily (opposite of 4.8) — every brief carries "do NOT spawn subagents"
     unless fan-out IS the brief's purpose (our disjoint-file model needs exactly one pair of
     hands per boundary).
   - Scope discipline must be EXPLICIT in the brief: "touch ONLY the named files; report
     adjacent defects, never fix them" — the Karpathy surgical-changes rule no longer transfers
     implicitly.
   - Reviewer briefs NEVER carry a severity filter — filters depress recall on Opus 5; demand
     report-EVERYTHING, rank/filter downstream in the main loop (matches the roast pattern).
   - `effort: low/medium` is unusually strong on Opus 5 — prefer dropping effort over dropping
     tier for mechanical work when the task needs opus-scale context.
3. **The brief is a HYPOTHESIS (adopted from working-agreements, consistent with Phase 0).**
   A delegate's FIRST action: verify the brief's premises against the live tree (seams exist at
   the stated file:line, the defect reproduces) and HALT LOUD on contradiction — never build on
   a premise the tree refutes. This is the delegate-side mirror of "reproduce before believing
   any recorded diagnosis."
4. **Adversarial-evaluator-over-self-evaluation** (the webinar's core claim, 39:00) is already
   law here (deep-work Phase 5, SUCCESSION rule 1: never self-accept) — no change; noted so
   nobody re-imports it as new. The SPECIFIC loop shape (negotiate contract → build →
   independent evaluation against the FULL contract → bounded repair → fail closed) is the
   `contract-gate` skill — run it for every serious increment.
5. **Working agreements folded in (from the audited working-agreements.md; the rest were
   already law here):** (a) comments are CLAIMS — verify against code before relying on one,
   and a change that falsifies a nearby comment fixes that comment in the SAME change;
   (b) never reason about correctness from timestamps — exit code + running the result;
   (c) a REVERSED conclusion mid-task is a stop signal: you never had the whole chain — stop,
   enumerate the full layer chain (skill `trace-the-chain`), never report the newest sample as
   the answer; (d) "is X enabled / did we fix Y" answers are CHAINS, not values — every layer
   gets file:line + a git date, table before verdict.

Self-correction: monitor child output for degradation (redundant code, dropped imports,
vibes-not-evidence); feed each increment's mistake-patterns into the next brief as do-nots.
Savings: `honey-eco` (committed EcoLogits port — never hand-estimate); `honey-compress` for
re-read memory files. To-dos come FROM the Ouroboros seed; status lines are outcome-first
(`Verified live:` / `DONE:` / `NOT built.`), never narratives.

## SUCCESSION — no-Fable operation

**On Codex/Hermes this section IS the operating mode, not a contingency.** These harnesses run
one model and have no tier to escalate to, so read every "tier" below as "an independent
reviewer in a separate context" — which, here, means the sandbox lane. Rule 1 is the one that
binds hardest: a single-model harness has no internal way to satisfy "independent", so
independence is obtained by handing the work back, never by re-reading your own diff.

(The standing goal: the tier below must not need the tier above.) Every protocol here is
model-agnostic BY CONSTRUCTION — quality tracks the brief and the gates, not the coordinator's
tier. When Opus coordinates:
1. **Never self-accept.** The coordinator's own spine/design work gets an INDEPENDENT
   same-or-higher-tier adversarial review (loaded brief: files:lines, suspicions, demanded
   runnable evidence) before commit — the role split substitutes for the judgment gap.
   **BUILDERS never self-accept a deviation from a stated brief constraint either
   (2026-08-28: a builder genericized pinned telemetry text against a byte-preservation
   constraint and "accepted" it in its own self-attack — 4 existing-suite reds shipped).
   A deviation from any byte-preservation / exact-contract clause is STOP-and-report, and
   a touched file's EXISTING suites always belong in the builder's final gate.**
2. **Replace judgment with STRUCTURE.** Anything the top tier would have eyeballed becomes
   2-of-3 diverse-lens verification (correctness/security/repro) + deterministic gates; when
   reviewer intelligence drops, RAISE gate teeth (negative controls, mutation audits,
   identity assertions) — never lower the bar to match the reviewer.
3. **Tables decide, not intuition.** The Phase-2 measured-value-table discipline is the
   design-call substitute: read the decision off the table; ambiguous table → escalate to the
   human as a PATH-2 text question rather than deciding.
4. **Briefs are the interface.** Pre-flight every brief against the orchestrator checklist
   (verified seams, prior mistake-patterns as do-nots, evidence demands, foreground long
   gates); an under-briefed strong model loses to a well-briefed cheap one. Every delegate
   brief carries the standing do-not: NEVER take outward-facing actions (open/close PRs,
   post comments, publish) — a delegate once opened a clean-build→main PR to deliver a
   one-line docs edit, minting a 256k-line phantom diff whose failing fork-CI checks
   mailed the owner on every subsequent push for a day (closed 2026-07-22, PR #1).
5. **Keep compounding.** The retrospective rule runs identically — bake lessons in the same
   increment; the protocol is the institution, the coordinator is replaceable.

## Repair briefs: the unit of work is the SET, and evidence rules for repair claims

(2026-09-01, the I3→I3b→I3c triple round.) A repair brief that names defect SITES gets back
narrowly-fixed sites: I3b fixed every named line and missed the second _compute_G call site,
five e2_eval routing sites, the batch-side guard twin, the sibling LUT builder — and its own
new conjunct shipped with zero production callers (AP-54 reintroduced INSIDE the AP-54 fix).
Rules, all mandatory in any repair/threading brief:
1. **The unit of work is the complete caller/sibling set, never the named instance.** For
   every threaded parameter: the brief demands the COMPLETE production caller enumeration
   (grep AND graft, both outputs IN the report) with every member threaded or its default
   justified. For every guard/branch fix: the sibling sweep (elementwise↔batch, M1↔M2↔M4,
   duplicate LUT/validator copies) is a listed deliverable per fix.
2. **A skipped gate is a NOT-done, never an argument.** "Structurally covered" /
   "the kwargs all default False" is not a differential run and not a mutation rerun — the
   I3b/I3c builders each deferred the mutation harness and the OFF differential on structural
   arguments; round-2 lanes proved three "fixed" blockers had no test that reds on revert.
   The coordinator (or the verify lane) RUNS the skipped gate before any push.
3. **Attribution is evidence, not narrative.** "Test X went green because of fix Y" requires
   the red-green pair (revert Y alone → red; revert the test's own fixture change alone →
   what happens). The I3b ledger credited a threading fix that was never written; the green
   came from a fixture repair (proven by the V2 A2a/A2b pair).
4. **Durable prose cites SYMBOLS, not line numbers, and counts only from commands run this
   session.** Line cites drifted 4-12 lines in three consecutive ledger entries; the
   pre-existing-red count was wrong three times (2→5→6) until measured directly.

## Delegate refusals are hypotheses too

**A delegate's "infeasible/heavyweight" claim about test infrastructure is a brief-hypothesis
to verify against the tree, not a scope ruling to accept** — check the NEIGHBORING test files
for an existing fixture pattern before granting the exemption, and if the pattern exists,
either send it back with the file:line or close the gap yourself (a builder declined the same
search-space gate three times as "requires a heavyweight integration fixture"; the complete
lightweight pattern — a ~15-line ctx stub driving the real featurize→build_problem chain —
sat in the adjacent test_stages_slippage_wiring.py the whole time, and the finished gate was
~40 lines that killed both mutants the suite had been blind to). Corollary: a repeated refusal
on the SAME item across rounds is a signal to stop delegating THAT item — the marginal round
costs more than doing it in the main loop.

## Parallel agents, liveness, coordinator economy

- **Parallel agents for breadth, yourself for depth — and CAP the solo probe loop.** Fan out for
  reading/searching/auditing; design decisions, root-cause calls, final verification stay in the
  main loop. After ~3 FALSIFIED hypotheses on one defect, stop probing and delegate an
  instrumented-forensics agent carrying the full evidence ledger (every probe, result, and killed
  hypothesis) — the ledger is what makes the handoff cheap and the next probe non-redundant (an
  xterm render-loss defect ate 7 main-loop probes before the handoff that should have come at 3).
  Never probe files an agent is concurrently mutating (check `git status` before trusting any
  probe during a mutation audit). **A NUDGED agent is LIVE until proven dead:** a queued wake
  message can resurrect a presumed-dead delegate mid-recovery — after any nudge, re-verify
  liveness (transcript mtime) before running its tests or touching its files (a resurrected B9.2
  builder edited its test file mid-orchestrator-run, minting a phantom "flaky" bitwise failure
  that cost two 7-minute reruns to un-diagnose). **Corollary — NEVER `git commit`/`--amend` the
  shared tree while a delegate may be mid-mutation** (e.g. an adversarial mutation-audit verifier):
  a clean `git status` is a point-in-time SNAPSHOT, not a liveness proof, and the delegate can
  re-inject a mutant the next second — committing then captures the mutant. A git-state stop-hook
  that pressures a commit/amend during a live audit is answered by DEFERRING to the delegate's
  completion notification, not by the clean-status snapshot. **The hold widens when a delegate
  runs `git stash`-based base-attribution (observed I3 2026-09-01): stash/pop round-trips the
  WHOLE working tree, so any coordinator edit of a TRACKED file while the lane is live can be
  swept into its test states or conflict its pop — during a live build/verify lane the
  coordinator writes only NEW untracked files; tracked-file edits (ledger, wiki, skills) queue
  for the lane boundary.** (this stop-hook fired 3× during the
  DX6b/DX7 verifies; deferring each time was correct).
- **Coordinator token economy: the main loop AUTHORS and VERDICTS; it does not EXECUTE.** "Final
  verification stays in the main loop" means reading evidence and issuing the verdict — not
  personally driving every probe/deploy. Mechanical execution (browser-probe plans, VM
  deploy/relaunch sequences, screenshot fetching, gate re-runs) goes to a cheap delegate carrying
  the exact plan + expected outcomes; the coordinator reads the returned steps.jsonl/log lines and
  spot-checks ONE artifact. Coordinator-priced work is only: designs, briefs, dry-run plan
  reviews, security/spine hunk reads, and the kill-switch question on every green.

## The ORCHESTRATOR protocol (proven over a full MVP sprint)

Delegate the bulk to well-briefed agents, keep review + the hardest seams yourself.

(a) **Disjoint file boundaries per parallel agent** — conflict-free by construction; commit one
boundary while another runs. **(a2) Workflow worktree isolation creates worktrees from
origin/main, NOT the checked-out branch (bit 2026-07-24: 608 commits stale, every briefed seam
absent) — every worktree brief pins the tip SHA and mandates `git reset --hard <tip>` +
verification as the delegate's FIRST action.** **(a3) Any editable or vendored dependency
tree that a copy must reference at the ORIGINAL path (symlink, not duplicate) needs
`rm -rf <copy>/<dep> && ln -s <repo>/<dep> <copy>/<dep>` in every tree-copy builder
(worktree, `git archive`, mutation harness). Without it: a gate on the copy reds for a
reason unrelated to the code, and a mutation harness KILLS every mutant narrowed to such a
file whatever the mutation did (V7-F1, 2026-09-02, hollow kills in the source repo). `ln -s`
alone onto a worktree lands the link INSIDE the tracked dir (phantom reds); the `rm -rf` is
load-bearing. When the repo has multiple archive builders, a fix to one is silent until it
reaches the others.**

(b) **The brief carries seams YOU verified + prior mistake-patterns as do-nots** (delegates
repeat mistakes you don't name); **any brief creating a NEW numeric module on market data
carries anti-hollow-green tactic-1 EXPLICITLY (isfinite + positivity on the whole unusable
class) — the I1 lane shipped a NaN fail-open in the exposure-increasing direction because the
brief assumed the tactic transfers implicitly (2026-09-01, F10/F11);** **research/findings briefs must NOT demand the delegate Write
the report file — the harness blocks subagent writes of `.md` report files ("Subagents should
return findings as text"); brief them to RETURN the full body as final text, and the
coordinator persists it (2026-08-27: an obj-battery research lane hit the block, correctly
refused to route around it, and returned the body — the brief cost nothing but the retry was
luck); **a long brief travels as a FILE, not an inline prompt** —
scratchpad file + a short pointer prompt that Reads it first and STOPS loud if missing (an inline
audit brief once arrived truncated to 79 chars and burned the dispatch; the file pattern makes
re-truncation impossible and a lost file a cheap loud retry).

(c) **Review = re-run the gates yourself + read only security/spine-critical hunks** — where
every real delegate defect was caught (dead-wire tier check, jail escape, fabricated-green risk);
never accept "all green" without your own gate run. **Re-run on the builder's OWN full set, not
a coordinator-chosen subset, and require the LITERAL pytest invocation in the report AND commit
message** — 2026-08-26: a builder claimed "184 x2" while its tree had 4 reproducible failures;
the coordinator's 76-test subset was green because it skipped the broken file, and three
different true counts (155/158/168) circulated unverifiably until the invocation was pinned.
**A harvested diff that ADDS a mutant must also add its killer file to the lane's GATE SET in
the same harvest commit (2026-09-02):** the I4b delegate registered M_I4B_sever_relabel with a
new killer test file, the harvest cherry-picked both, and the gate set stayed blind — the next
lane's `--check-anchors --tests` pre-flight said SCOPE_FAIL, which is the instrument working
but one increment late. Harvest checklist line: `git diff` touching `scripts/mutants/*` ⇒ diff
the mutant's killer list against the gate file before committing.
**Semantic-duplicate lens (slopo, IP-1): when a slopo index is live (`slopo.conf.yaml` +
`.slopo-runtime/`), run `slopo review --base origin/claude/soundbox-kit-migration-iz1jwf` over
a landed build lane's diff — ADVISORY only, never a gate; attach flagged clusters to verify
briefs.**
**(c2) THE LANE EXIT GATE IS A SCRIPT, NOT A PARAGRAPH (owner mandate 2026-09-02, after
seven RP-30b verify rounds).** Every build/repair brief ends with: run
`scripts/lane_gate.sh <push-base> <gate-files.txt> [--mutants scripts/mutants/<lane>.py]
[--digest <script>]` as ONE detached invocation, poll `$OUT/DONE`, paste the VERDICT block
verbatim into the report AND the final commit body; VERDICT RED = the lane is not done,
whatever the prose says. Every verify brief runs the SAME script first and grades from its
artifacts (`reds_new.txt`, `mutants.txt`, `lint_delta.txt`) before any reading. Verifier
findings that need a repair ship as RED TESTS (committed failing tests or manifest mutants),
never file:line prose — the repair brief is "make these N tests green, do not edit them".
A finding with no test is INFO and does not open a round. "Pre-existing" is a word only
`lane_gate.sh` may say (its `reds pre-existing=` line, computed against the PUSH BASE
archive) — the I3g report called a range regression pre-existing off a mid-stack SHA, and
the mis-label cost a full round. Round cap: `contract-gate` §4 — round-3 NOT-READY stops the
wave for a main-loop churn root-cause; there is no round-4 brief.

**(c3) A GATE OF RECORD FREEZES THE WHOLE TREE — wiki, skills, docs, ledger included
(2026-09-02).** `lane_gate.sh` re-checks HEAD and `git status --porcelain` at the END of its
run and REDs on "HEAD moved" / "tree dirtied during the gate", with no file-type carve-out —
a wiki live-state edit or a ledger stamp during the ~90-min run wastes the whole run exactly
like a code edit would. The coordinator nearly did this twice in one window (a live-state
delta mid-run; then the GitNexus banner rewriter regrew AGENTS.md/CLAUDE.md after a
compaction setup pass). Rules: (1) park every non-code delta as a patch in the scratchpad
(`git diff > $S/<name>_pending.patch`, `git checkout -- <file>`) and apply it AFTER the
VERDICT block is read; (2) every keep-alive tick during a gate runs `git status --porcelain
--untracked-files=no` and reverts banner churn (`git checkout -- AGENTS.md CLAUDE.md`) — the
running pytest lives in a separate worktree, so the revert is safe; (3) commits, task-DB
metadata and wiki updates queue behind the verdict — the ONLY things that move during a gate
are scratchpad files and the in-session task DB.

(d) **Background-agent liveness = transcript-file mtime probe** (never read the transcript —
context overflow). **Staleness is only a death signal when it EXCEEDS the brief's longest
foreground gate (2026-09-01: an I2 builder went mtime-silent for 14 min inside its own 8-min
test_problem.py run; the coordinator declared it dead, dispatched a duplicate lane onto the
SAME files, and the original then completed — the duplicate had to be TaskStop'd mid-collision
window).** Before re-dispatching over a stale lane: compare staleness against the longest gate
the brief mandates, and prefer waiting one more poll cycle for the completion notification —
a duplicate lane on shared files is strictly worse than a late one. **Brief delegates to run long gates (full pytest etc.) in ONE foreground call
— a delegate that backgrounds a run and stops is NEVER rewoken by its completion; it sits stalled
until the coordinator messages it (two executors parked this way in one sprint).** A stalled
agent's EXTERNAL artifacts persist — recover by inspecting what it left and finishing lean, not
re-running from scratch.

(e) **Commit at every boundary between agent handoffs** — a dirty tree across turn-ends burns
quota and blocks committing finished work.

(f) **A push publishes EVERY local boundary, reviewed or not: run `git log
origin/<branch>..HEAD` before ANY push** and review each unreviewed delegate commit first (a
routine push once shipped two unreviewed spine commits that happened to be sound — the check is
one command, the alternative is luck). **While any delegate is LIVE, log-then-push-HEAD is itself
a TOCTOU race — the delegate can commit in the gap between your log and your push (bit
2026-07-21: an Inc4 spine commit landed mid-push and went out unreviewed). Push the REVIEWED SHA
explicitly (`git push origin <sha>:<branch>`), never HEAD.** **The push is also its
own CALL, sequenced after you have READ every gate/probe result it depends
on — a push chained in the same call as a mutation probe fires regardless
of the probe's outcome (bit 2026-08-18: a probe SURVIVED — vacuous test —
and the pre-chained push shipped the unverified guard anyway; sound code
by luck, not by process).** **The full SHA comes from `git rev-parse
<short>`, never typed from memory — a hand-extended short SHA is a
plausible-looking invalid ref whose push failure mimics a non-fast-forward
race and triggers a needless continuity alarm (bit 2026-08-24).**
**Delegate commit MESSAGES are part of the review surface: the harness
auto-appends a model-identifier trailer that this session's rules ban from
pushed artifacts — but NEVER `git commit --amend` while ANY delegate is
live. A HEAD-identity guard is the WRONG predicate: the INDEX is shared,
and amend commits the whole index — on 2026-08-25 a guarded amend swept a
live delegate's 6 staged files into the AP-33 commit and the push shipped
them unreviewed under a message enumerating 4 files (seventh costume of
the ship-unreviewed class). Trailer/message cleanup waits until ZERO
delegates are live; and EVERY coordinator commit in a shared tree is
preceded by `git diff --cached --stat`, read as its own call, confirming
the staged set is exactly the intended files.**
**Cite only ON-ORIGIN SHAs in durable prose (wiki, registry, docs):
push_clean's filter-branch rewrites every unpushed commit, so a local SHA
written into an artifact BEFORE the push becomes an orphan the moment the
push lands (bit twice on 2026-08-28 in one night — the second time in the
very commit that fixed the first). Write the prose, push, then cite —
or cite the already-pushed base and name the commit by SUBJECT until it
has an origin identity.**

(g) **When two parallel increments share a vocabulary (names/keys/slugs one produces and the
other consumes), the merge reconciles to ONE map keyed by the producer's COMMITTED constant and
LOCKS it with a structural equality test against that constant** (set(consumer keys) ==
set(producer names)) — an eyeballed alignment drifts on the next edit; the lock test makes drift
a red, not a review item (B8 merge: metric_roles keyed by the adapter's
CANONICAL_EXTRACTION_MAP, locked by test). **Corollary — CHANGING a canonical vocabulary
(renaming/swapping an objective, metric key, slug) must ship WITH a repo-wide old-name consumer
sweep (grep + full-tree run) in the SAME increment:** registering the new name on its N official
surfaces misses every consumer that INDEXES the old one (the Wave-0
trade_count→position_coverage swap left four silently broken for days — a frozen selector struct
that couldn't import, a tilt map that KeyError'd every artifact, an evaluator whose F-vector went
NaN on the productive path, and a stale test — all invisible to the swap's own per-suite gates,
caught only by full-tree + adversarial verify). **Second corollary — an emitted metric's MEANING is vocabulary too:** changing what a
telemetry field measures (even in a "pure instrumentation repair") must sweep every prereg/
runbook/doc that READS that field by name in the same increment — the W4 bucket repair
redefined signal_gen_s while a pre-registered benchmark said "read signal_gen_s", minting a
~200x phantom speedup that only the adversarial verify caught (2026-08-26, W4 F1).

- **Owner-run launch blocks are delegate briefs for a human** (2026-08-25 launch saga, AP-35): setsid + redirect + background + inline self-verification over EVERY matching PID; never hand a foreground command whose death-by-terminal-close is silent; check for stale babysitters before the launch, not after the third failure. Two hard extensions (2026-08-26, K4 launches 5-6): (a) never multi-line blocks — owner paste splits them; bake the whole launch into a PC-side script, hand ONE word; (b) every env var name in the block is read from its CONSUMER in the code before launch, and post-launch validity = CONSUMPTION evidence (run_config snapshot + the path-discriminating gen-0 telemetry event) — /proc presence of names you yourself wrote is a mirror, not a gate; a launch that runs much faster than its predecessors is running a smaller wrong problem until proven otherwise.

- **Thermo-nuclear full-stack gate on every multi-commit push (owner mandate 2026-08-26).**
  (c)-review is per-increment; the PUSH of a stack (>1 code commit beyond origin) additionally
  requires a `thermo-nuclear-review` pass over the whole `origin..HEAD` diff on the verify lane
  — dispatched in PARALLEL with the final finding-driven verify, both verdicts gating the push.
  It also carries a bug-echo leg: for each defect class fixed IN the stack, the diff itself is
  swept for reintroductions. Same standing status as /bug-echo — part of the validation chain,
  never a side pass.
  **Infra-kill fallback (2026-08-27, two container restarts killed the verify lane twice in
  ~30 min):** when repeated infrastructure kills prevent the pre-push thermo from completing
  while a coordinator-reviewed stack sits unpushed, the rollback-loss risk of the local stack
  outweighs the sequencing rule — push after the coordinator's OWN full review + clean re-gate
  (every failure attributed pre-existing at the base SHA), re-dispatch the thermo POST-push,
  and treat its findings as immediate follow-up fixes. Record the deviation in the wiki the
  same turn; this is a fallback for infra failure only, never a shortcut when the lane can run.

## Checkpoint discipline for delegate lanes (baked 2026-08-31, after TWO restart-kills)
The sandbox container restarts without warning and kills running lanes; uncommitted delegate
work died twice in 24h (the original perf build, then its repair lane mid-edit). EVERY
delegate brief now carries: (a) builders COMMIT each increment the moment its gate is green
— never batch commits to the end; (b) evidence/report lanes WRITE THEIR REPORT FILE
INCREMENTALLY (append per section), never hold a finished report in memory; (c) the
coordinator, on any lane-death notice, salvages `git diff` + stash BEFORE any cleanup, and
re-dispatches from the brief — never resumes from the untrusted partial (recovery restores
bytes, not trust). Corollary for the coordinator itself: push verified work at every
delegates-dead window (split the stack if part of it is unmerged/NOT-READY — cherry-pick the
safe commits to trunk rather than holding everything hostage to the broken one).

**PC-LANE PLACEMENT (2026-09-03, agent-factory Hermes bring-up — eight runs).** When a lane runs
under a foreign harness on another host, prove three things from the LANE'S OWN OUTPUT before any
real brief rides it: `pwd` equals the pinned worktree (a `gitdir:` file, HEAD = PIN), the hard
limits refuse (`git push`, `gh pr` → blocked, exit code quoted), and the deliverable path returns
(report AND patch fetched). A 60-second read-only diagnostic brief answers all three; five build
runs did not. Flags that move the process (`cd`, `--in`) do not move the tool — find the tool's
own cwd carrier (Hermes: `TERMINAL_CWD`). Never wire a coordinator turn-end hook into a one-shot
lane: it consumes the final report. A known-broken optional MCP server must be disabled for lanes
— a crash loop at startup costs minutes per run and zero model calls. Two more before the first real brief (2026-09-03, round 2 died on a 503): measure the lane
profile's prompt (`hermes prompt-size`) and curate the skills it indexes — a build lane does not
need the domain library on every call — and install a `fallback_providers` chain so one busy route
fails over instead of killing the lane after three retries.
