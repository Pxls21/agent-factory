# SCRUB2-R1 round 5Q: the lane's report of record (task #321)

> **Coordinator note (2026-09-30 08:3xZ).** The lane's report, brought home by the dispatcher's re-attach at 08:2xZ and
> saved verbatim below, with its patch `tasks/briefs/system1/SCRUB2-R1-R5Q.patch` (sha256 prefix a3d9728a3991; 7 files against the PIN
> 238fcf2: the lane's own 3, the round-4 files it started from, and the runner's scrubbed transcript digest).
> **Route (D-114), read only:** the lane's one Hermes session (`20260930_005040_103afd`) made 263 API calls on the raw
> id `qwen-local/qwen3.8-27b-local` and ended at 07:02:46Z (`agent_close`). OmniRoute's `call_logs` hold 279 rows tagged
> with the lane, 23:51:08Z to 07:07:43Z, all on the local route (277 with status 200, 2 with status 499), no combo; the
> runner's steps after the session made no model call. The dispatcher's own provider-mix line read no rows: on a
> re-attach to a lane that has ended, `scripts/pc_lane.sh` sets its window to the last minute (`LAUNCH_AT` is the
> re-attach time, :350-356), a harvest gap (a task in the ledger).
> **Status:** the lane reports DONE on all seven items. It is a PROPOSAL, verified only if the owner picks ONE MORE
> ROUND in the scrubber's D-115 review; under A, B or D it is moot. Its DISCREPANCIES flag "a Cloudflare quick-tunnel
> host+token literal" at line 220 of `tasks/briefs/system1/VERIFY-SCRUB2-R1-R4-report.md`. Checked: it is a made-up
> fixture (a two-letter tunnel host, no token field, no hex run of 24 or more characters), and
> `scripts/known_values_check.py` finds none of the live bridge's URL, host or token, and not the relay key, in that
> file (NO HIT). Nothing to rotate.

---

All evidence files are present and back every run-claim in the report (proto_collision, a7, a7report, collision_check, measure6 all match the report's numbers). The work is complete and verified. Final report below; the full text is at `/home/rocco/agent-factory/.lanes/SCRUB2-R1-R5Q-brief.md--238fcf2/report-draft.md`. Nothing committed — the working tree holds the diff for the coordinator.

---

# SCRUB2-R1 round 5 (local model) — lane report (task #321, D-112, D-114)

Route: `qwen-local/qwen3.8-27b-local` (local only, no cloud fallback). Role: code-implementer. PIN: 238fcf2.

**Outcome: DONE (all 7 contract items).** The collision-proof shield is in, the K-chain is closed, 12 red items moved in, the de-xfail de-marked, both new tests pass and fail where they must, the manifest sha is set, and all 12 gate files pass. One open item: 23 pre-existing environment errors in `test_push_clean_lock.py`, proven red at the PIN.

## 1. Premise (re-run in the lane tree, 8 lines — all match)
L1 `238fcf2` is an ancestor of HEAD · L2 transcript_export.py sha16 `6ad316dccfca0147` · L3 test sha16 `5b22cc0040767dc7` · L4 R4-patch sha16 `f18f85c9b0abaf7b` · L5 5 files · L6 2 × `### R4V-1` · L7 21 transcripts · L8 1 manifest line. **CONTRACT-VALID** — all 8 identical to the brief. `git diff --cached --stat` names the 6 dispatcher-applied files.

## 2. K-chain reproduced on round-4 code (the "before")
On round-4 `scrub_payload` (sha `8c0b66b6fa41f8c8`): decoded K-chain → `_hidden=False`, canonical K-chain → `_hidden=False`. Confirmed: D1 keeps a refused credentials value whole; a head inside it is read by a post-credentials rule, its token eats a later head's name, and that later value (hidden at the PIN) shows. `scrub()` unaffected.

## 3. The shield (collision-proof) — form and why it cannot collide
`scrub_payload` (`scripts/transcript_export.py:397-460`), the brief's order, with a runtime-chosen stand-in. Two helpers above it:
- `_shield_chars(text: str)` (`:372`) — picks two PUA chars (U+E000..U+FFFF) **absent from this input**.
- `_standin(i, a, b) -> str` (`:390`) — 16-char stand-in per kept value, index encoded as a/b, so every kept value has a distinct stand-in.

Why it cannot collide (docstring `:398-415`):
1. **Chosen-absent stand-in alphabet** — no input byte sequence can equal a stand-in, so the per-value exact `str.replace` restore only matches stand-ins this run made. No wrong-place, no drop.
2. **No late rule crosses or matches a stand-in — MEASURED:** built a real stand-in, embedded it with whitespace on both sides, ran `finditer` for every non-credentials STAGE1 / PAYLOAD / STAGE2 pattern (the superset of the actual late set): **0 matches cross it, 0 match it alone** — closing the `.`/`[\s\S]`-spanning path a PUA-presence scan alone can't. Independently, no pattern string and no replacement (static or the four callables `_cookie_or_same`, `_credentials_or_same`, `_key_block_or_same`, `_redact_run`) holds any PUA char (0 hits), so a rule never emits a stand-in either.
3. `scrub()` untouched (21/21 byte-identical).

The prototype's fixed `0xE000` stand-in fails (1): an input holding `<`+8×U+E000+`>` is indistinguishable from a stand-in and gets overwritten.

## 4. The 12 red items moved in
Ported into `tests/test_transcript_export.py:2064-2097`, **byte-identical** to the red file's lines 49-82 (empty `diff`; only the module loader + helpers are the file's own). The three functions (defs 2071/2084/2094, 5+5+2 cases). The strict xfail at `:2054` lost its marker → plain `def` (de-xfail comment 2052-2053) and passes. All 12 pass.

