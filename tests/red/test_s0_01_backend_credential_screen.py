"""VERIFY-D5c (round 7, 2026-09-06) RED tests for the scripted backend's credential screen + allow-list gate.

Findings R7-D5c-F1/F2/F6/F7 are open defects: their tests carry a STRICT xfail marker so CI stays green while the
defect is open and turns red the moment the fix lands without the marker being removed (pre-mint gate, AF-AP-36).
Lane D5d makes them green by fixing proofs/S0-01/tools/scripted_backend.py and REMOVING the markers — never by
editing the assertions. F3/F4/F5 are the verifier's missing controls (mutants M48/M41/M20 survived without them):
they pass today and must keep passing. Self-contained: own backend fixture, own raw-socket helper, tmp_path only.
"""
import http.client
import json
import pathlib
import re
import socket
import subprocess
import sys
import time
from urllib.parse import unquote

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SERVER = ROOT / "proofs" / "S0-01" / "tools" / "scripted_backend.py"
TOKEN = "s0-01-upstream-token-0123456789abcdef"
MARKER = {"credential_in_unexpected_location": True}
MAX_CONTENT_LENGTH = int(re.search(r"^MAX_CONTENT_LENGTH\s*=\s*([0-9_]+)", SERVER.read_text(), re.M).group(1))


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def backend(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("backend-red")
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
    yield {"port": port, "rec": tmp / "rec"}
    proc.terminate()
    proc.wait(timeout=10)


def _raw(port, raw_bytes, timeout=5.0):
    """Send raw bytes in ONE sendall (request + forged tail) and return everything the server sends back."""
    with socket.create_connection(("127.0.0.1", port), timeout=timeout) as s:
        s.sendall(raw_bytes)
        chunks = []
        while True:
            try:
                data = s.recv(65536)
            except socket.timeout:
                break
            if not data:
                break
            chunks.append(data)
    return b"".join(chunks)


def _records(backend):
    return sorted(backend["rec"].glob("*.json"))


def _last_record_text(backend):
    return _records(backend)[-1].read_text()


TAIL = b"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\nContent-Length: 2\r\n\r\n{}"


def _post(port, body: bytes, extra_headers: str = "", tail: bytes = b""):
    return (f"POST /v1/chat/completions HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
            f"Authorization: Bearer {TOKEN}\r\nContent-Type: application/json\r\n{extra_headers}"
            f"Content-Length: {len(body)}\r\n\r\n").encode() + body + tail


def _absent_under_all_normalizations(text: str) -> bool:
    stripped = re.sub(r"\s+", "", text)
    return all(TOKEN not in form for form in (text, unquote(text), stripped, unquote(stripped), unquote(unquote(text))))


# ---- R7-D5c-F1 (BLOCKING): a whitespace-split token inside a VALID JSON body is recorded verbatim ---------------
@pytest.mark.xfail(strict=True, reason="R7-D5c-F1: raw body not screened on the valid-JSON POST path (json.dumps re-escapes the separator)")
@pytest.mark.parametrize("sep", ["\t", "\n", "\r", "\f", "\v"], ids=["TAB", "LF", "CR", "FF", "VT"])
def test_credential_whitespace_split_in_valid_json_body_returns_400(backend, sep):
    port = backend["port"]
    mid = len(TOKEN) // 2
    n0 = len(_records(backend))
    body = json.dumps({"model": "s0-01-pong", "messages": [], "note": TOKEN[:mid] + sep + TOKEN[mid:]}).encode()
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())


