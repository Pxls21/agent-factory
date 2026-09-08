# Lane M1 — S0-06 four-scope adapter design proof: the first-party composite adapter, the tuple/precedence/leak checker over evidence from a REAL pinned ai-memory, the PC leg runner (sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".)

**Why:** S0-06 has nothing built (`proofs/S0-06/` absent, no `fixtures/s0-06/`, ledger ABSENT — `material-S0-06.md` §5.1). Its class is
SETTLED as `execution_proof` by the positive `rust-ai-memory` spike (`spikes/rust-ai-memory/result.json`: ai-memory 1.39.0 at the pinned
commit `73715b6f` builds on the PC with `cargo +1.95.0`; KC-3 falsified the blocked label). The seed block is exact
(`seeds/seed-stage0-v1.yaml:442-459`): four assertions — the auth tuple (actor/agent/team/project) is validated OUTSIDE model control ·
merge precedence Agent→Project→Team→Company with deterministic de-duplication (same input twice ⇒ byte-identical merged output) · writes
land ONLY in the explicitly authorized active scope · a honeytoken staged in one scope NEVER surfaces in another scope's recall — and ONE
negative fixture at the seed's literal path `fixtures/s0-06/neg-unauthorized-tuple.json` ⇒ `denied: scope-tuple-unauthorized`. The
component under proof is the ADAPTER (docs/03 §4: one composite provider `factory_memory` mapping Company `(factory,_global)`, Team
`(factory,team--<id>)`, Project `(factory,project--<id>)`, Agent `(factory,agent--<id>)`) — an authorization boundary over a substrate that
has NO native per-project RBAC (docs/02:67-76, D-007). The evidence comes from a REAL pinned ai-memory instance on the PC; the adapter's
pure logic is proven in the sandbox.
**Inputs (read in this order):** `tasks/briefs/stage0-parallel-support/material-S0-06.md` (whole — §1 the seed, §4 the seams verbatim:
docs/03 §4 read/write contracts, docs/04 §2-§6, docs/01 §6, docs/02 audit facts, BOTH ADR 0003 files, the safe posture env, §6 the spike
facts) · `material-S0-02.md` §5.4 (S0-07/S0-11 spec exemplars — S0-07 drives a REAL pinned checkout by absolute path), §7 (the 18 classes +
mint-wide AF-AP rows) · the pinned ai-memory source at `/home/user/nerdherderdani/ai-memory` (commit 73715b6f, READ-ONLY; starting
points, cite the exact lines you rely on): `crates/ai-memory-web/src/mount.rs:324` (`/api/v1` mounted as the PROTECTED read API — enumerate
its routes and their query parameters for workspace/project), `crates/ai-memory-mcp/src/server.rs:1481-1570` (`write_target_ids`,
`write_target_ids_with_actor`, `search_project` — how a write is scoped and how a read is scoped), the test at `server.rs:6818`
(`write_page_scope_global_lands_in_reserved_scope` — the `_global` reservation), `crates/ai-memory-mcp/src/auth.rs` + `human_auth.rs`
(the token model: `AI_MEMORY_AUTH_TOKEN`, pepper, per-actor keys — what a token CAN and CANNOT scope), `crates/ai-memory-core/src/actor.rs`,
`active_project.rs` (the `(workspace_id, project_id)` model), the record/page serialization types (the REAL record shape every fixture
must carry — AF-AP-42), `docs/deploy.md`, `docs/install.md`, `docs/frontend-api.md`, `docs/mcp-install.md` (how an instance is started
with a data dir, port and token; which surface WRITES — MCP tool or CLI — and which READS) · `.env.example:37-43` (the posture variables) ·
`proofs/schemas/{spec,result}.schema.json` · `scripts/proof-runner` (the mint path) · `scripts/validate-ledger`.
**Scope (all NEW + tests + your report):** `proofs/S0-06/spec.json` · `proofs/S0-06/adapter/factory_memory.py` (the adapter: a library +
a CLI `recall|write` — the component under proof) · `proofs/S0-06/adapter/bindings.json` (the AUTHORIZED tuple table — the "outside model
control" source: loaded from this committed file, never from the request) · `fixtures/s0-06/neg-unauthorized-tuple.json` (the seed's
path, at the REPO ROOT) · `proofs/S0-06/fixtures/{records-precedence.json, honeytokens.json, evidence-leak/, evidence-wrong-scope-write/}`
(committed negative bundles) · `proofs/S0-06/check_four_scope.py` · `proofs/S0-06/tools/pc/{run_s0_06_legs.sh, start_ai_memory.sh,
seed_scopes.py, collect_leg.sh}` (PC-side, NOT run here) · `tests/test_s0_06_four_scope.py` · report `tasks/briefs/s0-06-support/M1-report.md`.
NOT yours: `proofs/registry.yaml`, the ledger, the ADRs, the docs, the seed, anything under other proofs. Shared-tree rules as every lane:
never `git stash/checkout/restore/reset/add/commit/push`; gates from a `git archive <PIN>` copy under
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/m1/ + your files; explicit `--basetemp`; kill only your own
processes by pid; NEVER background a run and stop; no outward actions; NO PC bridge; NO cargo build in the sandbox (618 MB debug binary,
the spike measured it — heavy jobs run on the PC; the sandbox toolchain is 1.94.1 < MSRV 1.95 anyway); never read or print a credential.
Interpreter `/root/venv-agent-factory/bin/python`.

