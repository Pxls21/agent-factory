#!/usr/bin/env python3
"""The J2 probes, UNCHANGED, against OpenJev 0.1 on codiv.ai (owner 2026-09-24 14:1xZ: the hosted Jev for testing and data).

J2 section 3 set the rule for a new candidate: "these two samples and scripts rerun against it unchanged, with the same
baselines". This runner loads `ap_probe.py`, `v1_probe.py` and `j2b.py` as they are committed and swaps only their `post`:
the request goes to `https://api.codiv.ai/v1/systemone` with model `openjev-latest`, and a batch whose question ids all
name `state.chunks` is split one chunk per request, as the local Laya server does, so every question sees one chunk.
The key is read from a private file (`CODIV_ENV`, default `/root/.codiv/api.env`), never from argv, and never printed.
The API allows 60 requests per minute per key; requests start at least 1.05 s apart.
The owner approved sending repo text to codiv.ai for this work (D-078, after reading its terms); every string in a request
first passes `transcript_export.scrub` (the scrubber `scripts/jev.py` uses), so no secret shape leaves as written.

  openjev_j2.py [--only v1_full,v1,v1_choice_rich,v1_blocking,ap_choice,ap_noul] [--out-dir DIR]
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
sys.path.insert(0, str(HERE.parents[3] / "scripts"))
from transcript_export import scrub  # noqa: E402  (the scrubber scripts/jev.py uses)
MODEL = "openjev-latest"
MIN_GAP = 1.05
_last = [0.0]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _env():
    path = os.environ.get("CODIV_ENV", "/root/.codiv/api.env")
    pairs = (line.split("=", 1) for line in Path(path).read_text(encoding="utf-8").splitlines() if "=" in line)
    return {k.strip(): v.strip() for k, v in pairs}


def _scrubbed(value):
    """Every string in the request, keys included, through the scrubber; other JSON types unchanged."""
    if isinstance(value, str):
        return scrub(value)
    if isinstance(value, dict):
        return {_scrubbed(k): _scrubbed(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_scrubbed(v) for v in value]
    return value


def _one(env, state, questions):
    body = json.dumps({"model": MODEL, "state": _scrubbed(state), "questions": _scrubbed(questions)}).encode()
    for attempt in range(7):
        wait = MIN_GAP - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        req = urllib.request.Request(env["TYPESAFE_BASE_URL"] + "/v1/systemone", data=body, headers={
            "Content-Type": "application/json", "User-Agent": "python-httpx/0.28.1",
            "Authorization": "Bearer " + env["TYPESAFE_API_KEY"]})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == 6:
                raise SystemExit(f"codiv HTTP {e.code}: {e.read(300).decode('utf-8', 'replace')}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == 6:
                raise SystemExit(f"codiv unreachable: {type(e).__name__}: {e}")
        time.sleep(5 * 2 ** attempt)
    raise AssertionError("unreachable")


def make_post(env, usage):
    def post(url, body, timeout=600):
        state, questions = body["state"], body["questions"]
        chunks = state.get("chunks") if isinstance(state, dict) else None
        if isinstance(chunks, list) and set(questions) <= {c["id"] for c in chunks}:
            text = {c["id"]: c["text"] for c in chunks}
            base = {k: v for k, v in state.items() if k != "chunks"}
            answers = {}
            for qid, q in questions.items():
                out = _one(env, dict(base, chunk=text[qid]), {qid: q})
                answers[qid] = out["answers"][qid]
                usage["requests"] += 1
                usage["input_tokens"] += out.get("usage", {}).get("input_tokens", 0)
            return {"answers": answers, "fan_out": len(questions)}
        out = _one(env, state, questions)
        usage["requests"] += 1
        usage["input_tokens"] += out.get("usage", {}).get("input_tokens", 0)
        return out
    return post


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", default="v1_full,v1,v1_choice_rich,v1_blocking,ap_choice,ap_noul")
    ap.add_argument("--out-dir", default=str(HERE / "openjev"))
    args = ap.parse_args(argv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    env = _env()
    usage = {"requests": 0, "input_tokens": 0}
    post = make_post(env, usage)
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
            apm.cmd_score(argparse.Namespace(sample=str(FINDINGS / "ap-hawk-probe" / "sample.json"), url="codiv",
                                             out=str(out_dir / "ap_noul.json")))
        elif name == "v1":
            v1m.cmd_score(argparse.Namespace(sample=str(FINDINGS / "j2-v1-probe" / "sample.json"), url="codiv",
                                             out=str(out_dir / "v1.json")))
        elif name == "v1_full":  # J2c: the same rows with the whole finding (section 6 of the J2 findings)
            v1m.cmd_score(argparse.Namespace(sample=str(FINDINGS / "j2c-fulltext" / "sample.json"), url="codiv",
                                             out=str(out_dir / "v1_full.json")))
        else:
            res = j2b.VARIANTS[name]("codiv")
            (out_dir / f"{name}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
            print(name, json.dumps(res), flush=True)
        summary[name] = {"seconds": round(time.time() - t0, 1), "requests": usage["requests"] - before["requests"],
                         "input_tokens": usage["input_tokens"] - before["input_tokens"]}
        print(name, "done", json.dumps(summary[name]), flush=True)
    (out_dir / "usage.json").write_text(json.dumps({"model": MODEL, "runs": summary}, indent=1, sort_keys=True) + "\n",
                                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
