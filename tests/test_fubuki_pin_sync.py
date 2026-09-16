"""`scripts/fubuki_pin_sync.sh` — the pinned fubuki-os checkout as a DECLARED input on every venue.

GOV1's landing (2026-09-15): twelve governance tests were green on the PC only through the lane shell's PYTHONPATH
(AF-AP-81). The sync script provisions `DEST/fubuki-os` at the lock's commit and `DEST/fubuki-os-other` (one empty
commit on top, the identical tree) as the negative control, idempotently, and refuses drift by name instead of
resetting it. Offline here: the SOURCE is the venue's own pinned checkout (`FUBUKI_OS_ROOT`, a declared input).
The provisioned roots are graded by the CONSUMER, `verify_pinned_fubuki`, not only by git.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
import yaml

from agent_factory.governance.pin import GovernanceError, verify_pinned_fubuki

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fubuki_pin_sync.sh"
LOCK = ROOT / "upstream.lock.yaml"
LOCK_COMMIT = yaml.safe_load(LOCK.read_text(encoding="utf-8"))["selected_core"]["fubuki-os"]["commit"]


@pytest.fixture
def source() -> Path:
    value = os.environ.get("FUBUKI_OS_ROOT")
    if not value:
        pytest.fail("FUBUKI_OS_ROOT is a declared input (the offline clone source of this test)")
    return Path(value).resolve()


def _sync(dest: Path, source: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), str(dest), str(source)], capture_output=True, text=True, timeout=180, check=False
    )


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


def _roots(result: subprocess.CompletedProcess[str]) -> tuple[Path, Path]:
    lines = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    return Path(lines["FUBUKI_OS_ROOT"]), Path(lines["FUBUKI_OTHER_ROOT"])


def test_provisions_the_pin_and_the_negative_control_idempotently(tmp_path: Path, source: Path) -> None:
    first = _sync(tmp_path / "pin", source)
    assert first.returncode == 0, first.stderr
    pin, other = _roots(first)
    assert _git(pin, "rev-parse", "HEAD") == LOCK_COMMIT
    assert _git(pin, "status", "--porcelain") == ""
    assert (pin / "src" / "fubuki_os").is_dir()
    assert (pin / "lint" / "persona_lint.py").is_file()
    other_head = _git(other, "rev-parse", "HEAD")
    assert other_head != LOCK_COMMIT
    assert _git(other, "rev-parse", "HEAD^") == LOCK_COMMIT
    assert _git(other, "rev-parse", "HEAD^{tree}") == _git(pin, "rev-parse", "HEAD^{tree}")
    assert _git(other, "status", "--porcelain") == ""
    # the consumer's verdicts, not only git's
    assert verify_pinned_fubuki(pin, LOCK).commit == LOCK_COMMIT
    with pytest.raises(GovernanceError, match="^fubuki-commit-mismatch"):
        verify_pinned_fubuki(other, LOCK)
    # idempotent: a second run verifies and changes nothing (no second empty commit)
    second = _sync(tmp_path / "pin", source)
    assert second.returncode == 0, second.stderr
    assert second.stdout == first.stdout
    assert _git(other, "rev-parse", "HEAD") == other_head


def test_a_dirty_pin_is_a_finding_not_a_reset(tmp_path: Path, source: Path) -> None:
    assert _sync(tmp_path / "pin", source).returncode == 0
    readme = tmp_path / "pin" / "fubuki-os" / "README.md"
    original = readme.read_bytes()
    readme.write_bytes(b"drift\n" + original)
    result = _sync(tmp_path / "pin", source)
    assert result.returncode == 3
    assert "dirty" in result.stderr
    assert readme.read_bytes() == b"drift\n" + original  # untouched: no reset, no checkout


def test_a_moved_pin_is_named_by_commit(tmp_path: Path, source: Path) -> None:
    assert _sync(tmp_path / "pin", source).returncode == 0
    pin = tmp_path / "pin" / "fubuki-os"
    subprocess.run(
        ["git", "-C", str(pin), "-c", "user.name=x", "-c", "user.email=x@x.invalid",
         "commit", "-q", "--allow-empty", "-m", "moved"],
        check=True,
    )
    result = _sync(tmp_path / "pin", source)
    assert result.returncode == 3
    assert "commit-mismatch" in result.stderr


def test_a_source_without_the_pin_is_refused_and_leaves_nothing(tmp_path: Path, source: Path) -> None:
    empty = tmp_path / "empty-src"
    subprocess.run(["git", "init", "-q", str(empty)], check=True)
    subprocess.run(
        ["git", "-C", str(empty), "-c", "user.name=x", "-c", "user.email=x@x.invalid",
         "commit", "-q", "--allow-empty", "-m", "unrelated"],
        check=True,
    )
    result = _sync(tmp_path / "pin", empty)
    assert result.returncode == 3
    assert "commit-absent" in result.stderr
    assert not (tmp_path / "pin" / "fubuki-os").exists()


def test_the_sync_script_needs_no_dev_fd(  # review 2026-09-15: "every venue" must not rely on /dev/fd
) -> None:
    """The header promises the script runs on every venue. Process substitution `>(…)`/`<(…)` is bash's only
    /dev/fd dependency here (four tests failed where /dev/fd was absent); assert it is gone — the source-text half
    of the fix, paired with the behavioral controls below and the four provisioning tests above."""
    text = SCRIPT.read_text(encoding="utf-8")
    assert ">(" not in text, "output process substitution needs /dev/fd — not mounted on every venue"
    assert "<(" not in text, "input process substitution needs /dev/fd — not mounted on every venue"


def test_a_nonrepo_source_fails_loudly_and_keeps_gits_error(tmp_path: Path) -> None:
    """The portable clone filter must preserve git's exit code and its real stderr (only the benign 'shallow' note
    is dropped). A source that is not a repository makes `git clone` itself fail before any checkout — the failure
    and its message must surface, and the stderr tempfile must be cleaned up. No FUBUKI_OS_ROOT: the clone fails first."""
    dest = tmp_path / "pin"
    result = _sync(dest, tmp_path / "not-a-repo")  # nonexistent source → git clone fails at the first clone
    assert result.returncode != 0
    assert result.returncode != 3  # not a die-3 provisioning refusal — the clone itself failed, code preserved
    assert "does not exist" in result.stderr or "not a git repository" in result.stderr
    assert list(dest.glob(".fubuki-clone-stderr.*")) == []  # the stderr tempfile is removed even on failure
