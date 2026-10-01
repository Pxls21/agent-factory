"""scripts/hook_context.py and scripts/install_session_hooks.py (task #214, AF-AP-172).

hook_context turns a hook's plain stdout into additionalContext (the only PreToolUse/PostToolUse output the model reads,
measured live 2026-09-24); install_session_hooks registers 15 project hooks for a session rooted above the repo
(task_sync.py, LS-B7, on Stop and SessionStart with a 30-second timeout; its own behavior is tests/test_task_sync.py's;
the stack catalog, LS-B9 round 4, on SessionStart for start, resume and compact; its text is tests/test_stack.py's;
the chat form, LS-B10, scripts/ls_req.py on UserPromptSubmit, Stop and SessionStart, last in each list; its behavior is
tests/test_ls_req.py's; the file packs, K2, scripts/filepacks.py on PreToolUse and SessionStart; its behavior is
tests/test_filepacks.py's).
The end-to-end tests run the INSTALLED command strings through a shell, so a quoting or path defect fails here.
Since S1-RATE (task #295) the wrapper stamps what it hands the model: a first line `[S1 <id> <source>]` and a last line
that asks for the score. `unstamp` checks both against literals (tests/test_s1_rate.py holds the stamp's own tests), and
AF_S1_RATE_STATE keeps the wrapper's telemetry out of the real .jev/.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WRAP = ROOT / "scripts" / "hook_context.py"
INSTALL = ROOT / "scripts" / "install_session_hooks.py"
MARKER = f"{ROOT}/.claude/hooks/"
SYNC = f"{ROOT}/scripts/task_sync.py"
CATALOG = f"{ROOT}/scripts/stack.py catalog"
REQ = f"{ROOT}/scripts/ls_req.py"
FILEPACKS = f"{ROOT}/scripts/filepacks.py"
STAMP = re.compile(r"\[S1 (s1-[0-9a-f]{8}) ([A-Za-z0-9_.-]+)\]")
REQUEST = ('Begin your next text with "S1-RATE {id} rel=R use=U" (+ a note <=120 chars: why, if a 0), one line per '
           'unscored injection. rel 0 unrelated,1 same area not this step,2 relevant to this step,3 governs it; '
           'use 0 noise/known,1 confirms,2 used it,3 changed what I did')


@pytest.fixture(autouse=True)
def _s1_rate_state(tmp_path, monkeypatch):
    monkeypatch.setenv("AF_S1_RATE_STATE", str(tmp_path / "s1-rate-state"))


def unstamp(text, source):
    """The lines between a stamped text's stamp line and its request line, both checked against the literals."""
    first, _, rest = text.partition("\n")
    m = STAMP.fullmatch(first)
    assert m and m.group(2) == source, first[:80]
    body, _, last = rest.rpartition("\n")
    assert last == REQUEST.format(id=m.group(1)), last[:80]
    return body


def wrap(event, cmd, stdin=b""):
    return subprocess.run([sys.executable, str(WRAP), event, "--", *cmd], input=stdin, capture_output=True, timeout=60)


def install(target, *extra):
    return subprocess.run([sys.executable, str(INSTALL), "--target", str(target), *extra],
                          capture_output=True, text=True, timeout=60)


# ---- hook_context.py ----

