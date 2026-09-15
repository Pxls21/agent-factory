# lane context pack — 97bb0c0 2026-09-15T13:05Z
files: proofs/S0-01/tools/acp_probe.py tests/test_s0_01_acp_probe.py
symbols: _read_regular _open_regular _framedir_flags_from_probe_source test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd test_probe_agent_launch_pins_the_close_fds_default_second_defence

## proofs/S0-01/tools/acp_probe.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — proofs/S0-01/tools/acp_probe.py
- L48-L78  function _read_regular  def _read_regular(path, mode="rb")
- L81-L92  function _sha256_file  def _sha256_file(path): # N5h-#7 (class): every file the probe reads must be a REGULAR file — open() on a # FIFO blocks forever and a character device (/dev/zero) never reaches EOF. # N5k round 14: the classification now happens on the FD after one open # (_read_regular), never on the pathname before it — one guard covers all # three receivers of this function: the probe's own file, the agent # entrypoint, the child interpreter.
- L95-L128  function _open_regular  def _open_regular(name, mode, *, dir_fd=None, display_path=None)
- L148-L150  function _utc_now  def _utc_now()
- L153-L168  function _drain_stderr  def _drain_stderr(proc, stderr_name, error_slot, *, framedir_fd, display_path)
- L171-L183  function _redact_env  def _redact_env(env)
- L186-L192  function _leaf_handle  def _leaf_handle(framedir_fd, framedir, name, mode)
- L195-L200  function _write_env  def _write_env(framedir, framedir_fd)
- L203-L250  function _write_evidence  def _write_evidence(framedir, framedir_fd, timeline, agent, agent_realpath, child_pid, interp_realpath, interp_sha256, spawned_at_utc, agent_exit_code, probe_error)
- L253-L673  function main  def main(): # Validate required env vars early with a named message (L15/A10: exit 64). # Empty/unset cases exit 64 WITHOUT probe_error because the try block (which # writes runtime-identity.json) has not started yet — this is a documented # exception: probe_error requires the wrapped body to have opened.
- L645-L650  function _m3_write  def _m3_write(name, text)
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 8 hits over 1 files ---
AF-AP-55: 3
    proofs/S0-01/tools/acp_probe.py:392: candidate = os.readlink("/proc/%d/exe" % proc.pid)
    proofs/S0-01/tools/acp_probe.py:468: interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
    proofs/S0-01/tools/acp_probe.py:559: interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
AP-1: 2
    proofs/S0-01/tools/acp_probe.py:259: v = os.environ.get(k)
    proofs/S0-01/tools/acp_probe.py:338: timeout_raw = os.environ.get("ACP_PROBE_TIMEOUT", "30")
AP-32: 2
    proofs/S0-01/tools/acp_probe.py:88: h = hashlib.sha256()
    proofs/S0-01/tools/acp_probe.py:179: "sha256_12": hashlib.sha256(v.encode("utf-8")).hexdigest()[:12],
AP-24: 1
    proofs/S0-01/tools/acp_probe.py:573: except Exception:

