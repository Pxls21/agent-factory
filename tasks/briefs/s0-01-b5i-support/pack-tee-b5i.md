# lane context pack — e17278a 2026-09-07T23:12Z
files: proofs/S0-01/tools/frame_tee.py tests/test_s0_01_frame_tee.py
symbols: _kill_own_grandchild pump_pipe _write_status test_shutdown_prose_matches_the_pinned_source test_kill_calls_only_at_allowed_sites

## proofs/S0-01/tools/frame_tee.py
### graft skeleton

graft skeleton — proofs/S0-01/tools/frame_tee.py
- L56-L62  class _Terminated  class _Terminated(BaseException)
- L65-L70  function _sha256_file  def _sha256_file(path)
- L73-L75  function _utc_now  def _utc_now()
- L78-L98  function _read_lines_from_fd  def _read_lines_from_fd(fd)
- L101-L103  function _reject_nan_inf  def _reject_nan_inf(constant)
- L106-L111  function _reject_overflow_float  def _reject_overflow_float(s)
- L114-L478  function main  def main()
- L146-L162  function _record_write_error  def _record_write_error(arm, direction, error_text)
- L169-L207  function _write_status  def _write_status(final=False, exit_code_val=None, agent_rc=None)
- L218-L219  function _sigterm_handler  def _sigterm_handler(signum, _frame)
- L256-L338  function pump_fd  def pump_fd(fd, dst, direction, dir_path, close_dst)
- L340-L412  function pump_pipe  def pump_pipe(src, dst, direction, dir_path, close_dst)
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 12 hits over 1 files ---
AP-24: 4
    proofs/S0-01/tools/frame_tee.py:310: except Exception:
    proofs/S0-01/tools/frame_tee.py:318: except Exception:
    proofs/S0-01/tools/frame_tee.py:337: except Exception:
    proofs/S0-01/tools/frame_tee.py:411: except Exception:
AP-1: 3
    proofs/S0-01/tools/frame_tee.py:115: framedir = os.environ.get("S0_01_FRAMEDIR")
    proofs/S0-01/tools/frame_tee.py:125: agent = os.environ.get("S0_01_AGENT")
    proofs/S0-01/tools/frame_tee.py:246: "python_dont_write_bytecode": os.environ.get("PYTHONDONTWRITEBYTECODE") == "1",
AP-51: 2
    proofs/S0-01/tools/frame_tee.py:6: frames-client-to-agent.jsonl - byte-identical relay c2a
    proofs/S0-01/tools/frame_tee.py:7: frames-agent-to-client.jsonl - byte-identical relay a2c
AF-AP-55: 1
    proofs/S0-01/tools/frame_tee.py:231: interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
AF-AP-58: 1
    proofs/S0-01/tools/frame_tee.py:221: signal.signal(signal.SIGTERM, _sigterm_handler)
AP-32: 1
    proofs/S0-01/tools/frame_tee.py:66: h = hashlib.sha256()

## tests/test_s0_01_frame_tee.py
### graft skeleton

