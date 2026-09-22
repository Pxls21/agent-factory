# PC lane — E1-R1 (the ONE focused repair of VERIFY-E1 F1: the S0-05 checker asserts the mechanism; a totally isolated namespace can never pass)

PIN: 953ccfe

Role: code-implementer. Route: the LOCAL build route (`agentfactory-build-local`, the vLLM server default effort). Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first. Honey mode: ultra Lever-2 (the report is DATA: files:lines, verbatim counts, NOT-done).

## THE FINDING YOU CLOSE (D-031: one focused repair, keyed by proof S0-05 + seed:434-435 + C's digest below)
VERIFY-E1 (`tasks/briefs/s0-05-support/VERIFY-E1-report.md`, §F1 — read it whole first) reproduced, through the REAL collector and the
REAL checker, that `proofs/S0-05/check_egress.py` REQUIRES `gate["mechanism"]` (`C:78` GATE_KEYS) and never asserts its VALUE: a
namespace with no path off itself (`mechanism=netns-no-veth`, the AF-AP-1 class the seed declares inadmissible at
`seeds/seed-stage0-v1.yaml:434-435` and the checker's own docstring rejects at `C:21`) plus one internal veth pair produced
`PASS: S0-05 no-direct-egress - 1 units, 11 canaries failed as required, positive controls 1/1`, rc 0. The guard is EMITTED by the
library (`L:149-153`: `veth-iptables` | `netns-no-veth`, observed not claimed) and RECORDED by the collector (`R:114`), and never fires
— an emitted-but-unreachable check, the silent hollow green of build-loop rule 1. The committed `evidence-bare-unshare` fixture is
refused today only by a downstream symptom (`positive-control-failed: curl`), never by its class.

## PREMISE — MEASURED at authoring (2026-09-22 06:5xZ, the sandbox clone at 953ccfe); re-measure as item 1
```
sha256 (first 16) at 953ccfe: C proofs/S0-05/check_egress.py 59b884c6e60fa784 (370 lines) · T tests/test_s0_05_egress.py 6c96693ad4063c35 (730 lines)
                               S proofs/S0-05/spec.json 0751bf678f50349e · L proofs/S0-05/netns_lib.sh · R proofs/S0-05/run_canaries.sh
git log --oneline 24e80e6..953ccfe -- proofs/S0-05 tests/test_s0_05_egress.py   → (empty: the boundary is E1's landing, untouched since)
C seams: GATE_KEYS C:78 · read_gate C:174-186 (presence of the six keys, allowed non-empty list, gate in {enabled,disabled}) ·
  check() C:311 · PHASE 1 (gates read for every unit, `egress-permitted: gate-disabled`) C:321-326 · PHASE 2 C:329-334
  (records, positives += check_positive_control C:334, denials, recorded, runtime+rules) · the PASS line C:342-343
L: egress_ns_mechanism() L:149 prints `veth-iptables` (L:151) or `netns-no-veth` (L:153) · egress_ns_create_isolated L:124 · egress_ns_create L:66
R: usage R:5 `run_canaries.sh <unit> <ns> <allowed ip:port> [evidence-root] [blocked ip:port] [venue]` · MECHANISM recorded R:114
S: legs S (4): positive fixtures/evidence-mechanism-sandbox → rc 0 · positive proofs/S0-05/evidence → rc 0 (absent today: deferred) ·
  negative fixtures/evidence-gate-off → rc 1 `egress-permitted: gate-disabled` · negative fixtures/evidence-bare-unshare → rc 1
  `positive-control-failed: curl` (S:39)
T pins of that reason: T:7 (docstring), T:142 (test_bare_unshare_bundle_is_red_on_the_positive_control, T:137-145),
  T:211 (test_positive_control_is_mandatory — C0 mutations of the veth-iptables bundle: UNAFFECTED by this repair)
T helpers: run_checker T:59 · copy_bundle(tmp_path, source=MECHANISM) T:64 · records T:70 · write_records T:75 · patch_json(path, **fields) T:80 ·
  netns_capable T:87 · NEEDS_NETNS T:93-97 · the live isolated-control test T:703-720 (egress_ns_create_isolated, mechanism netns-no-veth,
  c0-rc=7, destroy in finally) · root-gated tests: T:653, T:680, T:703, T:723 (the PC's 4 skips)
fixture mechanism values: evidence-bare-unshare netns-no-veth/enabled · evidence-gate-off veth-iptables/disabled ·
  evidence-mechanism-sandbox veth-iptables/enabled · evidence-synthetic-pass veth-iptables/enabled (both units)
2026-09-22T06:53:38Z coordinator reproduction at 953ccfe: copy of evidence-mechanism-sandbox → rc 0 PASS; the same copy with gate.json
  mechanism=netns-no-veth → rc 0 PASS (THE HOLLOW GREEN); fixtures/evidence-bare-unshare → rc 1 (`exit 1 per contract`)
2026-09-22T06:54:27Z sandbox: python3 -m pytest -q tests/test_s0_05_egress.py → 98 passed in 4.22s (root: the 4 netns tests RUN here)
```

## THE CONTRACT (exactly this; nothing else changes)
1. **C — the guard, in PHASE 1, mechanism BEFORE gate state:** a module constant `MECHANISM = "veth-iptables"` (comment: the one
   mechanism this proof accepts — `L:151`; `netns-no-veth` is the AF-AP-1 total-isolation class, `L:153`). In the PHASE 1 loop
   (C:322-326), right after `gates[unit] = read_gate(...)` and BEFORE the `gate-disabled` check:
   `if gates[unit]["mechanism"] != MECHANISM: raise Failure(f"total-isolation: {unit} mechanism={gates[unit]['mechanism']}")`.
   An exact-equality allow-list of ONE value (AF-AP-47: never a blacklist of known-bad strings); a non-string value prints its str form.
   Nothing moves into PHASE 2; `check_positive_control` and everything after C:329 are untouched.
2. **S — the bare-unshare leg re-pinned to the class-naming reason:** `S:39` becomes
   `"failure_reason": "total-isolation: curl mechanism=netns-no-veth"` (the gate-off leg keeps `egress-permitted: gate-disabled`;
   the two positive legs unchanged). The schema `proofs/schemas/spec.schema.json` is not touched (S0-05 is not minted — no attested
   regeneration; do NOT run `scripts/proof-runner` on S0-05).
3. **T — three red controls, written red-first on the PIN's checker (paste the red run), green after:**
   (a) `test_bare_unshare_bundle_is_red_on_the_positive_control` (T:137-145) renamed `…_is_red_as_total_isolation`: rc 1 and line 0
   == `total-isolation: curl mechanism=netns-no-veth`; keep the c0 rc-7 assertion (the fixture's shape is unchanged); update the T:7 docstring.
   (b) NEW fixture-mutation controls on `copy_bundle` of the veth-iptables bundle: `patch_json(bundle/"curl"/"gate.json",
   mechanism="netns-no-veth")` → rc 1, line 0 the exact reason; `mechanism=""` and `mechanism=["veth-iptables"]` → rc 1 with the
   reason's `mechanism=` tail printing the value's str form; `mechanism="veth-iptables "` (a trailing space) → rc 1 (exact equality,
   no normalisation). And the ORDER control: a bundle with mechanism=netns-no-veth AND gate=disabled → `total-isolation` first.
   (c) NEW `@NEEDS_NETNS` live test beside T:703: the verifier's topology — `egress_ns_create_isolated <ns> "127.0.0.1:<port>"` with a
   loopback stand-in listener INSIDE the namespace on that port and ONE internal veth pair (both ends inside; the report §F1 has the
   exact `ip -n <ns> link add …` recipe and the C0 shape), then the REAL collector `R` (`run_canaries.sh curl <ns> 127.0.0.1:<port>
   <tmp-root> "" sandbox`) and the REAL checker on `<tmp-root>` → rc 1, line 0 `total-isolation: curl mechanism=netns-no-veth`;
   destroy the namespace by NAME in `finally` (T:718-720's shape); assert `ip netns list` no longer carries it. This is the motivating
   instance (anti-hollow-green tactic 11) and MUST be red on the PIN's checker (it passed there — paste that run from the sandbox
   section of your report as "NOT run here" if you are on the PC: the test is NEEDS_NETNS-skipped on this host; the coordinator runs it
   in the sandbox at harvest — write it so it runs there).
4. **Mutants (≥ 4, each compile-checked, on a scratch copy; the named test that goes red pasted):** M1 the guard deleted → (a),
   (b), (c); M2 `MECHANISM` widened to a tuple containing `netns-no-veth` with `not in` → (a), (b); M3 the guard moved AFTER
   `check_positive_control` (C:334) → (a) regresses to `positive-control-failed: curl` and the ORDER control; M4 the reason string
   changed to `mechanism-invalid: …` → (a)/(b)/S-leg test; M5 `!=` → `is not` (same value, different object — may survive: declare).
5. **Nothing else:** not `L`, not `R`, not `PC`, not the fixtures' bytes, not `proofs/S0-05/fixtures/PROVENANCE.md`, not CLAUDE.md,
   not the F2-F24 residue (issue #13 — out of this repair by D-031).

## ITEMS
1. PREMISE (first; stop on failure): re-run the identity/grep/test lines above on your worktree, paste; reproduce the hollow green
   yourself (the mechanism=netns-no-veth copy → rc 0 PASS on the PIN's checker) and paste it; a mismatch → CONTRACT-INVALID, stop.
2. Red-first: write (a)/(b) and run them on the PIN's checker → red (paste); implement item 1 of the contract; (a)/(b) green (paste).
3. S:39 + the spec-leg test(s) that read S (grep T for `failure_reason` / `SPEC`): the leg table's new reason; green (paste).
4. (c) written per the contract; on this host it SKIPS (NEEDS_NETNS) — paste the skip line; do not try to become root.
5. Mutants per item 4; restore byte-identical (paste the sha).
6. Gates on this host: `python -m pytest -q tests/test_s0_05_egress.py` ×2 (expect the 4 existing + 1 new NEEDS_NETNS skips; paste both
   summary lines with `date -u`; set id `scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py` if the script runs locally, else the
   file name beside the count); `python3 -m py_compile proofs/S0-05/check_egress.py`; `python3 scripts/ap_screen.py proofs/S0-05`
   (expect the 3 known hits, 0 new); pyflakes on C and T (0 new).
7. Report `tasks/briefs/s0-05-support/E1-R1-report.md`: the identity table before/after, the guard's file:line span, the red-first
   pastes, the mutant lines, the gate lines, NOT-done (the live (c) run, the F2-F24 residue), `report_lint.py` summary with
   `--map C=proofs/S0-05/check_egress.py --map T=tests/test_s0_05_egress.py --map S=proofs/S0-05/spec.json --map L=proofs/S0-05/netns_lib.sh
   --map R=proofs/S0-05/run_canaries.sh --rev 953ccfe` — at most three fix rounds (AF-AP-76).

## VENUE NOTES (this host)
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; pytest directly with a SHORT absolute `--basetemp` (`mkdir -p /tmp/e1r1 &&
  --basetemp /tmp/e1r1/bt`); Hermes's `terminal` tool caps ONE call at 420 s — the suite runs in ~5 s.
- You are uid 1000: no `ip netns`, no `sudo`, no `iptables` — the netns tests skip by design here; never work around it.
- Other lanes (VERIFY-S4H, K1-d, VERIFY-B67, VERIFY-GOV2c) and the vLLM `qwen` container share this host: never touch their trees, the
  container, OmniRoute or any server; never `pkill`/`killall` by name; every count PASTED beside `date -u`, every file:line by `sed -n` on the PIN.

**Authorization:** defensive testing of the owner's own egress proof on the owner's own host; no namespace is created on this host by this lane.
