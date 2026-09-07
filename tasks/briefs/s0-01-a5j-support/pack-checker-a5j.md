# lane context pack — 40e8471 2026-09-07T23:15Z
files: proofs/S0-01/check_acp_conformance.py proofs/S0-01/negative_contract.py tests/test_s0_01_check_acp_conformance.py
symbols: _real_leg test_ck11_real_leg_dir_is_resolved_from_the_environment test_ck11_venue_is_resolved_from_the_environment _is_known_stale test_ck11_known_stale_is_the_whole_reason_not_a_tail test_ck11_fifo_at_tools_acp_probe_is_named test_ck11_dir_at_tools_acp_probe_is_named test_ck11_absent_acp_schema_is_a_failure test_ck11_no_presence_gated_check_in_the_proof test_ck11_every_read_is_under_the_walk_or_require_file owner test_ck10_rejected_cap_installs_no_handler test_ck11_alarm_inside_try_cannot_leak_the_handler test_ck11_dead_branch_comments_cite_a_real_guard

## proofs/S0-01/check_acp_conformance.py
### graft skeleton

graft skeleton — proofs/S0-01/check_acp_conformance.py
- L33-L34  function _fixtures  def _fixtures() -> Path
- L158-L159  class Deferred  class Deferred(Exception)
- L162-L163  class Failure  class Failure(Exception)
- L166-L171  function _sha256_file  def _sha256_file(path: Path) -> str
- L174-L175  function _sha256_bytes  def _sha256_bytes(data: bytes) -> str
- L178-L179  function _parse_utc  def _parse_utc(s: str) -> datetime
- L182-L183  function _parse_utc_summary  def _parse_utc_summary(s: str) -> datetime
- L186-L189  function _reject_nan  def _reject_nan(line: str, leg: str, seq_hint: int)
- L187-L188  function _raise  def _raise(c)
- L192-L200  function _require_file  def _require_file(path: Path, leg: str, name: str)
- L203-L206  function _require_dir  def _require_dir(path: Path, leg: str, name: str)
- L209-L211  function _is_strict_int  def _is_strict_int(v)
- L250-L259  function _run_check  def _run_check(fn, leg, *args, **kwargs)
- L262-L364  function check_timeline  def check_timeline(entries, leg, leg_dir)
- L299-L326  function _load_dir  def _load_dir(fpath, name, expected_split)
- L367-L388  function check_initialize_frames  def check_initialize_frames(c2a, a2c, leg, schema=None)
- L391-L433  function check_runtime_identity  def check_runtime_identity(leg_dir, leg)
- L404-L406  function _chk  def _chk(field, expected, desc=None)
- L436-L506  function check_env  def check_env(leg_dir, leg, identities)
- L509-L589  function check_mentions  def check_mentions(leg_dir, leg, identities, entries, post_summary_ts=None)
- L592-L692  function check_route  def check_route(leg_dir, leg, entries)
- L695-L708  function _prompt_windows  def _prompt_windows(entries, leg)
- L711-L767  function check_prompt_turn  def check_prompt_turn(c2a, a2c, leg, entries, expect_stop="end_turn")
- L770-L777  function _shape  def _shape(value)
- L780-L847  function normalize_timeline  def normalize_timeline(entries)
- L784-L786  function id_ph  def id_ph(v)
- L788-L789  function sid_ph  def sid_ph(v)
- L850-L873  function check_cancel  def check_cancel(entries, c2a, a2c, leg_dir, leg="cancel")
- L876-L881  function check_shutdown  def check_shutdown(entries, c2a, a2c, leg_dir, leg="shutdown")
- L884-L959  function check_two_users  def check_two_users(c2a, a2c, entries, identities, leg="two-users", *, leg_dir)
- L962-L994  function check_manifests  def check_manifests(leg_dir, leg, baseline_path, baseline_gz_sha)
- L997-L1033  function _parse_manifest_body  def _parse_manifest_body(body: bytes, leg: str) -> dict
- L1036-L1047  function _parse_summary  def _parse_summary(summary_path, leg, name)
- L1050-L1150  function check_config_echo  def check_config_echo(leg_dir, leg)
- L1153-L1175  function _parse_scan_v23  def _parse_scan_v23(path, leg, name)
- L1178-L1359  function check_process_evidence  def check_process_evidence(leg_dir, leg)
- L1362-L1381  function check_buzzacp_log  def check_buzzacp_log(leg_dir, leg)
- L1384-L1482  function check_tee_status  def check_tee_status(leg_dir, leg, entries)
- L1485-L1505  function check_negative  def check_negative(neg_dir, leg="negative")
- L1508-L1609  function check_golden  def check_golden(golden_dir, leg="golden")
- L1588-L1594  function _raw_sid  def _raw_sid(ents)
- L1612-L1619  function _load_timeline_raw  def _load_timeline_raw(leg_dir, leg)
- L1622-L1639  function _check_with_timeout  def _check_with_timeout(timeout_s, fn, *args)
- L1625-L1627  function _raise_timeout  def _raise_timeout(signum, frame)
- L1642-L1653  function check_bundle  def check_bundle(root: Path, timeout_s: int = 90) -> str: # R8-CK-F2: the wall-clock cap lives HERE so in-process consumers get it too. # Default 90 s < the runner's 120 s. # R9-CK-F1: reject non-positive, non-int, and out-of-range caps. # alarm(0) cancels the alarm silently; bool/float/NaN/inf/str are not ints; # values >= 2**31 overflow signal.alarm's C int (AF-AP-58 sibling).
- L1656-L1806  function _check_bundle_uncapped  def _check_bundle_uncapped(root: Path) -> str
- L1809-L1853  function main  def main(argv) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 7 hits over 1 files ---
AF-AP-40: 5
    proofs/S0-01/check_acp_conformance.py:1488: if neg_dir.is_dir():
    proofs/S0-01/check_acp_conformance.py:1501: if stderr_path.exists():
    proofs/S0-01/check_acp_conformance.py:1698: if item.is_dir() and item.name not in expected_dirs:
    proofs/S0-01/check_acp_conformance.py:1700: if item.is_file() and item.name not in expected_files:
    proofs/S0-01/check_acp_conformance.py:1713: if post_sum_path.exists():
