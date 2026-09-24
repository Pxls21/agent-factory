#!/usr/bin/env python3
"""J2b comparator: a general model (Haiku 4.5) on the SAME two J2 samples, to split "the model" from "the task".

POST-HOC like `j2b.py`. The comparator saw label-free inputs only (built by `inputs`); its answers are recorded data
(`haiku_ap.json`, `haiku_v1.json`, one run, 2026-09-24), scored here against the committed samples' labels.

  haiku_compare.py inputs --out DIR      # writes DIR/ap_inputs.json and DIR/v1_inputs.json (no labels, deterministic)
  haiku_compare.py score [--ap F] [--v1 F]
"""
import argparse
import collections
import json
import sys
from pathlib import Path

from j2b import BLOCKING, tokens

HERE = Path(__file__).resolve().parent
FINDINGS = HERE.parent


def _ap():
    data = json.loads((FINDINGS / "ap-hawk-probe" / "sample.json").read_text(encoding="utf-8"))
    rows = data["rows"]
    rt = {k: tokens(v) for k, v in rows.items()}
    out = []
    for s in data["sample"]:
        q = tokens(s["state"])
        lex = sorted(rows, key=lambda r: (-len(q & rt[r]), int(r.split("-")[-1])))[:16]
        out.append((s, lex, rows))
    return out


def _v1():
    return json.loads((FINDINGS / "j2-v1-probe" / "sample.json").read_text(encoding="utf-8"))["sample"]


def cmd_inputs(args):
    d = Path(args.out)
    d.mkdir(parents=True, exist_ok=True)
    ap = [{"id": i, "incident": s["state"], "candidates": [{"row": r, "text": rows[r][:260]} for r in lex]}
          for i, (s, lex, rows) in enumerate(_ap())]
    v1 = [{"id": i, "finding": s["state"]} for i, s in enumerate(_v1())]
    (d / "ap_inputs.json").write_text(json.dumps(ap, ensure_ascii=False) + "\n", encoding="utf-8")
    (d / "v1_inputs.json").write_text(json.dumps(v1, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


def cmd_score(args):
    pa = json.loads(Path(args.ap).read_text(encoding="utf-8"))
    hit1 = hit3 = lex1 = dev = dev_model = dev_lex = 0
    items = _ap()
    for i, (s, lex, _rows) in enumerate(items):
        labels, p = set(s["labels"]), pa[str(i)]
        hit1 += p["top1"] in labels
        hit3 += bool(labels & set(p["top3"][:3]))
        lex1 += lex[0] in labels
        if p["top1"] != lex[0]:
            dev += 1
            dev_model += p["top1"] in labels
            dev_lex += lex[0] in labels
    n = len(items)
    print("ap", json.dumps({"n": n, "top1": round(hit1 / n, 4), "top3": round(hit3 / n, 4), "lexical_top1": round(lex1 / n, 4),
                            "departs_from_lexical_top1": dev, "right_when_departing": dev_model,
                            "lexical_right_there": dev_lex}))
    pv = json.loads(Path(args.v1).read_text(encoding="utf-8"))
    per = collections.defaultdict(lambda: [0, 0])
    hits = split = tp = fn = fp = tn = 0
    sample = _v1()
    for i, s in enumerate(sample):
        p, g = pv[str(i)], s["label"]
        per[g][1] += 1
        per[g][0] += p == g
        hits += p == g
        split += (p in BLOCKING) == (g in BLOCKING)
        tp += p in BLOCKING and g in BLOCKING
        fn += p not in BLOCKING and g in BLOCKING
        fp += p in BLOCKING and g not in BLOCKING
        tn += p not in BLOCKING and g not in BLOCKING
    n = len(sample)
    print("v1", json.dumps({"n": n, "accuracy": round(hits / n, 4),
                            "balanced_accuracy": round(sum(h / c for h, c in per.values()) / len(per), 4),
                            "blocking_split": round(split / n, 4), "blocking_recall": f"{tp}/{tp + fn}",
                            "false_alarms": f"{fp}/{fp + tn}",
                            "per_class_recall": {k: f"{h}/{c}" for k, (h, c) in sorted(per.items())}}))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("inputs")
    i.add_argument("--out", required=True)
    s = sub.add_parser("score")
    s.add_argument("--ap", default=str(HERE / "haiku_ap.json"))
    s.add_argument("--v1", default=str(HERE / "haiku_v1.json"))
    args = ap.parse_args(argv)
    return cmd_inputs(args) if args.cmd == "inputs" else cmd_score(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
