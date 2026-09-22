# VERIFY-E1-R1 — the targeted adversarial verify of the S0-05 mechanism guard (E1-R1)

**Role:** `adversarial-verifier` (Opus 5), IN THE SANDBOX as root (netns / iptables / veth available — the
PC lane user cannot create namespaces, so the live test only runs here). Honey `full`: line-bounded findings,
evidence anchors, SOLID/UNSURE on every claim. Your report is DATA for the coordinator's gate; you return a
GATE RECOMMENDATION, never a verdict.

**PIN:** `860ab9e` (the E1-R1 landing on origin). The working tree is origin head `5e5a7f4`; the S0-05
boundary (`proofs/S0-05/**`, `tests/test_s0_05_egress.py`) is BYTE-IDENTICAL between the two (measured:
`git diff --stat 860ab9e 5e5a7f4 -- proofs/S0-05 tests/test_s0_05_egress.py` is empty). Work on the tree
READ-ONLY: every mutant and every hostile bundle lives in a scratch copy under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ve1r1/` (a `git archive 860ab9e`
of the boundary, or `cp -a` of a fixture). The ONLY file you write in the tree is your report.

**Authorization (state of the art, not folklore):** this is defensive work on the owner's own system — the
S0-05 proof's own namespace library builds throwaway network namespaces on loopback; nothing egresses beyond
this container; no owner server exists in the sandbox. The census after every live run:
`ip netns list` and `ip -o link show type veth` must both be empty of anything you created.

## What E1-R1 claims (the repair under test; file:line at the PIN)

VERIFY-E1 F1 (`tasks/briefs/s0-05-support/VERIFY-E1-report.md:338-388`, BLOCKER, SOLID): the collector
records the egress mechanism it observes (`proofs/S0-05/netns_lib.sh:149-154` `egress_ns_mechanism`,
recorded at `proofs/S0-05/run_canaries.sh:114`) but the checker required the key and never asserted its
VALUE, so a totally isolated namespace with a loopback stand-in on the allowed port produced a PASSING
bundle — the AF-AP-1 class minted as S0-05 evidence. The contract: `seeds/seed-stage0-v1.yaml:432-435`
("bare unshare is proven total-block and is NOT acceptable evidence").

The ONE focused repair (D-031, keyed: S0-05 checker · the seed's S0-05 block · `check_egress.py` sha256
prefix `5b766582a9a03f91` at the PIN):

- C `proofs/S0-05/check_egress.py:79-81` — `MECHANISM = "veth-iptables"` (the comment cites the two tokens
  the library emits, `netns_lib.sh:151` / `:153`).
- C `:330-331` — in PHASE 1 of `check()` (`:314`), for EVERY run unit, immediately after `read_gate`
  (`:177`) and BEFORE the gate-state check (`:332-333`) and before any canary is read (PHASE 2, `:336-342`):
  `if gates[unit]["mechanism"] != MECHANISM: raise Failure(f"total-isolation: {unit} mechanism={...}")`.
  An exact-equality allow-list of ONE value; the reason names the value in its plain `str` form, no
  normalisation.
- S `proofs/S0-05/spec.json:39` — the bare-unshare leg's `failure_reason` is now
  `total-isolation: curl mechanism=netns-no-veth` (was the positive control's downstream symptom).
- T `tests/test_s0_05_egress.py` — `test_bare_unshare_bundle_is_red_as_total_isolation` (:138),
  `test_a_mechanism_mutation_is_rejected_by_class[wrong|empty|list|trailing-space]` (:149-165),
  `test_total_isolation_precedes_a_disabled_gate` (:168), and the root-gated
  `test_the_motivating_instance_is_a_total_isolation_class` (:795-853): the verifier's exact topology — an
  isolated namespace, ONE internal veth pair (both ends inside, not the derived name, so the detector still
  reads `netns-no-veth`), a loopback HTTP stand-in on the allowed port INSIDE the namespace
  (`_in_ns_listener`, :754-792) so C0 passes and the old symptom never fires — through the REAL
  `run_canaries.sh` and the REAL checker, asserting the class reason on the FIRST stdout line.

Other digests at the PIN (sha256 prefixes): `spec.json ed6edbd1c408ad83` · `test_s0_05_egress.py
7545714460183c94` · `run_canaries.sh 6f7298077aa39819` · `netns_lib.sh 1b2bd911d54262d3`. Nothing else in
the boundary changed; S0-05 is NOT minted (`proofs/S0-05/result.json` absent — no attested-input
regeneration is in play).

## PREMISE — MEASURED (coordinator, 2026-09-22 08:2x-08:4xZ, sandbox as root)

```
repaired tree, tests/test_s0_05_egress.py: 104 passed in 5.49s
red-first — the new T over a git archive 953ccfe copy of the PIN's checker: 7 failed, 97 deselected in 1.71s
  (the PIN's checker prints PASS rc 0 on the live isolated topology — F1 reproduced live)
M1 guard deleted (py_compile clean), scratch copy: 8 failed, 96 passed in 5.53s
  (the seven + test_every_spec_leg_behaves_exactly_as_declared)
netns/veth census clean after both runs
hostile gate.json values on a copy of evidence-mechanism-sandbox (rc, first line):
  "VETH-IPTABLES"      -> 1  total-isolation: curl mechanism=VETH-IPTABLES
  "veth‐iptables" -> 1  total-isolation: curl mechanism=veth‐iptables
  null                 -> 1  total-isolation: curl mechanism=None
  true                 -> 1  total-isolation: curl mechanism=True
evidence-synthetic-pass (units curl, hermes-acp), one unit flipped to netns-no-veth:
  second unit -> 1  total-isolation: hermes-acp mechanism=netns-no-veth
  first unit  -> 1  total-isolation: curl mechanism=netns-no-veth
flipped mechanism + canaries.jsonl deleted -> 1  total-isolation: curl mechanism=netns-no-veth
flipped mechanism + runtime.json deleted   -> 1  total-isolation: curl mechanism=netns-no-veth
  (PHASE 1 precedes PHASE 2's file checks)
AP screen on C: 3 hits over 2 files (AF-AP-72 x2, AP-32 x1 = the known set); test screen 0; pyflakes 0
GitNexus detect-changes: 3 files, 7 symbols, risk medium (check in two flows)
```

The lane's own gates (PC, the live test venue-skipped): baseline `94 passed, 4 skipped` → `99 passed,
5 skipped` ×2; mutants M1 (guard deleted) · M2 (tuple widened + `not in`) · M3 (guard moved after the
positive control) · M4 (reason renamed `mechanism-invalid`) · M5 (`!=` → `is not`) all killed
(`tasks/briefs/s0-05-support/E1-R1-report.md:112-124`). Report lint at the working tree
`25 refs — OK 18, NEAR 0, MISS 7`.

**Everything above is ALREADY MEASURED. Do not spend your budget re-deriving the builder's cases or the
coordinator's table — your value is the shapes NOBODY has tried.** Re-run a listed measurement only when
one of your findings depends on it.

## ITEMS (discovery exhaustive; disposition disciplined)

Number your findings F1…; for each: evidence level (reproduced / read / inferred), file:line, expected vs
observed, the cheapest red control, and whether the blocking predicate holds (contract-mapped · reproduced
through the real production path · materially effective · a concrete discriminator · in-boundary). A red
test is necessary, never sufficient.

1. **Reachability of the guard from the CLI entry.** Trace `main` (C:354) → `check` (C:314) → the PHASE 1
   loop. Is there ANY path on which a unit's canaries are read before its mechanism is asserted — declared
   `--units` sets, a unit declared `not-run` whose directory is present, an empty run-unit list, a unit
   added by the manifest but absent on disk? Name the path or state SOLID that none exists, with the
   line-bounded evidence.
2. **The producer's detector as a class signal.** `egress_ns_mechanism` (L:149-154) reads ONE fact: whether
   the derived interface name (`egress_ns_if`) exists in the namespace. Question, not an expectation: name
   any topology the detector records as `veth-iptables` while total isolation holds (no route off the
   namespace), or `netns-no-veth` while selective egress holds — and classify each as
   MISTAKE-REACHABLE (a library create path, a partial teardown, a rerun) or ADVERSARY-ONLY (an operator
   builds it by hand). The detector is the COLLECTOR's seam (VERIFY-E1's residue is issue #13); a finding
   here blocks only if a library-reachable path produces the misread. Cite L lines.
3. **Kill-switch on the live test (T:795-853).** Does it prove what it claims?
   (a) Confirm the stand-in really serves INSIDE the namespace (T:774-776 `ip netns exec`): would the test
   still be green with the listener on the HOST loopback? Show by a scratch-copy edit, then restore.
   (b) With the guard deleted (M1, in a scratch copy) read the live test's actual failure text: is it the
   rc-0 PASS the docstring promises (`result.returncode == 1` failing with the PASS line in stdout), or a
   setup error masquerading as a kill?
   (c) Teardown: insert a deliberately failing assertion after the collector run in a scratch copy — is
   the namespace destroyed on the failing path (the `finally` at T:846-853 handles the listener; who
   destroys the namespace?) — census after the run. If a namespace leaks, that is VERIFY-E1 F7's class;
   state whether the new test widened it.
   (d) The C6 target `192.0.2.0:12801` and the internal pair's addresses: does any canary in the live run
   reach OUTSIDE the container (it must not — the census + `ss -tnp` evidence)?
4. **The exact-reason contract.** `test_every_spec_leg_behaves_exactly_as_declared` (T:637) and the spec
   leg (S:39): does the binding hold on the FIRST line by EQUALITY? Attack with scratch mutants: the reason
   printed on the second line after a `NOT run:` line; the reason with a suffix; the reason with the unit
   name dropped. Which tests catch each? (AF-AP-78: every mutant compiles and collects; paste counts.)
5. **Hostile `gate.json` shapes not yet tried.** A `mechanism` value with an embedded newline
   (`"veth-iptables\n"` — the reason then spans two stdout lines; does `splitlines()[0]` still discriminate
   in every consumer, and does the spec-leg binding read it right?), a value carrying NUL, a 1 MiB value
   (is the reason printed unbounded?), a duplicated `mechanism` key in the JSON text (last wins?), a
   `gate.json` that is a JSON list, a unit whose `gate.json` is a symlink to another unit's. Report rc and
   the first line for each; classify any NON-refusal or ambiguous reason.
6. **Two-unit ordering under a broken second unit.** On `evidence-synthetic-pass`: unit `curl` sound, unit
   `hermes-acp`'s `gate.json` unreadable (a FIFO — `test_a_fifo_in_place_of_evidence_is_rejected_without_
   hanging` covers ONE unit; a directory; 0 bytes; a mechanism flip). Which reason wins, and is any of
   `curl`'s canaries read before `hermes-acp`'s gate is asserted (strace or a scratch instrumentation)?
7. **What the swap lost.** The lane REPLACED `test_bare_unshare_bundle_is_red_on_the_positive_control`
   (asserting `positive-control-failed: curl`) with the class-reason test. Is `check_positive_control`
   (C:217) still red-controlled through a committed bundle and the real CLI (`test_positive_control_is_
   mandatory`, T:236, is parametrised over mutations — confirm it runs on a `veth-iptables` bundle and
   still discriminates)? Name any assertion the proof lost.
8. **New mutants (never M1-M5).** At least: M6 `gates[unit].get("mechanism")` (equivalent? — say so with
   the reason); M7 the guard moved AFTER the gate-state check (the order control must catch it — paste);
   M8 `MECHANISM` read from `os.environ` with the same default (AP-1 — which test or screen catches it?);
   M9 the reason without the unit name; M10 `raise SystemExit(1)` in place of `Failure` (exit code and
   first-line semantics); M11 the guard applied only to `units[0]`. One row each: mutant · compiles ·
   counts · killed-by / SURVIVED / EQUIVALENT.
9. **The lane's report (`E1-R1-report.md`).** Classify the 7 lint MISSes (moved ranges vs wrong claims):
   `python3 scripts/report_lint.py tasks/briefs/s0-05-support/E1-R1-report.md`. Any claim in §OUTCOME or
   §7 SELF-ATTACK that the tree at the PIN does not support is a finding.
10. **Out of scope, do not re-litigate:** the seed's second assertion / the D4 routed-variant question is
    the OWNER's pending decision (VERIFY-E1 §D4, item 14); F2-F24 of VERIFY-E1 are issue #13's. Note a
    touchpoint in one line if your findings bear on them.

## Deliverable

`tasks/briefs/s0-05-support/VERIFY-E1-R1-report.md` — sections: OUTCOME (one paragraph, the GATE
RECOMMENDATION first: `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) ·
IDENTITY (the digests you measured vs the table above) · ITEMS 1-10 with findings F1… · MUTATION TABLE ·
GATES (every count PASTED from the run, with the exact pytest invocation; never typed) · FOLLOW-UPS
(non-blocking findings, one line each, for the coordinator to file under D-034) · CENSUS (the two
commands' output after your last live run) · NOT-done (first-class). Lint floor:
`python3 scripts/report_lint.py --min-refs 15 tasks/briefs/s0-05-support/VERIFY-E1-R1-report.md`; apply
its `fix:` hints for at most three rounds, then paste and finish. Every count in prose is pasted from the
run that produced it. Run long gates in ONE foreground call (a backgrounded run that you stop waiting for
is lost). Never edit the tree except the report; never `git stash`/`git checkout` anything; never touch
`proofs/S0-05/fixtures/**` in place. Do not commit, push, post, or open issues — the coordinator does.
