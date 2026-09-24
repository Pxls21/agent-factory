#!/usr/bin/env python3
"""Fine-tune Laya typed-decisions on teacher labels (task #233; brief FT1 D-1, D-7). The real run is the coordinator's GPU
window (D-078); a CPU run is for smokes.

  <laya venv>/bin/python scripts/laya_ft/train.py --dataset DIR --labels LABELS.jsonl --out DIR --mode head|full
      --device cpu|cuda [--model-dir DIR] [--epochs 1] [--batch-size 8] [--lr LR] [--seed 1234] [--limit N] [--eval-loss]

Everything is Laya's own (vendor-first, D-1): the model loads through laya.load (weights verified, strict); each example is
laya.common.build_sequence(tok, state, question, max_len, head_max_len) with the checkpoint config's lengths, as
Agent.system_one builds it; batches are laya.common.collate_items with the teacher distribution as each item's "target";
the loss is the NEGATED laya.common.proper_reward (the strictly proper scoring rule) over softmax(logits), masked by
marker_mask. --mode head freezes the encoder (requires_grad off, and Laya's own detach_encoder=True in the forward) and
trains the decision head, the type embedding and the scorer; --mode full trains the encoder too. The act head is never
trained: it is outside the loss, frozen, outside the optimizer, and its digest is compared after the run (the encoder's
too, in head mode). AdamW; a fixed seed (the data order per epoch derives from it); bf16 autocast on CUDA; a non-finite
loss stops the run. Output: checkpoint.pt (the state_dict of the trained parameters, on CPU) and train-manifest.json. The
Hugging Face cache is only read: an --out inside it is refused, and the model directory's files (size and mtime) are
compared before and after the run. The dataset must have been built for this model (its manifest's fingerprint).
Exit: 0 done; 5 a guard failed after training (a frozen part changed, or the model directory changed); 64 usage or refusal.
"""
import argparse
import hashlib
import json
import os
import random
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # scripts/: the laya_ft package
from laya_ft import common as C  # noqa: E402

TRAINED_PREFIXES = ("head.", "type_emb.", "scorer.")   # the decision head: trained in both modes
ENCODER_PREFIX, ACT_PREFIX = "encoder.", "act_head."
DEFAULT_LR = {"head": 1e-4, "full": 2e-5}


class Refusal(Exception):
    pass


def load_base(model_dir, device):
    """The base model, loaded offline through Laya's own loader."""
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    import laya
    return laya.load(str(model_dir), device=device)


def select_trainable(model, mode):
    """Set requires_grad on exactly the parameters `mode` trains. -> [(name, param)]"""
    trainable = []
    for name, p in model.named_parameters():
        if not name.startswith(TRAINED_PREFIXES + (ENCODER_PREFIX, ACT_PREFIX)):
            raise Refusal("an unknown parameter %r: the DecisionModel layout changed" % name)
        train = name.startswith(TRAINED_PREFIXES) or (mode == "full" and name.startswith(ENCODER_PREFIX))
        p.requires_grad_(train)
        if train:
            trainable.append((name, p))
    return trainable


def set_train_modes(model, mode):
    model.train()
    if mode == "head":
        model.encoder.eval()   # frozen: no dropout either way (ModernBERT's are 0.0), eval says it


def make_items(tok, cfg, examples):
    """Laya items with soft targets, the sequences exactly as Agent.system_one builds them."""
    from laya.agent import Agent
    from laya.common import QTYPES, build_sequence, render_options
    max_len, head_max_len = cfg.get("max_len", 512), cfg.get("head_max_len", 192)
    items = []
    for row, target, _rec in examples:
        q = Agent._to_internal(row["question"])
        seq, markers = build_sequence(tok, row["state"], q, max_len, head_max_len)
        if len(markers) != len(render_options(q)) or len(markers) != len(target):
            raise Refusal("row %s: %d markers for %d options" % (row["item_id"], len(markers), len(target)))
        items.append({"ids": seq, "markers": markers, "qtype": QTYPES[q["t"]], "target": list(target)})
    return items


