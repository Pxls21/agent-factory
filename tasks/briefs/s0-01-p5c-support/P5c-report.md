# P5c report — S0-01 PC capture tools round 3

BUILD STATUS: BLOCKED. No implementation was made.

## NOT DONE — blocking contradiction at item 1

P5c item 1 requires every required artifact made empty to fail with a named `<leg>: <name> is empty` reason, specifically `25/25` for the v2.2 real-corpus sweep. The pinned v2.2 required set includes two intentional zero-byte completion markers: `P:232` marks `manifest-pre.done` as `required`, and `P:239` marks `manifest-post.done` as `required`.

Those markers are deliberately empty at production: `M:69-71` gzip-compresses the manifest, writes its digest, then `touch`es the `.done` marker. The copied real `run-1` corpus has both markers at zero bytes. Re-applying the proposed empty mutation (`: > marker`) left each file byte-identical under `cmp`.

A content validator cannot accept the valid zero-byte marker and reject the same zero-byte path as an empty artifact. Metadata-based detection would not be content validation, has no pinned stable value, and would manufacture a hollow green. I did not add such a workaround.

The current builder defect itself was reproduced before any edit. `B:69-85` only gates required files by presence and has a separate `timeline.jsonl` empty check. On a fresh copied real v2.2 `run-1`, emptying each of its 25 required files produced 22 rc-0 records; empty `env.json` and `runtime-identity.json` emitted raw `JSONDecodeError` tracebacks; only empty `timeline.jsonl` produced a named failure. This confirms the reported class, but it does not make the pinned 25/25 remedy implementable without changing the marker contract.

## Verified evidence

| claim | evidence |
|---|---|
| Required-set contradiction | `pins.required_files("v2.2")` returned 25 names including both `.done` markers; the table classifies both as `required` at `P:232` and `P:239`. |
| Producer semantics | `pc_manifest.sh` uses `touch` after completing gzip and digest work at `M:69-71`. |
| Corpus semantics | `stat` measured `manifest-pre.done` and `manifest-post.done` as zero-byte regular files in the immutable real corpus copy source. |
| Mutation impossibility | Emptying each marker did not change its bytes; `cmp` returned success for both. |
| Existing defect | Empty sweep: `required 25`, `rc0 22`, `rc1 3`; named results only for `timeline.jsonl`, raw JSON errors for the two JSON files. |
| Header defect | Duplicate header, body header, trailing field, and CRLF each returned a version from `pins.corpus_version()` on standalone scratch inputs. |
| Idiom-table defect | Removing one declared `Path(framedir, ...)` row from a valid scratch test copy yielded `10 passed, 87 deselected in 0.18s`. |
| S0-02 seam | D-022 and the read-only runner specify a separate `RUST_LOG=debug` environment extension; no runner or S0-02 file was edited. |

## Disposition needed

A coordinator/owner decision is required before P5c can continue. Real options are:

1. Revise item 1 to define the two `.done` files as intentionally empty marker constraints and revise the empty-mutation requirement to cover only the 23 artifacts for which empty content is invalid.
2. Change the producer contract so the `.done` markers carry non-empty pinned content, then recapture the corpus and update all consumers/acceptance evidence. `pc_manifest.sh`, the immutable corpus, and checker consumers are outside this lane's write boundary.
3. Remove the markers from the required-file contract only if the independent checker/consumer contract is changed and verifies that removal.

Option 1 preserves existing corpus bytes but is a material change to the stated `25/25` acceptance condition. Options 2 and 3 require cross-lane design approval. I will not silently select one.

## Items not started

Items 2–10 were intentionally not implemented because the brief requires items in order and item 1 is contradictory. This includes the strict-header implementation, idiom-table cardinality change, S0-02 environment extension, P5b historical-report status line, mutations, AP sweep, tests, lane gates, and report-lint for an implementation change.

F5 remains A5l work: the checker still owns a different pinned-process/version consumer. The real recapture and VB-F12/VB-F13/VB-F14 remain not done. No live buzz-acp, Hermes, tee, relay, model, or owner service was started.

## Evidence tiers

- Verified: source table and producer reads; required-set enumeration; corpus file type/size; `cmp`; the complete empty-file sweep; header probes; idiom-row deletion probe; static S0-02 runner/decision read.
- Inferred: no deterministic content-only validator can distinguish byte-identical valid and mutated zero-byte marker inputs at the same path.
- Assumed: none.

## Self-attack

1. The markers might not be required in v2.2. Ruled out by the executable `required_files("v2.2")` enumeration and the `required` table rows at `P:232` and `P:239`.
2. The corpus markers might be accidentally empty while the producer writes content. Ruled out by the producer's terminal `touch` at `M:71` and the direct corpus size measurement.
3. A filesystem timestamp might distinguish the mutation. Rejected: it is neither content validation nor a pinned semantic value, and a copy/collection changes it independently of evidence validity.

## Hygiene

No production or test source file was modified. The only in-tree output is this blocker report; the required external incremental draft is outside the repository tree. No `git add`, commit, push, reset, checkout, stash, credentials read, or owner-service action occurred. Scratch probes copied the real corpus under this lane's scratch directory and did not write to the golden source.

Implementation file identity: none, because no implementation file changed. No implementation gate result exists and no gate outcome is claimed. The planned 25/25 empty-artifact mutation denominator is invalid as written: two stipulated mutations are byte-identical no-ops, so a hollow-green rate for that nonexistent gate must not be fabricated.

Mechanical self-lint after writing this blocker report:

    report_lint: 10 refs — OK 10, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
