#!/usr/bin/env python3
"""RWKV-7 stream reader beside a temporary Qwen server: the side-by-side probe (task #262; D-087, D-088).

Runs ON the PC with ~/venv-rwkv-b/bin/python, started once per configuration by scripts/gpu_side_by_side.sh inside a
GPU window, while that script's temporary Qwen server (a smaller GPU share) answers on loopback. Reuses
../j2b-variants/rwkv7_g0.py by import (its phase_env, load, real_text_ids and Scorer.forward, which sends
logits_to_keep=1); torch is imported only inside functions, so the sandbox tests import this file without it.
Three phases, each written to --out as it completes (a failed phase is recorded and the next one still runs):
  alone           read T real tokens in chunks of C, the state carried chunk to chunk: per-chunk seconds and torch
                  peaks; every compute app's pid and MiB from nvidia-smi (which pid is Qwen's is not assumed); the G0
                  question 5 times from a deepcopy of the final state; two chunks of C/2 against one forward of C
  qwen_idle_rwkv  N concurrent chat completions to the Qwen server while the RWKV model sits loaded and idle: aggregate
                  completion tokens per second from each response's usage and the wall time (skipped when N is 0)
  together        the same load started and, while it runs, the read and the questions again; the read then repeats
                  until the load ends, so Qwen's tokens per second is measured with RWKV working for the whole load,
                  and the record says how much of the load RWKV covered
The exit is 0 only when every phase produced its measurement. The load requests carry only model, messages,
max_tokens and temperature (AF-AP-201). The key is read from --key-file into a header in process: never printed,
never in argv, never in the record; the URL must be loopback.
  rwkv_sbs_probe.py --tokens T --chunk C --load N --url http://127.0.0.1:PORT/v1/chat/completions --key-file F --out J
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import math
import os
import re
import statistics
import subprocess
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
G0_PATH = HERE.parent / "j2b-variants" / "rwkv7_g0.py"
MODEL = "qwen3.8-27b-local"
MAX_TOKENS = 512
QUESTION = "\n\nUser: Which component does this document describe first?\n\nAssistant:"   # rwkv7_g0.phase_ladder's
QUESTION_REPEATS = 5
PROMPT_CHARS = 6000
HTTP_TIMEOUT = 300
PHASES = ("alone", "qwen_idle_rwkv", "together")


def load_g0():
    spec = importlib.util.spec_from_file_location("rwkv7_g0", G0_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Engine:
    """The real side: G0's Scorer on the GPU, and torch's clocks and memory peaks. The tests pass a fake with the same
    methods; this class is exercised only on the PC."""

    def __init__(self, scorer):
        import torch
        self.torch, self.scorer = torch, scorer

    def forward(self, ids, state):
        return self.scorer.forward(ids, state)

    def sync(self):
        self.torch.cuda.synchronize()

    def reset_peak(self):
        self.torch.cuda.reset_peak_memory_stats()

    def peak(self):
        c = self.torch.cuda
        return {"peak_allocated_mib": c.max_memory_allocated() >> 20, "peak_reserved_mib": c.max_memory_reserved() >> 20}

    def finite(self, logits):
        return bool(self.torch.isfinite(logits).all())

    def compare(self, a, b):
        d = (a.float() - b.float()).abs()
        return {"max_abs_logit_diff": float(d.max()), "same_argmax": int(a.argmax()) == int(b.argmax())}

    def release(self):                                   # after a failed phase (an OOM leaves cached blocks)
        self.torch.cuda.empty_cache()


def read(engine, ids, chunk, clock):
    """One pass over ids in chunks of `chunk`, the state carried from each chunk to the next: (rows, final state)."""
    rows, state = [], None
    for start in range(0, len(ids), chunk):
        part = ids[start:start + chunk]
        engine.reset_peak()
        engine.sync()
        t0 = clock()
        logits, state = engine.forward(part, state)
        engine.sync()
        rows.append(dict(start=start, tokens=len(part), seconds=round(clock() - t0, 4), finite=engine.finite(logits),
                         **engine.peak()))
    return rows, state


def read_stats(rows):
    secs = [r["seconds"] for r in rows]
    return {"chunks": len(rows), "tokens": sum(r["tokens"] for r in rows), "seconds_total": round(sum(secs), 4),
            "seconds_median_chunk": round(statistics.median(secs), 4),
            "seconds_median_after_first": round(statistics.median(secs[1:]), 4) if len(secs) > 1 else None,
            "peak_allocated_mib": max(r["peak_allocated_mib"] for r in rows),
            "peak_reserved_mib": max(r["peak_reserved_mib"] for r in rows), "finite": all(r["finite"] for r in rows)}


def questions(engine, state, question, clock):
    """The G0 question from a deepcopy of the final state, QUESTION_REPEATS times; the copy is inside the timing, as G0
    times it. The state itself is never read from, so it stays the reader's."""
    times, finite = [], True
    for _ in range(QUESTION_REPEATS):
        engine.sync()
        t0 = clock()
        logits, _ = engine.forward(question, copy.deepcopy(state))
        engine.sync()
        times.append(clock() - t0)
        finite = finite and engine.finite(logits)
    return {"question_tokens": len(question), "seconds_median": round(statistics.median(times), 4),
            "seconds_all": [round(t, 4) for t in times], "finite": finite}


