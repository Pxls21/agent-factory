# VERIFY-B2 — adversarial grade of S0-02 round 2

PIN: `f737de55a8929ce2704f444aee8c073add4b2b24`

## Verdict: NOT-READY

This is a PC-lane adversarial report, not an acceptance verdict. The static
proof suite is reproducibly green, but three independent defects in the
proposed evidence path leave a false-green route. The live eight-leg capture
also remains uncaptured. Sandbox-side adversarial verification still owns any
final gate decision.

### Findings

1. SOLID — expected-leg directory symlinks are accepted.

   At C:567-589, root closure checks only extra names and `_check_leg` uses
   `_require_dir`; neither requires every expected entry to be a real,
   non-symlink directory contained by the evidence root. On a scratch copy of
   the committed pass bundle, I replaced `legs/neg-stale` with a symlink to an
   external copied leg. The actual checker returned rc 0 and its normal PASS
   line. This violates the item's required symlink attack and makes root
   closure a name check rather than evidence containment.

   Minimal fix: before any evidence read, reject `is_symlink()` for the root,
   every expected leg and replay sub-leg, and verify each resolved directory is
   below the resolved evidence root. Add a negative-control test that symlinks
   an expected leg to a complete outside directory and requires rc 1.

2. SOLID — the producer normalises non-boolean relay `accepted` values with
   Python truthiness.

   D:120-143 uses `bool(blob["accepted"])`. Scratch calls to the actual
   `_normalise` showed a relay response with `{"accepted":"false",...}` becomes
   The stored-bundle checker then sees a proper bool and cannot distinguish the
   malformed upstream response. This violates the claimed producer-shaped,
   strict receipt contract at the only live receipt producer.

   Minimal fix: accept `accepted` only when `type(value) is bool`; otherwise
   preserve a non-success receipt with a named malformed-response message (or
   fail `deliver_event.py` before writing the bundle). Add direct `_normalise`
   tests for string, integer, float and bool values, including the string
   `"false"` case.

3. SOLID — whitespace-only `BUZZ_PRIVATE_KEY` passes the preflight and reaches
   signing with an empty key.

   The key resolver checks the untrimmed environment value and only then
   returns `key.strip().lower()`. The actual scratch invocation returned an
   empty normalized key for a whitespace-only input; absent and empty values
   exited non-zero. That violates the brief's “absent or empty fails loudly
   before any network action” requirement for a common pasted-secret failure
   class.

   Minimal fix: normalize first, then reject the empty normalized value. Add a
   test for spaces, tab/newline-only input, and a surrounding-whitespace valid
   throwaway key. No key material is needed for this unit-level assertion.

4. UNSURE — the freshness source scanner is not a proof against equivalent
   dataflow-shaped wall-clock checks.

   The source scanner classifies only a line that contains both clock and
   event-time tokens, so a three-statement freshness rule evades it.
   `event_time = event.created_at`, `age = clock.duration_since(event_time)`,
   then `if age > maximum_age`; the actual channel-path test remained green.
   This is outside the implemented scanner's stated syntax class, so it does
   not falsify its narrow explicit-form claim. It does falsify any broader D3
   claim that the test proves there is no wall-clock freshness rule on the
   channel path.

   Minimal fix: narrow the report/contract to direct syntactic comparisons, or
   parse/type-check the channel arm with a Rust-aware analysis that follows
   local aliases and dataflow. Do not describe the present grep-like predicate
   as a general “no rule” proof.

5. UNSURE — the membership-removal receipt is still unauthenticated
   coordinator-authored evidence.

   The checker validates the removal's internal fields and ordering only. The
   runner copies an externally supplied JSON receipt after the leg wipe. There
   is no signature, relay response digest, authenticated query, or independently
   observed relay state. This does not negate the checker's structural ordering
   guard, but it means the revoked leg cannot prove an actual relay membership
   removal from these bytes alone.

   Minimal fix: bind a signed/attested relay response or independently capture
   and verify the post-removal membership state. Until then label this evidence
   coordinator-supplied and insufficient for an end-to-end revocation claim.

## Reproduced work

### Item 0 — mechanical gates and identity

I graded the archive pin, with the required venv first on PATH. The static
copy gate ran twice:

```text
RESULT: rev=f737de55a892 files=59 deleted=0 runs=2 identical=yes rc=0 summary="125 passed in 73.34s (0:01:13) 125 passed in 72.86s (0:01:12)"
```

The coordinator's quoted file count was 57; this run counted 59 commit files,
including `STATUS.md` and `todo/BUILD-TASKLIST.md`. Collection independently
reported exactly 125 S0-02 tests. The primary source identities named in the
brief matched the archive in the gate run. Pyflakes and `bash -n` were clean;
a fresh fixture build reported `fixture-drift: none (8 fixtures match a fresh
build)`.

`ap_screen.py` found AP-1 once in the delivery helper's environment lookup,
AP-32 three times (deterministic sha256 derivations), AF-AP-40 three times
(deferral/destination existence), and test-only AF-AP-34 lexical references to
prohibited kill-by-name commands.
The checker, oracle, fixture builder and delivery helper spawn no subprocess;
the runner's command census is its static owned-directory, launcher, bounded
poll, pidfile and delivery operations. I did not run the runner or delivery
against a relay.

### Item 1 — whole-source verification scanner

The targeted source tests ran 6 passed. The exact six pinned sites were
observed, an added direct production call made the equality test red, and an
actual deletion of `lib.rs:256` made it red with `gone=['lib.rs:256']`.
Comments, block comments, an early `#[cfg(test)] mod`, and a two-line
`#[cfg(test)] fn` were excluded. The scanner sees a string literal, a
same-line cfg attribute, `#[cfg(any(test, feature = "x"))]`, and a trait
`.verify()` call as sites; it misses a static alias form and macro expansion.
The brief's required alias form `use ... verify_event as v; v(...)` is
covered by the suite and was red in the targeted source test.

The exact site set is therefore sound for the six source forms that currently
exist, but this is not a general Rust call-graph analysis. The awkward scanner
forms are scope limitations, not evidence that another form occurs at the pin.

### Item 2 — freshness scan

The direct-form test catches inline, reverse, bound-now, saturating, Duration,
9000, and match-arm syntaxes when the event-time and clock relationship occur
on a classified line. Finding 4 documents the reproduced multi-statement
evasion. The numeric relay drift check separately rejects a value 9000 where
900 is required. Thus the pin supports “no direct same-expression comparison
in the scanned arm,” not absence of arbitrary dataflow-equivalent freshness
logic.

### Item 3 — receipt shape

The stored-bundle receipt checks reject receipt strings, floats, extra/missing
keys, case-changed ids, and inconsistent accepted/status combinations.
Scratch attacks killed all eight requested bundle shapes. The synthetic builder
imports the live normalizer to construct its receipt shape, and the live helper
writes the normalized receipt after its HTTP response. The negative producer
truthiness defect is Finding 2.

### Item 4 — removal/wipe and trust boundary

The static runner sequence removes each output directory before its case arm;
for revoked, it copies the external membership receipt after the wipe. The
checker killed float, bool, equal/after-t0, wrong channel, non-2xx, string
status, and wrong-sender receipt attacks. Its evidence authenticity boundary
is Finding 5.

### Item 5 — replay timing

The checker gives only the replay second sub-leg the 150-second tolerance, and
the runner passes the first sub-leg t0 into the reused second delivery. The
121-second second-t0 attack passed and 151 seconds failed; the first sub-leg at
121 seconds failed. This is a typed local allowance, not a value derived from
the pinned relay constant.

### Item 6 — level-aware canary

C:318-356 requires a complete canary on a DEBUG-token line only for
buzz-acp evidence rows. INFO with message-text `DEBUG`, lowercase debug, TRACE
and split-line variants were rejected. The three affected oracle rows are
replay, self-authored and not-allowlisted; relay-decided rows need no canary.

### Item 7 — observable channels and closure

The checker killed named observables duplicated in both evidence channels and
two different observables in one log. Extra root files and trailing-space leg
names are rejected, and a FIFO was rejected under standalone timeout with
`is not a regular file`. An unexpected regular file *inside* a leg is not
rejected, because closure is implemented only at the root; the brief's phrase
“a leg directory with an extra regular file” is therefore not satisfied.
Finding 1 is the stronger containment failure for an expected-leg symlink.