## Design (pinned — build it, do not redesign it)
1. **The adapter is small and every decision is a named reason.** `factory_memory.py`: `Binding(actor, agent, team, project)` validated
   against `bindings.json` (a tuple is authorized iff it appears verbatim; any field missing/extra/wrong ⇒ `denied: scope-tuple-unauthorized`
   BEFORE any network call — the request body is never consulted for authorization, only the caller-supplied tuple + the committed table);
   `scopes_for(binding)` = the four `(workspace, project)` pairs from docs/03 §4 with `workspace = "factory"` fixed; `recall(binding, query)`
   queries every authorized scope through ai-memory's READ surface (cite the route), then `merge(results_by_scope)` — precedence
   Agent→Project→Team→Company, de-duplication by a deterministic key (the record's stable id; a same-content record in two scopes keeps the
   higher-precedence one and RECORDS the shadowed scope in provenance), output sorted by (precedence rank, stable id) — a PURE function of
   its input with NO clock, NO randomness, NO dict-order dependence (assert `merge(x) == merge(x)` byte-for-byte after `json.dumps(sort_keys)`
   and that a shuffled input yields the same bytes); each returned record carries `scope`, `stable_id`, `timestamp`, `confidence`,
   `provenance` (docs/03 §4 read contract 4); `write(binding, active_scope, record)` refuses any `active_scope` not in the binding's four
   (`denied: write-scope-not-active`) and writes to exactly that scope through the WRITE surface (cite: MCP tool or CLI — whichever the
   pinned source exposes without the admin/approve/delete tools; the adapter exposes NO delete/purge/promote — assert structurally: its
   public surface is `recall` and `write` only, tested by `dir()`), idempotent by `(session, turn, event_id)` (a retry with the same key is
   a no-op — record it). Status is explicit: `{"status": "ok"|"degraded"|"denied", "reason": …}`; a scope that errors makes the status
   `degraded` with the scope named, never a silent partial (docs/04 §4). The CLI: `factory_memory.py recall --tuple-file F --query Q
   [--base-url U --token-file T]` / `write --tuple-file F --scope S --record-file R …`; `--token-file` read at call time, value never
   printed (AF-AP-35). Emit one JSON event per decision to stderr (reason field) — the telemetry rule.
2. **The negative control is the adapter refusing, offline.** `fixtures/s0-06/neg-unauthorized-tuple.json` = a tuple whose `team` is not
   bound to that `agent` in `bindings.json` (a REAL-looking tuple, one field wrong — not garbage). `spec.json` negative: `python3
   proofs/S0-06/adapter/factory_memory.py recall --tuple-file fixtures/s0-06/neg-unauthorized-tuple.json --query x` expect exit 1 +
   `failure_reason: denied: scope-tuple-unauthorized` EXACT on stdout's last line; it must make NO network call (test: a closed `--base-url`
   port and the denial arrives first, in bounded time). `required_negative_controls: 1` satisfied by this plus the two committed evidence
   bundles below (list all three).
