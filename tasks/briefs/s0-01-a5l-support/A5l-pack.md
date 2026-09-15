# lane context pack — d23762a 2026-09-15T07:57Z
files: proofs/S0-01/tools/check_acp_conformance.py tests/test_s0_01_check_acp_conformance.py proofs/S0-01/tools/pins.py
symbols: _parse_scan_v24 _is_pinned_process is_pinned_argv corpus_version _corpus_version test_real_leg_runtime_identity

## proofs/S0-01/tools/check_acp_conformance.py
### graft skeleton
graft skeleton — proofs/S0-01/tools/check_acp_conformance.py

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 0 files ---

## tests/test_s0_01_check_acp_conformance.py
### graft skeleton

graft skeleton — tests/test_s0_01_check_acp_conformance.py
- L77-L81  function _cached_pm  def _cached_pm(k, point)
- L85-L89  function _patch_nostr_verify  def _patch_nostr_verify()
- L92-L93  function _sha256  def _sha256(data: bytes) -> str
- L96-L101  function _sha256_file  def _sha256_file(path: Path) -> str
- L104-L107  function _load_frames  def _load_frames(leg_dir: Path)
- L110-L111  function _load_fingerprint  def _load_fingerprint()
- L114-L139  function _make_interleaved_timeline  def _make_interleaved_timeline(c2a, a2c, leg)
- L142-L159  function _write_timeline  def _write_timeline(leg_dir, entries)
- L162-L173  function _write_runtime_identity  def _write_runtime_identity(leg_dir, leg)
- L176-L188  function _write_env  def _write_env(leg_dir, identities, leg)
- L191-L218  function _write_startup_and_log  def _write_startup_and_log(leg_dir, leg)
- L221-L222  function _write_model  def _write_model(leg_dir, leg)
- L225-L238  function _write_manifests  def _write_manifests(leg_dir, baseline_path)
- L243-L248  function _sign_mention  def _sign_mention(seckey, content, tags_list, created_at=None)
- L251-L273  function _write_mentions  def _write_mentions(leg_dir, leg, identities, entries)
- L276-L314  function _write_upstream_records  def _write_upstream_records(leg_dir, leg, entries, fingerprint)
- L317-L323  function _scan_header  def _scan_header(mode, *, rows=0, table_rows=50, buzz_pid=12300, buzz_present=1, owned=3, owned_present=3, pinned_present=0, owned_zombies=0)
- L326-L348  function _write_process_scan  def _write_process_scan(leg_dir, leg)
- L351-L359  function _write_capture_contract_files  def _write_capture_contract_files(leg_dir, leg)
- L362-L387  function _write_tee_status  def _write_tee_status(leg_dir, entries)
- L390-L422  function _write_negative  def _write_negative(neg_dir, identities)
- L426-L463  function _session_bundle  def _session_bundle(tmp_path_factory)
- L467-L486  function bundle  def bundle(_session_bundle, tmp_path, monkeypatch)
- L489-L498  function _rewrite  def _rewrite(path, data)
- L501-L506  function _run  def _run(root: Path, fixtures_dir: Path = None)
- L509-L521  function _check  def _check(bndl, timeout_s=60)
- L525-L531  function test_real_bundle_cli  def test_real_bundle_cli()
- L534-L540  function test_passing_v2_bundle  def test_passing_v2_bundle(bundle)
- L543-L549  function test_cli_pass_path_fails_on_golden_pin  def test_cli_pass_path_fails_on_golden_pin(bundle, _session_bundle)
- L552-L555  function test_cli_usage_error_exit_64  def test_cli_usage_error_exit_64()
- L559-L564  function test_absent_defers  def test_absent_defers(tmp_path)
- L567-L571  function test_no_timelines_defers  def test_no_timelines_defers(tmp_path)
- L575-L582  function test_m1_manifest_zeroed  def test_m1_manifest_zeroed(bundle)
- L585-L591  function test_m2_tampered_sig  def test_m2_tampered_sig(bundle)
- L594-L604  function test_m2_wrong_pubkey  def test_m2_wrong_pubkey(bundle)
- L607-L616  function test_m3_cancel_foreign  def test_m3_cancel_foreign(bundle)
- L619-L631  function test_m4_shutdown_init_only  def test_m4_shutdown_init_only(bundle)
- L634-L645  function test_m5_1s  def test_m5_1s(bundle)
- L648-L658  function test_m5_7200  def test_m5_7200(bundle)
- L675-L680  function test_deletion  def test_deletion(bundle, fn, leg)
- L683-L687  function test_del_mentions  def test_del_mentions(bundle)
- L690-L694  function test_del_upstream  def test_del_upstream(bundle)
- L697-L701  function test_del_baseline  def test_del_baseline(bundle)
- L704-L708  function test_del_negative  def test_del_negative(bundle)
- L711-L715  function test_del_golden_jsonl  def test_del_golden_jsonl(bundle)
- L718-L722  function test_del_leg  def test_del_leg(bundle)
- L727-L736  function test_del_negative_file  def test_del_negative_file(bundle, fn)
- L739-L745  function test_del_neg_fixture  def test_del_neg_fixture(bundle)
- L748-L753  function test_del_identities  def test_del_identities(bundle)
- L757-L764  function test_seq_float  def test_seq_float(bundle)
- L767-L773  function test_seq_bool  def test_seq_bool(bundle)
- L776-L784  function test_seq_gap  def test_seq_gap(bundle)
- L787-L795  function test_mono_backwards  def test_mono_backwards(bundle)
- L798-L803  function test_nan  def test_nan(bundle)
- L806-L812  function test_mono_string  def test_mono_string(bundle)
- L815-L821  function test_dir_unknown  def test_dir_unknown(bundle)
- L825-L832  function test_frames_c2a_extra_line  def test_frames_c2a_extra_line(bundle)
- L835-L844  function test_frames_a2c_reordered  def test_frames_a2c_reordered(bundle)
- L847-L854  function test_blank_line_in_frames  def test_blank_line_in_frames(bundle)
- L858-L865  function test_rid_missing_tee_pid  def test_rid_missing_tee_pid(bundle)
- L868-L875  function test_rid_buzz_sha_wrong  def test_rid_buzz_sha_wrong(bundle)
- L878-L885  function test_rid_tee_sha_wrong  def test_rid_tee_sha_wrong(bundle)
- L888-L896  function test_rid_argv_wrong  def test_rid_argv_wrong(bundle)
- L899-L906  function test_rid_entrypoint_sha_wrong  def test_rid_entrypoint_sha_wrong(bundle)
- L909-L915  function test_argv_tampered  def test_argv_tampered(bundle)
- L918-L924  function test_interp_tampered  def test_interp_tampered(bundle)
- L928-L929  function _ids  def _ids(bundle)
- L932-L938  function test_env_extra_key  def test_env_extra_key(bundle)
- L941-L948  function test_env_hermes_home_wrong  def test_env_hermes_home_wrong(bundle)
- L951-L958  function test_env_path_wrong  def test_env_path_wrong(bundle)
- L961-L968  function test_env_policy_wrong  def test_env_policy_wrong(bundle)
- L971-L978  function test_env_pdwb_wrong  def test_env_pdwb_wrong(bundle)
- L981-L987  function test_owner_swap  def test_owner_swap(bundle)
- L990-L996  function test_env_leak  def test_env_leak(bundle)
- L999-L1005  function test_hex_leak_env  def test_hex_leak_env(bundle)
- L1008-L1015  function test_hex_leak_uppercase  def test_hex_leak_uppercase(bundle)
- L1018-L1025  function test_hex_leak_with_prefix  def test_hex_leak_with_prefix(bundle)
- L1028-L1035  function test_allowlist_super  def test_allowlist_super(bundle)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 4 hits over 1 files ---
AP-66: 2
    tests/test_s0_01_check_acp_conformance.py:87: nv._point_mul = _cached_pm
    tests/test_s0_01_check_acp_conformance.py:89: nv._point_mul = _orig_pm
