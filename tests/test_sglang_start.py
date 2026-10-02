"""Self-test of deploy/sglang_start.py, the SGLang model server's start inside the qwen container (task #454).

A fake sglang package stands in for the server: it prints its resolved arguments with the key in them, as SGLang does
at startup (engine.py:1109 at 94602c9c), and records its own argv and what it printed in side files, so each test can
show the key was really emitted (the negative control) and then that it never left the start script. The real server
is checked on the PC with a fake key; nothing here starts a model."""
import json
import os
import pathlib
import signal
import stat
import subprocess
import sys
import textwrap
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
START = ROOT / "deploy" / "sglang_start.py"
FAKE_SERVER = textwrap.dedent('''
    import json, os, pathlib, signal, sys, time
    side = pathlib.Path(os.environ["FAKE_SIDE"])
    argv = sys.argv[1:]
    cfg = argv[argv.index("--config") + 1]
    text = pathlib.Path(cfg).read_text()
    mode = os.environ.get("FAKE_MODE", "print")
    st = os.stat(cfg)
    key = json.loads(text.split("api-key: ", 1)[1].split("\\n", 1)[0])
    ctx = int(text.split("context-length: ", 1)[1].split("\\n", 1)[0])
    printed = [f"server_args={{'api_key': '{key}', 'context_length': {ctx}, 'admin_api_key': None}}",
               f"ServerArgs(api_key={key!r}, port=8080)", "the key alone: " + key, "Prefill batch, #new-seq: 1"]
    (side / "server.json").write_text(json.dumps({
        "argv": argv, "cmdline": open("/proc/self/cmdline", "rb").read().decode(errors="replace"),
        "cfg_mode": oct(st.st_mode & 0o777), "dir_mode": oct(os.stat(os.path.dirname(cfg)).st_mode & 0o777),
        "key": key, "ctx": ctx, "printed": printed, "unbuffered": os.environ.get("PYTHONUNBUFFERED")}))
    for line in printed:
        print(line, flush=True)
    print("to stderr: " + key, file=sys.stderr, flush=True)
    if mode == "term":
        got = []
        signal.signal(signal.SIGTERM, lambda n, f: got.append(n))
        (side / "ready").write_text("1")
        deadline = time.monotonic() + 20
        while not got and time.monotonic() < deadline:
            time.sleep(0.05)
        print("got TERM" if got else "no TERM", flush=True)
        sys.exit(0 if got else 9)
    if mode == "otherkey":
        q = chr(34)
        print("server_args={'api_key': 'v" + "z" * 15 + "', 'admin-api-key': " + q + "w" + "y" * 15 + q + "}", flush=True)
    if mode == "selfkill":
        os.kill(os.getpid(), signal.SIGKILL)
    sys.exit(int(os.environ.get("FAKE_RC", "0")))
''')


@pytest.fixture
def env(tmp_path):
    pkg = tmp_path / "fake" / "sglang"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    (pkg / "launch_server.py").write_text(FAKE_SERVER)
    side = tmp_path / "side"
    side.mkdir()
    key = "k" + os.urandom(12).hex()  # a fake key, built at run time
    kf = tmp_path / "api_key.txt"
    kf.write_text(key + "\n")
    # only the script may set PYTHONUNBUFFERED: an inherited one would hide its absence
    e = {k: v for k, v in os.environ.items()
         if k not in ("MAX_LEN", "SGL_KEY_FILE", "FAKE_MODE", "FAKE_RC", "PYTHONUNBUFFERED")}
    e.update(PYTHONPATH=str(tmp_path / "fake"), FAKE_SIDE=str(side), SGL_KEY_FILE=str(kf), MAX_LEN="131072",
             PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(tmp_path))
    return {"env": e, "key": key, "side": side, "kf": kf, "tmp": tmp_path}


def run(env, *args, **extra):
    e = dict(env["env"], **extra)
    return subprocess.run([sys.executable, str(START), *args], env=e, capture_output=True, timeout=60)


def server(env):
    return json.loads((env["side"] / "server.json").read_text())


