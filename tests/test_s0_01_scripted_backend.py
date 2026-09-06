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
            http.client.HTTPConnection("127.0.0.1", port, timeout=1).request("GET", "/v1/models")
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
    assert len(recs) > count_before
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
                        f"must have no group/other bits (0o600 or 0o400)")
        assert expected_msg in proc.stderr


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
    assert len(recs) > count_before
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
    assert len(recs) > count_before
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
    assert count_after > count_before, \
        "S27b mutant: body literal 'BAD_CL' matched the sentinel, no record written"
    # The response should carry the JSON error, not a bare 400+close
    assert b"messages: Expected array" in resp


def test_body_literal_chunked_string_is_not_sentinel(backend):
    """V10/S27: a POST whose JSON body is the string 'CHUNKED' must not collide
    with the _CHUNKED sentinel and must be processed as a normal request."""
    count_before = len(list(backend["rec"].glob("*.json")))
    body_bytes = b'"CHUNKED"'
    raw = (
        f"POST /v1/chat/completions HTTP/1.1\r\n"
        f"Host: 127.0.0.1:{backend['port']}\r\n"
        f"Authorization: Bearer {TOKEN}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"\r\n"
    ).encode() + body_bytes
    resp = _raw_request(backend["port"], raw)
    count_after = len(list(backend["rec"].glob("*.json")))
    assert count_after > count_before, \
        "S27 mutant: body literal 'CHUNKED' matched the sentinel"
    assert b"messages: Expected array" in resp


# -- V11/S28: handler timeout mutant killer ------------------------------------

def test_handler_timeout_bounds_incomplete_body(backend):
    """V11/S28: timeout=30 prevents an incomplete body from blocking forever.
    A client sending headers + partial body but keeping the connection open must
    see the connection close within ~35s (the handler timeout). If timeout is
    removed (S28 mutant), this hangs indefinitely."""
    port = backend["port"]
    s = socket.socket()
    s.settimeout(60)
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
    # Keep connection open — no SHUT_WR — the server must timeout at 30s
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
    except (socket.timeout, ConnectionResetError, BrokenPipeError, OSError):
        pass
    elapsed = time.time() - t0
    s.close()
    assert 20 < elapsed < 50, \
        f"expected ~30s (handler timeout), got {elapsed:.1f}s"
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
    assert len(recs) > count_before
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
    assert len(recs) > count_before
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes, \
        "P1 mutant: token leaked through JSON-error recording path (header)"


def test_malformed_json_with_token_in_body_redacted(backend):
    """P1: malformed-JSON POST with token embedded in the raw body -> 400,
    token NOT in record."""
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
    recs = sorted(backend["rec"].glob("*.json"))
    assert len(recs) > count_before
    last_bytes = recs[-1].read_bytes()
    assert TOKEN.encode() not in last_bytes, \
        "P1 mutant: token leaked through JSON-error recording path (body)"


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
