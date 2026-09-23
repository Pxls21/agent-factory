from __future__ import annotations

import ast
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

import pytest

from agent_factory.decisions import DecisionStateError, decision_state
from agent_factory.decisions.ledger import replay


ROOT = Path(os.environ.get("DECIDE_HARVEST_TEST_ROOT", Path(__file__).resolve().parents[1]))
SCRIPT = ROOT / "scripts" / "decide-harvest"
FIXTURE = ROOT / "tests" / "fixtures" / "decisions" / "sources"
GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "J1 fixture",
    "GIT_AUTHOR_EMAIL": "j1@example.invalid",
    "GIT_COMMITTER_NAME": "J1 fixture",
    "GIT_COMMITTER_EMAIL": "j1@example.invalid",
    "GIT_AUTHOR_DATE": "2026-01-01T00:00:00+00:00",
    "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+00:00",
}
TYPE_COUNTS = {
    "ap.violates_row": 3,
    "b1.finding_kind": 1,
    "b1.finding_sev": 1,
    "b2.hit_role": 1,
    "d1.bug_echo_scores": 1,
    "v1.finding_class": 2,
    "wf.drift": 1,
}
SUMMARY = (
    "harvest: 10 rows, per question type: ap.violates_row=3, "
    "b1.finding_kind=1, b1.finding_sev=1, b2.hit_role=1, "
    "d1.bug_echo_scores=1, v1.finding_class=2, wf.drift=1"
)
SOURCES = (
    "sources: 4 read (incident_log=1, lane_report=1, transcript_jsonl=1, "
    "verify_report=1), 0 with no records; refused: 0 records; skipped: 0 duplicates"
)


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
        env=GIT_ENV,
    )


def _commit(repo: Path, message: str) -> None:
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", message)


def _make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    shutil.copytree(FIXTURE, repo)
    (repo / "scripts").mkdir(exist_ok=True)
    shutil.copy2(SCRIPT, repo / "scripts" / "decide-harvest")
    shutil.copytree(ROOT / "src", repo / "src", dirs_exist_ok=True)
    _git(repo, "init", "-q")
    _commit(repo, "fixture")
    return repo


def _run(repo: Path, out: Path, *sources: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), "--out", str(out), *sources],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )


def _mutate_and_commit(repo: Path, path: str, old: str, new: str) -> None:
    target = repo / path
    text = target.read_text(encoding="utf-8")
    assert old in text
    target.write_text(text.replace(old, new, 1), encoding="utf-8")
    _commit(repo, f"mutate {path}")


def _rows_by_question(path: Path) -> dict[str, list[dict]]:
    rows = replay(path)
    grouped = {question_id: [] for question_id in TYPE_COUNTS}
    for row in rows:
        grouped[row["question_id"]].append(row)
    return grouped


def test_fixture_harvest_exact_rows_and_provenance(tmp_path):
    repo = _make_repo(tmp_path)
    out = tmp_path / "ledger.jsonl"
    result = _run(repo, out)

    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.splitlines() == [
        SUMMARY,
        "negatives: 0 (hand-labeled in J2)",
        SOURCES,
    ]
    grouped = _rows_by_question(out)
    assert {key: len(rows) for key, rows in grouped.items()} == TYPE_COUNTS
    expected = {
        "ap.violates_row": ("yes", "incident_log", "docs/INCIDENT-LOG.md", "2026-01-01 — AF-AP-1 happened"),
        "b1.finding_kind": ("logic-bug", "transcript_jsonl", "transcripts/x/t.jsonl", "result-review#R1"),
        "b1.finding_sev": ("H", "transcript_jsonl", "transcripts/x/t.jsonl", "result-review#R1"),
        "b2.hit_role": ("def", "transcript_jsonl", "transcripts/x/t.jsonl", "result-scout#H1"),
        "d1.bug_echo_scores": ("urgency=high;risk_fix=low;risk_no_fix=high;roi=excellent;blast=2-files;effort=small", "lane_report", "tasks/briefs/x/X-report.md", "1 @ AF-AP-1 bug echo"),
        "v1.finding_class": ("BLOCKER", "verify_report", "tasks/briefs/x/VERIFY-X-report.md", "F-1 @ Findings"),
        "wf.drift": ("yes", "lane_report", "tasks/briefs/x/X-report.md", "BOUNDARY DEVIATION @ Build"),
    }
    for question_id, want in expected.items():
        row = grouped[question_id][0]
        got = (
            row["incumbent_answer"],
            row["source_ref"]["kind"],
            row["source_ref"]["path"],
            row["source_ref"]["locator"],
        )
        assert got == want
    assert grouped["ap.violates_row"][0]["state"]["row_title"] == "uncommitted source accepted"


