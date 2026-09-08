# Lane M2 — S0-06 round 2: the leak agent seeded, the oracles scoped to the records, the "no request" instrument as an allowlist plus a substrate-side witness, hostile shapes named not crashed, the substrate digest bound to the run, the raw instruments' provenance read (build lane: PC Hermes `code-implementer` when the slot is free, else sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".) Lane M1's landing is `380877b`
(pushed); its report was amended on the tip (`e27eaaa`); the 56 files are otherwise unchanged at HEAD.

**Why:** VERIFY-M1 (report `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/wf-results-r5/VERIFY-M1.md`
— READ IT WHOLE FIRST; it is the contract for this round) graded lane M1 NOT-READY with ONE blocker and a fix-before-capture set.
**F-1 (blocker):** `run_s0_06_legs.sh:50-51` seeds `--agent "$S0_06_AGENT"` (a-alpha) only, while `collect_leg.sh:106,115` runs the
leak leg as `$S0_06_LEAK_AGENT` (a-beta) → `agent--a-beta` never exists → ai-memory answers 404 (`api.rs:993-1007`) → the adapter
degrades → CLI exit 3 → `set -e` aborts the leg before anything is graded; and even with an `ok` recall the a-beta honeytoken was
never staged (M24). **Fix-before-capture (re-capture is the expensive step):** F-2 `binary_sha256` is a FORMAT check — any 64-hex
passes; F-5 the "independent" raw instruments' own `workspace`/`project` are never read (four copies of ONE project's search pass
as four scopes); F-8 the "no request was made" instrument is a one-string denylist (`http-request`, `HTTP_REQUEST`, a nested
event all pass); F-9 the leak vacuity oracle is a whole-file substring — an EMPTY recall with the token in a stray field passes;
F-10 eight hostile bundle SHAPES crash the checker with a traceback and no reason line (a `KeyError`/`TypeError`/`AttributeError`
each), against the module's own exit contract; D-3b assertion 1 has ONE instrument (the subject's self-report), not two. Hardening
in the verifier's order: F-6 the winner's CONTENT never compared, F-7 the write path never re-derived from the idempotency key,
F-11 `normalize_hit` outside the `try` — a malformed 200 crashes `recall` with the same exit as a denial, F-3 the version literal,
F-4 `substrate.json` records the producer's own constants (never a readback), F-12/13/14/15/16/17/18/19/20/21/22. What held
and must stay held: the authorization boundary (15 corruption inputs, one call site, no env, a real red control, the denial proven
BEFORE the connect with a counting instrument), `merge` order-independent/clock-free/non-mutating, 9 of 10 injected bugs caught,
the claims boundary clean, nothing minted.

**Inputs (read in this order):** VERIFY-M1 whole · the lane brief `tasks/briefs/s0-06-m1-four-scope-adapter-real-ai-memory-checker-pc-legs.md`
and `tasks/briefs/s0-06-support/M1-report.md` · the pinned ai-memory source `/home/user/nerdherderdani/ai-memory` (73715b6f,
READ-ONLY): `crates/ai-memory-web/src/routes/api.rs:352-423,993-1007,1254-1263` · `crates/ai-memory-store/src/reader.rs:1174-1185,1483,6022-6030`
· `crates/ai-memory-mcp/src/admin.rs:6400` (`create_ws_proj`) · `crates/ai-memory-cli/src/commands/serve.rs` + `crates/ai-memory-web`
(HOW a request is logged — the trace/access-log layer, if any: the substrate-side witness for D-3b depends on what the server
writes to `serve.log` per request; READ it before designing item 7) · `crates/ai-memory-cli/src/commands/generate_auth_token.rs:26`
· `upstream.lock.yaml:33-38` · `docs/INCIDENT-LOG.md` (AF-AP-28, AF-AP-36, AF-AP-40, AF-AP-42, AF-AP-56, AF-AP-63, AF-AP-64) · the
pack `scripts/lane_context.sh -q 'what does the checker read from each leg and what does the runner write' -s check_substrate
check_precedence check_write_scope check_leak check_denied recall write -o pack.md proofs/S0-06/check_four_scope.py
proofs/S0-06/adapter/factory_memory.py` (run it first; attach it).
**Scope (under S0-06 + its test + your report):** `proofs/S0-06/adapter/factory_memory.py` · `proofs/S0-06/check_four_scope.py` ·
`proofs/S0-06/tools/pc/{run_s0_06_legs.sh, start_ai_memory.sh, seed_scopes.py, collect_leg.sh}` · `proofs/S0-06/spec.json` (REASONS
only if a negative changes) · `proofs/S0-06/fixtures/**` (regenerated where an item says — every fixture must be a shape the
producer can emit, AF-AP-42) · `tests/test_s0_06_four_scope.py` · `tasks/briefs/s0-06-support/M1-report.md` (ONLY the re-pasted
report_lint line + the class-6 citation, F-17) · report `tasks/briefs/s0-06-support/M2-report.md`. NOT yours: `docs/03_*`, the
ADRs (D-2 is the owner's; D-3's rename `company--<id>` is a plan change — state it in DISCREPANCIES, do not rename), the registry,
the ledger, `proofs/S0-06/adapter/bindings.json`'s identities (a-beta stays the leak agent). Shared-tree rules: never
`git stash/checkout/restore/reset/add/commit/push`; every gate from a `git archive <PIN> | tar -x` copy under
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/m2/ with your files copied in (`scripts/lane_gate.sh -r <PIN>
-f "<your files>" -t "tests/test_s0_06_four_scope.py tests/test_spec_probe_schemas.py tests/test_validate_ledger.py
tests/test_proof_runner.py" -n 2`, ONE foreground call, `LANE_GATE_DIR` under your scratch dir); explicit `--basetemp`; kill only your
own processes by pid (never pkill/pgrep -f); NEVER background a run and stop; no outward actions; NO PC bridge; NO cargo build; no
network beyond loopback servers you start; never read, print or commit a credential (the honeytokens are synthetic canaries by
design). Authorization: the owner's own memory boundary under test. Interpreter `/root/venv-agent-factory/bin/python`.

