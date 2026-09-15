from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

import pytest

from agent_factory.governance.packet import (
    Packet,
    compile_canonical,
    governance_hash,
    lint_sources,
    load_packet,
)
from agent_factory.governance.pin import GovernanceError, verify_pinned_fubuki

LOCK = Path(__file__).resolve().parents[1] / "upstream.lock.yaml"
FIXTURES = Path(__file__).parent / "fixtures" / "governance"
PACKAGE = FIXTURES / "package"
SOURCE_FILES = (
    "compile-request.json",
    "core/doctrine.md",
    "core/persona.md",
    "examples/gold.jsonl",
    "modes/strategy.md",
)


@pytest.fixture(autouse=True)
def pinned_fubuki():
    """The declared input FUBUKI_OS_ROOT reaches the tests ONLY through the production pin.

    Bare (no PYTHONPATH) this suite was red on 2026-09-15: the upstream had been reachable
    only through an ambient path the lane's shell carried — a hidden test input.
    """
    value = os.environ.get("FUBUKI_OS_ROOT")
    if not value:
        pytest.fail("FUBUKI_OS_ROOT is a declared GOV1 test input")
    return verify_pinned_fubuki(Path(value).resolve(), LOCK)


def _rehash_manifest(root: Path) -> None:
    manifest_path = root / "persona.package.json"
    manifest = json.loads(manifest_path.read_text())
    for entry in manifest["files"]:
        entry["sha256"] = "sha256:" + hashlib.sha256(
            (root / entry["path"]).read_bytes()
        ).hexdigest()
    constitution = next(
        entry for entry in manifest["files"] if entry["role"] == "constitution"
    )
    manifest["core_hash"] = constitution["sha256"]
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def test_lint_exit_semantics() -> None:
    assert lint_sources(FIXTURES / "clean.txt").exit_code == 0
    assert lint_sources(FIXTURES / "review-only.txt").exit_code == 2
    result = lint_sources(FIXTURES / "ordered-review-then-violation.txt")
    assert result.exit_code == 1
    assert [finding[0] for finding in result.findings] == [
        "REVIEW",
        "VIOLATION",
        "VIOLATION",
    ]


def test_compile_is_canonical_and_hash_is_exact_sha256(tmp_path: Path) -> None:
    first = compile_canonical(PACKAGE)
    second = compile_canonical(PACKAGE)
    assert first == second
    assert governance_hash(first) == hashlib.sha256(first).hexdigest()

    first_object = json.loads(first)
    reordered_object = {key: first_object[key] for key in reversed(first_object)}
    reordered_bytes = json.dumps(
        reordered_object, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode()
    assert reordered_bytes == first
    assert governance_hash(reordered_bytes) == governance_hash(first)

    permuted = tmp_path / "permuted"
    shutil.copytree(PACKAGE, permuted)
    manifest_path = permuted / "persona.package.json"
    manifest = json.loads(manifest_path.read_text())
    manifest_path.write_text(json.dumps(manifest, sort_keys=False) + "\n")
    assert compile_canonical(permuted) == first


@pytest.mark.parametrize("relative", SOURCE_FILES)
def test_each_source_byte_changes_hash(tmp_path: Path, relative: str) -> None:
    changed = tmp_path / relative.replace("/", "-")
    shutil.copytree(PACKAGE, changed)
    source = changed / relative
    source.write_bytes(source.read_bytes() + b" ")
    _rehash_manifest(changed)
    assert governance_hash(compile_canonical(changed)) != governance_hash(
        compile_canonical(PACKAGE)
    )


def test_unreviewed_compiled_packet_refuses_readiness() -> None:
    with pytest.raises(GovernanceError, match="^fubuki-packet-unreviewed$"):
        load_packet(PACKAGE)


def test_packet_is_frozen() -> None:
    packet = Packet(b"{}", governance_hash(b"{}"), False)
    with pytest.raises(AttributeError):
        packet.reviewed = True
