"""Tests for scripts/owner_rulings.py: the owner's rulings that match a topic, newest first (orchestration 0l)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "owner_rulings.py"

LOG = """# Decision log

| ID | Decision |
|---|---|
| D-078 | OWNER RULINGS 2026-09-24 15:1xZ: LAYA TRAINING RUNS ON THE GPU; a training window needs NO lanes running. |
| D-080 | COORDINATOR RULING 2026-09-24 17:1xZ: the GPU budget heuristic stays. |
| D-081 | OWNER RULING 2026-09-24 17:2xZ: "Yes add test to gpu". The probe runs inside the same no-lanes GPU window. |
| D-087 | OWNER DIRECTION 2026-09-25 04:5xZ: our workflow is the factory's test bed. |
"""


def run(tmp_path, *args):
    log = tmp_path / "log.md"
    log.write_text(LOG, encoding="utf-8")
    return subprocess.run([sys.executable, str(SCRIPT), "--log", str(log), *args], capture_output=True, text=True, timeout=30)


def test_any_word_matches_owner_rows_newest_first(tmp_path):
    p = run(tmp_path, "gpu")
    assert p.returncode == 0
    ids = [line.split(":")[0] for line in p.stdout.splitlines() if line.startswith("D-")]
    assert ids == ["D-081", "D-078"]          # newest first; D-080 names the GPU but is not the owner's


def test_all_words_must_appear(tmp_path):
    p = run(tmp_path, "--all", "gpu", "window")
    ids = [line.split(":")[0] for line in p.stdout.splitlines() if line.startswith("D-")]
    assert ids == ["D-081", "D-078"]
    p = run(tmp_path, "--all", "gpu", "factory")
    assert p.returncode == 1 and "0 owner row(s)" in p.stdout


def test_no_match_exits_1_and_a_missing_log_exits_2(tmp_path):
    assert run(tmp_path, "zebra").returncode == 1
    p = subprocess.run([sys.executable, str(SCRIPT), "--log", str(tmp_path / "absent.md"), "gpu"],
                       capture_output=True, text=True, timeout=30)
    assert p.returncode == 2 and "cannot read" in p.stderr


def test_the_real_log_answers_the_gpu_question():
    # The question asked at 04:3xZ on 2026-09-25 ("may I test it beside vLLM in a GPU window?") had an answer in the log.
    p = subprocess.run([sys.executable, str(SCRIPT), "--all", "gpu", "test"], capture_output=True, text=True, timeout=30)
    assert p.returncode == 0
    assert any(line.startswith("D-081:") for line in p.stdout.splitlines())
