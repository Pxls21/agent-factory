#!/usr/bin/env python3
"""A local System One endpoint backed by the open Laya model (owner ask 2026-09-22).

Speaks the request/response contract that TypeSafe clients use (jev-pruner's `src/jev.ts`):
  POST /v1/systemone  body {"model": <ignored>, "state": <str|dict|list>, "questions": {id: {...}}}
  -> 200 {"model": ..., "answers": {id: {"type": ..., "noul": <float>, ...}}, "usage": {...}}
`GET /health` -> {"ok": true, "model": ..., "snapshot": ...}.
Every answer comes from `laya.Agent.system_one` on the CPU, FP32 (the J0 probe's loader); nothing is
synthesized here. PER-CHUNK FAN-OUT (measured 2026-09-22): when every question id names an entry of `state.chunks`
(the pruner's batch form), the open model answers ONE value for the whole batch (0.598 for three unlike chunks);
asked one chunk per state it discriminates (PASSED lines 0.468, `collected` 0.460, AssertionError 0.651, Traceback
0.615). So a batch whose ids all match chunk ids is answered per chunk: state = the request state minus `chunks`
plus `chunk` = that chunk's text, one question per call (~0.3 s each on the sandbox CPU); any other shape goes
to the model as one call — a load failure is a refusal (503 with a reason), never a fake answer.
Bind is loopback only. The bearer token is not checked (the endpoint is loopback-only; there is no
second tenant); a client's `authorization` header is ignored. Run inside the Laya venv:
  HF_HUB_OFFLINE=1 HF_HOME=/root/hf-laya-probe /root/venv-laya-probe/bin/python scripts/laya_systemone_server.py
"""
import argparse
import glob
import json
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_BODY = 8 * 1024 * 1024


def _find_snapshot(hf_home):
    pats = glob.glob(os.path.join(hf_home, "hub", "models--convaiinnovations--laya", "snapshots", "*"))
    return sorted(pats)[0] if pats else None


class State:
    agent = None
    lock = threading.Lock()
    snapshot = None
    subfolder = None
    load_error = None
    calls = 0


def load_agent(hf_home, subfolder, threads):
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ["OMP_NUM_THREADS"] = str(threads)
    import torch  # noqa: E402
    torch.set_num_threads(threads)
    import laya  # noqa: E402
    snap = _find_snapshot(hf_home)
    if snap is None:
        raise RuntimeError("no local Laya snapshot under %s (HF offline; run the J0 probe download first)" % hf_home)
    t0 = time.time()
    agent = laya.load(snap, device="cpu", subfolder=subfolder)
    State.agent, State.snapshot, State.subfolder = agent, snap, subfolder
    return time.time() - t0


def _chunk_map(state):
    """The pruner's batch form: state.chunks = [{id, text}, ...] -> {id: text}; None for any other shape."""
    if not isinstance(state, dict) or not isinstance(state.get("chunks"), list):
        return None
    out = {}
    for c in state["chunks"]:
        if not isinstance(c, dict) or not isinstance(c.get("id"), str) or not isinstance(c.get("text"), str):
            return None
        out[c["id"]] = c["text"]
    return out


def _answer(state, questions):
    """One model call per chunk when every question id names a chunk (see the module docstring); else one call."""
    chunks = _chunk_map(state)
    if chunks is None or not set(questions) <= set(chunks):
        return State.agent.system_one(state, questions)
    base = {k: v for k, v in state.items() if k != "chunks"}
    answers, usage = {}, {"input_tokens": 0, "output_tokens": 0}
    model = None
    for qid, q in questions.items():
        one = State.agent.system_one(dict(base, chunk=chunks[qid]), {qid: q})
        answers[qid] = one["answers"][qid]
        model = one.get("model", model)
        for k in usage:
            usage[k] += int((one.get("usage") or {}).get(k, 0) or 0)
    return {"model": model, "answers": answers, "usage": usage, "fan_out": len(questions)}


class Handler(BaseHTTPRequestHandler):
    server_version = "laya-systemone/0.1"

    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # one JSON line per request on stderr (the reason field)
        sys.stderr.write(json.dumps({"ts": time.time(), "msg": fmt % args}) + "\n")

    def do_GET(self):
        if self.path != "/health":
            return self._send(404, {"error": "not found"})
        if State.agent is None:
            return self._send(503, {"ok": False, "reason": State.load_error or "model not loaded"})
        return self._send(200, {"ok": True, "snapshot": State.snapshot, "subfolder": State.subfolder, "calls": State.calls})

    def do_POST(self):
        if self.path != "/v1/systemone":
            return self._send(404, {"error": "not found"})
        n = int(self.headers.get("content-length") or 0)
        if n <= 0 or n > MAX_BODY:
            return self._send(413 if n > MAX_BODY else 400, {"error": "body length %d refused" % n})
        try:
            req = json.loads(self.rfile.read(n))
        except ValueError as e:
            return self._send(400, {"error": "malformed JSON: %s" % e})
        if not isinstance(req, dict) or "state" not in req or not isinstance(req.get("questions"), dict) or not req["questions"]:
            return self._send(400, {"error": "body must be {state, questions:{id:{...}}}"})
        for qid, q in req["questions"].items():
            if not isinstance(q, dict) or q.get("type") not in ("noul", "choice", "score"):
                return self._send(400, {"error": "question %r: type must be noul|choice|score" % qid})
        if State.agent is None:
            return self._send(503, {"error": State.load_error or "model not loaded"})
        t0 = time.time()
        try:
            with State.lock:  # one forward pass at a time on the CPU
                result = _answer(req["state"], req["questions"])
        except Exception as e:  # a model error is a refusal, never a fabricated answer
            return self._send(500, {"error": "system_one failed: %s: %s" % (type(e).__name__, e)})
        answers = result.get("answers") if isinstance(result, dict) else None
        if not isinstance(answers, dict) or set(answers) != set(req["questions"]):
            return self._send(502, {"error": "model returned answers for %s, asked %s" % (sorted(answers or {}), sorted(req["questions"]))})
        State.calls += 1
        result["latency_ms"] = round((time.time() - t0) * 1000, 1)
        return self._send(200, result)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=47411)
    ap.add_argument("--hf-home", default=os.environ.get("HF_HOME", "/root/hf-laya-probe"))
    ap.add_argument("--subfolder", default="typed-decisions")
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()
    if a.host not in ("127.0.0.1", "localhost", "::1"):
        print("refusing a non-loopback bind: %s" % a.host, file=sys.stderr)
        return 64
    try:
        secs = load_agent(a.hf_home, a.subfolder, a.threads)
    except Exception as e:
        State.load_error = "%s: %s" % (type(e).__name__, e)
        print("laya_systemone_server: model load FAILED: %s" % State.load_error, file=sys.stderr)
        return 3
    print(json.dumps({"event": "ready", "snapshot": State.snapshot, "subfolder": a.subfolder, "load_s": round(secs, 1),
                      "url": "http://%s:%d/v1/systemone" % (a.host, a.port)}), file=sys.stderr, flush=True)
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
