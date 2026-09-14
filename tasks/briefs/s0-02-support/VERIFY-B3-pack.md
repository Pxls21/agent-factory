# lane context pack — 1a1ec4b 2026-09-14T12:30Z
files: proofs/S0-02/check_buzz_authz.py proofs/S0-02/tools/build_fixtures.py proofs/S0-02/tools/pc/deliver_event.py tests/test_s0_02_buzz_authz.py
symbols: _leg_closure _require_real_dir test_evidence_root_replaced_by_a_symlink_is_refused test_extra_regular_file_inside_a_leg_is_refused test_leg_file_table_matches_the_runner_writes test_leg_replaced_by_a_symlink_to_an_outside_copy_is_refused test_missing_required_file_inside_a_leg_is_named test_normalise_takes_accepted_only_when_upstream_is_bool test_privkey_normalises_then_refuses_before_any_network_action test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance test_replay_leg_must_carry_exactly_the_two_subleg_directories test_replay_subleg_replaced_by_a_symlink_is_refused test_wall_clock_freshness_scan_documented_limit_is_not_silently_widened

## proofs/S0-02/check_buzz_authz.py
### graft skeleton

graft skeleton — proofs/S0-02/check_buzz_authz.py
- L64-L76  class Anchors  class Anchors
- L65-L68  method __init__  def __init__(self, identities_path: Path, fixtures_dir: Path, synthetic: bool)
- L71-L72  method default  def default(cls)
- L75-L76  method from_synthetic_root  def from_synthetic_root(cls, root: Path)
- L79-L85  function _load_by_path  def _load_by_path(name: str, path: Path)
- L102-L117  function _require_real_dir  def _require_real_dir(path: Path, leg: str, name: str) -> Path
- L155-L167  function _leg_closure  def _leg_closure(leg_dir: Path, leg: str, expected: frozenset)
- L170-L175  function _read_json  def _read_json(path: Path, leg: str, name: str)
- L178-L190  function _prompt_frames  def _prompt_frames(entries, leg)
- L193-L196  function _prompt_text  def _prompt_text(frame) -> str
- L199-L201  function _check_masking  def _check_masking(log_text: str, leg: str)
- L204-L253  function _check_delivered_event  def _check_delivered_event(leg_dir: Path, leg: str, fixture: dict, identities: dict) -> dict
- L256-L295  function _check_freshness  def _check_freshness(leg_dir: Path, leg: str, fixture: dict, delivered: dict)
- L298-L360  function _check_delivery  def _check_delivery( leg_dir: Path, leg: str, delivered: dict, fixture: dict, expected_accepted: "bool | None" = None, ) -> dict
- L368-L406  function _observe_all  def _observe_all(leg_dir: Path, leg: str, delivery: dict, fixture_name: str) -> frozenset
- L409-L411  function _observed_key  def _observed_key(found: frozenset) -> str
- L414-L448  function _check_named_observable  def _check_named_observable(leg: str, fixture_name: str, found: frozenset, delivery: dict)
- L451-L454  function _turns  def _turns(leg_dir: Path, leg: str)
- L457-L558  function _check_leg  def _check_leg(leg_dir: Path, leg: str, fixture_name: str, identities: dict, anchors: "Anchors")
- L561-L626  function _check_replay  def _check_replay(root: Path, identities: dict, anchors: "Anchors")
- L629-L648  function _has_any_timeline  def _has_any_timeline(root: Path) -> bool
- L651-L725  function _check_bundle_uncapped  def _check_bundle_uncapped(root: Path, anchors: "Anchors") -> str: # The root itself must be a real directory, not a symlink: resolve() would # happily re-anchor every later containment check under the symlink target.
- L728-L731  function check_bundle  def check_bundle(root: Path, anchors: "Anchors | None" = None) -> str
- L734-L761  function main  def main(argv) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## proofs/S0-02/tools/build_fixtures.py
### graft skeleton

