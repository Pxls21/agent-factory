"""Verify the configured Fubuki checkout before importing it."""

from __future__ import annotations

import importlib
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


# The top-level upstream packages the verified checkout supplies (src/fubuki_os and lint/).
# No effectful governance path may reach an upstream module that did not come from the active pin.
_UPSTREAM_TOP = ("fubuki_os", "lint")

# The pin verified for THIS interpreter. Written once by verify_pinned_fubuki, read by
# import_pinned; module state, never a config channel (no env, no caller may set it).
_ACTIVE_PIN: PinnedFubuki | None = None


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

    # An upstream module already imported into THIS interpreter from OUTSIDE the verified root
    # would win over the clean path insert below (sys.modules is consulted before sys.path), so a
    # dirty pre-import survives a later clean verify. Refuse fail-closed — verify from a clean
    # interpreter (VERIFY-GOV1 F1, probe v1f).
    foreign = _foreign_preimports(root)
    if foreign:
        raise GovernanceError("fubuki-preimported-foreign", ",".join(foreign))

    # The verified checkout supplies TWO import roots: `src/` (the `fubuki_os` package) and the
    # repository root (the `lint` package — persona_lint lives beside `src/`, not inside it).
    # Each is inserted once; nothing else may put an upstream on the path (a bare suite proved
    # 12 tests green only through an ambient PYTHONPATH — the hidden-input hollow green).
    for entry in (str(root), str(root / "src")):
        if entry not in sys.path:
            sys.path.insert(0, entry)
    global _ACTIVE_PIN
    _ACTIVE_PIN = PinnedFubuki(root=root, commit=actual)
    return _ACTIVE_PIN


def _foreign_preimports(root: Path) -> list[str]:
    """Upstream modules already in sys.modules whose file is NOT under the verified root."""
    foreign: list[str] = []
    for name, module in list(sys.modules.items()):
        if name.split(".", 1)[0] not in _UPSTREAM_TOP:
            continue
        file = getattr(module, "__file__", None)
        if file is None:
            continue
        try:
            resolved = Path(file).resolve()
        except OSError:
            foreign.append(name)
            continue
        if not resolved.is_relative_to(root):
            foreign.append(name)
    return sorted(foreign)


def import_pinned(module_name: str):
    """Import an upstream module bound to the active verified pin, or fail closed.

    Closes VERIFY-GOV1 F1: `verify_pinned_fubuki` inserts the clean path, but sys.modules wins over
    sys.path, so an already-cached dirty module survives; and a caller that skipped verification
    reaches the upstream with no pin proof. Every effectful governance path imports through here, so
    the pin is enforced AT USE — no active pin refuses `fubuki-pin-not-verified`; a module resolved
    from outside the pinned root (a cached foreign module) refuses `fubuki-import-foreign`.
    """
    pin = _ACTIVE_PIN
    if pin is None:
        raise GovernanceError("fubuki-pin-not-verified", module_name)
    module = importlib.import_module(module_name)
    file = getattr(module, "__file__", None)
    try:
        resolved = Path(file).resolve() if file is not None else None
    except OSError:
        resolved = None
    if resolved is None or not resolved.is_relative_to(pin.root):
        raise GovernanceError("fubuki-import-foreign", f"{module_name}:{file}")
    return module
