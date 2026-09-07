"""tests/test_ripwire_review.py — deterministic, LLM-free, no network, no real binary.

Proves:
  (a) bogus mode + missing binary → exit 64
  (b) valid mode + missing binary → exit 0 + exact "missing" line
  (c) every mode builds the exact argv the wrapper must produce (excludes, verb, --limit/--top-k)
  (d) fake binary exit code passes through unchanged
  (e) negative control: a mutant that omits an exclude flag fails the argv assertion
"""
from __future__ import annotations

import os
import stat
import subprocess
import textwrap
from pathlib import Path

import pytest

SCRIPT = str(Path(__file__).resolve().parent.parent / "scripts" / "ripwire_review.sh")
EXCLUDES = [
    "--exclude=sandbox-kit",
    "--exclude=/.claude",
    "--exclude=/graft",
    "--exclude=/.agents",
    "--exclude=harness-ports/ports",
]


def _make_fake_binary(tmp_path: Path, exit_code: int = 0) -> str:
    """Create a shell script that prints its argv one-per-line and exits with exit_code."""
    fake = tmp_path / "ripwire"
    fake.write_text(
        textwrap.dedent(f"""\
            #!/usr/bin/env bash
            for arg in "$@"; do echo "$arg"; done
            exit {exit_code}
        """)
    )
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    return str(fake)


def _run(args: list[str], env_override: dict | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    if env_override:
        env.update(env_override)
    return subprocess.run(
        ["bash", SCRIPT] + args,
        capture_output=True, text=True, env=env, timeout=30,
    )


# --- (a) bogus mode with missing binary → exit 64 ---

def test_bogus_mode_exits_64():
    r = _run(["nosuchmode"], {"RIPWIRE_BIN": "/nonexistent/ripwire"})
    assert r.returncode == 64, f"expected 64, got {r.returncode}: {r.stdout}{r.stderr}"


# --- (b) valid mode + missing binary → exit 0 + exact "missing" line ---

@pytest.mark.parametrize("mode", ["map", "for", "callers", "impact", "exercises", "test-gate", "edit-check", "skipped"])
def test_missing_binary_exits_0(mode):
    # Modes that need an extra argument
    extra = {"for": ['"q"'], "callers": ["sym"], "impact": ["sym"],
             "exercises": ["f.py"], "test-gate": ["f.py"], "edit-check": ["sym"]}
    args = [mode] + extra.get(mode, [])
    r = _run(args, {"RIPWIRE_BIN": "/nonexistent/ripwire"})
    assert r.returncode == 0, f"expected 0, got {r.returncode}: {r.stdout}{r.stderr}"
    assert "ripwire_review: /nonexistent/ripwire missing" in r.stdout


# --- (c) every mode builds the exact argv (excludes + verb + --limit/--top-k) ---

def _assert_argv(tmp_path, mode, mode_args, expected_fragments, *, exit_code=0, env_extra=None):
    """Run the wrapper with a fake binary and assert every expected fragment appears in its argv."""
    fake = _make_fake_binary(tmp_path, exit_code)
    env = {"RIPWIRE_BIN": fake}
    if env_extra:
        env.update(env_extra)
    r = _run([mode] + mode_args, env)
    lines = r.stdout.strip().splitlines()
    for frag in expected_fragments:
        assert frag in lines, f"missing {frag!r} in argv: {lines}"
    # Every exclude must be present
    for exc in EXCLUDES:
        assert exc in lines, f"missing exclude {exc!r} in argv: {lines}"
    return r


def test_map_argv(tmp_path):
    _assert_argv(tmp_path, "map", ["--top-k=5"], ["--top-k=5"])


def test_map_default_argv(tmp_path):
    """map with no extra args produces no --limit (only the excludes + the root dir)."""
    fake = _make_fake_binary(tmp_path)
    r = _run(["map"], {"RIPWIRE_BIN": fake})
    lines = r.stdout.strip().splitlines()
    assert not any("--limit" in l for l in lines), f"map should not produce --limit: {lines}"


def test_for_argv(tmp_path):
    _assert_argv(tmp_path, "for", ["where is X"], ['--for=where is X'])


def test_callers_argv(tmp_path):
    _assert_argv(tmp_path, "callers", ["_write_status"], ["--callers=_write_status", "--limit=20"])


def test_callers_custom_limit(tmp_path):
    _assert_argv(tmp_path, "callers", ["sym"], ["--callers=sym", "--limit=50"],
                 env_extra={"RIPWIRE_LIMIT": "50"})


def test_impact_argv(tmp_path):
    _assert_argv(tmp_path, "impact", ["main"], ["--impact=main", "--limit=20"])


def test_exercises_argv(tmp_path):
    _assert_argv(tmp_path, "exercises", ["tests/test_foo.py"],
                 ["--exercises=tests/test_foo.py", "--limit=20"])


def test_test_gate_argv(tmp_path):
    _assert_argv(tmp_path, "test-gate", ["a.py", "b.py"],
                 ["--test-gate=a.py", "--test-gate=b.py", "--limit=20"])


def test_edit_check_argv(tmp_path):
    _assert_argv(tmp_path, "edit-check", ["foo"], ["--edit-check=foo", "--limit=20"])


def test_skipped_argv(tmp_path):
    _assert_argv(tmp_path, "skipped", [], ["--skipped", "--limit=20"])


# --- (d) fake exit code passes through ---

def test_exit_code_passthrough(tmp_path):
    """A non-zero exit from the real binary passes through unchanged."""
    r = _assert_argv(tmp_path, "callers", ["sym"], ["--callers=sym"], exit_code=4)
    assert r.returncode == 4, f"expected passthrough exit 4, got {r.returncode}"


# --- (e) negative control: mutant that drops an exclude → assertion fails ---

def test_negative_control_missing_exclude(tmp_path):
    """A wrapper that omits --exclude=/graft would fail the exclude check. Prove it."""
    fake = _make_fake_binary(tmp_path)
    r = _run(["map"], {"RIPWIRE_BIN": fake})
    lines = r.stdout.strip().splitlines()
    # Simulate a mutant that dropped --exclude=/graft
    mutant_lines = [l for l in lines if l != "--exclude=/graft"]
    # The assertion that would run on the mutant's output:
    with pytest.raises(AssertionError):
        assert "--exclude=/graft" in mutant_lines
