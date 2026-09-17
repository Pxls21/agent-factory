# lane context pack — a98261c 2026-09-17T12:33Z
files: proofs/S0-03/check_omniroute_roundtrip.py proofs/S0-03/tools/pc/collect_leg.sh tests/test_s0_03_omniroute.py
symbols: _walk_credentials _instant check_roundtrip transport_method check_env_record

## proofs/S0-03/check_omniroute_roundtrip.py
### graft skeleton

graft skeleton — proofs/S0-03/check_omniroute_roundtrip.py
- L109-L126  function _load_s0_01_module  def _load_s0_01_module()
- L177-L191  function is_credential_name  def is_credential_name(name: str) -> bool
- L202-L203  class Failure  class Failure(Exception)
- L206-L207  class Deferred  class Deferred(Exception)
- L210-L211  function _reason  def _reason(key: str, *args) -> str
- L214-L215  function _fail  def _fail(key: str, *args)
- L219-L226  function _require_file  def _require_file(path: Path, name: str) -> Path
- L229-L234  function _reject_constant  def _reject_constant(token: str)
- L237-L242  function _read_json  def _read_json(path: Path, name: str)
- L245-L252  function _read_yaml  def _read_yaml(path: Path, name: str)
- L255-L258  function _obj  def _obj(value, name: str) -> dict
- L261-L264  function _str  def _str(value, name: str) -> str
- L277-L278  class Usage  class Usage(Exception)
- L281-L315  function parse_args  def parse_args(argv) -> dict
- L318-L327  function _is_stub  def _is_stub(name: str, stub_routes) -> bool
- L334-L343  function _authorization_presented  def _authorization_presented(direct: dict) -> bool
- L346-L368  function check_credential_at_the_gate  def check_credential_at_the_gate(direct: dict)
- L371-L378  function check_credential_in_the_environ  def check_credential_in_the_environ(env_names)
- L382-L421  function check_direct_stream  def check_direct_stream(direct: dict)
- L425-L428  function check_identity_model  def check_identity_model(direct: dict, spec: dict)
- L432-L453  function _rows_by_leg  def _rows_by_leg(requests: dict) -> dict
- L456-L467  function _instant  def _instant(value, name: str)
- L470-L478  function _require_in_window  def _require_in_window(row: dict, window: dict)
- L481-L572  function check_identity_route  def check_identity_route(requests: dict, direct: dict, leg_record: dict, spec: dict)
- L576-L589  function _updates  def _updates(entries)
- L592-L600  function _agent_text  def _agent_text(entries) -> str
- L603-L661  function check_roundtrip  def check_roundtrip(entries, nonce2: str)
- L665-L673  function _provider_block  def _provider_block(profile) -> tuple[str, dict]
- L676-L693  function _walk_credentials  def _walk_credentials(node, path: str)
- L696-L720  function check_transport  def check_transport(profile)
- L724-L738  function check_env  def check_env(env_names)
- L742-L779  function check_env_record  def check_env_record(record: dict, leg: dict)
- L783-L794  function load_direct  def load_direct(root: Path) -> dict
- L797-L826  function load_bundle  def load_bundle(root: Path, direct: dict) -> dict
- L829-L848  function check_bundle  def check_bundle(root: Path, spec: dict) -> str
- L851-L865  function main  def main(argv) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-03/tools/pc/collect_leg.sh
### graft skeleton
graft skeleton — proofs/S0-03/tools/pc/collect_leg.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## tests/test_s0_03_omniroute.py
### graft skeleton