def to_device(batch, device):
    return {k: (v.to(device) if hasattr(v, "to") else v) for k, v in batch.items()}


def forward(model, batch, mode, device):
    import torch
    with torch.autocast(device_type=device.type, dtype=torch.bfloat16, enabled=device.type == "cuda"):
        logits, _act = model(batch["input_ids"], batch["attention_mask"], batch["marker_pos"], batch["marker_mask"],
                             batch["qtype"], detach_encoder=(mode == "head"))
    return logits


def loss_fn(logits, batch):
    """The negated strictly proper reward the model was trained with, over softmax(logits), marker-masked."""
    import torch
    from laya.common import proper_reward
    q = torch.softmax(logits.float(), -1)
    return -proper_reward(q, batch["target"], batch["qtype"], batch["marker_mask"].float()).mean()


def train_step(model, opt, items, mode, device, pad_id, params, max_grad_norm):
    import torch
    from laya.common import collate_items
    b = to_device(collate_items([items], pad_id), device)
    loss = loss_fn(forward(model, b, mode, device), b)
    if not torch.isfinite(loss):
        raise FloatingPointError("non-finite loss %r: the step is refused" % float(loss))
    opt.zero_grad(set_to_none=True)
    loss.backward()
    if max_grad_norm:
        torch.nn.utils.clip_grad_norm_(params, max_grad_norm)
    opt.step()
    return float(loss.detach())


def eval_loss(model, items, mode, device, pad_id, batch_size):
    """The mean loss over `items` in eval mode (no dropout, no grad); the train modes are restored after."""
    import torch
    from laya.common import collate_items
    model.eval()
    total = 0.0
    with torch.no_grad():
        for i in range(0, len(items), batch_size):
            chunk = items[i:i + batch_size]
            b = to_device(collate_items([chunk], pad_id), device)
            total += float(loss_fn(forward(model, b, mode, device), b)) * len(chunk)
    set_train_modes(model, mode)
    return total / len(items)


