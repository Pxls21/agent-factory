"""scripts/gpu_side_by_side.sh and its reader probe, the side-by-side GPU window job (task #262; D-087, D-088).

The job runs on the PC inside a GPU window and drives podman, nvidia-smi, the temporary server's /v1/models and the
reader probe. Here those are replaced at the system boundary only, as tests/test_gpu_window.py does it: PATH shims for
`podman` (a state file stands in for the container; every argv is logged as JSON) and `nvidia-smi` (a number); the REAL
curl behind a shim that logs its argv; a loopback HTTP server that answers /v1/models 200 only while the fake container
is "up" AND the request carries the right bearer key; and a fake reader probe on the SBS_PROBE seam. The unit is the
repo's own deploy/qwen.container with only the key path moved into the test's tree, so a key the job does not copy
turns these tests red. The key is a FAKE string.

The probe (docs/research/findings/jev-pipes/rwkv_sbs_probe.py) is driven in process with a fake engine (no torch, no
GPU) and a loopback fake chat server. Nothing here is a measurement: the GPU phases run only on the PC, in a window.
The brief's numbers are written out again (BRIEF_*) so the job is checked against the brief, not against itself.
"""
import ast
import copy
import hashlib
import http.server
import importlib.util
import json
import math
import os
import pathlib
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "gpu_side_by_side.sh"
RUNNER = ROOT / "scripts" / "gpu_window.sh"
PROBE = ROOT / "docs" / "research" / "findings" / "jev-pipes" / "rwkv_sbs_probe.py"
JOBS = ROOT / "docs" / "research" / "findings" / "jev-pipes" / "sbs-window.jobs"
G0 = ROOT / "docs" / "research" / "findings" / "j2b-variants" / "rwkv7_g0.py"
REAL_UNIT = (ROOT / "deploy" / "qwen.container").read_text()
REAL_KEY_PATH = "/home/rocco/.config/qwen-builder/api-key"
KEY = "SBS7-fake-side-by-side-key-41d9"
REAL_CURL = shutil.which("curl")

BRIEF_IMAGE = "ghcr.io/syv-ai/qwen38-27b-rtx3090@sha256:c52d9033527df5249d2f7306b35173a47f4f87d45bb60927fbe93fdb4986aacb"
BRIEF_MODEL = "qwen3.8-27b-local"
BRIEF_MAX_TOKENS = 512
BRIEF_PAYLOAD_KEYS = {"model", "messages", "max_tokens", "temperature"}
# the window's configurations: the brief's pair moved to keep ~500 MiB spare (SBS1-report section 7; the coordinator)
BRIEF_CONFIGS = [("0.90", "1024"), ("0.88", "4096")]
BRIEF_TOKENS, BRIEF_LOAD = "16384", "4"
# the running server's lines as the brief's premise printed them (the 2026-09-24 boot, util 0.972)
PREMISE_LOG = (
    "Model loading took 14.26 GiB memory and 17.888750 seconds\n"
    "Available KV cache memory: 7.08 GiB\n"
    "GPU KV cache size: 222,822 tokens, Maximum concurrency for 131,072 tokens per request: 1.70x\n"
    "Free memory on device (23.05/23.56 GiB) on startup. Desired GPU memory utilization is (0.972, 22.9 GiB). Actual "
    "usage is 14.73 GiB for consumed memory (weights + non-torch), 1.09 GiB for peak activation, and 0.71 GiB for "
    "CUDAGraph memory.\n")
ARGS = ("--util", "0.90", "--chunk", "4096", "--tokens", "16384", "--load", "4")


def server_log(util="0.9"):
    """The premise's lines as a server started with GPU_UTIL=util would print its desired share."""
    return PREMISE_LOG.replace("(0.972, 22.9 GiB)", "(%s, 21.2 GiB)" % util)


PODMAN = r'''#!/usr/bin/env python3
import json, os, signal, sys, time
shim = os.environ["SHIM_DIR"]
args = sys.argv[1:]
with open(os.path.join(shim, "podman-argv.log"), "a") as fh:
    fh.write(json.dumps(args) + "\n")
flag = lambda name: os.path.exists(os.path.join(shim, name))
container = os.path.join(shim, "container")


def note(line):
    with open(os.path.join(shim, "calls.log"), "a") as fh:
        fh.write(line + "\n")


if args[:2] == ["container", "exists"]:
    if flag("exists-error"):
        sys.exit(125)
    sys.exit(0 if args[2:] == ["qwen"] and os.path.exists(container) else 1)
if args[:1] == ["run"]:
    if flag("run-fails"):
        print("Error: fake run failure", file=sys.stderr)
        sys.exit(125)
    if not flag("exits-at-boot"):
        open(container, "w").write("qwen\n")
        if not flag("never-up"):
            open(os.path.join(shim, "up"), "w").write("1\n")
    print("0123456789abcdef")
    sys.exit(0)
if args[:1] == ["logs"]:
    if not os.path.exists(container):
        print('Error: no container with name or ID "qwen" found', file=sys.stderr)
        sys.exit(125)
    sys.stdout.write(open(os.path.join(shim, "server.log")).read())
    sys.stdout.flush()
    if "-f" in args:
        open(os.path.join(shim, "follower.pid"), "w").write(str(os.getpid()))
        while os.path.exists(container):
            time.sleep(0.1)
    sys.exit(0)
if args[:1] == ["rm"]:
    note("rm-start")
    if flag("rm-hang"):
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        time.sleep(60)
    if flag("rm-slow"):
        time.sleep(2)
    for name in ("container", "up"):
        if os.path.exists(os.path.join(shim, name)):
            os.unlink(os.path.join(shim, name))
    note("rm-done")
    sys.exit(0)
sys.exit(99)
'''
NVIDIA_SMI = r"""#!/usr/bin/env bash
echo "nvidia-smi $*" >> "$SHIM_DIR/calls.log"
[ -e "$SHIM_DIR/nvsmi-broken" ] && { echo "Failed to initialize NVML: Driver/library version mismatch"; exit 18; }
cat "$SHIM_DIR/gpu_used" 2>/dev/null || echo 255
"""
CURL = r"""#!/usr/bin/env bash
printf '%s\n' "$*" >> "$SHIM_DIR/curl-argv.log"
exec REAL_CURL "$@"
"""
SYSTEMCTL = r"""#!/usr/bin/env bash
echo "systemctl $*" >> "$SHIM_DIR/calls.log"
case "$*" in
  "--user is-active --quiet qwen") [ -e "$SHIM_DIR/active" ];;
  "--user stop qwen") rm -f "$SHIM_DIR/active";;
  "--user start qwen") touch "$SHIM_DIR/active";;
  *) exit 99;;
esac
"""
FAKE_PROBE = r'''
import hashlib, json, os, sys, time
shim = os.environ["SHIM_DIR"]
argv = sys.argv[1:]
with open(os.path.join(shim, "probe-argv.log"), "a") as fh:
    fh.write(json.dumps(argv) + "\n")
with open(os.path.join(shim, "probe.pid"), "w") as fh:
    fh.write(str(os.getpid()))
args = dict(zip(argv[::2], argv[1::2]))
with open(args["--key-file"], "rb") as fh:
    served = hashlib.sha256(fh.read().strip()).hexdigest() == os.environ["SHIM_KEY_SHA256"]
mode = open(os.path.join(shim, "probe-mode")).read().strip() if os.path.exists(os.path.join(shim, "probe-mode")) else "ok"
if mode == "sleep":
    time.sleep(60)
rec = {"probe": "fake", "key_file_is_the_served_key": served}
for phase in ("alone", "qwen_idle_rwkv", "together"):
    rec[phase] = {"ok": True}
if mode == "phase-not-ok":
    rec["together"] = {"ok": False, "error": "fake"}
with open(args["--out"], "w") as fh:
    json.dump(rec, fh)
sys.exit(1 if mode == "fail" else 0)
'''


