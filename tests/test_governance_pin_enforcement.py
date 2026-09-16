"""GOV2a — the pinned-source contract is enforced AT the production API (VERIFY-GOV1 F1).

Three escape paths the verifier reproduced on GOV1, now red controls:
  V1  an effectful path called with NO active pin reaches the upstream       -> fubuki-pin-not-verified
  V2  a dirty/foreign upstream already imported survives a later clean verify -> fubuki-preimported-foreign
  V3  a foreign module injected into sys.modules AFTER verify wins at use     -> fubuki-import-foreign

The pin binds to the verified CHECKOUT (path), not just the code: the negative-control root carries the
identical tree one commit above the pin, so importing it and refusing is a provenance refusal, not a diff.
"""

from __future__ import annotations

import importlib
import os
import sys
import types
from pathlib import Path

import pytest

from agent_factory.governance import pin as pinmod
from agent_factory.governance.bounds import bound_records
from agent_factory.governance.packet import Packet, compile_canonical, governance_hash, lint_sources
from agent_factory.governance.pin import GovernanceError, import_pinned, verify_pinned_fubuki

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "upstream.lock.yaml"
FIXTURES = ROOT / "tests" / "fixtures" / "governance"
PACKAGE = FIXTURES / "package"
_UPSTREAM = ("fubuki_os", "lint")


def _upstream_modules() -> list[str]:
    return [name for name in list(sys.modules) if name.split(".", 1)[0] in _UPSTREAM]


@pytest.fixture(autouse=True)
def restore_process_state():
    """Snapshot and restore the module pin, upstream sys.modules, and sys.path each test perturbs."""
    saved_pin = pinmod._ACTIVE_PIN
    saved_modules = {name: sys.modules[name] for name in _upstream_modules()}
    saved_path = list(sys.path)
    try:
        yield
    finally:
        pinmod._ACTIVE_PIN = saved_pin
        for name in _upstream_modules():
            sys.modules.pop(name, None)
        sys.modules.update(saved_modules)
        sys.path[:] = saved_path


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


def _dummy_packet() -> Packet:
    return Packet(b"{}", governance_hash(b"{}"), True)


# --- V1: no active pin -> every effectful path refuses before touching the upstream --------------


def test_compile_canonical_without_verify_refuses() -> None:
    pinmod._ACTIVE_PIN = None
    with pytest.raises(GovernanceError, match="^fubuki-pin-not-verified"):
        compile_canonical(PACKAGE)


def test_lint_sources_without_verify_refuses() -> None:
    pinmod._ACTIVE_PIN = None
    with pytest.raises(GovernanceError, match="^fubuki-pin-not-verified"):
        lint_sources(FIXTURES / "clean.txt")


def test_bound_records_without_verify_refuses() -> None:
    pinmod._ACTIVE_PIN = None
    with pytest.raises(GovernanceError, match="^fubuki-pin-not-verified"):
        bound_records([], _dummy_packet())


# --- V2: a foreign upstream imported BEFORE verify makes verify itself fail closed ---------------


def test_foreign_preimport_refused_at_verify(fubuki_root: Path, other_fubuki_root: Path) -> None:
    for name in _upstream_modules():
        sys.modules.pop(name, None)
    sys.path.insert(0, str(other_fubuki_root / "src"))
    importlib.import_module("fubuki_os")
    assert Path(sys.modules["fubuki_os"].__file__).resolve().is_relative_to(other_fubuki_root)
    with pytest.raises(GovernanceError, match="^fubuki-preimported-foreign"):
        verify_pinned_fubuki(fubuki_root, LOCK)


# --- V3: a foreign module injected AFTER a clean verify is caught at USE, not just at path-insert -


def test_foreign_module_injected_after_verify_refused_at_use(fubuki_root: Path, tmp_path: Path) -> None:
    verify_pinned_fubuki(fubuki_root, LOCK)
    poison = types.ModuleType("fubuki_os.memory.bounds")
    poison.__file__ = str(tmp_path / "evil.py")
    poison.evaluate_records = lambda *a, **k: ([], [])  # never reached
    sys.modules["fubuki_os.memory.bounds"] = poison
    with pytest.raises(GovernanceError, match="^fubuki-import-foreign"):
        bound_records([], _dummy_packet())


# --- positive controls: the guard does not break the happy path ---------------------------------


def test_import_pinned_returns_module_under_the_pinned_root(fubuki_root: Path) -> None:
    pinned = verify_pinned_fubuki(fubuki_root, LOCK)
    module = import_pinned("fubuki_os.memory.bounds")
    assert Path(module.__file__).resolve().is_relative_to(pinned.root)


def test_compile_canonical_still_works_after_verify(fubuki_root: Path) -> None:
    verify_pinned_fubuki(fubuki_root, LOCK)
    out = compile_canonical(PACKAGE)
    assert isinstance(out, bytes) and out
