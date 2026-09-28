> **COORDINATOR NOTE (2026-09-28 12:5xZ):** the verifier returned this report as its final message (the harness refuses subagent report files). The coordinator saved the text as the report of record, extracted from the verifier's transcript (its SubagentHandback call at 12:55:34Z), never retyped.

# VERIFY-I59-LANDING report (task #315): the issue #59 batch landing attacked

Written 2026-09-28 12:5xZ (date -u 12:53:37Z). Lane: adversarial-verifier, sandbox, Opus 5.5. No subagents. Work ran 2026-09-26 11:2xZ–12:2xZ and 2026-09-28 12:2xZ–12:5xZ, with the weekly quota pause between. **No report file was written.** This session's harness forbids report .md files, so the whole report is here.

**Gate recommendation: MERGE-READY-WITH-FOLLOWUPS.** No finding meets the whole blocking predicate. This rests on an emulated CI, not real CI. It also rests on 67 tests that did not run here: `tests/test_lane_gate.py` (10, the disk floor) and 55 of the 57 tests in `tests/test_vendored_manifest.py` (never run whole). The landing does not touch either file's code or tests. There is one follow-up to take before the push, F1 (STATUS.md). It touches no attested file, so it costs no re-mint and no re-sign.

## What held (all reproduced here)
- [x] Item 1. The landing is exactly its parts. Nothing is extra.
- [x] Item 2. The re-mint is sound:
  - All 12 attestations equal my own computation.
  - The venue labels are unchanged.
  - Every changed field is explained.
  - The re-mint reproduces.
  - The declared inputs equal the reads and stats that strace observed, for all 12 proofs.
  - 15 of 15 one-byte negative controls invalidated exactly the right proofs.
- [x] Item 3. `check-proof-status.py` gives rc 0 with exactly twelve WARNING lines. The README re-sign procedure works on this state with a throwaway key: for one proof in both shapes, and for all twelve.
- [x] Item 4. All five stage0-ci jobs are predicted green: 0 failures in 5,800 emulated tests. All 334 skips are listed, and each is correct and visible.
- [x] Item 5. The round-4 delta holds: FU-7 is accurate, and the FU-8 tests kill V-S4 and V-L4. The builder's re-listing of those two rows is legitimate. The builder's 18 rows are 18 KILLED at the landing.
- [ ] Item 6. The quirk line is true except for one overclaim (F3).

## Finding inventory (no severity filter)

**F1 FOLLOW-UP (fix before the push). The landing makes STATUS.md false.**
- What STATUS.md says (lines 11-12 and 68-79 at the landing; origin 2c234ca has the same text): "the eight tag objects committed as `docs/governance/tags/accepted-<id>.tag` … so every anchor is current". Each proof row says "the tag object committed as `docs/governance/tags/accepted-S0-NN.tag`".
- What the landing does: it deletes all twelve tag files and puts all twelve anchors at PENDING.
- Evidence: VERIFIED.
  - Reproduce: `git show <landing>:STATUS.md | grep -c 'docs/governance/tags/accepted-'` prints a non-zero count.
  - Beside it: `git show <landing> --stat | grep -c 'docs/governance/tags/accepted-S0-..\.tag.*13 -'` prints 12 (the twelve deletions).
