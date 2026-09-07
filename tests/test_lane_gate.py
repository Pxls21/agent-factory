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
    gate = next(p for p in tmp_path.iterdir() if p.name.startswith("gate-"))
    assert (gate / "scripts" / "test_summary.sh").is_file()  # a real archive, not the shared tree


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
