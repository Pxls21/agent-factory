"""transcript_export: every planted secret class is scrubbed before it reaches disk (negative
control per class), user/assistant text survives (positive control), noise turns are dropped,
output is deterministic and idempotent. Synthetic JSONL only — never the live transcript."""
import base64
import contextlib
import importlib.util
import inspect
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import types
from secrets import token_bytes, token_hex

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "transcript_export.py"

PLANTED = {
    "bridge-token-assign": "AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr",
    "env-token": "PC_BRIDGE_TOKEN=abcdefghijklmnop123456",
    "header": "X-Agent-Token: zzzzzzzzzzzzzzzzzzzzzz",
    "bearer": "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig",
    "openai-key": "sk-3c3d5f1e8a2b4c6d9e0f1234567890ab",
    "github-pat": "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "google-key": "AIzaSyA1234567890abcdefghijklmnopqrstuv",
    "yaml-key": "api_key: sk-live-0123456789abcdef0123",
    "bridge-url": "https://leading-twist-aruba-pulse.trycloudflare.com/exec",
    "opaque": "token=" + "Q" * 44,
}
RAW_SECRETS = ["cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr", "abcdefghijklmnop123456", "zzzzzzzzzzzzzzzzzzzzzz",
               "eyJhbGciOiJIUzI1NiJ9", "3c3d5f1e8a2b4c6d9e0f1234567890ab", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
               "AIzaSyA1234567890abcdefghijklmnopqrstuv", "sk-live-0123456789abcdef0123",
               "leading-twist-aruba-pulse", "Q" * 44]


def _entry(role, text, ts):
    return json.dumps({"type": role, "timestamp": ts, "message": {"role": role, "content": [{"type": "text", "text": text}]}})


def _write_jsonl(p):
    lines = [
        _entry("user", "please deploy; here is the banner " + " ".join(PLANTED.values()), "2026-09-03T05:00:00Z"),
        _entry("assistant", "KEEP-ME: the plan is three waves", "2026-09-03T05:01:00Z"),
        _entry("user", "Stop hook feedback: noise", "2026-09-03T05:02:00Z"),
        _entry("user", "<system-reminder> noise", "2026-09-03T05:03:00Z"),
        json.dumps({"type": "user", "timestamp": "2026-09-03T05:04:00Z", "message": {"role": "user", "content": [{"type": "tool_result", "content": "secret-in-tool-result sk-toolresult00000000000000"}]}}),
        _entry("assistant", "next day text", "2026-09-04T01:00:00Z"),
        "not json at all",
    ]
    p.write_text("\n".join(lines) + "\n")


def _fixture_sources(where):
    """Value-gate sources for a CLI test: an env file and a raw key file in `where`, holding fakes made at run time."""
    env, key = pathlib.Path(where) / "zq-fixture.env", pathlib.Path(where) / "zq-fixture.key"
    env.write_text("ZQ_FIXTURE_TOKEN=%s\n" % _fake_value())
    key.write_bytes(token_bytes(32))
    return (("env-file", str(env), ()), ("raw-file", str(key), ()))


def _run(jsonl, out, *args, sources=None):
    """The CLI in process: MOD.main() with these arguments; its exit code, stdout and stderr. main() reads
    MOD.KNOWN_VALUE_SOURCES when it runs, and for this call it holds `sources` (default: fakes made next to `out`).
    VERIFY-SCRUB1 F1: this ran the CLI as a child process, which read the machine's real value-gate sources."""
    saved = MOD.KNOWN_VALUE_SOURCES
    MOD.KNOWN_VALUE_SOURCES = _fixture_sources(pathlib.Path(out).parent) if sources is None else sources
    o, e = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
            rc = MOD.main(["--transcript", str(jsonl), "--out", str(out), *map(str, args)])
    finally:
        MOD.KNOWN_VALUE_SOURCES = saved
    return types.SimpleNamespace(returncode=rc, stdout=o.getvalue(), stderr=e.getvalue())


def test_secrets_never_reach_disk_and_text_survives(tmp_path):
    jsonl = tmp_path / "t.jsonl"
    _write_jsonl(jsonl)
    out = tmp_path / "out"
    r = _run(jsonl, out)
    assert r.returncode == 0, r.stderr
    files = sorted(out.glob("chat-*.md"))
    assert [f.name for f in files] == ["chat-2026-09-03.md", "chat-2026-09-04.md"]
    blob = "".join(f.read_text() for f in files)
    for s in RAW_SECRETS:
        assert s not in blob, f"secret survived: {s[:12]}…"
    assert "sk-toolresult" not in blob, "tool results must not be exported at all"
    assert "KEEP-ME: the plan is three waves" in blob
    assert "Stop hook feedback" not in blob and "system-reminder" not in blob
    assert "<redacted>" in blob or "redacted" in blob


def test_idempotent_and_deterministic(tmp_path):
    jsonl = tmp_path / "t.jsonl"
    _write_jsonl(jsonl)
    out = tmp_path / "out"
    assert _run(jsonl, out).returncode == 0
    first = {f.name: f.read_bytes() for f in out.glob("chat-*.md")}
    assert _run(jsonl, out).returncode == 0
    second = {f.name: f.read_bytes() for f in out.glob("chat-*.md")}
    assert first == second


def _export_one(tmp_path, text, cap):
    jsonl = tmp_path / "one.jsonl"
    jsonl.write_text(_entry("user", text, "2026-09-03T05:00:00Z") + "\n")
    out = tmp_path / "out"
    r = _run(jsonl, out, "--cap", cap)
    assert r.returncode == 0, r.stderr
    return (out / "chat-2026-09-03.md").read_text()


def test_secret_straddling_the_cap_never_reaches_disk(tmp_path):
    # AF-AP-127: capped BEFORE the scrub, each value below is cut under its pattern's minimum
    # (sk- needs 12 characters, a named token 8) and the stub reaches disk; scrubbed first, none does.
    lead = "note one two three "
    for secret, keep in (("sk-3c3d5f1e8a2b4c6d9e0f1234567890ab", 10),
                         ("AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr", 19)):
        blob = _export_one(tmp_path, lead + secret, len(lead) + keep)
        stub = secret[keep - 7:keep]
        assert stub not in blob, f"a {len(stub)}-char stub of the secret survived the cap: {blob!r}"


# Real key bodies carry `+` and `/`, which break a base64 line into runs shorter than the
# 40-character opaque rule, so without a key-block class their bytes reach disk.
KEY_BODY = "MIIEpAIB+AAKCAQ/EAx7Qe+Wz3k/Rt9L" * 4


def test_private_key_block_is_scrubbed_whole_or_to_the_end(tmp_path):
    pem = "-----BEGIN RSA PRIVATE KEY-----\n" + KEY_BODY + "\n-----END RSA PRIVATE KEY-----"
    blob = _export_one(tmp_path, "the key is\n" + pem + "\nafter the key", 4000)
    assert "AAKCAQ" not in blob and "x7Qe" not in blob, blob
    assert "<private-key-redacted>" in blob and "after the key" in blob
    # a block whose END line is missing at the source is redacted to the end of the turn
    blob = _export_one(tmp_path, "cut short\n-----BEGIN OPENSSH PRIVATE KEY-----\n" + KEY_BODY, 4000)
    assert "AAKCAQ" not in blob and "<private-key-redacted>" in blob and "cut short" in blob, blob
    # a block longer than the cap: scrubbed whole before the cap, no key characters on disk
    long_pem = "-----BEGIN RSA PRIVATE KEY-----\n" + KEY_BODY * 12 + "\n-----END RSA PRIVATE KEY-----"
    blob = _export_one(tmp_path, "long\n" + long_pem, 200)
    assert "AAKCAQ" not in blob and "<private-key-redacted>" in blob, blob


KEY_FAMILIES = ("RSA PRIVATE KEY", "EC PRIVATE KEY", "OPENSSH PRIVATE KEY", "ENCRYPTED PRIVATE KEY",
                "PRIVATE KEY", "PGP PRIVATE KEY BLOCK", "PGP SECRET KEY BLOCK")


@pytest.mark.parametrize("label", KEY_FAMILIES)
def test_every_key_family_is_scrubbed_whole(tmp_path, label):
    # VERIFY-AF-AP-127 F1: GnuPG armor ends its label in `KEY BLOCK` (and PGP 2.x says SECRET), so a
    # rule that wants `PRIVATE KEY-----` never matched it and the body lines reached disk. The plain
    # PKCS#8 label has no type word before PRIVATE (F8d).
    armor = "\n" if label.startswith("PGP") else ""          # GnuPG writes a blank line, then a checksum
    check = "\n=AbCd" if label.startswith("PGP") else ""
    block = f"-----BEGIN {label}-----\n{armor}{KEY_BODY}{check}\n-----END {label}-----"
    blob = _export_one(tmp_path, "the key is\n" + block + "\nafter the key", 4000)
    assert "AAKCAQ" not in blob and "x7Qe" not in blob, blob
    assert "<private-key-redacted>" in blob and "after the key" in blob, blob


def test_key_block_after_a_credential_keyword_is_scrubbed_whole(tmp_path):
    # The key rule runs FIRST (F8a): a credential rule that ran before it would take the BEGIN line
    # as the assigned value, and the key rule would then find no BEGIN and leave the body behind.
    block = "secret: -----BEGIN RSA PRIVATE KEY-----\n" + KEY_BODY + "\n-----END RSA PRIVATE KEY-----"
    blob = _export_one(tmp_path, block + "\nafter the key", 4000)
    assert "AAKCAQ" not in blob and "x7Qe" not in blob, blob
    assert "after the key" in blob, blob


# O-3 (J1-1-R1's hand-back, task #187; AF-AP-149's third site): the rule wanted `:`/`=` straight
# after the name, so a quoted key (JSON, quoted YAML) and a compound `*_key` / `*-key` name passed
# it and the value reached disk. Every value here is fake.
QUOTED_OR_COMPOUND = (
    ('"api_key": "Fk1eJsonApiKey0001"', "Fk1eJsonApiKey0001"),
    ('"password":"Fk1eJsonPasswd0002"', "Fk1eJsonPasswd0002"),
    ("'token': 'Fk1eQuotedTok0003'", "Fk1eQuotedTok0003"),
    ("SECRET_KEY: Fk1eSecretKey0004", "Fk1eSecretKey0004"),
    ("AWS_SECRET_ACCESS_KEY=Fk1eAwsAccess0005", "Fk1eAwsAccess0005"),
    ('DJANGO_SECRET_KEY = "Fk1eDjangoKey0006"', "Fk1eDjangoKey0006"),
    ("private_key: Fk1ePrivateKey0007", "Fk1ePrivateKey0007"),
    ("X-Secret-Key: Fk1eHeaderKey0008", "Fk1eHeaderKey0008"),
)


