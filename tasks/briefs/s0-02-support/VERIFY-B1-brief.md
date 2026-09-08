# VERIFY-B1 — adversarial grade of lane B1 (S0-02 Buzz authorization/freshness: the deterministic fixtures, the source-derived oracle table, the distinctness-first checker, two SYNTHETIC bundles, the NIP-98 delivery tool and the PC leg runner)

You are an adversarial-verifier (Opus 5 in the sandbox, or the PC Hermes `adversarial-verifier` role). Repo /home/user/agent-factory,
branch claude/soundbox-kit-migration-iz1jwf. **PIN: `088efef`** (the commit carrying the lane's 128 files + its report). Grade
the bytes of `git archive 088efef` from a copy under the session scratchpad /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/
(`vb1/`; delete it when done). Read-only git on the shared tree (it carries other lanes' uncommitted S0-01 edits — none in your scope);
every mutant on scratch copies; every pytest run with an explicit `--basetemp`; kill only what you start, PID-targeted; never
background a run and stop; no outward actions; NO network call to any relay (the owner's Buzz relay stack on the PC is production —
never touched by a verifier; `deliver_event.py` is READ, never run); never read, print or commit a private key (`identities.json`
is pubkey-only; the fixture SPECIMEN key is a labelled test key derived from a committed seed — cite it, never a role key).
Interpreter `/root/venv-agent-factory/bin/python`. The declared input `S0_02_BUZZ_SRC` = the pinned buzz checkout
`/home/user/nerdherderdani/buzz` (commit 1c8321cd, READ-ONLY; `scripts/test_summary.sh` sets the venue so the default applies).

**The ONE bridge action you MAY take:** the pytest-only PC gate `scripts/pc_suite.sh launch -n 8 -- tests/test_s0_02_buzz_authz.py`
from a clean detached worktree of the PIN, then `wait <RUN_ID>` (`pc_suite.sh` exports `S0_02_BUZZ_SRC` to the PC's pinned clone).
Nothing else on the bridge — NEVER run `run_s0_02_legs.sh` or `deliver_event.py`, never touch the relay or buzz-acp on the PC.

**Inputs (read in this order):** the lane brief `tasks/briefs/s0-02-b1-buzz-authz-fixtures-checker-pc-legs.md` (the contract:
Design 1-8; if the file name differs, it is the one brief under `tasks/briefs/` whose title starts `Lane B1`) · the lane's report
`tasks/briefs/s0-02-support/B1-report.md` (the 20-row source table, the A1-A3 evidence chains, the five negatives + the revoked leg,
24 mutants with FOUR round-1 survivors, the 18-class preflight, NOT_DONE 1-9, discrepancies D1-D8, the self-attack S1-S3) · the
material pack `tasks/briefs/stage0-parallel-support/material-S0-02.md` (the seed block `seeds/seed-stage0-v1.yaml:366-380`,
docs/03 §1 `:22`, the S0-07/S0-11 exemplars §5.4, the 18 classes §7) · the pinned buzz source (`crates/buzz-acp/src/lib.rs`,
`crates/buzz-acp/src/relay.rs`, `crates/buzz-relay/src/handlers/ingest.rs`, `crates/buzz-relay/src/api/bridge.rs`,
`crates/buzz-core/src/error.rs` — the lane's citations) · the S0-01 modules the checker IMPORTS by path (`proofs/S0-01/
check_acp_conformance.py` `_require_file` + the timeline reader, `proofs/S0-01/nostr_verify.py`, `proofs/S0-01/pins.py:44`
`PINNED_ENV_KEYS`) at the PIN — note the S0-01 checker is under repair by another lane (A5k on the PC) · the real S0-01 corpus
`/root/s0-01-realleg/golden/run-1/` (`timeline.jsonl`, `mentions/owner.receipt.json` — the shapes the synthetic bundles mirror) ·
`docs/INCIDENT-LOG.md` (AF-AP-29, AF-AP-34, AF-AP-39, AF-AP-40, AF-AP-42, AF-AP-59, AF-AP-62, AF-AP-63).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-02-support/B1-report.md --rev 088efef --map C=proofs/S0-02/check_buzz_authz.py
--map T=tests/test_s0_02_buzz_authz.py --map O=proofs/S0-02/oracle/denial_table.py --map B=proofs/S0-02/tools/build_fixtures.py`
plus a `--map` per buzz source file into `/home/user/nerdherderdani/buzz/` — MISS 0 or a finding (the lane reports UNCHECKABLE 20 and
names them; check that every one of the thirteen "also cited elsewhere as OK" claims is true); `ap_screen.py proofs/S0-02
proofs/S0-02/oracle proofs/S0-02/tools proofs/S0-02/tools/pc` (AF-AP-40 ×3, AP-32 ×3, AP-1 ×1) and `--tests` (AF-AP-34 ×4) — each
classified by RUNNING it; `git ls-files proofs/S0-02 | grep -c buzzacp.log` at the PIN must be 16 (AF-AP-62: the coordinator's
git-view gate found the bundles' logs gitignored — confirm the re-include holds and that `git archive 088efef` carries them).

## Items
1. **The oracle table against the source.** Reproduce all 20 rows by `sed -n` on the pinned checkout. Then attack the two
   DISCREPANCY claims that rest on a heuristic: `_production_verify_sites` cuts each `.rs` at its first `#[cfg(test)]` and drops
   `//` comments — plant (on a scratch copy of the checkout, pointed at by `S0_02_BUZZ_SRC`) a `verify_event` call inside a
   `mod tests` placed BEFORE the marker, a call through a helper (`fn check(e) { buzz_core::verify_event(e) }`) invoked on the
   channel path, a `verify_event` behind a `/* */` block comment, and a `use buzz_core::verify_event as v; v(&event)` alias: which
   does the claim-test miss? D3 (no per-event freshness rule): is `channel_since` the ONLY `created_at`-driven inbound behaviour —
   grep the whole `buzz-acp` crate for `created_at` and classify every site.
2. **The distinctness gate (`_observe_all` → count → `_check_named_observable`).** The lane's S1 says the ORDER is the whole point.
   Attack: two legs sharing an observable KEY with different texts (whitespace, case, a trailing period); one leg carrying TWO
   observables (which is chosen — first, last, both?); a relay observable planted in `buzzacp.log` and a buzz-acp observable in
   `delivery.json` (channel confusion); a sixth negative leg with a NEW distinct observable (does the gate require exactly five, or
   at least five?); the BLANKET bundle with ONE leg repaired (4 distinct of 5 — the reason must name the collapse). Re-introduce the
   assert-then-count order on a scratch copy and confirm BLANKET-ACCEPTED goes green (AF-AP-63 — the lane's own class).
3. **Freshness and the window.** `_check_freshness` measures age against the leg's own t0: a t0 in the future, a t0 missing, a t0
   that is a string, a `created_at` exactly at the window edge (±0, ±1 s). `RELAY_DRIFT_WINDOW_S` = 900 — is it RE-DERIVED from
   `MAX_TIMESTAMP_DRIFT_SECS` by a test that reads the source line, or a typed literal pinned by another typed literal? The stale
   specimen's `created_at` — by how much does it clear the window, and does the fixture builder derive it from the constant?
4. **The identity binding (D6/D7).** The delivered instance is bound to the committed template on kind, tags, content and the
   `created_at` policy, to the ROLE on pubkey, and the specimen key must NOT be the delivered key. Attack: tags in a different order;
   an extra tag; content with trailing whitespace or a different Unicode normalisation; an instance for a DIFFERENT channel id;
   a delivered event whose `id` is recomputed correctly after tampering (does the checker recompute the id from the fields, or
   trust the field?); `--synthetic-root` pointed at the REAL evidence root (can a synthetic anchor set be used to grade a real
   bundle, and would that be a finding?); the spec's `cmd` pinning of that parameter (`validate-ledger:275`).
5. **The replay leg** (first/second sub-legs, one id, exactly one turn): the second delivery with a turn; neither turning; two ids;
   the two sub-legs sharing one timeline file; the id equal but the second delivery's receipt `accepted: false` (a relay-side dedup
   — is that a buzz-acp replay observable or a relay one, and does the checker accept it as the replay proof?).
6. **The revoked leg.** `membership.json` names the delivered sender and records a COMPLETED removal; the event is FRESH. Attack:
   the removal receipt timestamped AFTER the delivery (does the checker order t_removal < t_delivery?); `removed: "true"` (a
   string); the receipt for the right key but a different channel; the leg's rejection text identical to `neg-unauthorized` (D5 —
   the structural separation: what exactly makes the two legs distinct in the checker's eyes, and can a bundle satisfy `revoked`
   with a `neg-unauthorized` copy plus a forged receipt?).
7. **The positive leg.** Exactly one `session/new` and one `session/prompt` carrying the fixture's nonce: the nonce in a
   `session/cancel` frame; the nonce in TWO prompts of one session; two sessions one prompt; a prompt whose nonce is a substring
   of a longer token; the receipt for a different event id (WRONG-EVENT-ID-ACCEPTED — reproduce).
8. **Masking and the canary.** A 64-hex token anywhere in `buzzacp.log` fails the leg — a 63-hex near miss, a 64-hex sha256 that
   is NOT a pubkey (a false red?), the masked form the real log uses (cite the real startup line's shape from the corpus); the
   DEBUG canary `startup watermark set to` required — present at INFO in a future buzz-acp (a false red?); `ignore_self=true`
   asserted from which artifact?
9. **The read class and the wall-clock cap (NOT_DONE 8).** FIFO-HANG proved `_require_file` load-bearing; the checker has NO
   SIGALRM cap. Measure: a FIFO at each of the six leg files is NAMED (six parametrisations) — and a FIFO at a path the checker
   opens OUTSIDE `_require_file` (the spec? the fixtures dir? `--synthetic-root` files?) — enumerate every `open`/`read_text`/
   `json.load` in the checker and the oracle by AST and say which are guarded. Then the dependency: the checker imports
   `_require_file` and the timeline reader from `proofs/S0-01/check_acp_conformance.py` BY PATH — with lane A5k about to change
   that file, what breaks S0-02 (a renamed helper, a moved `_require_file` into `pins.py` as VERIFY-CK12 recommends)? State the
   exact import surface S0-02 depends on so the coordinator can sequence the landings.
10. **The declared-input matrix** (A/B/C reproduced) and the PC path: `S0_02_BUZZ_SRC` absent-but-declared FAILS; the PC gate
    must pass with `pc_suite.sh`'s export — if the PC clone at `/home/rocco/s0-01-pinned/buzz` is not at 1c8321cd, the oracle
    tests must FAIL there, never skip (check what the test does when the commit differs).
11. **The PC runner + the delivery tool — READ, never run** (`proofs/S0-02/tools/pc/`): the NIP-98 header (`_nip98_header` —
    the payload hash, the `u`/`method` tags, the expiry); `BUZZ_PRIVATE_KEY` read ONCE from the environment (AF-AP-39 — never
    argv) and never logged; `errors="replace"` decodes recorded verbatim with no decision on them (class 7); `wait_turn_window`
    exits on `buzz-acp.exit` as well as on the turn; `stop_leg` by its own pidfile + `/proc/$pid/exe`, no name-based kill
    (the AF-AP-34 test); the RUST_LOG refusal (exit 3, the text) and the membership refusal (the `membership.json` shape printed);
    every external command enumerated — one the lane missed = a finding; `set -u` + traps (AF-AP-58).
12. **Fixture determinism.** `build_fixtures.py --check` byte-identical; the ONE flipped signature byte; the specimen seed. The
    hard question: how is a Schnorr signature byte-identical across rebuilds — RFC6979-style deterministic nonces in the signer
    (`proofs/S0-01/nostr_verify.py` — cite the line), or a fixed aux-rand? If the signer draws a random nonce, the committed-equals-
    fresh-build test is only green by luck — say which, from the code.
13. **The 18-class preflight** the lane ran (its class-3 and class-15 finds) — re-scan the 14 code/test files; a class the lane
    missed = a finding; the AF-AP-40 ×3 hits classified by RUN (the deferral gate: every timeline removed → exit 2 never 0; one
    timeline present → every later absence a Failure).
14. **The PC gate (the carve-out)**; paste beside the checkpoint's lines; agree.
15. **Mutants ≥ 32** (the lane's 24 + yours from items 2-8: the channel-confusion plant, the sixth-leg count, the t0-in-the-future,
    the recomputed-id tamper, the removal-after-delivery order, the nonce-in-cancel, the 63-hex near miss, the string `"true"`).
16. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census.
17. **The design.** D1: the component S0-02 names (buzz-acp) decides two of five reasons; the relay decides three at publish —
    is the seed's "buzz-acp rejects…" framing still met by grading the relay's receipt, or does the proof need the seed's block
    amended (say which words)? D4: five negatives + the revoked leg vs the seed's four — does the registry's
    `required_negative_controls` still bind? D6/D7: the template + specimen design and the closed `--synthetic-root` parameter —
    the smallest change that would remove the parameter (a keyed synthetic signer? committing the specimen private key as a
    labelled TEST key?) and whether it is worth it. The wall-clock cap: recommend the exact shape (S0-01's `check_bundle` alarm).
    Keep it to what you measured.

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-B1.md` — draft after EACH item — then return it whole. Findings: ALL, no severity
filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact red test, SOLID/UNSURE;
reproduced vs reviewed vs skipped; shared-tree hygiene; verdict MERGE-READY or NOT-READY with the blocking set, the cheapest path, and
the exact PC steps for the coordinator's live legs (what `run_s0_02_legs.sh` needs before it may run on the owner's PC: the RUST_LOG
seam, the membership write, the key).
