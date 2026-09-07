"""VERIFY-D5c (round 7, 2026-09-06) RED tests for the scripted backend's credential screen + allow-list gate.

Findings R7-D5c-F1/F2/F6/F7 are now fixed (lane D5d). The xfail markers have been removed; all tests pass.
F3/F4/F5 are the verifier's missing controls (mutants M48/M41/M20 survived without them):
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
import unicodedata
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


_INVIS_CATEGORIES = frozenset({"Cf", "Cs", "Cc", "Mn", "Me", "Zs", "Zl", "Zp"})
_INVISIBLE_EXTRA = frozenset({
    chr(0x115F), chr(0x1160), chr(0x3164), chr(0xFFA0),
    chr(0x2800), chr(0x180E),
})


def _absent_under_all_normalizations(text: str) -> bool:
    """F2: STRICTLY WIDER oracle than the backend's _normal_forms.

    Enumerates every word over {unquote, unquote_plus, lower,
    utf8_redecode_lenient, strip_invis} up to depth 6 (the backend uses
    depth 5 with the same operators plus utf8_redecode strict; this oracle
    goes one depth level further).  Never imports the backend's helper.
    strip_invis drops every code point whose unicodedata.category is in
    {Cf, Cs, Cc, Mn, Me, Zs, Zl, Zp} plus _INVISIBLE_EXTRA (Lo/So fillers
    and MVS) — subsumes the former strip_ws, strip_zwc, and strip_ctl
    (all fully redundant, removed D5i).
    utf8_redecode_lenient: encode("latin-1").decode("utf-8", errors="ignore");
    strictly wider than the impl's strict utf8_redecode.
    ``unquote`` is redundant with ``unquote_plus`` only for a token
    containing no ``+``; it stays so the oracle is token-agnostic (D5h-F12).
    Seeds with json.loads of every JSON string literal (F4/F7).
    """
    def strip_invis(x):
        return "".join(c for c in x
                       if unicodedata.category(c) not in _INVIS_CATEGORIES
                       and c not in _INVISIBLE_EXTRA)
    def utf8_redecode_lenient(x):
        try:
            return x.encode("latin-1").decode("utf-8", errors="ignore")
        except UnicodeEncodeError:
            return x
    ops = (unquote, unquote_plus, str.lower, utf8_redecode_lenient, strip_invis)
    # F4: seed with JSON-unescaped text of every JSON string literal
    forms = {text}
    for m in re.findall(r'"(?:[^"\\]|\\.)*"', text):
        try:
            forms.add(json.loads(m))
        except (ValueError, json.JSONDecodeError):
            pass
    frontier = set(forms)
    for _depth in range(6):
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
def test_credential_quad_percent_encoded_at_depth4(backend):
    """Token encoded four times reaches the token at closure depth 4 (400)."""
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
_MJD_MATCH = re.search(r"^MAX_JSON_DEPTH\s*=\s*([0-9_]+)", SERVER.read_text(), re.M)
if _MJD_MATCH is None:
    pytest.fail("MAX_JSON_DEPTH missing from the backend")
MAX_JSON_DEPTH = int(_MJD_MATCH.group(1))


def _nested_note_body(depth: int) -> bytes:
    """A valid chat body whose `note` value is nested `depth` levels deep (the outer object is level 1)."""
    inner = "[" * (depth - 1) + "1" + "]" * (depth - 1)
    return ('{"model": "s0-01-pong", "messages": [{"role": "user", "content": "hi"}], "note": ' + inner + "}").encode()


def test_json_depth_over_limit_returns_400_no_record(backend):
    """CI runs 87-89 (Python 3.12): depth 1000 parsed fine and the handler crashed later with NO response; the bound
    must come from a raw-byte scan, not from the interpreter's recursion limit — depth MAX+1 is a 400 on every venue."""
    port = backend["port"]
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, _nested_note_body(MAX_JSON_DEPTH + 1), tail=TAIL))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert resp.count(b"HTTP/1.1 ") == 1
    assert b"\r\nConnection: close\r\n" in resp
    assert len(_records(backend)) == n0


