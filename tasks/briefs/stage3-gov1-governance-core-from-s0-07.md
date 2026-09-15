# Lane GOV1 — Stage 3 governance core, the FIRST production increment (owner 2026-09-15 13:3xZ: "build the stuff we have proofs for so far … in parallel, as the proofs are being made"): the `agent_factory.governance` package built on the S0-07 proof — corrected lint exit, canonical compile + hash, the immutable Hermes projection, the BoundDecision-to-record join — plus the `src/` package skeleton and the seed of the Stage 1 audit envelope (build lane: PC Hermes `code-implementer`; sandbox fallback `code-implementer`)

PIN: `9376760`

**Why and what is proven.** S0-07 (`proofs/S0-07/`, MINTED 2026-09-07, an ATTESTED artifact you never touch) proved three corrections against
the pinned `fubuki-os` (`upstream.lock.yaml`: NerdHerderDani/fubuki-os @ `7375e56d6a5dc857bfd43ceccbc09bbc817d575a`, Apache-2.0, observed
0.1.0): (1) `persona_lint`'s exit code must be 1 when ANY violation exists even if a later finding is review-only (`_correct_lint_exit`,
checker:27-35; the ordered fixture `proofs/S0-07/fixtures/ordered-lint`), (2) `bounds.evaluate_record` returns a `BoundDecision` whose
`record_id` must be JOINED back to the source record — the decision carries no payload (checker:79-133), (3) `release.hashing.canonical_json`
+ `hash_obj` are stable across key order and runs (checker:135-172). Stage 3 of `docs/07_BUILD_PLAN.md` builds exactly on these; the contract
is `docs/03_INTEGRATION_CONTRACTS.md` §3 (lines 53-72): load reviewed sources → lint with the corrected exit → compile canonical JSON + hash →
project the IMMUTABLE runtime governance layer into Hermes → refuse readiness on invalid/unreviewed packets; the invariant
`session.governance_hash == sha256(canonical_fubuki_packet)`; bounded memory joins allowed `BoundDecision.record_id` back to records and logs
each reason/rule. Standing rules 8 (packets immutable, canonical, hash-pinned per session), 9 (a prompt instruction is not a control), 13
(pins by commit), 14 (tests for normal, failure AND the security boundary), 15 (no "runnable" claim without the gate) bind you. The pack
`tasks/briefs/stage3-governance-support/GOV1-pack.md` covers the S0-07 checker (START FROM IT). READ, in order: `docs/02_COMPONENT_AUDIT.md`
§Fubuki (lines 58-65), `docs/03_INTEGRATION_CONTRACTS.md` §3, `docs/01_ARCHITECTURE.md` (the Governance row), `proofs/S0-07/check_fubuki_corrections.py`
whole, then the pinned fubuki-os source itself (`src/fubuki_os/release/hashing.py`, `memory/bounds.py`, `memory/models.py`, the lint module,
the packet compiler — find and cite the functions you call by file:line at the pin).

