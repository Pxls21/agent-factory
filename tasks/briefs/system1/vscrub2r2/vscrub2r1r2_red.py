"""VERIFY-SCRUB2-R1-R2's red tests (scratch only, never committed). V4 (round 2, item 4): no redaction the PIN makes may be
lost in any view. N1: the pwd and credentials floors count a backslash pair, an escape or a group of escapes as ONE unit,
so a value of 8+ characters with literal backslash content falls under the floor where the PIN (it counted characters) hid
it. N2: a Cookie head the PIN never read (an escaped-quote head, `my_cookie:`) takes a value that runs over a later pwd /
credentials head and stops before that head's value (AF-AP-157), which then shows. Every value is a fake built here."""
import importlib.util
import json
import pathlib
import secrets

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "transcript_export.py"
_spec = importlib.util.spec_from_file_location("transcript_export_vscrub2r1r2", TOOL)
MOD = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MOD)
B = "\\"


def _h(n):
    return secrets.token_hex(n)[:n]


def _canon(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _hidden(v, out):
    """no 8-character piece of v, as written or as JSON writes it, is in out"""
    forms = {v, json.dumps(v)[1:-1]}
    return not any(f[i:i + 8] in out for f in forms for i in range(len(f) - 7))


# N1, decoded text (the digest): 8 characters, one literal pair / tab escape / a group of two escapes / three pairs.
@pytest.mark.parametrize("head", ["pwd=", "PWD: ", "credentials="])
@pytest.mark.parametrize("shape", ["pair8", "pairs10", "oddrun9"])
def test_n1_a_short_value_with_backslash_content_stays_hidden_in_decoded_text(head, shape):
    v = {"pair8": "Q" + _h(1) + B + B + _h(4), "pairs10": "Q" + B * 2 + _h(1) + B * 2 + _h(1) + B * 2 + "z",
         "oddrun9": "Q" + _h(4) + B * 3 + "x"}[shape]
    assert _hidden(v, MOD.scrub(head + v))


@pytest.mark.parametrize("shape", ["tab8", "group8"])
def test_n1_a_short_pwd_value_with_literal_escapes_stays_hidden_in_decoded_text(shape):
    v = {"tab8": "R" + _h(2) + B + "t" + _h(3), "group8": "M" + _h(1) + B + "n" + B + "n" + _h(2)}[shape]
    assert _hidden(v, MOD.scrub("pwd=" + v))


# N1, canonical JSON (convert()'s tool_call): the decoded pair is four backslashes there, one unit to round 2's floor.
@pytest.mark.parametrize("head", ["--pwd=", "credentials="])
def test_n1_a_short_value_with_a_pair_stays_hidden_in_canonical_json(head):
    v = "Q" + _h(1) + B + B + _h(4)
    assert _hidden(v, MOD.scrub_payload(_canon({"command": head + v})))


# N2: a Cookie head the PIN never read swallows the pwd head; the pwd value must stay hidden as the PIN hid it.
@pytest.mark.parametrize("fmt", ["{" + B + "\"Cookie" + B + "\": " + B + "\"sid=%s; pwd='%s'" + B + "\"}",
                                 "my_cookie: session=%s; db_pwd=\"%s\"",
                                 "my_cookie: sid=%s; credentials=\"%s\""])
def test_n2_a_newly_read_cookie_head_never_frees_a_later_value(fmt):
    c, v = "7" + _h(14) + "q", "7" + _h(14) + "q"
    text = fmt % (c, v)
    assert _hidden(v, MOD.scrub(text)) and _hidden(v, MOD.scrub_payload(text))
