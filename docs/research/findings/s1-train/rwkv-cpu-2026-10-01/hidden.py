"""Does llama.cpp on the CPU give the same RWKV-7 hidden states as the official rwkv package? The heads read the final
hidden state (after ln_out, before the head), so that is what is compared, at every position of one text.
Reference: the rwkv package, fp32, plain torch (JIT off), with its head replaced by an identity matrix.
Usage: hidden.py <pth without .pth> <gguf> [<gguf> ...]   (prints numbers only; the text is repo prose)"""
import json
import os
import subprocess
import sys

os.environ["RWKV_V7_ON"] = "1"
os.environ["RWKV_JIT_ON"] = "0"
os.environ["RWKV_CUDA_ON"] = "0"
import torch  # noqa: E402

torch.set_num_threads(4)
SP = os.path.dirname(os.path.abspath(__file__))
EMBD = SP + "/lcpp/llama_cpp_python-0.3.36/vendor/llama.cpp/build/bin/llama-embedding"
TEXT = " ".join(open("/home/user/agent-factory/README.md", encoding="utf-8").read().split()) * 4


def reference(path, ids):
    from rwkv.model import RWKV
    model = RWKV(model=path, strategy="cpu fp32")
    # The v7 class is always a ScriptModule (model.py:185), so model.z reads back a copy: set the whole dict again
    # with an identity head, and the forward returns the hidden state (after ln_out, before the head).
    z = model.z
    z["head.weight"] = torch.eye(model.args.n_embd)
    model.z = z
    out, _ = model.forward(ids, None, full_output=True)
    if out.shape[-1] != model.args.n_embd:
        sys.exit("the identity head did not take: output width %d" % out.shape[-1])
    return out.float()


def llamacpp(gguf, text_file, n):
    # -np 2: with -np 1 the tool reserves outputs for every parallel sequence it supports (256) and asserts
    # against a smaller batch; two sequences and a batch of 2(n+16) hold every position of one text.
    m = str(2 * (n + 16))
    r = subprocess.run([EMBD, "-m", gguf, "-f", text_file, "--embd-separator", "<#nosep#>", "--pooling", "none",
                        "--embd-normalize", "-1", "--embd-output-format", "json", "-t", "4", "-np", "2", "-c", m,
                        "-b", m, "-ub", m], capture_output=True, text=True, timeout=600)
    if r.returncode:
        sys.exit("llama-embedding rc %d: %s" % (r.returncode, r.stderr[-400:]))
    out = r.stdout[r.stdout.index("{"):]
    data = json.loads(out)["data"]
    return torch.tensor([d["embedding"] for d in data]).float()


def main():
    from rwkv.utils import PIPELINE
    pth, ggufs = sys.argv[1], sys.argv[2:]
    tok = PIPELINE(None, "rwkv_vocab_v20230424")
    for n in (64, 512):
        ids = tok.encode(TEXT)[:n]
        text = tok.decode(ids)
        if tok.encode(text) != ids:
            sys.exit("the text does not round-trip through the tokenizer at n=%d" % n)
        tf = "%s/hidden-text-%d.txt" % (SP, n)
        open(tf, "w", encoding="utf-8").write(text)
        ref = reference(pth, ids)
        for g in ggufs:
            got = llamacpp(g, tf, n)
            if got.shape != ref.shape:
                print("n=%d %s: shape %s against %s" % (n, os.path.basename(g), tuple(got.shape), tuple(ref.shape)))
                continue
            cos = torch.nn.functional.cosine_similarity(got, ref, dim=1)
            rel = (got - ref).norm(dim=1) / ref.norm(dim=1)
            print("n=%4d %-28s cosine min %.5f mean %.5f last %.5f | relative error mean %.2e max %.2e" % (
                n, os.path.basename(g), cos.min(), cos.mean(), cos[-1], rel.mean(), rel.max()), flush=True)


if __name__ == "__main__":
    main()
