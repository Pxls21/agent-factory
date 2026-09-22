#!/usr/bin/env python3
"""J0 FP32 latency + determinism probe for the Laya typed-decisions checkpoint.

Usage:
    python scripts/laya_probe.py \
        --checkpoint typed-decisions \
        --revision 1c5edc17a7acd8701df6fc341c0d179f1c62c982 \
        --cache /root/hf-laya-probe \
        --threads 4 --pin-cpus 0-3 --n 200 \
        --fixture tests/fixtures/decisions/probe/questions.json \
        --out docs/research/findings/laya-probe-1-sandbox.json
"""
import argparse
import hashlib
import json
import os
import sys
import time


def parse_cpu_range(s):
    """Parse '0-3' or '0,1,2,3' into a set of ints."""
    cpus = set()
    for part in s.split(","):
        if "-" in part:
            lo, hi = part.split("-", 1)
            cpus.update(range(int(lo), int(hi) + 1))
        else:
            cpus.add(int(part))
    return cpus


def get_cpu_model():
    with open("/proc/cpuinfo") as f:
        for line in f:
            if line.startswith("model name"):
                return line.split(":", 1)[1].strip()
    return "unknown"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s):
    return hashlib.sha256(s.encode()).hexdigest()


def load_fixture(path):
    with open(path) as f:
        raw = f.read()
    data = json.loads(raw)
    fixture_sha = sha256_str(raw.rstrip("\n"))
    return data["questions"], fixture_sha


def load_avg():
    with open("/proc/loadavg") as f:
        return f.read().strip()


def run_probe(agent, questions, n_per_type):
    """Run the probe: n timed calls per question type, return per-type and overall stats."""
    from collections import defaultdict

    by_type = defaultdict(list)
    for q in questions:
        by_type[q["question_type"]].append(q)

    all_latencies = []
    per_type_stats = {}
    all_prob_vectors = []
    total_tokens = 0
    total_questions = 0

    for qtype, qs in sorted(by_type.items()):
        # Use up to n questions of this type, cycling if fewer
        type_latencies = []
        type_prob_vectors = []
        for i in range(n_per_type):
            q = qs[i % len(qs)]
            state = q["state"]
            qdef = {qtype: q["question"]}

            t0 = time.perf_counter()
            result = agent.system_one(state, qdef)
            elapsed_ms = (time.perf_counter() - t0) * 1000.0

            type_latencies.append(elapsed_ms)
            all_latencies.append(elapsed_ms)

            # Extract probability vector
            ans = result["answers"][qtype]
            probs = ans.get("probabilities", {})
            # Sort by key for deterministic ordering
            prob_vec = [round(float(v), 6) for _, v in sorted(probs.items())]
            type_prob_vectors.append((qtype, i, prob_vec))
            all_prob_vectors.append((qtype, i, prob_vec))

            total_tokens += result.get("usage", {}).get("input_tokens", 0)
            total_questions += 1

        type_latencies_sorted = sorted(type_latencies)
        p50_idx = len(type_latencies_sorted) // 2
        p95_idx = int(len(type_latencies_sorted) * 0.95)
        per_type_stats[qtype] = {
            "n": len(type_latencies),
            "p50_ms": round(type_latencies_sorted[p50_idx], 2),
            "p95_ms": round(type_latencies_sorted[p95_idx], 2),
            "max_ms": round(max(type_latencies), 2),
        }

    # Overall
    all_sorted = sorted(all_latencies)
    p50_idx = len(all_sorted) // 2
    p95_idx = int(len(all_sorted) * 0.95)
    overall = {
        "n": len(all_sorted),
        "p50_ms": round(all_sorted[p50_idx], 2),
        "p95_ms": round(all_sorted[p95_idx], 2),
        "max_ms": round(max(all_sorted), 2),
    }

    mean_tokens = round(total_tokens / max(1, total_questions), 1)

    return per_type_stats, overall, all_prob_vectors, mean_tokens


def prob_vectors_digest(vectors):
    """Compute sha256 of the serialized probability vectors (6 decimals)."""
    parts = []
    for qtype, idx, vec in vectors:
        parts.append("%s:%d:%s" % (qtype, idx, ",".join("%.6f" % v for v in vec)))
    return sha256_str("\n".join(parts))


def classify_latency(p50_ms):
    if p50_ms <= 256:
        return "116-256ms"
    if p50_ms <= 464:
        return "193-464ms"
    if 1000 <= p50_ms <= 1250:
        return "1000-1250ms"
    return "other"


