from __future__ import annotations

import ast
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import stat
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


def _run(
    repo: Path, out: Path, *sources: str, env: dict[str, str] | None = None, timeout: int = 60
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), "--out", str(out), *sources],
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def _mutate_and_commit(repo: Path, path: str, old: str, new: str) -> None:
    target = repo / path
    text = target.read_text(encoding="utf-8")
    assert old in text
    target.write_text(text.replace(old, new, 1), encoding="utf-8")
    _commit(repo, f"mutate {path}")


def _append_and_commit(repo: Path, path: str, text: str) -> None:
    target = repo / path
    target.write_text(target.read_text(encoding="utf-8") + text, encoding="utf-8")
    _commit(repo, f"append to {path}")


def _git_shim(tmp_path: Path, action: str) -> tuple[dict[str, str], Path]:
    """An environment whose PATH starts with a `git` shim that forwards every call to the real git and runs
    ACTION (one shell command) once, just before the harvester's SECOND `ls-tree`: the first git read after
    admission and after the `--out` lock and replay. Returns the environment and the `ls-tree` call counter."""
    real_git = shutil.which("git")
    assert real_git is not None
    shim_dir = tmp_path / "shim"
    shim_dir.mkdir()
    calls = shim_dir / "ls-tree-calls"
    calls.write_text("0\n", encoding="utf-8")
    shim = shim_dir / "git"
    shim.write_text(
        "#!/bin/sh\n"
        'if [ "$3" = ls-tree ]; then\n'
        f'  n=$(( $(cat "{calls}") + 1 )); echo "$n" > "{calls}"\n'
        f'  if [ "$n" -eq 2 ]; then {action} || exit 97; fi\n'
        "fi\n"
        f'exec "{real_git}" "$@"\n',
        encoding="utf-8",
    )
    shim.chmod(0o755)
    return {**os.environ, "PATH": f"{shim_dir}{os.pathsep}{os.environ['PATH']}"}, calls


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
    # S2 (F-07): a content-bearing field, not only the digest, comes from the admitted HEAD bytes.
    drift = [row for row in replay(out) if row["question_id"] == "wf.drift"]
    assert [row["source_ref"]["locator"] for row in drift] == ["BOUNDARY DEVIATION @ Build"]


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
    # R2 (F-02, D-064 (1)): `**` right after DEVIATION IS a declared delimiter, so this form is an anchor.
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
    drift = [row for row in replay(out) if row["question_id"] == "wf.drift"]
    assert [row["state"]["observed"] for row in drift] == [
        "touched an extra fixture because the contract required it"
    ]

    # The negative stays: no delimiter after DEVIATION is no anchor.
    _mutate_and_commit(
        repo,
        "tasks/briefs/x/X-report.md",
        "- **BOUNDARY DEVIATION** touched an extra fixture",
        "1. BOUNDARY DEVIATION touched an extra fixture",
    )
    out = tmp_path / "no-delimiter.jsonl"
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
    assert {alias.name for alias in ledger_import.names} == {"append", "make_row", "replay"}
    write_calls = []
    append_calls = []
    os_open_flags = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "append":
            append_calls.append(node)
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "open"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "os"
        ):
            # D-063 / R5 (a) and S1: the only opens are the `--out` lock (never written through) and the admission read.
            os_open_flags.append(sorted(n.attr for n in ast.walk(node.args[1]) if isinstance(n, ast.Attribute)))
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"open", "os.open", "os.write"}:
            write_calls.append(node)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {
            "open",
            "write",
            "write_text",
            "write_bytes",
            "ftruncate",
            "truncate",
            "pwrite",
            "writev",
        }:
            write_calls.append(node)
    assert len(append_calls) == 1
    assert write_calls == []
    assert sorted(os_open_flags) == [
        ["O_CLOEXEC", "O_CREAT", "O_NOFOLLOW", "O_NONBLOCK", "O_RDWR"],
        ["O_CLOEXEC", "O_NOFOLLOW", "O_NONBLOCK", "O_RDONLY"],
    ]


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


# --- J1-3-R1 (tasks/briefs/pc/pc-j1-3-r1.md): R1-R6, S1-S6 ---------------------------------------------------


