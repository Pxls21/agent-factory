"""K170 (task #170): the lock, SBOM and provenance parsers of `scripts/vendored_manifest.py`
fail closed (D-1 through D-3, R1 through R8; bug-echo 2026-09-23, AF-AP-25).

Written FIRST and run RED on the PIN's line parsers before the fix (K170-report.md, item 3).

Every test mutates a SCRATCH copy of the real repository file (built in code; every
separator character via `chr()`, never typed). Each asserts the EXACT outcome: either the
returned map equal to the real file's map (the values pinned at the PIN 9e6821b below),
or a `ManifestError` whose message names the stated key or line.

Row map (the brief's table, extended with the rows the brief's mutations cannot express):
  L1-L9  lock        L7 is a regression row (PyYAML 1.1 reads `1e10` as a string, so the
                     old parser already returns the real map there); L7b is the dedicated
                     R5 non-string-pin test (a real YAML int, `12345`)
  S1-S6  SBOM        S4 replaces the whole hermes item with one flow mapping (the brief's
                     own snippet has a doubled closing brace, a YAML syntax error, and
                     leaves the item's `license`/`role` lines dangling); S6 is the
                     dedicated R5 non-string-pin test
  P1     provenance  a non-blank table-internal line that does not start with `|` is
                     refused, naming its line (R8); the table's 9 data rows are lines
                     11-19, the walk ends at the blank line 20 (R0)
  X1-X5  R1/R3/R4/R7 separators and shape refusals, plus X4b (a top-level scalar is
                     ignored, the R3 regression row); X4's appended `k170_probe: [a, b]`
                     is VALID YAML (the R3 section-not-a-mapping refusal fires), while the
                     brief's literal mid-file `selected_core: [a, b]` is a ParserError at
                     line 46 (the R2 class)
  R0     the three real files unchanged: the two D-3 digests and 9 provenance roots

The module under test is loaded fresh under a UNIQUE name with no `sys.modules` caching,
so every test re-reads the file on disk (a module cached under one name would otherwise
be served again by later reloads under a different name).
"""
from __future__ import annotations

import importlib.util
import sys
from hashlib import sha256
from json import dumps
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "vendored_manifest.py"

# Separator characters, built in code (R1): U+0085, U+2028, U+2029, carriage return.
NL = chr(0x0085)
LS = chr(0x2028)
PS = chr(0x2029)
CR = chr(0x000D)

LOCK_TEXT = (REPO / "upstream.lock.yaml").read_bytes().decode("utf-8")
SBOM_TEXT = (REPO / "SBOM.yaml").read_bytes().decode("utf-8")
PROV_TEXT = (REPO / "sandbox-kit/VENDORED-FROM.md").read_bytes().decode("utf-8")

HERMESL = "github.com/nousresearch/hermes-agent"
HERMES_COMMIT = "527da60844d4dced37879ea50259675371abe10e"
HERMES_SBOM_BLOCK = (
    "  - name: hermes-agent\n"
    "    repository: https://github.com/NousResearch/hermes-agent.git\n"
    f"    commit: {HERMES_COMMIT}\n"
    "    license: MIT\n"
    "    role: main_production_workhorse_and_native_acp_server\n"
)


_MODULE_COUNTER = 0


def load_module() -> type:
    """A fresh import of the script under test, under a unique name, never re-served from
    `sys.modules` (a name cached under one name would otherwise be returned again by a
    later reload under a different name)."""
    global _MODULE_COUNTER
    _MODULE_COUNTER += 1
    name = f"vendored_manifest_under_test_k170_{_MODULE_COUNTER}"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _fresh_module() -> type:
    return load_module()


def _digest(mapping: dict) -> str:
    """D-3: first 16 hex characters of the sha256 of `json.dumps(sorted(mapping.items()))`."""
    return sha256(dumps(sorted(mapping.items())).encode()).hexdigest()[:16]


def _write(tmp_path: Path, name: str, text: str) -> Path:
    path = tmp_path / name
    path.write_bytes(text.encode("utf-8"))
    return path


def _mutate_once(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)


