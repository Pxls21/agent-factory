# lane context pack — c367d76 2026-09-17T12:59Z
files: proofs/S0-06/adapter/factory_memory.py tests/test_s0_06_four_scope.py
symbols: load_bindings authorize _bind _run_with_bindings test_malformed_binding_scopes_fail_closed_through_the_public_cli test_duplicate_binding_identity_tuples_fail_closed_through_each_public_cli test_a_well_formed_scratch_binding_still_authorizes_exactly_its_scopes

## proofs/S0-06/adapter/factory_memory.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
[graft] refreshed the graph (1 file changed) before answering

graft skeleton — proofs/S0-06/adapter/factory_memory.py
- L97-L98  class _BindingsConfigurationError  class _BindingsConfigurationError(ValueError)
- L101-L107  class Binding  class Binding(NamedTuple)
- L110-L117  function scopes_for  def scopes_for(binding: Binding) -> dict
- L120-L163  function load_bindings  def load_bindings(path: Path = BINDINGS_PATH) -> list
- L166-L186  function authorize  def authorize(tuple_obj: dict, table: list) -> dict | None
- L189-L216  function normalize_hit  def normalize_hit(hit: dict, scope: str, updated_at: str | None) -> dict
- L219-L249  function merge  def merge(records_by_scope: dict) -> list
- L252-L261  function idempotency_path  def idempotency_path(session: str, turn: str, event_id: str) -> str
- L264-L267  class _Denied  class _Denied(Exception)
- L265-L267  method __init__  def __init__(self, reason: str)
- L270-L449  class FactoryMemory  class FactoryMemory
- L273-L280  method __init__  def __init__(self, base_url=DEFAULT_BASE_URL, token=None, bindings_path=BINDINGS_PATH, timeout_s=DEFAULT_TIMEOUT_S, events=None)
- L283-L295  method _emit  def _emit(self, event, reason, **fields)
- L298-L308  method _bind  def _bind(self, tuple_obj)
- L311-L324  method _request  def _request(self, method, path, body=None, event_path=None, event_fields=None)
- L326-L335  method _search  def _search(self, workspace, project, query, limit)
- L337-L343  method _page_times  def _page_times(self, workspace, project)
- L346-L386  method recall  def recall(self, tuple_obj, query, limit=DEFAULT_LIMIT)
- L388-L449  method write  def write(self, tuple_obj, active_scope, record)
- L452-L456  function _read_json_file  def _read_json_file(path)
- L459-L466  function _read_token  def _read_token(path)
- L469-L486  function _build_parser  def _build_parser()
- L489-L513  function _main  def _main(argv=None)
- L516-L533  function main  def main(argv=None)
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 3 hits over 1 files ---
AP-32: 2
    proofs/S0-06/adapter/factory_memory.py:261: return "observations/" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16] + ".md"
    proofs/S0-06/adapter/factory_memory.py:332: query_sha256_16 = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]
AF-AP-70: 1
    proofs/S0-06/adapter/factory_memory.py:491: # DOCUMENTED LIMIT (F-21): every READ path in this module is lstat+S_ISREG guarded, but these

