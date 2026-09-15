# lane context pack — efde78d 2026-09-15T15:11Z
files: proofs/S0-01/tools/acp_probe.py tests/test_s0_01_acp_probe.py
symbols: _read_regular _run_probe _sha256_file _write_evidence _leaf_handle main

## proofs/S0-01/tools/acp_probe.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
[graft] refreshed the graph (2 files changed) before answering

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
- L253-L674  function main  def main(): # Validate required env vars early with a named message (L15/A10: exit 64). # Empty/unset cases exit 64 WITHOUT probe_error because the try block (which # writes runtime-identity.json) has not started yet — this is a documented # exception: probe_error requires the wrapped body to have opened.
- L646-L651  function _m3_write  def _m3_write(name, text)
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 8 hits over 1 files ---
AF-AP-55: 3
    proofs/S0-01/tools/acp_probe.py:393: candidate = os.readlink("/proc/%d/exe" % proc.pid)
    proofs/S0-01/tools/acp_probe.py:469: interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
    proofs/S0-01/tools/acp_probe.py:560: interp_realpath = os.readlink("/proc/%d/exe" % proc.pid)
AP-1: 2
    proofs/S0-01/tools/acp_probe.py:259: v = os.environ.get(k)
    proofs/S0-01/tools/acp_probe.py:338: timeout_raw = os.environ.get("ACP_PROBE_TIMEOUT", "30")
AP-32: 2
    proofs/S0-01/tools/acp_probe.py:88: h = hashlib.sha256()
    proofs/S0-01/tools/acp_probe.py:179: "sha256_12": hashlib.sha256(v.encode("utf-8")).hexdigest()[:12],
AP-24: 1
    proofs/S0-01/tools/acp_probe.py:574: except Exception:

## tests/test_s0_01_acp_probe.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — tests/test_s0_01_acp_probe.py
- L39-L65  function agent_result  def agent_result(tmp_path)
- L69-L90  function agent_error  def agent_error(tmp_path)
- L94-L105  function agent_silent  def agent_silent(tmp_path)
- L109-L137  function agent_stderr_heavy  def agent_stderr_heavy(tmp_path)
- L141-L154  function agent_partial_line  def agent_partial_line(tmp_path)
- L158-L188  function agent_notification_then_response  def agent_notification_then_response(tmp_path)
- L192-L221  function agent_non_json  def agent_non_json(tmp_path)
- L225-L236  function agent_sigterm  def agent_sigterm(tmp_path)
- L239-L254  function _run_probe  def _run_probe(tmp_path, agent, timeout_override=None, extra_env=None)
- L257-L258  function _short_unix_socket_path  def _short_unix_socket_path()
- L263-L306  function test_probe_result_response_and_check_initialize  def test_probe_result_response_and_check_initialize(tmp_path, agent_result)
- L309-L322  function test_probe_error_response  def test_probe_error_response(tmp_path, agent_error)
- L325-L338  function test_probe_never_answers  def test_probe_never_answers(tmp_path, agent_silent)
- L341-L354  function test_probe_stderr_heavy_no_deadlock  def test_probe_stderr_heavy_no_deadlock(tmp_path, agent_stderr_heavy)
- L357-L375  function test_probe_env_json_redaction  def test_probe_env_json_redaction(tmp_path, agent_result)
- L380-L395  function test_probe_partial_line_completes  def test_probe_partial_line_completes(tmp_path, agent_partial_line)
- L400-L414  function test_probe_notification_then_response  def test_probe_notification_then_response(tmp_path, agent_notification_then_response)
- L419-L429  function test_probe_spawned_at_precedes_first_frame  def test_probe_spawned_at_precedes_first_frame(tmp_path, agent_result)
- L434-L450  function test_probe_bad_agent_path_writes_probe_error  def test_probe_bad_agent_path_writes_probe_error(tmp_path)
- L455-L464  function test_probe_sigterm_killed_agent_exit_code  def test_probe_sigterm_killed_agent_exit_code(tmp_path, agent_sigterm)
- L469-L483  function test_probe_bytecode_false_when_unset  def test_probe_bytecode_false_when_unset(tmp_path, agent_result)
- L488-L497  function test_probe_error_surfaces_on_exception  def test_probe_error_surfaces_on_exception(tmp_path)
- L502-L515  function test_probe_non_json_a2c_line  def test_probe_non_json_a2c_line(tmp_path, agent_non_json)
- L520-L585  function test_probe_broken_pipe_deterministic  def test_probe_broken_pipe_deterministic(tmp_path, agent_result)
- L590-L594  function test_probe_timeout_nan_exits_64  def test_probe_timeout_nan_exits_64(tmp_path, agent_result)
- L597-L601  function test_probe_timeout_negative_exits_64  def test_probe_timeout_negative_exits_64(tmp_path, agent_result)
- L604-L608  function test_probe_timeout_infinity_exits_64  def test_probe_timeout_infinity_exits_64(tmp_path, agent_result)
- L611-L615  function test_probe_timeout_non_numeric_exits_64  def test_probe_timeout_non_numeric_exits_64(tmp_path, agent_result)
- L618-L622  function test_probe_timeout_zero_exits_64  def test_probe_timeout_zero_exits_64(tmp_path, agent_result)
- L625-L629  function test_probe_timeout_space_exits_64  def test_probe_timeout_space_exits_64(tmp_path, agent_result)
- L632-L636  function test_probe_timeout_empty_string_exits_64  def test_probe_timeout_empty_string_exits_64(tmp_path, agent_result)
- L641-L652  function test_probe_c2a_params_match_fixture  def test_probe_c2a_params_match_fixture(tmp_path, agent_result)
- L657-L673  function test_probe_interpreter_fields_pinned  def test_probe_interpreter_fields_pinned(tmp_path, agent_result)
- L678-L688  function test_probe_missing_framedir_exits_64  def test_probe_missing_framedir_exits_64()
- L691-L701  function test_probe_missing_agent_exits_64  def test_probe_missing_agent_exits_64(tmp_path)
- L706-L713  function test_probe_timeout_nan_writes_probe_error  def test_probe_timeout_nan_writes_probe_error(tmp_path, agent_result)
- L716-L723  function test_probe_timeout_negative_writes_probe_error  def test_probe_timeout_negative_writes_probe_error(tmp_path, agent_result)
- L726-L733  function test_probe_timeout_abc_writes_probe_error  def test_probe_timeout_abc_writes_probe_error(tmp_path, agent_result)
- L738-L753  function test_probe_empty_framedir_exits_64_no_probe_error  def test_probe_empty_framedir_exits_64_no_probe_error(tmp_path)
- L756-L770  function test_probe_framedir_is_file_exits_64  def test_probe_framedir_is_file_exits_64(tmp_path, agent_result)
- L775-L797  function test_probe_interpreter_is_child_not_self  def test_probe_interpreter_is_child_not_self(tmp_path)
- L802-L815  function test_probe_spawned_at_two_sided  def test_probe_spawned_at_two_sided(tmp_path, agent_result)
- L820-L919  function test_probe_identity_fields_all_pinned  def test_probe_identity_fields_all_pinned(tmp_path)
- L924-L940  function test_probe_creates_absent_framedir  def test_probe_creates_absent_framedir(tmp_path, agent_result)
- L945-L956  function test_probe_empty_agent_exits_64  def test_probe_empty_agent_exits_64(tmp_path)
- L961-L982  function test_probe_env_redaction_all_alternatives  def test_probe_env_redaction_all_alternatives(tmp_path, agent_result)
- L987-L1026  function test_probe_interpreter_sample_failure  def test_probe_interpreter_sample_failure(tmp_path, agent_result)
- L1031-L1049  function test_probe_agent_exits_without_output_keeps_interpreter_identity  def test_probe_agent_exits_without_output_keeps_interpreter_identity(tmp_path)
- L1052-L1129  function test_probe_interpreter_sample_failure_after_child_exit  def test_probe_interpreter_sample_failure_after_child_exit(tmp_path)
- L1135-L1175  function test_probe_fast_exit_agent_is_deterministic  def test_probe_fast_exit_agent_is_deterministic(tmp_path)
- L1178-L1278  function test_probe_post_loop_sha256_failure_truthful_error  def test_probe_post_loop_sha256_failure_truthful_error(tmp_path)
- L1281-L1342  function test_probe_self_deleting_script_is_probe_error_not_traceback  def test_probe_self_deleting_script_is_probe_error_not_traceback(tmp_path)
- L1345-L1405  function test_probe_broken_pipe_post_loop_placement  def test_probe_broken_pipe_post_loop_placement(tmp_path, agent_result)
- L1408-L1504  function test_probe_early_retry_recovers_from_transient_readlink_failure  def test_probe_early_retry_recovers_from_transient_readlink_failure(tmp_path, agent_result)
- L1510-L1554  function test_probe_interpreter_is_the_final_exec_not_a_wrapper  def test_probe_interpreter_is_the_final_exec_not_a_wrapper(tmp_path)
- L1557-L1619  function test_probe_env_shebang_interpreter_is_constant  def test_probe_env_shebang_interpreter_is_constant(tmp_path)
- L1625-L1700  function test_probe_early_sample_loop_bound_is_pinned  def test_probe_early_sample_loop_bound_is_pinned(tmp_path, agent_result)
- L1706-L1777  function test_probe_late_sample_clears_early_interpreter_error  def test_probe_late_sample_clears_early_interpreter_error(tmp_path, agent_result)
- L1783-L1832  function test_probe_m3_handler_writes_complete_evidence  def test_probe_m3_handler_writes_complete_evidence(tmp_path, agent_result)
- L1838-L1904  function test_probe_late_readlink_failure_keeps_the_early_reading  def test_probe_late_readlink_failure_keeps_the_early_reading(tmp_path, agent_result)
- L1910-L1931  function test_probe_interpreter_is_child_not_self_for_a_silent_agent  def test_probe_interpreter_is_child_not_self_for_a_silent_agent(tmp_path)
- L1937-L2047  function test_probe_interpreter_is_sampled_once_at_the_first_a2c_byte  def test_probe_interpreter_is_sampled_once_at_the_first_a2c_byte(tmp_path)
- L2053-L2131  function test_probe_interpreter_deleted_after_start_is_a_loud_probe_error  def test_probe_interpreter_deleted_after_start_is_a_loud_probe_error(tmp_path)
- L2140-L2152  function _probe_tree_copy  def _probe_tree_copy(tmp_path)
- L2157-L2194  function test_probe_refuses_a_non_regular_fixture  def test_probe_refuses_a_non_regular_fixture(tmp_path, agent_result)
- L2197-L2228  function test_sha256_file_refuses_a_non_regular_file  def test_sha256_file_refuses_a_non_regular_file(tmp_path)
- L2237-L2274  function test_probe_reports_a_stderr_drain_failure  def test_probe_reports_a_stderr_drain_failure(tmp_path, agent_result, kind, exc_name, err)
- L2285-L2315  function test_probe_keeps_raw_b64_when_a_byte_was_replaced  def test_probe_keeps_raw_b64_when_a_byte_was_replaced(tmp_path)
- L2318-L2327  function test_probe_clean_utf8_line_carries_no_raw_b64  def test_probe_clean_utf8_line_carries_no_raw_b64(tmp_path, agent_result)
- L2332-L2351  function test_probe_redaction_pattern_equals_the_pin  def test_probe_redaction_pattern_equals_the_pin()
- L2381-L2395  function test_probe_timeout_rejects_forms_outside_the_domain  def test_probe_timeout_rejects_forms_outside_the_domain(tmp_path, agent_result, raw, expected)
- L2399-L2404  function test_probe_timeout_accepts_the_domain  def test_probe_timeout_accepts_the_domain(tmp_path, agent_result, raw)
- L2425-L2469  function test_identity_records_the_runtime_bytecode_state_not_the_string  def test_identity_records_the_runtime_bytecode_state_not_the_string( tmp_path, agent_result, value, dash_b, force_m3)
- L2474-L2482  function _hostile_env  def _hostile_env(agent, framedir, timeout="5")
- L2486-L2512  function test_probe_evidence_writes_refuse_a_non_regular_path  def test_probe_evidence_writes_refuse_a_non_regular_path(tmp_path, agent_result, target)
- L2515-L2540  function test_probe_timeout_reject_write_refuses_a_non_regular_path  def test_probe_timeout_reject_write_refuses_a_non_regular_path(tmp_path, agent_result)
- L2546-L2612  function test_probe_survives_its_own_file_being_replaced_mid_run  def test_probe_survives_its_own_file_being_replaced_mid_run(tmp_path, agent_result, also_break_env)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 5 hits over 1 files ---
AF-AP-80: 4
    tests/test_s0_01_acp_probe.py:2274: assert "probe_error" not in json.loads((control / "runtime-identity.json").read_text())
    tests/test_s0_01_acp_probe.py:2404: assert "probe_error" not in json.loads((framedir / "runtime-identity.json").read_text())
    tests/test_s0_01_acp_probe.py:2734: assert "probe_error" not in json.loads((control / "runtime-identity.json").read_text())
    tests/test_s0_01_acp_probe.py:3050: assert token in prim or token in src, f"the guarded write boundary lost {token}"
