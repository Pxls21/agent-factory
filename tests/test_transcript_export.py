"""transcript_export: every planted secret class is scrubbed before it reaches disk (negative
control per class), user/assistant text survives (positive control), noise turns are dropped,
output is deterministic and idempotent. Synthetic JSONL only — never the live transcript."""
import importlib.util
import json
import pathlib
import subprocess
import sys

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


def _run(jsonl, out):
    return subprocess.run([sys.executable, str(TOOL), "--transcript", str(jsonl), "--out", str(out)],
                          capture_output=True, text=True, timeout=60)


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
    r = subprocess.run([sys.executable, str(TOOL), "--transcript", str(jsonl), "--out", str(out), "--cap", str(cap)],
                       capture_output=True, text=True, timeout=60)
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
