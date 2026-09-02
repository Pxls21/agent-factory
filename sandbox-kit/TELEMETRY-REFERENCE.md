# Telemetry — NO BLACK BOX (extracted from CLAUDE.md)

Full telemetry rules and framework reference for agent-distiller.
CLAUDE.md carries a compressed summary; read this file for the complete specification.

---

This is a novel, unproven system: its components are individually well-backed but can fail under pressure in
ways we can't predict. The ONLY way we find out *when* and *how* is if everything is recorded. Treat the
codebase like a PLC — every state, decision, and transition must be externally observable. **When you start a
workflow / build anything, telemetry is not optional. If omitting a trace anywhere would create a black box,
don't omit it.**

## The Framework

`obs/trace.py`, byte-invisible human plane — never touches the committed projection, so
adding it needs no golden re-baseline:
- **Spans:** `with stage("name") as span:` for a cascade stage; `stage_event(current_span(), "name", **detail)`
  for a point-in-time event. Both are zero-cost no-ops outside a `recording(...)`.
- **Attributes:** `set_attrs(span, ...)` (committed, allow-listed) · `human_attr` / `llm_io` (human plane).
- **Session context — ALWAYS attach it.** `recording(input_hash, session_id=..., metadata={...})` (and
  `session_context(...)` to add mid-run) stamps **`session.id`** + **custom `metadata`** (JSON + flattened
  `metadata.<k>`) onto EVERY span — this is what makes Phoenix grouping / filtering / **annotation** work.
  **This is a SINGLE-USER local system (you, at the Hermes CLI), so `user.id` is dead weight — skip it.** The
  vital IDs are ARCHITECTURAL — track *which iteration of the system ran*, not who ran it:
  - **`hermes.session_id` / `session_id`** — the CLI task/run id; ties a whole multi-step task's steps into
    one Phoenix session (the Hermes front door passes it; `recording(session_id=...)`).
  - **`distiller.workflow_id`** — which compiled workflow served (group by it to see per-shortcut run-count /
    cost-saved / error-rate). Stamped on the solve root span from `Result.row_id`.
  - **`distiller.mode`** — `"interrupted"` when the deterministic spine short-circuited the model (tier-0
    replay / graft / heal — the reuse win) vs `"standard"` (tier-2 compile — the model ran) vs `"park"`.
  - plus any **`metadata`** worth filtering by: `dataset`, `tenant`, `request_id`, model, knob-vector.
  A `user.id` param still exists in the framework (generic OpenInference) but is unused here by design.
  Never leave a real request without its session_id + architectural metadata — a trace you can't group by
  workflow or filter by mode is half-useless for annotation later.

## The Rules (apply to EVERY new code path)

1. **Every decision, branch, hand-off, abstain, skip, retry, early-return, and error emits a span or event
   carrying the REASON** (not just that it happened — *why*). A silent decision path is a defect, full stop.
2. **No shallow spans.** A span with no useful attributes tells you nothing — stamp the inputs, the outcome,
   and the discriminating detail (score / verdict / reason / counts).
3. **Custom metadata, user IDs, and session IDs go on the span context**, via `recording(...)` /
   `session_context(...)` — not buried in a log line. This is the annotation substrate.
4. **It stays byte-invisible.** Human-plane keys are unprefixed (`session.id`, `user.id`, `metadata*`) or
   span *events* — the committed exporter reads only `obs.*` + `attr.*`, so rich telemetry never changes
   committed bytes and never forces a frozen-golden re-baseline. Prove it with an immunity test when in doubt.
5. **After building any subsystem, do a telemetry pass** (a swarm/workflow audit for anything wide): find
   every path that is missing, shallow, or lacks session/architectural IDs/metadata, and fill it. Verify the
   LIVE stream (spy on `stage_event` under a real run) — presence in source is not proof it fires.
6. **Enrich by ID type, not just "add a span."** Every ENTITY that flows (episode, skill, workflow, gate,
   cell, lineage, task_spec, verdict, execution, gepa-candidate, recovery, model, dataset, env) needs a
   stable, namespaced ID attribute so you can group/filter/annotate it end-to-end. The canonical taxonomy +
   per-stage stamp table lives in **`docs/TELEMETRY-ENRICHMENT-SPEC.md`** — consult it and keep it current.
   IDs that identify a whole run/entity (session, workflow, cell, lineage) must PROPAGATE down the trace via
   `session_context(...)` / `metadata` so child spans inherit their parents' identity.

## The Standing Loop

**Telemetry is never "done" — it is the debugging substrate:**
- **When ANYTHING goes wrong, analyze the trace/telemetry FIRST** — before guessing, before reading code
  blind. The failure's story should be in the spans (which stage, which decision, which reason, which IDs).
- **On every failure, ASSESS telemetry sufficiency.** Ask: "does the trace tell me *exactly* where and why
  this failed?" If yes, fix the bug. If NO — the trace is silent, shallow, or missing an ID/reason at the
  failure point — that gap is itself a defect: **FIX THE TELEMETRY GAP FIRST (add the missing span/ID/reason),
  then re-run**, so the next failure (or a re-run of this one) is legible. Never ignore a telemetry gap you
  hit while debugging; never debug blind around it.
- This is iterative on purpose: we have a ~80–90% baseline now; as real runs fail, the remaining gaps surface
  exactly where they matter. Close each gap as you hit it, re-run, repeat — the leftover shallow spots get
  dealt with along the way instead of all at once. A failing run should read like a PLC fault code, not a
  mystery.
