# VERIFY-GOV1 — adversarial verification of the FIRST production increment: `src/agent_factory/governance` + `src/agent_factory/audit` as LANDED at the PIN (GOV1 + the coordinator's AF-AP-81 amendment), graded against the CONTRACT (`docs/03_INTEGRATION_CONTRACTS.md` §3, the standing rules 8/9/13/14/15, the S0-07 corrections), never against the builder's own cases (verify lane: PC Hermes `adversarial-verifier` on the LOCAL route at xhigh; sandbox fallback Opus 5 `adversarial-verifier`)

PIN: `78f400d`

**What you grade.** The landed bytes at the PIN: `src/agent_factory/governance/{pin,packet,projection,bounds}.py`, `src/agent_factory/audit/events.py`,
`tests/test_governance_{pin,packet,projection,bounds}.py`, `tests/test_audit_events.py`, `tests/fixtures/governance/`, the driver
`tasks/briefs/stage3-governance-support/mutants.sh`, `pyproject.toml`, and the provisioning `scripts/fubuki_pin_sync.sh` + `tests/test_fubuki_pin_sync.py`.
The builder's report is `tasks/briefs/stage3-governance-support/GOV1-report.md` (with the coordinator's amendment at its top); the pack over
the modules is `tasks/briefs/stage3-governance-support/VERIFY-GOV1-pack.md` (START FROM IT). The upstream is the pinned fubuki-os
(`upstream.lock.yaml`: `7375e56d6a5dc857bfd43ceccbc09bbc817d575a`) — on this venue at `FUBUKI_OS_ROOT=/home/rocco/fubuki-pin/fubuki-os` with the
negative control `FUBUKI_OTHER_ROOT=/home/rocco/fubuki-pin/fubuki-os-other` (one empty commit above the pin; provisioned by
`scripts/fubuki_pin_sync.sh` — run it once yourself to re-verify, it is idempotent and refuses drift). Export BOTH variables for every
pytest call; the suites FAIL by design without them (a declared input, never a skip). `report_lint.py` map for the builder's report:
`--map C=proofs/S0-07/check_fubuki_corrections.py --map P=src/agent_factory/governance/packet.py --map J=src/agent_factory/governance/projection.py --map B=src/agent_factory/governance/bounds.py`.

**The known state you must not re-discover as news.** (a) The pinned upstream carries NO review/approval field: `load_packet` fails closed on
every packet (`fubuki-packet-unreviewed`) — declared by the builder, kept by the coordinator, GOV2's first item (a first-party review record
keyed by the governance hash). Grade the REFUSAL (it must be unforgeable from package sources — item V2), not the absence of a success path.
(b) AF-AP-81: the lane's `29 passed` had been green only through an ambient PYTHONPATH; the landing fixed it (the pin inserts both upstream
roots, the suites pin through the production function). Reproduce the bare gate (item V10); do not re-report the fixed class as open.

