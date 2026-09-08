"""lane_gate.sh — the one-command static-copy gate: an archive of REV plus exactly the named working-tree files, the identity
table of those files, N test_summary runs whose counts must agree, one RESULT line. The archive is a real `git archive` of
HEAD; the lane file is a three-test PROBE each test writes under tests/.lane_gate_probe_<id>/ — a dot-directory that pytest's
default norecursedirs keeps out of any concurrent `pytest tests/` in the shared tree, and a file HEAD's archive does not
carry, so the run is green ONLY because the gate copied the working-tree bytes. (2026-09-08: these tests used to point at
tests/test_ap_screen.py and went red whenever a live lane held that file in a state HEAD's tree could not pass — a tooling
test must never depend on the shared tree's live-lane state.)"""
import os
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PROBE_BODY = "def test_one():\n    assert 1\n\n\ndef test_two():\n    assert 2\n\n\ndef test_three():\n    assert 3\n"


@pytest.fixture
def probe():
    """ROOT-relative path of a three-test file in an untracked dot-directory under tests/; the directory is removed after."""
    d = ROOT / "tests" / f".lane_gate_probe_{uuid.uuid4().hex[:8]}"
    d.mkdir()
    (d / "test_probe.py").write_text(PROBE_BODY)
    try:
        yield f"tests/{d.name}/test_probe.py"
    finally:
        shutil.rmtree(d)


def _run(tmp_path, *args):
    env = dict(os.environ, LANE_GATE_DIR=str(tmp_path))
    return subprocess.run(["bash", str(ROOT / "scripts/lane_gate.sh"), *args], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=600)


def test_gate_runs_the_tests_on_the_archive_and_reports_agreeing_counts(tmp_path, probe):
    # the probe is absent from HEAD's archive: the green below exists only if the gate copied the working-tree bytes over it
    assert subprocess.run(["git", "cat-file", "-e", f"HEAD:{probe}"], cwd=ROOT, capture_output=True).returncode != 0
    r = _run(tmp_path, "-r", "HEAD", "-f", probe, "-t", probe, "-n", "2")
    assert r.returncode == 0, r.stdout + r.stderr
    result = [l for l in r.stdout.splitlines() if l.startswith("RESULT:")][-1]
    assert "identical=yes rc=0" in result and "3 passed" in result, result
    ident = [l for l in r.stdout.splitlines() if l.endswith("lines") and probe in l]
    assert len(ident) == 1 and len(ident[0].split()[0]) == 64  # sha256 + path + line count
    # a green, agreeing gate removes its archive (the temp filesystem filled with them); the run logs remain
    assert not [p for p in tmp_path.iterdir() if p.name.startswith("gate-") and p.is_dir()], "archive kept after a green gate"
    gate = tmp_path / [l.name for l in tmp_path.glob("gate-*.run1.log")][0].replace(".run1.log", "")
    # every run's full pytest output is kept beside the archive, green runs included
    logs = sorted(tmp_path.glob(gate.name + ".run*.log"))
    assert [l.name for l in logs] == [gate.name + ".run1.log", gate.name + ".run2.log"], logs
    assert all("3 passed" in l.read_text() for l in logs)
    assert "archive removed" in r.stdout


