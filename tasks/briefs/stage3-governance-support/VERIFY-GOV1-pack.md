# lane context pack — 78f400d 2026-09-15T14:56Z
files: src/agent_factory/governance/pin.py src/agent_factory/governance/packet.py src/agent_factory/governance/projection.py src/agent_factory/governance/bounds.py src/agent_factory/audit/events.py
symbols: verify_pinned_fubuki lint_sources compile_canonical load_packet project write_projection read_projection bound_records JsonlSink

## src/agent_factory/governance/pin.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — src/agent_factory/governance/pin.py
- L13-L20  class GovernanceError  class GovernanceError(RuntimeError)
- L16-L20  method __init__  def __init__(self, reason: str, detail: str = "") -> None
- L24-L26  class PinnedFubuki  class PinnedFubuki
- L29-L43  function _git  def _git(root: Path, *args: str) -> str
- L46-L54  function _locked_commit  def _locked_commit(lock_path: Path) -> str
- L57-L80  function verify_pinned_fubuki  def verify_pinned_fubuki(root: str | Path, lock_path: str | Path) -> PinnedFubuki
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 1 hits over 1 files ---
AF-AP-37: 1
    src/agent_factory/governance/pin.py:76: # 12 tests green only through an ambient PYTHONPATH — the hidden-input hollow green).

## src/agent_factory/governance/packet.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — src/agent_factory/governance/packet.py
- L15-L17  class LintResult  class LintResult
- L21-L24  class Packet  class Packet
- L27-L34  function _correct_lint_exit  def _correct_lint_exit(findings: Iterable[tuple[str, str, str]]) -> int
- L37-L56  function _source_files  def _source_files(root: Path) -> tuple[Path, ...]
- L59-L78  function lint_sources  def lint_sources(root: str | Path) -> LintResult
- L81-L105  function _compile_request  def _compile_request(sources_root: Path, package_id: str) -> Any
- L108-L124  function compile_canonical  def compile_canonical(sources_root: str | Path) -> bytes
- L127-L131  function governance_hash  def governance_hash(canonical_bytes: bytes) -> str
- L134-L138  function _reviewed  def _reviewed(packet: dict[str, Any]) -> bool
- L141-L154  function load_packet  def load_packet(root: str | Path) -> Packet
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 9 hits over 1 files ---
AF-AP-40: 6
    src/agent_factory/governance/packet.py:38: if root.is_file():
    src/agent_factory/governance/packet.py:41: if manifest_path.is_file():
    src/agent_factory/governance/packet.py:52: if path.is_file() and not path.is_symlink()
    src/agent_factory/governance/packet.py:67: banned = load_banned(root if root.is_dir() else root.parent)
    src/agent_factory/governance/packet.py:75: label = source.name if root.is_file() else str(source.relative_to(root))
    src/agent_factory/governance/packet.py:85: if request_path.is_file():
AP-32: 3
    src/agent_factory/governance/packet.py:127: def governance_hash(canonical_bytes: bytes) -> str:
    src/agent_factory/governance/packet.py:131: return hashlib.sha256(canonical_bytes).hexdigest()
    src/agent_factory/governance/packet.py:154: return Packet(canonical=canonical, hash=governance_hash(canonical), reviewed=True)

## src/agent_factory/governance/projection.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — src/agent_factory/governance/projection.py
- L19-L22  class GovernanceProjection  class GovernanceProjection
- L25-L30  function _freeze  def _freeze(value: Any) -> Any
- L33-L57  function project  def project(packet: Packet) -> GovernanceProjection
- L60-L65  function _plain  def _plain(value: Any) -> Any
- L68-L83  function _document  def _document(projection: GovernanceProjection) -> bytes
- L86-L93  function _exclusive_flags  def _exclusive_flags() -> int
- L96-L112  function write_projection  def write_projection(projection: GovernanceProjection, path: str | Path) -> None
- L115-L130  function _read_regular  def _read_regular(path: Path) -> bytes
- L133-L152  function read_projection  def read_projection(path: str | Path, expected_hash: str) -> GovernanceProjection
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 3 hits over 1 files ---
AP-32: 3
    src/agent_factory/governance/projection.py:39: actual_hash = governance_hash(packet.canonical)
    src/agent_factory/governance/projection.py:79: "projection_hash": hashlib.sha256(body_bytes).hexdigest(),
    src/agent_factory/governance/projection.py:145: if not isinstance(projection_hash, str) or not hashlib.sha256(body_bytes).hexdigest() == projection_

