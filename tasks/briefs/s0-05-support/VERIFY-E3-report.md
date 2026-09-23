# VERIFY-E3 — report (task #165, lane verify-e3, sandbox, agent `adversarial-verifier` on claude-opus-5-5)

STATUS: COMPLETE (2026-09-23 10:18Z). GATE RECOMMENDATION: **NOT-READY** on ONE blocker, F3 (a second stop signal during
`cleanup` aborts it; the namespace and, for the pair, D-051's DNAT + `route_localnet=1` outlive the run), with a one-line repair
already shown to discriminate; **F2 returned as CONTRACT-DEFECT** (A2's directory-stat census cannot see in-place writes). Every other
row is a follow-up. Mutants: the builders' 18 of 18 KILLED; mine 12 KILLED, 5 SURVIVED, 1 EQUIVALENT. Census at the end: empty.
Key: RC = `proofs/S0-05/run_canaries.sh`, C = `proofs/S0-05/check_egress.py`, PC = `proofs/S0-05/tools/pc/run_s0_05_units.sh`,
L = `proofs/S0-05/netns_lib.sh`, CAN = `proofs/S0-05/canaries/c0_allowed_target.sh`, T = `tests/test_s0_05_egress.py`.
Nothing in this lane ran on the PC.

## 1. PREMISE — re-measured (sandbox, uid 0)

````
$ date -u
Wed Sep 23 08:55:19 UTC 2026

$ git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf ; git rev-parse --short HEAD
2ebd486
2ebd486

$ git diff c269263 origin/... -- <the seven files> | wc -l ; git diff origin/... HEAD -- <the seven files> | wc -l ; git status --porcelain -- <the seven files> | wc -l
0
0
0

$ for f in <the seven files>; do sha256(16) lines path; done
5241b539c50a98b8 175 proofs/S0-05/run_canaries.sh
d39bb7b2665c6413 511 proofs/S0-05/check_egress.py
d2837c4d073bf398 410 proofs/S0-05/netns_lib.sh
888e9f3ebf27fb2e 15 proofs/S0-05/canaries/c0_allowed_target.sh
6d313b8bef0c677e 36 proofs/S0-05/canaries/_emit.sh
07a274102b1abf2a 578 proofs/S0-05/tools/pc/run_s0_05_units.sh
3050c242f33d38ee 2999 tests/test_s0_05_egress.py

$ git diff --name-only c269263 origin/...      # c269263 -> 2ebd486 touches no code
docs/INCIDENT-LOG.md
tasks/briefs/hermes-repin/VERIFY-REPIN-a-report.md
tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-S-brief.md
tasks/briefs/s0-02-support/B9-R1-brief.md
tasks/briefs/s0-05-support/VERIFY-E3-brief.md
todo/BUILD-TASKLIST.md
transcripts/sandbox/chat-2026-09-23.md
wiki/topics/live-state.md

$ git diff c269263 HEAD -- proofs/S0-05 proofs/S0-01/pins.py | wc -l ; git status --porcelain -- proofs/S0-05 proofs/S0-01 tests/test_s0_05_egress.py | wc -l
0
0

$ git log --format="%h %ad %s" --date=format:"%m-%d %H:%M" -3 -- proofs/S0-05 | cut -c1-110
76f439f 09-23 08:26 E3-b landed (GATED-PENDING-VERIFY): S0-05's collector takes the unit's whole allow-set, C0
ec56bb7 09-23 06:41 E3 landed (GATED-PENDING-VERIFY): the S0-05 live-unit launch recipe (Part X, CD1 A1-A8, th
6f2589d 09-23 03:47 S0-05 E2-R1 landed (GATED-PENDING-VERIFY): VERIFY-E2's seven blockers closed in the netns

$ df -h /home/user | tail -1
/dev/vda        252G   36G  1.9G  96% /

$ /tmp/ve3/census.sh     # baseline, before anything of mine exists
netns: 0 []
veth: 0 []
nat PREROUTING: -P PREROUTING ACCEPT|
nat OUTPUT: -P OUTPUT ACCEPT|
filter FORWARD: -P FORWARD ACCEPT|
/etc/netns: 0 []
/run/s0-05-egress: 0 []
route_localnet(all/default): 0/0; nonzero-per-if:
ip_forward: 0
````

PREMISE HOLDS: every S0-05 byte is identical at c269263, origin 2ebd486 and the working tree; the seven hashes and line counts
match the brief's table line for line. Not CONTRACT-INVALID.

## Gates (the brief's, pasted; run FIRST, before any namespace of mine existed, so no name could collide)

````
$ for n in 1 2; do mkdir -p /tmp/ve3/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/ve3/bt | tail; rm -rf /tmp/ve3/bt; done
Wed Sep 23 09:03:46 UTC 2026
251 passed in 202.04s (0:03:22)
ROOT1 pipestatus=0
Wed Sep 23 09:07:09 UTC 2026
251 passed in 202.21s (0:03:22)
ROOT2 pipestatus=0

$ rm -rf /tmp/ve3nr && mkdir -p /tmp/ve3nr && chmod 1777 /tmp/ve3nr && setpriv --reuid=65534 --regid=65534 --clear-groups env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/ve3nr/bt -rs
Wed Sep 23 09:10:31 UTC 2026
SKIPPED [1] tests/test_s0_05_egress.py:2957: network-namespace legs need root + iproute2 + iptables; NOT run here — they run on a capable venue (this sandbox has them; CI does not)
204 passed, 47 skipped in 6.35s
NONROOT pipestatus=0

$ bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py
1 files set=9f0502080347
$ bash -n (the four shell files) -> rc=0 each ; command -v shellcheck -> absent
$ tools: GNU bash 5.2.21 · iproute2-6.1.0 · iptables v1.8.10 (nf_tables) · setpriv util-linux 2.39.3 · curl 8.5.0 · Python 3.11.15 · locale -a: C, C.utf8, POSIX
$ census after the gates (09:10:38Z): netns 0 · veth 0 · nat PREROUTING `-P PREROUTING ACCEPT` only · /etc/netns 0 · /run/s0-05-egress 0 · route_localnet 0/0
````

The builders' counts reproduce exactly (251 / 251 / 204+47, set `9f0502080347`, the brief's premise id).

## 2. E3 Part X — X1, X2 (X3 and X4 below)

### X1 + G parity (items 2 and 5 together): one table, six consumers

Driver `/tmp/ve3/parity.py` (scratch, deleted at the end): 83 rows of MY entries (the five E3 X1 rows, marked `X1-*`, plus 78 the
builder's `_G_ROWS` does not hold). Each row is judged by the REAL code: `egress_allow_entry_ok` (L:77) sourced under `LC_ALL` =
`C`, `C.UTF-8`, `POSIX` (every installed locale, `locale -a`); the checker's `_split_ip_port` (C:206), exact refusal text
required; the collector (RC:46 `egress_allow_entry_ok`, a nonexistent namespace and an explicit valid blocked entry: 64 + the exact text + no evidence dir
= refused, 3 + the drop-counter text = accepted; rows with `,` or `/` skipped, they are collector syntax); and `egress_ns_create`
(L:88 `egress_ns_create`): 64 + the exact contract line + a clean census of that name = refused, rc 0 + a namespace = accepted, destroyed by name.

````
$ /root/venv-agent-factory/bin/python -B /tmp/ve3/parity.py /tmp/ve3/par        (2026-09-23 09:12:29Z, root)
OK  X1-20-digits    "10.9.9.9:99999999999999999999"  want=ref lib[C]=ref lib[C.UTF-8]=ref lib[POSIX]=ref checker=ref collector=ref create=ref
OK  X1-2^63         "10.9.9.9:9223372036854775808"   want=ref ... (all six ref)
OK  X1-65536        "10.9.9.9:65536"                 want=ref ... (all six ref)
OK  X1-0            "10.9.9.9:0"                     want=ref ... (all six ref)
OK  X1-00080        "10.9.9.9:00080"                 want=ref ... (all six ref)
OK  min-port-1 "1.2.3.4:1" · octets-199-249-250-251 "199.249.250.251:65534" · octets-200-201-209-219 · octets-25-5-2-0 "25.5.2.0:65535" · octet-99-100 · port-65534   -> want=acc, all six acc
OK  last-octet-256 · octet-260 · octet-300 · octet-999 · octet-4-digits · octet-00 · last-octet-00 · octet-01-second · three-octets · five-octets
    · empty-octet · leading-dot · trailing-dot · hex-octet "0x0a.0.0.1:80" · glob-octet "10.0.0.*:80" · qmark-octet "1?.0.0.1:80"
    · port-65540 · port-69999 · port-99999 · port-00000 · port-0080 · port-long-zeros · port-2^32 · port-2^64 · port-2^64+1
    · plus-port "+80" · minus-port "-80" · minus-zero "-0" · hex-port "0x50" · hex-port-upper "0X50" · exp-port "1e3" · float-port "80.0"
    · underscore-port "8_0" · plus-ip · arith-port "$((80))" · param-port "${PATH}" · bracket-port "[80]" · hash-port "80#x"
    · space-before-port · leading-space · nl-inside-ip · nl-leading · nl-double-end · nel-end U+0085 · ls-end U+2028 · nbsp-end · nbsp-inside
    · devanagari-port · bengali-port · thai-port · persian-port (U+06F0) · fullwidth-port (U+FF10) · fullwidth-octet · math-bold-port (U+1D7CE)
    · superscript-port "8²" · mixed-arabic-digit "8٠" · fullwidth-colon U+FF1A · fullwidth-dot U+FF0E
    · empty-ip ":80" · colon-only · double-colon · extra-colon-middle "::80" · colon-after-port "80:" · two-ports "80:90"
    · ipv6-loopback-bare "::1:80" · ipv6-mapped-bracket · ipv6-mapped-bare "::ffff:10.0.0.1:80" · ipv6-zone "fe80::1%eth0:80"
    · path-suffix "80/x" (collector n/a) · comma-suffix "80," (collector n/a)                                   -> want=ref, all ref
MISMATCH cr-end "10.0.0.1:80\r" / crlf-end "10.0.0.1:80\r\n": collector rc=64, create rc=64, census clean — ODD only on the stderr text
rows=83 mismatches=2
````

The two ODD rows are MY harness (Python `text=True` turns `\r` into `\n`), re-checked as bytes, both exact refusals:

````
collector '10.0.0.1:80\r' 64 True b"run_canaries: allowed entry '10.0.0.1:80\r' is not <ip>:<port>[/<path>]\n"
create    '10.0.0.1:80\r' 64 True b"egress: allow entry must be <ip>:<port>, got '10.0.0.1:80\r'\n"
collector '10.0.0.1:80\r\n' 64 True b"run_canaries: allowed entry '10.0.0.1:80\r\n' is not <ip>:<port>[/<path>]\n"
create    '10.0.0.1:80\r\n' 64 True b"egress: allow entry must be <ip>:<port>, got '10.0.0.1:80\r\n'\n"
````

So all 83 rows agree in every consumer and locale; each X1 row returns 64 with the contract line and creates nothing (the
`create` column requires a clean census). A structured differential fuzz (near-valid quads with 0-3 mutations drawn from ASCII
digits, `.:`, whitespace, signs, `x e _ / , [ ] % # * ?` and 14 non-ASCII code points; a generator of mine, not the builder's),
library batched in one bash per locale vs the checker:

````
seed=23 locale=C: 20000 entries, accepted by the checker 2350, mismatches 0 []
seed=23 locale=C.UTF-8: 20000 entries, accepted by the checker 2350, mismatches 0 []
seed=23 locale=POSIX: 20000 entries, accepted by the checker 2350, mismatches 0 []
seed=165 locale=C: 20000 entries, accepted by the checker 2336, mismatches 0 []
seed=165 locale=C.UTF-8: 20000 entries, accepted by the checker 2336, mismatches 0 []
seed=165 locale=POSIX: 20000 entries, accepted by the checker 2336, mismatches 0 []
````

AF-AP-129 sweep of the final boundary (every `-gt/-ge/-lt/-le/-eq/-ne` and `$(( ))`): the only input-derived numeric tests are
`L:82` (`-le 65535` after the digit-bounded regex), `RC:58` (`-lt 65535` on a port the rule already accepted) and `PC:198` `ID_REFUSED`
(`8#$mode` after `^[0-7]{1,4}$`); the rest (`L:51-52` `sha256sum` hash digits, `L:91` `egress_ns_create`, `L:226` `egress_ns_create_isolated`, `L:331` `removed`, `L:357-384` `remaining` counters, `PC:149` `_pins`,
`PC:395`, `PC:403` `$? -ne 0` exit statuses) are not input-derived. No instance.

### X2 — fault injection at steps the builder did not use (library)

Driver `/tmp/ve3/x2.sh`: each case sources the REAL `netns_lib.sh`, defines ONE fault as a function (the contract's test seam),
runs `egress_ns_create` on a fresh name, prints rc + stderr + the census of that name, then destroys it by name.

````
$ bash /tmp/ve3/x2.sh        (2026-09-23 09:15:22Z)
=== case hostaddr    create rc=1  stderr: VE3-injected: host address refused     census: netns=0 veth=0 etc=no owner_dir=[] nat=0
=== case hostup      create rc=1  stderr: VE3-injected: host link up refused     census: netns=0 veth=0 etc=no owner_dir=[] nat=0
=== case peermove    create rc=1  stderr: VE3-injected: peer move refused        census: netns=0 veth=0 etc=no owner_dir=[] nat=0
=== case nsaddr      create rc=1  stderr: VE3-injected: ns address refused       census: netns=0 veth=0 etc=no owner_dir=[] nat=0
=== case nslo        create rc=1  stderr: VE3-injected: ns lo up refused         census: netns=0 veth=0 etc=no owner_dir=[] nat=0
=== case etcmkdir    create rc=1  stderr: VE3-injected: /etc/netns mkdir refused census: netns=0 veth=0 etc=no owner_dir=[] nat=0
=== case resolv      create rc=1  stderr: .../netns_lib.sh: line 142: /etc/netns/ve3-x2-resolv/resolv.conf: Is a directory   census: all 0/no/[]
=== case policy      create rc=1  stderr: VE3-injected: first policy refused     census: netns=0 veth=0 etc=no owner_dir=[] nat=0
=== case rule2       create rc=1  stderr: VE3-injected: second gate rule refused census: netns=0 veth=0 etc=no owner_dir=[] nat=0
=== case entry2      create rc=1  stderr: VE3-injected: second entry rule refused census: netns=0 veth=0 etc=no owner_dir=[] nat=0
=== case looprule    create rc=1  stderr: VE3-injected: last loopback rule refused census: netns=0 veth=0 etc=no owner_dir=[] nat=0
=== case ln          create rc=65 stderr: namespace-live: ve3-x2-ln owned by pid  (claim churn after 10 attempts)   census: all 0/no/[]
=== case rb-netnsdel create rc=1  stderr: VE3-injected: ns lo up refused         census: netns=1 veth=0 etc=no owner_dir=[] nat=0
=== case rb-linkdel  create rc=1  stderr: VE3-injected: ns lo up refused         census: netns=0 veth=0 etc=no owner_dir=[] nat=0
=== case rb-etcrm    (vacuous: its trigger fired before /etc/netns existed; redone below with a late trigger)
(every case, after its destroy-by-name: netns=0 veth=0 etc=no owner_dir=[] nat=0)
````

Eleven new fault points (host address, host link, peer move, namespace address, `lo` up, `/etc/netns` mkdir, the resolv.conf
write, the first policy, the SECOND gate rule of an entry, the second ENTRY's rule, the last loopback rule) roll back cleanly
with the failing step's message on stderr: X2 holds for single faults. Two observations:

- **ln (the claim's owner record cannot be linked)**: rc 65 and the line `namespace-live: ve3-x2-ln owned by pid  (claim churn after 10 attempts)`
  — an EMPTY pid and the wrong reason (nothing is live; the record could not be written). L:160-161 `namespace-live` says the function
  returns "1 when the record cannot be written at all"; the link failure path (L:169-185 `EGRESS_OWNER_DIR`) loops ten times on an absent record and
  refuses 65. Fail-closed; nothing created. (Finding F7.)
- **A rollback step that itself fails leaves an UNOWNED leftover** (`rb-netnsdel`: the namespace survives, the owner record is
  gone). The late-trigger `/etc/netns` variant (fault at the first policy, then ONE failing `rm -rf /etc/netns/<ns>`):

````
VE3-injected: first policy refused
VE3-injected: rm of /etc/netns refused once
create rc=1
census: netns=0 etc=yes owner_dir=[]
after destroy-by-name: etc=no netns=0
````

Mechanism (read from primary source): `_egress_ns_teardown` swallows the three deletes (`ip link del … || true`,
`ip netns del … || true`, `rm -rf "/etc/netns/$ns"`, L:399-401) and returns only its rc, which records a relay-reach failure (L:350 `egress_relay_reach_del`) or a pid that
survived SIGKILL (L:391-396 `final_survivors`). `_egress_ns_rollback` (L:191) releases the claim whenever that rc is 0. So the comment at L:188-190 `teardown`
("a leftover the rollback could not remove stays owned by $$") holds for two of the teardown's five steps only.

### X2 through the REAL runner: is that leftover reaped by `cleanup`? (the contract's promise)

Driver `/tmp/ve3/rb_runner.py` (imports the test module's helpers; the stand-in via the RECORDED override; a PATH `ip`/`rm` shim
fails ONE create step of `s0-05-hermes-acp`, then ONE rollback step):

````
$ /root/venv-agent-factory/bin/python -B /tmp/ve3/rb_runner.py netnsdel        (09:16:19Z)
runner rc: 1
runner stderr (non-override lines): [..., 'SKIP hermes-acp: VE3-injected: create step refused']
units.json hermes-acp: [{'unit': 'hermes-acp', 'status': 'not-run', 'reason': 'VE3-injected: create step refused', 'override': {...}}]
census AFTER the runner exited: {'netns': True, 'veth': False, 'etc_netns': False, 'owner_dir': []}
census after my destroy-by-name: {'netns': False, 'veth': False, 'etc_netns': False, 'owner_dir': []}

$ /root/venv-agent-factory/bin/python -B /tmp/ve3/rb_runner.py etcrm
runner rc: 1
units.json hermes-acp: [{... 'reason': 'VE3-injected: create step refused\nVE3-injected: rollback rm of /etc/netns refused once', ...}]
census AFTER the runner exited: {'netns': False, 'veth': False, 'etc_netns': True, 'owner_dir': []}
stray files in /etc/netns: ['s0-05-hermes-acp']
census after my destroy-by-name: {'netns': False, 'veth': False, 'etc_netns': False, 'owner_dir': []}
````

The name WAS in the reap set before create (PC:392 `NS_LIVE`), but `cleanup` (PC:322-327) reaps only a name whose owner record is `$$`,
and the rollback had already released it: the leftover namespace (or `/etc/netns` entry) outlives the runner, silently in the
`netnsdel` case (the failing `ip netns del`'s own stderr is discarded by `2>/dev/null`, L:400). (Finding F1.)

### X3 — two creators race ONE stale claim (natural race, no pause), the real library

Driver `/tmp/ve3/x3race.py`: per trial a fresh name, a stale owner record from a reaped pid (every other trial also the legacy
E2-R1 `<ns>.claim` dir), N creators released by one barrier file, each `egress_ns_create` then printing rc/pid/inode and STAYING
ALIVE until killed by PID. Invariants per trial: exactly one rc 0 and the rest rc 65; every loser's stderr is exactly
`namespace-live: <ns> owned by pid <winner>`; the owner record names the winner; the inode the winner saw is the final one; no
claim temp or tombstone left (the legacy `.claim` dir is removed only by destroy, L:196); the census is clean after destroy by name.

````
$ x3race.py 60 2    (09:18:18Z; the first version also flagged the legacy .claim dir as a stray: 30 "violations", all of them
                     that dir alone, removed by destroy — `left_after_destroy: []` — my invariant, not the code)
$ x3race.py 100 2   (09:19:01Z, the legacy dir counted separately)
trials=100 exactly-one-winner-and-one-65=100 violations=0
$ x3race.py 40 3    (three creators: the DECLARED LIMIT at L:157-159)
trials=40 exactly-one-winner-and-one-65=35 violations=5
trials=40 exactly-one-winner-and-one-65=27 violations=13
shown violations: 10 | trials where >=2 creators passed the claim (rc 0 or a failed build): 10
VIOLATION {'trial': 19, 'lines': ['rc=65 pid=29532 ino=', 'rc=0 pid=29533 ino=4026532262', 'rc=1 pid=29534 ino='], 'errs': ['namespace-live: ve3-x3-dc83cab7 owned by pid 29534\n', '', 'Cannot create namespace file "/run/netns/ve3-x3-dc83cab7": File exists\n'], 'owner': None, 'final_ino': None, ...}
````

X3 holds for the contract's case (two creators): 100 of 100. The three-creator limit is real and declared, but its text
understates it (Finding F8): the window is not "microseconds" — it spans the mv, cat and ln processes (L:177-179 `owner_file`) —
and the effect is not only "orphan the winner's record": two creators pass the claim; in trial 19 the second's failed build
rolled back the FIRST's namespace and released the claim, so a creator returned rc 0 for a namespace that no longer existed.

### X4 — the REAL runner's `cleanup` against a namespace owned by a LIVE pid and by a DEAD one

Driver `/tmp/ve3/x4.py` (the stand-in through the recorded override; the holder killed by PID; destroy by name after):

````
=== X4 case live (09:21:37)
before: {'ino': 4026532262, 'owner': '17997'} holder pid 17997
runner rc 1 | row [{'unit': 'hermes-acp', 'status': 'not-run', 'reason': 'namespace-live: s0-05-hermes-acp owned by pid 17997'}]
after:  {'ino': 4026532262, 'owner': '17997'} | same inode + owner: True
=== X4 case dead-refused (09:21:38)        (the dead owner's leftover; the runner refused before its claim: port 0)
before: {'ino': 4026532262, 'owner': '18199'} | owner alive: False
runner rc 1 | row [{'unit': 'hermes-acp', 'status': 'not-run', 'reason': "egress: allow entry must be <ip>:<port>, got '10.201.107.1:0'"}]
after:  {'ino': 4026532262, 'owner': '18199'} | census: {'netns': True, 'veth': True, 'etc_netns': True, 'owner_dir': ['s0-05-hermes-acp.owner']}
=== X4 case dead-takeover (09:21:39)       (the same leftover; a valid run)
before: {'ino': 4026532262, 'owner': '18381'} | owner alive: False
runner rc 1 | row [{'unit': 'hermes-acp', 'status': 'run', 'note': 'contained live unit'}]
after:  {'ino': None, 'owner': None} | census: {'netns': False, 'veth': False, 'etc_netns': False, 'owner_dir': []}
(each case, after my destroy-by-name: {'netns': False, 'veth': False, 'etc_netns': False, 'owner_dir': []})
````

X4 holds: `cleanup` (PC:322-327) leaves a live owner's namespace intact (same inode, same record), never touches a dead owner's
leftover it did not claim, and a valid run takes the stale claim over (L:107 `_egress_ns_claim`) and leaves nothing (rc 1 = the checker's override
refusal, by design).

## 3. E3 Part A — line by line against CD1 and the E3 brief (real runner legs; stand-ins through the recorded override)

### A5 + A3 + A1 on one real hermes-acp leg (my sentinels, a real-shaped OmniRoute stand-in: 200 `/api/health`, 401 `/v1/models`)

Driver `/tmp/ve3/partA.py`. Seventeen variables of MY choosing planted in the runner's environment (the builder's four `PLANTED`
stay too): `VE3_SENTINEL_PLAIN`, `VE3_API_KEY_SENTINEL`, `ve3_lower_token`, `VE3PASSWORDX`, `NSEC1VE3`, `VE3_PRIVATE`, `VE3_SECRET_`
(seven match `pins.REDACTED_ENV_KEY_RE`), `HOME`, `HERMES_HOME`, `LANG`, `LC_ALL`, `PYTHONDONTWRITEBYTECODE` (planted values),
`http_proxy`, `HTTPS_PROXY`, `TZ`, `VE3.DOTTED_KEY` (a name bash cannot un-export) and an exported function `BASH_FUNC_ve3fn%%`:

````
runner rc 1
stand-in records: 1
  env_keys: ['HERMES_HOME', 'HOME', 'LANG', 'PATH', 'PYTHONDONTWRITEBYTECODE']
  env values: {'PATH': '/usr/bin:/bin', 'HOME': '/tmp/ve3/pa-2lprzqa4/evidence/hermes-acp/scratch/home', 'HERMES_HOME': '/tmp/ve3/pa-2lprzqa4/evidence/hermes-acp/scratch/hermes-home', 'LANG': 'C.UTF-8', 'PYTHONDONTWRITEBYTECODE': '1'}
  uid/gid: 65534 65534 | cwd: /tmp/ve3/pa-2lprzqa4/evidence/hermes-acp/scratch/home | stdin: fifo stdout: fifo | stop: eof
  sentinel names that reached the unit: [] | names matching REDACTED_ENV_KEY_RE: [] | exact key set == UNIT_ENV_KEYS: True
C0 records: [{'canary': 'C0', 'detail': 'curl exit 0, HTTP 200', 'http_status': 200, 'kind': 'http-get', 'path': '/api/health', 'rc': 0, 'status': 'run', 'target': '10.201.107.1:18431', 'unit': 'hermes-acp'}]
listener log (path asked from the namespace): ['10.201.107.2 /api/health', '10.201.107.2 /api/health', '']
checker on the REAL runner output: (1, 'units-manifest-invalid: hermes-acp override present', '')
````

A5 holds (`env -i`, PC:460-465 `PINNED_PATH`: exactly the five keys, planted values replaced, no sentinel name). A3 holds (stdin and stdout
are FIFOs, `stop: eof` = the stdin close at PC:511 `unit_in` stopped it). A1's recorded override is on the row and refused by the checker.

### A1 — every override shape on that REAL runner output (checker C:428 `override` + C:462 `overridden`)

````
A1 value {}               -> (1, 'units-manifest-invalid: hermes-acp override present', '')
A1 value null             -> (1, 'units-manifest-invalid: hermes-acp override present', '')
A1 value false            -> (1, 'units-manifest-invalid: hermes-acp override present', '')
A1 value 0                -> (1, 'units-manifest-invalid: hermes-acp override present', '')
A1 value ''               -> (1, 'units-manifest-invalid: hermes-acp override present', '')
A1 value []               -> (1, 'units-manifest-invalid: hermes-acp override present', '')
A1 value 'x'              -> (1, 'units-manifest-invalid: hermes-acp override present', '')
A1 value nested           -> (1, 'units-manifest-invalid: hermes-acp override present', '')
A1 key on a duplicate row only -> (1, 'units-manifest-invalid: hermes-acp override present', '')
A1 key removed            -> (1, 'unit-identity-invalid: hermes-acp entrypoint_realpath /tmp/ve3/pa-2lprzqa4/hermes-acp-standin is not the pin', '')
A1 key 'Override'         -> (1, 'unit-identity-invalid: hermes-acp entrypoint_realpath /tmp/ve3/pa-2lprzqa4/hermes-acp-standin is not the pin', '')
A1 key 'override '        -> (1, 'unit-identity-invalid: hermes-acp entrypoint_realpath /tmp/ve3/pa-2lprzqa4/hermes-acp-standin is not the pin', '')
A1 units.json absent      -> (1, 'unit-identity-invalid: hermes-acp entrypoint_realpath /tmp/ve3/pa-2lprzqa4/hermes-acp-standin is not the pin', '')
````

Every value of the `override` key is refused (presence, `"override" in entry`, C:428). A differently spelled key or a deleted
`units.json` is not an override to the checker, and A7 then refuses the stand-in anyway: the refusal is layered, never open.

### A7 — the checker against MY forgeries of a pins-matching record (a copy of the committed synthetic-pass fixture)

````
baseline (unmutated copy)          rc=0 | 'NOT run: buzz-acp — unit not launched in this collection'
exe trailing slash                 rc=1 | 'unit-identity-invalid: hermes-acp exe_realpath /usr/bin/python3.13/ is not the pin'
exe with /./                       rc=1 | 'unit-identity-invalid: hermes-acp exe_realpath /usr/bin/./python3.13 is not the pin'
sha256 UPPERCASE of the pin        rc=1 | 'unit-identity-invalid: hermes-acp entrypoint_sha256 F90A0CC333FA86D99495C7C984E4E11A1B83A7E3DC92883B7FD295AE70358EF1 is not the pin'
sha256 + trailing newline          rc=1 | 'unit-identity-invalid: hermes-acp entrypoint_sha256 f90a0cc333fa86d99495c7c984e4e11a1b83a7e3dc92883b7fd295ae70358ef1'   (the reason continues on a 2nd line)
entrypoint a list                  rc=1 | "unit-identity-invalid: hermes-acp entrypoint_realpath ['/home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp'] is not the pin"
uid saved-set 0                    rc=1 | 'unit-identity-invalid: hermes-acp uid 0'
uid fs 0                           rc=1 | 'unit-identity-invalid: hermes-acp uid 0'
uid strings                        rc=1 | "unit-identity-invalid: hermes-acp uid ['1000', '1000', '1000', '1000'] is not the four uids of the Uid line"
uid floats                         rc=1 | 'unit-identity-invalid: hermes-acp uid [1000.0, 1000.0, 1000.0, 1000.0] is not the four uids of the Uid line'
uid -1                             rc=1 | 'unit-identity-invalid: hermes-acp uid [-1, 1000, 1000, 1000] is not the four uids of the Uid line'
uid five values                    rc=1 | 'unit-identity-invalid: hermes-acp uid [1000, 1000, 1000, 1000, 1000] is not the four uids of the Uid line'
record is a list                   rc=1 | 'unit-identity-invalid: hermes-acp unit-identity.json lacks one of unit, pid, exe_realpath, entrypoint_realpath, entrypoint_sha256, uid, argv'
duplicate uid keys (1000 then 0)   rc=1 | 'unit-identity-invalid: hermes-acp uid 0'
empty file / invalid UTF-8         rc=1 | 'unit-identity-invalid: hermes-acp unit-identity.json is not JSON'
Infinity in pid                    rc=1 | 'unit-identity-invalid: hermes-acp unit-identity.json contains Infinity'
a symlink to a valid record        rc=1 | 'unit-identity-invalid: hermes-acp unit-identity.json is not a regular file'
a dangling symlink                 rc=1 | 'unit-identity-invalid: hermes-acp unit-identity.json absent'
a FIFO (must not hang)             rc=1 | 'unit-identity-invalid: hermes-acp unit-identity.json is not a regular file'
uid 4294967295 x4                  rc=0 | PASS            (a forger's value; /proc never reports it)
duplicate uid keys (0 then 1000)   rc=0 | PASS            (json.loads keeps the last key)
unit field names buzz-acp          rc=0 | PASS            (the record's `unit` is never compared with its directory)
pid with a newline + PASS line     rc=0 | PASS            (the identity line prints `pid` raw: a line `PASS: S0-05 forged ...` appears)
````

A7's contract refusals all hold (a missing file, a digest or path not the pin, uid 0 in ANY of the four slots), with the exact
`unit-identity-invalid: <unit> <detail>` text, and no shape hangs or crashes. The four accepted forgeries all need a hand-written
record (declared limit 4: unkeyed); the details print raw values (C:396-400 `entrypoint_realpath`, C:406 `entrypoint`), so a value with a newline splits a reason
or injects a line, but only into output the verdict does not depend on (the lines print only when `check()` returns). (Finding F12.)

### A4 — the unit user

The runner refuses a literal uid `0` (PC:369 `UNIT_UID`) after a shape regex that accepts `4294967295` (PC:161 `UNIT_USER`). Probed directly:

````
4294967295:4294967295    setpriv: uid 4294967295 not found, --init-groups requires an user that can be found on the system
(clear-groups)           uid=0(root) gid=0(root) groups=0(root)
1000:4294967295          uid=1000(ubuntu) gid=0(root) groups=0(root),4(adm),...
65534:0                  uid=65534(nobody) gid=0(root) groups=0(root),65534(nogroup)
the runner's S0_05_UNIT_USER regex (PC:161) ACCEPTS 4294967295:4294967295
````

`setpriv` reads uid `4294967295` as "no change" (root) under `--clear-groups`, but the LAUNCH (PC:464, PC:469) uses
`--init-groups`, which refuses a uid with no passwd entry; the only `--clear-groups` call (PC:440) runs `test -w`. So no A4
bypass for the unit (UNSURE only for a venue with a passwd entry for 4294967295). A unit gid of 0 (`S0_05_UNIT_USER=<uid>:0`, or a
gid of 4294967295) IS accepted and runs the unit in the root group; A7 records only the `Uid:` line (PC:248). A4's text is
uid-only, so this is a follow-up (Finding F11).

### A6 — identity-file shapes the builder did not use, through the REAL runner (the pair)

````
fifo 0600 nobody                 rc=1 row='identity file refused: shape'
directory 0700 nobody            rc=1 row='identity file refused: shape'
mode 0604                        rc=1 row='identity file refused: mode 604'
mode 0610                        rc=1 row='identity file refused: mode 610'
export prefix                    rc=1 row='identity file refused: shape'
empty value                      rc=1 row='identity file refused: shape'
leading space                    rc=1 row='identity file refused: shape'
mode 0400 (accepted?)            rc=1 row='positive control unreachable: 10.201.219.1:3999 not reachable from s0-05-buzz-acp'
mode 04600 setuid (accepted?)    rc=1 row='positive control unreachable: 10.201.219.1:3999 not reachable from s0-05-buzz-acp'
CRLF value (accepted?)           rc=1 row='positive control unreachable: 10.201.219.1:3999 not reachable from s0-05-buzz-acp'
key on line 2 after a comment    rc=1 row='positive control unreachable: 10.201.219.1:3999 not reachable from s0-05-buzz-acp'
symlink to a valid file          rc=1 row='positive control unreachable: 10.201.219.1:3999 not reachable from s0-05-buzz-acp'
S0-01 path by name               rc=1 row='identity file refused: S0-01 path /tmp/ve3/a6-yl7843so/s0-01-base/.secrets/agent.env'
HARD LINK to S0-01's agent.env   rc=1 row='positive control unreachable: 10.201.219.1:3999 not reachable from s0-05-buzz-acp'
byte COPY of S0-01's agent.env   rc=1 row='positive control unreachable: 10.201.219.1:3999 not reachable from s0-05-buzz-acp'
census: {'netns': False, 'veth': False, 'etc_netns': False, 'owner_dir': []}
````

(`positive control unreachable` = the identity was ACCEPTED and the leg went on; no relay listener in this probe.) The four
contract refusals hold with their exact texts, a FIFO or a directory is never opened (PC:200), and S0-01's `.secrets` is refused
by name (PC:195 `ID_REFUSED`). Accepted: a CRLF value (the key keeps its `\r`: declared limit 3), and a hard link or byte copy of S0-01's
`agent.env` — the contract's "by name" is met, the secret is not (Finding F13).

### A2 — the S0-01 tree census: what it can see

Driver `/tmp/ve3/a2.py`: the pinned base moved by the recorded override to a scratch tree the unit user OWNS (as rocco owns
`/home/rocco/s0-01-pinned` on the PC and IS the default unit user, PC:160 `PINNED_AGENT_REALPATH`); the stand-in (running as that user) writes during the leg.

````
--- in-place writes (no snapped dir stat changes): runner rc=1
  s0-01-tree-changed lines: []
  census changed: [] | tree: present | checker ran: True
  bytes on disk after the leg: {'pid': 'S0-05 WAS HERE (in place)\n', 'framedir': '', 'frames': 'S0-01 original bytes\nS0-05 appended a frame\n', 'subfile': 'S0-05 new file one level down\n'}
--- positive control: a new entry in .markers: runner rc=1
  s0-01-tree-changed lines: ['s0-01-tree-changed: /tmp/ve3/a2-_sqow9l_/s0-01-pinned/.markers']
  census changed: ['/tmp/ve3/a2-_sqow9l_/s0-01-pinned/.markers'] | tree: present | checker ran: False
````

The census (PC:210-228) snaps the `lstat` of `.markers` and of each `v2-*` DIRECTORY only. The unit rewrote `.markers/buzz-acp.pid`
in place, truncated `.markers/current-framedir`, appended to `v2-run-1/frames.jsonl` and created a file one directory down —
exactly the writes CD1's defect section names ("writes S0-01's `.markers/buzz-acp.pid` and `.markers/current-framedir`") — and
`s0-01-census.json` recorded `"changed": []` while the runner went on to its checker. The implementation matches the letter of
A2 (a `stat` census of the directories); the letter cannot see the harm it was written for (Finding F2, CONTRACT-DEFECT).

## 4. E3 Part D — the relay reach exists only for the pair's leg (REAL runner, the pair)

Driver `/tmp/ve3/partD.py` (compiled pair stand-in, relay stand-in on the host's 127.0.0.1:3999 ONLY, a real-shaped OmniRoute
stand-in). After each run: nat rules naming the pair's interface `ehda7d8593`, its `route_localnet`, the interface, the census.

````
--- D1 preflight fails (relay down): runner rc=1 in 0.7s | row=[{... 'reason': 'positive control unreachable: 10.201.219.1:3999 not reachable from s0-05-buzz-acp'}]
  after D1: nat rules naming ehda7d8593: [] | route_localnet: None | interface present: False | census: CLEAN
--- D2 launch fails: runner rc=1 in 1.9s | row=[{... 'reason': 'launch exited within the settle window; see .../buzz-acp.launch.log'}]
  checker first line: ['unit-declared-absent-but-present: buzz-acp']
  after D2: nat rules naming ehda7d8593: [] | route_localnet: None | interface present: False | census: CLEAN
--- D3 identity fails (unit as uid 0): runner rc=1 in 31.5s | row=[{... 'reason': 'unit identity not observed: uid 0'}]
  checker first line: ['unit-declared-absent-but-present: buzz-acp']
  after D3: nat rules naming ehda7d8593: [] | route_localnet: None | interface present: False | census: CLEAN
--- D4 canaries fail (collector exit 3): runner rc=1 in 31.1s | row=[{'unit': 'buzz-acp', 'status': 'run', 'note': 'contained live unit'}]
  stderr: ['run_canaries: cannot read the OUTPUT DROP counter of s0-05-buzz-acp']
  checker first line: ['evidence-missing: buzz-acp gate.json absent at .../evidence/buzz-acp/gate.json']
  after D4: nat rules naming ehda7d8593: [] | route_localnet: None | interface present: False | census: CLEAN
  [D5 SIGTERM mid-leg] mid-leg state before the signal: nat=['-A PREROUTING -d 10.201.219.1/32 -i ehda7d8593 -p tcp -m tcp --dport 3999 -j DNAT --to-destination 127.0.0.1:3999'] rl=1
--- D5 SIGTERM mid-leg: runner rc=143 in 1.7s | row=None | checker ran: False
  after D5: nat rules naming ehda7d8593: [] | route_localnet: None | interface present: False | census: CLEAN
  [D6] planted before the run (interface absent): ['-A PREROUTING -d 10.201.219.1/32 -i ehda7d8593 -p tcp -m tcp --dport 3999 -j DNAT --to-destination 127.0.0.1:3999', '-A PREROUTING -i ehda7d8593 -p udp -m udp --dport 53 -j DNAT --to-destination 127.0.0.1:53'] | interface present: False
--- D6 two stale rules naming the deleted interface, then a full run: runner rc=1 in 37.1s | row=[{'unit': 'buzz-acp', 'status': 'run', 'note': 'contained live unit'}]
  after D6: nat rules naming ehda7d8593: [] | route_localnet: None | interface present: False | census: CLEAN
--- D7a route_localnet silently unset (rule present): runner rc=1 in 5.7s | row=[{... 'reason': 'positive control unreachable: 10.201.219.1:3999 not reachable from s0-05-buzz-acp'}]
--- D7b DNAT silently not added (route_localnet set): runner rc=1 in 0.6s | row=[{... 'reason': 'positive control unreachable: 10.201.219.1:3999 not reachable from s0-05-buzz-acp'}]
  after D7a / D7b: nat rules naming ehda7d8593: [] | route_localnet: None | interface present: False | census: CLEAN
$ /tmp/ve3/census.sh (09:32:43Z): netns 0 · veth 0 · nat PREROUTING `-P PREROUTING ACCEPT` · /etc/netns 0 · /run/s0-05-egress 0 · route_localnet 0/0
````

Part D holds: after a leg that fails at EVERY step after the add (preflight D1, launch D2, identity D3, canaries D4) and after a
stop (D5), no rule names the interface and the interface (with its sysctl) is gone; two stale rules naming the DELETED interface
(a crashed run's shape, one of them a foreign spec) are removed by the next create's destroy-first (L:111 `_egress_ns_teardown` → L:350 `egress_relay_reach_del`); either half
of the reach alone (D7a: rule without `route_localnet`; D7b: `route_localnet` without rule) reads the existing `unreachable`
reason. Observations: D2/D3's checker line is E3's own DISCREPANCY 4 (`unit-declared-absent-but-present`); D4 — the runner wrote
`"status": "run", "note": "contained live unit"` for a leg whose collector exited 3 and left no bundle: PC:506-507 never reads the
collector's status (Finding F5).

## 5. E3-b G — see section 2 (the 83-row parity table and the 2 x 20,000-entry fuzz ran through library, collector and checker)

The rule holds in its three places (L:77 `egress_allow_entry_ok`, RC:46, C:206 `_split_ip_port`) for every row and fuzzed entry, under `C`, `C.UTF-8` and `POSIX`.

## 6. E3-b A — the order 3 → 5 → 6 and "before anything", with an instrument

Driver `/tmp/ve3/item6.py`: a PATH instrument of logging wrappers for `ip`, `iptables`, `curl`, `mkdir`, `python3` (any namespace
access, directory, canary or bundle write) and for the pure `sha256sum`, `cut` (`egress_ns_host_ip`), every row through the REAL
collector with a namespace that does not exist. A refusal must be exit 64 + its exact text + NO effectful call + no evidence root.
Rows: the builder's 23 `_A_REFUSALS` (imported, not retyped) and 27 of mine.

````
$ /root/venv-agent-factory/bin/python -B /tmp/ve3/item6.py        (09:34:41Z)
OK  empty-argument · leading-comma · trailing-comma · doubled-comma · leading-zero-port · overflow · bad-second-entry · path-with-space
    · path-64-chars · path-non-ascii · path-query · path-only · listed-twice · listed-twice-other-path · blocked-with-a-path
    · blocked-leading-zero · blocked-explicit-in-set · default-blocked-65536 · order-3-before-5-and-6 · order-5-before-6
    · order-default-5-before-6                                                  rc=64 REFUSED, no effect  effects=[] pure-calls=[]
OK  blocked-default-in-set · order-6-last                                       rc=64 REFUSED, no effect  effects=[] pure-calls=['cut', 'sha256sum']
OK  path-double-slash-ok? "…:80//" · path-dotdot-ok? "…:80/.." · path-63-exact  rc=3 VALID (reaches the namespace)
      effects=['ip netns exec ve3-item6-nonexistent iptables -L OUTPUT -v -n -x'] pure-calls=['cut', 'sha256sum']
OK  path-64 · path-percent "/%2e%2e" · path-hash · path-at · path-colon · path-plus · path-backslash · path-tab · path-newline
    · path-fullwidth-slash (U+FF0F) · path-injection "/$(touch …/INJECTED)" · dup-then-bad · bad-then-dup · three-bad-args · 5-and-6-bad
    · blocked-in-set-then-bad-venue · blocked-leading-space · blocked-65536 · one-comma "," · entry-only-slash "/"
                                                                                rc=64 REFUSED, no effect  effects=[] pure-calls=[]
OK  default-in-set-then-bad-venue · venue-empty · venue-PC-upper · venue-pc-space   rc=64 REFUSED, no effect  effects=[] pure-calls=['cut', 'sha256sum']
rows=50 bad=0 | injected file exists: False
````

A holds: every one of the 47 refusal rows exits 64 with its exact text before any effectful call and leaves no evidence root; the
order is 3 → 5 → 6 on every combined row. The only calls before a refusal are the pure `sha256sum`/`cut` of `egress_ns_host_ip`
(RC:59, the DEFAULT blocked entry), which, with the `$((first_port + 1))` beside it, run BEFORE argument 6 is validated — on a port
the rule already accepted (no side effect; INFO, Finding F16). Paths: the 63-character bound holds (63 valid, 64 refused); the
character set is exactly `[A-Za-z0-9._~/-]` (13 near-miss characters refused); `//` and `/..` are GRAMMATICAL (RC:40 `PROBE_PATH_RE` admits `.` and
`/`) — and C0 then does not ask what it records:

````
record path='/..'                            http_status=200 rc=0 | the server saw: '/'
record path='/./api/health'                  http_status=200 rc=0 | the server saw: '/api/health'
record path='/x/../api/health'               http_status=200 rc=0 | the server saw: '/api/health'
record path='/v1/models/../../api/health'    http_status=200 rc=0 | the server saw: '/api/health'
record path='/api//health'                   http_status=200 rc=0 | the server saw: '/api//health'
````

(curl 8.5 removes dot segments; the `//` row's `/` came from my Python listener's own normalisation, not curl.) The record's `path`
(CAN:15) is the argument, not the request, whenever the path holds a dot segment. The runner's two constants hold none (PC:81-82 `RELAY_PROBE_PATH`),
so no production call reaches it (Finding F9).

## 7. E3-b P and C — the checker (REAL checker CLI on copies of the committed sandbox mechanism bundle)

Driver `/tmp/ve3/item7.py` (the fixture's one entry is `10.201.136.1:12800`):

````
baseline (unmutated copy)                      rc=0 | PASS
P: C0 records path '/v1/models' (not R1's)     rc=0 | PASS
P: C0 records path 42 (an int)                 rc=0 | PASS
C: allowed [e, e], one C0, duplicate rules     rc=0 | PASS
C: allowed [e, e], one C0, rules unchanged     rc=1 | "egress-rules-unpinned: curl rules are not the pinned allow-list for ['10.201.136.1:12800', '10.201.136.1:12800"
C: allowed [e, e], two C0 for e                rc=1 | 'positive-control-failed: curl'
C: allowed [20128] + C0 target 20128           rc=1 | '' | stderr: "TypeError: expected string or bytes-like object, got 'int'"
C: allowed [True] + C0 target True             rc=1 | '' | stderr: "TypeError: expected string or bytes-like object, got 'bool'"
C: allowed [1.5] / [[e]] / [{e}] + same target rc=1 | '' | stderr: "TypeError: expected string or bytes-like object, got 'float' / 'list' / 'dict'"
C: allowed [None] + C0 target None             rc=1 | 'gate-manifest-invalid: allow entry None is not <ipv4>:<port>'
C: allowed [0] + C0 target 0                   rc=1 | 'gate-manifest-invalid: allow entry 0 is not <ipv4>:<port>'
C: C0 target with a trailing space / the path appended   rc=1 | 'positive-control-failed: curl'
C0 rc false / rc 0.0 / rc -0.0                 rc=0 | PASS
C0 rc '0'                                      rc=1 | 'positive-control-failed: curl'
C0 http_status true / 200.0 / '200'            rc=1 | 'positive-control-failed: curl'
C0 status 'run '                               rc=1 | "evidence-invalid: curl canary C0 status='run '"
C0 http_status 299 → PASS · 300, 199, absent → rc=1 'positive-control-failed: curl'
````

- **P**: nothing asserts `path` — the checker by contract (E3-b P: "The checker never grades `path`"), and the runner never reads the
  record's `path` back after the collector (PC:506-507 `EVIDENCE_ROOT`). A C0 on another path of the right ip:port proves the same thing S0-05 claims
  (the namespace REACHES that ip:port, declared limit 6), so a wrong path does not weaken the containment verdict; D-051/R1 put the
  path in the record for a READER. Consistent with the contract; no finding beyond F9.
- **C, duplicates**: `allowed: [e, e]` with ONE C0 and the rules a duplicate-accepting producer builds PASSES (`targets.count(e) == 1`
  holds for each copy, C:296 `targets`). No phase refuses the duplicate; the collector refuses it (`listed twice`, RC:49) and `egress_ns_create`
  accepts it. The letter of C ("every allowed entry exactly once") is met by a list with a repeated entry (Finding F6, follow-up).
- **C, a non-string entry**: `_split_ip_port` (C:207 `IPV4_PORT`) crashes on int/bool/float/list/dict with a traceback and no reason line (exit 1,
  so never a pass) — the E3-b report's adjacent defect, reproduced; `None` and `0` read clean refusals (`entry or ""`) (Finding F10).
- **C0 `rc: false` / `0.0` / `-0.0` PASS** — `c0_proves` compares `record.get("rc") != 0` (C:280) without `_is_int`, while the
  http status IS type-checked. This is the PIN's own predicate (148e38d: `record["rc"] != 0 or not _is_int(status)`), which E3-b
  kept by contract ("today's predicate"); only a hand-written bundle carries it (`_emit.sh:21` writes `int(rc)`). So the refusal of
  the class is NOT in the frozen contract: a follow-up in the AF-AP-26 class (Finding F4).

## 8. E3-b R1/R2 — the preflight's split between `not-2xx` and `unreachable` (REAL runner, hermes-acp)

Driver `/tmp/ve3/item8.py` + `/tmp/ve3/rawsrv.py`: one raw-socket server behaviour per run; the stand-in exits at once after
startup, so a PASSING preflight reads `launch exited within the settle window`; beside it, what the SAME canary records outside
any namespace for that behaviour.

````
code-204           canary record: rc=0 http_status=204 | preflight -> PASSED (unit launched)
code-299           canary record: rc=0 http_status=299 | preflight -> PASSED (unit launched)
103-then-200       canary record: rc=0 http_status=200 | preflight -> PASSED (unit launched)
http10-no-length   canary record: rc=0 http_status=200 | preflight -> PASSED (unit launched)
code-199           canary record: rc=1 http_status=199 | preflight -> positive control unreachable: 10.201.107.1:18505 not reachable from s0-05-hermes-acp
100-then-close     canary record: rc=52 http_status=100 | preflight -> positive control unreachable: 10.201.107.1:18506 not reachable from s0-05-hermes-acp
code-300           canary record: rc=0 http_status=300 | preflight -> positive control not 2xx: 10.201.107.1:18507/api/health answered HTTP 300 from s0-05-hermes-acp
301-location       canary record: rc=0 http_status=301 | preflight -> positive control not 2xx: 10.201.107.1:18508/api/health answered HTTP 301 from s0-05-hermes-acp
302-no-location    canary record: rc=0 http_status=302 | preflight -> positive control not 2xx: …/api/health answered HTTP 302 …
code-304 / 404 / 599 / 999                      rc=0 | preflight -> positive control not 2xx: … answered HTTP 304 / 404 / 599 / 999 …
status-000         canary record: rc=1 http_status=0 | preflight -> positive control unreachable: …
truncated-200      canary record: rc=18 http_status=200 | preflight -> positive control unreachable: 10.201.107.1:18515 not reachable from s0-05-hermes-acp
slow-200           canary record: rc=28 http_status=200 | preflight -> positive control unreachable: 10.201.107.1:18516 not reachable from s0-05-hermes-acp | 8.6s
garbage / http09 / reset   rc=1 / 1 / 56, http_status=0 | preflight -> positive control unreachable: …
(every run: census of s0-05-hermes-acp CLEAN)
````

The scratch-tree half (`/tmp/ve3/item8b.py`: ONE malformation per scratch copy of the tree, its own runner, a working 200 service):

````
emit-syntax-error        runner rc=2 | row: None | stderr: ['…/_emit.sh: line 24: unexpected EOF while looking for matching `"\'', "run_s0_05_units: cannot read the canaries' scrub list (canaries/_emit.sh)"]
emit-empty-scrub-list    runner rc=2 | row: None | stderr: ["run_s0_05_units: cannot read the canaries' scrub list (canaries/_emit.sh)"]
emit-prints-twice        runner rc=1 | row: 'positive control unreachable: 10.201.107.1:18561 not reachable from s0-05-hermes-acp'
emit-prints-nothing      runner rc=1 | row: 'positive control unreachable: 10.201.107.1:18561 not reachable from s0-05-hermes-acp'
checker-syntax-error     runner rc=1 | row: 'positive control unreachable: …' | stderr: ['Traceback (most recent call last):', …]
checker-no-c0_proves     runner rc=1 | row: 'positive control unreachable: …' | stderr: [… "AttributeError: module 'check_egress' has no attribute 'c0_proves'"]
````

Every path fails closed: nothing outside 2xx with curl rc 0 ever launches a unit, and a 3xx is graded as itself (curl never
follows: no `-L` in CAN:11). The `not-2xx`/`unreachable` split is exactly `rc == 0 and an int status > 0 outside 2xx` (PC:292-296).
The operator text names the WRONG cause whenever the service answered but curl's rc was not 0 (a 1xx final, a truncated or slow
200) or the grading itself broke (a record printed twice or not at all, a checker that does not import). Each reads
`positive control unreachable` and PC:427-428 `egress_ns_host_ip` then tells the operator to rebind a service that WAS reached. E3-b declared this reading
(its DISCREPANCY 4); the contract names two shapes only. Follow-up (Finding F14). A malformed `_emit.sh` stops at startup with
the right cause (PC:275-276 `EGRESS_SCRUBBED_ENV`).

## 9. E3-b R3 + C6's new default blocked port (a REAL two-entry pair run)

Driver `/tmp/ve3/item9.py` (compiled pair stand-in; the relay on the host's 127.0.0.1:3999 only; a real-shaped OmniRoute; a HOST
listener on 0.0.0.0:4000 = the pair's new C6 default, the FIRST entry's port + 1):

````
--- real pair leg + a host listener on 0.0.0.0:4000: runner rc=1 row={'unit': 'buzz-acp', 'status': 'run', 'note': 'contained live unit'}
  gate.json allowed: ['10.201.219.1:3999', '10.201.219.1:18601'] | rule pin: gate-fired: buzz-acp OUTPUT policy DROP 0 -> 10 packets
  C0: [('10.201.219.1:3999', '/health', 0, 200), ('10.201.219.1:18601', '/api/health', 0, 200)]
  C6: {'target': '10.201.219.1:4000', 'rc': 28, 'detail': 'curl: (28) Failed to connect to 10.201.219.1 port 4000 after 5002 ms: Timeout was reached'} | denial grade: 11 denials passed
  the host listener on :4000 saw: ''
  checker first line: ['units-manifest-invalid: buzz-acp override present']
--- collision: OmniRoute port 4000 (= relay port + 1): runner rc=1 row={'unit': 'buzz-acp', 'status': 'run', 'note': 'contained live unit'}
  collector stderr: ["run_canaries: blocked entry '10.201.219.1:4000' is in the allowed set"]
  NO gate.json in ['scratch', 'unit-identity.json']
  checker first line: ['evidence-missing: buzz-acp gate.json absent at /tmp/ve3/i9-lrqaoasi/evidence/buzz-acp/gate.json']
(both runs: census CLEAN, no nat rule)
````

R3 holds: the collector received the whole list in the runner's order (PC:505-506), gate.json `allowed` = [relay, OmniRoute], and the
rule pin passes on the real bundle (`check_runtime_and_rules`). C6's default `<host ip>:4000` cannot be reached by the namespace
whatever listens there: the namespace's OUTPUT policy drops it (rc 28, the gate's own timeout) and the host listener saw no packet,
so a real PC service on :4000 cannot turn C6 into a pass or a false fail while the gate is on (UNSURE only in that nothing on the PC
was probed: no bridge in this lane). A collision with an ALLOWED port (an OmniRoute port of 4000) is refused by the collector's
blocked-in-set rule (RC:61 `ALLOWED`) — the leg fails closed, but the runner's row still reads `run|contained live unit` (Finding F5 again).

## 10. E3-b R4 — stops (REAL runner; the runner in its own session, pgid = pid; signals to the PID or to the process group)

Driver `/tmp/ve3/item10.py`. Phase markers: create = a PATH `ip` hold on the veth add (3 s, marker); preflight = a server that
delays its 200 by 3 s (the request logged); launch = the stand-in's record; canaries = the first line of `canaries.jsonl`; teardown =
a PATH `ip` hold on `link del <host if>` after the unit ran. Each row: rc, stop latency (first signal → exit), `units.json`,
`s0-01-census.json`, the checker, then the census, nat, `route_localnet` and the stand-in's liveness.

````
TERM pid during create      rc=143 stop=3.17s units.json=False census-file=False checker=False  after: CLEAN nat=[] route_localnet=None unit-alive=[]
TERM pgroup during create   rc=143 stop=0.05s  … all False … CLEAN
INT pid during create       rc=130 stop=3.19s  … CLEAN          INT pgroup during create     rc=130 stop=0.05s … CLEAN
TERM pid during preflight   rc=143 stop=3.10s  … CLEAN          TERM pgroup during preflight rc=143 stop=0.06s … CLEAN
INT pid during preflight    rc=130 stop=3.08s  … CLEAN          INT pgroup during preflight  rc=130 stop=0.07s … CLEAN
TERM pid during launch      rc=143 stop=1.01s  … CLEAN          TERM pgroup during launch    rc=143 stop=0.13s … CLEAN
INT pid during launch       rc=130 stop=0.99s  … CLEAN          INT pgroup during launch     rc=130 stop=0.12s … CLEAN
TERM pid during canaries    rc=143 stop=6.16s  … CLEAN          TERM pgroup during canaries  rc=143 stop=0.08s … CLEAN
INT pid during canaries     rc=130 stop=6.47s  … CLEAN          INT pgroup during canaries   rc=130 stop=0.14s … CLEAN
TERM pid during teardown    rc=143 stop=3.07s  … CLEAN          TERM pgroup during teardown  rc=143 stop=0.09s … CLEAN
INT pid during teardown     rc=130 stop=3.06s  … CLEAN          INT pgroup during teardown   rc=130 stop=0.08s … CLEAN
(every row: units.json=False census-file=False checker=False; CLEAN = {'netns': False, 'veth': False, 'etc_netns': False, 'owner_dir': []})
````

R4 holds for ONE signal, in all 20 combinations. Stop latency: bash defers the trap while a foreground child runs, so a PID-directed
stop waits for that child (the 3 s holds; about 1 s in the settle loop's `sleep 1`, PC:479-482; 6.2-6.5 s in the canary window, where
the collector finishes the whole suite and WRITES its bundle before the runner exits — a complete, checker-shaped bundle with no
`units.json` beside it: INFO, Finding F17). A group signal stops in 0.05-0.14 s.

### A SECOND signal while `cleanup` runs: it does not re-enter `cleanup`, it ABORTS it

`cleanup` runs from `trap cleanup EXIT` (PC:334), while `trap 'exit 130' INT` and `trap 'exit 143' TERM` (PC:335-336) stay armed
inside it. When a trap handler calls `exit` inside the EXIT trap, bash abandons the rest of the EXIT trap. Measured three ways:

````
(a) the operator's double Ctrl-C, NO shim, a default unit: SIGINT to the group, then again +0.05 s
INT pgroup, canary window, then INT pgroup +0.05s (default unit) rc=130 stop=0.06s units.json=False census-file=False checker=False
    after: {'netns': True, 'veth': False, 'etc_netns': True, 'owner_dir': ['s0-05-hermes-acp.owner']} nat=[] route_localnet=None unit-alive=[]
(+0.15 s and +0.30 s: CLEAN — the window is as long as cleanup; the stand-in dies at once)

(b) deterministic: a unit whose SIGTERM handler takes 3 s (a unit that is slow to shut down); the 2nd signal fires when the unit
    received cleanup's SIGTERM (a marker it writes)
    [second signal fires: the unit got TERM from cleanup = True ]
TERM pid (launch window) + TERM pid inside cleanup   rc=143 stop=3.99s units.json=False census-file=False checker=False
    after: {'netns': True, 'veth': True, 'etc_netns': True, 'owner_dir': ['s0-05-hermes-acp.owner']} nat=[] route_localnet=0 unit-alive=[]
TERM pid (canary window) + INT pid inside cleanup    rc=130 stop=9.09s units.json=False census-file=False checker=False
    after: {'netns': True, 'veth': True, 'etc_netns': True, 'owner_dir': ['s0-05-hermes-acp.owner']} nat=[] route_localnet=0 unit-alive=[]
control: ONE TERM pid (launch window), slow unit     rc=143 stop=4.03s … after: {'netns': False, 'veth': False, 'etc_netns': False, 'owner_dir': []}

(c) the PAIR: a PATH `iptables` hold (2 s, timing only) on the teardown's `-t nat -D`; the 2nd signal fires inside that removal
    [second signal fires inside the relay-reach removal = True | nat now: ['-A PREROUTING -d 10.201.219.1/32 -i ehda7d8593 -p tcp -m tcp --dport 3999 -j DNAT --to-destination 127.0.0.1:3999'] ]
PAIR: TERM pid (launch) + TERM pid inside the nat -D     rc=143 stop=3.05s units.json=False census-file=False checker=False
    after: {'netns': True, 'veth': True, 'etc_netns': True, 'owner_dir': ['s0-05-buzz-acp.owner']} nat=[] route_localnet=1
PAIR: TERM pid (launch) + TERM pgroup inside the nat -D  rc=143 stop=1.02s units.json=False census-file=False checker=False
    after: {'netns': True, 'veth': True, 'etc_netns': True, 'owner_dir': ['s0-05-buzz-acp.owner']} nat=['-A PREROUTING -d 10.201.219.1/32 -i ehda7d8593 -p tcp -m tcp --dport 3999 -j DNAT --to-destination 127.0.0.1:3999'] route_localnet=1
````

(After each row my driver killed any stand-in by PID and destroyed the name by NAME; the census after every batch read CLEAN.) A
diagnostic leg confirmed the units share the runner's process group and do not ignore SIGINT (`SigIgn=0000000001001000`: SIGPIPE and
SIGXFSZ only), so a group signal kills them; the stand-in pids my driver listed as alive right after exit (c) died within
milliseconds (my own kill found one gone) — I claim NO live unit. What a double stop does leave, after the runner has exited
with 143/130: the namespace, its veth, `/etc/netns/<ns>`, an owner record naming the DEAD runner (reaped only by the next create or
destroy of that name), and — for the pair — `route_localnet=1` on the leftover host interface and, when the second signal reaches
the process group inside the removal, D-051's DNAT rule to the loopback relay itself (Finding F3).

## 11. The declared limits (E3 + E3-b): true? written where an operator reads them?

The operator reads the runner's header, `# DECLARED LIMITS` (PC:35-54), and the builders' recipes (E3 report §8, E3-b report §8).

| Limit (PC line) | True? (measured here) | Where an operator reads it |
|---|---|---|
| 1 canaries share the namespace, not the unit's sockets (PC:36 `namespace`) | TRUE: every canary runs through `egress_ns_run` (RC:83) | header |
| 2 no route/NAT out; ONE DNAT + `route_localnet` for the pair's leg; "`egress_ns_destroy` removes both, at the leg's teardown and in `cleanup`" (PC:39-44) | TRUE for every single stop and every failure point (sections 4, 10); FALSE after a DOUBLE stop: the rule and `route_localnet=1` outlive the run (F3) | header |
| 3 a wrong identity file "only fails the pair's C0 / relay handshake" (PC:45-46) | HALF: C0 is an unauthenticated GET of `/health` (CAN:11) and never carries the key, so a wrong key cannot fail C0; it fails (or not) at the pair's own relay handshake, which S0-05 does not grade (limit 1) | header |
| 4 `unit-identity.json` is unkeyed, "not against a forger with root" (PC:47-48, C:49-50) | TRUE, and it UNDERSTATES: a forger needs no root when the evidence root's parent is writable by the unit user — the E3 recipe's `EV=/home/rocco/s0-05-evidence/<stamp>` (E3 report line 406) sits in the unit user's home, and that user can replace a root-made evidence directory: `RENAME+REPLACE-OK` below (F15) | header + checker docstring |
| 5 the probe paths are PC facts; a moved path fails closed as `not 2xx` (PC:49-51) | TRUE: 3xx/4xx/5xx on the probe path read `not-2xx` and launch nothing (section 8) | header |
| 6 a health 2xx proves reach, not the model API, nor the instance (PC:52-54 `namespace`) | TRUE | header |
| X3 three creators out of model (L:157-159 `microseconds`) | TRUE that it breaks; the text understates window and effect (F8) | the LIBRARY only, not the runner header |
| (undeclared) a SIGKILLed runner leaves its namespaces (E3 report §11.3) | TRUE by construction (no trap runs) | the E3 REPORT only |
| (undeclared) a second stop during `cleanup` aborts it (section 10) | measured | nowhere (F3) |
| (undeclared) a PID-directed stop waits for the current foreground child (up to the whole canary suite) | measured, 6.2-6.5 s in the sandbox (section 10) | nowhere (INFO) |

````
$ as root: mkdir <nobody-owned dir>/ev (root 0755) ; then as uid 65534: mv ev ev.moved-by-unit-user && mkdir ev && write ev/units.json
drwxr-xr-x 3 nobody nogroup 4096 Sep 23 09:57 /tmp/ve3/own65534
drwxr-xr-x 2 root   root    4096 Sep 23 09:57 /tmp/ve3/own65534/ev
RENAME+REPLACE-OK
drwxr-xr-x 2 nobody nogroup 4096 Sep 23 09:57 ev
drwxr-xr-x 2 root   root    4096 Sep 23 09:57 ev.moved-by-unit-user
{"units": []} forged by uid 65534
````

## 12. Mutation audit (scratch copies only: `/tmp/ve3/base` = the builder's 51 inputs, the eight seam files `cmp`-identical to the repo)

Harness `/tmp/ve3/mut.py` + `/tmp/ve3/mutrun.py`: ONE exact replacement per mutant (refused unless the old text occurs exactly once —
all 36 checked: `mutants: 36 | old-text occurrence problems: []`), `bash -n` / `py_compile`, the WHOLE file collected (`251 tests
collected` required), then the named killers with `-x`; KILLED = rc 1 with a FAILED killer; SURVIVED = rc 0. The shared tree was
never mutated. AF-AP-138 first — every killer selection on the UNMUTATED base:

````
$ /root/venv-agent-factory/bin/python -B /tmp/ve3/mutrun.py baseline        (09:59:32Z)
UNMUTATED base, every killer selection: rc=0 | 112 passed, 139 deselected in 136.71s (0:02:16) | failed=[]
collect on the base: 251 tests collected in 0.38s
````

| Mutant | What it does | Compiles | Collected | Killed by (first FAILED) / verdict |
|---|---|---|---|---|
| B1 | gate.json records only the first entry (RC:166 `rules_sha256`) | bash -n rc=0 | 251 | `test_d_pair_leg_reaches_the_relay_through_the_dnat` |
| B2 | C0 only for the first entry (RC:116 `ALLOWED`) | bash -n rc=0 | 251 | `test_d_pair_leg_reaches_the_relay_through_the_dnat` |
| B3 | the path not passed to C0 (RC:117 `c0_allowed_target`) | bash -n rc=0 | 251 | `test_runner_live_leg` |
| B4 | the collector's validation removed (RC:46 `egress_allow_entry_ok` → `if false`) | bash -n rc=0 | 251 | `test_e3b_a_a_bad_argument_is_refused_before_anything[empty-argument]` |
| B5 | the duplicate refusal removed (RC:49 `ALLOWED`) | bash -n rc=0 | 251 | `...[listed-twice]` |
| B6 | the blocked-in-set refusal removed (RC:61 `ALLOWED`) | bash -n rc=0 | 251 | `...[blocked-explicit-in-set]` |
| B7 | "nothing else" removed (C:298-299) | py_compile ok | 251 | `test_e3b_c_the_positive_control_is_per_allowed_entry[c0-target-outside-the-allow-set]` |
| B8 | "every allowed entry exactly once" removed (C:296-297 `positive`) | py_compile ok | 251 | `...[allowed-entry-without-c0]` |
| B9 | the checker's grammar back to `\d` (C:102 `IPV4_PORT`) | py_compile ok | 251 | `test_e3b_g_one_allow_entry_rule_in_the_library_and_the_checker[leading-zero-octet]` |
| B10 | the preflight passes any rc-0 HTTP answer (PC:290 `c0_proves`) | bash -n rc=0 | 251 | `test_e3b_r2_a_health_path_answering_401_launches_nothing` |
| B11 | `trap cleanup EXIT INT TERM` (PC:334-336) | bash -n rc=0 | 251 | `test_x4_runner_cleanup_reaps_its_own_namespace_at_exit` |
| B12 | the runner passes only the OmniRoute entry (PC:506 `EVIDENCE_ROOT`) | bash -n rc=0 | 251 | `test_runner_live_leg` |
| B13 | C0's `path=` removed (CAN:15) | bash -n rc=0 | 251 | `test_e3b_a_a_two_entry_run_records_the_whole_allow_set` |
| B14 | `egress_ns_create` checks only its first argument (L:96 `for entry in "$@"`) | bash -n rc=0 | 251 | `test_e3b_g_egress_ns_create_checks_every_entry_by_the_one_rule[arabic-indic-port]` |
| X1 | P's path grammar not applied (RC:46 `egress_allow_entry_ok`) | bash -n rc=0 | 251 | `...[path-with-space]` |
| X2 | the default-blocked 65536 guard removed (RC:58 `first_port`) | bash -n rc=0 | 251 | `...[default-blocked-65536]` |
| X3 | the preflight asks the canary's default path (PC:279 `c0_allowed_target`) | bash -n rc=0 | 251 | `test_runner_live_leg` |
| X4 | the venue checked before argument 3 | bash -n rc=0 | 251 | `...[order-3-before-5-and-6]` |
| N1 | X3: the loser never links the winner's record back (L:179 `owner_file`) | bash -n rc=0 | 251 | `test_x3_stale_takeover_is_atomic` |
| N2 | X3: a live owner read as stale (L:172 `kill -0` → `false`) | bash -n rc=0 | 251 | `test_create_race_one_wins` |
| N3 | X2: the rollback releases the claim even when teardown fails (L:191 `_egress_ns_rollback` `&&` → `;`) | bash -n rc=0 | 251 | **SURVIVED** (`-k 'x2_ or x4_'` → 5 passed): no test fails a rollback step (F1) |
| N5 | D: the reach removal deletes the FIRST matching rule only (L:331 `removed` → `break`) | bash -n rc=0 | 251 | **SURVIVED** (`-k test_d_` → 4 passed): no test holds two rules naming the interface (section 4's D6 does) |
| N7 | D: the DNAT for any destination (`-d $host_ip` dropped, L:320 `host_if`) | bash -n rc=0 | 251 | `test_d_relay_reach_add_and_del` |
| N9 | P: the path regex loses its `$` (RC:40 `PROBE_PATH_RE`) | bash -n rc=0 | 251 | `...[path-with-space]` |
| N10 | C: `c0_proves` accepts HTTP 300 (C:281 `status` `<` → `<=`) | py_compile ok | 251 | **SURVIVED** (`-k 'positive or c0 or pass'` → 17 passed): the 2xx upper bound is unpinned |
| N11 | C: two C0 records for one entry accepted (C:296 `!= 1` → `< 1`) | py_compile ok | 251 | `...[two-c0-for-one-target]` |
| N12 | R2: the preflight without the runner's `env -u` wrapper (PC:279 `c0_allowed_target`) | bash -n rc=0 | 251 | **EQUIVALENT**: the canary itself runs `unset $EGRESS_SCRUBBED_ENV` (`_emit.sh:13`), the same list — the wrapper is redundant defence |
| N13 | R2: the preflight demands exactly 200 (stricter than `c0_proves`) | bash -n rc=0 | 251 | **SURVIVED** (3 passed): no stand-in answers a non-200 2xx through the preflight (section 8 measured 204/299 pass on the real bytes) |
| N15 | R4: SIGINT exits 143 | bash -n rc=0 | 251 | `test_e3b_r4_sigint_stops_the_runner_with_130` |
| N17 | A5: the unit's HOME inherited from the runner (PC:460) | bash -n rc=0 | 251 | `test_runner_live_leg` |
| N18 | A6: the identity file's OTHER bits unchecked (PC:198 `ID_REFUSED` `077` → `070`) | bash -n rc=0 | 251 | **SURVIVED** (`test_a6_identity_file_refusals` → 7 passed): the mode case is 0644 only; section 3 measured 0604 refused on the real bytes |
| N19 | A7: the checker checks only the real uid (C:404 `0 in uid`) | py_compile ok | 251 | `test_a7_the_checker_refuses_an_identity_that_is_not_the_pin[effective-uid-0]` |
| N20 | A2: the census compares keys only (PC:527 `changed`) | bash -n rc=0 | 251 | `test_a2_s0_01_tree_change_fails_the_leg` |
| N21 | C6's default is port + 2 (RC:59 `egress_ns_host_ip`) | bash -n rc=0 | 251 | `...[blocked-default-in-set]` |
| N22 | G: the library accepts port 65536 (L:82 `port_re`) | bash -n rc=0 | 251 | `test_x1_port_is_digit_bounded_before_any_arithmetic[port-65536]` |
| N25 | A: the venue checked before argument 5 | bash -n rc=0 | 251 | `...[order-5-before-6]` |

Tally: the builders' 18 (B1-B14, X1-X4): **18 KILLED** on the final bytes. Mine, 18 new: **12 KILLED, 5 SURVIVED (N3, N5, N10, N13,
N18), 1 EQUIVALENT (N12)**. A first N5 (`while`→`if`) failed `bash -n` and was refused before any run (AF-AP-78's gate). Each
survivor is a behaviour the real bytes get RIGHT (measured in sections 2-8) that no committed test pins (Finding F20).

The two blocker candidates' discriminators, as REPAIR copies (scratch, not counted as mutants), through the SAME reproductions:

````
FIX-F3 = `cleanup() {` + `trap '' INT TERM` (PC:322): bash -n rc=0 251 tests collected in 0.41s
REPO (defective): TERM pid + TERM pid inside cleanup   rc=143 after: {'netns': True, 'veth': True, 'etc_netns': True, 'owner_dir': ['s0-05-hermes-acp.owner']} nat=[] route_localnet=0
REPO (defective): PAIR TERM pid + TERM pgroup in the nat -D   rc=143 after: {'netns': True, 'veth': True, 'etc_netns': True, 'owner_dir': ['s0-05-buzz-acp.owner']} nat=['-A PREROUTING -d 10.201.219.1/32 -i ehda7d8593 -p tcp -m tcp --dport 3999 -j DNAT --to-destination 127.0.0.1:3999'] route_localnet=1
FIX-F3 (corrected): TERM pid + TERM pid inside cleanup   rc=143 after: {'netns': False, 'veth': False, 'etc_netns': False, 'owner_dir': []} nat=[] route_localnet=None
FIX-F3 (corrected): PAIR TERM pid + TERM pgroup in the nat -D   rc=143 after: {'netns': False, 'veth': False, 'etc_netns': False, 'owner_dir': []} nat=[] route_localnet=None
FIX-F1 = `_egress_ns_teardown` returns 1 while /run/netns/<ns> or /etc/netns/<ns> still exists (L:401-402 `rm -rf "/etc/netns/$ns"`): bash -n rc=0 251 tests collected in 0.37s
REPO (defective)     rollback-step fault netnsdel : census AFTER the runner exited: {'netns': True, 'veth': False, 'etc_netns': False, 'owner_dir': []}
FIX-F1 (corrected)   rollback-step fault netnsdel : census AFTER the runner exited: {'netns': False, 'veth': False, 'etc_netns': False, 'owner_dir': []}
REPO (defective)     rollback-step fault etcrm    : census AFTER the runner exited: {'netns': False, 'veth': False, 'etc_netns': True, 'owner_dir': []}
FIX-F1 (corrected)   rollback-step fault etcrm    : census AFTER the runner exited: {'netns': False, 'veth': False, 'etc_netns': False, 'owner_dir': []}
````

(`trap '' INT TERM` also covers a signal to the whole group, because every command `cleanup` starts inherits the ignored dispositions.)

## 13. AF-AP-115, and anything else

- **The test file**: every `shutil.which` (T:96, T:635, T:1252, T:1555, T:2312, T:2465, T:2773) is test-side — capability probes and
  the REAL binary a shim `exec`s. No trust decision rests on them. The landing commit's body (76f439f) does not mention
  AF-AP-115; `scripts/ap_screen.py --tests` flags no AF-AP-115 row today.
- **The production path DOES resolve from the caller's `PATH`**: the root runner takes `SETPRIV_BIN=$(command -v setpriv)`,
  `ENV_BIN`, `IP_BIN`, `PY_BIN` (PC:72-73), and the library calls `ip`, `iptables`, `sysctl`, `sha256sum`, `ln`, `mv`, `kill`, `ps` by
  bare name, as does `_unit_identity`'s `subprocess.run(["ip", ...])` (PC:251 `capture_output`). `setpriv` is the A4 privilege drop itself: section
  4's D3 ran the real runner with a PATH `setpriv` that never drops, and the unit ran as uid 0 for the whole settle window (31.5 s)
  before A7 refused it (`unit identity not observed: uid 0`). This is the AF-AP-115 class in production. But the E3 contract PRESCRIBES
  PATH shims as its test seam (E3 brief, "Test-seam rule"), and the PC invocation is `sudo` (Fedora's `secure_path`: root-owned
  dirs). So it is not in the frozen contract, and it is not a blocker (Finding F18).
- **A stopped or failed run leaves checker-shaped evidence and marks nothing** (`/tmp/ve3`, reuse probe):

````
run 1 rc 1 | units.json written | bundle: ['canaries.jsonl', 'gate.json', 'runtime.json', 'scratch', 'unit-identity.json']
run 2 stopped rc 143 | units.json still present: True | unchanged (run 1's): True
the evidence root now: ['hermes-acp', 'hermes-acp.launch.log', 's0-01-census.json', 'units.json'] | hermes-acp: ['canaries.jsonl', 'gate.json', 'runtime.json', 'scratch', 'unit-identity.json']
the checker on this mixed root: 1 ['units-manifest-invalid: hermes-acp override present']
````

  R4's "no units.json" holds for the stopped run, but the runner neither refuses a non-empty evidence root nor stamps a run id, so
  a reused root keeps an earlier run's manifest beside the stopped run's leftovers. A PID-directed stop in the canary window also
  lets the collector finish and write a complete bundle with no manifest (section 10) (Finding F17; E3-b's recipe says "start again
  from a fresh `$EV`": a procedure, not a check).
- **The runner never reads the collector's exit status** (PC:506-507 `EVIDENCE_ROOT`): a collector that refused its arguments (section 9, collision)
  or lost its instrument (section 4, D4: exit 3) still produces `"status": "run", "note": "contained live unit"`; the checker then
  fails closed with `evidence-missing: … gate.json absent` (Finding F5).
- **E3's own DISCREPANCY 4 reproduced**: a pair refused after launch (D2, D3) reads `unit-declared-absent-but-present: buzz-acp`
  as the checker's first line, not the unit's reason (fail closed; the coordinator's open call) (Finding F21).
- **Static only (UNVERIFIED)**: an override value holding a NUL (`"\u0000"` is valid JSON; PC:112 `OVERRIDABLE` accepts any non-empty string)
  shifts the NUL-delimited key/value stream the runner reads back (PC:145-152 `PAIR_ARGV`); by my reading the misalignment ends in `set -u`'s
  `unbound variable` at PC:154 `OVERRIDE` (fail closed), and the override is a test-only input ("LEAVE IT UNSET ON THE PC") (Finding F22).
  A create whose subshell is killed between `ln` and `rm -f "$tmp"` (L:169) would leave a `.<ns>.owner.<pid>.<n>` temp that
  `_egress_ns_release` (L:194-197) never removes; I did not reproduce the window (Finding F23).

## Findings inventory (no severity filter; ranked; the blocking predicate applied to each)

Predicate columns: (1) contract-mapped · (2) reproduced through the real production path · (3) materially effective · (4) a concrete
discriminator · (5) inside the landed boundary. Evidence: VERIFIED = reproduced in this lane; STATIC = read only.

**F3 — BLOCKER. A second SIGINT/SIGTERM while `cleanup` runs aborts it: the namespace, its veth, `/etc/netns/<ns>`, an owner record
naming the dead runner and, for the pair, `route_localnet=1` and D-051's DNAT to the loopback relay outlive the run.**
VERIFIED (section 10). Mechanism: `trap 'exit 130' INT` / `trap 'exit 143' TERM` (PC:335-336) stay armed inside `trap cleanup EXIT`
(PC:334); bash abandons an EXIT trap when a handler calls `exit` inside it, so `cleanup` (PC:322-330) stops wherever it is.
(1) YES — E3 Part D: "removes the rule explicitly in the leg's teardown AND in `cleanup` ... and the census reads no PREROUTING rule
naming that interface afterwards"; E3 X4: "a namespace owned by this runner is destroyed at exit"; E3-b R4 + its test line "SIGTERM
mid-leg: exit 143 ... census clean"; D-051: the reach exists "for this leg only". (2) YES — the real runner and library: an operator's
double Ctrl-C with NO shim and a default unit (SIGINT to the group twice, 0.05 s apart) left the namespace; deterministic with a unit
that takes 3 s to stop (the second signal on its marker) and with a 2 s PATH `iptables` hold (timing only, the contract's own seam) on
the pair. (3) YES — host state the contract says is gone after a stop, including the owner-authorized leg-scoped DNAT and
`route_localnet=1`, persists until the next create of that name. The E3-b report §8 tells the operator that after exit 143/130 "the
runner's own namespaces, relay reach ... [are] gone". The window is as long as `cleanup`, up to about 7 s when a unit is slow to die (L:356-385). (4) YES — FIX-F3 (`trap '' INT TERM` as `cleanup`'s first line) turns all
four reproductions clean (section 12). (5) YES — the runner's traps are E3-b R4's lines. Suggested repair: that one line (its
children inherit the ignore, which also covers a group signal) + a test that fires a second signal inside `cleanup` (the
stand-in's marker pattern above) and asserts the census and the nat rules afterwards.

**F2 — CONTRACT-DEFECT (returned for an explicit amendment; not a builder repair). A2's census cannot see the harm it was written
for: in-place writes inside `.markers` and `v2-*` leave `s0-01-census.json` at `"changed": []`.** VERIFIED (section 3, A2). The
runner implements the frozen letter (a `stat` census of `.markers` and each `v2-*` DIRECTORY, PC:210-228), and that letter is blind
to a rewrite of an existing file (`.markers/buzz-acp.pid`, `.markers/current-framedir` — CD1's own named harms), an append to a frame
file, or a file one directory down; the unit user owns the tree on the PC. The record then certifies an unchanged S0-01 tree that
changed (evidence falsified), and the runner proceeds to its checker. Amendment options for the coordinator: census every entry under
`.markers` recursively (lstat + sha256 of regular files), or narrow A2's claim to "directory metadata" in the declared limits.

**F1 — FOLLOW-UP (the materiality condition is where I stop; UNSURE for the coordinator). A rollback step that itself fails leaves an
UNOWNED leftover that the runner's `cleanup` does not reap.** VERIFIED (section 2, X2 through the real runner). (1) YES — X2: "a
leftover that create could not roll back is still reaped by `cleanup` under the ownership check"; the comment at L:188-190 claims
the same. (2) YES — the real runner, a PATH shim (the contract's seam). (4) YES — FIX-F1 turns both cases clean (section 12).
(5) YES. (3) NOT MET by itself: the trigger is a DOUBLE fault (a create step fails AND `ip netns del` or `rm -rf /etc/netns/<ns>`
fails inside the rollback, calls that practically never fail on a healthy host), and the leftover is an EMPTY namespace or file that
the next create's destroy-first removes; making the teardown verify its deletes is hardening. The comment's overclaim is real either
way. Fix: `_egress_ns_teardown` returns non-zero while `/run/netns/<ns>` or `/etc/netns/<ns>` (or the host interface) still exists
(the FIX-F1 shape), so the rollback keeps the claim; or correct the comment. Mutant N3 (the rollback always releasing) SURVIVES.

**F5 — FOLLOW-UP. The runner never reads the collector's exit status** (PC:506-507 `EVIDENCE_ROOT`): a collector that exited 3 (D4) or 64 (item 9's
collision) still yields `"status": "run", "note": "contained live unit"` in units.json. VERIFIED. Fail-closed (the checker reads
`evidence-missing: <unit> gate.json absent`); the manifest misstates the leg. Not in the contract. Fix: a non-zero collector →
`not-run|collector failed: <rc>`.

**F17 — FOLLOW-UP. A stopped or failed run leaves checker-shaped evidence and marks nothing; a reused evidence root keeps an
earlier run's `units.json`.** VERIFIED (sections 10, 13). A PID-directed stop in the canary window lets the collector finish its
bundle; R4 then writes no manifest, which on a reused root means the OLD one stays. The runner never refuses a non-empty `$EV` and
stamps no run id; E3-b's "start again from a fresh `$EV`" is procedure only. Fix: refuse a non-empty evidence root (or write a
run-id stamp the checker requires to match units.json).

**F15 — FOLLOW-UP. The evidence can be replaced by the unit user under the E3 recipe's layout; declared limit 4 names only "a forger
with root".** VERIFIED at the permission level (section 11: `RENAME+REPLACE-OK`); the whole-leg forgery was NOT run. The recipe's
`EV=/home/rocco/s0-05-evidence/<stamp>` sits in the unit user's home. Fix: root-owned, non-group/other-writable ancestry for `$EV`
(check it at the top of the runner), or say so in limit 4 and the recipe.

**F18 — FOLLOW-UP. AF-AP-115 in production: the root runner resolves its trust-boundary executables from the caller's `PATH`**
(PC:72-73 `run_s0_05_units` `command -v setpriv/env/ip/python3`; bare `ip`/`iptables`/`sysctl` in the library; PC:251 `capture_output`). VERIFIED consequence: a PATH
`setpriv` that never drops ran the unit as uid 0 for the whole 31.5 s settle window before A7 refused it (section 4, D3). Not
contract-mapped: the E3 test-seam rule prescribes PATH shims, and `sudo`'s `secure_path` protects the PC invocation. Fix: resolve
from a fixed root-owned list and refuse a binary in a user-writable directory, with the tests' shims moved behind a recorded input
(the pin-override pattern), or declare the limit.

**F14 — FOLLOW-UP. The preflight's operator text names the wrong cause when the service DID answer but curl's rc was not 0 (a 1xx
final, a truncated or slow 200) or when grading broke (a record printed twice or not at all, a checker that does not import)**: all
read `positive control unreachable` and PC:427-428 `egress_ns_host_ip` tell the operator to rebind the service. VERIFIED (section 8). Fail-closed
everywhere; E3-b declared the reading (its DISCREPANCY 4). Fix: a third verdict (`answered HTTP <code>, curl rc <n>` / `preflight
could not grade: <detail>`).

**F20 — FOLLOW-UP (test gaps). Five mutants of mine SURVIVE (section 12)**: N3 (rollback releases on a failed teardown), N5 (the
reach removal deletes only the first rule naming the interface), N10 (`c0_proves` accepts HTTP 300), N13 (a preflight stricter than
the checker, 200 only), N18 (the identity file's other-bits unchecked). The real bytes are right on each (measured); no committed
test pins them. Fix: one row each (a second stale nat rule; a C0 at 300 and at 204 through the preflight; an identity file at 0604).

**F6 — FOLLOW-UP. Duplicate entries in gate.json `allowed` pass**: `[e, e]` with one C0 and the duplicated rules reads PASS (C:296,
`count == 1` per copy). VERIFIED (section 7). The letter of C holds; the collector refuses duplicates (RC:49 `ALLOWED`) and `egress_ns_create`
accepts them. No containment effect (the allow-set is `{e}`). Fix: `read_gate` refuses a repeated entry.

**F4 — FOLLOW-UP (AF-AP-26 class; kept by contract). `c0_proves` accepts `rc: false`, `0.0`, `-0.0`** (C:280 compares `!= 0`
without `_is_int`; the http status IS type-checked). VERIFIED. The PIN predicate did the same (148e38d), and E3-b kept "today's
predicate"; `_emit.sh:21` always writes `int(rc)`, so only a hand-written bundle carries it. Fix: `_is_int(rc) and rc == 0`.

**F10 — FOLLOW-UP (pre-existing; E3-b's own adjacent defect, reproduced). A non-string allowed entry (int, bool, float, list, dict)
with a matching C0 target crashes the checker** (`TypeError` at C:207 `IPV4_PORT`, exit 1, no reason line). VERIFIED. Fail-closed. Fix:
`read_gate` requires every entry to be a `str`.

**F11 — FOLLOW-UP. A unit gid of 0 is accepted** (`S0_05_UNIT_USER=<uid>:0`, or a gid of 4294967295 which `setpriv` reads as "no
change"): the unit runs in the root group, and A7 records only the `Uid:` line (PC:248). VERIFIED with `setpriv` directly (section 3,
A4). A4 is uid-only. No uid bypass: the launch's `--init-groups` refuses uid 4294967295 (UNSURE only on a venue with a passwd entry
for it). Fix: refuse gid 0 too and record the `Gid:` line.

**F8 — FOLLOW-UP (doc). X3's declared limit (L:157-159 `microseconds`) understates both the window and the effect**: three creators broke the claim
in 5 of 40 and 13 of 40 trials — the window spans the `mv`, `cat` and `ln` processes, not "microseconds" — and two creators
passed the claim, one rolling back the other's namespace (a creator returned rc 0 for a namespace that no longer existed). VERIFIED.
Two creators: 100 of 100 correct (the contract's case). It is also declared only in the library, not in the runner's header.

**F9 — FOLLOW-UP. The path grammar admits dot segments (RC:40 `PROBE_PATH_RE`) and C0 then records its argument, not its request**: recorded
`/v1/models/../../api/health`, asked `/api/health` (curl removes dot segments; CAN:11 has no `--path-as-is`). VERIFIED. No
production caller (PC:81-82 `RELAY_PROBE_PATH` hold none). Fix: refuse `/./` and `/../` in the grammar, or `--path-as-is`.

**F7 — FOLLOW-UP. A claim whose record cannot be linked reads `namespace-live: <ns> owned by pid  (claim churn after 10 attempts)`**
— an empty pid, the wrong reason; L:160-161 `namespace-live` says that case returns 1. VERIFIED (section 2). Fail-closed. Fix: return
1 with `claim record not writable` when `ln` fails with no record present.

**F13 — FOLLOW-UP / INFO. S0-01's `agent.env` is refused by name only**: a hard link or a byte copy of it is accepted (section 3,
A6). VERIFIED. The contract says "by name". Fix (optional): refuse a file whose (dev, inode) is S0-01's `agent.env`.

**F19 — FOLLOW-UP (doc). Declared-limit text gaps** (section 11): limit 3's "C0" (a wrong key cannot fail C0); the SIGKILL residue
and the PID-directed stop latency are undeclared in the runner header; limit 2's "removes both ... in cleanup" is false after a double
stop (F3).

**F12 — INFO.** A7's checker accepts four hand-written forgeries (uid 4294967295, duplicate keys with the last non-zero, a `unit`
field naming another unit, a pid carrying a newline that prints a `PASS: ...` line) and prints raw field values (C:396-406 `entrypoint_realpath`), so a
value with a newline splits a reason. All need a hand-written record (declared limit 4); the lines print only when `check()` passes.
**F24 — INFO.** A1: a differently spelled key (`Override`, `override `) or a deleted units.json is not an override to the checker
(C:428 `override`); A7 refuses the stand-in anyway (layered). **F16 — INFO.** The default blocked entry's `egress_ns_host_ip` and
`$((first_port + 1))` (RC:57-59) run before argument 6 is validated, on a port the rule already accepted: no side effect.
**F21 — INFO.** E3's DISCREPANCY 4 (`unit-declared-absent-but-present` first for a unit refused after launch) reproduced in D2/D3.

**F22, F23 — UNVERIFIED (static).** An override value with a NUL desynchronises PC:145-152 `PAIR_ARGV` (by my reading it ends at PC:154 `OVERRIDE`'s
`unbound variable`, fail-closed; test-only input). A create killed between `ln` and `rm -f "$tmp"` (L:169) would leave a claim temp
that `_egress_ns_release` never removes (the window was not reproduced).

## GATE RECOMMENDATION

**NOT-READY** — ONE finding meets the complete blocking predicate: **F3** (a second stop signal during `cleanup` aborts it and leaves
the namespace, the veth, `/etc/netns/<ns>`, a dead runner's owner record and, for the pair, `route_localnet=1` and D-051's DNAT on the
host). The one focused repair (D-031), keyed to S0-05 at this contract revision: `trap '' INT TERM` as the first line of `cleanup`
(PC:322) plus a regression test that fires the second signal inside `cleanup` and reads the census and the nat rules. FIX-F3 on a
scratch copy already turns all four reproductions clean. **F2 is returned as CONTRACT-DEFECT** for an explicit A2 amendment (the
census design, not the builder's code). Every other row is a follow-up (`verify-followup`, D-034); the strongest are F1, F5, F17,
F15 and F18. This recommendation rests only on what I reproduced; nothing here ran on the PC.

## NOT-done (first-class)

- NOTHING ran on the PC (no bridge use in this lane): the real units' stop behaviour (their shutdown time sets F3's window; whether
  the real buzz-acp exits on stdin EOF), anything listening on the PC at :4000, the real services' answers, `secure_path` under the
  coordinator's actual `sudo` line (F18).
- Kills were proven with named `-k` selections after a whole-file collection per mutant (the builders' method), not a whole-file
  run per mutant; the FIX-F1/FIX-F3 copies were run through the reproductions only, not the whole file.
- E3's own mutants (M14, E1-E16) were not re-run; the brief asked for E3-b's B1-B14 and X1-X4.
- Only the installed locales were exercised (`C`, `C.UTF-8`, `POSIX`); `shellcheck` is absent (not run).
- F15's whole-leg forgery, F22 and F23 were not reproduced (static or permission-level only).
- No commit, stage or push; no file outside this report was written in the repository.

## Final census (pasted) and the lint

````
$ date -u
Wed Sep 23 10:18:40 UTC 2026
$ ip netns list
(end)
$ ip -o link show type veth
(end)
$ iptables -t nat -S PREROUTING
-P PREROUTING ACCEPT
$ ls -A /etc/netns
(end)
$ ls -A /run/s0-05-egress
(end)
$ route_localnet all/default + any interface set to 1
0
0
(none)
$ processes of mine (stand-ins, listeners, raw servers, runners, collectors)
(none but this census command's own shell, which the pattern matches)
$ ls -d /tmp/ve3 /tmp/ve3nr /tmp/e3-*
ls: cannot access '/tmp/ve3': No such file or directory
ls: cannot access '/tmp/ve3nr': No such file or directory
ls: cannot access '/tmp/e3-*': No such file or directory
$ git status --porcelain      (mine: only this report; the S0-02, CI and incident-log paths are the other agents')
?? tasks/briefs/s0-05-support/VERIFY-E3-report.md
````

Every namespace, veth, nat rule, sysctl, claim, `/etc/netns` entry and process this lane created was destroyed by NAME or PID from
its own record (each driver's `finally`: `egress_ns_destroy <name>`, `os.kill(<pid>)`, the listeners' `_stop(<Popen>)`), never
`pkill -f`; every scratch copy and `--basetemp` lived under `/tmp/ve3/` and is gone.

````
$ python3 scripts/report_lint.py --min-refs 20 --map RC=proofs/S0-05/run_canaries.sh --map C=proofs/S0-05/check_egress.py --map PC=proofs/S0-05/tools/pc/run_s0_05_units.sh --map L=proofs/S0-05/netns_lib.sh --map T=tests/test_s0_05_egress.py tasks/briefs/s0-05-support/VERIFY-E3-report.md --root .
round 1: report_lint: 155 refs — OK 62, NEAR 7, MISS 71, UNCHECKABLE 15, UNRESOLVED 0 (worktree)
round 2: report_lint: 155 refs — OK 146, NEAR 1, MISS 7, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
round 3: report_lint: 155 refs — OK 153, NEAR 1, MISS 1, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
````

The one MISS (pytest's own SKIPPED line in the gates block, which names the test file's decorator line) and the one NEAR (my
probe's echoed line in the A4 block) sit inside pasted output and stay verbatim. Round 1's misses were correct line numbers whose report line carried no token from
the cited line; the fixes added one identifier copied from each cited line.
