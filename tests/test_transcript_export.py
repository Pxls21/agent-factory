"""transcript_export: every planted secret class is scrubbed before it reaches disk (negative
control per class), user/assistant text survives (positive control), noise turns are dropped,
output is deterministic and idempotent. Synthetic JSONL only — never the live transcript."""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "transcript_export.py"

PLANTED = {
    "bridge-token-assign": "AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr",
    "env-token": "PC_BRIDGE_TOKEN=abcdefghijklmnop123456",
    "header": "X-Agent-Token: zzzzzzzzzzzzzzzzzzzzzz",
    "bearer": "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig",
    "openai-key": "sk-3c3d5f1e8a2b4c6d9e0f1234567890ab",
    "github-pat": "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "google-key": "AIzaSyA1234567890abcdefghijklmnopqrstuv",
    "yaml-key": "api_key: sk-live-0123456789abcdef0123",
    "bridge-url": "https://leading-twist-aruba-pulse.trycloudflare.com/exec",
    "opaque": "token=" + "Q" * 44,
}
RAW_SECRETS = ["cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr", "abcdefghijklmnop123456", "zzzzzzzzzzzzzzzzzzzzzz",
               "eyJhbGciOiJIUzI1NiJ9", "3c3d5f1e8a2b4c6d9e0f1234567890ab", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
               "AIzaSyA1234567890abcdefghijklmnopqrstuv", "sk-live-0123456789abcdef0123",
               "leading-twist-aruba-pulse", "Q" * 44]


def _entry(role, text, ts):
    return json.dumps({"type": role, "timestamp": ts, "message": {"role": role, "content": [{"type": "text", "text": text}]}})


def _write_jsonl(p):
    lines = [
        _entry("user", "please deploy; here is the banner " + " ".join(PLANTED.values()), "2026-09-03T05:00:00Z"),
        _entry("assistant", "KEEP-ME: the plan is three waves", "2026-09-03T05:01:00Z"),
        _entry("user", "Stop hook feedback: noise", "2026-09-03T05:02:00Z"),
        _entry("user", "<system-reminder> noise", "2026-09-03T05:03:00Z"),
        json.dumps({"type": "user", "timestamp": "2026-09-03T05:04:00Z", "message": {"role": "user", "content": [{"type": "tool_result", "content": "secret-in-tool-result sk-toolresult00000000000000"}]}}),
        _entry("assistant", "next day text", "2026-09-04T01:00:00Z"),
        "not json at all",
    ]
    p.write_text("\n".join(lines) + "\n")


def _run(jsonl, out):
    return subprocess.run([sys.executable, str(TOOL), "--transcript", str(jsonl), "--out", str(out)],
                          capture_output=True, text=True, timeout=60)


def test_secrets_never_reach_disk_and_text_survives(tmp_path):
    jsonl = tmp_path / "t.jsonl"
    _write_jsonl(jsonl)
    out = tmp_path / "out"
    r = _run(jsonl, out)
    assert r.returncode == 0, r.stderr
    files = sorted(out.glob("chat-*.md"))
    assert [f.name for f in files] == ["chat-2026-09-03.md", "chat-2026-09-04.md"]
    blob = "".join(f.read_text() for f in files)
    for s in RAW_SECRETS:
        assert s not in blob, f"secret survived: {s[:12]}…"
    assert "sk-toolresult" not in blob, "tool results must not be exported at all"
    assert "KEEP-ME: the plan is three waves" in blob
    assert "Stop hook feedback" not in blob and "system-reminder" not in blob
    assert "<redacted>" in blob or "redacted" in blob


def test_idempotent_and_deterministic(tmp_path):
    jsonl = tmp_path / "t.jsonl"
    _write_jsonl(jsonl)
    out = tmp_path / "out"
    assert _run(jsonl, out).returncode == 0
    first = {f.name: f.read_bytes() for f in out.glob("chat-*.md")}
    assert _run(jsonl, out).returncode == 0
    second = {f.name: f.read_bytes() for f in out.glob("chat-*.md")}
    assert first == second


def test_missing_transcript_exits_3(tmp_path):
    r = subprocess.run([sys.executable, str(TOOL), "--transcript", str(tmp_path / "nope.jsonl"), "--out", str(tmp_path / "o")],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 3 and "no transcript" in r.stderr
