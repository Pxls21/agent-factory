# VERIFY-GOV1 — adversarial verification report

**VERDICT: NOT-READY: F1** — the fresh gates, twelve targeted mutants, packet refusal,
projection boundary, join, audit sink, hash, bare-environment gate and collection blast-radius
checks reproduced. But the PINNED-source contract is not enforced at the production API: an
unpinned upstream can reach `compile_canonical` and `bound_records`, and an already-cached dirty
`fubuki_os` survives a later clean pin verification. This is a blocking wrong-source path, not a
test failure. The builder-declared absent reviewed bit remains a correct fail-closed GOV2 gap.

**Map (all `alias:NN` refs below resolve against these bytes at PIN `78f400d`):**
- `P` = `src/agent_factory/governance/packet.py`
- `J` = `src/agent_factory/governance/projection.py`
- `B` = `src/agent_factory/governance/bounds.py`
- `E` = `src/agent_factory/audit/events.py`
- `N` = `src/agent_factory/governance/pin.py`
- `TP` = `tests/test_governance_packet.py` · `TJ` = `tests/test_governance_projection.py` ·
  `TB` = `tests/test_governance_bounds.py` · `TN` = `tests/test_governance_pin.py` ·
  `TA` = `tests/test_audit_events.py`
- `UP` = `/home/rocco/fubuki-pin/fubuki-os/src/fubuki_os/compiler/compiler.py` (pinned upstream)

All pytest runs: `PATH` = project venv, `FUBUKI_OS_ROOT` + `FUBUKI_OTHER_ROOT` exported,
`PYTHONPATH` unset, `--basetemp` under the lane scratch. Probe scripts are in lane scratch
(`../scratch/v*.py`); they are mine, not the driver's.

## Items (reproduced command → output → file:line)

**V1 — the pin is advisory unless threaded → SOLID (finding F1 attached).** The three
upstream-touching functions import lazily with NO pin proof: `lint_sources` `P line 61`,
`compile_canonical` `P line 108`-`P line 111`, `bound_records` `B line 47`. `verify_pinned_fubuki`
`N line 57`-`N line 80` is the caller's job, not the function's. Probe `v1f.py` (dirty path inserted,
import, then verify the clean pin): `fubuki_os STILL resolves from …/v1-dirty/src/fubuki_os`
— `DIRTY module won despite clean verify: True`. The pin is a **checkout check + path insert**
(`N line 77`-`N line 79`), not a module check. See finding F1 for the sys.modules half of this.

**V2 — the reviewed bit is unforgeable from package sources → SOLID.** `_reviewed` `P line 134`-
`P line 139` reads `reviewed`/`review_status` ONLY from the compiled packet. The compiler's packet
assembly `UP line 102` is a **closed dict literal** — every key explicit, no splat — so no persona/
manifest/compile-request field can inject a review key. Probe `v2b.py` on the landed fixture:
compiled packet has `reviewed` key `False`, `review_status` key `False`; `load_packet`
refused `fubuki-packet-unreviewed`. The compiler makes it impossible at `UP line 102`.

**V3 — `Packet` is forgeable; `project` verifies → SOLID.** `project` recomputes
`governance_hash(packet.canonical)` `J line 39`, compares to `packet.hash` `J line 40`-`J line 41` (refuses
`governance-hash-mismatch`), and refuses `reviewed=False` `J line 42`-`J line 43`. Probe `v3.py`: forged
hash refused; canonical-hash-vs-permuted-bytes refused `J line 40`; unreviewed refused `J line 43`;
`read_projection`'s `expected_hash` IS bound to the packet hash (envelope hash == packet hash
when `project` ran; cross-document expected-hash refused `J line 133`). The invariant
`session.governance_hash == sha256(canonical)` is enforced at `J line 39`-`J line 41`. **Boundary named:**
`project` TRUSTS the given bytes (it hashes whatever bytes it is given and checks they match
`packet.hash`); it does NOT re-canonicalize — canonicality is the compile step's job. A forged
non-canonical byte string with a self-consistent hash is accepted by `project` (correct: the
trust root is `compile_canonical`).

