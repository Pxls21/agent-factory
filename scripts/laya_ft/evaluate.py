#!/usr/bin/env python3
"""Evaluate Laya (the base model, or the base plus a train.py checkpoint) on the held-out J2 samples with J2's own scorers
(task #233; brief FT1 D-8).

  <laya venv>/bin/python scripts/laya_ft/evaluate.py [--checkpoint PATH] [--only v1,v1_full,ap,...] [--out-dir DIR]
      [--model-dir DIR] [--device cpu|cuda] [--threads N]

The model loads in this process (laya.load; a checkpoint's tensors are loaded over it). The committed J2 scorers run
UNCHANGED, as openjev_j2.py reran them against OpenJev: v1_probe.py `cmd_score` on the J2 sample (titles, run `v1`) and on
the J2c sample (whole findings, run `v1_full`), ap_probe.py `cmd_score` on the AP sample (run `ap`); only their `post` is
swapped, for an in-process call of the local server's own `_answer` (scripts/laya_systemone_server.py: one system_one
call, or one per chunk when every question id names a chunk, which is what J2 scored). So the metrics are J2's: accuracy,
balanced accuracy, blocking split and per-class recall (BLOCKER recall is its BLOCKER entry) for v1 and v1_full, top-1 and
top-3 over the lexical 16 for ap, beside the baselines those scorers compute (majority, heuristic, lexical). Added beside
them: the KC-J3 verdict line, the committed base numbers, the rows that agree with the committed base predictions, and
laya.common.ece_score over the answers as served (with the checkpoint config's temperatures; confidence = the chosen
option's probability). `v1_blocking` and `v1_full_blocking` score the trained D-6(b) question (threshold 0.5), which J2
never asked in this form, so they have no committed base number. With NO checkpoint the run is its own positive control:
every number of v1, v1_full and ap must equal the committed J2, J2c and AP results (exit 2 otherwise). A served
probability that is not a finite float refuses the evaluation (exit 5) instead of being scored, and train.load_checkpoint
refuses a checkpoint with a non-finite tensor (VERIFY-FT1 F-1).
"""
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # scripts/: the laya_ft package
from laya_ft import common as C  # noqa: E402

J2_RUNS = {   # run -> (sample, committed results), repo-relative under docs/research/findings
    "v1": ("j2-v1-probe/sample.json", "j2-v1-probe/results.json"),
    "v1_full": ("j2c-fulltext/sample.json", "j2c-fulltext/results.json"),
    "ap": ("ap-hawk-probe/sample.json", "ap-hawk-probe/results.json"),
}
BLOCKING_RUNS = {"v1_blocking": "j2-v1-probe/sample.json", "v1_full_blocking": "j2c-fulltext/sample.json"}
ALL_RUNS = tuple(J2_RUNS) + tuple(BLOCKING_RUNS)
LAYA_V1 = ("jev_choice", "jev_noul")


class NonFiniteAnswer(Exception):
    """A served probability that is not a finite float: the evaluation is refused (exit 5), nothing is scored."""


def check_served(out):
    """Refuse (NonFiniteAnswer) a served answer whose probabilities (a choice's or a score's `probabilities`, a noul's
    `noul`) are not all finite floats. VERIFY-FT1 F-1: J2's scorers counted a NaN checkpoint's answers, every prediction
    BLOCKER with ECE 0.0. -> out"""
    for qid, a in (out.get("answers") or {}).items():
        for v in list((a.get("probabilities") or {}).values()) + ([a["noul"]] if "noul" in a else []):
            if not (isinstance(v, float) and math.isfinite(v)):
                raise NonFiniteAnswer("answer %r serves the probability %r, not a finite float" % (qid, v))
    return out


def compare(run, mine, committed):
    """Every number of a J2 run that differs from the committed result: [] means reproduced."""
    diffs = []
    if run == "ap":
        pairs = [("rates.%s" % k, mine["rates"].get(k), v) for k, v in sorted(committed["rates"].items())]
    else:
        pairs = [("methods.%s.%s" % (m, k), mine["methods"].get(m, {}).get(k), v)
                 for m in sorted(committed["methods"]) for k, v in sorted(committed["methods"][m].items())]
    pairs.append(("n", mine.get("n"), committed.get("n")))
    for name, got, want in pairs:
        if got != want:
            diffs.append("%s.%s: %r, committed %r" % (run, name, got, want))
    return diffs


