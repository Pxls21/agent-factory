# DATA-SESSION: the typed decisions our own sessions make, with recorded answers (task #251's next source; owner 2026-09-25)

Role: evidence-gatherer (the EXPLORE lane, sandbox, Opus 5.5). Honey full. Report:
`docs/research/findings/laya-ft-data/SESSION-DECISIONS-2026-09-25.md` (write it incrementally from the start). Do NOT
spawn subagents. No verdicts: you catalogue and count; the coordinator decides.

## WHY

The owner (2026-09-25, voice-typed): "we use our own data ... this session alone is huge ... all the workflows that we're
using ... in this agent factory ... all the tools that we are using in our current session will be used in the agent
factory as well ... 3 birds, 1 stone." Our System 1 models (Laya, the RWKV student) learn typed decisions: a choice among
fixed options, a yes/no, a score. Our own sessions make the same kinds of decisions thousands of times, and the outcome
is often recorded right there: an exit code, a gate's verdict, a verifier's class, a refusal, an owner's ruling. A dataset
built from them trains the model on exactly the questions the factory's own workflow asks. D-083 governs labels: an answer
our process recorded, never a guess; a teacher only where no answer is recorded. DSV2 (running) harvests the committed
reports and commit messages; you cover the session records.

## GOAL

A catalogue of RECURRING typed decisions in our session records, each row with:
- the decision as a System 1 question (its type: choice, yes/no or score; the fixed options);
- the state: which record fields would form the input, and roughly how long it is;
- the recorded answer: where it comes from (an exit code, a later event, a verdict written in the record) and how
  deterministic that is;
- the count of instances, from a command you ran;
- the factory mapping: which agent-factory workflow or tool asks the same question (a gate, the stop hook, the lane
  dispatcher, the verify lane, the push path, bug-echo and the registry, routing);
- the risks: label leaks (the answer written inside the state), secrets in the state, and near-duplicates.

Seed families, to check and extend, not a limit:
- Tool calls: a command and its exit code; the error family (`scripts/hiccup_families.tsv`, as `scripts/hiccup_scan.py`
  clusters them).
- Gates and hooks: push_clean refusals (the stale-id check, the CI gate's waits and refusals), the commit stamp gate,
  the search intercept, the edit-snapshot AP screen tells.
- Verify lanes: the finding classes, the gate recommendations (MERGE-READY, MERGE-READY-WITH-FOLLOWUPS, NOT-READY,
  CONTRACT-INVALID), the repairs.
- Dispatches: a lane or agent's terminal outcome (landed, FAILED, refused), and the served-model mix.
- Owner turns: the coordinator's question and the owner's ruling (a D-row quoting the owner's words is a recorded answer).
- Retro answers at the stop gate (a lesson baked or "nothing to bake").
- Bug-echo runs: a defect and the AF-AP class it was registered under.

## SOURCES (read-only)

- The raw session transcripts under `/root/.claude/projects/-home-user/` (the main session file is about 702 MB, and 296
  JSONL files hold about 1.3 GB in total, including subagent transcripts). STREAM every file line by line; never load a
  file whole.
- The agent output files under `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/tasks/` (69 MB).
- The committed digests `transcripts/sandbox/` and the PC lane digests `transcripts/pc/`.
- Tools that already parse these: `scripts/hiccup_scan.py`, `scripts/chat_tail.py`, `scripts/transcript_export.py`,
  `scripts/decide-harvest` (its `transcript_jsonl` source kind reads 0 records today).

## CONSTRAINTS

- Read-only on the repository at `/home/user/agent-factory`: write ONLY your report, and small files under
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/data-session/`. The sandbox disk is 94% full
  (2.6 GB free): keep every file you write under 50 MB in total. No git writes of any kind (a build lane shares the tree).
- The transcripts are raw session records. Report COUNTS, SHAPES and field names. Quote nothing unless it has passed
  `scripts/transcript_export.py`'s scrub first, and keep any quote short. Never search the records for keys, tokens,
  passwords or credentials, and never print an environment dump.
- No network; no PC bridge; no outward-facing action.
- FAKE strings only for anything secret-shaped. Check the report with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`
  (0 expected) before you finish.

## EVIDENCE DEMANDS

1. The catalogue table: at least 12 decision types, each with its count and the command that produced it.
2. For the 5 rows with the best mix of volume and label determinism: 3 scrubbed examples each (the state's fields and
   the recorded answer), plus the label-leak check you ran.
3. An export budget: the bytes per record for each of the 5 (state plus answer plus provenance), and the total, so the
   coordinator can size a scrubbed export to the PC.
4. The factory mapping, one line per row.
5. NOT-done: what you could not count, and why.

## PREMISE (measured at authoring, 2026-09-25 01:3xZ, the sandbox)

```
$ du -sh /root/.claude/projects/-home-user /root/.claude/projects/-home-user-agent-factory
1.3G	/root/.claude/projects/-home-user
1.8M	/root/.claude/projects/-home-user-agent-factory
$ ls -la /root/.claude/projects/-home-user/*.jsonl | awk '{s+=$5} END {print "main jsonl bytes", s}'
main jsonl bytes 701574704
$ find /root/.claude/projects -name "*.jsonl" | wc -l
296
$ du -sh /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/tasks
69M	/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/tasks
$ df -h /root | tail -1
/dev/vda        252G   35G  2.6G  94% /
$ python3 scripts/decide-harvest --out <scratch>/rows.jsonl   (stderr)
sources: 298 read (incident_log=1, lane_report=165, transcript_jsonl=0, verify_report=132), 276 with no records; refused: 153 records; skipped: 0 duplicates
```
