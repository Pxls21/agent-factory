"""The push lock (AF-AP-216; amendment 1 of tasks #268 and #269): scripts/push_clean.sh holds the file
`git rev-parse --git-path push-in-flight` (its pid) for its whole run, scripts/safe_commit.sh waits while it is held, and
scripts/hooks/pre-commit refuses a raw commit while it is held, except push_clean's own (PUSH_IN_FLIGHT_PID).

The race it closes (2026-09-25, push_when_green.sh's first real run): a commit landed on the branch while
push_clean --lanes-live pushed from its detached worktree; the follow step then found the trees unequal and left the ref
unfollowed. The first test reproduces it in a throwaway repo with a bare origin. The scripts under test are copied into
the repo and COMMITTED, because the inner run executes the worktree's committed copies. A FAKE scripts/ci_gate.py holds
the inner push at the gate until the test releases it (GATE_RELEASE); the real scripts/stale_ids.py rides along. The
pre-commit hook is the real one (the repo's core.hooksPath holds a link to it), with the scripts its other gates call
linked in. Deterministic and LLM-free; every git call runs with the GIT_* variables dropped and the global and system
config off, so no case can reach this repo's index.
"""
import os
import shutil
import signal
import subprocess
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"
UNDER_TEST = ("push_clean.sh", "safe_commit.sh", "stamp.sh", "stale_ids.py")
HOOK_SCRIPTS = ("lint_delta.py", "stamp_check.py", "ap_screen.py", "no_laya_in_gates.py")
DROP = ("PUSH_BRANCH", "PUSH_IN_FLIGHT_PID", "SAFE_COMMIT_LOCK_WAIT", "TRANSCRIPT_SYNC", "SKIP_STAMP_CHECK", "CI_FIX",
        "CI_WAIT_SKIP", "CI_GATE_OFFLINE", "CI_GATE_RUNS_JSON", "GATE_REACHED", "GATE_RELEASE", "GATE_RC")
TRAILER = "Co-Authored-By: Claude <noreply@anthropic.com>"
WARNING = "tree differs from the branch tree after the push"      # push_clean's AF-AP-216 line

FAKE_GATE = """import os, pathlib, sys, time
reached, release = os.environ.get("GATE_REACHED"), os.environ.get("GATE_RELEASE")
if reached:
    pathlib.Path(reached).write_text("reached")
if release:
    deadline = time.monotonic() + 120
    while not os.path.exists(release) and time.monotonic() < deadline:
        time.sleep(0.05)
sys.exit(int(os.environ.get("GATE_RC", "0")))
"""
FAKE_EXPORT = """import pathlib, sys
out = pathlib.Path(sys.argv[sys.argv.index("--out") + 1])
out.mkdir(parents=True, exist_ok=True)
(out / "digest.md").write_text("a digest")
"""


