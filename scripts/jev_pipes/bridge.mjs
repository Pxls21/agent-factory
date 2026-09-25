// P1 replay bridge (task #231): runs the VENDORED jev-pruner's own trimOutput (vendor/jev-pruner/dist, pinned 47d017c
// plus the one local option `minTokensFloor`) on one recorded tool result per stdin line, the way the plugin's tool.call
// handler drives it (vendor/jev-pruner/hooks/fast-jev-output.ts:150-296), and answers one JSON line on stdout.
//
// The chunking, keep rules and rendering are the pruner's (trimOutput). This file holds only the host side: the handler's
// parameter glue (mirrored line by line, cited below) and the transport to the local Laya scorer with the seed's fail-open
// trips. The mirrors are plain JavaScript so the bridge runs on any Node with fetch; tests/test_jev_pipes_replay.py loads
// the vendored TypeScript hook itself (where Node can strip types) and holds every mirrored value and the goal equal to it.
// A job's text lives in memory only; the answer line carries the pruned output for the caller's miss check, never a log.
import { createHash } from 'node:crypto';
import { createInterface } from 'node:readline';
import { pathToFileURL } from 'node:url';
import { buildJevRequest, parseJevResponse, trimOutput } from '../../vendor/jev-pruner/dist/index.js';
import { classifyOutput, exceedsOutputThreshold, looksBinary, looksStructured, recoveryFooter } from '../../vendor/jev-pruner/dist/output.js';
import { classifyInformation, isProtectedLine, keepScore } from '../../vendor/jev-pruner/dist/retention.js';
import { looksSecret } from '../../vendor/jev-pruner/dist/secrets.js';

// hooks/fast-jev-output.ts:18-28 (ARCHIVE_DIR, DEFAULT_MAX_SCORING_REQUESTS, VISIBLE_CHARS_PER_REQUEST, DEFAULTS).
export const HOOK = {
  archiveDir: '.claude/fast-jev-output',
  defaultMaxScoringRequests: 11,
  visibleCharsPerRequest: 192,
  persistedMaxChars: 8_000,
  chunkLines: 20,
  keepThreshold: 0.5,
  maxStateTokens: 25_000,
  model: 'jev-latest',
};
// The P1 floor: the 2,000-character gate is the caller's candidate filter, so the pruner's token floor is lowered to 0
// through the local option (vendor/jev-pruner/PROVENANCE.md). The hook itself floors at 10,000 tokens.
export const FLOOR_TOKENS = 0;
// The local server ignores the bearer (scripts/laya_systemone_server.py:15-16). A fake, never a real key.
const API_KEY = 'FAKE-LOCAL-SCORER-NO-AUTH';

export class FailOpen extends Error {
  constructor(reason) {
    super(`fail-open: ${reason}`);
    this.reason = reason;
  }
}

const now = () => performance.now();
const round = (ms) => Math.round(ms * 10) / 10;

// hooks/fast-jev-output.ts:109-120.
export function goalFromMessages(messages) {
  return messages
    .filter((m) => m.role === 'user' && m.text.trim().length > 0 && (!m.toolResults || m.toolResults.length === 0))
    .slice(-3)
    .map((m) => m.text.slice(0, 500))
    .join('\n');
}

function refused(error) {
  return error?.cause?.code === 'ECONNREFUSED' || error?.code === 'ECONNREFUSED';
}

