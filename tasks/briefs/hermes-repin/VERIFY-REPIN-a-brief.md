# VERIFY-REPIN-a — the targeted adversarial verify of the Hermes LANE-runtime pin entry

PIN: 905bb1d (origin; the REPIN-a landing). Component: `upstream.lock.yaml` (the appended `lane_runtime.hermes-agent-lane-runtime` section, lines 161-173), `tests/test_upstream_lock_lane_runtime.py` (8 tests), `docs/HARNESS-PORTS.md` §12. Contract (frozen): `tasks/briefs/hermes-repin/REPIN-brief.md` §REPIN-a + D-048 item 3 (`docs/08_DECISION_LOG.md`). The builder's report `tasks/briefs/hermes-repin/REPIN-a-report.md` is an input to attack.
ROLE: adversarial-verifier (Opus 5, sandbox); READ-ONLY on the tree (scratch copies only); never commit; no bridge use — the PC-side values are attacked by CONSISTENCY, not re-measured.
DISPATCH RULE: only after the J0-a probe lane has finished (no timing on a contended box).

## Items
1. Reproduce: the 8 tests twice; `bash scripts/verify-planning-repo.sh`; `python3 scripts/validate-ledger integrity --root .`; the S0-12 suite — paste.
2. The golden of `selected_core.hermes-agent`: does the test assert the LINES or a parsed dict? A whitespace-only edit of the existing entry (a scratch copy) — caught or not? Is that in contract (the brief says "byte-identical")?
3. The entry's key set: is it CLOSED (an extra key `foo:` in a scratch copy → red)? The 7-hex control — does a 39-hex or a 41-hex commit also fail by name? An uppercase hex?
4. Consumers (the builder claims none reads `lane_runtime`): verify with two instruments (graft `ask` + grep over scripts/, proofs/, tests/, harness-ports/, .github/) that the claim holds, and state plainly that the pin is UNENFORCED until REPIN-b; is `docs/HARNESS-PORTS.md` §12 honest about that (a hollow green in prose is a finding)?
5. Internal consistency of the recorded facts against the primary sources in the repo: D-043's row (527da60 vs b3399c1, 31,816 commits, 3939 files, SQLite versions), the `hermes-agent` entry's `observed_version: 0.21.0`, the incident-log entry for the 2026-09-08 `hermes update` — any contradiction is a finding.
6. The `verified:` field's count (43) — reproduce the builder's grep from its report; is the grep's shape sound (does it count ledger notes, or matches of words like HOME in unrelated lines)? If the count is not reproducible or the grep over-counts, the field is a finding (a typed number in disguise).
7. Report lint on the builder's report (paste).

## Output
`tasks/briefs/hermes-repin/VERIFY-REPIN-a-report.md`: observations with file:line + SOLID/UNSURE, the GATE RECOMMENDATION with the blocking predicate applied. `report_lint --min-refs 8` (≤ 3 rounds).