## tests/test_s0_06_four_scope.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — tests/test_s0_06_four_scope.py
- L52-L56  function _load  def _load(name, path)
- L65-L67  function _hit  def _hit(scope, project, path, title, snippet, rank)
- L70-L76  function _closed_port  def _closed_port()
- L82-L125  class _Recorder  class _Recorder(BaseHTTPRequestHandler)
- L87-L88  method log_message  def log_message(self, *_args)
- L90-L96  method _send  def _send(self, payload)
- L98-L115  method do_GET  def do_GET(self)
- L117-L125  method do_POST  def do_POST(self)
- L128-L148  class _Server  class _Server
- L129-L135  method __init__  def __init__(self, extra_pages=(), bad_search=_UNSET)
- L138-L139  method base_url  def base_url(self)
- L142-L143  method calls  def calls(self)
- L145-L148  method close  def close(self)
- L152-L157  function server  def server()
- L160-L167  function _repair_wrong_scope  def _repair_wrong_scope(dest: Path) -> Path
- L170-L179  function _repair_leak  def _repair_leak(dest: Path) -> Path
- L183-L184  function good  def good(tmp_path)
- L187-L189  function _run_checker  def _run_checker(root)
- L192-L194  function _verdict  def _verdict(root)
- L197-L200  function _edit  def _edit(path: Path, fn)
- L203-L206  function _edit_recalls  def _edit_recalls(root: Path, fn)
- L211-L215  function test_authorized_tuples_are_accepted  def test_authorized_tuples_are_accepted()
- L219-L228  function test_every_single_field_corruption_is_denied  def test_every_single_field_corruption_is_denied(field)
- L237-L238  function test_shape_violations_are_denied  def test_shape_violations_are_denied(presented)
- L241-L249  function test_the_committed_table_is_the_only_authorization_source  def test_the_committed_table_is_the_only_authorization_source()
- L252-L262  function test_a_malformed_table_row_can_never_authorize_a_null_tuple  def test_a_malformed_table_row_can_never_authorize_a_null_tuple()
- L265-L272  function test_cli_has_no_bindings_override_flag  def test_cli_has_no_bindings_override_flag()
- L275-L283  function test_seed_negative_fixture_is_a_real_looking_tuple_with_one_wrong_field  def test_seed_negative_fixture_is_a_real_looking_tuple_with_one_wrong_field()
- L288-L295  function test_scopes_for_is_the_docs_03_mapping  def test_scopes_for_is_the_docs_03_mapping()
- L300-L303  function _four_way  def _four_way(scope, rank)
- L306-L310  function _collision_input  def _collision_input()
- L313-L317  function test_merge_is_byte_identical_on_a_repeat_call  def test_merge_is_byte_identical_on_a_repeat_call()
- L320-L326  function test_merge_is_independent_of_input_order  def test_merge_is_independent_of_input_order()
- L329-L335  function test_merge_resolves_a_four_way_collision_to_the_agent_record  def test_merge_resolves_a_four_way_collision_to_the_agent_record()
- L338-L341  function test_merge_output_is_sorted_by_precedence_then_stable_id  def test_merge_output_is_sorted_by_precedence_then_stable_id()
- L344-L348  function test_merge_does_not_mutate_its_input  def test_merge_does_not_mutate_its_input()
- L351-L353  function test_merge_carries_the_docs_03_read_contract_fields  def test_merge_carries_the_docs_03_read_contract_fields()
- L356-L360  function test_a_lower_precedence_only_record_survives_the_merge  def test_a_lower_precedence_only_record_survives_the_merge()
- L365-L367  function test_public_adapter_surface_is_recall_and_write_only  def test_public_adapter_surface_is_recall_and_write_only()
- L370-L383  function test_no_module_level_mutation_entry_point_exists  def test_no_module_level_mutation_entry_point_exists()
- L389-L396  function test_write_refuses_a_scope_the_binding_does_not_authorize  def test_write_refuses_a_scope_the_binding_does_not_authorize(scope, server)
- L399-L413  function test_a_company_write_is_refused_even_when_the_table_authorizes_it  def test_a_company_write_is_refused_even_when_the_table_authorizes_it(server)
- L416-L429  function test_write_lands_in_the_active_scope_only  def test_write_lands_in_the_active_scope_only(server)
- L432-L445  function test_a_retry_with_the_same_key_is_a_recorded_no_op  def test_a_retry_with_the_same_key_is_a_recorded_no_op()
- L448-L459  function test_the_idempotency_key_covers_every_component  def test_the_idempotency_key_covers_every_component()
- L463-L469  function test_an_incomplete_record_is_refused_before_the_write  def test_an_incomplete_record_is_refused_before_the_write(missing, server)
- L474-L489  function test_recall_queries_every_authorized_scope_on_the_read_route  def test_recall_queries_every_authorized_scope_on_the_read_route(server)
- L492-L499  function test_a_partly_authorized_binding_never_touches_the_other_scopes  def test_a_partly_authorized_binding_never_touches_the_other_scopes(server)
- L502-L517  function test_the_recording_server_answers_with_the_real_ai_memory_shapes  def test_the_recording_server_answers_with_the_real_ai_memory_shapes(server)
- L520-L530  function test_the_record_timestamp_comes_from_the_page_listing  def test_the_record_timestamp_comes_from_the_page_listing(server)
- L533-L539  function test_every_request_carries_the_bearer_token  def test_every_request_carries_the_bearer_token(server)
- L542-L552  function test_a_failing_scope_degrades_visibly_and_names_the_scope  def test_a_failing_scope_degrades_visibly_and_names_the_scope(server, tmp_path)
- L555-L568  function test_the_token_never_reaches_the_event_stream  def test_the_token_never_reaches_the_event_stream(tmp_path, server)
- L571-L574  function test_the_adapter_uses_no_clock_and_no_randomness  def test_the_adapter_uses_no_clock_and_no_randomness()
- L579-L607  function _run_with_bindings  def _run_with_bindings(tmp_path, rows, *, verb="recall", base_url=None)
- L623-L632  function test_malformed_binding_scopes_fail_closed_through_the_public_cli  def test_malformed_binding_scopes_fail_closed_through_the_public_cli(tmp_path, scopes, message)
- L636-L646  function test_duplicate_binding_identity_tuples_fail_closed_through_each_public_cli  def test_duplicate_binding_identity_tuples_fail_closed_through_each_public_cli(tmp_path, verb)
- L649-L657  function test_a_well_formed_scratch_binding_still_authorizes_exactly_its_scopes  def test_a_well_formed_scratch_binding_still_authorizes_exactly_its_scopes(tmp_path, server)
- L660-L677  function test_the_negative_control_denies_without_a_network_call  def test_the_negative_control_denies_without_a_network_call(tmp_path)
- L680-L686  function test_the_cli_denial_line_is_exactly_the_seed_reason  def test_the_cli_denial_line_is_exactly_the_seed_reason()
- L692-L702  function test_committed_bundles_carry_the_real_ai_memory_record_shapes  def test_committed_bundles_carry_the_real_ai_memory_record_shapes(bundle)
- L706-L717  function test_committed_bundle_recall_records_match_the_adapters_own_shape  def test_committed_bundle_recall_records_match_the_adapters_own_shape(bundle)
- L720-L725  function test_the_honeytoken_fixture_names_all_four_scopes  def test_the_honeytoken_fixture_names_all_four_scopes()
- L730-L734  function test_a_repaired_wrong_scope_bundle_passes  def test_a_repaired_wrong_scope_bundle_passes(good)
- L737-L740  function test_a_repaired_leak_bundle_passes  def test_a_repaired_leak_bundle_passes(tmp_path)
- L743-L760  function test_the_checker_prints_exactly_one_stdout_line  def test_the_checker_prints_exactly_one_stdout_line(good, tmp_path)
- L763-L766  function test_an_absent_evidence_root_defers  def test_an_absent_evidence_root_defers(tmp_path)
- L769-L771  function test_the_sandbox_tree_has_no_captured_evidence_so_the_spec_positive_leg_defers  def test_the_sandbox_tree_has_no_captured_evidence_so_the_spec_positive_leg_defers()
- L776-L779  function test_the_committed_leak_bundle_is_refused  def test_the_committed_leak_bundle_is_refused()
- L782-L785  function test_the_committed_wrong_scope_bundle_is_refused  def test_the_committed_wrong_scope_bundle_is_refused()
- L790-L792  function test_substrate_commit_mutant  def test_substrate_commit_mutant(good)
- L795-L797  function test_substrate_version_mutant  def test_substrate_version_mutant(good)
- L800-L804  function test_substrate_binary_digest_mutant  def test_substrate_binary_digest_mutant(good)
- L807-L815  function test_posture_wrong_value_mutant  def test_posture_wrong_value_mutant(good)
- L810-L812  function unsafe  def unsafe(doc)
- L818-L821  function test_posture_absent_key_mutant  def test_posture_absent_key_mutant(good)
- L824-L831  function test_a_declared_posture_the_instance_never_received_is_refused  def test_a_declared_posture_the_instance_never_received_is_refused(good)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 13 hits over 1 files ---
AF-AP-80: 9
    tests/test_s0_06_four_scope.py:381: assert route not in source
    tests/test_s0_06_four_scope.py:383: assert "/admin/write-page" in source
    tests/test_s0_06_four_scope.py:574: assert token not in source
    tests/test_s0_06_four_scope.py:677: assert "http_request" not in events.read_text()
    tests/test_s0_06_four_scope.py:1112: assert lock["selected_core"]["ai-memory"]["commit"] not in CHECKER_PATH.read_text()
    tests/test_s0_06_four_scope.py:1508: assert lock["selected_core"]["ai-memory"]["observed_version"] not in CHECKER_PATH.read_text()
    ... +3
