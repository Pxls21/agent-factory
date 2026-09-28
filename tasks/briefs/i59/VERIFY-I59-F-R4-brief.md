# VERIFY-I59-F round 4: attack the verify fold and task #344 before the re-mint (tasks #335 and #344)

Role: the VERIFY-I59-F verifier, resumed (sandbox adversarial-verifier, Opus 5.5). Do NOT spawn subagents. Report:
`tasks/briefs/i59/VERIFY-I59-F-R4-report.md`, written as you go; if the harness refuses a report-file write, return the
rest of the report as the text of your final message, in full; never work around the refusal.

Authored 2026-09-28 21:2xZ by the coordinator. PIN: origin d71197e.

The change under test: round 4 of I59-F, held as `tasks/briefs/i59/I59-F.patch` (rounds 1 to 4; sha256 in the premise).
Its contract: the `## ROUND 4` section of `tasks/briefs/i59/I59-F-brief.md` (the fold of your own round-1 findings, F-1 to
F-16, by the rulings there, plus task #344: the S0-01 manifest parse in linear time over the same bytes). The builder's
account: the `## Round 4 (the verify fold and task #344)` section of `tasks/briefs/i59/I59-F-report.md`; every claim in it
is a hypothesis, its mutation table and its discrepancies D-R4-1 to D-R4-8 included. Your round-1 report is
`tasks/briefs/i59/VERIFY-I59-F-report.md`.

Why it matters: after this verdict the coordinator re-mints S0-01 to S0-05 at once (S0-05 through a PC re-capture that
records the gid) and the owner signs once (D-104 (3)). A fix that is hollow, or a red that is not the one cause the builder
names, reaches a signed proof.

Your copy: apply the patch to a `git archive` of HEAD in your scratch (`/tmp/vi59f4/`), never in the main tree and never in
the lane's worktree `/home/user/i59-landing` (READ only; its files equal the patch's result, the premise shows).

## WHAT TO ATTACK (report every observation; no severity filter)

1. **Each finding of yours that round 4 claims closed.** Re-run your own round-1 reproduction against the round-4 bytes,
   through the real path: F-1 (is the known set the right vocabulary now, and does any pinned source name a Responses
   transport?), F-2, F-3 and F-8, F-4 and F-12 (the per-climb check up to the root: race windows between climbs, and the
   measured cost, 4.8 s against 2.4 s per row at 1,100 levels), F-6, F-7 (`--clear-groups`: what you can run here; the PC's
   setpriv is PC-only, say so), F-9 (and the builder's D-R4-2: a non-UTF-8 profile is now a read error), F-10, F-11 (the
   gid grading), F-13 and F-14.
2. **Task #344.** The digest identity on the 11 committed golden manifests, by your own oracle (both tools, old and new
   bytes); the 20-second bound; D-R4-5 (the comment kept on the same line so no line moved): does it hide anything?
3. **The reds the builder calls expected.** `tests/test_s0_05_egress.py`'s 8 failures: is each one F-11's single cause (read
   each failure's message)? The five attestation mismatches of `python3 scripts/validate-ledger integrity` on the patched
   copy, S0-02 included: is that the complete re-mint set, and does each proof's changed-input list match the builder's?
4. **What else changed.** Diff round 4 against round 3 (round 3's patch is `tasks/briefs/i59/I59-F.patch` at commit
   a1a639b): any behavior change outside the fold is a finding.
5. **Mutation.** Reproduce at least six of the builder's 30 rows as FAILED tests (one of X-R4-F4-chain, X-R4-F7-launch,
   X-R4-F11-gid0 and X-344-c-bytes among them); add a mutant for each fold clause no row covers, and name the survivors.
6. **The builder's two adjacent defects** (the S0-03 checker's credential walk on a non-string key; `netns_lib.sh:172`'s
   ranged class): confirm or refute them.

## GATE

Apply the blocking predicate of skill `contract-gate` and D-034 (only a CORE-BLOCKING finding re-opens the build; the rest
become follow-ups). One recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID, each
blocking finding with its reproduction command. Name separately anything that must hold before the re-mint and the PC
re-capture.

## BOUNDARY

READ everything. WRITE only your report and scratch under `/tmp/vi59f4/` (removed at the end). No git writes. Never apply
the patch in the main tree or the worktree.

## STANDING RULES

- No PC bridge (a PC-only item is written `NOT run here: PC only`), no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, GH_TOKEN, GITHUB_TOKEN.
- The S0-05 tests create network namespaces and iptables rules: after every run, `ip netns list` must print nothing and the
  iptables rule set must be what it was before you started (record both at the start). Kill by pid only.
- Other lanes are live (`.lanes-live`: SCRUB2-R1 round 3 and LS-B9 round 3 in the main tree); touch none of their files.
- A private `--basetemp` outside every work tree for every pytest run (`mkdir -p` its parent;
  `tests/test_proof_status.py` needs a short one); never run the whole `tests/test_vendored_manifest.py`. Counts pasted from
  `scripts/test_summary.sh` with their set ids; stamps from `date -u`. Long commands in one foreground call each, under
  10 minutes.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.

## PREMISE — MEASURED at authoring (2026-09-28 21:2xZ, the main tree at the pushed head; `bash scripts/premise_block.sh`)

```
$ git rev-parse --short HEAD
d71197e
$ sha256sum tasks/briefs/i59/I59-F.patch tasks/briefs/i59/I59-F-report.md | cut -c1-16,65-
5cf9db295c98fddc  tasks/briefs/i59/I59-F.patch
231bfe78ba5b31f9  tasks/briefs/i59/I59-F-report.md
$ git -C /home/user/i59-landing status --porcelain | wc -l
16
$ rm -rf /tmp/vi59f4-premise && mkdir -p /tmp/vi59f4-premise && git archive HEAD $(git -C /home/user/i59-landing status --porcelain | awk '$1=="M"{print $2}') | tar -x -C /tmp/vi59f4-premise
$ cd /tmp/vi59f4-premise && git init -q && git apply --whitespace=nowarn /home/user/agent-factory/tasks/briefs/i59/I59-F.patch && echo applied
applied
$ cd /tmp/vi59f4-premise && for f in $(git -C /home/user/i59-landing status --porcelain | awk '{print $2}' | grep -v 'I59-F-report.md'); do cmp -s "$f" "/home/user/i59-landing/$f" || echo "MISMATCH $f"; done; echo checked
checked
$ rm -rf /tmp/vi59f4-premise
$ python3 scripts/validate-ledger integrity 2>&1 | grep -c attestation-mismatch
0
[rc=1]
$ df -m / | tail -1
/dev/vda          258020 26126     11813  69% /
```

(`grep -c` exits 1 when it counts zero: the `[rc=1]` above is that, with the count 0 at the pushed head, before the patch.)
