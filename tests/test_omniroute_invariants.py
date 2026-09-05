"""Deterministic tests for scripts/omniroute_invariants.sh (LLM-free, network-free).

The script is exercised end to end with PATH shims for `ss`, `systemctl` and `curl` and a fixture
/proc tree (PROC_ROOT). Every negative control asserts the EXACT failing check name and reason
prefix, and the positive control asserts exit 0 with no FAIL line. The fake curl records its argv so
the test can prove the API key never travels in argv (it must arrive via a header FILE).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "omniroute_invariants.sh"
BASH = shutil.which("bash")  # resolved BEFORE any test empties PATH
SERVICE = "omniroute-migrated.service"
DATA_DIR = "/home/rocco/.omniroute-migrated"
GOOD_CGROUP = f"0::/user.slice/user-1000.slice/user@1000.service/app.slice/{SERVICE}"
REQUIRED = ["agentfactory-build", "agentfactory-verify", "agentfactory-research",
            "agentfactory-sweep", "ollama-cloud/kimi-k3"]
KEY = "sk-test-0123456789abcdefghijklmnopqrstuvwxyz"


def _write_exec(path: Path, body: str) -> None:
    path.write_text(body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _catalog(ids):
    return json.dumps({"object": "list", "data": [{"id": i, "object": "model"} for i in ids]})


def make_world(tmp: Path, *, listeners=(4242,), cgroup=GOOD_CGROUP, environ=None,
               unit_env=f"Environment=HOME=/x DATA_DIR={DATA_DIR}", health="200",
               models_code="200", catalog_ids=None, key_file=True):
    """Build shims + fixture proc; return (env, curl_log_path)."""
    shim = tmp / "shim"; shim.mkdir()
    proc = tmp / "proc"; proc.mkdir()
    if environ is None:
        environ = {"HOME": "/home/rocco/omniroute-migration-20260829/candidate-home",
                   "DATA_DIR": DATA_DIR, "REQUIRE_API_KEY": "true", "OMNIROUTE_SERVER_HOST": "0.0.0.0"}
    for pid in listeners:
        d = proc / str(pid); d.mkdir()
        (d / "cgroup").write_text(cgroup + "\n")
        (d / "environ").write_bytes(b"".join(f"{k}={v}".encode() + b"\0" for k, v in environ.items()))
    ss_lines = "".join(
        f'LISTEN 0 511 0.0.0.0:20128 0.0.0.0:* users:(("omniroute",pid={pid},fd=21))\n' for pid in listeners)
    _write_exec(shim / "ss", "#!/usr/bin/env bash\nprintf '%s' \"$SS_OUT\"\n")
    _write_exec(shim / "systemctl", "#!/usr/bin/env bash\nprintf '%s\\n' \"$UNIT_ENV\"\n")
    catalog_file = tmp / "catalog.json"
    catalog_file.write_text(_catalog(REQUIRED if catalog_ids is None else catalog_ids))
    curl_log = tmp / "curl.log"
    # Fake curl: honours -o <file> and -w '%{http_code}'; answers by URL suffix; logs argv as JSON.
    _write_exec(shim / "curl", """#!/usr/bin/env bash
python3 - "$@" <<'PY'
import json, os, sys
args = sys.argv[1:]
with open(os.environ["CURL_LOG"], "a") as fh: fh.write(json.dumps(args) + "\\n")
out = None; url = None
i = 0
while i < len(args):
    a = args[i]
    if a == "-o": out = args[i+1]; i += 2; continue
    if a in ("-w", "-m", "-H"): i += 2; continue
    if a.startswith("http"): url = a
    i += 1
if url.endswith("/api/health"):
    code = os.environ["FAKE_HEALTH"]; body = "{}"
elif url.endswith("/v1/models"):
    code = os.environ["FAKE_MODELS_CODE"]; body = open(os.environ["FAKE_CATALOG"]).read()
else:
    code = "404"; body = ""
if out and out != "/dev/null":
    open(out, "w").write(body)
