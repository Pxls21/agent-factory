"""scripts/known_values_check.py: counts real secret values in files, prints names and counts only.

Every secret here is FAKE and assembled at run time from a hash (no source line holds one), so this file and the
transcript that wrote it carry no whole value for a later export's check to trip on (AF-AP-213).
"""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "known_values_check.py"


def fake(tag, n=40):
    h = hashlib.sha512(("known-values fake " + tag).encode()).hexdigest()
    alphabet = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(alphabet[int(h[i:i + 2], 16) % len(alphabet)] for i in range(0, 2 * (n - 1), 2)) + "9"


def run(args, env=None, timeout=60):
    # the child's environment is this one without the two token variables, which this file never reads (SCRUB2)
    e = {k: os.environ[k] for k in os.environ if k not in ("GH_TOKEN", "GITHUB_TOKEN")}
    e.update(env or {})
    p = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=e, timeout=timeout)
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


def test_a_token_file_is_one_secret(tmp_path):
    token = fake("keyfile")
    kf = tmp_path / "api-key"
    kf.write_text(token + "\n")
    target = tmp_path / "t.txt"
    target.write_text("Authorization: Bearer %s\n" % token[:20])
    rc, out = run(["--token-file", str(kf), str(target)])
    assert rc == 3 and "api-key:token value whole=0 windows=13/" in out
    short = tmp_path / "short"
    short.write_text("abc\n")
    assert run(["--token-file", str(short), str(target)])[0] == 2


def test_a_source_that_is_not_a_regular_file_is_refused_at_once(tmp_path):
    # VERIFY-SCRUB1 F10: a FIFO source hung the check at open() (it waits for a writer), and a device was read as empty.
    # Each is refused now (exit 2), whatever flag names it; a directory was refused before and still is.
    target = tmp_path / "t.txt"
    target.write_text("x\n")
    fifo = tmp_path / "zq-fifo"
    os.mkfifo(fifo)
    for flag in ("--env-file", "--raw-file", "--token-file"):
        assert run([flag, str(fifo), str(target)], timeout=20) == (2, "known-values: cannot read a source (NotRegularFile)\n"), flag
    assert run(["--raw-file", os.devnull, str(target)], timeout=20) == (2, "known-values: cannot read a source (NotRegularFile)\n")
    assert run(["--env-file", str(tmp_path), str(target)], timeout=20) == (
        2, "known-values: cannot read a source (IsADirectoryError)\n")


def test_a_malformed_env_line_is_printed_as_its_line_number(tmp_path):
    # VERIFY-SCRUB1 F13: the part of a line before `=` was printed verbatim, and on a malformed line it can hold anything
    # (here a piece of the value). Its line number is printed instead, counted on "\n" as grep counts (a lone "\r" still
    # ends an entry, as it did, without moving the count: AF-AP-132).
    token = fake("malformed")
    env = tmp_path / "bad.env"
    env.write_text("# comment\n\nzq %s=%s\nGOOD_NAME=%s\nX=1\rzq b=%s\n" % (token[:20], token, token, token))
    target = tmp_path / "t.txt"
    target.write_text("the value %s\n" % token)
    rc, out = run(["--env-file", str(env), str(target)])
    assert rc == 3 and [ln.split(" whole=")[0] for ln in out.splitlines() if " whole=" in ln] == [
        "bad.env:<malformed line 3> value", "bad.env:GOOD_NAME value", "bad.env:<malformed line 5> value"]
    assert not any(w in out for w in windows(token))
