# VERIFY-I59-LANDING: attack the issue #59 batch landing before the owner re-signs twelve proofs (task #315)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/i59/VERIFY-I59-LANDING-report.md`
(write it incrementally). If the harness refuses a report-file write ("Subagents should return findings as text"), return the
rest of the report as the text of your final message; never work around the refusal.

PIN: the landing commit on the local branch `i59-landing` (subject "The issue #59 batch landed (task #315): ..."; its parent
is origin eb48880; the premise gives its local id). Cite it as "the landing commit", never by its local id: the push rewrites
that id. The coordinator's worktree of it is `/home/user/i59-landing`: never write there. Make your own:
`git worktree add --detach /tmp/vland-wt <landing id>` (world-traversable: S0-11's uid 65534 child reads its fixtures), and
remove it with `git worktree remove --force` when done.

## WHY

This commit re-mints all twelve Stage 0 proofs and turns their twelve owner anchors to PENDING; after it lands the owner
re-signs all twelve in one command (D-069's form). A wrong green here costs the owner a second re-sign, or lets a changed
input pass silently. The coordinator ran the procedure and its gates; nobody has attacked the result (orchestration 0f).
Sources: the plan `tasks/issue59-batch-plan.md`; the procedure, `tasks/briefs/i59/I59-A-report.md` section 5; the I59-A
verifier's rounds 1-2, `tasks/briefs/i59/VERIFY-I59-A-report.md` (its section 13 is round 2).

## WHAT TO ATTACK (report every observation; no severity filter)

1. **The landing is exactly its parts.** Rebuild it from origin eb48880 plus the four held patches
   (`tasks/briefs/i59/I59-{A,B,C,E}.patch`), FU-4 (`-rs` on CI's pytest line and the test that pins it) and the one
   env-tool-quirks line (plus its lane copy and the manifest), and diff the trees. The remaining difference must be only the
   re-mint outputs (`proofs/*/result.json`, `proofs/ledger.json`) and the anchor step (the twelve tag files removed, twelve
   PENDING lines, `EXPECTED_PENDING`). Anything else is a finding.
2. **The re-mint.** For each of the twelve: the attestation map equals, computed by your own instrument, the closure plus the
   schemas plus the proof directory's files (minus its own result.json and blocked.json and `__pycache__`) plus its declared
   `extra_attested_inputs`; the venue label equals the previous result's; every field that changed against the parent commit,
   listed and explained. Negative controls in a scratch copy: one byte of a declared outside input (`proofs/S0-01/pins.py`,
   `upstream.lock.yaml`, `LICENSE-DECISION.md`, an S0-01 file S0-02 loads) turns exactly the right proofs INVALID.
3. **The anchors.** `scripts/check-proof-status.py` rc 0 with twelve WARNING lines and nothing else; the re-sign procedure in
   `docs/governance/README.md` works on this state: in a scratch clone, with a THROWAWAY key standing in for the owner's
   (a scratch `owner-signing-key.asc`), sign one tag on a commit holding the re-minted result, import it the committed way,
   remove that PENDING line and its `EXPECTED_PENDING` entry: that proof must read verified and the rest stay WARNING. The
   owner's real key is never needed and never touched.
4. **CI on the landing.** Run the suite as uid 65534 with CI's environment (`S0_01_VENUE=ci`; the dependencies CI installs),
   as VERIFY-I59-A did, and predict each stage0-ci job (tests, ledger-integrity, harness-suites, planning, stage1-gate).
   With FU-4's `-rs`, list every skip and say whether each is correct and visible.
5. **I59-A round 4's delta** (FU-7: the attestation description in `proofs/schemas/result.schema.json`; FU-8: the
   `os.access` and `os.path.lexists` shapes and the multibyte long segment in `tests/test_attested_inputs.py`; I-14: the
   docstring's blind spots). VERIFY-I59-A saw rounds 1-3 only: attack round 4 as you would a new change, and check the
   builder's re-listing of mutants V-S4 and V-L4 (its report, section 17).
6. **The env-tool-quirks line** ("Outside reads are attested inputs too"): is every claim in it true of the code?

## GATE

Apply the blocking predicate of skill `contract-gate`. Return one recommendation for the landing: MERGE-READY /
MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID, each blocking finding with its reproduction command.

## BOUNDARY

READ everything. WRITE only your report and scratch under `/tmp/vland-*` (removed at the end). Never write the coordinator's
landing worktree, the shared tree's tracked files, a tag or a ref of the shared repository (the tag experiments of item 3
run in a separate scratch CLONE with its own refs). No git writes in the shared repository except your own worktree add and
remove.

## STANDING RULES

- No PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables. Never use the owner's signing
  key or any real GPG key; the scratch key is generated in your scratch and deleted with it.
- Another lane may hold the shared tree (SCRUB2-R1: the scrubber files); `.lanes-live` lists them. VERIFY-I59-BCE runs beside
  you on the same commit: never touch `/tmp/vbce-*`.
- The disk is shared (about 1.4 GB free, two verifiers beside each other): a worktree of this repo is about 300 MB. Never
  commit in the shared repository's worktrees: the post-commit hook would build about 740 MB of code-intel indexes there
  (measured on the landing worktree). The tag experiment's clone shares objects (`git clone --shared`) and checks out only
  what it needs. Scratch under 450 MB, clones and worktrees included, deleted as you go; a short `--basetemp`; never run
  the whole `tests/test_vendored_manifest.py`.
- Test counts are pasted from `scripts/test_summary.sh`. Stamps are substituted from `date -u`, never typed.
- Long commands in one foreground call, each under 10 minutes; kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text of
  its own (under 200 characters; a note only for a 0).
