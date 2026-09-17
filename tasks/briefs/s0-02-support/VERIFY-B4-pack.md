# lane context pack — 826f14a 2026-09-17T13:51Z
files: proofs/S0-02/check_buzz_authz.py tests/test_s0_02_buzz_authz.py
symbols: _LEG_FILES_PLAIN REPLAY_CLOCK_TOLERANCE_S removal_note

## proofs/S0-02/check_buzz_authz.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

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
- L651-L722  function _check_bundle_uncapped  def _check_bundle_uncapped(root: Path, anchors: "Anchors") -> str: # The root itself must be a real directory, not a symlink: resolve() would # happily re-anchor every later containment check under the symlink target.
- L725-L728  function check_bundle  def check_bundle(root: Path, anchors: "Anchors | None" = None) -> str
- L731-L758  function main  def main(argv) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## tests/test_s0_02_buzz_authz.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

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
- L691-L698  function test_missing_revoked_leg_fails_before_the_removal_summary  def test_missing_revoked_leg_fails_before_the_removal_summary(tmp_path)
- L701-L714  function test_removal_summary_uses_only_the_revoked_leg_note  def test_removal_summary_uses_only_the_revoked_leg_note(tmp_path, monkeypatch)
- L706-L710  function drop_revoked_note  def drop_revoked_note(leg_dir, leg, fixture_name, identities, anchors)
- L717-L725  function test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output  def test_removal_receipt_is_labelled_coordinator_supplied_in_checker_output()
- L728-L736  function test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance  def test_removal_receipt_label_is_pinned_in_spec_and_fixture_provenance()
- L739-L742  function test_blanket_bundle_is_a_blanket_rejection  def test_blanket_bundle_is_a_blanket_rejection()
- L745-L756  function test_spec_negative_leg_reason_is_the_exact_observed_line  def test_spec_negative_leg_reason_is_the_exact_observed_line()
- L759-L763  function test_spec_validates_against_the_repo_schema  def test_spec_validates_against_the_repo_schema()
- L766-L773  function test_spec_positive_leg_points_at_the_real_evidence_root  def test_spec_positive_leg_points_at_the_real_evidence_root()
- L776-L781  function test_deferred_when_the_evidence_root_is_absent  def test_deferred_when_the_evidence_root_is_absent(tmp_path)
- L784-L789  function test_real_evidence_root_defers_today  def test_real_evidence_root_defers_today()
- L792-L804  function test_all_timelines_removed_defers_and_never_passes  def test_all_timelines_removed_defers_and_never_passes(tmp_path)
- L807-L813  function test_deferral_stops_once_any_leg_carries_a_timeline  def test_deferral_stops_once_any_leg_carries_a_timeline(tmp_path)
- L820-L832  function test_removing_a_legs_observable_fails_that_leg  def test_removing_a_legs_observable_fails_that_leg(tmp_path, name)
- L836-L853  function test_swapping_a_legs_observable_for_another_legs_fails  def test_swapping_a_legs_observable_for_another_legs_fails(tmp_path, name)
- L856-L871  function test_bad_signature_leg_delivering_a_VALID_event_fails  def test_bad_signature_leg_delivering_a_VALID_event_fails(tmp_path)
- L874-L893  function test_two_legs_with_swapped_observables_fail_the_named_check  def test_two_legs_with_swapped_observables_fail_the_named_check(tmp_path)
- L896-L908  function test_a_buzz_acp_leg_showing_only_a_relay_reason_fails_the_named_check  def test_a_buzz_acp_leg_showing_only_a_relay_reason_fails_the_named_check(tmp_path)
- L911-L926  function test_wrong_channel_observables_are_rejected  def test_wrong_channel_observables_are_rejected(tmp_path)
- L929-L937  function test_a_leg_with_two_denial_observables_is_not_counted_as_a_distinct_reason  def test_a_leg_with_two_denial_observables_is_not_counted_as_a_distinct_reason(tmp_path)
- L940-L945  function test_a_negative_leg_that_produced_a_turn_fails  def test_a_negative_leg_that_produced_a_turn_fails(tmp_path)
- L948-L956  function test_a_positive_leg_with_two_turns_fails  def test_a_positive_leg_with_two_turns_fails(tmp_path)
- L959-L963  function test_a_positive_leg_with_no_turn_fails  def test_a_positive_leg_with_no_turn_fails(tmp_path)
- L966-L971  function test_a_positive_turn_without_the_fixture_nonce_fails  def test_a_positive_turn_without_the_fixture_nonce_fails(tmp_path)
- L974-L980  function test_positive_nonce_must_be_a_complete_json_token  def test_positive_nonce_must_be_a_complete_json_token()
- L983-L989  function test_a_missing_debug_canary_fails_a_buzz_acp_leg  def test_a_missing_debug_canary_fails_a_buzz_acp_leg(tmp_path)
- L992-L996  function test_an_info_level_canary_does_not_prove_debug_capture  def test_an_info_level_canary_does_not_prove_debug_capture(tmp_path)
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 11 hits over 1 files ---
AF-AP-80: 7
    tests/test_s0_02_buzz_authz.py:697: assert "removal_line = removal_note\n" in source
    tests/test_s0_02_buzz_authz.py:698: assert "removal_line = removal_note or" not in source
    tests/test_s0_02_buzz_authz.py:1003: assert checker.DEBUG_LEVEL_CANARY not in real_log.read_text()
    tests/test_s0_02_buzz_authz.py:1503: assert "_load_timeline_raw = s0_01._load_timeline_raw" in src
    tests/test_s0_02_buzz_authz.py:1504: assert "_require_file = s0_01._require_file" in src
    tests/test_s0_02_buzz_authz.py:1536: assert "_load_timeline_raw(leg_dir, leg)" in src
    ... +1
