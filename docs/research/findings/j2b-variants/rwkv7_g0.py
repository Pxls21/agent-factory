#!/usr/bin/env python3
"""RWKV-7 G0: the pinned RWKV-7 0.4B checkpoint, zero-shot, on the PC's GPU inside a GPU window (task #242, D-081).

Runs ON the PC with the vLLM `qwen` service stopped (scripts/gpu_window.sh starts it as a job). Three phases, each
recorded to <out-dir>/g0.json even when a later one fails:
  env     library versions, the GPU, the load time and the parameter count
  ladder  one forward over real repo text at 2k to 60k tokens (seconds, peak MiB), and the per-decision cost of a
          question answered from a COPY of the 16k and 60k states (the RNN reuse the long-input plan relies on), with a
          check that prefix-then-suffix gives the same next-token logits as one whole forward
  j2      the committed J2 probes UNCHANGED (ap_choice, v1_choice_rich, v1_blocking, v1, v1_full, ap_noul), loaded as
          openjev_j2.py loads them, with only the request path swapped for a local scorer: simple-jev's own
          PromptCompiler (policy baseline) builds the prompts and simple-jev's build_answers reads the answers
J4 (the long-input test) is NOT run: it is not built yet.

The RWKV adapter, a declared deviation from simple-jev's stock prompt (measured 2026-09-24 18:2xZ-18:5xZ, AF-AP-195):
simple-jev's numeric answer prefill `{"answer": ` ends with a space that the RWKV World tokenizer merges with the digit,
so its boundary check refuses `noul` and `score`; here that prefill loses its trailing space and the labels become
' 1'..' 9' (' 0'.. for score). simple-jev's HFBackend is NOT used: fla's RWKV7 takes `logits_to_keep` as an int and
slices the last N positions, while HFBackend passes a tensor of positions for its branch batches, which would read the
wrong position without an error. The scorer here forwards the shared prefix once and each branch's suffix from a deep
copy of that state, unpadded, and reads the last position.

  rwkv7_g0.py [--out-dir DIR] [--only env,ladder,j2] [--variants a,b,...] [--no-cache] [--plumbing]
--no-cache scores each branch with one whole forward (no shared-prefix state) and skips the state-reuse rows: on the
PC, transformers 4.57 (~/venv-rwkv) cannot build fla 0.3.0's cache ("You should provide exactly one of `layers` or
`layer_class_to_replicate`"), measured 2026-09-24 19:1xZ; ~/venv-rwkv-b (transformers below 4.54) is the cached path.
--plumbing replaces the MODEL with uniform logits so the harness can be exercised on a CPU before the window; its
output is marked plumbing and is never a measurement.
"""
import argparse
import copy
import dataclasses
import importlib.util
import json
import os
import sys
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SNAPSHOT = Path(os.path.expanduser(
    "~/.cache/huggingface/hub/models--RWKV--RWKV7-Goose-World2.9-0.4B-HF/snapshots/"
    "e94655a9fad2c8da9f25aba575d8f0fdedc05931"))                    # upstream.lock.yaml advisory_models pin
SIMPLE_JEV = Path(os.environ.get("SIMPLE_JEV", os.path.expanduser("~/simple-jev")))
LADDER = (2048, 4096, 8192, 16384, 32768, 61440)
VARIANTS = ("ap_choice", "v1_choice_rich", "v1_blocking", "v1", "v1_full", "ap_noul")


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def rwkv_adapter(hf_prompt_policies, tok):
    """The two adapter changes, applied where simple-jev looks them up: compile -> prepare_policy -> prepare_prompt
    (module global of hf_prompt_policies), and the tokenizer's chat template fed plain strings."""
    orig_prepare, orig_apply = hf_prompt_policies.prepare_prompt, tok.apply_chat_template

    def prepare(*a, **k):
        plan = orig_prepare(*a, **k)
        name = next(f.name for f in dataclasses.fields(plan)
                    if isinstance(getattr(plan, f.name), (tuple, list)) and getattr(plan, f.name)
                    and hasattr(getattr(plan, f.name)[0], "answer_prefix"))
        qs = [dataclasses.replace(q, answer_prefix=q.answer_prefix.rstrip(" "),
                                  output_labels=tuple(" " + x for x in q.output_labels))
              if q.answer_prefix.endswith(" ") else q for q in getattr(plan, name)]
        return dataclasses.replace(plan, **{name: type(getattr(plan, name))(qs)})

    def apply(messages, *a, **k):
        flat = [dict(m, content="".join(b.get("text", "") for b in m["content"]))
                if isinstance(m.get("content"), list) else m for m in messages]
        return orig_apply(flat, *a, **k)

    hf_prompt_policies.prepare_prompt = prepare
    tok.apply_chat_template = apply