def param_digest(model, prefix):
    """sha256 over the name and bytes of every parameter under `prefix` (a bitwise-unchanged check)."""
    h = hashlib.sha256()
    for name, p in model.named_parameters():
        if name.startswith(prefix):
            h.update(name.encode("utf-8"))
            h.update(p.detach().float().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def trained_state_dict(trainable):
    return {name: p.detach().cpu().clone() for name, p in trainable}


def save_checkpoint(sd, path, margin=64 << 20):
    """torch.save through a .tmp file, refused BEFORE writing when the disk cannot hold it: a full disk fails every
    process on the machine (FT1 filled the sandbox disk once, 2026-09-24, with a 1.6 GB encoder checkpoint)."""
    import torch
    path = Path(path)
    need = sum(t.numel() * t.element_size() for t in sd.values()) + margin
    free = shutil.disk_usage(path.parent).free
    if free < need:
        raise Refusal("the checkpoint needs %d MiB and %s has %d MiB free" % (need >> 20, path.parent, free >> 20))
    tmp = path.with_name(path.name + ".tmp")
    try:
        torch.save(sd, str(tmp))
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def load_checkpoint(model, path):
    """Load a checkpoint.pt into a base model: every key must name a parameter of the same shape, the act head never.
    -> (tensors, the top-level modules it replaced)"""
    import torch
    sd = torch.load(str(path), map_location="cpu", weights_only=True)
    own = dict(model.named_parameters())
    bad = [k for k in sd if k not in own or tuple(own[k].shape) != tuple(sd[k].shape) or k.startswith(ACT_PREFIX)]
    if not sd or bad:
        raise Refusal("checkpoint %s: %d tensors, %d not loadable: %s" % (path, len(sd), len(bad), bad[:3]))
    _missing, unexpected = model.load_state_dict(sd, strict=False)
    if unexpected:
        raise Refusal("checkpoint %s: unexpected keys %s" % (path, unexpected[:3]))
    return len(sd), sorted({k.split(".")[0] for k in sd})


def cache_root(model_dir):
    """The Hugging Face cache that holds a snapshot directory (HF_HOME when the snapshot sits under hub/)."""
    p = Path(model_dir).resolve()
    for parent in [p] + list(p.parents):
        if parent.name.startswith("models--"):
            root = parent.parent
            return root.parent if root.name == "hub" else root
    return p


def dir_state(model_dir):
    """(relative path, size, mtime_ns) of every file under the model directory, symlinks followed to their blobs."""
    root = Path(model_dir)
    out = []
    for p in sorted(root.rglob("*")):
        if p.is_file():
            st = p.stat()
            out.append((str(p.relative_to(root)), st.st_size, st.st_mtime_ns))
    return out


def run(args):
    t0 = time.time()
    model_dir, out = Path(args.model_dir), Path(args.out)
    root = cache_root(model_dir)
    if out.resolve() == root or root in out.resolve().parents:
        raise Refusal("--out %s is inside the Hugging Face cache %s" % (out, root))
    before = dir_state(model_dir)
    rows, dmanifest = C.load_dataset(args.dataset)
    fp = C.model_fingerprint(model_dir)
    for k in ("max_len", "head_max_len", "config_sha256", "tokenizer_sha256"):
        if dmanifest["model"].get(k) != fp[k]:
            raise Refusal("the dataset was built for another model: %s %r != %r" % (k, dmanifest["model"].get(k), fp[k]))
    labels, lstats = C.read_labels(args.labels)
    examples = C.join_labels(rows, labels)
    if args.limit is not None:
        examples = examples[:args.limit]
    if not examples:
        raise Refusal("no labeled example: %d rows, %d labels" % (len(rows), len(labels)))

    import numpy as np
    import torch
    if args.threads:
        torch.set_num_threads(args.threads)
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if args.device == "cuda" and not torch.cuda.is_available():
        raise Refusal("--device cuda but CUDA is unavailable (no silent CPU fallback)")
    agent = load_base(model_dir, args.device)
    device = agent.device
    if device.type != args.device:
        raise Refusal("the model landed on %s, not %s" % (device.type, args.device))
    model, tok = agent.model, agent.tok
    items = make_items(tok, agent.cfg, examples)
    trainable = select_trainable(model, args.mode)
    params = [p for _, p in trainable]
    if args.grad_checkpointing:
        model.encoder.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    act_before = param_digest(model, ACT_PREFIX)
    enc_before = param_digest(model, ENCODER_PREFIX) if args.mode == "head" else None
    lr = args.lr if args.lr is not None else DEFAULT_LR[args.mode]
    opt = torch.optim.AdamW(params, lr=lr, weight_decay=args.weight_decay)
    set_train_modes(model, args.mode)
    pad_id = tok.pad_token_id
    loss_before = eval_loss(model, items, args.mode, device, pad_id, args.batch_size) if args.eval_loss else None
    per_epoch, steps = [], 0
    for epoch in range(args.epochs):
        order = torch.randperm(len(items), generator=torch.Generator().manual_seed(args.seed + epoch)).tolist()
        total = 0.0
        for i in range(0, len(order), args.batch_size):
            batch = [items[j] for j in order[i:i + args.batch_size]]
            total += train_step(model, opt, batch, args.mode, device, pad_id, params, args.max_grad_norm) * len(batch)
            steps += 1
        per_epoch.append(total / len(items))
        print("epoch %d/%d loss %.6f (%d steps, %.0f s)" % (epoch + 1, args.epochs, per_epoch[-1], steps,
                                                             time.time() - t0), flush=True)
    loss_after = eval_loss(model, items, args.mode, device, pad_id, args.batch_size) if args.eval_loss else None
    guards = {"act_head_unchanged": param_digest(model, ACT_PREFIX) == act_before}
    if enc_before is not None:
        guards["encoder_unchanged"] = param_digest(model, ENCODER_PREFIX) == enc_before
    out.mkdir(parents=True, exist_ok=True)
    sd = trained_state_dict(trainable)
    save_checkpoint(sd, out / "checkpoint.pt")
    guards["model_dir_unchanged"] = dir_state(model_dir) == before
    import laya
    import transformers
    teachers = {}
    for _row, _t, rec in examples:
        k = "%s @ %s" % (rec.get("model"), rec.get("endpoint"))
        teachers[k] = teachers.get(k, 0) + 1
    manifest = {
        "dataset": {"dir": str(Path(args.dataset).resolve()), "sha256": dmanifest["dataset"]["sha256"],
                    "commit": dmanifest["commit"], "rows": len(rows)},
        "labels": {"file": str(Path(args.labels).resolve()), "sha256": C.sha256_file(args.labels),
                   **lstats, "used": len(examples), "teachers": teachers},
        "examples": {"n": len(items), "by_question": {q: sum(r["question_id"] == q for r, _t, _r in examples)
                                                       for q in C.QUESTIONS}},
        "base_model": dict(fp, model_dir=str(model_dir.resolve()),
                           safetensors_sha256=C.sha256_file(model_dir / "model.safetensors")),
        "hyperparameters": {"mode": args.mode, "device": args.device, "epochs": args.epochs,
                            "batch_size": args.batch_size, "lr": lr, "weight_decay": args.weight_decay,
                            "seed": args.seed, "max_grad_norm": args.max_grad_norm, "limit": args.limit,
                            "threads": args.threads, "grad_checkpointing": args.grad_checkpointing,
                            "optimizer": "AdamW", "amp": "bf16 autocast" if device.type == "cuda" else "none (fp32)",
                            "loss": "-laya.common.proper_reward(softmax(logits), target, qtype, marker_mask), mean",
                            "data_order": "torch.randperm per epoch, generator seed = seed + epoch"},
        "trained": {"tensors": len(sd), "parameters": int(sum(t.numel() for t in sd.values())),
                    "prefixes": sorted({k.split(".")[0] for k in sd})},
        "steps": steps, "per_epoch_loss": per_epoch, "eval_loss_before": loss_before, "eval_loss_after": loss_after,
        "guards": guards,
        "checkpoint": {"file": "checkpoint.pt", "sha256": C.sha256_file(out / "checkpoint.pt"),
                       "bytes": (out / "checkpoint.pt").stat().st_size},
        "device": str(device), "torch": torch.__version__, "laya": laya.__version__,
        "transformers": transformers.__version__, "wall_seconds": round(time.time() - t0, 1),
    }
    (out / "train-manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--labels", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--mode", required=True, choices=("head", "full"))
    ap.add_argument("--device", required=True, choices=("cpu", "cuda"))
    ap.add_argument("--model-dir", default=C.DEFAULT_MODEL_DIR)
    ap.add_argument("--epochs", type=int, default=1)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--lr", type=float, default=None, help="default %s by mode" % DEFAULT_LR)
    ap.add_argument("--weight-decay", type=float, default=0.01)
    ap.add_argument("--max-grad-norm", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--limit", type=int, default=None, help="train on the first N labeled rows (dataset order)")
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--grad-checkpointing", action="store_true", help="encoder gradient checkpointing (full mode)")
    ap.add_argument("--eval-loss", action="store_true", help="also record the eval-mode loss before and after")
    args = ap.parse_args(argv)
    if args.epochs < 1 or args.batch_size < 1 or (args.limit is not None and args.limit < 1):
        ap.error("--epochs, --batch-size and --limit must be >= 1")
    try:
        m = run(args)
    except (Refusal, C.DatasetError, C.HeldOutLeak, C.HeldOutError, C.LabelError) as e:
        print("train: refused: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 64
    print(json.dumps({k: m[k] for k in ("examples", "steps", "per_epoch_loss", "eval_loss_before", "eval_loss_after",
                                        "guards", "trained", "checkpoint", "device", "wall_seconds")}, sort_keys=True))
    if not all(m["guards"].values()):
        print("train: GUARD FAILED: %s" % m["guards"], file=sys.stderr)
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
