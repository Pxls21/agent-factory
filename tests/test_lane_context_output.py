"""`scripts/lane_context.sh -o <path>` — the output path is a declared sink, never a fail-open.

QM1-b (2026-09-15): a `-o ../scratch/...` whose parent did not exist made the redirection fail, `emit` never ran, and the
wrapper still printed "pack written to … ( lines)" with rc 0 (AF-AP-86: a wrapper that reports an output it never wrote).
The wrapper now refuses a missing parent BEFORE emitting (rc 64, nothing written) and an EMPTY pack after (rc 64, the empty
file removed). The positive control runs the real instruments over one small file.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "lane_context.sh"
SMALL = "scripts/anchor_edit.py"


def _run(out: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(SCRIPT), "-q", "what does anchor_edit refuse", "-o", str(out), SMALL],
        cwd=ROOT, capture_output=True, text=True, timeout=600, check=False,
    )


def test_missing_output_parent_is_refused_before_anything_is_written(tmp_path: Path) -> None:
    out = tmp_path / "absent-parent" / "pack.md"
    result = _run(out)
    assert result.returncode == 64
    assert "output parent absent" in result.stderr
    assert "pack written" not in result.stdout
    assert not out.exists()
    assert not out.parent.exists()


def test_present_output_parent_writes_a_non_empty_pack(tmp_path: Path) -> None:
    out = tmp_path / "pack.md"
    result = _run(out)
    assert result.returncode == 0, result.stderr
    assert "pack written to" in result.stdout
    assert out.is_file() and out.stat().st_size > 0
