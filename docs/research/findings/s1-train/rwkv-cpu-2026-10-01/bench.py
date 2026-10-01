"""CPU timing: RWKV-7 World 0.4B (the official rwkv package, plain-torch path) against Laya's encoder shape (ModernBERT,
28 layers, hidden 1024, built from its own config; compute does not depend on the weight values). Prints numbers only.
Usage: bench.py rwkv <pth without .pth> <strategy> | laya <encoder config.json>"""
import os
import resource
import sys
import time

import torch

torch.set_num_threads(int(os.environ.get("BENCH_THREADS", "4")))
TEXT = open("/home/user/agent-factory/README.md", encoding="utf-8").read() * 40   # repo prose, no secret


def rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def rwkv(path, strategy):
    os.environ["RWKV_V7_ON"] = "1"
    os.environ["RWKV_JIT_ON"] = "1"
    os.environ["RWKV_CUDA_ON"] = "0"
    from rwkv.model import RWKV
    from rwkv.utils import PIPELINE
    t0 = time.time()
    model = RWKV(model=path, strategy=strategy)
    pipe = PIPELINE(model, "rwkv_vocab_v20230424")
    print("load %.1f s, peak rss %.0f MB" % (time.time() - t0, rss_mb()))
    ids = pipe.encode(TEXT)
    print("tokens available %d" % len(ids))
    q = pipe.encode("Q: Which city is the Eiffel Tower in?\n\nA: It is in the city of")
    out, _ = model.forward(q, None)
    print("sanity: next token %r" % pipe.decode([int(torch.argmax(out))]))
    for n in (512, 2048, 8192):
        t0 = time.time()
        out, state = model.forward(ids[:n], None)
        dt = time.time() - t0
        print("read %5d tokens: %.2f s, %.0f tokens/s" % (n, dt, n / dt))
    _, state = model.forward(ids[:2048], None)
    for n in (64, 256):
        s = [x.clone() for x in state]
        t0 = time.time()
        model.forward(ids[2048:2048 + n], s)
        dt = time.time() - t0
        print("from a copied state, %3d new tokens: %.3f s" % (n, dt))
    s = [x.clone() for x in state]
    t0 = time.time()
    for t in ids[2048:2048 + 64]:
        _, s = model.forward([t], s)
    print("one token at a time, 64 tokens: %.3f s" % (time.time() - t0))
    print("state size %.2f MB, peak rss %.0f MB" % (sum(x.numel() * x.element_size() for x in state) / 2 ** 20, rss_mb()))


def laya(cfg_path):
    from transformers import AutoConfig, AutoModel
    cfg = AutoConfig.from_pretrained(os.path.dirname(cfg_path))
    cfg._attn_implementation = "sdpa"
    model = AutoModel.from_config(cfg).eval()
    print("params %.0f M" % (sum(p.numel() for p in model.parameters()) / 1e6))
    for n in (512, 2048, 8192):
        x = torch.randint(5, cfg.vocab_size - 5, (1, n))
        with torch.no_grad():
            model(input_ids=x[:, :64])
            t0 = time.time()
            model(input_ids=x)
            dt = time.time() - t0
        print("read %5d tokens: %.2f s, %.0f tokens/s" % (n, dt, n / dt))
    print("peak rss %.0f MB" % rss_mb())


if __name__ == "__main__":
    {"rwkv": lambda: rwkv(sys.argv[2], sys.argv[3]), "laya": lambda: laya(sys.argv[2])}[sys.argv[1]]()