AF-AP-57: 1
    tests/test_s0_01_acp_probe.py:1448: if _rl_calls[0] <= 3:

## graft ask — Which read of an evidence file or fixture in the probe does not go through _read_regular, and which Popen or fork in the probe or its tests can still inherit the framedir fd or a pipe?
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
graft ask — "Which read of an evidence file or fixture in the probe does not go through _read_regular, and which Popen or fork in the probe or its tests can still inherit the framedir fd or a pipe?"  (lexical)

1. main · function  [symbol]
   proofs/S0-01/tools/acp_probe.py:L253-L674
   def main(): # Validate required env vars early with a named message (L15/A10: exit 64). # Empty/unset cases exit 64 WITHOUT probe_error because the try block (which # writes runtime-identity.json) has not started yet — this is a documented # exception: probe_error requires the wrapped body to have opened.

2. main · function  [symbol]
   proofs/S0-01/tools/pc/pc_launch.py:L281-L425
   def main()

3. _refuse_non_regular · function  [symbol]
   proofs/S0-01/tools/scripted_backend.py:L394-L411
   def _refuse_non_regular(path: Path) -> bool

4. pump_fd · function  [symbol]
   proofs/S0-01/tools/frame_tee.py:L339-L421
   def pump_fd(fd, dst, direction, dir_path, close_dst)