graft skeleton — tests/test_s0_03_omniroute.py
- L52-L56  function _load  def _load(path: Path, name: str)
- L64-L65  function _spec  def _spec() -> dict
- L68-L82  function _leg_flags  def _leg_flags(leg: dict) -> dict
- L85-L86  function _positive_leg  def _positive_leg() -> dict
- L89-L96  function _flags  def _flags() -> list
- L99-L101  function run_checker  def run_checker(root, *, extra=None)
- L106-L117  function passing  def passing(tmp_path) -> Path
- L120-L124  function _edit  def _edit(root: Path, rel: str, mutate)
- L127-L129  function _timeline  def _timeline(root: Path)
- L132-L133  function _write_timeline  def _write_timeline(path: Path, entries)
- L136-L144  function test_passing_bundle_passes  def test_passing_bundle_passes(passing)
- L160-L164  function test_committed_negative_bundle_exact_reason  def test_committed_negative_bundle_exact_reason(bundle, reason)
- L167-L170  function test_credential_absent_reason_is_the_seed_kill_switch  def test_credential_absent_reason_is_the_seed_kill_switch()
- L173-L179  function test_every_negative_bundle_is_a_declared_spec_leg  def test_every_negative_bundle_is_a_declared_spec_leg()
- L182-L190  function test_each_negative_leg_reason_is_produced_verbatim  def test_each_negative_leg_reason_is_produced_verbatim()
- L193-L204  function test_fixtures_track_the_spec_expected_model_id  def test_fixtures_track_the_spec_expected_model_id()
- L207-L222  function test_every_bundle_has_provenance  def test_every_bundle_has_provenance()
- L227-L234  function test_conjunct_i_direct_stream  def test_conjunct_i_direct_stream(passing)
- L237-L252  function test_conjunct_i_rejects_a_vacuous_nonce  def test_conjunct_i_rejects_a_vacuous_nonce(passing)
- L255-L260  function test_conjunct_i_requires_the_compression_header_was_sent  def test_conjunct_i_requires_the_compression_header_was_sent(passing)
- L263-L273  function test_conjunct_ii_identity_model  def test_conjunct_ii_identity_model(passing)
- L276-L284  function test_conjunct_iii_identity_route  def test_conjunct_iii_identity_route(passing)
- L287-L299  function test_conjunct_iii_catches_every_declared_stub_id_and_its_namespace  def test_conjunct_iii_catches_every_declared_stub_id_and_its_namespace(passing)
- L302-L308  function test_conjunct_iii_binds_the_row_to_our_route  def test_conjunct_iii_binds_the_row_to_our_route(passing)
- L311-L318  function test_conjunct_iii_requires_the_two_instruments_to_agree  def test_conjunct_iii_requires_the_two_instruments_to_agree(passing)
- L321-L332  function test_conjunct_iv_roundtrip_requires_a_completed_tool_call  def test_conjunct_iv_roundtrip_requires_a_completed_tool_call(passing)
- L335-L344  function test_conjunct_iv_roundtrip_requires_a_tool_call_at_all  def test_conjunct_iv_roundtrip_requires_a_tool_call_at_all(passing)
- L347-L355  function test_conjunct_iv_requires_exactly_one_prompt_turn  def test_conjunct_iv_requires_exactly_one_prompt_turn(passing)
- L358-L367  function test_conjunct_iv_requires_the_nonce_in_the_final_text  def test_conjunct_iv_requires_the_nonce_in_the_final_text(passing)
- L370-L381  function test_conjunct_iv_binds_the_answer_to_the_question  def test_conjunct_iv_binds_the_answer_to_the_question(passing)
- L387-L393  function test_transport_requires_exact_post_on_both_rows  def test_transport_requires_exact_post_on_both_rows(passing, leg, method)
- L395-L406  function test_conjunct_v_transport  def test_conjunct_v_transport(passing)
- L423-L431  function test_credential_screen_recurses_over_the_whole_provider_block  def test_credential_screen_recurses_over_the_whole_provider_block(passing, mutation, path)
- L434-L441  function test_credential_screen_allows_only_the_provider_key_env_name  def test_credential_screen_allows_only_the_provider_key_env_name(passing)
- L443-L450  function test_conjunct_v_rejects_an_inline_key_in_the_captured_profile  def test_conjunct_v_rejects_an_inline_key_in_the_captured_profile(passing)
- L458-L470  function test_conjunct_v_rejects_a_credential_in_extra_headers  def test_conjunct_v_rejects_a_credential_in_extra_headers(passing, line, named)
- L473-L479  function test_conjunct_v_still_accepts_the_key_env_NAME  def test_conjunct_v_still_accepts_the_key_env_NAME(passing)
- L482-L487  function test_conjunct_v_requires_the_compression_header_in_the_profile  def test_conjunct_v_requires_the_compression_header_in_the_profile(passing)
- L490-L498  function test_conjunct_vi_env  def test_conjunct_vi_env(passing)
- L501-L512  function test_first_failure_order_is_pinned  def test_first_failure_order_is_pinned(passing)
- L515-L524  function test_a_credential_verdict_outranks_the_stream_conjunct  def test_a_credential_verdict_outranks_the_stream_conjunct(passing)
- L527-L537  function test_a_present_but_refused_key_is_rejected_not_absent  def test_a_present_but_refused_key_is_rejected_not_absent(passing)
- L540-L553  function test_a_401_on_a_request_that_sent_no_key_is_the_kill_switch  def test_a_401_on_a_request_that_sent_no_key_is_the_kill_switch(passing)
- L544-L549  function strip_auth  def strip_auth(record)
- L556-L566  function test_a_401_with_an_unreadable_header_record_is_a_bundle_failure  def test_a_401_with_an_unreadable_header_record_is_a_bundle_failure(passing)
- L559-L561  function break_headers  def break_headers(record)
- L569-L576  function test_an_environ_without_the_key_is_the_kill_switch  def test_an_environ_without_the_key_is_the_kill_switch(passing)
- L605-L615  function test_env_allowlist_is_a_closed_exact_set  def test_env_allowlist_is_a_closed_exact_set(name, rejected)
- L618-L623  function test_env_allowlist_reports_deterministically  def test_env_allowlist_reports_deterministically()
- L627-L629  function test_reason_values_are_unique  def test_reason_values_are_unique()
- L632-L639  function test_every_failing_exit_uses_the_reason_table  def test_every_failing_exit_uses_the_reason_table()
- L642-L645  function test_reason_templates_render_without_stray_placeholders  def test_reason_templates_render_without_stray_placeholders()
- L649-L656  function test_timeline_reader_is_imported_from_the_s0_01_checker  def test_timeline_reader_is_imported_from_the_s0_01_checker()
- L667-L677  function test_fifo_at_any_evidence_path_fails_in_bounded_time  def test_fifo_at_any_evidence_path_fails_in_bounded_time(passing, rel)
- L685-L691  function test_directory_at_an_evidence_path_is_a_named_failure  def test_directory_at_an_evidence_path_is_a_named_failure(passing, rel)
- L702-L708  function test_absent_file_is_a_failure_not_a_deferral  def test_absent_file_is_a_failure_not_a_deferral(passing, rel)
- L711-L714  function test_deferred_when_nothing_was_captured  def test_deferred_when_nothing_was_captured(tmp_path)
- L717-L722  function test_deferred_when_the_root_has_no_leg_directory  def test_deferred_when_the_root_has_no_leg_directory(tmp_path)
- L725-L729  function test_usage_error_is_64_not_a_deferral  def test_usage_error_is_64_not_a_deferral(tmp_path)
- L732-L736  function test_malformed_json_is_a_named_failure  def test_malformed_json_is_a_named_failure(passing)
- L740-L743  function test_spec_validates_against_the_schema  def test_spec_validates_against_the_schema()
- L746-L751  function test_spec_proof_id_and_checker_path  def test_spec_proof_id_and_checker_path()
- L754-L760  function test_spec_declares_the_stub_routes_the_deployment_has  def test_spec_declares_the_stub_routes_the_deployment_has()
- L763-L767  function test_every_leg_declares_the_same_inputs  def test_every_leg_declares_the_same_inputs()
- L772-L784  class _Handler  class _Handler(http.server.BaseHTTPRequestHandler)
- L775-L781  method do_GET  def do_GET(self)
- L783-L784  method log_message  def log_message(self, *args)
- L787-L792  function _serve  def _serve(status)
- L795-L800  function _closed_port  def _closed_port() -> int
- L803-L809  function run_probe  def run_probe(url, env_key="present")
- L813-L822  function test_probe_maps_each_http_status  def test_probe_maps_each_http_status(status, expected)
- L825-L833  function test_probe_key_absent_is_10  def test_probe_key_absent_is_10()
- L836-L841  function test_probe_closed_port_is_13_not_credential_rejected  def test_probe_closed_port_is_13_not_credential_rejected()
- L844-L846  function test_probe_dns_failure_is_13  def test_probe_dns_failure_is_13()
- L849-L851  function test_probe_usage_error_is_64  def test_probe_usage_error_is_64()
- L854-L862  function test_probe_never_prints_the_key  def test_probe_never_prints_the_key()
- L865-L871  function test_probe_json_reason_map_covers_exactly_the_credential_verdicts  def test_probe_json_reason_map_covers_exactly_the_credential_verdicts()
- L874-L880  function test_probe_exit_constants_match_the_reason_map  def test_probe_exit_constants_match_the_reason_map()
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 6 hits over 1 files ---
AF-AP-34: 3
    tests/test_s0_03_omniroute.py:891: """AF-AP-34 / AF-AP-59: `pkill`, `pgrep -f` and `killall` match the owner's production
    tests/test_s0_03_omniroute.py:891: """AF-AP-34 / AF-AP-59: `pkill`, `pgrep -f` and `killall` match the owner's production
    tests/test_s0_03_omniroute.py:892: processes by name. Four `pkill -x buzz-relay` already restarted buzz-prod-relay-1."""
AF-AP-80: 2
    tests/test_s0_03_omniroute.py:1567: assert "pc_mention.sh" in RUNNER.read_text()
    tests/test_s0_03_omniroute.py:1576: assert "current-framedir" in PC_MENTION.read_text()
AF-AP-59: 1
    tests/test_s0_03_omniroute.py:891: """AF-AP-34 / AF-AP-59: `pkill`, `pgrep -f` and `killall` match the owner's production

