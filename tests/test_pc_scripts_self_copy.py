"""The self-copy guard on the long-running bridge scripts (lane_gate.sh, pc_lane.sh, pc_suite.sh): each re-execs from a
private copy of its own bytes so an edit to the file cannot corrupt a running instance (bash reads scripts lazily —
2026-09-08: two live gates died that way). The regression this pins: after the re-exec `$0`/`BASH_SOURCE` name the COPY
under /tmp, so the repo root must come from the *_ORIG variable — the first version of the guard resolved ROOT to `/` and
pc_lane.sh died with "PC_BRIDGE_URL not set" before reading its brief. Run from a foreign cwd, each script must reach its
own argument validation (proving ROOT resolved) and leave no copy behind (the EXIT trap)."""
import glob
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(script, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("PC_")}
    env["TMPDIR"] = str(ROOT / ".pytest-selfcopy-tmp")
    Path(env["TMPDIR"]).mkdir(exist_ok=True)
    r = subprocess.run(["bash", str(ROOT / "scripts" / script), *args], cwd="/", env=env,
                       capture_output=True, text=True, timeout=60)
    leftovers = glob.glob(str(Path(env["TMPDIR"]) / (script + ".*")))
    return r, leftovers


def test_pc_lane_resolves_its_root_from_the_original_path():
    r, leftovers = _run("pc_lane.sh", "/nonexistent-brief.md", "hermes", "code-implementer")
    # past the bridge-env check (ROOT resolved, .pc-bridge.env loaded or the env exported) and onto the brief
    assert "PC_BRIDGE_URL not set" not in r.stderr or "brief not found" in r.stderr, r.stderr
    assert leftovers == []


def test_pc_suite_prints_usage_from_a_foreign_cwd():
    r, leftovers = _run("pc_suite.sh")
    assert "usage" in (r.stdout + r.stderr).lower(), r.stdout + r.stderr
    assert leftovers == []


def test_lane_gate_usage_from_a_foreign_cwd():
    r, leftovers = _run("lane_gate.sh")
    assert r.returncode == 64 and "usage" in r.stderr, r.stderr
    assert leftovers == []