# --- R0: the real files, unmutated (the D-3 digests and the 9 provenance roots) ---


def test_R0_real_files_unchanged(tmp_path: Path) -> None:
    module = _fresh_module()
    lock = module.parse_lock(REPO / "upstream.lock.yaml")
    assert len(lock) == 24, f"24 expected (D-3), got {len(lock)}"
    assert _digest(lock) == "f3b81f34ac1966c3"
    sbom = module.parse_sbom(REPO / "SBOM.yaml")
    assert len(sbom) == 22, f"22 expected (D-3), got {len(sbom)}"
    assert _digest(sbom) == "734a79b525e59e2f"
    _, roots = module.parse_provenance(REPO / "sandbox-kit/VENDORED-FROM.md")
    assert len(roots) == 9, f"9 roots expected (R0), got {len(roots)}"


# --- L rows: the lock ---


def test_L1_lock_trailing_space_on_component_line(tmp_path: Path) -> None:
    """A trailing space on `  hermes-agent:`: the old parser dropped the following
    agent-client-protocol pin and re-labelled hermes as agent-client-protocol."""
    module = _fresh_module()
    text = _mutate_once(LOCK_TEXT, "\n  hermes-agent:\n", "\n  hermes-agent: \n")
    lock = module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))
    real = module.parse_lock(REPO / "upstream.lock.yaml")
    assert lock == real, "the real map (24 entries) is required"


def test_L2_lock_trailing_comment_on_component_line(tmp_path: Path) -> None:
    module = _fresh_module()
    text = _mutate_once(LOCK_TEXT, "\n  hermes-agent:\n", "\n  hermes-agent:  # note\n")
    lock = module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))
    assert lock == module.parse_lock(REPO / "upstream.lock.yaml")


def test_L3_lock_three_space_indent(tmp_path: Path) -> None:
    """A three-space indent is a YAML syntax error: refused, naming the lock and line 10."""
    module = _fresh_module()
    text = _mutate_once(LOCK_TEXT, "\n  hermes-agent:\n", "\n   hermes-agent:\n")
    with pytest.raises(module.ManifestError, match="upstream lock parse failure at line 10"):
        module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))


def test_L4_lock_duplicate_component(tmp_path: Path) -> None:
    """A second `hermes-agent:` component: the old parser let its pin (40 zeros) replace
    hermes's. D-1/D-2: the safe loader refuses the duplicate key, naming it and the
    second key's line (line 45: the insertion point, immediately before
    `selected_later_planes:`)."""
    module = _fresh_module()
    text = _mutate_once(
        LOCK_TEXT,
        "\nselected_later_planes:\n",
        "\n  hermes-agent:\n"
        "    repository: https://github.com/NousResearch/hermes-agent.git\n"
        "    commit: 0000000000000000000000000000000000000000\n"
        "\nselected_later_planes:\n",
    )
    with pytest.raises(module.ManifestError, match="duplicate key 'hermes-agent' at line 45"):
        module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))


def test_L5_lock_repository_pinned_twice(tmp_path: Path) -> None:
    """A second component carrying hermes's repository: the old parser let the last one
    win. R6: refused, naming both `section.component` keys."""
    module = _fresh_module()
    text = _mutate_once(
        LOCK_TEXT,
        "\nselected_later_planes:\n",
        "\nk170_probe_section:\n"
        "  hermes-agent-copy:\n"
        "    repository: https://github.com/NousResearch/hermes-agent.git\n"
        "    commit: 0000000000000000000000000000000000000000\n"
        "\nselected_later_planes:\n",
    )
    with pytest.raises(
        module.ManifestError,
        match="is pinned by both selected_core\\.hermes-agent and k170_probe_section\\.hermes-agent-copy",
    ):
        module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))


def test_L6_lock_pin_key_typo(tmp_path: Path) -> None:
    """`comit:` instead of `commit:`: the old parser dropped hermes. R4: refused,
    naming `selected_core.hermes-agent`."""
    module = _fresh_module()
    text = _mutate_once(LOCK_TEXT, f"    commit: {HERMES_COMMIT}\n", f"    comit: {HERMES_COMMIT}\n")
    with pytest.raises(
        module.ManifestError,
        match="selected_core\\.hermes-agent has a repository but no pin",
    ):
        module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))


