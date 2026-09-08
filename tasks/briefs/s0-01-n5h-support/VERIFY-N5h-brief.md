# VERIFY-N5h — adversarial grade of lane N5h (S0-01 ACP probe, round 11: the sweep's six production rows + the ordinal gate, closed as classes)

You are an Opus-5 `adversarial-verifier`. Repo /home/user/agent-factory, branch claude/soundbox-kit-migration-iz1jwf.
**PIN: `9aaefd0ab4804d74f01c1eb43f3ae80ae700d548`** (the checkpoint carrying the lane's two files + its report; parent for the scope files = the
MERGE-READY probe of VERIFY-N5g-b, blob `b9eb56dd…`, at `2823f05`). Grade the bytes of `git archive <PIN>` from a copy under the
session scratchpad /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ (`vn11/`). Read-only git on the shared
tree; every mutant on scratch copies; every pytest run with an explicit `--basetemp` under your scratch dir; kill only what you
start, PID-targeted; never background a run and stop; no outward actions.

**The ONE bridge action you MAY take (owner ruling 2026-09-07):** a pytest-only PC gate through `scripts/pc_suite.sh launch -n 8 --
tests/test_s0_01_acp_probe.py tests/test_s0_01_negative_contract.py` then `wait <RUN_ID>`, from a CLEAN detached worktree of the PIN.
Nothing else on the bridge.

**Inputs (read in this order):** the brief `tasks/briefs/s0-01-n5h-probe-the-sweep-rows-closed-as-classes.md` (the contract: 9 items) ·
the lane's report `tasks/briefs/s0-01-n5h-support/N5h-report.md` (DONE 1-9, the class-closure tables, 13 mutants, DEVIATION 1-2,
D1-D5, the self-attack) · the MERGE-READY verdict it builds on `tasks/briefs/s0-01-n5g-support/verify-N5g-b.md` (or the nearest
`verify-N5g*.md` — the DL-INLINE killer, the phase gate) · the sweep rows it answers: `tasks/briefs/s0-01-sweep-support/SWEEP-prod.md`
#7, #10, #23, #34, #39, #40 and `SWEEP-tests.md` 4.1 / 9.3 / 13.1 · the consumer: `proofs/S0-01/check_acp_conformance.py`
`check_timeline` (the exact key set that now rejects a lossy entry's `raw_b64`) and `proofs/S0-01/negative_contract.py` ·
`proofs/S0-01/pins.py` (`REDACTED_ENV_KEY_RE`) · `docs/INCIDENT-LOG.md` (AF-AP-55/57, the NaN/inf wormhole rows).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-01-n5h-support/N5h-report.md --rev <PIN> --map probe=proofs/S0-01/tools/acp_probe.py
--map test=tests/test_s0_01_acp_probe.py` — MISS 0 or a finding; `ap_screen.py` on the probe (8 hits, each classified by running it)
and `--tests` on the test file (the ONE AF-AP-57 hit at `test:1436` — DEVIATION 1: the lane kept a count-gated transient-retry fake
with three named guards and asks for a RULING; give it: is a count that IS the semantics (K transient failures) a legitimate exception
to AF-AP-57, and are the three guards sufficient? Write the mutant that would fool it if not).

## Items (grade against the brief; red-before on the parent for every new test; full file, never -x)
1. **The six rows + the ordinal gate — closure table**: one row per sweep row, red-before reproduced on the parent (the lane pasted
   each; re-run them), the green, verdict.
2. **#7 the read class.** The fixture `S_ISREG` guard (FIFO → rc 64 in bounded time; a directory; `/dev/zero`); `_sha256_file`'s guard
   covering three receivers — mutant SHA-GUARD-OFF re-run; then the lane's D1: the WRITE side is open (a FIFO at `runtime-identity.json`
   hangs the probe; at `agent-stderr.txt` it is silently swallowed rc 0). Reproduce both on the PIN with a bounded watchdog (kill the
   probe by pid). This is the class the round set out to close, still open at four output paths — grade it as the verdict demands
   (the sweep's rule: the class, not the instance), and design the fix the lane proposed (`_open_regular` for the four evidence writes
   + the M3 handler's rescue-write path) precisely enough for the next brief.
3. **#10 the drain failure recorded.** `stderr drain failed: IsADirectoryError…` exact; first error wins vs the entrypoint-hash guard —
   plant BOTH failures and show which message survives and whether the other is lost silently (a lost second error is a finding).
4. **#23 lossless copy.** `raw_b64` only on lossy lines; the strict-then-replace order; a line that is INVALID UTF-8 in the JSON
   string's escape (valid bytes, invalid surrogate `\udc80` escape — `json.loads` raises?) — which branch, and is the raw copy kept?
   Then the consumer: `check_timeline` REJECTS a lossy entry with `unexpected keys` — reproduce with the real checker; rule whether a
   lossy line in a captured leg should be a named checker failure (`timeline: lossy a2c line at seq N (raw_b64 kept)`) rather than a
   key-set message — this feeds A5k.
5. **#34 the mirror pinned** — `_REDACTED_ENV_KEY_RE.pattern == pins.REDACTED_ENV_KEY_RE`; the negative control that the probe stays
   import-free of `pins` (why must it? state the reason from the probe's runtime context: it runs on the PC inside the pinned venv
   where `pins.py` is not on the path — verify that claim from `run_leg.sh`/`pc_launch.py`).
6. **#39 the timeout domain.** All eleven rejected forms + the four accepted; the 400-digit overflow (D3) rejected by `isfinite` on the
   FINAL value; DEVIATION 2 (the regex gates accept; `float()` runs once in the reject branch to pick the message) — is there an input
   the regex rejects, `float()` accepts, and the message MISNAMES (says "not a valid number" for a numeric-but-out-of-domain form, or
   vice versa)? Enumerate: `1e3`, `+30`, `.5`, `5.`, `٣٠`, `30\n`, `' 30'`, `0x1p3`, `1_000`, `NaN`, `Infinity`, `-0`, `0.0`, `1e400`.
7. **#40 the runtime state** — `sys.dont_write_bytecode` in both records; the oracle is a child CPython; a `-B` flag on the interpreter
   (state true with the env unset) — recorded true? Run it.
8. **4.1/9.3 AF-AP-57** — the four fakes; the sentinel assertions; the ten-consecutive-runs stability under load (re-run 10× yourself
   with the box as it is and paste the counts); LATE-NOCLEAR / LATE-NULL / LATE-EVERY / AP-F1a / DL-INLINE mutants all re-run.
9. **13.1 — the SAFE ruling** on `os.readlink(f"/proc/{os.getpid()}/exe")` in the test: agree or refute.
10. **The PC gate (the carve-out)** from a clean detached worktree; paste beside the sandbox line; agree.
11. **Mutants ≥ 20** (the lane's 13 + yours); every survivor classed; `ran` = executed; killers from the run.
12. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census.
13. **The design.** Is the probe now closed on the read side as a CLASS (every `open`/`stat`/`readlink` receiver enumerated by an AST
    self-scan, as the checker does after A5j — or by a grep the next edit can drift past)? Should the same self-scan cover the write
    side? Keep it to what you measured.

## Report
Save to the session scratchpad `wf-results-r5/VERIFY-N5h.md` (draft after each item; return it whole). Findings: ALL, no severity
filtering, each with file:line on the PIN, expected vs observed, the failing input, the minimal fix, the exact red test, SOLID/UNSURE;
reproduced vs reviewed vs skipped; shared-tree hygiene; verdict MERGE-READY or NOT-READY with the blocking set — and the cheapest path
to MERGE-READY.
