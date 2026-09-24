#!/usr/bin/env python3
"""The AP-hawk signal probe (task #221 step 3; J2's shape on the question type that has labels).

Question: given an incident heading with its AF-AP ids masked, does Jev (the local Laya endpoint) pick the registry row
the coordinator named, better than the baselines? This is a PROXY for the AP-hawk (whose real input is a code hunk,
which has no labels): an incident heading is the coordinator's own summary and often repeats the row's words.

  ap_probe.py sample [--out sample.json]      parse the incident log; write the sample; print its sha256
  ap_probe.py score --sample sample.json [--url http://127.0.0.1:47411] [--out results.json]

The sample is written and its digest committed BEFORE any scoring (the council's J2 rule). Scoring: the lexical stage
ranks every registry row by token overlap with the masked heading and keeps the top 16; Jev scores those 16 with one
`noul` question per row (the server's per-chunk fan-out). Printed side by side: majority class, random within 16,
lexical top-1/top-3, Jev top-1/top-3, and the lexical stage's recall at 16 (the ceiling for any reranker). Advisory
measurement only: nothing here feeds a gate (KC-J1).
"""
import argparse
import collections
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LOG = ROOT / "docs" / "INCIDENT-LOG.md"
ANCHOR = re.compile(r"^(?:- )?\*\*\d{4}-\d{2}-\d{2}\b")   # decide-harvest's INCIDENT_ANCHOR_RE
AP_ID = re.compile(r"\bAF-AP-(\d+)\b")
ROW = re.compile(r"^\|\s*AF-AP-(\d+)\s*\|")
STOP = set("the a an and or to of in on for is it that this with by as at be are was from its not no any every one "
           "two into than then when where which who what how why".split())
TOP_K = 16
INSTRUCTION = "Does this incident show this anti-pattern?"


def tokens(text):
    return {w for w in re.findall(r"[a-z0-9_]{3,}", text.lower()) if w not in STOP}


def registry(lines):
    rows = {}
    for line in lines:
        m = ROW.match(line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        rows["AF-AP-" + m.group(1)] = " ".join(cells[1:3])[:400]
    return rows


def heading(lines, start):
    first = lines[start]
    opening = first.find("**")
    pieces = []
    for offset in range(10):
        if start + offset >= len(lines):
            break
        piece = first[opening + 2:] if offset == 0 else lines[start + offset]
        close = piece.find("**")
        if close >= 0:
            return " ".join(" ".join(pieces + [piece[:close]]).split())
        pieces.append(piece)
    return None


def cmd_sample(args):
    lines = LOG.read_text(encoding="utf-8").splitlines()
    rows = registry(lines)
    sample = []
    for i, line in enumerate(lines):
        if not ANCHOR.match(line):
            continue
        h = heading(lines, i)
        if not h:
            continue
        ids = sorted({"AF-AP-" + n for n in AP_ID.findall(h)} & set(rows), key=lambda s: int(s.split("-")[-1]))
        if ids:
            sample.append({"line": i + 1, "labels": ids, "state": AP_ID.sub("AF-AP-?", h)})
    body = json.dumps({"rows": rows, "sample": sample}, sort_keys=True, ensure_ascii=False, indent=1)
    Path(args.out).write_text(body + "\n", encoding="utf-8")
    print(f"sample: {len(sample)} headings naming {len({l for s in sample for l in s['labels']})} rows; "
          f"registry {len(rows)} rows; sha256 {hashlib.sha256((body + chr(10)).encode()).hexdigest()}")
    return 0


def post(url, body, timeout=600):
    req = urllib.request.Request(url + "/v1/systemone", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def cmd_score(args):
    data = json.loads(Path(args.sample).read_text(encoding="utf-8"))
    rows, sample = data["rows"], data["sample"]
    row_tok = {rid: tokens(text) for rid, text in rows.items()}
    counts = collections.Counter(l for s in sample for l in s["labels"])
    majority = counts.most_common(1)[0][0]
    hit = collections.Counter()
    per = []
    t0 = time.time()
    for n, s in enumerate(sample, 1):
        q = tokens(s["state"])
        lex = sorted(rows, key=lambda rid: (-len(q & row_tok[rid]), int(rid.split("-")[-1])))[:TOP_K]
        labels = set(s["labels"])
        in16 = bool(labels & set(lex))
        body = {"model": "laya", "state": {"query": s["state"], "chunks": [{"id": rid, "text": rows[rid]} for rid in lex]},
                "questions": {rid: {"type": "noul", "instructions": INSTRUCTION} for rid in lex}}
        out = post(args.url, body)
        if out.get("fan_out") != len(lex):
            raise SystemExit(f"no per-chunk fan-out at sample {n}: fan_out={out.get('fan_out')!r}")
        score = {rid: out["answers"][rid]["noul"] for rid in lex}
        jev = sorted(lex, key=lambda rid: (-score[rid], int(rid.split("-")[-1])))
        hit["majority@1"] += majority in labels
        hit["lexical@1"] += lex[0] in labels
        hit["lexical@3"] += bool(labels & set(lex[:3]))
        hit["jev@1"] += jev[0] in labels
        hit["jev@3"] += bool(labels & set(jev[:3]))
        hit["recall@16"] += in16
        hit["random@1 (expected)"] += len(labels & set(lex)) / TOP_K
        per.append({"line": s["line"], "labels": s["labels"], "lexical": lex[:3], "jev": jev[:3],
                    "jev_scores": {rid: round(score[rid], 4) for rid in jev[:3]}})
        if n % 10 == 0:
            print(f"  {n}/{len(sample)} scored, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    total = len(sample)
    table = {k: round(v / total, 4) for k, v in sorted(hit.items())}
    result = {"n": total, "rows": len(rows), "top_k": TOP_K, "majority_label": majority, "rates": table,
              "seconds": round(time.time() - t0, 1), "per_sample": per}
    Path(args.out).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("n", "rows", "top_k", "majority_label", "rates", "seconds")}, indent=1))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--out", default=str(Path(__file__).with_name("sample.json")))
    c = sub.add_parser("score")
    c.add_argument("--sample", default=str(Path(__file__).with_name("sample.json")))
    c.add_argument("--url", default="http://127.0.0.1:47411")
    c.add_argument("--out", default=str(Path(__file__).with_name("results.json")))
    args = ap.parse_args(argv)
    return cmd_sample(args) if args.cmd == "sample" else cmd_score(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
