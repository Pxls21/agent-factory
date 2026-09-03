# BRIEF — evidence search (role: researcher)
PIN: {PIN}

Read-only. No edits, no commits, no subagents, no outward actions. Web access: {WEB_ALLOWED: yes/no}.

QUESTION: {QUESTION}

Answer with EVIDENCE, not a verdict. Instruments, in order: `graft ask "<question>"` (and `graft skeleton <file>` for surfaces), `rg -n` for literal tokens, GitNexus (`node .gitnexus/run.cjs impact|query …`) when the question is about callers/blast radius, the pinned upstream sources named in `upstream.lock.yaml` when the question is about a dependency (clone at the pinned commit into `/tmp` if needed; never into the repo), the web only if allowed above (cite URL + retrieval date).

Report: an evidence table — claim · file:line (or URL+date) · the verbatim line(s) (short) · SOLID/UNSURE; then the instruments used with their exact commands; then every ABSENCE you assert with the exact search that found nothing; then open questions the evidence cannot settle. No recommendations unless the brief asks; the coordinator decides.
