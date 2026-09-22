# lane context pack — b7d14aa 2026-09-22T12:34Z
files: scripts/vendored_manifest.py tests/test_vendored_manifest.py
symbols: walk_tree build_records render validate_declared_roots parse_provenance main

## scripts/vendored_manifest.py
### graft skeleton

graft skeleton — scripts/vendored_manifest.py
- L25-L31  class VendoredRoot  class VendoredRoot(NamedTuple)
- L96-L97  class ManifestError  class ManifestError(RuntimeError)
- L100-L110  class TreeRecord  class TreeRecord(NamedTuple)
- L113-L114  function sha256_bytes  def sha256_bytes(data: bytes) -> str
- L117-L120  function normalize_repo  def normalize_repo(value: str) -> str
- L123-L126  function excluded  def excluded(relative: PurePosixPath) -> bool
- L129-L158  function walk_tree  def walk_tree(root: Path, repo_root: Path | None) -> list[tuple[str, bytes]]
- L161-L174  function repo_root_of  def repo_root_of(root: Path) -> Path | None
- L177-L202  function symlink_record  def symlink_record(root: Path, path: Path, repo_root: Path | None) -> tuple[str, bytes]
- L205-L212  function digest_records  def digest_records(records: Iterable[tuple[str, bytes]]) -> str
- L215-L231  function detect_spdx  def detect_spdx(text: str) -> str
- L234-L253  function license_for  def license_for(root: Path, records: list[tuple[str, bytes]]) -> tuple[str, str | None, str | None]
- L256-L257  function markdown_cells  def markdown_cells(line: str) -> list[str]
- L260-L261  function clean_code  def clean_code(cell: str) -> str
- L264-L339  function parse_provenance  def parse_provenance(path: Path) -> tuple[set[str], dict[str, int]]
- L342-L360  function validate_declared_roots  def validate_declared_roots(root: Path) -> None
- L363-L393  function parse_lock  def parse_lock(path: Path) -> dict[str, tuple[str, str]]
- L396-L420  function parse_sbom  def parse_sbom(path: Path) -> dict[str, tuple[str, str]]
- L402-L406  function finish  def finish() -> None
- L423-L448  function validate_pin_agreement  def validate_pin_agreement(root: Path) -> None
- L451-L462  function git_revision  def git_revision(root: Path) -> str
- L465-L486  function build_records  def build_records(root: Path, repo_root: Path | None) -> list[TreeRecord]
- L489-L490  function escape_cell  def escape_cell(value: str) -> str
- L493-L503  function generated_at_utc  def generated_at_utc() -> str
- L506-L552  function render  def render(root: Path, revision: str | None = None) -> str
- L555-L570  function normalize_generated_time  def normalize_generated_time(text: str) -> str
- L573-L582  function first_difference  def first_difference(expected: str, actual: str) -> str
- L585-L633  function main  def main(argv: list[str] | None = None) -> int
### anti-pattern screen (whole file)
--- AP_SCREEN over 1 path(s): 4 hits over 1 files ---
AP-32: 2
    scripts/vendored_manifest.py:114: return hashlib.sha256(data).hexdigest()
    scripts/vendored_manifest.py:206: digest = hashlib.sha256()
AF-AP-40: 1
    scripts/vendored_manifest.py:155: elif path.is_file():
AP-1: 1
    scripts/vendored_manifest.py:494: source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")

## tests/test_vendored_manifest.py
### graft skeleton

