# Deployment contract

No runnable production Compose file is included yet. The first-party adapters, policy service, hardened images, immutable image digests, stateful OmniRoute bootstrap, and target-host gVisor proof do not exist. A Compose file that concealed these gaps would be misleading.

`topology.blueprint.yaml` is a planning inventory and must not be passed to Docker Compose.

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
