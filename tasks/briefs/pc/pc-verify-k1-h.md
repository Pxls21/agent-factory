# VERIFY-K1-h — the targeted independent adversarial verify of K1-h: the vendored skill sets and the kit-root copies under `.claude/` as manifest rows (task #194)

PIN: the post-push SHA of local efb4518 ("K1-h landed (task #137; GATED-PENDING-VERIFY; …)"), named in the dispatch prompt; read it
with `git log --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf -8` and match the subject. Your worktree is at the PIN;
later heads may regenerate V and C for unrelated `.claude/` edits (task #150), which is not a finding against K1-h.
LANE: pc-verify-k1-h
ROLE: adversarial-verifier on the local route. The contract-gate predicate (D-031): a finding BLOCKS only if it is contract-mapped,
reproduced through the real tool (`python3 scripts/vendored_manifest.py --write|--check` on a scratch copy of the tree), materially
effective (a file is classed wrong, a drift goes undetected, a verification is skipped, or a stated claim is false as stated), with a
concrete discriminator, and inside the boundary (M, T, V, C below). Everything else is a follow-up. Emit ONE GATE RECOMMENDATION:
`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`; the coordinator owns the gate.

COMPONENT: `scripts/vendored_manifest.py` (M), `tests/test_vendored_manifest.py` (T), `sandbox-kit/VENDORED-MANIFEST.md` (V),
`sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv` (C). CONTRACT (frozen): `tasks/briefs/pc/pc-k1-h.md` (the K1-h brief) on top of the K1-g
contract (`tasks/briefs/pc/pc-k1-g.md`) and K1's (`tasks/briefs/pc/pc-k1-d.md`). The builder's report
`tasks/briefs/kit-k1-support/K1-h-report.md` and the lane record `tasks/briefs/pc/report-pc-k1-h.md--74aa8c5.md` are INPUTS to attack.
THE MERGE: the lane built on 74aa8c5, before D-054 moved `agents/code-implementer.md` to kit-adapted; the coordinator merged the
patch three-way (the landing commit's body says how: kit-verbatim 2957, kit-adapted 15, first-party 12). The merge is part of the
code under test.

## Items (report EVERY observation; no severity filter; SOLID/UNSURE per observation)

1. PREMISE. Re-measure the block below at the PIN (blob ids, `--check`, the class counts, the test count and set id). A mismatch that
   changes an item is CONTRACT-INVALID for that item; say which.
2. The copy rule (`M:541-558`: blob identity only, never by name; a blob under two declared roots is refused by name). In a scratch copy:
   (a) a `.claude/` file with the SAME NAME as a kit-root file but different bytes → first-party, not copy; (b) a byte-identical copy
   under a DIFFERENT name → copy; (c) an EMPTY file (or a file whose bytes match files under two kit roots) added under `.claude/` → the
   named `ambiguous` refusal: does that refusal stop `--check` and `--write` for the whole tree, and where would it fire (pre-commit,
   CI, a lane)? Is that the contract's intent, or a denial of service on an innocent file? (d) a kit-root file edited upstream so the
   `.claude/` copy no longer matches → the class flips to first-party: does `--check` name the drift?
3. The declared sets (`verify_declared_sets`, `M:457`, called at the top of `build_manifest_data`, `M:858`). For each of aegis, prism
   and typesafe: a member deleted from disk; an extra file placed in a set's directory but not in its PROVENANCE; a PROVENANCE entry
   naming a path outside `.claude/`; a symlink as a member; the PROVENANCE file's own pin or source line edited. For each: the exact
   refusal text and rc, or the silent outcome.
4. The 12 first-party files (the test's `K1H_FIRST_PARTY_REMAINDER`). For each, is it truly first-party: search every `sandbox-kit/`
   root for a byte-identical or near-identical source (a diff of a few lines is a kit-adapted copy the rule cannot see; report it as a
   finding with the diff size, never fix it).
5. The coordinator's merge. Confirm from the diff that no K1-h test was lost and that the counts 2957/15/12 are the regenerated values,
   not constants copied by hand: regenerate C and V in a scratch copy and compare. Re-run the lane's mutants m1, m2, m3 and m5 on the
   merged bytes (a spot check; say how each dies).
6. MUTANTS (new; never the lane's m1-m5): at least one each on the copy rule, the ambiguity refusal, `verify_declared_sets` and the
   class-file parse (`parse_classes`, `M:570`). Each mutant compiles and collects (AF-AP-78); before you count a kill, run the killing
   test on the UNMUTATED copy and paste that it passes (AF-AP-138). A survivor is a finding.
7. GATES, each with its output: `python -m pytest -n 8 tests/test_vendored_manifest.py -q -p no:cacheprovider` twice (xdist is
   installed on the PC; each call under the 420 s cap) with `bash scripts/pc_suite.sh set-id -- tests/test_vendored_manifest.py`
   (the landing: `51 passed`, set `21e700b8344c`); `python3 scripts/vendored_manifest.py --check` on your worktree; pyflakes on M and T.

## Boundary and standing do-nots

CREATE `tasks/briefs/kit-k1-support/VERIFY-K1-h-report.md` in your lane tree (write it incrementally from the start); nothing else.
Every scratch copy, mutant and fixture lives under `$HOME/tmp-vk1h/` (never the PC's tmpfs `/tmp` for trees or basetemps, AF-AP-112)
and is removed at the end. Never run `--write` in your lane tree (it rewrites V and C); only in a scratch copy. This is the owner's
PC: user scope only, no sudo; never stop, restart or edit OmniRoute, the vLLM `qwen` container, the Buzz relay, the `laya-systemone`
unit, Ollama, Phoenix, OpenObserve or neo4j; never touch another lane's tree; never print a `.env` file. No outward-facing action
(no push, PR, comment or issue).

CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
`scripts/lane_context.sh -q 'how does the vendored manifest class a .claude file as a kit copy or a declared set member and verify it' -s claude_records -s verify_declared_sets -s build_manifest_data -s parse_classes -o $HOME/tmp-vk1h/pack.md scripts/vendored_manifest.py tests/test_vendored_manifest.py`.

Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/kit-k1-support/VERIFY-K1-h-report.md --root .` (full
repo-relative paths, or `--map` flags pasted with it); apply its `fix:` hints for at most three rounds, then paste and finish. The
report ends with DISCREPANCIES and NOT-done.

## PREMISE — MEASURED at authoring (2026-09-23 14:2xZ, sandbox @ local 5312ffd; K1-h = local efb4518)
```
$ date -u +%Y-%m-%dT%H:%MZ; git rev-parse --short HEAD
2026-09-23T14:23Z
5312ffd
$ git log -1 --format="%h %s" efb4518 | cut -c1-100
efb4518 K1-h landed (task #137; GATED-PENDING-VERIFY; VERIFY-K1-h = task #194): the vendored skill s
$ blob[:12] lines path (at efb4518)
4a4ed0fece0b  1221 scripts/vendored_manifest.py
74b02f869df5  1246 tests/test_vendored_manifest.py
34b28324963f    37 sandbox-kit/VENDORED-MANIFEST.md
2310ac61fbd5  3102 sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv
b4944d735ba8     5 .claude/skills/PROVENANCE-AEGIS.md
2dd9eb5c2fbe    30 .claude/skills/PROVENANCE-PRISM.md
73df19c7f823    27 .claude/skills/PROVENANCE-TYPESAFE.md
$ python3 scripts/vendored_manifest.py --check
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
$ cut -f2 sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv | sort | uniq -c
     20 copy:sandbox-kit/council-of-high-intelligence/
     19 copy:sandbox-kit/honey-for-devs/
     13 copy:sandbox-kit/llm-wiki-compiler/
      4 copy:sandbox-kit/output-styles/
     12 first-party
     15 kit-adapted
   2957 kit-verbatim
     47 vendored:aegis
     12 vendored:prism
      2 vendored:typesafe
$ grep -n (seams)
13:refused by name) -> `copy:sandbox-kit/<name>/`; (d) everything else, including
420:    `sandbox-kit/<name>/` root (the `copy:` rule's source side; the root
457:def verify_declared_sets(root: Path) -> dict[str, int]:
487:def claude_records(
557:                        f"copy:{matched[0]}" if matched else "first-party"
583:            klass.startswith("copy:") or klass.startswith("vendored:")
855:def build_manifest_data(root: Path, repo_root: Path | None) -> ManifestData:
858:    set_pin_lines = verify_declared_sets(root)
914:                row_files = claude_by_class.get(f"copy:{item.path}", [])
$ grep -c "^def test_" tests/test_vendored_manifest.py
41
$ bash scripts/pc_suite.sh set-id -- tests/test_vendored_manifest.py
1 files set=21e700b8344c
```