def test_L7_lock_pin_read_as_scalar_is_a_regression_row(tmp_path: Path) -> None:
    """REGRESSION ROW (already green at the PIN, documented in K170-report.md):
    `commit: 1e10`. The brief's premise is that YAML reads `1e10` as a float, but
    PyYAML 1.1's resolver does not: it is a plain string, so the old parser already
    keeps hermes with `1e10` as the pin value and R5 accepts it as a string. This
    row proves the pin survives as the 24-entry map with `1e10` as a string (the
    dedicated non-string-pin refusal is L7b, which a real YAML int exercises)."""
    module = _fresh_module()
    text = _mutate_once(LOCK_TEXT, f"    commit: {HERMES_COMMIT}\n", "    commit: 1e10\n")
    lock = module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))
    assert len(lock) == 24, f"24 expected, got {len(lock)}"
    assert lock[HERMESL] == ("1e10", "selected_core.hermes-agent")


def test_L7b_lock_pin_read_as_int_is_refused(tmp_path: Path) -> None:
    """The dedicated R5 test: a pin YAML reads as an int (`12345`) is refused, naming
    the component. This is the real non-string-pin class (YAML reads a long run of
    digits as an int, an empty value as None)."""
    module = _fresh_module()
    text = _mutate_once(
        LOCK_TEXT,
        f"    commit: {HERMES_COMMIT}\n",
        "    commit: 12345\n",
    )
    with pytest.raises(
        module.ManifestError,
        match=r"selected_core\.hermes-agent: the value 12345 is not a non-empty whitespace-free string",
    ):
        module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))


def test_L8_lock_pin_with_trailing_comment(tmp_path: Path) -> None:
    """The old parser glued the comment into the pin value. The YAML loader drops the
    comment: the real map is returned."""
    module = _fresh_module()
    text = _mutate_once(
        LOCK_TEXT, f"    commit: {HERMES_COMMIT}\n", f"    commit: {HERMES_COMMIT}  # note\n"
    )
    lock = module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))
    assert lock == module.parse_lock(REPO / "upstream.lock.yaml")


def test_L9_lock_yaml_round_trip(tmp_path: Path) -> None:
    """The lock re-dumped by `yaml.safe_dump`: the old parser raised
    `upstream lock parse failure at line 163` (a skipped legitimate field). The YAML
    loader returns the real map."""
    module = _fresh_module()
    text = yaml.safe_dump(yaml.safe_load(LOCK_TEXT), sort_keys=False, width=4096)
    lock = module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))
    assert lock == module.parse_lock(REPO / "upstream.lock.yaml")


# --- S rows: the SBOM ---


def test_S1_sbom_trailing_comment_on_name(tmp_path: Path) -> None:
    """The old parser named hermes `agent-client-protocol` and dropped the following
    pin. The YAML loader returns the real map (22 entries)."""
    module = _fresh_module()
    text = _mutate_once(SBOM_TEXT, "\n  - name: hermes-agent\n", "\n  - name: hermes-agent  # note\n")
    sbom = module.parse_sbom(_write(tmp_path, "SBOM.yaml", text))
    assert sbom == module.parse_sbom(REPO / "SBOM.yaml")


def test_S2_sbom_repository_named_twice(tmp_path: Path) -> None:
    """An appended item with hermes's repository: the old parser let the last one win.
    R7: refused, naming both items' names."""
    module = _fresh_module()
    text = (
        SBOM_TEXT.rstrip("\n")
        + "\n\n  - name: hermes-agent-copy\n"
        "    repository: https://github.com/NousResearch/hermes-agent.git\n"
        "    commit: 0000000000000000000000000000000000000000\n"
    )
    with pytest.raises(
        module.ManifestError,
        match="is named by both hermes-agent and hermes-agent-copy",
    ):
        module.parse_sbom(_write(tmp_path, "SBOM.yaml", text))


