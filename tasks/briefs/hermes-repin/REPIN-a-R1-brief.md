# REPIN-a-R1 — the ONE focused repair of VERIFY-REPIN-a (the Hermes lane-runtime pin's tests and its `verified:` field) (task #169)

PIN: 1978e55 (origin head at authoring; the three boundary files are byte-identical to HEAD, measured below).
LANE: repin-a-r1 (sandbox; agent `code-implementer` on the D-054 pin, in the SHARED tree, no worktree isolation). Honey `ultra`
Lever-2: your report is DATA — files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

CONTRACT SOURCES (read them whole before you design): `tasks/briefs/hermes-repin/REPIN-brief.md` §REPIN-a (the original contract) ·
`tasks/briefs/hermes-repin/VERIFY-REPIN-a-report.md` §8 (F1, F2, F3 with their fix lines; §2-§3 hold the G1-G7, K and T mutants by
value) · `docs/08_DECISION_LOG.md` D-048 item 3 (the owner ruling: "the harness-ports compatibility suite on the PC and the lanes'
record since 2026-09-08") · the coordinator's F4 decision and PC measurements in `todo/BUILD-TASKLIST.md` (the note "F4 DECIDED;
D-048's PC COMPATIBILITY RUN DONE") · `tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md` (the lane count, measured on the PC).

BOUNDARY (exact): MODIFY `tests/test_upstream_lock_lane_runtime.py` (T) · `upstream.lock.yaml` (L: the `verified:` value of
`lane_runtime.hermes-agent-lane-runtime` ONLY — every other byte of L stays; the key set stays closed) · `docs/HARNESS-PORTS.md`
(H: §12 "Lane runtime pin" only). CREATE `tasks/briefs/hermes-repin/REPIN-a-R1-report.md` (write it incrementally from the start).
READ-ONLY: everything else, including `scripts/vendored_manifest.py` (a live PC lane owns it), `tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md`
(the coordinator's evidence), `.claude/`, `.github/`, `scripts/`. A line you cannot meet inside the boundary is a DISCREPANCY, never a
silent edit. Other sandbox agents work in this tree on disjoint files (`proofs/S0-02/`, `proofs/S0-05/`, their tests,
`tasks/briefs/s0-02-support/`, `tasks/briefs/s0-05-support/`, `tasks/briefs/laya/`) and one in `/tmp/wt-ci166`: never touch, run or revert
them. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push`. No outward-facing action; no PC
or bridge use. The sandbox has about 1.7 GB free: every pytest `--basetemp` lives under `/tmp/rr1/` and is removed after each run.

CODE INTEL FIRST: `graft ask` before any grep for code questions; `scripts/lane_context.sh -q 'how is the lane-runtime pin tested'
-s _load_lock -s test_hermes_agent_entry_unchanged -s test_short_commit_rejected -o /tmp/rr1/pack.md tests/test_upstream_lock_lane_runtime.py upstream.lock.yaml`.

## The contract (build to it; the HOW is yours)

R1 (F1 — the golden is the entry's LINES). T reads L's raw text. Exactly one line equals `  hermes-agent:` (two spaces, the name, a
colon, nothing after it), and it sits under `selected_core:`; the entry is that line through the line before the next line that starts
with exactly two spaces and a non-space (or the next top-level key). Those lines equal a golden list of the six committed lines
(pasted in the premise, `cat -A` shows no trailing whitespace) byte for byte. Keep the parsed-dict comparison as a second view. The
failure message names the first differing line. VERIFY-REPIN-a's G1-G7 (a trailing space, a re-indent, quoting, key reorder, a
comment, a duplicate `commit:`) each go RED by name; G8 stays red.

R2 (F2 — a live negative control). ONE helper decides whether a lock's lane-runtime commit is valid, and raises with the exact text
`commit is not 40 lowercase hex: <value>`; the positive test calls it on L as committed. The control writes a copy of L with the
lane-runtime commit replaced, loads it through the SAME loader function the positive test uses, and asserts the named failure with
`pytest.raises(..., match=...)` for each of: `b3399c1` (7 hex), 39 hex, 41 hex, 40 uppercase hex, a YAML integer. No regex copy in the
control. Mutants T1 (the helper's pattern weakened) and T2 (the helper's check removed) each go RED.

R3 (F3 + F4 — `verified:` says what each piece proves). The value becomes ONE string that records, in this order and in these words
or plainer: (a) "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: all
suites passed, rc 0, 2026-09-23 09:08Z (binary-free by its header)"; (b) "identity probe 2026-09-23 08:58Z: b3399c1, Hermes Agent
v0.21.1, venv Python 3.11.15, SQLite 3.53.1, shared state.db WAL"; (c) "110 PC lanes first launched after 2026-09-08 14:22Z (98 with a
report), tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md". Every number in it is copied from the premise below or the lane record,
never typed from memory. T asserts the exact committed value.

R4 (F7 — every value pinned). T asserts the whole expected dict of `hermes-agent-lane-runtime` (all eight keys' exact values), so a
change to `python`, `role`, `reason` or `diff_from_proof_pin` goes red by name.

R5 (F5 — §12 says what is NOT enforced). H §12 gains one sentence: until REPIN-b lands, nothing reads `lane_runtime`, so a `hermes
update` or a `HERMES_BIN` override moves the lanes with no check failing. Nothing else in H changes.

## Tests and mutants

Every contract line has a test that is RED on the PIN bytes (paste the RED run) and GREEN after. The mutation table (scratch copies
only; each mutant compiles — `py_compile` — and its suite collects, AF-AP-78; run the killer on the UNMUTATED tree first and paste that
it passes, AF-AP-138): G1-G7 (on a scratch copy of L), T1, T2, plus R4's four value mutants and one per R3 piece (a changed digit in
each number). One row each: mutant · compiles · collected · killed-by / SURVIVED / EQUIVALENT with the reason.

## Gates (paste every command with its output)

`mkdir -p /tmp/rr1/bt && bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py --basetemp /tmp/rr1/bt` TWICE, identical
counts (`rm -rf /tmp/rr1/bt` between; the premise floor is `8 passed`, set bbc177a039e2 — your count grows by your tests) ·
`bash scripts/test_summary.sh tests/test_s0_12_license_sbom.py` (S0-12 reads L) · `python3 scripts/vendored_manifest.py --check` (the pin
agreement reads L) · `python3 scripts/validate-ledger integrity --root .` (no INVALID) · `bash scripts/verify-planning-repo.sh` ·
`/root/venv-agent-factory/bin/python -m pyflakes tests/test_upstream_lock_lane_runtime.py` · `python3 scripts/ap_screen.py --tests
tests/test_upstream_lock_lane_runtime.py` (new hits only) · `python3 scripts/no_laya_in_gates.py`.

## Report (`tasks/briefs/hermes-repin/REPIN-a-R1-report.md`)

PREMISE re-measured · per contract line R1-R5: files:lines and the tests that pin it · RED then GREEN (pasted) · the mutant table ·
the gates · DISCREPANCIES · NOT-done (F6 is REPIN-b's; F8 and F10 are issue #36's). Lint floor: `python3 scripts/report_lint.py
--min-refs 10 --map T=tests/test_upstream_lock_lane_runtime.py --map L=upstream.lock.yaml --map H=docs/HARNESS-PORTS.md
tasks/briefs/hermes-repin/REPIN-a-R1-report.md --root .`; apply its `fix:` hints for at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 09:14Z, sandbox @ 1978e55)
```
$ date -u; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
Wed Sep 23 09:14:12 UTC 2026
1978e55
$ git log --format="%h %s" -3 -- upstream.lock.yaml tests/test_upstream_lock_lane_runtime.py docs/HARNESS-PORTS.md | cut -c1-110
433d15e T92 landed (GATED-PENDING-VERIFY): per-lane cloned Hermes profiles without the fallback chain, the lan
6406750 PCJ1 graded: the Laya System One endpoint lands (GATED-PENDING-VERIFY); the pruner is NOT wired into l
905bb1d REPIN-a: the formal Hermes LANE-runtime pin (D-043 -> D-048 item 3) — upstream.lock.yaml lane_runtim
$ for f in <boundary>; do sha256 of HEAD blob, lines; done
529261bd7488126f   173 upstream.lock.yaml
b663bcd87b960cff   121 tests/test_upstream_lock_lane_runtime.py
3d90882e2d58fe43   743 docs/HARNESS-PORTS.md
$ git diff --quiet HEAD -- <boundary> && echo "tree == HEAD on the boundary"
tree == HEAD on the boundary
$ grep -n "^  hermes-agent:$" upstream.lock.yaml; grep -c "^  hermes-agent:" upstream.lock.yaml
10:  hermes-agent:
1
$ sed -n "10,15p" upstream.lock.yaml | cat -A   (the six committed lines of selected_core.hermes-agent; $ = end of line)
  hermes-agent:$
    repository: https://github.com/NousResearch/hermes-agent.git$
    commit: 527da60844d4dced37879ea50259675371abe10e$
    observed_version: 0.21.0$
    license: MIT$
    role: main_production_workhorse_and_native_acp_server$
$ sed -n "164,173p" upstream.lock.yaml
lane_runtime:
  hermes-agent-lane-runtime:
    commit: b3399c139624a0081d70397741a5b45f60fbe1f4
    version: "0.21.1"
    python: "3.11.15"
    sqlite: "3.53.1"
    role: "lane-runtime (scripts/pc_lane.sh -> hermes on the PC); NOT the S0-01 proof runtime"
    reason: "SQLite >= 3.51.3 for WAL on the shared profile state.db (VERIFY-B5j); owner-run hermes update 2026-09-08"
    diff_from_proof_pin: "31816 commits, 3939 files"
    verified: "harness-ports/tests/run-all.sh (sandbox) + 43 PC-lane HOME/LANDED notes since 2026-09-08 14:2xZ"
$ grep -n "^def \|HERMES_AGENT_GOLDEN\|b3399c1\|re.fullmatch\|safe_load" tests/test_upstream_lock_lane_runtime.py
18:HERMES_AGENT_GOLDEN = {
27:LANE_RUNTIME_COMMIT = "b3399c139624a0081d70397741a5b45f60fbe1f4"
34:def _load_lock():
35:    return yaml.safe_load(LOCK_PATH.read_text(encoding="utf-8"))
40:def test_lane_runtime_entry_exists():
49:def test_lane_runtime_has_exact_keys():
60:def test_lane_runtime_commit_is_40_hex():
64:    assert re.fullmatch(r"[0-9a-f]{40}", commit), (
69:def test_lane_runtime_commit_value():
78:def test_lane_runtime_version():
85:def test_lane_runtime_sqlite():
92:def test_hermes_agent_entry_unchanged():
99:    assert entry == HERMES_AGENT_GOLDEN, (
106:def test_short_commit_rejected(tmp_path):
113:    lock["lane_runtime"]["hermes-agent-lane-runtime"]["commit"] = "b3399c1"
116:    mutated = yaml.safe_load(mutated_path.read_text(encoding="utf-8"))
119:    assert not re.fullmatch(r"[0-9a-f]{40}", str(commit)), (
$ grep -n "Lane runtime pin\|REPIN-b\|What this pin covers" docs/HARNESS-PORTS.md
728:## 12. Lane runtime pin
734:**What this pin covers:** every `scripts/pc_lane.sh` dispatch on the PC, where
742:**Drift check (REPIN-b, pending):** `scripts/pc_lane.sh` will read the pinned commit from
$ mkdir -p /tmp/rr1p && bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py --basetemp /tmp/rr1p/bt   (x2)
pytest-summary: 8 passed in 0.16s
pytest-summary: 8 passed in 0.13s
$ bash scripts/pc_suite.sh set-id -- tests/test_upstream_lock_lane_runtime.py
1 files set=bbc177a039e2
$ python3 scripts/vendored_manifest.py --check | tail -1; python3 scripts/validate-ledger integrity --root . | grep -c INVALID
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
0
$ the builder grep behind verified: (REPIN-a-report.md) and its count at HEAD
44:## Verified: lane count (pasted from grep, not typed)
48:grep -E '(HOME|LANDED)' todo/BUILD-TASKLIST.md | grep -iE '(PC|hermes|Qwen|local-Qwen)' \
49:  | grep -oE '[A-Za-z0-9_][A-Za-z0-9_-]* (HOME|LANDED) 2026-09-(08 1[4-9]|08 2[0-3]|0[9]|1[0-9]|2[0-2])' \
$ bash scripts/pc.sh <run-all.sh on the PC in a git clone at 2ebd486, AF_VENV=$HOME/venv-agent-factory>   (coordinator, 09:07-09:08Z; the result lines)
AF_VENV=/home/rocco/venv-agent-factory python3=Python 3.13.11
ALL SUITES PASSED
rc=0
end=2026-09-23T09:08:58Z
$ <the read-only identity probe on the PC, 08:58Z>
$ git -C ~/.hermes/hermes-agent rev-parse HEAD; log -1 --format=%cI
b3399c139624a0081d70397741a5b45f60fbe1f4
2026-09-08T14:05:24Z
$ readlink -f ~/.local/bin/hermes
/home/rocco/.local/bin/hermes
$ ~/.local/bin/hermes --version
Hermes Agent v0.21.1 (2026.9.7) · upstream b3399c13
Install directory: /home/rocco/.hermes/hermes-agent
Install method: git
$ venv python + sqlite versions
3.11.15 3.53.1
$ journal_mode of the shared agentfactory state.db (read-only connection)
wal
$ git -C ~/s0-01-pinned/hermes-agent rev-parse --short HEAD
527da60
2026-09-23T08:58:34Z
$ <the lane record, 09:14Z: tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md, summary>
lanes=110 with_report=98 failed_marker=4
```
