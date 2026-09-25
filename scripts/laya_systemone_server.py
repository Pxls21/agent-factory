#!/usr/bin/env python3
"""A local System One endpoint backed by the open Laya model (owner ask 2026-09-22).

Speaks the request/response contract that TypeSafe clients use (jev-pruner's `src/jev.ts`):
  POST /v1/systemone  body {"model": <ignored>, "state": <str|dict|list>, "questions": {id: {...}}}
  -> 200 {"model": ..., "answers": {id: {"type": ..., "noul": <float>, ...}}, "usage": {...}}
`GET /health` -> {"ok": true, "model": ..., "snapshot": ..., "device": ..., "revision": ...}.
Every answer comes from `laya.Agent.system_one`; nothing is synthesized here. PER-CHUNK FAN-OUT
(measured 2026-09-22): when every question id names an entry of `state.chunks` (the pruner's batch
form), the open model answers ONE value for the whole batch (0.598 for three unlike chunks); asked
one chunk per state it discriminates. So a batch whose ids all match chunk ids is answered per
chunk, one question per call, on the shape J2 scored and the fine-tune data holds: the request's
fields except `chunks`, then `chunk` = that chunk's text, last. Laya keeps only the first tokens of a
state (`laya.common.build_sequence`, `st[:room]`), so each per-chunk state first goes through the
dataset builder's own fit (scripts/laya_ft/fit.py; AF-AP-208: unfitted, behind the pruner's history,
every chunk was cut): unchanged when it fits whole, else its other fields are cut, the longest
first, never the chunk. Every chunk is fitted before the model is asked about any; a chunk that does
not fit even with every other field empty refuses the whole request (422 with the reason, final for
scripts/jev.py). Any other shape goes to the model as one call, unchanged — a load failure is a
refusal (503 with a reason), never a fake answer.
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
from typing import Any, ClassVar

MAX_BODY = 8 * 1024 * 1024
PINNED_REVISION = "1c5edc17a7acd8701df6fc341c0d179f1c62c982"
MIN_CUDA_FREE_BYTES = 3 * 1024 * 1024 * 1024
MIB = 1024 * 1024


def _mib(n):
    return int(n // MIB)


def _pick_device(requested, cuda_available, free_bytes):
    """Return (device, reason); device None means the explicit request must refuse."""
    free_mib = _mib(free_bytes)
    need_mib = _mib(MIN_CUDA_FREE_BYTES)
    if requested == "cpu":
        return "cpu", "cpu explicitly requested"
    if requested == "cuda":
        if not cuda_available:
            return None, "cuda requested but CUDA unavailable (%d MiB free; need %d MiB)" % (free_mib, need_mib)
        if free_bytes < MIN_CUDA_FREE_BYTES:
            return None, "cuda requested but only %d MiB free; need %d MiB" % (free_mib, need_mib)
        return "cuda", "cuda requested with %d MiB free" % free_mib
    if cuda_available and free_bytes >= MIN_CUDA_FREE_BYTES:
        return "cuda", "auto: CUDA has %d MiB free" % free_mib
    if cuda_available:
        return "cpu", "auto: CUDA has %d MiB free; need %d MiB" % (free_mib, need_mib)
    return "cpu", "auto: CUDA unavailable (%d MiB free; need %d MiB)" % (free_mib, need_mib)


def _one_line(s):
    return str(s).splitlines()[0]


def _find_snapshot(hf_home, revision):
    root = os.path.join(hf_home, "hub", "models--convaiinnovations--laya", "snapshots")
    expected = os.path.join(root, revision)
    if os.path.isdir(expected):
        return expected
    found = sorted(os.path.basename(p) for p in glob.glob(os.path.join(root, "*")) if os.path.isdir(p))
    if not found:
        raise RuntimeError("no local Laya snapshot under %s for revision %s (HF offline; run laya-server.sh install first)" % (root, revision))
    raise RuntimeError("expected %s; found: %s" % (revision, ", ".join(found)))


class State:
    agent: ClassVar[Any] = None
    lock: ClassVar[threading.Lock] = threading.Lock()
    snapshot: ClassVar[str | None] = None
    subfolder: ClassVar[str | None] = None
    load_error: ClassVar[str | None] = None
    calls: ClassVar[int] = 0
    device: ClassVar[str | None] = None
    device_reason: ClassVar[str | None] = None
    revision: ClassVar[str | None] = None


def load_agent(hf_home, subfolder, threads, requested_device, revision):
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ["OMP_NUM_THREADS"] = str(threads)
    import torch  # noqa: E402
    torch.set_num_threads(threads)
    import laya  # noqa: E402
    if requested_device == "cpu":
        device, reason = _pick_device(requested_device, False, 0)
    else:
        cuda_available = bool(torch.cuda.is_available())
        free_bytes = 0
        if cuda_available:
            try:
                free_bytes, _total = torch.cuda.mem_get_info()
            except Exception as e:
                if requested_device == "cuda":
                    raise RuntimeError("cuda requested but CUDA memory probe failed: %s" % _one_line(e))
                device, reason = "cpu", "auto: CUDA memory probe failed (%s); using CPU" % _one_line(e)
            else:
                device, reason = _pick_device(requested_device, cuda_available, free_bytes)
        else:
            device, reason = _pick_device(requested_device, cuda_available, free_bytes)
    if device is None:
        raise RuntimeError(reason)
    snap = _find_snapshot(hf_home, revision)
    t0 = time.time()
    agent = laya.load(snap, device=device, subfolder=subfolder)
    State.agent, State.snapshot, State.subfolder = agent, snap, subfolder
    State.device, State.device_reason, State.revision = device, reason, revision
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


class FitRefused(Exception):
    """A per-chunk state that does not fit Laya's window even with every other field empty: the request gets no answer
    (HTTP 422; scripts/jev.py treats it as final and asks no other venue)."""


def _laya_fit():
    """scripts/laya_ft/fit.py, the dataset builder's own fit, imported here in the fan-out path; importing it needs no
    laya (the module imports laya when a fit runs, in the Laya venv)."""
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    from laya_ft import fit
    return fit


def _fit(agent, qid, q, state):
    """The per-chunk state fitted by the dataset builder's fit, with the loaded agent's tokenizer, window and question
    form as Agent.system_one reads them. The named seam the model-free tests replace; in production an agent without a
    tokenizer fails here (a 500), so no state reaches the model unfitted."""
    fit = _laya_fit()
    try:
        return fit.fit_state(agent.tok, agent._to_internal(q), agent.cfg.get("max_len", 512),
                             agent.cfg.get("head_max_len", 192), state)[0]
    except fit.Unfit as e:
        raise FitRefused("chunk %r does not fit Laya's window with every other field empty: %d of its %d state tokens "
                         "kept; no chunk was asked" % (qid, e.kept, e.own))


def _answer(state, questions):
    """One model call per chunk when every question id names a chunk (see the module docstring); else one call."""
    chunks = _chunk_map(state)
    if chunks is None or not set(questions) <= set(chunks):
        return State.agent.system_one(state, questions)
    base = {k: v for k, v in state.items() if k != "chunks"}
    # every per-chunk state is fitted before the model is asked about any chunk, so a refusal answers nothing
    fitted = {qid: _fit(State.agent, qid, q, dict(base, chunk=chunks[qid])) for qid, q in questions.items()}
    answers, usage = {}, {"input_tokens": 0, "output_tokens": 0}
    model = None
    for qid, q in questions.items():
        one = State.agent.system_one(fitted[qid], {qid: q})
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
        return self._send(200, {"ok": True, "snapshot": State.snapshot, "subfolder": State.subfolder,
                               "calls": State.calls, "device": State.device, "device_reason": State.device_reason,
                               "revision": State.revision})

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
            with State.lock:  # one forward pass at a time on the CPU/CUDA device; `calls` guarded with the forward pass
                result = _answer(req["state"], req["questions"])
                answers = result.get("answers") if isinstance(result, dict) else None
                if isinstance(answers, dict) and set(answers) == set(req["questions"]):
                    State.calls += 1
        except FitRefused as e:  # the request cannot be served in the trained shape: final for the client (jev.py)
            return self._send(422, {"error": str(e)})
        except Exception as e:  # a model error is a refusal, never a fabricated answer
            return self._send(500, {"error": "system_one failed: %s: %s" % (type(e).__name__, e)})
        answers = result.get("answers") if isinstance(result, dict) else None
        if not isinstance(answers, dict) or set(answers) != set(req["questions"]):
            return self._send(502, {"error": "model returned answers for %s, asked %s" % (sorted(answers or {}), sorted(req["questions"]))})
        result["latency_ms"] = round((time.time() - t0) * 1000, 1)
        return self._send(200, result)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=47411)
    ap.add_argument("--hf-home", default=os.environ.get("HF_HOME", "/root/hf-laya-probe"))
    ap.add_argument("--subfolder", default="typed-decisions")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--device", choices=("auto", "cuda", "cpu"), default="auto")
    ap.add_argument("--revision", default=PINNED_REVISION)
    a = ap.parse_args()
    if a.host not in ("127.0.0.1", "localhost", "::1"):
        print("refusing a non-loopback bind: %s" % a.host, file=sys.stderr)
        return 64
    try:
        secs = load_agent(a.hf_home, a.subfolder, a.threads, a.device, a.revision)
    except Exception as e:
        State.load_error = "%s: %s" % (type(e).__name__, e)
        print("laya_systemone_server: model load FAILED: %s" % State.load_error, file=sys.stderr)
        return 3
    print(json.dumps({"event": "ready", "snapshot": State.snapshot, "subfolder": a.subfolder,
                      "load_s": round(secs, 1), "device": State.device, "device_reason": State.device_reason,
                      "revision": State.revision, "url": "http://%s:%d/v1/systemone" % (a.host, a.port)}),
          file=sys.stderr, flush=True)
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
