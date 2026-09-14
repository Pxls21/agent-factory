# lane context pack — 1a1ec4b 2026-09-14T12:31Z
files: proofs/S0-08/canaries/P1.sh proofs/S0-08/canaries/P2.sh proofs/S0-08/canaries/P3.sh proofs/S0-08/canaries/P4.sh proofs/S0-08/canaries/P5.sh proofs/S0-08/canaries/P6.sh proofs/S0-08/canaries/P7.sh proofs/S0-08/canaries/P8.sh proofs/S0-08/check_containment.py proofs/S0-08/tools/pc/run_containment.sh tests/test_s0_08_containment.py
symbols: _check_canary_exec_user _check_image_identity _check_run_argv _identity_string check_identity check_observer_identity expected_run_argv test_canary_exec_user_must_be_a_json_string test_closed_run_argv_grammar_refuses_extra_tokens test_closed_run_argv_grammar_refuses_reordered_required_pair test_each_canary_must_read_back_the_requested_exec_uid test_each_required_run_argv_pair_is_required test_every_shipped_canary_measures_its_exec_uid test_image_identity_is_measured_and_bound test_image_identity_rejects_missing_baked_provenance test_p6_own_pid_count_has_a_positive_floor test_runner_builds_from_the_pin_archive_and_sets_image_provenance test_runner_measures_prebuilt_and_running_image_identity test_runner_uses_and_removes_a_fresh_named_data_volume

## proofs/S0-08/canaries/P1.sh
### graft skeleton
graft skeleton — proofs/S0-08/canaries/P1.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-08/canaries/P2.sh
### graft skeleton
graft skeleton — proofs/S0-08/canaries/P2.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-08/canaries/P3.sh
### graft skeleton
graft skeleton — proofs/S0-08/canaries/P3.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-08/canaries/P4.sh
### graft skeleton
graft skeleton — proofs/S0-08/canaries/P4.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-51: 1
    proofs/S0-08/canaries/P4.sh:26: # the exec environment exposed to that uid; it is deliberately not claimed as byte-identical to the

## proofs/S0-08/canaries/P5.sh
### graft skeleton
graft skeleton — proofs/S0-08/canaries/P5.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-08/canaries/P6.sh
### graft skeleton
graft skeleton — proofs/S0-08/canaries/P6.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-08/canaries/P7.sh
### graft skeleton
graft skeleton — proofs/S0-08/canaries/P7.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-08/canaries/P8.sh
### graft skeleton
graft skeleton — proofs/S0-08/canaries/P8.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-08/check_containment.py
### graft skeleton

graft skeleton — proofs/S0-08/check_containment.py
- L101-L102  class Deferred  class Deferred(Exception)
- L105-L106  class Failure  class Failure(Exception)
- L109-L117  function _require_file  def _require_file(path: Path, name: str) -> Path
- L120-L125  function _load_json  def _load_json(path: Path, name: str)
- L128-L159  function _load_canaries  def _load_canaries(path: Path) -> dict
- L162-L173  function _canary  def _canary(canaries: dict, cid: str) -> dict
- L176-L185  function _field  def _field(observed: dict, cid: str, key: str) -> str
- L188-L190  function _csv  def _csv(observed: dict, cid: str, key: str) -> list[str]
- L200-L212  function expected_run_argv  def expected_run_argv(runtime: str, image: str, data_volume: str) -> list[str]
- L215-L221  function _identity_string  def _identity_string(identity: dict, key: str) -> str
- L224-L255  function _check_image_identity  def _check_image_identity(identity: dict, commit: str) -> None
- L258-L285  function _check_run_argv  def _check_run_argv(identity: dict) -> None
- L288-L301  function _check_canary_exec_user  def _check_canary_exec_user(identity: dict) -> str
- L304-L331  function check_identity  def check_identity(identity: dict) -> str
- L334-L342  function check_observer_identity  def check_observer_identity(canaries: dict, expected_uid: str) -> None
- L347-L354  function check_p1  def check_p1(canaries: dict) -> None
- L357-L388  function check_p2  def check_p2(canaries: dict) -> None
- L391-L402  function check_p3  def check_p3(canaries: dict) -> None
- L405-L425  function check_p4  def check_p4(canaries: dict) -> None
- L428-L447  function check_p5  def check_p5(canaries: dict, identity: dict) -> None
- L450-L509  function check_p6  def check_p6(canaries: dict) -> None
- L512-L523  function check_recorded  def check_recorded(canaries: dict) -> None
- L528-L545  function check_bundle  def check_bundle(evidence_dir: Path) -> str
- L548-L561  function main  def main(argv) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-08/tools/pc/run_containment.sh
### graft skeleton
graft skeleton — proofs/S0-08/tools/pc/run_containment.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## tests/test_s0_08_containment.py
### graft skeleton

