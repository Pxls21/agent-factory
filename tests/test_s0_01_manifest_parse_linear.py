"""Task #344: S0-01's two manifest parsers build each section's digest in linear time, over the same bytes.

`_parse_manifest_body` (proofs/S0-01/check_acp_conformance.py) and `_parse_manifest_gz`
(proofs/S0-01/tools/build_capture_record.py) grew each section by `+=` on a dict value. CPython cannot extend a string
in place while the dict holds it too, so every line copied its whole section: quadratic. On the old code, here, a
200,000-line manifest took 113.94 s in the checker and 53.51 s in the record builder (2026-09-28, task #344). Each
timed parse below runs in a child process with BOUND seconds as its timeout, so a quadratic parser fails by the clock,
fast. The digests stay the same: every committed golden manifest is parsed by both tools, and each digest is checked
against an oracle computed here (the sha256 of a section's lines, each followed by a newline).
"""
import gzip
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
S0_01 = ROOT / "proofs" / "S0-01"
CHECKER = S0_01 / "check_acp_conformance.py"
BUILDER = S0_01 / "tools" / "build_capture_record.py"
GOLDEN_DIR = S0_01 / "evidence" / "golden"
GOLDEN = sorted(GOLDEN_DIR.rglob("manifest-*.txt.gz"))
LINES_PER_TREE = 50_000          # four trees: 200,000 lines in all
BOUND = 20.0                     # seconds of wall time for one child; the old code needed 113.94 s and 53.51 s

_pins_spec = importlib.util.spec_from_file_location("s0_01_pins_for_344", S0_01 / "pins.py")
PINS = importlib.util.module_from_spec(_pins_spec)
_pins_spec.loader.exec_module(PINS)

# The child loads one tool by its path, with proofs/S0-01 first on sys.path (both tools `import pins`).
LOAD = ("import importlib.util, sys\n"
        "sys.path.insert(0, {s0_01!r})\n"
        "spec = importlib.util.spec_from_file_location('tool', {path!r})\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(mod)\n")


def _child(tool, body, timeout):
    """Run <body> in a child process after loading <tool>; <timeout> is the child's wall bound."""
    code = LOAD.format(s0_01=str(S0_01), path=str(tool)) + body
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=timeout, cwd=str(ROOT))


def _big_manifest():
    """200,000 lines in the pinned header order, each line in the v2.2 shape (pins.MANIFEST_LINE_RE)."""
    out = []
    for tree in PINS.MANIFEST_TREES:
        out.append(f"## {tree}")
        out += [f"{hashlib.sha256(f'{tree}/{i}'.encode()).hexdigest()} f 0644  ./dir{i % 997}/file-{i}.py"
                for i in range(LINES_PER_TREE)]
    return ("\n".join(out) + "\n").encode()


def _oracle(body):
    """Each section's sha256, computed apart from both tools: its lines, each followed by a newline."""
    sections, current = {}, None
    for line in body.decode("utf-8").split("\n"):
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current is not None and line:
            sections[current].append(line)
    return {tree: hashlib.sha256("".join(f"{line}\n" for line in lines).encode("utf-8")).hexdigest()
            for tree, lines in sections.items()}


def test_the_big_manifest_is_one_the_checker_parses_line_by_line():
    """The timed input is well formed: 200,000 lines, the pinned header order, every line in the pinned shape. So
    the checker reads it to the end and stops only at the pinned per-tree file count."""
    lines = _big_manifest().decode().split("\n")[:-1]
    assert len(lines) == 4 * (LINES_PER_TREE + 1) and len(PINS.MANIFEST_TREES) == 4
    assert [line for line in lines if line.startswith("## ")] == [f"## {tree}" for tree in PINS.MANIFEST_TREES]
    shape = re.compile(PINS.MANIFEST_LINE_RE)
    assert all(shape.match(line) for line in lines if not line.startswith("## "))


def test_the_checker_parses_200000_lines_within_the_bound(tmp_path):
    """The checker's parser reads every line, then refuses the per-tree file count (the manifest is not the pinned
    tree). That refusal comes after the whole body is read, and within BOUND seconds."""
    path = tmp_path / "manifest.txt"
    path.write_bytes(_big_manifest())
    try:
        proc = _child(CHECKER, "try:\n"
                               f"    mod._parse_manifest_body(open({str(path)!r}, 'rb').read(), 'big')\n"
                               "except mod.Failure as exc:\n"
                               "    print(exc)\n", BOUND)
    except subprocess.TimeoutExpired:
        pytest.fail(f"the checker's manifest parse needed more than {BOUND} s for {4 * LINES_PER_TREE} lines")
    assert proc.returncode == 0, proc.stderr[-2000:]
    first = PINS.MANIFEST_TREES[0]
    assert proc.stdout == (f"big: manifest {first} file count {LINES_PER_TREE} != pinned "
                           f"{PINS.PINNED_BASELINE_FILE_COUNTS[first]}\n"), proc.stdout


def test_the_record_builder_parses_200000_lines_within_the_bound(tmp_path):
    """The record builder's parser returns every section's digest within BOUND seconds, each equal to the oracle's."""
    body = _big_manifest()
    path = tmp_path / "manifest.txt.gz"
    path.write_bytes(gzip.compress(body, 1))
    try:
        proc = _child(BUILDER, "import json\nfrom pathlib import Path\n"
                               f"print(json.dumps(mod._parse_manifest_gz(Path({str(path)!r})), sort_keys=True))\n",
                      BOUND)
    except subprocess.TimeoutExpired:
        pytest.fail(f"the record builder's manifest parse needed more than {BOUND} s for {4 * LINES_PER_TREE} lines")
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert json.loads(proc.stdout) == _oracle(body)


def test_there_are_committed_golden_manifests():
    """The next test's rows exist: a glob that finds nothing would pass it vacuously."""
    assert len(GOLDEN) == 11, [str(path) for path in GOLDEN]


@pytest.mark.parametrize("path", GOLDEN, ids=[str(path.relative_to(GOLDEN_DIR)) for path in GOLDEN])
def test_a_committed_golden_manifest_keeps_its_digests_in_both_tools(path):
    """Both tools, on one committed golden manifest: every digest equals the oracle's, so the bytes each tool hashes
    did not change."""
    want = _oracle(gzip.decompress(path.read_bytes()))
    assert list(want) == list(PINS.MANIFEST_TREES), list(want)
    built = _child(BUILDER, "import json\nfrom pathlib import Path\n"
                            f"print(json.dumps(mod._parse_manifest_gz(Path({str(path)!r})), sort_keys=True))\n", 120)
    assert built.returncode == 0, built.stderr[-2000:]
    assert json.loads(built.stdout) == want
    checked = _child(CHECKER, "import gzip, json\n"
                              f"body = gzip.decompress(open({str(path)!r}, 'rb').read())\n"
                              "print(json.dumps(mod._parse_manifest_body(body, 'golden'), sort_keys=True))\n", 120)
    assert checked.returncode == 0, checked.stderr[-2000:]
    assert json.loads(checked.stdout) == want
