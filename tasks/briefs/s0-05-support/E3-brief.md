# E3 — S0-05's live-unit launch recipe (CD1 A1-A8 + D-051's relay DNAT) and the partial-state class VERIFY-E2-R1 found

PIN: 06828ea (origin head at authoring; the S0-05 boundary is byte-identical to the E2-R1 landing 6f2589d, measured below).
LANE: s0-05-e3 (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation — `isolation: "worktree"` fails on
this tree; root is needed: every namespace test runs as uid 0). Honey `ultra` Lever-2: your report is DATA — files:lines, pasted
counts, discrepancies, NOT-done. Do NOT spawn subagents.

CONTRACT SOURCES (read them whole before you design): `tasks/briefs/s0-05-support/CD1-AMENDMENT.md` (STATUS DECIDED; A1-A8, the
three probes with their pasted output, OD-1 decided as option 1) · `docs/08_DECISION_LOG.md` D-051 (the leg-scoped DNAT) ·
`tasks/briefs/s0-05-support/VERIFY-E2-R1-report.md` (F1 the blocker, F4 and F8 folded here; the rest is issue #31) · the E2 and
E2-R1 briefs in the same folder (the frozen contract E3 builds on) · `proofs/S0-01/pins.py:31-62` (the pinned paths, digests and
buzz-acp argv — the ONE source of truth for every pinned value; never retype one).

BOUNDARY (exact): MODIFY `proofs/S0-05/netns_lib.sh`, `proofs/S0-05/tools/pc/run_s0_05_units.sh`,
`proofs/S0-05/check_egress.py`, `tests/test_s0_05_egress.py`; MODIFY the committed fixtures under `proofs/S0-05/fixtures/` only as
the A7 identity record requires (say which, and why, in the report); CREATE `tasks/briefs/s0-05-support/E3-report.md` (write it
incrementally from the start). Read anything. Do NOT modify `proofs/S0-05/spec.json`, `proofs/S0-05/run_canaries.sh`, the
canaries, anything under `proofs/S0-01/`, `scripts/`, `.github/`, `.claude/`, `sandbox-kit/`, any hook, or `pyproject.toml`
(a line you cannot meet without one of them is a DISCREPANCY, never a silent edit). Two other sandbox agents run in this tree on
disjoint files (`src/agent_factory/decisions/ledger.py`, `tests/test_decisions_ledger.py`, `tasks/briefs/laya/`,
`scripts/verify_command.py`, `tests/test_verify_command.py`, `tasks/briefs/canny/`): never touch, run or revert them. Never run
`git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push` here. No outward-facing action of any kind.
No PC or bridge use: every live PC step is the coordinator's after your landing. Every namespace, veth, nat rule, sysctl, claim,
`/etc/netns` entry and process you create is destroyed by NAME or PID from your own record, never by `pkill -f`; the census below
must read empty at the end (pasted). The sandbox has about 2 GB free.

CODE INTEL FIRST: `graft ask` before any grep for code questions; `scripts/lane_context.sh -q '<question>' -s egress_ns_create -s
_egress_ns_teardown -s cleanup -o /tmp/e3/pack.md proofs/S0-05/netns_lib.sh proofs/S0-05/tools/pc/run_s0_05_units.sh
proofs/S0-05/check_egress.py` gives you the quartet pack in one call.

This is defensive testing of the owner's own containment boundary (S0-05, "no direct egress"): the egress canaries, the
namespace gate and the negative controls are the proof's instruments on the owner's own machines.

## Why

S0-05 is one of the two proofs still ABSENT (10 of 12 PRESENT). Its live leg cannot run until the runner launches the real units
the right way. CD1 (the coordinator's contract defect, returned by VERIFY-E2) showed the E2 rows launched S0-01's capture tool,
which would re-own S0-01's tree as root and die at its probe; CD1 A1-A8 is the decided recipe. The buzz-acp pair cannot reach the
relay on `127.0.0.1:3999` from a namespace; D-051 (owner, 2026-09-23) decided a leg-scoped DNAT. And VERIFY-E2-R1 returned E2-R1
NOT-READY on one blocker whose class this lane closes: a create that fails after its first mutation leaves its namespace, veth,
`/etc/netns` entry, claim and owner record behind, and the runner never reaps them (reproduced by the coordinator below).

## The contract (coordinator, decided; do not re-litigate — a line you cannot meet is a DISCREPANCY with its measurement, never a silent change)

The E2 and E2-R1 contracts stand except where this brief amends them. Refusal texts below are exact.

**Part X — the library and the runner's own correctness (VERIFY-E2-R1; do these first and checkpoint them in the report).**

- **X1 (F1, AF-AP-129).** `egress_ns_create`'s up-front validation bounds the port's DIGIT COUNT before any arithmetic: a port is
  `^[1-9][0-9]{0,4}$` and at most 65535. `10.9.9.9:99999999999999999999`, `10.9.9.9:9223372036854775808`, `10.9.9.9:65536`,
  `10.9.9.9:0` and `10.9.9.9:00080` each return 64 with the existing contract line `egress: allow entry must be <ip>:<port>,
  got '<entry>'` and create NOTHING (census). Sweep the rest of your boundary for any other `[ "$x" -op N ]` on a value from input
  (AF-AP-129's row) and list the result.
- **X2 (the partial-state class).** A create that fails at ANY step after its first mutation (the claim, the namespace, the veth,
  an address, a link, `/etc/netns`, a gate rule) rolls back everything it made — namespace, veth, `/etc/netns/<ns>`, claim and
  owner record — then returns its failure code with the failing step's message on stderr. And the runner puts the name into its
  reap set BEFORE it calls create, so a leftover that create could not roll back is still reaped by `cleanup` under the ownership
  check (E2-R1's F3 rule: only a namespace whose owner record is this runner's pid). Prove it with fault injection at two steps
  (one early, e.g. the veth; one late, e.g. a gate rule) and paste the census after each.
- **X3 (F4, the stale-claim takeover).** The takeover of a claim whose owner pid is dead is atomic: of two concurrent creators
  that both find the same stale claim, exactly one proceeds; the other refuses `namespace-live: <ns> owned by pid <winner>` (65)
  and creates nothing; the owner record names the winner. Decide the mechanism (for example an atomic `mv` of the stale claim to
  a unique tombstone, then the normal `mkdir` claim); state-guards, not a lock held across destroy-and-recreate.
- **X4 (F8).** A test drives the runner's REAL `cleanup` (not a copy of its logic): a namespace owned by this runner is destroyed
  at exit; one whose owner record names another live pid is left untouched; mutant M14 (the owner check dropped) dies by name.

**Test-seam rule for X2-X4 and everything below:** no test hook in production code — no environment variable, flag or file the
library or runner reads only for tests. Inject faults from the test side: a `PATH` shim (an `iptables` or `ip` wrapper that fails
on one exact argv, then execs the real binary), a bash function defined after sourcing the library, a paused child. Where a
production input must differ in a test (the pinned paths below), it goes through the runner's RECORDED override (A1).

**Part A — CD1's launch recipe (the amendment's text is the contract; these lines add only what it left to E3).**

- **A1** exactly as CD1 says, with the pinned values read from `proofs/S0-01/pins.py` at run time (one source of truth). The
  runner's refusal is `not-run|unit identity mismatch: <path>`; a test fails on any row naming `proofs/S0-01/tools`, `.markers`
  or `.secrets`. THE RECORDED OVERRIDE: the sandbox cannot hold the PC's pinned binaries, so tests replace a unit with a stand-in
  ONLY through one runner input (you name it) whose use is written into `units.json` for that unit (`"override": {…}` naming what
  was replaced); `check_egress.py` then REFUSES a bundle with any override for a live (pc-venue) claim
  (`units-manifest-invalid: <unit> override present`). A stand-in run can therefore never pass as the live leg — test that
  refusal on a real runner output.
- **A2** as CD1 says (a per-unit scratch tree under the evidence root, owned by the unit's user, its own `HOME` and
  `HERMES_HOME`; the before/after `stat` census of `/home/rocco/s0-01-pinned/.markers` and every `v2-*` directory, the leg failing
  with `s0-01-tree-changed: <path>` and a non-zero exit when anything changed). The census paths come from `pins.py`'s pinned base,
  not a literal; a missing tree on the venue is recorded, not failed.
- **A3** as CD1 says: stdin a pipe the runner holds open for the canary window, stdout+stderr a pipe into the unit log; never
  `/dev/null`, never a regular file; the stop is closing stdin, namespace destroy the backstop. (Today's line 118 feeds
  `</dev/null` and a regular file — exactly the crash CD1's probe 2 measured.)
- **A4** as CD1 says, with the unit user resolved once at the top: an operator input you name, default the owner uid:gid of the
  pinned agent realpath; a resolved uid 0 is `not-run|unit would run as root`.
- **A5** as CD1 says: the unit's environment is built from nothing (no inherited variables) — `PATH`, `HOME`, `HERMES_HOME`,
  locale — and a test asserts no key name matching `pins.REDACTED_ENV_KEY_RE` except the pair's own identity key reaches a unit.
- **A6** as CD1 says, the row read from `pins.PINNED_LAUNCH_ARGV`'s shape with three substitutions only: `--relay-url
  ws://<egress_ns_host_ip ns>:3999` (the DNAT address), `--agent-command <PINNED_AGENT_REALPATH>` (the agent itself, not S0-01's
  tee) and the S0-05 identity. The identity is an operator input (a file path) the runner reads without printing: absent →
  `not-run|identity file refused: absent`; group/other bits set → `not-run|identity file refused: mode <octal>`; not owned by the
  unit user → `not-run|identity file refused: owner uid <n>`; no `BUZZ_PRIVATE_KEY=` line → `not-run|identity file refused:
  shape`. Never S0-01's `.secrets/agent.env` (a test refuses that path by name). The value reaches only the pair's environment.
- **A7** as CD1 says, plus the evidence side: the runner writes `<unit>/unit-identity.json` (pid, `/proc/<pid>/exe` realpath, the
  entrypoint realpath and sha256, `Uid` from `/proc/<pid>/status`, the argv) and runs the canaries only if it matches the pins
  (else `not-run|unit identity not observed: <detail>`); `check_egress.py` requires that file for every `run` unit whose bundle
  says venue pc and refuses `unit-identity-invalid: <unit> <detail>` on a missing file, a digest or path that is not the pin, or
  uid 0. The synthetic-pass fixture gains the record it now needs; a negative fixture (uid 0) is committed beside it.
- **A8** as CD1 says: every allow entry is formed by the runner from `egress_ns_host_ip` and a port input (OmniRoute `20128`,
  the relay `3999` for the pair); no operator-typed address.

**Part D — D-051, the relay reach for the pair (only for the buzz-acp unit, only for its leg).** Before the pair's preflight the
root runner adds ONE host rule `iptables -t nat -A PREROUTING -i <egress_ns_host_if ns> -p tcp -d <egress_ns_host_ip ns> --dport
3999 -j DNAT --to-destination 127.0.0.1:3999` and sets `net.ipv4.conf.<egress_ns_host_if ns>.route_localnet=1`; it removes the
rule explicitly in the leg's teardown AND in `cleanup` (a nat rule naming a deleted interface outlives it), and the census reads no
PREROUTING rule naming that interface afterwards. A failure to add either is `not-run|relay reach not established: <detail>`. No
service is touched, restarted or rebound. The pair's allow-set is exactly {relay `<host_ip>:3999`, OmniRoute `<host_ip>:20128`}.
The live preflight (C0 to both) is the coordinator's on the PC; in the sandbox, prove the DNAT path with a listener on the host's
`127.0.0.1:3999` reached from inside the namespace through `<host_ip>:3999`, and the negative control (the rule absent → C0
fails with the existing `positive control unreachable` reason).

**Declared limits** (in the runner header and the report): the canaries prove the namespace, not the unit's own sockets (kept);
the DNAT makes the one veth interface route to loopback for the leg; an operator who supplies a wrong identity file only fails the
pair's C0/relay handshake; the unit-identity record is unkeyed (it binds identity to the pins, not against a forger with root).

## Tests (`tests/test_s0_05_egress.py`; root-gated where they need namespaces, with the existing `NEEDS_NETNS` pattern)

Every refusal above is asserted with its exact text through the REAL runner or library, each written RED first against the PIN
bytes (paste the RED run — the failures must be the PIN's behaviour this brief measured, not an import error), then GREEN. The
existing 137 tests stay; an existing assertion may only become stricter, never weaker or deleted; a changed expectation names its
contract item in a comment. At least: the X1 port list; X2 at two fault points with the census; X3's two-creator race on a stale
claim (deterministic: pause the loser between its read and its takeover from the test side); X4's two cleanup cases; A1's
identity mismatch, the S0-01-path refusal and the override refusal by the checker; A2's census failure; A3's stdin-EOF stop of a
stand-in that crashes on `/dev/null` stdin (as the real adapter does, per probe 2); A4's root refusal and the `Uid` record; A5's
clean environment; A6's four identity-file refusals; A7's `unit-identity.json` and the checker's three refusals; A8's derived
entries; D's DNAT positive path, its removal (census), and its negative control.

## Mutants (scratch-copy restore only — never a git restore in this shared tree; each mutant compiles (`bash -n` / `py_compile`) and collects, AF-AP-78)

At least: M14 (the cleanup owner check dropped — VERIFY-E2-R1's survivor) · E1 X1's digit bound removed · E2 create's rollback
removed · E3 the runner's early reap-set entry removed · E4 the stale takeover back to read-then-write · E5 the checker's override
refusal removed · E6 the A7 uid check removed (runner) and E7 (checker) · E8 the DNAT teardown removed · E9 `route_localnet` left
set · E10 the unit env inherited · E11 stdin back to `/dev/null`. One row each: mutant · compiles · collected · killed-by (test
id) / SURVIVED / EQUIVALENT with the reason.

## Gates (paste verbatim, each with its invocation)

`mkdir -p /tmp/e3/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider
--basetemp=/tmp/e3/bt` twice as root (`rm -rf /tmp/e3/bt` after each) · the same file once as `nobody` (the non-root venue; the
namespace tests skip, everything else passes): `rm -rf /tmp/e3nr && mkdir -p /tmp/e3nr && chmod 1777 /tmp/e3nr && setpriv
--reuid=65534 --regid=65534 --clear-groups env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest
tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3nr/bt` · `bash -n` on the two shell files · `shellcheck` if
present (say if absent) · `/root/venv-agent-factory/bin/python -m pyflakes proofs/S0-05/check_egress.py tests/test_s0_05_egress.py`
· `python3 scripts/ap_screen.py proofs/S0-05/check_egress.py` and `python3 scripts/ap_screen.py --tests tests/test_s0_05_egress.py`
· `python3 scripts/no_laya_in_gates.py` · the census, pasted: `ip netns list`, `ip -o link show type veth`, `iptables -t nat -S
PREROUTING`, `ls /etc/netns`, the owner dir, and no stand-in or listener pid of yours alive.

## Report (`tasks/briefs/s0-05-support/E3-report.md`)

PREMISE re-measured (item 1 of your work: re-run the premise commands below on the PIN and stop CONTRACT-INVALID on a mismatch
that changes the contract) · Part X checkpoint · what changed per item (file:line refs) · RED then GREEN (pasted) · the mutant
table · gates (pasted) · the live-leg operator recipe the coordinator will run on the PC (every input, the expected `units.json`,
what each named refusal means) · DISCREPANCIES · NOT-done (first-class: nothing here ran on the PC). Lint floor: `python3
scripts/report_lint.py --min-refs 15 --map L=proofs/S0-05/netns_lib.sh --map PC=proofs/S0-05/tools/pc/run_s0_05_units.sh --map
C=proofs/S0-05/check_egress.py --map T=tests/test_s0_05_egress.py tasks/briefs/s0-05-support/E3-report.md --root .`; apply its
`fix:` hints for at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 05:0xZ, sandbox as root @ 06828ea)

```
$ git diff --stat 6f2589d HEAD -- proofs/S0-05 tests/test_s0_05_egress.py
(empty = byte-identical to 6f2589d)
$ sha256[:16] + lines
234bb13ac0e475c6 320 proofs/S0-05/netns_lib.sh
4d3b917c6fd8c973 177 proofs/S0-05/tools/pc/run_s0_05_units.sh
5d9c502e862d0507 380 proofs/S0-05/check_egress.py
44b1428b431303a1 139 proofs/S0-05/run_canaries.sh
ed6edbd1c408ad83 43 proofs/S0-05/spec.json
d93b1b32d075f684 1507 tests/test_s0_05_egress.py
$ git log --format='%h %s' -3 -- proofs/S0-05/netns_lib.sh proofs/S0-05/tools/pc/run_s0_05_units.sh    (no later repair)
6f2589d S0-05 E2-R1 landed (GATED-PENDING-VERIFY): VERIFY-E2's seven blockers closed in the netns library, the unit runn
9223162 E2 landed (GATED-PENDING-VERIFY): S0-05's live-leg prerequisites (issue #13) + two coordinator touches with red/
24e80e6 S0-05: the canary suite, the selective-netns library, the collector, the checker, three REAL namespace bundles a
$ grep -n (the line map, netns_lib.sh)
54:egress_ns_resolver()   200:egress_ns_run()   247:EGRESS_OWNER_DIR=${EGRESS_OWNER_DIR:-/run/s0-05-egress}
248:egress_ns_owner_file()   258:_egress_ns_teardown()   314:egress_ns_destroy()
77:    if ! [[ "$port" =~ ^[1-9][0-9]*$ ]] || [ "$port" -gt 65535 ]; then          (the AF-AP-129 guard)
$ run_s0_05_units.sh at the PIN (read): LAUNCH rows :52 and :54 = "/usr/bin/python3 $S0_01_TOOLS/pc_launch.py --leg run-1
  --model s0-01-pong" (CD1's defect); the create-failure path :93-97 records not-run and continues WITHOUT adding the name to
  NS_LIVE; cleanup :74-80 reaps only NS_LIVE names whose owner record is $$; the launch :118 is `</dev/null` into a regular file
$ proofs/S0-01/pins.py (the values E3 reads, never retypes)
31:PINNED_BUZZ_ACP_EXE_REALPATH = "/home/rocco/s0-01-pinned/buzz/target/release/buzz-acp"
32:PINNED_BUZZ_ACP_SHA256 = "a5a17ffc0c7ef878648a506b9d5066120b91984d1158a60e6ce9664a39f88064"
33:PINNED_AGENT_REALPATH = "/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp"
34:PINNED_AGENT_ENTRYPOINT_SHA256 = "f90a0cc333fa86d99495c7c984e4e11a1b83a7e3dc92883b7fd295ae70358ef1"
38:PINNED_RELAY_URL = "ws://127.0.0.1:3999"
52:PINNED_IDLE_TIMEOUT_ARG = "900"
53:PINNED_MAX_TURN_DURATION_ARG = "3600"
55:PINNED_LAUNCH_ARGV = [ PINNED_BUZZ_ACP_EXE_REALPATH, "--relay-url", PINNED_RELAY_URL, "--agent-command", PINNED_TEE_PATH,
    "--agent-args", "", "--idle-timeout", PINNED_IDLE_TIMEOUT_ARG, "--max-turn-duration", PINNED_MAX_TURN_DURATION_ARG ]
$ bash -c '[ 99999999999999999999 -gt 65535 ]; echo "rc=$?"'
bash: line 1: [: 99999999999999999999: integer expression expected
rc=2
$ the partial-state class, reproduced as root (EGRESS_OWNER_DIR under the scratchpad; everything destroyed after):
  . proofs/S0-05/netns_lib.sh; egress_ns_create e3-premise-a 10.9.9.9:99999999999999999999
capable: ok
proofs/S0-05/netns_lib.sh: line 77: [: 99999999999999999999: integer expression expected
iptables v1.8.10 (nf_tables): invalid port/service `99999999999999999999' specified
Try `iptables -h' or 'iptables --help' for more information.
create rc=1
--- census after the refused create
netns: 1
veth host if ehec0fd5cf: 1
/etc/netns/e3-premise-a: present
claim dir: present
owner file: present (13635)
destroy rc=0
--- census after destroy
netns: 0 veth: 0 etc: absent claim: absent
$ VERIFY-E2-R1's gates on the same bytes (its report, 2026-09-23 04:4xZ): root `137 passed in 60.86s`; non-root `122 passed,
  15 skipped in 3.99s`; M14 (cleanup owner check dropped) SURVIVED; F4 the stale takeover raced under a pause injection
```

The owner file above names pid 13635, the probe's own dead subshell: the refused create also left a STALE claim, the exact shape
X3's takeover must handle.