AF-AP-34: 2
    tests/test_s0_06_four_scope.py:1149: for banned in ("pkill", "killall", "pgrep"):
    tests/test_s0_06_four_scope.py:1149: for banned in ("pkill", "killall", "pgrep"):
AF-AP-35: 2
    tests/test_s0_06_four_scope.py:980: path.write_text(path.read_text().replace(tokens["team"], "HT-team-scrubbed"))
    tests/test_s0_06_four_scope.py:987: path.write_text(path.read_text().replace(tokens["agent"], "HT-agent-scrubbed"))

## graft ask — where is a binding row validated and consumed for authorization
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
graft ask — "where is a binding row validated and consumed for authorization"  (lexical)

1. _bind · method  [symbol]
   proofs/S0-06/adapter/factory_memory.py:L298-L308
   def _bind(self, tuple_obj)

2. Binding · class  [symbol]
   proofs/S0-06/adapter/factory_memory.py:L101-L107
   class Binding(NamedTuple)

3. FactoryMemory · class  [symbol]
   proofs/S0-06/adapter/factory_memory.py:L270-L449
   class FactoryMemory

4. authorize · function  [symbol]
   proofs/S0-06/adapter/factory_memory.py:L166-L186
   def authorize(tuple_obj: dict, table: list) -> dict | None

