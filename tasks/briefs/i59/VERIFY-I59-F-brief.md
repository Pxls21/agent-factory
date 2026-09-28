# VERIFY-I59-F: attack the proof-code follow-ups before the owner's re-sign (task #335, rounds 1 to 3)

Authored 2026-09-28 16:5xZ by the coordinator.

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/i59/VERIFY-I59-F-report.md`
(write it incrementally). If the harness refuses a report-file write, return the rest of the report as the text of your
final message; never work around the refusal.

The change under test: the I59-F lane's patch of record `tasks/briefs/i59/I59-F.patch` (sha256 in the premise), built in
three rounds by one sandbox lane and re-run by nobody else yet. Contract: `tasks/briefs/i59/I59-F-brief.md` (items 1-10,
and its ROUND 2, ROUND 3 and ROUND 3 ITEM 1 sections: A-1 to A-4, D-R2-2 by route B, D-R2-3). The builder's report: `tasks/briefs/i59/I59-F-report.md`. Its claims are
hypotheses. AF-AP-169, AF-AP-223, AF-AP-232, AF-AP-233 and AF-AP-234 in `docs/INCIDENT-LOG.md` give the classes.

Your copy: the disk is tight (about 1.48 GB free, three lanes sharing it), so never a full worktree. Make a partial copy
in a world-traversable path (S0-05's legs drop to a unit user, and the scratchpad is mode 0700):
`mkdir -p /tmp/vf-wt && git -C /home/user/agent-factory archive c9889ee proofs tests scripts harness-ports .github | tar -x -C /tmp/vf-wt`
(about 41 MB; add a path only when a test needs it, and say which), then `git init -q` there with one commit of the copy
(no hooks are configured in a fresh repository), then `git -C /tmp/vf-wt apply <the patch>`. Remove `/tmp/vf-wt` when
done. Never write the main tree or `/home/user/i59-landing`.

AUTHORIZATION: first-party, defensive work on the owner's own proofs: S0-05's runner creates network namespaces,
iptables rules, mounts and holder processes in this sandbox to prove egress containment (its tests already do); S0-03
and S0-04 are secret-leak hardening. Every test secret is a FAKE string built at run time.

## WHAT TO ATTACK (report every observation; no severity filter)

1. E-1 and A-2: every failure message of `proofs/S0-03/check_omniroute_roundtrip.py` and
   `proofs/S0-04/check_compression.py` that reads the profile or the config; any path that still prints a value or a
   long enough part of one (a custom YAML tag, an alias, a huge value, a non-string, a read error); is the shape itself
   a leak for a short or guessable value (the builder's self-attack 3).
2. B-1 and A-4: hostile evidence roots and pair identity paths with a newline anywhere (given, through a symbolic
   link, through `..`, trailing); is exit 73 the only way out, and is nothing written first?
3. B-2: the mount-id check: a bind mount of the same filesystem, a mount of another filesystem, a mount appearing
   during the walk; the fail-closed branches (no statx, no mount-id bit): can they be reached, and do they hand back
   nothing?
4. B-3: the iterative walk: 1,100 levels and more, hard links, FIFOs, sockets, devices, a directory moved during the
   walk, RLIMIT_NOFILE 1024; does the summary count every entry left; is the "way up is where it came from" check sound?
5. B-4 and A-1: every id form at every seam (SUDO_UID, SUDO_GID, S0_05_UNIT_USER): overflow, (uid_t)-1, zero, leading
   zeros, signs, empty parts, huge digit runs; is there ANY way the stand-in unit runs as uid 0 or gid 0; is the refusal
   before anything is written or launched?
6. The #331 shim and A-3: the signal tests under the `nohup bash -c '… & wait'` launch and under load; the five-signal
   deviation (D3, accepted); GW's child masks.
7. C-1, C-2, E-2, F2: the pinned lines, `stdout == ""`, `stderr == ""`, `-rfEs` and its pin.
8. Mutation: reproduce at least five of the builder's mutants as FAILED tests, including one each for A-1, A-2 and B-3;
   add a mutant for each contract clause the builder's set does not cover.
9. D-R2-2 by route B: S0-04 keeps its own copy of the two api_mode names, pinned by a test to S0-03's
   `PERMITTED_API_MODES`; D-R2-3: a default unit user resolved with gid 0 exits 64, and A7 records and compares the
   Gid line. Is the pin blind anywhere? Can a near name or a secret-shaped value print as a known mode?
10. Two questions, answered with evidence: (a) `proofs/S0-05/check_egress.py` grades the uid of a unit-identity
   record but not its gid (the lane's D-R3-4): is that a gap in the containment claim, and how would the committed
   evidence and fixtures be affected by grading it? (b) S0-04 records the api_mode and does not assert it (the lane's
   D-B-2, against D-021 in `docs/08_DECISION_LOG.md`): does that contradict a frozen criterion?
11. The ledger: `python3 scripts/validate-ledger integrity --root .` in your copy names exactly the attestation
   mismatches the patch causes (S0-03, S0-04, S0-05) and nothing else.

## GATE

Apply the blocking predicate of skill `contract-gate` (contract-mapped, reproduced through the real code path, materially
effective, a concrete discriminator, in-boundary) and D-034 (a finding re-opens the build only if it is CORE-BLOCKING;
the rest become follow-ups). Return one gate recommendation for the patch: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS /
NOT-READY / CONTRACT-INVALID, each blocking finding with its reproduction command.

## BOUNDARY

READ everything. WRITE only your report and scratch under `/tmp/vf-*` (removed at the end). No git writes except your own
worktree add, apply and remove. Never touch a tag or a ref.

## STANDING RULES

- No PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables.
- Every namespace, rule, mount and process you create is destroyed by name or pid; `ip netns list` is empty at the end
  and the iptables stable form equals its value before.
- Other lanes hold files in the main tree (`.lanes-live` lists them); never write there.
- The disk is shared (see the premise): your worktree is about 300 MB; scratch under 400 MB in all, the worktree
  included; a short `--basetemp`; never run the whole `tests/test_vendored_manifest.py`; `tests/test_lane_gate.py`
  refuses below 1,500 MB free (exit 66): leave it out.
- Test counts are pasted from `scripts/test_summary.sh`. Stamps are substituted from `date -u`, never typed.
- Long commands in one foreground call, each under 10 minutes; signal tests in the foreground (AF-AP-234); kill by pid.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.

## PREMISE — MEASURED at authoring (2026-09-28 16:5xZ, the main tree; `bash scripts/premise_block.sh`)

```
$ git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
c9889ee
$ git diff --stat c32ac3f c9889ee -- proofs/S0-03/check_omniroute_roundtrip.py tests/test_s0_03_omniroute.py proofs/S0-05/tools/pc/run_s0_05_units.sh tests/test_s0_05_egress.py tests/test_s0_04_compression.py .github/workflows/stage0-ci.yml tests/test_no_laya_in_gates.py proofs/S0-04/check_compression.py tests/test_gpu_window.py | tail -1
$ sha256sum tasks/briefs/i59/I59-F.patch | cut -c1-16
dc64a3f5853b48d8
$ grep -c '^diff --git' tasks/briefs/i59/I59-F.patch
9
$ git apply --check --stat tasks/briefs/i59/I59-F.patch | tail -1
 9 files changed, 1031 insertions(+), 65 deletions(-)
