# JEV LEVERAGE RE-AUDIT — SYNTHESIS (task #221, D-069 item 5)

| Field | Value |
|---|---|
| Date | 2026-09-24, written 12:1xZ |
| Author | the coordinator (verdicts and plan are the coordinator's; every fact cites the evidence doc) |
| Evidence | `docs/research/findings/JEV-LEVERAGE-EVIDENCE-2026-09-24.md` (rows E1-E6, an Opus 5.5 evidence lane, no verdicts); `docs/research/findings/CLM-AGENT-BEACON-READ-2026-09-24.md` (#222); `docs/research/findings/MOJEV-AUDIT-2026-09-24.md`; `docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md` (D-045) |
| Fresh reads | PC `GET 127.0.0.1:47411/health` at 12:09Z: `"ok": true, "calls": 2, "device": "cpu"`; unit `laya-systemone` active since 2026-09-23 19:59:59Z, `NRestarts=0`. Sandbox: 16 GB RAM (14.7 GB free), 4 CPUs, `/root/venv-laya-probe` imports `laya` 0.3.5, the pinned snapshot is under `/root/hf-laya-probe` (1.6 GB) |

## 1. The answer: no, Jev is not leveraged

The owner asked whether this setup uses Jev the way it should. It does not. What exists is a capture plane and a set of probes. Nothing
reads a Jev answer in daily work.

1. The PC endpoint has answered 2 requests since it started 16 hours ago (the fresh read above). Both were the PCJ1 smoke.
2. The sandbox has no endpoint (E1.1 row 19). The sandbox's output-pruner plugin is enabled but never engaged: 0 real pruner footers in
   this session's 651 MB transcript (E1.3).
3. The J1 decision ledger has no consumer and no committed rows (E2, J1 table). `scripts/decide-harvest` runs only by hand. The last
   real harvest gave 235 rows: `ap.violates_row` 121, `v1.finding_class` 111, `wf.drift` 3, every other type 0.
4. The council's next step, J2 (the signal probe), is not started. Its named type, B2 hit-role, has 0 harvested rows. KC-J7 (label famine,
   2026-11-03) will fire on that type as things stand.
5. The planned Jev consumers have no code: the AP-hawk (#115), the drift-hawk (#116), the pijev port (#133), the dream triage (#195)
   (E2). The pruner is parked for Hermes lanes (D-053).

## 2. Where the System-2 spend goes

The owner's premise is that System-2 models spend tokens on System-1 work. The evidence says the biggest waste is context volume, not
decisions (E5, this session's transcript):

- A median API request carries 457,469 tokens (p90 720,193). The session compacted 118 times.
- `task_reminder` records are 44.4% of the transcript's bytes. Each one carries the whole task list.
- Tool results: Bash is 80% of result bytes but small per call (1,624 bytes on average). The largest single results are Reads of big
  files and TaskList calls (35-49 KB each).
- The one context hook that fired per prompt (`wiki-context.py`) injected 6.5 KB per person's prompt and 11.5 KB per background event
  once the hooks went live (AF-AP-182).

E3 lists 70 decision points in the skills, hooks, scripts and CLAUDE.md. 28 of them are model judgment inside skills. Most have no
label source, so no one can yet say whether a scorer would do them as well.

So the order is: cut the volume deterministically first, then use Jev where it can choose what the big model reads.

## 3. The principle: Jev finds, deterministic code blocks

KC-J1 (D-045, accepted by the owner) stays. No Jev value reaches a gate, a merge, a lint, a commit, a push or a proof predicate. The owner
also asked for hooks that "block or stop certain things". Both hold under one pattern:

1. Jev flags a candidate (cheap, broad, System-1).
2. The System-2 model or a person confirms it (KC-J1b: a Jev score is never the only evidence).
3. The confirmed case becomes a deterministic rule and a failing test.
4. The deterministic rule blocks.

This is the #198 leak-hunter design, generalized. Jev takes the searching and sorting off the big model. A probabilistic miss never
becomes a hollow green, because nothing Jev says is enforced until a deterministic rule encodes it.

## 4. The plan, in order, each step measured

| Step | What | Status 12:1xZ |
|---|---|---|
| 0 | Deterministic context diet: the hook skips background events and injects one block (AF-AP-182, cf026a9); task subjects trimmed; closed tasks pruned from the in-session DB (the ledger keeps them) | first two DONE, the third next |
| 1 | `scripts/jev.py`, the programmable tool: `health`, `ask` (one typed question), `rank` (score candidates for a query), `classify` (a choice). Venue order: a sandbox-local server, then the PC endpoint over the bridge; any failure is fail-open (exit code, one stderr line, no answer). Every call appends a local log line (question, state digest, answer, latency) so that calls become labels. States are scrubbed of secrets before they leave the process. No gate file may import or run it (the screen enforces this) | NOT built |
| 2 | `scripts/hiccup_scan.py` and a generated page of agent progress and quirks (section 6) | NOT built |
| 3 | The first signal probe on the types that HAVE labels: `ap.violates_row` (121) and `v1.finding_class` (111), scored through `jev.py` against the majority-class and lexical baselines (J2's shape; J2 names B2, which has 0 rows) | NOT run; owner question Q1 |
| 4 | Jev in the hooks, only where step 3 beats the baselines (section 5) | NOT built |
| 5 | MoJev Gate 0 on the PC (brief `tasks/briefs/pc/pc-mojev-g0.md`): does a 16k-token scorer fit our CPU for long states (whole reports, transcript windows)? Laya's window is 1,024 tokens by its config (E1.1 rows 4, 4a) | staged, waits for K170 to free the local slot |
| 6 | J1 gets its consumer: step 3 reads the harvest; after J1-1-R4 verifies, the harvest runs at session start | waits on J1-1-R4 |

Why a sandbox-local server: J0 measured the sandbox at p50 260 ms per question (4 threads, SYNC-OK) and the PC at p50 336 ms (ASYNC-ONLY,
plus the bridge round trip) (E1.1 row 13). The hooks run in the sandbox. The weights and the venv are already here. Two costs: CPU
contention with running agents (J0 ran on a quiet box), and a fresh container has no snapshot (an 842 MB download, or the PC fallback).
For the production copy, the PC endpoint on loopback is the target: Hermes lanes run on the PC.

## 5. Jev in the hooks

| Hook | Jev role | Mode | Why this mode |
|---|---|---|---|
| New `.claude/hooks/ap-hawk.py` (PostToolUse on Edit/Write of production `.py`) | lexical top-16 of the 137 registry rows with no mechanical screen (E4.1), then a Jev choice; inject the top 3 as "suggested, unverified" | inject once step 3 passes on `ap.violates_row` | `edit-snapshot.py` is a listed gate file (`scripts/gate_files.txt:53`), so Jev never enters it; a separate hook keeps KC-J1 clean |
| `wiki-context.py` (UserPromptSubmit) | rerank the candidate wiki and registry sections for a person's prompt | shadow: log both rankings, inject the lexical one | no label source (E3 row H1); the log creates the labels |
| `turn-retro-gate.sh` (Stop) | none yet | none | its checklist decisions have only partial labels (E3 row S13) |
| `session-start.sh` | none yet; later, rank which open tasks and ledger lines to inject | none | same |
| Output pruner (Bash results) | already built (`fast-jev-output`); engages over 10,000 estimated tokens | on once a server runs | the coordinator already cuts outputs with `head`/`tail`; low value here (E5) |

## 6. The hiccup and quirk tracker

The owner asked for a document that shows how the agents progress and where they hit quirks. The evidence lane already wrote the parser
(E4.3). It becomes `scripts/hiccup_scan.py`, deterministic, no model. It streams the session transcripts and the subagent transcripts and
writes one page with:

- per day: tool calls, errors by family, compactions, median context per request, reminders, refusal stops;
- per agent or lane: the served model mix, refusals, duration;
- recurring error first-lines (numbers, paths, keys and URLs removed, then the transcript scrubber), with counts, first and last seen,
  and whether an AF-AP row or a CLAUDE.md quirk line already covers them; an uncovered cluster is flagged;
- later, a Jev column: the registry class each uncovered cluster most resembles (advisory, KC-J1b). This borrows agent-beacon's
  question-over-batch-summary loop (#222), run against our local scorer, never a hosted one.

This session's numbers show why it pays: 239 tool errors, 28 blocked foreground sleeps, 23 auto-mode denials, 11 edit-anchor misses, 1,064
"the user has not heard from you" reminders (E4.3).

## 7. Moving System-1 work off the big models

Candidates from E3, ordered by the labels that exist today:

| Decision | Where | Labels | Jev fit | Next |
|---|---|---|---|---|
| Which registry row a change resembles | S7, H8 (137 rows unscreened) | 121 (`ap.violates_row`) | ranking plus a choice | step 3, then the AP-hawk |
| A verify finding's class | S2 | 111 (`v1.finding_class`) | 6-way choice | step 3, advisory only (KC-J1b) |
| Which wiki or registry section to read | H1 | none | ranking | shadow log |
| An error event's class | the tracker | none | choice over classes A-J | the tracker creates labels |
| Which lane report shape came back | P12 | report files | regex works today | no change |
| Tier and breadth routing | C1, C2 | none | deferred by the council (sync class) | no change |

Delegation is the other half. The routing table already sends sweeps to Haiku and verify lanes to other models. The deterministic diet
(step 0) is the cheapest System-1 saving of all.

## 8. The production copy (E6)

- The Hermes hook map carries four of the five hooks; `turn-retro-gate` is commented out
  (`harness-ports/hermes/config-snippet.yaml`). Whether the PC lane profiles carry the snippet is not verified.
- `jev.py` must work on the PC against the loopback endpoint, because production runs there.
- The pruner does not engage in Hermes lanes (D-053).
- `docs/WORKFLOW-OFFLOAD-MAP.md` is the only committed statement of what production mirrors; it predates Jev.

## 9. Owner questions

- **Q1. J2's question type.** The council named B2 hit-role, which has 0 harvested rows. Run J2 first on `ap.violates_row` (121) and
  `v1.finding_class` (111), with the same comparators and the same pre-committed sample digest? Recommended: yes. The alternative (wait
  for B2 labels) stalls the layer into KC-J7.
- **Q2. Jev never blocks.** Keep KC-J1 and meet "block or stop" through the pattern in section 3? Recommended: yes. A scorer inside a
  gate would give a flaky gate or a hollow green.
- **Q3. A Laya server inside the sandbox.** Run one for the hooks, with the PC endpoint as the fallback? Recommended: yes. It costs CPU
  while agents run and does not survive a container reset without a download.

## 10. NOT built (12:1xZ)

`scripts/jev.py`, `scripts/hiccup_scan.py`, the tracker page, any Jev hook, the step-3 probe, J2, the AP-hawk, the drift-hawk, the pijev
port, the dream triage, MoJev Gate 0 (not run), a sandbox Laya server. Built and live: the PC endpoint (2 calls), the J1 capture plane (no
consumer), the never-a-gate screen, the J0 and pijev probes.
