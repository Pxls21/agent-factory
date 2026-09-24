"""Time Laya typed-decisions TRAINING steps on this CPU (no data leaves the machine; synthetic targets; nothing saved)."""
import glob
import json
import os
import sys
import time

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
THREADS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
os.environ["OMP_NUM_THREADS"] = str(THREADS)
import torch  # noqa: E402

torch.set_num_threads(THREADS)
import laya  # noqa: E402
from laya.common import QTYPES, build_sequence, collate_items  # noqa: E402

snap = glob.glob("/home/rocco/hf-laya/**/snapshots/1c5edc17a7acd8701df6fc341c0d179f1c62c982", recursive=True)[0]
t0 = time.time()
agent = laya.load(snap, device="cpu", subfolder="typed-decisions")
res = {"threads": THREADS, "load_s": round(time.time() - t0, 1), "torch": torch.__version__,
       "params_total": sum(p.numel() for p in agent.model.parameters()),
       "params_encoder": sum(p.numel() for p in agent.model.encoder.parameters())}
model, tok = agent.model, agent.tok
head = agent.cfg.get("head_max_len", 192)
filler = open("/home/rocco/agent-factory/docs/INCIDENT-LOG.md", encoding="utf-8").read()
q = {"t": "choice", "ins": "Which class did the verifier give this finding?",
     "crit": {c: "d" for c in ("A", "B", "C", "D", "E", "F")}}


def batch(B, L):
    items = []
    for i in range(B):
        seq, markers = build_sequence(tok, filler[i * 5000:i * 5000 + L * 8], q, L, head)
        items.append({"ids": seq, "markers": markers, "qtype": QTYPES["choice"], "target": [1.0] + [0.0] * 5})
    return collate_items([items], tok.pad_token_id)


def step(b, opt, detach):
    logits, _act = model(b["input_ids"], b["attention_mask"], b["marker_pos"], b["marker_mask"], b["qtype"],
                         detach_encoder=detach)
    loss = -(b["target"] * torch.log_softmax(logits, -1)).sum(-1).mean()
    opt.zero_grad()
    loss.backward()
    opt.step()


model.train()
for L in (256, 512):
    b = batch(8, L)
    b["qtype"] = torch.as_tensor(b["qtype"])
    with torch.no_grad():
        t = time.time()
        model.encoder(input_ids=b["input_ids"], attention_mask=b["attention_mask"])
        res[f"encoder_forward_b8_L{L}_s"] = round(time.time() - t, 2)
    for mode in ("head_only", "full"):
        if mode == "head_only":
            params = [p for n, p in model.named_parameters() if not n.startswith("encoder.")]
        else:
            params = list(model.parameters())
        opt = torch.optim.AdamW(params, lr=1e-5)
        step(b, opt, mode == "head_only")  # warm-up
        times = []
        for _ in range(3):
            t = time.time()
            step(b, opt, mode == "head_only")
            times.append(round(time.time() - t, 2))
        res[f"{mode}_step_b8_L{L}_s"] = times
        del opt
    print(json.dumps(res), flush=True)
print("DONE", json.dumps(res), flush=True)