class _Models(http.server.BaseHTTPRequestHandler):
    """/v1/models: 200 only for the right bearer key while the server's flag file exists."""

    def do_GET(self):  # noqa: N802 (the stdlib's name)
        auth = self.headers.get("Authorization", "")
        self.server.seen.append((self.path, auth))
        ok_key = auth == "Bearer " + KEY
        up = (self.server.shim / self.server.flag).exists() and self.path == "/v1/models"
        self.send_response(200 if (ok_key and up) else (401 if not ok_key else 503))
        self.end_headers()
        self.wfile.write(b'{"data":[]}')

    def log_message(self, *a):
        pass


def _server(shim, flag):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Models)
    srv.seen, srv.shim, srv.flag = [], shim, flag
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


@pytest.fixture
def sbs(tmp_path):
    shim = tmp_path / "shim"
    shim.mkdir()
    for name, body in (("podman", PODMAN), ("nvidia-smi", NVIDIA_SMI), ("curl", CURL.replace("REAL_CURL", REAL_CURL)),
                       ("systemctl", SYSTEMCTL)):
        (shim / name).write_text(body)
        (shim / name).chmod(0o755)
    (shim / "fake_probe.py").write_text(FAKE_PROBE)
    (shim / "server.log").write_text(server_log())
    key = tmp_path / "secrets" / "api-key"
    key.parent.mkdir()
    key.write_text(KEY + "\n")
    key.chmod(0o600)
    home = tmp_path / "home"
    unit = home / ".config" / "containers" / "systemd" / "qwen.container"
    unit.parent.mkdir(parents=True)
    assert REAL_KEY_PATH in REAL_UNIT
    unit.write_text(REAL_UNIT.replace(REAL_KEY_PATH, str(key)))
    srv = _server(shim, "up")
    env = dict(os.environ, PATH="%s:%s" % (shim, os.environ["PATH"]), HOME=str(home), SHIM_DIR=str(shim),
               SBS_PORT=str(srv.server_address[1]), SBS_PYTHON=sys.executable, SBS_PROBE=str(shim / "fake_probe.py"),
               SHIM_KEY_SHA256=hashlib.sha256(KEY.encode()).hexdigest())
    for k in ("BOOT_SECONDS", "GPU_FREE_MIB", "SBS_RM_SECONDS", "http_proxy", "HTTP_PROXY"):
        env.pop(k, None)
    w = types.SimpleNamespace(tmp=tmp_path, shim=shim, key=key, unit=unit, srv=srv, env=env, out=tmp_path / "out",
                              port=srv.server_address[1])
    yield w
    srv.shutdown()
    srv.server_close()


def _run(w, *args, timeout=60, **extra):
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, env=dict(w.env, **extra),
                          timeout=timeout)


def _job(w, *args, **extra):
    return _run(w, *(args or ARGS), "--out", str(w.out), **extra)


# Scripts under test start with SIGINT at its default disposition: a detached launcher (`nohup ... &`, as
# scripts/lane_gate.sh advises) starts the whole run with SIGINT ignored, bash cannot trap a signal that was ignored at
# entry, and every INT test would hang to its timeout (AF-AP-210). exec keeps the pid.
INT_DEFAULT = [sys.executable, "-c",
               "import os, signal, sys; signal.signal(signal.SIGINT, signal.SIG_DFL); os.execvp(sys.argv[1], sys.argv[1:])"]


def _start(w, *args, **extra):
    return subprocess.Popen(INT_DEFAULT + ["bash", str(SCRIPT), *(args or ARGS), "--out", str(w.out)], env=dict(w.env, **extra),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)


def _podman(w):
    p = w.shim / "podman-argv.log"
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []


def _calls(w):
    p = w.shim / "calls.log"
    return p.read_text().splitlines() if p.exists() else []


def _summary(w):
    return json.loads((w.out / "summary.json").read_text())


def _nothing_started(w):
    assert [a for a in _podman(w) if a[:2] != ["container", "exists"]] == []
    assert not (w.shim / "probe-argv.log").exists() and not (w.out / "summary.json").exists()


def _removed_once(w):
    assert [a for a in _podman(w) if a[:1] == ["rm"]] == [["rm", "-f", "-i", "qwen"]]
    assert _calls(w).count("rm-done") == 1 and not (w.shim / "container").exists()


def _key_never_leaked(w):
    for log in ("podman-argv.log", "curl-argv.log", "probe-argv.log"):
        p = w.shim / log
        text = p.read_text() if p.exists() else ""
        assert KEY not in text and "VLLM_API_KEY" not in text, log
    for p in w.tmp.rglob("*"):
        if p.is_file() and p != w.key:
            assert KEY not in p.read_text(errors="replace"), p


def _wait_for(pred, seconds=15):
    deadline = time.monotonic() + seconds
    while not pred():
        assert time.monotonic() < deadline, "timed out waiting"
        time.sleep(0.05)


def _dead(pid, seconds=10):
    deadline = time.monotonic() + seconds
    while True:
        try:
            st = pathlib.Path("/proc/%d/stat" % pid).read_text().rsplit(")", 1)[1].split()[0]
        except (FileNotFoundError, ProcessLookupError):
            return True
        if st == "Z":
            return True
        if time.monotonic() > deadline:
            return False
        time.sleep(0.05)


def _pid(w, name):
    _wait_for(lambda: (w.shim / name).exists() and (w.shim / name).read_text().strip())
    return int((w.shim / name).read_text())


def expected_run(port, key, util):
    """The podman argv from the brief: the unit's lines 21-32 plus GPU_UTIL, loopback only, --rm, command batch."""
    return ["run", "-d", "--rm", "--pull=never", "--name", "qwen", "-p", "127.0.0.1:%s:8080" % port,
            "-v", "qwen-cache:/cache", "-v", "/home/rocco/qwen-serving/models:/app/models",
            "-v", "%s:/app/api_key.txt:ro" % key,
            "-e", "PORT=8080", "-e", "SPEC=mtp", "-e", "MAX_LEN=131072", "-e", "PREFIX_CACHE=1",
            "-e", "EXTRA_ARGS=--served-model-name qwen3.8-27b-local qwen3.8-27b",
            "--ipc=host", "--device", "nvidia.com/gpu=all", "-e", "GPU_UTIL=%s" % util, BRIEF_IMAGE, "batch"]


# ------------------------------------------------------------------ the job: refusals start nothing

def test_usage_errors_start_nothing(sbs):
    out = ("--out", str(sbs.out))
    cases = [((), "usage: gpu_side_by_side.sh"), (ARGS, "usage:"), (("--util",), "usage:"),
             (ARGS + out + ("--load", "4"), "usage:"), (ARGS + out + ("--bogus", "1"), "usage:"),
             (("--util", "0.49") + ARGS[2:] + out, "must be 0.50-0.97"),
             (("--util", "0.975") + ARGS[2:] + out, "must be 0.50-0.97"),
             (("--util", "1") + ARGS[2:] + out, "needs a decimal"), (("--util", ".9") + ARGS[2:] + out, "needs a decimal"),
             (("--util", "0.9x") + ARGS[2:] + out, "needs a decimal"),
             (ARGS[:2] + ("--chunk", "1023") + ARGS[4:] + out, "--chunk must be 1024-16384"),
             (ARGS[:2] + ("--chunk", "16385") + ARGS[4:] + out, "--chunk must be 1024-16384"),
             (ARGS[:2] + ("--chunk", "4k") + ARGS[4:] + out, "--chunk needs a whole number"),
             (ARGS[:4] + ("--tokens", "4095") + ARGS[6:] + out, "--tokens must be 4096-65536"),
             (ARGS[:4] + ("--tokens", "65537") + ARGS[6:] + out, "--tokens must be 4096-65536"),
             (ARGS[:6] + ("--load", "9") + out, "--load must be 0-8"),
             (ARGS[:6] + ("--load", "-1") + out, "--load needs a whole number"),
             (ARGS + ("--out", "/proc/no-such/dir"), "cannot write --out")]
    for args, msg in cases:
        r = _run(sbs, *args, timeout=15)
        assert r.returncode == 64 and msg in r.stderr, (args, r.returncode, r.stderr)
    assert _podman(sbs) == [] and not (sbs.shim / "probe-argv.log").exists()


