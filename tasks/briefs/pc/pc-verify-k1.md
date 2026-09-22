# PC lane — VERIFY-K1 (the independent, targeted adversarial verify of K1-d + the K1-e landing touch: the vendored-tree manifest, its generator and its drift gate)

PIN: cd976f5

Role: adversarial-verifier. Route: the LOCAL verify route (`agentfactory-verify-local`; on the vLLM route the effort is the server
default and cannot be set per lane; the route is HYBRID in practice — every "local" combo falls to its cloud step 2 on a
chat-template 400 — say both in the report header and make no claim about which model produced your verdict). Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first. Honey mode: full (line-bounded findings, evidence anchors, SOLID/UNSURE). Keep
your context small: bounded terminal output (`| tail -n 40`), one line per harness case, the report drafted after each item.

## WHAT YOU GRADE

Commit `cd976f5` (2026-09-22, "K1-d LANDED + the K1-e landing touch"): lane K1-d built, and the coordinator touched at landing,
the vendored-tree manifest the owner decided on 2026-09-08 (task #28 option a: "a generated source/commit/license manifest for the
vendored trees so reviewers skip them mechanically"). Three files are the boundary:

- M `scripts/vendored_manifest.py` — a stdlib-only generator: `VENDORED_ROOTS` (M:36-95, eight roots: `.claude/` and seven
  `sandbox-kit/*` trees, each with source, pin, pin source, provenance line), `walk_tree` (M:129-159; `os.walk` without following
  links; `.git`, `__pycache__`, `node_modules`, `*.pyc` excluded), `symlink_record` (M:177-204; a link digested by its TARGET STRING,
  allowed when its resolved target lies inside the repository root, refused by name when dangling or escaping), `license_for` +
  `detect_spdx` (M:215-255; top-level `license|copying|notice*` files; MIT / Apache-2.0 / AGPL-3.0 / CC0-1.0 / unknown),
  `parse_provenance` + `validate_declared_roots` (M:264-362; the roots table must agree with `sandbox-kit/VENDORED-FROM.md`),
  `validate_pin_agreement` (M:423-450; lock ∩ SBOM pins must agree; a root whose source is in the lock must carry the lock's pin),
  `render` (M:506-554), `normalize_generated_time` (M:555-571; the K1-e touch: the timestamp AND the generating-commit line are
  blanked before the drift comparison), `main` (M:585-637; `--write` / `--check`, the `--check` retry when HEAD moves mid-run).
- T `tests/test_vendored_manifest.py` — 22 tests: fixtures copy only the generator's declared inputs into a temp git toplevel
  (`copy_fixture`, T:27-66), `run_tool` (T:70), the named-mutant wrapper (`MUTANTS`, T:458-494: unsorted digest, empty exclusions,
  agreement removed, symlink refusal removed) and `test_committed_manifest_passes_check_at_a_later_head` (T:180-207, the K1-e
  boundary lock: HEAD moved → PASS; one changed vendored byte at the moved HEAD → drift on its ROW, never on the header line).
- V `sandbox-kit/VENDORED-MANIFEST.md` — 22 lines, regenerated at d5de7fb; `--check` PASSES on the committed tree at cd976f5.

## PREMISE — MEASURED at authoring (2026-09-22 09:4xZ, the sandbox clone at 1a68cbf, the three files byte-identical to cd976f5; re-measure as item 1)

```
sha256 (first 16) / lines: M 6528c8da30e38e55 / 637 · T e29b4a4fec3ae7ec / 568 · V ff472fc4d937a81d / 22
python3 scripts/vendored_manifest.py --root . --check   → PASS: sandbox-kit/VENDORED-MANIFEST.md matches 8 vendored roots (rc 0)
   (on the committed tree whose HEAD is NOT the manifest's "Generated from commit" line — the K1-e boundary; before the touch this read
    "vendored manifest drift: line 4: committed='Generated from commit: `4d45f19…`' …" rc 1 on every commit after the generating one)
bash scripts/test_summary.sh tests/test_vendored_manifest.py → 22 passed in 19.95s / 22 passed in 21.30s  (set 21e700b8344c)
red-first of the K1-e lock over the lane's original normalizer: 1 failed, 21 deselected — "vendored manifest drift: line 4 … Generated from commit"
pyflakes M T: 0. AP screen: AF-AP-70 at T:214 (a test-side is_file), AP-1 at M:494 (`os.environ.get("SOURCE_DATE_EPOCH")`)
wiring: `grep -rl vendored_manifest scripts/hooks harness-ports .github .claude/hooks` → nothing: --check is NOT on any gate path
sandbox-kit/ top-level dirs: aleph codebase-memory-mcp council-of-high-intelligence docs honey-for-devs llm-wiki-compiler output-styles
   reference-scripts — `docs/` is NOT a declared root (undeclared trees are neither digested nor refused)
.claude/ top-level: agents commands hooks output-styles settings.json skills workflows — the `.claude/` row claims source
   `pxls21/sandbox-kit:dot-claude/` @ aeb3082 for the WHOLE tree, yet .claude/ carries first-party content (git log --diff-filter=A:
   hooks 1 adding commit, skills 4, agents 3, output-styles 1; e.g. .claude/skills/orchestration/SKILL.md edited 953ccfe 2026-09-22)
pin agreement on the real tree: lock entries 24, SBOM entries 22, lock ∩ SBOM = 22 (loop 1 LIVE); roots whose source is in the lock: []
   (loop 2 VACUOUS for every manifest row — the lane's own NOT-done: "the eight manifest sources have no shared source entry with
   SBOM.yaml/upstream.lock.yaml at this PIN")
```

Lane-reported (K1-d, `tasks/briefs/kit-k1-support/K1-report.md`): PC `22 passed in 4.64s` / `4.22s`, lane_gate RESULT ×2 identical at
4d45f19, two writes byte-identical under SOURCE_DATE_EPOCH, `check_rcs=0,0`, pyflakes 0; the four named mutants killed.

**The owner's audit bar for K1 (2026-09-22): "Do not claim the vendored manifest complete until it binds path, type, target
existence, source, commit/version, license and tree digest, and its verifier kills omissions and path/type substitutions."** Grade
against that bar explicitly (item 7).

## ITEMS (discovery exhaustive; disposition disciplined — the blocking predicate: contract-mapped · reproduced through the real
generator/checker · materially effective · a concrete discriminator · in-boundary)

1. **PREMISE first (stop on failure):** re-run the identity, `--check`, and the two pytest lines above on your worktree with
   `--basetemp` under your lane scratch (never `/tmp`); a different identity → CONTRACT-INVALID, stop.
2. **Coverage — what the manifest does NOT see.** (a) Create `sandbox-kit/newtool/` with one file in a scratch copy of the declared
   inputs (T's `copy_fixture` shape): `--check` still PASSES? Then an undeclared vendored tree is invisible to the gate — classify
   (a reviewer "skips vendored trees mechanically" only if every vendored tree is in the table). (b) `sandbox-kit/docs/` today: is it
   vendored, first-party, or mixed? (c) `.claude/`: list the top-level entries that are NOT from the kit snapshot (by git history) and
   say whether the row's source/pin claim is TRUE for the tree it digests; the owner's ask was "the vendored PARTS of .claude/". A
   false provenance claim in a committed manifest is a hollow green in prose (CLAUDE.md #1 rule) — decide whether it blocks.
3. **Symlinks (M:177-204).** Hostile shapes: a link chain ending outside the repo; a link to a DIRECTORY outside; a relative `..`
   link that resolves inside; a link whose target string changes while resolving to the same file (digest must change — by design);
   a link inside `.claude/skills/` to `.agents/skills/…` (the AMENDMENT-2 cross-root case); a link named `LICENSE` (which bytes does
   `license_for` digest?). Paste rc + the first stderr line per shape.
4. **Special files and names (M:129-159).** A FIFO, a socket and a device node inside a root: skipped silently (neither counted nor
   refused) — measure and classify; an unreadable regular file (chmod 000, as the lane user) → which error, rc; a non-UTF-8 filename
   (surrogate) → which error; an empty directory; a nested `.git` directory inside a root (excluded — say whether that hides a
   vendored submodule's identity).
5. **License detection (M:215-255).** A REUSE-style `LICENSES/` directory (not matched — `none found`?); a root with LICENSE
   (unknown) + COPYING (MIT) — which file and identifier are reported; a NOTICE-only tree; an SPDX tag inside a longer license text;
   a BOM-prefixed license file. Are the four SPDX ids and `unknown` the whole domain the manifest can print?
6. **Agreement and provenance (M:264-362, :423-450).** Confirm loop 2 is vacuous on the real tree (paste the empty intersection) and
   say what the manifest's "SBOM/lock agreement" claim is worth today; a root added to `VENDORED-FROM.md` but not to
   `VENDORED_ROOTS` (and the reverse) → the named refusal; a provenance line off by one → `declared provenance lines drifted`.
7. **The audit's completion bar.** For each binding — path, type (file/symlink/dir), target existence, source, commit/version,
   license, tree digest — say WHERE the manifest binds it (file:line) or that it does not. Then the mutants the bar names: OMISSION
   (a root's row deleted from V; a file deleted from a root; a root deleted from `VENDORED_ROOTS`) and PATH/TYPE SUBSTITUTION (a
   regular file replaced by a symlink to identical bytes; a directory replaced by a symlink to it; a row's path renamed) — each
   through the REAL `--check`, rc + first line pasted. A substitution the gate cannot see is a finding.
8. **The K1-e touch.** The generating-commit line is now informational: a manifest with a FORGED commit line and correct rows
   passes — acceptable? Weigh the alternative the coordinator rejected as too large: record `git log -1 --format=%H -- <the eight
   roots>` (the roots' last-change commit) — stable across unrelated commits, still a drift signal for the roots' history. One
   paragraph, a recommendation, no code.
9. **The `--check` retry loop (M:598-627).** `start_revision != end_revision` retries once — with the commit line ignored, is the
   guard still load-bearing? Mutant: delete it — which test notices? Also `--write` is not atomic (`write_text`): a failed write
   leaves a truncated manifest → `--check` then fails closed (measure with a read-only target path).
10. **Mutants (≥ 10, none overlapping the lane's four; AF-AP-78 — each compiles and collects; a scratch copy of M under your lane
    scratch, the worktree file's sha pasted before and after).** Suggested: `resolved.exists()` dropped (dangling accepted); `followlinks=True`;
    the file digest replaced by the path only; `EXCLUDED_DIRS` gaining `tests`; `license_for` returning the first candidate without
    detection; `--check` comparing row COUNT only; the final sort dropped; `validate_declared_roots` call dropped; `render` dropping
    the `.claude/` row; the normalizer blanking EVERY line starting with `Generated` (over-broad — does the boundary test still
    discriminate rows?); `SOURCE_DATE_EPOCH` ignored. Row: mutant · compiles · killed-by <test> / SURVIVED / EQUIVALENT (with why).
11. **Gates:** `bash scripts/test_summary.sh tests/test_vendored_manifest.py` ×2 (identical), `--check` on the worktree, pyflakes,
    `python3 scripts/ap_screen.py scripts/vendored_manifest.py tests/test_vendored_manifest.py`, every count pasted beside `date -u`.
12. **The lane's report** (`tasks/briefs/kit-k1-support/K1-report.md`): lint with
    `python3 scripts/report_lint.py tasks/briefs/kit-k1-support/K1-report.md --rev cd976f5 --map M=scripts/vendored_manifest.py
    --map T=tests/test_vendored_manifest.py`; any §DONE-TABLE claim the tree does not support is a finding.
13. **Out of scope, note only:** wiring `--check` into a hook / run-all (K1-f after this verify); the seven `sandbox-kit/*` roots'
    upstream pins beyond what the table declares; the owner's `.claude/` scoping decision if item 2(c) needs one.

## DELIVERABLE

`tasks/briefs/kit-k1-support/VERIFY-K1-report.md`, drafted after each item: header (PIN, the route note, gpg-free — this lane needs no
keys), item 1 pastes, per item reproduced / reviewed / skipped with pasted rc and first lines, findings F1… with the predicate, the
MUTATION TABLE, GATES, FOLLOW-UPS (one line each, for the coordinator to file under D-034), NOT-done, and ONE closing line
`GATE RECOMMENDATION: MERGE-READY | MERGE-READY-WITH-FOLLOWUPS | NOT-READY | CONTRACT-INVALID`. Lint the report with
`python3 scripts/report_lint.py <report> --rev cd976f5 --map M=… --map T=…` (at most three fix rounds, AF-AP-76). Commit nothing, push
nothing, post nothing. Scratch under your lane directory, never `/tmp` (AF-AP-112), never a whole-tree copy — copy the generator's
declared inputs the way `copy_fixture` does.

**Authorization:** the manifest and its tests are this project's own tooling on the owner's own host; nothing leaves the host; no
server is touched.
