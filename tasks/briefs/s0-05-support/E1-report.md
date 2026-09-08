# Lane E1 — S0-05 no-direct-egress: canary suite, selective netns as a library, unit runner, checker

PIN: `23a3458` · venue: sandbox (root, kernel 6.18.44-fc-v24, iptables v1.8.10 nf_tables) · 2026-09-08T03:02Z
Model: Opus 4.6 `code-implementer`. Nothing committed, nothing pushed, no PC bridge used, no proof minted.
S0-05 stays `ABSENT` in the ledger: `proofs/S0-05/result.json` does not exist and this lane never ran the mint path.

---

## 1. FILE IDENTITY (sha256 first 16 | path | lines — pasted from the gate's identity table)

```
6d313b8bef0c677e  proofs/S0-05/canaries/_emit.sh  36
2710a809b664ea7d  proofs/S0-05/canaries/c0_allowed_target.sh  15
da07fa501f38bac3  proofs/S0-05/canaries/c1_dns_resolve.sh  26
1756448e541588aa  proofs/S0-05/canaries/c2_tcp_connect.sh  10
7fc1bbb9752e5920  proofs/S0-05/canaries/c3_tls_handshake.sh  9
e9264596e3e6d179  proofs/S0-05/canaries/c4_internet_target.sh  10
04ab37a96dd7390d  proofs/S0-05/canaries/c5_udp_dns.sh  10
c26bda73bb432815  proofs/S0-05/canaries/c6_blocked_local.sh  16
5bd9d835004f7dd7  proofs/S0-05/canaries/connect_probe.py  87
59b884c6e60fa784  proofs/S0-05/check_egress.py  370
f2f1bc756a2b8a78  proofs/S0-05/fixtures/evidence-bare-unshare/curl/canaries.jsonl  13
96a11164a6d71958  proofs/S0-05/fixtures/evidence-bare-unshare/curl/gate.json  10
b76bbd9d0e19679b  proofs/S0-05/fixtures/evidence-bare-unshare/curl/runtime.json  27
b24914a11e4feef7  proofs/S0-05/fixtures/evidence-bare-unshare/units.json  34
7102bcd10b2ce1a1  proofs/S0-05/fixtures/evidence-gate-off/curl/canaries.jsonl  13
19c02524c0397d87  proofs/S0-05/fixtures/evidence-gate-off/curl/gate.json  10
8b36e54004aa73cc  proofs/S0-05/fixtures/evidence-gate-off/curl/runtime.json  23
936e2ade30655595  proofs/S0-05/fixtures/evidence-gate-off/units.json  34
df655e2a626e9ad1  proofs/S0-05/fixtures/evidence-mechanism-sandbox/curl/canaries.jsonl  13
cd68311410466935  proofs/S0-05/fixtures/evidence-mechanism-sandbox/curl/gate.json  10
15ec337388302c48  proofs/S0-05/fixtures/evidence-mechanism-sandbox/curl/runtime.json  27
a7ac9edf1dd948aa  proofs/S0-05/fixtures/evidence-mechanism-sandbox/units.json  34
7bb9d226fc164270  proofs/S0-05/fixtures/evidence-synthetic-pass/curl/canaries.jsonl  13
bb720642a77cfae1  proofs/S0-05/fixtures/evidence-synthetic-pass/curl/gate.json  10
be79dcd14add8f51  proofs/S0-05/fixtures/evidence-synthetic-pass/curl/runtime.json  27
6ee5f1f8b801d6d2  proofs/S0-05/fixtures/evidence-synthetic-pass/hermes-acp/canaries.jsonl  13
0264fb2546188451  proofs/S0-05/fixtures/evidence-synthetic-pass/hermes-acp/gate.json  10
421e4d8bbbf48749  proofs/S0-05/fixtures/evidence-synthetic-pass/hermes-acp/runtime.json  27
0452e6c77318e3c0  proofs/S0-05/fixtures/evidence-synthetic-pass/units.json  34
1b2bd911d54262d3  proofs/S0-05/netns_lib.sh  209
6f7298077aa39819  proofs/S0-05/run_canaries.sh  131
0751bf678f50349e  proofs/S0-05/spec.json  43
b28dc7632602d555  proofs/S0-05/tools/pc/run_s0_05_units.sh  150
6c96693ad4063c35  tests/test_s0_05_egress.py  730
```

34 files, all NEW, all inside the brief's Scope. `git status --porcelain proofs/S0-05 tests/test_s0_05_egress.py` → `?? proofs/S0-05/` and `?? tests/test_s0_05_egress.py`; no tracked file was touched, nothing staged, nothing committed.