5. main · function  [symbol]
   proofs/S0-01/tools/pc/pc_negative.py:L19-L50
   def main()

6. main · function  [symbol]
   proofs/S0-01/tools/build_capture_record.py:L48-L217
   def main() -> int

7. frame_tee_v1.py · file  [symbol]
   proofs/S0-01/tools/archive/frame_tee_v1.py

8. main · function  [symbol]
   proofs/S0-01/tools/archive/build_capture_record_v1.py:L43-L101
   def main() -> int

## symbol _read_regular
### GitNexus impact (upstream)
  "impactedCount": null,
  "risk": "UNKNOWN",
      "impactedCount": 4,
      "risk": "LOW",
      "direct": 2
      "impactedCount": 1,
      "risk": "LOW",
      "direct": 1
### code-review-graph callers_of / tests_for
  "summary": "Found 7 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::_read_regular')",
      "name": "_sha256_file",
      "name": "main",
      "name": "test_probe_read_regular_refuses_final_symlink_with_eloop",
      "name": "test_probe_read_primitive_reads_a_regular_file",
      "name": "test_probe_read_primitive_refuses_named_non_regular_shapes",
      "name": "test_probe_read_primitive_leaves_no_fd_on_refusal",
      "name": "test_probe_read_primitive_mutants_die_at_the_open_level",
  "summary": "Found 5 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::_read_regular')",
      "name": "test_probe_read_regular_refuses_final_symlink_with_eloop",
      "name": "test_probe_read_primitive_reads_a_regular_file",
      "name": "test_probe_read_primitive_refuses_named_non_regular_shapes",
      "name": "test_probe_read_primitive_leaves_no_fd_on_refusal",
      "name": "test_probe_read_primitive_mutants_die_at_the_open_level",
### ripwire callers
<callers of="_read_regular" defs="2" count="3" root="/home/user/agent-factory" hop_tested="1" hop_untested="2" shown="3" capped="0" total="3" has_more="0" next_offset="3" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="101" counts_floor="1" next="--uses=_read_regular">

