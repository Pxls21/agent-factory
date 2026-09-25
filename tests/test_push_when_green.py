"""scripts/push_when_green.sh — wait for the CI verdict, guard the GitNexus banner, pick the mode, push (task #269).

Deterministic and LLM-free. Every case copies the real script into a throwaway repo beside a FAKE scripts/ci_gate.py
and a FAKE scripts/push_clean.sh: the script resolves both from its own directory, as push_clean.sh resolves
ci_gate.py, so the production code carries no test seam. Each fake appends one line to the log the test names
(PWG_LOG) and exits with the rc the test asks for (PWG_GATE_RC, PWG_PUSH_RC). Origin is a local bare repo that a second
clone moves ahead before each run: only a fetch brings refs/remotes/origin/feat to that commit, so the fake
push_clean's record of the ref proves the fetch ran before it. Every git call runs with the GIT_* variables dropped
and the global and system config off.
"""
import os
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "scripts" / "push_when_green.sh"
START, END = "<!-- gitnexus:start -->", "<!-- gitnexus:end -->"
DOC = f"# doc\nintro line\n\n{START}\n# GitNexus\nindexed (100 symbols)\n{END}\n\ntail line\n"
CHURN = DOC.replace("indexed (100 symbols)", "indexed (101 symbols)\na new stats line")   # inside the block only
OVERRIDES = ("CI_FIX", "CI_WAIT_SKIP", "CI_GATE_OFFLINE")

FAKE_GATE = """import os, sys
seen = ",".join(n for n in ("CI_FIX", "CI_WAIT_SKIP", "CI_GATE_OFFLINE") if n in os.environ)
with open(os.environ["PWG_LOG"], "a") as fh:
    fh.write("ci_gate " + " ".join(sys.argv[1:]) + " overrides=" + seen + "\\n")
sys.exit(int(os.environ.get("PWG_GATE_RC", "0")))
"""
FAKE_PUSH = """set -eu
seen=""
for n in CI_FIX CI_WAIT_SKIP CI_GATE_OFFLINE; do [ -z "${!n+x}" ] || seen="$seen$n,"; done
printf 'push_clean %s branch=%s origin=%s dirty=%s overrides=%s cwd=%s\\n' "$*" "$PUSH_BRANCH" \\
  "$(git rev-parse "refs/remotes/origin/$PUSH_BRANCH")" "$(git status --porcelain --untracked-files=no | tr '\\n' ' ')" \\
  "$seen" "$(pwd -P)" >> "$PWG_LOG"
exit "${PWG_PUSH_RC:-0}"
"""


def _env(**extra):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("GIT_") and k not in OVERRIDES + ("PUSH_BRANCH", "CI_GATE_RUNS_JSON")}
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
               GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1")
    env.update(extra)
    return env


def _git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, check=True, env=_env(),
                          timeout=60).stdout.strip()


@pytest.fixture
def w(tmp_path):
    origin, root, other = tmp_path / "origin.git", tmp_path / "work", tmp_path / "other"
    _git(tmp_path, "init", "-q", "--bare", str(origin))
    _git(tmp_path, "init", "-q", "-b", "feat", str(root))
    (root / "scripts").mkdir()
    shutil.copy2(TOOL, root / "scripts" / "push_when_green.sh")
    (root / "scripts" / "ci_gate.py").write_text(FAKE_GATE)
    (root / "scripts" / "push_clean.sh").write_text(FAKE_PUSH)
    for name in ("AGENTS.md", "CLAUDE.md"):
        (root / name).write_text(DOC)
    (root / "f.txt").write_text("1\n")
    (root / ".git" / "info" / "exclude").write_text(".lanes-live\n")      # as in the real tree: never tracked
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "one")
    _git(root, "remote", "add", "origin", str(origin))
    _git(root, "push", "-q", "origin", "feat")
    _git(tmp_path, "clone", "-q", "-b", "feat", str(origin), str(other))
    (other / "g.txt").write_text("ahead\n")
    _git(other, "add", "g.txt")
    _git(other, "commit", "-q", "-m", "origin moves ahead")
    _git(other, "push", "-q", "origin", "feat")
    return SimpleNamespace(root=root, log=tmp_path / "pwg.log", ahead=_git(other, "rev-parse", "HEAD"),
                           old=_git(root, "rev-parse", "refs/remotes/origin/feat"))


