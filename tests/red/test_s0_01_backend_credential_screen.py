"""VERIFY-D5c (round 7, 2026-09-06) RED tests for the scripted backend's credential screen + allow-list gate.

Findings R7-D5c-F1/F2/F6/F7 are now fixed (lane D5d). The xfail markers have been removed; all tests pass.
F3/F4/F5 are the verifier's missing controls (mutants M48/M41/M20 survived without them):
they pass today and must keep passing. Self-contained: own backend fixture, own raw-socket helper, tmp_path only.
"""
import importlib.util
import json
import pathlib
import re
import socket
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, unquote_plus

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SERVER = ROOT / "proofs" / "S0-01" / "tools" / "scripted_backend.py"
TOKEN = "s0-01-upstream-token-0123456789abcdef"
MARKER = {"credential_in_unexpected_location": True}
MAX_CONTENT_LENGTH = int(re.search(r"^MAX_CONTENT_LENGTH\s*=\s*([0-9_]+)", SERVER.read_text(), re.M).group(1))


# D5m-F4: the failure-aware readiness wait is ONE helper, defined beside the other backend
# fixtures in tests/test_s0_01_scripted_backend.py.  It is loaded BY PATH rather than by
# `import test_s0_01_scripted_backend`, because this file is also run on its own (every mutant
# campaign runs it standalone) and pytest only puts `tests/` on sys.path when a module from
# `tests/` is collected in the same session.  The module name below is deliberately not the
# test module's own name, so pytest still collects that file exactly once.
_MAIN_TESTS = ROOT / "tests" / "test_s0_01_scripted_backend.py"
_spec = importlib.util.spec_from_file_location("s0_01_backend_testlib", _MAIN_TESTS)
_testlib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_testlib)
_wait_ready = _testlib._wait_ready


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
    _wait_ready(proc, port)
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


TAIL = b"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\nContent-Length: 2\r\n\r\n{}"


def _post(port, body: bytes, extra_headers: str = "", tail: bytes = b""):
    return (f"POST /v1/chat/completions HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
            f"Authorization: Bearer {TOKEN}\r\nContent-Type: application/json\r\n{extra_headers}"
            f"Content-Length: {len(body)}\r\n\r\n").encode() + body + tail


