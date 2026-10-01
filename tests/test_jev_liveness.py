"""scripts/jev_liveness.py: the Jev liveness probe (task #407, D-123 item 7).

Every input is a fixture: a fake relay /health on a loopback port, a port with no listener, a settings file, the
pruner's decision records, the relay's day log and a transcript. The probe never sends a Jev request; the fake key in
the settings must never reach its output.
"""
from __future__ import annotations

import hashlib
import http.server
import json
import secrets
import socket
import subprocess
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "jev_liveness.py"
NOW = "2026-10-01T03:00:00Z"
OURS, UPSTREAM = "fast-jev-output-floor@agent-factory-vendor", "fast-jev-output@fast-jev-output"


def _sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


class _Health(http.server.BaseHTTPRequestHandler):
    identity: dict = {}  # set per test: the relay's reported code hashes

    def do_GET(self):  # noqa: N802 (the stdlib's name)
        body = json.dumps({"ok": True, "pid": 4242, "upstream_host": "upstream.example", "models": ["m"],
                           "counts": {"requests": 7, "relayed": 6, "refused": 1, "upstream_error": 0},
                           **_Health.identity}).encode()
        self.send_response(200 if self.path == "/health" else 404)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


@pytest.fixture(autouse=True)
def _relay_identity():
    _Health.identity = {"relay_sha256": _sha("scripts/jev_relay.py"), "scrub_sha256": _sha("scripts/transcript_export.py")}


@pytest.fixture(scope="module")
def relay_url():
    server = http.server.HTTPServer(("127.0.0.1", 0), _Health)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()


@pytest.fixture(scope="module")
def dead_url():
    with socket.socket() as sock:  # a port that was free a moment ago and has no listener now
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    return f"http://127.0.0.1:{port}"


STARTED = "2026-10-01T02:00:00Z"  # the Claude Code start the tests pass; the fixture's installs come before it


def _tree(tmp_path: Path, relay: str, *, enabled: dict, beat: str | None, bash_finish: str, floor: int = 1000,
          decisions_dir: str | None = None, updated: str = "2026-10-01T01:00:00Z") -> dict:
    tmp_path.mkdir(parents=True, exist_ok=True)
    key = "fake-" + secrets.token_hex(8)
    records = tmp_path / ".jev" / "pruner" / "decisions"
    settings = {"enabledPlugins": enabled, "pluginConfigs": {
        OURS: {"options": {"apiKey": key, "baseUrl": relay + "/v1/systemone", "minTokensFloor": floor,
                           "minTokens": floor, "decisionsDir": decisions_dir or str(records)}},
        UPSTREAM: {"options": {"baseUrl": relay + "/v1/systemone"}}}}
    (tmp_path / "settings.json").write_text(json.dumps(settings))
    (tmp_path / "installed.json").write_text(json.dumps({"version": 2, "plugins": {
        OURS: [{"scope": "project", "version": "0.1.0", "installedAt": "2026-09-30T10:00:00Z",
                "lastUpdated": "2026-09-30T10:00:00Z"},  # an older row: the newest of the rows counts
               {"scope": "user", "version": "0.1.1", "installedAt": "2026-10-01T00:30:00Z", "lastUpdated": updated}],
        UPSTREAM: [{"scope": "user", "version": "0.1.0", "installedAt": "2026-09-22T19:18:25.132Z"}]}}))
    (records / "2026-10-01").mkdir(parents=True)
    if beat:
        (records / "last.json").write_text(json.dumps({"at": beat, "decision": "below_threshold"}) + "\n")
    for name, decision in (("a", "pruned"), ("b", "kept_all")):
        (records / "2026-10-01" / f"{name}.json").write_text(json.dumps({"decision": decision}) + "\n")
    (tmp_path / ".jev" / "relay").mkdir(parents=True)
    (tmp_path / ".jev" / "relay" / "2026-10-01.jsonl").write_text(
        json.dumps({"ts": "2026-10-01T02:31:00Z", "answer": "SECRET-TEXT"}) + "\n"
        + json.dumps({"ts": "2026-10-01T02:58:00Z", "answer": "SECRET-TEXT"}) + "\n")
    transcript = tmp_path / "t.jsonl"
    transcript.write_text("\n".join(json.dumps(r) for r in [
        {"timestamp": "2026-10-01T02:50:00Z", "message": {"content": [{"type": "tool_use", "id": "b1", "name": "Bash"}]}},
        {"timestamp": bash_finish, "message": {"content": [{"type": "tool_result", "tool_use_id": "b1", "content": "x"}]}},
        {"timestamp": "2026-10-01T02:59:59Z", "message": {"content": [{"type": "tool_use", "id": "r1", "name": "Read"}]}},
        {"timestamp": "2026-10-01T02:59:59Z", "message": {"content": [{"type": "tool_result", "tool_use_id": "r1"}]}},
    ]) + "\n")
    return {"key": key, "transcript": transcript}


