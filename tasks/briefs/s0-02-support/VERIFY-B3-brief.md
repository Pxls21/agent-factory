# VERIFY-B3 — adversarial grade of lane B3 (S0-02 round 3: closure is containment, the receipt typed at the producer, the key normalised first, D3 pinned as a limit, the tolerance bound, the removal receipt labelled — and the three brief items the lane's report never mentions)

You are an adversarial-verifier (the PC Hermes verify lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo
agent-factory, branch claude/soundbox-kit-migration-iz1jwf. **PIN: `c6c384a`** — the S0-02 round-3 LANDING: the coordinator's harvest
of lane B3's PC tree (PIN 887f341), a straight copy plus ONE coordinator touch (two unused imports removed from the test — the sandbox
pyflakes), plus the coordinator's attested regeneration (item 8). FILE IDENTITY at the PIN (lines, sha256[:8]):
`proofs/S0-02/check_buzz_authz.py` (765, `fc791273`) · `proofs/S0-02/tools/pc/deliver_event.py` (221, `a14c027b`) ·
`proofs/S0-02/tools/build_fixtures.py` (549, `38ae5a69`) · `proofs/S0-02/spec.json` (26, `7cc99c95`) ·
`proofs/S0-02/fixtures/PROVENANCE.md` (20, `23b1c09f`) · `proofs/schemas/spec.schema.json` (48, `f425996d`) ·
`tests/test_s0_02_buzz_authz.py` (1599, `3bfc6703`); the eight regenerated `delivery.json` under `fixtures/evidence-{pass,blanket}/legs/`;
the lane's report `tasks/briefs/s0-02-support/B3-report.md`; its transcript `transcripts/pc/pc-b3.md--887f341.md`.
Grade the bytes of `git archive c6c384a` from a scratch copy under your lane's scratch dir; every mutant on scratch copies; every pytest
run with an explicit SHORT absolute `--basetemp`, `/home/rocco/venv-agent-factory/bin` FIRST on PATH and the venue exports
(`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz` — the
drift-window test `T:643` reads the pinned Buzz tree through `_buzz_src()` `T:102-117` and FAILS, never skips, when the declared checkout
is absent; `T:37-38` names the env var and the sandbox default); kill only what you start, by pid; never background a run and stop; no
outward actions; no live relay delivery, membership write or role-key read — the live legs are the coordinator's; never read, print or
commit a credential (the identities files hold TEST identities — cite pubkeys only; every key you mint for item 3 is a throwaway on
scratch). Authorization: the owner's own Buzz authorization proof under test on the owner's system. Do NOT spawn subagents.

**Inputs (read in this order):** VERIFY-B2's report `tasks/briefs/s0-02-support/VERIFY-B2-report.md` (the round's contract: F1-F5
and the observations) · the lane brief `tasks/briefs/s0-02-b3-buzz-authz-closure-is-containment-the-receipt-typed-the-key-normalised-first.md`
(NINE pinned design items — the report covers six) · the lane's report (prose: `line ~120`, `line 651-vicinity`; no identity table; no
mutant list; `Items built (1–9)` over six subsections) · the pack `tasks/briefs/s0-02-support/VERIFY-B3-pack.md` (graft skeletons,
impact, callers, the registry screen — a start, never a verdict) · the pinned Buzz source (read-only) · `docs/INCIDENT-LOG.md`
(AF-AP-56 attested inputs, AF-AP-62, AF-AP-65, AF-AP-72, AF-AP-73).

