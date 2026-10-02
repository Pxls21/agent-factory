#!/usr/bin/env python3
"""make_workload.py - the fixed chat workload of task #454's A/B (D-127, D-128), sized with the model
server's own tokenizer.

Each chat holds the shared system prompt and its own corpus files. Its first user turn is cut so the whole
first prompt (system, chat template and text) comes as close to the chat's target as the tokenizer allows
without passing it; its follow-up turns hold about --turn-tokens each. Every count is the server's own
/tokenize answer (vLLM's, chat template included), never a characters-per-token guess: the guess sent one
chat of the first window over the 131,072-token context. The worst-case last prompt (each earlier reply at
--max-reply-tokens plus a margin) must leave room for one more reply under the context limit, or the build
stops. Every arm of the A/B replays the same file byte for byte; chat_load.py gives each run its own run id
in the system prompt's first line, so no run reuses another run's prefix cache.

The API key is read from a file in process and never printed. Exit codes: 0 written; 2 a bad argument, a
target below the base prompt, a corpus too small for a target, a workload over the context limit, or a
tokenizer error.
"""
import argparse
import http.client
import json
import pathlib
import random
import sys
import time
import urllib.parse

QUESTION = ("Read the file text above. Say in five short bullet points what it does, then name one risk "
            "in it and the line it sits on.")
RUN_ID_LINE = "Run id: 00000000."  # chat_load.py swaps the eight digits per run; a digit is one token
REPLY_MARGIN = 16  # tokens per earlier reply: a reply re-tokenized in the history can differ a little


def die(msg):
    print(f"make_workload: {msg}", file=sys.stderr)
    sys.exit(2)


def corpus_files(roots, exts, min_bytes=2000):
    files = []
    for root in roots:
        r = pathlib.Path(root)
        if not r.is_dir():
            die(f"corpus root is not a directory: {root}")
        for p in sorted(r.rglob("*")):
            if p.is_file() and not p.is_symlink() and p.suffix in exts and p.stat().st_size >= min_bytes:
                files.append(p)
    if not files:
        die("the corpus holds no file")
    return files


class Tokenizer:
    """The server's /tokenize: a prompt or a chat (template applied) in, a token count out."""

    def __init__(self, url, key, model, thinking):
        self.u = urllib.parse.urlsplit(url)
        self.key, self.model, self.thinking = key, model, thinking
        self.calls = 0
        self.max_model_len = None

    def _count(self, body):
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"
        try:
            conn = http.client.HTTPConnection(self.u.hostname, self.u.port, timeout=120)
            conn.request("POST", self.u.path, body=json.dumps(dict(body, model=self.model)), headers=headers)
            resp = conn.getresponse()
            data = resp.read()
        except (OSError, http.client.HTTPException) as e:
            die(f"the tokenizer did not answer: {type(e).__name__}")
        if resp.status != 200:
            die(f"the tokenizer answered HTTP {resp.status}: {data[:200].decode(errors='replace')}")
        self.calls += 1
        r = json.loads(data)
        self.max_model_len = r.get("max_model_len", self.max_model_len)
        return r["count"]

    def text(self, s):
        return self._count({"prompt": s})

    def chat(self, messages):
        body = {"messages": messages, "add_generation_prompt": True}
        if self.thinking != "server":
            body["chat_template_kwargs"] = {"enable_thinking": self.thinking == "on"}
        return self._count(body)


