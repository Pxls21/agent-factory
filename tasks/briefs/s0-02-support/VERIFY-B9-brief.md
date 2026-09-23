# VERIFY-B9 — the independent targeted adversarial verify of B9: S0-02's replay leg as a per-delivery DELTA (issue #17, D-036; task #146)

PIN: bee499f (origin head at authoring; every S0-02 file is byte-identical to the B9 landing 221e68b, measured below).
LANE: verify-b9 (sandbox; agent `adversarial-verifier`, in the SHARED tree, no worktree isolation). Honey `full`: line-bounded
findings, evidence anchors, SOLID/UNSURE. Do NOT spawn subagents. Venue note: the S0-02 test file passes whole in this sandbox
today (`175 passed`, measured below), so this verify runs here while the PC's local slots are full.

WHAT LANDED (GATED-PENDING-VERIFY, rule 0f): B9 (`221e68b`, harvested from the PC build lane `pc-b9.md--71463f3`). Its report
`tasks/briefs/s0-02-support/B9-report.md` is the CLAIM under test, never the oracle. The frozen contract is the B9 brief
`tasks/briefs/pc/pc-b9.md` (§THE CONTRACT: issue #17's seven steps verbatim, D-036's oracle, the two mismatches M-A and M-B) —
read it whole first. D-036's oracle, verbatim: "identical event id · the `duplicate:` receipt bound to the second delivery · ONE
continuous buzz-acp process · ONE prompt in total · ZERO prompts in the second delta · the synthetic Buzz-ACP replay guard kept as
defense-in-depth".

Files (READ-ONLY for you; write ONLY the report): R `proofs/S0-02/tools/pc/run_s0_02_legs.sh` · C `proofs/S0-02/check_buzz_authz.py`
· T2 `tests/test_s0_02_buzz_authz.py` · D `proofs/S0-02/tools/pc/deliver_event.py` · PP `proofs/S0-01/tools/pc/pc_post.sh` (the
masked-log producer, :107) · the committed bundles under `proofs/S0-02/fixtures/`. Report: `tasks/briefs/s0-02-support/VERIFY-B9-report.md`
(write it incrementally from the start).

BOUNDARY: your only write is the report. Mutants in scratch copies only (never a git restore in this shared tree); each mutant
compiles (`bash -n` / `py_compile`) and collects (AF-AP-78); before you count a kill, run the killing test on the UNMUTATED tree and
paste that it passes (AF-AP-138). The sandbox has about 1.9 GB free: every pytest `--basetemp` lives under `/tmp/vb9/` and is removed
after each run; never keep scratch repositories. Two other sandbox agents run in this tree on disjoint files (`proofs/S0-05/`,
`tests/test_s0_05_egress.py`, `tasks/briefs/s0-05-support/`, `tasks/briefs/ci/`): never touch, run or revert them. Never run
`git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push`. No outward-facing action; no PC or bridge use;
no live capture, real launcher, relay, harness server or host secret file (every test uses the labelled doubles and a closed
loopback relay URL).

CODE INTEL FIRST: `graft ask` before any grep for code questions; `scripts/lane_context.sh -q 'how does the neg-replayed leg cut
and grade its two timelines' -s snapshot_timeline -s delta_timeline -s _check_replay -s collect_masked -o /tmp/vb9/pack.md
proofs/S0-02/tools/pc/run_s0_02_legs.sh proofs/S0-02/check_buzz_authz.py`.

## Items (attack the whole contract with NEW shapes, never the builder's cases; report EVERY observation, no severity filter)

1. **PREMISE:** re-run the premise commands below on the PIN and paste them under `## PREMISE — RE-MEASURED`; stop CONTRACT-INVALID
   on a mismatch that changes this brief.
2. **D-036 clause by clause.** For each of the oracle's five clauses (and the synthetic replay guard), name the checker line that
   enforces it and a test that goes red when that enforcement is removed (run it). Hypothesis H1, to reproduce or refute: "ONE
   continuous buzz-acp process" has NO check — C holds zero occurrences of `initialize`, `continuous` or `seq`, and the committed
   PASS fixture's second sub-leg restarts at seq 1 with a fresh `initialize` (a second process) and passes. Build a replay bundle
   whose two sub-legs come from two processes and run the REAL checker on it. If it passes, state the finding with the clause it
   maps to; do not decide core-blocking (the coordinator does, D-034).
3. **Hypothesis H2 — the boundary's position.** Issue #17 step 2 says the boundary is recorded "after the first terminal
   observation". The runner snapshots right after `wait_turn_window 1` (R:227-231), which returns on the first `session/prompt`
   REQUEST line (R:85-86), before the turn's result. With a nonzero `S0_02_TURN_WAIT_S` and a fake whose first turn emits its
   `session/update` and result lines some seconds after the prompt line: where do those lines land (first, or the second delta)? Does
   the checker's grade of the replay leg change? State what the landed code does against the issue's wording.
4. **m7's "equivalence".** The report declares m7 (the second `wait_turn_window 0` removed) EQUIVALENT "under this zero-latency fake +
   `S0_02_TURN_WAIT_S=0`" — a configuration in which the window is zero anyway (T2:2192, :2559, :2969 set it to 0). With a nonzero
   window and a fake that emits a SECOND prompt late (the relay did NOT drop the duplicate), does the landed runner put that prompt in
   the delta (the checker then refuses) while m7 reads the delta too early (zero prompts, a hollow green)? If no committed test
   separates them, that is a finding.
5. **The snapshot/delta domain** (R:111-135): at snapshot time the live timeline absent, empty, or with no newline at all (what is
   `first_bytes`, and what does `delta_timeline` then do: exit code, text, and whether `second/timeline.jsonl` exists — is the failure
   named, or does it read as "prefix mismatch"?); a final timeline shorter than the snapshot; the same length with bytes rewritten; the
   file replaced by a new inode that repeats the prefix; CRLF; one very long line. Note `snapshot_timeline` ends with `printf`, so its
   exit status inside `first_bytes=$(…)` is printf's (R:121) — measure what `set -euo pipefail` (R:18) does and does not catch.
6. **The collection** (R:297-308): the one masked log copied into both sub-legs (byte-identical?); the 64-hex refusal firing on the
   SECOND copy after the first succeeded (the partial leg directory left behind, and the checker's verdict on it, by name); the
   closure the checker demands (C:143-149, C:561-574) against what the runner leaves on every failure path.
7. **The integration test** (T2:2657 and its siblings): the issue requires "the exact replay portion of `run_s0_02_legs.sh` (the
   sourced functions, a stub launcher for the ACP process is acceptable ONLY for the process, never for the timeline shape) … then
   the exact checker on its output. A hand-built synthetic second-delivery bundle is not sufficient." State which R functions the
   test sources, what it stubs, and whether any part of the second-delivery bundle is hand-built.
8. **Mutants.** Re-run the report's m1-m7 against the WHOLE T2 file, pasting counts and the ACTUAL killing test(s). Add at least six
   of your own: `first_bytes` empty at the call site; `cmp -n` → `cmp` (no byte count); `head -c` → `head -n`; the snapshot moved
   after the second delivery; `collect_masked "$out/second"` dropped; the second `wait_turn_window 0` → `wait_turn_window 1`. One row
   each: mutant · compiles · collected · killed-by (test id) / SURVIVED / EQUIVALENT with the reason, measured in a configuration where
   the mutated feature is live.
9. **Gates** (paste every line): T2 twice (`mkdir -p /tmp/vb9/bt && bash scripts/test_summary.sh tests/test_s0_02_buzz_authz.py
   --basetemp /tmp/vb9/bt`, then `rm -rf /tmp/vb9/bt`), counts agreeing, the set id `a5de0beef100` beside each; `bash -n R`;
   `/root/venv-agent-factory/bin/python -m pyflakes T2`; `python3 scripts/ap_screen.py R` and `python3 scripts/ap_screen.py --tests T2`.
10. Anything else you find.

## Verdict

Apply the blocking predicate (contract-mapped · canonically reproduced through the real code path · materially effective · a concrete
discriminator · in-boundary of what B9 landed) and return a GATE RECOMMENDATION: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY
/ CONTRACT-INVALID. A finding in the checker (read-only for B9) is still reported, with its clause; the coordinator decides its route.

## Report (`tasks/briefs/s0-02-support/VERIFY-B9-report.md`)

PREMISE — RE-MEASURED · each item with its evidence (commands and output pasted, file:line refs) · the MUTATION TABLE (theirs re-run
+ yours) · FINDINGS (every observation: SOLID/UNSURE, primary source, class BLOCKER / FOLLOW-UP / INFO / UNVERIFIED with the predicate
applied) · GATES · FOLLOW-UPS FOR D-034 · NOT-DONE · GATE RECOMMENDATION. Lint floor: `python3 scripts/report_lint.py --min-refs 15
--map R=proofs/S0-02/tools/pc/run_s0_02_legs.sh --map C=proofs/S0-02/check_buzz_authz.py --map T2=tests/test_s0_02_buzz_authz.py
--map PP=proofs/S0-01/tools/pc/pc_post.sh tasks/briefs/s0-02-support/VERIFY-B9-report.md --root .`; apply its `fix:` hints for at most
three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 07:1xZ, sandbox @ bee499f)