def test_output_becomes_additional_context():
    r = wrap("PostToolUse", ["printf", "line one\nline two\n"])
    assert r.returncode == 0
    obj = json.loads(r.stdout)
    assert list(obj) == ["hookSpecificOutput"] and list(obj["hookSpecificOutput"]) == ["hookEventName",
                                                                                     "additionalContext"]
    assert obj["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert unstamp(obj["hookSpecificOutput"]["additionalContext"], "printf") == "line one\nline two"


def test_no_output_prints_nothing():
    r = wrap("PreToolUse", ["true"])
    assert (r.returncode, r.stdout, r.stderr) == (0, b"", b"")


def test_stdin_reaches_the_hook():
    r = wrap("PreToolUse", ["cat"], stdin=b'{"tool_name": "Grep"}')
    assert unstamp(json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"], "cat") == '{"tool_name": "Grep"}'


def test_a_blocking_exit_keeps_its_code_and_stdout_and_its_stderr_is_stamped():
    r = wrap("PreToolUse", ["sh", "-c", "echo out; echo blocked >&2; exit 2"])
    assert (r.returncode, r.stdout) == (2, b"out\n")
    err = r.stderr.decode()
    assert err.endswith("\n") and unstamp(err[:-1], "sh") == "blocked"      # the model reads a PreToolUse block


def test_usage_errors_never_block():
    for argv in ([], ["PostToolUse"], ["PostToolUse", "true"], ["Stop", "--", "true"]):
        r = subprocess.run([sys.executable, str(WRAP), *argv], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0 and r.stdout == "" and "usage" in r.stderr, argv


def test_a_command_that_cannot_run_never_blocks():
    r = wrap("PostToolUse", ["/nonexistent/hook-binary"])
    assert r.returncode == 0 and r.stdout == b"" and b"did not run" in r.stderr


def test_real_graft_nag_reaches_the_model_form():
    hook = ["python3", str(ROOT / ".claude/hooks/graft-first-nag.py")]
    semantic = json.dumps({"tool_name": "Grep", "tool_input": {"pattern": "parse_lock", "path": "scripts"}}).encode()
    literal = json.dumps({"tool_name": "Grep", "tool_input": {"pattern": "^PROOF-STATUS: S0-0[0-9]", "path": "todo"}}).encode()
    hit = wrap("PreToolUse", hook, stdin=semantic)
    assert "GRAFT-FIRST" in json.loads(hit.stdout)["hookSpecificOutput"]["additionalContext"]
    assert wrap("PreToolUse", hook, stdin=literal).stdout == b""


def test_real_edit_snapshot_screen_reaches_the_model_form():
    hook = ["python3", str(ROOT / ".claude/hooks/edit-snapshot.py")]
    hunk = '        except (OSError, IOError):\n            state = "gone"\n        assert state == "Z"\n'
    payload = {"tool_name": "Edit", "tool_input": {"file_path": f"{ROOT}/tests/test_probe_only.py", "new_string": hunk}}
    r = wrap("PostToolUse", hook, stdin=json.dumps(payload).encode())
    assert "AF-AP-181" in json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]


# ---- install_session_hooks.py ----

def test_fresh_install_registers_and_prints_15_hooks(tmp_path):
    """15 hooks since K2 (LS-B10's three and K2's two, each family counted through hook_count), and the installer says
    so: its install line prints the count and --help states it, both counted from what it registers, never a literal,
    and the help names no other count (VERIFY-LS-B10 F10). Mutants: the old literal 8 in either line; a count of the
    events (5) in place of the hooks; a count written into the docstring's first line ("eight", or a 15 that the next
    hook would make stale)."""
    target = tmp_path / ".claude" / "settings.json"
    mine = ish.our_hooks(ROOT)
    family = {name: ish.hook_count({ev: [g for g in groups if key in g["hooks"][0]["command"]]
                                    for ev, groups in mine.items()}) for name, key in (("ls_req", REQ),
                                                                                       ("filepacks", FILEPACKS))}
    assert (family, ish.hook_count(mine)) == ({"ls_req": 3, "filepacks": 2}, 15), (family, ish.hook_count(mine))
    r = install(target)
    assert r.returncode == 0 and "installed 15 in" in r.stdout
    hooks = json.loads(target.read_text())["hooks"]
    assert sorted(hooks) == ["PostToolUse", "PreToolUse", "SessionStart", "Stop", "UserPromptSubmit"]
    cmds = {ev: [h["command"] for e in v for h in e["hooks"]] for ev, v in hooks.items()}
    assert {ev: len(c) for ev, c in cmds.items()} == {"PostToolUse": 1, "PreToolUse": 3, "SessionStart": 5, "Stop": 3,
                                                      "UserPromptSubmit": 3}
    assert f"installed {sum(map(len, cmds.values()))} in" in r.stdout     # the count printed is the count written
    h = install(tmp_path / "help.json", "--help")
    assert h.returncode == 0 and "It registers 15 hooks." in " ".join(h.stdout.split()), h.stdout
    assert not (tmp_path / "help.json").exists()
    said = re.findall(r"\b(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|"
                      r"fifteen)\b", " ".join(h.stdout.split()).lower())
    assert said == ["15"], said                    # no written count beside the counted one (F10: it said eight)
    assert all(MARKER in c or SYNC in c or CATALOG in c or REQ in c or FILEPACKS in c for cs in cmds.values()
               for c in cs)
    assert cmds["SessionStart"][1].endswith(f"python3 {SYNC} --hook session-start")       # LS-B7: after the others
    assert CATALOG in cmds["SessionStart"][2]                                              # LS-B9 round 4: after it
    assert cmds["Stop"][1].endswith(f"python3 {SYNC} --hook stop")
    assert "hook_context.py PostToolUse --" in cmds["PostToolUse"][0]
    assert "hook_context.py PreToolUse --" in cmds["PreToolUse"][0]
    assert hooks["PostToolUse"][0]["matcher"] == "Edit|Write|Read"
    assert [e["matcher"] for e in hooks["PreToolUse"]] == ["Grep|Bash", "Write|Edit|Bash", "Read|Edit|Write|Bash"]
    assert "/.claude/hooks/search-intercept.py" in cmds["PreToolUse"][0]
    # system1-context (S1-L1): the tool event and the prompt event, both through the wrapper; wiki-context through the
    # wrapper too since D-095, so its excerpt carries the S1-RATE stamp
    assert "hook_context.py PreToolUse -- python3" in cmds["PreToolUse"][1]
    assert cmds["PreToolUse"][1].endswith("/.claude/hooks/system1-context.py")
    assert "hook_context.py UserPromptSubmit -- python3" in cmds["UserPromptSubmit"][0]
    assert cmds["UserPromptSubmit"][0].endswith(f"python3 {ROOT}/.claude/hooks/wiki-context.py")
    assert "hook_context.py UserPromptSubmit -- python3" in cmds["UserPromptSubmit"][1]
    assert cmds["UserPromptSubmit"][1].endswith("/.claude/hooks/system1-context.py")


def test_second_install_is_a_no_op(tmp_path):
    target = tmp_path / "settings.json"
    install(target)
    before = target.read_bytes()
    r = install(target)
    assert r.returncode == 0 and "unchanged" in r.stdout and target.read_bytes() == before


def test_merge_keeps_foreign_keys_and_hooks_and_remove_restores_them(tmp_path):
    target = tmp_path / "settings.json"
    foreign = {"permissions": {"allow": ["Bash(ls:*)"]},
               "hooks": {"PostToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "echo other"}]}]}}
    target.write_text(json.dumps(foreign))
    assert install(target).returncode == 0
    merged = json.loads(target.read_text())
    assert merged["permissions"] == foreign["permissions"]
    assert merged["hooks"]["PostToolUse"][0] == foreign["hooks"]["PostToolUse"][0]
    assert len(merged["hooks"]["PostToolUse"]) == 2
    assert install(target, "--check").returncode == 0
    assert install(target, "--remove").returncode == 0
    assert json.loads(target.read_text()) == foreign
    assert install(target, "--check").returncode == 1


def test_an_unreadable_file_is_refused_and_left_alone(tmp_path):
    target = tmp_path / "settings.json"
    for bad in ("{not json", "[1, 2]"):
        target.write_text(bad)
        r = install(target)
        assert r.returncode == 1 and "REFUSED" in r.stderr and target.read_text() == bad


def test_installed_commands_run_through_a_shell(tmp_path):
    target = tmp_path / "settings.json"
    install(target)
    hooks = json.loads(target.read_text())["hooks"]
    pre = hooks["PreToolUse"][0]["hooks"][0]["command"]
    # a quirk payload: blocked with exit 2 through the wrapper, and it needs neither graft nor rg, which CI lacks
    # (VERIFY-JT3 F-4); the search answer itself is tested in tests/test_search_intercept.py
    quirk = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git rev-parse --short HEAD HEAD~1"}})
    env = dict(os.environ, AF_SEARCH_INTERCEPT_STATE=str(tmp_path / "intercept-state"))  # never the real .jev/
    r = subprocess.run(["sh", "-c", pre], input=quirk, capture_output=True, text=True, timeout=60, cwd="/", env=env)
    assert r.returncode == 2 and r.stdout == "" and r.stderr.endswith("\n")        # blocked once, explained, stamped
    assert unstamp(r.stderr[:-1], "search-intercept").startswith("QUIRK GUARD")
    prompt = hooks["UserPromptSubmit"][0]["hooks"][0]["command"]
    r = subprocess.run(["sh", "-c", prompt], input=json.dumps({"prompt": "what is live now"}),
                       capture_output=True, text=True, timeout=60, cwd="/")
    assert r.returncode == 0


# ---- VERIFY-COORD-0924 follow-ups (issue #67): fail open, the cd, the override, the event names, quoting, the mode ----

sys.path.insert(0, str(ROOT / "scripts"))
import install_session_hooks as ish  # noqa: E402


def _commands(root):
    return {ev: arr[0]["hooks"][0]["command"] for ev, arr in ish.our_hooks(Path(root)).items()}


def _all_commands(root):
    """(event, command) for every group of every event, not only the first (PreToolUse and UserPromptSubmit hold two)."""
    return [(ev, h["command"]) for ev, arr in ish.our_hooks(Path(root)).items() for g in arr for h in g["hooks"]]


def _fake_repo(tmp_path, hook_scripts=True, wrapper=True, stop_rc=0):
    repo = tmp_path / "repo"
    (repo / ".claude" / "hooks").mkdir(parents=True)
    (repo / "scripts").mkdir()
    if hook_scripts:
        (repo / ".claude" / "hooks" / "session-start.sh").write_text('echo "dir=$CLAUDE_PROJECT_DIR pwd=$(pwd)"\n')
        (repo / ".claude" / "hooks" / "turn-retro-gate.sh").write_text(f"echo retro >&2; exit {stop_rc}\n")
        for name in ("wiki-context.py", "edit-snapshot.py", "search-intercept.py", "system1-context.py"):
            (repo / ".claude" / "hooks" / name).write_text("import os; print('ran from', os.getcwd())\n")
        (repo / "scripts" / "filepacks.py").write_text("import os; print('ran from', os.getcwd())\n")
    if wrapper:
        (repo / "scripts" / "hook_context.py").write_bytes(WRAP.read_bytes())
    return repo


def _sh(cmd, stdin="{}", cwd="/", env=None):
    return subprocess.run(["sh", "-c", cmd], input=stdin, capture_output=True, text=True, timeout=60, cwd=cwd, env=env)


def test_every_installed_command_fails_open_when_the_repo_is_absent(tmp_path):
    cmds = _all_commands(tmp_path / "no-such-repo")
    assert len(cmds) == 15
    for ev, cmd in cmds:
        r = _sh(cmd)
        assert (r.returncode, r.stdout) == (0, ""), (ev, r.returncode, r.stdout, r.stderr)


def test_wrapped_commands_fail_open_when_the_wrapper_is_absent(tmp_path):
    repo = _fake_repo(tmp_path, wrapper=False)
    wrapped = [(ev, cmd) for ev, cmd in _all_commands(repo) if "hook_context.py" in cmd]
    assert sorted(ev for ev, _ in wrapped) == ["PostToolUse", "PreToolUse", "PreToolUse", "PreToolUse",
                                               "UserPromptSubmit", "UserPromptSubmit"]    # wiki-context since D-095
    for ev, cmd in wrapped:
        r = _sh(cmd)
        assert (r.returncode, r.stdout) == (0, ""), (ev, r.returncode, r.stderr)


def test_a_missing_hook_script_fails_open(tmp_path):
    repo = _fake_repo(tmp_path, hook_scripts=False)
    for ev, cmd in _all_commands(repo):
        r = _sh(cmd)
        assert (r.returncode, r.stdout) == (0, ""), (ev, r.returncode, r.stderr)


def test_a_present_hook_keeps_its_blocking_exit(tmp_path):
    repo = _fake_repo(tmp_path, stop_rc=2)
    r = _sh(_commands(repo)["Stop"])
    assert r.returncode == 2 and "retro" in r.stderr


def test_commands_run_from_the_repo_and_session_start_gets_the_project_dir(tmp_path):
    repo = _fake_repo(tmp_path)
    cmds = _commands(repo)
    env = {"PATH": "/usr/bin:/bin", "CLAUDE_PROJECT_DIR": "/elsewhere"}
    r = _sh(cmds["SessionStart"], env=env)
    assert r.returncode == 0 and r.stdout.strip() == f"dir={repo} pwd={repo}", r.stdout
    r = _sh(cmds["UserPromptSubmit"])          # wiki-context, through the wrapper since D-095: its text arrives stamped
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"].split("\n")
    assert re.fullmatch(r"\[S1 s1-[0-9a-f]{8} wiki-context\]", ctx[0]) and ctx[1] == f"ran from {repo}", ctx


def test_wrapped_commands_name_their_own_event(tmp_path):
    for ev, cmd in _all_commands(tmp_path):
        if "hook_context.py" in cmd:
            assert cmd.rsplit("hook_context.py ", 1)[1].split(" ", 1)[0] == ev, (ev, cmd)  # the call, not the guard
    repo = _fake_repo(tmp_path)
    for ev, cmd in _all_commands(repo):
        if "hook_context.py" in cmd:
            r = _sh(cmd)
            assert json.loads(r.stdout)["hookSpecificOutput"]["hookEventName"] == ev, (ev, r.stdout)


def test_a_real_read_from_another_cwd_reaches_the_model_form():
    cmd = _commands(ROOT)["PostToolUse"]
    payload = json.dumps({"tool_name": "Read", "tool_input": {"file_path": str(INSTALL)}})
    r = _sh(cmd, stdin=payload, cwd="/")
    assert r.returncode == 0 and "READ CONTEXT" in json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]


def test_a_repo_path_that_needs_quoting_stays_idempotent_and_removable(tmp_path):
    root = Path("/tmp/a b'c/agent-factory")
    foreign = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo other"}]}]}}
    once = ish.merged(foreign, root, remove=False)
    assert ish.merged(once, root, remove=False) == once
    assert sum(len(v) for v in once["hooks"].values()) == 16
    assert ish.merged(once, root, remove=True) == foreign


def test_a_foreign_hook_in_a_group_with_ours_survives_install_and_remove(tmp_path):
    """S1-L1-R1 F19: the merge works hook by hook. A foreign hook someone put in one of our groups stays there, under
    that group's matcher, through an install and through --remove."""
    target = tmp_path / "settings.json"
    assert install(target).returncode == 0
    s = json.loads(target.read_text())
    next(g for g in s["hooks"]["PreToolUse"] if g["matcher"] == "Write|Edit|Bash")["hooks"].append(
        {"type": "command", "command": "echo foreign"})
    target.write_text(json.dumps(s))
    assert install(target).returncode == 0
    groups = json.loads(target.read_text())["hooks"]["PreToolUse"]
    assert ("Write|Edit|Bash", "echo foreign") in [(g.get("matcher"), h["command"]) for g in groups for h in g["hooks"]]
    assert install(target, "--remove").returncode == 0
    assert json.loads(target.read_text()) == {"hooks": {"PreToolUse": [
        {"matcher": "Write|Edit|Bash", "hooks": [{"type": "command", "command": "echo foreign"}]}]}}


def test_remove_takes_out_only_our_exact_commands(tmp_path):
    """S1-L1-R1 F19: a hook of the owner's own that names a script in the repo's hooks directory is not ours; --remove
    leaves it."""
    target = tmp_path / "settings.json"
    own = {"type": "command", "command": f"bash {ROOT}/.claude/hooks/owner-own.sh"}
    assert install(target).returncode == 0
    s = json.loads(target.read_text())
    s["hooks"]["Stop"].append({"hooks": [own]})
    target.write_text(json.dumps(s))
    assert install(target, "--remove").returncode == 0
    assert json.loads(target.read_text()) == {"hooks": {"Stop": [{"hooks": [own]}]}}


def test_the_install_keeps_the_file_mode(tmp_path):
    target = tmp_path / "settings.json"
    target.write_text("{}\n")
    target.chmod(0o600)
    assert install(target).returncode == 0
    assert (target.stat().st_mode & 0o777) == 0o600


# ---- LS-B7: task_sync.py on Stop and SessionStart, each with a 30-second timeout (the brief's evidence demand 5) ----

SYNC_LEDGER = ("# BUILD TASK LIST\n\n## 2. LIVE ledger (append-only sync blocks; newest first)\n\n"
               f"**TASK #10 REGISTERED {chr(0x2014)} 2026-09-28 10:0xZ.** #10 (the sync hook): write the view.\n")


def _sync_repo(tmp_path):
    """A temp repo with a copy of task_sync.py and a one-task ledger: the hooks never see the main tree's .jev/."""
    repo = _fake_repo(tmp_path)
    shutil.copyfile(ROOT / "scripts" / "task_sync.py", repo / "scripts" / "task_sync.py")
    (repo / "todo").mkdir()
    (repo / "todo" / "BUILD-TASKLIST.md").write_text(SYNC_LEDGER, encoding="utf-8")
    return repo


def _sync_groups(hooks):
    return {ev: [g for g in hooks[ev] if "scripts/task_sync.py" in g["hooks"][0]["command"]]
            for ev in ("SessionStart", "Stop")}


def test_the_task_sync_hooks_are_installed_with_a_30_second_timeout(tmp_path):
    target = tmp_path / "settings.json"
    assert install(target).returncode == 0
    hooks = json.loads(target.read_text())["hooks"]
    groups = _sync_groups(hooks)
    for ev, arg in (("SessionStart", "session-start"), ("Stop", "stop")):
        assert len(groups[ev]) == 1 and "matcher" not in groups[ev][0]
        h = groups[ev][0]["hooks"]
        assert len(h) == 1 and type(h[0].get("timeout")) is int and h[0].get("timeout") == 30
        assert h[0]["command"] == (f"[ -f {ROOT}/scripts/task_sync.py ] || exit 0; cd {ROOT} || exit 0; "
                                   f"python3 {SYNC} --hook {arg}")
    others = [h for v in hooks.values() for g in v for h in g["hooks"]
              if "task_sync.py" not in h["command"] and "stack.py catalog" not in h["command"]
              and "ls_req.py" not in h["command"]]
    assert len(others) == 9 and all("timeout" not in h for h in others)


def test_the_installed_task_sync_commands_run_against_a_temp_repo(tmp_path):
    repo = _sync_repo(tmp_path)
    groups = _sync_groups(ish.our_hooks(repo))
    stop, start = (groups[ev][0]["hooks"][0]["command"] for ev in ("Stop", "SessionStart"))
    env = dict(os.environ, CLAUDE_CONFIG_DIR=str(tmp_path / "config"))
    d = tmp_path / "config" / "tasks" / "s1"
    r = _sh(stop, stdin=json.dumps({"session_id": "s1"}), env=env)
    assert (r.returncode, r.stdout, r.stderr) == (0, "", "") and [p.name for p in d.glob("*.json")] == ["10.json"]
    r = _sh(start, stdin=json.dumps({"session_id": "s1", "source": "startup"}), env=env)
    assert r.returncode == 0 and r.stdout.startswith("Task list = the ledger's view")
    assert "#10 pending t10-sync-hook-write-the-view" in r.stdout
    (repo / ".jev" / "task-sync-off").write_text("off\n")          # the off switch: both exit 0 at once, write no file
    (d / "10.json").unlink()
    for cmd in (stop, start):
        r = _sh(cmd, stdin=json.dumps({"session_id": "s1"}), env=env)
        assert (r.returncode, r.stdout, r.stderr) == (0, "", "")
    assert not (d / "10.json").exists()
    (repo / ".jev" / "task-sync-off").unlink()                      # a sync error on Stop: exit 1, one line, never 2
    (repo / "todo" / "BUILD-TASKLIST.md").write_text("# no live section\n")
    r = _sh(stop, stdin=json.dumps({"session_id": "s1"}), env=env)
    assert (r.returncode, r.stdout, len(r.stderr.splitlines())) == (1, "", 1)


def test_an_older_task_sync_spelling_is_replaced_on_install(tmp_path):
    target = tmp_path / "settings.json"
    old = {"type": "command", "command": f"python3 {SYNC} --hook stop --an-older-spelling"}
    target.write_text(json.dumps({"hooks": {"Stop": [{"hooks": [old]}]}}))
    assert install(target).returncode == 0
    cmds = [h["command"] for g in json.loads(target.read_text())["hooks"]["Stop"] for h in g["hooks"]]
    assert sum("task_sync.py" in c for c in cmds) == 1 and old["command"] not in cmds
    assert install(target, "--check").returncode == 0


def test_the_repo_settings_register_both_task_sync_hooks(tmp_path):
    hooks = json.loads((ROOT / ".claude" / "settings.json").read_text())["hooks"]
    assert "session-start.sh" in hooks["SessionStart"][0]["hooks"][0]["command"]        # the first groups stay first
    assert "turn-retro-gate.sh" in hooks["Stop"][0]["hooks"][0]["command"]
    groups = _sync_groups(hooks)
    repo = _sync_repo(tmp_path)
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(repo), CLAUDE_CONFIG_DIR=str(tmp_path / "config"))
    for ev, arg in (("SessionStart", "session-start"), ("Stop", "stop")):
        assert len(groups[ev]) == 1
        h = groups[ev][0]["hooks"][0]
        assert type(h.get("timeout")) is int and h.get("timeout") == 30
        assert h["command"] == ("[ -f $CLAUDE_PROJECT_DIR/scripts/task_sync.py ] || exit 0; "
                                f"python3 $CLAUDE_PROJECT_DIR/scripts/task_sync.py --hook {arg}")
        r = _sh(h["command"], stdin=json.dumps({"session_id": "s2"}), env=env)
        assert r.returncode == 0 and r.stderr == "", (ev, r.stderr)
    assert (tmp_path / "config" / "tasks" / "s2" / "10.json").exists()


# ---- LS-B9 round 4 item 7: the stack catalog on SessionStart (start, resume, compact), fail loud, under 4,000 ----

CATALOG_CMD = (f"[ -f {ROOT}/scripts/stack.py ] || exit 0; cd {ROOT} || exit 0; "
               f"python3 {ROOT}/scripts/stack.py catalog "
               '|| echo "stacks: no catalog (scripts/stack.py catalog exited $?)"')


def _catalog_command(root):
    [g] = [g for g in ish.our_hooks(Path(root))["SessionStart"]
           if "scripts/stack.py catalog" in g["hooks"][0]["command"]]
    return g["hooks"][0]["command"]


def test_the_catalog_hook_is_installed_once_on_start_resume_and_compact(tmp_path):
    """One SessionStart group after LS-B7's, matcher startup|resume|compact (never on clear), a 30-second timeout, the
    command pinned; a second install changes nothing. Mutants: no matcher (it fires on clear too); the group before
    LS-B7's; no timeout."""
    target = tmp_path / "settings.json"
    assert install(target).returncode == 0
    groups = json.loads(target.read_text())["hooks"]["SessionStart"]
    ours = [g for g in groups if CATALOG in g["hooks"][0]["command"]]
    assert len(ours) == 1 and groups.index(ours[0]) == 2 and ours[0]["matcher"] == "startup|resume|compact"
    [h] = ours[0]["hooks"]
    assert (h["command"], type(h.get("timeout")), h.get("timeout")) == (CATALOG_CMD, int, 30)
    before = target.read_bytes()
    r = install(target)
    assert r.returncode == 0 and "unchanged" in r.stdout and target.read_bytes() == before


def test_the_installed_catalog_command_prints_the_catalog_under_4000_characters():
    """The installed command through a shell from another cwd: the real catalog (the heading, `stack.py list`'s lines,
    the ratings line), exit 0, under 4,000 characters (above 10,000 the harness shows only a 2,000-character preview,
    AF-AP-183; the cap on a larger registry is tests/test_stack.py's). Mutant: the hook running `stack.py list` (no
    heading, no ratings line)."""
    r = _sh(_catalog_command(ROOT), stdin=json.dumps({"source": "compact"}))
    listed = subprocess.run([sys.executable, str(ROOT / "scripts" / "stack.py"), "list"], capture_output=True,
                            text=True, timeout=60)
    assert (r.returncode, r.stderr, listed.returncode) == (0, "", 0)
    assert r.stdout.startswith("Stacks (scripts/stacks.toml): ") and listed.stdout in r.stdout
    assert r.stdout.splitlines()[-1].startswith(
        "Ratings, the content stacks only (ctx, impact, find, echo, review, cbm, why, locate, fix-echo)")
    assert len(r.stdout) < 4000


def test_the_catalog_hook_fails_loud_in_one_line_and_exits_0(tmp_path):
    """Fail loud, never silent, never blocking: a stack.py that cannot run leaves ONE line naming its exit code, and
    a registry that does not load, ONE line naming the defect; the command exits 0 each time. Mutants: the echo
    dropped (the hook prints nothing on a failure); the catalog's refusal sent to stderr (the reader sees nothing)."""
    repo = _fake_repo(tmp_path)
    cmd = _catalog_command(repo)
    (repo / "scripts" / "stack.py").write_text("raise SystemExit(3)\n")
    r = _sh(cmd)
    assert (r.returncode, r.stdout) == (0, "stacks: no catalog (scripts/stack.py catalog exited 3)\n"), r.stderr
    shutil.copyfile(ROOT / "scripts" / "stack.py", repo / "scripts" / "stack.py")
    (repo / "scripts" / "stacks.toml").write_text("version = 2\n")
    r = _sh(cmd)
    assert (r.returncode, r.stdout, r.stderr) == (0, "stacks: no catalog (registry: version: must be 1 (found 2))\n",
                                                  "")


def test_an_older_catalog_spelling_is_replaced_on_install(tmp_path):
    """The merge rule names `<repo>/scripts/stack.py catalog` as ours, so a changed command replaces the old one
    instead of printing the catalog twice. Mutant: the catalog marker left out of the merge rule (two catalog hooks)."""
    target = tmp_path / "settings.json"
    old = {"type": "command", "command": f"python3 {ROOT}/scripts/stack.py catalog --an-older-spelling"}
    target.write_text(json.dumps({"hooks": {"SessionStart": [{"matcher": "startup", "hooks": [old]}]}}))
    assert install(target).returncode == 0
    cmds = [h["command"] for g in json.loads(target.read_text())["hooks"]["SessionStart"] for h in g["hooks"]]
    assert sum("stack.py catalog" in c for c in cmds) == 1 and old["command"] not in cmds
    assert install(target, "--check").returncode == 0


# ---- LS-B10 (task #364, D-108 item 6): the chat form, scripts/ls_req.py, last on the prompt, Stop and start ----

REQ_GROUPS = (("UserPromptSubmit", "prompt", 30), ("Stop", "stop", 300), ("SessionStart", "session-start", 30))
REQ_SCRIPTS = ("ls_req.py", "stack.py", "stacks.toml", "handback_extract.py")
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}


def _req_constants():
    """The chat form's round budget, kill grace and catch-up wait, read from scripts/ls_req.py itself."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("ls_req_consts", ROOT / "scripts" / "ls_req.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ROUND_BUDGET_S, mod.KILL_GRACE_S, mod.CATCHUP_S


def _git_repo(repo, *names):
    """A temp git repository holding copies of the named repo files (one commit): the hooks keep their state in ITS
    .jev/, never the main tree's."""
    for name in names:
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, repo / name)
    env = dict(os.environ, **GIT_ENV)
    for args in (["init", "-q", "-b", "main"], ["add", "."], ["commit", "-q", "--no-verify", "-m", "one"]):
        r = subprocess.run(["git", "-C", str(repo), *args], env=env, capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
    return repo


def _text_record(tx, text, n):
    with open(tx, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"type": "assistant", "uuid": "a%d" % n, "message": {
            "id": "m%d" % n, "role": "assistant", "content": [{"type": "text", "text": text}]}},
            separators=(",", ":")) + "\n")


