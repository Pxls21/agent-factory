# lane context pack — 1a1ec4b 2026-09-14T12:31Z
files: proofs/S0-01/pins.py proofs/S0-01/tools/build_capture_record.py proofs/S0-01/tools/pc/pc_launch.py tests/conftest.py tests/test_s0_01_pc_post_scan.py tests/test_s0_01_pc_tools.py
symbols: ConstraintFailure _idiom_contribution _launch_env_fixture _leg_with_scan _utf8 content_constraint env_json_with_set_marker launch_env test_an_unknown_env_set_name_is_refused_by_name test_corpus_version_accepts_the_good_v24_header test_corpus_version_refuses_a_header_in_the_body_after_rows test_corpus_version_refuses_a_header_with_trailing_fields test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name test_corpus_version_refuses_a_second_header_line_in_the_body test_corpus_version_refuses_an_unknown_header_version test_corpus_version_refuses_crlf_line_endings test_each_declared_parser_idiom_resolves_exactly_its_pinned_count test_env_json_names_the_set_that_launched_the_capture test_the_content_constraint_table_is_complete_and_pinned test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log validate_artifact

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

## proofs/S0-01/tools/build_capture_record.py
### graft skeleton

graft skeleton — proofs/S0-01/tools/build_capture_record.py
- L23-L24  function _sha256  def _sha256(data: bytes) -> str
- L27-L32  function _sha256_file  def _sha256_file(p: Path) -> str
- L35-L45  function _parse_manifest_gz  def _parse_manifest_gz(gz_path: Path) -> dict
- L48-L217  function main  def main() -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 17 hits over 1 files ---
AF-AP-40: 12
    proofs/S0-01/tools/build_capture_record.py:102: if tl_path.exists():
    proofs/S0-01/tools/build_capture_record.py:126: if rid_path.exists():
    proofs/S0-01/tools/build_capture_record.py:131: if env_path.exists():
    proofs/S0-01/tools/build_capture_record.py:137: if startup_path.exists():
    proofs/S0-01/tools/build_capture_record.py:144: if model_path.exists():
    proofs/S0-01/tools/build_capture_record.py:148: # VERIFY-P5a F7: `receipt = json.loads(rp.read_text()) if rp.exists() else {}` was an UNDOMINATED pr
    ... +6
AP-32: 4
    proofs/S0-01/tools/build_capture_record.py:23: def _sha256(data: bytes) -> str:
    proofs/S0-01/tools/build_capture_record.py:24: return hashlib.sha256(data).hexdigest()
    proofs/S0-01/tools/build_capture_record.py:28: h = hashlib.sha256()
    proofs/S0-01/tools/build_capture_record.py:45: return {k: _sha256(v.encode("utf-8")) for k, v in sections.items()}
AF-AP-41: 1
    proofs/S0-01/tools/build_capture_record.py:139: kvs = dict(re.findall(r"(idle_timeout|max_turn|session_policy)=(\S+)", startup))

## proofs/S0-01/tools/pc/pc_launch.py
### graft skeleton

