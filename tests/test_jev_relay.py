"""scripts/jev_relay.py (task #373, D-109): the scrubbing relay between the output-pruner plugin and codiv.ai.

Every case drives the real entry (`python3 scripts/jev_relay.py serve`) as a subprocess against a fake upstream on the
loopback that records every byte it receives, so "nothing leaves" is measured at the upstream, not inferred. Every secret
is a fake built at run time; the relay knows only the test's own key file (`--no-default-sources`), never a real one.
"""
import hashlib
import json
import os
import random
import socket
import stat
import string
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RELAY = ROOT / "scripts" / "jev_relay.py"
sys.path.insert(0, str(ROOT / "scripts"))
import transcript_export as te  # noqa: E402

RND = random.Random()
ALNUM = string.ascii_letters + string.digits
NO_PROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fake(n, alphabet=ALNUM):
    return "".join(RND.choice(alphabet) for _ in range(n))


class Upstream:
    """A fake /v1/systemone on the loopback: records (headers, body, arrival time) and answers `reply`."""

    def __init__(self, status=200, body=None):
        self.status = status
        self.body = body if body is not None else json.dumps({"model": "openjev-latest",
                                                              "answers": {"q1": {"noul": 0.8}}}).encode()
        self.seen = []
        up = self

        class H(BaseHTTPRequestHandler):
            def do_POST(self):
                data = self.rfile.read(int(self.headers["Content-Length"]))
                up.seen.append({"path": self.path, "headers": dict(self.headers), "body": data,
                                "t": time.monotonic()})
                self.send_response(up.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(up.body)))
                self.end_headers()
                self.wfile.write(up.body)

            def log_message(self, *a):
                return

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def upstream():
    up = Upstream()
    yield up
    up.close()


@pytest.fixture
def key():
    return "sk-codiv-" + fake(40)


@pytest.fixture
def env_file(tmp_path, upstream, key):
    p = tmp_path / "api.env"
    p.write_text("TYPESAFE_API_KEY=%s\nTYPESAFE_BASE_URL=http://127.0.0.1:%d\n" % (key, upstream.port))
    return p


