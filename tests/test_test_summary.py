"""Tests for scripts/test_summary.sh — deterministic, LLM-free, network-free."""

import os
import subprocess
import tempfile
import textwrap

SCRIPT = os.path.join(
    os.path.dirname(__file__), os.pardir, "scripts", "test_summary.sh"
)


def _run_summary(test_file_path: str) -> subprocess.CompletedProcess:
    """Run test_summary.sh on a single test file, capture output."""
    return subprocess.run(
        ["bash", SCRIPT, test_file_path],
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_pass_and_skip():
    """One passing + one skipped test yields exit 0 and correct summary."""
    code = textwrap.dedent("""\
        import pytest

        def test_ok():
            assert True

        @pytest.mark.skip(reason="deliberate")
        def test_skipped():
            pass
    """)
    with tempfile.NamedTemporaryFile(
        suffix=".py", prefix="tmp_test_", mode="w", delete=False
    ) as f:
        f.write(code)
        f.flush()
        tmp = f.name
    try:
        result = _run_summary(tmp)
        lines = result.stdout.strip().splitlines()
        exit_line = [l for l in lines if l.startswith("pytest-exit:")]
        summary_line = [l for l in lines if l.startswith("pytest-summary:")]
        assert exit_line, f"No pytest-exit line in output:\n{result.stdout}"
        assert summary_line, f"No pytest-summary line in output:\n{result.stdout}"
        assert exit_line[-1] == "pytest-exit: 0"
        body = summary_line[-1].removeprefix("pytest-summary: ")
        assert "1 passed" in body
        assert "1 skipped" in body
        assert result.returncode == 0
    finally:
        os.unlink(tmp)


def test_failure():
    """A failing test yields exit 1 and summary containing '1 failed'."""
    code = textwrap.dedent("""\
        def test_bad():
            assert False, "intentional"
    """)
    with tempfile.NamedTemporaryFile(
        suffix=".py", prefix="tmp_test_", mode="w", delete=False
    ) as f:
        f.write(code)
        f.flush()
        tmp = f.name
    try:
        result = _run_summary(tmp)
        lines = result.stdout.strip().splitlines()
        exit_line = [l for l in lines if l.startswith("pytest-exit:")]
        summary_line = [l for l in lines if l.startswith("pytest-summary:")]
        assert exit_line, f"No pytest-exit line in output:\n{result.stdout}"
        assert summary_line, f"No pytest-summary line in output:\n{result.stdout}"
        assert exit_line[-1] == "pytest-exit: 1"
        body = summary_line[-1].removeprefix("pytest-summary: ")
        assert "1 failed" in body
        assert result.returncode == 1
    finally:
        os.unlink(tmp)