_INVIS_CATEGORIES = frozenset({"Cf", "Cs", "Cc", "Mn", "Me", "Zs", "Zl", "Zp"})
_INVISIBLE_EXTRA = frozenset({
    chr(0x115F), chr(0x1160), chr(0x3164), chr(0xFFA0),
    chr(0x2800), chr(0x180E),
    chr(0x2065),
    chr(0xFFF0), chr(0xFFF1), chr(0xFFF2), chr(0xFFF3), chr(0xFFF4),
    chr(0xFFF5), chr(0xFFF6), chr(0xFFF7), chr(0xFFF8),
})
# Oracle's OWN copy of the committed range string (D5i-F3); the oracle unions
# this with the LIVE categories so it is >= the impl on every interpreter.
_ORACLE_INVIS_RANGES = (
    "0000-0020 007F-00A0 00AD 0300-036F 0483-0489 0591-05BD 05BF 05C1-05C2 "
    "05C4-05C5 05C7 0600-0605 0610-061A 061C 064B-065F 0670 06D6-06DD "
    "06DF-06E4 06E7-06E8 06EA-06ED 070F 0711 0730-074A 07A6-07B0 07EB-07F3 "
    "07FD 0816-0819 081B-0823 0825-0827 0829-082D 0859-085B 0890-0891 "
    "0898-089F 08CA-0902 093A 093C 0941-0948 094D 0951-0957 0962-0963 0981 "
    "09BC 09C1-09C4 09CD 09E2-09E3 09FE 0A01-0A02 0A3C 0A41-0A42 0A47-0A48 "
    "0A4B-0A4D 0A51 0A70-0A71 0A75 0A81-0A82 0ABC 0AC1-0AC5 0AC7-0AC8 0ACD "
    "0AE2-0AE3 0AFA-0AFF 0B01 0B3C 0B3F 0B41-0B44 0B4D 0B55-0B56 0B62-0B63 "
    "0B82 0BC0 0BCD 0C00 0C04 0C3C 0C3E-0C40 0C46-0C48 0C4A-0C4D 0C55-0C56 "
    "0C62-0C63 0C81 0CBC 0CBF 0CC6 0CCC-0CCD 0CE2-0CE3 0D00-0D01 0D3B-0D3C "
    "0D41-0D44 0D4D 0D62-0D63 0D81 0DCA 0DD2-0DD4 0DD6 0E31 0E34-0E3A "
    "0E47-0E4E 0EB1 0EB4-0EBC 0EC8-0ECE 0F18-0F19 0F35 0F37 0F39 0F71-0F7E "
    "0F80-0F84 0F86-0F87 0F8D-0F97 0F99-0FBC 0FC6 102D-1030 1032-1037 "
    "1039-103A 103D-103E 1058-1059 105E-1060 1071-1074 1082 1085-1086 108D "
    "109D 115F-1160 135D-135F 1680 1712-1714 1732-1733 1752-1753 1772-1773 "
    "17B4-17B5 17B7-17BD 17C6 17C9-17D3 17DD 180B-180F 1885-1886 18A9 "
    "1920-1922 1927-1928 1932 1939-193B 1A17-1A18 1A1B 1A56 1A58-1A5E 1A60 "
    "1A62 1A65-1A6C 1A73-1A7C 1A7F 1AB0-1ACE 1B00-1B03 1B34 1B36-1B3A 1B3C "
    "1B42 1B6B-1B73 1B80-1B81 1BA2-1BA5 1BA8-1BA9 1BAB-1BAD 1BE6 1BE8-1BE9 "
    "1BED 1BEF-1BF1 1C2C-1C33 1C36-1C37 1CD0-1CD2 1CD4-1CE0 1CE2-1CE8 1CED "
    "1CF4 1CF8-1CF9 1DC0-1DFF 2000-200F 2028-202F 205F-206F "
    "20D0-20F0 2800 2CEF-2CF1 2D7F 2DE0-2DFF 3000 302A-302D 3099-309A 3164 "
    "A66F-A672 A674-A67D A69E-A69F A6F0-A6F1 A802 A806 A80B A825-A826 A82C "
    "A8C4-A8C5 A8E0-A8F1 A8FF A926-A92D A947-A951 A980-A982 A9B3 A9B6-A9B9 "
    "A9BC-A9BD A9E5 AA29-AA2E AA31-AA32 AA35-AA36 AA43 AA4C AA7C AAB0 "
    "AAB2-AAB4 AAB7-AAB8 AABE-AABF AAC1 AAEC-AAED AAF6 ABE5 ABE8 ABED "
    "D800-DFFF FB1E FE00-FE0F FE20-FE2F FEFF FFA0 FFF0-FFFB 101FD 102E0 "
    "10376-1037A 10A01-10A03 10A05-10A06 10A0C-10A0F 10A38-10A3A 10A3F "
    "10AE5-10AE6 10D24-10D27 10EAB-10EAC 10EFD-10EFF 10F46-10F50 10F82-10F85 "
    "11001 11038-11046 11070 11073-11074 1107F-11081 110B3-110B6 110B9-110BA "
    "110BD 110C2 110CD 11100-11102 11127-1112B 1112D-11134 11173 11180-11181 "
    "111B6-111BE 111C9-111CC 111CF 1122F-11231 11234 11236-11237 1123E 11241 "
    "112DF 112E3-112EA 11300-11301 1133B-1133C 11340 11366-1136C 11370-11374 "
    "11438-1143F 11442-11444 11446 1145E 114B3-114B8 114BA 114BF-114C0 "
    "114C2-114C3 115B2-115B5 115BC-115BD 115BF-115C0 115DC-115DD 11633-1163A "
    "1163D 1163F-11640 116AB 116AD 116B0-116B5 116B7 1171D-1171F 11722-11725 "
    "11727-1172B 1182F-11837 11839-1183A 1193B-1193C 1193E 11943 119D4-119D7 "
    "119DA-119DB 119E0 11A01-11A0A 11A33-11A38 11A3B-11A3E 11A47 11A51-11A56 "
    "11A59-11A5B 11A8A-11A96 11A98-11A99 11C30-11C36 11C38-11C3D 11C3F "
    "11C92-11CA7 11CAA-11CB0 11CB2-11CB3 11CB5-11CB6 11D31-11D36 11D3A "
    "11D3C-11D3D 11D3F-11D45 11D47 11D90-11D91 11D95 11D97 11EF3-11EF4 "
    "11F00-11F01 11F36-11F3A 11F40 11F42 13430-13440 13447-13455 16AF0-16AF4 "
    "16B30-16B36 16F4F 16F8F-16F92 16FE4 1BC9D-1BC9E 1BCA0-1BCA3 "
    "1CF00-1CF2D 1CF30-1CF46 1D167-1D169 1D173-1D182 1D185-1D18B 1D1AA-1D1AD "
    "1D242-1D244 1DA00-1DA36 1DA3B-1DA6C 1DA75 1DA84 1DA9B-1DA9F 1DAA1-1DAAF "
    "1E000-1E006 1E008-1E018 1E01B-1E021 1E023-1E024 1E026-1E02A 1E08F "
    "1E130-1E136 1E2AE 1E2EC-1E2EF 1E4EC-1E4EF 1E8D0-1E8D6 1E944-1E94A "
    "E0001 E0020-E007F E0100-E01EF"
)


