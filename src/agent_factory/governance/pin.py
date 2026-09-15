"""Verify the configured Fubuki checkout before importing it."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


class GovernanceError(RuntimeError):
    """A fail-closed governance boundary refusal with a stable reason."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        self.detail = detail
        message = reason if not detail else f"{reason}: {detail}"
        super().__init__(message)


@dataclass(frozen=True)
class PinnedFubuki:
    root: Path
    commit: str


def _git(root: Path, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GovernanceError("fubuki-git-unavailable", str(exc)) from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        raise GovernanceError("fubuki-git-failed", detail)
    return completed.stdout.strip()


def _locked_commit(lock_path: Path) -> str:
    try:
        data = yaml.safe_load(lock_path.read_text(encoding="utf-8"))
        commit = data["selected_core"]["fubuki-os"]["commit"]
    except (OSError, KeyError, TypeError, yaml.YAMLError) as exc:
        raise GovernanceError("fubuki-lock-invalid", str(exc)) from exc
    if not isinstance(commit, str) or len(commit) != 40:
        raise GovernanceError("fubuki-lock-invalid", "commit must be a 40-character string")
    return commit


def verify_pinned_fubuki(root: str | Path, lock_path: str | Path) -> PinnedFubuki:
    """Fail closed unless root is the clean commit named by the lock file."""
    root = Path(root).resolve()
    package_src = root / "src" / "fubuki_os"
    if not package_src.is_dir():
        raise GovernanceError("fubuki-source-missing", str(package_src))

    expected = _locked_commit(Path(lock_path))
    actual = _git(root, "rev-parse", "HEAD")
    if actual != expected:
        raise GovernanceError(
            "fubuki-commit-mismatch", f"expected {expected}, found {actual}"
        )
    if _git(root, "status", "--porcelain"):
        raise GovernanceError("fubuki-tree-dirty", str(root))

    # The verified checkout supplies TWO import roots: `src/` (the `fubuki_os` package) and the
    # repository root (the `lint` package — persona_lint lives beside `src/`, not inside it).
    # Each is inserted once; nothing else may put an upstream on the path (a bare suite proved
    # 12 tests green only through an ambient PYTHONPATH — the hidden-input hollow green).
    for entry in (str(root), str(root / "src")):
        if entry not in sys.path:
            sys.path.insert(0, entry)
    return PinnedFubuki(root=root, commit=actual)
