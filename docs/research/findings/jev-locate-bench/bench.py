#!/usr/bin/env python3
"""The JT2 retrospective benchmark (A3 of tasks/briefs/jev-laya/JT2-brief.md): does the bug locator put the files a past
fix touched into its "files to read" top 5, and does Jev's ranking help?

  bench.py select [--pin R]  writes cases.json from git history at PIN (deterministic); prints its sha256
                             (PIN db71586 was rewritten by push_clean into db34178 on origin, the SAME tree 8bc6616f;
                             `--pin db34178` reproduces the identical 20 cases, only the file's "pin" field differs)
  bench.py run [--limit N]   runs the cases not yet in results.jsonl (resumable; one JSON line per case)
  bench.py report            writes results.md from cases.json and results.jsonl
  bench.py rescore           recomputes every ordering from the saved chunks and scores (no instrument, no Jev)

CASES (fixed before any run; the case list is committed by digest): a commit in `git log PIN` whose message names
exactly ONE AF-AP id, that touches one or two production files (code under proofs/ spikes/ scripts/ src/ harness-ports/,
not a test, not a fixture) that all exist at PIN, and whose id has a registry row at PIN; per id the EARLIEST such commit;
the eligible ids sorted by number, 20 of them evenly spaced. INPUT: the row's mechanism cell (its second cell; the first
is the id), with the answer's own words removed: every AF-AP id, every commit id, and each target file's path, basename
and stem. TARGET: the commit's production files. CAVEAT: the tree searched is HEAD (plus the shared tree's uncommitted
edits), where every fix is already in.

ORDERINGS of the "files to read" list, all from ONE instrument pass and ONE Jev call per case:
  unranked     D-3's fallback: summed instrument agreement, then summed lexical overlap
  lexical      summed lexical overlap alone
  jev          D-3 as pinned: files by their chunks' summed Jev scores (the measure of Jev's signal; not a pack order,
               since it can drop what the base keeps: KC-J5)
  jev>unranked Jev reorders the unranked order's 10 displayed files (the pack's --order jev, KC-J5)
  jev>lexical  Jev reorders the lexical order's 10 displayed files
Jev scores the chunks jev_context.jev_rank sends: the unranked and the lexical top 12 first, then the lexical pre-filter,
at most 48 (a superset of what either pack order protects; each chunk is its own model call, so a score does not depend
on its batch).

METRICS per case: recall@5 = |targets in the top 5 files| / |targets|; hit@5 = any target there; MRR@10 = 1/rank of
the first target in the top 10 (0 if none).

DECISION RULE (pre-registered; the coordinator's note of 13:3xZ): the pack's default order is the one with the highest
mean recall@5 among {unranked, lexical, jev>unranked, jev>lexical}; ties by mean MRR@10; a remaining tie goes to the order
that does not call Jev. The `jev` column is reported, never chosen.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import jev_context as jc  # noqa: E402

PIN = "db71586"
N_CASES = 20
PROD_DIRS = ("proofs/", "spikes/", "scripts/", "src/", "harness-ports/")
CODE_EXT = (".py", ".sh", ".bash", ".js", ".cjs", ".mjs", ".ts", ".rs")
CASES = os.path.join(HERE, "cases.json")
RESULTS = os.path.join(HERE, "results.jsonl")
REPORT = os.path.join(HERE, "results.md")
ORDERS = ("unranked", "lexical", "jev", "jev>unranked", "jev>lexical")
CHOOSABLE = ("unranked", "lexical", "jev>unranked", "jev>lexical")
SHOWN = 10


def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True, check=True).stdout


def _shebang(path):
    try:
        return git("show", "%s:%s" % (PIN, path)).startswith("#!")
    except subprocess.CalledProcessError:
        return False


def is_prod(path):
    parts = path.split("/")
    if not path.startswith(PROD_DIRS) or "tests" in parts or "fixtures" in parts or parts[-1].startswith("test_"):
        return False
    ext = os.path.splitext(parts[-1])[1]
    return ext in CODE_EXT or (ext == "" and _shebang(path))


def exists_at_pin(path):
    """By ls-tree's OUTPUT, not an exit code (AF-AP-141: `cat-file -e` fails the same way when git cannot tell)."""
    return git("ls-tree", PIN, "--", path).strip() != ""


def registry_at_pin():
    rows = {}
    for i, ln in enumerate(git("show", "%s:docs/INCIDENT-LOG.md" % PIN).split("\n"), 1):
        m = re.match(r"^\| (AF-AP-\d+) \| (.*?) \|", ln)
        if m:
            rows[m.group(1)] = (i, m.group(2))
    return rows


