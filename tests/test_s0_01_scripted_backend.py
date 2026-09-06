"""proofs/S0-01/tools/scripted_backend.py — the golden's deterministic upstream (stdlib server).

Spawns the real server under sys.executable on an ephemeral port, then proves: bearer required (401
exact body), models list, non-stream and stream completions byte-identical across repeated calls,
the slow model's chunking, unknown model / bad body errors, request recording with the bearer
reduced to a fingerprint, and that the token never appears in argv.

V-c F3: header keys lowercase in records.
V-c F10: credential-bearing headers dropped; fail-closed on leak.
V-c F11: Transfer-Encoding: chunked rejected with 411.
V-c F12: Content-Length validated as int in [0, 1_048_576].
V-c F13: --record-dir as file refused at startup.
V-c F14: received_at microsecond format regex; t_mono_ns strictly increasing.
V-c F15: 0400 token file mode accepted.
V-d F19: healthz record count pinned; /healthz not recorded.
V-d F21: missing token file yields named refusal, exit 2.
R5-D5-F1: framing gate (TE/CL) before any route dispatch incl. /healthz.
R5-D5-F2: close_connection anti-smuggling proven via 1-response assertions.
R5-D5-F3: credential screen covers header NAMES (not just values).
R5-D5-F4: duplicate Content-Length rejected (RFC 9112 s6.3).
R5-D5-F5: GET with Content-Length: 0 accepted and recorded.
R5-D5-F6: percent-encoded token in query caught via unquote(path).
R5-D5-F7: --slow-delay type= callable; -inf/-nan/-1e-9 get named refusal.
R5-D5-F10: exact assertions on named refusals and record values.
"""
from __future__ import annotations

import hashlib
import http.client
import json
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "proofs" / "S0-01" / "tools" / "scripted_backend.py"
TOKEN = "s0-01-upstream-token-0123456789abcdef"

# V-c F14: the EXACT received_at format: YYYY-MM-DDTHH:MM:SS.ffffffZ (microsecond precision)
_RECEIVED_AT_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z$"
)


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def backend(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("backend")
    token_file = tmp / "upstream.env"
    token_file.write_text(f"UPSTREAM_TOKEN={TOKEN}\n")
    token_file.chmod(0o600)
    port = _free_port()
    argv = [sys.executable, str(SERVER), "--port", str(port), "--token-file", str(token_file),
            "--record-dir", str(tmp / "rec"), "--slow-delay", "0.05", "--pidfile", str(tmp / "pid")]
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
            conn.request("GET", "/healthz")
            resp = conn.getresponse()
            resp.read()
            conn.close()
            if resp.status == 200:
                break
        except OSError:
            time.sleep(0.05)
    yield {"port": port, "proc": proc, "argv": argv, "rec": tmp / "rec", "pidfile": tmp / "pid"}
    proc.terminate()
    proc.wait(timeout=10)


def _call(port, method, path, body=None, token=TOKEN, stream=False, extra_headers=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=15)
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)
    conn.request(method, path, body=json.dumps(body) if body is not None else None, headers=headers)
    resp = conn.getresponse()
    data = resp.read()
    conn.close()
    return resp.status, data


def _raw_request(port, raw_bytes):
    """Send raw bytes over a socket and return the response bytes."""
    s = socket.socket()
    s.settimeout(5)
    s.connect(("127.0.0.1", port))
    s.sendall(raw_bytes)
    chunks = []
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
    except socket.timeout:
        pass
    s.close()
    return b"".join(chunks)


def test_bearer_required_exact_401(backend):
    p = backend["port"]
    for tok in (None, "wrong-token"):
        status, data = _call(p, "GET", "/v1/models", token=tok)
        assert status == 401
        assert json.loads(data) == {"error": {"code": "unauthorized", "message": "missing or invalid upstream bearer", "type": "authentication_error"}}
    status, data = _call(p, "POST", "/v1/chat/completions", {"model": "s0-01-pong", "messages": []}, token=None)
    assert status == 401


def test_models_list(backend):
    status, data = _call(backend["port"], "GET", "/v1/models")
    assert status == 200
    assert [m["id"] for m in json.loads(data)["data"]] == ["s0-01-pong", "s0-01-slow"]


def test_non_stream_completion_is_pong_and_byte_identical(backend):
    body = {"model": "s0-01-pong", "messages": [{"role": "user", "content": "Reply with exactly the single word: pong"}]}
    a = _call(backend["port"], "POST", "/v1/chat/completions", body)
    b = _call(backend["port"], "POST", "/v1/chat/completions", body)
    assert a == b and a[0] == 200
    obj = json.loads(a[1])
    assert obj["choices"][0]["message"] == {"role": "assistant", "content": "pong"}
    assert obj["choices"][0]["finish_reason"] == "stop" and "tool_calls" not in obj["choices"][0]["message"]
    assert obj["usage"] == {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2}


def test_stream_completion_frames_are_deterministic(backend):
    body = {"model": "s0-01-pong", "stream": True, "messages": [{"role": "user", "content": "x"}]}
    a = _call(backend["port"], "POST", "/v1/chat/completions", body)
    b = _call(backend["port"], "POST", "/v1/chat/completions", body)
    assert a == b and a[0] == 200
    frames = [ln for ln in a[1].decode().split("\n\n") if ln.startswith("data: ")]
    assert frames[-1] == "data: [DONE]"
    payloads = [json.loads(f[6:]) for f in frames[:-1]]
    assert [c["choices"][0]["delta"].get("content") for c in payloads] == ["", "pong", None]
    assert payloads[-1]["choices"][0]["finish_reason"] == "stop" and "usage" in payloads[-1]
    assert all(c["id"] == "chatcmpl-s0-01" and c["created"] == 1788566400 for c in payloads)


def test_slow_model_streams_in_pieces_with_a_delay(backend):
    body = {"model": "s0-01-slow", "stream": True, "messages": [{"role": "user", "content": "x"}]}
    t0 = time.time()
    status, data = _call(backend["port"], "POST", "/v1/chat/completions", body)
    elapsed = time.time() - t0
    assert status == 200 and elapsed >= 0.05 * 3 * 0.9
    payloads = [json.loads(f[6:]) for f in data.decode().split("\n\n") if f.startswith("data: ") and f != "data: [DONE]"]
    assert "".join(c["choices"][0]["delta"].get("content") or "" for c in payloads) == "pong"
    assert len(payloads) == 5  # role + po + n + g + finish


def test_unknown_model_and_bad_body_are_exact_errors(backend):
    status, data = _call(backend["port"], "POST", "/v1/chat/completions", {"model": "gpt-9", "messages": []})
    assert status == 404 and json.loads(data)["error"]["code"] == "model_not_found"
    status, data = _call(backend["port"], "POST", "/v1/chat/completions", {"model": "s0-01-pong"})
    assert status == 400 and json.loads(data)["error"]["message"] == "messages: Expected array"


def test_requests_are_recorded_with_fingerprint_and_token_absent_from_argv(backend):
    # F8/F18: self-contained -- issue own POST before reading records
    _call(backend["port"], "POST", "/v1/chat/completions",
          {"model": "s0-01-pong", "messages": [{"role": "user", "content": "x"}]})
    recs = sorted(backend["rec"].glob("*.json"))
    assert recs, "no request records written"
    last = json.loads(recs[-1].read_text())
    assert last["method"] == "POST" and last["path"] == "/v1/chat/completions"
    # Authorization header dropped entirely from stored headers
    assert not any(k.lower() == "authorization" for k in last["headers"])
    # V-c F3: all header keys are lowercase
    assert all(k == k.lower() for k in last["headers"]), \
        f"header keys must be lowercase, got {list(last['headers'].keys())}"
    # authorization_fingerprint is the full sha256 of the presented token
    expected_fp = hashlib.sha256(TOKEN.encode()).hexdigest()
    assert last["authorization_fingerprint"] == expected_fp
    # V-c F14: received_at matches the exact microsecond format
    assert _RECEIVED_AT_RE.match(last["received_at"]), \
        f"received_at format wrong: {last['received_at']!r}"
    assert isinstance(last["t_mono_ns"], int) and last["t_mono_ns"] > 0
    # L13/L6: exact remote_addr on POST records
    assert last["remote_addr"] == "127.0.0.1"
    # TOKEN never appears in argv
    assert all(TOKEN not in a for a in backend["argv"])
    assert int(backend["pidfile"].read_text()) == backend["proc"].pid


