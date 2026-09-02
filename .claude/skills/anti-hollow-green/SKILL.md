---
name: anti-hollow-green
description: The anti-hollow-green tactics — general-purpose, any project: the full operational checklist behind the #1 NO STUBS rule, with war-story evidence (NaN fail-open wormholes, os.environ config leaks, mutation-testing, oracle independence, searchable-parameter-domain attack surface). Load when designing or reviewing ANY gate, oracle, test suite, benchmark, guard on externally-sourced values, or numeric fail-closed check; when a green looks too easy; or when bounding any optimizer/search parameter domain. CLAUDE.md carries the rule + one-line tactic index — this skill is the authoritative expansion.
---

# Anti-hollow-green TACTICS — operational checklist (every gate, oracle, test, increment)

The #1 rule (CLAUDE.md): NEVER replace a real component with a stub, fake, no-op, hardcoded
value, tautology, or shortcut to "get past" a blocker. A fake-substrate result is worse than
none. The hollow green lives in PROSE too. On a blocker: STOP → SURFACE → offer real options →
pivot to the nearest REAL provable thing → wait for direction. This skill is the full tactical
expansion.

1. **Test the UNHAPPY path.** Every gate needs a NEGATIVE CONTROL: PASS a compliant fixture AND
   FAIL a violating one — never ship a check with one leg. Assert the EXACT error/exit-code, not
   merely "it failed". Cover null/bad-input/timeout branches, not just the golden path. **A
   fail-closed NUMERIC guard on any externally-sourced value must reject the WHOLE unusable class —
   `not math.isfinite(x)` AND a positivity check on the FINAL scaled value — never a bare `x <= 0`.
   NaN is a fail-open WORMHOLE: `nan <= 0` is False (slips the guard) and every downstream `y > nan`
   is also False (slips the cap), so ONE NaN poisons an entire chain of guards; +inf slips `<= 0`
   too; and a raw-value guard misses a post-scaling degenerate (a positive answer under an absurd
   decimals/expo → 0 or ∞). This bit TWICE in one session — DX8a (unbounded expo/decimals → zero
   price) and DX7-full (NaN price → an oversized order cleared the notional cap, $1B vs a 2-token
   wallet) — both caught only by the adversarial pass, not the builder's own de-vacuating controls.**
   **The dual leg: a hard gate also needs a POSITIVE-POWER control — planted TRUE positives at the
   production geometry must certify at a measured rate BEFORE the gate is used as a veto. A gate
   whose power was never measured is an unfalsifiable no; its refusals carry no information about
   the candidates. (P1b 2026-08-02: the production-geometry cell certified 0/10 planted genuine
   Sharpe-3 edges while refusing 18/18 nulls — every prior refusal at that geometry was ambiguous
   between "overfit candidate" and "blind instrument".)**
2. **Execution guards — make cheating structurally impossible, not policy-forbidden.** (a) Isolate
   the env so the agent can't inject the expected result. (b) Timeouts on every subprocess — hollow
   code hides in loose loops. (c) Verify STATE, not returned flags — check the artifact actually
   changed. (d) A gain on one axis NEVER converts to trust on an orthogonal axis — combine
   quality×confidence with AND (a ceiling), never a sum. **(e) Process-global `os.environ` is NOT a
   config channel between co-resident components — an eval/gate path must resolve ambient config
   ONCE at construction and thread it EXPLICITLY, never read env at eval time. A co-resident
   component's RUNTIME env write silently reshapes any sibling that reads that env as a fallback,
   and it is INVISIBLE to a launch-env comparison — "env X was eliminated from the start-env" proves
   nothing about a runtime write, so attribution-by-elimination against a start-env ledger will
   finger the wrong suspect (#319: a paper daemon's startup `os.environ[flag]="1"` flipped the
   co-resident GA's blend features ON for a whole day's runs and mis-accused the GPU; fix = pure
   resolver + RunConfig-sourced flags threaded to `generate_signals`).**
