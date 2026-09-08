"""Real-producer contract for the S0-01 process observation (pc_post.sh `scan`, v2.4).

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

# v2.4 (P5a, SWEEP-prod #5 + SWEEP-tests 4.2/15.2): `rows` counts the rows THIS FILE carries and `table_rows`
# the full process table — two populations, two names, never asserted equal. In v2.3 one name carried both
# meanings, so `pinned_present` (full table) could exceed the body it headed, and a producer-side `rows=4`
# literal left all 11 tests in this file green while the header lied about the table it headed.
_HEADER_RE = re.compile(
    r"^# process-scan v2\.4 mode=(after|teardown) rows=(\d+) buzz_acp_pid=(\d+|none) buzz_present=([01]) "
    r"owned=(\d+) owned_present=(\d+) pinned_present=(\d+) owned_zombies=(\d+) table_rows=(\d+) "
    r"utc=(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)$")
_ROWS, _TABLE_ROWS = 2, 9   # header group numbers: the body counter and the full-table counter


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
    assert m, f"header does not match the v2.4 shape: {lines[0]!r}"
    rows = []
    for line in lines[1:]:
        pid, ppid, etimes, cmd = line.split(None, 3)
        rows.append((int(pid), int(ppid), int(etimes), cmd))
    # SWEEP-tests 15.2: the header's own counter against its own body, on EVERY caller. `> 3` / `> 0` could not
    # express "the enumeration header describes this file": a hard-coded `rows=4` in the producer passed both.
    assert int(m.group(_ROWS)) == len(rows), (
        f"header rows={m.group(_ROWS)} but the body carries {len(rows)} rows")
    return m, rows


sys.path.insert(0, str(ROOT / "proofs" / "S0-01"))
import pins  # noqa: E402 — the producer's only pin source; the pinned paths are never repeated as literals here


def _is_pinned(cmd: str) -> bool:
    """The producer's OWN rule, not a mirror of it: `pins.is_pinned_argv` (VERIFY-P5a F4, A5k list item 5).

    This used to be a hand copy (AF-AP-42) justified by the producer's rule living inside a `python3 - <<PY`
    heredoc — but that heredoc already imports pins by path, so the copy bought nothing and cost the usual
    price: when the producer's version admitted `/usr/bin/cat <tee>`, so did this one, and every assertion
    written against it agreed with the defect. Producer, checker and test now compute one predicate; the
    contract is still driven end to end through the real producer in
    test_pinned_present_is_exact_over_a_synthetic_table."""
    return pins.is_pinned_argv(cmd.split())


def _split_world(rows, owned):
    """The scan is WORLD-scoped by design: its body carries every owned row AND every live row that IS a pinned
    process, whoever spawned it. Under a parallel venue (the PC gate runs 8 xdist workers) a sibling worker's
    real tee lands in THIS test's body — PC run 20260907T161133Z, AF-AP-59. So a test asserts the OWNED subset
    exactly and characterises the rest: every foreign row must be admissible under the producer's only other
    rule (it is pinned by entry point); anything else is an unexplained row and fails."""
    own = [r for r in rows if r[0] in owned]
    foreign = [r for r in rows if r[0] not in owned]
    for r in foreign:
        assert _is_pinned(r[3]), f"unexplained foreign row in the scan body: {r!r}"
    return own, foreign


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
    assert int(m.group(_TABLE_ROWS)) > 3             # the full table was enumerated (ps, this test, the tree ...)
    assert int(m.group(_TABLE_ROWS)) >= int(m.group(_ROWS))   # two populations; the body is a subset, never larger
    assert m.group(3) == str(buzz) and m.group(4) == "1"
    assert m.group(5) == "3" and m.group(6) == "3"   # closure = buzz, tee, agent; all present
    own, foreign = _split_world(rows, {buzz, tee, agent})
    # v2.4: pinned_present is counted over the BODY, so it is EXACT from inside one test even under a parallel
    # venue (AF-AP-59) — a sibling worker's real tee is foreign, pinned, and lands in body and header alike; a
    # sibling's helper-shaped row is dropped from both. None of this tree's rows is a pinned entry point, so the
    # count is exactly the foreign rows. (In v2.3 the header counted the full table and could only be bounded.)
    assert int(m.group(7)) == len(foreign)
    assert {row[0] for row in own} == {buzz, tee, agent}
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
    assert m.group(1) == "teardown" and int(m.group(_TABLE_ROWS)) > 0   # the table was enumerated ...
    assert int(m.group(_ROWS)) == len(rows)                             # ... and the body counter is its own
    assert m.group(4) == "0"                          # buzz gone
    assert m.group(5) == "3" and m.group(6) == "0"    # closure remembered, nothing of it LIVE
    own, _foreign = _split_world(rows, {buzz, tee, agent})
    assert own == []                                  # a clean cleanup IS an empty OWNED body
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
    own, _foreign = _split_world(rows, {buzz, tee, agent})
    assert [row[0] for row in own] == [agent]
    assert "time.sleep(120)" in own[0][3]             # its real command line, not a pinned path


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
        own, _foreign = _split_world(rows, {parent.pid, child})
        assert {row[0] for row in own} == {parent.pid, child}
        assert m.group(6) == "2" and len(own) == 2           # owned_present equals the OWNED rows in the body
    finally:
        for p in (child, parent.pid):
            try:
                os.kill(p, 9)
            except ProcessLookupError:
                pass
        parent.wait(timeout=10)


def test_scan_fails_loud_on_an_unparsable_ps_row(tmp_path):
    """VERIFY-CK8 F13: a ps row with fewer than five fields used to be skipped silently — and a skipped row is absent from
    rows=, owned_present and pinned_present alike, so an owned survivor lost that way would be invisible to every checker
    rule. The scan now exits 1 naming the row. Driven through a `ps` shim on PATH that prints one short row first."""
    shim_dir = tmp_path / "bin"
    shim_dir.mkdir()
    shim = shim_dir / "ps"
    shim.write_text("#!/bin/sh\necho '4242 1 7 S'\nexec /usr/bin/ps \"$@\"\n")
    shim.chmod(0o755)
    fd = tmp_path / "fd"
    fd.mkdir()
    r = subprocess.run(["bash", str(PC_POST), "scan", "after", str(fd)], capture_output=True, text=True,
                       env={**os.environ, "S0_01_REPO": str(ROOT), "PATH": f"{shim_dir}:{os.environ['PATH']}"}, timeout=60)
    assert r.returncode == 1, (r.returncode, r.stderr)
    assert r.stderr.strip() == "scan: unparsable ps row (4 fields): '4242 1 7 S'"
    assert not (fd / "process-scan-after.txt").exists()


def test_a_process_that_only_mentions_a_pinned_path_is_not_counted_as_pinned(tmp_path):
    """SWEEP-prod #6, through REAL processes: `any(p in r[3] for p in PINNED)` counted a `sleep` whose argv merely
    MENTIONED the pinned tee path as a pinned process (the sweep's decoy moved pinned_present 1 -> 2 and put the
    sleeper in the body). v2.4 matches the ENTRY POINT: argv[0] for the buzz-acp binary, argv[1] for the two pinned
    scripts. Neither decoy below is a pinned entry point, so both are absent from the body and from the counter.

    This test replaces VERIFY-CK8 F14, whose property — a helper-shaped pinned row dropped from the body while
    still counted in the header, surfacing as a loud `pinned_present … inconsistent with body` — is deliberately
    RETIRED by the #5 fix: both counters now come off the same list, so the drop shows only as table_rows > rows.
    The helper filter itself is still pinned, over a synthetic table, by the test below."""
    tee = pins.PINNED_TEE_PATH
    buzz = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"])
    helper = subprocess.Popen([sys.executable, "-c", f"import time; time.sleep(120) # {tee} pc_post.sh"])
    plain = subprocess.Popen([sys.executable, "-c", f"import time; time.sleep(120) # {tee}"])
    try:
        _seed(tmp_path, buzz.pid, [buzz.pid])
        r = _scan("after", tmp_path)
        assert r.returncode == 0, r.stderr
        m, rows = _parse(tmp_path / "process-scan-after.txt")
        body_pids = {row[0] for row in rows}
        assert buzz.pid in body_pids                       # owned root kept, whatever its command
        assert plain.pid not in body_pids                  # mentions the tee path in a comment: NOT an entry point
        assert helper.pid not in body_pids                 # same, and helper-shaped as well
        assert not any(_is_pinned(row[3]) for row in rows if row[0] in (plain.pid, helper.pid))
        # the decoys are invisible to BOTH counters (in v2.3 they moved pinned_present)
        assert int(m.group(7)) == sum(1 for row in rows if _is_pinned(row[3]))
    finally:
        for proc in (helper, plain, buzz):
            proc.kill()
            proc.wait(timeout=10)


def test_split_world_rejects_an_unexplained_foreign_row():
    """VERIFY-CK10 F-R10-20: the negative control of the world-aware helper, COMMITTED. A foreign row that names no
    pinned path is an unexplained process in the scan body — the helper must FAIL, never characterise it away."""
    with pytest.raises(AssertionError, match="unexplained foreign row"):
        _split_world([(1, 0, 5, "/usr/bin/sleep 60")], owned={2})


def test_split_world_admits_a_foreign_row_that_is_a_pinned_entry_point():
    """The positive twin: a foreign row that IS a pinned entry point (here the real tee shape, `python3 <tee>`) is
    admissible evidence — the producer's only other rule — and comes back in `foreign`, never in `own`; the owned
    row comes back in `own` whatever its command."""
    rows = [(2, 0, 5, "/usr/bin/sleep 60"), (1, 0, 5, f"python3 {pins.PINNED_TEE_PATH}")]
    own, foreign = _split_world(rows, owned={2})
    assert [r[0] for r in own] == [2]
    assert [r[0] for r in foreign] == [1]


def test_split_world_rejects_a_row_that_only_mentions_a_pinned_path():
    """The negative control of the MIRROR itself (SWEEP-prod #6): the helper must not admit a row whose command
    merely contains a pinned path — that was the producer's old substring rule, and a test helper that kept it
    would characterise away exactly the rows the producer no longer emits."""
    decoy = f"python3 -c 'time.sleep(1) # {pins.PINNED_TEE_PATH}'"
    assert not _is_pinned(decoy)
    with pytest.raises(AssertionError, match="unexplained foreign row"):
        _split_world([(1, 0, 5, decoy)], owned={2})


def test_parse_rejects_a_header_whose_rows_counter_lies(tmp_path):
    """SWEEP-tests 4.2/15.2, the negative control of the one-line fix: with `rows=4` hard-coded in the producer the
    whole file was green (`11 passed in 1.28s`). `_parse` now compares the header's own counter with the body it
    heads, so a lying header fails wherever it is read."""
    scan = tmp_path / "process-scan-after.txt"
    scan.write_text(
        "# process-scan v2.4 mode=after rows=4 buzz_acp_pid=1 buzz_present=1 owned=1 owned_present=1 "
        "pinned_present=0 owned_zombies=0 table_rows=9 utc=2026-09-08T00:00:00Z\n"
        "1 0 5 /usr/bin/sleep 60\n"
        "2 1 5 /usr/bin/sleep 60\n")
    with pytest.raises(AssertionError, match=r"header rows=4 but the body carries 2 rows"):
        _parse(scan)


def test_pinned_present_is_exact_over_a_synthetic_table(tmp_path):
    """The EXACT v2.4 contract, driven through the REAL producer over a `ps` shim that prints a synthetic table and
    nothing else — no world, no sibling worker, no AF-AP-59 flakiness (VERIFY-CK10 F-R10-20 asked for an exact
    number; from inside a live-table test that number used to be world-scoped).

    Its shape is unchanged from v2.3; its EXPECTATIONS changed twice. (a) `rows` is now the body counter and
    `table_rows` the full table, so the "whole table enumerated" assertion moved to table_rows (#5 / tests 15.2).
    (b) The rows themselves are now the three shapes a captured leg really carries plus the two the rule must
    reject, because pinned-ness is the ENTRY POINT and not a substring (#6): under v2.3 the decoy at 5001 — a
    `python3 -c` sleeper whose comment names the tee — WAS counted as a pinned process and kept in the body.

    Table: 4242 owned, unpinned · 5001 decoy naming the tee in a `-c` string · 5002 helper-shaped AND a genuine
    tee entry point · 5003 foreign and unrelated · 5004 the real buzz-acp · 5005 the real tee · 5006 the real
    agent · 5007 a real `/usr/bin/cat <tee>`. Body = owned + the three real pinned rows (the helper-shaped one
    is filtered out); pinned_present counts the body's pinned rows (3), never the filtered 5002, never the
    decoy, never the bystander.

    Row 5007 is VERIFY-P5a F4, reproduced there with a REAL process: under the first v2.4 rule any command
    whose FIRST OPERAND is a pinned script counted as pinned, so `cat`, `vim`, `less` or `sha256sum` on
    frame_tee.py — an owner reading the file during a capture — moved pinned_present and entered the leg's
    evidence body, where the checker then failed the leg for a bystander."""
    tee, agent = pins.PINNED_TEE_PATH, pins.PINNED_AGENT_REALPATH
    buzz_exe = pins.PINNED_BUZZ_ACP_EXE_REALPATH
    shim_dir = tmp_path / "bin"
    shim_dir.mkdir()
    shim = shim_dir / "ps"
    shim.write_text(
        "#!/bin/sh\n"
        "echo '4242 1 7 S /usr/bin/sleep 120'\n"
        f"echo '5001 1 7 S python3 -c \"time.sleep(120) # {tee}\"'\n"
        f"echo '5002 1 7 S python3 {tee} pc_post.sh'\n"
        "echo '5003 1 7 S /usr/bin/sleep 60'\n"
        f"echo '5004 1 7 S {buzz_exe} --relay-url ws://127.0.0.1:3999 --agent-command {tee} --agent-args'\n"
        f"echo '5005 5004 7 S python3 {tee}'\n"
        f"echo '5006 5005 7 S /home/rocco/s0-01-pinned/.venv-hermes/bin/python3 {agent}'\n"
        f"echo '5007 1 7 S /usr/bin/cat {tee}'\n"
    )
    shim.chmod(0o755)
    fd = tmp_path / "fd"
    fd.mkdir()
    _seed(fd, 4242, [4242])
    r = subprocess.run(["bash", str(PC_POST), "scan", "after", str(fd)], capture_output=True, text=True,
                       env={**os.environ, "S0_01_REPO": str(ROOT), "PATH": f"{shim_dir}:{os.environ['PATH']}"}, timeout=60)
    assert r.returncode == 0, (r.returncode, r.stderr)
    m, rows = _parse(fd / "process-scan-after.txt")           # _parse pins rows == len(body)
    assert m.group(_TABLE_ROWS) == "8"                        # the whole synthetic table was enumerated
    assert m.group(_ROWS) == "4"                              # ... and the body is the four rows below
    assert (m.group(6), m.group(7)) == ("1", "3"), m.group(0)  # owned_present exact; pinned_present over the BODY
    assert {row[0] for row in rows} == {4242, 5004, 5005, 5006}
    assert 5001 not in {row[0] for row in rows}               # #6: mentioning a pinned path is not being one
    assert 5002 not in {row[0] for row in rows}               # helper-shaped, dropped from body AND header alike
    assert 5007 not in {row[0] for row in rows}               # F4: `cat <tee>` is a bystander, not an entry point
