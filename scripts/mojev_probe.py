#!/usr/bin/env python3
"""MoJev Gate 0 probe: load, integrity, latency, memory, truncation, order, determinism on the PC's CPU.

Contract: tasks/briefs/pc/pc-mojev-g0.md (PINNED DECISIONS D-1..D-4, CONTRACT G0-1..G0-6), as amended by
tasks/briefs/jev-laya/MOJEV-G0-SANDBOX-brief.md (built in the sandbox, run on the PC by the coordinator).
It measures what docs/research/findings/MOJEV-AUDIT-2026-09-24.md section 4 only estimated, and writes one
JSON result. Every number in that JSON comes from a child process that loaded the real checkpoint.

Run on the PC only (the sandbox runs --dry-run and tests/test_mojev_probe.py):
    nice -n 10 ~/venv-mojev/bin/python scripts/mojev_probe.py --pin ~/mojev-pin \
        --snapshot ~/mojev-snapshot/<revision dir> --out <dir>/mojev-probe-0.json
    --dry-run      print the plan (tasks, token cuts, candidate sets) and exit; no model, no torch import
    --only ID      run only the named task(s), a smoke; writes the partial log, never the final JSON

Design (the PC brief's PINNED DECISIONS):
  D-1  MoJev's own code from --pin: load_packed (mojev/evaluate.py:40) and Engine.answer (mojev/serve.py:182),
       both unmodified. Engine.__init__ is bypassed because it loads the processor with trust_remote_code=True
       (mojev/serve.py:169-172); load_engine sets the same attributes with trust_remote_code=False. A processor
       that will not load that way stops the run (exit 3). Remote code is never enabled.
  D-2  two dtypes: released_bf16 (as loaded: bf16 encoder, fp32 head) and fp32 (the encoder cast after loading).
  D-3  states are docs/INCIDENT-LOG.md at --text-rev, cut to an exact token count with the snapshot's tokenizer;
       the question and the candidates are fixed below; the only randomness is the seeded G0-4 orderings.
  D-4  one child process per task: each load, forward pass and VmHWM belongs to one child. The parent imports no
       torch; it hashes, spawns, stops a child by pid past the phase limit or the RSS cap, and writes the JSON.
torch, transformers and mojev are imported only inside load_engine, so the tests run without them.

Exit codes: 0 done; 2 G0-1 refusal (weights or code pin, before any load); 3 a child refused (processor,
dtype variant, threads, pin origin, ...) and the run stopped; 4 the result is incomplete and was not written
(each missing or unmeasured cell or block is named); 64 usage.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime
import hashlib
import json
import math
import os
import random
import selectors
import statistics
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path

SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[1]

# ---- G0-1 pins (the Hub listing for the revision, re-read in this lane's premise) ----
WEIGHTS_FILE = "model.safetensors"
WEIGHTS_SIZE = 1_710_234_304
WEIGHTS_SHA256 = "eae27bf03e0e44501316cafab2406b1505732ddf4b836d19fbb8deb642f55f50"
CODE_HEAD = "a74d58cd19ec573e83e8e27f9fecd837b8d830fb"          # github.com/MoLeMo-Lab/mojev master
SNAPSHOT_REVISION = "0c8695b6252f4205907433d4e196a94f032e60c3"  # huggingface.co/MoLeMo-Lab/mojev

# ---- D-3 inputs ----
TEXT_PATH = "docs/INCIDENT-LOG.md"
TEXT_REV = "8c684be"  # the PC brief's PIN
IMAGE_MARKERS = ("<|image_pad|>", "<|vision_start|>", "<|vision_end|>", "<|video_pad|>")  # audit section 4 item 6
QUESTION = "subsystem_of_the_first_incident"
ANSWERS = (
    "PC bridge", "push script", "CI gate", "wiki hooks", "lane dispatcher",
    "vLLM server", "OmniRoute route", "proof runner", "ledger file", "gVisor sandbox",
    "egress policy", "Hermes profile", "task database", "GitNexus index", "Ouroboros server",
    "test suite",
)
LABELS = tuple(f"{chr(ord('A') + i)}. " for i in range(len(ANSWERS)))  # G0-4: the label decides the sorted slot
SEED = 20260924

# ---- G0-2 matrix and the limits every child runs under ----
STATE_TOKENS = (2048, 4096, 8192, 16384)
CANDIDATE_COUNTS = (5, 10, 16)
DTYPES = ("released_bf16", "fp32")
RUNS = 4                        # run-0 is the warm-up, run-1..run-3 are timed
THREADS = 6
NICE = 10
PHASE_TIMEOUT_S = 600.0         # a load, a run, or silence past this stops the task: TIMEOUT, a finding
RSS_CAP_KB = 32 * 1024 * 1024   # 32 GiB, against VmRSS (kB) in /proc/<pid>/status
POLL_S = 0.5
CHILD_ENV = {
    "CUDA_VISIBLE_DEVICES": "", "HF_HUB_OFFLINE": "1", "TRANSFORMERS_OFFLINE": "1",
    "OMP_NUM_THREADS": str(THREADS), "MKL_NUM_THREADS": str(THREADS), "OPENBLAS_NUM_THREADS": str(THREADS),
    "TOKENIZERS_PARALLELISM": "false",
}

# ---- G0-3 .. G0-6 ----
TRUNC_STATE_TOKENS = 20_000
TRUNC_BUDGET = 16_384           # config.context_tokens of the release; the child refuses any other value
TRUNC_CANDIDATES = 5
ORDER_TOKENS = 4096
ORDER_CANDIDATES = 16
ORDER_CONTROLS = 2              # seeded plain shuffles, besides the listed order
ORDER_LABELINGS = 5             # seeded label assignments, besides the identity reference
DETERMINISM_CELL = (4096, 10)
PROJECTION_CELLS = ((8192, 10), (16384, 16))
PROJECTION_DECISIONS = 100
FIELD_PROMPT_CAP = 32           # packed_collate's field_tokens_max (mojev/full.py:132,150-151)

# Lines of the pinned code this probe depends on, re-read on the PC pin at run time (G0-4 "cite it").
CITATIONS = (
    ("mojev/evaluate.py", 40, "def load_packed(checkpoint: str, device: torch.device):"),
    ("mojev/evaluate.py", 53, "model = PackedScorer.from_pretrained(checkpoint).to(device).eval()"),
    ("mojev/serve.py", 142, "class Engine:"),
    ("mojev/serve.py", 169, "self.processor = AutoProcessor.from_pretrained("),
    ("mojev/serve.py", 171, "trust_remote_code=True,"),
    ("mojev/serve.py", 193, "order = sort_candidates(options)"),
    ("mojev/serve.py", 196, "menus.append(tuple(options[i] for i in order))"),
    ("mojev/serve.py", 219, "logits = self.model(batch)[0]"),
    ("mojev/serve.py", 225, "probabilities = unsort(order, row.softmax(-1).tolist())"),
    ("mojev/full.py", 83, "return sorted(range(len(options)), key=lambda index: options[index])"),
    ("mojev/full.py", 167, "contexts = tokenizer([e.context for e in examples], truncation=True,"),
)
SORT_SITE = {
    "sort": "mojev/full.py:70-83 sort_candidates orders a menu by candidate text",
    "on_this_path": "mojev/serve.py:193 order = sort_candidates(options) in Engine.answer; :196 packs the sorted "
                    "menu; :225 unsort(order, ...) maps the probabilities back to the caller's order",
    "probe_path": "Engine.answer (mojev/serve.py:182-231), called unmodified",
}
ORDER_METHOD = (
    "The sort makes a plain reorder invisible: the control requests list the same answers in shuffled orders. "
    "To move an answer inside the packed input, every answer carries a leading label and the label decides its "
    "sorted slot. The label text moves with the slot, so a change mixes the slot effect with the label text."
)


def cell_id(tokens, candidates, dtype):
    return f"{tokens}x{candidates}/{dtype}"


CELL_IDS = tuple(cell_id(t, c, d) for t in STATE_TOKENS for c in CANDIDATE_COUNTS for d in DTYPES)
BLOCKS = ("g0_3_truncation", "g0_4_order", "g0_5_determinism")
MEASURED = ("OK", "TIMEOUT", "RSS_CAP")


class Refusal(Exception):
    """A named refusal: the probe stops rather than measure the wrong thing."""

    def __init__(self, code, detail):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail = code, detail


class HollowResult(Exception):
    """The writer's refusal of an incomplete result; every problem is named."""

    def __init__(self, problems):
        super().__init__("G0 result refused (hollow): " + ", ".join(problems))
        self.problems = list(problems)


