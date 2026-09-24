# PC lane MOJEV-G0 (task #210): MoJev Gate 0 on the PC's CPU (load, integrity, latency, memory, truncation, order, determinism)

PIN: 8c684be (the origin head when this brief was written; the lane creates new files only).

Role: code-implementer. Route: the LOCAL build route (`agentfactory-build-local`, medium; D-061: local Hermes only). Claim nothing about
which model you are; the harvest measures the provider mix. Venue: `tasks/briefs/pc/VENUE-MAP.md`, read it FIRST; where it says "no live
model requests" it means the OmniRoute routes: loading MoJev in-process on the CPU is this lane's job. Honey ultra, Lever-2: the report is
DATA (files:lines, verbatim numbers, discrepancies, NOT-done). Keep your context small: `| tail -n 40` on long output, `sed -n` ranges
instead of whole-file reads. Do NOT spawn subagents. Code questions go to graft first (CODE INTEL FIRST).

AUTHORIZATION AND LIMITS: the owner authorized running MoJev's code and weights on this PC's CPU (D-069 item 3, 2026-09-24). CPU only:
export `CUDA_VISIBLE_DEVICES=` (the 3090 belongs to the vLLM `qwen` container). At most 6 threads (`torch.set_num_threads(6)`), every
model process under `nice -n 10`. Offline only: export `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` before any import; the code and the
weights are already on disk (PREMISE). Never `trust_remote_code=True`. Never pip-install into `~/venv-laya` (the live Laya unit's venv).
If a package MoJev needs is missing there, create `~/venv-mojev` (python3.11) and install EXACT versions from PyPI into it only, each
listed in the report. No server touch (vLLM, OmniRoute, laya-systemone, Buzz, Ollama, Phoenix: never stopped, restarted or called). No
outward-facing action. Never read `~/.hermes/`. Write only inside your lane tree (the boundary below), `../scratch/` and `~/venv-mojev`.
A model process whose resident memory passes 32 GB is stopped by you, by pid, and recorded as a finding.

## WHY (read first)

`docs/research/findings/MOJEV-AUDIT-2026-09-24.md` read MoJev statically (a 0.85B typed-decision scorer: it returns a probability per
candidate answer and writes no text). Option B (section 6), which the owner chose, needs measured facts before any use: section 4 item 3
only ESTIMATES about 20 s per decision at 4k tokens and about 60 s at 16k on this CPU; section 4 item 1 says a state over 16,384 tokens
is cut silently; section 4 item 5 says candidate order can move scores because the 18 linear-attention layers get no mask. Gate 0
measures all three plus integrity and determinism. Gate 1 (bug localization on at least 100 mined cases) waits on this result and is
NOT part of this lane.

The evidence file `docs/research/findings/jev-audit/mojev-evidence.md` cites the exact source lines: read rows 1.6-1.17 (config, class,
dtypes), 2.10-2.20 (context and truncation), 6.15-6.26 (the Engine and the request shape) before writing code.

## BOUNDARY

- CREATE `scripts/mojev_probe.py`: the Gate 0 probe. It imports torch, transformers and `mojev` LAZILY inside the function that runs
  the model, so the test file imports it on a machine without them (CI has neither).
- CREATE `tests/test_mojev_probe.py` (no model load; see TESTS).
- CREATE `docs/research/findings/mojev-probe-0.json` (the probe's own output, committed as produced) and
  `docs/research/findings/MOJEV-PROBE-0.md` (the human report; every number in it is copied from the JSON).
- CREATE `tasks/briefs/jev-laya/MOJEV-G0-report.md`. Write it incrementally from the start: a dead lane's partial report must survive.
- READ-ONLY: everything else, including `~/mojev-pin`, `~/mojev-snapshot/0c8695b6252f4205907433d4e196a94f032e60c3/` and `~/venv-laya`.
- An adjacent defect you find is REPORTED, never fixed.

## PINNED DECISIONS

- **D-1: in-process, through MoJev's own local classes.** Load with the package's `mojev.modeling.PackedScorer.from_pretrained(<snapshot
  dir>)` (the path `mojev/evaluate.py:40` `load_packed` and `serve.py`'s `Engine` use), with `~/mojev-pin` on `PYTHONPATH`. Never
  `AutoModel` on the snapshot: its `config.json` maps `AutoModel` to the Hub's `modeling.py` (remote code, PREMISE). The processor
  classes are standard transformers classes (PREMISE), so load them with `trust_remote_code=False`; if that fails, STOP and report the
  error rather than enabling remote code. Never start `serve.py`'s HTTP server. Rejected: calling the HTTP server (wsgiref, no body
  cap, no timeouts; audit section 4 item 6) and the Hub's `modeling.py` (unreviewed remote code).
- **D-2: two dtypes.** As released (bf16 encoder, fp32 head; row 1.10 says the mix is load-bearing) and an fp32 variant (the encoder
  cast to fp32 after loading). This CPU has AVX2 and no bf16 instructions (PREMISE), so the two may differ in speed a lot. Report both.
  On every request scored in both, report whether the argmax agrees and the largest probability difference.
- **D-3: deterministic inputs.** States are built from committed text (`docs/INCIDENT-LOG.md` at the PIN), cut to an EXACT token count
  with MoJev's own tokenizer. The question and the candidate strings are fixed in the probe's source. The only randomness is a seeded
  permutation (seed in the JSON).
- **D-4: one process per matrix cell,** so each cell's peak resident memory (`VmHWM` from `/proc/self/status`) is its own; the parent
  process only orchestrates and writes the JSON.

## CONTRACT (each item is a JSON block and a report section)

- **G0-1 integrity.** Before any load the probe checks `model.safetensors` against the pin: size 1,710,234,304 and sha256
  eae27bf03e0e44501316cafab2406b1505732ddf4b836d19fbb8deb642f55f50. A mismatch is a named refusal (exit 2, no load). Record the
  verified values, the code HEAD and the snapshot revision in the JSON.
- **G0-2 the matrix.** States of 2,048, 4,096, 8,192 and 16,384 tokens by 5, 10 and 16 candidates, one question per request: 12 cells,
  for BOTH dtypes (24 cells). Per cell: one warm-up plus three timed runs; wall ms p50 and max; peak resident memory; the load time and
  the resident memory after load. A single run over 600 s stops the cell and records `TIMEOUT` with the elapsed time: a finding, never
  a silent skip. Run the cheap cells first (2k/5 upward) so a slow machine still yields the small end.
- **G0-3 truncation.** A 20,000-token state: compare its probabilities with those for the first 16,384 tokens and for the last 16,384
  tokens of the same state (bitwise equality, or the largest absolute difference). State which end the model keeps, and whether
  anything (a warning, a field, a log line) reports the cut.
- **G0-4 candidate order.** One 16-candidate request at 4,096 tokens. `mojev/full.py:83` sorts candidates by text (PREMISE): find where
  that sort applies on your path and cite it. Then measure whether a candidate's probability depends on its position in the packed
  input: if the path canonicalizes the order, vary the candidate strings' leading labels so the canonical order changes (the same
  answers, different positions) over at least 5 seeded orderings. Report the largest probability change per candidate and the number
  of argmax changes.
- **G0-5 determinism.** The same request twice in one process and once in a fresh process, at 6 threads: bitwise-identical
  probabilities or the largest difference.
- **G0-6 Gate 1 feasibility.** From the matrix: the projected wall time for 100 decisions at the 8,192/10 cell and at the 16,384/16
  cell, per dtype.

## TESTS (`tests/test_mojev_probe.py`; no model load, run with `/home/rocco/venv-agent-factory/bin/python`)

- The integrity check refuses a wrong-size file and a wrong-hash file (real temp files; the named refusal text asserted exactly), and
  accepts a file whose size and hash you pass as the expected pair.
- The JSON writer refuses a result that lacks any of the 24 cells or any of the G0-3, G0-4 and G0-5 blocks (a hollow result is
  refused by name).
- The committed `docs/research/findings/mojev-probe-0.json` holds all 24 cells (a TIMEOUT cell counts, with its elapsed time) and the
  three blocks, and `MOJEV-PROBE-0.md` quotes the JSON's p50 for every cell that has one (the pattern of `tests/test_laya_probe_report.py`).
Run the file twice, paste both summary lines.

## GATES

- The test file twice (above). `python3 scripts/lint_delta.py --base 8c684be` clean for your files. `python3 scripts/ap_screen.py
  scripts/mojev_probe.py tests/test_mojev_probe.py` pasted.
- The probe's full run, with its wall time, its exit code and the JSON's sha256 pasted.

## REPORT (`tasks/briefs/jev-laya/MOJEV-G0-report.md`)

Item 1 is the premise re-measured: paste your run of the block's commands (a mismatch stops the lane with CONTRACT-INVALID). Then:
the environment (python, torch, transformers and numpy versions; which venv; threads; nice level; whether `~/venv-mojev` was created
and what went into it); G0-1 to G0-6 with numbers copied from the JSON; the gates; what could not be done and why; DISCREPANCIES;
BOUNDARY DEVIATIONS (none expected). No verdict on MoJev's usefulness beyond the numbers: the coordinator decides whether Gate 1 runs.

## PREMISE — MEASURED at authoring (2026-09-24 11:4xZ; the sandbox tree at 200ed95 over origin 8c684be, and the PC over the bridge)

```
# sandbox, 11:30Z: the Hub API for the pinned revision (read-only GET)
$ curl -sS https://huggingface.co/api/models/MoLeMo-Lab/mojev/revision/0c8695b6252f4205907433d4e196a94f032e60c3?blobs=true
sha 0c8695b6252f4205907433d4e196a94f032e60c3 lastModified 2026-09-23T20:23:19.000Z
config.json size=5935 blob=946557eb49d7 lfs_sha256=-
model.safetensors size=1710234304 blob=8507a0ef6d04 lfs_sha256=eae27bf03e0e44501316cafab2406b1505732ddf4b836d19fbb8deb642f55f50
modeling.py size=13390 blob=8b1415ffb650 lfs_sha256=-
tokenizer.json size=19989325 blob=5520bfd2dd83 lfs_sha256=06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523
$ git ls-remote https://github.com/MoLeMo-Lab/mojev
a74d58cd19ec573e83e8e27f9fecd837b8d830fb	HEAD
a74d58cd19ec573e83e8e27f9fecd837b8d830fb	refs/heads/master
# sandbox: the committed inputs the lane reads
$ git show 8c684be:docs/INCIDENT-LOG.md | wc -c
548542
$ git ls-files tests/test_laya_probe_report.py docs/research/findings/jev-audit/mojev-evidence.md docs/research/findings/MOJEV-AUDIT-2026-09-24.md
docs/research/findings/MOJEV-AUDIT-2026-09-24.md
docs/research/findings/jev-audit/mojev-evidence.md
tests/test_laya_probe_report.py
$ git ls-files scripts/mojev_probe.py tests/test_mojev_probe.py docs/research/findings/MOJEV-PROBE-0.md   (none exist yet)
0
# the PC over the bridge, 11:4xZ (the prep script ~/mojev-prep.sh ran 11:35:57Z..11:38:29Z: clone + checkout, curl at the revision, every file checked)
$ tail -4 ~/mojev-prep.log
OK blob README.md 56bb73fdbbb4b2e1b791f8bf516e04212103a784
OK sha256 tokenizer.json 06b9509352d2af50381ab2247e083b80d32d5c0aba91c272ca9ff729b6a0e523
OK sha256 model.safetensors eae27bf03e0e44501316cafab2406b1505732ddf4b836d19fbb8deb642f55f50
DONE 11:38:29Z
$ git -C ~/mojev-pin rev-parse HEAD
a74d58cd19ec573e83e8e27f9fecd837b8d830fb
$ grep -n auto_map/processor_class in the snapshot configs
5:  "auto_map": {
6-    "AutoConfig": "modeling.PackedScorerConfig",
7-    "AutoModel": "modeling.PackedScorer"
8-  },
19:  "processor_class": "Qwen3VLProcessor",
20:  "image_processor_type": "Qwen2VLImageProcessorFast"
27:  "tokenizer_class": "Qwen2Tokenizer",
$ grep -n in ~/mojev-pin
mojev/evaluate.py:40:def load_packed(checkpoint: str, device: torch.device):
mojev/serve.py:142:class Engine:
mojev/full.py:83:    return sorted(range(len(options)), key=lambda index: options[index])
$ nproc; cpu flags; memory; disk
12
avx2 
Mem:             125          18           1           2         109         106
 396G
$ ~/venv-laya/bin/python -c versions
3.11.14 2.14.0+cu130 5.17.0 2.4.6
$ ~/venv-laya/bin/python -c import PIL, torchvision
ModuleNotFoundError: No module named 'PIL'
ModuleNotFoundError: No module named 'torchvision'
```
