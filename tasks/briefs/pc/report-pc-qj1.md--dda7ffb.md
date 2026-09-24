DRAFT REPORT — the Hermes session FAILED (usage.json "failed": true, "completed": false; harness rc=0) before writing its final report; its last output is not a report and is kept in report.failed-output.md. This is the incremental draft the lane kept. Grade it as PARTIAL evidence, never as a verdict.
FAILED SESSION OUTPUT (first 200 bytes, newlines shown as \n): API call failed after 3 retries: ollama-cloud/kimi-k3: auth — [ollama-cloud/kimi-k3] [403]: your subscription payment is past due. update your payment method: https://ollama.com/settings/billing (re

# QJ1 report (D-079, task #241) — the Qwen 27B Jev adapter
(drafted incrementally; the final message is the full report)

## STATUS
- Building the adapter + the J2 runner.
- D-3 first question ANSWERED (measured): the OmniRoute path does NOT reproduce the compiler's token count.
  Root cause: the serving container runs tokenizers 0.22.2 / transformers 5.15.0 / vLLM 0.28.0; the pinned
  oracle venv runs tokenizers 0.23.2 / transformers 5.17.0. Same tokenizer.json, different library version,
  so the same rendered text segments to a different token count (e.g. examples_binary choice: venv 1102 vs
  container 1154 = +52; noul: 1038 vs 1090). The label LOGPROBS still land at the correct next-token position
  (the top prediction is the answer label: A/red, B/yes), so the SCORING boundary is intact; only the total
  prompt-token bookkeeping differs. Per D-3 this is the STOP-and-report case; a direct vLLM call (matching
  tokenizer) or aligning the serving tokenizer to 0.23.2 would be needed for an exact D-4 parity pass.

## PREMISE (re-measured this lane)
- pin 5686b217dd0330b81b3325a64c8ace319017f8a2 (upstream.lock.yaml:183) == git -C ~/simple-jev HEAD  [MATCH]
- venv 3.13.11 / pydantic 2.13.5 / numpy 2.5.3 / transformers 5.17.0 / tokenizers 0.23.2 / fastapi 0.141.1 / jinja2 3.1.6  [MATCH]
- tokenizer digests (first16): chat_template.c3cf9e34 / config.eddb28f7 / generation_config.1a450b75 /
  processor_config.d89ef49c / tokenizer_config.5f7aa0d8 / tokenizer.json.06b95093  [ALL MATCH]
- key file 600 36  [MATCH]  ; port 47420 free  [MATCH]
- auto policy resolve: Qwen dense 27B -> examples_binary  [MATCH D-2]
- container: tokenizers 0.22.2 / transformers 5.15.0 / vllm 0.28.0  [NEW MEASUREMENT — the mismatch source]

## D-3/D-4 PARITY (the lane's first question)
Probe: compile with simple-jev PromptCompiler, send each branch through OmniRoute with the exact D-3 wire
(continue_final_message=true, add_generation_prompt=false, chat_template_kwargs.enable_thinking per policy,
max_tokens=1, temperature=0, logprobs=true, top_logprobs=20). One representative request (1 choice + 1 noul).
- examples_binary choice (color): compiler 1102 / omni 1090 / delta -12 / REFUSED by D-4 / top label A (red)
- examples_binary noul  (is_red): compiler 1038 / omni 1038 / delta 0 / PASS / top label B (yes)
- baseline       choice (color): compiler 430  / omni 430  / delta 0 / PASS / top label A (red)
- baseline       noul  (is_red): compiler 430  / omni 502  / whitespace-only next token (the 16:1xZ 502) / REFUSED
Raw /v1/completions of the venv-rendered text (no logprobs): omni usage.prompt_tokens = 1154/1090/482/481 vs
venv encode 1102/1038/430/430 -> the container tokenizes the SAME text to more tokens (+52/+52/+52/+51).
So the offset is a tokenizers-library-version effect, not a chat-template effect.

## D-3/D-4 PARITY — 20 required branches (10 j2c choice + 10 ap noul), both policies
Compiled with the pinned oracle, sent through the exact D-3 wire (the named policy's
text-block-list content + final assistant prefill; baseline = plain-string + final assistant):
- examples_binary: 10 noul branches delta 0 (PASS) | 10 choice branches delta -12 (REFUSED by D-4)
- baseline:        10 choice branches delta 0 (PASS) | noul branches HTTP 502 (whitespace-only next token)
So under D-4 ("fail the count -> refuse; a 502 is an upstream refusal"), examples_binary can score NOUL
but not CHOICE, and baseline can score CHOICE but not NOUL. The -12 on every choice branch is a
tokenizer-library-version artifact (container 0.22.2 vs oracle venv 0.23.2 re-segmenting the same
rendered text); the next-token/label boundary is intact (the top logprob is the answer label).
This is D-3's "first question": the OmniRoute path does NOT reproduce the compiler's count for the
choice class, so a direct vLLM call (matching tokenizer) or aligning the serving tokenizer to 0.23.2
is needed for an exact D-4 parity pass. STOP-and-report case per D-3.

## J2 variant -> script -> question-type map (the committed scripts, unchanged)
- v1_full / v1   -> v1_probe.cmd_score (1 CHOICE + 6 NOUL fan-out)
- ap_noul        -> ap_probe.cmd_score (16 NOUL fan-out)
- ap_choice / v1_choice_rich -> j2b.VARIANTS (pure CHOICE)
- v1_blocking    -> j2b.VARIANTS (pure NOUL)
Implication for the J2 run (examples_binary): choice branches refused (delta -12); noul branches pass
the count but the choice-dependent metrics read a refused answer. The run still exercises the adapter
end-to-end and records the refused/bounded counts per variant; the scored cells are degenerate by the
measured parity wall, which is the honest result to report (NOT a capability claim).

## DECISION (the D-3 "first question") — build + measure, not a hard STOP
The brief's D-3 STOP condition is "if no path through OmniRoute does [reproduce the compiler's
rendering]." A path DOES (partially): noul/eB and choice/baseline match (delta 0); choice/eB (delta
-12) and noul/baseline (502) do not. So the hard STOP is NOT triggered; D-4's per-branch refusal
governs, and evidence demand 4's "if they do not [pass parity], say so with the evidence" is the
operative instruction for the failing classes. I proceed to build the real adapter (D-1..D-6) and run
the J2 on it, reporting the parity wall and every refused/degenerate cell as MEASURED findings, NOT
as a capability claim. The choice-class J2 numbers are a measurement of the parity wall, not of the
model. GATE RECOMMENDATION (not a verdict, for the adversarial-verifier lane): the adapter is a real
component; the J2 result is a PARTIAL measurement (noul-class scores are real; choice-class is
refused by the tokenizer-version wall).