def test_numbers_are_decimal_and_the_seams_are_checked_before_anything_starts(sbs):
    r = _run(sbs, "--util", "0.9", "--chunk", "04096", "--tokens", "016384", "--load", "08", "--out", str(sbs.out))
    assert r.returncode == 0, r.stderr                                  # a leading zero is not octal
    assert _summary(sbs)["config"] == {"util": 0.9, "chunk": 4096, "tokens": 16384, "load": 8, "port": sbs.port,
                                       "image": BRIEF_IMAGE}
    (sbs.shim / "podman-argv.log").unlink()
    for seam, value, msg in (("BOOT_SECONDS", "15m", "BOOT_SECONDS needs a whole number"),
                             ("BOOT_SECONDS", "3601", "BOOT_SECONDS must be 0-3600"),
                             ("GPU_FREE_MIB", "1.5k", "GPU_FREE_MIB needs a whole number"),
                             ("SBS_RM_SECONDS", "0", "SBS_RM_SECONDS must be 1-20"),
                             ("SBS_RM_SECONDS", "21", "SBS_RM_SECONDS must be 1-20"),
                             ("SBS_PORT", "80", "SBS_PORT must be 1024-65535"),
                             ("SBS_PORT", "9999999", "SBS_PORT is too large")):
        r = _job(sbs, **{seam: value})
        assert r.returncode == 64 and msg in r.stderr, (seam, value, r.stderr)
    assert _podman(sbs) == []


def test_a_container_named_qwen_refuses_and_is_never_removed(sbs):
    (sbs.shim / "container").write_text("the live one\n")
    r = _job(sbs)
    assert r.returncode == 3 and "a container named qwen exists: not inside a GPU window" in r.stderr, r.stderr
    _nothing_started(sbs)
    assert (sbs.shim / "container").read_text() == "the live one\n"


@pytest.mark.parametrize("state,msg", [
    ("exists-error", "podman cannot tell whether a container named qwen exists (rc 125)"),
    ("nvsmi-broken", "nvidia-smi gives no reading"),
    ("busy", "the GPU holds 1500 MiB (at or over 1500): not inside a GPU window")])
def test_outside_a_window_refuses_and_starts_nothing(sbs, state, msg):
    if state == "busy":
        (sbs.shim / "gpu_used").write_text("1500\n")
    else:
        (sbs.shim / state).touch()
    r = _job(sbs)
    assert r.returncode == 3 and msg in r.stderr, r.stderr
    _nothing_started(sbs)


def test_a_gpu_just_under_the_threshold_is_a_window(sbs):
    (sbs.shim / "gpu_used").write_text("1499\n")
    r = _job(sbs)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize("image", [
    "ghcr.io/syv-ai/qwen38-27b-rtx3090:latest", "ghcr.io/syv-ai/qwen38-27b-rtx3090",
    BRIEF_IMAGE[:-1], BRIEF_IMAGE.replace("@sha256:", "@sha512:"), BRIEF_IMAGE + ":tag", BRIEF_IMAGE.upper(),
    "@sha256:" + BRIEF_IMAGE.rsplit(":", 1)[1]])
def test_an_unpinned_image_refuses_before_anything_starts(sbs, image):
    sbs.unit.write_text(sbs.unit.read_text().replace(BRIEF_IMAGE, image))
    r = _job(sbs)
    assert r.returncode == 3 and "the unit's Image= is not digest-pinned (@sha256:)" in r.stderr, r.stderr
    _nothing_started(sbs)


@pytest.mark.parametrize("edit,msg", [
    (lambda u: u.replace("Exec=batch\n", "Exec=batch\nSecurityLabelDisable=true\n"),
     "key 'SecurityLabelDisable' is not one this job copies"),
    (lambda u: u.replace("--device nvidia.com/gpu=all", "--device nvidia.com/gpu=all --shm-size=16g"),
     "PodmanArgs token --shm-size is not a device or IPC argument"),
    (lambda u: u.replace("ContainerName=qwen", "ContainerName=qwen-vllm"), "ContainerName= is not qwen"),
    (lambda u: u.replace("Exec=batch", "Exec=serve"), "Exec= is not batch"),
    (lambda u: u.replace(":/app/api_key.txt:ro", ":/app/api_key.txt"), "key mount at /app/api_key.txt is not read-only"),
    (lambda u: u.replace("Volume=%s:/app/api_key.txt:ro\n" % "KEYPATH", ""), "exactly one read-only key mount"),
    (lambda u: u.replace("Environment=PORT=8080", "Environment=PORT=8080\nEnvironment=VLLM_API_KEY=%s" % KEY),
     "names VLLM_API_KEY"),
    (lambda u: u.replace("Environment=SPEC=mtp", "Environment=SPEC=mtp \\"), "continues on the next line"),
    (lambda u: u.replace("PublishPort=8080:8080\n", ""), "exactly one PublishPort= (it has 0)")])
def test_the_unit_is_copied_only_as_far_as_the_job_understands_it(sbs, edit, msg):
    unit = sbs.unit.read_text().replace(str(sbs.key), "KEYPATH")
    sbs.unit.write_text(edit(unit).replace("KEYPATH", str(sbs.key)))
    r = _job(sbs)
    assert r.returncode == 3 and msg in r.stderr, r.stderr
    assert KEY not in r.stderr and KEY not in r.stdout                 # a refusal never echoes an Environment= value
    _nothing_started(sbs)


def test_a_missing_unit_refuses(sbs):
    sbs.unit.unlink()
    r = _job(sbs)
    assert r.returncode == 3 and "cannot read the unit" in r.stderr, r.stderr
    _nothing_started(sbs)


@pytest.mark.parametrize("seam,msg", [("SBS_PYTHON", "no Python at"), ("SBS_PROBE", "no probe at")])
def test_a_missing_probe_or_python_refuses_before_the_server_starts(sbs, seam, msg):
    r = _job(sbs, **{seam: str(sbs.tmp / "absent")})
    assert r.returncode == 3 and msg in r.stderr, r.stderr
    _nothing_started(sbs)


# ------------------------------------------------------------------ the job: one configuration, end to end

