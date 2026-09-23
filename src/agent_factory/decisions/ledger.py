"""The append-only decision ledger (J1-2).

One JSONL line per row: ``canonical(row) + "\\n"``.  Every row is an
INCUMBENT decision (``calibration_state = "incumbent"``,
``checkpoint_digest = "none"``).  Append is the only write; existing bytes
are never rewritten.  Single writer by contract (no lock).

The row carries ``question_id`` (the row type), ``source_ref.kind`` (the
source kind).  ``redactions`` and ``captured_only`` are NOT carried:
``canonical()`` refuses booleans, ``normalize`` does not report which
classes it stripped, and every J1 row is capture-only by construction.

Declared limits:
  - An unkeyed digest catches accidental or naive mutation, not a forger
    who recomputes every digest.
  - Deleting a whole row is not detected (no hash chain in J1).
  - One writer at a time.

Contract: tasks/briefs/laya/J1-2-brief.md (seeds/seed-laya-j1-v1.yaml;
amendment J1-A1: ``source_ref.source_digest`` is NOT part of row identity).
"""
from __future__ import annotations

import hashlib
import json
import os

from agent_factory.decisions.canonical import canonical, state_digest
from agent_factory.decisions.volatile import (
    DecisionStateError,
    normalize,
    redact,
    schema_keys,
)

_VALID_KINDS = frozenset({
    "transcript_jsonl",
    "lane_report",
    "verify_report",
    "incident_log",
    "registry",
})

_ROW_FIELDS = (
    "calibration_state",
    "checkpoint_digest",
    "incumbent_answer",
    "producer",
    "question_id",
    "row_digest",
    "row_id",
    "source_ref",
    "state",
    "state_digest",
)

_SOURCE_REF_FIELDS = ("kind", "path", "source_digest", "locator")


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _is_hex64(s: str) -> bool:
    if not isinstance(s, str) or len(s) != 64:
        return False
    return all(c in "0123456789abcdef" for c in s)


def _compute_row_id(row: dict) -> str:
    """Amendment J1-A1: source_digest is NOT part of the identity."""
    identity = {
        "producer": row["producer"],
        "question_id": row["question_id"],
        "source_ref": {
            "kind": row["source_ref"]["kind"],
            "locator": row["source_ref"]["locator"],
            "path": row["source_ref"]["path"],
        },
        "state_digest": row["state_digest"],
    }
    return _sha256_hex(canonical(identity))


def _compute_row_digest(row: dict) -> str:
    without = {k: v for k, v in row.items() if k != "row_digest"}
    return _sha256_hex(canonical(without))


def _validate_row(row: dict) -> None:
    """Steps (a)-(d) of the append contract."""
    # (a) completeness: every field present and non-empty.
    for field in _ROW_FIELDS:
        if field not in row:
            raise DecisionStateError(
                "decision-row-incomplete", f"missing {field}"
            )
        if field == "source_ref":
            if not isinstance(row["source_ref"], dict):
                raise DecisionStateError(
                    "decision-row-incomplete", "missing source_ref.kind"
                )
            for sub in _SOURCE_REF_FIELDS:
                if sub not in row["source_ref"]:
                    raise DecisionStateError(
                        "decision-row-incomplete", f"missing source_ref.{sub}"
                    )
                val = row["source_ref"][sub]
                if not isinstance(val, str) or not val:
                    raise DecisionStateError(
                        "decision-row-incomplete", f"missing source_ref.{sub}"
                    )
        elif field == "state":
            if not isinstance(row[field], dict):
                raise DecisionStateError(
                    "decision-row-incomplete", f"missing {field}"
                )
        else:
            val = row[field]
            if not isinstance(val, str) or not val:
                raise DecisionStateError(
                    "decision-row-incomplete", f"missing {field}"
                )

    # (b) validity: the two literals, the kind set, the path shape, hex shapes.
    if row["checkpoint_digest"] != "none":
        v = str(row["checkpoint_digest"])[:80]
        raise DecisionStateError("decision-row-invalid", f"checkpoint_digest={v}")
    if row["calibration_state"] != "incumbent":
        v = str(row["calibration_state"])[:80]
        raise DecisionStateError(
            "decision-row-invalid", f"calibration_state={v}"
        )
    sr = row["source_ref"]
    if sr["kind"] not in _VALID_KINDS:
        v = str(sr["kind"])[:80]
        raise DecisionStateError("decision-row-invalid", f"source_ref.kind={v}")
    path = sr["path"]
    if path.startswith("/"):
        v = str(path)[:80]
        raise DecisionStateError("decision-row-invalid", f"source_ref.path={v}")
    if "\\" in path:
        v = str(path)[:80]
        raise DecisionStateError("decision-row-invalid", f"source_ref.path={v}")
    if ".." in path.split("/"):
        v = str(path)[:80]
        raise DecisionStateError("decision-row-invalid", f"source_ref.path={v}")
    if not _is_hex64(row["state_digest"]):
        v = str(row["state_digest"])[:80]
        raise DecisionStateError("decision-row-invalid", f"state_digest={v}")
    if not _is_hex64(sr["source_digest"]):
        v = str(sr["source_digest"])[:80]
        raise DecisionStateError(
            "decision-row-invalid", f"source_ref.source_digest={v}"
        )
    if not _is_hex64(row["row_id"]):
        v = str(row["row_id"])[:80]
        raise DecisionStateError("decision-row-invalid", f"row_id={v}")

    # (c) digest recomputation.
    expected_sd = _sha256_hex(canonical(row["state"]))
    if row["state_digest"] != expected_sd:
        raise DecisionStateError(
            "decision-row-digest-mismatch", row["row_id"]
        )
    expected_rid = _compute_row_id(row)
    if row["row_id"] != expected_rid:
        raise DecisionStateError(
            "decision-row-digest-mismatch", row["row_id"]
        )
    expected_rd = _compute_row_digest(row)
    if row["row_digest"] != expected_rd:
        raise DecisionStateError(
            "decision-row-digest-mismatch", row["row_id"]
        )

    # (d) fixed-point check: redact(normalize(qid, state, None)) == state.
    qid = row["question_id"]
    try:
        restate = redact(normalize(qid, row["state"], None))
    except DecisionStateError:
        raise DecisionStateError(
            "decision-row-state-not-canonical", row["row_id"]
        )
    if restate != row["state"]:
        raise DecisionStateError(
            "decision-row-state-not-canonical", row["row_id"]
        )


