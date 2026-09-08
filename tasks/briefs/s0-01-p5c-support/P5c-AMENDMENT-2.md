# P5c — AMENDMENT 2 (coordinator decision 2026-09-08 21:3xZ): the constraint table is VERSION-AWARE, and the invalid mutation is defined per (version, file) from a MEASURED corpus

The P5c-b lane stopped a second time, correctly (`tasks/briefs/s0-01-p5c-support/P5c-report.md`, lint `7 refs — OK 5,
UNCHECKABLE 2`): AMENDMENT 1's sentence "every other required file has a kind for which empty content is INVALID" is false for
the v2.2 corpus. AMENDMENT 1 was written from memory of the producers; this amendment is written from a measurement of the real
corpus, taken 2026-09-08 21:3xZ on the PC (`stat -c %s` over every file of the four positive legs of
`/home/rocco/s0-01-pinned/realleg/golden`; the scan files' first lines read with `head -1`):

| leg | zero-byte files | `process-scan-after.txt` |
|---|---|---|
| run-1 | `manifest-pre.done`, `manifest-post.done`, `process-scan-teardown.txt` | 444 bytes, line 1 a body row (`<pid> <ppid> <etimes> …/buzz-acp --relay …`), no header |
| cancel | the same three | 444 bytes, a body row, no header |
| shutdown | the same three + `process-scan-after.txt` | 0 bytes |
| two-users | the same three | 444 bytes, a body row, no header |

`pins.py:269-272` states the contract these bytes follow: a v2.2 leg's `process-scan-after.txt` has NO header — line 1 is a body
row or the file is EMPTY (a clean v2.2 shutdown scan wrote no rows); `pins.py:305-328` (`corpus_version`) derives v2.2 from
exactly that shape. `process-scan-teardown.txt` is empty on every v2.2 leg. Neither file is a completion marker: they are the
v2.2 scan artifacts, and v2.3/v2.4 (`PINNED_SCAN_VERSIONS`) give them a header and rows.

## Item 1, revised again (replaces AMENDMENT 1's item 1 in full; items 2-10 stand unchanged)

**F4 — content validation for EVERY required artifact, before record construction, by a constraint that is a function of
`(version, name)`.** `pins.py` gains the per-artifact content-constraint table beside `required_files()`; a row's kind may
differ by capture-contract version. The kinds, closed: `json-object`, `json-array`, `jsonl-nonempty`, `gzip-text-nonempty`,
`text-nonempty`, `int-exit-code`, `empty-marker` (exactly 0 bytes), **`utf8-text-maybe-empty`** (valid UTF-8, empty allowed),
**`scan-headed`** (non-empty, line 1 full-matches the scan header grammar `pins._SCAN_HEADER_VERSION_RE` for a version in
`PINNED_SCAN_VERSIONS`, every later line a body row). Version-aware rows:

| name | v2.2 | v2.3 / v2.4 |
|---|---|---|
| `process-scan-after.txt` | `utf8-text-maybe-empty` (line 1, if present, is a body row — a `#` line here means a header the pin does not know: `corpus_version` already refuses it) | `scan-headed` |
| `process-scan-teardown.txt` | `utf8-text-maybe-empty` | `scan-headed` |
| `manifest-pre.done`, `manifest-post.done` | `empty-marker` | `empty-marker` |
| every other required name | a kind for which empty is invalid (as AMENDMENT 1) | the same |

The constraint function is `content_constraint(version, name)`; a test asserts that for every known version the table's key
set equals `required_files(version)` and every kind is in the closed set. `build_capture_record.py` (`:69-85`) validates each
present required file against `content_constraint(pins.corpus_version(leg), name)` BEFORE constructing `capture.json`; every
refusal is named as AMENDMENT 1 specifies (`<leg>: <name> is empty` / `… is a completion marker and must be empty (N bytes)` /
`… is not valid <kind>: <reason>` / for `scan-headed`: `… has no enumeration header` or `… unrecognised header`).

**The sweep, per (version, file):** every required file gets exactly ONE invalid mutation defined by its kind — empty-forbidding
kinds: emptied; `empty-marker`: one byte; `utf8-text-maybe-empty`: one non-UTF-8 byte (`\xff`) appended; `scan-headed`: the
header line removed (a v2.4 file that then reads as a v2.2 body row is NOT a valid v2.4 leg: `corpus_version` of that leg drops
to v2.2 and `tee-status.json` is then an unexpected entry — the refusal must name that, never mint). Two sweeps, both pasted
in full: (a) the v2.2 sweep on a copy of the real `run-1` corpus — 25 files, 25 named refusals, the untouched copy rc 0 — plus
the `shutdown` copy untouched → rc 0 (the empty after-scan accepted as v2.2); (b) the v2.4 sweep on a synthetic v2.4 leg
built from the committed `synthetic_leg` fixture with a v2.4 header written into both scan files (`required_files("v2.4")`
= 26 names with `tee-status.json`) — 26 files, 26 named refusals, the untouched synthetic leg rc 0. Malformed JSON, `[]`,
corrupt gzip, a non-UTF-8 byte in a text file → named, as before. The `--check` path validates the same constraints.

## Everything else stands

Items 2-10 of the original brief are unchanged. Both blocker reports stay in the final report as its "Blocker (resolved by
AMENDMENT 1)" and "Blocker (resolved by AMENDMENT 2)" sections; their verified rows are the red-befores. The measurement table
above is the corpus contract for this round — if the lane measures anything different on the PC, it STOPS and reports the
difference; it never widens a kind to fit.