class Relay:
    def __init__(self, tmp_path, env_file, *extra, min_gap="0"):
        self.port = free_port()
        self.state_dir = tmp_path / "state"
        self.proc = subprocess.Popen(
            [sys.executable, str(RELAY), "serve", "--port", str(self.port), "--env-file", str(env_file),
             "--state-dir", str(self.state_dir), "--min-gap", min_gap, "--no-default-sources", *extra],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if self.proc.poll() is not None:
                break
            try:
                h = self.health()
            except OSError:
                time.sleep(0.05)
                continue
            # AF-AP-33: a relay left on this port by another run also answers /health; only our pid is ours
            assert h["pid"] == self.proc.pid, "port %d answered from pid %s, not %s" % (self.port, h["pid"], self.proc.pid)
            return
        self.stop()
        raise AssertionError("the relay did not start: rc=%s %s" % (self.proc.returncode, self.proc.stderr.read()))

    def url(self, path):
        return "http://127.0.0.1:%d%s" % (self.port, path)

    def health(self):
        with NO_PROXY.open(self.url("/health"), timeout=2) as r:
            return json.loads(r.read())

    def post(self, body, auth="Bearer relay-placeholder", raw=None):
        data = raw if raw is not None else json.dumps(body).encode()
        req = urllib.request.Request(self.url("/v1/systemone"), data=data, method="POST",
                                     headers={"Content-Type": "application/json", "Authorization": auth})
        try:
            with NO_PROXY.open(req, timeout=30) as r:
                return r.status, r.read()
        except urllib.error.HTTPError as e:
            return e.code, e.read()

    def stop(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()


@pytest.fixture
def relay(tmp_path, env_file):
    r = Relay(tmp_path, env_file)
    yield r
    r.stop()


def body_with(state, instructions="Does this chunk hold an error line?"):
    return {"model": "openjev-latest", "state": state,
            "questions": {"q1": {"type": "noul", "instructions": instructions}}}


def planted():
    """Fakes of the shapes the scrub names, each built at run time."""
    return {"sk": "sk-" + fake(30), "gh": "ghp_" + fake(36), "aiza": "AIza" + fake(35),
            "slack": "xoxb-" + fake(24), "bearer": fake(32), "pass": fake(16),
            "bridge": "https://%s.trycloudflare.com/x" % fake(12, string.ascii_lowercase)}


def test_planted_secrets_never_reach_the_upstream(relay, upstream):
    p = planted()
    state = {"command": "cat build.log", "history": [
        "export OPENAI_KEY=%s" % p["sk"], {"tool_result": "token %s and %s" % (p["gh"], p["aiza"])}],
        "chunks": [{"id": "q1", "text": "Authorization: Bearer %s\nDB_PASS=%s\n%s\n%s" % (
            p["bearer"], p["pass"], p["slack"], p["bridge"])}]}
    status, reply = relay.post(body_with(state, "Keep %s?" % p["sk"]))
    assert status == 200, reply
    assert json.loads(reply)["answers"]["q1"]["noul"] == 0.8          # the upstream's answer came back
    assert len(upstream.seen) == 1
    sent = upstream.seen[0]["body"].decode()
    for name, value in p.items():
        assert value not in sent, name
    assert "<redacted>" in sent


def test_the_key_file_supplies_the_key_and_the_callers_header_is_dropped(relay, upstream, key):
    status, _ = relay.post(body_with("plain text"), auth="Bearer relay-placeholder")
    assert status == 200
    headers = upstream.seen[0]["headers"]
    assert headers["Authorization"] == "Bearer " + key
    assert "relay-placeholder" not in json.dumps(headers)
    assert upstream.seen[0]["path"] == "/v1/systemone"


def test_the_value_gate_refuses_a_known_value_the_shapes_miss(tmp_path, env_file, upstream):
    value = fake(30, string.ascii_lowercase)
    text = "the build printed %s near the end" % value
    assert te.scrub_payload(text) == text                   # no shape rule takes it: only the value gate can
    extra = tmp_path / "extra.env"
    extra.write_text("SOME_SECRET=%s\n" % value)
    r = Relay(tmp_path, env_file, "--value-file", str(extra))
    try:
        status, reply = r.post(body_with({"chunks": [{"id": "q1", "text": text}]}))
        assert status == 422 and b"value gate" in reply, reply
        assert value.encode() not in reply
        assert upstream.seen == []
        status, _ = r.post(body_with({"chunks": [{"id": "q1", "text": "the build printed nothing"}]}))
        assert status == 200 and len(upstream.seen) == 1      # the control: a clean body passes the same relay
    finally:
        r.stop()


def test_an_object_key_holding_a_secret_shape_is_refused(relay, upstream):
    body = {"model": "openjev-latest", "state": "x",
            "questions": {"sk-" + fake(30): {"type": "noul", "instructions": "i"}}}
    status, reply = relay.post(body)
    assert status == 422 and b"object key" in reply, reply
    assert upstream.seen == []


def test_only_the_allowed_model_is_sent(relay, upstream):
    status, reply = relay.post(dict(body_with("x"), model="jev-latest"))
    assert status == 400 and b"model" in reply
    assert upstream.seen == []
    body = body_with("x")
    del body["model"]
    body["url"] = "http://elsewhere.invalid/"                   # a key the relay never honors
    status, _ = relay.post(body)
    assert status == 200
    sent = json.loads(upstream.seen[0]["body"])
    assert sent["model"] == "openjev-latest" and set(sent) == {"model", "state", "questions"}


@pytest.mark.parametrize("raw,reason", [
    (b"not json", b"not JSON"),
    (b"[1, 2]", b"not a JSON object"),
    (json.dumps({"state": 3, "questions": {"q1": {}}}).encode(), b"state must be"),
    (json.dumps({"state": "x", "questions": {}}).encode(), b"questions must be"),
    (json.dumps({"state": "x", "questions": {"q1": "text"}}).encode(), b"questions must be"),
])
def test_a_malformed_body_is_refused(relay, upstream, raw, reason):
    status, reply = relay.post(None, raw=raw)
    assert status == 400 and reason in reply, reply
    assert upstream.seen == []


def test_a_body_over_the_cap_is_refused_unread(relay, upstream):
    # Only the headers are sent: the relay answers from the Content-Length alone, before any body byte (a client still
    # writing a large body would see its pipe closed, which the plugin's fetch treats as a failed call).
    with socket.create_connection(("127.0.0.1", relay.port), timeout=10) as s:
        s.sendall(b"POST /v1/systemone HTTP/1.1\r\nHost: 127.0.0.1\r\nContent-Type: application/json\r\n"
                  b"Content-Length: %d\r\n\r\n" % (4 * 1024 * 1024 + 1))
        reply = b""
        while True:                     # the reply can come in several segments; the server closes after it (HTTP/1.0)
            chunk = s.recv(65536)
            if not chunk:
                break
            reply += chunk
    assert reply.startswith(b"HTTP/1.0 413") or reply.startswith(b"HTTP/1.1 413"), reply[:80]
    assert b"over" in reply
    assert upstream.seen == []
    assert relay.health()["counts"]["refused"] == 1


def test_an_upstream_reply_never_carries_the_key(tmp_path, key):
    up = Upstream(status=401, body=json.dumps({"error": "invalid key %s" % key}).encode())
    env = tmp_path / "api.env"
    env.write_text("TYPESAFE_API_KEY=%s\nTYPESAFE_BASE_URL=http://127.0.0.1:%d\n" % (key, up.port))
    r = Relay(tmp_path, env)
    try:
        status, reply = r.post(body_with("x"))
        assert status == 401
        assert key.encode() not in reply and b"<redacted>" in reply
    finally:
        r.stop()
        up.close()


def test_an_unreachable_upstream_answers_502_and_the_relay_keeps_serving(tmp_path, key):
    env = tmp_path / "api.env"
    env.write_text("TYPESAFE_API_KEY=%s\nTYPESAFE_BASE_URL=http://127.0.0.1:%d\n" % (key, free_port()))
    r = Relay(tmp_path, env)
    try:
        status, reply = r.post(body_with("x"))
        assert status == 502 and b"unreachable" in reply
        assert r.health()["counts"]["upstream_error"] == 1
    finally:
        r.stop()


def test_the_data_log_keeps_the_scrubbed_request_and_the_answer(relay, upstream, key):
    p = planted()
    state = {"chunks": [{"id": "q1", "text": "error: %s failed" % p["sk"]}]}
    status, _ = relay.post(body_with(state))
    assert status == 200
    days = list(relay.state_dir.glob("*.jsonl"))
    assert len(days) == 1
    rows = [json.loads(line) for line in days[0].read_text().splitlines()]
    assert len(rows) == 1
    row = rows[0]
    assert row["status"] == 200 and row["answer"]["answers"]["q1"]["noul"] == 0.8
    assert row["questions"] == {"q1": {"type": "noul", "instructions": "Does this chunk hold an error line?"}}
    assert row["scrub_sha256"] == hashlib.sha256((ROOT / "scripts" / "transcript_export.py").read_bytes()).hexdigest()
    state_file = relay.state_dir / "states" / (row["state_sha256"] + ".json")
    assert hashlib.sha256(state_file.read_bytes()).hexdigest() == row["state_sha256"]
    assert state_file.read_bytes() in upstream.seen[0]["body"]          # the logged state is the state that was sent
    everything = b"".join(f.read_bytes() for f in relay.state_dir.rglob("*") if f.is_file())
    assert p["sk"].encode() not in everything and key.encode() not in everything
    assert stat.S_IMODE(os.stat(relay.state_dir).st_mode) == 0o700
    files = [f for f in relay.state_dir.rglob("*") if f.is_file()]
    assert len(files) == 2, files                         # the day file and the state file: the mode check is not empty
    for f in files:
        assert stat.S_IMODE(os.stat(f).st_mode) == 0o600, f


def test_no_data_keeps_no_log(tmp_path, env_file, upstream):
    r = Relay(tmp_path, env_file, "--no-data")
    try:
        assert r.post(body_with("x"))[0] == 200
        assert not r.state_dir.exists()
    finally:
        r.stop()


def test_upstream_sends_start_at_least_min_gap_apart(tmp_path, env_file, upstream):
    r = Relay(tmp_path, env_file, min_gap="0.4")
    try:
        results = []
        threads = [threading.Thread(target=lambda: results.append(r.post(body_with("x"))[0])) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert results == [200, 200, 200]
        times = sorted(s["t"] for s in upstream.seen)
        assert all(b - a >= 0.38 for a, b in zip(times, times[1:])), times
    finally:
        r.stop()


def test_health_names_the_upstream_and_the_scrub(relay):
    h = relay.health()
    assert h["ok"] is True and h["upstream_host"] == "127.0.0.1" and h["models"] == ["openjev-latest"]
    assert h["scrub_sha256"] == hashlib.sha256((ROOT / "scripts" / "transcript_export.py").read_bytes()).hexdigest()
    assert h["relay_sha256"] == hashlib.sha256(RELAY.read_bytes()).hexdigest()


def test_a_taken_port_is_refused(relay, env_file, tmp_path):
    p = subprocess.run([sys.executable, str(RELAY), "serve", "--port", str(relay.port), "--env-file", str(env_file),
                        "--state-dir", str(tmp_path / "s2"), "--no-default-sources"],
                       capture_output=True, text=True, timeout=30)
    assert p.returncode == 75 and "cannot be bound" in p.stderr


@pytest.mark.parametrize("content,missing", [
    ("TYPESAFE_BASE_URL=https://api.example.invalid\n", "TYPESAFE_API_KEY"),
    ("TYPESAFE_API_KEY=%s\n", "TYPESAFE_BASE_URL"),
])
def test_a_key_file_without_its_names_stops_the_relay(tmp_path, content, missing, key):
    env = tmp_path / "api.env"
    env.write_text(content % key if "%s" in content else content)
    p = subprocess.run([sys.executable, str(RELAY), "serve", "--port", str(free_port()), "--env-file", str(env),
                        "--no-default-sources"], capture_output=True, text=True, timeout=30)
    assert p.returncode == 2 and missing in p.stderr
    assert key not in p.stderr and key not in p.stdout


def test_a_missing_key_file_stops_the_relay(tmp_path):
    p = subprocess.run([sys.executable, str(RELAY), "serve", "--port", str(free_port()), "--env-file",
                        str(tmp_path / "absent.env"), "--no-default-sources"], capture_output=True, text=True, timeout=30)
    assert p.returncode == 2 and "cannot be used" in p.stderr


@pytest.mark.parametrize("gap", ["nan", "inf", "-1"])
def test_a_gap_that_is_not_a_finite_non_negative_number_is_refused(tmp_path, gap, key):
    # `nan < 0` is False, so a bare `< 0` guard let `--min-gap nan` through, and max(now, last + nan) is `now`: no gap.
    env = tmp_path / "api.env"
    env.write_text("TYPESAFE_API_KEY=%s\nTYPESAFE_BASE_URL=https://api.example.invalid\n" % key)
    p = subprocess.run([sys.executable, str(RELAY), "serve", "--port", str(free_port()), "--env-file", str(env),
                        "--min-gap", gap, "--no-default-sources"], capture_output=True, text=True, timeout=30)
    assert p.returncode == 64 and "bad --port or --min-gap" in p.stderr, (gap, p.returncode, p.stderr)


def test_a_value_source_rewritten_after_start_joins_the_gate_before_the_next_send(tmp_path, env_file, upstream):
    """Task #418: the relay loads its known values at start, and a source written later (the owner's next bridge banner
    in .pc-bridge.env) must reach the gate before the next send; a value known before the rewrite stays known."""
    old, new = fake(30, string.ascii_lowercase), fake(30, string.ascii_lowercase)
    text = "the banner said %s near the end"
    assert te.scrub_payload(text % new) == text % new          # no shape rule takes it: only the value gate can
    extra = tmp_path / "extra.env"
    extra.write_text("PC_BRIDGE_TOKEN=%s\n" % old)
    r = Relay(tmp_path, env_file, "--value-file", str(extra))
    try:
        status, _ = r.post(body_with({"chunks": [{"id": "q1", "text": text % new}]}))
        assert status == 200 and len(upstream.seen) == 1       # before the rewrite the new value is unknown, so it went
        extra.write_text("PC_BRIDGE_TOKEN=%s\n" % new)           # rewritten in place: same inode, same size
        status, reply = r.post(body_with({"chunks": [{"id": "q1", "text": text % new}]}))
        assert status == 422 and b"value gate" in reply, reply
        assert new.encode() not in reply and len(upstream.seen) == 1
        status, reply = r.post(body_with({"chunks": [{"id": "q1", "text": text % old}]}))
        assert status == 422, reply                              # the reload adds values, it never forgets one
        status, _ = r.post(body_with({"chunks": [{"id": "q1", "text": "the banner said nothing"}]}))
        assert status == 200 and len(upstream.seen) == 2         # the control: a clean body still passes
        assert r.health()["counts"]["reloads"] == 1
    finally:
        r.stop()


def test_a_value_source_that_turns_unreadable_after_start_fails_closed(tmp_path, env_file, upstream):
    """A changed source the gate cannot read (here a FIFO, which a plain read would block on) refuses every request with
    503 until it reads again: the gate never falls back to the values it had."""
    extra = tmp_path / "extra.env"
    extra.write_text("PC_BRIDGE_TOKEN=%s\n" % fake(30, string.ascii_lowercase))
    r = Relay(tmp_path, env_file, "--value-file", str(extra))
    try:
        extra.unlink()
        os.mkfifo(extra)
        status, reply = r.post(body_with("plain text"))
        assert status == 503 and b"value gate" in reply, reply
        assert upstream.seen == []
        extra.unlink()
        extra.write_text("PC_BRIDGE_TOKEN=%s\n" % fake(30, string.ascii_lowercase))
        status, _ = r.post(body_with("plain text"))
        assert status == 200 and len(upstream.seen) == 1          # readable again: the relay sends again
    finally:
        r.stop()
