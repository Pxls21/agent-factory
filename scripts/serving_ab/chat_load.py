#!/usr/bin/env python3
"""chat_load.py - a multi-chat, long-context load for an OpenAI-compatible model server (task #454, the
SGLang A/B of D-127 and D-128).

It replays a workload file make_workload.py wrote (sized with the server's own tokenizer): the first N chats
run at once, each an agent-style loop of one shared system prompt, a long first user turn, then turns that
each append the model's reply and the workload's next user turn. Each run puts its own eight-digit run id in
the system prompt's first line, so no run reuses another run's prefix cache, while the chats of one run share
the system prompt as lanes do. Every request streams; its record holds the time to its first token, its
decode rate, its token counts, its status and a loop flag; a first turn's record also holds the workload's
planned prompt size, so a server whose tokenizer or chat template differs shows up in the summary. The
server's /metrics text is saved before and after the run, and nvidia-smi is sampled during it.

The API key is read from a file in process and never printed.

Exit codes: 0 the run finished (its records say how each request went), 2 a bad argument or input.
"""
import argparse
import hashlib
import http.client
import json
import math
import pathlib
import secrets
import subprocess
import sys
import threading
import time
import urllib.parse
import zlib



def die(msg):
    print(f"chat_load: {msg}", file=sys.stderr)
    sys.exit(2)


def looped(text, tail=2000):
    """A reply that ends in a repeat compresses far better than prose: flag it."""
    t = text[-tail:]
    return len(t) >= 1500 and len(zlib.compress(t.encode())) / len(t.encode()) < 0.15


