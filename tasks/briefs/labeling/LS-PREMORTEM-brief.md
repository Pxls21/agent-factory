# LS-PREMORTEM: attack the labeling output style design before it is built (task #339)

Authored 2026-09-28 14:1xZ by the coordinator. Lane: sandbox `adversarial-verifier` (Opus 5.5), premortem mode:
assume it is 2026-10-12, LS was built exactly as designed, and it failed or did harm. Find how.

## Read first

- The design: `docs/research/findings/labeling/LS-DESIGN-2026-09-28.md` (the thing under attack).
- The evidence it rests on: `tasks/briefs/labeling/LS-AUDIT-report.md` (the Jev families, the S1-RATE plumbing, the hook
  contracts quoted from the harness docs, the three owner repos).
- The owner's rulings: `docs/08_DECISION_LOG.md` rows D-100 and D-101.
- The live code the design builds on: `scripts/hook_context.py`, `scripts/s1_scores.py`,
  `.claude/hooks/turn-retro-gate.sh`, `.claude/settings.json`, `scripts/install_session_hooks.py`,
  `/root/.claude/stop-hook-git-check.sh` (read-only), and the harness docs copy
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ls-audit/hooks.md`.

## What to attack (report EVERYTHING you find; no severity filter; rank at the end)

1. **The request loop.** Several Stop hooks at once (ls-exec, the retro gate, the git check): what does the harness do
   with two exit-2 hooks, and in which order? The 8-continuation cap. `stop_hook_active`. A REQ in a message that also
   triggers the git check. A subagent's stop (SubagentStop) and lanes. Hook timeouts (the docs and the binary disagree:
   AUDIT §6 item 3).
2. **Safety.** Can a REQ run that the coordinator did not write in this turn (quoted text, a pasted report, a
   transcript digest, a subagent's text echoed into the final message)? Does the nonce design close that? Path
   traversal, symlinks and races in `book` targets; a `book` write while a lane holds the same file; the lossless and
   mirror gates; the stamp rule. Anything that lets text in the output reach a shell or an outward action.
3. **The labels.** Will the coordinator actually write them (the S1-RATE missing rate: AUDIT §2.1)? Selection bias,
   leakage of the answer into the state, labels written where the context is not (the SYNTH1 lesson), the D4-only rule
   and whether the family registry covers the owner's "about 20 instances".
4. **The offload.** Does `book` really save tool calls and tokens, or move them? The task-list view: what breaks if the
   in-session task list stops being mirrored by hand?
5. **The Read hook.** Recall risk on this repo's files; the goal source; the confidence overlap the jev bench found
   (AUDIT §5.1); what a silent miss costs.
6. **Anything the design omits** that the owner asked for in D-101.

Run cheap probes where they settle a claim (read-only commands, the binary's strings, a Python parse of a sample
message against a draft regex). Never edit a hook, a setting, or any file in the repo.

## Output

A premortem report: each failure mode with its mechanism, the evidence (file:line, a quote, or a probe you ran), how
likely and how bad, and the design change that prevents it. Then a GATE RECOMMENDATION on the design: PROCEED,
PROCEED-WITH-CHANGES (list them) or REDESIGN.

## Rules

- Read-only. No git writes, no PC bridge, no subagents, no outward-facing action. Do not change any hook or setting.
- Never read a secret source (`.pc-bridge.env`, any `*.env`, `/root/.codiv/`, `~/.config/qwen-*`,
  `/root/.config/session-export/`). Do not read session transcripts under `/root/.claude/projects/`.
- Work in `/home/user/i59-landing` (read-only); another lane edits seven files there.
- Scratch under 50 MB in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ls-premortem/`.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Return the whole report as your final message; the harness refuses subagent report files.

## PREMISE — MEASURED at authoring (2026-09-28 14:1xZ, the worktree at the design commit's parent)

```
$ wc -w docs/research/findings/labeling/LS-DESIGN-2026-09-28.md tasks/briefs/labeling/LS-AUDIT-report.md
1894 docs/research/findings/labeling/LS-DESIGN-2026-09-28.md
(the audit report: 66,832 bytes)
$ grep -n 'exit' .claude/hooks/turn-retro-gate.sh | tail -1
74:exit 2
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ls-audit/
hooks.md
```
