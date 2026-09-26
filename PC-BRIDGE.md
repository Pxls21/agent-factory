# PC bridge runbook (sandbox → owner PC) — agent-factory

The owner's PC (`rocco@fedora` — 12-core Ryzen, 128 GB RAM, RTX 3090, Fedora 42, NVMe `/home`)
is the **execution host** for everything the sandbox cannot run: containers (podman), gVisor,
the local model server, and long/live jobs. CLAUDE.md invariant: **heavy jobs ON the PC.**
Adapted from `trading-system/docs/PC-BRIDGE-RUNBOOK.md` (verified live there 2026-07-10/11);
re-verify every PC-side fact below through the bridge before relying on it here.

**Links and tokens are EPHEMERAL — never commit them.** The owner pastes a "BRIDGE READY"
banner per session (`AGENT_TOKEN` + `trycloudflare` URL); PC-side they live in `~/.agent_token`
and `~/.agent_url`. A new bridge launch mints a new URL and token. Sandbox-side, put them in
the untracked `.pc-bridge.env` (gitignored):

```
PC_BRIDGE_URL=https://<something>.trycloudflare.com
PC_BRIDGE_TOKEN=<AGENT_TOKEN>
```

## Protocol

- Endpoint: `POST <URL>/exec` · auth header **`X-Agent-Token: <token>`** (the ONLY accepted
  form — `Authorization: Bearer`, `X-Auth-Token`, query-param, token-in-body are rejected with
  `{"error":"forbidden"}`) · body `{"cmd": "<shell command>"}` · response
  `{"rc": <int>, "stdout": "<str>", "stderr": "<str>"}` · any GET path returns `{"ok":true}`
  (health only).
- Tunnel is HTTP/HTTPS only (sandbox egress is 80/443 via the gateway) — Tailscale/SSH do NOT
  work from the sandbox.

## THE connection-poisoning quirk (cost 20 minutes once — do not rediscover)

On a REJECTED request the server responds without reading the POST body; the tunnel's pooled
connection then has the unread body queued and the NEXT request parses as garbage (an HTML
"Unsupported method" page instead of JSON). Mitigation, BOTH required: send `Connection: close`
on every request AND retry up to 3× when the response does not start with `{`. `scripts/pc.sh`
does both.

## Working pattern

- `scripts/pc.sh '<command>'` — JSON-encodes the command, posts with the right header, prints
  stdout/stderr, exits with the remote rc. Committed here so it never needs rebuilding.
- Long jobs (installs, builds, spikes): fire-and-poll — one call launches
  PRECEDENCE (bit 2026-09-06 by pc_suite.sh): `a && b && setsid x … &` backgrounds the WHOLE and-list in a
  subshell that still holds the bridge's stdout pipe, so the call blocks until the job ends and the client's
  retries launch duplicates — separate the statements with `;` (or a wrapper script) so only the setsid
  command is backgrounded, and guard INSIDE the same call on state the job creates (`if [ -s pid ]`).
  The PC's `/tmp` is a 63 GB tmpfs: point pytest at `--basetemp` under a disk-backed dir (one 8-worker
  run writes ~5 GB); the replayed launches above filled it and the next run crashed at startup.
  `setsid bash <guard.sh> > /tmp/<job>.log 2>&1 < /dev/null &`, later calls poll
  `ps -p <pid>` + `tail` the log. NEVER hold an HTTP call open past ~2 min. A plain `nohup … &`
  inside a bridge call dies with the command's process group — use `setsid` + a `flock` guard.
- `pgrep -f`/`pkill -f` self-match kills the bridge shell — use the `[b]racket` pattern trick.
- Harmless noise: every call's stderr carries tirith bash-hook "bind" warnings — ignore.
- Never stop the owner's model servers (`llama-server`, vLLM) from the bridge without owner say-so.

## PC-side facts relevant to Stage 0 (from the trading runbook — RE-VERIFY here first)