class Scorer:
    """Next-token logits over each branch's output labels: the shared prefix once, each suffix from a copy of its
    state. model=None is the plumbing stand-in (uniform logits)."""

    def __init__(self, model, device, use_cache=True):
        self.model, self.device, self.use_cache, self.forwards, self.tokens = model, device, use_cache, 0, 0

    def forward(self, ids, cache=None):
        import torch
        out = self.model(input_ids=torch.tensor([ids], device=self.device), past_key_values=cache,
                         use_cache=self.use_cache, logits_to_keep=1)
        self.forwards += 1
        self.tokens += len(ids)
        return out.logits[0, -1], out.past_key_values

    def score(self, compiled):
        import torch
        seqs = [b.token_ids for b in compiled.branches]
        if self.model is None:
            return {b.branch_id: torch.zeros(len(b.output_ids)) for b in compiled.branches}
        n = min(map(len, seqs)) - 1 if self.use_cache else 0      # no cache: every branch is one whole forward
        prefix = seqs[0][:n]
        for s in seqs[1:]:
            k = 0
            while k < len(prefix) and s[k] == prefix[k]:
                k += 1
            prefix = prefix[:k]
        with torch.inference_mode():
            cache = self.forward(prefix)[1] if prefix else None
            out = {}
            for b in compiled.branches:
                logits, _ = self.forward(b.token_ids[len(prefix):], copy.deepcopy(cache))
                out[b.branch_id] = logits[list(b.output_ids)].float().cpu()
        return out


def phase_env(rec, args):
    import torch
    import transformers
    info = {"torch": torch.__version__, "transformers": transformers.__version__, "python": sys.version.split()[0],
            "snapshot": str(SNAPSHOT), "cuda": torch.cuda.is_available()}
    for mod in ("triton", "fla"):
        try:
            info[mod] = __import__(mod).__version__
        except Exception as e:                               # a missing library is a finding, not a crash
            info[mod] = "absent: %s" % type(e).__name__
    if info["cuda"]:
        free, total = torch.cuda.mem_get_info()
        info.update(gpu=torch.cuda.get_device_name(0), free_mib=free >> 20, total_mib=total >> 20)
    rec["env"] = info


def load(rec, args):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(SNAPSHOT, trust_remote_code=True, local_files_only=True)
    if args.plumbing:
        rec["load"] = {"plumbing": True}
        return tok, Scorer(None, "cpu")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(SNAPSHOT, trust_remote_code=True, local_files_only=True,
                                                 torch_dtype=torch.bfloat16).to("cuda").eval()
    torch.cuda.synchronize()
    rec["load"] = {"seconds": round(time.time() - t0, 2), "dtype": "bfloat16", "class": type(model).__name__,
                   "parameters": sum(p.numel() for p in model.parameters()),
                   "allocated_mib": torch.cuda.memory_allocated() >> 20}
    return tok, Scorer(model, "cuda", use_cache=not args.no_cache)


def real_text_ids(tok, n):
    """Real repo prose (docs/*.md, sorted), tokenized, first n tokens."""
    ids = []
    for p in sorted((REPO / "docs").glob("*.md")):
        ids += tok.encode(p.read_text(encoding="utf-8", errors="replace"), add_special_tokens=False)
        if len(ids) >= n:
            return ids[:n]
    raise RuntimeError("docs/*.md hold only %d tokens, fewer than %d" % (len(ids), n))


def phase_ladder(rec, tok, scorer):
    import torch
    rows, reuse = [], {}
    question = tok.encode("\n\nUser: Which component does this document describe first?\n\nAssistant:",
                          add_special_tokens=False)
    for n in LADDER:
        ids = real_text_ids(tok, n)
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()
        t0 = time.time()
        with torch.inference_mode():
            logits, cache = scorer.forward(ids)
        torch.cuda.synchronize()
        row = {"tokens": n, "seconds": round(time.time() - t0, 3), "peak_mib": torch.cuda.max_memory_allocated() >> 20,
               "finite": bool(torch.isfinite(logits).all())}
        if n in (16384, 61440) and scorer.use_cache:
            times = []
            with torch.inference_mode():
                for _ in range(5):
                    torch.cuda.synchronize()
                    t1 = time.time()
                    scorer.forward(question, copy.deepcopy(cache))
                    torch.cuda.synchronize()
                    times.append(time.time() - t1)
            reuse[str(n)] = {"question_tokens": len(question), "seconds_median": round(sorted(times)[2], 4),
                             "seconds_all": [round(t, 4) for t in times]}
        rows.append(row)
        rec["ladder"] = {"rows": rows, "state_reuse": reuse}
        del cache
    if not scorer.use_cache:
        rec["ladder"]["state_reuse"] = "NOT run: --no-cache"
        return
    ids = real_text_ids(tok, 2048)                            # the reuse path must equal one whole forward
    with torch.inference_mode():
        whole, _ = scorer.forward(ids + question)
        _, c = scorer.forward(ids)
        split, _ = scorer.forward(question, c)
    diff = (whole.float() - split.float()).abs()
    rec["ladder"]["reuse_check"] = {"max_abs_logit_diff": float(diff.max()), "same_argmax":
                                    int(whole.argmax()) == int(split.argmax())}