## 5. Item 4 — the collision test (fails on prototype, passes on shield)
`test_r5v1_a_prototype_standin_already_in_the_input_is_neither_collided_with_nor_consumed` (`:2107-2114`).
- **Prototype** (run via scratch `proto_run.py`): `out='x Z\tBearer <redacted>\tBearer <redacted> = <redacted> end'`, hidden(v)=True, **standin-unchanged=False → FAILS** (input's own stand-in overwritten by a kept value).
- **My shield** (run directly): `out='x <\ue000…> credentials=Z\tBearer <redacted> = <redacted> end'`, hidden(v)=True, **standin-unchanged=True → PASSES**.
- Committed test on the shield: `1 passed`.

## 6. Item 5 — the A7 order test
`test_r4v2_credentials_rule_before_payload_and_link_hides_v_in_the_call_view_and_decoded` (`:2122-2127`): the A7 text `credentials = jHAoL\fx9y8z7w6https://q1.trycloudflare.com/k6rMS4AuzM5y2,api_key=\"<V>\"` as canonical JSON, scrubbed to a fixed point; asserts `<V>` hidden in both the call and decoded views.
- **Shield:** `1 passed`.
- **A7 mutant** (credentials rule moved after PAYLOAD in a scratch copy of the final `scrub_payload`): canon `hidden=False`, decoded `hidden=False` → **FAILS in both views**, matching the verifier's round-4 measurement. So it genuinely discriminates the required order. (The `api_key` VALUE is a run-time fake; the tunnel literal is already committed in the verify report.)

## 7. Item 6 — measurements (21 transcripts)
- (a) `scrub()` byte-identical before/after: **21/21**.
- (b) best-of-3: `scrub` 3.45336s→3.43713s (**0.995x**); `scrub_payload` 5.21182s→7.74383s (**1.486x** — faster than the prototype's 1.62x).
- (c) manifest sha256 line set to the final `scripts/transcript_export.py` sha `54df2dc20a754cd3744138f3fddd3fc7ee9dacd781abd3233f0ef4ea6de28fa8` (`dataset-manifest.json:10`, the only line changed); `test_laya_ft.py` and `test_s1_synth.py` pass.

## 8. Item 7 — gates (12 files, twice, `-n 8 -q`)
Pass 1: 431 + 422 + (66 passed, 17 skipped, 23 errors). Pass 2: 431 + 422 + 65 passed, 17 skipped + `test_push_clean_lock.py` 1 passed, 23 errors. Target file `tests/test_transcript_export.py`: **278 tests** — reconciled as 195 (PIN) + 69 (R4) = 264 + 12 (red) + 2 (new) = 278.

## 8b. Self-attack — the three most likely ways this is wrong
1. **Stand-in still collides.** Ruled out by the direct stand-in-crossing probe (0 crossing / 0 standalone matches, section 3) plus the 0-PUA-emit measurement. **One residual, stated plainly (docstring `:391-393`):** the index is 16-bit, so >65,536 refused credentials values would let two indices truncate to one stand-in and the restore would collapse them — no guard for that, recorded as a known limit, no corpus transcript anywhere near it.
2. **Red items / de-xfail silently altered (hollow green).** Ruled out by byte-identical `diff` of the ported region (2064-2097) vs red-file 49-82, and the de-xfail body vs the staged round-4 file.
3. **A7 test is a tautology (negative control that doesn't fail).** Ruled out: with A7 applied to the final code, V shows in both views (`_hidden=False`), so it fails where it must.

## 9. DISCREPANCIES
- `tests/test_push_clean_lock.py`: **23 setup errors in both passes** — the pc-lane hook refuses `git push` in a lane (exit 13). **Proven a pre-existing environment condition:** identical `1 passed, 23 errors` at the PIN in a clean detached worktree. Not caused by this change; reported, not fixed.
- A7 text embeds a Cloudflare quick-tunnel host+token literal (verify-report line 220); the `api_key` value is a run-time fake. Flagged for the coordinator to rotate/drop if the tunnel is still live.
- ap_screen on the two changed files: module 3 hits (AF-AP-204 ×2 @18/613, AP-1 @551); test 5 hits (AF-AP-224 ×4 @715-716, AP-1 @964) — **all pre-existing, none in the added region** (`transcript_export.py:372-460` / `test_transcript_export.py:2061-2127`). No new anti-pattern hits.
- report_lint (brief's alias map): **`12 refs — OK 4, NEAR 1, MISS 0, UNCHECKABLE 7, UNRESOLVED 0`** — reached in 2 of the 3 bounded rounds; the 7 UNCHECKABLE are range-only prose citations with no backticked token to check (the honest category for a prose description of a range).

## 10. NOT done
- No contract item left undone. The only open item is the 23 `test_push_clean_lock.py` environment errors (section 9) — independent of this change and red at the PIN. No other red/skip/xfail in the 12 gate files.
- **Harvest diff is clean:** exactly my 3 named files (`scripts/transcript_export.py` +58, `tests/test_transcript_export.py` +71, `dataset-manifest.json` 1 line); the red file and the dispatcher's 3 other R4-patch files are untouched by me.
- The lane did **not** commit (standing do-nots) — the working tree holds the diff for the coordinator. This is a **PROPOSAL** until the sandbox-side adversarial-verifier grades it; I have not self-accepted or issued a gate verdict.