AF-AP-34: 4
    tests/test_s0_02_buzz_authz.py:1567: """AF-AP-34: no pkill/killall/name match anywhere in the PC runner."""
    tests/test_s0_02_buzz_authz.py:1567: """AF-AP-34: no pkill/killall/name match anywhere in the PC runner."""
    tests/test_s0_02_buzz_authz.py:1571: for word in ("pkill", "killall", "pgrep"):
    tests/test_s0_02_buzz_authz.py:1571: for word in ("pkill", "killall", "pgrep"):

## graft ask — how does the S0-02 closure test enumerate every runner write, how is the replay tolerance relation pinned, and where was the removal-receipt fallback
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
graft ask — "how does the S0-02 closure test enumerate every runner write, how is the replay tolerance relation pinned, and where was the removal-receipt fallback"  (lexical)

1. check_buzz_authz.py · file  [symbol]
   proofs/S0-02/check_buzz_authz.py

2. _write_leg · function  [symbol]
   proofs/S0-02/tools/build_fixtures.py:L364-L401
   def _write_leg(leg_dir: Path, fixture: dict, ids: dict, bundle: str, *, accepted: bool, message: str, with_turn: bool, log_extra, membership: dict | None = None)

3. main · function  [symbol]
   proofs/S0-02/tools/pc/deliver_event.py:L165-L217
   def main(argv) -> int

4. denial_table.py · file  [symbol]
   proofs/S0-02/oracle/denial_table.py

5. _check_leg · function  [symbol]
   proofs/S0-02/check_buzz_authz.py:L457-L558
   def _check_leg(leg_dir: Path, leg: str, fixture_name: str, identities: dict, anchors: "Anchors")

6. build_one · function  [symbol]
   proofs/S0-02/tools/build_fixtures.py:L188-L252
   def build_one(spec: dict, ids: dict, built: dict) -> dict

7. _normalise · function  [symbol]
   proofs/S0-02/tools/pc/deliver_event.py:L118-L162
   def _normalise(status: int, raw: str, event_id: str) -> dict

8. observable_key · function  [symbol]
   proofs/S0-02/oracle/denial_table.py:L282-L288
   def observable_key(fixture: str) -> str

## symbol _LEG_FILES_PLAIN
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "No node found matching '_LEG_FILES_PLAIN'.",
  "summary": "No node found matching '_LEG_FILES_PLAIN'.",
### ripwire callers
<callers of="_LEG_FILES_PLAIN" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=_LEG_FILES_PLAIN">

## symbol REPLAY_CLOCK_TOLERANCE_S
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "No node found matching 'REPLAY_CLOCK_TOLERANCE_S'.",
  "summary": "No node found matching 'REPLAY_CLOCK_TOLERANCE_S'.",
### ripwire callers
<callers of="REPLAY_CLOCK_TOLERANCE_S" defs="1" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="108" graph_unresolved="109" counts_floor="1" next="--uses=REPLAY_CLOCK_TOLERANCE_S">

## symbol removal_note
### GitNexus impact (upstream)
### code-review-graph callers_of / tests_for
  "summary": "No node found matching 'removal_note'.",
  "summary": "No node found matching 'removal_note'.",
### ripwire callers

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
