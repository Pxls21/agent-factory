# MOJEV-AUDIT — read-only evidence audit of MoLeMo-Lab/mojev @ a74d58c (owner ask 2026-09-24 02:0xZ)

Owner: "I found this variant of jev that has up to 1 million tokens in context … maybe we can use them in tandem. Laya is
used for simple one-off tasks, and MoJev as a higher level, with long token context — summary, and all that kind of stuff …
especially for Hermes, since it can have the same amount of context as Hermes, and it can analyse an entire session in one
go. Our whole session between compactions." Links: https://github.com/MoLeMo-Lab/mojev, https://molemo-lab.github.io/mojev/
(the site is `docs/` in the clone). Prior audits: `docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md`,
`docs/research/findings/CANNY-AUDIT-2026-09-23.md`.

ROLE: evidence-gatherer (the EXPLORE lane). Collect evidence; do NOT conclude, recommend or rank. The coordinator writes the
verdict (Reflection Firewall). Do NOT spawn subagents.

SOURCES (both already on disk; you need no network):
- `/home/user/molemo-lab/mojev`: a shallow read-only clone. HEAD `a74d58cd19ec573e83e8e27f9fecd837b8d830fb`
  (2026-09-24T05:15:51+08:00, "Publish MoJev", one commit); MIT; 77 files; 3,784 lines of Python under `mojev/`.
- `/home/user/molemo-lab/hf-snapshot`: the Hugging Face side, fetched 2026-09-24 02:08Z (URLs and HTTP codes in `fetch.log`,
  hashes in `SHA256SUMS`): the model API JSON and file tree at model revision `0c8695b6252f4205907433d4e196a94f032e60c3`,
  the model card, `config.json`, the model repo's `modeling.py` (the code `trust_remote_code=True` executes at load time),
  the dataset `MoLeMo-Lab/mojev-mix` API JSON and card at `424bc3ea988836459c0feca10920566310a760e9`, and the base model
  `Qwen/Qwen3.5-0.8B` API JSON.

SAFETY (non-negotiable): STATIC READING ONLY. Never run, build, install or import anything from the clone or the snapshot:
no pip, no python/node on their files, no `mojev` CLI, no onnx, no torch, no `hf download`. No network calls. Read the
preprint `paper/mojev-preprint.pdf` with the Read tool (page ranges). Write ONLY the deliverable below; touch no other file
in `/home/user/agent-factory` (two other lanes and the coordinator have uncommitted work there). No commits, pushes or
outward actions. Never print a credential value (name env vars only). Our session transcripts may be read ONLY through a
script that prints numbers (never message text).

DELIVERABLE: `/home/user/agent-factory/docs/research/findings/jev-audit/mojev-evidence.md` — evidence tables with
`mojev/<path>:<line>` citations (relative to the clone root), `hf/<file>:<line>` for the snapshot, `paper:p<N>` for the
preprint and `af/<path>:<line>` for this repo, in the format of the sibling files (read `canny-evidence.md` and
`laya-evidence.md` in that directory first). Write it incrementally; a "not found" row carries the exact search you ran.

## PREMISE — MEASURED at authoring (2026-09-24 02:0xZ)