graft skeleton — tests/test_s0_01_frame_tee.py
- L84-L89  function _sha256_file  def _sha256_file(path)
- L92-L101  function _build_input  def _build_input()
- L104-L156  function _kill_own_grandchild  def _kill_own_grandchild(framedir)
- L159-L215  function _run_tee  def _run_tee(tmpdir, agent_code, input_bytes, env_extra=None, timeout=30)
- L219-L226  function tee_run  def tee_run(tmp_path_factory)
- L232-L261  class TestTimeline  class TestTimeline
- L233-L237  method test_seq_strictly_increasing  def test_seq_strictly_increasing(self, tee_run)
- L239-L241  method test_dir_values  def test_dir_values(self, tee_run)
- L243-L248  method test_has_t_utc_and_t_mono  def test_has_t_utc_and_t_mono(self, tee_run)
- L250-L253  method test_t_mono_non_decreasing  def test_t_mono_non_decreasing(self, tee_run)
- L255-L257  method test_c2a_count  def test_c2a_count(self, tee_run)
- L259-L261  method test_a2c_count  def test_a2c_count(self, tee_run)
- L265-L278  class TestNonJsonLine  class TestNonJsonLine
- L266-L271  method test_c2a_non_json  def test_c2a_non_json(self, tee_run)
- L273-L278  method test_a2c_non_json  def test_a2c_non_json(self, tee_run)
- L282-L287  class TestByteRelay  class TestByteRelay
- L283-L284  method test_c2a_relay  def test_c2a_relay(self, tee_run)
- L286-L287  method test_a2c_relay  def test_a2c_relay(self, tee_run)
- L291-L306  class TestDirectionalEqualsTimeline  class TestDirectionalEqualsTimeline
- L292-L300  method _timeline_split  def _timeline_split(self, tee_run, direction)
- L302-L303  method test_c2a_split  def test_c2a_split(self, tee_run)
- L305-L306  method test_a2c_split  def test_a2c_split(self, tee_run)
- L310-L342  class TestRuntimeIdentity  class TestRuntimeIdentity
- L311-L318  method test_has_all_keys  def test_has_all_keys(self, tee_run)
- L320-L321  method test_agent_sha256  def test_agent_sha256(self, tee_run)
- L323-L324  method test_tee_sha256  def test_tee_sha256(self, tee_run)
- L326-L327  method test_agent_argv  def test_agent_argv(self, tee_run)
- L329-L330  method test_python_dont_write_bytecode  def test_python_dont_write_bytecode(self, tee_run)
- L332-L334  method test_spawned_at_utc_format  def test_spawned_at_utc_format(self, tee_run)
- L336-L338  method test_agent_child_pid  def test_agent_child_pid(self, tee_run)
- L340-L342  method test_tee_pid  def test_tee_pid(self, tee_run)
- L346-L348  class TestExitCode  class TestExitCode
- L347-L348  method test_exit_code  def test_exit_code(self, tee_run)
- L352-L364  class TestSignalExitCode  class TestSignalExitCode
- L353-L364  method test_sigterm_agent_exit_143  def test_sigterm_agent_exit_143(self, tmp_path)
- L370-L531  class TestLateClientFrameRecorded  class TestLateClientFrameRecorded
- L371-L422  method test_late_client_frame_recorded_or_exit_70  def test_late_client_frame_recorded_or_exit_70(self, tmp_path)
- L424-L480  method test_late_frame_agent_stdin_closed_before_handshake  def test_late_frame_agent_stdin_closed_before_handshake(self, tmp_path)
- L482-L531  method test_agent_stdin_closed_before_handshake_exit_code  def test_agent_stdin_closed_before_handshake_exit_code(self, tmp_path)
- L535-L609  class TestGrandchildStdout  class TestGrandchildStdout
- L536-L609  method test_grandchild_keeps_tee_alive  def test_grandchild_keeps_tee_alive(self, tmp_path)
- L573-L577  function _drain  def _drain()
- L613-L643  class TestLockContention  class TestLockContention
- L614-L643  method test_seq_contiguous_and_mono_nondecreasing_under_contention  def test_seq_contiguous_and_mono_nondecreasing_under_contention(self, tmp_path)
- L647-L663  class TestLargeLineRoundTrip  class TestLargeLineRoundTrip
- L648-L663  method test_64kb_line_preserved  def test_64kb_line_preserved(self, tmp_path)
- L667-L673  class TestPartialLastLineC2A  class TestPartialLastLineC2A
- L668-L673  method test_c2a_partial_line_at_eof  def test_c2a_partial_line_at_eof(self, tmp_path)
- L676-L687  class TestPartialLastLine  class TestPartialLastLine
- L677-L687  method test_partial_line_at_eof  def test_partial_line_at_eof(self, tmp_path)
- L690-L702  class TestCrlfPreservation  class TestCrlfPreservation
- L691-L702  method test_crlf_line_byte_exact  def test_crlf_line_byte_exact(self, tmp_path)
- L706-L722  class TestBytecodeFlag  class TestBytecodeFlag
- L707-L710  method test_bytecode_true_when_set  def test_bytecode_true_when_set(self, tmp_path)
- L712-L722  method test_bytecode_false_when_unset  def test_bytecode_false_when_unset(self, tmp_path)
- L728-L741  class TestTimestampsAreReal  class TestTimestampsAreReal
- L729-L736  method test_t_utc_within_fixture_window  def test_t_utc_within_fixture_window(self, tee_run)
- L738-L741  method test_t_utc_increases  def test_t_utc_increases(self, tee_run)
- L745-L761  class TestMonoNsWindow  class TestMonoNsWindow
- L746-L761  method test_t_mono_ns_within_monotonic_window  def test_t_mono_ns_within_monotonic_window(self, tmp_path)
- L765-L787  class TestNanInfinityRawBranch  class TestNanInfinityRawBranch
- L766-L771  method test_nan_line_takes_raw_branch  def test_nan_line_takes_raw_branch(self, tmp_path)
- L773-L778  method test_infinity_line_takes_raw_branch  def test_infinity_line_takes_raw_branch(self, tmp_path)
- L780-L783  method test_neg_infinity_line_takes_raw_branch  def test_neg_infinity_line_takes_raw_branch(self, tmp_path)
- L785-L787  method test_nan_line_directional_file_byte_exact  def test_nan_line_directional_file_byte_exact(self, tmp_path)
- L790-L802  class TestMissingEnvVars  class TestMissingEnvVars
- L791-L795  method test_missing_framedir  def test_missing_framedir(self, tmp_path)
- L797-L802  method test_missing_agent  def test_missing_agent(self, tmp_path)
- L806-L826  class TestNonFiniteRawBranchWithOracle  class TestNonFiniteRawBranchWithOracle
- L808-L820  method test_both_directions_raw_and_oracle  def test_both_directions_raw_and_oracle(self, tmp_path, input_text)
- L816-L817  function _raise  def _raise(c)
- L822-L826  method test_normal_float_still_parsed  def test_normal_float_still_parsed(self, tmp_path)
- L832-L1299  class TestTeeStatus  class TestTeeStatus
- L833-L845  method test_normal_run_writes_status  def test_normal_run_writes_status(self, tee_run)
- L847-L850  method test_status_keys_exact  def test_status_keys_exact(self, tee_run)
- L852-L855  method test_status_keys_order_matches_pin  def test_status_keys_order_matches_pin(self, tee_run)
- L857-L904  method test_agent_burst_drained  def test_agent_burst_drained(self, tmp_path)
- L883-L887  function _drain  def _drain()
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-66: 1
    tests/test_s0_01_frame_tee.py:920: timer.daemon = True

