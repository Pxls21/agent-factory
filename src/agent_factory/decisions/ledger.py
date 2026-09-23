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
  - ``O_NOFOLLOW`` covers the final path component only (a symlinked
    parent directory is followed).
  - ``ENOSPC`` with nothing written raises ``OSError`` and leaves the
    file unchanged.
  - An ``os.fsync`` error after a full write raises ``OSError`` with the
    line in place (a later ``replay`` shows whether it landed).
  - ``make_row`` refuses a lone surrogate anywhere in ``raw_state``,
    even in a field ``normalize`` would drop.

Contract: tasks/briefs/laya/J1-2-brief.md (seeds/seed-laya-j1-v1.yaml;
amendment J1-A1: ``source_ref.source_digest`` is NOT part of row identity).
Repair: tasks/briefs/laya/J1-2-R1-brief.md (R1-R8).
"""
from __future__ import annotations

import hashlib
import json
import os
import posixpath
import stat

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

# Characters forbidden in source_ref.path (below U+0020, plus DEL and
# Unicode line terminators).
_PATH_BAD_CHARS = set(chr(c) for c in range(0x20))
_PATH_BAD_CHARS |= {"\x7f", "\x85", "\u2028", "\u2029"}


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


def _validate_path(path: str) -> None:
    """R4 path rules: normpath idempotent, no dot, no bad chars, etc."""
    if posixpath.normpath(path) != path:
        v = str(path)[:80]
        raise DecisionStateError("decision-row-invalid", f"source_ref.path={v}")
    if path == ".":
        v = str(path)[:80]
        raise DecisionStateError("decision-row-invalid", f"source_ref.path={v}")
    if any(c in _PATH_BAD_CHARS for c in path):
        v = str(path)[:80]
        raise DecisionStateError("decision-row-invalid", f"source_ref.path={v}")
    if path != path.strip():
        v = str(path)[:80]
        raise DecisionStateError("decision-row-invalid", f"source_ref.path={v}")
    if path.startswith("~"):
        v = str(path)[:80]
        raise DecisionStateError("decision-row-invalid", f"source_ref.path={v}")
    if len(path) >= 2 and path[1] == ":" and path[0].isalpha():
        v = str(path)[:80]
        raise DecisionStateError("decision-row-invalid", f"source_ref.path={v}")


def _validate_row(row: dict) -> None:
    """Steps (a)-(d) of the append contract."""
    # R2: row must be a dict.
    if not isinstance(row, dict):
        raise DecisionStateError(
            "decision-row-invalid", f"row={type(row).__name__}"
        )

    # R3: closed shape — refuse unknown top-level keys.
    for key in sorted(row):
        if key not in _ROW_FIELDS:
            raise DecisionStateError(
                "decision-row-unknown-field", key
            )

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
            # R3: closed shape for source_ref.
            for skey in sorted(row["source_ref"]):
                if skey not in _SOURCE_REF_FIELDS:
                    raise DecisionStateError(
                        "decision-row-unknown-field", f"source_ref.{skey}"
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
    # R2: each field's value must canonicalize and encode as UTF-8.
    for field in _ROW_FIELDS:
        if field == "source_ref":
            for sub in _SOURCE_REF_FIELDS:
                try:
                    canonical(row["source_ref"][sub]).encode("utf-8")
                except DecisionStateError:
                    raise
                except Exception as exc:
                    raise DecisionStateError(
                        "decision-row-invalid",
                        f"source_ref.{sub}={type(exc).__name__}",
                    ) from exc
        elif field == "state":
            try:
                canonical(row[field]).encode("utf-8")
            except DecisionStateError:
                raise
            except Exception as exc:
                raise DecisionStateError(
                    "decision-row-invalid",
                    f"{field}={type(exc).__name__}",
                ) from exc
        else:
            try:
                canonical(row[field]).encode("utf-8")
            except DecisionStateError:
                raise
            except Exception as exc:
                raise DecisionStateError(
                    "decision-row-invalid",
                    f"{field}={type(exc).__name__}",
                ) from exc

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
    # R4: additional path rules.
    _validate_path(path)

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


def _resolve_ledger_path(ledger_path) -> str:
    """R5: resolve ledger_path once via os.fspath; refuse bad types."""
    try:
        resolved = os.fspath(ledger_path)
    except TypeError:
        raise DecisionStateError(
            "decision-ledger-path-invalid", type(ledger_path).__name__
        )
    if isinstance(resolved, bytes):
        raise DecisionStateError(
            "decision-ledger-path-invalid", "bytes"
        )
    if not resolved:
        raise DecisionStateError(
            "decision-ledger-path-invalid", "empty"
        )
    if "\x00" in resolved:
        raise DecisionStateError(
            "decision-ledger-path-invalid", "nul"
        )
    return resolved


def _check_line(path_str: str, raw_line: bytes, lineno: int,
                parsed: dict) -> None:
    """R3: the per-line check shared by replay and append's pre-write guard.

    Raises DecisionStateError on any content problem.
    """
    # Must be valid JSON object.
    if not isinstance(parsed, dict):
        raise DecisionStateError(
            "decision-ledger-unparseable", f"{path_str}:{lineno}"
        )

    # Must equal canonical(parsed) byte for byte.
    try:
        expected_bytes = canonical(parsed).encode("utf-8")
    except DecisionStateError:
        raise DecisionStateError(
            "decision-ledger-unparseable", f"{path_str}:{lineno}"
        )
    if raw_line != expected_bytes:
        raise DecisionStateError(
            "decision-ledger-unparseable", f"{path_str}:{lineno}"
        )

    # Validate row: (a)-(d).
    _validate_row(parsed)


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

    R7: refuses by name and validates its own output. J1-1's refusals
    (unknown question, missing/unknown key, bad enum, absolute path
    outside the root, float) pass through unchanged.
    """
    # R7: check row-field inputs before any J1-1 call.
    if not isinstance(incumbent_answer, str) or not incumbent_answer:
        raise DecisionStateError(
            "decision-row-incomplete", "missing incumbent_answer"
        )
    if not isinstance(producer, str) or not producer:
        raise DecisionStateError(
            "decision-row-incomplete", "missing producer"
        )
    if not isinstance(source_ref, dict):
        raise DecisionStateError(
            "decision-row-incomplete", "missing source_ref.kind"
        )
    for sub in _SOURCE_REF_FIELDS:
        if sub not in source_ref:
            raise DecisionStateError(
                "decision-row-incomplete", f"missing source_ref.{sub}"
            )
        val = source_ref[sub]
        if not isinstance(val, str) or not val:
            raise DecisionStateError(
                "decision-row-incomplete", f"missing source_ref.{sub}"
            )
        # R7+R2: each sub-field must canonicalize and encode as UTF-8.
        try:
            canonical(val).encode("utf-8")
        except DecisionStateError:
            raise
        except Exception as exc:
            raise DecisionStateError(
                "decision-row-invalid",
                f"source_ref.{sub}={type(exc).__name__}",
            ) from exc

    # R7+R2: incumbent_answer must canonicalize and encode as UTF-8.
    try:
        canonical(incumbent_answer).encode("utf-8")
    except DecisionStateError:
        raise
    except Exception as exc:
        raise DecisionStateError(
            "decision-row-invalid",
            f"incumbent_answer={type(exc).__name__}",
        ) from exc

    # Validate question_id via J1-1 (raises DecisionStateError if unknown).
    schema_keys(question_id)

    # R7: compute state and state_digest; wrap non-DSE exceptions.
    try:
        s = redact(normalize(question_id, raw_state, root))
        sd = state_digest(question_id, raw_state, root)
    except DecisionStateError:
        raise
    except Exception as exc:
        raise DecisionStateError(
            "decision-row-invalid", f"state={type(exc).__name__}"
        ) from exc

    row: dict = {
        "calibration_state": "incumbent",
        "checkpoint_digest": "none",
        "incumbent_answer": incumbent_answer,
        "producer": producer,
        "question_id": question_id,
        "source_ref": dict(source_ref),
        "state": s,
        "state_digest": sd,
    }
    row["row_id"] = _compute_row_id(row)
    row["row_digest"] = _compute_row_digest(row)

    # R7: validate the output so make_row only returns what append accepts.
    _validate_row(row)

    return row


