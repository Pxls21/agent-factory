# Lane B2 report — S0-02 round 2

PIN: `246bec7ccc7d6cf40bb16ce3cae08045b0106719`

Status: BUILD PROPOSAL. The deterministic static-copy gate's own final output was `rc=0` on the final bytes. This is not an acceptance verdict; sandbox-side adversarial verification still owns that decision.

## NOT DONE / known gaps

1. No live relay delivery, membership write, role-key read, or PC service action was performed. The live eight-leg evidence bundle remains uncaptured.
2. The three buzz-acp-decided legs remain blocked until the coordinator lands the out-of-scope `RUST_LOG=debug` seam in the S0-01 launcher's closed environment set. The runner refuses loudly rather than fabricating evidence.
3. The revoked leg still requires an owner/coordinator relay membership removal and an externally written removal receipt. This lane only preserves and verifies that receipt.
4. The `neg-not-allowlisted` live leg assumes `user2` remains a member of the target channel at capture time. Only the coordinator's live operation can establish that state.
5. F16, the `validate-ledger` binding change, is coordinator-owned and untouched.

## Verified premise and file identity

The upstream source is `/home/rocco/s0-01-pinned/buzz` at commit `1c8321cd08feb597f8bcff5195c21148fb3e98ed`, clean when checked. The original premise still reproduces: the B1 scanner's first-`#[cfg(test)]` prefix cut excluded the later channel EVENT path, while the pinned source still has the six whole-file verification sites and the channel-event deserialisation seam.

Final primary-file identities:

| file | sha256 | lines |
|---|---|---:|
| `proofs/S0-02/check_buzz_authz.py` | `cbd9bcfda75d605bd9e660d386ac08e22a1a89715fd9e389e87e21e825c4f8b6` | 661 |
| `proofs/S0-02/oracle/denial_table.py` | `a3c31dbda859a6358a8a8b76e2f59a2799d480d78169407bc5223d7bf0944ba8` | 288 |
| `proofs/S0-02/tools/build_fixtures.py` | `fbcc2f7afad93d9dfd8583ea561acb9bf720b75a541ea21c460a09e5381a528a` | 546 |
| `proofs/S0-02/tools/pc/deliver_event.py` | `a00c3b7bc81dabde05a5407bc65de518d94359a576bf89d4b84046f77b01b516` | 202 |
| `proofs/S0-02/tools/pc/run_s0_02_legs.sh` | `03dc46c9591d439e38cb72e619281224a783edcb7fcb55f6e6ad214db48bc5a3` | 205 |
| `proofs/S0-02/spec.json` | `b224b5228b8d122a91f5ef4a6a0b4759623c6d3cf9f0c9dcec3a2db479cf2b0f` | 24 |
| `tests/test_s0_02_buzz_authz.py` | `055b39d94c85afed3fe6c6cd3e1bd540b6d3fb0ba26ed3c28fbd7f852b4c59f4` | 1412 |

The primary seven-file patch against the PIN is 919 additions and 156 deletions. The fixture set adds/regenerates the remaining scoped files. The complete scoped gate copied 55 files.

## Implemented contract

### Whole-source verification and freshness scan

- The source test now scans whole Rust files while structurally excluding `#[cfg(test)]` items and comments. It recognises direct calls, method calls, and imported aliases; exact equality pins the six known production sites. The channel-event handler is derived by brace depth and checked separately.
- Red controls cover a channel-path verification plant and an alias plant. False-red controls keep an early test module and a block-comment plant green.
- The channel-event region is also scanned for a same-expression `created_at` versus wall-clock comparison. The final predicate catches direct comparisons and method-chain rules such as `now.saturating_sub(event.created_at.as_u64()) > 600`; a mere log line containing both values stays false.
- The relay drift constant is parsed numerically, so `9000` cannot satisfy the `900` gate.

### Evidence and receipt semantics

- Delivery receipts have exactly five fields: `accepted`, `event_id`, `event_id_echoed`, `http_status`, and `message`. Fixture construction calls the real `deliver_event._normalise`, including explicit empty-message preservation.
- Accepted legs require bool `accepted=true`, integer HTTP 200, and an echoed event id. Relay-decided legs require bool `accepted=false`, integer HTTP 400, and no claimed relay echo.
- Each negative leg must carry exactly its one named observable in the oracle-declared evidence channel. A second known observable is a named failure; wrong-channel copies are not accepted. Distinctness remains an independent six-leg blanket-rejection gate.
- Root closure rejects any unknown directory or garbage file. Every evidence-path read is guarded by the imported S0-01 regular-file check, and the outer checker is capped at 90 seconds.
- The positive nonce must be a complete token, not a substring of a longer token.

