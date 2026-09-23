"""J1-2 tests: the append-only decision ledger (make_row, append, replay).

Every test is LLM-free and deterministic. The negative controls fail for the
EXACT expected reason. Row identity follows amendment J1-A1: source_digest is
NOT part of the identity (it stays as provenance, covered by row_digest).

Contract: tasks/briefs/laya/J1-2-brief.md (seeds/seed-laya-j1-v1.yaml AC 1 +
AC 2; amendment J1-A1).
"""
from __future__ import annotations

import hashlib
import json
import os

import pytest

from agent_factory.decisions.canonical import canonical
from agent_factory.decisions.volatile import DecisionStateError

GOLDEN_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "decisions", "golden")

GOLDEN_IDS = [
    "b2.hit_role",
    "b1.finding_sev",
    "b1.finding_kind",
    "d1.bug_echo_scores",
    "v1.finding_class",
    "ap.violates_row",
    "wf.drift",
]


def _load(qid: str) -> dict:
    with open(os.path.join(GOLDEN_DIR, qid + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def _fake_source_ref(*, source_digest=None):
    """An invented source_ref with all required sub-fields."""
    return {
        "kind": "incident_log",
        "path": "docs/INCIDENT-LOG.md",
        "source_digest": source_digest or "a" * 64,
        "locator": "AF-AP-76: mech-bar three-round cap",
    }


def _make_row_for_golden(qid: str, *, producer="decide-harvest/incident-log",
                         source_ref=None):
    """Build a valid ledger row from a golden fixture."""
    from agent_factory.decisions.ledger import make_row

    fixture = _load(qid)
    return make_row(
        producer=producer,
        question_id=qid,
        raw_state=fixture["state"],
        incumbent_answer="accepted",
        source_ref=source_ref or _fake_source_ref(),
        root=fixture.get("root"),
    )


# ---------------------------------------------------------------------------
# AC 1: the import command prints OK
# ---------------------------------------------------------------------------


def test_import_ac1():
    import agent_factory.decisions as d  # noqa: F811
    import agent_factory.decisions.canonical  # noqa: F811
    import agent_factory.decisions.ledger  # noqa: F811
    assert hasattr(d, "DecisionStateError")
    assert hasattr(agent_factory.decisions.ledger, "make_row")
    assert hasattr(agent_factory.decisions.ledger, "append")
    assert hasattr(agent_factory.decisions.ledger, "replay")


# ---------------------------------------------------------------------------
# Replay byte-identical x2: 7 rows (one per question type), appended into two
# fresh ledgers in the same order => byte-identical files, replay returns the
# appended rows.  The whole test runs twice, bitwise.
# ---------------------------------------------------------------------------


def _build_and_replay(tmp_path, suffix):
    from agent_factory.decisions.ledger import append, replay

    ledger = tmp_path / f"ledger{suffix}.jsonl"
    rows = []
    for qid in GOLDEN_IDS:
        row = _make_row_for_golden(qid)
        rid = append(ledger, row)
        assert rid == row["row_id"]
        rows.append(row)
    replayed = replay(ledger)
    assert len(replayed) == len(GOLDEN_IDS)
    for i, r in enumerate(replayed):
        assert r == rows[i], f"row {i} ({GOLDEN_IDS[i]}) differs after replay"
    return ledger.read_bytes(), rows


def test_replay_byte_identical_x2(tmp_path):
    # Run the whole build+replay twice; the two ledger files must be
    # byte-identical and the replayed rows must match.
    bytes_a, rows_a = _build_and_replay(tmp_path, "_a")
    bytes_b, rows_b = _build_and_replay(tmp_path, "_b")
    assert bytes_a == bytes_b, "two independent ledgers are not byte-identical"
    assert rows_a == rows_b, "replayed rows differ between the two runs"
    # Run the assertion a second time (bitwise).
    bytes_c, rows_c = _build_and_replay(tmp_path, "_c")
    bytes_d, rows_d = _build_and_replay(tmp_path, "_d")
    assert bytes_c == bytes_d
    assert bytes_a == bytes_c, "runs across the four are not byte-identical"


# ---------------------------------------------------------------------------
# Re-landing: each golden's variant with the same producer and source_ref
# => same row_id, refused as decision-row-duplicate.
# ---------------------------------------------------------------------------


def test_relanding_same_row_id(tmp_path):
    from agent_factory.decisions.ledger import append, make_row

    ledger = tmp_path / "ledger.jsonl"
    for qid in GOLDEN_IDS:
        fixture = _load(qid)
        src = _fake_source_ref()
        producer = "decide-harvest/incident-log"
        # Append the base row first.
        base = make_row(
            producer=producer,
            question_id=qid,
            raw_state=fixture["state"],
            incumbent_answer="accepted",
            source_ref=src,
            root=fixture.get("root"),
        )
        append(ledger, base)
        # Build a row from the variant: same producer, same source_ref.
        variant = make_row(
            producer=producer,
            question_id=qid,
            raw_state=fixture["variant"],
            incumbent_answer="accepted",
            source_ref=src,
            root=fixture.get("root"),
        )
        # The variant must produce the same row_id (normalize -> same state_digest).
        assert variant["row_id"] == base["row_id"], (
            f"{qid}: variant row_id {variant['row_id']} != base {base['row_id']}"
        )
        # And therefore be refused as a duplicate.
        with pytest.raises(DecisionStateError, match="decision-row-duplicate"):
            append(ledger, variant)


# ---------------------------------------------------------------------------
# J1-A1: source_digest is NOT part of the identity.
# ---------------------------------------------------------------------------


def test_source_digest_not_in_identity(tmp_path):
    from agent_factory.decisions.ledger import append, make_row

    ledger = tmp_path / "ledger.jsonl"
    fixture = _load("b1.finding_sev")
    root = fixture.get("root")
    producer = "decide-harvest/incident-log"

    # Two different source_digest values => one row_id.
    src_a = _fake_source_ref(source_digest="a" * 64)
    src_b = _fake_source_ref(source_digest="b" * 64)
    row_a = make_row(
        producer=producer, question_id="b1.finding_sev",
        raw_state=fixture["state"], incumbent_answer="accepted",
        source_ref=src_a, root=root,
    )
    row_b = make_row(
        producer=producer, question_id="b1.finding_sev",
        raw_state=fixture["state"], incumbent_answer="accepted",
        source_ref=src_b, root=root,
    )
    assert row_a["row_id"] == row_b["row_id"], (
        "source_digest must NOT be part of the identity"
    )
    append(ledger, row_a)
    with pytest.raises(DecisionStateError, match="decision-row-duplicate"):
        append(ledger, row_b)

    # A different locator => a different row_id.
    src_c = dict(_fake_source_ref())
    src_c["locator"] = "AF-AP-99: a different entry"
    row_c = make_row(
        producer=producer, question_id="b1.finding_sev",
        raw_state=fixture["state"], incumbent_answer="accepted",
        source_ref=src_c, root=root,
    )
    assert row_c["row_id"] != row_a["row_id"], (
        "a different locator must produce a different row_id"
    )

    # A different producer => a different row_id.
    row_d = make_row(
        producer="decide-harvest/registry", question_id="b1.finding_sev",
        raw_state=fixture["state"], incumbent_answer="accepted",
        source_ref=src_a, root=root,
    )
    assert row_d["row_id"] != row_a["row_id"], (
        "a different producer must produce a different row_id"
    )


# ---------------------------------------------------------------------------
# Missing provenance: each of the five provenance fields and each source_ref
# sub-field, both absent and empty.
# ---------------------------------------------------------------------------


def test_missing_provenance_each(tmp_path):
    from agent_factory.decisions.ledger import append, make_row

    fixture = _load("b1.finding_sev")
    root = fixture.get("root")
    base_row = make_row(
        producer="decide-harvest/incident-log",
        question_id="b1.finding_sev",
        raw_state=fixture["state"],
        incumbent_answer="accepted",
        source_ref=_fake_source_ref(),
        root=root,
    )
    ledger = tmp_path / "ledger.jsonl"

    # Top-level fields that are provenance strings.
    top_fields = [
        "question_id", "producer", "checkpoint_digest",
        "calibration_state", "incumbent_answer",
    ]
    for field in top_fields:
        for bad_val in [None, ""]:
            row = dict(base_row)
            if bad_val is None:
                row.pop(field, None)
            else:
                row[field] = bad_val
            # Recompute digests so we test the COMPLETENESS check, not the
            # digest check.
            with pytest.raises(DecisionStateError) as exc:
                append(ledger, row)
            assert str(exc.value) == f"decision-row-incomplete: missing {field}", (
                f"field={field} bad_val={bad_val!r}: {exc.value}"
            )

    # source_ref sub-fields.
    for sub in ["kind", "path", "source_digest", "locator"]:
        for bad_val in [None, ""]:
            row = dict(base_row)
            row["source_ref"] = dict(base_row["source_ref"])
            if bad_val is None:
                row["source_ref"].pop(sub, None)
            else:
                row["source_ref"][sub] = bad_val
            with pytest.raises(DecisionStateError) as exc:
                append(ledger, row)
            assert str(exc.value) == f"decision-row-incomplete: missing source_ref.{sub}", (
                f"sub={sub} bad_val={bad_val!r}: {exc.value}"
            )


# ---------------------------------------------------------------------------
# Duplicate refused, file bytes unchanged.
# ---------------------------------------------------------------------------


def test_duplicate_refused_bytes_unchanged(tmp_path):
    from agent_factory.decisions.ledger import append

    ledger = tmp_path / "ledger.jsonl"
    row = _make_row_for_golden("b1.finding_sev")
    append(ledger, row)
    before = ledger.read_bytes()
    with pytest.raises(DecisionStateError, match="decision-row-duplicate"):
        append(ledger, row)
    after = ledger.read_bytes()
    assert before == after, "duplicate append must not change the file"


# ---------------------------------------------------------------------------
# Tamper detected: one character flipped in the FILE and in memory.
# ---------------------------------------------------------------------------


def test_tamper_detected(tmp_path):
    from agent_factory.decisions.ledger import append, replay

    ledger = tmp_path / "ledger.jsonl"
    row = _make_row_for_golden("b1.finding_sev")
    append(ledger, row)
    good_bytes = ledger.read_bytes()

    # --- File-level tamper ---
    # Each flip target: incumbent_answer, a state value, source_ref.locator,
    # source_ref.source_digest, and row_id.
    def _flip_in_file(target_str: str, label: str, *, hex_flip=False):
        """Flip one character of target_str in the file and assert replay
        refuses with decision-row-digest-mismatch naming the stored row_id.
        For hex fields, flip to a different valid hex char so the validity
        check passes and the digest mismatch is hit."""
        data = good_bytes.decode("utf-8")
        pos = data.index(target_str)
        c = data[pos]
        if hex_flip:
            replacement = "b" if c != "b" else "c"
        else:
            replacement = "X" if c != "X" else "Y"
        tampered = data[:pos] + replacement + data[pos + 1:]
        ledger.write_bytes(tampered.encode("utf-8"))
        with pytest.raises(DecisionStateError) as exc:
            replay(ledger)
        # R8 amendment: exact reason, never "decision-ledger-unparseable".
        assert exc.value.reason == "decision-row-digest-mismatch", (
            f"{label}: {exc.value}"
        )
        ledger.write_bytes(good_bytes)  # restore

    _flip_in_file(row["incumbent_answer"], "incumbent_answer")
    # A state value (the 'file' key).
    state_val = row["state"]["file"]
    _flip_in_file(state_val, "state.file")
    _flip_in_file(row["source_ref"]["locator"], "source_ref.locator")
    _flip_in_file(row["source_ref"]["source_digest"][:16],
                  "source_ref.source_digest", hex_flip=True)
    _flip_in_file(row["row_id"][:16], "row_id", hex_flip=True)

    # --- In-memory tamper ---
    def _flip_in_memory(row_copy: dict, label: str):
        """An in-memory row with a flipped field: append refuses with
        decision-row-digest-mismatch, the file unchanged."""
        before = ledger.read_bytes()
        with pytest.raises(DecisionStateError) as exc:
            append(ledger, row_copy)
        assert exc.value.reason == "decision-row-digest-mismatch", (
            f"{label}: {exc.value}"
        )
        assert ledger.read_bytes() == before, f"{label}: file changed"

    # Flip incumbent_answer.
    bad = dict(row)
    bad["incumbent_answer"] = row["incumbent_answer"][:-1] + "X"
    _flip_in_memory(bad, "mem:incumbent_answer")

    # Flip a state value.
    bad = dict(row)
    bad["state"] = dict(row["state"])
    bad["state"]["file"] = row["state"]["file"][:-1] + "X"
    _flip_in_memory(bad, "mem:state.file")

    # Flip source_ref.locator.
    bad = dict(row)
    bad["source_ref"] = dict(row["source_ref"])
    bad["source_ref"]["locator"] = row["source_ref"]["locator"][:-1] + "X"
    _flip_in_memory(bad, "mem:source_ref.locator")

    # Flip source_ref.source_digest.
    bad = dict(row)
    bad["source_ref"] = dict(row["source_ref"])
    sd = row["source_ref"]["source_digest"]
    bad["source_ref"]["source_digest"] = ("b" if sd[0] == "a" else "a") + sd[1:]
    _flip_in_memory(bad, "mem:source_ref.source_digest")

    # Flip row_id.
    bad = dict(row)
    rid = row["row_id"]
    bad["row_id"] = ("b" if rid[0] == "a" else "a") + rid[1:]
    _flip_in_memory(bad, "mem:row_id")


# ---------------------------------------------------------------------------
# State not canonical: an un-normalized state and an unredacted secret, both
# with consistent digests.
# ---------------------------------------------------------------------------


def test_state_not_canonical(tmp_path):
    from agent_factory.decisions.ledger import append

    ledger = tmp_path / "ledger.jsonl"

    # 1. Un-normalized state (double whitespace in a field).
    unnormed = {
        "file": "src/a.py",
        "kind": "k",
        "msg": "a  double  space",  # not collapsed
    }
    # Build a row manually with consistent digests but an un-normalized state.
    sd = hashlib.sha256(canonical(unnormed).encode("utf-8")).hexdigest()
    src = _fake_source_ref()
    identity = {
        "producer": "decide-harvest/incident-log",
        "question_id": "b1.finding_sev",
        "state_digest": sd,
        "source_ref": {
            "kind": src["kind"],
            "path": src["path"],
            "locator": src["locator"],
        },
    }
    rid = hashlib.sha256(canonical(identity).encode("utf-8")).hexdigest()
    row = {
        "calibration_state": "incumbent",
        "checkpoint_digest": "none",
        "incumbent_answer": "accepted",
        "producer": "decide-harvest/incident-log",
        "question_id": "b1.finding_sev",
        "source_ref": src,
        "state": unnormed,
        "state_digest": sd,
        "row_id": rid,
    }
    row["row_digest"] = hashlib.sha256(
        canonical(row).encode("utf-8")
    ).hexdigest()
    with pytest.raises(DecisionStateError, match="decision-row-state-not-canonical"):
        append(ledger, row)

    # 2. Unredacted secret with consistent digests.
    secret_state = {
        "file": "src/a.py",
        "kind": "k",
        "msg": "key is sk-abcdef1234567890",
    }
    sd2 = hashlib.sha256(canonical(secret_state).encode("utf-8")).hexdigest()
    identity2 = {
        "producer": "decide-harvest/incident-log",
        "question_id": "b1.finding_sev",
        "state_digest": sd2,
        "source_ref": {
            "kind": src["kind"],
            "path": src["path"],
            "locator": src["locator"],
        },
    }
    rid2 = hashlib.sha256(canonical(identity2).encode("utf-8")).hexdigest()
    row2 = {
        "calibration_state": "incumbent",
        "checkpoint_digest": "none",
        "incumbent_answer": "accepted",
        "producer": "decide-harvest/incident-log",
        "question_id": "b1.finding_sev",
        "source_ref": src,
        "state": secret_state,
        "state_digest": sd2,
        "row_id": rid2,
    }
    row2["row_digest"] = hashlib.sha256(
        canonical(row2).encode("utf-8")
    ).hexdigest()
    with pytest.raises(DecisionStateError, match="decision-row-state-not-canonical"):
        append(ledger, row2)


# ---------------------------------------------------------------------------
# Unparseable lines: torn last line, non-JSON, valid JSON not canonical.
# ---------------------------------------------------------------------------


def test_unparseable_lines(tmp_path):
    from agent_factory.decisions.ledger import replay

    # Build a valid line first.
    row = _make_row_for_golden("b1.finding_sev")
    good_line = canonical(row).encode("utf-8") + b"\n"

    # 1. Torn last line (no trailing newline).
    ledger_torn = tmp_path / "torn.jsonl"
    ledger_torn.write_bytes(good_line + b'{"torn":')
    with pytest.raises(DecisionStateError) as exc:
        replay(ledger_torn)
    assert str(exc.value) == f"decision-ledger-unparseable: {ledger_torn}:2"

    # 2. Non-JSON line.
    ledger_bad = tmp_path / "bad.jsonl"
    ledger_bad.write_bytes(good_line + b"not json at all\n")
    with pytest.raises(DecisionStateError) as exc:
        replay(ledger_bad)
    assert str(exc.value) == f"decision-ledger-unparseable: {ledger_bad}:2"

    # 3. Valid JSON that is not canonical (spaces after colons on one line).
    not_canonical = json.dumps(row, separators=(", ", ": "),
                               sort_keys=True).encode("utf-8") + b"\n"
    assert not_canonical != canonical(row).encode("utf-8") + b"\n"
    ledger_nc = tmp_path / "nc.jsonl"
    ledger_nc.write_bytes(good_line + not_canonical)
    with pytest.raises(DecisionStateError) as exc:
        replay(ledger_nc)
    assert str(exc.value) == f"decision-ledger-unparseable: {ledger_nc}:2"


# ---------------------------------------------------------------------------
# Invalid fields.
# ---------------------------------------------------------------------------


def test_invalid_fields(tmp_path):
    from agent_factory.decisions.ledger import append

    ledger = tmp_path / "ledger.jsonl"
    base = _make_row_for_golden("b1.finding_sev")

    def _assert_invalid(row_copy, expected_field, label=""):
        with pytest.raises(DecisionStateError) as exc:
            append(ledger, row_copy)
        assert exc.value.reason == "decision-row-invalid", (
            f"{label}: {exc.value}"
        )
        assert expected_field in str(exc.value), (
            f"{label}: expected '{expected_field}' in '{exc.value}'"
        )

    # Another calibration_state.
    bad = dict(base)
    bad["calibration_state"] = "calibrated"
    _assert_invalid(bad, "calibration_state=", "cal_state")

    # Another checkpoint_digest.
    bad = dict(base)
    bad["checkpoint_digest"] = "abc123"
    _assert_invalid(bad, "checkpoint_digest=", "chk_digest")

    # Unknown kind.
    bad = dict(base)
    bad["source_ref"] = dict(base["source_ref"])
    bad["source_ref"]["kind"] = "unknown_kind"
    _assert_invalid(bad, "source_ref.kind=", "unknown_kind")

    # Absolute path.
    bad = dict(base)
    bad["source_ref"] = dict(base["source_ref"])
    bad["source_ref"]["path"] = "/etc/passwd"
    _assert_invalid(bad, "source_ref.path=", "abs_path")

    # A ".." path segment.
    bad = dict(base)
    bad["source_ref"] = dict(base["source_ref"])
    bad["source_ref"]["path"] = "docs/../etc/passwd"
    _assert_invalid(bad, "source_ref.path=", "dotdot_path")

    # Non-hex digest.
    bad = dict(base)
    bad["state_digest"] = "zzzz" + "0" * 60
    _assert_invalid(bad, "state_digest=", "non_hex_digest")


# ---------------------------------------------------------------------------
# Append-only prefix: after K more appends the first N lines stay identical.
# ---------------------------------------------------------------------------


def test_append_only_prefix(tmp_path):
    from agent_factory.decisions.ledger import append

    ledger = tmp_path / "ledger.jsonl"
    # Append the first 3 rows.
    for qid in GOLDEN_IDS[:3]:
        append(ledger, _make_row_for_golden(qid))
    prefix = ledger.read_bytes()

    # Append 4 more rows.
    for qid in GOLDEN_IDS[3:]:
        append(ledger, _make_row_for_golden(qid))
    full = ledger.read_bytes()
    assert full[:len(prefix)] == prefix, "the first N lines changed after K appends"


# ---------------------------------------------------------------------------
# Corrupt ledger not appended: a tampered file + a valid append => replay
# refusal, the file unchanged.
# ---------------------------------------------------------------------------


def test_corrupt_ledger_not_appended(tmp_path):
    from agent_factory.decisions.ledger import append

    ledger = tmp_path / "ledger.jsonl"
    row_a = _make_row_for_golden("b1.finding_sev")
    append(ledger, row_a)

    # Tamper the file.
    data = ledger.read_bytes()
    tampered = data.replace(b"accepted", b"rejectXd")
    ledger.write_bytes(tampered)
    before = ledger.read_bytes()

    # A valid new row: append must refuse (replay fails), file unchanged.
    row_b = _make_row_for_golden("b2.hit_role")
    with pytest.raises(DecisionStateError):
        append(ledger, row_b)
    assert ledger.read_bytes() == before, "corrupt ledger was modified by failed append"


# ---------------------------------------------------------------------------
# J1-1 refusals propagate through make_row.
# ---------------------------------------------------------------------------


def test_j1_1_refusals_propagate():
    from agent_factory.decisions.ledger import make_row

    # Unknown question.
    with pytest.raises(DecisionStateError) as exc:
        make_row(
            producer="p",
            question_id="x.unknown",
            raw_state={},
            incumbent_answer="a",
            source_ref=_fake_source_ref(),
            root=None,
        )
    assert str(exc.value) == "decision-question-unknown: x.unknown"

    # Unknown key in state.
    with pytest.raises(DecisionStateError) as exc:
        make_row(
            producer="p",
            question_id="b1.finding_sev",
            raw_state={"file": "a.py", "kind": "k", "msg": "m", "extra": "x"},
            incumbent_answer="a",
            source_ref=_fake_source_ref(),
            root=None,
        )
    assert str(exc.value) == "decision-state-unknown-key: b1.finding_sev.extra"


# ---------------------------------------------------------------------------
# R1: short write refused, file truncated back (hostile table rows 1-4).
# ---------------------------------------------------------------------------


def test_short_write_spy(tmp_path):
    """Row 1: os.write forced to write 50 of 693 bytes; row 2: writes 0."""
    from agent_factory.decisions.ledger import append, replay
    from unittest.mock import patch

    ledger = tmp_path / "ledger.jsonl"
    # Build a 2-row ledger first.
    row_a = _make_row_for_golden("b1.finding_sev")
    row_b = _make_row_for_golden("b1.finding_kind")
    append(ledger, row_a)
    append(ledger, row_b)
    before_bytes = ledger.read_bytes()

    # Row 1: spy that writes first 50 bytes for real.
    row_c = _make_row_for_golden("b2.hit_role")
    line_c = canonical(row_c) + "\n"
    expected_len = len(line_c.encode("utf-8"))

    real_write = os.write

    def spy_50(fd, data):
        return real_write(fd, data[:50])

    with patch("agent_factory.decisions.ledger.os.write", side_effect=spy_50):
        with pytest.raises(DecisionStateError) as exc:
            append(ledger, row_c)
        assert str(exc.value) == (
            f"decision-ledger-short-write: {ledger}:50/{expected_len}"
        )

    # File must be restored to the 2-row state.
    assert ledger.read_bytes() == before_bytes
    # Replay returns the 2 rows.
    replayed = replay(ledger)
    assert len(replayed) == 2
    # Next good append succeeds.
    rid = append(ledger, row_c)
    assert rid == row_c["row_id"]

    # Row 2: spy that writes 0 bytes.
    row_d = _make_row_for_golden("d1.bug_echo_scores")
    line_d = canonical(row_d) + "\n"
    expected_len_d = len(line_d.encode("utf-8"))
    before_3 = ledger.read_bytes()

    def spy_0(fd, data):
        return 0

    with patch("agent_factory.decisions.ledger.os.write", side_effect=spy_0):
        with pytest.raises(DecisionStateError) as exc:
            append(ledger, row_d)
        assert str(exc.value) == (
            f"decision-ledger-short-write: {ledger}:0/{expected_len_d}"
        )
    assert ledger.read_bytes() == before_3


def test_short_write_real_tmpfs(tmp_path):
    """Row 3: real 4 KiB tmpfs filled until a row only partly fits.
    Row 4: filled to the byte, one more append => OSError ENOSPC."""
    import subprocess
    import errno as errno_mod

    # Skip if not root or mount fails.
    if os.geteuid() != 0:
        pytest.skip("test_short_write_real_tmpfs: not root, cannot mount tmpfs")

    from agent_factory.decisions.ledger import append, replay

    tmpfs_dir = tmp_path / "tmpfs"
    tmpfs_dir.mkdir()
    try:
        result = subprocess.run(
            ["mount", "-t", "tmpfs", "-o", "size=4k", "none", str(tmpfs_dir)],
            capture_output=True,
        )
        if result.returncode != 0:
            pytest.skip(
                f"test_short_write_real_tmpfs: mount failed rc={result.returncode}"
            )

        ledger = tmpfs_dir / "ledger.jsonl"
        appended = []
        # Append rows until one only partly fits.
        for i, qid in enumerate(GOLDEN_IDS):
            row = _make_row_for_golden(qid, producer=f"p/{i}")
            line_bytes = (canonical(row) + "\n").encode("utf-8")
            expected_len = len(line_bytes)
            try:
                rid = append(ledger, row)
                appended.append(rid)
            except DecisionStateError as exc:
                assert exc.reason == "decision-ledger-short-write"
                # The detail must be <path>:<n>/<len>.
                detail = str(exc).split(": ", 1)[1]
                assert f"/{expected_len}" in detail
                # File bytes unchanged from before this append.
                replayed = replay(ledger)
                assert len(replayed) == len(appended)
                break
            except OSError as exc_os:
                # Row 4: ENOSPC with nothing written.
                assert exc_os.errno == errno_mod.ENOSPC
                break
        else:
            pytest.fail("expected a short write or ENOSPC on a 4k tmpfs")

    finally:
        subprocess.run(["umount", str(tmpfs_dir)], capture_output=True)
        # Verify unmount.
        mounts = open("/proc/mounts").read()
        assert str(tmpfs_dir) not in mounts, "tmpfs not unmounted"


# ---------------------------------------------------------------------------
# R2: no bare exception from content (hostile table rows 5-7).
# ---------------------------------------------------------------------------


def test_replay_content_exceptions(tmp_path):
    """Rows 5-7: replay of corrupt lines that used to raise bare exceptions."""
    from agent_factory.decisions.ledger import replay

    row = _make_row_for_golden("b1.finding_kind")
    good_line = canonical(row).encode("utf-8") + b"\n"

    # Row 5a: scalar 1.
    p = tmp_path / "scalar1.jsonl"
    p.write_bytes(good_line + b"1\n")
    with pytest.raises(DecisionStateError) as exc:
        replay(p)
    assert str(exc.value) == f"decision-ledger-unparseable: {p}:2"

    # Row 5b: scalar string "calibration_state".
    p2 = tmp_path / "scalar_str.jsonl"
    p2.write_bytes(good_line + b'"calibration_state"\n')
    with pytest.raises(DecisionStateError) as exc:
        replay(p2)
    assert str(exc.value) == f"decision-ledger-unparseable: {p2}:2"

    # Row 5c: empty array [].
    p3 = tmp_path / "array.jsonl"
    p3.write_bytes(good_line + b"[]\n")
    with pytest.raises(DecisionStateError) as exc:
        replay(p3)
    assert str(exc.value) == f"decision-ledger-unparseable: {p3}:2"

    # Row 6a: lone surrogate escape.
    p4 = tmp_path / "surrogate.jsonl"
    # A JSON line with \ud800 escape — json.loads will produce the surrogate.
    p4.write_bytes(good_line + b'{"calibration_state":"\\ud800"}\n')
    with pytest.raises(DecisionStateError) as exc:
        replay(p4)
    assert str(exc.value) == f"decision-ledger-unparseable: {p4}:2"

    # Row 6b: raw bytes ED A0 80 inside a string value.
    p5 = tmp_path / "raw_surrogate.jsonl"
    # Build a JSON-like line with raw surrogate bytes.
    raw_bad = b'{"calibration_state":"abc' + b"\xed\xa0\x80" + b'"}\n'
    p5.write_bytes(good_line + raw_bad)
    with pytest.raises(DecisionStateError) as exc:
        replay(p5)
    assert str(exc.value) == f"decision-ledger-unparseable: {p5}:2"

    # Row 7a: 600-deep nesting.
    p6 = tmp_path / "deep600.jsonl"
    deep_600 = b"[" * 600 + b"1" + b"]" * 600 + b"\n"
    p6.write_bytes(good_line + deep_600)
    with pytest.raises(DecisionStateError) as exc:
        replay(p6)
    assert str(exc.value) == f"decision-ledger-unparseable: {p6}:2"

    # Row 7b: 100000-deep nesting.
    p7 = tmp_path / "deep100k.jsonl"
    deep_100k = b"[" * 100000 + b"1" + b"]" * 100000 + b"\n"
    p7.write_bytes(good_line + deep_100k)
    with pytest.raises(DecisionStateError) as exc:
        replay(p7)
    assert str(exc.value) == f"decision-ledger-unparseable: {p7}:2"


# ---------------------------------------------------------------------------
# R6: FIFO, symlink, directory (hostile table rows 8-10).
# ---------------------------------------------------------------------------


def test_fifo_refused(tmp_path):
    """Row 8: replay/append on a FIFO must not block."""
    import signal
    from agent_factory.decisions.ledger import append, replay

    fifo = tmp_path / "fifo.jsonl"
    os.mkfifo(str(fifo))

    # Use SIGALRM as a 10 s watchdog.
    old_handler = signal.signal(signal.SIGALRM, signal.SIG_DFL)
    signal.alarm(10)
    try:
        with pytest.raises(DecisionStateError) as exc:
            replay(fifo)
        assert str(exc.value) == f"decision-ledger-not-regular: {fifo}"

        row = _make_row_for_golden("b1.finding_sev")
        with pytest.raises(DecisionStateError) as exc:
            append(fifo, row)
        assert str(exc.value) == f"decision-ledger-not-regular: {fifo}"
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


def test_symlink_refused(tmp_path):
    """Row 9: symlink to valid ledger; dangling symlink."""
    from agent_factory.decisions.ledger import append, replay

    # Valid ledger through a symlink.
    real = tmp_path / "real.jsonl"
    row = _make_row_for_golden("b1.finding_sev")
    # Write via direct path.
    from agent_factory.decisions.ledger import append as direct_append
    direct_append(real, row)

    link = tmp_path / "link.jsonl"
    os.symlink(str(real), str(link))

    with pytest.raises(DecisionStateError) as exc:
        replay(link)
    assert str(exc.value) == f"decision-ledger-not-regular: {link}"

    with pytest.raises(DecisionStateError) as exc:
        append(link, _make_row_for_golden("b2.hit_role"))
    assert str(exc.value) == f"decision-ledger-not-regular: {link}"

    # Dangling symlink.
    dangling = tmp_path / "dangling.jsonl"
    dangling_target = tmp_path / "nonexistent.jsonl"
    os.symlink(str(dangling_target), str(dangling))

    with pytest.raises(DecisionStateError) as exc:
        replay(dangling)
    assert str(exc.value) == f"decision-ledger-not-regular: {dangling}"

    with pytest.raises(DecisionStateError) as exc:
        append(dangling, _make_row_for_golden("b1.finding_sev"))
    assert str(exc.value) == f"decision-ledger-not-regular: {dangling}"

    # The target must NOT exist afterwards.
    assert not dangling_target.exists(), "dangling symlink target was created"


def test_directory_refused(tmp_path):
    """Row 10: a directory at the path."""
    from agent_factory.decisions.ledger import append, replay

    adir = tmp_path / "adir"
    adir.mkdir()

    with pytest.raises(DecisionStateError) as exc:
        replay(adir)
    assert str(exc.value) == f"decision-ledger-not-regular: {adir}"

    with pytest.raises(DecisionStateError) as exc:
        append(adir, _make_row_for_golden("b1.finding_sev"))
    # Directory opens but is not S_ISREG.
    assert exc.value.reason == "decision-ledger-not-regular"


# ---------------------------------------------------------------------------
# R5 + R2: DirEntry of corrupt ledger, path types (hostile table rows 11-14).
# ---------------------------------------------------------------------------


def test_direntry_corrupt_ledger(tmp_path, monkeypatch):
    """Row 11: replay(os.DirEntry) of a 2-line ledger whose line 2 is garbage."""
    from agent_factory.decisions.ledger import replay

    # A str(DirEntry) bug resolves "<DirEntry 'ledger.jsonl'>" against the
    # working directory: pin it to tmp_path so the test never touches the repo.
    monkeypatch.chdir(tmp_path)

    row = _make_row_for_golden("b1.finding_sev")
    good_line = canonical(row).encode("utf-8") + b"\n"
    ledger = tmp_path / "ledger.jsonl"
    ledger.write_bytes(good_line + b"not valid json\n")

    # Get a DirEntry for the ledger.
    entries = list(os.scandir(str(tmp_path)))
    entry = [e for e in entries if e.name == "ledger.jsonl"][0]

    with pytest.raises(DecisionStateError) as exc:
        replay(entry)
    assert str(exc.value) == f"decision-ledger-unparseable: {entry.path}:2"


def test_path_types_refused(tmp_path):
    """Row 12: replay/append with None, 1, bytes, empty string, NUL string."""
    from agent_factory.decisions.ledger import append, replay

    row = _make_row_for_golden("b1.finding_sev")

    # None.
    with pytest.raises(DecisionStateError) as exc:
        replay(None)
    assert str(exc.value) == "decision-ledger-path-invalid: NoneType"

    with pytest.raises(DecisionStateError) as exc:
        append(None, row)
    assert str(exc.value) == "decision-ledger-path-invalid: NoneType"

    # int.
    with pytest.raises(DecisionStateError) as exc:
        replay(1)
    assert str(exc.value) == "decision-ledger-path-invalid: int"

    # bytes.
    with pytest.raises(DecisionStateError) as exc:
        replay(b"sub/rel.jsonl")
    assert str(exc.value) == "decision-ledger-path-invalid: bytes"

    # Empty string.
    with pytest.raises(DecisionStateError) as exc:
        replay("")
    assert str(exc.value) == "decision-ledger-path-invalid: empty"

    with pytest.raises(DecisionStateError) as exc:
        append("", row)
    assert str(exc.value) == "decision-ledger-path-invalid: empty"

    # NUL in string.
    with pytest.raises(DecisionStateError) as exc:
        replay("a\x00b")
    assert str(exc.value) == "decision-ledger-path-invalid: nul"

    with pytest.raises(DecisionStateError) as exc:
        append("a\x00b", row)
    assert str(exc.value) == "decision-ledger-path-invalid: nul"

    # Nothing created.
    assert not os.path.exists("./None")


def test_direntry_duplicate_refused(tmp_path, monkeypatch):
    """Row 13: append(DirEntry) of a duplicate row."""
    from agent_factory.decisions.ledger import append

    # A str(DirEntry) bug writes "<DirEntry 'ledger.jsonl'>" relative to the
    # working directory; with the cwd pinned here the junk check below sees it.
    monkeypatch.chdir(tmp_path)

    ledger = tmp_path / "ledger.jsonl"
    row = _make_row_for_golden("b1.finding_sev")
    append(ledger, row)

    # Get a DirEntry.
    entries = list(os.scandir(str(tmp_path)))
    entry = [e for e in entries if e.name == "ledger.jsonl"][0]

    with pytest.raises(DecisionStateError) as exc:
        append(entry, row)
    assert exc.value.reason == "decision-row-duplicate"
    assert row["row_id"] in str(exc.value)

    # No junk file created.
    files = os.listdir(str(tmp_path))
    assert files == ["ledger.jsonl"]


def test_non_dict_row_refused(tmp_path):
    """Row 14: append(path, 1) and append(path, None)."""
    from agent_factory.decisions.ledger import append

    ledger = tmp_path / "ledger.jsonl"

    with pytest.raises(DecisionStateError) as exc:
        append(ledger, 1)
    assert str(exc.value) == "decision-row-invalid: row=int"

    with pytest.raises(DecisionStateError) as exc:
        append(ledger, None)
    assert str(exc.value) == "decision-row-invalid: row=NoneType"


# ---------------------------------------------------------------------------
# R3: closed row shape (hostile table rows 15-16).
# ---------------------------------------------------------------------------


def test_extra_top_level_key_refused(tmp_path):
    """Row 15: a row with an extra top-level key, digests recomputed."""
    import hashlib as hl
    from agent_factory.decisions.ledger import append

    ledger = tmp_path / "ledger.jsonl"
    row = _make_row_for_golden("b1.finding_sev")
    extra_row = dict(row)
    extra_row["zz_extra"] = "value"
    # Recompute digests with the extra key.
    without = {k: v for k, v in extra_row.items() if k != "row_digest"}
    extra_row["row_digest"] = hl.sha256(
        canonical(without).encode("utf-8")
    ).hexdigest()

    with pytest.raises(DecisionStateError) as exc:
        append(ledger, extra_row)
    assert str(exc.value) == "decision-row-unknown-field: zz_extra"
    # Nothing written.
    assert not ledger.exists()


def test_extra_source_ref_key_refused(tmp_path):
    """Row 16: a row with an extra source_ref key."""
    import hashlib as hl
    from agent_factory.decisions.ledger import append

    ledger = tmp_path / "ledger.jsonl"
    row = _make_row_for_golden("b1.finding_sev")
    extra_row = dict(row)
    extra_row["source_ref"] = dict(row["source_ref"])
    extra_row["source_ref"]["zz_extra"] = "val"
    # Recompute digests.
    without = {k: v for k, v in extra_row.items() if k != "row_digest"}
    extra_row["row_digest"] = hl.sha256(
        canonical(without).encode("utf-8")
    ).hexdigest()

    with pytest.raises(DecisionStateError) as exc:
        append(ledger, extra_row)
    assert str(exc.value) == "decision-row-unknown-field: source_ref.zz_extra"


# ---------------------------------------------------------------------------
# R7: make_row refuses by name (hostile table rows 17-22).
# ---------------------------------------------------------------------------


def test_make_row_source_ref_missing_fields():
    """Row 17: make_row with source_ref missing kind/path/locator."""
    from agent_factory.decisions.ledger import make_row

    base_sr = _fake_source_ref()
    fixture = _load("b1.finding_sev")

    for sub in ["kind", "path", "locator"]:
        bad_sr = dict(base_sr)
        del bad_sr[sub]
        with pytest.raises(DecisionStateError) as exc:
            make_row(
                producer="p", question_id="b1.finding_sev",
                raw_state=fixture["state"], incumbent_answer="a",
                source_ref=bad_sr, root=None,
            )
        assert str(exc.value) == f"decision-row-incomplete: missing source_ref.{sub}"


def test_make_row_source_ref_none():
    """Row 18: make_row(source_ref=None)."""
    from agent_factory.decisions.ledger import make_row

    fixture = _load("b1.finding_sev")
    with pytest.raises(DecisionStateError) as exc:
        make_row(
            producer="p", question_id="b1.finding_sev",
            raw_state=fixture["state"], incumbent_answer="a",
            source_ref=None, root=None,
        )
    assert str(exc.value) == "decision-row-incomplete: missing source_ref.kind"


def test_make_row_producer_empty_and_none():
    """Row 19: make_row(producer="") and make_row(producer=None)."""
    from agent_factory.decisions.ledger import make_row

    fixture = _load("b1.finding_sev")
    for val in ["", None]:
        with pytest.raises(DecisionStateError) as exc:
            make_row(
                producer=val, question_id="b1.finding_sev",
                raw_state=fixture["state"], incumbent_answer="a",
                source_ref=_fake_source_ref(), root=None,
            )
        assert str(exc.value) == "decision-row-incomplete: missing producer", (
            f"producer={val!r}: {exc.value}"
        )


def test_make_row_incumbent_answer_bad():
    """Row 20: make_row(incumbent_answer=5) and make_row(incumbent_answer="")."""
    from agent_factory.decisions.ledger import make_row

    fixture = _load("b1.finding_sev")
    for val in [5, ""]:
        with pytest.raises(DecisionStateError) as exc:
            make_row(
                producer="p", question_id="b1.finding_sev",
                raw_state=fixture["state"], incumbent_answer=val,
                source_ref=_fake_source_ref(), root=None,
            )
        assert str(exc.value) == "decision-row-incomplete: missing incumbent_answer", (
            f"incumbent_answer={val!r}: {exc.value}"
        )


def test_make_row_invalid_kind_and_path():
    """Row 21: make_row with source_ref.kind='bogus' and path='/etc/passwd'."""
    from agent_factory.decisions.ledger import make_row

    fixture = _load("b1.finding_sev")

    # bogus kind.
    bad_sr = _fake_source_ref()
    bad_sr["kind"] = "bogus"
    with pytest.raises(DecisionStateError) as exc:
        make_row(
            producer="p", question_id="b1.finding_sev",
            raw_state=fixture["state"], incumbent_answer="a",
            source_ref=bad_sr, root=None,
        )
    assert str(exc.value) == "decision-row-invalid: source_ref.kind=bogus"

    # Absolute path.
    bad_sr2 = _fake_source_ref()
    bad_sr2["path"] = "/etc/passwd"
    with pytest.raises(DecisionStateError) as exc:
        make_row(
            producer="p", question_id="b1.finding_sev",
            raw_state=fixture["state"], incumbent_answer="a",
            source_ref=bad_sr2, root=None,
        )
    assert str(exc.value) == "decision-row-invalid: source_ref.path=/etc/passwd"


def test_make_row_lone_surrogate():
    """Row 22: lone surrogate in locator, incumbent_answer, raw_state."""
    from agent_factory.decisions.ledger import make_row

    fixture = _load("b1.finding_sev")

    # locator with lone surrogate.
    bad_sr = _fake_source_ref()
    bad_sr["locator"] = "abc\ud800def"
    with pytest.raises(DecisionStateError) as exc:
        make_row(
            producer="p", question_id="b1.finding_sev",
            raw_state=fixture["state"], incumbent_answer="a",
            source_ref=bad_sr, root=None,
        )
    assert str(exc.value) == (
        "decision-row-invalid: source_ref.locator=UnicodeEncodeError"
    )

    # incumbent_answer with lone surrogate.
    with pytest.raises(DecisionStateError) as exc:
        make_row(
            producer="p", question_id="b1.finding_sev",
            raw_state=fixture["state"],
            incumbent_answer="abc\ud83ddef",
            source_ref=_fake_source_ref(), root=None,
        )
    assert str(exc.value) == (
        "decision-row-invalid: incumbent_answer=UnicodeEncodeError"
    )

    # raw_state['file'] with lone surrogate.
    bad_state = dict(fixture["state"])
    bad_state["file"] = "abc\ud800def"
    with pytest.raises(DecisionStateError) as exc:
        make_row(
            producer="p", question_id="b1.finding_sev",
            raw_state=bad_state, incumbent_answer="a",
            source_ref=_fake_source_ref(), root=None,
        )
    assert str(exc.value) == "decision-row-invalid: state=UnicodeEncodeError"


# ---------------------------------------------------------------------------
# R4: path spellings (hostile table rows 23-24).
# ---------------------------------------------------------------------------


def test_path_spellings_refused(tmp_path):
    """Row 23: various path spellings that must be refused by make_row AND
    by append of a hand-built row."""
    from agent_factory.decisions.ledger import append, make_row
    import hashlib as hl

    fixture = _load("b1.finding_sev")

    bad_paths = [
        "./docs/INCIDENT-LOG.md",
        "docs//INCIDENT-LOG.md",
        "docs/./INCIDENT-LOG.md",
        "docs/INCIDENT-LOG.md/",
        "~/x",
        " docs/x ",
        ".",
        "C:/x",
        "a\tb",
        "a\u2028b",
        "a\x00b",
    ]

    for path in bad_paths:
        # make_row must refuse.
        sr = _fake_source_ref()
        sr["path"] = path
        with pytest.raises(DecisionStateError) as exc:
            make_row(
                producer="p", question_id="b1.finding_sev",
                raw_state=fixture["state"], incumbent_answer="a",
                source_ref=sr, root=None,
            )
        err_str = str(exc.value)
        assert ("decision-row-invalid" in err_str
                or "decision-row-incomplete" in err_str
                or "decision-ledger-path-invalid" in err_str), (
            f"path={path!r}: {exc.value}"
        )

    # Also test append with a hand-built row for the non-NUL paths.
    for path in bad_paths:
        if "\x00" in path:
            continue  # NUL is caught at path-level, not row-level
        sr = _fake_source_ref()
        sr["path"] = path
        # Build a row manually, bypassing make_row.
        row = dict(_make_row_for_golden("b1.finding_sev"))
        row["source_ref"] = dict(row["source_ref"])
        row["source_ref"]["path"] = path
        # Recompute identity and digests.
        try:
            row["state_digest"] = hl.sha256(
                canonical(row["state"]).encode("utf-8")
            ).hexdigest()
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
            row["row_id"] = hl.sha256(
                canonical(identity).encode("utf-8")
            ).hexdigest()
            without = {k: v for k, v in row.items() if k != "row_digest"}
            row["row_digest"] = hl.sha256(
                canonical(without).encode("utf-8")
            ).hexdigest()
        except Exception:
            continue  # canonical may refuse; that's fine

        ledger = tmp_path / f"path_{hash(path) & 0xFFFFFF:06x}.jsonl"
        with pytest.raises(DecisionStateError) as exc:
            append(ledger, row)
        assert "decision-row-invalid" in str(exc.value), (
            f"append path={path!r}: {exc.value}"
        )


def test_path_spellings_accepted():
    """Row 24: valid paths that must still be accepted."""
    from agent_factory.decisions.ledger import make_row

    fixture = _load("b1.finding_sev")
    good_paths = [
        "docs/INCIDENT-LOG.md",
        "a/..b",
        "%2e%2e/a",
        "a/b.c",
    ]
    for path in good_paths:
        sr = _fake_source_ref()
        sr["path"] = path
        row = make_row(
            producer="p", question_id="b1.finding_sev",
            raw_state=fixture["state"], incumbent_answer="a",
            source_ref=sr, root=None,
        )
        assert row["source_ref"]["path"] == path


# ---------------------------------------------------------------------------
# R8: exact-string assertions on existing tests, uppercase hex, 80/81 chars,
#     duplicate in file, unterminated last line, fsync spy.
# ---------------------------------------------------------------------------


def test_tamper_exact_strings(tmp_path):
    """R8: each file flip -> decision-row-digest-mismatch: <the stored row_id>."""
    from agent_factory.decisions.ledger import append, replay

    ledger = tmp_path / "ledger.jsonl"
    row = _make_row_for_golden("b1.finding_sev")
    append(ledger, row)
    good_bytes = ledger.read_bytes()
    stored_row_id = row["row_id"]

    def _flip_and_check(target_str, *, hex_flip=False, is_row_id=False):
        data = good_bytes.decode("utf-8")
        pos = data.index(target_str)
        c = data[pos]
        repl = ("b" if c != "b" else "c") if hex_flip else ("X" if c != "X" else "Y")
        tampered = data[:pos] + repl + data[pos + 1:]
        ledger.write_bytes(tampered.encode("utf-8"))
        with pytest.raises(DecisionStateError) as exc:
            replay(ledger)
        # R8: exact reason, never re-labelled unparseable (kills M19).
        expected_reason = "decision-row-digest-mismatch"
        assert exc.value.reason == expected_reason, (
            f"expected {expected_reason}, got {exc.value.reason}: {exc.value}"
        )
        if not is_row_id:
            # For non-row_id flips, the carried row_id is unchanged.
            assert str(exc.value) == f"{expected_reason}: {stored_row_id}"
        ledger.write_bytes(good_bytes)

    _flip_and_check(row["incumbent_answer"])
    _flip_and_check(row["source_ref"]["locator"])
    _flip_and_check(row["source_ref"]["source_digest"][:16], hex_flip=True)
    _flip_and_check(row["row_id"][:16], hex_flip=True, is_row_id=True)


def test_uppercase_hex_refused(tmp_path):
    """R8: uppercase hex in source_digest, state_digest, row_id."""
    from agent_factory.decisions.ledger import append

    ledger = tmp_path / "ledger.jsonl"
    row = _make_row_for_golden("b1.finding_sev")

    # Uppercase source_digest.
    bad = dict(row)
    bad["source_ref"] = dict(row["source_ref"])
    bad["source_ref"]["source_digest"] = "A" * 64
    with pytest.raises(DecisionStateError) as exc:
        append(ledger, bad)
    assert "source_ref.source_digest=" in str(exc.value)

    # Uppercase state_digest.
    bad2 = dict(row)
    bad2["state_digest"] = "B" * 64
    with pytest.raises(DecisionStateError) as exc:
        append(ledger, bad2)
    assert "state_digest=" in str(exc.value)

    # Uppercase row_id.
    bad3 = dict(row)
    bad3["row_id"] = "C" * 64
    with pytest.raises(DecisionStateError) as exc:
        append(ledger, bad3)
    assert "row_id=" in str(exc.value)


def test_value_80_and_81_chars(tmp_path):
    """R8: invalid value of exactly 80 and 81 chars in the detail."""
    from agent_factory.decisions.ledger import append

    ledger = tmp_path / "ledger.jsonl"
    row = _make_row_for_golden("b1.finding_sev")

    # 80-char value: detail carries all 80.
    val_80 = "x" * 80
    bad = dict(row)
    bad["calibration_state"] = val_80
    with pytest.raises(DecisionStateError) as exc:
        append(ledger, bad)
    assert f"calibration_state={val_80}" in str(exc.value)

    # 81-char value: detail carries only the first 80.
    val_81 = "y" * 81
    bad2 = dict(row)
    bad2["calibration_state"] = val_81
    with pytest.raises(DecisionStateError) as exc:
        append(ledger, bad2)
    assert f"calibration_state={val_81[:80]}" in str(exc.value)
    assert val_81 not in str(exc.value)


def test_duplicate_in_file(tmp_path):
    """R8: the same valid line twice in one file."""
    from agent_factory.decisions.ledger import replay

    row = _make_row_for_golden("b1.finding_sev")
    good_line = canonical(row).encode("utf-8") + b"\n"
    ledger = tmp_path / "dup.jsonl"
    ledger.write_bytes(good_line + good_line)

    with pytest.raises(DecisionStateError) as exc:
        replay(ledger)
    assert str(exc.value) == f"decision-row-duplicate: {row['row_id']}"


def test_unterminated_last_line(tmp_path):
    """R8: a complete valid row as the last line without its newline."""
    from agent_factory.decisions.ledger import replay

    row = _make_row_for_golden("b1.finding_sev")
    good_line = canonical(row).encode("utf-8")
    ledger = tmp_path / "noterm.jsonl"
    # No trailing newline.
    ledger.write_bytes(good_line)

    with pytest.raises(DecisionStateError) as exc:
        replay(ledger)
    assert str(exc.value) == f"decision-ledger-unparseable: {ledger}:1"


def test_fsync_called_once_per_append(tmp_path):
    """R8: one os.fsync call on the ledger's fd per successful append."""
    from agent_factory.decisions.ledger import append
    from unittest.mock import patch

    ledger = tmp_path / "ledger.jsonl"
    row = _make_row_for_golden("b1.finding_sev")

    fsync_calls = []
    real_fsync = os.fsync

    def spy_fsync(fd):
        fsync_calls.append(fd)
        return real_fsync(fd)

    with patch("agent_factory.decisions.ledger.os.fsync", side_effect=spy_fsync):
        append(ledger, row)

    assert len(fsync_calls) == 1, f"expected 1 fsync call, got {len(fsync_calls)}"


# ---------------------------------------------------------------------------
# J1-1-R1 (D-056, A3 + A5): an over-limit state whose bounded field carries a
# secret that straddles the limit goes through the REAL make_row -> append ->
# replay path. Every secret is FAKE; a secret body uses only the letters
# Q Z X J, which no other byte of these rows contains (the digests are
# lower-case hex), so the ledger file is searched one character at a time.
# ---------------------------------------------------------------------------


def test_over_limit_straddling_secret_appends_and_replays(tmp_path):
    """make_row then append: the row is accepted, the ledger file's bytes
    hold no byte of any secret body, replay verifies every row, and the
    fixed-point check (run by append and by replay) accepts each one --
    VERIFY-J1-1 F-9: both ledger call sites use decision_state."""
    from agent_factory.decisions.ledger import append, make_row, replay

    body = "QZXJ" * 12  # 48 FAKE characters
    limit = 400  # ap.violates_row.action_excerpt

    def straddle(secret, k):
        # The secret's first k characters sit before the limit, the rest after.
        return "a" * (limit - k - 1) + " " + secret + " tail"

    pem = "-----BEGIN RSA PRIVATE KEY-----\n" + "\n".join(body for _ in range(30))
    gpg = "-----BEGIN PGP PRIVATE KEY BLOCK-----\n" + "\n".join(body for _ in range(30))
    cases = [
        ("sk, 7 body characters before the limit", straddle("sk-" + body, 10)),
        ("bearer, 15 body characters before the limit", straddle("Bearer " + body, 22)),
        ("token run, 31 characters before the limit", straddle("token: " + body[:40], 38)),
        ("token assignment C-F3a", straddle("AGENT_TOKEN: " + body[:40], 30)),
        ("env assignment C-F3b", straddle("password: " + body, 20)),
        ("a TOKEN name with a short value (the D-1 ruling)", straddle("SECRET_TOKEN = " + body[:20], 25)),
        ("a base64url token value (the D-1 ruling)", straddle("token: " + body[:16] + "-" + body[16:32], 20)),
        ("the cut lands inside the envval placeholder", straddle("API_KEY=" + body, 15)),
        ("a PEM block of 1,500 characters", "see " + pem + "\n-----END RSA PRIVATE KEY----- tail"),
        ("GnuPG armor", "see " + gpg + "\n-----END PGP PRIVATE KEY BLOCK----- tail"),
        ("a PEM block with no END line", "a" * 390 + " " + pem),
        ("F-3: the cut lands right after a space", "a" * 399 + " b"),
    ]
    ledger = tmp_path / "ledger.jsonl"
    rows = []
    for name, excerpt in cases:
        raw_state = {
            "action_kind": "edit",
            "action_target": "a/b.py",
            "action_excerpt": excerpt,
            "row_id": "AF-AP-1",
            "row_title": "t",
        }
        source_ref = dict(_fake_source_ref(), locator="straddle case " + name)
        row = make_row(
            producer="decide-harvest/incident-log",
            question_id="ap.violates_row",
            raw_state=raw_state,
            incumbent_answer="accepted",
            source_ref=source_ref,
            root=None,
        )
        assert append(ledger, row) == row["row_id"], name
        leaked = sorted(set(ledger.read_text(encoding="utf-8")) & set("QZXJ"))
        assert not leaked, f"{name}: secret body bytes {leaked} reached the ledger file"
        assert len(row["state"]["action_excerpt"]) <= limit, name
        rows.append(row)
    assert replay(ledger) == rows


# ---------------------------------------------------------------------------
# J1-1-R2 (D-057, B1 + B2): the brief's appendix driver as tests
# (tasks/briefs/laya/J1-1-R2-brief.md). Each shape is b1.finding_sev's msg
# and goes through the REAL make_row -> append -> the JSONL line on disk ->
# replay. The bodies are FAKE "QZJ8" runs; the digests are lower-case hex and
# no other field holds an upper-case Q, Z or J, so the file is searched for
# those letters one character at a time.
# ---------------------------------------------------------------------------

_V = "QZJ8" * 5  # the driver's 20-character FAKE value body
_RUN = "QZJ8" * 10  # the driver's 40-character FAKE token run

# A secret NAME that the sk or bearer class swallowed freed its value at the
# PIN (VERIFY-J1-1-R1 V-1). Each row leaks at the PIN.
_V1_ROWS = [
    ("V1-a", f"task-password: {_V}"),
    ("V1-b", f"ask-password={_V}"),
    ("V1-c", f'"task-password": "{_V}"'),
    ("V1-d", f"desk-secret_key: {_V}"),
    ("V1-e", f"flask-access_token={_RUN}"),
    ("V1-f", "disk-PASSWORD=QZJ8QZ"),
    ("V1-g", f"bearer my-service-password: {_V}"),
    ("V1-h", f"sk-abcdefgh-password={_V}"),
]
# The controls the PIN redacts, C-4 included (the verifier's option B leaks it).
_V1_CONTROLS = [
    ("C-1", f"mask-token: {_RUN}"),
    ("C-2", f"task-api_key: {_V}"),
    ("C-3", f"db_password={_V}"),
    ("C-4", f"Authorization: Bearer {_V}: rejected"),
    ("C-5", f"key sk-{_V} used"),
    ("C-6", f'"sk-{_V}"'),
]


def _append_driver_row(tmp_path, shape):
    """make_row -> append for one driver shape; the row, the file's text and
    replay's rows."""
    from agent_factory.decisions.ledger import append, make_row, replay

    fixture = _load("b1.finding_sev")
    row = make_row(
        producer="decide-harvest/incident-log",
        question_id="b1.finding_sev",
        raw_state=dict(fixture["state"], msg=f"set {shape} now"),
        incumbent_answer="accepted",
        source_ref=dict(_fake_source_ref(), locator="the V-1 driver"),  # no Q, Z or J here
        root=fixture.get("root"),
    )
    ledger = tmp_path / "ledger.jsonl"
    assert append(ledger, row) == row["row_id"]
    return row, ledger.read_text(encoding="utf-8"), replay(ledger)


def _assert_no_value_byte_on_disk(tmp_path, shape):
    row, text, replayed = _append_driver_row(tmp_path, shape)
    leaked = sorted(set(text) & set("QZJ"))
    assert not leaked, f"{shape!r}: value body bytes {leaked} reached the ledger file: {text!r}"
    assert "abcdefgh" not in text, f"{shape!r}: the sk value left its placeholder: {text!r}"
    assert replayed == [row], shape


@pytest.mark.parametrize("shape", [shape for _, shape in _V1_ROWS], ids=[row_id for row_id, _ in _V1_ROWS])
def test_v1_row_no_value_byte_reaches_the_ledger_file(tmp_path, shape):
    # B1: no byte of the value body is in the appended line on disk, and
    # replay accepts the row (its fixed-point check included).
    _assert_no_value_byte_on_disk(tmp_path, shape)


@pytest.mark.parametrize(
    "shape", [shape for _, shape in _V1_CONTROLS], ids=[row_id for row_id, _ in _V1_CONTROLS]
)
def test_v1_control_keeps_its_redaction_in_the_ledger_file(tmp_path, shape):
    # B2: green at the PIN and after; the negative control is a mutant (the
    # verifier's option-B bearer form leaks C-4's token into the file).
    _assert_no_value_byte_on_disk(tmp_path, shape)
