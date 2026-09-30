"""scripts/jev_relay_up.sh (task #419, D-119): start the Jev relay at session start when it is not running.

Every case runs the real script with a key file built at run time and passes the relay `--no-default-sources` and
`--no-data`, so no real secret file is read and no data log is written; a relay a case starts is stopped by the pid its
/health reports.
"""
import json
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
UP = ROOT / "scripts" / "jev_relay_up.sh"
NO_PROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def health(port):
    try:
        with NO_PROXY.open("http://127.0.0.1:%d/health" % port, timeout=1) as r:
            return json.loads(r.read())
    except OSError:
        return None


@pytest.fixture
def env_file(tmp_path):
    p = tmp_path / "api.env"
    p.write_text("TYPESAFE_API_KEY=sk-codiv-%s\nTYPESAFE_BASE_URL=https://api.example.invalid\n" % os.urandom(20).hex())
    return p


@pytest.fixture
def port():
    return free_port()


@pytest.fixture(autouse=True)
def reap(tmp_path):
    """At teardown every process whose argv holds this case's state directory (a relay a failing case or a mutant
    started, in any phase of its start: the starter's forked shell, setsid, nohup or the relay) is stopped by its pid.
    A /health poll missed a relay that came up after its wait: the mutant that skips the start wait left one that bound
    a port its case had freed."""
    yield
    mark = str(tmp_path / "state").encode()
    for d in Path("/proc").iterdir():
        if not d.name.isdigit():
            continue
        try:
            argv = (d / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        if mark in argv:
            try:
                os.kill(int(d.name), signal.SIGTERM)
            except ProcessLookupError:
                pass


@pytest.fixture
def started():
    pids = []
    yield pids
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass


def run_up(tmp_path, port, env_file):
    args = ["bash", str(UP), "--port", str(port), "--env-file", str(env_file), "--off-file", str(tmp_path / "relay-off"),
            "--log", str(tmp_path / "relay.log"), "--",
            "--no-default-sources", "--no-data", "--state-dir", str(tmp_path / "state")]
    return subprocess.run(args, capture_output=True, text=True, timeout=60)


def test_starts_a_relay_that_answers_health_and_a_second_run_reuses_it(tmp_path, env_file, started, port):
    p = run_up(tmp_path, port, env_file)
    h = health(port)
    assert h is not None, (p.returncode, p.stdout, p.stderr)
    started.append(h["pid"])
    assert p.returncode == 0 and p.stdout.startswith("jev relay: started on 127.0.0.1:%d (pid %d," % (port, h["pid"])), p.stdout
    assert h["upstream_host"] == "api.example.invalid"          # the key file named on the command line, not the default
    q = run_up(tmp_path, port, env_file)
    assert q.returncode == 0 and q.stdout == "jev relay: already running on 127.0.0.1:%d (pid %d)\n" % (port, h["pid"]), q.stdout
    assert health(port)["pid"] == h["pid"]                       # no second relay


def test_the_off_file_starts_nothing(tmp_path, env_file, port):
    (tmp_path / "relay-off").write_text("")
    p = run_up(tmp_path, port, env_file)
    assert p.returncode == 0 and p.stdout.startswith("jev relay: off ("), p.stdout
    assert health(port) is None


def test_no_key_file_starts_nothing(tmp_path, port):
    p = run_up(tmp_path, port, tmp_path / "absent.env")
    assert p.returncode == 0 and p.stdout.startswith("jev relay: NOT started, no key file"), p.stdout
    assert health(port) is None


def test_a_port_held_by_something_else_is_never_reported_running(tmp_path, env_file):
    # A listener that is not a relay: "running" needs a /health answer, and the relay started beside it cannot bind.
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        port = s.getsockname()[1]
        p = run_up(tmp_path, port, env_file)
    assert p.returncode == 0 and p.stdout.startswith("jev relay: NOT started (no /health answer"), p.stdout
    assert "cannot be bound" in (tmp_path / "relay.log").read_text()


def test_a_relay_running_other_code_is_reported_and_left_running(tmp_path, env_file, started, port):
    # A relay started from a copy whose bytes differ, as an older build still running after an update: reported, never
    # stopped (the stop is by its pid, by hand).
    old = tmp_path / "old" / "scripts"
    old.mkdir(parents=True)
    for f in ("jev_relay.py", "transcript_export.py", "known_values_check.py"):
        (old / f).write_bytes((ROOT / "scripts" / f).read_bytes())
    with open(old / "jev_relay.py", "a") as fh:
        fh.write("# an older build\n")
    proc = subprocess.Popen([sys.executable, str(old / "jev_relay.py"), "serve", "--port", str(port), "--env-file",
                             str(env_file), "--no-default-sources", "--no-data"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    started.append(proc.pid)
    deadline = time.monotonic() + 15
    while health(port) is None and time.monotonic() < deadline:
        time.sleep(0.05)
    assert health(port)["pid"] == proc.pid
    p = run_up(tmp_path, port, env_file)
    assert p.returncode == 0 and p.stdout.startswith(
        "jev relay: already running on 127.0.0.1:%d (pid %d) with code other than scripts/jev_relay.py;" % (port, proc.pid)), p.stdout
    assert proc.poll() is None and health(port)["pid"] == proc.pid


def test_a_foreign_service_answering_health_is_never_a_relay(tmp_path, env_file):
    # Something else on the port answers /health with JSON that is no relay's (no upstream_host): never "already
    # running"; the relay started beside it cannot bind, and the line says so.
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            body = json.dumps({"ok": True, "status": "up"}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *a):
            return

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        p = run_up(tmp_path, srv.server_address[1], env_file)
    finally:
        srv.shutdown()
        srv.server_close()
    assert p.returncode == 0 and p.stdout.startswith("jev relay: NOT started (no /health answer"), p.stdout
    assert "cannot be bound" in (tmp_path / "relay.log").read_text()

@pytest.mark.parametrize("args", [["--port"], ["--port", "x1"], ["--bogus"]])
def test_a_usage_error_exits_64(tmp_path, args):
    # Scratch paths first, so a starter that misses the usage error (a mutant) never reaches the real key file, the
    # default log or the repository's off file: the mutant without the port check once started a relay with the real
    # key file's path, stopped only by the relay's own argument check.
    safe = ["--env-file", str(tmp_path / "absent.env"), "--off-file", str(tmp_path / "relay-off"),
            "--log", str(tmp_path / "relay.log")]
    p = subprocess.run(["bash", str(UP), *safe, *args], capture_output=True, text=True, timeout=30)
    assert p.returncode == 64 and p.stdout == "", (args, p.returncode, p.stdout, p.stderr)