@pytest.mark.parametrize(
    ("heading", "locator"),
    [
        (
            "**2026-01-11 — AF-AP-1 first line\ncontinues with AF-AP-2 here**\n",
            "2026-01-11 — AF-AP-1 first line continues with AF-AP-2 here",
        ),
        (
            "**2026-01-12 — AF-AP-1 line one\nline two with AF-AP-2\nline three**\n",
            "2026-01-12 — AF-AP-1 line one line two with AF-AP-2 line three",
        ),
    ],
    ids=["I-k", "I-l"],
)
def test_wrapped_incident_heading_keeps_every_line(tmp_path, heading, locator):
    # R1 (F-01): the bold text runs from the opening ** to the first closing ** in the window.
    repo = _make_repo(tmp_path)
    _append_and_commit(repo, "docs/INCIDENT-LOG.md", "\n" + heading)
    out = tmp_path / "wrapped-heading.jsonl"
    result = _run(repo, out, "docs/INCIDENT-LOG.md")
    assert (result.returncode, result.stderr) == (0, "")
    rows = [row for row in replay(out) if row["source_ref"]["locator"] == locator]
    assert [row["state"]["row_id"] for row in rows] == ["AF-AP-1", "AF-AP-2"]
    assert {row["state"]["action_excerpt"] for row in rows} == {locator}


@pytest.mark.parametrize(
    ("bullet", "finding_id", "title"),
    [
        ("- **F-11 BLOCKER — part one\n  part two**\n", "F-11", "part one part two"),
        ("- **F-12 BLOCKER — part one\n  part two\n  part three**\n", "F-12", "part one part two part three"),
    ],
    ids=["V-k", "V-l"],
)
def test_wrapped_bullet_title_keeps_every_line(tmp_path, bullet, finding_id, title):
    # R1 (F-01): the shape-B title "may wrap" and keeps every line.
    repo = _make_repo(tmp_path)
    _append_and_commit(repo, "tasks/briefs/x/VERIFY-X-report.md", "\n" + bullet)
    out = tmp_path / "wrapped-title.jsonl"
    result = _run(repo, out, "tasks/briefs/x/VERIFY-X-report.md")
    assert (result.returncode, result.stderr) == (0, "")
    rows = [row for row in replay(out) if row["state"].get("finding_id") == finding_id]
    assert [(row["incumbent_answer"], row["state"]["title"]) for row in rows] == [("BLOCKER", title)]


@pytest.mark.parametrize(
    ("line", "observed"),
    [
        (
            "- **BOUNDARY DEVIATION: touched scripts/x.py**",
            "touched scripts/x.py** because the contract required it",
        ),
        (
            "- **BOUNDARY DEVIATION — `tests/conftest.py` was patched** (fixture).",
            "`tests/conftest.py` was patched** (fixture). because the contract required it",
        ),
        (
            "- **BOUNDARY DEVIATION** touched scripts/z.py",
            "touched scripts/z.py because the contract required it",
        ),
    ],
    ids=["L-c", "L-c2", "L-c3"],
)
def test_boundary_deviation_contract_anchor_forms(tmp_path, line, observed):
    # R2 (F-02, D-064 (1)): the contract's own anchor, `^(?:- \*\*|\d+\. )BOUNDARY DEVIATION\b\s*(?:—|:|\*\*)`.
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo, "tasks/briefs/x/X-report.md", "- **BOUNDARY DEVIATION** — touched an extra fixture", line
    )
    out = tmp_path / "anchor-forms.jsonl"
    result = _run(repo, out, "tasks/briefs/x/X-report.md")
    assert (result.returncode, result.stderr) == (0, "")
    drift = [row for row in replay(out) if row["question_id"] == "wf.drift"]
    assert [(row["source_ref"]["locator"], row["state"]["observed"]) for row in drift] == [
        ("BOUNDARY DEVIATION @ Build", observed)
    ]


