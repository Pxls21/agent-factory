# VERIFY-J1-2 — the targeted adversarial verify of the J1 decision ledger (`src/agent_factory/decisions/ledger.py`)

**Role:** `adversarial-verifier` (Opus 5), IN THE SANDBOX. Honey `full`: line-bounded findings, evidence anchors, SOLID/UNSURE
on every claim. Your report is DATA for the coordinator's gate; you return a GATE RECOMMENDATION, never a verdict. Do NOT spawn
subagents.

**PIN:** `9d11c25` (the J1-2 landing on origin). The working tree's decisions boundary is BYTE-IDENTICAL to the PIN (measured
below). Work on the tree READ-ONLY: every mutant, fixture and hostile ledger lives in a scratch copy under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vj12/` (a `git archive 9d11c25` of `src/` and the two
test files; run it with `PYTHONPATH=<scratch>/src`). The ONLY file you write in the tree is your report. The sandbox has about
2 GB of free disk: keep scratch small and delete it when done. No model, no network: this module must never call Laya (KC-J1).

## What landed (file:line at the PIN; L = `src/agent_factory/decisions/ledger.py`, V = `src/agent_factory/decisions/volatile.py`, C = `src/agent_factory/decisions/canonical.py`, T = `tests/test_decisions_ledger.py`)

Contract (frozen): `tasks/briefs/laya/J1-2-brief.md` items 1-7 with AMENDMENT J1-A1 (`source_ref.source_digest` is NOT part of
`row_id`) and the declared limits (an unkeyed digest stops accidental or naive mutation, not a forger who recomputes every
digest; a deleted row is not detected; one writer at a time). The seed's AC 2: replaying the same committed sources twice gives a
byte-identical ledger, with row identity and `state_digest` stable across differing commits and compacted transcripts
(`seeds/seed-laya-j1-v1.yaml`). The builder's report `tasks/briefs/laya/J1-2-report.md` is an INPUT to attack, never evidence.

- The row and its identity — the field tuples L:36 (`_VALID_KINDS`), L:44 (`_ROW_FIELDS`), L:57 (`_SOURCE_REF_FIELDS`);
  `_compute_row_id` L:70 (producer, question_id, state_digest, source_ref {kind, path, locator}); `_compute_row_digest` L:85
  (the row without `row_digest`); `_validate_row` L:90 (steps a-d: complete, valid, digests recomputed, the stored state a
  fixed point).
- `make_row` L:191 — the two literals set, `root` threaded explicitly, J1-1's refusals passed through.
- `append` L:230 — validate, replay-verify the whole file, refuse a duplicate `row_id`, then ONE `os.write` of
  `canonical(row) + "\n"` (L:256) with `O_WRONLY|O_APPEND|O_CREAT` (L:252) and `os.fsync` (L:257).
- `replay` L:264 — `open(path_str, "rb")` (L:274); a missing or empty file is `[]`; every line must end in `\n` and equal
  `canonical(parsed)` byte for byte, else `decision-ledger-unparseable: <path>:<lineno>`; then a-d per row; a repeated `row_id`
  → `decision-row-duplicate`.
- Tests T:70 `test_import_ac1`, T:104 `test_replay_byte_identical_x2`, T:124 `test_relanding_same_row_id`, T:165
  `test_source_digest_not_in_identity`, T:222 `test_missing_provenance_each`, T:278 `test_duplicate_refused_bytes_unchanged`,
  T:296 `test_tamper_detected`, T:387 `test_state_not_canonical`, T:470 `test_unparseable_lines`, T:507
  `test_invalid_fields`, T:562 `test_append_only_prefix`, T:584 `test_corrupt_ledger_not_appended`, T:609
  `test_j1_1_refusals_propagate`.

## PREMISE — MEASURED (coordinator, 2026-09-23 03:4x-04:1xZ, sandbox)

```
$ git diff --stat 9d11c25 HEAD -- src/agent_factory/decisions tests/test_decisions_ledger.py tests/test_decisions_canonical.py
(empty = byte-identical)
$ sha256[:16] + lines at 9d11c25
803197133f2e2f6e 333 src/agent_factory/decisions/ledger.py
bc9cb1d03fdb77a4 77 src/agent_factory/decisions/canonical.py
b48899c883c7231f 295 src/agent_factory/decisions/volatile.py
2aec3875f71213e4 21 src/agent_factory/decisions/__init__.py
787f08043ca086a1 634 tests/test_decisions_ledger.py
48fdf09e8038a146 340 tests/test_decisions_canonical.py
# the gates below ran on the lane's working-tree bytes before the landing commit; the identities above are those bytes
$ mkdir -p /tmp/j12/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/j12/bt  (x2)
27 passed in 0.36s
27 passed in 0.31s
$ /root/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/ledger.py tests/test_decisions_ledger.py
(clean, rc 0)
$ AC 1 with the venv interpreter: OK  (the system python3 has no agent_factory; PYTHONPATH=src also passes)
$ AC 2: python -m pytest tests/test_decisions_ledger.py -q
13 passed in 0.19s
$ python3 scripts/ap_screen.py src/agent_factory/decisions/ledger.py
AP-32: 1   src/agent_factory/decisions/ledger.py:61: return hashlib.sha256(text.encode("utf-8")).hexdigest()
$ python3 scripts/ap_screen.py --tests tests/test_decisions_ledger.py
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 38 files scanned, clean
```

The builder's mutation table (J1-2-report.md): m1-m7 all RED (not re-run by the coordinator). **Everything above is ALREADY
MEASURED — do not spend your budget re-deriving it; your value is the shapes nobody tried.**

## ITEMS (discovery exhaustive; disposition disciplined)

Number your findings F1…; for each: evidence level (reproduced / read / inferred), file:line, expected vs observed, the
cheapest red control, and the blocking predicate (contract-mapped · reproduced through the real production path · materially
effective · a concrete discriminator · in boundary). A red test is necessary, never sufficient.

1. **Identity (J1-A1).** `incumbent_answer`, `checkpoint_digest` and `calibration_state` are not in `row_id`. Build two rows from
   the same source entry whose incumbent answers differ (the source edited in place, then re-harvested): is the second refused
   as a duplicate, and is that what AC 2 and the contract intend, or does it silently keep a stale answer? Then the reverse
   check: two DIFFERENT decisions that share producer, question, state and locator (two findings under one heading): do they
   collide? Grade each against the contract text, not against the tests.
2. **The canonical line.** Hand-write lines that are valid JSON but not canonical: keys out of order, extra whitespace, a
   `é` escape against a literal `é`, an NFD string against its NFC form, `1.0` against `1`, `-0`, a duplicate key inside
   one object, a trailing `\r\n`, a UTF-8 BOM on line 1. Paste `replay`'s refusal (reason and `<path>:<lineno>`) for each, and
   name any that is accepted.
3. **The append path's failure modes.** (a) A short write: put the ledger on a tiny tmpfs you mount under your scratch root
   (as root: `mount -t tmpfs -o size=<small> tmpfs <dir>`, unmount after) so the last row only partly fits; does `append`
   return the `row_id` while the file holds a partial line (L:256 ignores `os.write`'s return), and what does the next `replay`
   say? (b) A FIFO at the ledger path: does `replay` (L:274) block? Run it under `timeout 10`. (c) A symlink at the ledger path
   to another scratch file: followed by both `replay` and `append`? (d) A directory at the path. Grade each against the
   contract and the declared limits; a hang or a silent success on a partial write is the class to look for.
4. **Named refusals.** Reach every reason the contract names (`decision-row-incomplete`, `-invalid`, `-digest-mismatch`,
   `-state-not-canonical`, `-duplicate`, `decision-ledger-unparseable`) through the PUBLIC functions, and check each detail
   format: `missing <field>` with `source_ref.<sub>` for a sub-field; `<field>=<value>` cut to 80 characters (try a value of
   79, 80, 81 characters and one holding a newline); the row_id the row carries on a digest mismatch; `<path>:<lineno>` with the
   path as given (a relative path, a `pathlib.Path`) and a 1-based line number. List any refusal that surfaces as a bare
   `KeyError`, `TypeError`, `UnicodeDecodeError` or `json` exception instead of a `DecisionStateError`.
5. **Path and kind validity.** `source_ref.path` must be repo-relative with no leading `/`, no `..` segment and no `\`: try
   `./a`, `a/./b`, `a//b`, `a/..b` (not a `..` segment), `%2e%2e/a`, an empty segment, a trailing `/`, a NUL byte, and a
   `locator` holding `\r` or U+2028. Which are accepted, and does the contract say they should be?
