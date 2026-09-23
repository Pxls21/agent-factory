# VERIFY-REPIN-a-R1 — the targeted adversarial verify of the one focused repair of the Hermes lane-runtime pin (task #173)

PIN: the post-push SHA of the local landing commit 2f46cc6 ("REPIN-a-R1 landed (task #169) …"); the dispatch prompt names it.
Read it with `git log --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf -8` and match the subject.
COMPONENT: `tests/test_upstream_lock_lane_runtime.py` (T, 16 tests) · `upstream.lock.yaml` (L: the `verified:` value at line 173 and
the six `selected_core.hermes-agent` lines 10-15) · `docs/HARNESS-PORTS.md` (H: §12, the added sentence). The builder's report
`tasks/briefs/hermes-repin/REPIN-a-R1-report.md` and the coordinator's evidence `tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md`
are INPUTS TO ATTACK, not truths.
CONTRACT (frozen): `tasks/briefs/hermes-repin/REPIN-a-R1-brief.md` R1-R5 (the one focused repair of VERIFY-REPIN-a, D-031) +
`tasks/briefs/hermes-repin/REPIN-brief.md` §REPIN-a + D-048 item 3 (`docs/08_DECISION_LOG.md`). The coordinator accepted the
builder's discrepancy D1 ("at or after 14:22:00Z", the record's `-ge` count): attack whether it is TRUE, not whether it matches
the brief's older words.
ROLE: adversarial-verifier (sandbox, the D-054 pin). READ-ONLY on the tree: mutate scratch copies only (`/tmp/vrr1/`), never the
shared files. No bridge or PC use: the PC-side numbers are attacked by CONSISTENCY against the committed record and the committed
dispatcher code, never re-measured.
BOUNDARY: CREATE `tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md` (write it incrementally from the start); nothing else.
Other sandbox agents work in this tree on disjoint files (`proofs/S0-02/`, `proofs/S0-05/`, their tests, `tasks/briefs/s0-02-support/`,
`tasks/briefs/s0-05-support/`, `tasks/briefs/ci/`, `scripts/no_laya_in_gates.py`, `tests/test_no_laya_in_gates.py`,
`scripts/gate_files.txt`, `tasks/briefs/laya/`): never touch, run or revert them. `scripts/vendored_manifest.py` belongs to a live PC
lane: read it, never edit it. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push`. No
outward-facing action. Do NOT spawn subagents. Every pytest `--basetemp` lives under `/tmp/vrr1/` and is removed after the run
(the sandbox has about 1.6 GB free).
CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack: `scripts/lane_context.sh -q 'how is the lane-runtime pin
tested and who reads it' -s _hermes_agent_entry -s _check_lane_runtime_commit -s parse_lock -o /tmp/vrr1/pack.md
tests/test_upstream_lock_lane_runtime.py upstream.lock.yaml scripts/vendored_manifest.py`.

## Items (report EVERY observation; no severity filter; rank downstream)

1. PREMISE. Re-measure the block below on the PIN (identities, the run, the set id, the six lines, line 173). A mismatch that
   changes an item is CONTRACT-INVALID for that item; say which.
2. R1, the line golden (`_hermes_agent_entry`, `test_hermes_agent_entry_lines_golden`). Attack it with NEW shapes, never the builder's
   G1-G7: a `  # comment` line at the two-space indent placed INSIDE the entry and placed right AFTER it; a blank line inside the
   entry; a three-space re-indent of one child; a quoted head `  "hermes-agent":` added as a SECOND key later in `selected_core:`
   (PyYAML keeps the last duplicate — which view catches it, and is a same-valued duplicate an equivalent mutant?); a BOM at the
   file start; a CRLF file; the entry moved under another top-level key. For each: which test goes red, by which message, or it
   survives. Does the parsed-dict view (`test_hermes_agent_entry_unchanged`) still hold its own weight?
3. R2, the live control (`_check_lane_runtime_commit`, `test_bad_lane_runtime_commit_rejected`). New shapes through the SAME loader:
   an empty value (`commit:`), `null`, a quoted 40-hex with a trailing space inside the quotes, a 40-hex with a leading `0x`-free
   octal-looking all-digit string that YAML reads as an int, a YAML list, a value that YAML reads as a float. Is every rejection by
   the named message? Is there any 40-character value that PASSES the helper and is not a real 40-lowercase-hex string?
