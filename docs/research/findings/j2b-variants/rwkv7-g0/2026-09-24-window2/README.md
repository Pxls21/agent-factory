# RWKV-7 G0, window 2 (2026-09-24 23:24Z-23:29Z): zero-shot fails every KC-J3 line; the long-input mechanics work

Run: `rwkv7_g0.py --out-dir ~/rwkv-g0/out-b-w1` in `~/venv-rwkv-b` (torch 2.7.1+cu128, transformers 4.53.3, fla 0.3.0,
triton 3.3.1, Python 3.11.15), job 1 of GPU window `20260924T232358Z` (`scripts/gpu_window.sh`, the jobs file
`tasks/briefs/jev-laya/window1.jobs`; `window-record.jsonl` is that window's record). Model: RWKV7-Goose-World2.9-0.4B-HF
(snapshot e94655a9fad2c8da9f25aba575d8f0fdedc05931), bf16, 450,767,872 parameters. The files here are the PC outputs,
each sha256-checked on arrival. Zero-shot only; J4 (the long-input test) is not built.

## Quality: no probe beats its baseline (KC-J3: REJECTED on every line)

| probe (file) | RWKV-7 0.4B | baseline to beat | reading |
|---|---|---|---|
| ap choice (`ap_choice.json`) | top-1 0.57, top-3 0.68 | lexical top-1 0.59, top-3 0.69 | at or under lexical |
| ap scored per row (`ap_noul.json`) | top-1 0.08, top-3 0.20 | lexical 0.59; majority 0.09; random 0.061 | near random |
| v1 titles, choice (`v1.json`) | accuracy 0.10 | majority 0.43, heuristic 0.41 | under |
| v1 titles, scored (`v1.json`) | accuracy 0.13 (balanced 0.21) | majority 0.43 (balanced 0.17) | under on accuracy |
| v1 full text, choice (`v1_full.json`) | accuracy 0.18 | majority 0.43, heuristic 0.32 | under |
| v1 full text, scored (`v1_full.json`) | accuracy 0.15 (balanced 0.24) | majority 0.43, heuristic balanced 0.22 | under on accuracy |
| v1 rich choice (`v1_choice_rich.json`) | accuracy 0.07; BLOCKER 7/7, every other class 0 | majority 0.43 | one constant answer |
| v1 blocking (`v1_blocking.json`) | blocking recall 0/9, false alarms 0/91 | the never-blocking split 0.91 | one constant answer |

Not resolved here: the ap choice top-1 (0.57) sits at the lexical top-1 (0.59), and the probe passes its 16 candidates
sorted by lexical overlap (`j2b.py` `ap_choice`: `criteria` is built from the sorted list). The probe records only its
summary, so a first-option bias is not excluded; a model that always picked the first candidate would score the
lexical top-1.

## Mechanics: what the long-input plan needs holds on the 3090

- Load 0.44 s; 859 MiB allocated.
- One forward over real repo text (`g0.json` ladder; all logits finite): 2,048 tokens 42.9 s (the first call pays
  Triton's compile and autotune), 4,096 0.38 s, 8,192 0.18 s, 16,384 1.47 s, 32,768 0.64 s, 61,440 1.17 s; peak memory
  1,260 MiB at 2k up to 10,474 MiB at 61,440 tokens.
- A 15-token question answered from a copy of the saved state: median 0.0372 s after 16,384 tokens and 0.0456 s after
  61,440 tokens (the first 16k call, 9.6 s, includes a compile).
- Prefix-then-suffix against one whole forward: the same argmax; the largest logit difference 0.1875 (bf16).