@pytest.mark.parametrize("line,value", QUOTED_OR_COMPOUND)
def test_quoted_and_compound_key_names_are_scrubbed(tmp_path, line, value):
    blob = _export_one(tmp_path, "config follows " + line + " end", 4000)
    assert value not in blob, blob
    assert "<redacted>" in blob and "config follows" in blob and " end" in blob, blob


def test_prose_beside_a_key_name_survives(tmp_path):
    # the name must be followed by its separator, and the value must reach 8 characters
    text = "tokenizer: whitespace, keyboard_key_map: qwertyuiop, sort_key: name, \"api_key\": short"
    blob = _export_one(tmp_path, text, 4000)
    assert text in blob and "<redacted>" not in blob, blob


def test_compound_key_rule_stays_linear_on_a_long_run(tmp_path):
    # The compound-name class starts only where a name can start (after a non-alphanumeric). Without
    # that anchor every position of a long base64 run re-scans the run: 40k characters took 17 s
    # (measured 2026-09-23), against 0.005 s anchored.
    import time
    t0 = time.monotonic()
    blob = _export_one(tmp_path, "blob " + "Ab1" * 14000 + " done", 60000)
    assert time.monotonic() - t0 < 3, "the scrub is not linear on a long alphanumeric run"
    assert "done" in blob


