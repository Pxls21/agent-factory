"""proofs/S0-01/tools/scripted_backend.py — the golden's deterministic upstream (stdlib server).

Spawns the real server under sys.executable on an ephemeral port, then proves: bearer required (401
exact body), models list, non-stream and stream completions byte-identical across repeated calls,
the slow model's chunking, unknown model / bad body errors, request recording with the bearer
reduced to a fingerprint, and that the token never appears in argv.
"""
from __future__ import annotations

import http.client
import json
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "proofs" / "S0-01" / "tools" / "scripted_backend.py"
TOKEN = "s0-01-upstream-token-0123456789abcdef"


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


def _call(port, method, path, body=None, token=TOKEN, stream=False):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=15)
    headers = {"Content-Type": "application/json"}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
    conn.request(method, path, body=json.dumps(body) if body is not None else None, headers=headers)
    resp = conn.getresponse()
    data = resp.read()
    conn.close()
    return resp.status, data


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


def test_requests_are_recorded_with_masked_bearer_and_token_absent_from_argv(backend):
    recs = sorted(backend["rec"].glob("*.json"))
    assert recs, "no request records written"
    last = json.loads(recs[-1].read_text())
    assert last["method"] == "POST" and last["path"] == "/v1/chat/completions"
    auth = {k: v for k, v in last["headers"].items() if k.lower() == "authorization"}
    assert auth and all(v.startswith("<bearer fp=") and TOKEN not in v for v in auth.values())
    assert all(TOKEN not in a for a in backend["argv"])
    assert int(backend["pidfile"].read_text()) == backend["proc"].pid