graft skeleton — proofs/S0-02/tools/build_fixtures.py
- L52-L58  function _load_module  def _load_module(name: str, path: Path)
- L61-L63  function _load_nostr_verify  def _load_nostr_verify()
- L83-L85  function _specimen_privkey  def _specimen_privkey(fixture_name: str) -> str
- L88-L89  function _identities  def _identities() -> dict
- L176-L180  function _oracle  def _oracle()
- L183-L185  function _tags  def _tags(ids: dict) -> list
- L188-L252  function build_one  def build_one(spec: dict, ids: dict, built: dict) -> dict
- L255-L260  function build_all  def build_all(ids: dict | None = None) -> dict
- L263-L264  function _serialise  def _serialise(fixture: dict) -> str
- L283-L284  function _bundle_privkey  def _bundle_privkey(bundle: str, role: str) -> str
- L287-L294  function _bundle_identities  def _bundle_identities(bundle: str) -> dict
- L297-L302  function _iso  def _iso(offset_ms: int) -> str
- L305-L338  function _timeline  def _timeline(with_turn: bool, prompt_text: str) -> str
- L341-L352  function _log  def _log(extra_lines) -> str
- L355-L361  function _raw_delivery_response  def _raw_delivery_response(*, accepted: bool, event_id: str, message: str) -> str
- L364-L401  function _write_leg  def _write_leg(leg_dir: Path, fixture: dict, ids: dict, bundle: str, *, accepted: bool, message: str, with_turn: bool, log_extra, membership: dict | None = None)
- L407-L420  function _tamper  def _tamper(leg_dir: Path, pos_delivered: dict) -> None
- L423-L506  function build_bundle  def build_bundle(bundle: str, root: Path) -> None
- L448-L449  function leg  def leg(name)
- L509-L545  function main  def main(argv) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 3 hits over 1 files ---
AP-32: 2
    proofs/S0-02/tools/build_fixtures.py:85: return hashlib.sha256(f"{SPECIMEN_SEED}/{fixture_name}".encode()).hexdigest()
    proofs/S0-02/tools/build_fixtures.py:284: return hashlib.sha256(f"{SPECIMEN_SEED}/bundle/{bundle}/{role}".encode()).hexdigest()
AF-AP-40: 1
    proofs/S0-02/tools/build_fixtures.py:428: if root.exists():

## proofs/S0-02/tools/pc/deliver_event.py
### graft skeleton

graft skeleton — proofs/S0-02/tools/pc/deliver_event.py
- L59-L65  function _load  def _load(name: str, path: Path)
- L71-L89  function _privkey  def _privkey() -> str
- L92-L103  function _nip98_header  def _nip98_header(privkey: str, url: str, method: str, body: bytes) -> str
- L106-L115  function _post  def _post(url: str, body: bytes, header: str) -> tuple
- L118-L162  function _normalise  def _normalise(status: int, raw: str, event_id: str) -> dict
- L165-L217  function main  def main(argv) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 2 hits over 1 files ---
AP-1: 1
    proofs/S0-02/tools/pc/deliver_event.py:78: key = os.environ.get("BUZZ_PRIVATE_KEY", "").strip().lower()
AP-32: 1
    proofs/S0-02/tools/pc/deliver_event.py:95: payload = hashlib.sha256(body).hexdigest()

## tests/test_s0_02_buzz_authz.py
### graft skeleton