def test_registry_heading_accepts_the_committed_qualified_form(tmp_path):
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo,
        "docs/INCIDENT-LOG.md",
        "## ANTI-PATTERN REGISTRY",
        "## ANTI-PATTERN REGISTRY (owner mandate)",
    )
    out = tmp_path / "qualified-registry.jsonl"
    result = _run(repo, out, "docs/INCIDENT-LOG.md")
    assert result.returncode == 0
    assert result.stderr == ""
    assert len(replay(out)) == 2


def test_determinism_and_relanding_stability(tmp_path):
    repo = _make_repo(tmp_path)
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    assert _run(repo, first).returncode == 0
    assert _run(repo, second).returncode == 0
    assert first.read_bytes() == second.read_bytes()
    before = {(row["row_id"], row["state_digest"]) for row in replay(first)}
    before_source_digests = {row["source_ref"]["source_digest"] for row in replay(first)}

    for path in (
        "docs/INCIDENT-LOG.md",
        "tasks/briefs/x/VERIFY-X-report.md",
        "tasks/briefs/x/X-report.md",
        "transcripts/x/t.jsonl",
    ):
        target = repo / path
        if path.endswith(".jsonl"):
            target.write_text(target.read_text(encoding="utf-8").replace('"dispatch-scout"', '"dispatch-scout-v2"'), encoding="utf-8")
        else:
            target.write_text("\n" + target.read_text(encoding="utf-8"), encoding="utf-8")
    _commit(repo, "reland")
    relanded = tmp_path / "relanded.jsonl"
    assert _run(repo, relanded).returncode == 0
    after = {(row["row_id"], row["state_digest"]) for row in replay(relanded)}
    after_source_digests = {row["source_ref"]["source_digest"] for row in replay(relanded)}
    assert after == before
    assert after_source_digests.isdisjoint(before_source_digests)


def test_duplicate_rerun_prints_every_skip_and_preserves_bytes(tmp_path):
    repo = _make_repo(tmp_path)
    out = tmp_path / "ledger.jsonl"
    assert _run(repo, out).returncode == 0
    before = out.read_bytes()
    result = _run(repo, out)
    assert result.returncode == 0
    assert out.read_bytes() == before
    assert result.stdout.splitlines()[0].startswith("harvest: 0 rows, per question type:")
    assert result.stdout.splitlines()[-1].endswith("refused: 0 records; skipped: 10 duplicates")
    assert len(result.stderr.splitlines()) == 10
    assert all(line.startswith("decision-row-duplicate: ") for line in result.stderr.splitlines())


