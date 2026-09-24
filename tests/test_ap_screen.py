"""ap_screen.py — the whole-file registry screen: the two ways a signature reaches a line.

The hook screens multi-line HUNKS; the whole-file screen used to walk lines, so a signature spanning a line break
(a subprocess argv list wrapped after the paren — the AF-AP-60 shape) was invisible to it while the hook saw it.
The screen now runs each compiled pattern over the whole text and reports the line where the match starts; rows
whose matcher is a custom object exposing only search() (the hook's AST-backed rows) keep the per-line walk.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ap_screen  # noqa: E402


class _SearchOnly:
    """The hook's custom matcher shape: search() and nothing else."""

    def __init__(self, needle):
        self.needle = needle

    def search(self, text):
        return self.needle in text


def test_whole_text_scan_reports_the_line_where_a_wrapped_signature_starts(tmp_path, capsys):
    f = tmp_path / "test_x.py"
    f.write_text("import subprocess\nr = subprocess.run(\n    [\"grep\", \"-cP\", 'x', 'f'],\n    capture_output=True)\n")
    rows = [("AF-AP-60", re.compile(r"""\[\s*["']grep["']\s*,"""), "grep-based guard")]
    total = ap_screen.screen([f], rows, "t")
    out = capsys.readouterr().out
    assert total == 1
    assert f"{f}:3:" in out  # the match starts on the wrapped argv line, not the subprocess.run( line


def test_a_search_only_matcher_still_screens_per_line(tmp_path, capsys):
    f = tmp_path / "prod.py"
    f.write_text("a = 1\nemit(None)\nb = 2\nemit(None)\n")
    rows = [("AP-X", _SearchOnly("emit(None)"), "custom matcher row")]
    total = ap_screen.screen([f], rows, "t")
    out = capsys.readouterr().out
    assert total == 2
    assert f"{f}:2:" in out and f"{f}:4:" in out


def test_a_clean_file_yields_zero_hits(tmp_path, capsys):
    f = tmp_path / "clean.py"
    f.write_text("x = 1\n")
    rows = [("AF-AP-60", re.compile(r"""\[\s*["']grep["']\s*,"""), "grep-based guard")]
    assert ap_screen.screen([f], rows, "t") == 0


def test_the_ordinal_gate_row_sees_a_bracketed_call_count(tmp_path, capsys):
    """VERIFY-N5h F11, a tooling UNDER-report: the AF-AP-57 row's alternation offered `[0]` to `calls` and
    `attempts` but not to `call_count`, so the commonest spelling of the ordinal gate — `_call_count[0] == 1`
    — was invisible. Measured by the verifier on the probe test's parent: the screen reported ONE ordinal gate
    where a broad grep found FIVE across four fakes. Run against the hook's REAL row, not a stand-in."""
    _ap, test_rows = ap_screen._load_screens()
    rows = [r for r in test_rows if r[0] == "AF-AP-57"]
    assert len(rows) == 1, [r[0] for r in test_rows]
    f = tmp_path / "test_fake.py"
    f.write_text("def fake():\n"
                 "    _call_count[0] += 1\n"
                 "    if _call_count[0] == 1:\n"
                 "        raise OSError()\n"
                 "    return 0\n")
    assert ap_screen.screen([f], rows, "TEST_SCREEN") == 1
    out = capsys.readouterr().out
    assert "AF-AP-57" in out and f"{f}:3:" in out


def test_the_ordinal_gate_row_still_ignores_a_phase_gate(tmp_path, capsys):
    """The no-fire twin of the same row: widening the alternation must not swallow a gate on observable STATE,
    which is the remedy the row exists to recommend."""
    _ap, test_rows = ap_screen._load_screens()
    rows = [r for r in test_rows if r[0] == "AF-AP-57"]
    f = tmp_path / "test_fake.py"
    f.write_text("def fake():\n"
                 "    if threading.active_count() == 1:\n"
                 "        raise OSError()\n"
                 "    assert spy.call_count == 1\n")
    assert ap_screen.screen([f], rows, "TEST_SCREEN") == 0


