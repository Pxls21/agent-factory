"""DSV2 (task #251; D-083, D-085): scripts/laya_ft/recorded_labels.py writes a version-2 dataset's labels from the
answers its rows record, in the record shape teacher_label.py writes and common.join_labels checks.

Deterministic and LLM-free, in the project venv (the module imports no torch and no laya). The datasets here are small
version-2 datasets written by the builder's own make_row; the committed record at the PIN is checked in
tests/test_laya_ft.py (the Laya venv builds it)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from laya_ft import build_dataset as BD  # noqa: E402
from laya_ft import common as C  # noqa: E402
from laya_ft import recorded_labels as RL  # noqa: E402
from laya_ft import teacher_label as TL  # noqa: E402

SCRIPT = ROOT / "scripts" / "laya_ft" / "recorded_labels.py"
COMMIT_TIME = 1790270071
FINDING = {"kind": "verify_finding", "path": "tasks/briefs/x/VERIFY-X-report.md", "finding_id": "F-9", "family": "F3"}
INCIDENT = {"kind": "incident", "line": 3, "heading": "2026-01-01 — a FAKE incident (AF-AP-?)", "row": "AF-AP-2"}
COMMIT = {"kind": "commit", "commit": "c" * 40, "row": "AF-AP-2"}


def _rows():
    """One row per case, in the builder's own row format (make_row)."""
    ap = {"query": "a FAKE incident text", "chunk": "a mirror test passes"}
    return [
        BD.make_row("v1", "v1.finding_class", "a finding text", [dict(FINDING, answer="FOLLOW-UP",
                                                                      provenance="verifier-class")], None),
        BD.make_row("v1", "v1.blocking", "a finding text", [dict(FINDING, answer="false", provenance="verifier-class")],
                    None),
        BD.make_row("ap", "ap.violates_row", ap, [dict(INCIDENT, answer="true", provenance="heading-cite+body-cite")],
                    None),
        BD.make_row("ap", "ap.violates_row", dict(ap, chunk="disk space"),
                    [dict(INCIDENT, row="AF-AP-3", answer="false", provenance="not-cited")], None),
        BD.make_row("ap", "ap.violates_row", dict(ap, chunk="an entry that cites nothing"), [dict(INCIDENT)], None),
        BD.make_row("ap", "ap.violates_row", {"query": "a FAKE commit message", "chunk": "c"},   # a commit and its link
                    [dict(COMMIT, answer="true", provenance="registry-commit"),
                     {"kind": "incident", "heading": "a FAKE linked entry", "role": "linked"}], None),
        BD.make_row("v1", "v1.finding_class", "a finding two reports share",   # twins merged by fit_rows: one answer
                    [dict(FINDING, answer="INFO", provenance="verifier-class"),
                     dict(FINDING, path="tasks/briefs/pc/report-pc-verify-x.md", answer="INFO",
                          provenance="verifier-class")], None),
        BD.make_row("v1", "v1.finding_class", "a finding two sources disagree on",
                    [dict(FINDING, finding_id="F-10", answer="INFO", provenance="verifier-class"),
                     dict(FINDING, finding_id="F-11", answer="BLOCKER", provenance="verifier-class")], None),
    ]


