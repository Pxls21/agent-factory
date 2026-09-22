# lane context pack — 4324757 2026-09-22T18:04Z
files: scripts/no_laya_in_gates.py
symbols: _glob_structural_staged _exists_staged _read_staged _parse_allowlist main

## scripts/no_laya_in_gates.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — scripts/no_laya_in_gates.py
- L56-L92  function _check_line  def _check_line(line, is_py)
- L97-L106  function _read_staged  def _read_staged(path)
- L109-L115  function _read_file  def _read_file(root, path)
- L120-L128  function _parse_allowlist  def _parse_allowlist(text)
- L131-L133  function _load_allowlist  def _load_allowlist(list_path)
- L136-L159  function _glob_structural  def _glob_structural(root)
- L162-L179  function _glob_structural_staged  def _glob_structural_staged()
- L182-L188  function _exists_staged  def _exists_staged(path)
- L193-L292  function main  def main()
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 7 hits over 1 files ---
AF-AP-40: 7
    scripts/no_laya_in_gates.py:141: if hooks_dir.is_dir():
    scripts/no_laya_in_gates.py:143: if p.is_file():
    scripts/no_laya_in_gates.py:147: if wf_dir.is_dir():
    scripts/no_laya_in_gates.py:149: if p.is_file():
    scripts/no_laya_in_gates.py:153: if proofs_dir.is_dir():
    scripts/no_laya_in_gates.py:155: if sub.is_dir():
    ... +1

## graft ask — In --staged mode, how do the allowlist read, the structural walk and the existence control resolve, and where can a git failure become an empty set or a silent skip?
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
graft ask — "In --staged mode, how do the allowlist read, the structural walk and the existence control resolve, and where can a git failure become an empty set or a silent skip?"  (lexical)

1. main · function  [symbol]
   scripts/no_laya_in_gates.py:L193-L292
   def main()

2. walk_tree · function  [symbol]
   scripts/vendored_manifest.py:L186-L221
   def walk_tree(root: Path, repo_root: Path | None) -> list[tuple[str, bytes]]

3. main · function  [symbol]
   scripts/lint_delta.py:L116-L158
   def main() -> int

4. _read_file · function  [symbol]
   scripts/report_lint.py:L50-L59
   def _read_file(path: str, rev: str | None, root: Path) -> list[str] | None

5. _git · function  [symbol]
   scripts/check-proof-status.py:L88-L92
   def _git(repo_root, *args, env=None, binary=False)

6. ooo_mcp.py · file  [symbol]
   scripts/ooo_mcp.py

7. gn_mcp.py · file  [symbol]
   scripts/gn_mcp.py

8. chat_tail.py · file  [symbol]
   scripts/chat_tail.py

## symbol _glob_structural_staged
### GitNexus impact (upstream)
  "impactedCount": 2,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/scripts/no_laya_in_gates.py::_glob_structural_staged')",
      "name": "main",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/scripts/no_laya_in_gates.py::_glob_structural_staged')",
### ripwire callers
<callers of="_glob_structural_staged" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="112" counts_floor="1" next="--uses=_glob_structural_staged">

## symbol _exists_staged
### GitNexus impact (upstream)
  "impactedCount": 2,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/scripts/no_laya_in_gates.py::_exists_staged')",
      "name": "main",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/scripts/no_laya_in_gates.py::_exists_staged')",
### ripwire callers
<callers of="_exists_staged" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="112" counts_floor="1" next="--uses=_exists_staged">

## symbol _read_staged
### GitNexus impact (upstream)
  "impactedCount": 2,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/scripts/no_laya_in_gates.py::_read_staged')",
      "name": "main",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/scripts/no_laya_in_gates.py::_read_staged')",
### ripwire callers
<callers of="_read_staged" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="112" counts_floor="1" next="--uses=_read_staged">

## symbol _parse_allowlist
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 2,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/scripts/no_laya_in_gates.py::_parse_allowlist')",
      "name": "_load_allowlist",
      "name": "main",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/scripts/no_laya_in_gates.py::_parse_allowlist')",
### ripwire callers
<callers of="_parse_allowlist" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="112" counts_floor="1" next="--uses=_parse_allowlist">

## symbol main
### GitNexus impact (upstream)
  "impactedCount": null,
  "risk": "UNKNOWN",
      "impactedCount": 2,
      "risk": "LOW",
      "direct": 1
      "impactedCount": 2,
      "risk": "LOW",
      "direct": 1
### code-review-graph callers_of / tests_for
  "summary": "Found 32 result(s) for callers_of('/home/user/agent-factory/scripts/no_laya_in_gates.py::main')",
      "name": "/home/user/agent-factory/scripts/no_laya_in_gates.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-logic-visualizer/tests/test_visualizer.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-news/tests/test_news.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-predictor/tests/test_predictor.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-reporter/tests/test_reporter.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-search/tests/test_search.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-sentiment/tests/test_sentiment.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-signal-tracker/tests/test_tracker.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-stock/tests/test_stock.py",
      "name": "test_output_file_written",
      "name": "/home/user/agent-factory/.agents/skills/exa-search/tests/test_exa_search.py",
  "summary": "Found 2 result(s) for tests_for('/home/user/agent-factory/scripts/no_laya_in_gates.py::main')",
      "name": "/home/user/agent-factory/sandbox-kit/codebase-memory-mcp/tests/test_main.c",
      "name": "test_main_orders_stop_post_and_masked_collection",
### ripwire callers
<callers of="main" defs="57" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="112" counts_floor="1" next="--uses=main">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
<test-gate changed="1" impacted="0" tests="0" untested="0" shown_tests="0" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="10" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="4324757ba+dirty" next="--situ">
