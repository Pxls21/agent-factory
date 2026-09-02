# output-styles — provenance

Vendored 2026-08-10 (owner request) from https://github.com/alexgreensh/attention-span
(v0.3, main @ vendoring date, 157 stars, AGPL-3.0 — license applies to these three .md
files; private in-repo use with attribution, do not redistribute without the license).

Three Claude Code output styles (chat formatting only, `keep-coding-instructions: true`):
- **attention-kind.md** — answer-first, bold-scannable, plain English (the default pick).
- **spartan.md** — same skeleton, zero warmth, maximum compression.
- **rundown.md** — TL;DR briefing format with status checkboxes.

Install (setup.sh does this every session): copy to `~/.claude/output-styles/`.
Activate: `/output-style Attention-kind` in-session, or `"outputStyle": "Attention-kind"`
in settings.json. Relationship to house rules: these govern chat FORMAT; CLAUDE.md's
honey levers + the STE100 writing rule govern content density. They compose — answer
first, short sentences, bold the load-bearing terms, length only where the work is the
deliverable.
