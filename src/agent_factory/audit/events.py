"""Minimal common audit envelope and fail-closed JSONL sink."""

from __future__ import annotations

import json
import os
import stat
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


class AuditError(RuntimeError):
    """An invalid event or unsafe audit sink path."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        message = reason if not detail else f"{reason}: {detail}"
        super().__init__(message)


@dataclass(frozen=True)
class Event:
    ts: str
    kind: str
    reason: str
    correlation_id: str
    governance_hash: str
    fields: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise AuditError("audit-reason-required")
        if not all(
            isinstance(value, str) and value
            for value in (self.ts, self.kind, self.correlation_id, self.governance_hash)
        ):
            raise AuditError("audit-envelope-field-required")
        if not isinstance(self.fields, Mapping):
            raise AuditError("audit-fields-invalid")
        object.__setattr__(self, "fields", MappingProxyType(dict(self.fields)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "ts": self.ts,
            "kind": self.kind,
            "reason": self.reason,
            "correlation_id": self.correlation_id,
            "governance_hash": self.governance_hash,
            "fields": dict(self.fields),
        }


class JsonlSink:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, event: Event) -> None:
        if not isinstance(event, Event):
            raise AuditError("audit-event-invalid")
        try:
            payload = json.dumps(
                event.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8") + b"\n"
        except (TypeError, ValueError) as exc:
            raise AuditError("audit-event-not-json", str(exc)) from exc

        flags = (
            os.O_WRONLY
            | os.O_CREAT
            | os.O_APPEND
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0)
        )
        try:
            fd = os.open(self.path, flags, 0o600)
        except OSError as exc:
            raise AuditError("audit-sink-open-refused", str(exc)) from exc
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise AuditError("audit-sink-not-regular", str(self.path))
            written = os.write(fd, payload)
            if written != len(payload):
                raise AuditError("audit-sink-short-write")
            os.fsync(fd)
        finally:
            os.close(fd)