graft skeleton — tests/test_s0_08_containment.py
- L43-L49  function dmesg_restrict  def dmesg_restrict() -> str
- L52-L60  function dmesg_works  def dmesg_works() -> bool
- L63-L65  function venue  def venue() -> str
- L68-L72  function run_checker  def run_checker(evidence_dir) -> subprocess.CompletedProcess
- L75-L79  function run_marker_gate  def run_marker_gate(proof_dir) -> subprocess.CompletedProcess
- L86-L141  function passing_canaries  def passing_canaries() -> list[dict]
- L144-L173  function passing_identity  def passing_identity() -> dict
- L176-L184  function write_bundle  def write_bundle(directory: Path, canaries=None, identity=None) -> Path
- L189-L199  function test_crun_bundle_fails_on_p1_with_the_exact_spec_reason  def test_crun_bundle_fails_on_p1_with_the_exact_spec_reason()
- L202-L211  function test_crun_bundle_identity_is_valid_so_p1_is_what_catches_it  def test_crun_bundle_identity_is_valid_so_p1_is_what_catches_it()
- L216-L220  function test_synthetic_passing_bundle_passes  def test_synthetic_passing_bundle_passes(tmp_path)
- L223-L228  function test_passing_bundle_is_deterministic  def test_passing_bundle_is_deterministic(tmp_path)
- L233-L236  function test_absent_evidence_dir_defers  def test_absent_evidence_dir_defers(tmp_path)
- L239-L246  function test_present_dir_with_missing_files_is_a_failure_not_a_deferral  def test_present_dir_with_missing_files_is_a_failure_not_a_deferral(tmp_path)
- L284-L292  function test_each_property_mutation_is_caught  def test_each_property_mutation_is_caught(tmp_path, mutant_id, canary, field, value, expected)
- L295-L304  function test_p4_secret_env_key_is_caught  def test_p4_secret_env_key_is_caught(tmp_path)
- L307-L318  function test_p4_count_and_names_must_agree  def test_p4_count_and_names_must_agree(tmp_path)
- L323-L331  function test_runsc_version_unpinned_is_caught  def test_runsc_version_unpinned_is_caught(tmp_path)
- L334-L342  function test_runsc_sha_unpinned_is_caught  def test_runsc_sha_unpinned_is_caught(tmp_path)
- L345-L351  function test_identity_absent_fields_are_caught  def test_identity_absent_fields_are_caught(tmp_path)
- L357-L364  function test_missing_canary_line_fails_by_name  def test_missing_canary_line_fails_by_name(tmp_path, dropped)
- L367-L373  function test_duplicate_canary_line_is_rejected  def test_duplicate_canary_line_is_rejected(tmp_path)
- L376-L387  function test_canary_that_did_not_observe_is_not_a_pass  def test_canary_that_did_not_observe_is_not_a_pass(tmp_path)
- L390-L406  function test_p5_without_the_sentinel_env_var_fails_closed  def test_p5_without_the_sentinel_env_var_fails_closed(tmp_path)
- L409-L415  function test_unknown_canary_id_is_rejected  def test_unknown_canary_id_is_rejected(tmp_path)
- L420-L428  function test_p5_without_the_host_control_is_not_a_pass  def test_p5_without_the_host_control_is_not_a_pass(tmp_path)
- L431-L439  function test_p5_path_mismatch_is_caught  def test_p5_path_mismatch_is_caught(tmp_path)
- L442-L448  function test_p5_host_control_that_did_not_read_is_caught  def test_p5_host_control_that_did_not_read_is_caught(tmp_path)
- L454-L463  function test_fifo_at_an_evidence_path_is_refused_not_hung  def test_fifo_at_an_evidence_path_is_refused_not_hung(tmp_path, victim)
- L466-L472  function test_directory_at_an_evidence_path_is_refused  def test_directory_at_an_evidence_path_is_refused(tmp_path)
- L475-L480  function test_malformed_jsonl_line_is_named  def test_malformed_jsonl_line_is_named(tmp_path)
- L485-L492  function test_marker_gate_malformed_matches_the_spec_leg  def test_marker_gate_malformed_matches_the_spec_leg()
- L495-L500  function test_marker_gate_absent  def test_marker_gate_absent(tmp_path)
- L503-L510  function test_marker_gate_expired_without_result_is_red  def test_marker_gate_expired_without_result_is_red(tmp_path)
- L513-L519  function test_marker_gate_completed_transition  def test_marker_gate_completed_transition(tmp_path)
- L522-L530  function test_marker_gate_expired_with_result_is_green  def test_marker_gate_expired_with_result_is_green(tmp_path)
- L533-L541  function test_marker_gate_honest_deferral_is_green  def test_marker_gate_honest_deferral_is_green(tmp_path)
- L545-L553  function test_marker_gate_names_each_missing_field  def test_marker_gate_names_each_missing_field(tmp_path, field)
- L556-L564  function test_marker_gate_rejects_out_of_enum_status  def test_marker_gate_rejects_out_of_enum_status(tmp_path)
- L567-L574  function test_marker_gate_result_presence_alone_does_not_retire_the_marker  def test_marker_gate_result_presence_alone_does_not_retire_the_marker(tmp_path)
- L577-L584  function test_marker_gate_rejects_a_result_from_another_proof  def test_marker_gate_rejects_a_result_from_another_proof(tmp_path)
- L587-L594  function test_marker_gate_result_fifo_is_refused_not_hung  def test_marker_gate_result_fifo_is_refused_not_hung(tmp_path)
- L597-L603  function test_marker_gate_fifo_is_refused_not_hung  def test_marker_gate_fifo_is_refused_not_hung(tmp_path)
- L606-L613  function test_live_marker_is_expired_and_red  def test_live_marker_is_expired_and_red()
- L618-L622  function test_every_canary_script_exists_and_is_executable  def test_every_canary_script_exists_and_is_executable()
- L625-L629  function test_every_canary_script_is_shell_clean  def test_every_canary_script_is_shell_clean()
- L632-L644  function test_committed_bundle_carries_every_canary_and_parses  def test_committed_bundle_carries_every_canary_and_parses()
- L648-L658  function test_read_only_canaries_emit_one_parseable_line_when_run  def test_read_only_canaries_emit_one_parseable_line_when_run(canary)
- L666-L746  function test_live_canary_output_binds_to_the_fields_the_checker_reads  def test_live_canary_output_binds_to_the_fields_the_checker_reads( tmp_path, canary, expected_reason_fragment)
- L749-L756  function test_canaries_never_print_a_verdict  def test_canaries_never_print_a_verdict()
- L759-L771  function test_a_canary_line_carrying_a_verdict_is_still_judged_by_the_checker  def test_a_canary_line_carrying_a_verdict_is_still_judged_by_the_checker(tmp_path)
- L776-L779  function test_spec_validates_against_the_schema  def test_spec_validates_against_the_schema()
- L782-L797  function test_spec_negative_legs_reproduce_their_pinned_reasons  def test_spec_negative_legs_reproduce_their_pinned_reasons()
- L800-L811  function test_spec_positive_leg_defers_until_the_pc_run_lands  def test_spec_positive_leg_defers_until_the_pc_run_lands()
- L814-L818  function test_pc_runner_is_bash_clean  def test_pc_runner_is_bash_clean()
- L824-L834  function runner_code  def runner_code() -> str
- L837-L844  function test_pc_runner_tears_down_by_id_never_by_name  def test_pc_runner_tears_down_by_id_never_by_name()
- L847-L854  function test_pc_runner_pins_the_verified_runsc_flags  def test_pc_runner_pins_the_verified_runsc_flags()
- L857-L863  function test_runner_code_filter_actually_removes_comments  def test_runner_code_filter_actually_removes_comments()
- L874-L885  function _mount_failed_p6  def _mount_failed_p6(canaries, **overrides)
- L888-L895  function test_p6_mount_failure_still_asserts_the_containment_signature  def test_p6_mount_failure_still_asserts_the_containment_signature(tmp_path)
- L898-L910  function test_p6_mount_failure_is_not_a_silent_pass  def test_p6_mount_failure_is_not_a_silent_pass(tmp_path)
- L913-L920  function test_p6_mount_failure_without_a_reason_is_caught  def test_p6_mount_failure_without_a_reason_is_caught(tmp_path)
- L923-L933  function test_p6_pid1_comm_must_agree_with_p2s_independent_read  def test_p6_pid1_comm_must_agree_with_p2s_independent_read(tmp_path)
- L936-L941  function test_p6_own_pid_count_must_be_a_count  def test_p6_own_pid_count_must_be_a_count(tmp_path)
- L945-L952  function test_p6_own_pid_count_has_a_positive_floor  def test_p6_own_pid_count_has_a_positive_floor(tmp_path, value)
- L957-L969  function test_p2_ambiguous_main_cmdline_is_refused  def test_p2_ambiguous_main_cmdline_is_refused(tmp_path)
- L972-L980  function test_p2_pid_and_uid_lists_must_agree  def test_p2_pid_and_uid_lists_must_agree(tmp_path)
- L983-L992  function test_p2_main_program_absent_is_named  def test_p2_main_program_absent_is_named(tmp_path)
- L995-L1004  function test_p2_without_the_main_cmdline_env_fails_closed  def test_p2_without_the_main_cmdline_env_fails_closed()
- L1007-L1037  function test_p2_reports_every_holder_of_the_main_cmdline  def test_p2_reports_every_holder_of_the_main_cmdline(tmp_path)
- L1040-L1050  function test_runner_and_p2_share_one_source_for_the_main_cmdline  def test_runner_and_p2_share_one_source_for_the_main_cmdline()
- L1053-L1060  function test_runner_main_cmd_does_not_collide_with_the_images_root_sleeper  def test_runner_main_cmd_does_not_collide_with_the_images_root_sleeper()
- L1065-L1071  function test_pc_runner_execs_every_canary_as_the_runtime_user  def test_pc_runner_execs_every_canary_as_the_runtime_user()
- L1074-L1081  function test_pc_runner_checks_the_exec_status_not_only_its_output  def test_pc_runner_checks_the_exec_status_not_only_its_output()
- L1084-L1092  function test_canaries_exec_d_as_root_are_refused  def test_canaries_exec_d_as_root_are_refused(tmp_path)
- L1095-L1101  function test_canary_exec_user_absent_is_refused  def test_canary_exec_user_absent_is_refused(tmp_path)
- L1104-L1109  function test_canary_exec_user_must_be_a_json_string  def test_canary_exec_user_must_be_a_json_string(tmp_path)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 8 hits over 1 files ---
AF-AP-34: 8
    tests/test_s0_08_containment.py:829: pkill and host networking are forbidden — the check must read code, not
    tests/test_s0_08_containment.py:838: """AF-AP-34: this runs on the owner's shared host. A name match or a pkill
    tests/test_s0_08_containment.py:842: assert "pkill" not in code
    tests/test_s0_08_containment.py:843: assert "killall" not in code
    tests/test_s0_08_containment.py:862: assert "pkill" in raw, "the explanatory comment naming pkill is gone"
    tests/test_s0_08_containment.py:862: assert "pkill" in raw, "the explanatory comment naming pkill is gone"
    ... +2

## graft ask — in proofs/S0-08, where is the observer uid read back from the executed canary, and where is the image digest measured and bound to the built image
unmapped — graft ask unavailable or failed (rc 1): ✗ nothing indexed under "proofs/S0-08/canaries/" — scopes here: sandbox-kit/honey-for-devs/ · sandbox-kit/aleph/ (or any path prefix)

## symbol _check_canary_exec_user
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-08/check_containment.py::_check_canary_exec_user')",
      "name": "check_identity",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-08/check_containment.py::_check_canary_exec_user')",
### ripwire callers
<callers of="_check_canary_exec_user" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=_check_canary_exec_user">

## symbol _check_image_identity
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-08/check_containment.py::_check_image_identity')",
      "name": "check_identity",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-08/check_containment.py::_check_image_identity')",
### ripwire callers
<callers of="_check_image_identity" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=_check_image_identity">

## symbol _check_run_argv
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-08/check_containment.py::_check_run_argv')",
      "name": "check_identity",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-08/check_containment.py::_check_run_argv')",
### ripwire callers
<callers of="_check_run_argv" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=_check_run_argv">

## symbol _identity_string
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/proofs/S0-08/check_containment.py::_identity_string')",
      "name": "_check_image_identity",
      "name": "_check_run_argv",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-08/check_containment.py::_identity_string')",
### ripwire callers
<callers of="_identity_string" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=_identity_string">

## symbol check_identity
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-08/check_containment.py::check_identity')",
      "name": "check_bundle",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-08/check_containment.py::check_identity')",
### ripwire callers
<callers of="check_identity" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=check_identity">

## symbol check_observer_identity
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-08/check_containment.py::check_observer_identity')",
      "name": "check_bundle",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-08/check_containment.py::check_observer_identity')",
### ripwire callers
<callers of="check_observer_identity" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=check_observer_identity">

## symbol expected_run_argv
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-08/check_containment.py::expected_run_argv')",
      "name": "_check_run_argv",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-08/check_containment.py::expected_run_argv')",
### ripwire callers
<callers of="expected_run_argv" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=expected_run_argv">

## symbol test_canary_exec_user_must_be_a_json_string
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_08_containment.py::test_canary_exec_user_must_be_a_json_string')",
  "summary": "Found 55 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_08_containment.py::test_canary_exec_user_must_be_a_json_string')",
      "name": "test_crun_bundle_fails_on_p1_with_the_exact_spec_reason",
      "name": "test_crun_bundle_identity_is_valid_so_p1_is_what_catches_it",
      "name": "test_synthetic_passing_bundle_passes",
      "name": "test_passing_bundle_is_deterministic",
      "name": "test_absent_evidence_dir_defers",
      "name": "test_present_dir_with_missing_files_is_a_failure_not_a_deferral",
      "name": "test_each_property_mutation_is_caught",
      "name": "test_p4_secret_env_key_is_caught",
      "name": "test_p4_count_and_names_must_agree",
      "name": "test_runsc_version_unpinned_is_caught",
      "name": "test_runsc_sha_unpinned_is_caught",
### ripwire callers
<callers of="test_canary_exec_user_must_be_a_json_string" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_canary_exec_user_must_be_a_json_string">

## symbol test_closed_run_argv_grammar_refuses_extra_tokens
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_08_containment.py::test_closed_run_argv_grammar_refuses_extra_tokens')",
  "summary": "Found 55 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_08_containment.py::test_closed_run_argv_grammar_refuses_extra_tokens')",
      "name": "test_runsc_version_unpinned_is_caught",
      "name": "test_runsc_sha_unpinned_is_caught",
      "name": "test_identity_absent_fields_are_caught",
      "name": "test_p5_without_the_host_control_is_not_a_pass",
      "name": "test_p5_path_mismatch_is_caught",
      "name": "test_p5_host_control_that_did_not_read_is_caught",
      "name": "test_canaries_exec_d_as_root_are_refused",
      "name": "test_canary_exec_user_absent_is_refused",
      "name": "test_canary_exec_user_must_be_a_json_string",
      "name": "test_evidence_from_another_image_is_refused",
      "name": "test_image_identity_is_measured_and_bound",
### ripwire callers
<callers of="test_closed_run_argv_grammar_refuses_extra_tokens" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_closed_run_argv_grammar_refuses_extra_tokens">

## symbol test_closed_run_argv_grammar_refuses_reordered_required_pair
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_08_containment.py::test_closed_run_argv_grammar_refuses_reordered_required_pair')",
  "summary": "Found 55 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_08_containment.py::test_closed_run_argv_grammar_refuses_reordered_required_pair')",
      "name": "test_runsc_version_unpinned_is_caught",
      "name": "test_runsc_sha_unpinned_is_caught",
      "name": "test_identity_absent_fields_are_caught",
      "name": "test_p5_without_the_host_control_is_not_a_pass",
      "name": "test_p5_path_mismatch_is_caught",
      "name": "test_p5_host_control_that_did_not_read_is_caught",
      "name": "test_canaries_exec_d_as_root_are_refused",
      "name": "test_canary_exec_user_absent_is_refused",
      "name": "test_canary_exec_user_must_be_a_json_string",
      "name": "test_evidence_from_another_image_is_refused",
      "name": "test_image_identity_is_measured_and_bound",
### ripwire callers
<callers of="test_closed_run_argv_grammar_refuses_reordered_required_pair" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_closed_run_argv_grammar_refuses_reordered_required_pair">

## symbol test_each_canary_must_read_back_the_requested_exec_uid
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_08_containment.py::test_each_canary_must_read_back_the_requested_exec_uid')",
  "summary": "Found 55 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_08_containment.py::test_each_canary_must_read_back_the_requested_exec_uid')",
      "name": "test_crun_bundle_fails_on_p1_with_the_exact_spec_reason",
      "name": "test_crun_bundle_identity_is_valid_so_p1_is_what_catches_it",
      "name": "test_synthetic_passing_bundle_passes",
      "name": "test_passing_bundle_is_deterministic",
      "name": "test_absent_evidence_dir_defers",
      "name": "test_present_dir_with_missing_files_is_a_failure_not_a_deferral",
      "name": "test_each_property_mutation_is_caught",
      "name": "test_p4_secret_env_key_is_caught",
      "name": "test_p4_count_and_names_must_agree",
      "name": "test_runsc_version_unpinned_is_caught",
      "name": "test_runsc_sha_unpinned_is_caught",
### ripwire callers
<callers of="test_each_canary_must_read_back_the_requested_exec_uid" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_each_canary_must_read_back_the_requested_exec_uid">

## symbol test_each_required_run_argv_pair_is_required
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_08_containment.py::test_each_required_run_argv_pair_is_required')",
  "summary": "Found 55 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_08_containment.py::test_each_required_run_argv_pair_is_required')",
      "name": "test_crun_bundle_fails_on_p1_with_the_exact_spec_reason",
      "name": "test_crun_bundle_identity_is_valid_so_p1_is_what_catches_it",
      "name": "test_synthetic_passing_bundle_passes",
      "name": "test_passing_bundle_is_deterministic",
      "name": "test_absent_evidence_dir_defers",
      "name": "test_present_dir_with_missing_files_is_a_failure_not_a_deferral",
      "name": "test_each_property_mutation_is_caught",
      "name": "test_p4_secret_env_key_is_caught",
      "name": "test_p4_count_and_names_must_agree",
      "name": "test_runsc_version_unpinned_is_caught",
      "name": "test_runsc_sha_unpinned_is_caught",
### ripwire callers
<callers of="test_each_required_run_argv_pair_is_required" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_each_required_run_argv_pair_is_required">

## symbol test_every_shipped_canary_measures_its_exec_uid
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_08_containment.py::test_every_shipped_canary_measures_its_exec_uid')",
  "summary": "Found 3 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_08_containment.py::test_every_shipped_canary_measures_its_exec_uid')",
      "name": "test_runner_and_p2_share_one_source_for_the_main_cmdline",
      "name": "test_every_shipped_canary_measures_its_exec_uid",
      "name": "test_canary_code_filter_actually_removes_comments",
### ripwire callers
<callers of="test_every_shipped_canary_measures_its_exec_uid" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_every_shipped_canary_measures_its_exec_uid">

## symbol test_image_identity_is_measured_and_bound
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_08_containment.py::test_image_identity_is_measured_and_bound')",
  "summary": "Found 55 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_08_containment.py::test_image_identity_is_measured_and_bound')",
      "name": "test_crun_bundle_fails_on_p1_with_the_exact_spec_reason",
      "name": "test_crun_bundle_identity_is_valid_so_p1_is_what_catches_it",
      "name": "test_synthetic_passing_bundle_passes",
      "name": "test_passing_bundle_is_deterministic",
      "name": "test_absent_evidence_dir_defers",
      "name": "test_present_dir_with_missing_files_is_a_failure_not_a_deferral",
      "name": "test_each_property_mutation_is_caught",
      "name": "test_p4_secret_env_key_is_caught",
      "name": "test_p4_count_and_names_must_agree",
      "name": "test_runsc_version_unpinned_is_caught",
      "name": "test_runsc_sha_unpinned_is_caught",
### ripwire callers
<callers of="test_image_identity_is_measured_and_bound" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_image_identity_is_measured_and_bound">

## symbol test_image_identity_rejects_missing_baked_provenance
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_08_containment.py::test_image_identity_rejects_missing_baked_provenance')",
  "summary": "Found 55 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_08_containment.py::test_image_identity_rejects_missing_baked_provenance')",
      "name": "test_synthetic_passing_bundle_passes",
      "name": "test_passing_bundle_is_deterministic",
      "name": "test_each_property_mutation_is_caught",
      "name": "test_p4_secret_env_key_is_caught",
      "name": "test_p4_count_and_names_must_agree",
      "name": "test_runsc_version_unpinned_is_caught",
      "name": "test_runsc_sha_unpinned_is_caught",
      "name": "test_identity_absent_fields_are_caught",
      "name": "test_missing_canary_line_fails_by_name",
      "name": "test_duplicate_canary_line_is_rejected",
      "name": "test_canary_that_did_not_observe_is_not_a_pass",
### ripwire callers
<callers of="test_image_identity_rejects_missing_baked_provenance" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_image_identity_rejects_missing_baked_provenance">

## symbol test_p6_own_pid_count_has_a_positive_floor
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_08_containment.py::test_p6_own_pid_count_has_a_positive_floor')",
  "summary": "Found 55 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_08_containment.py::test_p6_own_pid_count_has_a_positive_floor')",
      "name": "test_each_property_mutation_is_caught",
      "name": "test_p4_secret_env_key_is_caught",
      "name": "test_p4_count_and_names_must_agree",
      "name": "test_missing_canary_line_fails_by_name",
      "name": "test_duplicate_canary_line_is_rejected",
      "name": "test_canary_that_did_not_observe_is_not_a_pass",
      "name": "test_p5_without_the_sentinel_env_var_fails_closed",
      "name": "test_unknown_canary_id_is_rejected",
      "name": "test_live_canary_output_binds_to_the_fields_the_checker_reads",
      "name": "test_a_canary_line_carrying_a_verdict_is_still_judged_by_the_checker",
      "name": "test_p6_mount_failure_still_asserts_the_containment_signature",
### ripwire callers
<callers of="test_p6_own_pid_count_has_a_positive_floor" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_p6_own_pid_count_has_a_positive_floor">

## symbol test_runner_builds_from_the_pin_archive_and_sets_image_provenance
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_08_containment.py::test_runner_builds_from_the_pin_archive_and_sets_image_provenance')",
  "summary": "Found 11 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_08_containment.py::test_runner_builds_from_the_pin_archive_and_sets_image_provenance')",
      "name": "test_pc_runner_tears_down_by_id_never_by_name",
      "name": "test_pc_runner_pins_the_verified_runsc_flags",
      "name": "test_runner_code_filter_actually_removes_comments",
      "name": "test_runner_and_p2_share_one_source_for_the_main_cmdline",
      "name": "test_runner_main_cmd_does_not_collide_with_the_images_root_sleeper",
      "name": "test_pc_runner_execs_every_canary_as_the_runtime_user",
      "name": "test_pc_runner_checks_the_exec_status_not_only_its_output",
      "name": "test_runner_builds_from_the_pin_archive_and_sets_image_provenance",
      "name": "test_runner_measures_prebuilt_and_running_image_identity",
      "name": "test_runner_uses_and_removes_a_fresh_named_data_volume",
      "name": "test_runner_calls_the_preflight_with_the_pinned_commit",
### ripwire callers
<callers of="test_runner_builds_from_the_pin_archive_and_sets_image_provenance" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_runner_builds_from_the_pin_archive_and_sets_image_provenance">

## symbol test_runner_measures_prebuilt_and_running_image_identity
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_08_containment.py::test_runner_measures_prebuilt_and_running_image_identity')",
  "summary": "Found 11 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_08_containment.py::test_runner_measures_prebuilt_and_running_image_identity')",
      "name": "test_pc_runner_tears_down_by_id_never_by_name",
      "name": "test_pc_runner_pins_the_verified_runsc_flags",
      "name": "test_runner_code_filter_actually_removes_comments",
      "name": "test_runner_and_p2_share_one_source_for_the_main_cmdline",
      "name": "test_runner_main_cmd_does_not_collide_with_the_images_root_sleeper",
      "name": "test_pc_runner_execs_every_canary_as_the_runtime_user",
      "name": "test_pc_runner_checks_the_exec_status_not_only_its_output",
      "name": "test_runner_builds_from_the_pin_archive_and_sets_image_provenance",
      "name": "test_runner_measures_prebuilt_and_running_image_identity",
      "name": "test_runner_uses_and_removes_a_fresh_named_data_volume",
      "name": "test_runner_calls_the_preflight_with_the_pinned_commit",
### ripwire callers
<callers of="test_runner_measures_prebuilt_and_running_image_identity" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_runner_measures_prebuilt_and_running_image_identity">

## symbol test_runner_uses_and_removes_a_fresh_named_data_volume
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_08_containment.py::test_runner_uses_and_removes_a_fresh_named_data_volume')",
  "summary": "Found 11 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_08_containment.py::test_runner_uses_and_removes_a_fresh_named_data_volume')",
      "name": "test_pc_runner_tears_down_by_id_never_by_name",
      "name": "test_pc_runner_pins_the_verified_runsc_flags",
      "name": "test_runner_code_filter_actually_removes_comments",
      "name": "test_runner_and_p2_share_one_source_for_the_main_cmdline",
      "name": "test_runner_main_cmd_does_not_collide_with_the_images_root_sleeper",
      "name": "test_pc_runner_execs_every_canary_as_the_runtime_user",
      "name": "test_pc_runner_checks_the_exec_status_not_only_its_output",
      "name": "test_runner_builds_from_the_pin_archive_and_sets_image_provenance",
      "name": "test_runner_measures_prebuilt_and_running_image_identity",
      "name": "test_runner_uses_and_removes_a_fresh_named_data_volume",
      "name": "test_runner_calls_the_preflight_with_the_pinned_commit",
### ripwire callers
<callers of="test_runner_uses_and_removes_a_fresh_named_data_volume" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_runner_uses_and_removes_a_fresh_named_data_volume">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
<test-gate changed="1" impacted="0" tests="0" untested="0" shown_tests="0" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="4" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="1a1ec4bf5+dirty" next="--situ">