@pytest.mark.parametrize(
    ("path", "old", "new", "reason"),
    [
        (
            "docs/INCIDENT-LOG.md",
            "**2026-01-01 — AF-AP-1 happened**\n\nBody mentions AF-AP-2 but does not attribute it.\n\n- **2026-01-02",
            "**2026-01-01 — AF-AP-1 happened\nline 2\nline 3\nline 4\nline 5\nline 6\nline 7\nline 8\nline 9\nline 10\nline 11\n\n- **2026-01-02",
            "unterminated-heading",
        ),
        ("tasks/briefs/x/VERIFY-X-report.md", "| F-2 | INFO, SOLID |", "| F-2 | FOLLOW-UP / UNVERIFIED |", "bad-class"),
        ("docs/INCIDENT-LOG.md", "AF-AP-1 happened", "AF-AP-9 happened", "no-registry-row"),
        ("transcripts/x/t.jsonl", '\\\"n\\\":1}', '\\\"n\\\":2}', "n-mismatch"),
        ("transcripts/x/t.jsonl", '\\\"role\\\":\\\"def\\\"', '\\\"role\\\":\\\"helper\\\"', "unknown-role"),
        ("tasks/briefs/x/X-report.md", "| HIGH | LOW | HIGH | EXCELLENT |", "| HIGH | LOW | HIGH | AMAZING |", "bad-rating"),
    ],
)
def test_malformed_record_refused_by_name_and_other_rows_survive(tmp_path, path, old, new, reason):
    repo = _make_repo(tmp_path)
    _mutate_and_commit(repo, path, old, new)
    out = tmp_path / "ledger.jsonl"
    result = _run(repo, out)
    assert result.returncode == 3
    expected_lines = {
        "docs/INCIDENT-LOG.md": {10},
        "tasks/briefs/x/VERIFY-X-report.md": {8},
        "transcripts/x/t.jsonl": {2},
        "tasks/briefs/x/X-report.md": {10},
    }
    match = re.fullmatch(
        rf"harvest-source-unparseable: {re.escape(path)}:(\d+) \({re.escape(reason)}\)\n",
        result.stderr,
    )
    assert match is not None
    assert int(match.group(1)) in expected_lines[path]
    assert "refused: 1 records" in result.stdout
    assert replay(out)


def test_admission_untracked_modified_unknown_and_existing_out_untouched(tmp_path):
    repo = _make_repo(tmp_path)
    out = tmp_path / "ledger.jsonl"
    untracked = "tasks/briefs/x/NEW-report.md"
    (repo / untracked).write_text("# new\n", encoding="utf-8")
    result = _run(repo, out, untracked)
    assert (result.returncode, result.stderr) == (4, f"harvest-source-uncommitted: {untracked}\n")
    assert not out.exists()

    tracked = "tasks/briefs/x/X-report.md"
    original = (repo / tracked).read_text(encoding="utf-8")
    (repo / tracked).write_text(original.replace("# Build", "# Changed", 1), encoding="utf-8")
    out.write_bytes(b"keep\n")
    result = _run(repo, out, tracked)
    assert (result.returncode, result.stderr) == (4, f"harvest-source-uncommitted: {tracked}\n")
    assert out.read_bytes() == b"keep\n"

    result = _run(repo, out, "README.md")
    assert (result.returncode, result.stderr) == (5, "harvest-source-unknown: README.md\n")
    assert out.read_bytes() == b"keep\n"


def test_all_requested_sources_are_admitted_before_any_rows_are_written(tmp_path):
    repo = _make_repo(tmp_path)
    out = tmp_path / "out.jsonl"
    dirty = "tasks/briefs/x/X-report.md"
    target = repo / dirty
    target.write_text(
        target.read_text(encoding="utf-8").replace("# Build", "# Dirty", 1),
        encoding="utf-8",
    )
    result = _run(repo, out, "docs/INCIDENT-LOG.md", dirty)
    assert (result.returncode, result.stderr) == (4, f"harvest-source-uncommitted: {dirty}\n")
    assert not out.exists()


def test_subset_prints_all_seven_types_with_zeros(tmp_path):
    repo = _make_repo(tmp_path)
    result = _run(repo, tmp_path / "subset.jsonl", "docs/INCIDENT-LOG.md")
    assert result.returncode == 0
    assert result.stdout.splitlines()[0] == (
        "harvest: 2 rows, per question type: ap.violates_row=2, "
        "b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, "
        "d1.bug_echo_scores=0, v1.finding_class=0, wf.drift=0"
    )


