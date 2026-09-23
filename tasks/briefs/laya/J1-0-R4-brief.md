# J1-0-R4 — the never-a-gate screen never goes blind: a scan that ends mid-construct fails closed, YAML is parsed, and dynamic loads are include edges (task #172; the ONE focused repair of VERIFY-J1-0-R23-STAMP (B))

PIN: the origin commit of this brief (the post-push SHA, named in the dispatch prompt). The three boundary files are byte-identical
to local 361b30c (measured below); re-measure them first.
LANE: j1-0-r4 (sandbox; agent `code-implementer` on the D-054 pin, in the SHARED tree, no worktree isolation). Honey `ultra`
Lever-2: your report is DATA — files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

WHY: VERIFY-J1-0-R23-STAMP (`tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-report.md`, section (B)) found two blockers in J1-0-R3, both
reproduced through the real pre-commit hook on real commits, and the coordinator reproduced F-B1 on a clean copy of HEAD (below):
- **F-B1 (AF-AP-143).** The shell/YAML scan in `scripts/no_laya_in_gates.py` (`_command_segments`) loses sync on ordinary text and
  then scans NOTHING to the end of the file, silently. Live: `scripts/pc_lane.sh:292` holds `"$(bridge "… <<'PY'` — the inner quote
  closes the scanner's quote, `<<'PY'` registers as a heredoc bash never opens, and lines 293-610 are never scanned. In a workflow
  file, one apostrophe in a step name masks later lines the same way (YH-4 below).
- **F-B2 (AF-AP-120, reopened).** `scripts/lint_delta.py:106` (run by pre-commit on every commit) and `scripts/ap_screen.py:26` load
  the UNLISTED `.claude/hooks/edit-snapshot.py` into their own process through `spec_from_file_location`. The J1-0-R3 docstring files
  dynamic imports under "the same limit" as exec edges, but they run IN-PROCESS, which is what AMENDMENT 2 closes.
This is the one repair D-031 allows for this contract revision. The non-blocking findings (F-A2, F-B3..F-B6, F-C1, F-C2, the INFO rows)
are issue #37: do not fix them here; say in the report which of them your change closes incidentally, with the evidence.

CONTRACT SOURCES (read whole before you design): `tasks/briefs/laya/J1-0-R3-brief.md` (AMENDMENT 2 — still in force: every rule there
stands unless a line below replaces it) · the verify report's sections (B) B2, B3, the F-B1 canonical reproduction, the F-B2 census,
the proposed regression tests and the (B) finding inventory · `scripts/no_laya_in_gates.py` and `tests/test_no_laya_in_gates.py` as
they stand at the PIN.

## The contract — AMENDMENT 3 (coordinator, 2026-09-23; decided, do not re-litigate; a contradiction is a DISCREPANCY)

R4-1 **A scan never ends in a non-final state silently.** When the shell scan of a listed non-Python gate file reaches end of input
with a quote open, a heredoc pending, or a `$(`, `${`, `$((` or backtick construct unclosed, the screen refuses with exit 4 (the
completeness family): `gate-file-unparseable: <path>:<line>: <what is open>`, where `<line>` is the line the open construct began on.
Both modes (worktree and `--staged`). This is the backstop; it must never be the reason the LIVE tree fails (R4-2).

R4-2 **The shell scan models the text the live tree holds.** Nested quoting inside `$(…)` within double quotes; `$'…'` with `\'`;
heredoc delimiters by bash's word rules (`<<\EOF`, `<<'EOF'`, `<<"EOF"`, `<<-EOF`, words with hyphens such as `END-X`); `<<` inside
`$(( … ))` is arithmetic, not a heredoc; `${…}` expansions holding quotes or braces; a `}` or `#` inside a word neither splits a
command nor starts a comment. Acceptance: every member trigger of F-B1's shell family in the report's B2 table (S12, S17, S18, S24,
S26, S34, S35, S36) is CAUGHT (`gate-file-sources`) or refused by R4-1 — never CLEAN; BH-2 (below) is refused; and the live tree
stays `clean` in both modes. Where bash itself treats text as data (inside a heredoc body, a single-quoted string), a `.`/`source`
there is NOT an edge: the live `pc_lane.sh` heredoc bodies that are remote scripts must not start refusing.