# ---- R7-D5c-F2 (BLOCKING): the Expect arm tests truthiness, not presence ---------------------------------------
@pytest.mark.parametrize("value", [
    pytest.param("", marks=pytest.mark.xfail(strict=True, reason="R7-D5c-F2: `Expect:` (empty) is present but falsy — served with the tail")),
    "bogus", "100-Continue", "100-continue",
])
@pytest.mark.parametrize("method", ["GET", "POST"])
def test_expect_header_any_value_rejected_417(backend, method, value):
    port = backend["port"]
    n0 = len(_records(backend))
    path = "/v1/models" if method == "GET" else "/v1/chat/completions"
    body = b"" if method == "GET" else b"{}"
    req = (f"{method} {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nAuthorization: Bearer {TOKEN}\r\n"
           f"Expect: {value}\r\nContent-Length: {len(body)}\r\n\r\n").encode() + body + TAIL
    resp = _raw(port, req)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 417 Expectation Failed"
    assert resp.count(b"HTTP/1.1 ") == 1
    assert b"\r\nConnection: close\r\n" in resp
    assert len(_records(backend)) == n0


# ---- R7-D5c-F3 (control that kills mutant M48): the Authorization exemption is by exact NAME only ---------------
@pytest.mark.parametrize("name", ["Authorization-X", "Authorizationfoo", "X-Authorization"])
def test_authorization_prefixed_header_name_is_not_exempt(backend, name):
    port = backend["port"]
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, b"{}", extra_headers=f"{name}: Bearer {TOKEN}\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert TOKEN.encode() not in recs[-1].read_bytes()


# ---- R7-D5c-F4 (control that kills mutant M41): percent-encoded AND whitespace-split token in a header value ----
def test_credential_percent_encoded_and_whitespace_split_in_header_value(backend):
    port = backend["port"]
    n0 = len(_records(backend))
    enc = TOKEN[:-1] + "%%%02x" % ord(TOKEN[-1])
    k = len(enc) // 2
    val = enc[:k] + " \t " + enc[k:]
    resp = _raw(port, _post(port, b"{}", extra_headers=f"X-Trace: {val}\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())


# ---- R7-D5c-F5 (control that kills mutant M20): Content-Length == MAX is ACCEPTED on POST ----------------------
def test_post_content_length_exactly_max_is_accepted(backend):
    port = backend["port"]
    n0 = len(_records(backend))
    core = json.dumps({"model": "s0-01-pong", "messages": [{"role": "user", "content": "hi"}]}).encode()
    body = core + b" " * (MAX_CONTENT_LENGTH - len(core))
    assert len(body) == MAX_CONTENT_LENGTH
    resp = _raw(port, _post(port, body), timeout=20.0)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 200 OK"
    assert len(_records(backend)) == n0 + 1


# ---- R7-D5c-F6: an obs-folded header hiding a framing header passes the allow-list ------------------------------
@pytest.mark.xfail(strict=True, reason="R7-D5c-F6: obs-fold (RFC 9112 §5.2) is neither rejected nor unfolded — the folded Content-Length/Transfer-Encoding is invisible to the gate")
@pytest.mark.parametrize("folded", ["Content-Length: 5", "Transfer-Encoding: chunked"], ids=["CL", "TE"])
def test_obs_folded_header_rejected_400(backend, folded):
    port = backend["port"]
    n0 = len(_records(backend))
    req = (f"GET /v1/models HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nAuthorization: Bearer {TOKEN}\r\n"
           f"X-Foo: bar\r\n {folded}\r\n\r\n").encode() + TAIL
    resp = _raw(port, req)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert resp.count(b"HTTP/1.1 ") == 1
    assert b"\r\nConnection: close\r\n" in resp
    assert len(_records(backend)) == n0


# ---- R7-D5c-F7: a double percent-encoded token defeats the single-unquote screen -------------------------------
@pytest.mark.xfail(strict=True, reason="R7-D5c-F7: one unquote pass; the token is recovered by a second pass over the record")
def test_credential_double_percent_encoded_in_header_value_returns_400(backend):
    port = backend["port"]
    n0 = len(_records(backend))
    once = TOKEN[:-1] + "%%%02x" % ord(TOKEN[-1])
    twice = once.replace("%", "%25")
    resp = _raw(port, _post(port, b"{}", extra_headers=f"X-Trace: {twice}\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())
