"""VERIFY-D5c (round 7, 2026-09-06) RED tests for the scripted backend's credential screen + allow-list gate.

Findings R7-D5c-F1/F2/F6/F7 are now fixed (lane D5d). The xfail markers have been removed; all tests pass.
F3/F4/F5 are the verifier's missing controls (mutants M48/M41/M20 survived without them):
they pass and must keep passing. F3/F4/F5 are the verifier's missing controls (mutants M48/M41/M20 survived without them):
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
from urllib.parse import unquote, unquote_plus

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
    """F2: STRICTLY WIDER oracle than the backend's _normal_forms.

    Enumerates every word over {unquote, strip_ws, lower, unquote_plus} up to
    length 4 (a different lattice, more operators, its own code — never imports
    the backend's helper). Asserts the token absent under all of them.
    """
    strip_ws = lambda x: re.sub(r"\s+", "", x)
    ops = (unquote, strip_ws, str.lower, unquote_plus)
    forms = {text}
    frontier = {text}
    for _depth in range(4):
        new_frontier = set()
        for form in frontier:
            for op in ops:
                v = op(form)
                if v not in forms:
                    forms.add(v)
                    new_frontier.add(v)
        if not new_frontier:
            break
        frontier = new_frontier
    return all(TOKEN not in form for form in forms)


# ---- R7-D5c-F1 (BLOCKING): a whitespace-split token inside a VALID JSON body is recorded verbatim ---------------
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
    "",
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
@pytest.mark.parametrize("folded,fold_char", [
    ("Content-Length: 5", "\r\n"),
    ("Transfer-Encoding: chunked", "\r\n"),
    ("Content-Length: 5", "\n"),
    ("Transfer-Encoding: chunked", "\n"),
], ids=["CL-CRLF", "TE-CRLF", "CL-LF", "TE-LF"])
def test_obs_folded_header_rejected_400(backend, folded, fold_char):
    port = backend["port"]
    n0 = len(_records(backend))
    req = (f"GET /v1/models HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nAuthorization: Bearer {TOKEN}\r\n"
           f"X-Foo: bar{fold_char} {folded}\r\n\r\n").encode() + TAIL
    resp = _raw(port, req)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert resp.count(b"HTTP/1.1 ") == 1
    assert b"\r\nConnection: close\r\n" in resp
    assert len(_records(backend)) == n0


# ---- R7-D5c-F7: a double percent-encoded token defeats the single-unquote screen -------------------------------
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


# ---- R8-D5d-F1 (BLOCKING): token split by ENCODED whitespace (%20/%09/%0A/%0d/+) -----------------------------
@pytest.mark.parametrize("sep", ["%20", "%09", "%0A", "%0d", "+"], ids=["%20", "%09", "%0A", "%0d", "PLUS"])
@pytest.mark.parametrize("sink", ["header_value", "json_body_value", "query_string"], ids=["header", "json_body", "query"])
def test_credential_encoded_whitespace_split_returns_400(backend, sep, sink):
    """Token split by encoded whitespace must be caught by the closure screen."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    split_token = TOKEN[:mid] + sep + TOKEN[mid:]
    n0 = len(_records(backend))

    if sink == "header_value":
        resp = _raw(port, _post(port, b"{}", extra_headers=f"X-Trace: {split_token}\r\n"))
    elif sink == "json_body_value":
        body = json.dumps({"model": "s0-01-pong", "messages": [], "note": split_token}).encode()
        resp = _raw(port, _post(port, body))
    else:  # query_string
        resp = _raw(port, (f"GET /v1/models?note={split_token} HTTP/1.1\r\n"
                          f"Host: 127.0.0.1:{port}\r\n"
                          f"Authorization: Bearer {TOKEN}\r\n"
                          f"Content-Length: 0\r\n\r\n").encode())

    status_line = resp.split(b"\r\n", 1)[0]
    assert status_line == b"HTTP/1.1 400 Bad Request", \
        f"[{sink}/{sep}] expected 400, got {status_line!r}"
    recs = _records(backend)
    assert len(recs) == n0 + 1, f"[{sink}/{sep}] expected 1 new record, got {len(recs)-n0}"
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())


# ---- R8-D5d-F5: token split by whitespace inside a JSON KEY ----------------------------------------------------
@pytest.mark.parametrize("sep", ["\t", "\n", "\r", "\f", "\v"], ids=["TAB", "LF", "CR", "FF", "VT"])
def test_credential_whitespace_split_as_json_key_returns_400(backend, sep):
    """Whitespace-split token inside a JSON key must be caught (keys are screened too)."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    key = TOKEN[:mid] + sep + TOKEN[mid:]
    body = json.dumps({"model": "s0-01-pong", "messages": [], key: 1}).encode()
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())


# ---- R8-D5d-F4: QUADRUPLE percent-encoded token must fail closed ----------------------------------------------
def test_credential_quad_percent_encoded_fails_closed(backend):
    """Token encoded four times must still trigger the fail-closed branch (400)."""
    port = backend["port"]
    once = TOKEN[:-1] + "%%%02x" % ord(TOKEN[-1])
    twice = once.replace("%", "%25")
    thrice = twice.replace("%", "%25")
    quad = thrice.replace("%", "%25")
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, b"{}", extra_headers=f"X-Trace: {quad}\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())


# ---- R8-D5d-F6: duplicate JSON key hiding the token in wire bytes only -----------------------------------------
def test_duplicate_json_key_hiding_token_returns_400(backend):
    """A duplicate JSON key where the first value is the token and the second is safe.
    The raw-body screen must catch the token in the wire bytes even though the
    parsed dict keeps only the last value.
    """
    port = backend["port"]
    body = b'{"n":"' + TOKEN.encode() + b'","n":"safe"}'
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())


# ---- R8-D5d-F10: depth-1000 JSON body -> 400 + close, 0 records -------------------------------------------------
def test_depth_1000_json_body_returns_400_no_record(backend):
    """A body nested 1000 deep must trigger RecursionError in _read_body -> 400."""
    port = backend["port"]
    # Build depth-1000 JSON array nesting: [[[[...]]]]
    depth = 1000
    body = b"[" * depth + b"1" + b"]" * depth
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    # No new record should be written for this request
    assert len(_records(backend)) == n0


# ---- R8-D5d-F11: NaN/Infinity body coerced to "<non-finite>" ----------------------------------------------------
def test_non_finite_float_body_coerced_and_recorded(backend):
    """A body containing NaN/Infinity must be recorded with allow_nan=False;
    the record must parse under parse_constant=raise."""
    port = backend["port"]
    # Python's json.dumps emits NaN/Infinity by default (allow_nan=True)
    body = json.dumps({"model": "s0-01-pong", "messages": [], "x": float("nan"), "y": float("inf")}).encode()
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, body))
    # The request itself is screened for the token; since it doesn't carry one it should 200
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 200 OK"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    rec_text = recs[-1].read_text()
    # The record must parse under parse_constant=raise (no bare NaN/Infinity)
    def _raise(x):
        raise ValueError(f"non-finite constant in record: {x}")
    rec = json.loads(rec_text, parse_constant=_raise)
    assert rec["body"]["x"] == "<non-finite>"
    assert rec["body"]["y"] == "<non-finite>"
