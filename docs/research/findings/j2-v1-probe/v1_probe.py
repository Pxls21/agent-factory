#!/usr/bin/env python3
"""J2 on `v1.finding_class` (D-072 item 1): does Jev (the local Laya endpoint) classify a verify finding like the verifier did?

  v1_probe.py sample --ledger LEDGER.jsonl [--out sample.json]   stratified sample from a real decide-harvest ledger
  v1_probe.py score --sample sample.json [--url http://127.0.0.1:47411] [--out results.json]

The ledger comes from `scripts/decide-harvest` run over the committed verify reports (the J1 capture plane); the label is
the verifier's own class. The sample keeps every row of the rare classes and fills the rest from INFO and FOLLOW-UP in
row-digest order (deterministic), 100 rows. The class words are masked in the state. The heuristic baseline below is
fixed BEFORE scoring and committed with the sample. Printed side by side: majority, heuristic, Jev `choice` (one native
question over the six classes) and Jev per-class `noul` (six chunks, one model call each, argmax); accuracy, balanced
accuracy (mean per-class recall) and the blocking split (BLOCKER or CONTRACT-DEFECT against the rest). Advisory
measurement only: KC-J1 and KC-J1b stand (a Jev score is never the sole evidence for a verifier's class).
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

CLASSES = {
    "BLOCKER": "meets the blocking predicate: it breaks the contract, is reproduced through the real path and matters",
    "FOLLOW-UP": "a real defect or gap that should be fixed later but does not block the merge",
    "INFO": "an observation or measurement with no defect in it",
    "UNVERIFIED": "a suspicion the verifier could not reproduce",
    "CONTRACT-DEFECT": "the contract or the brief itself is wrong or contradicts the tree",
    "KNOWN": "an issue already recorded before this verify",
}
BLOCKING = {"BLOCKER", "CONTRACT-DEFECT"}
MASK = re.compile(r"\b(BLOCKER|FOLLOW-UP|INFO|UNVERIFIED|CONTRACT-DEFECT|KNOWN|BLOCKING|NON-BLOCKING)\b", re.I)
N = 100
RULES = [  # the fixed heuristic baseline (first match wins); written before any score was seen
    ("UNVERIFIED", re.compile(r"not reproduced|could not|did not run|not run\b|unverified|cannot confirm", re.I)),
    ("CONTRACT-DEFECT", re.compile(r"\bcontract\b|the brief|brief says|premise", re.I)),
    ("KNOWN", re.compile(r"\bknown\b|already (recorded|filed|tracked)|pre-existing", re.I)),
    ("BLOCKER", re.compile(r"\bleak|\bblocks?\b|\bbypass|\bwrong\b|\bbroken\b|\bcrash|\bfails? open\b", re.I)),
    ("FOLLOW-UP", re.compile(r"\btest|\bmissing\b|\bgap\b|\bsurviv|\bmutant|\bshould\b|\bno guard\b|\bdrift", re.I)),
]


def heuristic(text):
    return next((label for label, rx in RULES if rx.search(text)), "INFO")


def cmd_sample(args):
    rows = [json.loads(line) for line in Path(args.ledger).read_text(encoding="utf-8").splitlines() if line.strip()]
    v1 = sorted((r for r in rows if r["question_id"] == "v1.finding_class"), key=lambda r: r["row_digest"])
    by = collections.defaultdict(list)
    for r in v1:
        by[r["incumbent_answer"]].append(r)
    rare = [r for c, rs in by.items() if c not in ("INFO", "FOLLOW-UP") for r in rs]
    left = N - len(rare)
    take = rare + by["INFO"][: left // 2] + by["FOLLOW-UP"][: left - left // 2]
    sample = [{"row_digest": r["row_digest"], "label": r["incumbent_answer"], "lane": r["state"].get("lane"),
               "state": MASK.sub("[CLASS]", str(r["state"].get("title", "")))} for r in sorted(take, key=lambda r: r["row_digest"])]
    body = json.dumps({"n_ledger_v1": len(v1), "sample": sample}, sort_keys=True, ensure_ascii=False, indent=1) + "\n"
    Path(args.out).write_text(body, encoding="utf-8")
    counts = collections.Counter(s["label"] for s in sample)
    print(f"sample: {len(sample)} of {len(v1)} v1 rows; {dict(sorted(counts.items()))}; sha256 {hashlib.sha256(body.encode()).hexdigest()}")
    return 0


def post(url, body):
    req = urllib.request.Request(url + "/v1/systemone", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def rates(pred, gold):
    per = collections.defaultdict(lambda: [0, 0])
    for p, g in zip(pred, gold):
        per[g][1] += 1
        per[g][0] += p == g
    acc = sum(p == g for p, g in zip(pred, gold)) / len(gold)
    bal = sum(h / n for h, n in per.values()) / len(per)
    block = sum((p in BLOCKING) == (g in BLOCKING) for p, g in zip(pred, gold)) / len(gold)
    return {"accuracy": round(acc, 4), "balanced_accuracy": round(bal, 4), "blocking_split": round(block, 4),
            "per_class_recall": {c: f"{h}/{n}" for c, (h, n) in sorted(per.items())}}


def cmd_score(args):
    data = json.loads(Path(args.sample).read_text(encoding="utf-8"))
    sample = data["sample"]
    gold = [s["label"] for s in sample]
    majority = collections.Counter(gold).most_common(1)[0][0]
    preds = {"majority": [majority] * len(sample), "heuristic": [heuristic(s["state"]) for s in sample],
             "jev_choice": [], "jev_noul": []}
    t0 = time.time()
    for n, s in enumerate(sample, 1):
        out = post(args.url, {"model": "laya", "state": s["state"], "questions": {"q": {
            "type": "choice", "instructions": "Which class did the verifier give this finding?", "criteria": CLASSES}}})
        preds["jev_choice"].append(out["answers"]["q"]["choice"])
        chunks = [{"id": c, "text": f"{c}: {d}"} for c, d in CLASSES.items()]
        out = post(args.url, {"model": "laya", "state": {"query": s["state"], "chunks": chunks},
                              "questions": {c: {"type": "noul", "instructions": "Does this class describe the finding?"} for c in CLASSES}})
        if out.get("fan_out") != len(CLASSES):
            raise SystemExit(f"no per-chunk fan-out at sample {n}: {out.get('fan_out')!r}")
        preds["jev_noul"].append(max(CLASSES, key=lambda c: (out["answers"][c]["noul"], c)))
        if n % 10 == 0:
            print(f"  {n}/{len(sample)} scored, {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
    result = {"n": len(sample), "majority_label": majority, "seconds": round(time.time() - t0, 1),
              "methods": {k: rates(v, gold) for k, v in preds.items()},
              "predictions": [{"row_digest": s["row_digest"], "label": g, **{k: v[i] for k, v in preds.items()}}
                              for i, (s, g) in enumerate(zip(sample, gold))]}
    Path(args.out).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("n", "majority_label", "seconds", "methods")}, indent=1))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--ledger", required=True)
    s.add_argument("--out", default=str(Path(__file__).with_name("sample.json")))
    c = sub.add_parser("score")
    c.add_argument("--sample", default=str(Path(__file__).with_name("sample.json")))
    c.add_argument("--url", default="http://127.0.0.1:47411")
    c.add_argument("--out", default=str(Path(__file__).with_name("results.json")))
    args = ap.parse_args(argv)
    return cmd_sample(args) if args.cmd == "sample" else cmd_score(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
