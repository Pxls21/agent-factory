"""scripts/skill_bake_finish.sh: the refusals that happen before it touches anything (usage, a bad or unknown skill name).

The ride-along refusal (another skill's edit present) and the ready path (a clean-worktree manifest) were proven live on
2026-09-24 against the shared tree (the commit that adds the script pastes both); they need a mutable tree, so they are not
repeated here. Each case below asserts the exit code and the message, and that no tracked file changed.
"""
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "skill_bake_finish.sh"


def _status():
    return subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"],
                          capture_output=True, text=True, check=True).stdout


def _run(*args):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, cwd=ROOT, timeout=60)


def test_no_skill_is_a_usage_error():
    before = _status()
    r = _run()
    assert r.returncode == 64 and "usage: skill_bake_finish.sh" in r.stderr
    assert _status() == before


def test_a_path_like_name_is_refused():
    before = _status()
    for bad in ("../x", "a/b", ".hidden"):
        r = _run(bad)
        assert r.returncode == 64 and "bad skill name: %s" % bad in r.stderr, (bad, r.stderr)
    assert _status() == before


def test_an_unknown_skill_is_refused():
    before = _status()
    r = _run("no-such-skill-qz8")
    assert r.returncode == 64 and "no .claude/skills/no-such-skill-qz8/SKILL.md" in r.stderr
    assert _status() == before
