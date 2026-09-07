# lane context pack — 13c1bd2 2026-09-07T22:56Z
files: proofs/S0-01/tools/scripted_backend.py tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py
symbols: _framing_gate _normal_forms _authorized load_token test_no_not_equal_marker_assertions test_pct_dense_junk_that_now_saturates_is_served

## proofs/S0-01/tools/scripted_backend.py
### graft skeleton

graft skeleton — proofs/S0-01/tools/scripted_backend.py
- L202-L237  function _parse_invis_ranges  def _parse_invis_ranges(s: str) -> frozenset[int]
- L243-L246  class _ParseError  class _ParseError(Exception)
- L245-L246  method __init__  def __init__(self, raw: bytes)
- L249-L271  function _has_invalid_utf8_bytes  def _has_invalid_utf8_bytes(s: str) -> bool
- L274-L336  function _normal_forms  def _normal_forms(s: str) -> tuple[frozenset[str], bool]
- L299-L305  function strip_invis  def strip_invis(x)
- L306-L313  function utf8_redecode_lenient  def utf8_redecode_lenient(x)
- L314-L317  function unquote_drop  def unquote_drop(x)
- L318-L321  function unquote_plus_drop  def unquote_plus_drop(x)
- L339-L363  function _json_nesting_depth  def _json_nesting_depth(raw: bytes) -> int
- L366-L383  function _iter_json_strings  def _iter_json_strings(obj)
- L386-L387  function _fingerprint  def _fingerprint(value: str) -> str
- L390-L396  function load_token  def load_token(path: Path) -> str
- L399-L409  function _validate_slow_delay  def _validate_slow_delay(s)
- L412-L443  function _json_safe  def _json_safe(o)
- L446-L538  class State  class State
- L447-L452  method __init__  def __init__(self, token: str, record_dir: Path, slow_delay: float)
- L454-L477  method _carries_secret  def _carries_secret(self, s: str, *, byte_view: bool) -> bool
- L479-L538  method record  def record(self, method: str, path: str, headers, body, remote_addr: str, bearer_token: str | None, *, raw_body: bytes | None = None) -> tuple[int, bool]
- L541-L752  function make_handler  def make_handler(state: State)
- L542-L750  class Handler  class Handler(BaseHTTPRequestHandler)
- L547-L548  method log_message  def log_message(self, fmt, *args): # quiet; the record dir is the log
- L551-L555  method _reject  def _reject(self, code: int)
- L557-L603  method _framing_gate  def _framing_gate(self) -> bool
- L605-L608  method handle_expect_100  def handle_expect_100(self)
- L611-L619  method _send_json  def _send_json(self, code: int, obj, extra=None)
- L621-L623  method _error  def _error(self, code: int, message: str, err_type: str, err_code: str)
- L625-L627  method _authorized  def _authorized(self) -> bool
- L629-L631  method _bearer_token  def _bearer_token(self)
- L633-L658  method _read_body  def _read_body(self)
- L661-L682  method do_GET  def do_GET(self)
- L684-L723  method do_POST  def do_POST(self)
- L725-L750  method _stream  def _stream(self, model: str)
- L734-L736  function emit  def emit(obj)
- L755-L803  function main  def main(argv=None) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 5 hits over 1 files ---
AF-AP-40: 2
    proofs/S0-01/tools/scripted_backend.py:784: if args.record_dir.exists() and not args.record_dir.is_dir():
    proofs/S0-01/tools/scripted_backend.py:788: if args.record_dir.is_dir() and any(args.record_dir.iterdir()):
AP-32: 2
    proofs/S0-01/tools/scripted_backend.py:387: return hashlib.sha256(value.encode()).hexdigest()[:12]
    proofs/S0-01/tools/scripted_backend.py:531: auth_fp = hashlib.sha256(bearer_token.encode()).hexdigest() if bearer_token else None
AP-51: 1
    proofs/S0-01/tools/scripted_backend.py:96: Determinism: identical request bodies -> byte-identical responses (fixed ids, timestamps, usage).

