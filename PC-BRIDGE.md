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