graft skeleton — tests/test_s0_02_buzz_authz.py
- L42-L46  function _load  def _load(name: str, path: Path)
- L60-L64  function _bundle  def _bundle(tmp_path: Path, src: Path = PASS_BUNDLE) -> Path
- L67-L70  function _run_checker  def _run_checker(bundle_root: Path, legs: str = "legs")
- L73-L77  function _expect_failure  def _expect_failure(bundle_root: Path, needle: str, legs: str = "legs")
- L80-L81  function _leg  def _leg(bundle_root: Path, name: str) -> Path
- L84-L87  function _set_delivery_outcome  def _set_delivery_outcome(blob: dict, *, accepted: bool, status: int, echoed: bool) -> None
- L90-L93  function _set_delivery_event_id  def _set_delivery_event_id(blob: dict, event_id: str) -> None
- L96-L99  function _rewrite  def _rewrite(path: Path, mutate)
- L102-L117  function _buzz_src  def _buzz_src() -> Path
- L123-L126  function test_committed_fixtures_equal_a_fresh_build  def test_committed_fixtures_equal_a_fresh_build()
- L129-L132  function test_fixture_build_is_byte_identical_across_two_runs  def test_fixture_build_is_byte_identical_across_two_runs()
- L135-L161  function test_every_bundle_delivery_uses_the_real_producer_normalizer  def test_every_bundle_delivery_uses_the_real_producer_normalizer()
- L164-L168  function test_every_named_fixture_exists_and_names_itself  def test_every_named_fixture_exists_and_names_itself()
- L171-L176  function test_positive_specimen_verifies  def test_positive_specimen_verifies()
- L179-L183  function test_bad_signature_specimen_is_rejected_by_verify_event  def test_bad_signature_specimen_is_rejected_by_verify_event()
- L186-L191  function test_bad_signature_specimen_differs_from_positive_only_in_the_signature  def test_bad_signature_specimen_differs_from_positive_only_in_the_signature()
- L194-L199  function test_replayed_specimen_is_the_positive_event_id  def test_replayed_specimen_is_the_positive_event_id()
- L202-L209  function test_stale_specimen_created_at_clears_the_relay_window  def test_stale_specimen_created_at_clears_the_relay_window()
- L212-L216  function test_self_authored_specimen_names_the_agent_identity  def test_self_authored_specimen_names_the_agent_identity()
- L219-L225  function test_unauthorized_specimen_is_not_a_known_identity  def test_unauthorized_specimen_is_not_a_known_identity()
- L228-L244  function test_no_committed_fixture_carries_a_private_key  def test_no_committed_fixture_carries_a_private_key()
- L234-L241  function walk  def walk(node, where)
- L247-L253  function test_every_negative_fixture_carries_its_own_expected_failure_block  def test_every_negative_fixture_carries_its_own_expected_failure_block()
- L256-L263  function test_the_four_seed_reasons_are_all_present  def test_the_four_seed_reasons_are_all_present()
- L266-L272  function test_not_allowlisted_specimen_is_relay_accepted_user2  def test_not_allowlisted_specimen_is_relay_accepted_user2()
- L278-L287  function test_pinned_tree_is_the_locked_commit  def test_pinned_tree_is_the_locked_commit()
- L290-L297  function test_pinned_tree_non_git_path_is_a_named_failure  def test_pinned_tree_non_git_path_is_a_named_failure(tmp_path, monkeypatch)
- L301-L312  function test_oracle_row_line_still_carries_its_pattern  def test_oracle_row_line_still_carries_its_pattern(row)
- L315-L319  function test_oracle_secondary_silent_drop_row_is_pinned_too  def test_oracle_secondary_silent_drop_row_is_pinned_too()
- L322-L340  function test_oracle_prose_file_line_references_exist  def test_oracle_prose_file_line_references_exist()
- L343-L420  function _rust_code_lines  def _rust_code_lines(text: str) -> list[tuple[int, str]]
- L423-L439  function _production_verify_sites  def _production_verify_sites() -> list[str]
- L442-L454  function _channel_event_region  def _channel_event_region(relay_text: str) -> tuple[int, int]
- L457-L462  function _copy_buzz_acp_src  def _copy_buzz_acp_src(tmp_path: Path) -> Path
- L465-L478  function test_verify_site_scan_rejects_a_channel_path_plant  def test_verify_site_scan_rejects_a_channel_path_plant(tmp_path, monkeypatch)
- L481-L490  function test_verify_site_scan_finds_an_aliased_call  def test_verify_site_scan_finds_an_aliased_call(tmp_path, monkeypatch)
- L493-L505  function test_verify_site_scan_ignores_cfg_test_items_and_comments  def test_verify_site_scan_ignores_cfg_test_items_and_comments(tmp_path, monkeypatch)
- L508-L530  function test_buzz_acp_performs_no_signature_check_on_a_channel_event  def test_buzz_acp_performs_no_signature_check_on_a_channel_event()
- L533-L545  function test_buzz_acp_has_no_per_event_freshness_constant_for_channel_events  def test_buzz_acp_has_no_per_event_freshness_constant_for_channel_events()
- L548-L560  function _is_wall_clock_freshness_rule  def _is_wall_clock_freshness_rule(line: str) -> bool
- L563-L582  function test_buzz_acp_has_no_wall_clock_freshness_rule_on_the_channel_event_path  def test_buzz_acp_has_no_wall_clock_freshness_rule_on_the_channel_event_path()
- L585-L596  function test_wall_clock_freshness_scan_rejects_an_inline_rule  def test_wall_clock_freshness_scan_rejects_an_inline_rule()
- L599-L618  function test_wall_clock_freshness_scan_documented_limit_is_not_silently_widened  def test_wall_clock_freshness_scan_documented_limit_is_not_silently_widened()
- L621-L640  function test_shipped_respond_to_and_subscription_rule_defaults_do_not_reference_timestamp  def test_shipped_respond_to_and_subscription_rule_defaults_do_not_reference_timestamp()
- L643-L648  function test_relay_drift_window_matches_the_checker_constant  def test_relay_drift_window_matches_the_checker_constant()
- L651-L656  function test_debug_canary_line_exists_in_the_pinned_source  def test_debug_canary_line_exists_in_the_pinned_source()
- L659-L661  function test_every_negative_row_has_a_distinct_observable_key  def test_every_negative_row_has_a_distinct_observable_key()
- L664-L670  function test_revoked_row_declares_its_shared_text_as_a_discrepancy  def test_revoked_row_declares_its_shared_text_as_a_discrepancy()
- L674-L676  function test_rows_without_a_buzz_acp_observable_say_so  def test_rows_without_a_buzz_acp_observable_say_so(fixture)
- L682-L688  function test_pass_bundle_passes  def test_pass_bundle_passes()
- L691-L699  function test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output  def test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output()
- L702-L710  function test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance  def test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance()
- L713-L716  function test_blanket_bundle_is_a_blanket_rejection  def test_blanket_bundle_is_a_blanket_rejection()
- L719-L730  function test_spec_negative_leg_reason_is_the_exact_observed_line  def test_spec_negative_leg_reason_is_the_exact_observed_line()
- L733-L737  function test_spec_validates_against_the_repo_schema  def test_spec_validates_against_the_repo_schema()
- L740-L747  function test_spec_positive_leg_points_at_the_real_evidence_root  def test_spec_positive_leg_points_at_the_real_evidence_root()
- L750-L755  function test_deferred_when_the_evidence_root_is_absent  def test_deferred_when_the_evidence_root_is_absent(tmp_path)
- L758-L763  function test_real_evidence_root_defers_today  def test_real_evidence_root_defers_today()
- L766-L778  function test_all_timelines_removed_defers_and_never_passes  def test_all_timelines_removed_defers_and_never_passes(tmp_path)
- L781-L787  function test_deferral_stops_once_any_leg_carries_a_timeline  def test_deferral_stops_once_any_leg_carries_a_timeline(tmp_path)
- L794-L806  function test_removing_a_legs_observable_fails_that_leg  def test_removing_a_legs_observable_fails_that_leg(tmp_path, name)
- L810-L827  function test_swapping_a_legs_observable_for_another_legs_fails  def test_swapping_a_legs_observable_for_another_legs_fails(tmp_path, name)
- L830-L845  function test_bad_signature_leg_delivering_a_VALID_event_fails  def test_bad_signature_leg_delivering_a_VALID_event_fails(tmp_path)
- L848-L867  function test_two_legs_with_swapped_observables_fail_the_named_check  def test_two_legs_with_swapped_observables_fail_the_named_check(tmp_path)
- L870-L882  function test_a_buzz_acp_leg_showing_only_a_relay_reason_fails_the_named_check  def test_a_buzz_acp_leg_showing_only_a_relay_reason_fails_the_named_check(tmp_path)
- L885-L900  function test_wrong_channel_observables_are_rejected  def test_wrong_channel_observables_are_rejected(tmp_path)
- L903-L911  function test_a_leg_with_two_denial_observables_is_not_counted_as_a_distinct_reason  def test_a_leg_with_two_denial_observables_is_not_counted_as_a_distinct_reason(tmp_path)
- L914-L919  function test_a_negative_leg_that_produced_a_turn_fails  def test_a_negative_leg_that_produced_a_turn_fails(tmp_path)
- L922-L930  function test_a_positive_leg_with_two_turns_fails  def test_a_positive_leg_with_two_turns_fails(tmp_path)
- L933-L937  function test_a_positive_leg_with_no_turn_fails  def test_a_positive_leg_with_no_turn_fails(tmp_path)
- L940-L945  function test_a_positive_turn_without_the_fixture_nonce_fails  def test_a_positive_turn_without_the_fixture_nonce_fails(tmp_path)
- L948-L954  function test_positive_nonce_must_be_a_complete_json_token  def test_positive_nonce_must_be_a_complete_json_token()
- L957-L963  function test_a_missing_debug_canary_fails_a_buzz_acp_leg  def test_a_missing_debug_canary_fails_a_buzz_acp_leg(tmp_path)
- L966-L970  function test_an_info_level_canary_does_not_prove_debug_capture  def test_an_info_level_canary_does_not_prove_debug_capture(tmp_path)
- L973-L980  function test_relay_decided_leg_needs_no_debug_canary  def test_relay_decided_leg_needs_no_debug_canary(tmp_path)
- L983-L988  function test_self_authored_leg_requires_ignore_self_true  def test_self_authored_leg_requires_ignore_self_true(tmp_path)
- L991-L995  function test_unmasked_pubkey_in_the_log_fails  def test_unmasked_pubkey_in_the_log_fails(tmp_path)
- L1001-L1006  function test_replay_second_delivery_with_a_turn_fails  def test_replay_second_delivery_with_a_turn_fails(tmp_path)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 4 hits over 1 files ---
AF-AP-34: 4
    tests/test_s0_02_buzz_authz.py:1467: """AF-AP-34: no pkill/killall/name match anywhere in the PC runner."""
    tests/test_s0_02_buzz_authz.py:1467: """AF-AP-34: no pkill/killall/name match anywhere in the PC runner."""
    tests/test_s0_02_buzz_authz.py:1471: for word in ("pkill", "killall", "pgrep"):
    tests/test_s0_02_buzz_authz.py:1471: for word in ("pkill", "killall", "pgrep"):

