"""The repo hooks must work from a LINKED WORKTREE (PC lanes run there), where `.git` is a file.

Born 2026-09-03: a Hermes lane looped 20 model calls because turn-retro-gate.sh wrote its
once-per-HEAD sentinel to "$REPO_ROOT/.git/turn-retro-acked" — unwritable in a linked worktree —
so the gate fired on every turn. Positive control: from a linked worktree the first run of the
gate BLOCKS (exit 2, checklist printed) and writes the sentinel into that worktree's own git dir;
the second run is silent (exit 0). Negative control: the sentinel is NOT written under the main
repo's .git dir. post-commit's wiki-stale marker goes to the COMMON git dir so main and worktree
agree on it. All in a throwaway repo — the real hooks, copied in."""
import os
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _sh(cmd, cwd, env):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env, timeout=60)


def _repo(tmp_path):
    repo = tmp_path / "main"
    (repo / ".claude" / "hooks").mkdir(parents=True)
    (repo / "scripts" / "hooks").mkdir(parents=True)
    shutil.copy(ROOT / ".claude" / "hooks" / "turn-retro-gate.sh", repo / ".claude" / "hooks" / "turn-retro-gate.sh")
    for h in ("post-commit", "pre-push"):
        shutil.copy(ROOT / "scripts" / "hooks" / h, repo / "scripts" / "hooks" / h)
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t", HOME=str(tmp_path), PATH=os.environ["PATH"])
    assert _sh(["git", "init", "-q", "-b", "main"], repo, env).returncode == 0
    (repo / "README.md").write_text("x\n")
    assert _sh(["git", "add", "."], repo, env).returncode == 0
    assert _sh(["git", "commit", "-q", "-m", "init"], repo, env).returncode == 0
    wt = tmp_path / "lane-tree"
    assert _sh(["git", "worktree", "add", "--detach", "-q", str(wt), "HEAD"], repo, env).returncode == 0
    assert (wt / ".git").is_file(), "a linked worktree's .git must be a file for this test to mean anything"
    return repo, wt, env


def test_retro_gate_sentinel_lands_in_the_worktree_git_dir(tmp_path):
    repo, wt, env = _repo(tmp_path)
    gate = wt / ".claude" / "hooks" / "turn-retro-gate.sh"
    first = _sh(["bash", str(gate)], wt, env)
    assert first.returncode == 2 and "RETRO" in first.stdout + first.stderr, (first.returncode, first.stdout, first.stderr)
    git_dir = _sh(["git", "rev-parse", "--absolute-git-dir"], wt, env).stdout.strip()
    assert git_dir.startswith(str(repo / ".git" / "worktrees")), git_dir
    assert (pathlib.Path(git_dir) / "turn-retro-acked").is_file(), "sentinel must be in the worktree's own git dir"
    assert not (repo / ".git" / "turn-retro-acked").exists(), "sentinel must NOT land in the main repo's .git"
    second = _sh(["bash", str(gate)], wt, env)
    assert second.returncode == 0 and second.stdout == "", (second.returncode, second.stdout)


def test_post_commit_marker_uses_the_common_git_dir(tmp_path):
    repo, wt, env = _repo(tmp_path)
    assert _sh(["git", "config", "core.hooksPath", "scripts/hooks"], repo, env).returncode == 0
    (wt / "code.txt").write_text("y\n")
    assert _sh(["git", "add", "code.txt"], wt, env).returncode == 0
    r = _sh(["git", "commit", "-q", "-m", "lane commit"], wt, env)
    assert r.returncode == 0, r.stderr
    assert (repo / ".git" / "wiki-stale").is_file(), "wiki-stale must be written to the COMMON git dir from a worktree"
