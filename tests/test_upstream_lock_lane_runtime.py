"""Tests for the hermes-agent-lane-runtime entry in upstream.lock.yaml (D-043 -> D-048 item 3; REPIN-a-R1).

Asserts:
  1. The lane_runtime.hermes-agent-lane-runtime entry exists with the brief's exact keys.
  2. Its commit passes the ONE validity check, `_check_lane_runtime_commit` (a string of 40 lowercase hex).
  3. All eight of its values are pinned, `verified:` included: three pieces of evidence, in order (R3, R4).
  4. The existing selected_core.hermes-agent entry is byte-identical to its six committed lines, read from the
     raw bytes (R1); its parsed values equal the golden dict (the second view).
  5. Negative control: a lock copy whose lane-runtime commit is 7 hex, 39 hex, 41 hex, 40 uppercase hex or a
     YAML integer, read by the same loader, fails the same check by name (R2).
  6. docs/HARNESS-PORTS.md §12 says that nothing reads the pin until REPIN-b lands (R5).
"""
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = REPO_ROOT / "upstream.lock.yaml"
HARNESS_PORTS_PATH = REPO_ROOT / "docs" / "HARNESS-PORTS.md"

# ---- golden: the existing hermes-agent entry, read at test-authoring time ----
# The byte view: its six committed lines (`sed -n 10,15p upstream.lock.yaml | cat -A` shows no trailing whitespace).
HERMES_AGENT_GOLDEN_LINES = [
    "  hermes-agent:",
    "    repository: https://github.com/NousResearch/hermes-agent.git",
    "    commit: 527da60844d4dced37879ea50259675371abe10e",
    "    observed_version: 0.21.0",
    "    license: MIT",
    "    role: main_production_workhorse_and_native_acp_server",
]
# The parsed view (the second view): blind to whitespace, quoting, key order, comments and duplicate keys.
HERMES_AGENT_GOLDEN = {
    "repository": "https://github.com/NousResearch/hermes-agent.git",
    "commit": "527da60844d4dced37879ea50259675371abe10e",
    "observed_version": "0.21.0",
    "license": "MIT",
    "role": "main_production_workhorse_and_native_acp_server",
}

# ---- brief's measured values for the lane-runtime entry ----
LANE_RUNTIME_COMMIT = "b3399c139624a0081d70397741a5b45f60fbe1f4"
LANE_RUNTIME_EXPECTED_KEYS = {
    "commit", "version", "python", "sqlite",
    "role", "reason", "diff_from_proof_pin", "verified",
}
# `verified:` (REPIN-a-R1 R3): three pieces, in this order, each saying what it proves. Every number is copied
# from the REPIN-a-R1 brief's premise or from tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md.
LANE_RUNTIME_VERIFIED = "; ".join((
    # (a) the harness adapters on the PC's shell and Python; the suite runs no Hermes binary
    "harness-ports/tests/run-all.sh on the PC at 2ebd486, in a git clone with the lanes' AF_VENV, Python 3.13.11: "
    "all suites passed, rc 0, 2026-09-23 09:08Z (binary-free by its header)",
    # (b) the lane runtime's identity, read on the PC
    "identity probe 2026-09-23 08:58Z: b3399c1, Hermes Agent v0.21.1, venv Python 3.11.15, SQLite 3.53.1, "
    "shared state.db WAL",
    # (c) the lanes launched since the update, counted from their directories on the PC
    "110 PC lane directories whose latest launch was at or after 2026-09-08 14:22:00Z (98 with a report; brief.md--0000000 never ran Hermes), "
    "tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md",
))
# The whole entry (REPIN-a-R1 R4): all eight keys' exact values.
LANE_RUNTIME_EXPECTED = {
    "commit": LANE_RUNTIME_COMMIT,
    "version": "0.21.1",
    "python": "3.11.15",
    "sqlite": "3.53.1",
    "role": "lane-runtime (scripts/pc_lane.sh -> hermes on the PC); NOT the S0-01 proof runtime",
    "reason": "SQLite >= 3.51.3 for WAL on the shared profile state.db (VERIFY-B5j); owner-run hermes update 2026-09-08",
    "diff_from_proof_pin": "31816 commits, 3939 files",
    "verified": LANE_RUNTIME_VERIFIED,
}

# ---- docs/HARNESS-PORTS.md §12 (REPIN-a-R1 R5) ----
SECTION_12_HEADING = "## 12. Lane runtime pin"
SECTION_12_UNENFORCED = (
    "Until REPIN-b lands, nothing reads `lane_runtime`, so a `hermes update` or a `HERMES_BIN` override moves "
    "the lanes with no check failing."
)