## graft ask — who calls _require_real_dir and _leg_closure in proofs/S0-02/check_buzz_authz.py, and who consumes the receipt that _normalise in proofs/S0-02/tools/pc/deliver_event.py writes
graft ask — "who calls _require_real_dir and _leg_closure in proofs/S0-02/check_buzz_authz.py, and who consumes the receipt that _normalise in proofs/S0-02/tools/pc/deliver_event.py writes"  (lexical)

⚠ structural index: no entries for 'check_buzz_authz.py' — showing lexical matches; for precise edges try graft callers 'check_buzz_authz.py', or graft grep 'check_buzz_authz.py' for every reference (loosen the pattern if it returns nothing)

1. deliver_event.py · file  [symbol]
   proofs/S0-02/tools/pc/deliver_event.py

2. _check_leg · function  [symbol]
   proofs/S0-02/check_buzz_authz.py:L457-L558
   def _check_leg(leg_dir: Path, leg: str, fixture_name: str, identities: dict, anchors: "Anchors")

3. _write_leg · function  [symbol]
   proofs/S0-02/tools/build_fixtures.py:L364-L401
   def _write_leg(leg_dir: Path, fixture: dict, ids: dict, bundle: str, *, accepted: bool, message: str, with_turn: bool, log_extra, membership: dict | None = None)

