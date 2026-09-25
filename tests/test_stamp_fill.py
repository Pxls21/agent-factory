"""scripts/stamp_fill.py — the {STAMP} and {DATESTAMP} tokens filled from the clock (task #268).

Deterministic and LLM-free. Fixed instants pin the two forms exactly (the expected texts are written out, never computed
by the module under test); the live cases compare with `date -u` through the rule's own formula, read before and after
each run so that a ten-minute boundary between the reads is allowed. stamp_fill's computation must agree with
scripts/stamp.sh, the shell source of the same two forms.
"""
import datetime
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "scripts" / "stamp_fill.py"
STAMP_SH = REPO / "scripts" / "stamp.sh"
UTC = datetime.timezone.utc


@pytest.fixture
def sf():
    spec = importlib.util.spec_from_file_location("stamp_fill_under_test", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _oracle():
    """(bare, dated) from date -u and the rule's formula: `date -u +'%Y-%m-%d %H:%M' | sed 's/[0-9]$/xZ/'`."""
    out = subprocess.run(["bash", "-c", "date -u +'%Y-%m-%d %H:%M' | sed 's/[0-9]$/xZ/'"], capture_output=True,
                         text=True, check=True, timeout=30).stdout.strip()
    return out[11:], out


def _cli(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True, timeout=30)


@pytest.mark.parametrize("instant, bare, dated", [
    (datetime.datetime(2026, 9, 25, 9, 7, 59, tzinfo=UTC), "09:0xZ", "2026-09-25 09:0xZ"),
    (datetime.datetime(2026, 9, 25, 23, 59, 59, 999999, tzinfo=UTC), "23:5xZ", "2026-09-25 23:5xZ"),
    (datetime.datetime(2026, 9, 26, 0, 0, 0, tzinfo=UTC), "00:0xZ", "2026-09-26 00:0xZ"),
    (datetime.datetime(2026, 9, 26, 1, 15, tzinfo=datetime.timezone(datetime.timedelta(hours=2))),
     "23:1xZ", "2026-09-25 23:1xZ"),                                     # an aware non-UTC instant is read in UTC
])
def test_stamps_at_fixed_instants(sf, instant, bare, dated):
    assert sf.stamps(instant) == (bare, dated)


def test_fill_fills_every_token_and_counts_them(sf):
    now = datetime.datetime(2026, 9, 25, 11, 27, 3, tzinfo=UTC)
    assert sf.fill("a {STAMP} b {DATESTAMP} c {STAMP}\n", now) == ("a 11:2xZ b 2026-09-25 11:2xZ c 11:2xZ\n", 3)
    assert sf.fill("{DATESTAMP}{STAMP}{{STAMP}}", now) == ("2026-09-25 11:2xZ11:2xZ{11:2xZ}", 3)
    plain = "no token: {stamp} {STAMP } STAMP {DATE STAMP}"
    assert sf.fill(plain, now) == (plain, 0)


def test_the_python_forms_agree_with_stamp_sh(sf):
    """The one-source-of-truth check: stamp_fill's computation equals stamp.sh -b and stamp.sh at the same clock."""
    def shell():
        return tuple(subprocess.run(["bash", str(STAMP_SH), *mode], capture_output=True, text=True, check=True,
                                    timeout=30).stdout.strip() for mode in (["-b"], []))
    for _ in range(3):                       # a ten-minute boundary inside the reads: read again
        before = shell()
        python = sf.stamps(sf.clock())
        if shell() == before:
            assert python == before
            return
    pytest.fail("the clock crossed a ten-minute boundary during three read rounds")


def test_the_cli_fills_both_tokens_in_place_and_keeps_every_other_byte(tmp_path):
    path = tmp_path / "brief.md"
    raw = "# brief\r\n## PREMISE — MEASURED at authoring ({DATESTAMP}, the tree)\r\nat {STAMP}: é, no final newline"
    path.write_bytes(raw.encode("utf-8"))
    before, result, after = _oracle(), _cli(path), _oracle()
    assert result.returncode == 0, result.stderr
    want = {raw.replace("{DATESTAMP}", dated).replace("{STAMP}", bare).encode("utf-8"): dated
            for bare, dated in (before, after)}
    got = path.read_bytes()
    assert got in want, got
    assert result.stdout == f"stamp_fill: 2 token(s) filled in {path} ({want[got]})\n"
    assert result.stderr == ""


def test_a_file_with_no_token_is_never_written(tmp_path):
    path = tmp_path / "plain.md"
    path.write_bytes(b"no token here, {stamp}\n")
    os.utime(path, ns=(1_000_000_000, 1_000_000_000))
    inode = path.stat().st_ino
    result = _cli(path)
    assert result.returncode == 0, result.stderr
    assert result.stdout == f"stamp_fill: 0 token(s) in {path}, untouched\n"
    assert path.read_bytes() == b"no token here, {stamp}\n"
    assert (path.stat().st_mtime_ns, path.stat().st_ino) == (1_000_000_000, inode)   # not rewritten, not replaced


@pytest.mark.parametrize("bad_first", [False, True], ids=["good-then-bad", "bad-then-good"])
@pytest.mark.parametrize("kind", ["missing", "not-utf8"])
def test_one_unreadable_file_refuses_the_run_and_nothing_is_written(tmp_path, kind, bad_first):
    good = tmp_path / "good.md"
    good.write_text("{STAMP}\n")
    bad = tmp_path / "bad.md"
    if kind == "not-utf8":
        bad.write_bytes(b"\xff\xfe {STAMP}\n")
    result = _cli(*((bad, good) if bad_first else (good, bad)))
    assert result.returncode == 2, result
    assert result.stderr.startswith(f"stamp_fill: REFUSED, nothing written — {bad}: "), result.stderr
    assert result.stdout == ""
    assert good.read_text() == "{STAMP}\n"
    if kind == "missing":
        assert not bad.exists()
    else:
        assert bad.read_bytes() == b"\xff\xfe {STAMP}\n"


def test_one_clock_read_serves_every_file_of_a_run(sf, tmp_path, monkeypatch, capsys):
    ticks = iter([datetime.datetime(2026, 9, 25, 11, 29, 59, tzinfo=UTC),
                  datetime.datetime(2026, 9, 25, 11, 30, 0, tzinfo=UTC)])     # a second read would cross a boundary
    reads = []
    monkeypatch.setattr(sf, "clock", lambda: reads.append(1) or next(ticks))
    first, second = tmp_path / "a.md", tmp_path / "b.md"
    first.write_text("a {STAMP}\n")
    second.write_text("b {DATESTAMP}\n")
    assert sf.main(["stamp_fill.py", str(first), str(second)]) == 0
    assert len(reads) == 1
    assert (first.read_text(), second.read_text()) == ("a 11:2xZ\n", "b 2026-09-25 11:2xZ\n")
    assert capsys.readouterr().out == (f"stamp_fill: 1 token(s) filled in {first} (2026-09-25 11:2xZ)\n"
                                       f"stamp_fill: 1 token(s) filled in {second} (2026-09-25 11:2xZ)\n")


@pytest.mark.parametrize("args", [[], ["--help"], ["-x", "a.md"]])
def test_usage_errors_exit_64_and_write_nothing(tmp_path, args):
    result = subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, timeout=30,
                            cwd=tmp_path)
    assert result.returncode == 64, result
    assert "{STAMP}" in result.stderr and "{DATESTAMP}" in result.stderr   # the usage text names the tokens
    assert list(tmp_path.iterdir()) == []
