---
name: session-continuity
description: Resume/continuity protocol — verify session timeline and work provenance against the transcript and git BEFORE asserting who did what, when, or re-executing any close-out. Load on EVERY session resume from a compaction summary, whenever origin is ahead of your remembered state, whenever local commits look like duplicates of origin, or before claiming a container/session "died" or that "another session" did work.
---

# Session continuity — verify before asserting (owner mandate 2026-08-04)

## The incident this skill exists for

2026-08-04: a session resumed from a compaction summary frozen at Jul 31 in a
workspace whose DISK was also rolled back to the Jul-31 state — while the same
session had in fact worked continuously Jul 31 → Aug 3 (RP-I4, PBO-IN-LOOP
P1–P4, ~30 pushed commits). The coordinator trusted the stale summary plus the
stale disk, RE-DID an increment it had already built and pushed three days
earlier, then — on seeing origin ahead at fetch time — invented a false
"parallel session did this while this container was dead 3.5 days" narrative
and reported it to the owner as fact. Two independent stale sources
(summary + disk) agreeing with each other felt like confirmation. They were
the same rollback twice.

## The protocol (mandatory, in order, BEFORE resumed work)

On every resume from a summary — and again at any point mid-session where
origin state, task state, or owner statements contradict what you remember:

0. **The sandbox task DB resets with the container (learned 2026-08-25, twice in one
   day).** It is container-local state — after any reset, do NOT trust its rows and do
   NOT laboriously reconstruct them: re-seed ONE ledger-resync summary task from
   `wiki/topics/live-state.md` + `todo/BUILD-TASKLIST.md` (the survivors), fix only the
   rows you will actively drive. Run `scripts/resume-heal.sh` first — it does the whole
   mechanical resume (ff-only sync, venv reinstalls, hooksPath, index rebuilds) in one
   command.
1. **Fetch first.** `git fetch origin <branch>` before ANY plan built on the
   summarized state. A close-out chain (rebase/push/report) planned against a
   stale origin is wrong from step one.
2. **Date the three clocks and compare:**
   - origin tip: `git log -1 --format='%ci %s' origin/<branch>`
   - local tip + base: `git log --oneline origin/<branch>..HEAD`
   - transcript: first/last timestamps + entries-per-day histogram of
     `/root/.claude/projects/<project>/<session-id>.jsonl`
   If the transcript shows activity AFTER the summary's last event, the
   summary is STALE — the transcript is the primary source for session
   history, the summary is a lossy cache. Rebuild state from transcript tail
   + origin log before acting.
3. **Origin ahead of your memory = almost always YOUR OWN later work.** One
   session, many container incarnations, is the normal topology here — the
   owner runs ONE chat. Unpushed local commits whose messages nearly match
   origin commits are a rollback artifact (your own redone or rolled-back
   work), not evidence of a second author. NEVER assert a multi-session /
   parallel-agent narrative without transcript evidence (a second session id,
   interleaved foreign turns). Commit-message similarity is evidence FOR
   rollback, AGAINST parallelism.
4. **The workspace disk is not a clock.** Containers get reset and restored
   from snapshots that can lag the transcript by days. "The tree matches my
   memory" verifies nothing about recency — only pushed origin state and the
   transcript carry trustworthy timestamps.
   **The summary's push-state claims are a clock too — verify the boundary
   with `git log origin/<branch>..HEAD` and `git merge-base --is-ancestor`
   before trusting "unpushed"** (2026-08-28: a summary claimed a 4-commit
   stack was local-only; it had been pushed pre-compaction — raw, with the
   trailers push_clean.sh exists to strip — and the "gated push" plan built
   on that claim was fiction until the boundary read caught it).
5. **When the owner contradicts your timeline, they are the better-calibrated
   instrument.** Stop, go to the transcript, and re-derive — do not defend
   the narrative or ask them to re-explain. The owner watched all three days
   happen; you remember a summary of one.

## Recovery assets when a rollback IS confirmed

- **Pushed commits** — authoritative; reset the branch to origin rather than
  re-verifying duplicate local work.