def scrub_leaks(text, targets):
    """The input without the answer's own words: AF-AP ids, commit ids, each target's path, basename and stem."""
    removed = []

    def cut(pattern, t):
        nonlocal removed
        found = re.findall(pattern, t)
        removed += found
        return re.sub(pattern, " ", t)
    t = cut(r"AF-AP-\d+", text)
    t = cut(r"\b(?=[0-9a-f]*[0-9])(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b", t)
    for p in targets:
        base = p.rsplit("/", 1)[-1]
        stem = os.path.splitext(base)[0]
        for w in sorted({p, base, stem} - {""}, key=len, reverse=True):
            if len(w) >= 4:
                t = cut(r"(?<![\w./-])" + re.escape(w) + r"(?![\w-])", t)
    t = re.sub(r"`\s*`", " ", t)
    return " ".join(t.split()), removed


def select():
    if git("rev-parse", "--is-shallow-repository").strip() != "false":
        sys.exit("bench: a shallow clone cannot give the whole history; refusing to select")
    rows = registry_at_pin()
    out = git("log", "--format=%x00%H%x01%s%x01%B%x01", "--name-only", "-i", "-E", "--grep=AF-AP-[0-9]+", PIN)
    earliest = {}
    for rec in out.split("\x00")[1:]:
        sha, subject, body, names = rec.split("\x01")
        ids = sorted(set(re.findall(r"AF-AP-\d+", body)))
        if len(ids) != 1 or ids[0] not in rows:
            continue
        prod = sorted({f for f in names.split("\n") if f.strip() and is_prod(f.strip())})
        if not 1 <= len(prod) <= 2 or not all(exists_at_pin(f) for f in prod):
            continue
        earliest[ids[0]] = (sha, subject, prod)      # git log is newest first: the last write is the earliest
    ids = sorted(earliest, key=lambda i: int(i.split("-")[-1]))
    n = len(ids)
    picks = [ids[round(i * (n - 1) / (N_CASES - 1))] for i in range(N_CASES)] if n >= N_CASES else ids
    cases = []
    for aid in picks:
        sha, subject, prod = earliest[aid]
        line, cell = rows[aid]
        text, removed = scrub_leaks(cell, prod)
        cases.append({"id": aid, "commit": sha, "subject": subject, "targets": prod, "row_line": line,
                      "input": text, "leaks_removed": removed})
    doc = {"pin": PIN, "eligible_ids": n, "rule": "see bench.py's docstring", "cases": cases}
    data = json.dumps(doc, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    with open(CASES, "w", encoding="utf-8") as fh:
        fh.write(data)
    print("cases.json: %d cases of %d eligible ids; sha256 %s" % (len(cases), n,
                                                                   hashlib.sha256(data.encode()).hexdigest()))


def metrics(files, targets):
    top = [f for f in files][:SHOWN]
    hit5 = [f for f in top[:5] if f in targets]
    ranks = [i for i, f in enumerate(top, 1) if f in targets]
    return {"recall5": len(set(hit5)) / len(targets), "hit5": 1 if hit5 else 0, "mrr10": 1.0 / ranks[0] if ranks else 0.0}


def orderings(chunks, scores):
    """-> {order: [file paths, best first]} from saved chunks and Jev scores (None when Jev did not answer)."""
    out = {}
    for mode in ("unranked", "lexical"):
        out[mode] = [f["path"] for f in jc.files_to_read(jc.order_base(chunks, mode), mode, scores)]
    if scores is not None:
        out["jev"] = [f["path"] for f in jc.files_to_read(jc.order_ranked(chunks, scores), "jev", scores)]
        for mode in ("unranked", "lexical"):
            files = jc.files_to_read(jc.order_base(chunks, mode), mode, scores)[:SHOWN]
            out["jev>" + mode] = [f["path"] for f in jc.reorder(files, lambda f: f["score"] if f["scored"] else None)]
    return out


def run(limit):
    with open(CASES, encoding="utf-8") as fh:
        cases = json.load(fh)["cases"]
    done = set()
    if os.path.exists(RESULTS):
        with open(RESULTS, encoding="utf-8") as fh:
            done = {json.loads(ln)["id"] for ln in fh if ln.strip()}
    ctx = jc.Context(REPO, jc.default_tools(os.path.expanduser("~")))
    head = git("rev-parse", "--short", "HEAD").strip()
    dirty = len([x for x in git("status", "--short").split("\n") if x.strip()])
    todo = [c for c in cases if c["id"] not in done][:limit]
    for c in todo:
        t0 = time.monotonic()
        hits, notes, answered = jc.collect(c["input"], ctx)
        t1 = time.monotonic()
        chunks = jc.merge(hits, jc.words(c["input"]))
        protect = jc.order_base(chunks, "unranked")[:jc.TOP_DEFAULT]
        ids = {x["id"] for x in protect}
        protect += [x for x in jc.order_base(chunks, "lexical")[:jc.TOP_DEFAULT] if x["id"] not in ids]
        scores, reason, sent = jc.jev_rank(c["input"], chunks, protect=protect)
        t2 = time.monotonic()
        order = orderings(chunks, scores)
        row = {"id": c["id"], "head": head, "dirty_paths": dirty, "targets": c["targets"],
               "answered": answered, "notes": notes, "hits": len(hits), "chunks": len(chunks), "sent": len(sent),
               "jev_reason": reason, "instrument_s": round(t1 - t0, 1), "jev_s": round(t2 - t1, 1),
               "files": {k: v[:SHOWN] for k, v in order.items()},
               "metrics": {k: metrics(v, c["targets"]) for k, v in order.items()},
               "targets_anywhere": sorted(set(c["targets"]) & set(order["unranked"])),
               "chunk_table": [[x["id"], x["path"], x["line"], x["instruments"], x["lexical"], x["record"]]
                               for x in chunks],
               "scores": scores}
        with open(RESULTS, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
        m = row["metrics"]
        print("%-10s hits=%4d chunks=%3d sent=%2d inst=%5.1fs jev=%5.1fs %s | %s" % (
            c["id"], len(hits), len(chunks), len(sent), t1 - t0, t2 - t1, reason or "jev ok",
            " ".join("%s=%.2f" % (k, m[k]["recall5"]) for k in ORDERS if k in m)), flush=True)


def _rows():
    with open(RESULTS, encoding="utf-8") as fh:
        return [json.loads(ln) for ln in fh if ln.strip()]


def _chunks(row):
    return [{"id": i, "path": p, "line": ln, "instruments": inst, "agreement": len(inst), "lexical": lex, "record": rec,
             "text": ""} for i, p, ln, inst, lex, rec in row["chunk_table"]]


def rescore():
    """Every ordering recomputed from the saved chunks and scores by the CURRENT library (the A6 mutant 1 check)."""
    rows = _rows()
    for r in rows:
        r["metrics"] = {k: metrics(v, r["targets"]) for k, v in orderings(_chunks(r), r["scores"]).items()}
    summary(rows, sys.stdout)


def summary(rows, out):
    out.write("| order | cases | mean recall@5 | hit@5 | mean MRR@10 |\n|---|---|---|---|---|\n")
    means = {}
    for k in ORDERS:
        ms = [r["metrics"][k] for r in rows if k in r["metrics"]]
        if ms:
            means[k] = (sum(m["recall5"] for m in ms) / len(ms), sum(m["mrr10"] for m in ms) / len(ms))
            out.write("| %s | %d | %.3f | %d | %.3f |\n" % (k, len(ms), means[k][0], sum(m["hit5"] for m in ms),
                                                          means[k][1]))
    both = [r for r in rows if all(k in r["metrics"] for k in ORDERS)]
    if len(both) != len(rows):
        out.write("\nJev answered %d of %d cases; the Jev columns cover those only.\n" % (len(both), len(rows)))
    ranked = sorted((k for k in CHOOSABLE if k in means),
                    key=lambda k: (-round(means[k][0], 9), -round(means[k][1], 9), k.startswith("jev"), k))
    if ranked:
        out.write("\nDecision rule winner: **%s** (mean recall@5 %.3f, MRR@10 %.3f).\n"
                  % (ranked[0], means[ranked[0]][0], means[ranked[0]][1]))
    return ranked


def report():
    with open(CASES, encoding="utf-8") as fh:
        cases = {c["id"]: c for c in json.load(fh)["cases"]}
    rows = _rows()
    with open(REPORT, "w", encoding="utf-8") as out:
        out.write("# JT2 A3: the retrospective benchmark, results\n\nGenerated by `bench.py report` from `cases.json` and "
                  "`results.jsonl` (the method and the decision rule: bench.py's docstring). The tree searched is HEAD "
                  "plus the shared tree's uncommitted edits, where every fix is already in.\n\n## Summary\n\n")
        summary(rows, out)
        out.write("\n## Per case (recall@5; a dash = Jev did not answer)\n\n| id | targets | unranked | lexical | jev | "
                  "jev>unranked | jev>lexical | targets anywhere | Jev | instruments answered |\n"
                  "|---|---|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            m = r["metrics"]
            cell = lambda k: "%.2f" % m[k]["recall5"] if k in m else "-"
            out.write("| %s | %s | %s | %s | %s | %s | %s | %d of %d | %s | %s |\n" % (
                r["id"], ", ".join(r["targets"]), cell("unranked"), cell("lexical"), cell("jev"), cell("jev>unranked"),
                cell("jev>lexical"), len(r["targets_anywhere"]), len(r["targets"]),
                "ok" if r["scores"] is not None else (r["jev_reason"] or "")[:60], ", ".join(r["answered"])))
        out.write("\n## Inputs\n\n")
        for r in rows:
            out.write("- %s (%s): %s\n" % (r["id"], cases[r["id"]]["commit"][:7], cases[r["id"]]["input"]))


def main():
    global PIN
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=("select", "run", "report", "rescore"))
    ap.add_argument("--limit", type=int, default=N_CASES)
    ap.add_argument("--pin", default=PIN, help="the commit whose history select reads (default %s)" % PIN)
    a = ap.parse_args()
    PIN = a.pin
    {"select": select, "report": report, "rescore": rescore}.get(a.cmd, lambda: run(a.limit))()


if __name__ == "__main__":
    main()