4. denial_table.py · file  [symbol]
   proofs/S0-02/oracle/denial_table.py

5. main · function  [symbol]
   proofs/S0-02/tools/pc/deliver_event.py:L165-L217
   def main(argv) -> int

6. check_buzz_authz.py · file  [symbol]
   proofs/S0-02/check_buzz_authz.py

7. build_fixtures.py · file  [symbol]
   proofs/S0-02/tools/build_fixtures.py

8. row · function  [symbol]
   proofs/S0-02/oracle/denial_table.py:L277-L279
   def row(fixture: str) -> dict

## symbol _leg_closure
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 2,
    "processes_affected": 0,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/proofs/S0-02/check_buzz_authz.py::_leg_closure')",
      "name": "_check_leg",
      "name": "_check_replay",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-02/check_buzz_authz.py::_leg_closure')",
### ripwire callers
<callers of="_leg_closure" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=_leg_closure">

## symbol _require_real_dir
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 2,
    "processes_affected": 0,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/proofs/S0-02/check_buzz_authz.py::_require_real_dir')",
      "name": "_check_leg",
      "name": "_check_replay",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/proofs/S0-02/check_buzz_authz.py::_require_real_dir')",
### ripwire callers
<callers of="_require_real_dir" defs="1" count="2" root="/home/user/agent-factory" hop_tested="0" hop_untested="2" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=_require_real_dir">

