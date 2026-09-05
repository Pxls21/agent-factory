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
    assert "127.0.0.1" in last["remote_addr"]
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

def test_token_file_mode_0644_refuses_to_start(tmp_path):
    """Negative control: token file with 0644 mode must be rejected (exit 2)."""
    tf = tmp_path / "token.env"
    tf.write_text(f"UPSTREAM_TOKEN={TOKEN}\n")
    tf.chmod(0o644)
    proc = subprocess.run(
        [sys.executable, str(SERVER), "--port", str(_free_port()),
         "--token-file", str(tf), "--record-dir", str(tmp_path / "rec")],
        capture_output=True, text=True, timeout=10)
    assert proc.returncode == 2
    assert "no group/other bits" in proc.stderr


def test_token_file_mode_0400_accepted(tmp_path):
    """V-c F15: 0400 (owner-read-only) must be accepted."""
    tf = tmp_path / "token.env"
    tf.write_text(f"UPSTREAM_TOKEN={TOKEN}\n")
    tf.chmod(0o400)
    port = _free_port()
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
    assert started, "server should start with 0400 token file"


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
    assert "non-empty" in proc.stderr


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
    assert "not a directory" in proc.stderr


def test_missing_token_file_named_refusal(tmp_path):
    """V-d F21: missing --token-file yields exit 2 with named reason, not a traceback."""
    proc = subprocess.run(
        [sys.executable, str(SERVER), "--port", str(_free_port()),
         "--token-file", str(tmp_path / "nonexistent.env"),
         "--record-dir", str(tmp_path / "rec")],
        capture_output=True, text=True, timeout=10)
    assert proc.returncode == 2
    assert "not found" in proc.stderr
    # Must NOT be a Python traceback
    assert "Traceback" not in proc.stderr


def test_chunked_transfer_encoding_rejected_with_411(backend):
    """V-c F11: Transfer-Encoding: chunked must yield 411 and close."""
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
    assert b"411" in resp, f"expected 411 in response, got: {resp[:200]}"


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
    assert b"400" in resp, f"expected 400 in response, got: {resp[:200]}"


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
    assert b"400" in resp, f"expected 400 in response, got: {resp[:200]}"


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


def test_credential_in_extra_header_returns_400(backend):
    """V-c F10: token in x-api-key (a non-authorization credential header) does NOT leak
    because x-api-key is dropped; but token in a custom header value triggers 400."""
    # x-api-key is dropped from the record, so it does not leak; token in another header:
    status, data = _call(backend["port"], "GET", "/v1/models",
                         extra_headers={"X-Custom": TOKEN})
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
    assert "matches" in r2.stdout

    # Tamper with capture.json and verify --check fails
    cj = leg / "capture.json"
    cj.write_text(cj.read_text().replace('"version": 2', '"version": 99'))
    r3 = subprocess.run(
        [sys.executable, str(BUILD_CAPTURE), "--check", str(leg), "test-leg"],
        capture_output=True, text=True, timeout=10)
    assert r3.returncode == 1, f"--check should fail after tamper: {r3.stderr}"
    assert "differs" in r3.stderr