AP-32: 2
    proofs/S0-01/check_acp_conformance.py:167: h = hashlib.sha256()
    proofs/S0-01/check_acp_conformance.py:175: return hashlib.sha256(data).hexdigest()

## proofs/S0-01/negative_contract.py
### graft skeleton

graft skeleton — proofs/S0-01/negative_contract.py
- L30-L31  class NegativeFailure  class NegativeFailure(Exception)
- L34-L35  class NegativeDeferred  class NegativeDeferred(Exception)
- L38-L43  function _sha256_file  def _sha256_file(path: Path) -> str
- L46-L47  function _raise_constant  def _raise_constant(name)
- L50-L54  function _parse_float_strict  def _parse_float_strict(s)
- L57-L69  function _load_timeline  def _load_timeline(path: Path)
- L72-L73  function _is_int  def _is_int(v) -> bool
- L76-L79  function _parse_utc  def _parse_utc(s: str) -> datetime.datetime
- L82-L217  function validate_negative_dir  def validate_negative_dir(neg_dir: Path, fixtures_dir: Path | None = None) -> str
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-32: 1
    proofs/S0-01/negative_contract.py:39: h = hashlib.sha256()

## tests/test_s0_01_check_acp_conformance.py
### graft skeleton

graft skeleton — tests/test_s0_01_check_acp_conformance.py
- L75-L79  function _cached_pm  def _cached_pm(k, point)
- L83-L87  function _patch_nostr_verify  def _patch_nostr_verify()
- L90-L91  function _sha256  def _sha256(data: bytes) -> str
- L94-L99  function _sha256_file  def _sha256_file(path: Path) -> str
- L102-L105  function _load_frames  def _load_frames(leg_dir: Path)
- L108-L109  function _load_fingerprint  def _load_fingerprint()
- L112-L137  function _make_interleaved_timeline  def _make_interleaved_timeline(c2a, a2c, leg)
- L140-L157  function _write_timeline  def _write_timeline(leg_dir, entries)
- L160-L171  function _write_runtime_identity  def _write_runtime_identity(leg_dir, leg)
- L174-L186  function _write_env  def _write_env(leg_dir, identities, leg)
- L189-L218  function _write_startup_and_log  def _write_startup_and_log(leg_dir, leg)
- L221-L222  function _write_model  def _write_model(leg_dir, leg)
- L225-L238  function _write_manifests  def _write_manifests(leg_dir, baseline_path)
- L243-L248  function _sign_mention  def _sign_mention(seckey, content, tags_list, created_at=None)
- L251-L273  function _write_mentions  def _write_mentions(leg_dir, leg, identities, entries)
- L276-L314  function _write_upstream_records  def _write_upstream_records(leg_dir, leg, entries, fingerprint)
- L317-L324  function _scan_header  def _scan_header(mode, *, rows=50, buzz_pid=12300, buzz_present=1, owned=3, owned_present=3, pinned_present=0, owned_zombies=0)
- L327-L351  function _write_process_scan  def _write_process_scan(leg_dir, leg)
- L354-L379  function _write_tee_status  def _write_tee_status(leg_dir, entries)
- L382-L414  function _write_negative  def _write_negative(neg_dir, identities)
- L418-L454  function _session_bundle  def _session_bundle(tmp_path_factory)
- L458-L477  function bundle  def bundle(_session_bundle, tmp_path, monkeypatch)
- L480-L489  function _rewrite  def _rewrite(path, data)
- L492-L497  function _run  def _run(root: Path, fixtures_dir: Path = None)
- L500-L512  function _check  def _check(bndl, timeout_s=60)
- L516-L522  function test_real_bundle_cli  def test_real_bundle_cli()
- L525-L531  function test_passing_v2_bundle  def test_passing_v2_bundle(bundle)
- L534-L540  function test_cli_pass_path_fails_on_golden_pin  def test_cli_pass_path_fails_on_golden_pin(bundle, _session_bundle)
- L543-L546  function test_cli_usage_error_exit_64  def test_cli_usage_error_exit_64()
- L550-L555  function test_absent_defers  def test_absent_defers(tmp_path)
- L558-L562  function test_no_timelines_defers  def test_no_timelines_defers(tmp_path)
- L566-L573  function test_m1_manifest_zeroed  def test_m1_manifest_zeroed(bundle)
- L576-L582  function test_m2_tampered_sig  def test_m2_tampered_sig(bundle)
- L585-L595  function test_m2_wrong_pubkey  def test_m2_wrong_pubkey(bundle)
- L598-L607  function test_m3_cancel_foreign  def test_m3_cancel_foreign(bundle)
- L610-L622  function test_m4_shutdown_init_only  def test_m4_shutdown_init_only(bundle)
- L625-L636  function test_m5_1s  def test_m5_1s(bundle)
- L639-L649  function test_m5_7200  def test_m5_7200(bundle)
- L666-L672  function test_deletion  def test_deletion(bundle, fn, leg)
- L675-L679  function test_del_mentions  def test_del_mentions(bundle)
- L682-L686  function test_del_upstream  def test_del_upstream(bundle)
- L689-L693  function test_del_baseline  def test_del_baseline(bundle)
- L696-L700  function test_del_negative  def test_del_negative(bundle)
- L703-L707  function test_del_golden_jsonl  def test_del_golden_jsonl(bundle)
- L710-L714  function test_del_leg  def test_del_leg(bundle)
- L719-L729  function test_del_negative_file  def test_del_negative_file(bundle, fn)
- L732-L739  function test_del_neg_fixture  def test_del_neg_fixture(bundle)
- L742-L748  function test_del_identities  def test_del_identities(bundle)
- L752-L759  function test_seq_float  def test_seq_float(bundle)
- L762-L768  function test_seq_bool  def test_seq_bool(bundle)
- L771-L779  function test_seq_gap  def test_seq_gap(bundle)
- L782-L790  function test_mono_backwards  def test_mono_backwards(bundle)
- L793-L798  function test_nan  def test_nan(bundle)
- L801-L807  function test_mono_string  def test_mono_string(bundle)
- L810-L816  function test_dir_unknown  def test_dir_unknown(bundle)
- L820-L827  function test_frames_c2a_extra_line  def test_frames_c2a_extra_line(bundle)
- L830-L839  function test_frames_a2c_reordered  def test_frames_a2c_reordered(bundle)
- L842-L849  function test_blank_line_in_frames  def test_blank_line_in_frames(bundle)
- L853-L860  function test_rid_missing_tee_pid  def test_rid_missing_tee_pid(bundle)
- L863-L870  function test_rid_buzz_sha_wrong  def test_rid_buzz_sha_wrong(bundle)
- L873-L880  function test_rid_tee_sha_wrong  def test_rid_tee_sha_wrong(bundle)
- L883-L891  function test_rid_argv_wrong  def test_rid_argv_wrong(bundle)
- L894-L901  function test_rid_entrypoint_sha_wrong  def test_rid_entrypoint_sha_wrong(bundle)
- L904-L910  function test_argv_tampered  def test_argv_tampered(bundle)
- L913-L919  function test_interp_tampered  def test_interp_tampered(bundle)
- L923-L924  function _ids  def _ids(bundle)
- L927-L933  function test_env_extra_key  def test_env_extra_key(bundle)
- L936-L943  function test_env_hermes_home_wrong  def test_env_hermes_home_wrong(bundle)
- L946-L953  function test_env_path_wrong  def test_env_path_wrong(bundle)
- L956-L963  function test_env_policy_wrong  def test_env_policy_wrong(bundle)
- L966-L973  function test_env_pdwb_wrong  def test_env_pdwb_wrong(bundle)
- L976-L982  function test_owner_swap  def test_owner_swap(bundle)
- L985-L991  function test_env_leak  def test_env_leak(bundle)
- L994-L1000  function test_hex_leak_env  def test_hex_leak_env(bundle)
- L1003-L1010  function test_hex_leak_uppercase  def test_hex_leak_uppercase(bundle)
- L1013-L1020  function test_hex_leak_with_prefix  def test_hex_leak_with_prefix(bundle)
- L1023-L1030  function test_allowlist_super  def test_allowlist_super(bundle)
- L1033-L1040  function test_redacted_len_true  def test_redacted_len_true(bundle)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 2 hits over 1 files ---
AP-66: 2
    tests/test_s0_01_check_acp_conformance.py:85: nv._point_mul = _cached_pm
    tests/test_s0_01_check_acp_conformance.py:87: nv._point_mul = _orig_pm

