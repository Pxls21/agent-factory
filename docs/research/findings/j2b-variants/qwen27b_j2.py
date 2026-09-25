#!/usr/bin/env python3
"""The J2 probes, UNCHANGED, against the Qwen3.8-27B Jev adapter (D-079, task #241).

J2 section 3 set the rule for a new candidate: "these two samples and scripts rerun against it unchanged,
with the same baselines". This runner loads `ap_probe.py`, `v1_probe.py` and `j2b.py` as they are committed and
swaps only their `post`: the request goes to `http://127.0.0.1:47420/v1/systemone` (the Qwen adapter's wire,
D-5), which does the per-chunk fan-out server-side (the Laya server's form), so every question sees one chunk.
The adapter's policy is `examples_binary` (D-2's default, the oracle's own selection for this backbone); the
`baseline` policy is run separately (`--policy baseline`), comparison only. The vLLM key is read by the
adapter from its private file (D-6); this runner never touches it.

Deliberate deviation from openjev_j2.py (named, not hidden): openjev scrubbed every request string before
sending because codiv.ai is external egress. This runner sends over loopback only, and the brief's "only the
URL differs" means the samples reach the adapter byte-identical to the committed J2 scripts (the Laya runs
sent them unscrubbed too). Measured: 4 of the 484 sample/row texts change under scrub, so scrubbing here would
change the scored inputs; the loopback destination is the owner's own machine and no new egress is added.

  qwen27b_j2.py [--only v1_full,v1,v1_choice_rich,v1_blocking,ap_choice,ap_noul] [--out-dir DIR] [--url URL] [--policy P]

D-7 (the port): before the first request the runner checks the adapter's /health and refuses to
score if its `revision` does not match this lane's LANE_ID — a listener the lane did not start
(AF-AP-33: QJ1's orphaned adapter squatted 47420) would score the OLD transport and the lane must
not treat it as itself. The check is read-only; it never restarts the adapter.
"""
import argparse
import importlib.util
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
FINDINGS = HERE.parent


