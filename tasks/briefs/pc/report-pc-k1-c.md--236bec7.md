NOT built. K1-c stopped on a new premise conflict at PIN `236bec7`; no manifest was minted.

BLOCKER (resolved by AMENDMENT 1)

The 2026-09-08 lane correctly stopped because the original item-2 policy bounded symlinks by each vendored root. Its real run refused `.claude/skills/design-artifact -> ../../.agents/skills/design-artifact`. `K1-AMENDMENT-1.md:10-18` changed the boundary to the repository root while retaining fail-closed refusal for a dangling link.

CURRENT BLOCKER (not resolved)

AMENDMENT 1 says that the six real `.claude/skills/*` links pass and that dangling links are refused. At PIN `236bec7`, all six links dangle because their named targets are absent. These requirements are jointly unsatisfiable without changing repository content outside K1's boundary or weakening the mandated guard. I did neither.

VERIFIED PREMISE CHECK

- `K1-AMENDMENT-1.md:12-18` requires target-string hashing, repository-root containment, and refusal by name for both outside-repository and dangling links.
- Worktree probe at `236bec7`:
  - `.claude/skills/design-artifact`: link `yes`, target `../../.agents/skills/design-artifact`, resolved target exists `no`.
  - `.claude/skills/html`: link `yes`, target `../../.agents/skills/html`, resolved target exists `no`.
  - `.claude/skills/html-diagram`: link `yes`, target `../../.agents/skills/html-diagram`, resolved target exists `no`.
  - `.claude/skills/html-plan`: link `yes`, target `../../.agents/skills/html-plan`, resolved target exists `no`.
  - `.claude/skills/html-prototype`: link `yes`, target `../../.agents/skills/html-prototype`, resolved target exists `no`.
  - `.claude/skills/html-wireframe`: link `yes`, target `../../.agents/skills/html-wireframe`, resolved target exists `no`.
- `git ls-tree -r --name-only <rev> -- <six target paths>` returned `matching_target_paths=0` for both `be5cf35` and `236bec7`.
- `git log --oneline --all -- <six target paths>` returned no commit.
- `git rev-parse --show-toplevel` resolves to this lane tree, so the repository-root boundary itself is unambiguous.
- Between `be5cf35` and `236bec7`, `upstream.lock.yaml` gained only the D-032 local-model-server entry; `SBOM.yaml` had no diff. The `.agents/skills` and `.claude` trees changed, but none of the six target paths exists at either PIN.

REAL COMMAND OUTPUT

1. Generator, real tree:

`python3 scripts/vendored_manifest.py --root . --write`

`write_rc=1`
`FAIL: escaping symlink refused in /home/rocco/agent-factory/.lanes/pc-k1-c.md--236bec7/tree/.claude: skills/design-artifact -> ../../.agents/skills/design-artifact`

The recovered draft still enforces the old vendored-root boundary, so it stops on the first cross-root link before it can distinguish the new dangling-target defect. Applying AMENDMENT 1 faithfully would still stop because that same resolved target does not exist.

2. Recovered draft tests, exact required runner:

`scripts/test_summary.sh -n 8 --basetemp /home/rocco/agent-factory/.lanes/pc-k1-c.md--236bec7/scratch/bt-final tests/test_vendored_manifest.py`

`9 failed, 5 passed in 1.97s`
`pytest-exit: 1`
`pytest-summary: 9 failed, 5 passed in 1.97s`

The failures reproduce the old root-boundary blocker. They do not establish a valid amended implementation.

3. Syntax and lint:

`python3 -m py_compile scripts/vendored_manifest.py tests/test_vendored_manifest.py`

`py_compile_rc=0`

`python3 -m pyflakes scripts/vendored_manifest.py tests/test_vendored_manifest.py`

`tests/test_vendored_manifest.py:3:1: 'dataclasses' imported but unused`
`pyflakes_rc=1`

This is a defect in the recovered draft. I did not repair it because the premise conflict requires STOP rather than further implementation.

FILE IDENTITY

The recovered lane patch remains the proposal under review; I reverted my attempted amendment edits after the premise conflict became definitive.

- `scripts/vendored_manifest.py`: staged draft SHA-256 `34bed8991febc377b676094931662dac741e7387511705dc581281ab7a4ac574`; 559 lines.
- `tests/test_vendored_manifest.py`: staged draft SHA-256 `4c483bfcc046c5ba7911a713e84257f7e48564bd1536a845a12818728ed4cf90`; 320 lines.
- `sandbox-kit/VENDORED-MANIFEST.md`: absent.
- This report is the only K1-c report edit.

