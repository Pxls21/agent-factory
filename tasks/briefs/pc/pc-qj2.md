# PC lane QJ2 (task #241; D-079, D-082): the Qwen 27B Jev adapter on the DIRECT vLLM path, exact by construction, and the J2 test on it

PIN: d6a2142 (the origin head at authoring). The lane tree is the PIN plus QJ1's harvested files, shipped as LANE_PATCH
`tasks/briefs/pc/patch-pc-qj1.md--dda7ffb.diff` (sha256 37f3abc5b07239d4..., three new files; unverified work of a lane
that ended FAILED).

Role: code-implementer. Route: the LOCAL build route (`agentfactory-build-local`, medium; D-061/D-062: local only). Claim
nothing about which model you are; the harvest measures the provider mix. Venue: `tasks/briefs/pc/VENUE-MAP.md`, read it
FIRST. Honey ultra, Lever-2: the report is DATA (files:lines, verbatim counts, discrepancies, NOT-done). Keep your context
small: `| tail -n 40` on long output, `sed -n` ranges instead of whole-file reads. Do NOT spawn subagents. Code questions go
to graft first (CODE INTEL FIRST).

AUTHORIZATION AND LIMITS: first-party tooling work in the owner's repository on the owner's PC, approved by the owner
(D-079; D-082, 2026-09-25: "wire it straight to [vLLM]", "direct connection to system 1"). Network: ONLY the vLLM server
on loopback, `http://127.0.0.1:8080`, for the adapter's scoring. The adapter does NOT use OmniRoute (D-082). Nothing else:
no pip, no git fetch, no Hugging Face. No server touch: never start, stop or restart vLLM, OmniRoute or the Laya unit.
**Never send `echo`, `prompt_logprobs`, `best_of` or `n` to the vLLM server: `prompt_logprobs` makes it compute output for
every PROMPT token outside its reserved memory, and one such request OOM-killed its engine on 2026-09-24 and took the
owner's qwen down for five minutes for everyone (AF-AP-201). Every scoring request carries exactly the key set in D-3.**
No outward-facing action (no push, no PR, no comment). Never read `~/.hermes/`. Write only inside your lane tree and your
lane's `../scratch/` directory.

## WHY (read first)

QJ1 (`tasks/briefs/pc/pc-qj1.md`) built a thin adapter that applies simple-jev's v1 rules to the running Qwen3.8-27B, sent
it through OmniRoute, and died before finishing. The coordinator then measured the transport
(`docs/research/findings/j2b-variants/qwen27b/TRANSPORT-2026-09-24.md`, at the PIN): OmniRoute drops the final assistant
turn's `reasoning_content`, so every `examples_binary` choice branch reached the model 12 tokens short (QJ1 blamed a
tokenizers version; that is not the cause). Straight to vLLM the same request keeps the field, and a raw completion whose
prompt is the compiler's own `token_ids` matches the compiler BY CONSTRUCTION, with the same label logprobs (the premise
block). The owner ruled (D-082): System 1 connects straight to its model server; OmniRoute stays for System 2; for
training, whichever path gives the best output. Qwen is meant to be the local TEACHER for Laya and the RWKV student. The
first teacher, OpenJev, is under the lexical baseline on the anti-pattern rows, and the Laya checkpoint trained on its
labels was rejected on every KC-J3 line (`docs/research/findings/laya-ft-eval/`). So this J2 run decides whether Qwen is
a better teacher.

## BOUNDARY

- MODIFY (they arrive from the LANE_PATCH): `scripts/qwen_jev.py`, `tests/test_qwen_jev.py`,
  `docs/research/findings/j2b-variants/qwen27b_j2.py`.
