"""Tests for scripts/verify_command.py -- the Canny verify-command classifier port.

Test tables sourced from qkal/canny @ f2c5e53:
  test/checks.test.ts:47-137 (isVerify + product tables + override)
  test/checks.test.ts:238-242 (pipefail-feeding config test)
"""
from __future__ import annotations

import subprocess
import sys

import pytest

# Import the module under test from its path in scripts/.
import importlib.util
import pathlib

# Resolved from this file, never from the cwd: a relative path made the suite
# fail to collect when pytest ran outside the repository root.
SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "verify_command.py"

_spec = importlib.util.spec_from_file_location(
    "verify_command",
    SCRIPT,
    submodule_search_locations=[],
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

VERIFY = _mod.VERIFY
executed = _mod.executed
is_verify = _mod.is_verify
with_pipefail = _mod.with_pipefail


# ---------------------------------------------------------------------------
# Canny's 27-row table (test/checks.test.ts:49-75)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "cmd, expected",
    [
        ("pnpm test", True),
        ("node --test 2>&1 | tail -20", False),
        ("set -o pipefail; node --test 2>&1 | tail -20", True),
        ("set -euo pipefail\npnpm test | tail -5", True),
        ("echo pipefail; pnpm test 2>&1 | tail -20", False),
        ("pnpm test | tail -20 # set -o pipefail", False),
        ("set -o pipefail; set +o pipefail; pnpm test | tail", False),
        ("set +o pipefail; set -o pipefail; pnpm test | tail", True),
        ("pnpm test & echo done", False),
        ("pnpm test > out.log 2>&1", True),
        ("pnpm test || true", False),
        ("pnpm test; echo done", False),
        ("pnpm test 2>&1 | tail -5 && pnpm lint", True),
        ("echo tsc", False),
        ("tsc --version", False),
        ("git diff -- vitest.config.ts", False),
        ("cd web && uv run pytest -q", True),
        ("pnpm type-check", True),
        ("cargo build --release", True),
        ("ruff check .", True),
        ("ruff format .", False),
        ('git commit -m "add pytest suite"', False),
        ("ls -la", False),
        ("! npm test", False),
        ("true # npm test", False),
        ("npm test # every suite", True),
        ("npm test -- --grep=\\ #foo | tail", False),
    ],
    ids=[
        "pnpm_test",
        "piped_no_pipefail",
        "piped_with_pipefail",
        "pipefail_via_set_euo",
        "echo_before_piped",
        "pipefail_in_comment",
        "pipefail_off_then_on_off",
        "pipefail_on_then_off_on",
        "backgrounded",
        "redirected_stderr",
        "or_true",
        "semicolon_echo",
        "piped_tail_then_and_lint",
        "echo_tsc",
        "tsc_version",
        "git_diff",
        "cd_then_pytest",
        "type_check",
        "cargo_build",
        "ruff_check",
        "ruff_format",
        "commit_msg_pytest",
        "ls",
        "negated",
        "comment_hides",
        "comment_after",
        "escaped_space_comment",
    ],
)
def test_is_verify_27_rows(cmd: str, expected: bool) -> None:
    assert is_verify(cmd) is expected


# ---------------------------------------------------------------------------
# Product tables (test/checks.test.ts:80-131)
# ---------------------------------------------------------------------------
CHECKS = [
    "pnpm test",
    "npm test",
    "npx vitest run",
    "uv run pytest -q",
    "go test ./...",
    "cargo test",
    "tsc --noEmit",
    "pnpm build",
    "pnpm lint",
    "ruff check .",
    "pre-commit run --all-files",
]

HIDES = [
    lambda c: f"{c} | tail -5",
    lambda c: f"{c} 2>&1 | tee out.log",
    lambda c: f"{c} | grep -v warn",
    lambda c: f"{c} || true",
    lambda c: f"({c}) || echo failed",
    lambda c: f"{c}; echo done",
    lambda c: f"{c}\necho done",
    lambda c: f"{c} &",
    lambda c: f"{c} & wait",
    lambda c: f"if ! {c}; then echo bad; fi",
    lambda c: f"echo {c}",
    lambda c: f"{c} --help",
    lambda c: f'git commit -m "{c}"',
    lambda c: f'cat package.json | grep "{c}"',
]