4. The lane_runtime entry itself. Is a DUPLICATE key inside `hermes-agent-lane-runtime` (two `commit:` lines, the second the pinned
   value) refused by any test? PyYAML keeps the last; a line reader that keeps the first (the planned REPIN-b drift check, or any
   `grep -m1`) would read the other. Is a key REORDER inside the entry pinned by anything, and is it in contract (R4 names values,
   not order)? Report what survives; decide in-contract or not with the contract line.
5. Consumers, with TWO instruments named in the report (graft + a grep; AF-AP rule for reachability claims). H §12 now says "nothing
   reads `lane_runtime`". A literal grep for `lane_runtime` is blind to a GENERIC reader: `scripts/vendored_manifest.py` `parse_lock`
   walks every section of L line by line. Does the lane-runtime entry reach `parse_lock`'s returned map (it has no `repository:`)?
   What would one added `repository:` line in it do to the `hermes-agent` pin agreement in `validate_pin_agreement` (a later entry
   with the same repository key)? Is the closed key set (`test_lane_runtime_has_exact_keys`) the only guard? Is §12's sentence TRUE
   at the PIN, and is it complete?
6. R3, the `verified:` value, piece by piece, against the record and the committed dispatcher:
   a. "110 PC lanes … (98 with a report)": recount from the record's table (rows, the `report` column, the `FAILED` column) and
      state the count of rows with no report. Does the record's own script print the numbers it claims (its counters live inside a
      pipeline)? Say where 110/98/4 came from.
   b. "first launched": the record reads the mtime of a lane's `prompt.md`. Read `harness-ports/bin/pc-lane.sh` (the `PROMPT_FILE`
      lines): is `prompt.md` truncated and rewritten on a relaunch of the same lane directory? If yes, the mtime is the LAST launch,
      and a lane first launched before 14:22Z and relaunched after it is counted — did it then run on b3399c1 (say why or why not),
      and is "first launched" the right word?
   c. "with a report": the record counts a NON-EMPTY `report.md`. Read how pc-lane.sh writes `report.md` and what it does with a
      refusal line, a `No reply:` line, a FAILED lane and a PARTIAL draft: can a non-empty `report.md` be something other than a
      lane's final report?
   d. "harness-ports/tests/run-all.sh on the PC … (binary-free by its header)": read the header of `harness-ports/tests/run-all.sh`.
      If the suite never runs the Hermes binary, what does its pass prove about the lane runtime b3399c1? Does the value, §12 or the
      ledger overclaim it? Is the value's word order such that a reader could take the run-all pass as a test OF b3399c1?
   e. The identity probe piece and D-043/D-048's recorded facts (b3399c1, v0.21.1, Python 3.11.15, SQLite 3.53.1, WAL): any
      contradiction between L, H §12, the ledger note "F4 DECIDED; D-048's PC COMPATIBILITY RUN DONE" in `todo/BUILD-TASKLIST.md`,
      `docs/08_DECISION_LOG.md` and CLAUDE.md is a finding.
