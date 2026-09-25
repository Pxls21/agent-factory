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

Stamp tokens (task #268): {STAMP} and {DATESTAMP} in NEW and TEXT (an `@path` value after its read)
are filled from the clock with the bare and the dated ten-minute bucket (11:2xZ, 2026-09-25 11:2xZ;
scripts/stamp_fill.py, one clock read per run).  OLD and PREFIX are never filled: they match text
already in the file.
"""
import importlib.util
import pathlib
import sys

# The one Python computation of the stamp tokens, loaded by path from beside this file (as ap_screen.py loads its hook).
_spec = importlib.util.spec_from_file_location("stamp_fill", pathlib.Path(__file__).resolve().parent / "stamp_fill.py")
stamp_fill = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(stamp_fill)


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
    now, filled = stamp_fill.clock(), 0         # one clock read: every token of the run gets the same bucket
    while i < len(argv):
        flag = argv[i]
        if flag not in ("--replace", "--insert-after", "--insert-before") or i + 2 >= len(argv):
            print("anchor_edit: bad arguments at %r" % (flag,), file=sys.stderr)
            return 64
        anchor = _val(argv[i + 1])
        value, n = stamp_fill.fill(_val(argv[i + 2]), now)   # NEW / TEXT only: OLD and PREFIX match existing text
        ops.append((flag[2:], anchor, value))
        filled += n
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
    if filled:
        print("anchor_edit: %d stamp token(s) filled from the clock (%s)" % (filled, stamp_fill.stamps(now)[1]))
    grew = after.count("\n\n\n") - before.count("\n\n\n")   # advisory: a TEXT ending in a newline inserts one more
    if grew > 0:                                            # (empty) line; bit four times on 2026-09-24
        print("anchor_edit: WARNING: the edit adds %d run(s) of two or more blank lines; an insert TEXT that ends "
              "in a newline inserts one more (empty) line" % grew, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
