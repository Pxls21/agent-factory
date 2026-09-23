#!/usr/bin/env python3
"""Record Hermes lane facts and nudge when code changed after the last check.

This is a deterministic hook helper. ``record`` handles the ``post_tool_call``
observer; ``gate`` handles the bounded ``pre_verify`` directive. Ledgers live in
the OS temporary directory, outside the repository.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
VERIFY_COMMAND = ROOT / "scripts" / "verify_command.py"
CODE_SUFFIXES = {
    ".py", ".sh", ".bash", ".js", ".mjs", ".cjs", ".ts", ".rs", ".go",
    ".toml", ".yaml", ".yml", ".json", ".sql", ".c", ".h",
}
PROJECT_PATTERNS = [
    r"^bash\s+harness-ports/tests/[A-Za-z0-9_.-]+\.sh(?:\s|$)",
    r"^python3\s+harness-ports/tests/test_[A-Za-z0-9_.-]+\.py(?:\s|$)",
    r"^bash\s+scripts/lane_gate\.sh(?:\s|$)",
    r"^bash\s+scripts/test_summary\.sh(?:\s|$)",
]
PATCH_PATH = re.compile(
    r"^\*\*\* (?:Add File|Update File|Delete File|Move to):\s*(.+?)\s*$",
    re.MULTILINE,
)
RC_WRAPPER = re.compile(
    r"^\s*set\s+-o\s+pipefail\s*;\s*"
    r"(?P<check>.+?)\s*\|\s*tee\s+[^;|&\n]+\s*;\s*"
    r"rc=\$\{PIPESTATUS\[0\]\}\s*;\s*"
    r"(?:(?:printf|echo)\b[^;\n]*;\s*)?"
    r"exit\s+['\"]?\$rc['\"]?\s*$",
    re.DOTALL,
)


def _warn(message: str) -> None:
    print(f"lane-done-gate: {message}", file=sys.stderr)


def _repo_root(_cwd: Any) -> Path:
    return ROOT.resolve()


def ledger_file(root: Path, session_id: Any) -> Path:
    tag = hashlib.sha256(str(root).encode()).hexdigest()[:12]
    raw = session_id if isinstance(session_id, str) else ""
    sid = "".join(c for c in raw if c.isalnum() or c in "-_")[:64] or "default"
    return Path(tempfile.gettempdir()) / f"lane-done-gate-{tag}-{sid}.jsonl"


def _classifier():
    spec = importlib.util.spec_from_file_location("lane_done_verify_command", VERIFY_COMMAND)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load scripts/verify_command.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _is_direct_check(command: str, module: Any, patterns: list[str]) -> bool:
    """Keep project runners closed even though C1 patterns use ``search``."""
    stripped = command.strip()
    for pattern in PROJECT_PATTERNS:
        match = re.match(pattern, stripped, re.ASCII)
        if match:
            remainder = stripped[match.end():].lstrip()
            if remainder.startswith("&&") or remainder.startswith("||"):
                return False
            return module.is_verify(stripped, patterns)
    if any(re.search(pattern.pattern, stripped, re.ASCII) for pattern in module.VERIFY):
        return module.is_verify(stripped, patterns)
    return False


def counts_as_check(command: str) -> tuple[bool, str]:
    """Classify only the closed project set plus C1's existing checks."""
    try:
        module = _classifier()
        patterns = [pattern.pattern for pattern in module.VERIFY] + PROJECT_PATTERNS
        if _is_direct_check(command, module, patterns):
            return True, "recognized check"
        wrapper = RC_WRAPPER.fullmatch(command)
        if wrapper and _is_direct_check(wrapper.group("check"), module, patterns):
            return True, "recognized pipefail/tee check"
        return False, "command does not count as a check"
    except Exception as exc:
        return False, f"classifier error: {type(exc).__name__}: {exc}"


def _append(path: Path, fact: dict[str, Any]) -> None:
    line = json.dumps(fact, ensure_ascii=False, separators=(",", ":")) + "\n"
    flags = os.O_APPEND | os.O_CREAT | os.O_WRONLY
    fd = os.open(path, flags, 0o600)
    try:
        os.write(fd, line.encode())
    finally:
        os.close(fd)


def _result_exit_code(extra: Any) -> tuple[int | None, str]:
    if not isinstance(extra, dict):
        return None, "extra is not an object"
    raw = extra.get("result")
    if not isinstance(raw, str):
        return None, "extra.result is not a JSON string"
    try:
        result = json.loads(raw)
    except Exception as exc:
        return None, f"extra.result is not JSON: {type(exc).__name__}"
    if not isinstance(result, dict):
        return None, "extra.result JSON is not an object"
    value = result.get("exit_code")
    if type(value) is not int:
        return None, "exit_code is not an int"
    return value, "exit_code parsed"


def _edit_paths(tool: str, tool_input: Any) -> list[str]:
    if not isinstance(tool_input, dict):
        return []
    if tool == "write_file":
        path = tool_input.get("path")
        return [path] if isinstance(path, str) and path else []
    if tool != "patch":
        return []
    if tool_input.get("mode") == "patch":
        text = tool_input.get("patch")
        if not isinstance(text, str):
            return []
        return list(dict.fromkeys(m.group(1) for m in PATCH_PATH.finditer(text)))
    path = tool_input.get("path")
    return [path] if isinstance(path, str) and path else []