## symbol test_evidence_root_replaced_by_a_symlink_is_refused
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_evidence_root_replaced_by_a_symlink_is_refused')",
  "summary": "Found 53 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_evidence_root_replaced_by_a_symlink_is_refused')",
      "name": "test_blanket_bundle_is_a_blanket_rejection",
      "name": "test_deferral_stops_once_any_leg_carries_a_timeline",
      "name": "test_removing_a_legs_observable_fails_that_leg",
      "name": "test_bad_signature_leg_delivering_a_VALID_event_fails",
      "name": "test_two_legs_with_swapped_observables_fail_the_named_check",
      "name": "test_a_buzz_acp_leg_showing_only_a_relay_reason_fails_the_named_check",
      "name": "test_wrong_channel_observables_are_rejected",
      "name": "test_a_leg_with_two_denial_observables_is_not_counted_as_a_distinct_reason",
      "name": "test_a_negative_leg_that_produced_a_turn_fails",
      "name": "test_a_positive_leg_with_two_turns_fails",
      "name": "test_a_positive_leg_with_no_turn_fails",
### ripwire callers
<callers of="test_evidence_root_replaced_by_a_symlink_is_refused" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_evidence_root_replaced_by_a_symlink_is_refused">

## symbol test_extra_regular_file_inside_a_leg_is_refused
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_extra_regular_file_inside_a_leg_is_refused')",
  "summary": "Found 53 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_extra_regular_file_inside_a_leg_is_refused')",
      "name": "test_blanket_bundle_is_a_blanket_rejection",
      "name": "test_deferral_stops_once_any_leg_carries_a_timeline",
      "name": "test_removing_a_legs_observable_fails_that_leg",
      "name": "test_bad_signature_leg_delivering_a_VALID_event_fails",
      "name": "test_two_legs_with_swapped_observables_fail_the_named_check",
      "name": "test_a_buzz_acp_leg_showing_only_a_relay_reason_fails_the_named_check",
      "name": "test_wrong_channel_observables_are_rejected",
      "name": "test_a_leg_with_two_denial_observables_is_not_counted_as_a_distinct_reason",
      "name": "test_a_negative_leg_that_produced_a_turn_fails",
      "name": "test_a_positive_leg_with_two_turns_fails",
      "name": "test_a_positive_leg_with_no_turn_fails",
