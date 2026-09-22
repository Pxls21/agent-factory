# PC lane — VERIFY-B67 (targeted adversarial verification of TWO landed repairs on the S0-02 test file: B6's real-CLI key refusal and B7's runner preflight + env-set selection)

PIN: 22bd6f5

Role: adversarial-verifier. Route: the LOCAL Qwen verify route (`agentfactory-verify-local`, the pc_lane.sh default for
adversarial-verifier — do NOT set HERMES_MODEL; the effort is the vLLM server's default, D-028's xhigh is not
verifiable on this route). Venue: `tasks/briefs/pc/VENUE-MAP.md` — read it first. Report: draft after EACH item at
`tasks/briefs/s0-02-support/VERIFY-B67-report.md`, return it whole as your final message. You VERIFY; you never fix.
A finding is file:line-bounded, reproduced through the real path, and graded by the blocking predicate
(contract-mapped · reproduced canonically · materially effective · a concrete discriminator · in-boundary). Emit a GATE
RECOMMENDATION (MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID), never a verdict — the
coordinator decides; under D-034 a non-blocking finding becomes a `verify-followup` issue. TWO sibling lanes may share
this host (VERIFY-S4H, K1-d) — never touch their trees. Owner authorization: defensive test-oracle work on the owner's
own repository and its isolated test harness.

## Scope — two repairs on one file, nothing else
- B6 (issue #3; landed c439580; report `tasks/briefs/s0-02-support/B6-report.md`): the F3 pre-network key refusal of
  D = `proofs/S0-02/tools/pc/deliver_event.py` EXECUTED through the real CLI in a subprocess with a closed environment
  against an OWNED 127.0.0.1 listener that counts accepted connections — `test_cli_refuses_a_malformed_key_before_any_connection`
  (T2:1922; rc 1, the exact `REFUSE_TEXT` T2:1838, `listener.count == 0`) and the connecting positive control
  `test_cli_with_a_valid_key_reaches_the_owned_listener` (T2:1961; a deterministic throwaway secp256k1 scalar
  T2:1949, one accepted POST with Authorization + Content-Type); helpers `_OwnedListener` T2:1848, `_run_deliver_cli`
  T2:1901 (the key travels ONLY via env, AF-AP-39). The lane's F3-KEY-SHAPE-BYPASS mutant (`len(key) != 64` alone,
  message kept) dies at the `REFUSE_TEXT` equality (both paths exit 1 — the text discriminates, the rc could not).
- B7 (landed 22bd6f5; report `tasks/briefs/s0-02-support/B7-report.md`): R = `proofs/S0-02/tools/pc/run_s0_02_legs.sh`
  R:52-68 the preflight greps BOTH exact S0-02 pin definitions in `proofs/S0-01/pins.py` (`^PINNED_ENV_KEYS_S0_02 =
  .*{"RUST_LOG"}` with grep -E; the exact line `PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}` with grep -Fx) BEFORE
  `mkdir -p "$DEST"`, exit 3 with the BLOCKER text on a miss; R:72-74 `launch_leg` passes `--env-set s0-02`;
  T2:1725 `test_pc_runner_preflights_and_selects_the_s0_02_env_set` (source-string pins on R and pins.py);
  T2:807 `test_real_evidence_root_is_not_a_passing_bundle_today` (a partial root rc 1 or an absent root rc 2, `PASS:`
  forbidden). The runner reads `REPO=${S0_02_REPO:-/home/rocco/agent-factory}` (R:22), so a scratch tree can drive its
  preflight without touching the repository.
