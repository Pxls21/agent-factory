> **Review status (coordinator, 2026-09-05, contract-gate lens): an OPERATIONAL HANDOFF, NOT an
> acceptance verdict — Codex's own closing words, kept.** Everything below the rule is the Codex
> session's file byte-for-byte (sha256 `9c72fe023031f906896182f89fa5280f000be3025c5dc7e1b731c05806d90b27`, 11,897 bytes; it
> was left untracked in the PC clone `~/agent-factory` and is preserved verbatim at
> `~/s0-01-pinned/.markers/handoff-codex-original.md`). What the coordinator independently
> REPRODUCED over the bridge (read-only, 2026-09-05) versus what remains Codex's REPORT:
>
> | Claim | Status |
> |---|---|
> | `omniroute-migrated.service` active; the `:20128` listener sits in the unit's cgroup; the `DATA_DIR` override exists; `/api/health` 200 | REPRODUCED with the runbook commands (MainPID 1132861; listener pid 1132879 in `…/app.slice/omniroute-migrated.service`; sole listener) |
> | the listener runs with `DATA_DIR=/home/rocco/.omniroute-migrated` | REPRODUCED from `/proc/<pid>/environ` (kernel truth, not the unit's declaration) |
> | 2,626-entry catalog; four `agentfactory-*` combos; K3/GLM inference 200 | NOT reproduced — the authenticated catalog needs a client key (creation blocked, below). These are connectivity probes in any case, never acceptance |
> | `pc-lane.sh` role mapping "left as a proposal pending verification" | SUPERSEDED: the mapping is COMMITTED on the branch and is a superset (`contract-runner` → sweep). Focused tests 33/33 twice; the full harness suite (`harness-ports/tests/run-all.sh`) ALL SUITES PASSED in the sandbox — the "unrelated red suites" Codex saw were PC-host artefacts (AF-AP-11 class), not code |
> | env-file layering (not in the handoff) | ADDED: the managed unit loads `~/.omniroute-migrated/.env` FIRST, then `~/omniroute-migration-20260829/candidate-home/.omniroute/.env` (the unit's `HOME`), then the npm package `.env`. `~/.omniroute/.env` is NOT read by the managed unit — it was the orphan's file |
> | **SECURITY FINDING (new)** | the first-loaded env file sets `REQUIRE_API_KEY=false` and the unit binds `OMNIROUTE_SERVER_HOST=0.0.0.0`: `POST {}` to `/v1/chat/completions` and `/v1/responses` with NO key, and with a bogus key, returns 400 (body validation) — there is no auth gate on the inference plane. firewalld's default zone opens `1025-65535/tcp`; the host has a LAN address (`192.168.40.12/24`) besides Tailscale. Every device on the owner's WiFi can bill the owner's providers. Owner decision (task #34): `REQUIRE_API_KEY=true` in `~/.omniroute-migrated/.env` and/or bind the Tailscale address, then restart. The coordinator changed nothing |
> | **Hermes client key (new finding)** | the `OMNIROUTE_API_KEY` in `~/.hermes/profiles/agentfactory/.env` and the inline `api_key` in both `config.yaml` files are one value whose 12-char prefix matches NO row of the authoritative `api_keys` table (one row: `hermes`, prefix `sk-3c3c93f39`, active, scopes `["self:usage"]`); `/v1/models` answers `401` to it, and a bogus key behaves identically on `/v1/chat/completions` (400 = body validation). The owner's Hermes works ONLY because `REQUIRE_API_KEY=false`. Before `REQUIRE_API_KEY=true` can be enabled (task #34) the owner must regenerate the `hermes` key in the dashboard (reveal is disabled: `ALLOW_API_KEY_REVEAL=false`) and put it in the lane `.env` + both `config.yaml` files |
> | Hermes transport | DEVIATION from ADR 0002 / `docs/03_INTEGRATION_CONTRACTS.md` §2 (`api_mode: codex_responses`, `x-omniroute-compression: off`): both repaired profiles use `chat_completions`. Owner decision (task #35): amend the ADR or revert the transport. The pinned S0-01 Hermes (0.21.0) supports both modes and per-provider `extra_headers` |
> | `STORAGE_ENCRYPTION_KEY` | leaked into the coordinator's session transcript on 2026-09-04 (AF-AP-35); the same value sits in all three env files; 29 of the 32 provider connections (6 OAuth, 4 cookie sessions, 19 API keys) are `enc:v1:` under it. OmniRoute 3.8.50 has NO in-app re-encryption to a new secret (`encryption.ts` derives one key; `STORAGE_ENCRYPTION_KEY_VERSION` is read by no code; the only decrypt path is the local-only `omniroute auth export`, with no import). Client keys are stored hashed + as a plaintext column, so the rotation forces no client-key reissue. Owner-run procedure below (task #33) |
> | combo chain orders | CHANGED on 2026-09-05 relative to the committed `pc-lane.sh` comment and `docs/WORKFLOW-OFFLOAD-MAP.md` (K3 promoted; `deepseek-v4-flash` removed) — both synced in the increment that commits this file |
>
> **Remaining-actions ledger (the numbered list at the end of the handoff):** 1 DONE · 2 DONE (the
> mapping is committed, a superset) · 3 DONE (33/33 ×2; ALL SUITES PASSED) · 4+5 DONE as
> `scripts/omniroute_invariants.sh` (read-only, never remediates; seven named checks incl. the
> listener's own `DATA_DIR` and `REQUIRE_API_KEY=true`; deterministic tests in
> `tests/test_omniroute_invariants.py`, negative controls per check). Live run 2026-09-05 over the
> bridge: `listener` `cgroup` `data_dir_environ` `data_dir_unit` `health` OK; `require_api_key`
> FAIL (the finding above); `catalog` FAIL (no key file yet) — an honest red, not a green ·
> 6 OWNER-ONLY (Web2API needs the owner's authenticated cookies) · 7 OWNER-ONLY (Google Cloud
> console) · 8 = the S0-01 build/verify lanes once the client key exists; research and sweep
> lanes remain UNMEASURED · 9 DONE (`docs/INCIDENT-LOG.md` 2026-09-05 entry; registry row AF-AP-33).
>
> **Client key: use the one Hermes already uses (owner ruling 2026-09-05).** The earlier "create a
> new scoped S0-01 key" directive was issued while every key returned `401 AUTH_002`; the cause was the
> orphan instance serving a database without the owner's key, not the key. With the managed instance back
> the owner's existing key works (`hermes` → `ping`/`pong`), OmniRoute's model is one client key for many
> models, and the S0-01 proof reads that same key from the owner's Hermes config at launch — never copied
> into the repo, printed, or passed in argv. The sandbox classifier had blocked the coordinator's
> management-API login twice; that route is dropped, not worked around. `scripts/omniroute_invariants.sh`
> takes the same key via `OMNIROUTE_API_KEY_FILE`.
>
> **`STORAGE_ENCRYPTION_KEY` rotation (owner-run; the coordinator will not touch the owner's
> service):** (1) `omniroute backup`; (2) `omniroute auth export --format env --out <0600 file>` on
> the PC only (plaintext — shred it at the end); (3) stop `omniroute-migrated.service`; (4) write
> the new key (`openssl rand -base64 32`) into BOTH loaded files, `~/.omniroute-migrated/.env` and
> `…/candidate-home/.omniroute/.env` (and retire `~/.omniroute/.env`, which nothing managed reads);
> (5) start the unit — every `enc:v1:` credential now fails to decrypt LOUDLY by design; (6) re-add
> the 19 API-key connections from the export, re-run OAuth for `codex`, `agy`, `antigravity`,
> `kimi-coding`, re-establish the 4 cookie sessions; (7) run `scripts/omniroute_invariants.sh` and one
> real request per `agentfactory-*` combo; (8) shred the export. Do NOT overwrite the key in place
> without the export: step 5 would make all 29 records unreadable.
>
> ---
>
# OmniRoute and Hermes Fedora Handoff

**Status:** Verified live on 2026-09-05. This document records the laptop-to-Fedora migration, Agent Factory routing configuration, incident recovery, verification evidence, and remaining work. It contains no credentials.

## Objective

Run OmniRoute on the Fedora PC and expose it to the laptop through Tailscale. Hermes on both machines must use OmniRoute as its sole model egress. Agent Factory uses Fable5 for orchestration, seed creation, contracts, and final validation while specialized Hermes PC lanes perform implementation, independent verification, research, and mechanical sweeps.

## Live topology

```text
Laptop Hermes / messaging gateways
             |
             | Tailscale: http://100.64.254.33:20128/v1
             v
Fedora omniroute-migrated.service
             |
             +-- paid Codex connections
             +-- Gemini API-key connections
             +-- Gemini/Antigravity OAuth connections
             +-- authenticated Ollama Cloud connection
             +-- free fallback combinations

Buzz on Fedora: http://100.64.254.33:3001
```

Fedora's local OmniRoute endpoint is `http://127.0.0.1:20128/v1`. Remote laptop clients use the Fedora Tailscale IP. Do not configure Hermes to call providers directly.

## Authoritative Fedora state

- systemd unit: `omniroute-migrated.service`
- executable: `/home/rocco/.omniroute-migration-npm/node_modules/.bin/omniroute`
- authoritative data directory: `/home/rocco/.omniroute-migrated`
- authoritative database: `/home/rocco/.omniroute-migrated/storage.sqlite`
- persistent systemd override: `~/.config/systemd/user/omniroute-migrated.service.d/10-data-dir.conf`
- required override value: `Environment=DATA_DIR=/home/rocco/.omniroute-migrated`

Do not treat `/home/rocco/.omniroute/storage.sqlite` as authoritative. It is a smaller default database accidentally opened by an unmanaged process. Do not restore the pre-combo backup over the current database.

## Repairs completed

### Hermes provider identity

Fedora's default Hermes profile and the Agent Factory profile previously used a bare `provider: custom`. Hermes silently resolved that configuration to OpenRouter. Both profiles were changed to a named custom provider, `custom:omniroute-fedora`, pointing to Fedora OmniRoute and using `chat_completions` transport with model discovery enabled.

The Fedora Hermes model picker used 1.5-second and 5-second discovery timeouts. OmniRoute's large catalog regularly needs longer, which made Hermes display only one model. The discovery paths in `~/.hermes/hermes-agent/hermes_cli/model_switch.py` were raised to 30 seconds and the file was syntax-checked.

### Messaging and supporting services

Laptop Signal and primary Hermes session URLs were changed from localhost to Fedora. The Musa WhatsApp profile was also pointed to Fedora. Signal, both Hermes gateways, WhatsApp health, Buzz health, OmniRoute, the Gemini Web2API bridge, and the xKiro bridge were observed active during migration checks.

Buzz's `/health` endpoint is the correct probe. A 404 from Buzz `/` is not an outage.

### Agent Factory lane routing

`harness-ports/bin/pc-lane.sh` was prepared to map roles as follows:

| Role | Combo | Default effort |
|---|---|---|
| `code-implementer` | `agentfactory-build` | `ultra` |
| `adversarial-verifier` | `agentfactory-verify` | `xhigh` |
| `researcher`, `evidence-gatherer` | `agentfactory-research` | `high` |
| `curator`, `echo-sweeper` | `agentfactory-sweep` | `medium` |
| other/default | `agentfactory-build` | `ultra` |

Focused behavioral tests passed twice at 24/24. At that time the full harness suite still had unrelated existing failures in Codex hook adapter, Hermes hook adapter, and Hermes spool tests, so the lane mapping was left as a proposal pending the repository's required independent sandbox verification. Re-check the current branch rather than assuming those uncommitted edits still exist.

## Current routing combinations

All combinations use priority ordering. Paid or authenticated routes precede free combination references.

### `agentfactory-build`

1. `codex/gpt-5.6-sol-ultra`
2. `ollama-cloud/kimi-k3`
3. `codex/gpt-5.6-sol-xhigh`
4. `codex/gpt-5.6-terra-ultra`
5. `codex/gpt-5.5-xhigh`
6. `ollama-cloud/glm-5.2`
7. combo reference `free-coding`

### `agentfactory-verify`

1. `codex/gpt-5.6-terra-xhigh`
2. `ollama-cloud/kimi-k3`
3. `ollama-cloud/glm-5.2`
4. `agy/gemini-3.1-pro-low`
5. `antigravity/gemini-3.1-pro-low`
6. `codex/gpt-5.5-xhigh`
7. combo reference `free-reasoning`

### `agentfactory-research`

1. `ollama-cloud/kimi-k3`
2. `gemini/gemini-3.1-pro-preview`
3. `ollama-cloud/glm-5.2`
4. `agy/gemini-3.1-pro-low`
5. `antigravity/gemini-3.1-pro-low`
6. `gemini/gemini-3-flash-preview`
7. combo reference `free-chat`

### `agentfactory-sweep`

1. `ollama-cloud/kimi-k3`
2. `gemini/gemini-3-flash-preview`
3. `agy/gemini-3-flash-agent`
4. `antigravity/gemini-3-flash-agent`
5. combo reference `free-fast`

`ollama-cloud/deepseek-v4-flash` had successful historical laptop calls but is no longer present in Ollama Cloud's active live catalog. A Fedora direct probe returned 400, so it was removed from `agentfactory-sweep` rather than leaving a known-dead route.

## Verification evidence

After recovering the correct managed instance on 2026-09-05:

- `/api/health`: HTTP 200.
- live authenticated catalog: 2,626 entries.
- all four `agentfactory-*` combinations appeared in `/v1/models`.
- `ollama-cloud/kimi-k3`: HTTP 200 direct inference.
- `ollama-cloud/glm-5.2`: HTTP 200 direct inference.
- `ollama-cloud/deepseek-v4-flash`: HTTP 400 because it is absent from the active live catalog; removed from routing.
- `agentfactory-build`: HTTP 200.
- `agentfactory-verify`: HTTP 200.
- `agentfactory-research`: HTTP 200.
- `agentfactory-sweep`: HTTP 200, then updated to replace the unavailable DeepSeek step with verified K3.

Earlier creation probes also demonstrated successful paid/provider failover through Codex, Antigravity, and direct Gemini routes. These small probes prove connectivity and route selection, not workflow quality or acceptance-gate correctness.

## September 5 outage: root cause and permanent repair

Symptoms:

- OmniRoute appeared down from Hermes.
- `/api/health` still returned 200.
- catalog fell from thousands of entries to roughly 622.
- all `agentfactory-*` combinations disappeared.
- Ollama Cloud reported no active credentials.

Root cause:

1. An unmanaged OmniRoute process from an old interactive shell was already listening on port 20128.
2. It ran with `HOME=/home/rocco` and served the small default `~/.omniroute` database.
3. `omniroute-migrated.service` repeatedly failed with `EADDRINUSE`, even though systemd transiently reported it active during its restart loop.
4. The correct `~/.omniroute-migrated/storage.sqlite` remained intact throughout.

Repair:

1. Added the explicit systemd `DATA_DIR` override.
2. Identified the exact unmanaged listener and its old session cgroup.
3. Sent `SIGTERM` only to that duplicate OmniRoute PID.
4. Allowed `omniroute-migrated.service` to reclaim port 20128.
5. Verified the restored catalog, combinations, credentials, and live inference.

## Recovery runbook

Run these on Fedora. Never kill a PID until its command and cgroup have been inspected.

```bash
systemctl --user is-active omniroute-migrated.service
systemctl --user show -p MainPID -p Environment omniroute-migrated.service
ss -lntp 'sport = :20128'
pgrep -af 'omniroute.*serve|next-server'
journalctl --user -u omniroute-migrated.service --since '20 minutes ago' --no-pager
```

Expected invariants:

- exactly one OmniRoute listener owns port 20128;
- its process belongs to `omniroute-migrated.service`, not an interactive `session-*.scope`;
- the service environment contains `DATA_DIR=/home/rocco/.omniroute-migrated`;
- health returns 200;
- the authenticated catalog includes the four Agent Factory combinations and `ollama-cloud/kimi-k3`.

If `EADDRINUSE` appears:

1. Resolve the listener PID with `ss`.
2. Inspect it with `ps -o pid,ppid,lstart,cmd -p PID` and `cat /proc/PID/cgroup`.
3. If and only if it is an unmanaged duplicate in an interactive session, terminate that exact PID with `kill -TERM PID`.
4. Restart `omniroute-migrated.service` and repeat every invariant check.

Do not use broad `pkill`, do not delete either database, and do not copy the small default database over the migrated database.

## Backups retained

Important Fedora backups include:

- `~/.omniroute-migrated/storage.sqlite.bak-before-agentfactory-combos-20260903`
- `~/.omniroute-migrated/storage.sqlite.bak-before-ollama-combos-20260905`
- Hermes configuration backups made before named-provider migration
- `~/.hermes/hermes-agent/hermes_cli/model_switch.py.bak-before-omniroute-timeout-20260903`

The September 3 pre-combo backup intentionally lacks the Agent Factory combinations. Prefer the September 5 backup if reverting only the Ollama combo edits.

## Gemini rate limits

Two Google AI Studio keys were migrated and the second healthy record was enabled. Gemini API rate limits apply per Google Cloud project, not per API key. Keys in the same project share quota. A Google AI Pro consumer subscription is also distinct from Gemini API paid billing. Preview models have tighter limits. This is why two keys can still receive 429 responses.

K3 is now ahead of Gemini in research and sweep so those workflows are not dependent on Gemini availability. Gemini remains a downstream fallback/search-capable route.

## Web-token and Web2API status

The migration contains numerous authenticated provider connections, including web-session/token connections. Their presence must not be equated with current health; validate each with a real minimal call.

The Gemini Web2API service was running, and its model-list endpoint responded, but generation lacked usable authenticated cookies/XSRF state and hung during testing. It is not a proven backup until a real generation request succeeds. Do not describe it as operational based only on service health or `/v1/models`.

## Skills and hooks

Agent Factory already contains the battle-tested portability work:

- `.agents/skills/`
- `.codex/`
- `.hermes.md`
- `harness-ports/` role definitions, briefs, hooks, MCP configuration, and tests

Do not wholesale-copy the laptop Codex or Claude configuration into Hermes. Many hooks and mechanisms are runtime-specific. Port only a demonstrated missing behavior, map it to a native Hermes mechanism, add deterministic tests, and preserve the project's no-hollow-green rules.

## Remaining actions for Fable

1. Read this file together with `AGENTS.md`, `.hermes.md`, `docs/WORKFLOW-OFFLOAD-MAP.md`, and `docs/HANDOFF-HERMES-LANES.md`.
2. Confirm the current branch still contains or intentionally supersedes the `pc-lane.sh` role mapping proposal.
3. Run the focused PC-lane tests twice and then the full harness suite. Do not self-accept unrelated red suites.
4. Add deterministic monitoring that fails when port 20128 is owned outside `omniroute-migrated.service`, or when the catalog lacks the four required combos.
5. Add a regression test or service assertion for the explicit authoritative `DATA_DIR`.
6. Reauthenticate and live-test Web2API before adding it as a fallback.
7. Validate the two Google keys' Cloud project identities and billing tiers without logging the keys.
8. Run representative real Agent Factory build, verify, research, and sweep workloads. The connectivity probes in this document are not final workflow validation.
9. Record the duplicate-process/data-directory incident in `docs/INCIDENT-LOG.md` using the repository's bug-echo convention.

All code or configuration proposals still require the repository's contract gate and independent adversarial verification lane. This document is an operational handoff, not an acceptance verdict.
