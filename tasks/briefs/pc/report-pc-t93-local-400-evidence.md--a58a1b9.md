EVIDENCE COMPLETE, NO VERDICT.

Report:
tasks/briefs/pc-t93-support/T93-evidence.md

Absolute path:
/home/rocco/agent-factory/.lanes/pc-t93-local-400-evidence.md--a58a1b9/tree/tasks/briefs/pc-t93-support/T93-evidence.md

Key evidence at the fixed 13:21Z cutoff:

- 866 local Qwen 400s: 780 system-placement errors and 86 no-user errors.
- 422 complete rejected requests begin H S, with OmniRoute’s handoff system before Hermes’s system prompt.
- 416 rejected artifacts omit their request heads due to log truncation. Their exact shapes and first producers remain unknown.
- 26 complete no-user refusals contain OmniRoute compression-generated system rows.
- Qwen’s template requires any system message at index 0 and at least one real user query.
- 783 adjacent local-400 → cloud-200 → local-400 → cloud-200 chains occurred across 55 session tags.
- 92.93% is recorded only as an upper bound on cloud turns that template compatibility might have kept local.
- The active Hermes runtime is 0.21.1 at b3399c1, not the repository’s pinned 0.21.0 at 527da60.
- No repair, configuration edit, restart, live-container exec, model request, commit, or push occurred.

Verification:

report_lint: 29 refs — OK 26, NEAR 3, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)

SHA-256:
68bee04ddf7bda71ef58d12a5ecd6b81aa46b618fe27315277c5b1bd185fc0cc

The only worktree addition is tasks/briefs/pc-t93-support/T93-evidence.md. The report remains evidence for coordinator review, not a gate verdict.

🌱 graft saved approximately 2,544 tokens this turn.

⚠️ File-mutation verifier: 1 file(s) were NOT modified this turn despite any wording above that may suggest otherwise. Run `git status` or `read_file` to confirm.
  • `tasks/briefs/pc-t93-support/T93-evidence.md` — [patch] Failed to read file: `/home/rocco/.hermes/hermes-agent/tasks/briefs/pc-t93-support/T93-evidence.md`
