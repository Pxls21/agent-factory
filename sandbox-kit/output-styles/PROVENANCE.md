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

Local change (agent-factory, 2026-10-01, task #440; the owner's D-101 item 3 and D-123 step 3): each style ends with a
`## Labels` section (run a step as its stack label, name a repeated sequence in the retro, keep the machine lines apart
from the answer). The upstream text above it is unchanged. A session rooted above the repo (the cloud default,
`/home/user`) reads its settings there, so `scripts/install_session_hooks.py` sets the repo's `outputStyle` at that root
when the root sets none (task #440); before that, such a session loaded no output style (LS-AUDIT 3.2).