## src/agent_factory/governance/bounds.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — src/agent_factory/governance/bounds.py
- L15-L18  class Denial  class Denial
- L22-L25  class BoundResult  class BoundResult
- L28-L31  function _rule  def _rule(reasons: tuple[str, ...]) -> str
- L34-L111  function bound_records  def bound_records( records: Iterable[Any], packet: Packet, *, branch: str = "main", active_person: str = "operator", third_party_visible: bool = False, request_tags: tuple[str, ...] = (), at: str = "", correlation_id: str = "governance-bounds", sink: JsonlSink | None = None, ) -> BoundResult
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## src/agent_factory/audit/events.py
### graft skeleton
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).

graft skeleton — src/agent_factory/audit/events.py
- L14-L20  class AuditError  class AuditError(RuntimeError)
- L17-L20  method __init__  def __init__(self, reason: str, detail: str = "") -> None
- L24-L52  class Event  class Event
- L32-L42  method __post_init__  def __post_init__(self) -> None
- L44-L52  method to_dict  def to_dict(self) -> dict[str, Any]
- L55-L88  class JsonlSink  class JsonlSink
- L56-L57  method __init__  def __init__(self, path: str | Path) -> None
- L59-L88  method append  def append(self, event: Event) -> None
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

## graft ask — Where can an unverified fubuki_os or lint module be imported before verify_pinned_fubuki runs, and where does a caller reach compile_canonical, bound_records, project or write_projection without holding a PinnedFubuki?
⬆ graft 0.16.0 → 0.18.0 available: run `npm i -g @nanonets/graft@latest` (restart your agent after).
graft ask — "Where can an unverified fubuki_os or lint module be imported before verify_pinned_fubuki runs, and where does a caller reach compile_canonical, bound_records, project or write_projection without holding a PinnedFubuki?"  (structural)

callers / references of verify_pinned_fubuki

- test_provisions_the_pin_and_the_negative_control_idempotently  tests/test_fubuki_pin_sync.py:L49-L70  (calls) — def test_provisions_the_pin_and_the_negative_control_idempotently(tmp_path: Path, source: Path) -> None
- pinned_fubuki  tests/test_governance_bounds.py:L18-L23  (calls) — def pinned_fubuki()
- pinned_fubuki  tests/test_governance_packet.py:L33-L42  (calls) — def pinned_fubuki()
- test_pinned_clean_checkout_passes_and_path_is_inserted_once  tests/test_governance_pin.py:L33-L44  (calls) — def test_pinned_clean_checkout_passes_and_path_is_inserted_once( fubuki_root: Path, ) -> None
- test_pinned_upstream_modules_resolve_from_the_pinned_checkout  tests/test_governance_pin.py:L47-L61  (calls) — def test_pinned_upstream_modules_resolve_from_the_pinned_checkout(fubuki_root: Path) -> None
- test_other_commit_refuses_by_name  tests/test_governance_pin.py:L64-L66  (calls) — def test_other_commit_refuses_by_name(other_fubuki_root: Path) -> None
- test_dirty_checkout_refuses_by_name  tests/test_governance_pin.py:L69-L74  (calls) — def test_dirty_checkout_refuses_by_name(tmp_path: Path, fubuki_root: Path) -> None
- test_missing_source_refuses_before_git  tests/test_governance_pin.py:L77-L79  (calls) — def test_missing_source_refuses_before_git(tmp_path: Path) -> None

## symbol verify_pinned_fubuki
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 9 result(s) for callers_of('/home/user/agent-factory/src/agent_factory/governance/pin.py::verify_pinned_fubuki')",
      "name": "test_provisions_the_pin_and_the_negative_control_idempotently",
      "name": "test_pinned_clean_checkout_passes_and_path_is_inserted_once",
      "name": "test_pinned_upstream_modules_resolve_from_the_pinned_checkout",
      "name": "test_other_commit_refuses_by_name",
      "name": "test_dirty_checkout_refuses_by_name",
      "name": "test_missing_source_refuses_before_git",
      "name": "test_invalid_lock_refuses",
      "name": "pinned_fubuki",
      "name": "pinned_fubuki",
  "summary": "Found 7 result(s) for tests_for('/home/user/agent-factory/src/agent_factory/governance/pin.py::verify_pinned_fubuki')",
      "name": "test_provisions_the_pin_and_the_negative_control_idempotently",
      "name": "test_pinned_clean_checkout_passes_and_path_is_inserted_once",
      "name": "test_pinned_upstream_modules_resolve_from_the_pinned_checkout",
      "name": "test_other_commit_refuses_by_name",
      "name": "test_dirty_checkout_refuses_by_name",
      "name": "test_missing_source_refuses_before_git",
      "name": "test_invalid_lock_refuses",