// The host transport: the hook's jevAsker (hooks/fast-jev-output.ts:95-107: buildJevRequest, fetch, parseJevResponse)
// plus the seed's trips. `tr`: {url, budget_ms, abort_at_budget, enforce_budget, serialize, request_timeout_ms, plan_only}.
// Modes: live = abort at the budget, refuse a second pending request; replay = the same trips, but an in-flight request
// is waited for (never abandoned on the shared server) and its real latency kept; unbudgeted = no budget or queue trip,
// requests one at a time.
function makeAsker(tr, out, t0, sent) {
  let pending = 0;
  let chain = Promise.resolve();
  const trip = (reason, atMs) => {
    if (reason === 'budget' && out.trips.some((t) => t.reason === 'budget')) return; // one budget trip per job
    out.trips.push({ reason, t_ms: round(atMs ?? now() - t0) });
  };

  async function send(state, questions, entry) {
    if (out.trips.length > 0) {
      // the job has already failed open: nothing more goes to the shared scorer
      entry.error = 'after_trip';
      throw new FailOpen(firstTrip(out.trips));
    }
    entry.sent = true;
    pending += 1;
    for (const chunk of state?.chunks ?? []) sent.set(chunk.id, chunk.text);
    // the state the scorer reads BEFORE each chunk (the server appends the chunk last): its length says whether the chunk
    // can fall inside the scorer's first-tokens window at all (the report's truncation check)
    const { chunks: _chunks, ...base } = state ?? {};
    entry.prefix_chars = JSON.stringify(base).length;
    const request = buildJevRequest({ apiKey: API_KEY, model: HOOK.model, baseUrl: tr.url }, state, questions);
    const start = now();
    // AbortSignal.timeout takes an integer: a fractional remaining budget raised RangeError before any request left
    // (caught by test_failopen_budget_live_aborts_at_the_budget)
    const timeout = Math.max(1, Math.ceil(tr.abort_at_budget ? tr.budget_ms - (start - t0) : tr.request_timeout_ms));
    let response;
    let text;
    try {
      response = await fetch(request.url, {
        method: request.method, headers: request.headers, body: request.body, signal: AbortSignal.timeout(timeout),
      });
      text = await response.text();
    } catch (error) {
      entry.latency_ms = round(now() - start);
      entry.error_detail = `${error?.name ?? typeof error}:${error?.cause?.code ?? error?.cause?.name ?? ''}`;
      const reason = error?.name === 'TimeoutError' ? (tr.abort_at_budget ? 'budget' : 'request_timeout')
        : refused(error) ? 'refused' : 'transport';
      entry.error = reason;
      trip(reason, reason === 'budget' ? tr.budget_ms : undefined);
      throw new FailOpen(reason);
    } finally {
      pending -= 1;
    }
    entry.latency_ms = round(now() - start);
    entry.status = response.status;
    if (tr.enforce_budget && now() - t0 > tr.budget_ms) trip('budget', tr.budget_ms);
    let parsed;
    try {
      parsed = parseJevResponse(response.status, response.ok, text);
    } catch {
      const reason = response.ok ? 'unparseable' : 'non_200';
      entry.error = reason;
      trip(reason);
      throw new FailOpen(reason);
    }
    const ids = Object.keys(questions);
    const covered = ids.every((id) => typeof parsed.answers[id]?.noul === 'number' && Number.isFinite(parsed.answers[id].noul));
    if (!covered) {
      entry.error = 'incomplete';
      trip('incomplete');
      throw new FailOpen('incomplete');
    }
    entry.scores = ids.map((id) => parsed.answers[id].noul);
    if (tr.enforce_budget && out.trips.some((t) => t.reason === 'budget')) throw new FailOpen('budget');
    return parsed;
  }

  return {
    async ask(state, questions) {
      const entry = { questions: Object.keys(questions).length, sent: false, chunk_ids: (state?.chunks ?? []).map((c) => c.id) };
      out.requests.push(entry);
      if (tr.plan_only) {
        // which history segment this request carries (a short digest; the report counts segments per result)
        entry.history_key = createHash('sha256').update(JSON.stringify(state?.history ?? [])).digest('hex').slice(0, 16);
        throw new FailOpen('plan_only');
      }
      if (tr.serialize) {
        const run = chain.then(() => send(state, questions, entry));
        chain = run.catch(() => {});
        return run;
      }
      if (pending >= 1) {
        entry.error = 'queue_depth';
        trip('queue_depth');
        throw new FailOpen('queue_depth');
      }
      return send(state, questions, entry);
    },
  };
}

function firstTrip(trips) {
  let best = null;
  for (const t of trips) if (best === null || t.t_ms < best.t_ms) best = t;
  return best?.reason ?? null;
}

function pruneErrorClass(error) {
  const message = String(error?.message ?? error);
  if (message.includes('state leaves no room')) return 'pruner_error:state_no_room';
  if (message.includes('history fragment cannot fit')) return 'pruner_error:history_fragment';
  if (message.includes('request budget exhausted')) return 'pruner_error:request_budget';
  if (message.includes('Invalid Jev answer')) return 'pruner_error:invalid_answer';
  return 'pruner_error:other';
}

