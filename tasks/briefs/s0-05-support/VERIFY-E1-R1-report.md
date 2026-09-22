# VERIFY-E1-R1 — adversarial grade of the S0-05 mechanism guard (E1-R1)

Role: `adversarial-verifier` (Opus 5), IN THIS SANDBOX as root (uid 0; `ip`, `iptables`, veth available).
PIN `860ab9e`. Honey `full`. This is a GATE RECOMMENDATION and an evidence table — the coordinator owns the gate.

## OUTCOME

**GATE RECOMMENDATION: NOT-READY** — one blocker, `F1`, and the fix is two lines inside the boundary.

The production guard is **correct and I proved it against the real F1 instance**: on a bundle collected by the REAL
`proofs/S0-05/run_canaries.sh` from a totally isolated namespace whose DROP counter genuinely advances, the pre-repair
checker (`953ccfe`, sha256 `59b884c6e60fa784`) prints `PASS: S0-05 no-direct-egress - 1 units, 11 canaries failed as
required, positive controls 1/1` rc 0, and the repaired checker at the PIN prints `total-isolation: curl
mechanism=netns-no-veth` rc 1. The guard fires for EVERY run unit before any canary is read (three instruments agree),
refuses every hostile `gate.json` shape I could build (17 shapes, 0 fail-open), and 9 of my 13 fresh mutants died.

