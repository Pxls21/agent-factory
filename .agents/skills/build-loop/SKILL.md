---
name: build-loop
description: The meticulous build loop ("Fable light") — MANDATORY for every code increment, in any project. Full text with war-story evidence. Load before writing any code increment, test, or commit; when verifying seams; when debugging an unexpected test failure; when running a live smoke; or when closing an increment. the project instructions file carries the condensed operative steps — this skill is the authoritative expansion.
---

> **HARNESS PORT.** This copy is read by Codex CLI (`.agents/skills/`) and by Hermes
> (via `skills.external_dirs`). It is the same protocol as `.claude/skills/build-loop/SKILL.md`;
> only lines naming a Claude-Code-specific mechanism were reworded — see `docs/HARNESS-PORTS.md`.
> "the project instructions file" = `AGENTS.md` on Codex, `.hermes.md` on Hermes.
> Model-tier names below ("Fable light", "Opus 5 lane") are PROTOCOL LABELS, not routing
> instructions: these harnesses run ONE model. Where the protocol calls for an independent
> verifier, hand the work BACK to the sandbox lane — never self-accept.

# The meticulous build loop ("Fable light" — mandatory for every code increment)

Model-agnostic, per increment, no skipping steps. This is the verbatim protocol; the project instructions file's
build-loop section is the condensed index of it. On any doubt, THIS text governs.

> **Golden-fence rule for byte-constrained refactors (2026-08-28, refactor waves G+A):** when an
> extraction/dedup must be byte-output-identical (identity hashes, persisted hash chains, feature
> bytes, parity contracts), the golden fixtures — serialized bytes, digests, chain tips, captured
> from the PRE-change tree — are COMMITTED FIRST as their own increment, before any extraction
> commit. The commit ordering itself then proves the oracle predates the change (no "captured the
> post-change output and called it golden" hollow). Mutants on every format axis (ordering,
> separators, algorithm, domain separator) must fail the fence before the refactor commits ride it.

> **Seam rule extension (2026-08-25, launcher near-miss):** seam verification applies to the
> FIX's own dependencies too — every variable your fix references must be proven DEFINED on the
> EXECUTING path (not just somewhere in the file: a branch-scoped definition + `set -u` turns an
> unbound reference into a launch-killer). Prove with the cheapest whole-artifact gate
> (`bash -n` + a DRY_RUN invocation), never by reading alone.

1. **Verify every seam BEFORE writing code that calls it — and for any seam AROUND a vendored library, run the `vendor-first` pass FIRST** (grep the vendored tree + introspect the live object for an existing mechanism before designing a new one; AP-28, the in_outputs incident 2026-08-22). Read the actual
   signature/regex/contract in the repo — never code from memory or a doc (memory-written code has
   been silently dead; the real contract differed). Doc vs code disagree → code wins, doc gets
   fixed. **MEASURING THE INPUTS IS NOT VERIFYING THE CONTRACT THAT CONSUMES THEM, and a test
   written from the same assumption as the code is a MIRROR, not a gate** (2026-07-25: I measured
   the das-dennis reference-direction counts live and correctly resized the M=5 lattice, then
   ASSUMED the engine wanted `H <= pop_size`; it enforces `H == pop_size` exactly
   (`engine.py:770`), so the deploy ran ZERO generations — and my own lock test asserted the same
   `<=`, so it passed while production failed. When a change pairs two numbers, assert the
   RELATION the consumer enforces, read FROM the consumer). **A CONFIG/DEPLOY VALUE is an
   increment too — stage no env/config value without pushing it through every validating
   chokepoint on its consuming chain, OFFLINE, first** (2026-08-27: a staged GA_SYMBOLS
   universe was rejected at launch by the hash-pinned compliance allowlist —
   `validate_universe_proposal` was importable and would have refused in seconds; the miss
   burned an owner kill+relaunch cycle. Corollary: a consumption proof needs a value that
   DIFFERS from the default — env==default "verified" nothing). **A bulk mechanical edit (re.sub
   sweep, scripted insert) gets verified at the SEMANTIC level, not the import level: "module
   imports clean" is a vacuous gate for binding bugs — prove the touched NAME resolves
   (`getattr(mod, name)`) and the insertion landed as code, not inside a string/docstring**
   (2026-08-26 AP-36 wave 2: a scripted insert glued runner.py's module import into its
   docstring; the module imported clean while every call site was a dormant NameError).
   **When enriching a build (new
   rung/language/channel/check), guard against dead-on-arrival artifacts at GENERATION time: emit
   only shapes that can actually fire** (e.g. scope emission to the parent shape) — an
   emitted-but-unreachable check is a silent hollow green.
   **A durable record that guards an IRREVERSIBLE side effect (an on-chain send, a file write, a
   remote submit) must be written BEFORE the side effect, keyed by an identifier known PRE-action —
   verify from primary source that the id IS available pre-action, never assume it is "only known
   after" the call returns. Record-after-the-fact leaves exactly the crash window the record exists
   to close (DX10-D: both DEX adapters recorded the pending_tx row AFTER `send_transaction` on the
   false premise that the tx hash was only known post-send; the sign-time signature/`signed.hash` was
   in fact known pre-broadcast — a crash between send and record → no durable row → restart double-swap;
   the adversarial verify caught it). The residual (crash between record and send) must fail the SAFE
   way — an unresolvable record → fail-loud HALT, never a silent re-do.**
   **Verify the PRODUCER before reasoning about the consumer's evidence — "the design doc says
   component X feeds this" is not "the tree RUNS X."** (2026-07-31: a whole architecture research
   round reasoned about a regime layer's causality guarantees against the HMM provider its design
   doc named; the live producer was a different class entirely — VolatilityBucket — so the
   causality certificate was falsified as written and every downstream argument inherited the
   skew. One grep of the live call site would have caught it at design time.)