7. R4 and R5. Does T assert all eight values by name (`LANE_RUNTIME_EXPECTED`)? The §12 test is a whitespace-normalized SUBSTRING
   check: does a negated sentence around it ("It is false that …"), or a contradicting sentence elsewhere in §12 ("REPIN-b has
   landed; the drift check runs"), stay green? Is that a presence pin with no behavioral pair (AF-AP-80's class), and is there any
   behavioral pair possible for prose?
8. The F1-class sibling (outside the component; the coordinator's UNSURE from grading): `tests/test_s0_01_pc_tools.py:1106`
   `assert set(s0_01) == set(pins.PINNED_ENV_KEYS)  # default byte-identical to today` — the comment and the docstring say the
   default `s0-01` launch env is byte-identical to the pre-extension launcher; the assert compares key SETS. Does any other test pin
   the default env's VALUES (a golden)? If none, is this a real hollow claim (a changed value stays green), and what is the minimal
   killing test? Sweep for more siblings of the class "the message or comment claims byte identity, the assert compares a
   projection" in `tests/` (report each; never fix).
9. MUTANTS (new ones, never the builder's 28 rows). On scratch copies of T and L: at least these, each compiled (`py_compile`) and
   collected (AF-AP-78), the killer run on the UNMUTATED copy first (AF-AP-138): M1 the head test loosened to `line.strip() ==
   "hermes-agent:"`; M2 the `selected_core:` parent assert removed; M3 the end regex narrowed to `r"  \S"`; M4 `re.fullmatch` →
   `re.match` in the helper; M5 the `isinstance(commit, str)` guard removed; M6 the §12 test's heading match loosened to
   `startswith("## 12")`; plus any your items 2-7 suggest. One row each: mutant · compiles · collected · killed-by / SURVIVED /
   EQUIVALENT with the reason.
10. Gates (paste each command with its output): T TWICE with identical counts (`bash scripts/test_summary.sh
    tests/test_upstream_lock_lane_runtime.py --basetemp /tmp/vrr1/bt`, `rm -rf` between); `bash scripts/test_summary.sh
    tests/test_s0_12_license_sbom.py`; `python3 scripts/vendored_manifest.py --check`; `python3 scripts/validate-ledger integrity
    --root .`; `bash scripts/verify-planning-repo.sh`; report lint on the BUILDER's report: `python3 scripts/report_lint.py
    --min-refs 10 --map T=tests/test_upstream_lock_lane_runtime.py --map L=upstream.lock.yaml --map H=docs/HARNESS-PORTS.md
    tasks/briefs/hermes-repin/REPIN-a-R1-report.md --root .`.

## Output

`tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md`: every observation with file:line, SOLID/UNSURE, and its reproduction;
the mutant table; the GATE RECOMMENDATION (`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) with the
blocking predicate applied per finding (contract-mapped to R1-R5 or the frozen REPIN-a contract · reproduced through the real test
path · materially effective · a concrete discriminator · in-boundary). Non-blocking findings are listed as follow-ups with a one-line
fix each. Lint your own report: `python3 scripts/report_lint.py --min-refs 12 --map T=tests/test_upstream_lock_lane_runtime.py
--map L=upstream.lock.yaml --map H=docs/HARNESS-PORTS.md --map P=harness-ports/bin/pc-lane.sh --map V=scripts/vendored_manifest.py
tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md --root .` (apply its `fix:` hints for at most three rounds, then paste and finish).

## PREMISE — MEASURED at authoring (2026-09-23 10:0xZ, sandbox @ 2f46cc6, the local landing commit; origin at 3846636)

The component at HEAD equals the working tree; the three component files changed only in 2f46cc6 since origin. T collects 16 tests
and passes twice. The six `hermes-agent` lines carry no trailing whitespace. The literal grep for `lane_runtime` finds no reader
outside T; `parse_lock` reads every section generically (item 5's question). `prompt.md` is truncated at every pc-lane.sh start
(item 6b's question). The record's table has 110 rows: 98 `report`, 12 without; 4 `FAILED` (a 111th date-led line is prose, the
Rule's second line).

````
$ date -u; git rev-parse --short HEAD; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
Wed Sep 23 10:06:15 UTC 2026
2f46cc6
3846636

$ git diff --stat 3846636 2f46cc6
 docs/HARNESS-PORTS.md                          |   2 +
 tasks/briefs/hermes-repin/REPIN-a-R1-report.md | 454 +++++++++++++++++++++++++
 tests/test_upstream_lock_lane_runtime.py       | 188 ++++++++--
 todo/BUILD-TASKLIST.md                         |   1 +
 upstream.lock.yaml                             |   2 +-
 5 files changed, 618 insertions(+), 29 deletions(-)

$ for f in …; do echo "$(git rev-parse --short=12 HEAD:$f) $(git show HEAD:$f | wc -l) $f"; done
0e64aba8ea20 253 tests/test_upstream_lock_lane_runtime.py
65b0f05ef43a 173 upstream.lock.yaml
ee9ff9b5efd6 745 docs/HARNESS-PORTS.md
5725e15a885d 148 tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md
6fd845c863b1 454 tasks/briefs/hermes-repin/REPIN-a-R1-report.md
$ git diff --quiet HEAD -- tests/test_upstream_lock_lane_runtime.py upstream.lock.yaml docs/HARNESS-PORTS.md; echo rc=$?
rc=0

$ sed -n 10,15p upstream.lock.yaml | cat -A     (the six golden lines; `$` = end of line)
  hermes-agent:$
    repository: https://github.com/NousResearch/hermes-agent.git$
    commit: 527da60844d4dced37879ea50259675371abe10e$
    observed_version: 0.21.0$
    license: MIT$
    role: main_production_workhorse_and_native_acp_server$

$ sed -n 164,173p upstream.lock.yaml
lane_runtime:
  hermes-agent-lane-runtime:
    commit: b3399c139624a0081d70397741a5b45f60fbe1f4
    version: "0.21.1"
    python: "3.11.15"
    sqlite: "3.53.1"
    role: "lane-runtime (scripts/pc_lane.sh -> hermes on the PC); NOT the S0-01 proof runtime"
    reason: "SQLite >= 3.51.3 for WAL on the shared profile state.db (VERIFY-B5j); owner-run hermes update 2026-09-08"
    diff_from_proof_pin: "31816 commits, 3939 files"
    verified: "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: all suites passed, rc 0, 2026-09-23 09:08Z (binary-free by its header); identity probe 2026-09-23 08:58Z: b3399c1, Hermes Agent v0.21.1, venv Python 3.11.15, SQLite 3.53.1, shared state.db WAL; 110 PC lanes first launched at or after 2026-09-08 14:22:00Z (98 with a report), tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md"

$ grep -n '^def ' tests/test_upstream_lock_lane_runtime.py
81:def _load_lock(path=LOCK_PATH):
85:def _check_lane_runtime_commit(lock):
93:def _hermes_agent_entry(text):
118:def test_lane_runtime_entry_exists():
127:def test_lane_runtime_has_exact_keys():
138:def test_lane_runtime_commit_is_40_hex():
143:def test_lane_runtime_commit_value():
152:def test_lane_runtime_version():
159:def test_lane_runtime_sqlite():
166:def test_lane_runtime_entry_values():
177:def test_lane_runtime_verified_value():
185:def test_hermes_agent_entry_unchanged():
200:def test_hermes_agent_entry_lines_golden():
213:def test_harness_ports_section_12_says_the_pin_is_unenforced():
238:def test_bad_lane_runtime_commit_rejected(tmp_path, raw, loaded):

$ for i in 1 2; do rm -rf /tmp/vrr1/bt; bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py --basetemp /tmp/vrr1/bt | tail -1; done
pytest-summary: 16 passed in 0.17s
pytest-summary: 16 passed in 0.19s
$ bash scripts/pc_suite.sh set-id -- tests/test_upstream_lock_lane_runtime.py
1 files set=bbc177a039e2

$ grep -n '## 12\.' docs/HARNESS-PORTS.md; sed -n 737,738p docs/HARNESS-PORTS.md
728:## 12. Lane runtime pin
Until REPIN-b lands, nothing reads `lane_runtime`, so a `hermes update` or a `HERMES_BIN`
override moves the lanes with no check failing.

$ grep -rn lane_runtime scripts proofs tests harness-ports .github src --include=*.py --include=*.sh --include=*.yml --include=*.yaml | grep -v '^tests/test_upstream_lock_lane_runtime.py'
(no output)

$ sed -n 598,621p scripts/vendored_manifest.py   (parse_lock: every section, then only entries with repository AND a pin)
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            section = line[:-1]
…
    for name, values in entries.items():
        pin = values.get("commit") or values.get("binary_sha256") or values.get("asset_sha256")
        repository = values.get("repository")
        if repository and pin:
            parsed[normalize_repo(repository)] = (pin, values["key"])

$ sed -n 217,218p harness-ports/bin/pc-lane.sh
PROMPT_FILE="$LANE_DIR/prompt.md"
: > "$PROMPT_FILE"

$ grep -cE '^2026-09-[0-9]{2}T' tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md
111
$ grep -E '^2026-09-[0-9]{2}T' tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md | awk '{print $2}' | sort | uniq -c
     12 -
     98 report
      1 the
$ grep -E '^2026-09-[0-9]{2}T' tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md | awk '{print $3}' | sort | uniq -c
    106 -
      4 FAILED
      1 owner's

$ sed -n 1104,1106p tests/test_s0_01_pc_tools.py   (item 8)
    s0_01 = pc_launch.launch_env(*base_args, env_set="s0-01")
    s0_02 = pc_launch.launch_env(*base_args, env_set="s0-02")
    assert set(s0_01) == set(pins.PINNED_ENV_KEYS)            # default byte-identical to today
````