def test_the_chat_form_hooks_are_installed_last_with_their_timeouts(tmp_path):
    """One group each on UserPromptSubmit (`prompt`, 30 s), Stop (`stop`, 300 s) and SessionStart (`session-start`,
    30 s, every source: no matcher), each LAST in its list, the commands pinned, on no other event; the Stop timeout
    covers the hook's round budget, kill grace and catch-up wait (read from ls_req.py); a second install changes
    nothing. Mutants: a group not last; a missing timeout; the Stop timeout at 60 s (under the round budget); a matcher
    on SessionStart (a compaction or a resume missed)."""
    target = tmp_path / "settings.json"
    assert install(target).returncode == 0
    hooks = json.loads(target.read_text())["hooks"]
    for ev, arg, timeout in REQ_GROUPS:
        ours = [g for g in hooks[ev] if REQ in g["hooks"][0]["command"]]
        assert len(ours) == 1 and hooks[ev][-1] == ours[0] and "matcher" not in ours[0], (ev, hooks[ev])
        [h] = ours[0]["hooks"]
        assert (h["command"], type(h.get("timeout")), h.get("timeout")) == (
            f"[ -f {REQ} ] || exit 0; cd {ROOT} || exit 0; python3 {REQ} {arg}", int, timeout)
    assert sorted(ev for ev, v in hooks.items() for g in v for h in g["hooks"] if REQ in h["command"]) == sorted(
        ev for ev, _a, _t in REQ_GROUPS)
    budget, grace, catchup = _req_constants()
    assert budget + grace + catchup + 30 <= 300
    before = target.read_bytes()
    r = install(target)
    assert r.returncode == 0 and "unchanged" in r.stdout and target.read_bytes() == before


