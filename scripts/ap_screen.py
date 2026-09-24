#!/usr/bin/env python3
"""ap_screen.py — the anti-pattern registry screen over WHOLE FILES, not edited hunks.

The edit-snapshot hook screens only the hunk a lane just wrote, so a registered signature sitting in a line nobody
touched this round is never seen again: the S0-01 checker carried an AF-AP-40 presence-gated schema check from
checkpoint 5 to checkpoint 8t — eleven verification rounds — while its signature was in the registry the whole
time. Run this over the whole component before every checkpoint and after every new registry row (the bug-echo
sweep): it prints every hit per class, production files against AP_SCREEN and test files against TEST_SCREEN.
Advisory (exit 0): a hit is a candidate to classify by RUNNING it — defect / reviewed-safe (name the guard) /
documented limit — never a verdict by itself, and never silently ignored.

Usage: scripts/ap_screen.py [--tests] PATH...      (a directory is walked for *.py; --tests selects TEST_SCREEN)
       scripts/ap_screen.py --s0-01                (the S0-01 production + test sets, both screens)
       scripts/ap_screen.py --staged-shell         (the staged *.sh files of the repo in the cwd; silent on no hit)
The last form is the pre-commit hook's shell step (task #245): the edit-snapshot hook returns early for a non-.py
file, so AF-AP-145's registered signature never ran on scripts/gpu_window.sh and the class was met there twice.
"""
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_screens():
    spec = importlib.util.spec_from_file_location("es", ROOT / ".claude" / "hooks" / "edit-snapshot.py")
    es = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(es)
    return list(es.AP_SCREEN), list(getattr(es, "TEST_SCREEN", []))


def _files(paths):
    out = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            out += sorted(x for x in p.glob("*.py"))
        elif p.is_file():
            out.append(p)
    return out


def screen(files, rows, label, limit=8, quiet=False):
    items = []
    for f in files:
        try:
            items.append((f, f.read_text(errors="replace")))
        except OSError:
            continue
    return screen_texts(items, rows, label, limit, quiet, n_files=len(files))


def screen_texts(items, rows, label, limit=8, quiet=False, n_files=None):
    """The screen over (name, text) pairs: a file read from the tree, or a staged blob (--staged-shell)."""
    hits = {}
    for f, text in items:
        lines = text.split("\n")  # "\n" only, matching text.count("\n") below (AF-AP-132)
        # the whole text, not line by line: the hook screens multi-line HUNKS, and a signature that spans a line
        # break (a subprocess argv list wrapped after the paren) must screen the same way here
        for row in rows:
            finditer = getattr(row[1], "finditer", None)
            if finditer is None:  # a custom matcher object (the hook's AST-backed rows expose search() only)
                for i, line in enumerate(lines, 1):
                    if row[1].search(line):
                        hits.setdefault(row[0], []).append(f"{f}:{i}: {line.strip()[:100]}")
                continue
            for m in finditer(text):
                i = text.count("\n", 0, m.start()) + 1
                hits.setdefault(row[0], []).append(f"{f}:{i}: {lines[i - 1].strip()[:100]}")
    total = sum(len(v) for v in hits.values())
    if quiet and not total:
        return 0
    print(f"--- {label}: {total} hits over {len(items) if n_files is None else n_files} files ---")
    for ap in sorted(hits, key=lambda k: (-len(hits[k]), k)):
        print(f"{ap}: {len(hits[ap])}")
        for h in hits[ap][:limit]:
            print("   ", h)
        if len(hits[ap]) > limit:
            print(f"    ... +{len(hits[ap]) - limit}")
    return total


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--tests", action="store_true", help="screen the given paths with TEST_SCREEN")
    ap.add_argument("--s0-01", action="store_true", help="the S0-01 production and test sets")
    ap.add_argument("--staged-shell", action="store_true",
                    help="the staged *.sh files of the repo in the cwd (not sandbox-kit/ or .claude/); silent on no hit")
    ap.add_argument("--limit", type=int, default=8)
    ns = ap.parse_args(argv)
    ap_rows, test_rows = _load_screens()
    if ns.staged_shell:
        # The STAGED blob of each staged *.sh (`git show :<path>`), never the working-tree file: the commit carries the
        # blob (VERIFY-T243-245 B-F1), a staged symlink is its target string, never followed (B-F3), and the names are
        # filtered here rather than by a pathspec that GIT_*_PATHSPECS would reinterpret (B-F4); T counts (B-F2).
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                             check=True).stdout.strip()
        names = subprocess.run(["git", "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMRT"], cwd=top,
                               capture_output=True, check=True).stdout.decode("utf-8", "surrogateescape").split("\0")
        items = []
        for n in names:
            if not n.endswith(".sh") or n.startswith(("sandbox-kit/", ".claude/")):
                continue
            blob = subprocess.run(["git", "show", ":" + n], cwd=top, capture_output=True, check=True).stdout
            items.append((Path(top) / n, blob.decode("utf-8", "replace")))
        if screen_texts(items, ap_rows, "AP_SCREEN over the staged shell files", ns.limit, quiet=True):
            print("(advisory, never blocking: classify each hit by running it; the screen finds tells, not verdicts)")
        return 0
    if ns.s0_01:
        prod = _files([ROOT / "proofs/S0-01", ROOT / "proofs/S0-01/tools", ROOT / "proofs/S0-01/tools/pc"])
        tests = sorted((ROOT / "tests").glob("test_s0_01_*.py")) + sorted((ROOT / "tests/red").glob("test_s0_01_*.py"))
        screen(prod, ap_rows, "AP_SCREEN over S0-01 production", ns.limit)
        screen(tests, test_rows, "TEST_SCREEN over S0-01 tests", ns.limit)
        return 0
    if not ns.paths:
        ap.error("give PATH... or --s0-01")
    rows, label = (test_rows, "TEST_SCREEN") if ns.tests else (ap_rows, "AP_SCREEN")
    screen(_files(ns.paths), rows, f"{label} over {len(ns.paths)} path(s)", ns.limit)
    return 0


if __name__ == "__main__":
    sys.exit(main())
