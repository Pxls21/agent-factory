#!/usr/bin/env python3
"""Which transport of a compiled examples_binary CHOICE branch reproduces the pinned simple-jev compiler's tokens through
OmniRoute? (task #241, the QJ1 continuation; coordinator probe 2026-09-24.)

Runs ON the PC with ~/venv-qwenjev/bin/python: simple-jev at its upstream.lock.yaml pin, the served model's tokenizer copy
(~/qwen-jev-tokenizer), and OmniRoute on loopback with the model id qwen-local/qwen3.8-27b-local (the key is read in
process from ~/.config/qwen-jev/omniroute.key and never printed). One question, one branch, max_tokens 1 per request.
Local: the oracle's own template call renders each variant, and its tokens are diffed against the compiler's branch.
Wire: each variant goes to /v1/chat/completions with continue_final_message, and usage.prompt_tokens is compared.
"""
import difflib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

SJ = os.path.expanduser("~/simple-jev")
PIN = "5686b217dd0330b81b3325a64c8ace319017f8a2"   # upstream.lock.yaml advisory_jev_runtimes.simple-jev.revision
SERVED = "qwen-local/qwen3.8-27b-local"


def main():
    head = subprocess.run(["git", "-C", SJ, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if head != PIN:
        print("simple-jev is not at the pin")
        return 2
    sys.path[:0] = [SJ, os.path.join(SJ, "hf-server")]
    from transformers import AutoTokenizer
    from common import ClassifierRequest
    from hf_prompt_policies import prepare_policy
    from hf_server import PromptCompiler
    tok = AutoTokenizer.from_pretrained(os.path.expanduser("~/qwen-jev-tokenizer"))
    with open(os.path.expanduser("~/.config/qwen-jev/omniroute.key"), encoding="utf-8") as f:
        key = f.read().strip()
    creq = ClassifierRequest.model_validate({
        "model": SERVED, "state": {"incident": "The ball on the table is red and round."},
        "questions": {"color": {"type": "choice", "instructions": "What color is the ball?",
                                "criteria": {"red": "The ball is red.", "blue": "The ball is blue."}}}})
    prepare_policy(creq, "v1", "examples_binary")
    br = PromptCompiler(tok, prompt_policy="examples_binary").compile(creq).branches[0]
    rc, prefix, want = br.reasoning_content, br.answer_prefix, list(br.token_ids)
    base = [{**m, "content": [{"type": "text", "text": m["content"]}]} for m in br.messages]
    think = "<think>\n" + rc.strip("\n") + "\n</think>\n\n"
    text_block = [{"type": "text", "text": prefix}]
    variants = {
        "A reasoning_content field (QJ1's transport)": {"role": "assistant", "content": text_block, "reasoning_content": rc},
        "B think block in the content, text list": {"role": "assistant", "content": [{"type": "text", "text": think + prefix}]},
        "C think block in the content, string": {"role": "assistant", "content": think + prefix},
        "D reasoning field": {"role": "assistant", "content": text_block, "reasoning": rc},
        "E reasoning and reasoning_content fields": {"role": "assistant", "content": text_block, "reasoning": rc,
                                                     "reasoning_content": rc},
    }
    labels = [tok.decode([i]) for i in br.output_ids]
    print("compiler: %d tokens; reasoning %r; labels %s" % (len(want), rc, labels))
    for name, last in variants.items():
        text = tok.apply_chat_template(base + [last], tokenize=False, add_generation_prompt=False,
                                       continue_final_message=True, enable_thinking=True)
        ids = tok.encode(text, add_special_tokens=False)
        diff = []
        if ids != want:
            a, b = tok.convert_ids_to_tokens(want), tok.convert_ids_to_tokens(ids)
            diff = [(op, a[i1:i2], b[j1:j2]) for op, i1, i2, j1, j2
                    in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes() if op != "equal"]
        body = {"model": SERVED, "messages": base + [last], "continue_final_message": True, "add_generation_prompt": False,
                "chat_template_kwargs": {"enable_thinking": True}, "max_tokens": 1, "temperature": 0,
                "logprobs": True, "top_logprobs": 20}
        req = urllib.request.Request("http://127.0.0.1:20128/v1/chat/completions", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
        try:
            with urllib.request.urlopen(req, timeout=100) as r:
                resp = json.loads(r.read())
            pt = resp.get("usage", {}).get("prompt_tokens")
            first = ((resp["choices"][0].get("logprobs") or {}).get("content") or [{}])[0]
            tops = first.get("top_logprobs") or []
            wire = "served %r; prompt_tokens %s (delta %+d); logprobs.content[0] keys %s, %d top_logprobs; labels in them %s" % (
                resp.get("model"), pt, pt - len(want), sorted(first), len(tops),
                [lab for lab in labels if any(t.get("token") == lab for t in tops)])
        except urllib.error.HTTPError as e:
            wire = "HTTP %s %s" % (e.code, e.read()[:160].decode("utf-8", "replace"))
        print("%s\n  local render: %d tokens (delta %+d)%s\n  wire: %s" % (
            name, len(ids), len(ids) - len(want), ("; diff %s" % diff) if diff else "; equal to the compiler", wire))
    return 0


if __name__ == "__main__":
    sys.exit(main())