3. **The checker over PC evidence, two instruments per assertion.** `check_four_scope.py <evidence-root>` reads `substrate.json` (the
   instance's identity: pinned commit, `ai-memory --version` output, binary sha256, the posture env NAMES with their values for the four
   posture keys only, port, data dir) — a bundle whose commit != `upstream.lock.yaml`'s `ai-memory.commit` or whose version != 1.39.0 ⇒
   `substrate: not the pinned ai-memory (<got>)`; posture keys not `require_approval=true, scheduler=false, maintenance=false,
   per_user=false` ⇒ `substrate: unsafe posture <key>=<value>`. Then per leg: `precedence/` — the adapter's `recall.json` run TWICE
   (`recall-1.json`, `recall-2.json`, byte-identical or `merge: nondeterministic`), against a seeded set where the same stable id exists in
   all four scopes with distinguishable bodies ⇒ the merged record is the AGENT one and provenance lists the three shadowed scopes; the
   second instrument `raw-<scope>.json` = the direct `/api/v1` read of each of the four projects (bypassing the adapter) proving the four
   variants really exist in the substrate. `write-scope/` — the adapter wrote as agent A into `agent--A`; `raw-*.json` for ALL four projects
   show the record in `agent--A` ONLY (`write: record found in <scope>` otherwise) and the idempotent retry produced ONE record. `leak/` —
   honeytokens `HT-<scope>-<hex>` staged directly (seed_scopes.py, the raw write surface) in all four scopes; a binding authorized for
   Agent+Project only recalls ⇒ `recall.json` carries NO `HT-team-*`/`HT-company-*` (`leak: honeytoken <t> surfaced from <scope>`), while
   `raw-team.json`/`raw-company.json` DO carry theirs (else the leak test is vacuous: `leak: honeytoken absent from its own scope` — the
   oracle self-test, AF-AP-52). `denied/` — the unauthorized tuple's `recall.json` = the denial and the substrate access log (if the instance
   logs requests — cite; else the adapter's own event stream) shows NO request for that leg. Absent root ⇒ `deferred: S0-06 evidence not
   captured` exit 2; S_ISREG rule on every read; reasons EXACT strings from one `REASONS` table; PASS line `PASS: S0-06 four-scope - 4/4
   assertions, substrate ai-memory 1.39.0@73715b6f`.
4. **Committed negative bundles** `fixtures/evidence-leak/` (a `HT-team-*` token inside `recall.json` for the Agent+Project binding) ⇒ the
   leak reason; `fixtures/evidence-wrong-scope-write/` (the written record present in `project--P` too) ⇒ the write reason. Record shapes =
   the REAL ai-memory serialization (cite the struct/JSON shape file:line; a `PROVENANCE.md` per bundle says which fields are verbatim from
   the source and which are synthetic values — AF-AP-42).
5. **The PC runner (NOT run here)** `tools/pc/run_s0_06_legs.sh`: `start_ai_memory.sh` clones the pinned commit into `~/s0-06-pinned/ai-memory`
   (idempotent), `cargo +1.95.0 build --release` for the server binary (cite which bin), starts ONE instance on a free loopback port with a
   fresh temp data dir, the posture env from docs/04 §6, and a token generated for the run (0600 file, never printed) — its OWN process,
   killed by pid at the end; NEVER touches the owner's services. `seed_scopes.py` creates the four projects and the seed records/honeytokens
   through the raw write surface; the legs run the adapter CLI; `collect_leg.sh` writes the bundle with `substrate.json` first. `bash -n`
   clean; every external command listed in the report; the runner's own preflight refuses to run if the port is already bound (the owner's
   box: no port squats — AF-AP-33 in reverse).
6. **Tests** (`tests/test_s0_06_four_scope.py`): tuple validation (every single-field corruption of an authorized tuple ⇒ denied; the
   authorized set accepted; the table is the only source — a tuple present in the request but absent from the table is denied); merge
   determinism (twice byte-identical; shuffled input identical; the precedence order on a four-way collision; dedup keeps provenance;
   sorted output); the write-scope refusal and the idempotent key; the public surface has no delete/purge/promote; the checker over a
   synthetic PASSING bundle built by the test from the committed shapes + the two negative bundles ⇒ exact reasons; every REASONS row
   reachable by one mutant (substrate commit, version, posture, nondeterminism, shadowed provenance, wrong-scope write, leak, the vacuous
   leak oracle); FIFO/directory reads; `deferred:`; the offline negative control makes no network call (closed port + timing bound);
   `spec.json` validates; the seed-path fixture exists at the repo root. The adapter's HTTP client is exercised in tests ONLY against a
   local recording `http.server` on 127.0.0.1 that answers with REAL ai-memory response shapes (copied from the source, cited) — this
   proves what the adapter SENDS (route, project, token header) and is NOT proof evidence: the checker refuses any bundle without a real
   `substrate.json` (item 3), so a recorded-server bundle cannot mint. Preflight the 18 classes over your files before the report.
7. **The ADR conflict — record, do not resolve.** Two accepted ADRs carry the number 0003 with contradicting decisions (`material-S0-06.md`
   §4.10). The seed (the contract), docs/03 §4, docs/01 §6, docs/04 §2 and D-006 all say FOUR scopes; `spec.json` cites
   `docs/adr/0003-four-logical-memory-scopes.md` + D-006. Your report's DISCREPANCIES section quotes both ADR headers and states the
   proof follows the seed; the owner decides the ADR file's fate (the coordinator surfaces it).
8. **Report discipline** as every lane: `report_lint.py` MISS 0 (`--map A=proofs/S0-06/adapter/factory_memory.py --map
   C=proofs/S0-06/check_four_scope.py --map T=tests/test_s0_06_four_scope.py`), ap_screen classified (`python3 scripts/ap_screen.py
   proofs/S0-06` and `--tests`), file:line by grep on the FINAL bytes, counts pasted twice (`bash scripts/test_summary.sh
   tests/test_s0_06_four_scope.py`), pyflakes + `bash -n`, the process census, the `NOT run here` list (every PC leg, the cargo build),
   the DISCREPANCIES section (the ADRs; the seed's `Execution proofs are exactly …` list omitting S0-06; anything the source contradicts —
   e.g. if ai-memory's read surface cannot address a project without a session/active-project dance, say exactly what the adapter had to do).