3. **Mutation-testing IS the hollow-green detector.** Inject bugs into the code-under-gate; a gate
   that still passes is hollow. Demand BRANCH coverage. A gate surviving no mutants is a tautology
   — reject it. **3a. Mutants live in tmp/scratchpad COPIES — even inside COMMITTED test
   controls.** A subprocess mutation control must import a tmp copy (PYTHONPATH prepend /
   scratchpad cwd), never rewrite the real module with restore-in-finally: any crash inside the
   window leaves the mutant IN THE TREE (AP-34, 2026-08-25: a committed force-flag-ON control
   had a measured 64s window that would have armed a dark path tree-wide; a sibling run was
   SIGTERM'd mid-suite the same day). Prove the production file's hash is unchanged across the
   control's run. **3b. A mutant harness must PROVE the mutant actually loaded** — print/assert
   the imported module's `__file__` resolves into the mutant tree before trusting any verdict:
   `sys.path[0]` (the cwd) SHADOWS a PYTHONPATH prepend, so a mutant run from the repo root
   silently tests the REAL module and any "killed/survived" reading is vacuous (bit 2026-08-31:
   an F1-gate mutant "passed" 0.13s green — the real engine had loaded; caught only by the
   module-identity check, then re-run from inside a full mutant tree copy).
   **3c. Red-proof new regression tests against the PRE-FIX version from git history, no tree
   mutation:** `git show <old-sha>:path > scratchpad/old.py`, load via
   `importlib.util.spec_from_file_location` (print `__file__` — same identity rule as 3b), and
   reproduce the exact failure the new test pins (2026-09-01 repair round: three verifier
   findings proved red this way in one probe — no stash, no checkout, shared tree untouched).
4. **Ban hardcoded expected outputs.** The oracle is spec-authored, independent, un-importable by
   the thing it grades. **4a. DROP an inapplicable assertion, NEVER REWRITE it** (rewriting lets
   the graded artifact choose its own oracle value). Drop ONLY when: (a) change provably scoped,
   (b) ≥1 retained assertion is INVARIANT to the change, (c) the reduced gate still fails an
   empty/mutant workflow. Fail any leg → abstain, never mint.
   **4b. Pair every absolute pinned golden with a structural discriminator** (2026-09-02,
   dark-emissions digest): an absolute pin (sha of output bytes) fires on BOTH the defect it
   guards against AND every intentional upstream evolution — undecidable red, and "re-pin to
   green" quietly becomes the norm. Ship, next to the pin, a same-run structural test that
   isolates the guarded mechanism (e.g. output bytes with the suspect subsystem suppressed ==
   live bytes): pin red + discriminator green = evolution (re-pin WITH provenance: the probe
   result and the window of intentional movers); discriminator red = the real defect,
   root-cause. A pin without its discriminator makes every future red a judgment call.
5. **No LLM-judge in the gate spine.** Gate/oracle/assertion execution is deterministic
   exit-code / set-hash comparison; an LLM enters ONLY at codify/generate/tune time.
6. **A stress benchmark's value is the defects it FORCES, not the green it prints.** Design the
   matrix to hunt (adversarial cases, cross-family negatives, modified-requirement asks); a red
   first pass is the expected good outcome.
7. **The tell:** if a green was produced without the part it claims to need actually running (kill
   the model mid-graft and it still "succeeds"; disable the store and cost is unchanged), the
   capability does not exist — that is a falsification to REPORT, never a number to tune past.
8. **A GENE/PARAMETER DOMAIN is part of the attack surface:** any searchable value profitable
   ONLY inside one engine's fill/semantics model is a latent exploit the optimizer WILL find —
   bound domains with ECONOMIC-REALISM floors (fees+slippage-derived), lock them with tests, and
   treat single-engine robustness statistics (PBO inside the same engine) as structurally blind to
   cross-engine artifacts (x58 tsl 3e-05: the whole fitness summit was a vbt fill artifact; the
   paper layer caught it on day one).

9. **Verify input ownership at MINT time, not launch time.** A launch-time existence check on a
   shared append-only artifact is NOT a race guard: a concurrent writer (a test suite calling the
   real machinery through a CWD-derived path) can append between check and mint, and a verdict
   computed "from every row on disk" silently unions the foreign rows (2026-08-19 ORDERFLOW-LEAK:
   4 synthetic-predictive test rows flipped a dormant family to "admit"; the ledger guard had
   passed hours earlier). Before minting any verdict/summary, assert every input row was produced
   by THIS run (columns ⊆ scored set) and refuse loudly otherwise. Corollaries: artifact paths
   anchor to the repo root (file-anchored), never `Path.cwd()`; tests that exercise real
   writer machinery get autouse output-dir isolation; a PERFECT score (sign_fraction 1.0,
   quintile rho ≈1.0, t≈40) is a look-ahead tell — treat it as an indictment of the harness,
   never a win.

10. **Validate against the RESOLVER, not the namespace.** A membership check (`name in
   ALL_METRIC_NAMES`) guarding a consumer that must later RESOLVE that name (mint an F column,
   look up roles/direction/penalty) is fail-open: construction-green ≠ evaluation-green. The
   2026-08-27 instance: `total_return` passed `validate_objective_names` but had no
   `resolve_objective_sources` entry — armed, it raised PER GENOME inside run_ga's blanket
   except: ONE warning, `ga_result=None`, a full cycle with no champion (silent starvation), and
   the builder's 17 tests never evaluated a genome (the reachability hollow-green of tactic 7).
   Twelve sibling names shared the hole. The fix pattern: the validator calls the resolver
   itself (or a set derived FROM it) and rejects at construction; the mandatory test drives one
   swapped config through the REAL resolution+vector-build path. Greppable signature when
   auditing any gate: a name/id validated by set membership, consumed by a lookup table built
   from different rows.

11. **The motivating instance is a MANDATORY fixture.** A gate/screen/detector built because of
   a known measured incident must run that incident's REAL measured values through itself as a
   positive control (and the nearest legitimate shapes as negative controls) before it ships —
   synthetic fixtures alone let the threshold COMPOSITION drift away from the very case the
   gate exists for. 2026-08-28 instance (AP-46): the token-data staleness screen was designed
   FROM the PAXG case (kurt 847, 11.4% zero bars, measured and wiki-recorded), tested only on
   synthetic shapes, and passed PAXG on its maiden real run — the conjunctive legs (kurt AND
   weekend-ratio>3) individually missed a case that any real-number fixture would have caught
   at write time. If the incident's numbers exist anywhere (wiki, findings, incident log),
   copying them into the test file is cheaper than every alternative.

12. **A lane's green is a SCRIPT VERDICT, never a paragraph (AP-62, 2026-09-02).** "Tests
   green, reds pre-existing, mutants die" written by hand was wrong at least once per round
   across seven RP-30b I3 rounds. The exit gate is `scripts/lane_gate.sh <push-base>
   <gate-files> [--mutants] [--digest]` and its VERDICT block pasted verbatim; a verifier
   finding with no red test or mutant is INFO, not a repair item (skill `contract-gate` §4).
   The gate script gets its own negative control (tactic 1): a seeded probe with a known
   lint hit, a surviving mutant and a drifted anchor must come back RED before the first
   real lane trusts it.

Related requirement (from the #1 rule): **every benchmark/eval MUST exercise the ACTUAL
pipeline**, score against a **real independent oracle**, and report the **hollow-green
(gate-false-positive) rate**. A harness that re-implements or stubs the spine it claims to prove
is forbidden.

## Tactic 9 — a guard's operand must be the CONSUMED quantity, never an upstream proxy (2026-08-26)

The W6-G basis guard floored `len(padded_genomes)` (the elite INPUT count) while the
protected decision consumed `gate.n_configs` (the POST-DEDUP column count) — an 8-clone
elite passed the floor with a 2-column verdict. Same mirror class as verifying your own
launch-env names: the guard checked the author's proxy, not the consumer's operand. When
writing ANY floor/threshold/eligibility guard: name the exact variable the protected
decision reads, trace where it is produced (here: inside the gate, after two dedups), and
gate on THAT — if it is not available at the guard site, thread it there (the W6-G2 fix
stores the verdict's n_configs on the snapshot). A guard on a proxy is a mirror, and its
tests will be mirrors too (every W6-G test built snapshots by hand and never ran a real
verdict, so 7/7 mutants died yet the fail-open survived).
