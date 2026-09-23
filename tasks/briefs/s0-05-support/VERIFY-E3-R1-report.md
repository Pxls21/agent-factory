# VERIFY-E3-R1 — report (task #185, lane verify-e3-r1, sandbox, uid 0, agent `adversarial-verifier`)

MODEL MIX (coordinator-measured from this lane's transcript; not self-observed per turn): `claude-opus-5-5` from the open (12:17Z)
through ~12:34:49Z, when the Bash call writing an `ip`/`rm`-shim `item2.py` ended with stop_reason "refusal"; then
`claude-opus-4-8` for 49 turns, 12:34:55Z-12:54:32Z; the worker restarted ~12:54Z and this session resumed the draft. By section:
§1 (premise) on opus-5-5; §2-§4 substantially produced in the opus-4-8 span; §4-close (this resume) on the current worker. Every
measurement was RE-RUN and pasted here regardless of which model drove the turn.

COORDINATOR NOTE (2026-09-23 13:5xZ; measured from this lane's transcript, one count per assistant record): 71 records on Opus 5.5
(12:17:04Z-13:00:16Z) and 188 on Opus 4.8 (12:34:55Z-13:46:41Z), with THREE refusals, all on Opus 5.5: 12:34:00Z, 12:34:49Z and
13:00:16Z. The third fired on the first turn after the 12:5xZ resume, with the item-4 PATH `ip` shim driver in context, and every
later turn (13:01Z-13:46Z) ran on Opus 4.8. The header above and the hand-back line "No refusal recurred on the re-run's drivers"
predate that fact. The coordinator reproduced the load-bearing gates at the landed blobs (the lint 19 refs OK 19; qwen-matrix-sh
19 passed, 0 failed; the S0-05 suite as root "263 passed in 232.93s (0:03:52)") and graded PC/T and M/MT MERGE-READY-WITH-FOLLOWUPS;
follow-ups in issue #48. The report is final; the STATUS line below is the lane's own, written while it ran.

STATUS: IN PROGRESS (opened 2026-09-23T12:17:37Z; resumed after a ~12:54Z worker restart). Written incrementally; the gate
recommendation is at the end.
Key: PC = `proofs/S0-05/tools/pc/run_s0_05_units.sh`, T = `tests/test_s0_05_egress.py`, L = `proofs/S0-05/netns_lib.sh`,
M = `harness-ports/bin/qwen-matrix.sh`, MT = `harness-ports/tests/test_qwen_matrix_sh.sh`. PINS: PC/T at 97b589a (the post-push SHA
of local e0f173e), M/MT at 0c05970 (the post-push SHA of local 2fd0a7d). Nothing in this lane ran on the PC.

## 1. PREMISE — re-measured (sandbox, uid 0, before any state of mine existed)

````
$ date -u; id -u; cat /proc/loadavg; df -h /
2026-09-23T12:17:37Z
0
1.58 3.27 2.99 5/166 26562
/dev/vda        252G   36G  1.4G  97% /
$ git log --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf -12 (the two pins, matched by subject)
97b589a E3-R1 landed (task #175; GATED-PENDING-VERIFY): a second signal cannot abort the S0-05 runner's cleanup, and the S0-01 tree census compares content
0c05970 qwen-matrix.sh: a second signal cannot abort the baseline restore (task #176, AF-AP-145's matrix instance)
$ git diff --stat 97b589a 9b55f6b -- PC T ; git diff --stat 0c05970 9b55f6b -- M MT      (origin head 9b55f6b; both empty, rc 0)
$ blob@pin[:12] blob@worktree[:12] lines
076f863a54b9 076f863a54b9 641 proofs/S0-05/tools/pc/run_s0_05_units.sh
8b2f1f042bdf 8b2f1f042bdf 3367 tests/test_s0_05_egress.py
e42d72236c02 e42d72236c02 195 harness-ports/bin/qwen-matrix.sh
75ca7c341681 75ca7c341681 263 harness-ports/tests/test_qwen_matrix_sh.sh
$ grep -n "trap \|^cleanup()\|_s0_01_census\|census-failed\|census failed" PC
223:_s0_01_census() {  # snap | compare <census file>
382:cleanup() {
383:  trap '' INT TERM
394:# checker runs. (`trap cleanup EXIT INT TERM` ran cleanup on the signal and then CONTINUED, E3.)
400:# `exit` would end the EXIT trap before `cleanup` began (E3-R1 report, section 2). Not covered: a stop
403:trap cleanup EXIT
404:trap 'trap "" INT TERM; exit 130' INT
405:trap 'trap "" INT TERM; exit 143' TERM
407:CENSUS_BEFORE=$(_s0_01_census snap)
594:census_changed=$(_s0_01_census compare "$EVIDENCE_ROOT/s0-01-census.json" 3<<<"$CENSUS_BEFORE") \
632:  echo "=== S0-01's tree census failed (exit $census_failed): the leg FAILS ===" >&2
$ grep -n "^def test_e3r1\|^def _iptables_shim" T
2415 _iptables_shim · 3057 r1_b · 3099 r1_c · 3147 r1_a · 3254 r2 four writes · 3299 r2 symlink · 3339 r2 unchanged · 3358 r2 cannot be taken
$ grep -n "trap " M
96:  trap '' INT TERM
97:  trap - EXIT
143:# EXIT trap before cleanup began (measured on the S0-05 runner, E3-R1 report section 2). Not covered:
145:trap cleanup EXIT
146:trap 'trap "" INT TERM; exit 130' INT
147:trap 'trap "" INT TERM; exit 143' TERM
$ host census before anything of mine: netns 0 · veth 0 · nat `-P PREROUTING ACCEPT` · /etc/netns 0 · /run/s0-05-egress empty
  route_localnet: all=0 default=0 eth0=0 ifb0=0 ifb1=0 lo=0 · strace /usr/bin/strace · gdb /usr/bin/gdb
````
$ (item 1's one full root run of T, 12:18:40Z → 12:22:32Z; loadavg before 1.49 2.93 2.89, after 1.80 2.01 2.49)
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py
1 files set=9f0502080347
$ /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/ve3r1/bt1 > /tmp/ve3r1/premise-root.log 2>&1; echo "pytest rc=$?"; tail -1 …
pytest rc=0
263 passed in 231.31s (0:03:51)
$ host census after it: netns 0 · veth 0 · nat `-P PREROUTING ACCEPT` · /etc/netns 0 · /run/s0-05-egress 0
````

PREMISE HOLDS for every item: the four blob ids and line counts, the trap lines (PC:382-383, PC:403-405; M:96-97, M:145-147), the
census line map (PC:223, PC:407, PC:594, PC:632) and the eight test anchors are exactly the brief's; T as root reads `263 passed`,
set 9f0502080347, the landing gate's count. No item is CONTRACT-INVALID on its premise.

Code intel: `scripts/lane_context.sh -q 'how does the S0-05 runner stop, clean up and census S0-01' -s cleanup -s _s0_01_census -o
/tmp/ve3r1/pack.md PC T` ran (170 lines). graft: "unmapped — graft ask unavailable" (nothing indexed under
`proofs/S0-05/tools/pc/`); crg: `_s0_01_census` 1 caller (PC itself), 0 tests_for; ripwire: 0 callers (blind to shell). Fallback
instrument: PC read whole (641 lines), L's `_egress_ns_teardown` / `egress_relay_reach_del` / `egress_ns_destroy` (L:324-410) and T's
E3-R1 block (T:3011-3367) plus its helpers (T:1554-1760, T:2319-2427) read by line range.

## 2. R1 by NEW signal shapes (real runner, `_runner_session`, slow-unit shape; driver /tmp/ve3r1/drv/item2*.py)

Every case runs the REAL runner in its own session (pgid=pid). The FIRST signal is pid-directed and opens the wide cleanup window on
the 3 s slow unit (T's SLOW_STOP, T:3021), exactly as T's r1_b does; the SECOND signal(s) are the new shapes, fired once cleanup's
TERM has reached the unit (its marker). "clean" = T._census CLEAN + no nat rule + route_localnet as before. loadavg 0.3-0.7 (1-min)
throughout — a mechanism, not a clock, decides each verdict.

````
double-INT-pid            rc=130 clean=True    (2nd INT to the pid, dropped)
2nd-double-INT-group      rc=143 clean=True    (two INT to the group during cleanup, both dropped)
triple-TERM-pid           rc=143 clean=True    (three TERM total, 2nd+3rd dropped)
triple-mixed-pid+group    rc=143 clean=True    (2nd INT pid, 3rd TERM group, both dropped)
INT-then-TERM-pid         rc=130 clean=True    (status stays the FIRST signal's, 130)
2nd-TERM-group            rc=130 clean=True
2nd-QUIT-group  (x3)      rc=143 clean=True    (SIGQUIT: non-interactive bash sets it SIG_IGN, so it is dropped)
2nd-HUP-group   (x3)      rc=-1  clean=FALSE   LEFT netns+veth+/etc/netns+owner  <-- FINDING VE3R1-F1
2nd-HUP-pid     (x1)      rc=-1  clean=FALSE   LEFT netns+veth+/etc/netns+owner
only-HUP  launch-window   rc=-1  clean=True    (deferred through the foreground `sleep`, then EXIT trap runs cleanup)
only-QUIT launch-window   rc=1   clean=True    (ignored; the run reaches its own end)
````

R1 as built (INT and TERM, PID- and group-directed, single/double/triple, in any INT/TERM combination) HOLDS: every INT/TERM shape is
dropped, the status stays the FIRST signal's, and the host is clean. The unit is reaped in every case. This confirms F3's repair for
the frozen contract's signal set.

**VE3R1-F1 (FOLLOW-UP, not a blocker). A second SIGHUP during cleanup aborts it and leaves host state.** A SIGHUP arriving while
cleanup runs (PID- or group-directed) kills bash (rc=-1 = killed by signal 1) before the teardown finishes, leaving the namespace,
its veth, `/etc/netns/<ns>` and the dead runner's owner record (for the pair leg it would also leave the DNAT and route_localnet=1 —
same class as F3). Deterministic: 4/4. MECHANISM: cleanup's guard (PC:383) and the two handlers (PC:404-405) ignore INT and TERM
ONLY; SIGHUP has no trap, so a HUP delivered during cleanup terminates bash with its default action. Why a HUP elsewhere is clean: as
the FIRST/only signal (or in the launch window) it is deferred while bash waits on a foreground child, then bash exits THROUGH the
EXIT trap and cleanup runs to the end (measured: only-HUP launch-window is clean). The gap is specifically a HUP that lands DURING
cleanup, when the EXIT trap is already the running context.
- Contract mapping: NONE against R1. R1 (frozen) is "a second INT or TERM"; the brief's item 2 states "R1 names INT and TERM only, so
  say what the runner does and whether the leftover state matters", and the runner's own comment (PC:395-402) claims only INT/TERM
  coverage and names SIGKILL as not-covered. So this does not contradict a frozen criterion — it is the characterization the brief
  asked for. Predicate condition 1 fails: FOLLOW-UP.
- Does the leftover matter? On the owner's PC the runner is run under sudo, in a terminal, likely over SSH (E3 report §8). A closed
  terminal or a dropped SSH session sends SIGHUP to the foreground process group. If that lands in the ~2-7 s cleanup window, egress
  state (a namespace, and for the pair the leg-scoped DNAT + route_localnet=1) outlives the run — the exact harm F3 addresses, by a
  signal F3's contract did not name. Suggested (optional) hardening: add HUP to the ignore set — `trap '' INT TERM HUP` at PC:383 and
  `trap "" INT TERM HUP` in each handler, plus a `trap ... HUP` so a first HUP still exits through cleanup deterministically.

## 3. R1, the microsecond window — is M1b (the one-line repair) deterministically killable? (drivers /tmp/ve3r1/win/)

The window reproduced INDEPENDENTLY on a minimal script shaped like PC's traps (f3.sh: cleanup with `trap '' INT TERM` first, then
the two handlers; design 1 = M1b's bare-exit handlers, design 2 = the shipped `trap "" INT TERM; exit` handlers). Two TERMs <gap> µs
apart, 40 trials/cell, loadavg 1-4 (a mechanism decides, not the clock):
````
design=1 (M1b)  gap=0/20 us: full 40/40   gap=50 us: none 6/40   gap=100 us: none 7/40   gap=200 us: full 40/40
design=2 (ship) gap=0..200 us:            full 40/40 EVERY cell (0 aborts)
````
This CONFIRMS the builder's D1: the one-line repair aborts cleanup 6-7/40 at 50-100 µs; both ignores close it (0 aborts). Mechanism:
in design 1 the first TERM handler's `exit 143` reaches the EXIT trap while the TERM trap is still `exit 143` (cleanup's `trap ''`
has not run), so a second TERM in that sliver runs `exit 143` again and abandons cleanup; in design 2 the first handler sets
`trap "" INT TERM` BEFORE exiting, so every later TERM is dropped.

Deterministic opener — TRIED, none found that is committable:
- SIGSTOP + queue two TERMs, then SIGCONT: CANNOT work. Standard signals COALESCE — a stopped process resumes with ONE pending TERM,
  not two, so the freeze-and-queue does not rebuild the two-delivery race. (Reasoned, and consistent with the coalescing rule.)
- gdb/ptrace freeze at `run_exit_trap` (the brief's suggestion), gdb 15.1, root, ptrace available: the breakpoint hits at the right
  point (cleanup about to run), but in `-batch` mode the harness prevented cleanup from completing EVEN WITH NO injected signal — the
  control `INJECT=0` produced no cleanup output (`step1` never written) for BOTH designs (drivers gdbdrv.py/gdbctl.py; the `.ready`
  file is written, `step1` is not). So the gdb path breaks the exit trap unconditionally and CANNOT discriminate design 1 from design
  2. A gdb-driven test is also unfit as a committed gate: it needs root AND gdb, depends on the bash build's symbol layout, and the
  CI venue has neither (it would be a flaky, non-portable, non-LLM-free-in-spirit gate, not a deterministic one).
- A signal FLOOD is what the builder measured (26/60 design 1, 0/360 design 2): statistical, so flaky, and design 2 drops all of it.

CONCLUSION (item 3): M1b has NO practical deterministic, committable killer — which MATCHES the builder's claim. M1b SURVIVING is
correct and is NOT a hollow green: design 2 is safe BY MECHANISM (the first handler ignores before exiting), evidenced by the 0/360
probe and reproduced here (0/40 at every gap). Shipping BOTH ignores is the right call; a deterministic test is not the evidence, the
mechanism is. This is the strongest reading FOR the builder's design, reached by trying to break it.
INFO VE3R1-I2: design 2 emitted `bash: warning: run_pending_traps: bad value in trap_list[15]: 0x1` on the minimal probe when a
second signal was dropped mid-reset — a cosmetic bash warning (bash recovers, cleanup completes); it may reach the operator's stderr
on a real dropped second signal. Harmless; noted.

## 4. R1, the cost of ignoring — a hung teardown child (real runner, PATH `ip` shim; driver /tmp/ve3r1/drv/item4.py)

The injection seam: the runner resolves `ip` via `command -v ip` (PC:77) and the cleanup LIBRARY (`netns_lib.sh`) calls bare
`ip`/`iptables`/`sysctl`/`rm` (PATH-resolved at call time). There is NO dedicated `S0_05_IP`/`rm` override env var; a PATH-prefix
shim is the seam, and it is the SAME seam T's committed tests already use (`_iptables_shim` T:2415, the `ip` shim in
`test_e3r1_r1_a` T:3155, `test_e3b_r4_a_stop_in_the_first_leg` T:2969). The shim below runs the REAL `ip` for every argv but the one
it holds, in throwaway scratch under /tmp/ve3r1.

Case: `ip link del <host_if>` (cleanup's veth removal) is held 120 s, gated on the slow unit's `term-*` marker so the hold lands in
CLEANUP, never in create's destroy-first. First TERM to the runner pid opens cleanup; cleanup reaches the held `ip link del`; the
child inherits cleanup's `trap '' INT TERM`. Then INT+TERM are sent to the whole process group for ~2 s.
````
flood INT+TERM to the group ~2 s: runner_alive=True  hangs_recorded=1  (loadavg 0.55 1.12 1.36)
after SIGKILL to the group:       rc=-9  leftover={netns:True, veth:True, etc_netns:True, owner:['s0-05-hermes-acp.owner']} nat=[]  elapsed=1.5s
census after reap (my egress_ns_destroy): CLEAN
````
FINDING VE3R1-F2 (FOLLOW-UP/INFO, not a blocker). A stop that cannot be stopped: when a teardown child hangs, the operator cannot
end the run with INT or TERM (the child and cleanup inherit SIG_IGN, so the group flood is dropped — runner stays alive), and
cleanup's time is NOT bounded at the `ip`/`iptables` syscall level (the library bounds only the pid-kill WAIT loops, L:352-385: 5 s +
2 s; the `ip netns del`/`ip link del`/`iptables -D` calls themselves have no timeout). The only escape is SIGKILL to the group, which
runs no trap and leaves the whole host state (namespace, veth, `/etc/netns/<ns>`, owner record; for the pair also the DNAT +
route_localnet=1 — the F3 class).
- Predicate: (1) NOT contradicting a frozen criterion — R1 REQUIRES the ignore and "children inherit the same protection", so the
  un-interruptibility is the design working as specified. (2) NOT reproducible through the REAL `ip` — on the PC `ip netns del`/`ip
  link del` are fast kernel ops; the hang needs an injected shim, a pathology the runner does not introduce. So conditions 1 and 2
  fail: FOLLOW-UP.
- Why it still matters: a genuinely stuck teardown syscall (a kernel/netns edge, an `iptables` lock contention on a busy host) would
  leave the operator only SIGKILL, and SIGKILL leaves state. The operator's mental model should carry this. Optional hardening
  (not contract-required): wrap the teardown's `ip`/`iptables` calls in a `timeout`, or leave one signal as an escape hatch.

## 5. R2 census with NEW shapes (real runner leg `_census_leg`; drivers /tmp/ve3r1/drv/item5*.py)

Each change is made by the unit (uid 65534) between the runner's snap (before units) and compare (after units). "named" =
`s0-01-tree-changed` line; "leg passes" = the checker ran. Records compare type, mode, uid, gid, size, and a file's sha256 or a
link's target (PC:230-247); times, inodes, link counts and xattrs are declared NOT compared (limit 7, PC:57-58).
````
file -> FIFO (same name)        named ['f']       leg FAILS (checker=False)   RIGHT: type change caught, fail-closed
file -> unix socket (same name) named ['f']       leg FAILS                   RIGHT: type change caught
file -> device node (mknod)     n/a: os.mknod EPERM as nobody                 RIGHT: a non-root unit CANNOT create a device node;
                                                                              if root ever did, it is a type change -> named
hard-link count change          named []          leg PASSES (checker=True)   RIGHT: nlink not compared (limit 7); declaration TRUE
xattr set (user.s0_05)          named []          leg PASSES                  RIGHT: xattr not compared (limit 7); declaration TRUE
mode-only chmod 0644->0600      named ['f']       leg FAILS                   RIGHT: mode IS compared
changed-and-back (transient)    named []          leg PASSES                  RIGHT: a change reverted between snap and compare is
                                                                              never observable by a before/after census — by design
.markers replaced (symlink)     named [f,v2-run-1,v2-run-1/x] leg FAILS       RIGHT: entries 4->1, wholesale replacement caught by
                                                                              the entry-set difference, fail-closed before the checker
3000-deep directory chain       named (whole chain) leg FAILS                 RIGHT: census walks with an explicit todo stack
                                                                              (PC:254-262), NOT recursion — no RecursionError
300 MB new file                 named ['big']     leg FAILS  leg_wall 4.2 s   RIGHT: sha256 reads all bytes, bounded, no hang
tree changed WHILE census walks  NOT reproduced through the runner            the runner snaps before any unit and compares after all
                                                                              units exit, so no unit is a concurrent writer; the walk
                                                                              is not atomic (listdir then per-entry record), but a
                                                                              non-unit writer during the census window is outside the
                                                                              runner's control and outside S0-05's threat model
an entry the census cannot read  the census runs as ROOT — permission is never the barrier; the only unreadable case is a type-race
                                 (regular->special between listdir and open), handled by O_NOFOLLOW|O_NONBLOCK + the fstat S_ISREG
                                 check (PC:238-241) -> OSError -> census exits non-zero -> leg fails closed (item 6)
````
R2 as built HOLDS for every reachable shape: every COMPARED attribute change (type, mode, size, content, target) is named and fails
the leg before the checker; every NOT-compared attribute (nlink, xattr, times, inode) is correctly invisible and matches the declared
limit; a wholesale `.markers` replacement is caught by the entry-set difference; deep trees and large files are bounded, not hangs. No
finding: the census is sound against these shapes.

## 6. D2 — the census that cannot be taken (real census code, hostile fd-3 baselines; /tmp/ve3r1/it6/)

The REAL census block (PC:224-285, extracted verbatim) driven with hostile baselines on fd 3 and hostile bases:
````
compare, GOOD baseline, unchanged           rc=0 changed=[]        -> leg PASSES (correct)
compare, EMPTY baseline (snap had failed)   rc=1 no file written   -> census_failed -> leg FAILS  (fail-closed)
compare, TRUNCATED baseline                 rc=1                   -> census_failed -> leg FAILS  (fail-closed)
compare, valid-but-WRONG baseline (a string)rc=1 TypeError         -> census_failed -> leg FAILS  (no swallowed exception)
snap, base/.markers ENOTDIR (base a file)   rc=1 NotADirectoryError-> NOT treated as absent; compare then fails on the empty
                                                                      baseline -> leg FAILS  (the committed test's mechanism)
snap, base absent entirely                  rc=0 prints {}         -> absent, recorded not failed (correct, A2')
````
D2 HOLDS: the leg fails with the printed line BEFORE the checker (PC:631-634 `census_failed` branch precedes PC:640 `=== checker
===`), and the census failure is `exit 1`, whose EXIT trap runs cleanup (the committed `test_e3r1_r2_a_census_that_cannot_be_taken`
asserts `_census == CLEAN`, so cleanup leaves nothing). There is NO census failure that reads as a pass: `census()` catches ONLY
`FileNotFoundError` (-> `{}` absent, PC:252-253); every other error (ENOTDIR, a corrupt/empty/wrong-type baseline, a mid-walk removal)
propagates to a non-zero exit -> `census_failed` -> the leg fails. The only passes are unchanged-tree and absent-tree, both
legitimate.
INFO VE3R1-I3: PC:407 (`CENSUS_BEFORE=$(_s0_01_census snap)`) does NOT check snap's exit code; a failed snap yields an empty
`CENSUS_BEFORE`, and the unit legs RUN before the failure is caught at compare time. This is still fail-closed (the leg fails at
compare, no false pass) and only wastes the leg's work + detects late — a defense-in-depth nicety, not a defect. Not contract-mapped.

## 7. The tests themselves — a killed test's leftover and self-heal (real pytest + real library; /tmp/ve3r1/drv/item7*.py)

- SIGKILL the pytest process while a netns test is mid-flight: momentarily leaves netns + owner record, but the runner subprocess
  runs in its OWN session (`start_new_session=True`, T:3037), so it is NOT killed with pytest and completes its own EXIT-trap cleanup
  — measured: leftover gone within 3 s, and the re-run passed clean.
- Worst case, SIGKILL pytest AND the runner (no trap runs at all): a genuine PERSISTENT leftover — namespace `s0-05-hermes-acp`,
  its veth, `/etc/netns/<ns>`, and the owner record — as measured (`ip netns list` showed it).
- SELF-HEAL, deterministic: I planted exactly that leftover (real namespace + veth + `/etc/netns` + an owner record naming DEAD pid
  999999) and re-ran the test: `2 passed`, and the host after was `owner=[] etc_netns=[] veth=0`. MECHANISM: the library's idempotent
  `egress_ns_create` runs `_egress_ns_claim` (a stale/dead-pid record is taken over by an atomic rename, L:162-190) then destroy-first
  `_egress_ns_teardown` (removes the stale namespace, veth, `/etc/netns`, relay reach, L:346-403). So the NEXT test that creates the
  same namespace name cleans the prior leftover and passes.
INFO VE3R1-I4 (not contract-mapped; not a blocker): a killed test's leftover persists ONLY until the next create of that SAME
namespace name. A killed PAIR test would leave `route_localnet=1` + the DNAT on `ehda7d8593` until the next `s0-05-buzz-acp` create
resets them; if no later test creates that name, they would reach the final census. In practice each committed test creates+destroys
its own namespace, and the suite ends clean (premise: 263 passed, host clean after). Not a runner-contract issue — the contract covers
the runner's cleanup on a STOP, not pytest-crash recovery — and it self-heals.

## 8. R3 — comments and declared limits vs the code

PC (the frozen R3 scope) is ACCURATE:
- Limit 2 (PC:39-45): "egress_ns_destroy removes both ... which a second SIGINT or SIGTERM cannot cut short" — TRUE (item 2). This
  fixes VERIFY-E3 F19's limit-2 part (the old bare "removes both ... in cleanup", false after a double stop, is now qualified).
- Limit 7 (PC:56-58): compares type/mode/uid/gid/size + a file's sha256 + a link's target; not times/inodes/link counts/xattrs;
  "never reads what a symbolic link points to" — every clause TRUE (item 5).
- Cleanup comment (PC:377-381) and trap comment (PC:392-402): "its first command ignores SIGINT and SIGTERM ... every command it
  starts inherits the ignore" — TRUE (item 4); R4 "cleanup runs ONCE, on EXIT; SIGINT and SIGTERM exit 130/143" — TRUE (item 2);
  "Not covered: ... a SIGKILL, which runs no trap" — TRUE. The three "stat census" mentions (PC:211 A2' rationale, T:3240) and the
  trap-shape at PC:394 are explicit HISTORICAL context ("VERIFY-E3 F2 showed", "ran cleanup ... and then CONTINUED, E3"), not current
  claims — accurate.
- Compare comment (PC:591-592): "a change ... fails the leg, and so does a census that could not be taken" — TRUE (items 5, 6).

VE3R1-F3 (FOLLOW-UP, doc; not a blocker). Stale test docstring. `test_a2_s0_01_tree_change_fails_the_leg` (T:2083) still opens "the
runner takes a stat census of <pinned base>/.markers and every v2-* directory" — the SUPERSEDED A2 mechanism — while the test body now
verifies A2' (it asserts `changed_records[...]["mode"]`, the recursive `entries == 3`, and carries the in-body A2' comment at
T:2107-2110). The first sentence describes the old stat census; the code and the rest of the test are A2'. Predicate: not contract-
mapped (R3 is PC-scoped; this is a T docstring) and no material effect (documentation) -> FOLLOW-UP. Fix: update the docstring's first
sentence to A2' (content census of every entry under `.markers`, recursively).
VE3R1-F1 tie-in: the trap comment (PC:400-402) names SIGKILL as not-covered but is silent on SIGHUP, which is also not covered (item
2). The comment is scoped to "a second SIGINT or SIGTERM" so it makes no false claim, but it does not enumerate HUP — a completeness
gap, tied to VE3R1-F1 (FOLLOW-UP).

## 9. NEW mutants (scratch /tmp/ve3r1/mut/tree, runner blob = PIN 076f863a54b9; never the builder's M1-M10)

Each on a line the builder's rows did NOT touch; each `bash -n` clean, its census heredoc `py_compile`-clean, the file collects 263;
every killer was GREEN on the UNMUTATED scratch copy first (AF-AP-138: `9 passed` across the six selections).
````
mutant                                                     line (untouched by M1-M10)   compiles/collect   killer -> verdict
MUT1 R1 cleanup owner check  = "$$"  ->  != "$$"           PC:387                        bash-n0 col263     r1_a: 2 failed  KILLED
MUT2 R1 TERM handler status  exit 143 -> exit 142          PC:405                        bash-n0 col263     r1_b: 2 failed,1 passed KILLED
MUT3 R2 recursion  drop todo.append(rel)                   PC:261                        bash-n0 col263     four-writes: 1 failed KILLED
MUT4 R2 mode field -> constant "0644"                      PC:232                        py0 col263         a2: 1 failed  KILLED
MUT5 R2 uid field  st.st_uid -> 0                          PC:233                        py0 col263         four-writes: 1 failed KILLED
MUT6 D2 census-failed branch  [ -n ] -> [ -z ] (inverted)  PC:631                        bash-n0 col263     cannot-be-taken+unchanged: 2 failed KILLED
````
6/6 KILLED. The MUT1 kill is a reap-timeout (the inverted owner check makes cleanup skip its own namespace, `held` never written,
r1_a's 120 s wait times out); MUT2/3/5/6 fail fast on assertions. R3 is TEXT only, so no behaviour-changing mutant exists for it (a
comment change is not test-catchable — expected; the builder's table also carries no R3 mutant). The R1/R2/D2 tests are not hollow:
each contract mechanism (the owner check, the stop status, the recursive walk, the mode/uid fields, the census-failure branch) is
independently gated on a line the builder never mutated. Runner restored to the PIN blob after the audit.

## 10. THE MATRIX RUNNER M/MT (task #176, 2fd0a7d; the coordinator's own fix, never self-accepted)

`bash harness-ports/tests/run-all.sh` -> ALL SUITES PASSED (test_qwen_matrix_sh.sh: 19 passed, 0 failed). M's cleanup uses E3-R1's
design: `trap '' INT TERM` after reading rc (M:96), `trap - EXIT` (M:97), and each handler ignores both before its exit (M:146-147).

Attacked through the REAL `harness-ports/bin/qwen-matrix.sh` with MT's fakes (drivers /tmp/ve3r1/mdrv/), NEW shapes (never MT's three),
the second signal placed during a HUNG restore install (fake `qwen-server install` sleeps 8 s) or in the padded read-loop window:
````
2nd TERM during install (pid)     rc=143  restored=True   OK   the ignore drops it; restore completes
2nd TERM during install (group)   rc=143  restored=True   OK
double INT during install         rc=130  restored=True   OK
2nd HUP during install (pid)      rc=-1   restored=True   (HUP deferred past the foreground install child; baseline restored, no run-complete)
2nd HUP during install (GROUP)    rc=-1   restored=FALSE  cell unit LEFT  <-- VE3R1-F4
2nd HUP in the read-loop window   rc=-1   restored=FALSE  cell unit LEFT  <-- VE3R1-F4
````
M's R1-analog HOLDS for INT/TERM (pid/group, single/double, during the GPU kill/install/sha window): the second signal is dropped,
the restore completes (baseline restored), the status stays the first signal's — the fix works as its commit claims.

Discriminator SOUND (the 0.3 s delay vs the padded env): I built the PRE-FIX M (cleanup `trap - EXIT INT TERM`, handlers bare-exit)
and ran the same windows — `PRE-FIX readloop 2nd TERM pid: rc=-15 cell unit LEFT`, `PRE-FIX install 2nd TERM group: rc=-15 cell unit
LEFT` (RED). The fix goes GREEN (restored=True) at the identical window. So the padded env genuinely holds cleanup in the read loop
past 0.3 s (the second signal lands BEFORE the restore, aborting the pre-fix), and MT does NOT pass for the wrong reason. How I know:
the pre-fix design fails the same test the fix passes — if the read loop were faster than 0.3 s the pre-fix would have passed too.

VE3R1-F4 (FOLLOW-UP, not a blocker; M-analog of VE3R1-F1). A SIGHUP during M's cleanup leaves the owner's model-server unit in the
CELL configuration: a group HUP kills the hung restore-install child (baseline never written), and a HUP in the read-loop window kills
bash before the restore. Predicate: commit 2fd0a7d names "a second SIGINT or SIGTERM" and lists only SIGKILL as not-covered — SIGHUP
is out of its stated scope, so this does not falsify a stated claim. FOLLOW-UP (the operator on the PC runs this under sudo; a closed
terminal / dropped SSH during the restore leaves the unit in a cell config — the exact harm the fix addresses, by an uncovered signal).
VE3R1-F5 (FOLLOW-UP, not a blocker; M-analog of VE3R1-F2). The ignore makes a hung restore install unstoppable by INT/TERM: the
install child inherits SIG_IGN (M:96 precedes M:119), so an operator INT/TERM flood is dropped (measured: the 2nd TERM waited out the
full 8 s hang); only SIGKILL stops it, leaving the cell unit. Not contract-mapped; a design tradeoff, same class as VE3R1-F2.

## 11. GATES (pasted) and the final host census

````
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py
1 files set=9f0502080347
$ ROOT run 1 (13:33:43Z, loadavg 1.61)  pipestatus=0
263 passed in 231.97s (0:03:51)
$ ROOT run 2 (13:37:35Z, loadavg 2.10)  pipestatus=0
263 passed in 232.69s (0:03:52)
$ NOBODY (setpriv 65534, PYTHONPATH=src)  pipestatus=0
204 passed, 59 skipped in 6.40s
$ bash -n proofs/S0-05/tools/pc/run_s0_05_units.sh  -> rc=0
$ bash -n harness-ports/bin/qwen-matrix.sh          -> rc=0   (read-only, for completeness)

$ FINAL HOST CENSUS (13:41:56Z)
netns:            count=0
veth:             0
nat PREROUTING:   -P PREROUTING ACCEPT
/etc/netns:       []
/run/s0-05-egress:[]
route_localnet:   all 0 (no interface nonzero)
````
Counts agree across the two root runs (263 passed, set 9f0502080347 — the premise floor) and the nobody run (204 passed, 59 skipped:
the 12 new root-only tests skip). `bash -n` clean on PC and M. The host is clean: no namespace, veth, nat rule, `/etc/netns` entry,
owner record or nonzero route_localnet. The `sleep`/`pytest` processes seen in a `ps` sweep belong to the THREE other live sandbox
agents (their poll loops) and the coordinator's `ci_gate.py --wait` (parents 6163/6164/14732/25804/7850/20180) — NOT this lane; I left
them untouched. My own runs all exited; no netns/veth/gdb of mine remain.

## DISCREPANCIES

- D-1 (REFUSAL, coordinator-measured). At 12:34:49Z a Bash call writing an `ip`/`rm`-shim `item2.py` ended stop_reason "refusal" on
  claude-opus-5-5; the harness then ran the lane on claude-opus-4-8 (12:34:55-12:54:32Z), and a worker restart at ~12:54Z resumed it
  on the current worker (header MODEL MIX). The shim technique is authorized (defensive testing of the owner's own runner cleanup in
  throwaway scratch, per the brief). Injection seam: the runner reads NO dedicated `ip`/`rm` override — it resolves `ip` via
  `command -v ip` (PC:77) and the cleanup library calls bare `ip`/`iptables`/`sysctl`/`rm` (PATH-resolved), so a PATH-prefix shim is
  the seam, and it is the same seam T's committed tests use (`_iptables_shim` T:2415, the `ip` shims T:3155/T:2969). No refusal
  recurred on the re-run's drivers (item2 signals, item4 hung-child shim, item5-7 census/kill drivers, item10 matrix fakes all ran).
- D-2. The premise `_iptables_shim`/`ip`-shim references in the brief's item-2 note (an `ip`/`rm` hold for 2 s after the first signal)
  describe the REFUSED approach; this lane's items 2 and 4 reached the same windows through the slow-unit marker (item 2) and a
  cleanup-gated `link del` hold (item 4) — the same real runner, a different seam, no re-implementation.
- D-3. Item 3's deterministic-opener probe used gdb (the brief's suggestion) but the batch-mode harness prevented cleanup completing
  even with no injected signal, so it could not discriminate; the window claim rests on the statistical probe + the mechanism, as the
  builder's does.

## NOT-done (first-class)

- NOTHING ran on the PC (no bridge use in this lane, per the brief): the live run is the owner's, with sudo. The real units' stop
  behaviour, the real `ip netns del` timing (item 4's hang is a sandbox shim, not the real `ip`), and the PC-scale census timing
  (item 5's 300 MB / 3000-deep are sandbox measurements) are the coordinator's live-run concern.
- Issue #39's findings (F1, F4-F18, F20, F19 apart from limit-2) are out of scope and untouched.
- Item 5's "device node" and "concurrent writer during snap" shapes were characterized analytically (a non-root unit cannot mknod; the
  runner snaps before any unit and compares after all exit, so no unit is a concurrent writer), not reproduced through the runner.
- No commit, stage or push; no file outside this report was written in the repository. The other agents' files
  (`src/agent_factory/decisions/`, the `tasks/briefs/laya|continuity|s0-02-support/` reports) were never touched.

## Finding inventory (no severity filter; ranked; the blocking predicate applied to each)

Predicate columns: (1) contract-mapped (R1-R3/A2'/D2 as built, or 2fd0a7d's claims for M) · (2) reproduced through the real runner ·
(3) materially effective · (4) concrete discriminator · (5) in-boundary (PC, T / M, MT). No finding meets ALL five: none is a BLOCKER.

1. VE3R1-F1 — FOLLOW-UP. SIGHUP during the S0-05 runner's `cleanup` aborts it and leaves the namespace, veth, `/etc/netns/<ns>` and
   owner record (for the pair, DNAT + route_localnet=1). VERIFIED (item 2, 4/4 deterministic; real runner). Contract mapping: NONE —
   R1 is frozen to "a second INT or TERM"; the brief's item 2 asked me to characterize HUP; PC:395-402 claims only INT/TERM and names
   SIGKILL as uncovered. Material on the PC (a closed terminal / dropped SSH during the ~2-7 s cleanup leaves egress state), but not a
   frozen-criterion breach. Reproduction: /tmp/ve3r1/drv/item2*.py. Fix: add HUP to the ignore set + a `trap ... HUP` exit-through-cleanup.
2. VE3R1-F2 — FOLLOW-UP/INFO. A hung teardown child makes the run un-interruptible by INT/TERM (child inherits SIG_IGN); cleanup's
   `ip`/`iptables` calls are not time-bounded; only SIGKILL stops it, leaving state. VERIFIED (item 4, real runner + PATH `ip` shim).
   Not contract-mapped (R1 REQUIRES the ignore + child inheritance) and not reproducible through the REAL `ip` (needs a shim). Fix
   (optional): `timeout`-wrap the teardown syscalls, or leave one escape signal.
3. VE3R1-F4 — FOLLOW-UP. M-analog of F1: SIGHUP during M's cleanup leaves the owner's model-server unit in the CELL config. VERIFIED
   (item 10, real `qwen-matrix.sh` + MT fakes). Not contract-mapped (2fd0a7d names INT/TERM, lists only SIGKILL uncovered).
4. VE3R1-F5 — FOLLOW-UP. M-analog of F2: a hung restore install is unstoppable by INT/TERM (install child inherits SIG_IGN); only
   SIGKILL, which leaves the cell unit. VERIFIED (item 10). Not contract-mapped.
5. VE3R1-F3 — FOLLOW-UP (doc). Stale test docstring: `test_a2_s0_01_tree_change_fails_the_leg` (T:2083) opens with the superseded
   "stat census of ... every v2-* directory" while the body verifies A2'. Reviewed statically. Not contract-mapped (R3 is PC-scoped),
   no material effect. Fix: one-line docstring update.
6. VE3R1-I2 — INFO. Design 2 emits `bash: warning: run_pending_traps: bad value in trap_list[15]` when a second signal is dropped
   mid-reset (item 3, minimal probe); cosmetic, may reach the operator's stderr. Harmless.
7. VE3R1-I3 — INFO. PC:407 does not check `snap`'s exit code; a failed snap is caught at compare (fail-closed), only later + wasting the
   leg's work (item 6). Defense-in-depth nicety, not a defect.
8. VE3R1-I4 — INFO. A killed test's host leftover persists only until the next create of that same namespace name, which self-heals it
   (item 7); a killed pair test's route_localnet=1/DNAT would reach the final census if no later test recreates that name. In practice
   the suite ends clean.

What I VERIFIED sound (no finding): R1 for every INT/TERM shape (item 2), the microsecond window closed by design 2 — reproduced
0/40 vs the one-line repair's 6-7/40 (item 3), R2 census against 12 shapes (item 5), D2 fail-closed against hostile baselines (item 6),
T self-heals a killed-test leftover (item 7), R3 PC text accurate (item 8), 6 new mutants on untouched lines all killed (item 9),
M's fix works for its stated claims + the MT discriminator is sound (item 10), and every gate green (item 11).

## GATE RECOMMENDATION (separately for PC/T and M/MT; the coordinator owns the final gate)

- **PC/T (the S0-05 runner + tests, PIN 97b589a): `MERGE-READY-WITH-FOLLOWUPS`.** No finding meets the complete blocking predicate.
  R1, R2 (A2'), R3 and D2 are verified sound through the real runner; the 6 new mutants are killed; the gates are green (263 passed
  twice, 204 passed/59 skipped, host clean). Real follow-ups: VE3R1-F1 (SIGHUP), VE3R1-F2 (hung-child), VE3R1-F3 (stale docstring),
  and VE3R1-I2/I3/I4. This recommendation rests only on what I reproduced; nothing ran on the PC.
- **M/MT (the Qwen matrix runner + test, PIN 0c05970): `MERGE-READY-WITH-FOLLOWUPS`.** The fix works for commit 2fd0a7d's stated
  claims (a second INT/TERM cannot abort the restore; status stays the first signal's; the restore install inherits the ignore),
  verified through the real `qwen-matrix.sh`, and the 0.3 s-vs-padded-env discriminator is sound (the pre-fix goes RED, the fix GREEN).
  `run-all.sh` passes. Real follow-ups: VE3R1-F4 (SIGHUP) and VE3R1-F5 (hung restore install), the M-analogs of F1/F2.

NOTE for the coordinator: VE3R1-F1 and VE3R1-F4 are the SAME uncovered-signal class (SIGHUP) across both runners; if the owner's live
invocation can receive SIGHUP (a terminal close / SSH drop during cleanup), widening both ignore sets to include HUP would close it in
one focused follow-up. It is a FOLLOW-UP, not a blocker, because the frozen contracts scope to INT/TERM.

## Reference anchors (full repo-relative paths; one ref per line; each token verified at its line)

- Cleanup's guard `trap '' INT TERM` is proofs/S0-05/tools/pc/run_s0_05_units.sh:383.
- The INT handler `exit 130` is proofs/S0-05/tools/pc/run_s0_05_units.sh:404.
- The TERM handler `exit 143` is proofs/S0-05/tools/pc/run_s0_05_units.sh:405.
- Cleanup's `egress_ns_destroy` owner-guarded call is proofs/S0-05/tools/pc/run_s0_05_units.sh:387.
- The census `S_IMODE` mode field is proofs/S0-05/tools/pc/run_s0_05_units.sh:232.
- The census `st.st_uid` uid field is proofs/S0-05/tools/pc/run_s0_05_units.sh:233.
- The census recursion `todo.append(rel)` is proofs/S0-05/tools/pc/run_s0_05_units.sh:261.
- The compare call `_s0_01_census compare` is proofs/S0-05/tools/pc/run_s0_05_units.sh:594.
- The D2 guard `census_failed` is proofs/S0-05/tools/pc/run_s0_05_units.sh:631.
- Limit 7's `sha256 and a symbolic link` clause is proofs/S0-05/tools/pc/run_s0_05_units.sh:57.
- The R1 slow-unit test `test_e3r1_r1_b_a_second_signal_while_cleanup_waits_for_a_slow_unit` is tests/test_s0_05_egress.py:3057.
- The four-writes test `test_e3r1_r2_each_in_place_write_fails_the_leg_by_name` is tests/test_s0_05_egress.py:3254.
- The stale docstring `takes a stat census` is tests/test_s0_05_egress.py:2083.
- The library teardown `_egress_ns_teardown` is proofs/S0-05/netns_lib.sh:346.
- The stale-owner takeover `_egress_ns_claim` is proofs/S0-05/netns_lib.sh:162.
- M's cleanup guard `trap ' + chr(39)*2 + ' INT TERM` is harness-ports/bin/qwen-matrix.sh:96.
- M's restore install `restore_args` is harness-ports/bin/qwen-matrix.sh:119.
- M's INT handler `exit 130` is harness-ports/bin/qwen-matrix.sh:146.
- MT's `signal2-matrix.py` fixture is harness-ports/tests/test_qwen_matrix_sh.sh:211.
