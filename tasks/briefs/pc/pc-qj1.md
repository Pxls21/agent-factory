# PC lane QJ1 (task #241, D-079): the Qwen 27B Jev adapter, v1-exact through OmniRoute, and the J2 test on it

PIN: dda7ffb (the post-push origin head; it carries D-079 and the `upstream.lock.yaml` pins).

Role: code-implementer. Route: the LOCAL build route (`agentfactory-build-local`, medium; D-061: local Hermes only). Claim nothing about
which model you are; the harvest measures the provider mix. Venue: `tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey ultra, Lever-2:
the report is DATA (files:lines, verbatim counts, discrepancies, NOT-done). Keep your context small: `| tail -n 40` on long output,
`sed -n` ranges instead of whole-file reads. Do NOT spawn subagents. Code questions go to graft first (CODE INTEL FIRST).

AUTHORIZATION AND LIMITS: first-party tooling work in the owner's repository on the owner's PC, approved by the owner (D-079: "can't you
use something like this", pointing at simple-jev). Network: ONLY OmniRoute on loopback (`http://127.0.0.1:20128`) with the model id
`qwen-local/qwen3.8-27b-local`; nothing else (no pip, no git fetch, no Hugging Face). No server touch: never start, stop or restart
OmniRoute, the vLLM `qwen` container or the Laya unit. No outward-facing action (no push, no PR, no comment). Never read `~/.hermes/`.
Write only inside your lane tree (the boundary below) and your lane's `../scratch/` directory.

## WHY (read first)

simple-jev (featherless-ai, Apache-2.0, pinned in `upstream.lock.yaml` under `advisory_jev_runtimes`) turns any open causal LM into a
Jev: it answers typed questions (choice, score, noul) from the next-token logits over the answer labels, with no text generation. Its
v1 rules are a language-independent spec (`~/simple-jev/common/PROMPT_STRUCTURE_V1.md`) plus plain Python (`~/simple-jev/common/`), and
its own server (`~/simple-jev/hf-server/hf_server.py`) loads the model with Transformers. That server cannot run here: the 3090 is full
with the vLLM container that already serves Qwen3.8-27B behind OmniRoute. D-079 makes that model the local TEACHER for Laya and the RWKV
student, and a working-Jev candidate. This lane builds the thin adapter that applies simple-jev's rules to the running model and proves
its answers are v1-exact, then runs the J2 test on it (the same samples and scorers Laya, Haiku and OpenJev ran).

## BOUNDARY

- CREATE `scripts/qwen_jev.py`: a stdlib HTTP server (`GET /health`, `GET /v1/models`, `POST /v1/systemone` and `POST /v1/classifier`,
  the same handler) on `127.0.0.1:<port>` (default 47420; check it is free), and the library behind it.
- CREATE `tests/test_qwen_jev.py` (deterministic, LLM-free; a local stand-in HTTP upstream is a test double for the NETWORK only).
- CREATE `docs/research/findings/j2b-variants/qwen27b_j2.py` (the J2 runner, the pattern of `openjev_j2.py` beside it) and the results
  directory `docs/research/findings/j2b-variants/qwen27b/`.
- CREATE the report `tasks/briefs/jev-laya/QJ1-report.md`.
- READ: `~/simple-jev` (the pinned checkout), `scripts/laya_systemone_server.py` (the house wire contract: per-chunk fan-out),
  `scripts/jev.py`, the J2 scripts (`docs/research/findings/j2-v1-probe/v1_probe.py`, `docs/research/findings/ap-hawk-probe/ap_probe.py`,
  `docs/research/findings/j2b-variants/j2b.py`, `docs/research/findings/j2b-variants/openjev_j2.py`), `docs/08_DECISION_LOG.md` (D-079),
  `upstream.lock.yaml`.

## PINNED DECISIONS (a conflict with the tree is a STOP-and-report)

- **D-1 simple-jev is the oracle, used, never copied.** Import `common` and `hf_prompt_policies` from `~/simple-jev` (add it and its
  `hf-server/` to `sys.path`) with `~/venv-qwenjev/bin/python`. At start, refuse to serve unless `git -C ~/simple-jev rev-parse HEAD`
  equals `advisory_jev_runtimes.simple-jev.revision` in `upstream.lock.yaml`. Use simple-jev's `hf_server.PromptCompiler` with the
  served model's tokenizer (`~/qwen-jev-tokenizer`, copied from the container's `/app/models/Qwen3.8-27B-W4A16-AutoRound`) to compile
  every request, and simple-jev's own scoring (`common.build_response` and, for binary noul, `hf_prompt_policies.restore_binary_noul`)
  to build every answer from the label logprobs. Never re-implement the prompt text or the scoring.