## Items (every item = a reproduced probe with its exact command, output and file:line; MERGE-READY needs every BLOCKING item closed)
- **V1 — the pin is advisory unless threaded.** `lint_sources`, `compile_canonical`, `load_packet` and `bound_records` import `fubuki_os` / `lint`
  lazily (`P:61`, `P:82`, `P:108-111`, `B:47`) with no proof the pin ran. Attack: insert a DIRTY or WRONG-COMMIT checkout's `src` and root into
  `sys.path` by hand (never call `verify_pinned_fubuki`), then call `compile_canonical` and `bound_records` on the fixtures — does anything refuse?
  Expected: nothing does. State it as a finding with severity (the contract says the packet is compiled from REVIEWED, PINNED sources; a caller
  that skips the pin compiles from anything) and the fix shape (a required `PinnedFubuki` parameter — the token obtainable only from
  `verify_pinned_fubuki` — threaded into every upstream-touching function; the #2 tactic). BLOCKING if an unpinned upstream reaches the hash.
- **V2 — the reviewed bit must be unforgeable from package sources.** `_reviewed` (`P:134-139`) accepts `reviewed: True` or `review_status ∈
  {approved, reviewed, certified}` read from the COMPILED packet. Attack: can ANY package-controlled input (`persona.package.json`, the manifest,
  `compile-request.json`, a persona/mode source, an example) put those keys into the compiled packet? Read the pinned compiler
  (`src/fubuki_os/compiler/compiler.py:32-134`) and the loader/validator for every key that flows to the output verbatim; build the hostile package
  and run `load_packet`. If a source can self-declare review → BLOCKING (a hollow readiness green minted by the governed party). If not, name the
  exact line where the compiler makes it impossible.
- **V3 — `Packet` is a forgeable frozen dataclass.** The tests build `Packet(b"{}", "a" * 64, True)` by hand; `project` (`J:33-57`) "verifies packet
  identity and review" — does it RECOMPUTE `governance_hash(packet.canonical)` and compare to `packet.hash`, and refuse `reviewed=False`? Attack: a
  Packet whose `hash` does not match its bytes; a Packet whose canonical bytes are not canonical (key order permuted) — does `project` re-canonicalize
  or trust? Reproduce; state whether `read_projection(path, expected_hash)`'s hash is bound to the PACKET hash or only to the document envelope
  (`J:68-83`, `J:133-152`): the invariant is `session.governance_hash == sha256(canonical_fubuki_packet)` — show where that equality is enforced
  end to end (compile → hash → projection document → read-back) or where it breaks.
- **V4 — the write boundary, behaviorally.** `write_projection` (`J:86-112`): existing regular file, existing symlink (to a regular file and dangling),
  a FIFO at the path, a path whose PARENT is a symlink, a path in a non-writable directory, a crash mid-write (simulate: patch `os.write` to write
  half then raise) — for each, the exact outcome and what is left on disk; then `read_projection` on the leftover. AF-AP-80 lens: every flag the
  lane lists must have a behavioral control that fails when the flag is dropped — run the driver's `projection-no-excl` and `projection-follow-symlink`
  rows and ADD any missing one (the parent-symlink case is not covered by O_NOFOLLOW; say whether it is in scope and why).
- **V5 — the read boundary.** `_read_regular` (`J:115-130`): a final symlink (ELOOP by name?), a FIFO (nonblocking → ENXIO or a hang?), a directory,
  a hardlink to a foreign file, a file modified between open and read (TOCTOU: the hash check must catch it), an oversized file. Exact refusals; the
  fd closed on every refusal (`/proc/self/fd` census before/after).
- **V6 — the join.** `bound_records` (`B:34-111`): duplicate `record_id` in the INPUT records; a decision naming an id absent from the input; the
  planted `payload`; object identity of `kept` (same objects, not copies); one audit event per decision with `reason` and `rule` non-empty; the sink
  failing mid-way (a sink whose second append raises) — fail-LOUD (the whole call raises, nothing partially "kept") or fail-soft? The contract logs
  each reason/rule: prove the events for DENIED records exist and carry the rule.
- **V7 — the audit sink.** `JsonlSink.append` (`E:59-88`): a symlink sink, a FIFO sink with no reader, a directory, a sink deleted between events,
  two writers appending concurrently (one `os.write` per event?), an event whose reason is whitespace, a non-serializable field. `Event` is frozen —
  can `__post_init__` be bypassed by `object.__setattr__`? (state, do not fix).
- **V8 — the hash contract.** `governance_hash` = `sha256(canonical_bytes).hexdigest()` unprefixed while the upstream's `hash_obj` returns
  `sha256:`-prefixed; the projection document's hash covers every byte (the lane's test). Independently recompute the governance hash of the fixture
  package from the pinned `canonical_json` (a 5-line script, no agent_factory import) and compare; permute the manifest key order and re-run;
  change ONE byte in each declared source and confirm the hash moves (the lane's sweep) — paste the five hashes.
- **V9 — the driver's validity (AF-AP-78) and its import identity.** Every row must compile and collect; INVALID gated; the driver claims importlib
  mode + a copied test import the MUTANT module — prove it: add a probe row whose mutant raises at import time and confirm the row reports KILLED
  through THAT error (not a pre-existing failure); then confirm a no-op mutant (a comment change) SURVIVES (the driver's control). Paste
  `EXPECTED/KILLED/SURVIVED/INVALID/CONTROL`.
- **V10 — the bare gate and the declared inputs.** From `git archive 78f400d` + nothing else, with ONLY `FUBUKI_OS_ROOT` and `FUBUKI_OTHER_ROOT`
  exported and PYTHONPATH unset: the five suites + `tests/test_fubuki_pin_sync.py` — paste the count (the coordinator read `34 passed`). Then unset
  `FUBUKI_OS_ROOT`: every fubuki-dependent test must FAIL (not skip) — paste `N failed, M passed, 0 skipped`. Then point `FUBUKI_OS_ROOT` at a DIRTY
  copy of the pin: the pin tests refuse by name and every dependent test fails.
- **V11 — the pyproject's blast radius.** `pytest --collect-only -q tests/ | tail -1` on the PIN vs on `git archive 9376760` (the tree before the
  pyproject) — the difference must be exactly the added test files' items; `tests/test_sentrux_review.py` count identical (the coordinator read
  `8 passed` both sides; the PC reads `4 passed, 4 skipped` — say why the skips differ by venue).
- **V12 — the report.** Re-verify the FILE IDENTITY table against the PIN; run `report_lint.py` with the map and `--min-refs 12`; grade every VERIFIED
  claim you can reproduce in ≤ 5 min; list every claim you could not reproduce as UNSURE, never as false.

**Output.** `tasks/briefs/stage3-governance-support/VERIFY-GOV1-report.md`: verdict line first (`MERGE-READY` / `NOT-READY: <blocking ids>`), then per
item `SOLID`/`UNSURE` with the command, the output and `file:line` (aliases `P=`packet.py, `J=`projection.py, `B=`bounds.py, `E=`events.py, `N=`pin.py,
`T*=`the test file — declare the map at the top); findings ranked by severity with the fix shape; a NOT-done list. Report lint with your map,
`--min-refs 15`, the bounded rule (three rounds, then paste and finish). No self-acceptance language; no edits to the landed bytes (a hostile row
you add goes into your report and your scratch, not the driver).