def agreement(run, mine, committed):
    """Rows whose Laya prediction equals the committed base prediction (the committed files carry them per row)."""
    if run == "ap":
        pairs = list(zip(mine["per_sample"], committed["per_sample"]))
        return {"jev_top3": "%d/%d" % (sum(a["jev"] == b["jev"] for a, b in pairs), len(pairs))}
    pairs = list(zip(mine["predictions"], committed["predictions"]))
    return {m: "%d/%d" % (sum(a[m] == b[m] for a, b in pairs), len(pairs)) for m in LAYA_V1}


def kc_j3(run, res):
    """KC-J3 (docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md): at or under max(majority, heuristic) rejects the type;
    for ap the plain baselines are the majority and the lexical order."""
    if run == "ap":
        r = res["rates"]
        bar = max(r["majority@1"], r["lexical@1"])
        return ["KC-J3 ap: Laya top-1 %.4f vs max(majority %.4f, lexical %.4f) = %.4f -> %s" % (
            r["jev@1"], r["majority@1"], r["lexical@1"], bar, "REJECTED (at or under)" if r["jev@1"] <= bar else
            "PASSES (above)")]
    m = res["methods"]
    bar = max(m["majority"]["accuracy"], m["heuristic"]["accuracy"])
    return ["KC-J3 %s %s: accuracy %.4f vs max(majority %.4f, heuristic %.4f) = %.4f -> %s" % (
        run, meth, m[meth]["accuracy"], m["majority"]["accuracy"], m["heuristic"]["accuracy"], bar,
        "REJECTED (at or under)" if m[meth]["accuracy"] <= bar else "PASSES (above)") for meth in LAYA_V1]


def blocking_metrics(preds, gold):
    """J2b's v1_blocking shape: the split, blocking recall and false alarms, from p(true) >= 0.5."""
    tp = sum(p and g for p, g in zip(preds, gold))
    fp = sum(p and not g for p, g in zip(preds, gold))
    fn = sum(g and not p for p, g in zip(preds, gold))
    tn = sum(not p and not g for p, g in zip(preds, gold))
    n = len(gold)
    return {"n": n, "blocking_split": round((tp + tn) / n, 4), "blocking_recall": "%d/%d" % (tp, tp + fn),
            "false_alarms": "%d/%d" % (fp, fp + tn), "never_baseline_split": round((fp + tn) / n, 4)}


def ece_of(calls, run, sample):
    """ece_score over the served answers: v1 `choice` (confidence = the chosen option's probability, correct = the
    verifier's class), ap per-row noul (confidence = max(p, 1 - p), correct = (p >= 0.5) == the row is a label)."""
    import numpy as np
    from laya.common import ece_score
    conf, correct = [], []
    if run == "ap":
        if len(calls) != len(sample):
            raise AssertionError("%d calls for %d ap rows" % (len(calls), len(sample)))
        for (_body, out), s in zip(calls, sample):
            for rid, a in out["answers"].items():
                p = a["noul"]
                conf.append(max(p, 1 - p))
                correct.append(float((p >= 0.5) == (rid in s["labels"])))
    else:
        choice_calls = [out for body, out in calls if list(body["questions"]) == ["q"]]
        if len(choice_calls) != len(sample):
            raise AssertionError("%d choice calls for %d v1 rows" % (len(choice_calls), len(sample)))
        for out, s in zip(choice_calls, sample):
            a = out["answers"]["q"]
            conf.append(a["probabilities"][a["choice"]])
            correct.append(float(a["choice"] == s["label"]))
    return round(ece_score(np.array(conf, dtype=float), np.array(correct, dtype=float)), 4)


def main(argv=None):
    try:
        return _main(argv)
    except NonFiniteAnswer as e:
        print("evaluate: refused: NonFiniteAnswer: %s: nothing is scored" % e, file=sys.stderr)
        return 5