| Fact | Consequence for agent-factory |
|---|---|
| Containers = **podman** (rootless; `systemctl --user start podman.socket`, `DOCKER_HOST=unix:///run/user/1000/podman/podman.sock`, `podman-compose`, volumes need `:Z` for SELinux) | Buzz relay stack (Postgres 17 / Redis / MinIO), OmniRoute, ai-memory run here via podman-compose, not docker |
| Bare-metal Fedora 42 → KVM available (verify `/dev/kvm`) | gVisor `runsc` install + the S0-08 containment run happen HERE |
| Local **vLLM** OpenAI-compatible endpoint `http://localhost:8010/v1`, served-model-name `sim9b`, guard `~/vllm_serve.sh` (setsid+flock), tool calling ON (`qwen3_xml` parser), thinking off via `chat_template_kwargs` | OmniRoute's upstream provider for S0-03 = this endpoint. The S0-03 pass asserts upstream identity = `sim9b` in the response `model` field. **No third-party API key needed.** |
| `llama-server` 27B parked (`bash ~/llama_server_restore.sh` restores) | leave parked unless the owner says otherwise |
| Python 3.11 venvs the norm (system 3.13 avoided); Rust/cargo state unknown here | Rust 1.95 for ai-memory: verify `rustup` on the PC via the bridge (Wave-0 spike) |
| Git remote SSH with a working deploy key | the PC can clone/pull this repo directly |

## What Stage 0 runs where

- **Sandbox:** machinery (#1–2), fixture authoring, Fubuki (S0-07), ADR shells (S0-09/10/12), rubric-isolation fixtures (S0-11), selective-egress netns mechanism spike.
- **PC via bridge:** `runsc`/KVM spike + S0-08 live run · podman stacks for S0-01/S0-02 (Buzz relay + buzz-acp + hermes-acp), S0-03/S0-04 (OmniRoute + vLLM upstream), S0-06 (ai-memory) · the full S0-05 egress canaries over live units.
- Every bridge-side proof still writes the same `result.json` artifact family; the runner records `env_fingerprint = pc-bridge:<hostname>` so ledger entries name their venue.

## Session start with the bridge

1. Owner pastes the BRIDGE READY banner → write `.pc-bridge.env` (never commit).
2. `scripts/pc.sh 'hostname && uname -r && ls /dev/kvm && command -v podman runsc rustup cargo && curl -s localhost:8010/v1/models'` — the liveness + capability probe (Wave-0 spike `pc-bridge`).
3. Record the probe output as `spikes/pc-bridge/result.json` (dated; URLs redacted).

## Hermes BUILD lanes on the PC (owner ruling 2026-09-03)

All token-heavy work (building, fixing, debugging, running) runs on the owner's Hermes CLI on the
PC through OmniRoute; the coordinator keeps briefs, the contract gate and the final validation.

- **Profile:** `agentfactory` (`hermes -p agentfactory`, created with `hermes profile create
  --clone`, config at `~/.hermes/profiles/agentfactory/config.yaml`). The repo snippet
  (`harness-ports/hermes/config-snippet.yaml`: repo skills dir, MCP servers, hooks, lane approvals
  with the `git push*`/`gh pr *` hard denies) is merged ADD-ONLY into that profile by
  `harness-ports/bin/hermes-config-merge.py` (backup written first). The owner's default profile is
  never touched.
- **Model:** OmniRoute route `codex/gpt-5.6-sol-ultra` (the owner's "OpenAI sol 5.6, highest"),
  Hermes `--reasoning ultra`; both env-overridable per lane (`HERMES_MODEL`, `HERMES_REASONING`).
- **Dispatch from the sandbox:** `scripts/pc_lane.sh <brief.md> hermes code-implementer` — the
  brief MUST carry a `PIN: <full sha>` line (the lane worktree is pinned to it); the runner ships
  the brief, launches `harness-ports/bin/pc-lane.sh` detached, polls, and fetches `report.md`.
  Lane state lives PC-side under `~/agent-factory/.lanes/<lane-id>/` (brief, prompt, tree,
  lane.pid, lane.log, launch.log, report.md, usage.json). Re-running the same dispatch is
  replay-safe (a live pid or an existing report is never doubled).
  **Stop a lane with ONE signal:** `kill -TERM $(cat ~/agent-factory/.lanes/<lane-id>/lane.pid)` on the PC — the runner is
  its session's leader and its TERM trap takes the whole session with it (the harness, its terminal-tool shells, their probes
  and load loops), then removes the pidfile. Never hand-build a kill list one level deep (AF-AP-68: six orphaned busy loops
  burned six cores for 90 minutes after a pid-by-pid stop, 2026-09-08).
- **Bring-up:** `harness-ports/bin/pc-setup.sh` (user-level, idempotent: venv, gitnexus 1.6.10,
  graft, codebase-memory, code-review-graph, ouroboros, detached indexes). PC clone:
  `~/agent-factory` on the designated branch, hooks active.
- **Working directory:** `pc-lane.sh` exports `TERMINAL_CWD=<lane tree>` — Hermes's terminal tool
  takes its cwd from that carrier, not from the process cwd (`--in` alone left a lane's shell in
  `$HOME`; proven by a read-only diagnostic lane, 2026-09-03). Verified: `pwd` = the pinned
  linked worktree, `.git` is a `gitdir:` file, HEAD = PIN.
- **Hard limits, verified under yolo:** Hermes one-shot runs with `HERMES_YOLO_MODE=1` (no human
  can answer a prompt), so the lane's limits are the profile deny list plus the git/gh shims. A
  negative-control lane ran `git push origin HEAD` and `gh pr list`: both BLOCKED by
  `approvals.deny` ("not even with --yolo"), exit -1.
- **Never** run a lane against the owner's default profile; never let a lane push (blocked as
  above); never wire coordinator turn-end hooks (the retro gate) into a one-shot lane — they
  replace the final DATA report.