def test_secret_text_is_redacted_through_make_row(tmp_path):
    repo = _make_repo(tmp_path)
    secret = "sk-1234567890abcdef"
    _mutate_and_commit(repo, "tasks/briefs/x/VERIFY-X-report.md", "the blocker", f"the blocker {secret}")
    _mutate_and_commit(repo, "transcripts/x/t.jsonl", "review finding", f"review finding {secret}")
    out = tmp_path / "ledger.jsonl"
    assert _run(repo, out).returncode == 0
    assert secret.encode() not in out.read_bytes()
    assert b"<redacted:sk>" in out.read_bytes()


def test_clean_tree_harvests_head_bytes(tmp_path):
    repo = _make_repo(tmp_path)
    out = tmp_path / "ledger.jsonl"
    result = _run(repo, out, "tasks/briefs/x/X-report.md")
    assert result.returncode == 0
    assert len(replay(out)) == 2
    assert _git(repo, "status", "--porcelain").stdout == ""


def test_source_bytes_come_from_head_after_admission(tmp_path):
    repo = _make_repo(tmp_path)
    source = "tasks/briefs/x/X-report.md"
    original = (repo / source).read_bytes()
    replacement = original.replace(b"# Build", b"# Changed", 1)
    probe = repo / "probe.py"
    probe.write_text(
        """
import hashlib
import os
from pathlib import Path
import runpy

source = Path(os.environ["SOURCE"])
original = source.read_bytes()
replacement = original.replace(b"# Build", b"# Changed", 1)
module = runpy.run_path(os.environ["SCRIPT"], run_name="decide_harvest_probe")
real = module["_regular_worktree_bytes"]
armed = iter((True, False))

def swap(root, path):
    data = real(root, path)
    if next(armed, False):
        source.write_bytes(replacement)
    return data

module["_regular_worktree_bytes"].__globals__["_regular_worktree_bytes"] = swap
ledger = __import__("agent_factory.decisions.ledger", fromlist=["replay"])
code = module["main"]([
    "--root", os.environ["ROOT"], "--out", os.environ["OUT"], os.environ["REL"]
])
rows = ledger.replay(os.environ["OUT"])
expected = hashlib.sha256(original).hexdigest()
if any(row["source_ref"]["source_digest"] != expected for row in rows):
    raise SystemExit(99)
raise SystemExit(code)
""".lstrip(),
        encoding="utf-8",
    )
    out = tmp_path / "head-only.jsonl"
    result = subprocess.run(
        [sys.executable, str(probe)],
        check=False,
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "ROOT": str(repo),
            "SCRIPT": str(SCRIPT),
            "SOURCE": str(repo / source),
            "REL": source,
            "OUT": str(out),
        },
    )
    assert result.returncode == 0
    assert len(replay(out)) == 2
    assert (repo / source).read_bytes() == replacement


def test_pc_report_lane_pin_is_normalized_only_by_decision_state(tmp_path):
    repo = _make_repo(tmp_path)
    source = repo / "tasks/briefs/x/report-pc-verify-k1.md--1234abc.md"
    source.write_text((repo / "tasks/briefs/x/VERIFY-X-report.md").read_text(encoding="utf-8"), encoding="utf-8")
    _commit(repo, "first pin")
    first = tmp_path / "first.jsonl"
    result = _run(repo, first, source.relative_to(repo).as_posix())
    assert result.returncode == 0
    rows = [row for row in replay(first) if row["question_id"] == "v1.finding_class"]
    assert {row["state"]["lane"] for row in rows} == {"pc-verify-k1.md"}
    assert all(not re.search(r"[0-9a-f]{7,}", row["state"]["lane"]) for row in rows)

    second_source = repo / "tasks/briefs/x/report-pc-verify-k1.md--7654def.md"
    second_source.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    _commit(repo, "second pin")
    second = tmp_path / "second.jsonl"
    result = _run(repo, second, second_source.relative_to(repo).as_posix())
    assert result.returncode == 0
    second_rows = [row for row in replay(second) if row["question_id"] == "v1.finding_class"]
    assert {row["state"]["lane"] for row in second_rows} == {"pc-verify-k1.md"}
    assert {row["source_ref"]["path"] for row in rows} != {row["source_ref"]["path"] for row in second_rows}