## tests/test_s0_01_acp_probe.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — tests/test_s0_01_acp_probe.py
- L38-L64  function agent_result  def agent_result(tmp_path)
- L68-L89  function agent_error  def agent_error(tmp_path)
- L93-L104  function agent_silent  def agent_silent(tmp_path)
- L108-L136  function agent_stderr_heavy  def agent_stderr_heavy(tmp_path)
- L140-L153  function agent_partial_line  def agent_partial_line(tmp_path)
- L157-L187  function agent_notification_then_response  def agent_notification_then_response(tmp_path)
- L191-L220  function agent_non_json  def agent_non_json(tmp_path)
- L224-L235  function agent_sigterm  def agent_sigterm(tmp_path)
- L238-L253  function _run_probe  def _run_probe(tmp_path, agent, timeout_override=None, extra_env=None)
- L258-L301  function test_probe_result_response_and_check_initialize  def test_probe_result_response_and_check_initialize(tmp_path, agent_result)
- L304-L317  function test_probe_error_response  def test_probe_error_response(tmp_path, agent_error)
- L320-L333  function test_probe_never_answers  def test_probe_never_answers(tmp_path, agent_silent)
- L336-L349  function test_probe_stderr_heavy_no_deadlock  def test_probe_stderr_heavy_no_deadlock(tmp_path, agent_stderr_heavy)
- L352-L370  function test_probe_env_json_redaction  def test_probe_env_json_redaction(tmp_path, agent_result)
- L375-L390  function test_probe_partial_line_completes  def test_probe_partial_line_completes(tmp_path, agent_partial_line)
- L395-L409  function test_probe_notification_then_response  def test_probe_notification_then_response(tmp_path, agent_notification_then_response)
- L414-L424  function test_probe_spawned_at_precedes_first_frame  def test_probe_spawned_at_precedes_first_frame(tmp_path, agent_result)
- L429-L445  function test_probe_bad_agent_path_writes_probe_error  def test_probe_bad_agent_path_writes_probe_error(tmp_path)
- L450-L459  function test_probe_sigterm_killed_agent_exit_code  def test_probe_sigterm_killed_agent_exit_code(tmp_path, agent_sigterm)
- L464-L478  function test_probe_bytecode_false_when_unset  def test_probe_bytecode_false_when_unset(tmp_path, agent_result)
- L483-L492  function test_probe_error_surfaces_on_exception  def test_probe_error_surfaces_on_exception(tmp_path)
- L497-L510  function test_probe_non_json_a2c_line  def test_probe_non_json_a2c_line(tmp_path, agent_non_json)
- L515-L580  function test_probe_broken_pipe_deterministic  def test_probe_broken_pipe_deterministic(tmp_path, agent_result)
- L585-L589  function test_probe_timeout_nan_exits_64  def test_probe_timeout_nan_exits_64(tmp_path, agent_result)
- L592-L596  function test_probe_timeout_negative_exits_64  def test_probe_timeout_negative_exits_64(tmp_path, agent_result)
- L599-L603  function test_probe_timeout_infinity_exits_64  def test_probe_timeout_infinity_exits_64(tmp_path, agent_result)
- L606-L610  function test_probe_timeout_non_numeric_exits_64  def test_probe_timeout_non_numeric_exits_64(tmp_path, agent_result)
- L613-L617  function test_probe_timeout_zero_exits_64  def test_probe_timeout_zero_exits_64(tmp_path, agent_result)
- L620-L624  function test_probe_timeout_space_exits_64  def test_probe_timeout_space_exits_64(tmp_path, agent_result)
- L627-L631  function test_probe_timeout_empty_string_exits_64  def test_probe_timeout_empty_string_exits_64(tmp_path, agent_result)
- L636-L647  function test_probe_c2a_params_match_fixture  def test_probe_c2a_params_match_fixture(tmp_path, agent_result)
- L652-L668  function test_probe_interpreter_fields_pinned  def test_probe_interpreter_fields_pinned(tmp_path, agent_result)
- L673-L683  function test_probe_missing_framedir_exits_64  def test_probe_missing_framedir_exits_64()
- L686-L696  function test_probe_missing_agent_exits_64  def test_probe_missing_agent_exits_64(tmp_path)
- L701-L708  function test_probe_timeout_nan_writes_probe_error  def test_probe_timeout_nan_writes_probe_error(tmp_path, agent_result)
- L711-L718  function test_probe_timeout_negative_writes_probe_error  def test_probe_timeout_negative_writes_probe_error(tmp_path, agent_result)
- L721-L728  function test_probe_timeout_abc_writes_probe_error  def test_probe_timeout_abc_writes_probe_error(tmp_path, agent_result)
- L733-L748  function test_probe_empty_framedir_exits_64_no_probe_error  def test_probe_empty_framedir_exits_64_no_probe_error(tmp_path)
- L751-L765  function test_probe_framedir_is_file_exits_64  def test_probe_framedir_is_file_exits_64(tmp_path, agent_result)
- L770-L792  function test_probe_interpreter_is_child_not_self  def test_probe_interpreter_is_child_not_self(tmp_path)
- L797-L810  function test_probe_spawned_at_two_sided  def test_probe_spawned_at_two_sided(tmp_path, agent_result)
- L815-L914  function test_probe_identity_fields_all_pinned  def test_probe_identity_fields_all_pinned(tmp_path)
- L919-L935  function test_probe_creates_absent_framedir  def test_probe_creates_absent_framedir(tmp_path, agent_result)
- L940-L951  function test_probe_empty_agent_exits_64  def test_probe_empty_agent_exits_64(tmp_path)
- L956-L977  function test_probe_env_redaction_all_alternatives  def test_probe_env_redaction_all_alternatives(tmp_path, agent_result)
- L982-L1021  function test_probe_interpreter_sample_failure  def test_probe_interpreter_sample_failure(tmp_path, agent_result)
- L1026-L1044  function test_probe_agent_exits_without_output_keeps_interpreter_identity  def test_probe_agent_exits_without_output_keeps_interpreter_identity(tmp_path)
- L1047-L1124  function test_probe_interpreter_sample_failure_after_child_exit  def test_probe_interpreter_sample_failure_after_child_exit(tmp_path)
- L1130-L1170  function test_probe_fast_exit_agent_is_deterministic  def test_probe_fast_exit_agent_is_deterministic(tmp_path)
- L1173-L1273  function test_probe_post_loop_sha256_failure_truthful_error  def test_probe_post_loop_sha256_failure_truthful_error(tmp_path)
- L1276-L1337  function test_probe_self_deleting_script_is_probe_error_not_traceback  def test_probe_self_deleting_script_is_probe_error_not_traceback(tmp_path)
- L1340-L1400  function test_probe_broken_pipe_post_loop_placement  def test_probe_broken_pipe_post_loop_placement(tmp_path, agent_result)
- L1403-L1499  function test_probe_early_retry_recovers_from_transient_readlink_failure  def test_probe_early_retry_recovers_from_transient_readlink_failure(tmp_path, agent_result)
- L1505-L1549  function test_probe_interpreter_is_the_final_exec_not_a_wrapper  def test_probe_interpreter_is_the_final_exec_not_a_wrapper(tmp_path)
- L1552-L1614  function test_probe_env_shebang_interpreter_is_constant  def test_probe_env_shebang_interpreter_is_constant(tmp_path)
- L1620-L1695  function test_probe_early_sample_loop_bound_is_pinned  def test_probe_early_sample_loop_bound_is_pinned(tmp_path, agent_result)
- L1701-L1772  function test_probe_late_sample_clears_early_interpreter_error  def test_probe_late_sample_clears_early_interpreter_error(tmp_path, agent_result)
- L1778-L1827  function test_probe_m3_handler_writes_complete_evidence  def test_probe_m3_handler_writes_complete_evidence(tmp_path, agent_result)
- L1833-L1899  function test_probe_late_readlink_failure_keeps_the_early_reading  def test_probe_late_readlink_failure_keeps_the_early_reading(tmp_path, agent_result)
- L1905-L1926  function test_probe_interpreter_is_child_not_self_for_a_silent_agent  def test_probe_interpreter_is_child_not_self_for_a_silent_agent(tmp_path)
- L1932-L2042  function test_probe_interpreter_is_sampled_once_at_the_first_a2c_byte  def test_probe_interpreter_is_sampled_once_at_the_first_a2c_byte(tmp_path)
- L2048-L2126  function test_probe_interpreter_deleted_after_start_is_a_loud_probe_error  def test_probe_interpreter_deleted_after_start_is_a_loud_probe_error(tmp_path)
- L2135-L2147  function _probe_tree_copy  def _probe_tree_copy(tmp_path)
- L2152-L2189  function test_probe_refuses_a_non_regular_fixture  def test_probe_refuses_a_non_regular_fixture(tmp_path, agent_result)
- L2192-L2223  function test_sha256_file_refuses_a_non_regular_file  def test_sha256_file_refuses_a_non_regular_file(tmp_path)
- L2232-L2269  function test_probe_reports_a_stderr_drain_failure  def test_probe_reports_a_stderr_drain_failure(tmp_path, agent_result, kind, exc_name, err)
- L2280-L2310  function test_probe_keeps_raw_b64_when_a_byte_was_replaced  def test_probe_keeps_raw_b64_when_a_byte_was_replaced(tmp_path)
- L2313-L2322  function test_probe_clean_utf8_line_carries_no_raw_b64  def test_probe_clean_utf8_line_carries_no_raw_b64(tmp_path, agent_result)
- L2327-L2346  function test_probe_redaction_pattern_equals_the_pin  def test_probe_redaction_pattern_equals_the_pin()
- L2376-L2390  function test_probe_timeout_rejects_forms_outside_the_domain  def test_probe_timeout_rejects_forms_outside_the_domain(tmp_path, agent_result, raw, expected)
- L2394-L2399  function test_probe_timeout_accepts_the_domain  def test_probe_timeout_accepts_the_domain(tmp_path, agent_result, raw)
- L2420-L2464  function test_identity_records_the_runtime_bytecode_state_not_the_string  def test_identity_records_the_runtime_bytecode_state_not_the_string( tmp_path, agent_result, value, dash_b, force_m3)
- L2469-L2477  function _hostile_env  def _hostile_env(agent, framedir, timeout="5")
- L2481-L2507  function test_probe_evidence_writes_refuse_a_non_regular_path  def test_probe_evidence_writes_refuse_a_non_regular_path(tmp_path, agent_result, target)
- L2510-L2535  function test_probe_timeout_reject_write_refuses_a_non_regular_path  def test_probe_timeout_reject_write_refuses_a_non_regular_path(tmp_path, agent_result)
- L2541-L2607  function test_probe_survives_its_own_file_being_replaced_mid_run  def test_probe_survives_its_own_file_being_replaced_mid_run(tmp_path, agent_result, also_break_env)
- L2610-L2663  function test_probe_unreadable_own_file_is_named_not_a_traceback  def test_probe_unreadable_own_file_is_named_not_a_traceback(tmp_path, agent_result)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 1 hits over 1 files ---
AF-AP-57: 1
    tests/test_s0_01_acp_probe.py:1443: if _rl_calls[0] <= 3:

