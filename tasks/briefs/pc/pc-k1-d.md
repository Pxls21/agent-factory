# PC lane — K1-d (the vendored manifest, CONTINUED a second time: the 2026-09-08 draft + AMENDMENT 1's symlink rule + AMENDMENT 2's inventory)

PIN: 4d45f19

Role: code-implementer. Route: the LOCAL Qwen build route (`agentfactory-build-local`; the pc_lane.sh default — do NOT set
HERMES_MODEL). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Report: draft after EACH item at
`tasks/briefs/kit-k1-support/K1-report.md` (keep the two existing blocker reports as its "Blocker (resolved by AMENDMENT 1)"
and "Blocker (resolved by AMENDMENT 2)" sections), return it whole as your final message. THREE sibling lanes share this host
(VERIFY-A5q, VERIFY-S4H, B7) — never touch `proofs/`, `tests/test_s0_*`, or their trees.

## CONTINUATION (read second)
Lane K1 (2026-09-08, PIN be5cf35) stopped on its symlink rule; AMENDMENT 1 (`tasks/briefs/kit-k1-support/K1-AMENDMENT-1.md`)
moved the boundary to the repository root. Lane K1-c (2026-09-22, PIN 236bec7) then stopped CONTRACT-INVALID, correctly: the
six `.claude/skills/*` links AMENDMENT 1 said "pass" dangled at that PIN. The coordinator removed them from the tree (a
repository defect, not a generator defect) and wrote **AMENDMENT 2** — `tasks/briefs/kit-k1-support/K1-AMENDMENT-2.md` — READ
IT FIRST: the committed symlink inventory at THIS PIN is exactly one resolving link
(`sandbox-kit/codebase-memory-mcp/Formula -> pkg/homebrew/Formula`), enumerated and pasted there; the revised test list (a)-(e);
the draft's pyflakes hit to fix. K1's draft is ALREADY APPLIED on your worktree as the lane patch
(`scripts/vendored_manifest.py` 559 lines, `tests/test_vendored_manifest.py` 320 lines — the 2026-09-08 bytes; its
`9 failed, 5 passed` were downstream of the old vendored-root rule). Treat it as a DRAFT written against a three-week-old
tree: verify its premises against the PIN (the vendored roots, `SBOM.yaml`, `upstream.lock.yaml`, the provenance tables —
`sandbox-kit/VENDORED-FROM.md`, `sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md`), finish items 1-7 of the original brief under
AMENDMENT 1's rule and AMENDMENT 2's tests, write `sandbox-kit/VENDORED-MANIFEST.md` for real, and run `--check` twice.

**The original brief governs**: `tasks/briefs/kit-k1-vendored-manifest-source-commit-license-per-tree.md` — READ IT WHOLE
(the seven pinned design items: the stdlib-only generator with `--write`/`--check`; per-root source, pin, license/SPDX,
file count, sorted tree sha256; the header with the generating commit; SBOM/lock agreement; the deterministic tests;
the named mutants; the report discipline).

## Premise check (item 0, before any edit — STOP and report on a conflict)
- `git ls-files -s | awk '$1=="120000"{print $4}'` on your worktree, each entry with `readlink` and `test -e`: exactly the one
  entry AMENDMENT 2 pastes. Paste yours.
- `python3 -m pyflakes scripts/vendored_manifest.py tests/test_vendored_manifest.py` at the start: the one known hit
  (`'dataclasses' imported but unused`) and nothing else. Paste.
- The real-tree run of the DRAFT generator BEFORE your edits (`python3 scripts/vendored_manifest.py --root . --write` into a
  scratch output path if the draft supports one, else `--check`): paste its first refusal or its output — this is the red-first
  line for the boundary rule (the draft still enforces the old vendored-root rule).

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