5. load_bindings · function  [symbol]
   proofs/S0-06/adapter/factory_memory.py:L120-L163
   def load_bindings(path: Path = BINDINGS_PATH) -> list

6. recall · method  [symbol]
   proofs/S0-06/adapter/factory_memory.py:L346-L386
   def recall(self, tuple_obj, query, limit=DEFAULT_LIMIT)

7. scopes_for · function  [symbol]
   proofs/S0-06/adapter/factory_memory.py:L110-L117
   def scopes_for(binding: Binding) -> dict

8. write · method  [symbol]
   proofs/S0-06/adapter/factory_memory.py:L388-L449
   def write(self, tuple_obj, active_scope, record)

## symbol load_bindings
### GitNexus impact (upstream)
unmapped — GitNexus index absent
### code-review-graph callers_of / tests_for
unmapped — code-review-graph graph absent (run: /home/rocco/venv-crg/bin/code-review-graph build)
### ripwire callers
<callers of="load_bindings" defs="1" count="10" root="/home/rocco/agent-factory/.lanes/pc-m4.md--c367d76/tree" hop_tested="1" hop_untested="9" shown="10" capped="0" total="10" has_more="0" next_offset="10" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=load_bindings">

## symbol authorize
### GitNexus impact (upstream)
unmapped — GitNexus index absent
### code-review-graph callers_of / tests_for
unmapped — code-review-graph graph absent (run: /home/rocco/venv-crg/bin/code-review-graph build)
### ripwire callers
<callers of="authorize" defs="1" count="7" root="/home/rocco/agent-factory/.lanes/pc-m4.md--c367d76/tree" hop_tested="1" hop_untested="6" shown="7" capped="0" total="7" has_more="0" next_offset="7" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=authorize">

## symbol _bind
### GitNexus impact (upstream)
unmapped — GitNexus index absent
### code-review-graph callers_of / tests_for
unmapped — code-review-graph graph absent (run: /home/rocco/venv-crg/bin/code-review-graph build)
### ripwire callers
<callers of="_bind" defs="2" count="7" root="/home/rocco/agent-factory/.lanes/pc-m4.md--c367d76/tree" hop_tested="2" hop_untested="5" shown="7" capped="0" total="7" has_more="0" next_offset="7" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=_bind">

## symbol _run_with_bindings
### GitNexus impact (upstream)
unmapped — GitNexus index absent
### code-review-graph callers_of / tests_for
unmapped — code-review-graph graph absent (run: /home/rocco/venv-crg/bin/code-review-graph build)
### ripwire callers
<callers of="_run_with_bindings" defs="1" count="3" root="/home/rocco/agent-factory/.lanes/pc-m4.md--c367d76/tree" hop_tested="0" hop_untested="3" shown="3" capped="0" total="3" has_more="0" next_offset="3" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=_run_with_bindings">

## symbol test_malformed_binding_scopes_fail_closed_through_the_public_cli
### GitNexus impact (upstream)
unmapped — GitNexus index absent
### code-review-graph callers_of / tests_for
unmapped — code-review-graph graph absent (run: /home/rocco/venv-crg/bin/code-review-graph build)
### ripwire callers
<callers of="test_malformed_binding_scopes_fail_closed_through_the_public_cli" defs="1" count="0" root="/home/rocco/agent-factory/.lanes/pc-m4.md--c367d76/tree" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=test_malformed_binding_scopes_fail_closed_through_the_public_cli">

## symbol test_duplicate_binding_identity_tuples_fail_closed_through_each_public_cli
### GitNexus impact (upstream)
unmapped — GitNexus index absent
### code-review-graph callers_of / tests_for
unmapped — code-review-graph graph absent (run: /home/rocco/venv-crg/bin/code-review-graph build)
### ripwire callers
<callers of="test_duplicate_binding_identity_tuples_fail_closed_through_each_public_cli" defs="1" count="0" root="/home/rocco/agent-factory/.lanes/pc-m4.md--c367d76/tree" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=test_duplicate_binding_identity_tuples_fail_closed_through_each_public_cli">

## symbol test_a_well_formed_scratch_binding_still_authorizes_exactly_its_scopes
### GitNexus impact (upstream)
unmapped — GitNexus index absent
### code-review-graph callers_of / tests_for
unmapped — code-review-graph graph absent (run: /home/rocco/venv-crg/bin/code-review-graph build)
### ripwire callers
<callers of="test_a_well_formed_scratch_binding_still_authorizes_exactly_its_scopes" defs="1" count="0" root="/home/rocco/agent-factory/.lanes/pc-m4.md--c367d76/tree" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=test_a_well_formed_scratch_binding_still_authorizes_exactly_its_scopes">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