- CREATE: `tests/fixtures/qwen_jev/completion-choice.json` and `tests/fixtures/qwen_jev/completion-noul.json`, REAL
  `/v1/completions` responses you capture (the tests' fake is built from them); the results directories
  `docs/research/findings/j2b-variants/qwen27b/j2-examples_binary/` and `.../j2-baseline/`; the report
  `tasks/briefs/jev-laya/QJ2-report.md` (write it incrementally from the start).
- READ: `~/simple-jev` (the pinned checkout), `scripts/laya_systemone_server.py` (the house wire contract: per-chunk
  fan-out), `scripts/jev.py`, the J2 scripts (`docs/research/findings/j2-v1-probe/v1_probe.py`,
  `docs/research/findings/ap-hawk-probe/ap_probe.py`, `docs/research/findings/j2b-variants/j2b.py`,
  `docs/research/findings/j2b-variants/openjev_j2.py`), `docs/research/findings/j2b-variants/qwen27b/TRANSPORT-2026-09-24.md`
  and `transport_probe.py`, `upstream.lock.yaml`, `tasks/briefs/pc/pc-qj1.md` (its D-1, D-5 and D-6 still hold, except
  where this brief changes them).

## PINNED DECISIONS (a conflict with the tree is a STOP-and-report)

- **D-1 simple-jev is the oracle, used, never copied** (QJ1's D-1): import `common` and `hf_prompt_policies` from
  `~/simple-jev` with `~/venv-qwenjev/bin/python`; refuse to serve unless `git -C ~/simple-jev rev-parse HEAD` equals
  `advisory_jev_runtimes.simple-jev.revision` in `upstream.lock.yaml`; compile with `hf_server.PromptCompiler` and the
  served tokenizer (`~/qwen-jev-tokenizer`); build every answer with simple-jev's `common.build_response` (and, for
  binary noul, `hf_prompt_policies.restore_binary_noul`). Never re-implement the prompt text or the scoring.
- **D-2 The policies.** `examples_binary` (simple-jev's own choice for this backbone) is the primary. `baseline` runs the
  same J2 as the comparison the owner asked for ("you can try it out"). Both through the same transport.
- **D-3 The transport (D-082).** Each compiled branch goes to `POST http://127.0.0.1:8080/v1/completions` with EXACTLY the
  body keys `model`, `prompt`, `max_tokens`, `temperature`, `logprobs`: `model` = the served id read from
  `GET /v1/models` at start (the premise shows `qwen3.8-27b-local`), `prompt` = the branch's `token_ids` (the list of
  ints the compiler produced), `max_tokens: 1`, `temperature: 0`, `logprobs: 20`. The response's `model` must equal the
  id sent, or the answer is refused. Chat is not a scoring path; it is item 2's cross-check only.
- **D-4 Parity is checked, never assumed.** `usage.prompt_tokens` must equal `len(token_ids)`; a mismatch is refused (not
  scored). Each label's logprob is read from `choices[0].logprobs.top_logprobs[0]` (a dict, token string to logprob) by
  the label's decoded token (`tokenizer.decode([output_id])`). A label absent from the 20 is BOUNDED (the lowest logprob
  shown, an upper bound) and named in the answer (`"bounded_labels"`); never silently filled.
