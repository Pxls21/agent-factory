# VERIFY-M1 — adversarial grade of lane M1 (S0-06 four-scope adapter: the authorization boundary, the deterministic merge, the substrate-identity checker with two instruments per assertion, the seed-path negative fixture, two hostile bundles, the PC leg runner)

You are an adversarial-verifier (Opus 5 in the sandbox, or the PC Hermes `adversarial-verifier` role). Repo /home/user/agent-factory,
branch claude/soundbox-kit-migration-iz1jwf. **PIN: `380877b`** (the commit carrying the lane's 56 files + its report). Grade
the bytes of `git archive 380877b` from a copy under the session scratchpad /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/
(`vm1/`; delete it when done). Read-only git on the shared tree (it carries other lanes' uncommitted S0-01 edits — none in your scope);
every mutant on scratch copies; every pytest run with an explicit `--basetemp`; kill only what you start, PID-targeted; never
background a run and stop; no outward actions; NO network call except loopback test servers you start yourself; NO cargo build in the
sandbox; never read, print or commit a credential (the honeytokens in `proofs/S0-06/fixtures/honeytokens.json` are synthetic canaries
by design — the bearer token of a real instance is the one secret, and none exists in the sandbox). Interpreter
`/root/venv-agent-factory/bin/python`.

**The ONE bridge action you MAY take:** the pytest-only PC gate `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_06_four_scope.py`
from a clean detached worktree of the PIN, then `wait <RUN_ID>`. Nothing else on the bridge — NEVER run `run_s0_06_legs.sh`,
`start_ai_memory.sh` or anything that clones, builds or starts ai-memory on the PC.

**Inputs (read in this order):** the lane brief `tasks/briefs/s0-06-m1-four-scope-adapter-real-ai-memory-checker-pc-legs.md` (the
contract: Design 1-8) · the lane's report `tasks/briefs/s0-06-support/M1-report.md` (the seams read from source with file:line, the
four self-found defects, 28 mutants over 19 REASONS rows, discrepancies D-1..D-6, NOT-done 1-7, the self-attack A/B/C) · the material
pack `tasks/briefs/stage0-parallel-support/material-S0-06.md` (the seed block `seeds/seed-stage0-v1.yaml:442-459`, docs/03 §4 read
contracts 1-6 and the write contract, docs/04 §2-§6, BOTH ADR 0003 files, the safe-posture env) · the pinned ai-memory source
`/home/user/nerdherderdani/ai-memory` (commit 73715b6f, READ-ONLY): `crates/ai-memory-web/src/routes/api.rs` (the search route
:41-45, the scoped mode :352-405, `ApiSearchHit` :1254-1263), `crates/ai-memory-store/src/reader.rs:1174-1185` (`PageSummary`),
`crates/ai-memory-mcp/src/admin.rs:636,6332-6374` (`/admin/write-page`), `crates/ai-memory-store/src/scope.rs:231-292` (the reserved
scope), `crates/ai-memory-core/src/actor.rs`, `crates/ai-memory-cli/src/config.rs:702,812,937` (the posture default and env nesting)
· `docs/INCIDENT-LOG.md` (AF-AP-35, AF-AP-39, AF-AP-40, AF-AP-42, AF-AP-52, AF-AP-58, AF-AP-59) · `proofs/S0-07/` and `proofs/S0-11/`
as the spec exemplars · `scripts/proof-runner` + `scripts/validate-ledger` (the mint path: exit 2 = Deferred, nothing minted).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-06-support/M1-report.md --rev 380877b` (the report's short names resolve without a map;
add `--map` only for the ai-memory citations you check) — MISS 0 or a finding; `ap_screen.py proofs/S0-06 proofs/S0-06/adapter
proofs/S0-06/tools/pc` (AP-32, AP-51) and `--tests tests/test_s0_06_four_scope.py` (AF-AP-34 ×2, AF-AP-35 ×2) — each classified by
RUNNING it, not by reading the lane's classification.

## Items
1. **The authorization boundary (`authorize`, `factory_memory.py:123`).** The tuple must match a `bindings.json` row VERBATIM. Attack
   with: an extra field, a missing field, JSON `null` (the lane's fixed fail-open — confirm the red control is red on the PRE-fix code
   by reverting the guard on a scratch copy), case variants, a trailing space, a Unicode homoglyph in the agent id, a list-valued
   field, a row with an extra key, two identical rows, a tuple that is a real binding for a DIFFERENT actor. Then the channel question:
   is there ANY path by which the request body, the query, the record, the environment or a CLI flag reaches `authorize`? Prove it by
   reading every call site and by a mutant that plants an authorization hint in the record. Where is `bindings.json` resolved from —
   a path relative to the module, a symlink, a directory in its place (S_ISREG)?
2. **The merge (`merge`, `factory_memory.py:170`).** Determinism is proven over synthetic records; attack the DOMAIN: two records with
   the same path inside ONE scope; a record missing `path`/`stable_id`; a `rank` of `NaN`, `-0.0`, `inf` (Python's `json.dumps`
   emits `NaN`/`Infinity` — not JSON — and `sort_keys` cannot order them: is that a byte-identity wormhole for the `nondet` row?);
   ties in `(precedence rank, stable id)`; a scope name outside the four. Does `shadowed_scopes` record EVERY shadowed scope or the
   first? Is the dedup key (the page path) what docs/03 §4 calls the stable ID, and is the identity key COVERING the attribute that
   changes across scopes (title, body)? Write the mutant that makes two scopes' records collide on path with different bodies and read
   what the winner carries.
3. **The checker's substrate identity (`check_substrate`, `check_four_scope.py:128`).** The commit comes from `upstream.lock.yaml` —
   how is the lock parsed (regex, yaml?), what if the lock carries two ai-memory entries or the key moves? The version literal `1.39.0`
   — pinned where, and does the lock carry a version to compare against? **`binary_sha256` is checked as 64-hex: is it compared to
   anything?** If any 64-hex digest passes, the "identity" is a FORMAT check, not an identity — say so as a finding (class: a format
   check standing in for an identity check) and state what a real comparison would need (a digest recorded by the spike, by the PC
   build, or nothing yet — be exact). The four posture variables: exact-value equality or presence (AF-AP-40)?
4. **The four assertions, two instruments each.** For every REASONS row, reproduce ONE lane mutant (paste the killer line) and add
   yours: `precedence` — four distinct titles but the same body; the collision id present in four raw reads but the merged winner
   from a fifth scope; `write` — present in `agent--A` exactly once but with content that is NOT the written record (does the checker
   compare content, or only the path?); a raw listing that carries the path twice with different `updated_at`; `leak` — the token
   inside a DIFFERENT record's field of the recall; the token present in the recall of the leg whose binding IS authorized for that
   scope; an EMPTY recall with an authorized token absent (M24) — and an empty recall whose status is `ok`; `denied` — an event
   spelled `http-request` / `HTTP_REQUEST` / a nested `{"event": "http_request"}`; an EMPTY event stream (zero events: does "no
   requests" pass trivially, or is the `scope_tuple_denied` event REQUIRED?); events written to a sibling file the checker never reads.
5. **The record shapes (AF-AP-42).** Re-derive `SEARCH_HIT_KEYS` and `PAGE_SUMMARY_KEYS` by `sed -n` on `api.rs:1254-1263` and
   `reader.rs:1174-1185`; confirm the committed bundles and the recording server carry EXACTLY those sets; then the semantics the lane
   admits it never saw: `rank` (f64 — sign? range?), `updated_at` (which timestamp format does the store emit — cite the serializer),
   `snippet` vs the page body (does the leak check read the snippet only, and can a token sit past the snippet window?). D-4: the
   timestamp comes from a SECOND GET (the page listing) — a consistency window between the search and the listing: can `recall-1`
   and `recall-2` differ in `updated_at` on a live substrate without any write? If yes, the `nondet` row is a false red waiting to
   happen on the PC — say what the checker should compare (the record minus the volatile field, or a listing taken once).
6. **The negative controls.** The three spec negatives reproduce their pinned `failure_reason` EXACTLY on the PIN (run the spec's
   own commands); the seed's literal path `fixtures/s0-06/neg-unauthorized-tuple.json`; the tuple has exactly ONE wrong field (which,
   and is `t-platform` really bound to `a-gamma` in `bindings.json`); the denial makes no network call (a closed loopback port, a port
   that ACCEPTS and hangs — is the denial still before the connect?).
7. **The PC runner — READ, never run** (`proofs/S0-06/tools/pc/`): the port preflight refuses (`exit 65`); the token 0600 and never
   echoed — trace every place it is read (curl `--config`, `seed_scopes.py`, `collect_leg.sh`) and grep the scripts for any `set -x`,
   `echo`, `printf` or log line that could carry it; **the run dir is KEPT after the run with the token inside** — is that an
   acceptable residue on the owner's PC or a finding (shred on exit, keep only `serve.log`)?; the readiness wait exits on the child
   dying (68) and on timeout (69); the stop path reads its OWN pidfile and confirms `/proc/$pid/exe` — is the check done under
   `set -u` with the pidfile absent (AF-AP-58)?; `cargo +1.95.0` — does the pinned checkout's `rust-toolchain.toml` (D-5: it IS
   tracked, `channel = "1.95"`) make the override redundant or conflicting?; `seed_scopes.py` imports NOTHING from the adapter (assert
   by AST, not by grep); every external command enumerated by the lane — one it missed = a finding; the posture variables are
   EXPORTED to the instance (not only asserted afterwards).
8. **The claims boundary.** Grep the adapter, the spec, the report, the ledger row (`todo/BUILD-TASKLIST.md` `s0-13-s0-06-four-scope`)
   and `STATUS.md` for any claim of Fubuki bounds, a token budget, `memory_required`, a live substrate or a minted result: read
   contract 5 and the pre-dispatch check are NOT built and nothing minted — a claim otherwise is a hollow green in prose.
9. **The 18-class preflight** the lane ran — re-scan the 12 code/test files; a class the lane missed = a finding; the lane's
   class-6 rows (PC-only env domains `S0_06_SRC`, `S0_06_TOOLCHAIN`, the scope ids in `run_s0_06_legs.sh:24-27`) — what does a
   wrong VALUE do (a typo'd scope id seeds the wrong scope and the checker greens on it?).
10. **The PC gate (the carve-out)**; paste beside the checkpoint's `95 passed in 3.11s`; agree.
11. **Mutants ≥ 40** (the lane's 28 + yours from items 1-4: any-64-hex digest, NaN rank, same-body distinct titles, the write-leg
    content mismatch, `http-request` spelling, the empty event stream, the token in another field, a bindings row with an extra key,
    the snippet-window token, a posture value with trailing whitespace).
12. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census (every loopback server
    you start, killed by pid).
13. **The design.** D-2: the two accepted ADR 0003 files — state, from the seed and docs/03, which one the Stage 0 contract binds, and
    exactly what comes OUT of this proof if the owner picks the two-scope ADR (files, rows, legs). D-3: is addressing Company as an
    ordinary `_global` project in the `factory` workspace a naming hazard worth a rename (`company--factory`?) — keep it to the
    consequences you can cite in source. Is the adapter's own event stream an adequate "no request was made" instrument given
    ai-memory's audit log covers mutations only (the lane's §1.3 argument) — or must the PC leg add a second instrument (the
    instance's access log, a loopback packet count)? Keep it to what you measured.

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-M1.md` — draft after EACH item — then return it whole. Findings: ALL, no severity
filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact red test, SOLID/UNSURE;
reproduced vs reviewed vs skipped; shared-tree hygiene; verdict MERGE-READY or NOT-READY with the blocking set, the cheapest path, and
the exact PC steps for the coordinator's live leg (what `run_s0_06_legs.sh` needs before it may run on the owner's PC).