def test_report_path_suffixes_are_canonicalized_and_sorted(tmp_path):
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo,
        "tasks/briefs/x/VERIFY-X-report.md",
        "Evidence in `src/existing.py:7`; ignore `src/missing.py:9`.",
        "Evidence in `src/existing.py:8-10`, `src/existing.py:7`; ignore `src/missing.py:9`.",
    )
    out = tmp_path / "paths.jsonl"
    assert _run(repo, out, "tasks/briefs/x/VERIFY-X-report.md").returncode == 0
    row = next(row for row in replay(out) if row["question_id"] == "v1.finding_class" and row["state"]["finding_id"] == "F-1")
    assert row["state"]["paths"] == ["src/existing.py"]


def test_transcript_payload_field_types_fail_closed(tmp_path):
    repo = _make_repo(tmp_path)
    _mutate_and_commit(repo, "transcripts/x/t.jsonl", '\\\"line\\\":7', '\\\"line\\\":true')
    out = tmp_path / "out.jsonl"
    result = _run(repo, out, "transcripts/x/t.jsonl")
    assert result.returncode == 3
    assert result.stderr == "harvest-source-unparseable: transcripts/x/t.jsonl:2 (bad-payload)\n"
    assert len(replay(out)) == 2


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1 file", "blast=1-file"),
        ("2 files", "blast=2-files"),
        ("3+ files", "blast=3-plus-files"),
    ],
)
def test_bug_echo_blast_vocabulary(tmp_path, text, expected):
    repo = _make_repo(tmp_path)
    if text != "2 files":
        _mutate_and_commit(repo, "tasks/briefs/x/X-report.md", "2 files", text)
    out = tmp_path / "ratings.jsonl"
    assert _run(repo, out, "tasks/briefs/x/X-report.md").returncode == 0
    row = next(row for row in replay(out) if row["question_id"] == "d1.bug_echo_scores")
    assert expected in row["incumbent_answer"]


def test_reviewer_n_mismatch_is_refused(tmp_path):
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo,
        "transcripts/x/t.jsonl",
        '\\\"review finding\\\"]],\\\"n\\\":1}',
        '\\\"review finding\\\"]],\\\"n\\\":2}',
    )
    out = tmp_path / "reviewer-n.jsonl"
    result = _run(repo, out, "transcripts/x/t.jsonl")
    assert result.returncode == 3
    assert result.stderr == "harvest-source-unparseable: transcripts/x/t.jsonl:4 (n-mismatch)\n"
    assert len(replay(out)) == 1


def test_unknown_report_suffix_is_rejected(tmp_path):
    repo = _make_repo(tmp_path)
    source = repo / "tasks/briefs/x/report-pc-verify-x.md.bak"
    source.write_text("# not a declared report shape\n", encoding="utf-8")
    _commit(repo, "unknown shape")
    result = _run(repo, tmp_path / "out.jsonl", source.relative_to(repo).as_posix())
    assert (result.returncode, result.stderr) == (
        5,
        "harvest-source-unknown: tasks/briefs/x/report-pc-verify-x.md.bak\n",
    )