- **D-5 The house wire contract** (QJ1's D-5, unchanged).
- **D-6 The key.** The vLLM key is read in process from `~/.config/qwen-builder/api-key` (0600, directory 0700;
  `QWEN_JEV_KEY_FILE` overrides the path for tests). Never in argv, a log, an error line or a response; a test proves it
  with a FAKE key file.
- **D-7 The port is yours only if you bound it.** The adapter refuses to start when its port is taken (a clear error,
  non-zero exit) and never treats a listener it did not start as itself: QJ1's adapter squatted 47420 for five hours
  after its lane died (AF-AP-33), and a J2 run pointed at it would have scored the OLD transport. The adapter's `/health`
  reports the lane's revision and the J2 runner checks it before the first request. Stop your adapter by its pid before
  you report.

## THE THREE DEFECTS IN QJ1'S FILES (fix each; a test reds on the old code)

1. `_branch_logits` passes `logprobs.content` (the chat shape: one entry per GENERATED token) to the label reader as the
   candidate list; on a real response only the generated token would be found. With D-3 the candidates are
   `choices[0].logprobs.top_logprobs[0]`.
2. The served-model check compares the response's `model` with `qwen-local/qwen3.8-27b-local` (an OmniRoute id); vLLM
   answers with its own served id.
3. `fake_ok_response` builds the test double from the code's own assumption (AF-AP-42): it put the 20 candidates straight
   into `logprobs.content`. Rebuild the fake from the captured real responses (the fixture files), so a shape change reds.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report on any mismatch.
2. Parity: at least 20 real branches (10 from `docs/research/findings/j2c-fulltext/sample.json`, 10 from
   `docs/research/findings/ap-hawk-probe/sample.json`), under BOTH policies: a table of the compiler's token count,
   `usage.prompt_tokens`, labels found in the top 20, bounded labels and the top token. Every count equal, or STOP.
   Cross-check: 5 of those branches also through `/v1/chat/completions` directly (QJ1's chat body, the reasoning as the
   `reasoning_content` field): the same `prompt_tokens`, and label logprobs within 0.01 of the completion's.
3. Tests, run twice: `PATH="$HOME/venv-qwenjev/bin:$PATH" bash scripts/test_summary.sh tests/test_qwen_jev.py --basetemp
   <lane scratch>/bt` (make the basetemp parent first). They cover:
   - the wire contract (D-5: the fan-out, a request with no `model`);
   - scoring equal to simple-jev's `build_response` on fixed label logprobs;
   - a count mismatch refused, and a bounded label named;
   - a served model other than the id sent refused;
   - a simple-jev checkout at another revision refused;
   - the FAKE key never in argv, the log, an error or a response;
   - the request body's key set exactly D-3's, so a body carrying `echo`, `prompt_logprobs`, `best_of` or `n` cannot be
     built;
   - the port-taken refusal (D-7).
4. J2 on the adapter, `examples_binary` then `baseline`: `v1_full`, `v1`, `v1_choice_rich`, `v1_blocking`, `ap_choice`,
   `ap_noul`, each through the committed scripts unchanged (only the URL differs). Results go in the policy's directory,
   with requests, prompt tokens, wall time and refused and bounded counts per variant. Run each policy's J2 as a
   background job with its own log (`nohup ... &`, pid recorded), and poll it with short calls: the terminal tool caps
   one call at 420 s.
5. Mutants on scratch copies only, each red on a named test:
   - drop the count check;
   - score with your own softmax instead of simple-jev's;
   - fill a missing label silently;
   - accept another served model;
   - skip the pin check;
   - add `"echo": true` to the body;
   - read `logprobs.content` again (defect 1).
6. Gates: pyflakes on every file you write; `python3 scripts/no_laya_in_gates.py`; the separator check
   (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`) on every file you write.
7. The report:
   - files and lines, the parity table, and pasted counts;
   - the J2 table for both policies, beside the committed baselines: majority, heuristic, lexical; the Laya base and the
     head checkpoint (`docs/research/findings/laya-ft-eval/`); OpenJev (`docs/research/findings/j2b-variants/openjev/`);
     Haiku (`docs/research/findings/j2b-variants/haiku_*.json`);
   - the mutant table, deviations, NOT-done.

## PREMISE — MEASURED at authoring (2026-09-25 00:1xZ-00:2xZ; the PC, whose clone has fetched origin 67195a9b1e6b; the sandbox at d6a2142)

```
$ git -C ~/simple-jev rev-parse HEAD
5686b217dd0330b81b3325a64c8ace319017f8a2
$ ~/venv-qwenjev/bin/python -c "import sys,pydantic,numpy,transformers,tokenizers,fastapi,jinja2; print(...)"
3.13.11 2.13.5 2.5.3 5.17.0 0.23.2 0.141.1 3.1.6
$ sha256sum ~/qwen-jev-tokenizer/* | cut -c1-16
c3cf9e34abf4f9e3  chat_template.jinja
eddb28f7ebde5456  config.json
1a450b75a54bf9e6  generation_config.json
d89ef49ce9cd37fb  processor_config.json
5f7aa0d810000c4a  tokenizer_config.json
06b9509352d2af50  tokenizer.json
$ stat -c "%a %s" ~/.config/qwen-builder/api-key; stat -c %a ~/.config/qwen-builder
600 65
700
$ ss -ltn | grep -c ":47420 "      (first reading: QJ1's orphaned adapter held the port)
1
$ ss -ltnp | grep ":47420 "; ps -o pid,ppid,etime,cmd -p 1615333; readlink /proc/1615333/cwd
LISTEN 0 5 127.0.0.1:47420 0.0.0.0:* users:(("python",pid=1615333,fd=3))
1615333       1    04:59:51 /home/rocco/venv-qwenjev/bin/python scripts/qwen_jev.py --port 47420 --policy examples_binary
/home/rocco/agent-factory/.lanes/pc-qj1.md--dda7ffb/tree
$ kill -TERM 1615333; ss -ltn | grep -c ":47420 "      (the coordinator stopped it; the port is free)
0
$ (every process whose cwd is under ~/agent-factory/.lanes/)
(none)
$ for f in ~/agent-factory/.lanes/*/lane.pid: alive?
dead s0-01-b5i-tee-one-sentence-joined-by-equ-58741bb2.failed-503-1
$ sha256sum tasks/briefs/pc/patch-pc-qj1.md--dda7ffb.diff | cut -c1-16
37f3abc5b07239d4
$ git worktree add --detach <tmp> d6a2142 && git -C <tmp> apply --check --verbose <that patch>
Checking patch docs/research/findings/j2b-variants/qwen27b_j2.py...
Checking patch scripts/qwen_jev.py...
Checking patch tests/test_qwen_jev.py...
apply_check_rc=0
$ ~/venv-qwenjev/bin/python direct_probe.py   (the coordinator's probe, 00:20:36Z: one choice and one noul question,
  examples_binary, straight to 127.0.0.1:8080; the body keys of the token-id request are exactly D-3's)
models HTTP 200: ['qwen3.8-27b-local', 'qwen3.8-27b']
choice: compiler 1106 tokens; reasoning True; labels ['A', 'B']
  chat: served 'qwen3.8-27b-local'; prompt_tokens 1106 (delta +0); labels {'A': -0.0011, 'B': -6.8761}
  token ids: served 'qwen3.8-27b-local'; prompt_tokens 1106 (delta +0); 20 top logprobs (mass 1.0000); labels {'A': -0.0011, 'B': -6.8761}; generated 'A'
noul: compiler 1037 tokens; reasoning False; labels ['A', 'B']
  chat: served 'qwen3.8-27b-local'; prompt_tokens 1037 (delta +0); labels {'A': -6.877, 'B': -0.002}
  token ids: served 'qwen3.8-27b-local'; prompt_tokens 1037 (delta +0); 20 top logprobs (mass 1.0000); labels {'A': -6.877, 'B': -0.002}; generated 'B'
```

Not measured here, so questions for you, never facts: whether every J2 branch fits the server's context (the longest
`ap_noul` prompts), and whether any label falls outside the top 20 on real samples (the probe's two questions had all
the mass in the 20).
