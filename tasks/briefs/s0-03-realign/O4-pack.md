# lane context pack — 6a5f660 2026-09-18T18:54Z
files: proofs/S0-03/check_omniroute_roundtrip.py proofs/S0-03/tools/pc/collect_leg.sh proofs/S0-03/tools/pc/direct_responses_probe.py proofs/S0-03/tools/pc/run_s0_03_legs.sh tests/test_s0_03_omniroute.py
symbols: check_identity_route

## proofs/S0-03/check_omniroute_roundtrip.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — proofs/S0-03/check_omniroute_roundtrip.py
- L109-L126  function _load_s0_01_module  def _load_s0_01_module()
- L181-L195  function is_credential_name  def is_credential_name(name: str) -> bool
- L206-L207  class Failure  class Failure(Exception)
- L210-L211  class Deferred  class Deferred(Exception)
- L214-L215  function _reason  def _reason(key: str, *args) -> str
- L218-L219  function _fail  def _fail(key: str, *args)
- L223-L230  function _require_file  def _require_file(path: Path, name: str) -> Path
- L233-L238  function _reject_constant  def _reject_constant(token: str)
- L241-L246  function _read_json  def _read_json(path: Path, name: str)
- L249-L256  function _read_yaml  def _read_yaml(path: Path, name: str)
- L259-L262  function _obj  def _obj(value, name: str) -> dict
- L265-L268  function _str  def _str(value, name: str) -> str
- L281-L282  class Usage  class Usage(Exception)
- L285-L319  function parse_args  def parse_args(argv) -> dict
- L322-L331  function _is_stub  def _is_stub(name: str, stub_routes) -> bool
- L338-L347  function _authorization_presented  def _authorization_presented(direct: dict) -> bool
- L350-L372  function check_credential_at_the_gate  def check_credential_at_the_gate(direct: dict)
- L375-L382  function check_credential_in_the_environ  def check_credential_in_the_environ(env_names)
- L386-L425  function check_direct_stream  def check_direct_stream(direct: dict)
- L429-L432  function check_identity_model  def check_identity_model(direct: dict, spec: dict)
- L436-L457  function _rows_by_leg  def _rows_by_leg(requests: dict) -> dict
- L460-L477  function check_row_counts  def check_row_counts(requests: dict)
- L480-L491  function _instant  def _instant(value, name: str)
- L494-L502  function _require_in_window  def _require_in_window(row: dict, window: dict)
- L505-L596  function check_identity_route  def check_identity_route(requests: dict, direct: dict, leg_record: dict, spec: dict)
- L600-L613  function _updates  def _updates(entries)
- L616-L624  function _agent_text  def _agent_text(entries) -> str
- L627-L685  function check_roundtrip  def check_roundtrip(entries, nonce2: str)
- L689-L697  function _provider_block  def _provider_block(profile) -> tuple[str, dict]
- L700-L717  function _walk_credentials  def _walk_credentials(node, path: str)
- L720-L744  function check_transport  def check_transport(profile)
- L748-L762  function check_env  def check_env(env_names)
- L766-L803  function check_env_record  def check_env_record(record: dict, leg: dict)
- L807-L818  function load_direct  def load_direct(root: Path) -> dict
- L821-L850  function load_bundle  def load_bundle(root: Path, direct: dict) -> dict
- L853-L873  function check_bundle  def check_bundle(root: Path, spec: dict) -> str
- L876-L890  function main  def main(argv) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-03/tools/pc/collect_leg.sh
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
graft skeleton — proofs/S0-03/tools/pc/collect_leg.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-03/tools/pc/direct_responses_probe.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — proofs/S0-03/tools/pc/direct_responses_probe.py
- L77-L78  function _utc  def _utc() -> str
- L81-L96  function read_key  def read_key(key_file: str) -> str
- L99-L118  function parse_sse  def parse_sse(raw: str)
- L121-L133  function _first_model  def _first_model(events)
- L136-L146  function _first  def _first(events, *keys)
- L149-L180  function parse_args  def parse_args(argv) -> dict
- L183-L197  function build_headers  def build_headers(key)
- L200-L281  function main  def main(argv) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 2 hits over 1 files ---
AP-1: 2
    proofs/S0-03/tools/pc/direct_responses_probe.py:151: base_url = os.environ.get("S0_03_BASE_URL", DEFAULT_BASE_URL)
    proofs/S0-03/tools/pc/direct_responses_probe.py:203: os.environ.get("S0_03_KEY_FILE") or DEFAULT_KEY_FILE)

