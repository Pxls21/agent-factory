# lane context pack — d83baa8 2026-09-15T10:09Z
files: proofs/S0-01/check_acp_conformance.py tests/test_s0_01_check_acp_conformance.py proofs/S0-01/pins.py
symbols: _pinned_process_count _captured_leg_version _scan_direct_writes _presence_gate_hits _enumerate_read_sites _validate_dead_branch_citations _read_site_drift test_v24_table_rows_key_cannot_be_replaced_by_rows _write_unknown_scan_header test_ck13_unknown_header_is_not_downgraded test_ck12_corpus_version_rejects_missing_scan test_ck13_main_closes_system_exit_status_domain test_ck13_checker_has_no_private_pinned_process_predicate test_ck13_process_evidence_consumes_shared_predicate classify test_real_leg_runtime_identity test_ck13_bound_path_open_mutant test_ck13_os_link_mutant test_ck13_os_symlink_mutant test_ck13_shutil_move_mutant test_ck13_tar_extractall_mutant test_ck13_zip_extract_mutant test_ck13_presence_gate_detector_covers_each_probe_family _resolve_bound_path_aliases test_ck13_read_inventory_covers_each_declared_family test_ck13_read_site_drift_names_added_and_removed_sites test_ck13_checker_names_each_missing_required_file test_ck13_dead_branch_citation_mutants_die test_ck13_read_site_drift_validator_rejects_rebound_expected test_ck11_dead_branch_comments_cite_a_real_guard test_ck13_dead_branch_validator_names_all_bad_and_missing_citations

## proofs/S0-01/check_acp_conformance.py
### graft skeleton