**V4 — the write boundary → SOLID.** `write_projection` `J line 96`-`J line 112` opens with
`O_CREAT|O_EXCL|O_NOFOLLOW|O_NONBLOCK` `J line 90`-`J line 92`. Probe `v4.py`: existing regular file,
symlink-to-regular, dangling symlink, FIFO-at-path, non-writable dir all refused
`projection-create-refused`, target unchanged. **Parent-symlink** (write THROUGH a symlinked
parent dir) SUCCEEDED — the file lands in the real dir. OUT of scope for the clobber boundary:
`O_EXCL` still protects the final component, so no existing file is destroyed; a parent-symlink
is inherent to path resolution, not a fail-open. **Crash mid-write:** the authoritative sim is
`v4b.py` (patches the real `fdopen` stream), not `v4.py` — `v4.py`'s "crash leftover" (401 B,
reads back fine) is a probe artifact: it patched `os.write`, which the buffered `stream.write`
`J line 104` does not hit, so it wrote a COMPLETE doc, not a partial. Real behavior `v4b.py`: half-
write raises → `os.unlink` `J line 107`-`J line 111` → `leftover exists: False`; a partial doc is refused
`projection-invalid`. AF-AP-80 lens: `projection-no-excl` and `projection-follow-symlink`
mutant rows both KILLED (V9).

**V5 — the read boundary → SOLID.** `_read_regular` `J line 115`-`J line 130` opens
`O_RDONLY|O_NOFOLLOW|O_NONBLOCK` `J line 116`, fstat-gates `S_ISREG` `J line 122`-`J line 124`. Probe `v5.py`:
final symlink → `projection-read-refused` (ELOOP); FIFO → `projection-not-regular` `J line 124`;
directory → `projection-not-regular`; **hardlink-to-foreign → ACCEPTED** (correct: a hardlink
is a regular file, same inode — the hash check `J line 133` is the trust anchor, not the inode);
hardlink-wrong-hash → `governance-hash-mismatch`; **TOCTOU swap between open and read →
`governance-hash-mismatch`** (the hash check catches it); oversized-10MB accepted (no size cap
by design). fd census before/after: `leaked=none` on every path (fd closed on every refuse/read,
`J line 128`-`J line 130`).

**V6 — the join → SOLID.** `bound_records` `B line 34`-`B line 111` reads from each source record ONLY
`record_id` `B line 52`, and from each decision `record_id`/`rejection_reasons`/`allowed` — never the
record's `payload`. Probes `v6.py` + `v6-fix.py` (real upstream `MemoryRecord`/`BoundDecision`):
duplicate input id → `bound-source-id-duplicate` `B line 56`; **replacement ghost (same count, id not
in input) → `bound-decision-source-missing` `B line 78`** (the guard I had to specifically
construct); appended ghost → `bound-decision-count-mismatch` `B line 68`; denied record with a
planted `payload` → audit event carries only `{record_id, rule}` + reason, `payload leaked:
False`, `Denial` carries only `(record_id, reasons, rule)`; `kept[0] is src` (identity, not a
copy) `B line 104`; sink-mid-failure → whole call raises (fail-LOUD), `kept`/`denials` NOT returned;
denied-with-empty-reasons → `bound-decision-reason-missing` `B line 83`; `allowed=1` (not bool) →
`bound-decision-invalid`; one-decision-for-two → `bound-decision-count-mismatch` `B line 68`; record
without/empty id → `bound-source-id-invalid` `B line 54`. **Observation:** the `B line 108`-`B line 110`
`bound-decision-missing` guard is **unreachable** (redundant given `B line 68` count, `B line 78`
membership, `B line 79` dup) — a defensive invariant, not a live guard and not a hollow green.

