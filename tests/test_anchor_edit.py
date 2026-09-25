"""scripts/anchor_edit.py — all-or-nothing anchored edits: every anchor validated before any write.

Task #268: {STAMP} and {DATESTAMP} in NEW and TEXT are filled from the clock, never in OLD or PREFIX. The clock oracle
is `date -u` through the rule's own formula, read before and after each run (a ten-minute boundary between is allowed).
"""
import datetime
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


def test_insert_that_adds_a_blank_run_warns_and_still_writes(tmp_path):
    doc = "head\n\n**B** block\n"
    p = tmp_path / "d.md"; p.write_text(doc)
    r = _run(p, "--insert-before", "**B**", "**A** block\n\n")     # the 2026-09-24 slip: one newline too many
    assert r.returncode == 0, r
    assert p.read_text() == "head\n\n**A** block\n\n\n**B** block\n"
    assert "WARNING: the edit adds 1 run(s) of two or more blank lines" in r.stderr, r.stderr
    p.write_text(doc)                                                # the right shape: exactly one newline, no warning
    r = _run(p, "--insert-before", "**B**", "**A** block\n")
    assert r.returncode == 0 and r.stderr == "", r
    assert p.read_text() == "head\n\n**A** block\n\n**B** block\n"


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


# --- task #268: the stamp tokens -------------------------------------------------------------------------------------
UTC = datetime.timezone.utc


def _oracle():
    """(bare, dated) from date -u and the rule's formula: `date -u +'%Y-%m-%d %H:%M' | sed 's/[0-9]$/xZ/'`."""
    out = subprocess.run(["bash", "-c", "date -u +'%Y-%m-%d %H:%M' | sed 's/[0-9]$/xZ/'"], capture_output=True,
                         text=True, check=True, timeout=30).stdout.strip()
    return out[11:], out


def test_new_and_text_values_are_filled_from_the_clock(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    before = _oracle()
    r = _run(p, "--replace", "row alpha | x |", "row alpha | {STAMP} |",
             "--insert-after", "- **Origin tip:**", "- **Checked:** {DATESTAMP} ({STAMP})")
    after = _oracle()
    assert r.returncode == 0, r
    want = {"# title\n- **Origin tip:** old\n- **Checked:** %s (%s)\n- row alpha | %s |\n- row beta | y |\n"
            % (dated, bare, bare): dated for bare, dated in (before, after)}
    got = p.read_text()
    assert got in want, got
    assert r.stdout.endswith("anchor_edit: 3 stamp token(s) filled from the clock (%s)\n" % want[got]), r.stdout


def test_an_at_file_value_is_filled_after_its_read_and_the_file_itself_is_left_alone(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    new = tmp_path / "new.txt"; new.write_text("row alpha | {DATESTAMP} |")
    before = _oracle()
    r = _run(p, "--replace", "row alpha | x |", "@" + str(new))
    after = _oracle()
    assert r.returncode == 0, r
    assert p.read_text() in {DOC.replace("row alpha | x |", "row alpha | %s |" % dated) for _, dated in (before, after)}
    assert new.read_text() == "row alpha | {DATESTAMP} |"


def test_old_and_prefix_are_matched_as_typed_never_filled(tmp_path):
    """The file also holds the clock's own bucket texts, so a FILLED anchor would match them and edit the wrong line."""
    bare, dated = _oracle()
    doc = "{STAMP} line\n{DATESTAMP} head\n%s line\n%s head\n" % (bare, dated)
    p = tmp_path / "d.md"; p.write_text(doc)
    r = _run(p, "--replace", "{STAMP} line", "stamp line", "--insert-before", "{DATESTAMP} head", "above")
    assert r.returncode == 0, r
    assert p.read_text() == "stamp line\nabove\n{DATESTAMP} head\n%s line\n%s head\n" % (bare, dated)
    assert "stamp token(s) filled" not in r.stdout


def test_a_refused_run_with_tokens_still_writes_nothing(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    r = _run(p, "--replace", "row alpha", "row {STAMP}", "--replace", "absent anchor", "{DATESTAMP}")
    assert r.returncode == 2 and "matched 0 times" in r.stderr and "nothing written" in r.stderr, r
    assert p.read_text() == DOC
    assert r.stdout == ""


def test_a_run_without_a_token_reports_no_fill(tmp_path):
    p = tmp_path / "d.md"; p.write_text(DOC)
    r = _run(p, "--replace", "row alpha | x |", "row alpha | {stamp} {STAMP } |")
    assert r.returncode == 0, r
    after = DOC.replace("row alpha | x |", "row alpha | {stamp} {STAMP } |")
    assert p.read_text() == after
    assert r.stdout == "anchor_edit: 1 op(s) applied to %s (%d -> %d bytes)\n" % (p, len(DOC), len(after))


def test_one_clock_read_serves_every_token_of_a_run(tmp_path, monkeypatch):
    ticks = iter([datetime.datetime(2026, 9, 25, 11, 29, 59, tzinfo=UTC),
                  datetime.datetime(2026, 9, 25, 11, 30, 0, tzinfo=UTC)])     # a second read would cross a boundary
    reads = []
    monkeypatch.setattr(anchor_edit.stamp_fill, "clock", lambda: reads.append(1) or next(ticks))
    p = tmp_path / "d.md"; p.write_text(DOC)
    rc = anchor_edit.main(["anchor_edit.py", str(p), "--replace", "row alpha | x |", "row alpha | {STAMP} |",
                           "--replace", "row beta | y |", "row beta | {DATESTAMP} |"])
    assert rc == 0 and len(reads) == 1
    assert p.read_text() == DOC.replace("row alpha | x |", "row alpha | 11:2xZ |").replace(
        "row beta | y |", "row beta | 2026-09-25 11:2xZ |")
