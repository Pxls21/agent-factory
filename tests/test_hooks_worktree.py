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


def _commit(repo, env, files, msg):
    for rel, text in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text)
    assert _sh(["git", "add", *files], repo, env).returncode == 0
    assert _sh(["git", "commit", "-q", "-m", msg], repo, env).returncode == 0


def test_a_retro_plane_commit_does_not_fire_the_gate_again(tmp_path):
    # 2026-09-24: a retro answered with an incident entry, a ledger note and a wiki delta fired the gate a second time.
    repo, _wt, env = _repo(tmp_path)
    gate = repo / ".claude" / "hooks" / "turn-retro-gate.sh"
    _commit(repo, env, {"scripts/tool.py": "x = 1\n"}, "code")
    assert _sh(["bash", str(gate)], repo, env).returncode == 2
    _commit(repo, env, {"docs/INCIDENT-LOG.md": "entry\n", "todo/BUILD-TASKLIST.md": "note\n",
                        "wiki/topics/live-state.md": "block\n"}, "retro answer")
    assert _sh(["bash", str(gate)], repo, env).returncode == 0
    _commit(repo, env, {".claude/skills/build-loop/SKILL.md": "lesson\n", ".agents/skills/build-loop/SKILL.md": "lesson\n",
                        ".agents/lane-skills/build-loop/SKILL.md": "lesson\n", "harness-ports/hand-ported.sha256": "h\n",
                        "sandbox-kit/VENDORED-MANIFEST.md": "m\n", "sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv": "t\n"},
            "skill bake")
    assert _sh(["bash", str(gate)], repo, env).returncode == 0


def test_code_beside_the_ledger_still_fires_the_gate(tmp_path):
    repo, _wt, env = _repo(tmp_path)
    gate = repo / ".claude" / "hooks" / "turn-retro-gate.sh"
    _commit(repo, env, {"scripts/tool.py": "x = 1\n"}, "code")
    assert _sh(["bash", str(gate)], repo, env).returncode == 2
    _commit(repo, env, {"todo/BUILD-TASKLIST.md": "note\n", "scripts/tool.py": "x = 2\n"}, "code and ledger")
    assert _sh(["bash", str(gate)], repo, env).returncode == 2
    _commit(repo, env, {"sandbox-kit/OTHER.md": "guide\n"}, "a kit guide is not in the retro plane")
    assert _sh(["bash", str(gate)], repo, env).returncode == 2


def test_a_skill_bake_with_its_companions_is_quiet_in_both_hooks(tmp_path):
    # 2026-09-24: a build-loop bake (the skill, its two mirrors, the hand-port hashes, the manifest and the class file)
    # marked the wiki stale in post-commit although the retro gate treated the same set as retro plane.
    repo, _wt, env = _repo(tmp_path)
    assert _sh(["git", "config", "core.hooksPath", "scripts/hooks"], repo, env).returncode == 0
    gate = repo / ".claude" / "hooks" / "turn-retro-gate.sh"
    marker = repo / ".git" / "wiki-stale"
    _commit(repo, env, {"scripts/tool.py": "x = 1\n"}, "code")
    assert marker.is_file()
    marker.unlink()
    assert _sh(["bash", str(gate)], repo, env).returncode == 2
    _commit(repo, env, {".claude/skills/build-loop/SKILL.md": "lesson\n", ".agents/skills/build-loop/SKILL.md": "lesson\n",
                        ".agents/lane-skills/build-loop/SKILL.md": "lesson\n", "harness-ports/hand-ported.sha256": "h\n",
                        "sandbox-kit/VENDORED-MANIFEST.md": "m\n", "sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv": "t\n"},
            "skill bake")
    assert not marker.exists(), "a skill bake with its companions must not mark the wiki stale"
    assert _sh(["bash", str(gate)], repo, env).returncode == 0
    _commit(repo, env, {"transcripts/pc/x.jsonl": "{}\n"}, "transcripts sync")
    assert not marker.exists() and _sh(["bash", str(gate)], repo, env).returncode == 0


def test_a_rewritten_range_does_not_fire_the_gate_again(tmp_path):
    # 2026-09-24: push_clean strips model trailers from the unpushed range, so every pushed commit gets a new SHA with the
    # same tree and subject; the gate read the rewritten commits as new work and re-fired after each push.
    repo, _wt, env = _repo(tmp_path)
    gate = repo / ".claude" / "hooks" / "turn-retro-gate.sh"
    (repo / "scripts").mkdir(exist_ok=True)
    (repo / "scripts" / "tool.py").write_text("x = 1\n")
    assert _sh(["git", "add", "scripts/tool.py"], repo, env).returncode == 0
    assert _sh(["git", "commit", "-q", "-m", "code\n\nCo-Authored-By: someone <x@y>"], repo, env).returncode == 0
    assert _sh(["bash", str(gate)], repo, env).returncode == 2
    assert _sh(["git", "commit", "--amend", "-q", "-m", "code"], repo, env).returncode == 0  # the rewrite: same tree
    assert _sh(["bash", str(gate)], repo, env).returncode == 0
    _commit(repo, env, {"scripts/tool.py": "x = 2\n"}, "more code")
    assert _sh(["bash", str(gate)], repo, env).returncode == 2
