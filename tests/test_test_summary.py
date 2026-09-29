"""Tests for scripts/test_summary.sh — deterministic, LLM-free, network-free.

V-d F19: assert the EXACT summary line format (full regex), not substrings.
"""

import os
import re
import subprocess
import sys
import tempfile
import textwrap

SCRIPT = os.path.join(
    os.path.dirname(__file__), os.pardir, "scripts", "test_summary.sh"
)

# The EXACT format: "N passed[, M skipped] in X.XXs"
# No other shape is accepted.
_SUMMARY_RE = re.compile(
    r"^(\d+ passed(?:, \d+ skipped)?) in \d+\.\d+s$"
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
        # V-d F19: exact regex match, not substring
        assert _SUMMARY_RE.match(body), \
            f"summary line does not match exact format: {body!r}"
        # Additionally confirm the exact counts (not a superstring like "11 passed")
        m = _SUMMARY_RE.match(body)
        assert m.group(1) == "1 passed, 1 skipped"
        assert result.returncode == 0
    finally:
        os.unlink(tmp)


def test_failure():
    """A failing test yields exit 1 and summary matching the full regex."""
    code = textwrap.dedent("""\
        def test_bad():
            assert False, "intentional"
    """)
    # F13: the failing case also uses the full regex, not substring
    _FAIL_RE = re.compile(
        r"^(\d+ failed(?:, \d+ passed)?) in \d+\.\d+s$"
    )
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
        m = _FAIL_RE.match(body)
        assert m, f"summary line does not match exact format: {body!r}"
        assert m.group(1) == "1 failed"
        assert result.returncode == 1
    finally:
        os.unlink(tmp)


def test_nonexistent_path_yields_exit_4():
    """V-d F19: a nonexistent path must yield pytest-exit: 4."""
    result = subprocess.run(
        ["bash", SCRIPT, "/tmp/does_not_exist_at_all/test_fake.py"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    lines = result.stdout.strip().splitlines()
    exit_line = [l for l in lines if l.startswith("pytest-exit:")]
    assert exit_line, f"No pytest-exit line in output:\n{result.stdout}"
    assert exit_line[-1] == "pytest-exit: 4"
    assert result.returncode == 4


def test_a_basetemp_whose_parent_is_missing_is_made_first(tmp_path):
    # 2026-09-29: a brief's premise line passed --basetemp=/tmp/premise-jevrelay/bt with no parent, and all 24 relay
    # tests errored at setup (FileNotFoundError); the same shape read every mutant as KILLED in AF-AP-223.
    test = tmp_path / "test_uses_tmp.py"
    test.write_text("def test_tmp(tmp_path):\n    assert tmp_path.is_dir()\n")
    for form in (["--basetemp=%s" % (tmp_path / "gone1" / "bt")], ["--basetemp", str(tmp_path / "gone2" / "bt")]):
        r = subprocess.run(["bash", SCRIPT, str(test), *form], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, (form, r.stdout)
        assert r.stdout.splitlines()[-1].startswith("pytest-summary: 1 passed"), (form, r.stdout)


def test_a_direct_pytest_run_makes_a_missing_basetemp_parent(tmp_path):
    # The same trap outside the wrapper (2026-09-29): a mutant run called pytest directly with --basetemp under a
    # missing parent, and every test errored at setup; a mutation driver reads that as KILLED (AF-AP-223).
    # tests/conftest.py's pytest_configure makes the parent for every pytest run over tests/.
    root = os.path.join(os.path.dirname(__file__), os.pardir)
    target = "tests/test_test_summary.py::test_a_basetemp_whose_parent_is_missing_is_made_first"   # takes tmp_path
    bt = tmp_path / "gone" / "deeper" / "bt"
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--basetemp=%s" % bt, target],
                       capture_output=True, text=True, timeout=120, cwd=root)
    assert r.returncode == 0, r.stdout[-2000:]
    assert r.stdout.strip().splitlines()[-1].startswith("1 passed"), r.stdout[-2000:]