## graft ask — how does the probe read files through _read_regular and write through _open_regular; which tests pin the read flags, the close_fds Popen block and the framedir open flags; where is the isolated census test
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
graft ask — "how does the probe read files through _read_regular and write through _open_regular; which tests pin the read flags, the close_fds Popen block and the framedir open flags; where is the isolated census test"  (lexical)

1. _open_regular · function  [symbol]
   proofs/S0-01/tools/acp_probe.py:L95-L128
   def _open_regular(name, mode, *, dir_fd=None, display_path=None)

2. _refuse_non_regular · function  [symbol]
   proofs/S0-01/tools/scripted_backend.py:L394-L411
   def _refuse_non_regular(path: Path) -> bool

3. main · function  [symbol]
   proofs/S0-01/tools/pc/pc_launch.py:L281-L425
   def main()

4. pump_fd · function  [symbol]
   proofs/S0-01/tools/frame_tee.py:L339-L421
   def pump_fd(fd, dst, direction, dir_path, close_dst)

5. main · function  [symbol]
   proofs/S0-01/tools/pc/pc_negative.py:L19-L50
   def main()

6. main · function  [symbol]
   proofs/S0-01/tools/build_capture_record.py:L48-L217
   def main() -> int

7. pump · function  [symbol]
   proofs/S0-01/tools/archive/frame_tee_v1.py:L7-L20
   def pump(src, dst, path, close_dst)