def make_row(
    *,
    producer: str,
    question_id: str,
    raw_state: dict,
    incumbent_answer: str,
    source_ref: dict,
    root: str | os.PathLike | None,
) -> dict:
    """Build a complete ledger row.

    Sets the two literals (``checkpoint_digest``, ``calibration_state``).
    Computes ``state``, ``state_digest``, ``row_id``, ``row_digest``.
    No caller assembles a digest by hand.

    J1-1's refusals (unknown question, missing/unknown key, bad enum,
    absolute path outside the root, float) pass through unchanged.
    """
    # Validate question_id via J1-1 (raises DecisionStateError if unknown).
    schema_keys(question_id)

    state = redact(normalize(question_id, raw_state, root))
    sd = state_digest(question_id, raw_state, root)

    row: dict = {
        "calibration_state": "incumbent",
        "checkpoint_digest": "none",
        "incumbent_answer": incumbent_answer,
        "producer": producer,
        "question_id": question_id,
        "source_ref": dict(source_ref),
        "state": state,
        "state_digest": sd,
    }
    row["row_id"] = _compute_row_id(row)
    row["row_digest"] = _compute_row_digest(row)
    return row


def append(ledger_path: str | os.PathLike, row: dict) -> str:
    """Append one row to the ledger.  Returns the row_id.

    Validation order: (a) completeness, (b) validity, (c) digest
    recomputation, (d) fixed-point check, (e) replay-verify existing file,
    (f) duplicate check, (g) write with ``O_WRONLY|O_APPEND|O_CREAT`` and
    ``fsync``.  Existing bytes are never rewritten.  Single writer by
    contract (no lock).
    """
    # (a)-(d)
    _validate_row(row)

    # (e) replay-verify existing file (a corrupt ledger is never appended to).
    existing = replay(ledger_path)

    # (f) duplicate check.
    seen_ids = {r["row_id"] for r in existing}
    if row["row_id"] in seen_ids:
        raise DecisionStateError("decision-row-duplicate", row["row_id"])

    # (g) write: one canonical(row) + "\n" in a single os.write, then fsync.
    line = canonical(row) + "\n"
    fd = os.open(
        str(ledger_path), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644
    )
    try:
        os.write(fd, line.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)

    return row["row_id"]


def replay(ledger_path: str | os.PathLike) -> list[dict]:
    """Replay-verify the ledger.  Returns the list of validated rows.

    A missing or empty file is an empty ledger (``[]``).  Every line must
    parse as JSON, end with ``\\n``, and equal ``canonical(parsed)`` byte
    for byte.  Then steps (a)-(d) per row.  A row_id seen twice in the
    file raises ``decision-row-duplicate``.
    """
    path_str = str(ledger_path)
    try:
        with open(path_str, "rb") as fh:
            data = fh.read()
    except FileNotFoundError:
        return []

    if not data:
        return []

    parts = data.split(b"\n")
    # A well-formed file ends with \n, so the last element is b"".
    if parts[-1] != b"":
        lineno = len(parts)
        raise DecisionStateError(
            "decision-ledger-unparseable", f"{path_str}:{lineno}"
        )

    lines = parts[:-1]
    rows: list[dict] = []
    seen_ids: set[str] = set()

    for i, raw_line in enumerate(lines, 1):
        # An empty line (from a double newline) is unparseable.
        if not raw_line:
            raise DecisionStateError(
                "decision-ledger-unparseable", f"{path_str}:{i}"
            )

        # Must be valid JSON.
        try:
            parsed = json.loads(raw_line)
        except (json.JSONDecodeError, ValueError):
            raise DecisionStateError(
                "decision-ledger-unparseable", f"{path_str}:{i}"
            )

        # Must equal canonical(parsed) byte for byte.
        try:
            expected_bytes = canonical(parsed).encode("utf-8")
        except DecisionStateError:
            raise DecisionStateError(
                "decision-ledger-unparseable", f"{path_str}:{i}"
            )
        if raw_line != expected_bytes:
            raise DecisionStateError(
                "decision-ledger-unparseable", f"{path_str}:{i}"
            )

        # Validate row: (a)-(d).
        _validate_row(parsed)

        # Duplicate within file.
        if parsed["row_id"] in seen_ids:
            raise DecisionStateError(
                "decision-row-duplicate", parsed["row_id"]
            )
        seen_ids.add(parsed["row_id"])

        rows.append(parsed)

    return rows
