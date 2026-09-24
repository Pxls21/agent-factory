#!/usr/bin/env python3
"""jev_locate: give it a bug, get the files, lines and records to read (task #227; D-072 item 4; the brief
tasks/briefs/jev-laya/JT2-brief.md, D-5).

  jev_locate.py "<bug text>" [--from-file PATH] [--in PATH] [--top K] [--budget N] [--json]
                [--root DIR] [--instruments LIST] [--order lexical|unranked|jev] [--jev-url URL] [--jev-timeout S]
                [--no-jev-log]

The bug text can be an error trace, a failing test's output or a sentence; --from-file reads it (its last 4,000
characters when larger). Every code-intel instrument runs (scripts/jev_context.py: graft, GitNexus, codebase-memory,
code-review-graph, rg, the registry rows, the CLAUDE.md quirk lines, git log -S), and the pack names the top K items
and the files to read, under --budget characters (default 6,000; hard cap 9,000). --in scopes graft and rg to one path.
The order is `lexical` by default (D-077: in the A3 benchmark Jev did not beat the plain order); `--order jev` is opt-in
and lets Jev reorder the lexical selection, never drop from it (KC-J5); `--order unranked` is D-3's agreement-first
order. Jev is asked only on the local endpoint (or the loopback --jev-url).

Advisory only (KC-J1, KC-J1b): the pack is a lead for the model, never a verdict. Exit 0 with a pack whenever the
input is usable, even with every instrument unmapped and Jev down; 64 on a usage error (one stderr line). The wall
time goes to one stderr line, never into the pack (the pack is deterministic for fixed instrument outputs).
"""
import argparse
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import jev_context as jc  # noqa: E402

FROM_FILE_CHARS = 4000


class Usage(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Usage(message)


def parse_instruments(value, known):
    names = [n.strip() for n in value.split(",") if n.strip()]
    bad = [n for n in names if n not in known]
    if not names or bad:
        raise Usage("--instruments takes a comma list of %s (got %r)" % (", ".join(known), value))
    return names


def check_budget(budget):
    if budget < jc.BUDGET_MIN:
        raise Usage("--budget must be at least %d characters" % jc.BUDGET_MIN)
    return jc.clamp_budget(budget)


def check_top(top):
    if not 1 <= top <= jc.MAX_JEV_CHUNKS:
        raise Usage("--top must be 1-%d" % jc.MAX_JEV_CHUNKS)
    return top


def rank_chunks(order, query, chunks, top, a, instructions=None, what="chunks"):
    """-> (base mode, scores or None, the ranking line). A base order never asks Jev. `jev` asks it for the base's
    top chunks first (so every item the pack can show is scored) and may only reorder them (KC-J5)."""
    if order != "jev":
        return order, None, "ranking: %s order (%s), Jev not asked" % (
            order, "instrument agreement, then lexical overlap" if order == "unranked" else "lexical overlap")
    base = jc.JEV_BASE
    if not chunks:
        return base, None, "Jev not asked: no %s to rank (unranked)" % what
    protect = jc.order_base(chunks, base)[:top]
    scores, reason, sent = jc.jev_rank(query, chunks, instructions=instructions, url=a.jev_url,
                                       timeout=a.jev_timeout, log=not a.no_jev_log, protect=protect)
    if scores is None:
        return base, None, "Jev unavailable: %s (unranked)" % reason
    return base, scores, ("ranking: Jev reorders the %s order's selection (KC-J5: it never drops an item); %d of %d "
                          "%s scored, one noul each" % (base, len(scores), len(chunks), what))


def read_question(a):
    if (a.text is None) == (a.from_file is None):
        raise Usage("give the bug text OR --from-file, exactly one")
    if a.from_file is not None:
        try:
            with open(a.from_file, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as e:
            raise Usage("cannot read --from-file %s: %s" % (a.from_file, e.strerror))
        # The WHOLE file is scrubbed before the cut: a raw cut can leave a value whose name it removed, which no later
        # scrub recognizes (VERIFY-JT2-R1 F-16, F-17; AF-AP-193). Without the scrubber nothing is sent to Jev, and the
        # lexical order reads the raw tail as before.
        fitted = jc.fit_scrubbed(text, FROM_FILE_CHARS, "tail")
        text = fitted if fitted is not None else text[-FROM_FILE_CHARS:]
    else:
        text = a.text
    if not text.strip():
        raise Usage("the bug text is empty")
    return text


def main(argv=None):
    ap = _Parser(prog="jev_locate.py", description=__doc__.splitlines()[0])
    ap.add_argument("text", nargs="?")
    ap.add_argument("--from-file")
    ap.add_argument("--in", dest="scope")
    ap.add_argument("--top", type=int, default=jc.TOP_DEFAULT)
    ap.add_argument("--budget", type=int, default=jc.BUDGET_DEFAULT)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=jc.ROOT)
    ap.add_argument("--instruments", default=",".join(jc.INSTRUMENTS))
    ap.add_argument("--order", choices=jc.ORDERS, default=jc.DEFAULT_ORDER,
                    help="the pack's order (default %s, D-077); jev asks the local endpoint and only reorders the "
                         "%s selection" % (jc.DEFAULT_ORDER, jc.JEV_BASE))
    ap.add_argument("--jev-url", help="pin one loopback endpoint (tests); default: the local endpoint")
    ap.add_argument("--jev-timeout", type=float, default=jc.JEV_TIMEOUT)
    ap.add_argument("--no-jev-log", action="store_true", help="no line in jev.py's call log")
    t0 = time.monotonic()
    try:
        a = ap.parse_args(argv)
        top = check_top(a.top)
        budget, budget_note = check_budget(a.budget)
        instruments = parse_instruments(a.instruments, jc.INSTRUMENTS)
        root = os.path.abspath(a.root)
        if not os.path.isdir(root):
            raise Usage("--root %s is not a directory" % a.root)
        if a.scope is not None:
            scope = os.path.relpath(os.path.abspath(os.path.join(root, a.scope)), root)
            if scope.startswith("..") or not os.path.exists(os.path.join(root, scope)):
                raise Usage("--in %s is not a path inside the root" % a.scope)
            a.scope = scope
        if not (a.jev_timeout > 0):
            raise Usage("--jev-timeout must be above 0")
        question = read_question(a)
    except Usage as e:
        sys.stderr.write("jev_locate: usage: %s\n" % e)
        return 64
    ctx = jc.Context(root, jc.default_tools(os.path.expanduser("~")), scope=a.scope)
    hits, notes, answered = jc.collect(question, ctx, instruments)
    chunks = jc.merge(hits, jc.words(question))
    mode, scores, rank = rank_chunks(a.order, question, chunks, top, a)
    pack = jc.build_pack("jev locate", [("question", question)], chunks, mode, scores, rank, answered, notes,
                         extra=[budget_note] if budget_note else [])
    sys.stdout.write(jc.render(pack, top, budget, a.json))
    sys.stderr.write("jev_locate: %d hits, %d chunks, %d ranked by Jev, %d of %d instruments answered, wall %.1f s\n"
                     % (len(hits), len(chunks), len(scores or {}), len(answered), len(instruments),
                        time.monotonic() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
