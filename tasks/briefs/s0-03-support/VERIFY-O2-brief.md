# VERIFY-O2 — adversarial grade of lane O2 (S0-03 round 2: the call_logs row BOUND to the leg, conjunct (v) reads the wire, the credential screen over the whole provider block, `credential_rejected` RED, the round trip real, the pid the tee writes, leg B on the real capture path, a negative leg the producer can make, the model where Hermes reads it)

You are an adversarial-verifier (the PC Hermes verify lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo
agent-factory, branch claude/soundbox-kit-migration-iz1jwf. **PIN: `d12fc13`** — the S0-03 round-2 checkpoint, landed on top of
checkpoint 9c (the joint landing that carries P5b's `pc_launch.py --profile` seam the runner now uses: the runner's leg-B
invocation is red on any tree without it — `['--profile']` not declared — so the PIN's parent matters). O2's bytes on the PIN:
`proofs/S0-03/check_omniroute_roundtrip.py` (824 lines, sha `efba8162…`), `proofs/S0-03/tools/pc/{run_s0_03_legs.sh (313),
collect_leg.sh (175), direct_responses_probe.py (285), hermes_env_names.py (148)}`, `proofs/S0-03/hermes/config.yaml`,
`proofs/S0-03/spec.json` (54), the four fixture bundles under `proofs/S0-03/fixtures/` (two of them REGENERATED to the
producer's shape, `evidence-credential-rejected` NEW, the stale `evidence-credential-absent/hermes/*` files DELETED with a
`NOT-CAPTURED.md` in their place), `tests/test_s0_03_omniroute.py` (1734, `715a3cc6…`) and the lane's report
`tasks/briefs/s0-03-support/O2-report.md`. Grade the bytes of `git archive d12fc13` from a scratch copy under your lane's scratch
dir; every mutant on scratch copies; every pytest run with an explicit `--basetemp`; loopback servers you start are killed by
pid; NEVER make an OmniRoute, model or bridge request and NEVER launch Hermes, buzz-acp or the agent — the live legs (A, B, the
negative) are the coordinator's later capture; the OmniRoute API key on this host is never read or printed; no outward actions.
Authorization: the owner's own OmniRoute round-trip proof under test on the owner's system.

**Inputs (read in this order):** VERIFY-O1's report `tasks/briefs/s0-03-support/VERIFY-O1-report.md` (the round's contract:
F-1..F-23, the blocking set F-1/F-7/F-8/F-9/F-3/F-4/F-5/F-13, the cheapest path (a)-(i)) · the lane brief
`tasks/briefs/s0-03-o2-omniroute-the-row-bound-to-the-leg-and-the-real-capture-path.md` and its PC continuation
`tasks/briefs/pc/pc-o2.md` · the lane's report `O2-report.md` (§0 identity, §1 items 1-10 with red-before on b5670c1, §2 what it
added, §3 the mutant table, §4 the two RESULT lines, §7 DISCREPANCIES, §8 NOT-done, §9 self-attack) · P5b's report
`tasks/briefs/s0-01-p5b-support/P5b-report.md` §"THE EXACT ARGV FOR THE S0-03 RUNNER" and DECISIONS (the `S0_01_HERMES_HOME` seam
never moves the pinned constant) · `docs/INCIDENT-LOG.md` (AF-AP-40, AF-AP-42, AF-AP-56, AF-AP-65).

