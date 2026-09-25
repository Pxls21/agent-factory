"""scripts/stamp.sh — its three modes against the clock (task #268 adds -b, the bare ten-minute bucket).

Deterministic and LLM-free. The oracle is `date -u` piped through the rule's own formula (CLAUDE.md:
`date -u +'%H:%M' | sed 's/[0-9]$/xZ/'`), never the script under test. The oracle is read before and after each
run, and the script's output must equal one of the two, so a ten-minute boundary between the reads is allowed.
"""
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "scripts" / "stamp.sh"


def _stamp(*args):
    return subprocess.run(["bash", str(TOOL), *args], capture_output=True, text=True, check=True, timeout=30).stdout


def _oracle(fmt):
    return subprocess.run(["bash", "-c", f"date -u +'{fmt}' | sed 's/[0-9]$/xZ/'"], capture_output=True, text=True,
                          check=True, timeout=30).stdout


def test_the_default_prints_the_dated_bucket():
    before, got, after = _oracle("%Y-%m-%d %H:%M"), _stamp(), _oracle("%Y-%m-%d %H:%M")
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\dxZ\n", got), got
    assert got in (before, after), (before, got, after)


def test_b_prints_the_bare_bucket():
    before, got, after = _oracle("%H:%M"), _stamp("-b"), _oracle("%H:%M")
    assert re.fullmatch(r"\d{2}:\dxZ\n", got), got
    assert got in (before, after), (before, got, after)


def test_b_is_the_time_part_of_the_default():
    before, bare, after = _stamp(), _stamp("-b"), _stamp()
    assert bare in (before[11:], after[11:]), (before, bare, after)


def test_x_prints_the_exact_instant():
    before, got, after = _oracle("%Y-%m-%dT%H:%M"), _stamp("-x"), _oracle("%Y-%m-%dT%H:%M")
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\n", got), got
    assert got[:15] in (before[:15], after[:15]), (before, got, after)   # the ten-minute bucket of the instant