# AF-AP-157 (task #198 increment A): the credential value ran over a following secret NAME and its separator, so the rule
# never saw that name and its value reached disk. The value now stops before each head (a name read at its shortest, an
# optional quote, `:` or `=`) and the name stays. The 8-character floor reads the UNCUT run, as before; every value inside
# a run it admits is redacted at any length, because the old rule redacted all of it. Every value here is fake.
def _load_scrub():
    spec = importlib.util.spec_from_file_location("transcript_export_under_test", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.scrub


SCRUB = _load_scrub()

# (text, its scrub output, the fake values of which no byte may survive). The first three are the brief's premise shapes.
CHAINED = (
    ("passwd=aAPI_KEY : X4Z92Q0X1ZX02Z71", "passwd=<redacted>API_KEY : <redacted>", ("X4Z92Q0X1ZX02Z71",)),
    ("token='_API_KEY = 6Z4Z02ZX6Z4Z", "token='<redacted>API_KEY = <redacted>", ("6Z4Z02ZX6Z4Z",)),
    ("password='-db_password: 62669Q3JJ88ZX5466", "password='<redacted>password: <redacted>", ("62669Q3JJ88ZX5466",)),
    # a `token` head whose separator ends the run; its value comes after a space
    ("api_key=QZJ8QZJ8token: X4Z92Q0X1ZX02Z71", "api_key=<redacted>token: <redacted>", ("QZJ8QZJ8", "X4Z92Q0X1ZX02Z71")),
    # upper case, the name at the run's very end, spaces around `=`
    ("password=QZJ8QZJ8QZJ8_TOKEN = X4Z92Q0X1ZX02Z71", "password=<redacted>TOKEN = <redacted>",
     ("QZJ8QZJ8QZJ8", "X4Z92Q0X1ZX02Z71")),
    # a quote between the name and `:` (JSON)
    ('secret: QZJ8QZJ8.api_key": "X4Z92Q0X1ZX02Z71"', 'secret: <redacted>api_key": "<redacted>"',
     ("QZJ8QZJ8", "X4Z92Q0X1ZX02Z71")),
    # a quote after `=`: the head ends the run
    ("TOKEN=QZJ8QZJ8QZJ8SECRET='X4Z92Q0X1ZX02Z71'", "TOKEN=<redacted>SECRET='<redacted>'", ("QZJ8QZJ8QZJ8", "X4Z92Q0X1ZX02Z71")),
    # lower case, a hyphenated name, a space before `:`
    ("passwd=qzj8qzj8qzj8.api-key : x4z92q0x1zx02z71", "passwd=<redacted>api-key : <redacted>",
     ("qzj8qzj8qzj8", "x4z92q0x1zx02z71")),
    # three heads in one run
    ("password=QZJ8QZJ8_secret=WQ7XWQ7X_token : X4Z92Q0X1ZX02Z71", "password=<redacted>secret=<redacted>token : <redacted>",
     ("QZJ8QZJ8", "WQ7XWQ7X", "X4Z92Q0X1ZX02Z71")),
    # a value glued to a `*_key` name: read at its shortest (`_key`), the name leaves the value's own tail a value
    ("password=QZJ8QZJ8my_key: X4Z92Q0X1ZX02Z71", "password=<redacted>_key: <redacted>", ("QZJ8QZJ8", "X4Z92Q0X1ZX02Z71")),
)


@pytest.mark.parametrize("text,scrubbed,secrets", CHAINED)
def test_a_value_stops_before_the_next_secret_name(text, scrubbed, secrets):
    out = SCRUB(text)
    for s in secrets:
        assert s not in out, f"a chained value survived: {out!r}"
    assert out == scrubbed, out


# Inside the run the floor admitted, a short piece before a head, a short value after one and an empty piece stay redacted.
# (The old rule kept these values hidden too, as one long value, but it swallowed the second name.)
IN_RUN = (
    ("passwd=QZJ8Q_api_key=X4Z92Q0X1ZX02Z71", "passwd=<redacted>api_key=<redacted>", ("QZJ8Q", "X4Z92Q0X1ZX02Z71")),
    ("passwd=QZJ8QZJ8_API_KEY=X4Z9X4Z", "passwd=<redacted>API_KEY=<redacted>", ("QZJ8QZJ8", "X4Z9X4Z")),
    ("token=api_key=QZJ8QZJ8QZJ8", "token=api_key=<redacted>", ("QZJ8QZJ8QZJ8",)),
    # two env lines glued together: the first value's tail is not read into the second name
    ("DB_PASSWORD=QZJ8QZ12REDIS_KEY=X4Z9X4Z9", "DB_PASSWORD=<redacted>_KEY=<redacted>", ("QZJ8QZ12", "X4Z9X4Z9")),
)


@pytest.mark.parametrize("text,scrubbed,secrets", IN_RUN)
def test_a_value_cut_by_a_head_is_redacted_at_any_length(text, scrubbed, secrets):
    out = SCRUB(text)
    for s in secrets:
        assert s not in out, f"a value inside the run survived: {out!r}"
    assert out == scrubbed, f"the second name did not stay a name: {out!r}"


# The same class between rules (AF-AP-157 the other way): a value that ate the Bearer keyword, a value that ended inside a
# bridge link (at `&`), and a Bearer token that ate a following `Bearer` or `https` each stopped a later rule, and what
# that rule would have redacted showed. A value now stops before a Bearer match and takes a bridge link whole; a Bearer
# token stops before a Bearer match and a link.
LATER_RULES = (
    # a head the old rule swallowed now starts its own value, which must not eat the Bearer keyword
    ("passwd=QZJ8QZJ8.api_key:'QZJ8QZJ8/Bearer X4Z92Q0X1ZX02Z71", "passwd=<redacted>api_key:'<redacted>Bearer <redacted>",
     ("QZJ8QZJ8", "X4Z92Q0X1ZX02Z71")),
    ("token=QZJ8:Bearer X4Z92Q0X1ZX02Z71", "token=<redacted>Bearer <redacted>", ("QZJ8", "X4Z92Q0X1ZX02Z71")),
    # ... nor end inside a bridge link whose tail runs past `&`
    ("passwd=QZJ8QZJ8.api_key: https://qz-jf.trycloudflare.com/x&s=X4Z92Q0X1ZX02Z71", "passwd=<redacted>api_key: <redacted>",
     ("QZJ8QZJ8", "X4Z92Q0X1ZX02Z71")),
    ("api_key=https://qz-jf.trycloudflare.com/x&s=X4Z92Q0X1ZX02Z71", "api_key=<redacted>", ("X4Z92Q0X1ZX02Z71",)),
    # a Bearer token must not eat the next Bearer keyword, nor a bridge link's `https`
    ("Authorization: Bearer QZJ8QZJ8QZJ8Bearer X4Z92Q0X1ZX02Z71", "Authorization: Bearer <redacted>Bearer <redacted>",
     ("QZJ8QZJ8QZJ8", "X4Z92Q0X1ZX02Z71")),
    ("Bearer QZJ8QZJ8QZJ8https://qz-jf.trycloudflare.com/X4Z92Q0X1ZX02Z71", "Bearer <redacted>https://<bridge-link-redacted>",
     ("QZJ8QZJ8QZJ8", "X4Z92Q0X1ZX02Z71")),
)


@pytest.mark.parametrize("text,scrubbed,secrets", LATER_RULES)
def test_a_match_leaves_a_later_rule_its_whole_match(text, scrubbed, secrets):
    out = SCRUB(text)
    for s in secrets:
        assert s not in out, f"a later rule's secret survived: {out!r}"
    assert out == scrubbed, f"the output moved: {out!r}"


# Negative controls: plain assignments, two chained shapes the old rule already split (separate runs), a name with no value,
# a short non-secret value, and the planted classes. Each output is the PIN's (9801fb5), pasted from a run of its scrub.
PIN_OUTPUTS = (
    ("api_key: QZJ8QZJ8QZJ8", "api_key: <redacted>"),
    ('password = "X4Z92Q0X1ZX02Z71"', 'password = "<redacted>"'),
    ("key: service-API_KEY: QZJ8QZJ8QZJ8", "key: service-API_KEY: <redacted>"),
    ("mask-PASSWORD=QZJ8QZJ8QZJ8;token: WQ7XWQ7XWQ7XWQ7X", "mask-PASSWORD=<redacted>;token: <redacted>"),
    # a link that ends inside the value run, and a Bearer whose rule takes no token, stay part of the value
    ("api_key=https://qz-jf.trycloudflare.com/exec", "api_key=<redacted>"),
    ("api_key=QZJ8QZJ8QZJ8Bearer short", "api_key=<redacted> short"),
    ("Bearer QZJ8QZJ8QZJ8Bearer short", "Bearer <redacted> short"),
    ("x_key=QZJ8QZJ8QZJ8", "x_key=<redacted>"),
    ("api_key:", "api_key:"),
    ("password=", "password="),
    ("token = ", "token = "),
    ("X-Secret-Key:", "X-Secret-Key:"),
    ("sort_key: name", "sort_key: name"),
    ('"api_key": short', '"api_key": short'),
    ("DB_PASSWORD=short", "DB_PASSWORD=short"),
    ("my_API_KEY=short", "my_API_KEY=short"),
    ("token: abc1234", "token: abc1234"),
    (PLANTED["bridge-token-assign"], "AGENT_TOKEN=<redacted>"),
    (PLANTED["env-token"], "PC_BRIDGE_TOKEN=<redacted>"),
    (PLANTED["header"], "X-Agent-Token: <redacted>"),
    (PLANTED["bearer"], "Authorization: Bearer <redacted>"),
    (PLANTED["openai-key"], "sk-<redacted>"),
    (PLANTED["github-pat"], "gh<redacted>"),
    (PLANTED["google-key"], "AIza<redacted>"),
    (PLANTED["yaml-key"], "api_key: <redacted>"),
    (PLANTED["bridge-url"], "https://<bridge-link-redacted>"),
    (PLANTED["opaque"], "token=<redacted>"),
)


@pytest.mark.parametrize("text,pin_output", PIN_OUTPUTS)
def test_negative_controls_keep_their_pin_output(text, pin_output):
    assert SCRUB(text) == pin_output


def test_value_head_check_stays_linear_on_a_long_run():
    # The value's head check runs at every value character; it must stay linear (a compound name without its anchor there
    # would re-scan the rest of a long run at each position: AF-AP-152).
    import time
    t0 = time.monotonic()
    out = SCRUB("password=" + "Ab1" * 14000 + " done")
    assert time.monotonic() - t0 < 3, "the value's head check is not linear on a long run"
    assert out == "password=<redacted> done", out[:60]


def test_chained_values_never_reach_disk(tmp_path):
    # the outward path: one turn per shape through the real CLI
    rows = CHAINED + IN_RUN + LATER_RULES
    jsonl = tmp_path / "chained.jsonl"
    jsonl.write_text("".join(_entry("user", text, f"2026-09-23T15:{i:02d}:00Z") + "\n" for i, (text, _, _) in enumerate(rows)))
    out = tmp_path / "out"
    r = _run(jsonl, out)
    assert r.returncode == 0, r.stderr
    blob = (out / "chat-2026-09-23.md").read_text()
    for _, scrubbed, secrets in rows:
        for s in secrets:
            assert s not in blob, f"a chained value reached disk: {s[:4]}…"
        assert f"\n{scrubbed}\n" in blob, scrubbed


def test_missing_transcript_exits_3(tmp_path):
    r = subprocess.run([sys.executable, str(TOOL), "--transcript", str(tmp_path / "nope.jsonl"), "--out", str(tmp_path / "o")],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 3 and "no transcript" in r.stderr


# SESSION-EXPORT (task #252, D-086): tool payloads pass `scrub_payload` (scrub, then payload shapes scrub does not take) and
# the output of a command that names a secret file passes `scrub_strict` (every assignment value, every long mixed run,
# every lone token line). `scrub` itself is unchanged, so every consumer that imports it keeps its output. Each function is
# read at test time, so a module without it fails its own tests only. Every value here is fake.
def _module():
    spec = importlib.util.spec_from_file_location("transcript_export_payload_under_test", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _module()
PRODUCTION_SOURCES = MOD.KNOWN_VALUE_SOURCES          # taken at import, before a test replaces the attribute
TRIPWIRE = (("tripwire", "the production sources, reached in a test", ()),)


@pytest.fixture(autouse=True)
def _never_the_real_sources(monkeypatch):
    """VERIFY-SCRUB1 F1: no test reads a real value-gate source. main() reads MOD.KNOWN_VALUE_SOURCES when it runs, and
    in every test that is a tripwire, a kind the gate refuses before it reads any source, unless the test names fixture
    sources (`_run`'s default holds fakes). The production list itself is pinned as data (the test after the gate's)."""
    monkeypatch.setattr(MOD, "KNOWN_VALUE_SOURCES", TRIPWIRE)


# (text, its scrub_payload output, the fake values of which no byte may survive)
PAYLOAD_SHAPES = (
    # a bridge host with no scheme (the link rule wants http(s)://), one under another scheme, one with two labels
    ("curl -s zq-fake-quartz-tunnel.trycloudflare.com/exec", "curl -s <bridge-link-redacted>/exec", ("zq-fake-quartz",)),
    ("wss://zq-fake-quartz-tunnel.trycloudflare.com/ws", "wss://<bridge-link-redacted>/ws", ("zq-fake-quartz",)),
    ("host a.zq-fake-quartz.trycloudflare.com", "host <bridge-link-redacted>", ("zq-fake-quartz",)),
    # a Bearer token with b64token characters the Bearer rule's class stops at
    ("Authorization: Bearer Fk1eBearerTok0001+Fk1e/Tail0002==", "Authorization: Bearer <redacted>",
     ("Fk1eBearerTok0001", "Tail0002")),
    ("Bearer Fk1eBearerTok0003~Fk1eTail0004 next", "Bearer <redacted> next", ("Fk1eBearerTok0003", "Tail0004")),
    # HTTP Basic credentials in a header
    ("-H 'Authorization: Basic ZmFrZXVzZXI6ZmFrZXBhc3N3b3Jk'", "-H 'Authorization: Basic <redacted>'",
     ("ZmFrZXVzZXI6ZmFrZXBhc3N3b3Jk",)),
    # a password in a URL's userinfo
    ("postgres://fakeuser:Fk1ePgPass0005@db.internal:5432/app", "postgres://fakeuser:<redacted>@db.internal:5432/app",
     ("Fk1ePgPass0005",)),
)


@pytest.mark.parametrize("text,scrubbed,secrets", PAYLOAD_SHAPES)
def test_payload_shapes_scrub_misses_are_scrubbed(text, scrubbed, secrets):
    out = getattr(MOD, "scrub_payload")(text)
    for s in secrets:
        assert s not in out, f"a payload value survived: {out!r}"
    assert out == scrubbed, out


# Negative controls: none of these holds a secret, so scrub_payload leaves each one as it is.
PAYLOAD_KEEP = (
    "see https://example.com/a+b=c and x+y=z",
    "git@github.com:owner/repo.git",
    "mailto:someone@example.com",
    "https://user@example.com/x",
    "http://localhost:20128/v1/chat",
    "user@host:~/dir",
    "the trycloudflare.com docs",
    "Basic auth is off; Authorization: Basic",
    "Authorization: Bearer <redacted>Bearer <redacted>",
    "Bearer <redacted> short",
)


@pytest.mark.parametrize("text", PAYLOAD_KEEP)
def test_payload_rules_keep_text_with_no_secret(text):
    assert getattr(MOD, "scrub_payload")(text) == text


def test_payload_rules_leave_every_pinned_fixture_as_scrub_leaves_it():
    # the payload rules run after scrub; on every fixture above they change nothing scrub produced
    payload = getattr(MOD, "scrub_payload")
    texts = [t for t, _ in PIN_OUTPUTS] + [t for t, _, _ in CHAINED + IN_RUN + LATER_RULES] + [t for t, _ in QUOTED_OR_COMPOUND]
    texts += list(PLANTED.values()) + ["-----BEGIN %s-----\n%s\n-----END %s-----" % (k, KEY_BODY, k) for k in KEY_FAMILIES]
    moved = [t[:24] for t in texts if payload(t) != SCRUB(t)]
    assert moved == [], moved


# (text, its scrub_strict output, the fake values of which no byte may survive)
STRICT_SHAPES = (
    # an env file printed whole: every value goes, whatever its name
    ("PC_BRIDGE_URL=https://zq-fake.trycloudflare.com\nPC_BRIDGE_TOKEN=Fk1eTok0006x\nZQ_ENDPOINT=http://10.9.8.7:20128/v1\n"
     "export ZQ_OTHER='two fake words'\n",
     "PC_BRIDGE_URL=<redacted>\nPC_BRIDGE_TOKEN=<redacted>\nZQ_ENDPOINT=<redacted>\nexport ZQ_OTHER=<redacted>\n",
     ("zq-fake", "Fk1eTok0006x", "10.9.8.7", "two fake words")),
    # grep -n output and a file:line prefix
    ("3:ZQ_SETTING=Fk1eValue0007\nsrc/app.env:7:ZQ_B=Fk1eValue0008", "3:ZQ_SETTING=<redacted>\nsrc/app.env:7:ZQ_B=<redacted>",
     ("Fk1eValue0007", "Fk1eValue0008")),
    # a key file printed raw: a long token, and a short one alone on its line
    ("Fk1eRawKey0009abcdef\nFk1eRaw00010\n", "<redacted>\n<redacted>\n", ("Fk1eRawKey0009", "Fk1eRaw00010")),
    # a long mixed run inside a line, with base64 characters
    ("key is Fk1eMixed/Run0011+abcdefgh== here", "key is <redacted> here", ("Fk1eMixed", "Run0011")),
    # a curl config: each line's value goes
    ('header = "X-Agent-Token: Fk1eHdr0012"\nurl = "https://zq-fake.trycloudflare.com/exec"', "header = <redacted>\nurl = <redacted>",
     ("Fk1eHdr0012", "zq-fake")),
    # the strict pass includes scrub_payload: a key block and a bare bridge host
    ("-----BEGIN OPENSSH PRIVATE KEY-----\n" + KEY_BODY + "\n-----END OPENSSH PRIVATE KEY-----\nzq-fake-host.trycloudflare.com",
     "<private-key-redacted>\n<bridge-link-redacted>", ("AAKCAQ", "zq-fake-host")),
)


@pytest.mark.parametrize("text,scrubbed,secrets", STRICT_SHAPES)
def test_strict_pass_takes_every_value_of_a_secret_file(text, scrubbed, secrets):
    out = getattr(MOD, "scrub_strict")(text)
    for s in secrets:
        assert s not in out, f"a value survived the strict pass: {out!r}"
    assert out == scrubbed, out


# Negative controls: ordinary command output with no assignment, no long mixed run and no lone token line stays.
STRICT_KEEP = (
    "5 passed in 1.20s",
    "tests/test_x.py::test_y PASSED",
    "no such file: /etc/zq.env",
    "/home/user/agent-factory/scripts/pc_lane.sh",
    "short tok9 here",
    "if x > 1: print('ok')",
)


@pytest.mark.parametrize("text", STRICT_KEEP)
def test_strict_pass_keeps_plain_output(text):
    assert getattr(MOD, "scrub_strict")(text) == text


def test_strict_pass_is_a_fixed_point_and_stays_linear():
    import time
    strict = getattr(MOD, "scrub_strict")
    once = strict(STRICT_SHAPES[0][0] + STRICT_SHAPES[4][0])
    assert strict(once) == once
    run = ("Ab1" * 10 + "+") * 1400          # no piece reaches the opaque rule's 40; one run for the strict pass
    t0 = time.monotonic()
    out = strict("A=" + run + "\n" + run + " x\n" + run)
    assert time.monotonic() - t0 < 3, "the strict pass is not linear on a long run"
    assert out == "A=<redacted>\n<redacted> x\n<redacted>", out[:80]


# SESSION-EXPORT AMENDMENT 1, G6: scrub_payload and scrub_strict take an `opaque` callable for the coarse opaque-run rule
# (session_export.py's stable pseudonyms). Every named rule runs first, so a value a named rule takes never reaches the
# callable, even when it is 40+ characters long. Every value here is fake.
NAMED_LONG = (
    ("PC_BRIDGE_TOKEN=" + "Q7" * 22, "PC_BRIDGE_TOKEN=<redacted>"),
    ("ghp_" + "Zq9" * 14, "gh<redacted>"),
    ("host " + "zq" * 22 + ".trycloudflare.com", "host <bridge-link-redacted>"),
    ("Bearer Fk1eBearerTok0001+" + "Q7" * 22, "Bearer <redacted>"),
    ("Authorization: Basic " + "Zm9v" * 11, "Authorization: Basic <redacted>"),
    ("postgres://u:" + "Q7" * 22 + "@db/x", "postgres://u:<redacted>@db/x"),
)


@pytest.mark.parametrize("text,scrubbed", NAMED_LONG)
def test_named_rules_take_a_long_value_before_the_opaque_rule(text, scrubbed):
    seen = []
    out = getattr(MOD, "scrub_payload")(text, opaque=lambda m: seen.append(m.group(0)) or "[opaque:x]")
    assert out == scrubbed and seen == [], (out, len(seen))


def test_the_opaque_callable_gets_only_what_no_named_rule_takes():
    sha = "0123456789abcdef" * 2 + "01234567"                       # a fake 40-hex commit id
    seen = []
    out = getattr(MOD, "scrub_payload")("pushing %s to origin" % sha, opaque=lambda m: seen.append(m.group(0)) or "[opaque:x]")
    assert out == "pushing [opaque:x] to origin" and seen == [sha]
    assert getattr(MOD, "scrub_payload")("pushing %s" % sha) == "pushing <opaque-redacted>"      # no callable: the marker
    assert getattr(MOD, "scrub_strict")("sha " + sha, opaque=lambda m: "[opaque:x]") == "sha [opaque:x]"


# SESSION-EXPORT-R1 (task #252, the one D-031 repair of VERIFY-SESSION-EXPORT). Every value here is fake.
def _canon(obj):
    """What session_export.py writes for a tool input, a hook, an attachment or a system record."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


R = "<redacted>"
# R-1 (F-1): a named credential whose value sits behind a JSON-escaped quote. (the object, its fake value): the verifier's
# seven shapes (attack 1's json-* rows), then the same class one level deeper, as a JSON Basic header and under a PASS name.
ESCAPED = (
    ({"command": 'export PC_BRIDGE_TOKEN="%s" && bash scripts/pc.sh ls', "description": "x"}, "Fk1eEscTok0001"),
    ({"command": "curl -s -d '{\"password\": \"%s\"}' https://api.example.com/login"}, "Fk1eEscPwd0002"),
    ({"content": '{\n  "api_key": "%s",\n  "region": "eu"\n}\n', "file_path": "/srv/app/service.json"}, "Fk1eEscKey0003"),
    ({"file_path": "/srv/app/app.yaml", "new_string": 'token: "%s"', "old_string": 'token: "x"'}, "Fk1eEscTok0004"),
    ({"hookName": "PostToolUse:Bash", "stdout": '{"token": "%s"}', "type": "hook_success"}, "Fk1eEscTok0005"),
    ({"data": {"note": 'secret: "%s"'}, "type": "structured_output"}, "Fk1eEscSec0006"),
    ({"hookErrors": ['retry with password="%s"'], "subtype": "stop_hook_summary"}, "Fk1eEscPwd0007"),
    ({"command": 'curl -d "{\\"password\\": \\"%s\\"}" https://api.example.com/login'}, "Fk1eEscPwd0008"),
    ({"content": '{"headers": {"Authorization": "Basic %s"}}', "file_path": "/srv/app/h.json"}, "Zk1lRXNjQmFzaWMwMDA5"),
    ({"command": 'export DB_PASS="%s" && ./run.sh'}, "Fk1eEscPass0010"),
)


def _fill(obj, value):
    """obj with every `%s` in its strings replaced by value."""
    if isinstance(obj, str):
        return obj.replace("%s", value)
    if isinstance(obj, dict):
        return {k: _fill(v, value) for k, v in obj.items()}
    return [_fill(v, value) for v in obj] if isinstance(obj, list) else obj


@pytest.mark.parametrize("obj,value", ESCAPED)
def test_a_credential_behind_an_escaped_quote_is_redacted(obj, value):
    out = getattr(MOD, "scrub_payload")(_canon(_fill(obj, value)))
    assert value not in out and not any(value[i:i + 8] in out for i in range(len(value) - 7)), "the value survived"
    assert out == _canon(_fill(obj, R)), out              # the rest stays as it was, and the escaping stays whole
    assert json.loads(out) == _fill(obj, R)


def test_an_escaped_long_token_is_redacted_not_pseudonymized():
    # AMENDMENT 1 G6: a value a named rule takes is redacted, never a pseudonym; behind an escaped quote the credential
    # rule missed it and only the opaque rule's callable saw it (VERIFY-SESSION-EXPORT attack 3, tok44-esc)
    obj = {"command": 'export PC_BRIDGE_TOKEN="%s" && bash scripts/pc.sh ls'}
    seen = []
    out = getattr(MOD, "scrub_payload")(_canon(_fill(obj, "Q7" * 22)),
                                        opaque=lambda m: seen.append(m.group(0)) or "[opaque:x]")
    assert (out, len(seen)) == (_canon(_fill(obj, R)), 0)


# R-3: named shapes the payload pass missed (F-5, F-6). (text, its scrub_payload output, the fake values)
NAMED_R3 = (
    ("authorization: bearer Fk1eBearerLow0011", "authorization: bearer " + R, ("Fk1eBearerLow0011",)),
    ('"authorization": "bearer Fk1eBearerLow0012"', '"authorization": "bearer ' + R + '"', ("Fk1eBearerLow0012",)),
    ("then use bearer Fk1eBearerBare0013 here", "then use bearer " + R + " here", ("Fk1eBearerBare0013",)),
    ("curl -s -u bob:Fk1eCurlPass0014 https://api.example.com/v1/me", "curl -s -u bob:" + R + " https://api.example.com/v1/me",
     ("Fk1eCurlPass0014",)),
    ('curl --user "bob:Fk1eCurlPass0015" https://x', 'curl --user "bob:' + R + '" https://x', ("Fk1eCurlPass0015",)),
    (_canon({"command": 'curl -u "bob:Fk1eCurlPass0016" https://x'}), _canon({"command": 'curl -u "bob:' + R + '" https://x'}),
     ("Fk1eCurlPass0016",)),
    ("DB_HOST=db.internal\nDB_PASS=Fk1eDbPass0017\n", "DB_HOST=db.internal\nDB_PASS=" + R + "\n", ("Fk1eDbPass0017",)),
    ("SMTP-PASS: Fk1eSmtpPass0018", "SMTP-PASS: " + R, ("Fk1eSmtpPass0018",)),
    ("PASS=Fk1eBarePass0019", "PASS=" + R, ("Fk1eBarePass0019",)),
    # inside a quoted string of canonical JSON: the escape of the closing quote stays, so the JSON stays valid
    (_canon({"command": 'docker run -e "DB_PASS=Fk1eDockPass0025" img'}),
     _canon({"command": 'docker run -e "DB_PASS=' + R + '" img'}), ("Fk1eDockPass0025",)),
    ("origin https://Fk1eUrlToken0020x@github.com/zq/zq.git (fetch)", "origin https://" + R + "@github.com/zq/zq.git (fetch)",
     ("Fk1eUrlToken0020x",)),
    ("https://bob:Fk1eAtPart0021@Fk1eAtTail0022@db.example.com/app", "https://bob:" + R + "@db.example.com/app",
     ("Fk1eAtPart0021", "Fk1eAtTail0022")),
)


@pytest.mark.parametrize("text,scrubbed,secrets", NAMED_R3)
def test_r3_named_shapes_are_scrubbed(text, scrubbed, secrets):
    out = getattr(MOD, "scrub_payload")(text)
    for s in secrets:
        assert s not in out, "a value survived"
    assert out == scrubbed, out


# Names that end in PASSWD or PASSWORD were scrub's own credential names before R1 (a pin, not a new rule).
@pytest.mark.parametrize("text,scrubbed", (("DB_PASSWD=Fk1eDbPasswd0023", "DB_PASSWD=" + R),
                                           ("MYSQL_ROOT_PASSWORD: Fk1eRootPw0024", "MYSQL_ROOT_PASSWORD: " + R)))
def test_passwd_and_password_names_stay_scrubbed(text, scrubbed):
    assert getattr(MOD, "scrub_payload")(text) == scrubbed


# Negative controls for R-1 and R-3: text with no secret stays as it is.
PAYLOAD_KEEP_R1 = (
    "the bearer of bad news", "bearer tokens are fine here", "authorization: bearer short",
    "python3 -u script.py", "git push -u origin main", "docker run -u 1000 img",
    "BYPASS=abcdefghij", "COMPASS_HEADING=northnorth", "--- PASS: TestSomethingLongEnough (0.00s)",
    "PASS: tests/test_x.py::test_a_long_name_here", "https://john.doe@example.com/x", "https://mirror@example.com/x",
    _canon({"command": 'export PC_BRIDGE_TOKEN="short"'}), _canon({"note": 'token: "a b c d e f g h"'}),
    # what the first R-3 rules took thousands of times in the real transcripts (R1's own measurement): `date -u`, other
    # `-u` flags, code variables that end in `pass`, and `$` references
    "date -u +%H:%M:%SZ", _canon({"command": "date -u +%Y-%m-%dT%H:%M:%SZ && ls"}), "docker run -u 1000:1000 img",
    "first_pass = something_long_here", "n_pass=len(results)", "PASS=$((PASS+1))", 'curl -u "$USER:$PASS" https://x',
    "DB_PASS=$SECRET_FROM_VAULT", _canon({"content": 'first_pass = "something_long_here"'}),
)


@pytest.mark.parametrize("text", PAYLOAD_KEEP_R1)
def test_r1_rules_keep_text_with_no_secret(text):
    assert getattr(MOD, "scrub_payload")(text) == text


def test_r1_rules_stay_linear_on_long_runs():
    import time
    payload = getattr(MOD, "scrub_payload")
    for text in ("password\\\": " * 4000, "token" + "\\" * 40000 + "x", "bearer " * 6000, "-u a " * 8000, "_PASS" * 8000,
                 "ab://" * 8000, "curl -x " * 8000):
        t0 = time.monotonic()
        payload(text)
        assert time.monotonic() - t0 < 3, text[:12]


# AMENDMENT 3: scrub_strict leaves a value, run or token in `keep` (the repo's committed runs) as it is; the named rules
# still run first, so a committed fake token under a credential name is redacted all the same.
COMMITTED = frozenset(("tests/test_zq_s0_01_committed_path", "tests/test_zq_s0_01_committed_path.py",
                       "claude/zq-committed-branch-01", "ZQfake0committed0fixture0token0v1"))


def test_strict_pass_keeps_committed_runs():
    strict = getattr(MOD, "scrub_strict")
    text = ("tests/test_zq_s0_01_committed_path.py::test_x PASSED\n"          # a key run
            "tests/test_zq_s0_01_committed_path.py\n"                         # a token line
            "ZQ_BRANCH=claude/zq-committed-branch-01\n"                       # an assignment value
            "ZQ_RUN=zq7run7id7not7committed7x9\n"                              # not committed: redacted
            "QZ7uncommittedkeyrun0000000000 left\n"                            # not committed: redacted
            "PC_BRIDGE_TOKEN=ZQfake0committed0fixture0token0v1\n"            # a named rule takes it first
            "ZQfake0committed0fixture0token0v1\n")                            # committed, alone on its line: kept
    out = strict(text, keep=COMMITTED)
    assert out == ("tests/test_zq_s0_01_committed_path.py::test_x PASSED\ntests/test_zq_s0_01_committed_path.py\n"
                   "ZQ_BRANCH=claude/zq-committed-branch-01\nZQ_RUN=" + R + "\n" + R + " left\nPC_BRIDGE_TOKEN=" + R + "\n"
                   "ZQfake0committed0fixture0token0v1\n"), out
    assert strict(out, keep=COMMITTED) == out                               # a fixed point
    # negative control: without the committed runs every one of them is redacted, as before AMENDMENT 3
    assert strict(text) == (R + ".py::test_x PASSED\n" + R + ".py\nZQ_BRANCH=" + R + "\nZQ_RUN=" + R + "\n" + R + " left\n"
                            "PC_BRIDGE_TOKEN=" + R + "\n" + R + "\n")


def test_run_shapes_are_the_rules_own_shapes():
    # the set session_export.py builds uses the opaque rule's own pattern, the key-run rule's and the token-line class
    shapes = getattr(MOD, "RUN_SHAPES")
    opaque = [p for p, r in MOD.SECRET_PATTERNS if r == MOD.OPAQUE_MARK]
    assert len(shapes) == 3 and shapes[0] is opaque[0] and shapes[1] is MOD._KEY_RUN
    assert shapes[2].pattern + "" == MOD._TOKEN_LINE.pattern.split("(", 3)[3].split(")")[0]


# SCRUB1 (task #280, AF-AP-224): the four provider-key rules were anchored on `\b`, which wants a non-word character before
# the key, so a key glued to a preceding `_` passed whole. The anchor is now `(?<![A-Za-z0-9])`. Every key here is fake and
# built at run time; each context keeps the key's run under the opaque rule's 40 characters, so only its rule can take it.
def _fake_keys():
    t = token_hex
    return {"sk": ["sk-" + t(12), "sk-proj-" + t(8)], "gh": [p + "_" + t(12) for p in ("ghp", "gho", "ghu", "ghs", "ghr")],
            "AIza": ["AIza" + t(15)], "xox": ["xox%s-%s" % (c, t(6)) for c in "abprs"]}


MARK = {"sk": "sk-<redacted>", "gh": "gh<redacted>", "AIza": "AIza<redacted>", "xox": "xox-<redacted>"}
CONTEXTS = (("standalone", "{k}"), ("after =", "ZQ={k}"), ("after a double quote", '"{k}"'), ("after a quote", "'{k}'"),
            ("after _", "zq_{k}"), ("after __", "zq__{k}"), ("in a URL query", "https://api.zq.example/v1?q={k}&x=1"),
            ("in a URL path", "https://api.zq.example/v1/{k}/x"), ("at a line start", "first line\n{k} rest"),
            ("at a line end", "first {k}\nnext line"))
GLUED = ("after _", "after __")
# The PIN's four rules (03ca747:scripts/transcript_export.py:74-77), for the negative controls below.
PIN_RULES = (r"\bsk-[A-Za-z0-9_\-]{12,}\b", r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b", r"\bAIza[0-9A-Za-z_\-]{30,}\b",
             r"\bxox[abprs]-[A-Za-z0-9\-]{10,}\b")


def _misses(scrub_fn):
    """[(rule, context)] where a key's random tail survives scrub_fn, or the output is not the context with the key
    replaced by its rule's marker (the text around the key stays)."""
    out = set()
    for rule, keys in _fake_keys().items():
        for key in keys:
            for name, ctx in CONTEXTS:
                got = scrub_fn(ctx.format(k=key))
                if key[-12:] in got or got != ctx.format(k=MARK[rule]):
                    out.add((rule, name))
    return sorted(out)


def _scrub_with(rules):
    """MOD's scrub with its four provider rules replaced by `rules` (in the order of MARK)."""
    marks = list(MARK.values())
    pats = [(re.compile(rules[marks.index(r)]), r) if r in marks else (p, r) for p, r in MOD.SECRET_PATTERNS]
    assert sum(r in marks for _, r in pats) == 4

    def run(text):
        for p, r in pats:
            text = p.sub(r, text)
        return text
    return run


def test_every_provider_rule_takes_its_key_in_every_context():
    assert _misses(SCRUB) == []
    assert _misses(getattr(MOD, "scrub_payload")) == []          # session_export's scrubber runs the same rules


def test_the_context_test_reds_on_the_pin_rules_exactly_at_the_glued_contexts():
    # negative control: the PIN's `\b` rules miss every rule's key after `_` and `__`, and nothing else
    assert _misses(_scrub_with(PIN_RULES)) == sorted((rule, g) for rule in MARK for g in GLUED)


# A letter before the prefix is not a separator: `task-` is the word a letter anchor would take 17,258 times in this
# session's transcripts (the `<task-notification>` tag, SCRUB1's measurement). The brief's five words first.
ORDINARY = ("task-notification-center", "the risk-register-entries list", "disk-usage-report-weekly",
            "skip-validation-checks-now", "ghost_protocol_engaged_now_x", "<task-notification>",
            "subtask-breakdown-for-stage0", "desk-assignment-roster-q3", "flask-application-factory",
            "laughs_AtTheMoonAndStarsTogether")


def test_ordinary_words_are_not_redacted():
    assert [t for t in ORDINARY if SCRUB(t) != t] == []


def test_the_ordinary_words_red_on_rules_that_take_a_letter_before_the_key():
    # negative control: with no left anchor (a key glued to a letter matched too) every word that holds a prefix is taken
    wide = _scrub_with(tuple(r[2:] for r in PIN_RULES))
    assert [t for t in ORDINARY if wide(t) == t] == ["skip-validation-checks-now", "ghost_protocol_engaged_now_x"]


def test_glued_keys_never_reach_disk(tmp_path):
    # the outward path: every fake key glued after `_` and `__`, one turn each, through the real CLI
    keys = [k for ks in _fake_keys().values() for k in ks]
    jsonl = tmp_path / "glued.jsonl"
    jsonl.write_text("".join(_entry("user", "tool mcp__zq__%s and zq_%s" % (k, k), "2026-09-25T18:%02d:00Z" % i) + "\n"
                             for i, k in enumerate(keys)))
    r = _run(jsonl, tmp_path / "out")
    assert r.returncode == 0, r.stderr
    blob = (tmp_path / "out" / "chat-2026-09-25.md").read_text()
    assert [k[:4] for k in keys if k[-12:] in blob] == []
    assert blob.count("mcp__zq__") == blob.count("zq_") - blob.count("mcp__zq__") == len(keys)


# SCRUB1 contract item 2: the value gate. A fixture source holds a fake value built at run time: 32 hex characters, a shape
# no rule takes (no name, under the opaque rule's 40), so only the gate can stop it. Output: source names and counts only.
def _fake_value():
    return "7" + token_hex(16)[1:]                         # a digit, so its 8-byte windows count (known_values)


def _turns(tmp_path, *texts):
    """A transcript of one user turn per text, one day each (2026-09-21, 2026-09-22, ...)."""
    jsonl = tmp_path / "gate.jsonl"
    jsonl.write_text("".join(_entry("user", t, "2026-09-%02dT18:00:00Z" % (21 + i)) + "\n" for i, t in enumerate(texts)))
    return str(jsonl)


def _no_piece(value, text):
    return not any(value[i:i + 8] in text for i in range(len(value) - 7))


def test_the_value_gate_refuses_a_known_value_and_writes_nothing(tmp_path):
    fake = _fake_value()
    env = tmp_path / "zq.env"
    env.write_text("ZQ_FAKE_TOKEN=%s\n" % fake)
    src, out = (("env-file", str(env), ()),), tmp_path / "out"
    with pytest.raises(MOD.KnownValueRefusal) as e:           # the first day is clean, the second holds the value
        MOD.export(_turns(tmp_path, "a clean day", "the value is %s here" % fake), str(out), 4000, sources=src)
    assert e.value.args[0] == ["zq.env:ZQ_FAKE_TOKEN value whole=1 windows=25/25"]
    assert not out.exists() and _no_piece(fake, repr(e.value.args))     # no file, no directory, no piece of the value
    # positive control: the same days and source without the value are written
    written = MOD.export(_turns(tmp_path, "a clean day", "the value is not here"), str(out), 4000, sources=src)
    assert [pathlib.Path(p).name for p in written] == ["chat-2026-09-21.md", "chat-2026-09-22.md"]
    assert "the value is not here" in (out / "chat-2026-09-22.md").read_text()


def test_the_value_gate_reads_the_scrubbed_text(tmp_path):
    # a known value that a named rule takes never reaches the digest, so it does not block it (the gate reads what is written)
    fake = _fake_value()
    env = tmp_path / "zq.env"
    env.write_text("ZQ_FAKE_TOKEN=%s\n" % fake)
    out = tmp_path / "out"
    MOD.export(_turns(tmp_path, "the bridge token=%s set" % fake), str(out), 4000, sources=(("env-file", str(env), ()),))
    assert (out / "chat-2026-09-21.md").read_text().endswith("the bridge token=<redacted> set\n")


def test_the_value_gate_counts_a_cut_copy_by_its_windows(tmp_path):
    fake = _fake_value()
    env = tmp_path / "zq.env"
    env.write_text("ZQ_FAKE_TOKEN=%s\n" % fake)
    with pytest.raises(MOD.KnownValueRefusal) as e:
        MOD.export(_turns(tmp_path, "a cut copy %s ends" % fake[:12]), str(tmp_path / "out"), 4000,
                   sources=(("env-file", str(env), ()),))
    assert e.value.args[0] == ["zq.env:ZQ_FAKE_TOKEN value whole=0 windows=5/25"]


def test_the_value_gate_reads_a_variable_and_a_raw_key_file(tmp_path, monkeypatch):
    fake = _fake_value()
    raw = bytes(0xA0 | b & 0x0F for b in token_bytes(12))   # every byte's hex holds a letter: hex and HEX differ
    (tmp_path / "zq.key").write_bytes(raw)
    monkeypatch.setenv("ZQ_FAKE_GATE_VAR", fake)
    src = (("env", "ZQ_FAKE_GATE_VAR", ()), ("raw-file", str(tmp_path / "zq.key"), ()))
    with pytest.raises(MOD.KnownValueRefusal) as e:
        MOD.export(_turns(tmp_path, "var %s and key %s" % (fake, raw.hex())), str(tmp_path / "out"), 4000, sources=src)
    assert e.value.args[0] == ["env:ZQ_FAKE_GATE_VAR value whole=1 windows=25/25", "zq.key:raw hex whole=1 windows=17/17"]


def test_the_value_gate_skips_a_missing_source_with_one_line(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("ZQ_UNSET_GATE_VAR", raising=False)
    monkeypatch.setenv("ZQ_SHORT_GATE_VAR", "short")                # under 8 characters: not a secret
    src = (("env-file", str(tmp_path / "none.env"), ()), ("raw-file", str(tmp_path / "none.key"), ()),
           ("env", "ZQ_UNSET_GATE_VAR", ()), ("env", "ZQ_SHORT_GATE_VAR", ()))
    assert len(MOD.export(_turns(tmp_path, "plain text"), str(tmp_path / "out"), 4000, sources=src)) == 1
    assert capsys.readouterr().err.splitlines() == [
        "transcript_export: value gate: source %s missing or empty, skipped" % s
        for s in (tmp_path / "none.env", tmp_path / "none.key", "env:ZQ_UNSET_GATE_VAR", "env:ZQ_SHORT_GATE_VAR")]


def test_a_hostname_does_not_block_when_its_key_holds_no_secret(tmp_path):
    env = tmp_path / "zq.env"
    env.write_text("ZQ_BASE_URL=https://api.zq-fake.example/v1\n")
    text = "the service at api.zq-fake.example answered"
    assert len(MOD.export(_turns(tmp_path, text), str(tmp_path / "out"), 4000,
                          sources=(("env-file", str(env), ("ZQ_BASE_URL",)),))) == 1
    # negative control: the same source with no skip counts the host
    with pytest.raises(MOD.KnownValueRefusal) as e:
        MOD.export(_turns(tmp_path, text), str(tmp_path / "out2"), 4000, sources=(("env-file", str(env), ()),))
    assert e.value.args[0] == ["zq.env:ZQ_BASE_URL host whole=1 windows=0/0"]
    # the production list skips the public base URL whose host the committed digests hold (the premise's one hit)
    assert ("env-file", "/root/.codiv/api.env", ("TYPESAFE_BASE_URL",)) in PRODUCTION_SOURCES


def test_the_value_gate_fails_closed_on_a_source_it_cannot_read(tmp_path):
    (tmp_path / "zq-dir.env").mkdir()                                # present, and open() fails on it
    with pytest.raises(MOD.KnownValueRefusal) as e:
        MOD.export(_turns(tmp_path, "plain text"), str(tmp_path / "out"), 4000,
                   sources=(("env-file", str(tmp_path / "zq-dir.env"), ()),))
    assert e.value.args[0] == ["value gate: cannot read the source zq-dir.env (IsADirectoryError)"]
    assert not (tmp_path / "out").exists()


def test_the_cli_refuses_with_exit_4_and_prints_names_and_counts_only(tmp_path, monkeypatch):
    # main() with fixture sources whose fake values are pasted into the transcript: an env file's and a variable's
    fake, var = _fake_value(), _fake_value()
    env = tmp_path / "zq.env"
    env.write_text("ZQ_FAKE_TOKEN=%s\n" % fake)
    monkeypatch.setenv("ZQ_FAKE_GATE_VAR", var)
    src = (("env-file", str(env), ()), ("env", "ZQ_FAKE_GATE_VAR", ()))
    jsonl, out = tmp_path / "cli.jsonl", tmp_path / "out"
    jsonl.write_text(_entry("user", "a pasted value %s and %s here" % (fake, var), "2026-09-25T18:00:00Z") + "\n")
    r = _run(jsonl, out, sources=src)
    assert r.returncode == 4, r.stderr
    assert r.stderr.splitlines() == ["transcript_export: REFUSED, nothing written: zq.env:ZQ_FAKE_TOKEN value whole=1 windows=25/25",
                                     "transcript_export: REFUSED, nothing written: env:ZQ_FAKE_GATE_VAR value whole=1 windows=25/25"]
    assert r.stdout == "" and not out.exists() and _no_piece(fake, r.stderr) and _no_piece(var, r.stderr)
    # positive control: the same sources, and a transcript without the values
    jsonl.write_text(_entry("user", "nothing pasted here", "2026-09-25T18:00:00Z") + "\n")
    r = _run(jsonl, out, sources=src)
    assert r.returncode == 0 and r.stdout.strip() == str(out / "chat-2026-09-25.md"), r.stderr


# SCRUB2 (task #292; VERIFY-SCRUB1 F1-F3, F8-F10, F12-F14). Item 4: the sources. main() reads the module's tuple when it
# runs, export() and known_values() take theirs from the caller, and the production tuple is pinned as data, never opened.
def test_the_production_sources_are_the_five_known_ones():
    # VERIFY-SCRUB1 F8: a wrong entry fails silently in production (its skip line goes to stderr, which push_clean
    # discards), so the list is pinned whole: the bridge env beside the repo root, the API env with its public base URL
    # skipped, the raw pseudonym key, the two token variables
    bridge_dir, bridge_name = os.path.split(PRODUCTION_SOURCES[0][1])
    assert (os.path.realpath(bridge_dir), bridge_name) == (str(ROOT), ".pc-bridge.env")
    assert PRODUCTION_SOURCES == (("env-file", os.path.join(bridge_dir, ".pc-bridge.env"), ()),
                                  ("env-file", "/root/.codiv/api.env", ("TYPESAFE_BASE_URL",)),
                                  ("raw-file", "/root/.config/session-export/pseudonym.key", ()),
                                  ("env", "GH_TOKEN", ()),
                                  ("env", "GITHUB_TOKEN", ()))


def test_main_reads_the_sources_when_it_runs(tmp_path, monkeypatch):
    # VERIFY-SCRUB1 F1: export()'s default was bound when export() was defined, so a replaced module attribute never
    # reached main(), which always read the real sources. The tuple main() finds when it runs is now the one it uses.
    fake = _fake_value()
    env = tmp_path / "zq.env"
    env.write_text("ZQ_FAKE_TOKEN=%s\n" % fake)
    monkeypatch.setattr(MOD, "KNOWN_VALUE_SOURCES", (("env-file", str(env), ()),))
    jsonl, out = tmp_path / "t.jsonl", tmp_path / "out"
    jsonl.write_text(_entry("user", "the value %s here" % fake, "2026-09-25T18:00:00Z") + "\n")
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = MOD.main(["--transcript", str(jsonl), "--out", str(out)])
    assert (rc, err.getvalue().splitlines()) == (4, [
        "transcript_export: REFUSED, nothing written: zq.env:ZQ_FAKE_TOKEN value whole=1 windows=25/25"])
    assert not out.exists()


def test_export_and_known_values_take_their_sources_from_the_caller():
    # no default is bound at definition time: a call that names no sources is an error, never the production list
    for fn in (MOD.export, MOD.known_values):
        assert inspect.signature(fn).parameters["sources"].default is inspect.Parameter.empty, fn.__name__
    with pytest.raises(TypeError):
        MOD.export(os.devnull, os.devnull, 4000)


def test_a_test_that_names_no_sources_meets_the_tripwire(tmp_path):
    # the autouse fixture: main() in a test that names no sources refuses on the tripwire, before any source is read
    jsonl = tmp_path / "t.jsonl"
    jsonl.write_text(_entry("user", "plain text", "2026-09-25T18:00:00Z") + "\n")
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc = MOD.main(["--transcript", str(jsonl), "--out", str(tmp_path / "out")])
    assert (rc, err.getvalue().splitlines()) == (4, ["transcript_export: REFUSED, nothing written: value gate: the source "
                                                     "the production sources, reached in a test has an unknown kind 'tripwire'"])
    assert not (tmp_path / "out").exists()


def test_nothing_outside_the_process_can_replace_the_sources():
    # only code in the process replaces the sources (the module attribute, export's argument): the CLI takes no option
    # for them, the tuple is assigned once, and the module reads the environment only for a source of kind env, so
    # push_clean's sync, which runs the plain CLI, always gets the production list
    out = io.StringIO()
    with contextlib.redirect_stdout(out), pytest.raises(SystemExit) as e:
        MOD.main(["--help"])
    assert e.value.code == 0 and set(re.findall(r"--[a-z]+", out.getvalue())) == {"--help", "--transcript", "--out", "--cap"}
    src = TOOL.read_text()
    assert re.findall(r"os\.environ[^\n]*", src) == ['os.environ.get(where, "").encode()']
    assert re.findall(r"getenv|putenv", src) == [] and re.findall(r"(?m)^KNOWN_VALUE_SOURCES\b.*", src) == [
        "KNOWN_VALUE_SOURCES = ("]


# Item 5: the gate's sources. A child process runs export() where a source could block a read: a hang then fails the
# test by its timeout instead of stopping the suite.
CHILD = r"""
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("transcript_export_child", sys.argv[1])
te = importlib.util.module_from_spec(spec)
spec.loader.exec_module(te)
try:
    te.export(sys.argv[2], sys.argv[3], 4000, sources=tuple((k, w, tuple(s)) for k, w, s in json.loads(sys.argv[4])))
except te.KnownValueRefusal as e:
    print("\n".join(e.args[0]))
    sys.exit(4)
"""


def _export_in_a_child(tmp_path, sources, *texts):
    """export() in a child process with these fixture sources ([kind, where, skip] lists); its exit code and stdout."""
    r = subprocess.run([sys.executable, "-c", CHILD, str(TOOL), _turns(tmp_path, *texts), str(tmp_path / "out"),
                        json.dumps(sources)], capture_output=True, text=True, timeout=20)
    return r.returncode, r.stdout.splitlines()


def test_a_source_that_is_not_a_regular_file_refuses_at_once(tmp_path):
    # VERIFY-SCRUB1 F10: a FIFO source hung the export at open() (it waits for a writer); a device was read as empty
    # and skipped. Each refuses now, before anything is written.
    fifo = tmp_path / "zq-fifo.env"
    os.mkfifo(fifo)
    for kind in ("env-file", "raw-file"):
        assert _export_in_a_child(tmp_path, [[kind, str(fifo), []]], "plain text") == (
            4, ["value gate: cannot read the source zq-fifo.env (NotRegularFile)"]), kind
    assert _export_in_a_child(tmp_path, [["raw-file", os.devnull, []]], "plain text") == (
        4, ["value gate: cannot read the source null (NotRegularFile)"])
    assert not (tmp_path / "out").exists()


def test_a_malformed_env_line_is_named_by_its_line_number(tmp_path):
    # VERIFY-SCRUB1 F13: a refusal printed an env line's part before `=` verbatim, and on a malformed line that part can
    # hold anything (here a piece of the value). A name that is not an env name is printed as its line number.
    fake = _fake_value()
    env = tmp_path / "zq.env"
    env.write_text("# a comment\nzq %s=%s\nexport ZQ_GOOD_NAME=%s\n" % (fake[:20], fake, fake))
    with pytest.raises(MOD.KnownValueRefusal) as e:
        MOD.export(_turns(tmp_path, "the value %s here" % fake), str(tmp_path / "out"), 4000,
                   sources=(("env-file", str(env), ()),))
    assert e.value.args[0] == ["zq.env:<malformed line 2> value whole=1 windows=25/25",
                               "zq.env:ZQ_GOOD_NAME value whole=1 windows=25/25"]
    assert _no_piece(fake, repr(e.value.args))


def test_a_source_of_an_unknown_kind_is_refused_before_any_source_is_read(tmp_path):
    # VERIFY-SCRUB1 F10: a kind typo (`env_file`) was read as a raw file, so the values in it were never counted. The
    # kinds are checked before any source is read (a FIFO listed first would block a read).
    fake = _fake_value()
    env = tmp_path / "zq.env"
    env.write_text("ZQ_FAKE_TOKEN=%s\n" % fake)
    line = "value gate: the source zq.env has an unknown kind 'env_file'"
    assert _export_in_a_child(tmp_path, [["env_file", str(env), []]], "the value %s here" % fake) == (4, [line])
    fifo = tmp_path / "zq-fifo.key"
    os.mkfifo(fifo)
    assert _export_in_a_child(tmp_path, [["raw-file", str(fifo), []], ["env_file", str(env), []]], "plain") == (4, [line])
    assert not (tmp_path / "out").exists()


def test_a_letter_before_the_key_is_not_a_separator_in_any_rule():
    # VERIFY-SCRUB1 F9 (V5, V6): the ordinary words pin the letter decision for sk and gh only (no word puts a letter
    # before `AIza` or `xox`), so an AIza or xox rule that lost its left anchor passed every test. Pinned per rule.
    for rule, keys in _fake_keys().items():
        for key in keys:
            assert SCRUB("zq" + key + " end") == "zq" + key + " end", rule


def test_the_8_character_floor_counts_8_and_skips_7(tmp_path, monkeypatch, capsys):
    # VERIFY-SCRUB1 F9 (V12): a value of 8 characters is a secret and one of 7 is not, in a variable and in an env file
    v8, v7, f8, f7 = ("7" + token_hex(4)[1:n] for n in (8, 7, 8, 7))
    monkeypatch.setenv("ZQ_GATE_VAR8", v8)
    monkeypatch.setenv("ZQ_GATE_VAR7", v7)
    env = tmp_path / "zq.env"
    env.write_text("ZQ_FILE8=%s\nZQ_FILE7=%s\n" % (f8, f7))
    src = (("env", "ZQ_GATE_VAR8", ()), ("env", "ZQ_GATE_VAR7", ()), ("env-file", str(env), ()))
    with pytest.raises(MOD.KnownValueRefusal) as e:
        MOD.export(_turns(tmp_path, "%s %s %s %s" % (v8, v7, f8, f7)), str(tmp_path / "out"), 4000, sources=src)
    assert e.value.args[0] == ["env:ZQ_GATE_VAR8 value whole=1 windows=0/0", "zq.env:ZQ_FILE8 value whole=1 windows=0/0"]
    assert capsys.readouterr().err.splitlines() == [
        "transcript_export: value gate: source env:ZQ_GATE_VAR7 missing or empty, skipped"]


def test_the_public_base_url_is_skipped_in_its_own_source_only(tmp_path):
    # VERIFY-SCRUB1 F9 (V13): TYPESAFE_BASE_URL is skipped where its source says so (api.env in the production list); the
    # same name in another source is counted like any other
    host = "api-%s.zq-fake.example" % token_hex(3)
    own, other = tmp_path / "own.env", tmp_path / "other.env"
    for f in (own, other):
        f.write_text("TYPESAFE_BASE_URL=https://%s/v1\n" % host)
    text = "the service at %s answered" % host
    assert len(MOD.export(_turns(tmp_path, text), str(tmp_path / "out"), 4000,
                          sources=(("env-file", str(own), ("TYPESAFE_BASE_URL",)),))) == 1
    with pytest.raises(MOD.KnownValueRefusal) as e:
        MOD.export(_turns(tmp_path, text), str(tmp_path / "out2"), 4000,
                   sources=(("env-file", str(own), ("TYPESAFE_BASE_URL",)), ("env-file", str(other), ())))
    assert e.value.args[0] == ["other.env:TYPESAFE_BASE_URL host whole=1 windows=0/0"]


# Items 1 and 2: the right side of the four rules (F2) and a key right after a JSON escape (F3). Every context keeps a
# key's run under the opaque rule's 40, so only its own rule can take it. The expected output is the context with the
# key's run replaced by its marker, the run being the key and what its rule's class takes after it (`_zq` joins an sk
# or AIza key, not a gh or xox one; the `-` before a quote joins every key but gh's).
SCRUB1_RULES = tuple(r"(?<![A-Za-z0-9])" + r[2:] for r in PIN_RULES)       # 49bf75e..f3ab062: only the left anchor moved
BODY = {"sk": r"[A-Za-z0-9_\-]", "gh": r"[A-Za-z0-9]", "AIza": r"[0-9A-Za-z_\-]", "xox": r"[A-Za-z0-9\-]"}
ESCAPES = ("\\n", "\\r", "\\t", "\\b", "\\f", "\\u00e9", "\\u001b")
SCRUB2_CONTEXTS = tuple(("after a literal %s" % e, "zq" + e + "{k} end") for e in ESCAPES) + (
    ("before é", "zq {k}é zq"), ("before の", "zq {k}のです"), ("between é and の", "é{k}の"), ("before _", "zq {k}_zq end"),
    ("before a quote, the key ending in -", "zq '{k}-' end"), ("before a literal \\n", "zq {k}\\nzq"), ("after é", "zqé{k} end"))


def _expected(rule, ctx):
    before, after = ctx.split("{k}")
    return before + MARK[rule] + re.sub("^" + BODY[rule] + "*", "", after)


def _misses2(scrub_fn):
    """[(rule, context)] where scrub_fn's output is not the context with the key's run replaced by its rule's marker."""
    out = set()
    for rule, keys in _fake_keys().items():
        for key in keys:
            for name, ctx in SCRUB2_CONTEXTS:
                if scrub_fn(ctx.replace("{k}", key)) != _expected(rule, ctx):
                    out.add((rule, name))
    return sorted(out)


def test_every_provider_rule_takes_its_key_on_the_right_and_after_an_escape():
    assert _misses2(SCRUB) == []
    assert _misses2(getattr(MOD, "scrub_payload")) == []          # session_export's scrubber runs the same rules


def test_the_scrub2_grid_reds_on_the_scrub1_rules_exactly_where_expected():
    # negative control: SCRUB1's rules (\b on the right, no escape anchor) miss every rule after a literal escape and
    # before or between non-ASCII letters, gh and xox before `_`, and a key ending in `-` before a quote (\b left the `-`)
    want = {(r, "after a literal %s" % e) for r in MARK for e in ESCAPES}
    want |= {(r, c) for r in MARK for c in ("before é", "before の", "between é and の")}
    want |= {("gh", "before _"), ("xox", "before _")} | {(r, "before a quote, the key ending in -") for r in ("sk", "AIza", "xox")}
    assert _misses2(_scrub_with(SCRUB1_RULES)) == sorted(want)


def test_an_xox_token_followed_by_an_underscore_loses_no_segment():
    # VERIFY-SCRUB1 F2: before an `_` the xox rule ended at the token's last hyphen, and the secret last segment stayed
    tok = "xoxb-%s-%s-%s" % (token_hex(5), token_hex(6), token_hex(12))
    text = "zq %s_zq end" % tok
    assert SCRUB(text) == "zq xox-<redacted>_zq end"
    assert _scrub_with(SCRUB1_RULES)(text) == "zq xox-<redacted>%s_zq end" % tok.rsplit("-", 1)[1]    # negative control


# Item 1, the opaque rule (F12): `\b` never holds next to a non-ASCII letter, so a 40+ run glued to one passed on either
# side. Each end is now `\b` or its ASCII form, which keeps every run `\b` took (a dash after `é` still starts one).
def _opaque_contexts():
    """(name, text, its scrub output, the fake of which no piece may survive or None)."""
    t, t39 = token_hex(24), token_hex(20)[:39]
    return (("after é", "café%s zq" % t, "café<opaque-redacted> zq", t),
            ("before é", "zq %sé" % t, "zq <opaque-redacted>é", t),
            ("between の", "の%sの" % t, "の<opaque-redacted>の", t),
            ("after é and a dash, 40 with the dash", "é-%s zq" % t39, "é<opaque-redacted> zq", t39),
            ("standalone", "zq %s zq" % t, "zq <opaque-redacted> zq", t),
            ("after _", "zq_%s zq" % t, "<opaque-redacted> zq", t),
            ("after =", "ZQ=%s" % t, "ZQ=<opaque-redacted>", t),
            ("in a quote", "'%s'" % t, "'<opaque-redacted>'", t),
            ("in a URL path", "https://zq.example/v1/%s/x" % t, "https://zq.example/v1/<opaque-redacted>/x", t),
            ("at a line start", "first line\n%s rest" % t, "first line\n<opaque-redacted> rest", t),
            ("39 after é, under the floor", "é%s zq" % t39, "é%s zq" % t39, None))


def _scrub_with_opaque(pattern):
    """MOD's scrub with its opaque rule's pattern replaced by `pattern`."""
    pats = [(re.compile(pattern), r) if r == MOD.OPAQUE_MARK else (p, r) for p, r in MOD.SECRET_PATTERNS]

    def run(text):
        for p, r in pats:
            text = p.sub(r, text)
        return text
    return run


def test_the_opaque_rule_takes_a_run_next_to_a_non_ascii_letter():
    for name, text, want, _ in _opaque_contexts():
        assert SCRUB(text) == want, name
        assert getattr(MOD, "scrub_payload")(text) == want, name


def test_the_opaque_grid_reds_on_either_boundary_alone():
    # negative controls: `\b` alone (the PIN) misses the three runs glued to a non-ASCII letter; the ASCII boundary alone
    # drops the run `\b` took after `é` and its dash (39 characters are left, under the rule's 40)
    ctx = _opaque_contexts()
    pin = _scrub_with_opaque(r"\b[A-Za-z0-9_\-]{40,}\b")
    ascii_only = _scrub_with_opaque(r"(?a:\b)[A-Za-z0-9_\-]{40,}(?a:\b)")
    assert [n for n, text, want, _ in ctx if pin(text) != want] == ["after é", "before é", "between の"]
    assert [n for n, text, want, _ in ctx if ascii_only(text) != want] == ["after é and a dash, 40 with the dash"]


# Item 3, the shape gaps (F14), each measured before it went in (SCRUB2-report.md): `passphrase` as a credential name;
# `pwd` and `credentials` assigned a value that is not a path; a Cookie header; an Authorization credential after a
# known scheme; a private-key block with malformed header lines (it needs its END line).
def _named_shapes():
    """(text, its scrub output, the fakes of which no piece may survive), fakes built here."""
    v = ["7" + token_hex(10)[1:] for _ in range(20)]
    b64 = base64.b64encode(token_bytes(96)).decode()

    def pem(head, tail):
        return "%s\n%s\n%s" % (head, b64, tail)
    return (
        ("passphrase=%s" % v[0], "passphrase=" + R, [v[0]]),
        ('"passphrase": "%s"' % v[1], '"passphrase": "%s"' % R, [v[1]]),
        ("SSH_PASSPHRASE: %s" % v[2], "SSH_PASSPHRASE: " + R, [v[2]]),
        ("db_pwd=%s" % v[3], "db_pwd=" + R, [v[3]]),
        ("Server=db;Uid=sa;Pwd=%s;" % v[4], "Server=db;Uid=sa;Pwd=%s;" % R, [v[4]]),
        ('"pwd": "%s"' % v[5], '"pwd": "%s"' % R, [v[5]]),
        ("credentials=%s" % v[6], "credentials=" + R, [v[6]]),
        ('{"credentials": "%s"}' % v[7], '{"credentials": "%s"}' % R, [v[7]]),
        ("AWS_CREDENTIALS = %s" % v[8], "AWS_CREDENTIALS = " + R, [v[8]]),
        ("Cookie: session=%s; theme=dark" % v[9], "Cookie: " + R, [v[9]]),
        ("curl -H 'Cookie: a=1; sid=%s' https://zq.example" % v[10], "curl -H 'Cookie: %s' https://zq.example" % R, [v[10]]),
        ("Set-Cookie: sid=%s; Path=/; HttpOnly" % v[11], "Set-Cookie: " + R, [v[11]]),
        ('"Cookie": "session=%s"' % v[12], '"Cookie": "%s"' % R, [v[12]]),
        ("Authorization: Token %s" % v[13], "Authorization: Token " + R, [v[13]]),
        ("authorization: bearer %s" % v[14], "authorization: bearer " + R, [v[14]]),
        ("Authorization: Basic %s+/%s==" % (v[15][:9], v[15][9:]), "Authorization: Basic " + R, [v[15][:9], v[15][9:]]),
        ('"Authorization": "Token %s"' % v[16], '"Authorization": "Token %s"' % R, [v[16]]),
        ("curl -H \"authorization: ApiKey %s\" https://zq.example" % v[17],
         "curl -H \"authorization: ApiKey %s\" https://zq.example" % R, [v[17]]),
        (pem("----BEGIN RSA PRIVATE KEY----", "----END RSA PRIVATE KEY----"), "<private-key-redacted>", [b64]),
        (pem("---- BEGIN OPENSSH PRIVATE KEY ----", "---- END OPENSSH PRIVATE KEY ----"), "<private-key-redacted>", [b64]),
        (pem("---BEGIN EC PRIVATE KEY---", "-----END EC PRIVATE KEY-----"), "<private-key-redacted>", [b64]),
    )


# Ordinary text the item-3 shapes must leave as it is: what the wider forms took on this session's transcripts (a path
# after PWD, a Python annotation after `credentials:`, prose after this repo's `AUTHORIZATION:` headings), a header with no
# credential, a malformed key header with no END line (prose about it), a rule of dashes, and CJK prose.
ORDINARY2 = ("PWD=/home/user/agent-factory", "OLDPWD=/tmp/zq-work", "pwd: ~/work/zq", "PWD=$HOME/zq", 'cd "$(pwd)"',
             "pwd=./relative/zq/path", "oldpwd = os.getcwd()", "credentials: LoginRequest",
             "async def login(credentials: HTTPBasicCredentials):", "GOOGLE_APPLICATION_CREDENTIALS=/srv/zq/key.json",
             "credentials = ~/creds.json", "AUTHORIZATION: a read-only harvester over the owner's own commit",
             "Authorization: this is defensive work on the owner's own system", "Authorization: Basic auth",
             "the Cookie: header carries the session", "Cookie: a=1", "Set-Cookie: theme=dark", "cookies: many of them",
             "the passphrase is set", "passphrase: short",
             "a line of prose: ----BEGIN RSA PRIVATE KEY---- starts the block", "-" * 42, "これはtestです")


def test_the_shape_gaps_are_scrubbed():
    missed = [(i, fn.__name__) for i, (text, scrubbed, fakes) in enumerate(_named_shapes())
              for fn in (SCRUB, getattr(MOD, "scrub_payload")) if fn(text) != scrubbed or not all(_no_piece(f, fn(text)) for f in fakes)]
    assert missed == []                                                  # (the shape's index, the scrubber), no value


def test_the_shape_gaps_leave_ordinary_text():
    assert [t for t in ORDINARY2 if SCRUB(t) != t] == []
    assert [t for t in ORDINARY2 if getattr(MOD, "scrub_payload")(t) != t] == []


def test_a_value_stops_before_a_passphrase_name():
    # `passphrase` is an in-run head too (AF-AP-157's class): the value before it stops, and the name stays a name
    v1, v2 = "QZJ8" + token_hex(4), "X4Z9" + token_hex(6)
    assert SCRUB("password=%spassphrase=%s" % (v1, v2)) == "password=%spassphrase=%s" % (R, R)


def test_scrub2_shapes_never_reach_the_digest(tmp_path):
    # the outward path: every key in every SCRUB2 context, the opaque runs and the item-3 shapes, one turn each, through
    # main() in process with fixture sources; the ordinary texts reach the digest whole
    rows = [(ctx.replace("{k}", key), key) for keys in _fake_keys().values() for key in keys for _, ctx in SCRUB2_CONTEXTS]
    rows += [(text, fake) for _, text, _, fake in _opaque_contexts() if fake]
    rows += [(text, fake) for text, _, fakes in _named_shapes() for fake in fakes]
    texts = [t for t, _ in rows] + list(ORDINARY2)
    jsonl = tmp_path / "scrub2.jsonl"
    jsonl.write_text("".join(_entry("user", t, "2026-09-26T00:%02d:%02d.000Z" % divmod(i, 60)) + "\n"
                             for i, t in enumerate(texts)))
    r = _run(jsonl, tmp_path / "out")
    assert r.returncode == 0, r.stderr
    blob = (tmp_path / "out" / "chat-2026-09-26.md").read_text()
    assert [f[:4] for _, f in rows if not _no_piece(f, blob)] == []
    assert [t for t in ORDINARY2 if "\n%s\n" % t not in blob] == []


def _session_export():
    spec = importlib.util.spec_from_file_location("session_export_scrub2", ROOT / "scripts" / "session_export.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_scrub2_shapes_never_reach_the_session_export(tmp_path):
    # VERIFY-SCRUB1 F3 through session_export's real convert(): a tool input is written as canonical JSON, so a key at a
    # line start sits after `\n`, one after a tab after `\t`, one after a control character after `\u001b`; the item-3
    # shapes as JSON members; a 48-character run glued to `é`
    fakes, inputs = [], []
    for keys in _fake_keys().values():
        for key in keys:
            fakes.append(key)
            inputs += [{"command": "first line\n%s rest" % key}, {"command": "a\tb\t%s" % key}, {"command": "\x1b%s" % key}]
    v = ["7" + token_hex(10)[1:] for _ in range(6)]
    t = token_hex(24)
    fakes += v + [t]
    inputs += [{"headers": {"Cookie": "session=%s" % v[0], "Authorization": "Token %s" % v[1]}},
               {"pwd": v[2], "credentials": v[3], "passphrase": v[4]}, {"command": "psql 'Pwd=%s;'" % v[5]},
               {"command": "café%s" % t}]
    lines = []
    for n, inp in enumerate(inputs, 1):
        lines.append(json.dumps({
            "parentUuid": None, "isSidechain": False, "userType": "external", "cwd": str(tmp_path),
            "sessionId": "0f0f0f0f-fake-4a4a-8b8b-00000000cafe", "version": "2.1.0", "gitBranch": "fake",
            "type": "assistant", "uuid": "u-%05d" % n, "timestamp": "2026-09-26T00:%02d:%02d.000Z" % divmod(n, 60),
            "requestId": "req_fake%05d" % n,
            "message": {"model": "claude-fake", "id": "msg_fake%05d" % n, "type": "message", "role": "assistant",
                        "content": [{"type": "tool_use", "id": "toolu_%05d" % n, "name": "Bash", "input": inp,
                                     "caller": {"type": "direct"}}],
                        "stop_reason": "tool_use", "usage": {"input_tokens": 1, "output_tokens": 1}}},
            separators=(",", ":")))
    path = tmp_path / "scrub2.jsonl"
    path.write_text("\n".join(lines) + "\n")
    events = []
    _session_export().convert(str(path), src="zq/scrub2.jsonl", key=token_bytes(32), sink=events.append)
    calls = [e for e in events if e.get("kind") == "tool_call"]
    assert len(calls) == len(inputs), [e.get("kind") for e in events][:8]
    blob = json.dumps(events, ensure_ascii=False)
    assert [f[:4] for f in fakes if not _no_piece(f, blob)] == []