sys.stdout.write(code)
PY
""")
    kf = tmp / "omniroute.env"
    if key_file:
        kf.write_text(f"OMNIROUTE_API_KEY={KEY}\n"); kf.chmod(0o600)
    env = dict(os.environ)
    env.update({
        "PATH": f"{shim}:{env['PATH']}",
        "PROC_ROOT": str(proc),
        "SS_OUT": ss_lines,
        "UNIT_ENV": unit_env,
        "FAKE_HEALTH": health,
        "FAKE_MODELS_CODE": models_code,
        "FAKE_CATALOG": str(catalog_file),
        "CURL_LOG": str(curl_log),
        "OMNIROUTE_API_KEY_FILE": str(kf) if key_file else "",
    })
    if not key_file:
        env.pop("OMNIROUTE_API_KEY_FILE", None)
    return env, curl_log


def run(env):
    return subprocess.run([BASH, str(SCRIPT)], env=env, capture_output=True, text=True, timeout=60)


def _fails(out: str):
    return [ln for ln in out.splitlines() if ln.startswith("FAIL ")]


def test_all_invariants_hold(tmp_path):
    env, log = make_world(tmp_path)
    r = run(env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert _fails(r.stdout) == []
    for check in ("listener", "cgroup", "data_dir_environ", "data_dir_unit", "require_api_key", "health", "catalog"):
        assert re.search(rf"^OK   {check}:", r.stdout, re.M), r.stdout
    assert "5 ids; every required id present" in r.stdout


def test_key_never_in_argv_and_travels_by_header_file(tmp_path):
    env, log = make_world(tmp_path)
    assert run(env).returncode == 0
    calls = [json.loads(l) for l in log.read_text().splitlines()]
    models_calls = [c for c in calls if any(a.endswith("/v1/models") for a in c)]
    assert len(models_calls) == 1
    argv = models_calls[0]
    assert all(KEY not in a for a in argv), argv
    hdr = [argv[i + 1] for i, a in enumerate(argv) if a == "-H"]
    assert hdr and hdr[0].startswith("@/dev/fd/"), argv


def test_second_listener_fails_exactly(tmp_path):
    env, _ = make_world(tmp_path, listeners=(4242, 5151))
    r = run(env)
    assert r.returncode == 1
    assert any(f.startswith("FAIL listener: expected exactly 1 listener pid on :20128, found 2") for f in _fails(r.stdout)), r.stdout


def test_unmanaged_session_scope_fails_cgroup(tmp_path):
    env, _ = make_world(tmp_path, cgroup="0::/user.slice/user-1000.slice/user@1000.service/session.slice/session-7.scope")
    r = run(env)
    assert r.returncode == 1
    fails = _fails(r.stdout)
    assert any(f.startswith("FAIL cgroup: listener pid 4242 is in") and "not omniroute-migrated.service" in f for f in fails), r.stdout
    assert not any(f.startswith("FAIL listener") for f in fails)


def test_missing_data_dir_in_environ_and_unit(tmp_path):
    env, _ = make_world(tmp_path, environ={"HOME": "/home/rocco", "REQUIRE_API_KEY": "true"},
                        unit_env="Environment=HOME=/home/rocco")
    r = run(env)
    assert r.returncode == 1
    fails = _fails(r.stdout)
    assert any(f == f"FAIL data_dir_environ: listener environ lacks DATA_DIR={DATA_DIR}" for f in fails), r.stdout
    assert any(f.startswith(f"FAIL data_dir_unit: {SERVICE} does not declare DATA_DIR={DATA_DIR}") for f in fails), r.stdout


def test_require_api_key_false_fails(tmp_path):
    env, _ = make_world(tmp_path, environ={"DATA_DIR": DATA_DIR, "REQUIRE_API_KEY": "false"})
    r = run(env)
    assert r.returncode == 1
    assert any(f.startswith("FAIL require_api_key: listener environ lacks REQUIRE_API_KEY=true") for f in _fails(r.stdout)), r.stdout


def test_health_500_fails(tmp_path):
    env, _ = make_world(tmp_path, health="500")
    r = run(env)
    assert r.returncode == 1
    assert "FAIL health: GET /api/health -> 500" in r.stdout


def test_catalog_missing_combo_fails_naming_it(tmp_path):
    env, _ = make_world(tmp_path, catalog_ids=[i for i in REQUIRED if i != "agentfactory-sweep"])
    r = run(env)
    assert r.returncode == 1
    assert "FAIL catalog: catalog (4 ids) lacks: agentfactory-sweep" in r.stdout


def test_catalog_401_fails(tmp_path):
    env, _ = make_world(tmp_path, models_code="401")
    r = run(env)
    assert r.returncode == 1
    assert "FAIL catalog: GET /v1/models -> 401" in r.stdout


def test_no_key_file_fails_closed(tmp_path):
    env, _ = make_world(tmp_path, key_file=False)
    r = run(env)
    assert r.returncode == 1
    assert "FAIL catalog: OMNIROUTE_API_KEY_FILE not set" in r.stdout


def test_missing_tool_is_usage_error(tmp_path):
    env, _ = make_world(tmp_path)
    empty = tmp_path / "empty"; empty.mkdir()
    env["PATH"] = str(empty)  # no ss/systemctl/curl at all
    r = run(env)
    assert r.returncode == 2
    assert "tool missing: ss" in r.stderr