## Design (pinned — build it, do not redesign it; line numbers are `380877b`'s)
1. **F-1 — the leak agent is seeded, and the wiring is pinned.** After `run_s0_06_legs.sh:51`, a second `seed_scopes.py` call with
   `--agent "$S0_06_LEAK_AGENT"` (idempotent for the three shared projects — READ `seed_scopes.py` to confirm a re-run does not
   double-stage; if it does, make it idempotent by page path); the a-beta honeytoken is staged into `agent--a-beta`. Test (the
   verifier's, sandbox-only): every agent the legs query (`collect_leg.sh` `tuple_file`/`project_for` variables) ⊆ the agents the
   runner seeds — RED on `380877b` with `{'S0_06_LEAK_AGENT'}` (paste).
2. **F-9 — the vacuity oracle reads the records.** The authorized tokens must appear in `json.dumps(recall["records"], sort_keys=True)`;
   the forbidden half stays whole-file. Red: the verifier's V10/V11 (`records: []` + the token in a stray field / in
   `scopes_queried`) → `leak_empty`.
3. **F-8 — the denied leg's event set is an ALLOWLIST.** `{e["event"] for e in events} == {"scope_tuple_denied"}` else
   `denied_request` naming the extra names; V13/V14/V15 → RED; the empty stream stays `denied_status` (V16).
