"""scripts/premise_block.sh: the echoed command line is the executed command, byte for byte (VERIFY-J1-3, 2026-09-23)."""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "premise_block.sh"


def _run(text):
    return subprocess.run(["bash", str(SCRIPT)], input=text, capture_output=True, text=True, cwd=ROOT, timeout=60)


def test_each_command_is_echoed_as_run_then_its_output_and_a_nonzero_rc():
    cmds = "printf 'a.b\\naxb\\n' | grep -E 'a\\.b'\n# a comment line is skipped\n\nfalse\n"
    r = _run(cmds)
    assert r.returncode == 0, r.stderr
    assert r.stdout == "$ printf 'a.b\\naxb\\n' | grep -E 'a\\.b'\na.b\n$ false\n[rc=1]\n", r.stdout


def test_the_echo_is_the_command_that_ran_not_a_retyped_one():
    # the escaped dot matters: `a.b` would also match `axb`; the echoed pattern must be the one that produced the output
    r = _run("printf 'a.b\\naxb\\n' | grep -c -E 'a.b'\n")
    assert r.stdout == "$ printf 'a.b\\naxb\\n' | grep -c -E 'a.b'\n2\n", r.stdout


def test_stderr_is_part_of_the_pasted_output():
    r = _run("echo out; echo err >&2\n")
    assert r.stdout == "$ echo out; echo err >&2\nout\nerr\n", r.stdout