### ripwire callers
<callers of="verify_pinned_fubuki" defs="1" count="9" root="/home/user/agent-factory" hop_tested="0" hop_untested="9" shown="9" capped="0" total="9" has_more="0" next_offset="9" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="94" counts_floor="1" next="--uses=verify_pinned_fubuki">

## symbol lint_sources
### GitNexus impact (upstream)
  "impactedCount": 1,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/src/agent_factory/governance/packet.py::lint_sources')",
      "name": "load_packet",
      "name": "test_lint_exit_semantics",
  "summary": "Found 1 result(s) for tests_for('/home/user/agent-factory/src/agent_factory/governance/packet.py::lint_sources')",
      "name": "test_lint_exit_semantics",
### ripwire callers
<callers of="lint_sources" defs="1" count="2" root="/home/user/agent-factory" hop_tested="1" hop_untested="1" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="94" counts_floor="1" next="--uses=lint_sources">

## symbol compile_canonical
### GitNexus impact (upstream)
  "impactedCount": 1,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 3 result(s) for callers_of('/home/user/agent-factory/src/agent_factory/governance/packet.py::compile_canonical')",
      "name": "load_packet",
      "name": "test_compile_is_canonical_and_hash_is_exact_sha256",
      "name": "test_each_source_byte_changes_hash",
  "summary": "Found 2 result(s) for tests_for('/home/user/agent-factory/src/agent_factory/governance/packet.py::compile_canonical')",
      "name": "test_compile_is_canonical_and_hash_is_exact_sha256",
      "name": "test_each_source_byte_changes_hash",
### ripwire callers
<callers of="compile_canonical" defs="1" count="3" root="/home/user/agent-factory" hop_tested="1" hop_untested="2" shown="3" capped="0" total="3" has_more="0" next_offset="3" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="94" counts_floor="1" next="--uses=compile_canonical">

## symbol load_packet
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/src/agent_factory/governance/packet.py::load_packet')",
      "name": "test_unreviewed_compiled_packet_refuses_readiness",
  "summary": "Found 7 result(s) for tests_for('/home/user/agent-factory/src/agent_factory/governance/packet.py::load_packet')",
      "name": "test_unreviewed_compiled_packet_refuses_readiness",
      "name": "test_compile_is_canonical_and_hash_is_exact_sha256",
      "name": "test_each_source_byte_changes_hash",
      "name": "test_packet_is_frozen",
      "name": "test_projection_is_deeply_immutable_and_selective",
      "name": "test_project_refuses_mutated_packet_identity",
      "name": "test_lint_exit_semantics",
### ripwire callers
<callers of="load_packet" defs="1" count="1" root="/home/user/agent-factory" hop_tested="0" hop_untested="1" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="94" counts_floor="1" next="--uses=load_packet">

## symbol project
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
  "summary": "Found 6 result(s) for callers_of('/home/user/agent-factory/src/agent_factory/governance/projection.py::project')",
      "name": "test_projection_is_deeply_immutable_and_selective",
      "name": "test_projection_round_trip_and_tamper_detection",
      "name": "test_projection_refuses_hash_mismatch_and_existing_path",
      "name": "test_projection_refuses_symlink_before_write",
      "name": "test_projection_refuses_fifo_without_blocking",
      "name": "test_project_refuses_mutated_packet_identity",
  "summary": "Found 7 result(s) for tests_for('/home/user/agent-factory/src/agent_factory/governance/projection.py::project')",
      "name": "test_projection_is_deeply_immutable_and_selective",
      "name": "test_projection_round_trip_and_tamper_detection",
      "name": "test_projection_refuses_hash_mismatch_and_existing_path",
      "name": "test_projection_refuses_symlink_before_write",
      "name": "test_projection_refuses_fifo_without_blocking",
      "name": "test_project_refuses_mutated_packet_identity",
      "name": "test_projection_document_hash_covers_every_byte",
### ripwire callers
<callers of="project" defs="25" count="6" root="/home/user/agent-factory" hop_tested="0" hop_untested="6" shown="6" capped="0" total="6" has_more="0" next_offset="6" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="94" counts_floor="1" next="--uses=project">

## symbol write_projection
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 5 result(s) for callers_of('/home/user/agent-factory/src/agent_factory/governance/projection.py::write_projection')",
      "name": "test_projection_round_trip_and_tamper_detection",
      "name": "test_projection_refuses_hash_mismatch_and_existing_path",
      "name": "test_projection_refuses_symlink_before_write",
      "name": "test_projection_refuses_fifo_without_blocking",
      "name": "test_projection_document_hash_covers_every_byte",
  "summary": "Found 5 result(s) for tests_for('/home/user/agent-factory/src/agent_factory/governance/projection.py::write_projection')",
      "name": "test_projection_round_trip_and_tamper_detection",
      "name": "test_projection_refuses_hash_mismatch_and_existing_path",
      "name": "test_projection_refuses_symlink_before_write",
      "name": "test_projection_refuses_fifo_without_blocking",
      "name": "test_projection_document_hash_covers_every_byte",
