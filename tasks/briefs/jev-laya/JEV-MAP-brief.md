# JEV-MAP: every place in our setup where a System 1 Jev can read the session and act (owner 2026-09-25; D-086)

Role: evidence-gatherer (the EXPLORE lane, sandbox, Opus 5.5). Honey full. Report:
`docs/research/findings/laya-ft-data/JEV-INTEGRATION-MAP-2026-09-25.md` (write it incrementally from the start). Do NOT spawn
subagents. No verdicts: you map and measure; the coordinator decides.

## WHY

The owner (2026-09-25, D-086): "You dont consider them high quality because you havent fully mapped out how much jev can truly be
integrated in our setup ... the rwkv version will be processing session data alongside layla so we need to leverage it." Two
System 1 models are in play:
- **Laya** (0.4B): per-block typed decisions over a window of 512 tokens (its config), about 1 s per question on CPU.
- **The RWKV-7 student** (0.4B, starting from G0): its fixed-size state reads a whole stream. Measured on the 3090 (premise): one
  forward over 61,440 tokens in 1.17 s, and a 15-token question answered from a copy of the saved state in a median 0.046 s.
The earlier audits mapped a different reader: JEV-LEVERAGE (nothing reads a Jev answer in daily work; a hooks table), MOJEV (a
16k-token scorer cannot read a session) and DATA-SESSION (26 decision types, judged by each record's own fields). None mapped a
STREAM reader, whose state is everything before the decision. SESSION-EXPORT (a build lane running beside you) will produce the
scrubbed stream; this map says which decisions to train and where each would plug in.

## GOAL

A map of every decision point in our workflow where a Jev could answer a typed question: in this sandbox session, in the PC lanes,
and in the factory's planned runtime. For each point:
- the question as a System 1 question, with its type (choice, yes/no or score) and its options;
- when it is asked: the event in the stream just before it, and the seam (file:line of the hook, script or tool);
- what the answer would change: warn, block, route, rank, prefetch, skip a run, stop a lane early;
- its label: the recorded answer (DATA-SESSION's R-row, or a new one you name with its source field and a count);
- whether the stream prefix holds the answer's cause, MEASURED on our transcripts (the coordinator's probe in the premise is the
  shape: the prior read of an edited file, 614 of 652), and whether the record's own fields hold it (Laya's view);
- the model: the RWKV stream reader, Laya per block, or both;
- the time budget: the seam's timeout or the latency that makes the answer useful, against the measured speeds.

Families to check and extend (not a limit): PreToolUse (will this call fail, be blocked by the harness, be denied; does an Edit
need a Read first; the search intercept), PostToolUse (the error family; anti-pattern tells on an edit hunk; prune a large
output), Stop (the retro gate: bake or nothing; uncommitted, untracked, unpushed), UserPromptSubmit (which wiki or registry section
to inject), SessionStart (which ledger lines and tasks to inject), the lane dispatcher (a lane stuck, looping on refusals, starved
of KV cache; its terminal outcome early), the push path (a CI red before the push), the verify lane (a finding's class, blocking,
the gate recommendation), the harvest (the served-model mix), bug-echo (the registry class of a defect), routing (the tier and
the agent type), and the factory's runtime (the Hermes `pre_tool_call` policy hook as an advisory, the dream triage).

## SOURCES (read-only)

- The raw transcripts under `/root/.claude/projects/-home-user/` (1.3 GB; STREAM every file, never load one whole) and the agent
  outputs under `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/tasks/`.
