"""scripts/sentrux_review.sh — the ADVISORY architecture-health wrapper (never a gate).

Two properties are pinned: (1) a missing binary is a message and exit 0, never a failure that
could block a lane; (2) with the pinned binary present, `check` scans the composed copy and
writes its report under .sentrux-runtime/ while still exiting 0 (the tool's own exit is
reported, not propagated) — and `--strict` propagates it.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts" / "sentrux_review.sh"
BIN = Path("/root/.local/bin/sentrux")


def _binary_available(path: Path = BIN) -> bool:
    """True only when the pinned binary is present AND this identity can see it.

    AF-AP-44 (2026-09-06): CI runs as a non-root user and /root is 0700, so `Path.exists()` raises
    PermissionError instead of returning False — at module scope that error aborts pytest COLLECTION for
    the whole tests job (four red workflow runs across checkpoints 4-5). Any OSError means "not available
    here": the venue-gated tests skip, they never error."""
    try:
        return path.is_file()
    except OSError:
        return False


def test_binary_probe_never_raises(monkeypatch):
    """AF-AP-44 control: a PermissionError from the filesystem probe is 'unavailable', not a collection error."""
    def _denied(self):
        raise PermissionError(13, "Permission denied", str(self))
    monkeypatch.setattr(Path, "is_file", _denied)
    assert _binary_available(Path("/root/.local/bin/sentrux")) is False


def test_binary_probe_true_for_an_existing_file(tmp_path):
    f = tmp_path / "sentrux"; f.write_bytes(b"#!/bin/sh\n"); f.chmod(0o755)
    assert _binary_available(f) is True


def _run(*args, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    assert "SENTRUX_RUNTIME_DIR" in env, "every test points the wrapper at tmp_path — never the repo root"
    return subprocess.run(["bash", str(WRAPPER), *args], capture_output=True, text=True, env=env, timeout=300)


def test_missing_binary_is_advisory_exit_zero(tmp_path):
    r = _run("check", env_extra={"SENTRUX_BIN": str(tmp_path / "absent"), "SENTRUX_RUNTIME_DIR": str(tmp_path / "rt")})
    assert r.returncode == 0
    assert r.stdout.strip() == f"sentrux_review: {tmp_path / 'absent'} missing — run scripts/setup.sh (pinned install)"


def test_usage_error_exits_64(tmp_path):
    r = _run("bogus", env_extra={"SENTRUX_RUNTIME_DIR": str(tmp_path / "rt")})
    assert (r.returncode, r.stdout.strip()) == (64, "usage: sentrux_review.sh check|save|compare [--strict]")


@pytest.mark.skipif(not _binary_available(), reason="pinned sentrux binary not installed in this venue")
def test_check_reports_and_exits_zero(tmp_path):
    rt = tmp_path / "rt"
    r = _run("check", env_extra={"SENTRUX_RUNTIME_DIR": str(rt)})
    assert r.returncode == 0
    assert (rt / "last-check.txt").exists()
    assert (rt / "tree" / ".sentrux" / "rules.toml").exists()
    assert not (rt / "tree" / "sandbox-kit").exists()
    last = r.stdout.strip().splitlines()[-1]
    assert last.startswith("sentrux check: tool exit ") and last.endswith("(advisory — never a gate; --strict passes it through)")


@pytest.mark.skipif(not _binary_available(), reason="pinned sentrux binary not installed in this venue")
def test_strict_propagates_tool_exit(tmp_path):
    r = _run("check", "--strict", env_extra={"SENTRUX_RUNTIME_DIR": str(tmp_path / "rt")})
    tool_rc = int(r.stdout.strip().splitlines()[-1].split("tool exit ")[1].split()[0])
    assert r.returncode == tool_rc


@pytest.mark.skipif(not _binary_available(), reason="pinned sentrux binary not installed")
def test_compare_without_baseline_is_advisory(tmp_path):
    r = _run("compare", env_extra={"SENTRUX_RUNTIME_DIR": str(tmp_path / "rt")})
    assert r.returncode == 0
    assert r.stdout.strip() == "sentrux_review: no baseline — run 'save' before the lane"


@pytest.mark.skipif(not _binary_available(), reason="pinned sentrux binary not installed")
def test_save_then_compare_in_tmp_runtime(tmp_path):
    rt = tmp_path / "rt"
    assert _run("save", env_extra={"SENTRUX_RUNTIME_DIR": str(rt)}).returncode == 0
    assert (rt / "baseline.json").exists()
    r = _run("compare", env_extra={"SENTRUX_RUNTIME_DIR": str(rt)})
    assert r.returncode == 0 and "No degradation detected" in (rt / "last-compare.txt").read_text()


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
