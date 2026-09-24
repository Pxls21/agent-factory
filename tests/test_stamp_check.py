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


def test_a_bucket_stamp_gets_no_slack(tmp_path):
    """2026-09-24: a `20:1xZ` block written at 20:08:53Z was 67 s ahead, inside the 120 s slack, and passed. A bucket
    already spans ten minutes, so its earliest instant may not pass the clock at all; a minute stamp keeps the slack."""
    repo = _repo(tmp_path, {LEDGER: "# ledger\n"})
    _stage(repo, LEDGER, "# ledger\nX 2026-09-24 20:1xZ\n")
    r = _run(repo, "2026-09-24T20:08:53Z")
    assert r.returncode == 1 and "'2026-09-24 20:1xZ' is 1.1 min ahead" in r.stderr, r.stderr
    assert _run(repo, "2026-09-24T20:10:00Z").returncode == 0
    _stage(repo, LEDGER, "# ledger\nX 2026-09-24 20:10Z\n")
    assert _run(repo, "2026-09-24T20:08:53Z").returncode == 0


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


def test_a_brief_premise_heading_ahead_of_the_clock_blocks(tmp_path):
    """2026-09-24: VERIFY-JT3-R1's premise heading read 17:3xZ at 17:29Z (and a plan's STATUS read 16:4xZ at 16:38Z)."""
    repo = _repo(tmp_path, {"README.md": "r\n"})
    _stage(repo, "tasks/briefs/x.md", "# b\n## PREMISE — MEASURED at authoring (2026-09-24 17:3xZ, the tree)\n")
    r = _run(repo, "2026-09-24T17:25:00Z")          # beyond the 120 s slack (the real slip was 1 min, inside it)
    assert r.returncode == 1 and "stamp_check: tasks/briefs/x.md: '2026-09-24 17:3xZ' is 5.0 min ahead" in r.stderr, r.stderr
    _stage(repo, "tasks/plan.md", "STATUS 2026-09-24 16:4xZ: a PLAN\n")
    r = _run(repo, "2026-09-24T16:35:00Z")
    assert r.returncode == 1 and "stamp_check: tasks/plan.md: '2026-09-24 16:4xZ' is 5.0 min ahead" in r.stderr, r.stderr


def test_a_brief_measurement_stamp_in_the_past_passes_and_other_brief_stamps_stay_unchecked(tmp_path):
    repo = _repo(tmp_path, {"README.md": "r\n"})
    _stage(repo, "tasks/briefs/x.md", "## PREMISE — MEASURED at authoring (2026-09-24 17:2xZ, the tree)\n"
                                       "The window opens 2026-09-25 09:0xZ (a plan, not a measurement).\n")
    r = _run(repo, "2026-09-24T17:29:00Z")
    assert r.returncode == 0, r.stderr
    assert r.stderr == ("stamp_check: 1 new measurement stamp(s) in 1 tasks/ file(s), none ahead of the clock "
                        "2026-09-24T17:29:00Z\n"), r.stderr


def test_a_measurement_line_outside_tasks_is_not_checked(tmp_path):
    repo = _repo(tmp_path, {"README.md": "r\n"})
    _stage(repo, "docs/x.md", "## PREMISE — MEASURED at authoring (2026-09-24 17:3xZ)\n")
    r = _run(repo, "2026-09-24T17:29:00Z")
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


# --message (the commit-msg hook, 2026-09-24): "retro 21:5xZ" was committed at 21:45:43Z; the staged files were clean.
def _msg(tmp_path, text, now):
    m = tmp_path / "COMMIT_EDITMSG"
    m.write_text(text)
    return subprocess.run([sys.executable, SCRIPT, "--message", str(m), "--now", now], capture_output=True,
                          text=True, env=_env())


