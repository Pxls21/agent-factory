# Lane O3 — S0-03 round 3: the collector complete over the window (never a capped prefix), the credential screen recursive with the path named, the completed tool call bound to the exact terminal request and ordered after its start, `pid` validated and bound to the tee's record, aware timestamps required, POST on both rows (build lane: PC Hermes `code-implementer`; sandbox Opus 4.6 `code-implementer` only if the bridge is down)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".) Lane O2's landing is `d12fc13`
and every S0-03 file is unchanged since (VERIFY-O2's identity table: `check_omniroute_roundtrip.py` 824 lines blob `143bc57c…`,
`tools/pc/collect_leg.sh` 175 `dd441844…`, `tools/pc/hermes_env_names.py` 148 `80c70511…`, `tools/pc/run_s0_03_legs.sh` 313
`fddb1505…`, `tools/pc/direct_responses_probe.py` 285 `e4978382…`, `tests/test_s0_03_omniroute.py` 1734 `ca57bbd1…`). Line numbers
below are those bytes'.

**Why:** VERIFY-O2 (`tasks/briefs/s0-03-support/VERIFY-O2-report.md` — READ IT WHOLE FIRST; it is the contract for this round)
graded round 2 NOT-READY: the 48-case contract set is killed 48/48 and the parent's two red controls are closed, but six
compositions and hostile domains pass the checker, every one reproduced on scratch copies. **V-O2-1 BLOCKING** —
`collect_leg.sh:75,133-141`: the window query is `… WHERE requested_model = ? ORDER BY timestamp ASC LIMIT ?` (default
`S0_03_LOG_LIMIT=50`) and the window is filtered in Python AFTERWARDS; a real SQLite fixture with 49 earlier rows, the target row
and a foreign same-window row 51 exported ONE Hermes row and the checker PASSED — `len(grouped["hermes"]) == 1` (`C:509`) is a
hollow green (registry row **AF-AP-71**); the direct query (`:127-130`) carries the same cap. **V-O2-2 BLOCKING** — `C:680-685`
walks `block.items() + headers.items()` only: `providers.<x>.nested.api_key`, `providers.<x>.headers.Authorization: Bearer …` and
`extra_headers.Authorization: Basic …` each PASS. **V-O2-3 BLOCKING** — `C:614-641` accepts ANY `completed` tool call whose output
carries nonce2 (a `read_file` whose content quotes the nonce passes) and builds unordered sets, so a completion placed BEFORE its
start passes. **V-O2-4** — `hermes_env_names.py:128-141` writes `pid`; `C:728-734` reads only `exe`/`agent_realpath`
(`"not-a-pid"` passes). **V-O2-5** — `C:456-472`: `_instant` accepts a naive datetime and `_require_in_window` then raises
`TypeError` — a traceback, no `failure_reason`. **V-O2-6** — `C:542-546` reads `row.get("status")` and the path only: `GET /v1/responses` rows pass on
both legs. Also: the O2 report's `pc_launch.py:293-294` citation is a MISS (the line carries the regex `s0-01-\w+`, not the
described rewrite). What held and must stay held: `response_id` exact, `status` exactly 200, the exported window equal to the
recorded one, the window boundary instants (`T:1724-1734`, `test_a_row_at_either_window_edge_is_inside_it`), `/v1/chat/completions` and a trailing slash refused, the top-level
`api_key`/`Authorization`/`X-Api-Key` refused, `credential_rejected` an exit-1 RED, NaN/Infinity rejected, the route bound as a
query parameter, the runner's `--leg --model --profile` = the launcher's declared flags (`run_s0_03_legs.sh:197-199`, `"$LAUNCHER" --leg`),
`216 passed` on both venues.