# ---------------------------------------------------------------- plan

def order_plan(seed=SEED, n=ORDER_CANDIDATES):
    """G0-4 orderings (D-3): the listed order plus seeded shuffles; identity plus seeded label assignments."""
    rng = random.Random(seed)

    def shuffled():
        perm = list(range(n))
        rng.shuffle(perm)
        return perm

    controls = [list(range(n))] + [shuffled() for _ in range(ORDER_CONTROLS)]
    labelings = [list(range(n))] + [shuffled() for _ in range(ORDER_LABELINGS)]
    return controls, labelings


def build_plan():
    """Every task in run order, cheap first: 2k and 4k cells, G0-5 fresh, G0-4, 8k and 16k cells, G0-3."""
    controls, labelings = order_plan()

    def cell(t, c, d, runs=RUNS, tid=None):
        return {"task": "cell", "id": tid or cell_id(t, c, d), "tokens": t, "candidates": c, "dtype": d, "runs": runs}

    tasks = [cell(t, c, d) for t in STATE_TOKENS[:2] for c in CANDIDATE_COUNTS for d in DTYPES]
    t, c = DETERMINISM_CELL
    tasks += [cell(t, c, d, runs=1, tid=f"g0_5-fresh/{t}x{c}/{d}") for d in DTYPES]
    tasks += [{"task": "order", "id": f"g0_4/{d}", "tokens": ORDER_TOKENS, "candidates": ORDER_CANDIDATES,
               "dtype": d, "controls": controls, "labelings": labelings} for d in DTYPES]
    tasks += [cell(t, c, d) for t in STATE_TOKENS[2:] for c in CANDIDATE_COUNTS for d in DTYPES]
    tasks += [{"task": "truncation", "id": f"g0_3/{d}", "tokens": TRUNC_STATE_TOKENS, "budget": TRUNC_BUDGET,
               "candidates": TRUNC_CANDIDATES, "dtype": d} for d in DTYPES]
    return tasks


def requests_in(task):
    if task["task"] == "cell":
        return task["runs"]
    if task["task"] == "order":
        return len(task["controls"]) + len(task["labelings"])
    return 3


def describe_plan(tasks):
    lines = [
        f"question: {QUESTION} (one question per request, through Engine.answer)",
        "candidates (5 = the first five, 10 = the first ten, 16 = all):",
    ]
    lines += [f"  {i + 1:2d}. {a}" for i, a in enumerate(ANSWERS)]
    lines.append(f"G0-4 labels (answer i gets LABELS[assignment[i]]): {' '.join(label.strip() for label in LABELS)}")
    lines.append("tasks, in run order (one process each):")
    for i, t in enumerate(tasks, 1):
        head = f"  {i:02d} {t['id']}:"
        if t["task"] == "cell":
            runs = "warm-up + 3 timed runs" if t["runs"] == RUNS else "1 run (G0-5 fresh process)"
            lines.append(f"{head} state = first {t['tokens']} tokens (exact), candidates = first {t['candidates']}, {runs}")
        elif t["task"] == "order":
            lines.append(f"{head} state = first {t['tokens']} tokens, {t['candidates']} candidates, seed {SEED}")
            lines += [f"       control-{k} (listed order of answers): {o}" for k, o in enumerate(t["controls"])]
            lines += [f"       label-{k} (answer i -> slot): {a}" for k, a in enumerate(t["labelings"])]
        else:
            lines.append(f"{head} state = first {t['tokens']} tokens; head cut = its first {t['budget']}; tail cut = "
                         f"its last {t['budget']}; budget = checkpoint context_tokens ({t['budget']} planned); "
                         f"candidates = first {t['candidates']}")
    n_cells = sum(1 for t in tasks if t["id"] in CELL_IDS)
    lines.append(f"matrix cells: {n_cells} (planned {len(CELL_IDS)}); tasks: {len(tasks)}; model loads: {len(tasks)}; "
                 f"scored requests: {sum(requests_in(t) for t in tasks)}")
    lines.append(f"limits: {THREADS} threads, nice >= {NICE}, {PHASE_TIMEOUT_S:.0f} s per load or run, "
                 f"RSS cap {RSS_CAP_KB} kB (32 GiB); child env {CHILD_ENV}")
    return lines


# ---------------------------------------------------------------- G0-1 integrity (parent, before any load)

