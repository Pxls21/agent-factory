# The Qwen Jev adapter's transport through OmniRoute (task #241, the QJ1 continuation): measured 2026-09-24 23:4xZ

QJ1 (the PC lane that built the adapter, ended FAILED) found that every `examples_binary` CHOICE branch reached the model
12 tokens short of the pinned simple-jev compiler's count, and put it down to a tokenizers version difference between the
serving container and the oracle venv. The coordinator re-measured it with `transport_probe.py` (beside this file; run on
the PC with `~/venv-qwenjev/bin/python`, simple-jev at 5686b217, one choice question, one branch). The 12 tokens are the
reasoning block the compiler puts in the final assistant turn, and the version explanation does not hold on this path.

## The run (pasted, 23:44:09Z)

```
compiler: 1106 tokens; reasoning '[thinking]\n[thinking]\n[thinking]\n'; labels ['A', 'B']
A reasoning_content field (QJ1's transport)
  local render: 1106 tokens (delta +0); equal to the compiler
  wire: served 'qwen3.8-27b-local'; prompt_tokens 1094 (delta -12); logprobs.content[0] keys ['bytes', 'logprob', 'token', 'top_logprobs'], 20 top_logprobs; labels in them ['A', 'B']
B think block in the content, text list
  local render: 1110 tokens (delta +4); diff [('insert', [], ['ĊĊ', '</think>', 'ĊĊ', '<think>'])]
  wire: served 'qwen3.8-27b-local'; prompt_tokens 1110 (delta +4); logprobs.content[0] keys ['bytes', 'logprob', 'token', 'top_logprobs'], 20 top_logprobs; labels in them ['A', 'B']
C think block in the content, string
  local render: 1110 tokens (delta +4); diff [('insert', [], ['ĊĊ', '</think>', 'ĊĊ', '<think>'])]
  wire: served 'qwen3.8-27b-local'; prompt_tokens 1110 (delta +4); logprobs.content[0] keys ['bytes', 'logprob', 'token', 'top_logprobs'], 20 top_logprobs; labels in them ['A', 'B']
D reasoning field
  local render: 1094 tokens (delta -12); diff [('replace', ['Ċ', '[', 'thinking', ']', 'Ċ', '[', 'thinking', ']', 'Ċ', '[', 'thinking', ']', 'Ċ'], ['ĊĊ'])]
  wire: served 'qwen3.8-27b-local'; prompt_tokens 1094 (delta -12); logprobs.content[0] keys ['bytes', 'logprob', 'token', 'top_logprobs'], 20 top_logprobs; labels in them ['A', 'B']
E reasoning and reasoning_content fields
  local render: 1106 tokens (delta +0); equal to the compiler
  wire: served 'qwen3.8-27b-local'; prompt_tokens 1094 (delta -12); logprobs.content[0] keys ['bytes', 'logprob', 'token', 'top_logprobs'], 20 top_logprobs; labels in them ['A', 'B']
23:44:09Z
```

## What it shows

1. The compiler's branch carries the fixed reasoning `[thinking]` x3 in a `reasoning_content` field on the final assistant
   message. The local template renders that transport (A) token for token like the compiler (1,106). On the wire the model
   sees 1,094: exactly the 12 tokens of the reasoning block (`[thinking]` x3 with their newlines, measured alone with the
   served tokenizer: 12). A `reasoning` field (D), or both fields (E), arrive the same way: the field does not reach the
   template on the server.
2. With the reasoning inside the message text (B as a text list, C as a string), the local render and the wire AGREE at
   1,110 tokens: the template adds an empty think block first (`\n\n`, `</think>`, `\n\n`, `<think>`). Since the server
   renders these variants exactly as the local template does, the template and tokenizer match; only the field is lost
   (OmniRoute's message normalization or vLLM's input parsing; not located, see below).
3. The response names the model `qwen3.8-27b-local`, not the request's `qwen-local/qwen3.8-27b-local`: a check that compares
   the response's `model` with the request id refuses every answer.
4. The 20 candidates sit in `logprobs.content[0].top_logprobs`; `logprobs.content` has one entry per generated token (one
   here). QJ1's harvested `_branch_logits` (`tasks/briefs/pc/patch-pc-qj1.md--dda7ffb.diff`) passes `logprobs.content` itself
   to its label reader, so on a real response every label but the generated token would be "bounded"; its tests passed
   because its fake response put the 20 candidates straight into `logprobs.content`.

## Not measured, and why

- ~~Where the field is dropped (OmniRoute or vLLM) is not located~~: LOCATED 2026-09-25, see the next section. OmniRoute
  drops it; vLLM keeps it.
- Whether a token-count match also means the same token ids: the server's prompt ids are not in the chat response. vLLM's
  `prompt_logprobs` would return them, but it must never be sent to the shared server: at 23:45:08Z one such request
  OOM-killed the vLLM engine and systemd restarted `qwen.service` (AF-AP-201, `docs/INCIDENT-LOG.md`).

## The direct path (D-082: System 1 connects straight to its model server), measured 2026-09-25 00:20Z

`direct_probe.py` (beside this file) sends the same compiled branches straight to the vLLM server on `127.0.0.1:8080`, two
ways: chat with the `reasoning_content` field (QJ1's transport), and a raw completion whose prompt is the compiler's own
`token_ids` (exact by construction; the check is that the server counts the same number). Every option was priced first
(AF-AP-201): one generated token, its 20 top logprobs; no echo, no `prompt_logprobs`, no `best_of`.

```
models HTTP 200: ['qwen3.8-27b-local', 'qwen3.8-27b']
choice: compiler 1106 tokens; reasoning True; labels ['A', 'B']
  chat: served 'qwen3.8-27b-local'; prompt_tokens 1106 (delta +0); labels {'A': -0.0011, 'B': -6.8761}
  token ids: served 'qwen3.8-27b-local'; prompt_tokens 1106 (delta +0); 20 top logprobs (mass 1.0000); labels {'A': -0.0011, 'B': -6.8761}; generated 'A'
noul: compiler 1037 tokens; reasoning False; labels ['A', 'B']
  chat: served 'qwen3.8-27b-local'; prompt_tokens 1037 (delta +0); labels {'A': -6.877, 'B': -0.002}
  token ids: served 'qwen3.8-27b-local'; prompt_tokens 1037 (delta +0); 20 top logprobs (mass 1.0000); labels {'A': -6.877, 'B': -0.002}; generated 'B'
00:20:36Z
```

Read: straight to vLLM, the chat transport keeps the reasoning field (1,106 = the compiler; 1,094 through OmniRoute), so
OmniRoute is what drops it. The token-id transport matches by construction, and both give the same label logprobs to four
decimals. The 20 returned candidates carry all of the probability mass (1.0000), so neither label had to be bounded here.