## graft ask — how does the S0-03 checker bind the call-log row to the leg, screen credentials recursively, grade the exact terminal call and require aware instants and POST
graft ask — "how does the S0-03 checker bind the call-log row to the leg, screen credentials recursively, grade the exact terminal call and require aware instants and POST"  (lexical)

1. check_identity_route · function  [symbol]
   proofs/S0-03/check_omniroute_roundtrip.py:L481-L572
   def check_identity_route(requests: dict, direct: dict, leg_record: dict, spec: dict)

2. main · function  [symbol]
   proofs/S0-03/tools/pc/direct_responses_probe.py:L200-L281
   def main(argv) -> int

3. hermes_env_names.py · file  [symbol]
   proofs/S0-03/tools/pc/hermes_env_names.py

4. probe_omniroute.py · file  [symbol]
   proofs/S0-03/probe_omniroute.py

5. _require_in_window · function  [symbol]
   proofs/S0-03/check_omniroute_roundtrip.py:L470-L478
   def _require_in_window(row: dict, window: dict)

6. direct_responses_probe.py · file  [symbol]
   proofs/S0-03/tools/pc/direct_responses_probe.py

7. main · function  [symbol]
   proofs/S0-03/tools/pc/hermes_env_names.py:L126-L144
   def main(argv) -> int