6. **Configuration channel.** Does anything in L read `os.environ`, the cwd, or a default root when `root` is omitted? (A config
   read from the environment is AF-AP-24's class.)
7. **New mutants (never m1-m7).** At least: M8 `_compute_row_id` with `source_digest` back in the identity (the J1-A1 test
   T:165 must red); M9 `replay`'s byte comparison against `canonical(parsed)` removed; M10 `append`'s duplicate check removed
   while `replay`'s stays; M11 `_is_hex64` accepting uppercase; M12 `os.fsync` removed (say whether any test can observe it, and
   whether that is a declared limit); M13 the value cut to 80 changed to 79. One row each: mutant · compiles (`py_compile`) ·
   collected count · killed-by / SURVIVED / EQUIVALENT (AF-AP-78: a syntax kill is not a kill).
8. **The report.** Any claim in `J1-2-report.md` the PIN does not support is a finding (line cites, counts, the mutant table,
   DISCREPANCIES, NOT-done).
9. **Out of scope, do not re-litigate:** J1-1's internals (`normalize`, `redact`, `canonical`, `state_digest`; VERIFY-J1-1 is
   running on the PC and J1-1-R1, task #139, repairs the bound-after-redact finding), J1-3's harvest grammars (not built), and
   any Laya call (none may exist). Note a touchpoint in one line if a finding bears on them.

## Deliverable

`tasks/briefs/laya/VERIFY-J1-2-report.md` — sections: OUTCOME (one paragraph, the GATE RECOMMENDATION first: `MERGE-READY` /
`MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) · IDENTITY (the digests you measured vs the table above) · ITEMS
1-9 with findings F1… · MUTATION TABLE · GATES (every count PASTED from the run with its exact invocation; never typed; the two
files twice, `--basetemp` under your scratch dir) · FOLLOW-UPS (non-blocking, one line each, for the coordinator to file under
D-034) · NOT-done (first-class). Lint floor: `python3 scripts/report_lint.py --min-refs 12 --map
L=src/agent_factory/decisions/ledger.py --map V=src/agent_factory/decisions/volatile.py --map
C=src/agent_factory/decisions/canonical.py --map T=tests/test_decisions_ledger.py tasks/briefs/laya/VERIFY-J1-2-report.md --root
.`; apply its `fix:` hints for at most three rounds, then paste and finish. Write the report incrementally from the start. Run
gates in ONE foreground call. Never edit the tree except the report; never `git stash` / `git checkout` / `git restore`
anything. Unmount every tmpfs you mounted and remove your scratch root before you finish. Do not commit, push, post, or open
issues — the coordinator does.