4. **D-3b — a second, substrate-side instrument for "no request was made".** READ how the pinned server logs requests (the
   `serve.log` the runner keeps — a tracing/access-log line per request? the web layer's trace layer?). If a per-request log line
   exists: `collect_leg.sh` records the count of `/api/v1` request lines in `serve.log` BEFORE and AFTER the denied recall
   (`denied/serve-count.json` with both numbers) and the checker asserts the delta is 0 — with the PAIRED POSITIVE CONTROL: the
   precedence leg records the same before/after and its delta must be ≥ 4 (the checker fails `denied_witness_vacuous` if the
   positive leg's delta is 0, so a server that logs nothing cannot pass by silence). If NO per-request log exists in the pinned
   server, use the socket-side witness the verifier demonstrated (a loopback `accept()` counter is not available for a foreign
   process — use `ss -tn` established-connection counts to the instance's port before/after, with the same positive control) and
   SAY which you built and why, citing the server source. Hostile bundle: a denied leg with delta 1 → RED; a bundle whose
   precedence delta is 0 → RED (vacuous).
5. **F-10 — hostile SHAPES are named, never tracebacks.** Wrap `check_substrate` and the four leg checks so `KeyError`/`TypeError`/
   `AttributeError`/`IndexError`/`ValueError` become `Fail("shape", leg=…, detail=…)` with a REASONS row `leg: {leg} evidence shape
   invalid ({detail})`; the adapter's absent `bindings.json` becomes a named `ValueError` too. Parametrised test over the verifier's
   eight shapes (+ the absent table): `rc == 1`, stdout is ONE reason line, `Traceback` not in stderr — RED on `380877b` (paste one).
6. **F-2/F-3/F-4 — the substrate record is an observation, bound to the run.** `start_ai_memory.sh` records `bin_path`, `cargo
   --version`, `rustc --version`, the `version_stdout` it already has, and the child's ACTUAL environment (`tr '\0' '\n' <
   /proc/$SERVE_PID/environ | grep '^AI_MEMORY_'`) as `posture_observed` — never a re-typed echo; `collect_leg.sh` re-hashes the
   binary at `bin_path` into each leg (`substrate-observed.json`) and the checker requires the digest to EQUAL the startup one and the
   version to appear in `version_stdout`; `binary_sha256` is renamed `binary_sha256_observed` with a docstring saying "the same
   binary throughout the run — provenance, not a pin" (no repo constant can pin a release build); `EXPECTED_VERSION` comes from
   `upstream.lock.yaml`'s `observed_version` by the same reader as the commit (F-3; the source test asserts no `"1.39.0"` literal in
   the checker). Red: V1 (any 64-hex) → RED because the two digests differ; a lock bumped to 1.40.0 → RED; a posture block that
   says `true` while `posture_observed` says `false` → RED. Regenerate the committed bundles' `substrate.json` to the producer's
   NEW shape (AF-AP-42: a fixture the producer cannot emit is a hollow green).
7. **F-5 — the raw instruments' provenance.** `collect_leg.sh` writes the fetched URL beside each raw file (`raw-<scope>.url`);
   `check_precedence`/`check_leak` require every hit's `workspace == "factory"` and `project` == the scope's project for the
   tuple in `tuple.json` (which the runner already writes and the checker must now READ); `check_write_scope` requires each
   `raw-<scope>.url` to name the expected `workspace`/`project` (PageSummary carries no project — say so). Red: V4/V5 → RED.
8. **F-6/F-7 — content and derivation.** The merged winner's `provenance.title`/`snippet` must equal the agent raw hit's; the
   write leg's `page_path` must equal `observations/` + sha256("\x1f".join([session, turn, event_id]))[:16] + `.md` re-derived IN
   THE CHECKER (a deliberate 3-line duplicate — an oracle that imports the subject is a mirror), and the raw listing's entry must
   carry `kind == "fact"`, `tier == "semantic"`. Red: V6/V7/V8/V9 → RED.
9. **F-11 — a malformed 200 degrades, never crashes.** Move the `normalize_hit` comprehension inside the `try`; catch `TypeError`
   at the three sites; a scope with a malformed body → `degraded` naming it; the CLI's exit codes: denied 1, degraded 3, a crash can
   never be 1 (a distinct exit, e.g. 70, for an unexpected exception at the top level with ONE stderr line). Red: the verifier's
   G1-G5 bodies against a loopback recording server → `degraded`.
10. **The rest, each one line or a test:** F-12 lock parse failures → `substrate_pin` named + a duplicate-key refusal, `import yaml`
    at module scope; F-13 `shadowed_scopes` a set minus the winner's scope; F-14 an unknown scope name in a bindings row →
    `ValueError` at load; F-15 `json.dumps(..., allow_nan=False)` at both sinks; F-16 the external-command comment lists exactly
    what the scripts invoke (`grep`, `nohup`, `head` in; `date`, `chmod` out) + the verifier's test; F-18 `shred -u` of `token` and
    `curl.cfg` in `stop_instance` (keep `serve.log` + `substrate.json`; print the path) and ONE token derivation (`sed '$!d'` at both
    sites); F-19 clone into `"$RUNDIR/src"` when `S0_06_SRC` is unset; F-20 the S_ISREG guard test (dir/fifo/symlink); F-21 a
    documented-limit comment at the two write sinks; F-22 a symlinked evidence root refused; F-23/F-24/F-25 as docstring notes (the
    `nondet` row's one non-adapter cause — rank ties at the `truncate(limit)` boundary; the query text kept out of the event's
    `path`). F-17: re-paste the M1 report's report_lint line from a real run and split the class-6 citation.
11. **Mutants:** the lane's 28 + the verifier's V1-V20, H1-H11, L1-L5, G1-G5, C10 — every survivor must DIE with a named killer
    (paste the line); the mutation audit of the gate (10 injected bugs) re-run with C10 dead.
12. **18-class self-sweep as an ENUMERATION** (counts + method per class; class 6 = six env domains incl. `HOME`; class 3 closed
    at the producer too — the checker prints exactly one stdout line on every exit).
13. **Report discipline:** FILE IDENTITY of the FINAL bytes; every `file:line` from `grep -n` on the FINAL bytes and
    `python3 scripts/report_lint.py <report> --map factory_memory.py=proofs/S0-06/adapter/factory_memory.py --map
    check_four_scope.py=proofs/S0-06/check_four_scope.py --map seed_scopes.py=proofs/S0-06/tools/pc/seed_scopes.py --map
    run_s0_06_legs.sh=proofs/S0-06/tools/pc/run_s0_06_legs.sh --map start_ai_memory.sh=proofs/S0-06/tools/pc/start_ai_memory.sh
    --map collect_leg.sh=proofs/S0-06/tools/pc/collect_leg.sh` pasted with MISS 0; the two `lane_gate.sh` RESULT lines pasted; every
    red-before on `380877b` beside its green-after; `ap_screen.py proofs/S0-06 proofs/S0-06/adapter proofs/S0-06/tools/pc` and
    `--tests` classified by run; `bash -n` on the three scripts; NOT-done first-class (the PC leg — VERIFY-M1's eight preconditions —
    the mint, D-2, D-3's rename).
