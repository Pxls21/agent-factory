# PC lane — B3 (S0-02 round 3: closure is containment, the receipt typed at the producer, the key normalised first, D3 narrowed, the tolerance bound, the removal receipt labelled)

PIN: 887f341

Role: code-implementer. Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first; it maps every sandbox path in the brief.

**The brief governs**: `tasks/briefs/s0-02-b3-buzz-authz-closure-is-containment-the-receipt-typed-the-key-normalised-first.md` —
READ IT WHOLE and build items 1-9 in order. Your worktree IS `git archive <PIN>`: VERIFY-B2's report
(`tasks/briefs/s0-02-support/VERIFY-B2-report.md`), the B2 brief and report are in the tree. Save your report at
`tasks/briefs/s0-02-support/B3-report.md` inside your tree, draft after EACH item (the incremental rule), and return it whole as
your final message.

Venue notes specific to this build:
- The pinned buzz source is `/home/rocco/s0-01-pinned/buzz` (export `S0_02_BUZZ_SRC` to it — the test's default is the sandbox
  path); venue exports `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`;
  `/home/rocco/venv-agent-factory/bin` FIRST on PATH; an absolute `--basetemp` under your lane's scratch dir; the four-file gate
  runs under a minute with `-n 8` — ONE foreground `lane_gate.sh` call, pasted.
- No relay delivery, no live leg, no membership write on this host — the live legs are the coordinator's. The relay's keys and the
  NIP-98 identities are never read or printed beyond the test identities' pubkeys; `deliver_event.py` and the runner are read,
  `bash -n`/pyflakes-checked and unit-tested in-process, never run against the owner's relay.
- `proofs/S0-01/*` is read-only (P5c, N5j, B5k, D5n are editing S0-01 in their own trees); S0-02's own `_require_real_dir` is
  yours, S0-01's `_require_dir` is not.