def _parse_oracle_ranges(s):
    result = set()
    for part in s.split():
        if '-' in part:
            lo, hi = part.split('-')
            for cp in range(int(lo, 16), int(hi, 16) + 1):
                result.add(cp)
        else:
            result.add(int(part, 16))
    return frozenset(result)


_ORACLE_INVIS_PINNED = _parse_oracle_ranges(_ORACLE_INVIS_RANGES)


def _absent_under_all_normalizations(text: str) -> bool:
    """F2: STRICTLY WIDER oracle than the backend's _normal_forms.

    Enumerates every word over {unquote_drop, unquote_plus_drop, lower,
    utf8_redecode_lenient, strip_invis} up to depth 6 (the backend uses
    the same five operators at depth 5; D5i).  Never imports the backend's
    helper.  strip_invis drops every code point in _ORACLE_INVIS_PINNED
    (the committed UCD-15.1 table) OR whose live unicodedata.category is in
    _INVIS_CATEGORIES — the oracle is >= the impl on every interpreter and
    wider on a newer UCD (D5i-F3).
    unquote_drop / unquote_plus_drop use errors="ignore" so that an invalid
    percent-encoded UTF-8 byte (e.g. %80) is dropped, not replaced with
    U+FFFD which would survive strip_invis (D5i-F2).
    ``unquote`` with default errors is redundant with ``unquote_plus`` only
    for a token containing no ``+``; the drop-variant replaces it and stays
    so the oracle is token-agnostic (D5h-F12).
    Seeds with json.loads of every JSON string literal (F4/F7).
    """
    def strip_invis(x):
        return "".join(c for c in x
                       if ord(c) not in _ORACLE_INVIS_PINNED
                       and unicodedata.category(c) not in _INVIS_CATEGORIES
                       and c not in _INVISIBLE_EXTRA)
    def utf8_redecode_lenient(x):
        try:
            return x.encode("latin-1").decode("utf-8", errors="ignore")
        except UnicodeEncodeError:
            return x
    def unquote_drop(x):
        return unquote(x, errors="ignore")
    def unquote_plus_drop(x):
        return unquote_plus(x, errors="ignore")
    ops = (unquote_drop, unquote_plus_drop, str.lower, utf8_redecode_lenient, strip_invis)
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
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == json.loads(core)


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
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == json.loads(_nested_note_body(MAX_JSON_DEPTH))


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
        # D5h-F13: strip_invis Cc arm (U+0085 = NEL, a C1 control)
        (TOKEN[:len(TOKEN)//2] + chr(0x85) + TOKEN[len(TOKEN)//2:], False),
        # D5h-F13: strip_invis Cc arm (U+007F = DEL)
        (TOKEN[:len(TOKEN)//2] + chr(0x7F) + TOKEN[len(TOKEN)//2:], False),
        # D5i: strip_invis self-tests (invisible separators by category)
        (TOKEN[:len(TOKEN)//2] + chr(0x200C) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x200E) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x2800) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x3164) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0xFE00) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x0301) + TOKEN[len(TOKEN)//2:], False),
        # D5j: _INVISIBLE_EXTRA members pinned (D5i-F4)
        (TOKEN[:len(TOKEN)//2] + chr(0xFFA0) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x115F) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x1160) + TOKEN[len(TOKEN)//2:], False),
        # D5j: Me/Zl/Zp/Cs members pinned (D5i-F5/F16)
        (TOKEN[:len(TOKEN)//2] + chr(0x2028) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x2029) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x20DD) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0x0488) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0xD800) + TOKEN[len(TOKEN)//2:], False),
        # D5j: percent-encoded invalid UTF-8 separator (D5i-F2)
        (TOKEN[:len(TOKEN)//2] + "%80" + TOKEN[len(TOKEN)//2:], False),
        # D5k item 2: UCD-15 addition (RED on 3.11 under O-TABLE-DROP)
        (TOKEN[:len(TOKEN)//2] + chr(0x0ECE) + TOKEN[len(TOKEN)//2:], False),
        # D5k item 3: permanently-reserved BMP slots
        (TOKEN[:len(TOKEN)//2] + chr(0x2065) + TOKEN[len(TOKEN)//2:], False),
        (TOKEN[:len(TOKEN)//2] + chr(0xFFF0) + TOKEN[len(TOKEN)//2:], False),
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
            "halfwidth_filler_split", "choseong_split", "jungseong_split",
            "line_sep_split", "para_sep_split",
            "enclosing_circle_split", "cyrillic_enclosing_split",
            "lone_surrogate_split",
            "pct_lone_continuation_split",
            "ucd15_addition_split",
            "reserved_2065_split", "reserved_fff0_split",
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
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == json.loads(body)


def test_json_depth_handles_escaped_quote(backend):
    r"""An escaped quote (q\") followed by 40 '[' stays inside the string (kills MG5)."""
    port = backend["port"]
    n0 = len(_records(backend))
    body = b'{"model":"s0-01-pong","messages":[{"role":"user","content":"hi"}],"note":"q\\"' + b'[' * 40 + b'"}'
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 200 OK"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == json.loads(body)


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
    n0 = len(_records(backend))
    vec = TOKEN[:mid] + "+" + TOKEN[mid:] + "%2520"
    resp = _raw(port, _post(port, b'{"model":"s0-01-pong","messages":[]}',
                            extra_headers=f"X-Trace: {vec}\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


# ---- R9-D5g-F2: raw UTF-8 zero-width separator ------

@pytest.mark.parametrize("sep", [
    "​", "﻿", "­", "⁠", " ", "　",
], ids=["ZWSP", "BOM", "SOFT_HYPHEN", "WORD_JOINER", "NBSP", "IDEOGRAPHIC_SPACE"])
def test_credential_raw_utf8_zero_width_in_header_returns_400(backend, sep):
    """F2/F15 'raw': the separator arrives as UTF-8 BYTES on the wire;
    http.server decodes header lines as latin-1, producing 2-3 latin-1 chars
    that strip_invis does not touch until utf8_redecode_lenient has
    recovered the real code point."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    n0 = len(_records(backend))
    body = b'{"model":"s0-01-pong","messages":[]}'
    payload = (f"POST /v1/chat/completions HTTP/1.1\r\nHost: x\r\n"
               f"Authorization: Bearer {TOKEN}\r\nContent-Type: application/json\r\n"
               f"X-Trace: ").encode() + TOKEN[:mid].encode() + sep.encode("utf-8") \
              + TOKEN[mid:].encode() + f"\r\nContent-Length: {len(body)}\r\n\r\n".encode() + body
    resp = _raw(port, payload)
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


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
    value must be caught by strip_invis (Cc arm)."""
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
    """%252520%252B fails to saturate at depth 5 only because unquote_drop is
    in the op set.  Mutant M_UQ_DEL dies on this test."""
    port = backend["port"]
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, b'{"model":"s0-01-pong","messages":[]}',
                            extra_headers="X-Trace: %252520%252B\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


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
    not by a hand-written list) must be caught.  RED on the D5h PIN
    (the old strip_zwc covered only U+200B/FEFF/AD/2060)."""
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
    (0x2800, "BRAILLE_BLANK"), (0x3164, "HANGUL_FILLER"),
    (0xFFA0, "HALFWIDTH_FILLER"), (0x115F, "CHOSEONG_FILLER"),
    (0x1160, "JUNGSEONG_FILLER"),
    (0x2028, "LINE_SEPARATOR"), (0x2029, "PARAGRAPH_SEPARATOR"),
    (0x20DD, "ENCLOSING_CIRCLE"), (0x0488, "CYRILLIC_ENCLOSING"),
], ids=["ZWNJ", "ZWJ", "LRM", "COMBINING_ACUTE",
        "BRAILLE_BLANK", "HANGUL_FILLER", "HALFWIDTH_FILLER",
        "CHOSEONG_FILLER", "JUNGSEONG_FILLER",
        "LINE_SEPARATOR", "PARAGRAPH_SEPARATOR",
        "ENCLOSING_CIRCLE", "CYRILLIC_ENCLOSING"])
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


# ---- D5h-F4: C1 control wire form (valid UTF-8 → only strip_invis Cc arm catches it) ----

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

def test_precheck_before_closure_on_invalid_utf8(backend, monkeypatch):
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

    monkeypatch.setattr(sb, "_normal_forms", counting_nf)
    state = sb.State("tok", pathlib.Path("/dev/null"), 0.0)
    # invalid UTF-8 byte view: 0x80 0xC0 are not valid UTF-8
    s = "ua-" + bytes([0x80, 0xC0]).decode("latin-1") + "-probe"
    result = state._carries_secret(s, byte_view=True)
    assert result is True, "invalid UTF-8 byte view must return True"
    assert call_count[0] == 0, (
        f"_normal_forms was called {call_count[0]} times; precheck should short-circuit"
    )


# ---- D5j item 1 (D5i-F1): top-level JSON string body is not a byte view ----

@pytest.mark.parametrize("doc", [
    b'"caf\xc3\xa9"', b'"M\xc3\xbcller"', b'"\xc2\xa3100"',
], ids=["e_acute", "u_uml", "pound"])
def test_top_level_json_string_body_is_not_a_byte_view(backend, doc):
    """A top-level JSON string is DECODED by json.loads; the precheck must not
    re-encode it.  UTF-8 on the wire, no credential -> ordinary route 400,
    record verbatim (not the credential MARKER).  D5i-F1."""
    port = backend["port"]
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, doc))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == json.loads(doc)


def test_top_level_json_string_hello_control(backend):
    """Control for D5i-F1: 'hello' is pure ASCII, served 400 + verbatim
    both before and after the fix."""
    port = backend["port"]
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, b'"hello"'))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == "hello"


# ---- D5j item 2 (D5i-F2): percent-encoded invalid UTF-8 separator ----

@pytest.mark.parametrize("sep", ["%80", "%C0", "%FF", "%ED%A0%80"],
                         ids=["lone_cont", "overlong_lead", "ff", "surrogate"])
def test_credential_pct_encoded_invalid_utf8_separator_returns_400(backend, sep):
    """unquote() defaults to errors='replace', so %80 becomes U+FFFD (So)
    and survives strip_invis.  With errors='ignore' (unquote_drop) the
    byte is dropped and the token is found.  D5i-F2."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    split = TOKEN[:mid] + sep + TOKEN[mid:]
    body = b'{"model":"s0-01-pong","messages":[]}'
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, body, extra_headers=f"X-Trace: {split}\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


# ---- D5j item 4 (D5i-F5): lone surrogate in JSON body ----

def test_credential_lone_surrogate_separator_in_json_body_returns_400(backend):
    """A lone surrogate escape (category Cs) splitting the token must be
    caught by strip_invis.  D5i-F5."""
    port = backend["port"]
    mid = len(TOKEN) // 2
    body = (b'{"model":"s0-01-pong","messages":[],"t":"'
            + TOKEN[:mid].encode() + b'\\ud800' + TOKEN[mid:].encode() + b'"}')
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, body))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 400 Bad Request"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["body"] == MARKER


# ---- D5k item 3: permanently-reserved BMP slots in JSON body ----

@pytest.mark.parametrize("cp,cp_id", [
    (0x2065, "RESERVED_2065"), (0xFFF0, "RESERVED_FFF0"),
], ids=["RESERVED_2065", "RESERVED_FFF0"])
def test_credential_reserved_bmp_separator_in_json_body_returns_400(backend, cp, cp_id):
    """D5k item 3: permanently-reserved BMP code points (U+2065, U+FFF0-FFF8)
    splitting the token via JSON escape must be caught.  RED on the PIN
    (served 200 before the reserved slots joined _INVISIBLE_EXTRA)."""
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


# ---- D5k item 1 (D5j-F1): no "!= MARKER" anywhere in the test files ----

def test_no_not_equal_marker_assertions(tmp_path):
    """D5j-F1 class: no S0-01 test uses MARKER as a NEGATIVE acceptance check.

    Scope is the GLOB, not a file list.  VERIFY-D5l F1: the two-file version was green over a
    live violation planted in a third S0-01 test file (`2 passed` while the banned form sat in
    tests/test_s0_01_negative_contract.py) — SWEEP-tests rows 4.4/18.1 register "a lint whose
    scope is a hard-coded file list" as the class.  The glob costs nothing: it returns 0 hits
    over all of tests/test_s0_01_*.py + tests/red/test_s0_01_*.py today.

    CAUGHT by the walk (measured, controls below): `x != MARKER` / `MARKER != x` in either
    operand order and at any nesting inside the assert's test (tuple, lambda, walrus),
    `x not in (MARKER,)`, `x is not MARKER`, and `not (x == MARKER)`.

    OUT OF SCOPE, stated rather than silently missed (VERIFY-D5l's 16-form table measured each
    one escaping): an alias (`M = MARKER; assert x != M`), a helper function
    (`def _served(r): return r != MARKER`), `operator.ne(x, MARKER)`, the dunder
    `x.__ne__(MARKER)`, an attribute spelling (`x != m.MARKER`) and a differently-named
    constant.  Each needs data-flow or import resolution, which an AST walk of one file does
    not have.  This is a documented limit, not a claim of closure.
    """
    import ast

    def _mentions_marker(node):
        return any(isinstance(n, ast.Name) and n.id == "MARKER" for n in ast.walk(node))

    def marker_not_equal_asserts(path):
        found = []
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(node, ast.Assert):
                continue
            for sub in ast.walk(node.test):
                # x != MARKER / x not in (MARKER,) / x is not MARKER, either operand order
                if (isinstance(sub, ast.Compare)
                        and any(isinstance(op, (ast.NotEq, ast.NotIn, ast.IsNot)) for op in sub.ops)
                        and _mentions_marker(sub)):
                    found.append((path.name, node.lineno))
                    break
                # not (x == MARKER) / not (x in (MARKER,)) / not (x is MARKER)
                if (isinstance(sub, ast.UnaryOp) and isinstance(sub.op, ast.Not)
                        and isinstance(sub.operand, ast.Compare)
                        and any(isinstance(op, (ast.Eq, ast.In, ast.Is)) for op in sub.operand.ops)
                        and _mentions_marker(sub.operand)):
                    found.append((path.name, node.lineno))
                    break
        return found

    # two-sided controls: a walker that always returns [] fails these, one that returns
    # everything fails the positive control, and each pins the LINE so a reporting off-by-one dies
    controls = {
        "break_form.py": ('import json\nMARKER = {}\nassert json.loads(x)["body"] != MARKER\n', 3),
        "evade_form.py": ('import json\nMARKER = {}\n_b = json.loads(x)["body"]\nassert _b != MARKER\n', 4),
        "not_eq_form.py": ('MARKER = {}\nassert not (x == MARKER)\n', 2),
        "not_in_form.py": ('MARKER = {}\nassert x not in (MARKER,)\n', 2),
        "is_not_form.py": ('MARKER = {}\nassert x is not MARKER\n', 2),
    }
    for name, (src, lineno) in controls.items():
        f = tmp_path / name
        f.write_text(src)
        assert marker_not_equal_asserts(f) == [(name, lineno)], name
    ok_file = tmp_path / "positive_form.py"
    ok_file.write_text('import json\nMARKER = {}\n_b = json.loads(x)["body"]\nassert _b == expected\n')
    assert marker_not_equal_asserts(ok_file) == []
    # a POSITIVE acceptance use of MARKER (this file's own idiom) must not be flagged
    keep_file = tmp_path / "keep_form.py"
    keep_file.write_text('import json\nMARKER = {}\nassert json.loads(r)["body"] == MARKER\n')
    assert marker_not_equal_asserts(keep_file) == []

    root = pathlib.Path(__file__).parents[1]
    targets = sorted(root.glob("test_s0_01_*.py")) + sorted((root / "red").glob("test_s0_01_*.py"))
    # the scope is itself asserted, so a future hard-coded list cannot come back unnoticed
    names = {p.name for p in targets}
    assert names >= {p.name for p in root.glob("test_s0_01_*.py")}
    assert names >= {p.name for p in (root / "red").glob("test_s0_01_*.py")}
    assert pathlib.Path(__file__).name in names
    for target in targets:
        assert marker_not_equal_asserts(target) == [], target


# ---- D5k item 5 (D5j-F6): saturation-flip test ----

def test_pct_dense_junk_that_now_saturates_is_served(backend):
    """One of the 105 vectors that move from fail-closed to served under the
    drop-variant: the depth-6 oracle confirms the token absent.  RED under
    UQ-REPLACE-BOTH (the replace variant blanks this record)."""
    port = backend["port"]
    vec = "s0-01-upstream-tok%2B%C0%252520%209\t %C0en-0123456789abcdef"
    n0 = len(_records(backend))
    resp = _raw(port, _post(port, b'{"model":"s0-01-pong","messages":[]}',
                            extra_headers=f"X-Trace: {vec}\r\n"))
    assert resp.split(b"\r\n", 1)[0] == b"HTTP/1.1 200 OK"
    recs = _records(backend)
    assert len(recs) == n0 + 1
    assert json.loads(recs[-1].read_text())["headers"]["x-trace"] == vec
    assert _absent_under_all_normalizations(recs[-1].read_text())