def test_an_older_chat_form_spelling_is_replaced_on_install(tmp_path):
    """The merge rule names `<repo>/scripts/ls_req.py` as ours, so a changed command replaces the old one instead of
    answering every request twice. Mutant: the marker left out of the merge rule (two chat-form Stop hooks)."""
    target = tmp_path / "settings.json"
    old = {"type": "command", "command": f"python3 {REQ} stop --an-older-spelling"}
    target.write_text(json.dumps({"hooks": {"Stop": [{"hooks": [old]}]}}))
    assert install(target).returncode == 0
    cmds = [h["command"] for g in json.loads(target.read_text())["hooks"]["Stop"] for h in g["hooks"]]
    assert sum("ls_req.py" in c for c in cmds) == 1 and old["command"] not in cmds
    assert install(target, "--check").returncode == 0


def test_the_repo_settings_register_the_chat_form_hooks_last():
    """The repo's own .claude/settings.json (its commands spell $CLAUDE_PROJECT_DIR): the same three groups, last in
    their lists, with the same timeouts. Mutant: an entry missing or not last; a timeout left out."""
    hooks = json.loads((ROOT / ".claude" / "settings.json").read_text())["hooks"]
    for ev, arg, timeout in REQ_GROUPS:
        assert sum("ls_req.py" in h["command"] for g in hooks[ev] for h in g["hooks"]) == 1, ev
        last = hooks[ev][-1]
        assert "matcher" not in last and len(last["hooks"]) == 1, ev
        h = last["hooks"][0]
        assert (h["command"], type(h.get("timeout")), h.get("timeout")) == (
            f"[ -f $CLAUDE_PROJECT_DIR/scripts/ls_req.py ] || exit 0; python3 $CLAUDE_PROJECT_DIR/scripts/ls_req.py "
            f"{arg}", int, timeout)
    assert not any("ls_req.py" in h["command"] for ev in ("PreToolUse", "PostToolUse") for g in hooks[ev]
                   for h in g["hooks"])