def _run(tmp_path: Path, relay: str, dead: str, transcript: Path, *extra: str) -> subprocess.CompletedProcess:
    argv = [sys.executable, str(SCRIPT), "--settings", str(tmp_path / "settings.json"), "--root", str(tmp_path),
            "--installed", str(tmp_path / "installed.json"), "--claude-started", STARTED,
            "--transcript", str(transcript), "--now", NOW, "--endpoint", f"relay={relay}",
            "--endpoint", f"laya={dead}", "--endpoint", f"qwen={dead}", *extra]
    return subprocess.run(argv, capture_output=True, text=True, timeout=60)


def test_a_live_system_reports_its_counts_and_no_warning(tmp_path, relay_url, dead_url):
    tree = _tree(tmp_path, relay_url, enabled={OURS: True, UPSTREAM: False}, beat="2026-10-01T02:59:30Z",
                 bash_finish="2026-10-01T02:59:00Z")
    run = _run(tmp_path, relay_url, dead_url, tree["transcript"])
    assert run.returncode == 0, run.stderr
    lines = run.stdout.splitlines()
    assert lines[0] == "jev pulse"
    assert lines[1] == (f"  relay :{relay_url.rsplit(':', 1)[1]} ok (pid 4242, to upstream.example; since start 6 relayed, "
                        "1 refused, 0 upstream errors; log today 2 rows, newest 2026-10-01T02:58:00Z)")
    assert lines[2].startswith(f"  laya :{dead_url.rsplit(':', 1)[1]} down (")
    assert lines[4] == (f"  pruner our copy ({OURS}) on, floor 1000 tokens, to {relay_url}/v1/systemone; heartbeat 30s ago "
                        "(below_threshold); today past the floor: 2 (kept_all 1, pruned 1)")
    assert "WARN" not in run.stdout
    assert tree["key"] not in run.stdout and "SECRET-TEXT" not in run.stdout


def test_a_bash_call_the_hook_never_saw_is_a_dead_hook(tmp_path, relay_url, dead_url):
    tree = _tree(tmp_path, relay_url, enabled={OURS: True}, beat="2026-10-01T02:40:00Z",
                 bash_finish="2026-10-01T02:59:00Z")
    run = _run(tmp_path, relay_url, dead_url, tree["transcript"])
    assert run.stdout.splitlines()[-1] == (
        "  WARN the pruner hook has not run since 2026-10-01T02:40:00Z, and a Bash call finished at "
        "2026-10-01T02:59:00+00:00: the hook is not loaded (restart Claude Code or /reload-plugins)")
    # no record at all reads the same way
    (tmp_path / ".jev" / "pruner" / "decisions" / "last.json").unlink()
    run = _run(tmp_path, relay_url, dead_url, tree["transcript"])
    assert "  WARN the pruner hook has written no record, and a Bash call finished at 2026-10-01T02:59:00+00:00" in run.stdout


def test_a_down_relay_under_the_pruner_is_named(tmp_path, relay_url, dead_url):
    tree = _tree(tmp_path, dead_url, enabled={OURS: True}, beat="2026-10-01T02:59:30Z", bash_finish="2026-10-01T02:59:00Z")
    run = _run(tmp_path, dead_url, dead_url, tree["transcript"])
    assert "  WARN the our copy pruner sends to relay, which is down: outputs past the floor pass untrimmed" in run.stdout


def test_two_pruners_and_the_upstream_floor_are_warned(tmp_path, relay_url, dead_url):
    tree = _tree(tmp_path, relay_url, enabled={OURS: True, UPSTREAM: True}, beat="2026-10-01T02:59:30Z",
                 bash_finish="2026-10-01T02:59:00Z")
    run = _run(tmp_path, relay_url, dead_url, tree["transcript"])
    assert "  WARN both pruner plugins are enabled: each wraps every Bash call (enable one)" in run.stdout
    assert "  WARN the upstream pruner's floor is 10000 tokens: no inline Bash output reached 10,000" in run.stdout
    tree = _tree(tmp_path / "off", relay_url, enabled={OURS: False}, beat=None, bash_finish="2026-10-01T02:59:00Z")
    run = _run(tmp_path / "off", relay_url, dead_url, tree["transcript"])
    assert "  WARN no pruner plugin is enabled: no Bash output is trimmed" in run.stdout