def sha256_file(path, chunk=8 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                return h.hexdigest()
            h.update(block)


def check_weights(path, expected_size=WEIGHTS_SIZE, expected_sha256=WEIGHTS_SHA256):
    """Size, then sha256, against the pin. Any mismatch is a Refusal; nothing is loaded."""
    path = Path(path)
    try:
        size = path.stat().st_size
        if size != expected_size:
            raise Refusal("G0-1", f"{path.name} size {size} != pinned {expected_size}")
        t0 = time.monotonic()
        digest = sha256_file(path)
    except OSError as exc:
        raise Refusal("G0-1", f"{path} unreadable: {exc}") from exc
    if digest != expected_sha256:
        raise Refusal("G0-1", f"{path.name} sha256 {digest} != pinned {expected_sha256}")
    return {"path": str(path), "size": size, "sha256": digest, "expected_size": expected_size,
            "expected_sha256": expected_sha256, "verified": True, "hash_s": round(time.monotonic() - t0, 3)}


def check_code(pin, expected_head=CODE_HEAD):
    """The MoJev checkout must be the pinned commit with no tracked change."""
    def git(*args):
        return subprocess.run(["git", "-C", str(pin), *args], capture_output=True, text=True)

    head = git("rev-parse", "HEAD")
    if head.returncode != 0:
        raise Refusal("G0-1", f"{pin} is not a readable git checkout: {head.stderr.strip()}")
    sha = head.stdout.strip()
    if sha != expected_head:
        raise Refusal("G0-1", f"code HEAD {sha} != pinned {expected_head}")
    status = git("status", "--porcelain", "--untracked-files=no")
    changed = [line for line in status.stdout.split("\n") if line.strip()]
    if status.returncode != 0 or changed:
        raise Refusal("G0-1", f"code checkout has tracked changes: {changed[:5]} (git rc {status.returncode})")
    return {"pin": str(pin), "head": sha, "expected_head": expected_head, "tracked_changes": 0, "verified": True}


def snapshot_files(snapshot):
    """Size and sha256 of every top-level file of the snapshot except the weights (hashed by check_weights)."""
    return {p.name: {"size": p.stat().st_size, "sha256": sha256_file(p)}
            for p in sorted(Path(snapshot).iterdir()) if p.name != WEIGHTS_FILE and p.is_file()}


def verify_citations(pin):
    rows = []
    for rel, line, expected in CITATIONS:
        try:
            lines = (Path(pin) / rel).read_text(encoding="utf-8").split("\n")  # not splitlines(): AF-AP-132
            found = lines[line - 1].strip() if line <= len(lines) else None
        except OSError as exc:
            found = f"unreadable: {exc}"
        rows.append({"at": f"{rel}:{line}", "expected": expected, "found": found, "ok": found == expected})
    return rows


def read_source(repo, rev):
    """D-3: the committed state text as git stores it (bytes, no newline translation)."""
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{TEXT_PATH}"], capture_output=True)
    if proc.returncode != 0:
        raise Refusal("text-source", f"git show {rev}:{TEXT_PATH}: {proc.stderr.decode('utf-8', 'replace').strip()}")
    data = proc.stdout
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Refusal("text-source", f"{rev}:{TEXT_PATH} is not UTF-8: {exc}") from exc
    commit = subprocess.run(["git", "-C", str(repo), "rev-parse", f"{rev}^{{commit}}"],
                            capture_output=True, text=True).stdout.strip()
    return data, {"rev": rev, "commit": commit, "path": TEXT_PATH, "bytes": len(data),
                  "sha256": hashlib.sha256(data).hexdigest(),
                  "image_markers": sum(text.count(m) for m in IMAGE_MARKERS)}


# ---------------------------------------------------------------- parent: one child per task (D-4)

def child_env(base, pin):
    env = dict(base)
    env.update(CHILD_ENV)
    env["PYTHONPATH"] = os.pathsep.join(p for p in (str(pin), env.get("PYTHONPATH", "")) if p)
    return env


def proc_status_kb(pid, key):
    """VmRSS / VmHWM (kB) from /proc/<pid>/status; None when the process or the field is gone."""
    try:
        with open(f"/proc/{pid}/status", encoding="ascii", errors="replace") as fh:
            for line in fh:
                if line.startswith(key + ":"):
                    return int(line.split()[1])
    except OSError:
        return None
    return None


def _parse_event(raw):
    try:
        event = json.loads(raw)
    except ValueError:
        return None
    return event if isinstance(event, dict) and isinstance(event.get("event"), str) else None


def _stop(proc, grace_s=5.0):
    """Stop one child by pid: SIGTERM, then SIGKILL after the grace. Returns the signal used, or None."""
    if proc.poll() is not None:
        return None
    proc.terminate()
    try:
        proc.wait(timeout=grace_s)
        return "SIGTERM"
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return "SIGKILL"


def _tail(path, n=40):
    try:
        lines = Path(path).read_bytes().decode("utf-8", "replace").split("\n")
    except OSError:
        return []
    return [line[:300] for line in lines if line.strip()][-n:]


def run_child(argv, env, stderr_path, task_id, timeout_s=PHASE_TIMEOUT_S, rss_cap_kb=RSS_CAP_KB, poll_s=POLL_S):
    """Run one child; read its events; stop it past the phase limit, after silence past it, or over the RSS cap."""
    t0 = time.monotonic()
    events, noise, stop, max_rss, buf = [], [], None, 0, b""
    phase, phase_t0, last_phase, last_t = None, None, None, t0
    eof = False
    with open(stderr_path, "wb") as err:
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=err, env=env)
    fd = proc.stdout.fileno()
    sel = selectors.DefaultSelector()
    sel.register(fd, selectors.EVENT_READ)
    try:
        while not eof:
            if sel.select(timeout=poll_s):
                chunk = os.read(fd, 1 << 16)
                eof = not chunk
                *lines, buf = (buf + chunk).split(b"\n")
                for raw in lines:
                    event = _parse_event(raw)
                    if event is None:
                        if raw.strip() and len(noise) < 20:
                            noise.append(raw.decode("utf-8", "replace")[:300])
                        continue
                    events.append(event)
                    last_t = time.monotonic()
                    if event["event"] == "phase" and event.get("state") == "start":
                        phase, phase_t0 = event.get("phase"), last_t
                    elif event["event"] == "phase":
                        last_phase, phase, phase_t0 = phase, None, None
            now = time.monotonic()
            rss = proc_status_kb(proc.pid, "VmRSS")
            if rss is not None:
                max_rss = max(max_rss, rss)
                if rss > rss_cap_kb:
                    stop = {"status": "RSS_CAP", "phase": phase or f"after {last_phase}", "rss_kb_at_stop": rss,
                            "rss_cap_kb": rss_cap_kb, "elapsed_s": round(now - (phase_t0 or last_t), 3)}
                    break
            ref = phase_t0 if phase_t0 is not None else last_t
            if not eof and now - ref > timeout_s:
                stop = {"status": "TIMEOUT", "phase": phase or f"after {last_phase}", "elapsed_s": round(now - ref, 3),
                        "limit_s": timeout_s}
                break
    finally:
        sel.close()
        signal_used = _stop(proc) if (stop is not None or not eof) else None
        if stop is not None:
            stop["signal"] = signal_used
        try:
            exit_code = proc.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            _stop(proc)
            exit_code = proc.wait()
        proc.stdout.close()
    if buf.strip() and len(noise) < 20:
        noise.append(buf.decode("utf-8", "replace")[:300])
    return record_from_events(task_id, events, exit_code=exit_code, stop=stop, elapsed_s=round(time.monotonic() - t0, 3),
                              parent_max_rss_kb=max_rss, stderr_tail=_tail(stderr_path), noise=noise)


def record_from_events(task_id, events, *, exit_code, stop, elapsed_s, parent_max_rss_kb, stderr_tail=(), noise=()):
    """One task's record from its child's events (live, or collected in-process by the tests)."""
    phases, final, refusal, error = {}, None, None, None
    for ev in events:
        kind = ev.get("event")
        if kind == "phase" and ev.get("state") == "end":
            phases[ev.get("phase")] = ev.get("data") or {}
        elif kind == "result":
            final = ev.get("data") or {}
        elif kind == "refusal":
            refusal = {"code": ev.get("code"), "detail": ev.get("detail")}
        elif kind == "error":
            error = ev.get("detail")
    if stop is not None:
        status = stop["status"]
    elif refusal is not None:
        status = "REFUSED"
    elif final is not None and exit_code == 0:
        status = "OK"
    else:
        status = "ERROR"
    return {"task": task_id, "status": status, "phases": phases, "final": final, "stop": stop, "refusal": refusal,
            "error": error, "exit_code": exit_code, "elapsed_s": elapsed_s, "parent_max_rss_kb": parent_max_rss_kb,
            "stderr_tail": [] if status == "OK" else list(stderr_tail), "noise": list(noise)}


# ---------------------------------------------------------------- child: one task in its own process

def child_main(spec_json):
    """Events go out on a private copy of fd 1; anything a library prints lands in the stderr log."""
    spec = json.loads(spec_json)
    os.environ.update(CHILD_ENV)  # torch, tokenizers and huggingface_hub read these at import: set before any import
    current = os.nice(0)
    if current < NICE:
        os.nice(NICE - current)
    stream = os.fdopen(os.dup(1), "w", buffering=1, encoding="utf-8")
    os.dup2(2, 1)

    def emit(event):
        stream.write(json.dumps(event, sort_keys=True, allow_nan=False) + "\n")
        stream.flush()

    try:
        run_child_task(spec, load_engine, emit)
    except Refusal as r:
        emit({"event": "refusal", "code": r.code, "detail": r.detail})
        return 3
    except Exception:  # a real failure: the traceback is the record, never swallowed
        emit({"event": "error", "detail": traceback.format_exc()[-6000:]})
        return 1
    return 0


def run_child_task(spec, loader, emit, clock=time.perf_counter_ns, status=None):
    """Load, cut the state(s), score every request of the task, emitting one start/end event pair per phase."""
    status = status or (lambda key: proc_status_kb("self", key))
    emit({"event": "phase", "phase": "load", "state": "start"})
    engine, facts = loader(spec)
    facts = dict(facts, rss_after_load_kb=status("VmRSS"), hwm_after_load_kb=status("VmHWM"))
    emit({"event": "phase", "phase": "load", "state": "end", "data": facts})
    emit({"event": "phase", "phase": "setup", "state": "start"})
    source = read_verified_source(spec)
    if spec["task"] == "truncation":
        with capture_reports() as reported:
            setup, requests = prepare_requests(spec, engine, source)
        setup["reported"] = reported
    else:
        setup, requests = prepare_requests(spec, engine, source)
    emit({"event": "phase", "phase": "setup", "state": "end", "data": setup})
    for name, state, candidates, extra in requests:
        emit({"event": "phase", "phase": name, "state": "start"})
        if spec["task"] == "truncation":
            with capture_reports() as reported:
                result = score_request(engine, state, candidates, clock)
            result["reported"] = reported
        else:
            result = score_request(engine, state, candidates, clock)
        result.update(extra)
        expected = spec["budget"] if spec["task"] == "truncation" else spec["tokens"]
        if name != "full" and result["context_tokens_in_batch"] != expected:
            raise Refusal("state-tokens", f"{name}: {result['context_tokens_in_batch']} state tokens in the batch, "
                                          f"planned {expected}")
        emit({"event": "phase", "phase": name, "state": "end", "data": result})
    emit({"event": "result", "data": {"hwm_end_kb": status("VmHWM"), "rss_end_kb": status("VmRSS")}})