def test_the_installed_chat_form_commands_run_against_a_temp_repo(tmp_path):
    """The installed commands through a shell from another cwd, against a temp git repository holding the chat form's
    scripts: the prompt injects ONE nonce line; a Stop with no request line stays silent; a request line with the nonce
    runs through the temp repo's stack runner and comes back as exit 2 with its receipt; a compaction's SessionStart
    re-injects the nonce; with .jev/req-off every command is silent. Mutants: the event names swapped between the
    commands; the chat form registered through hook_context.py (its JSON would be stamped as text)."""
    repo = _git_repo(tmp_path / "repo", *("scripts/" + n for n in REQ_SCRIPTS))
    cmds = {ev: h["command"] for ev, groups in ish.our_hooks(repo).items() for g in groups for h in g["hooks"]
            if "ls_req.py" in h["command"]}
    assert sorted(cmds) == ["SessionStart", "Stop", "UserPromptSubmit"]
    env = {k: v for k, v in os.environ.items() if k not in ("AF_REQ_STATE", "CLAUDE_CODE_STOP_HOOK_BLOCK_CAP")}
    tx = tmp_path / "transcript.jsonl"
    tx.write_text("")
    base = {"session_id": "s9", "transcript_path": str(tx), "cwd": str(repo)}
    r = _sh(cmds["UserPromptSubmit"], stdin=json.dumps(dict(base, prompt="go")), env=env)
    out = json.loads(r.stdout)["hookSpecificOutput"]
    assert (r.returncode, r.stderr, out["hookEventName"]) == (0, "", "UserPromptSubmit")
    m = re.fullmatch(r"Chat form \(LS-B10\) nonce ([0-9a-f]{12}): [^\n]*", out["additionalContext"])
    assert m, out["additionalContext"][:200]
    nonce = m.group(1)
    assert (repo / ".jev" / "req" / "sessions" / "s9.json").is_file()
    _text_record(tx, "No request here.", 1)
    r = _sh(cmds["Stop"], stdin=json.dumps(dict(base, stop_hook_active=False)), env=env)
    assert (r.returncode, r.stdout, r.stderr) == (0, "", "")
    _text_record(tx, "REQ %s r1 premise files=scripts/ls_req.py" % nonce, 2)
    r = _sh(cmds["Stop"], stdin=json.dumps(dict(base, stop_hook_active=False)), env=env)
    assert r.returncode == 2 and re.search(r"^RES %s r1 ran rc=0 run=s-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{6}$" % nonce,
                                           r.stderr, re.M), r.stderr[:500]
    assert (repo / ".jev" / "stacks" / "runs.jsonl").is_file()          # the temp repo's runner log, never the main's
    r = _sh(cmds["SessionStart"], stdin=json.dumps(dict(base, source="compact")), env=env)
    out = json.loads(r.stdout)["hookSpecificOutput"]
    assert (r.returncode, out["hookEventName"]) == (0, "SessionStart")
    assert out["additionalContext"].startswith("Chat form (LS-B10) nonce %s: " % nonce)
    (repo / ".jev" / "req-off").write_text("off\n")
    for ev, cmd in cmds.items():
        r = _sh(cmd, stdin=json.dumps(dict(base, prompt="go", source="compact")), env=env)
        assert (r.returncode, r.stdout, r.stderr) == (0, "", ""), ev