def test_a_run_starts_the_server_waits_records_the_sizing_runs_the_probe_and_removes_it(sbs):
    r = _job(sbs)
    assert r.returncode == 0, r.stderr
    runs = [a for a in _podman(sbs) if a[:1] == ["run"]]
    assert runs == [expected_run(sbs.port, sbs.key, "0.90")]
    order = [i for i, a in enumerate(_podman(sbs)) if a[:1] in (["run"], ["logs"], ["rm"])]
    kinds = [_podman(sbs)[i][0] for i in order]
    assert kinds[0] == "run" and kinds[-1] == "rm" and kinds.count("rm") == 1 and ["logs", "qwen"] in _podman(sbs)
    assert ["logs", "-f", "qwen"] in _podman(sbs)
    assert sbs.srv.seen and set(sbs.srv.seen) == {("/v1/models", "Bearer " + KEY)}
    assert "@/dev/fd/" in (sbs.shim / "curl-argv.log").read_text()
    probe_argv = json.loads((sbs.shim / "probe-argv.log").read_text())
    assert probe_argv == ["--tokens", "16384", "--chunk", "4096", "--load", "4",
                          "--url", "http://127.0.0.1:%d/v1/chat/completions" % sbs.port,
                          "--key-file", str(sbs.key), "--out", str(sbs.out / "probe.json")]
    s = _summary(sbs)
    assert (s["rc"], s["reason"], s["probe_rc"], s["cleanup"]) == (0, None, 0, {"podman_rm_rc": 0})
    assert s["probe"]["key_file_is_the_served_key"] is True and s["probe"]["alone"] == {"ok": True}
    sz = s["sizing"]
    assert (sz["ok"], sz["missing"], sz["invalid"], sz["util_applied"]) == (True, [], [], True)
    assert (sz["available_kv_gib"], sz["kv_tokens"], sz["max_concurrency"], sz["desired_util"], sz["desired_gib"]) == (
        7.08, 222822, 1.70, 0.9, 21.2)
    assert (sz["max_concurrency_tokens_per_request"], sz["startup_free_gib"], sz["startup_total_gib"]) == (
        131072, 23.05, 23.56)
    assert (sz["consumed_gib"], sz["peak_activation_gib"], sz["cudagraph_gib"], sz["model_loading_gib"]) == (
        14.73, 1.09, 0.71, 14.26)
    assert isinstance(s["boot_seconds"], int) and s["config"]["util"] == 0.9
    _removed_once(sbs)
    assert _dead(int((sbs.shim / "follower.pid").read_text()))
    _key_never_leaked(sbs)


def test_the_default_port_is_8081_on_loopback_only(sbs):
    env = dict(sbs.env)
    env.pop("SBS_PORT")
    (sbs.shim / "never-up").touch()
    r = subprocess.run(["bash", str(SCRIPT), *ARGS, "--out", str(sbs.out)], capture_output=True, text=True,
                       env=dict(env, BOOT_SECONDS="0"), timeout=60)
    assert r.returncode == 1, r.stderr
    assert [a for a in _podman(sbs) if a[:1] == ["run"]] == [expected_run(8081, sbs.key, "0.90")]
    assert "http://127.0.0.1:8081/v1/models" in (sbs.shim / "curl-argv.log").read_text()
    _removed_once(sbs)


def test_the_premises_own_log_parses_to_its_numbers_and_a_share_not_applied_fails(sbs):
    """The brief's premise lines (the server at 0.972) under a 0.90 configuration: every number parses, and the
    share the server reports is not the configured one, so the job fails."""
    (sbs.shim / "server.log").write_text(PREMISE_LOG)
    r = _job(sbs)
    assert r.returncode == 1, r.stderr
    s = _summary(sbs)
    sz = s["sizing"]
    assert (sz["ok"], sz["util_applied"], sz["missing"], sz["invalid"]) == (False, False, [], [])
    assert (sz["available_kv_gib"], sz["kv_tokens"], sz["max_concurrency"], sz["desired_util"], sz["desired_gib"]) == (
        7.08, 222822, 1.70, 0.972, 22.9)
    assert s["rc"] == 1 and s["reason"].startswith("sizing:") and (sbs.shim / "probe-argv.log").exists()
    _removed_once(sbs)


@pytest.mark.parametrize("edit,missing", [
    (lambda t: t.replace("Available KV cache memory: 7.08 GiB\n", ""), ["available_kv_gib"]),
    (lambda t: t.replace("GPU KV cache size: 222,822 tokens, ", ""), ["kv_tokens"]),
    (lambda t: t.replace(", Maximum concurrency for 131,072 tokens per request: 1.70x", ""), ["max_concurrency"]),
    (lambda t: re.sub(r"Desired GPU memory utilization is \([^)]*\)\. ", "", t), ["desired_util", "desired_gib"])])
def test_a_missing_sizing_line_is_a_recorded_failure_never_a_zero(sbs, edit, missing):
    (sbs.shim / "server.log").write_text(edit(server_log()))
    r = _job(sbs)
    assert r.returncode == 1, r.stderr
    s = _summary(sbs)
    assert s["rc"] == 1 and s["reason"].startswith("sizing:")
    assert s["sizing"]["ok"] is False and s["sizing"]["missing"] == missing
    assert all(s["sizing"][name] is None for name in missing)
    _removed_once(sbs)


def test_a_zero_or_an_unreadable_number_is_invalid(sbs):
    (sbs.shim / "server.log").write_text(server_log().replace("222,822 tokens", "0 tokens").replace("1.70x", "1.7.0x"))
    r = _job(sbs)
    assert r.returncode == 1, r.stderr
    sz = _summary(sbs)["sizing"]
    assert sz["invalid"] == ["kv_tokens"] and sz["kv_tokens"] is None and sz["missing"] == ["max_concurrency"]


def test_the_sizing_lines_split_across_log_lines_parse_the_same(sbs):
    text = server_log().replace("tokens, Maximum", "tokens\n(EngineCore_DP0 pid=7) INFO 09-25 [kv_cache_utils.py] Maximum")
    (sbs.shim / "server.log").write_text(text)
    assert _job(sbs).returncode == 0
    assert _summary(sbs)["sizing"]["max_concurrency"] == 1.70


def test_a_boot_that_never_answers_fails_after_boot_seconds_and_removes(sbs):
    (sbs.shim / "never-up").touch()
    r = _job(sbs, BOOT_SECONDS="0")
    assert r.returncode == 1, r.stderr
    s = _summary(sbs)
    assert s["reason"] == "boot: http://127.0.0.1:%d/v1/models did not answer 200 within 0s" % sbs.port
    assert not (sbs.shim / "probe-argv.log").exists() and s["probe"] is None and s["sizing"] is None
    _removed_once(sbs)


def test_a_server_that_exits_during_boot_fails_at_once(sbs):
    (sbs.shim / "exits-at-boot").touch()
    t0 = time.monotonic()
    r = _job(sbs, BOOT_SECONDS="600")
    assert r.returncode == 1 and time.monotonic() - t0 < 20, r.stderr
    assert _summary(sbs)["reason"] == "boot: the server exited (see qwen.log)"
    _removed_once(sbs)


def test_a_failed_start_fails_and_still_removes(sbs):
    (sbs.shim / "run-fails").touch()
    r = _job(sbs)
    assert r.returncode == 1 and _summary(sbs)["reason"] == "podman run: rc 125 (see podman-run.log)", r.stderr
    _removed_once(sbs)


@pytest.mark.parametrize("mode,reason", [("fail", "probe: rc 1 (see probe.log)"),
                                         ("phase-not-ok", "probe: no measurement from together")])
def test_a_probe_without_every_measurement_fails_the_job(sbs, mode, reason):
    (sbs.shim / "probe-mode").write_text(mode)
    r = _job(sbs)
    assert r.returncode == 1, r.stderr
    assert (_summary(sbs)["rc"], _summary(sbs)["reason"]) == (1, reason)
    _removed_once(sbs)


def test_a_proxy_in_the_environment_is_never_used_for_the_loopback_check(sbs):
    dead = "http://127.0.0.1:9"
    r = _job(sbs, http_proxy=dead, HTTP_PROXY=dead, no_proxy="", NO_PROXY="")
    assert r.returncode == 0, r.stderr


# ------------------------------------------------------------------ the job: signals and the bounded cleanup

def test_term_to_the_job_group_stops_the_reader_and_removes_once(sbs):
    """What the runner's timeout does on abort or on its budget: TERM to the whole process group."""
    (sbs.shim / "probe-mode").write_text("sleep")
    proc = _start(sbs)
    try:
        pid = _pid(sbs, "probe.pid")
        t0 = time.monotonic()
        os.killpg(proc.pid, signal.SIGTERM)
        rc = proc.wait(timeout=40)
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
    assert rc == 130 and time.monotonic() - t0 < 10, (rc, proc.stderr.read())
    assert _dead(pid) and _dead(int((sbs.shim / "follower.pid").read_text()))
    s = _summary(sbs)
    assert (s["rc"], s["reason"], s["cleanup"]) == (130, "stopped by TERM", {"podman_rm_rc": 0})
    _removed_once(sbs)
    _key_never_leaked(sbs)


