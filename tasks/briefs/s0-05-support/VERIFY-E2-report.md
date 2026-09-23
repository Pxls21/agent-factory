# VERIFY-E2 — adversarial verify of S0-05's live-leg prerequisites (E2 at `9223162` + the two coordinator touches)

Verifier: sandbox `adversarial-verifier`, root, 2026-09-23 01:51Z–02:50Z. PIN `9223162`; tree HEAD at the end `52c02ee`
(the boundary is byte-identical, IDENTITY below). READ-ONLY on the tree: every mutant, fixture and hostile input lived
in the session scratchpad `ve2/` (a `git archive 9223162` copy, restored from a pristine copy after every mutant). The
only tree write is this file. Evidence levels: **reproduced** (run here, output pasted), **read** (source read at the
PIN), **inferred** (reasoned, not run). Confidence: SOLID / UNSURE on every claim.

## OUTCOME

**NOT-READY.** Seven findings meet the whole blocking predicate. Each is reproduced here through the production path at
the PIN and has a deterministic red control. **F3**: the runner's exit cleanup destroys a live sibling's namespace, so
F23 is not closed (two real runners; the sibling's C6 canary is killed mid-flight). **F2**: F23 is check-then-act; the
owner record is written last, so a sibling create inside a window of about 0.15 s destroys and recreates a namespace
whose recorded owner is live, and both creates return 0. **F4**: a double quote in create's stderr corrupts
`units.json` (a regression against the push base). **F11**: F19 is not a dotted-quad check (`1.2.3:80` is accepted,
`010.0.0.1:80` installs an ACCEPT for `8.0.0.1`), the refusal comes after the DROP policies are written, and a refused
runner leg leaves its namespace behind. **F12**: the three F19 tests fail as non-root, so the CI `tests` job is red
(`3 failed, 110 passed, 9 skipped` against the push base's `101 passed, 5 skipped`). **F14**: the runner live test never
asserts that the stand-in ran, so the AF-AP-80 pairing required by E2 item 5 is hollow (M16 and the brief's own m9
survive; the lane's m9 row was a compound mutant). **F1**: a unit that ignores or outlasts SIGTERM survives
`egress_ns_destroy` silently and every census reads clean. One **CONTRACT-DEFECT** is returned for an amendment, not
repaired: **CD1**, the real S0-01 launcher named in both LAUNCH rows deletes S0-01's `v2-run-1` framedir, recreates it
owned by root, and then dies at a host-loopback probe that cannot succeed inside the namespace. On the PC the live leg
as designed would damage S0-01's pinned tree and could never record a `run` unit. What holds (SOLID): the F6 refusal
(any host interface, nothing new left behind), the F23 named refusal for a sibling that starts after the owner's record
exists, F9 at the PIN, F10, F11 (exact-match venue), F18's three spellings, the F3+F17 `DROP_BEFORE` path, and both
touches (no top-level `local`; only `resolv.conf` in `/etc/netns/<ns>/`; zero `Bind` lines in a live runner run). The
recommendation does not depend on anything unreproduced. F1's production reach is UNVERIFIED (it depends on how
buzz-acp and Hermes handle SIGTERM); that does not change the recommendation.

## IDENTITY

Measured first (01:51Z), then again at the end (HEAD `52c02ee`). Both match the brief's table (SOLID, reproduced):

```
$ git diff --stat 9223162 HEAD -- proofs/S0-05 tests/test_s0_05_egress.py        (HEAD fba2f41, then 52c02ee)
(empty both times)
$ sha256[:16] + lines, at the PIN (git show) and in the working tree
324ffdd9aa646531 258 proofs/S0-05/netns_lib.sh           (PIN = WT)
44b1428b431303a1 139 proofs/S0-05/run_canaries.sh        (PIN = WT)
24087a298ab1b9f9 159 proofs/S0-05/tools/pc/run_s0_05_units.sh   (PIN = WT)
5d9c502e862d0507 380 proofs/S0-05/check_egress.py        (PIN = WT)
ce86f3a2d9bb81c9 1243 tests/test_s0_05_egress.py        (PIN = WT)
```

The scratch tree (`git archive 9223162` of `proofs/S0-05`, `proofs/schemas`, `proofs/S0-01/tools/pc`, the test file,
`tests/conftest.py`, `pyproject.toml`) carries the same five digests. It was restored to them after the last mutant.

## ITEMS

### Item 1 — F7 under a process that ignores SIGTERM

Reproduced (02:02:24Z, the real library). The unit shape is the runner's own: `egress_ns_run <ns> setsid bash -c "trap '' TERM; sleep 300"`.

```
ip netns pids ve2-item1 = [17033 ]
  pid 17033 comm=sleep SigIgn=0000000000004000 netns=net:[4026532262]
named netns inode (before delete) = 4026532262
destroy rc=0 elapsed=5.34s stderr-free
CENSUS netns=[] veth=[] owner_dir=[] etc_netns=[]
  SURVIVOR pid 17033 comm=sleep netns=net:[4026532262] links=[lo ] policy=[-P OUTPUT DROP]
        NS NPROCS   PID COMMAND
4026532262      1 17033 sleep 300
next create of the same name rc=0  new named inode=4026532314
```

The same class through the exact consumer (02:04:00Z): the real runner with a test-local stand-in unit that ignores
SIGTERM (the E2 test's own modelling):

```
runner pid=18737  owner record=[18737]  standin pid=[18820] standin netns=net:[4026532262] named=4026532262
runner rc=0
CENSUS netns=[] veth=[] owner_dir=[] etc_netns=[]
STAND-IN SURVIVED pid=18820 netns=net:[4026532262] links=[lo ]
units.json hermes-acp row: [{'unit': 'hermes-acp', 'status': 'run', 'note': 'contained live unit'}]
PASS: S0-05 no-direct-egress - 1 units, 11 canaries failed as required, positive controls 1/1
```

Answers. The destroy takes 5.34 s and then deletes regardless. The survivor stays in an anonymous namespace (only `lo`,
policy DROP), so it cannot egress. The C0–C6 evidence stays sound (the canaries ran before the destroy; the checker
passed). The survivor holds no F6/F23 state for the next run (the next create returned 0 with a new inode; the record
and the veth were gone). I killed both survivors by pid (17033, 18820) and the census read clean.

**F1 — BLOCKER — F7's postcondition fails for a unit that ignores or outlasts SIGTERM.** Reproduced, SOLID.
`L:241` `kill "$pid"` sends SIGTERM only. The bounded wait at `L:244` `remaining=50` ends silently on budget, and
`L:254` `ip link del "$host_if"` / `L:255` `ip netns del "$ns"` then run regardless. `egress_ns_destroy` returns 0 with
no message, while a process is still in the deleted namespace and every census (netns, veth, owner dir, `/etc/netns`)
reads clean. That is exactly VERIFY-E1 F7's symptom, back for this class. Mutant M11 (the wait loop removed) also
survives the suite, because `T:1044` `time.sleep(0.5)` checks after a pause and its sleeper exits at once on SIGTERM.
The property "no process at the moment destroy returns" is untested (D-M11: the PIN leaves a 1-s slow-exit process gone
at return; M11 leaves it ALIVE at return).
- Expected (E2 item 3): "waits … bounded, failure-aware … after it returns, no process is left in that network namespace".
  Observed: rc 0, no message, a live process in `net:[4026532262]`.
- Predicate: contract-mapped (E2 item 3, verbatim) · canonical (the real library; the real runner with a stand-in unit,
  as the E2 test models units) · material (the claimed state, "a stopped unit leaves nothing running", is false and
  invisible; the unit outlives its runner) · discriminator (a stand-in that ignores SIGTERM; checked at return) · in
  boundary (L). Production reach UNVERIFIED: whether buzz-acp or Hermes outlast SIGTERM by more than 5 s is not measurable
  here, and today the real launcher cannot start inside a namespace at all (CD1).
- Cheapest red control: `egress_ns_run <ns> setsid bash -c "trap '' TERM; sleep 300" &`, then `egress_ns_destroy <ns>`,
  then assert that no pid read before the delete is alive at return.
- Fix: after the budget, `kill -KILL` each survivor, re-check, and fail loud (stderr names the survivors, non-zero
  return) if any remain.

### Item 2 — F23's liveness signal

**(a)** Reproduced (02:05:22Z). A record naming a live, unrelated `sleep` of mine, and no namespace at all:

```
unrelated live sleep pid=19991 (mine)
named netns present: 0
namespace-live: ve2-item2 owned by pid 19991
create rc=65
  retry 1 rc=65   retry 2 rc=65   retry 3 rc=65
== recovery: egress_ns_destroy by hand, then create
destroy rc=0 record present: no
create rc=0 record=[19988] self=19988
```

**(d)** Reproduced (same run). The record deleted by hand while the namespace lives and holds a process:

```
live process in ve2-item2: pid=20217 (mine)
record removed by hand
sibling create rc=0 sibling pid=20222
  after the sibling: pid 20217 alive=no; record=[20222]
```

**(c)** Reproduced (02:04:00Z, the live runner). `PC:86` `create_err` runs create in a command
substitution, and the record read during the run is `[18737]`, the runner's own pid. A later create by the same shell
while the record exists passes: D-M22 at the PIN gives `second create rc=0`.

**(b)** Reproduced. Library level, 12 simultaneous trials (02:05:51Z): every trial, both creators passed the F23 check.
One lost at `ip netns add` with rc 1 and `Cannot create namespace file "/run/netns/ve2-race": File exists`, never the
named `namespace-live`. An offset sweep (02:40:32Z) finds every bad outcome inside about 0.15 s:

```
offset 0.00s: A rc=0 || B rc=1 err=[Cannot create namespace file "/run/netns/ve2-race2": File exists|]
offset 0.04s: A rc=1 err=[Cannot find device "ehb3ac40e5"|] || B rc=0        (B's destroy-first deleted A's veth)
offset 0.08s: A rc=1 err=[Terminated|] || B rc=0                             (B's destroy-first killed A's in-flight command)
offset 0.13s: A pid=31065 rc=0 || B pid=31121 rc=0 || netns=1 owner=[31121]  (both succeed; B replaced A's namespace)
offset 0.16s: A rc=0 || B rc=65 err=[namespace-live: ve2-race2 owned by pid 31247|]
```

A deterministic control (02:44:50Z). B pauses 1 s at the first command of its destroy-first, after its F23 check has
passed. A (unmodified) finishes and records itself meanwhile:

```
B resumes destroy-first: record=[3212] recorded owner alive=yes
A pid=3212 rc=0 record-at-A-return=[3212]  || B pid=3224 rc=0
final record=[3224]
```

With a pause in A before its record write instead (02:41:50Z), both return 0, the record names A on a namespace B
built, and the OUTPUT chain holds 4 ACCEPT rules where the pinned set has 2 (`rules=4`).

Two real runners released from one barrier (02:07:09Z, 5 trials): the loser's `units.json` is invalid JSON in 5/5 (F4).
The both-return-0 outcome was not observed at runner level (NOT-done).

**F2 — BLOCKER — F23 is check-then-act: the owner record is written last.** Reproduced, SOLID. The record check
at `L:77` `egress_ns_owner_file` runs before `L:87` `egress_ns_destroy "$ns"`, but the claim is written only at `L:114`
`EGRESS_OWNER_DIR` (after `L:99` `ip netns add` and the veth steps). A sibling whose check falls inside that window
passes it, and its destroy-first then deletes a namespace whose recorded owner is live (`record=[3212] recorded owner
alive=yes`) or kills the owner's in-flight command (`Terminated`). Both creates can return 0.
- Expected (E2 item 2): "refuses to destroy-and-recreate a namespace whose recorded owner is a LIVE process other than
  itself … the sibling's namespace, veth and processes untouched". Observed: destroyed and recreated; both rc 0.
- Predicate: contract-mapped (item 2) · canonical (the production create from two shells, as `T:978` `test_live_sibling_namespace_is_refused`
  models a sibling; the natural window reproduced at a 0.13 s offset with no injection) · material (two runs believe
  they own one namespace, the rule set is duplicated, the recorded owner can be wrong) · discriminator (the pause control
  above) · in boundary (L).
- Fix: claim first. Write the record atomically before `L:87` `egress_ns_destroy` (for example `set -o noclobber` or a `mkdir` claim); on
  an existing claim, refuse if its pid is live and not `$$`, otherwise take it over; then destroy-first.

**F3 — BLOCKER — the runner's exit cleanup destroys a live sibling's namespace (F23 not closed).** Reproduced, SOLID.
`PC:92` `NS_LIVE="$NS_LIVE $ns"` is never pruned when the loop itself runs `egress_ns_destroy` (`PC:102`, `PC:125`, `PC:134`).
`PC:73` `cleanup() { for ns in $NS_LIVE; do egress_ns_destroy "$ns"; done; }` runs at exit
with no ownership check. A sibling that took the name after the leg ended is destroyed.
Deterministic (02:08:24Z, a library-level sibling as in `T:978` `test_live_sibling_namespace_is_refused`):

```
02:09:01 A reached buzz-acp; netns now=[s0-05-buzz-acp (id: 0) ]
02:09:02 sibling pid=28576 sibling create rc=0 owner record=[28576] sibling proc in ns=28658
02:09:37 runner A exited rc=0
AFTER A's exit: sibling pid 28576 alive=yes; netns list=[]; owner record=[cat: …: No such file or directory]; sibling proc 28658 alive=no
```

Two real runners (02:10:12Z). B (`hermes-acp`) starts 3 s after A (`hermes-acp buzz-acp`) moves to `buzz-acp`. A's
checker passes at 02:11:25.02, A exits, and its cleanup kills B's C6 canary mid-flight (B's last record is C5 at
02:11:22.93):

```
runner A rc=0
runner B rc=1
B units.json: {"unit": "hermes-acp", "status": "run", "note": "contained live unit"}
B checker: canary-missing: hermes-acp C6 / exit 1 per contract
B stderr: Terminated
B bundle files: [canaries.jsonl gate.json runtime.json ]
```

- Expected (E2 item 2): the runner "never destroys a namespace it did not create"; the sibling is untouched (VERIFY-E1
  F23: "two concurrent PC-runner invocations tear down each other's namespaces"). Observed: A destroys B's namespace,
  kills its processes and its record, and corrupts B's evidence.
- Predicate: contract-mapped (item 2; VERIFY-E1 F23) · canonical (two real runners) · material (a sibling's evidence
  corrupted; its `units.json` still says `run`) · discriminator (the deterministic run above) · in boundary (PC).
- Fix: drop a name from `NS_LIVE` at every in-loop destroy, and have `cleanup` destroy a name only while its record
  still reads `$$`. The repair's test is a runner-level two-invocation test, which also kills M20 and M21 (F17).

**F4 — BLOCKER — `units.json` becomes invalid JSON when create's stderr carries a double quote (a regression).**
Reproduced, SOLID. `PC:86` `create_err` captures every stderr line of create, `PC:88` `RESULT` stores it, and `PC:147` `printf`
writes it into a JSON string unescaped. Deterministic, with no race (a stray quote in the operator's value):

```
$ ALLOWED_HERMES='10.201.107.1:20128"' run_s0_05_units.sh … hermes-acp          (PIN)
    {"unit": "hermes-acp", "status": "not-run", "reason": "egress: allow entry must be <ip>:<port>, got '10.201.107.1:20128"'"},
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 3 column 125 (char 139)
evidence-invalid: units.json Expecting ',' delimiter: line 3 column 125 (char 139)
$ the same input through the push base 25896e4's runner
    {"unit": "hermes-acp", "status": "not-run", "reason": "namespace creation failed"},
units.json VALID
```

The natural trigger is F2's race. The losing runner records `"reason": "Cannot create namespace file
"/run/netns/s0-05-hermes-acp": File exists"` (5/5 trials). Effect: one unit's refusal text makes the whole evidence
root unreadable, including any other unit's valid bundle.
- Predicate: contract-mapped (E2 item 2, "records a refused unit as `not-run` with the refusal text as its reason"; item
  10, the evidence format unchanged) · canonical (the real runner) · material (the evidence manifest is corrupted, and
  the checker's verdict turns into `evidence-invalid`) · discriminator (the quoted-value run) · in boundary (PC).
- Fix: build `units.json` with `json.dumps` (the runner already calls python for the checker), or escape the reason.

**F5 — FOLLOW-UP — a recycled or unrelated live pid in a record refuses a name forever, even with no namespace, and the
recovery is undocumented.** Reproduced, SOLID. The check at `L:81` `kill -0 "$owner_pid"` has no identity beyond the
pid number, and it does not ask whether the namespace exists. The only recovery is `egress_ns_destroy <ns>` by hand;
no runbook, header or refusal text says so (`namespace-live` appears only in briefs, the library, the test and the
ledger). The trigger needs a runner killed without its exit trap and then pid reuse, so it is rare. Fix: record the
pid's start time (`/proc/<pid>/stat` field 22) beside it; refuse only if the namespace exists; name the recovery in the
refusal text.

**F6 — INFO — the record is the only liveness signal.** Reproduced (2(d) above). Deleting it by hand makes a live
namespace stale, and a sibling's destroy-first kills its process. This conforms to the contract ("no owner file = stale").
On the PC, `/run` is a tmpfs, so the records and `/run/netns` reset together at reboot (inferred). In this sandbox,
`/run` is on the root ext4 (measured: `findmnt /run` shows no mount). `ip netns pids <ns>` could corroborate liveness.

### Item 3 — F6's reach

Reproduced (02:17:02Z). `dummy` links are not supported by this kernel (`Error: Unknown device type.`), so a `bridge`
stood in as the non-veth interface. The first attempt with `dummy` lost its output to the disk-full event (02:13Z) and
was re-run.

```
== 3(a) a 10.201.107.x address on a non-veth host interface
address-plan-collision: s0-05-hermes-acp 10.201.107.0/24 on ve2br0
create rc=65
   left behind: netns=0 veth=0 etc_netns=no owner=no
== 3(a') the same /24 as a /32 on a DOWN link
address-plan-collision: s0-05-hermes-acp 10.201.107.0/24 on ve2br0
create rc=65
== 3(a'') a SUPERNET covering the /24 (10.201.0.1/16) on the host
create rc=0
200  <- positive control from the unit ns rc=0
== 3(b) the /24 held only INSIDE another namespace
create rc=0
== 3(d) a stale same-name namespace (dead owner) holding a process, plus a collision
stale ns process pid=1924 (mine)
address-plan-collision: s0-05-hermes-acp 10.201.107.0/24 on ve2br1
create rc=65
   after the refusal: stale process 1924 alive=no netns=0 veth=0 etc_netns=no owner=no
```

**F7 — INFO — F6 holds as contracted.** Reproduced, SOLID. `L:94` `index($4, pfx) == 1` refuses any host interface in
the /24 (bridge, `/32`, a down link) and leaves nothing new behind. Two edges are harmless. A covering supernet is not
refused, but the more specific /24 wins and the positive control still returns 200. A /24 held only inside another
namespace is missed by design; it is another routing domain, and through the library it is reachable only by removing a
host address by hand. 3(d): the refusal at `L:96` `address-plan-collision` comes after `L:87` `egress_ns_destroy`, so a
stale same-name namespace (and its process) is already cleaned when the create is refused. That matches the F23
stale-cleanup rule, and nothing of the new namespace is left.

**F8 — INFO — the octet table.** Reproduced. The names in use (`PC:52`/`PC:54` `LAUNCH` rows, `PC:63` `ABSENT` rows,
the test names):

```
s0-05-ai-memory            2      s0-05-s0-01-backend        153
s0-05-memory-adapter       63     s0-05-harness-router       191
s0-05-hermes-acp           107    s0-05-pandaprobe           203
s0-05-u7                   107    s0-05-dream-foundry        216
                                  s0-05-buzz-acp             219
random s0-05-e2-<uuid8> hitting {107,219}: 165/20000 = 0.0083 (2/254 = 0.0079)
```

The only shared octet is the deliberate test collider `s0-05-u7`. `n % 254 + 1` over one hash byte makes octets 1 and 2
twice as likely as any other (`0x00`/`0xfe` map to 1, `0x01`/`0xff` to 2).

### Item 4 — the second exit-3 path (`DROP_AFTER`)

Reproduced (02:17:50Z): the real collector on a real namespace deleted after C0 was recorded, then the real checker.

```
collector rc=3 stderr=[Cannot open network namespace "ve2-item4": No such file or directory| … |run_canaries: cannot read the OUTPUT DROP counter of ve2-item4|]
on disk: [canaries.jsonl ] records=2 canaries=[C0 C1]
evidence-missing: curl gate.json absent at item4-ev/curl/gate.json
exit 1 per contract
checker rc=1
```

**F9 — FOLLOW-UP — the `DROP_AFTER` exit leaves `canaries.jsonl` behind.** Reproduced, SOLID. `R:114` `DROP_AFTER` /
`R:115` `DROP_AFTER` exit 3 after the canaries wrote records, with no `gate.json` or `runtime.json`. The checker refuses
the bundle by name (`evidence-missing`, rc 1): not a pass, not a traceback, fail-closed. Two notes. The contract
sentence "an exit-3 collection leaves no `canaries.jsonl`" overreaches its own m4 rationale, which relies on this path
writing records; the implementation meets the operative instruction (`R:79` `mkdir -p "$OUT"` / `R:80` `JSONL` after
`R:75` `DROP_BEFORE`). The checker's rc 1 labels an instrument failure as a violation. The realistic trigger is F3 (a
sibling deleting the namespace mid-collection). Fix: on the `DROP_AFTER` exit, remove or mark the partial file, or have
the checker classify a bundle without `gate.json` as a broken instrument.

**F10 — FOLLOW-UP — the runner ignores the collector's exit status.** Reproduced (F3's run: B recorded `run` after its
collection was cut). `PC:129` `run_canaries.sh` is followed at `PC:130` by `RESULT[$unit]="run|contained live unit"`
whatever it returned (3 or 64). The pattern predates E2. Fix: record `not-run` with the collector's rc and stderr.

### Item 5 — F19's class

Reproduced (02:18:10Z) through `_egress_apply_gate`, entered exactly as `T:1237` `ip netns add` then
`_egress_apply_gate` (the test's own entry point):

```
1..2:80          rc=1   msg=[iptables v1.8.10 (nf_tables): host/network `1..2' not found|…]      OUTPUT-accepts-written=[]
....:80          rc=1   msg=[iptables v1.8.10 (nf_tables): host/network `....' not found|…]      OUTPUT-accepts-written=[]
999.1.1.1:80     rc=1   msg=[iptables v1.8.10 (nf_tables): host/network `999.1.1.1' not found|…] OUTPUT-accepts-written=[]
1.2.3:80         rc=0   msg=[]                                                                    OUTPUT-accepts-written=[-A OUTPUT -d 1.2.3.0/32 ]
01.2.3.4:80      rc=0   msg=[]                                                                    OUTPUT-accepts-written=[-A OUTPUT -d 1.2.3.4/32 ]
1.2.3.4.5:80     rc=1   msg=[iptables v1.8.10 (nf_tables): host/network `1.2.3.4.5' not found|…] OUTPUT-accepts-written=[]
010.0.0.1:80     rc=0   msg=[]                                                                    OUTPUT-accepts-written=[-A OUTPUT -d 8.0.0.1/32 ]
0x0a.0.0.1:80    rc=64  msg=[egress: allow entry must be <ip>:<port>, got '0x0a.0.0.1:80']       OUTPUT-accepts-written=[]
10.0.0.1/8:443   rc=64  msg=[egress: allow entry must be <ip>:<port>, got '10.0.0.1/8:443']      OUTPUT-accepts-written=[]
--- a two-entry list, the bad entry second:
egress: allow entry must be <ip>:<port>, got 'host.example:443'
rc=64
-P INPUT DROP|-P FORWARD DROP|-P OUTPUT DROP|-A INPUT -s 10.0.0.1/32 -p tcp -m tcp --sport 80 -j ACCEPT|-A OUTPUT -d 10.0.0.1/32 -p tcp -m tcp --dport 80 -j ACCEPT|
```

Through the real runner (a refused entry, the runner then exits):

```
ALLOWED_HERMES=10.0.0.1/8:443 runner rc=1 reason=["egress: allow entry must be <ip>:<port>, got '10.0.0.1/8:443'"]
CENSUS netns=[s0-05-hermes-acp (id: 0) ] veth=[eh6a87fce7@if538 ] owner_dir=[s0-05-hermes-acp.owner ] etc_netns=[s0-05-hermes-acp ]
   rules left in the namespace: -P INPUT DROP|-P FORWARD DROP|-P OUTPUT DROP|
```

The CI view (01:59:12Z; an unprivileged uid, the condition of the CI `tests` job, `stage0-ci.yml` `python -m pytest tests/ -q`):

```
>           assert result.returncode == 64, (result.returncode, result.stderr, result.stdout)
E           AssertionError: (1, 'mount --make-shared /run/netns failed: Operation not permitted
E             Cannot open network namespace "s0-05-e2-735fc759": No such file or directory
FAILED tests/test_s0_05_egress.py::test_allow_entry_must_be_ipv4_literal[cidr]
FAILED tests/test_s0_05_egress.py::test_allow_entry_must_be_ipv4_literal[hostname]
FAILED tests/test_s0_05_egress.py::test_allow_entry_must_be_ipv4_literal[empty-host]
3 failed, 110 passed, 9 skipped in 4.41s
```

**F11 — BLOCKER — F19 is not the contracted check.** Reproduced, SOLID. Four problems.
- (i) `L:136` `*[!0-9.]*|*/*|""` tests characters, not a dotted-quad shape. Four non-quads reach iptables and fail rc 1
  instead of the named rc 64. `1.2.3:80` is ACCEPTED (rc 0, an ACCEPT for `1.2.3.0/32`; glibc's resolver reads the same
  literal as `1.2.0.3`). Leading zeros are accepted and iptables reads them as octal: `010.0.0.1:80` installs an ACCEPT
  for `8.0.0.1`, an address the operator never declared.
- (ii) The check sits inside the entry loop, after `L:127` `iptables -P "$chain" DROP` has written the three policies and
  after earlier entries' ACCEPT rules (`L:138` `iptables -A OUTPUT`). "Before any rule is written" is false, and the
  checker's own pinned set counts the `-P` lines as rules.
- (iii) Through the runner, the refusal lands after `L:99` `ip netns add`, the veth and the `L:114` `EGRESS_OWNER_DIR`
  record exist, and the failed create never enters `NS_LIVE`. The runner exits leaving the namespace, the veth (holding
  the /24), the record and `/etc/netns/<ns>`. This leak is pre-existing for a bad port (the push base leaks too; its
  create path is the same). E2's new refusals now land on it too, for example a CIDR, which the library accepted before
  (VERIFY-E1 F19 measured that).
- (iv) Downstream is fail-closed. With no route off the /24, no egress results; the preflight fails; the checker refuses
  (`gate-manifest-invalid` for `1.2.3`, `egress-rules-unpinned` for `010.…`). So the safety impact is nil; the claimed
  output and state are wrong.
- Predicate: contract-mapped (E2 item 9: "refuses an entry whose host part is not a dotted-quad IPv4 literal … return
  64, before any rule is written") · canonical (the production function; the real runner) · material (rc 0 or 1 where
  the contract says 64, an undeclared ACCEPT, a leaked namespace after the run) · discriminator (the table above) · in
  boundary (L, PC).
- Fix: validate every entry before `egress_ns_create` touches anything, against a strict dotted quad (each octet
  `0|[1-9][0-9]?|1[0-9][0-9]|2[0-4][0-9]|25[0-5]`, no leading zeros) and a port of 1–65535. That also fixes F12.

**F12 — BLOCKER — the three F19 tests fail as non-root, so the CI `tests` job is red.** Reproduced, SOLID.
`T:1231` `def test_allow_entry_must_be_ipv4_literal` carries no `NEEDS_NETNS` mark. `T:1237` `ip netns add` fails as non-root,
and `_egress_apply_gate` returns 1 at its first `ip netns exec` (`L:127` `iptables -P "$chain" DROP`) before the F19
check. At the push base `25896e4` the same unprivileged run reads `101 passed, 5 skipped in 3.94s` (rc 0), so the three
reds are new. This breaks the file's own invariant (`T:19`: namespace tests "SKIP with a declared reason, never fail").
Corroborated: the coordinator's CI-repair commit `5f6919b` names these three failures from CI run 917 and routes them
into E2's one repair, rejecting a skip. Predicate: contract-mapped (the file's invariant; the E2 test list's "the whole
existing file stays green"; CI green) · canonical (the real test file under the CI uid class) · material (integration:
every push red) · discriminator (the unprivileged run) · in boundary (T, L). Fix: F11's up-front validation needs no
root, so the test drops its `ip netns add` and runs everywhere.

### Item 6 — F11 and F18 edges

Reproduced (the real collector and checker; the committed `evidence-mechanism-sandbox` fixture read-only):

```
R venue=PC           rc=64  first=[run_canaries: venue must be sandbox or pc, got 'PC']
R venue=pc\          rc=64  first=[run_canaries: venue must be sandbox or pc, got 'pc ']
R venue=$'sandbox\n' rc=64  first=[run_canaries: venue must be sandbox or pc, got 'sandbox]
R venue=sandbox      rc=3   first=[run_canaries: cannot read the OUTPUT DROP counter of ve2-no-such-ns]
(no evidence directory created by the three refusals)
C --units=\ curl     rc=1   first=[unit-missing:  curl]
C --units=curl\,     rc=64  first=[usage: --units carries an empty unit name]
C --units=\,         rc=64  first=[usage: --units carries an empty unit name]
C --units=\          rc=1   first=[unit-missing:  ]
C --units=curl\,\    rc=1   first=[unit-missing:  ]
C --units omitted rc=0 first=[PASS: S0-05 no-direct-egress - 1 units, 11 canaries failed as required, positive controls 1/1]
C --units (no value) rc=2 first=[check_egress.py: error: argument --units: expected one argument]
C (no args) rc=2 last=[check_egress.py: error: the following arguments are required: evidence_root]
```

**F13 — FOLLOW-UP — the F18 and usage-code edges.** Reproduced, SOLID. `R:32` `case "$VENUE"` is exact-match and
refuses by name before any write (SOLID, holds). `C:362` `if any(not part for part in parts)` refuses the three
contracted spellings. Whitespace-only names (`' '`, `'curl, '`) and a padded `' curl'` pass into later code and fail
closed as `unit-missing` (rc 1), not as the usage refusal. Argparse's own usage errors exit 2, the deferral code, while
`C:49` now reads "64 + usage error"; that is true only for the F18 check (argparse behaviour predates E2). Fix: strip
and refuse blank names; override `parser.error` to exit 64.

### Item 7 — F8 on the real tool, and the AF-AP-80 pairing

Read and reproduced. `proofs/S0-01/tools/pc/pc_launch.py:1` `#!/usr/bin/env python3`. In this sandbox `env python3`
resolves to `/usr/local/bin/python3`, which links to `/usr/bin/python3.11`, the same binary as `/usr/bin/python3`
(through `/etc/alternatives`). On the PC it selects the first `python3` on root's `PATH` (NOT measured; no bridge use).
The row at `PC:52` `LAUNCH` pins `/usr/bin/python3` explicitly, so the shebang is never consulted at launch.
`T:1169` `S0_01_TOOLS` resolves the target to the REAL file (`PROOF.parent / "S0-01"`), and `T:1177` `shebang` compares
`"python" in shebang` (a substring pin). The paired behavioral control is hollow:

```
M16 (the launch line handed to bash, never run as given)    122 passed in 16.11s   (the baseline takes 51 s)
D-M16: standins launched=0 hermes row=[('not-run', 'launch exited within the settle window; …')]
       launch.log=[/usr/bin/python3: /usr/bin/python3: cannot execute binary file ]
M17 (= the brief's m9 exactly: the stop becomes a kill of the launch pid alone; cleanup kept)   122 passed in 51.42s
D-M17 [pin.orig] during the buzz-acp leg: hermes-acp stand-in pid 25170 alive=no
D-M17 [mt/M17]   during the buzz-acp leg: hermes-acp stand-in pid 26421 alive=yes
```

**F14 — BLOCKER — the runner live test never asserts that the stand-in ran, so the AF-AP-80 pairing E2 item 5 requires
is hollow, and the brief's m9 survives.** Reproduced, SOLID. `T:1066-1151` `test_runner_live_leg` checks the stand-in's ABSENCE after the
run (`T:1129` `standin_procs.returncode != 0`), the namespace census and the F10 row (`T:1138` `backend_row`), all true
when the unit never launched. Nothing checks that the hermes-acp row is `run` (`T:1136` `units_json` is read for the
backend row only) or that the stand-in ever executed. M16 (`PC:111` `setsid` handed to bash) survives with a 16 s suite.
The brief's m9 as specified (M17: stop by `kill "$launch_pid"` alone) survives, because the `PC:73` `cleanup` masks it at
exit, although the unit stays alive through the next unit's leg. The lane's m9 row ("runner stops by kill + skip NS_LIVE
cleanup") was a compound mutant, and its DISCREPANCIES says "None". The required mutation evidence is false for m9.
- Predicate: contract-mapped (E2 item 5: "paired with the runner-level live test below, which launches a row as given
  and asserts the stand-in actually ran (AF-AP-80)"; the frozen mutant list m9) · canonical (the real test file and
  runner) · material (a regression of F8's run-as-given or F9's stop-through-the-namespace ships green; the report's
  9/9 is false) · discriminator (M16, M17) · in boundary (T).
- Fix: in `T:1066` `test_runner_live_leg`, assert the hermes-acp row is run, have the stand-in write its pid and its `ns/net` inode, and
  assert that inode equals the unit namespace's. Run two units and assert the first unit's stand-in is dead when the
  second unit's header prints. That kills M16 and M17.

**CD1 — CONTRACT-DEFECT (returned for an explicit amendment; not repaired, not a gate on E2's own items) — the real
S0-01 launcher in both LAUNCH rows damages S0-01's pinned tree and cannot start inside a unit namespace.** Reproduced,
SOLID for the mechanism; the PC-side effect is inferred. Through the real runner and the real launcher (the default
`S0_01_TOOLS`), with the launcher's own validated seam `S0_01_HERMES_HOME` pointing at a scratch base owned by uid
65534 (standing in for `rocco`) with a sentinel in its framedir (02:36:27Z):

```
before: nobody …/rocco/s0-01-pinned/.markers/v2-run-1 [SENTINEL-prior-capture.txt ]
runner rc=1
after:  root …/rocco/s0-01-pinned/.markers/v2-run-1 [hermes-config.sha256 hermes-model.txt mentions upstream-records ]
launch.log: … leg=run-1 framedir=…/.markers/v2-run-1 model line: default: s0-01-scripted/s0-01-pong pc_launch: backend /healthz probe failed (URLError: <urlopen error [Errno 111] Connection refused>); run pc_backend_restart.sh first
hermes row: [('not-run', 'launch exited within the settle window; see …/hermes-acp.launch.log')]
```

Mechanism: `PC:52` / `PC:54` `LAUNCH` rows both run `pc_launch.py --leg run-1`.
`proofs/S0-01/tools/pc/pc_launch.py:308` `shutil.rmtree(FD, ignore_errors=True)` deletes `<BASE>/.markers/v2-run-1`, the
directory `collect_leg.sh` packs S0-01's leg evidence from, and recreates it as the runner's uid (root on the PC). Then
`proofs/S0-01/tools/pc/pc_launch.py:328` `urlopen("http://127.0.0.1:20201/healthz")` runs inside the unit namespace,
whose loopback is its own, and fails. So on the PC (sudo, the base `/home/rocco/s0-01-pinned`), a default run would
delete S0-01's `v2-run-1` capture (both rows reset the same directory), leave it root-owned (so a later rocco-run S0-01 launch cannot clean
it; inferred), and record both units `not-run`; the checker then reads `unit-missing`. It also breaks the launcher's
own seam rule: `proofs/S0-01/tools/pc/pc_launch.py:222` `no other proof` ("ever writes into S0-01's pinned tree"). This
predates E2 (the row arguments are unchanged), and VERIFY-E1 Item 9 judged the units launchable. The owner's PC run
needs an amendment first: a `--profile` for an S0-05 leg with its own Hermes home (the launcher's sanctioned seam), and
a decision on how a contained unit reaches the backend its launcher probes.

### Item 8 — the coordinator touches

**(a)** Reproduced. A function-scope scan (a brace-depth scan with heredocs skipped) of PC, R and L found
`top-level local/return hits = 0` in all three. Its seeded control (the lane's `local create_err` restored in a scratch
copy) is flagged as `L86: local create_err`. L's 14 in-function `local` lines are not flagged.

**(b)** Reproduced, only inside a scratch `EGRESS_OWNER_DIR`, with the link aimed at a scratch file:

```
== (i) symlink planted BEFORE create, target content not a pid
create rc=0
   victim now=[VICTIM-ORIGINAL]  record type=regular file content=[3601] self=3601
== (ii) symlink planted in the window AFTER destroy-first, BEFORE the record write
create rc=0
   victim now=[3601]  record type=symbolic link
   after destroy: link present=no victim=[3601]
== default-dir mode as created by root (umask 0022): 755 root
```

**(c)** Reproduced (the live runner run of Item 1): `/etc/netns/s0-05-hermes-acp contents: [resolv.conf ]`, and
`stderr lines: Bind=0 local=0 total=0`. Only `L:113` `mkdir -p "/etc/netns/$ns"` and the `resolv.conf` write touch
that directory.

**F15 — INFO — touch 1 is clean.** Reproduced, SOLID (8(a)).

**F16 — INFO — touch 2 is clean in production; a symlink window exists but only root can use it.** Reproduced, SOLID.
The `L:114` `printf … > "$(egress_ns_owner_file "$ns")"` write follows a symlink planted between destroy-first and the
write (8(b)(ii)). A link planted earlier is removed by `L:257` `rm -f` in destroy-first. The default directory is root
`0755`, so only root can plant a link, and no privilege boundary is crossed on either venue. Two notes.
`L:230` `EGRESS_OWNER_DIR` is read from the environment, an ambient config channel; a `sudo -E` with a user-writable directory
would turn the window into a root write through a link. Namespace names are never validated before `rm -rf
"/etc/netns/$ns"` (pre-existing; the runner only passes fixed names).

### Item 9 — new mutants

See the MUTATION TABLE. **F17 — FOLLOW-UP — four non-equivalent survivors on correct code.** Reproduced, SOLID.
- M10: `L:94` `index($4, pfx) == 1` changed to `> 0`. D-M10: a host holding `110.201.107.5/24` gives PIN rc 0 and M10
  rc 65, a false collision. There is no prefix-anchoring control.
- M20: the runner destroys the namespace after a create refusal. D-M20: the PIN leaves the sibling intact, M20 destroys
  it. The PIN's runner-level F23 path is correct, and this was its first run: reason `namespace-live: s0-05-hermes-acp
  owned by pid 24657`, sibling namespace and process intact.
- M21: `PC:88` `RESULT` reason made a constant. Non-equivalent by construction (the reason string differs).
- M22: the `!= "$$"` clause of `L:81` `owner_pid` dropped. D-M22: a same-shell re-create gives PIN rc 0 and M22 rc 65.
- M11, M16 and M17 also survive; they are facets of F1 and F14. M12 is EQUIVALENT on the record domain the library
  writes (a positive `$$`, checked as root); it differs only for hand-edited records such as `self`, `0` or `-1`.
- Fix: the F3 repair's two-runner test covers M20 and M21. Add a `110.201.<octet>.x` negative control (M10) and a
  same-shell re-create (M22).

### Item 10 — the builder's report against the PIN

**F18 — FOLLOW-UP — `E2-report.md` makes claims the PIN does not support.** Read, SOLID.
- Stale design: its row for L 75–84 says `owner_file="/etc/netns/$ns/owner"`, and its row for L 114 writes
  `/etc/netns/$ns/owner`. At the PIN, `L:77` reads `egress_ns_owner_file` and `L:114` writes into `EGRESS_OWNER_DIR`
  (touch 2).
- Line counts: L "209 -> 251" is 258 at the PIN; PC "150 -> 160" is 159 (touch 1 removed a line); T "899 -> 1237" is
  1243 (touch assertions).
- Ranges moved:
  - F7's "L 229–244" is now the `L:236` `egress_ns_destroy` body (through line 257).
  - PC "86–92" is now PC 85–91; "PC 112" is `PC:111` `setsid`; "PC 133–135" is PC 132–134.
  - T "1066–1136" is now T 1066–1151; "1148–1176" is T 1154–1181; "1179–1193" is T 1184–1197; "1197–1210" is
    T 1200–1215; "1215–1221" is T 1218–1225; "1225–1237" is T 1228–1243.
- Substance: the m9 row is a compound mutant (F14). The DISCREPANCIES "None" omits it. Its `T:1066` `test_runner_live_leg` row presents a
  library-level concurrency check as the runner-level one.
- Note: `report_lint` scores this report "OK 32" because it matches tokens, not meaning. A range that still contains
  the token passes even when its claim is false (F21).

### Item 11 — out of scope: touchpoints only

- VERIFY-E1 F2 (gate-fired is not attributed to any canary): F2 and F3's shared or replaced namespace would let two
  runs' canaries advance one DROP counter, and the checker cannot tell.
- VERIFY-E1 F12 (the allow-list pinned to itself): `C:157` `join(octets)` keeps leading zeros verbatim, so F11's octal case fails
  closed as `egress-rules-unpinned`, which is exactly F12's self-pin at work.
- Nothing bears on F4, F5, F13-F16, F20-F22, F24 or the seed wording.

### Other observations

**F19 — INFO — the new tests share fixed resources.** Read. `T:992` `/tmp/e2_sibling.err` and `T:1107` `e2_runner_sibling` write fixed paths
in the shared `/tmp`, not `tmp_path`; both files remain there after every run. T:909 and T:1066 share the name
`s0-05-hermes-acp` and port 18080, and their teardowns (`T:971`, `T:1149`, each `egress_ns_destroy`) remove that fixed name unconditionally. Run
as root beside a live leg, they would destroy the live run's namespace. xdist is absent in this sandbox
(`ModuleNotFoundError: No module named 'xdist'`), so no parallel root venue exists today.

**F20 — UNVERIFIED — a signal to the runner does not stop it.** Read only. `PC:74` `trap cleanup EXIT INT TERM` runs
`cleanup` on INT or TERM and then returns. Bash resumes the loop, so Ctrl-C aborts the current unit and moves on to the
next one. Pre-existing; not run.

**F21 — INFO — `report_lint` is token-level.** Reproduced (F18): a semantically false range with a matching token lints OK.

## MUTATION TABLE

Driver `ve2/exp/mutdrv.py`. For each mutant: a fresh copy of the pristine PIN tree, an exact single-occurrence
replacement (anchor count 1 asserted), `bash -n` / `py_compile`, a collect count, and the whole file in ONE run. The
tree was restored to the PIN digests afterwards (pasted in IDENTITY). No mutant was INVALID.

| mutant | site | compiles | collected | result | killed-by / differential |
|---|---|---|---|---|---|
| M10 | `L:94` `index($4, pfx) == 1` → `> 0` | rc 0 | 122 | SURVIVED (non-equivalent) | D-M10: host `110.201.107.5/24` → PIN rc 0, M10 rc 65 |
| M11 | `L:244` `remaining` wait loop (L:243-253) removed | rc 0 | 122 | SURVIVED (non-equivalent) | D-M11: 1-s slow exit → PIN gone at return (1.11 s); M11 ALIVE at return (0.04 s) |
| M12 | `L:81` `kill -0 "$owner_pid"` → `[ -d /proc/$owner_pid ]` | rc 0 | 122 | SURVIVED — EQUIVALENT | same on the record domain (a positive `$$`, root); differs only for `self`/`0`/`-1` |
| M13 | `C:362` `parts` → `if not parts[0]` | rc 0 | 122 | KILLED | `test_empty_unit_name_rejected[interior-empty]` |
| M14 | `R:33` `sandbox` case widened with `""` | rc 0 | 122 | KILLED | `test_venue_required_and_validated[missing]` |
| M15 | `L:231` `egress_ns_owner_file` → `/etc/netns/<ns>/owner` | rc 0 | 122 | KILLED | `test_runner_live_leg` at `T:1123` `Bind /etc/netns/` (the touch-2 control) + `test_live_sibling_namespace_is_refused` at `T:1002` `owner_pid` (a hard-coded path) |
| M16 | `PC:111` `setsid` + `bash` | rc 0 | 122 | SURVIVED (non-equivalent) | suite 16.11 s; the stand-in never launched (`cannot execute binary file`) |
| M17 | `PC:134` `egress_ns_destroy` → `kill "$launch_pid"` (the brief's m9 exactly) | rc 0 | 122 | SURVIVED (non-equivalent) | D-M17: stand-in alive during the next unit's leg (PIN: dead) |
| M20 | `PC:88` `RESULT` path + `egress_ns_destroy "$ns"` | rc 0 | 122 | SURVIVED (non-equivalent) | D-M20: sibling namespace destroyed, process killed (PIN: intact) |
| M21 | `PC:88` `RESULT` reason → constant | rc 0 | 122 | SURVIVED (non-equivalent by construction) | the `units.json` reason changes; no test reads it |
| M22 | `L:81` `owner_pid` `!= "$$"` clause dropped | rc 0 | 122 | SURVIVED (non-equivalent) | D-M22: same-shell re-create → PIN rc 0, M22 rc 65 |

Pasted driver rows (02:21:36Z–02:28:24Z):

```
M13 | proofs/S0-05/check_egress.py | compiles rc=0 | collected: 122 tests collected in 0.18s | KILLED | 1 failed, 121 passed in 51.22s | 51s
M14 | proofs/S0-05/run_canaries.sh | compiles rc=0 | collected: 122 tests collected in 0.19s | KILLED | 1 failed, 121 passed in 51.45s | 52s
M15 | proofs/S0-05/netns_lib.sh | compiles rc=0 | collected: 122 tests collected in 0.20s | KILLED | 2 failed, 120 passed in 50.99s | 51s
M12 | proofs/S0-05/netns_lib.sh | compiles rc=0 | collected: 122 tests collected in 0.17s | SURVIVED | 122 passed in 54.09s | 54s
M10 | proofs/S0-05/netns_lib.sh | compiles rc=0 | collected: 122 tests collected in 0.17s | SURVIVED | 122 passed in 51.05s | 51s
M11 | proofs/S0-05/netns_lib.sh | compiles rc=0 | collected: 122 tests collected in 0.19s | SURVIVED | 122 passed in 51.25s | 52s
M16 | proofs/S0-05/tools/pc/run_s0_05_units.sh | compiles rc=0 | collected: 122 tests collected in 0.20s | SURVIVED | 122 passed in 16.11s | 16s
M17 | proofs/S0-05/tools/pc/run_s0_05_units.sh | compiles rc=0 | collected: 122 tests collected in 0.18s | SURVIVED | 122 passed in 51.42s | 52s
M20 | proofs/S0-05/tools/pc/run_s0_05_units.sh | compiles rc=0 | collected: 122 tests collected in 0.18s | SURVIVED | 122 passed in 51.36s | 52s
M21 | proofs/S0-05/tools/pc/run_s0_05_units.sh | compiles rc=0 | collected: 122 tests collected in 0.18s | SURVIVED | 122 passed in 51.49s | 52s
M22 | proofs/S0-05/netns_lib.sh | compiles rc=0 | collected: 122 tests collected in 0.19s | SURVIVED | 122 passed in 51.59s | 52s
```

The M15 kill assertions (a targeted run of the two tests): `tests/test_s0_05_egress.py:1002: AssertionError` (`'self=27584' == 'self='`) and
`AssertionError: Bind /etc/netns/s0-05-hermes-acp/owner -> /etc/owner failed: No such file or directory` (the touch-2 control).

## GATES

Every count below is pasted from the run that produced it.

```
$ python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=<scratch>/bt/g1        (real tree, root, 02:42:34Z)
122 passed in 51.57s
rc=0
$ python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=<scratch>/bt/base0     (scratch PIN tree, root, 01:58:14Z)
122 passed in 51.33s
rc=0
$ setpriv --reuid=65534 --regid=65534 --clear-groups env HOME=/tmp/ve2nr python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/ve2nr/bt1   (real tree, 01:59:12Z)
3 failed, 110 passed, 9 skipped in 4.41s
rc=1
$ (the same, on git archive 25896e4 = the E2 push base)
101 passed, 5 skipped in 3.94s
rc=0
$ bash -n proofs/S0-05/netns_lib.sh proofs/S0-05/run_canaries.sh proofs/S0-05/tools/pc/run_s0_05_units.sh
rc=0
$ python -m pyflakes proofs/S0-05/check_egress.py tests/test_s0_05_egress.py
rc=0
```

Not re-run (already measured in the premise; no finding depends on them): `no_laya_in_gates.py`, `ap_screen.py`.
The report lint on this file is pasted in NOT-done after its last round.

## FOLLOW-UPS (non-blocking; one line each, for D-034)

- F5: bind the owner record to the pid's start time and to the namespace's existence; name the recovery (`egress_ns_destroy <ns>`) in the `namespace-live` text.
- F6: corroborate liveness with `ip netns pids <ns>` when the record is missing (the contract calls a missing record stale).
- F9: remove or mark the partial `canaries.jsonl` on the `DROP_AFTER` exit (R:115), or classify a `gate.json`-less bundle as a broken instrument.
- F10: the runner records `not-run` with the collector's rc and stderr when `run_canaries.sh` exits non-zero (PC:129).
- F13: refuse whitespace-only unit names; make argparse usage errors exit 64, not the deferral code 2.
- F16: pin `EGRESS_OWNER_DIR` (or check that it is root-owned and not group- or world-writable) before writing; validate namespace names before `rm -rf`.
- F17: controls for M10 (a `110.201.<octet>.x` address) and M22 (a same-shell re-create); M20 and M21 come with F3's repair test.
- F18: correct `E2-report.md`'s stale rows (the `/etc/netns` owner record, line counts, ranges, the m9 row).
- F19: tests write into `tmp_path` and use per-test namespace names and free ports; teardown destroys only what the test created.
- F20: the runner's INT/TERM trap should exit after `cleanup` (measure first).
- F21: `report_lint` cannot see a semantically stale range; a verify lane re-derives cited ranges from primary source.
- F8: consider a hash-to-octet map without the double weight on octets 1 and 2 (INFO only).

## CENSUS

After the last live run (02:44:50Z) and again before writing this report:

```
$ ip netns list
$ ip -o link show type veth
$ ls /run/s0-05-egress
(all three empty; /etc/netns empty; no listener, sleep or stand-in process of mine alive — swept by `ps`)
```

`/run/s0-05-egress` itself pre-existed my session (created 01:44Z by earlier runs); I created nothing in it that
remains. Every process I started was killed by its recorded pid; none was killed by name. `/tmp` stayed `1777`
throughout (checked after the unprivileged run). I created `/tmp/ve2nr` (my own; nobody-owned, `0700`) for the
unprivileged gate. The fixed `/tmp/e2_sibling.err` and `/tmp/e2_runner_sibling.err` belong to the tests (F19), not to me.

## NOT-done (first-class)

- No PC runs. The bridge was not used; the lane's carve-out allows only pytest gates there, and none was needed. CD1's
  PC-side effects (the root-owned `/home/rocco/s0-01-pinned/.markers/v2-run-1`, the lost capture) are inferred from the
  mechanism reproduced here.
- The actual GitHub CI run for `9223162` was not queried (no `gh` CLI; MCP avoided per the standing rule). F12 rests on
  the unprivileged reproduction, corroborated by the coordinator's reading of CI run 917 (`5f6919b`).
- F1's production reach is not measured (how buzz-acp and Hermes behave on SIGTERM).
- F2 at runner level: the loser's rc 1 outcome was seen with two real runners (5/5), but the both-return-0 outcome only
  at library level (natural at a 0.13 s offset; deterministic with a pause).
- m1–m8 were not re-run (the lane's rows). m9 was re-run exactly as the brief specifies (M17).
- `shellcheck` is absent here (as the premise says).
- The kernel lacks `dummy` links, so a `bridge` stood in for Item 3(a). One Item-3 attempt was lost to the disk-full
  event of 02:1xZ (the coordinator's own AF-AP-126); it was re-run in full.
- Report lint on this file, the brief's exact command (`--min-refs 15`, maps L/R/PC/C/T), three rounds:
  round 1: 118 refs — OK 81, NEAR 2, MISS 34, UNCHECKABLE 1 (refs split from their tokens across line breaks, and
  the builder's stale numbers quoted as live refs); round 2: 102 refs — OK 101, MISS 1; round 3 (final):
  report_lint: 101 refs — OK 101, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
