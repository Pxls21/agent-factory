# T92 — the per-lane cloned Hermes profile: NO fallback chain (D-048), the `x-omniroute-session-id` header = the lane id, the harvest keyed on it (AF-AP-118; VERIFY-T90-R2 F5)

PIN: 879c6f9 (origin head; the tree you start from — it carries T90-R3's dispatcher).
LANE: pc-t92
ROLE: code-implementer (build) — the local route (`HERMES_MODEL=qwen-local/qwen3.8-27b-local`). You may be re-routed by the very chain you are removing (AF-AP-118); nothing to do about it, the harvest measures it.
COMPONENT (boundary, nothing else): NEW `harness-ports/bin/lane-profile.sh` · `harness-ports/bin/pc-lane.sh` (ONE block: create-or-reuse the lane profile before the launch at :430 and pass `-p <lane profile>`; the profile name into `usage.json`'s neighbourhood / the transcript footer) · `scripts/pc_lane.sh` (the provider-mix query at :448-475: key on `session_tag = '<lane id>'` first, `requested_model` for untagged raw-id rows second, never `combo_name` alone; read `usage.json`'s `model` into the harvest line as `served=<model>`) · NEW `harness-ports/tests/test_lane_profile.sh` · `harness-ports/tests/test_pc_lane_dispatcher.sh` (the mix-SQL shape checks) · `harness-ports/tests/run-all.sh` (register the new test) · ONE section in `docs/HARNESS-PORTS.md`. NEVER edit `~/.hermes/profiles/agentfactory/` (the owner's interactive profile: read it, clone it, never change it); NEVER print, grep, cat or paste any `.env` content (AF-AP-39: copy with `cp -p`, compare with `sha256sum`, name keys only if you must); never stop or restart any server; never touch a live lane's profile. Do NOT commit, do NOT push.
AUTHORIZATION: the owner's PC; user-scope files under `~/.hermes/profiles/` only; D-048 (owner 2026-09-22 22:0xZ, "go with what you recommend 2") authorizes the per-lane clone WITHOUT `fallback_providers`.
BUDGET: one build round; report DATA, not prose; every count and diff pasted.

## Why (measured 2026-09-22; the ledger's VERIFY-K1-g HOME and VERIFY-T90-R2 HOME notes)
The `agentfactory` profile's config.yaml carries `fallback_providers` (three cloud codex models through OmniRoute, lines 7-18 below). Hermes itself requests those models after a local 504/499/400, so a "strict raw id" lane is HYBRID in practice (16:02-20:35Z: 301 local rows against 278 cloud rows on the `hermes` key; three lane closes bound to a `499 Request aborted` on the fallback model seconds after `ended_at`). The dispatcher's mix line keys on `combo_name` and is blind to raw-id lanes (VERIFY-T90-R2 F5: 348 direct raw-id rows, 0 matches). `call_logs.session_tag` carries OmniRoute's own `conv_…` tags when no header is sent (401 of 401 rows in the last three hours).

## Build (in this order; each step's output pasted into the report)
0. **PREMISE CHECKS FIRST — stop and report BLOCKED with the evidence if one fails:**
   (a) the installed Hermes runtime (v0.21.1, upstream b3399c1) can send a per-request header to its OpenAI-compatible provider: locate the package (`hermes` is a bash wrapper — read its venv path from the wrapper, then `<venv>/bin/python -c 'import hermes, os; print(os.path.dirname(hermes.__file__))'` or the equivalent module name) and paste the grep for `extra_headers` / `default_headers` / `headers` in its provider client and config loader (ADR 0002 claims per-provider extra_headers). If the runtime has NO way to add a request header from config, the session-tag half of this lane is BLOCKED: report it with the grep, still land the no-fallback half (steps 1-2 without the header, 3 with `requested_model` keying only).
   (b) how OmniRoute turns the header into `call_logs.session_tag`: one source line (path:line) from `/home/rocco/.omniroute-migrated` (grep `x-omniroute-session-id` case-insensitively across every extension — the `*.js`-only grep found 0 files while the whole tree mentions it 1,322 times); paste it.
   (c) `hermes profile create --clone-from agentfactory <name>` semantics on a throwaway `t92probe` (lowercase alphanumeric per the help): paste the file list of the clone, the `sha256sum` of the clone's `.env` against the source's (equal or not — shas only), whether `hooks/` and `cron` came along; then `hermes profile delete t92probe`.
1. **`harness-ports/bin/lane-profile.sh create|verify|remove <lane-id>`**: the profile name = `aflane<lane-id lower-cased, non-alphanumerics dropped, truncated to 40>` (paste the name rule's three examples). `create` = `hermes profile create --clone-from agentfactory --no-alias <name>` (add what 0c showed missing — `hooks/`, `cron` — by `cp -a`), then ONE deterministic Python step over the clone's `config.yaml`: delete the top-level `fallback_providers` key; add the request header `x-omniroute-session-id: <lane-id>` in the form 0a proved; nothing else changes (assert with a key-set diff). Idempotent: an existing verified clone is reused. `verify` = exit 0 only if the clone's config has NO `fallback_providers`, HAS the header with the exact lane id, and its `.env` sha256 equals the source's; exact one-line reasons otherwise (`lane-profile: chain present` / `lane-profile: header missing or wrong: <got>` / `lane-profile: env drift`). `remove` = `hermes profile delete <name>` — REFUSE any name without the `aflane` prefix (`lane-profile: refusing to delete non-lane profile <name>`, rc 64), tested.
2. **`harness-ports/bin/pc-lane.sh`**: before the launch (:430) run `lane-profile.sh create "$LANE_ID"` and `verify`, then launch with `-p "$LANE_PROFILE"`; an explicit `HERMES_PROFILE` in the environment overrides (the escape hatch, logged as `pc-lane: profile override <name>`); the profile name written next to `usage.json` (`profile.txt`) and into the transcript footer. Live lanes are unaffected (they hold their processes); only new launches change.
3. **`scripts/pc_lane.sh` provider mix**: the shipped read-only SQL keys on `session_tag = '<lane id>'` (single-quote-escaped) and reports `requested_model × provider × status × count`; a second aggregate counts the window's raw-id rows WITHOUT the tag as `untagged-raw-rows=N` (the pre-T92 blindness stays visible); the harvest line gains `served=<usage.json model>`; the combo-window caveat stays for combo lanes. Keep the lane's SQL escaping test shape.
4. **Tests**: `harness-ports/tests/test_lane_profile.sh` (a fake `hermes` on PATH that materialises a fixture clone + a fixture source profile dir: create strips the chain and adds the header; verify RED on a chain present, a wrong lane id, a changed .env sha — exact messages; remove refuses a non-`aflane` name; the name rule's examples); the dispatcher test's mix checks (the shipped SQL contains `session_tag = '<id>'`, never `combo_name = '<raw id>'` for a raw-id lane; `served=` in the harvest line); `run-all.sh` registers the new test.
5. **LIVE proof on the PC (paste)**: one throwaway lane profile created from the REAL source with a made-up lane id; `verify` exit 0; `diff` of the clone's config against the source with any `key`/`api_key`/`key_env` value redacted — exactly the two intended changes; one `hermes -p <clone> -z 'reply with the single word PONG'` on the local route; then the read-only `call_logs` row of that call (`session_tag`, `requested_model`, `provider`, `status`) — the tag MUST equal the lane id; then `remove`. The servers stay untouched; the one-shot runs while other lanes run (it is one request).

## Gates (paste verbatim)
`bash -n` on every shell file; `bash harness-ports/tests/test_lane_profile.sh` twice; `bash harness-ports/tests/test_pc_lane_dispatcher.sh` twice (bitwise; the PIN reads `38 passed, 0 failed`); `bash harness-ports/tests/run-all.sh` → `ALL SUITES PASSED`; `python3 scripts/ap_screen.py --tests harness-ports/bin/lane-profile.sh harness-ports/bin/pc-lane.sh scripts/pc_lane.sh harness-ports/tests/test_lane_profile.sh`; `python3 scripts/no_laya_in_gates.py` rc 0. Mutants (scratch copy, the killing test NAMED): m1 the chain strip dropped → verify red; m2 the header carries the profile name instead of the lane id → verify red; m3 remove accepts any name → the refusal test red; m4 the mix keys on `combo_name` again → the dispatcher SQL check red. Every gate call under the 420 s cap.

## Report (`tasks/briefs/pc-t90-support/T92-report.md`)
DATA: files:lines, the premise checks' pasted outputs, the RED→GREEN pairs, the four mutant rows, the live proof's redacted diff + the call_logs row, DISCREPANCIES / NOT-done (if 0a blocked the header half, say so first). `python3 scripts/report_lint.py --min-refs 12 tasks/briefs/pc-t90-support/T92-report.md --root .` (≤ 3 fix rounds, then paste and finish).

## PREMISE — MEASURED at authoring (2026-09-22T22:04:03Z; the PC over the bridge + the sandbox tree; read-only, values redacted)
```
$ hermes profile create --help | sed -n 1,18p
usage: hermes profile create [-h] [--clone] [--clone-all]
                             [--clone-from SOURCE] [--no-alias] [--no-skills]
                             [--description DESCRIPTION]
                             profile_name
positional arguments:
  profile_name          Profile name (lowercase, alphanumeric)
options:
  -h, --help            show this help message and exit
  --clone               Copy config.yaml, .env, SOUL.md, and skills from
                        active profile
  --clone-all           Full copy of active profile (all state, excluding per-
                        profile history)
  --clone-from SOURCE   Source profile to clone from; implies --clone unless
                        --clone-all is set
  --no-alias            Skip wrapper script creation
  --no-skills           Create an empty profile with no bundled skills (opts
$ ls -la ~/.hermes/profiles/agentfactory | awk '{print $5, $9}'   (names + sizes only)
0 audio_cache
0 auth.lock
494 cache
7737 config.yaml
7737 config.yaml.bak-20260922T165224Z-t93r1
4969 config.yaml.bak-before-agent-factory-20260903-075644
9610 config.yaml.bak-before-agent-factory-20260915-082226
7707 config.yaml.bak-before-agent-factory-20260915-085310
7709 config.yaml.bak-before-client-auth-20260905
9346 config.yaml.bak-before-omniroute-provider-20260903
729 context_length_cache.yaml
12 cron
23535 .env
23535 .env.bak-before-client-auth-20260905
0 home
8800 hook_outputs
$ awk '/^[A-Za-z_]+:/' config.yaml   (top-level keys only)
model: fallback_providers: agent: terminal: browser: tool_loop_guardrails: compression: prompt_caching: display: stt: memory: delegation: skills: approvals: command_allowlist: plugins: hooks: code_execution: streaming: updates: _config_version: session_reset: group_sessions_per_user: platform_toolsets: mcp_servers: known_plugin_toolsets: known_builtin_toolsets: providers: context_file_max_chars: 
$ sed -n 7,18p config.yaml | sed -E 's/(key|key_env|api_key)[^ ]*:.*/\1: <redacted>/'   (the chain, values redacted)
fallback_providers:
- provider: custom
  model: codex/gpt-5.6-sol-xhigh
  base_url: http://127.0.0.1:20128/v1
  key_env: <redacted>
- provider: custom
  model: codex/gpt-5.6-terra-ultra
  base_url: http://127.0.0.1:20128/v1
  key_env: <redacted>
- provider: custom
  model: codex/gpt-5.5-xhigh
  base_url: http://127.0.0.1:20128/v1
$ grep -c . ~/.hermes/profiles/agentfactory/.env; grep -c '^OMNIROUTE_API_KEY=' .env   (names only; values never read)
411
1
$ grep -rIl 'x-omniroute-session-id' ~/.omniroute-migrated --include=*.js | wc -l
0
$ sqlite3 -readonly call_logs: session_tag shapes, last 3 h
conv_	401
$ hermes --version
Hermes Agent v0.21.1 (2026.9.7) · upstream b3399c13
$ (sandbox @ 64a02e6) grep -n '"$HERMES_BIN" -p' harness-ports/bin/pc-lane.sh
430:  "$HERMES_BIN" -p "${HERMES_PROFILE:-agentfactory}" --in "$TREE" --no-restore-cwd -z "$(cat "$PROMPT_RUN")" \
$ grep -n 'combo_name = \|api_key_name = ' scripts/pc_lane.sh
471:  WHERE api_key_name = 'hermes'
472:    AND combo_name = '$MIX_COMBO_SQL'
$ ls harness-ports/bin/ | grep -c lane-profile   (0 = new file)
0
```
