---
name: ouroboros-stdio
description: Driving the Ouroboros interview and seed tools through the stdio client scripts/ooo_mcp.py, with every measured quirk (moved verbatim from CLAUDE.md by CTX1, D-089), covering IS_SANDBOX=1, the initial_context cap that poisons a session, the Synapse fan-out submission and the exact data_context contract (the no_evidence_reason enum), rejected metacharacters and words, nothing retained between partial submissions, the exact resume shape, ouroboros_generate_seed writing no file, the broken native MCP server and its uvx fallback, patch_ouroboros.py. Load before any Ouroboros interview round, fan-out submission, resume or seed generation. Append each new Ouroboros quirk here the moment it bites.
---

# Ouroboros through the stdio client

CLAUDE.md was shortened losslessly (the owner, D-089, 2026-09-25): the text below left it VERBATIM, and CLAUDE.md points
here. Setup and the two idempotent upstream patches: `sandbox-kit/OUROBOROS-SETUP.md`.

**Ouroboros** — 3-tier fallback (MCP → stdio `scripts/ooo_mcp.py` → CLI `ouroboros`). **Always
prefer stdio** (`python scripts/ooo_mcp.py` — full MCP tool surface as JSON-RPC, no permission
gates; MCP tools hang on permission prompts when the user is away, the sandbox times out, and
in-flight requests are lost). **Stdio quoting:** shell expansion corrupts curly-brace JSON — write
it to a temp file: `JSONARG=$(cat /path/args.json) && python scripts/ooo_mcp.py tool_name
"$JSONARG"`. The interview tool starts with `initial_context` (not `topic`/`context`) and resumes
with `session_id` + `answer`.
**Ouroboros stdio quirks (hit 2026-09-02, all reproduced):** every `scripts/ooo_mcp.py` call that
drives the interview/seed backend needs `IS_SANDBOX=1` exported (the nested claude refuses
root+bypassPermissions; symptom: a question-less "cannot complete yet" reply) · `initial_context`
is capped (~1.5k chars) and an oversized one POISONS the session for every later round — start a
fresh interview and push detail through answers · each question issues a Synapse fan-out: submit
`{session_id, fanout_id, correlation_key:"context.lane_id", results:[{key, content}|{key,
undispatched:true}]}` covering the required lanes; `data_context` must match its contract exactly
(`{question_identity, lane_id, data_needed:false, no_evidence_reason, read_requests:[]}`) and the
`question_identity` lives in `~/.ouroboros/data/fanout/<fanout_id>.json` (`no_evidence_reason` is an ENUM, `not_a_measurement` / `answer_would_not_be_an_aggregate` / `question_too_ambiguous_to_measure` / `no_data_store_described` / `store_described_but_not_callable`, and data_context's `content` is the object itself, never a JSON string; bit twice 2026-09-25) (read the registry
file — `ls -t` over tool-result files picked a stale one) · string values are rejected on shell
metacharacters (`;` `|` `&` backticks `$`) and certain WORDS ("subprocess" → "Potentially
dangerous input"; paraphrase) — scrub before submitting · nothing is retained between partial
submissions — resubmit every lane · `ouroboros_generate_seed` returns YAML and writes NO file —
transcribe to `seeds/` immediately and run the seed's own `verify_command`s (a red first pass is
the gate working: ours caught a missing per-proof section).
**Resume uses the EXACT documented
arg shape** `{session_id, last_question, answer, ambiguity_score}` (the server also writes its artifact store into the PROJECT cwd, `.ouroboros/artifacts/artifacts.db` + WAL, on every interview call — gitignored since 2026-09-22, never committed) — a bare `{session_id,
answer}` resume and the `ouroboros_session_status` tool both report "No events found" even when
the session file exists under `~/.ouroboros/data/` (status reads a different store). Interview
rounds can take >3 min — run them as background Bash. **`ouroboros mcp serve` is broken in the
installed tool env** (MCP-SDK v2 vs the claude-sdk extra's v1.x — the user-scope MCP registration
shows CONNECTION_CLOSED every session); `scripts/ooo_mcp.py` auto-falls-back to an isolated
`uvx --from 'ouroboros-ai[mcp]'` server on that signature — expect the native attempt to fail
first (one stderr line): that is the fallback working. `scripts/patch_ouroboros.py` (run with the
ooo tool interpreter; setup.sh does it) applies the two idempotent upstream patches
(`sandbox-kit/OUROBOROS-SETUP.md`).