def chunk_check(engine, ids, chunk):
    """Two chunks of C/2 (the state carried) against one forward of C: the same last-position argmax? Recorded, not a
    gate: bf16 noise can flip a near tie (G0 measured a 0.1875 largest difference at 2,048 tokens)."""
    half = chunk // 2
    whole, _ = engine.forward(ids[:chunk], None)
    _, state = engine.forward(ids[:half], None)
    split, _ = engine.forward(ids[half:chunk], state)
    return dict(tokens=chunk, first=half, second=chunk - half, **engine.compare(whole, split))


def smi_apps(run=subprocess.run):
    """Every compute app's pid and MiB from nvidia-smi, and this process's own row. Which pid is Qwen's is not
    assumed: a rootless container's process may or may not show under a host pid."""
    rec = {"own_pid": os.getpid()}
    try:
        r = run(["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError) as e:
        return dict(rec, ok=False, error="%s: %s" % (type(e).__name__, e))
    if r.returncode != 0:
        return dict(rec, ok=False, error="rc %d: %s" % (r.returncode, (r.stdout + r.stderr).strip()[:300]))
    apps = []
    for line in r.stdout.splitlines():
        if line.strip():
            pid, _, mib = (x.strip() for x in line.partition(","))
            apps.append({"pid": int(pid) if pid.isdigit() else None, "used_mib": int(mib) if mib.isdigit() else None,
                         "raw": line.strip()})
    own = [a["used_mib"] for a in apps if a["pid"] == rec["own_pid"]]
    return dict(rec, ok=True, apps=apps, own_mib=own[0] if own else None)


def prompt_text(repo=REPO):
    """The fixed load prompt: the first PROMPT_CHARS characters of the first docs/*.md (sorted), then one instruction."""
    src = sorted((repo / "docs").glob("*.md"))[0]
    return src.read_text(encoding="utf-8", errors="replace")[:PROMPT_CHARS] + (
        "\n\nSummarize the text above in ten numbered points.")


def chat_payload(prompt):
    """Only these four keys go to the server (AF-AP-201: never logprobs, prompt_logprobs, n, best_of or echo)."""
    return {"model": MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": MAX_TOKENS,
            "temperature": 0}


def read_key(path):
    key = Path(path).read_text(encoding="utf-8").strip()
    if not key or any(c.isspace() for c in key):
        raise ValueError("the key file %s holds no single-line key" % path)
    return key


def make_post(url, key, timeout=HTTP_TIMEOUT):
    """POST one chat completion with the key in the Authorization header only. No proxy: the server is on loopback."""
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + key}

    def post(payload):
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with opener.open(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    return post


def scrubber(key):
    """For recorded error text. In process only (the key is here anyway, for the header): any Bearer token by pattern
    class, which also covers a cut-off echo, then the value itself (AF-AP-35: never a filter built into argv)."""
    def scrub(s):
        s = re.sub(r"(?i)(bearer\s+)\S+", r"\1<key>", s)
        return s.replace(key, "<key>") if key else s
    return scrub


def chat_load(post, n, payload, clock, t_ref, scrub=str):
    """N concurrent chat completions. Each row: start and end (seconds after t_ref), status, and the response's own
    usage. A response without an integer usage.completion_tokens fails its row: never a silent zero. The aggregate is
    the ok rows' completion tokens over the wall time from the first start to the last end."""
    rows = [None] * n

    def one(i):
        t0 = clock()
        row = {"start": round(t0 - t_ref, 4)}
        try:
            status, body = post(payload)
            usage = body.get("usage") if isinstance(body, dict) else None
            ct = usage.get("completion_tokens") if isinstance(usage, dict) else None
            row["status"] = status
            if isinstance(ct, int) and not isinstance(ct, bool) and ct >= 0:
                row.update(ok=True, completion_tokens=ct, prompt_tokens=usage.get("prompt_tokens"))
            else:
                row.update(ok=False, error="no integer usage.completion_tokens in the response")
        except urllib.error.HTTPError as e:
            row.update(ok=False, status=e.code,
                       error=scrub("HTTP %d: %s" % (e.code, e.read()[:300].decode("utf-8", "replace"))))
        except Exception as e:                                         # every failure is a recorded row
            row.update(ok=False, error=scrub("%s: %s" % (type(e).__name__, e))[:300])
        t1 = clock()
        row.update(end=round(t1 - t_ref, 4), seconds=round(t1 - t0, 4))
        rows[i] = row

    threads = [threading.Thread(target=one, args=(i,), daemon=True) for i in range(n)]
    t0 = clock()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    wall = clock() - t0
    done = [r for r in rows if r and r.get("ok")]
    tokens = sum(r["completion_tokens"] for r in done)
    tps = tokens / wall if wall > 0 else float("nan")
    return {"requests": n, "requests_ok": len(done), "start": round(t0 - t_ref, 4), "end": round(t0 + wall - t_ref, 4),
            "wall_seconds": round(wall, 4), "completion_tokens": tokens,
            "tokens_per_second": round(tps, 3) if math.isfinite(tps) else None,
            "ok": len(done) == n and math.isfinite(tps) and tps > 0, "rows": rows}


def phase_alone(out, engine, ids, question, chunk, clock, smi):
    rows, state = read(engine, ids, chunk, clock)
    out["read"] = dict(read_stats(rows), rows=rows)
    out["smi"] = smi()
    out["questions"] = questions(engine, state, question, clock)
    out["chunk_check"] = chunk_check(engine, ids, chunk)
    out["ok"] = out["read"]["finite"] and out["questions"]["finite"] and out["smi"]["ok"]


def phase_qwen_idle(out, post, n, payload, clock, scrub):
    if n == 0:
        out.update(ok=True, skipped="N is 0: no load")
        return
    out["load"] = chat_load(post, n, payload, clock, clock(), scrub)
    out["ok"] = out["load"]["ok"]


def phase_together(out, engine, ids, question, chunk, post, n, payload, clock, smi, scrub):
    """The load starts, then the read and the questions run again (pass 1, recorded in full); while the load still
    runs, further passes keep RWKV working (each summarized), so the load's aggregate is Qwen's rate with RWKV busy."""
    t_ref, box = clock(), {}
    loader = threading.Thread(target=lambda: box.update(load=chat_load(post, n, payload, clock, t_ref, scrub)),
                              daemon=True)
    if n:
        loader.start()
    r0 = clock()
    rows, state = read(engine, ids, chunk, clock)
    out["read"] = dict(read_stats(rows), rows=rows)
    out["questions"] = questions(engine, state, question, clock)
    first_end, passes = clock(), []
    while n and loader.is_alive():
        p0 = clock()
        prows, pstate = read(engine, ids, chunk, clock)
        q = questions(engine, pstate, question, clock)
        passes.append(dict(read_stats(prows), start=round(p0 - t_ref, 4), end=round(clock() - t_ref, 4),
                           question_seconds_median=q["seconds_median"], question_finite=q["finite"]))
    r1 = clock()
    out["more_passes"] = passes
    out["smi"] = smi()
    finite = (out["read"]["finite"] and out["questions"]["finite"]
              and all(p["finite"] and p["question_finite"] for p in passes))
    if not n:
        out["load"] = {"skipped": "N is 0: no load"}
        out["ok"] = finite and out["smi"]["ok"]
        return
    loader.join()
    load = out["load"] = box.get("load")
    if load is None:
        out.update(ok=False, error="the load thread returned no record")
        return
    ls, le = load["start"], load["end"]
    rs, fe, re_ = r0 - t_ref, first_end - t_ref, r1 - t_ref
    covered = max(0.0, min(le, re_) - max(ls, rs))
    out["overlap"] = {"load_start": ls, "load_end": le, "rwkv_start": round(rs, 4), "rwkv_first_pass_end": round(fe, 4),
                      "rwkv_end": round(re_, 4), "first_pass_inside_load": fe <= le,
                      "load_seconds_with_rwkv": round(covered, 4),
                      "load_fraction_with_rwkv": round(covered / (le - ls), 4) if le > ls else None}
    out["ok"] = finite and out["smi"]["ok"] and load["ok"]


def run_phases(rec, engine, ids, question, chunk, n, post, payload, clock=time.perf_counter, smi=smi_apps,
               write=lambda: None, scrub=str):
    """Every phase in order; each recorded as it completes. A failed phase keeps its partial rows and its error, and
    the next phase still runs. Returns 0 only when every phase says ok."""
    steps = (("alone", lambda o: phase_alone(o, engine, ids, question, chunk, clock, smi)),
             ("qwen_idle_rwkv", lambda o: phase_qwen_idle(o, post, n, payload, clock, scrub)),
             ("together", lambda o: phase_together(o, engine, ids, question, chunk, post, n, payload, clock, smi,
                                                    scrub)))
    for name, step in steps:
        out = rec[name] = {}
        try:
            step(out)
        except Exception:
            out.update(ok=False, error=scrub(traceback.format_exc()[-2000:]))
            try:
                engine.release()
            except Exception as e:                                     # recorded, never masking the phase's error
                out["release_error"] = "%s: %s" % (type(e).__name__, e)
        write()
    return 0 if all(rec[p].get("ok") is True for p in PHASES) else 1


def parse_args(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tokens", type=int, required=True)
    ap.add_argument("--chunk", type=int, required=True)
    ap.add_argument("--load", type=int, required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--key-file", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    if not (1024 <= args.chunk <= 16384 and args.chunk <= args.tokens <= 65536 and 0 <= args.load <= 8):
        ap.error("--chunk takes 1024-16384, --tokens chunk-65536, --load 0-8")
    if not args.url.startswith("http://127.0.0.1:"):
        ap.error("--url must be loopback (http://127.0.0.1:PORT/...): the key goes nowhere else")
    return args


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    out = Path(args.out)
    rec = {"probe": "rwkv_sbs_probe", "started": now(), "pid": os.getpid(),
           "config": {"tokens": args.tokens, "chunk": args.chunk, "load": args.load, "url": args.url, "model": MODEL,
                      "max_tokens": MAX_TOKENS, "temperature": 0, "question_repeats": QUESTION_REPEATS}}

    def write():
        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_name(out.name + ".tmp")
        tmp.write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(tmp, out)

    scrub, rc = str, 1
    try:
        key = read_key(args.key_file)
        scrub = scrubber(key)
        post = make_post(args.url, key)
        prompt = prompt_text()
        rec["prompt"] = {"source": str(sorted((REPO / "docs").glob("*.md"))[0].relative_to(REPO)),
                         "chars": len(prompt), "sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]}
        g0 = load_g0()
        ns = argparse.Namespace(plumbing=False, no_cache=False)
        g0.phase_env(rec, ns)                                          # free/total MiB: what Qwen left this process
        tok, scorer = g0.load(rec, ns)
        write()
        import torch
        engine = Engine(scorer)
        rec["smi_after_load"] = smi_apps()
        ids = g0.real_text_ids(tok, args.tokens)
        question = tok.encode(QUESTION, add_special_tokens=False)
        with torch.inference_mode():
            rc = run_phases(rec, engine, ids, question, args.chunk, args.load, post, chat_payload(prompt),
                            write=write, scrub=scrub)
    except Exception:
        rec["error"] = scrub(traceback.format_exc()[-2000:])
        rc = 1
    rec.update(finished=now(), rc=rc)
    write()
    print(json.dumps({"rc": rc, "error": (rec.get("error") or "")[-300:] or None,
                      **{p: rec.get(p, {}).get("ok") for p in PHASES}}, sort_keys=True))
    return rc


if __name__ == "__main__":
    sys.exit(main())