def test_line_mode_prints_one_line(tmp_path, relay_url, dead_url):
    tree = _tree(tmp_path, relay_url, enabled={OURS: True}, beat="2026-10-01T02:59:30Z", bash_finish="2026-10-01T02:59:00Z")
    run = _run(tmp_path, relay_url, dead_url, tree["transcript"], "--line")
    assert run.returncode == 0 and run.stdout.count("\n") == 1 and run.stdout.startswith("jev: relay :")


def test_a_bad_endpoint_is_a_usage_error(tmp_path):
    run = subprocess.run([sys.executable, str(SCRIPT), "--endpoint", "relay"], capture_output=True, text=True, timeout=60)
    assert (run.returncode, run.stderr) == (64, "jev_liveness: --endpoint takes NAME=http://HOST:PORT\n")


def test_a_relay_on_other_code_is_named(tmp_path, relay_url, dead_url):
    """AF-AP-33: a 200 from the port is not the relay of this tree; the reported code hashes must match."""
    tree = _tree(tmp_path, relay_url, enabled={OURS: True}, beat="2026-10-01T02:59:30Z", bash_finish="2026-10-01T02:59:00Z")
    _Health.identity = {"relay_sha256": "0" * 64, "scrub_sha256": _sha("scripts/transcript_export.py")}
    run = _run(tmp_path, relay_url, dead_url, tree["transcript"])
    port = relay_url.rsplit(":", 1)[1]
    assert (f"  WARN the relay on :{port} reports relay_sha256 000000000000, and this tree's scripts/jev_relay.py is "
            f"{_sha('scripts/jev_relay.py')[:12]}: a stale or foreign relay (restart it: scripts/jev_relay_up.sh)") in run.stdout
    assert "scrub_sha256" not in run.stdout
    _Health.identity = {}  # a server with no identity at all: both hashes are named
    run = _run(tmp_path, relay_url, dead_url, tree["transcript"])
    assert run.stdout.count("a stale or foreign relay") == 2


def test_an_update_after_the_start_is_named_and_one_before_is_not(tmp_path, relay_url, dead_url):
    """An update reaches the running hook only at a restart (2026-10-01: 0.1.1 installed at 09:41Z ran the old code)."""
    tree = _tree(tmp_path, relay_url, enabled={OURS: True}, beat="2026-10-01T02:59:30Z", bash_finish="2026-10-01T02:59:00Z",
                 updated="2026-10-01T02:30:00Z")
    run = _run(tmp_path, relay_url, dead_url, tree["transcript"])
    assert ("  WARN the our copy pruner was installed or updated at 2026-10-01T02:30:00+00:00, after this Claude Code "
            "started at 2026-10-01T02:00:00+00:00: the running hook is the older code until a restart (a session resume "
            "restarts it; /reload-plugins does not run over a remote connection)") in run.stdout.splitlines()
    tree = _tree(tmp_path / "before", relay_url, enabled={OURS: True}, beat="2026-10-01T02:59:30Z",
                 bash_finish="2026-10-01T02:59:00Z", updated=STARTED)  # the same second is not after
    run = _run(tmp_path / "before", relay_url, dead_url, tree["transcript"])
    assert "WARN" not in run.stdout, run.stdout


def test_a_relative_record_folder_is_named_not_read(tmp_path, relay_url, dead_url):
    """The hook resolves a relative decisionsDir against Claude Code's launch directory (/home/user in the cloud
    session, 2026-10-01), so the probe names it instead of reading the repo's folder and calling the hook dead."""
    tree = _tree(tmp_path, relay_url, enabled={OURS: True}, beat="2026-10-01T02:40:00Z", bash_finish="2026-10-01T02:59:00Z",
                 decisions_dir=".jev/pruner/decisions")
    run = _run(tmp_path, relay_url, dead_url, tree["transcript"])
    warns = [line for line in run.stdout.splitlines() if "WARN" in line]
    assert warns == ["  WARN the our copy pruner's decisionsDir is relative (.jev/pruner/decisions): the hook resolves it "
                     "against Claude Code's launch directory, not the repo, so its records are not read here (set an "
                     "absolute path with claude plugin configure)"], warns
    assert "heartbeat" not in run.stdout
