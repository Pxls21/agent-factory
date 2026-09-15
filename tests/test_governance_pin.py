from __future__ import annotations

import importlib
import os
import shutil
import sys
from pathlib import Path

import pytest

from agent_factory.governance.pin import GovernanceError, verify_pinned_fubuki

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "upstream.lock.yaml"


@pytest.fixture
def fubuki_root() -> Path:
    value = os.environ.get("FUBUKI_OS_ROOT")
    if not value:
        pytest.fail("FUBUKI_OS_ROOT is a declared GOV1 test input")
    return Path(value).resolve()


@pytest.fixture
def other_fubuki_root() -> Path:
    value = os.environ.get("FUBUKI_OTHER_ROOT")
    if not value:
        pytest.fail("FUBUKI_OTHER_ROOT is a declared GOV1 negative-control input")
    return Path(value).resolve()


def test_pinned_clean_checkout_passes_and_path_is_inserted_once(
    fubuki_root: Path,
) -> None:
    src = str(fubuki_root / "src")
    root = str(fubuki_root)
    sys.path[:] = [entry for entry in sys.path if entry not in (src, root)]
    pinned = verify_pinned_fubuki(fubuki_root, LOCK)
    again = verify_pinned_fubuki(fubuki_root, LOCK)
    assert pinned.commit == "7375e56d6a5dc857bfd43ceccbc09bbc817d575a"
    assert again == pinned
    assert sys.path.count(src) == 1
    assert sys.path.count(root) == 1


def test_pinned_upstream_modules_resolve_from_the_pinned_checkout(fubuki_root: Path) -> None:
    """`fubuki_os` (under src/) and `lint` (beside src/) both come from the verified root.

    Behavioral, not an inventory pin: the modules are imported and their files located.
    """
    src = str(fubuki_root / "src")
    root = str(fubuki_root)
    sys.path[:] = [entry for entry in sys.path if entry not in (src, root)]
    for name in ("fubuki_os", "lint", "lint.persona_lint"):
        sys.modules.pop(name, None)
    verify_pinned_fubuki(fubuki_root, LOCK)
    package = importlib.import_module("fubuki_os")
    linter = importlib.import_module("lint.persona_lint")
    assert Path(package.__file__).resolve().is_relative_to(fubuki_root / "src" / "fubuki_os")
    assert Path(linter.__file__).resolve() == (fubuki_root / "lint" / "persona_lint.py").resolve()


def test_other_commit_refuses_by_name(other_fubuki_root: Path) -> None:
    with pytest.raises(GovernanceError, match="^fubuki-commit-mismatch"):
        verify_pinned_fubuki(other_fubuki_root, LOCK)


def test_dirty_checkout_refuses_by_name(tmp_path: Path, fubuki_root: Path) -> None:
    dirty = tmp_path / "dirty"
    shutil.copytree(fubuki_root, dirty)
    (dirty / "README.md").write_bytes((dirty / "README.md").read_bytes() + b"dirty")
    with pytest.raises(GovernanceError, match="^fubuki-tree-dirty"):
        verify_pinned_fubuki(dirty, LOCK)


def test_missing_source_refuses_before_git(tmp_path: Path) -> None:
    with pytest.raises(GovernanceError, match="^fubuki-source-missing"):
        verify_pinned_fubuki(tmp_path, LOCK)


def test_invalid_lock_refuses(tmp_path: Path, fubuki_root: Path) -> None:
    lock = tmp_path / "lock.yaml"
    lock.write_text("selected_core: {}\n")
    with pytest.raises(GovernanceError, match="^fubuki-lock-invalid"):
        verify_pinned_fubuki(fubuki_root, lock)