$ sha256sum tasks/briefs/i59/I59-F-brief.md tasks/briefs/i59/I59-F-report.md | cut -c1-16,65-
591b7f0bf2c727df  tasks/briefs/i59/I59-F-brief.md
a9f1c311a608af25  tasks/briefs/i59/I59-F-report.md
$ grep -n -E '^## (ROUND|Round)|^### Item 1, route B' tasks/briefs/i59/I59-F-brief.md tasks/briefs/i59/I59-F-report.md
tasks/briefs/i59/I59-F-brief.md:138:## ROUND 2 (the fold of A-1..A-4): the message sent to the resumed lane, 2026-09-28 14:5xZ, verbatim
tasks/briefs/i59/I59-F-brief.md:165:## ROUND 3 (D-R2-2 and D-R2-3): the message sent to the resumed lane, 2026-09-28 15:5xZ (15:51:20Z), verbatim
tasks/briefs/i59/I59-F-brief.md:186:## ROUND 3, ITEM 1: THE ROUTE RULING, 2026-09-28 16:4xZ (16:43:56Z), verbatim
tasks/briefs/i59/I59-F-report.md:364:## Round 2 (the fold of A-1..A-4)
tasks/briefs/i59/I59-F-report.md:620:## Round 3 (D-R2-2 and D-R2-3)
tasks/briefs/i59/I59-F-report.md:840:### Item 1, route B
$ df -m / | tail -1
/dev/vda          258020 36433      1506  97% /
```

The builder's final gates and hashes are in its report (each round's Gates and Final sha256 sections); your item 8 re-runs them.
The expected reds until the re-mint: `validate-ledger integrity` names S0-03, S0-04 and S0-05 attestation mismatches.