def test_the_retro_gate_defers_while_this_stop_answers_chat_form_requests(tmp_path):
    """PM P6 (LS-B10 item 7): while this Stop's texts carry a current nonce the gate exits 0 WITHOUT writing its
    sentinel, so the retro fires at the chain's end; with no request in this Stop it fires (exit 2, the checklist, the
    sentinel written); a payload that is not JSON never defers; without scripts/ls_req.py the gate is unchanged.
    Mutants: the deferral writes the sentinel (the retro lost for this HEAD); defer on any payload; a deferral while
    scripts/ls_req.py is absent. (The guard itself is not observable: without it python cannot open the file, prints
    nothing, and the gate fires, the same outcome.)"""
    repo = _git_repo(tmp_path / "gate", ".claude/hooks/turn-retro-gate.sh", *("scripts/" + n for n in REQ_SCRIPTS))
    gate, sent = repo / ".claude" / "hooks" / "turn-retro-gate.sh", repo / ".git" / "turn-retro-acked"
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                          timeout=60).stdout.strip()
    env = dict({k: v for k, v in os.environ.items() if k != "CLAUDE_CODE_STOP_HOOK_BLOCK_CAP"},
               AF_REQ_STATE=str(tmp_path / "req-state"))
    tx = tmp_path / "transcript.jsonl"
    tx.write_text("")
    base = {"session_id": "s7", "transcript_path": str(tx)}

    def run_gate(stdin):
        return subprocess.run(["bash", str(gate)], input=stdin, capture_output=True, text=True, env=env, timeout=60,
                              cwd=str(repo))

    r = subprocess.run([sys.executable, str(repo / "scripts" / "ls_req.py"), "prompt"],
                       input=json.dumps(dict(base, prompt="go")), capture_output=True, text=True, env=env, timeout=60)
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    nonce = re.search(r"nonce ([0-9a-f]{12}):", ctx).group(1)
    _text_record(tx, "Asking.\nREQ %s r1 premise files=scripts/ls_req.py" % nonce, 1)
    r = run_gate(json.dumps(base))
    assert (r.returncode, r.stdout, r.stderr, sent.exists()) == (0, "", "", False)
    r = run_gate("{not json")
    assert r.returncode == 2 and "TURN-END RETRO" in r.stderr and sent.read_text().strip() == head
    sent.unlink()
    with open(tx, "a", encoding="utf-8") as fh:                         # the Stop that answered r1, then plain text
        fh.write(json.dumps({"type": "system", "subtype": "stop_hook_summary", "uuid": "s1", "hookErrors": ["x"]},
                            separators=(",", ":")) + "\n")
    _text_record(tx, "Done.", 2)
    r = run_gate(json.dumps(base))
    assert r.returncode == 2 and "TURN-END RETRO" in r.stderr and sent.read_text().strip() == head
    sent.unlink()
    (repo / "scripts" / "ls_req.py").unlink()
    _text_record(tx, "REQ %s r2 premise files=scripts/stack.py" % nonce, 3)
    r = run_gate(json.dumps(base))
    assert r.returncode == 2 and "TURN-END RETRO" in r.stderr and sent.read_text().strip() == head