def stream_request(url, key, body, timeout):
    """One streamed chat completion. Returns the record fields; never raises on a server error."""
    u = urllib.parse.urlsplit(url)
    conn_cls = http.client.HTTPSConnection if u.scheme == "https" else http.client.HTTPConnection
    headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    rec = {"status": None, "error": None, "ttft_s": None, "total_s": None, "decode_tok_s": None,
           "prompt_tokens": None, "completion_tokens": None, "cached_tokens": None, "loop": False,
           "usage_seen": False}
    content, t0, t_first = [], time.monotonic(), None
    try:
        conn = conn_cls(u.hostname, u.port, timeout=timeout)
        conn.request("POST", u.path.rstrip("/") + "/chat/completions", body=json.dumps(body), headers=headers)
        resp = conn.getresponse()
        rec["status"] = resp.status
        if resp.status != 200:
            rec["error"] = resp.read(400).decode(errors="replace").replace("\n", " ")
            return rec, ""
        usage = None
        for raw in resp:
            line = raw.decode(errors="replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            ev = json.loads(data)
            if ev.get("usage"):
                usage = ev["usage"]
            for ch in ev.get("choices") or []:
                d = ch.get("delta") or {}
                piece = d.get("content") or ""
                thought = d.get("reasoning_content") or d.get("reasoning") or ""
                if (piece or thought) and t_first is None:
                    t_first = time.monotonic()
                content.append(piece)
        t_end = time.monotonic()
        rec["total_s"] = round(t_end - t0, 3)
        if t_first is not None:
            rec["ttft_s"] = round(t_first - t0, 3)
        if usage:
            rec["usage_seen"] = True
            rec["prompt_tokens"] = usage.get("prompt_tokens")
            rec["completion_tokens"] = usage.get("completion_tokens")
            details = usage.get("prompt_tokens_details") or {}
            rec["cached_tokens"] = details.get("cached_tokens")
            if t_first is not None and rec["completion_tokens"] and t_end > t_first:
                rec["decode_tok_s"] = round(rec["completion_tokens"] / (t_end - t_first), 2)
    except (OSError, http.client.HTTPException, json.JSONDecodeError) as e:
        rec["error"] = f"{type(e).__name__}: {e}"[:400]
        rec["total_s"] = round(time.monotonic() - t0, 3)
    text = "".join(content)
    rec["loop"] = looped(text)
    return rec, text


def run_chat(args, key, wl, system, chat, out, lock, start_delay):
    time.sleep(start_delay)
    msgs = [{"role": "system", "content": system}]
    for turn, t in enumerate(chat["turns"], 1):
        msgs.append({"role": "user", "content": t["content"]})
        body = {"model": args.model, "messages": msgs, "stream": True,
                "stream_options": {"include_usage": True}, "max_tokens": wl["max_reply_tokens"],
                "temperature": args.temperature, "seed": args.seed * 1000 + chat["idx"] * 100 + turn}
        if wl["thinking"] != "server":
            body["chat_template_kwargs"] = {"enable_thinking": wl["thinking"] == "on"}
        t_wall = time.time()
        rec, reply = stream_request(args.base_url, key, body, args.timeout)
        rec.update({"arm": args.arm, "chat": chat["idx"], "turn": turn, "t_start_unix": round(t_wall, 3),
                    "planned_prompt_tokens": chat["first_prompt_tokens"] if turn == 1 else None,
                    "over_limit": rec["ttft_s"] is None or rec["ttft_s"] > args.ttft_limit})
        with lock:
            out.write(json.dumps(rec, sort_keys=True) + "\n")
            out.flush()
        if rec["error"] is not None and args.stop_chat_on_error:
            return
        msgs.append({"role": "assistant", "content": reply or "(no answer)"})


def scrape_metrics(base_url, key, dest):
    u = urllib.parse.urlsplit(base_url)
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    try:
        conn = http.client.HTTPConnection(u.hostname, u.port, timeout=30)
        conn.request("GET", "/metrics", headers=headers)
        resp = conn.getresponse()
        body = resp.read().decode(errors="replace")
        keep = [ln for ln in body.splitlines() if ln.startswith(("vllm:", "sglang:"))]
        dest.write_text("\n".join(keep) + "\n")
        return resp.status, len(keep)
    except OSError as e:
        dest.write_text(f"# scrape failed: {type(e).__name__}\n")
        return None, 0


def pct(xs, q):
    """Nearest rank: q=0 is the minimum, q=1 the maximum."""
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    return xs[max(0, math.ceil(q * len(xs)) - 1)]


def summarize(path, wall_s, limit):
    recs = [json.loads(ln) for ln in path.read_text().splitlines() if ln.strip()]
    cold = [r["ttft_s"] for r in recs if r["turn"] == 1]
    warm = [r["ttft_s"] for r in recs if r["turn"] > 1]
    dec = [r["decode_tok_s"] for r in recs]
    toks = sum(r["completion_tokens"] or 0 for r in recs)
    plan = [abs(r["prompt_tokens"] - r["planned_prompt_tokens"]) for r in recs
            if r["turn"] == 1 and r["prompt_tokens"] is not None and r["planned_prompt_tokens"] is not None]
    return {
        "requests": len(recs),
        "ok": sum(1 for r in recs if r["status"] == 200 and r["error"] is None),
        "errors": sum(1 for r in recs if r["error"] is not None),
        f"missed_{int(limit)}s": sum(1 for r in recs if r["over_limit"]),  # no first token in time; a failure counts
        "cold_ttft_p50_s": pct(cold, 0.5), "cold_ttft_max_s": pct(cold, 1.0),
        "warm_ttft_p50_s": pct(warm, 0.5), "warm_ttft_p95_s": pct(warm, 0.95), "warm_ttft_max_s": pct(warm, 1.0),
        "decode_tok_s_p50": pct(dec, 0.5), "decode_tok_s_min": pct(dec, 0.0),
        "aggregate_tok_s": round(toks / wall_s, 2) if wall_s > 0 else None,
        "prompt_tokens_max": max((r["prompt_tokens"] or 0 for r in recs), default=0),
        "turn1_plan_diff_max": max(plan, default=None),
        "loops": sum(1 for r in recs if r["loop"]),
        "no_usage": sum(1 for r in recs if r["status"] == 200 and not r["usage_seen"]),
        "wall_s": round(wall_s, 1),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--arm", required=True, help="a label for this server and configuration")
    ap.add_argument("--base-url", required=True, help="e.g. http://127.0.0.1:8080/v1")
    ap.add_argument("--model", required=True)
    ap.add_argument("--api-key-file", help="read in process, never printed")
    ap.add_argument("--workload", required=True, help="a file make_workload.py wrote")
    ap.add_argument("--chats", type=int, default=2, help="the first N chats of the workload run at once")
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--stagger-s", type=float, default=30.0)
    ap.add_argument("--ttft-limit", type=float, default=80.0, help="OmniRoute's first-event limit")
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--seed", type=int, default=454)
    ap.add_argument("--stop-chat-on-error", action="store_true")
    ap.add_argument("--nvsmi", action="store_true", help="sample nvidia-smi every 2 s during the run")
    ap.add_argument("--out", required=True, help="a directory that does not exist yet")
    args = ap.parse_args(argv)
    out = pathlib.Path(args.out)
    if out.exists():
        die(f"--out exists: {out}")
    raw = pathlib.Path(args.workload).read_bytes()
    wl = json.loads(raw)
    if not 1 <= args.chats <= len(wl["chats"]):
        die(f"--chats must be 1 to {len(wl['chats'])}, the chats the workload holds")
    if not wl["system"].startswith(wl["run_id_line"]):
        die("the workload's system prompt does not start with its run id line")
    key = ""
    if args.api_key_file:
        key = pathlib.Path(args.api_key_file).expanduser().read_text().strip()
        if not key:
            die("the key file is empty")
    run_id = f"{secrets.randbelow(10 ** 8):08d}"
    system = wl["system"].replace(wl["run_id_line"], f"Run id: {run_id}.", 1)
    chats = wl["chats"][:args.chats]
    out.mkdir(parents=True)
    run = {k: v for k, v in vars(args).items() if k != "api_key_file"}
    run.update({"run_id": run_id, "workload_sha256": hashlib.sha256(raw).hexdigest()})
    (out / "run.json").write_text(json.dumps(run, sort_keys=True, indent=1) + "\n")
    print(f"chat_load: arm {args.arm}: {args.chats} chats x {wl['turns']} turns; first prompts "
          f"{[c['first_prompt_tokens'] for c in chats]} tokens", flush=True)
    m0 = scrape_metrics(args.base_url, key, out / "metrics-before.txt")
    sampler = None
    if args.nvsmi:
        sampler = subprocess.Popen(
            ["nvidia-smi", "--query-gpu=timestamp,memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader", "-lms", "2000"],
            stdout=open(out / "nvsmi.csv", "w"), stderr=subprocess.DEVNULL)
    lock = threading.Lock()
    t0 = time.monotonic()
    with open(out / "requests.jsonl", "w") as fh:
        threads = [threading.Thread(target=run_chat, daemon=True,
                                    args=(args, key, wl, system, c, fh, lock, k * args.stagger_s))
                   for k, c in enumerate(chats)]
        for th in threads:
            th.start()
        for th in threads:
            th.join()
    wall = time.monotonic() - t0
    if sampler is not None:
        sampler.terminate()
    m1 = scrape_metrics(args.base_url, key, out / "metrics-after.txt")
    summary = summarize(out / "requests.jsonl", wall, args.ttft_limit)
    summary.update({"arm": args.arm, "chats": args.chats, "turns": wl["turns"],
                    "metrics_lines_before": m0[1], "metrics_lines_after": m1[1]})
    (out / "summary.json").write_text(json.dumps(summary, sort_keys=True, indent=1) + "\n")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
