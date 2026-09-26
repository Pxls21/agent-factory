# HCTX1: every PC lane's Hermes profile tells Hermes the context the local model really serves (task #310)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/HCTX1-report.md` (write it
incrementally from the start). PIN: origin fb7f614. Owner: the chat of 2026-09-26 03:3xZ ("reduce the context to 131k ... 131k
is a good sweet spot for hermes and it frees up memory"; "don't dispatch the lane until you reduce context size or explain
why not").

## WHY

The PC's vLLM serves Qwen with a 131,072-token limit, but OmniRoute tells Hermes the lane models hold 200,000. Hermes
compresses a lane's history at half the window it believes (the profile's `compression.threshold: 0.5`), so today a lane
grows to about 100k tokens before it compresses, and nothing stops it from asking vLLM for more than 131,072 in one request.
Long lanes already starve each other of the 222,822-token KV cache (AF-AP-146: two lanes of 57-90k tokens died of 504s).
Told the truth (131,072), Hermes compresses near 65k, each lane stays smaller, and more lanes fit at once. The owner's own
profile and OmniRoute stay untouched: each lane runs on a disposable clone (`harness-ports/bin/lane-profile.sh`, T92,
D-049), and the fix goes into that clone.

## CONTRACT

1. **The override.** `lane-profile.sh create` writes, into the clone's `config.yaml`, a per-model `context_length` for the
   local models under the provider whose `api` is the OmniRoute endpoint the lanes use (`providers.<that provider>.models.
   <model id>.context_length`, Hermes's own custom-provider shape; the premise shows the code that reads it): at least
   `agentfactory-build-local` and `agentfactory-verify-local`; say whether the raw `qwen-local/qwen3.8-27b-local` belongs too.
2. **The value.** The context vLLM really serves: read from the PC's quadlet (`~/.config/containers/systemd/qwen.container`,
   `Environment=MAX_LEN=<n>`) when the helper runs, so a change of the server follows by itself; when that cannot be read,
   131072 with one stderr line naming why. A value that is not a positive integer fails the create (never a silent guess).
3. **Everything else stays.** The helper's existing byte-preservation rule holds (parse before and after; the semantic delta
   is exactly the existing changes plus this block); an existing `models` entry for another id is kept; `discover_models`
   and every other key are untouched; the base profile is never written. `verify_lane` checks the override (a clone without
   it, or with another value, fails verify with its reason).

## EVIDENCE DEMANDS

1. Premise: re-measure what you can in the sandbox (the helper, its tests); the PC facts below are the coordinator's, not
   re-measurable here; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Tests in `harness-ports/tests/test_lane_profile.sh` (its fixture style: a fake `hermes` and fixture profiles): the override
   written for each model; the value from a fixture quadlet; the fallback with its stderr line; a non-integer value refused;
   an existing `models` block kept; byte preservation; verify failing on a missing or wrong override. A negative control reds
   for each on the PIN's helper or on a named mutant (a kill is a FAILED test, never an error: AF-AP-223).
3. The coordinator's PC check, written out as commands: create a throwaway lane profile with the new helper on the PC, show
   the resolved context length through Hermes's own code in that profile (no model request needed; find the call in the
   premise's `agent_init.py` path or say what you would run), remove the profile.