## tests/test_s0_01_scripted_backend.py
### graft skeleton

graft skeleton — tests/test_s0_01_scripted_backend.py
- L51-L54  function _free_port  def _free_port()
- L58-L81  function backend  def backend(tmp_path_factory)
- L84-L95  function _call  def _call(port, method, path, body=None, token=TOKEN, stream=False, extra_headers=None)
- L98-L114  function _raw_request  def _raw_request(port, raw_bytes)
- L117-L124  function test_bearer_required_exact_401  def test_bearer_required_exact_401(backend)
- L127-L130  function test_models_list  def test_models_list(backend)
- L133-L141  function test_non_stream_completion_is_pong_and_byte_identical  def test_non_stream_completion_is_pong_and_byte_identical(backend)
- L144-L154  function test_stream_completion_frames_are_deterministic  def test_stream_completion_frames_are_deterministic(backend)
- L157-L165  function test_slow_model_streams_in_pieces_with_a_delay  def test_slow_model_streams_in_pieces_with_a_delay(backend)
- L168-L172  function test_unknown_model_and_bad_body_are_exact_errors  def test_unknown_model_and_bad_body_are_exact_errors(backend)
- L175-L200  function test_requests_are_recorded_with_fingerprint_and_token_absent_from_argv  def test_requests_are_recorded_with_fingerprint_and_token_absent_from_argv(backend): # F8/F18: self-contained -- issue own POST before reading records
- L203-L212  function test_received_at_microsecond_format_kills_truncation_mutant  def test_received_at_microsecond_format_kills_truncation_mutant(backend)
- L215-L227  function test_t_mono_ns_strictly_increasing_across_requests  def test_t_mono_ns_strictly_increasing_across_requests(backend)
- L232-L247  function test_nonempty_record_dir_refuses_without_flag  def test_nonempty_record_dir_refuses_without_flag(tmp_path)
- L250-L280  function test_allow_existing_records_flag_overrides  def test_allow_existing_records_flag_overrides(tmp_path)
- L283-L299  function test_healthz_unauthenticated_and_not_recorded  def test_healthz_unauthenticated_and_not_recorded(backend)
- L302-L310  function test_record_null_fingerprint_when_no_bearer  def test_record_null_fingerprint_when_no_bearer(backend)
- L313-L327  function test_record_dir_as_file_refuses_startup  def test_record_dir_as_file_refuses_startup(tmp_path)
- L330-L340  function test_missing_token_file_named_refusal  def test_missing_token_file_named_refusal(tmp_path)
- L343-L356  function test_chunked_post_rejected_with_411  def test_chunked_post_rejected_with_411(backend)
- L359-L369  function test_chunked_get_rejected_with_411  def test_chunked_get_rejected_with_411(backend)
- L372-L384  function test_content_length_negative_rejected  def test_content_length_negative_rejected(backend)
- L387-L398  function test_content_length_oversized_rejected  def test_content_length_oversized_rejected(backend)
- L401-L412  function test_content_length_underscore_rejected  def test_content_length_underscore_rejected(backend)
- L415-L420  function test_credential_in_query_string_returns_400  def test_credential_in_query_string_returns_400(backend)
- L423-L429  function test_credential_in_body_returns_400  def test_credential_in_body_returns_400(backend)
- L432-L438  function test_credential_in_custom_header_returns_400  def test_credential_in_custom_header_returns_400(backend)
- L444-L451  function test_credential_in_credential_header_returns_400  def test_credential_in_credential_header_returns_400(backend, header_name)
- L454-L466  function test_credential_headers_dropped_from_records  def test_credential_headers_dropped_from_records(backend)
- L469-L478  function test_header_keys_lowercase_in_records  def test_header_keys_lowercase_in_records(backend)
- L481-L496  function test_leak_record_does_not_contain_token  def test_leak_record_does_not_contain_token(backend)
- L499-L507  function test_remote_addr_exact_on_get_record  def test_remote_addr_exact_on_get_record(backend)
- L517-L554  function test_token_file_mode_guard  def test_token_file_mode_guard(tmp_path, mode, accept)
- L559-L576  function test_post_arm_leak_record_does_not_contain_token  def test_post_arm_leak_record_does_not_contain_token(backend)
- L579-L589  function test_post_arm_leak_via_header_redacted  def test_post_arm_leak_via_header_redacted(backend)
- L594-L614  function test_body_literal_bad_cl_is_not_sentinel  def test_body_literal_bad_cl_is_not_sentinel(backend)
- L617-L633  function test_chunked_transfer_encoding_411_writes_no_record  def test_chunked_transfer_encoding_411_writes_no_record(backend)
- L638-L684  function test_handler_timeout_bounds_incomplete_body  def test_handler_timeout_bounds_incomplete_body(backend, tmp_path)
- L690-L702  function test_port_outside_valid_range_refuses_exit_2  def test_port_outside_valid_range_refuses_exit_2(tmp_path, port)
- L707-L739  function test_short_body_returns_400_no_record  def test_short_body_returns_400_no_record(backend)
- L744-L765  function test_malformed_json_with_token_in_url_redacted  def test_malformed_json_with_token_in_url_redacted(backend)
- L768-L789  function test_malformed_json_with_token_in_header_redacted  def test_malformed_json_with_token_in_header_redacted(backend)
- L792-L824  function test_malformed_json_with_token_in_body_redacted  def test_malformed_json_with_token_in_body_redacted(backend)
- L827-L854  function test_p1_boundary_credential_check_in_record  def test_p1_boundary_credential_check_in_record(tmp_path)
- L862-L913  function test_build_capture_record_roundtrip_check  def test_build_capture_record_roundtrip_check(tmp_path)
- L918-L928  function test_credential_in_query_no_auth_header_returns_400  def test_credential_in_query_no_auth_header_returns_400(backend)
- L931-L942  function test_credential_in_header_no_auth_returns_400  def test_credential_in_header_no_auth_returns_400(backend)
- L945-L957  function test_credential_in_body_no_auth_returns_400  def test_credential_in_body_no_auth_returns_400(backend)
- L960-L984  function test_credential_in_raw_body_no_auth_returns_400  def test_credential_in_raw_body_no_auth_returns_400(backend)
- L987-L1001  function test_short_bogus_bearer_does_not_collapse_records  def test_short_bogus_bearer_does_not_collapse_records(backend)
- L1006-L1038  function test_get_with_body_rejected_no_smuggling  def test_get_with_body_rejected_no_smuggling(backend)
- L1051-L1064  function test_slow_delay_invalid_refuses_exit_2  def test_slow_delay_invalid_refuses_exit_2(tmp_path, delay_args, printed)
- L1070-L1100  function test_healthz_with_cl_body_rejected_one_response_zero_records  def test_healthz_with_cl_body_rejected_one_response_zero_records(backend, token)
- L1104-L1134  function test_healthz_with_te_body_rejected_one_response_zero_records  def test_healthz_with_te_body_rejected_one_response_zero_records(backend, token)
- L1138-L1168  function test_healthz_query_with_cl_body_rejected_one_response_zero_records  def test_healthz_query_with_cl_body_rejected_one_response_zero_records(backend, token)
- L1174-L1206  function test_chunked_te_post_smuggling_one_response_zero_records  def test_chunked_te_post_smuggling_one_response_zero_records(backend, token)
- L1210-L1240  function test_chunked_te_get_smuggling_one_response_zero_records  def test_chunked_te_get_smuggling_one_response_zero_records(backend, token)
- L1244-L1277  function test_get_cl_over_max_smuggling_one_response_zero_records  def test_get_cl_over_max_smuggling_one_response_zero_records(backend, token)
- L1282-L1303  function test_credential_in_header_name_returns_400  def test_credential_in_header_name_returns_400(backend)
- L1309-L1332  function test_duplicate_content_length_rejected_400  def test_duplicate_content_length_rejected_400(backend, token)
- L1337-L1353  function test_get_content_length_zero_accepted_and_recorded  def test_get_content_length_zero_accepted_and_recorded(backend)
- L1358-L1370  function test_credential_percent_encoded_in_query_returns_400  def test_credential_percent_encoded_in_query_returns_400(backend)
- L1375-L1388  function test_get_with_cl_1_rejected_400  def test_get_with_cl_1_rejected_400(backend)
- L1397-L1408  function _forged_tail  def _forged_tail(port)
- L1411-L1559  function _build_domain_table  def _build_domain_table()
- L1571-L1641  function test_framing_domain_table  def test_framing_domain_table(backend, case_id, method, path, header_lines, body_bytes, token_val, expected_status, expect_close, expected_records)
- L1646-L1652  function test_bearer_superstring_rejected_401  def test_bearer_superstring_rejected_401(backend)
- L1655-L1665  function test_bearer_extra_space_rejected_401  def test_bearer_extra_space_rejected_401(backend)
- L1670-L1679  function test_healthz_exact_path_no_prefix_match  def test_healthz_exact_path_no_prefix_match(backend)
- L1684-L1704  function test_credential_percent_encoded_in_header_value  def test_credential_percent_encoded_in_header_value(backend)
- L1709-L1725  function test_credential_percent_encoded_in_header_name  def test_credential_percent_encoded_in_header_name(backend)
- L1730-L1750  function test_credential_percent_encoded_in_json_body  def test_credential_percent_encoded_in_json_body(backend)
- L1755-L1778  function test_credential_obs_folded_in_header_value  def test_credential_obs_folded_in_header_value(backend)
- L1783-L1805  function test_credential_triple_percent_encoded_in_header_value  def test_credential_triple_percent_encoded_in_header_value(backend)
- L1810-L1822  function test_slow_delay_argumenttypeerror_arm  def test_slow_delay_argumenttypeerror_arm(tmp_path)
- L1827-L1845  function test_negative_control_defects_gate_arm  def test_negative_control_defects_gate_arm(backend)
- L1848-L1863  function test_negative_control_te_gate_arm  def test_negative_control_te_gate_arm(backend)
- L1866-L1884  function test_negative_control_dup_cl_gate_arm  def test_negative_control_dup_cl_gate_arm(backend)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---