### gVisor install (owner-run, needs sudo)

The release binaries are staged and checksum-verified in `~/gvisor-install` (`runsc
release-20260817.0`, sha512 OK). The owner runs:

```bash
sudo install -m 0755 -o root -g root ~/gvisor-install/runsc /usr/local/bin/runsc
sudo install -m 0755 -o root -g root ~/gvisor-install/containerd-shim-runsc-v1 /usr/local/bin/containerd-shim-runsc-v1
sudo restorecon -v /usr/local/bin/runsc /usr/local/bin/containerd-shim-runsc-v1
runsc --version
```

The user-level podman runtime entry is already written (`~/.config/containers/containers.conf`:
`runsc = ["/usr/local/bin/runsc"]`). Optional, not required: `sudo modprobe kvm_amd`.

**Status 2026-09-03: `runsc` INSTALLED by the owner (`/usr/local/bin/runsc`, root:root, `bin_t`, sha256
`048b89aa…` = the staged file; `runsc version release-20260817.0, spec 1.2.1`). The shim was not
installed — podman does not need it (it is for containerd/docker); install it only if Docker ever
enters the picture. Silent success is normal: `install` and `restorecon` print nothing.**

**Verified rootless gVisor run (the runsc spike's positive control):**

```bash
podman run --rm --runtime /usr/local/bin/runsc --runtime-flag ignore-cgroups \
  --security-opt label=disable docker.io/library/alpine:3.20 sh -c 'uname -r; echo runsc-ok'
# -> 4.19.0-gvisor / runsc-ok   (dmesg inside: "Starting gVisor..."; HTTPS to example.com from inside: ok)
# negative control: the same command on the default runtime (crun) prints the HOST kernel 6.17.11-200.fc42
```

Two caveats, stated first-class for the S0-08 spec: (1) `--security-opt label=disable` — runsc refuses
an OCI spec carrying an SELinux process label (`FetchSpec failed: SELinux is not supported`), so the
gVisor sandbox, not SELinux, is the container's confinement; the host still confines the runsc process.
(2) `--runtime-flag ignore-cgroups` — rootless runsc cannot set up cgroups here (systemd driver: `Interactive
authentication required`; cgroupfs: root `cgroup.subtree_control` denied; `--cgroups=disabled` rejected by
runsc), so NO resource limits apply in this configuration even though `user@1000.service` delegates
`cpu io memory pids`. The production shape (delegated systemd cgroups or rootful) is a Wave-0 spike
question; the containment proof itself does not depend on cgroups. Platform: systrap (runsc default;
`/dev/kvm` absent).

**PC-lane concurrency cap (2026-09-06; re-measured 2026-09-07):** the model route behind `hermes -z` admits about TWO concurrent sessions on the codex members — and the owner's OWN Hermes sessions count: with two of them live (2026-09-07 23:1xZ) the SECOND of two lane dispatches was refused on every call, so the working cap is ONE lane at a time while the owner is using Hermes; dispatch the second lane in the sandbox (`code-implementer`) instead of queueing. A refused dispatch is `HTTP 503: Chat admission capacity is temporarily unavailable`. On the Ollama Cloud members (`ollama-cloud/kimi-k3`, `glm-5.2`) the cap is ONE lane: two concurrent Kimi lanes tripped the per-credential cooldown (`429 … cooling down`) within minutes and the second lane died through the exhausted codex fallback chain (13:4xZ). Launch one Kimi lane at a time; dispatch with an explicit `HERMES_MODEL` after a 24-token probe that records the SERVED model, never the combo (it degrades silently to `big-pickle`). `harness-ports/bin/pc-lane.sh` retries the 503/429 cooldown class with backoff and never the quota 429 (`exhausted their quota`). The PC clone must be ff-synced to the pushed tip for the PC-side script to carry a fix. **2026-09-06 18:2xZ update:** even ONE Kimi lane died the same way after ~30 min (lane A5g), because Hermes walks the profile's codex fallback chain on a 429 regardless of `HERMES_MODEL`; until the codex quota resets (~2026-09-07 22:00Z) the PC Hermes lane is not a build venue — build in the sandbox (Opus 4.6 `code-implementer`) and keep the PC for suites (`pc_suite.sh`). Owner item: a fallback-free lane profile.

## The vLLM Qwen container — the KEEPER local model server (2026-09-16, D-032)

- **`qwen.service`** — a `--user` rootless podman Quadlet (`deploy/qwen.container` in the repo, deployed to
  `~/.config/containers/systemd/qwen.container`; `Restart=always`, wired into `default.target.wants` with
  `Linger=yes`, so it survives reboot). The vendor image
  `ghcr.io/syv-ai/qwen38-27b-rtx3090@sha256:c52d9033…` (digest-pinned in `upstream.lock.yaml`) runs vLLM 0.28
  (MTP/batch) and serves Qwen3.8-27B under BOTH **`qwen3.8-27b-local`** and `qwen3.8-27b` on `0.0.0.0:8080`,
  behind the same `~/.config/qwen-builder/api-key` (mounted read-only to `/app/api_key.txt`; the entrypoint reads
  it). It fills the 3090 (~23.8 GiB). The served name is set through `EXTRA_ARGS` (the image hardcodes
  `--served-model-name qwen3.8-27b` and appends `${EXTRA_ARGS}` last; vLLM's `--served-model-name` is
  last-occurrence-wins), so OmniRoute's `qwen-local` node + the `agentfactory-*-local` combos resolve with NO
  OmniRoute change. Measured 2026-09-16: ~45 tok/s single-request decode, near-linear to ~310 tok/s aggregate at 7
  concurrent lanes — the concurrency win over llama.cpp (~62 single / ~93 at 4-up) is why it replaced it as PRIMARY.
- **Operate:** `bash scripts/pc.sh 'export XDG_RUNTIME_DIR=/run/user/$(id -u); systemctl --user status qwen'`;
  `podman logs --tail 50 qwen` for the vLLM boot; `/v1/models` (with the api-key bearer) lists the served ids.
- **Fall back to llama.cpp** (same name + port → transparent to OmniRoute): `systemctl --user stop qwen ; podman
  rm -f qwen ; systemctl --user reset-failed qwen-builder ; systemctl --user start qwen-builder`. Restore the
  container with `systemctl --user start qwen`. Change the unit: edit `deploy/qwen.container`, copy it to
  `~/.config/containers/systemd/qwen.container`, `systemctl --user daemon-reload`, `systemctl --user restart qwen`.
- **`GPU_UTIL=0.96` since 2026-09-26 (D-099; the image default is 0.972):** `laya-systemone` keeps a 256 MiB CUDA context (AF-AP-231), and at 0.972 vLLM had 63 MiB of slack: it crashed under four requests and could not restart. At 0.96 the KV pool is 6.83 GiB = 215,112 tokens (1.64x at 131,072) and 796 MiB stays free beside laya. A start that logs `Free memory on device ... is less than desired GPU memory utilization` names another process on the GPU: `nvidia-smi --query-compute-apps=pid,used_memory --format=csv`.
- **Never stop or restart it while a local-route lane is live** — it holds the 3090, and a restart kills every lane
  mid-turn (the `.lanes/*/lane.pid` guard rule, AF-AP-79 / D-030, applies to this container too).

## The Qwen Jev adapter's prerequisites on the PC (D-079, task #241; set up 2026-09-24 16:1xZ-16:3xZ)

The adapter (`scripts/qwen_jev.py`, lane QJ1) applies simple-jev's v1 rules to the Qwen3.8-27B that the vLLM `qwen` container
serves, through OmniRoute. What it needs on the PC, and how each piece was made (rebuild in this order):
- **`~/simple-jev`** at the pinned revision (`upstream.lock.yaml` `advisory_jev_runtimes.simple-jev.revision`, 5686b217):
  `git clone --depth 1 https://github.com/featherless-ai/simple-jev ~/simple-jev`, then check `git -C ~/simple-jev rev-parse HEAD`
  (a newer main is not the pin: fetch the pinned commit instead). Used read-only; nothing of it is copied into this repository.
- **`~/venv-qwenjev`** (Python 3.13.11, the system `python3`): `pydantic` 2.13.5, `numpy` 2.5.3, `transformers` 5.17.0 (tokenizers
  only; no torch, so it warns "PyTorch was not found"), `tokenizers` 0.23.2, `fastapi` 0.141.1, `jinja2` 3.1.6, `pytest` 9.1.1.
- **`~/qwen-jev-tokenizer`**: the SERVED model's tokenizer and chat template, copied out of the container
  (`podman cp qwen:/app/models/Qwen3.8-27B-W4A16-AutoRound/<file> ~/qwen-jev-tokenizer/` for `tokenizer.json`,
  `tokenizer_config.json`, `chat_template.jinja`, `config.json`, `generation_config.json`, `processor_config.json`). The served
  folder is the one on the vLLM command line (`vllm serve /app/models/Qwen3.8-27B-W4A16-AutoRound`), not the `-fast` twin; the
  host's Hugging Face cache holds no tokenizer for it. simple-jev's `resolve_prompt_policy` reads this `config.json` as
  "Qwen dense 27B" and picks `examples_binary`.
- **`~/.config/qwen-jev/omniroute.key`** (0600, directory 0700): the OmniRoute inference key, written in process by a script that
  reads it with `harness-ports/bin/omniroute_local_builder.py`'s own `env_value` (never printed, never in argv), so no lane process
  reads `~/.hermes/`. Rewrite it the same way after a key rotation.
- **What OmniRoute carries (measured 16:0xZ-16:1xZ):** a plain chat call with `logprobs: true, top_logprobs: 20` returns the logprobs
  for `qwen-local/qwen3.8-27b-local` and for the build combo (use the model id: the combo can fall back to the cloud chain). A chat
  call with `continue_final_message` and the prefill `{"answer": ` returned 502 `upstream_empty_response` (OmniRoute refuses a
  whitespace-only token). `/v1/completions` with a raw prompt and integer `logprobs` returned 400 on `body.logprobs`. **Measured
  2026-09-24 23:4xZ (`docs/research/findings/j2b-variants/qwen27b/TRANSPORT-2026-09-24.md`):** a `reasoning_content` field on the
  final assistant message does not reach the server's template (an `examples_binary` choice branch arrives 12 tokens short,
  exactly its reasoning block; a `reasoning` field, or both, the same). With the reasoning inside the message text, the local
  template and the wire agree token for token (both +4: an empty think block comes first). The response names the model
  `qwen3.8-27b-local`, and the 20 candidates sit in `logprobs.content[0].top_logprobs`. **Straight to vLLM (D-082: System 1
  connects directly; measured 2026-09-25 00:20Z, `docs/research/findings/j2b-variants/qwen27b/direct_probe.py`):** the same
  chat request keeps the field (1,106 tokens = the compiler), so OmniRoute is what drops it; `/v1/completions` with the
  compiler's `token_ids` as the prompt matches by construction, with the same label logprobs. The vLLM key is
  `~/.config/qwen-builder/api-key` (read in process); `/v1/models` lists `qwen3.8-27b-local` and `qwen3.8-27b`.
