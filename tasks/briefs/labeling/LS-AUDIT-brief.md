# LS-AUDIT: evidence for the labeling output style (task #339)

Authored 2026-09-28 13:3xZ by the coordinator. Lane: sandbox `evidence-gatherer` (Opus 5.5). You COLLECT evidence; you
do not conclude, recommend or design (the Reflection Firewall: verdicts stay in the main loop).

## WHY

The owner's direction (D-101, 2026-09-28): the chat output style becomes the labeling layer. Every action the coordinator
takes is written in the chat as a labeled request; Jev and scripts carry it out; the result comes back; the coordinator
rates it. The rated records become training data for every System-1 (Jev) use in the system; the owner counts about 20
such uses, each needing its own labels. Menial work (the task list, the ledger, the wiki, bookkeeping) moves to Jev and
scripts. The coordinator designs this from your evidence, so the evidence must be complete and cited.

## WHAT TO COLLECT (tables, each row with file:line and the git date of that line where it matters)

1. **The Jev instance inventory.** Every System-1 use in this repo: built, planned, or proposed. Sources to read in full:
   `docs/research/findings/JEV-LEVERAGE-AUDIT-2026-09-24.md`, `JEV-LEVERAGE-EVIDENCE-2026-09-24.md`,
   `RESEARCH-FINDINGS-2-part2-system-one-integration-map.md`, `JEV-LAYA-AUDIT-2026-09-22.md`, `MOJEV-AUDIT-2026-09-24.md`,
   the folders `docs/research/findings/jev-audit/`, `jev-pipes/`, `jev-fit/`, `laya-ft-*`, and the decision log rows
   D-046, D-047 and D-072 to D-100 (`docs/08_DECISION_LOG.md`). Find the list the owner calls "about 20 instances"; paste
   where it lives and its exact count. Per instance: a short name; the decision it makes and its question type (choice,
   score, yes/no); the state it reads; where it runs (hook, script, lane, planned); the label source today, if any; labels
   collected so far (count, file); the defining doc:line.
2. **The labeling and rating plumbing today.** The S1-RATE path end to end: the hook that stamps `[S1 <id> <source>]`
   (`.claude/hooks/system1-context.py`, `.claude/hooks/wiki-context.py`), the score request text, `scripts/s1_scores.py`
   (what it parses, from where, what it writes), the off switch `.jev/s1-rate-off`, and every other producer of labels or
   outcomes (verifier finding classes, registry citations, DATA-SESSION outcomes, the dsv2 exports, SYNTH1). Per producer:
   input, output file, record shape, count so far.
3. **The output styles.** `.claude/output-styles/` (attention-kind, rundown, spartan, PROVENANCE): what each prescribes,
   which is the project default and where that is set, and any existing rule about labels or typed lines.
4. **The hook surfaces.** Every hook in `.claude/settings.json`: event, matcher, command, what it reads, what it writes,
   what it prints back and how (additionalContext, `updatedInput`, exit code 2 with stderr). In particular: how
   `.claude/hooks/turn-retro-gate.sh` blocks a stop and feeds text back (its exit code and stream), and which fields
   the harness passes each hook event on stdin (the transcript path among them). Cite the harness's own documentation
   for the Stop and PreToolUse contracts (the Claude Code hooks reference, via WebFetch), with the URL and the quoted
   lines.
5. **Reusable parts in the owner's three repos** (cloned read-only; nothing installed or run):
   - `/home/user/borislemeec/jev` (e81c1d0): the Read hook (`internal/run/hook.go`, `locate.go`), every constant and the
     measurement behind it (`bench/`), its fail-open rules, what it sends to TypeSafe.
   - `/home/user/kerpopule/hermes-jev-skills` (89b073f): the skill-selection and web-screen code, and whether and how it
     logs decisions or outcomes for training (file:line).
   - `/home/user/kyu1204/jgrep` (c56119f): how it packs chunks and questions into one request, and its caching.

## RULES

- Read-only everywhere. No git writes, no PC bridge, no subagents, no outward-facing action. No code runs except read
  commands, `graft ask`, and the repo's read-only scripts.
- Never read a secret source (`.pc-bridge.env`, any `*.env`, `/root/.codiv/`, `~/.config/qwen-*`,
  `/root/.config/session-export/`). Do not read session transcripts (`/root/.claude/projects/`): the coordinator
  measures those itself.
- Cite every claim: file:line (or URL plus the quoted line). A claim you could not source is marked UNVERIFIED.
- Absence is a claim too: say which searches you ran (the command or the graft question) before writing "none".
- The disk is shared (about 1.6 GB free): scratch under 50 MB in
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ls-audit/`.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Return the whole evidence report as your final message (the harness refuses subagent report files; do not write one).

## PREMISE — MEASURED at authoring (2026-09-28 13:3xZ, the worktree `/home/user/i59-landing` at eab2988)

```
$ ls docs/research/findings/ | grep -i -E 'jev|map|pipe|system1|laya'
JEV-LAYA-AUDIT-2026-09-22.md
JEV-LEVERAGE-AUDIT-2026-09-24.md
JEV-LEVERAGE-EVIDENCE-2026-09-24.md
LAYA-PROBE-1.md
MOJEV-AUDIT-2026-09-24.md
PIJEV-ORDER-PROBE-1.md
RESEARCH-FINDINGS-2-part1-laya-sieve-fp32-build-spec.md
RESEARCH-FINDINGS-2-part2-system-one-integration-map.md
jev-audit
jev-fit
jev-locate-bench
jev-pipes
laya-ft-data
laya-ft-eval
laya-ft-labels
laya-probe-1-pc.json
laya-probe-1-sandbox-contended.json
laya-probe-1-sandbox.json
laya-train-timing
pijev-order-probe
$ ls .claude/output-styles/ .claude/hooks/
PROVENANCE.md attention-kind.md rundown.md spartan.md
edit-snapshot.py graft-first-nag.py search-intercept.py session-start.sh system1-context.py system1-situations.json
turn-retro-gate.sh wiki-context.py
$ grep -n 'exit' .claude/hooks/turn-retro-gate.sh | tail -1
74:exit 2
$ wc -l .claude/hooks/system1-context.py scripts/s1_scores.py
1061 .claude/hooks/system1-context.py
448 scripts/s1_scores.py
```

A question for you, not a fact: the owner's "about 20 instances" may be one list or the union of several. Report what the
sources hold.
