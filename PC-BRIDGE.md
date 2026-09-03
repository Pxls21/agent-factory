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
