# 06 — Governance & Fubuki Seams (v2)

**Version:** 2.0 · **Date:** 2026-09-01 · Fubuki facts are **[H] read from source**.

Two halves: the Fubuki integration (Seams A & B, the bounds engine, `persona_lint`), and the build-discipline gates + remaining open decisions.

---

## Part 1 — Fubuki integration

### Seam A — compile → canonical-JSON packet + hash-pin (LOCKED)

Fubuki compiles a persona package into a byte-identical **canonical-JSON packet** with a `packet_hash`. Governor stays BRAIN (deterministic, never calls a model); the harness is HANDS.

**Canonicalization (`release/hashing.py`):** `json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False)` — keys sorted at every level, no whitespace, UTF-8. **Floats are forbidden** (integers/strings only; `_reject_floats` raises). Reimplementable in any language in ~10 lines.

**Hashes:** `hash_obj(obj) = "sha256:" + sha256(canonical_bytes(obj))`; `hash_file(path) = "sha256:" + sha256(raw bytes)`; strings are line-ending-normalized (CRLF→LF) before hashing packet payloads.

**Packet hash (`compiler/compiler.py`):** the packet dict is assembled in a fixed key set, then `packet["packet_hash"] = "sha256:"+sha256(canonical_bytes(packet_without_packet_hash))`. **Verify** = drop `packet_hash`, re-canonicalize, re-hash, compare. **No wall-clock** enters the packet (`compiled_at` appears only if a `time_override` is injected); timestamps live in audit events. Same package + DB snapshot + adapter + time ⇒ identical packet + hash. Golden anchor: `examples/expected-packet.json` (`packet_hash sha256:66fbb461…`).

**Injection (from the code):** the adapter emits `adapter_notes` with `placement=system` and "host may inject its own system scaffold; persona packet is layered beneath it." So the loader (`08` Adapter A) writes the compiled packet as the **system layer** of the harness session, and a `pre_llm_call` hook recomputes `sha256_prefixed(canonical_bytes(packet_without_hash))` and **blocks the call on mismatch**. Belt-and-suspenders: verify at the loader and at the hook.

**Packet keys (schema `fubuki-compiled-packet/0.1`):** `packet_schema, package_id, core_hash, package_hash, adapter, adapter_notes, mode, register, state, resident_kernel, mode_manifest, bounded_context, selected_examples, output_contract, hard_constraints, memory_cutoff, source_pointers, packet_hash` (+ optional `compiled_at`). `register ∈ {conversational, deliverable}`; `output_contract` = {register, screenshot_safe, snark_allowed, canon_references_allowed, humor_allowed}.

### Seam B — the continuity split (LOCKED, corrected)

Reading `migrations/0001_initial.sql` + `0002_preferences_permissions.sql` shows Fubuki's SQLite holds **two kinds of tables**, and only one moves to ai-memory:

- **Governance ledger — STAYS in Fubuki (first-party, deterministic):** `persona_packages`, `package_files`, `branches`, `releases` (+ `rollback_release_id`, `certification`), `sessions`, `runtime_states`, `audit_events` (`sensitivity` default `metadata`), `artifacts`. This is the release registry / rollback chain / state engine / metadata-only audit — the governor's spine. **ai-memory never touches these.**
- **Memory layer — REPLACED by forked ai-memory:** `memory_records`, `memory_links`, `preferences`, `permissions`.

`memory_records` columns (the overlay target, `04` §2): `id, type, claim, status(default 'pending'/proposed), provenance_class, branch, confidence, evidence_pointer, sensitivity(default normal), validity_json{not_before,not_after}, payload_json{influence}, created_at`. `preferences`: `claim, domain, scope, confidence, explicitness, reinforcement_json, decay_json, validity_json, influence_json{text,tool_parameters}`. `permissions`: `action_class, scope_json, confirmation_policy(default always), issuer, validity_json, revoked_at`.

So Seam B = "ai-memory becomes the store for the memory/preference/permission layer; Fubuki keeps its governance ledger." The Fubuki→ai-memory bounded-read adapter (`08` Adapter B) maps ai-memory pages to `MemoryRecord`s and runs the bounds engine.

### The bounds engine (`memory/bounds.py`) — stays in Fubuki