### Revocation, replay, and canary

- `S0_02_MEMBERSHIP` defaults outside the revoked leg directory, survives the `rm -rf`, and is copied into the fresh leg only after the wipe.
- The checker requires a completed removal for the delivered sender, integer `at_epoch_s < t0`, a delivered `h`-tag channel match, and integer 2xx relay response status.
- The replay runner sleeps one second before its second publish, reuses the first delivery's t0, and gives only that second sub-leg a 150-second clock tolerance. Ordinary legs retain 120 seconds.
- The startup canary is accepted only on a DEBUG line and required only for oracle rows decided in buzz-acp. Relay-decided INFO-only corpus logs need no debug canary.

### New negative leg and D8 correction

- `neg-not-allowlisted` uses `user2`: the relay accepts the channel member, then buzz-acp's configured author gate drops it. It supplies the sixth distinct observable and is present in both deterministic bundles, the oracle, runner, checker, fixtures, and pass summary.
- D8 now states the narrow result: no shipped default `respond_to`/subscription rule references timestamp, while `FilterContext.timestamp` makes sender `created_at` config-reachable.

## Deterministic tests and negative controls

Fresh final runs against the pinned PC inputs:

```text
125 passed in 91.81s (0:01:31)
PYTEST_RC=0
```

Static-copy gate, from a `git archive 246bec7` copy with exactly the 55 scoped working-tree files overlaid (recorded in `../scratch/lane-gate-final2.txt`):

```text
RESULT: rev=246bec7ccc7d files=55 runs=2 identical=yes rc=0 summary="189 passed in 116.65s (0:01:56) 189 passed in 115.39s (0:01:55)"
LANE_GATE_RC=0
```

The first gate attempt was deterministically red, `30 failed, 159 passed` twice, because `lane_gate.sh` invokes PATH's `python3` and the system interpreter lacked `rfc3339-validator`. Re-running with `/home/rocco/venv-agent-factory/bin` first on PATH used the declared project dependency; the gate then reported the two rc-0 runs above. No source was weakened to route around that environment failure.

Other executed checks:

```text
fixture-drift: none (8 fixtures match a fresh build)
FIXTURE_CHECK_RC=0

pyflakes: no output, rc=0
bash -n proofs/S0-02/tools/pc/run_s0_02_legs.sh: rc=0
git diff --check: rc=0
tests/test_lane_gate.py::test_committed_evidence_and_fixture_logs_are_not_gitignored: 1 passed
```

The in-process independent-oracle exercise returned:

```text
PASS: S0-02 buzz-authz - 1 positive, 6 negative legs, 6 distinct reasons; +1 revocation leg (assertion 2)
failure_reason: blanket-rejection: reasons ['delivery::restricted: not a channel member'] not distinct — 6 negative legs collapsed to 1 observable(s)
```

The required 12 survivor families all die in the final attack run: channel-path verify, inline wall-clock freshness, alias call, two observables, both wrong-channel directions, unknown/garbage root entries, far-future t0, strict relay boundary, after-delivery/malformed removal receipts, nonce substring, and INFO canary. The attack ledger in `../scratch/mutants-final.tsv` reports `20 KILLED / 20`; receipt variants are separate rows.

The prior 44 killed/caught attack classes were re-run through 27 selected negative-control nodes covering the families named by the predecessor verifier, including both six-way observable parametrisations; every selected node returned rc 0. Full details are in `../scratch/rerun44-final4.tsv`. The predecessor's three false-red classes are gone: test-module verify and block-comment verify both pass on source plants, and the real INFO-only relay-decided corpus case, including its non-pubkey 64-hex material, passes.

## 18-class self-sweep