def _env(**extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_") and k not in DROP}
    env.update(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t",
               GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", FILTER_BRANCH_SQUELCH_WARNING="1")
    env.update({k: str(v) for k, v in extra.items()})
    return env


def _git(cwd, *args):
    r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env=_env(), timeout=60)
    assert r.returncode == 0, (args, r.stderr)
    return r.stdout.strip()


@pytest.fixture
def w(tmp_path):
    origin, root, hooks = tmp_path / "origin.git", tmp_path / "work", tmp_path / "hooks"
    hooks.mkdir()
    (hooks / "pre-commit").symlink_to(SCRIPTS / "hooks" / "pre-commit")
    _git(tmp_path, "init", "-q", "--bare", str(origin))
    _git(tmp_path, "init", "-q", "-b", "feat", str(root))
    (root / "scripts").mkdir()
    for name in UNDER_TEST:
        shutil.copy2(SCRIPTS / name, root / "scripts" / name)
    (root / "scripts" / "ci_gate.py").write_text(FAKE_GATE)
    (root / "scripts" / "gate_files.txt").write_text("# gate files: none in this throwaway repo\n")
    (root / "f.txt").write_text("1\n")
    (root / "lane.txt").write_text("a lane's file\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    _git(root, "remote", "add", "origin", str(origin))
    _git(root, "push", "-q", "origin", "feat")
    (root / "f.txt").write_text("2\n")
    _git(root, "commit", "-q", "-am", f"work to push\n\n{TRAILER}")      # the rewrite gives it a new id on origin
    for name in HOOK_SCRIPTS:                                             # the hook's other gates, real, untracked
        (root / "scripts" / name).symlink_to(SCRIPTS / name)
    (root / ".git" / "info" / "exclude").write_text(
        ".lanes-live\nscripts/transcript_export.py\n" + "".join(f"scripts/{n}\n" for n in HOOK_SCRIPTS))
    _git(root, "config", "core.hooksPath", str(hooks))
    return SimpleNamespace(root=root, origin=origin, lock=root / ".git" / "push-in-flight",
                           reached=tmp_path / "gate-reached", release=tmp_path / "gate-release",
                           unpushed=_git(root, "rev-parse", "HEAD"))


def _push(w, *args, **env):
    return subprocess.Popen(["bash", str(w.root / "scripts" / "push_clean.sh"), *args], cwd=w.root, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            env=_env(PUSH_BRANCH="feat", TRANSCRIPT_SYNC="0", **env))


def _held_at_the_gate(w, *args):
    """push_clean started and held at the fake gate (inside the inner run under --lanes-live)."""
    proc = _push(w, *args, GATE_REACHED=w.reached, GATE_RELEASE=w.release)
    deadline = time.monotonic() + 60
    while not w.reached.exists():
        assert proc.poll() is None, "push_clean ended before its gate: " + proc.communicate()[0]
        assert time.monotonic() < deadline, "push_clean did not reach its gate"
        time.sleep(0.05)
    return proc


def _declare_a_live_lane(w):
    (w.root / ".lanes-live").write_text("lane.txt\n")
    (w.root / "lane.txt").write_text("the lane edits its file\n")       # the dirty set is the declared lane file


def _leftovers(w):
    return sorted(p.name for p in w.lock.parent.glob("push-in-flight*"))


def test_a_commit_during_the_inner_push_waits_and_lands_on_the_pushed_tip(w):
    """AF-AP-216, reproduced: without the lock the commit lands mid-push and the ref is left unfollowed."""
    _declare_a_live_lane(w)
    push, commit = _held_at_the_gate(w, "--lanes-live"), None
    try:
        lock_at_gate = w.lock.read_text().strip() if w.lock.exists() else None
        (w.root / "wiki.md").write_text("a wiki block\n")
        commit = subprocess.Popen(["bash", str(w.root / "scripts" / "safe_commit.sh"), "-m", "wiki block", "wiki.md"],
                                  cwd=w.root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=_env())
        for _ in range(30):                     # 1.5 s: enough for a commit that does not wait to land
            if commit.poll() is not None:
                break
            time.sleep(0.05)
        head_at_release = _git(w.root, "rev-parse", "HEAD")
    finally:
        w.release.write_text("go")
    push_out = push.communicate(timeout=120)[0]
    commit_out = commit.communicate(timeout=120)[0]
    pushed = _git(w.origin, "rev-parse", "refs/heads/feat")
    assert WARNING not in push_out, push_out                                 # the symptom of AF-AP-216
    assert push.returncode == 0 and "branch ref followed origin" in push_out, push_out
    assert commit.returncode == 0, commit_out
    assert head_at_release == w.unpushed, "the commit landed while the push ran"
    assert _git(w.root, "rev-parse", "HEAD^") == pushed != w.unpushed          # on the pushed (rewritten) tip
    assert _git(w.root, "log", "-1", "--format=%s") == "wiki block"
    assert _git(w.root, "rev-parse", "refs/remotes/origin/feat") == pushed
    assert lock_at_gate == str(push.pid), "the main lock names the OUTER run while the inner run pushes"
    assert commit_out.count(f"== a push is in flight (push_clean pid {push.pid}): waiting up to 600 s") == 1
    assert _leftovers(w) == []


def test_a_raw_commit_during_the_push_is_refused_by_the_real_hook_and_lands_after_it(w):
    _declare_a_live_lane(w)
    push = _held_at_the_gate(w, "--lanes-live")
    try:
        (w.root / "wiki.md").write_text("a wiki block\n")
        _git(w.root, "add", "wiki.md")
        raw = subprocess.run(["git", "commit", "-q", "-m", "raw commit"], cwd=w.root, capture_output=True, text=True,
                             env=_env(), timeout=60)
        head_at_release = _git(w.root, "rev-parse", "HEAD")
    finally:
        w.release.write_text("go")
    push_out = push.communicate(timeout=120)[0]
    assert WARNING not in push_out, push_out
    assert raw.returncode == 1, raw.stdout + raw.stderr
    assert f"COMMIT BLOCKED: a push is in flight (scripts/push_clean.sh, pid {push.pid}; lock {w.lock})" in raw.stderr
    assert head_at_release == w.unpushed
    assert push.returncode == 0 and "branch ref followed origin" in push_out, push_out
    retry = subprocess.run(["git", "commit", "-q", "-m", "raw commit"], cwd=w.root, capture_output=True, text=True,
                           env=_env(), timeout=60)
    assert retry.returncode == 0, retry.stdout + retry.stderr
    assert _git(w.root, "rev-parse", "HEAD^") == _git(w.origin, "rev-parse", "refs/heads/feat") != w.unpushed


def test_push_cleans_own_transcript_commit_passes_the_real_hook_while_it_holds_the_lock(w):
    """The exemption: push_clean exports PUSH_IN_FLIGHT_PID, and its transcript-digest sync commits under it."""
    (w.root / "scripts" / "transcript_export.py").write_text(FAKE_EXPORT)
    r = subprocess.run(["bash", str(w.root / "scripts" / "push_clean.sh"), "--no-delegates-live"], cwd=w.root,
                       capture_output=True, text=True, timeout=120, env=_env(PUSH_BRANCH="feat"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert "== transcripts synced:" in r.stdout and "transcript sync: commit/push failed" not in r.stderr, r.stderr
    tip = _git(w.origin, "rev-parse", "refs/heads/feat")
    assert _git(w.origin, "log", "-1", "--format=%s", tip).startswith("transcripts: scrubbed sandbox chat digests")
    assert _git(w.origin, "show", f"{tip}:transcripts/sandbox/digest.md") == "a digest"
    assert _leftovers(w) == []


def test_a_live_lock_held_by_another_process_refuses_the_run_and_is_left_as_it_is(w):
    holder = subprocess.Popen(["sleep", "60"])
    try:
        w.lock.write_text(f"{holder.pid}\n")
        r = subprocess.run(["bash", str(w.root / "scripts" / "push_clean.sh"), "--no-delegates-live"], cwd=w.root,
                           capture_output=True, text=True, timeout=120, env=_env(PUSH_BRANCH="feat", TRANSCRIPT_SYNC="0"))
        assert r.returncode == 5, r.stdout + r.stderr
        assert (f"REFUSED: another push_clean (pid {holder.pid}) holds the push lock {w.lock}; wait for it to end."
                in r.stderr)
        assert w.lock.read_text() == f"{holder.pid}\n" and _leftovers(w) == ["push-in-flight"]
        assert _git(w.origin, "rev-parse", "refs/heads/feat") == _git(w.root, "rev-parse", "HEAD^")   # nothing pushed
    finally:
        holder.kill()
        holder.wait()


def _dead_pid():
    proc = subprocess.Popen(["true"])
    proc.wait()
    return proc.pid


def test_a_stale_lock_is_replaced_with_one_line_and_the_run_goes_on(w):
    dead = _dead_pid()
    w.lock.write_text(f"{dead}\n")
    r = subprocess.run(["bash", str(w.root / "scripts" / "push_clean.sh"), "--no-delegates-live"], cwd=w.root,
                       capture_output=True, text=True, timeout=120, env=_env(PUSH_BRANCH="feat", TRANSCRIPT_SYNC="0"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stderr.count(f"push_clean: a stale push lock (pid {dead}, not running) was replaced.") == 1, r.stderr
    assert _git(w.origin, "rev-parse", "refs/heads/feat") == _git(w.root, "rev-parse", "HEAD") != w.unpushed
    assert _leftovers(w) == []


def test_the_lock_names_the_run_while_it_runs_and_a_signal_still_releases_it(w):
    """bash handles a TERM that arrives during a foreground child when the child returns (measured): the release file
    ends the fake gate, bash then runs its EXIT trap and dies, and nothing after the gate runs."""
    base = _git(w.origin, "rev-parse", "refs/heads/feat")
    push = _held_at_the_gate(w, "--no-delegates-live")
    try:
        held = w.lock.read_text()
        push.send_signal(signal.SIGTERM)
    finally:
        w.release.write_text("go")
    push.communicate(timeout=60)
    assert held == f"{push.pid}\n"
    assert push.returncode in (143, -signal.SIGTERM), push.returncode
    assert _leftovers(w) == []
    assert _git(w.origin, "rev-parse", "refs/heads/feat") == base            # the signal stopped the push


def test_a_run_never_removes_a_lock_it_does_not_hold(w, holder):
    """If the lock names another live run when this one ends (a replacement it did not make), it stays."""
    push = _held_at_the_gate(w, "--no-delegates-live")
    try:
        w.lock.write_text(f"{holder.pid}\n")
    finally:
        w.release.write_text("go")
    out = push.communicate(timeout=120)[0]
    assert push.returncode == 0, out
    assert w.lock.read_text() == f"{holder.pid}\n"


@pytest.mark.parametrize("case", ["bad mode", "dirty tree", "lanes-live without .lanes-live", "red gate"])
def test_every_refusal_releases_the_lock(w, case):
    args, env = ["--no-delegates-live"], {}
    if case == "bad mode":
        args = ["--frobnicate"]
    elif case == "dirty tree":
        (w.root / "f.txt").write_text("dirty\n")
    elif case == "lanes-live without .lanes-live":
        args = ["--lanes-live"]
    else:
        env = {"GATE_RC": "1"}
    r = subprocess.run(["bash", str(w.root / "scripts" / "push_clean.sh"), *args], cwd=w.root, capture_output=True,
                       text=True, timeout=120, env=_env(PUSH_BRANCH="feat", TRANSCRIPT_SYNC="0", **env))
    assert r.returncode == 1, r.stdout + r.stderr
    assert _leftovers(w) == []


# --- scripts/safe_commit.sh and the real pre-commit hook against a lock the test holds (a sleeping process's pid) -----

def _safe_commit(w, **env):
    (w.root / "wiki.md").write_text("a wiki block\n")
    return subprocess.run(["bash", str(w.root / "scripts" / "safe_commit.sh"), "-m", "wiki block", "wiki.md"],
                          cwd=w.root, capture_output=True, text=True, timeout=60, env=_env(**env))


@pytest.fixture
def holder():
    proc = subprocess.Popen(["sleep", "60"])
    yield proc
    proc.kill()
    proc.wait()


def test_safe_commit_refuses_after_its_bounded_wait_and_stages_nothing(w, holder):
    w.lock.write_text(f"{holder.pid}\n")
    r = _safe_commit(w, SAFE_COMMIT_LOCK_WAIT="1")
    assert r.returncode == 5, r.stdout + r.stderr
    assert r.stdout.count(f"== a push is in flight (push_clean pid {holder.pid}): waiting up to 1 s") == 1, r.stdout
    assert (f"REFUSED: push_clean (pid {holder.pid}) still holds the push lock {w.lock} after 1 s; nothing staged."
            in r.stderr)
    assert _git(w.root, "diff", "--cached", "--name-only") == ""
    assert _git(w.root, "rev-parse", "HEAD") == w.unpushed


def test_safe_commit_waits_and_commits_once_the_lock_holder_ends(w):
    """The holder behaves as push_clean does: it names itself in the lock and removes the lock as it ends. (A holder
    that dies without removing it stays live to kill -0 until its parent reaps it; see the report's limits.)"""
    short = subprocess.Popen(["bash", "-c", f'echo $$ > "{w.lock}"; sleep 2; rm -f "{w.lock}"'])
    try:
        deadline = time.monotonic() + 30
        while not w.lock.exists():
            assert time.monotonic() < deadline
            time.sleep(0.02)
        r = _safe_commit(w, SAFE_COMMIT_LOCK_WAIT="30")
    finally:
        short.wait()
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.count(f"== a push is in flight (push_clean pid {short.pid}): waiting up to 30 s") == 1, r.stdout
    assert r.stdout.count("== a push is in flight") == 1, r.stdout
    assert _git(w.root, "log", "-1", "--format=%s") == "wiki block"


@pytest.mark.parametrize("case", ["stale", "own run"])
def test_safe_commit_does_not_wait_for_a_stale_lock_or_its_own_run(w, holder, case):
    if case == "stale":                               # a short bound: a wrong wait fails fast, never hangs
        w.lock.write_text(f"{_dead_pid()}\n")
        r = _safe_commit(w, SAFE_COMMIT_LOCK_WAIT="5")
    else:
        w.lock.write_text(f"{holder.pid}\n")
        r = _safe_commit(w, SAFE_COMMIT_LOCK_WAIT="5", PUSH_IN_FLIGHT_PID=holder.pid)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "a push is in flight" not in r.stdout
    assert _git(w.root, "log", "-1", "--format=%s") == "wiki block"


@pytest.mark.parametrize("value", ["abc", "-1", "1.5", ""])
def test_safe_commit_refuses_a_malformed_wait_before_staging(w, value):
    r = _safe_commit(w, SAFE_COMMIT_LOCK_WAIT=value)
    if value == "":                                   # an empty value is unset: the default applies
        assert r.returncode == 0, r.stdout + r.stderr
        return
    assert r.returncode == 1 and "usage: SAFE_COMMIT_LOCK_WAIT takes whole seconds" in r.stderr, r.stdout + r.stderr
    assert _git(w.root, "diff", "--cached", "--name-only") == ""


def test_the_lock_gate_is_the_hooks_last_gate():
    """Placed last, only the commit-msg hook runs between the check and git's ref update (its checker took 0.035 s,
    measured, against 0.25 s more for the gates above): that is the window in which a commit that passed the check can
    still land after a push began. Placed first, the window held every other gate."""
    hook = (SCRIPTS / "hooks" / "pre-commit").read_text()
    lock = hook.index('_PLOCK="$(git rev-parse --path-format=absolute --git-path push-in-flight')
    assert hook.rindex('"$PY" "$REPO_ROOT/scripts/') < lock < hook.rindex("\nexit 0")


def _raw_commit(w, **env):
    (w.root / "wiki.md").write_text("a wiki block\n")
    _git(w.root, "add", "wiki.md")
    return subprocess.run(["git", "commit", "-q", "-m", "raw commit"], cwd=w.root, capture_output=True, text=True,
                          env=_env(**env), timeout=60)


@pytest.mark.parametrize("case", ["live", "other pid named", "holder named", "stale"])
def test_the_real_hook_refuses_a_raw_commit_only_while_another_run_holds_the_lock(w, holder, case):
    other = subprocess.Popen(["sleep", "60"])
    try:
        w.lock.write_text(f"{_dead_pid() if case == 'stale' else holder.pid}\n")
        named = {"other pid named": other.pid, "holder named": holder.pid}.get(case)
        r = _raw_commit(w, **({"PUSH_IN_FLIGHT_PID": named} if named else {}))
    finally:
        other.kill()
        other.wait()
    if case in ("holder named", "stale"):
        assert r.returncode == 0, r.stdout + r.stderr
        assert _git(w.root, "log", "-1", "--format=%s") == "raw commit"
    else:
        assert r.returncode == 1, r.stdout + r.stderr
        assert f"COMMIT BLOCKED: a push is in flight (scripts/push_clean.sh, pid {holder.pid}; lock {w.lock})" in r.stderr
        assert _git(w.root, "rev-parse", "HEAD") == w.unpushed