// Labels for the decision row (not decisions): which chunk ids the rendered output kept or dropped, found by walking the
// pruner's own chunk texts (from its requests) through its compact rendering (src/output.ts:562-578), and why each kept
// chunk stayed, by the pruner's exported predicates in the order of src/output.ts:478-486.
export function chunkLabels(sent, result, rendered, footer, keepThreshold) {
  const n = result.chunks;
  const texts = Array.from({ length: n }, (_, i) => sent.get(`c${i + 1}`));
  const body = rendered.slice(rendered.indexOf('\n') + 1, rendered.length - footer.length).split('\n');
  const kept = [];
  const dropped = [];
  let at = 0;
  let pending = 0;
  for (let i = 0; i < n; i += 1) {
    if (texts[i] === undefined) return { alignment: 'partial', kept: [], dropped: [] }; // a chunk the pruner never sent
    const lines = texts[i].split('\n');
    const markerOk = pending === 0 || body[at] === `[${pending} lines omitted]`;
    const start = pending === 0 ? at : at + 1;
    if (markerOk && lines.every((line, k) => body[start + k] === line)) {
      kept.push(i);
      at = start + lines.length;
      pending = 0;
    } else {
      dropped.push(i);
      pending += lines.length;
    }
  }
  if (pending > 0) {
    if (body[at] !== `[${pending} lines omitted]`) return { alignment: 'failed', kept: [], dropped: [] };
    at += 1;
  }
  if (at !== body.length) return { alignment: 'failed', kept: [], dropped: [] };
  const reason = (i) => {
    if (i === 0) return 'first';
    if (i === n - 1) return 'last';
    if (isProtectedLine(texts[i])) return 'protected_line';
    if (isProtectedLine(texts[i - 1].split('\n').at(-1)) || isProtectedLine(texts[i + 1].split('\n')[0])) return 'protected_neighbor';
    if (keepScore(result.scores[i], keepThreshold)) return 'score';
    return 'not_fully_scored';
  };
  return {
    alignment: 'ok',
    kept: kept.map((i) => ({ id: `c${i + 1}`, reason: reason(i) })),
    dropped: dropped.map((i) => ({ id: `c${i + 1}`, score: result.scores[i] })),
  };
}