- Contract mapping: none frozen. The closest rule is CLAUDE.md's "hollow green lives in PROSE too".
- Material effect: none on the proofs, the ledger or the checker. It does misstate the governance state in the file the owner reads before re-signing. It is not blocking, because STATUS.md is not required evidence of this increment.
- Suggested fix: one STATUS.md edit (all twelve re-minted by the issue #59 batch, anchors PENDING the owner's re-sign). The same edit is needed again after the re-sign, because the rows name the old commits.

**F2 FOLLOW-UP. FU-4's `-rs` removes the FAILED and ERROR lines from CI's short summary.**
- Cause: pytest's `-r` replaces the default `fE`.
- Evidence: VERIFIED with pytest 9.1.1. Take a file with one failing, one skipped and one erroring test:
  - `-q` lists `FAILED …` and `ERROR …`.
  - `-q -rs` lists only `SKIPPED [1] …: a named reason`.
  - The count line and the exit code do not change.
  - To reproduce: `python -m pytest -q -rs <that file>`.
- Material effect: none on the verdict. The CI log loses its compact list of failing tests; the tracebacks stay.
- Suggested fix: use `-rfEs` on the CI line and in the line that `tests/test_no_laya_in_gates.py` pins. Neither file is attested.
- `scripts/test_summary.sh` has the same trait. That predates the landing.
- FU-4's pin is real: with `-rs` removed from the workflow, `test_real_workflow_step_that_sources_is_refused[YH-3,YH-4]` fail ("2 failed, 131 passed"). The pin is an exact-text match.

**F3 FOLLOW-UP. The new env-tool-quirks line overclaims.**
- True claims:
  - The allowed path form (repo-relative, regular files, no globs, no `..`, no symbolic links) matches `_extra_inputs` and `_is_regular_file`.
  - `proof_attestation()` hashes the declared files.
  - The guard watches opens, imports and `os.stat`, `os.lstat` and `os.access`, with the three wrapped in `HOOK`.
  - The Fubuki checkout and the interpreter are not attested.
- The overclaim: "reds on an undeclared one" leaves out the guard's named blind spots (unhooked or non-Python children, C-level or `dir_fd` stats, `readlink`, tests of directories or absence, directory listings, C-level readers). It also leaves out that on CI the guard skips S0-07 and S0-11.
- Suggested addition: "(blind spots in its docstring; CI skips S0-07 and S0-11)".
- A second point, older than the landing: the ATTESTED INPUTS line above it still says `--venue sandbox` "for each minted id". That conflicts with the `pc-bridge` labels of S0-01, S0-02 and S0-05.

**INFO**
- I-1. S0-07's recorded positive-leg `stdout_sha256` (5e88f0e1…) depends on the path where it was minted, the coordinator's worktree `/home/user/i59-landing`.
  - I re-ran the leg and swapped only the path. `/home/user/i59-landing` gives 5e88f0e1… (the landing's value), `/home/user/agent-factory` gives 87cac7a8… (the parent's value), and my worktree gives c68f1dee….
  - The verdict is the same everywhere. The S0-07 ledger digest carries the path, so the landing records a path that disappears.
  - This is the builder's A3 and VERIFY-I59-A's I-8.
- I-2. On CI, 16 of the landing's 133 new test items skip:
  - 14 I59-B runner tests, marked `NEEDS_ROOT` or `NEEDS_NETNS`, including the sudo handback and the INT/TERM/HUP signal tests;
  - the guard's S0-07 and S0-11 cases.
  - Each skip is correct and now visible. The sudo handback is tested only on root venues.
- I-3. `tests/test_s0_07_fubuki_corrections.py:15` hardcodes `/home/user/nerdherderdani/fubuki-os`. CI therefore always skips its 4 tests, although CI provisions `FUBUKI_OS_ROOT`. This predates the landing (task #320 area).
- I-4. The manifest header "Generated from tree `e37a9c4a…`" names eb48880's tree, from before the rebase. It is information only, and `--check` passes.
- I-5. Origin moved to 2c234ca. From 8992772 to 2c234ca, no attested or code path changed. The landing merges cleanly onto 2c234ca (`git merge-tree --write-tree`, rc 0, run in my scratch clone).
- I-6. The plan's #315 said to re-mint "on the PC". The landing re-minted in the sandbox, following the I59-A report's section 5 and its reasons. The labels are unchanged.
- I-7. The premise's HUP flake (task #331) was not reproduced. It belongs to VERIFY-I59-BCE's lane, and it skips on CI.

## Evidence by item

**Item 1: rebuild.**
- I extracted the parent's versions of the 43 changed files and applied the four patches. Their sha256 prefixes match the premise: 342e8d42 (A), c46b5dff (B), d048d18f (C), ea9da227 (E). The patches are identical at 8992772 and at the landing.
- The eleven patched files are byte-identical to the landing's.
- The other 32 files:
  - FU-4: one CI line and the line the test pins.
  - The quirk line: one added line in both `.claude` and `.agents` copies, which are identical.
  - The manifest: two header lines and the `.claude/ (first-party)` row. `vendored_manifest.py --check` says "PASS: … matches 10 vendored roots".
  - The re-mint: 12 `result.json` files and `ledger.json`.
  - The anchor step: 12 tag files deleted, 12 PENDING lines (one under each PROOF-STATUS line, and nothing else in the ledger), and `EXPECTED_PENDING` = the twelve.
- No test function was removed (an AST diff shows 43 added, 0 removed). The only mode changes are the new test file and the 12 deletions.

**Item 2: the re-mint.**
- My attestation instrument used git blobs of the committed tree and PyYAML for the registry. It found "ALL ATTESTATIONS EQUAL". Key counts: 247, 214, 96, 44, 63, 168, 14, 30, 12, 12, 13, 18.
- `env_fingerprint` is identical to the parent's for all 12 proofs: `pc-bridge:vm` for S0-01, S0-02 and S0-05, and `sandbox:vm` for the rest.
- Changed against the parent:
  - `recorded_at` and the run timestamps.
  - `digest` (a hash over the runs, timestamps included).
  - In the attestation, the hashes of `scripts/validate-ledger`, `proofs/registry.yaml` and `result.schema.json`.
  - Keys added: S0-02 +6, S0-03 +5, S0-05 +1, S0-06 +2, S0-09 +1, S0-10 +1, S0-12 +4 (the declared inputs), and S0-08 +1 (its nested `blocked.json` fixture).
  - The proofs' own changed files: S0-03 `check_omniroute_roundtrip.py`, S0-04 `tools/pc/capture_leg.py`, S0-05 `tools/pc/run_s0_05_units.sh`.
  - S0-07's `runs[0].stdout_sha256` (I-1).
  - Nothing else: exit codes, commands, failure reasons and negative controls are all equal.
- The ledger's normalized digest strips timestamps, `env_fingerprint` and `digest`. All twelve still change, because every attestation changed.
- In my worktree:
  - `integrity` rc 0 (12 PRESENT, 0 INVALID; 9/9 and 3/3).
  - `ledger-gen` twice gives identical output that equals the committed ledger.
  - `integrity --ledger` rc 0, and `stage1-gate` rc 0.
- A re-mint of all twelve through `scripts/proof-runner` under strace (the section 5 venues) ran 12/12 rc 0. It gives attestations equal to the landing's and runs equal apart from S0-07's path. VERIFY-I59-A's strace parser (`st_compare.py`) prints "ALL MATCH"; S0-12's two files are stat-only. There were no uncovered reads, and the only writes were `__pycache__`.
- One byte flipped in each of 15 files, then `integrity --ledger`:
  - `pins.py` → S0-01, S0-02, S0-03, S0-05 INVALID.
  - `upstream.lock.yaml` → S0-06, S0-12.
  - `LICENSE-DECISION.md` → S0-12.
  - `identities.json` → S0-01, S0-02.
  - `check_acp_conformance.py`, `check_initialize.py`, `negative_contract.py` and `nostr_verify.py` → S0-01, S0-02, S0-03.
  - `SBOM.yaml`, `THIRD-PARTY-NOTICES.md`, the two ADRs, the S0-06 tuple fixture and the S0-08 fixture → only their declarer.
  - `README.md` → none, rc 0.
  - Result: "ALL NEGATIVE CONTROLS EXACT". The expected sets came from the strace readers, and each invalidation named exactly that file.

**Item 3: the anchors.** In my worktree: rc 0, 0 lines on stdout, 12 lines on stderr, all of the form `proof-status: WARNING S0-NN: ACCEPTED with the anchor PENDING … — not owner-verifiable yet`.

The re-sign experiment:
- Setup: a sparse `--shared --no-tags` clone at the landing commit. A throwaway ed25519 key in a scratch GNUPGHOME; its public half was written into the clone's `owner-signing-key.asc`.
- Signing and import:
  - `tag -s accepted/S0-05` on the landing commit.
  - `git cat-file tag` into `docs/governance/tags/accepted-S0-05.tag`; `hash-object` reproduces the object; then the ref was deleted, which is CI's shape.
- Negative control n2 (tag present, PENDING line kept): rc 1, "exists but the ledger still declares PROOF-ANCHOR PENDING".
- With the PENDING line and the `EXPECTED_PENDING` entry removed:
  - rc 0 and 11 WARNINGs; S0-05 appears nowhere, so it reads verified.
  - The same after the ref was restored with `update-ref`.
  - The same after a commit.
  - `tests/test_proof_status.py`: "pytest-exit: 0 / pytest-summary: 33 passed in 4.08s".
- Negative control n1 (a tag on the parent, which holds the old result): rc 1, "the minted proofs/S0-05/result.json changed since accepted/S0-05".
- Negative control n3 (`EXPECTED_PENDING` left at twelve): "pytest-exit: 1 / pytest-summary: 1 failed, 6 passed, 26 deselected in 1.74s".
- All twelve signed, 12 tag files, no PENDING lines, `EXPECTED_PENDING = set()`: `check-proof-status` rc 0 with no output; "pytest-exit: 0 / pytest-summary: 33 passed in 5.26s".
- Origin has no tags (`git ls-remote --tags origin` is empty).

**Item 4: CI emulation.**
- Setup:
  - A `--shared --no-tags` clone at the landing commit, owned by uid 65534.
  - A Python 3.12.3 venv with CI's packages: pytest 9.1.1, pyflakes 4.0.0, jsonschema 4.25.1, rfc3339-validator 0.1.4, PyYAML 6.0.3.
  - `S0_01_VENUE=ci`; `FUBUKI_*` from `fubuki_pin_sync.sh`, sourced from the local checkout at the lock's commit.
  - `/home/user/nerdherderdani` hidden under a tmpfs in a private mount namespace.
  - HOME set to a directory holding CI's git identity.
  - Counts from `scripts/test_summary.sh`, minus its four sandbox-default exports so the environment matches CI's. Its `S0_01_REAL_LEG_DIR=/root/…` default would raise PermissionError as non-root, where CI simply skips.
- Collected: 5867 tests. Run: 110 files set=0b079a70ddb7, in 15 chunks. Pasted:
  - A: 221 passed, 76 skipped in 10.27s
  - B: 477 passed, 24 skipped in 199.80s
  - C: 385 passed, 2 skipped in 39.16s
  - D0–D3: 142 passed in 286.36s · 100 passed, 14 skipped in 176.14s · 70 passed, 48 skipped in 308.14s · 94 passed in 151.54s
  - E1: 348 passed in 99.78s
  - E2: 592 passed, 7 skipped in 253.45s
  - F (tests/red): 206 passed in 80.74s
  - G1: 338 passed, 12 skipped in 71.37s
  - G2: 499 passed, 4 skipped in 44.34s
  - H: 650 passed, 56 skipped, 8 xfailed in 176.22s
  - I: 662 passed, 52 skipped in 185.27s; re-run as you asked: 662 passed, 52 skipped in 267.78s
  - J: 674 passed, 39 skipped in 412.66s
  - Every pytest-exit was 0. Sum: 5458 passed, 334 skipped, 8 xfailed = 5800; 0 failed, 0 errors.
- The two committed-manifest tests: 1 passed in 36.71s, and 1 passed in 7.54s.
- Predictions by job:
  - `tests`: GREEN. Both lint steps rc 0.
  - `ledger-integrity`: GREEN. `ledger-gen` then `git diff --exit-code` rc 0; `integrity --ledger` rc 0, 12 PRESENT.
  - `stage1-gate`: GREEN, rc 0.
  - `planning`: GREEN. rc 0 with system Python 3.11 and with 3.12, 12 WARNING lines, "passed".
  - `harness-suites`: GREEN, "ALL SUITES PASSED" (test_sync_skills 34, test_context_mirrors 11).
- Skips: 334 in 28 groups, each printed with its reason under `-rs`, and each firing only on its named venue cause.
  - Root or netns: S0-05 76, S0-11 10.
  - Declared real-leg corpus: 71.
  - Buzz checkout: 24.
  - Tools not installed: codemap 36, graft 35, slopo 50, sentrux 4.
  - Laya venue declarations: 17.
  - Hardcoded S0-07 path: 4 (I-3).
  - The guard's S0-07 and S0-11: 2.
  - Other single causes: tmpfs mount 1, Node version 2 (may run on CI if CI's Node is 22.18 or later), MoJev declaration 1, SYNTH1's fixed guard 1.

**Item 5: round 4.**
- FU-7: the parsed schema equals the parent's apart from the description, and `check_schema` passes. The description matches the code.
- My mutants:
  - V-S4 against the re-listed tests: KILLED 2/2. Against VERIFY-I59-A's original row: SURVIVED 0/4, which confirms why the rows needed re-listing.
  - `access` unwatched: KILLED. `lstat` unwatched: KILLED. A stat with a positional argument not recorded: KILLED.
  - V-L4 against the multibyte test: KILLED. Against the ASCII case: SURVIVED, as the builder said.
  - A latin-1 byte count: KILLED.
  - "ROWS=8 AS-EXPECTED=8".
- The builder's `mutate_r4.py` at the landing: "EXPECTED=18 KILLED=18 SURVIVED=0 INVALID=0".
- I-14: the docstring names the `dir_fd` and `readlink` blind spots.
- Root at the landing, 4 files set=379203742124: "pytest-exit: 0 / pytest-summary: 195 passed in 53.36s".

## Reproduced, reviewed statically, skipped
- **Reproduced:** everything above.
- **Reviewed statically:** the landing diff; the governance README; the `check-proof-status.py` and `ledger-gen` normalization; the skip guards; the stale-context sweep (STATUS.md is stale; README.md, the governance README and the task ledger are consistent).
- **Skipped:**
  - Real CI.
  - The whole suite as root (the coordinator's premise run).
  - The PC.
  - VERIFY-I59-BCE's scope: the B/C/E semantics and the HUP flake.

## NOT done
- `test_lane_gate.py`: it refuses below 1,500 MB free, a venue fact.
- 55 manifest tests: the whole-file ban; the file is untouched by the landing.
- Real CI. The emulation differs from CI in these ways:
  - uid 65534, not the runner's uid;
  - chunked runs, not one process;
  - `-p no:cacheprovider`;
  - the Fubuki pin cloned from a local source.
- The report file (the harness instruction).

## DISCREPANCIES
- D1. The brief's PIN paragraph names the parent as eb48880. The landing's parent is 8992772, after a docs-only rebase. The premise block and your message agree on 8992772.
- D2. Your message said chunk I "never returned". My transcript and its log had the full result. The re-run gave the same counts.
- D3. The premise's suite totals 5811 tests (manifest file ignored). My collection gives 5810 without the manifest file, as uid 65534 under `ci`. The 1-test difference is not explained; I did not re-collect as root.
- D4. `scripts/import_owner_tags.py` (plan, task #306) does not exist. The "committed way" is the README's tag file plus `hash-object` or `update-ref`, which is what I used.
- D5. The brief estimates a worktree at about 300 MB. Measured: 215 MB, and 217 MB for the CI clone.

## Boundary and cleanup
- Made and removed: worktree `/tmp/vland-wt` (`git worktree remove --force`); the two scratch clones; the venv; the Fubuki pin; the throwaway GNUPGHOME (its agent killed first); all `/tmp/vland-*`.
- The shared repository holds no `accepted/*` refs, and its dirty files are other lanes'.
- **Deviation (mine):** I ran `git merge-tree --write-tree 2c234ca <landing>` once in the shared repository, with the output discarded. It wrote unreferenced loose objects, including the merged tree 03d6df08…, which I measured as present. It changed no ref, index, tag or working tree. I did not delete these objects on purpose: a rebase of the landing onto 2c234ca creates the same objects, and deleting them could corrupt that commit. `git gc` prunes them if nothing references them.
- I ran `scripts/fubuki_pin_sync.sh` from the path `/home/user/i59-landing`. It only read there and wrote only to my scratch.
- Network reads: `git ls-remote --tags origin`, and one pip install into the scratch venv.
- I read no secret, used no real key, used no PC bridge, took no outward-facing action, and served on no model other than Opus 5.5.