# ---- K2 (task #353, D-106): the file packs, scripts/filepacks.py, on PreToolUse (last) and SessionStart ----

FILEPACKS_PRE = (f"[ -f {FILEPACKS} ] && [ -f {ROOT}/scripts/hook_context.py ] || exit 0; cd {ROOT} || exit 0; "
                 f"python3 {ROOT}/scripts/hook_context.py PreToolUse -- python3 {FILEPACKS} hook")
FILEPACKS_RESET = f"[ -f {FILEPACKS} ] || exit 0; cd {ROOT} || exit 0; python3 {FILEPACKS} hook --reset"


def test_the_file_pack_hooks_are_installed_before_the_chat_form(tmp_path):
    """One group on PreToolUse, last, matcher Read|Edit|Write|Bash, through the wrapper; one on SessionStart with no
    matcher (every source), after the catalog and before LS-B10's group, which stays last; neither has a timeout; the
    commands pinned; a second install changes nothing. Mutants: the reset after the chat form's group (it would no
    longer be last); a matcher on the reset (a resume or a clear missed); the tool hook unwrapped."""
    target = tmp_path / "settings.json"
    assert install(target).returncode == 0
    hooks = json.loads(target.read_text())["hooks"]
    pre = [g for g in hooks["PreToolUse"] if FILEPACKS in g["hooks"][0]["command"]]
    assert len(pre) == 1 and hooks["PreToolUse"][-1] == pre[0] and pre[0]["matcher"] == "Read|Edit|Write|Bash"
    assert pre[0]["hooks"] == [{"type": "command", "command": FILEPACKS_PRE}]
    start = [g["hooks"][0]["command"] for g in hooks["SessionStart"]]
    assert start.index(FILEPACKS_RESET) == len(start) - 2 and REQ in start[-1] and CATALOG in start[-3], start
    [g] = [g for g in hooks["SessionStart"] if g["hooks"][0]["command"] == FILEPACKS_RESET]
    assert "matcher" not in g and g["hooks"] == [{"type": "command", "command": FILEPACKS_RESET}]
    assert sorted(ev for ev, v in hooks.items() for g in v for h in g["hooks"] if FILEPACKS in h["command"]) == [
        "PreToolUse", "SessionStart"]
    before = target.read_bytes()
    r = install(target)
    assert r.returncode == 0 and "unchanged" in r.stdout and target.read_bytes() == before