What blocks is the ONE test that claims to be that proof. `tests/test_s0_05_egress.py:795-862` (`@NEEDS_NETNS`) builds a topology whose
OUTPUT DROP counter never advances — `0 -> 0` on 4 of 4 runs — so the bundle it produces was ALREADY refused before the
repair, by `proofs/S0-05/check_egress.py:280` `gate-inert: {unit} OUTPUT DROP counter did not advance`. Its docstring at
`tests/test_s0_05_egress.py:806-807` states `On the PIN's checker this bundle` PASSES (rc 0); measured, the PIN's checker
returns rc 1 `gate-inert: curl OUTPUT DROP counter did not advance (0 -> 0)`. Its comment at
`tests/test_s0_05_egress.py:836` states `the DROP counter advances despite total isolation`; it does not. So the
increment ships a committed artifact whose load-bearing factual claim is false, and the F1 hollow green has no committed
regression lock. The lane predicted exactly this in its own §7.1 ("Most likely wrong: the root-only live topology does
not reproduce F1 … Sandbox execution is mandatory before acceptance") and left it NOT-done — this run is that check, and
the answer is that it does not reproduce F1. The repair for it is measured and pasted in F1: add one route inside the
namespace and retarget C6.

## IDENTITY — measured vs the brief's table

| file | brief (PIN) | measured at `860ab9e` | measured in the worktree | verdict |
|---|---|---|---|---|
| `proofs/S0-05/check_egress.py` | `5b766582a9a03f91` | `5b766582a9a03f91` | `5b766582a9a03f91` | MATCH |
| `proofs/S0-05/spec.json` | `ed6edbd1c408ad83` | `ed6edbd1c408ad83` | `ed6edbd1c408ad83` | MATCH |
| `tests/test_s0_05_egress.py` | `7545714460183c94` | `7545714460183c94` | `7545714460183c94` | MATCH |
| `proofs/S0-05/run_canaries.sh` | `6f7298077aa39819` | `6f7298077aa39819` | `6f7298077aa39819` | MATCH |
| `proofs/S0-05/netns_lib.sh` | `1b2bd911d54262d3` | `1b2bd911d54262d3` | `1b2bd911d54262d3` | MATCH |

`git diff --stat 860ab9e -- proofs/S0-05 tests/test_s0_05_egress.py` is empty. The pre-repair checker used throughout is
`git show 953ccfe:proofs/S0-05/check_egress.py`, sha256 `59b884c6e60fa784`, identical to `860ab9e~1`'s copy (measured).
`proofs/S0-05/result.json` is absent — S0-05 is NOT minted, so no attested-input regeneration is in play.

---

## ITEMS 1–10 — finding inventory (no severity filter)

### Item 1 — reachability of the guard from the CLI entry. SOLID: no such path exists.

`main` (`proofs/S0-05/check_egress.py:354`) → `check` (`:314`) → PHASE 1 (`:326` `# PHASE 1`) → PHASE 2 (`:335`
`# PHASE 2`). Three independent instruments agree that the ONLY canary reader is `read_records`, and that it has exactly
one call site:

* ripwire `callers of="read_records"` → `count="1" total="1"` → `<s t="fn" n="check" p="proofs/S0-05/check_egress.py:314"/>`, i.e. `def check(root, required_units)`;
  same for `read_gate` (`count="1"`).
* graft `ask --in proofs/S0-05` places `read_records` at L191-L214 and `check` at L314-L351.
* literal sweep of call sites: `:329` `gates[unit] = read_gate(root / unit, unit)` (PHASE 1) and `:338`
  `records = read_records(root / unit, unit)`, `:339` `check_positive_control`, `:340` `check_denials`, `:342`
  `check_runtime_and_rules` (all PHASE 2).

PHASE 1 iterates the WHOLE `units` list before PHASE 2 begins, so no unit's canaries can be read before every unit's
mechanism is asserted. Reproduced, not merely read — six unit-set edge cases, each `rc=1`, first line pasted:

```
declared not-run but present           rc=1  first='unit-declared-absent-but-present: hermes-acp'   (:321, before PHASE 1)
declared-run unit missing on disk      rc=1  first='unit-missing: hermes-acp'                       (:323, before PHASE 1)
undeclared stray dir, bad mechanism    rc=1  first='total-isolation: zz-stray mechanism=netns-no-veth'
--units '' with bad mechanism          rc=1  first='total-isolation: curl mechanism=netns-no-veth'
no unit directories at all             rc=1  first='no-units: no run unit in <root>'                (:344 `if not units:`)
no units.json, 2nd mechanism bad       rc=1  first='total-isolation: hermes-acp mechanism=netns-no-veth'
```

The decisive ordering probe: on `evidence-synthetic-pass` with unit 2's mechanism flipped AND unit 1's `canaries.jsonl`
DELETED, the answer is `total-isolation: hermes-acp mechanism=netns-no-veth`, never `evidence-missing` — PHASE 1 for the
second unit precedes PHASE 2 for the first. **F-none. No finding.**

### Item 2 — the producer's detector as a class signal. Two misreads exist; both are ADVERSARY-ONLY.

`egress_ns_mechanism` reads ONE fact — whether the derived name exists in the namespace
(`proofs/S0-05/netns_lib.sh:150` `ip netns exec "$1" ip -o link show "$(egress_ns_if "$1")"`, then `:151`
`echo veth-iptables` / `:153` `echo netns-no-veth`). It is a link-EXISTENCE probe, not a link-FUNCTION probe. Measured
live on one namespace built by the library's own `egress_ns_create`:

```
[A] routes UP:   10.201.115.0/24 dev en729321b0 proto kernel scope link src 10.201.115.2
[A] mechanism=veth-iptables  tcp-to-host: ConnectionRefusedError 111      <- the packet REACHED the host
[B] routes DOWN: (empty)
[B] mechanism=veth-iptables  tcp-to-host: OSError 101                     <- ENETUNREACH: TOTAL ISOLATION
[C] after rename: mechanism=netns-no-veth  links=lo,renamed0@if104        <- selective egress works, reads no-veth
```

**F2 — FOLLOW-UP — `veth-iptables` recorded while total isolation holds; the REPAIRED checker returns rc 0 PASS.**
Evidence: reproduced live through the real collector and the real PIN checker. Bundle: `egress_ns_create` with
`allowed=127.0.0.1:12800`, then one operator action `ip -n <ns> link set en<hash> down`, an internal routed pair for the
counter, and a loopback stand-in inside the namespace. Collector wrote `"mechanism": "veth-iptables"`, `"gate":
"enabled"`, `drop 0 -> 5`; the PIN checker printed `gate-fired: curl OUTPUT policy DROP 0 -> 5 packets` and
`PASS: S0-05 no-direct-egress - 1 units, 11 canaries failed as required, positive controls 1/1` rc 0. Classification:
**ADVERSARY-ONLY**, not library-reachable — no library function brings the link down, and every PARTIAL create path
returns before `_egress_apply_gate`, so the bundle records `gate: disabled` and dies at
`proofs/S0-05/check_egress.py:332` `gates[unit]["gate"] != "enabled"` instead. Per the brief's own rule ("a finding here
blocks only if a library-reachable path produces the misread") this does NOT block. It bounds the claim: the guard
asserts the LABEL the collector wrote, not containment as a property. This is VERIFY-E1's residue #13 (the COLLECTOR's
seam) made concrete. **Fix:** have `egress_ns_mechanism` require the derived interface to be `UP` with an address, or
add a second recorded fact (the namespace's route table) the checker can bind. **Red control:** the bundle above.

**F3 — INFO — the reverse misread, fail-closed.** A renamed namespace interface reads `netns-no-veth` while selective
egress still works ([C] above): a FALSE RED, never a false green. Not library-reachable. No action.

### Item 3 — kill-switch on the live test. It kills, but it does not prove what it claims.

**F1 — BLOCKER — `tests/test_s0_05_egress.py:795-862` (`@NEEDS_NETNS`) does not reproduce F1; its docstring and its comment are false.**

* **Evidence level:** reproduced, four times, through the REAL `proofs/S0-05/run_canaries.sh`, the REAL checker at the
  PIN and the REAL pre-repair checker. SOLID.
* **Contract:** the brief's item 3 ("Does it prove what it claims?"); the PREMISE line "the PIN's checker prints PASS
  rc 0 on the live isolated topology — F1 reproduced live"; CLAUDE.md's #1 rule ("the hollow green lives in PROSE too");
  AF-AP-36 (a reviewer-reported mutation of a proof's evidence becomes a committed FAILING regression test).
* **file:line vs observed.** `tests/test_s0_05_egress.py:836` asserts in prose `the DROP counter advances despite total
  isolation`; `tests/test_s0_05_egress.py:806-807` asserts `On the PIN's checker this bundle` PASSES (rc 0). Measured,
  the bundle the test writes carries `drop_counter_before=0, drop_counter_after=0` on 4 of 4 runs (deterministic):

  ```
  run1: drop 0 -> 0     run2: drop 0 -> 0     run3: drop 0 -> 0     (+ the first, retained, bundle)
  ```

  Mechanism: the internal pair's two addresses (`tests/test_s0_05_egress.py:819` `ip -n {ns} link add ve1a type veth peer name ve1b`, then `192.0.2.1/31` and `192.0.2.0/31`) are BOTH local to the namespace, so C6's target
  (`tests/test_s0_05_egress.py:840` `192.0.2.0:12801`) is delivered over loopback and matched by the gate's
  `-A OUTPUT -o lo -j ACCEPT`. Nothing is ever dropped. The recorded C6 is
  `curl: (7) Failed to connect to 192.0.2.0 port 12801 after 0 ms: Couldn't connect to server` — an on-link refusal,
  not a gate denial.
* **Canonical reproduction (the discriminator), pasted:**

  ```
  $ python3 <953ccfe check_egress.py, sha 59b884c6e60fa784> /tmp/s5/bt/test_the_motivating_instance_i0/evidence
  gate-inert: curl OUTPUT DROP counter did not advance (0 -> 0)
  exit 1 per contract
  rc=1                                   <- NOT the rc-0 PASS the docstring promises
  ```

  and through the test itself, the pre-repair checker dropped into a scratch copy of the PIN tree:

  ```
  $ cd <scratch>/REDFIRST-953ccfe && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_s0_05_egress.py -q \
      -p no:cacheprovider --basetemp=/tmp/s5/rf2 -k "motivating or bare_unshare" --tb=line
  E   AssertionError: gate-inert: curl OUTPUT DROP counter did not advance (0 -> 0)
    - total-isolation: curl mechanism=netns-no-veth
    + gate-inert: curl OUTPUT DROP counter did not advance (0 -> 0)
  <scratch>/REDFIRST-953ccfe/tests/test_s0_05_egress.py:851: AssertionError
  2 failed, 102 deselected in 1.43s
  ```

  (item 3b, answered literally: the red state is a `gate-inert` refusal, not the promised rc-0 PASS. The assertion that
  fires is the right one — `tests/test_s0_05_egress.py:851` `total-isolation: curl mechanism=netns-no-veth` — so the test IS a guard discriminator; it is not a
  reproduction of F1.)
* **Material effect.** The delivered increment states a checkable fact about the production path that the production
  path falsifies, and the only committed test that claims to lock the motivating hollow green does not exercise it. The
  guard's remaining locks are relabelled-fixture mutations, which never see the drop-counter interaction.
* **The corrected topology, measured here (this is the fix, not a suggestion).** Add ONE route inside the namespace and
  point C6 at a routed, non-local address — everything else unchanged:

  ```
  ip -n <ns> route add 198.51.100.0/24 dev ve1a          # after the two /31 addresses
  run_canaries.sh curl <ns> 127.0.0.1:12800 <root> 198.51.100.7:12801 sandbox
  ```

  Result, through the REAL collector: `drop 0 -> 5`, C6 `curl: (28) Failed to connect to 198.51.100.7 port 12801 after
  5002 ms: Timeout was reached`. Then:

  ```
  $ python3 <953ccfe checker> <routed bundle>
  recorded: curl C4 example.com:443 denied rc=7 — OSError [Errno 101] Network is unreachable
  gate-fired: curl OUTPUT policy DROP 0 -> 5 packets
  PASS: S0-05 no-direct-egress - 1 units, 11 canaries failed as required, positive controls 1/1
  rc=0                                            <- F1 REPRODUCED LIVE, the true hollow green

  $ python3 proofs/S0-05/check_egress.py <routed bundle>
  total-isolation: curl mechanism=netns-no-veth
  exit 1 per contract
  rc=1                                            <- the guard kills it
  ```

  `0 -> 5` is byte-for-byte the counter VERIFY-E1 F1 reported, so this is that verifier's topology, restored.
* **Predicate:** contract-mapped ✔ · reproduced through the exact production consumer and producer at the PIN ✔ ·
  materially effective (a false evidence claim in a committed artifact; no regression lock on the motivating instance) ✔
  · concrete discriminator, with both the defective and the corrected topology measured ✔ · in-boundary
  (`tests/test_s0_05_egress.py`, two lines, the same focused repair) ✔. **ALL FIVE HOLD.**
* **What this finding does NOT say:** the guard is wrong. It is right, and I proved it against the real instance above.

**F4 — INFO — item 3a: the stand-in genuinely serves INSIDE the namespace; the test is not a tautology.** Scratch edit
of `tests/test_s0_05_egress.py:776` `["ip", "netns", "exec", ns, sys.executable, str(script), str(port)],` to launch on
the HOST loopback → `AssertionError: loopback stand-in did not become ready inside the namespace`
(`tests/test_s0_05_egress.py:792` `loopback stand-in did not become ready inside the namespace`), `1 failed, 103 deselected in 5.31s`. The readiness probe, which also runs
`ip netns exec`, is load-bearing.

**F5 — INFO — item 3c: teardown is sound on the failing path and does NOT widen VERIFY-E1 F7.** A scratch copy with
`assert False, "deliberate teardown probe"` inserted right after the collector assertion fails at
the inserted line (anchor `tests/test_s0_05_egress.py:842` `assert run.returncode == 0, run.stderr`) and the census is still clean — `ip netns list` empty, `ip -o link show type veth`
empty, `pgrep -af '[l]oopback_standin'` none. `tests/test_s0_05_egress.py:855` `listener.terminate()` runs BEFORE
`tests/test_s0_05_egress.py:861` `_lib(f'egress_ns_destroy {ns}')`, so no process is left inside the namespace at
destroy time — F7's invisible-residue class is not enlarged. The census assertion at
`tests/test_s0_05_egress.py:862` `assert ns not in subprocess.run` is outside the `finally` and is skipped on a failing path; the destroy is not.

**F6 — INFO — item 3d: nothing reaches outside this container.** Every connect runs inside the namespace, which after
`egress_ns_create_isolated` has no link off itself: in the retained live bundle C2/C3/C4/C5 are all
`OSError [Errno 101] Network is unreachable`, C6 is an on-link refusal, C0 is `127.0.0.1:12800`. The only host-side
network operation is `resolve4`'s `getaddrinfo` for three model hostnames and `example.com`
(`proofs/S0-05/run_canaries.sh:104` `run_canary c6_blocked_local.sh` and its siblings run inside the namespace; the resolution happens outside by
design). No listener of mine bound anything but `127.0.0.1` inside a namespace. Census clean after every live run.

### Item 4 — the exact-reason contract. It holds on the FIRST line by EQUALITY, and mutants prove it.

`tests/test_s0_05_egress.py:650` `assert result.stdout.splitlines()[0] == leg["expect"]["failure_reason"]` binds
`proofs/S0-05/spec.json:39` `"failure_reason": "total-isolation: curl mechanism=netns-no-veth"`. Attacks:

* **reason with a suffix** (`M18`, VERIFY-E1's own suggested wording `… is not selective egress`): killed by 8 tests —
  the four `test_a_mechanism_mutation_is_rejected_by_class` rows, `test_bare_unshare_bundle_is_red_as_total_isolation`,
  `test_every_spec_leg_behaves_exactly_as_declared`, `test_total_isolation_precedes_a_disabled_gate` and the live test.
  `8 failed, 96 passed in 6.52s`.
* **unit name dropped** (`M9`): same 8 killers, `8 failed, 96 passed in 5.84s`.
* **the reason on the SECOND line after a `NOT run:` line:** structurally impossible and measured so. `check` returns a
  LIST that `main` prints only on success; a `Failure` propagates before any print. On `evidence-synthetic-pass` (five
  `NOT run:` lines) every guard refusal prints the class reason as line 1 with no `NOT run:` line at all — e.g. both
  units flipped → `total-isolation: curl mechanism=netns-no-veth`, `lines=2`.

**F7 — INFO — the PRODUCTION runner is weaker than the test, by design of the runner, not of this repair.**
`scripts/proof-runner:195` matches the declared reason with `if expected_reason in line` over ANY line of stdout+stderr,
so a suffixed or second-line reason would satisfy the minting path. The equality binding lives only in
`tests/test_s0_05_egress.py:650` `leg["expect"]["failure_reason"]` (AF-AP-29 held by the test). Out of this increment's boundary; S0-05 is not minted.
Worth stating the positive: because `proofs/S0-05/spec.json:39` now names the class reason `total-isolation: curl mechanism=netns-no-veth`, the runner itself
discriminates the guard — with the guard deleted the bare-unshare leg yields `positive-control-failed: curl`, which
contains the declared reason nowhere, so the leg would fail `negative-control-unmet`.

### Item 5 — hostile `gate.json` shapes. 17 shapes, 0 fail-open.

Every row measured on a scratch copy of `evidence-mechanism-sandbox`; `rc` and the FIRST stdout line pasted:

```
value 'veth-iptables\n'                rc=1  lines=3    bytes=67        first='total-isolation: curl mechanism=veth-iptables'
value newline + forged PASS            rc=1  lines=3    bytes=160       first='total-isolation: curl mechanism=veth-iptables'
value '\nveth-iptables'                rc=1  lines=3    bytes=67        first='total-isolation: curl mechanism='
value newline + declared reason        rc=1  lines=3    bytes=100       first='total-isolation: curl mechanism=x'
value with NUL                         rc=1  lines=2    bytes=67        first='total-isolation: curl mechanism=veth-iptables\x00'
value NUL in middle                    rc=1  lines=2    bytes=67        first='total-isolation: curl mechanism=veth\x00-iptables'
value 1 MiB                            rc=1  lines=2    bytes=1048629   first='total-isolation: curl mechanism=AAAA…'
duplicate mechanism key (bad,good)     rc=0  lines=8    bytes=595       first='NOT run: buzz-acp — live unit runs on the PC …'
duplicate mechanism key (good,bad)     rc=1  lines=2    bytes=66        first='total-isolation: curl mechanism=netns-no-veth'
gate.json is a JSON list               rc=1  lines=2    bytes=70        first='evidence-invalid: curl gate.json is not an object'
mechanism is a dict                    rc=1  lines=2    bytes=75        first="total-isolation: curl mechanism={'m': 'veth-iptables'}"
mechanism is a number                  rc=1  lines=2    bytes=54        first='total-isolation: curl mechanism=1'
mechanism is a float                   rc=1  lines=2    bytes=56        first='total-isolation: curl mechanism=1.0'
mechanism is a zero                    rc=1  lines=2    bytes=54        first='total-isolation: curl mechanism=0'
value CR + forged PASS                 rc=1  lines=3    bytes=160       first='total-isolation: curl mechanism=netns-no-veth'
curl gate.json -> hermes gate.json     rc=1  lines=2    bytes=75        first='evidence-missing: curl gate.json is not a regular file'
curl gate.json -> committed original   rc=1  lines=2    bytes=75        first='evidence-missing: curl gate.json is not a regular file'
```

Symlinks die at `proofs/S0-05/check_egress.py:131` `if not stat.S_ISREG(path.lstat().st_mode):` — `lstat`, so even a
symlink to the legitimate committed file is refused. Non-strings are rendered by `str` with no normalisation, exactly as
the four committed parametrised rows declare (`tests/test_s0_05_egress.py:154` `"trailing-space-mechanism"`).

**F8 — INFO — an embedded newline splits the reason across lines but never flips the verdict.** `splitlines()[0]`
still discriminates in every consumer I exercised, and a forged `PASS:` line on line 2 leaves rc 1. The one reachable
consequence is on `scripts/proof-runner:195`'s any-line `expected_reason in line` substring match (F7): a value like
`"x\ntotal-isolation: curl mechanism=netns-no-veth"` puts the DECLARED reason on line 2 while line 1 says
`total-isolation: curl mechanism=x`. Both are the guard firing, so the semantic difference is nil. No action.

**F9 — INFO — the reason is printed unbounded.** A 1 MiB `mechanism` produces 1,048,629 bytes of stdout, all of it the
refusal line. Fail-closed, but a hostile bundle can dictate the size of a recorded `failure_reason`. Optional hardening
only (truncate the interpolated value); does not qualify on its own.

**F10 — INFO — duplicate JSON keys are last-wins, with no second parser to disagree.** `{"mechanism":"netns-no-veth",
…,"mechanism":"veth-iptables"}` parses as `veth-iptables` and the bundle PASSES (rc 0). Every other reader of
`gate.json` in this pipeline is also Python `json` (`egress_gate_off`, `proofs/S0-05/netns_lib.sh:188`), so there is no
parser differential to exploit, and a forger who can write the file can simply write the good value once. No action.

### Item 6 — two-unit ordering. Every shape is red; precedence across units is POSITIONAL.

```
2nd gate.json = FIFO                   rc=1  first='evidence-missing: hermes-acp gate.json is not a regular file'
2nd gate.json = directory              rc=1  first='evidence-missing: hermes-acp gate.json is not a regular file'
2nd gate.json = 0 bytes                rc=1  first='evidence-invalid: hermes-acp gate.json Expecting value: line 1 column 1 (char 0)'
2nd mech flipped + 1st canaries gone   rc=1  first='total-isolation: hermes-acp mechanism=netns-no-veth'
2nd mech flipped + 1st C2 reachable    rc=1  first='total-isolation: hermes-acp mechanism=netns-no-veth'
both units flipped                     rc=1  first='total-isolation: curl mechanism=netns-no-veth'
1st mech flipped + 2nd gate off        rc=1  first='total-isolation: curl mechanism=netns-no-veth'
1st gate off + 2nd mech flipped        rc=1  first='egress-permitted: gate-disabled'
```

No canary of `curl` is read before `hermes-acp`'s gate is asserted (rows 4 and 5 are the discriminators: deleting unit
1's canaries or making one of them succeed changes nothing).

**F11 — INFO — the ORDER claim is per-unit, not global.** `tests/test_s0_05_egress.py:176` `total-isolation: curl mechanism=netns-no-veth` proves the mechanism guard
precedes the gate-state check WITHIN one unit. Across units the PHASE-1 loop body is read-gate → mechanism → gate-state
per unit, so unit 1's gate-state check precedes unit 2's mechanism check (last row). Both outcomes are refusals and the
frozen contract fixes no cross-unit precedence, so this is a documented property, not a defect.

**F12 — FOLLOW-UP — `read_gate` never binds `gate["unit"]` to the directory it was read from, though `read_records`
does.** `proofs/S0-05/check_egress.py:181` `for key in GATE_KEYS:` checks presence only, while
`proofs/S0-05/check_egress.py:211` `if record["unit"] != unit:` binds every canary record. Measured: hard-linking
`curl/gate.json` to `hermes-acp/gate.json` on `evidence-synthetic-pass` leaves the bundle PASSING (rc 0) even though
`curl`'s manifest now declares `"unit": "hermes-acp"` and another namespace. The mechanism the guard reads is therefore
the mechanism of whichever gate file happens to sit in the directory. Checker-completeness, the same class as
VERIFY-E1's F5, and out of this repair's boundary. **Fix:** one condition in `read_gate`. **Red test:** the hardlinked
bundle must exit 1. (A unit DIRECTORY that is a symlink to another unit is caught, but only later, in PHASE 2, by the
canary unit binding: `evidence-invalid: curl canaries.jsonl line 1 names unit 'hermes-acp'`.)

### Item 7 — what the swap lost.

`check_positive_control` (`proofs/S0-05/check_egress.py:217`) IS still red-controlled through committed evidence and the
real CLI: `test_positive_control_is_mandatory` runs its six mutations over `evidence-mechanism-sandbox`, a genuine
`veth-iptables` bundle, so every case must now clear the new PHASE-1 guard before reaching the positive control, and
`tests/test_s0_05_egress.py:243` still pins `positive-control-failed: curl` as the complete first line. Confirmed by
mutation: `M13` (constant inverted to `netns-no-veth`) turns the suite to `65 failed, 39 passed`, those rows included.

**F13 — INFO — one assertion was lost: no test now drives the positive control with REAL collected failing evidence.**
`evidence-bare-unshare` is the only committed bundle whose C0 genuinely failed (`positive-control-failed: curl` under
the pre-repair checker, measured), and PHASE 1 now short-circuits it. What survives is a data assertion on the fixture's
records (`tests/test_s0_05_egress.py:145-146` `c0[0]["rc"] == 7`), not a checker path. Acceptable — the guard SHOULD win by class
— but worth recording that the positive control's only real-evidence exercise is gone.

### Item 8 — mutation table. 13 fresh mutants, none overlapping M1–M5. All compiled and collected (AF-AP-78).

| mutant | compiles | suite | killed-by / verdict |
|---|---|---|---|
| M6 `gates[unit].get("mechanism")` | yes | `104 passed in 6.31s` | **EQUIVALENT** — `proofs/S0-05/check_egress.py:181` `for key in GATE_KEYS:` already raises `gate-manifest-invalid` when the key is absent, so `.get` can never return `None` here |
| M7 guard moved AFTER the gate-state check | yes | `1 failed, 103 passed in 5.79s` | `test_total_isolation_precedes_a_disabled_gate` |
| M8 `MECHANISM = os.environ.get("S0_05_MECHANISM", "veth-iptables")` | yes | `104 passed in 6.26s` | **SURVIVED the suite; CAUGHT by the AP screen** — `scripts/ap_screen.py` prints `AP-1: 1 … :82` (signature at `.claude/hooks/edit-snapshot.py:66`). The shipped file screens clean of AP-1 |
| M9 reason without the unit name | yes | `8 failed, 96 passed in 5.84s` | 4× `test_a_mechanism_mutation_is_rejected_by_class`, `test_bare_unshare_bundle_is_red_as_total_isolation`, `test_every_spec_leg_behaves_exactly_as_declared`, `test_total_isolation_precedes_a_disabled_gate`, `test_the_motivating_instance_is_a_total_isolation_class` |
| M10 `raise SystemExit(1)` in place of `Failure` | yes | `8 failed, 96 passed in 5.89s` | same 8 (exit code stays 1, but no reason line is printed — every first-line assertion fires) |
| M11 guard applied only to `units[0]` | yes | `104 passed in 5.61s` | **SURVIVED** — see F14 |
| M12 `!=` → `not in MECHANISM` (substring) | yes | `2 failed, 102 passed in 5.71s` | `…[empty-mechanism]`, `…[list-mechanism]` |
| M13 `MECHANISM = "netns-no-veth"` | yes | `65 failed, 39 passed in 6.77s` | the whole positive corpus |
| M14 guard nested under the gate-state check | yes | `1 failed, 103 passed in 5.57s` | `test_total_isolation_precedes_a_disabled_gate` |
| M15 `str(...).strip() != MECHANISM` | yes | `1 failed, 103 passed in 6.82s` | `…[trailing-space-mechanism]` |
| M16 `str(...).casefold() != MECHANISM` | yes | `104 passed in 6.96s` | **SURVIVED** — see F15 |
| M17 guard moved to PHASE 2, after the positive control (VERIFY-E1's own suggested placement) | yes | `3 failed, 101 passed in 5.81s` | `test_bare_unshare_bundle_is_red_as_total_isolation`, `test_every_spec_leg_behaves_exactly_as_declared`, `test_total_isolation_precedes_a_disabled_gate` |
| M18 reason suffixed `… is not selective egress` | yes | `8 failed, 96 passed in 7.53s` | same 8 as M9 |

Totals: **13 run · 9 killed · 3 survived · 1 equivalent · 0 invalid.** M17 is the notable positive: the PHASE-1
placement the lane chose over VERIFY-E1's suggested one is locked by the spec leg and the committed fixture together.

**F14 — FOLLOW-UP — M11 survives: no committed test exercises a bad mechanism on a NON-first unit.** The shipped code is
correct (item 6, rows 4-5, measured), but the brief's frozen wording is "for EVERY run unit" and the suite cannot tell
`every` from `units[0]`. **Fix / red test:** on `evidence-synthetic-pass`, flip `hermes-acp`'s mechanism and assert the
first line is `total-isolation: hermes-acp mechanism=netns-no-veth` — one parametrised row, already measured above.

**F15 — FOLLOW-UP — M16 survives: case-sensitivity is unpinned.** The shipped exact-equality check rejects
`"VETH-IPTABLES"` (the coordinator measured it), but no committed row locks that, so a future `casefold()` would pass
the suite. **Fix:** add `("VETH-IPTABLES", "total-isolation: curl mechanism=VETH-IPTABLES")` to
`tests/test_s0_05_egress.py:149-154` (`trailing-space-mechanism`). Defence-in-depth; does not qualify on its own.

### Item 9 — the lane's report. All 7 lint MISSes are convention; no unsupported claim in §OUTCOME or §7.

Reproduced the premise exactly, but only WITH alias maps:

```
$ python3 scripts/report_lint.py tasks/briefs/s0-05-support/E1-R1-report.md \
    --map C=proofs/S0-05/check_egress.py --map T=tests/test_s0_05_egress.py --map S=proofs/S0-05/spec.json \
    --map R=proofs/S0-05/run_canaries.sh --map L=proofs/S0-05/netns_lib.sh
report_lint: 25 refs — OK 18, NEAR 0, MISS 7, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```

Classification of the 7:
* **5 × `report:209`** — all on the report's own LINT-SUMMARY line, whose claim tokens are `report_lint.py`, `NEAR`,
  `MISS`. Each cited range is CORRECT (`T:754-862` → `def _in_ns_listener`, `T:838-852` → `run = subprocess.run(`,
  `T:168-176` → `def test_total_isolation_precedes_a_disabled_gate`, `T:149-165` → the `@pytest.mark.parametrize`
  decorator, `T:795-862` → `@NEEDS_NETNS`). Lint convention, not wrong claims (VERIFY-E1's F21 class).
* **`report:64 T:605-618`** and **`report:198 C:323`** — both are PIN-ERA references, and the report says so in words
  ("the same symbol is at PIN `T:605-618`", "at the PIN the same region starts at C:323"). Verified at `953ccfe`:
  `test_every_spec_leg_behaves_exactly_as_declared` IS at line 605 and `# PHASE 1 — the gate state of EVERY unit` IS at
  line 323. They are right; they are written as bare `alias:NN` instead of `alias@953ccfe:NN`, which is exactly the
  lint's own fix hint.

**Zero wrong claims among the 7.** §OUTCOME's "NOT run here" and §7.1's "Most likely wrong: the root-only live topology
does not reproduce F1 … Sandbox execution is mandatory before acceptance" are both supported and both honest — §7.1 is
the finding this report confirms.

**F16 — INFO — the brief's literal item-9 command lints clean by construction.** `python3 scripts/report_lint.py
tasks/briefs/s0-05-support/E1-R1-report.md` with no `--map` returns `0 refs — OK 0, NEAR 0, MISS 0, UNCHECKABLE 0,
UNRESOLVED 0 (worktree)` — the aliases `C:`/`T:`/`S:` do not resolve. That is the B3 trap the tool's own docstring
warns about. Any future brief quoting a lint bar must name the maps, or the report must cite repo-relative paths (this
report does the latter).

### Item 10 — D4 / the seed's second assertion: one touchpoint, not re-litigated.

The routed topology I built for F1's discriminator is the same shape as VERIFY-E1's D4 "routed variant". It bears on D4
only as evidence that the routed form is cheap to build in this sandbox (one `ip route add`). The owner's pending
decision is untouched here. Also noted: the repair did NOT disturb the seed's declared negative control —
`seeds/seed-stage0-v1.yaml:440` `expected_failure_reason: 'egress-permitted: gate-disabled'` still matches
`proofs/S0-05/spec.json` leg 3, because `evidence-gate-off/curl/gate.json` carries `"mechanism": "veth-iptables"` and so
clears the new PHASE-1 guard (measured: rc 1, first line `egress-permitted: gate-disabled`).

---

## GATES — every count pasted from the run that produced it

```
$ cd /home/user/agent-factory && bash scripts/test_summary.sh tests/test_s0_05_egress.py
104 passed in 5.34s
pytest-exit: 0
pytest-summary: 104 passed in 5.34s

$ cd /home/user/agent-factory && bash scripts/test_summary.sh tests/test_s0_05_egress.py      # determinism, 2nd run
104 passed in 5.47s
pytest-exit: 0
pytest-summary: 104 passed in 5.47s

$ bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py
1 files set=9f0502080347                       # matches the lane report's set id

$ cd /home/user/agent-factory && python3 -m pytest tests/test_s0_05_egress.py -q              # first tree baseline
104 passed in 5.73s      rc=0

$ cd <scratch>/pin && python3 -m pytest tests/test_s0_05_egress.py -q                          # scratch harness sound
104 passed in 6.25s      rc=0

$ cd <scratch>/REDFIRST-953ccfe && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_s0_05_egress.py -q \
    -p no:cacheprovider --basetemp=/tmp/s5/rf -k "motivating or bare_unshare or mechanism_mutation or \
    total_isolation_precedes or spec_leg" --tb=line
8 failed, 96 deselected in 1.76s               # every new/changed test is red-first on the PIN's checker

$ python3 scripts/ap_screen.py proofs/S0-05/check_egress.py
--- AP_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-32: 1   proofs/S0-05/check_egress.py:174
```

Mutation totals: **13 mutants · 9 killed · 3 survived (M8, M11, M16) · 1 equivalent (M6) · 0 invalid.** Hostile-input
totals: **17 `gate.json` shapes + 8 two-unit shapes + 6 unit-set shapes = 31 probes, 0 fail-open** (the one rc-0 row is
the duplicate-key last-wins parse, F10, and the one hardlink row is F12).

## FOLLOW-UPS (non-blocking, for the coordinator to file under D-034)

1. **F2** — the mechanism detector reads link EXISTENCE, not function: a `veth-iptables` label with the link DOWN passes
   the repaired checker (rc 0, measured). Require UP + addressed, or record the route table. Collector seam (issue #13).
2. **F12** — `read_gate` never binds `gate["unit"]` to its directory though `read_records` binds every canary record; a
   hardlinked cross-unit `gate.json` passes.
3. **F14** — add a NON-first-unit mechanism row; M11 (`units[0]` only) survives the whole suite today.
4. **F15** — add a case row (`"VETH-IPTABLES"`); M16 (`casefold()`) survives the whole suite today.
5. **F13** — no test now drives `check_positive_control` with real collected failing evidence; consider keeping one
   `evidence-bare-unshare` path that reaches it (e.g. a copy with the mechanism corrected).
6. **F9** — the refusal reason interpolates an unbounded attacker-chosen value (1 MiB measured).
7. **F16** — brief/checkpoint lint bars must name `--map` aliases, or reports must cite repo-relative paths.

## CENSUS (after the last live run)

```
$ ip netns list
(no output)
$ ip -o link show type veth
(no output)
$ pgrep -af '[l]oopback_standin'
(none)
```

`/etc/netns` is empty — no per-namespace `resolv.conf` residue. Every live run in this lane was censused; all were
clean.

**Shared-tree hygiene.** The tree was clean when I started. It is now dirty with `CLAUDE.md`,
`harness-ports/tests/test_pc_lane_dispatcher.sh`, `scripts/pc_lane.sh` and the `tasks/briefs/pc-t90-support/` set —
a CONCURRENT lane's work, none of it in the S0-05 boundary, none of it touched or staged by me. The only file I wrote
is this report. `git diff --stat 860ab9e -- proofs/S0-05 tests/test_s0_05_egress.py` is still empty. Every mutant,
hostile bundle and scratch edit lived under the session scratchpad; nothing was ever `git stash`/`checkout`/`reset`.
Every live run in this lane was censused; all were clean. All namespaces I created were named
`s0-05-ve1r1-<8 hex>` or created by the suite itself and destroyed by `egress_ns_destroy`. Nothing bound any address
other than `127.0.0.1` inside a namespace and the namespaces' own on-link `/31`s.

## NOT-done (first-class)

* **`scripts/proof-runner run --proof S0-05`** — NOT run: it writes `proofs/S0-05/result.json` into the tree, which is
  read-only for this lane, and the second positive leg defers by design (`proofs/S0-05/evidence` is absent;
  `test_the_committed_spec_positive_leg_defers_here` pins that). F7's runner analysis is read from
  `scripts/proof-runner:178-210` (`negative-control-unmet`), not executed.
* **The wider repo suite** — NOT run: out of this increment's boundary. The gate here is the one file, set id
  `9f0502080347`.
* **The PC venue** — NOT run: this verify is sandbox-only by the brief (the PC lane user cannot create namespaces).
* **VERIFY-E1's F2–F24** — NOT re-examined; they belong to issue #13.
* **The owner's D4 decision** — NOT re-litigated (item 10).
* **F2's fix and F12's fix** — diagnosed and reproduced, NOT implemented (out of boundary; this lane writes only this
  report).

## Report lint

```
$ python3 scripts/report_lint.py --min-refs 15 tasks/briefs/s0-05-support/VERIFY-E1-R1-report.md
report_lint: 41 refs — OK 40, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
```

Round 1 of at most three applied; floor met (40 OK against a bar of 15), MISS 0. The one UNCHECKABLE is a
path:line inside a pasted `ap_screen.py` output block, not a claim of mine.

```text
(end)
```
