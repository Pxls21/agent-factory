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


def test_real_tree_lists_every_checker_helper():
    """The four first-party helpers the checkers import are listed (the real-tree closure)."""
    listed = set((REPO_ROOT / "scripts" / "gate_files.txt").read_text().split())
    for helper in ("proofs/S0-01/pins.py", "proofs/S0-01/negative_contract.py",
                   "proofs/S0-01/tools/nostr_verify.py", "proofs/S0-02/oracle/denial_table.py"):
        assert helper in listed, helper
