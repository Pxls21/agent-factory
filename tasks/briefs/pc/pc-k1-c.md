# PC lane — K1-c (the vendored manifest, CONTINUED on a fresh PIN: the 2026-09-08 draft + AMENDMENT 1's symlink rule)

PIN: 236bec7

Role: code-implementer. Route: the LOCAL Qwen build route (`agentfactory-build-local`; the pc_lane.sh default — do NOT set
HERMES_MODEL). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Report: draft after EACH item at
`tasks/briefs/kit-k1-support/K1-report.md` (keep the existing blocker report as its "Blocker (resolved by AMENDMENT 1)"
section), return it whole as your final message. THREE sibling lanes share this host tonight (VERIFY-G2 and A5q own
`tests/test_s0_01_check_acp_conformance.py`; B6 owns `tests/test_s0_02_buzz_authz.py`) — never touch `proofs/`,
`tests/test_s0_*`, or their trees.

## CONTINUATION (read second)
Lane K1 (2026-09-08, PIN be5cf35) stopped correctly on a blocker: its symlink rule refused the six committed
`.claude/skills/*` links into `.agents/skills/*`. The coordinator resolved it as **AMENDMENT 1** —
`tasks/briefs/kit-k1-support/K1-AMENDMENT-1.md` — READ IT FIRST (a link is recorded by its target string and allowed when
its resolved target lies inside the REPOSITORY root; escaping or dangling links are refused by name). K1's draft is
ALREADY APPLIED on your worktree as the lane patch (`scripts/vendored_manifest.py` 559 lines, `tests/test_vendored_manifest.py`
320 lines — recovered from the PC lane tree; its `9 failed, 5 passed` were downstream of the one rule). Treat it as a DRAFT
written against a two-week-old tree: verify its premises against the PIN (the vendored roots, `SBOM.yaml`,
`upstream.lock.yaml`, the provenance tables — `sandbox-kit/VENDORED-FROM.md`, `sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md`
— all moved since be5cf35), finish items 1-7 of the original brief under the revised rule, write
`sandbox-kit/VENDORED-MANIFEST.md` for real, and run `--check` twice.

**The original brief governs**: `tasks/briefs/kit-k1-vendored-manifest-source-commit-license-per-tree.md` — READ IT WHOLE
(the seven pinned design items: the stdlib-only generator with `--write`/`--check`; per-root source, pin, license/SPDX,
file count, sorted tree sha256; the header with the generating commit; SBOM/lock agreement; the deterministic tests;
the named mutants; the report discipline).

## Venue notes for this build
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH (pyflakes from that venv); an absolute SHORT `--basetemp` under
  `../scratch/bt`; the tests run in seconds — paste them twice; two `--write` runs must produce BITWISE-identical
  manifests (item 7's gate: `sha256sum` of both).
- The vendored roots are read-only inputs; `SBOM.yaml` and `upstream.lock.yaml` are never edited (a disagreement is
  REPORTED as a finding, not fixed). No live service, no network.
- CODE INTEL FIRST: `graft skeleton` / `graft ask` before any whole-file read. `report_lint --min-refs 10`, at most
  THREE fix rounds, then paste and finish.

## Boundary
`scripts/vendored_manifest.py`, `tests/test_vendored_manifest.py`, `sandbox-kit/VENDORED-MANIFEST.md` (new), your report.
Nothing else changes. No git write, no commit, no push, no outward action.

## Report shape (DATA)
FILE IDENTITY of the FINAL bytes · the premise check against the PIN (which roots/pins moved since be5cf35) · per item the
command and the exact output · the mutant table (item 6) · the two `--check` lines and the two manifest shas · the two
pytest summaries · pyflakes · DISCREPANCIES · NOT-done · GATE RECOMMENDATION (a proposal; the coordinator grades).
