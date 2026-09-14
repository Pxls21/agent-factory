"""scripts/report_lint.py — the mechanical file:line check for lane/verify reports (AF-AP-37's class).

Every verdict since CK10 spent a blocker on typed line references; this makes the class a five-second check.
A synthetic file + a synthetic report: an OK ref, a NEAR ref (off by one), a MISS ref (points at a blank line),
an UNCHECKABLE ref (no claim token), and the exit code.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINT = ROOT / "scripts" / "report_lint.py"


def _run(report, maps, tmp_path):
    cmd = [sys.executable, str(LINT), str(report), "--root", str(tmp_path)] + [x for m in maps for x in ("--map", m)]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=60)


def test_report_lint_classifies_ok_near_miss_uncheckable(tmp_path):
    src = tmp_path / "mod.py"
    src.write_text("import os\n\ndef check_bundle(root, timeout_s=90):\n    pass\n\n\n_KNOWN_XFAIL_REASONS = frozenset()\n")
    rep = tmp_path / "report.md"
    rep.write_text(
        "| B4 | one default | C:3 `def check_bundle` |\n"          # OK: token on line 3
        "| B4b | signature | C:2 `def check_bundle` |\n"          # NEAR: line 2 is blank, line 3 has it
        "| B1 | the anchor | C:5 `_KNOWN_XFAIL_REASONS` |\n"      # MISS: line 5 blank, token at line 7 (tolerance 1)
        "| B9 | see C:4 for the body |\n"                          # UNCHECKABLE: no claim token
    )
    r = _run(rep, ["C=mod.py"], tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "report_lint: 4 refs — OK 1, NEAR 1, MISS 1, UNCHECKABLE 1, UNRESOLVED 0 (worktree)" in r.stdout, r.stdout
    assert "MISS         report:3     C:5" in r.stdout


def test_report_lint_exit_zero_when_no_miss(tmp_path):
    src = tmp_path / "mod.py"
    src.write_text("def alpha_beta():\n    return 1\n")
    rep = tmp_path / "report.md"
    rep.write_text("`def alpha_beta` at C:1\n")
    r = _run(rep, ["C=mod.py"], tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "OK 1, NEAR 0, MISS 0" in r.stdout


def test_report_lint_min_refs_floor_fails_a_report_that_cites_nothing(tmp_path):
    """The hollow lint (2026-09-14): B3's report lints `0 refs — OK 0, MISS 0` at its PIN because it cites NOTHING
    machine-checkable, and `MISS 0` alone reads as clean. `--min-refs N` makes the floor a gate: rc 1 with the FLOOR
    line when fewer than N refs resolve OK; without the flag the old contract holds (the negative control)."""
    src = tmp_path / "mod.py"
    src.write_text("def alpha_beta():\n    return 1\n\n\ndef gamma_delta():\n    return 2\n")
    empty = tmp_path / "empty.md"
    empty.write_text("The closure is containment (line ~120); the receipt is typed (line 651-vicinity).\n")
    r = _run(empty, ["C=mod.py"], tmp_path)
    assert r.returncode == 0 and "0 refs — OK 0, NEAR 0, MISS 0" in r.stdout, r.stdout      # the old contract: clean over nothing
    r = subprocess.run([sys.executable, str(LINT), str(empty), "--root", str(tmp_path), "--map", "C=mod.py",
                        "--min-refs", "1"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "report_lint: FLOOR — OK 0 < --min-refs 1" in r.stdout, r.stdout
    two = tmp_path / "two.md"
    two.write_text("`def alpha_beta` at C:1; `def gamma_delta` at C:5\n")
    for floor, rc in (("2", 0), ("3", 1)):
        r = subprocess.run([sys.executable, str(LINT), str(two), "--root", str(tmp_path), "--map", "C=mod.py",
                            "--min-refs", floor], capture_output=True, text=True, timeout=60)
        assert r.returncode == rc, (floor, r.stdout + r.stderr)
        assert "OK 2, NEAR 0, MISS 0" in r.stdout, r.stdout
        assert ("FLOOR — OK 2 < --min-refs 3" in r.stdout) == (rc == 1), r.stdout


def test_report_lint_resolves_a_bare_basename_and_a_repo_path(tmp_path):
    (tmp_path / "pkg").mkdir()
    src = tmp_path / "pkg" / "thing.py"
    src.write_text("VALUE_ONE = 1\nVALUE_TWO = 2\n")
    rep = tmp_path / "report.md"
    rep.write_text("`VALUE_TWO` lives at thing.py:2 and pkg/thing.py:2; `VALUE_ONE` is not at thing.py:2\n")
    r = _run(rep, ["T=pkg/thing.py"], tmp_path)
    # three refs on one line share the line's claim tokens: VALUE_TWO matches at :2 for all three, so all OK
    assert "OK 3, NEAR 0, MISS 0" in r.stdout, r.stdout
