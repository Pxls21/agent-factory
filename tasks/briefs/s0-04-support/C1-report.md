# Lane C1 — S0-04 compression contract: checker over captured legs, fixtures, PC leg runner

PIN: `23a3458` · venue: sandbox (Opus 4.6 `code-implementer`) · report written 2026-09-08T02:56:08Z (pasted from `date -u`)
Working-tree HEAD at report time: `545a9ff` — other lanes landed commits while this lane ran; every gate below ran from the
PIN archive, not the moving tree.

**TL;DR** — S0-04 is BUILT and graded in the sandbox: spec + checker + two committed request fixtures + three committed
evidence bundles + PC-side capture/runner + 67 tests, 16/16 mutants killed, zero survivors. **NOT run here: the three PC
legs and the config capture** — this lane has no bridge, by brief. **One pinned design item did not survive contact with
the instrument:** the S0-01 backend does not persist raw request bytes, so assertion A3 is a canonical-bytes + wire-length
comparison, not a literal wire-byte compare. That is written into the checker's own docstring and detailed at D1.

`scripts/report_lint.py` over this report (with the four `--map` aliases below):
`112 refs — OK 112, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0`. The lint is heuristic: it proves only that every cited
line contains a token this report claims about it — it proves nothing about the report's reasoning.

Citation aliases used below: `C` = `proofs/S0-04/check_compression.py` · `T` = `tests/test_s0_04_compression.py` ·
`K` = `proofs/S0-04/tools/pc/capture_leg.py` · `R` = `proofs/S0-04/tools/pc/run_s0_04_legs.sh`.

---

## FILE IDENTITY (sha256 of the final bytes)

| file | sha256 (first 12) | lines |
|---|---|---|
| `proofs/S0-04/check_compression.py` | `88b03be62f33` | 390 |
| `proofs/S0-04/spec.json` | `968d9034b08c` | 24 |
| `proofs/S0-04/tools/pc/capture_leg.py` | `27112fbf823e` | 257 |
| `proofs/S0-04/tools/pc/run_s0_04_legs.sh` | `7cd1319665dd` | 137 |
| `proofs/S0-04/fixtures/request-baseline.json` | `6b1772d4e301` | body 189 B |
| `proofs/S0-04/fixtures/request-large.json` | `de33670256f6` | body 65536 B |
| `tests/test_s0_04_compression.py` | `a8a5af2480a3` | 845 |

27 files under `proofs/S0-04/` (2 request fixtures + 3 bundles × 7 files + spec + checker + 2 PC tools).
`git status --porcelain` shows exactly `?? proofs/S0-04/` and `?? tests/test_s0_04_compression.py`. **Nothing under
`proofs/S0-01/` was edited** — the backend is used by absolute path (the PC runner) and by subprocess (the tests).

Gate copy: `git archive 23a3458` into the scratch dir, plus exactly these files. Identity table: 28/28 rows OK (working
tree == gate copy, byte for byte). `git ls-tree 23a3458 -- proofs/S0-04` returns 0 entries, so the gate measures only this
lane's bytes.

**Counts pasted verbatim from `scripts/test_summary.sh`, two runs on the gate copy:**

```
GATE RUN 1  pytest-exit: 0   pytest-summary: 67 passed in 6.34s
GATE RUN 2  pytest-exit: 0   pytest-summary: 67 passed in 5.46s
```

`python3 -m pyflakes` over the three Python files: clean, 0 hits. `bash -n run_s0_04_legs.sh`: clean.

---

## DONE — assertion → capture field → checker rule → test

The three seed assertions (`seeds/seed-stage0-v1.yaml:406-410` carries the `execution_proof` block).

**A1 — the Hermes-side request carries `x-omniroute-compression: off`.**
Capture fields: `config/hermes-provider.json` `extra_headers`, and every request leg's `request.json`.
Checker: `def check_config_leg` at C:296 looks the key up case-insensitively and compares the value EXACTLY; absence raises
`config-header-absent` at C:307. Each request leg binds `request.json` to the committed fixture field by field.
Tests: `test_mutant_config_header_missing_accepted` T:229 · `test_config_header_key_case_is_also_insensitive` T:335 ·
`test_request_json_must_equal_the_committed_fixture` T:413 · `test_config_field_mutations` T:466.

