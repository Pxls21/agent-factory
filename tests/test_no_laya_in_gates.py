"""Tests for the advisory-exclusion screen (scripts/no_laya_in_gates.py).

Each test is deterministic and LLM-free. The screen's contract:
  exit 0  = clean
  exit 3  = violation (<path>:<line>:<token>)
  exit 4  = completeness control (gate-file-unlisted / gate-file-missing)
  exit 64 = usage error
"""

import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

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


# --- Helper: set up git env for throwaway repos ---

def _git_env():
    """Return an env dict suitable for git operations in throwaway repos."""
    env = os.environ.copy()
    env["GIT_AUTHOR_NAME"] = "test"
    env["GIT_AUTHOR_EMAIL"] = "test@test"
    env["GIT_COMMITTER_NAME"] = "test"
    env["GIT_COMMITTER_EMAIL"] = "test@test"
    return env


def _init_repo(tmp_path, gate_files_txt, files, env):
    """Create a fixture tree, git init, add all, commit."""
    gf = tmp_path / "scripts" / "gate_files.txt"
    gf.parent.mkdir(parents=True, exist_ok=True)
    gf.write_text(gate_files_txt)
    for path, content in files.items():
        fp = tmp_path / path
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True, env=env)
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=True, env=env)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-gpg-sign"],
        cwd=tmp_path, capture_output=True, check=True, env=env,
    )


# =========================================================================
# B1/B2 regression tests (J1-0-R1)
# =========================================================================