def test_received_at_microsecond_format_kills_truncation_mutant(backend):
    """V-c F14: the mutant that truncates received_at to '%Y-%m-%dT%H:%MZ' must fail."""
    # Make two requests; both must have full microsecond timestamps
    _call(backend["port"], "GET", "/v1/models")
    recs = sorted(backend["rec"].glob("*.json"))
    last = json.loads(recs[-1].read_text())
    assert _RECEIVED_AT_RE.match(last["received_at"]), \
        f"received_at {last['received_at']!r} does not match YYYY-MM-DDTHH:MM:SS.ffffffZ"


def test_t_mono_ns_strictly_increasing_across_requests(backend):
    """V-c F14: the mutant that hardcodes t_mono_ns to 1 must fail."""
    _call(backend["port"], "GET", "/v1/models")
    recs_a = sorted(backend["rec"].glob("*.json"))
    mono_a = json.loads(recs_a[-1].read_text())["t_mono_ns"]
    _call(backend["port"], "GET", "/v1/models")
    recs_b = sorted(backend["rec"].glob("*.json"))
    mono_b = json.loads(recs_b[-1].read_text())["t_mono_ns"]
    assert isinstance(mono_a, int) and isinstance(mono_b, int)
    assert mono_b > mono_a, f"t_mono_ns not strictly increasing: {mono_a} >= {mono_b}"


# -- new safeguard tests ---------------------------------------------------

def test_nonempty_record_dir_refuses_without_flag(tmp_path):
    """Negative control: non-empty record dir without --allow-existing-records -> exit 2."""
    tf = tmp_path / "token.env"
    tf.write_text(f"UPSTREAM_TOKEN={TOKEN}\n")
    tf.chmod(0o600)
    rec = tmp_path / "rec"
    rec.mkdir()
    (rec / "old.json").write_text("{}\n")
    proc = subprocess.run(
        [sys.executable, str(SERVER), "--port", str(_free_port()),
         "--token-file", str(tf), "--record-dir", str(rec)],
        capture_output=True, text=True, timeout=10)
    assert proc.returncode == 2
    expected_msg = (f"scripted_backend: --record-dir {rec} is non-empty; "
                    f"pass --allow-existing-records to override\n")
    assert proc.stderr == expected_msg


def test_allow_existing_records_flag_overrides(tmp_path):
    """Positive control: --allow-existing-records lets the server start despite non-empty dir."""
    tf = tmp_path / "token.env"
    tf.write_text(f"UPSTREAM_TOKEN={TOKEN}\n")
    tf.chmod(0o600)
    rec = tmp_path / "rec"
    rec.mkdir()
    (rec / "old.json").write_text("{}\n")
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVER), "--port", str(port),
         "--token-file", str(tf), "--record-dir", str(rec),
         "--allow-existing-records", "--slow-delay", "0.05"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    started = False
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
            conn.request("GET", "/healthz")
            resp = conn.getresponse()
            resp.read()
            conn.close()
            if resp.status == 200:
                started = True
                break
        except OSError:
            time.sleep(0.05)
    proc.terminate()
    proc.wait(timeout=10)
    assert started, "server should start with --allow-existing-records"


def test_healthz_unauthenticated_and_not_recorded(backend):
    """V-d F19: GET /healthz returns 200, reports exact record count, and is NOT recorded."""
    # Snapshot current record count
    count_before = len(list(backend["rec"].glob("*.json")))
    status, data = _call(backend["port"], "GET", "/healthz", token=None)
    assert status == 200
    obj = json.loads(data)
    assert obj["ok"] is True
    assert obj["models"] == ["s0-01-pong", "s0-01-slow"]
    assert isinstance(obj["records"], int)
    # The healthz record count must equal the actual file count before the healthz call
    assert obj["records"] == count_before, \
        f"healthz reports {obj['records']} but {count_before} record files exist"
    # Healthz must NOT create a new record
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before, \
        f"/healthz created a record: {count_after} != {count_before}"


def test_record_null_fingerprint_when_no_bearer(backend):
    """A request without Bearer gets authorization_fingerprint: null and no auth header stored."""
    _call(backend["port"], "GET", "/v1/models", token=None)
    recs = sorted(backend["rec"].glob("*.json"))
    last = json.loads(recs[-1].read_text())
    assert last["authorization_fingerprint"] is None
    assert not any(k.lower() == "authorization" for k in last["headers"])


def test_record_dir_as_file_refuses_startup(tmp_path):
    """V-c F13: --record-dir pointing at a regular file must refuse (exit 2)."""
    tf = tmp_path / "token.env"
    tf.write_text(f"UPSTREAM_TOKEN={TOKEN}\n")
    tf.chmod(0o600)
    recfile = tmp_path / "rec"
    recfile.write_text("not a directory\n")
    proc = subprocess.run(
        [sys.executable, str(SERVER), "--port", str(_free_port()),
         "--token-file", str(tf), "--record-dir", str(recfile)],
        capture_output=True, text=True, timeout=10)
    assert proc.returncode == 2
    expected_msg = (f"scripted_backend: --record-dir {recfile} "
                    f"exists but is not a directory\n")
    assert proc.stderr == expected_msg


def test_missing_token_file_named_refusal(tmp_path):
    """V-d F21: missing --token-file yields exit 2 with named reason, not a traceback."""
    proc = subprocess.run(
        [sys.executable, str(SERVER), "--port", str(_free_port()),
         "--token-file", str(tmp_path / "nonexistent.env"),
         "--record-dir", str(tmp_path / "rec")],
        capture_output=True, text=True, timeout=10)
    assert proc.returncode == 2
    missing_path = tmp_path / "nonexistent.env"
    expected_msg = f"scripted_backend: token file not found: {missing_path}\n"
    assert proc.stderr == expected_msg


def test_chunked_post_rejected_with_411(backend):
    """V-c F11: Transfer-Encoding: chunked on POST must yield 411 and close."""
    body_bytes = b'5\r\nhello\r\n0\r\n\r\n'
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{backend['port']}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Transfer-Encoding: chunked\r\n"
        f"Content-Type: application/json\r\n"
        f"\r\n"
    ).encode() + body_bytes
    resp = _raw_request(backend["port"], raw)
    # L6: exact status-line assertion
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 411 Length Required"


def test_chunked_get_rejected_with_411(backend):
    """M4: Transfer-Encoding: chunked on GET must also yield 411."""
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{backend['port']}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Transfer-Encoding: chunked\r\n"
        f"\r\n"
    ).encode()
    resp = _raw_request(backend["port"], raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 411 Length Required"


def test_content_length_negative_rejected(backend):
    """V-c F12: Content-Length: -1 must yield 400 and close."""
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{backend['port']}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Length: -1\r\n"
        f"Content-Type: application/json\r\n"
        f"\r\n"
    ).encode()
    resp = _raw_request(backend["port"], raw)
    # L6: exact status-line assertion
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"


