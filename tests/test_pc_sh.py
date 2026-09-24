"""scripts/pc.sh against a fake local bridge: the owner's shell-hook `bind: warning` lines are dropped from the remote
stderr, and nothing else is. pc.sh sources the repo's .pc-bridge.env when it exists, which would point it at the LIVE
bridge, so every test runs a copy of pc.sh in a temp tree that has no .pc-bridge.env."""
import http.server
import json
import os
import shutil
import subprocess
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WARN = "/home/rocco/.local/share/tirith/shell/lib/bash-hook.bash: line %d: bind: warning: line editing not enabled"


@pytest.fixture
def bridge(tmp_path):
    """A fake bridge answering every POST /exec with the envelope the test sets; yields (run, set_envelope)."""
    envelope, seen = {}, []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):                      # like the bridge: only POST /exec with the token runs a command
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            seen.append((self.path, self.headers.get("X-Agent-Token"), req))
            ok = self.path == "/exec" and self.headers.get("X-Agent-Token") == "fake-token-not-real"
            body = json.dumps(envelope if ok else {"error": "forbidden"}).encode()
            self.send_response(200 if ok else 403)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    (tmp_path / "scripts").mkdir()
    shutil.copy(ROOT / "scripts" / "pc.sh", tmp_path / "scripts" / "pc.sh")
    assert not (tmp_path / ".pc-bridge.env").exists()
    env = {k: v for k, v in os.environ.items() if k.lower() not in ("http_proxy", "https_proxy", "all_proxy")}
    env.update(PC_BRIDGE_URL="http://127.0.0.1:%d" % server.server_address[1], PC_BRIDGE_TOKEN="fake-token-not-real",
               NO_PROXY="127.0.0.1", no_proxy="127.0.0.1")

    def run(env_overrides=None):
        return subprocess.run(["bash", str(tmp_path / "scripts" / "pc.sh"), "true"], capture_output=True, text=True,
                              env={**env, **(env_overrides or {})}, timeout=60)

    yield run, envelope.update, seen
    server.shutdown()


def test_the_hook_warning_lines_are_dropped_and_the_real_stderr_kept(bridge):
    run, set_envelope, seen = bridge
    set_envelope({"stdout": "data-without-newline", "rc": 0,
                  "stderr": "%s\n%s\nreal error line\n%s\n" % (WARN % 121, WARN % 122, WARN % 163)})
    r = run()
    assert seen == [("/exec", "fake-token-not-real", {"cmd": "true"})]
    assert r.returncode == 0, r
    assert r.stdout == "data-without-newline"
    assert r.stderr == "real error line\n"


def test_a_wrong_token_is_refused_by_the_stand_in(bridge):
    """Negative control for the stand-in itself: it answers only the request the real bridge runs."""
    run, set_envelope, _seen = bridge
    set_envelope({"stdout": "must not print", "stderr": "", "rc": 0})
    r = run({"PC_BRIDGE_TOKEN": "another-fake-token"})
    assert r.returncode == 4 and r.stdout == "" and "bridge error: forbidden" in r.stderr, r


def test_only_exact_whole_lines_are_dropped(bridge):
    run, set_envelope, _seen = bridge
    kept = ("bind: warning: something else entirely\n"
            "prefix text " + (WARN % 5) + "\n"
            "bind: warning: line editing not enabled, and more\n")
    set_envelope({"stdout": "", "rc": 0, "stderr": "bind: warning: line editing not enabled\n" + kept})
    r = run()
    assert r.stderr == kept


def test_the_remote_rc_is_the_exit_code(bridge):
    run, set_envelope, _seen = bridge
    set_envelope({"stdout": "x", "stderr": WARN % 1 + "\n", "rc": 5})
    r = run()
    assert (r.returncode, r.stdout, r.stderr) == (5, "x", "")
