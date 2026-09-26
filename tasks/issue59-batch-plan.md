# The issue #59 batch: every attested follow-up in one re-mint and one re-sign (plan, 2026-09-26 03:5xZ)

STATUS: PLANNED (coordinator, 2026-09-26 03:58Z; origin 4b5434f). Not dispatched. Tasks #312-#315 in `todo/BUILD-TASKLIST.md`.

## Why now

All twelve Stage 0 proofs are ACCEPTED (D-094). The open verify follow-ups that change ATTESTED files force a re-mint, and a
re-mint makes the owner's acceptance tags stale. Issue #59's ordering note: batch them, so the owner re-signs once. After the
batch comes the Stage 0 pull request to `main` (only the owner merges it), then Stage 1 (`docs/07_BUILD_PLAN.md`).

## The set, measured (not only the instance the verifier named)

Issue #59 F-1 names S0-05 (and S0-03 in passing): a checker imports a file outside its own proof directory, and
`proof_attestation()` (`scripts/validate-ledger`, `ATTESTATION_CLOSURE` + `proofs/schemas/*.json` + `proofs/<id>/**`) never
hashes it, so a change there leaves the proof PRESENT. The coordinator's sweep of every proof (an AST pass over string
constants and path-based imports, then a grep for `spec_from_file_location`, `sys.path` and root-relative reads) finds the
class is wider:

| Consumer (file:line at 4b5434f) | Outside input | How it is reached |
|---|---|---|
| S0-02 `check_buzz_authz.py:47-49`, `:87` | `proofs/S0-01/check_acp_conformance.py`, `proofs/S0-01/tools/nostr_verify.py`, `proofs/S0-01/fixtures/identities.json` | `spec_from_file_location`, reads |
| S0-02, S0-03 (transitive, through S0-01's checker `:37-38`, `:99-102`) | `proofs/S0-01/pins.py`, `check_initialize.py`, `negative_contract.py`, `tools/nostr_verify.py` | the loaded checker's own imports |
| S0-03 `check_omniroute_roundtrip.py:104`, `:114` | `proofs/S0-01/check_acp_conformance.py` | `spec_from_file_location` |
| S0-05 `check_egress.py:117`, `:125` | `proofs/S0-01/pins.py` | `spec_from_file_location` |
| S0-06 `check_four_scope.py:60`, `:213` | `upstream.lock.yaml` (the ai-memory pin) | `read_text` |
| S0-07 `check_fubuki_corrections.py:21-24`, `:212-215` | the Fubuki upstream checkout (a path from argv, outside the repo) | `sys.path.insert` |

Open questions for the build lane (not facts): does `pins.py` read any data file? Does S0-07's checker verify the checkout's
commit against `upstream.lock.yaml`, and should the lock file then be its declared input? Do the PC capture tools (shell)
count, or only what the checker reads when it grades?

## The increments

**#312 I59-A, the tooling (re-mints all twelve).** A registry field per proof, `extra_attested_inputs`: repo-relative paths
of regular files, no globs, no `..`, no symlinks; `proof_attestation()` hashes them beside the proof's own files (one function
serves the runner and the validator); a missing or irregular path is a named registry finding. A drift guard: a test that
enumerates each proof's path-based imports and root-relative reads statically and fails when one is undeclared (the SET
above is its first oracle). Declare the set for S0-02, S0-03, S0-05, S0-06 (and S0-07 per the lane's answer).
Rejected: (a) an automatic import closure at attestation time (a path built at run time evades a parser, and an upstream
checkout outside the repo cannot be enumerated); (b) attesting all of `proofs/**` for every proof (any change to one proof
would re-mint all twelve, every time); (c) copying S0-01's files into each consumer (the checkers import by path on purpose:
"never copied").

**#313 I59-B, S0-05 (re-mints S0-05).** F-6: reword limit 8 (containment holds; the census admits any end state equal to a
pure append). The AF-AP-169 runner guard (refuse an evidence root inside a git work tree; hand what it writes to
`SUDO_UID:SUDO_GID`). F-2 (a pid reused with another start time) and F-3 (an `O_RDWR` holder): tests only; each kills its
named mutant (M1, M4) as a FAILED test. Census shapes 2c, 2i and 2j run on the PC (the sandbox's classifier stopped the
verifier's helper for them).

**#314 I59-C, S0-04 (re-mints S0-04).** VERIFY-S0-04-LEAK-R1's G2: `do_config` catches every exception of `yaml.safe_load`
and reports the error class and position only, never the value (a `!!int` or `!!float` tag makes PyYAML raise a plain
`ValueError`, and `main`'s catch-all prints it); G5: tests for a ParserError and a ComposerError (mutant D5 survives today);
G6: pin the tail bound (a 4-segment catch, a 5-segment pass) and the `_ENV` exclusion (A7-A10 survive today).

**#315 I59-D, the re-mint and the re-sign.** After #312-#314 land and their verify lanes pass: re-mint all twelve on the PC
from the committed bundles; one verify lane on the whole batch; the owner re-signs all twelve tags in one command (D-069's
form); `scripts/import_owner_tags.py` (task #306) imports them; `tests/test_proof_status.py`'s `EXPECTED_PENDING` stays empty.

## Order and venues

#312 first (it changes the attestation every other increment re-mints under); #313 and #314 in parallel after it, each in
its own boundary; #315 last. Build lanes run on the PC Hermes lane (the default route; one long-context local lane at a time
while the cloud route is out, D-061/D-062) once HCTX1 (task #310, D-097) lands, or as sandbox agents when a slot is free.
Each gets an independent verify lane before its landing is called good.

## Premortem (how this batch fails)

1. The drift guard misses a read built at run time, so a new undeclared input slips in: the guard's negative control plants
   one of each shape (a `spec_from_file_location` on a joined path, a `read_text` on a root-relative path).
2. The re-mint happens before every attested change has landed, and a second re-mint (and re-sign) follows: #315 starts only
   when #312-#314 are all verified.
3. The new field breaks the registry's own schema check or the CI `stage1-gate`/`ledger-integrity` jobs: the validator's
   tests and the CI job list are in #312's gate.
4. A re-mint on the PC changes a bundle (a live capture re-run by mistake): the re-mint runs the checkers on the COMMITTED
   bundles only, and the brief says which verb may change them (none).