def test_content_length_oversized_rejected(backend):
    """V-c F12: Content-Length: 2000000 must yield 400 and close."""
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{backend['port']}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Length: 2000000\r\n"
        f"Content-Type: application/json\r\n"
        f"\r\n"
    ).encode()
    resp = _raw_request(backend["port"], raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"


def test_content_length_underscore_rejected(backend):
    """L5: Content-Length with underscores (Python int() accepts '1_0') must be rejected."""
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{backend['port']}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Length: 1_0\r\n"
        f"Content-Type: application/json\r\n"
        f"\r\n"
    ).encode()
    resp = _raw_request(backend["port"], raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"


def test_credential_in_query_string_returns_400(backend):
    """V-c F10: token in query string triggers fail-closed 400."""
    status, data = _call(backend["port"], "GET", f"/v1/models?key={TOKEN}")
    assert status == 400
    obj = json.loads(data)
    assert obj["error"]["message"] == "credential in unexpected location"


def test_credential_in_body_returns_400(backend):
    """V-c F10: token in body triggers fail-closed 400."""
    body = {"model": "s0-01-pong", "messages": [{"role": "user", "content": TOKEN}]}
    status, data = _call(backend["port"], "POST", "/v1/chat/completions", body)
    assert status == 400
    obj = json.loads(data)
    assert obj["error"]["message"] == "credential in unexpected location"


def test_credential_in_custom_header_returns_400(backend):
    """V-c F10: token in a non-credential header value triggers 400."""
    status, data = _call(backend["port"], "GET", "/v1/models",
                         extra_headers={"X-Custom": TOKEN})
    assert status == 400
    obj = json.loads(data)
    assert obj["error"]["message"] == "credential in unexpected location"


@pytest.mark.parametrize("header_name", [
    "api-key", "x-api-key", "cookie", "x-auth-token", "proxy-authorization",
])
def test_credential_in_credential_header_returns_400(backend, header_name):
    """M12: token in api-key/x-api-key/cookie/x-auth-token/proxy-authorization
    must return 400 + marker record (exempts ONLY 'authorization')."""
    status, data = _call(backend["port"], "GET", "/v1/models",
                         extra_headers={header_name: TOKEN})
    assert status == 400
    obj = json.loads(data)
    assert obj["error"]["message"] == "credential in unexpected location"


def test_credential_headers_dropped_from_records(backend):
    """V-c F10: proxy-authorization, x-api-key, api-key, x-auth-token, cookie all dropped."""
    # Send a request with an extra credential header (api-key) — since value != TOKEN, no leak
    _call(backend["port"], "GET", "/v1/models",
          extra_headers={"api-key": "some-other-value"})
    recs = sorted(backend["rec"].glob("*.json"))
    last = json.loads(recs[-1].read_text())
    for k in last["headers"]:
        assert k not in ("authorization", "proxy-authorization", "x-api-key",
                         "api-key", "x-auth-token", "cookie"), \
            f"credential header {k!r} found in record"


def test_header_keys_lowercase_in_records(backend):
    """V-c F3: the backend stores all header keys lowercased."""
    # Send a GET with standard mixed-case headers (Host, Content-Type from http.client)
    _call(backend["port"], "GET", "/v1/models")
    recs = sorted(backend["rec"].glob("*.json"))
    last = json.loads(recs[-1].read_text())
    for k in last["headers"]:
        assert k == k.lower(), f"header key {k!r} not lowercase"


def test_leak_record_does_not_contain_token(backend):
    """H1: the leak marker record must NOT contain the bearer token verbatim.
    path=None, headers={} so the token never reaches committed evidence."""
    count_before = len(list(backend["rec"].glob("*.json")))
    _call(backend["port"], "GET", f"/v1/models?key={TOKEN}")
    recs = sorted(backend["rec"].glob("*.json"))
    # A new record should have been written
    assert len(recs) == count_before + 1
    last_bytes = recs[-1].read_bytes()
    # The token must NOT appear anywhere in the written record
    assert TOKEN.encode() not in last_bytes, \
        "the bearer token appears verbatim in the leak marker record"
    last = json.loads(last_bytes)
    assert last["path"] is None, "leak record path must be null"
    assert last["headers"] == {}, "leak record headers must be empty"
    assert last["body"] == {"credential_in_unexpected_location": True}


def test_remote_addr_exact_on_get_record(backend):
    """L13: remote_addr must be exact '127.0.0.1' on GET records too."""
    _call(backend["port"], "GET", "/v1/models")
    recs = sorted(backend["rec"].glob("*.json"))
    last = json.loads(recs[-1].read_text())
    assert last["method"] == "GET"
    assert last["remote_addr"] == "127.0.0.1"


@pytest.mark.parametrize("mode,accept", [
    (0o600, True),
    (0o400, True),
    (0o640, False),
    (0o644, False),
    (0o660, False),
])
def test_token_file_mode_guard(tmp_path, mode, accept):
    """M5: mode tests over 0o600/0o400 accept; 0o640/0o644/0o660 refuse with exact message."""
    tf = tmp_path / "token.env"
    tf.write_text(f"UPSTREAM_TOKEN={TOKEN}\n")
    tf.chmod(mode)
    port = _free_port()
    if accept:
        proc = subprocess.Popen(
            [sys.executable, str(SERVER), "--port", str(port),
             "--token-file", str(tf), "--record-dir", str(tmp_path / "rec"),
             "--slow-delay", "0.05"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        started = False
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=1)
                conn.request("GET", "/healthz")
                resp = conn.getresponse()
                resp.read()
                conn.close()
                if resp.status == 200:
                    started = True
                    break
            except OSError:
                time.sleep(0.05)
        proc.terminate()
        proc.wait(timeout=10)
        assert started, f"server should start with mode {oct(mode)}"
    else:
        proc = subprocess.run(
            [sys.executable, str(SERVER), "--port", str(port),
             "--token-file", str(tf), "--record-dir", str(tmp_path / "rec")],
            capture_output=True, text=True, timeout=10)
        assert proc.returncode == 2
        expected_msg = (f"scripted_backend: token file mode is {oct(mode)}, "
                        f"must have no group/other bits (0o600 or 0o400)\n")
        assert proc.stderr == expected_msg


# -- V5/S23: POST-arm leak record mutant killer --------------------------------

def test_post_arm_leak_record_does_not_contain_token(backend):
    """V5/S23: the POST arm of the credential-leak must produce a sanitized record
    (path=None, headers={}) with the token absent from the written bytes."""
    count_before = len(list(backend["rec"].glob("*.json")))
    body = {"model": "s0-01-pong", "messages": [{"role": "user", "content": "hello"}]}
    status, data = _call(backend["port"], "POST",
                         f"/v1/chat/completions?key={TOKEN}", body)
    assert status == 400
    assert json.loads(data)["error"]["message"] == "credential in unexpected location"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes, \
        "S23 mutant: the bearer token appears in the POST-arm leak record"
    last = json.loads(last_bytes)
    assert last["path"] is None
    assert last["headers"] == {}
    assert last["body"] == {"credential_in_unexpected_location": True}


def test_post_arm_leak_via_header_redacted(backend):
    """V5/S23: credential in a non-Authorization header on a POST -> sanitized record."""
    count_before = len(list(backend["rec"].glob("*.json")))
    body = {"model": "s0-01-pong", "messages": []}
    status, data = _call(backend["port"], "POST", "/v1/chat/completions",
                         body, extra_headers={"X-Trace-Id": TOKEN})
    assert status == 400
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes


# -- V10/S27b: sentinel mutant killers -----------------------------------------

def test_body_literal_bad_cl_is_not_sentinel(backend):
    """V10/S27b: a POST whose JSON body is the string 'BAD_CL' must be processed
    normally — not matched by the _BAD_CL sentinel. With bare-string sentinels
    and == comparison, this body matches and skips recording."""
    count_before = len(list(backend["rec"].glob("*.json")))
    body_bytes = b'"BAD_CL"'
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{backend['port']}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"\r\n"
    ).encode() + body_bytes
    resp = _raw_request(backend["port"], raw)
    # Must be the normal error path (record written), not the _BAD_CL path (no record)
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before + 1, \
        "S27b mutant: body literal 'BAD_CL' matched the sentinel, no record written"
    # The response should carry the JSON error, not a bare 400+close
    assert b"messages: Expected array" in resp


def test_chunked_transfer_encoding_411_writes_no_record(backend):
    """4-F9: chunked Transfer-Encoding on POST yields 411 and writes NO record."""
    count_before = len(list(backend["rec"].glob("*.json")))
    body_bytes = b'5\r\nhello\r\n0\r\n\r\n'
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{backend['port']}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Transfer-Encoding: chunked\r\n"
        f"Content-Type: application/json\r\n"
        f"\r\n"
    ).encode() + body_bytes
    resp = _raw_request(backend["port"], raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 411 Length Required"
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before, \
        f"chunked TE wrote {count_after - count_before} record(s), expected 0"


# -- V11/S28: handler timeout mutant killer ------------------------------------

def test_handler_timeout_bounds_incomplete_body(backend):
    """V11/S28: Handler.timeout prevents an incomplete body from blocking forever.
    A client sending headers + partial body but keeping the connection open must
    see the connection close within the handler timeout. If timeout is removed
    (S28 mutant), this hangs indefinitely."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("scripted_backend", str(SERVER))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _st = mod.State("x", Path("/tmp/unused-timeout-test"), 0)
    handler_timeout = mod.make_handler(_st).timeout
    port = backend["port"]
    s = socket.socket()
    s.settimeout(handler_timeout * 3)
    s.connect(("127.0.0.1", port))
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: 1048576\r\n"
        f"\r\n"
    ).encode() + b'{"model":"s0-01-pong"}'
    t0 = time.time()
    s.sendall(raw)
    # Keep connection open — no SHUT_WR — the server must timeout
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
    except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError):
        pass
    elapsed = time.time() - t0
    s.close()
    # F15/F20: bound derived from the handler's configured timeout, not hand-copied
    assert elapsed >= handler_timeout * 0.5, \
        f"completed too fast ({elapsed:.1f}s), expected >= {handler_timeout * 0.5:.0f}s"
    assert elapsed <= handler_timeout * 2.5, \
        f"took too long ({elapsed:.1f}s), expected <= {handler_timeout * 2.5:.0f}s"
    # Server must still be alive
    status, _ = _call(port, "GET", "/healthz", token=None)
    assert status == 200


# -- V17/A18: port range validation --------------------------------------------

@pytest.mark.parametrize("port", [-1, 0, 65536, 70000])
def test_port_outside_valid_range_refuses_exit_2(tmp_path, port):
    """V17/A18: --port outside 1..65535 -> named refusal exit 2."""
    tf = tmp_path / "token.env"
    tf.write_text(f"UPSTREAM_TOKEN={TOKEN}\n")
    tf.chmod(0o600)
    proc = subprocess.run(
        [sys.executable, str(SERVER), "--port", str(port),
         "--token-file", str(tf), "--record-dir", str(tmp_path / "rec")],
        capture_output=True, text=True, timeout=10)
    assert proc.returncode == 2
    expected_msg = (f"scripted_backend: --port {port} "
                    f"is outside the valid range 1-65535\n")
    assert proc.stderr == expected_msg


# -- V18/A18: short body -> 400 + zero records ---------------------------------

def test_short_body_returns_400_no_record(backend):
    """V18/A18: a body shorter than declared Content-Length (client hangs up early)
    must yield 400 and zero new records."""
    count_before = len(list(backend["rec"].glob("*.json")))
    port = backend["port"]
    body = b'{"model":"s0-01-pong","messages":[{"role":"user","content":"hi"}]}'
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: 100000\r\n"
        f"\r\n"
    ).encode() + body
    s = socket.socket()
    s.settimeout(5)
    s.connect(("127.0.0.1", port))
    s.sendall(raw)
    s.shutdown(socket.SHUT_WR)
    resp = b""
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            resp += chunk
    except socket.timeout:
        pass
    s.close()
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before, \
        f"short body wrote {count_after - count_before} record(s), expected 0"


# -- P1: malformed-JSON credential redaction at recording boundary --------------

def test_malformed_json_with_token_in_url_redacted(backend):
    """P1: malformed-JSON POST with token in URL -> 400, token NOT in record.
    Kills the P1 mutant: moving the credential check outside record()
    lets the JSON-error path write the URL (with the token) verbatim."""
    count_before = len(list(backend["rec"].glob("*.json")))
    port = backend["port"]
    malformed_body = b'{bad json'
    raw = (
        f"POST /v1/chat/completions?key={TOKEN} HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(malformed_body)}\r\n"
        f"\r\n"
    ).encode() + malformed_body
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes, \
        "P1 mutant: token leaked through JSON-error recording path (URL)"


def test_malformed_json_with_token_in_header_redacted(backend):
    """P1: malformed-JSON POST with token in an ordinary header -> 400,
    token NOT in record."""
    count_before = len(list(backend["rec"].glob("*.json")))
    port = backend["port"]
    malformed_body = b'{bad json'
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"X-Custom: {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(malformed_body)}\r\n"
        f"\r\n"
    ).encode() + malformed_body
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes, \
        "P1 mutant: token leaked through JSON-error recording path (header)"


def test_malformed_json_with_token_in_body_redacted(backend):
    """P1/4-F7/6-F17: malformed-JSON POST with token in raw body -> 400
    with 'credential in unexpected location' (not 'body is not JSON'),
    record is marker.  Dropping raw_body=e.raw makes the error message change."""
    count_before = len(list(backend["rec"].glob("*.json")))
    port = backend["port"]
    # Malformed JSON body containing the token
    malformed_body = (f'{{"key": "{TOKEN}" invalid').encode()
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(malformed_body)}\r\n"
        f"\r\n"
    ).encode() + malformed_body
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    # 4-F7/6-F17: exact error message gates the raw_body arm — without it
    # the response would be "body is not JSON" and this assertion fails.
    body_start = resp.find(b"\r\n\r\n")
    assert body_start >= 0
    resp_body = json.loads(resp[body_start + 4:])
    assert resp_body["error"]["message"] == "credential in unexpected location"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes, \
        "P1 mutant: token leaked through JSON-error recording path (body)"
    last = json.loads(last_bytes)
    assert last["path"] is None
    assert last["headers"] == {}
    assert last["body"] == {"credential_in_unexpected_location": True}


def test_p1_boundary_credential_check_in_record(tmp_path):
    """P1 boundary mutant: proves the credential-leak check inside record()
    sanitizes the written file. If the check were moved back to the handler
    (pre-P1 state), any direct record() call with the token in the path
    would write it verbatim."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "scripted_backend", str(SERVER))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rec = tmp_path / "rec"
    st = mod.State(TOKEN, rec, 0.05)
    # Call with token in path — record() must sanitize
    n, leaked = st.record("POST", f"/v1/chat?key={TOKEN}", {},
                          "<invalid json>", "127.0.0.1", TOKEN)
    assert leaked is True
    written = (rec / f"{n:06d}.json").read_bytes()
    assert TOKEN.encode() not in written
    data = json.loads(written)
    assert data["path"] is None
    assert data["headers"] == {}
    assert data["body"] == {"credential_in_unexpected_location": True}
    # Normal call without leak — record() returns leaked=False
    n2, leaked2 = st.record("POST", "/v1/chat/completions", {},
                            {"model": "test"}, "127.0.0.1", TOKEN)
    assert leaked2 is False
    data2 = json.loads((rec / f"{n2:06d}.json").read_bytes())
    assert data2["path"] == "/v1/chat/completions"


# -- build_capture_record.py tests (V-d F12) ---------------------------------

BUILD_CAPTURE = ROOT / "proofs" / "S0-01" / "tools" / "build_capture_record.py"


def test_build_capture_record_roundtrip_check(tmp_path):
    """V-d F12: build a capture.json from a synthetic leg, then --check round-trips."""
    leg = tmp_path / "testleg"
    leg.mkdir()
    # timeline.jsonl — two entries
    tl = [
        {"seq": 1, "dir": "c2a", "t_utc": "2026-09-05T12:00:00.000000Z",
         "t_mono_ns": 1000, "frame": {"jsonrpc": "2.0", "id": 1, "method": "initialize"}},
        {"seq": 2, "dir": "a2c", "t_utc": "2026-09-05T12:00:01.000000Z",
         "t_mono_ns": 2000, "frame": {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": 1}}},
    ]
    (leg / "timeline.jsonl").write_text(
        "\n".join(json.dumps(e, separators=(",", ":")) for e in tl) + "\n"
    )
    # runtime-identity.json
    (leg / "runtime-identity.json").write_text(json.dumps({"tee_pid": 1234}) + "\n")
    # env.json
    (leg / "env.json").write_text(json.dumps({"PATH": "/usr/bin"}) + "\n")
    # buzz-acp.exit
    (leg / "buzz-acp.exit").write_text("0\n")
    # buzz-acp.pid
    (leg / "buzz-acp.pid").write_text("9999\n")
    # hermes-model.txt
    (leg / "hermes-model.txt").write_text("default: s0-01-scripted/s0-01-pong\n")
    # startup-line.txt
    (leg / "startup-line.txt").write_text(
        "2026-09-05T12:00:00Z  INFO buzz_acp: buzz-acp starting: idle_timeout=900s max_turn=3600s session_policy=thread\n"
    )

    # Build capture.json
    r1 = subprocess.run(
        [sys.executable, str(BUILD_CAPTURE), str(leg), "test-leg"],
        capture_output=True, text=True, timeout=10)
    assert r1.returncode == 0, f"build failed: {r1.stderr}"
    assert (leg / "capture.json").exists()

    # --check must pass (round-trip)
    r2 = subprocess.run(
        [sys.executable, str(BUILD_CAPTURE), "--check", str(leg), "test-leg"],
        capture_output=True, text=True, timeout=10)
    assert r2.returncode == 0, f"--check failed: {r2.stderr}"
    # F13: exact assertion, not substring
    assert r2.stdout.strip() == "test-leg: capture.json matches (--check)"

    # Tamper with capture.json and verify --check fails
    cj = leg / "capture.json"
    cj.write_text(cj.read_text().replace('"version": 2', '"version": 99'))
    r3 = subprocess.run(
        [sys.executable, str(BUILD_CAPTURE), "--check", str(leg), "test-leg"],
        capture_output=True, text=True, timeout=10)
    assert r3.returncode == 1, f"--check should fail after tamper: {r3.stderr}"
    assert r3.stderr.strip() == "test-leg: capture.json differs from re-derived content (--check)"


# -- 4-F1/6-F3: credential screen keyed on CONFIGURED token (not request bearer) --

def test_credential_in_query_no_auth_header_returns_400(backend):
    """4-F1/6-F3: token in URL query with NO Authorization header -> 400,
    record does not contain the token (keyed on configured token)."""
    count_before = len(list(backend["rec"].glob("*.json")))
    status, data = _call(backend["port"], "GET", f"/v1/models?key={TOKEN}", token=None)
    assert status == 400
    assert json.loads(data)["error"]["message"] == "credential in unexpected location"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes


def test_credential_in_header_no_auth_returns_400(backend):
    """4-F1/6-F3: token in a custom header with NO Authorization header -> 400,
    record does not contain the token."""
    count_before = len(list(backend["rec"].glob("*.json")))
    status, data = _call(backend["port"], "GET", "/v1/models",
                         token=None, extra_headers={"X-Trace-Id": TOKEN})
    assert status == 400
    assert json.loads(data)["error"]["message"] == "credential in unexpected location"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes


def test_credential_in_body_no_auth_returns_400(backend):
    """4-F1/6-F3: token in JSON body with NO Authorization header -> 400,
    record does not contain the token."""
    count_before = len(list(backend["rec"].glob("*.json")))
    body = {"model": "s0-01-pong", "messages": [{"role": "user", "content": TOKEN}]}
    status, data = _call(backend["port"], "POST", "/v1/chat/completions",
                         body, token=None)
    assert status == 400
    assert json.loads(data)["error"]["message"] == "credential in unexpected location"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes


def test_credential_in_raw_body_no_auth_returns_400(backend):
    """4-F1/6-F3: token in malformed JSON body with NO Authorization header -> 400
    with 'credential in unexpected location', record does not contain the token."""
    count_before = len(list(backend["rec"].glob("*.json")))
    port = backend["port"]
    malformed_body = (f'{{"key": "{TOKEN}" invalid').encode()
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(malformed_body)}\r\n"
        f"\r\n"
    ).encode() + malformed_body
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    # Exact error message: without the configured-token screen this would be
    # "body is not JSON" (bearer_token is None so the old check was skipped).
    body_start = resp.find(b"\r\n\r\n")
    assert body_start >= 0
    resp_body = json.loads(resp[body_start + 4:])
    assert resp_body["error"]["message"] == "credential in unexpected location"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes


def test_short_bogus_bearer_does_not_collapse_records(backend):
    """4-F1 DoE inverse: Authorization: Bearer 1 must NOT collapse records.
    The screen uses self.token (the configured secret), so a short bearer
    cannot match substrings of unrelated fields."""
    count_before = len(list(backend["rec"].glob("*.json")))
    status, data = _call(backend["port"], "GET", "/v1/models", token="1")
    assert status == 401  # wrong bearer, not a leak
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    last = json.loads(recs[-1].read_bytes())
    # Record must contain the real path, not a marker
    assert last["path"] == "/v1/models"
    # R5-D5-F10: exact value — credential headers dropped, content-type preserved
    assert "authorization" not in last["headers"]
    assert last["headers"]["content-type"] == "application/json"


# -- 4-F4: GET with Content-Length rejected, no request smuggling ----------------

def test_get_with_body_rejected_no_smuggling(backend):
    """4-F4: GET with Content-Length > 0 reads the body, returns 400 with
    Connection: close, and does NOT parse a second request from the leftover."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    smuggled_body = json.dumps({"model": "s0-01-pong",
                                "messages": [{"role": "user", "content": "FORGED"}]})
    smuggled = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(smuggled_body)}\r\n"
        f"\r\n"
        f"{smuggled_body}"
    )
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Length: {len(smuggled)}\r\n"
        f"\r\n"
    ).encode() + smuggled.encode()
    resp = _raw_request(port, raw)
    # Must get 400 (GET with body rejected), not 200/401 from normal GET
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    # Only ONE HTTP response — no smuggling
    assert resp.count(b"HTTP/1.1 ") == 1, \
        f"expected 1 response but got {resp.count(b'HTTP/1.1 ')}: smuggling likely"
    # No new records created (rejected before recording)
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before, \
        f"GET-with-body wrote {count_after - count_before} record(s), expected 0"


# -- 4-F12: --slow-delay validation ---------------------------------------------

@pytest.mark.parametrize("delay_args,printed", [
    (["--slow-delay", "nan"], "nan"),
    (["--slow-delay", "-1"], "-1.0"),
    (["--slow-delay", "inf"], "inf"),
    (["--slow-delay=-inf"], "-inf"),
    (["--slow-delay=-nan"], "nan"),
    (["--slow-delay=-1e-9"], "-1e-09"),
])
def test_slow_delay_invalid_refuses_exit_2(tmp_path, delay_args, printed):
    """R5-D5-F7: --slow-delay nan/-1/inf/-inf/-nan/-1e-9 -> named refusal exit 2."""
    tf = tmp_path / "token.env"
    tf.write_text(f"UPSTREAM_TOKEN={TOKEN}\n")
    tf.chmod(0o600)
    proc = subprocess.run(
        [sys.executable, str(SERVER), "--port", str(_free_port()),
         "--token-file", str(tf), "--record-dir", str(tmp_path / "rec")]
        + delay_args,
        capture_output=True, text=True, timeout=10)
    assert proc.returncode == 2
    expected = (f"scripted_backend: --slow-delay {printed} "
                f"must be a finite number >= 0\n")
    assert proc.stderr == expected


# -- R5-D5-F1: /healthz smuggling vectors ----------------------------------------

@pytest.mark.parametrize("token", [TOKEN, None], ids=["with_cred", "no_cred"])
def test_healthz_with_cl_body_rejected_one_response_zero_records(backend, token):
    """R5-D5-F1: GET /healthz with Content-Length body must be rejected (400),
    exactly 1 response, zero new records — the framing gate sits BEFORE /healthz."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    smuggled_body = json.dumps({"model": "s0-01-pong",
                                "messages": [{"role": "user", "content": "FORGED"}]})
    smuggled = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(smuggled_body)}\r\n"
        f"\r\n"
        f"{smuggled_body}"
    )
    auth = f"Authorization: Bearer {token}\r\n" if token else ""
    raw = (
        f"GET /healthz HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"{auth}"
        f"Content-Length: {len(smuggled)}\r\n"
        f"\r\n"
    ).encode() + smuggled.encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert resp.count(b"HTTP/1.1 ") == 1, \
        f"expected 1 response but got {resp.count(b'HTTP/1.1 ')}: smuggling via /healthz"
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before, \
        f"/healthz+CL smuggle wrote {count_after - count_before} record(s), expected 0"