## graft ask — which checker reads are guarded by _require_file or the walk, and which tests pin the venue and corpus declaration
graft ask — "which checker reads are guarded by _require_file or the walk, and which tests pin the venue and corpus declaration"  (lexical)

1. _require_file · function  [symbol]
   proofs/S0-01/check_acp_conformance.py:L192-L200
   def _require_file(path: Path, leg: str, name: str)

2. pins.py · file  [symbol]
   proofs/S0-01/pins.py

3. build_capture_record.py · file  [symbol]
   proofs/S0-01/tools/build_capture_record.py

4. _sha256_file · function  [symbol]
   proofs/S0-01/tools/acp_probe.py:L41-L46
   def _sha256_file(path)

5. _sha256_file · function  [symbol]
   proofs/S0-01/tools/frame_tee.py:L65-L70
   def _sha256_file(path)

6. sha256_file · function  [symbol]
   proofs/S0-01/tools/pc/pc_launch.py:L44-L49
   def sha256_file(path)

7. _sha256_file · function  [symbol]
   proofs/S0-01/negative_contract.py:L38-L43
   def _sha256_file(path: Path) -> str

8. _check_response_directory · function  [symbol]
   proofs/S0-01/check_initialize.py:L118-L173
   def _check_response_directory(dirpath: Path, fixtures_dir: Path = None) -> int