KEEPS = [
    lambda c: f"cd packages/web && {c}",
    lambda c: f"cd web\n{c}",
    lambda c: f"{c} 2>&1",
    lambda c: f"{c} > out.log 2>&1",
    lambda c: f"CI=1 {c}",
    lambda c: f"env CI=1 {c}",
    lambda c: f"time {c}",
    lambda c: f"timeout 120 {c}",
    lambda c: f"({c})",
    lambda c: f"pnpm install && {c}",
    lambda c: f"echo start; {c}",
    lambda c: f"{c} && echo ok",
    lambda c: f"set -o pipefail; {c} | tail -20",
]


def _all_forms(forms, checks=CHECKS):
    return [form(c) for form in forms for c in checks]


def test_hides_exit_status() -> None:
    """11 checks x 14 hiding forms = 154 commands; none may count."""
    failing = [cmd for cmd in _all_forms(HIDES) if is_verify(cmd)]
    assert failing == [], f"{len(failing)} commands incorrectly counted"


def test_keeps_exit_status() -> None:
    """11 checks x 13 keeping forms = 143 commands; all must count."""
    failing = [cmd for cmd in _all_forms(KEEPS) if not is_verify(cmd)]
    assert failing == [], f"{len(failing)} commands incorrectly not counted"


# ---------------------------------------------------------------------------
# Override (test/checks.test.ts:133-136)
# ---------------------------------------------------------------------------
def test_override_replaces_defaults() -> None:
    assert is_verify("pnpm test", patterns=["^just check$"]) is False
    assert is_verify("just check", patterns=["^just check$"]) is True


# ---------------------------------------------------------------------------
# Pipefail-feeding config test (test/checks.test.ts:238-242)
# ---------------------------------------------------------------------------
def test_pipefail_with_config() -> None:
    config = ["^npm test$"]
    assert is_verify("set -o pipefail; npm test | tail -5", patterns=config) is True
    assert (
        with_pipefail("npm test | tail -5", patterns=config)
        == "set -o pipefail && npm test | tail -5"
    )


# ---------------------------------------------------------------------------
# Our additions (not from Canny's test tables)
# ---------------------------------------------------------------------------

def test_leading_spaces_do_not_count() -> None:
    # Canny's own comment at checks.ts:33-34 names leading whitespace as a past
    # bypass: ``   echo tsc`` should not count.
    assert is_verify("   echo tsc") is False


def test_pipefail_does_not_excuse_or_true() -> None:
    # Coordinator touch at landing (kills M5). Without pipefail the pipe rule
    # already refuses ``||`` (it contains ``|``); only a pipefail command
    # exercises the ``||`` rule itself. Canny's own tables have no such row.
    assert is_verify("set -o pipefail; pnpm test || true") is False


def test_quoted_check_name_after_a_non_print_word() -> None:
    # Coordinator touch at landing (kills M1). Quote removal matters only when
    # the first word is not a print/inspect command, as in these two rows.
    assert is_verify('python -c "import pytest"') is False
    assert is_verify("true 'npm test'") is False


def test_nbsp_before_help_does_not_trigger_asks_only() -> None:
    # U+00A0 (NBSP) is not matched by ``\\s`` under re.ASCII.  So
    # ``tsc --help`` is NOT caught by ASKS_ONLY and therefore counts.
    assert is_verify("tsc --help") is True


def test_with_pipefail_returns_none_for_head() -> None:
    # Only ``tail`` qualifies; ``head`` quits early and SIGPIPEs the check.
    assert with_pipefail("npm test | head -5") is None


def test_with_pipefail_returns_none_when_already_counts() -> None:
    assert with_pipefail("npm test") is None


def test_invalid_pattern_raises_value_error() -> None:
    with pytest.raises(ValueError, match="invalid pattern"):
        is_verify("npm test", patterns=["(unclosed"])


def test_cli_counts(tmp_path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--", "npm test"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "counts"


def test_cli_does_not_count(tmp_path) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--", "echo hello"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout.strip() == "does-not-count"


def test_cli_usage_error_no_dashdash() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "npm test"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert result.stderr.strip() != ""


def test_cli_usage_error_empty_command() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert result.stderr.strip() != ""


def test_cli_usage_error_invalid_pattern() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--pattern", "(bad", "--", "npm test"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert result.stderr.strip() != ""


def test_cli_with_pipefail() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--with-pipefail", "--", "npm test | tail -5"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "set -o pipefail && npm test | tail -5"


def test_cli_with_pipefail_no_effect() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--with-pipefail", "--", "npm test"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout.strip() == ""