def test_head_moved_after_admission_rows_come_from_the_resolved_commit(tmp_path):
    # R3 (F-03): HEAD moves to a second commit between admission and the later reads (the tree listing, the
    # registry); every content-bearing field still comes from the commit resolved once, before admission.
    repo = _make_repo(tmp_path)
    first = _git(repo, "rev-parse", "HEAD").stdout.strip()
    log = repo / "docs" / "INCIDENT-LOG.md"
    log.write_text(
        log.read_text(encoding="utf-8").replace(
            "| AF-AP-2 | malformed record silently dropped |", "| AF-AP-2 | a title from the second commit |"
        ),
        encoding="utf-8",
    )
    (repo / "src" / "existing.py").unlink()
    _commit(repo, "second commit")
    second = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "reset", "-q", "--hard", first)
    env, calls = _git_shim(tmp_path, f'"{shutil.which("git")}" -C "{repo}" update-ref HEAD {second}')
    out = tmp_path / "one-commit.jsonl"
    result = _run(repo, out, env=env)
    assert (result.returncode, result.stderr) == (0, "")
    assert calls.read_text(encoding="utf-8") == "2\n"
    assert _git(repo, "rev-parse", "HEAD").stdout.strip() == second
    rows = replay(out)
    assert {
        row["state"]["row_title"]
        for row in rows
        if row["question_id"] == "ap.violates_row" and row["state"]["row_id"] == "AF-AP-2"
    } == {"malformed record silently dropped"}
    finding = next(row for row in rows if row["state"].get("finding_id") == "F-1")
    assert finding["state"]["paths"] == ["src/existing.py"]


def test_registry_line_separator_is_text_and_refusal_lines_count_newlines(tmp_path):
    # R4 (F-04), the `_registry` site: one U+2028 inside a registry cell is text, not a line break.
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo,
        "docs/INCIDENT-LOG.md",
        "| AF-AP-1 | uncommitted source accepted |",
        "| AF-AP-1 | uncommitted source accepted |",
    )
    out = tmp_path / "registry-separator.jsonl"
    result = _run(repo, out, "docs/INCIDENT-LOG.md")
    assert (result.returncode, result.stderr) == (0, "")
    assert {row["state"]["row_id"]: row["state"]["row_title"] for row in replay(out)} == {
        "AF-AP-1": "uncommitted source accepted",
        "AF-AP-2": "malformed record silently dropped",
    }
    # `<line>` is the 1-based "\n" line of the blob: the entry sits on line 10 whatever precedes it.
    _mutate_and_commit(repo, "docs/INCIDENT-LOG.md", "AF-AP-1 happened", "AF-AP-9 happened")
    result = _run(repo, tmp_path / "registry-separator-2.jsonl", "docs/INCIDENT-LOG.md")
    assert (result.returncode, result.stderr) == (
        3,
        "harvest-source-unparseable: docs/INCIDENT-LOG.md:10 (no-registry-row)\n",
    )


def test_line_separator_before_an_incident_anchor_is_mid_line(tmp_path):
    # R4 (F-04), the `_parse_incident` site (I-j): the anchor text sits mid-line on ONE git line, so no row.
    repo = _make_repo(tmp_path)
    _append_and_commit(
        repo, "docs/INCIDENT-LOG.md", "\nSee the entry below. **2026-01-10 — AF-AP-1 minted from mid-line**\n"
    )
    out = tmp_path / "incident-separator.jsonl"
    result = _run(repo, out, "docs/INCIDENT-LOG.md")
    assert (result.returncode, result.stderr) == (0, "")
    assert [row["source_ref"]["locator"] for row in replay(out)] == [
        "2026-01-01 — AF-AP-1 happened",
        "2026-01-02 — AF-AP-2 happened",
    ]


@pytest.mark.parametrize(
    ("text", "new_titles"),
    [
        ("\nContext sentence. - **F-13 BLOCKER — minted from mid-line**\n", {}),
        (
            "| F-14 | INFO | quotes a b payload | none |\n| F-15 | INFO | the next row | none |\n",
            {"F-14": "quotes a b payload", "F-15": "the next row"},
        ),
    ],
    ids=["V-m", "V-n"],
)
def test_line_separator_in_a_verify_report_is_text(tmp_path, text, new_titles):
    # R4 (F-04), the `_finding_candidates` site: no row from mid-line text (V-m); no valid row lost (V-n).
    repo = _make_repo(tmp_path)
    _append_and_commit(repo, "tasks/briefs/x/VERIFY-X-report.md", text)
    out = tmp_path / "verify-separator.jsonl"
    result = _run(repo, out, "tasks/briefs/x/VERIFY-X-report.md")
    assert (result.returncode, result.stderr) == (0, "")
    findings = [row for row in replay(out) if row["question_id"] == "v1.finding_class"]
    assert [row["state"]["finding_id"] for row in findings] == ["F-1", "F-2", *new_titles]
    assert {
        row["state"]["finding_id"]: row["state"]["title"] for row in findings[2:]
    } == new_titles


