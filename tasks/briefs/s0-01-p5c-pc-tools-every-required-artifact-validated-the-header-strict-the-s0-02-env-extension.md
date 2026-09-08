# Lane P5c — S0-01 PC capture tools round 3: every required artifact validated for content with named parse errors, the scan header grammar strict, the parser-idiom table as data with cardinality, the S0-02-only pinned environment extension

**PIN: `3614dc9`** (the current branch head; the PC tool files are 77f46a2's round-2 bytes, unchanged since). Role: code-implementer (the
PC Hermes build lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo agent-factory, branch
claude/soundbox-kit-migration-iz1jwf. Boundary (yours, disjoint from every other lane): `proofs/S0-01/pins.py`,
`proofs/S0-01/tools/build_capture_record.py`, `proofs/S0-01/tools/pc/pc_launch.py`, `proofs/S0-01/tools/pc/pc_negative.py`,
`proofs/S0-01/tools/pc/pc_post.sh`, `proofs/S0-01/tools/pc/collect_leg.sh`, `proofs/S0-01/tools/pc/run_leg.sh`,
`tests/test_s0_01_pc_tools.py`, `tests/test_s0_01_pc_post_scan.py`, a one-line STATUS stamp atop
`tasks/briefs/s0-01-p5b-support/P5b-report.md`, your report `tasks/briefs/s0-01-p5c-support/P5c-report.md`. NOT yours: the checker
(`check_acp_conformance.py` — lane A5l adopts the pins predicates), the tee, the backend, the probe (lane N5j is editing
`acp_probe.py` and its test right now), `proofs/S0-02/**` (the S0-02 runner SELECTS your extension in its own round; you only
provide it). No live buzz-acp / hermes-acp / Hermes / tee / relay / model execution (the venue rule); every FIFO/symlink rig standalone
under `timeout` with a PID-scoped watchdog; kill only what you start, by pid; never background a run and stop; no outward actions.

**Inputs (read in this order):** VERIFY-P5b's report `tasks/briefs/s0-01-p5b-support/VERIFY-P5b-report.md` (the round's contract:
F1-F5, the 40-mutant audit, Item 10's round-3 list) · the P5b brief and report (`tasks/briefs/s0-01-p5b-*.md`,
`tasks/briefs/s0-01-p5b-support/P5b-report.md`) · the S0-02 runner's PREFLIGHT comment (`proofs/S0-02/tools/pc/run_s0_02_legs.sh:45-50`,
read-only: the seam you provide) · the owner decision on the seam (`docs/08_DECISION_LOG.md`, the S0-02 live-legs D-row; task #47
option a) · `docs/INCIDENT-LOG.md` (AF-AP-40, AF-AP-57, AF-AP-63, AF-AP-64, AF-AP-65).

## Design (pinned — build it, do not redesign it; line numbers are `3614dc9`'s = 77f46a2's)
1. **F4 — content validation for EVERY required artifact, before record construction.** `pins.py` gains a per-artifact content
   constraint table beside `required_files()` (`:279`) — one row per required file naming its kind: `json-object`, `json-array`,
   `jsonl-nonempty`, `gzip-text-nonempty`, `text-nonempty`, `int-exit-code`, … — every required name has exactly one row (a test
   asserts the table's key set equals `required_files(v)` for every known version, so a new required file without a constraint is
   red). `build_capture_record.py` (`:75`) validates each present required file against its row BEFORE constructing `capture.json`:
   empty → `<leg>: <name> is empty`; unparseable JSON / bad gzip / non-UTF-8 → `<leg>: <name> is not valid <kind>: <reason>` — never a
   raw traceback; the wrong JSON shape (`[]` where an object is required) → named. VERIFY-P5b's sweep becomes a committed
   parametrized test over the whole required set on a copy of the real v2.2 `run-1` corpus (the PC's
   `/home/rocco/s0-01-pinned/realleg/golden/run-1`; the sandbox uses `S0_01_REAL_LEG_DIR`): every required file emptied → rc 1 with
   its named line (25/25, never "22 of 25"); malformed JSON, `[]`, corrupt gzip, a non-UTF-8 byte → named; the untouched corpus → rc 0.
   The `--check` path validates the same constraints (byte identity over VALID artifacts).
