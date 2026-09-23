# J1-2 — ledger.py: the append-only decision ledger (mandatory provenance, row identity, duplicate refusal, replay with digest verification)

PIN: the origin commit that carries this brief (read it with `git log -1 --format=%h origin/claude/soundbox-kit-migration-iz1jwf -- tasks/briefs/laya/J1-2-brief.md`; nothing in the J1 boundary changed since d259f48, the premise's measurement point). LANE: laya-j1-2 (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation: `isolation: "worktree"` fails on this tree).
CONTRACT: `seeds/seed-laya-j1-v1.yaml` AC 1 (`ac_bdaf2f13a1cee8c9`, the import command) + AC 2 (`ac_19c60ff84406dcb4`, `python -m pytest tests/test_decisions_ledger.py -q`) · `tasks/laya-j1-breakdown.md` row J1-2 and the pinned decisions (a row = one incumbent decision; row_id; duplicate refusal is named; mandatory provenance; replay verifies digests) · AMENDMENT J1-A1 below.
BOUNDARY (exact): NEW `src/agent_factory/decisions/ledger.py`, NEW `tests/test_decisions_ledger.py`, NEW `tests/fixtures/decisions/ledger/` (only if a committed fixture is truly needed; build rows in the test from J1-1's goldens instead where you can), NEW `tasks/briefs/laya/J1-2-report.md`. Read anything. Do NOT modify `src/agent_factory/decisions/__init__.py`, `canonical.py` or `volatile.py` (J1-1's; its repair J1-1-R1 will touch `volatile.py`), the golden fixtures, anything under `scripts/`, `proofs/` or `.github/`, any hook, or `pyproject.toml`. Another lane holds `proofs/S0-05/netns_lib.sh`, `proofs/S0-05/tools/pc/run_s0_05_units.sh`, `tests/test_s0_05_egress.py` and `tasks/briefs/s0-05-support/E2-R1-report.md` in this same tree: never touch, run or revert them. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push` here. Do NOT spawn subagents. No outward-facing action of any kind.

## The contract (coordinator, decided; do not re-litigate — a line you cannot meet is a DISCREPANCY with its measurement, never a silent change)

1. **The row.** One JSONL line per row: `canonical(row) + "\n"` with J1-1's `canonical()` (sorted keys, NFC, integers/strings/lists/dicts only). Every field is required; every string field is non-empty:
   - `question_id` — one of J1-1's seven types (`schema_keys` refuses an unknown one: `decision-question-unknown: <question_id>`).
   - `producer` — the harvester that produced the row (J1-3 names them, e.g. `decide-harvest/incident-log`).
   - `checkpoint_digest` — the literal `none` (every J1 row is an incumbent).
   - `calibration_state` — the literal `incumbent`.
   - `incumbent_answer` — the answer the existing system produced.
   - `state` — the STORED state, `redact(normalize(question_id, raw_state, root))`, a dict; never raw bytes.
   - `state_digest` — J1-1's `state_digest(question_id, raw_state, root)`, 64 lowercase hex; it equals sha256 of `canonical(state)`.
   - `source_ref` — `{kind, path, source_digest, locator}`: `kind` ∈ {`transcript_jsonl`, `lane_report`, `verify_report`, `incident_log`, `registry`}; `path` repo-relative (no leading `/`, no `..` segment, no `\`); `source_digest` 64 lowercase hex (sha256 of the file bytes at harvest); `locator` newline-free (a JSONL message uuid, a finding id + heading, a dated entry heading).
   - `row_id` — item 2.
   - `row_digest` — sha256 hex of `canonical(row without row_digest)`.
   The seed's ontology also names `row_type`, `source_kind`, `redactions` and `captured_only`. Here `question_id` IS the row type and `source_ref.kind` IS the source kind. `redactions` and `captured_only` are NOT carried: `canonical()` refuses booleans, J1-1's `normalize` does not report which classes it stripped, and every J1 row is capture-only by construction. Say so in the module docstring.
2. **row_id, AMENDMENT J1-A1 (coordinator, 2026-09-23).** `row_id = sha256(canonical({"producer", "question_id", "state_digest", "source_ref": {"kind", "path", "locator"}}))`, hex. `source_ref.source_digest` is NOT part of the identity. The breakdown put the whole `source_ref`, file digest included, into the identity. Every harvest source only grows (39 commits touched `docs/INCIDENT-LOG.md` since 2026-09-22 00:00Z; premise below), so an old entry read from a later file version would get a new row_id and be appended again instead of being refused as a duplicate, and AC 2's "row identity stable across differing commits" would fail. The file digest stays in the row as provenance, covered by `row_digest`.
3. **`make_row(*, producer, question_id, raw_state, incumbent_answer, source_ref, root)`** builds a complete row. It sets the two literals itself, threads `root` explicitly (never from `os.environ`), and refuses bad input by name (items 4-6). No caller assembles a digest by hand.
4. **`append(ledger_path, row) -> row_id`**, in this order: (a) completeness: every field of item 1 present and non-empty, else `decision-row-incomplete: missing <field>` (a sub-field is named `source_ref.<sub>`); (b) validity: the two literals, the kind set, the path shape, the hex shapes, else `decision-row-invalid: <field>=<value>` (value cut to 80 characters); (c) the row's own digests recomputed (row_id per item 2, `state_digest` as sha256 of `canonical(state)`, `row_digest`), else `decision-row-digest-mismatch: <row_id>` naming the row_id the row carries; (d) the stored state is a fixed point, `redact(normalize(question_id, state, None)) == state`, else `decision-row-state-not-canonical: <row_id>` (measured below: all 14 golden states and a secret-bearing state are fixed points at the PIN); (e) the EXISTING file is replay-verified first, and any replay refusal propagates: a corrupt ledger is never appended to; (f) an existing row_id → `decision-row-duplicate: <row_id>`, the file's bytes unchanged; (g) ONE `canonical(row) + "\n"` written with `os.open(path, O_WRONLY|O_APPEND|O_CREAT, 0o644)` in a single `os.write`, then `os.fsync`. Existing bytes are never rewritten. Single writer by contract (no lock; say so).
5. **`replay(ledger_path) -> list[dict]`**: every line must parse, end with `\n`, and equal `canonical(parsed)` byte for byte, else `decision-ledger-unparseable: <path>:<lineno>` (1-based, the path as given); then (a)-(d) of item 4 per row, in that order; a row_id seen twice in the file → `decision-row-duplicate: <row_id>`. A missing or empty file is an empty ledger (`[]`).
6. Errors are `DecisionStateError` from `agent_factory.decisions.volatile` (`str(e) == f"{reason}: {detail}"`); no new exception class. J1-1's refusals pass through `make_row` unchanged (unknown question, missing or unknown key, bad enum, absolute path outside the root, float).
7. Consume J1-1 ONLY through `normalize`, `redact`, `canonical`, `state_digest`, `schema_keys` and `DecisionStateError`. Reimplement none of them.

**Declared limits** (in the docstring and the report): an unkeyed digest catches accidental or naive mutation, not a forger who recomputes every digest; deleting a whole row is not detected (no hash chain in J1); one writer at a time.

## Tests (each RED before `ledger.py` exists, GREEN after; paste both)
`test_import_ac1` (the seed's AC 1 command prints `OK`) · `test_replay_byte_identical_x2` (≥ 7 rows, one per question type, built from `tests/fixtures/decisions/golden/*.json` with their `state` and `root`, appended in the same order into two fresh ledgers → the files are byte-identical and replay returns the appended rows; the whole test run twice, bitwise) · `test_relanding_same_row_id` (each golden's `variant` with the same producer and source_ref → the same row_id, refused as `decision-row-duplicate: <row_id>`, the file unchanged) · `test_source_digest_not_in_identity` (J1-A1: two different `source_digest` values → one row_id; a different `locator` or `producer` → a different row_id) · `test_missing_provenance_each` (each of the five provenance fields and each `source_ref` sub-field, absent and empty → `decision-row-incomplete: missing <field>` exactly) · `test_duplicate_refused_bytes_unchanged` · `test_tamper_detected` (one character flipped in the FILE in `incumbent_answer`, a state value, `source_ref.locator`, `source_ref.source_digest` and `row_id` → replay refuses `decision-row-digest-mismatch: <stored row_id>`; the same flips on an in-memory row → `append` refuses, the file unchanged) · `test_state_not_canonical` (an un-normalized stored state with consistent digests, and an unredacted secret with consistent digests → `decision-row-state-not-canonical: <row_id>`) · `test_unparseable_lines` (a torn last line, a non-JSON line, and valid JSON that is not canonical → `decision-ledger-unparseable: <path>:<lineno>`) · `test_invalid_fields` (another calibration state, another checkpoint digest, an unknown kind, an absolute path, a `..` path, a non-hex digest → `decision-row-invalid: <field>=<value>`) · `test_append_only_prefix` (after K more appends the first N lines are byte-identical) · `test_corrupt_ledger_not_appended` (a tampered file + a valid append → the replay refusal, the file unchanged) · `test_j1_1_refusals_propagate` (`decision-question-unknown: <qid>`, `decision-state-unknown-key: <qid>.<key>`).
Every secret in a test is an INVENTED string (the shapes in `tests/test_decisions_canonical.py` are fine to reuse).

## Mutants (scratch-copy restore only, never a git restore in this shared tree; each mutant must compile and collect, AF-AP-78; paste the failing test per row)
m1 skip one provenance field → `test_missing_provenance_each` red · m2 a duplicate becomes a silent no-op → `test_duplicate_refused_bytes_unchanged` red · m3 replay skips the digest check → `test_tamper_detected` red · m4 `source_digest` back in the identity → `test_source_digest_not_in_identity` red · m5 the fixed-point check dropped → `test_state_not_canonical` red · m6 replay drops the canonical-line check → `test_unparseable_lines` red · m7 truncating open instead of `O_APPEND` → `test_append_only_prefix` red.

## Gates (paste verbatim)
`mkdir -p /tmp/j12/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/j12/bt` twice (`rm -rf /tmp/j12/bt` after each; J1-1's 14 tests stay green) · `/root/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/ledger.py tests/test_decisions_ledger.py` · the seed's AC 1 and AC 2 verify_commands · `python3 scripts/ap_screen.py src/agent_factory/decisions/ledger.py` and `python3 scripts/ap_screen.py --tests tests/test_decisions_ledger.py` · `python3 scripts/no_laya_in_gates.py` (must stay clean).

## Report (`tasks/briefs/laya/J1-2-report.md`, written incrementally from the start)
DATA, not prose: files:lines; the RED→GREEN pairs; the mutant table; the two gate runs pasted; DISCREPANCIES (a contract line the code could not meet, with the measurement); NOT-done; the declared limits. Lint floor: `python3 scripts/report_lint.py --min-refs 10 --map L=src/agent_factory/decisions/ledger.py --map T=tests/test_decisions_ledger.py tasks/briefs/laya/J1-2-report.md --root .`, at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23, sandbox @ d259f48)
Item 1 of your work: re-run these on the PIN and stop CONTRACT-INVALID on a mismatch that changes the contract.
```
$ git rev-parse --short HEAD; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
d259f48
d259f48
$ ls src/agent_factory/decisions/
__init__.py canonical.py volatile.py 
$ git log --oneline -1 -- src/agent_factory/decisions/
01ca7d5 J1-1 landed (GATED-PENDING-VERIFY): the decisions module (seven closed state schem
$ grep -n "^def \|^class \|^SCHEMAS\|^PLACEHOLDERS" src/agent_factory/decisions/volatile.py src/agent_factory/decisions/canonical.py | grep -v "def _"
src/agent_factory/decisions/volatile.py:33:PLACEHOLDERS = {
src/agent_factory/decisions/volatile.py:62:class DecisionStateError(RuntimeError):
src/agent_factory/decisions/volatile.py:73:class _Field:
src/agent_factory/decisions/volatile.py:153:SCHEMAS: dict[str, dict[str, _Field]] = {
src/agent_factory/decisions/volatile.py:235:def schema_keys(question_id: str) -> tuple[str, ...]:
src/agent_factory/decisions/volatile.py:242:def normalize(question_id: str, state: dict, root: str | os.PathLike | None = None) -> dict:
src/agent_factory/decisions/volatile.py:271:def redact(state: dict) -> dict:
src/agent_factory/decisions/canonical.py:34:def canonical(obj) -> str:
src/agent_factory/decisions/canonical.py:70:def state_digest(question_id: str, state: dict, root: str | None = None) -> str:
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/j12p/bt | tail -1
14 passed in 0.03s
$ python: state_digest(state) and state_digest(variant) against expected_digest, per golden; then an unknown question
ap.violates_row True True
b1.finding_kind True True
b1.finding_sev True True
b2.hit_role True True
d1.bug_echo_scores True True
v1.finding_class True True
wf.drift True True
DecisionStateError decision-question-unknown: x.unknown
$ python: is redact(normalize(q, s1, None)) == s1 for s1 = redact(normalize(q, raw, root)), per golden state and variant, and for a secret-bearing ap.violates_row state
fixed points: 14 of 14 golden states; secret state fixed point: True 'curl -H "Authorization: <redacted:bearer>" x <redacted:sk>'
$ git log --since=2026-09-22T00:00:00Z --format=%h -- docs/INCIDENT-LOG.md | wc -l
39
$ grep -n "row_id = sha256" tasks/laya-j1-breakdown.md | cut -c1-160
14:- **row_id = sha256(canonical JSON of {producer, question_id, state_digest, source_ref})**; `state_digest = sha256(canonical(redact(normalize(state))))`; `so
```
