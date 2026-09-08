# P5c — AMENDMENT 1 (coordinator decision 2026-09-08 20:1xZ): item 1's constraint table is PER FILE, and two required artifacts are valid only when EMPTY

The P5c lane stopped at item 1 with a blocker report (`tasks/briefs/s0-01-p5c-support/P5c-report.md`, lint `10 refs — OK 10`):
the brief's acceptance line "every required file emptied → rc 1 with its named line (25/25)" contradicts the producer's contract for
two of the 25 required artifacts. `manifest-pre.done` and `manifest-post.done` (`proofs/S0-01/pins.py:232,239`, both `required`) are
completion MARKERS that `pc_manifest.sh` creates with `touch` after the gzip and the digest (`proofs/S0-01/tools/pc/pc_manifest.sh:71`);
the immutable real corpus carries both at zero bytes, and "emptying" them is a byte-identical no-op (`cmp` equal). The lane was right
to stop rather than manufacture a metadata-based distinction (the NO-STUBS rule). This amendment takes the lane's option 1 and pins it.

## Item 1, revised (replaces the original item 1 in full; items 2-10 stand unchanged)

**F4 — content validation for EVERY required artifact, before record construction, by a PER-FILE constraint.** `pins.py` gains a
per-artifact content-constraint table beside `required_files()` — one row per required file naming its kind. The kinds, closed:
`json-object`, `json-array`, `jsonl-nonempty`, `gzip-text-nonempty`, `text-nonempty`, `int-exit-code`, and **`empty-marker`**
(exactly 0 bytes — the file's whole meaning is "the phase completed"; any content means a foreign or corrupted artifact). The two
`.done` markers are `empty-marker`; every other required file has a kind for which empty content is INVALID. A test asserts the
table's key set equals `required_files(v)` for every known version (a new required file without a row is red) and that every kind
in the table is one of the closed set.

`build_capture_record.py` (`:69-85` — today presence only, plus one `timeline.jsonl` size check) validates each present required file
against its row BEFORE constructing `capture.json`: an empty file whose kind forbids it → `<leg>: <name> is empty`; a non-empty
`empty-marker` → `<leg>: <name> is a completion marker and must be empty (N bytes)`; unparseable JSON / bad gzip / non-UTF-8 →
`<leg>: <name> is not valid <kind>: <reason>` — never a raw traceback; the wrong JSON shape (`[]` where an object is required) → named.

**The sweep, corrected:** VERIFY-P5b's sweep becomes a committed parametrized test over the whole required set on a copy of the real
v2.2 `run-1` corpus (the PC's `/home/rocco/s0-01-pinned/realleg/golden/run-1`; the sandbox uses `S0_01_REAL_LEG_DIR`): each of the
25 required files mutated to ITS invalid content — the 23 non-marker files emptied, the 2 markers given one byte — → rc 1 with the
named line, 25/25 (the denominator is the 25 required files, each with its own invalid mutation, never "emptied" for all);
malformed JSON, `[]`, corrupt gzip, a non-UTF-8 byte → named; the untouched corpus → rc 0. The `--check` path validates the same
constraints (byte identity over VALID artifacts). Paste the sweep's 25 rows.

## Everything else stands

Items 2-10 of `tasks/briefs/s0-01-p5c-pc-tools-every-required-artifact-validated-the-header-strict-the-s0-02-env-extension.md` are
unchanged, in order: the strict header parser (2), the idiom table with cardinality (3), the P5b report stamp (4), the S0-02 env
extension (the owner's decision, task #47), the mutants, the AP sweep, the gates, the report discipline. The blocker report's
verified rows (the 22-of-25 rc-0 sweep on the presence gate, the header probes, the idiom-row deletion at `10 passed, 87 deselected`)
are the red-befores for items 1-3 — paste them beside the green-afters. Report path: `tasks/briefs/s0-01-p5c-support/P5c-report.md`
(the blocker report becomes its "Blocker (resolved by AMENDMENT 1)" section; do not delete it).