graft skeleton — proofs/S0-01/check_acp_conformance.py
- L34-L35  function _fixtures  def _fixtures() -> Path
- L161-L162  class Deferred  class Deferred(Exception)
- L165-L166  class Failure  class Failure(Exception)
- L169-L174  function _sha256_file  def _sha256_file(path: Path) -> str
- L177-L178  function _sha256_bytes  def _sha256_bytes(data: bytes) -> str
- L181-L182  function _parse_utc  def _parse_utc(s: str) -> datetime
- L185-L186  function _parse_utc_summary  def _parse_utc_summary(s: str) -> datetime
- L189-L192  function _reject_nan  def _reject_nan(line: str, leg: str, seq_hint: int)
- L190-L191  function _raise  def _raise(c)
- L195-L204  function _require_file  def _require_file(path: Path, leg: str, name: str)
- L207-L210  function _require_dir  def _require_dir(path: Path, leg: str, name: str)
- L213-L215  function _is_strict_int  def _is_strict_int(v)
- L254-L263  function _run_check  def _run_check(fn, leg, *args, **kwargs)
- L266-L370  function check_timeline  def check_timeline(entries, leg, leg_dir)
- L305-L332  function _load_dir  def _load_dir(fpath, name, expected_split)
- L373-L394  function check_initialize_frames  def check_initialize_frames(c2a, a2c, leg, schema=None)
- L397-L439  function check_runtime_identity  def check_runtime_identity(leg_dir, leg)
- L410-L412  function _chk  def _chk(field, expected, desc=None)
- L442-L512  function check_env  def check_env(leg_dir, leg, identities)
- L515-L601  function check_mentions  def check_mentions(leg_dir, leg, identities, entries, post_summary_ts=None)
- L604-L706  function check_route  def check_route(leg_dir, leg, entries)
- L709-L722  function _prompt_windows  def _prompt_windows(entries, leg)
- L725-L781  function check_prompt_turn  def check_prompt_turn(c2a, a2c, leg, entries, expect_stop="end_turn")
- L784-L791  function _shape  def _shape(value)
- L794-L861  function normalize_timeline  def normalize_timeline(entries)
- L798-L800  function id_ph  def id_ph(v)
- L802-L803  function sid_ph  def sid_ph(v)
- L864-L887  function check_cancel  def check_cancel(entries, c2a, a2c, leg_dir, leg="cancel")
- L890-L895  function check_shutdown  def check_shutdown(entries, c2a, a2c, leg_dir, leg="shutdown")
- L898-L975  function check_two_users  def check_two_users(c2a, a2c, entries, identities, leg="two-users", *, leg_dir)
- L978-L1013  function check_manifests  def check_manifests(leg_dir, leg, baseline_path, baseline_gz_sha)
- L1016-L1052  function _parse_manifest_body  def _parse_manifest_body(body: bytes, leg: str) -> dict
- L1055-L1066  function _parse_summary  def _parse_summary(summary_path, leg, name)
- L1069-L1169  function check_config_echo  def check_config_echo(leg_dir, leg)
- L1172-L1192  function _parse_scan_v24  def _parse_scan_v24(path, leg, name)
- L1195-L1197  function _pinned_process_count  def _pinned_process_count(commands)
- L1200-L1385  function check_process_evidence  def check_process_evidence(leg_dir, leg)
- L1388-L1407  function check_buzzacp_log  def check_buzzacp_log(leg_dir, leg)
- L1410-L1508  function check_tee_status  def check_tee_status(leg_dir, leg, entries)
- L1511-L1531  function check_negative  def check_negative(neg_dir, leg="negative")
- L1534-L1635  function check_golden  def check_golden(golden_dir, leg="golden")
- L1614-L1620  function _raw_sid  def _raw_sid(ents)
- L1638-L1647  function _load_timeline_raw  def _load_timeline_raw(leg_dir, leg)
- L1650-L1666  function _check_with_timeout  def _check_with_timeout(timeout_s, fn, *args)
- L1653-L1655  function _raise_timeout  def _raise_timeout(signum, frame)
- L1669-L1680  function check_bundle  def check_bundle(root: Path, timeout_s: int = 90) -> str: # R8-CK-F2: the wall-clock cap lives HERE so in-process consumers get it too. # Default 90 s < the runner's 120 s. # R9-CK-F1: reject non-positive, non-int, and out-of-range caps. # alarm(0) cancels the alarm silently; bool/float/NaN/inf/str are not ints; # values >= 2**31 overflow signal.alarm's C int (AF-AP-58 sibling).
- L1683-L1702  function _captured_leg_version  def _captured_leg_version(golden: Path) -> str
- L1705-L1851  function _check_bundle_uncapped  def _check_bundle_uncapped(root: Path) -> str
- L1854-L1903  function main  def main(argv) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 11 hits over 1 files ---
AF-AP-40: 5
    proofs/S0-01/check_acp_conformance.py:1514: if neg_dir.is_dir():
    proofs/S0-01/check_acp_conformance.py:1527: if stderr_path.exists():
    proofs/S0-01/check_acp_conformance.py:1751: if item.is_dir() and item.name not in expected_dirs:
    proofs/S0-01/check_acp_conformance.py:1753: if item.is_file() and item.name not in expected_files:
    proofs/S0-01/check_acp_conformance.py:1766: if post_sum_path.exists():
AF-AP-72: 4
    proofs/S0-01/check_acp_conformance.py:1188: pid, ppid, etimes = int(parts[0]), int(parts[1]), int(parts[2])
    proofs/S0-01/check_acp_conformance.py:1188: pid, ppid, etimes = int(parts[0]), int(parts[1]), int(parts[2])
    proofs/S0-01/check_acp_conformance.py:1188: pid, ppid, etimes = int(parts[0]), int(parts[1]), int(parts[2])
    proofs/S0-01/check_acp_conformance.py:1873: timeout_s = int(args[idx + 1])