- **The transcript JSONL records every Write tool call with full content** —
  lost scratchpad briefs, wrapper scripts, and drafts are recoverable by
  extracting `tool_use` entries (`name == "Write"`) and replaying their
  `content`.
- **CORRECTED 2026-08-27 (proven live): SUBAGENT transcripts SURVIVE rollbacks**
  at `/root/.claude/projects/<project>/<session-id>/subagents/agent-<id>.jsonl`
  — `/root/.claude` is the durable store; only the `/tmp` scratchpad task
  mirrors roll back with the disk. Recover from `/root`, never conclude loss
  from `/tmp` absence.
- **CORRECTED 2026-08-27: unpushed commits destroyed by a rollback are
  REBUILDABLE by edit replay** — `scripts/replay_transcript_edits.py` (in-repo,
  survives rollbacks) re-applies every Edit/Write from the main-session +
  subagent JSONLs in timestamp order onto the rolled-back tree; set the target
  file list + timestamp cutoff at the top. Proven 2026-08-27: five commits
  (37 edits) rebuilt verbatim, 0 failures. LIMIT: content appended via Bash
  heredocs is transcript-INVISIBLE — redo those by hand (and prefer
  Write/Edit over heredocs for anything worth recovering).
- **Push-on-green inverts under a rollback storm** (incident 2026-08-27):
  once the verify lane has graded the CONTENT (bitwise/mutant evidence),
  holding commits hostage to a full-suite pass the environment keeps killing
  is net-negative — push the verified content, finish the suite forward.
  Say so first-class in the recovery report ("NOT recovered: <sha> <what>"),
  and rebuild from the recovered briefs + verdict summaries.
- **The task DB is a rollback victim too, and WORSE: its ~20 slot numbers get
  reused, so completed programs vanish silently (owner caught it 2026-08-10 —
  the PBO-IN-LOOP/SEAL-era programs had no rows left).** The durable mirror is
  `todo/BUILD-TASKLIST.md` §LIVE (mirror every task create/close there in the
  same increment, push); the forensic backstop is the transcript's complete
  TaskCreate/TaskUpdate record (extract `tool_use` entries by name — 70
  creates were recovered that way). On resume: restore the task DB FROM the
  ledger, and diff task-DB-vs-ledger on keep-alive ticks whenever either
  changed.

## Standing rules distilled

