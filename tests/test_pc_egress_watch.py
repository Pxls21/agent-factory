"""scripts/pc_egress_watch.sh (task #365, H1b): the egress watch records a lane's connections and no one else's.

The runner starts Hermes as `hermes -p <lane profile> ...`, so a lane process is one whose command line carries
`-p <profile>`. The controls: a process with that argv connects to a local listener and the watch records the peer
under its pid (positive); a child of such a process is recorded too (the descendant walk); a process whose profile only
shares the prefix is not recorded (the name boundary); the refusals keep the watch to lane profile names."""
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WATCH = ROOT / "scripts" / "pc_egress_watch.sh"
CLIENT = "import socket,sys,time; c=socket.create_connection(('127.0.0.1', int(sys.argv[1]))); time.sleep(3)"
PARENT = "import subprocess,sys; subprocess.run([sys.executable, '-c', sys.argv[2], sys.argv[1]])"

pytestmark = pytest.mark.skipif(not (shutil.which("ss") and shutil.which("pgrep")),
                                reason="LOUD SKIP: the egress watch needs ss and pgrep")


@pytest.fixture
def listener():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    s.listen(8)
    yield s.getsockname()[1]
    s.close()


def _profile(tag):
    return f"aflanet{os.getpid()}{tag}"


def _watch(prof, out, max_s="8"):
    env = dict(os.environ, EGRESS_WATCH_GRACE="1")
    r = subprocess.run(["bash", str(WATCH), prof, str(out), max_s], env=env, capture_output=True, text=True,
                       timeout=60)
    assert r.returncode == 0, r.stderr
    summary = Path(str(out) + ".summary").read_text().splitlines()
    lines = [ln.split() for ln in Path(out).read_text().splitlines()]
    return summary, lines


def test_a_lane_process_connection_is_recorded_under_its_pid(tmp_path, listener):
    prof = _profile("pos")
    client = subprocess.Popen([sys.executable, "-c", CLIENT, str(listener), "-p", prof])
    try:
        summary, lines = _watch(prof, tmp_path / "out.txt")
    finally:
        client.wait(timeout=30)
    assert summary[0].startswith("WATCH-END seen=1 lines="), summary
    assert any(ln.split()[1:] == ["tcp", f"127.0.0.1:{listener}"] for ln in summary[1:]), summary
    assert lines and {ln[1] for ln in lines} == {str(client.pid)}, lines


def test_a_child_of_a_lane_process_is_recorded(tmp_path, listener):
    prof = _profile("kid")
    parent = subprocess.Popen([sys.executable, "-c", PARENT, str(listener), CLIENT, "-p", prof])
    try:
        summary, lines = _watch(prof, tmp_path / "out.txt")
    finally:
        parent.wait(timeout=30)
    assert summary[0].startswith("WATCH-END seen=1 lines="), summary
    peers = [ln for ln in lines if ln[3] == f"127.0.0.1:{listener}"]
    assert peers and str(parent.pid) not in {ln[1] for ln in peers}, lines


def test_a_profile_that_only_shares_the_prefix_is_not_recorded(tmp_path, listener):
    prof = _profile("neg")
    other = subprocess.Popen([sys.executable, "-c", CLIENT, str(listener), "-p", prof + "x"])
    try:
        summary, lines = _watch(prof, tmp_path / "out.txt", max_s="3")
    finally:
        other.wait(timeout=30)
    assert summary == ["WATCH-END seen=0 lines=0"], summary
    assert lines == []


@pytest.mark.parametrize("args", [
    ["notalane", "OUT"],
    ["aflaneABC", "OUT"],
    ["aflane", "OUT"],
    ["aflanex", "OUT", "12a"],
    ["aflanex"],
])
def test_the_watch_refuses_what_is_not_a_lane_profile(tmp_path, args):
    argv = [str(tmp_path / "o.txt") if a == "OUT" else a for a in args]
    r = subprocess.run(["bash", str(WATCH), *argv], capture_output=True, text=True, timeout=30)
    assert r.returncode == 64, (r.returncode, r.stderr)
    assert not (tmp_path / "o.txt").exists()
