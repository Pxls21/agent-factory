from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agent_factory.audit.events import AuditError, Event, JsonlSink


def _event(**changes) -> Event:
    values = {
        "ts": "2026-09-15T14:00:00Z",
        "kind": "governance.bound.denied",
        "reason": "status:proposed",
        "correlation_id": "request-1",
        "governance_hash": "a" * 64,
        "fields": {"record_id": "r1", "rule": "status"},
    }
    values.update(changes)
    return Event(**values)


def test_event_requires_reason() -> None:
    with pytest.raises(AuditError, match="^audit-reason-required$"):
        _event(reason="")


def test_jsonl_sink_round_trips_and_appends(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    sink = JsonlSink(path)
    sink.append(_event())
    sink.append(_event(correlation_id="request-2"))
    records = [json.loads(line) for line in path.read_text().splitlines()]
    assert [record["correlation_id"] for record in records] == [
        "request-1",
        "request-2",
    ]
    assert all(record["reason"] for record in records)


def test_jsonl_sink_refuses_symlink(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.write_text("unchanged")
    link = tmp_path / "audit.jsonl"
    link.symlink_to(target)
    with pytest.raises(AuditError, match="^audit-sink-open-refused"):
        JsonlSink(link).append(_event())
    assert target.read_text() == "unchanged"


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFO unsupported")
def test_jsonl_sink_refuses_fifo_without_blocking(tmp_path: Path) -> None:
    fifo = tmp_path / "audit.fifo"
    os.mkfifo(fifo)
    with pytest.raises(
        AuditError, match="^audit-sink-(open-refused|not-regular)"
    ):
        JsonlSink(fifo).append(_event())
