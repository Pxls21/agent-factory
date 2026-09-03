---
topic: pc-bridge-and-environment
last_compiled: 2026-09-03
---

# PC Bridge and Environment — execution host, probed facts, observability

## 1. Purpose [coverage: high -- 6 sources]

The owner's PC (Fedora 42, Ryzen 5, RTX 3090, 128 GB RAM) is the execution host for everything
the sandbox cannot run: containers (podman), gVisor, the model server, and long/live jobs.
Communication is through a token-gated HTTP bridge with per-session ephemeral links. The
observability plane (OpenObserve, Phoenix) runs on the PC but receives nothing from this project
yet.

CLAUDE.md invariant: **heavy jobs ON the PC.** Development + verification lanes stay in the
sandbox (parallel delegates, isolation, rollback safety); everything heavy or live runs on the PC.

## 2. Architecture [coverage: high -- 5 sources]

**Bridge protocol** ([PC-BRIDGE.md](PC-BRIDGE.md)):
- `POST <URL>/exec` with header `X-Agent-Token: <token>` (the ONLY accepted auth form)
- Body: `{"cmd": "<shell command>"}` --> response `{"rc": <int>, "stdout": "...", "stderr": "..."}`
- Links and tokens are EPHEMERAL (never committed); owner pastes "BRIDGE READY" banner per session
- Helper: [scripts/pc.sh](scripts/pc.sh) (JSON-encode, right header, `Connection: close`,
  retry on non-JSON response)
- Connection-poisoning quirk: rejected request leaves unread body in the tunnel's pooled
  connection; next request parses as garbage. Mitigation: `Connection: close` + retry.

**PC-side facts** (probed 2026-09-03, spike #0,
[spikes/pc-bridge/result.json](spikes/pc-bridge/result.json)):
- Fedora 42, kernel 6.17.11, 12 cores, 125 GB RAM, 701 GB free on /home, SELinux Enforcing
- RTX 3090 24 GB; vLLM resident ~10.2 GB
- podman 5.7.0, user socket active; podman-compose ABSENT
- Buzz production relay stack RUNNING: postgres:17-alpine, redis:7-alpine, minio, relay (3001),
  pairing-relay
- OmniRoute RUNNING on port 20128
- vLLM at localhost:8010/v1 serving `sim9b` (Qwen 3.5 9B AWQ, max_model_len 16384)
- Ollama on 11434 (bge-m3 embeddings), mirofish-ollama on 11435
- Phoenix 17.26.0 (6006/4317), OpenObserve (5080) -- RUNNING but receiving nothing from this
  project
- neo4j x2, mirofish/miroshark, osint/analyst stacks
- runsc ABSENT; /dev/kvm ABSENT (CPU has SVM; modules on disk but unloaded)
- rustc/cargo 1.93.0 default; rustup has 1.95.0 (ai-memory buildable with `cargo +1.95.0`)
- Python 3.13.11, python3.11, node v22.21.1, uv 0.9.17
- sudo NEEDS_PASSWORD

**Observability** ([docs/OBSERVABILITY-RUNBOOK.md](docs/OBSERVABILITY-RUNBOOK.md)):
- OpenObserve: port 5080, OTLP HTTP ingest, Basic auth. Credential staleness on container
  recreate (check `ZO_ROOT_USER_PASSWORD` from `podman inspect`).
- Phoenix: UI 6006, OTLP gRPC 4317.
- PandaProbe: retained roadmap component, NOT deployed.

**Sandbox environment** (from findings):
- Python 3.11.15, node 22.22.2, uv 0.8.17, Docker CLI (no daemon), no runsc, no bwrap
- Root (uid 0); pip/npm/uv installs work; raw.githubusercontent.com blocked
- GitHub access session-scoped (`add_repo` per repo)

## 3. Talks To [coverage: medium -- 4 sources]

- Sandbox --> PC bridge (`scripts/pc.sh`) --> PC execution host
- PC: OmniRoute --> vLLM / other model providers
- PC: Buzz relay stack (postgres, redis, minio, relay, pairing-relay)
- PC: OpenObserve/Phoenix --> planned telemetry from future components
- PC: podman containers for production topology testing

## 4. API Surface [coverage: medium -- 3 sources]

- `scripts/pc.sh '<cmd>'`: the bridge helper (committed, self-contained)
- `scripts/pc_lane.sh`: sandbox-side lane spawn coordinator for PC-side agents
- Bridge contract: `X-Agent-Token` header, `{"cmd"}` body, `/exec` endpoint
- Long jobs: fire-and-poll pattern with `setsid` + `flock` guard (never hold HTTP > 2 min)

## 5. Data [coverage: medium -- 3 sources]

- `.pc-bridge.env` (untracked, gitignored): `PC_BRIDGE_URL` and `PC_BRIDGE_TOKEN`
- Spike result: `spikes/pc-bridge/result.json` (probed facts, redacted links)
- PC-side: model weights, running containers, OmniRoute state, observability stores
- Runbook: `docs/OBSERVABILITY-RUNBOOK.md` (PC facts verified 2026-09-03)

## 6. Key Decisions [coverage: high -- 4 sources]

- Owner ruling (2026-09-03): "the system is supposed to run on my PC, supposed to use PC bridge"
- HYBRID compute placement (sandbox for dev/verify, PC for heavy/live)
- vLLM is NOT a dependency -- OmniRoute is the egress, vLLM is merely one of its upstreams
- Owner ruling: never stop/restart the owner's running servers without say-so; `sudo` needs
  the owner's password
- AF-AP-4: sandbox-probe-as-world -- venue classification from sandbox alone while the PC
  holds the capability

## 7. Gotchas [coverage: high -- 5 sources]

**NOT-built (first-class):**
- No component ships telemetry to OpenObserve or Phoenix yet (sinks running, nothing sends)
- Harness ports NOT smoke-tested on the PC
- No bridge banner this session = bridge-side items are `NOT run here: no bridge banner`
- runsc absent on the PC (owner `sudo modprobe kvm_amd` + install needed)
- podman-compose absent (but buzz-prod containers exist via some compose path -- unverified)

**Bridge quirks:**
- Connection-poisoning on rejected requests (mitigated by `Connection: close` + retry)
- `pgrep -f` self-match kills the bridge shell (`[b]racket` pattern required)
- Long-running calls must use setsid + flock guard (not `nohup &`, which dies with process group)
- tirith bash-hook "bind" warnings on every call's stderr -- harmless noise

## 8. Sources

- [PC-BRIDGE.md](PC-BRIDGE.md)
- [scripts/pc.sh](scripts/pc.sh)
- [spikes/pc-bridge/result.json](spikes/pc-bridge/result.json)
- [spikes/pc-bridge/README.md](spikes/pc-bridge/README.md)
- [docs/OBSERVABILITY-RUNBOOK.md](docs/OBSERVABILITY-RUNBOOK.md)
- [docs/HARNESS-PORTS.md](docs/HARNESS-PORTS.md)
