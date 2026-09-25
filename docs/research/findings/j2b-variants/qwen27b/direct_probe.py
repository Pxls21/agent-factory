#!/usr/bin/env python3
"""The direct vLLM path for the Qwen Jev adapter (D-082, task #241): does it reproduce the pinned simple-jev compiler's
tokens, and on which transport? Runs ON the PC with ~/venv-qwenjev/bin/python against the vLLM `qwen` server on
127.0.0.1:8080 (its key read in process from ~/.config/qwen-builder/api-key, never printed).

Priced before sending (AF-AP-201): max_tokens 1, temperature 0 and 20 top logprobs of the ONE generated token (the same
work as the chat top_logprobs OmniRoute already carried); a prompt given as token ids skips tokenization. Never sent: echo,
prompt_logprobs, best_of, n > 1 (they make the server compute output per PROMPT token, outside its reserved memory).

Transports, per branch of one choice and one yes/no question (examples_binary, simple-jev's policy for this backbone):
  chat         /v1/chat/completions, the final assistant message with the `reasoning_content` field (QJ1's transport)
  token ids    /v1/completions with the compiler's own `token_ids` as the prompt: the prompt is the compiler's by
               construction; the check is that usage.prompt_tokens equals their count
"""
import json
import math
import os
import subprocess
import sys
import urllib.error
import urllib.request

SJ = os.path.expanduser("~/simple-jev")
PIN = "5686b217dd0330b81b3325a64c8ace319017f8a2"   # upstream.lock.yaml advisory_jev_runtimes.simple-jev.revision
BASE = "http://127.0.0.1:8080"


def call(path, key, body=None):
    req = urllib.request.Request(BASE + path, data=None if body is None else json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=100) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read()[:200].decode("utf-8", "replace")}


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
    with open(os.path.expanduser("~/.config/qwen-builder/api-key"), encoding="utf-8") as f:
        key = f.read().strip()
    st, models = call("/v1/models", key)
    served = [m.get("id") for m in models.get("data", [])] if st == 200 else []
    print("models HTTP %s: %s" % (st, served))
    if not served:
        return 3
    model = served[0]
    state = {"incident": "The ball on the table is red and round."}
    cases = {"choice": {"color": {"type": "choice", "instructions": "What color is the ball?",
                                  "criteria": {"red": "The ball is red.", "blue": "The ball is blue."}}},
             "noul": {"is_red": {"type": "noul", "instructions": "Is the ball red?"}}}
    for kind, questions in cases.items():
        creq = ClassifierRequest.model_validate({"model": model, "state": state, "questions": questions})
        prepare_policy(creq, "v1", "examples_binary")
        br = PromptCompiler(tok, prompt_policy="examples_binary").compile(creq).branches[0]
        want, rc = list(br.token_ids), br.reasoning_content
        labels = [tok.decode([i]) for i in br.output_ids]
        print("%s: compiler %d tokens; reasoning %s; labels %s" % (kind, len(want), rc is not None, labels))
        last = {"role": "assistant", "content": [{"type": "text", "text": br.answer_prefix}]}
        if rc is not None:
            last["reasoning_content"] = rc
        msgs = [{**m, "content": [{"type": "text", "text": m["content"]}]} for m in br.messages] + [last]
        st, r = call("/v1/chat/completions", key, {
            "model": model, "messages": msgs, "continue_final_message": True, "add_generation_prompt": False,
            "chat_template_kwargs": {"enable_thinking": rc is not None}, "max_tokens": 1, "temperature": 0,
            "logprobs": True, "top_logprobs": 20})
        if st == 200:
            tops = ((r["choices"][0].get("logprobs") or {}).get("content") or [{}])[0].get("top_logprobs") or []
            got = {t["token"]: t["logprob"] for t in tops}
            pt = r["usage"]["prompt_tokens"]
            print("  chat: served %r; prompt_tokens %d (delta %+d); labels %s" % (
                r.get("model"), pt, pt - len(want), {lab: round(got[lab], 4) for lab in labels if lab in got}))
        else:
            print("  chat: HTTP %s %s" % (st, r))
        st, r = call("/v1/completions", key, {"model": model, "prompt": want, "max_tokens": 1, "temperature": 0,
                                              "logprobs": 20})
        if st == 200:
            lp = r["choices"][0].get("logprobs") or {}
            tops = (lp.get("top_logprobs") or [{}])[0] or {}
            pt = r["usage"]["prompt_tokens"]
            found = {lab: round(tops[lab], 4) for lab in labels if lab in tops}
            mass = sum(math.exp(v) for v in tops.values())
            print("  token ids: served %r; prompt_tokens %d (delta %+d); %d top logprobs (mass %.4f); labels %s; generated %r" % (
                r.get("model"), pt, pt - len(want), len(tops), mass, found, (lp.get("tokens") or [None])[0]))
        else:
            print("  token ids: HTTP %s %s" % (st, r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
