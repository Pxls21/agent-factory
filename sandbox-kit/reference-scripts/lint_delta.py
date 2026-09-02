#!/usr/bin/env python
"""Pyflakes DELTA + anti-pattern screen over a change set.

Why a delta and not a plain lint: the tree carries pre-existing pyflakes hits
that nobody is fixing this increment. Blocking on those would train everyone
to bypass the hook. Blocking on NEW hits only is cheap, deterministic, and
catches the classes that cost verify rounds 5-6 of RP-30b (orphaned imports,
np/pd used without import = AP-61, a helper reading a caller-only local =
AP-60): each was a pyflakes `undefined name` / `imported but unused` line that
no builder ran.

Modes:
  --staged          index vs HEAD (pre-commit hook)
  --base REV        working tree vs REV for every .py changed in REV..worktree
                    (lane_gate.sh: the push-base delta table)

Exit 1 when any NEW pyflakes hit exists. The anti-pattern regex screen
(AP_SCREEN from .claude/hooks/edit-snapshot.py) runs over ADDED lines only and
is advisory: tells, not verdicts. Bypass for a documented emergency with
SKIP_LINT_DELTA=1 — the bypass is printed so it shows up in the commit review.
"""
from __future__ import annotations

import argparse
import collections
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

from pyflakes import api as pyflakes_api
from pyflakes import reporter as pyflakes_reporter

REPO = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())


class _Collect(pyflakes_reporter.Reporter):
    def __init__(self) -> None:
        self.hits: list[str] = []
        self.syntax: list[str] = []

    def unexpectedError(self, filename, msg):  # noqa: N802 (pyflakes API)
        self.syntax.append(f"{filename}: {msg}")

    def syntaxError(self, filename, msg, lineno, offset, text):  # noqa: N802
        self.syntax.append(f"{filename}:{lineno}: {msg}")

    def flake(self, message):
        # Line numbers dropped on purpose: a hunk above shifts every line, and
        # the delta must compare WHAT was flagged, not WHERE.
        self.hits.append(message.message % message.message_args)


def _flakes(src: str | None, name: str) -> collections.Counter:
    if src is None:
        return collections.Counter()
    rep = _Collect()
    pyflakes_api.check(src, name, rep)
    c = collections.Counter(rep.hits)
    for s in rep.syntax:
        c[f"SYNTAX {s}"] += 1
    return c


def _git_show(spec: str) -> str | None:
    p = subprocess.run(["git", "show", spec], capture_output=True, text=True, cwd=REPO)
    return p.stdout if p.returncode == 0 else None


def _changed(args) -> list[str]:
    if args.staged:
        cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
    else:
        cmd = ["git", "diff", "--name-only", "--diff-filter=ACMR", args.base]
    out = subprocess.check_output(cmd, text=True, cwd=REPO)
    return [f for f in out.split() if f.endswith(".py")]


def _pair(args, path: str) -> tuple[str | None, str | None]:
    if args.staged:
        return _git_show(f"HEAD:{path}"), _git_show(f":{path}")
    wt = REPO / path
    new = wt.read_text() if wt.exists() else None
    return _git_show(f"{args.base}:{path}"), new


def _added_lines(args, path: str) -> list[str]:
    cmd = ["git", "diff", "-U0", "--no-color"]
    cmd += ["--cached"] if args.staged else [args.base]
    cmd += ["--", path]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO).stdout
    return [l[1:] for l in out.splitlines() if l.startswith("+") and not l.startswith("+++")]


def _ap_screen():
    hook = REPO / ".claude" / "hooks" / "edit-snapshot.py"
    if not hook.exists():
        return []
    spec = importlib.util.spec_from_file_location("edit_snapshot", hook)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception as e:  # the screen is advisory; never let it wedge a commit
        print(f"lint_delta: AP_SCREEN unavailable ({e!r})", file=sys.stderr)
        return []
    return getattr(mod, "AP_SCREEN", [])


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--staged", action="store_true")
    g.add_argument("--base")
    ap.add_argument("--no-ap", action="store_true", help="skip the anti-pattern screen")
    args = ap.parse_args()

    files = _changed(args)
    new_hits: list[tuple[str, str, int]] = []
    fixed = 0
    for f in files:
        old, new = _pair(args, f)
        d_old, d_new = _flakes(old, f), _flakes(new, f)
        for msg, n in (d_new - d_old).items():
            new_hits.append((f, msg, n))
        fixed += sum((d_old - d_new).values())

    label = "index vs HEAD" if args.staged else f"worktree vs {args.base}"
    print(f"lint_delta ({label}): {len(files)} .py changed, "
          f"{sum(n for _, _, n in new_hits)} NEW pyflakes hit(s), {fixed} removed")
    for f, msg, n in sorted(new_hits):
        print(f"  NEW  {f}: {msg}" + (f"  x{n}" if n > 1 else ""))

    if not args.no_ap:
        screen = _ap_screen()
        tells = []
        for f in files:
            added = "\n".join(_added_lines(args, f))
            for ap_id, rx, msg in screen:
                if rx.search(added):
                    tells.append(f"  {ap_id:6s}{f}: {msg}")
        if tells:
            print("anti-pattern screen (TELLS on added lines — verify each, advisory):")
            print("\n".join(tells))

    if new_hits:
        if os.environ.get("SKIP_LINT_DELTA") == "1":
            print("lint_delta: SKIP_LINT_DELTA=1 — NEW hits ACCEPTED BY BYPASS (say why in the commit body)")
            return 0
        print("lint_delta: BLOCKED — fix the NEW hits (or SKIP_LINT_DELTA=1 with a reason in the commit body)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
