# PC lane — T93 (EVIDENCE ONLY: why 43 % of the local Qwen calls are chat-template 400s — the two refused request shapes, who produces each, and the fix seam; no repair in this lane)

PIN: a58a1b9

Role: evidence-gatherer (the EXPLORE role: exhaustive, file:line-cited, git-dated evidence tables; NO verdict, NO fix — the
coordinator decides). Route: the research route (`agentfactory-research`, cloud; state the route in the report header, claim
nothing about which model produced it). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Honey mode: full (line-bounded
findings, evidence anchors, SOLID/UNSURE). Keep your context small: bounded terminal output (`| tail -n 40`), the report drafted
after each item; never print a request body whole — print ROLE SEQUENCES and bounded excerpts (≤ 120 chars) only.

AUTHORIZATION: read-only forensics on the owner's own OmniRoute call-log artifacts and the pinned Hermes source. NOTHING is
changed: no OmniRoute setting, combo, node or connection; no Hermes profile file; no vLLM container or chat template; no server
restart. Every command is a read (`sqlite3 -readonly 'file:…?mode=ro'`, `python3` readers, `grep -n`, `sed -n`). Secrets: the
artifacts carry no API keys, but redact any `sk-…` or `Bearer …` token you meet (`sed -E 's/(sk-[A-Za-z0-9_-]{6})[A-Za-z0-9_-]+/\1<redacted>/g'`)
and never print `~/.hermes/profiles/agentfactory/.env` or any `*.env`. The prompt CONTENT of other lanes is theirs: cite shapes,
lengths and the first 80 characters of a system message only.

## THE CONTRACT — an evidence table answering FOUR questions, each row SOLID or UNSURE with its primary source

Q1 SHAPE: for today's local 400s (UTC 2026-09-22), the exact message-role shapes behind `[400]: System message must be at the
   beginning.` and `[400]: No user query found in messages.`, their counts, and the FIRST producer of each shape.
Q2 ORIGIN of the `<context_handoff>` system message at index 0 (OmniRoute's context-handoff feature — the `context_handoffs`
   table, the combo's `context_cache_protection`, the handoff injection code in the built OmniRoute) and of the NO-system-message
   requests (Hermes's own request builder: which code path sends messages without the system prompt — compaction, a summarizer
   call, a tool-continuation, `codex_responses` vs `chat_completions` wire mode).
Q3 THE TEMPLATE RULE: the exact lines of the Qwen3.8 chat template the vLLM container serves (the model's tokenizer/chat
   template file inside the container image pinned in `upstream.lock.yaml`, or a `--chat-template` the unit passes) that raise
   the two texts, quoted with their file:line.
Q4 THE LOOP: whether a refused local turn falling through to the cloud step CAUSES the next local refusal (the handoff block
   is injected after a provider switch) — measured on session tags: the sequence local-400 → codex-200 → local-400 → codex-200
   and how long a session stays on the cloud once it starts.
Plus the FIX SEAMS (candidates only, no code): where each shape could be corrected — the Hermes request builder, the hook
adapter's `pre_llm_call`, an OmniRoute per-combo setting, the template — with the owner-authority each needs.

Boundary: READ-ONLY everywhere. Your only WRITE is the report `tasks/briefs/pc-t93-support/T93-evidence.md` (and the draft).

## PREMISE — MEASURED at authoring (2026-09-22 13:1xZ, read-only probes over the bridge; the PC clone at the PIN)

```
call_logs (sqlite3 -readonly 'file:/home/rocco/.omniroute-migrated/storage.sqlite?mode=ro'), provider like 'openai-compatible-chat-%', 2026-09-22T00:00Z..13:0xZ:
   status 200 ×1,096 · 400 ×828 · 401 ×28 · 499 ×27 · 504 ×20 · 502 ×1
   400 error_summary: 753 "[400]: System message must be at the beginning." · 75 "[400]: No user query found in messages."
   every 400 row: api_key_name=hermes, requested_model=qwen-local/qwen3.8-27b-local, has_request_body=1, artifact_relpath set (830/830)
   hourly (200|400): 00 83|0 · 01 111|10 · 02 87|107 · 03 83|99 · 04 94|95 · 05 66|53 · 06 74|15 · 07 72|10 · 08 96|34 · 09 85|146 · 10 77|201 · 11 68|24 · 12 100|34
artifacts: /home/rocco/.omniroute-migrated/call_logs/2026-09-22/<ts>_<id>.json — keys error, pipeline (only {error:{_omniroute_truncated, reason}}), requestBody, responseBody, schemaVersion, summary
census of the 830 refused requestBody message lists (role sequence; sys@ = indexes of system messages; first = messages[0] kind):
   372  system-first  sys@[0,1] first=<context_handoff> last=tool n_user=1     e.g. 2026-09-22T02-03-01.425Z_1790042581248-412011
   292  system-first  sys@[]    first=plain(no system at all) last=tool n_user=0  e.g. 2026-09-22T02-19-47.828Z_1790043587647-fec86c
    54  system-first  sys@[]    last=tool n_user=1
    49  no-user-query sys@[]    last=tool n_user=0
    25  system-first  sys@[0,1] first=<context_handoff> last=tool n_user=2
    24  no-user-query sys@[0,1] last=tool n_user=0
   (12 more rows ≤ 2 each)  → two mechanisms: A) TWO system messages, the OmniRoute <context_handoff> block ("<transfer_reason>Model routing: …", 2,724 chars) BEFORE Hermes's own 65,566-char system prompt (sample 1790082019402-dda235, 48 messages);  B) NO system message and mostly NO user message (only assistant/tool turns)