def _run(w, *args, cwd=None, **env):
    return subprocess.run(["bash", str(w.root / "scripts" / "push_when_green.sh"), *args], cwd=cwd or w.root,
                          capture_output=True, text=True, timeout=60, env=_env(PWG_LOG=str(w.log), **env))


def _calls(w):
    return w.log.read_text().splitlines() if w.log.exists() else []


def _push_line(w, mode, dirty="", overrides=""):
    return (f"push_clean {mode} branch=feat origin={w.ahead} dirty={dirty} overrides={overrides} "
            f"cwd={w.root.resolve()}")


GATE_LINE = "ci_gate --branch feat --wait 1700 overrides="


def _steps(result):
    return [line for line in (result.stdout + result.stderr).splitlines() if line.startswith("push_when_green:")]


def test_green_pushes_exactly_once_after_the_fetch_with_one_line_per_step(w):
    r = _run(w)
    assert r.returncode == 0, r.stdout + r.stderr
    assert _calls(w) == [GATE_LINE, _push_line(w, "--no-delegates-live")]
    assert _steps(r) == [
        "push_when_green: [1/4] ci_gate.py --wait allows the push of feat (rc 0)",
        "push_when_green: [2/4] banner guard: AGENTS.md and CLAUDE.md match HEAD",
        "push_when_green: [3/4] mode --no-delegates-live (auto: no .lanes-live)",
        "push_when_green: [4/4] fetched origin/feat; push_clean.sh --no-delegates-live exited rc 0"]


def test_the_wait_comes_from_the_flag_and_the_branch_from_push_branch(w):
    _git(w.root, "checkout", "-q", "-b", "other")
    r = _run(w, "--wait", "30", PUSH_BRANCH="feat")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _calls(w) == ["ci_gate --branch feat --wait 30 overrides=", _push_line(w, "--no-delegates-live")]


@pytest.mark.parametrize("rc", [1, 2, 75, 64, 3])
def test_a_verdict_rc_other_than_0_is_the_exit_and_nothing_is_fetched_or_pushed(w, rc):
    r = _run(w, PWG_GATE_RC=str(rc))
    assert r.returncode == rc, r.stdout + r.stderr
    assert _calls(w) == [GATE_LINE]
    assert _git(w.root, "rev-parse", "refs/remotes/origin/feat") == w.old          # no fetch ran
    assert _steps(r) == [_steps(r)[0]] and _steps(r)[0].startswith(f"push_when_green: [1/4] ci_gate.py rc {rc}: ")
    assert "nothing fetched or pushed" in r.stderr


def test_a_banner_only_difference_is_restored_before_the_push(w):
    for name in ("AGENTS.md", "CLAUDE.md"):
        (w.root / name).write_text(CHURN)
    r = _run(w)
    assert r.returncode == 0, r.stdout + r.stderr
    assert _calls(w) == [GATE_LINE, _push_line(w, "--no-delegates-live")]           # dirty= empty at the push
    assert (w.root / "AGENTS.md").read_text() == DOC and (w.root / "CLAUDE.md").read_text() == DOC
    assert ("push_when_green: [2/4] banner guard: restored AGENTS.md CLAUDE.md "
            "(a difference from HEAD inside the gitnexus block only)") in _steps(r)


OUTSIDE = {
    "before the block": CHURN.replace("intro line", "intro line, an unsaved edit"),
    "after the block": DOC.replace("tail line", "tail line, an unsaved edit"),
    "the start marker": DOC.replace(START, START + " "),
    "the end marker": DOC.replace(END, "<!-- gitnexus:END -->"),
    "the final newline": DOC[:-1],
    "a second block": DOC + f"{START}\n{END}\n",
    "the block removed": DOC.replace(f"{START}\n# GitNexus\nindexed (100 symbols)\n{END}\n", ""),
    "the markers swapped": DOC.replace(START, "@@").replace(END, START).replace("@@", END),
}


