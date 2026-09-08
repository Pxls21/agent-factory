"""S0-08 marker gate — the seed's `marker_control`, made executable.

seeds/seed-stage0-v1.yaml:493 requires: "the Stage-1 grep-gate FAILS when the
NOT-run marker is absent or malformed". No literal `NOT run here:` grep-gate
exists anywhere in the tree; the machine check that exists is
`validate-ledger stage1-gate`'s state comparison. This gate is the per-proof
counterpart: it reads ONE proof directory and rules on its marker alone.

Verdicts (stdout, one line):
  PASS  marker: completed transition (result.json present, blocked.json gone)
  PASS  marker: <blocker_status> (a well-formed, still-honest deferral)
  FAIL  marker: absent
  FAIL  marker: malformed: <field>
  FAIL  marker: expired - the proof must run

Exit codes: 0 PASS / 1 FAIL / 64 usage error.

This gate NEVER writes. proofs/S0-08/blocked.json stays in place until the
coordinator's mint transition removes it.
"""
from __future__ import annotations

import json
import stat as _stat
import sys
from pathlib import Path

# blocked.schema.json:19 — the only statuses a marker may carry.
VALID_BLOCKER_STATUS = ("absent", "rejecting", "expired")

# The marker fields the seed's marker_control requires.
REQUIRED_MARKER_FIELDS = ("probe_run", "blocker_status", "unblock_condition")


class Fail(Exception):
    """The marker does not satisfy the control."""


def _read_json(path: Path, name: str):
    """Reject a non-regular file BEFORE reading it: a FIFO at an artifact path
    must be a named refusal, never a hang."""
    if not _stat.S_ISREG(path.lstat().st_mode):
        raise Fail(f"marker: malformed: {name} is not a regular file")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise Fail(f"marker: malformed: {name} is not readable JSON ({type(exc).__name__})")


def _result_is_real(result: Path, proof_dir: Path) -> bool:
    """AF-AP-40: presence alone must not retire the marker. A FIFO, a directory
    or an unparseable file named result.json is not a proof that ran, and
    neither is one carrying another proof's id (AF-AP-10)."""
    if not result.exists():
        return False
    if not _stat.S_ISREG(result.lstat().st_mode):
        raise Fail("marker: malformed: result.json is not a regular file")
    try:
        payload = json.loads(result.read_text(encoding="utf-8"))
    except Exception:
        raise Fail("marker: malformed: result.json is not readable JSON")
    if not isinstance(payload, dict):
        raise Fail("marker: malformed: result.json is not an object")
    if payload.get("proof_id") != proof_dir.resolve().name:
        raise Fail(
            f"marker: malformed: result.json proof_id {payload.get('proof_id')!r} "
            f"does not match {proof_dir.resolve().name}"
        )
    return True


def check_marker(proof_dir: Path) -> str:
    blocked = proof_dir / "blocked.json"
    result = proof_dir / "result.json"
    result_ran = _result_is_real(result, proof_dir)

    # The completed transition: the proof ran, so the marker is gone by design.
    if result_ran and not blocked.exists():
        return "marker: completed transition"

    if not blocked.exists():
        raise Fail("marker: absent")

    payload = _read_json(blocked, "blocked.json")
    if not isinstance(payload, dict):
        raise Fail("marker: malformed: blocked.json is not an object")

    marker = payload.get("marker")
    if not isinstance(marker, dict):
        raise Fail("marker: malformed: marker")

    for field in REQUIRED_MARKER_FIELDS:
        if field not in marker:
            raise Fail(f"marker: malformed: {field}")

    status = marker["blocker_status"]
    if status not in VALID_BLOCKER_STATUS:
        raise Fail(f"marker: malformed: blocker_status {status!r}")

    # The blocker is gone. A deferral may not outlive its blocker.
    if status == "expired" and not result_ran:
        raise Fail("marker: expired - the proof must run")

    return f"marker: {status}"


def main(argv) -> int:
    args = list(argv[1:])
    if len(args) != 2 or args[0] != "--proof-dir":
        print("usage: marker_gate.py --proof-dir <dir>", file=sys.stderr)
        return 64
    proof_dir = Path(args[1])
    if not proof_dir.is_dir():
        print(f"usage: {proof_dir} is not a directory", file=sys.stderr)
        return 64
    try:
        print(check_marker(proof_dir))
        return 0
    except Fail as f:
        print(f)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