## symbol _run_probe
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 36 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_acp_probe.py::_run_probe')",
      "name": "test_probe_result_response_and_check_initialize",
      "name": "test_probe_error_response",
      "name": "test_probe_never_answers",
      "name": "test_probe_stderr_heavy_no_deadlock",
      "name": "test_probe_partial_line_completes",
      "name": "test_probe_notification_then_response",
      "name": "test_probe_spawned_at_precedes_first_frame",
      "name": "test_probe_bad_agent_path_writes_probe_error",
      "name": "test_probe_sigterm_killed_agent_exit_code",
      "name": "test_probe_error_surfaces_on_exception",
      "name": "test_probe_non_json_a2c_line",
  "summary": "Found 36 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_acp_probe.py::_run_probe')",
      "name": "test_probe_result_response_and_check_initialize",
      "name": "test_probe_error_response",
      "name": "test_probe_never_answers",
      "name": "test_probe_stderr_heavy_no_deadlock",
      "name": "test_probe_partial_line_completes",
      "name": "test_probe_notification_then_response",
      "name": "test_probe_spawned_at_precedes_first_frame",
      "name": "test_probe_bad_agent_path_writes_probe_error",
      "name": "test_probe_sigterm_killed_agent_exit_code",
      "name": "test_probe_error_surfaces_on_exception",
      "name": "test_probe_non_json_a2c_line",
### ripwire callers
<callers of="_run_probe" defs="1" count="36" root="/home/user/agent-factory" hop_tested="0" hop_untested="36" shown="20" capped="1" total="36" has_more="1" next_offset="20" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="101" counts_floor="1" next="--uses=_run_probe">

## symbol _sha256_file
### GitNexus impact (upstream)
  "impactedCount": null,
  "risk": "UNKNOWN",
      "impactedCount": 5,
      "risk": "LOW",
      "direct": 2
      "impactedCount": 5,
      "risk": "LOW",
      "direct": 1
### code-review-graph callers_of / tests_for
  "summary": "Found 3 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::_sha256_file')",
      "name": "/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py",
      "name": "_write_evidence",
      "name": "main",
  "summary": "Found 6 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::_sha256_file')",
      "name": "test_probe_read_regular_refuses_final_symlink_with_eloop",
      "name": "test_probe_read_primitive_reads_a_regular_file",
      "name": "test_probe_read_primitive_refuses_named_non_regular_shapes",
      "name": "test_probe_read_primitive_leaves_no_fd_on_refusal",
      "name": "test_probe_read_primitive_mutants_die_at_the_open_level",
      "name": "test_sha256_file_refuses_a_non_regular_file",
### ripwire callers
<callers of="_sha256_file" defs="7" count="18" root="/home/user/agent-factory" hop_tested="2" hop_untested="16" shown="18" capped="0" total="18" has_more="0" next_offset="18" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="101" counts_floor="1" next="--uses=_sha256_file">

## symbol _write_evidence
### GitNexus impact (upstream)
  "impactedCount": 2,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::_write_evidence')",
      "name": "main",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::_write_evidence')",
### ripwire callers
<callers of="_write_evidence" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="101" counts_floor="1" next="--uses=_write_evidence">

## symbol _leaf_handle
### GitNexus impact (upstream)
  "impactedCount": 5,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 4,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 4 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::_leaf_handle')",
      "name": "_write_env",
      "name": "_write_evidence",
      "name": "main",
      "name": "_m3_write",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::_leaf_handle')",
### ripwire callers
<callers of="_leaf_handle" defs="1" count="4" root="/home/user/agent-factory" hop_tested="0" hop_untested="4" shown="4" capped="0" total="4" has_more="0" next_offset="4" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="101" counts_floor="1" next="--uses=_leaf_handle">

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
  "summary": "Found 32 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::main')",
      "name": "/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py",
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
  "summary": "Found 6 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/acp_probe.py::main')",
      "name": "test_probe_read_regular_refuses_final_symlink_with_eloop",
      "name": "test_probe_read_primitive_reads_a_regular_file",
      "name": "test_probe_read_primitive_refuses_named_non_regular_shapes",
      "name": "test_probe_read_primitive_leaves_no_fd_on_refusal",
      "name": "test_probe_read_primitive_mutants_die_at_the_open_level",
      "name": "/home/user/agent-factory/sandbox-kit/codebase-memory-mcp/tests/test_main.c",
### ripwire callers
<callers of="main" defs="51" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="101" counts_floor="1" next="--uses=main">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
<test-gate changed="1" impacted="0" tests="0" untested="0" shown_tests="0" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="8" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="efde78dff+dirty" next="--situ">