def record(payload: dict[str, Any]) -> None:
    root = _repo_root(payload.get("cwd"))
    ledger = ledger_file(root, payload.get("session_id"))
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if tool in {"write_file", "patch"}:
        paths = _edit_paths(str(tool), tool_input)
        if not paths:
            _warn(f"{tool} payload has no path")
            return
        for path in paths:
            _append(ledger, {"kind": "edit", "path": path})
        return
    if tool == "terminal":
        command = tool_input.get("command") if isinstance(tool_input, dict) else None
        if not isinstance(command, str):
            _append(ledger, {"kind": "check", "command": "", "exit_code": None,
                             "passing": False, "reason": "terminal command missing"})
            _warn("terminal payload has no command")
            return
        counts, reason = counts_as_check(command)
        exit_code, exit_reason = _result_exit_code(payload.get("extra"))
        passing = counts and exit_code == 0
        if exit_code is None:
            reason = exit_reason
            _warn(exit_reason)
        elif not counts:
            reason = "command does not count as a check"
        elif exit_code != 0:
            reason = f"check exited {exit_code}"
        _append(
            ledger,
            {"kind": "check", "command": command, "exit_code": exit_code,
             "passing": passing, "reason": reason},
        )


def _facts(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    facts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            fact = json.loads(line)
        except Exception:
            _warn("ledger contains malformed JSON; ignored one line")
            continue
        if isinstance(fact, dict):
            facts.append(fact)
    return facts


def _relative(path: str, root: Path) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            return candidate.resolve().relative_to(root).as_posix()
        except ValueError:
            return candidate.as_posix()
    return PurePosixPath(path).as_posix()


def _is_code(path: str, root: Path) -> bool:
    rel = _relative(path, root)
    parts = PurePosixPath(rel).parts
    if "transcripts" in parts:
        return False
    suffix = PurePosixPath(rel).suffix.lower()
    if suffix in {".md", ".txt"}:
        return False
    if suffix in CODE_SUFFIXES:
        return True
    if suffix:
        return False
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        with candidate.open("rb") as stream:
            return stream.read(2) == b"#!"
    except OSError:
        return False


def gate(payload: dict[str, Any]) -> None:
    root = _repo_root(payload.get("cwd"))
    facts = _facts(ledger_file(root, payload.get("session_id")))
    changed = payload.get("extra", {}).get("changed_paths", [])
    if not isinstance(changed, list):
        changed = []
    changed_code = sorted({
        _relative(path, root) for path in changed
        if isinstance(path, str) and _is_code(path, root)
    })
    if not changed_code:
        return

    last_pass = -1
    last_command = "none"
    edit_positions: dict[str, int] = {}
    for index, fact in enumerate(facts):
        if fact.get("kind") == "check" and fact.get("passing") is True:
            last_pass = index
            last_command = str(fact.get("command") or "none")
        elif fact.get("kind") == "edit" and isinstance(fact.get("path"), str):
            edit_positions[_relative(fact["path"], root)] = index

    known_stale = [path for path in changed_code if edit_positions.get(path, -1) > last_pass]
    unknown = [path for path in changed_code if path not in edit_positions]
    if unknown and last_pass >= 0:
        shown = ", ".join(unknown[:5])
        suffix = f" and {len(unknown) - 5} more" if len(unknown) > 5 else ""
        _warn(f"unknown edit order for {shown}{suffix}; a passing check exists")
    stale = known_stale + (unknown if last_pass < 0 else [])
    stale = list(dict.fromkeys(stale))
    if not stale:
        return

    shown = ", ".join(stale[:5])
    suffix = f" and {len(stale) - 5} more" if len(stale) > 5 else ""
    command = last_command.replace("\n", " ")
    if len(command) > 300:
        command = command[:297] + "..."
    reason = (
        f"Code changed after the last passing check: {shown}{suffix}. "
        f"Last passing check: {command}. Re-run the checks that cover those files, "
        "then print the COMPLETE final report again, because the harness keeps only "
        "the last message."
    )
    encoded = json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False)
    if len(encoded.encode()) > 1500:
        suffix_text = "... Re-run checks, then print the COMPLETE final report again."
        low, high = 0, len(reason)
        while low < high:
            midpoint = (low + high + 1) // 2
            candidate = reason[:midpoint] + suffix_text
            candidate_encoded = json.dumps(
                {"decision": "block", "reason": candidate}, ensure_ascii=False
            )
            if len(candidate_encoded.encode()) <= 1500:
                low = midpoint
            else:
                high = midpoint - 1
        encoded = json.dumps(
            {"decision": "block", "reason": reason[:low] + suffix_text},
            ensure_ascii=False,
        )
    print(encoded)


def main() -> int:
    try:
        if len(sys.argv) != 2 or sys.argv[1] not in {"record", "gate"}:
            _warn("usage: lane-done-gate.py record|gate")
            return 0
        raw = sys.stdin.read()
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("payload is not an object")
        if sys.argv[1] == "record":
            record(payload)
        else:
            gate(payload)
    except Exception as exc:
        _warn(f"{type(exc).__name__}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