- **THREE-LAYER STARTUP ORIENTATION (owner directive 2026-08-28: "you look
  at the last commits, you look at the chat history... and then you use
  graft at the end to just connect the dots").** At EVERY session start /
  resume, in order: (1) CHAT — the transcript raw, for intent (what was
  said/decided last); (2) COMMITS — the files the last commits touched,
  for the delta; (3) GRAFT — `graft ask` on the touched code areas, the
  final context layer that connects intent to wiring. `scripts/orient.sh`
  mechanizes layers 1-2 and prints ready-to-run layer-3 asks (hooked into
  session-start.sh); the agent RUNS the asks for any area it will touch
  before resuming work there. Hybrid division stands: graft for code
  wiring, chat_tail+Read for conversation nuance — orient.sh is where they
  meet. Then the three-clock verify as always.
- **READ THE CHAT HISTORY FIRST when confused (owner mandate 2026-08-28:
  "if you don't know something, then just read the fucking chat — that
  should be part of the recovery plan").** On ANY confusion about what
  happened, what was decided, or what a message refers to: read this
  session's transcript JSONL tail (`scripts/chat_tail.py <transcript>
  [--turns N] [--day YYYY-MM-DD]` — live-proven; prints the hour histogram
  + last real user turns) BEFORE asking the owner anything or acting on a
  guess. For SEMANTIC questions ("what did the owner decide about X", "why
  did we abandon Y"), run `chat_tail.py --export <dir>` (one clean md per
  day, noise stripped; 6,891 turns in 1.4s measured) and Read the relevant
  day file — the model reading prose IS the semantic engine. Do NOT reach
  for graft here: measured 2026-08-28 (owner-requested A/B), `graft build`
  on the exported 3.8MB markdown corpus parsed 0 of 0 files (language-
  grammar parsers; prose has no wiring) and `ask` returned empty — graft
  is for CODE questions, structurally inapplicable to chat history. If the transcript has a TIME HOLE (an hour-histogram shows
  zero events across a window origin's commits span), the work happened in
  a SIBLING SESSION whose transcript is not on this disk — recover its
  state from what it PUSHED, in this order: wiki live-state → the findings/
  docs its commits name → commit messages (reasoning records) → the task
  ledger. The owner's messages in a sibling session are reachable only
  through those artifacts — treat OWNER-RULED lines in live-state/docs as
  the ruling record. Never make the owner re-explain something the record
  already carries.
- **Scratchpad state rolls back WITH the container — re-seed side-channel
  creds BEFORE diagnosing any external outage (2026-08-27, bit twice in one
  night).** The bridge wrapper (scratchpad `pc.sh`) carries an ephemeral
  tunnel URL + token; after a rollback it silently reverts to DEAD old creds,
  and every probe then returns a convincing 502 "bridge down". A whole tick's
  bridge window was lost to that misdiagnosis. On every resume/rollback:
  re-seed the wrapper from the owner's most recent banner (transcript/summary
  carry it) FIRST, then probe. General form: any failure through a
  scratchpad-held credential is UNTRUSTED until the credential's freshness is
  re-verified — the 502 tells you about the OLD creds, not the service.
- Never re-execute a close-out chain (rebase → push → report) from a resumed
  summary without a fresh fetch + three-clock comparison first.
- Never report a provenance/timeline claim ("container died N days", "another
  session pushed this") to the owner without citing which clock proved it.
- A stop-hook or fetch surprise ("origin moved", "commits unverified") during
  resumed work is a CONTINUITY alarm first, a git problem second — run the
  protocol before touching the tree.
- **Armed fallback prompts and scheduled triggers are snapshots, not truth
  (2nd bite, 2026-08-07).** A send_later/trigger message describes the world
  as of when it was WRITTEN; after a rollback it can instruct you to resume
  subagents, re-verify commits, or check runs that later incarnations already
  superseded and closed. Run fetch + three-clock BEFORE acting on ANY armed
  instruction on wake — the protocol gates trigger-driven work exactly as it
  gates summary-driven work. Same for resuming subagents: a builder/verifier
  from a pre-rollback timeline is a zombie once origin has moved past its
  brief — STOP it and reconcile against origin instead of nudging it onward.
- **The summary re-bites on every recycle (3rd bite, 2026-08-07, same day).** A compaction
  summary is re-served to EVERY new incarnation; container snapshots and local origin refs can
  all be stale TOGETHER and agree. Two defenses: (1) `git fetch` in the literal first tool batch
  of any incarnation resumed from a summary — a stale local origin ref agreeing with your memory
  is the failure mode, not reassurance; (2) after reconciling, state the verdict in USER-VISIBLE
  text ("origin tip is <sha>; local <date> state is a rollback artifact") — the conversation is
  the only artifact that survives recycles, so the next summary must carry the truth. Extra
  rollback tell: `list_triggers` showing fired send_laters you don't remember arming.

- **Closure claims are SEMANTIC, not string-level (2026-08-24, "these are terrible
  questions").** "X was never addressed" requires a capability-level search — concept
  synonyms across commits (the reasoning records), compaction summaries, ledger, and
  code — never a grep for the registration row's own text. Programs resolve old asks
  under NEW names (a "CSCV regime-blindness" complaint was answered by the whole
  M-mode/regime-specialist program; "family combination" by K-specialists-per-run);
  string-closure marks them unaddressed and re-asks the owner questions the build
  already answered. Same instrument rule as re-derivation: read the wave
  findings/commits BEFORE proposing a fork or a question the program may have settled.

- **LOST-COMMIT RECOVERY FROM SUBAGENT TRANSCRIPTS (2026-08-31, proven).** A delegate's
  commits that were never pushed are NOT lost to a container rollback: the subagent
  transcript survives under
  `/root/.claude/projects/<project>/<session>/subagents/agent-<id>.jsonl` and records every
  Edit/Write tool_use with full content. Recovery recipe: (1) locate the transcript by
  grepping for a distinctive symbol the agent created; (2) extract tool_use ops
  programmatically (never Read the JSONL whole — it overflows context); (3) replay
  Write=write / Edit=replace-first in transcript order onto the SAME base SHA the agent
  started from; 34/34 hunks applying with zero fuzz is itself the fidelity proof;
  (4) commit + push to a RECOVERY branch immediately (push IS the durability boundary),
  never to trunk while unverified. CAVEAT (proven the hard way, same incident): a
  transcript-recovered diff is UNVERIFIED CODE regardless of the original builder's green
  report — the 08-31 adversarial pass found two CRITICAL regressions in a
  "79-green x2" recovered diff. Recovery restores bytes, not trust; the full verify
  gate still runs. Upstream prevention: delegates on rollback-prone containers push a
  work branch when green (orchestration lane rule).

- **OWNER TERMS OF ART RESOLVE IN THE OWNER'S SOURCE REPO BEFORE THEY ARE INTERPRETED (2026-09-03,
  agent-factory port).** "The quartet" was answered as the git-hook trio; it was the four code-intel
  tools — a section TITLE in the source repo's CLAUDE.md. Same message, second misread: a model server
  seen running on the PC was assumed to be a dependency when the owner's egress was the gateway in front
  of it. Rule: when the owner names something you cannot place, `grep -rn -i '<term>'` the repo they
  built with (its CLAUDE.md, ledgers, runbooks) and their live-asset runbooks BEFORE answering; the
  source repo is a primary source for vocabulary, not only for code. Answering from the nearest
  familiar meaning costs a correction round every time.

- **REPORTS OF RECORD NEVER LIVE ONLY IN THE SCRATCHPAD (2026-09-02, bit twice in one
  night — two container restarts wiped `$S/report_V4.md` + `$S/report_V6.md`, blocking
  three I4e residuals whose scope was defined ONLY there).** A verify/repair lane's
  report of record, any proposed-edit text awaiting a ruling, and any enumerated work
  list (e.g. an unrun-mutant set) gets persisted to the REPO (`tasks/` stamp,
  `.agents/research/`, or the ledger row) in the same increment that cites it —
  the scratchpad is for in-flight working files only. Recovery from the transcript
  JSONL works (every Write is recorded) but costs a whole archaeology lane; the
  one-line repo copy at citation time costs nothing.

## Handed-value freshness (2026-09-03 — three stale values in one night, all owner-caught)

Any VALUE handed to a human for execution (env var, launch parameter, universe,
timeframe, K) is a brief, and its premises age like briefs. Before handing one over,
build the value→dated-source table and take each value from the NEWEST dated layer:
ledger sync block > interview-validated seed > campaign findings > runbook env section
> script/code default. The runbook's env lines and code defaults are convenience
copies that drift (three did: GA_SYMBOLS 6 weeks stale, launch-script default 4-token,
code default 3-token); the ledger's dated sync blocks are append-only and win. An
EXTERNAL research doc is a source of questions, never of campaign constants — RP-31's
"hourly" framing contradicted the settled 4h frame and rode into two preregs before
the audit caught it.

## Deep-history asset (2026-09-03)

`.agents/research/2026-09-03-session-histogram.md` is the full-transcript
reconstruction (every owner ruling verbatim in §4, pinned campaign parameters in
§5, eras back to July from the ledger). Live-state = the recent map; the histogram
= the deep record. Consult §5 before handing any value for execution and §4 before
re-deciding anything that smells previously ruled. If it ages, regenerate with the
chat-histogram workflow script under the session workflows dir.

- **When the owner NAMES an artifact ("the inc9 script"), grep the commit history for
  that name FIRST** (`git log --all --oneline | grep -i <name>` + the runbook) — never
  reply with a rebuilt/guessed substitute. 2026-09-03: the owner named relaunch_inc9
  three times while the coordinator invented a new script, offered the wrong launcher,
  and searched scripts/ twice; the answer was in the runbook's "proven cell" paragraph
  and the commit subjects the whole time. Owner recall of names outranks search heuristics.