def phase_j2(rec, args, tok, scorer):
    sys.path[:0] = [str(SIMPLE_JEV), str(SIMPLE_JEV / "hf-server")]
    import hf_prompt_policies  # noqa: E402  (simple-jev)
    import hf_server  # noqa: E402
    from common import build_answers  # noqa: E402
    rwkv_adapter(hf_prompt_policies, tok)
    compiler = hf_server.PromptCompiler(tok, max_tokens=65536, prompt_policy="baseline")
    oj = _load("openjev_j2", HERE / "openjev_j2.py")          # its post (the per-chunk split) and the probe loaders
    usage = {"requests": 0, "input_tokens": 0}

    def local_one(env, state, questions):
        compiled = compiler.compile({"model": "rwkv7", "state": state, "questions": questions})
        answers = build_answers(compiled.plan, scorer.score(compiled))
        return {"answers": answers, "usage": {"input_tokens": sum(len(b.token_ids) for b in compiled.branches)}}

    oj._one = local_one
    post = oj.make_post({}, usage)
    apm = _load("ap_probe", HERE.parent / "ap-hawk-probe" / "ap_probe.py")
    v1m = _load("v1_probe", HERE.parent / "j2-v1-probe" / "v1_probe.py")
    j2b = _load("j2b", HERE / "j2b.py")
    for mod in (apm, v1m, j2b):
        mod.post = post
    out_dir = Path(args.out_dir)
    runs = rec.setdefault("j2", {})
    for name in args.variants.split(","):
        t0, before, f0 = time.time(), dict(usage), scorer.forwards
        try:
            if name == "ap_noul":
                apm.cmd_score(argparse.Namespace(sample=str(HERE.parent / "ap-hawk-probe" / "sample.json"),
                                                 url="rwkv7", out=str(out_dir / "ap_noul.json")))
            elif name in ("v1", "v1_full"):
                sample = HERE.parent / ("j2-v1-probe" if name == "v1" else "j2c-fulltext") / "sample.json"
                v1m.cmd_score(argparse.Namespace(sample=str(sample), url="rwkv7", out=str(out_dir / f"{name}.json")))
            else:
                res = j2b.VARIANTS[name]("rwkv7")
                (out_dir / f"{name}.json").write_text(json.dumps(res, indent=1, sort_keys=True) + "\n", encoding="utf-8")
            runs[name] = {"ok": True}
        except Exception as e:
            runs[name] = {"ok": False, "error": "%s: %s" % (type(e).__name__, str(e)[:300])}
        runs[name].update(seconds=round(time.time() - t0, 1), requests=usage["requests"] - before["requests"],
                          forwards=scorer.forwards - f0)
        write(rec, args)


def write(rec, args):
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    (Path(args.out_dir) / "g0.json").write_text(json.dumps(rec, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default=str(HERE / "rwkv7-g0"))
    ap.add_argument("--only", default="env,ladder,j2")
    ap.add_argument("--variants", default=",".join(VARIANTS))
    ap.add_argument("--plumbing", action="store_true", help="uniform logits instead of the model; never a measurement")
    ap.add_argument("--no-cache", action="store_true", help="one whole forward per branch; no state reuse")
    args = ap.parse_args(argv)
    phases = args.only.split(",")
    if not set(phases) <= {"env", "ladder", "j2"} or not set(args.variants.split(",")) <= set(VARIANTS):
        ap.error("--only takes env,ladder,j2 and --variants takes %s" % ",".join(VARIANTS))
    if args.plumbing and "ladder" in phases:
        ap.error("--plumbing has no model, so it cannot run the ladder")
    rec = {"g0": "rwkv7-world2.9-0.4b zero-shot", "plumbing": args.plumbing, "no_cache": args.no_cache,
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "j4": "NOT run: J4 is not built"}
    rc = 0
    try:
        if "env" in phases:
            phase_env(rec, args)
        tok, scorer = load(rec, args)
        write(rec, args)
        if "ladder" in phases:
            phase_ladder(rec, tok, scorer)
            write(rec, args)
        if "j2" in phases:
            phase_j2(rec, args, tok, scorer)
    except Exception:
        rec["error"] = traceback.format_exc()[-2000:]
        rc = 1
    rec["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if any(not r.get("ok") for r in rec.get("j2", {}).values()):
        rc = 1
    write(rec, args)
    print(json.dumps({k: rec.get(k) for k in ("load", "ladder", "j2", "error")}, sort_keys=True)[:4000])
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