2. **One increment = code + deterministic test + commit.** Test is LLM-free, in-sandbox, with a
   NEGATIVE control failing for the exact expected reason (e.g. a synthetic mutant workflow whose
   gate runs RED and provably never touches the cwd). **A capability-gated proof is tested under
   BOTH a capable and an incapable environment (AF-AP-24, S0-11): every leg that reads the gated
   capability is guarded by the SAME preflight the real check consumes (not a proxy signal, not a
   selected subset), and a test proves the incapable path DEFERS (a distinct "unavailable" exit,
   never a false pass or false breach) — a guard on only some legs is the owner's "2 failed" on the
   host that lacks the capability. Exercise the CANONICAL CONSUMER, in both venue states, not a
   proxy (AF-AP-24 recurrence-3, S0-11 cycle-5): a test that invokes the checker legs directly
   proves nothing about the runner production actually calls — the runner had NO defer branch and
   destroyed the artifact on the incapable venue while the "canonical" test that bypassed it stayed
   green. Drive the real runner/CLI; where a capable box can simulate the incapable venue (drop to
   a non-privileged uid via `setpriv`), run the SAME test both ways so the defer path is covered
   wherever the suite runs. A deferring/failing run must PRESERVE the capable-venue artifact, never
   delete-then-fail.** **A fixture that cannot carry the PRODUCTION
   data TYPE is a vacuous test — build round-trip/serialization tests from the real producer's
   types, not hand-built native-Python stand-ins** (PREMORTEM-2 R2-01: a champion test used a
   native-`bool` `make_genome_dict` fixture; the real pymoo MixedVariable population carries
   `numpy.bool_`, which `json.dump(default=str)` corrupted to the string `"True"` — decode failed
   on EVERY real champion while the test stayed green). **A parity/equivalence gate must also
   assert the ORACLE ACTED** — two arms that both do nothing are bitwise-equal (a size/price=NaN
   fixture made VBT skip every order; six "bitwise parity" tests passed over zero fills while
   hiding a real reject-everything kernel bug). Assert position moved / records exist / the core
   branch fired, in the SAME test that compares outputs. **And a parity gate over a
   DISCRETE/threshold-derived metric (trade_count, fill count, any threshold-crossing tally) must
   assert the discrete value EXACTLY and exercise the branch that GENERATES it** — a 1e-9
   tolerance on upstream continuous equity certifies nothing about an integer decided by threshold
   crossings, and a fixture set that never fires the generating branch (stops) leaves that metric
   ungated (#319: the GPU parity gate passed at 1e-9 on no-stop fixtures while the kernel diverged
   by whole trades at a 9-vs-10 floor boundary, flipping a full day's feasibility verdicts).
   **De-vacuous the control at WRITE time:** if the "failing" fixture passes through an unintended
   independent code path it proves nothing — rebuild it so the guard-under-test is the ONLY reason
   it fails. Prove STATE, not returned flags — assert the file/store/tree changed — **and prove
   IDENTITY, not just success**: on any path that selects/serves/recalls an entity, assert it is
   the exact entity claimed (id/intent/content-hash), never merely that *something* came back —
   **and verify the identity KEY actually COVERS the attribute whose change you claim to detect: a
   change-detector keyed on a hash that omits the changing field is structurally blind (FIND-20:
   champion rotation compared `compliance_hash`, which carries no genes/mode, so successive GA
   runs under one compliance config could NEVER rotate — dead since ship, surfaced only by a new
   test's positive control)** (a tier-only assertion passed while the WRONG entity served; a
   surviving SSE badge is not a surviving transcript — status persistence is not state
   persistence). **A fail-loud path tested ONLY through a FAKE emitter/sink is a hollow control** —
   the fake swallows anything, bypassing the REAL sink's own validation (stage/schema
   registration), so production CRASHES where the test "degraded". Drive at least ONE negative
   control through the REAL emitter (DX9 threaded a real EventEmitter and instantly hit a
   `dex_inventory` telemetry stage unregistered in the events schema — every DX7/DX7-full test
   used a SpyEmitter, so the risk-gate inventory read would have raised ValueError, i.e. CRASHED,
   instead of failing closed the first time a held token was unpriceable). **The commit message IS
   the reasoning record:** name the rejected alternative, the exact level/ordering rationale, and
   the primary source consulted (e.g. "behavioral-build outranks grep because it exercises a real
   compile; source: the installed language-pack"). Several legitimate changes in one file →
   enumerate disjoint hunks ("TWO logical changes: 1… 2…"); a load-bearing ordering decision also
   gets a comment at the decision SITE. Keep commits surgical and cherry-pickable. Commit BEFORE
   any destructive probe or mutation audit touches the same files. **Deterministic-fixture tests
   (seeded RNG, captured trace, golden output): run twice, assert bitwise-identical, before
   trusting baselines.** **Forced to commit mid-increment:** embed recovery state in the message —
   (a) the acceptance bar + where the result stands, (b) WHY it falls short, (c) the concrete plan
   — "needs redesign" alone forces a full re-analysis on the successor. **Never chain a scripted
   file mutation (python heredoc replace, sed) with `git commit` in one call: a partial mutation
   failure does not stop the commit, which then ships the half-state (bit 3x on 2026-08-24 —
   quote-mismatch asserts fired, commits landed anyway). Mutate, VERIFY the mutation's own
   output, then commit as a separate call — or use exact-match Edit, which fails loud.**
3. **An unexpected test failure indicts YOUR assumption first — debugging ladder: telemetry →
   isolation → code.** Read the trace FIRST (a 10-line stage_event spy) — a well-instrumented
   failure NAMES the branch (`abstain_divergent_top` pointed straight at the P5.1 guard). Then
   layered isolation probes: rebuild with the smallest REAL-component pipeline, binary-search layer
   by layer, never a mock. **Reproduce before believing any RECORDED diagnosis** — a handoff's
   root cause is a symptom report, not a mechanism; re-derive live (a past handoff named the wrong
   layer; a compaction summary claimed seed-spec content the seed didn't contain — post-compaction,
   re-open the breakdown/seed before building from the summary). Then probe the actual runtime
   value (5-line REPL), fix the root cause, not the assertion. **A piped gate run's exit code is
   the LAST pipe stage's, not the tool's** — read `${PIPESTATUS[0]}` (a `pytest | tail` "green"
   was tail's rc=0 over a pytest usage error).
4. **The live run is the real proof — live failures are FINDINGS, never noise.** After
   deterministic green, run the real thing (VM/Hermes/live smoke): paired positive + negative
   control, exact outcomes asserted (oracle rc==0, file present / model blocked, no file) — **and
   assert the probe's INSTRUMENT actually produced the condition under test** (a mode-marker flip,
   not just surviving content: an emulated-browser resize never crossed the CSS breakpoint, so the
   first rotation "survival" proved nothing). **No telemetry records whether the instrument
   fired? Find a structural SIGNATURE in the output that only one mode can produce** (#380: the
   launcher doesn't pin GA_SHARPE_KOFN and no event emits the resolved K, but K-of-N violations
   are integers `K − folds_cleared` while every-fold violations are continuous — the value
   histogram {1,2}/{3,4} vs 1.1801 proved the knob was live; emit the missing field anyway). A live
   break on an undocumented contract → **resolve from primary source** (read the installed
   package: docs said dict, the package returned an object needing attribute access). Never paper
   over a live failure with a retry or shape guess. **Prove the fix at the OUTERMOST boundary
   where the failure was observed** — re-run the exact entry point that failed (server E2E, full
   solve()), not a narrower harness (a bug "fixed" twice at an inner layer was still broken at the
   outer entry point).
5. **Close the loop in writing — and ECHO before closing (owner mandate, ratified into the
   light loop 2026-08-22).** Any real defect this increment FOUND or FIXED gets `/bug-echo`
   run on its anti-pattern and the class registered in the ANTI-PATTERN REGISTRY atop
   `docs/INCIDENT-LOG.md` BEFORE the increment closes — part of the validation contract for
   EVERY increment, not just deep-mode. Evidence: the 2026-08-21 mega-sweep found unexploded
   siblings in ~half of previously-fixed bug classes; the 08-22 CUDA parity defects each
   spawned a sibling sweep that is now the standing pattern. Update runbook/status docs the moment the live proof lands (a
   doc still saying "blocked" after the fix is a defect); sync TODO with task list; push; stop and
   report. **Status lines open with the OUTCOME, tagged by verification level:** `Verified live:`
   (real path) ≠ `DONE:` (tests green) ≠ `NOT built.` (absent/dormant, stated first-class). The
   verdict leads; the story follows. **`REVIEW-PENDING` is its own level, below `DONE` (AF-AP-32,
   S0-11 cycle-5): work the owner is actively reviewing is not closed until the OWNER accepts —
   the coordinator never self-records "closed"/"re-closed" for it, in the ledger or the task DB.**
   The verification level in the chat handoff and the tracked status must agree; a ledger that
   claims closure while the handoff says review-pending is a hollow green in the tracker. **Mechanize
   it as a STATE guard, not a vocabulary ban (S0-11 cycle-6, AF-AP-32):** a guard that rejects only
   the word "re-closed" still passes a "DONE by coordinator" row. Parse a single canonical status
   marker per item, require REVIEW-PENDING, and fail on DONE/CLOSED/a deleted marker/conflicting
   duplicates — with negative tests for each. A regex vocabulary check is not a semantic state
   guard (the same regex-vs-parser class as a security scan that greps where it must parse).
   **Cycle-7 sharpening (S0-11 seventh review — three more AF-AP-32 instances):**
   (a) **ONE VISIBLE authoritative source.** A HIDDEN marker (an HTML comment) can diverge from the
   visible ledger a human reads — a visible "DONE" row alongside a hidden "REVIEW-PENDING" marker
   passed. The authoritative status is a single VISIBLE line; reject hidden markers and any visible
   row (e.g. a table row keyed by the bare item id) that asserts a competing status.
   (b) **THE COORDINATOR NEVER BUILDS AN ACCEPTANCE GATE IT CAN SATISFY.** Any acceptance file the
   coordinator can write, it can forge — an arbitrary `OWNER-ACCEPTED` file "created by
   implementation agent" self-accepted. File existence is not authentication. The coordinator may
   record ONLY the pending state; genuine acceptance is an OWNER action on owner-controlled
   infrastructure it structurally cannot forge (a merge to a protected branch, a protected review,
   a signature against the owner's key). If you cannot build an unforgeable acceptance path
   (no crypto tooling, no owner anchor), SURFACE it as an owner decision — do not fabricate a
   fourth forgeable mechanism (#1 rule).
   (c) **Store review metadata OUTSIDE any attested/hashed input tree** — an acceptance file placed
   in the attested proof dir made the acceptance procedure itself break integrity.
   (d) **Test a state TRANSITION through EVERY adjacent gate, not just its focused test.** The
   cycle-6 ACCEPTED test never ran ledger integrity afterward, which is exactly how the
   attestation break slipped through; the transition test must run all gates the transition
   touches.

**Addendum — a DELTA gate meeting OLD code is a full-tree audit in disguise (2026-09-03,
agent-factory port).** Delta gates (pyflakes delta, the anti-pattern screen on ADDED lines) never
re-screen files that pre-date them, so a wholesale port or a vendoring drop is the one moment every
old line is NEW: the screen lit up 11 hits on adapters the source repo had run for weeks (five real
silent `except` sites, the rest fixture strings the tests exist to flag). Rule: budget the audit
into the port increment; resolve hits by CLASS, never by count — fail-loud the real ones, exclude
vendored trees from the gate the way the edit-snapshot screen already does, and take the hook's
own sanctioned bypass ONLY for by-design hits with each one named in the commit body. Never edit a
test to silence the screen.