````
$ date -u '+%Y-%m-%d %H:%MZ'; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
2026-09-23 07:15Z
bee499f

$ git diff --stat 221e68b origin/claude/soundbox-kit-migration-iz1jwf -- proofs/S0-02 tests/test_s0_02_buzz_authz.py proofs/S0-01/tools/pc/pc_post.sh | wc -l
0

$ for f in proofs/S0-02/tools/pc/run_s0_02_legs.sh proofs/S0-02/check_buzz_authz.py tests/test_s0_02_buzz_authz.py proofs/S0-02/tools/pc/deliver_event.py proofs/S0-01/tools/pc/pc_post.sh; do printf '%s %s %s last=%s\n' "$(sha256sum < $f | cut -c1-16)" "$(wc -l < $f)" "$f" "$(git log -1 --format=%h -- $f)"; done
93bf0cf987f9d4a0 319 proofs/S0-02/tools/pc/run_s0_02_legs.sh last=221e68b
6bc4729839495148 762 proofs/S0-02/check_buzz_authz.py last=91e33f2
f35cd9542e07ec53 2979 tests/test_s0_02_buzz_authz.py last=221e68b
9fdf8f3a87fa96b3 234 proofs/S0-02/tools/pc/deliver_event.py last=b3eba6a
92bf9609f54652d3 155 proofs/S0-01/tools/pc/pc_post.sh last=77f46a2

