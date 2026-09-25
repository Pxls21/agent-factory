"""scripts/known_values_check.py: counts real secret values in files, prints names and counts only.

Every secret here is FAKE and assembled at run time from a hash (no source line holds one), so this file and the
transcript that wrote it carry no whole value for a later export's check to trip on (AF-AP-213).
"""
import hashlib
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "known_values_check.py"


def fake(tag, n=40):
    h = hashlib.sha512(("known-values fake " + tag).encode()).hexdigest()
    alphabet = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(alphabet[int(h[i:i + 2], 16) % len(alphabet)] for i in range(0, 2 * (n - 1), 2)) + "9"


def run(args, env=None):
    import os
    e = dict(os.environ)
    e.update(env or {})
    p = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=e, timeout=60)
    return p.returncode, p.stdout + p.stderr


def windows(v, w=8):
    return {v[i:i + w] for i in range(len(v) - w + 1)}


def setup(tmp_path, body):
    token, host = fake("tok"), "calm-otter-%s.example.net" % fake("host", 10).lower()
    env = tmp_path / "bridge.env"
    env.write_text("PC_BRIDGE_URL=https://%s/run\nPC_BRIDGE_TOKEN=%s\nPORT=80\n" % (host, token))
    target = tmp_path / "export"
    target.mkdir()
    (target / "a.jsonl").write_text(body(token, host))
    return env, target, token, host


def test_a_clean_target_passes(tmp_path):
    env, target, token, _ = setup(tmp_path, lambda t, h: '{"text": "nothing secret here"}\n')
    rc, out = run(["--env-file", str(env), str(target)])
    assert rc == 0 and "NO HIT" in out
    assert "bridge.env:PC_BRIDGE_TOKEN value whole=0 windows=0/%d" % (len(token) - 7) in out
    assert "PORT" not in out   # a value under 8 characters is not a secret


def test_the_whole_value_is_counted(tmp_path):
    env, target, _, _ = setup(tmp_path, lambda t, h: "a %s b %s\n" % (t, t))
    rc, out = run(["--env-file", str(env), str(target)])
    assert rc == 3 and "bridge.env:PC_BRIDGE_TOKEN value whole=2" in out


def test_a_cut_copy_is_caught_by_its_windows(tmp_path):
    env, target, _, _ = setup(tmp_path, lambda t, h: "xxd column: %s\n" % t[5:17])
    rc, out = run(["--env-file", str(env), str(target)])
    assert rc == 3 and "PC_BRIDGE_TOKEN value whole=0 windows=5/" in out


def test_a_url_is_checked_whole_and_by_its_host(tmp_path):
    env, target, _, host = setup(tmp_path, lambda t, h: "curl %s/health\n" % h)
    rc, out = run(["--env-file", str(env), str(target)])
    assert rc == 3 and "PC_BRIDGE_URL value whole=0" in out and "PC_BRIDGE_URL host whole=1" in out
    assert "PC_BRIDGE_URL value whole=0 windows=0/0" in out   # a URL is not windowed (its words would match prose)


def test_a_raw_key_is_checked_in_its_printed_forms(tmp_path):
    key = tmp_path / "pseudonym.key"
    key.write_bytes(hashlib.sha256(b"known-values fake raw key").digest())
    target = tmp_path / "t.txt"
    target.write_text("key hex %s\n" % key.read_bytes().hex())
    rc, out = run(["--raw-file", str(key), str(target)])
    assert rc == 3 and "pseudonym.key:raw hex whole=1" in out and "pseudonym.key:raw base64 whole=0" in out


def test_an_env_variable_is_read_by_name(tmp_path):
    token = fake("env")
    target = tmp_path / "t.txt"
    target.write_text("token %s\n" % token)
    rc, out = run(["--env", "KV_FAKE_TOKEN", str(target)], env={"KV_FAKE_TOKEN": token})
    assert rc == 3 and "env:KV_FAKE_TOKEN value whole=1" in out


def test_no_value_or_window_is_ever_printed(tmp_path):
    env, target, token, host = setup(tmp_path, lambda t, h: "%s %s %s\n" % (t, h, t[3:15]))
    rc, out = run(["--env-file", str(env), str(target)])
    assert rc == 3
    assert not any(w in out for w in windows(token)) and host not in out


def test_usage_and_unreadable_sources(tmp_path):
    empty = tmp_path / "empty.env"
    empty.write_text("# nothing\nA=1\n")
    target = tmp_path / "t.txt"
    target.write_text("x\n")
    assert run(["--env-file", str(empty), str(target)])[0] == 2
    assert run(["--env", "KV_SURELY_UNSET_VARIABLE", str(target)], env={"KV_SURELY_UNSET_VARIABLE": ""})[0] == 2
    assert run(["--env-file", str(tmp_path / "missing.env"), str(target)])[0] == 2
    assert run(["--env", "KV_FAKE_TOKEN", str(tmp_path / "no-such-target")], env={"KV_FAKE_TOKEN": fake("u")})[0] == 64
    assert run([])[0] == 64


def test_a_skipped_key_is_left_out_and_named(tmp_path):
    env, target, _, host = setup(tmp_path, lambda t, h: "public base %s\n" % h)
    rc, out = run(["--env-file", str(env), "--skip", "PC_BRIDGE_URL", str(target)])
    assert rc == 0 and "PC_BRIDGE_URL" not in out.replace("skipped keys PC_BRIDGE_URL", "")
    assert "known-values: skipped keys PC_BRIDGE_URL" in out