AP-32: 2
    proofs/S0-01/check_acp_conformance.py:170: h = hashlib.sha256()
    proofs/S0-01/check_acp_conformance.py:178: return hashlib.sha256(data).hexdigest()

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
    tests/test_s0_01_check_acp_conformance.py:5352: assert all(site[3] in {"walk", "require_regular_file", "stdin", "consumer"}
AF-AP-57: 1
    tests/test_s0_01_check_acp_conformance.py:4797: if call_count[0] == 2:

## proofs/S0-01/pins.py
### graft skeleton

graft skeleton — proofs/S0-01/pins.py
- L19-L28  function require_regular_file  def require_regular_file(path: Path, what: str, failure_type: type[Exception] = ValueError) -> Path
- L365-L366  function _version_key  def _version_key(version)
- L369-L382  function required_files  def required_files(version)
- L385-L392  function entry_allowlist  def entry_allowlist()
- L395-L447  function corpus_version  def corpus_version(leg_dir)
- L450-L461  function content_constraint  def content_constraint(version, name)
- L464-L572  function validate_artifact  def validate_artifact(leg_dir, name, version)
- L499-L503  function _utf8  def _utf8(b)
- L575-L576  class ConstraintFailure  class ConstraintFailure(ValueError)
- L579-L607  function is_pinned_argv  def is_pinned_argv(argv)
- L610-L629  function hermes_home  def hermes_home()
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 4 hits over 1 files ---
AF-AP-72: 3
    proofs/S0-01/pins.py:567: int(parts[0]); int(parts[1]); int(parts[2])
    proofs/S0-01/pins.py:567: int(parts[0]); int(parts[1]); int(parts[2])
    proofs/S0-01/pins.py:567: int(parts[0]); int(parts[1]); int(parts[2])
AP-1: 1
    proofs/S0-01/pins.py:623: override = os.environ.get("S0_01_HERMES_HOME")

## graft ask — How does the S0-01 checker consume pins.is_pinned_argv, pins.corpus_version, pins.required_files and pins.entry_allowlist after round 14; which test-side scanners (_scan_direct_writes, _presence_gate_hits, _enumerate_read_sites) enumerate which syntax families, and what do they declare as excluded?
graft ask — "How does the S0-01 checker consume pins.is_pinned_argv, pins.corpus_version, pins.required_files and pins.entry_allowlist after round 14; which test-side scanners (_scan_direct_writes, _presence_gate_hits, _enumerate_read_sites) enumerate which syntax families, and what do they declare as excluded?"  (lexical)

1. pins.py · file  [symbol]
   proofs/S0-01/pins.py

2. main · function  [symbol]
   proofs/S0-01/tools/pc/pc_launch.py:L281-L425
   def main()

3. main · function  [symbol]
   proofs/S0-01/tools/build_capture_record.py:L48-L217
   def main() -> int

4. _captured_leg_version · function  [symbol]
   proofs/S0-01/check_acp_conformance.py:L1683-L1702
   def _captured_leg_version(golden: Path) -> str

5. main · function  [symbol]
   proofs/S0-01/tools/acp_probe.py:L253-L673
   def main(): # Validate required env vars early with a named message (L15/A10: exit 64). # Empty/unset cases exit 64 WITHOUT probe_error because the try block (which # writes runtime-identity.json) has not started yet — this is a documented # exception: probe_error requires the wrapped body to have opened.

6. validate_negative_dir · function  [symbol]
   proofs/S0-01/negative_contract.py:L87-L222
   def validate_negative_dir(neg_dir: Path, fixtures_dir: Path | None = None) -> str

7. check_initialize.py · file  [symbol]
   proofs/S0-01/check_initialize.py

8. _framing_gate · method  [symbol]
   proofs/S0-01/tools/scripted_backend.py:L599-L645
   def _framing_gate(self) -> bool

## symbol _pinned_process_count
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/proofs/S0-01/check_acp_conformance.py::_pinned_process_count'.",
  "summary": "No node found matching '/home/user/agent-factory/proofs/S0-01/check_acp_conformance.py::_pinned_process_count'.",
### ripwire callers
<callers of="_pinned_process_count" defs="1" count="2" root="/home/user/agent-factory" hop_tested="1" hop_untested="1" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_pinned_process_count">

## symbol _captured_leg_version
### GitNexus impact (upstream)
  "impactedCount": 4,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 0,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/check_acp_conformance.py::_captured_leg_version')",
      "name": "_check_bundle_uncapped",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/check_acp_conformance.py::_captured_leg_version')",
### ripwire callers
<callers of="_captured_leg_version" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_captured_leg_version">

## symbol _scan_direct_writes
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_scan_direct_writes')",
      "name": "test_f43_no_direct_writes_outside_rewrite",
  "summary": "Found 1 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_scan_direct_writes')",
      "name": "test_f43_no_direct_writes_outside_rewrite",
### ripwire callers
<callers of="_scan_direct_writes" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_scan_direct_writes">

## symbol _presence_gate_hits
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 3 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_presence_gate_hits')",
      "name": "test_ck12_no_presence_gated_check_in_the_proof",
      "name": "test_ck12_presence_gate_detector_catches_all_ten_shapes",
      "name": "test_ck12_presence_exemption_is_comment_stable",
  "summary": "Found 3 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_presence_gate_hits')",
      "name": "test_ck12_no_presence_gated_check_in_the_proof",
      "name": "test_ck12_presence_gate_detector_catches_all_ten_shapes",
      "name": "test_ck12_presence_exemption_is_comment_stable",
### ripwire callers
<callers of="_presence_gate_hits" defs="1" count="4" root="/home/user/agent-factory" hop_tested="0" hop_untested="4" shown="4" capped="0" total="4" has_more="0" next_offset="4" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_presence_gate_hits">

## symbol _enumerate_read_sites
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_enumerate_read_sites')",
      "name": "test_ck12_every_read_matches_the_guarded_golden_list",
      "name": "test_ck12_read_inventory_detects_new_site_and_guard_drift",
  "summary": "Found 2 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_enumerate_read_sites')",
      "name": "test_ck12_every_read_matches_the_guarded_golden_list",
      "name": "test_ck12_read_inventory_detects_new_site_and_guard_drift",
### ripwire callers
<callers of="_enumerate_read_sites" defs="1" count="3" root="/home/user/agent-factory" hop_tested="0" hop_untested="3" shown="3" capped="0" total="3" has_more="0" next_offset="3" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_enumerate_read_sites">

## symbol _validate_dead_branch_citations
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_validate_dead_branch_citations'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_validate_dead_branch_citations'.",
### ripwire callers
<callers of="_validate_dead_branch_citations" defs="1" count="3" root="/home/user/agent-factory" hop_tested="0" hop_untested="3" shown="3" capped="0" total="3" has_more="0" next_offset="3" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_validate_dead_branch_citations">

## symbol _read_site_drift
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_read_site_drift'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_read_site_drift'.",
### ripwire callers
<callers of="_read_site_drift" defs="1" count="3" root="/home/user/agent-factory" hop_tested="0" hop_untested="3" shown="3" capped="0" total="3" has_more="0" next_offset="3" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_read_site_drift">

## symbol test_v24_table_rows_key_cannot_be_replaced_by_rows
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_v24_table_rows_key_cannot_be_replaced_by_rows'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_v24_table_rows_key_cannot_be_replaced_by_rows'.",
### ripwire callers
<callers of="test_v24_table_rows_key_cannot_be_replaced_by_rows" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_v24_table_rows_key_cannot_be_replaced_by_rows">

## symbol _write_unknown_scan_header
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_write_unknown_scan_header'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_write_unknown_scan_header'.",
### ripwire callers
<callers of="_write_unknown_scan_header" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_write_unknown_scan_header">

## symbol test_ck13_unknown_header_is_not_downgraded
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_unknown_header_is_not_downgraded'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_unknown_header_is_not_downgraded'.",
### ripwire callers
<callers of="test_ck13_unknown_header_is_not_downgraded" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck13_unknown_header_is_not_downgraded">

## symbol test_ck12_corpus_version_rejects_missing_scan
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck12_corpus_version_rejects_missing_scan'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck12_corpus_version_rejects_missing_scan'.",
### ripwire callers
<callers of="test_ck12_corpus_version_rejects_missing_scan" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck12_corpus_version_rejects_missing_scan">

## symbol test_ck13_main_closes_system_exit_status_domain
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_main_closes_system_exit_status_domain'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_main_closes_system_exit_status_domain'.",
### ripwire callers
<callers of="test_ck13_main_closes_system_exit_status_domain" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck13_main_closes_system_exit_status_domain">

## symbol test_ck13_checker_has_no_private_pinned_process_predicate
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_checker_has_no_private_pinned_process_predicate'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_checker_has_no_private_pinned_process_predicate'.",
### ripwire callers
<callers of="test_ck13_checker_has_no_private_pinned_process_predicate" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck13_checker_has_no_private_pinned_process_predicate">

## symbol test_ck13_process_evidence_consumes_shared_predicate
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_process_evidence_consumes_shared_predicate'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_process_evidence_consumes_shared_predicate'.",
### ripwire callers
<callers of="test_ck13_process_evidence_consumes_shared_predicate" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck13_process_evidence_consumes_shared_predicate">

## symbol classify
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_classify_read_guard')",
      "name": "_enumerate_read_sites",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_classify_read_guard')",
### ripwire callers
<callers of="classify" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=classify">

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
<callers of="test_real_leg_runtime_identity" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_real_leg_runtime_identity">

## symbol test_ck13_bound_path_open_mutant
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_bound_path_open_mutant'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_bound_path_open_mutant'.",
### ripwire callers

## symbol test_ck13_os_link_mutant
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_os_link_mutant'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_os_link_mutant'.",
### ripwire callers

## symbol test_ck13_os_symlink_mutant
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_os_symlink_mutant'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_os_symlink_mutant'.",
### ripwire callers

## symbol test_ck13_shutil_move_mutant
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_shutil_move_mutant'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_shutil_move_mutant'.",
### ripwire callers

## symbol test_ck13_tar_extractall_mutant
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_tar_extractall_mutant'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_tar_extractall_mutant'.",
### ripwire callers

## symbol test_ck13_zip_extract_mutant
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_zip_extract_mutant'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_zip_extract_mutant'.",
### ripwire callers

## symbol test_ck13_presence_gate_detector_covers_each_probe_family
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_presence_gate_detector_covers_each_probe_family'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_presence_gate_detector_covers_each_probe_family'.",
### ripwire callers
<callers of="test_ck13_presence_gate_detector_covers_each_probe_family" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck13_presence_gate_detector_covers_each_probe_family">

## symbol _resolve_bound_path_aliases
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_resolve_bound_path_aliases'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::_resolve_bound_path_aliases'.",
### ripwire callers
<callers of="_resolve_bound_path_aliases" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=_resolve_bound_path_aliases">

## symbol test_ck13_read_inventory_covers_each_declared_family
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_read_inventory_covers_each_declared_family'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_read_inventory_covers_each_declared_family'.",
### ripwire callers
<callers of="test_ck13_read_inventory_covers_each_declared_family" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck13_read_inventory_covers_each_declared_family">

## symbol test_ck13_read_site_drift_names_added_and_removed_sites
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_read_site_drift_names_added_and_removed_sites'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_read_site_drift_names_added_and_removed_sites'.",
### ripwire callers
<callers of="test_ck13_read_site_drift_names_added_and_removed_sites" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck13_read_site_drift_names_added_and_removed_sites">

## symbol test_ck13_checker_names_each_missing_required_file
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_checker_names_each_missing_required_file'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_checker_names_each_missing_required_file'.",
### ripwire callers
<callers of="test_ck13_checker_names_each_missing_required_file" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck13_checker_names_each_missing_required_file">

## symbol test_ck13_dead_branch_citation_mutants_die
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_dead_branch_citation_mutants_die'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_dead_branch_citation_mutants_die'.",
### ripwire callers
<callers of="test_ck13_dead_branch_citation_mutants_die" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck13_dead_branch_citation_mutants_die">

## symbol test_ck13_read_site_drift_validator_rejects_rebound_expected
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_read_site_drift_validator_rejects_rebound_expected'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_read_site_drift_validator_rejects_rebound_expected'.",
### ripwire callers
<callers of="test_ck13_read_site_drift_validator_rejects_rebound_expected" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck13_read_site_drift_validator_rejects_rebound_expected">

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
<callers of="test_ck11_dead_branch_comments_cite_a_real_guard" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck11_dead_branch_comments_cite_a_real_guard">

## symbol test_ck13_dead_branch_validator_names_all_bad_and_missing_citations
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_dead_branch_validator_names_all_bad_and_missing_citations'.",
  "summary": "No node found matching '/home/user/agent-factory/tests/test_s0_01_check_acp_conformance.py::test_ck13_dead_branch_validator_names_all_bad_and_missing_citations'.",
### ripwire callers
<callers of="test_ck13_dead_branch_validator_names_all_bad_and_missing_citations" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="87" counts_floor="1" next="--uses=test_ck13_dead_branch_validator_names_all_bad_and_missing_citations">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
