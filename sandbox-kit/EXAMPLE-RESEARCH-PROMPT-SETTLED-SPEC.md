<!-- WHY (whole file): this is a WORKED EXAMPLE for sandbox-kit/RESEARCH-PROMPT-GUIDE.md's
     SETTLED-SPEC mode. The subject ("cfgmig", a config-migration tool) is INVENTED and neutral so
     this file copies cleanly into any repo — copy the SHAPE, not the subject. It mirrors the shape
     of docs/research/prompts/RESEARCH-PROMPT-45.md in the source repo (the guide's own best
     example) but is fully self-contained: no other file needs to exist for this prompt to be
     paste-ready. Every section below is annotated with the exact guide rule it satisfies so you
     can check compliance line-by-line when you author your own. -->

# RESEARCH-PROMPT-EX1 — NESTED-KEY MIGRATION LOSS: a depth-generalized flatten mechanism for `cfgmig`

<!-- WHY: guide house-structure element "question-first" + "lead with the real question, not the
     substrate" — the title names the actual failure (nested-key loss), not the tool/substrate
     (the flatten function) that happens to host it. -->

> **At a glance:** `cfgmig` (our legacy-config → current-schema migration tool) correctly migrates
> **40/40** verbatim-key configs and **32/40** renamed-key configs in the committed 80-file corpus,
> but only **6/40** configs that nest a moved key two or more levels deep — not because the schema
> validator or the parser is wrong, but because the key-mapper's flatten step recurses exactly one
> level by a hardcoded loop bound, silently dropping anything nested deeper. We proved this with a
> per-file measured table (below) that also falsifies the three fixes tried so far. This brief
> researches the ORTHOGONAL fix: a flatten mechanism that generalizes to arbitrary nesting depth
> without regressing the 72 files that already migrate correctly.
> Status: RESEARCH ONLY — nothing is being built until findings return. Tracker: task #EX-1.
> Council: SKIPPED deliberately — the framing is settled by a measured falsification (below), not
> by open strategic questions; per RESEARCH-PROMPT-GUIDE this substitution is stated explicitly.

<!-- WHY: mirrors RP-45's at-a-glance block. Also satisfies "Lead with the real question, not the
     substrate" (the paragraph states the QUESTION — a depth-general flatten mechanism — before any
     implementation detail) and pre-declares the council-skip per the guide's explicit-substitution
     rule instead of silently omitting step 1.5. -->

## Current-state capability ledger (proven-live vs built-never-run vs absent — do not re-derive)

<!-- WHY: guide's "what-the-system-IS is MANDATORY and must be a CONCRETE, EXHAUSTIVE INVENTORY of
     what is ALREADY BUILT — name the module:function and what each does" — the #1 research
     failure mode is the agent not knowing what's already built; this section is the fix. -->

- **Proven live:** deterministic migration spine — `cfgmig/parse.py:load_legacy` (YAML parse, no
  side effects) → `cfgmig/keymap.py:rewrite_keys` (verbatim + renamed key lookup against the
  committed `keymap.yaml` table) → `cfgmig/validate.py:check_schema` (JSON-Schema v3 validation,
  exit-code only, no LLM). Verbatim-key migrations 40/40 correct (byte-identical to golden output);
  renamed-key migrations 32/40 correct (8 misses are a separate, already-tracked issue: task #EX-4,
  out of scope here).
- **The hole (this brief):** nested-key migrations 6/40 correct; 34/40 silently drop the moved key
  instead of relocating it, and `validate.py` still exits 0 because the target schema treats the
  key as optional — so today's gate is a **false negative that currently reads as a pass**.
- **Built-never-run:** `cfgmig/keymap.py:rewrite_keys_recursive` — a recursive variant written
  during a 2026-05 spike, never wired into the CLI entry point (`cfgmig/cli.py:main` still calls
  `rewrite_keys`), never covered by the corpus test. Its existence must not be assumed as "the fix"
  without re-verifying it against the current 80-file corpus and the two guarded invariants below —
  it predates the renamed-key fix and may have rotted.
- **Absent:** no depth-general flatten mechanism ships in `keymap.py` today. No cycle/self-reference
  guard exists anywhere in the migration spine.
- **Falsified already (do NOT propose again):** (a) raising the hardcoded recursion bound in
  `rewrite_keys` from 1 to a large constant (10) — fixed 28/34 nested misses but hung
  indefinitely on the two corpus files containing YAML anchor self-references (`configs/anchor_01.
  legacy.yaml`, `anchor_07.legacy.yaml`), because nothing bounds a cycle; (b) a regex-based
  dotted-path rewrite (`old\.nested\.key` → `new.key`) — broke 5 previously-passing verbatim files
  whose *values* (not keys) legitimately contain literal dots (e.g. `version: "1.2.3"` got
  corrupted), measured and reverted at commit `<hash>`; (c) inferring nesting depth from file size
  — plotted depth vs. byte-size across all 80 corpus files, correlation r=0.04, no usable signal.
- **Full evidence:** the 80-file before/after table + per-file root causes live in
  `scratchpad/ex1_corpus_table.json` (this session); task #EX-1 carries the digest.

## SETTLED direction (do not re-open)

<!-- WHY: guide's "Separate the research DIRECTION from the research QUESTION... You decide
     direction and mark it SETTLED — never ask the agent to pick it." Also satisfies "CORE SYSTEM
     INVARIANTS ARE SETTLED GUARDRAILS — NEVER expose them as open" for items 3-4 below: they are
     stated as non-negotiable, with the rejected alternative named. -->