@pytest.mark.parametrize("token", [TOKEN, None], ids=["with_cred", "no_cred"])
def test_healthz_with_te_body_rejected_one_response_zero_records(backend, token):
    """R5-D5-F1: GET /healthz with Transfer-Encoding: chunked must be rejected (411),
    exactly 1 response, zero new records."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    smuggled_body = json.dumps({"model": "s0-01-pong",
                                "messages": [{"role": "user", "content": "FORGED"}]})
    smuggled = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(smuggled_body)}\r\n"
        f"\r\n"
        f"{smuggled_body}"
    )
    auth = f"Authorization: Bearer {token}\r\n" if token else ""
    raw = (
        f"GET /healthz HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"{auth}"
        f"Transfer-Encoding: chunked\r\n"
        f"\r\n"
    ).encode() + smuggled.encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 411 Length Required"
    assert resp.count(b"HTTP/1.1 ") == 1, \
        f"expected 1 response but got {resp.count(b'HTTP/1.1 ')}: smuggling via /healthz+TE"
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before, \
        f"/healthz+TE smuggle wrote {count_after - count_before} record(s), expected 0"


@pytest.mark.parametrize("token", [TOKEN, None], ids=["with_cred", "no_cred"])
def test_healthz_query_with_cl_body_rejected_one_response_zero_records(backend, token):
    """R5-D5-F1: GET /healthz?x=1 with Content-Length body must be rejected (400),
    exactly 1 response, zero new records."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    smuggled_body = json.dumps({"model": "s0-01-pong",
                                "messages": [{"role": "user", "content": "FORGED"}]})
    smuggled = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(smuggled_body)}\r\n"
        f"\r\n"
        f"{smuggled_body}"
    )
    auth = f"Authorization: Bearer {token}\r\n" if token else ""
    raw = (
        f"GET /healthz?x=1 HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"{auth}"
        f"Content-Length: {len(smuggled)}\r\n"
        f"\r\n"
    ).encode() + smuggled.encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert resp.count(b"HTTP/1.1 ") == 1, \
        f"expected 1 response but got {resp.count(b'HTTP/1.1 ')}: smuggling via /healthz?x=1"
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before, \
        f"/healthz?x=1+CL smuggle wrote {count_after - count_before} record(s), expected 0"