graft skeleton — proofs/S0-01/tools/pc/pc_launch.py
- L45-L46  function utc_now  def utc_now()
- L49-L54  function sha256_file  def sha256_file(path)
- L57-L64  function read_kv  def read_kv(path, key)
- L67-L76  function alive_pinned_buzz  def alive_pinned_buzz(pidfile)
- L79-L82  function masked_log_text  def masked_log_text(raw_path)
- L85-L108  function wait_for_manifest  def wait_for_manifest(fd, phase, tries=600)
- L111-L118  function summary_tail  def summary_tail(path)
- L121-L133  function wait_for_tee_identity  def wait_for_tee_identity(fd, tries=60)
- L136-L146  function buzz_identity  def buzz_identity(pid, rc)
- L149-L174  function session_closure  def session_closure(pid)
- L177-L193  function redact_environ  def redact_environ(raw, red)
- L196-L203  function env_json_with_set_marker  def env_json_with_set_marker(live_env, env_set)
- L206-L208  function leg_framedir  def leg_framedir(markers, leg)
- L211-L239  function resolve_launch_profile  def resolve_launch_profile(leg, model, profile, hermes_home)
- L242-L278  function launch_env  def launch_env(leg, framedir, hermes_home, respond_to, allowlist, sec_dir, hermes_env, env_set="s0-01")
- L281-L425  function main  def main()
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 11 hits over 1 files ---
AP-51: 3
    proofs/S0-01/tools/pc/pc_launch.py:199: s0-01 writes NO marker, so its env.json stays byte-identical to the pre-extension bytes."""
    proofs/S0-01/tools/pc/pc_launch.py:246: (byte-identical to the pre-extension launcher), S0-02 adds exactly the one pinned key/value
    proofs/S0-01/tools/pc/pc_launch.py:290: help="pinned launch env set: s0-01 (default, byte-identical to the pre-extension launcher) "
AF-AP-45: 2
    proofs/S0-01/tools/pc/pc_launch.py:153: detach shares that session. Walking the FULL `ps -eo pid,ppid` table instead adopts any foreign row 
    proofs/S0-01/tools/pc/pc_launch.py:156: ps = subprocess.run(["ps", "-s", str(pid), "-o", "pid,ppid", "--no-headers"],
AF-AP-55: 2
    proofs/S0-01/tools/pc/pc_launch.py:73: exe = os.readlink(f"/proc/{pid}/exe")
    proofs/S0-01/tools/pc/pc_launch.py:144: return os.readlink(f"/proc/{pid}/exe"), sha256_file(f"/proc/{pid}/exe")
AF-AP-72: 2
    proofs/S0-01/tools/pc/pc_launch.py:162: rows.append((int(parts[0]), int(parts[1])))
    proofs/S0-01/tools/pc/pc_launch.py:162: rows.append((int(parts[0]), int(parts[1])))
AP-32: 2
    proofs/S0-01/tools/pc/pc_launch.py:50: h = hashlib.sha256()
    proofs/S0-01/tools/pc/pc_launch.py:190: "sha256_12": hashlib.sha256(vb).hexdigest()[:12]}

## tests/conftest.py
### graft skeleton

graft skeleton — tests/conftest.py
- L24-L72  function synthetic_leg  def synthetic_leg()
- L37-L70  function _make  def _make(dst)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---

## tests/test_s0_01_pc_post_scan.py
### graft skeleton

graft skeleton — tests/test_s0_01_pc_post_scan.py
- L49-L59  function tree  def tree()
- L62-L64  function _scan  def _scan(mode: str, fd: Path) -> subprocess.CompletedProcess
- L67-L69  function _seed  def _seed(fd: Path, buzz: int, owned: list[int]) -> None
- L72-L84  function _parse  def _parse(path: Path)
- L91-L100  function _is_pinned  def _is_pinned(cmd: str) -> bool
- L103-L113  function _split_world  def _split_world(rows, owned)
- L116-L121  function _gone_or_zombie  def _gone_or_zombie(pid: int) -> bool
- L124-L131  function _wait_gone  def _wait_gone(pids, timeout=10.0)
- L134-L155  function test_after_scan_persists_the_owned_closure_and_the_header  def test_after_scan_persists_the_owned_closure_and_the_header(tree, tmp_path)
- L158-L174  function test_teardown_scan_after_a_clean_exit_is_empty_with_owned_present_zero  def test_teardown_scan_after_a_clean_exit_is_empty_with_owned_present_zero(tree, tmp_path)
- L177-L190  function test_teardown_scan_names_an_owned_survivor_whatever_its_command  def test_teardown_scan_names_an_owned_survivor_whatever_its_command(tree, tmp_path)
- L193-L198  function test_scan_rejects_an_unknown_mode  def test_scan_rejects_an_unknown_mode(tmp_path)
- L201-L226  function test_scan_rows_are_not_clipped_at_80_columns  def test_scan_rows_are_not_clipped_at_80_columns(tmp_path)
- L229-L250  function test_owned_row_is_never_dropped_by_the_helper_filter  def test_owned_row_is_never_dropped_by_the_helper_filter(tmp_path)
- L253-L268  function test_scan_fails_loud_on_an_unparsable_ps_row  def test_scan_fails_loud_on_an_unparsable_ps_row(tmp_path)
- L271-L300  function test_a_process_that_only_mentions_a_pinned_path_is_not_counted_as_pinned  def test_a_process_that_only_mentions_a_pinned_path_is_not_counted_as_pinned(tmp_path)
- L303-L307  function test_split_world_rejects_an_unexplained_foreign_row  def test_split_world_rejects_an_unexplained_foreign_row()
- L310-L317  function test_split_world_admits_a_foreign_row_that_is_a_pinned_entry_point  def test_split_world_admits_a_foreign_row_that_is_a_pinned_entry_point()
- L320-L327  function test_split_world_rejects_a_row_that_only_mentions_a_pinned_path  def test_split_world_rejects_a_row_that_only_mentions_a_pinned_path()
- L330-L341  function test_parse_rejects_a_header_whose_rows_counter_lies  def test_parse_rejects_a_header_whose_rows_counter_lies(tmp_path)
- L344-L395  function test_pinned_present_is_exact_over_a_synthetic_table  def test_pinned_present_is_exact_over_a_synthetic_table(tmp_path)
- L405-L407  function _leg_with_scan  def _leg_with_scan(tmp_path, first, rest="")
- L410-L411  function test_corpus_version_accepts_the_good_v24_header  def test_corpus_version_accepts_the_good_v24_header(tmp_path)
- L414-L416  function test_corpus_version_refuses_a_second_header_line_in_the_body  def test_corpus_version_refuses_a_second_header_line_in_the_body(tmp_path)
- L419-L422  function test_corpus_version_refuses_a_header_in_the_body_after_rows  def test_corpus_version_refuses_a_header_in_the_body_after_rows(tmp_path)
- L425-L429  function test_corpus_version_refuses_a_header_with_trailing_fields  def test_corpus_version_refuses_a_header_with_trailing_fields(tmp_path)
- L432-L434  function test_corpus_version_refuses_crlf_line_endings  def test_corpus_version_refuses_crlf_line_endings(tmp_path)
- L437-L441  function test_corpus_version_refuses_an_unknown_header_version  def test_corpus_version_refuses_an_unknown_header_version(tmp_path)
- L444-L451  function test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name  def test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name(tmp_path)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---

## tests/test_s0_01_pc_tools.py
### graft skeleton

graft skeleton — tests/test_s0_01_pc_tools.py
- L49-L55  function _corpus  def _corpus()
- L58-L76  function _corpus_version  def _corpus_version()
- L135-L139  function _expand  def _expand(name)
- L142-L169  function _framedir_names  def _framedir_names(rel, root=None)
- L172-L178  function test_the_status_vocabulary_is_closed_and_the_dirs_are_named  def test_the_status_vocabulary_is_closed_and_the_dirs_are_named()
- L181-L208  function test_the_content_constraint_table_is_complete_and_pinned  def test_the_content_constraint_table_is_complete_and_pinned()
- L211-L221  function test_every_corpus_leg_entry_is_in_the_pinned_mapping  def test_every_corpus_leg_entry_is_in_the_pinned_mapping()
- L224-L233  function test_no_collected_leg_may_carry_an_excluded_name  def test_no_collected_leg_may_carry_an_excluded_name()
- L236-L247  function test_every_required_name_is_present_in_every_corpus_positive_leg  def test_every_required_name_is_present_in_every_corpus_positive_leg()
- L250-L258  function test_the_corpus_version_rule_actually_discriminates  def test_the_corpus_version_rule_actually_discriminates()
- L269-L271  function test_the_one_corpus_version_detector_reads_the_header  def test_the_one_corpus_version_detector_reads_the_header(tmp_path, line, expected)
- L276-L284  function test_the_one_corpus_version_detector_refuses_to_default  def test_the_one_corpus_version_detector_refuses_to_default(tmp_path, line)
- L287-L291  function test_the_corpus_version_detector_defers_to_the_completeness_gate_when_there_is_no_scan  def test_the_corpus_version_detector_defers_to_the_completeness_gate_when_there_is_no_scan(tmp_path)
- L294-L302  function test_the_entry_allowlist_is_the_three_admissible_statuses  def test_the_entry_allowlist_is_the_three_admissible_statuses()
- L305-L310  function test_every_pinned_dir_is_present_in_every_corpus_positive_leg  def test_every_pinned_dir_is_present_in_every_corpus_positive_leg()
- L313-L318  function test_the_negative_corpus_leg_is_exactly_the_pinned_negative_set  def test_the_negative_corpus_leg_is_exactly_the_pinned_negative_set()
- L340-L348  function test_every_producer_write_lands_in_the_pinned_mapping  def test_every_producer_write_lands_in_the_pinned_mapping(rel)
- L352-L361  function test_the_producer_parse_does_not_lose_coverage  def test_the_producer_parse_does_not_lose_coverage(rel)
- L364-L383  function _idiom_contribution  def _idiom_contribution(rel, name, root=None)
- L386-L399  function test_each_declared_parser_idiom_resolves_exactly_its_pinned_count  def test_each_declared_parser_idiom_resolves_exactly_its_pinned_count()
- L402-L410  function test_every_pinned_name_has_a_producer  def test_every_pinned_name_has_a_producer()
- L413-L423  function test_no_positive_leg_producer_writes_agent_stderr_txt  def test_no_positive_leg_producer_writes_agent_stderr_txt()
- L426-L434  function test_the_framedir_parser_fails_loud_on_an_unresolved_placeholder  def test_the_framedir_parser_fails_loud_on_an_unresolved_placeholder(tmp_path)
- L451-L460  function test_the_producer_parser_recognises_every_declared_idiom  def test_the_producer_parser_recognises_every_declared_idiom(tmp_path, source, expected)
- L466-L467  function _capture  def _capture(*args)
- L470-L477  function test_build_capture_record_fails_on_a_leg_with_no_timeline  def test_build_capture_record_fails_on_a_leg_with_no_timeline(tmp_path)
- L484-L491  function test_build_capture_record_writes_the_record_for_a_complete_leg  def test_build_capture_record_writes_the_record_for_a_complete_leg(tmp_path, synthetic_leg)
- L496-L512  function test_build_capture_record_takes_its_required_list_from_pins  def test_build_capture_record_takes_its_required_list_from_pins(tmp_path, synthetic_leg, dropped)
- L516-L530  function test_build_capture_record_requires_a_regular_file_not_just_an_entry  def test_build_capture_record_requires_a_regular_file_not_just_an_entry(tmp_path, synthetic_leg, shape)
- L533-L546  function test_build_capture_record_accepts_a_v2_2_corpus_leg  def test_build_capture_record_accepts_a_v2_2_corpus_leg(tmp_path)
- L549-L561  function test_build_capture_record_fails_on_an_empty_timeline  def test_build_capture_record_fails_on_an_empty_timeline(tmp_path, synthetic_leg)
- L564-L579  function test_build_capture_record_fails_on_a_mention_with_no_receipt  def test_build_capture_record_fails_on_a_mention_with_no_receipt(tmp_path, synthetic_leg)
- L582-L594  function test_build_capture_record_check_mode_keeps_its_own_diagnosis  def test_build_capture_record_check_mode_keeps_its_own_diagnosis(tmp_path, synthetic_leg)
- L597-L600  function test_capture_json_is_admitted_by_the_pinned_mapping  def test_capture_json_is_admitted_by_the_pinned_mapping()
- L606-L611  class _NoSleep  class _NoSleep
- L610-L611  method sleep  def sleep(self, seconds)
- L615-L616  function nosleep  def nosleep(monkeypatch)
- L619-L627  function test_pre_manifest_wait_breaks_on_a_manifest_error  def test_pre_manifest_wait_breaks_on_a_manifest_error(tmp_path, nosleep)
- L630-L634  function test_pre_manifest_wait_returns_when_the_marker_lands  def test_pre_manifest_wait_returns_when_the_marker_lands(tmp_path, nosleep)
- L637-L640  function test_pre_manifest_wait_still_times_out_when_nothing_happens  def test_pre_manifest_wait_still_times_out_when_nothing_happens(tmp_path, nosleep)
- L643-L651  function test_pc_launch_survives_an_empty_pre_manifest_summary  def test_pc_launch_survives_an_empty_pre_manifest_summary(tmp_path)
- L654-L660  function test_pc_launch_fails_when_the_tee_identity_never_appears  def test_pc_launch_fails_when_the_tee_identity_never_appears(tmp_path, nosleep)
- L663-L672  function test_pc_launch_names_a_buzz_exit_during_identity_capture  def test_pc_launch_names_a_buzz_exit_during_identity_capture(monkeypatch)
- L667-L668  function boom  def boom(path)
- L675-L680  function test_pc_launch_captures_the_identity_of_a_live_process  def test_pc_launch_captures_the_identity_of_a_live_process()
- L683-L716  function test_pc_launch_owned_closure_is_scoped_to_the_buzz_session  def test_pc_launch_owned_closure_is_scoped_to_the_buzz_session()
- L719-L725  function test_pc_launch_owned_closure_fails_loud_on_a_dead_session  def test_pc_launch_owned_closure_fails_loud_on_a_dead_session()
- L728-L743  function test_env_redaction_fingerprints_the_raw_bytes  def test_env_redaction_fingerprints_the_raw_bytes()
- L746-L754  function test_env_redaction_covers_every_pinned_secret_key_name  def test_env_redaction_covers_every_pinned_secret_key_name()
- L760-L768  function _stub_probe  def _stub_probe(tmp_path, ending)
- L777-L796  function test_pc_negative_propagates_the_probe_exit_code  def test_pc_negative_propagates_the_probe_exit_code(tmp_path, monkeypatch, capsys, ending, expected)
- L814-L815  function _exclude_patterns  def _exclude_patterns()
- L818-L838  function test_collect_leg_exclusions_and_the_pinned_mapping_agree  def test_collect_leg_exclusions_and_the_pinned_mapping_agree()
- L841-L847  function test_every_excluded_on_collect_name_is_really_excluded  def test_every_excluded_on_collect_name_is_really_excluded()
- L850-L852  function _glob_match  def _glob_match(pattern, name)
- L855-L860  function test_the_leg_drivers_stop_on_the_first_failure  def test_the_leg_drivers_stop_on_the_first_failure()
- L863-L889  function test_the_collected_shape_is_the_mapping_minus_what_collect_drops  def test_the_collected_shape_is_the_mapping_minus_what_collect_drops(tmp_path)
- L907-L913  function test_is_pinned_argv_matches_the_entry_point_only  def test_is_pinned_argv_matches_the_entry_point_only(cmd, pinned, why)
- L916-L924  function test_is_pinned_argv_does_not_count_a_pinned_binary_reached_by_another_path  def test_is_pinned_argv_does_not_count_a_pinned_binary_reached_by_another_path()
- L927-L935  function test_is_pinned_argv_matches_every_row_of_the_real_corpus_scan  def test_is_pinned_argv_matches_every_row_of_the_real_corpus_scan()
- L938-L945  function test_the_scan_producer_and_its_test_shim_read_one_rule  def test_the_scan_producer_and_its_test_shim_read_one_rule()
- L951-L962  function test_the_s0_01_legs_keep_their_closed_set_without_a_profile  def test_the_s0_01_legs_keep_their_closed_set_without_a_profile()
- L975-L985  function test_the_launcher_cli_really_reaches_the_leg_validator  def test_the_launcher_cli_really_reaches_the_leg_validator(argv, expected)
- L988-L1003  function test_a_foreign_leg_launches_against_its_own_profile  def test_a_foreign_leg_launches_against_its_own_profile(tmp_path)
- L1006-L1026  function test_the_launch_env_carries_the_profile_home_and_the_leg_name  def test_the_launch_env_carries_the_profile_home_and_the_leg_name(tmp_path)
- L1029-L1036  function _launch_env_fixture  def _launch_env_fixture(tmp_path)
- L1039-L1061  function test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log  def test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log(tmp_path)
- L1064-L1075  function test_an_unknown_env_set_name_is_refused_by_name  def test_an_unknown_env_set_name_is_refused_by_name(tmp_path)
- L1078-L1088  function test_env_json_names_the_set_that_launched_the_capture  def test_env_json_names_the_set_that_launched_the_capture()
- L1091-L1096  function _pins_in_subprocess  def _pins_in_subprocess(env_extra, expr="print(pins.hermes_home())")
- L1099-L1110  function test_the_hermes_home_override_is_validated  def test_the_hermes_home_override_is_validated(tmp_path)
- L1113-L1124  function test_the_override_never_moves_the_pin_the_checker_compares_against  def test_the_override_never_moves_the_pin_the_checker_compares_against(tmp_path)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---

## graft ask — who calls validate_artifact, content_constraint and corpus_version in proofs/S0-01/pins.py, and who consumes env_set in proofs/S0-01/tools/pc/pc_launch.py
graft ask — "who calls validate_artifact, content_constraint and corpus_version in proofs/S0-01/pins.py, and who consumes env_set in proofs/S0-01/tools/pc/pc_launch.py"  (structural)

callers / references of content_constraint

- validate_artifact  proofs/S0-01/pins.py:L464-L572  (calls) — def validate_artifact(leg_dir, name, version)

## symbol ConstraintFailure
### GitNexus impact (upstream)
  "impactedCount": 6,
  "risk": "MEDIUM",
  "epistemic": "exact",
    "direct": 6,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/pins.py::ConstraintFailure')",
      "name": "validate_artifact",
      "name": "_utf8",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/pins.py::ConstraintFailure')",
### ripwire callers
<callers of="ConstraintFailure" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=ConstraintFailure">

## symbol _idiom_contribution
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::_idiom_contribution')",
      "name": "test_each_declared_parser_idiom_resolves_exactly_its_pinned_count",
  "summary": "Found 1 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::_idiom_contribution')",
      "name": "test_each_declared_parser_idiom_resolves_exactly_its_pinned_count",
### ripwire callers
<callers of="_idiom_contribution" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=_idiom_contribution">

## symbol _launch_env_fixture
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::_launch_env_fixture')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::_launch_env_fixture')",
### ripwire callers
<callers of="_launch_env_fixture" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=_launch_env_fixture">

## symbol _leg_with_scan
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 7 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::_leg_with_scan')",
      "name": "test_corpus_version_accepts_the_good_v24_header",
      "name": "test_corpus_version_refuses_a_second_header_line_in_the_body",
      "name": "test_corpus_version_refuses_a_header_in_the_body_after_rows",
      "name": "test_corpus_version_refuses_a_header_with_trailing_fields",
      "name": "test_corpus_version_refuses_crlf_line_endings",
      "name": "test_corpus_version_refuses_an_unknown_header_version",
      "name": "test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name",
  "summary": "Found 7 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::_leg_with_scan')",
      "name": "test_corpus_version_accepts_the_good_v24_header",
      "name": "test_corpus_version_refuses_a_second_header_line_in_the_body",
      "name": "test_corpus_version_refuses_a_header_in_the_body_after_rows",
      "name": "test_corpus_version_refuses_a_header_with_trailing_fields",
      "name": "test_corpus_version_refuses_crlf_line_endings",
      "name": "test_corpus_version_refuses_an_unknown_header_version",
      "name": "test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name",
### ripwire callers
<callers of="_leg_with_scan" defs="1" count="7" root="/home/user/agent-factory" hop_tested="0" hop_untested="7" shown="7" capped="0" total="7" has_more="0" next_offset="7" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=_leg_with_scan">

## symbol _utf8
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/pins.py::_utf8')",
      "name": "validate_artifact",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/pins.py::_utf8')",
### ripwire callers
<callers of="_utf8" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=_utf8">

## symbol content_constraint
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/pins.py::content_constraint')",
      "name": "test_the_content_constraint_table_is_complete_and_pinned",
      "name": "validate_artifact",
  "summary": "Found 6 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/pins.py::content_constraint')",
      "name": "test_the_content_constraint_table_is_complete_and_pinned",
      "name": "test_every_required_name_is_present_in_every_corpus_positive_leg",
      "name": "test_the_corpus_version_rule_actually_discriminates",
      "name": "test_the_corpus_version_detector_defers_to_the_completeness_gate_when_there_is_no_scan",
      "name": "test_the_entry_allowlist_is_the_three_admissible_statuses",
      "name": "test_build_capture_record_accepts_a_v2_2_corpus_leg",
### ripwire callers
<callers of="content_constraint" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=content_constraint">

## symbol env_json_with_set_marker
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 0,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/pc/pc_launch.py::env_json_with_set_marker')",
      "name": "test_env_json_names_the_set_that_launched_the_capture",
      "name": "main",
  "summary": "Found 1 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/pc/pc_launch.py::env_json_with_set_marker')",
      "name": "test_env_json_names_the_set_that_launched_the_capture",
### ripwire callers
<callers of="env_json_with_set_marker" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=env_json_with_set_marker">

## symbol launch_env
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 0,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 4 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/tools/pc/pc_launch.py::launch_env')",
      "name": "test_the_launch_env_carries_the_profile_home_and_the_leg_name",
      "name": "test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log",
      "name": "test_an_unknown_env_set_name_is_refused_by_name",
      "name": "main",
  "summary": "Found 3 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/tools/pc/pc_launch.py::launch_env')",
      "name": "test_the_launch_env_carries_the_profile_home_and_the_leg_name",
      "name": "test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log",
      "name": "test_an_unknown_env_set_name_is_refused_by_name",
### ripwire callers
<callers of="launch_env" defs="1" count="4" root="/home/user/agent-factory" hop_tested="0" hop_untested="4" shown="4" capped="0" total="4" has_more="0" next_offset="4" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=launch_env">

## symbol test_an_unknown_env_set_name_is_refused_by_name
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::test_an_unknown_env_set_name_is_refused_by_name')",
  "summary": "Found 3 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::test_an_unknown_env_set_name_is_refused_by_name')",
      "name": "test_the_launch_env_carries_the_profile_home_and_the_leg_name",
      "name": "test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log",
      "name": "test_an_unknown_env_set_name_is_refused_by_name",
### ripwire callers
<callers of="test_an_unknown_env_set_name_is_refused_by_name" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_an_unknown_env_set_name_is_refused_by_name">

## symbol test_corpus_version_accepts_the_good_v24_header
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_accepts_the_good_v24_header')",
  "summary": "Found 11 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_accepts_the_good_v24_header')",
      "name": "test_corpus_version_accepts_the_good_v24_header",
      "name": "test_corpus_version_refuses_a_second_header_line_in_the_body",
      "name": "test_corpus_version_refuses_a_header_in_the_body_after_rows",
      "name": "test_corpus_version_refuses_a_header_with_trailing_fields",
      "name": "test_corpus_version_refuses_crlf_line_endings",
      "name": "test_corpus_version_refuses_an_unknown_header_version",
      "name": "test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name",
      "name": "test_the_one_corpus_version_detector_reads_the_header",
      "name": "test_the_one_corpus_version_detector_refuses_to_default",
      "name": "test_the_corpus_version_detector_defers_to_the_completeness_gate_when_there_is_no_scan",
      "name": "test_build_capture_record_accepts_a_v2_2_corpus_leg",
### ripwire callers
<callers of="test_corpus_version_accepts_the_good_v24_header" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_corpus_version_accepts_the_good_v24_header">

## symbol test_corpus_version_refuses_a_header_in_the_body_after_rows
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_refuses_a_header_in_the_body_after_rows')",
  "summary": "Found 11 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_refuses_a_header_in_the_body_after_rows')",
      "name": "test_corpus_version_accepts_the_good_v24_header",
      "name": "test_corpus_version_refuses_a_second_header_line_in_the_body",
      "name": "test_corpus_version_refuses_a_header_in_the_body_after_rows",
      "name": "test_corpus_version_refuses_a_header_with_trailing_fields",
      "name": "test_corpus_version_refuses_crlf_line_endings",
      "name": "test_corpus_version_refuses_an_unknown_header_version",
      "name": "test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name",
      "name": "test_the_one_corpus_version_detector_reads_the_header",
      "name": "test_the_one_corpus_version_detector_refuses_to_default",
      "name": "test_the_corpus_version_detector_defers_to_the_completeness_gate_when_there_is_no_scan",
      "name": "test_build_capture_record_accepts_a_v2_2_corpus_leg",
### ripwire callers
<callers of="test_corpus_version_refuses_a_header_in_the_body_after_rows" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_corpus_version_refuses_a_header_in_the_body_after_rows">

## symbol test_corpus_version_refuses_a_header_with_trailing_fields
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_refuses_a_header_with_trailing_fields')",
  "summary": "Found 11 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_refuses_a_header_with_trailing_fields')",
      "name": "test_corpus_version_accepts_the_good_v24_header",
      "name": "test_corpus_version_refuses_a_second_header_line_in_the_body",
      "name": "test_corpus_version_refuses_a_header_in_the_body_after_rows",
      "name": "test_corpus_version_refuses_a_header_with_trailing_fields",
      "name": "test_corpus_version_refuses_crlf_line_endings",
      "name": "test_corpus_version_refuses_an_unknown_header_version",
      "name": "test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name",
      "name": "test_the_one_corpus_version_detector_reads_the_header",
      "name": "test_the_one_corpus_version_detector_refuses_to_default",
      "name": "test_the_corpus_version_detector_defers_to_the_completeness_gate_when_there_is_no_scan",
      "name": "test_build_capture_record_accepts_a_v2_2_corpus_leg",
### ripwire callers
<callers of="test_corpus_version_refuses_a_header_with_trailing_fields" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_corpus_version_refuses_a_header_with_trailing_fields">

## symbol test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name')",
  "summary": "Found 11 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name')",
      "name": "test_the_one_corpus_version_detector_reads_the_header",
      "name": "test_the_one_corpus_version_detector_refuses_to_default",
      "name": "test_the_corpus_version_detector_defers_to_the_completeness_gate_when_there_is_no_scan",
      "name": "test_build_capture_record_accepts_a_v2_2_corpus_leg",
      "name": "test_corpus_version_accepts_the_good_v24_header",
      "name": "test_corpus_version_refuses_a_second_header_line_in_the_body",
      "name": "test_corpus_version_refuses_a_header_in_the_body_after_rows",
      "name": "test_corpus_version_refuses_a_header_with_trailing_fields",
      "name": "test_corpus_version_refuses_crlf_line_endings",
      "name": "test_corpus_version_refuses_an_unknown_header_version",
      "name": "test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name",
### ripwire callers
<callers of="test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name">

## symbol test_corpus_version_refuses_a_second_header_line_in_the_body
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_refuses_a_second_header_line_in_the_body')",
  "summary": "Found 11 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_refuses_a_second_header_line_in_the_body')",
      "name": "test_corpus_version_accepts_the_good_v24_header",
      "name": "test_corpus_version_refuses_a_second_header_line_in_the_body",
      "name": "test_corpus_version_refuses_a_header_in_the_body_after_rows",
      "name": "test_corpus_version_refuses_a_header_with_trailing_fields",
      "name": "test_corpus_version_refuses_crlf_line_endings",
      "name": "test_corpus_version_refuses_an_unknown_header_version",
      "name": "test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name",
      "name": "test_the_one_corpus_version_detector_reads_the_header",
      "name": "test_the_one_corpus_version_detector_refuses_to_default",
      "name": "test_the_corpus_version_detector_defers_to_the_completeness_gate_when_there_is_no_scan",
      "name": "test_build_capture_record_accepts_a_v2_2_corpus_leg",
### ripwire callers
<callers of="test_corpus_version_refuses_a_second_header_line_in_the_body" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_corpus_version_refuses_a_second_header_line_in_the_body">

## symbol test_corpus_version_refuses_an_unknown_header_version
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_refuses_an_unknown_header_version')",
  "summary": "Found 11 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_refuses_an_unknown_header_version')",
      "name": "test_the_one_corpus_version_detector_reads_the_header",
      "name": "test_the_one_corpus_version_detector_refuses_to_default",
      "name": "test_the_corpus_version_detector_defers_to_the_completeness_gate_when_there_is_no_scan",
      "name": "test_build_capture_record_accepts_a_v2_2_corpus_leg",
      "name": "test_corpus_version_accepts_the_good_v24_header",
      "name": "test_corpus_version_refuses_a_second_header_line_in_the_body",
      "name": "test_corpus_version_refuses_a_header_in_the_body_after_rows",
      "name": "test_corpus_version_refuses_a_header_with_trailing_fields",
      "name": "test_corpus_version_refuses_crlf_line_endings",
      "name": "test_corpus_version_refuses_an_unknown_header_version",
      "name": "test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name",
### ripwire callers
<callers of="test_corpus_version_refuses_an_unknown_header_version" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_corpus_version_refuses_an_unknown_header_version">

## symbol test_corpus_version_refuses_crlf_line_endings
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_refuses_crlf_line_endings')",
  "summary": "Found 11 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_post_scan.py::test_corpus_version_refuses_crlf_line_endings')",
      "name": "test_the_one_corpus_version_detector_reads_the_header",
      "name": "test_the_one_corpus_version_detector_refuses_to_default",
      "name": "test_the_corpus_version_detector_defers_to_the_completeness_gate_when_there_is_no_scan",
      "name": "test_build_capture_record_accepts_a_v2_2_corpus_leg",
      "name": "test_corpus_version_accepts_the_good_v24_header",
      "name": "test_corpus_version_refuses_a_second_header_line_in_the_body",
      "name": "test_corpus_version_refuses_a_header_in_the_body_after_rows",
      "name": "test_corpus_version_refuses_a_header_with_trailing_fields",
      "name": "test_corpus_version_refuses_crlf_line_endings",
      "name": "test_corpus_version_refuses_an_unknown_header_version",
      "name": "test_corpus_version_refuses_a_headerless_leg_that_claims_a_v24_name",
### ripwire callers
<callers of="test_corpus_version_refuses_crlf_line_endings" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_corpus_version_refuses_crlf_line_endings">

## symbol test_each_declared_parser_idiom_resolves_exactly_its_pinned_count
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::test_each_declared_parser_idiom_resolves_exactly_its_pinned_count')",
  "summary": "Found 1 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::test_each_declared_parser_idiom_resolves_exactly_its_pinned_count')",
      "name": "test_each_declared_parser_idiom_resolves_exactly_its_pinned_count",
### ripwire callers
<callers of="test_each_declared_parser_idiom_resolves_exactly_its_pinned_count" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_each_declared_parser_idiom_resolves_exactly_its_pinned_count">

## symbol test_env_json_names_the_set_that_launched_the_capture
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::test_env_json_names_the_set_that_launched_the_capture')",
  "summary": "Found 1 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::test_env_json_names_the_set_that_launched_the_capture')",
      "name": "test_env_json_names_the_set_that_launched_the_capture",
### ripwire callers
<callers of="test_env_json_names_the_set_that_launched_the_capture" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_env_json_names_the_set_that_launched_the_capture">

## symbol test_the_content_constraint_table_is_complete_and_pinned
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::test_the_content_constraint_table_is_complete_and_pinned')",
  "summary": "Found 6 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::test_the_content_constraint_table_is_complete_and_pinned')",
      "name": "test_the_content_constraint_table_is_complete_and_pinned",
      "name": "test_every_required_name_is_present_in_every_corpus_positive_leg",
      "name": "test_the_corpus_version_rule_actually_discriminates",
      "name": "test_the_corpus_version_detector_defers_to_the_completeness_gate_when_there_is_no_scan",
      "name": "test_the_entry_allowlist_is_the_three_admissible_statuses",
      "name": "test_build_capture_record_accepts_a_v2_2_corpus_leg",
### ripwire callers
<callers of="test_the_content_constraint_table_is_complete_and_pinned" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_the_content_constraint_table_is_complete_and_pinned">

## symbol test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log')",
  "summary": "Found 3 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_01_pc_tools.py::test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log')",
      "name": "test_the_launch_env_carries_the_profile_home_and_the_leg_name",
      "name": "test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log",
      "name": "test_an_unknown_env_set_name_is_refused_by_name",
### ripwire callers
<callers of="test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_the_s0_02_env_set_adds_exactly_the_pinned_rust_log">

## symbol validate_artifact
### GitNexus impact (upstream)
  "impactedCount": 2,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/proofs/S0-01/pins.py::validate_artifact')",
      "name": "main",
  "summary": "Found 1 result(s) for tests_for('/home/user/agent-factory/proofs/S0-01/pins.py::validate_artifact')",
      "name": "test_the_content_constraint_table_is_complete_and_pinned",
### ripwire callers
<callers of="validate_artifact" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=validate_artifact">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
