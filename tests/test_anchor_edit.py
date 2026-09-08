"""scripts/anchor_edit.py — all-or-nothing anchored edits: every anchor validated before any write."""
import importlib.util
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOOL = ROOT / "scripts" / "anchor_edit.py"
_spec = importlib.util.spec_from_file_location("anchor_edit", TOOL)
anchor_edit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(anchor_edit)

DOC = "# title\n- **Origin tip:** old\n- row alpha | x |\n- row beta | y |\n"


def _run(path, *args):
    return subprocess.run([sys.executable, str(TOOL), str(path), *args], capture_output=True, text=True, timeout=30)


def test_replace_unique_anchor_applies(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    r = _run(p, "--replace", "row alpha | x |", "row alpha | x | LANDED")
    assert r.returncode == 0, r
    assert p.read_text() == DOC.replace("row alpha | x |", "row alpha | x | LANDED")


def test_zero_matches_refused_and_file_untouched(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    r = _run(p, "--replace", "typed from memory", "x")
    assert r.returncode == 2, r
    assert "matched 0 times" in r.stderr and "nothing written" in r.stderr
    assert p.read_text() == DOC


def test_two_matches_refused(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    r = _run(p, "--replace", "- row ", "- ROW ")
    assert r.returncode == 2 and "matched 2 times" in r.stderr, r
    assert p.read_text() == DOC


def test_all_or_nothing_a_good_op_before_a_bad_one_writes_nothing(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    r = _run(p, "--replace", "row alpha", "row ALPHA", "--replace", "absent anchor", "z")
    assert r.returncode == 2, r
    assert p.read_text() == DOC, "the first (valid) op must not land when the second refuses"


def test_insert_after_prefix_line(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    r = _run(p, "--insert-after", "- **Origin tip:**", "- **Local HEAD:** new")
    assert r.returncode == 0, r
    assert p.read_text() == "# title\n- **Origin tip:** old\n- **Local HEAD:** new\n- row alpha | x |\n- row beta | y |\n"


def test_insert_before_prefix_line_multiline_text(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    r = _run(p, "--insert-before", "- row beta", "- row a2\n- row a3")
    assert r.returncode == 0, r
    assert p.read_text() == "# title\n- **Origin tip:** old\n- row alpha | x |\n- row a2\n- row a3\n- row beta | y |\n"


def test_prefix_matching_two_lines_refused(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    r = _run(p, "--insert-after", "- row", "- row gamma")
    assert r.returncode == 2 and "matched 2 lines" in r.stderr, r
    assert p.read_text() == DOC


def test_at_file_values_and_later_op_sees_earlier_edit(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    new = tmp_path / "new.txt"; new.write_text("row alpha | x | LANDED")
    r = _run(p, "--replace", "row alpha | x |", "@" + str(new), "--insert-after", "- row alpha | x | LANDED", "- row alpha-2")
    assert r.returncode == 0, r
    assert p.read_text() == "# title\n- **Origin tip:** old\n- row alpha | x | LANDED\n- row alpha-2\n- row beta | y |\n"


def test_bad_arguments_exit_64_without_touching_the_file(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    assert _run(p, "--replace", "only-one-arg").returncode == 64
    assert _run(p).returncode == 64
    assert _run(p, "--frobnicate", "a", "b").returncode == 64
    assert p.read_text() == DOC


def test_plan_is_pure_and_deterministic():
    ops = [("replace", "alpha", "ALPHA"), ("insert-after", "- row ALPHA", "- inserted")]
    assert anchor_edit.plan(DOC, ops) == anchor_edit.plan(DOC, ops)
    assert anchor_edit.plan(DOC, ops) == "# title\n- **Origin tip:** old\n- row ALPHA | x |\n- inserted\n- row beta | y |\n"
