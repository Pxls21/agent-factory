"""VERIFY-SCRUB2-R1-R3's red tests (scratch only, never committed). N2 (round 3, item 2): a head the PIN never read never
frees a later value the PIN hid. N2R: round 3's stops cover later pwd, credentials and Cookie heads (and _APART names for
a new Cookie head) but not the heads of the rules that run after it in scrub_payload: the R1 escaped-quote credential
(`name=\\"<v>\\"`, any _NAME or _PASS name), the PASS rule (`DB_PASS="<v>"`) and curl's `-u "user:pass"`. A new Cookie
head (in canonical JSON every Cookie line after an escaped newline is one: the PIN's `\\b` fails after the `n`), or a new
pwd or credentials head, takes a value that runs over such a head and stops right before its value, which then shows in
convert()'s events. The PIN hid each. Every value is a fake built here."""
import importlib.util
import json
import pathlib
import secrets

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "transcript_export.py"
_spec = importlib.util.spec_from_file_location("transcript_export_vscrub2r1r3", TOOL)
MOD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MOD)
B = "\\"


def _v():
    return "7" + secrets.token_hex(8) + "q"


def _canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _hidden(v, out):
    """no 8-character piece of v, as written or as JSON writes it, is in out"""
    forms = {v, json.dumps(v)[1:-1]}
    return not any(f[i:i + 8] in out for f in forms for i in range(len(f) - 7))


def _settle(text):
    """convert()'s scrub of one event's text: scrub_payload to a fixed point (at most 4 passes)"""
    for _ in range(4):
        out = MOD.scrub_payload(text)
        if out == text:
            return out
        text = out
    return "<UNSETTLED>"


# canonical JSON (convert()'s tool_call): a Cookie line after an escaped newline, then a quoted credential on a later line
@pytest.mark.parametrize("later", ["export DB_PASSWORD=\"%s\"", "token=\"%s\"", "api_key=\"%s\"", "AGENT_TOKEN=\"%s\"",
                                   "SMTP_PASS='%s'"])
def test_n2r_a_line_start_cookie_in_canonical_json_frees_no_later_value(later):
    c, v = _v(), _v()
    text = "cat > /tmp/zq/req.http <<'EOF'\nGET /api HTTP/1.1\nCookie: session=%s\nEOF\n%s\n" % (c, later % v)
    assert _hidden(v, _settle(_canon({"command": text})))


# decoded text (convert()'s text and tool_result events): a head the PIN never read, then a PAYLOAD rule's head
@pytest.mark.parametrize("fmt", ["my_cookie: sid=%s; DB_PASS=\"%s\"", "my_cookie: sid=%s; curl -u \"admin:%s\" https://zq.example",
                                 "x" + B + "rPWD: sid=%sSMTP_PASS='%s'", "my_cookie: sid=%s; password=" + B + "\"%s" + B + "\""])
def test_n2r_a_new_head_in_decoded_text_frees_no_later_value(fmt):
    c, v = _v(), _v()
    assert _hidden(v, _settle(fmt % (c, v)))


# canonical JSON: a pwd or credentials head the PIN never read (after a literal \t or \r), its value over an escaped line
# end (the V4 continuation), then a quoted credential on the next line
@pytest.mark.parametrize("fmt", ["x" + B + "tpwd=sid=%s\nDB_PASSWORD=\"%s\"", "y" + B + "rcredentials = sid=%s\r\ntoken=\"%s\""])
def test_n2r_a_new_pwd_or_credentials_head_in_canonical_json_frees_no_later_value(fmt):
    c, v = _v(), _v()
    assert _hidden(v, _settle(_canon({"command": fmt % (c, v)})))
