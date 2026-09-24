"""The pre-commit CLASS-PIN gate (AF-AP-185): when the staged `.claude/` class file's class counts change, the two
pinned tests in tests/test_vendored_manifest.py run and a red result blocks the commit.

Born 2026-09-24: cf026a9 moved `.claude/hooks/wiki-context.py` from kit-verbatim to kit-adapted; the manifest gate
passed after '--write', the pinned counts (16 kit-adapted) went red in CI. The fixture is a throwaway repo with the REAL
pre-commit hook, stub scripts for the unrelated gates (lint delta, the never-a-gate screen; the stamp gate bypassed by
its flag) and a stand-in for the pinned test file whose result a flag file sets. Nothing here touches the real tree."""
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLS = "sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv"
PINNED = '''import pathlib
def _ok():
    return pathlib.Path(__file__).with_name("PIN_OK").exists()
def test_real_claude_split_counts_and_class_file():
    assert _ok()
def test_k1h_claude_classification_and_remainder():
    assert _ok()
def test_unrelated_slow_test():
    raise SystemExit("the gate must select only the two pinned tests")
'''


def _git(repo, *args, env):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, env=env, timeout=120)


def _repo(tmp_path):
    repo = tmp_path / "r"
    (repo / "scripts" / "hooks").mkdir(parents=True)
    shutil.copy(ROOT / "scripts" / "hooks" / "pre-commit", repo / "scripts" / "hooks" / "pre-commit")
    for stub in ("lint_delta.py", "no_laya_in_gates.py"):
        (repo / "scripts" / stub).write_text("import sys; sys.exit(0)\n")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_vendored_manifest.py").write_text(PINNED)
    (repo / "sandbox-kit").mkdir()
    (repo / CLS).write_text("path\tclass\na.md\tkit-verbatim\nb.md\tkit-verbatim\n")
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@t", HOME=str(tmp_path), SKIP_STAMP_CHECK="1")
    env.pop("AF_VENV", None)
    assert _git(repo, "init", "-q", "-b", "main", env=env).returncode == 0
    assert _git(repo, "add", ".", env=env).returncode == 0
    assert _git(repo, "commit", "-q", "--no-verify", "-m", "init", env=env).returncode == 0
    assert _git(repo, "config", "core.hooksPath", "scripts/hooks", env=env).returncode == 0
    return repo, env


def _stage_classes(repo, env, rows):
    (repo / CLS).write_text("path\tclass\n" + "".join(f"{p}\t{c}\n" for p, c in rows))
    assert _git(repo, "add", CLS, env=env).returncode == 0


def test_unchanged_class_counts_skip_the_pinned_tests(tmp_path):
    repo, env = _repo(tmp_path)
    _stage_classes(repo, env, [("a.md", "kit-verbatim"), ("c.md", "kit-verbatim")])  # a rename, same counts
    r = _git(repo, "commit", "-q", "-m", "same counts", env=env)
    assert r.returncode == 0 and "class counts changed" not in r.stderr, r.stderr


def test_a_class_move_with_stale_pins_blocks_the_commit(tmp_path):
    repo, env = _repo(tmp_path)
    _stage_classes(repo, env, [("a.md", "kit-verbatim"), ("b.md", "kit-adapted")])
    r = _git(repo, "commit", "-q", "-m", "a class move", env=env)
    assert r.returncode != 0 and "COMMIT BLOCKED" in r.stderr and "AF-AP-185" in r.stderr, r.stderr
    assert _git(repo, "rev-list", "--count", "HEAD", env=env).stdout.strip() == "1"


def test_a_class_move_with_updated_pins_commits(tmp_path):
    repo, env = _repo(tmp_path)
    (repo / "tests" / "PIN_OK").write_text("")
    _stage_classes(repo, env, [("a.md", "kit-verbatim"), ("b.md", "kit-adapted")])
    r = _git(repo, "commit", "-q", "-m", "a class move, pins updated", env=env)
    assert r.returncode == 0 and "class counts changed" in r.stderr, r.stderr