8. main · function  [symbol]
   proofs/S0-03/probe_omniroute.py:L56-L84
   def main()

## symbol _walk_credentials
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/proofs/S0-03/check_omniroute_roundtrip.py::_walk_credentials')",
      "name": "_walk_credentials",
      "name": "check_transport",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-03/check_omniroute_roundtrip.py::_walk_credentials')",
### ripwire callers
<callers of="_walk_credentials" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=_walk_credentials">

## symbol _instant
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 2,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-03/check_omniroute_roundtrip.py::_instant')",
      "name": "_require_in_window",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-03/check_omniroute_roundtrip.py::_instant')",
### ripwire callers
<callers of="_instant" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=_instant">

## symbol check_roundtrip
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-03/check_omniroute_roundtrip.py::check_roundtrip')",
      "name": "check_bundle",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-03/check_omniroute_roundtrip.py::check_roundtrip')",
### ripwire callers
<callers of="check_roundtrip" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=check_roundtrip">

## symbol transport_method
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching 'transport_method'.",
  "summary": "No node found matching 'transport_method'.",
### ripwire callers

## symbol check_env_record
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-03/check_omniroute_roundtrip.py::check_env_record')",
      "name": "check_bundle",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-03/check_omniroute_roundtrip.py::check_env_record')",
### ripwire callers
<callers of="check_env_record" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=check_env_record">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
<test-gate changed="1" impacted="0" tests="0" untested="0" shown_tests="0" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="10" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="a98261c41+dirty" next="--situ">
