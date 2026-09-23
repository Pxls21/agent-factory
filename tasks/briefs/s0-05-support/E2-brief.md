# E2 — S0-05 live-leg prerequisites: the namespace library, the collector and the PC runner made safe to run (issue #13)

PIN: the origin head that carries this brief (read it with `git log -1 --format=%h origin/claude/soundbox-kit-migration-iz1jwf`;
since 5762efe the only changes are this brief's commit and the transcripts-sync commit after it).
ROLE: a SANDBOX build lane (`code-implementer`), run as root in the sandbox because every namespace test needs uid 0 and the PC
lane user is uid 1000 (`netns_lib.sh:57`). You work in the SHARED tree `/home/user/agent-factory` (no worktree). You do NOT commit,
push, stage (`git add`), stash, checkout, restore or reset anything; you do NOT open PRs or comment anywhere; you do NOT spawn
subagents; you do NOT touch the PC bridge. Leave every change uncommitted and end with the report.

BOUNDARY (exact; nothing else):
- MODIFY `proofs/S0-05/netns_lib.sh` (L), `proofs/S0-05/run_canaries.sh` (R), `proofs/S0-05/tools/pc/run_s0_05_units.sh` (PC),
  `proofs/S0-05/check_egress.py` (C, a listed gate file: `scripts/gate_files.txt:35`), `tests/test_s0_05_egress.py` (T).
- CREATE `tasks/briefs/s0-05-support/E2-report.md` (write it INCREMENTALLY, one section at a time, from the start).
- READ anything. Do NOT edit `proofs/S0-05/spec.json`, any committed fixture under `proofs/S0-05/fixtures/`, the canaries, any
  S0-01 file, or any other path. Report an adjacent defect; never fix it.

## Why

VERIFY-E1 (issue #13, `tasks/briefs/s0-05-support/VERIFY-E1-report.md`) named five findings that must be closed before the owner
runs `run_s0_05_units.sh` as root on the PC: F6, F8, F9, F10, F23. The live legs are the only step between S0-05 and a mint
(S0-05 is ABSENT in `proofs/ledger.json`; 10 of 12 proofs are PRESENT). Every finding reproduces on this tree (premise block).
Four small guards in the same files ride along: F3, F7, F11, F17, F18, F19. The checker hardening rows (F2, F4, F5, F12, F13, F14),
the report corrections (F15, F16), F20-F22 and F24 are NOT in scope. The seed's wording question for S0-05's second assertion
(containment property versus a routed variant) is the owner's and is NOT in scope; nothing here depends on it.

## The contract (coordinator, decided; do not re-litigate)

1. **F6, address-plan collision.** `egress_ns_create` refuses when the /24 its name derives (`10.201.<octet>.0/24`) is already
   assigned to ANY host interface after its own destroy-first step: message `address-plan-collision: <ns> 10.201.<octet>.0/24 on
   <if>` on stderr, return 65, and NOTHING of the new namespace is left behind (no netns, no veth, no `/etc/netns/<ns>`).
   Rejected alternative: a wider hash alone (it lowers the odds and still passes a collision silently).
2. **F23, a live sibling run.** `egress_ns_create` records its owner (the creating shell's `$$`) in `/etc/netns/<ns>/owner`. It
   refuses to destroy-and-recreate a namespace whose recorded owner is a LIVE process other than itself: message `namespace-live:
   <ns> owned by pid <p>`, return 65, the sibling's namespace, veth and processes untouched. A namespace whose recorded owner is dead
   (or that has no owner file) is stale: destroy-first cleans it as today. The runner records a refused unit as `not-run` with the
   refusal text as its reason and never destroys a namespace it did not create. Rejected alternatives: a per-invocation nonce in the
   namespace name (the derived /24 would change per run, so the operator could not set a unit's allowed address before the run);
   `flock` (a state guard on the owner's liveness is the project rule for destroy-and-recreate).
3. **F7 + F9, a stopped unit leaves nothing running.** `egress_ns_destroy` kills every process in the namespace (`ip netns pids`),
   waits for them with a bounded, failure-aware wait, and only then deletes the veth, the netns and `/etc/netns/<ns>`; after it
   returns, no process is left in that network namespace (prove it from `/proc/<pid>/ns/net` inodes read BEFORE the delete). The
   runner stops a unit through the namespace, never by `kill "$launch_pid"` (that pid is the bash wrapper; the unit survives it —
   premise F9). Its settle-window liveness check may keep the wrapper pid.
4. **F10, the S0-01 scripted backend is not a contained unit.** It is the model-provider stand-in on OmniRoute's upstream side (the
   sanctioned stub in CLAUDE.md), not a `docs/05_SECURITY.md` §6 source, and OmniRoute must reach it on host loopback. Remove it
   from `ALLOWED`/`LAUNCH` and from the default unit list; `units.json` lists it as `not-run` with the reason `not a docs/05 §6
   source: the S0-01 scripted backend is the model-provider stand-in behind OmniRoute`.
5. **F8, the interpreter lives in the unit row.** Each `LAUNCH` row carries its full argv including the interpreter
   (`/usr/bin/python3 "$S0_01_TOOLS/pc_launch.py" …`); the launch line runs the row as given. A test asserts every row's interpreter
   agrees with its target script's shebang, so a bash script can never again be handed to python3. That static test is paired
   with the runner-level live test below, which launches a row as given and asserts the stand-in actually ran (AF-AP-80).
6. **F3 + F17, an unreadable counter writes nothing.** `run_canaries.sh` creates `<unit>/canaries.jsonl` only AFTER the
   `DROP_BEFORE` guard; an exit-3 collection leaves no `canaries.jsonl`. The test asserts exit 3, the message AND the absent file:
   with the `DROP_BEFORE` guard removed (mutant m4) the canaries run and write records before the `DROP_AFTER` guard exits 3, so the
   file's absence discriminates (the existing test cannot: the twin guard at R:107 satisfies it).
7. **F11, no default venue.** The venue argument is required and must be `sandbox` or `pc`; anything else, or nothing, is
   `run_canaries: venue must be sandbox or pc, got '<v>'` on stderr, exit 64, before any file is written. Update every caller
   (premise: PC:121 passes `pc`; T:629 passes none; T:858 passes `sandbox`).
8. **F18, no empty unit name.** `check_egress.py --units` refuses an empty name anywhere in the list (`""`, `","`, `"a,,b"`):
   `usage: --units carries an empty unit name`, exit 64, before any bundle is read. The module docstring's exit list gains 64.
9. **F19, the allow entry is an IPv4 literal.** `_egress_apply_gate` refuses an entry whose host part is not a dotted-quad IPv4
   literal (a CIDR `10.0.0.1/8`, a hostname, an empty host): the existing message family `egress: allow entry must be <ip>:<port>,
   got '<entry>'`, return 64, before any rule is written.
10. Nothing else changes: the rule set, the digests, the canaries, the observed gate state and mechanism, the evidence format, the
    checker's verdict logic and its 0/1/2 codes, every committed fixture.

## Tests (each RED before its code change and GREEN after; paste both runs with the first failing assertion)

Name them as you see fit; the set must include, at minimum:
- the F6 collision: two namespaces whose names derive one octet (premise: `s0-05-hermes-acp` and `s0-05-u7` → 107) → the second
  create returns 65 with the exact message and leaves nothing behind; the first still passes its positive control.
- the F23 live sibling: a create of a name whose owner is a live process → 65, the sibling's veth still present inside its
  namespace; a stale owner (a dead pid) → the create succeeds.
- F7 + F9: a process started inside a namespace (as the runner starts a unit: `egress_ns_run <ns> setsid …` in the background) is
  gone after `egress_ns_destroy`, and no process's net-namespace inode equals the deleted namespace's.
- a RUNNER-level live test (root-gated like the other namespace tests): `run_s0_05_units.sh <tmp> hermes-acp` with `S0_01_TOOLS`
  pointing at a test-local stand-in launcher (under `tmp_path`, never under `proofs/`) and `ALLOWED_HERMES` at a local listener on
  the unit's veth host address (`egress_ns_host_ip s0-05-hermes-acp`, premise: 10.201.107.1); assert after it exits: no stand-in
  process remains, no namespace remains, `units.json` carries the F10 row, and a second concurrent invocation for the same unit is
  refused while the first holds its namespace. Do NOT assert the checker's verdict (the model hosts may not resolve here, so it may
  defer).
- F8's shebang agreement, F3+F17's absent file, F11's refusals (missing, empty, `synthetic`), F18's three spellings, F19's CIDR,
  hostname and empty-host entries.
- `test_live_tree_…`-style regression: the whole existing file stays green (premise: `106 passed` twice).

Test doubles for the S0-01 launcher live ONLY under the test's `tmp_path`; the proof's evidence always comes from the real launcher
on the PC (owner-run). Every namespace a test creates is destroyed in its teardown, even on failure.

## Mutants (scratch-copy restore only: copy the file, mutate the copy in place, run, restore from the copy; never `git checkout`,
`stash` or `restore` the shared tree; every mutant must COMPILE and COLLECT — `bash -n` / `py_compile` — per AF-AP-78)

Paste, per row, the mutant, the run's rc and the failing test's name:
m1 the F6 refusal removed · m2 the F23 owner guard removed · m3 `egress_ns_destroy` without the kill · m4 the R:72 `DROP_BEFORE`
guard removed · m5 the venue default `sandbox` restored · m6 the checker's `if unit` filter restored · m7 the IPv4 check removed ·
m8 the backend's bash script restored as a python3 row · m9 the runner stopping the unit by `kill "$launch_pid"` alone.

## Gates (paste verbatim)

```
mkdir -p /tmp/e2 && python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e2/bt1   # twice, bt1 and bt2: counts identical
bash -n proofs/S0-05/netns_lib.sh proofs/S0-05/run_canaries.sh proofs/S0-05/tools/pc/run_s0_05_units.sh
python -m pyflakes proofs/S0-05/check_egress.py tests/test_s0_05_egress.py
python3 scripts/no_laya_in_gates.py                      # C is a listed gate file; expect: 37 files scanned, clean
python3 scripts/ap_screen.py proofs/S0-05/check_egress.py proofs/S0-05/netns_lib.sh proofs/S0-05/run_canaries.sh proofs/S0-05/tools/pc/run_s0_05_units.sh
python3 scripts/ap_screen.py --tests tests/test_s0_05_egress.py
ip netns list; ip -o link show | grep -c ' eh'           # after the last run: no namespace, zero eh* veths
```
Run each gate in ONE foreground call (never background a gate and stop). `shellcheck` is absent in this sandbox (premise); say so.

## Report (`tasks/briefs/s0-05-support/E2-report.md`)

DATA, not prose: every file:line created or changed; each RED→GREEN pair; the nine mutant rows; the gate runs pasted; every
DISCREPANCY with a premise below (your item 1 re-measures the premise block; a mismatch you cannot resolve in three experiments is
one DISCREPANCIES row, then build on the measured truth or stop if the intent cannot be met); NOT-done. Then
`python3 scripts/report_lint.py --min-refs 12 --map L=proofs/S0-05/netns_lib.sh --map R=proofs/S0-05/run_canaries.sh --map
PC=proofs/S0-05/tools/pc/run_s0_05_units.sh --map C=proofs/S0-05/check_egress.py --map T=tests/test_s0_05_egress.py
tasks/briefs/s0-05-support/E2-report.md` — apply its `fix:` hints for at most three rounds, then paste the summary and finish.
Your final message carries the report's summary table.

Standing do-nots: never change the mode or owner of a shared directory (`/tmp`, `/root`, `/etc`; AF-AP-117); never kill a
process you did not start (kill by pid, never by name); leave no namespace, veth, listener or stand-in process behind.

## PREMISE — MEASURED at authoring (2026-09-23 01:0xZ, sandbox root @ 5762efe)

```
$ git log -1 --format='%h %s' HEAD ; git log -1 --format=%h origin/claude/soundbox-kit-migration-iz1jwf
5762efe transcripts: scrubbed sandbox chat digests (2026-09-23)
5762efe
$ git log --format='%h %ad %s' --date=format:'%Y-%m-%dT%H:%M' -- proofs/S0-05 tests/test_s0_05_egress.py | head -3
56d2c78 2026-09-22T09:14 S0-05 E1-R2 (coordinator touch on the test only): the live motivating-instance test now reproduces F1 …
860ab9e 2026-09-22T08:38 S0-05 E1-R1: the checker asserts mechanism == veth-iptables in PHASE 1 (VERIFY-E1 F1, the D-031 …
24e80e6 2026-09-08T03:24 S0-05: the canary suite, the selective-netns library, the collector, the checker, three REAL namespace …
$ sha256sum (first 16) + wc -l
1b2bd911d54262d3 209 proofs/S0-05/netns_lib.sh
6f7298077aa39819 131 proofs/S0-05/run_canaries.sh
b28dc7632602d555 150 proofs/S0-05/tools/pc/run_s0_05_units.sh
5b766582a9a03f91 375 proofs/S0-05/check_egress.py
3a630a624cf9a518 899 tests/test_s0_05_egress.py
$ python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e2pre/bt1   (and bt2; uid 0)
106 passed in 12.08s
106 passed in 10.59s
$ line map
R:30 VENUE=${6:-sandbox}          R:37 mkdir -p "$OUT"   R:39 : > "$JSONL"
R:69 DROP_BEFORE=…   R:72 [ -n "$DROP_BEFORE" ] || … exit 3   R:107 [ -n "$DROP_AFTER" ] || … exit 3
PC:52 LAUNCH[hermes-acp]="$S0_01_TOOLS/pc_launch.py --leg run-1 --model s0-01-pong"
PC:54 LAUNCH[buzz-acp]=  (the same)   PC:56 LAUNCH[s0-01-backend]="$S0_01_TOOLS/pc_backend_restart.sh"
PC:65 default UNITS=(hermes-acp buzz-acp s0-01-backend)   PC:72-73 cleanup + trap   PC:82 ns="s0-05-$unit"
PC:103 egress_ns_run "$ns" setsid /usr/bin/python3 ${LAUNCH[$unit]} … &   PC:105 launch_pid=$!   PC:124 kill "$launch_pid"
PC:121 bash "$P/run_canaries.sh" "$unit" "$ns" "$allowed" "$EVIDENCE_ROOT" "" pc
L:44-47 _egress_octet … n % 254 + 1   L:76 egress_ns_destroy "$ns" (destroy-first)   L:206-207 ip link del / ip netns del
L:107-111 _egress_apply_gate: the port is validated, the ip is not
C:357-360 --units default "curl"; required = [unit for unit in args.units.split(",") if unit]
$ collector callers: PC:121 (6 args, venue pc) · T:629 (4 args, NO venue; the unreadable-counter test) · T:858 (6 args, sandbox)
$ F18: python3 proofs/S0-05/check_egress.py proofs/S0-05/fixtures/evidence-mechanism-sandbox --units hermes-acp ; echo rc=$?
unit-missing: hermes-acp / exit 1 per contract          rc=1
$ … --units ""                                          rc=0   (PASS: 1 units, 11 canaries failed as required)
$ F6/F7/F23 probe (sandbox root; the script is in the appendix)
== F6: two namespaces on one /24 (octet 107)
create s0-05-hermes-acp rc=0
create s0-05-u7 rc=0
host: eh6a87fce7 10.201.107.1/24
host: eh6a854620 10.201.107.1/24
positive control from s0-05-hermes-acp: rc=0 http=200
positive control from s0-05-u7: rc=28 http=000 curl: (28) Failed to connect to 10.201.107.1 port 18080 after 3002 ms
== F7: destroy while a process is inside
create e2-f7 rc=0
destroy rc=0
ip netns list has e2-f7: 0
sleep pid 2070 alive: yes; its netns inode=4026532313 (before destroy 4026532313)
   (note: stat of /proc/1/ns/net is refused here — "Permission denied" — so compare against inodes read before the delete)
== F23: a second create of the same name while the first run's process is inside
A create rc=0
A process links before B: lo en6a87fce7
B create (same name) rc=0
A process links after B:  lo
$ octets of the fixed names: s0-05-hermes-acp 107 · s0-05-buzz-acp 219 · s0-05-s0-01-backend 153 · collider s0-05-u7 107
$ F8: head -1 proofs/S0-01/tools/pc/pc_backend_restart.sh ; python3 ast.parse of it
#!/usr/bin/env bash
SyntaxError: leading zeros in decimal integer literals are not permitted; use an 0o prefix for octal integers
$ F9: egress_ns_run e2-f9 setsid /usr/bin/python3 -c 'import time; time.sleep(45)' & launch_pid=$!
launch_pid=2338 comm=bash
unit pid(s)=2340
after kill $launch_pid: unit 2340 alive=yes
$ after both probes: ip netns list → (empty); no listener, no sleep left
$ command -v shellcheck → (absent)
$ python3 scripts/no_laya_in_gates.py → no_laya_in_gates: 37 files scanned, clean   (proofs/S0-05/check_egress.py listed at scripts/gate_files.txt:35)
```

### Appendix — the probe (re-run it as your item 1; it cleans up after itself)

```bash
set -u; cd /home/user/agent-factory; . proofs/S0-05/netns_lib.sh
PIDS=(); cleanup() { for p in "${PIDS[@]}"; do kill "$p" 2>/dev/null; done; egress_ns_destroy s0-05-hermes-acp; egress_ns_destroy s0-05-u7; egress_ns_destroy e2-f7; }; trap cleanup EXIT
egress_ns_create s0-05-hermes-acp 10.201.107.1:18080; echo "create s0-05-hermes-acp rc=$?"
egress_ns_create s0-05-u7 10.201.107.1:18080; echo "create s0-05-u7 rc=$?"
ip -o -4 addr show | awk '$4 ~ /^10\.201\.107\./ {print "host:", $2, $4}'
python3 -m http.server 18080 --bind 0.0.0.0 >/dev/null 2>&1 & PIDS+=($!); sleep 1
for ns in s0-05-hermes-acp s0-05-u7; do egress_ns_run "$ns" curl -sS --connect-timeout 3 -o /dev/null -w "%{http_code}" http://10.201.107.1:18080/; echo " rc=$? from $ns"; done
egress_ns_destroy s0-05-u7; egress_ns_destroy s0-05-hermes-acp
egress_ns_create e2-f7 10.201.1.1:1 >/dev/null; ip netns exec e2-f7 sleep 60 & PIDS+=($!); sp=$!; sleep 1
ino=$(stat -Lc %i /proc/$sp/ns/net); egress_ns_destroy e2-f7
echo "listed: $(ip netns list | grep -c '^e2-f7') alive: $(kill -0 $sp && echo yes) inode: $(stat -Lc %i /proc/$sp/ns/net) was $ino"
```
