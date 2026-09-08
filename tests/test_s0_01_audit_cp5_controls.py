"""Checkpoint-5 audit controls for the S0-01 process-evidence check (coordinator-owned, AF-AP-36 pre-mint gate).

The owner's external auditor (2026-09-06, review of 541648c) ran the real producer against controlled
process tables and fed its output to `check_process_evidence`: a successful cleanup (empty scan) was
REJECTED and an owned `/usr/bin/sleep 60` survivor was ACCEPTED, because the shutdown branch demanded a
non-empty scan and screened only the pinned command names. These controls encode the contract the
checker must meet, built from the REAL producer (`pc_post.sh scan`, v2.4 with the enumeration header)
run on a process tree this test owns. They were committed RED (AF-AP-36 pre-mint gate) and made green by lane A5c —
no lane may edit this file.

Contract under test (A20 v2.4):
  * a scan file's first line is the enumeration header; `table_rows > 0` proves enumeration ran while `rows` counts the body;
  * a SHUTDOWN leg's after-scan with `owned_present=0` and an empty body is a PASS (cleanup succeeded);
  * any owned pid that is still LIVE in the shutdown after-scan or in any teardown scan is a survivor →
    Failure `"<leg>: process <pid> (<cmd[:40]>) survived shutdown|teardown"`, whatever its command line;
  * exited-but-unreaped members (zombies) are counted in the header, never listed, never survivors.
"""
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PC_POST = ROOT / "proofs" / "S0-01" / "tools" / "pc" / "pc_post.sh"
CHECKER = ROOT / "proofs" / "S0-01" / "check_acp_conformance.py"

sys.path.insert(0, str(ROOT / "proofs" / "S0-01"))
_spec = importlib.util.spec_from_file_location("check_acp_conformance", CHECKER)
cc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cc)

_TREE = r"""
import os, subprocess, sys, time
child = subprocess.Popen([sys.executable, "-c",
    "import subprocess, sys, time; g = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)']);"
    " print(g.pid, flush=True); time.sleep(120)"], stdout=subprocess.PIPE, text=True)
gpid = child.stdout.readline().strip()
print(os.getpid(), child.pid, gpid, flush=True)
time.sleep(120)
"""


@pytest.fixture
def tree():
    proc = subprocess.Popen([sys.executable, "-c", _TREE], stdout=subprocess.PIPE, text=True)
    pids = [int(x) for x in proc.stdout.readline().split()]
    assert len(pids) == 3 and pids[0] == proc.pid
    yield proc, pids
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    proc.wait(timeout=10)


def _scan(mode: str, fd: Path) -> None:
    r = subprocess.run(["bash", str(PC_POST), "scan", mode, str(fd)], capture_output=True, text=True,
                       env={**os.environ, "S0_01_REPO": str(ROOT)}, timeout=60)
    assert r.returncode == 0, r.stderr


def _gone_or_zombie(pid: int) -> bool:
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return True
    return stat.rsplit(")", 1)[1].split()[0] == "Z"


def _kill(proc, pids, reap_root=True):
    for pid in pids:
        os.kill(pid, signal.SIGKILL)
    end = time.monotonic() + 10
    while time.monotonic() < end and not all(_gone_or_zombie(p) for p in pids):
        time.sleep(0.1)
    assert all(_gone_or_zombie(p) for p in pids), pids
    if reap_root and proc.pid in pids:
        proc.wait(timeout=10)


def _spawned(fd: Path, buzz: int) -> None:
    """What the launcher writes at spawn, BEFORE any scan: the pidfile and the READY-time owned set."""
    (fd / "buzz-acp.pid").write_text(f"{buzz}\n")
    (fd / "owned-pids.json").write_text(json.dumps({"buzz_acp_pid": buzz, "owned": [buzz], "taken_at": "ready"}))


def _shutdown_leg(fd: Path, tee: int, agent: int) -> None:
    """What the shutdown leg leaves behind after buzz-acp exits on `!shutdown`."""
    (fd / "buzz-acp.exit").write_text("0\n")
    (fd / "runtime-identity.json").write_text(json.dumps({"tee_pid": tee, "agent_child_pid": agent}))


def test_clean_shutdown_empty_after_scan_passes(tree, tmp_path):
    """Audit control 1: all owned processes exited -> the producer's empty scan is a PASS, not a Failure."""
    proc, (buzz, tee, agent) = tree
    _spawned(tmp_path, buzz)
    _scan("after", tmp_path)                       # READY-time closure while the tree is alive (launcher role)
    _kill(proc, [agent, tee, buzz])                # the `!shutdown` exit: everything owned is gone
    _scan("after", tmp_path)                       # the shutdown leg's after-scan runs AFTER buzz-acp.exit exists
    _scan("teardown", tmp_path)
    _shutdown_leg(tmp_path, tee, agent)
    body = (tmp_path / "process-scan-after.txt").read_text().splitlines()
    assert body[0].startswith("# process-scan v2.4 mode=after ") and " owned_present=0 " in body[0]
    assert body[1:] == []
    cc.check_process_evidence(tmp_path, "shutdown")   # must not raise


def test_shutdown_owned_survivor_is_named_whatever_its_command(tree, tmp_path):
    """Audit control 2: an owned process that outlives the shutdown is a Failure naming pid + cmd."""
    proc, (buzz, tee, agent) = tree
    _spawned(tmp_path, buzz)
    _scan("after", tmp_path)
    _kill(proc, [tee, buzz])                       # the grandchild (the audit's `sleep 60`) survives
    _scan("after", tmp_path)
    _scan("teardown", tmp_path)
    _shutdown_leg(tmp_path, tee, agent)
    rows = (tmp_path / "process-scan-after.txt").read_text().splitlines()[1:]
    assert len(rows) == 1 and rows[0].split()[0] == str(agent)
    cmd = rows[0].split(None, 3)[3]
    with pytest.raises(cc.Failure) as ei:
        cc.check_process_evidence(tmp_path, "shutdown")
    assert str(ei.value) == f"shutdown: process {agent} ({cmd[:40]}) survived shutdown"


def test_scan_without_the_enumeration_header_is_rejected(tree, tmp_path):
    """A scan file that lacks the v2.4 header cannot prove enumeration ran — Failure naming the file."""
    proc, (buzz, tee, agent) = tree
    _spawned(tmp_path, buzz)
    _scan("after", tmp_path)
    _kill(proc, [agent, tee, buzz])
    _scan("after", tmp_path)
    _scan("teardown", tmp_path)
    _shutdown_leg(tmp_path, tee, agent)
    (tmp_path / "process-scan-after.txt").write_text("")   # the pre-v2.3 shape of a clean shutdown
    with pytest.raises(cc.Failure) as ei:
        cc.check_process_evidence(tmp_path, "shutdown")
    assert str(ei.value) == "shutdown: process-scan-after.txt has no enumeration header"
