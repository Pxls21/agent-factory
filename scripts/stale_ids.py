#!/usr/bin/env python3
"""stale_ids.py — refuse a push whose added text cites a commit id the push itself rewrote (task #243).

push_clean.sh rewrites every commit of the unpushed range that carries a model-identifier trailer, and so every commit
after it: their ids change on the way to origin. A note written before the push that cites one of them by its LOCAL id
points at nothing on origin (2026-09-24: the ledger, the wiki and the incident log cited e0d2bdc, 911a6cd, b97c84c and
2b2aa18, which became d03e7c4, ee09d94, f74dfd7 and 3c9eb6f; AF-AP-187's class in prose).

push_clean.sh records the range's ids before its rewrite (--old, one full id per line, oldest first) and calls this
after it, before the push. Every hex token of 7 to 40 characters on an ADDED line of `git diff <origin-ref> HEAD`
that is the prefix of a rewritten id is a stale citation: exit 4, naming the file, the line, the old id and the new
one (cite the commit by its subject, or by the new id: the rewritten commits keep their new ids on the next run). A
commit MESSAGE of the range that cites one is reported as a warning only (a message cannot change without a rewrite).
Exit 0 when nothing is stale; 2 when git fails.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys

HEX = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def stale_in(line, rewritten):
    """-> [(token, old id)] for every token on the line that is the prefix of a rewritten id."""
    return [(tok, old) for tok in HEX.findall(line) for old in rewritten if old.startswith(tok)]


def added_lines(origin_ref, head):
    """-> [(path, line number, text)] for every added line of the range's diff. The prefixes are explicit, so a
    `diff.noprefix` or `diff.mnemonicPrefix` config cannot change the header; a `+++ ` line is a header only between
    `diff --git` and the first hunk, so an added line whose text starts with `++ ` is still scanned; a path git quotes
    (a non-ASCII name) is only a label: its lines are scanned all the same."""
    out, path, num, in_header = [], "?", 0, False
    diff = git("diff", "--no-color", "--no-ext-diff", "--src-prefix=a/", "--dst-prefix=b/", "-U0", origin_ref, head)
    for raw in diff.split("\n"):
        if raw.startswith("diff --git "):
            in_header, path = True, "?"
        elif in_header:
            if raw.startswith("+++ "):
                path = raw[4:].strip('"')
                path = path[2:] if path.startswith("b/") else path
            elif raw.startswith("@@"):
                in_header = False
                m = HUNK.match(raw)
                num = int(m.group(1)) if m else 0
        elif raw.startswith("@@"):
            m = HUNK.match(raw)
            num = int(m.group(1)) if m else 0
        elif raw.startswith("+"):
            out.append((path, num, raw[1:]))
            num += 1
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--old", required=True, help="a file of the range's full ids before the rewrite, oldest first")
    ap.add_argument("--origin-ref", required=True)
    ns = ap.parse_args(argv)
    try:
        head = git("rev-parse", "--verify", "HEAD^{commit}").strip()   # resolved once: every read below uses it
        rng = "%s..%s" % (ns.origin_ref, head)
        with open(ns.old, encoding="ascii") as fh:
            old = [x.strip() for x in fh if x.strip()]
        new = git("rev-list", "--reverse", rng).split()
        if len(old) != len(new):
            print("stale_ids: the range had %d commits before the rewrite and %d after; cannot map them"
                  % (len(old), len(new)), file=sys.stderr)
            return 2
        rewritten = {o: n for o, n in zip(old, new) if o != n}
        if not rewritten:
            return 0
        hits = [(p, i, tok, old_id) for p, i, text in added_lines(ns.origin_ref, head)
                for tok, old_id in stale_in(text, rewritten)]
        for line in git("log", rng, "--format=%h %B").split("\n"):
            for tok, old_id in stale_in(line, rewritten):
                print("stale_ids: WARNING: a commit message cites %s, which this push rewrote to %s"
                      % (tok, rewritten[old_id][:len(tok)]), file=sys.stderr)
    except (OSError, subprocess.CalledProcessError) as exc:
        print("stale_ids: %s" % exc, file=sys.stderr)
        return 2
    for path, num, tok, old_id in hits:
        print("stale_ids: %s:%d cites %s, a commit this push rewrote; it is %s on origin. Cite the commit by its "
              "subject or by the new id." % (path, num, tok, rewritten[old_id][:len(tok)]), file=sys.stderr)
    return 4 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