2. **F2 — `corpus_version()` is a STRICT header parser** (pinned decision: strict, not a sniffer). `_SCAN_HEADER_VERSION_RE` (`:272`)
   full-matches the complete v2.x header grammar the checker owns (cite the checker's grammar line, do not edit the checker); a
   second header line, a header in the body, trailing fields, CRLF → `process-scan header malformed: <reason>` from `corpus_version()`
   (`:305`), never a guessed version. Tests for each shape; the golden corpus still parses.
3. **F3 — the parser-idiom table is DATA with a cardinality assertion.** The 11 declared producer idioms (`tests/test_s0_01_pc_tools.py:340`)
   move into a named constant (a tuple of (source, expected) rows) consumed by the parametrization AND by a separate test that asserts
   `len(IDIOMS) == 11` and the exact set of expected names — deleting a row is red twice (VERIFY-P5b's M10 is the killer).
4. **The S0-02-only pinned environment extension (owner decision, task #47 option a; task #52).** `pins.py` gains
   `PINNED_ENV_KEYS_S0_02 = PINNED_ENV_KEYS | frozenset({"RUST_LOG"})` and `PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}`, both
   frozen; `pc_launch.py` gains `--env-set {s0-01,s0-02}` (default `s0-01` — the default behaviour byte-identical to today: a test
   proves the built environment for every S0-01 leg is unchanged), and with `s0-02` the launch environment carries exactly one more
   key with the pinned value, the closed-set check at `:254` using the selected set; the recorded `env.json` names the set
   (`env_set: "s0-02"`) so a capture never hides which set launched it. Tests: the default set unchanged (byte-identical dict), the
   extension differs by exactly `{"RUST_LOG": "debug"}`, an unknown set name refused by name, `s0-02` never selected implicitly.
   You do NOT edit the S0-02 runner; state in the report the one-line change it will make (`--env-set s0-02` on its three
   buzz-acp-decided legs).
5. **F1 — the P5b report's drifted refs.** Add ONE line atop `tasks/briefs/s0-01-p5b-support/P5b-report.md`: `STATUS 2026-09-08: line
   references are 77f46a2-era and drifted in the 9c three-way merge of pins.py (VERIFY-P5b F1); the round-3 report supersedes them.`
   Never rewrite the historical report.
6. **F5 is A5l's** (the checker adopts `pins.is_pinned_argv` / `required_files` / `entry_allowlist` / the shared version detector) —
   state it NOT-done first-class and do not touch the checker.
7. **Every negative control fails for the EXACT expected reason** (the named line; AF-AP-63); no `if <field> == <literal>:` without a
   raising other arm (AF-AP-65); no presence-gated assertion (AF-AP-40); `os.environ` is never read below `main()` (the resolved-once
   rule at `pc_launch.py:32`).
8. **Mutants:** VERIFY-P5b's 40 re-run + this round's (each content constraint removed one at a time → its named test red; the
   strict header regex loosened; the cardinality assertion removed; the extension selected by default; the extension's value
   changed; the set name absent from env.json) — every one killed with its killer line pasted; ≥50 total; by-construction survivors
   named as such.
9. **18-class self-sweep as an ENUMERATION** (class 2 — every required artifact READ and VALIDATED: the constraint table IS the
   enumeration; class 6 — the env domains incl. the new set).
10. **Report discipline:** FILE IDENTITY of the FINAL bytes; every `file:line` in the machine form `path:line` (VERIFY-P5b's own report
    cited lines in prose and became unlintable — do not repeat it) from `grep -n` on the FINAL bytes and `python3 scripts/report_lint.py
    <report> --map P=proofs/S0-01/pins.py --map B=proofs/S0-01/tools/build_capture_record.py --map L=proofs/S0-01/tools/pc/pc_launch.py
    --map T=tests/test_s0_01_pc_tools.py --map S=tests/test_s0_01_pc_post_scan.py` pasted with MISS 0; the direct venue suite pasted
    (`S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden`, `/home/rocco/venv-agent-factory/bin` first on PATH,
    an absolute `--basetemp`) for the two test files (VERIFY-P5b's `194 passed` is the floor) AND the joint S0-01 set the 9c gate ran
    (the checker and backend tests consume `pins` — `1556 passed, 9 xfailed` is the floor; a red there is YOUR regression); the two
    `lane_gate.sh` RESULT lines (`scripts/lane_gate.sh -r 3614dc9 -f "<your files>" -t "tests/test_s0_01_pc_tools.py
    tests/test_s0_01_pc_post_scan.py" -n 2`); `ap_screen.py --s0-01` + `--tests` classified by run; NOT-done first-class (F5, the live
    capture, VB-F12/F13/F14).

## Report
Write it to `tasks/briefs/s0-01-p5c-support/P5c-report.md` inside your tree, draft after EACH item, and return it whole as your
final message: the DONE table (item → file:line → the red test → its killer line), the constraint table, the mutant table (≥50), the
discrepancies, the self-attack, the evidence tiers, NOT-done first.