**A2 — the response carries `X-OmniRoute-Compression` reporting off.**
Capture field: `<leg>/response.json` `headers`, an ORDERED LIST of pairs.
Checker, one rule per line (the header NAME is matched case-insensitively, the VALUE exactly — AF-AP-38):
absence raises `compression-header-missing` at C:259 ·
a duplicate raises `compression-header-duplicated` at C:261 ·
any other value raises `compression-header-value` at C:263.
Tests: `test_mutant_header_absent_accepted` T:102 · `test_mutant_header_value_on_accepted` T:109 ·
`test_mutant_case_sensitive_header` T:320 · `test_duplicated_response_header_is_refused` T:345.

**A3 — the stub upstream's received request compares equal to the sent fixture.**
Capture field: `<leg>/upstream-record.json`, the backend's own record file copied verbatim.
Checker: record identity first — `nonce-mismatch` at C:278 · then the wire byte length,
`request-not-preserved: content-length` at C:281 · then the canonical body bytes,
`request-not-preserved: first diff at byte` at C:284.
Tests: `test_mutant_body_diff_accepted` T:122 · `test_mutant_offset_wrong` T:129 ·
`test_offset_tracks_the_mutation_position` T:143 · `test_content_length_mutation_is_caught` T:357 ·
`test_tail_truncation_of_the_body_is_caught` T:368 · `test_a_real_truncation_trips_the_length_half_of_a3` T:385 ·
`test_truncation_that_removes_the_nonce_is_caught_as_a_wrong_record` T:401.

### Gates that are not seed assertions but close named classes

| rule | where | why + test |
|---|---|---|
| the leg set is CLOSED and DECLARED | `REQUIRED_LEGS = (` at C:58, `LEG_FIXTURE` at C:60 | a discovered set lets a deleted leg shrink the proof (AF-AP-40) and an extra directory smuggle evidence (AF-AP-23): `test_partial_capture_fails_it_does_not_defer` T:291, `test_extra_leg_is_refused` T:300 |
| every bundle file is credential-screened before grading | `LEAK_PATTERNS` at C:75, `def _screen_tree` at C:149, `credential-in-evidence` at C:170 | `test_mutant_bearer_in_evidence_accepted` T:179, `test_credential_screen_covers_every_leg_and_file` T:192 |
| the `authorization_fingerprint` carve-out is shape-validated, then masked | `def _fingerprints` at C:173 | the instrument's redaction is a 64-hex sha256; without the carve-out no real bundle could pass, without the shape check the field would be a smuggling lane: `test_fingerprint_field_may_not_carry_a_bearer` T:205, `test_a_second_hex64_still_fails` T:217 |
| every read is S_ISREG-gated before it happens | `def _require_file` at C:124, `evidence-not-regular-file` at C:162 | `test_mutant_fifo_hang` T:254, `test_symlink_in_bundle_is_refused` T:265 |
| response headers are pairs, never a dict | `def _header_values` at C:201 | a dict collapses a duplicated header to the last value — AF-AP-41's mechanism: `test_duplicated_response_header_is_refused` T:345 |
| the leg was captured THROUGH OmniRoute | `OMNIROUTE_PORT = 20128` at C:64, `request-url-unexpected` at C:244 | a leg captured straight at the backend would preserve the request perfectly and prove nothing about the gateway: `test_request_url_must_be_the_omniroute_endpoint` T:433 |
| the fixture is asserted canonical before grading | `fixture-not-canonical` at C:228 | a non-canonical fixture makes the compare unable to detect any difference: `test_non_canonical_fixture_is_refused` T:510 |
| reason lines are redacted | `def _redact` at C:100 | a hostile bundle must not turn the checker into the leak: `test_mutant_bearer_in_evidence_accepted` T:179 also asserts the rejected value is not echoed |
| the checker reads NO environment | structural | no exported value can flip a leg: `test_checker_reads_no_environment` T:612, `test_capture_leg_resolves_the_key_file_at_exactly_one_site` T:620 |

### Spec and mint state

`proofs/S0-04/spec.json`: positive `check_compression.py proofs/S0-04/evidence` expect 0; negative
`check_compression.py proofs/S0-04/fixtures/evidence-header-missing` expect 1 plus the seed's frozen
`compression-header-missing`. Validated against `proofs/schemas/spec.schema.json` with `jsonschema` 4.25.1 by
`test_spec_matches_the_schema` T:597, which also runs a structural half so it can never silently skip.
`test_spec_negative_reason_is_produced_by_the_real_checker` T:627 runs the negative leg's own argv through the real
checker and binds the frozen reason to the line the checker actually prints (AF-AP-27/AF-AP-29).

