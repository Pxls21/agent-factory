"""scripts/hook_context.py and scripts/install_session_hooks.py (task #214, AF-AP-172).

hook_context turns a hook's plain stdout into additionalContext (the only PreToolUse/PostToolUse output the model reads,
measured live 2026-09-24); install_session_hooks registers the five project hooks for a session rooted above the repo.
The end-to-end tests run the INSTALLED command strings through a shell, so a quoting or path defect fails here.
"""
import json
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

def test_fresh_install_registers_the_five_hooks(tmp_path):
    target = tmp_path / ".claude" / "settings.json"
    r = install(target)
    assert r.returncode == 0 and "installed 5" in r.stdout
    hooks = json.loads(target.read_text())["hooks"]
    assert sorted(hooks) == ["PostToolUse", "PreToolUse", "SessionStart", "Stop", "UserPromptSubmit"]
    cmds = {ev: [h["command"] for e in v for h in e["hooks"]] for ev, v in hooks.items()}
    assert all(len(c) == 1 and MARKER in c[0] for c in cmds.values())
    assert "hook_context.py PostToolUse --" in cmds["PostToolUse"][0]
    assert "hook_context.py PreToolUse --" in cmds["PreToolUse"][0]
    assert hooks["PostToolUse"][0]["matcher"] == "Edit|Write|Read" and hooks["PreToolUse"][0]["matcher"] == "Grep"


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
    semantic = json.dumps({"tool_name": "Grep", "tool_input": {"pattern": "parse_lock", "path": "scripts"}})
    r = subprocess.run(["sh", "-c", pre], input=semantic, capture_output=True, text=True, timeout=60, cwd="/")
    assert r.returncode == 0 and "GRAFT-FIRST" in json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    prompt = hooks["UserPromptSubmit"][0]["hooks"][0]["command"]
    r = subprocess.run(["sh", "-c", prompt], input=json.dumps({"prompt": "what is live now"}),
                       capture_output=True, text=True, timeout=60, cwd="/")
    assert r.returncode == 0
