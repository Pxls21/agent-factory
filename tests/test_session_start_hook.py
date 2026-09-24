"""`.claude/hooks/session-start.sh`: what reaches the model at a session start or a compaction (VERIFY-COORD-0924 F-L1-3).

The harness swaps any hook text over 10,000 characters for a 2 KB preview of its head. The hook used to print setup's
whole output first (18,836 characters at the 2026-09-24 11:24Z compaction), so the live-state after it never reached the
model. Now setup goes to a log, its problem lines are shown, and the live-state's newest block follows.
The fixture runs copies of the hook and of wiki-context.py inside a temp tree with a noisy fake setup and orientation.
"""
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOKS = ROOT / ".claude" / "hooks"
LIMIT = 10000

LIVE_STATE = """# Live State

## Active lanes

**2026-09-24 12:3xZ — WHAT IS LIVE NOW (newest).**
- **LIVE:** the newest lane NEWESTMARK.

**2026-09-24 11:0xZ — WHAT IS LIVE NOW (older).**
- **LIVE:** an older lane OLDERMARK.
"""

SETUP = """#!/bin/bash
for i in $(seq 1 400); do printf '  \\033[1;32m✓\\033[0m installed optional tool number %s with a long line of noise\\n' "$i"; done
printf '  \\033[1;33m!\\033[0m fake optional install FAILEDMARK\\n'
exit 1
"""

ORIENT = """#!/bin/bash
for i in $(seq 1 200); do echo "orient line $i ── with a multibyte rule and some padding text"; done
"""


def _tree(tmp_path, live_state=LIVE_STATE):
    (tmp_path / ".claude" / "hooks").mkdir(parents=True)
    for name in ("session-start.sh", "wiki-context.py"):
        shutil.copy(HOOKS / name, tmp_path / ".claude" / "hooks" / name)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "setup.sh").write_text(SETUP)
    (tmp_path / "scripts" / "orient.sh").write_text(ORIENT)
    (tmp_path / "scripts" / "orient.sh").chmod(0o755)
    (tmp_path / "wiki" / "topics").mkdir(parents=True)
    (tmp_path / "wiki" / "topics" / "live-state.md").write_text(live_state)
    return tmp_path


def _run(tree, remote="true"):
    env = {"PATH": os.environ["PATH"], "CLAUDE_CODE_REMOTE": remote, "CLAUDE_PROJECT_DIR": str(tree),
           "AF_SETUP_LOG": str(tree / "setup.log")}
    r = subprocess.run(["bash", str(tree / ".claude" / "hooks" / "session-start.sh")], capture_output=True,
                       timeout=120, env=env, cwd=str(tree))
    return r.returncode, r.stdout.decode("utf-8")  # strict: a cut inside a UTF-8 sequence fails here


def test_the_output_fits_the_harness_limit_and_carries_the_newest_block(tmp_path):
    tree = _tree(tmp_path)
    rc, out = _run(tree)
    assert rc == 0
    assert len(out) < 9000 < LIMIT, len(out)
    assert "NEWESTMARK" in out and "OLDERMARK" not in out
    assert out.index("NEWESTMARK") < 2000  # the live-state sits near the top, inside any 2 KB preview


def test_setup_goes_to_the_log_and_only_its_problems_are_shown(tmp_path):
    tree = _tree(tmp_path)
    rc, out = _run(tree)
    assert "FAILEDMARK" in out and "rc 1" in out
    assert "installed optional tool number" not in out
    log = (tree / "setup.log").read_text()
    assert log.count("installed optional tool number") == 400 and "FAILEDMARK" in log


def test_the_real_live_state_page_fits(tmp_path):
    tree = _tree(tmp_path, (ROOT / "wiki" / "topics" / "live-state.md").read_text())
    rc, out = _run(tree)
    assert rc == 0 and len(out) < 9000, len(out)
    newest = next(line for line in (ROOT / "wiki" / "topics" / "live-state.md").read_text().splitlines()
                  if line.startswith("**20"))
    assert newest[:60] in out


def test_outside_the_web_container_it_does_nothing(tmp_path):
    tree = _tree(tmp_path)
    rc, out = _run(tree, remote="false")
    assert (rc, out) == (0, "") and not (tree / "setup.log").exists()
