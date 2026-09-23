# E3-R1 — the ONE focused repair of VERIFY-E3 (S0-05's runner cleanup) plus the first build of the A2 census amendment (task #175)

PIN: de33838 (origin head at authoring). Every S0-05 file is byte-identical to 2ebd486, the tree VERIFY-E3 graded (measured below).
LANE: s0-05-e3-r1 (sandbox; agent `code-implementer` on the D-054 pin, in the SHARED tree, no worktree isolation; ROOT is required
for the network-namespace legs, and this sandbox has it). Honey `ultra` Lever-2: your report is DATA — files:lines, pasted counts,
discrepancies, NOT-done. Do NOT spawn subagents.

AUTHORIZATION: defensive work on the owner's own system. You create and destroy network namespaces, veth pairs, a DNAT rule and
stand-in units in THIS sandbox only, to prove the runner leaves nothing behind. Never touch the PC.

CONTRACT SOURCES (read them whole before you design):
- `tasks/briefs/s0-05-support/VERIFY-E3-report.md`: §10 "A SECOND signal while `cleanup` runs" (F3's three reproductions and the
  discriminator), §3 "A2 — the S0-01 tree census: what it can see" (F2's driver and its four writes), the findings F3 and F2 with
  their fix lines, and the GATE RECOMMENDATION.
- The E3 and E3-b briefs (`tasks/briefs/s0-05-support/E3-brief.md`, `tasks/briefs/s0-05-support/E3-b-brief.md`): Part A (A2 as
  written), Part D (the relay reach), R4 (a stop stops).
- `docs/08_DECISION_LOG.md` D-051 (the pair's relay reach exists only for its leg).

WHY THIS ROUND HAS TWO PARTS (the coordinator's routing, D-031): F3 meets the blocking predicate: it is the one focused repair of E3
and E3-b at this contract revision. F2 is a CONTRACT DEFECT: A2 as written ("a stat census of `.markers` and every `v2-*` directory")
cannot see the harm CD1 names (in-place writes to `.markers/buzz-acp.pid`, `.markers/current-framedir`). The coordinator amends A2
here (A2' below). This lane is the first build under the amended contract.

BOUNDARY (exact): MODIFY `proofs/S0-05/tools/pc/run_s0_05_units.sh` (PC) and `tests/test_s0_05_egress.py` (T). CREATE
`tasks/briefs/s0-05-support/E3-R1-report.md` (write it incrementally from the start). READ-ONLY: `proofs/S0-05/netns_lib.sh`,
`proofs/S0-05/check_egress.py`, the collector, the canaries, `proofs/S0-05/spec.json`, every fixture, `proofs/S0-01/**`, `scripts/`,
`.github/`, `.claude/`. A contract line you cannot meet inside the boundary is a DISCREPANCY, never a silent edit.

Other sandbox agents work in this tree on disjoint files. Never touch, run or revert them:
- `scripts/no_laya_in_gates.py`, `tests/test_no_laya_in_gates.py`, `scripts/gate_files.txt`, `tasks/briefs/laya/`;
- `tasks/briefs/ci/`, `tasks/briefs/continuity/`, `tasks/briefs/hermes-repin/`.

Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push`. No outward-facing action; no PC or
bridge use. Every namespace, veth, rule and stand-in you create is destroyed by NAME or PID when you are done (never `pkill -f`,
never a name-based kill of a system process; AF-AP-34), and your report pastes a final census (netns, veth, nat PREROUTING,
`/etc/netns`, `/run/s0-05-egress`, `route_localnet`) that reads empty. The sandbox has about 1.6 GB free: every pytest `--basetemp`
and scratch lives under `/tmp/e3r1/` and is removed after each run.

CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack: `scripts/lane_context.sh -q 'how does the S0-05 runner
clean up and census S0-01' -s cleanup -s _s0_01_census -o /tmp/e3r1/pack.md proofs/S0-05/tools/pc/run_s0_05_units.sh`.

## The contract (build to it; the HOW is yours)

R1 (F3). `cleanup` cannot be aborted by a second INT or TERM. The first signal still ends the run with 130 or 143 through `cleanup`,
exactly as R4 says. A signal that arrives while `cleanup` runs, whether PID-directed or group-directed, changes nothing: every
teardown step runs to its end. Children that `cleanup` starts inherit the same protection. A regression test drives the REAL runner
through VERIFY-E3's deterministic shapes, each a named case:
- (b) a unit whose SIGTERM handler takes at least 2 s, with the second signal fired once the unit has received cleanup's TERM;
- (c) the pair, with a PATH `iptables` hold on the teardown's `-t nat -D` and the second signal fired inside it.

After exit, the test asserts:
- the exit status of the FIRST signal;
- no namespace, veth, `/etc/netns/<ns>`, owner record or relay-reach nat rule is left;
- `route_localnet` is back to its value before the run.

The RED run on the PIN bytes must show the leftover.

R2 (F2, A2 amended; the coordinator's decision). A2' reads:

> The census covers EVERY entry under `<base>/.markers`, recursively, without following symbolic links. It records each entry's
> path relative to `.markers`, its type, mode, uid, gid and size; for a regular file the sha256 of its bytes; for a symbolic link
> its target. Times and inode numbers are not compared. It runs before the first unit and after the last. An added, removed or
> changed entry prints `s0-01-tree-changed: <path>` and fails the leg before the checker, as today. A tree absent on this venue is
> recorded, not failed, as today.

The census file `s0-01-census.json` stays small. It records, for each side, the entry count and one sha256 digest over the sorted
entry records, plus the full before and after records of the CHANGED entries only. It never holds the whole entry list: the PC tree
has 33,864 entries (premise).

Tests:
- each of VERIFY-E3's four writes (an in-place rewrite of `.markers/buzz-acp.pid`, a truncation of `.markers/current-framedir`, an
  append to a frames file, a new file one directory down) fails the leg by name through the real runner;
- a symbolic link inside the tree is recorded by its target, never followed;
- an unchanged tree passes;
- the census file carries no full entry list.

R3 (text). Every comment and declared limit in PC that describes `cleanup`, R4 or A2 says what the code now does. VERIFY-E3's F19
names limit 2 ("removes both … in cleanup", false after a double stop). The comment above the traps says what a second signal does.

## Tests and mutants

Every contract line has a test that is RED on the PIN bytes (paste the RED run) and GREEN after. Mutation table (scratch copies only;
each mutant parses with `bash -n` or compiles with `py_compile`, and its suite collects, AF-AP-78; run each killer on the UNMUTATED
tree first and paste that it passes, AF-AP-138), one row each: mutant · compiles · collected · killed-by / SURVIVED / EQUIVALENT
with the reason. The rows:
- the protection line removed;
- the protection scoped to INT only;
- the census back to directory `lstat` only;
- the sha256 dropped from file records;
- symbolic links followed;
- the digest computed but never compared.

## Gates (paste every command with its output)

- ROOT, TWICE, identical counts, one call each:
  `mkdir -p /tmp/e3r1/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3r1/bt | tail -1; rm -rf /tmp/e3r1/bt`.
  The premise floor is `251 passed`, set 9f0502080347; your count grows by your tests.
- NOBODY:
  `rm -rf /tmp/e3r1nr && mkdir -p /tmp/e3r1nr && chmod 1777 /tmp/e3r1nr && setpriv --reuid=65534 --regid=65534 --clear-groups env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3r1nr/bt | tail -1`.
  Floor `204 passed, 47 skipped`.
- `bash -n` on PC.
- `/root/venv-agent-factory/bin/python -m pyflakes tests/test_s0_05_egress.py`.
- `python3 scripts/ap_screen.py --tests tests/test_s0_05_egress.py` (new hits only).
- `python3 scripts/no_laya_in_gates.py`.
- The final census.

## Report (`tasks/briefs/s0-05-support/E3-R1-report.md`)

The report holds:
- PREMISE re-measured;
- per contract line R1-R3, the files:lines and the tests that pin it;
- RED then GREEN (pasted), the mutant table and the gates;
- DISCREPANCIES;
- NOT-done: F1, F4-F20 are issue #39's; the PC live run is the coordinator's, with the owner's sudo.

Lint floor: `python3 scripts/report_lint.py --min-refs 12 --map PC=proofs/S0-05/tools/pc/run_s0_05_units.sh --map
T=tests/test_s0_05_egress.py tasks/briefs/s0-05-support/E3-R1-report.md --root .`. Apply its `fix:` hints for at most three rounds,
then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 10:2xZ, sandbox @ de33838)

The S0-05 files are unchanged since 2ebd486 (VERIFY-E3's tree), so VERIFY-E3's root gate (`251 passed` twice, set 9f0502080347,
measured by that lane at 09:03-09:10Z) holds for these bytes. The non-root run below is this session's. The coordinator reproduced
F3's mechanism independently with a minimal script: a second TERM inside an EXIT-trap `cleanup` whose INT/TERM traps call `exit`.
The census and cleanup code are pasted as they stand.

````
$ date -u; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
Wed Sep 23 10:23:55 UTC 2026
de33838

$ git diff 2ebd486 de33838 -- proofs/S0-05 tests/test_s0_05_egress.py | wc -l
0
$ for f in proofs/S0-05/tools/pc/run_s0_05_units.sh tests/test_s0_05_egress.py; do echo "$(git rev-parse --short=12 HEAD:$f) $(wc -l <$f) $f"; done
5d58951f392a 578 proofs/S0-05/tools/pc/run_s0_05_units.sh
50bf20a92986 2999 tests/test_s0_05_egress.py

$ bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py
1 files set=9f0502080347
$ (NOBODY gate, the command above)
204 passed, 47 skipped in 6.54s

$ sed -n 322,336p proofs/S0-05/tools/pc/run_s0_05_units.sh
cleanup() {
  local ns owner_pid pid dir
  for ns in $NS_LIVE; do
    owner_pid=$(cat "$(egress_ns_owner_file "$ns")" 2>/dev/null)
    [ "$owner_pid" = "$$" ] && egress_ns_destroy "$ns"
  done
  for pid in $LOG_PIDS; do _kill_our_child "$pid"; done
  for dir in $FIFO_DIRS; do rm -rf "$dir"; done
}
# R4 (E3-b): a stop stops. `cleanup` runs ONCE, on EXIT; SIGINT and SIGTERM exit 130 / 143 through it,
# so no further unit leg starts, no units.json is written, and neither the census comparison nor the
# checker runs. (`trap cleanup EXIT INT TERM` ran cleanup on the signal and then CONTINUED, E3.)
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

$ grep -n "_s0_01_census\|s0-01-tree-changed\|s0-01-census" proofs/S0-05/tools/pc/run_s0_05_units.sh
210:_s0_01_census() {
338:CENSUS_BEFORE=$(_s0_01_census)
523:census_changed=$(python3 -B - "$CENSUS_BEFORE" "$(_s0_01_census)" "$EVIDENCE_ROOT/s0-01-census.json" <<'PY'
573:  while IFS= read -r path; do echo "s0-01-tree-changed: $path" >&2; done <<< "$census_changed"
574:  echo "=== S0-01's tree changed during the leg: the leg FAILS (census: $EVIDENCE_ROOT/s0-01-census.json) ===" >&2

$ sed -n 214-225 (the census body: lstat of .markers and of each v2-* DIRECTORY only)
def snap(path):
    st = os.lstat(path)
    return [st.st_ino, st.st_uid, st.st_gid, stat.S_IMODE(st.st_mode), st.st_mtime_ns, st.st_ctime_ns]
entries = {}
try:
    entries[markers] = snap(markers)
    if stat.S_ISDIR(os.lstat(markers).st_mode):
        for name in sorted(os.listdir(markers)):
            path = os.path.join(markers, name)
            if name.startswith("v2-") and stat.S_ISDIR(os.lstat(path).st_mode):
                entries[path] = snap(path)

$ grep -n "def test_a2_s0_01_tree_change_fails_the_leg\|def test_e3b_r4_" tests/test_s0_05_egress.py
2082:def test_a2_s0_01_tree_change_fails_the_leg(e3dir):
2929:def test_e3b_r4_sigint_stops_the_runner_with_130(e3dir):
2958:def test_e3b_r4_a_stop_in_the_first_leg_starts_no_second_leg(e3dir):

$ (PC, read-only over the bridge, 10:2xZ) the S0-01 tree A2' will census
/home/rocco/s0-01-pinned/.markers
entries=33864 files=33829 dirs=35 links=0
101696529	/home/rocco/s0-01-pinned/.markers
sha256 all files ms=861

$ (coordinator's F3 mechanism reproduction, a minimal stand-in: cleanup under `trap cleanup EXIT`, `trap 'exit 143' TERM`;
   TERM at +0.3 s, a second TERM at +0.6 s while cleanup sleeps between its two steps)
fix=0 rc=143 steps: step1
fix=1 rc=143 steps: step1 step2-released      (fix = `trap '' INT TERM` as cleanup's first line)
````
