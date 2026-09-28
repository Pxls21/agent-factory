#!/usr/bin/env python3
"""gate_files.py — the tests that name a path: the project rule "a changed file's gate includes every test that names
its path" (skill build-loop, 2026-09-25) as a script (task #339, D-103; brief tasks/briefs/labeling/LS-B9-brief.md).

  python3 scripts/gate_files.py PATH...          the test files, sorted and unique, one per line
  python3 scripts/gate_files.py --why PATH...    one line per test file: the kind of each mention and its lines

A test file is a file under tests/ named test_*.py, or any file under harness-ports/tests/: tracked or untracked,
never under __pycache__, text only (a file that holds a NUL byte is skipped). It is listed when its text holds one of
the given path strings, and a given path that is itself a test file is listed too. The match is the literal path
string, as `grep -l` matches it (a PATH is normalized first: `./scripts/x.py` and an absolute path under the root both
become `scripts/x.py`). A test that builds the path from parts (ROOT / "scripts" / "x.py") does not name it and is
not listed; ripwire's test-gate is the instrument for import edges.

--why prints `<file>  self  code:L,L  comment:L,L` (the parts that apply): `self` for a given path that is itself a
test file, `comment` for a mention on a line whose first non-blank character is `#` or on a docstring line of a
Python file, `code` for every other mention. A comment-only mention still counts; the table shows it before a gate
pays for the file (2026-09-28: a test that named docs/INCIDENT-LOG.md only in two comments ran over 19 minutes in a
docs gate).

exit: 0 (with or without a file listed); 2 usage.
"""
import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# (directory under the root, True when only files named test_*.py count)
TEST_DIRS = (("tests", True), (os.path.join("harness-ports", "tests"), False))


def test_files(root):
    """Yield (repo-relative POSIX path, absolute path) for every candidate test file under the root."""
    for rel_dir, only_test_py in TEST_DIRS:
        for d, subdirs, names in os.walk(os.path.join(root, rel_dir)):
            subdirs[:] = sorted(s for s in subdirs if s != "__pycache__")
            for name in sorted(names):
                if only_test_py and not (name.startswith("test_") and name.endswith(".py")):
                    continue
                path = os.path.join(d, name)
                if os.path.isfile(path):
                    yield os.path.relpath(path, root).replace(os.sep, "/"), path


def read_text(path):
    """The file's text, or None for a binary (NUL byte) or unreadable file (the second one is reported)."""
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError as e:
        sys.stderr.write("gate_files: unreadable, skipped: %s (%s)\n" % (path, e.strerror or e))
        return None
    if b"\0" in data:
        return None
    return data.decode("utf-8", errors="replace")


def docstring_lines(text):
    """The line numbers of every module, class and function docstring (an empty set when the text does not parse)."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return set()
    lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            first = node.body[0] if node.body else None
            if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                lines.update(range(first.lineno, first.end_lineno + 1))
    return lines


def normalize(path, root):
    """The path string a test would name: normalized, relative to the root when it lies under it."""
    p = os.path.normpath(path)
    if os.path.isabs(p):
        rel = os.path.relpath(p, root)
        if rel != ".." and not rel.startswith(".." + os.sep):
            p = rel
    return p.replace(os.sep, "/")


def gate(root, paths):
    """{test file: (is a given path, [code lines], [comment lines])} for every test file that names a path."""
    needles = sorted({normalize(p, root) for p in paths})
    found = {}
    for rel, path in test_files(root):
        is_self = rel in needles
        text = read_text(path)
        if text is None:
            continue
        lines = text.split("\n")          # "\n" only: the numbering grep -n and an editor show
        hits = [i for i, line in enumerate(lines, 1) if any(n in line for n in needles)]
        if not hits and not is_self:
            continue
        doc = docstring_lines(text) if (hits and rel.endswith(".py")) else set()
        code, comment = [], []
        for i in hits:
            (comment if lines[i - 1].lstrip().startswith("#") or i in doc else code).append(i)
        found[rel] = (is_self, code, comment)
    return found


def main(argv=None):
    ap = argparse.ArgumentParser(prog="gate_files.py", description=__doc__.splitlines()[0])
    ap.add_argument("--why", action="store_true", help="one line per file: self, and the code and comment lines")
    ap.add_argument("--root", default=ROOT, help="the repository root (default: the one holding this script)")
    ap.add_argument("paths", nargs="+", metavar="PATH")
    a = ap.parse_args(argv)
    root = os.path.realpath(a.root)
    bad = [p for p in a.paths if normalize(p, root) in ("", ".")]
    if bad:
        ap.error("a PATH must name something below the root, not the root itself: %r" % bad[0])
    found = gate(root, a.paths)
    for rel in sorted(found):
        if not a.why:
            print(rel)
            continue
        is_self, code, comment = found[rel]
        parts = [rel] + (["self"] if is_self else [])
        parts += ["code:" + ",".join(map(str, code))] if code else []
        parts += ["comment:" + ",".join(map(str, comment))] if comment else []
        print("  ".join(parts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
