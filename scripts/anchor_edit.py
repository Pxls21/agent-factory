#!/usr/bin/env python3
"""anchor_edit.py — all-or-nothing anchored text edits for the ledger plane.

Every anchor is validated (exactly ONE match) before a single byte is written; one bad anchor
refuses the whole batch with rc 2 and the file untouched.  Born 2026-09-08: the checkpoint-9d
landing chained a heredoc edit script (whose first anchor was typed from memory) with the commit,
and the redo's second script died half-way on a fixed line index — a partial mutation twice in
one hour.  This tool never commits; commit in a SEPARATE call (skill build-loop, item 2).

    anchor_edit.py FILE [--replace OLD NEW]... [--insert-after PREFIX TEXT]... [--insert-before PREFIX TEXT]...

OLD/NEW/PREFIX/TEXT may be `@path` to read the value from a file (long ledger rows).  --replace
needs OLD to occur exactly once in the file; --insert-* need exactly one LINE that starts with
PREFIX, and insert TEXT as its own line(s) after/before it.  Ops apply in the order given; a
later op's anchor is validated against the text as the earlier ops leave it.
"""
import sys


def _val(v):
    return open(v[1:], encoding="utf-8").read() if v.startswith("@") else v


def plan(text, ops):
    """Return the edited text, or raise ValueError naming the first bad anchor.  Pure."""
    for kind, a, b in ops:
        if kind == "replace":
            n = text.count(a)
            if n != 1:
                raise ValueError("replace anchor matched %d times (need 1): %r" % (n, a[:80]))
            text = text.replace(a, b)
        else:
            lines = text.split("\n")
            hits = [i for i, l in enumerate(lines) if l.startswith(a)]
            if len(hits) != 1:
                raise ValueError("%s prefix matched %d lines (need 1): %r" % (kind, len(hits), a[:80]))
            at = hits[0] + (1 if kind == "insert-after" else 0)
            lines[at:at] = b.split("\n")
            text = "\n".join(lines)
    return text


def main(argv):
    if len(argv) < 2 or argv[1].startswith("-"):
        print(__doc__, file=sys.stderr)
        return 64
    path, ops, i = argv[1], [], 2
    while i < len(argv):
        flag = argv[i]
        if flag not in ("--replace", "--insert-after", "--insert-before") or i + 2 >= len(argv):
            print("anchor_edit: bad arguments at %r" % (flag,), file=sys.stderr)
            return 64
        ops.append((flag[2:], _val(argv[i + 1]), _val(argv[i + 2])))
        i += 3
    if not ops:
        print("anchor_edit: no ops", file=sys.stderr)
        return 64
    with open(path, encoding="utf-8") as f:
        before = f.read()
    try:
        after = plan(before, ops)
    except ValueError as e:
        print("anchor_edit: REFUSED, nothing written — %s" % (e,), file=sys.stderr)
        return 2
    with open(path, "w", encoding="utf-8") as f:
        f.write(after)
    print("anchor_edit: %d op(s) applied to %s (%d -> %d bytes)" % (len(ops), path, len(before), len(after)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