def test_line_separator_before_a_boundary_anchor_is_mid_line(tmp_path):
    # R4 (F-04), the `_parse_lane_report` site (L-k).
    repo = _make_repo(tmp_path)
    _append_and_commit(
        repo, "tasks/briefs/x/X-report.md", "\nContext. 1. BOUNDARY DEVIATION: minted from mid-line\n"
    )
    out = tmp_path / "lane-separator.jsonl"
    result = _run(repo, out, "tasks/briefs/x/X-report.md")
    assert (result.returncode, result.stderr) == (0, "")
    drift = [row for row in replay(out) if row["question_id"] == "wf.drift"]
    assert [row["state"]["observed"] for row in drift] == [
        "touched an extra fixture because the contract required it"
    ]


def test_line_separator_inside_a_jsonl_string_is_one_record(tmp_path):
    # R4 (F-04), the `_parse_transcript` site (T-g): a raw U+2028 inside a JSON string is one valid record.
    repo = _make_repo(tmp_path)
    payload = json.dumps(
        {"hits": [{"id": "H9", "sym": "thing", "file": "src/existing.py", "line": 7, "role": "test", "note": "a b"}], "n": 1},
        ensure_ascii=False,
    )
    records = (
        {"message": {"content": [{"id": "tool-sep", "input": {"subagent_type": "hive-scout"}, "name": "Agent", "type": "tool_use"}]}, "type": "assistant", "uuid": "dispatch-sep"},
        {"message": {"content": [{"content": [{"text": payload, "type": "text"}], "tool_use_id": "tool-sep", "type": "tool_result"}]}, "type": "user", "uuid": "result-sep"},
    )
    lines = [json.dumps(record, ensure_ascii=False) for record in records]
    assert " " in lines[1]
    _append_and_commit(repo, "transcripts/x/t.jsonl", "".join(line + "\n" for line in lines))
    out = tmp_path / "jsonl-separator.jsonl"
    result = _run(repo, out, "transcripts/x/t.jsonl")
    assert (result.returncode, result.stderr) == (0, "")
    hits = [row for row in replay(out) if row["source_ref"]["locator"] == "result-sep#H9"]
    assert [(row["incumbent_answer"], row["state"]["snippet"]) for row in hits] == [("test", "a b")]


def test_held_output_lock_is_refused_by_name_without_waiting(tmp_path):
    # R5 (a), D-064 (4): a held lock is refused non-blocking with the reason `locked`; the bytes stay.
    repo = _make_repo(tmp_path)
    out = tmp_path / "held.jsonl"
    assert _run(repo, out, "tasks/briefs/x/X-report.md").returncode == 0
    before = out.read_bytes()
    holder = os.open(out, os.O_RDONLY | os.O_CLOEXEC)
    try:
        fcntl.flock(holder, fcntl.LOCK_EX)
        result = _run(repo, out, timeout=20)
    finally:
        os.close(holder)
    assert (result.returncode, result.stdout) == (6, "")
    assert result.stderr == f"harvest-output-invalid: {out} (locked)\n"
    assert out.read_bytes() == before


def test_corrupt_output_ledger_is_refused_before_any_append(tmp_path):
    # R5 (b): the up-front replay refuses a ledger with a row id twice, before any append. The copied row is
    # the one this harvest appends FIRST, so an append-time check alone would read it as a skip.
    repo = _make_repo(tmp_path)
    out = tmp_path / "corrupt.jsonl"
    assert _run(repo, out).returncode == 0
    data = out.read_bytes()
    out.write_bytes(data + data.split(b"\n")[0] + b"\n")
    before = out.read_bytes()
    result = _run(repo, out)
    assert (result.returncode, result.stdout) == (6, "")
    assert result.stderr == f"harvest-output-invalid: {out} (decision-row-duplicate)\n"
    assert out.read_bytes() == before