def _main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--checkpoint", default=None, help="a train.py checkpoint.pt; none = the base model")
    ap.add_argument("--only", default="v1,v1_full,ap", help="runs, from %s" % ",".join(ALL_RUNS))
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--model-dir", default=C.DEFAULT_MODEL_DIR)
    ap.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    ap.add_argument("--threads", type=int, default=None)
    args = ap.parse_args(argv)
    runs = [r for r in args.only.split(",") if r]
    if not runs or set(runs) - set(ALL_RUNS):
        ap.error("--only takes %s" % ",".join(ALL_RUNS))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    import torch
    from laya_ft import train as T
    if args.threads:
        torch.set_num_threads(args.threads)
    if args.device == "cuda" and not torch.cuda.is_available():
        print("evaluate: --device cuda but CUDA is unavailable", file=sys.stderr)
        return 64
    t0 = time.time()
    agent = T.load_base(Path(args.model_dir), args.device)
    ckpt = None
    if args.checkpoint:
        tensors, prefixes = T.load_checkpoint(agent.model, args.checkpoint)
        ckpt = {"file": str(Path(args.checkpoint).resolve()), "sha256": C.sha256_file(args.checkpoint),
                "tensors": tensors, "prefixes": prefixes}
    server = C.load_module("laya_ft_server", C.ROOT / "scripts" / "laya_systemone_server.py")
    server.State.agent = agent
    calls = []

    def post(url, body, timeout=600):   # the J2 scorers' post, in process: the server's own fan-out, no socket
        out = check_served(server._answer(body["state"], body["questions"]))   # a non-finite answer is never scored
        calls.append((body, out))
        return out

    C.V1.post = post
    C.AP.post = post
    summary = {"checkpoint": ckpt, "model_dir": str(Path(args.model_dir).resolve()), "device": str(agent.device),
               "threads": torch.get_num_threads(), "runs": {}}
    failures = []
    for run in runs:
        calls.clear()
        t_run = time.time()
        if run in J2_RUNS:
            sample_rel, committed_rel = J2_RUNS[run]
            sample_path, res_path = C.FINDINGS / sample_rel, out_dir / ("%s.json" % run)
            ns = argparse.Namespace(sample=str(sample_path), url="in-process", out=str(res_path))
            (C.AP if run == "ap" else C.V1).cmd_score(ns)
            mine = json.loads(res_path.read_text(encoding="utf-8"))
            committed = json.loads((C.FINDINGS / committed_rel).read_text(encoding="utf-8"))
            sample = json.loads(sample_path.read_text(encoding="utf-8"))["sample"]
            entry = {"result_file": str(res_path), "kc_j3": kc_j3(run, mine), "ece": ece_of(calls, run, sample),
                     "committed_base": committed.get("rates") if run == "ap" else
                     {m: committed["methods"][m] for m in LAYA_V1},
                     "agreement_with_committed_base": agreement(run, mine, committed),
                     "differences_from_committed_base": compare(run, mine, committed)}
            if args.checkpoint is None:
                failures += entry["differences_from_committed_base"]
        else:
            sample = json.loads((C.FINDINGS / BLOCKING_RUNS[run]).read_text(encoding="utf-8"))["sample"]
            q = C.QUESTIONS["v1.blocking"]
            ps = [post("in-process", {"state": s["state"], "questions": {"v1.blocking": q}})["answers"]["v1.blocking"]["noul"]
                  for s in sample]
            gold = [s["label"] in C.V1.BLOCKING for s in sample]
            preds = [p >= 0.5 for p in ps]
            import numpy as np
            from laya.common import ece_score
            entry = dict(blocking_metrics(preds, gold), ece=round(ece_score(
                np.array([max(p, 1 - p) for p in ps]), np.array([float(a == b) for a, b in zip(preds, gold)])), 4),
                committed_base=None)
        entry["seconds"] = round(time.time() - t_run, 1)
        summary["runs"][run] = entry
        print("== %s (%.0f s) ==" % (run, entry["seconds"]), flush=True)
        for line in entry.get("kc_j3", []):
            print(line, flush=True)
        print(json.dumps({k: v for k, v in entry.items() if k not in ("kc_j3", "result_file")}, sort_keys=True),
              flush=True)
    summary["wall_seconds"] = round(time.time() - t0, 1)
    if args.checkpoint is None:
        summary["positive_control"] = "FAIL" if failures else "PASS"
        print("POSITIVE CONTROL (no checkpoint): %s%s" % (summary["positive_control"],
              "" if not failures else " - " + "; ".join(failures[:8])), flush=True)
    (out_dir / "evaluate-summary.json").write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n",
                                                   encoding="utf-8")
    return 2 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