The four CLI states, run from the gate copy:

```
proofs/S0-04/fixtures/evidence-pass            -> exit 0
    observation: off upstream record carries x-omniroute-compression: off
    observation: off-large upstream record carries x-omniroute-compression: off
    observation: config api_mode = chat_completions (RECORDED, not asserted - ADR 0002 deviation, owner task #35)
    PASS: S0-04 compression-contract - 3 assertions over 3 legs
proofs/S0-04/fixtures/evidence-header-missing  -> exit 1
    failure_reason: off: compression-header-missing
proofs/S0-04/fixtures/evidence-body-diff       -> exit 1
    failure_reason: off: request-not-preserved: first diff at byte 56
proofs/S0-04/evidence                          -> exit 2
    deferred: S0-04 evidence not captured
```

The `PASS: S0-04 compression-contract` line is emitted at C:356; `raise Deferred("S0-04 evidence not captured")` sits at C:332.
The positive leg **DEFERS today** because the evidence root does not exist, and the runner treats exit 2 as
`capability-unavailable` (`scripts/proof-runner:181-185`),
preserving any artifact — so **no `result.json` is minted and the ledger stays ABSENT for S0-04**
(`proofs/registry.yaml:15` already carries the row with `assertion_count`). `test_spec_positive_leg_defers_today` T:640
pins that.

**Attested inputs (AF-AP-56).** The attestation set is `ATTESTATION_CLOSURE` + the schemas + the proof's own tree, at `scripts/validate-ledger:68-71`.
This lane creates only `proofs/S0-04/**`, which no existing
artifact attests, and edits none of `proofs/schemas/`, `scripts/proof-runner`, `scripts/validate-ledger` or
`proofs/registry.yaml`. **No regeneration is required, and none was run.**

**Committed bundles are pinned to the REAL producer (AF-AP-42).** Every `upstream-record.json` in the three bundles was
written by RUNNING `proofs/S0-01/tools/scripted_backend.py` against the committed fixture bytes.
`test_record_shape_is_the_current_producer_shape` T:788 re-runs that producer inside the suite, pins the record's key set,
and feeds the freshly produced record to the checker; `test_real_record_of_a_mutated_body_is_rejected` T:816 is its paired
negative and `test_real_large_record_round_trips` T:835 its 64 KiB sibling.

---

## MUTANTS — 16 applied to scratch copies, 16 killed, 0 survivors

Harness: each mutant gets a fresh minimal-but-complete tree (checker, schemas, the S0-01 backend, the test file); the
script asserts the mutation site exists AND that the bytes changed, so no mutant can be vacuous. Negative control on the
harness itself: `BASELINE (unmutated) GREEN 67 passed in 4.89s`.

| # | mutant | verdict | run | first killers |
|---|---|---|---|---|
| 1 | HEADER-ABSENT-ACCEPTED | KILLED | 2 failed, 65 passed | `test_mutant_header_absent_accepted`, `test_spec_negative_reason_is_produced_by_the_real_checker` |
| 2 | HEADER-VALUE-ON-ACCEPTED (presence, not value) | KILLED | 1 failed, 66 passed | `test_mutant_header_value_on_accepted` |
| 3 | BODY-DIFF-ACCEPTED | KILLED | 8 failed, 59 passed | `test_mutant_body_diff_accepted`, `test_mutant_offset_wrong` |
| 4 | NONCE-MISMATCH-ACCEPTED | KILLED | 2 failed, 65 passed | `test_mutant_nonce_mismatch_accepted` |
| 5 | BEARER-IN-EVIDENCE-ACCEPTED | KILLED | 4 failed, 63 passed | `test_a_second_hex64_still_fails`, `test_credential_screen_covers_every_leg_and_file` |
| 6 | CONFIG-HEADER-MISSING-ACCEPTED | KILLED | 2 failed, 65 passed | `test_mutant_config_header_missing_accepted` |
| 7 | FIFO-HANG (S_ISREG gate removed) | KILLED | 2 failed, 65 passed in **186.34s** | `test_mutant_fifo_hang`, `test_symlink_in_bundle_is_refused` |
| 8 | DEFERRED-AS-PASS | KILLED | 3 failed, 64 passed | `test_empty_root_defers`, `test_mutant_deferred_as_pass` |
| 9 | CASE-SENSITIVE-HEADER | KILLED | 27 failed, 40 passed | `test_committed_bundle_passes_unpatched` |
| 10 | OFFSET-WRONG (`_first_diff` returns 0) | KILLED | 7 failed, 60 passed | `test_mutant_offset_wrong` |
| 11 | CONTENT-LENGTH-UNCHECKED | KILLED | 2 failed, 65 passed | `test_content_length_mutation_is_caught` |
| 12 | FIXTURE-CANONICALITY-UNCHECKED | KILLED | 1 failed, 66 passed | `test_non_canonical_fixture_is_refused` |
| 13 | LEGS-DISCOVERED-NOT-DECLARED | KILLED | 1 failed, 66 passed | `test_partial_capture_fails_it_does_not_defer` |
| 14 | REQUEST-FIXTURE-UNBOUND | KILLED | 1 failed, 66 passed | `test_request_json_must_equal_the_committed_fixture` |
| 15 | DUPLICATE-HEADER-LAST-WINS | KILLED | 1 failed, 66 passed | `test_duplicated_response_header_is_refused` |
| 16 | REQUEST-URL-UNBOUND (tail anchor restored) | KILLED | 2 failed, 65 passed | `test_request_url_must_be_the_omniroute_endpoint` |