AF-AP-48: 1
    tests/test_s0_01_check_acp_conformance.py:5106: assert all(site[3] in {"walk", "require_regular_file", "stdin"}
AF-AP-57: 1
    tests/test_s0_01_check_acp_conformance.py:4687: if call_count[0] == 2:

## proofs/S0-01/tools/pins.py
### graft skeleton
graft skeleton — proofs/S0-01/tools/pins.py

no definitions indexed for this file
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 0 files ---

## graft ask — How does check_acp_conformance.py decide a process is the pinned hermes-acp and which corpus version a leg carries; where do its private _parse_scan_v24 / _is_pinned_process and the test-side _corpus_version fold duplicate pins.is_pinned_argv / pins.corpus_version, and who consumes each?
graft ask — "How does check_acp_conformance.py decide a process is the pinned hermes-acp and which corpus version a leg carries; where do its private _parse_scan_v24 / _is_pinned_process and the test-side _corpus_version fold duplicate pins.is_pinned_argv / pins.corpus_version, and who consumes each?"  (lexical)

1. main · function  [symbol]
   proofs/S0-01/tools/pc/pc_launch.py:L281-L425
   def main()

2. main · function  [symbol]
   proofs/S0-01/tools/build_capture_record.py:L48-L217
   def main() -> int

3. main · function  [symbol]
   proofs/S0-01/tools/pc/pc_negative.py:L19-L50
   def main()

4. acp_probe.py · file  [symbol]
   proofs/S0-01/tools/acp_probe.py

5. main · function  [symbol]
   proofs/S0-01/tools/archive/build_capture_record_v1.py:L43-L101
   def main() -> int

6. frame_tee.py · file  [symbol]
   proofs/S0-01/tools/frame_tee.py

7. _carries_secret · method  [symbol]
   proofs/S0-01/tools/scripted_backend.py:L489-L512
   def _carries_secret(self, s: str, *, byte_view: bool) -> bool

8. nostr_verify.py · file  [symbol]
   proofs/S0-01/tools/nostr_verify.py

## symbol _parse_scan_v24
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 0,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/check_acp_conformance.py::_parse_scan_v24')",
      "name": "check_process_evidence",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/check_acp_conformance.py::_parse_scan_v24')",
### ripwire callers
<callers of="_parse_scan_v24" defs="1" count="1" root="/home/user/agent-factory" hop_tested="1" hop_untested="0" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="9" graph_unresolved="87" counts_floor="1" next="--uses=_parse_scan_v24">

## symbol _is_pinned_process
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 0,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/check_acp_conformance.py::_is_pinned_process')",
      "name": "check_process_evidence",
      "name": "test_v24_entry_point_rule_matches_tokens_not_substrings",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/check_acp_conformance.py::_is_pinned_process')",
### ripwire callers
<callers of="_is_pinned_process" defs="1" count="2" root="/home/user/agent-factory" hop_tested="1" hop_untested="1" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="9" graph_unresolved="87" counts_floor="1" next="--uses=_is_pinned_process">

## symbol is_pinned_argv
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "'is_pinned_argv' matches 4 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "is_pinned_argv",
      "name": "test_is_pinned_argv_does_not_count_a_pinned_binary_reached_by_another_path",
      "name": "test_is_pinned_argv_matches_every_row_of_the_real_corpus_scan",
      "name": "test_is_pinned_argv_matches_the_entry_point_only",
      "name": "is_pinned_argv",
      "name": "test_is_pinned_argv_does_not_count_a_pinned_binary_reached_by_another_path",
      "name": "test_is_pinned_argv_matches_every_row_of_the_real_corpus_scan",
      "name": "test_is_pinned_argv_matches_the_entry_point_only",
  "summary": "'is_pinned_argv' matches 4 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "is_pinned_argv",
      "name": "test_is_pinned_argv_does_not_count_a_pinned_binary_reached_by_another_path",
      "name": "test_is_pinned_argv_matches_every_row_of_the_real_corpus_scan",
      "name": "test_is_pinned_argv_matches_the_entry_point_only",
      "name": "is_pinned_argv",
      "name": "test_is_pinned_argv_does_not_count_a_pinned_binary_reached_by_another_path",
      "name": "test_is_pinned_argv_matches_every_row_of_the_real_corpus_scan",
      "name": "test_is_pinned_argv_matches_the_entry_point_only",
### ripwire callers
<callers of="is_pinned_argv" defs="1" count="4" root="/home/user/agent-factory" hop_tested="0" hop_untested="4" shown="4" capped="0" total="4" has_more="0" next_offset="4" offset="0" limit="20" graph_ambiguous="9" graph_unresolved="87" counts_floor="1" next="--uses=is_pinned_argv">

## symbol corpus_version
### GitNexus impact (upstream)
  "impactedCount": 2,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "'corpus_version' matches 16 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "corpus_version",
      "name": "_corpus_version",
      "name": "test_ck12_corpus_version_rejects_malformed_newer_corpus",
      "name": "test_ck12_corpus_version_rejects_missing_newer_artifact",
      "name": "test_corpus_version_accepts_the_good_v24_header",
      "name": "test_corpus_version_refuses_a_header_in_the_body_after_rows",
      "name": "test_corpus_version_refuses_a_header_with_trailing_fields",
      "name": "test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name",
      "name": "test_corpus_version_refuses_a_second_header_line_in_the_body",
      "name": "test_corpus_version_refuses_an_unknown_header_version",
      "name": "test_corpus_version_refuses_crlf_line_endings",
  "summary": "'corpus_version' matches 16 node(s). Re-run with a qualified_name from disambiguation.",
      "name": "corpus_version",
      "name": "_corpus_version",
      "name": "test_ck12_corpus_version_rejects_malformed_newer_corpus",
      "name": "test_ck12_corpus_version_rejects_missing_newer_artifact",
      "name": "test_corpus_version_accepts_the_good_v24_header",
      "name": "test_corpus_version_refuses_a_header_in_the_body_after_rows",
      "name": "test_corpus_version_refuses_a_header_with_trailing_fields",
      "name": "test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name",
      "name": "test_corpus_version_refuses_a_second_header_line_in_the_body",
      "name": "test_corpus_version_refuses_an_unknown_header_version",
      "name": "test_corpus_version_refuses_crlf_line_endings",
### ripwire callers
<callers of="corpus_version" defs="1" count="13" root="/home/user/agent-factory" hop_tested="0" hop_untested="13" shown="13" capped="0" total="13" has_more="0" next_offset="13" offset="0" limit="20" graph_ambiguous="9" graph_unresolved="87" counts_floor="1" next="--uses=corpus_version">

## symbol _corpus_version
### GitNexus impact (upstream)
  "impactedCount": null,
  "risk": "UNKNOWN",
      "impactedCount": 0,
      "risk": "UNKNOWN",
      "direct": 0,
      "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe."
      "impactedCount": 0,
      "risk": "UNKNOWN",
### code-review-graph callers_of / tests_for
  "summary": "Found 3 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_corpus_version')",
      "name": "test_ck12_corpus_version_rejects_malformed_newer_corpus",
      "name": "test_ck12_corpus_version_rejects_missing_newer_artifact",
      "name": "/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py",
  "summary": "Found 10 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_corpus_version')",
      "name": "test_ck12_corpus_version_rejects_malformed_newer_corpus",
      "name": "test_ck12_corpus_version_rejects_missing_newer_artifact",
      "name": "test_real_leg_process_evidence",
      "name": "test_corpus_version_accepts_the_good_v24_header",
      "name": "test_corpus_version_refuses_a_second_header_line_in_the_body",
      "name": "test_corpus_version_refuses_a_header_in_the_body_after_rows",
      "name": "test_corpus_version_refuses_a_header_with_trailing_fields",
      "name": "test_corpus_version_refuses_crlf_line_endings",
      "name": "test_corpus_version_refuses_an_unknown_header_version",
      "name": "test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name",
### ripwire callers
<callers of="_corpus_version" defs="2" count="5" root="/home/user/agent-factory" hop_tested="0" hop_untested="5" shown="5" capped="0" total="5" has_more="0" next_offset="5" offset="0" limit="20" graph_ambiguous="9" graph_unresolved="87" counts_floor="1" next="--uses=_corpus_version">

## symbol test_real_leg_runtime_identity
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_real_leg_runtime_identity')",
  "summary": "Found 38 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_real_leg_runtime_identity')",
      "name": "test_real_leg_timeline",
      "name": "test_real_leg_initialize_frames",
      "name": "test_real_leg_runtime_identity",
      "name": "test_real_leg_env",
      "name": "test_real_leg_mentions",
      "name": "test_real_leg_route",
      "name": "test_real_leg_config_echo",
      "name": "test_real_leg_manifests",
      "name": "test_real_leg_process_evidence",
      "name": "test_real_leg_buzzacp_log",
      "name": "test_real_leg_prompt_turn",
### ripwire callers
<callers of="test_real_leg_runtime_identity" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="9" graph_unresolved="87" counts_floor="1" next="--uses=test_real_leg_runtime_identity">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