def test_gate_keeps_the_archive_when_asked_or_red(tmp_path, probe):
    env_keep = dict(os.environ, LANE_GATE_DIR=str(tmp_path / "keep"), LANE_GATE_KEEP="1")
    (tmp_path / "keep").mkdir()
    r = subprocess.run(["bash", str(ROOT / "scripts/lane_gate.sh"), "-r", "HEAD", "-f", probe, "-t", probe, "-n", "1"],
                       cwd=ROOT, env=env_keep, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0 and [p for p in (tmp_path / "keep").iterdir() if p.is_dir()], r.stdout + r.stderr


def test_gate_refuses_an_unresolvable_rev_and_a_missing_lane_file(tmp_path, probe):
    r = _run(tmp_path, "-r", "no-such-rev", "-f", probe, "-t", probe)
    assert r.returncode == 65 and "does not resolve" in r.stderr
    r = _run(tmp_path, "-r", "HEAD", "-f", "tests/no_such_file.py", "-t", probe)
    assert r.returncode == 67 and "absent in the working tree" in r.stderr


def test_gate_fails_when_a_run_is_red(tmp_path, probe):
    bad = tmp_path / "test_red_probe.py"; bad.write_text("def test_red():\n    assert 0\n")
    # a lane file outside the repo cannot be copied by relative path; point -f at a real file and -t at the red test's abs path
    r = _run(tmp_path, "-r", "HEAD", "-f", probe, "-t", str(bad), "-n", "1")
    assert r.returncode != 0
    result = [l for l in r.stdout.splitlines() if l.startswith("RESULT:")][-1]
    assert "rc=1" in result and "1 failed" in result, result
    assert [p for p in tmp_path.iterdir() if p.name.startswith("gate-") and p.is_dir()], "a red gate must keep its archive"
    # a red run NAMES its failing test inline and keeps the full pytest output beside the archive (2026-09-08: a
    # "1 failed, 113 passed" with no test name forced a blind re-run of a three-minute gate)
    assert "test_red" in r.stdout and "full output:" in r.stdout, r.stdout
    log = [l.split("full output: ", 1)[1].strip() for l in r.stdout.splitlines() if "full output:" in l][0]
    assert Path(log).is_file() and "test_red" in Path(log).read_text(), log


def test_gate_names_gitignored_files_under_the_lane_directories(tmp_path, probe):
    """AF-AP-62 (2026-09-08): 16 gitignored buzzacp.log files under S0-02's committed bundles never reached the git-view
    copy — the lane's own byte-copy gate was green, the coordinator's `39 failed`. The gate now NAMES ignored files under
    the lane's directories (informational: the run itself still grades the git view, so the red stays red)."""
    ignored = ROOT / Path(probe).parent / "ignored_probe.log"  # *.log is ignored at the repo root
    ignored.write_text("ignored\n")
    rel = ignored.relative_to(ROOT).as_posix()
    assert subprocess.run(["git", "check-ignore", "-q", rel], cwd=ROOT).returncode == 0, "*.log must be ignored"
    r = _run(tmp_path, "-r", "HEAD", "-f", probe, "-t", probe, "-n", "1")
    assert r.returncode == 0, r.stdout + r.stderr
    warn = [l for l in r.stdout.splitlines() if l.startswith("lane_gate: WARNING")]
    assert len(warn) == 1 and "gitignored file(s) under the lane's directories" in warn[0], r.stdout
    assert rel in r.stdout, r.stdout


def test_committed_evidence_and_fixture_logs_are_not_gitignored():
    """AF-AP-62 (2026-09-08) and VERIFY-B1 F4: a proof's committed bundles AND its real evidence root carry the log
    files its checker requires (S0-02: buzzacp.log in every leg); the root `*.log` rule must not swallow either.
    The control proves the rule still ignores an ordinary log."""
    def ignored(path):
        return subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT).returncode == 0
    assert not ignored("proofs/S0-02/fixtures/evidence-pass/legs/pos-allowed/buzzacp.log")
    assert not ignored("proofs/S0-02/evidence/pos-allowed/buzzacp.log")
    assert not ignored("proofs/S0-99/evidence/any-leg/anything.log")
    assert ignored("tests/lane_gate_ignored_probe.log"), "the control: an ordinary log must still be ignored"