def test_S3_sbom_pin_key_typo(tmp_path: Path) -> None:
    """`comit:` in the SBOM's hermes item: the old parser dropped hermes. R7: refused,
    naming `hermes-agent`."""
    module = _fresh_module()
    text = _mutate_once(SBOM_TEXT, f"    commit: {HERMES_COMMIT}\n", f"    comit: {HERMES_COMMIT}\n")
    with pytest.raises(
        module.ManifestError,
        match="component hermes-agent has a repository but no pin",
    ):
        module.parse_sbom(_write(tmp_path, "SBOM.yaml", text))


def test_S4_sbom_flow_style_item(tmp_path: Path) -> None:
    """The hermes item written in flow style: the old parser dropped it (the line loop
    only knows the block form). The YAML loader reads both: the real map is returned.

    The mutation replaces the WHOLE item (name, repository, commit, license, role) with
    one flow mapping. The brief's own snippet has a doubled closing brace (a YAML
    syntax error) and leaves the item's `license`/`role` lines dangling under the closed
    mapping, which would make the document malformed (K170-report.md, DISCREPANCIES).
    """
    module = _fresh_module()
    flow_item = (
        "  - {name: hermes-agent, "
        "repository: \"https://github.com/NousResearch/hermes-agent.git\", "
        f"commit: {HERMES_COMMIT}, "
        "license: MIT, role: main_production_workhorse_and_native_acp_server"
        + "}\n"
    )
    text = _mutate_once(SBOM_TEXT, HERMES_SBOM_BLOCK, flow_item)
    sbom = module.parse_sbom(_write(tmp_path, "SBOM.yaml", text))
    assert sbom == module.parse_sbom(REPO / "SBOM.yaml")


def test_S5_sbom_yaml_round_trip_is_a_regression_row(tmp_path: Path) -> None:
    """REGRESSION ROW (already green at the PIN): the real SBOM re-dumped by
    `yaml.safe_dump` is still the block form the old parser accepts, so it returns the
    real map. It is a regression row, not a red one."""
    module = _fresh_module()
    text = yaml.safe_dump(yaml.safe_load(SBOM_TEXT), sort_keys=False, width=4096)
    sbom = module.parse_sbom(_write(tmp_path, "SBOM.yaml", text))
    assert sbom == module.parse_sbom(REPO / "SBOM.yaml")


def test_S6_sbom_pin_read_as_int_is_refused(tmp_path: Path) -> None:
    """The dedicated R5/R7 non-string-pin test: an appended item whose commit YAML reads
    as an int is refused, naming the item's name."""
    module = _fresh_module()
    text = (
        SBOM_TEXT.rstrip("\n")
        + "\n\n  - name: k170-probe\n"
        "    repository: https://github.com/k170probe/k170-probe.git\n"
        "    commit: 12345\n"
    )
    with pytest.raises(
        module.ManifestError,
        match=r"component k170-probe: the value 12345 is not a non-empty whitespace-free string",
    ):
        module.parse_sbom(_write(tmp_path, "SBOM.yaml", text))


# --- P rows: the provenance (R8) ---


def test_P1_provenance_non_row_line_is_refused(tmp_path: Path) -> None:
    """A non-blank line inside the table that does not start with `|` is refused,
    naming its line. The 9 data rows are lines 11-19; the third data row (line 13,
    `scripts/gn_mcp.py`) is the mutation target. The old walk stopped at the first
    non-`|` line silently, yielding 2 of the 9 roots."""
    module = _fresh_module()
    rows = [line for line in PROV_TEXT.splitlines() if line.startswith("| ")]
    assert len(rows) == 10, f"10 expected (9 data rows + the header), got {len(rows)}"
    target = rows[3]
    assert PROV_TEXT.splitlines().index(target) == 12, "the target must be file line 13"
    text = _mutate_once(PROV_TEXT, target + "\n", " " + target + "\n")
    with pytest.raises(
        module.ManifestError,
        match=r"provenance table parse failure at line 13: expected a row",
    ):
        module.parse_provenance(_write(tmp_path, "VENDORED-FROM.md", text))


# --- X rows: separators (R1) and shapes (R3/R4/R7) ---


