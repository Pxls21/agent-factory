from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from agent_factory.governance.bounds import bound_records
from agent_factory.governance.packet import Packet
from agent_factory.governance.pin import GovernanceError, verify_pinned_fubuki

LOCK = Path(__file__).resolve().parents[1] / "upstream.lock.yaml"


@pytest.fixture(autouse=True)
def pinned_fubuki():
    """The declared input FUBUKI_OS_ROOT reaches the tests ONLY through the production pin."""
    value = os.environ.get("FUBUKI_OS_ROOT")
    if not value:
        pytest.fail("FUBUKI_OS_ROOT is a declared GOV1 test input")
    return verify_pinned_fubuki(Path(value).resolve(), LOCK)


def _record(record_id: str, status: str):
    from fubuki_os.memory.models import MemoryRecord

    return MemoryRecord(
        record_id=record_id,
        record_type="fact",
        claim=f"claim {record_id}",
        branch="main",
        provenance_class="operator_stated",
        confidence="high",
        created_at="2026-01-01T00:00:00Z",
        status=status,
    )


def _packet() -> Packet:
    return Packet(b"{}", "a" * 64, True)


def test_bound_join_keeps_source_identity_and_denial_reason() -> None:
    approved = _record("allowed", "approved")
    denied = _record("denied", "proposed")
    result = bound_records(
        [approved, denied],
        _packet(),
        at="2026-06-01T00:00:00Z",
        correlation_id="request-1",
    )
    assert result.kept == (approved,)
    assert result.kept[0] is approved
    assert result.denials[0].record_id == "denied"
    assert result.denials[0].rule == "status"
    assert "only approved records load" in result.denials[0].reasons[0]
    assert [event.kind for event in result.events] == [
        "governance.bound.allowed",
        "governance.bound.denied",
    ]
    assert all(event.governance_hash == _packet().hash for event in result.events)
    assert all(event.reason for event in result.events)


def test_bound_join_never_reads_planted_decision_payload(monkeypatch) -> None:
    import fubuki_os.memory.bounds as upstream

    source = _record("allowed", "approved")
    decision = SimpleNamespace(
        record_id="allowed",
        allowed=True,
        rejection_reasons=(),
        payload={"attacker": "must-not-appear"},
    )
    monkeypatch.setattr(upstream, "evaluate_records", lambda records, **context: ([decision], []))
    result = bound_records([source], _packet())
    assert result.kept[0] is source
    assert result.kept[0] is not decision.payload
    assert "attacker" not in repr(result)


def test_bound_join_refuses_decision_without_source(monkeypatch) -> None:
    import fubuki_os.memory.bounds as upstream

    source = _record("present", "approved")
    decisions = [
        SimpleNamespace(record_id="present", allowed=True, rejection_reasons=()),
        SimpleNamespace(record_id="absent", allowed=True, rejection_reasons=()),
    ]
    monkeypatch.setattr(
        upstream, "evaluate_records", lambda records, **context: (decisions, [])
    )
    with pytest.raises(GovernanceError, match="^bound-decision-source-missing"):
        bound_records([source, replace(source, record_id="second")], _packet())


def test_bound_join_refuses_duplicate_source_id() -> None:
    source = _record("same", "approved")
    with pytest.raises(GovernanceError, match="^bound-source-id-duplicate"):
        bound_records([source, replace(source)], _packet())
