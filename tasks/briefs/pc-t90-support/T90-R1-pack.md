# lane context pack — 5b37468 2026-09-22T12:52Z
files: scripts/pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh
symbols: _premise_block_ok bridge die

## scripts/pc_lane.sh
### graft skeleton
graft skeleton — scripts/pc_lane.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## harness-ports/tests/test_pc_lane_dispatcher.sh
### graft skeleton
graft skeleton — harness-ports/tests/test_pc_lane_dispatcher.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-44: 1
    harness-ports/tests/test_pc_lane_dispatcher.sh:82: run_gate() { # run_gate <brief> [ENV=VAL ...] --  (sets GATE_RC; stderr in $TMP/err.txt, calls in $B

## graft ask — how does the dispatcher decide RESUME vs FIRST, make its private self-copy, validate the premise block, and compute the provider-mix window; where do the liveness-bound probe, the fail-closed copy, the non-space line count and the lane launch time go
graft ask — "how does the dispatcher decide RESUME vs FIRST, make its private self-copy, validate the premise block, and compute the provider-mix window; where do the liveness-bound probe, the fail-closed copy, the non-space line count and the lane launch time go"  (lexical)

1. chat_tail.py · file  [symbol]
   scripts/chat_tail.py

2. validate_declared_roots · function  [symbol]
   scripts/vendored_manifest.py:L342-L360
   def validate_declared_roots(root: Path) -> None

3. check · function  [symbol]
   scripts/check-proof-status.py:L200-L300
   def check(repo_root, anchors=True, warnings=None)

4. pc_bridge_exec.py · file  [symbol]
   scripts/pc_bridge_exec.py

5. report_lint.py · file  [symbol]
   scripts/report_lint.py

6. ooo_mcp.py · file  [symbol]
   scripts/ooo_mcp.py

7. _drive · function  [symbol]
   scripts/gn_mcp.py:L27-L65
   def _drive(requests, want_id=2, timeout=120)

8. ap_screen.py · file  [symbol]
   scripts/ap_screen.py

## symbol _premise_block_ok
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/scripts/pc_lane.sh::_premise_block_ok')",
      "name": "/home/user/agent-factory/scripts/pc_lane.sh",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/scripts/pc_lane.sh::_premise_block_ok')",
### ripwire callers
<callers of="_premise_block_ok" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="107" counts_floor="1" next="--uses=_premise_block_ok">

## symbol bridge
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "'bridge' matches 45 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "/home/user/agent-factory/harness-ports/tests/test_bridge_token_handling.py",
      "name": "/home/user/agent-factory/harness-ports/tests/test_pc_bridge_exec.py",
      "name": "Stub",
      "name": "do_POST",
      "name": "log_message",
      "name": "_run",
      "name": "_serve",
      "name": "main",
      "name": "/home/user/agent-factory/sandbox-kit/aleph/aleph/mcp/node_bridge.py",
      "name": "_get_callable",
      "name": "_get_helper",
  "summary": "'bridge' matches 45 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "/home/user/agent-factory/harness-ports/tests/test_bridge_token_handling.py",
      "name": "/home/user/agent-factory/harness-ports/tests/test_pc_bridge_exec.py",
      "name": "Stub",
      "name": "do_POST",
      "name": "log_message",
      "name": "_run",
      "name": "_serve",
      "name": "main",
      "name": "/home/user/agent-factory/sandbox-kit/aleph/aleph/mcp/node_bridge.py",
      "name": "_get_callable",
      "name": "_get_helper",
### ripwire callers
<callers of="bridge" defs="3" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="107" counts_floor="1" next="--uses=bridge">

## symbol die
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "'die' matches 17 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
  "summary": "'die' matches 17 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
      "name": "die",
### ripwire callers
<callers of="die" defs="8" count="8" root="/home/user/agent-factory" hop_tested="0" hop_untested="8" shown="8" capped="0" total="8" has_more="0" next_offset="8" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="107" counts_floor="1" next="--uses=die">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
<test-gate changed="1" impacted="0" tests="0" untested="0" shown_tests="0" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="10" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="5b3746862+dirty" next="--situ">