@pytest.mark.parametrize(
    ("foreign", "reason"),
    [("copy", "decision-row-duplicate"), ("garbage", "decision-ledger-unparseable")],
)
def test_foreign_append_during_the_run_stops_it_by_name(tmp_path, foreign, reason):
    # R5 (c): a writer that ignores the advisory lock appends to `--out` after the up-front replay. The next
    # `append` refuses; a duplicate naming ANOTHER row's id is not a skip. The run stops at once.
    repo = _make_repo(tmp_path)
    out = tmp_path / "shared.jsonl"
    assert _run(repo, out, "tasks/briefs/x/X-report.md").returncode == 0
    before = out.read_bytes()
    line = before.split(b"\n")[0] + b"\n" if foreign == "copy" else b"not json\n"
    action = f'head -n 1 "{out}" >> "{out}"' if foreign == "copy" else f'echo "not json" >> "{out}"'
    env, calls = _git_shim(tmp_path, action)
    result = _run(repo, out, "docs/INCIDENT-LOG.md", "tasks/briefs/x/X-report.md", env=env)
    assert calls.read_text(encoding="utf-8") == "2\n"
    assert (result.returncode, result.stdout) == (6, "")
    assert result.stderr == f"harvest-output-invalid: {out} ({reason})\n"
    assert out.read_bytes() == before + line


@pytest.mark.parametrize("shape", ["missing-parent", "symlink", "fifo", "directory"])
def test_output_path_failures_are_one_named_refusal(tmp_path, shape):
    # R5 (a) (F-12): each failure to open, prove regular or lock `--out` is ONE line and exit 6.
    repo = _make_repo(tmp_path)
    target = tmp_path / "target.jsonl"
    target.write_bytes(b"")
    out = tmp_path / f"{shape}.jsonl"
    if shape == "missing-parent":
        out, reason = tmp_path / "absent" / "out.jsonl", "ENOENT"
    elif shape == "symlink":
        out.symlink_to(target)
        reason = "ELOOP"
    elif shape == "fifo":
        os.mkfifo(out)
        reason = "decision-ledger-not-regular"
    else:
        out.mkdir()
        reason = "EISDIR"
    result = _run(repo, out, timeout=20)
    assert (result.returncode, result.stdout) == (6, "")
    assert result.stderr == f"harvest-output-invalid: {out} ({reason})\n"
    assert target.read_bytes() == b""
    assert not (tmp_path / "absent").exists()


def test_class_cell_loses_every_asterisk(tmp_path):
    # R6 (F-19, D-064 (2)): V-r, a bold class token with a qualifier.
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo, "tasks/briefs/x/VERIFY-X-report.md", "| F-2 | INFO, SOLID |", "| F-2 | **CONTRACT-DEFECT** (x) |"
    )
    out = tmp_path / "bold-class.jsonl"
    result = _run(repo, out, "tasks/briefs/x/VERIFY-X-report.md")
    assert (result.returncode, result.stderr) == (0, "")
    row = next(row for row in replay(out) if row["state"].get("finding_id") == "F-2")
    assert (row["incumbent_answer"], row["state"]["disposition"]) == ("CONTRACT-DEFECT", "BLOCKING")


def test_admission_refuses_a_fifo_in_the_check_window_without_blocking(tmp_path):
    # S1 (F-06): the forced window. A FIFO replaces a tracked source, and a path pre-check (if the admission read
    # still has one) is made to pass for it. The read must refuse the FIFO by its fd type, never block on it.
    repo = _make_repo(tmp_path)
    source = "tasks/briefs/x/X-report.md"
    fifo = repo.resolve() / source
    fifo.unlink()
    os.mkfifo(fifo)
    probe = tmp_path / "fifo_probe.py"
    probe.write_text(
        """
import os
import pathlib
import runpy
import sys

fifo = pathlib.Path(os.environ["FIFO"])
real_is_file = pathlib.Path.is_file
pathlib.Path.is_file = lambda self: self == fifo or real_is_file(self)
module = runpy.run_path(os.environ["SCRIPT"], run_name="decide_harvest_fifo_probe")
sys.exit(module["main"](["--root", os.environ["ROOT"], "--out", os.environ["OUT"], os.environ["REL"]]))
""".lstrip(),
        encoding="utf-8",
    )
    out = tmp_path / "fifo.jsonl"
    result = subprocess.run(
        [sys.executable, str(probe)],
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
        env={**os.environ, "FIFO": str(fifo), "SCRIPT": str(SCRIPT), "ROOT": str(repo), "OUT": str(out), "REL": source},
    )
    assert (result.returncode, result.stderr) == (4, f"harvest-source-uncommitted: {source}\n")
    assert stat.S_ISFIFO(os.lstat(fifo).st_mode)
    assert not out.exists()