```
$ git -C /home/user/molemo-lab/mojev log -1 --format='%H %cI %an %s'
a74d58cd19ec573e83e8e27f9fecd837b8d830fb 2026-09-24T05:15:51+08:00 MoLeMo Lab Publish MoJev
$ grep -n -E '262,144|1,010,000|16,384|YaRN' README.md
68:MoJev supports a 262,144-token native context and up to 1,010,000 tokens with
69:YaRN scaling. Training truncates state inputs at 16,384 tokens; inference uses
70:that window by default. Serving at 1M uses a YaRN configuration. The `serve`,
$ (hf-snapshot/model-config.json, parsed)
24 layers {'full_attention': 6, 'linear_attention': 18} full at [3, 7, 11, 15, 19, 23]
max_position_embeddings 262144 rope {'mrope_interleaved': True, 'mrope_section': [11, 11, 10], 'partial_rotary_factor': 0.25, 'rope_theta': 10000000, 'rope_type': 'default'}
context_tokens 16384
$ (hf-snapshot/model-tree.json) model.safetensors 1710234304 bytes; browser/ = 24 per-layer q4 ONNX files + head.onnx + int8 embeddings
$ (hf-snapshot/base-qwen3.5-0.8b-api.json) base sha 2fc06364715b967f1860aea9cf38778875588b17 ['license:apache-2.0']
$ grep -rn trust_remote_code --include=*.py .    (in the clone)
mojev/serve.py:171, browser/export.py:110,162, browser/validate.py:47,49, tests/test_mojev.py:629, space/app.py:15,16
$ diff mojev/modeling.py ../hf-snapshot/model-modeling.py | wc -l
27
$ sed -n 63,67p af/scripts/no_laya_in_gates.py
SIMPLE_TOKENS = frozenset([
    "laya", "systemone", "system_one", "system-one",
    "jev", "jevcache", "sieve", "sieve-run",
    "decide-harvest", "decide_harvest", "laya-decide",
])
```

## Questions (each answered with cited evidence)

1. **What it is.** The model (`mojev/modeling.py` and the HF `modeling.py`): the base, the TreePacked attention mask, the
   rank-512 readout, the parameter count, dtype. The 27-line diff between the GitHub and HF `modeling.py`: paste it and state
   what each hunk changes (facts, no judgment). The question types and output (`mojev/schema.py`): list every type; say
   whether any path generates free text (a summary) or only scores caller-supplied candidates.
2. **Context length.** Every place the code reads or sets a context window (`context_tokens`, `--context-tokens`, YaRN or
   `rope_scaling`, `max_position_embeddings`): cite each. What happens when a state is longer than the window: truncated or
   refused; which end is kept; is it reported to the caller or silent. Whether the released `config.json` carries any YaRN
   setting, and what enabling 1M requires (cite the code or doc that says so, or "not found").
3. **Evidence at long context.** Every evaluation in the repo, the preprint, the model card and the dataset card that
   reports a result at a state length above 16,384 tokens: the length, the metric, the hardware, and whether the data that
   produced it is committed. `mojev/wikiqa.py`: what it builds and at what lengths. The preprint's claims about 262k and 1M,
   quoted with page numbers. Distinguish MEASURED (a table with committed data) from STATED.
4. **Headline results.** The 93.23 % accuracy / 0.79 % ECE claim: its producer (command, code, data split, sample size), the
   `ood` split, and whether the repo commits the outputs. The HF model-index `verified:false`. Any per-task breakdown.
5. **Compute.** Every latency, throughput or memory number in the repo, the paper and the cards, with its context length,
   batch and hardware. CPU support (dtype on CPU, any CPU path or benchmark), the ONNX/browser path's maximum context. Facts
   only; do not estimate.
6. **The server** (`mojev/serve.py`): bind address and port defaults; auth (is the api_key checked); request size and
   question-count limits; timeouts; concurrency; the image-by-absolute-path loader (what paths it will open, any allowlist,
   what an error returns to the caller); logging of request content. Wire compatibility: its request and response shapes
   against TypeSafe's `system_one` and against our endpoint (`af/scripts/laya_systemone_server.py` docstring and `_answer`).
7. **Supply chain and side effects.** A table of every network call, file write, subprocess, env read and download in the
   package, the Space and the browser tools; `trust_remote_code` uses; pickle or `torch.load` uses vs safetensors;
   `pyproject.toml` dependencies and their pins; the CI workflow; any telemetry.
8. **Training data provenance.** `mojev/openjev.py`, `mojev/balance.py`, `mojev/data.py` and the dataset card: every source
   dataset or API named, and its license as stated. Whether any labels come from a hosted model's outputs (for example
   TypeSafe's API); quote the lines.
9. **Tests.** What `tests/test_mojev.py` covers (by area), whether any test exercises a state above 16,384 tokens, and the
   CI workflow's steps.