def _load_lock(path=LOCK_PATH):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _check_lane_runtime_commit(lock):
    """The ONE validity check of the lane-runtime commit: the positive test and the negative control call it."""
    commit = lock["lane_runtime"]["hermes-agent-lane-runtime"]["commit"]
    if not isinstance(commit, str) or re.fullmatch(r"[0-9a-f]{40}", commit) is None:
        raise ValueError(f"commit is not 40 lowercase hex: {commit!r}")
    return commit


def _hermes_agent_entry(text):
    """(index of its first line, its raw lines) for selected_core.hermes-agent in the lock text `text`.

    Exactly one line equals `  hermes-agent:`, and its top-level key is `selected_core:`. The entry runs from that
    line to the line before the next line that starts with exactly two spaces and a non-space, or with a
    top-level key. The text is split on "\\n" only, so a trailing space, a tab or a "\\r" stays in its line.
    """
    lines = text.split("\n")
    heads = [i for i, line in enumerate(lines) if line == "  hermes-agent:"]
    assert len(heads) == 1, (
        f"upstream.lock.yaml has {len(heads)} lines equal to '  hermes-agent:' (at {[i + 1 for i in heads]}); "
        f"lines that differ from it only in whitespace: "
        f"{[i + 1 for i, line in enumerate(lines) if line.strip() == 'hermes-agent:' and i not in heads]}"
    )
    head = heads[0]
    keys = [line for line in lines[:head] if re.match(r"[^\s#]", line)]
    assert keys and keys[-1] == "selected_core:", (
        f"'  hermes-agent:' (line {head + 1}) is not under 'selected_core:' but under {(keys[-1] if keys else None)!r}"
    )
    end = next((j for j in range(head + 1, len(lines)) if re.match(r"  \S|[^\s#]", lines[j])), len(lines))
    return head, lines[head:end]


# ---------- positive controls ----------

def test_lane_runtime_entry_exists():
    """The lane_runtime section and its hermes-agent-lane-runtime entry exist."""
    lock = _load_lock()
    section = lock.get("lane_runtime")
    assert section is not None, "lane_runtime section missing from upstream.lock.yaml"
    entry = section.get("hermes-agent-lane-runtime")
    assert entry is not None, "hermes-agent-lane-runtime entry missing"


def test_lane_runtime_has_exact_keys():
    """The entry carries exactly the keys the brief specifies."""
    lock = _load_lock()
    entry = lock["lane_runtime"]["hermes-agent-lane-runtime"]
    actual_keys = set(entry.keys())
    assert actual_keys == LANE_RUNTIME_EXPECTED_KEYS, (
        f"key mismatch: extra={actual_keys - LANE_RUNTIME_EXPECTED_KEYS}, "
        f"missing={LANE_RUNTIME_EXPECTED_KEYS - actual_keys}"
    )


def test_lane_runtime_commit_is_40_hex():
    """The committed commit passes the ONE validity check; a failure reads `commit is not 40 lowercase hex: ...`."""
    _check_lane_runtime_commit(_load_lock())


def test_lane_runtime_commit_value():
    """The commit matches the brief's measured value."""
    lock = _load_lock()
    commit = lock["lane_runtime"]["hermes-agent-lane-runtime"]["commit"]
    assert commit == LANE_RUNTIME_COMMIT, (
        f"commit mismatch: got {commit!r}, expected {LANE_RUNTIME_COMMIT!r}"
    )


def test_lane_runtime_version():
    """The version matches the brief's measured value."""
    lock = _load_lock()
    entry = lock["lane_runtime"]["hermes-agent-lane-runtime"]
    assert entry["version"] == "0.21.1"


def test_lane_runtime_sqlite():
    """The sqlite version matches the brief's measured value."""
    lock = _load_lock()
    entry = lock["lane_runtime"]["hermes-agent-lane-runtime"]
    assert entry["sqlite"] == "3.53.1"


def test_lane_runtime_entry_values():
    """All eight values of the entry are pinned (F7); a failure names every key whose value differs."""
    entry = _load_lock()["lane_runtime"]["hermes-agent-lane-runtime"]
    absent = object()
    assert entry == LANE_RUNTIME_EXPECTED, "lane_runtime.hermes-agent-lane-runtime differs at " + "; ".join(
        f"{key}: got {entry.get(key, '<absent>')!r}, expected {LANE_RUNTIME_EXPECTED.get(key, '<absent>')!r}"
        for key in sorted(entry.keys() | LANE_RUNTIME_EXPECTED.keys())
        if entry.get(key, absent) != LANE_RUNTIME_EXPECTED.get(key, absent)
    )


