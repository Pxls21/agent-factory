"""lane_gate.sh — the one-command static-copy gate: an archive of REV plus exactly the named working-tree files, the identity
table of those files, N test_summary runs whose counts must agree, one RESULT line. Exercised on a two-test set so it runs
in seconds; the archive is a real `git archive` of HEAD."""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(tmp_path, *args):
    env = dict(os.environ, LANE_GATE_DIR=str(tmp_path))
    return subprocess.run(["bash", str(ROOT / "scripts/lane_gate.sh"), *args], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=600)


def test_gate_runs_the_tests_on_the_archive_and_reports_agreeing_counts(tmp_path):
    r = _run(tmp_path, "-r", "HEAD", "-f", "tests/test_ap_screen.py", "-t", "tests/test_ap_screen.py", "-n", "2")
    assert r.returncode == 0, r.stdout + r.stderr
    result = [l for l in r.stdout.splitlines() if l.startswith("RESULT:")][-1]
    assert "identical=yes rc=0" in result and "3 passed" in result, result
    ident = [l for l in r.stdout.splitlines() if l.endswith("lines") and "tests/test_ap_screen.py" in l]
    assert len(ident) == 1 and len(ident[0].split()[0]) == 64  # sha256 + path + line count
    # a green, agreeing gate removes its archive (the temp filesystem filled with them); the run logs remain
    assert not [p for p in tmp_path.iterdir() if p.name.startswith("gate-") and p.is_dir()], "archive kept after a green gate"
    gate = tmp_path / [l.name for l in tmp_path.glob("gate-*.run1.log")][0].replace(".run1.log", "")
    # every run's full pytest output is kept beside the archive, green runs included
    logs = sorted(tmp_path.glob(gate.name + ".run*.log"))
    assert [l.name for l in logs] == [gate.name + ".run1.log", gate.name + ".run2.log"], logs
    assert all("3 passed" in l.read_text() for l in logs)
    assert "archive removed" in r.stdout


def test_gate_keeps_the_archive_when_asked_or_red(tmp_path):
    env_keep = dict(os.environ, LANE_GATE_DIR=str(tmp_path / "keep"), LANE_GATE_KEEP="1")
    (tmp_path / "keep").mkdir()
    r = subprocess.run(["bash", str(ROOT / "scripts/lane_gate.sh"), "-r", "HEAD", "-f", "tests/test_ap_screen.py",
                        "-t", "tests/test_ap_screen.py", "-n", "1"], cwd=ROOT, env=env_keep, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0 and [p for p in (tmp_path / "keep").iterdir() if p.is_dir()], r.stdout + r.stderr


def test_gate_refuses_an_unresolvable_rev_and_a_missing_lane_file(tmp_path):
    r = _run(tmp_path, "-r", "no-such-rev", "-f", "tests/test_ap_screen.py", "-t", "tests/test_ap_screen.py")
    assert r.returncode == 65 and "does not resolve" in r.stderr
    r = _run(tmp_path, "-r", "HEAD", "-f", "tests/no_such_file.py", "-t", "tests/test_ap_screen.py")
    assert r.returncode == 67 and "absent in the working tree" in r.stderr


def test_gate_fails_when_a_run_is_red(tmp_path):
    bad = tmp_path / "test_red_probe.py"; bad.write_text("def test_red():\n    assert 0\n")
    # a lane file outside the repo cannot be copied by relative path; point -f at a real file and -t at the red test's abs path
    r = _run(tmp_path, "-r", "HEAD", "-f", "tests/test_ap_screen.py", "-t", str(bad), "-n", "1")
    assert r.returncode != 0
    result = [l for l in r.stdout.splitlines() if l.startswith("RESULT:")][-1]
    assert "rc=1" in result and "1 failed" in result, result
    assert [p for p in tmp_path.iterdir() if p.name.startswith("gate-") and p.is_dir()], "a red gate must keep its archive"
    # a red run NAMES its failing test inline and keeps the full pytest output beside the archive (2026-09-08: a
    # "1 failed, 113 passed" with no test name forced a blind re-run of a three-minute gate)
    assert "test_red" in r.stdout and "full output:" in r.stdout, r.stdout
    log = [l.split("full output: ", 1)[1].strip() for l in r.stdout.splitlines() if "full output:" in l][0]
    assert Path(log).is_file() and "test_red" in Path(log).read_text(), log


def test_gate_names_gitignored_files_under_the_lane_directories(tmp_path):
    """AF-AP-62 (2026-09-08): 16 gitignored buzzacp.log files under S0-02's committed bundles never reached the git-view
    copy — the lane's own byte-copy gate was green, the coordinator's `39 failed`. The gate now NAMES ignored files under
    the lane's directories (informational: the run itself still grades the git view, so the red stays red)."""
    probe = ROOT / "tests" / "lane_gate_ignored_probe.log"  # *.log is ignored at the repo root
    assert subprocess.run(["git", "check-ignore", "-q", str(probe)], cwd=ROOT).returncode == 0, "*.log must be ignored"
    probe.write_text("ignored\n")
    try:
        r = _run(tmp_path, "-r", "HEAD", "-f", "tests/test_ap_screen.py", "-t", "tests/test_ap_screen.py", "-n", "1")
    finally:
        probe.unlink()
    assert r.returncode == 0, r.stdout + r.stderr
    warn = [l for l in r.stdout.splitlines() if l.startswith("lane_gate: WARNING")]
    assert len(warn) == 1 and "gitignored file(s) under the lane's directories" in warn[0], r.stdout
    assert "tests/lane_gate_ignored_probe.log" in r.stdout, r.stdout