graft skeleton — tests/test_vendored_manifest.py
- L18-L24  function load_module  def load_module(path: Path = SCRIPT)
- L27-L61  function copy_fixture  def copy_fixture(tmp_path: Path, module=None) -> Path
- L64-L67  function write_module_source  def write_module_source(root: Path, module) -> None
- L70-L78  function run_tool  def run_tool(root: Path, mode: str = "--check") -> subprocess.CompletedProcess[str]
- L81-L84  function manifest_row  def manifest_row(text: str, path: str) -> str
- L87-L118  function test_real_link_passes_and_changes_digest_when_target_string_changes  def test_real_link_passes_and_changes_digest_when_target_string_changes(tmp_path: Path) -> None: # AMENDMENT 2(a): the ONE real link passes. Its target STRING (not target # contents) is digest input, proved by changing only that string to another # in-repo path and observing the codebase-memory row's tree digest change.
- L121-L125  function test_committed_manifest_matches_fresh_generation  def test_committed_manifest_matches_fresh_generation(tmp_path: Path) -> None
- L128-L140  function test_two_write_runs_are_byte_identical  def test_two_write_runs_are_byte_identical(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None
- L143-L165  function test_generation_time_is_only_normalized_drift_line  def test_generation_time_is_only_normalized_drift_line( tmp_path: Path, monkeypatch: pytest.MonkeyPatch ) -> None
- L168-L177  function test_invalid_source_date_epoch_is_named  def test_invalid_source_date_epoch_is_named( tmp_path: Path, monkeypatch: pytest.MonkeyPatch ) -> None
- L180-L207  function test_committed_manifest_passes_check_at_a_later_head  def test_committed_manifest_passes_check_at_a_later_head(tmp_path: Path) -> None
- L210-L221  function test_changed_vendored_byte_names_root_and_returns_one  def test_changed_vendored_byte_names_root_and_returns_one(tmp_path: Path) -> None
- L224-L245  function test_provenance_root_missing_from_declared_list_is_named  def test_provenance_root_missing_from_declared_list_is_named(tmp_path: Path) -> None
- L248-L261  function test_escaping_symlink_is_refused_by_name  def test_escaping_symlink_is_refused_by_name(tmp_path: Path) -> None: # AMENDMENT 2(b): an absolute link to /etc/hostname is outside the fixture # repository root and is refused with the link and target named.
- L264-L275  function test_dangling_symlink_is_refused_by_name  def test_dangling_symlink_is_refused_by_name(tmp_path: Path) -> None: # AMENDMENT 2(c): a dangling link inside a vendored root is refused by name.
- L278-L294  function test_cross_root_link_inside_repository_is_allowed_and_digested  def test_cross_root_link_inside_repository_is_allowed_and_digested(tmp_path: Path) -> None: # AMENDMENT 2(d): .claude/x crosses roots into .agents/skills but stays # inside the repository. It is allowed; changing only its TARGET STRING to a # second path that resolves to the same directory changes .claude's digest.
- L297-L305  function test_missing_repository_root_refuses_symlink  def test_missing_repository_root_refuses_symlink(tmp_path: Path) -> None
- L308-L326  function test_moving_real_link_target_outside_repo_flips_to_refused  def test_moving_real_link_target_outside_repo_flips_to_refused(tmp_path: Path) -> None: # AMENDMENT 2(e): moving the real Formula link target outside the repository # flips its disposition from allowed to refused. The outside target exists, # so this proves containment, not the dangling guard.
- L329-L350  function test_license_detection_reports_spdx_and_sha_or_none  def test_license_detection_reports_spdx_and_sha_or_none(tmp_path: Path) -> None
- L354-L367  function test_walk_is_sorted_before_digest  def test_walk_is_sorted_before_digest(tmp_path: Path) -> None
- L370-L387  function test_exclusions_do_not_affect_tree_record  def test_exclusions_do_not_affect_tree_record(tmp_path: Path) -> None
- L390-L413  function test_sbom_pin_disagreement_is_named  def test_sbom_pin_disagreement_is_named(tmp_path: Path) -> None
- L416-L455  function test_manifest_root_matching_lock_must_use_lock_pin  def test_manifest_root_matching_lock_must_use_lock_pin(tmp_path: Path) -> None
- L496-L568  function test_required_mutants_are_killed  def test_required_mutants_are_killed( tmp_path: Path, mutant_name: str, mutate, killer: str, ) -> None
### anti-pattern screen (whole file)
--- TEST_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-66: 1
    tests/test_vendored_manifest.py:228: setattr(

## graft ask — how does the vendored manifest walk declared roots, classify entries and check drift; where would a declared-root type check, a closed sandbox-kit entry table and a per-file .claude classification against a committed index go
graft ask — "how does the vendored manifest walk declared roots, classify entries and check drift; where would a declared-root type check, a closed sandbox-kit entry table and a per-file .claude classification against a committed index go"  (lexical)

1. vendored_manifest.py · file  [symbol]
   scripts/vendored_manifest.py

2. check-proof-status.py · file  [symbol]
   scripts/check-proof-status.py

3. lint_delta.py · file  [symbol]
   scripts/lint_delta.py

4. ap_screen.py · file  [symbol]
   scripts/ap_screen.py

5. main · function  [symbol]
   scripts/transcript_export.py:L87-L102
   def main() -> int

6. ooo_mcp.py · file  [symbol]
   scripts/ooo_mcp.py

7. _read_file · function  [symbol]
   scripts/report_lint.py:L50-L59
   def _read_file(path: str, rev: str | None, root: Path) -> list[str] | None

8. anchor_edit.py · file  [symbol]
   scripts/anchor_edit.py

## symbol walk_tree
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 6 result(s) for callers_of('/home/user/agent-factory/scripts/vendored_manifest.py::walk_tree')",
      "name": "build_records",
      "name": "test_missing_repository_root_refuses_symlink",
      "name": "test_license_detection_reports_spdx_and_sha_or_none",
      "name": "test_walk_is_sorted_before_digest",
      "name": "test_exclusions_do_not_affect_tree_record",
      "name": "test_required_mutants_are_killed",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/scripts/vendored_manifest.py::walk_tree')",
### ripwire callers
<callers of="walk_tree" defs="1" count="6" root="/home/user/agent-factory" hop_tested="1" hop_untested="5" shown="6" capped="0" total="6" has_more="0" next_offset="6" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="106" counts_floor="1" next="--uses=walk_tree">

## symbol build_records
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 2 result(s) for callers_of('/home/user/agent-factory/scripts/vendored_manifest.py::build_records')",
      "name": "render",
      "name": "test_real_link_passes_and_changes_digest_when_target_string_changes",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/scripts/vendored_manifest.py::build_records')",
### ripwire callers
<callers of="build_records" defs="1" count="2" root="/home/user/agent-factory" hop_tested="1" hop_untested="1" shown="2" capped="0" total="2" has_more="0" next_offset="2" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="106" counts_floor="1" next="--uses=build_records">

## symbol render
### GitNexus impact (upstream)
  "impactedCount": null,
  "risk": "UNKNOWN",
      "impactedCount": 2,
      "risk": "LOW",
      "direct": 1
      "impactedCount": 2,
      "risk": "LOW",
      "direct": 1
### code-review-graph callers_of / tests_for
  "summary": "Found 12 result(s) for callers_of('/home/user/agent-factory/scripts/vendored_manifest.py::render')",
      "name": "main",
      "name": "render_chart_to_file",
      "name": "render_chart_to_file",
      "name": "visualize_tree",
      "name": "visualize_tree",
      "name": "render_chart_to_file",
      "name": "render_chart_to_file",
      "name": "visualize_tree",
      "name": "visualize_tree",
      "name": "test_real_link_passes_and_changes_digest_when_target_string_changes",
      "name": "test_cross_root_link_inside_repository_is_allowed_and_digested",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/scripts/vendored_manifest.py::render')",
### ripwire callers
<callers of="render" defs="1" count="4" root="/home/user/agent-factory" hop_tested="0" hop_untested="4" shown="4" capped="0" total="4" has_more="0" next_offset="4" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="106" counts_floor="1" next="--uses=render">

## symbol validate_declared_roots
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/scripts/vendored_manifest.py::validate_declared_roots')",
      "name": "render",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/scripts/vendored_manifest.py::validate_declared_roots')",
### ripwire callers
<callers of="validate_declared_roots" defs="1" count="1" root="/home/user/agent-factory" hop_tested="1" hop_untested="0" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="106" counts_floor="1" next="--uses=validate_declared_roots">

## symbol parse_provenance
### GitNexus impact (upstream)
  "impactedCount": 3,
  "risk": "LOW",
  "epistemic": "exact",
    "direct": 1,
    "processes_affected": 1,
      "impact": "direct"
### code-review-graph callers_of / tests_for
  "summary": "Found 1 result(s) for callers_of('/home/user/agent-factory/scripts/vendored_manifest.py::parse_provenance')",
      "name": "validate_declared_roots",
  "summary": "Found 0 result(s) for tests_for('/home/user/agent-factory/scripts/vendored_manifest.py::parse_provenance')",
### ripwire callers
<callers of="parse_provenance" defs="1" count="1" root="/home/user/agent-factory" hop_tested="1" hop_untested="0" shown="1" capped="0" total="1" has_more="0" next_offset="1" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="106" counts_floor="1" next="--uses=parse_provenance">

## symbol main
### GitNexus impact (upstream)
  "impactedCount": null,
  "risk": "UNKNOWN",
      "impactedCount": 2,
      "risk": "LOW",
      "direct": 1
      "impactedCount": 2,
      "risk": "LOW",
      "direct": 1
### code-review-graph callers_of / tests_for
  "summary": "Found 32 result(s) for callers_of('/home/user/agent-factory/scripts/vendored_manifest.py::main')",
      "name": "/home/user/agent-factory/scripts/vendored_manifest.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-logic-visualizer/tests/test_visualizer.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-news/tests/test_news.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-predictor/tests/test_predictor.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-reporter/tests/test_reporter.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-search/tests/test_search.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-sentiment/tests/test_sentiment.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-signal-tracker/tests/test_tracker.py",
      "name": "/home/user/agent-factory/.agents/skills/alphaear-stock/tests/test_stock.py",
      "name": "test_output_file_written",
      "name": "/home/user/agent-factory/.agents/skills/exa-search/tests/test_exa_search.py",
  "summary": "Found 1 result(s) for tests_for('/home/user/agent-factory/scripts/vendored_manifest.py::main')",
      "name": "/home/user/agent-factory/sandbox-kit/codebase-memory-mcp/tests/test_main.c",
### ripwire callers
<callers of="main" defs="54" count="0" root="/home/user/agent-factory" hop_tested="0" hop_untested="0" shown="0" capped="0" total="0" has_more="0" next_offset="0" offset="0" limit="20" graph_ambiguous="110" graph_unresolved="106" counts_floor="1" next="--uses=main">

## ripwire test-gate — tests to run + the UNTESTED blast radius (a zero is 'none found', never 'none exists')
<test-gate changed="1" impacted="0" tests="0" untested="0" shown_tests="0" tests_capped="0" shown_untested="0" untested_capped="0" script_gates_unmodelled="10" script_gates_registered="0" script_gates_mapped="0" script_gates_unresolved_dynamic="0" ccx_bar="15" counts_floor="1" total="0" has_more="0" next_offset="0" offset="0" limit="20" at="b7d14aa46+dirty" next="--situ">
