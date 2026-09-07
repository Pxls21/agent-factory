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


def test_report_lint_resolves_a_bare_basename_and_a_repo_path(tmp_path):
    (tmp_path / "pkg").mkdir()
    src = tmp_path / "pkg" / "thing.py"
    src.write_text("VALUE_ONE = 1\nVALUE_TWO = 2\n")
    rep = tmp_path / "report.md"
    rep.write_text("`VALUE_TWO` lives at thing.py:2 and pkg/thing.py:2; `VALUE_ONE` is not at thing.py:2\n")
    r = _run(rep, ["T=pkg/thing.py"], tmp_path)
    # three refs on one line share the line's claim tokens: VALUE_TWO matches at :2 for all three, so all OK
    assert "OK 3, NEAR 0, MISS 0" in r.stdout, r.stdout