def test_staged_renamed_gate_file_is_missing_not_clean(tmp_path):
    """B1: git mv a listed file + plant laya -> rc 4 gate-file-missing, not rc 0."""
    env = _git_env()
    _init_repo(tmp_path, "scripts/hooks/pre-commit\nscripts/report_lint.py\n", {
        "scripts/hooks/pre-commit": "#!/bin/bash\necho ok\n",
        "scripts/report_lint.py": "# clean\n",
    }, env)

    # Rename the listed file and plant the vocabulary in the new name
    subprocess.run(
        ["git", "mv", "scripts/report_lint.py", "scripts/report_lint_v2.py"],
        cwd=tmp_path, capture_output=True, check=True, env=env,
    )
    (tmp_path / "scripts" / "report_lint_v2.py").write_text("# laya token planted\n")
    subprocess.run(
        ["git", "add", "scripts/report_lint_v2.py"],
        cwd=tmp_path, capture_output=True, check=True, env=env,
    )

    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 4, (
        f"Expected exit 4 (gate-file-missing), got {r.returncode}.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "gate-file-missing: scripts/report_lint.py" in r.stderr


def test_staged_deleted_gate_file_is_missing(tmp_path):
    """B1: git rm a listed file -> rc 4 gate-file-missing."""
    env = _git_env()
    _init_repo(tmp_path, "scripts/hooks/pre-commit\nscripts/report_lint.py\n", {
        "scripts/hooks/pre-commit": "#!/bin/bash\necho ok\n",
        "scripts/report_lint.py": "# clean\n",
    }, env)

    subprocess.run(
        ["git", "rm", "scripts/report_lint.py"],
        cwd=tmp_path, capture_output=True, check=True, env=env,
    )

    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 4, (
        f"Expected exit 4 (gate-file-missing), got {r.returncode}.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "gate-file-missing: scripts/report_lint.py" in r.stderr


def test_staged_allowlist_is_read_from_index(tmp_path):
    """B2: unstaged deletion of allowlist line -> staged still reads the index's list."""
    env = _git_env()
    _init_repo(tmp_path, "scripts/hooks/pre-commit\nscripts/report_lint.py\n", {
        "scripts/hooks/pre-commit": "#!/bin/bash\necho ok\n",
        "scripts/report_lint.py": "# clean\n",
    }, env)

    # Stage a violation in scripts/report_lint.py
    (tmp_path / "scripts" / "report_lint.py").write_text("# laya token planted\n")
    subprocess.run(
        ["git", "add", "scripts/report_lint.py"],
        cwd=tmp_path, capture_output=True, check=True, env=env,
    )

    # Remove the report_lint.py line from the allowlist on disk (NOT staged)
    (tmp_path / "scripts" / "gate_files.txt").write_text("scripts/hooks/pre-commit\n")

    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 3, (
        f"Expected exit 3 (violation from index allowlist), got {r.returncode}.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "scripts/report_lint.py" in r.stdout


def test_staged_allowlist_absent_from_index_refused(tmp_path):
    """Allowlist absent from index (but present on disk) -> exit 64."""
    env = _git_env()
    hooks_dir = tmp_path / "scripts" / "hooks"
    hooks_dir.mkdir(parents=True)
    (hooks_dir / "pre-commit").write_text("#!/bin/bash\necho ok\n")

    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True, env=env)
    subprocess.run(
        ["git", "add", "scripts/hooks/pre-commit"],
        cwd=tmp_path, capture_output=True, check=True, env=env,
    )
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-gpg-sign"],
        cwd=tmp_path, capture_output=True, check=True, env=env,
    )

    # Create gate_files.txt on disk only (NOT in the index)
    gf = tmp_path / "scripts" / "gate_files.txt"
    gf.write_text("scripts/hooks/pre-commit\n")

    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 64, (
        f"Expected exit 64 (allowlist absent from index), got {r.returncode}.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "gate-file-missing:" in r.stderr


def test_scanned_count_equals_listed_count(tmp_path):
    """A listed file absent from the index cannot be silently skipped (count < list length)."""
    env = _git_env()
    _init_repo(tmp_path, "scripts/hooks/pre-commit\nscripts/report_lint.py\n", {
        "scripts/hooks/pre-commit": "#!/bin/bash\necho ok\n",
        "scripts/report_lint.py": "# clean\n",
    }, env)

    # Remove one file from the index only (keep it on disk and in the allowlist)
    subprocess.run(
        ["git", "rm", "--cached", "scripts/report_lint.py"],
        cwd=tmp_path, capture_output=True, check=True, env=env,
    )

    r = _run(["--staged"], cwd=tmp_path)
    # After fix: rc=4 (gate-file-missing). At the PIN: rc=0 with "1 files scanned, clean".
    assert r.returncode != 0, (
        f"Expected non-zero (missing file must not be silently skipped), got rc=0.\n"
        f"stderr: {r.stderr}"
    )


# =========================================================================
# R3 regression tests (J1-0-R2, contract AMENDMENT 1): a listed path must be a
# REGULAR file. `git show :<path>` returns a symlink's LINK TEXT, so a listed
# gate file replaced by a symlink to an unlisted laya-carrying file screened
# "clean" and committed (VERIFY-J1-0-R1 R3).
# =========================================================================


def test_staged_symlinked_gate_file_is_not_regular(tmp_path):
    """--staged: a listed path whose index entry is a symlink (120000) -> rc 4 by name."""
    env = _git_env()
    _init_repo(tmp_path, "scripts/hooks/pre-commit\nscripts/report_lint.py\n", {
        "scripts/hooks/pre-commit": "#!/bin/bash\necho ok\n",
        "scripts/report_lint.py": "# clean\n",
        "scripts/report_lint_impl.py": "# laya token planted\n",
    }, env)
    # Replace the listed file by a symlink to the unlisted, violating file and stage it.
    target = tmp_path / "scripts" / "report_lint.py"
    target.unlink()
    target.symlink_to("report_lint_impl.py")
    subprocess.run(["git", "add", "scripts/report_lint.py"], cwd=tmp_path, capture_output=True, check=True, env=env)
    mode = subprocess.run(["git", "ls-files", "--stage", "--", "scripts/report_lint.py"],
                          cwd=tmp_path, capture_output=True, text=True, check=True, env=env).stdout.split()[0]
    assert mode == "120000", mode  # the fixture really staged a symlink

    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 4, (
        f"Expected exit 4 (gate-file-not-regular), got {r.returncode}.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "gate-file-not-regular: scripts/report_lint.py mode=120000" in r.stderr
    assert "files scanned, clean" not in r.stderr


def test_worktree_symlinked_gate_file_is_not_regular(tmp_path):
    """--root: a listed path that is a symlink on disk -> rc 4 by name, even when its target is clean."""
    root = tmp_path / "tree"
    (root / "scripts" / "hooks").mkdir(parents=True)
    (root / "scripts" / "gate_files.txt").write_text("scripts/hooks/pre-commit\nscripts/report_lint.py\n")
    (root / "scripts" / "hooks" / "pre-commit").write_text("#!/bin/bash\necho ok\n")
    (root / "scripts" / "report_lint_impl.py").write_text("# clean target\n")
    (root / "scripts" / "report_lint.py").symlink_to("report_lint_impl.py")

    r = _run(["--root", str(root)])
    assert r.returncode == 4, (
        f"Expected exit 4 (gate-file-not-regular), got {r.returncode}.\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )
    assert "gate-file-not-regular: scripts/report_lint.py symlink" in r.stderr


def test_executable_regular_gate_file_stays_clean(tmp_path):
    """Positive control: a listed file at index mode 100755 is a regular file and screens clean."""
    env = _git_env()
    _init_repo(tmp_path, "scripts/hooks/pre-commit\nscripts/report_lint.py\n", {
        "scripts/hooks/pre-commit": "#!/bin/bash\necho ok\n",
        "scripts/report_lint.py": "#!/usr/bin/env python3\n# clean\n",
    }, env)
    (tmp_path / "scripts" / "report_lint.py").chmod(0o755)
    subprocess.run(["git", "add", "scripts/report_lint.py"], cwd=tmp_path, capture_output=True, check=True, env=env)
    mode = subprocess.run(["git", "ls-files", "--stage", "--", "scripts/report_lint.py"],
                          cwd=tmp_path, capture_output=True, text=True, check=True, env=env).stdout.split()[0]
    assert mode == "100755", mode

    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 0, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert "2 files scanned, clean" in r.stderr


# =========================================================================
# AMENDMENT 2 (J1-0-R3, AF-AP-120): the in-process include edges are closed
# =========================================================================

import importlib.util  # noqa: E402

_CHECKER = "proofs/x/check_y.py"


def _screen_module():
    spec = importlib.util.spec_from_file_location("no_laya_in_gates_mod", SCREEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _err_lines(r):
    return [line for line in r.stderr.splitlines() if line.startswith("gate-file-")]


def test_sourced_helper_refused(tmp_path):
    """A listed shell gate file that sources a file (line start, or mid-line after &&) -> exit 4,
    even though the sourced helper itself is not listed and carries banned vocabulary."""
    _make_tree(tmp_path, "scripts/hooks/pre-commit\n", {
        "scripts/hooks/pre-commit": (
            "#!/bin/bash\n"
            ". scripts/helper.sh\n"
            "[ -f x ] && source \"$ROOT/scripts/helper.sh\"\n"
        ),
        "scripts/helper.sh": "echo laya\n",
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == [
        "gate-file-sources: scripts/hooks/pre-commit:2: scripts/helper.sh",
        'gate-file-sources: scripts/hooks/pre-commit:3: "$ROOT/scripts/helper.sh"',
    ], r.stderr


def test_source_words_in_strings_comments_heredocs_not_flagged(tmp_path):
    """A '. word' inside a quoted string, a comment, a heredoc body or ${#var} is not a source."""
    _make_tree(tmp_path, "scripts/hooks/pre-commit\n", {
        "scripts/hooks/pre-commit": (
            "#!/bin/bash\n"
            "echo \"run setup (sandbox). Then retry\" >&2\n"
            "printf '(see docs). Next\\n'\n"
            "# . scripts/helper.sh would be refused\n"
            "n=${#ARR[@]}; echo \"$n\"\n"
            "cat <<'EOF'\n"
            ". scripts/helper.sh\n"
            "EOF\n"
            "echo done\n"
        ),
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 0, f"stdout: {r.stdout}\nstderr: {r.stderr}"


def test_allowed_source_pair_passes_only_for_its_file(tmp_path):
    """An ALLOWED_SOURCES pair passes in its own gate file and is refused in any other."""
    line = '[ -f "$ROOT/.pc-bridge.env" ] && . "$ROOT/.pc-bridge.env"\n'
    _make_tree(tmp_path, "scripts/pc_lane.sh\nscripts/hooks/pre-commit\n", {
        "scripts/pc_lane.sh": "#!/usr/bin/env bash\n" + line,
        "scripts/hooks/pre-commit": "#!/bin/bash\n" + line,
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == [
        'gate-file-sources: scripts/hooks/pre-commit:2: "$ROOT/.pc-bridge.env"',
    ], r.stderr


def test_yaml_parentheses_do_not_split_but_run_sources_are_refused(tmp_path):
    """YAML prose with '(x). Word' is not a source; a run step that sources a file is."""
    wf = ".github/workflows/ci.yml"
    _make_tree(tmp_path, wf + "\n", {
        wf: "name: ci\njobs:\n  t:\n    steps:\n      - name: Run tests (fast). Then report\n        run: echo ok\n",
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 0, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    (tmp_path / wf).write_text("name: ci\njobs:\n  t:\n    steps:\n      - run: . scripts/helper.sh\n")
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: %s:5: scripts/helper.sh" % wf], r.stderr


def test_unlisted_import_refused(tmp_path):
    """A listed checker importing an UNLISTED first-party helper -> exit 4 naming the helper."""
    _make_tree(tmp_path, _CHECKER + "\n", {
        _CHECKER: "import os\nimport helper\n",
        "proofs/x/helper.py": "X = 1\n",
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == [
        "gate-file-import-unlisted: proofs/x/check_y.py:2 imports helper -> proofs/x/helper.py",
    ], r.stderr


def test_listed_import_screened(tmp_path):
    """Once listed, the helper is screened: its vocabulary is an exit-3 violation."""
    _make_tree(tmp_path, _CHECKER + "\nproofs/x/helper.py\n", {
        _CHECKER: "import helper\n",
        "proofs/x/helper.py": "X = 1\n# a laya call would live here\n",
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 3, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert r.stdout.splitlines() == ["proofs/x/helper.py:2:laya"], r.stdout


def test_subdir_import_resolved(tmp_path):
    """A helper two levels deep is found (the checkers put tools/ and oracle/ on sys.path)."""
    _make_tree(tmp_path, _CHECKER + "\nproofs/x/tools/deep/helper2.py\n", {
        _CHECKER: "from helper2 import X\n",
        "proofs/x/tools/deep/helper2.py": "X = 1\n",
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 0, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert "2 files scanned, clean" in r.stderr


def test_unresolved_import_refused(tmp_path):
    """A non-stdlib, non-external name with no repo file -> exit 4 unresolved."""
    _make_tree(tmp_path, _CHECKER + "\n", {_CHECKER: "import json\nimport not_a_module_anywhere\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == [
        "gate-file-import-unresolved: proofs/x/check_y.py:2 imports not_a_module_anywhere",
    ], r.stderr


def test_ambiguous_import_refused(tmp_path):
    """Two repo files answer the same name -> exit 4 ambiguous, never the first match."""
    _make_tree(tmp_path, _CHECKER + "\nproofs/x/helper.py\nscripts/helper.py\n", {
        _CHECKER: "import helper\n",
        "proofs/x/helper.py": "X = 1\n",
        "scripts/helper.py": "X = 2\n",
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == [
        "gate-file-import-ambiguous: proofs/x/check_y.py:1 imports helper -> proofs/x/helper.py,scripts/helper.py",
    ], r.stderr


def test_stdlib_and_external_allowed(tmp_path):
    """Standard-library and EXTERNAL_MODULES imports need no repo file."""
    _make_tree(tmp_path, _CHECKER + "\n", {
        _CHECKER: "import os, json\nimport yaml\nfrom jsonschema import validate\nfrom __future__ import annotations\n",
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 0, f"stdout: {r.stdout}\nstderr: {r.stderr}"


def test_relative_import(tmp_path):
    """`from . import sibling` resolves against the importing file's own directory."""
    gate = "scripts/gatepkg/check.py"
    _make_tree(tmp_path, gate + "\n", {
        gate: "from . import sibling\n",
        "scripts/gatepkg/__init__.py": "",
        "scripts/gatepkg/sibling.py": "X = 1\n",
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == [
        "gate-file-import-unlisted: scripts/gatepkg/check.py:1 imports .sibling -> scripts/gatepkg/sibling.py",
    ], r.stderr


def test_python_shebang_gate_imports_checked(tmp_path):
    """An extensionless gate with a python shebang is a Python gate: its imports are closed too."""
    gate = "scripts/validate-thing"
    _make_tree(tmp_path, gate + "\n", {
        gate: "#!/usr/bin/env python3\nimport helper\n",
        "scripts/helper.py": "X = 1\n",
    })
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == [
        "gate-file-import-unlisted: scripts/validate-thing:2 imports helper -> scripts/helper.py",
    ], r.stderr


def test_unparseable_python_gate(tmp_path):
    """A listed Python gate that does not parse -> exit 4, never a silent pass."""
    _make_tree(tmp_path, _CHECKER + "\n", {_CHECKER: "def (\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-unparseable: proofs/x/check_y.py"], r.stderr


def test_staged_import_closure(tmp_path):
    """--staged resolves imports against the INDEX: a helper present only in the worktree is
    unresolved (not 'unlisted'), and an unlisting staged in the index is what counts."""
    env = _git_env()
    _init_repo(tmp_path, _CHECKER + "\nproofs/x/helper.py\n", {
        _CHECKER: "import helper\n",
        "proofs/x/helper.py": "X = 1\n",
    }, env)
    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 0, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    # The index unlists the helper; the worktree list still has it -> the index wins.
    gf = tmp_path / "scripts" / "gate_files.txt"
    gf.write_text(_CHECKER + "\n")
    subprocess.run(["git", "add", "scripts/gate_files.txt"], cwd=tmp_path, check=True, env=env)
    gf.write_text(_CHECKER + "\nproofs/x/helper.py\n")
    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == [
        "gate-file-import-unlisted: proofs/x/check_y.py:1 imports helper -> proofs/x/helper.py",
    ], r.stderr
    # A new import of a helper that exists only in the worktree is unresolved in the index.
    (tmp_path / _CHECKER).write_text("import helper\nimport wt_only\n")
    (tmp_path / "proofs" / "x" / "wt_only.py").write_text("Y = 2\n")
    subprocess.run(["git", "add", "scripts/gate_files.txt", _CHECKER], cwd=tmp_path, check=True, env=env)
    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == [
        "gate-file-import-unresolved: proofs/x/check_y.py:2 imports wt_only",
    ], r.stderr


def test_closed_sets_locked():
    """EXTERNAL_MODULES and ALLOWED_SOURCES are closed; widening either is a reviewed change."""
    mod = _screen_module()
    assert mod.EXTERNAL_MODULES == frozenset(["fubuki_os", "jsonschema", "lint", "pyflakes", "yaml"])
    assert mod.ALLOWED_SOURCES == frozenset([
        ("scripts/pc_lane.sh", '"$ROOT/.pc-bridge.env"'),
        ("scripts/pc_lane.sh", '"$PC_LANE_BRIDGE_FN"'),
    ])
    assert mod.ALLOWED_DYNAMIC_LOADS == {
        ("scripts/lint_delta.py", ".claude/hooks/edit-snapshot.py"): 1,
        ("scripts/proof-runner", "scripts/validate-ledger"): 1,
        ("scripts/ledger-gen", "scripts/validate-ledger"): 1,
    }


def test_real_tree_lists_every_checker_helper():
    """The four first-party helpers the checkers import are listed (the real-tree closure)."""
    listed = set((REPO_ROOT / "scripts" / "gate_files.txt").read_text().split())
    for helper in ("proofs/S0-01/pins.py", "proofs/S0-01/negative_contract.py",
                   "proofs/S0-01/tools/nostr_verify.py", "proofs/S0-02/oracle/denial_table.py"):
        assert helper in listed, helper


# =========================================================================
# AMENDMENT 3 (J1-0-R4; AF-AP-143, AF-AP-120 reopened): the scan never goes blind (R4-1..R4-3),
# and a dynamic in-process load is an include edge (R4-4, R4-5)
# =========================================================================

_HELPER = {"scripts/helper.sh": "echo HELPER-RAN laya\n"}
_GATE = "scripts/g.sh"
_WF = ".github/workflows/w.yml"


def _bash_runs_helper(root, *argv):
    """De-vacuous check: bash itself runs the fixture, and the fixture sources the helper."""
    r = subprocess.run(["bash", *argv], cwd=root, capture_output=True, text=True, timeout=60)
    return "HELPER-RAN" in r.stdout


def _workflow_runs(root, wf):
    """The run: values PyYAML reads from a workflow fixture, in document order."""
    import yaml
    found = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "run" and isinstance(value, str):
                    found.append(value)
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(yaml.safe_load((root / wf).read_text()))
    return found


# F-B1's shell member triggers (VERIFY-J1-0-R23-STAMP, B2): each read CLEAN at J1-0-R3 while bash ran the helper.
_SHELL_MEMBERS = [
    ("S12", "echo $'it\\'s'\n. scripts/helper.sh\n", 3),
    ("S17", "cat <<END-X\nbody\nEND-X\n. scripts/helper.sh\n", 5),   # = the verifier's proposed test 3
    ("S18", "cat <<\\EOF\nit's\nEOF\n. scripts/helper.sh\n", 5),
    ("S24", 'y=${x#"}"}\n. scripts/helper.sh\n', 3),
    ("S26", "z=$(( 1 << n ))\n. scripts/helper.sh\n", 3),
    ("S34", "echo x}#; . scripts/helper.sh\n", 2),
    ("S35", "m=\"$(printf '%s' \"it's\")\"\n. scripts/helper.sh\n", 3),
    ("S36", "y=${x:-'{'}; . scripts/helper.sh\n", 2),
    # beyond the B2 table: the arithmetic command, and a case pattern inside a quoted substitution
    ("arith-command", "(( m = 1 << n ))\n. scripts/helper.sh\n", 3),
    ("case-in-cmdsub", "r=\"$(case \"$1\" in a) echo \"it's\";; esac)\"\n. scripts/helper.sh\n", 3),
    # a source inside a backquote or a process substitution runs in the gate's forked shell (S6's class)
    ("backtick-source", "echo \"`. scripts/helper.sh`\"\n", 2),
    ("procsub-source", "cat <(. scripts/helper.sh)\n", 2),
]


@pytest.mark.parametrize("shape,body,line", _SHELL_MEMBERS, ids=[m[0] for m in _SHELL_MEMBERS])
def test_shell_member_trigger_is_caught(tmp_path, shape, body, line):
    """R4-2: after each trigger the scan stays in sync and names the source edge that follows it."""
    _make_tree(tmp_path, _GATE + "\n", dict(_HELPER, **{_GATE: "#!/bin/bash\n" + body}))
    assert _bash_runs_helper(tmp_path, _GATE), shape   # the fixture really sources the helper
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"{shape}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: %s:%d: scripts/helper.sh" % (_GATE, line)], r.stderr


# F-B1's workflow member triggers (B2: S39, S40, X3).
_YAML_MEMBERS = [
    # S39 = the verifier's proposed test 2 (YH-4's shape)
    ("S39", "jobs:\n  a:\n    steps:\n      - name: Install the suite's dependencies\n        run: echo ok\n"
            "      - run: . scripts/helper.sh\n", 6),
    ("S40", "jobs:\n  a:\n    steps:\n      - run: |\n          cat <<EOF\n          body\n          EOF\n"
            "      - run: . scripts/helper.sh\n", 8),
    ("X3", "jobs:\n  a:\n    steps:\n      - {name: a, run: . scripts/helper.sh}\n", 4),
]


@pytest.mark.parametrize("shape,text,line", _YAML_MEMBERS, ids=[m[0] for m in _YAML_MEMBERS])
def test_workflow_member_trigger_is_caught(tmp_path, shape, text, line):
    """R4-3: a workflow is parsed and each run: value is its own shell text, refused at its own YAML line."""
    _make_tree(tmp_path, _WF + "\n", dict(_HELPER, **{_WF: text}))
    runs = _workflow_runs(tmp_path, _WF)
    assert runs[-1] == ". scripts/helper.sh" and _bash_runs_helper(tmp_path, "-c", runs[-1]), runs
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"{shape}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: %s:%d: scripts/helper.sh" % (_WF, line)], r.stderr


def test_nested_quote_heredoc_text_does_not_blind_the_scan(tmp_path):
    """F-B1's live mechanism (scripts/pc_lane.sh:292; the verifier's proposed test 1): <<'PY' inside the quoted
    argument of "$(bridge "…")" is text, not a heredoc, and the source edge after the construct is found."""
    gate = ('#!/bin/bash\nX="$(bridge "python3 - \\"\\$MP\\" <<\'PY\'\nprint(1)\nPY")" || true\n'
            ". scripts/helper.sh\n")
    _make_tree(tmp_path, _GATE + "\n", dict(_HELPER, **{_GATE: gate}))
    assert _bash_runs_helper(tmp_path, _GATE)
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: scripts/g.sh:5: scripts/helper.sh"], r.stderr


def test_heredoc_bodies_are_data_but_their_expansions_run(tmp_path):
    """R4-2: a `.` line in a heredoc body is data, quoted or not, and so is a $( … ) in a quoted body; an
    UNQUOTED body expands $( … ), so a source inside that substitution runs and is refused."""
    gate = ("#!/bin/bash\ncat <<EOF\n. scripts/helper.sh\nEOF\ncat <<'EOF'\n$(. scripts/helper.sh)\nEOF\n"
            "cat <<EOF\n$(. scripts/helper.sh)\nEOF\n")
    _make_tree(tmp_path, _GATE + "\n", dict(_HELPER, **{_GATE: gate}))
    assert _bash_runs_helper(tmp_path, _GATE)   # only line 9's substitution can print the marker
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: scripts/g.sh:9: scripts/helper.sh"], r.stderr


# R4-1's tripwire alone: the text ends with a construct open (none of these is a source edge).
_OPEN_AT_END = [
    ("dquote", 'echo "open\n. scripts/helper.sh\n', 'quote " open'),
    ("squote", "echo 'open\n. scripts/helper.sh\n", "quote ' open"),
    ("ansi", "echo $'open\n. scripts/helper.sh\n", "quote $' open"),
    ("heredoc", "cat <<EOF\nbody\n. scripts/helper.sh\n", "heredoc <<EOF pending"),
    ("cmdsub", "x=$(echo a\necho b\n", "$( unclosed"),
    ("param", "y=${x:-a\necho b\n", "${ unclosed"),
    ("arith", "z=$(( 1 + 2\necho b\n", "$(( unclosed"),
    ("backtick", "w=`echo a\necho b\n", "` unclosed"),
]


@pytest.mark.parametrize("shape,body,what", _OPEN_AT_END, ids=[m[0] for m in _OPEN_AT_END])
def test_scan_ending_inside_a_construct_fails_closed(tmp_path, shape, body, what):
    """R4-1: a text that ends inside an open construct is refused, naming the line the construct began on."""
    _make_tree(tmp_path, _GATE + "\n", dict(_HELPER, **{_GATE: "#!/bin/bash\necho ok\n" + body}))
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"{shape}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-unparseable: scripts/g.sh:3: " + what], r.stderr


def test_scan_ending_inside_a_construct_fails_closed_staged(tmp_path):
    """R4-1 in --staged mode: the index's text is what is scanned, and its open quote is refused."""
    env = _git_env()
    _init_repo(tmp_path, _GATE + "\n", {_GATE: "#!/bin/bash\necho ok\n"}, env)
    (tmp_path / _GATE).write_text("#!/bin/bash\necho ok\necho \"open\n")
    subprocess.run(["git", "add", _GATE], cwd=tmp_path, check=True, env=env)
    (tmp_path / _GATE).write_text("#!/bin/bash\necho ok\n")   # the worktree copy is clean
    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ['gate-file-unparseable: scripts/g.sh:3: quote " open'], r.stderr


def test_unparseable_workflow_refused(tmp_path):
    """R4-3: a workflow file that does not parse is refused whole."""
    _make_tree(tmp_path, _WF + "\n", {_WF: "jobs: [unclosed\n  - run: . scripts/helper.sh\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-unparseable: .github/workflows/w.yml"], r.stderr


def test_workflow_run_ending_inside_a_construct_names_its_yaml_line(tmp_path):
    """R4-1 inside R4-3: an open quote in a literal run: block is refused at its line in the YAML file."""
    text = "jobs:\n  a:\n    steps:\n      - run: echo ok\n      - run: |\n          echo start\n          echo \"open\n"
    _make_tree(tmp_path, _WF + "\n", {_WF: text})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ['gate-file-unparseable: .github/workflows/w.yml:7: quote " open'], r.stderr


def test_real_pc_lane_is_scanned_to_its_end(tmp_path):
    """BH-2: the real scripts/pc_lane.sh, copied at test time, with `. scripts/helper.sh` inserted after line
    400 (inside the 318 lines J1-0-R3 never scanned) is refused at line 401; the file alone reads clean."""
    real = (REPO_ROOT / "scripts" / "pc_lane.sh").read_text()
    _make_tree(tmp_path, "scripts/pc_lane.sh\n", dict(_HELPER, **{"scripts/pc_lane.sh": real}))
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 0, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    lines = real.split("\n")
    gate = tmp_path / "scripts" / "pc_lane.sh"
    gate.write_text("\n".join(lines[:400] + [". scripts/helper.sh"] + lines[400:]))
    assert subprocess.run(["bash", "-n", str(gate)]).returncode == 0
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: scripts/pc_lane.sh:401: scripts/helper.sh"], r.stderr


def _stage0_ci_with_a_sourcing_step(apostrophe):
    """The real stage0-ci.yml plus a step that sources the helper, after the Run tests step; with or without
    one apostrophe in an earlier step name. Returns the text and the new run: line (1-based)."""
    lines = (REPO_ROOT / ".github" / "workflows" / "stage0-ci.yml").read_text().split("\n")
    name_at = lines.index("      - name: Install dependencies")
    run_at = lines.index("        run: python -m pytest tests/ -q")
    assert name_at < run_at
    if apostrophe:
        lines[name_at] = "      - name: Install the suite's dependencies"
    lines[run_at + 1:run_at + 1] = ["      - name: Load helper", "        run: . scripts/helper.sh"]
    return "\n".join(lines), run_at + 3


@pytest.mark.parametrize("apostrophe", [False, True], ids=["YH-3", "YH-4"])
def test_real_workflow_step_that_sources_is_refused(tmp_path, apostrophe):
    """YH-3 / YH-4: the real stage0-ci.yml, copied at test time, with a sourcing step; one apostrophe in an
    earlier step name no longer hides it."""
    wf = ".github/workflows/stage0-ci.yml"
    text, line = _stage0_ci_with_a_sourcing_step(apostrophe)
    _make_tree(tmp_path, wf + "\n", dict(_HELPER, **{wf: text}))
    assert ". scripts/helper.sh" in _workflow_runs(tmp_path, wf)
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: %s:%d: scripts/helper.sh" % (wf, line)], r.stderr


_LOADER_HEAD = "import importlib.util\nfrom pathlib import Path\n\nHERE = Path(__file__).resolve().parent\n"


def test_dynamic_import_of_an_unlisted_file_is_refused(tmp_path):
    """F-B2's code path (the verifier's proposed test 4, P09): spec_from_file_location + exec_module of an
    unlisted repo file is an include edge."""
    _make_tree(tmp_path, _CHECKER + "\n", {
        _CHECKER: "import importlib.util\nspec = importlib.util.spec_from_file_location('h', 'proofs/x/helper.py')\n"
                  "m = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(m)\n",
        "proofs/x/helper.py": "X = 1\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-import-unlisted: proofs/x/check_y.py:2 loads proofs/x/helper.py"], r.stderr


def test_real_tree_lists_the_dynamically_loaded_helper():
    """R4-5 (the verifier's proposed test 5): scripts/lint_delta.py and scripts/ap_screen.py load this hook."""
    listed = set((REPO_ROOT / "scripts" / "gate_files.txt").read_text().split())
    assert ".claude/hooks/edit-snapshot.py" in listed


def test_dynamic_load_is_closed_over_the_list(tmp_path):
    """R4-4: a Path(__file__)-built target that is unlisted is refused; listed, the helper is screened (its
    vocabulary is an exit-3 violation); clean, the tree passes."""
    checker = _LOADER_HEAD + 'spec = importlib.util.spec_from_file_location("helper", HERE / "helper.py")\n'
    _make_tree(tmp_path, _CHECKER + "\n", {_CHECKER: checker, "proofs/x/helper.py": "X = 1\n# laya\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-import-unlisted: proofs/x/check_y.py:5 loads proofs/x/helper.py"], r.stderr
    (tmp_path / "scripts" / "gate_files.txt").write_text(_CHECKER + "\nproofs/x/helper.py\n")
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 3 and r.stdout.splitlines() == ["proofs/x/helper.py:2:laya"], r.stdout + r.stderr
    (tmp_path / "proofs" / "x" / "helper.py").write_text("X = 1\n")
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 0 and "2 files scanned, clean" in r.stderr, r.stderr


def test_dynamic_load_that_cannot_be_resolved_is_refused(tmp_path):
    """R4-4: a load whose target is a runtime value cannot be proven, so it is refused."""
    _make_tree(tmp_path, _CHECKER + "\n", {_CHECKER: "import runpy\nimport sys\nrunpy.run_path(sys.argv[1])\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-import-unresolved: proofs/x/check_y.py:3"], r.stderr


_UNLISTED_LOADS = [
    ("SourceFileLoader", "import importlib.machinery\nimportlib.machinery.SourceFileLoader('h', 'proofs/x/helper.py')\n"),
    ("run_path", "import runpy\nrunpy.run_path('proofs/x/helper.py')\n"),
    ("import_module", "import importlib\nimportlib.import_module('helper')\n"),
    ("__import__", "import os\n__import__('helper')\n"),
    ("exec-open-read", "import os\nexec(open('proofs/x/helper.py').read())\n"),
    ("compile-read_text", "from pathlib import Path\ncompile(Path('proofs/x/helper.py').read_text(), 'h', 'exec')\n"),
    ("aliased", "from importlib.util import spec_from_file_location as load\nload('h', 'proofs/x/helper.py')\n"),
]


@pytest.mark.parametrize("kind,checker", _UNLISTED_LOADS, ids=[k for k, _ in _UNLISTED_LOADS])
def test_every_loader_kind_is_an_include_edge(tmp_path, kind, checker):
    """R4-4: each call that loads a file's code into the gate's process names what it loads; unlisted, refused."""
    _make_tree(tmp_path, _CHECKER + "\n", {_CHECKER: checker, "proofs/x/helper.py": "X = 1\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"{kind}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-import-unlisted: proofs/x/check_y.py:2 loads proofs/x/helper.py"], r.stderr


def test_loads_that_bring_no_repo_code_pass(tmp_path):
    """R4-4's positive controls: a stdlib module by name, and code written in the gate itself."""
    checker = "import importlib\nimportlib.import_module('json')\n__import__('os.path')\nexec('X = 1')\ncompile('Y = 2', 'y', 'exec')\n"
    _make_tree(tmp_path, _CHECKER + "\n", {_CHECKER: checker})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 0, f"stdout: {r.stdout}\nstderr: {r.stderr}"


def test_loader_parameter_is_resolved_at_its_calls(tmp_path):
    """R4-4: a loader wrapper's parameter takes the values its callers in the file pass (the S0-02 checker's
    _load_by_path shape): the unlisted one is refused at the load site; a wrapper that escapes as a value
    can be called with anything, so its load is unresolved."""
    checker = (_LOADER_HEAD + "\n\ndef _load_by_path(name, path):\n"
               "    spec = importlib.util.spec_from_file_location(name, path)\n    return spec\n\n\n"
               '_load_by_path("a", HERE / "listed.py")\n_load_by_path("b", HERE / "helper.py")\n')
    _make_tree(tmp_path, _CHECKER + "\nproofs/x/listed.py\n", {
        _CHECKER: checker, "proofs/x/listed.py": "X = 1\n", "proofs/x/helper.py": "X = 2\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-import-unlisted: proofs/x/check_y.py:8 loads proofs/x/helper.py"], r.stderr
    (tmp_path / _CHECKER).write_text(checker.replace('_load_by_path("b", HERE / "helper.py")', "LOADERS = [_load_by_path]"))
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-import-unresolved: proofs/x/check_y.py:8"], r.stderr


_PROOF_RUNNER = ('#!/usr/bin/env python3\nimport importlib.machinery\nimport sys\nfrom pathlib import Path\n\n\n'
                 'def _load_validator(root):\n    path = root / "scripts" / "validate-ledger"\n'
                 '    return importlib.machinery.SourceFileLoader("v", str(path))\n\n\n'
                 '_load_validator(Path(sys.argv[1]))\n')


def test_allowed_dynamic_load_is_bounded_and_keyed_by_target(tmp_path):
    """R4-4's exception set: (scripts/proof-runner, scripts/validate-ledger) covers ONE load under a runtime
    root; a second such load refuses both, and a load re-pointed at another (even listed) file is not covered."""
    _make_tree(tmp_path, "scripts/proof-runner\nscripts/validate-ledger\nscripts/other.py\n", {
        "scripts/proof-runner": _PROOF_RUNNER,
        "scripts/validate-ledger": "#!/usr/bin/env python3\nX = 1\n",
        "scripts/other.py": "X = 1\n"})
    runner = tmp_path / "scripts" / "proof-runner"
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 0, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    runner.write_text(_PROOF_RUNNER.replace(
        "    return importlib", '    importlib.machinery.SourceFileLoader("w", str(path))\n    return importlib'))
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-import-unresolved: scripts/proof-runner:9",
                             "gate-file-import-unresolved: scripts/proof-runner:10"], r.stderr
    runner.write_text(_PROOF_RUNNER.replace('"validate-ledger"', '"other.py"'))
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-import-unresolved: scripts/proof-runner:9"], r.stderr


def test_edit_snapshot_hook_load_is_an_include_edge(tmp_path):
    """ES (F-B2): the real scripts/ap_screen.py loads the real .claude/hooks/edit-snapshot.py in-process
    (both copied at test time). Unlisted, the load is refused; listed, a vocabulary line in the hook is an
    exit-3 violation naming its line."""
    ap = (REPO_ROOT / "scripts" / "ap_screen.py").read_text()
    hook = (REPO_ROOT / ".claude" / "hooks" / "edit-snapshot.py").read_text()
    site = next(n for n, text in enumerate(ap.split("\n"), 1) if "spec_from_file_location" in text)
    _make_tree(tmp_path, "scripts/ap_screen.py\n", {
        "scripts/ap_screen.py": ap, ".claude/hooks/edit-snapshot.py": hook + "# laya\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == [
        "gate-file-import-unlisted: scripts/ap_screen.py:%d loads .claude/hooks/edit-snapshot.py" % site], r.stderr
    (tmp_path / "scripts" / "gate_files.txt").write_text("scripts/ap_screen.py\n.claude/hooks/edit-snapshot.py\n")
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 3, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert r.stdout.splitlines() == [".claude/hooks/edit-snapshot.py:%d:laya" % (hook.count("\n") + 1)], r.stdout


def test_allowed_dynamic_loads_match_the_live_tree_exactly():
    """Each ALLOWED_DYNAMIC_LOADS entry covers exactly its count of loads in the live gate file. The screen
    refuses more; this test refuses fewer, so a stale entry cannot wait for a new load to cover."""
    mod = _screen_module()
    for (gate, target), count in mod.ALLOWED_DYNAMIC_LOADS.items():
        sites = mod._load_sites(gate, ast.parse((REPO_ROOT / gate).read_text()))
        covered = [line for line, kind, values in sites if ("under", target) in values]
        assert len(covered) == count, (gate, target, covered)


def test_live_tree_clean_staged(tmp_path):
    """The live tree through --staged: every listed file and the list, added to a throwaway index, read clean
    with every listed file scanned (the index-side twin of test_live_tree_clean)."""
    listed = [line.strip() for line in (REPO_ROOT / "scripts" / "gate_files.txt").read_text().splitlines()
              if line.strip() and not line.strip().startswith("#")]
    for rel in listed + ["scripts/gate_files.txt"]:
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / rel, dst)
    env = _git_env()
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, env=env)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, env=env)
    r = _run(["--staged"], cwd=tmp_path)
    assert r.returncode == 0, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert "%d files scanned, clean" % len(listed) in r.stderr, r.stderr


# Found while building R4-4 (the J1-0-R4 report, "self-attack"): Python's own binding rules can re-point a
# load whose target reads as listed; each shape was a fail-open in a first draft of the resolver.
_REBOUND_TARGETS = [
    ("global-rebind", "T = HERE / 'listed.py'\n\n\ndef g():\n    global T\n    T = 'proofs/x/helper.py'\n\n\n"
                      "g()\nimportlib.util.spec_from_file_location('x', T)\n", 14),
    ("nonlocal-rebind", "def outer():\n    T = HERE / 'listed.py'\n\n    def inner():\n        nonlocal T\n"
                        "        T = 'proofs/x/helper.py'\n    inner()\n    importlib.util.spec_from_file_location('x', T)\n", 12),
    ("decorated-wrapper", "def deco(fn):\n    return lambda p: fn('proofs/x/helper.py')\n\n\n@deco\ndef load(p):\n"
                          "    return importlib.util.spec_from_file_location('x', p)\n\n\nload('proofs/x/listed.py')\n", 11),
    ("star-import", "T = HERE / 'listed.py'\nfrom os.path import *  # noqa\nimportlib.util.spec_from_file_location('x', T)\n", 7),
    ("shadowed-Path", "def Path(x):\n    return 'proofs/x/helper.py'\n\n\n"
                      "importlib.util.spec_from_file_location('x', Path('proofs/x/listed.py'))\n", 9),
]


@pytest.mark.parametrize("shape,body,line", _REBOUND_TARGETS, ids=[m[0] for m in _REBOUND_TARGETS])
def test_rebinding_a_load_target_is_refused(tmp_path, shape, body, line):
    """R4-4: a target name that a global, nonlocal, decorator, star import or shadowed helper can re-point
    cannot be proven listed, so the load is refused."""
    _make_tree(tmp_path, _CHECKER + "\nproofs/x/listed.py\n", {
        _CHECKER: _LOADER_HEAD + body, "proofs/x/listed.py": "X = 1\n", "proofs/x/helper.py": "X = 2\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"{shape}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-import-unresolved: proofs/x/check_y.py:%d" % line], r.stderr


_INLINE_LOADS = [
    ("exec-import", "exec('import helper')\n"),
    ("exec-loader", "exec(\"import runpy; runpy.run_path('proofs/x/helper.py')\")\n"),
    ("eval-dunder", "eval(\"__import__('helper')\")\n"),
    ("exec-constant", "CODE = 'import helper'\nexec(CODE)\n"),
]


@pytest.mark.parametrize("shape,body", _INLINE_LOADS, ids=[m[0] for m in _INLINE_LOADS])
def test_inline_code_that_loads_is_refused(tmp_path, shape, body):
    """R4-4: code written into the gate as a string is part of the gate only while it imports and loads
    nothing; otherwise exec/eval/compile of it is refused (the string hides the edge from the import rule)."""
    _make_tree(tmp_path, _CHECKER + "\n", {_CHECKER: "import os\n" + body, "proofs/x/helper.py": "X = 1\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"{shape}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-import-unresolved: proofs/x/check_y.py:%d" % (body.count("\n") + 1)], r.stderr


_MODELLING_EDGES = [
    # pathlib keeps a relative path relative: HERE / Path("a/b").parent is HERE/a, never the repo's a
    ("relative-parent", "importlib.util.spec_from_file_location('x', HERE / Path('proofs/x/listed.py/y').parent)\n",
     "gate-file-import-unresolved: proofs/x/check_y.py:5"),
    # an argument annotation runs when the function is defined
    ("annotation", "def f(a: exec(open('proofs/x/helper.py').read())):\n    pass\n",
     "gate-file-import-unlisted: proofs/x/check_y.py:5 loads proofs/x/helper.py"),
]


@pytest.mark.parametrize("shape,body,line", _MODELLING_EDGES, ids=[m[0] for m in _MODELLING_EDGES])
def test_path_modelling_edges_are_refused(tmp_path, shape, body, line):
    """R4-4: two more first-draft fail-opens (the J1-0-R4 report): a relative path joined as if it were the
    repo's, and a load inside an annotation."""
    _make_tree(tmp_path, _CHECKER + "\nproofs/x/listed.py\n", {
        _CHECKER: _LOADER_HEAD + body, "proofs/x/listed.py": "X = 1\n", "proofs/x/helper.py": "X = 2\n"})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"{shape}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == [line], r.stderr


# =========================================================================
# AMENDMENT 4 (J1-0-R5; VERIFY-J1-0-R4 V-01, V-04, V-06; AF-AP-153)
# =========================================================================

# V-01, an R4 regression: bash translates the ANSI-C escape of a $'…' heredoc word and ends the body at the
# translation (line 4); R4 kept the escape, ended the body at line 6 (the untranslated word), read the source edge
# on line 5 as body text and printed CLEAN, where R3 refused. R5-1 (b): such a word is refused at its own line.
_ANSI_C_WORDS = [
    # (shape, the heredoc word, the line where bash ends the body, the line where R4 ended it)
    ("AQ1", "$'echo \\x41'", "echo A", "echo \\x41"),
    ("AQ2", "$'E\\x4fF'", "EOF", "E\\x4fF"),
    ("AQ3", "$'E\\\\F'", "E\\F", "E\\\\F"),
    ("AQ4", "$'E\\'F'", "E'F", "E\\F"),
    ("PQ5b", "$'E\\tF'", "E\tF", "E\\tF"),
    ("mid-word", "E$'\\x4f'F", "EOF", "E\\x4fF"),
]


@pytest.mark.parametrize("shape,word,bash_end,r4_end", _ANSI_C_WORDS, ids=[m[0] for m in _ANSI_C_WORDS])
def test_heredoc_word_with_an_ansi_c_escape_is_refused(tmp_path, shape, word, bash_end, r4_end):
    """R5-1: bash ends the body on line 4 and runs the source edge on line 5; the word is refused on line 2."""
    gate = "#!/bin/bash\ncat <<%s >/dev/null\nbody\n%s\n. scripts/helper.sh\n%s\n" % (word, bash_end, r4_end)
    _make_tree(tmp_path, _GATE + "\n", dict(_HELPER, **{_GATE: gate}))
    assert _bash_runs_helper(tmp_path, _GATE), shape
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"{shape}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    want = "gate-file-unparseable: scripts/g.sh:2: heredoc <<%s: $'...' escape not translated" % word
    assert _err_lines(r) == [want], r.stderr


def test_heredoc_word_in_ansi_c_quotes_without_an_escape_still_reads(tmp_path):
    """R5-1 keeps <<$'EOF' (PQ7's class): with no backslash the word is EOF to bash and to the scan, the `.` line is
    body text to both, and the text reads clean."""
    gate = "#!/bin/bash\ncat <<$'EOF' >/dev/null\n. scripts/helper.sh\nEOF\necho done\n"
    _make_tree(tmp_path, _GATE + "\n", dict(_HELPER, **{_GATE: gate}))
    ran = subprocess.run(["bash", _GATE], cwd=tmp_path, capture_output=True, text=True, timeout=60)
    assert ran.stdout == "done\n", ran   # bash reaches the end and never runs the helper
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 0, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert "1 files scanned, clean" in r.stderr


# V-04, introduced by R4: a $(( that fails as arithmetic is re-scanned as commands, and R4 re-ran every inner attempt
# for each enclosing one, so k nested levels doubled k times (27.62 s at k=22 in the verify lane; the hook runs the
# screen on every commit). R5-2: the decision is made once per start.
_NESTED_ATTEMPTS = [
    ("V-04", "v=" + "$(( " * 22 + "x" + " ) )" * 22 + "\n. scripts/helper.sh\n", 3),
    # a <<W in each level is a shift in the attempt and a heredoc in the re-scan: a memo keyed by the pending
    # heredocs as well as the start would re-run every level once per state, 2^k again
    ("heredoc-per-level", "v=" + "".join("$(( <<W%d " % j for j in range(22)) + "x" + " ) )" * 22 + "\n"
     + "".join("W%d\n" % j for j in range(22)) + ". scripts/helper.sh\n", 25),
]


@pytest.mark.parametrize("shape,body,line", _NESTED_ATTEMPTS, ids=[m[0] for m in _NESTED_ATTEMPTS])
def test_nested_arithmetic_attempts_scan_in_bounded_time(tmp_path, shape, body, line):
    """R5-2: 22 nested failed attempts scan in under 5 s (R4: about 28 s), and the source edge after them is found."""
    _make_tree(tmp_path, _GATE + "\n", dict(_HELPER, **{_GATE: "#!/bin/bash\n" + body}))
    assert _bash_runs_helper(tmp_path, _GATE), shape
    try:
        r = subprocess.run([PY, SCREEN, "--root", str(tmp_path)], capture_output=True, text=True, timeout=5)
    except subprocess.TimeoutExpired:
        pytest.fail("%s: the scan of 22 nested $(( attempts took more than 5 s" % shape)
    assert r.returncode == 4, f"{shape}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: scripts/g.sh:%d: scripts/helper.sh" % line], r.stderr


# R5-2 changes no decision: an R4 arithmetic case and an R4 subshell case, each inside an enclosing attempt that
# fails, so the inner text is scanned twice and the memo is read on the second pass. The lines are R4's.
_MEMO_DECISIONS = [
    # `1 << 2` is a shift: no heredoc swallows line 3
    ("shift-in-subshell", "v=$(( $(( 1 << 2 )) ) )\n. scripts/helper.sh\n", 3),
    # an attempt that succeeds is re-scanned, so its $( … ) re-adds the edge the failed outer attempt deleted
    ("arith-in-subshell", "v=$(( $(( $(. scripts/helper.sh) + 1 )) ) )\n", 2),
    # a subshell: its body is commands in both passes
    ("subshell-in-subshell", "v=$(( $(( . scripts/helper.sh ) ) ) )\n", 2),
]


@pytest.mark.parametrize("shape,body,line", _MEMO_DECISIONS, ids=[m[0] for m in _MEMO_DECISIONS])
def test_arithmetic_memo_keeps_every_decision(tmp_path, shape, body, line):
    """R5-2: the memo keeps R4's verdict; bash sources the helper in each (a marker: $( … ) captures its output)."""
    helper = {"scripts/helper.sh": "echo HELPER-RAN laya\n: > helper.ran\n"}
    _make_tree(tmp_path, _GATE + "\n", dict(helper, **{_GATE: "#!/bin/bash\n" + body}))
    subprocess.run(["bash", _GATE], cwd=tmp_path, capture_output=True, timeout=60)
    assert (tmp_path / "helper.ran").exists(), shape
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"{shape}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: scripts/g.sh:%d: scripts/helper.sh" % line], r.stderr


# A failed attempt that read a heredoc body (a newline inside a nested $( … )) holds only under the heredocs it read.
# Revisited with others pending (<<A is a shift in the enclosing attempt and a heredoc in its re-scan), it is
# refused, never trusted and never re-run.
_MEMO_REFUSALS = [
    # bash runs the helper here; R4 named line 5
    ("bash-valid", "x=$(( <<A $(( $(:\nA\n) ) ) ) )\n. scripts/helper.sh\n", True),
    # bash rejects this one (a syntax error before line 6); R4 refused it at line 6, and a memo trusted under other
    # heredocs reads it CLEAN
    ("trusted-memo-reads-clean", "x=$(( <<A $(( $(:\n) ) ))\nA\n) <<B )) ) )\n. scripts/helper.sh\nB\n", False),
]


@pytest.mark.parametrize("shape,body,bash_runs", _MEMO_REFUSALS, ids=[m[0] for m in _MEMO_REFUSALS])
def test_arithmetic_memo_refuses_a_revisit_it_cannot_prove(tmp_path, shape, body, bash_runs):
    """R5-2 fails closed: the inner $(( on line 2 is refused there."""
    _make_tree(tmp_path, _GATE + "\n", dict(_HELPER, **{_GATE: "#!/bin/bash\n" + body}))
    assert _bash_runs_helper(tmp_path, _GATE) == bash_runs, shape
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"{shape}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-unparseable: scripts/g.sh:2: $(( re-read with other heredocs pending"], r.stderr


# V-06: a folded or quoted run: value folds or escapes its line breaks, so its own newlines are not lines of the
# file; R4 counted them from the value's first line (Y13 named the next step's line). R5-4: every refusal in such a
# value names the line the value starts on. Line 6 is the first step.
_WF_HEAD = "on: push\njobs:\n  a:\n    runs-on: ubuntu-latest\n    steps:\n"
_NON_LITERAL_RUNS = [
    # (shape, steps, the refusal line: the value's first line; R4 named 8, 8, 7, 7)
    ("Y2b", "      - run: >\n          echo a\n          echo b\n            . scripts/helper.sh\n", 7),
    ("Y2c", "      - run: >\n          echo a\n\n          . scripts/helper.sh\n", 7),
    ("Y13", '      - run: "echo a\\n. scripts/helper.sh"\n      - run: echo ok\n', 6),
    ("Y14", "      - run: 'echo a\n\n          . scripts/helper.sh'\n", 6),
    # D-MX6 (VERIFY-J1-0-R5 V5-08): a plain value over a blank line folds it to one break; read line for line it
    # would name 7
    ("MX6", "      - run: echo a\n\n          . scripts/helper.sh\n      - run: echo ok\n", 6),
]


@pytest.mark.parametrize("shape,steps,line", _NON_LITERAL_RUNS, ids=[m[0] for m in _NON_LITERAL_RUNS])
def test_folded_or_quoted_run_refusal_names_its_first_line(tmp_path, shape, steps, line):
    """R5-4: the refusal names a line inside the value (its first), never the next step's."""
    _make_tree(tmp_path, _WF + "\n", dict(_HELPER, **{_WF: _WF_HEAD + steps}))
    runs = _workflow_runs(tmp_path, _WF)
    assert _bash_runs_helper(tmp_path, "-c", runs[0]), runs   # the value a YAML consumer runs sources the helper
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"{shape}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: %s:%d: scripts/helper.sh" % (_WF, line)], r.stderr


def test_quoted_run_that_ends_open_names_its_first_line(tmp_path):
    """R5-4 for R4-1's refusal: a double-quoted value whose second line opens a quote is refused at the value's
    first line (R4 named line 7, the next step's)."""
    _make_tree(tmp_path, _WF + "\n", {_WF: _WF_HEAD + '      - run: "echo a\\necho \\"open"\n      - run: echo ok\n'})
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ['gate-file-unparseable: .github/workflows/w.yml:6: quote " open'], r.stderr


def test_literal_run_block_keeps_its_line_map(tmp_path):
    """R5-4 keeps a literal block (|) line for line (Y1): the source edge after a heredoc inside the block is refused
    at the YAML line that holds it."""
    steps = "      - run: |\n          cat <<EOF\n          body\n          EOF\n          . scripts/helper.sh\n"
    _make_tree(tmp_path, _WF + "\n", dict(_HELPER, **{_WF: _WF_HEAD + steps}))
    assert _bash_runs_helper(tmp_path, "-c", _workflow_runs(tmp_path, _WF)[0])
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: %s:10: scripts/helper.sh" % _WF], r.stderr


# V5-05 (VERIFY-J1-0-R5): PyYAML's node start mark is the node's first property (an &anchor or a !!tag), and the
# property can sit on the line above the scalar; R5 counted from it and named the indicator's or the key's line.
# R6 (AMENDMENT 5) counts from the scalar's own token. Line 6 is the first step.
_PROPERTY_RUNS = [
    # (shape, steps, the refusal line; R5 named 8, 7, 7, 6, 6)
    ("W10", "      - run: &x\n          |\n          echo a\n          . scripts/helper.sh\n", 9),
    ("W10b", "      - run: &x\n          |\n          . scripts/helper.sh\n", 8),
    ("W11", "      - run: !!str\n          >\n          echo a\n\n          . scripts/helper.sh\n", 8),
    ("W12", "      - run: &x\n          . scripts/helper.sh\n", 7),
    ("W12b", '      - run: !!str\n          ". scripts/helper.sh"\n', 7),
]


def test_empty_run_value_has_no_token_and_is_read_from_its_node(tmp_path):
    """R6: an empty run: value, bare or behind a property, has no scalar token; its line falls back to the node, the
    scan does not stop on it, and the next step's source edge is named at its own line."""
    steps = "      - run:\n      - run: &y\n      - run: . scripts/helper.sh\n"
    _make_tree(tmp_path, _WF + "\n", dict(_HELPER, **{_WF: _WF_HEAD + steps}))
    runs = _workflow_runs(tmp_path, _WF)
    assert runs == [". scripts/helper.sh"] and _bash_runs_helper(tmp_path, "-c", runs[0]), runs
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"stdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: %s:8: scripts/helper.sh" % _WF], r.stderr


@pytest.mark.parametrize("shape,steps,line", _PROPERTY_RUNS, ids=[m[0] for m in _PROPERTY_RUNS])
def test_run_value_behind_a_node_property_names_a_line_inside_it(tmp_path, shape, steps, line):
    """R6: a property on the line before the scalar moves no refusal out of the value; a literal block (W10, W10b)
    still names the helper's own line, any other style its first line."""
    _make_tree(tmp_path, _WF + "\n", dict(_HELPER, **{_WF: _WF_HEAD + steps}))
    runs = _workflow_runs(tmp_path, _WF)
    assert _bash_runs_helper(tmp_path, "-c", runs[0]), runs   # the value a YAML consumer runs sources the helper
    r = _run(["--root", str(tmp_path)])
    assert r.returncode == 4, f"{shape}\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert _err_lines(r) == ["gate-file-sources: %s:%d: scripts/helper.sh" % (_WF, line)], r.stderr
