# N5n — S0-01 probe round 17: broaden the close-fds AST walker (VERIFY-N5m F1)

**Authorization.** Defensive work on the owner's own S0-01 ACP-conformance probe. The close_fds
boundary is a security property of the owner's system: an agent child must not inherit non-stdio
fds. This round HARDENS the test that guards it. No live model, relay, or capture.

**Ground (LANDED at the PIN).** N5m (probe round 16) landed as 60615c9; VERIFY-N5m
(`tasks/briefs/s0-01-n5l-support/VERIFY-N5m-report.md`) returned ONE blocker with V1-V5 controls
SOLID. The production probe `proofs/S0-01/tools/acp_probe.py` (P) is UNCHANGED and stays unchanged
this round unless you find a real second launch in it (see item 2). PIN: `c728be5`.

**The finding (VERIFY-N5m F1, BLOCKING).** `_agent_popen_close_fds_value` in
`tests/test_s0_01_acp_probe.py` (T, ~3591-3630) recognizes ONLY an `ast.Assign` whose target is
exactly the Name `proc` and whose call is `subprocess.Popen`, then asserts exactly one such node.
Two bypasses were reproduced against a scratch production copy:
- **Alternate target.** `sidecar = subprocess.Popen([agent], close_fds=False)` inserted before the
  guarded `proc = ...` launch is NOT collected (target id != "proc"), so the gate stays green
  (`1 passed, 125 deselected`) while a real second child launches without close_fds.
- **Loop.** A `for`/`while` wrapping the guarded `proc = subprocess.Popen(..., close_fds=True)`
  launch is ONE AST node, so `len(calls) == 1` holds and the gate passes, but the agent launches
  more than once at runtime.

A called helper carrying an unguarded `subprocess.Popen` is likewise invisible (the walker prunes
nested defs).

## Items (in order; each a code change + a deterministic LLM-free test + its negative control)

1. **Broaden the walker to every `subprocess.Popen` in `main`, any target, and reject loops and
   extras.** Rewrite `_agent_popen_close_fds_value` (or add a companion) so it:
   - collects EVERY `ast.Call` to `subprocess.Popen` reachable in `main`'s body regardless of
     assignment target (assigned to any name, a tuple target, or an unassigned expression), still
     pruning nested `FunctionDef`/`AsyncFunctionDef`/`Lambda` bodies;
   - REJECTS any collected Popen whose ancestor chain within `main` includes a `For`, `AsyncFor`,
     `While`, or a comprehension (`ListComp`/`SetComp`/`DictComp`/`GeneratorExp`) — a launch that
     can run more than once;
   - requires EXACTLY ONE agent Popen and that its `close_fds` is the literal `True` (keep the
     `**kwargs` ban and the comment-only-mutant defence from round 16).
   TEST: a scratch production copy with a second `sidecar = subprocess.Popen(..., close_fds=False)`
   before the guarded launch is REJECTED (reproduce the V-N5m bypass going RED); a scratch copy
   that wraps the guarded launch in a `for _ in range(2):` is REJECTED with a loop-specific message;
   the unmodified production source is ACCEPTED (returns True). Negative controls: remove the
   any-target broadening → the `sidecar` copy is accepted (red); remove the loop rejection → the
   looped copy is accepted (red).

2. **A module-wide Popen count closes the moved-to-helper bypass.** Assert the WHOLE production
   module contains exactly one `subprocess.Popen` call (module-wide `ast` walk), so a launch moved
   into a helper `main` calls is caught. TEST: a scratch copy that adds an unguarded
   `subprocess.Popen` inside a module-level helper is REJECTED by the count; production passes
   (count == 1). Negative control: drop the count assertion → the helper copy passes (red). If the
   REAL production probe already holds more than one `subprocess.Popen`, STOP — that is a production
   finding: surface it, do not edit P to hide it.

3. **Keep V1-V5 intact.** Re-run the general fd census, the two-main-launch rejection, the literal
   `EXPECTED` denominator + `--self-test`, and the socket-fixture cleanup — none regresses. Add the
   two new mutant rows (alternate-target, loop) to the driver
   `tasks/briefs/s0-01-n5l-support/mutants.sh` (D), each compiling and collecting before its test
   runs (AF-AP-78), each killed by the matching negative control; bump the literal `EXPECTED`
   accordingly and update the `--self-test` deleted-row expectation.

## Gates (paste every line verbatim)

- `python3 -m py_compile` the test; `pyflakes` it; `git diff --check` → rc 0 each.
- `git diff --quiet c728be5 -- proofs/S0-01/tools/acp_probe.py; echo rc=$?` → **rc 0** (P unchanged),
  unless item 2 surfaced a real production finding (then say so, still do not edit P).
- `scripts/lane_gate.sh -r c728be5 -f "tests/test_s0_01_acp_probe.py tasks/briefs/s0-01-n5l-support/mutants.sh" -t "tests/test_s0_01_acp_probe.py" -n 2` — paste the RESULT line (the probe file alone; under the 420 s terminal cap it runs serial in ~1 min).
- The driver + its `--self-test`: paste `EXPECTED=N KILLED=N SURVIVED=0 INVALID=0 CONTROL=1` and the self-test wrapper rc.
- `python3 scripts/ap_screen.py --s0-01 tests/test_s0_01_acp_probe.py` — classify every hit; any NEW class is a finding.
- FILE IDENTITY: sha256 + line count of P (unchanged), T, D before → after.
- `scripts/report_lint.py` with the P=/T=/D= maps.

**Boundary.** `tests/test_s0_01_acp_probe.py` (T), `tasks/briefs/s0-01-n5l-support/mutants.sh` (D),
your report `tasks/briefs/s0-01-n5l-support/N5n-report.md`. `proofs/S0-01/tools/acp_probe.py` (P)
is READ-ONLY — touch it only to build a hostile SCRATCH copy, never the tracked file. The S0-01
sweep class list AF-AP-78/80/81/82/84/85/87 is your preflight. CODE INTEL FIRST: `graft ask` /
`ripwire` before grep. Retro: name any new class for the coordinator; bake nothing yourself.
