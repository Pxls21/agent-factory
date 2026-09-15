"""Immutable, tamper-evident bootstrap projection for Hermes."""

from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from .packet import Packet, governance_hash
from .pin import GovernanceError


@dataclass(frozen=True)
class GovernanceProjection:
    governance_hash: str
    bootstrap: str
    metadata: Mapping[str, Any]


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value


def project(packet: Packet) -> GovernanceProjection:
    """Project only Fubuki's runtime text and identity, not memory or examples."""
    try:
        compiled = json.loads(packet.canonical)
    except (TypeError, json.JSONDecodeError) as exc:
        raise GovernanceError("fubuki-packet-invalid", str(exc)) from exc
    actual_hash = governance_hash(packet.canonical)
    if actual_hash != packet.hash:
        raise GovernanceError("governance-hash-mismatch")
    if not packet.reviewed:
        raise GovernanceError("fubuki-packet-unreviewed")

    text_parts = [compiled.get("resident_kernel", ""), compiled.get("mode_manifest", "")]
    bootstrap = "\n\n".join(part for part in text_parts if part)
    metadata = _freeze(
        {
            "package_id": compiled.get("package_id"),
            "core_hash": compiled.get("core_hash"),
            "mode": compiled.get("mode"),
            "register": compiled.get("register"),
            "hard_constraints": compiled.get("hard_constraints", []),
            "output_contract": compiled.get("output_contract", {}),
        }
    )
    return GovernanceProjection(actual_hash, bootstrap, metadata)


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    return value


def _document(projection: GovernanceProjection) -> bytes:
    body = {
        "bootstrap": projection.bootstrap,
        "governance_hash": projection.governance_hash,
        "metadata": _plain(projection.metadata),
    }
    body_bytes = json.dumps(
        body, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    envelope = {
        **body,
        "projection_hash": hashlib.sha256(body_bytes).hexdigest(),
    }
    return json.dumps(
        envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _exclusive_flags() -> int:
    return (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )


def write_projection(projection: GovernanceProjection, path: str | Path) -> None:
    """Create one immutable projection file without following special paths."""
    try:
        fd = os.open(path, _exclusive_flags(), 0o600)
    except OSError as exc:
        raise GovernanceError("projection-create-refused", str(exc)) from exc
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(_document(projection))
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        try:
            os.unlink(path)
        except OSError:
            pass
        raise


def _read_regular(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise GovernanceError("projection-read-refused", str(exc)) from exc
    try:
        mode = os.fstat(fd).st_mode
        if not stat.S_ISREG(mode):
            raise GovernanceError("projection-not-regular", str(path))
        with os.fdopen(fd, "rb") as stream:
            fd = -1
            return stream.read()
    finally:
        if fd >= 0:
            os.close(fd)


def read_projection(path: str | Path, expected_hash: str) -> GovernanceProjection:
    """Read a regular projection and verify envelope and governance identities."""
    try:
        raw = json.loads(_read_regular(Path(path)))
        projection_hash = raw.pop("projection_hash")
        body_bytes = json.dumps(
            raw, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    except GovernanceError:
        raise
    except (KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise GovernanceError("projection-invalid", str(exc)) from exc
    if not isinstance(projection_hash, str) or not hashlib.sha256(body_bytes).hexdigest() == projection_hash:
        raise GovernanceError("projection-tampered")
    if raw.get("governance_hash") != expected_hash:
        raise GovernanceError("governance-hash-mismatch")
    metadata = raw.get("metadata")
    if not isinstance(metadata, dict) or not isinstance(raw.get("bootstrap"), str):
        raise GovernanceError("projection-invalid", "wrong field types")
    return GovernanceProjection(expected_hash, raw["bootstrap"], _freeze(metadata))