**The pinned upstream on this venue.** Look for a checkout at `7375e56` under `/home/rocco/s0-01-pinned/fubuki-os` or `/home/rocco/nerdherderdani/fubuki-os`;
if absent, `git clone https://github.com/NerdHerderDani/fubuki-os.git` into your lane's scratch dir and `git checkout 7375e56d6a5dc857bfd43ceccbc09bbc817d575a`
(verify `git rev-parse HEAD` equals the lock's commit; paste it). Export `FUBUKI_OS_ROOT=<that path>` for your tests. The production code
NEVER hard-codes a path: the root is an explicit parameter resolved ONCE by the caller (the #2 tactic: `os.environ` is not a config channel
inside the library; a thin CLI/test shim may read `FUBUKI_OS_ROOT` and thread it).

**Boundary (new files only, plus the two listed edits).** `pyproject.toml` (NEW: `[project] name = "agent-factory"`, python ≥ 3.11, a
`src/` layout with `[tool.setuptools.packages.find] where = ["src"]`, and `[tool.pytest.ini_options] pythonpath = ["src"]` — NO `testpaths`,
NO other pytest option: the existing suites must run exactly as before; prove it by running one existing file, `tests/test_sentrux_review.py`,
before and after with the same count), `src/agent_factory/__init__.py`, `src/agent_factory/governance/{__init__,packet,projection,bounds,pin}.py`,
`src/agent_factory/audit/{__init__,events}.py` (the SEED of Stage 1's envelope — minimal), `tests/test_governance_packet.py`,
`tests/test_governance_projection.py`, `tests/test_governance_bounds.py`, `tests/test_governance_pin.py`, `tests/test_audit_events.py`,
`tests/fixtures/governance/` (your fixture sources — derived from S0-07's fixtures, never pointing at them by path), the driver
`tasks/briefs/stage3-governance-support/mutants.sh`, the report `tasks/briefs/stage3-governance-support/GOV1-report.md`. EDITS: one line in
`scripts/setup.sh` and one in `harness-ports/bin/pc-setup.sh` that `pip install -e .` the package into each venue's venv (idempotent; guarded
by the pyproject's presence) — read both scripts first and match their style. Everything else read-only; `proofs/` never.

## Items (build in order; every item = code + deterministic LLM-free tests (normal + failure + the security boundary) + a pasted line)
1. **`pin.py` — the upstream is verified before it is used.** `verify_pinned_fubuki(root, lock_path) -> PinnedFubuki` reads
   `upstream.lock.yaml`'s `fubuki-os.commit`, runs `git -C root rev-parse HEAD` and refuses (a named `GovernanceError`, exit-style reason
   string) on a mismatch, a dirty tree (`git status --porcelain` non-empty), or a missing `src/fubuki_os`; on success it returns the root and
   the commit and INSERTS the pinned `src/` on `sys.path` exactly once (the S0-07 checker's shape, `_add_fubuki`). Tests: the pinned checkout
   passes; a checkout at another commit refuses by name; a dirty checkout refuses; a directory without `src/fubuki_os` refuses.
2. **`packet.py` — lint, compile, hash.** `lint_sources(root) -> LintResult(findings, exit_code)` calling the pinned persona lint with the
   CORRECTED exit semantics (port `_correct_lint_exit` from the checker — cite it); `compile_canonical(sources_root) -> bytes` (the packet built
   by fubuki-os's own compiler, then `canonical_json`); `governance_hash(canonical_bytes) -> str` = `sha256` hex (state whether fubuki's
   `hash_obj` is that exact function; if it is not sha256 over the canonical bytes, use `hashlib.sha256` and SAY so — the invariant names
   sha256); `load_packet(root) -> Packet` = lint (refuse on exit 1) → compile → hash, returning a frozen dataclass with `canonical: bytes`,
   `hash: str`, `reviewed: bool` (from the packet's own review/status field — find it in the fubuki model and cite it; if no such field
   exists, the packet is NOT reviewed and `load_packet` refuses — say so). Tests: the ordered-lint fixture → exit 1 (never 2); a clean fixture →
   0; a review-only fixture → 2; the hash is identical across two loads and across a key-order-permuted copy of the same sources; a one-byte
   change in any source changes the hash (a sweep over every file in the fixture — enumerate them); an unreviewed packet refuses readiness by
   name.
3. **`projection.py` — the immutable runtime layer for Hermes.** `project(packet) -> GovernanceProjection` (frozen dataclass; nested
   mappings wrapped in `MappingProxyType`; `governance_hash` inside it; the persona/bounds text Hermes will receive as its reviewed bootstrap
   layer — the shape `docs/03` §1 line 17 names (`BUZZ_ACP_SYSTEM_PROMPT_FILE`), state exactly which packet fields are projected and which are
   not); `write_projection(projection, path)` writes atomically (`O_CREAT|O_EXCL|O_NOFOLLOW|O_NONBLOCK` then fdopen — the S0-01 write primitive's
   shape, AF-AP-70; refuse an existing file, a symlink, a FIFO); `read_projection(path, expected_hash)` refuses on a hash mismatch or a
   tampered byte. Tests: mutation of the projection raises; the file round-trips; a tampered file refuses by name; a symlink/FIFO at the path
   refuses before any write (rig the FIFO with a bounded timeout); the hash inside equals `governance_hash` of the packet it came from.
4. **`bounds.py` — the join.** `bound_records(records, packet) -> BoundResult`: calls the pinned `evaluate_record` per source record (or
   `evaluate_records` if it exists at the pin — cite), keeps ONLY records whose `record_id` is in the allowed decisions, joined by id to the
   SOURCE record objects, never reading a payload from a decision; returns the kept records, the denied ids with each decision's reason/rule,
   and EMITS one audit event per decision (item 5). Tests: the join returns the source objects (identity, not copies); a decision naming an
   id absent from the sources is refused by name (never fabricated); a denied record is absent from the result and present in the denials with
   its reason; a mutant that reads a payload from the decision is killed (a decision object with a planted `payload` attribute that must never
   appear in the output).
5. **`audit/events.py` — the envelope seed (Stage 1's "common audit envelope", minimal).** `Event` (frozen: `ts`, `kind`, `reason`,
   `correlation_id`, `governance_hash`, `fields` mapping) and `JsonlSink(path)` appending one JSON line per event (atomic append, the same open
   discipline); `reason` is REQUIRED and non-empty (a silent decision path is a defect — the telemetry rule). Tests: an event without a reason
   is refused; the line round-trips; the sink refuses a symlinked path.
6. **The driver** (`mutants.sh`, AF-AP-78 obeyed: `py_compile` + collect-only before the verdict, `INVALID` gated, kills as pasted assertion
   lines): rows — lint exit 2 after a violation; hash over a subset of fields; hash not over canonical bytes (key order leaks); the join reading
   the decision payload; the projection mutable (a plain dict); `write_projection` without `O_EXCL`; `read_projection` skipping the hash check;
   an event without `reason` accepted; the pin check skipping the commit compare. ≥ 2 rows of your own. Summary `EXPECTED=… KILLED=… SURVIVED=0
   INVALID=0 CONTROL=…`.
7. **Gates.** `python -m pytest tests/test_governance_*.py tests/test_audit_events.py -q -p no:cacheprovider --basetemp=<scratch>` TWICE
   (paste both), `bash scripts/pc_suite.sh set-id -- <those files>` beside each count; pyflakes rc 0 over `src/` and the new tests; the
   before/after run of `tests/test_sentrux_review.py` (same count); `python -c "import agent_factory.governance"` from the repo root under
   the pytest pythonpath AND after `pip install -e .` into a THROWAWAY venv you create in scratch (never the shared venv). Hermes's `terminal`
   tool caps a call at 420 s: everything here is seconds.
8. **Report** at `tasks/briefs/stage3-governance-support/GOV1-report.md`: FILE IDENTITY (every new file's sha + lines), the fubuki-os functions
   you call by file:line at the pin, per item the pasted line, the driver output, DISCREPANCIES (anything in this brief or the docs that the
   pinned library contradicts — say it, do not paper over it), NOT-done (explicitly: the projection is NOT yet wired into a Hermes session —
   that needs the spine (S0-01/S0-03), so `session.governance_hash` binding is a later increment; the audit sink is a file, not OpenObserve).
   Lint LAST: `python3 scripts/report_lint.py --map C=proofs/S0-07/check_fubuki_corrections.py --map P=src/agent_factory/governance/packet.py
   --map J=src/agent_factory/governance/projection.py --map B=src/agent_factory/governance/bounds.py --min-refs 12 <report>`, at most THREE
   rounds, then paste and finish.
9. **Discipline.** No hard-coded paths in `src/`; no `os.environ` reads inside the library; no network except the one pinned clone; kill by pid;
   scratch copies only; no git writes; never touch `proofs/`, the model unit, or other lanes' trees.