Report aliases used below: `C` = `proofs/S0-05/check_egress.py` · `L` = `proofs/S0-05/netns_lib.sh` ·
`R` = `proofs/S0-05/run_canaries.sh` · `T` = `tests/test_s0_05_egress.py` · `PC` = `proofs/S0-05/tools/pc/run_s0_05_units.sh`.

---

## 2. GATES (counts pasted verbatim, twice, from a `git archive 23a3458` copy + exactly these files)

```
lane_gate: archive of 23a345872943 at .../scratchpad/e1/gateF; 2026-09-08T03:02:15Z
run 1: pytest-exit: 0 | pytest-summary: 98 passed in 6.80s
run 2: pytest-exit: 0 | pytest-summary: 98 passed in 5.76s
RESULT: PASS 2/2 runs agree — 98 passed
```

Invocation, explicit `--basetemp` on both runs:
`python3 -m pytest tests/test_s0_05_egress.py -q -rs -p no:cacheprovider --basetemp=<scratch>/btf{1,2}`.
`-rs` reports skips: none. The three root-gated namespace tests RAN here.

Lint: `bash -n` OK on all 11 shell files (`test_every_new_shell_file_parses` runs the same check in-suite);
pyflakes 3.4.0 on `check_egress.py`, `connect_probe.py` and the test file → 0 findings.
`python3 scripts/ap_screen.py` over the two production Python files → `AP_SCREEN over 2 path(s): 1 hits over 2 files`,
`AP-32: 1` at `C:170` (`def rules_digest(lines):`) — classified in §6. `--tests` over the test file → `0 hits over 1 files`.
`scripts/report_lint.py` over this report, with a `--map` per scope file:
`report_lint: 107 refs — OK 107, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

---

## 3. DONE — assertion → canary → checker rule → test

The seed's two assertions — `proof_id: S0-05` at seeds/seed-stage0-v1.yaml:423, and the negative control's
`expected_failure_reason: 'egress-permitted: gate-disabled'` at seeds/seed-stage0-v1.yaml:440 — map like this.

| # | assertion | canary | checker rule | test |
|---|---|---|---|---|
| A1 | the unit CAN reach its allowed target | C0 `canaries/c0_allowed_target.sh` (curl → HTTP status) | `C:214` `def check_positive_control(records, unit):` — every C0 record must be `rc 0` + a 2xx `http_status`, else `positive-control-failed: <unit>` | `T:204` `test_positive_control_is_mandatory` (6 shapes), `T:137` `test_bare_unshare_bundle_is_red_on_the_positive_control` |
| A2 | DNS for model hosts fails inside the namespace | C1 `canaries/c1_dns_resolve.sh` × 3 hosts | `C:229` `def check_denials(records, unit):` — rc ∈ {6,7,28} + a vocabulary detail + the detail must name its own target | `T:218` `test_a_canary_that_succeeded_is_caught`, `T:326` `test_hosts_file_shortcircuit_is_accepted` |
| A3 | TCP to a model endpoint fails | C2 `canaries/c2_tcp_connect.sh` × 3 (addresses resolved OUTSIDE the ns) | same denial rule | `T:235` `test_a_deleted_canary_is_caught`, `T:246` `test_a_denial_rc_outside_the_set_is_caught` |
| A4 | TLS handshake to a model endpoint fails | C3 `canaries/c3_tls_handshake.sh` × 3 (handshake only, zero application bytes) | same denial rule | as A3 |
| A5 | the general internet is RECORDED, not asserted | C4 `canaries/c4_internet_target.sh` | `C:254` `def check_recorded(records, unit):` — prints a `recorded:` line; a missing C4 is `canary-missing` | `T:235` `test_a_deleted_canary_is_caught` (case `[C4]`) |
| A6 | UDP/53 egress fails (the spike tested TCP only) | C5 `canaries/c5_udp_dns.sh` | same denial rule | `T:218` `test_a_canary_that_succeeded_is_caught` (case `[C5]`) |
| A7 | a routable, non-allow-listed endpoint fails — **the leg the firewall alone decides** | C6 `canaries/c6_blocked_local.sh` (ADDED, see §7) | same denial rule | `T:125` `test_gate_off_bundle_really_did_flip_a_canary` |
| A8 | the gate was ON | — | `C:328` `raise Failure("egress-permitted: gate-disabled")`, evaluated for EVERY unit before any canary is read | `T:118` `test_gate_off_bundle_is_red_with_the_seed_reason`, `T:160` `test_gate_check_runs_before_any_canary` |
| A9 | the gate actually FIRED | — | `C:277` `gate-inert: {unit} OUTPUT DROP counter did not advance` | `T:409` `test_a_gate_that_never_fired_is_caught` |
| A10 | the rule set is the pinned allow-list | — | `C:282` and `C:284` `egress-rules-unpinned` — recorded rules must hash to the gate digest AND equal `C:157` `def expected_rules(allowed):` | `T:340` `test_rules_that_do_not_hash_to_the_digest_are_caught`, `T:352` `test_a_widened_rule_set_with_a_matching_digest_is_caught`, `T:366` `test_a_dropped_policy_line_is_caught`, `T:377` `test_a_widened_allow_list_changes_the_expected_digest` |
| A11 | units that do not exist are recorded, never passed | — | `C:288` `def read_units_manifest(root):` — a `not-run` unit needs a reason, is excluded from the run set, and prints `NOT run: …` | `T:442` `test_a_declared_absent_unit_cannot_also_be_present`, `T:470` `test_a_malformed_units_manifest_is_rejected` |
| A12 | evidence that does not exist DEFERS | — | `C:313` `deferred: evidence-root-absent` (exit 2) and a `not-run` canary defers | `T:481` `test_an_absent_evidence_root_defers`, `T:494` `test_a_canary_that_could_not_run_defers` |

### The library (the spike lifted, not re-derived)

`L:66` `egress_ns_create() {` lifts spikes/selective-egress/probe.sh:39-58 in shape — `ip netns add`, the veth pair, the peer
moved into the ns, addresses, links up; the rule application is factored into `L:101` `_egress_apply_gate() {` which is `probe.sh:50-58`
(policy DROP on the three chains, an ACCEPT pair per allowed `ip:port`, loopback ACCEPT).
`L:180` `egress_gate_off() {` is `probe.sh:113-116` (flush + policy ACCEPT) and stamps the run's `gate.json`.
`L:203` `egress_ns_destroy() {` is the trap body of `probe.sh:26-32`, by name, never by pattern.
`L:157` `egress_ns_run() { local ns=$1; shift; ip netns exec "$ns" "$@"; }` is the unit's execution seam.

Beyond the spike, and why:
* `L:93` writes a per-namespace `resolv.conf` naming a blackhole resolver inside the namespace's own /24. The spike recorded
  "DNS resolution inside the netns (no resolver configured)" as NOT verified; without a configured resolver a DNS canary
  fails for want of a resolver, which is the AF-AP-22 shape. With this resolver the query is on-link and the DROP policy is
  what stops it — measured below.
* `L:140` `egress_ns_gate_state() {` and `L:149` `egress_ns_mechanism() {` OBSERVE the namespace (OUTPUT policy; veth peer
  present) instead of letting the collector assert them, so a bundle collected after the mutation records `disabled` whether
  or not the collector meant to.
* `L:170` `egress_ns_drop_counter() {` reads the OUTPUT policy's packet counter — the evidence that the gate fired.
* `L:124` `egress_ns_create_isolated() {` is the committed AF-AP-1 control: the same gate with NO veth.

### The collector

`R:42` `SCRUBBED="HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY http_proxy https_proxy all_proxy no_proxy"` — every canary runs
with the venue's proxy variables removed (§7 D6). `R:52` `resolve4() {` resolves model hosts OUTSIDE the namespace;
`R:60` `not_run() {` records a host that will not resolve as `status: not-run`, which the checker DEFERS on.
`R:69` `DROP_BEFORE=$(egress_ns_drop_counter "$NS")` and `R:106` `DROP_AFTER=$(egress_ns_drop_counter "$NS")` bracket the run;
`R:113` `GATE_STATE=$(egress_ns_gate_state "$NS")` and `R:114` `MECHANISM=$(egress_ns_mechanism "$NS")` are observed, not claimed.

### The sandbox mechanism run — the mechanism leg re-proven on the PIN

Three bundles were collected on a REAL network namespace in this sandbox, each by `run_canaries.sh` against stand-in HTTP
listeners started and killed by pid. Gate ON:

```
recorded: curl C4 example.com:443 denied rc=7 — OSError [Errno 101] Network is unreachable
gate-fired: curl OUTPUT policy DROP 0 -> 10 packets
PASS: S0-05 no-direct-egress - 1 units, 11 canaries failed as required, positive controls 1/1
CHECK1-RC=0
```

Gate OFF (`egress_gate_off`, then the same suite): `egress-permitted: gate-disabled`, `CHECK2-RC=1`.
Total isolation (`egress_ns_create_isolated`): `positive-control-failed: curl`, `CHECK3-RC=1`.
A direct, library-free control ran alongside: `unshare --net -- curl http://<host-ip>:12800/v1/models` →
`curl: (7) Failed to connect to 10.201.136.1 port 12800 after 0 ms: Couldn't connect to server`, `bare-unshare-C0-rc=7`.

The committed gate-on bundle is `proofs/S0-05/fixtures/evidence-mechanism-sandbox/`, `runtime.json` carrying
`"venue": "sandbox"`, `"drop_counter_before": 0`, `"drop_counter_after": 10`, and the seven-line rule list. Its label is the
council's verbatim one: **mechanism proven, containment unproven**.

### The one measurement that makes the negative control non-vacuous

C6 is the only canary whose verdict the firewall alone decides, and it flips across the three bundles:

| bundle | C6 rc | C6 detail |
|---|---|---|
| gate ON | 28 | `curl: (28) Failed to connect to 10.201.136.1 port 12801 after 5002 ms: Timeout was reached` |
| gate OFF | 0 | `curl exit 0, HTTP 200` |
| total isolation | 7 | `curl: (7) Failed to connect to 10.201.136.1 port 12801 after 0 ms: Couldn't connect to server` |

C5 moves the same way (gate ON → `PermissionError [Errno 1] Operation not permitted`, the kernel reporting the OUTPUT DROP to
the sender; gate OFF → `TimeoutError timed out`). Everything else fails identically in both gate states — see §7 D4.

---

## 4. MUTANTS — 20 applied to the PRODUCTION code in the archive copy, never to the shared tree

Each mutant was applied to `gateF/proofs/S0-05/{check_egress.py,netns_lib.sh}`, the whole test file run with `-x`, then the
file restored from a pristine in-memory copy (verified identical to the working tree afterwards).

| mutant | verdict | killer test |
|---|---|---|
| GATE-OFF-ACCEPTED | CAUGHT | `test_gate_off_bundle_is_red_with_the_seed_reason` |
| GATE-CHECK-AFTER-CANARIES | CAUGHT | `test_gate_off_bundle_is_red_with_the_seed_reason` |
| POSITIVE-CONTROL-OPTIONAL | CAUGHT | `test_positive_control_is_mandatory[c0-deleted]` |
| BARE-UNSHARE-ACCEPTED | CAUGHT | `test_bare_unshare_bundle_is_red_on_the_positive_control` |
| CANARY-SUCCESS-ACCEPTED | CAUGHT | `test_a_canary_that_succeeded_is_caught[C1]` |
| RULES-DIGEST-UNPINNED | CAUGHT | `test_a_widened_rule_set_with_a_matching_digest_is_caught` |
| RULES-DIGEST-RECORDED-UNBOUND | CAUGHT | `test_rules_that_do_not_hash_to_the_digest_are_caught` |
| DNS-CANARY-DROPPED | CAUGHT | `test_sandbox_mechanism_bundle_passes` |
| UNIT-SET-EMPTY-PASSES | CAUGHT | `test_an_empty_evidence_root_is_red` |
| DEFERRED-AS-PASS | CAUGHT | `test_an_absent_evidence_root_defers` |
| FIFO-HANG | CAUGHT | `test_a_fifo_in_place_of_evidence_is_rejected_without_hanging[curl/canaries.jsonl]` |
| DETAIL-UNCHECKED-vocabulary | CAUGHT | `test_a_denial_detail_from_another_mechanism_is_rejected[tls-error]` |
| DETAIL-UNCHECKED-foreign-target | CAUGHT | `test_proxy_shaped_denial_is_rejected` |
| GATE-INERT-ACCEPTED | CAUGHT | `test_a_gate_that_never_fired_is_caught[0-0]` |
| NOT-RUN-UNIT-COUNTED | CAUGHT | `test_a_malformed_units_manifest_is_rejected[no-reason]` |
| NETNS-LEAK (`egress_ns_destroy` → no-op) | CAUGHT | `test_library_round_trip_leaves_no_namespace_behind` |
| LOOPBACK-ALIAS-ACCEPTED | CAUGHT | `test_a_forged_loopback_ip_cannot_whitelist_a_proxy_denial` |
| PASS-RATIO-COUNTS-RECORDS | CAUGHT | `test_the_pass_line_counts_units_not_records` |
| COUNTER-READS-DROP-ONLY | CAUGHT | `test_the_drop_counter_reads_both_policies` |
| PASS-RATIO-TAUTOLOGY (denominator `{positives}` for `{len(units)}`) | **SURVIVED — EQUIVALENT** | — |

`mutants: 16  survived: 0` (first batch) and `extra mutants: 4  survived: 1` (second batch).
The one survivor is a proved equivalent, not a gap: `C:214` `def check_positive_control(records, unit):` returns exactly 1
per unit and is called once per unit at `C:334` `positives += check_positive_control(records, unit)`, so `positives == len(units)` unconditionally at the PASS line. The mutation
that mattered — the numerator counting C0 RECORDS instead of units — is the separate `PASS-RATIO-COUNTS-RECORDS` row, and it
is CAUGHT. I am reporting the survivor rather than quietly dropping it.

The FIFO mutant's run took 33.8 s against a 30 s subprocess timeout: that is the hang the `C:123` `def _require_regular(path, name):`
guard prevents, observed rather than argued.

---

## 5. NOT_DONE — stated first-class

* **NOT run here: every live-unit leg.** `PC:2` `run_s0_05_units.sh` was authored and `bash -n`-parsed, never executed. It needs
  the live units and this lane does not touch the PC bridge. Nothing in it is an observation — the file calls its own
  content `a PLAN read from` the plan docs, at `PC:6`.
* **NOT run here: `hermes-acp`, `buzz-acp`, the S0-01 scripted backend inside a namespace.** No S0-01 launch has ever been run
  inside a network namespace. `PC:99` carries that as a `NOT VERIFIED` comment above the launch.
* **NOT built: the NAT-ed namespace variant** in which the general internet is routable and only the allow-list holds providers
  back. Without it, §7 D4 stands.
* **NOT built: units that do not exist** — `memory-adapter`, `ai-memory`, `dream-foundry`, `pandaprobe`, `harness-router`. They
  are declared `not-run` with reasons in every committed `units.json` and printed by the checker as `NOT run: <unit> — <reason>`.
* **NOT run: the gVisor/runsc interaction.** `spikes/selective-egress/result.json` listed it as unverified and it still is.
* **NOT done: no proof minted, no ledger row, no registry edit, no commit, no push.** `proofs/S0-05/spec.json` exists;
  `proofs/S0-05/result.json` does not. S0-05 remains `ABSENT`. The spec's live positive leg
  (`check_egress.py proofs/S0-05/evidence`) returns exit 2 here — `test_the_committed_spec_positive_leg_defers_here` pins that.
* **NOT verified: that the coordinator's mint will stay green.** Creating `proofs/S0-05/` changes no other proof's attestation
  (`scripts/validate-ledger` hashes the shared closure plus `proofs/<id>/`), and `proofs/ledger.json` is untouched, but I did
  not run `validate-ledger integrity` as part of the lane gate — that is the coordinator's step.
* **NOT done: performance, persistence across restarts, IPv6.** No canary covers IPv6; `expected_rules` and the library are
  IPv4-only and reject a non-dotted-quad allow entry (`T:399` `test_a_malformed_allow_entry_is_rejected`).

---

## 6. THE 18-CLASS PREFLIGHT over my own files (`class | site | verdict | the run | fix`)

| class | instances | verdict |
|---|---|---|
| 1 presence-gated | 12 sites in `check_egress.py` (`.exists()`, `.is_dir()`, `.get(`) | 11 SAFE — every "absent" branch RAISES or DEFERS, each exercised by `T:204` `test_positive_control_is_mandatory`, `T:470` `test_a_malformed_units_manifest_is_rejected`, `T:481` `test_an_absent_evidence_root_defers` and `T:524` `test_missing_evidence_files_are_named`; 1 **DEFECT** → the `ip` alias, fixed, see class 18 |
| 2 reads outside the walk / no S_ISREG | 4 reads, all via `C:123` `def _require_regular(path, name):` | SAFE — guard named; `T:511` `test_a_fifo_in_place_of_evidence_is_rejected_without_hanging` drives a FIFO through all four of `canaries.jsonl`, `gate.json`, `runtime.json` and `units.json` |
| 3 stale `[-1]` / positional reads | 1 production (`C:108` `rsplit(":", 1)[0]`), ~20 test `splitlines()[0]` | SAFE (the `[0]` assertions pin the reason as the COMPLETE first line, which is stronger than a substring) — 1 **DEFECT** in the test (a positional `records(...)[0]` assumed C0 was written first) → now selects by canary id |
| 4 negative acceptance | 1 — `T:631` `test_bash_n_would_have_caught_a_broken_script`, the instrument control | SAFE — its positive half is `T:624` `test_every_new_shell_file_parses` |
| 5 substring / tail anchors classifying an outcome | ~24 | SAFE — 20 are `splitlines()[0] ==` exact or `.startswith(<complete deterministic prefix>)` where only an IP/path varies; the 4 `in result.stdout` cases assert a whole line |
| 6 env-domain fail-opens | 3 | 1 **DEFECT** (`${DROP_BEFORE:-0}` defaulted an unreadable counter to 0, inflating the delta and fail-OPENing `gate-inert`) → fixed, `R:69` now exits 3; 2 SAFE (`PC:44` `ALLOWED_HERMES` unset ⇒ the unit is declared `not-run` with a reason) |
| 7 lossy decodes | **0** | EMPTY CLASS — a result |
| 8 broad catches | 9 | SAFE — `C:143` and `C:202` `except Exception as error:` re-raise as a `Failure` (fail-closed); `connect_probe.py` classifies, and an unclassified exception yields a detail outside the vocabulary that `C:229` `def check_denials(records, unit):` rejects; `L:203` `egress_ns_destroy() {` teardown is best-effort by design and the census is its check |
| 9 waits / polls | 13 network probes + 1 launch wait | SAFE for the probes (every one bounded: `--connect-timeout 5 --max-time 8`, socket timeouts, subprocess timeouts) — 1 **DEFECT**: `PC` used a blind `sleep 10` after launching a unit → replaced with a failure-aware bounded poll whose exit condition includes the process being gone |
| 10 skips / xfails | 3 (`T:93` `NEEDS_NETNS`) | SAFE — declared reason, and they RAN here (`-rs` reported no skips in either gate run) |
| 11 world-scoped enumerations | 3 | SAFE — all scoped: `L:149` `egress_ns_mechanism() {` to the given ns, `C:315` `child.is_dir()` to the evidence root, `T:48` to the proof's own `canaries` dir, which also makes the `bash -n` corpus self-extending |
| 12 signal installs before their try | 1 (`PC:73` `trap cleanup EXIT INT TERM`) | SAFE — installed after `cleanup` is defined and before any namespace exists. `run_canaries.sh` installs none by design: the caller owns the namespace lifecycle, stated in its header |
| 13 `/proc/<pid>/exe` races | **0** | EMPTY CLASS |
| 14 mirrors of the code under test | 2 (`C:157` `def expected_rules(allowed):` vs `L:101` `_egress_apply_gate() {`; the synthetic fixture's typed rule list) | SAFE — not a mirror: `T:653` `test_library_round_trip_leaves_no_namespace_behind` compares `expected_rules` against a REAL kernel, so the oracle is the kernel, and the fixture states the rules independently |
| 15 two counters over different populations asserted equal | 1 | **DEFECT** — the PASS line printed `positive controls {positives}/{positives}`, a ratio that could not fail, over a numerator counting RECORDS → numerator now counts units, denominator `len(units)`; `T:564` `test_the_pass_line_counts_units_not_records` |
| 16 provably redundant guards | 3 candidates | SAFE — none redundant: `_is_int` rejects `7.0` (which `rc in DENIAL_RCS` accepts) and `True`; the `rc == 0` branch precedes the rc-set branch to give the specific reason, and both are separately mutated |
| 17 hardlink-clobbering writes | **0** | EMPTY CLASS — the only appends are to a file the collector truncates and owns |
| 18 other families | 3 found | (a) **DEFECT**: `C:101` `def _foreign_endpoint_in_detail(record):` accepted `record["ip"]` unconditionally, so a forged `"ip": "127.0.0.1"` would whitelist exactly the proxy-shaped denial the rule exists to reject → floor added, `T:270` `test_a_forged_loopback_ip_cannot_whitelist_a_proxy_denial` and `T:283` `test_a_real_remote_ip_alias_is_still_accepted`; (b) **DEFECT**: two comments cited `docs/INCIDENT-LOG.md` by LINE (145, 168) and the log grew to 155/178 between dispatch and gate → now cite the stable row ids; (c) **DEFECT**: the counter reader understood only a DROP policy, so gate-OFF collection exited 3 and wrote an EMPTY fixture → fixed, `T:680` `test_the_drop_counter_reads_both_policies` |

Six production defects and one test defect found by the sweep, all fixed in this lane with a test each; four of the fixes
have their own mutant row in §4 (`LOOPBACK-ALIAS-ACCEPTED`, `PASS-RATIO-COUNTS-RECORDS`, `COUNTER-READS-DROP-ONLY`, plus the
FIFO coverage extension). `AP_SCREEN` flagged `AP-32` ("hashing in edited code — is the hashed form EXACTLY what the store
holds?") at `C:170` `def rules_digest(lines):`: SAFE, and proven rather than argued — the producer hashes
`egress_ns_rules | sha256sum` (`L:161` `egress_ns_rules_sha256()`) while the consumer hashes `"\n".join(rules) + "\n"` from
`runtime.json`; the committed bundle passes that cross-language comparison, and
`T:653` `test_library_round_trip_leaves_no_namespace_behind` compares the same rule text to the kernel.

---

## 7. DISCREPANCIES — deviations from the brief, and what the evidence does NOT say

**D1 — the brief's §6 invocation cannot work as written; the stand-in does not bind 127.0.0.1.**
The brief pins `run_canaries.sh curl <ns> 127.0.0.1:<port>` and the standing rules say a stand-in listener binds `127.0.0.1`.
A fresh network namespace has its own empty loopback, so a host-loopback listener is unreachable from inside it — that is the
Chairman probe this proof is built on — `Bare netns is TOTAL isolation` at docs/research/FINDINGS-STAGE0-v1.md:98. I bound the stand-in to the veth HOST
address (`10.201.<n>.1`, the spike's own shape) and passed that as the allowed target. Re-measured here to justify the
deviation rather than assert it: `unshare --net -- curl http://10.201.136.1:12800/v1/models` → `curl: (7) … Couldn't connect
to server`. The address is RFC-1918, lives on a veth whose only peer is my namespace, and the namespace's FORWARD policy is
DROP; no listener was ever bound to a wildcard address, and both listeners were started and killed by pid.
**A reviewer who wants the literal 127.0.0.1 form must add a host-side DNAT — that is NOT built.**

**D2 — C6 is an ADDITION to the pinned C0–C5 canary set, and it is a REQUIRED denial.**
Reason: with no default route out of the namespace, C1/C2/C3/C4 fail on ROUTING, not on the firewall, so without C6 no canary
in the suite would be decided by the gate under test and the negative control would rest entirely on a JSON field. C6 is the
spike's own `negative leg: blocked port` at spikes/selective-egress/probe.sh:98, it flips 28 → 0 when the gate is flushed, and it is in
`C:59` `REQUIRED_DENIALS = ("C1", "C2", "C3", "C5", "C6")`. Dropping it is a one-token edit if the coordinator disagrees.

**D3 — `spec.json` carries an extra positive leg.** The brief pins one positive (`proofs/S0-05/evidence`). I put the committed
sandbox mechanism bundle FIRST as a second positive so the canonical contract also carries the claim my tests make about it
(AF-AP-29). The live leg still defers here, so the proof as a whole defers — `test_every_spec_leg_behaves_exactly_as_declared`
drives all four legs and pins each negative's `failure_reason` as the checker's COMPLETE first line.

**D4 — what the gate blocks versus what the topology blocks. This is the most important limit in the report.**
Only C6 and C5 are decided by iptables. C1 (for two of three hosts), C2, C3 and C4 fail with `[Errno 101] Network is
unreachable` in BOTH the gate-ON and gate-OFF bundles, because the namespace has no route off its own /24. The gate's own
firing is proven separately by the OUTPUT policy counter (`0 -> 10 packets`) and by C5's `Operation not permitted`, which only
a DROP rule produces. Read plainly: **this mechanism contains a unit by giving it exactly one reachable destination; the
firewall is what makes that destination exclusive, and the absence of a route is what makes everything else unreachable.**
A claim of the form "the iptables gate blocks api.openai.com" is NOT supported by this evidence.

**D5 — `docs/02_COMPONENT_AUDIT.md:56` ("OmniRoute is sole model API egress, not automatically sole web/tool egress") is not
settled by this mechanism.** C4 (`example.com:443`) was DENIED in every bundle — so the mechanism blocks general web egress as
well as model egress — but by the same routing barrier as D4, not by a model-specific rule. The checker therefore RECORDS C4
and asserts nothing about it (`C:254` `def check_recorded(records, unit):`).

**D6 — two venue facts poison naive canaries, and both are now defended and recorded.**
(a) This sandbox exports `HTTPS_PROXY=http://127.0.0.1:40173`. Inside the namespace curl then fails with rc 7 and curl 8.5's
generic `Couldn't connect to server` — the SAME rc and text a real gate denial produces. Defence one: `R:42` `SCRUBBED` removes the proxy
variables and `canaries/_emit.sh` unsets them again. Defence two: `C:101` `def _foreign_endpoint_in_detail(record):` rejects a
denial whose diagnostic names an endpoint other than the canary's own target. `T:256` `test_proxy_shaped_denial_is_rejected`
uses the measured string verbatim.
(b) `/etc/hosts` in this sandbox maps `api.anthropic.com` to the provider address, so C1 for that host resolves locally and
fails at connect instead of at resolution. That record is accepted (it names its own target) and the resolver's answer is
recorded in the canary line as `"resolved": "160.79.104.10"`. C5 remains the canary that actually exercises DNS egress.
**Neither fact is a property of the PC; both must be re-measured there.**

**D7 — the "bare unshare" fixture is a namespace with the same gate and NO veth, not a literal `unshare --net`.**
`egress_ns_create_isolated` was used so the bundle passes through the same collector and carries a truthful `gate.json`. The
distinguishing property (total isolation kills the positive control) is identical, and the literal form was measured beside it
(D1). In that bundle `"gate": "enabled"` means "the DROP gate has not been flushed", which is vacuously true where there is no
veth; `"mechanism": "netns-no-veth"` is what tells them apart, and
`T:703` `test_the_isolated_control_has_no_veth_and_fails_its_positive_control` re-derives that shape live.

**D8 — the canaries share the unit's network namespace; they are not the unit's own sockets.** They prove the NAMESPACE cannot
reach a provider, which is the boundary `## 6. Network segmentation` at docs/05_SECURITY.md:74 specifies. They prove nothing about a unit's in-process
client behaviour. `PC:20` marks the routed variant `NOT BUILT` in the file that will run the live legs.

**D9 — classification unchanged.** This lane delivers the mechanism leg re-proven on the PIN plus the full suite, checker,
spec and fixtures. The seed's second assertion ("network canaries FAIL from every non-OmniRoute unit") is NOT met: one unit
(`curl`) was contained here and no live unit was. The council's label stands verbatim: *mechanism proven, containment unproven*.

**D10 — a lane-process bit, not a code defect.** My first process census used `pgrep -af '[h]ttp\.server'` in a command line
that also echoed the plain token, so the pattern matched my own shell. The bracket trick is not enough when the same command
line prints the literal string. Final censuses below were taken without the token on the line.

---

## 8. CENSUS — nothing of mine survives

Taken after the final gate and the mutation audit:

```
=== netns census ===          ip netns list  ->  (no output)
=== /etc/netns leftovers ===  ls -A /etc/netns  ->  (no output)
=== veth leftovers ===        ip -o link show | grep -cE ' (eh|en)[0-9a-f]{8}@'  ->  0
```

Every namespace this lane created was named `s0-05-e1-<nonce>` (or `s0-05-e1-b<nonce>` for the isolated control), destroyed by
name in a trap, and is absent from `ip netns list`. Both stand-in listeners were killed by pid — no `kill`-by-name was used
anywhere. One leftover `/etc/netns/s0-05-e1-820edf36` appeared during the NETNS-LEAK mutant (whose whole point is a no-op
destroy) and was removed by hand; the census above is after that removal.

---

## 9. SELF-ATTACK — the three most likely ways this is wrong

**1. "The suite is green because nothing in the namespace can reach anything, gate or no gate."**
This is the AF-AP-22 trap and it is half true — see D4. What rules out the vacuous reading: C6 flips 28 → 0 → 7 across the three
committed bundles; C5's reason changes from `Operation not permitted` (a DROP reported to the sender) to `TimeoutError timed
out` when the gate is flushed; and the OUTPUT policy counter advanced `0 -> 10` during the gate-ON run, which `C:277` requires
and `T:409` `test_a_gate_that_never_fired_is_caught` mutates. A bundle in which the gate never fired cannot pass. What is NOT ruled out: that on a routed venue the
model-endpoint canaries would behave differently — stated as D4 rather than papered over.

**2. "The checker is graded only against bundles I produced."**
Partly true and deliberately mitigated: 20 mutants on the production code (§4), 30-odd hostile bundle mutations built in
`tmp_path` from copies, and one hostile input I did NOT invent — the proxy-shaped denial, which the checker rejected on its own
during the first real collection run and which is now `T:256` `test_proxy_shaped_denial_is_rejected`. The residual risk is the shape I did not think of; the pre-mint
gate (AF-AP-36) is the coordinator's, and nothing is minted here.

**3. "The rule digest proves the rules were not weakened."**
It proves the recorded rules hash to the recorded digest AND equal the set derived from the DECLARED allow-list. It does NOT
prove the recorded rules were the ones in force — a collector that lies about both `rules` and `allowed` produces a consistent
bundle. What narrows that: the digest is computed inside the namespace at collection time by `L:161` `egress_ns_rules_sha256()`, the gate state and
mechanism are read from the namespace rather than asserted — `L:140` `egress_ns_gate_state() {` and
`L:149` `egress_ns_mechanism() {` — and `T:653` `test_library_round_trip_leaves_no_namespace_behind` compares the same rule
text to a real kernel. A collector running on a venue nobody watched is still trusted for
the fact that it ran there — that is what the `runtime.json` venue field records and what the live PC legs will have to
establish independently.

**Fourth, smaller:** `test_the_collector_refuses_an_unreadable_drop_counter` drives `run_canaries.sh` against a namespace that
does not exist, so it proves the fail-loud guard, not the whole collector. The collector's happy path is proven only by the
three real collections, whose outputs are the committed fixtures.