def _dataset(ddir, rows, version=2, commit_time=COMMIT_TIME, summary=True):
    body = "".join(json.dumps(r, ensure_ascii=True) + "\n" for r in rows).encode("ascii")
    ddir.mkdir(parents=True, exist_ok=True)
    (ddir / "dataset.jsonl").write_bytes(body)
    manifest = {"version": version, "commit": "d" * 40, "commit_time": commit_time, "model": {},
                "counts": {"rows_total": len(rows)}, "sources": {}, "heldout": {}, "heading_body_agreement": {},
                "dataset": {"file": "dataset.jsonl", "sha256": C.sha256_hex(body), "bytes": len(body)}}
    (ddir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    if summary:
        (ddir / "summary.json").write_text(json.dumps({"from": "the builder"}), encoding="utf-8")
    return ddir


def _run(ddir, out, *extra):
    return subprocess.run([sys.executable, str(SCRIPT), "--dataset", str(ddir), "--out", str(out), *extra],
                          capture_output=True, text=True, timeout=120)


def _labels(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_a_record_has_the_teacher_records_keys_in_order(tmp_path):
    rows = _rows()
    r = _run(_dataset(tmp_path / "ds", rows), tmp_path / "labels.jsonl")
    assert r.returncode == 0, r.stderr

    class Client:   # teacher_label's client, minus the network: label_row itself builds the record
        endpoint, usage = "api.example.invalid", {"answers": 0}

        def ask(self, body):
            return {"model": "openjev-0.1", "answers": {"v1.finding_class": {
                "choice": "INFO", "probabilities": dict(zip(rows[0]["options"], [0, 0, 1, 0, 0, 0]))}}}, 1

    teacher = TL.label_row(Client(), rows[0])
    assert [list(rec) for rec in _labels(tmp_path / "labels.jsonl")] == [list(teacher)] * 6


def test_the_target_is_one_hot_on_the_recorded_answer_and_reads_back(tmp_path):
    rows = _rows()
    r = _run(_dataset(tmp_path / "ds", rows), tmp_path / "labels.jsonl")
    assert r.returncode == 0, r.stderr
    by_key = {C.label_key(row["item_id"], row["question_id"]): row for row in rows}
    expected = dict(zip([C.label_key(rows[i]["item_id"], rows[i]["question_id"]) for i in (0, 1, 2, 3, 5, 6)],
                        [("FOLLOW-UP", "verifier-class"), ("false", "verifier-class"),
                         ("true", "heading-cite+body-cite"), ("false", "not-cited"), ("true", "registry-commit"),
                         ("INFO", "verifier-class")]))   # rows 0 and 1 share a state: the key names the question too
    labels = _labels(tmp_path / "labels.jsonl")
    assert sorted(rec["key"] for rec in labels) == sorted(expected) and len(expected) == 6
    for rec in labels:
        row = by_key[rec["key"]]
        answer, provenance = expected[rec["key"]]
        assert rec["target"] == [1.0 if name == answer else 0.0 for name in row["options"]]   # one-hot, option order
        assert C.distribution(rec["answer"], row["question"]) == rec["target"]   # the teacher path reads it back
        assert (rec["sent_state_sha"], rec["question_sha"], rec["options"]) == (
            row["state_sha"], row["question_sha"], row["options"])
        assert (rec["model"], rec["endpoint"], rec["ts"], rec["input_tokens"], rec["attempts"]) == (
            "recorded", provenance, float(COMMIT_TIME), 0, 0)
    assert json.loads(r.stdout)["unlabeled"] == {"ap.violates_row|incident": 1}
    assert (json.loads(r.stdout)["labeled"], json.loads(r.stdout)["conflicts"]) == (6, 1)


def test_the_labels_join_every_labeled_row_and_a_stale_one_is_refused(tmp_path):
    rows = _rows()
    assert _run(_dataset(tmp_path / "ds", rows), tmp_path / "labels.jsonl").returncode == 0
    records, stats = C.read_labels(tmp_path / "labels.jsonl")
    assert len(C.join_labels(rows, records)) == stats["records"] == 6 and stats["torn"] == stats["duplicates"] == 0
    key = next(iter(records))
    with pytest.raises(C.LabelError, match="1 stale label"):   # the state changed after labeling
        C.join_labels(rows, dict(records, **{key: dict(records[key], sent_state_sha="0" * 64)}))


def test_the_same_dataset_gives_the_same_bytes(tmp_path):
    ddir = _dataset(tmp_path / "ds", _rows())
    assert _run(ddir, tmp_path / "a.jsonl").returncode == _run(ddir, tmp_path / "b.jsonl").returncode == 0
    assert (tmp_path / "a.jsonl").read_bytes() == (tmp_path / "b.jsonl").read_bytes()


def test_the_summary_carries_the_builders_counts_and_the_labels(tmp_path):
    r = _run(_dataset(tmp_path / "ds", _rows()), tmp_path / "labels.jsonl", "--summary", str(tmp_path / "s.json"))
    assert r.returncode == 0, r.stderr
    summary = json.loads((tmp_path / "s.json").read_text())
    assert summary["dataset_summary"] == {"from": "the builder"}
    assert summary["labels"]["by_question_answer"] == {"v1.finding_class|FOLLOW-UP": 1, "v1.finding_class|INFO": 1,
                                                       "v1.blocking|false": 1, "ap.violates_row|true": 2,
                                                       "ap.violates_row|false": 1}
    assert summary["labels"]["labels"]["sha256"] == C.sha256_hex((tmp_path / "labels.jsonl").read_bytes())
    r = _run(_dataset(tmp_path / "nosum", _rows(), summary=False), tmp_path / "l2.jsonl", "--summary",
             str(tmp_path / "s2.json"))
    assert (r.returncode, r.stderr.strip()) == (64, "recorded_labels: refused: DatasetError: %s has no summary.json"
                                                % (tmp_path / "nosum"))


@pytest.mark.parametrize(("case", "message"), [
    ("version-1", "is not a version-2 dataset (its rows record no answers)"),
    ("commit-time", "manifest commit_time '1790270071' is not a positive integer"),
    ("held-out", "1 held-out row(s) in the dataset (D-3)"),
    ("not-an-option", "recorded answer 'MAYBE' is not one of its options"),
    ("provenance", "unknown provenance ['a-guess']"),
])
def test_refusals_write_nothing(tmp_path, case, message):
    rows = _rows()
    kwargs = {}
    if case == "version-1":
        kwargs["version"] = None
    elif case == "commit-time":
        kwargs["commit_time"] = str(COMMIT_TIME)   # a string is never coerced (AF-AP-72)
    elif case == "held-out":
        j2c = json.loads((ROOT / "docs/research/findings/j2c-fulltext/sample.json").read_text())["sample"]
        path, fid = j2c[0]["source"].rsplit("#", 1)
        rows.append(BD.make_row("v1", "v1.blocking", "a held-out finding",
                                [dict(FINDING, path=path, finding_id=fid, answer="true", provenance="verifier-class")],
                                None))
    elif case == "not-an-option":
        rows[1]["sources"][0]["answer"] = "MAYBE"
    else:
        rows[0]["sources"][0]["provenance"] = "a-guess"
    out = tmp_path / "labels.jsonl"
    r = _run(_dataset(tmp_path / "ds", rows, **kwargs), out)
    assert r.returncode == 64 and message in r.stderr and r.stderr.startswith("recorded_labels: refused: ")
    assert not out.exists()


def test_the_module_imports_no_model_package():
    """recorded_labels runs in the project venv and in CI: nothing it imports pulls torch, transformers or laya."""
    probe = ("import sys; sys.path.insert(0, %r); import laya_ft.recorded_labels; "
             "print(sorted(m for m in ('torch', 'transformers', 'laya') if m in sys.modules))" % str(ROOT / "scripts"))
    assert subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True,
                          timeout=120).stdout.strip() == "[]"
    assert RL.MODEL == "recorded" and RL.PROVENANCES == BD.PROVENANCES