$ grep -n 'snapshot_timeline\|delta_timeline\|cmp -n\|REPLAY_PREFIX_MISMATCH\|return 8\|collect_masked\|neg-replayed\|first/\|second/' proofs/S0-02/tools/pc/run_s0_02_legs.sh
36:# Named return code for the neg-replayed leg: the final live timeline is not an
39:S0_02_REPLAY_PREFIX_MISMATCH=8
41:ALL_LEGS="pos-allowed neg-unauthorized neg-bad-signature neg-replayed neg-stale neg-self-authored neg-not-allowlisted revoked"
109:# snapshot_timeline : cut the live timeline at its last newline into
110:# $out/first/timeline.jsonl and print the snapshot's byte length.
111:snapshot_timeline() {
120:  head -c "$first_bytes" "$FD/timeline.jsonl" > "$out/first/timeline.jsonl"
124:# delta_timeline <first_bytes> : prove the final live timeline is an exact byte
125:# extension of the first snapshot (cmp -n on the byte count); on a mismatch print
127:# success write only the post-boundary bytes to $out/second/timeline.jsonl.
128:delta_timeline() {
130:  if ! cmp -n "$first_bytes" "$out/first/timeline.jsonl" "$FD/timeline.jsonl"; then
131:    echo "S0-02: neg-replayed final timeline does not extend the first snapshot (prefix mismatch)" >&2
132:    return "$S0_02_REPLAY_PREFIX_MISMATCH"
135:  tail -c +$((first_bytes + 1)) "$FD/timeline.jsonl" > "$out/second/timeline.jsonl"
140:collect_masked() {
159:# it only after stop_leg; then collect_masked waits for BOTH post artifacts.
193:# neg-replayed, neg-self-authored and neg-not-allowlisted are decided INSIDE
209:NOT run: neg-replayed, neg-self-authored and neg-not-allowlisted need
223:    neg-replayed)
231:      first_bytes=$(snapshot_timeline "$out")
237:      local_first_t0=$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["t0_epoch_s"])' "$out/first/t0.json")
238:      deliver neg-replayed "$out/second" "$(role_for neg-replayed)" \
239:        --reuse "$out/first/delivered-event.json" \
244:      # bytes as the second delivery's timeline. The prefix proof (cmp -n) and
245:      # the delta write (tail) both live inside delta_timeline, so the tests
252:      delta_timeline "$out" "$first_bytes"
297:  if [ "$leg" = "neg-replayed" ]; then
305:    collect_masked "$out/first"
306:    collect_masked "$out/second"
308:    collect_masked "$out"

$ grep -n 'def _check_replay\|def _leg_closure\|_LEG_FILES_PLAIN =\|expected exactly the sub-leg\|second.*prompt\|first.*prompt' proofs/S0-02/check_buzz_authz.py | head -20
143:_LEG_FILES_PLAIN = frozenset({
155:def _leg_closure(leg_dir: Path, leg: str, expected: frozenset):
561:def _check_replay(root: Path, identities: dict, anchors: "Anchors"):
571:            f"neg-replayed: expected exactly the sub-leg directories "

$ grep -n 'def test_.*\(replay\|delta\|snapshot\|prefix\)' tests/test_s0_02_buzz_authz.py
217:def test_replayed_specimen_is_the_positive_event_id():
1062:def test_replay_second_delivery_with_a_turn_fails(tmp_path):
1070:def test_replay_first_delivery_without_a_turn_fails(tmp_path):
1078:def test_replay_with_two_different_event_ids_fails(tmp_path):
1094:def test_replay_second_subleg_uses_only_the_wider_replay_tolerance(tmp_path):
1406:def test_replay_subleg_replaced_by_a_symlink_is_refused(tmp_path):
1428:def test_replay_leg_must_carry_exactly_the_two_subleg_directories(tmp_path):
1724:def test_pc_runner_replay_window_and_nip98_guard_are_pinned():
2657:def test_replay_integration_runner_producer_into_real_checker(tmp_path):
2692:def test_replay_integration_empty_delta_second_timeline_passes(tmp_path):
2707:def test_replay_integration_pin_runner_reproduces_the_failure(tmp_path):
2799:def test_replay_prefix_proof_refuses_a_non_extension(tmp_path):
2811:def test_replay_mid_line_snapshot_first_plus_delta_equals_final(tmp_path):
2822:def test_replay_empty_delta_writes_zero_byte_second(tmp_path):
2834:def test_replay_mutant_cumulative_second_is_rejected(tmp_path):
2854:def test_replay_mutant_no_prefix_proof_still_writes_second(tmp_path):
2882:def test_replay_mutant_off_by_one_delta_breaks_concatenation(tmp_path):
2906:def test_replay_mutant_root_only_masked_log_is_rejected(tmp_path):
2926:def test_replay_mutant_masked_log_first_only_fails_second_closure(tmp_path):
2942:def test_replay_mutant_snapshot_not_cut_at_newline(tmp_path):
2966:def test_replay_mutant_wait_removed_case_a_still_passes(tmp_path):

$ bash scripts/pc_suite.sh set-id -- tests/test_s0_02_buzz_authz.py
1 files set=a5de0beef100

$ grep -n '^| m[0-9]\|^| M[0-9]\|m7\|EQUIVALENT\|equivalent' tasks/briefs/s0-02-support/B9-report.md | head -20
46:| m1 | second gets the cumulative timeline copy | `T2:2834` `test_replay_mutant_cumulative_second_is_rejected` | KILLED: exact `C:621` `if turns[1] != 0` second-turn failure text |
47:| m2 | remove the `cmp -n` prefix proof | `T2:2854` `test_replay_mutant_no_prefix_proof_still_writes_second` plus item 6a | KILLED: mutant writes second; real proof returns rc 8 |
48:| m3 | use `tail -c +$first_bytes` | `T2:2882` `test_replay_mutant_off_by_one_delta_breaks_concatenation` | KILLED: first+delta differs from final |
49:| m4 | root-only masked log (PIN behavior) | `T2:2906` `test_replay_mutant_root_only_masked_log_is_rejected` | KILLED: exact `C:569` `REPLAY_SUBLEGS` replay-root closure text |
50:| m5 | masked log into first only | `T2:2926` `test_replay_mutant_masked_log_first_only_fails_second_closure` | KILLED: exact `neg-replayed/second: missing ['buzzacp.log']` |
51:| m6 | snapshot includes the partial trailing line | `T2:2942` `test_replay_mutant_snapshot_not_cut_at_newline` | KILLED: first snapshot does not end LF |
52:| m7 | remove `wait_turn_window` before final read | `T2:2966` `test_replay_mutant_wait_removed_case_a_still_passes` | EQUIVALENT under this zero-latency fake + `S0_02_TURN_WAIT_S=0`; exact checker PASS. Production latency is why the window remains. |

$ mkdir -p /tmp/vb9/bt && bash scripts/test_summary.sh tests/test_s0_02_buzz_authz.py --basetemp /tmp/vb9/bt 2>&1 | tail -2; rm -rf /tmp/vb9
pytest-exit: 0
pytest-summary: 175 passed in 91.35s (0:01:31)

$ for s in first second; do python3 -c <method/seq per line> $F/$s/timeline.jsonl; done   # the committed PASS fixture's replay leg
first: [(1, 'c2a', 'initialize'), (2, 'a2c', 'result'), (3, 'c2a', 'session/new'), (4, 'a2c', 'result'), (5, 'c2a', 'session/prompt'), (6, 'a2c', 'session/update'), (7, 'a2c', 'result')]
second: [(1, 'c2a', 'initialize'), (2, 'a2c', 'result')]

$ grep -n 'initialize\|continuous\|seq' proofs/S0-02/check_buzz_authz.py | wc -l
0

$ git log -1 --format='%h %ad' --date=short -- $F/second/timeline.jsonl
088efef 2026-09-08

$ sed -n '78,90p' proofs/S0-02/tools/pc/run_s0_02_legs.sh   # wait_turn_window: returns early only when want > 0
# Wait for a turn, or for the window to close. Failure-aware: it also stops early
# when buzz-acp died, so a dead harness is never read as "no turn, as expected".
wait_turn_window() {
  local want=$1 deadline=$((SECONDS + TURN_WAIT_S)) n
  while [ "$SECONDS" -lt "$deadline" ]; do
    # grep -c emits 0 and returns 1 for a no-match file. Preserve its
    # output, neutralize only that status, then supply 0 for an absent file.
    n=$(grep -c '"method":"session/prompt"' "$FD/timeline.jsonl" 2>/dev/null || true); n=${n:-0}
    [ "$n" -ge "$want" ] && [ "$want" -gt 0 ] && return 0
    [ -f "$FD/buzz-acp.exit" ] && { echo "buzz-acp exited during the turn window" >&2; return 6; }
    sleep "$POLL_S"
  done
  return 0

$ sed -n '226,232p' proofs/S0-02/tools/pc/run_s0_02_legs.sh   # the snapshot follows wait_turn_window 1
      deliver pos-allowed "$out/first" "$(role_for pos-allowed)"
      wait_turn_window 1
      # issue #17 step 2: cut the first delivery's timeline at its last newline
      # (a partial trailing line never enters the snapshot) and record its byte
      # length; the second delivery's timeline is the post-boundary DELTA.
      first_bytes=$(snapshot_timeline "$out")
      # F5: sleep 1 before the second deliver to avoid the NIP-98 same-second

$ grep -n 'S0_02_TURN_WAIT_S' tests/test_s0_02_buzz_authz.py | head
1771:        r"^TURN_WAIT_S=\$\{S0_02_TURN_WAIT_S:-(\d+)\}$", text, re.MULTILINE
2192:        "S0_02_TURN_WAIT_S": "0",
2559:        "S0_02_TURN_WAIT_S": "0",
2969:    S0_02_TURN_WAIT_S=0, the second delivery is already in the timeline by the
````