A pure, deterministic **default-deny** filter that runs **before** compilation (the compiler never sees raw memory). Seven filters, reasons always recorded:
1. **Status** — only `approved` records load (proposed/rejected/expired/superseded → blocked).
2. **Branch** — `record.branch ∈ {request.branch, "shared"}`.
3. **Identity** — non-`normal` sensitivity is operator-only.
4. **Audience** — `restricted` never leaves the operator channel; `sensitive` never enters third-party-visible output.
5. **Temporal** — `validity.not_before/not_after` vs injected time (ISO-8601 lexical compare).
6. **Trust** — `inferred` + `low` confidence never loads.
7. **Relevance** — if the request carries tags, the record must intersect them (no tags ⇒ no match; default deny).

Influence is granted at the lowest sufficient level (`none` / `text` / `tool_parameters`); `tool_parameters` only for `operator_stated`/`operator_confirmed`. `confirmation_required` when sensitive / imported / inferred / tool_parameters. This is Fubuki's contribution to the read path and stays first-party.

### `persona_lint` (`lint/persona_lint.py`) — a first-party output/promotion gate

Deterministic linter, two tiers: **VIOLATION** (blocks ship) and **REVIEW** (human-adjudicated). Checks: corporate-filler, closing-filler, em-dash, warmth-stack, persona-banned-tokens (from the package's `banned_tokens.txt`), register-bleed (deliverable register). Exit `0` clean / `1` violations / `2` review-only. Drops directly into the dream-phase gate (`05` step ③) and the output gate (`02`). Its rationale, verbatim: "in-head style enforcement fails… the gate catches what instruction cannot."

## Part 2 — Build-discipline gates

Encode these as first-party deterministic gates the factory runs on its own agents.

- **§0 No hollow greens.** "Verified"/"done"/"passing" is banned in agent output unless a command and its output back it up; a commit-lint enforces it. (`persona_lint` is the style/vocabulary arm; this is the evidence arm.)
- **§2 De-vacuoused negative controls.** Every capability claim must survive a check constructed to fail if the work were fake/vacuous. The retro gate = independent oracle + negative control.
- **§5 Anti-pattern registry.** Every real failure → append-only entry; = distillation source + #sec-ops corpus; drives the self-heal loop (`05`).
- **§6 Continuity authority.** git-origin > KB wiki > task ledger.
- **Gates block, don't ask.** A failed gate stops the pipeline.
- **Roles can't grade their own work.** The producer never runs its own verifier (independent verifier).
- **Self-test suite.** Violate each rule on purpose; assert the gate fires. If a deliberate violation can't trip the gate, the gate isn't real.
- **Human-gated merge.** No agent auto-merges to a protected brain/branch.

## Part 3 — Open decisions (most now resolved)

| ID | Decision | Status |
|---|---|---|
| D1 | HarnessRouter in/out (Pi ACP?) | **RESOLVED** — Pi is ACP via community adapter; HarnessRouter → Phase 2; no shim in v1. |
| D2 | Fubuki inner schema / seams | **RESOLVED** — read from source; Seams A & B locked (this doc). |
| D7 | Tiering | **RESOLVED** — hybrid (shared store + dedicated instance for sensitive agents). |
| D8 | Adopt vs fork ai-memory | **RESOLVED** — fork-and-extend. |
| D3 | Buzz-Desktop runtime for privileged agents | Open — recommend **forbid** (auto-approves permissions); gVisor mandatory regardless. |
| D4 | Confirm NIP-OA revocation/rotation semantics | Open — verify from `buzz-acp` before trusting chain-of-custody at scale. |
| D5 | Hermes license | Open — confirm before imaging Hermes. |
| D6 | PandaProbe judge egress (via OmniRoute vs local) | Open — decide per telemetry policy; keep gate-critical judging deterministic. |
| D9 | ai-memory eval-gate can host an external scorer as a hard pre-write gate? | Open — verify `[auto_improve.eval] command=` blocks the write on failure; if not, patch `ai-memory-consolidate` (`04` §7). |
| D10 | Dream mechanism source | Open — pick from your dream repos; slot into `05` ①/④ only. |

Minor verifications to fold in while building: exact ai-memory `pages` migration columns; the full `kind.rs` integer list; ast-grep/comby wrapper details.
