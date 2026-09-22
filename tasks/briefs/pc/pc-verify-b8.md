# PC lane — VERIFY-B8 (the independent targeted adversarial verify of B8: the S0-02 runner's D1-D3 repairs, the main() wrapper's exact-pin preflight, and the issue #15 refusals in deliver_event.py — new shapes, never the builder's cases)

PIN: b3eba6a

Role: adversarial-verifier. Route: the LOCAL verify route (`agentfactory-verify-local`, the vLLM server default effort; the
route is HYBRID in practice — the cloud step serves a turn when the local step refuses with the chat-template 400 — say so in
the report header, claim nothing about which model produced this report). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it
first. Honey mode: full (line-bounded findings, evidence anchors, SOLID/UNSURE). Keep your context small: bounded terminal
output (`| tail -n 40`), the report drafted after each item, never a whole-file read where `sed -n` of a range answers.

AUTHORIZATION: defensive verification of the owner's own S0-02 tooling. Every run uses a scratch repository + labelled
launcher/post doubles under the lane's own directory; NO live capture, no real launcher, relay, harness server, container or
host secret file is touched (the relay URL in every test is closed loopback). No commit, no push, no repair.

## THE CONTRACT — the frozen contract is the B8 brief `tasks/briefs/pc/pc-b8.md` (items D1, D2, D3, the wrapper, issue #15
rows 1-4) graded against the landed bytes at the PIN; the lane's own report `tasks/briefs/s0-02-support/B8-report.md` is the
CLAIM under test, never the oracle. Verify EVERY claim through the real production path (the real R sourced or executed, the
real D through its CLI), report every observation (no severity filter), then apply the blocking predicate (contract-mapped ·
canonically reproduced · materially effective · a concrete discriminator · in-boundary) and return a GATE RECOMMENDATION
(`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) — the coordinator owns the gate.

Files (read-only for you; write ONLY the report): R `proofs/S0-02/tools/pc/run_s0_02_legs.sh`, D
`proofs/S0-02/tools/pc/deliver_event.py`, T2 `tests/test_s0_02_buzz_authz.py`, PP `proofs/S0-01/tools/pc/pc_post.sh` (the
masked-log producer, :107), PL `proofs/S0-01/tools/pc/pc_launch.py`, NV `proofs/S0-01/tools/nostr_verify.py` (the scalar
bound `nv.n`). Report: `tasks/briefs/s0-02-support/VERIFY-B8-report.md`.

## PREMISE — MEASURED at authoring (2026-09-22 13:21Z, the sandbox clone at the PIN; the PC clone ff-synced to e0e3475 = the PIN + one transcripts commit); re-measure as item 1

```
PIN b3eba6a (the B8 harvest commit on origin; the PC clone at e0e3475 = b3eba6a + a transcripts commit); date 2026-09-22T13:21:02Z
proofs/S0-02/tools/pc/run_s0_02_legs.sh sha256[:16]=2f301973ee198a35 lines=253
proofs/S0-02/tools/pc/deliver_event.py sha256[:16]=9fdf8f3a87fa96b3 lines=234
tests/test_s0_02_buzz_authz.py sha256[:16]=3f341399d0cb4f1d lines=2437
proofs/S0-01/tools/pc/pc_post.sh sha256[:16]=92bf9609f54652d3 lines=155
set id: 1 files set=a5de0beef100
--- R anchors
41:launch_leg() {
44:  rm -f "$FD/launch.ready" "$FD/buzz-acp.exit" "$FD/buzz-acp.pid"
60:stop_leg() {
76:wait_turn_window() {
81:    n=$(grep -c '"method":"session/prompt"' "$FD/timeline.jsonl" 2>/dev/null || true); n=${n:-0}
91:collect_leg() {
99:collect_masked() {
107:    return 9
111:  if grep -Eq '[0-9a-fA-F]{64}' "$out/buzzacp.log"; then
113:    rm -f "$out/buzzacp.log"; return 7
119:post_leg() {
127:    return 9
144:main() {
158:if ! grep -Eq '^PINNED_ENV_KEYS_S0_02 = .*\{"RUST_LOG"\}' "$PINS" ||
159:   ! grep -Fqx 'PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}' "$PINS"; then
171:  exit 3
251:if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
--- D anchors
74:SCALAR_REFUSE_TEXT = (
80:def _privkey() -> str:
87:    key = os.environ.get("BUZZ_PRIVATE_KEY", "").strip().lower()
93:    if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
100:    if int(key, 16) < 1 or int(key, 16) >= nv.n:
105:def _nip98_header(privkey: str, url: str, method: str, body: bytes) -> str:
178:def main(argv) -> int:
--- T2 B8 tests
2135:def test_wait_turn_window_handles_absent_zero_and_n_matches(tmp_path):
2190:def test_collect_leg_succeeds_before_masked_log_exists(tmp_path):
2246:def test_post_leg_invokes_the_scratch_post_after_exit(tmp_path):
2280:def test_main_orders_stop_post_and_masked_collection(tmp_path):
2317:def test_launch_leg_removes_only_stale_owned_markers_before_launcher(tmp_path):
2354:def test_cli_normalises_padded_and_uppercase_keys_before_connecting(tmp_path):
2371:def test_cli_refuses_empty_and_out_of_range_keys_before_connecting(tmp_path):
2414:def test_real_runner_passes_exact_pins_then_stops_at_labelled_deliver(tmp_path):
1735:    assert "grep -Fqx 'PINNED_ENV_VALUES_S0_02" in preflight
--- pc_post.sh producer line
107:mask "$FD/buzzacp.raw.log" > "$FD/buzzacp.log"
--- gates at the PIN (sandbox)
pytest-summary: 162 passed in 70.82s (0:01:10)
coordinator's grade at the landing (13:1xZ): identity = the report's; bash -n / pyflakes / git diff --check clean;
   sandbox test_summary 162 passed in 72.95s / 70.71s (set a5de0beef100); the lane's PC pair 162 passed in 16.20s / 21.04s
mutants re-run by the coordinator in place with a scratchpad restore:
   m4 (.strip() dropped, D:87)            -> test_cli_normalises_padded_and_uppercase_keys_before_connecting: 1 failed   KILLED
   scalar (D:100 guard -> `if False:`)     -> test_cli_refuses_empty_and_out_of_range_keys_before_connecting: 1 failed  KILLED
   m5 (R:159 grep -Fqx -> grep -Fq)        -> whole file under bare pytest: 1 failed, 123 passed, 21 skipped — KILLED, but by the
       SOURCE-TEXT pin at T2:1735 (assert "grep -Fqx 'PINNED_ENV_VALUES_S0_02" in preflight); the behavioral test the report
       names as the killer (test_main_orders_stop_post_and_masked_collection) PASSES under the mutant (2 passed with the
       exact-pins test) → G1 below
the registry screen at the PIN vs before B8: ONE new hit the report's "zero new" missed — AF-AP-40 `.exists()` inside a test
   double: T2 `if Path(os.environ['B8_TRACE']).exists() else 'deliver'` (a fixture, not production) → G2
the lane's own report: red-first pasted for D1/D2/D3/scalar; 7 mutants claimed killed by named tests (D1, D2, D3, scalar,
   m4, m5, m6 = the preflight moved after the destination); report lint 49 refs — OK 22, MISS 16, UNCHECKABLE 10, UNRESOLVED 1
```

## ITEMS

1. **Re-measure the premise** at the PIN (`git rev-parse HEAD`, the four digests + line counts, the anchor lines by `grep -n`,
   the set id, ONE `bash scripts/test_summary.sh tests/test_s0_02_buzz_authz.py -n 4 --basetemp <lane>/scratch/bt1`) and paste
   it under `## PREMISE — RE-MEASURED`. A mismatch = STOP, `CONTRACT-INVALID`.

2. **G1 — the exact-values preflight (R:158-159) has only a source-text pin.** Build a scratch pins file where the exact value
   `PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}` appears ONLY as a SUBSTRING of a longer line (a trailing comment, an
   extra key, a leading `#`) and run the real `main()` through the wrapper: the landed `-Fqx` must REFUSE (rc 3 + the
   `BLOCKER` text, no DEST); the m5 mutant (`-Fq`) must ACCEPT it — a behavioral pair that discriminates the two. State whether
   T2 has any such case today (the coordinator found none by name); if not, that is a FOLLOW-UP or a BLOCKER by the predicate
   (a guard with no behavioral test is an AF-AP-80 instance — decide by the contract's wording, cite it).

3. **The seven mutants, re-run adversarially.** Each in a scratch copy (never the worktree file), `bash -n` / `py_compile` first,
   then the WHOLE T2 file (not only the named test) with counts pasted; state the ACTUAL killing test(s) per mutant. Add at
   least FIVE mutants of your own on the new code: the `n=${n:-0}` fallback removed (R:81); `collect_masked` accepting
   `buzzacp.log` without `buzz-acp.exit` (R:99-107); the 64-hex refusal (R:111-113) inverted; the `rm -f` at R:44 widened to
   `rm -rf "$FD"` (must be caught: it would delete the leg's frame content); the scalar guard's `< 1` changed to `< 0` (key 0
   accepted); the `.lower()` dropped (uppercase keys reaching nv). Every survivor is a finding or a stated equivalence.

4. **D2 through the REAL producer chain in a scratch leg.** The report admits the post step ran only as a labelled double. Wire
   a scratch leg where `post_leg` invokes the REAL `pc_post.sh` (PP) against a scratch frame directory holding a synthetic
   `buzzacp.raw.log` with two throwaway 64-hex strings, and prove: `buzzacp.log` is produced masked (PP:107), `collect_masked`
   copies it only after `buzz-acp.exit` exists, the 64-hex refusal (`return 7`) fires on an unmasked file, rc 9 fires when the
   masked log never appears. If PP needs stack pieces the scratch cannot supply, state exactly which and stop at that line.

5. **The wrapper and its preflight (R:144-171, :251).** New shapes: `PINNED_ENV_KEYS_S0_02` present but `PINNED_ENV_VALUES`
   absent; both present in the wrong order; the pins file a symlink; `S0_02_REPO` unset / pointing at a directory without the
   pins module; `BASH_SOURCE` sourced (no main run) vs executed. Each: the exact rc and text, DEST never created on a refusal.

6. **D3 and D1 edges.** D3: a stale `buzz-acp.pid` naming a LIVE unrelated pid (the runner must not kill it — read R:44-58);
   markers as symlinks; a launcher that writes `launch.ready` late. D1: a timeline with the method string inside a quoted
   payload (over-count), CRLF lines, a missing file (n=0), `grep -c` on a directory.

7. **Issue #15 rows through the CLI.** The scalar refusal text is exactly `SCALAR_REFUSE_TEXT` (D:74) for keys `0`, `f×64`,
   `nv.n` itself, `nv.n - 1` (accepted → must reach the listener exactly once), with the listener counting connections = 0 on
   every refusal; a key with surrounding whitespace + uppercase; a key of 63 or 65 chars; a non-hex character in position 64.

8. **G2 and the report's accuracy.** Re-run `python3 scripts/ap_screen.py R D T2` at the PIN and at 889f1cc (scratch copies via
   `git show`), diff the hit rows, and state every new row; grade the report's "zero new" and its mutant attributions (G1)
   as report-accuracy findings with the class they belong to.

9. **Gates (each under the 420 s cap; paste every line):** the T2 file twice with `-n 4` (counts agreeing, set id
   `a5de0beef100` beside each), `bash -n R`, `python3 -m pyflakes D T2`, `python3 scripts/ap_screen.py R D T2`,
   `python3 scripts/report_lint.py --min-refs 15 <your report>` (bounded: three hint rounds, then paste).

10. **Report** `tasks/briefs/s0-02-support/VERIFY-B8-report.md`: header (route caveat), PREMISE — RE-MEASURED, FINDING
    INVENTORY (every observation, SOLID/UNSURE, the primary source, the class: BLOCKER / FOLLOW-UP / INFO / UNVERIFIED with the
    predicate applied), the MUTATION TABLE (theirs re-run + yours), GATES, ITEMS DELIBERATELY SKIPPED, FOLLOW-UPS FOR D-034,
    NOT-DONE, GATE RECOMMENDATION. No repair; no commit; no push.
