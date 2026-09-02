# 08 — Adapters & Seams (the glue to build) (v2)

**Version:** 2.0 · **Date:** 2026-09-01

The first-party pieces no existing repo provides. Build in the order of `09_BUILD_PLAN.md`.

---

## Adapter A — Fubuki loader + hash-pin (Seam A) — REQUIRED
Injects the compiled canonical packet into the harness session and pins the hash.
```
load_packet(pkg, compile_request) -> {packet: json, packet_hash: str}
   run: python3 -m fubuki_os --json compile <compile_request> --package <pkg>
inject(session, packet):
   write `packet` as the SYSTEM layer of the harness session (adapter placement=system; beneath host scaffold)
verify hook (Hermes pre_llm_call, and at the loader):
   h = "sha256:" + sha256(canonical_bytes(packet_without_"packet_hash"))   # sort_keys, separators (",",":"), no floats, utf-8
   if h != packet.packet_hash: return {"action":"block","message":"fubuki packet hash mismatch"}
```
Deterministic, hermetic, first-party. Canonicalization is the ~10-line function from `release/hashing.py`.

## Adapter B — Fubuki → ai-memory bounded read (Seam B) — REQUIRED
Feeds the packet's `bounded_context` without letting the compiler see raw memory.
```
bounded_slice(scope, request_ctx) -> list[dict]:
   pages = ai_memory.GET /api/v1/.../search|briefing (scoped to agent/project; _global union)   # bearer auth
   records = [map_page_to_MemoryRecord(p) for p in pages]    # overlay fields: status/provenance_class/confidence/
                                                             #   branch/sensitivity/validity/evidence_pointer/tags
   allowed, rejected = fubuki.memory.bounds.evaluate_records(records, branch, active_person,
                                                             third_party_visible, request_tags, at=time_override)
   return [r.payload for r in allowed]     # rejected reasons go to the selection trace
```
ai-memory is the store; Fubuki's `bounds.py` is the 7-filter gate (`06`).

## Adapter C — Dream-phase distiller (companion crate) — REQUIRED
The gated upward-promotion pipeline (`05`), built as an ai-memory **companion** (calls HTTP/MCP; like `companions/ai-memory-importer`).
```
distill(scope_from, scope_to):
   for proposal in ai_memory.pending_or_nominated(scope_from):
       stripped = identifier_strip(proposal)            # rule scrub → independent verifier
       if canary_survives(stripped): reject(); continue
       if persona_lint(stripped).violations: reject(); continue      # exit 1 blocks
       if not retro_gate(stripped): reject(); continue               # oracle + negative control
       ai_memory.auto_improve.submit(stripped, target=scope_to)      # pending-write
   # eval-gate ([auto_improve.eval] command=this scorer) + require_approval=true finish the dispose
```
Registered as the `[auto_improve.eval] command`. If ai-memory's eval-gate can't hard-block the write, patch the pending-writes→approval transition in `ai-memory-consolidate` (D9).

## Adapter D — First-party CEL policy engine — REQUIRED
Reimplements OpenBot's deny-before-allow / fail-closed / record-before-act (`07`).
```
evaluate(action_ctx) -> ALLOW | DENY | REQUIRE_CONFIRM      # audit row written before return
load_policy(dir) -> compiled_rules                          # compile failure ⇒ refuse (fail-closed)
```
Wire into Hermes `pre_tool_call`, Claude Code PreToolUse, and enforce inside gVisor for Pi.

## Adapter E — Provenance-overlay migration (ai-memory core) — REQUIRED
Additive: add frontmatter + `pages` columns `provenance_class, confidence, branch, sensitivity, valid_from, valid_to, occurred_at, evidence_pointer` (query-needed ones as columns; rest pass-through YAML). Extend the parser/serializer in `ai-memory-wiki`; surface in `/api/v1`. Follow ai-memory's existing additive-migration pattern. Round-trips under `ai-memory reindex`.

## Adapter F — Deterministic codemod wrapper — REQUIRED (dev plane)
```
dry_run_diff(rule_file, files) -> patch        # pin rule; deterministic; no write
apply(patch)                                   # only after the diff passes the gate
route(lang): python|rust|js|… -> ast-grep ;  brace/format-only -> comby   # comby NOT for Python
```

## Adapter G — OmniRoute egress guards — REQUIRED
```
code_lane: compression = OFF (no engines)                 # even with the preservation engine on
byte_echo_canary: send code/URL/JSON fixture through /v1; assert byte-identical (CI + runtime)
model_pin: pin the model on gate-critical turns (no silent fallback swap)
empty_turn_detector: flag long-wait empty responses
```

## Adapter H — Port map + compose — REQUIRED
Resolve the Buzz `:3000` vs HarnessRouter UI `:3000` clash (HarnessRouter is Phase-2; remap its UI to `:3100`). Full map in `09`.

---

| ID | Adapter | Required? | Notes |
|---|---|---|---|
| A | Fubuki loader + hash-pin | **v1** | Seam A, from real source |
| B | Fubuki → ai-memory bounded read | **v1** | Seam B; runs bounds.py |
| C | Dream-phase distiller (companion) | **v1** | gated promotion (`05`) |
| D | First-party CEL engine | **v1** | `07` |
| E | Provenance-overlay migration | **v1** | ai-memory core, additive |
| F | Codemod wrapper | **v1** | dev plane |
| G | OmniRoute egress guards | **v1** | byte integrity |
| H | Port map + compose | **v1** | `:3000` clash |
| — | ACP↔UHP shim | **Phase 2** | only if a UHP-only harness appears (`11`) |