@pytest.mark.parametrize("name", ["CLAUDE.md", "AGENTS.md"])
@pytest.mark.parametrize("case", sorted(OUTSIDE))
def test_a_difference_outside_the_block_refuses_and_leaves_the_file_untouched(w, name, case):
    (w.root / name).write_text(OUTSIDE[case])
    r = _run(w)
    assert r.returncode == 65, r.stdout + r.stderr
    assert (f"push_when_green: [2/4] REFUSED: {name} differs from HEAD outside its gitnexus block; left untouched, "
            "nothing restored or pushed") in r.stderr
    assert (w.root / name).read_text() == OUTSIDE[case]
    assert _calls(w) == [GATE_LINE]
    assert _git(w.root, "rev-parse", "refs/remotes/origin/feat") == w.old


def test_a_deleted_file_refuses(w):
    (w.root / "CLAUDE.md").unlink()
    r = _run(w)
    assert r.returncode == 65, r.stdout + r.stderr
    assert "[2/4] REFUSED: CLAUDE.md differs from HEAD outside its gitnexus block" in r.stderr
    assert not (w.root / "CLAUDE.md").exists() and _calls(w) == [GATE_LINE]


def test_two_blocks_in_head_are_ambiguous_and_refuse(w):
    """With two marker pairs, "the block" names no one block: even a change inside the first pair refuses."""
    two = DOC + f"{START}\nsecond (1)\n{END}\n"
    (w.root / "CLAUDE.md").write_text(two)
    _git(w.root, "commit", "-q", "-am", "two blocks")
    edited = two.replace("indexed (100 symbols)", "indexed (101 symbols)")
    (w.root / "CLAUDE.md").write_text(edited)
    r = _run(w)
    assert r.returncode == 65, r.stdout + r.stderr
    assert "[2/4] REFUSED: CLAUDE.md differs from HEAD outside its gitnexus block" in r.stderr
    assert (w.root / "CLAUDE.md").read_text() == edited and _calls(w) == [GATE_LINE]


def test_both_files_are_judged_before_either_is_restored(w):
    (w.root / "AGENTS.md").write_text(CHURN)                                      # banner-only: restorable alone
    (w.root / "CLAUDE.md").write_text(OUTSIDE["after the block"])                 # an unsaved edit
    r = _run(w)
    assert r.returncode == 65, r.stdout + r.stderr
    assert (w.root / "AGENTS.md").read_text() == CHURN, "a refused run restored nothing"
    assert (w.root / "CLAUDE.md").read_text() == OUTSIDE["after the block"]
    assert "REFUSED: CLAUDE.md" in r.stderr and "REFUSED: AGENTS.md" not in r.stderr
    assert _calls(w) == [GATE_LINE]


@pytest.mark.parametrize("lanes, change, mode, reason", [
    ("scripts/x.py\n", "unstaged", "--lanes-live", ".lanes-live declares 1 path(s) and the tracked tree has changes"),
    ("a\n# a comment\n\nb", "staged", "--lanes-live", ".lanes-live declares 2 path(s) and the tracked tree has changes"),
    ("scripts/x.py\n", "untracked", "--no-delegates-live", "the tracked tree has no changes"),
    ("scripts/x.py\n", "banner", "--no-delegates-live", "the tracked tree has no changes"),
    (None, "unstaged", "--no-delegates-live", "no .lanes-live"),
    ("# only a comment\n\n", "unstaged", "--no-delegates-live", ".lanes-live declares no path"),
])
def test_the_auto_mode_picks_each_mode_on_its_condition(w, lanes, change, mode, reason):
    if lanes is not None:
        (w.root / ".lanes-live").write_text(lanes)
    if change == "unstaged":
        (w.root / "f.txt").write_text("2\n")
    elif change == "staged":
        (w.root / "f.txt").write_text("2\n")
        _git(w.root, "add", "f.txt")
    elif change == "untracked":
        (w.root / "new.txt").write_text("x\n")
    else:                                                  # banner churn only: the guard restores it first
        (w.root / "CLAUDE.md").write_text(CHURN)
    r = _run(w)
    assert r.returncode == 0, r.stdout + r.stderr
    assert _calls(w)[1].startswith(f"push_clean {mode} branch=feat origin={w.ahead} ")
    assert f"push_when_green: [3/4] mode {mode} (auto: {reason})" in _steps(r)