- **Never send `prompt_logprobs` (or `best_of`) to the shared server (AF-AP-201, 2026-09-24):** vLLM computes a float32
  log-softmax over the whole vocabulary for every prompt token, outside the memory it reserved at start. One request (a
  1,037-token prompt: 758 MiB needed, 148 MiB free) OOM-killed the EngineCore at 23:45:08Z; systemd restarted `qwen.service`
  at 23:45:21Z and it answered again at 23:50:00Z, about 5 minutes down for every user.

- **No second CUDA process while `qwen.service` runs (measured 2026-09-24 18:0xZ; a CPU-only service counts when it creates a context: `laya-systemone`'s probe holds 256 MiB, AF-AP-231, D-099):** vLLM leaves about 550 MB of the 3090 free, and a toy RWKV-7 probe failed at CUDA context creation (`CUDA_ERROR_OUT_OF_MEMORY` from `cuDevicePrimaryCtxRetain`); vLLM was unaffected. Any GPU test, even a tiny one, waits for a window with the service stopped (D-078, D-081). The RWKV-7 G0 environment: `~/venv-rwkv` (Python 3.11, torch 2.14.0+cu130, triton 3.8.0, flash-linear-attention 0.3.0, transformers 4.57.6; imports clean) and a fallback `~/venv-rwkv-b` (torch 2.7.1 cu128, flash-linear-attention 0.3.0, transformers below 4.54); the checkpoint `RWKV/RWKV7-Goose-World2.9-0.4B-HF` at e94655a9 is in the Hugging Face cache (`model.safetensors` 901,620,328 bytes).
- **The RWKV-7 environments, measured on the CPU 2026-09-24 19:1xZ (no GPU needed to see these):** `~/venv-rwkv` loads the checkpoint (450,767,872 parameters, 7.5 s) but a forward with `use_cache=True` fails at fla 0.3.0's cache: transformers 4.57.6 requires `layers` or `layer_class_to_replicate` ("You should provide exactly one of ..."); with `use_cache=False` on the CPU, fla's CPU fallback fails (`module 'torch.cpu' has no attribute 'device'`). `~/venv-rwkv-b` (torch 2.7.1+cu128, transformers 4.53.3, triton 3.3.1) cannot import fla without a visible GPU (Triton: "0 active drivers"), so its forward is testable only inside the GPU window; it is the cached path for G0 and `~/venv-rwkv` with `--no-cache` the fallback. simple-jev needs pydantic, fastapi and starlette in each venv (the same pins as `~/venv-rwkv`). There is no CPU path for RWKV-7 through fla here.
- **GPU-window preflight: Triton needs `Python.h` (measured 2026-09-24 23:1xZ, the first live window lost all three jobs in 32 s to it):** Triton compiles a C shim for its CUDA driver on first GPU use, with gcc and the interpreter's headers. The PC has `python3.11` 3.11.14 and `python3-devel` for 3.13 but no `python3.11-devel`, so `/usr/include/python3.11/` holds only `pyconfig-64.h`. The compile needs no GPU memory, so check it while `qwen.service` runs, in every venv a window job uses: `TC=$(mktemp -d); TRITON_CACHE_DIR=$TC ~/venv-X/bin/python -c 'from triton.backends.nvidia.driver import CudaUtils; CudaUtils()'; rm -rf $TC` must exit 0. With the uv CPython 3.11.13 headers on `C_INCLUDE_PATH` (`~/.local/share/uv/python/cpython-3.11.13-linux-x86_64-gnu/include/python3.11`) it compiles in `~/venv-rwkv-b` (triton 3.3.1) and `~/venv-laya` (triton 3.8.0); the clean fix is `sudo dnf install python3.11-devel` (the owner's). **Fixed 2026-09-24 23:2xZ:** the owner installed `python3.11-devel` 3.11.15-4; the same transaction moved `python3.11` and `python3.11-libs` from 3.11.14 to 3.11.15, and the venvs follow the system interpreter. The check then passed with no `C_INCLUDE_PATH` in `~/venv-rwkv-b` (triton 3.3.1), `~/venv-rwkv` and `~/venv-laya` (triton 3.8.0), 23:23Z. **Owner-run package commands carry `-y` (`sudo dnf install -y …`):** the owner's terminal does not take a typed answer at dnf's `Is this ok [y/N]` prompt (2026-09-24, not the first time), so a command without it hangs there and holds a dnf process until the terminal is closed.


