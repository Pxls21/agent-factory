# VERIFY-I59-F round 5: attack the four attested follow-ups before the re-mint (tasks #335 and #344)

Role: the VERIFY-I59-F verifier, resumed (sandbox adversarial-verifier, Opus 5.5). Do NOT spawn subagents. Report:
`tasks/briefs/i59/VERIFY-I59-F-R5-report.md`, written as you go; if the harness refuses a report-file write, return the
rest of the report as the text of your final message, in full; never work around the refusal.

Authored 2026-09-28 by the coordinator. A NARROW round: round 5 changed five files for four of your round-4 findings.

The change under test: round 5 of I59-F, held as `tasks/briefs/i59/I59-F.patch` (now rounds 1 to 5; sha256 in the
premise). Its contract: `tasks/briefs/i59/I59-F-R5-brief.md` (your R4-F1, R4-F3, R4-F4 and the R4-F5 test row, folded
before the re-mint because each changes an attested input, D-104 (3)). The builder's account: the `## Round 5 (the three
attested follow-ups and R4-F5)` section of `tasks/briefs/i59/I59-F-report.md`; every claim in it is a hypothesis, its
DISCREPANCIES D-R5-1 to D-R5-7 included. Your round-4 report: `tasks/briefs/i59/VERIFY-I59-F-R4-report.md`.

Why it matters: after this verdict the coordinator applies the patch, re-mints S0-01 to S0-04, re-captures S0-05 on the
PC with the round-5 runner, re-pins T's `LIVE_OUTPUT` (R4-F2) and re-mints S0-05; the owner then signs once. A hollow fix
here reaches a signed proof.

Your copy: apply the patch to a `git archive` of HEAD in your scratch (`/tmp/vi59f5/`), never in the main tree and never
in the lane's worktree `/home/user/i59-landing` (READ only; its files equal the patch's result, the premise shows).

## WHAT TO ATTACK (report every observation; no severity filter)

1. **Each finding round 5 claims closed**, through your own reproduction on the round-5 bytes:
   - R4-F1: a non-string key in the S0-03 checker fails by its type, with no traceback and no value printed. Try the
     shapes beyond the builder's four (a key inside a list item, a deeper mapping, a YAML merge key, a tuple-like key).
   - R4-F3: the handback's cost is linear. Re-measure the count and the clock at your own depths. D-R5-1's budget leaves
     a window (a move deeper than 32 levels is seen at most ceil(d / 32) climbs later): is it bounded as R's comment says,
     and can a mover use it to reach a file the walk then hands back?
   - R4-F4: CE grades the Groups line and bounds each id. The builder's NOT-done says a group above 4294967294 still
     passes: judge whether that matters before the re-mint.
   - R4-F5: the bind-mount row; your mutant V4-mount-by-st_dev-only now dies.
2. **What else changed.** Diff round 5's patch against round 4's (`tasks/briefs/i59/I59-F.patch` at the commit "I59-F
   round 4 home, held as a committed patch (rounds 1 to 4) ...", origin d71197e): any behavior change outside the four
   items is a finding.
3. **The expected reds.** T's 8 failures and TA's S0-05 row are F-11's single cause (read each message); `python3
   scripts/validate-ledger integrity` on the patched copy names exactly S0-01 to S0-05. Is the re-mint set still exactly
   those five?
4. **Mutation.** Reproduce at least four of the builder's 13 new rows as FAILED tests (X-R5-F3-never and
   X-R5-F4-bound-by-one among them); add a mutant for each round-5 clause no row covers, and name the survivors.
5. **Before the re-mint.** Update your round-4 list of what must hold before the re-mint and the PC re-capture.

## GATE

Apply the blocking predicate of skill `contract-gate` and D-034 (only a CORE-BLOCKING finding re-opens the build; the rest
become follow-ups). One recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID, each
blocking finding with its reproduction command. Name separately anything that must hold before the re-mint.

## BOUNDARY

READ everything. WRITE only your report and scratch under `/tmp/vi59f5/` (removed at the end). No git writes. Never apply
the patch in the main tree or the worktree.

## STANDING RULES

- No PC bridge (a PC-only item is written `NOT run here: PC only`), no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, GH_TOKEN, GITHUB_TOKEN.
- The S0-05 tests create network namespaces and iptables rules: after every run, `ip netns list` must print nothing and the
  iptables rule set must be what it was before you started (record both at the start). Kill by pid only.
- Other lanes are live (`.lanes-live` lists their files); touch none of them.
- A private `--basetemp` outside every work tree for every pytest run, passed as a pytest ARGUMENT, never through
  `PYTEST_ADDOPTS` (AF-AP-237); `tests/test_proof_status.py` needs a short one; never run the whole
  `tests/test_vendored_manifest.py`. Counts pasted from `scripts/test_summary.sh` with their set ids; stamps from
  `date -u`. Long commands in one foreground call each, under 10 minutes.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.
- Cite commits by subject or by an origin id; the coordinator's local ids change on the push.

## PREMISE — MEASURED at authoring (2026-09-28, main tree@0c11fd1)

Printed by `bash scripts/premise_block.sh` from the main tree at the PIN, origin 0c11fd1 (the pushed id). Expected to differ when you re-run it: nothing, unless HEAD moved (the first line checks the PIN is still an ancestor). The last command applies the held patch to HEAD's copies and compares each file with the lane's worktree: all 15 must read `same`.

```
$ git merge-base --is-ancestor 0c11fd1 HEAD && echo PIN-is-an-ancestor-of-HEAD
PIN-is-an-ancestor-of-HEAD
$ sha256sum tasks/briefs/i59/I59-F.patch tasks/briefs/i59/I59-F-report.md tasks/briefs/i59/I59-F-R5-brief.md tasks/briefs/i59/VERIFY-I59-F-R4-report.md | cut -c1-16,65-
7382fdbacb103793  tasks/briefs/i59/I59-F.patch
1f3880cfdaec6fff  tasks/briefs/i59/I59-F-report.md
dcebc0bc5878d21e  tasks/briefs/i59/I59-F-R5-brief.md
be65de75d9c49032  tasks/briefs/i59/VERIFY-I59-F-R4-report.md
$ git -C /home/user/i59-landing status --porcelain | wc -l
16
$ rm -rf /tmp/vi59f5-premise && mkdir -p /tmp/vi59f5-premise && git archive HEAD $(git -C /home/user/i59-landing status --porcelain | awk '$1=="M"{print $2}') | tar -x -C /tmp/vi59f5-premise && (cd /tmp/vi59f5-premise && git apply --whitespace=nowarn /home/user/agent-factory/tasks/briefs/i59/I59-F.patch) && for f in $(git -C /home/user/i59-landing status --porcelain | awk '{print $2}' | grep -v 'I59-F-report.md'); do cmp -s /tmp/vi59f5-premise/$f /home/user/i59-landing/$f && echo "same $f" || echo "DIFF $f"; done; rm -rf /tmp/vi59f5-premise
same .github/workflows/stage0-ci.yml
same proofs/S0-01/check_acp_conformance.py
same proofs/S0-01/tools/build_capture_record.py
same proofs/S0-03/check_omniroute_roundtrip.py
same proofs/S0-04/check_compression.py
same proofs/S0-05/check_egress.py
same proofs/S0-05/fixtures/evidence-synthetic-pass/hermes-acp/unit-identity.json
same proofs/S0-05/fixtures/evidence-synthetic-uid0/hermes-acp/unit-identity.json
same proofs/S0-05/tools/pc/run_s0_05_units.sh
same tests/test_gpu_window.py
same tests/test_no_laya_in_gates.py
same tests/test_s0_03_omniroute.py
same tests/test_s0_04_compression.py
same tests/test_s0_05_egress.py
same tests/test_s0_01_manifest_parse_linear.py
```