## Item 0 — the mechanical gates, pasted
The coordinator's gates on these bytes: sandbox `RESULT: rev=887f341ced9a files=19 deleted=0 runs=2 identical=yes rc=0
summary="137 passed in 86.36s (0:01:26) 137 passed in 70.82s (0:01:10)"`; the PC union run on the landed tip `4 failed, 1561 passed,
9 xfailed in 232.41s` (8 workers, 20260914T121247Z-c6c384a) — the four reds are `tests/test_proof_status.py`'s S0-11 re-acceptance class
(item 8), none in this suite. Agree or disagree by your own run of `tests/test_s0_02_buzz_authz.py` (ONE foreground call, twice, counts
pasted). Then the report-discipline gap: the B3 report lints `report_lint: 0 refs — OK 0, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0
(at c6c384a)` — machine-clean because it cites NOTHING machine-checkable (brief item 9 demanded every `file:line` from `grep -n` on the
final bytes with MISS 0; round 2's report had the same gap, VERIFY-B2 item 0). Resolve every claim in the report against the PIN
yourself and list the claims with no anchor. `ap_screen.py` over the four production sources (paste; the coordinator's run: AP-32 ×3 —
the specimen/payload sha256 derivations; AF-AP-40 ×1 — `build_fixtures.py:428 if root.exists():`, a check-then-act on the fixture
root, classify by RUN; AP-1 ×1 — `deliver_event.py:78`, the resolve-once design, classify) and `--tests` (AF-AP-34 ×4 = the test's own
scanner words at `T:1467,1471`); pyflakes; `bash -n proofs/S0-02/tools/pc/run_s0_02_legs.sh`; `build_fixtures.py --check`
(`fixture-drift: none`); the FILE IDENTITY table against the PIN; the external-command census (VERIFY-B1 F23) by pid.

## Items
1. **F1 — containment (`C:102-118` `_require_real_dir`; `C:651-660` the root; `C:155-171` `_leg_closure`; `C:629-650`
   `_has_any_timeline`; `C:96` `_require_file = s0_01._require_file` → `proofs/S0-01/check_acp_conformance.py:198-208` →
   `proofs/S0-01/pins.py:19-26` `require_regular_file`, `os.stat(follow_symlinks=False)` + `S_ISREG`).** Reproduce the B2 attack first
   (the expected leg `legs/neg-stale` replaced by a symlink to a complete outside copy → rc 1, the named reason). Then: a symlinked ROOT;
   a symlinked replay sub-leg; a symlinked FILE inside a leg (`delivery.json` → an outside file: which guard refuses it, which message);
   a HARDLINKED file inside a leg (`S_ISREG` passes — state whether shared bytes are inside or outside the containment claim, and why);
   an extra regular file; a leftover `.probe/` directory (the runner makes and removes it, `R:163-166`; dotfiles ARE in `iterdir()`); an
   EMPTY required file; a leg directory that is a FIFO (standalone under `timeout`, never through pytest); a leg name with a trailing
   space; the replay leg with a third sub-leg, with `first` only, with both sub-legs symlinked; `membership.json` inside a PLAIN leg;
   the revoked leg without it (the named `missing`); the two committed bundles PASS unchanged. The brief's item 1 also demanded a
   `path.resolve()` ancestor belt per node: `.resolve(` occurs at `C:660` only (the root) — decide whether the lstat chain (root →
   leg → sub-leg → every file) makes the belt redundant, name the one node class it would still catch if any (a root reached THROUGH a
   symlinked parent is the operator's own path — say so or refute), and rule the brief's `RESOLVE-DROPPED` mutant EQUIVALENT or a
   missing belt with its red test. The table `C:143-152` against the PRODUCERS, pasted as your own enumeration: `fixture.json`,
   `delivered-event.json`, `t0.json`, `delivery.json` from `deliver_event.py:206-212`; `timeline.jsonl`, `buzzacp.log` from
   `R:115,117`; `membership.json` from `R:185`. Then `test_leg_file_table_matches_the_runner_writes` (`T:1373-1465`): what does it
   PARSE — the runner, the producer, both? A write it cannot see (a `tee`, a heredoc `cat > "$out/x"`, a `python3 -c` that opens a
   file, an `mv` into the leg) planted in a scratch copy of the runner — red? If not, the test is a mirror of its own regex: say so
   with the red test that would make it a gate.
2. **F2 — the receipt typed at the producer (`D:118-163` `_normalise`; `type(blob["accepted"]) is bool` at `D:143`; the malformed
   message `D:148`).** Direct in-process calls: `"false"`, `"true"`, `0`, `1`, `1.0`, `True`, `False`, `None`, the key absent, a non-JSON
   body, an empty body, a JSON array, a 2xx with `accepted: false`, a 4xx/5xx with `accepted: true` — every outcome exact (five fields
   always; `accepted` never truthy from a non-bool). `event_id_echoed`: an echoed id differing by case, by whitespace, an id echoed under
   another key. Is `_normalise` the ONE writer of `delivery.json` (grep every writer: the runner, the builder `B`, tests)? Rebuild the
   eight fixtures fresh on scratch and diff BYTES against the committed set. Then the consumer: a receipt `{accepted:false,
   http_status:200, message:"malformed relay response: …"}` on a POSITIVE leg — the checker's leg verdict (find the receipt rule at
   the PIN; reproduce that the leg FAILS with a reason naming the receipt, never a pass on `http_status`).
3. **F3 — normalise, then refuse (`D:71-90` `_privkey`: `.strip().lower()` at `:78`, empty → `SystemExit` `:80`, the shape `:85-86`
   "exactly 64 lowercase hex"; `main` calls `_privkey()` at `:182` before `_post` at `:203`).** Throwaway keys never printed: spaces
   only; `\t\n` only; a valid key with surrounding whitespace and a trailing newline (normalised); 63 chars; 65 chars; UPPERCASE hex
   (lowercased → accepted: intended? state it); an inner space; a `0x` prefix. The network-ordering claim by BEHAVIOUR: an unreachable
   `--relay-http` (a closed port on 127.0.0.1 — or a listening socket of yours that must see nothing) with an invalid key → the shape
   `SystemExit` and NO connection attempt (`strace -e trace=connect` or your socket's log); `T:1588`
   `test_privkey_normalises_then_refuses_before_any_network_action` asserts SOURCE ORDER — state whether it is a mirror and what a
   behavioural test needs (the red test).
4. **F4 — D3 pinned as a documented limit (`T:599-614`).** Reproduce that the three-statement plant is NOT caught and that the control
   is written so the claim cannot silently widen (which assertion dies if the scanner grows to catch it — is that the intended
   direction?). Then the direct-expression scanner itself with VERIFY-B2 item 2's shapes (a helper `fn age(e)`, a bound `now` two
   statements earlier, `saturating_sub`, a `Duration` comparison, the other direction, `9000` vs `900`, a `match` arm): which evade; and
   quote the test docstring and the report's D3 sentence side by side — is the stated class EXACTLY the class the scanner proves?
5. **The tolerance bound (`C:121` `RELAY_DRIFT_WINDOW_S = 900` — typed, the comment cites `ingest.rs:2224`; `C:124`
   `LEG_CLOCK_TOLERANCE_S = 120`; `C:127` `REPLAY_CLOCK_TOLERANCE_S = 150`; `T:643-660`
   `test_relay_drift_window_matches_the_checker_constant` reads `const MAX_TIMESTAMP_DRIFT_SECS: i64 = N;` from the pinned tree).**
   Attack the regex (`T:646`) on a scratch copy of the pinned `ingest.rs`: the constant as `u64`, as `900_000`, as an expression, declared
   twice, commented out — which passes a wrong value. Brief item 6 demanded TWO assertions: `REPLAY + LEG < RELAY` (joint satisfiability)
   and the runner's replay gap constant `<= REPLAY_CLOCK_TOLERANCE_S` (grep the gap in `R`; cite it) — which exists at the PIN, which is
   missing (each missing one is a finding with its red test; the `TOLERANCE-9000` mutant must die by name). `T:1033`
   `test_replay_second_subleg_uses_only_the_wider_replay_tolerance`: the tolerance applied to `first`; `second/t0.json` carrying the
   first's t0; 149 s / 151 s; a replay whose second delivery is EARLIER than the first.
6. **F5 — the removal receipt labelled (`C:547-555` the per-leg line, `C:718` the bundle line; `spec.json:3-4` `limits.removal_receipt`;
   `spec.schema.json:10-12` — `limits` is an object of strings with OPEN keys; `fixtures/PROVENANCE.md`).** Does `T:702` pin the KEY
   `removal_receipt` or only the sentence (a `limits.anything` with the sentence passes the schema — say what the test binds)? The
   sentence mutated in ONE of its two occurrences (the lane mutated both) — which test dies? The report's self-attack 3 makes three
   claims — the label is appended only after a 2xx relay response, only when the removal precedes delivery, and the revoked leg never
   PASSES without its receipt — reproduce each conjunct by RUN (a revoked leg whose `membership.json` is empty, `{}`, a symlink, a bool
   `at_epoch_s`, `at_epoch_s == t0`, one second after t0, a removal for another sender, for another channel — B2's item-4 set re-run).
   State the trust boundary of the receipt exactly (unauthenticated bytes; what the checker verifies, what it cannot).
7. **Items 7, 8, 9 of the build brief — absent from the report.** (7) the B2 report carries NO stamp line (`head -3` of
   `tasks/briefs/s0-02-support/B2-report.md` at the PIN) — NOT done; (8) the report offers two red controls and one label mutation as its
   only mutation evidence — no named mutants, no killer lines; (9) no identity table, no lint, no `ap_screen` paste, no pack. Grade each
   NOT-done unless the tree shows otherwise; the `Items built (1–9)` heading over six items is itself a report-discipline finding.
8. **The attested regeneration (the coordinator's, inside the PIN).** `proofs/schemas/spec.schema.json` gained `limits` → the five minted
   `proofs/*/result.json` regenerated (AF-AP-56) → the owner's signed `accepted/S0-11` tag no longer matches. Confirm at the PIN:
   `python3 scripts/validate-ledger integrity --root .` PRESENT ×5; `python3 scripts/ledger-gen --root .` then `git diff --exit-code
   proofs/ledger.json` clean; `check-proof-status.py` reports the re-acceptance line for S0-11 and nothing else; `tests/test_proof_status.py`
   with a SHORT `--basetemp`: which tests fail and by WHICH assertion (expected three, the committed-state re-acceptance class; read the
   assertion, never the count — a long basetemp adds gpg-socket false reds, a venue fact).
9. **Mutants ≥ 30 in total**, every one on a scratch copy, the killer line pasted, by-construction survivors stated: the brief's ten named
   (`LEG-SYMLINK`, `ACCEPTED-TRUTHINESS`, `KEY-WHITESPACE`, `ROOT-SYMLINK`, `LEG-EXTRA-FILE`, `RESOLVE-DROPPED`, `LSTAT-TO-ISDIR`,
   `TYPE-TO-ISINSTANCE-INT`, `TOLERANCE-9000`, `LABEL-DROPPED`), B2's 20 rows from YOUR reconstruction (never the lane's driver), the
   attacks above that no test kills.
10. **The 18-class re-scan** over the seven files by RUN; every `if <field> == <literal>:` without a raising other arm (AF-AP-65); every
    evidence read through the regular-file guard — enumerate the guarded reads (`C:171,379,499,506,665` and the rest) and every
    `read_text()` / `open(` / `json.load` on evidence bytes NOT behind it.
11. **Discipline** — `file:line` by `sed -n` on the PIN; `report_lint.py` on your own report with `--rev c6c384a --map
    C=proofs/S0-02/check_buzz_authz.py --map T=tests/test_s0_02_buzz_authz.py --map O=proofs/S0-02/oracle/denial_table.py --map
    B=proofs/S0-02/tools/build_fixtures.py --map D=proofs/S0-02/tools/pc/deliver_event.py --map R=proofs/S0-02/tools/pc/run_s0_02_legs.sh`
    pasted (MISS 0, UNRESOLVED 0); the process census by pid.
12. **The design.** Is the synthetic proof now the PRODUCER's shape end to end — the `.probe` sub-leg and the `--reuse` replay path
    (`R:145-166`), the flipped-signature refusal (`D:191`), the receipt the producer writes vs the receipt the checker grades? What must
    the live eight-leg capture show (RUST_LOG through P5c's `--env-set s0-02`, the role keys, the owner-run membership removal — the
    coordinator's and the owner's), and is anything left that is the LANE's? What must round 4 do, if anything, for S0-02 to be
    MERGE-READY?

## Report
Write it to `tasks/briefs/s0-02-support/VERIFY-B3-report.md` inside your tree, draft after EACH item, and return it whole as your final
message. Findings: ALL, no severity filtering, each with `file:line` on the PIN, expected vs observed, the failing input, the minimal
fix, the exact red test, SOLID/UNSURE; reproduced vs reviewed vs skipped; verdict MERGE-READY or NOT-READY with the blocking set and the
cheapest path; the items that are the coordinator's or the owner's named as such.
