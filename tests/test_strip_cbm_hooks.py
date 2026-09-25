"""scripts/strip_cbm_hooks.py: only the codebase-memory hooks leave the settings file; everything else stays."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "strip_cbm_hooks.py"


def run(path):
    p = subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True, timeout=30)
    return p.returncode, p.stdout + p.stderr


def settings_with_cbm():
    cbm = lambda name: {"type": "command", "command": '"$HOME/.claude/hooks/%s"' % name, "timeout": 5}
    return {
        "model": "keep-me",
        "hooks": {
            "PreToolUse": [{"matcher": "Grep|Glob", "hooks": [cbm("cbm-code-discovery-gate")]},
                           {"matcher": "Bash", "hooks": [{"type": "command", "command": "python3 other_hook.py"}]}],
            "PostToolUse": [{"matcher": "Read", "hooks": [cbm("cbm-code-discovery-gate")]}],
            "SessionStart": [{"matcher": "startup", "hooks": [cbm("cbm-session-reminder"),
                                                             {"type": "command", "command": "bash session-start.sh"}]}],
            "SubagentStart": [{"matcher": "*", "hooks": [cbm("cbm-subagent-reminder")]}],
        },
    }


def test_only_the_cbm_hooks_are_removed(tmp_path):
    f = tmp_path / "settings.json"
    f.write_text(json.dumps(settings_with_cbm()))
    rc, out = run(f)
    assert rc == 0 and "removed 4 codebase-memory hook(s)" in out
    s = json.loads(f.read_text())
    assert s["model"] == "keep-me"
    assert s["hooks"] == {
        "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "python3 other_hook.py"}]}],
        "SessionStart": [{"matcher": "startup", "hooks": [{"type": "command", "command": "bash session-start.sh"}]}],
    }


def test_idempotent_and_byte_stable_on_a_second_run(tmp_path):
    f = tmp_path / "settings.json"
    f.write_text(json.dumps(settings_with_cbm()))
    run(f)
    first = f.read_bytes()
    rc, out = run(f)
    assert rc == 0 and "removed 0 codebase-memory hook(s)" in out and f.read_bytes() == first


def test_a_missing_file_is_a_no_op_and_bad_json_is_left_untouched(tmp_path):
    rc, out = run(tmp_path / "absent.json")
    assert rc == 0 and "absent; nothing to do" in out
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    rc, _ = run(bad)
    assert rc == 2 and bad.read_text() == "{not json"