## The local build-lane model on the PC — `qwen-builder` (2026-09-14; the vLLM fallback since 2026-09-16, D-032)

- **`qwen-builder.service`** (systemd --user, `Linger=yes`, **autostart DISABLED 2026-09-16 — the manual fallback to the vLLM `qwen` container above, D-032**; unit text generated by
  `harness-ports/bin/qwen-server.sh unit`; logs `~/qwen-builder/logs/server.log`): the June CUDA llama.cpp build
  `~/Desktop/projects/llama-cpp/llama.cpp-mtp/build/bin/llama-server` (version `1 (00139b6)`) serving
  `~/.cache/huggingface/hub/models--unsloth--Qwen3.8-27B-GGUF/…/Qwen3.8-27B-UD-IQ4_XS.gguf` (blob = sha256
  `40fac405…6199`) as `qwen3.8-27b-local` on `127.0.0.1:8080` behind `~/.config/qwen-builder/api-key` (0600; only
  OmniRoute reads it). It holds ~22.7 GiB of the 3090: nothing else fits on the GPU while it runs.
- **In OmniRoute:** node `qwen-local` (openai-compatible, `http://127.0.0.1:8080`), connection `qwen-local`, combo
  `agentfactory-build-local` (the local model first, then the `agentfactory-build` chain) — created and re-checked by
  `harness-ports/bin/omniroute_local_builder.py ensure|status|probe` with the installed CLI's machine-bound loopback
  token (`harness-ports/bin/omni_api.mjs`; run with `OMNIROUTE_API_KEY` unset). Exposed model id
  `qwen-local/qwen3.8-27b-local`.