def test_a_declared_deletion_is_removed_from_the_archive_copy(tmp_path, probe):
    """-d: a file the lane DELETED (present at the rev, absent from its working tree) is removed from the archive copy, so
    the gate runs on the tree the lane means. 2026-09-08, lane O2: four stale fixture files it removed could not be
    represented — `-f` refused them (rc 67) and omitting them kept the stale bytes (`33 failed`)."""
    victim = "tests/test_lane_gate.py"  # tracked at HEAD, not in the -t set; deleted from the ARCHIVE COPY only
    assert (ROOT / victim).is_file()
    env = dict(os.environ, LANE_GATE_DIR=str(tmp_path), LANE_GATE_KEEP="1")
    r = subprocess.run(["bash", str(ROOT / "scripts/lane_gate.sh"), "-r", "HEAD", "-f", probe, "-t", probe, "-n", "1",
                        "-d", victim], cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout + r.stderr
    assert any(l.startswith("DELETED  " + victim) for l in r.stdout.splitlines()), r.stdout
    gate = [p for p in tmp_path.iterdir() if p.name.startswith("gate-") and p.is_dir()][0]
    assert not (gate / victim).exists(), "the deleted file is still in the archive copy"
    assert (ROOT / victim).is_file(), "the gate touched the working tree"
    result = [l for l in r.stdout.splitlines() if l.startswith("RESULT:")][-1]
    assert "deleted=1" in result and "3 passed" in result, result


def test_a_deletion_absent_at_the_rev_is_refused(tmp_path, probe):
    """NEGATIVE CONTROL: -d of a path the rev does not carry is a typo, not a no-op — rc 67, nothing gated."""
    r = _run(tmp_path, "-r", "HEAD", "-f", probe, "-t", probe, "-n", "1", "-d", "tests/no_such_file_ever.py")
    assert r.returncode == 67, r.stdout + r.stderr
    assert "not present at HEAD" in r.stderr
    assert not [l for l in r.stdout.splitlines() if l.startswith("RESULT:")]


def test_a_deletion_prunes_the_directory_it_empties(tmp_path, probe):
    """A checkout carries no empty directory, so a deleted file's emptied parent must go too (2026-09-08: S0-03's provenance
    test asserts `hermes/` is ABSENT after O2 deleted its four files — the first -d gate left the empty directory and read
    `1 failed, 215 passed` where the PC's git-applied patch read `216 passed`). The rev is a dangling commit built from
    HEAD's tree plus one synthetic file in its own directory — no ref, no working-tree change."""
    victim_dir = f"tests/.lane_gate_probe_gone_{uuid.uuid4().hex[:8]}"
    victim = f"{victim_dir}/only.txt"
    env = dict(os.environ, GIT_INDEX_FILE=str(tmp_path / "index"))
    subprocess.run(["git", "read-tree", "HEAD"], cwd=ROOT, env=env, check=True)
    blob = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=ROOT, input="gone\n", capture_output=True,
                          text=True, check=True).stdout.strip()
    subprocess.run(["git", "update-index", "--add", "--cacheinfo", f"100644,{blob},{victim}"], cwd=ROOT, env=env, check=True)
    tree = subprocess.run(["git", "write-tree"], cwd=ROOT, env=env, capture_output=True, text=True, check=True).stdout.strip()
    rev = subprocess.run(["git", "commit-tree", tree, "-p", "HEAD", "-m", "lane_gate probe: a file to delete"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.strip()
    env_keep = dict(os.environ, LANE_GATE_DIR=str(tmp_path), LANE_GATE_KEEP="1")
    r = subprocess.run(["bash", str(ROOT / "scripts/lane_gate.sh"), "-r", rev, "-f", probe, "-t", probe, "-n", "1",
                        "-d", victim], cwd=ROOT, env=env_keep, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout + r.stderr
    gate = [p for p in tmp_path.iterdir() if p.name.startswith("gate-") and p.is_dir()][0]
    assert not (gate / victim).exists()
    assert not (gate / victim_dir).exists(), "the emptied directory survived the deletion"
    assert (gate / "tests").is_dir(), "pruning must stop at a non-empty parent"

