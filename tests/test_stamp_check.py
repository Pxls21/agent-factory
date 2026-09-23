"""Tests for scripts/stamp_check.py, the future-stamp pre-commit gate (AF-AP-37's timestamp half).

Deterministic and LLM-free: every case runs the real script in a throwaway git repo with a
fixed --now. The motivating instance (2026-09-23): the ledger line "E2 LANDED 2026-09-23 01:5xZ"
was committed at 01:46:42Z; its stamp named an instant 3.3 minutes in the future.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = str(REPO_ROOT / "scripts" / "stamp_check.py")
LEDGER = "todo/BUILD-TASKLIST.md"
# Written out, never imported from the script: a test that reads the tuple under test mirrors it.
EXPECTED_PLANE = [
    "todo/BUILD-TASKLIST.md",
    "docs/INCIDENT-LOG.md",
    "wiki/topics/live-state.md",
    "docs/08_DECISION_LOG.md",
]


def _env():
    env = os.environ.copy()
    for k, v in (("GIT_AUTHOR_NAME", "t"), ("GIT_AUTHOR_EMAIL", "t@t"),
                 ("GIT_COMMITTER_NAME", "t"), ("GIT_COMMITTER_EMAIL", "t@t")):
        env[k] = v
    return env


def _git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, capture_output=True, check=True, env=_env())


def _repo(tmp_path, files):
    """A throwaway repo whose HEAD holds FILES ({path: text})."""
    for path, text in files.items():
        p = tmp_path / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "--no-gpg-sign", "-m", "init")
    return tmp_path


def _stage(repo, path, text):
    p = repo / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    _git(repo, "add", path)


def _run(repo, now, *extra):
    return subprocess.run([sys.executable, SCRIPT, "--staged", "--now", now, *extra],
                          cwd=repo, capture_output=True, text=True, env=_env())


def test_the_motivating_instance_blocks_with_the_exact_line(tmp_path):
    repo = _repo(tmp_path, {LEDGER: "# ledger\n"})
    _stage(repo, LEDGER, "# ledger\n**E2 LANDED 2026-09-23 01:5xZ (task #131)\n")
    r = _run(repo, "2026-09-23T01:46:42Z")
    assert r.returncode == 1, r.stderr
    assert r.stderr == ("stamp_check: todo/BUILD-TASKLIST.md: '2026-09-23 01:5xZ' is 3.3 min ahead of "
                        "the clock 2026-09-23T01:46:42Z — paste stamps from date -u or the commit clock\n")


def test_the_pasted_stamp_passes(tmp_path):
    repo = _repo(tmp_path, {LEDGER: "# ledger\n"})
    _stage(repo, LEDGER, "# ledger\n**E2 LANDED 2026-09-23 01:4xZ (task #131)\n")
    r = _run(repo, "2026-09-23T01:46:42Z")
    assert r.returncode == 0, r.stderr
    assert r.stderr == ("stamp_check: 1 new stamp(s) in 1 ledger-plane file(s), none ahead of the clock "
                        "2026-09-23T01:46:42Z\n")


def test_the_slack_boundary_is_inclusive(tmp_path):
    """The stamp's instant equal to now + slack passes; one second less of clock blocks."""
    repo = _repo(tmp_path, {LEDGER: "# ledger\n"})
    _stage(repo, LEDGER, "# ledger\nX 2026-09-23 01:50Z\n")
    assert _run(repo, "2026-09-23T01:48:00Z").returncode == 0
    r = _run(repo, "2026-09-23T01:47:59Z")
    assert r.returncode == 1 and "'2026-09-23 01:50Z' is 2.0 min ahead" in r.stderr, r.stderr


def test_the_bucket_compares_its_earliest_instant(tmp_path):
    """01:5xZ names 01:50:00 at the earliest; at 01:52:00 it is not in the future."""
    repo = _repo(tmp_path, {LEDGER: "# ledger\n"})
    _stage(repo, LEDGER, "# ledger\nX 2026-09-23 01:5xZ\n")
    assert _run(repo, "2026-09-23T01:52:00Z", "--slack-seconds", "0").returncode == 0
    r = _run(repo, "2026-09-23T01:49:59Z", "--slack-seconds", "0")
    assert r.returncode == 1 and "is 0.0 min ahead" in r.stderr, r.stderr


def test_the_minute_and_iso_forms_are_checked(tmp_path):
    repo = _repo(tmp_path, {LEDGER: "# ledger\n"})
    _stage(repo, LEDGER, "# ledger\nA 2026-09-23 02:05Z\nB 2026-09-23T02:06:30Z\nC 2026-09-23 01:59Z\n")
    r = _run(repo, "2026-09-23T02:00:00Z")
    assert r.returncode == 1
    lines = r.stderr.splitlines()
    assert len(lines) == 2, r.stderr
    assert "'2026-09-23 02:05Z' is 5.0 min ahead" in lines[0]
    assert "'2026-09-23T02:06:30Z' is 6.5 min ahead" in lines[1]


