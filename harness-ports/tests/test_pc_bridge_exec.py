"""scripts/pc_bridge_exec.py unwraps the bridge envelope: remote stdout -> stdout, remote stderr
-> stderr, remote rc -> exit code; a non-JSON reply is retried and then exits 3; the token never
appears in argv. Runs against a local HTTP stub — no PC, no network."""
import http.server
import json
import os
import pathlib
import subprocess
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parents[2]
HELPER = ROOT / "scripts" / "pc_bridge_exec.py"
SEEN = []


class Stub(http.server.BaseHTTPRequestHandler):
    mode = "json"

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        SEEN.append((self.path, self.headers.get("X-Agent-Token"), body))
        if Stub.mode == "json":
            out = json.dumps({"rc": 3, "stdout": "hello from pc\n", "stderr": "warn line"}).encode()
        else:
            out = b"<html>gateway hiccup</html>"
        self.send_response(200)
        self.send_header("Content-Type", "application/json" if Stub.mode == "json" else "text/html")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *a):  # quiet
        pass


def _serve():
    srv = http.server.HTTPServer(("127.0.0.1", 0), Stub)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return srv


def _run(url, cmd):
    env = dict(os.environ, PC_BRIDGE_URL=url, PC_BRIDGE_TOKEN="tok-secret-123")
    return subprocess.run([sys.executable, str(HELPER), cmd], capture_output=True, text=True, env=env, timeout=60)


def main():
    srv = _serve()
    url = f"http://127.0.0.1:{srv.server_port}"
    checks = 0
    # positive: envelope unwrapped, rc propagated, token in the header not in argv
    Stub.mode = "json"
    r = _run(url, "echo hi")
    assert r.stdout == "hello from pc\n", r.stdout
    assert "warn line" in r.stderr, r.stderr
    assert r.returncode == 3, r.returncode
    assert SEEN[-1][0] == "/exec" and SEEN[-1][1] == "tok-secret-123" and SEEN[-1][2] == {"cmd": "echo hi"}
    checks += 4
    # negative control: a non-JSON reply is retried three times, then exit 3 with no stdout
    Stub.mode = "html"
    before = len(SEEN)
    r = _run(url, "echo hi")
    assert r.returncode == 3 and r.stdout == "", (r.returncode, r.stdout)
    assert len(SEEN) - before == 3, len(SEEN) - before
    assert "no JSON envelope" in r.stderr, r.stderr
    checks += 3
    # negative control: missing env -> exit 2, nothing sent
    env = {k: v for k, v in os.environ.items() if not k.startswith("PC_BRIDGE_")}
    r = subprocess.run([sys.executable, str(HELPER), "echo"], capture_output=True, text=True, env=env, timeout=60)
    assert r.returncode == 2 and "not set" in r.stderr
    checks += 1
    srv.shutdown()
    print(f"test_pc_bridge_exec: {checks} checks passed")


if __name__ == "__main__":
    main()