def test_term_to_the_job_alone_still_stops_the_reader(sbs):
    """A TERM to the shell alone never reaches its background reader: the cleanup must stop it."""
    (sbs.shim / "probe-mode").write_text("sleep")
    proc = _start(sbs)
    try:
        pid = _pid(sbs, "probe.pid")
        proc.send_signal(signal.SIGTERM)
        rc = proc.wait(timeout=40)
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
    assert rc == 130 and _dead(pid, seconds=5), rc
    assert _summary(sbs)["reason"] == "stopped by TERM"
    _removed_once(sbs)


def test_int_during_the_boot_wait_removes_once(sbs):
    (sbs.shim / "never-up").touch()
    proc = _start(sbs, BOOT_SECONDS="600")
    try:
        _wait_for(lambda: any(a[:1] == ["run"] for a in _podman(sbs)) and (sbs.shim / "curl-argv.log").exists())
        os.killpg(proc.pid, signal.SIGINT)
        rc = proc.wait(timeout=40)
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
    assert rc == 130 and _summary(sbs)["reason"] == "stopped by INT", rc
    assert not (sbs.shim / "probe-argv.log").exists()
    _removed_once(sbs)


def test_signals_during_the_cleanup_are_ignored_and_it_runs_once(sbs):
    (sbs.shim / "probe-mode").write_text("sleep")
    (sbs.shim / "rm-slow").touch()
    proc = _start(sbs)
    try:
        _pid(sbs, "probe.pid")
        os.killpg(proc.pid, signal.SIGTERM)
        _wait_for(lambda: "rm-start" in _calls(sbs))
        proc.send_signal(signal.SIGTERM)
        time.sleep(0.2)
        proc.send_signal(signal.SIGINT)
        rc = proc.wait(timeout=40)
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
    assert rc == 130 and _summary(sbs)["reason"] == "stopped by TERM", rc
    _removed_once(sbs)


def test_a_hung_removal_is_bounded(sbs):
    """The runner gives a job 30 s after TERM before KILL: a removal that ignores TERM is KILLed at its bound."""
    (sbs.shim / "probe-mode").write_text("sleep")
    (sbs.shim / "rm-hang").touch()
    proc = _start(sbs, SBS_RM_SECONDS="1")
    try:
        _pid(sbs, "probe.pid")
        t0 = time.monotonic()
        os.killpg(proc.pid, signal.SIGTERM)
        rc = proc.wait(timeout=40)
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
    assert rc == 130 and time.monotonic() - t0 < 12, (rc, time.monotonic() - t0)
    assert _summary(sbs)["cleanup"] == {"podman_rm_rc": 137}
    assert [a for a in _podman(sbs) if a[:1] == ["rm"]] == [["rm", "-f", "-i", "qwen"]]