def test_X1_lock_line_separator_is_refused(tmp_path: Path) -> None:
    """U+2028 inside a lock value. The old parser: a YAML syntax error (a raw
    `yaml.YAMLError`, a crash). R1: refused before any parsing, naming the file and
    the line (line 12, the hermes commit line)."""
    module = _fresh_module()
    text = _mutate_once(
        LOCK_TEXT,
        f"    commit: {HERMES_COMMIT}\n",
        f"    commit: {HERMES_COMMIT[:20]}{LS}{HERMES_COMMIT[20:]}\n",
    )
    with pytest.raises(
        module.ManifestError,
        match=r"upstream\.lock\.yaml: line 12 holds '\\u2028'",
    ):
        module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))


def test_X2_lock_crlf_line_endings_are_refused(tmp_path: Path) -> None:
    """The lock with CRLF line endings. R1: refused at line 1, naming the file and
    the character. (The read must be raw bytes: `Path.read_text` translates CRLF to
    LF and would never see the carriage return, a hollow green — K170-report.md,
    DISCREPANCIES.)"""
    module = _fresh_module()
    text = LOCK_TEXT.replace("\n", CR + "\n")
    with pytest.raises(
        module.ManifestError,
        match=r"upstream\.lock\.yaml: line 1 holds '\\r'",
    ):
        module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))


def test_X3_sbom_item_without_repository_is_refused(tmp_path: Path) -> None:
    """The hermes item without its `repository`: the old parser dropped it. R7:
    refused, naming the item's name."""
    module = _fresh_module()
    text = _mutate_once(
        SBOM_TEXT,
        HERMES_SBOM_BLOCK,
        "  - name: hermes-agent\n",
    )
    with pytest.raises(
        module.ManifestError,
        match=r"component hermes-agent is missing its repository",
    ):
        module.parse_sbom(_write(tmp_path, "SBOM.yaml", text))


def test_X4_lock_section_written_as_a_list_is_refused(tmp_path: Path) -> None:
    """R3: a section whose value is a flow LIST (not a mapping). Appended at the file end,
    `k170_probe: [a, b]` is VALID YAML (a top-level value that has no mapping continuation);
    the refusal is R3's, naming the section: `upstream lock: section 'k170_probe' is a list,
    not a mapping`. (The brief's literal mid-file mutation `selected_core: [a, b]` instead
    collides with the block mapping already begun at the indent and is a YAML syntax error —
    measured: `ParserError` at line 46 — refused by the R2 class, a different refusal.)"""
    module = _fresh_module()
    text = LOCK_TEXT.rstrip("\n") + "\n\nk170_probe: [a, b]\n"
    with pytest.raises(
        module.ManifestError,
        match=r"upstream lock: section 'k170_probe' is a list, not a mapping",
    ):
        module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))


def test_X4b_lock_top_level_scalar_is_ignored_regression_row(tmp_path: Path) -> None:
    """REGRESSION ROW (R3, already the contract at the PIN): a top-level SCALAR (not
    a list, not a mapping) carries no pin and is ignored, as the real file's
    `snapshot_date` already is. The brief's R3 names the list case (X4) as the
    refusal; a scalar is the ignored case."""
    module = _fresh_module()
    text = LOCK_TEXT.rstrip("\n") + "\n\nk170_probe: a-scalar\n"
    lock = module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))
    assert lock == module.parse_lock(REPO / "upstream.lock.yaml")


def test_X5_lock_component_value_as_a_list_is_refused(tmp_path: Path) -> None:
    """R3: inside a section, a component whose value is a list (not a mapping) is
    refused, naming `section.component`."""
    module = _fresh_module()
    text = (
        LOCK_TEXT.rstrip("\n")
        + "\n\nk170_probe:\n"
        "  k170-probe-component:\n"
        "    - a\n"
        "    - b\n"
    )
    with pytest.raises(
        module.ManifestError,
        match=r"k170_probe\.k170-probe-component is not a mapping",
    ):
        module.parse_lock(_write(tmp_path, "upstream.lock.yaml", text))