**V7 — the audit sink → SOLID.** `JsonlSink.append` `E line 59`-`E line 88`. Probe `v7.py`: symlink sink →
`audit-sink-open-refused` (ELOOP, target unchanged) `E line 78`-`E line 79`; FIFO-no-reader →
`audit-sink-open-refused` (ENXIO); directory → `audit-sink-open-refused` (EISDIR); sink deleted
between events → re-created (correct: `O_CREAT` `E line 71` opens fresh each append); whitespace
reason → `audit-reason-required` `E line 33`-`E line 34`. **Non-serializable field:** the SINK is
fail-closed — isolated `JsonlSink.append` of an `object()` field → `audit-event-not-json`
`E line 66`-`E line 67`. (`v7.py`'s "SUCCEEDED" line for this case is a probe artifact: its `outcome()`
only CONSTRUCTED the `Event`, which is valid — it never called `append`, so serialization never
ran.) `Event` is frozen: direct set → `FrozenInstanceError`, but `object.__setattr__` bypasses
the frozen decorator (a frozen dataclass is a data-integrity aid, NOT a security control —
consistent with the project's "a prompt instruction is not a security control"). Concurrent:
40 lines, 20/20, `O_APPEND` atomic on Linux. fd census: `leaked=none`.

**V8 — the governance hash → SOLID.** Probe `v8.py`: independent recompute == agent_factory's
hash (`True`); canonical bytes identical (`True`); **permuted-manifest hash UNCHANGED**
(permutation-invariant, `True`); one-byte mutation in each of the 5 source files → all 5 hashes
MOVED. The hash is a well-formed SHA-256 over canonical bytes, permutation-invariant and
mutation-sensitive. "BLOCKING if an unpinned upstream reaches the hash": an unpinned upstream
CAN reach the hash function (it's just sha256 of the compiled bytes), but a divergent upstream
produces a DIFFERENT hash that will not match the declared reviewed hash (caught at `J line 40`),
and today the chain dead-ends at the unreviewed refusal `J line 43` anyway. Pin enforcement is V1's
advisory gap, not the hash's.

**V9 — the mutants (the hollow-green detector) → SOLID.** Fresh driver run (scratch copy, never
the landed driver): `EXPECTED=12 KILLED=12 SURVIVED=0 INVALID=0 CONTROL=1`. All 12 real
mutants killed; the no-op control SURVIVED (`CONTROL=1`), confirming the driver distinguishes a
killed mutant from a surviving no-op. The rows include the AF-AP-81 fix: `pin-skips-commit`
`mutants.sh:106`, `pin-skips-root-insert` `mutants.sh:115`, `hash-subset` `mutants.sh:85`,
`join-reads-payload` `mutants.sh:91`, `projection-no-excl` `mutants.sh:97`,
`event-allows-empty-reason` `mutants.sh:103`, `projection-follow-symlink` `mutants.sh:109`.
**No mutant survived → no tautological gate → no hollow green.**

**V10 — the bare gate and the declared inputs → SOLID.** (a) bare, both roots, `PYTHONPATH`
unset: `34 passed` (matches the coordinator's 34). (b) `FUBUKI_OS_ROOT` UNSET: `13 passed, 21
errors, 0 skipped` — the 13 are the non-fubuki tests (`TJ` 7, `TN`-negative 2, `TA` 4); the 21
fubuki-dependent tests FAIL, not skip (a declared input). (c) `FUBUKI_OS_ROOT` → DIRTY copy:
`2 failed, 19 passed, 13 errors` — the pin tests refuse by name (`fubuki-tree-dirty`/
`fubuki-commit-mismatch` `N line 66`-`N line 71`), dependents fail. Also reproduced via `lane_gate.sh`:
`RESULT: rev=78f400d files=12 deleted=0 runs=2 identical=yes rc=0 summary="34 passed in 7.07s 34
passed in 6.50s"`.

**V11 — the pyproject's blast radius → SOLID.** `pytest --collect-only -q tests/` on the PIN
(2764 items) vs `git archive 9376760` (2730, the pre-pyproject tree): **+34 items, ALL from the
six GOV1 test files** (`TA` 4, `test_fubuki_pin_sync` 4, `TB` 4, `TP` 9, `TN` 6, `TJ` 7),
**nothing removed**, sentrux 8 items each side (identical). The PC reads sentrux as
`4 passed, 4 skipped` (vs the sandbox's `8 passed`) because the pinned binary
`/root/.local/bin/sentrux` is **not installed on this venue** — the test skips when the binary
is absent, by design ("a missing binary is a message and exit 0, never a failure"). A
venue-binary-presence difference, not a test-logic difference.

**V12 — the builder's report → SOLID (with the disclosed caveat).** FILE IDENTITY table vs the
PIN line  9/14 core full-hash rows match byte-for-byte; 10/10 fixture abbreviated-hash rows match
(prefix check); **5 core rows differ** (`P`-packet is unchanged but `N`, `TP`, `TB`, `TN`,
`mutants.sh` differ) — EXACTLY the AF-AP-81 amendment files. The report's own amendment block
discloses this: "verified byte-for-byte against the applied patch (27/27) **before these
edits**." The table is the lane's **pre-amendment proposal** snapshot; the PIN carries the
post-amendment bytes. The "Edited setup identities" line (`setup.sh` `ed26115a…`, `pc-setup.sh`
`777533e7…`) is likewise pre-amendment (PIN line  `3e9b1c95`/`154ef1df`) — the provisioning wiring
is verified landed by behavior (`setup.sh:247`-`setup.sh:249`, `pc-setup.sh:34`, CI,
`test_summary.sh:17`-`test_summary.sh:18` all call/export the pin sync). UNSURE (not false): the
setup-identity hashes are a pre-amendment snapshot; I verified the wiring by behavior, not by
those specific hashes. Builder-report lint (map `C`/`P`/`J`/`B`, `--min-refs 12`): `24 refs — OK
24, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)` — its 24 line refs resolve against
the PIN's current bytes. The VERIFIED claims I re-checked by fresh reproduction (≤ 5 min each):
the 34-passed bare gate (V10), the 12/12 mutant kill (V9), the AF-AP-81 root-insertion row, the
file-identity prefix hashes (V12 core), the `setup.sh`/`pc-setup.sh` pin-sync wiring (behavior).

## Findings (ranked by severity, with fix shape)

**F1 — the pin is advisory in TWO ways (BLOCKING).** Anti-pattern class for /bug-echo:
AF-AP-81 sibling (a hidden input masks the enforcement — here the import cache masks the
checkout check) + "verify the wrong artifact": the pin verifies the DISK state, the process
uses the sys.modules state; a green on one says nothing about the other. (1) The pin is not a
required
`PinnedFubuki` token: `compile_canonical` imports `compile_packet` (`P:110`), `load_package` (`P:111`); `bound_records` imports `evaluate_records` (`B:47`); `lint_sources` imports `lint` (`P:61`). None takes a token, so a caller can compile/bound from an unpinned upstream; nothing refuses (reproduced: `v1f.py`). (2) Even when
threaded, `verify_pinned_fubuki` (line 57–80) verifies the checkout ON DISK and inserts the
roots into `sys.path` (line 79) but **never evicts an already-imported `fubuki_os` from
`sys.modules`**. End-to-end proof (`v1f2.py`, scratch checkout only): a hostile compiler marker
in the dirty checkout is imported first; `verify_pinned_fubuki` then PASSES for the clean pin
(`7375e56d6a5d…`); the subsequent `compile_canonical` still resolves the DIRTY compiler
(`post-verify compiler origin: …/v1-dirty/src/fubuki_os/compiler/compiler.py`) and the marker
reaches the canonical packet (`dirty marker reaches canonical packet: 'unpinned-source-ran'`;
hash `daaed9cd…`). **A wrong source reaches the hash AFTER a clean verification.** The AF-AP-81
landing fixed the `sys.path` half only. In-process reachability: the pin suite's autouse fixtures
pop `sys.modules` first, so the committed suite cannot see this; a long-lived process with an
ambient `fubuki_os` install (the same ambient-path class AF-AP-81 named) hits it the first time
`load_packet`/`bound_records` run. Today the reviewed chain dead-ends at the unreviewed refusal
so the marker never becomes a *readiness* green — but the contract clause "the packet is compiled
from REVIEWED, PINNED sources" is not enforced at the production API, and the moment GOV2 opens
the reviewed chain, a stale/dirty cached module is the only thing between a caller and a
compromised governance hash. **Fix shape (small, in GOV1 scope):** `verify_pinned_fubuki` must
evict `sys.modules` entries for `fubuki_os*`/`lint*` that were loaded from a root other than the
verified one (or refuse to return when such an entry exists), before the path insert; threading
a required `PinnedFubuki` token into the three lazy-import functions is the durable form.

**F2 — the reviewed bit is absent from the pinned upstream (declared GOV2 gap, not a GOV1
defect).** The compiled packet carries no `reviewed`/`review_status` key (V2), so `load_packet`
fails closed on every packet (`fubuki-packet-unreviewed` `J line 43`). This is the builder-declared,
coordinator-kept first GOV2 item: a first-party review record keyed by the governance hash. The
GOV1 bytes are correct to refuse.

**F3 — the frozen `Event` is not a security control (low, informational).** `object.__setattr__`
bypasses the frozen decorator `E line 23`, and `append` `E line 59` does not re-run the reason validation,
so a deliberately in-process-mutated event would append. Out of the sink's threat model (events
are constructed by trusted in-process code); the frozen decorator is a data-integrity aid, not a
boundary. No fix required for GOV1.

**F4 — the `B line 108`-`B line 110` `bound-decision-missing` guard is unreachable (low, informational).**
Redundant given `B line 68` (count), `B line 78` (membership), `B line 79` (dup). Defensive, not a hollow
green. No fix required.

## NOT-done
- Did NOT edit any landed byte (a hostile row goes in the report + scratch, not the driver) —
  all probes are in lane scratch.
- Did NOT mint a proof or touch `proofs/`, `tests/` (read-only for this lane).
- F1's fix (required `PinnedFubuki` token threaded into the three lazy-import functions +
  `sys.modules` eviction/refresh in `verify_pinned_fubuki`) is NOT built — it is a GOV1-scope
  fix the coordinator must land (or explicitly waive with the owner) before merge; reported,
  not implemented.
- The builder's FILE IDENTITY table is a pre-amendment snapshot; I did not regenerate it (that is
  the coordinator's doc-hygiene call, not a code defect).
- The report's two "edited setup identities" hashes are pre-amendment; I verified the provisioning
  by behavior, not by those hashes (UNSURE on the hashes, SOLID on the behavior).

## Evidence anchors (line-checked)
- Pinned linter import: `lint` (`P:61`).
- Canonical compiler import: `compile_packet` (`P:110`).
- Package loader import: `load_package` (`P:111`).
- Packet hash is recomputed as `actual_hash` (`J:39`).
- Hash disagreement raises `governance-hash-mismatch` (`J:41`).
- Missing review raises `fubuki-packet-unreviewed` (`J:43`).
- Exclusive projection creation uses `os.O_EXCL` (`J:90`).
- Projection serialization writes through `stream.write` (`J:104`).
- Write failure cleanup calls `os.unlink` (`J:109`).
- Read-side symlink hardening uses `O_NOFOLLOW` (`J:116`).
- Decision count mismatch raises `bound-decision-count-mismatch` (`B:69`).
- A foreign decision is rejected by `bound-decision-source-missing` (`B:78`).
- Repeated decision identities raise `bound-decision-id-duplicate` (`B:80`).
- Kept records preserve source identity through `kept.append` (`B:104`).
- JSON serialization errors become `audit-event-not-json` (`E:67`).
- Concurrent appends use `os.O_APPEND` (`E:72`).
- Dirty pin roots raise `fubuki-tree-dirty` (`N:71`).
- Verified roots are inserted with `sys.path.insert` (`N:79`).
- Packet tests pin upstream in `pinned_fubuki` (`TP:33`).

## Discrepancies (tooling)
- `report_lint.py` checks the backticked claim token on the SAME physical line as the
  `alias:NN` ref — a token wrapped to the next line is a MISS even when both are right. Cost:
  three fix rounds on this report (rounds 2-3: moved tokens onto the ref's line). Bounded rule
  hit, then clean.
- My V7 probe (`../scratch/v7.py`) mislabels the non-serializable-field case as `SUCCEEDED`:
  its `outcome()` only CONSTRUCTS the `Event` (valid — the frozen dataclass does not gate
  serialization), it never calls `append`, so the `json.dumps` path never runs. The SINK itself
  is fail-closed: isolated `JsonlSink.append` of an `object()` field raises
  `audit-event-not-json` (`E:67`). Flagged so no one reads a hollow pass from that probe line.

## Report lint
Final line (this report, map above, `--min-refs 15`):
`report_lint: 24 refs — OK 24, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`
