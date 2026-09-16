# vLLM migration — grounded findings + plan (2026-09-16)

Owner directive 2026-09-16: switch the local build/verify model server off llama.cpp onto **vLLM**
(better batching + spec-decode). Owner constraint: the model must stay **Qwen3.8-27B** (the live
version; the on-disk 3.6 AWQ/GPTQ are the wrong version and are OUT). vLLM sits BEHIND OmniRoute as a
provider (same `127.0.0.1` served-model-name `qwen3.8-27b-local`) — sole-egress unchanged.

All facts below are from live PC probes (read-only; GPU untouched) and web research (sources at the end).

## The hardware wall — and the way through it

- **Stock 3.8 quants do NOT fit one 24 GB 3090.** `Qwen/Qwen3.8-27B-FP8` ≈ 28 GB; the community AWQ
  `barrydeen/Qwen3.8-27B-AWQ-4bit` is **27.8 GB** and "Built for 2× RTX 3090" (the 48 Gated-DeltaNet
  layers stay BF16 because they are quant-sensitive). `unsloth/Qwen3.8-27B-NVFP4` needs Blackwell (the
  3090 is Ampere). The only 3.8 quant that fits one card at stock is the aggressive GGUF — i.e. what
  llama.cpp runs now.
- **The way through:** a dedicated, benchmarked community build — **`syv-ai/qwen38-27b-rtx3090`**
  ("Qwen3.8-27B on a single RTX 3090 with vLLM"). It requantizes a W4A16 base (lm_head/embeddings/MTP →
  int8, int4 lm_head, a 40k draft vocab) and patches vLLM 0.28.0 (split-KV verify attention, MTP
  own-output draft), fitting ~21.8 GB and delivering big batching throughput.

## The path (syv-ai recipe)

- **Base weights:** `dbirks/Qwen3.8-27B-W4A16-AutoRound` (~19.5 GB) — a calibrated 4-bit of the real
  Qwen3.8-27B (the vLLM-native analogue of the "dynamic" GGUF).
- **Stack:** a NEW venv with **vLLM 0.28.0** + flashinfer (the installed vLLM is 0.24.0 — a separate env).
- **Requant (CPU, ~5 min):** `prepare/quant_lm_head.py`, `quant_embed.py`, `quant_mtp.py`,
  `build_draft_vocab.py`, `fetch_fast_variant.py` (int4 head+drafter), optional `fetch_dflash2.py`.
- **Patch:** apply `patches/series` to `venv/.../vllm` (targets 0.28.0 exactly).
- **VRAM budget (measured):** weights 14.7 + KV@65k 3.2 + Mamba state 0.88 + overhead 3.0 = **~21.8 GB**
  (fits 24 GB). Context modes: fast 64k BF16 KV / long 138k int8 KV / huge 268k 4-2bit KV.
- **Measured throughput (one 3090, 250 W):** single-user 118–133 tok/s (382 with DFlash2 doc-repro);
  **batch C64 ≈ 1,035 tok/s aggregate** (8 slots). vs the current llama.cpp: 62 single / 93 at 4-up.
- **MTP** included (`--speculative-config method=mtp` or DFlash2). Also an official Docker image
  `ghcr.io/syv-ai/qwen38-27b-rtx3090:latest`.
- Prereqs: ~40 GB disk (PC /home has ~580 GB free), 16 GB+ RAM (PC has 125), Python 3.12+, CUDA driver.
  Download ~10 min, requant ~5 min, first boot ~5 min (torch.compile).

## Plan

1. **Prep (no GPU, non-disruptive — qwen-builder stays up):** clone `~/qwen-serving`, build the vLLM
   0.28 venv, download `dbirks/Qwen3.8-27B-W4A16-AutoRound`, run the requant scripts, apply the patches,
   `bash verify.sh --no-server`. All CPU/disk.
2. **Cutover (needs owner say-so — `qwen-builder` is on the do-not-stop list):** stop `qwen-builder`,
   launch the vLLM server (batch mode for lanes), benchmark single + 2/4/8/64 concurrent, confirm the
   ~1000 tok/s figure and the context that fits, wire it on the port OmniRoute expects with
   served-model-name `qwen3.8-27b-local`. Keep the `qwen-builder` unit as instant fallback.
3. **Productionize:** a `vllm-builder` systemd unit replacing `qwen-builder`; update the OmniRoute local
   route if the port/name differs; PC-BRIDGE.md + upstream.lock.yaml pins + the ledger.

## Notes / decisions

- The stock-quant hardware wall is the reason 3.8 has been on llama.cpp: only the aggressive GGUF fit one
  card. The syv-ai requant is what makes vLLM viable on one 3090. A 2nd 3090 would also work (the
  barrydeen AWQ is the clean TP=2 path) — the owner's standing #61 GPU question.
- Serving mode: **batch mode** (SPEC=mtp, GPU_UTIL 0.90) for the fire-and-forget lanes; single-user
  DFlash2 mode is available if a latency-first path is ever wanted.

## Serving on the PC — the toolchain reality (2026-09-16)

