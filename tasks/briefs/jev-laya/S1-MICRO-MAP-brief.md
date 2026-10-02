# S1-MICRO-MAP (task #467, step 1): where a few generated tokens would serve System 1, and how the layers stack

Role: evidence-gatherer (sandbox, Opus 5.5). PIN: d2408a84 (the origin head at authoring; full id in the premise).
Read-only: touch NO tracked file. Report: your FINAL MESSAGE is the report, whole (the harness may refuse a subagent's
Write of a report file; never route around a refusal). The coordinator saves it as
`docs/research/findings/s1-micro/S1-MICRO-MAP-evidence.md`. Do NOT spawn subagents.

## WHY

D-133 (`docs/08_DECISION_LOG.md`, the owner's three messages of 2026-10-02 06:06Z to 06:33Z): the RWKV decision model
(D-126, D-127) may also emit a few tokens. It is hybrid: most decisions stay plain choices inside about 40 ms, and a
few generated tokens are spent only when a form has a free slot. The owner's first example is a label call with its
slots filled, so one label can take more cases and more kinds of tools than a fixed script. The owner then said that
is ONE use case: "This could be used in many other places ... how we can actually leverage this one tiny feature on top
of everything else and how to properly stack it with everything else."

The standing principle is "Jev finds, deterministic code blocks"
(`docs/research/findings/JEV-LEVERAGE-AUDIT-2026-09-24.md` section 3). The measured speed bounds the design: RWKV-7
0.4B generates 46.0 to 47.7 tokens a second on 3 sandbox threads (llama.cpp, 8-bit;
`docs/research/findings/s1-train/RWKV-CPU-2026-10-01.md`), about 21 ms a token, so 40 ms holds about two generated
tokens there.

Your job is the EVIDENCE for that map. The coordinator writes the design from it.

## THE COORDINATOR'S COUNTS (from this session's transcripts, which you never read)

Measured 2026-10-02 06:0xZ to 06:2xZ over every transcript of this session (2026-09-02 to 2026-10-02; counts only):

```
tool calls 72,373 (main thread 30,085, subagents 42,288); Bash 57,943 (80.1%), Edit 4,529, Read 3,692, Write 1,730
Bash calls that ran a label (scripts/stack.py): 730 (1.3% of Bash)
Bash command shapes (paths, numbers, hex ids and quoted strings replaced): 46,518 distinct; 24.1% of commands repeat a shape
Bash calls by kind (the first command after a leading cd):
  27.0% other (compound commands no rule below caught)
  14.9% read: sed -n / head / tail / cat
  11.9% tests: pytest, test_summary.sh, lane_gate.sh
  11.5% search: grep / rg / find
   8.6% PC bridge: pc.sh, pc_lane.sh, pc_suite.sh
   5.8% echo / date / printf
   5.6% git (and safe_commit.sh, push_clean.sh)
   5.1% write a file: cat >, tee, sed -i
   5.0% list and size: ls / wc / stat / du
   1.6% another repo script
   1.3% a label
   1.1% inline python
   0.6% wait
```

## WHAT TO MAP (evidence tables; each row cites file:line and the file's last commit date)

**T1. The System-1 decision points.** Every place in the tree where a hook, a Jev script or a planned System-1 head
decides, today or as a registered task plans it. Per row: file:line; the trigger (a hook event, a call); the input state;
the output today (a class among N, a score, keep or drop, or nothing yet); the consumer; the latency budget it runs
under (the hook's timeout value, where one is set); and whether it sits inside a gate or a predicate (KC-J1: no model
there). Start from `.claude/hooks/`, `scripts/jev*.py`, `scripts/s1_*.py`, `scripts/s1_train/`, `scripts/filepacks.py`,
`scripts/jev_pipes/`, `scripts/jev_trim/`, `vendor/jev-pruner/`, `harness-ports/bin/jev-pruner-setup.sh`, the leverage
audit's sections 5 to 7, and the ledger's open System-1 and Jev tasks (`todo/BUILD-TASKLIST.md`; among them #441, #448,
#346, #352, #406, #436, #295 and #318).

**T2. The free-text slots.** For each T1 row: the value that is typed by hand today, hard-coded, or missing, and that a
few tokens could supply (a query, a path, a pattern, a short reason, a summary marker). Give an example from the code
or the docs, never from a transcript.

**T3. The label registry.** Per label in `scripts/stacks.toml`, per parameter: its declared type, and which class its
values belong to: (a) a closed set; (b) a reference to something an earlier event in the stream names (a file just
edited, an agent id just dispatched, a run id just printed); (c) free text. Count each class. Also list what the label
notes and docs say a label cannot take today (a case, an option, a kind of tool).

**T4. The kinds without a label.** For each kind in the counts above that no label covers: the existing scripts that come
closest (file:line), and the slot values a form for that kind would need, classed as in T3.

**T5. The layers, located.** For each layer, what exists (file:line) and what does not: (1) the state stream (the render
and the view, `scripts/s1_train/`); (2) the choice heads (task #441); (3) a micro-output head; (4) deterministic
expansion and checks (where `scripts/stack.py` checks a parameter's value, file:line); (5) the runner and the policy
hooks; (6) the feedback signals (`S1-RATE`, `scripts/s1_scores.py`, the stack ratings).

**T6. Instruments for a constrained output.** What the tree and the RWKV-CPU findings record about the llama.cpp build
they used (path, version); whether that build's command-line tool or server takes a grammar (run its `--help` if the
binary is on this machine; never download anything); the same for the BlinkDL `rwkv` package's sampling code if it is
installed (read its source).

## STANDING RULES

- Read-only. Touch no tracked file; never commit, stash, checkout or reset in `/home/user/agent-factory`.
- Never read `.jev/`, `/root/.codiv/`, `.pc-bridge.env`, any `*.env`, the pseudonym key under
  `/root/.config/session-export/`, any real export, or a real transcript under `/root/.claude/projects/`. In the session
  scratchpad, read nothing outside a directory you create there.
- No network, no PC bridge, no subagents, no background jobs. Never `cd` at a command's top level (wrap it:
  `( cd <dir> && ... )`).
- Evidence only: facts with file:line and the last commit date (`git log -1 --format=%cs -- <file>`), and where you
  looked when you found nothing. No root causes, verdicts, designs or fixes.
- Your final message is the report: the six tables, then what you could not find, then what you did NOT do.

## PREMISE — MEASURED at authoring (2026-10-02 06:4xZ, /home/user/agent-factory@d2408a84)

Re-run each command at your HEAD; its output must match. On a difference, stop and report it.

```
$ git rev-parse --verify d2408a84^{commit}
d2408a84c84861b779a24dc35436730cff8a3cd1
$ git merge-base --is-ancestor d2408a84 HEAD && echo the PIN is an ancestor of HEAD
the PIN is an ancestor of HEAD
$ git ls-files docs/research/findings/JEV-LEVERAGE-AUDIT-2026-09-24.md docs/research/findings/JEV-LEVERAGE-EVIDENCE-2026-09-24.md docs/research/findings/s1-train/RWKV-CPU-2026-10-01.md scripts/stacks.toml scripts/stack.py scripts/filepacks.py scripts/s1_scores.py vendor/jev-pruner/.claude-plugin/marketplace.json harness-ports/bin/jev-pruner-setup.sh | wc -l
9
$ git ls-files .claude/hooks | grep -v __pycache__ | wc -l
8
$ grep -c '^| D-133 ' docs/08_DECISION_LOG.md
1
$ grep -c -E '^\[stacks\.[a-z0-9-]+\]$' scripts/stacks.toml
14
$ grep -n '^## 3\. The principle' docs/research/findings/JEV-LEVERAGE-AUDIT-2026-09-24.md
42:## 3. The principle: Jev finds, deterministic code blocks
$ grep -n -E '^\| RWKV-7, llama.cpp Q8_0' docs/research/findings/s1-train/RWKV-CPU-2026-10-01.md
85:| RWKV-7, llama.cpp Q8_0 (first run) | 353 | 322 | 331 | 46.0 |
87:| RWKV-7, llama.cpp Q8_0 (again, after Laya) | 322 | 330 | 341 | 47.7 |
```
