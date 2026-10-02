# PC lane SGL-SMOKE2 (task #454): the Hermes smoke lane again, after the out-of-memory fix

PIN: bfc0bc38 (the origin head at authoring). Role: code-implementer. Route: `HERMES_MODEL=qwen-local/qwen3.8-27b-local`
(the raw local id, D-114: no cloud fallback). Claim nothing about which model you are; the harvest measures it. Venue:
`tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey ultra, Lever-2: the report is DATA. Keep your context small. Do NOT
spawn subagents. This lane changes NO file: it is a smoke run that gathers evidence.

AUTHORIZATION AND LIMITS: first-party work on the owner's PC; the owner approved the switch to SGLang (D-129). Never read
a secret, a real profile's `.env`, `~/.hermes/` or any `*.env`. No network beyond your model route. No server touch:
never stop, restart or call the model server yourself. No outward-facing action. Write only your report.

## WHY

The PC's local model server changed from vLLM to SGLang on 2026-10-02 (task #454). The first SGL-SMOKE lane did not
finish: SGLang ran out of GPU memory on the lane's first long prompt (03:53:58Z), the container restarted, and the
lane's request got a 502. The unit now runs without the prefill CUDA graphs (3.46 GB of GPU memory left after
startup, against 1.17 GB), deployed at 04:15:19Z. This lane runs the same smoke: several turns, tool calls, and
tool results read back by the model.

## CONTRACT (evidence only; change nothing)

1. **Premise.** Re-run the block below in your lane tree; stop and report on any mismatch.
2. **Tool round trips.** Run each of these with your terminal tool, one call each, and paste each output whole:
   `wc -l deploy/qwen.container deploy/sglang_start.py scripts/serving_ab/abwin2.sh`;
   `grep -c 'gone()' scripts/serving_ab/abwin2.sh`;
   `git rev-parse HEAD`.
3. **A file read.** Read `deploy/sglang_start.py` with your file tool and quote the line that sets `KEY_FILE_DEFAULT`.
4. **One sentence** naming anything unexpected: a refused tool call, an empty reply, a warning about the model or the
   route. "None" is a valid answer.

## REPORT

Your final message is the report: the premise re-run, items 2 to 4 with their pasted outputs. NOT done, first-class.

## PREMISE — MEASURED at authoring (2026-10-02 04:1xZ, a sandbox worktree at the PIN)

```
$ git rev-parse HEAD
bfc0bc38c563799f3c70ffa6e7b4f8b1fd3e6593
$ wc -l deploy/qwen.container deploy/sglang_start.py scripts/serving_ab/abwin2.sh
   46 deploy/qwen.container
   86 deploy/sglang_start.py
  211 scripts/serving_ab/abwin2.sh
  343 total
$ grep -c 'gone()' scripts/serving_ab/abwin2.sh
2
$ grep -n '^KEY_FILE_DEFAULT' deploy/sglang_start.py
22:KEY_FILE_DEFAULT = "/app/api_key.txt"
```
