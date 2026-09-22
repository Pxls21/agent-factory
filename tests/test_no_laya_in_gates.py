"""Tests for the advisory-exclusion screen (scripts/no_laya_in_gates.py).

Each test is deterministic and LLM-free. The screen's contract:
  exit 0  = clean
  exit 3  = violation (<path>:<line>:<token>)
  exit 4  = completeness control (gate-file-unlisted / gate-file-missing)
  exit 64 = usage error
"""

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCREEN = str(REPO_ROOT / "scripts" / "no_laya_in_gates.py")
PY = sys.executable
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "decisions" / "gate_violation"


def _run(args, cwd=None, env=None):
    """Run the screen script and return the CompletedProcess."""
    return subprocess.run(
        [PY, SCREEN] + args,
        capture_output=True, text=True, cwd=cwd, env=env,
    )


# --- Helper: create a minimal fixture tree in tmp_path ---

def _make_tree(tmp_path, gate_files_txt, files):
    """Create a fixture tree under tmp_path.

    gate_files_txt: content of scripts/gate_files.txt
    files: dict {repo-relative-path: content}
    """
    gf = tmp_path / "scripts" / "gate_files.txt"
    gf.parent.mkdir(parents=True, exist_ok=True)
    gf.write_text(gate_files_txt)
    for path, content in files.items():
        fp = tmp_path / path
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)


# =========================================================================
# Tests
# =========================================================================


def test_live_tree_clean():
    """The screen over the real repo root exits 0 (no Laya vocabulary in gates)."""
    r = _run(["--root", str(REPO_ROOT)])
    assert r.returncode == 0, f"Expected exit 0, got {r.returncode}.\nstdout: {r.stdout}\nstderr: {r.stderr}"
    # The stderr diagnostic line reports the scanned file count
    assert "files scanned, clean" in r.stderr


def test_planted_violation_in_real_gate_path():
    """Fixture tree: scripts/hooks/pre-commit contains 'laya' -> exit 3."""
    r = _run(["--root", str(FIXTURE_ROOT)])
    assert r.returncode == 3, f"Expected exit 3, got {r.returncode}.\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "scripts/hooks/pre-commit:3:laya" in r.stdout


def test_planted_violation_stripped_is_clean(tmp_path):
    """Same tree shape but the token removed -> exit 0."""
    _make_tree(tmp_path, "scripts/hooks/pre-commit\n", {
        "scripts/hooks/pre-commit": "#!/bin/bash\n# clean fixture\necho clean\n",
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 0, f"Expected exit 0, got {r.returncode}.\nstdout: {r.stdout}\nstderr: {r.stderr}"


def test_unlisted_structural_match(tmp_path):
    """proofs/x/check_y.py not in list -> exit 4 gate-file-unlisted."""
    _make_tree(tmp_path, "scripts/hooks/pre-commit\n", {
        "scripts/hooks/pre-commit": "#!/bin/bash\necho ok\n",
        "proofs/x/check_y.py": "# a check script\n",
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"Expected exit 4, got {r.returncode}.\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "gate-file-unlisted: proofs/x/check_y.py" in r.stderr


def test_identifier_boundary(tmp_path):
    """'receives' and 'laya_probe' do NOT fire; 'Laya' fires."""
    # First: file with non-matching tokens -> exit 0
    _make_tree(tmp_path, "scripts/hooks/pre-commit\n", {
        "scripts/hooks/pre-commit": "#!/bin/bash\n# receives data and laya_probe runs\necho ok\n",
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 0, (
        f"Expected exit 0 (receives/laya_probe should not fire), got {r.returncode}.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )

    # Second: file with case-insensitive match -> exit 3
    (tmp_path / "scripts" / "hooks" / "pre-commit").write_text(
        "#!/bin/bash\n# Laya reference here\necho ok\n"
    )
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 3, f"Expected exit 3, got {r.returncode}.\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert ":laya" in r.stdout


def test_import_check(tmp_path):
    """A .py file with 'from agent_factory.decisions import ledger' -> exit 3."""
    _make_tree(tmp_path, "scripts/gate_check.py\n", {
        "scripts/gate_check.py": (
            "#!/usr/bin/env python3\n"
            "from agent_factory.decisions import ledger\n"
            "print(ledger)\n"
        ),
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 3, f"Expected exit 3, got {r.returncode}.\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "agent_factory.decisions" in r.stdout


def test_no_bypass(tmp_path):
    """SKIP_LAYA_GATE_CHECK=1 and SKIP_ALL=1 do NOT bypass the screen."""
    _make_tree(tmp_path, "scripts/hooks/pre-commit\n", {
        "scripts/hooks/pre-commit": "#!/bin/bash\n# planted laya token\necho done\n",
    })
    env = os.environ.copy()
    env["SKIP_LAYA_GATE_CHECK"] = "1"
    env["SKIP_ALL"] = "1"
    r = _run(["--root", str(tmp_path)], env=env)
    assert r.returncode == 3, (
        f"Expected exit 3 despite bypass env vars, got {r.returncode}.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )


def test_staged_mode(tmp_path):
    """--staged reads the index, not the worktree."""
    # Set up a throwaway git repo
    hooks_dir = tmp_path / "scripts" / "hooks"
    hooks_dir.mkdir(parents=True)
    gf = tmp_path / "scripts" / "gate_files.txt"
    gf.write_text("scripts/hooks/pre-commit\n")
    hook = hooks_dir / "pre-commit"
    hook.write_text("#!/bin/bash\necho clean\n")

    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "test"
    env["GIT_AUTHOR_EMAIL"] = "test@test"
    env["GIT_COMMITTER_NAME"] = "test"
    env["GIT_COMMITTER_EMAIL"] = "test@test"

    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True, env=env)
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=True, env=env)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-gpg-sign"],
        cwd=tmp_path, capture_output=True, check=True, env=env,
    )

    # Case 1: staged content clean, worktree has violation -> --staged exits 0
    hook.write_text("#!/bin/bash\necho laya here\n")
    # Do NOT stage the change
    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 0, (
        f"Staged mode should read index (clean), got rc={r.returncode}.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )

    # Case 2: stage the violation, make worktree clean -> --staged exits 3
    subprocess.run(["git", "add", "scripts/hooks/pre-commit"], cwd=tmp_path, capture_output=True, check=True, env=env)
    hook.write_text("#!/bin/bash\necho clean\n")
    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 3, (
        f"Staged mode should read index (violation), got rc={r.returncode}.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )


def test_precommit_wired():
    """scripts/hooks/pre-commit contains the screen block and no SKIP_.*LAYA."""
    hook_path = REPO_ROOT / "scripts" / "hooks" / "pre-commit"
    content = hook_path.read_text()
    assert "no_laya_in_gates" in content, "The screen is not wired into pre-commit"
    # No bypass variable for the laya screen
    import re
    assert not re.search(r"SKIP_.*LAYA", content), (
        "pre-commit contains a SKIP variable for the laya screen"
    )