## symbol _real_leg
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 16 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_real_leg')",
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
  "summary": "Found 17 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_real_leg')",
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
<callers of="_real_leg" defs="1" count="16" root="/home/user/agent-factory" hop_tested="0" hop_untested="16" shown="16" capped="0" total="16" has_more="0" next_offset="16" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=_real_leg">

## symbol test_ck11_real_leg_dir_is_resolved_from_the_environment
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_real_leg_dir_is_resolved_from_the_environment')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_real_leg_dir_is_resolved_from_the_environment')",
### ripwire callers
<callers of="test_ck11_real_leg_dir_is_resolved_from_the_environment" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_ck11_real_leg_dir_is_resolved_from_the_environment">

## symbol test_ck11_venue_is_resolved_from_the_environment
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_venue_is_resolved_from_the_environment')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_venue_is_resolved_from_the_environment')",
### ripwire callers
<callers of="test_ck11_venue_is_resolved_from_the_environment" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_ck11_venue_is_resolved_from_the_environment">

## symbol _is_known_stale
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_is_known_stale')",
      "name": "test_real_leg_negative",
      "name": "test_ck11_known_stale_is_the_whole_reason_not_a_tail",
  "summary": "Found 2 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_is_known_stale')",
      "name": "test_real_leg_negative",
      "name": "test_ck11_known_stale_is_the_whole_reason_not_a_tail",
### ripwire callers
<callers of="_is_known_stale" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=_is_known_stale">

## symbol test_ck11_known_stale_is_the_whole_reason_not_a_tail
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_known_stale_is_the_whole_reason_not_a_tail')",
  "summary": "Found 2 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_known_stale_is_the_whole_reason_not_a_tail')",
      "name": "test_real_leg_negative",
      "name": "test_ck11_known_stale_is_the_whole_reason_not_a_tail",
### ripwire callers
<callers of="test_ck11_known_stale_is_the_whole_reason_not_a_tail" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_ck11_known_stale_is_the_whole_reason_not_a_tail">

