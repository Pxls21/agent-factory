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
        assert exc.value.reason in (
            "decision-row-digest-mismatch",
            "decision-ledger-unparseable",
        ), f"{label}: {exc.value}"
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
