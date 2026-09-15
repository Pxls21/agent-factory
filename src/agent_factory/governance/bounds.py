"""Join Fubuki bound decisions back to source records by stable ID."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from agent_factory.audit.events import Event, JsonlSink

from .packet import Packet
from .pin import GovernanceError


@dataclass(frozen=True)
class Denial:
    record_id: str
    reasons: tuple[str, ...]
    rule: str


@dataclass(frozen=True)
class BoundResult:
    kept: tuple[Any, ...]
    denials: tuple[Denial, ...]
    events: tuple[Event, ...]


def _rule(reasons: tuple[str, ...]) -> str:
    if not reasons:
        return "bounds:unspecified"
    return reasons[0].split(":", 1)[0]


def bound_records(
    records: Iterable[Any],
    packet: Packet,
    *,
    branch: str = "main",
    active_person: str = "operator",
    third_party_visible: bool = False,
    request_tags: tuple[str, ...] = (),
    at: str = "",
    correlation_id: str = "governance-bounds",
    sink: JsonlSink | None = None,
) -> BoundResult:
    """Evaluate each source record and join decisions by ``record_id`` only."""
    from fubuki_os.memory.bounds import evaluate_records

    source_records = tuple(records)
    by_id: dict[str, Any] = {}
    for record in source_records:
        record_id = getattr(record, "record_id", None)
        if not isinstance(record_id, str) or not record_id:
            raise GovernanceError("bound-source-id-invalid")
        if record_id in by_id:
            raise GovernanceError("bound-source-id-duplicate", record_id)
        by_id[record_id] = record

    allowed, rejected = evaluate_records(
        source_records,
        branch=branch,
        active_person=active_person,
        third_party_visible=third_party_visible,
        request_tags=request_tags,
        at=at,
    )
    decisions = tuple(allowed) + tuple(rejected)
    if len(decisions) != len(source_records):
        raise GovernanceError("bound-decision-count-mismatch")

    kept: list[Any] = []
    denials: list[Denial] = []
    events: list[Event] = []
    seen: set[str] = set()
    for decision in decisions:
        record_id = getattr(decision, "record_id", None)
        if record_id not in by_id:
            raise GovernanceError("bound-decision-source-missing", str(record_id))
        if record_id in seen:
            raise GovernanceError("bound-decision-id-duplicate", record_id)
        seen.add(record_id)

        reasons = tuple(getattr(decision, "rejection_reasons", ()))
        allowed_value = getattr(decision, "allowed", None)
        if type(allowed_value) is not bool:
            raise GovernanceError("bound-decision-invalid", record_id)
        reason = "bounds:allowed" if allowed_value else "; ".join(reasons)
        if not reason:
            raise GovernanceError("bound-decision-reason-missing", record_id)
        rule = "bounds:allow" if allowed_value else _rule(reasons)
        event = Event(
            ts=at or "unspecified",
            kind="governance.bound.allowed" if allowed_value else "governance.bound.denied",
            reason=reason,
            correlation_id=correlation_id,
            governance_hash=packet.hash,
            fields={"record_id": record_id, "rule": rule},
        )
        if sink is not None:
            sink.append(event)
        events.append(event)

        if allowed_value:
            kept.append(by_id[record_id])
        else:
            denials.append(Denial(record_id, reasons, rule))

    if seen != set(by_id):
        missing = sorted(set(by_id) - seen)
        raise GovernanceError("bound-decision-missing", ",".join(missing))
    return BoundResult(tuple(kept), tuple(denials), tuple(events))