Allowed root entries are exactly the eight `LEG_NAMES`: pos-allowed plus the
seven negative fixture names. `PROVENANCE.md` at this root is rejected.

### Item 8 — sixth distinct leg

The actual pass checker returned the expected summary, and the blanket bundle
returned:

```text
failure_reason: blanket-rejection: reasons ['delivery::restricted: not a channel member'] not distinct — 6 negative legs collapsed to 1 observable(s)
```

O:245-266 assigns `neg-not-allowlisted` to user2 and its distinct
`buzzacp_log::inbound author gate` evidence. The pinned source confirms the
author gate logging/drop at
`/home/rocco/s0-01-pinned/buzz/crates/buzz-acp/src/lib.rs:543-552`; relay
membership rejection is at
`/home/rocco/s0-01-pinned/buzz/crates/buzz-relay/src/handlers/ingest.rs:750-770`.

### Item 9 — D8

The pin copies `created_at` into `FilterContext.timestamp` at pinned
`filter.rs:37-48` and binds it at `filter.rs:318-330`; the normal inbound
match call is at `lib.rs:599-606`. The supplied static shipped-default test
passes. Residual risk: a configured filter can gate on timestamp. No live
config or live capture was exercised.

### Item 10 — environment key preflight

Absent and empty variables both exited loudly before `_post`; wrapped valid
shape normalized successfully without printing it. Whitespace-only input
returned empty, producing Finding 3. I did not send any HTTP request.

### Items 11–12 — attack and sweep result

Independent scratch reconstruction killed the eight receipt, eight removal,
four canary/observable, root garbage, trailing-name, FIFO, and timing attacks
listed above. It also exposed the expected-leg symlink and producer truthiness
survivors. The supplied suite's 125 tests passed, but the lane's asserted
“20/20” mutant claim is not sufficient for the broader item-11 minimum because
these additional mutants survive.

The evidence reads are mostly routed through imported S0-01 regular-file
helpers: delivered event, receipt, fixture, t0, membership and log. Timeline
reading is delegated to the S0-01 loader. The early deferral helper at
C:556-564 uses `.exists()` before root containment is established; it is not a
read but contributes to Finding 1's symlink bypass.

### Item 13 — reference and process discipline

The inherited incremental draft's references all resolve to existing lines,
but its actual `report_lint.py` run returned rc 1: 16 OK, 1 NEAR, 7 MISS and
3 UNCHECKABLE. Its claims should not be relied upon as lint-clean evidence.
No processes were started in background and no PC service, relay, membership
or role-key operation was performed.

### Item 14 — design state

The synthetic bundles reproduce checker-compatible producer field shape but
not a live HTTP exchange, relay membership transition, ACP process wiring, or
turn reachability. A live capture needs the eight closed leg directories,
actual 200/400 response semantics and IDs, exactly one declared observable per
negative leg, the positive turn, replay 1 then 0 turns, and a corroborated
pre-delivery membership removal.

Coordinator-owned prerequisites remain: RUST_LOG in the closed S0-01 launch
environment for the three buzz-acp debug observables; per-role delivery keys;
and the relay membership removal/corroboration for revoked. The owner must
approve/run those live operations. The runner's preflight correctly refuses
rather than fabricating an INFO-level capture.

## Scope and omissions

Reproduced: static gate, 125-test collection and targeted source tests,
fixture drift, source-to-oracle mechanism reads, scratch bundle mutations,
standalone FIFO behavior, symlink mutation, receipt normalization, and key
preflight behavior.

Reviewed statically: PC runner, delivery network call path, source defaults,
and external command census.

Deliberately skipped: live delivery, membership writes, role-key reads, relay
or PC-service actions. They are expressly coordinator/owner-only under this
venue. No final test/gate verdict is issued by this single-model PC lane.

## Cheapest path

1. Fix Findings 1–3 with red tests, then rerun the static gate and an
   independent sandbox adversarial grade.
2. Make the freshness claim narrow or replace its scanner with Rust-aware
   analysis.
3. Capture the real eight-leg evidence only after the coordinator supplies the
   RUST_LOG seam, role keys and a corroborated membership-removal operation.