The model is prepared and `verify.sh` green (above). **Native vLLM serving on this bare-metal PC is
blocked by a CUDA-toolchain version triangle**, not a model problem:
- vLLM 0.28.0 is built for **CUDA 13** (needs `libcudart.so.13`); the box's CUDA **toolkit is 12.9**.
- With `CUDA_HOME=/usr/local/cuda` + PATH set (nvcc 12.9 found), torch.compile/inductor works, but
  **flashinfer** can't JIT its fp8-KV attention kernel: the recipe pins `flashinfer-cubin==0.6.13`
  while the *unpinned* `flashinfer-python` pulled 0.6.16.post3 (no 0.6.16 cubin exists) → JIT → ninja
  exit 1.
- Pinning `flashinfer-python==0.6.13` to match dragged torch back to **cu128**, which then breaks vLLM
  (`libcudart.so.13: cannot open`). vLLM(cu130) ↔ flashinfer(cu128) ↔ toolkit(12.9) don't reconcile
  natively without installing the CUDA 13.0 toolkit (a sudo step).

**The path: the vendor's Docker image via ROOTLESS CDI — no sudo, no bypass tool.**
- `ghcr.io/syv-ai/qwen38-27b-rtx3090:latest` (~9.5 GB) bundles the exact matched
  torch+vLLM+flashinfer+CUDA 13, so the triangle vanishes.
- `nvidia-ctk cdi generate --output=$HOME/cdi/nvidia.yaml` runs WITHOUT root (reads driver info via
  NVML); `~/.config/containers/containers.conf` `[engine] cdi_spec_dirs=["/home/rocco/cdi", …]` lets
  rootless podman 5.7 inject `--device nvidia.com/gpu=all`. (A third-party "nopasswd-sudo" tool the
  owner offered was DECLINED — running untrusted root-escalation on a production box is exactly what
  the no-sudo-workaround rule forbids; rootless CDI made it moot.)
- Run (batch/MTP, port 8080, mount the already-prepared model so there is no 20 GB re-download):
  `podman run -d --name qwen --device nvidia.com/gpu=all --ipc=host -p 8080:8080 -e PORT=8080
  -e VLLM_API_KEY=$(cat ~/.config/qwen-builder/api-key) -v ~/qwen-serving/models:/app/models
  -v qwen-cache:/cache ghcr.io/syv-ai/qwen38-27b-rtx3090:latest batch`
  (first boot ~15 min: torch.compile + graphs + flashinfer JIT, all inside the matched image).
  Container-measured batch: **~1,042 tok/s @ C64**; `single` profile = DFlash2 (owner chose MTP/batch).
- The `qwen-builder` llama.cpp unit stays the live server until the container is healthy; it is the
  instant fallback (restore: `systemctl --user reset-failed qwen-builder && … start`).

STATE 2026-09-16 18:2xZ — KEEPER (D-032), PRODUCTIONIZED. The container runs under a `--user` rootless
Quadlet (`deploy/qwen.container`, mirrored to `~/.config/containers/systemd/qwen.container`) and serves
Qwen3.8-27B under BOTH `qwen3.8-27b-local` and `qwen3.8-27b` on :8080; measured ~45 tok/s single-request
decode, near-linear to ~310 tok/s aggregate at 7 concurrent lanes. Image digest pinned in
`upstream.lock.yaml`. DONE + verified live this session:
- (a) NAME RECONCILE — the served name is now `qwen3.8-27b-local` (the id OmniRoute's `qwen-local` node +
  the `agentfactory-*-local` combos already forward, and the same name the llama.cpp `qwen-builder`
  served), so local-route lanes resolve with NO OmniRoute change; a 1-token completion under
  `qwen3.8-27b-local` returned `model=qwen3.8-27b-local`. Set via `EXTRA_ARGS` because the image hardcodes
  `--served-model-name qwen3.8-27b` and appends `${EXTRA_ARGS}` last, and vLLM's `--served-model-name` is
  last-occurrence-wins. Because both servers present the same name on the same port, primary↔fallback is
  transparent to OmniRoute.
- (b) BOOT UNIT — the Quadlet has `Restart=always` and is wired into `default.target.wants` (linger on),
  so it survives reboot; `qwen-builder`'s autostart is DISABLED (`systemctl --user disable qwen-builder`;
  the unit is kept installed as the manual fallback) so they no longer collide on :8080/GPU at boot.

(c) BUZZ LOCAL-MODEL TEAMMATE — PROVEN live 2026-09-16: a standalone `buzz-agent` ACP smoke held a session
backed by Qwen via OmniRoute (`buzz_agent::llm: call completed model="qwen-local/qwen3.8-27b-local"
provider=OpenAi`), no relay/pairing touched. Recorded: D-033, ADR-0007, `docs/LOCAL-MODEL-GUIDE.md` (the
portable how-to). STILL PENDING (no hollow green): which Buzz agents/scopes get a Qwen teammate, a policy gate
for the buzz-agent tool path (rule 9 — so a Qwen teammate is chat-only until then), a dedicated OmniRoute Buzz
key, and pairing (the owner's per-community step in the Buzz app).

## Sources

- https://huggingface.co/Qwen/Qwen3.8-27B-FP8
- https://recipes.vllm.ai/Qwen/Qwen3.8-27B
- https://huggingface.co/barrydeen/Qwen3.8-27B-AWQ-4bit
- https://github.com/syv-ai/qwen38-27b-rtx3090 (README: the full recipe)
- https://huggingface.co/dbirks/Qwen3.8-27B-W4A16-AutoRound (the base weights)