# -- R5-D5-F2: close_connection anti-smuggling proven ----------------------------

@pytest.mark.parametrize("token", [TOKEN, None], ids=["with_cred", "no_cred"])
def test_chunked_te_post_smuggling_one_response_zero_records(backend, token):
    """R5-D5-F2: chunked-TE POST whose body is a complete request -> exactly 1
    response (411), zero new records. Dropping close_connection lets the smuggled
    request parse -> 2 responses."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    smuggled_body = json.dumps({"model": "s0-01-pong",
                                "messages": [{"role": "user", "content": "FORGED"}]})
    smuggled = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(smuggled_body)}\r\n"
        f"\r\n"
        f"{smuggled_body}"
    )
    auth = f"Authorization: Bearer {token}\r\n" if token else ""
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"{auth}"
        f"Transfer-Encoding: chunked\r\n"
        f"Content-Type: application/json\r\n"
        f"\r\n"
    ).encode() + smuggled.encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 411 Length Required"
    assert resp.count(b"HTTP/1.1 ") == 1, \
        f"expected 1 response but got {resp.count(b'HTTP/1.1 ')}: TE POST smuggling"
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before, \
        f"TE POST smuggle wrote {count_after - count_before} record(s), expected 0"


@pytest.mark.parametrize("token", [TOKEN, None], ids=["with_cred", "no_cred"])
def test_chunked_te_get_smuggling_one_response_zero_records(backend, token):
    """R5-D5-F2: chunked-TE GET whose body is a complete request -> exactly 1
    response (411), zero new records."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    smuggled_body = json.dumps({"model": "s0-01-pong",
                                "messages": [{"role": "user", "content": "FORGED"}]})
    smuggled = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(smuggled_body)}\r\n"
        f"\r\n"
        f"{smuggled_body}"
    )
    auth = f"Authorization: Bearer {token}\r\n" if token else ""
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"{auth}"
        f"Transfer-Encoding: chunked\r\n"
        f"\r\n"
    ).encode() + smuggled.encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 411 Length Required"
    assert resp.count(b"HTTP/1.1 ") == 1, \
        f"expected 1 response but got {resp.count(b'HTTP/1.1 ')}: TE GET smuggling"
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before, \
        f"TE GET smuggle wrote {count_after - count_before} record(s), expected 0"