def main():
    parser = argparse.ArgumentParser(description="J0 FP32 latency + determinism probe")
    parser.add_argument("--checkpoint", required=True, choices=["typed-decisions", "encoder", "multilingual"])
    parser.add_argument("--revision", required=True)
    parser.add_argument("--cache", required=True)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--pin-cpus", default=None, help="CPU affinity range, e.g. 0-3")
    parser.add_argument("--n", type=int, default=200, help="Number of timed calls per question type")
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    # Print exact command line
    print("command: %s" % " ".join(sys.argv))

    # Set thread counts BEFORE importing torch
    os.environ["OMP_NUM_THREADS"] = str(args.threads)
    os.environ["MKL_NUM_THREADS"] = str(args.threads)
    os.environ["OPENBLAS_NUM_THREADS"] = str(args.threads)

    import torch
    torch.set_num_threads(args.threads)
    print("torch.get_num_threads(): %d" % torch.get_num_threads())

    # CPU pinning
    if args.pin_cpus:
        cpus = parse_cpu_range(args.pin_cpus)
        os.sched_setaffinity(0, cpus)
    affinity = sorted(os.sched_getaffinity(0))
    print("affinity: %s" % affinity)

    # Load fixture
    questions, fixture_sha = load_fixture(args.fixture)
    print("fixture: %s (%d questions, sha256=%s)" % (args.fixture, len(questions), fixture_sha))

    # Load average before
    loadavg_before = load_avg()
    print("loadavg_before: %s" % loadavg_before)

    # CPU info
    cpu_model = get_cpu_model()
    nproc = os.cpu_count()
    print("cpu: %s (%d cores)" % (cpu_model, nproc))

    # Download checkpoint
    import laya
    os.environ["HF_HOME"] = args.cache
    os.environ["TRANSFORMERS_CACHE"] = args.cache

    subfolder = args.checkpoint if args.checkpoint != "encoder" else None
    print("loading checkpoint: %s (revision=%s, subfolder=%s)" % (args.checkpoint, args.revision, subfolder))

    from huggingface_hub import snapshot_download
    local_dir = snapshot_download(
        "convaiinnovations/laya",
        revision=args.revision,
        cache_dir=args.cache,
        allow_patterns=[
            "%s/*" % args.checkpoint if args.checkpoint != "encoder" else "encoder/*",
            "model.safetensors" if args.checkpoint == "encoder" else "%s/model.safetensors" % args.checkpoint,
            "rl_agent_config.json" if args.checkpoint == "encoder" else "%s/rl_agent_config.json" % args.checkpoint,
            "tokenizer/*" if args.checkpoint == "encoder" else "%s/tokenizer/*" % args.checkpoint,
            "encoder/*" if args.checkpoint == "encoder" else "%s/encoder/*" % args.checkpoint,
            "rl_common.py",
        ],
    )

    # Find safetensors file and compute its sha
    if args.checkpoint == "encoder":
        st_path = os.path.join(local_dir, "model.safetensors")
    else:
        st_path = os.path.join(local_dir, args.checkpoint, "model.safetensors")
    safetensors_sha = sha256_file(st_path)
    print("safetensors: %s (sha256=%s)" % (st_path, safetensors_sha))

    # Load agent with FP32 forced
    agent = laya.load("convaiinnovations/laya", device="cpu", subfolder=subfolder)
    # Force FP32
    agent.model = agent.model.float()
    agent.dtype = torch.float32
    print("dtype: %s" % agent.dtype)
    print("device: %s" % agent.device)

    # Warm-up: one untimed forward pass
    print("warm-up pass...")
    warmup_q = questions[0]
    agent.system_one(warmup_q["state"], {warmup_q["question_type"]: warmup_q["question"]})
    print("warm-up done")

    # Run 1: N timed calls per type (in-process)
    print("run 1 (in-process, timed)...")
    wall_t0 = time.monotonic()
    stats1, overall1, vecs1, mean_tokens = run_probe(agent, questions, args.n)
    wall_t1 = time.monotonic()
    digest1 = prob_vectors_digest(vecs1)
    print("run 1 done: wall=%.1fs, digest=%s" % (wall_t1 - wall_t0, digest1))

    # Run 2: same process, same agent
    print("run 2 (in-process, timed)...")
    _, _, vecs2, _ = run_probe(agent, questions, args.n)
    digest2 = prob_vectors_digest(vecs2)
    print("run 2 done: digest=%s" % digest2)

    # Run 3: fresh process
    print("run 3 (fresh process)...")
    # We write a helper script and exec it
    helper_script = os.path.join(os.path.dirname(args.out) or ".", ".laya_probe_run3.py")
    with open(helper_script, "w") as hf:
        hf.write("""
import json, os, sys, hashlib, time
os.environ["OMP_NUM_THREADS"] = "%d"
os.environ["MKL_NUM_THREADS"] = "%d"
os.environ["OPENBLAS_NUM_THREADS"] = "%d"
os.environ["HF_HOME"] = "%s"
os.environ["TRANSFORMERS_CACHE"] = "%s"
import torch
torch.set_num_threads(%d)
if %r:
    os.sched_setaffinity(0, %r)
import laya
agent = laya.load("convaiinnovations/laya", device="cpu", subfolder=%r)
agent.model = agent.model.float()
agent.dtype = torch.float32
with open(%r) as f:
    questions = json.load(f)["questions"]
# warm up
q0 = questions[0]
agent.system_one(q0["state"], {q0["question_type"]: q0["question"]})
# run
from collections import defaultdict
by_type = defaultdict(list)
for q in questions:
    by_type[q["question_type"]].append(q)
all_vecs = []
for qtype, qs in sorted(by_type.items()):
    for i in range(%d):
        q = qs[i %% len(qs)]
        result = agent.system_one(q["state"], {qtype: q["question"]})
        ans = result["answers"][qtype]
        probs = ans.get("probabilities", {})
        vec = [round(float(v), 6) for _, v in sorted(probs.items())]
        all_vecs.append("%%s:%%d:%%s" %% (qtype, i, ",".join("%%.6f" %% v for v in vec)))
digest = hashlib.sha256("\\n".join(all_vecs).encode()).hexdigest()
print(digest)
""" % (args.threads, args.threads, args.threads,
       args.cache, args.cache, args.threads,
       bool(args.pin_cpus), list(affinity) if args.pin_cpus else [],
       subfolder, args.fixture, args.n))

    import subprocess
    r = subprocess.run(
        [sys.executable, helper_script],
        capture_output=True, text=True, timeout=1200
    )
    if r.returncode != 0:
        print("run 3 FAILED: rc=%d\nstderr: %s" % (r.returncode, r.stderr))
        digest3 = "FAILED"
    else:
        digest3 = r.stdout.strip().split("\n")[-1]
    print("run 3 done: digest=%s" % digest3)
    # Clean up helper
    try:
        os.unlink(helper_script)
    except OSError:
        pass

    # Load average after
    loadavg_after = load_avg()
    print("loadavg_after: %s" % loadavg_after)

    wall_time_s = round(wall_t1 - wall_t0, 1)

    # Determinism verdict
    deterministic = (digest1 == digest2 == digest3) and digest3 != "FAILED"

    # Latency family
    latency_family = classify_latency(overall1["p50_ms"])

    # Version info
    import transformers
    import safetensors
    versions = {
        "torch": torch.__version__,
        "laya": laya.__version__,
        "transformers": transformers.__version__,
        "safetensors": safetensors.__version__,
    }

    # Assemble output
    output = {
        "cpu_model": cpu_model,
        "nproc": nproc,
        "affinity": affinity,
        "threads": args.threads,
        "versions": versions,
        "checkpoint": args.checkpoint,
        "revision": args.revision,
        "safetensors_sha256": safetensors_sha,
        "fixture_sha256": fixture_sha,
        "fixture_count": len(questions),
        "n_per_type": args.n,
        "per_type": stats1,
        "overall": overall1,
        "mean_tokens_per_state": mean_tokens,
        "determinism": {
            "digest_run1": digest1,
            "digest_run2": digest2,
            "digest_run3_fresh_process": digest3,
            "deterministic": deterministic,
        },
        "loadavg_before": loadavg_before,
        "loadavg_after": loadavg_after,
        "wall_time_s": wall_time_s,
        "latency_family": latency_family,
        "dtype": "float32",
        "device": "cpu",
        "pin_cpus": args.pin_cpus,
    }

    with open(args.out, "w") as f:
        json.dump(output, f, indent=2)
        f.write("\n")
    print("output written: %s" % args.out)
    print("latency_family: %s" % latency_family)
    print("deterministic: %s" % deterministic)
    print("overall p50=%.2f p95=%.2f max=%.2f ms" % (overall1["p50_ms"], overall1["p95_ms"], overall1["max_ms"]))

    # Print per-type summary
    for qt, st in sorted(stats1.items()):
        print("  %s: n=%d p50=%.2f p95=%.2f max=%.2f" % (qt, st["n"], st["p50_ms"], st["p95_ms"], st["max_ms"]))


if __name__ == "__main__":
    main()