request_detail_logs: NO rows for these calls (client_request/translated_request unavailable — detail logging off for them)
context_handoffs: 55 rows today (columns: id session_id combo_name from_account summary key_decisions task_progress active_entities message_count model warning_threshold_pct generated_at expires_at created_at last_model)
the loop, one session tag (conv_ed17b0fa…): 02:19:29 codex 200 → 02:19:31 local 400 (System message…) → 02:19:43 codex 200 → 02:19:47 local 400 (no system) → … a 2-15 s cadence
Hermes pin: hermes-agent 0.21.0 @ 527da60844d4dced37879ea50259675371abe10e (upstream.lock.yaml:10-15); the PC lanes run the owner's Hermes CLI (`hermes -z`), profile agentfactory, wire mode chat_completions (ADR 0002)
the local server: the vLLM `qwen` container (deploy/qwen.container, D-032), model qwen3.8-27b-local served through OmniRoute node qwen-local; the combos agentfactory-build-local / -verify-local = local first, then the cloud chain (HYBRID, D-039)
```

## ITEMS

1. **Re-measure the premise** (the status counts, the two error texts, the census — your own script over the artifacts; paste
   its output) under `## PREMISE — RE-MEASURED`. A materially different census is a FINDING, not a stop.

2. **Q1 — the shapes, exhaustively.** Extend the census: for each refused request, the role sequence compressed (`S H U A T T A T…`
   with H = a `<context_handoff>` system message), the number of messages, the total content chars, the combo step id, the
   session tag, whether the PREVIOUS call on the same tag was a cloud 200 (Q4). Group by shape; cite three artifact ids per
   group. Then the SAME census over today's local 200s — the shapes that SUCCEED (a control: does any 200 carry two system
   messages? does any 200 lack a user message?).

3. **Q2 — origins.** (a) The handoff block: find in the built OmniRoute (`/home/rocco/.omniroute-migration-npm/node_modules/omniroute/dist/.build/next/server`,
   minified — bounded `grep -o '.{80}context_handoff.{80}'`) where `<context_handoff>` is composed and WHERE in the message list it
   is inserted, and what triggers it (a provider/model switch? `context_cache_protection`? a threshold `warning_threshold_pct`?);
   join `context_handoffs.generated_at` against the refused calls' timestamps on the same session_id. (b) The no-system requests:
   in the pinned Hermes source (the profile's runtime — locate it with `hermes --version` and `python3 -c 'import hermes,sys;print(hermes.__file__)'`
   from the profile's venv, read-only), find every code path that builds a chat request WITHOUT the system prompt (compaction /
   summarization / tool-continuation / the `codex_responses` translation) and cite file:line; match each to a shape from item 2.
   (c) The hook adapter (`harness-ports/bin/hermes-hook-adapter.py`, `pre_llm_call` inject) — does it ever add or reorder a
   system message? Cite the lines.

4. **Q3 — the template rule.** From the container image pinned in `upstream.lock.yaml` / `deploy/qwen.container` (read-only:
   `podman inspect`, `podman run --rm --entrypoint cat <image> <path>` is a READ — allowed; never `podman exec` into the live
   container, never restart it), quote the chat-template lines that raise "System message must be at the beginning" and "No user
   query found in messages" with file:line; state what the template ACCEPTS (exactly one system message at index 0? a user
   message required? tool messages allowed after assistant only?).

5. **Q4 — the loop, measured.** Over today's session tags: for each tag, the sequence of (provider, status) in time; count the
   local-400 → cloud-200 → local-400 chains; measure how many consecutive cloud turns follow the first fallback and whether a
   session ever returns to a local 200 without a new user message; state the share of today's cloud turns that a fixed template
   compatibility would have kept local (an UPPER bound, labelled as such).

6. **Fix seams (candidates, no code, no verdict):** for mechanism A and mechanism B, the seam(s) — with the file:line, what it
   would change, and WHO must authorize it (the owner for OmniRoute settings, the vLLM template or the Hermes profile; the
   coordinator for the hook adapter and the dispatcher). Name the cheapest seam that is entirely first-party.

7. **Report** `tasks/briefs/pc-t93-support/T93-evidence.md`: header (route caveat), PREMISE — RE-MEASURED, the evidence tables
   for Q1-Q4 (SOLID/UNSURE per row, primary source per row), the fix-seam table, DISCREPANCIES, NOT-DONE. Report lint:
   `python3 scripts/report_lint.py --min-refs 15 <report>` (bounded: three rounds, then paste). No commit, no push, no repair.
