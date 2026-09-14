# P5c report — S0-01 PC capture tools round 3

BUILD STATUS: BLOCKED. No implementation was made after the resolved marker contradiction exposed a second, independent contradiction in item 1.

## NOT DONE — blocking contradiction after AMENDMENT 1

AMENDMENT 1 correctly distinguishes `manifest-pre.done` and `manifest-post.done` as zero-byte `empty-marker` files. It nevertheless says every other required artifact has a kind for which empty content is invalid and requires a 25/25 invalid-content sweep: 23 files emptied and the two markers given one byte.

The immutable v2.2 corpus falsifies that new premise. `process-scan-teardown.txt` is a required v2.2 regular file and is zero bytes in every positive v2.2 leg. `process-scan-after.txt` is also a required zero-byte regular file on the shutdown leg. Those are not `.done` completion markers: they are valid v2.2 process-scan artifacts produced before the v2.4 header contract. The pinned detector itself documents the v2.2 empty-after-scan case at `P:312-315`.

A fresh copy of the real `run-1` corpus demonstrated the exact no-op. Its `process-scan-teardown.txt` was zero bytes before and after the requested empty mutation (`byte_identical=True`). The current builder exited `rc=0`, wrote `capture.json`, and printed `run-1: 9 raw files, 11 timeline entries`. Any P5c implementation that accepts the valid v2.2 capture must accept this byte-identical mutation. Rejecting it would make the declared real corpus invalid; accepting it cannot satisfy the required 23/25 invalid-empty assertion. I did not invent a metadata distinction or change the producer/corpus contract.

The underlying producer history confirms the shape is real, not accidental. The v2.4 scan header arrived in `77f46a2`; its parent `pc_post.sh` produced v2.3 headers but its `keep` body could be empty. The current corpus still carries v2.2 files, so a strict v2.4 grammar cannot be imposed retroactively without breaking valid captured evidence.

## Blocker (resolved by AMENDMENT 1)

P5c originally stopped because the brief required every required artifact made empty to fail, while `manifest-pre.done` and `manifest-post.done` are intentional zero-byte completion markers. `P:232` and `P:239` classify them as required; `M:69-71` gzip-compresses the manifest, writes its digest, then `touch`es each marker. The immutable `run-1` corpus carries both at zero bytes. Emptying either marker is byte-identical, so content validation cannot accept the valid marker and reject the same bytes. AMENDMENT 1 resolved that contradiction with `empty-marker` constraints and one-byte mutations for the two markers.

## Verified evidence

| claim | evidence |
|---|---|
| Required set | `pins.required_files("v2.2")` returned 25 names. |
| Resolved marker exception | `manifest-pre.done` and `manifest-post.done` are zero-byte required completion markers, as AMENDMENT 1 states. |
| New counterexample | `process-scan-teardown.txt` is required and zero bytes on `run-1`, `cancel`, `shutdown`, and `two-users`; `process-scan-after.txt` is also zero bytes on `shutdown`. |
| Exact no-op | Copying real `run-1`, emptying `process-scan-teardown.txt`, and running `B` returned `rc=0`; `capture.json` existed. |
| Pin semantics | `P:269-272` and `P:312-315` state that v2.2 scan files may be empty and have no header; those references were mechanically checked against the pinned source. |
| Producer history | Parent of `77f46a2` shows v2.3 scan output whose body can be empty; v2.4 headering was introduced at `77f46a2`. |
| Current builder defect | Before this lane made no source changes, the prior 25-file empty sweep produced 22 rc-0 records, raw JSON tracebacks for empty JSON inputs, and one named timeline failure. |
| Strict-header defect | Prior standalone probes showed duplicate header, body header, trailing field, and CRLF were accepted by `pins.corpus_version()`. |
| Idiom-table defect | Removing one declared `Path(framedir, ...)` row yielded `10 passed, 87 deselected in 0.18s`; no cardinality guard detected it. |
| S0-02 seam | D-022 and `proofs/S0-02/tools/pc/run_s0_02_legs.sh:45-65` specify an S0-02-only `RUST_LOG=debug` extension; no S0-02 file was edited. |

## Disposition needed

A coordinator/owner decision is required before P5c can continue. Real options are:

1. Amend item 1 again: model `process-scan-after.txt` and `process-scan-teardown.txt` as version-aware artifacts, permitting zero bytes in v2.2 where the existing producer and corpus do, and define valid/invalid mutations per `(version, filename)`.
2. Change the producer/capture contract so every required v2.2 scan artifact is non-empty, then recapture the corpus and update every consumer. This is cross-lane work and changes immutable evidence.
3. Define a new capture-contract version that requires non-empty scan headers, preserve v2.2 compatibility explicitly, and make the content table version-specific. The checker and corpus-migration work are outside this lane.

Option 1 is the minimum compatible design but changes the amendment's blanket `23 non-marker files emptied` claim. Options 2 and 3 require broader approval. I will not select one silently.

## Items not started

Items 2–10 remain intentionally unimplemented because the original brief requires item order and item 1 remains contradictory. This includes the strict-header implementation, idiom-table cardinality change, S0-02 environment extension, P5b historical-report status line, mutations, AP sweep, lane gates, and report lint for an implementation change.

F5 remains A5l work: the checker owns a different pinned-process/version consumer. The real recapture and VB-F12/VB-F13/VB-F14 remain not done. No live buzz-acp, Hermes, tee, relay, model, or owner service was started.

## Evidence tiers

- Verified: current pin and producer reads; v2.2 required-set enumeration; corpus file-size measurements; scratch copy/no-op probe; historical producer read; previous marker blocker evidence; static S0-02 runner and decision read.
- Inferred: a deterministic content-only validator cannot distinguish valid and re-emptied byte-identical scan inputs at the same path.
- Assumed: none.

## Self-attack

1. The empty teardown scan might be optional in v2.2. Ruled out by `pins.required_files("v2.2")` and direct corpus enumeration.
2. The empty scans might be corrupt evidence rather than producer-supported. Ruled out by the pin's explicit v2.2 empty-scan contract and the pre-v2.4 producer's ability to write an empty `keep` body.
3. A timestamp or filesystem metadata might distinguish the mutation. Rejected: it is not content validation, is not pinned evidence semantics, and changes during copy/collection.

## Hygiene

No production or test source file remains modified by this lane. The only in-tree output is this report. The required incremental draft path was absent when checked; no draft file was created because the blocking evidence must remain in the canonical report. No `git add`, commit, push, reset, checkout, stash, credential read, or owner-service action occurred. Scratch probes copied the real corpus under this lane's scratch directory and did not write to the golden source.

Implementation file identity: none. No implementation gate result exists and no gate outcome is claimed. The amendment's 25/25 invalid-content denominator remains unimplementable as written: beyond the two resolved markers, valid v2.2 required scan artifacts are zero bytes. A hollow-green rate for a nonexistent content gate is not fabricated.

Mechanical self-lint on this final report at `3614dc9`:

    report_lint: 7 refs — OK 5, NEAR 0, MISS 0, UNCHECKABLE 2, UNRESOLVED 0 (at 3614dc9)

The two UNCHECKABLE references are the two adjacent `P:` ranges in the pin-semantics table row; the linter reports no claim token on that row. Both were manually re-read against the pinned source. No reference was a MISS.