@pytest.mark.parametrize("token", [TOKEN, None], ids=["with_cred", "no_cred"])
def test_get_cl_over_max_smuggling_one_response_zero_records(backend, token):
    """R5-D5-F2: GET with CL > MAX_CONTENT_LENGTH and a forged request past the
    cut -> exactly 1 response (400), zero new records."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    smuggled_body = json.dumps({"model": "s0-01-pong",
                                "messages": [{"role": "user", "content": "FORGED"}]})
    smuggled = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(smuggled_body)}\r\n"
        f"\r\n"
        f"{smuggled_body}"
    )
    # CL larger than MAX (1_048_576); send MAX+1 bytes of padding + smuggled request
    padding = b"X" * 1_048_577
    total_len = len(padding) + len(smuggled)
    auth = f"Authorization: Bearer {token}\r\n" if token else ""
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"{auth}"
        f"Content-Length: {total_len}\r\n"
        f"\r\n"
    ).encode() + padding + smuggled.encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert resp.count(b"HTTP/1.1 ") == 1, \
        f"expected 1 response but got {resp.count(b'HTTP/1.1 ')}: GET CL>MAX smuggling"
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before, \
        f"GET CL>MAX smuggle wrote {count_after - count_before} record(s), expected 0"


# -- R5-D5-F3: credential screen covers header NAMES -----------------------------

def test_credential_in_header_name_returns_400(backend):
    """R5-D5-F3: the CONFIGURED token as a header NAME (not value) must trigger
    the credential-leak screen -> 400 + sanitized record."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"{TOKEN}: x\r\n"
        f"\r\n"
    ).encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    body_start = resp.find(b"\r\n\r\n")
    assert body_start >= 0
    resp_body = json.loads(resp[body_start + 4:])
    assert resp_body["error"]["message"] == "credential in unexpected location"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes


# -- R5-D5-F4: duplicate Content-Length rejected ----------------------------------

@pytest.mark.parametrize("token", [TOKEN, None], ids=["with_cred", "no_cred"])
def test_duplicate_content_length_rejected_400(backend, token):
    """R5-D5-F4: duplicate Content-Length headers -> 400 + close, zero new records."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    smuggled_body = json.dumps({"model": "s0-01-pong",
                                "messages": [{"role": "user", "content": "FORGED2"}]})
    inner_len = len(smuggled_body)
    auth = f"Authorization: Bearer {token}\r\n" if token else ""
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"{auth}"
        f"Content-Type: application/json\r\n"
        f"Content-Length: 2\r\n"
        f"Content-Length: {2 + inner_len}\r\n"
        f"\r\n"
    ).encode() + b"{}" + smuggled_body.encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert resp.count(b"HTTP/1.1 ") == 1, \
        f"expected 1 response but got {resp.count(b'HTTP/1.1 ')}: duplicate CL smuggling"
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before, \
        f"duplicate CL wrote {count_after - count_before} record(s), expected 0"


# -- R5-D5-F5: GET with Content-Length: 0 accepted and recorded -------------------

def test_get_content_length_zero_accepted_and_recorded(backend):
    """R5-D5-F5: GET with Content-Length: 0 must be accepted (200), served, and
    recorded — CL:0 is NOT a smuggling vector."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Length: 0\r\n"
        f"\r\n"
    ).encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 200 OK"
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before + 1, \
        f"CL:0 GET should write 1 record, wrote {count_after - count_before}"


# -- R5-D5-F6: percent-encoded token in query ------------------------------------

def test_credential_percent_encoded_in_query_returns_400(backend):
    """R5-D5-F6: percent-encoded token in query must be caught via unquote(path)."""
    port = backend["port"]
    # Encode the last character so the literal doesn't match but unquote does
    encoded_token = TOKEN[:-1] + "%{:02x}".format(ord(TOKEN[-1]))
    count_before = len(list(backend["rec"].glob("*.json")))
    status, data = _call(port, "GET", f"/v1/models?key={encoded_token}")
    assert status == 400
    assert json.loads(data)["error"]["message"] == "credential in unexpected location"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes


# -- R5-D5-F8: GET with CL:1 kills M11 mutant (cl > 0 -> cl > 1) ----------------

def test_get_with_cl_1_rejected_400(backend):
    """R5-D5-F8/M11: GET with Content-Length: 1 must be rejected (400).
    The M11 mutant (cl > 0 -> cl > 1) lets CL:1 fall through -> 200/401."""
    port = backend["port"]
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Length: 1\r\n"
        f"\r\n"
        f"X"
    ).encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"


# -- D5c: framing gate domain table -------------------------------------------

_POST_BODY = {"model": "s0-01-pong", "messages": [{"role": "user", "content": "hi"}]}
_POST_BODY_BYTES = json.dumps(_POST_BODY).encode()

# Forged POST tail: a complete valid request that creates a record if processed
def _forged_tail(port):
    body = json.dumps({"model": "s0-01-pong",
                        "messages": [{"role": "user", "content": "FORGED"}]})
    return (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"\r\n"
        f"{body}"
    ).encode()