def test_class_table_without_a_title_column_refuses_each_row(tmp_path):
    # S3 (F-08): `no-title-column` (mutant N3a).
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo, "tasks/briefs/x/VERIFY-X-report.md", "| id | class | what | evidence |", "| id | class | where | evidence |"
    )
    out = tmp_path / "no-title.jsonl"
    result = _run(repo, out, "tasks/briefs/x/VERIFY-X-report.md")
    assert (result.returncode, result.stderr) == (
        3,
        "harvest-source-unparseable: tasks/briefs/x/VERIFY-X-report.md:8 (no-title-column)\n",
    )
    assert [row["state"]["finding_id"] for row in replay(out) if row["question_id"] == "v1.finding_class"] == ["F-1"]


def test_class_table_short_row_is_refused(tmp_path):
    # S3 (F-08): `bad-table-row` (mutant N3b).
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo,
        "tasks/briefs/x/VERIFY-X-report.md",
        "| F-2 | INFO, SOLID | AF-AP-2 follow-up | `src/existing.py:8` |",
        "| F-2 | INFO, SOLID | AF-AP-2 follow-up |",
    )
    out = tmp_path / "short-row.jsonl"
    result = _run(repo, out, "tasks/briefs/x/VERIFY-X-report.md")
    assert (result.returncode, result.stderr) == (
        3,
        "harvest-source-unparseable: tasks/briefs/x/VERIFY-X-report.md:8 (bad-table-row)\n",
    )
    assert [row["state"]["finding_id"] for row in replay(out) if row["question_id"] == "v1.finding_class"] == ["F-1"]


def test_registry_requires_the_exact_header(tmp_path):
    # S3 (F-08): a table whose header differs from the declared one is not the registry (mutant N3c).
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo,
        "docs/INCIDENT-LOG.md",
        "| id | mechanism | greppable signature | proven instance | status |",
        "| id | mechanism | signature | instance | state |",
    )
    out = tmp_path / "other-header.jsonl"
    result = _run(repo, out, "docs/INCIDENT-LOG.md")
    assert (result.returncode, result.stderr) == (
        3,
        "harvest-source-unparseable: docs/INCIDENT-LOG.md:10 (no-registry-row)\n"
        "harvest-source-unparseable: docs/INCIDENT-LOG.md:14 (no-registry-row)\n",
    )
    assert replay(out) == []


def test_boundary_deviation_numbered_form_is_an_anchor(tmp_path):
    # S4 (F-09, mutant X2): the numbered form, case-insensitive on the two words.
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo,
        "tasks/briefs/x/X-report.md",
        "- **BOUNDARY DEVIATION** — touched an extra fixture",
        "3. Boundary deviation: touched an extra fixture",
    )
    out = tmp_path / "numbered.jsonl"
    result = _run(repo, out, "tasks/briefs/x/X-report.md")
    assert (result.returncode, result.stderr) == (0, "")
    drift = [row for row in replay(out) if row["question_id"] == "wf.drift"]
    assert [row["state"]["observed"] for row in drift] == [
        "touched an extra fixture because the contract required it"
    ]


def test_class_cell_qualifier_form_is_a_valid_class(tmp_path):
    # S4 (F-09, mutant X3): `<CLASS> (<qualifier>)`.
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo, "tasks/briefs/x/VERIFY-X-report.md", "| F-2 | INFO, SOLID |", "| F-2 | FOLLOW-UP (adjacent) |"
    )
    out = tmp_path / "qualifier.jsonl"
    result = _run(repo, out, "tasks/briefs/x/VERIFY-X-report.md")
    assert (result.returncode, result.stderr) == (0, "")
    row = next(row for row in replay(out) if row["state"].get("finding_id") == "F-2")
    assert (row["incumbent_answer"], row["state"]["disposition"]) == ("FOLLOW-UP", "NON-BLOCKING")