**Inputs (read in this order):** VERIFY-O2 whole · the O2 brief and `tasks/briefs/s0-03-support/O2-report.md` · the vendored
ACP schema `proofs/S0-01/vendor/buzz-acp/acp.rs` (the `tool_call` / `tool_call_update` fields: `toolCallId`, `title`, `kind`,
`status`, `rawInput`, `content` — cite the lines) and the committed positive fixture's `hermes/timeline.jsonl` (the REAL shape a
terminal call has: which field carries the command) · `proofs/S0-01/tools/frame_tee.py` (the runtime-identity keys:
`agent_child_pid`) · `docs/INCIDENT-LOG.md` (AF-AP-15, AF-AP-40, AF-AP-65, **AF-AP-71**, AF-AP-72) · the pack
`scripts/lane_context.sh -q 'what selects the rows the identity check grades' -s check_identity_route check_roundtrip check_transport check_env_record _instant -o pack.md proofs/S0-03/check_omniroute_roundtrip.py`
(run it first; attach it).
**Scope (under S0-03 + its test + your report):** `proofs/S0-03/check_omniroute_roundtrip.py` · `proofs/S0-03/tools/pc/{collect_leg.sh, run_s0_03_legs.sh, hermes_env_names.py}`
· `proofs/S0-03/spec.json` (only if a failure key is enumerated there) · `proofs/S0-03/fixtures/**` (regenerated where an item
says) · `tests/test_s0_03_omniroute.py` · `tasks/briefs/s0-03-support/O2-report.md` (ONE stamp line, item 7) · report
`tasks/briefs/s0-03-support/O3-report.md`. NOT yours: `proofs/S0-01/*` (read-only; P5c, N5j, B5k and D5n are editing S0-01 in
their own trees), `direct_responses_probe.py` (unless an item needs it — say why), `proofs/registry.yaml`, `blocked.json`, the
ledger. Shared-tree rules: never `git stash/checkout/restore/reset/add/commit/push`; every gate from a `git archive <PIN> | tar -x`
copy under your lane's scratch dir with your files copied in (`scripts/lane_gate.sh -r <PIN> -f "<your files>" -t "tests/test_s0_03_omniroute.py tests/test_spec_probe_schemas.py tests/test_validate_ledger.py tests/test_proof_runner.py" -n 2`,
ONE foreground call, `LANE_GATE_DIR` under your scratch dir); explicit `--basetemp`; kill only your own processes by pid; NEVER
background a run and stop; no outward actions; NO request to OmniRoute or any model endpoint and NO Hermes/buzz-acp launch
(loopback servers and temporary SQLite files you create are the only sockets and databases); never read, print or commit a
credential. Venue exports `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`.
Authorization: the owner's own egress boundary under test; the forged bundles are defensive fixtures.

## Design (pinned — build it, do not redesign it)
1. **V-O2-1 — no query the checker grades is capped.** Delete `LIMIT` from BOTH queries and the `S0_03_LOG_LIMIT` knob (`:70`);
   the window query is bounded IN SQL by a one-second-widened prefix of the instants (`timestamp >= <start − 1 s as
   'YYYY-MM-DDTHH:MM:SS'>` and `timestamp < <end + 2 s …>` — both producers' stamps share those 19 characters, so the prefix bound
   is safe for either fractional precision) and then filtered EXACTLY as instants in Python as today; the direct query stays
   `WHERE requested_model = ? AND response_id = ?` with no cap. The export records `row_counts: {direct: N, hermes: M}` and
   `truncated: false` is NOT a field — there is nothing to truncate. Red tests (RED on the PIN — paste): the verifier's fixture
   (49 earlier rows + the target + a foreign same-window row 51 → BOTH rows exported and the checker says `identity_unattributable`);
   a duplicate direct row at position 51; the existing collector tests re-run (`T:1568-1690`).