### ripwire callers
<callers of="write_projection" defs="1" count="5" root="/home/user/agent-factory" hop_tested="0" hop_untested="5" shown="5" capped="0" total="5" has_more="0" next_offset="5" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="94" counts_floor="1" next="--uses=write_projection">

## symbol read_projection
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 4 result(s) for callers_of('/home/user/agent-factory/src/agent_factory/governance/projection.py::read_projection')",
      "name": "test_projection_round_trip_and_tamper_detection",
      "name": "test_projection_refuses_hash_mismatch_and_existing_path",
      "name": "test_projection_refuses_fifo_without_blocking",
      "name": "test_projection_document_hash_covers_every_byte",
  "summary": "Found 4 result(s) for tests_for('/home/user/agent-factory/src/agent_factory/governance/projection.py::read_projection')",
      "name": "test_projection_round_trip_and_tamper_detection",
      "name": "test_projection_refuses_hash_mismatch_and_existing_path",
      "name": "test_projection_refuses_fifo_without_blocking",
      "name": "test_projection_document_hash_covers_every_byte",
### ripwire callers
<callers of="read_projection" defs="1" count="4" root="/home/user/agent-factory" hop_tested="0" hop_untested="4" shown="4" capped="0" total="4" has_more="0" next_offset="4" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="94" counts_floor="1" next="--uses=read_projection">

## symbol bound_records
### GitNexus impact (upstream)
  "impactedCount": 0,
  "risk": "UNKNOWN",
  "riskNote": "No callers resolved. Absence of edges is not evidence the symbol is unused: a caller reaching it through a reference class this index does not record — plain-object property access, a bare-identifier read of a module-scope const — produces no edge to find. Confirm with a text search before treating the change as safe.",
  "epistemic": "exact",
    "direct": 0,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 4 result(s) for callers_of('/home/user/agent-factory/src/agent_factory/governance/bounds.py::bound_records')",
      "name": "test_bound_join_keeps_source_identity_and_denial_reason",
      "name": "test_bound_join_never_reads_planted_decision_payload",
      "name": "test_bound_join_refuses_decision_without_source",
      "name": "test_bound_join_refuses_duplicate_source_id",
  "summary": "Found 7 result(s) for tests_for('/home/user/agent-factory/src/agent_factory/governance/bounds.py::bound_records')",
      "name": "test_bound_join_keeps_source_identity_and_denial_reason",
      "name": "test_bound_join_never_reads_planted_decision_payload",
      "name": "test_bound_join_refuses_decision_without_source",
      "name": "test_bound_join_refuses_duplicate_source_id",
      "name": "test_jsonl_sink_round_trips_and_appends",
      "name": "test_jsonl_sink_refuses_symlink",
      "name": "test_jsonl_sink_refuses_fifo_without_blocking",
### ripwire callers
<callers of="bound_records" defs="1" count="4" root="/home/user/agent-factory" hop_tested="0" hop_untested="4" shown="4" capped="0" total="4" has_more="0" next_offset="4" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="94" counts_floor="1" next="--uses=bound_records">

## symbol JsonlSink
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 2,
    "processes_affected": 0,
### code-review-graph callers_of / tests_for
  "summary": "Found 3 result(s) for callers_of('/home/user/agent-factory/src/agent_factory/audit/events.py::JsonlSink')",
      "name": "test_jsonl_sink_round_trips_and_appends",
      "name": "test_jsonl_sink_refuses_symlink",
      "name": "test_jsonl_sink_refuses_fifo_without_blocking",
  "summary": "Found 3 result(s) for tests_for('/home/user/agent-factory/src/agent_factory/audit/events.py::JsonlSink')",
      "name": "test_jsonl_sink_round_trips_and_appends",
      "name": "test_jsonl_sink_refuses_symlink",
      "name": "test_jsonl_sink_refuses_fifo_without_blocking",
### ripwire callers
<callers of="JsonlSink" defs="1" count="3" root="/home/user/agent-factory" hop_tested="0" hop_untested="3" shown="3" capped="0" total="3" has_more="0" next_offset="3" offset="0" limit="20" graph_ambiguous="11" graph_unresolved="94" counts_floor="1" next="--uses=JsonlSink">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