def test_rating_cell_leading_emoji_is_stripped(tmp_path):
    # S4 (F-09, mutant X5).
    repo = _make_repo(tmp_path)
    _mutate_and_commit(
        repo, "tasks/briefs/x/X-report.md", "| HIGH | LOW | HIGH | EXCELLENT |", "| \U0001F534 HIGH | LOW | HIGH | EXCELLENT |"
    )
    out = tmp_path / "emoji.jsonl"
    result = _run(repo, out, "tasks/briefs/x/X-report.md")
    assert (result.returncode, result.stderr) == (0, "")
    row = next(row for row in replay(out) if row["question_id"] == "d1.bug_echo_scores")
    assert row["incumbent_answer"].startswith("urgency=high;")


def test_paths_ignore_absolute_tokens_same_commit_at_two_roots(tmp_path):
    # S5 (F-15, mutant X4): `paths` holds only repo-relative blobs of the resolved commit, so the checkout's
    # location never changes a row.
    repo = _make_repo(tmp_path)
    _append_and_commit(
        repo,
        "tasks/briefs/x/VERIFY-X-report.md",
        f"\n- **F-30 INFO — cites an absolute path**\n  See `{repo.resolve()}/src/existing.py:1`.\n",
    )
    clone = tmp_path / "clone"
    _git(tmp_path, "clone", "-q", str(repo), str(clone))
    assert _git(clone, "rev-parse", "HEAD").stdout == _git(repo, "rev-parse", "HEAD").stdout
    at_repo, at_clone = tmp_path / "at-repo.jsonl", tmp_path / "at-clone.jsonl"
    assert _run(repo, at_repo, "tasks/briefs/x/VERIFY-X-report.md").returncode == 0
    assert _run(clone, at_clone, "tasks/briefs/x/VERIFY-X-report.md").returncode == 0
    assert at_repo.read_bytes() == at_clone.read_bytes()
    finding = next(row for row in replay(at_repo) if row["state"].get("finding_id") == "F-30")
    assert finding["state"]["paths"] == []


def _deep_transcript_lines(kind: str) -> str:
    if kind == "line":  # T-l: a JSONL line nested 100000 deep
        return "[" * 100000 + "]" * 100000 + "\n"
    if kind == "huge-int":  # a JSONL line whose parse raises ValueError, not JSONDecodeError
        return '{"n":' + "9" * 5000 + "}\n"
    deep = "[" * 100000 + "]" * 100000  # T-m: a valid record whose payload is nested 100000 deep
    records = (
        {"message": {"content": [{"id": "tool-deep", "input": {"subagent_type": "hive-scout"}, "name": "Agent", "type": "tool_use"}]}, "type": "assistant", "uuid": "dispatch-deep"},
        {"message": {"content": [{"content": [{"text": deep, "type": "text"}], "tool_use_id": "tool-deep", "type": "tool_result"}]}, "type": "user", "uuid": "result-deep"},
    )
    return "".join(json.dumps(record) + "\n" for record in records)


@pytest.mark.parametrize(
    ("kind", "refusal"),
    [("line", "5 (bad-json)"), ("huge-int", "5 (bad-json)"), ("payload", "6 (bad-payload)")],
    ids=["T-l", "huge-int", "T-m"],
)
def test_json_parse_errors_beyond_decode_errors_are_refused_by_name(tmp_path, kind, refusal):
    # S6 (F-11): RecursionError and ValueError are refused by name, never a traceback; the other rows survive.
    repo = _make_repo(tmp_path)
    _append_and_commit(repo, "transcripts/x/t.jsonl", _deep_transcript_lines(kind))
    out = tmp_path / "deep.jsonl"
    result = _run(repo, out, "transcripts/x/t.jsonl")
    assert (result.returncode, result.stderr) == (
        3,
        f"harvest-source-unparseable: transcripts/x/t.jsonl:{refusal}\n",
    )
    assert len(replay(out)) == 3