Mutant 7 is the informative one: the mutated checker HANGS on the FIFO (186 s against the clean checker's ~4 s) and the
kill comes from the subprocess timeout. The S_ISREG gate is what makes the checker TERMINATE, not merely what makes it
print a tidy message.

**A discarded first run, disclosed:** this lane's first mutation pass was thrown away. Its mutant trees lacked
`proofs/schemas/` and the S0-01 backend, so two tests failed in EVERY tree — failures that look like kills but are the
harness. The table above comes from complete trees with a green baseline.

---

## NOT_DONE (named, never silently skipped)

1. **The three PC legs — `off`, `off-large`, `config` — were NOT captured.** `proofs/S0-04/evidence/` does not exist. The
   brief forbids this lane the bridge, so no request went through OmniRoute `:20128` and **this lane has never observed a
   real `X-OmniRoute-Compression` response header.** Everything about the gateway's actual behaviour is UNPROVEN. What is
   proven is that the grader is not a tautology and that the instrument records what the grader reads.
2. **The config capture was NOT run.** `capture_leg.py --config` is unit-tested against in-memory profile dicts only:
   `test_capture_leg_provider_block_drops_inline_key` T:662 and
   `test_capture_leg_provider_block_without_key_env_is_null_not_a_value` T:673.
   It has never parsed the owner's real `~/.hermes/profiles/agentfactory/config.yaml`; whether that profile even carries
   `key_env` rather than an inline `api_key` is unverified here.
3. **`run_s0_04_legs.sh` has never been executed.** `bash -n` clean; its external calls are enumerated in its own header
   at R:9-14 (six calls, four of them `capture_leg.py`); its never-kill-by-name property is tested by
   `test_runner_never_kills_by_name` T:721. Nothing more. It is a specification for the PC operator, not a proven runner.
4. **The routed model id is unresolved.** The fixtures carry `"model": "s0-01-pong"` — the brief's pinned value and the id
   the backend itself serves. But `s0-01-scripted/s0-01-pong` is what `proofs/S0-01/GROUNDING.md:247` records the golden
   running on — possibly a NAMESPACED id at the OmniRoute edge. I could not resolve this without the
   bridge and refused to guess silently: the runner preflights `/v1/models` and dies with the observed scripted ids when
   the fixture's model `is not in the OmniRoute catalog` (R:82), telling the operator to resolve it with the coordinator
   rather than edit committed fixture bytes.
5. **PyYAML on the PC is unverified.** `--config` needs it; the runner preflights `import yaml` at R:57 and dies with a
   named message. Present in the sandbox (6.0.1).
6. **No wide-tree suite run.** The `tests/ proofs/` sweep was launched once and killed by a container restart; it was not
   re-run, because the shared tree holds other lanes' uncommitted edits and its result would not be attributable to this
   lane. The gate that IS reported is the PIN-archive static copy, run twice.
7. **The seed's own mutation control was not performed** — see D2.

**One adjacent-suite red, proven not mine.** `tests/test_s0_01_scripted_backend.py` in the working tree reports
`1 failed, 336 passed`; the failure is `test_build_capture_record_roundtrip_check`. Two independent checks place it
elsewhere: (a) `git status --porcelain` shows `proofs/S0-01/tools/build_capture_record.py` MODIFIED by another live lane,
and this lane's scope contains no `proofs/S0-01` file; (b) the same test PASSES both on a pristine `git archive 23a3458`
tree and in this lane's gate copy (PIN + my files).

---

## DISCREPANCIES

**D1 — the pinned A3 mechanism does not exist in the instrument. Load-bearing; the brief told me to read `record()`.**
Design item 4 says "the upstream record's body bytes == the fixture's body bytes". They cannot be compared. `State.record`
accepts `raw_body: bytes | None = None` (`proofs/S0-01/tools/scripted_backend.py:484`) **for the credential screen only**
and never writes it; the record file it writes (`:536-540`) stores the PARSED JSON body and serializes with
`sort_keys=True`, which is recursive, so the wire key ORDER is gone as well. Verified by running the real backend and
reading the record: its keys are exactly `authorization_fingerprint, body, headers, method, path, received_at,
remote_addr, seq, t_mono_ns`.

What I built instead, and why it is exact rather than a weakened stand-in:

* the fixture body is committed in canonical form (`sort_keys`, `separators=(",",":")`, `ensure_ascii`, ASCII only, no
  floats) and the checker asserts the fixture IS canonical before comparing (`fixture-not-canonical` at C:228), so the
  comparison cannot go vacuous;
* the record's parsed body is re-serialized identically and compared byte for byte, reporting the first differing offset;
* **plus** the wire byte length, taken from the record's verbatim `content-length` header, against the fixture's length.

Together these reject compression, re-encoding, truncation, insertion and any change of a key or a value. **The one
residual, stated plainly: a re-serialization that permutes keys without changing the total byte length is invisible in
this record shape.** Closing it needs raw bytes in the record — a change to the S0-01 instrument, outside this lane's
boundary. `test_record_shape_is_the_current_producer_shape` T:788 asserts `"raw_body" not in record`, so a future backend
that starts persisting raw bytes breaks this test and prompts the upgrade. The limitation is written into the checker's
module docstring, not only into this report.

**D2 — the seed's mutation control is NOT the one implemented.** The seed's negative control is "mutate OmniRoute's real
header-set path in the mutation audit → proof RED". That would mean modifying the owner's running OmniRoute; the brief
forbids it and so does the standing rule. **Substitute, as the brief directs:** a committed bundle whose response lacks the
header, producing exit 1 with the frozen reason (`test_mutant_header_absent_accepted` T:102). The substitute proves the
CHECKER dies on a missing header. It does **not** prove OmniRoute's header-set path is load-bearing; that gap belongs to
whoever runs the PC legs.

**D3 — the body-diff bundle is a committed negative control but is NOT a spec leg.** Brief item 5 calls it a committed
negative control; brief item 6 pins the spec to exactly two legs. I followed item 6 literally, and
`fixtures/evidence-body-diff` is exercised by `test_mutant_body_diff_accepted` T:122 instead. Promoting it to a third leg
is a four-line spec edit if the coordinator wants the mint to carry it.

**D4 — reason strings were made non-overlapping on purpose.** My first draft used `config-compression-header-missing` for
the config leg. That string CONTAINS `compression-header-missing`, and the runner binds a negative leg by substring over a
line — `negative-control-unmet` is only raised when no line matches (`scripts/proof-runner:192-199`) — so a config-leg
failure could have satisfied the response-leg control. The config reasons are now `config-header-absent` and
`config-header-value`, and `test_config_reason_does_not_satisfy_the_response_negative_control` T:241 asserts no config
failure contains the spec's bound substring.

**D5 — `chat_completions` vs `codex_responses`: RECORDED, not resolved.**
The contract line `x-omniroute-compression` sits at `docs/03_INTEGRATION_CONTRACTS.md:40`, under `api_mode: codex_responses`;
`docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md:17` records both live profiles on `chat_completions` as an open owner decision
(task #35). The checker requires `api_mode` to be present and non-empty and prints it as an observation naming the
deviation and the task; it does not grade it. The committed pass bundle carries `chat_completions`, so the observation
line is exercised by `test_observations_are_recorded_not_asserted` T:88.

**D6 — the fixtures use `/v1/chat/completions`.** That follows the instrument (the scripted backend serves only that
route) and D5's live reality, not `docs/03`'s `codex_responses` / `/v1/responses`. If task #35 resolves toward
`codex_responses` these fixtures need regenerating; they are committed bytes, so that would be a visible diff.

**D7 — what the material pack got right, and the one thing it did not carry.** Every pack claim I re-checked held:
`proofs/S0-04/` absent, the registry row present, the ledger ABSENT, no spike naming S0-04, the `docs/03` and `docs/02`
seams verbatim. The pack correctly flagged that the backend's docstring never mentions compression. What it did **not**
state — and what changes the design — is D1: it quotes the docstring's "Not recorded" list but not the fact that the
record file omits the raw body. That is a read of `record()` itself, which the brief correctly told me to do.

**D8 — `os.environ` in `capture_leg.py` (the lane's only production AP screen hit).** Classified SAFE, guard named:
`os.environ.get` appears at exactly one site, K:60, inside `def read_key` at K:57; `--key-file` takes precedence and the
resolved path is threaded explicitly. The CHECKER reads no environment at all, so no exported value can change a VERDICT.
Pinned by `test_checker_reads_no_environment` T:612 and `test_capture_leg_resolves_the_key_file_at_exactly_one_site` T:620.

---

## 18-CLASS PREFLIGHT over this lane's own files

Enumerated by grep/AST over `check_compression.py`, `capture_leg.py`, `run_s0_04_legs.sh` and the test file; every
instance RUN or structurally proven. An empty class is a result.

| class | instances | verdict |
|---|---|---|
| 1 presence-gated checks | 0 | EMPTY — deferral exists only for "nothing captured"; once a leg directory exists every required file is required, proven by `test_missing_required_file_fails_named` T:309 |
| 2 reads outside a walk / no S_ISREG | 6 → **2 DEFECT, fixed** | 4 SAFE, gated by `def _require_file` C:124, `def _screen_tree` C:149, `def read_key` K:57, `def find_record` K:117. DEFECT: `capture_leg` read the `--fixture` and `--profile` paths ungated, so a FIFO there hangs the capture. Fixed with `def read_regular` at K:137; red test `test_capture_leg_refuses_a_fifo_fixture` T:446 |
| 3 stale `[-1]` | 1 | SAFE — `test_pass_line_is_exact` T:82 takes the last line of freshly captured stdout and asserts equality, which is stricter than a substring |
| 4 negative acceptance assertions | 5 | SAFE — each is paired with a positive in the same test; `test_mutant_bearer_in_evidence_accepted` T:179 asserts both the failure and that the credential is not echoed |
| 5 substring / tail anchors classifying outcomes | 2 → **1 DEFECT, fixed** | DEFECT: the request leg's URL check used `endswith`, accepting ANY host including the backend itself, which would have made the whole proof vacuous. Fixed to pin scheme, port and exact path — `request-url-unexpected` at C:244; red test `test_request_url_must_be_the_omniroute_endpoint` T:433; mutant 16 |
| 6 env-domain fail-opens | 1 | SAFE — see D8 |
| 7 lossy decodes on a decision path | 5 | 3 SAFE (`b64decode(validate=True)` rejects junk; `find_record`'s replace can only FAIL to match, which is loud). 2 **DOCUMENTED-LIMIT**: `errors="replace"` at C:165 means a credential written as invalid UTF-8 could have a pattern broken by the replacement character. ASCII and valid-UTF-8 credentials — the shapes screened — are unaffected, and bundle files are JSON by contract |
| 8 broad catches | 2 | SAFE — both are terminal fail-closed handlers returning 1, never 0, with the reason redacted through `def _redact` C:100. A checker crash cannot satisfy the spec's negative leg because the runner also binds the reason substring |
| 9 waits / polls | 6 | SAFE — bounded tree walks; the test readiness loop is failure-aware and ends in `pytest.fail`; the runner's startup loop is bounded at 40 and dies with `backend exited during startup` at R:107 |
| 10 skips / xfails that cannot fire | 1 → **1 DEFECT, fixed** | DEFECT: `importorskip` would silently delete the spec-schema check on a venue without `jsonschema`. Replaced by a structural half that always runs plus an explicit failure — `test_spec_matches_the_schema` T:597 |
| 11 world-scoped enumerations | 9 | SAFE — every enumeration is scoped to the bundle root, the record dir or the fixtures dir; none touches a shared location |
| 12 signal installs | 0 | EMPTY |
| 13 `/proc/<pid>/exe` races | 1 → **1 DEFECT, fixed** | DEFECT: the runner's reuse branch trusted the pidfile plus `readlink "/proc/$pid/exe"` at R:90 alone, so a recycled pid would be adopted as "the backend" (AF-AP-55). Fixed by requiring a live service: the branch now dies unless `:20201/healthz -> $code` is 200, at R:93 |
| 14 mirrors of the code under test | 1 | DOCUMENTED-LIMIT — `test_mutant_offset_wrong` T:129 canonicalises with the same call the checker uses. The un-mirrored oracle is `test_offset_tracks_the_mutation_position` T:143, which derives the expected offset from the committed fixture bytes alone and never calls the checker's serializer |
| 15 counters over different populations | 1 | SAFE — `test_observations_are_recorded_not_asserted` T:88 asserts three observation lines against three declared legs; adding a leg correctly breaks it |
| 16 provably redundant guards | 1 | SAFE — the `_stat.S_ISDIR(leg_dir.lstat()` check at C:348 is reachable: a REGULAR file named `off` passes the screen and is refused there |
| 17 hardlink-clobbering writes | 3 → **3 DEFECT, fixed** | the two writers followed any pre-existing symlink at the destination. Fixed by `path.unlink()` before writing, at K:150; red test `test_capture_leg_never_writes_through_a_symlink` T:454 |
| 18 other families | 1 | the `--base-url` domain was unbounded; closed by the same fix as class 5 |

**Six DEFECT rows, all fixed in this round, each with a red-then-green test.** All 67 tests pass after the fixes and all
16 mutants still die.

`scripts/ap_screen.py` — production: 2 hits, both the same line, classified SAFE at D8. Tests: 3 hits (AF-AP-34 twice,
AF-AP-59 once), all on the single line inside `test_runner_never_kills_by_name` T:721 that ENUMERATES the banned tokens —
SAFE, that line is the enforcement, not a violation.

**Bug-echo.** Two classes are worth echoing beyond this lane: (a) reason-substring COLLISION between a checker's own
failure reasons and a spec's bound `failure_reason` (D4), a hollow-green path in any proof with more than one reason
family; (b) tail-anchored endpoint checks that accept any host (class 5), the same shape as AF-AP-47's
guard-narrowed-to-a-specimen. Neither is registered in `docs/INCIDENT-LOG.md`. **Registering them is the coordinator's
call — that file is outside this lane's scope and I did not touch it.**

---

## SELF-ATTACK — the three most likely ways this is still wrong

1. **"The proof passes without OmniRoute ever compressing anything, so it proves nothing."** Partly true, and unavoidable
   today: the gateway leg has not run. What the sandbox CAN establish is that the grader is not a tautology, and the
   mutation table is that evidence — including that removing the S_ISREG gate makes the checker hang rather than pass, and
   that a URL pointed at the backend instead of the gateway is refused. Ruled out as a *grader* defect. NOT ruled out as a
   *contract* claim: S0-04 must stay ABSENT until the PC legs run.
2. **"The canonical compare is a semantic compare wearing a byte-compare's name."** This is the real risk and I named it
   in three places: the checker's docstring, D1, and the failure string's own documentation. The mitigations are that the
   fixture's canonicality is asserted at check time (mutant 12 proves that assertion is load-bearing) and that the wire
   length is checked from a separate record field (mutant 11). The residual — an equal-length key permutation — is the
   only pass-through-violating rewrite this evidence cannot see, and I did not hide it by calling the check something it
   is not.
3. **"The committed bundles are self-serving: the checker was written against them."** The response half IS synthetic and
   I say so — there is no OmniRoute in this sandbox. The upstream half is not: every `upstream-record.json` came out of a
   run of the real S0-01 backend, and `test_record_shape_is_the_current_producer_shape` T:788 re-derives one inside the
   suite and pins the record's key set, so drift in the instrument breaks the suite rather than the PC capture. The
   un-mirrored oracle for the offset is `test_offset_tracks_the_mutation_position` T:143. What remains unpinned is the
   response header's real spelling on the wire; the first PC leg settles it, and the checker already accepts any casing
   (mutant 9).

**Kill switch.** Remove the compression header from the passing bundle's response and the proof goes red with the seed's
exact reason (`test_mutant_header_absent_accepted` T:102); delete a whole leg directory and it goes red naming the leg
(`test_partial_capture_fails_it_does_not_defer` T:291); delete the evidence root and it DEFERS rather than passing
(`test_mutant_deferred_as_pass` T:277).