## symbol test_ck11_fifo_at_tools_acp_probe_is_named
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_fifo_at_tools_acp_probe_is_named')",
  "summary": "Found 205 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_fifo_at_tools_acp_probe_is_named') \u2014 showing 100, 105 omitted",
      "name": "test_m1_manifest_zeroed",
      "name": "test_m2_tampered_sig",
      "name": "test_m2_wrong_pubkey",
      "name": "test_m3_cancel_foreign",
      "name": "test_m4_shutdown_init_only",
      "name": "test_m5_1s",
      "name": "test_m5_7200",
      "name": "test_deletion",
      "name": "test_del_mentions",
      "name": "test_del_upstream",
      "name": "test_del_baseline",
### ripwire callers
<callers of="test_ck11_fifo_at_tools_acp_probe_is_named" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_ck11_fifo_at_tools_acp_probe_is_named">

## symbol test_ck11_dir_at_tools_acp_probe_is_named
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_dir_at_tools_acp_probe_is_named')",
  "summary": "Found 205 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_dir_at_tools_acp_probe_is_named') \u2014 showing 100, 105 omitted",
      "name": "test_m1_manifest_zeroed",
      "name": "test_m2_tampered_sig",
      "name": "test_m2_wrong_pubkey",
      "name": "test_m3_cancel_foreign",
      "name": "test_m4_shutdown_init_only",
      "name": "test_m5_1s",
      "name": "test_m5_7200",
      "name": "test_deletion",
      "name": "test_del_mentions",
      "name": "test_del_upstream",
      "name": "test_del_baseline",
### ripwire callers
<callers of="test_ck11_dir_at_tools_acp_probe_is_named" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_ck11_dir_at_tools_acp_probe_is_named">

## symbol test_ck11_absent_acp_schema_is_a_failure
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_absent_acp_schema_is_a_failure')",
  "summary": "Found 205 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_absent_acp_schema_is_a_failure') \u2014 showing 100, 105 omitted",
      "name": "test_m1_manifest_zeroed",
      "name": "test_m2_tampered_sig",
      "name": "test_m2_wrong_pubkey",
      "name": "test_m3_cancel_foreign",
      "name": "test_m4_shutdown_init_only",
      "name": "test_m5_1s",
      "name": "test_m5_7200",
      "name": "test_deletion",
      "name": "test_del_mentions",
      "name": "test_del_upstream",
      "name": "test_del_baseline",
### ripwire callers
<callers of="test_ck11_absent_acp_schema_is_a_failure" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_ck11_absent_acp_schema_is_a_failure">

## symbol test_ck11_no_presence_gated_check_in_the_proof
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_no_presence_gated_check_in_the_proof')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_no_presence_gated_check_in_the_proof')",
### ripwire callers
<callers of="test_ck11_no_presence_gated_check_in_the_proof" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_ck11_no_presence_gated_check_in_the_proof">

## symbol test_ck11_every_read_is_under_the_walk_or_require_file
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_every_read_is_under_the_walk_or_require_file')",
  "summary": "Found 1 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_every_read_is_under_the_walk_or_require_file')",
      "name": "test_ck11_every_read_is_under_the_walk_or_require_file",
### ripwire callers
<callers of="test_ck11_every_read_is_under_the_walk_or_require_file" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_ck11_every_read_is_under_the_walk_or_require_file">

## symbol owner
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::owner')",
      "name": "test_ck11_every_read_is_under_the_walk_or_require_file",
  "summary": "Found 2 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::owner')",
      "name": "test_ck11_every_read_is_under_the_walk_or_require_file",
      "name": "test_owner_swap",
### ripwire callers
<callers of="owner" defs="9" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=owner">

## symbol test_ck10_rejected_cap_installs_no_handler
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck10_rejected_cap_installs_no_handler')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck10_rejected_cap_installs_no_handler')",
### ripwire callers
<callers of="test_ck10_rejected_cap_installs_no_handler" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_ck10_rejected_cap_installs_no_handler">

## symbol test_ck11_alarm_inside_try_cannot_leak_the_handler
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_alarm_inside_try_cannot_leak_the_handler')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_alarm_inside_try_cannot_leak_the_handler')",
### ripwire callers
<callers of="test_ck11_alarm_inside_try_cannot_leak_the_handler" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_ck11_alarm_inside_try_cannot_leak_the_handler">

## symbol test_ck11_dead_branch_comments_cite_a_real_guard
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_dead_branch_comments_cite_a_real_guard')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck11_dead_branch_comments_cite_a_real_guard')",
### ripwire callers
<callers of="test_ck11_dead_branch_comments_cite_a_real_guard" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="1" graph_unresolved="31" counts_floor="1" next="--uses=test_ck11_dead_branch_comments_cite_a_real_guard">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
<test-gate changed="1" impacted="0" tests="0" untested="0" shown_tests="0" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="4" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="40e8471d2+dirty" next="--situ">
