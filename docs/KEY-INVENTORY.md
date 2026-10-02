# Key inventory: names and places, never values

Owner ruling D-130 (2026-10-02 00:4xZ): nothing runs in production yet, so every key below is a
test key. Before the first sim-prod or production launch, every key gets a fresh value at once
(task #461). Until then a known exposure is recorded here. It is not a reason to hold work, and the
history is not rewritten.

This page holds no value, no prefix and no piece of any key: only names, places, readers and
exposures. A key's display prefix is part of the key (AF-AP-257), and no key character goes into a
file, a command or a message (AF-AP-39).

Last checked 2026-10-02 00:5xZ, from the repo's own code and docs: a sweep for key files, key
variables and credential paths over `scripts/`, `harness-ports/`, `deploy/`, `proofs/`, `src/`,
`docs/` and `PC-BRIDGE.md`. No secret file on the PC or in the sandbox was opened for this page.

## Keep it current

- Add an entry the day a new key appears: any code, config or service that reads a secret.
- Record an exposure the day it is found: which key, where, since when. Never its characters.
- At launch, work through "Rotate before launch" in order, and date each line.

## The keys

### 1. OmniRoute client key `hermes`

- **Lives in (PC):** `~/.hermes/profiles/agentfactory/.env` (`OMNIROUTE_API_KEY`); the inline
  `api_key` in the Hermes `config.yaml` files of the PC's and the laptop's profiles;
  `~/.config/qwen-jev/omniroute.key` (the same value); `~/s0-01-pinned/.hermes-home/.env`;
  OmniRoute's `api_keys` table (hashed). Check the cloned lane profiles
  (`~/.hermes/profiles/aflane*/`, D-049) and any Buzz config built from
  `docs/LOCAL-MODEL-GUIDE.md` (`OPENAI_COMPAT_API_KEY`) for copies.
- **Read by:** Hermes (the owner's sessions and every PC lane); `proofs/S0-03/tools/pc/run_s0_03_legs.sh`
  (`S0_03_KEY_FILE`); `proofs/S0-01/tools/pc/pc_post.sh`; `scripts/omniroute_invariants.sh`
  (`OMNIROUTE_API_KEY_FILE`); the qwen-jev transport probe.
- **Unlocks:** every model behind OmniRoute on `:20128`, billed to the owner's provider accounts.
- **Exposures:** its first 12 characters (OmniRoute's display prefix) sit in 3 blobs of the public
  repo's history, in both PC session exports and in session transcripts (AF-AP-257, found
  2026-10-01). The key was rotated once, on 2026-09-05.
- **Rotate:** regenerate it in the OmniRoute dashboard (reveal is off: `ALLOW_API_KEY_REVEAL=false`),
  then write the new value into every place above.

### 2. OmniRoute storage key (`STORAGE_ENCRYPTION_KEY`)

- **Lives in (PC):** `~/.omniroute-migrated/.env` and
  `~/omniroute-migration-20260829/candidate-home/.omniroute/.env` (both loaded by
  `omniroute-migrated.service`); `~/.omniroute/.env` (the old orphan's file; nothing managed reads it).
- **Read by:** OmniRoute.
- **Unlocks:** 29 of OmniRoute's 32 stored provider connections are encrypted with it.
- **Exposures:** in a session transcript since 2026-09-04 (AF-AP-35). The owner kept it on 2026-09-05.
- **Rotate:** the owner-run procedure in `docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md`
  ("`STORAGE_ENCRYPTION_KEY` rotation", task #33): back up, export the connections, write the new key
  into both loaded files, start, re-add the connections, re-run each OAuth, re-establish the cookie
  sessions. OmniRoute cannot re-encrypt in place.

### 3. OmniRoute's provider connections (the upstream accounts)

- **Lives in (PC):** OmniRoute's database, encrypted with key 2.
- **Read by:** OmniRoute only. No project code holds a provider key (standing rule 3).
- **Unlocks:** the owner's accounts at each provider: OAuth for `codex`, `agy`, `antigravity` and
  `kimi-coding`, 4 cookie sessions and 19 API keys (counted 2026-09-05).
- **Exposures:** none recorded.
- **Rotate:** the owner re-issues each one at its provider, then re-adds it in OmniRoute (key 2's
  procedure, step 6).

### 4. OmniRoute dashboard login

- **Lives in:** with the owner.
- **Read by:** the owner only; the coordinator never uses it (`PC-BRIDGE.md`).
- **Unlocks:** OmniRoute's management plane: client keys, routes, connections.
- **Exposures:** none recorded.
- **Rotate:** the owner.

### 5. Local model server key (vLLM `qwen`; SGLang after task #454)

- **Lives in (PC):** `~/.config/qwen-builder/api-key` (0600 in a 0700 directory), mounted read-only
  into the `qwen` container as `/app/api_key.txt` (`deploy/qwen.container`); OmniRoute's connection
  for the local route (OmniRoute calls `:8080` with it).
- **Read by:** the model server; OmniRoute; `harness-ports/bin/qwen-server.sh`; `scripts/qwen_jev.py`
  (`QWEN_JEV_KEY_FILE` overrides the path); `scripts/gpu_side_by_side.sh` (`VLLM_API_KEY`); the
  SGLang A/B harness (task #454).
- **Unlocks:** the local model on `:8080`.
- **Exposures:** none found: 0 windows over the tree, the history and both exports (the PC-side
  check, 2026-10-01).
- **Rotate:** write the new value into the file and into OmniRoute's local connection, then restart
  the server in a GPU window.

### 6. PC bridge token

- **Lives in:** PC: `~/.agent_token` (beside `~/.agent_url`). Sandbox: `.pc-bridge.env`
  (`PC_BRIDGE_TOKEN`; untracked and ignored).
- **Read by:** `scripts/pc.sh`, `scripts/pc_lane.sh`, `scripts/pc_suite.sh`, `scripts/ship_to_pc.py`,
  `scripts/pc_fetch.sh`.
- **Unlocks:** a shell on the PC as the owner's user.
- **Exposures:** every banner is pasted into the chat, so the session transcripts hold every token
  used.
- **Rotate:** a new bridge launch mints a new URL and token (`PC-BRIDGE.md`). At launch, restart the
  bridge or retire it.

### 7. codiv relay key

- **Lives in (sandbox):** `/root/.codiv/api.env` (`TYPESAFE_API_KEY`, beside `TYPESAFE_BASE_URL`).
  The fast-jev-output plugin keeps its own copy in its installed config (never read; our copy of the
  plugin carries a placeholder and goes through the relay).
- **Read by:** `scripts/jev_relay.py` (the relay on `:47430` injects the key);
  `docs/research/findings/j2b-variants/openjev_j2.py`.
- **Unlocks:** api.codiv.ai (the OpenJev calls), billed to the owner.
- **Exposures:** the owner pasted it into the chat, so the session transcripts hold it; an export
  with 11 of its characters was deleted on 2026-10-01.
- **Rotate:** at codiv.ai; write the new value into `api.env` (the relay re-reads its source);
  replace the plugin's stored copy through the `claude plugin` CLI.

### 8. Session-export pseudonym key

- **Lives in (sandbox):** `/root/.config/session-export/pseudonym.key`.
- **Read by:** `scripts/session_export.py`, `scripts/transcript_export.py`.
- **Unlocks:** nothing by itself; it ties the pseudonyms in every export to the names behind them.
- **Exposures:** none recorded.
- **Rotate:** a new key changes every pseudonym, so re-export after it.

### 9. Buzz test identities (Stage 0 proofs)

- **Lives in (PC):** `/home/rocco/s0-01-pinned/.secrets/<role>.env` for `owner`, `agent`, `user2`
  and `nonmember` (`BUZZ_PRIVATE_KEY`, 0600); the S0-05 pair identity in the file
  `S0_05_PAIR_IDENTITY` names (`~/s0-05-identity/pair.env`). The public halves are committed in
  `proofs/S0-02/fixtures/PROVENANCE.md`.
- **Read by:** the S0-01, S0-02 and S0-05 runners.
- **Unlocks:** posting as that identity on the Buzz relay.
- **Exposures:** none recorded.
- **Rotate:** new identities change the committed public halves and the proofs' fixtures, so make
  them with the proofs, or retire them with Stage 0.

### 10. S0-01 scripted backend token

- **Lives in (PC):** `/home/rocco/s0-01-pinned/.secrets/scripted-upstream.env` (`UPSTREAM_TOKEN`).
- **Read by:** `proofs/S0-01/tools/scripted_backend.py`, `proofs/S0-01/tools/pc/pc_post.sh`.
- **Unlocks:** the scripted test backend on `:20201` (test only).
- **Exposures:** none recorded.
- **Rotate:** with the proof, as key 9.

### 11. ai-memory token (S0-06)

- **Lives in (PC):** made for each run as `<run dir>/token` by
  `proofs/S0-06/tools/pc/start_ai_memory.sh`.
- **Unlocks:** that run's ai-memory server only.
- **Rotate:** nothing to do; each run makes a new one.

### 12. OpenObserve root login

- **Lives in (PC):** the OpenObserve container's `ZO_ROOT_USER_PASSWORD` (the authority) and any
  credentials file copied from it (`docs/OBSERVABILITY-RUNBOOK.md`).
- **Read by:** nothing in the project yet: no component ships telemetry.
- **Unlocks:** the telemetry store.
- **Exposures:** none recorded.
- **Rotate:** the owner; a recreated container makes every copy stale.

### 13. The owner's signing key

- **Lives in:** with the owner; the public half is committed at `docs/governance/owner-signing-key.asc`.
- **Read by:** `scripts/check-proof-status.py` (it checks the signed `accepted/S0-xx` tags).
- **Unlocks:** the acceptance of a proof.
- **Exposures:** none recorded.
- **Rotate:** the owner decides: a new key means a new committed public half and re-signed tags.

### 14. GitHub token

- **Lives in (sandbox):** the harness's environment.
- **Read by:** the harness's git and GitHub tools.
- **Unlocks:** the repositories this session can reach.
- **Rotate:** through the claude.ai GitHub connection, not in this project.

### Not recorded in this repo

The PC also runs neo4j, Phoenix and the Buzz relay stack. No project code reads a credential of
theirs today. Add an entry when one does.

## Rotate before launch (D-130, task #461)

Work in this order: a key that protects another key goes with it.

1. OmniRoute's storage key and provider connections together (keys 2 and 3), by the owner-run
   procedure.
2. The OmniRoute client key (key 1), into every place it lives.
3. The local model server key (key 5), and OmniRoute's local connection.
4. The codiv key (key 7).
5. The bridge token (key 6): a fresh bridge launch.
6. The pseudonym key (key 8), then a re-export.
7. The test identities and tokens (keys 9 and 10): make new ones with their proofs, or retire them.
8. The owner's signing key (key 13): the owner decides.

Then check each one: a request through each client with the new value (Hermes, a PC lane, the
relay); a request with the old value, which must get 401; `scripts/omniroute_invariants.sh`; and the
PC-side known-values check (task #456) over the tree, the history and every export, with the new
values.
