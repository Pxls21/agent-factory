# Observability runbook (agent-factory) — the human plane on the PC

The PLC principle (CLAUDE.md Telemetry): every part of the system externally observable — when
anything goes wrong, open the dashboards and see exactly what happened, zero guesswork. Ported
from `trading-system/docs/OBSERVABILITY-RUNBOOK.md`; the PC facts below were VERIFIED LIVE via
the bridge on 2026-09-03 (spike `pc-bridge`), the operating lessons come from the source repo.

## Planes

1. **Committed evidence spine (planned, Stage 0 increments 1–2):** proof runners write
   `result.json` artifacts (commands, exit codes, sha256 digests, env_fingerprint); the generated
   ledger is the durable record. This is the byte-invisible truth; nothing below may change it.
2. **Common audit envelope** (`docs/03_INTEGRATION_CONTRACTS.md` §9) — the event shape every
   component emits once code exists (schema_version, session/turn ids, governance_hash,
   event_type, payload, redaction_version). Reason field mandatory on every decision/branch.
3. **Human plane on the PC — default OFF, opt-in per run:**
   - **OpenObserve** — rootless podman container `openobserve`
     (`public.ecr.aws/zinclabs/openobserve:latest`), port **5080**, running (probe 2026-09-03).
     OTLP HTTP ingest base `http://localhost:5080/api/<org>`; the SDK appends `/v1/traces` and
     `/v1/logs`; auth `Authorization: Basic b64(email:password)`.
   - **Arize Phoenix** — podman container `phoenix` (`arizephoenix/phoenix:17.26.0`), UI **6006**,
     OTLP gRPC **4317**, running (probe 2026-09-03).
   - **PandaProbe** (`docs/06_EVALUATION.md` §7) stays a retained roadmap component — NOT deployed.

## Operating lessons (inherited, re-verify before relying)

- **OpenObserve credentials go STALE when the container is recreated**: the container's
  `ZO_ROOT_USER_PASSWORD` is the only authority; any credentials file is a copy. Divergence =
  every OTLP export answers `401` while endpoint/header look correct — a silently dead plane.
  Recover from the container: `podman inspect openobserve --format '{{range .Config.Env}}{{println .}}{{end}}'`.
  **Verify, don't assume:** `curl -o /dev/null -w '%{http_code}' -X POST
  http://localhost:5080/api/default/v1/traces -H "Authorization: Basic <b64>" -H 'Content-Type:
  application/x-protobuf' --data-binary ''` → `200` = auth good (writes zero spans); `401` = wrong.
  Any exporter this project ships MUST run that preflight at init and refuse to enable on
  401/403 with a loud `otel_degraded reason=export-rejected` event (fail-soft is fail-LOUD).
- Basic-auth header in env files percent-encodes the space (`Authorization=Basic%20<b64>`).
- Restart after reboot: `podman start openobserve` / `podman start phoenix`; health
  `curl localhost:5080/healthz` → `{"status":"ok"}`.
- Query-back (round-trip proof): `POST /api/default/_search?type=traces` with
  `{"query":{"sql":"select … from default where …","start_time":<us>,"end_time":<us>}}` — MICROseconds.
- Never commit credentials; never bake dashboards into a gate — promotion consumes signed,
  immutable results (`docs/06` §7), dashboards are advisory.

## Status
`NOT built.` here: no exporter, no envelope emitter, no dashboards wired — this runbook records the
live PC endpoints and the lessons so the first telemetry increment starts from facts.
