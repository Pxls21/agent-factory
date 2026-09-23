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
    # bypass: ``   echo tsc`` should not count.  The work is done by the
    # ``str.strip()`` calls on the segment, the ``&&``-part and the check, each
    # enough alone; the ``^\s*`` in _PRINTS_OR_INSPECTS never sees whitespace
    # (VERIFY-C1 F8).  The U+00A0 row aims at the strips: ``\s`` under re.ASCII
    # cannot match it, so only a strip removes it.
    assert is_verify("   echo tsc") is False
    assert is_verify("\xa0echo tsc") is False


def test_pipefail_does_not_excuse_or_true() -> None:
    # Coordinator touch at landing (killed M5). Without pipefail the pipe rule
    # already refuses ``||`` (it contains ``|``); only a pipefail command
    # exercises the ``||`` rule itself. Canny's own tables have no such row.
    # Since C1-R1, rule (a) refuses the ``||`` first, so this row goes red
    # only when both rule (a) and the per-part rule (checks.ts:69) are gone.
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
    # Two argv words the option loop consumes, so the parser reaches the
    # missing ``--`` check (VERIFY-C1 F11).  ``"npm", "test"`` would not: the
    # loop stops at ``unknown option: npm``.
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--pattern", "^npm test$"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert result.stderr == "missing -- before COMMAND\n"


def test_cli_usage_error_unknown_option() -> None:
    # The argv the no-dashdash test used before C1-R1: it reaches this branch.
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "npm test"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert result.stderr == "unknown option: npm test\n"


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


# ---------------------------------------------------------------------------
# C1-R1 (task #159): the one repair of VERIFY-C1.  Ours, not Canny's.
# ---------------------------------------------------------------------------

def _one_stderr_line(result) -> bool:
    return result.stderr.count("\n") == 1 and result.stderr.strip() != ""


# R1 (F2): re.ASCII on every regex.  One row per flag that changes an answer;
# the flags on the quoted-string strip, the segment split and the lone-``&``
# test are inert (those patterns hold no \b, \w, \s or \d).
def test_ascii_pipefail_scan_refuses_nbsp_in_set() -> None:
    # H3: bash reads ``set\xa0-o`` as one word ("command not found") and never
    # sets pipefail, so ``| tail`` hides the check.
    assert is_verify("set\xa0-o pipefail; pnpm test | tail") is False


def test_ascii_pipefail_scan_refuses_nbsp_in_set_cli() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--", "set\xa0-o pipefail; pnpm test | tail"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert result.stdout == "does-not-count\n"


def test_ascii_comment_strip_keeps_nbsp_hash() -> None:
    # bash starts a comment only at a word start, and NBSP does not end a
    # word: ``pytest\xa0#`` is one word and ``exit 0`` runs.  A Unicode ``\s``
    # would drop ``#; exit 0`` as a comment and count the command.
    assert is_verify("pytest\xa0#; exit 0") is False


def test_ascii_tail_test_needs_an_ascii_space_before_tail() -> None:
    # ``|\xa0tail`` pipes into a command named ``\xa0tail``, not into tail.
    assert with_pipefail("npm test |\xa0tail -5") is None


# R2: AMENDMENT C1-A2 (a)-(e).  Every row counted before C1-R1 while bash
# exited 0 with the check failing.
@pytest.mark.parametrize(
    "cmd",
    [
        "pytest && false || true",
        "pytest && echo ok || true",
        "trap 'exit 0' EXIT; pytest",
        "set -o pipefail\r\npnpm test | tail",
        "echo \\\npytest",
        "exec true; pytest",
        "coproc pytest",
    ],
    ids=["a_H1", "a_H1b", "b_H2", "c_H4", "d_H5", "e_H6", "e_H6b"],
)
def test_c1_a2_refuses_status_hiding_shapes(cmd: str) -> None:
    assert is_verify(cmd) is False


def test_invalid_pattern_raises_even_when_c1_a2_refuses() -> None:
    # The C1-A2 rules run after the patterns compile, so deviation 1 holds.
    with pytest.raises(ValueError, match="invalid pattern"):
        is_verify("pytest || true", patterns=["(unclosed"])


# R3: the declared limits, one per example in the module docstring.  Each
# asserts the SAFE answer; strict=True turns a fix into an XPASS failure,
# which forces the docstring update.
def _declared_limit(reason: str):
    # Strict, and only an AssertionError counts as the expected failure.
    return pytest.mark.xfail(strict=True, raises=AssertionError, reason=reason)


@_declared_limit("H7: a builtin swallows the status")
def test_limit_h7_builtin_swallows_status() -> None:
    assert is_verify("export R=$(pytest)") is False


@_declared_limit("H8: a function shadows the check")
def test_limit_h8_function_shadows_check() -> None:
    assert is_verify("pytest(){ return 0; }; pytest") is False


@_declared_limit("H9: a path bypasses the denylist")
def test_limit_h9_path_bypasses_denylist() -> None:
    assert is_verify("/bin/echo tsc") is False


@_declared_limit("a here-doc terminator reads as a command")
def test_limit_heredoc_terminator() -> None:
    assert is_verify("cat <<'pytest'\nfoo\npytest") is False


@_declared_limit("(b) and (e) see only segment starts")
def test_limit_trap_after_and() -> None:
    assert is_verify("true && trap 'exit 0' EXIT; pytest") is False


@_declared_limit("with_pipefail moves trap off a segment start")
def test_limit_with_pipefail_rewrites_trap() -> None:
    assert with_pipefail("trap 'exit 0' EXIT; pytest | tail") is None


@_declared_limit("pipefail\\b passes a kept character")
def test_limit_pipefail_option_word_suffix() -> None:
    assert is_verify("set -o pipefail-x; pnpm test | tail") is False


@_declared_limit("the cost of re.ASCII on the pipefail scan")
def test_limit_pipefail_non_ascii_suffix() -> None:
    assert is_verify("set -o pipefailé; pnpm test | tail") is False


# R4 (F3): rows for VERIFY-C1's surviving mutants, pinning today's answers.
@pytest.mark.parametrize(
    "cmd, patterns, expected",
    [
        ("npm testé", None, True),
        ("set -o pipefail; npm test | grep -- --help", None, True),
        ("pnpm test", [], False),
        ("echo set -o pipefail; pnpm test | tail", None, False),
    ],
    ids=["N5_ascii_verify", "N10_not_a_check_arg", "N11_empty_patterns", "N13_set_anchor"],
)
def test_verify_c1_survivors(cmd, patterns, expected) -> None:
    assert is_verify(cmd, patterns) is expected


# R5-R7 (F4-F6): the CLI refusals, each exit 2 with one stderr line.
def test_cli_refuses_more_than_one_command_word() -> None:
    # The caller's shell already removed the quotes executed() relies on:
    # joined, these three words counted (VERIFY-C1 F4).
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--", "python", "-c", "import pytest"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert _one_stderr_line(result)


def test_cli_refuses_empty_pattern() -> None:
    # An empty regex matches every check (VERIFY-C1 F5).
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--pattern", "", "--", "make build"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert _one_stderr_line(result)


def test_cli_with_pipefail_encoding_failure_exits_2() -> None:
    # A non-UTF-8 argv byte decodes to a surrogate, which a strict stdout
    # cannot write.  Exit 1 would read as "no rewrite" (VERIFY-C1 F6).
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--with-pipefail", "--", b"\xffnpm test | tail -5"],
        capture_output=True,
        text=True,
        env={"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8:strict"},
    )
    assert result.returncode == 2
    assert result.stdout == ""
    assert _one_stderr_line(result)
