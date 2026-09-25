---
name: anti-hollow-green
description: The anti-hollow-green tactics — general-purpose, any project: the full operational checklist behind the #1 NO STUBS rule, with war-story evidence (NaN fail-open wormholes, os.environ config leaks, mutation-testing, oracle independence, searchable-parameter-domain attack surface). Load when designing or reviewing ANY gate, oracle, test suite, benchmark, guard on externally-sourced values, or numeric fail-closed check; when a green looks too easy; or when bounding any optimizer/search parameter domain. the project instructions file carries the rule + one-line tactic index — this skill is the authoritative expansion.
---

> **HARNESS PORT.** This copy is read by Codex CLI (`.agents/skills/`) and by Hermes
> (via `skills.external_dirs`). It is the same protocol as `.claude/skills/anti-hollow-green/SKILL.md`;
> only lines naming a Claude-Code-specific mechanism were reworded — see `docs/HARNESS-PORTS.md`.
> "the project instructions file" = `AGENTS.md` on Codex, `.hermes.md` on Hermes.
> Model-tier names below ("Fable light", "Opus 5 lane") are PROTOCOL LABELS, not routing
> instructions: these harnesses run ONE model. Where the protocol calls for an independent
> verifier, hand the work BACK to the sandbox lane — never self-accept.

# Anti-hollow-green TACTICS — operational checklist (every gate, oracle, test, increment)

