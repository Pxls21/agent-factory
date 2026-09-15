from __future__ import annotations

import json
import os
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from agent_factory.governance.packet import Packet, governance_hash
from agent_factory.governance.pin import GovernanceError
from agent_factory.governance.projection import (
    GovernanceProjection,
    project,
    read_projection,
    write_projection,
)


def _packet() -> Packet:
    compiled = {
        "package_id": "synthia@0.0.1",
        "core_hash": "sha256:core",
        "mode": "strategy",
        "register": "conversational",
        "resident_kernel": "resident text",
        "mode_manifest": "mode text",
        "hard_constraints": ["one"],
        "output_contract": {"register": "conversational"},
        "bounded_context": [{"claim": "must not project"}],
        "selected_examples": [{"text": "must not project"}],
        "reviewed": True,
    }
    canonical = json.dumps(
        compiled, sort_keys=True, separators=(",", ":")
    ).encode()
    return Packet(canonical, governance_hash(canonical), True)


def test_projection_is_deeply_immutable_and_selective() -> None:
    packet = _packet()
    projection = project(packet)
    assert projection.governance_hash == governance_hash(packet.canonical)
    assert projection.bootstrap == "resident text\n\nmode text"
    assert "bounded_context" not in projection.metadata
    assert "selected_examples" not in projection.metadata
    with pytest.raises(TypeError):
        projection.metadata["mode"] = "mutated"
    with pytest.raises(TypeError):
        projection.metadata["output_contract"]["register"] = "mutated"
    with pytest.raises(FrozenInstanceError):
        projection.bootstrap = "mutated"


def test_projection_round_trip_and_tamper_detection(tmp_path: Path) -> None:
    packet = _packet()
    expected = project(packet)
    path = tmp_path / "projection.json"
    write_projection(expected, path)
    actual = read_projection(path, packet.hash)
    assert actual == expected

    raw = bytearray(path.read_bytes())
    target = raw.index(b"resident")
    raw[target] = ord("R")
    path.write_bytes(raw)
    with pytest.raises(GovernanceError, match="^projection-tampered$"):
        read_projection(path, packet.hash)


def test_projection_refuses_hash_mismatch_and_existing_path(tmp_path: Path) -> None:
    projection = project(_packet())
    path = tmp_path / "projection.json"
    write_projection(projection, path)
    with pytest.raises(GovernanceError, match="^governance-hash-mismatch$"):
        read_projection(path, "0" * 64)
    with pytest.raises(GovernanceError, match="^projection-create-refused"):
        write_projection(projection, path)


def test_projection_refuses_symlink_before_write(tmp_path: Path, monkeypatch) -> None:
    projection = project(_packet())
    target = tmp_path / "target"
    target.write_text("unchanged")
    link = tmp_path / "projection"
    link.symlink_to(target)
    real_open = os.open
    seen_flags: list[int] = []

    def observing_open(path, flags, mode=0o777):
        seen_flags.append(flags)
        return real_open(path, flags, mode)

    monkeypatch.setattr(os, "open", observing_open)
    with pytest.raises(GovernanceError, match="^projection-create-refused"):
        write_projection(projection, link)
    assert seen_flags and seen_flags[0] & os.O_EXCL
    assert seen_flags[0] & os.O_NOFOLLOW
    assert target.read_text() == "unchanged"


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO unsupported")
def test_projection_refuses_fifo_without_blocking(tmp_path: Path) -> None:
    projection = project(_packet())
    fifo = tmp_path / "projection.fifo"
    os.mkfifo(fifo)
    with pytest.raises(GovernanceError, match="^projection-create-refused"):
        write_projection(projection, fifo)
    with pytest.raises(GovernanceError, match="^projection-not-regular"):
        read_projection(fifo, projection.governance_hash)


def test_project_refuses_mutated_packet_identity() -> None:
    packet = _packet()
    bad = Packet(packet.canonical + b" ", packet.hash, True)
    with pytest.raises(GovernanceError, match="^governance-hash-mismatch$"):
        project(bad)


def test_projection_document_hash_covers_every_byte(tmp_path: Path) -> None:
    projection = GovernanceProjection("a" * 64, "text", {"nested": {"x": 1}})
    path = tmp_path / "projection.json"
    write_projection(projection, path)
    raw = json.loads(path.read_bytes())
    raw["metadata"]["nested"]["x"] = 2
    path.write_text(json.dumps(raw))
    with pytest.raises(GovernanceError, match="^projection-tampered$"):
        read_projection(path, projection.governance_hash)