## proofs/S0-03/tools/pc/run_s0_03_legs.sh
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
graft skeleton — proofs/S0-03/tools/pc/run_s0_03_legs.sh

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## tests/test_s0_03_omniroute.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

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
- L147-L150  function test_credential_name_recognises_authorization_header_identity  def test_credential_name_recognises_authorization_header_identity()
- L166-L170  function test_committed_negative_bundle_exact_reason  def test_committed_negative_bundle_exact_reason(bundle, reason)
- L173-L176  function test_credential_absent_reason_is_the_seed_kill_switch  def test_credential_absent_reason_is_the_seed_kill_switch()
- L179-L185  function test_every_negative_bundle_is_a_declared_spec_leg  def test_every_negative_bundle_is_a_declared_spec_leg()
- L188-L196  function test_each_negative_leg_reason_is_produced_verbatim  def test_each_negative_leg_reason_is_produced_verbatim()
- L199-L210  function test_fixtures_track_the_spec_expected_model_id  def test_fixtures_track_the_spec_expected_model_id()
- L213-L228  function test_every_bundle_has_provenance  def test_every_bundle_has_provenance()
- L233-L240  function test_conjunct_i_direct_stream  def test_conjunct_i_direct_stream(passing)
- L243-L258  function test_conjunct_i_rejects_a_vacuous_nonce  def test_conjunct_i_rejects_a_vacuous_nonce(passing)
- L261-L266  function test_conjunct_i_requires_the_compression_header_was_sent  def test_conjunct_i_requires_the_compression_header_was_sent(passing)
- L269-L279  function test_conjunct_ii_identity_model  def test_conjunct_ii_identity_model(passing)
- L282-L290  function test_conjunct_iii_identity_route  def test_conjunct_iii_identity_route(passing)
- L293-L305  function test_conjunct_iii_catches_every_declared_stub_id_and_its_namespace  def test_conjunct_iii_catches_every_declared_stub_id_and_its_namespace(passing)
- L308-L314  function test_conjunct_iii_binds_the_row_to_our_route  def test_conjunct_iii_binds_the_row_to_our_route(passing)
- L317-L324  function test_conjunct_iii_requires_the_two_instruments_to_agree  def test_conjunct_iii_requires_the_two_instruments_to_agree(passing)
- L327-L338  function test_conjunct_iv_roundtrip_requires_a_completed_tool_call  def test_conjunct_iv_roundtrip_requires_a_completed_tool_call(passing)
- L341-L350  function test_conjunct_iv_roundtrip_requires_a_tool_call_at_all  def test_conjunct_iv_roundtrip_requires_a_tool_call_at_all(passing)
- L353-L361  function test_conjunct_iv_requires_exactly_one_prompt_turn  def test_conjunct_iv_requires_exactly_one_prompt_turn(passing)
- L364-L373  function test_conjunct_iv_requires_the_nonce_in_the_final_text  def test_conjunct_iv_requires_the_nonce_in_the_final_text(passing)
- L376-L387  function test_conjunct_iv_binds_the_answer_to_the_question  def test_conjunct_iv_binds_the_answer_to_the_question(passing)
- L393-L399  function test_transport_requires_exact_post_on_both_rows  def test_transport_requires_exact_post_on_both_rows(passing, leg, method)
- L401-L412  function test_conjunct_v_transport  def test_conjunct_v_transport(passing)
- L429-L437  function test_credential_screen_recurses_over_the_whole_provider_block  def test_credential_screen_recurses_over_the_whole_provider_block(passing, mutation, path)
- L440-L447  function test_credential_screen_allows_only_the_provider_key_env_name  def test_credential_screen_allows_only_the_provider_key_env_name(passing)
- L456-L469  function test_credential_screen_rejects_authorization_header_by_identity  def test_credential_screen_rejects_authorization_header_by_identity( passing, header, value)
- L472-L479  function test_conjunct_v_rejects_an_inline_key_in_the_captured_profile  def test_conjunct_v_rejects_an_inline_key_in_the_captured_profile(passing)
- L487-L499  function test_conjunct_v_rejects_a_credential_in_extra_headers  def test_conjunct_v_rejects_a_credential_in_extra_headers(passing, line, named)
- L502-L508  function test_conjunct_v_still_accepts_the_key_env_NAME  def test_conjunct_v_still_accepts_the_key_env_NAME(passing)
- L511-L516  function test_conjunct_v_requires_the_compression_header_in_the_profile  def test_conjunct_v_requires_the_compression_header_in_the_profile(passing)
- L519-L527  function test_conjunct_vi_env  def test_conjunct_vi_env(passing)
- L530-L541  function test_first_failure_order_is_pinned  def test_first_failure_order_is_pinned(passing)
- L544-L553  function test_a_credential_verdict_outranks_the_stream_conjunct  def test_a_credential_verdict_outranks_the_stream_conjunct(passing)
- L556-L566  function test_a_present_but_refused_key_is_rejected_not_absent  def test_a_present_but_refused_key_is_rejected_not_absent(passing)
- L569-L582  function test_a_401_on_a_request_that_sent_no_key_is_the_kill_switch  def test_a_401_on_a_request_that_sent_no_key_is_the_kill_switch(passing)
- L573-L578  function strip_auth  def strip_auth(record)
- L585-L595  function test_a_401_with_an_unreadable_header_record_is_a_bundle_failure  def test_a_401_with_an_unreadable_header_record_is_a_bundle_failure(passing)
- L588-L590  function break_headers  def break_headers(record)
- L598-L605  function test_an_environ_without_the_key_is_the_kill_switch  def test_an_environ_without_the_key_is_the_kill_switch(passing)
- L634-L644  function test_env_allowlist_is_a_closed_exact_set  def test_env_allowlist_is_a_closed_exact_set(name, rejected)
- L647-L652  function test_env_allowlist_reports_deterministically  def test_env_allowlist_reports_deterministically()
- L656-L658  function test_reason_values_are_unique  def test_reason_values_are_unique()
- L661-L668  function test_every_failing_exit_uses_the_reason_table  def test_every_failing_exit_uses_the_reason_table()
- L671-L674  function test_reason_templates_render_without_stray_placeholders  def test_reason_templates_render_without_stray_placeholders()
- L678-L685  function test_timeline_reader_is_imported_from_the_s0_01_checker  def test_timeline_reader_is_imported_from_the_s0_01_checker()
- L696-L706  function test_fifo_at_any_evidence_path_fails_in_bounded_time  def test_fifo_at_any_evidence_path_fails_in_bounded_time(passing, rel)
- L714-L720  function test_directory_at_an_evidence_path_is_a_named_failure  def test_directory_at_an_evidence_path_is_a_named_failure(passing, rel)
- L731-L737  function test_absent_file_is_a_failure_not_a_deferral  def test_absent_file_is_a_failure_not_a_deferral(passing, rel)
- L740-L743  function test_deferred_when_nothing_was_captured  def test_deferred_when_nothing_was_captured(tmp_path)
- L746-L751  function test_deferred_when_the_root_has_no_leg_directory  def test_deferred_when_the_root_has_no_leg_directory(tmp_path)
- L754-L758  function test_usage_error_is_64_not_a_deferral  def test_usage_error_is_64_not_a_deferral(tmp_path)
- L761-L765  function test_malformed_json_is_a_named_failure  def test_malformed_json_is_a_named_failure(passing)
- L769-L772  function test_spec_validates_against_the_schema  def test_spec_validates_against_the_schema()
- L775-L780  function test_spec_proof_id_and_checker_path  def test_spec_proof_id_and_checker_path()
- L783-L789  function test_spec_declares_the_stub_routes_the_deployment_has  def test_spec_declares_the_stub_routes_the_deployment_has()
- L792-L796  function test_every_leg_declares_the_same_inputs  def test_every_leg_declares_the_same_inputs()
- L801-L813  class _Handler  class _Handler(http.server.BaseHTTPRequestHandler)
- L804-L810  method do_GET  def do_GET(self)
- L812-L813  method log_message  def log_message(self, *args)
- L816-L821  function _serve  def _serve(status)
- L824-L829  function _closed_port  def _closed_port() -> int
- L832-L838  function run_probe  def run_probe(url, env_key="present")
- L842-L851  function test_probe_maps_each_http_status  def test_probe_maps_each_http_status(status, expected)
- L854-L862  function test_probe_key_absent_is_10  def test_probe_key_absent_is_10()
- L865-L870  function test_probe_closed_port_is_13_not_credential_rejected  def test_probe_closed_port_is_13_not_credential_rejected()
- L873-L875  function test_probe_dns_failure_is_13  def test_probe_dns_failure_is_13()
- L878-L880  function test_probe_usage_error_is_64  def test_probe_usage_error_is_64()
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 6 hits over 1 files ---
AF-AP-34: 3
    tests/test_s0_03_omniroute.py:920: """AF-AP-34 / AF-AP-59: `pkill`, `pgrep -f` and `killall` match the owner's production
    tests/test_s0_03_omniroute.py:920: """AF-AP-34 / AF-AP-59: `pkill`, `pgrep -f` and `killall` match the owner's production
    tests/test_s0_03_omniroute.py:921: processes by name. Four `pkill -x buzz-relay` already restarted buzz-prod-relay-1."""
AF-AP-80: 2
    tests/test_s0_03_omniroute.py:1629: assert "pc_mention.sh" in RUNNER.read_text()
    tests/test_s0_03_omniroute.py:1638: assert "current-framedir" in PC_MENTION.read_text()
AF-AP-59: 1
    tests/test_s0_03_omniroute.py:920: """AF-AP-34 / AF-AP-59: `pkill`, `pgrep -f` and `killall` match the owner's production