The #1 rule (the project instructions file): NEVER replace a real component with a stub, fake, no-op, hardcoded
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
   **(f) The interpreter's import path is an input too (AF-AP-81, GOV1 2026-09-15): a suite that imports an
   upstream the repo neither vendors nor installs reaches it ONLY through the declared input's own contract — a
   pin/fixture that verifies the root and inserts its paths — never an ambient PYTHONPATH; the lane shell read
   `29 passed`, the bare static-copy gate `12 failed, 17 passed`. A report's count is graded in the BARE gate on
   the coordinator's venue before it is believed, and a mutation driver exports only repo roots (an ambient
   upstream path masked the root-insertion mutant).**
   **(g) To prove a run does not need package X, stop X in every process the run starts and record each try
   (AF-AP-179, J1-5 2026-09-24).** A block set up in the test's own process does not follow the scripts the tests
   launch, and a check that looks only for failures lets through an import the code catches or a test that skips
   when the import fails. Load the block in every Python process: a `sitecustomize.py` on `PYTHONPATH` that adds a
   `sys.meta_path` finder (it also sees `importlib.import_module`, which a `builtins.__import__` hook misses). Write
   each try to a log and require an empty log. Keep three controls: a plain import fails, a caught import still
   appears in the log, and a child process is reached. A child started with `-I`, `-S` or `-E`, or with an `env=`
   that drops `PYTHONPATH`, is outside the block; say so in the claim or forbid it.
   **(h) A venue skip keys on the declaration that the runner holding the module's inputs exports: the interpreter,
   never the machine (AF-AP-24's venue form; QJ2 2026-09-25).** `tests/test_qwen_jev.py` needs `transformers`, which only
   the PC's `~/venv-qwenjev` holds. A skip on `S0_01_VENUE=pc` would have failed the PC suite at collection
   (`scripts/pc_suite.sh` exports that flag with `~/venv-agent-factory`) and skipped the lane's own run
   (`scripts/test_summary.sh` exports `S0_01_VENUE=sandbox` by default). A dedicated declaration, exported only by the
   run that holds the inputs (`QWEN_JEV_VENUE=pc`), fixed both. Before a declaration ships, run the module under every
   runner that sets the flag it keys on, and show the skip or the pass on each.
3. **Mutation-testing IS the hollow-green detector.** Inject bugs into the code-under-gate; a gate
   A CONTROL mutation is itself verified before its effect is asserted — same length, same multiset (`sorted(moved) == sorted(orig)`), different order — and every "the output differs" control is paired with a NAMED production mutant it must kill: a slice-built "swap" that duplicated the neighbour let two production mutants survive a 476-test suite while the real checker's verdicts changed (S0-01 golden, VERIFY-VB-F12 2026-09-21, AF-AP-109).
   that still passes is hollow. Demand BRANCH coverage. A gate surviving no mutants is a tautology
   — reject it. **3-EQ. Mutate the EQUIVALENCE CLASS, not the named specimen (AF-AP-30, S0-11
   closed 3× before this stuck).** When a review names cases, the fix and its tests must cover
   every EQUIVALENT expression of the same defect, or the class re-appears one surface out. For a
   forbidden-call scan: the aliased import (`import subprocess as sp`), the from-import
   (`from subprocess import run`), the variable command (`cmd=[…]; run(cmd)`), the variable/computed
   argument (`mode=0o777`, `0o700|0o077`), the env-defaulted config (`${VAR:-host}`). For a
   filter: prefix-vs-exact (`RUBRIC_*` is not a closed set), blacklist-vs-allowlist. For a value
   check: boundary and wrong-type values (`isinstance(True,int)` is true — use `type(x) is int`
   plus a range). For an evidence source: self-report-vs-external-observation (never trust the
   subject's own report — a fake wrapper fabricates a clean one; observe from the kernel/parent).
   And when static scanning is the class's losing game (infinite equivalents), STOP adding
   synonyms — move the contract to a machine-readable policy field or a runtime-denial test, and
   state the scan's limits honestly. **3a. Mutants live in tmp/scratchpad COPIES — even inside COMMITTED test
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
   module-identity check, then re-run from inside a full mutant tree copy). The same holds for the BYTECODE (AF-AP-192, FT1 M11 2026-09-24): CPython reuses a cached `.pyc` whose recorded source mtime (whole seconds) and size match, so a same-length mutant written within the same second as the previous one runs the PREVIOUS mutant; run every mutant with `PYTHONDONTWRITEBYTECODE=1` from a fresh copy (or clear `__pycache__`), and re-run a survivor once with the cache cleared before reporting it. **3c. A mutant must COMPILE and
   COLLECT before its verdict counts (AF-AP-78, 2026-09-15):** a driver that maps every non-zero rc to KILLED mints
   a hollow score on a `SyntaxError` / `ImportError` / "no tests ran" — VERIFY-CK14 found a TABLE_ROWS row whose
   `sed` produced `keyword argument repeated` and a `KILLED … rc=2`. The driver `py_compile`s (or `ast.parse`s) every
   mutated file and runs a collect-only pass first; a failure there prints `INVALID <row>` and the summary gates on
   `INVALID=0`; a kill is a pasted assertion line (`FAILED … Failure`/`AssertionError`), never a bare rc.
   **3c. Red-proof new regression tests against the PRE-FIX version from git history, no tree
   mutation:** `git show <old-sha>:path > scratchpad/old.py`, load via
   `importlib.util.spec_from_file_location` (print `__file__` — same identity rule as 3b), and
   reproduce the exact failure the new test pins (2026-09-01 repair round: three verifier
   findings proved red this way in one probe — no stash, no checkout, shared tree untouched).
   **3d. Gate a fake on PHASE, never on call ORDINAL (2026-09-07, mutant DL-INLINE).** A fixture
   that selects behaviour by call count ("attempt 1 fails, attempt 2 succeeds") encodes the
   CURRENT loop shape — the first thing a mutant changes. A verifier-proposed killer for an
   inlined retry deadline printed its call count and still let the mutant live: the mutated
   loop's second attempt succeeded 2 ms later with the identical error text, count still 2. Key
   the fake on observable STATE only one phase can produce (a thread the code starts after the
   loop, a file the later stage writes, a protocol byte) and assert the mechanism from the
   wrapper. And RUN the named mutant before landing the killer: a proposed killer is a
   hypothesis, not a kill.
   **3e. When you rewrite a parser, lexer or screen, run the OLD version's refusals through the
   NEW one (AF-AP-153, 2026-09-23, VERIFY-J1-0-R4 V-01).** Give both versions the texts the old
   one refused plus fresh hostile variants; each old refusal must still be refused, or the report
   names it as a deliberate change. J1-0-R4 matched bash on the heredoc forms it listed but kept
   the escapes of an ANSI-C `$'…'` delimiter, which bash translates: a four-line gate that R3
   refused with rc 4 passed R4 as clean (rc 0), and neither the new tests nor the old ones went
   red. The other half, testing a verifier's proposed fix before adopting it, is orchestration
   0d″.
   **3f. Report a measured zero together with what its generator can draw (VERIFY-J1-1-R3, 2026-09-24; D-067
   void, D-068).** Zero failures over generated inputs covers only the input classes the generator produces. The
   J1-1-R3 builder counted 0 leaks with its own generator, and D-067 was ruled on that count. That generator never
   made a mixed-case `KEY` name, and its body count did not see special letters; the independent verifier's
   generator found a redacted value in the ledger line on 9 of 165,000 inputs. State the generator's alphabet next
   to the zero (name cases, character classes, lengths, separators, and what it cannot make), and do not claim the
   zero unless the class that motivated the test is inside that alphabet. A decision that rests on a builder's zero
   stays conditional until an independent generator reproduces it (orchestration 0f).
   **The driver's denominator is a LITERAL from the brief, never a sum of what ran (AF-AP-84, VERIFY-N5l 2026-09-15):**
   `expected=$((killed + survived))` let a deleted row read `EXPECTED=9 KILLED=9 SURVIVED=0` — pin `EXPECTED=N`, gate
   `[[ $killed -eq $EXPECTED ]]`, and give the driver a self-test (a copy with one row deleted must exit non-zero). A census or
   sweep named for a GENERAL property observes the whole population or names its subset (AF-AP-85: a framedir-only fd count
   read `CENSUS=0` while an inheritable pipe leaked through the same Popen).
   **A resource-hygiene census wraps the PRODUCTION call, never the fixture’s own cleanup (AF-AP-110, 2026-09-22):** the review
   binding’s test fixture killed its throwaway agents (`gpgconf --kill all`), which proved the TESTS clean up — while the production
   `verify_review` left one orphan `gpg-agent --daemon` per call behind its deleted TemporaryDirectory, unobserved through 16 green
   tests. The gate for "no process / fd / file / socket is left behind" is a before/after census around ONE production call with the
   fixture’s cleanup disabled or absent; a fixture that tidies is a fixture, not evidence.

4. **Ban hardcoded expected outputs.** The oracle is spec-authored, independent, un-importable by
   the thing it grades. **4a. DROP an inapplicable assertion, NEVER REWRITE it** (rewriting lets
   the graded artifact choose its own oracle value). Drop ONLY when: (a) change provably scoped,
   (b) ≥1 retained assertion is INVARIANT to the change, (c) the reduced gate still fails an
   empty/mutant workflow. Fail any leg → abstain, never mint.
   **4c. A feature derived from the label is a leak, not a signal** (2026-09-24, AF-AP-189): before any evaluation or training on captured rows, check every input field against the answer. `decide-harvest` stored the v1 finding's `disposition` (computed from its class) in the state, so a model given the whole state would score the blocking split perfectly.
5. **No LLM-judge in the gate spine.** Gate/oracle/assertion execution is deterministic
   exit-code / set-hash comparison; an LLM enters ONLY at codify/generate/tune time.
6. **A stress benchmark's value is the defects it FORCES, not the green it prints.** Design the
   matrix to hunt (adversarial cases, cross-family negatives, modified-requirement asks); a red
   first pass is the expected good outcome.
7. **The tell:** if a green was produced without the part it claims to need actually running (kill
   the model mid-graft and it still "succeeds"; disable the store and cost is unchanged), the
   capability does not exist — that is a falsification to REPORT, never a number to tune past.
   **Ported-tool corollary (2026-09-23, AF-AP-121):** when a third-party tool is carried from its native harness into ours, the smoke runs OUR production invocation with none of the tool's native-harness state planted, and it reads the tool's own effect instrument (an endpoint counter, an archive, a log line). jev-pruner, a Codex plugin, engages only after its Codex hook writes a transcript pointer. PCJ1's setup smoke planted that pointer under a temporary HOME and went green, while a Hermes lane never has one: through the lane path, 108,894 bytes came back whole, the endpoint's call counter did not move, and no archive was written. A fail-open wrapper's "ON" banner is an availability claim, not a measured effect.
   **Stand-in corollary (2026-09-23, S0-05's C0 probe, AF-AP-139):** a test stand-in for a named real service answers the probe's exact request the way that service does, and that answer is MEASURED on the real service before the design freezes; a stand-in that sends the same 2xx for every path and method grades the positive control against nothing. C0 asked `GET /v1/models` and every stand-in answered 200, while on the PC the real OmniRoute answered 401 there and the real relay 404, so the live leg's positive control would have failed. Key the stand-in's status on the path, and give it a negative control that refuses on the probe path. The same holds for a stand-in's INPUT grammar (2026-09-24, VERIFY-JT3-R1 N-1, AF-AP-194): the JT3 search hook answered Grep calls by running rg, but the Grep tool splits `glob` on commas and whitespace outside braces and rg reads one glob, so `*.sh,*.md` was answered "0 hits" where the tool finds 14 files. Parse every input as the tool does, or pass through on any input outside the subset proven equal.
   **Hollow-red corollary (2026-09-24, AF-AP-195):** the mirror of a hollow green is a false LIMIT: one layer's refusal (an adapter's safety check, a chat template, a parser) recorded as the model's or the system's incapacity. simple-jev's compiler refused RWKV-7's yes/no labels, and the G0 plan read "noul NOT run"; the owner asked whether the limit was real. It was the prompt: the prefill ends with a space, the RWKV World tokenizer merges that space with the digit, and without the space all nine labels are single stable tokens. Before recording "X cannot do Y", name the layer that refused and try its cheapest variation; record the refusal as that layer's, and run the capability through the varied path as a declared deviation.
   **Subject-in-window corollary (2026-09-25, AF-AP-208):** a model's answer is evidence only if the model read its subject. A windowed reader keeps the first N tokens of its input: the Laya server's fan-out added the chunk after up to 53 history segments, and Laya keeps 1,024 tokens, so every chunk question was answered without its chunk (0.52-0.60 on every answer, nothing pruned, no error). Before trusting a score, rebuild the input exactly as the model's own builder reads it (`laya.common.build_sequence`; `scripts/laya_ft/build_dataset.py` `Fitter`) and check that the subject survives. A narrow band of answers across unlike inputs is the tell. Its test half (the K265 brief, measured): the server's unit test compared the per-chunk states with dict equality, which ignores key order, so the suite passed with the subject last and with it first; `tests/test_jev_client.py` asserts its sent states the same way. When the consumer reads order (a serialization, then a prefix cut), the test compares order: the key list or the serialized bytes, never dict equality.
   **Remote-program corollary (2026-09-23, the T94 landing, AF-AP-162):** a command string built for the far side of a bridge is a program, and its test double RUNS it (`bash -c`) against a fake remote root that no local path matches; it never answers from the command's text. A `case` arm keyed on a substring returns a canned state, so the program's logic and quoting never run, and a lane that adds a case arm for its own new string has written the test's answer: T94's rewritten poll probe passed 42/42 that way while a doubled escape (AF-AP-89) made every poll a syntax error on the PC. Every branch that reads remote state gets its own executed case, and each mutant runs as the lane's user as well as root (VERIFY-T94 F-1).
8. **A GENE/PARAMETER DOMAIN is part of the attack surface:** any searchable value profitable
   ONLY inside one engine's fill/semantics model is a latent exploit the optimizer WILL find —
   bound domains with ECONOMIC-REALISM floors (fees+slippage-derived), lock them with tests, and
   treat single-engine robustness statistics (PBO inside the same engine) as structurally blind to
   cross-engine artifacts (x58 tsl 3e-05: the whole fitness summit was a vbt fill artifact; the
   paper layer caught it on day one).

   **The same blindness hits a CONTAINMENT claim read through one instrument (agent-factory 2026-09-23, AF-AP-128).**
   A claim about a namespace rests on two instruments whose view is scoped to that namespace. sysfs keeps the view of the
   netns that mounted it: under `unshare -n` or `nsenter --net` with no sysfs remount, `/sys/class/net` lists the HOST's
   interfaces (`ip netns exec` and container runtimes remount it). Read netns facts from `/proc/self/net/dev` and
   `ip -o link`. The CD1 probe first read a no-network user namespace as networked through sysfs; the second instrument
   caught it before any conclusion.
   **Scrubber corollary (2026-09-25, the session export, task #252):** a scrubber and its gate share one list of secret
   SHAPES, so the gate's 0 says nothing about a secret in a shape the list lacks. The independent instrument is a VALUE
   check: read every known secret where it lives, in process, and count it in the output, whole, by 8-byte windows and in
   its printed forms (`scripts/known_values_check.py`, names and counts only). Run it on every export before it ships, and
   on the repository's tracked files when committed text feeds an exemption.

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

13. **BIND the recorded proof to the CODE that produced it (AF-AP-31, S0-11 cycle-5).** A result
   artifact that records only command/output hashes is not bound to its producer: neuter the
   checker (replace the real isolation with a pass-through), keep the stale green artifact, and a
   validator that re-checks schema + a digest-over-the-runs still says PRESENT — because the
   positive hash is merely `sha256("PASS\n")` and CI never re-executes. The fix is an
   ATTESTATION: the runner records the sha256 of every executable input (checker source, spec,
   fixtures, design), the validator RE-DERIVES those digests from the tree and fails on any
   mismatch, and the schema REQUIRES the field. The kill-switch question here is literal — "could
   this green survive the real component being replaced by a no-op?" — and on an incapable venue
   where re-execution is impossible, the artifact must be regenerated on a CAPABLE one and the
   incapable check verifies the source binding, never a frozen self-hash. A validator that never
   re-derives from source is trusting a frozen lie. **The binding must be the COMPLETE trust
   closure, not the named files (S0-11 cycle-6, AF-AP-30 recurrence-6):** a first attestation
   that hashed only the proof-local inputs left the RUNNER and the VALIDATOR un-attested, so
   mutating the runner (every leg → `/usr/bin/true`) made the run fail while the stale green
   survived, and the validator still said PRESENT. Attest EVERYTHING that produces OR checks the
   verdict — the runner, the validator, the registry, the schemas — so a tooling mutation flips
   the artifact INVALID. Two siblings in the same class: (a) **bind the recorded run to the
   attested spec** — a result that records its own commands is forgeable (swap the positive
   command for `/usr/bin/true`, recompute the self-digest) until the validator checks the runs
   against the spec one-for-one (count, order, command, exit, each negative reason); a self-digest
   proves internal consistency, never fidelity to the contract. (b) **never preserve an artifact
   across a real failure** — an artifact is kept ONLY for an explicit capability-defer; a genuine
   run failure must INVALIDATE (remove) it, or a mutated producer that makes the proof fail leaves
   the previous green in place.
14. **A NAMED PROPERTY is not a USABLE contract — prove the property end-to-end (AF-AP-30
   recurrence-5, S0-11 cycle-5).** "The rubric gets a separate cwd" was satisfied by a
   root-owned `0700` temp dir the dropped uid could neither write nor collect from, deleted
   before anyone read it — a different directory, not a usable workspace. When a requirement is a
   CAPABILITY (writable workspace, reachable endpoint, persisted record), the gate must exercise
   the real workload the capability exists for: WRITE to it as the real principal, COLLECT the
   result back, then clean up — and fail if the collection is empty. A property observed as
   "present but different" while the workload that needs it never runs is a named-property hollow
   green; drive the actual write/collect/cleanup (or send/receive, or persist/read-back) so an
   unusable-but-present resource fails loud.

15. **An identity sampled at SPAWN time is the identity of a STAGE, not of the worker (AF-AP-55,
   VERIFY-N5e F1, 2026-09-06).** The S0-01 probe read `/proc/<pid>/exe` right after `Popen` and took
   the first reading as authoritative; for a `#!/usr/bin/env python3` or sh-wrapper agent that
   reading is `/usr/bin/env` or `/usr/bin/dash` — the launcher, not the interpreter that speaks the
   protocol — silently and run-to-run variable (9/12, 3/3) while the parent commit read python
   12/12. A lane minted the regression because every fixture was single-exec (`#!{sys.executable}`):
   the suite could not see the class. Rule: pin any identity reading (interpreter, argv, cwd, a
   connection's peer) to the first event that ONLY the final stage can produce (here the first
   protocol byte) and let that reading overwrite the earlier one; the early reading is a fallback
   for workers that never emit; and the fixture set MUST carry a multi-stage shape (an `env`
   shebang, a wrapper with `exec`) or the pin is untested. Corollary: a comment or commit that
   describes a fallback arm is a CLAIM — prove it reachable (a raise-instrument inside it fires in
   some test) or delete it (VERIFY-N5e F2: the `_last_good` arm was dead across 242 tests and 14
   agent shapes).

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

## Tactic 10 — world-scoped enumerations: EXACT over a synthetic world, BOUNDED over the live one (2026-09-07, AF-AP-59)

A test over a system-wide listing (ps/proc rows, listening ports, a directory walk, a pinned-path census)
has two honest shapes and one flake.
1. **The live world:** assert the OWNED subset exactly and CHARACTERISE the rest — every foreign row must
   be admissible under the producer's only other rule (here: it names a pinned path); anything else fails
   loud (`unexplained foreign row`), and the negative control of that helper is COMMITTED, never just run.
   A header that counts the FULL table is then a LOWER bound from inside one test, never an exact number:
   a sibling worker's helper (the PC gate runs 8 xdist workers) can sit in the table between two of one
   test's reads.
2. **The exact contract lives where the world is synthetic:** a `ps` shim on PATH that prints N rows and
   nothing else makes "pinned_present == 2 over the full table", "the helper-shaped row is dropped from the
   body but counted", "the unpinned foreign row is absent" EXACT and deterministic on every venue — and the
   producer mutants (count over the body instead of the table; helper filter off) die on it.
3. **The flake:** `if not foreign: assert pinned_present == "0"` — exact over the LIVE world, green only
   while the test is alone on the box (VERIFY-CK10 F-R10-20 asked for it; rejected on this evidence).
   VERIFY-CK11 then showed the rejection was right on STRONGER grounds: the header counts the full table and
   the body is a filtered subset, so the two numbers count DIFFERENT populations and the equality fails
   deterministically (one owned row + one helper-shaped pinned row → body empty, header 1) — no sibling worker
   needed. Before asserting a relation between two counters, check they count the same population.
War story: the PC checker gate's first rerun of checkpoint 8p went red on a sibling xdist worker's
`frame_tee.py` sleeper inside a world-scoped scan body (run 20260907T161133Z); the fix was shape 1 plus the
two committed controls, and shape 2 for the count (`tests/test_s0_01_pc_post_scan.py`).