### ripwire callers
<callers of="test_extra_regular_file_inside_a_leg_is_refused" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_extra_regular_file_inside_a_leg_is_refused">

## symbol test_leg_file_table_matches_the_runner_writes
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_leg_file_table_matches_the_runner_writes')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_leg_file_table_matches_the_runner_writes')",
### ripwire callers
<callers of="test_leg_file_table_matches_the_runner_writes" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_leg_file_table_matches_the_runner_writes">

## symbol test_leg_replaced_by_a_symlink_to_an_outside_copy_is_refused
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_leg_replaced_by_a_symlink_to_an_outside_copy_is_refused')",
  "summary": "Found 53 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_leg_replaced_by_a_symlink_to_an_outside_copy_is_refused')",
      "name": "test_all_timelines_removed_defers_and_never_passes",
      "name": "test_deferral_stops_once_any_leg_carries_a_timeline",
      "name": "test_removing_a_legs_observable_fails_that_leg",
      "name": "test_swapping_a_legs_observable_for_another_legs_fails",
      "name": "test_bad_signature_leg_delivering_a_VALID_event_fails",
      "name": "test_two_legs_with_swapped_observables_fail_the_named_check",
      "name": "test_a_buzz_acp_leg_showing_only_a_relay_reason_fails_the_named_check",
      "name": "test_wrong_channel_observables_are_rejected",
      "name": "test_a_leg_with_two_denial_observables_is_not_counted_as_a_distinct_reason",
      "name": "test_a_negative_leg_that_produced_a_turn_fails",
      "name": "test_a_positive_leg_with_two_turns_fails",
### ripwire callers
<callers of="test_leg_replaced_by_a_symlink_to_an_outside_copy_is_refused" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_leg_replaced_by_a_symlink_to_an_outside_copy_is_refused">

## symbol test_missing_required_file_inside_a_leg_is_named
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_missing_required_file_inside_a_leg_is_named')",
  "summary": "Found 53 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_missing_required_file_inside_a_leg_is_named')",
      "name": "test_all_timelines_removed_defers_and_never_passes",
      "name": "test_deferral_stops_once_any_leg_carries_a_timeline",
      "name": "test_removing_a_legs_observable_fails_that_leg",
      "name": "test_swapping_a_legs_observable_for_another_legs_fails",
      "name": "test_bad_signature_leg_delivering_a_VALID_event_fails",
      "name": "test_two_legs_with_swapped_observables_fail_the_named_check",
      "name": "test_a_buzz_acp_leg_showing_only_a_relay_reason_fails_the_named_check",
      "name": "test_wrong_channel_observables_are_rejected",
      "name": "test_a_leg_with_two_denial_observables_is_not_counted_as_a_distinct_reason",
      "name": "test_a_negative_leg_that_produced_a_turn_fails",
      "name": "test_a_positive_leg_with_two_turns_fails",
### ripwire callers
<callers of="test_missing_required_file_inside_a_leg_is_named" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_missing_required_file_inside_a_leg_is_named">

## symbol test_normalise_takes_accepted_only_when_upstream_is_bool
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_normalise_takes_accepted_only_when_upstream_is_bool')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_normalise_takes_accepted_only_when_upstream_is_bool')",
### ripwire callers
<callers of="test_normalise_takes_accepted_only_when_upstream_is_bool" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_normalise_takes_accepted_only_when_upstream_is_bool">

## symbol test_privkey_normalises_then_refuses_before_any_network_action
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_privkey_normalises_then_refuses_before_any_network_action')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_privkey_normalises_then_refuses_before_any_network_action')",
### ripwire callers
<callers of="test_privkey_normalises_then_refuses_before_any_network_action" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_privkey_normalises_then_refuses_before_any_network_action">