## graft ask — which tests read tee_proc stdout or stderr without a deadline, and where does the tee record the interpreter identity
graft ask — "which tests read tee_proc stdout or stderr without a deadline, and where does the tee record the interpreter identity"  (lexical)

1. main · function  [symbol]
   proofs/S0-01/tools/acp_probe.py:L134-L459
   def main(): # Validate required env vars early with a named message (L15/A10: exit 64). # Empty/unset cases exit 64 WITHOUT probe_error because the try block (which # writes runtime-identity.json) has not started yet — this is a documented # exception: probe_error requires the wrapped body to have opened.

2. main · function  [symbol]
   proofs/S0-01/tools/frame_tee.py:L114-L478
   def main()

3. main · function  [symbol]
   proofs/S0-01/tools/build_capture_record.py:L45-L159
   def main() -> int

4. main · function  [symbol]
   proofs/S0-01/tools/pc/pc_launch.py:L80-L269
   def main()

5. _read_body · method  [symbol]
   proofs/S0-01/tools/scripted_backend.py:L633-L658
   def _read_body(self)

6. frame_tee_v1.py · file  [symbol]
   proofs/S0-01/tools/archive/frame_tee_v1.py

7. build_capture_record_v1.py · file  [symbol]
   proofs/S0-01/tools/archive/build_capture_record_v1.py

8. pc_negative.py · file  [symbol]
   proofs/S0-01/tools/pc/pc_negative.py

## symbol _kill_own_grandchild
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 4 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_frame_tee.py::_kill_own_grandchild')",
      "name": "test_grandchild_keeps_tee_alive",
      "name": "test_grandchild_never_closes_sigterm_required",
      "name": "test_concurrent_main_thread_status_vs_pump",
      "name": "test_zombie_grandchild_is_already_gone",
  "summary": "Found 4 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_frame_tee.py::_kill_own_grandchild')",
      "name": "test_grandchild_keeps_tee_alive",
      "name": "test_grandchild_never_closes_sigterm_required",
      "name": "test_concurrent_main_thread_status_vs_pump",
      "name": "test_zombie_grandchild_is_already_gone",
### ripwire callers
<callers of="_kill_own_grandchild" defs="1" count="4" root="/home/user/agent-factory" hop_tested="0" hop_untested="4" shown="4" capped="0" total="4" has_more="0" next_offset="4" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=_kill_own_grandchild">

## symbol pump_pipe
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/frame_tee.py::pump_pipe')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/frame_tee.py::pump_pipe')",
### ripwire callers
<callers of="pump_pipe" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=pump_pipe">

## symbol _write_status
### GitNexus impact (upstream)
  "impactedCount": 4,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 3,
    "processes_affected": 2,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 3 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/frame_tee.py::_write_status')",
      "name": "pump_fd",
      "name": "pump_pipe",
      "name": "main",
  "summary": "Found 2 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/frame_tee.py::_write_status')",
      "name": "test_write_status_snapshot_and_rewrite_are_locked",
      "name": "test_write_status_reads_no_state_outside_the_lock",
### ripwire callers
<callers of="_write_status" defs="1" count="3" root="/home/user/agent-factory" hop_tested="0" hop_untested="3" shown="3" capped="0" total="3" has_more="0" next_offset="3" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=_write_status">

## symbol test_shutdown_prose_matches_the_pinned_source
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_frame_tee.py::test_shutdown_prose_matches_the_pinned_source'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_frame_tee.py::test_shutdown_prose_matches_the_pinned_source'.",
### ripwire callers
<callers of="test_shutdown_prose_matches_the_pinned_source" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_shutdown_prose_matches_the_pinned_source">

## symbol test_kill_calls_only_at_allowed_sites
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_frame_tee.py::test_kill_calls_only_at_allowed_sites'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_frame_tee.py::test_kill_calls_only_at_allowed_sites'.",
### ripwire callers
<callers of="test_kill_calls_only_at_allowed_sites" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_kill_calls_only_at_allowed_sites">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
<test-gate changed="1" impacted="0" tests="0" untested="0" shown_tests="0" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="4" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="e17278a2e+dirty" next="--situ">