1. The fix lives at the **key-mapper/flatten layer** (`cfgmig/keymap.py`), NOT at the parser
   (already correct — proven by 40/40 verbatim passes) and NOT at the schema validator (already
   correct against a well-formed rewrite — proven by the 6 nested files that DO pass). The parse
   and validate stages stay untouched.
2. `rewrite_keys_recursive` (built-never-run, above) is a CANDIDATE input to this research, not a
   pre-accepted answer — it must clear the same measured bar as any other candidate.
3. **NON-NEGOTIABLE — no silent drops.** A key that cannot be confidently relocated MUST fail the
   migration (nonzero exit, named key in the error) — never emit output missing the key. (Rejected
   alternative: today's de-facto behavior of silently dropping it and exiting 0 — this is the bug,
   not a fallback to preserve.)
4. **NON-NEGOTIABLE — cycle safety.** Any recursive/iterative traversal MUST terminate on
   self-referential YAML anchors without a hang or a crash. (Rejected alternative: an unbounded
   recursion bump — falsified above, hangs on 2/80 corpus files.)
5. **PRIORITY (SETTLED — do not ask which is primary):** the primary deliverable is the
   flatten-mechanism verdict below; the migration plan for already-shipped-wrong output files
   (Subordinate, below) is downstream of it and cannot be scoped until the mechanism is chosen.

## PRIMARY DELIVERABLE (one)

<!-- WHY: guide's "ONE primary deliverable. Never double-label 'the crux'" + the PRIORITY line
     above pre-closes any fork between "which mechanism" and "how to migrate old output" so the
     agent cannot stop to ask which is primary. -->

A verdict + design spec for the depth-general flatten mechanism, evaluated against the committed
80-file corpus. Candidate mechanisms to resolve —
**[PRIMARY-SOURCE TECHNICAL — resolve to a verdict, with measured evidence per candidate]**:

<!-- WHY: guide's "its inline resolution-KIND token" — each candidate below is implicitly covered
     by this one token since they are evaluated as a single ranked set against one gate; a brief
     with genuinely independent open questions would tag each with its OWN token (see the
     EXPLORATORY example for a brief with more than one). -->

- **(a) True recursive descent with an explicit visited-path cycle guard** — walk the legacy tree,
  track the path of keys visited, refuse (fail-closed) on a repeat. Cheap, deterministic; risk =
  correctly identifying "self-reference" vs. "same key name at two sibling branches" (not a cycle).
  Must be MEASURED against all 80 corpus files including the 2 anchor files.
- **(b) Iterative worklist algorithm** — a stack/queue of (path, node) pairs, no call-stack
  recursion, natural depth cap via a max-iterations guard. Same cycle-safety property as (a) by
  construction (a worklist can't grow unboundedly on a finite tree); risk = readability/complexity
  vs. (a) — quantify with a code-size/branch-count comparison, not a vibe.
- **(c) Adopt an existing deep-merge/deep-path library already used elsewhere in the toolchain, if
  one is committed** (audit the lockfile before proposing a NEW dependency) — bring evidence of its
  cycle-safety and license, not vibes; if no such library is already a dependency, this candidate is
  disqualified by the "ADOPT, don't invent" rule only when adoption is truly free (already vendored).
- **(d) Any published/primary-sourced alternative** (e.g. a tree-diff/JSON-patch algorithm) that
  fits invariants 3–4 above — bring evidence, not vibes.

Subordinate (relationship stated):

<!-- WHY: guide's "mark every other open question explicitly subordinate with its relationship
     stated (validity-GATE-on-the-primary / substrate / downstream), never as a competing
     primary." -->

- **Migration plan for already-migrated-wrong outputs** [DESIGN fork — DECIDE; downstream of the
  primary] — once a correct flatten mechanism ships, existing repos that ran the buggy `cfgmig`
  hold silently-truncated config files. Specify a re-migration script (dry-run first, precedent:
  none yet in this project — this would be the first) that re-runs the fixed tool against the
  ORIGINAL legacy source (never the corrupted output) and diffs against the previous output before
  overwriting.
- **Validity gate on the primary** [EMPIRICAL GATE — run FIRST on any candidate] — re-run the
  80-file corpus harness (`scratchpad/ex1_corpus_table.json`'s method, offline, against copies, no
  network) plus the committed `keymap.py` unit suite. Acceptance: nested ≥36/40 correct, verbatim
  stays 40/40 (zero regression), renamed stays ≥32/40 (zero regression), both anchor files
  terminate (pass or clean fail, never hang), zero silent drops across all 80 files.

<!-- WHY: satisfies the guide's "(c) irreducibly-EMPIRICAL gate ... stays OPEN as a runnable gate:
     exact corpus + metric + operating-point + attached decision rule" — this is the ONLY item
     allowed to end the report unresolved, and it's stated as a gate to RUN, not a hedge. -->

Deliverable shape: a findings report with (1) the per-candidate measured table on the real 80-file
corpus, (2) the chosen mechanism + why the runners-up lose, (3) the exact seams (`file:line`) an
implementing engineer touches, (4) the migration plan for already-wrong outputs, (5) the honest
NOT-resolved list.
Decide; do not ask.

<!-- WHY: guide's mandatory closing line, verbatim, plus the mandatory 5-part deliverable shape
     ("question-first · intended design · what-the-system-IS · SETTLED · ranked open questions ·
     'what would change the plan' [folded into the empirical gate here] · deliverable"). This is
     SETTLED-SPEC mode: the strategic answer (fix lives at the flatten layer) is already decided
     and proven in-repo by the falsified-already table; the agent's job is VERIFY + DEEPEN +
     CHALLENGE the candidate mechanisms, not re-derive the direction. -->
