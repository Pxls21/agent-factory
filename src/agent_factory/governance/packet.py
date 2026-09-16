"""Load reviewed Fubuki sources, then compile and hash a packet."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .pin import GovernanceError, import_pinned


@dataclass(frozen=True)
class LintResult:
    findings: tuple[tuple[str, str, str], ...]
    exit_code: int


@dataclass(frozen=True)
class Packet:
    canonical: bytes
    hash: str
    reviewed: bool


def _correct_lint_exit(findings: Iterable[tuple[str, str, str]]) -> int:
    """Port of the S0-07 correction: violations outrank review findings."""
    tiers = {finding[0] for finding in findings}
    if "VIOLATION" in tiers:
        return 1
    if "REVIEW" in tiers:
        return 2
    return 0


def _source_files(root: Path) -> tuple[Path, ...]:
    if root.is_file():
        return (root,)
    manifest_path = root / "persona.package.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            paths = tuple(root / entry["path"] for entry in manifest["files"])
        except (OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
            raise GovernanceError("fubuki-manifest-invalid", str(exc)) from exc
        return tuple(sorted(paths))

    files = tuple(
        path
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    )
    if not files:
        raise GovernanceError("fubuki-sources-empty", str(root))
    return files


def lint_sources(root: str | Path) -> LintResult:
    """Lint every declared source with Fubuki's pinned persona linter."""
    persona_lint = import_pinned("lint.persona_lint")
    lint, load_banned = persona_lint.lint, persona_lint.load_banned

    root = Path(root)
    if not root.exists():
        raise GovernanceError("fubuki-sources-missing", str(root))

    banned = load_banned(root if root.is_dir() else root.parent)
    findings: list[tuple[str, str, str]] = []
    for source in _source_files(root):
        try:
            text = source.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise GovernanceError("fubuki-source-unreadable", str(source)) from exc
        for tier, check, evidence in lint(text, "conversational", banned):
            label = source.name if root.is_file() else str(source.relative_to(root))
            findings.append((tier, check, f"{label}:{evidence}"))
    findings.sort(key=lambda finding: (0 if finding[0] == "REVIEW" else 1, finding[1], finding[2]))
    return LintResult(tuple(findings), _correct_lint_exit(findings))


def _compile_request(sources_root: Path, package_id: str) -> Any:
    CompileRequest = import_pinned("fubuki_os.compiler.models").CompileRequest

    request_path = sources_root / "compile-request.json"
    if request_path.is_file():
        try:
            raw = json.loads(request_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise GovernanceError("fubuki-compile-request-invalid", str(exc)) from exc
    else:
        raw = {
            "package_id": package_id,
            "branch": "main",
            "active_person": "operator",
            "request": {
                "text": "agent-factory governance bootstrap",
                "task_type": "general",
                "third_party_visible": False,
            },
            "session_id": "governance-bootstrap",
            "memory_cutoff": "1970-01-01T00:00:00Z",
            "adapter": "claude@agent-factory-bootstrap",
            "example_budget": 0,
        }
    return CompileRequest.from_dict(raw)


def compile_canonical(sources_root: str | Path) -> bytes:
    """Compile through Fubuki's own loader, validator, compiler, and canonicalizer."""
    compile_packet = import_pinned("fubuki_os.compiler.compiler").compile_packet
    load_package = import_pinned("fubuki_os.package.loader").load_package
    validate_package = import_pinned("fubuki_os.package.validator").validate_package
    canonical_json = import_pinned("fubuki_os.release.hashing").canonical_json

    sources_root = Path(sources_root)
    try:
        validated = validate_package(load_package(sources_root))
        request = _compile_request(sources_root, validated.package_id)
        compiled, _trace = compile_packet(validated, request)
        return canonical_json(compiled).encode("utf-8")
    except GovernanceError:
        raise
    except Exception as exc:
        raise GovernanceError("fubuki-compile-failed", str(exc)) from exc


def governance_hash(canonical_bytes: bytes) -> str:
    """Return the contract's unprefixed sha256 hex over canonical packet bytes."""
    if not isinstance(canonical_bytes, bytes):
        raise TypeError("canonical_bytes must be bytes")
    return hashlib.sha256(canonical_bytes).hexdigest()


def _reviewed(packet: dict[str, Any]) -> bool:
    """Read review only from the compiled packet; absence is never approval."""
    if packet.get("reviewed") is True:
        return True
    return packet.get("review_status") in {"approved", "reviewed", "certified"}


def load_packet(root: str | Path) -> Packet:
    """Lint, compile, hash, and refuse packets without an upstream review field."""
    result = lint_sources(root)
    if result.exit_code == 1:
        raise GovernanceError("fubuki-lint-violation")
    canonical = compile_canonical(root)
    try:
        compiled = json.loads(canonical)
    except (TypeError, json.JSONDecodeError) as exc:
        raise GovernanceError("fubuki-packet-invalid", str(exc)) from exc
    reviewed = _reviewed(compiled)
    if not reviewed:
        raise GovernanceError("fubuki-packet-unreviewed")
    return Packet(canonical=canonical, hash=governance_hash(canonical), reviewed=True)