def test_the_window_runner_stops_this_job_and_restores_the_service(sbs):
    """The composition: scripts/gpu_window.sh runs this job; a TERM to the runner reaches the job's reader through the
    runner's own timeout, the job removes its server once, and the runner starts the service again after it."""
    (sbs.shim / "probe-mode").write_text("sleep")
    (sbs.shim / "active").touch()
    runner_srv = _server(sbs.shim, "active")
    repo = sbs.tmp / "repo"
    (repo / ".lanes").mkdir(parents=True)
    jobs = sbs.tmp / "sbs.jobs"
    jobs.write_text("bash %s %s --out %s\n" % (SCRIPT, " ".join(ARGS), sbs.out))
    env = dict(sbs.env, AF_REPO=str(repo), QWEN_KEY_FILE=str(sbs.key), GPU_WINDOW_DIR=str(sbs.tmp / "state"),
               QWEN_MODELS_URL="http://127.0.0.1:%d/v1/models" % runner_srv.server_address[1],
               XDG_RUNTIME_DIR=str(sbs.tmp))
    proc = subprocess.Popen(INT_DEFAULT + ["bash", str(RUNNER), str(jobs)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, start_new_session=True)
    try:
        pid = _pid(sbs, "probe.pid")
        assert not (sbs.shim / "active").exists()                       # the window is open
        proc.send_signal(signal.SIGTERM)
        rc = proc.wait(timeout=60)
    finally:
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
        runner_srv.shutdown()
        runner_srv.server_close()
    assert rc == 130, proc.stderr.read()
    assert _dead(pid) and _summary(sbs)["reason"] == "stopped by TERM"
    _removed_once(sbs)
    calls = _calls(sbs)
    assert calls.index("rm-done") < calls.index("systemctl --user start qwen")
    events = [json.loads(line)["event"] for line in (sbs.tmp / "state" / "record.jsonl").read_text().splitlines()]
    assert events[-3:] == ["abort", "start", "back"] and (sbs.shim / "active").exists()


def _timeouts(text):
    """Every `timeout` invocation in shell code (comments dropped): (all of them, the ones without --foreground)."""
    code = "\n".join(re.sub(r"\s+#\s.*$", "", line) for line in text.splitlines() if not line.lstrip().startswith("#"))
    return re.findall(r"(?<![\w-])timeout \S+", code), re.findall(r"(?<![\w-])timeout (?!--foreground )\S+", code)


def test_every_inner_timeout_keeps_the_process_group():
    """A plain `timeout` makes a new process group (measured: its pgid is its own pid), which the window's TERM and KILL
    would not reach. Per occurrence, so a second call on a line cannot hide behind the first."""
    text = SCRIPT.read_text()
    uses, plain = _timeouts(text)
    assert len(uses) == 6 and plain == [], (uses, plain)
    mutant = text.replace("timeout --foreground -k 2 \"$RM_S\"", "timeout -k 2 \"$RM_S\"", 1)
    assert mutant != text and _timeouts(mutant)[1] == ['timeout -k']       # the check sees one dropped flag


def test_every_exit_once_the_traps_are_armed_ignores_int_and_term_first():
    """AF-AP-145, the deterministic form (tests/test_gpu_window.py's): the handlers open with the ignore, cleanup opens
    with it, and after the traps are armed every exit leaves through `leave` or `finish`."""
    code = [re.sub(r"\s+#\s.*$", "", line) for line in SCRIPT.read_text().splitlines()]
    assert "trap 'trap \"\" INT TERM; on_signal INT' INT" in code
    assert "trap 'trap \"\" INT TERM; on_signal TERM' TERM" in code
    assert "leave() { trap '' INT TERM; exit \"$1\"; }" in code
    c = code.index("cleanup() {")
    assert code[c + 1].strip() == "trap '' INT TERM"
    armed = code.index("trap 'on_exit $?' EXIT")
    bare = [(i + 1, line) for i, line in enumerate(code) if i > armed and re.search(r"(?<![\w-])exit(?![\w-])", line)
            and "sys.exit" not in line]
    assert bare == [], bare


# ------------------------------------------------------------------ the jobs file

def _job_lines():
    return [line for line in JOBS.read_text().splitlines() if line.strip() and not line.lstrip().startswith("#")]


def test_the_jobs_file_holds_the_briefs_two_configurations(sbs):
    lines = _job_lines()
    assert len(lines) == 2
    seen = []
    for line in lines:
        words = shlex.split(line)
        assert words[:3] == ["cd", "~/agent-factory", "&&"] and "timeout" in words and "--foreground" in words
        i = words.index("scripts/gpu_side_by_side.sh")
        args = dict(zip(words[i + 1::2], words[i + 2::2]))
        assert set(args) == {"--util", "--chunk", "--tokens", "--load", "--out"}
        assert (args["--tokens"], args["--load"]) == (BRIEF_TOKENS, BRIEF_LOAD)
        assert args["--out"].startswith("~/gpu-window/")
        seen.append((args["--util"], args["--chunk"]))
        # the job's own validation accepts them: refused at the window check (3), never at usage (64)
        (sbs.shim / "container").write_text("the live one\n")
        r = _run(sbs, *[x for k, v in args.items() if k != "--out" for x in (k, v)], "--out", str(sbs.out))
        assert r.returncode == 3 and "not inside a GPU window" in r.stderr, r.stderr
    assert seen == BRIEF_CONFIGS
    assert len({shlex.split(line)[-1] for line in lines}) == 2


# ------------------------------------------------------------------ the reader probe's harness

def _load_probe():
    spec = importlib.util.spec_from_file_location("rwkv_sbs_probe_under_test", PROBE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


probe = _load_probe()


def test_the_probe_imports_without_torch_or_transformers():
    code = ("import importlib.util, sys\n"
            "spec = importlib.util.spec_from_file_location('p', %r)\n"
            "m = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(m)\n"
            "m.load_g0()\n"
            "print(sorted(x for x in ('torch', 'transformers', 'fla') if x in sys.modules))\n" % str(PROBE))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0 and out.stdout.strip() == "[]", out.stderr


def _g0_node(tree, *path):
    node = tree
    for name in path:
        node = next(n for n in node.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)
    return node


def test_the_probe_asks_g0s_own_question_and_g0s_forward_keeps_one_position():
    """Scoped to the AST nodes (AF-AP-80): the string rwkv7_g0.phase_ladder encodes, and the keyword Scorer.forward
    passes to the model. A comment elsewhere in either file satisfies neither."""
    tree = ast.parse(G0.read_text())
    encoded = [c.args[0].value for c in ast.walk(_g0_node(tree, "phase_ladder")) if isinstance(c, ast.Call)
               and isinstance(c.func, ast.Attribute) and c.func.attr == "encode" and c.args
               and isinstance(c.args[0], ast.Constant) and isinstance(c.args[0].value, str)]
    assert encoded == [probe.QUESTION]
    kw = [k for c in ast.walk(_g0_node(tree, "Scorer", "forward")) if isinstance(c, ast.Call)
          for k in c.keywords if k.arg == "logits_to_keep"]
    assert len(kw) == 1 and isinstance(kw[0].value, ast.Constant) and kw[0].value.value == 1
    assert (probe.MODEL, probe.MAX_TOKENS, probe.QUESTION_REPEATS) == (BRIEF_MODEL, BRIEF_MAX_TOKENS, 5)
    own = {n.name for n in ast.parse(PROBE.read_text()).body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    assert not own & {"load", "real_text_ids", "phase_env", "Scorer", "phase_ladder"}   # imported, never copied


class FakeTensor:
    """The few tensor methods Engine uses, over a list or a scalar."""

    def __init__(self, v):
        self.v = v

    def float(self):
        return self

    def __sub__(self, other):
        return FakeTensor([a - b for a, b in zip(self.v, other.v)])

    def abs(self):
        return FakeTensor([abs(a) for a in self.v])

    def max(self):
        return FakeTensor(max(self.v))

    def argmax(self):
        return FakeTensor(self.v.index(max(self.v)))

    def all(self):
        return FakeTensor(all(self.v))

    def __float__(self):
        return float(self.v)

    def __int__(self):
        return int(self.v)

    def __bool__(self):
        return bool(self.v)


def test_main_reuses_g0_by_import_and_records_every_phase(tmp_path, monkeypatch, chat, capsys):
    """The real entry point with the GPU boundary faked: a stand-in torch module and a stand-in G0 module returned by
    load_g0. main must take the environment, the model, the text ids and the question from G0's functions, read
    through Engine -> Scorer.forward, run every phase inside inference_mode, and write the record with no key in it."""
    log, entered = [], []
    torch = types.ModuleType("torch")

    class _Mode:
        def __enter__(self):
            entered.append("in")

        def __exit__(self, *a):
            entered.append("out")

    torch.inference_mode = _Mode
    torch.isfinite = lambda x: FakeTensor([math.isfinite(a) for a in x.v])
    torch.cuda = types.SimpleNamespace(synchronize=lambda: None, reset_peak_memory_stats=lambda: None,
                                       max_memory_allocated=lambda: 1300 << 20, max_memory_reserved=lambda: 1400 << 20,
                                       empty_cache=lambda: None)
    monkeypatch.setitem(sys.modules, "torch", torch)

    class Scorer:
        calls = 0

        def forward(self, ids, cache=None):
            Scorer.calls += 1
            seen = (cache or {}).get("seen", 0) + len(ids)
            return FakeTensor([float((seen + k) % 3) for k in range(3)]), {"seen": seen}

    tok = types.SimpleNamespace(encode=lambda text, add_special_tokens: log.append(("encode", text, add_special_tokens))
                                or [5, 6, 7])
    g0 = types.SimpleNamespace(
        phase_env=lambda rec, a: log.append(("phase_env", vars(a))) or rec.update(env={"free_mib": 1576}),
        load=lambda rec, a: log.append(("load", vars(a))) or rec.update(load={"allocated_mib": 859}) or (tok, Scorer()),
        real_text_ids=lambda t, n: log.append(("real_text_ids", t is tok, n)) or list(range(n)))
    monkeypatch.setattr(probe, "load_g0", lambda: g0)
    shim = tmp_path / "bin" / "nvidia-smi"
    shim.parent.mkdir()
    shim.write_text('#!/usr/bin/env bash\necho "$PPID, 1234"\necho "4242, 21800"\n')
    shim.chmod(0o755)
    monkeypatch.setenv("PATH", "%s:%s" % (shim.parent, os.environ["PATH"]))
    key = tmp_path / "api-key"
    key.write_text(KEY + "\n")
    out = tmp_path / "probe.json"
    rc = probe.main(["--tokens", "4096", "--chunk", "1024", "--load", "2", "--url", chat.url, "--key-file", str(key),
                     "--out", str(out)])
    rec = json.loads(out.read_text())
    assert rc == 0 and rec["rc"] == 0 and all(rec[p]["ok"] is True for p in probe.PHASES), rec.get("error")
    assert [e[0] for e in log] == ["phase_env", "load", "real_text_ids", "encode"]
    assert log[0][1] == log[1][1] == {"plumbing": False, "no_cache": False}
    assert log[2] == ("real_text_ids", True, 4096) and log[3] == ("encode", probe.QUESTION, False)
    assert (rec["env"], rec["load"]) == ({"free_mib": 1576}, {"allocated_mib": 859})
    assert entered == ["in", "out"] and Scorer.calls >= 4 + 5 + 3 + 4 + 5          # alone, then together's pass 1
    assert rec["alone"]["read"]["chunks"] == 4 and rec["alone"]["read"]["peak_allocated_mib"] == 1300
    assert rec["smi_after_load"]["own_mib"] == 1234 and rec["alone"]["smi"]["apps"][1]["used_mib"] == 21800
    assert len(chat.seen) == 4 and all(s["auth"] == "Bearer " + KEY for s in chat.seen)
    assert KEY not in out.read_text() and KEY not in capsys.readouterr().out


def test_the_job_passes_what_the_probe_accepts(sbs):
    assert _job(sbs).returncode == 0
    args = probe.parse_args(json.loads((sbs.shim / "probe-argv.log").read_text()))
    assert (args.tokens, args.chunk, args.load, args.key_file) == (16384, 4096, 4, str(sbs.key))


@pytest.mark.parametrize("argv", [
    ["--tokens", "4096", "--chunk", "1023", "--load", "1"], ["--tokens", "4095", "--chunk", "4096", "--load", "1"],
    ["--tokens", "65537", "--chunk", "4096", "--load", "1"], ["--tokens", "4096", "--chunk", "4096", "--load", "9"]])
def test_the_probe_refuses_numbers_out_of_range(argv):
    with pytest.raises(SystemExit) as e:
        probe.parse_args(argv + ["--url", "http://127.0.0.1:1/v1/chat/completions", "--key-file", "k", "--out", "o"])
    assert e.value.code == 2


def test_the_probe_sends_the_key_to_loopback_only(capsys):
    with pytest.raises(SystemExit):
        probe.parse_args(["--tokens", "4096", "--chunk", "4096", "--load", "1", "--url",
                          "http://pc.example:8081/v1/chat/completions", "--key-file", "k", "--out", "o"])
    assert "--url must be loopback" in capsys.readouterr().err


class FakeEngine:
    """No torch: logits are lists, a state is a dict. A forward mutates the state it is given (as fla's cache does)
    and returns a new one; every call is logged with the object it received and a snapshot of it."""

    def __init__(self, nan=False, fail_after=None, on_call=None, delay=0.0):
        self.calls, self.returned, self.resets, self.releases = [], [], 0, 0
        self.nan, self.fail_after, self.on_call, self.delay = nan, fail_after, on_call, delay

    def forward(self, ids, state):
        if self.fail_after is not None and len(self.calls) >= self.fail_after:
            raise RuntimeError("fake CUDA out of memory")
        self.calls.append((tuple(ids), state, copy.deepcopy(state)))
        if self.on_call:
            self.on_call(len(self.calls))
        if self.delay:
            time.sleep(self.delay)
        seen = (state or {}).get("seen", 0) + len(ids)
        if state is not None:
            state["touched"] = state.get("touched", 0) + 1
        new = {"seen": seen}
        self.returned.append(new)
        return ([float("nan")] * 3 if self.nan else [float((seen + k) % 3) for k in range(3)]), new

    def sync(self):
        pass

    def reset_peak(self):
        self.resets += 1

    def peak(self):
        return {"peak_allocated_mib": 900 + len(self.calls), "peak_reserved_mib": 1000 + len(self.calls)}

    def finite(self, logits):
        return all(math.isfinite(x) for x in logits)

    def compare(self, a, b):
        return {"max_abs_logit_diff": max(abs(x - y) for x, y in zip(a, b)), "same_argmax": a.index(max(a)) == b.index(max(b))}

    def release(self):
        self.releases += 1


SMI_OK = {"ok": True, "own_pid": 1, "apps": [], "own_mib": None}


def test_the_read_carries_the_state_from_chunk_to_chunk():
    eng, ids = FakeEngine(), list(range(10))
    rows, state = probe.read(eng, ids, 4, time.perf_counter)
    assert [c[0] for c in eng.calls] == [tuple(range(0, 4)), tuple(range(4, 8)), (8, 9)]
    assert eng.calls[0][1] is None and eng.calls[1][1] is eng.returned[0] and eng.calls[2][1] is eng.returned[1]
    assert state is eng.returned[2] and state["seen"] == 10
    assert [(r["start"], r["tokens"]) for r in rows] == [(0, 4), (4, 4), (8, 2)] and eng.resets == 3
    assert [r["peak_allocated_mib"] for r in rows] == [901, 902, 903] and all(r["finite"] for r in rows)


def test_the_questions_read_a_fresh_copy_of_the_final_state_every_time():
    eng = FakeEngine()
    final = {"seen": 16384}
    q = probe.questions(eng, final, [7, 8, 9], time.perf_counter)
    assert len(eng.calls) == 5 and all(c[0] == (7, 8, 9) for c in eng.calls)
    assert all(c[1] is not final and c[2] == {"seen": 16384} for c in eng.calls)
    assert final == {"seen": 16384}                                     # the reader's state is never touched
    assert q["question_tokens"] == 3 and len(q["seconds_all"]) == 5 and q["finite"] is True
    assert q["seconds_median"] == round(sorted(q["seconds_all"])[2], 4) or abs(
        q["seconds_median"] - sorted(q["seconds_all"])[2]) < 1e-4


def test_the_chunk_check_compares_two_halves_with_one_whole():
    eng, ids = FakeEngine(), list(range(100))
    rec = probe.chunk_check(eng, ids, 8)
    assert [(c[0], c[1]) for c in eng.calls[:2]] == [(tuple(range(8)), None), (tuple(range(4)), None)]
    assert eng.calls[2][0] == tuple(range(4, 8)) and eng.calls[2][1] is eng.returned[1]
    assert (rec["tokens"], rec["first"], rec["second"]) == (8, 4, 4)
    assert rec["same_argmax"] is True and rec["max_abs_logit_diff"] == 0.0     # the fake's state sums: 8 either way


class _Chat(http.server.BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        s = self.server
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
        with s.lock:
            s.seen.append({"auth": self.headers.get("Authorization"), "path": self.path, "body": body})
            reply = s.replies.pop(0) if s.replies else {"usage": {"prompt_tokens": 1500, "completion_tokens": 37}}
        if self.headers.get("Authorization") != "Bearer " + KEY:
            return self._send(401, {"error": "bad key"})
        if s.barrier is not None:
            s.barrier.wait(timeout=10)
        if s.hold is not None:
            s.hold.wait(timeout=30)
        code = reply.pop("_code", 200)
        self._send(code, reply)

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a):
        pass


@pytest.fixture
def chat():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Chat)
    srv.seen, srv.replies, srv.barrier, srv.hold, srv.lock = [], [], None, None, threading.Lock()
    srv.url = "http://127.0.0.1:%d/v1/chat/completions" % srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield srv
    if srv.hold is not None:
        srv.hold.set()
    srv.shutdown()
    srv.server_close()


def _ticks(step=0.25):
    """A thread-safe clock that advances one step per call: the load's first and last reads are the main thread's, so
    its wall is (calls - 1) steps whatever order the request threads read it in."""
    lock, n = threading.Lock(), [0]

    def clock():
        with lock:
            n[0] += 1
            return n[0] * step
    return clock


def test_the_load_sends_n_requests_at_once_with_the_four_keys_and_the_key_in_the_header(chat):
    chat.barrier = threading.Barrier(4)                                 # sequential requests would break it
    payload = probe.chat_payload(probe.prompt_text())
    rec = probe.chat_load(probe.make_post(chat.url, KEY), 4, payload, _ticks(), 0.0)
    assert rec["ok"] is True and (rec["requests"], rec["requests_ok"], rec["completion_tokens"]) == (4, 4, 148)
    assert (rec["start"], rec["end"], rec["wall_seconds"]) == (0.25, 2.5, 2.25)   # 10 reads: main, 4 x 2, main
    assert rec["tokens_per_second"] == round(148 / 2.25, 3) == 65.778
    assert len(chat.seen) == 4
    for seen in chat.seen:
        assert seen["auth"] == "Bearer " + KEY and seen["path"] == "/v1/chat/completions"
        assert set(seen["body"]) == BRIEF_PAYLOAD_KEYS
        assert (seen["body"]["model"], seen["body"]["max_tokens"], seen["body"]["temperature"]) == (
            BRIEF_MODEL, BRIEF_MAX_TOKENS, 0)
        assert seen["body"]["messages"][0]["content"].startswith((ROOT / "docs" / "01_ARCHITECTURE.md").read_text()[:200])
        assert KEY not in json.dumps(seen["body"])
    assert all(r["ok"] and r["completion_tokens"] == 37 and r["end"] >= r["start"] for r in rec["rows"])


def test_a_response_without_usage_fails_its_row_never_a_zero(chat):
    chat.replies = [{"choices": []}]
    rec = probe.chat_load(probe.make_post(chat.url, KEY), 3, probe.chat_payload("p"), time.perf_counter,
                          time.perf_counter())
    bad = [r for r in rec["rows"] if not r["ok"]]
    assert rec["ok"] is False and rec["requests_ok"] == 2 and rec["completion_tokens"] == 74
    assert len(bad) == 1 and "completion_tokens" not in bad[0] and "no integer usage" in bad[0]["error"]


def test_an_error_body_that_echoes_the_key_is_scrubbed(chat):
    chat.replies = [{"_code": 500, "detail": "raw %s; header Bearer %s; cut Bearer %s" % (KEY, KEY, KEY[:9])}]
    rec = probe.chat_load(probe.make_post(chat.url, KEY), 1, probe.chat_payload("p"), time.perf_counter,
                          time.perf_counter(), probe.scrubber(KEY))
    assert rec["ok"] is False and rec["rows"][0]["status"] == 500
    assert KEY[:9] not in json.dumps(rec) and rec["rows"][0]["error"].count("<key>") == 3


def test_a_wrong_key_is_a_failed_row(chat):
    rec = probe.chat_load(probe.make_post(chat.url, "not-the-key"), 1, probe.chat_payload("p"), time.perf_counter,
                          time.perf_counter())
    assert rec["ok"] is False and rec["rows"][0]["status"] == 401


def test_every_phase_with_no_load(chat):
    eng, rec, writes = FakeEngine(), {}, []
    rc = probe.run_phases(rec, eng, list(range(8)), [1, 2], 4, 0, probe.make_post(chat.url, KEY),
                          probe.chat_payload("p"), smi=lambda: SMI_OK, write=lambda: writes.append(sorted(rec)))
    assert rc == 0 and chat.seen == []
    assert rec["qwen_idle_rwkv"] == {"ok": True, "skipped": "N is 0: no load"}
    assert rec["together"]["load"] == {"skipped": "N is 0: no load"} and rec["together"]["more_passes"] == []
    assert rec["alone"]["read"]["chunks"] == 2 and rec["alone"]["questions"]["question_tokens"] == 2
    assert rec["alone"]["chunk_check"]["tokens"] == 4 and rec["alone"]["smi"] == SMI_OK
    assert writes == [["alone"], ["alone", "qwen_idle_rwkv"], ["alone", "qwen_idle_rwkv", "together"]]


def test_together_keeps_rwkv_working_until_the_load_ends(chat):
    """The load is held until RWKV has made 40 forwards (pass 1 is 2 chunks + 5 questions = 7), so it outlasts pass 1:
    further passes must run until the load ends, and the overlap must say RWKV covered the load."""
    chat.hold = threading.Event()
    eng = FakeEngine(delay=0.001, on_call=lambda n: chat.hold.set() if n >= 40 else None)
    t = {}
    probe.phase_together(t, eng, list(range(8)), [1, 2], 4, probe.make_post(chat.url, KEY), 2, probe.chat_payload("p"),
                         time.perf_counter, lambda: SMI_OK, str)
    assert t["ok"] is True and t["load"]["ok"] is True and t["load"]["requests_ok"] == 2, t
    assert t["read"]["chunks"] == 2 and t["questions"]["question_tokens"] == 2 and len(eng.calls) >= 40
    assert len(t["more_passes"]) >= 4 and all(p["chunks"] == 2 for p in t["more_passes"])
    assert t["overlap"]["first_pass_inside_load"] is True and t["overlap"]["rwkv_end"] >= t["overlap"]["load_end"]
    assert t["overlap"]["load_fraction_with_rwkv"] >= 0.9


def test_a_failed_phase_keeps_the_earlier_rows_and_the_next_phase_still_runs(chat):
    eng = FakeEngine(fail_after=10)                    # alone: 2 chunks + 5 questions + 3 check forwards = 10 calls
    rec, writes = {}, []
    rc = probe.run_phases(rec, eng, list(range(8)), [1, 2], 4, 2, probe.make_post(chat.url, KEY),
                          probe.chat_payload("p"), smi=lambda: SMI_OK, write=lambda: writes.append(json.dumps(rec)))
    assert rc == 1 and rec["alone"]["ok"] is True and rec["qwen_idle_rwkv"]["ok"] is True
    assert rec["together"]["ok"] is False and "fake CUDA out of memory" in rec["together"]["error"]
    assert eng.releases == 1 and len(writes) == 3 and '"together"' not in writes[1]


def test_non_finite_logits_fail_the_phase(chat):
    rec = {}
    rc = probe.run_phases(rec, FakeEngine(nan=True), list(range(8)), [1, 2], 4, 0, probe.make_post(chat.url, KEY),
                          probe.chat_payload("p"), smi=lambda: SMI_OK)
    assert rc == 1 and rec["alone"]["ok"] is False and rec["alone"]["read"]["finite"] is False


def test_a_failed_nvidia_smi_fails_the_phase_it_measures(chat):
    rec = {}
    rc = probe.run_phases(rec, FakeEngine(), list(range(8)), [1, 2], 4, 0, probe.make_post(chat.url, KEY),
                          probe.chat_payload("p"), smi=lambda: {"ok": False, "error": "rc 18"})
    assert rc == 1 and rec["alone"]["ok"] is False and rec["together"]["ok"] is False


def test_smi_records_every_compute_app_and_its_own_row():
    me = os.getpid()
    out = "4242, 21800\n%d, 1830\n777, [N/A]\n" % me
    rec = probe.smi_apps(run=lambda *a, **k: types.SimpleNamespace(returncode=0, stdout=out, stderr=""))
    assert rec["ok"] is True and rec["own_pid"] == me and rec["own_mib"] == 1830
    assert [(a["pid"], a["used_mib"]) for a in rec["apps"]] == [(4242, 21800), (me, 1830), (777, None)]
    rec = probe.smi_apps(run=lambda *a, **k: types.SimpleNamespace(returncode=0, stdout="4242, 21800\n", stderr=""))
    assert rec["ok"] is True and rec["own_mib"] is None                 # not listed: recorded as absent, not a zero
    rec = probe.smi_apps(run=lambda *a, **k: types.SimpleNamespace(returncode=18, stdout="NVML mismatch", stderr=""))
    assert rec["ok"] is False and rec["error"].startswith("rc 18")

    def hang(*a, **k):
        raise subprocess.TimeoutExpired("nvidia-smi", 10)
    assert probe.smi_apps(run=hang)["ok"] is False


def test_smi_runs_the_real_binary_on_path(tmp_path, monkeypatch):
    shim = tmp_path / "nvidia-smi"
    shim.write_text('#!/usr/bin/env bash\n[ "$*" = "--query-compute-apps=pid,used_memory --format=csv,noheader,'
                    'nounits" ] || exit 9\necho "$PPID, 1234"\n')
    shim.chmod(0o755)
    monkeypatch.setenv("PATH", "%s:%s" % (tmp_path, os.environ["PATH"]))
    rec = probe.smi_apps()
    assert rec["ok"] is True and rec["own_mib"] == 1234, rec


def test_the_probe_fails_loud_without_a_model_and_never_leaks_the_key(tmp_path):
    """The real entry point in the sandbox: no torch (or no model under this HOME), so it records the error and
    exits 1 with its record written. CUDA is hidden so a venue that has torch cannot reach a GPU from a test."""
    key = tmp_path / "api-key"
    key.write_text(KEY + "\n")
    out = tmp_path / "out" / "probe.json"
    env = dict(os.environ, HOME=str(tmp_path), CUDA_VISIBLE_DEVICES="")
    r = subprocess.run([sys.executable, str(PROBE), "--tokens", "4096", "--chunk", "4096", "--load", "0", "--url",
                        "http://127.0.0.1:9/v1/chat/completions", "--key-file", str(key), "--out", str(out)],
                       capture_output=True, text=True, env=env, timeout=120)
    assert r.returncode == 1, r.stderr
    rec = json.loads(out.read_text())
    assert rec["rc"] == 1 and rec["error"] and not any(p in rec for p in probe.PHASES)
    assert rec["config"]["tokens"] == 4096 and rec["prompt"]["source"] == "docs/01_ARCHITECTURE.md"
    assert KEY not in r.stdout + r.stderr + out.read_text()