def test_lane_runtime_verified_value():
    """`verified:` is the exact committed value: the three pieces of evidence, in order (F3, F4)."""
    verified = _load_lock()["lane_runtime"]["hermes-agent-lane-runtime"]["verified"]
    assert verified == LANE_RUNTIME_VERIFIED, (
        f"verified mismatch: got {verified!r}, expected {LANE_RUNTIME_VERIFIED!r}"
    )


def test_hermes_agent_entry_unchanged():
    """The second view: selected_core.hermes-agent, as PyYAML parses it, equals its golden values.

    The byte view is test_hermes_agent_entry_lines_golden.
    """
    lock = _load_lock()
    section = lock.get("selected_core")
    assert section is not None, "selected_core section missing"
    entry = section.get("hermes-agent")
    assert entry is not None, "hermes-agent entry missing from selected_core"
    assert entry == HERMES_AGENT_GOLDEN, (
        f"hermes-agent entry differs from golden: {entry!r}"
    )


def test_hermes_agent_entry_lines_golden():
    """selected_core.hermes-agent is byte-identical to its six committed lines (F1); a failure names the first
    differing line."""
    head, entry = _hermes_agent_entry(LOCK_PATH.read_bytes().decode("utf-8"))
    golden = HERMES_AGENT_GOLDEN_LINES
    n = next((k for k in range(max(len(entry), len(golden))) if entry[k:k + 1] != golden[k:k + 1]), None)
    assert entry == golden, (
        f"selected_core.hermes-agent differs from its golden at entry line {n + 1} (upstream.lock.yaml line "
        f"{head + n + 1}): expected {(golden[n] if n < len(golden) else '<no line>')!r}, "
        f"got {(entry[n] if n < len(entry) else '<no line>')!r}"
    )


def test_harness_ports_section_12_says_the_pin_is_unenforced():
    """docs/HARNESS-PORTS.md §12 says that nothing reads the pin until REPIN-b lands (F5)."""
    lines = HARNESS_PORTS_PATH.read_text(encoding="utf-8").splitlines()
    heads = [i for i, line in enumerate(lines) if line == SECTION_12_HEADING]
    assert len(heads) == 1, f"docs/HARNESS-PORTS.md has {len(heads)} lines equal to {SECTION_12_HEADING!r}"
    end = next((j for j in range(heads[0] + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    section = " ".join(" ".join(lines[heads[0]:end]).split())
    assert SECTION_12_UNENFORCED in section, (
        f"docs/HARNESS-PORTS.md §12 (lines {heads[0] + 1}-{end}) lacks the sentence {SECTION_12_UNENFORCED!r}"
    )


# ---------- negative control ----------

BAD_COMMITS = [
    pytest.param("b3399c1", "b3399c1", id="7-hex"),
    pytest.param(LANE_RUNTIME_COMMIT[:39], LANE_RUNTIME_COMMIT[:39], id="39-hex"),
    pytest.param(LANE_RUNTIME_COMMIT + "0", LANE_RUNTIME_COMMIT + "0", id="41-hex"),
    pytest.param(LANE_RUNTIME_COMMIT.upper(), LANE_RUNTIME_COMMIT.upper(), id="40-uppercase-hex"),
    # 40 decimal digits: PyYAML loads an int, and str() of that int WOULD match the 40-hex pattern
    pytest.param("1234567890" * 4, int("1234567890" * 4), id="yaml-integer"),
]


@pytest.mark.parametrize("raw, loaded", BAD_COMMITS)
def test_bad_lane_runtime_commit_rejected(tmp_path, raw, loaded):
    """Negative control (F2): a copy of the lock whose lane-runtime commit line is replaced by `raw`, read by the
    SAME loader, fails the SAME check with the named message."""
    committed_line = f"    commit: {LANE_RUNTIME_COMMIT}\n"
    text = LOCK_PATH.read_text(encoding="utf-8")
    assert text.count(committed_line) == 1, (
        f"the lane-runtime commit line occurs {text.count(committed_line)} times, not once: {committed_line!r}"
    )
    copy = tmp_path / "upstream.lock.yaml"
    copy.write_text(text.replace(committed_line, f"    commit: {raw}\n"), encoding="utf-8")
    lock = _load_lock(copy)
    # de-vacuous: the copy carries exactly the bad value, with the type PyYAML gives it
    assert lock["lane_runtime"]["hermes-agent-lane-runtime"]["commit"] == loaded
    expected = f"commit is not 40 lowercase hex: {loaded!r}"
    with pytest.raises(ValueError, match=f"^{re.escape(expected)}$"):
        _check_lane_runtime_commit(lock)