def test_non_pin_pc_verify_report_shape_is_harvested(tmp_path):
    repo = _make_repo(tmp_path)
    source = repo / "tasks/briefs/x/report-pc-verify-k1-h.md"
    source.write_text(
        (repo / "tasks/briefs/x/VERIFY-X-report.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    _commit(repo, "pc report")
    out = tmp_path / "pc.jsonl"
    result = _run(repo, out, source.relative_to(repo).as_posix())
    assert result.returncode == 0
    rows = [row for row in replay(out) if row["question_id"] == "v1.finding_class"]
    assert {row["state"]["lane"] for row in rows} == {"pc-verify-k1-h"}


def test_boundary_deviation_requires_the_declared_delimiter(tmp_path):
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo,
        "tasks/briefs/x/X-report.md",
        "- **BOUNDARY DEVIATION** — touched an extra fixture",
        "- **BOUNDARY DEVIATION** touched an extra fixture",
    )
    out = tmp_path / "boundary.jsonl"
    result = _run(repo, out, "tasks/briefs/x/X-report.md")
    assert result.returncode == 0
    assert all(row["question_id"] != "wf.drift" for row in replay(out))


def test_class_table_rejects_invalid_finding_id(tmp_path):
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo,
        "tasks/briefs/x/VERIFY-X-report.md",
        "| F-2 | INFO, SOLID |",
        "| bad id | INFO, SOLID |",
    )
    out = tmp_path / "bad-id.jsonl"
    result = _run(repo, out, "tasks/briefs/x/VERIFY-X-report.md")
    assert result.returncode == 3
    assert result.stderr == (
        "harvest-source-unparseable: tasks/briefs/x/VERIFY-X-report.md:8 "
        "(bad-finding-id)\n"
    )
    assert len(replay(out)) == 1


def test_hive_anchor_with_missing_tool_id_is_refused(tmp_path):
    repo = _make_repo(tmp_path)
    _mutate_and_commit(repo, "transcripts/x/t.jsonl", '"id":"tool-scout",', "")
    out = tmp_path / "missing-id.jsonl"
    result = _run(repo, out, "transcripts/x/t.jsonl")
    assert result.returncode == 3
    assert result.stderr == "harvest-source-unparseable: transcripts/x/t.jsonl:1 (bad-payload)\n"
    assert "refused: 1 records" in result.stdout
    assert len(replay(out)) == 2


def test_committed_output_path_is_refused_before_harvest(tmp_path):
    repo = _make_repo(tmp_path)
    output = repo / "tasks/briefs/x/X-report.md"
    before = output.read_bytes()
    result = _run(repo, output)
    assert result.returncode == 4
    assert result.stderr == "harvest-output-source-conflict: tasks/briefs/x/X-report.md\n"
    assert output.read_bytes() == before


def test_script_delegates_every_write_to_ledger_append():
    source = SCRIPT.read_text(encoding="utf-8")
    tree = ast.parse(source)
    ledger_import = next(
        node
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and node.module == "agent_factory.decisions.ledger"
    )
    assert {alias.name for alias in ledger_import.names} == {"append", "make_row"}
    write_calls = []
    append_calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "append":
            append_calls.append(node)
        if isinstance(node.func, ast.Name) and node.func.id in {"open", "os.open", "os.write"}:
            write_calls.append(node)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {
            "open",
            "write",
            "write_text",
            "write_bytes",
        }:
            write_calls.append(node)
    assert len(append_calls) == 1
    assert write_calls == []


def test_usage_errors_exit_64_with_one_stderr_line():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 64
    assert result.stdout == ""
    assert len(result.stderr.splitlines()) == 1


def test_fixture_negative_control_rejects_mutated_state():
    state = {
        "lane": "pc-verify-k1.md--1234abc",
        "finding_id": "F-1",
        "title": "title",
        "paths": [],
        "disposition": "UNKNOWN",
    }
    with pytest.raises(DecisionStateError) as exc:
        decision_state("v1.finding_class", state, ROOT)
    assert exc.value.reason == "decision-state-bad-enum"


def test_fixture_negative_control_exact_error_for_unknown_source(tmp_path):
    repo = _make_repo(tmp_path)
    result = _run(repo, tmp_path / "negative.jsonl", "not/a/source.txt")
    assert result.returncode == 5
    assert result.stdout == ""
    assert result.stderr == "harvest-source-unknown: not/a/source.txt\n"
    assert not (tmp_path / "negative.jsonl").exists()
