# PC lane — K1 (the vendored-kit manifest: source, commit, license, tree digest per vendored tree)

PIN: be5cf35

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/kit-k1-vendored-manifest-source-commit-license-per-tree.md` — READ IT WHOLE and build items 1-7
in order. Your worktree IS `git archive be5cf35`. Save your report at `tasks/briefs/kit-support/K1-report.md` inside your tree,
draft after EACH item (the incremental rule), and return it whole as your final message.

Venue notes specific to this build:
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH for every pytest run; an absolute `--basetemp` under your lane's scratch dir.
- The vendored trees are large (`.claude/` carries 372 skills; `sandbox-kit/` carries vendored tools): walk them ONCE per run,
  never read them whole into your context — the script reads bytes, you read the script.
- Never edit a vendored file; a provenance line you cannot resolve is a DISCREPANCY row in the report, not a guess.