10. **Our side, facts only (cite into af/).** (a) KC-J1 and KC-J1b (`af/docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md`) and
    the never-a-gate vocabulary (`af/scripts/no_laya_in_gates.py:56-76`): would the tokens `mojev`, `MoJev`, `PackedScorer`
    or a `mojev serve` command line fire the screen? Answer from the matching rule's code and comments, not by running it.
    (b) The prior audit's §5 venue facts, §7 constraints and §8 fit list (`af/docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md`),
    quoted. (c) The PC's recorded resources (`af/PC-BRIDGE.md`: cores, RAM, the 3090 and what holds it) and LAYA-PROBE-1's
    measured CPU latency (`af/docs/research/findings/LAYA-PROBE-1.md`). (d) The owner's target input, MEASURED: for the
    coordinator transcript `/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl`, with a script that
    prints numbers only, the context size at each compaction (the last assistant record's usage before each compact boundary:
    input + cache-read + cache-creation tokens) and the byte size of each segment between boundaries; for PC lane sessions,
    quote the recorded prompt sizes (`af/docs/INCIDENT-LOG.md`, the AF-AP-146 row and entry). (e) The seams the owner's idea
    would touch, listed with citations and not assessed: the continuity plane (the ledger lines for task #25), the dream-phase
    triage (#195), the AP-hawk (#115) and drift-hawk (#116) proposals (`af/todo/BUILD-TASKLIST.md` and `af/docs/08_DECISION_LOG.md`
    D-046/D-047), and `af/docs/11_DREAM_PHASE.md`'s section headings.

## AMENDMENT 1 (2026-09-24 02:1xZ): three more owner use cases, three more questions

The owner stopped the first run (it made no deliverable yet) and added three use cases. Relaunched on Opus 5.5 (D-065). The rules
above hold for these questions too: facts only, cited, static reading, numbers-only transcript scripts.

11. **Bug localization** (owner: "it gets a bunch of outputs from the different tools and the error trace, then determines which
    function is the problem"). (a) What our code-intel instruments output: `af/scripts/lane_context.sh`, the pack's sections and which
    tool fills each (graft, GitNexus, codebase-memory, code-review-graph, ripwire, ap_screen), cited. (b) An evaluation corpus we
    already own: up to 15 past defects in `af/docs/INCIDENT-LOG.md` and its AF-AP registry rows that record BOTH the failing test or
    trace AND the fix commit or the function changed, each cited; do not analyze them. (c) Whether mojev-mix or the preprint has any
    code, stack-trace or program-repair domain: quote the domain list.
12. **Workflow hygiene** (owner: the model decides when the wiki, skills or the anti-pattern registry need an update, instead of a
    hook that reminds every time and costs tokens). (a) What fires the Stop hook `af/.claude/hooks/turn-retro-gate.sh`, what it
    injects, the byte size of the injected text, and whether `af/scripts/gate_files.txt` lists it. (b) The post-commit wiki-stale
    mechanism (`af/scripts/hooks/`, `.git/wiki-stale`) and what it triggers. (c) With a numbers-only script: how many times the retro
    checklist was injected in the coordinator transcript named in question 10(d), matched on a fixed marker taken from the hook's own
    source (paste the marker), per day.
13. **Context manager** (owner: "out of all the files and all the pieces of information we have, what is the most important thing
    right now that the agent needs to know … Laya identifies what needs to be searched, MoJev finds it and decides what to present,
    injected through the hooks"). (a) Every hook that injects context today and what it injects: `af/.claude/settings.json` (hook
    registrations), `session-start.sh`, `wiki-context.py` (how it selects excerpts: the matching rule, the budget), the graft-first
    nag; cite each. (b) The sieve plan already decided for Laya: the relevant lines of
    `af/docs/research/findings/RESEARCH-FINDINGS-2-part1-laya-sieve-fp32-build-spec.md`,
    `af/docs/research/findings/RESEARCH-FINDINGS-2-part2-system-one-integration-map.md` and
    `af/docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md` (its gates, e.g. the shadow week), quoted. (c) From the MoJev side: whether
    any code path, the preprint or the cards treat retrieval, reranking or relevance scoring over many candidates, and the largest
    candidate count per request the server accepts (question 6's limits).

## Final message (at most 40 lines)

The deliverable path and size; the count of cited rows per section; everything you could not determine and why. No
recommendation.