// One recorded tool result through the handler's steps (hooks/fast-jev-output.ts:150-270), at the P1 floor.
export async function runJob(job, archives) {
  const t0 = now();
  const answer = job.answer;
  const tr = job.transport;
  const out = {
    id: job.id, stage: 'result', trips: [], requests: [], fail_open: false, fail_open_reason: null,
    decision: answer.deny !== undefined ? 'denied' : answer.isError ? 'tool_error' : 'missing_result',
    result: null, output: null, chunk_labels: null,
  };
  const finish = () => {
    out.elapsed_ms = round(now() - t0);
    // what the hook hands back as stdout: the pruned text, or the original unchanged (the tests ask; the replay does not)
    if (job.return_stdout) out.stdout_after = out.output ?? answer.result?.stdout ?? null;
    return out;
  };
  if (answer.deny !== undefined || answer.isError || !answer.result) return finish(); // :166
  out.decision = 'archive_recovery';
  if ([...archives].some((path) => job.command.includes(path))) return finish(); // :168
  const record = answer.result;
  const persisted = record.persistedOutputPath; // :170 (persistedOutputs defaults to true, :77-78)
  out.stage = 'read_output';
  const output = persisted ? job.persisted_text : record.stdout; // :174
  if (typeof output !== 'string') {
    out.decision = 'persisted_unreadable'; // replay only: the archived file could not be read
    return finish();
  }
  out.source_chars = output.length;
  out.decision = 'below_threshold';
  if (!exceedsOutputThreshold(output, 0, FLOOR_TOKENS)) return finish(); // :178, at the P1 floor
  out.decision = 'binary';
  if (looksBinary(output)) return finish(); // :180
  out.decision = 'document';
  if (classifyOutput(job.command, output) === 'document') {
    // which of classifyOutput's two document rules held (src/output.ts:126-127), for the report's breakdown
    out.document_rule = looksStructured(job.command, output) ? 'structured' : classifyInformation(output) === 'reference' ? 'reference' : 'other';
    return finish(); // :183
  }
  const combined = persisted ? output : output + (record.stderr ? `\n${record.stderr}` : ''); // :184
  out.stage = 'history';
  const messages = job.messages; // :190
  const goal = goalFromMessages(messages); // :191
  const secret = looksSecret(job.command, combined); // :192
  const path = secret ? undefined : persisted ?? `${HOOK.archiveDir}/${job.archive_stem}-${job.tool_use_id}.txt`; // :193-195
  const footer = recoveryFooter(path); // :196
  const maxChars = persisted
    ? Math.min(Math.max(0, HOOK.persistedMaxChars) || Infinity, answer.text?.length ?? Infinity)
    : Infinity; // :197-202
  const visibleChars = Math.min(maxChars, answer.text?.length ?? combined.length); // :204
  const requestLimit = Math.min(
    1 + HOOK.defaultMaxScoringRequests,
    Math.max(1, Math.ceil(visibleChars / HOOK.visibleCharsPerRequest)),
  ); // :205-208
  Object.assign(out, { secret, request_limit: requestLimit, max_chars: Number.isFinite(maxChars) ? maxChars : 0 });
  out.decision = 'footer_exceeds_budget';
  if (maxChars <= footer.length) return finish(); // :209-210
  out.stage = 'scoring';
  out.decision = null; // from here the pruner decides (onDecision); null if it throws before deciding
  const sent = new Map();
  let trimmed = null;
  let thrown = null;
  try {
    trimmed = await trimOutput(
      { command: job.command, goal, messages, output, fullOutputPath: path },
      makeAsker(tr, out, t0, sent),
      {
        minTokens: 0,
        minTokensFloor: FLOOR_TOKENS,
        maxChars: Number.isFinite(maxChars) ? maxChars : 0,
        compactMarkers: true,
        chunkLines: HOOK.chunkLines,
        keepThreshold: HOOK.keepThreshold,
        maxStateTokens: HOOK.maxStateTokens,
        // plan-all lifts the request cap so the plan lists every request the pruner would need (never sent)
        maxScoringRequests: tr.plan_all_requests ? 1_000_000 : requestLimit - 1,
        onDecision: (reason) => { out.decision = reason; },
      },
    ); // :219-250
  } catch (error) {
    thrown = error;
  }
  if (tr.plan_only) {
    if (thrown !== null) out.decision = 'plan'; // requests were planned; otherwise the pruner decided before any request
    return finish();
  }
  if (tr.enforce_budget && now() - t0 > tr.budget_ms && !out.trips.some((t) => t.reason === 'budget')) {
    out.trips.push({ reason: 'budget', t_ms: tr.budget_ms }); // the pruner's own work passed the budget
  }
  if (out.trips.length > 0 || thrown !== null) {
    // The seed's rule: any trip passes the original text through unchanged (the hook's catch, :270-273, covers only a throw).
    out.fail_open = true;
    out.fail_open_reason = firstTrip(out.trips) ?? pruneErrorClass(thrown);
    out.pruner_decision = out.decision;
    out.decision = 'fail_open';
    if (trimmed) out.result_ignored = { trimmed: trimmed.trimmed, dropped: trimmed.dropped };
    return finish();
  }
  out.result = {
    trimmed: trimmed.trimmed, chunks: trimmed.chunks, kept: trimmed.kept, dropped: trimmed.dropped,
    charsBefore: trimmed.charsBefore, charsAfter: trimmed.charsAfter, scores: trimmed.scores,
  };
  if (trimmed.trimmed) {
    out.stage = 'publish';
    out.output = trimmed.output;
    if (path) archives.add(path); // :255
    out.chunk_labels = chunkLabels(sent, trimmed, trimmed.output, footer, HOOK.keepThreshold);
  }
  return finish();
}

async function main() {
  const archives = new Set();
  const lines = createInterface({ input: process.stdin, crlfDelay: Infinity });
  for await (const line of lines) {
    if (!line.trim()) continue;
    let answer;
    let job = null;
    try {
      job = JSON.parse(line);
      answer = await runJob(job, archives);
    } catch (error) {
      answer = { id: job?.id ?? null, bridge_error: String(error?.stack ?? error).split('\n')[0] };
    }
    process.stdout.write(`${JSON.stringify(answer)}\n`);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) await main();
