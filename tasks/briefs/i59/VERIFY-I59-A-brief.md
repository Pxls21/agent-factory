# VERIFY-I59-A: attack the attested-inputs change against its contract (task #312, issue #59 F-1)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/i59/VERIFY-I59-A-report.md`
(write it incrementally from the start). PIN: origin 2a50a65. The change under test: `tasks/briefs/i59/I59-A.patch` (four
diffs; it applies to the PIN's files, and the coordinator checked that it reproduces the builder's four files byte for
byte). The frozen contract: `tasks/briefs/i59/I59-A-brief.md` (CONTRACT 1-5, EVIDENCE DEMANDS). The builder's report:
`tasks/briefs/i59/I59-A-report.md` (rounds 1 and 2; section 5 is the landing command list). Its claims are hypotheses.
Plan: `tasks/issue59-batch-plan.md`.

## WHY

`scripts/validate-ledger` is the proof pack's trust root: every proof's attestation includes it and the registry. This
change re-mints all twelve proofs, and the owner then re-signs all twelve. A wrong green here either lets a changed input
pass silently (the bug it fixes) or blocks a correct proof at the owner's re-sign. The coordinator checked only that the
patch reproduces the builder's bytes; nobody has attacked the logic. You are the independent pass (orchestration 0f).

## WHAT TO ATTACK (report every observation; no severity filter)

1. **The declaration check** (contract item 1): each refusal by its exact finding text; hostile spellings (`./x`, a trailing
   slash, a backslash, a doubled slash, a Unicode lookalike, a path through a symlinked directory, a path into another
   proof's directory, a directory, a special file); the registry's closed key set.
2. **The attestation** (item 2): a proof with no declaration gets exactly the PIN's key set and hashes; a declared file
   changed, deleted, or replaced by a symlink turns its proof INVALID with the exact finding; a result minted while a
   declared file was absent.
3. **The drift guard** (item 4): in a scratch copy, plant one undeclared read of each shape (a `spec_from_file_location`
   on a joined path, a `read_text` on a root-relative path, an import through a `sys.path` entry, an `open()` on a computed
   path, a read inside a helper module the checker imports): each must red. Measure the builder's named blind spots (S0-11's
   isolated children, non-Python children, a verdict from a stat or a directory listing): does any CURRENT proof's verdict
   depend on one?
4. **The declared set** (item 3): enumerate each checker's outside reads with an instrument of your own (for example
   `strace -f -e trace=openat` over each checker grading its committed evidence) and compare with the registry. Also S0-07's
   Fubuki checkout and the `__pycache__` exclusion.
5. **The landing** (report section 5), dry-run in your scratch worktree with the patch applied: re-mint all twelve with
   their recorded venues; `validate-ledger integrity`; `ledger-gen` twice, identical; `stage1-gate`; the tag steps in a
   tag-free clone, then `check-proof-status.py` exits 0 with twelve warnings. Reproduce the pins.py demonstration: one byte
   turns S0-02, S0-03 and S0-05 INVALID while S0-09 stays PRESENT, and on the PIN's code all three stay PRESENT. One byte of
   S0-08's `fixtures/malformed-marker/blocked.json` turns S0-08 INVALID.
6. **CI after the landing**: will each stage0-ci job pass (tests, ledger-integrity, harness-suites, planning, stage1-gate)?
   Name what runs where. The guard's CI skips (S0-07: no checkout; S0-11: no root): are they correct, and are they visible?
7. **Mutation**: reproduce at least five of the builder's mutants as FAILED tests, and add a mutant for each contract clause
   the builder's set does not cover.

## GATE

Apply the blocking predicate of skill `contract-gate`: contract-mapped, reproduced through the real code path, materially
effective, a concrete discriminator, in-boundary. A red test is necessary, not sufficient. Return one gate recommendation:
MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID, with each blocking finding's reproduction command.

## BOUNDARY