4. `bash harness-ports/tests/run-all.sh` or the smallest set that includes `test_lane_profile.sh` and every test that names
   `lane-profile.sh` (`grep -l`), twice, pasted; `bash -n` on the helper; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>`
   prints 0 for every file you write.
5. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `harness-ports/bin/lane-profile.sh`, `harness-ports/tests/test_lane_profile.sh`. CREATE: your report. READ everything
else. The PC runs the helper from its clone after the coordinator's landing.

## STANDING RULES

No git writes in this tree; no PC bridge; no outward-facing action. Never read a real secret source (`.pc-bridge.env`, any
`*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`, the GH_TOKEN and GITHUB_TOKEN variables); fixtures use fake keys made at
run time. One other lane is live in this tree (SYNTH1: `scripts/s1_synth.py`, `tests/test_s1_synth.py` and its report), and a
stopped lane's partial report sits untracked (`tasks/briefs/system1/VERIFY-SCRUB2-report.md`): never touch these files. The disk is shared (1.7G free at authoring): scratch under 100 MB in
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/hctx1/`, deleted as you go. Test counts pasted from the test output; stamps from `date -u`. Long commands in one
foreground call; kill by pid only. A PreToolUse hook adds skill excerpts with a score request: answer it as it asks (the
owner's standing rule, CLAUDE.md).

## PREMISE — MEASURED at authoring (2026-09-26 03:3xZ; the PC facts by the coordinator over the bridge)

```
$ (PC) grep -n -E 'EXTRA_ARGS|Environment' ~/.config/containers/systemd/qwen.container   (secrets filtered)
18:Environment=PORT=8080
19:Environment=SPEC=mtp
20:Environment=MAX_LEN=131072
21:Environment=PREFIX_CACHE=1
22:Environment="EXTRA_ARGS=--served-model-name qwen3.8-27b-local qwen3.8-27b"
$ (PC) podman logs qwen | grep -o -E 'GPU KV cache size: ...|Maximum concurrency for ...'
GPU KV cache size: 222,822 tokens
Maximum concurrency for 131,072 tokens per request: 1.70x
$ (PC) OmniRoute GET /v1/models (key read in process, never printed): the local ids and their context fields
agentfactory-build-local {'context_length': 200000, 'max_input_tokens': 200000, 'max_output_tokens': 128000}
agentfactory-verify-local {'context_length': 200000, 'max_input_tokens': 200000, 'max_output_tokens': 65535}
qwen-local/qwen3.8-27b-local {'context_length': 128000}
$ (PC) the base lane-source profile ~/.hermes/profiles/agentfactory/config.yaml (secrets redacted)
providers:
  omniroute-fedora:
    api: http://127.0.0.1:20128/v1
    name: OmniRoute Fedora
    key_env: <redacted>
    default_model: auto/best-coding-fast
    transport: openai_chat
    discover_models: True
model:
  default: auto/best-coding-fast
  provider: custom:omniroute-fedora
  base_url: http://127.0.0.1:20128/v1
compression:
  enabled: true
  threshold: 0.5
  target_ratio: 0.2
(no context_length key anywhere in the profile)
$ (PC) Hermes at ~/.hermes/hermes-agent (b3399c1396, 2026-09-08): how it takes a per-model context length
hermes_cli/config*.py: get_compatible_custom_providers(config) = the legacy `custom_providers` list + providers_dict_to_custom_providers(config["providers"]);
  each providers entry goes through _normalize_custom_provider_entry: base_url from the entry (`api`), and
  models via _normalize_provider_models(entry.get("models")): a non-empty dict is kept as {model_id: settings}
  (a list of ids or {id: ...} rows is converted; the sentinels __discovered_model_catalog__ and
  __explicit_model_allowlist__ are stripped)
agent/agent_init.py ~1655-1675: for the custom-provider entry whose normalized base_url equals the active route,
  _cp_models.get(agent.model, {}).get("context_length") is the model's context length (an invalid value warns and
  falls back to auto-detection); `model.context_length` is IGNORED when the runtime model differs from model.default
  (_scope_context_length_to_default_runtime), and every lane runs a --model other than the default
$ bash harness-ports/tests/test_lane_profile.sh
lane profile: 13 passed, 0 failed
$ grep -n -E '^create_lane|^verify_lane|Preserve every untouched byte' harness-ports/bin/lane-profile.sh
25:verify_lane() {
89:create_lane() {
113:  # Preserve every untouched byte in config.yaml. Parse before and after, and refuse
```

A question for you, not a fact: does a `models` dict under a provider with `discover_models: true` change which models
Hermes lists or accepts for that provider (the `__explicit_model_allowlist__` sentinel suggests an allowlist mode)? A lane
always names its model, but say what you find in the premise's code description.
