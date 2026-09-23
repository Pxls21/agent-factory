"""transcript_export: every planted secret class is scrubbed before it reaches disk (negative
control per class), user/assistant text survives (positive control), noise turns are dropped,
output is deterministic and idempotent. Synthetic JSONL only — never the live transcript."""
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


def test_missing_transcript_exits_3(tmp_path):
    r = subprocess.run([sys.executable, str(TOOL), "--transcript", str(tmp_path / "nope.jsonl"), "--out", str(tmp_path / "o")],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 3 and "no transcript" in r.stderr