def test_json_depth_at_limit_is_served(backend):
    """The bound is exact: depth MAX is an ordinary request (200 + one record) — the gate must not fire early."""
    port = backend["port"]
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, _nested_note_body(MAX_JSON_DEPTH)))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 200 OK"
    assert len(_records(backend)) == n0 + 1


def test_depth_1000_json_body_returns_400_no_record(backend):
    """A body nested 1000 deep is refused by the depth gate (400, no record)."""
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


# ---- ORACLE SELF-TESTS (ruling 2): prove the oracle is not a tautology -----------

class TestOracleSelfTests:
    """The oracle must return False on known-bad inputs and True on known-good ones.
    If the oracle is mutated to ``return True``, the False assertions fail."""

    @pytest.mark.parametrize("text,expected", [
        # Known-bad: oracle must detect the token (return False)
        ("s0-01-upstream-tok%20en-0123456789abcdef-%25252541", False),
        ("s0-01-upstream-tok%25252520en-0123456789abcdef", False),
        (TOKEN.upper(), False),
        ("s0-01-upstream-tok​en-0123456789abcdef", False),
        ("s0-01-upstream-tok\ten-0123456789abcdef", False),
        # F6: + axis
        (TOKEN[:len(TOKEN)//2] + "+" + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + "%2B" + TOKEN[len(TOKEN)//2:], False),
        # F4: record-shaped JSON with escaped separator
        ('{"body": "s0-01-upstream-tok\\ten-0123456789abcdef"}', False),
        # D5h-F3: utf8_redecode_lenient on valid UTF-8 (latin-1 view of UTF-8 ZWSP between halves)
        (TOKEN[:len(TOKEN)//2] + bytes([0xE2, 0x80, 0x8B]).decode("latin-1") + TOKEN[len(TOKEN)//2:], False),
        # D5h-F3: utf8_redecode_lenient on invalid UTF-8 (ZWSP + one junk byte)
        (TOKEN[:len(TOKEN)//2] + bytes([0xE2, 0x80, 0x8B, 0x80]).decode("latin-1") + TOKEN[len(TOKEN)//2:], False),
        # D5h-F13: strip_ctl self-test (U+0085 = NEL, a C1 control)
        (TOKEN[:len(TOKEN)//2] + chr(0x85) + TOKEN[len(TOKEN)//2:], False),
        # D5h-F13: strip_ctl self-test (U+007F = DEL)
        (TOKEN[:len(TOKEN)//2] + chr(0x7F) + TOKEN[len(TOKEN)//2:], False),
        # D5i: strip_invis self-tests (invisible separators by category)
        (TOKEN[:len(TOKEN)//2] + chr(0x200C) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x200E) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x2800) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x3164) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0xFE00) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x0301) + TOKEN[len(TOKEN)//2:], False),
        # Known-good: oracle must NOT detect the token (return True)
        ('{"credential_in_unexpected_location": true}', True),
        ("Mozilla/5.0 (X11; Linux x86_64)", True),
        ("%25252540", True),
    ], ids=["junk_suffix", "depth5_nesting", "uppercased", "zwsp_split",
            "tab_split", "plus_split", "pct2b_split", "json_escaped_tab",
            "raw_utf8_mojibake", "raw_utf8_mojibake_junk",
            "c1_control_split", "del_split",
            "zwnj_split", "lrm_split", "braille_split",
            "hangul_filler_split", "vs1_split", "combining_split",
            "marker_record", "user_agent", "junk_alone"])
    def test_oracle_known_vectors(self, text, expected):
        assert _absent_under_all_normalizations(text) is expected


# ---- F1/F3: trailing nested escape with separator (5 seps x 3 sinks) -------------

@pytest.mark.parametrize("sep", ["%20", "%09", "%0A", "%0d", "+"], ids=["%20", "%09", "%0A", "%0d", "PLUS"])
@pytest.mark.parametrize("sink", ["header_value", "json_body_value", "query_string"], ids=["header", "json_body", "query"])
def test_credential_split_with_trailing_nested_escape_returns_400(backend, sep, sink):
    """F1: a 9-char suffix (%25252541) that pushes the closure past depth 5 must not
    disable the credential screen — the screen fails closed when the bound is exceeded."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    split_token = TOKEN[:mid] + sep + TOKEN[mid:] + "-%25252541"
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
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())


# ---- F1: depth-5 percent nesting in all sinks -----------------------------------

@pytest.mark.parametrize("vector", [
    "%25252520",
    "%2525252520",
    "%25252B",
    "%2+B",
], ids=["d5_space", "d6_space", "d5_plus", "d5_plus_alt"])
@pytest.mark.parametrize("sink", [
    "header_value", "header_name", "query", "path", "json_value", "json_key",
], ids=["header", "header_name", "query", "path", "json_val", "json_key"])
def test_credential_depth5_percent_nesting_returns_400(backend, vector, sink):
    """Depth-5+ percent-nesting of the token separator must be caught.
    F8: header_name included -- %, + and digits are RFC 9110 tchar; no parser
    interaction (the lane's stated reason for omitting it was false)."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    split_token = TOKEN[:mid] + vector + TOKEN[mid:]
    n0 = len(_records(backend))
    VALID = b'{"model":"s0-01-pong","messages":[]}'

    if sink == "header_value":
        resp = _raw(port, _post(port, b"{}", extra_headers=f"X-Trace: {split_token}\r\n"))
    elif sink == "header_name":
        resp = _raw(port, _post(port, VALID, extra_headers=f"X-{split_token}: v\r\n"))
    elif sink == "query":
        resp = _raw(port, (f"GET /v1/models?note={split_token} HTTP/1.1\r\n"
                          f"Host: 127.0.0.1:{port}\r\n"
                          f"Authorization: Bearer {TOKEN}\r\n"
                          f"Content-Length: 0\r\n\r\n").encode())
    elif sink == "path":
        resp = _raw(port, (f"GET /v1/models/{split_token} HTTP/1.1\r\n"
                          f"Host: 127.0.0.1:{port}\r\n"
                          f"Authorization: Bearer {TOKEN}\r\n"
                          f"Content-Length: 0\r\n\r\n").encode())
    elif sink == "json_value":
        body = json.dumps({"model": "s0-01-pong", "messages": [], "note": split_token}).encode()
        resp = _raw(port, _post(port, body))
    else:  # json_key
        body = json.dumps({"model": "s0-01-pong", "messages": [], split_token: 1}).encode()
        resp = _raw(port, _post(port, body))

    status_line = resp.split(b"\r\n", 1)[0]
    assert status_line == b"HTTP/1.1 400 Bad Request", \
        f"[{sink}/{vector}] expected 400, got {status_line!r}"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())


# ---- F8: whitespace-split token in a JSON list element (kills MC9) ---------------

@pytest.mark.parametrize("sep", ["\t", "\n", "\r", "\f", "\v"], ids=["TAB", "LF", "CR", "FF", "VT"])
def test_credential_whitespace_split_in_json_list_element_returns_400(backend, sep):
    """F8: token split by whitespace inside a JSON list element must be caught."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    n0 = len(_records(backend))
    body = json.dumps({"model": "s0-01-pong", "messages": [],
                       "n": ["x", TOKEN[:mid] + sep + TOKEN[mid:]]}).encode()
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())


# ---- F12: JSON depth gate handles brackets inside strings (kills MG4/MG5) --------

def test_json_depth_ignores_brackets_inside_strings(backend):
    """40 '[' inside a JSON string value must not inflate the depth count (kills MG4)."""
    port = backend["port"]
    n0 = len(_records(backend))
    body = ('{"model": "s0-01-pong", "messages": [{"role": "user", "content": "hi"}], '
            '"note": "' + '[' * 40 + '"}').encode()
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 200 OK"
    assert len(_records(backend)) == n0 + 1


def test_json_depth_handles_escaped_quote(backend):
    r"""An escaped quote (q\") followed by 40 '[' stays inside the string (kills MG5)."""
    port = backend["port"]
    n0 = len(_records(backend))
    body = b'{"model":"s0-01-pong","messages":[{"role":"user","content":"hi"}],"note":"q\\"' + b'[' * 40 + b'"}'
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 200 OK"
    assert len(_records(backend)) == n0 + 1


# ---- F14: uppercased token (kills str.lower omission) ----------------------------

def test_credential_uppercased_token_in_header_returns_400(backend):
    """F14: an uppercased token (recoverable by str.lower) must be caught."""
    port = backend["port"]
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, b"{}", extra_headers=f"X-Trace: {TOKEN.upper()}\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())


# ---- F15: zero-width separators -------------------------------------------------

@pytest.mark.parametrize("vector,name", [
    ("%E2%80%8B", "ZWSP"),
    ("%EF%BB%BF", "BOM"),
    ("%C2%AD", "SOFT_HYPHEN"),
], ids=["ZWSP", "BOM", "SOFT_HYPHEN"])
def test_credential_zero_width_pct_encoded_returns_400(backend, vector, name):
    """F15: percent-encoded zero-width char splitting the token must be caught."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    split_token = TOKEN[:mid] + vector + TOKEN[mid:]
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, b"{}", extra_headers=f"X-Trace: {split_token}\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())


def test_credential_zero_width_json_escape_returns_400(backend):
    r"""F15: JSON-escaped ​ splitting the token must be caught."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    body = (b'{"model":"s0-01-pong","messages":[],"note":"'
            + TOKEN[:mid].encode() + b'\\u200b' + TOKEN[mid:].encode() + b'"}')
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER
    assert _absent_under_all_normalizations(recs[-1].read_text())


# ---- R9-D5g-F1: keep `seen` -------

def test_credential_plus_split_with_pct2520_suffix_returns_400(backend):
    """Pins ruling 1's 'keep seen': the token is found at an INTERMEDIATE closure
    layer, not the final one.  Red if _normal_forms returns only the last frontier
    (mutant V3)."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    vec = TOKEN[:mid] + "+" + TOKEN[mid:] + "%2520"
    resp = _raw(port, _post(port, b'{"model":"s0-01-pong","messages":[]}',
                            extra_headers=f"X-Trace: {vec}\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert json.loads(_records(backend)[-1].read_text())["body"] == MARKER


# ---- R9-D5g-F2: raw UTF-8 zero-width separator ------

@pytest.mark.parametrize("sep", [
    "​", "﻿", "­", "⁠", " ", "　",
], ids=["ZWSP", "BOM", "SOFT_HYPHEN", "WORD_JOINER", "NBSP", "IDEOGRAPHIC_SPACE"])
def test_credential_raw_utf8_zero_width_in_header_returns_400(backend, sep):
    """F2/F15 'raw': the separator arrives as UTF-8 BYTES on the wire;
    http.server decodes header lines as latin-1, producing 2-3 latin-1 chars
    that neither strip_ws nor strip_zwc touches without utf8_redecode."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    body = b'{"model":"s0-01-pong","messages":[]}'
    payload = (f"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\n"
               f"Authorization: Bearer {TOKEN}\r\nContent-Type: application/json\r\n"
               f"X-Trace: ").encode() + TOKEN[:mid].encode() + sep.encode("utf-8") \
              + TOKEN[mid:].encode() + f"\r\nContent-Length: {len(body)}\r\n\r\n".encode() + body
    resp = _raw(port, payload)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert json.loads(_records(backend)[-1].read_text())["body"] == MARKER


# ---- R9-D5g-F5: ruling 2(b) ----

def test_record_text_carries_no_token_under_any_normalization(backend):
    """A TAB-split request must be caught, and the RECORD TEXT must pass the oracle.
    Asserts ONLY the oracle -- no == MARKER check.  The negative control (the oracle
    DETECTS the token in the raw input) ensures O1 (oracle -> return True) kills this
    test: `not True` -> False."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    raw_input = TOKEN[:mid] + "\t" + TOKEN[mid:]
    n0 = len(_records(backend))
    body = json.dumps({"model": "s0-01-pong", "messages": [],
                       "note": raw_input}).encode()
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert not _absent_under_all_normalizations(raw_input)
    assert _absent_under_all_normalizations(recs[-1].read_text())


# ---- D5h-F1: invalid UTF-8 separator in header -> 400 (fail closed) ----

@pytest.mark.parametrize("sep", [
    bytes([0xE2, 0x80, 0x80, 0x80]),
    bytes([0xC2, 0xA0, 0x80]),
    bytes([0xC0, 0xA0]),
    bytes([0x80]),
], ids=["enquad_plus_junk", "nbsp_plus_junk", "overlong_space", "lone_continuation"])
def test_credential_invalid_utf8_separator_in_header_returns_400(backend, sep):
    """D5h-F1: invalid UTF-8 bytes in the latin-1 view of a header value must
    fail closed (400 + MARKER + Connection: close).  The PIN's implementation
    failed open on these (200 OK, verbatim record)."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    body = b'{"model":"s0-01-pong","messages":[]}'
    payload = (f"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\n"
               f"Authorization: Bearer {TOKEN}\r\nContent-Type: application/json\r\n"
               f"X-Trace: ").encode() + TOKEN[:mid].encode() + sep \
              + TOKEN[mid:].encode() + f"\r\nContent-Length: {len(body)}\r\n\r\n".encode() + body
    n0 = len(_records(backend))
    resp = _raw(port, payload)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


# ---- D5h-F1: invalid UTF-8 separator via JSON escapes in body ----

@pytest.mark.parametrize("json_sep,sep_id", [
    # U+0080 is a C1 control; its latin-1 byte 0x80 is a lone continuation byte
    ("\\u0080", "u0080"),
    # U+00C0 U+00A0: their latin-1 view is bytes 0xC0 0xA0 (overlong encoding of space)
    ("\\u00c0\\u00a0", "u00c0_u00a0"),
    # U+00E2 U+0080 U+0080 U+0080: latin-1 view = 0xE2 0x80 0x80 0x80 (valid 3-byte + junk)
    ("\\u00e2\\u0080\\u0080\\u0080", "u00e2_u0080_u0080_u0080"),
], ids=["u0080", "overlong_pair", "enquad_plus_junk"])
def test_credential_invalid_utf8_separator_in_json_body_returns_400(backend, json_sep, sep_id):
    """D5h-F1 JSON twin: JSON escapes that decode to characters whose latin-1
    view contains invalid UTF-8 must fail closed."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    body = (b'{"model":"s0-01-pong","messages":[],"note":"'
            + TOKEN[:mid].encode() + json_sep.encode() + TOKEN[mid:].encode() + b'"}')
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


# ---- D5h-F13: control characters in header -> 400 ----

@pytest.mark.parametrize("ctl_char", [chr(0x7F), chr(0x01)], ids=["DEL", "SOH"])
def test_credential_control_char_in_header_value_returns_400(backend, ctl_char):
    """D5h-F13: control characters (DEL, C0) splitting the token in a header
    value must be caught by strip_ctl."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    split_token = TOKEN[:mid] + ctl_char + TOKEN[mid:]
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, b"{}", extra_headers=f"X-Trace: {split_token}\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


# ---- D5h-F13: control characters via JSON escapes in body -> 400 ----

@pytest.mark.parametrize("json_sep,sep_id", [
    ("\\u007f", "DEL"),
    ("\\u0001", "SOH"),
], ids=["DEL", "SOH"])
def test_credential_control_char_in_json_body_returns_400(backend, json_sep, sep_id):
    """D5h-F13 JSON twin: JSON-escaped control characters splitting the token
    must be caught by strip_invis in the parsed-JSON-string walk."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    body = (b'{"model":"s0-01-pong","messages":[],"note":"'
            + TOKEN[:mid].encode() + json_sep.encode() + TOKEN[mid:].encode() + b'"}')
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


# ---- D5h-F4: unquote op is required for the bound ----

def test_unquote_op_is_required_for_the_bound(backend):
    """%252520%252B fails to saturate at depth 5 only because unquote is in
    the op set.  Mutant M_UQ_DEL dies on this test."""
    port = backend["port"]
    resp = _raw(port, _post(port, b'{"model":"s0-01-pong","messages":[]}',
                            extra_headers="X-Trace: %252520%252B\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert json.loads(_records(backend)[-1].read_text())["body"] == MARKER


# ---- D5h-F5: raw non-ASCII header name -> 400 by gate, no record ----

def test_raw_non_ascii_header_name_rejected_by_gate_no_record(backend):
    """Raw non-ASCII bytes in a header NAME produce 400 with zero records:
    the email parser reports MissingHeaderBodySeparatorDefect, so _framing_gate
    arm 1 rejects before state.record is ever called."""
    port = backend["port"]
    n0 = len(_records(backend))
    body = b'{"model":"s0-01-pong","messages":[]}'
    # 0xC2 0xA0 in header name -> email parser defect -> gate 400
    header_name_bytes = b"X-" + bytes([0xC2, 0xA0]) + b"Test"
    payload = (b"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\n"
               b"Authorization: Bearer " + TOKEN.encode() + b"\r\n"
               b"Content-Type: application/json\r\n"
               + header_name_bytes + b": value\r\n"
               b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body)
    resp = _raw(port, payload)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    assert b"\r\nConnection: close\r\n" in resp
    assert len(_records(backend)) == n0  # zero new records


# ---- D5i-F1: ordinary accented text in a JSON body must be served (not rejected) ----

@pytest.mark.parametrize("content", [
    "caf" + chr(0xE9), chr(0x4D) + chr(0xFC) + "ller",
    "se" + chr(0xF1) + "or", chr(0xA3) + "100",
    "50" + chr(0xB0) + "C", chr(0xA9) + " 2026",
], ids=["e_acute", "u_uml", "n_tilde", "pound", "degree", "copyright"])
def test_ordinary_latin1_text_in_json_body_is_served(backend, content):
    """D5h-F1 / D5i item 1: a well-formed UTF-8 body carrying no credential
    must not be rejected.  RED on the PIN (the precheck re-encodes an
    already-decoded JSON leaf to latin-1 and falsely rejects it)."""
    port = backend["port"]
    body = json.dumps({"model": "s0-01-pong", "messages": [
        {"role": "user", "content": content}]}, ensure_ascii=False).encode("utf-8")
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 200 OK"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"]["messages"][0]["content"] == content


# ---- D5i-F2: invisible separator in header -> 400 (closed by category) ----

@pytest.mark.parametrize("cp", [0x200C, 0x200D, 0x200E, 0x200F, 0x2800, 0x3164, 0xFE00, 0x180E],
                         ids=["ZWNJ", "ZWJ", "LRM", "RLM", "BRAILLE_BLANK", "HANGUL_FILLER", "VS1", "MVS"])
def test_credential_invisible_separator_in_header_returns_400(backend, cp):
    """D5h-F2 / D5i item 3: invisible separators (closed by Unicode category,
    not by a hand-written list) must be caught.  RED on the PIN (strip_zwc
    covers only U+200B/FEFF/AD/2060; these are outside that set)."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    body = b'{"model":"s0-01-pong","messages":[]}'
    payload = (b"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\n"
               b"Authorization: Bearer " + TOKEN.encode() + b"\r\n"
               b"Content-Type: application/json\r\nX-Trace: "
               + TOKEN[:mid].encode() + chr(cp).encode("utf-8") + TOKEN[mid:].encode()
               + b"\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body)
    n0 = len(_records(backend))
    resp = _raw(port, payload)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


# ---- D5i-F2: invisible separator via JSON escapes in body ----

@pytest.mark.parametrize("cp,cp_id", [
    (0x200C, "ZWNJ"), (0x200D, "ZWJ"), (0x200E, "LRM"),
    (0x0301, "COMBINING_ACUTE"),
], ids=["ZWNJ", "ZWJ", "LRM", "COMBINING_ACUTE"])
def test_credential_invisible_separator_in_json_body_returns_400(backend, cp, cp_id):
    """D5i item 3 JSON twin: invisible separator via JSON \\uNNNN escape
    splitting the token in a JSON body value."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    esc = "\\u%04x" % cp
    body = (b'{"model":"s0-01-pong","messages":[],"note":"'
            + TOKEN[:mid].encode() + esc.encode() + TOKEN[mid:].encode() + b'"}')
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


# ---- D5i-F2: INVIS_LIST_ONLY killer: a vector OUTSIDE the _INVISIBLE_EXTRA list ----

def test_credential_function_application_separator_in_header_returns_400(backend):
    """D5i: U+2061 FUNCTION APPLICATION (category Cf, NOT in _INVISIBLE_EXTRA)
    must be caught by the category check.  Kills INVIS_LIST_ONLY mutant."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    body = b'{"model":"s0-01-pong","messages":[]}'
    payload = (b"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\n"
               b"Authorization: Bearer " + TOKEN.encode() + b"\r\n"
               b"Content-Type: application/json\r\nX-Trace: "
               + TOKEN[:mid].encode() + chr(0x2061).encode("utf-8") + TOKEN[mid:].encode()
               + b"\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body)
    n0 = len(_records(backend))
    resp = _raw(port, payload)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


# ---- D5h-F4: C1 control wire form (valid UTF-8 → only strip_ctl/strip_invis catches it) ----

@pytest.mark.parametrize("cp", [0x80, 0x85, 0x9F], ids=["PAD", "NEL", "APC"])
def test_credential_c1_control_wire_form_returns_400(backend, cp):
    """D5h-F4 / D5i: the UTF-8 wire form of a C1 control is VALID UTF-8, so
    the precheck passes; only strip_invis's Cc arm catches it.  CONTROL:
    kills CTL_PARTIAL_noC1."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    body = b'{"model":"s0-01-pong","messages":[]}'
    payload = (b"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\n"
               b"Authorization: Bearer " + TOKEN.encode() + b"\r\n"
               b"Content-Type: application/json\r\nX-Trace: "
               + TOKEN[:mid].encode() + chr(cp).encode("utf-8") + TOKEN[mid:].encode()
               + b"\r\nContent-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body)
    n0 = len(_records(backend))
    resp = _raw(port, payload)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


# ---- D5h-F5: refuse ≠ repair — invalid UTF-8 WITHOUT the token is still refused ----

def test_invalid_utf8_without_the_token_is_refused_not_repaired(backend):
    """D5h-F5 / D5i: the pinned design REFUSES invalid UTF-8 on byte-view sinks;
    a lenient re-decode would serve this 200.  CONTROL: kills LENIENT_IN_IMPL."""
    port = backend["port"]
    body = b'{"model":"s0-01-pong","messages":[]}'
    payload = (b"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\n"
               b"Authorization: Bearer " + TOKEN.encode() + b"\r\n"
               b"Content-Type: application/json\r\nX-Trace: ua-"
               + bytes([0x80, 0xC0]) + b"-probe\r\nContent-Length: "
               + str(len(body)).encode() + b"\r\n\r\n" + body)
    n0 = len(_records(backend))
    resp = _raw(port, payload)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


# ---- D5h-F14: precheck ordering — _normal_forms not entered for invalid UTF-8 ----

def test_precheck_before_closure_on_invalid_utf8(backend):
    """D5i item 5 / D5h-F14: the precheck fires BEFORE the closure, so
    _normal_forms is never called for an invalid-UTF-8 byte-view input.
    Timing-free: monkeypatches _normal_forms with a counter."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("sb_ordering", str(SERVER))
    sb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sb)
    call_count = [0]
    original_nf = sb._normal_forms

    def counting_nf(s):
        call_count[0] += 1
        return original_nf(s)

    sb._normal_forms = counting_nf
    state = sb.State("tok", pathlib.Path("/dev/null"), 0.0)
    # invalid UTF-8 byte view: 0x80 0xC0 are not valid UTF-8
    s = "ua-" + bytes([0x80, 0xC0]).decode("latin-1") + "-probe"
    result = state._carries_secret(s, byte_view=True)
    assert result is True, "invalid UTF-8 byte view must return True"
    assert call_count[0] == 0, (
        f"_normal_forms was called {call_count[0]} times; precheck should short-circuit"
    )
