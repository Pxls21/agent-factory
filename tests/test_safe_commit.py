"""scripts/safe_commit.sh — {STAMP} and {DATESTAMP} in the -m message are filled from the clock (task #268).

Deterministic and LLM-free. Every case commits in a throwaway repo through the real scripts/safe_commit.sh, which runs
the real scripts/stamp.sh beside it. The commit-msg gate is the REAL hook running the REAL checker: the throwaway
repo's core.hooksPath holds only `commit-msg`, a symlink to scripts/hooks/commit-msg, and the hook's
`$(git rev-parse --show-toplevel)/scripts/stamp_check.py` is a symlink to scripts/stamp_check.py. Symlinks, not
copies: the hook and the checker under test are this tree's own bytes. Every git call runs with the GIT_* variables
dropped and the global and system config off, so no case can reach this repo's index. The clock oracle is `date -u`
through the rule's own formula, read before and after each run (a ten-minute boundary between the reads is allowed).
"""
import datetime
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "scripts" / "safe_commit.sh"


def _env():
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k != "SKIP_STAMP_CHECK"}
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
               GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
    return env


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True,
                          env=_env(), timeout=60).stdout


def _oracle():
    """(bare, dated) from date -u and the rule's formula: `date -u +'%Y-%m-%d %H:%M' | sed 's/[0-9]$/xZ/'`."""
    out = subprocess.run(["bash", "-c", "date -u +'%Y-%m-%d %H:%M' | sed 's/[0-9]$/xZ/'"], capture_output=True,
                         text=True, check=True, timeout=30).stdout.strip()
    return out[11:], out


@pytest.fixture
def repo(tmp_path):
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    (hooks / "commit-msg").symlink_to(REPO / "scripts" / "hooks" / "commit-msg")
    root = tmp_path / "work"
    _git(tmp_path, "init", "-q", "-b", "main", str(root))
    (root / "scripts").mkdir()
    (root / "scripts" / "stamp_check.py").symlink_to(REPO / "scripts" / "stamp_check.py")
    (root / ".git" / "info" / "exclude").write_text("scripts/\n")
    (root / "f.txt").write_text("1\n")
    _git(root, "add", "f.txt")
    _git(root, "commit", "-q", "-m", "init")
    _git(root, "config", "core.hooksPath", str(hooks))
    return root


def _commit(repo, message, *paths, tool=TOOL):
    return subprocess.run(["bash", str(tool), "-m", message, *paths], cwd=repo, capture_output=True, text=True,
                          timeout=60, env=_env())


def _message(repo):
    return _git(repo, "log", "-1", "--format=%B").rstrip("\n")


def test_the_message_tokens_are_filled_from_the_clock_and_pass_the_real_gate(repo):
    (repo / "f.txt").write_text("2\n")
    before = _oracle()
    r = _commit(repo, "wiki {STAMP}: the tokens\n\nmeasured {DATESTAMP}; again {STAMP}", "f.txt")
    after = _oracle()
    assert r.returncode == 0, r.stdout + r.stderr          # the real commit-msg gate passed the filled message
    want = {f"wiki {bare}: the tokens\n\nmeasured {dated}; again {bare}": dated for bare, dated in (before, after)}
    got = _message(repo)
    assert got in want, got
    assert f"== stamp tokens filled from the clock: {want[got]} ==\n" in r.stdout


def test_a_typed_future_stamp_is_still_refused_by_the_real_commit_msg_gate(repo):
    future = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    future = future[:-1] + "xZ"                            # typed, a day ahead of the clock
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "f.txt").write_text("2\n")
    r = _commit(repo, f"wiki {{STAMP}}: planned {future}", "f.txt")
    assert r.returncode == 1, r.stdout + r.stderr
    assert f"stamp_check: the commit message: '{future}' is " in r.stderr           # the real checker ran ...
    assert "COMMIT BLOCKED by the future-stamp gate on the message" in r.stderr     # ... inside the real hook
    assert _git(repo, "rev-parse", "HEAD") == head
    _git(repo, "reset", "-q")                              # the paired positive: the same commit with a past stamp
    r = _commit(repo, "wiki {STAMP}: planned 2000-01-01 00:0xZ", "f.txt")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _git(repo, "rev-parse", "HEAD") != head


def test_file_content_is_never_filled(repo):
    (repo / "brief.md").write_text("typed {STAMP} and {DATESTAMP}\n")
    r = _commit(repo, "brief {STAMP}", "brief.md")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _git(repo, "show", "HEAD:brief.md") == "typed {STAMP} and {DATESTAMP}\n"
    assert (repo / "brief.md").read_text() == "typed {STAMP} and {DATESTAMP}\n"


def _tool_beside(tmp_path, stamp_body):
    """A copy of safe_commit.sh beside a stamp.sh with STAMP_BODY, in a directory of its own."""
    tools = tmp_path / "tools"
    tools.mkdir()
    shutil.copy2(TOOL, tools / "safe_commit.sh")
    (tools / "stamp.sh").write_text(stamp_body + "\n")
    return tools / "safe_commit.sh"


def test_a_message_without_a_token_is_committed_as_given_and_reads_no_clock(repo, tmp_path):
    tool = _tool_beside(tmp_path, "echo 'not a stamp'; exit 3")       # never run: there is no token
    (repo / "f.txt").write_text("2\n")
    r = _commit(repo, "plain subject {stamp}\n\nbody line", "f.txt", tool=tool)
    assert r.returncode == 0, r.stdout + r.stderr
    assert _message(repo) == "plain subject {stamp}\n\nbody line"
    assert "stamp tokens filled" not in r.stdout


@pytest.mark.parametrize("stamp_body", ["echo 'not a stamp'", "exit 3", "echo '2026-09-25 11:2xZ extra'", "echo ''",
                                        "echo '11:2xZ'"])
def test_a_bad_stamp_sh_refuses_before_anything_is_staged(repo, tmp_path, stamp_body):
    tool = _tool_beside(tmp_path, stamp_body)
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "f.txt").write_text("2\n")
    r = _commit(repo, "wiki {STAMP}", "f.txt", tool=tool)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "REFUSED: scripts/stamp.sh gave " in r.stderr and "nothing staged" in r.stderr, r.stderr
    assert _git(repo, "diff", "--cached", "--name-only") == ""
    assert _git(repo, "rev-parse", "HEAD") == head


def test_the_staged_index_guard_still_refuses(repo):
    (repo / "g.txt").write_text("a delegate's file\n")
    _git(repo, "add", "g.txt")
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "f.txt").write_text("2\n")
    r = _commit(repo, "wiki {STAMP}", "f.txt")
    assert r.returncode == 2, r.stdout + r.stderr
    assert "REFUSED: index already carries staged entries" in r.stderr and "g.txt" in r.stderr
    assert _git(repo, "rev-parse", "HEAD") == head
    assert _git(repo, "diff", "--cached", "--name-only") == "g.txt\n"