## tests/red/test_s0_01_backend_credential_screen.py
### graft skeleton

graft skeleton — tests/red/test_s0_01_backend_credential_screen.py
- L27-L30  function _free_port  def _free_port()
- L34-L57  function backend  def backend(tmp_path_factory)
- L60-L73  function _raw  def _raw(port, raw_bytes, timeout=5.0)
- L76-L77  function _records  def _records(backend)
- L80-L81  function _last_record_text  def _last_record_text(backend)
- L87-L90  function _post  def _post(port, body: bytes, extra_headers: str = "", tail: bytes = b"")
- L155-L164  function _parse_oracle_ranges  def _parse_oracle_ranges(s)
- L170-L222  function _absent_under_all_normalizations  def _absent_under_all_normalizations(text: str) -> bool
- L188-L192  function strip_invis  def strip_invis(x)
- L193-L197  function utf8_redecode_lenient  def utf8_redecode_lenient(x)
- L198-L199  function unquote_drop  def unquote_drop(x)
- L200-L201  function unquote_plus_drop  def unquote_plus_drop(x)
- L227-L237  function test_credential_whitespace_split_in_valid_json_body_returns_400  def test_credential_whitespace_split_in_valid_json_body_returns_400(backend, sep)
- L246-L257  function test_expect_header_any_value_rejected_417  def test_expect_header_any_value_rejected_417(backend, method, value)
- L262-L270  function test_authorization_prefixed_header_name_is_not_exempt  def test_authorization_prefixed_header_name_is_not_exempt(backend, name)
- L274-L285  function test_credential_percent_encoded_and_whitespace_split_in_header_value  def test_credential_percent_encoded_and_whitespace_split_in_header_value(backend)
- L289-L297  function test_post_content_length_exactly_max_is_accepted  def test_post_content_length_exactly_max_is_accepted(backend)
- L307-L316  function test_obs_folded_header_rejected_400  def test_obs_folded_header_rejected_400(backend, folded, fold_char)
- L320-L330  function test_credential_double_percent_encoded_in_header_value_returns_400  def test_credential_double_percent_encoded_in_header_value_returns_400(backend)
- L336-L360  function test_credential_encoded_whitespace_split_returns_400  def test_credential_encoded_whitespace_split_returns_400(backend, sep, sink)
- L365-L377  function test_credential_whitespace_split_as_json_key_returns_400  def test_credential_whitespace_split_as_json_key_returns_400(backend, sep)
- L381-L394  function test_credential_quad_percent_encoded_at_depth4  def test_credential_quad_percent_encoded_at_depth4(backend)
- L398-L411  function test_duplicate_json_key_hiding_token_returns_400  def test_duplicate_json_key_hiding_token_returns_400(backend)
- L421-L424  function _nested_note_body  def _nested_note_body(depth: int) -> bytes
- L427-L436  function test_json_depth_over_limit_returns_400_no_record  def test_json_depth_over_limit_returns_400_no_record(backend)
- L439-L445  function test_json_depth_at_limit_is_served  def test_json_depth_at_limit_is_served(backend)
- L448-L458  function test_depth_1000_json_body_returns_400_no_record  def test_depth_1000_json_body_returns_400_no_record(backend)
- L462-L480  function test_non_finite_float_body_coerced_and_recorded  def test_non_finite_float_body_coerced_and_recorded(backend)
- L476-L477  function _raise  def _raise(x)
- L485-L552  class TestOracleSelfTests  class TestOracleSelfTests
- L551-L552  method test_oracle_known_vectors  def test_oracle_known_vectors(self, text, expected)
- L559-L584  function test_credential_split_with_trailing_nested_escape_returns_400  def test_credential_split_with_trailing_nested_escape_returns_400(backend, sep, sink)
- L598-L635  function test_credential_depth5_percent_nesting_returns_400  def test_credential_depth5_percent_nesting_returns_400(backend, vector, sink)
- L641-L653  function test_credential_whitespace_split_in_json_list_element_returns_400  def test_credential_whitespace_split_in_json_list_element_returns_400(backend, sep)
- L658-L666  function test_json_depth_ignores_brackets_inside_strings  def test_json_depth_ignores_brackets_inside_strings(backend)
- L669-L676  function test_json_depth_handles_escaped_quote  def test_json_depth_handles_escaped_quote(backend)
- L681-L690  function test_credential_uppercased_token_in_header_returns_400  def test_credential_uppercased_token_in_header_returns_400(backend)
- L700-L711  function test_credential_zero_width_pct_encoded_returns_400  def test_credential_zero_width_pct_encoded_returns_400(backend, vector, name)
- L714-L726  function test_credential_zero_width_json_escape_returns_400  def test_credential_zero_width_json_escape_returns_400(backend)
- L731-L744  function test_credential_plus_split_with_pct2520_suffix_returns_400  def test_credential_plus_split_with_pct2520_suffix_returns_400(backend)
- L752-L769  function test_credential_raw_utf8_zero_width_in_header_returns_400  def test_credential_raw_utf8_zero_width_in_header_returns_400(backend, sep)
- L774-L790  function test_record_text_carries_no_token_under_any_normalization  def test_record_text_carries_no_token_under_any_normalization(backend)
- L801-L817  function test_credential_invalid_utf8_separator_in_header_returns_400  def test_credential_invalid_utf8_separator_in_header_returns_400(backend, sep)
- L830-L842  function test_credential_invalid_utf8_separator_in_json_body_returns_400  def test_credential_invalid_utf8_separator_in_json_body_returns_400(backend, json_sep, sep_id)
- L848-L859  function test_credential_control_char_in_header_value_returns_400  def test_credential_control_char_in_header_value_returns_400(backend, ctl_char)
- L868-L880  function test_credential_control_char_in_json_body_returns_400  def test_credential_control_char_in_json_body_returns_400(backend, json_sep, sep_id)
- L885-L895  function test_unquote_op_is_required_for_the_bound  def test_unquote_op_is_required_for_the_bound(backend)
- L900-L917  function test_raw_non_ascii_header_name_rejected_by_gate_no_record  def test_raw_non_ascii_header_name_rejected_by_gate_no_record(backend)
- L927-L939  function test_ordinary_latin1_text_in_json_body_is_served  def test_ordinary_latin1_text_in_json_body_is_served(backend, content)
- L946-L963  function test_credential_invisible_separator_in_header_returns_400  def test_credential_invisible_separator_in_header_returns_400(backend, cp)
- L981-L994  function test_credential_invisible_separator_in_json_body_returns_400  def test_credential_invisible_separator_in_json_body_returns_400(backend, cp, cp_id)
- L999-L1015  function test_credential_function_application_separator_in_header_returns_400  def test_credential_function_application_separator_in_header_returns_400(backend)
- L1021-L1038  function test_credential_c1_control_wire_form_returns_400  def test_credential_c1_control_wire_form_returns_400(backend, cp)
- L1043-L1058  function test_invalid_utf8_without_the_token_is_refused_not_repaired  def test_invalid_utf8_without_the_token_is_refused_not_repaired(backend)
- L1063-L1086  function test_precheck_before_closure_on_invalid_utf8  def test_precheck_before_closure_on_invalid_utf8(backend)
- L1074-L1076  function counting_nf  def counting_nf(s)
- L1094-L1104  function test_top_level_json_string_body_is_not_a_byte_view  def test_top_level_json_string_body_is_not_a_byte_view(backend, doc)
- L1107-L1116  function test_top_level_json_string_hello_control  def test_top_level_json_string_hello_control(backend)
- L1123-L1136  function test_credential_pct_encoded_invalid_utf8_separator_returns_400  def test_credential_pct_encoded_invalid_utf8_separator_returns_400(backend, sep)
- L1141-L1153  function test_credential_lone_surrogate_separator_in_json_body_returns_400  def test_credential_lone_surrogate_separator_in_json_body_returns_400(backend)
- L1161-L1175  function test_credential_reserved_bmp_separator_in_json_body_returns_400  def test_credential_reserved_bmp_separator_in_json_body_returns_400(backend, cp, cp_id)
- L1180-L1195  function test_no_not_equal_marker_assertions  def test_no_not_equal_marker_assertions()
- L1200-L1212  function test_pct_dense_junk_that_now_saturates_is_served  def test_pct_dense_junk_that_now_saturates_is_served(backend)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 3 hits over 1 files ---
AF-AP-60: 1
    tests/red/test_s0_01_backend_credential_screen.py:1190: ["grep", "-cP",
AF-AP-61: 1
    tests/red/test_s0_01_backend_credential_screen.py:1191: r'^\s*assert\s.*\["body"\]\s*!=\s*MARKER',
AP-66: 1
    tests/red/test_s0_01_backend_credential_screen.py:1077: 

## graft ask — how does the credential screen decide served vs blanked, and which tests pin the recorded request body and header values
graft ask — "how does the credential screen decide served vs blanked, and which tests pin the recorded request body and header values"  (lexical)

1. do_POST · method  [symbol]
   proofs/S0-01/tools/scripted_backend.py:L684-L723
   def do_POST(self)

2. build_capture_record_v1.py · file  [symbol]
   proofs/S0-01/tools/archive/build_capture_record_v1.py

3. main · function  [symbol]
   proofs/S0-01/tools/acp_probe.py:L134-L459
   def main(): # Validate required env vars early with a named message (L15/A10: exit 64). # Empty/unset cases exit 64 WITHOUT probe_error because the try block (which # writes runtime-identity.json) has not started yet — this is a documented # exception: probe_error requires the wrapped body to have opened.

4. pc_launch.py · file  [symbol]
   proofs/S0-01/tools/pc/pc_launch.py

5. _write_status · function  [symbol]
   proofs/S0-01/tools/frame_tee.py:L169-L207
   def _write_status(final=False, exit_code_val=None, agent_rc=None)

6. _parse_manifest_gz · function  [symbol]
   proofs/S0-01/tools/build_capture_record.py:L32-L42
   def _parse_manifest_gz(gz_path: Path) -> dict

7. scripted_backend.py · file  [symbol]
   proofs/S0-01/tools/scripted_backend.py

8. main · function  [symbol]
   proofs/S0-01/tools/archive/build_capture_record_v1.py:L43-L101
   def main() -> int

## symbol _framing_gate
### GitNexus impact (upstream)
  "impactedCount": 2,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 2,
    "processes_affected": 2,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/proofs/S0-01/tools/scripted_backend.py::_framing_gate'.",
  "summary": "No node found matching '/home/user/agent-factory/proofs/S0-01/tools/scripted_backend.py::_framing_gate'.",
### ripwire callers
<callers of="_framing_gate" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=_framing_gate">

## symbol _normal_forms
### GitNexus impact (upstream)
  "impactedCount": 4,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 2,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/scripted_backend.py::_normal_forms')",
      "name": "_carries_secret",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/scripted_backend.py::_normal_forms')",
### ripwire callers
<callers of="_normal_forms" defs="1" count="1" root="/home/user/agent-factory" hop_tested="1" hop_untested="0" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=_normal_forms">

## symbol _authorized
### GitNexus impact (upstream)
  "impactedCount": 2,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 2,
    "processes_affected": 2,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/proofs/S0-01/tools/scripted_backend.py::_authorized'.",
  "summary": "No node found matching '/home/user/agent-factory/proofs/S0-01/tools/scripted_backend.py::_authorized'.",
### ripwire callers
<callers of="_authorized" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=_authorized">

## symbol load_token
### GitNexus impact (upstream)
  "impactedCount": 2,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 0,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/scripted_backend.py::load_token')",
      "name": "main",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/scripted_backend.py::load_token')",
### ripwire callers
<callers of="load_token" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=load_token">

## symbol test_no_not_equal_marker_assertions
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/red/test_s0_01_backend_credential_screen.py::test_no_not_equal_marker_assertions')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/red/test_s0_01_backend_credential_screen.py::test_no_not_equal_marker_assertions')",
### ripwire callers
<callers of="test_no_not_equal_marker_assertions" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_no_not_equal_marker_assertions">

