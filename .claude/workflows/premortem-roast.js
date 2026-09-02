// premortem-roast — reusable adversarial pre-mortem / roast swarm.
//
// Parallel auditors each hunt one dimension for fakes / stubs / dead wiring /
// hollow greens / honesty holes / profit blockers, then a synthesis judge
// dedups + ranks into ONE ledger with a build order. Distilled from the
// premortem-roast (56-defect) and premortem-2 (R2, 32-finding) runs.
//
// Invoke:  Workflow({ name: 'premortem-roast', args: { ... } })
// args (all optional):
//   scope           — what's under audit (default: the whole system)
//   repo            — backend repo path (default /home/user/trading-system)
//   frontend        — frontend src path to also roast (optional)
//   known           — known gaps to NOT re-report as-is (find specifics beneath them)
//   extra_dimensions— [{key, prompt}] run-specific lenses appended to the defaults
//   dimensions      — [{key, prompt}] REPLACE the default lens set entirely
//   model           — agent model (default 'opus' = Opus 5; owner ruling 2026-07-28: verify/roast lanes run on Opus 5)
//   ledger_prefix   — id prefix for synthesized findings (default 'FIND')
export const meta = {
  name: 'premortem-roast',
  description: 'Adversarial pre-mortem / roast swarm — hunt every fake, stub, dead-wire, hollow-green and profit blocker, then rank into one ledger',
  phases: [
    { title: 'Audit', detail: 'parallel auditors, one dimension each' },
    { title: 'Synthesize', detail: 'dedup + rank into one ledger + build order' },
  ],
}

const A = (typeof args === 'object' && args) ? args : {}
const REPO = A.repo || '/home/user/trading-system'
const SCOPE = A.scope || 'the whole crypto GA trading system (backend + flywheel + dashboard)'
const FRONTEND = A.frontend || ''
const KNOWN = A.known || ''
const MODEL = A.model || 'opus'
const PREFIX = A.ledger_prefix || 'FIND'

const FINDINGS = {
  type: 'object', required: ['findings'],
  properties: { findings: { type: 'array', items: {
    type: 'object', required: ['id', 'file', 'summary', 'severity', 'category'],
    properties: {
      id: { type: 'string' }, file: { type: 'string' }, line: { type: 'number' },
      summary: { type: 'string' }, severity: { type: 'string', enum: ['P0','P1','P2','P3'] },
      category: { type: 'string' }, evidence: { type: 'string' }, fix: { type: 'string' },
    } } } },
}

const COMMON = `You are ONE auditor in an adversarial pre-mortem swarm over ${SCOPE}. Backend repo: ${REPO}.${FRONTEND ? ` Frontend src: ${FRONTEND}.` : ''} The owner's goal is PROFIT — a production system, not a demo. Distrust everything: a green test is the most practiced liar; docs/comments/status lines flatter the system. Every claim needs file:line evidence you ACTUALLY READ (read-only probes OK). Name a concrete fix. Severity: P0 = blocks profit/correctness or a compliance/safety violation, P1 = major gap, P2 = quality, P3 = polish. Hunt specifically for: stubs/hardcoded values/no-ops presented as real; dead wiring (a producer with no consumer, or a knob/gene/param decoded but never read); hollow greens (a pass produced without the capability actually running — apply the kill-switch question: what's the cheapest way this passed WITHOUT the real thing running?); silent fail-soft that should be fail-loud; honesty holes (UI/status/doc claiming a capability that isn't there). Return up to 8 findings.${KNOWN ? `\n\nKNOWN (do NOT re-report as-is — find the SPECIFICS beneath them): ${KNOWN}` : ''}`