## Item 0 — the mechanical gates, pasted
`python3 scripts/report_lint.py tasks/briefs/s0-03-support/O2-report.md --rev d12fc13 --map C=proofs/S0-03/check_omniroute_roundtrip.py --map T=tests/test_s0_03_omniroute.py --map P=proofs/S0-03/probe_omniroute.py`
plus maps for every bare script name the report cites — the lane pasted `28 refs — OK 8, NEAR 0, MISS 0, UNCHECKABLE 20`; the
coordinator's run with the brief's three maps read `12 refs — OK 1, UNCHECKABLE 11`: resolve which map set the lane used and
whether any ref is a MISS at the PIN; `ap_screen.py` over the four S0-03 python files (4 hits, AP-1) and `--tests` (AF-AP-34 ×3,
AF-AP-59 ×1) — classify by RUN; pyflakes; `bash -n` ×2; `python3 scripts/validate-ledger integrity --root .` (S0-03 stays
EXPIRED/unminted — say so); the FILE IDENTITY table against the PIN; the four test files the lane brief names run directly
(the coordinator's runs are pasted in the checkpoint commit) — agree or disagree by your own run.

## Items
1. **F-1 — the row is BOUND to the leg (`C:455-686`).** Reproduce the lane's two red-before controls on the PIN's parent
   (forged identity PASS; duplicate row PASS) and the greens; attack the binding: a `response_id` that matches but a
   `status != 200`; two rows with the same `response_id` (one 200, one 500); a row whose timestamp sits at the window edge
   (the lane's "window equality, timestamp containment, unique-row controls"); the session tag on leg B (`extra_headers`) —
   INFERRED, not live-proven: what exactly must the capture show for it to count, and what does the checker do when the tag
   is absent vs foreign?
2. **F-3/F-4/F-5 — conjunct (v) reads the wire; the credential screen over the whole provider block; `credential_rejected`
   RED.** A credential under a key other than `api_key` (`extra_headers.Authorization`, `headers`, a nested dict, an env
   reference); `call_logs.path` variants (`/v1/responses` vs `/v1/chat/completions` vs a trailing slash); a REJECTED credential
   (401/403 rows) graded `credential_rejected` never `blocked:`.
3. **F-6/F-7 — the round trip real; the pid the tee writes.** The tool-output nonce assertion (an agent that quotes the prompt
   back must FAIL); `agent_child_pid` read from a real-shaped `runtime-identity.json` (the S0-01 corpus's real files at
   `/home/rocco/s0-01-pinned/realleg/golden/run-*/runtime-identity.json` — read-only: does `hermes_env_names.py` parse them?).
4. **F-8/F-22 — leg B on the real capture path (`run_s0_03_legs.sh:136-195`).** The invocation vs `pc_launch.py`'s DECLARED
   flags on the PIN (the test `test_runner_leg_b_uses_only_flags_pc_launch_declares` — reproduce it green here and RED on a
   tree without `--profile`); the escape hatch (F-22) gone?; the marker preflight; the per-leg Hermes profile/header wiring
   — static, every `set -e` exit path before a bundle exists.
5. **F-9/F-10 — a negative leg the producer can make.** `direct_responses_probe.py --no-credential` (or the lane's shape) +
   `collect_leg.sh` on the negative root produce the committed `evidence-credential-absent` bundle's SHAPE (AF-AP-42): regenerate
   from the producer on a loopback stand-in and diff against the committed fixture — every field the writer emits vs what
   PROVENANCE says.
6. **F-11/F-12/F-13/F-16/F-17/F-15/F-21 — one run each:** the env record's `exe`/`pid` asserted; the env allow-list deny-by-default
   over the name domain (a `BUZZ_PRIVATE_KEY` finding stays declared — the lane's self-attack 3); the profile's `model:` where
   Hermes reads it (cite the Hermes source path the lane read); decision-irrelevant fields; `NaN`/`Infinity` refused; the bound
   SQL route parameter (`collect_leg.sh:82-141` — a route value with a quote); the mktemp leak closed.
7. **The deleted fixture files and `NOT-CAPTURED.md`.** Is a bundle that carries only `direct/` + `omniroute-requests.json` +
   `NOT-CAPTURED.md` gradeable by design (which reason does the checker return), or does it PASS a conjunct by absence
   (AF-AP-40)?; the `evidence-credential-rejected` bundle's PROVENANCE vs its bytes.
8. **The mutant table (§3, the lane's + the verifier's)** reconstructed on YOUR scratch copies → ≥ 40 with the attacks above,
   killers pasted; by-construction survivors stated.
9. **The 18-class re-scan** on the checker, the two scripts and the two tools by RUN; every `if <field> == <literal>:` without a
   raising other arm (AF-AP-65); the lane's §6 table agreed or disagreed per row; the lane's declared deviations (read order,
   one `hermes sessions list`, three skill loads, one overwritten draft) weighed.
10. **Discipline** — file:line by `sed -n` on the PIN; `report_lint.py` on your own report; the process census by pid.
11. **The design.** Is `response_id` + `status` + the time window the right binding, or must the tag be mandatory for leg B?
    What must the coordinator's capture (legs A, B, negative) show for S0-03 to flip from EXPIRED to a minted result, and which
    items are the coordinator's (the capture, the class flip, the remint) vs round 3's (O3)?

## Report
Write it to `tasks/briefs/s0-03-support/VERIFY-O2-report.md` inside your tree, draft after EACH item, and return it whole as
your final message. Findings: ALL, no severity filtering, each with file:line on the PIN, expected vs observed, the failing input,
the minimal fix, the exact red test, SOLID/UNSURE; reproduced vs reviewed vs skipped; verdict MERGE-READY or NOT-READY with the
blocking set and the cheapest path; the items that are the coordinator's named as such.
