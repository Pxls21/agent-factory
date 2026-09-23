# VERIFY-E2-R1 — report (adversarial verify of E2-R1, S0-05)

Status: COMPLETE. report_lint (final): `89 refs — OK 68, NEAR 3, MISS 0, UNCHECKABLE 18, UNRESOLVED 0` (floor
`--min-refs 15` met; UNCHECKABLE = citations in tables/prose with no adjacent claim token, not errors).

PIN: `6f2589d`. Lane: VERIFY-E2-R1, sandbox, root. Scratch root:
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ve2r1/` (a `git archive 6f2589d` of the
boundary). Key: L = `proofs/S0-05/netns_lib.sh`, R = `proofs/S0-05/run_canaries.sh`, PC =
`proofs/S0-05/tools/pc/run_s0_05_units.sh`, C = `proofs/S0-05/check_egress.py`, T = `tests/test_s0_05_egress.py`.

## OUTCOME

**GATE RECOMMENDATION: NOT-READY** (one blocker: F1). The coordinator owns the final gate.

Six of the seven E2-R1 repairs are SOLID and I could not break them: F2's atomic mkdir claim (the non-stale
concurrent race is correctly refused, `test_create_race_one_wins` reproduced), F3's cleanup ownership (correct in the
production code), F4's json.dump encoder (quote/backslash/newline round-trip exactly through the real runner), F1's
SIGKILL escalation (a SIGTERM-respawner and a SIGTERM-ignoring process are both gone at return; M11 is EQUIVALENT for
the "no survivor" postcondition), and F14's stand-in assertions (M16/M17 kills re-derived). All gates are green on the
landed bytes: root `137 passed`, non-root `122 passed, 15 skipped` (the 12 F19 cases pass non-root — F12 delivered),
bash -n / pyflakes / no_laya clean.

The blocker is F1 — the SAME class the F11/F12 repair set out to close. An allow-entry port ≥ 2^63 (e.g.
`10.9.9.9:99999999999999999999`) overflows bash's integer at `L:77` `[ "$port" -gt 65535 ]`, the `[` exits 2, the `||`
reads that as false, and the entry PASSES up-front validation. `egress_ns_create` then builds the namespace, the veth
(host IP `10.201.107.1/24`), `/etc/netns/<ns>`, the claim and the owner record before iptables refuses the port and it
returns 1 (not 64) with bash+iptables text (not the contract line). Through the REAL runner this state OUTLIVES the
runner (the not-run/continue path never adds the name to `NS_LIVE`, so `cleanup` never reaps it). That contradicts item
1's frozen "the port 1-65535 ... any violation returns 64 ... and leaves nothing behind" and the repo-wide AF-AP-129 /
anti-hollow-green tactic 1 (a numeric guard must reject the WHOLE unusable class). It fails SAFE for egress (the leaked
namespace carries policy DROP), so it is a falsified-refusal + resource-leak defect, not a containment breach. The fix
is one line (bound the port's digit count before the arithmetic) plus one test parameter. Because AF-AP-129 was already
measured in the brief's premise, the coordinator may instead scope it out via an explicit contract amendment — that
call is theirs; by the blocking predicate this lane must report it as NOT-READY.

Everything else is FOLLOW-UP (F3, F5, F6, F7, F8) or INFO (F2, F9, F10) — real observations, none meeting the full
blocking predicate. Details per item below.

## IDENTITY

Measured 2026-09-23T04:07Z (sandbox, HEAD `517212d`):

```
$ git diff --stat 6f2589d HEAD -- proofs/S0-05 tests/test_s0_05_egress.py ; echo "diff rc=$?"
diff rc=0            (empty = byte-identical)
234bb13ac0e475c6 320 proofs/S0-05/netns_lib.sh (PIN) = (tree)
44b1428b431303a1 139 proofs/S0-05/run_canaries.sh (PIN) = (tree)
4d3b917c6fd8c973 177 proofs/S0-05/tools/pc/run_s0_05_units.sh (PIN) = (tree)
5d9c502e862d0507 380 proofs/S0-05/check_egress.py (PIN) = (tree)
d93b1b32d075f684 1507 tests/test_s0_05_egress.py (PIN) = (tree)
```

All five match the brief's table.

## ITEMS

### Item 1 — F11/F12's class, beyond AF-AP-129

Probe (`ve2r1/i1/probe.sh`): each entry through the REAL `egress_ns_create` (tree bytes, read-only),
`EGRESS_OWNER_DIR=ve2r1/owner/i1`, a census after each (claim dir, owner record, netns, veth, `/etc/netns/<ns>`), and
a destroy of anything the probe itself created. Output, verbatim (message `%q`-quoted):

```
[1] plus-port                    rc=64 msg=egress:\ allow\ entry\ must\ be\ \<ip\>:\<port\>\,\ got\ \'1.2.3.4:+80\'
  census: claim=n owner=n netns=0 veth=0 etc_netns=n
[2] space-before-port            rc=64 msg=... got\ \'1.2.3.4:\ 80\'                census: all n/0
[3] trailing-space               rc=64 msg=... got\ \'1.2.3.4:80\ \'                census: all n/0
[4] newline-after-port           rc=64 msg=$'... got \'1.2.3.4:80\n\''              census: all n/0
[5] newline-in-ip                rc=64 msg=$'... got \'1.2.3.4\n:80\''              census: all n/0
[6] newline-between              rc=64 msg=$'... got \'1.2.3.4:80\n5.6.7.8:90\''    census: all n/0
[7] ipv6-loopback                rc=64 msg=... got\ \'::1:80\'                      census: all n/0
[8] all-zero                     rc=0 msg=''
  census: claim=Y owner=10868 netns=1 veth=1 etc_netns=Y    (destroyed by probe rc=0, then all n/0)
[9] broadcast                    rc=0 msg=''    (same shape as [8])
[10] loopback                    rc=0 msg=''    (same shape as [8])
[11] empty-entry                 rc=64 msg=... got\ \'\'                            census: all n/0
[12] bad-second-entry            rc=64 msg=... got\ \'bogus:80\'                    census: all n/0
[13] bad-second-port             rc=64 msg=... got\ \'10.201.1.1:70000\'            census: all n/0
[14] overflow-port (AP129)       rc=1 msg=$'.../netns_lib.sh: line 77: [: 99999999999999999999: integer expression expected\niptables v1.8.10 (nf_tables): invalid port/service `99999999999999999999\' specified\n...'
  census: claim=Y owner=10868 netns=1 veth=1 etc_netns=Y
[15] overflow-2^63               rc=1 (same shape as [14], 9223372036854775808)
[16] max-int64-port              rc=64 msg=... got\ \'10.9.9.9:9223372036854775807\'   census: all n/0
[17] good-then-overflow          rc=1 (same shape as [14]: a good first entry does not change it)
```

(Rows [2]-[13] abbreviated only in the shared message prefix `egress:\ allow\ entry\ must\ be\ \<ip\>:\<port\>\,\ got`;
every refused row printed the exact contract line.) The boundary is exactly 2^63: 9223372036854775807 is refused,
9223372036854775808 passes the guard.

**F1 — BLOCKER — an out-of-range port ≥ 2^63 passes validation; create returns 1, not 64, and leaves every piece of
state behind; through the real runner that state outlives the runner.** Reproduced, SOLID.
- Mechanism (read, then reproduced): `L:77` `[ "$port" -gt 65535 ]` exits 2 ("integer expression expected") when the
  digits overflow bash's intmax; the `||` in the `if` reads rc 2 as false, so the entry passes. Creation then runs to
  `L:155` (`iptables ... --dport "$port"`), which refuses the port; `egress_ns_create` returns 1 with the bash and
  iptables text, not the contract line, after `L:94` claim, `L:95` owner record, `L:123` netns, `L:124` veth, `L:137`
  `/etc/netns/<ns>`.
- Runner level (new; the premise measured the library only). `ALLOWED_HERMES='10.201.107.1:99999999999999999999'`
  through `PC` with a scratch owner dir:

```
runner rc=1
SKIP hermes-acp: /home/user/agent-factory/proofs/S0-05/netns_lib.sh: line 77: [: 99999999999999999999: integer expression expected
iptables v1.8.10 (nf_tables): invalid port/service `99999999999999999999' specified
=== checker ===
no-units: no run unit in .../ve2r1/i1r/ev
=== AFTER runner exit
netns: [s0-05-hermes-acp (id: 0) ]
veth: eh6a87fce7@if944
owner dir: s0-05-hermes-acp.claim s0-05-hermes-acp.owner  owner=11888
etc/netns: s0-05-hermes-acp
945: eh6a87fce7    inet 10.201.107.1/24 scope global eh6a87fce7
```

  `PC:93-97` records `not-run` and `continue`s BEFORE `PC:99` adds the name to `NS_LIVE`, so `PC:74-80` `cleanup`
  never sees it: a namespace, a host veth holding `10.201.107.1/24`, `/etc/netns/s0-05-hermes-acp`, the claim and a
  dead-pid owner record stay on the host after exit. (I destroyed it by name afterwards; census clean.)
- Expected (E2-R1 item 1, frozen): "the port 1-65535 decimal ... Any violation returns 64 with the existing line ...
  and leaves nothing behind." Observed: rc 1, no contract line, all five kinds of state left.
- Red control (reproduced): the committed `T:1489` `test_allow_entry_must_be_ipv4_literal` with ONE extra parameter
  `1.2.3.4:99999999999999999999` (scratch copy `ve2r1/rc1/`, PIN bytes otherwise): `FAILED
  tests/test_s0_05_egress.py::test_allow_entry_must_be_ipv4_literal[port-overflow]` / `1 failed, 12 passed, 125
  deselected in 0.57s` / `AssertionError: ... assert 1 == 64`. The test itself leaked `s0-05-e2-efb75675` (netns, veth,
  claim, owner, `/etc/netns`) because it has no cleanup for a refusal that is not a refusal; I destroyed it by name.
- Predicate: contract-mapped (E2-R1 item 1, verbatim) · canonical (the real library; the real runner) · material (state
  left on the host past the runner's exit; the refusal is mis-typed as rc 1 with non-contract text) · discriminator (the
  parameter above; deterministic) · in boundary (`L:77`, the repair's own line). All five hold.
- Fix (one line): test the port's digit COUNT before any arithmetic, for example
  `[[ "$port" =~ ^[1-9][0-9]{0,4}$ ]] && [ "$port" -le 65535 ]` (five digits cannot overflow), and add the overflow
  parameter to `T:1489`. AF-AP-129's class: every `[ -gt ]` / `(( ))` over an external digit string needs a length [line: `test_allow_entry_must_be_ipv4_literal`]
  bound first.

**F2 — INFO — `0.0.0.0`, `255.255.255.255` and `127.0.0.1` are accepted as allow targets.** Reproduced (rows [8]-[10]:
rc 0, full namespace). The contract's grammar (E2-R1 item 1: "a dotted quad of four decimal octets 0-255 with no
leading zero") makes all three VALID; nothing in E2-R1, the E2 contract or the seed's S0-05 block refuses special
addresses. Effect (inferred, not measured): `127.0.0.1` adds nothing beyond `L:158` `-o lo -j ACCEPT`; a TCP connect to
`0.0.0.0` is routed to a local address; TCP to broadcast cannot connect. None widens egress off the namespace. The one
visible effect (inferred): through the runner, a loopback allow row fails `PC:103`'s preflight against the namespace's [line: `egress_ns_run`]
own empty loopback and is recorded as `positive control unreachable`, not as a configuration refusal. FOLLOW-UP only.

**F3 — FOLLOW-UP — the namespace NAME is never validated (reviewed statically; not run, deliberately).** `L:93` [line: `claim_dir`]
`claim_dir="$EGRESS_OWNER_DIR/${ns}.claim"` and `L:248` `egress_ns_owner_file` build paths from the raw name, as do the
pre-existing `/etc/netns/$ns` lines (`L:137-138`, `L:305`, `L:311`, unchanged by E2-R1). A name holding a path
separator therefore moves every one of those paths out of its directory. No caller can pass one today: `PC:90` builds
`s0-05-$unit` only after `PC:84-89` found a non-empty `ALLOWED` row, and the table has exactly two keys (`PC:51`
hermes-acp, `PC:53` buzz-acp); `R:7` names create/destroy only in a comment (R never calls them); the tests use
`s0-05-e2-<hex8>` and the two fixed runner names (sweep: `grep egress_ns_create` over the tree). Not a blocker
(hypothetical misuse, no production caller). Fix: a strict name check (`^[a-z0-9][a-z0-9-]{0,63}$`) as the first
statement of `egress_ns_create`, `egress_ns_create_isolated` and `egress_ns_destroy`.

**Question answered — should `0.0.0.0` / `127.0.0.1` be refused?** Nothing in the frozen contract says so; F2 records
it as a follow-up, not a defect.

### Item 2 — F2's stale takeover

The mkdir claim (`L:94`) is atomic. But the STALE path (`L:96-105`, else branch) is check-then-act: when the claim dir [line: `mkdir`]
ALREADY exists (a dead prior owner), `mkdir` fails for BOTH concurrent creators, both fall to the else, both read the
dead pid, both pass `L:100` `kill -0`, and both reach `L:104` "take over atomically" — which is NOT atomic. Scratch
copy `ve2r1/i2/netns_lib_pause.sh` (PIN bytes + a `_ve2r1_pause` hook at two points; `bash -n` clean; the ONLY change
is the hook — diff pasted in scratch).

**Pause-injected control (both creators paused right after reading the dead owner, then released):**
```
stale owner pid=2000000 (dead)   reached stale_read: 2 paused pids=[13977 13978]
A: A_rc=0   B: B_rc=1
final owner record=[13978] (A=13977 B=13978)   netns count=1   veth=1
B.out: Cannot create namespace file "/run/netns/ve2r1-i2a": File exists
rules in ns (ACCEPT count): 2
```
Both took over the one stale claim. A won `ip netns add` (rc 0), B lost it (rc 1, raw text — not the named refusal),
and **the surviving owner record names B (13978), the LOSER, while A owns the namespace.** Through the runner this is a
leak: the winner (a real runner) has the name in `NS_LIVE`, but `PC:78` cleanup checks `owner == $$`, finds B's pid, [line: `owner_pid`]
and SKIPS destroying its own namespace at exit.

**Natural race (no injection), pre-existing stale claim, 12 trials:**
```
SUMMARY over 12 trials: both_rc0=0  named-refusal(65)=6  loser-hit-raw-error=6
```
The destructive both-rc-0 outcome appeared 0/12 without injection. Naturally the loser gets either the named
`namespace-live` rc 65 (6/12) or a raw rc 1 `File exists` (6/12); in every one of the 12 the owner record named the
live `netns=1` winner and the census was clean.

**Sub-cases:**
- (2a) Orphan claim dir, NO owner record (crash between `L:94` mkdir and `L:95` write): next create reads an empty
  owner (`owner_pid=""`), `L:100`'s `[ -n "$owner_pid" ]` is false, falls to take-over → `rc=0`, `owner=16633`,
  `netns=1`. Handled correctly.
- (2b) Claim + owner naming a recycled/unrelated LIVE pid, no namespace present: `namespace-live: ve2r1-i2d owned by
  pid 16918 / rc=65 / namespace present after=0`. The name is refused forever though nothing exists. This is VERIFY-E2
  **F5** (issue #29, out of scope per item 9) — noted as a touchpoint, not re-litigated.

**Does `test_create_race_one_wins` (T:1294) catch any of these?** No. It starts from a CLEAN owner dir, so the first
`mkdir` wins atomically and the second sees a LIVE owner → rc 65. It never sets up a PRE-EXISTING STALE claim under
concurrency, so the non-atomic stale-takeover window is untested.

**F4 — FOLLOW-UP — the stale-claim takeover is not atomic under concurrency.** Reproduced (pause-injected), SOLID on
mechanism; disposition FOLLOW-UP.
- Contract mapping: E2-R1 item 2 "a stale claim (dead pid) is taken over atomically" — the else branch is
  check-then-act, so two concurrent takeovers are possible.
- Why NOT a blocker (predicate #2/#3): the materially-damaging outcome (both rc 0, owner names the loser, winner's
  namespace leaks at cleanup) reproduces ONLY under pause injection — a surrogate mechanism; the natural path (0/12
  both-rc-0) yields either the correct named refusal or a cosmetically-wrong reason string (raw rc 1) on the loser,
  which is refused either way and not material to the containment guarantee. The precondition is compound and unusual:
  a prior runner SIGKILLed before its EXIT trap left a stale claim dir, AND two runners start concurrently for the
  same fixed unit name, AND they hit the sub-100 ms window between the stale read and the record write.
- Discriminator: the barrier control above (deterministic). Fix: make the stale takeover atomic too — e.g. `mkdir` a
  per-name `.lock`, or rename-into-place the owner file, or re-`mkdir` the claim after `rm`-ing a proven-stale one so
  exactly one creator re-creates it. A concurrent-with-pre-existing-stale-claim case belongs in `T:1294`'s family.

### Item 3 — F1 under shapes the tests do not use

**(a) SIGTERM-respawner.** A process whose TERM handler forks a replacement into the same namespace (`ve2r1/i3a/respawn.sh`):
```
before destroy: pids in ns=[17996 17997]   ns inode=4026532262
DESTROY_RC=0   AFTER destroy: netns present=0   processes still in the (deleted) ns inode: []
```
Caught. `L:278`'s SIGKILL pass re-reads `ip netns pids` fresh, so a child born during the SIGTERM grace is killed.
Reviewed-static note (no live repro, not a finding): the FINAL survivor check `L:297-300` iterates the `$survivors`
snapshot from `L:278`, not a fresh `ip netns pids`; a process appearing AFTER `L:278`'s read would be missed by the
loud-fail check. It cannot arise from a SIGKILLed parent (SIGKILL is uncatchable), so no reproduction; a fresh
`ip netns pids` in the final check would close the theoretical TOCTOU.

**(b) The rc-1 path — who reads it?** Reviewed (mechanism traced), not live-reproducible here (the loud rc-1 path at
`L:301-306` needs a process that survives SIGKILL, i.e. stuck in D-state — not constructible in this sandbox). [line: `final_survivors`]
`egress_ns_create`'s destroy-first `L:109` calls `_egress_ns_teardown` and does not read its rc; the runner's
`egress_ns_destroy` at `PC:109/132/141` also ignores rc. Crucially, on the survivor path `_egress_ns_teardown` STILL
runs `L:303-305` (`ip link del`, `ip netns del`, `rm -rf /etc/netns`) before `return 1`, so the NAMED namespace is
deleted regardless. A survivor is therefore stranded in an anonymous netns with NO veth (cannot egress), and a new
create gets a FRESH inode for the reused name — the old process cannot touch the new namespace. So
`egress_ns_destroy` freeing the claim after a failed teardown does NOT let an old process affect a reused name. Safe.
The only cost of the ignored rc is that a stranded D-state process is not surfaced to the caller — no egress risk.

**(c) M11 EQUIVALENT claim, graded.** M11 mutant = `L:266-275` TERM wait loop removed (`ve2r1/i3c/netns_lib_m11.sh`,
`bash -n` clean, diff pasted in scratch). Two behavioral tests on the REAL library vs M11:
- Slow-exit-on-TERM (exits 1 s after TERM): `M11: RC=0, survivors in deleted ns: []`. Gone at return under M11 too —
  the SIGKILL escalation (added by this repair) leaves no survivor. So M11 is EQUIVALENT for the F1 postcondition
  ("destroy never returns 0 with a survivor").
- Graceful handler that does 1 s of work BEFORE writing its log, then exits:
  ```
  M11:  destroy=1.99s  log=[]                  (graceful log LOST — SIGKILLed mid-work)
  REAL: destroy=1.12s  log=[FLUSHED_ON_TERM]   (graceful shutdown honored)
  ```
  So M11 is NOT behaviorally equivalent in general: it destroys a unit's delayed on-TERM work.

**Grade:** the builder's "M11 EQUIVALENT" is CORRECT for the frozen contract. E2-R1 item 5 / F1 requires only "no
survivor at return", which the SIGKILL escalation guarantees regardless of the wait loop. The graceful-shutdown
difference does NOT map to the S0-05 contract or the runner's evidence: the runner's unit is a stand-in that sleeps and
handles no TERM (`pc_launch.py`), and `PC:141` destroys AFTER the canary evidence is already written (`PC:136`), so a [line: `bash`, `egress_ns_destroy`]
unit's on-TERM behavior produces no evidence. FOLLOW-UP note: the inherited E2-brief item-5 phrase "the D-M11
differential (a 1-second slow exit is gone at return) kills M11" is now STALE — once the SIGKILL escalation was added,
a slow exit is gone at return under M11 too, so that differential no longer discriminates. Not a defect; a
contract-text drift for the coordinator to note.

### Item 4 — F3 cleanup and NS_LIVE

**(a) Substring pruning.** `PC:109/132/142` prune with `NS_LIVE=${NS_LIVE//$ns/}` (remove-all-substrings), then
`NS_LIVE=${NS_LIVE# }` (strip ONE leading space). Demonstrated corruption:
```
after removing 's0-05-a' from 's0-05-a s0-05-ab': NS_LIVE=[b]   (s0-05-ab corrupted to 'b' -> live ns MISSED)
```
So a colliding pair would leave a mangled fragment and drop the live sibling from cleanup. But the runner's unit table
(`PC:51` hermes-acp, `PC:53` buzz-acp) produces exactly `s0-05-hermes-acp` and `s0-05-buzz-acp`, and neither is a [line: `ALLOWED[buzz-acp]`, `ALLOWED[hermes-acp]`]
substring of the other (checked both directions). No current caller can trigger it. **F5 — FOLLOW-UP** (latent; not a
blocker: no production caller, no material effect today). Fix: prune by rebuilding the list token-wise
(`for x in $NS_LIVE; do [ "$x" != "$ns" ] && keep="$keep $x"; done`), the order-blind set-diff pattern.

**(b) Owner record removed by hand while the runner holds the namespace.** The runner's `cleanup` (`PC:74-80`) reads
the record; with it gone, `owner_pid=""`, `[ "" = "$$" ]` is false, so cleanup SKIPS its OWN namespace:
```
owner record before removal=[20093]   record removed; now exiting (cleanup runs)
AFTER runner exit: netns present=1   (leaked: cleanup skipped its own ns)
```
This is the designed trade-off of the F3 ownership check: the record is the sole liveness signal (VERIFY-E2 **F6**,
INFO, issue #29 — out of scope, noted as a touchpoint). It fails SAFE — a LEAK, never egress — and on the PC `/run` is
tmpfs so a reboot clears `/run/netns` and `/run/s0-05-egress` together (consistent). Not a blocker.

### Item 5 — F4 edges

Reason provenance (traced): `PC:84` `allowed=${ALLOWED[$unit]}` ← env `ALLOWED_HERMES`/`ALLOWED_BUZZACP` (operator-set,
any non-NUL bytes); `PC:93` `create_err=$(egress_ns_create ... 2>&1)` captures create's stderr, which echoes the entry [line: `create_err`]
(`got '<entry>'`); `PC:95` stores it as the reason. So a reason can carry any byte the operator put in `ALLOWED_*`. [line: `RESULT[`]

Contract cases through the REAL runner (each parsed by `check_egress.py`, reason compared to input):
```
[quote]      units.json size=942  parse=OK  reason=...got '10.201.107.1:20128"'...   checker: exit 1 per contract
[backslash]  units.json size=945  parse=OK  reason=...got '10.201.107.1:20128\\end'...
[newline]    units.json size=943  parse=OK  reason=...got '10.201.107.1:20128\nX'...
[all-three]  units.json size=950  parse=OK  reason=...got '10.201.107.1:20128" \\ x\ny'...
```
The `"`, `\` and newline round-trip EXACTLY — the F4 repair (json.dump) holds for its frozen test set. Checker exits 1
because hermes-acp was refused (no run unit), which is correct.

**Invalid-UTF-8 byte (the encoder's failure mode):** `ALLOWED_HERMES=$'\xff:80'` through the real runner:
```
SKIP hermes-acp: egress: allow entry must be <ip>:<port>, got '<0xff>:80'
Traceback (most recent call last): ... UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 46
units.json exists=Y size=0        (od: empty)
checker: evidence-invalid: units.json Expecting value: line 1 column 1 (char 0) / exit 1 per contract
```
`PC:164` `fields[i].decode()` is UTF-8-strict; a 0xff byte raises, the `python3 -c` block crashes, and `PC:172`'s `> "$EVIDENCE_ROOT/units.json"` redirect leaves units.json TRUNCATED TO EMPTY. The runner still runs the checker (`PC:176-177`), which reports [line: `checker`]
`evidence-invalid`. So one unit's non-UTF-8 reason corrupts the WHOLE manifest — the same class the F4 repair set out
to end ("units.json is encoded, never printed").

**F6 — FOLLOW-UP — an invalid-UTF-8 reason empties units.json (whole-manifest corruption).** Reproduced through the
real runner, SOLID.
- Why NOT a blocker: (predicate #1) the frozen F4 criterion is the three ASCII specials (`"`, `\`, newline), which
  round-trip — invalid UTF-8 is outside the frozen test set; (predicate #3) it fails CLOSED — the checker reports
  `evidence-invalid` and exits 1, never a false PASS, so no hollow green (the same fail-closed outcome as the
  pre-repair invalid-JSON bug). The trigger is an unusual operator error (a non-UTF-8 byte in an `ALLOWED_*` env var).
- Fix (one line): decode with `errors="surrogatepass"` or `errors="replace"`, or carry the fields as bytes and
  `json.dump(..., ensure_ascii=True)` after a lossless decode.

**Sub-questions.** Empty RESULT+ABSENT pair: `PC:158` `if not data: json.dump({"units": []})` handles it, but it is
unreachable — `ABSENT` is always populated (`PC:58-63`) and `RESULT` gets every requested unit, so `_json_tmp` is never
empty in the real runner. python3 failing in the block: shown above — units.json is left EMPTY and the runner DOES go
on to the checker, which then reports `evidence-invalid` (fail-closed).

### Item 6 — F14 binding

The stand-in records `pid`, `argv` AND `net_ino` (`T:1084` `os.stat('/proc/self/ns/net').st_ino`), but **`net_ino` is
never asserted** anywhere in the file (`grep net_ino` → the write at 1084 only). So the test binds to the record's
PRESENCE (`T:1135` `record_file.exists()`), `argv[0]` (`T:1142` `record["argv"][0] == expected_script`, kills M16), and
the pid being DEAD after the leg (`T:1147` `os.kill(standin_pid, 0)`, kills M17). It does
NOT compare the stand-in's namespace inode to the namespace under test.

Cheapest mutant (`ve2r1/i6/`, scratch tree): change `PC:118` `egress_ns_run "$ns" setsid ${LAUNCH[$unit]}` →
`setsid ${LAUNCH[$unit]}` so the stand-in runs OUTSIDE the namespace, record intact. Result:
```
FAILED .../i6/tests/test_s0_05_egress.py::test_runner_live_leg
AssertionError: stand-in pid 21825 still alive after its unit's leg     (1 failed, 136 deselected in 37.38s)
```
The mutant IS killed — but by the dead-after-leg (M17) assertion, not by an inode check: an outside stand-in survives
`PC:141` `egress_ns_destroy`, which reaps only `ip netns pids "$ns"`. So the F14 test catches "outside the namespace"
INDIRECTLY, because the runner's teardown is namespace-scoped. (The mutant leaked its outside stand-in, which the test's
namespace-scoped `finally` cannot reap; I killed it by pid — census clean.)

**F7 — FOLLOW-UP — F14's namespace binding is indirect.** Reviewed + reproduced, SOLID.
- The frozen F14 contract (E2-R1 item 6: record exists · argv kills M16 · dead-after-leg kills M17) is MET, and the
  outside-namespace mutant is killed. Not a blocker.
- The gap: the binding relies on the teardown staying namespace-scoped; a future change to kill-by-pid would silently
  un-bind the test (the recorded `net_ino` would still not be checked). Fix (the stand-in already records it): assert
  `record["net_ino"]` equals the namespace's inode (`stat -Lc %i /var/run/netns/<ns>` captured during the leg), the
  direct proof the frozen text hints at.

### Item 7 — new mutants (M12-M17)

All six built from the PIN bytes in `ve2r1/mut/<id>/` (scratch trees; each `bash -n` clean). Runs use the root venv
python; the scratch tree is a `git archive` of `proofs/S0-05` + the test only, so `test_spec_validates_against_the_schema`
and `test_shebang_matches_launch_interpreter` fail in EVERY scratch run (they read `proofs/schemas/` and
`proofs/S0-01/tools/`, absent from the boundary archive). I proved this by running the UNMUTATED PIN scratch copy:
`2 failed, 135 passed in 60.90s` with exactly those two — so those two are scratch artifacts, never mutation kills
(AF-AP-78). A mutant is KILLED only by an ADDITIONAL failure beyond that pair.

**M14 SURVIVED and M17 SURVIVED.** See the two findings below the table.

### MUTATION TABLE

| Mutant | Target | Compiles | Collected | Result | Killing test |
|---|---|---|---|---|---|
| M12 | `L:77` range test `-gt 65535` deleted (regex alone) | bash -n OK | 137 | KILLED | `test_allow_entry_must_be_ipv4_literal[port-65536]` (rc 1, not 64) |
| M13 | `L:94` `mkdir "$claim_dir"` → `mkdir -p` | bash -n OK | 137 | KILLED | `test_create_race_one_wins` (rc2=0) + `test_live_sibling_namespace_is_refused` (inner rc 0) |
| M14 | `PC:78` `owner_pid` comparison removed (destroy every `NS_LIVE`) | bash -n OK | 137 | **SURVIVED** | — (F8 below) |
| M15 | `PC:170` `json.dump` block → 9223162's printf loop | bash -n OK | 137 | KILLED | `test_units_json_quotes_in_reason` (JSONDecodeError) |
| M16 | `L:280` `kill -KILL` pass removed | bash -n OK | 137 | KILLED | `test_destroy_kills_sigterm_ignoring_process` (pid still in ns) |
| M17 | `egress_ns_destroy` always `return 0` | bash -n OK | 137 | **SURVIVED (EQUIVALENT)** | — (F9 below) |

(Collected = 137: the scratch runs collect the same 137 as the real tree; only the two schema/shebang artifacts fail.)

Re-run of the builder's listed mutants was not repeated here — the builder's M10/M11/M16/M17/M20/M21/M22 are on E2's
bytes; item 3(c) already re-graded M11 (EQUIVALENT for the F1 postcondition), and item 6 re-derived the M16/M17 kills
(`test_runner_live_leg`). See item 8 for the builder's table.

**F8 — FOLLOW-UP — M14 survives: the runner's `cleanup()` ownership check is not gated by a test that calls it.**
Reproduced, SOLID. M14 removes the `[ "$owner_pid" = "$$" ]` guard at `PC:78` so `cleanup()` destroys every `NS_LIVE`
name. Full suite: identical to the PIN scratch baseline (only the 2 artifacts fail) → no test kills it. Why: the F3
tests do NOT exercise the runner's real `cleanup()` with a populated `NS_LIVE` — `test_cleanup_does_not_destroy_sibling_namespace`
(`T:1353`) HAND-INLINES the ownership-check logic in bash rather than calling `cleanup()` (a MIRROR, not a gate: [line: `test_cleanup_does_not_destroy_sibling_namespace`]
build-loop rule), and `test_runner_refusal_does_not_destroy_sibling` (`T:1423`) refuses B's create so B's `NS_LIVE`
stays empty and `cleanup()` is a no-op. The PRODUCTION code is CORRECT (the guard is present at `PC:78`); the gap is [line: `owner_pid`]
test coverage. Not a blocker (no production defect; the runner is a PC script not run here). Fix: a test that runs the
real runner, interrupts it mid-leg (SIGINT after a create, before the in-loop destroy) so `NS_LIVE` holds a name a
sibling now owns, and asserts the sibling survives `cleanup()`.

**F9 — INFO — M17 is EQUIVALENT: `egress_ns_destroy`'s return code is never consumed.** Reproduced, SOLID. M17 makes
`egress_ns_destroy` return 0 even when `_egress_ns_teardown` reported a survivor (rc 1). No test kills it because the
survivor path needs a SIGKILL-proof (D-state) process, not constructible here; and no PRODUCTION caller reads the rc —
create's destroy-first uses `_egress_ns_teardown` directly and ignores its rc (`L:109`), the runner ignores
`egress_ns_destroy`'s rc (`PC:141`), and the loud stderr message comes from `_egress_ns_teardown` (`L:302`), which M17 [line: `egress`]
does not touch. So the "fail loud" is stderr-only and the F1 "destroy never returns 0 with a survivor" postcondition on
`egress_ns_destroy` is unobservable in practice. Equivalent, not a defect; noted because it means no caller ACTS on a
teardown failure (they delete the namespace regardless, which fails safe — no egress).

### Item 8 — the builder's report vs the PIN

Gate counts CONFIRMED against the landed bytes (see GATES): root `137 passed`, non-root `122 passed, 15 skipped`,
bash -n clean, pyflakes clean, no_laya clean — all match `E2-R1-report.md`. The mutant-table SUBSTANCE holds: I
re-derived M16/M17 kills through `test_runner_live_leg` (item 6) and re-graded M11 EQUIVALENT for the F1 postcondition
(item 3c).

**F10 — INFO — the builder's report line counts and ranges are a PRE-LANDING snapshot; they do not match the landed
bytes.** The "Files touched" table claims `netns_lib.sh` 325 / `run_s0_05_units.sh` 173 / `test` 1497; the landed
6f2589d bytes are 320 / 177 / 1507. Cited ranges drift similarly (e.g. up-front validation "67-84" → landed 71-83;
`test_allow_entry` "1467-1493" → landed 1489). The drift is explained by coordinator edits at the E2 landing that the
report predates — visible in the code itself (`L:244-246` "the F23 owner record lives OUTSIDE /etc/netns/... the E2
landing, 2026-09-23"; `T:1130-1142` "coordinator touch at the E2 landing"). Cosmetic; the report's substance is sound.
Not a blocker (the brief says the report is an INPUT to attack, and the landed bytes — not the report — are the
contract). The builder's own DISCREPANCIES #1 already flags that origin moved past its stated PIN.

### Item 9 — out-of-scope touchpoints (one line each, not re-litigated)

- Issue #29 F5 (recycled/unrelated live pid refuses a name forever with no namespace present): reproduced incidentally
  in item 2(b) — the F2 claim design inherits it. Out of scope.
- Issue #29 F6 (the owner record is the only liveness signal → record loss leaks): reproduced incidentally in item
  4(b). Out of scope.
- Issue #29 M10 (the F6 collision check `index($4,pfx)==1` breadth): the builder lists it SURVIVED/pre-existing; not
  re-run. Out of scope.
- CD1 launch recipe / D-051 relay DNAT: not built; not touched. The runner's `LAUNCH` rows and the preflight abort are
  unchanged. Out of scope.
- Seed second-assertion wording: owner's pending decision; not touched.

## GATES

All on the landed tree (HEAD `9ca6d09` at run time; S0-05 boundary `git diff --stat 6f2589d HEAD -- proofs/S0-05
tests/test_s0_05_egress.py` = empty, byte-identical to the PIN).

Exact invocation (root run 1):
`/root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=<scratch>/bt/g1`
```
137 passed in 60.86s (0:01:00)
ROOT1 pipestatus=0
```
Non-root:
`setpriv --reuid=65534 --regid=65534 --clear-groups env HOME=/tmp/e2r1nr /usr/bin/python3 -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e2r1nr/bt`
```
122 passed, 15 skipped in 3.99s
NONROOT pipestatus=0
```
(15 skips = the `@NEEDS_NETNS` legs, which need root; the 12 `test_allow_entry_must_be_ipv4_literal` cases PASS
non-root — the F12 repair.) The suite RAN: 137 passed root, 122+15=137 non-root — collection is real, not an
empty filter.

`bash -n` (all three shell files): `netns_lib.sh` rc 0, `run_s0_05_units.sh` rc 0, `run_canaries.sh` rc 0.
`pyflakes tests/test_s0_05_egress.py proofs/S0-05/check_egress.py`: clean, rc 0.
`python3 scripts/no_laya_in_gates.py`: `38 files scanned, clean`, rc 0.

Mutation gates (item 7): M12/M13/M15/M16 KILLED; M14 SURVIVED (F8); M17 SURVIVED/EQUIVALENT (F9). The PIN scratch
baseline (`2 failed, 135 passed` — schema+shebang artifacts) validates every scratch mutant run.

report_lint (below, in this same report's final pass).

## FOLLOW-UPS

For the coordinator to file under D-034 (non-blocking; one line each):
1. **F3** — validate the namespace NAME at the head of `egress_ns_create`/`_isolated`/`egress_ns_destroy`
   (`^[a-z0-9][a-z0-9-]{0,63}$`); today no caller passes a bad name, but the claim/owner/`/etc/netns` paths are built
   from it raw (`L:93`, `L:248`, `L:137`).
2. **F4** — make the STALE-claim takeover atomic (`L:96-105`); under a pre-existing stale claim + two concurrent
   creators, both can take over (pause-injected repro); add a concurrent-stale case to `T:1294`'s family.
3. **F5** — prune `NS_LIVE` token-wise, not `${NS_LIVE//$ns/}` (`PC:109/132/142`): the substring removal would corrupt
   a colliding name pair (no current pair collides).
4. **F6** — decode the units.json fields losslessly (`PC:164`): an invalid-UTF-8 byte in a reason crashes the encoder
   and empties units.json (fails closed, but re-introduces whole-manifest corruption for that class).
5. **F7** — assert `record["net_ino"]` against the namespace inode in `test_runner_live_leg` (`T:1066`); the stand-in
   already records it, but the test binds to the namespace only indirectly (via dead-after-leg).
6. **F8** — add a test that runs the real runner, interrupts it mid-leg, and asserts `cleanup()` skips a sibling's
   name; today M14 (drop `PC:78`'s owner check) SURVIVES because the F3 tests never call the real `cleanup()` with a [line: `owner_pid`]
   populated `NS_LIVE`.
7. **F2/F10** (INFO) — decide whether `0.0.0.0`/`127.0.0.1`/broadcast should be refused as allow targets (contract is
   silent); note that no production caller reads `egress_ns_destroy`'s return code, so its F1 "non-zero on survivor" is
   stderr-only.
8. Contract-text drift (item 3c): the inherited "D-M11 differential kills M11" phrase is stale now that the SIGKILL
   escalation exists — a slow exit is gone at return under M11 too.

Out-of-scope touchpoints (issue #29, item 9): F5-recycled-pid (my item 2b), F6-record-only-liveness (my item 4b),
M10-collision-breadth — not re-litigated.

## CENSUS

After the last live run (2026-09-23), all empty of anything I created:
```
$ ip netns list                     ->  (empty)
$ ip -o link show type veth         ->  (empty)
$ ls -A /run/s0-05-egress           ->  (empty)
$ ls -A <scratch>/owner/*/          ->  (empty)
$ ls -A /etc/netns                  ->  (empty)
$ pgrep -f '[p]c_launch.py'         ->  (none)
$ pgrep -f "[t]rap '' TERM"         ->  (none)
```
Every namespace/veth/process I created during a probe or a mutant run was destroyed by name / killed by pid from my own
record (never `pkill -f`). Two incidental leaks from red controls (`test_allow_entry[port-overflow]` left
`s0-05-e2-efb75675`; the item-6 outside-namespace mutant left a stand-in) were cleaned up in the same turn and are noted
at their items. Scratch (`ve2r1/`) is 14 MB; deleted at lane end. Disk: 2.1 GB free.

## NOT-done

- The PC-side live legs of `run_s0_05_units.sh` (real hermes-acp/buzz-acp units, real OmniRoute) were NOT run — the
  runner is a PC script (`NOT run here` by its own header) and this lane is sandbox-only. I exercised it with a
  stand-in launcher + a local listener, the same shape the committed `test_runner_live_leg` uses.
- F1's rc-1 loud-survivor path (`L:301-306`) was reviewed statically, not reproduced live: it needs a SIGKILL-proof [line: `final_survivors`]
  (D-state) process, not constructible here. Mechanism traced; name-reuse shown safe by reading (the named namespace is
  deleted even on that path).
- The builder's listed mutants (M10/M11/M16/M17/M20/M21/M22 on E2 bytes) were not all re-run; M11 was re-graded
  (item 3c) and M16/M17 kills re-derived (item 6). M10 (F6 collision breadth) is issue #29, out of scope.
- I did NOT re-run the full repo suite (`proofs/ spikes/ tests/`) — only `tests/test_s0_05_egress.py`, the boundary.