## symbol test_pct_dense_junk_that_now_saturates_is_served
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/red/test_s0_01_backend_credential_screen.py::test_pct_dense_junk_that_now_saturates_is_served')",
  "summary": "Found 45 result(s) for tests_for('/home/user/agent-factory/tests/red/test_s0_01_backend_credential_screen.py::test_pct_dense_junk_that_now_saturates_is_served')",
      "name": "test_credential_whitespace_split_in_valid_json_body_returns_400",
      "name": "test_expect_header_any_value_rejected_417",
      "name": "test_authorization_prefixed_header_name_is_not_exempt",
      "name": "test_credential_percent_encoded_and_whitespace_split_in_header_value",
      "name": "test_post_content_length_exactly_max_is_accepted",
      "name": "test_obs_folded_header_rejected_400",
      "name": "test_credential_double_percent_encoded_in_header_value_returns_400",
      "name": "test_credential_encoded_whitespace_split_returns_400",
      "name": "test_credential_whitespace_split_as_json_key_returns_400",
      "name": "test_credential_quad_percent_encoded_at_depth4",
      "name": "test_duplicate_json_key_hiding_token_returns_400",
### ripwire callers
<callers of="test_pct_dense_junk_that_now_saturates_is_served" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_pct_dense_junk_that_now_saturates_is_served">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
