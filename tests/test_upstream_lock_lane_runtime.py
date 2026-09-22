"""Tests for the hermes-agent-lane-runtime entry in upstream.lock.yaml (D-043 -> D-048 item 3).

Asserts:
  1. The lane_runtime.hermes-agent-lane-runtime entry exists with the brief's exact keys.
  2. The commit value is 40 lowercase hex characters.
  3. The existing selected_core.hermes-agent entry is byte-identical to its committed golden.
  4. Negative control: a copy with a 7-hex commit is rejected by name.
"""
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = REPO_ROOT / "upstream.lock.yaml"

# ---- golden: the existing hermes-agent entry, read at test-authoring time ----
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


def _load_lock():
    return yaml.safe_load(LOCK_PATH.read_text(encoding="utf-8"))


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
    """The commit field is exactly 40 lowercase hex characters."""
    lock = _load_lock()
    commit = lock["lane_runtime"]["hermes-agent-lane-runtime"]["commit"]
    assert re.fullmatch(r"[0-9a-f]{40}", commit), (
        f"commit is not 40 lowercase hex: {commit!r}"
    )


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


def test_hermes_agent_entry_unchanged():
    """The existing selected_core.hermes-agent entry is byte-identical to its golden."""
    lock = _load_lock()
    section = lock.get("selected_core")
    assert section is not None, "selected_core section missing"
    entry = section.get("hermes-agent")
    assert entry is not None, "hermes-agent entry missing from selected_core"
    assert entry == HERMES_AGENT_GOLDEN, (
        f"hermes-agent entry differs from golden: {entry!r}"
    )


# ---------- negative control ----------

def test_short_commit_rejected(tmp_path):
    """A lock copy with a 7-hex commit for the lane runtime is detected as invalid.

    This is the negative control: it MUST fail the 40-hex assertion.
    """
    lock = _load_lock()
    # Mutate the commit to only 7 hex characters.
    lock["lane_runtime"]["hermes-agent-lane-runtime"]["commit"] = "b3399c1"
    mutated_path = tmp_path / "upstream.lock.yaml"
    mutated_path.write_text(yaml.dump(lock, default_flow_style=False), encoding="utf-8")
    mutated = yaml.safe_load(mutated_path.read_text(encoding="utf-8"))
    commit = mutated["lane_runtime"]["hermes-agent-lane-runtime"]["commit"]
    # The 7-hex commit MUST NOT pass the 40-hex check.
    assert not re.fullmatch(r"[0-9a-f]{40}", str(commit)), (
        f"negative control failed: 7-hex commit {commit!r} passed the 40-hex check"
    )