ITEM STATUS

- Item 1: DRAFT ONLY. The stdlib generator and `--write`/`--check` interface exist in the recovered patch, but the real tree cannot reach manifest generation.
- Item 2: BLOCKED. The amended repository-root rule cannot simultaneously allow the six real links and refuse dangling links at this PIN.
- Item 3: DRAFT ONLY. Header generation exists but no real artifact was produced.
- Item 4: DRAFT ONLY. SBOM/lock parsing exists; no full real-tree generation reached the agreement gate.
- Item 5: NOT complete. The required deterministic suite is red (`9 failed, 5 passed`).
- Item 6: NOT complete. No admissible mutant table exists while the base suite is red; the recovered wrapper also over-selects its own parametrized test in nested runs.
- Item 7: NOT complete. No manifest, no two successful writes, no two `--check` lines, no two manifest SHAs, no lane-gate RESULT lines, and no green pyflakes run exist.

DISCREPANCIES

- The continuation brief says the six links are committed and pass under AMENDMENT 1. The links are committed, but all six targets are absent at both referenced PINs. They therefore dangle and must be refused by AMENDMENT 1 itself.
- The continuation says the prior `9 failed, 5 passed` are downstream of one boundary rule. That exact count reproduces, but after the boundary change the absent targets introduce a second independent failure condition.
- The original brief's report path says `tasks/briefs/kit-support/K1-report.md`; the continuation explicitly assigns `tasks/briefs/kit-k1-support/K1-report.md`. This report follows the continuation.
- `scripts/why.sh` cannot produce history for the new staged files; it returned `fatal: ambiguous argument ''` because no committed symbol revision exists.
- Code-intelligence pack: `lane_context: pack written to ../scratch/k1-final-pack.md (406 lines)`.
- GitNexus post-batch result: `No changes detected.` The clone index cannot see lane-only staged additions, so this is not evidence of no lane diff.
- AP screen classification: production `3 hits` (`AP-32` at `M:113` and `M:175` are required SHA-256 digest operations; `AF-AP-40` at `M:154` is the regular-file branch, not a symlink-following claim). Test screen `2 hits` (`AP-66` at `T:89` and `T:223` are deliberate fixture mutation via `setattr`, not mocks of the production sink).
- Bounded report lint final run: `report_lint: 9 refs — OK 3, NEAR 0, MISS 6, UNCHECKABLE 0, UNRESOLVED 0 (worktree)` and `report_lint: FLOOR — OK 3 < --min-refs 10: the report cites too little to be graded`. The misses are self-referential parses of the AP-screen references and the pasted prior lint line. I stopped at the required three-round bound because this blocker report has no landed implementation claims to pad with artificial source references.
- `sandbox-kit/VENDORED-MANIFEST.md` was not created. Creating it would require bypassing a mandated fail-closed check.
- `lane_gate` was not run because its subject cannot satisfy the frozen contract and the base focused suite is red.

SELF-ATTACK

1. Could the targets be present but hidden by a worktree quirk? Ruled out with three independent checks: `test -e` says `no` for every resolved link, `git ls-tree -r` finds zero target paths at both PINs, and `git log --all -- <paths>` finds no introducing commit.
2. Could repository-root containment alone make dangling links acceptable? No. `K1-AMENDMENT-1.md:15-18` separately requires dangling links to be refused and explicitly names a dangling-link negative test.
3. Could K1 create the six missing targets? No. The boundary permits only the generator, its test, the generated manifest, and this report. Creating `.agents/skills/*` would be an out-of-scope repository-content change and would silently alter the digest substrate.

NOT-DONE

- No amended production implementation was landed.
- No generated manifest was written.
- No write/check determinism evidence or manifest SHA pair exists.
- No green pytest, pyflakes, lane-gate, mutation, or report-lint-floor result exists.
- Independent adversarial verification has not run; this build-lane report is a proposal only.

GATE RECOMMENDATION

CONTRACT-INVALID. The coordinator must either supply the six real target trees at the pinned revision or amend the contract to define how these six dangling committed links are treated. Do not weaken dangling-link refusal merely to mint a manifest.

retro: nothing to bake; this is a brief/tree premise conflict, not a newly generalized implementation lesson.