def check_health(base, policy=None):
    """D-7: the runner must check /health before the first request and refuse a lane mismatch.
    D-2/D-3: the runner's --policy is a LABEL the summary carries; it is not a per-request field.
    The policy is a property of the ADAPTER (fixed at startup, the oracle's own selection for this
    backbone is examples_binary). A mismatch (e.g. --policy baseline pointed at an examples_binary
    adapter) would silently score the wrong policy — the runner's own mistake, measured 2026-09-25:
    the health check therefore also refuses a policy mismatch, not just a lane revision mismatch."""
    lane = os.environ.get("LANE_ID")
    with urllib.request.urlopen(base + "/health", timeout=15) as r:
        h = json.loads(r.read())
    if not h.get("ok"):
        raise SystemExit("refusing to score: /health is not ok: %s" % json.dumps(h)[:200])
    if lane and h.get("revision") != lane:
        raise SystemExit(
            "refusing to score (D-7): /health revision %r is not this lane %r; a listener this lane "
            "did not start is never treated as itself (AF-AP-33)" % (h.get("revision"), lane))
    if policy and h.get("prompt_policy") != policy:
        raise SystemExit(
            "refusing to score (D-2): /health prompt_policy %r is not the requested %r; the policy is "
            "an adapter property (fixed at startup), not a per-request field — restarting the adapter "
            "with --policy %r is required, this runner does not do that" % (h.get("prompt_policy"), policy, policy))
    return h


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def make_post(base, usage):
    def post(url, body, timeout=600):
        state, questions = body["state"], body["questions"]
        data = json.dumps({"state": state, "questions": questions}).encode()
        for attempt in range(7):
            req = urllib.request.Request(base + "/v1/systemone", data=data,
                                         headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    out = json.loads(r.read())
                    usage["requests"] += 1
                    usage["input_tokens"] += out.get("usage", {}).get("input_tokens", 0)
                    answers = out.get("answers", {})
                    usage["refused"] = usage.get("refused", 0) + sum(
                        1 for a in answers.values() if isinstance(a, dict) and a.get("refused"))
                    usage["bounded_answers"] = usage.get("bounded_answers", 0) + sum(
                        1 for a in answers.values() if isinstance(a, dict) and a.get("bounded_labels"))
                    usage["bounded_labels"] = usage.get("bounded_labels", 0) + sum(
                        len(a.get("bounded_labels") or []) for a in answers.values() if isinstance(a, dict))
                    return out
            except urllib.error.HTTPError as e:
                if e.code not in (500, 502, 503) or attempt == 6:
                    raise SystemExit(f"qwen-jev HTTP {e.code}: {e.read(300).decode('utf-8', 'replace')}")
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt == 6:
                    raise SystemExit(f"qwen-jev unreachable: {type(e).__name__}: {e}")
            time.sleep(5 * 2 ** attempt)
        raise AssertionError("unreachable")
    return post


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", default="v1_full,v1,v1_choice_rich,v1_blocking,ap_choice,ap_noul")
    ap.add_argument("--out-dir", default=str(HERE / "qwen27b"))
    ap.add_argument("--url", default="http://127.0.0.1:47420")
    ap.add_argument("--policy", default="examples_binary")
    args = ap.parse_args(argv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # D-7: refuse to score a listener this lane did not start (AF-AP-33) before the first request.
    # D-2: also refuse a policy mismatch — the policy is an adapter property, not a per-request field.
    health = check_health(args.url, policy=args.policy)
    usage = {"requests": 0, "input_tokens": 0, "refused": 0}
    post = make_post(args.url, usage)
    apm = _load("ap_probe", FINDINGS / "ap-hawk-probe" / "ap_probe.py")
    v1m = _load("v1_probe", FINDINGS / "j2-v1-probe" / "v1_probe.py")
    sys.path.insert(0, str(HERE))
    j2b = _load("j2b", HERE / "j2b.py")
    for mod in (apm, v1m, j2b):
        mod.post = post
    summary = {}
    for name in args.only.split(","):
        t0, before = time.time(), dict(usage)
        if name == "ap_noul":
            apm.cmd_score(argparse.Namespace(sample=str(FINDINGS / "ap-hawk-probe" / "sample.json"), url=args.url,
                                             out=str(out_dir / "ap_noul.json")))
            result = None
        elif name == "v1":
            v1m.cmd_score(argparse.Namespace(sample=str(FINDINGS / "j2-v1-probe" / "sample.json"), url=args.url,
                                             out=str(out_dir / "v1.json")))
            result = None
        elif name == "v1_full":  # J2c: the same rows with the whole finding (section 6 of the J2 findings)
            v1m.cmd_score(argparse.Namespace(sample=str(FINDINGS / "j2c-fulltext" / "sample.json"), url=args.url,
                                             out=str(out_dir / "v1_full.json")))
            result = None
        elif name == "v1_choice_rich":
            result = j2b.v1_choice_rich(args.url)
        elif name == "v1_blocking":
            result = j2b.v1_blocking(args.url)
        elif name == "ap_choice":
            result = j2b.ap_choice(args.url)
        else:
            raise SystemExit(f"unknown variant: {name}")
        if result is not None:  # the j2b variants return their metrics (openjev discards them; we persist ours)
            (out_dir / f"{name}.json").write_text(
                json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        summary[name] = {
            "policy": args.policy,
            "seconds": round(time.time() - t0, 1),
            "requests": usage["requests"] - before["requests"],
            "input_tokens": usage["input_tokens"] - before["input_tokens"],
            "refused": usage.get("refused", 0) - before.get("refused", 0),
            "bounded": usage.get("bounded_labels", 0) - before.get("bounded_labels", 0),
        }
        print(f"{name} {json.dumps(summary[name])}", flush=True)
    (out_dir / "run-summary.json").write_text(
        json.dumps({"policy": args.policy, "url": args.url,
                    "health": {"revision": health.get("revision"),
                               "oracle_revision": health.get("oracle_revision")},
                    "usage": usage, "per_variant": summary},
                   indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