8. main · function  [symbol]
   proofs/S0-01/tools/archive/build_capture_record_v1.py:L43-L101
   def main() -> int

## symbol _read_regular
### GitNexus impact (upstream)
  "impactedCount": 4,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 2,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::_read_regular')",
      "name": "_sha256_file",
      "name": "main",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::_read_regular')",
### ripwire callers
<callers of="_read_regular" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_read_regular">

## symbol _open_regular
### GitNexus impact (upstream)
  "impactedCount": 7,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 2,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::_open_regular')",
      "name": "_drain_stderr",
      "name": "_leaf_handle",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::_open_regular')",
### ripwire callers
<callers of="_open_regular" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_open_regular">

## symbol _framedir_flags_from_probe_source
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_acp_probe.py::_framedir_flags_from_probe_source')",
      "name": "test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd",
      "name": "test_probe_agent_launch_pins_the_close_fds_default_second_defence",
  "summary": "Found 2 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_acp_probe.py::_framedir_flags_from_probe_source')",
      "name": "test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd",
      "name": "test_probe_agent_launch_pins_the_close_fds_default_second_defence",
### ripwire callers
<callers of="_framedir_flags_from_probe_source" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_framedir_flags_from_probe_source">

## symbol test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_acp_probe.py::test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd')",
  "summary": "Found 2 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_acp_probe.py::test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd')",
      "name": "test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd",
      "name": "test_probe_agent_launch_pins_the_close_fds_default_second_defence",
### ripwire callers
<callers of="test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd">

## symbol test_probe_agent_launch_pins_the_close_fds_default_second_defence
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_acp_probe.py::test_probe_agent_launch_pins_the_close_fds_default_second_defence')",
  "summary": "Found 2 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_acp_probe.py::test_probe_agent_launch_pins_the_close_fds_default_second_defence')",
      "name": "test_probe_cloexec_is_load_bearing_child_sees_no_framedir_fd",
      "name": "test_probe_agent_launch_pins_the_close_fds_default_second_defence",
### ripwire callers
<callers of="test_probe_agent_launch_pins_the_close_fds_default_second_defence" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_probe_agent_launch_pins_the_close_fds_default_second_defence">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
<test-gate changed="1" impacted="0" tests="0" untested="0" shown_tests="0" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="8" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="97bb0c01f+dirty" next="--situ">