2. **V-O2-2 — the screen walks the whole provider block.** `_walk_credentials(node, path)` over every mapping and list at any
   depth: `is_credential_name(key)` on every key (except `key_env` at EXACTLY the path `providers.<name>.key_env`); value shapes
   at any depth: `bearer `, `basic `, `sk-`/`sk_`, and any string ≥ 32 chars under a credential-named key; the failure names the
   full dotted path (`profile.yaml carries an inline credential under providers.x.headers.Authorization`). Red tests: the three
   verifier profiles + a list-nested one + a positive control with `key_env: OMNIROUTE_API_KEY` only.
3. **V-O2-3 — the round trip is THE terminal call, in order.** From the prompt frame derive the expected command
   (`printf <nonce2>`; accept the nonce bare or single/double-quoted, nothing else); among `tool_call` updates find the ONE whose
   kind is the terminal/execute kind under the ACP schema (cite `acp.rs`) and whose input carries exactly that command (the field
   the committed timeline uses — cite it; never a substring match over the serialized update); the `tool_call_update` with the
   SAME `toolCallId`, status `completed`, must have an index GREATER than the start's and carry nonce2 in its content; every
   other completed call is irrelevant; nonce2 in the final agent text stays. Red tests: the verifier's `read_file`-with-nonce
   mutant; the completion-before-start mutant; `printf other` plus an unrelated echo of the nonce; a positive control on the
   committed fixture. If the committed fixture's terminal call does not carry the command in a structured field, STOP and report
   it — do not weaken to substrings.
4. **V-O2-4 — `pid` validated and BOUND.** The runner writes `agent_child_pid` (from the tee's `runtime-identity.json`, which
   `run_s0_03_legs.sh:171` names and `:229` passes to `hermes_env_names.py` as `--runtime-identity`) into `hermes/leg.json`; `check_env_record` requires `record["pid"]` a strict positive
   int (not bool) and `== leg["agent_child_pid"]` (the same type rule; AF-AP-72: no `int()` coercion of either). Fixtures
   regenerated with both fields. Red tests: string, zero, negative, `True`, mismatch, `agent_child_pid` absent.
5. **V-O2-5 — aware instants only.** `_instant`: `parsed.tzinfo is None or parsed.utcoffset() is None` → `Failure("bundle: <name>
   is not an RFC3339 stamp with an offset (…)")`; normalise to UTC before comparing. Red tests: an offset-less row stamp, window
   start, window end (each the named failure, rc 1, no traceback); a `+02:00` positive control.
6. **V-O2-6 — the method is graded.** `row.get("method") != "POST"` → `_fail("transport_method", leg, method)` on both rows; if
   `spec.json` enumerates failure keys, add it there. Red tests: GET direct, GET hermes, lowercase `post`.
7. **The O2 report stamped**, one line at its top: `STAMP 2026-09-08 (O3): the pc_launch.py:293-294 citation is a MISS (VERIFY-O2 item 0).`
8. **Mutants:** the 48 core re-run and still dead; the six bypasses above now KILLED by name; VERIFY-O2's decision-irrelevant
   survivors (call-log `id`, compression headers, protocol metadata, direct usage) listed as such, unchanged.
9. **Report discipline:** FILE IDENTITY of the FINAL bytes; every `file:line` from `grep -n` on the FINAL bytes and
   `python3 scripts/report_lint.py <report> --rev <PIN> --map C=proofs/S0-03/check_omniroute_roundtrip.py --map T=tests/test_s0_03_omniroute.py --map P=proofs/S0-03/probe_omniroute.py --map collect=proofs/S0-03/tools/pc/collect_leg.sh --map env=proofs/S0-03/tools/pc/hermes_env_names.py --map run=proofs/S0-03/tools/pc/run_s0_03_legs.sh`
   pasted with MISS 0; the two gate RESULT lines; every red-before pasted beside its green-after; pyflakes + `bash -n`;
   `ap_screen.py` over the five S0-03 sources (AF-AP-71 = 0 hits — paste both runs); the pack attached; NOT-done first-class.
   NOT this lane's: the live legs A/B/negative, the EXPIRED→result flip, the remint (the coordinator's capture).
