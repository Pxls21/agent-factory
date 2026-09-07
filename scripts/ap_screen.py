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
"""
from __future__ import annotations

import argparse
import importlib.util
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


def screen(files, rows, label, limit=8):
    hits = {}
    for f in files:
        try:
            lines = f.read_text(errors="replace").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, 1):
            for row in rows:
                if row[1].search(line):
                    hits.setdefault(row[0], []).append(f"{f}:{i}: {line.strip()[:100]}")
    total = sum(len(v) for v in hits.values())
    print(f"--- {label}: {total} hits over {len(files)} files ---")
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
    ap.add_argument("--limit", type=int, default=8)
    ns = ap.parse_args(argv)
    ap_rows, test_rows = _load_screens()
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
