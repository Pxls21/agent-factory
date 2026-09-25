"""scripts/hook_context.py and scripts/install_session_hooks.py (task #214, AF-AP-172).

hook_context turns a hook's plain stdout into additionalContext (the only PreToolUse/PostToolUse output the model reads,
measured live 2026-09-24); install_session_hooks registers the six project hooks for a session rooted above the repo.
The end-to-end tests run the INSTALLED command strings through a shell, so a quoting or path defect fails here.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAP = ROOT / "scripts" / "hook_context.py"
INSTALL = ROOT / "scripts" / "install_session_hooks.py"
MARKER = f"{ROOT}/.claude/hooks/"


def wrap(event, cmd, stdin=b""):
    return subprocess.run([sys.executable, str(WRAP), event, "--", *cmd], input=stdin, capture_output=True, timeout=60)


def install(target, *extra):
    return subprocess.run([sys.executable, str(INSTALL), "--target", str(target), *extra],
                          capture_output=True, text=True, timeout=60)


# ---- hook_context.py ----

def test_output_becomes_additional_context():
    r = wrap("PostToolUse", ["printf", "line one\nline two\n"])
    assert r.returncode == 0
    assert json.loads(r.stdout) == {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                                           "additionalContext": "line one\nline two"}}


def test_no_output_prints_nothing():
    r = wrap("PreToolUse", ["true"])
    assert (r.returncode, r.stdout, r.stderr) == (0, b"", b"")


def test_stdin_reaches_the_hook():
    r = wrap("PreToolUse", ["cat"], stdin=b'{"tool_name": "Grep"}')
    assert json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"] == '{"tool_name": "Grep"}'


def test_a_blocking_exit_passes_through_unchanged():
    r = wrap("PreToolUse", ["sh", "-c", "echo out; echo blocked >&2; exit 2"])
    assert (r.returncode, r.stdout, r.stderr) == (2, b"out\n", b"blocked\n")


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

def test_fresh_install_registers_the_six_hooks(tmp_path):
    target = tmp_path / ".claude" / "settings.json"
    r = install(target)
    assert r.returncode == 0 and "installed 6" in r.stdout
    hooks = json.loads(target.read_text())["hooks"]
    assert sorted(hooks) == ["PostToolUse", "PreToolUse", "SessionStart", "Stop", "UserPromptSubmit"]
    cmds = {ev: [h["command"] for e in v for h in e["hooks"]] for ev, v in hooks.items()}
    assert {ev: len(c) for ev, c in cmds.items()} == {"PostToolUse": 1, "PreToolUse": 2, "SessionStart": 1, "Stop": 1,
                                                      "UserPromptSubmit": 2}
    assert all(MARKER in c for cs in cmds.values() for c in cs)
    assert "hook_context.py PostToolUse --" in cmds["PostToolUse"][0]
    assert "hook_context.py PreToolUse --" in cmds["PreToolUse"][0]
    assert hooks["PostToolUse"][0]["matcher"] == "Edit|Write|Read"
    assert [e["matcher"] for e in hooks["PreToolUse"]] == ["Grep|Bash", "Write|Edit|Bash"]
    assert "/.claude/hooks/search-intercept.py" in cmds["PreToolUse"][0]
    # system1-context (S1-L1): the tool event and the prompt event, both through the wrapper; wiki-context unchanged
    assert "hook_context.py PreToolUse -- python3" in cmds["PreToolUse"][1]
    assert cmds["PreToolUse"][1].endswith("/.claude/hooks/system1-context.py")
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
    assert r.returncode == 2 and r.stdout == "" and r.stderr.startswith("QUIRK GUARD")  # blocked once, explained
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
    if wrapper:
        (repo / "scripts" / "hook_context.py").write_bytes(WRAP.read_bytes())
    return repo


def _sh(cmd, stdin="{}", cwd="/", env=None):
    return subprocess.run(["sh", "-c", cmd], input=stdin, capture_output=True, text=True, timeout=60, cwd=cwd, env=env)


def test_every_installed_command_fails_open_when_the_repo_is_absent(tmp_path):
    cmds = _all_commands(tmp_path / "no-such-repo")
    assert len(cmds) == 7
    for ev, cmd in cmds:
        r = _sh(cmd)
        assert (r.returncode, r.stdout) == (0, ""), (ev, r.returncode, r.stdout, r.stderr)


def test_wrapped_commands_fail_open_when_the_wrapper_is_absent(tmp_path):
    repo = _fake_repo(tmp_path, wrapper=False)
    wrapped = [(ev, cmd) for ev, cmd in _all_commands(repo) if "hook_context.py" in cmd]
    assert sorted(ev for ev, _ in wrapped) == ["PostToolUse", "PreToolUse", "PreToolUse", "UserPromptSubmit"]
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
    r = _sh(cmds["UserPromptSubmit"])
    assert r.stdout.strip() == f"ran from {repo}"


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
    assert sum(len(v) for v in once["hooks"].values()) == 8
    assert ish.merged(once, root, remove=True) == foreign


def test_the_install_raises_the_skill_listing_budget_and_remove_takes_only_ours():
    """D-092: at the default 0.01 the listing described 69 of 488 skills; at 0.07, all 488. The install sets at least
    ours, keeps a larger choice, replaces a non-number (a bool included), and --remove takes the key out only while it
    still holds ours."""
    k, f, root = ish.LISTING_KEY, ish.LISTING_FRACTION, Path("/x/agent-factory")
    assert ish.merged({}, root, remove=False)[k] == f
    assert ish.merged({k: 0.01}, root, remove=False)[k] == f
    assert ish.merged({k: 0.5}, root, remove=False)[k] == 0.5
    assert ish.merged({k: "0.5"}, root, remove=False)[k] == f
    assert ish.merged({k: True}, root, remove=False)[k] == f
    assert k not in ish.merged(ish.merged({}, root, remove=False), root, remove=True)
    assert ish.merged({k: 0.5}, root, remove=True)[k] == 0.5


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
