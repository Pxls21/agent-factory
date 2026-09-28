#!/usr/bin/env python3
"""lint_files.py — lint_delta.py's pyflakes DELTA over exactly the given files (task #339, D-103; LS-B9 round 2, item 2).

  python3 scripts/lint_files.py PATH...

lint_delta.py takes no file list: `--staged` (index vs HEAD) or `--base REV` (the tracked .py files git diff names), so
in a tree other lanes share it lints their files too, and it never sees an untracked new file. This script applies the
same rule to the given files only: a pyflakes hit that the file's HEAD version does not have is NEW. A tracked file is
compared with its HEAD version; an untracked file has no HEAD version, so every hit is new; a path that is not a .py
file, is absent or lies outside the root is listed as skipped. The rule is lint_delta's own `_flakes` (imported, never copied), so the
two cannot drift; its screen of added lines is not run here (the review stack runs scripts/ap_screen.py on the files).

exit: 0 no NEW hit; 1 a NEW hit; 2 usage.
"""
import argparse
import importlib.util
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load_lint_delta():
    spec = importlib.util.spec_from_file_location("lint_delta_rule", os.path.join(HERE, "lint_delta.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def resolve_head(root):
    """HEAD's commit sha, read ONCE for the whole run (AF-AP-175: other lanes commit into this tree mid-run), or None
    when the repository has no commit."""
    r = subprocess.run(["git", "-C", root, "rev-parse", "--verify", "-q", "HEAD^{commit}"], capture_output=True,
                       text=True, timeout=60)
    return r.stdout.strip() if r.returncode == 0 else None


def head_text(root, sha, rel):
    """The file at that commit, or None when it does not hold it (an untracked file)."""
    if sha is None:
        return None
    r = subprocess.run(["git", "-C", root, "show", "%s:%s" % (sha, rel)], capture_output=True, text=True, timeout=60)
    return r.stdout if r.returncode == 0 else None


def main(argv=None):
    ap = argparse.ArgumentParser(prog="lint_files.py", description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=ROOT, help="the repository root (default: the one holding this script)")
    ap.add_argument("paths", nargs="+", metavar="PATH")
    a = ap.parse_args(argv)
    root = os.path.realpath(a.root)
    rule = load_lint_delta()
    head = resolve_head(root)
    new_hits, skipped, linted, fixed = [], [], 0, 0
    for path in a.paths:
        rel = os.path.relpath(os.path.join(root, path), root)
        if rel == ".." or rel.startswith("../"):
            why = "outside the root"
        elif not rel.endswith(".py"):
            why = "not a .py file"
        elif not os.path.isfile(os.path.join(root, rel)):
            why = "absent"
        else:
            why = None
        if why:
            skipped.append("%s (%s)" % (rel, why))
            continue
        with open(os.path.join(root, rel), encoding="utf-8", errors="replace") as fh:
            new = fh.read()
        old = head_text(root, head, rel)
        d_old, d_new = rule._flakes(old, rel), rule._flakes(new, rel)
        linted += 1
        for msg, n in (d_new - d_old).items():
            new_hits.append((rel, msg, n, old is None))
        fixed += sum((d_old - d_new).values())
    print("lint_files (worktree vs HEAD %s, the given files): %d .py linted, %d NEW pyflakes hit(s), %d removed"
          % ((head or "none")[:12], linted, sum(n for _, _, n, _ in new_hits), fixed))
    for rel, msg, n, untracked in sorted(new_hits):
        print("  NEW  %s: %s%s%s" % (rel, msg, "  x%d" % n if n > 1 else "", "  (untracked: every hit is new)"
                                    if untracked else ""))
    for s in skipped:
        print("  skipped  %s" % s)
    return 1 if new_hits else 0


if __name__ == "__main__":
    sys.exit(main())