READ everything. WRITE only your report and scratch under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/verify-i59a/` (a scratch worktree of the PIN with
the patch applied goes there or, where a uid-65534 child must reach it, under `/tmp` as the builder did; remove it with
`git worktree remove --force` when done). Never apply the patch to the shared tree, never write a `proofs/*/result.json`,
`proofs/ledger.json`, a tag object or a tag ref in the shared tree, and never delete a tag in the shared repository (the
tag-free clone for the tag steps is a separate clone in your scratch).

## STANDING RULES

No git writes in the shared tree; no PC bridge; no outward-facing action. Never read a real secret source (`.pc-bridge.env`,
any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`, the GH_TOKEN and GITHUB_TOKEN variables). Other lanes hold this
tree: SYNTH1 (`scripts/s1_synth.py`, `tests/test_s1_synth.py`, `tasks/briefs/system1/SYNTH1-report.md`) and VERIFY-SCRUB2
(`tasks/briefs/system1/VERIFY-SCRUB2-report.md`): never touch their files. The disk is shared (about 1.7G free): scratch
under 400 MB, the worktree included, deleted as you go; a short `--basetemp`; never run the whole
`tests/test_vendored_manifest.py`. Test counts pasted from `scripts/test_summary.sh`; stamps substituted from `date -u`, never
typed. Long commands in one foreground call, each under 10 minutes; kill by pid only. When a hook injection stamped
`[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text of its own (under 200
characters; a note only for a 0).

## PREMISE — MEASURED at authoring (2026-09-26 06:0xZ, the sandbox tree)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-60
2a50a65 I59-A round 1 home (task #312; held for the issue #5
$ git diff --stat origin/claude/soundbox-kit-migration-iz1jwf HEAD -- scripts/ proofs/ tests/ | tail -1   (empty = HEAD's code equals the PIN's)
$ sha256sum tasks/briefs/i59/I59-A.patch | cut -c1-16; grep -c '^diff --git' tasks/briefs/i59/I59-A.patch
8e83b983e966ce2b
4
$ git apply --check -v tasks/briefs/i59/I59-A.patch
Checking patch proofs/registry.yaml...
Checking patch scripts/validate-ledger...
Checking patch tests/test_validate_ledger.py...
Checking patch tests/test_attested_inputs.py...
$ applied in a scratch copy of HEAD's three files: sha256 of the four results vs the lane's files (coordinator, before the patch commit)
validate-ledger 1fe875ebbcbdd2b9 = 1fe875ebbcbdd2b9; registry.yaml ad9a8d7721078062 = ad9a8d7721078062; test_validate_ledger.py dae0cd1c8a4c2798 = dae0cd1c8a4c2798; test_attested_inputs.py 2bce9a2e97c95764 = 2bce9a2e97c95764
$ grep -n '^## ' tasks/briefs/i59/I59-A-report.md | cut -c1-80
6:## 0. Premise check (evidence demand 1)
16:## 1. The enumeration (contract item 3; the drift guard's instrument, measure
60:## 2. The change (contract items 1, 2 and 3; landed in the tree 04:5xZ, uncom
92:## 3. The tests (evidence demand 2; written 05:0xZ)
148:## 4. Item 5: the landing proven in a scratch worktree (scratch file times 0
225:## 5. The landing command list (for the coordinator)
258:## 6. The gate in the tree (evidence demand 3)
301:## 7. NOT done
325:## 8. DISCREPANCIES (premise and brief vs measured)
342:## 9. Deviations from the brief (loud)
364:## 10. Adjacent defects and observations (reported, not fixed)
378:## 11. Self-attack: the three most likely ways this is wrong
395:## 12. Evidence tiers
404:## 13. Continuity
412:## 14. Status
417:## 15. Round 2: the S0-08 gap closed (2026-09-26 06:0xZ, the coordinator's r
$ df -h / | awk 'NR==2{print $4}'
1.7G
```