@pytest.mark.parametrize("stamp", ["2026-09-23 25:0xZ", "2026-02-30 01:0xZ", "2026-09-23T01:5x:10Z"])
def test_a_stamp_naming_no_valid_instant_blocks(tmp_path, stamp):
    repo = _repo(tmp_path, {LEDGER: "# ledger\n"})
    _stage(repo, LEDGER, f"# ledger\nX {stamp}\n")
    r = _run(repo, "2026-09-23T03:00:00Z")
    assert r.returncode == 1
    assert r.stderr == f"stamp_check: todo/BUILD-TASKLIST.md: '{stamp}' names no valid instant\n"


def test_a_stamp_already_in_head_is_not_new(tmp_path):
    """A re-edited line keeps its old stamps; a HEAD stamp is never re-judged."""
    repo = _repo(tmp_path, {LEDGER: "# ledger\nreview due 2026-12-31 23:5xZ\n"})
    _stage(repo, LEDGER, "# ledger\nreview due 2026-12-31 23:5xZ (moved)\n")
    r = _run(repo, "2026-09-23T02:00:00Z")
    assert r.returncode == 0, r.stderr
    assert "0 new stamp(s)" in r.stderr
    # the same future stamp NOT in HEAD blocks: the exclusion is what passed above
    _stage(repo, LEDGER, "# ledger\nreview due 2026-12-31 23:4xZ (moved)\n")
    assert _run(repo, "2026-09-23T02:00:00Z").returncode == 1


def test_the_index_is_read_never_the_worktree(tmp_path):
    repo = _repo(tmp_path, {LEDGER: "# ledger\n", "other.md": "x\n"})
    _stage(repo, "other.md", "y\n")
    (repo / LEDGER).write_text("# ledger\nX 2026-09-23 09:0xZ\n")  # future, NOT staged
    assert _run(repo, "2026-09-23T02:00:00Z").returncode == 0
    _stage(repo, LEDGER, "# ledger\nX 2026-09-23 09:0xZ\n")
    (repo / LEDGER).write_text("# ledger\n")  # worktree clean again, the index keeps the stamp
    assert _run(repo, "2026-09-23T02:00:00Z").returncode == 1


@pytest.mark.parametrize("path", EXPECTED_PLANE)
def test_every_ledger_plane_file_is_checked(tmp_path, path):
    repo = _repo(tmp_path, {path: "# f\n"})
    _stage(repo, path, "# f\nX 2026-09-23 09:0xZ\n")
    r = _run(repo, "2026-09-23T02:00:00Z")
    assert r.returncode == 1 and f"stamp_check: {path}: '2026-09-23 09:0xZ'" in r.stderr, r.stderr


def test_files_outside_the_ledger_plane_are_not_checked(tmp_path):
    repo = _repo(tmp_path, {"tasks/briefs/x.md": "# b\n"})
    _stage(repo, "tasks/briefs/x.md", "# b\nX 2026-09-23 09:0xZ\n")
    r = _run(repo, "2026-09-23T02:00:00Z")
    assert r.returncode == 0 and r.stderr == "", r.stderr


def test_a_new_ledger_plane_file_has_every_stamp_checked(tmp_path):
    repo = _repo(tmp_path, {"README.md": "r\n"})
    _stage(repo, "wiki/topics/live-state.md", "X 2026-09-23 09:0xZ\n")
    assert _run(repo, "2026-09-23T02:00:00Z").returncode == 1


def test_a_bare_time_is_not_checked(tmp_path):
    """The declared limit: a bare time carries no date, so it cannot be placed on the clock."""
    repo = _repo(tmp_path, {LEDGER: "# ledger\n"})
    _stage(repo, LEDGER, "# ledger\nVERIFY-E2 DISPATCHED 02:0xZ in the sandbox\n")
    r = _run(repo, "2026-09-23T01:51:00Z")
    assert r.returncode == 0 and "0 new stamp(s)" in r.stderr, r.stderr


def test_a_malformed_now_is_a_usage_error(tmp_path):
    repo = _repo(tmp_path, {LEDGER: "# ledger\n"})
    r = _run(repo, "2026-09-23 01:51")
    assert r.returncode == 2 and "is not YYYY-MM-DDTHH:MM:SSZ" in r.stderr, r.stderr


def test_the_real_ledger_plane_carries_no_future_stamp(tmp_path):
    """Every stamp in the committed ledger-plane files, staged as new, passes at the real clock."""
    repo = _repo(tmp_path, {p: "" for p in EXPECTED_PLANE})
    for p in EXPECTED_PLANE:
        _stage(repo, p, (REPO_ROOT / p).read_text(encoding="utf-8"))
    r = subprocess.run([sys.executable, SCRIPT, "--staged"], cwd=repo, capture_output=True,
                       text=True, env=_env())
    assert r.returncode == 0, r.stderr
    assert "in 4 ledger-plane file(s), none ahead of the clock" in r.stderr


def test_the_pre_commit_hook_runs_the_gate():
    hook = (REPO_ROOT / "scripts" / "hooks" / "pre-commit").read_text()
    assert '"$PY" "$REPO_ROOT/scripts/stamp_check.py" --staged' in hook
    assert "SKIP_STAMP_CHECK" in hook
    # the gate sits before the hook's final success exit
    assert hook.index("scripts/stamp_check.py") < hook.rindex("exit 0")