def append(ledger_path, row: dict) -> str:
    """Append one row to the ledger.  Returns the row_id.

    Validation order: (a) completeness, (b) validity, (c) digest
    recomputation, (d) fixed-point check, (e) replay-verify existing file,
    (f) duplicate check, (g) write with ``O_WRONLY|O_APPEND|O_CREAT`` and
    ``fsync``.  Existing bytes are never rewritten.  Single writer by
    contract (no lock).

    R1: returns the row_id ONLY after os.write reported every byte and
    os.fsync returned.  A short write truncates back and raises
    decision-ledger-short-write.
    """
    # R5: resolve path once.
    path_str = _resolve_ledger_path(ledger_path)

    # (a)-(d)
    _validate_row(row)

    # (e) replay-verify existing file (a corrupt ledger is never appended to).
    existing = replay(path_str)

    # (f) duplicate check.
    seen_ids = {r["row_id"] for r in existing}
    if row["row_id"] in seen_ids:
        raise DecisionStateError("decision-row-duplicate", row["row_id"])

    # (g) write: one canonical(row) + "\n" in a single os.write, then fsync.
    line = canonical(row) + "\n"
    line_bytes = line.encode("utf-8")

    # R3: run the per-line check on the exact bytes before writing.
    parsed_check = json.loads(line_bytes)
    _check_line(path_str, line_bytes.rstrip(b"\n"), 0, parsed_check)

    # R6: open with O_NOFOLLOW, check regular file on the fd.
    fd = os.open(
        path_str,
        os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW
        | os.O_NONBLOCK | os.O_CLOEXEC,
        0o644,
    )
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise DecisionStateError(
                "decision-ledger-not-regular", path_str
            )

        # R1: record file size before writing.
        size_before = st.st_size

        written = os.write(fd, line_bytes)
        expected = len(line_bytes)
        if written < expected:
            # Short write: truncate back to remove partial bytes.
            try:
                os.ftruncate(fd, size_before)
                os.fsync(fd)
            except OSError:
                raise DecisionStateError(
                    "decision-ledger-short-write",
                    f"{path_str}:{written}/{expected} truncate-failed",
                )
            raise DecisionStateError(
                "decision-ledger-short-write",
                f"{path_str}:{written}/{expected}",
            )
        os.fsync(fd)
    finally:
        os.close(fd)

    return row["row_id"]