- DATA-SESSION's report and scratch producers (`docs/research/findings/laya-ft-data/SESSION-DECISIONS-2026-09-25.md`;
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/data-session/decisions.py` has parsers for F01-F22:
  reuse them as a starting point, not as proof).
- `docs/research/findings/JEV-LEVERAGE-AUDIT-2026-09-24.md` (sections 4, 5, 7), `docs/research/findings/MOJEV-AUDIT-2026-09-24.md`,
  `docs/research/findings/j2b-variants/rwkv7-g0/2026-09-24-window2/README.md` (the RWKV mechanics).
- The hooks and their registration: `.claude/hooks/`, `.claude/settings.json`, `scripts/install_session_hooks.py`,
  `/home/user/.claude/settings.json` (read the hook entries and timeouts only).
- The dispatcher and runner: `scripts/pc_lane.sh`, `harness-ports/bin/pc-lane.sh`; the push path: `scripts/push_clean.sh`,
  `scripts/ci_gate.py`, `scripts/hooks/`; the factory plan: `docs/01_ARCHITECTURE.md`, `docs/11_DREAM_PHASE.md`.

## CONSTRAINTS

- Read-only on the repository: write ONLY your report, and small files under
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/jev-map/`. Keep what you write under 50 MB (the disk
  has about 2.7 GB free). No git writes of any kind (two build lanes share the tree).
- The transcripts are raw session records. Report COUNTS, SHAPES and field names. Quote nothing unless it has passed
  `scripts/transcript_export.py`'s `scrub` first, and keep any quote short. Never search the records for keys, tokens, passwords
  or credentials, and never print an environment dump.
- No network; no PC bridge; no outward-facing action. FAKE strings only for anything secret-shaped.
- Check the report with `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` (0 expected) before you finish.

## EVIDENCE DEMANDS

1. The map table: at least 25 decision points, every column filled or marked with why not, each measured cell with the command
   that produced it.
2. For the 10 points with the best mix of payoff and label count: the cause-in-prefix count and the cause-in-record count (from
   the transcripts), the label count by answer class, and the leak risks (an answer written into the state before the decision).
3. The runtime path: how a stream reader would receive the session live in each venue (the hook events this harness sends and
   their timeouts; the transcript file as it grows; Hermes lanes on the PC), and what one state update and one question cost at
   the measured speeds.
4. What SESSION-EXPORT must keep for each of the 10 points (fields and positions), checked against its brief's event schema
   (`tasks/briefs/jev-laya/SESSION-EXPORT-brief.md`, D-1).
5. NOT-done: what you could not map or measure, and why.

## PREMISE (measured at authoring, 2026-09-25 02:2xZ, the sandbox)

```
$ (the coordinator's cause-in-prefix probe over the main session file, 704,448,851 bytes)
EDIT {'n': 652, 'prior': 614, 'err': 11, 'err_prior': 9}
TEST {'n': 824, 'prev': 40, 'same_noedit': 17, 'noedit': 18, 'same_edit': 15, 'edit': 22}
$ sed -n 28,34p docs/research/findings/j2b-variants/rwkv7-g0/2026-09-24-window2/README.md
- Load 0.44 s; 859 MiB allocated.
- One forward over real repo text (`g0.json` ladder; all logits finite): 2,048 tokens 42.9 s (the first call pays
  Triton's compile and autotune), 4,096 0.38 s, 8,192 0.18 s, 16,384 1.47 s, 32,768 0.64 s, 61,440 1.17 s; peak memory
  1,260 MiB at 2k up to 10,474 MiB at 61,440 tokens.
- A 15-token question answered from a copy of the saved state: median 0.0372 s after 16,384 tokens and 0.0456 s after
  61,440 tokens (the first 16k call, 9.6 s, includes a compile).
- Prefix-then-suffix against one whole forward: the same argmax; the largest logit difference 0.1875 (bf16).
$ find /root/.claude/projects/-home-user -name '*.jsonl' | wc -l; du -sh /root/.claude/projects/-home-user
296
1.3G	/root/.claude/projects/-home-user
```

Questions for you, not facts: the median session length in tokens between compactions (MOJEV measured about 787k; re-measure or
cite); whether the harness exposes the transcript path to a hook, so a live reader could tail it; which hooks have a timeout short
enough to rule out a PC round trip.