- T2 = `tests/test_s0_02_buzz_authz.py` (1991 lines at the PIN). The frozen checker `proofs/S0-02/check_buzz_authz.py`,
  the oracle, the fixtures and D are byte-identical to 236bec7; the S0-02 proof is NOT minted (the live capture is
  blocked on issue #11's three owner decisions — out of scope here).

## PREMISE — MEASURED at authoring (2026-09-22 05:5xZ, the sandbox clone at 22bd6f5); re-measure as item 1
```
git log --format='%h %s' 236bec7..22bd6f5 -- proofs/S0-02 tests/test_s0_02_buzz_authz.py
  22bd6f5 S0-02 runner: B7 LANDS the env-set selection + the exact-pin preflight …
  c439580 S0-02 B6 LANDED (issue #3): the F3 pre-network key refusal EXECUTED …
git diff c439580^ c439580 -- tests/test_s0_02_buzz_authz.py | grep '^@@'
  @@ -11,13 +11,16 @@        @@ -1810,3 +1813,171 @@
git diff 22bd6f5^ 22bd6f5 -- proofs/S0-02/tools/pc/run_s0_02_legs.sh tests/test_s0_02_buzz_authz.py | grep -E '^diff|^@@'
  R: @@ -46,21 +46,21 @@   @@ -70,6 +70,7 @@       T2: @@ -804,12 +804,16 @@   @@ -1718,20 +1722,24 @@
sha256 at 22bd6f5: T2 4444842b886ac7debf3bccceaba8cb55eae83e577ebbfb491bc0b3f147426dc6
                   R  c092e8797ee7c42b06e578a2887b3905555fff65472c913effd039e4ff7123cb
                   D  a14c027b0da2f341cce8b37dfcce4efbd947fe49b1bc2bec5831f1cd5e00cf8a
```
The range 236bec7..22bd6f5 also carries S0-01 and S0-04 landings on OTHER paths (A5q, S4H, the symlink cleanup) — they
are not this brief's surface; the premise is the two S0-02 commits above and the three identities. The 21 venue-gated
tests in T2 run only with the PC pair exported (VENUE-MAP line 12); the lane pasted `151 passed` ×2 with it.

## Items (each: what you did · the exact command · the exact output · SOLID/UNSURE · blocking? each predicate clause)
1. PREMISE (first; stop on failure): re-run the four measured commands above on your worktree and paste them; a
   different hunk set or identity means the premise is false — CONTRACT-INVALID and stop. Then `python -m pytest -n 4 -q
   -p no:cacheprovider --basetemp ../scratch/bt/pre tests/test_s0_02_buzz_authz.py -k "cli_refuses or cli_with_a_valid_key
   or preflights_and_selects or not_a_passing_bundle_today"` → the four tests pass (paste).
2. B6 THROUGH YOUR OWN LISTENER (never the test's helper): write a scratch listener that counts accepted connections
   AND records whether any bytes arrived, run the REAL D CLI as a subprocess with a CLOSED env (`env={"BUZZ_PRIVATE_KEY":
   <shape>, "PATH": …}` and the exact argv shape of T2:1901-1918 — `--secret role.env` is a NAME, never a value; the key
   never in argv), and fill this table with rc · stderr first line · connections · bytes: (a) the throwaway valid key
   (T2:1949) → a connecting POST; (b) 63 hex chars, (c) 65 hex chars, (d) 64 chars with one `g`, (e) `0x` + 62 hex,
   (f) EMPTY, (g) whitespace-only → the OTHER refusal text ("not in the environment", D:80-83), (h) the valid key
   UPPERCASED, (i) the valid key padded with spaces and a newline → D:78 normalises (strip + lower) — expect a
   connecting POST, not a refusal; (j) all-zero 64 hex `0`×64 and (k) `f`×64 (≥ the secp256k1 order n) — shape-VALID
   at D:84, so what happens next is decided by `nv.sign_event` BEFORE any connection: paste rc, the stderr first line
   (a named refusal? a raw traceback?) and connections (expect 0 either way). A raw traceback on (j)/(k) is a finding
   graded by the predicate (D's shape contract cites nv.sign_event's "64 lowercase hex", which does not bound the
   scalar; say whether the consumer refuses these itself). Confirm with `ss`/the listener that connections == 0 on
   every refusal row; the B6 claim is "before any connection".
3. SIDE-EFFECT ORDER: D:176-178 creates `leg_dir` (`mkdir(parents=True, exist_ok=True)`) BEFORE `_privkey()` at D:180,
   so a refused run leaves an EMPTY leg directory. Reproduce (the leg dir exists after row (b) with no files), then read
   R's collect/copy steps: can a refused key leave a half-made leg under the runner's evidence root that the frozen
   checker later grades as "leg directory present but files absent" versus "leg directory absent" (B7's checker output
   on the partial root was `neg-unauthorized leg directory absent`)? Grade by the predicate; the B6 claim (no CONNECTION
   before the refusal) is unaffected — say so explicitly.
4. THE POSITIVE CONTROL'S STRENGTH: from your listener's captured request (row (a)), decode the `Authorization: Nostr
   <base64>` NIP-98 event (D:92-104): its `payload` tag must equal sha256(body), `u` the exact URL, `method` POST, and
   `nv.verify_event(event)` must be True with the pubkey derived from the throwaway key; state which of these the B6
   test T2:1961-1983 asserts and which it does not (an unasserted binding is INFO with the one-line assertion
   suggested). Also `_normalise` (D:118) on your listener's `{}` body: paste the receipt dict the CLI wrote to
   `delivery.json` and say whether `accepted`/`event_id_echoed` are typed as B3 pinned (bool; the echo False on `{}`).
5. MUTATION AUDIT on scratch copies (`git archive 22bd6f5`, one mutant tree at a time, deleted after; every mutant must
   compile and collect — AF-AP-78): D mutants — (m1) the lane's F3-KEY-SHAPE-BYPASS (`len(key) != 64` alone) → which
   test reds and at which assertion; (m2) `_privkey()` moved AFTER `_post` (the key checked after the network call) →
   the refusal test must red at `listener.count == 0` (the BEHAVIORAL kill — paste); (m3) the refusal's `raise
   SystemExit(...)` replaced by `return ""` (the CLI continues with an empty key) → what reds first; (m4) `.strip()`
   removed at D:78 → does any CLI-level test red (row (i) is the discriminator; if only the in-process B3 test T2:1801
   catches it, say so). R mutants — (m5) `grep -Fqx` → `grep -Fq` for the VALUES line: on a scratch tree whose pins.py
   carries ONLY a commented-out `# PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}` the mutant passes the preflight
   wrongly — which TEST reds? (the source-string pin T2:1725 asserts the literal `grep -Fqx '` — a text mirror; state
   whether any BEHAVIORAL test drives the preflight through `S0_02_REPO` on a scratch tree — if none, that is the
   AF-AP-80 pairing gap: FOLLOW-UP with the test sketched, never written); (m6) the preflight block moved below `mkdir -p
   "$DEST"` → EVIDENCE_DIR_CREATED=yes on a refused pin set — which test reds (expect none → the same follow-up);
   (m7) `--env-set s0-02` dropped (the lane's control) → T2:1725 reds at `'--env-set s0-02' in launch` (paste).
   Behavioral preflight controls run ONLY on a scratch tree with `S0_02_REPO=<scratch>` and a scratch `DEST`, and ONLY
   the NEGATIVE arm (a mutated pins.py → exit 3 before any launch): NEVER let the runner pass its preflight on this host
   — a passed preflight launches buzz-acp against the harness. The positive arm is the B7 report's measured live launch;
   cite it, do not repeat it.
6. DE-VACUOUS: flip each new assertion in the four tests on scratch copies → red at its own line (the refusal count
   0→1, the positive count 1→0, `REFUSE_TEXT` altered by one character, `REFUSE_RC` 1→0, the launch-string pin, the
   rc-set `(1, 2)` → `(0, 1, 2)`); paste each.
7. Gates on the PIN's bytes (three lanes share the 12 cores): `python -m pytest -n 4 -q -p no:cacheprovider --basetemp
   ../scratch/bt/<run> tests/test_s0_02_buzz_authz.py` TWICE with the PC pair exported (the lane pasted `151 passed`
   ×2 / `150 passed, 1 skipped` ×2 — paste yours and name which test skips); `python -m pyflakes
   tests/test_s0_02_buzz_authz.py proofs/S0-02/tools/pc/deliver_event.py` rc 0; `bash -n
   proofs/S0-02/tools/pc/run_s0_02_legs.sh` rc 0; `python3 scripts/ap_screen.py proofs/S0-02/tools/pc/run_s0_02_legs.sh`
   (0 hits at the PIN) and `python3 scripts/ap_screen.py --tests tests/test_s0_02_buzz_authz.py` (11 pre-existing hits
   at the PIN: AF-AP-80 ×7, AF-AP-34 ×4 — anything else is a finding; name the lines).
8. Anything else INSIDE the B6/B7 hunks (T2:11-16, T2:804-819, T2:1722-1745, T2:1813-1983; R:46-76). Exhaustive
   discovery; disciplined disposition.

## Boundary
READ-ONLY on the tree: attack through SCRATCH COPIES only (`../scratch`); never git-restore/stash/checkout the shared
tree; never `git add/commit/push`; never touch the isolated harness (the relay on 127.0.0.1:3999, the backend on
:20201, the `s0-01-harness-*` containers) beyond your OWN loopback listener on an ephemeral port; never run a runner leg;
never touch the model server, any unit, the secrets under `/home/rocco/s0-01-pinned/.secrets/` (names only, never read),
or another lane's tree. No outward action.

## Gate mechanics (each call under Hermes's 420 s terminal cap)
- `export S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`;
  `/home/rocco/venv-agent-factory/bin` first on PATH; `mkdir -p ../scratch/bt`; an absolute SHORT `--basetemp`.
- pytest on this host: `python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt <files>` DIRECTLY
  (`scripts/pc_suite.sh` is the SANDBOX's launcher and cannot run here). T2 runs in ~15 s at -n 4.
- CODE INTEL FIRST: `graft skeleton` / `graft ask` before any whole-file read (T2 is ~2,000 lines — read by range).
  `report_lint` gates on a FLOOR (`--min-refs 12`, maps `T2=tests/test_s0_02_buzz_authz.py`
  `R=proofs/S0-02/tools/pc/run_s0_02_legs.sh` `D=proofs/S0-02/tools/pc/deliver_event.py`); apply its `fix:` hints for at
  most THREE rounds, then paste and finish; paste its summary as PLAIN text.

## Report shape (DATA)
Per item: command · exact output · SOLID/UNSURE · blocking? (the predicate, each clause answered) · the file:line.
Then: the key-shape table (item 2), the mutant table (item 5: mutant · killer · assertion · `N failed` or SURVIVES),
the positive-control binding table (item 4), DISCREPANCIES, NOT-done, GATE RECOMMENDATION. Never a fix, never a verdict.
