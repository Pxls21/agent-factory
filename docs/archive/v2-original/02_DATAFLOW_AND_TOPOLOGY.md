# 02 — Dataflow & Topology (v2)

**Version:** 2.0 · **Date:** 2026-09-01

## 1. End-to-end request lifecycle

```
Human ──kind:9 @agent (#h channel, #p agent)──► Buzz relay   [WS :3000; NIP-42 kind 22242]
Buzz relay ──fan-out──────────────────────────► buzz-acp     [NIP-OA owner-only; 1 in-flight/channel]
buzz-acp ──session/new + session/prompt───────► harness      [ACP stdio; BUZZ_PRIVATE_KEY]
harness on_session_start ─────────────────────► Fubuki loader[compile → canonical packet + packet_hash]
   Fubuki reads a BOUNDED memory slice ────────► ai-memory    [scoped /api/v1 read → bounds.py 7-filter]
   packet placed as SYSTEM layer (adapter placement=system, beneath host scaffold)
harness pre_llm_call hook ────────────────────► verify packet_hash  [block on mismatch]
harness ──tool/shell call─────────────────────► CEL gate     [deny-before-allow; audit row FIRST]
   (allowed) ──containerized──────────────────► gVisor runsc [non-root; /workspace only]
harness ──model call──────────────────────────► OmniRoute    [:20128/v1; compression OFF (code lane)]
OmniRoute ────────────────────────────────────► provider     [4-tier fallback; BYO key]
harness output ──gates──► persona_lint (VIOLATION blocks) ─► #sec-ops scan ─► retro gate (green real?)
agent reply ──Buzz CLI send_message───────────► Buzz relay ──► Human   [signed kind:9]
code work ──git push (signed)─────────────────► git-origin    [git events = signed Nostr events]
memory writes ──proposed──────────────────────► ai-memory     [enters as 'proposed'; write path can't self-approve]
PandaProbe (if enabled) ──────────────────────► spans         [byte-invisible]
nightly ──dream phase──► propose→dispose promotion up the scopes (05)
```

**Provenance is the through-line.** A memory record enters as `proposed`; only the deterministic dream-phase pipeline (or a human) transitions it to `approved`. The compiler never sees raw memory — `bounds.py` filters first. Same law in three places: Fubuki's memory model, ai-memory's `require_approval`, and the dream phase.

## 2. The brain hierarchy = ai-memory scopes

```
   Company   =  ai-memory _global scope        (union-read into every query; company rules/heuristics)
      ▲ promote (dream phase, identifiers stripped)
   Team      =  ai-memory workspace            (one per channel: dev-coding, sec-ops, …)
      ▲
   Project   =  ai-memory project              (repo/cwd-keyed; .ai-memory.toml override)
      ▲
   Agent     =  ai-memory operator/actor scope (per-agent token + per_actor auto-scope + _slots)

READ (native, ungated — "pull-down is free"):
   an agent query resolves via ScopeResolver: its project + its operator slots + the _global union,
   with sibling-project/workspace scoping available. Fubuki then applies bounds.py (status→branch→
   identity→audience→temporal→trust→relevance) before anything enters the packet.

WRITE: proposed records append to the closest scope (Agent/Project). Invalidate-don't-delete.

PROMOTE (push-up, gated — the dream phase, 05): Agent→Project→Team→Company, identifiers stripped,
   via ai-memory auto-improve pending-writes + an executable eval-gate + human approval.
```

**Rules.** Company (`_global`) is read-only to agents (only the dream pipeline + a human write there). A Company summary must link to evidence, never overwrite it; a contradiction downgrades it to `uncertain`. Pull-down needs no mechanism; only push-up is gated.

## 3. Fault-containment topology

```
pipeline (within a step)          orchestrator-worker (PROJECT)      hierarchy (COMPANY reads)      blackboard (TEAM = Buzz)
A→B→C→D: fault flows downstream    O→W1/W2/W3 independent evidence    summary can hide findings       false claim spreads via
→ short verified chains only       → fault local unless one premise   → summary links, never          re-reads → contained only
                                     is broadcast to all (forbidden)     overwrites; conflict⇒uncertain   while provenance labels hold
```

| Level | Topology | Fault behavior | Enforced by |
|---|---|---|---|
| Agent | single governed persona | stays in the agent | Fubuki (one hash-pinned packet) |
| Project | orchestrator-worker | local unless a premise is broadcast | independent evidence; no shared premise |
| Team | blackboard (Buzz signed events) | spreads via re-reads; labels contain it | provenance + signed audit log |
| Company | hierarchy reads | summary can shadow findings | summary links to evidence; contradiction⇒uncertain |

## 4. Distillation dataflow (see `05` for the full pipeline)

```
lesson proven / session closes
   │  (model NOMINATES — soft, stochastic)
   ▼
identifier-strip (rule scrub → independent verifier → canary)  ── deterministic
   ▼
persona_lint provenance/style gate  →  retro gate (green survives negative control)
   ▼
ai-memory auto-improve pending-write  →  eval-gate scorer  →  require_approval (human)
   ▼  (pipeline DISPOSES — hard, deterministic)
scoped write UP one level (project→team→company), identifiers stripped
   └── the same stream feeds the anti-pattern registry (#sec-ops corpus)
```

Cross-refs: memory engine internals → `04`; the dream phase → `05`; bounds engine + Fubuki seams → `06`.
