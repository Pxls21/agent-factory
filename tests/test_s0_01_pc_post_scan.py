"""Real-producer contract for the S0-01 process observation (pc_post.sh `scan`, v2.3).

The checkpoint-5 audit ran the actual producer against controlled process tables and showed the checker
rejecting a successful cleanup (empty scan) while accepting an owned `sleep 60` survivor. These tests run
the SAME producer script in the sandbox against a process tree this test owns, so every process-evidence
fixture the checker suite consumes can be pinned to this output (AF-AP-42), and the header that lets the
checker distinguish "enumerated, nothing owned left" from "no scan ran" is proven at the source.

The tree: parent ("buzz") -> child ("tee") -> grandchild ("agent"), all `python3 -c` sleepers spawned by the
test, killed by the test. Only pids from this tree are ever signalled (AF-AP-34).
"""
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PC_POST = ROOT / "proofs" / "S0-01" / "tools" / "pc" / "pc_post.sh"

_TREE = r"""
import os, subprocess, sys, time
# parent = "buzz"; child = "tee"; grandchild = "agent" — each prints its pid on one line, then sleeps.
child = subprocess.Popen([sys.executable, "-c",
    "import subprocess, sys, time; g = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)']);"
    " print(g.pid, flush=True); time.sleep(120)"], stdout=subprocess.PIPE, text=True)
gpid = child.stdout.readline().strip()
print(os.getpid(), child.pid, gpid, flush=True)
time.sleep(120)
"""

_HEADER_RE = re.compile(
    r"^# process-scan v2\.3 mode=(after|teardown) rows=(\d+) buzz_acp_pid=(\d+|none) buzz_present=([01]) "
    r"owned=(\d+) owned_present=(\d+) pinned_present=(\d+) owned_zombies=(\d+) utc=(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)$")


@pytest.fixture
def tree():
    proc = subprocess.Popen([sys.executable, "-c", _TREE], stdout=subprocess.PIPE, text=True)
    pids = [int(x) for x in proc.stdout.readline().split()]
    assert len(pids) == 3 and pids[0] == proc.pid
    yield pids
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    proc.wait(timeout=10)


def _scan(mode: str, fd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(PC_POST), "scan", mode, str(fd)], capture_output=True, text=True,
                          env={**os.environ, "S0_01_REPO": str(ROOT)}, timeout=60)


def _seed(fd: Path, buzz: int, owned: list[int]) -> None:
    (fd / "buzz-acp.pid").write_text(f"{buzz}\n")
    (fd / "owned-pids.json").write_text(json.dumps({"buzz_acp_pid": buzz, "owned": owned, "taken_at": "ready"}))


def _parse(path: Path):
    lines = path.read_text().splitlines()
    m = _HEADER_RE.match(lines[0])
    assert m, f"header does not match the v2.3 shape: {lines[0]!r}"
    rows = []
    for line in lines[1:]:
        pid, ppid, etimes, cmd = line.split(None, 3)
        rows.append((int(pid), int(ppid), int(etimes), cmd))
    return m, rows


def _gone_or_zombie(pid: int) -> bool:
    try:
        stat = Path(f"/proc/{pid}/stat").read_text()
    except OSError:
        return True
    return stat.rsplit(")", 1)[1].split()[0] == "Z"   # the state field follows the parenthesised comm


def _wait_gone(pids, timeout=10.0):
    """A SIGKILLed process is gone or a zombie (exited, unreaped) — both mean it no longer runs."""
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if all(_gone_or_zombie(p) for p in pids):
            return
        time.sleep(0.1)
    raise AssertionError(f"pids still running after kill: {pids}")


def test_after_scan_persists_the_owned_closure_and_the_header(tree, tmp_path):
    buzz, tee, agent = tree
    _seed(tmp_path, buzz, [buzz])
    r = _scan("after", tmp_path)
    assert r.returncode == 0, r.stderr
    m, rows = _parse(tmp_path / "process-scan-after.txt")
    assert m.group(1) == "after"
    assert int(m.group(2)) > 3                       # the full table was enumerated (ps, this test, the tree ...)
    assert m.group(3) == str(buzz) and m.group(4) == "1"
    assert m.group(5) == "3" and m.group(6) == "3"   # closure = buzz, tee, agent; all present
    assert m.group(7) == "0"                          # no pinned path runs in the sandbox
    assert {row[0] for row in rows} == {buzz, tee, agent}
    by_pid = {row[0]: row for row in rows}
    assert by_pid[tee][1] == buzz and by_pid[agent][1] == tee
    owned = json.loads((tmp_path / "owned-pids.json").read_text())
    assert owned == {"buzz_acp_pid": buzz, "owned": sorted([buzz, tee, agent]), "taken_at": "ready+after"}