def take(count, texts, names, start, target):
    """From texts[start:], joined in order, the longest prefix (cut at a character) whose count stays
    within target. Returns (text, its count, the names it holds, the index of the first text it leaves
    untouched), or None when every remaining text together stays within the target."""
    if count("") > target:
        die(f"a target of {target} tokens is below the prompt that holds no corpus text")
    joined, starts, j = "", [], start
    want = target * 5  # characters; above any measured characters-per-token, so one growth step is usual
    while True:
        while j < len(texts) and len(joined) < want:
            starts.append(len(joined) + (2 if joined else 0))
            joined = texts[j] if not joined else joined + "\n\n" + texts[j]
            j += 1
        if count(joined) > target:
            break
        if j >= len(texts):
            return None
        want = len(joined) * 2
    lo, hi = 0, len(joined)  # count(joined[:lo]) <= target < count(joined[:hi])
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if count(joined[:mid]) <= target:
            lo = mid
        else:
            hi = mid
    text = joined[:lo]
    used = [k for k, s in enumerate(starts) if s < lo]
    nxt = start + (used[-1] + 1 if used else 0)
    return text, count(text), [names[start + k] for k in used], nxt


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--tokenize-url", required=True, help="e.g. http://127.0.0.1:8080/tokenize")
    ap.add_argument("--model", required=True)
    ap.add_argument("--api-key-file", help="read in process, never printed")
    ap.add_argument("--system-file", required=True, help="the shared system prompt (e.g. .hermes.md)")
    ap.add_argument("--corpus", nargs="+", required=True, help="directories of public text")
    ap.add_argument("--exts", default=".md,.py,.sh,.yaml,.toml")
    ap.add_argument("--first-prompt-tokens", required=True,
                    help="one target per chat, in replay order, e.g. 87000,57000,77000,67000")
    ap.add_argument("--turns", type=int, default=4)
    ap.add_argument("--turn-tokens", type=int, default=2500)
    ap.add_argument("--max-reply-tokens", type=int, default=512)
    ap.add_argument("--max-file-chars", type=int, default=40000)
    ap.add_argument("--ctx-limit", type=int, help="default: the server's max_model_len")
    ap.add_argument("--thinking", choices=["on", "off", "server"], default="off")
    ap.add_argument("--seed", type=int, default=454)
    ap.add_argument("--out", required=True, help="a file that does not exist yet")
    args = ap.parse_args(argv)
    try:
        targets = [int(x) for x in args.first_prompt_tokens.split(",")]
    except ValueError:
        die("--first-prompt-tokens takes integers joined by commas")
    if not targets or min(targets) < 1 or args.turns < 1 or args.turn_tokens < 1 or args.max_reply_tokens < 1:
        die("targets, turns, turn tokens and reply tokens must be at least 1")
    out = pathlib.Path(args.out)
    if out.exists():
        die(f"--out exists: {out}")
    key = ""
    if args.api_key_file:
        key = pathlib.Path(args.api_key_file).expanduser().read_text().strip()
        if not key:
            die("the key file is empty")
    system = RUN_ID_LINE + "\n" + pathlib.Path(args.system_file).read_text(errors="replace")
    files = corpus_files(args.corpus, set(args.exts.split(",")))
    random.Random(args.seed).shuffle(files)
    tok = Tokenizer(args.tokenize_url, key, args.model, args.thinking)
    reply = "word " * args.max_reply_tokens
    while tok.text(reply) < args.max_reply_tokens + REPLY_MARGIN:
        reply += "word " * (args.max_reply_tokens // 8 + 1)
    ctx = args.ctx_limit or tok.max_model_len
    if not ctx:
        die("no --ctx-limit, and the tokenizer reported no max_model_len")
    chats = []
    for i, target in enumerate(targets):
        mine = files[i::len(targets)]
        names = [p.name for p in mine]
        texts = [f"=== file: {p.name} ===\n{p.read_text(errors='replace')[:args.max_file_chars]}" for p in mine]

        def first(t):
            return tok.chat([{"role": "system", "content": system},
                             {"role": "user", "content": t + "\n\n" + QUESTION}])

        got = take(first, texts, names, 0, target)
        if got is None:
            die(f"chat {i}: its {len(mine)} files stay within {target} tokens; the corpus is too small")
        text, first_tokens, used, nxt = got
        turns = [{"content": text + "\n\n" + QUESTION, "files": used}]
        for t in range(2, args.turns + 1):
            got = take(lambda s: tok.text(s + "\n\n" + QUESTION), texts, names, nxt, args.turn_tokens)
            if got is None:
                die(f"chat {i}: its files run out at turn {t}; the corpus is too small")
            text, _, used, nxt = got
            turns.append({"content": text + "\n\n" + QUESTION, "files": used})
        for t in turns:
            t["content_tokens"] = tok.text(t["content"])
        msgs = [{"role": "system", "content": system}, {"role": "user", "content": turns[0]["content"]}]
        for t in turns[1:]:
            msgs += [{"role": "assistant", "content": reply}, {"role": "user", "content": t["content"]}]
        worst = tok.chat(msgs)
        if worst + args.max_reply_tokens > ctx:
            die(f"chat {i}: its worst last prompt is {worst} tokens; with a {args.max_reply_tokens}-token reply "
                f"that passes the {ctx}-token context limit")
        chats.append({"idx": i, "target": target, "first_prompt_tokens": first_tokens,
                      "worst_last_prompt_tokens": worst, "turns": turns})
        print(f"make_workload: chat {i}: first prompt {first_tokens} of {target}; worst last {worst} of {ctx}; "
              f"turns {[t['content_tokens'] for t in turns]}", flush=True)
    wl = {"version": 1, "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
          "tokenizer_url": args.tokenize_url, "model": args.model, "ctx_limit": ctx, "thinking": args.thinking,
          "max_reply_tokens": args.max_reply_tokens, "turns": args.turns, "run_id_line": RUN_ID_LINE,
          "system": system, "tokenize_calls": tok.calls, "chats": chats}
    out.write_text(json.dumps(wl, indent=1) + "\n")
    print(f"make_workload: wrote {out}: {len(chats)} chats, {tok.calls} tokenizer calls", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