- **Operate:** `bash scripts/pc.sh 'cd ~/agent-factory && bash harness-ports/bin/qwen-server.sh status'` (health +
  `/v1/models` + GPU line); `… probe` for one content-gated completion. Run `… guard` before any matrix or
  model-server restart: it reports local/cloud route per live lane from `/proc/<pid>/environ`, refuses local and
  absent-route lanes with rc 7, and lets cloud-route lanes continue. `install` returns with no service operation for an
  unchanged rendered unit; otherwise it runs that guard before it writes the unit or invokes systemd. Use
  `restart-when-idle` for a changed target: it atomically replaces `~/qwen-builder/pending/env`, keeps one watcher, and applies
  only after two consecutive zero `llamacpp:requests_processing` samples, no local lane, and no
  `~/qwen-builder/matrix/.cell.lock`. `status` shows pending hash/time/watcher/blocker; terminal env-keyed records are in
  `~/qwen-builder/logs/deferred-restart.log` (`applied`, `expired` rc 75, or `failed` rc n).
  `start|stop|restart|uninstall` guard before their first effect (AF-AP-79). Never
  restart while the owner's own sessions use the route. The bridge shell has no `XDG_RUNTIME_DIR`; the script exports
  `/run/user/$(id -u)` itself — do the same for any bare `systemctl --user` / `systemd-analyze --user` call over the bridge.


