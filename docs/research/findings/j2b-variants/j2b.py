#!/usr/bin/env python3
"""J2b: POST-HOC interface variants for Laya on the two J2 samples (task #226 follow-up, 2026-09-24).

J2 asked Laya one way per type and it failed both (`docs/research/findings/J2-SIGNAL-PROBE-2026-09-24.md`). The owner's
question is whether the model or the question is at fault. These variants were chosen AFTER seeing J2's results, so a
win here is a hypothesis, to be re-confirmed on rows the J2 samples never used; it is not a pre-registered result.

  ap_choice      one native `choice` question over the lexical 16 (criteria = row id -> the start of the row's text)
  v1_choice_rich one `choice` question, the state keyed as a finding, fuller class definitions
  v1_blocking    one `noul` question: is this finding blocking? (threshold 0.5) -> the blocking split and BLOCKER recall

  j2b.py --url http://127.0.0.1:47412 [--only ap_choice,v1_choice_rich,v1_blocking] [--out results.json]
"""
import argparse
import collections
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
FINDINGS = HERE.parent
STOP = set("the a an and or to of in on for is it that this with by as at be are was from its not no any every one two into "
           "than then when where which who what how why".split())
CLASSES_RICH = {
    "BLOCKER": "The finding breaks the frozen contract, the verifier reproduced it through the real production path, and it "
               "materially changes the result, so the landing must not merge until it is fixed.",
    "FOLLOW-UP": "A real defect, gap or missing test that should be fixed in a later change; the landing can merge meanwhile.",
    "INFO": "An observation, a measurement or a confirmation that something works; it names no defect.",
    "UNVERIFIED": "A suspicion the verifier could not reproduce or did not run.",
    "CONTRACT-DEFECT": "The contract or the brief is itself wrong, contradicts the code, or cannot be met as written.",
    "KNOWN": "An issue that was already recorded before this verify (a known limitation, an existing ticket).",
}
BLOCKING = {"BLOCKER", "CONTRACT-DEFECT"}


def tokens(text):
    return {w for w in re.findall(r"[a-z0-9_]{3,}", text.lower()) if w not in STOP}


def post(url, body):
    req = urllib.request.Request(url + "/v1/systemone", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())


def ap_choice(url):
    data = json.loads((FINDINGS / "ap-hawk-probe" / "sample.json").read_text(encoding="utf-8"))
    rows, sample = data["rows"], data["sample"]
    rt = {k: tokens(v) for k, v in rows.items()}
    hit1 = hit3 = in16 = 0
    for s in sample:
        q = tokens(s["state"])
        lex = sorted(rows, key=lambda r: (-len(q & rt[r]), int(r.split("-")[-1])))[:16]
        labels = set(s["labels"])
        in16 += bool(labels & set(lex))
        out = post(url, {"model": "laya", "state": {"incident": s["state"]}, "questions": {"q": {
            "type": "choice", "instructions": "Which anti-pattern row does this incident show?",
            "criteria": {r: rows[r][:260] for r in lex}}}})
        a = out["answers"]["q"]
        probs = a.get("probabilities") or {}
        top3 = sorted(probs, key=lambda k: -probs[k])[:3] if probs else [a["choice"]]
        hit1 += a["choice"] in labels
        hit3 += bool(labels & set(top3))
    n = len(sample)
    return {"n": n, "top1": round(hit1 / n, 4), "top3": round(hit3 / n, 4), "recall_at_16": round(in16 / n, 4)}


def _v1_sample():
    return json.loads((FINDINGS / "j2-v1-probe" / "sample.json").read_text(encoding="utf-8"))["sample"]


def v1_choice_rich(url):
    sample = _v1_sample()
    per = collections.defaultdict(lambda: [0, 0])
    hits = block = 0
    for s in sample:
        out = post(url, {"model": "laya", "state": {"finding": s["state"]}, "questions": {"q": {
            "type": "choice", "instructions": "An adversarial verifier wrote this finding. Which class did it assign?",
            "criteria": CLASSES_RICH}}})
        p = out["answers"]["q"]["choice"]
        per[s["label"]][1] += 1
        per[s["label"]][0] += p == s["label"]
        hits += p == s["label"]
        block += (p in BLOCKING) == (s["label"] in BLOCKING)
    n = len(sample)
    return {"n": n, "accuracy": round(hits / n, 4), "balanced_accuracy": round(sum(h / c for h, c in per.values()) / len(per), 4),
            "blocking_split": round(block / n, 4), "per_class_recall": {k: f"{h}/{c}" for k, (h, c) in sorted(per.items())}}


def v1_blocking(url):
    sample = _v1_sample()
    tp = fp = fn = tn = 0
    for s in sample:
        out = post(url, {"model": "laya", "state": {"finding": s["state"]}, "questions": {"q": {
            "type": "noul", "instructions": "Does this finding block the merge: a contract break the verifier reproduced "
                                            "through the real path, or a contract that is itself wrong?"}}})
        yes = out["answers"]["q"]["noul"] >= 0.5
        gold = s["label"] in BLOCKING
        tp += yes and gold
        fp += yes and not gold
        fn += (not yes) and gold
        tn += (not yes) and not gold
    n = len(sample)
    return {"n": n, "blocking_split": round((tp + tn) / n, 4), "blocking_recall": f"{tp}/{tp + fn}",
            "false_alarms": f"{fp}/{fp + tn}"}


VARIANTS = {"ap_choice": ap_choice, "v1_choice_rich": v1_choice_rich, "v1_blocking": v1_blocking}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", default="http://127.0.0.1:47412")
    ap.add_argument("--only", default=",".join(VARIANTS))
    ap.add_argument("--out", default=str(HERE / "results.json"))
    args = ap.parse_args(argv)
    results = {}
    for name in args.only.split(","):
        t0 = time.time()
        results[name] = VARIANTS[name](args.url)
        results[name]["seconds"] = round(time.time() - t0, 1)
        print(name, json.dumps(results[name]), flush=True)
    Path(args.out).write_text(json.dumps(results, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