@pytest.mark.parametrize("flag, lanes, change", [
    ("--no-delegates-live", "scripts/x.py\n", True),       # auto would pick --lanes-live
    ("--lanes-live", None, False),                         # auto would pick --no-delegates-live
])
def test_a_mode_flag_wins(w, flag, lanes, change):
    if lanes is not None:
        (w.root / ".lanes-live").write_text(lanes)
    if change:
        (w.root / "f.txt").write_text("2\n")
    r = _run(w, flag)
    assert r.returncode == 0, r.stdout + r.stderr
    assert _calls(w)[1].startswith(f"push_clean {flag} branch=feat ")
    assert f"push_when_green: [3/4] mode {flag} (given)" in _steps(r)


def test_push_clean_rc_is_the_exit(w):
    r = _run(w, PWG_PUSH_RC="4")
    assert r.returncode == 4, r.stdout + r.stderr
    assert _calls(w) == [GATE_LINE, _push_line(w, "--no-delegates-live")]
    assert "push_when_green: [4/4] fetched origin/feat; push_clean.sh --no-delegates-live exited rc 4" in r.stderr


def test_a_failed_fetch_pushes_nothing(w, tmp_path):
    _git(w.root, "remote", "set-url", "origin", str(tmp_path / "no-such-origin.git"))
    r = _run(w)
    assert r.returncode == 128, r.stdout + r.stderr
    assert "push_when_green: [4/4] git fetch -q origin feat failed (rc 128); nothing pushed" in r.stderr
    assert _calls(w) == [GATE_LINE]


@pytest.mark.parametrize("args", [["--wait"], ["--wait", "x"], ["--wait", "-5"], ["--wait", "1.5"], ["--bogus"],
                                  ["--lanes-live", "--no-delegates-live"], ["--no-delegates-live"] * 2])
def test_usage_errors_exit_64_before_anything_runs(w, args):
    r = _run(w, *args)
    assert r.returncode == 64, r.stdout + r.stderr
    assert "usage: push_when_green.sh" in r.stderr
    assert _calls(w) == []


def test_a_detached_head_needs_push_branch(w):
    _git(w.root, "checkout", "-q", "--detach")
    r = _run(w)
    assert r.returncode == 64 and "HEAD is detached: set PUSH_BRANCH=<branch>" in r.stderr, r.stdout + r.stderr
    assert _calls(w) == []
    r = _run(w, PUSH_BRANCH="feat")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _calls(w) == [GATE_LINE, _push_line(w, "--no-delegates-live")]


def test_it_runs_from_a_subdirectory_at_the_top_of_the_tree(w):
    (w.root / "sub").mkdir()
    r = _run(w, cwd=w.root / "sub")
    assert r.returncode == 0, r.stdout + r.stderr
    assert _calls(w) == [GATE_LINE, _push_line(w, "--no-delegates-live")]           # cwd= the top of the tree


@pytest.mark.parametrize("given", [{}, {"CI_FIX": "1009"}, {"CI_WAIT_SKIP": "x", "CI_GATE_OFFLINE": "y"}])
def test_it_sets_no_ci_override_and_passes_a_callers_own(w, given):
    r = _run(w, **given)
    assert r.returncode == 0, r.stdout + r.stderr
    seen = "".join(f"{name}," for name in OVERRIDES if name in given)
    assert _calls(w) == [f"ci_gate --branch feat --wait 1700 overrides={seen.rstrip(',')}",
                         _push_line(w, "--no-delegates-live", overrides=seen)]


def test_the_header_documents_the_background_use():
    header = TOOL.read_text().split("\nset -euo pipefail\n")[0]
    assert "run_in_background" in header and "setsid nohup bash scripts/push_when_green.sh" in header