- **D-2 The policy.** Default `examples_binary` (simple-jev's own selection for this backbone: its `resolve_prompt_policy` on the served
  config answers "Qwen dense 27B -> examples_binary"); `baseline` behind a flag, for comparison only.
- **D-3 One path, and it is OmniRoute.** Each compiled branch goes to OmniRoute `/v1/chat/completions` with the model id
  `qwen-local/qwen3.8-27b-local` (never a combo: the build combo falls back to the cloud chain), the branch's messages plus the assistant
  prefill as the final assistant message, `continue_final_message: true`, `add_generation_prompt: false`,
  `chat_template_kwargs: {"enable_thinking": <as the compiler used it>}`, the branch's `reasoning_content` when it has one,
  `max_tokens: 1`, `temperature: 0`, `logprobs: true`, `top_logprobs: 20`. The response's `model` must name the local model, or the
  answer is refused. Whether this path reproduces the compiler's rendering is the lane's first question (D-4); if no path through
  OmniRoute does, STOP and report: a direct vLLM call needs the owner's word.
- **D-4 Parity is checked, never assumed.** For every branch, the request's `usage.prompt_tokens` must equal the compiler's
  `len(branch.token_ids)`, and every label must map to its token: the label logprob is read from `top_logprobs` by the label's decoded
  token string. A branch that fails the token count is refused (not scored). A label absent from the top 20 is BOUNDED (given the lowest
  logprob shown, an upper bound) and named in the answer (`"bounded_labels": [...]`); never silently filled.