## graft ask — How does the S0-03 checker bind each OmniRoute call_logs row to a leg (check_identity_route, check_transport), and where does collect_leg.sh filter by route?
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
graft ask — "How does the S0-03 checker bind each OmniRoute call_logs row to a leg (check_identity_route, check_transport), and where does collect_leg.sh filter by route?"  (lexical)

1. check_identity_route · function  [symbol]
   proofs/S0-03/check_omniroute_roundtrip.py:L505-L596
   def check_identity_route(requests: dict, direct: dict, leg_record: dict, spec: dict)

2. main · function  [symbol]
   proofs/S0-03/tools/pc/direct_responses_probe.py:L200-L281
   def main(argv) -> int

3. probe_omniroute.py · file  [symbol]
   proofs/S0-03/probe_omniroute.py

4. main · function  [symbol]
   proofs/S0-03/tools/pc/hermes_env_names.py:L126-L144
   def main(argv) -> int

5. check_bundle · function  [symbol]
   proofs/S0-03/check_omniroute_roundtrip.py:L853-L873
   def check_bundle(root: Path, spec: dict) -> str

6. direct_responses_probe.py · file  [symbol]
   proofs/S0-03/tools/pc/direct_responses_probe.py

7. main · function  [symbol]
   proofs/S0-03/probe_omniroute.py:L56-L84
   def main()

8. resolve_identity · function  [symbol]
   proofs/S0-03/tools/pc/hermes_env_names.py:L82-L101
   def resolve_identity(args)

## symbol check_identity_route
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-03/check_omniroute_roundtrip.py::check_identity_route')",
      "name": "check_bundle",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-03/check_omniroute_roundtrip.py::check_identity_route')",
### ripwire callers
<callers of="check_identity_route" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="110" counts_floor="1" next="--uses=check_identity_route">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
<test-gate changed="1" impacted="0" tests="0" untested="0" shown_tests="0" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="10" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="6a5f6603d+dirty" next="--situ">
