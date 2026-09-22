# VERIFY-E1 — adversarial grade of lane E1 (S0-05 no-direct-egress: canaries C0-C6, the selective-netns library, the collector, the checker, three real namespace bundles, the PC unit runner)

You are an adversarial-verifier (Opus 5 in the sandbox — this round needs ROOT for the namespace work, which the sandbox has and the
PC's lane user does not). Repo /home/user/agent-factory, branch claude/soundbox-kit-migration-iz1jwf. **PIN: `24e80e6`** (the
commit carrying the lane's 34 files + its report). Grade the bytes of `git archive <PIN>` from a copy under the session scratchpad
(`ve1/`; delete it when done). Read-only git on the shared tree; every mutant on scratch copies; explicit `--basetemp`; kill only what
you start, PID-targeted; every namespace you create named `s0-05-ve1-<nonce>` and destroyed BY NAME in a trap (never by pattern);
never background a run and stop; no outward actions; the network namespaces you create must never get a default route to the world
(the sandbox's egress is the owner's proxy). **The ONE bridge action:** the pytest-only PC gate `scripts/pc_suite.sh launch -n 8 --
tests/test_s0_05_egress.py` from a clean detached worktree of the PIN, then `wait <RUN_ID>` (expect the 4 declared root-only skips).

**Inputs (read in this order):** the lane brief `tasks/briefs/s0-05-e1-egress-canary-suite-netns-runner-checker.md` · the report
`tasks/briefs/s0-05-support/E1-report.md` (§3 the assertion table, §4 the 20 mutants incl. the declared equivalent, §6 the 18-class
table with seven fixed defects, §7 D1-D10 — D4 is the round's centre) · the material pack `tasks/briefs/stage0-parallel-support/material-S0-05.md`
(the seed block :423-441, the council's "mechanism proven, containment unproven", the spike `spikes/selective-egress/`) ·
`spikes/selective-egress/probe.sh` + `result.json` (what the library lifts) · `docs/05_SECURITY.md:74-` (§6 network segmentation) ·
`docs/research/FINDINGS-STAGE0-v1.md:98` (the Chairman's "bare netns is TOTAL isolation") · `docs/INCIDENT-LOG.md` (AF-AP-1, AF-AP-22,
AF-AP-47, AF-AP-59).

## Item 0 — the mechanical gates, pasted
`report_lint.py … --rev <PIN> --map C=proofs/S0-05/check_egress.py --map L=proofs/S0-05/netns_lib.sh --map R=proofs/S0-05/run_canaries.sh
--map T=tests/test_s0_05_egress.py --map PC=proofs/S0-05/tools/pc/run_s0_05_units.sh` — MISS 0 or a finding; `ap_screen.py proofs/S0-05
proofs/S0-05/canaries` (one AP-32 hit) and `--tests` (0) — classified by running.

## Items
1. **D4 — what the gate decides vs what routing decides.** Reproduce the three bundles' shape on a fresh namespace: gate on / gate
   off / isolated; confirm C1-C4 fail with `Network is unreachable` in BOTH gate states and only C5/C6 flip. Then build the ROUTED
   variant the lane did not (a default route through the veth host end + NAT — in the sandbox this must NOT reach the world: point
   the "internet" at a second local listener on the host end and use a fake /etc/hosts) and show what the gate blocks when routing
   does not: which of C1-C4 then become firewall-decided? This is the measurement that tells the coordinator whether the PC legs
   need the routed variant before S0-05 can claim anything about model endpoints.
2. **The gate-fired proof** (the OUTPUT DROP counter `0 -> 10`; `gate-inert` otherwise): attack — a bundle whose counter advanced for
   an unrelated reason (a stray packet from the namespace's own resolver); a counter that wrapped; both policies read (mutant
   COUNTER-READS-DROP-ONLY re-run).
3. **The rules digest + the declared allow-list** (A10): the digest computed inside the namespace vs recomputed by the checker
   (cross-language hash of the rule text — reproduce); a widened rule set with a matching digest (mutant re-run); a rule REORDERED
   (same set, different order — the digest changes: is that a false red? should the comparison be order-insensitive, and if so does
   that open a hole?).
4. **The denial vocabulary + the own-target rule** (`_foreign_endpoint_in_detail`, the proxy-shaped denial): the sandbox's HTTPS_PROXY
   case (D6a) reproduced; a denial whose detail names the target AND a proxy; an `/etc/hosts` short-circuit (D6b); a canary whose
   `resolved` field is forged; the forged-loopback mutant re-run.
5. **The positive control** (C0 → the allowed target, 2xx): the isolated bundle red on it (AF-AP-1); a positive control that hits a
   DIFFERENT listener than the allow-list names (the allow entry `ip:port` vs the C0 URL — bound?).
6. **The units manifest**: a `not-run` unit without a reason rejected; a unit both present and declared absent rejected; the PASS
   line's numerator/denominator (mutant PASS-RATIO-COUNTS-RECORDS); the declared-equivalent survivor — agree it is equivalent, or
   write the killer.
7. **The library** (`netns_lib.sh`): the trap destroys by NAME (never `ip netns list | grep`); `egress_ns_destroy` on a namespace
   with a live process inside; the blackhole resolver address never colliding with the allowed target; the isolated control has no
   veth (D7); a second concurrent namespace (two nonces) does not share state; the veth names' uniqueness (`eh/en<8hex>`).
8. **The collector** (`run_canaries.sh`): the proxy scrub covers `NO_PROXY`/`no_proxy` and `ALL_PROXY`; the model hosts resolved
   OUTSIDE the namespace (a host that does not resolve → `not-run` → DEFER, never a fake denial); the DROP_BEFORE unreadable → exit 3
   (class 6 fix) re-run; the census `pgrep`-free.
9. **The PC runner — READ, never run** (`run_s0_05_units.sh`): the routed variant NOT BUILT stated at `PC:20`; the S0-01 launch inside
   a namespace `NOT VERIFIED` at `PC:99`; every external call; the failure-aware bounded poll (class 9 fix); never kills by name; the
   units it declares vs the units that exist on the PC (hermes-acp, buzz-acp, the scripted backend — where do they run today?).
10. **The 18-class table** — re-scan the 34 files; the seven fixed defects each have a red test (run them); a class missed = a finding.
11. **The PC gate (the carve-out)**; paste beside the checkpoint's lines (94 + 4 skipped: name the four and confirm each is the
    declared `NEEDS_NETNS`); agree.
12. **Mutants ≥ 30** (the lane's 20 + yours: the stray-counter, the reordered rules, the target-and-proxy detail, the forged resolved
    field, a C0 to a non-allowed listener, a namespace name collision, the routed-variant sanity).
13. **Discipline + census** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; `ip netns list` empty of your
    names, no veth leftovers, no `/etc/netns` leftovers, no listener of yours alive.
14. **The design.** Is the seed's "canaries FAIL from every non-OmniRoute unit" provable with THIS mechanism at all (a namespace whose
    only reachable destination is the allow-list) — or does the seed need the routed variant to mean anything about model
    endpoints? Say which, from the D4 measurement.

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-E1.md` — draft after EACH item — then return it whole. Findings: ALL, no severity
filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact red test, SOLID/UNSURE;
reproduced vs reviewed vs skipped; shared-tree hygiene + the namespace census; verdict MERGE-READY or NOT-READY with the blocking set,
the cheapest path, and the exact PC steps for the live-unit legs.

---

## AMENDMENT 1 (2026-09-22 06:1xZ, coordinator) — re-pin, measured premises, the disposition rules, the report path

**PIN → `5c2392e`** (the origin head at authoring; the original PIN 24e80e6 is 14 days behind it). The S0-05 boundary is byte-identical
to the original PIN — measured, not assumed:
`$ git diff --stat 24e80e6 5c2392e -- proofs/S0-05 tests/test_s0_05_egress.py spikes/selective-egress` → (empty).
Every `file:line` in the original items and in the E1 report still resolves at 5c2392e:
`$ python3 scripts/report_lint.py tasks/briefs/s0-05-support/E1-report.md --rev HEAD --map C=proofs/S0-05/check_egress.py --map L=proofs/S0-05/netns_lib.sh --map R=proofs/S0-05/run_canaries.sh --map T=tests/test_s0_05_egress.py --map PC=proofs/S0-05/tools/pc/run_s0_05_units.sh`
→ `report_lint: 112 refs — OK 107, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 5 (at HEAD)`; the five UNRESOLVED are unmapped aliases,
not misses: `probe.sh:50-58` (report:100), `probe.sh:113-116` (report:102), `probe.sh:26-32` (report:103) = `spikes/selective-egress/probe.sh`,
and `example.com:443` (report:131, report:288) = a host, not a file. Reproduce the line; add `--map probe.sh=spikes/selective-egress/probe.sh`
and confirm the three spike refs resolve (a moved line there is a NEAR, not a finding about S0-05).

**Item 0 re-measured at 5c2392e** (paste your own run beside these; the registry grew since the brief was written):
`$ python3 scripts/ap_screen.py proofs/S0-05 proofs/S0-05/canaries` →
`--- AP_SCREEN over 2 path(s): 3 hits over 2 files --- AF-AP-72: 2 — proofs/S0-05/canaries/connect_probe.py:48 (×2, one line) · AP-32: 1 — proofs/S0-05/check_egress.py:171`.
The brief's "one AP-32 hit" predates the AF-AP-72 row (a bare `int()`/`float()` parse of argv with no guard): classify it by RUNNING —
a non-numeric port or timeout argv to `connect_probe.py`: what does the canary emit, and does the collector read that as a denial?
`$ python3 scripts/ap_screen.py --tests tests/test_s0_05_egress.py` → `--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---`.

**Venue probe (THIS sandbox, 2026-09-22T06:07:38Z):** `uid=0`, kernel `6.18.44-fc-v37` (the E1 report ran on `fc-v24` — a different
image build: re-run the three bundle shapes on this kernel, never reuse the committed fixtures as "the venue"), `iptables v1.8.10 (nf_tables)`,
`iproute2-6.1.0`, `unshare from util-linux 2.39.3`; `ip netns add`/`del` OK, `unshare -n` OK, veth pair add OK, `nat POSTROUTING` policy
ACCEPT with no rules. The sandbox's only egress is the owner's proxy (`HTTPS_PROXY`); a namespace of yours never gets a default route
to it — the routed variant's "internet" is a second local listener on the veth host end.

**Why this lane runs in the sandbox (state it in the report's header):** `proofs/S0-05/netns_lib.sh:57` requires uid 0; the PC bridge
user is uid 1000 and `sudo` needs the owner's password — the PC local-Qwen verify route cannot host this brief. The live-unit legs on the
PC (`run_s0_05_units.sh`) are therefore an OWNER-run step; item 9 and item 14 produce the exact steps and the design answer for it.

**Dispositions (D-031 / D-034, adopted after this brief was written; skill `contract-gate`):** discovery stays exhaustive — every
observation reported, no severity filter. A finding BLOCKS only if it meets the whole predicate: contract-mapped (the seed block
`seeds/seed-stage0-v1.yaml` S0-05 / the E1 report's own claims) · canonically reproduced through the real path (the real scripts on a
real namespace, not a re-implementation) · materially effective · a concrete discriminator (a red test or a failing input, pasted) ·
in-boundary. Close with ONE line `GATE RECOMMENDATION: MERGE-READY | MERGE-READY-WITH-FOLLOWUPS | NOT-READY | CONTRACT-INVALID` and the
blocking set. Non-blocking residue = a numbered list with file:line + the minimal fix; the coordinator files it as `verify-followup`
issues — you file nothing, comment nowhere, commit nothing, push nothing. Item 1's D4 measurement and item 14's design answer are
ANSWERS for the coordinator; they are never blockers by themselves (a mechanism that cannot prove the seed's claim is a CONTRACT
finding, said plainly, not a NOT-READY on the lane).

**Report path:** draft after EACH item to `<the session scratchpad>/ve1/VERIFY-E1-draft.md` (a dead agent's draft is harvested from
there); the final report to `tasks/briefs/s0-05-support/VERIFY-E1-report.md` in the shared tree (a NEW file; never `git add`, never
commit). Header: PIN, venue line (uid/kernel/iptables), the sandbox-routing reason above, the item-0 pastes. Run `report_lint.py` on
your own report with the five maps + the probe.sh map at `--rev 5c2392e` and paste its summary line; MISS 0 or each MISS explained.

**Harness rules that bite here:** a foreground `sleep` is refused — wait on a process with `timeout N tail --pid=<pid> -f /dev/null`
or poll a file in a bounded loop without sleep; never `pkill -f` / `pkill -x` by NAME — kill by pid read from `pgrep -f '[p]attern'`
in its OWN call (two self-kills this month, rc 144); one long run in ONE foreground call (a run you background and stop on is never
rewoken); pytest with a SHORT `--basetemp` (`mkdir -p /tmp/ve1 && --basetemp /tmp/ve1/bt`); every mutant on a scratch copy under
`<scratchpad>/ve1/` (never edit, `git stash` or `git checkout --` the shared tree); read-only git on the shared tree. The ONE bridge
action (item 11) exactly as the original brief states, after `set -a; . ./.pc-bridge.env; set +a` in the same shell: `scripts/pc_suite.sh
launch -n 8 -- tests/test_s0_05_egress.py` from a clean detached worktree of the PIN, then `wait <RUN_ID>`; if the bridge answers anything
but a launch, write `NOT run here: <the exact error>` and continue — never retry into a server, never touch anything else on the PC.
Paste `date -u` beside every count. On exit paste the census: `ip netns list`, `ip link show type veth`, `ls /etc/netns`, your listeners.

**Authorization:** defensive testing of the owner's own system on the owner's own sandbox: the egress canaries prove containment of a
namespace the owner's design specifies (`docs/05_SECURITY.md` §6); every listener is loopback or veth-local; nothing reaches the world.