const DEFAULT_DIMS = [
  { key: 'fakes-stubs', prompt: `${COMMON} DIMENSION: fakes / stubs / hardcoded values / shortcuts presented as real across the core spine. Every canned number, tautological check, no-op fallback, or "get past the blocker" shortcut.` },
  { key: 'dead-wiring', prompt: `${COMMON} DIMENSION: DEAD WIRING. Producers with no consumer, consumers with no producer, queues nobody drains, and especially KNOBS/GENES/PARAMS that are decoded/declared but never actually read (grep each config/gene name for consumers outside its declaration/decode site — zero consumers = a dead knob). Dead knobs are why tuning does nothing.` },
  { key: 'correctness-hollow-green', prompt: `${COMMON} DIMENSION: correctness bugs + hollow greens in the value-producing spine. Any path that emits a result/PnL/verdict WITHOUT the real pipeline running. Swallowed exceptions hiding real bugs. Identity bugs (wrong entity served but "something" came back).` },
  { key: 'data-integrity', prompt: `${COMMON} DIMENSION: data & feature integrity. Stale/frozen data, silent row loss, serialization corruption, and — critically — whether the thing that TRAINS/optimizes sees the SAME data/features as the thing that VALIDATES/executes (a divergence = a silent correctness hole).` },
  { key: 'honesty-ux', prompt: `${COMMON} DIMENSION: honesty of the surfaces (dashboard/API/status/docs). Numbers that read as real but aren't, statuses that show "running/healthy" while the thing idles, results collapsed into a misleading label, capabilities claimed that aren't built. State the "user sees X, reality is Y".` },
  { key: 'safety-compliance', prompt: `${COMMON} DIMENSION: safety/compliance invariants (interface level, NOT exploit code). Verify each holds or is VIOLATED with file:line: value-producing constraints enforced in CODE not comments; fail-closed gates on the candidate LIST not just the winner; secrets never written to a committed file/log/telemetry; any domain rule (e.g. spot-only/no-shorts/no-leverage) actually enforced by the evaluator, not assumed.` },
  { key: 'test-rigor', prompt: `${COMMON} DIMENSION: are the tests real or hollow? Missing negative controls, tautologies, "not-None" assertions instead of identity/state assertions, fixtures that can't carry the PRODUCTION data type (so they can't exhibit the real bug), hermeticity bypasses. Name a specific surviving mutant for any test you call hollow.` },
  { key: 'ops-resilience', prompt: `${COMMON} PRE-MORTEM: 6 months later it made $0 because it kept FALLING OVER. Restart-on-crash, boot persistence, queue saturation, memory growth, config/tunnel drift. Verify each in code/deploy reality; name the minimal hardening.` },
  { key: 'telemetry-gaps', prompt: `${COMMON} DIMENSION: telemetry sufficiency. For each decision/branch/abstain/error on the spine: "if this failed in prod tonight, would the trace explain it?" Find still-silent decision paths and the exact emit sites to add. Flag any knob whose liveness can't be confirmed from telemetry.` },
  { key: 'premortem-profit', prompt: `${COMMON} PRE-MORTEM: 6 months later, $0. Work backwards through EVERY gap between "the system decides to act" and "money actually moves (even paper)". Verify each gap in code TODAY and rank by which to close first for the first real dollar.` },
]

let dims = Array.isArray(A.dimensions) && A.dimensions.length ? A.dimensions : DEFAULT_DIMS.slice()
if (Array.isArray(A.extra_dimensions)) dims = dims.concat(A.extra_dimensions)

phase('Audit')
const results = await parallel(dims.map(d => () =>
  agent(d.prompt, { label: `audit:${d.key}`, phase: 'Audit', schema: FINDINGS, model: MODEL })
))

phase('Synthesize')
const all = results.filter(Boolean).flatMap((r, i) => (r.findings || []).map(f => ({ ...f, dim: dims[i].key })))
log(`collected ${all.length} raw findings`)
const synth = await agent(
  `You are the synthesis judge for an adversarial pre-mortem of ${SCOPE}. ${all.length} findings from ${dims.length} auditors (JSON below). Dedup (same root cause -> one entry, keep best file:line evidence). Produce a RANKED ledger: P0 first (profit/correctness/compliance blockers), then P1, P2, P3. For each: id (${PREFIX}-nn), title, root_cause, files, fix_summary, effort (S/M/L), depends_on. ALSO produce build_order: the increment sequence to close the highest-ROI-for-profit issues first. Return via structured output.\n\nFINDINGS:\n${JSON.stringify(all).slice(0, 185000)}`,
  { label: 'synthesize', phase: 'Synthesize', model: MODEL, schema: {
    type: 'object', required: ['ledger', 'build_order'],
    properties: {
      ledger: { type: 'array', items: { type: 'object', required: ['id','title','severity','fix_summary'], properties: {
        id: {type:'string'}, title: {type:'string'}, severity: {type:'string'}, root_cause: {type:'string'},
        files: {type:'array', items:{type:'string'}}, fix_summary: {type:'string'}, effort: {type:'string'},
        depends_on: {type:'array', items:{type:'string'}} } } },
      build_order: { type: 'array', items: { type: 'string' } },
    } } }
)
return { raw_count: all.length, dimensions: dims.length, ledger: synth.ledger, build_order: synth.build_order }
