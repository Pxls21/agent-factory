"""The PC's model-server units (task #454's switch; D-129, D-131): deploy/qwen.container, the live SGLang unit, and
deploy/qwen-vllm.container, the vLLM fallback (D-032) that replaces it under the same name and port.

Each relation is read from the consumer that enforces it: harness-ports/bin/lane-profile.sh's own MAX_LEN parser (run
here from its heredoc) gives every lane profile its context; deploy/sglang_start.py owns --api-key, --context-length and
--config and reads the key from its KEY_FILE_DEFAULT; OmniRoute's local route forwards qwen3.8-27b-local to port 8080;
the live image is the one pc-lane.lock.yaml pins (D-131), with the start script's hash beside it, and the fallback's is
the one upstream.lock.yaml pins (D-032). Nothing here starts a container: the real start is checked on the PC."""
import hashlib
import importlib.util
import pathlib
import re
import shlex
import subprocess
import sys

import pytest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
LIVE = ROOT / "deploy" / "qwen.container"
FALLBACK = ROOT / "deploy" / "qwen-vllm.container"
START = ROOT / "deploy" / "sglang_start.py"
LANE_PROFILE = ROOT / "harness-ports" / "bin" / "lane-profile.sh"


def unit(path):
    """systemd's reading: a trailing backslash joins the next line; '#' and ';' lines are comments; a repeated key
    keeps every value in order."""
    out, section = {}, None
    for line in path.read_text().replace("\\\n", " ").splitlines():
        line = line.strip()
        if not line or line[0] in "#;":
            continue
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        k, eq, v = line.partition("=")
        assert eq, f"{path.name}: a line that is no key=value: {line[:60]!r}"
        out.setdefault((section, k.strip()), []).append(v.strip())
    return out


def one(u, section, key):
    vals = u.get((section, key), [])
    assert len(vals) == 1, (section, key, vals)
    return vals[0]


def start_module():
    spec = importlib.util.spec_from_file_location("sglang_start_under_test", START)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lane_profile_context(path):
    """lane-profile.sh's quadlet_context_length, its Python run as the script runs it."""
    src = LANE_PROFILE.read_text()
    m = re.search(r"quadlet_context_length\(\) \{\n  python3 - \"\$QWEN_QUADLET\" <<'PY'\n(.*?)\nPY\n\}", src, re.S)
    assert m, "lane-profile.sh's quadlet_context_length heredoc moved"
    return subprocess.run([sys.executable, "-", str(path)], input=m.group(1), capture_output=True, text=True,
                          timeout=30)


@pytest.mark.parametrize("path", [LIVE, FALLBACK], ids=["sglang", "vllm"])
def test_lane_profiles_read_131072_from_either_unit(path):
    # both variants state the same context, so a fallback swap leaves every lane profile right
    r = lane_profile_context(path)
    assert (r.returncode, r.stdout, r.stderr) == (0, "131072\n", "")


@pytest.mark.parametrize("path", [LIVE, FALLBACK], ids=["sglang", "vllm"])
def test_both_units_are_the_qwen_container_and_service(path):
    u = unit(path)
    assert one(u, "Container", "ContainerName") == "qwen"   # the name gpu_window.sh and the guards stop and start
    assert one(u, "Container", "PublishPort") == "8080:8080"  # OmniRoute's qwen-local node
    assert one(u, "Service", "Restart") == "always" and one(u, "Install", "WantedBy") == "default.target"
    assert one(u, "Service", "CPUQuota") == "300%"  # at most three CPU threads, whichever unit serves (D-136)
    # never unwatched: the heat guard starts first, and stopping it stops the model server (D-136)
    assert one(u, "Unit", "Requires") == "heat-guard.service" and "heat-guard.service" in u[("Unit", "After")]
    assert re.fullmatch(r"[a-z0-9./_-]+@sha256:[0-9a-f]{64}", one(u, "Container", "Image"))
    assert "/home/rocco/.config/qwen-builder/api-key:/app/api_key.txt:ro" in u[("Container", "Volume")]


def test_the_live_unit_starts_sglang_through_the_start_script():
    u = unit(LIVE)
    words = shlex.split(one(u, "Container", "Exec"))
    assert words[:2] == ["python3", "/af/sglang_start.py"]
    assert one(u, "Container", "Entrypoint") == "/opt/entrypoint.sh"  # it execs a command of two or more words
    mod = start_module()
    owned = [w for w in words if w.split("=", 1)[0] in mod.OWN_FLAGS]
    assert owned == []  # the start script would refuse them; the key and the context never ride on argv
    assert words[words.index("--served-model-name") + 1] == "qwen3.8-27b-local"
    assert words[words.index("--port") + 1] == "8080" and words[words.index("--host") + 1] == "0.0.0.0"
    for flag in ("--enable-metrics", "--enable-cache-report", "--enable-hierarchical-cache"):
        assert flag in words
    # the GPU headroom the grammar kernels need at first use; without it a long prompt with tools ran out of memory
    assert "--disable-prefill-cuda-graph" in words
    # an idle scheduler waits for requests; without it, it pins one CPU thread at 100% (D-135)
    assert "--sleep-on-idle" in words


def test_the_live_unit_mounts_the_key_and_the_start_script_read_only():
    u = unit(LIVE)
    vols = u[("Container", "Volume")]
    mod = start_module()
    assert f"/home/rocco/.config/qwen-builder/api-key:{mod.KEY_FILE_DEFAULT}:ro" in vols
    assert "/home/rocco/.config/qwen-serving/sglang_start.py:/af/sglang_start.py:ro" in vols
    assert all(v.endswith(":ro") for v in vols)
    env = [w for line in u[("Container", "Environment")] for w in shlex.split(line)]
    assert [w for w in env if w.startswith("MAX_LEN=")] == ["MAX_LEN=131072"]
    assert not any(w.split("=", 1)[0] in ("SGL_KEY_FILE", "SGLANG_API_KEY", "API_KEY") for w in env)


def test_the_live_image_and_start_script_are_the_lock_pins():
    lock = yaml.safe_load((ROOT / "pc-lane.lock.yaml").read_text())
    pin = lock["local_model_servers"]["sglang-exl3"]
    image = one(unit(LIVE), "Container", "Image")
    assert image == f"{pin['image']}@{pin['digest']}"
    assert pin["start_script"] == "deploy/sglang_start.py" and pin["unit"] == "deploy/qwen.container"
    assert pin["start_script_sha256"] == hashlib.sha256(START.read_bytes()).hexdigest()
    assert re.fullmatch(r"[0-9a-f]{40}", pin["sglang_revision"]) and re.fullmatch(r"[0-9a-f]{40}", pin["model_revision"])
    assert "task #463" in pin["full_migration_owed"]


def test_the_fallback_is_the_vllm_pin_upstream_lock_holds():
    u = unit(FALLBACK)
    pin = yaml.safe_load((ROOT / "upstream.lock.yaml").read_text())["local_model_server"]["qwen38-27b-rtx3090"]
    image = one(u, "Container", "Image")
    assert image.split("@")[1] == pin["digest"] and image.split("@")[0] == pin["image"].rsplit(":", 1)[0]
    assert one(u, "Container", "Exec") == "batch"