def read_verified_source(spec):
    data = Path(spec["source_path"]).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != spec["source_sha256"]:
        raise Refusal("text-source", f"{spec['source_path']} sha256 {digest} != {spec['source_sha256']}")
    return data.decode("utf-8")


def describe_text(text, tokens):
    return {"tokens": tokens, "chars": len(text), "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}


def prepare_requests(spec, engine, source):
    """The task's states, cut exactly (D-3), and its requests as (phase, state, candidates, extra) tuples."""
    tok, kind, n = engine.tokenizer, spec["task"], spec["candidates"]
    if kind == "truncation":
        budget = spec["budget"]
        if engine.context_tokens != budget:
            raise Refusal("budget", f"checkpoint context_tokens {engine.context_tokens} != planned {budget}")
        state = cut_head(tok, source, spec["tokens"])
        ids = tok([state])["input_ids"][0]
        head, tail = cut_head(tok, state, budget), cut_tail(tok, state, budget)
        head_ids, tail_ids = tok([head])["input_ids"][0], tok([tail])["input_ids"][0]
        setup = {"state": describe_text(state, len(ids)), "budget": budget,
                 "truncation_side": getattr(tok, "truncation_side", None),
                 "first_digest": ids_digest(ids[:budget]), "last_digest": ids_digest(ids[-budget:]),
                 "head_cut": dict(describe_text(head, len(head_ids)), digest=ids_digest(head_ids),
                                  equals_first=head_ids == ids[:budget]),
                 "tail_cut": dict(describe_text(tail, len(tail_ids)), digest=ids_digest(tail_ids),
                                  equals_last=tail_ids == ids[-budget:])}
        menu = list(ANSWERS[:n])
        requests = [("full", state, menu, {}), ("head", head, menu, {}), ("tail", tail, menu, {})]
    else:
        state = cut_head(tok, source, spec["tokens"])
        setup = {"state": describe_text(state, spec["tokens"])}
        if kind == "cell":
            requests = [(f"run-{k}", state, list(ANSWERS[:n]), {}) for k in range(spec["runs"])]
        else:
            requests = [(f"control-{k}", state, [ANSWERS[j] for j in order], {"order": order})
                        for k, order in enumerate(spec["controls"])]
            requests += [(f"label-{k}", state, [LABELS[a] + ANSWERS[i] for i, a in enumerate(assignment)],
                          {"assignment": assignment}) for k, assignment in enumerate(spec["labelings"])]
    for name, text, _, _ in requests:
        hits = [m for m in IMAGE_MARKERS if m in text]
        if hits:
            raise Refusal("image-marker", f"{name} state holds {hits}: the collator would take the image path")
    prompt = engine._Field(QUESTION, "choice", tuple(sorted(requests[0][2])), "").prompt
    setup["field_prompt"] = {"text": prompt, "tokens_untruncated": count_tokens(tok, prompt), "cap": FIELD_PROMPT_CAP}
    setup["candidates"] = requests[0][2]
    return setup, requests


def ids_digest(ids):
    return hashlib.sha256(json.dumps(list(ids), separators=(",", ":")).encode()).hexdigest()


def count_tokens(tok, text):
    """The state's length as packed_collate counts it: the same call, minus the cap (mojev/full.py:167-168)."""
    return len(tok([text])["input_ids"][0])


def _scan(span):
    yield 0
    for d in range(1, span + 1):
        yield -d
        yield d


def _offsets(tok, text, n):
    """Token offsets of a prefix long enough for n tokens, else of the whole text. Every cut is re-counted, so an
    offset near the end of the prefix window can cost a scan step but never an inexact count."""
    window = text[:max(4096, 8 * n)]
    offsets = tok(window, add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"]
    if len(offsets) < n and len(window) < len(text):
        offsets = tok(text, add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"]
    return offsets


def cut_head(tok, text, n, span=64):
    """A prefix of text, cut at a token end, that counts exactly n tokens (D-3); a Refusal when none is near."""
    extra = count_tokens(tok, "")
    offsets = _offsets(tok, text, n - extra)
    if len(offsets) < n - extra:
        raise Refusal("state-source-too-short", f"{len(offsets)} tokens < {n}")
    for d in _scan(span):
        k = n - extra + d
        if 1 <= k <= len(offsets):
            cut = text[:offsets[k - 1][1]]
            if count_tokens(tok, cut) == n:
                return cut
    raise Refusal("exact-cut-failed", f"no prefix counts exactly {n} tokens within {span} tokens of the naive cut")


def cut_tail(tok, text, n, span=64):
    """A suffix of text, cut at a token start, that counts exactly n tokens; a Refusal when none is near."""
    extra = count_tokens(tok, "")
    offsets = tok(text, add_special_tokens=False, return_offsets_mapping=True)["offset_mapping"]
    if len(offsets) < n - extra:
        raise Refusal("state-source-too-short", f"{len(offsets)} tokens < {n}")
    for d in _scan(span):
        j = len(offsets) - (n - extra) + d
        if 0 <= j < len(offsets):
            cut = text[offsets[j][0]:]
            if count_tokens(tok, cut) == n:
                return cut
    raise Refusal("exact-cut-failed", f"no suffix counts exactly {n} tokens within {span} tokens of the naive cut")


def score_request(engine, state, candidates, clock=time.perf_counter_ns):
    """One decision through Engine.answer, unmodified. Candidates are choice criteria with no description, which
    option_texts scores as the bare key (mojev/serve.py:83-93); build_answer maps them back (serve.py:122-127)."""
    questions = {QUESTION: {"type": "choice", "criteria": {c: None for c in candidates}}}
    t0 = clock()
    answers, usage = engine.answer(state, questions)
    wall_ns = clock() - t0
    answer = answers[QUESTION]
    raw = [answer["probabilities"][c] for c in candidates]
    finite = all(isinstance(p, float) and math.isfinite(p) for p in raw)
    result = {"wall_ms": wall_ns / 1e6, "forward_ms": engine.model.forward_ns / 1e6,
              "probabilities": raw if finite else [repr(p) for p in raw], "nonfinite": not finite,
              "choice": answer["choice"], "usage_input_tokens": usage["input_tokens"]}
    result.update(batch_facts(engine.model.batch))
    return result


def batch_facts(batch):
    """What packed_collate built (mojev/full.py:196-217): state and field spans from the start of the row."""
    ids = batch["packed_ids"].tolist()[0]
    live = sum(1 for v in batch["packed_mask"].tolist()[0] if v)
    state = sum(1 for v in batch["context_span"].tolist()[0] if v > 0)
    field = sum(1 for v in batch["field_span"].tolist()[0][0] if v > 0)
    return {"packed_tokens": live, "context_tokens_in_batch": state, "field_prompt_tokens": field,
            "packed_digest": ids_digest(ids[:live]), "context_digest": ids_digest(ids[:state])}


@contextlib.contextmanager
def capture_reports(limit=40):
    """G0-3: everything a caller could see during one step: warnings, log records, and text on fds 1 and 2."""
    import logging
    import warnings

    out = {"warnings": [], "log_records": [], "stdio": [], "any": False}

    class _Keep(logging.Handler):
        def emit(self, record):
            if len(out["log_records"]) < limit:
                out["log_records"].append(f"{record.name} {record.levelname}: {record.getMessage()}"[:500])

    keep = _Keep()
    loggers = [logging.getLogger(), logging.getLogger("transformers")]
    for logger in loggers:
        logger.addHandler(keep)
    sys.stdout.flush()
    sys.stderr.flush()
    saved = [os.dup(1), os.dup(2)]
    sink = tempfile.TemporaryFile()
    os.dup2(sink.fileno(), 1)
    os.dup2(sink.fileno(), 2)
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            yield out
        out["warnings"] = [f"{w.category.__name__}: {w.message}"[:500] for w in caught[:limit]]
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        os.dup2(saved[0], 1)
        os.dup2(saved[1], 2)
        for fd in saved:
            os.close(fd)
        for logger in loggers:
            logger.removeHandler(keep)
        sink.seek(0)
        text = sink.read().decode("utf-8", "replace")
        sink.close()
        out["stdio"] = [line[:500] for line in text.split("\n") if line.strip()][:limit]
        os.write(2, text.encode("utf-8"))  # the child's stderr log keeps it too
        out["any"] = bool(out["warnings"] or out["log_records"] or out["stdio"])


class _ForwardRecorder:
    """Stands in for Engine.model: runs the real model, keeps the batch it was given, times the forward."""

    def __init__(self, model):
        self.model, self.batch, self.forward_ns = model, None, None

    def __call__(self, batch):
        self.batch = batch
        t0 = time.perf_counter_ns()
        out = self.model(batch)
        self.forward_ns = time.perf_counter_ns() - t0
        return out


def numel_by_dtype(params):
    counts = {}
    for p in params:
        counts[str(p.dtype)] = counts.get(str(p.dtype), 0) + p.numel()
    return counts


def check_dtypes(variant, dtypes):
    """D-2: the variant must have taken. The head is fp32 in both (mojev/modeling.py:118-120)."""
    head, encoder = dtypes["head"], dtypes["encoder"]
    if set(head) != {"torch.float32"}:
        raise Refusal("dtype-variant", f"{variant}: head parameters {head}, expected torch.float32 only")
    if variant == "fp32" and set(encoder) != {"torch.float32"}:
        raise Refusal("dtype-variant", f"fp32: encoder parameters {encoder} after the cast")
    if variant == "released_bf16" and "torch.bfloat16" not in encoder:
        raise Refusal("dtype-variant", f"released_bf16: encoder parameters {encoder}, no torch.bfloat16")
    if variant not in DTYPES:
        raise Refusal("dtype-variant", f"unknown variant {variant}")


def load_engine(spec):
    """The real loader, PC only (D-1). The only place torch, transformers and mojev are imported."""
    import torch

    torch.set_num_threads(spec["threads"])
    pin = Path(spec["pin"]).resolve()
    snapshot = str(Path(spec["snapshot"]).resolve())
    sys.path.insert(0, str(pin))
    import mojev
    import transformers
    from mojev.evaluate import load_packed
    from mojev.schema import Field, Schema
    from mojev.serve import Engine
    from transformers import AutoProcessor

    origin = Path(mojev.__file__).resolve()
    if pin not in origin.parents:
        raise Refusal("mojev-origin", f"imported {origin}, not under --pin {pin}")
    if torch.get_num_threads() != spec["threads"]:
        raise Refusal("threads", f"torch.get_num_threads() = {torch.get_num_threads()}, planned {spec['threads']}")
    if torch.cuda.is_available():
        raise Refusal("cuda-visible", "torch sees a CUDA device; this probe is CPU only (CUDA_VISIBLE_DEVICES=)")
    device = torch.device("cpu")
    t0 = time.perf_counter()
    model, trained, config = load_packed(snapshot, device)
    load_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    if spec["dtype"] == "fp32":
        model.encoder.to(torch.float32)
    cast_s = time.perf_counter() - t0
    head = (p for m in (model.option_proj, model.context_proj, model.norm) for p in m.parameters())
    dtypes = {"encoder": numel_by_dtype(model.encoder.parameters()), "head": numel_by_dtype(head)}
    check_dtypes(spec["dtype"], dtypes)
    t0 = time.perf_counter()
    try:
        processor = AutoProcessor.from_pretrained(snapshot, trust_remote_code=False)
    except Exception as exc:  # D-1: stop and report; never retry with remote code
        raise Refusal("processor", f"AutoProcessor.from_pretrained(trust_remote_code=False): "
                                   f"{type(exc).__name__}: {exc}") from exc
    processor_load_s = time.perf_counter() - t0
    # Engine.__init__ (mojev/serve.py:151-180) minus its trust_remote_code=True: the attributes answer() reads.
    engine = Engine.__new__(Engine)
    engine.device = device
    engine.model = _ForwardRecorder(model)
    engine.config = config
    engine.context_tokens = config.context_tokens
    engine.processor = processor
    engine.tokenizer = processor.tokenizer
    engine.trained_schema = trained
    engine._Field, engine._Schema = Field, Schema
    try:
        import numpy
        numpy_version = numpy.__version__
    except ImportError:
        numpy_version = None
    cpu = getattr(torch.backends, "cpu", None)
    environ = dict(os.environ)
    env = {"python": sys.version.split()[0], "executable": sys.executable, "torch": torch.__version__,
           "transformers": transformers.__version__, "numpy": numpy_version, "threads": torch.get_num_threads(),
           "interop_threads": torch.get_num_interop_threads(), "nice": os.nice(0),
           "cpu_capability": cpu.get_cpu_capability() if hasattr(cpu, "get_cpu_capability") else None,
           "env_vars": {k: environ.get(k) for k in sorted(CHILD_ENV)}, "mojev_file": str(origin),
           "attn_implementation": getattr(model.encoder.config, "_attn_implementation", None),
           "processor_class": type(processor).__name__, "tokenizer_class": type(processor.tokenizer).__name__,
           "truncation_side": getattr(processor.tokenizer, "truncation_side", None),
           "context_tokens": config.context_tokens}
    return engine, {"load_s": load_s, "cast_s": cast_s, "processor_load_s": processor_load_s, "dtypes": dtypes,
                    "dtype_variant": spec["dtype"], "env": env}


# ---------------------------------------------------------------- analysis (parent, pure)

def _finite(values):
    return isinstance(values, list) and all(isinstance(x, float) and math.isfinite(x) for x in values)


def compare(a, b):
    """Bitwise equality (float.hex) and the largest absolute difference of two probability lists."""
    if not (_finite(a) and _finite(b)) or len(a) != len(b) or not a:
        return {"comparable": False, "bitwise_equal": False, "max_abs_diff": None}
    return {"comparable": True, "bitwise_equal": all(x.hex() == y.hex() for x, y in zip(a, b)),
            "max_abs_diff": max(abs(x - y) for x, y in zip(a, b))}


def compare_all(vectors):
    vectors = [v for v in vectors if v is not None]
    if len(vectors) < 2:
        return {"count": len(vectors), "comparable": False, "bitwise_equal": None, "max_abs_diff": None}
    pairs = [compare(vectors[0], v) for v in vectors[1:]]
    comparable = all(p["comparable"] for p in pairs)
    return {"count": len(vectors), "comparable": comparable,
            "bitwise_equal": all(p["bitwise_equal"] for p in pairs) if comparable else None,
            "max_abs_diff": max(p["max_abs_diff"] for p in pairs) if comparable else None}


def argmax(values):
    return max(range(len(values)), key=values.__getitem__) if _finite(values) and values else None


RUN_KEYS = ("wall_ms", "forward_ms", "choice", "usage_input_tokens", "packed_tokens", "context_tokens_in_batch",
            "field_prompt_tokens", "packed_digest", "context_digest", "nonfinite")


def assemble_cell(task, rec):
    ph = rec["phases"]
    load, setup = ph.get("load") or {}, ph.get("setup") or {}
    runs = [ph[f"run-{k}"] for k in range(task["runs"]) if f"run-{k}" in ph]
    cell = {"id": task["id"], "tokens": task["tokens"], "candidates": task["candidates"], "dtype": task["dtype"],
            "status": rec["status"], "elapsed_s": rec["elapsed_s"], "parent_max_rss_kb": rec["parent_max_rss_kb"],
            "load_s": load.get("load_s"), "cast_s": load.get("cast_s"), "processor_load_s": load.get("processor_load_s"),
            "rss_after_load_kb": load.get("rss_after_load_kb"), "hwm_after_load_kb": load.get("hwm_after_load_kb"),
            "dtypes": load.get("dtypes"), "state": setup.get("state"), "field_prompt": setup.get("field_prompt"),
            "runs": [{k: r.get(k) for k in RUN_KEYS} for r in runs],
            "probabilities": [r.get("probabilities") for r in runs],
            "in_process": compare_all([r.get("probabilities") for r in runs])}
    timed = [r["wall_ms"] for r in runs[1:]]
    cell["warmup_ms"] = runs[0]["wall_ms"] if runs else None
    cell["runs_ms"] = timed
    if rec["status"] == "OK" and timed:
        cell.update(p50_ms=statistics.median(timed), max_ms=max(timed), peak_rss_kb=(rec["final"] or {}).get("hwm_end_kb"))
    else:
        cell.update(p50_ms=None, max_ms=None, peak_rss_kb=None)
    if rec["status"] != "OK":
        cell.update(stop=rec["stop"], refusal=rec["refusal"], error=rec["error"], stderr_tail=rec["stderr_tail"])
    return cell


def _slim(req):
    return {k: req.get(k) for k in RUN_KEYS + ("probabilities",)}


def assemble_truncation(task, rec):
    ph = rec["phases"]
    setup = ph.get("setup") or {}
    reqs = {n: ph[n] for n in ("full", "head", "tail") if n in ph}
    block = {"id": task["id"], "dtype": task["dtype"], "status": rec["status"], "state_tokens_planned": task["tokens"],
             "budget": task["budget"], "candidates": task["candidates"], "setup": setup,
             "requests": {n: _slim(r) for n, r in reqs.items()},
             "reported": {n: r.get("reported") for n, r in reqs.items()}}
    if rec["status"] == "OK" and len(reqs) == 3:
        full = reqs["full"]["context_digest"]
        block["kept"] = ("first" if full == setup["first_digest"] else "last" if full == setup["last_digest"]
                         else "neither")
        block["dropped_tokens"] = setup["state"]["tokens"] - reqs["full"]["context_tokens_in_batch"]
        block["compare"] = {"full_vs_head": compare(reqs["full"]["probabilities"], reqs["head"]["probabilities"]),
                            "full_vs_tail": compare(reqs["full"]["probabilities"], reqs["tail"]["probabilities"])}
        block["usage_input_tokens"] = {n: r["usage_input_tokens"] for n, r in reqs.items()}
    else:
        block.update(stop=rec["stop"], refusal=rec["refusal"], error=rec["error"])
    return block


def _by_answer(order, probabilities):
    out = [None] * len(order)
    for slot, answer in enumerate(order):
        out[answer] = probabilities[slot]
    return out


def assemble_order(task, rec):
    ph = rec["phases"]
    n = task["candidates"]
    controls = [ph.get(f"control-{k}") for k in range(len(task["controls"]))]
    labels = [ph.get(f"label-{k}") for k in range(len(task["labelings"]))]
    block = {"id": task["id"], "dtype": task["dtype"], "status": rec["status"], "tokens": task["tokens"],
             "candidates": n, "seed": SEED, "sort_site": SORT_SITE, "method": ORDER_METHOD,
             "requests": {f"{kind}-{k}": (r or {}).get("probabilities")
                          for kind, rows in (("control", controls), ("label", labels)) for k, r in enumerate(rows)}}
    complete = all(controls) and all(labels)
    if rec["status"] != "OK" or not complete:
        block.update(stop=rec["stop"], refusal=rec["refusal"], error=rec["error"])
        return block
    vectors = [_by_answer(c["order"], c["probabilities"]) if _finite(c["probabilities"]) else None for c in controls]
    block["control"] = dict(compare_all(vectors), orders=task["controls"],
                            packed_inputs_equal=len({c["packed_digest"] for c in controls}) == 1)
    probs = [row["probabilities"] for row in labels]
    labeled = {"labels": list(LABELS[:n]), "assignments": task["labelings"], "orderings": len(labels) - 1,
               "packed_digests": [row["packed_digest"] for row in labels]}
    if all(_finite(p) for p in probs):
        winners = [argmax(p) for p in probs]
        per = [{"answer": ANSWERS[i], "slots": [a[i] for a in task["labelings"]],
                "max_abs_change": max(abs(p[i] - probs[0][i]) for p in probs[1:]),
                "range": max(p[i] for p in probs) - min(p[i] for p in probs)} for i in range(n)]
        labeled.update(argmax_answers=[ANSWERS[w] for w in winners],
                       argmax_changes=sum(1 for w in winners[1:] if w != winners[0]),
                       per_candidate=per, largest_change=max(row["max_abs_change"] for row in per))
    else:
        labeled["nonfinite"] = True
    block["labeled"] = labeled
    return block


def assemble_determinism(cells, fresh):
    t, c = DETERMINISM_CELL
    out = {}
    for d in DTYPES:
        cell, again = cells.get(cell_id(t, c, d)), fresh.get(d)
        if cell is None or again is None:
            continue
        entry = {"cell": cell["id"], "fresh_task": again["id"], "threads": THREADS}
        if cell["status"] != "OK" or again["status"] != "OK":
            bad = cell if cell["status"] != "OK" else again
            entry.update(status=bad["status"], stop=bad.get("stop"), from_task=bad["id"])
        else:
            entry["status"] = "OK"
            entry["in_process"] = dict(compare_all(cell["probabilities"]),
                                       packed_inputs_equal=len({r["packed_digest"] for r in cell["runs"]}) == 1)
            entry["fresh_process"] = dict(compare(cell["probabilities"][0], again["probabilities"][0]),
                                          packed_inputs_equal=cell["runs"][0]["packed_digest"]
                                          == again["runs"][0]["packed_digest"])
        out[d] = entry
    return out


def dtype_agreement(cells, truncation, order):
    """D-2: on every request scored in both dtypes, argmax agreement and the largest probability difference."""
    a, b = DTYPES
    pairs = {}
    for t in STATE_TOKENS:
        for c in CANDIDATE_COUNTS:
            ca, cb = cells.get(cell_id(t, c, a)), cells.get(cell_id(t, c, b))
            if ca and cb and ca["probabilities"] and cb["probabilities"]:
                pairs[f"{t}x{c}"] = (ca["probabilities"][0], cb["probabilities"][0])
    for label, blocks, key in (("g0_3", truncation, "requests"), ("g0_4", order, "requests")):
        if a in blocks and b in blocks:
            for name, pa in blocks[a][key].items():
                pb = blocks[b][key].get(name)
                pa = pa.get("probabilities") if isinstance(pa, dict) else pa
                pb = pb.get("probabilities") if isinstance(pb, dict) else pb
                if pa is not None and pb is not None:
                    pairs[f"{label}:{name}"] = (pa, pb)
    rows = {}
    for key, (pa, pb) in sorted(pairs.items()):
        cmp = compare(pa, pb)
        rows[key] = {"argmax_agree": argmax(pa) == argmax(pb) if cmp["comparable"] else None,
                     "max_abs_diff": cmp["max_abs_diff"], "bitwise_equal": cmp["bitwise_equal"]}
    return rows


def projections(cells):
    """G0-6: 100 decisions at the 8,192/10 and 16,384/16 cells, per dtype, from the timed p50."""
    out = {}
    for t, c in PROJECTION_CELLS:
        for d in DTYPES:
            cell = cells.get(cell_id(t, c, d))
            if cell is None:
                continue
            row = {"status": cell["status"], "decisions": PROJECTION_DECISIONS}
            if cell["status"] == "OK":
                load = cell["load_s"] + cell["cast_s"] + cell["processor_load_s"]
                row.update(p50_s=cell["p50_ms"] / 1000, projected_s=PROJECTION_DECISIONS * cell["p50_ms"] / 1000,
                           load_total_s=load, projected_with_one_load_s=load + PROJECTION_DECISIONS * cell["p50_ms"] / 1000)
            elif cell["status"] == "TIMEOUT":
                row["projected_s_lower_bound"] = PROJECTION_DECISIONS * PHASE_TIMEOUT_S
            out[cell["id"]] = row
    return {"formula": "projected_s = 100 * p50_ms / 1000; projected_with_one_load_s adds load_s + cast_s + "
                       "processor_load_s once; a TIMEOUT cell gives only the lower bound 100 * 600 s",
            "cells": out}


def environment(records):
    seen = {}
    for rec in records.values():
        env = (rec["phases"].get("load") or {}).get("env")
        if env:
            seen[json.dumps(env, sort_keys=True)] = env
    envs = list(seen.values())
    return {"consistent": len(envs) == 1, "child": envs[0] if len(envs) == 1 else None,
            "variants": envs if len(envs) > 1 else []}


def assemble_result(tasks, records, integrity, meta):
    by_id = {t["id"]: t for t in tasks}

    def built(fn, tid):
        return fn(by_id[tid], records[tid]) if tid in records and tid in by_id else None

    cells = {cid: built(assemble_cell, cid) for cid in CELL_IDS if cid in records}
    t, c = DETERMINISM_CELL
    fresh = {d: built(assemble_cell, f"g0_5-fresh/{t}x{c}/{d}") for d in DTYPES
             if f"g0_5-fresh/{t}x{c}/{d}" in records}
    truncation = {d: built(assemble_truncation, f"g0_3/{d}") for d in DTYPES if f"g0_3/{d}" in records}
    order = {d: built(assemble_order, f"g0_4/{d}") for d in DTYPES if f"g0_4/{d}" in records}
    return {"schema": "mojev-probe-0/v1", "probe": meta.get("probe"), "host": meta.get("host"),
            "plan": meta.get("plan"), "environment": environment(records), "g0_1_integrity": integrity,
            "g0_2_matrix": {"cells": cells, "dtype_agreement": dtype_agreement(cells, truncation, order)},
            "g0_3_truncation": truncation, "g0_4_order": order,
            "g0_5_determinism": assemble_determinism(cells, fresh), "g0_6_gate1_feasibility": projections(cells)}


def _num(value, positive=True):
    ok = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    return ok and (value > 0 if positive else value >= 0)


def _stop_problems(name, entry):
    stop = entry.get("stop")
    if not isinstance(stop, dict) or not isinstance(stop.get("phase"), str) or not _num(stop.get("elapsed_s")):
        return [f"stop-without-elapsed:{name}"]
    return []


def cell_problems(cid, cell):
    status = cell.get("status")
    if status in ("TIMEOUT", "RSS_CAP"):
        return _stop_problems(cid, cell)
    if status != "OK":
        return [f"unmeasured-cell:{cid}:{status}"]
    runs = cell.get("runs_ms")
    if not (isinstance(runs, list) and len(runs) == RUNS - 1 and all(_num(r) for r in runs)):
        return [f"bad-runs:{cid}"]
    problems = []
    if cell.get("p50_ms") != statistics.median(runs) or cell.get("max_ms") != max(runs):
        problems.append(f"bad-p50-or-max:{cid}")
    for key in ("peak_rss_kb", "rss_after_load_kb"):
        if not _num(cell.get(key)):
            problems.append(f"missing-{key}:{cid}")
    if not (_num(cell.get("load_s"), positive=False) and _num(cell.get("processor_load_s"), positive=False)):
        problems.append(f"missing-load-time:{cid}")
    probs = cell.get("probabilities") or []
    if len(probs) != RUNS or any(not isinstance(p, list) or len(p) != cell.get("candidates") for p in probs):
        problems.append(f"bad-probabilities:{cid}")
    return problems


def block_problems(block, d, entry):
    name = f"{block}/{d}"
    status = entry.get("status")
    if status in ("TIMEOUT", "RSS_CAP"):
        return _stop_problems(name, entry)
    if status != "OK":
        return [f"unmeasured-block:{name}:{status}"]
    if block == "g0_3_truncation":
        compared = entry.get("compare") or {}
        if entry.get("kept") not in ("first", "last", "neither") or set(compared) != {"full_vs_head", "full_vs_tail"}:
            return [f"incomplete-block:{name}"]
    elif block == "g0_4_order":
        labeled = entry.get("labeled") or {}
        per = labeled.get("per_candidate")
        if (not isinstance(labeled.get("orderings"), int) or labeled["orderings"] < ORDER_LABELINGS
                or not isinstance(per, list) or len(per) != entry.get("candidates")
                or not isinstance(labeled.get("argmax_changes"), int) or "control" not in entry):
            return [f"incomplete-block:{name}"]
    else:
        inproc, again = entry.get("in_process") or {}, entry.get("fresh_process") or {}
        if not (isinstance(inproc.get("count"), int) and inproc["count"] >= 2 and inproc.get("comparable")
                and again.get("comparable")):
            return [f"incomplete-block:{name}"]
    return []


def validate_result(result):
    """Every problem that makes a result hollow, by name; an empty list means complete."""
    problems = []
    integrity = result.get("g0_1_integrity") or {}
    if (integrity.get("model_safetensors") or {}).get("verified") is not True:
        problems.append("integrity-not-verified")
    cells = (result.get("g0_2_matrix") or {}).get("cells") or {}
    for cid in CELL_IDS:
        if cid in cells:
            problems += cell_problems(cid, cells[cid])
        else:
            problems.append(f"missing-cell:{cid}")
    problems += [f"unexpected-cell:{cid}" for cid in sorted(set(cells) - set(CELL_IDS))]
    for block in BLOCKS:
        entries = result.get(block)
        if not isinstance(entries, dict) or not entries:
            problems.append(f"missing-block:{block}")
            continue
        for d in DTYPES:
            if d in entries:
                problems += block_problems(block, d, entries[d])
            else:
                problems.append(f"missing-block:{block}/{d}")
    feasibility = (result.get("g0_6_gate1_feasibility") or {}).get("cells") or {}
    problems += [f"missing-projection:{cell_id(t, c, d)}" for t, c in PROJECTION_CELLS for d in DTYPES
                 if cell_id(t, c, d) not in feasibility]
    return problems


def write_result(result, path):
    """Refuse a hollow result by name; otherwise write it atomically (sorted keys, no NaN)."""
    problems = validate_result(result)
    if problems:
        raise HollowResult(problems)
    path = Path(path)
    text = json.dumps(result, indent=1, sort_keys=True, allow_nan=False) + "\n"
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render_cells_md(result):
    """The cell table for MOJEV-PROBE-0.md: every p50 copied from the JSON with one decimal."""
    cells = result["g0_2_matrix"]["cells"]
    rows = ["| cell | status | p50 ms | max ms | peak RSS GiB | RSS after load GiB | load s |",
            "|---|---|---|---|---|---|---|"]
    for cid in CELL_IDS:
        c = cells.get(cid)
        if c is None:
            continue
        if c["status"] == "OK":
            rows.append(f"| {cid} | OK | {c['p50_ms']:.1f} | {c['max_ms']:.1f} | {c['peak_rss_kb'] / 1048576:.2f} | "
                        f"{c['rss_after_load_kb'] / 1048576:.2f} | {c['load_s']:.1f} |")
        else:
            stop = c.get("stop") or {}
            rows.append(f"| {cid} | {c['status']} in {stop.get('phase')} after {stop.get('elapsed_s')} s "
                        f"| - | - | - | - | - |")
    return "\n".join(rows)


# ---------------------------------------------------------------- main

def _utc(fmt="%Y-%m-%dT%H:%M:%SZ"):
    return datetime.datetime.now(datetime.timezone.utc).strftime(fmt)


def _renice(target=NICE):
    current = os.nice(0)
    if current < target:
        os.nice(target - current)
    return os.nice(0)


def host_facts():
    facts = {"nproc": os.cpu_count(), "loadavg": list(os.getloadavg())}
    for path, key, name in (("/proc/cpuinfo", "model name", "cpu_model"), ("/proc/meminfo", "MemTotal", "mem_total")):
        facts[name] = None
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    if line.startswith(key):
                        facts[name] = line.split(":", 1)[1].strip()
                        break
        except OSError:
            pass
    return facts


def _summary(rec):
    if rec["status"] == "OK":
        runs = [rec["phases"][k]["wall_ms"] for k in sorted(rec["phases"]) if k.startswith("run-")][1:]
        hwm = (rec["final"] or {}).get("hwm_end_kb")
        p50 = f" p50 {statistics.median(runs):.1f} ms" if runs else ""
        peak = f" peak {hwm / 1048576:.2f} GiB" if isinstance(hwm, int) else ""
        return f"OK{p50}{peak}"
    detail = rec["stop"] or rec["refusal"] or {"exit_code": rec["exit_code"], "error": (rec["error"] or "")[-300:]}
    return f"{rec['status']} {json.dumps(detail, sort_keys=True)}"


def run_tasks(tasks, spawn, partial, log=print):
    """spawn(task) -> record for each task in order; every record is appended to the partial log before the next
    task starts; the first refusal stops the run (D-1: a refused processor is never worked around)."""
    records = {}
    for i, task in enumerate(tasks, 1):
        rec = spawn(task)
        records[task["id"]] = rec
        with open(partial, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, sort_keys=True) + "\n")
        log(f"[{i:02d}/{len(tasks):02d}] {task['id']} {_summary(rec)} ({rec['elapsed_s']:.1f} s)")
        if rec["status"] == "REFUSED":
            return records, rec
    return records, None


def dry_run(args, tasks, source):
    lines = ["MOJEV-G0 dry run: no model, no torch import, nothing written.",
             f"probe {SCRIPT.relative_to(REPO)} sha256 {sha256_file(SCRIPT)}",
             f"state source: git show {source['rev']}:{source['path']} (commit {source['commit']}): {source['bytes']} "
             f"bytes, sha256 {source['sha256']}, image markers {source['image_markers']}"]
    rc = 0
    for label, value in (("pin", args.pin), ("snapshot", args.snapshot)):
        if value is None:
            lines.append(f"{label}: not given (required for a run)")
            continue
        path = Path(value).expanduser()
        present = path.is_dir()
        rc = rc if present else 2
        lines.append(f"{label}: {path} {'present' if present else 'MISSING'}")
        if present and label == "snapshot":
            try:
                size = (path / WEIGHTS_FILE).stat().st_size
            except OSError:
                size = None
            verdict = "size matches" if size == WEIGHTS_SIZE else "MISMATCH (a run refuses: G0-1)"
            rc = rc if size == WEIGHTS_SIZE else 2
            lines.append(f"  {WEIGHTS_FILE}: size {size}, pinned {WEIGHTS_SIZE}: {verdict}; hashed only by a real run")
        if present and label == "pin":
            bad = [row["at"] for row in verify_citations(path) if not row["ok"]]
            lines.append(f"  citations: {len(CITATIONS) - len(bad)} of {len(CITATIONS)} lines match"
                         + (f"; MISMATCH at {bad}" if bad else ""))
    lines += describe_plan(tasks)
    print("\n".join(lines))
    return rc


def main(argv=None):
    parser = argparse.ArgumentParser(description="MoJev Gate 0 probe (G0-1..G0-6).")
    parser.add_argument("--pin", help="the MoJev checkout at the pinned commit (put on PYTHONPATH)")
    parser.add_argument("--snapshot", help="the local snapshot directory at the pinned revision")
    parser.add_argument("--out", help="the result JSON; its work directory lands beside it")
    parser.add_argument("--text-rev", default=TEXT_REV, help=f"git revision of {TEXT_PATH} (default {TEXT_REV})")
    parser.add_argument("--dry-run", action="store_true", help="print the plan and exit; loads nothing")
    parser.add_argument("--only", action="append", default=[], metavar="TASK_ID", help="run only this task (repeat)")
    parser.add_argument("--child", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.child is not None:
        return child_main(args.child)
    tasks = build_plan()
    unknown = sorted(set(args.only) - {t["id"] for t in tasks})
    if unknown:
        print(f"usage: unknown task id(s) {unknown}; see --dry-run", file=sys.stderr)
        return 64
    if args.only:
        tasks = [t for t in tasks if t["id"] in args.only]
    try:
        source_bytes, source = read_source(REPO, args.text_rev)
    except Refusal as r:
        print(f"REFUSED {r}", file=sys.stderr)
        return 64
    if args.dry_run:
        return dry_run(args, tasks, source)
    missing = [f"--{name}" for name in ("pin", "snapshot", "out") if not getattr(args, name)]
    if missing:
        print(f"usage: {' '.join(missing)} required (or --dry-run)", file=sys.stderr)
        return 64
    pin, snapshot = Path(args.pin).expanduser().resolve(), Path(args.snapshot).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    started, t0 = _utc(), time.monotonic()
    try:
        integrity = {"model_safetensors": check_weights(snapshot / WEIGHTS_FILE), "code": check_code(pin),
                     "snapshot": {"dir": str(snapshot), "expected_revision": SNAPSHOT_REVISION,
                                  "files": snapshot_files(snapshot)},
                     "citations": verify_citations(pin)}
    except Refusal as r:
        print(f"REFUSED {r}", file=sys.stderr)
        return 2
    parent_nice = _renice()
    host = dict(host_facts(), parent_nice=parent_nice)
    workdir = out.parent / f"{out.name}.work-{_utc('%Y%m%dT%H%M%SZ')}"
    workdir.mkdir(parents=True)
    # Children run a frozen copy: a sync of the clone during a long run must not change the code of later tasks.
    frozen = workdir / SCRIPT.name
    frozen.write_bytes(SCRIPT.read_bytes())
    probe = {"script": str(SCRIPT.relative_to(REPO)), "script_sha256": sha256_file(frozen), "frozen_copy": str(frozen),
             "repo_head": subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True,
                                         text=True).stdout.strip(),
             "argv": sys.argv, "started_utc": started, "workdir": str(workdir)}
    source_path = workdir / "state-source.txt"
    source_path.write_bytes(source_bytes)
    partial = workdir / "partial.jsonl"
    base = {"pin": str(pin), "snapshot": str(snapshot), "source_path": str(source_path),
            "source_sha256": source["sha256"], "threads": THREADS}
    env = child_env(os.environ, pin)
    print(f"MOJEV-G0 run {started}: {len(tasks)} tasks; work directory {workdir}", flush=True)

    def spawn(task):
        return run_child([sys.executable, str(frozen), "--child", json.dumps(dict(task, **base))], env,
                         workdir / (task["id"].replace("/", "__") + ".stderr.log"), task["id"])

    records, refused = run_tasks(tasks, spawn, partial, log=lambda line: print(line, flush=True))
    if refused is not None:
        print(f"REFUSED {refused['refusal']['code']}: {refused['refusal']['detail']} (task {refused['task']}); "
              f"run stopped; records in {partial}", file=sys.stderr)
        return 3
    if args.only:
        return 0 if all(r["status"] in MEASURED for r in records.values()) else 4
    host["loadavg_end"] = list(os.getloadavg())
    probe.update(finished_utc=_utc(), wall_s=round(time.monotonic() - t0, 1))
    meta = {"host": host, "probe": probe,
            "plan": {"tasks": tasks, "question": QUESTION, "answers": list(ANSWERS), "labels": list(LABELS),
                     "seed": SEED, "text_source": source,
                     "limits": {"threads": THREADS, "nice": NICE, "phase_timeout_s": PHASE_TIMEOUT_S,
                                "rss_cap_kb": RSS_CAP_KB, "child_env": CHILD_ENV}}}
    result = assemble_result(build_plan(), records, integrity, meta)
    try:
        digest = write_result(result, out)
    except HollowResult as hollow:
        print(f"REFUSED {hollow}; records in {partial}", file=sys.stderr)
        return 4
    table = render_cells_md(result)
    (workdir / "cells.md").write_text(table + "\n", encoding="utf-8")
    print(f"wrote {out} sha256 {digest}\n{table}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
