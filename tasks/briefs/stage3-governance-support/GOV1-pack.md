# lane context pack — fec185a 2026-09-15T13:32Z
files: proofs/S0-07/check_fubuki_corrections.py
symbols: _correct_lint_exit check_lint_ordering check_bound_decision_join check_hash_stability _add_fubuki

## proofs/S0-07/check_fubuki_corrections.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — proofs/S0-07/check_fubuki_corrections.py
- L22-L24  function _add_fubuki  def _add_fubuki(fubuki_root: Path)
- L27-L34  function _correct_lint_exit  def _correct_lint_exit(findings: list) -> int
- L37-L76  function check_lint_ordering  def check_lint_ordering(fubuki_root: Path) -> bool
- L79-L132  function check_bound_decision_join  def check_bound_decision_join(fubuki_root: Path) -> bool
- L135-L171  function check_hash_stability  def check_hash_stability(fubuki_root: Path) -> bool
- L174-L198  function lint_check_fixture  def lint_check_fixture(fixture_dir: Path, fubuki_root: Path) -> int
- L201-L231  function main  def main()
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## graft ask — how does the S0-07 checker consume the pinned fubuki-os: which functions it imports and calls for lint ordering, the BoundDecision join and hash stability, and what the corrected lint exit rule is
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
graft ask — "how does the S0-07 checker consume the pinned fubuki-os: which functions it imports and calls for lint ordering, the BoundDecision join and hash stability, and what the corrected lint exit rule is"  (lexical)

⚠ structural index: no entries for 'BoundDecision' — showing lexical matches; for precise edges try graft callers 'BoundDecision', or graft grep 'BoundDecision' for every reference (loosen the pattern if it returns nothing)

1. check_bound_decision_join · function  [symbol]
   proofs/S0-07/check_fubuki_corrections.py:L79-L132
   def check_bound_decision_join(fubuki_root: Path) -> bool

2. main · function  [symbol]
   proofs/S0-07/check_fubuki_corrections.py:L201-L231
   def main()

3. check_fubuki_corrections.py · file  [symbol]
   proofs/S0-07/check_fubuki_corrections.py

4. check_lint_ordering · function  [symbol]
   proofs/S0-07/check_fubuki_corrections.py:L37-L76
   def check_lint_ordering(fubuki_root: Path) -> bool

5. check_hash_stability · function  [symbol]
   proofs/S0-07/check_fubuki_corrections.py:L135-L171
   def check_hash_stability(fubuki_root: Path) -> bool

6. lint_check_fixture · function  [symbol]
   proofs/S0-07/check_fubuki_corrections.py:L174-L198
   def lint_check_fixture(fixture_dir: Path, fubuki_root: Path) -> int

7. _correct_lint_exit · function  [symbol]
   proofs/S0-07/check_fubuki_corrections.py:L27-L34
   def _correct_lint_exit(findings: list) -> int

8. _add_fubuki · function  [symbol]
   proofs/S0-07/check_fubuki_corrections.py:L22-L24
   def _add_fubuki(fubuki_root: Path)

## symbol _correct_lint_exit
### GitNexus impact (upstream)
  "impactedCount": 4,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 2,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/proofs/S0-07/check_fubuki_corrections.py::_correct_lint_exit')",
      "name": "check_lint_ordering",
      "name": "lint_check_fixture",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-07/check_fubuki_corrections.py::_correct_lint_exit')",
### ripwire callers
<callers of="_correct_lint_exit" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_correct_lint_exit">

## symbol check_lint_ordering
### GitNexus impact (upstream)
  "impactedCount": 2,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-07/check_fubuki_corrections.py::check_lint_ordering')",
      "name": "main",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-07/check_fubuki_corrections.py::check_lint_ordering')",
### ripwire callers
<callers of="check_lint_ordering" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=check_lint_ordering">

## symbol check_bound_decision_join
### GitNexus impact (upstream)
  "impactedCount": 2,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-07/check_fubuki_corrections.py::check_bound_decision_join')",
      "name": "main",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-07/check_fubuki_corrections.py::check_bound_decision_join')",
### ripwire callers
<callers of="check_bound_decision_join" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=check_bound_decision_join">

## symbol check_hash_stability
### GitNexus impact (upstream)
  "impactedCount": 2,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-07/check_fubuki_corrections.py::check_hash_stability')",
      "name": "main",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-07/check_fubuki_corrections.py::check_hash_stability')",
### ripwire callers
<callers of="check_hash_stability" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=check_hash_stability">

## symbol _add_fubuki
### GitNexus impact (upstream)
  "impactedCount": 6,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 4,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 4 result(s) for callers_of('/home/user/agent-factory/proofs/S0-07/check_fubuki_corrections.py::_add_fubuki')",
      "name": "check_lint_ordering",
      "name": "check_bound_decision_join",
      "name": "check_hash_stability",
      "name": "lint_check_fixture",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-07/check_fubuki_corrections.py::_add_fubuki')",
### ripwire callers
<callers of="_add_fubuki" defs="1" count="4" root="/home/user/agent-factory" hop_tested="0" hop_untested="4" shown="4" capped="0" total="4" has_more="0" next_offset="4" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_add_fubuki">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
<test-gate changed="1" impacted="0" tests="0" untested="0" shown_tests="0" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="8" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="fec185a3e+dirty" next="--situ">
