# Deployment contract

No runnable production Compose file is included yet. The first-party adapters, policy service, hardened images, immutable image digests, stateful OmniRoute bootstrap, and target-host gVisor proof do not exist. A Compose file that concealed these gaps would be misleading.

`topology.blueprint.yaml` is a planning inventory and must not be passed to Docker Compose.

## Deployed non-spine units

- `qwen.container` — the PC-side rootless Quadlet for the Qwen3.8-27B local model server, the keeper build/verify backend behind OmniRoute: SGLang v0.5.20 with EXL3 weights (D-129; pinned in `pc-lane.lock.yaml`, D-131), started by `sglang_start.py`, which keeps the API key off the command line and out of the log. `qwen-vllm.container` is the vLLM unit it replaced (D-032), kept as the fallback. This is real, running dev/build infrastructure on the owner's PC — NOT part of the production spine below, which is still planned. It sits behind OmniRoute (rule 3), never a direct egress. See `docs/research/findings/VLLM-MIGRATION.md` and `PC-BRIDGE.md`.
- `heat-guard.service` with `heat_guard.sh`: the PC's CPU heat guard (D-136, AF-AP-263), a rootless user service that starts at boot. Every 5 s it reads the CPU's Tctl; after three readings in a row at or above 90°C, or unreadable, it stops the `qwen` unit. Both qwen units require it (`Requires=` with `After=`), so the model server does not start without it and stops when it is stopped; both also cap their CPU at three threads (`CPUQuota=300%`). It watches the model server only: other CPU load on the PC is not guarded. The PC went down four times on 2026-10-02 while SGLang started beside an old cooler. Like the units above, it is dev infrastructure on the owner's PC, not the production spine.

## Planned production deployables

| Unit | Strategy | Persistent data |
|---|---|---|
| Buzz relay | Pinned upstream production shape with Postgres 17, passworded append-only Redis, pinned MinIO/init | Relay and object/database state |
| `buzz-acp` | Pinned bridge configured to start `hermes-acp` | Cursor/session metadata as required |
| Hermes | Pinned derivative with ACP support + first-party Fubuki/memory/policy extensions; run under `runsc` | Hermes home and scoped workspaces |
| OmniRoute | Pinned image, non-default secrets, reviewed stateful provider setup | `DATA_DIR` and route state |
| Composite memory adapter | First-party non-root service/provider boundary | Minimal idempotency/audit state |
| ai-memory | Pinned source via `docker/Dockerfile`, runtime user `ai-memory` | SQLite/wiki/git memory data |
| Policy service | First-party non-root image | Versioned policy and append-only audit |

## Planned isolated later deployables

| Unit | Authority |
|---|---|
| GBrain-informed dream worker | Read sanitized exports; write proposal artifacts only |
| JIT Foundry | Read task/config inputs; write candidate artifacts only |
| AlphaEval-derived runner/evaluator | Test-only execution and results; no production secrets/network |
| PandaProbe | Optional redacted trace ingestion/analysis only |
| HarnessRouter | Absent unless an ADR activates an approved UHP-only harness |

## Network intent

- `edge`: Buzz relay ↔ `buzz-acp`.
- `acp`: `buzz-acp` ↔ Hermes native ACP endpoint/process.
- `model`: Hermes/approved internal clients → OmniRoute.
- `memory`: Hermes → composite adapter → ai-memory.
- `policy`: Hermes → policy service.
- `tool-egress`: Hermes → approved broker only.
- `provider-egress`: OmniRoute → approved model providers only.
- `research`/`evaluation`: isolated from production, with artifact-mediated input/output.
- `conditional-harness`: created only after a HarnessRouter ADR.

## Compose acceptance gate

The first real Compose file must:

- pin source commits and image digests; never use `latest`;
- preserve upstream Buzz relay security/state dependencies;
- bind management surfaces to loopback or authenticated private ingress;
- declare health, dependency conditions, restart, limits, volumes, and backups;
- use secret injection, not committed values;
- run Hermes and untrusted research/evaluation workers with `runsc`;
- omit Docker socket, broad host mounts, production credentials from research, and direct provider egress;
- keep Codex/Claude/Pi runtimes absent while retaining disabled planned units for dream/Foundry/evaluation/conditional routing;
- pass `docker compose config` and the relevant stage acceptance suite.