## OmniRoute on the PC — the managed unit, and the process-kill rule (2026-09-05)

- **The authoritative OmniRoute is `omniroute-migrated.service`** (systemd --user; exec
  `~/.omniroute-migration-npm/node_modules/.bin/omniroute serve --port 20128`; data dir
  `~/.omniroute-migrated`, pinned by the unit override `~/.config/systemd/user/omniroute-migrated.service.d/10-data-dir.conf`).
  Env files load in this order: `~/.omniroute-migrated/.env` → `~/omniroute-migration-20260829/candidate-home/.omniroute/.env`
  (the unit's `HOME`) → the npm package `.env`; the first setter of a variable wins. `~/.omniroute/.env` is
  read by nothing managed — it belonged to the 2026-09-05 orphan (`docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md`,
  INCIDENT-LOG 2026-09-05, AF-AP-33). Health 200 says nothing about WHICH instance answers: run
  `bash scripts/pc.sh "$(cat scripts/omniroute_invariants.sh)"` (read-only; set `OMNIROUTE_API_KEY_FILE`
  for the catalog check) before trusting the port.
- **Never kill by name on this host (AF-AP-34).** The production Buzz relay's binary shows up in the
  host process table as `buzz-relay`, so `pkill -x buzz-relay` aimed at the isolated S0-01 relay
  restarted `buzz-prod-relay-1` four times on 2026-09-04. Every server started over the bridge writes
  a pidfile (`setsid <cmd> </dev/null >log 2>&1 & echo $! > <name>.pid`); stop it with
  `kill "$(cat <name>.pid)"` only after `readlink /proc/$(cat <name>.pid)/exe` shows YOUR binary path;
  diagnose port collisions with `ss -lntp 'sport = :<port>'` + `/proc/<pid>/cgroup`, never with a sweep.
- **Owner-only actions surfaced 2026-09-05:** `REQUIRE_API_KEY=true` (the inference plane is
  unauthenticated on `0.0.0.0`, task #34); the `STORAGE_ENCRYPTION_KEY` rotation (task #33); client-key
  creation for S0-01 (needs a dashboard session — the coordinator does not use the owner's password).