def _build_domain_table():
    """Build the full framing-gate domain table.

    Each entry: (case_id, method, path, header_lines, body_bytes, token_value,
                 expected_status, expect_close, expected_records_delta)

    Framing cases x routes x credentials, per the brief's allow-list design.
    """
    table = []
    cl_n_len = len(_POST_BODY_BYTES)

    # (name, extra_header_lines, get_gate_status, post_gate_status)
    # gate_status = None means accepted (not rejected by gate)
    FRAMINGS = [
        ("no_cl",       [],                                        None, None),
        ("cl_0",        ["Content-Length: 0"],                      None, None),
        ("cl_n",        [f"Content-Length: {cl_n_len}"],            400,  None),
        ("cl_neg1",     ["Content-Length: -1"],                     400,  400),
        ("cl_neg0",     ["Content-Length: -0"],                     400,  400),
        ("cl_abc",      ["Content-Length: abc"],                    400,  400),
        ("cl_1e3",      ["Content-Length: 1e3"],                    400,  400),
        ("cl_0x10",     ["Content-Length: 0x10"],                   400,  400),
        ("cl_empty",    ["Content-Length:"],                        400,  400),
        # Leading space: parser strips it, value becomes "5" -> accepted
        ("cl_space5",   ["Content-Length:  5"],                     400,  None),
        ("cl_5space",   ["Content-Length: 5 "],                     400,  400),
        ("cl_1_0",      ["Content-Length: 1_0"],                    400,  400),
        ("cl_over_max", ["Content-Length: 2000000"],                400,  400),
        ("dup_cl_eq",   ["Content-Length: 5", "Content-Length: 5"], 400,  400),
        ("dup_cl_diff", ["Content-Length: 5", "Content-Length: 10"],400,  400),
        ("te_chunked",  ["Transfer-Encoding: chunked"],            411,  411),
        ("te_gzip",     ["Transfer-Encoding: gzip"],               411,  411),
        ("te_identity", ["Transfer-Encoding: identity"],           411,  411),
        ("te_two",      ["Transfer-Encoding: chunked",
                         "Transfer-Encoding: gzip"],               411,  411),
        ("defects",     ["Content-Length : 5"],                     400,  400),
        ("expect",      ["Expect: 100-continue"],                  417,  417),
    ]

    ROUTES = [
        ("GET",  "/v1/models"),
        ("GET",  "/healthz"),
        ("GET",  "/healthz?x=1"),
        ("POST", "/v1/chat/completions"),
    ]

    for fname, headers, get_gate, post_gate in FRAMINGS:
        for route_method, route_path in ROUTES:
            for has_cred in (True, False):
                cred_label = "cred" if has_cred else "nocred"
                token_val = TOKEN if has_cred else None
                method = route_method

                gate_status = get_gate if method == "GET" else post_gate

                # cl_space5 on GET: parser strips leading space -> value "5" ->
                # fullmatch passes -> cl=5, cl > 0 on GET -> rejected 400
                if fname == "cl_space5" and method == "GET":
                    gate_status = 400

                # cl_space5 on POST: parser strips -> "5" -> valid, cl=5 <= MAX -> accepted
                # (post_gate is already None for cl_space5)

                if gate_status is not None:
                    status = gate_status
                    records = 0
                    close = True
                else:
                    # Gate accepts -- status depends on route/cred
                    close = False
                    if method == "GET":
                        base_path = route_path.split("?", 1)[0]
                        if base_path == "/healthz":
                            status = 200
                            records = 0
                        elif base_path == "/v1/models":
                            status = 200 if has_cred else 401
                            records = 1
                        else:
                            status = 404 if has_cred else 401
                            records = 1
                    else:  # POST
                        records = 1
                        if fname == "cl_n":
                            status = 200 if has_cred else 401
                        elif fname == "cl_space5":
                            # CL "5" -> reads 5 bytes of body -> short body
                            # if body is _POST_BODY_BYTES (longer) -> only 5 read
                            # Actually: cl=5 with len(body_bytes) matching is fine
                            # We send 5 bytes body -> short for real body -> 400
                            status = 400 if has_cred else 401
                            records = 0 if has_cred else 1
                        else:
                            # no_cl or cl_0: body is None
                            status = 400 if has_cred else 401

                # Build body_bytes — enough data so gate reads complete instantly
                if gate_status is not None:
                    # Rejected: supply body matching the claimed CL so reads don't block
                    if method == "GET" and fname == "cl_n":
                        body = b"X" * cl_n_len
                    elif method == "GET" and fname == "cl_over_max":
                        # gate reads min(2000000, MAX)=MAX bytes; supply them
                        body = b"X" * 1_048_576
                    elif method == "GET" and fname in ("cl_space5", "cl_5space"):
                        body = b"XXXXX"
                    else:
                        body = b""
                else:
                    if method == "POST" and fname == "cl_n":
                        body = _POST_BODY_BYTES
                    elif method == "POST" and fname == "cl_space5":
                        body = b"XXXXX"
                    else:
                        body = b""

                # cl_space5 on POST: CL=5, body=5 bytes "XXXXX", json.loads fails
                # -> _ParseError -> record written -> 400 "body is not JSON"
                # _ParseError returns 400 BEFORE the auth check, regardless of cred
                if fname == "cl_space5" and method == "POST" and gate_status is None:
                    records = 1
                    status = 400  # always "body is not JSON"

                case_id = f"{fname}/{route_method}{route_path}/{cred_label}"
                table.append((case_id, method, route_path, headers, body,
                              token_val, status, close, records))

    # Method overrides: PUT, HEAD, OPTIONS -> 501 via http.server
    for mname in ("PUT", "HEAD", "OPTIONS"):
        for _, route_path in ROUTES:
            for has_cred in (True, False):
                cred_label = "cred" if has_cred else "nocred"
                token_val = TOKEN if has_cred else None
                case_id = f"{mname.lower()}/{mname}{route_path}/{cred_label}"
                table.append((case_id, mname, route_path, [], b"",
                              token_val, 501, True, 0))

    return table


_DOMAIN_TABLE = _build_domain_table()


@pytest.mark.parametrize(
    "case_id,method,path,header_lines,body_bytes,token_val,"
    "expected_status,expect_close,expected_records",
    _DOMAIN_TABLE,
    ids=[t[0] for t in _DOMAIN_TABLE],
)
def test_framing_domain_table(backend, case_id, method, path, header_lines,
                               body_bytes, token_val, expected_status,
                               expect_close, expected_records):
    """D5c: table-driven domain test for the framing gate allow-list.

    Every request is followed by a forged POST tail in the same sendall.
    Asserts: expected status, Connection: close on rejections, exactly one
    HTTP/1.1 response, and exact record count delta.
    """
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))

    # Build raw request
    lines = [f"{method} {path} HTTP/1.1", f"Host: 127.0.0.1:{port}"]
    if token_val is not None:
        lines.append(f"Authorization: Bearer {token_val}")
    if method == "POST":
        lines.append("Content-Type: application/json")
    for hl in header_lines:
        lines.append(hl)
    raw_req = ("\r\n".join(lines) + "\r\n\r\n").encode() + body_bytes

    # Append forged tail (a complete valid POST that creates a record if processed)
    tail = _forged_tail(port)
    payload = raw_req + tail

    # Send and read response
    s = socket.socket()
    s.settimeout(5)
    s.connect(("127.0.0.1", port))
    s.sendall(payload)
    chunks = []
    try:
        while True:
            c = s.recv(8192)
            if not c:
                break
            chunks.append(c)
    except socket.timeout:
        pass
    s.close()
    resp = b"".join(chunks)

    # Assert status of the FIRST response
    status_line = resp.split(b"\r\n", 1)[0]
    assert status_line.split()[1] == str(expected_status).encode(), \
        f"[{case_id}] expected {expected_status}, got {status_line!r}"

    http_count = resp.count(b"HTTP/1.1 ")

    if expect_close:
        # REJECTED: gate closed the connection, tail must NOT be processed
        assert http_count == 1, \
            f"[{case_id}] expected 1 HTTP/1.1 response, got {http_count}: smuggling"
        assert b"Connection: close" in resp, \
            f"[{case_id}] rejection must include Connection: close"
        # Zero new records from the rejected request (tail blocked too)
        count_after = len(list(backend["rec"].glob("*.json")))
        actual_delta = count_after - count_before
        assert actual_delta == 0, \
            f"[{case_id}] rejected request wrote {actual_delta} record(s), expected 0"
    else:
        # ACCEPTED: first request served, tail processed via keep-alive
        # Tail is a valid POST that always creates 1 record
        assert http_count == 2, \
            f"[{case_id}] expected 2 HTTP/1.1 responses (served + tail), got {http_count}"
        count_after = len(list(backend["rec"].glob("*.json")))
        actual_delta = count_after - count_before
        total_expected = expected_records + 1  # +1 for the processed tail
        assert actual_delta == total_expected, \
            f"[{case_id}] expected {total_expected} new record(s) " \
            f"({expected_records} + 1 tail), got {actual_delta}"


# -- D5c: superstring bearer control ------------------------------------------

def test_bearer_superstring_rejected_401(backend):
    """D5c F11: Bearer <token>X must be rejected (not authenticated).
    Authorization uses ==, not startswith."""
    status, data = _call(backend["port"], "GET", "/v1/models",
                         token=TOKEN + "X")
    assert status == 401
    assert json.loads(data)["error"]["code"] == "unauthorized"


def test_bearer_extra_space_rejected_401(backend):
    """D5c F11: Bearer <token> extra must be rejected."""
    port = backend["port"]
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN} extra\r\n"
        f"\r\n"
    ).encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 401 Unauthorized"