- **D-5 The house wire contract.** Accept every request shape the J2 scripts and `scripts/jev.py` send today, unchanged: a request
  without `model` gets the served id; when every question id names a `state.chunks` id, each question sees only its own chunk (the
  Laya server's fan-out, `scripts/laya_systemone_server.py`). The response carries `answers` keyed by question id, `usage`, and `model`.
- **D-6 The key.** The OmniRoute inference key is read in process from `~/.config/qwen-jev/omniroute.key` (0600, written by the
  coordinator; `QWEN_JEV_KEY_FILE` overrides the path for tests). Never in argv, a log, an error line or a response; a test proves it
  with a FAKE key file.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below (the pin, the venv, the tokenizer digests, the oracle's two policies, the OmniRoute probes);
   stop and report on any mismatch.
2. Parity: at least 20 real branches (10 from `docs/research/findings/j2c-fulltext/sample.json`, 10 from
   `docs/research/findings/ap-hawk-probe/sample.json`; both policies' shapes): a table of compiler token count, OmniRoute
   `usage.prompt_tokens`, labels found in the top 20, bounded labels, the top token. All equal, or STOP (D-3).
3. Tests, run twice with `PATH="$HOME/venv-qwenjev/bin:$PATH" bash scripts/test_summary.sh tests/test_qwen_jev.py --basetemp <lane
   scratch>/bt` (the venv that holds simple-jev's dependencies and pytest; make the basetemp parent first):
   the wire contract (D-5, the fan-out and a request with no `model`); scoring equal to simple-jev's `build_response` on fixed label
   logprobs; a count mismatch refused; a bounded label named; a cloud-served `model` refused; a non-pinned simple-jev checkout refused;
   the FAKE key never in argv, the log, an error or a response.
4. J2 on the adapter (`examples_binary`): `v1_full`, `v1`, `v1_choice_rich`, `v1_blocking`, `ap_choice`, `ap_noul`, each through the
   committed scripts unchanged (only the URL differs), results in `docs/research/findings/j2b-variants/qwen27b/`, with requests, prompt
   tokens, wall time and bounded-label counts per variant. Then `v1_full` once more with `baseline`, if its branches pass parity; if they
   do not (the noul prefill ends with a space, and OmniRoute refused a whitespace-only token at 16:1xZ), say so with the evidence.
5. Mutants on scratch copies only, each red on a named test: drop the parity check; score with your own softmax instead of simple-jev's;
   fill a missing label silently; accept a combo or cloud `model`; skip the pin check.
6. Gates: pyflakes on every new file; `python3 scripts/no_laya_in_gates.py`; the separator check
   (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`) on every file you write.
7. The report: files and lines, the parity table, pasted counts, the J2 table beside the committed baselines (majority, heuristic,
   Laya, Haiku, OpenJev from `docs/research/findings/J2-SIGNAL-PROBE-2026-09-24.md` and `j2b-variants/openjev/`), the mutant table,
   deviations, NOT-done.

## PREMISE — MEASURED at authoring (2026-09-24 16:3xZ, the PC, and the sandbox clone at dda7ffb)

```
$ git -C ~/simple-jev rev-parse HEAD; git -C ~/simple-jev log -1 --format=%cI
5686b217dd0330b81b3325a64c8ace319017f8a2
2026-09-24T11:16:21Z
$ ~/venv-qwenjev/bin/python -c "import sys,pydantic,numpy,transformers,tokenizers,fastapi,jinja2; print(sys.version.split()[0], pydantic.VERSION, numpy.__version__, transformers.__version__, tokenizers.__version__, fastapi.__version__, jinja2.__version__)"
3.13.11 2.13.5 2.5.3 5.17.0 0.23.2 0.141.1 3.1.6
$ PATH="$HOME/venv-qwenjev/bin:$PATH" python3 -c "import sys, pytest; print(sys.executable, pytest.__version__)"
/home/rocco/venv-qwenjev/bin/python3 9.1.1
(stderr, filtered out above: transformers warns "PyTorch was not found"; tokenizers only, as intended)
$ podman exec qwen ... (the vLLM process command line)
/app/venv/bin/python3.12 /app/venv/bin/vllm serve /app/models/Qwen3.8-27B-W4A16-AutoRound --served-model-name qwen3.8-27b ... --max-model-len 131072 ...
$ sha256sum ~/qwen-jev-tokenizer/*   (copied out of that folder with podman cp; first 16 hex)
c3cf9e34abf4f9e3  chat_template.jinja
eddb28f7ebde5456  config.json
1a450b75a54bf9e6  generation_config.json
d89ef49ce9cd37fb  processor_config.json
5f7aa0d810000c4a  tokenizer_config.json
06b9509352d2af50  tokenizer.json
$ ~/venv-qwenjev/bin/python <the oracle probe: PromptCompiler(tok, prompt_policy=...).compile(the Mia request)>
AUTO PROMPT FORMAT: Qwen dense 27B -> examples_binary
baseline 0 prompt tokens 420 labels ['A', 'B'] prefill '{"answer": "' reasoning None tail '\n<|im_start|>assistant\n<think>\n\n</think>\n\n{"answer": "'
baseline 1 prompt tokens 428 labels ['1', '2', '3', '4', '5', '6', '7', '8', '9'] prefill '{"answer": ' reasoning None tail '\n<|im_start|>assistant\n<think>\n\n</think>\n\n{"answer": '
examples_binary 0 prompt tokens 1092 labels ['A', 'B'] prefill '{"answer": "' reasoning '[thinking]\n[thinking]\n[thinking]\n' tail ']\n[thinking]\n</think>\n\n{"answer": "'
examples_binary 1 prompt tokens 1036 labels ['A', 'B'] prefill '{"answer": "' reasoning None tail '\n<|im_start|>assistant\n<think>\n\n</think>\n\n{"answer": "'
$ (OmniRoute, the repo's key reader, 16:0xZ) plain chat, max_tokens 1, logprobs true, top_logprobs 20, per model id
qwen-local/qwen3.8-27b-local 0.44s served qwen3.8-27b-local content '1' logprobs key present: True top: [('1', -0.06), ('9', -3.81), ('0', -4.81), ('2', -4.81), ('3', -5.31), ('4', -5.56), ('8', -5.81), ('The', -6.31)]
agentfactory-build-local 0.22s served qwen3.8-27b-local content '1' logprobs key present: True top: [('1', -0.06), ('9', -3.81), ('0', -4.81), ('2', -4.81), ('3', -5.31), ('4', -5.56), ('8', -5.81), ('The', -6.31)]
$ (OmniRoute, 16:1xZ) chat with continue_final_message and the assistant prefill '{"answer": ' (enable_thinking false)
chat-prefill-space HTTP 502 {'error': {'message': '[openai-compatible-chat-98fcb302-795d-4db5-baee-2754a5723a39/qwen3.8-27b-local] upstream returned an empty response without usable output', 'type': 'upstream_response_error', 'code': 'upstream_empty_response'}}
$ (OmniRoute, 16:1xZ) /v1/completions with a raw prompt and integer logprobs 20
completions HTTP 400 {'error': {'message': '[400]: 1 validation error:', 'type': 'Bad Request', 'code': 400}, 'upstream_details': {'error': {'message': '1 validation error:', 'type': 'Bad Request', 'param': 'body.logprobs', 'code': 400}}}
$ stat -c "%a %s" ~/.config/qwen-jev/omniroute.key
600 36
```

The 502 shape has a whitespace-only next token; the `examples_binary` branches end in `{"answer": "` and their labels are letters,
so the question for item 2 is open, not answered: whether OmniRoute carries `continue_final_message`, `add_generation_prompt`,
`chat_template_kwargs` and `reasoning_content` to vLLM so that the token counts match.
