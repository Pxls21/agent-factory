# Lane O5 — S0-03 round-trip conjunct realign to the REAL ACP tool_call shape

**Authorization.** Defensive verification work on the owner's own OmniRoute/Hermes system. You
edit sandbox tooling + tests + fixtures only.

**PIN:** current HEAD of `claude/soundbox-kit-migration-iz1jwf` (commit `cf8d59c` or later — it
carries the spec). **Do NOT** run any live capture, touch the PC bridge, mint any artifact, edit
`blocked.json`/`result.json`/registry/ledger/`todo/BUILD-TASKLIST.md`, or take any outward action —
the coordinator re-captures + mints after this. **Do NOT commit** — leave the tree for the coordinator.

## The spec is written — READ IT FIRST
`proofs/S0-03/LIVE-CAPTURE-FINDINGS.md` §"Blocker 3" is the authoritative spec. It carries the REAL
ACP `tool_call` golden shape (from the live leg-B timeline) and the exact fix. The O4 realign fixed
the `call_logs` bindings and gated green — but the first LIVE re-capture crashed and would have
red-ed the checker because the round-trip parsing (conjunct iv + the runner's AF-AP-100 assertion)
was built from a FICTIONAL tool_call shape. This lane fixes the round-trip layer.

## The REAL tool_call golden shape (AF-AP-101 — pin the real shape, do NOT invent one)
```json
{"sessionUpdate":"tool_call","kind":"execute","locations":[],
 "title":"terminal: printf 3ee033173c9eafc2",
 "content":[{"content":{"text":"$ printf 3ee033173c9eafc2","type":"text"},"type":"content"}],
 "toolCallId":"tc-8d38ea4c7025"}
```
completion:
```json
{"sessionUpdate":"tool_call_update","kind":"execute","status":"completed",
 "content":[{"content":{"text":"terminal result\n- **output:** 3ee033173c9eafc2\n- **exit_code:** 0","type":"text"},"type":"content"}],
 "toolCallId":"tc-8d38ea4c7025"}
```
KEY: `content` is a LIST of blocks; the command is in the top-level `title`
(`terminal: printf <nonce>`) AND in `content[].content.text` (`$ printf <nonce>`); there is **NO
`rawInput`**. (The round trip also emits a SECOND tool_call for `buzz messages send …` that FAILS —
your bind must isolate the `printf <nonce>` execute call, not that one.)

## The changes (one atomic increment; sandbox tests green at the end)

### 1. `proofs/S0-03/tools/pc/run_s0_03_legs.sh` (the AF-AP-100 assertion, ~:244-273)
- Line ~256 crashes: `update.get("content", {}).get("title", "")` — `content` is a list. Read the
  command from `update.get("title", "")` (a `terminal: printf <nonce>` string) and/or from the
  content blocks (`content[].content.text` = `$ printf <nonce>`). The assertion must still require:
  a tool_call whose command contains `printf <nonce>`, kind=execute, reaching a
  `tool_call_update status=completed` with the same `toolCallId`, AND the agent's final message text
  contains the nonce. Keep every process-safety rule (kill by pidfile only; no name-matching killers —
  `tests/test_s0_03_omniroute.py` asserts their absence over the whole file).

### 2. `proofs/S0-03/check_omniroute_roundtrip.py` `check_roundtrip` (~:646-700)
- It requires `update["rawInput"]["command"] in expected_commands` (~:671-677). The real tool_call
  has NO `rawInput`. Rebind: an execute `tool_call` (`kind == "execute"`, a `toolCallId` str) whose
  command — parsed from `title` (strip the `terminal: ` prefix) OR from `content[].content.text`
  (strip a leading `$ `) — is in the expected set `{printf <nonce>, printf '<nonce>', printf "<nonce>"}`;
  exactly ONE such call (the printf one, not the buzz-send one); then a later `tool_call_update`
  `status == completed` with the same `toolCallId` whose content-text contains the nonce (the tool
  output). Keep the "exactly one prompt", "nonce in the prompt frame", and the completed-after-start
  ordering. Update the `_REASONS` strings to match.

### 3. `proofs/S0-03/fixtures/**/hermes/timeline.jsonl`
- Regenerate the tool_call + tool_call_update frames in EVERY fixture that has a hermes leg
  (the passing `evidence-provider-key-present`, `evidence-stub-route`, and each `hostile-*` bundle
  that carries a timeline) to the REAL shape above (content list + title, no rawInput). Keep each
  hostile bundle's specific defect intact. The passing fixture's printf tool_call must carry the
  real shape and the nonce in title + content + the completed output.
- If any hostile bundle keyed its red on the OLD tool_call shape, re-key it on the real one so it
  still reds for its stated reason (AF-AP-36 — RUN each red-then-green).

## Gate (paste verbatim; do NOT mint)
- `bash scripts/test_summary.sh tests/test_s0_03_omniroute.py` TWICE — identical counts; paste both.
- Run `proofs/S0-03/check_omniroute_roundtrip.py` on the passing fixture (rc 0) and on one hostile
  bundle (rc≠0 with the reason) — paste both.
- `python3 scripts/report_lint.py` on your report.
- Report DATA: files:lines, the pasted counts, each hostile red→green, and any NOT-done.

## Boundary (exactly these)
`proofs/S0-03/tools/pc/run_s0_03_legs.sh`, `proofs/S0-03/check_omniroute_roundtrip.py`,
`tests/test_s0_03_omniroute.py` (only if a test encodes the old tool_call shape),
`proofs/S0-03/fixtures/**`. Nothing else. NO live capture, NO mint, NO commit, NO outward action.
If a premise is wrong (a shape that does not reproduce), STOP and report rather than inventing.
