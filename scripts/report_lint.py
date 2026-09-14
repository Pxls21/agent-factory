#!/usr/bin/env python3
"""report_lint.py — mechanical check of every `file:line` claim in a lane/verify report against the tree.

Why: four consecutive S0-01 verdicts spent a BLOCKER each on typed line references (CK10: 13 wrong, CK11: 17 of 35,
D5i: 11 of 22, B5g: 6 of 8 killer lines) — AF-AP-37's class (numbers typed, not pasted), which no reviewer should
have to find by hand. A lane runs this before returning its report and pastes the summary line; a verifier runs it
first and spends its time on substance.

Usage:
  scripts/report_lint.py REPORT.md --map C=proofs/S0-01/check_acp_conformance.py --map T=tests/test_s0_01_check_acp_conformance.py
                        [--map backend=proofs/S0-01/tools/scripted_backend.py ...] [--rev <sha>] [--tolerance 1]

What it checks: every reference of the shape `<alias-or-path>:<line>[-<line>]` on a report line is resolved to the
file (an alias from --map, a repo-relative path, or a bare basename among the mapped files) and the cited lines
are read at --rev (default: the working tree). The report line's own CLAIM TOKENS — backticked spans, `def name`,
`_UPPER_CASE` names, quoted strings, 4+ characters, minus the reference itself — must appear in the cited lines:
  OK           a claim token appears inside the cited range
  NEAR         a claim token appears within --tolerance lines of the range (an off-by-one or two: still a MISS in spirit)
  MISS         the cited lines contain none of the claim tokens (points at a comment, a blank line, another function)
  UNCHECKABLE  the report line carries no claim token to test against (the ref is not proven, only stated)
Exit 1 when any MISS exists. NEAR and UNCHECKABLE never pass silently: they are counted in the summary line.
`--min-refs N` exits 1 when fewer than N refs resolve OK: a report with no machine-checkable ref lints clean by
construction (MISS 0 over nothing), so a checkpoint gates on a floor, never on the MISS count alone.
`alias@<sha>:NN` pins ONE reference to a git revision (a PIN-era line cited after the file moved on); token matching is
case-insensitive (a prose FIFO / TOCTOU matches the code's fifo / toctou); every MISS row ends with the fix hint. A lane
fixes MISSes for at most THREE rounds, then pastes the summary and stops — the bar is the floor plus the paste, never a
"MISS 0" chased forever (N5k, 2026-09-14: 47 minutes and 20 turns relocating references that were already right).
Heuristic by design — it proves nothing about a report; it removes the class of reference a reader cannot trust.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REF_RE = re.compile(r"(?<![\w/.-])([A-Za-z_][\w./-]*?)(?:@([0-9a-f]{7,40}))?:(\d+)(?:-(\d+))?(?![\w-])")
FIX_HINT = ("fix: if the cited line is RIGHT, add one backticked identifier copied from it to this report line; "
            "if the number is wrong, correct it; a line that existed only at an older revision is written as "
            "alias@<sha>:NN (checked at that revision) or in words, never as a bare alias:NN")
TOKEN_RES = [
    re.compile(r"`([^`]{4,})`"),
    re.compile(r"\b(def\s+\w{3,}|class\s+\w{3,})"),
    re.compile(r"\b(_?[A-Z][A-Z0-9_]{3,})\b"),
    re.compile(r"\"([^\"]{4,})\"|'([^']{4,})'"),
]


def _read_file(path: str, rev: str | None, root: Path) -> list[str] | None:
    if rev:
        r = subprocess.run(["git", "-C", str(root), "show", f"{rev}:{path}"], capture_output=True, text=True)
        if r.returncode != 0:
            return None
        return r.stdout.splitlines()
    p = root / path
    if not p.is_file():
        return None
    return p.read_text(errors="replace").splitlines()


def _claim_tokens(line: str, ref_text: str) -> list[str]:
    toks: list[str] = []
    for rx in TOKEN_RES:
        for m in rx.finditer(line):
            for g in m.groups():
                if g and g not in ref_text and not REF_RE.fullmatch(g.strip()):
                    toks.append(g.strip())
    # a backticked span that is itself a `X:NNN` reference is not a claim about the cited line
    return [t for t in toks if not REF_RE.search(t) and len(t) >= 4]


def lint(report: Path, maps: dict[str, str], rev: str | None, tolerance: int, root: Path):
    basenames = {Path(v).name: v for v in maps.values()}
    cache: dict[tuple, list[str] | None] = {}
    rows = []
    for lineno, line in enumerate(report.read_text(errors="replace").splitlines(), 1):
        for m in REF_RE.finditer(line):
            key, ref_rev, a, b = m.group(1), m.group(2), int(m.group(3)), int(m.group(4) or m.group(3))
            at = ref_rev or rev   # `alias@<sha>:NN` pins ONE ref to a revision (a PIN-era line cited after the file moved on)
            path = maps.get(key) or basenames.get(key) or (key if (root / key).is_file() or at else None)
            if path is None or (not at and not (root / path).is_file()):
                continue  # not a file reference we can resolve (a time, a ratio, a URL port ...)
            if (path, at) not in cache:
                cache[(path, at)] = _read_file(path, at, root)
            src = cache[(path, at)]
            if src is None:
                rows.append((lineno, m.group(0), "UNRESOLVED", f"{path} not at {at or 'worktree'}"))
                continue
            toks = _claim_tokens(line, m.group(0))
            if not toks:
                rows.append((lineno, m.group(0), "UNCHECKABLE", "no claim token on the report line"))
                continue
            lo, hi = max(1, min(a, b)), min(len(src), max(a, b))
            cited = "\n".join(src[lo - 1:hi]).lower()   # case-insensitive: a prose FIFO / TOCTOU / READ matches the code's spelling
            ltoks = [t.lower() for t in toks]
            if any(t in cited for t in ltoks):
                rows.append((lineno, m.group(0), "OK", ""))
                continue
            near_lo, near_hi = max(1, lo - tolerance), min(len(src), hi + tolerance)
            near = "\n".join(src[near_lo - 1:near_hi]).lower()
            if any(t in near for t in ltoks):
                rows.append((lineno, m.group(0), "NEAR", f"a claim token sits within {tolerance} line(s) of the range"))
            else:
                snippet = src[lo - 1].strip()[:70] if lo <= len(src) else "<beyond EOF>"
                rows.append((lineno, m.group(0), "MISS", f"cited line reads: {snippet!r}; tokens {toks[:3]}; " + FIX_HINT))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("report")
    ap.add_argument("--map", action="append", default=[], help="ALIAS=path (repeatable)")
    ap.add_argument("--rev", default=None, help="git revision to read the cited files at (default: the working tree)")
    ap.add_argument("--tolerance", type=int, default=1)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--min-refs", type=int, default=0,
                    help="fail (rc 1) when fewer than N refs resolve OK — a report that cites nothing lints clean "
                         "by construction (B3's `0 refs — OK 0, MISS 0`, 2026-09-14); a checkpoint passes a floor")
    ns = ap.parse_args(argv)
    maps = {}
    for item in ns.map:
        if "=" not in item:
            ap.error(f"--map expects ALIAS=path, got {item!r}")
        k, v = item.split("=", 1)
        maps[k] = v
    rows = lint(Path(ns.report), maps, ns.rev, ns.tolerance, Path(ns.root))
    counts = {"OK": 0, "NEAR": 0, "MISS": 0, "UNCHECKABLE": 0, "UNRESOLVED": 0}
    for lineno, ref, verdict, note in rows:
        counts[verdict] += 1
        if verdict != "OK":
            print(f"{verdict:12s} report:{lineno:<5d} {ref:40s} {note}")
    total = sum(counts.values())
    print(f"report_lint: {total} refs — OK {counts['OK']}, NEAR {counts['NEAR']}, MISS {counts['MISS']}, "
          f"UNCHECKABLE {counts['UNCHECKABLE']}, UNRESOLVED {counts['UNRESOLVED']}"
          + (f" (at {ns.rev})" if ns.rev else " (worktree)"))
    if counts["OK"] < ns.min_refs:
        print(f"report_lint: FLOOR — OK {counts['OK']} < --min-refs {ns.min_refs}: the report cites too little to be graded")
        return 1
    return 1 if counts["MISS"] else 0


if __name__ == "__main__":
    sys.exit(main())