def replay(ledger_path) -> list[dict]:
    """Replay-verify the ledger.  Returns the list of validated rows.

    A missing or empty file is an empty ledger (``[]``).  Every line must
    parse as JSON, end with ``\\n``, and equal ``canonical(parsed)`` byte
    for byte.  Then steps (a)-(d) per row.  A row_id seen twice in the
    file raises ``decision-row-duplicate``.
    """
    # R5: resolve path once.
    path_str = _resolve_ledger_path(ledger_path)

    # R6: open with O_RDONLY|O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC, check regular.
    try:
        fd = os.open(
            path_str,
            os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
        )
    except FileNotFoundError:
        return []
    except OSError as exc:
        # ELOOP (symlink with O_NOFOLLOW) → not-regular.
        import errno
        if exc.errno == errno.ELOOP:
            raise DecisionStateError(
                "decision-ledger-not-regular", path_str
            )
        raise

    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise DecisionStateError(
                "decision-ledger-not-regular", path_str
            )
        data = b""
        while True:
            chunk = os.read(fd, 65536)
            if not chunk:
                break
            data += chunk
    finally:
        os.close(fd)

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

        # Must be valid JSON.  R2: catch all content exceptions.
        try:
            parsed = json.loads(raw_line)
        except (json.JSONDecodeError, ValueError, RecursionError,
                TypeError, UnicodeError):
            raise DecisionStateError(
                "decision-ledger-unparseable", f"{path_str}:{i}"
            )

        # R2: non-dict JSON is unparseable.
        if not isinstance(parsed, dict):
            raise DecisionStateError(
                "decision-ledger-unparseable", f"{path_str}:{i}"
            )

        # Must equal canonical(parsed) byte for byte.
        # R2: catch all content exceptions.
        try:
            expected_bytes = canonical(parsed).encode("utf-8")
        except DecisionStateError:
            raise DecisionStateError(
                "decision-ledger-unparseable", f"{path_str}:{i}"
            )
        except (ValueError, RecursionError, TypeError, UnicodeError):
            raise DecisionStateError(
                "decision-ledger-unparseable", f"{path_str}:{i}"
            )
        if raw_line != expected_bytes:
            raise DecisionStateError(
                "decision-ledger-unparseable", f"{path_str}:{i}"
            )

        # Validate row: (a)-(d).  R2: row-level refusals keep THEIR reason.
        _validate_row(parsed)

        # Duplicate within file.
        if parsed["row_id"] in seen_ids:
            raise DecisionStateError(
                "decision-row-duplicate", parsed["row_id"]
            )
        seen_ids.add(parsed["row_id"])

        rows.append(parsed)

    return rows