def test_a_subject_bucket_ahead_of_the_clock_blocks_with_the_exact_line(tmp_path):
    r = _msg(tmp_path, "retro 21:5xZ: AF-AP-187 echo\n\nbody\n", "2026-09-24T21:45:43Z")
    assert r.returncode == 1, r.stderr
    assert ("stamp_check: the commit subject: '21:5xZ' is 4.3 min ahead of the clock 2026-09-24T21:45:43Z"
            in r.stderr), r.stderr


def test_the_current_bucket_and_a_past_minute_pass(tmp_path):
    r = _msg(tmp_path, "retro 21:4xZ, landed 21:45Z\n", "2026-09-24T21:45:43Z")
    assert r.returncode == 0, r.stderr


def test_a_minute_stamp_on_the_subject_keeps_the_slack(tmp_path):
    assert _msg(tmp_path, "x 21:47Z\n", "2026-09-24T21:45:43Z").returncode == 0
    r = _msg(tmp_path, "x 21:48Z\n", "2026-09-24T21:45:43Z")
    assert r.returncode == 1 and "'21:48Z' is 2.3 min ahead" in r.stderr, r.stderr


def test_a_bare_time_in_the_body_is_not_checked_but_a_dated_stamp_anywhere_is(tmp_path):
    assert _msg(tmp_path, "subject\n\nat 23:5xZ we\n", "2026-09-24T21:45:43Z").returncode == 0
    r = _msg(tmp_path, "subject\n\nat 2026-09-24 23:5xZ we\n", "2026-09-24T21:45:43Z")
    assert r.returncode == 1 and "the commit message: '2026-09-24 23:5xZ' is" in r.stderr, r.stderr


def test_a_dated_past_stamp_on_the_subject_is_not_read_as_a_bare_time(tmp_path):
    r = _msg(tmp_path, "the 2026-09-20 23:5xZ batch\n", "2026-09-24T21:45:43Z")
    assert r.returncode == 0, r.stderr


def test_a_subject_stamp_after_midnight_is_read_as_the_previous_day(tmp_path):
    r = _msg(tmp_path, "retro 23:5xZ\n", "2026-09-25T00:05:00Z")
    assert r.returncode == 0, r.stderr


def test_git_comment_lines_are_skipped(tmp_path):
    r = _msg(tmp_path, "# retro 23:5xZ\nsubject 21:4xZ\n# 2099-01-01 00:0xZ\n", "2026-09-24T21:45:43Z")
    assert r.returncode == 0, r.stderr


def test_an_invalid_subject_time_blocks(tmp_path):
    r = _msg(tmp_path, "at 25:1xZ\n", "2026-09-24T21:45:43Z")
    assert r.returncode == 1 and "'25:1xZ' names no valid time" in r.stderr, r.stderr


def test_the_commit_msg_hook_runs_the_gate_on_the_real_script(tmp_path):
    ok, bad = tmp_path / "ok", tmp_path / "bad"
    ok.write_text("subject\n")
    bad.write_text("subject\n\nplanned 2099-01-01 00:0xZ\n")
    hook = str(REPO_ROOT / "scripts" / "hooks" / "commit-msg")
    env = {k: v for k, v in _env().items() if k != "SKIP_STAMP_CHECK"}

    def run(path, **extra):
        return subprocess.run(["bash", hook, str(path)], cwd=REPO_ROOT, capture_output=True, text=True,
                              env={**env, **extra})
    assert run(ok).returncode == 0
    r = run(bad)
    assert r.returncode == 1 and "COMMIT BLOCKED by the future-stamp gate on the message" in r.stderr, r.stderr
    r = run(bad, SKIP_STAMP_CHECK="1")
    assert r.returncode == 0 and "bypassed" in r.stderr, r.stderr


def test_a_subject_bucket_gets_no_slack(tmp_path):
    r = _msg(tmp_path, "retro 21:5xZ\n", "2026-09-24T21:49:00Z")
    assert r.returncode == 1 and "'21:5xZ' is 1.0 min ahead" in r.stderr, r.stderr