def test_hit_line_text_is_the_numbered_line_past_a_unicode_line_separator(tmp_path, capsys):
    # AF-AP-132: the number counts "\n"; the printed text must come from the same numbering, not str.splitlines(),
    # which also breaks on U+2028/U+2029 and would print a later line's text beside this line's number
    f = tmp_path / "prod.py"
    f.write_text('BAD = {" ", " "}\nx = 1\nemit(None)\ny = 2\n', encoding="utf-8")
    rows = [("AP-X", re.compile(r"emit\(None\)"), "row")]
    total = ap_screen.screen([f], rows, "t")
    out = capsys.readouterr().out
    assert total == 1
    assert f"{f}:3: emit(None)" in out


# --staged-shell (task #245): the pre-commit hook's advisory step over the staged *.sh files. AF-AP-145's signature was
# registered with a screen line, yet it never ran on scripts/gpu_window.sh: the edit-snapshot hook returns early for a
# non-.py file, and the class was met there twice (2026-09-24).
import subprocess  # noqa: E402

TRAPPED = "#!/bin/bash\ncleanup() {\n  rm -f x\n}\ntrap cleanup EXIT\ntrap 'exit 143' TERM\n"
IGNORED = "#!/bin/bash\ncleanup() {\n  trap '' INT TERM\n  rm -f x\n}\ntrap cleanup EXIT\ntrap 'trap \"\" INT TERM; exit 143' TERM\n"
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ap_screen.py"


def _repo(tmp_path, files, staged):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    for name, text in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name).write_text(text)
    if staged:
        subprocess.run(["git", "add", "--", *staged], cwd=tmp_path, check=True)
    return subprocess.run([sys.executable, str(SCRIPT), "--staged-shell"], cwd=tmp_path, capture_output=True,
                          text=True, timeout=60)


def test_staged_shell_prints_the_af_ap_145_hits_of_a_staged_file(tmp_path):
    r = _repo(tmp_path, {"my run.sh": TRAPPED}, ["my run.sh"])
    assert r.returncode == 0, r.stderr
    assert "AF-AP-145: 2" in r.stdout and "my run.sh:2: cleanup() {" in r.stdout, r.stdout
    assert "my run.sh:6: trap 'exit 143' TERM" in r.stdout and "advisory, never blocking" in r.stdout


def test_staged_shell_is_silent_on_a_clean_file_unstaged_changes_and_the_vendored_trees(tmp_path):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "tracked.sh").write_text(IGNORED)
    subprocess.run(["git", "add", "tracked.sh"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=t@example.invalid", "-c", "user.name=t", "commit", "-q", "-m", "x"],
                   cwd=tmp_path, check=True)
    (tmp_path / "tracked.sh").write_text(TRAPPED)  # changed in the tree and not staged: not this commit's content
    r = _repo(tmp_path, {"ok.sh": IGNORED, "loose.sh": TRAPPED, "sandbox-kit/v.sh": TRAPPED, ".claude/h.sh": TRAPPED,
                         "notes.py": TRAPPED}, ["ok.sh", "sandbox-kit/v.sh", ".claude/h.sh", "notes.py"])
    assert r.returncode == 0 and r.stdout == "", (r.stdout, r.stderr)


def test_staged_shell_fails_loud_outside_a_git_repo(tmp_path):
    r = subprocess.run([sys.executable, str(SCRIPT), "--staged-shell"], cwd=tmp_path, capture_output=True, text=True,
                       timeout=60, env={"PATH": "/usr/bin:/bin", "GIT_CEILING_DIRECTORIES": str(tmp_path.parent)})
    assert r.returncode != 0 and "CalledProcessError" in r.stderr, (r.returncode, r.stderr[-300:])


def test_the_pre_commit_hook_runs_the_staged_shell_screen_and_never_blocks_on_it():
    hook = (Path(__file__).resolve().parents[1] / "scripts" / "hooks" / "pre-commit").read_text()
    assert '"$PY" "$REPO_ROOT/scripts/ap_screen.py" --staged-shell || true\n' in hook