def test_teardown_scan_after_a_clean_exit_is_empty_with_owned_present_zero(tree, tmp_path):
    buzz, tee, agent = tree
    _seed(tmp_path, buzz, [buzz])
    assert _scan("after", tmp_path).returncode == 0
    for pid in (agent, tee, buzz):
        os.kill(pid, signal.SIGKILL)
    _wait_gone((agent, tee, buzz))
    r = _scan("teardown", tmp_path)
    assert r.returncode == 0, r.stderr
    m, rows = _parse(tmp_path / "process-scan-teardown.txt")
    assert m.group(1) == "teardown" and int(m.group(2)) > 0
    assert m.group(4) == "0"                          # buzz gone
    assert m.group(5) == "3" and m.group(6) == "0"    # closure remembered, nothing of it LIVE
    assert rows == []                                 # a clean cleanup IS an empty body
    assert int(m.group(8)) <= 3                       # unreaped members are counted, never listed as survivors


def test_teardown_scan_names_an_owned_survivor_whatever_its_command(tree, tmp_path):
    buzz, tee, agent = tree
    _seed(tmp_path, buzz, [buzz])
    assert _scan("after", tmp_path).returncode == 0
    for pid in (tee, buzz):                            # the agent grandchild survives (the audit's `sleep 60`)
        os.kill(pid, signal.SIGKILL)
    _wait_gone((tee, buzz))
    r = _scan("teardown", tmp_path)
    assert r.returncode == 0, r.stderr
    m, rows = _parse(tmp_path / "process-scan-teardown.txt")
    assert m.group(6) == "1"                          # exactly one owned process still LIVE
    assert [row[0] for row in rows] == [agent]
    assert "time.sleep(120)" in rows[0][3]            # its real command line, not a pinned path


def test_scan_rejects_an_unknown_mode(tmp_path):
    _seed(tmp_path, 1, [1])
    r = _scan("bogus", tmp_path)
    assert r.returncode != 0
    assert "scan: mode must be after|teardown, got 'bogus'" in r.stderr
    assert not (tmp_path / "process-scan-bogus.txt").exists()


def test_scan_rows_are_not_clipped_at_80_columns(tmp_path):
    """PC gate 2026-09-06: on the PC, `ps -eo args` off a tty clipped every row at 80 columns, so the long venv path
    pushed the survivor's real command (and would push a pinned path) out of the evidence; the producer now uses -ww.
    The sandbox's ps did NOT clip (this test was green there before the fix), so its red proof is the PC venue —
    `scripts/pc_suite.sh` is where this test guards the property."""
    marker = "S0_01_LONG_ARGV_MARKER_" + "x" * 90
    parent = subprocess.Popen([sys.executable, "-c",
                               "import subprocess, sys, time; g = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120) # %s']);"
                               " print(g.pid, flush=True); time.sleep(120)" % marker], stdout=subprocess.PIPE, text=True)
    try:
        child = int(parent.stdout.readline())
        (tmp_path / "buzz-acp.pid").write_text(f"{parent.pid}\n")
        r = _scan("after", tmp_path)
        assert r.returncode == 0, r.stderr
        rows = _parse(tmp_path / "process-scan-after.txt")[1]
        by_pid = {row[0]: row for row in rows}
        assert child in by_pid
        assert marker in by_pid[child][3]
        assert len(by_pid[child][3]) > 100
    finally:
        for p in (child, parent.pid):
            try:
                os.kill(p, 9)
            except ProcessLookupError:
                pass
        parent.wait(timeout=10)


def test_owned_row_is_never_dropped_by_the_helper_filter(tmp_path):
    """VERIFY-CK7 producer/consumer note: the scan drops its own helper rows (`pc_post.sh`, `ps -e…`) — an OWNED row
    whose command happens to contain those strings is evidence and must stay, so owned_present == owned body rows."""
    parent = subprocess.Popen([sys.executable, "-c",
                               "import subprocess, sys, time; g = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120) # pc_post.sh ps -eo']);"
                               " print(g.pid, flush=True); time.sleep(120)"], stdout=subprocess.PIPE, text=True)
    try:
        child = int(parent.stdout.readline())
        _seed(tmp_path, parent.pid, [parent.pid, child])
        r = _scan("after", tmp_path)
        assert r.returncode == 0, r.stderr
        m, rows = _parse(tmp_path / "process-scan-after.txt")
        assert {row[0] for row in rows} == {parent.pid, child}
        assert m.group(6) == "2" and len(rows) == 2          # owned_present equals the owned rows in the body
    finally:
        for p in (child, parent.pid):
            try:
                os.kill(p, 9)
            except ProcessLookupError:
                pass
        parent.wait(timeout=10)