# -- D5c: /healthzXYZ control ------------------------------------------------

def test_healthz_exact_path_no_prefix_match(backend):
    """D5c F22: /healthzXYZ must NOT match /healthz -> recorded + auth-checked.
    With no credential: 401 (not 200 which /healthz would give)."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    status, data = _call(port, "GET", "/healthzXYZ", token=None)
    assert status == 401, "/healthzXYZ must NOT be treated as /healthz"
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after == count_before + 1, \
        "/healthzXYZ must write a record (not treated as /healthz)"


# -- D5c: credential screen — percent-encoded token in header value ----------

def test_credential_percent_encoded_in_header_value(backend):
    """D5c F9: percent-encoded token in header VALUE must be caught."""
    port = backend["port"]
    encoded = TOKEN[:-1] + "%{:02x}".format(ord(TOKEN[-1]))
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"X-Trace: {encoded}\r\n"
        f"\r\n"
    ).encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    body_start = resp.find(b"\r\n\r\n")
    assert body_start >= 0
    resp_body = json.loads(resp[body_start + 4:])
    assert resp_body["error"]["message"] == "credential in unexpected location"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    assert TOKEN.encode() not in recs[-1].read_bytes()


# -- D5c: credential screen — percent-encoded token in header name ----------

def test_credential_percent_encoded_in_header_name(backend):
    """D5c F9: percent-encoded token in header NAME must be caught."""
    port = backend["port"]
    encoded = TOKEN[:-1] + "%{:02x}".format(ord(TOKEN[-1]))
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"{encoded}: x\r\n"
        f"\r\n"
    ).encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    assert TOKEN.encode() not in recs[-1].read_bytes()


# -- D5c: credential screen — percent-encoded token in body -----------------

def test_credential_percent_encoded_in_json_body(backend):
    """D5c F9: percent-encoded token in JSON body must be caught."""
    port = backend["port"]
    encoded = TOKEN[:-1] + "%{:02x}".format(ord(TOKEN[-1]))
    body = json.dumps({"model": "s0-01-pong", "messages": [],
                        "note": encoded})
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"\r\n"
        f"{body}"
    ).encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    assert TOKEN.encode() not in recs[-1].read_bytes()


# -- D5c: credential screen — obs-folded token in header value ---------------

def test_credential_obs_folded_in_header_value(backend):
    """D5c F10: obs-folded token (whitespace inserted) in header value
    must be caught by the whitespace-strip normalization."""
    port = backend["port"]
    # Insert whitespace in the middle of the token
    mid = len(TOKEN) // 2
    folded = TOKEN[:mid] + " \t " + TOKEN[mid:]
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"X-Trace: {folded}\r\n"
        f"\r\n"
    ).encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    body_start = resp.find(b"\r\n\r\n")
    assert body_start >= 0
    resp_body = json.loads(resp[body_start + 4:])
    assert resp_body["error"]["message"] == "credential in unexpected location"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    assert TOKEN.encode() not in recs[-1].read_bytes()


# -- D5d/F7: triple percent-encoding caught by fixed-point unquote ------------

def test_credential_triple_percent_encoded_in_header_value(backend):
    """D5d/F7: triple percent-encoded token in header value must be caught.
    Proves the fixed-point unquote (bounded at 3 passes)."""
    port = backend["port"]
    # Single-encode the last char
    once = TOKEN[:-1] + "%%%02x" % ord(TOKEN[-1])
    # Double-encode: replace each % with %25
    twice = once.replace("%", "%25")
    # Triple-encode: replace each % with %25 again
    triple = twice.replace("%", "%25")
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"X-Trace: {triple}\r\n"
        f"\r\n"
    ).encode()
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) == count_before + 1
    assert TOKEN.encode() not in recs[-1].read_bytes()


# -- D5c: _validate_slow_delay ArgumentTypeError arm (F25) --------------------

def test_slow_delay_argumenttypeerror_arm(tmp_path):
    """D5c F25: --slow-delay with a non-numeric value triggers
    ArgumentTypeError (the ValueError arm in _validate_slow_delay)."""
    tf = tmp_path / "token.env"
    tf.write_text(f"UPSTREAM_TOKEN={TOKEN}\n")
    tf.chmod(0o600)
    proc = subprocess.run(
        [sys.executable, str(SERVER), "--port", str(_free_port()),
         "--token-file", str(tf), "--record-dir", str(tmp_path / "rec"),
         "--slow-delay", "abc"],
        capture_output=True, text=True, timeout=10)
    assert proc.returncode == 2
    assert "invalid float" in proc.stderr


# -- D5c: negative controls — gate arm deletion must cause red ----------------

def test_negative_control_defects_gate_arm(backend):
    """D5c negative control: if the defects gate arm were deleted,
    Content-Length : N (space before colon) would bypass the gate.
    This test asserts the gate fires — gate-deleted mutant would see 200/401."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Length : 0\r\n"
        f"\r\n"
    ).encode() + _forged_tail(port)
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request", \
        "defects gate arm must reject; deletion would let it through"
    assert resp.count(b"HTTP/1.1 ") == 1
    assert b"\r\nConnection: close\r\n" in resp
    assert len(list(backend["rec"].glob("*.json"))) == count_before


def test_negative_control_te_gate_arm(backend):
    """D5c negative control: TE gate arm deletion would let TE: gzip through."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Transfer-Encoding: gzip\r\n"
        f"\r\n"
    ).encode() + _forged_tail(port)
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 411 Length Required", \
        "TE gate arm must reject; deletion would let TE: gzip through"
    assert resp.count(b"HTTP/1.1 ") == 1
    assert len(list(backend["rec"].glob("*.json"))) == count_before


def test_negative_control_dup_cl_gate_arm(backend):
    """D5c negative control: dup CL gate arm deletion would let dup CL through."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: 2\r\n"
        f"Content-Length: 2\r\n"
        f"\r\n"
        f"{{}}"
    ).encode() + _forged_tail(port)
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request", \
        "dup CL gate arm must reject; deletion would process first CL"
    assert resp.count(b"HTTP/1.1 ") == 1
    assert len(list(backend["rec"].glob("*.json"))) == count_before


def test_negative_control_cl_format_gate_arm(backend):
    """D5c negative control: CL format gate arm deletion would let
    Content-Length: -1 through (int() accepts it, cl < 0 bypasses cl > 0 on GET)."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Length: -1\r\n"
        f"\r\n"
    ).encode() + _forged_tail(port)
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request", \
        "CL format gate arm must reject; deletion would let -1 through on GET"
    assert resp.count(b"HTTP/1.1 ") == 1
    assert len(list(backend["rec"].glob("*.json"))) == count_before


def test_negative_control_get_cl_body_gate_arm(backend):
    """D5c negative control: GET CL>0 gate arm deletion would serve GET with body."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Length: 5\r\n"
        f"\r\n"
        f"XXXXX"
    ).encode() + _forged_tail(port)
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request", \
        "GET CL>0 gate arm must reject; deletion would serve the request"
    assert resp.count(b"HTTP/1.1 ") == 1
    assert len(list(backend["rec"].glob("*.json"))) == count_before


def test_post_cl_overmax_ordering_beats_expect(backend):
    """D5c/M18: CL > MAX + Expect: 100-continue -> 400 (not 417).
    Proves the CL > MAX arm fires before the Expect arm (ordering)."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: 2000000\r\n"
        f"Expect: 100-continue\r\n"
        f"\r\n"
    ).encode() + _forged_tail(port)
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request", \
        "CL > MAX must fire before Expect (400, not 417)"
    assert resp.count(b"HTTP/1.1 ") == 1
    assert b"\r\nConnection: close\r\n" in resp
    assert len(list(backend["rec"].glob("*.json"))) == count_before


def test_negative_control_expect_gate_arm(backend):
    """D5c negative control: Expect gate arm deletion would send 100-continue
    (or let the request through to routing)."""
    port = backend["port"]
    count_before = len(list(backend["rec"].glob("*.json")))
    raw = (
        f"GET /v1/models HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{port}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Expect: 100-continue\r\n"
        f"\r\n"
    ).encode() + _forged_tail(port)
    resp = _raw_request(port, raw)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 417 Expectation Failed", \
        "Expect gate arm must reject; deletion would send 100-continue"
    assert resp.count(b"HTTP/1.1 ") == 1
    assert b"\r\nConnection: close\r\n" in resp
    assert len(list(backend["rec"].glob("*.json"))) == count_before
