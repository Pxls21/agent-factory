"""Every committed shell script parses (`bash -n`), and the pre-commit SHELL SYNTAX GATE
actually fires on a broken one.

Born 2026-09-03: scripts/hooks/post-commit carried a syntax-error tail after its `exit 0`
for a whole batch — bash reads scripts incrementally, so runtime never reached it and review
never saw it. Positive control: the real hook lets a valid script through (a commit lands).
Negative control: the same hook blocks a staged broken script for the EXACT stated reason
(the "bash -n failed" line), in a throwaway repo — the guard under test is the only thing
that can fail there (lint_delta is copied in so it runs green on a no-.py stage).
"""
import os
import pathlib
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _sh(cmd, cwd, env=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env, timeout=60)


def _committed_shell_scripts():
    out = _sh(["git", "ls-files"], ROOT).stdout.split("\n")
    for rel in out:
        if not rel or not (ROOT / rel).is_file():
            continue
        if rel.endswith(".sh") or rel.startswith("scripts/hooks/"):
            yield rel
            continue
        with open(ROOT / rel, "rb") as fh:
            first = fh.readline()
        if first.startswith(b"#!") and b"sh" in first and b"python" not in first:
            yield rel


def test_every_committed_shell_script_parses():
    scripts = list(_committed_shell_scripts())
    assert "scripts/hooks/post-commit" in scripts, "corpus must include the hook that bit"
    bad = [s for s in scripts if _sh(["bash", "-n", str(ROOT / s)], ROOT).returncode != 0]
    assert not bad, f"bash -n failed on: {bad}"


def test_bash_n_instrument_fires_on_a_broken_script(tmp_path):
    broken = tmp_path / "broken.sh"
    broken.write_text("#!/bin/bash\nexit 0\n  ) 9>/tmp/x.lock &\nfi\n")
    assert _sh(["bash", "-n", str(broken)], tmp_path).returncode != 0


def _throwaway_repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "scripts" / "hooks").mkdir(parents=True)
    shutil.copy(ROOT / "scripts" / "hooks" / "pre-commit", repo / "scripts" / "hooks" / "pre-commit")
    shutil.copy(ROOT / "scripts" / "lint_delta.py", repo / "scripts" / "lint_delta.py")
    os.chmod(repo / "scripts" / "hooks" / "pre-commit", 0o755)
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t", HOME=str(tmp_path))
    assert _sh(["git", "init", "-q"], repo, env).returncode == 0
    assert _sh(["git", "config", "core.hooksPath", "scripts/hooks"], repo, env).returncode == 0
    return repo, env


def test_pre_commit_gate_positive_and_negative_controls(tmp_path):
    repo, env = _throwaway_repo(tmp_path)
    (repo / "good.sh").write_text("#!/bin/bash\necho ok\nexit 0\n")
    assert _sh(["git", "add", "good.sh", "scripts"], repo, env).returncode == 0
    r = _sh(["git", "commit", "-q", "-m", "good"], repo, env)
    assert r.returncode == 0, r.stderr
    assert _sh(["git", "rev-list", "--count", "HEAD"], repo, env).stdout.strip() == "1"

    (repo / "bad.sh").write_text("#!/bin/bash\nexit 0\n  ) 9>/tmp/x.lock &\nfi\n")
    assert _sh(["git", "add", "bad.sh"], repo, env).returncode == 0
    r = _sh(["git", "commit", "-q", "-m", "bad"], repo, env)
    assert r.returncode != 0
    assert "bash -n failed on bad.sh" in r.stderr, r.stderr
    assert _sh(["git", "rev-list", "--count", "HEAD"], repo, env).stdout.strip() == "1"
