# Lane O6 — S0-03 fixtures + tests realign to the artifact-nonce direct binding (Blocker 4)

**Authorization.** Defensive verification work on the owner's own OmniRoute/Hermes system. You
edit sandbox tests + fixtures ONLY.

**PIN:** current HEAD of `claude/soundbox-kit-migration-iz1jwf` (commit `d0d1ab2` or later — it
carries the already-changed checker + collector). **Do NOT** run any live capture, touch the PC
bridge, mint anything, edit `check_omniroute_roundtrip.py` / `collect_leg.sh` / `direct_responses_probe.py`
/ `run_s0_03_legs.sh` / `spec.json` / `blocked.json` / `result.json` / registry / ledger /
`todo/BUILD-TASKLIST.md`, or take any outward action. **Do NOT commit** — leave the tree for the
coordinator. If a premise here is wrong, STOP and report rather than inventing.

## What already changed (DO NOT re-do — read to understand the target)
`proofs/S0-03/check_omniroute_roundtrip.py` `check_identity_route` and
`proofs/S0-03/tools/pc/collect_leg.sh` now bind the **direct** leg by the fresh nonce the direct
leg sent, which OmniRoute records in the row's artifact `requestBody` and the collector exports as
a `recorded_input` field on the direct row of `omniroute-requests.json`. The checker asserts:
`direct.json["nonce"] in row["recorded_input"]` (plus `combo_name == route`, `status == 200`,
`method == POST`, a permitted path, non-stub provider/model). It NO LONGER reads
`response_headers` / `id` / `x-omniroute-request-id` / `x-omniroute-model` for the direct binding.

REASONS changed: `identity_request_id` and `identity_model_header` are **deleted**; a new
`identity_direct_nonce` = `"identity: direct leg nonce {!r} is not in OmniRoute's recorded request for the row"`
(ONE format arg — the nonce). The hermes binding (`session_tag == nonce2`, `combo_name`, non-stub
provider, size-1 `models` set) is UNCHANGED.

## The `recorded_input` value (exact shape — mirror the real OmniRoute artifact requestBody)
For a fixture whose direct.json nonce is `<NONCE>`, its omniroute-requests.json **direct** row must
carry a `recorded_input` string = `json.dumps(BODY, sort_keys=True)` where BODY is exactly the
probe's request body (`direct_responses_probe.py:206-216`):
```json
{"input": [{"content": [{"text": "Reply with exactly the token <NONCE> and nothing else.", "type": "input_text"}], "role": "user"}], "model": "agentfactory-build", "stream": true}
```
The only requirement the checker enforces is `<NONCE> in recorded_input`; keep the shape faithful.

## The changes (ONE atomic increment; the S0-03 test file green ×2 at the end)

### 1. Fixtures that must PASS the direct-row validation — add `recorded_input` (contains the nonce)
For EACH of these bundles, set the `omniroute-requests.json` **direct** row's `recorded_input` to the
BODY above using THAT bundle's `direct/direct.json["nonce"]`:
`evidence-stub-route`, `evidence-provider-key-present`, `hostile-stub-provider`,
`hostile-combo-mismatch`, `hostile-missing-session-tag`, `hostile-wrong-transport-path`.
(These reach `check_identity_route`; the direct row must clear the recorded_input+nonce check to
reach each bundle's own defect. Keep every OTHER field and each bundle's specific defect intact.)
The two credential bundles (`evidence-credential-absent`, `evidence-credential-rejected`) gate
BEFORE `check_identity_route`; leave them unchanged.

### 2. Re-key `hostile-wrong-request-id` → `hostile-wrong-nonce` (rename the directory)
`git mv proofs/S0-03/fixtures/hostile-wrong-request-id proofs/S0-03/fixtures/hostile-wrong-nonce`.
Its direct row's `recorded_input` = the BODY above but with a DIFFERENT 16-hex token (NOT this
bundle's direct.json nonce). Then the checker reds:
`identity: direct leg nonce '<this bundle's direct.json nonce>' is not in OmniRoute's recorded request for the row`.

### 3. Re-key `hostile-model-header-mismatch` → `hostile-model-mismatch` (rename the directory)
The `identity_model_header` cross-check is gone. Instead make the DIRECT row's `model` differ from
the hermes rows' `model` so the size-1 `models` set fails. Keep the direct row otherwise VALID
(recorded_input with the nonce, provider non-stub, status 200, POST, permitted path). Reds:
`bundle: the call_logs rows report different model ids <sorted repr of the two model ids>`
(compute the exact `repr(sorted({direct_model, hermes_model}))` from the fixture you write).

### 4. Update `tests/test_s0_03_omniroute.py`
- `HOSTILE_BUNDLES` (≈:175-194): rename the two entries and set their new exact reasons (per §2/§3).
  The other four entries' reasons are unchanged — VERIFY each still matches by running the checker.
- The model-header test (≈:350-360, asserts `call_logs model ... != x-omniroute-model header`):
  rewrite to the model-set-mismatch reason (or delete if fully covered by the hostile-model-mismatch
  parametrize — prefer rewrite to keep the direct falsification).
- The id-realign test (≈:1149-1160, "direct row id must equal x-omniroute-request-id"): rewrite to
  the nonce binding — mutate `recorded_input` so it does NOT contain the direct nonce and assert
  `identity_direct_nonce`.
- The direct-binding tests (≈:1740-1840 and ≈:1950-1970): rewrite every reference to
  `response_headers["x-omniroute-request-id"]` / the `id==request_id` binding to the
  `recorded_input`/nonce binding. The `passing` fixture builder (≈:105-117) copies
  `evidence-stub-route` and repairs provider→codex; after §1 it inherits recorded_input, so
  `test_passing_bundle_passes` must stay green — confirm it.
- Grep the whole file for `x-omniroute-request-id`, `x-omniroute-model`, `identity_request_id`,
  `identity_model_header`, `response_headers` and resolve EVERY hit to the new binding.

## Gate (paste verbatim; do NOT mint, do NOT commit)
- `bash scripts/test_summary.sh tests/test_s0_03_omniroute.py` TWICE — identical counts; paste both.
- `python3 proofs/S0-03/check_omniroute_roundtrip.py` on the passing fixture (build it as the test's
  `passing` fixture does: copy evidence-stub-route, set every row provider=codex) → rc 0; paste.
- Run the checker UNPATCHED on EACH committed hostile + the two renamed ones → rc 1 with the exact
  reason; paste each (this is the AF-AP-36 red-then-green discipline).
- `python3 scripts/report_lint.py` on your report.
- Report DATA: files:lines changed, the two pasted counts, each hostile's reason line, any NOT-done.

## Boundary (exactly these)
`tests/test_s0_03_omniroute.py`, `proofs/S0-03/fixtures/**` (including the two `git mv` renames).
Nothing else. NO live capture, NO mint, NO commit, NO PC bridge, NO edits to the checker/collector/
probe/runner/spec/registry/ledger.