| class | final enumeration and disposition |
|---:|---|
| 1 | Four `.exists()` candidates. Two timeline checks form the explicit deferral gate; tests prove it can only withhold (rc 2), never grant. Builder destination existence is not a verdict path. |
| 2 | Five checker `read_text` calls on evidence paths; all are reached through `_require_file`, directly or via `_read_json`. Seven FIFO parametrisations plus the outer-timeout control pass. |
| 3 | Zero stale `[-1]` selectors. The spec command is compared whole. |
| 4 | Zero production `assert not` acceptance checks. Negative controls assert exact exceptions/results. |
| 5 | Sixty-six broad substring candidates by lexical sweep. Outcome-critical observable channel/name, spec line, event id, nonce boundary, debug level, and exact receipt shape are separately pinned by mutation tests. Human-facing diagnostic substring checks remain test helpers. |
| 6 | One production environment read: `BUZZ_PRIVATE_KEY`, resolved once and threaded because keys are prohibited in argv. The checker takes synthetic root and anchors explicitly. Matrix: undeclared venue skips; declared real source runs; declared absent source fails. |
| 7 | Two lossy UTF-8 decode sites in the HTTP helper. Documented limit: raw response text is evidence, while accepted/status/id semantics come from parsed fields and HTTP status; replacement bytes do not decide admission. |
| 8 | Zero broad catches. |
| 9 | Zero Python waits/polls; three bounded runner loops. The turn wait also watches `buzz-acp.exit`, and shutdown is pidfile plus executable-identity guarded. |
| 10 | One declared source skip. Declared-but-missing input fails, demonstrated by matrix arm C. |
| 11 | One production `iterdir`, scoped to the supplied evidence root and used for fail-closed root closure. Fixture/test globs remain repository- or tmp-scoped. |
| 12 | Zero signal-handler installs in Python. The runner signals only its own pidfile process after executable identity. |
| 13 | One `/proc/<pid>/exe` read in the runner. It refuses an unexpected executable; no name-wide kill command exists. |
| 14 | One timeline-shape candidate. The checker imports the first-party S0-01 loader rather than copying it; tests pin object identity and prohibit another timeline opener. |
| 15 | Two lexical counter comparisons; the distinctness counts are explicitly tied to the same `distinct_legs` population before comparison. |
| 16 | Zero pyflakes findings on all scoped Python source and test files. |
| 17 | No gate-path writes. The fixture builder writes only into an explicit build destination; committed fixture determinism is checked from fresh temporary roots. Live capture writes are runner-only and not an admission oracle. |
| 18 | Two load-bearing order/binding families remain pinned: signature precedes identity/freshness, and bad-signature differs from positive only by signature. Added round-2 family: named-observable cardinality is exactly one. |

`ap_screen.py` reports five production candidates: AF-AP-40 ×3 (two explicit deferral checks and one builder destination check) and AP-32 ×2 (deterministic specimen-key derivation, no stamp-store lookup). `--tests` reports four AF-AP-34 lexical hits, all inside the test that prohibits `pkill`, `killall`, and `pgrep`; none is executable runner code.

## External-command census

The checker, oracle, fixture builder, and delivery helper spawn no subprocesses. `deliver_event.py`'s only external effect is the bounded relay HTTP request in `_post`.

The PC runner's external commands are: `sed` and `grep` for the RUST_LOG preflight; `mkdir`, `rm`, and `cp` for its owned capture directories; `setsid /usr/bin/python3` for the S0-01 launcher; `seq`, `sleep`, and `grep` in bounded polls; `readlink /proc/$pid/exe` for stop identity; `/usr/bin/python3 deliver_event.py`; `/usr/bin/python3 -c` for committed fixture role and t0 reads; and `date +%s`. It was syntax-checked and read, never executed by this lane.

## Discrepancies and deviations

- No design deviation was introduced.
- The brief says the debug canary applies to “replayed, self-authored”; adding `neg-not-allowlisted` necessarily makes three buzz-acp-decided rows. The implementation follows the governing predicate, `evidence == EV_BUZZACP_LOG`, so the new leg is correctly included.
- The fixture bundles are synthetic checker-power evidence only. They do not establish live reachability, relay membership, or production readiness.
- GitNexus `detect-changes --scope compare --base-ref 246bec7 --repo /home/rocco/agent-factory` returned rc 0, 71 shared-tree files, 51 symbols, 0 affected processes, low risk. It includes other staged lane changes in the shared index; it cannot isolate this detached lane's staged-plus-unstaged overlay.

## Self-attack

1. Most likely wrong: the Rust source scanner still misses a syntactic verification form. Ruled down by whole-file exact-site equality, direct/method/alias plants, channel-region derivation, cfg(test) structural exclusion, and comment false-red controls. Not ruled out for arbitrary Rust macro expansion; the gate claims only the explicit forms in the pinned source contract.
2. Most likely wrong: synthetic receipt semantics diverge from the real relay. Ruled down by constructing every bundle receipt through `deliver_event._normalise`, exact five-key census, 200/400 and echo mutation tests, and pinned relay source prose. Only coordinator live capture can finish this proof.
3. Most likely wrong: a negative leg passes for an extra or copied reason. Ruled down by evidence-channel binding, exact one-observable cardinality, root closure, blanket mutation, swapped-reason mutation, and both wrong-channel attacks.

## Evidence tiers

Verified: all identities, source scans, fixture checks, test counts, gate result, negative-control outputs, pyflakes/bash syntax, gitignore test, and checks in this report were run on the final bytes.

Inferred: the runner will produce the same receipt/timing semantics live, based on static source and deterministic helper tests. It was not executed.

Assumed: coordinator-provided channel membership and removal state at live capture time.