def test_the_key_reaches_the_server_by_config_and_never_leaves_in_its_output(env):
    r = run(env, "--model-path", "/m", "--port", "8080")
    assert r.returncode == 0, r.stderr
    s = server(env)
    # the negative control: the fake server really printed the key, in three forms and on stderr
    assert s["key"] == env["key"] and sum(env["key"] in p for p in s["printed"]) == 3
    out = r.stdout + r.stderr
    assert env["key"].encode() not in out
    assert out.count(b"<redacted>") == 4
    assert b"Prefill batch, #new-seq: 1" in r.stdout  # other lines pass unchanged


def test_a_key_shaped_value_that_differs_from_the_file_is_masked_too(env):
    # the second guard: a printed key form whose value is not the file's (a cut or re-encoded key) is masked as well
    r = run(env, FAKE_MODE="otherkey")
    assert r.returncode == 0
    assert b"v" + b"z" * 15 not in r.stdout and b"w" + b"y" * 15 not in r.stdout
    assert b"'api_key': '<redacted>'" in r.stdout and b"'admin-api-key': \"<redacted>\"" in r.stdout


def test_the_key_is_on_no_command_line_and_the_config_is_private(env):
    run(env, "--model-path", "/m")
    s = server(env)
    assert env["key"] not in s["cmdline"] and env["key"] not in " ".join(s["argv"])
    assert s["argv"][:1] == ["--config"] and s["argv"][2:] == ["--model-path", "/m"]
    assert s["cfg_mode"] == "0o600" and s["dir_mode"] == "0o700"
    assert s["ctx"] == 131072 and s["unbuffered"] == "1"


def test_max_len_is_the_context_length(env):
    run(env, MAX_LEN="65536")
    assert server(env)["ctx"] == 65536


@pytest.mark.parametrize("value", ["", "0", "-5", "12k", " 131072", "1e5"])
def test_a_bad_max_len_refuses_and_starts_nothing(env, value):
    r = run(env, MAX_LEN=value)
    assert r.returncode == 64 and b"sglang_start: MAX_LEN must be a positive integer" in r.stderr
    assert not (env["side"] / "server.json").exists()


@pytest.mark.parametrize("content,why", [(None, "unreadable"), ("", "empty"), ("\n  \n", "empty"),
                                         ("a b", "more than one printable word"),
                                         ("line1\nline2", "more than one printable word")])
def test_a_bad_key_file_refuses_and_starts_nothing(env, content, why):
    if content is None:
        env["kf"].unlink()
    else:
        env["kf"].write_text(content)
    r = run(env)
    assert r.returncode == 64 and why.encode() in r.stderr, r.stderr
    assert not (env["side"] / "server.json").exists()
    if content:
        assert b"line2" not in r.stderr and b"a b" not in r.stderr  # a refusal never echoes the file


@pytest.mark.parametrize("flag", ["--api-key", "--api-key=x", "--context-length", "--config"])
def test_a_flag_this_script_owns_refuses_on_the_command_line(env, flag):
    r = run(env, "--model-path", "/m", flag, "x")
    assert r.returncode == 64 and f"{flag.split('=')[0]} is set by this script".encode() in r.stderr
    assert not (env["side"] / "server.json").exists()


def test_the_server_exit_code_is_the_scripts(env):
    assert run(env, FAKE_RC="3").returncode == 3


def test_a_server_ended_by_a_signal_exits_128_plus_its_number(env):
    assert run(env, FAKE_MODE="selfkill").returncode == 128 + signal.SIGKILL


def test_term_goes_to_the_server_which_ends_cleanly(env):
    e = dict(env["env"], FAKE_MODE="term")
    p = subprocess.Popen([sys.executable, str(START)], env=e, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    deadline = time.monotonic() + 30
    while not (env["side"] / "ready").exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    assert (env["side"] / "ready").exists()
    p.send_signal(signal.SIGTERM)
    out, err = p.communicate(timeout=30)
    assert p.returncode == 0 and b"got TERM" in out
    assert env["key"].encode() not in out + err


def test_the_module_is_stdlib_only_and_mode_0644():
    assert oct(START.stat().st_mode & 0o777) == "0o644"
    src = START.read_text()
    imports = {ln.split()[1].split(".")[0] for ln in src.splitlines() if ln.startswith(("import ", "from "))}
    assert imports <= {"json", "os", "re", "signal", "subprocess", "sys", "tempfile"}, imports
    assert not stat.S_ISLNK(START.lstat().st_mode)