## symbol test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output')",
  "summary": "Found 8 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output')",
      "name": "test_pass_bundle_passes",
      "name": "test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output",
      "name": "test_all_timelines_removed_defers_and_never_passes",
      "name": "test_swapping_a_legs_observable_for_another_legs_fails",
      "name": "test_relay_decided_leg_needs_no_debug_canary",
      "name": "test_replay_with_two_different_event_ids_fails",
      "name": "test_replay_second_subleg_uses_only_the_wider_replay_tolerance",
      "name": "test_a_fifo_in_place_of_a_leg_file_is_named_not_read",
### ripwire callers
<callers of="test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output">

## symbol test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance')",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance')",
### ripwire callers
<callers of="test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance">

## symbol test_replay_leg_must_carry_exactly_the_two_subleg_directories
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_replay_leg_must_carry_exactly_the_two_subleg_directories')",
  "summary": "Found 53 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_replay_leg_must_carry_exactly_the_two_subleg_directories')",
      "name": "test_deferral_stops_once_any_leg_carries_a_timeline",
      "name": "test_removing_a_legs_observable_fails_that_leg",
      "name": "test_swapping_a_legs_observable_for_another_legs_fails",
      "name": "test_bad_signature_leg_delivering_a_VALID_event_fails",
      "name": "test_two_legs_with_swapped_observables_fail_the_named_check",
      "name": "test_a_buzz_acp_leg_showing_only_a_relay_reason_fails_the_named_check",
      "name": "test_wrong_channel_observables_are_rejected",
      "name": "test_a_leg_with_two_denial_observables_is_not_counted_as_a_distinct_reason",
      "name": "test_a_negative_leg_that_produced_a_turn_fails",
      "name": "test_a_positive_leg_with_two_turns_fails",
      "name": "test_a_positive_leg_with_no_turn_fails",
### ripwire callers
<callers of="test_replay_leg_must_carry_exactly_the_two_subleg_directories" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_replay_leg_must_carry_exactly_the_two_subleg_directories">

## symbol test_replay_subleg_replaced_by_a_symlink_is_refused
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_replay_subleg_replaced_by_a_symlink_is_refused')",
  "summary": "Found 53 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_replay_subleg_replaced_by_a_symlink_is_refused')",
      "name": "test_all_timelines_removed_defers_and_never_passes",
      "name": "test_deferral_stops_once_any_leg_carries_a_timeline",
      "name": "test_removing_a_legs_observable_fails_that_leg",
      "name": "test_swapping_a_legs_observable_for_another_legs_fails",
      "name": "test_bad_signature_leg_delivering_a_VALID_event_fails",
      "name": "test_two_legs_with_swapped_observables_fail_the_named_check",
      "name": "test_a_buzz_acp_leg_showing_only_a_relay_reason_fails_the_named_check",
      "name": "test_wrong_channel_observables_are_rejected",
      "name": "test_a_leg_with_two_denial_observables_is_not_counted_as_a_distinct_reason",
      "name": "test_a_negative_leg_that_produced_a_turn_fails",
      "name": "test_a_positive_leg_with_two_turns_fails",
### ripwire callers
<callers of="test_replay_subleg_replaced_by_a_symlink_is_refused" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_replay_subleg_replaced_by_a_symlink_is_refused">

## symbol test_wall_clock_freshness_scan_documented_limit_is_not_silently_widened
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 0 result(s) for callers_of('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_wall_clock_freshness_scan_documented_limit_is_not_silently_widened')",
  "summary": "Found 3 result(s) for tests_for('/home/user/agent-factory/tests/test_s0_02_buzz_authz.py::test_wall_clock_freshness_scan_documented_limit_is_not_silently_widened')",
      "name": "test_buzz_acp_has_no_wall_clock_freshness_rule_on_the_channel_event_path",
      "name": "test_wall_clock_freshness_scan_rejects_an_inline_rule",
      "name": "test_wall_clock_freshness_scan_documented_limit_is_not_silently_widened",
### ripwire callers
<callers of="test_wall_clock_freshness_scan_documented_limit_is_not_silently_widened" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="7" graph_unresolved="71" counts_floor="1" next="--uses=test_wall_clock_freshness_scan_documented_limit_is_not_silently_widened">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