def test_the_repo_settings_register_the_file_pack_hooks():
    """The repo's own .claude/settings.json (its commands spell $CLAUDE_PROJECT_DIR): the same two groups, the tool hook
    last on PreToolUse and the reset right before the chat form's last group, no timeout, the commands the file-pack
    tests run (tests/test_filepacks.py REG_PRE and REG_RESET)."""
    hooks = json.loads((ROOT / ".claude" / "settings.json").read_text())["hooks"]
    last = hooks["PreToolUse"][-1]
    assert last["matcher"] == "Read|Edit|Write|Bash" and last["hooks"] == [{"type": "command", "command": (
        "[ -f $CLAUDE_PROJECT_DIR/scripts/filepacks.py ] && [ -f $CLAUDE_PROJECT_DIR/scripts/hook_context.py ] || "
        "exit 0; python3 $CLAUDE_PROJECT_DIR/scripts/hook_context.py PreToolUse -- python3 "
        "$CLAUDE_PROJECT_DIR/scripts/filepacks.py hook")}]
    reset = hooks["SessionStart"][-2]
    assert "matcher" not in reset and reset["hooks"] == [{"type": "command", "command": (
        "[ -f $CLAUDE_PROJECT_DIR/scripts/filepacks.py ] || exit 0; python3 "
        "$CLAUDE_PROJECT_DIR/scripts/filepacks.py hook --reset")}]
    assert sum("filepacks.py" in h["command"] for ev in hooks for g in hooks[ev] for h in g["hooks"]) == 2


def test_an_older_filepacks_spelling_is_replaced_on_install(tmp_path):
    """K2 (task #353): the merge rule names `<repo>/scripts/filepacks.py` as ours, so a changed command replaces the
    old one instead of running the hook twice. Mutant: the filepacks marker left out of the merge rule."""
    target = tmp_path / "settings.json"
    old = {"type": "command", "command": f"python3 {FILEPACKS} hook --an-older-spelling"}
    target.write_text(json.dumps({"hooks": {"PreToolUse": [{"matcher": "Read", "hooks": [old]}]}}))
    assert install(target).returncode == 0
    cmds = [h["command"] for g in json.loads(target.read_text())["hooks"]["PreToolUse"] for h in g["hooks"]]
    assert sum(FILEPACKS in c for c in cmds) == 1 and old["command"] not in cmds, "an older filepacks spelling stayed"
    assert install(target, "--check").returncode == 0