R4-3 **Workflow files are parsed, not scanned as one shell text.** Every listed `.github/workflows/*.yml` is loaded with a real YAML
parser (PyYAML is in the hook's venv; measure it), and each step's `run:` value is scanned as its own shell text by the R4-1/R4-2
scanner, with every refusal naming the file and the line of the offending command in the YAML file (compose-level node marks, or an
equivalent that maps back). A YAML file that does not parse is `gate-file-unparseable: <path>`. Acceptance: S39, S40, X3 (the flow
mapping `- {name: a, run: . scripts/h.sh}`) and YH-4 (below) are refused; YH-3 still names its line.

R4-4 **A dynamic in-process load is an include edge.** In every listed Python gate file, each call to
`importlib.util.spec_from_file_location`, `importlib.machinery.SourceFileLoader`, `runpy.run_path`, `importlib.import_module`,
`__import__`, and `exec`/`compile` of a file's text loads code into the gate's process. The screen proves each such site's target is
a listed gate file (or, for a module name, stdlib or `EXTERNAL_MODULES`, exactly like AMENDMENT 2's static imports), or refuses it:
`gate-file-import-unlisted: <path>:<line> loads <target>` when it resolves to an unlisted repo file,
`gate-file-import-unresolved: <path>:<line>` when it cannot be resolved. The mechanism is yours (static resolution of literals,
`Path(__file__)` chains and module constants; a closed, reviewed exception set; or both), under two constraints: (a) no exception is
keyed by text alone — the F-B5 class — an exception names the exact (file, target) and is checked for how many times it occurs;
(b) the seven live sites (census below) are all accounted for with the live screen `clean`. The ES reproduction (a vocabulary line in
the loaded hook) must be refused once R4-5 lists the file, and a NEW dynamic load of an unlisted helper must be refused.

R4-5 `scripts/gate_files.txt` lists `.claude/hooks/edit-snapshot.py` (measured: the screen reads `40 files scanned, clean` with it
listed). Listing a file is not editing it: NEVER modify anything under `.claude/` (another lane holds that tree's manifest).

R4-6 The docstring's limits paragraph is corrected: dynamic loads are no longer "the same limit" as exec edges. Exec edges (a script
run in ANOTHER process) stay the declared limit; re-measure the "26 literal exec edges, 12 unlisted scripts" count it quotes (F-B11)
and paste the command and its output, or correct the numbers.

Nothing else changes: the vocabulary, exit codes 0/3/4/64, the existing completeness errors and their texts, the SELF refusal, the
no-bypass rule, the output line format, AMENDMENT 2's static-import rules and EXTERNAL_MODULES lock.

## Tests (in `tests/test_no_laya_in_gates.py`; each RED at the PIN, GREEN after; paste both runs)

- The verifier's five proposed tests (the report's "Proposed regression tests" block, full text there), adopted and renamed as you
  see fit. Measured at authoring on HEAD bytes: `5 failed in 0.27s` (below).
- One fixture per member trigger: S12, S17, S18, S24, S26, S34, S35, S36, S39, S40, X3 (the exact shapes are in the report's B2 table).
- Real-file fixtures copied from the live tree: BH-2 (the real `scripts/pc_lane.sh` with `. scripts/h.sh` inserted after line 400)
  refused; YH-4 (the real `stage0-ci.yml` with the apostrophe and the sourcing step) refused. Copy the real files into the fixture tree
  at test time from the repo, so a later edit of the live files is still covered.
- R4-1's tripwire alone: a file ending inside an open quote, a pending heredoc and an unclosed `$(`, each refused with the start line.
- R4-4: an unlisted `spec_from_file_location` target refused; a listed one allowed; an unresolvable one refused; the ES shape (a
  listed `.claude/hooks/edit-snapshot.py` copy carrying a vocabulary word) exits 3 naming its line.
- The live-tree test stays: exit 0 on the real repo, both modes; paste the scanned-file count.

## Mutation audit (scratch copies only: never `git checkout`, `git restore` or `git stash` in this shared tree)

At least: m1 drop R4-1's end-state check · m2 drop the nested-quote model (S35's shape) · m3 read the heredoc delimiter as
`[A-Za-z0-9_]` only · m4 treat `<<` in arithmetic as a heredoc · m5 scan YAML as one shell text again · m6 drop R4-4's rule · m7 an
exception keyed by text alone · m8 unlist the edit-snapshot hook. Each mutant compiles and its suite collects (AF-AP-78); before you
count a kill, run the killing test on the UNMUTATED tree and paste that it passes (AF-AP-138). A survivor is a finding you report.

## Gates (paste every command with its output)

- `/root/venv-agent-factory/bin/python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/j10r4/bt<n>`
  TWICE, identical counts; the set id (`bash scripts/pc_suite.sh set-id -- tests/test_no_laya_in_gates.py`, premise `e3695f80792b`).
- `python3 scripts/no_laya_in_gates.py` and `python3 scripts/no_laya_in_gates.py --staged` on the real tree: both `clean`, with the
  new count. Time both before and after your change (the screen runs on every commit; say if it got slower and by how much).
- The real pre-commit hook in a THROWAWAY repository (a `git archive` copy of HEAD plus your working files, `git init`, the repo's
  hooks via `core.hooksPath`): BH-2, YH-4 and ES each refused on a real `git commit`; a clean commit lands.
- `/root/venv-agent-factory/bin/python -m pyflakes scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py` (no new hit);
  `python3 scripts/ap_screen.py` on the two files (no new hit, or say why).

## Boundary and standing do-nots

MODIFY `scripts/no_laya_in_gates.py`, `tests/test_no_laya_in_gates.py`, `scripts/gate_files.txt`; CREATE
`tasks/briefs/laya/J1-0-R4-report.md` (write it incrementally). Nothing else. A line you cannot meet inside the boundary is a
DISCREPANCY, never a silent edit elsewhere. Other sandbox agents work in this tree on disjoint files (`proofs/S0-02/`, `proofs/S0-05/`,
their tests, `tasks/briefs/s0-02-support/`, `tasks/briefs/s0-05-support/`, `tasks/briefs/hermes-repin/`, `tasks/briefs/ci/`,
`upstream.lock.yaml`, `docs/HARNESS-PORTS.md`, `tests/test_upstream_lock_lane_runtime.py`): never touch, run or revert them. Never run
`git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push` in this tree; throwaway repositories under
`/tmp/j10r4/` are yours. No outward-facing action; no PC or bridge use. Test vocabulary in fixtures is the screen's own closed list,
in throwaway trees only. Scratch lives under `/tmp/j10r4/` and is removed when you finish (the sandbox had about 1.9 GB free).

AUTHORIZATION: this is defensive work on the owner's own gate: planting helpers that source banned vocabulary into throwaway gate
trees to prove the screen refuses them.

CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
`scripts/lane_context.sh -q 'how does the never-a-gate screen split shell commands and follow include edges' -s _command_segments -s _source_errors -s _import_errors -s _package_files -o /tmp/j10r4/pack.md scripts/no_laya_in_gates.py`.

## Report (`tasks/briefs/laya/J1-0-R4-report.md`)

PREMISE re-measured · per contract line R4-1..R4-6: files:lines and the tests that pin each · the member-trigger table (shape →
before → after) · the mutant table · the gates pasted · which issue #37 findings your change closes incidentally, with evidence ·
DISCREPANCIES · NOT-done. Lint floor: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/J1-0-R4-report.md --root .`
(full repo-relative paths, no `--map`); apply its `fix:` hints for at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 09:46Z, sandbox @ local 361b30c; origin b511e4a; scratch copy = `git archive HEAD`)
```
$ date -u; git rev-parse --short HEAD; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
Wed Sep 23 09:46:01 UTC 2026
361b30c
b511e4a
$ for f in <boundary>; do blob, lines; done; git diff --quiet HEAD -- <boundary>
18c3939889cf 653 scripts/no_laya_in_gates.py
55a9a43af463 655 tests/test_no_laya_in_gates.py
0d8edcdc9e92 50 scripts/gate_files.txt
tree == HEAD on the boundary
$ python3 scripts/no_laya_in_gates.py; python3 scripts/no_laya_in_gates.py --staged
no_laya_in_gates: 39 files scanned, clean
rc=0
no_laya_in_gates: 39 files scanned, clean
rc=0
$ pytest tests/test_no_laya_in_gates.py (x2) + set id
33 passed in 2.29s
33 passed in 2.77s
1 files set=e3695f80792b
$ the dynamic-load census over the listed Python gates (grep -nE "spec_from_file_location|SourceFileLoader|run_path|import_module|__import__|exec\(")
scripts/ap_screen.py:26:    spec = importlib.util.spec_from_file_location("es", ROOT / ".claude" / "hooks" / "edit-snapshot.py")
scripts/lint_delta.py:106:    spec = importlib.util.spec_from_file_location("edit_snapshot", hook)
scripts/proof-runner:39:    loader = importlib.machinery.SourceFileLoader("stage0_validate_ledger", str(path))
scripts/ledger-gen:17:    loader = importlib.machinery.SourceFileLoader("stage0_validate_ledger", str(path))
proofs/S0-02/check_buzz_authz.py:80:    spec = importlib.util.spec_from_file_location(name, path)
proofs/S0-03/check_omniroute_roundtrip.py:114:    spec = importlib.util.spec_from_file_location(_S0_01_MODULE_NAME, _S0_01_CHECKER)
proofs/S0-05/check_egress.py:122:    spec = importlib.util.spec_from_file_location(_PINS_MODULE, _PINS_FILE)
$ experiments on a scratch copy of HEAD (git archive HEAD)
BH: ". scripts/h.sh" after pc_lane.sh line 100 -> gate-file-sources: scripts/pc_lane.sh:101: scripts/h.sh rc=4
BH: ". scripts/h.sh" after pc_lane.sh line 400 -> no_laya_in_gates: 39 files scanned, clean rc=0
step-name line: 39
        env:
          S0_01_VENUE: ci   # the S0-01 real-leg corpus is a DECLARED input: CI 
        run: python -m pytest tests/ -q
      - name: Lint scripts
        run: python -m pyflakes scripts/validate-ledger scripts/proof-runner
      - name: Lint proofs and tests
        run: python -m pyflakes proofs/S0-01 tests/
YH-3 (sourcing step, no apostrophe) -> gate-file-sources: .github/workflows/stage0-ci.yml:48: scripts/h.sh rc=4
YH-4 (the same step + one apostrophe in the step name at line 39) -> no_laya_in_gates: 39 files scanned, clean rc=0
PyYAML parses YH-4: ['. scripts/h.sh']
$ listing .claude/hooks/edit-snapshot.py in a copy of gate_files.txt
no_laya_in_gates: 40 files scanned, clean
rc=0
$ the verifier five proposed tests against HEAD bytes (tests/test_vj10_red.py in the copy)
wrote 5 tests
FAILED test_vj10_red.py::test_vj10_nested_quote_heredoc_text_does_not_blind_the_scan
FAILED test_vj10_red.py::test_vj10_yaml_apostrophe_does_not_blind_the_scan - ...
FAILED test_vj10_red.py::test_vj10_scan_ending_inside_a_heredoc_fails_closed
FAILED test_vj10_red.py::test_vj10_dynamic_import_of_an_unlisted_file_is_refused
FAILED test_vj10_red.py::test_vj10_real_tree_lists_the_dynamically_loaded_helper
5 failed in 0.27s
```
The verifier measured the same five tests red at its PIN (`5 failed in 0.24s`); the census above (7 syntactic sites; the verifier's 8
counts `_load_by_path`'s two call targets at `proofs/S0-02/check_buzz_authz.py`) reads the working tree, where B9-R1 holds
`proofs/S0-02/check_buzz_authz.py` modified: read that site at the PIN (`git show <PIN>:proofs/S0-02/check_buzz_authz.py`).
