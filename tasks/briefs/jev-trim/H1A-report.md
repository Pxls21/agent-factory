# H1a report: the LCM-X lane mode (task #365, D-108 item 7). Delivered as one patch. Stamp 2026-09-29 13:38Z (from `date -u`).

## TL;DR
- The patch is delivered at `/home/user/agent-factory/tasks/briefs/jev-trim/H1A-LCM-PROFILE.patch`.
  - 1110 lines, 75063 bytes.
  - sha256 `1269a424ab1e6bae808b592ab7a8ae097f1153b285fa5c25dd1f23469af120f8`.
  - It changes 8 files: 880 insertions, 9 deletions.
- It is the only write in the shared tree. There, `git status` shows only `?? tasks/briefs/jev-trim/H1A-LCM-PROFILE.patch` as mine. The `M scripts/handback_extract.py` and `M tests/test_stack.py` changes are not mine.
- On a clean worktree at the PIN with the patch applied:
  - The three suites passed: `lane profile: 69 passed, 0 failed`, `70 passed, 0 failed`, `pc_lane dispatcher: 53 passed, 0 failed`.
  - `run-all.sh` printed `ALL SUITES PASSED`.
- 56 named mutants were run: 56 killed.
- **BLOCKER FOR LANDING (D1):** the lock hunk makes CI's ledger-integrity job red.
  - The cause is S0-06 and S0-12, whose attested inputs include `upstream.lock.yaml`. The owner signed both accepted tags.
  - A re-mint and a re-sign, or an owner ruling, is needed before this lands. I did not choose between them.

## 1. Premise re-run (contract item 1): IDENTICAL
- The output file equals the expected file byte for byte.
- `bef1e9e-is-an-ancestor-of-HEAD`.
- sha256 prefixes of the seven files at the PIN:

| File | sha256 prefix |
|---|---|
| lane-profile.sh | 9b2aa796197009da |
| pc-lane.sh | fd281439ea3b5aaf |
| pc_lane.sh | 984fdda57951e54b |
| upstream.lock.yaml | 8990e5f12dbdb6a7 |
| test_lane_profile.sh | cfbed752380da49c |
| test_pc_lane.sh | bce3c4ff9bf83979 |
| test_pc_lane_dispatcher.sh | 5ff87dffc893d133 |

- `lcm` count is 0 in all four sources (rc=1).
- `346:for v in HERMES_MODEL…`; `221: python3 - … LANE_DONE_GAT`.
- b3399c1 is a `commit`; `1746:def _select_context_engine`.
- Suites at the PIN: `lane profile: 30 passed, 0 failed` · `67 passed, 0 failed` · `pc_lane dispatcher: 51 passed, 0 failed`.

## 2. Files: final lines and sha256 (the same bytes in the build worktree and the patched clean worktree)

| File | Lines | +/- | sha256 |
|---|---|---|---|
| docs/HARNESS-PORTS.md | 838 | +91/-0 | ac1b11cc16263896b5fa80f3bc8a1f5e127adc86ca84bca91265d3fc7ac37014 |
| harness-ports/bin/lane-profile.sh | 819 | +342/-6 | dae6e8955dedd66b5ff1a9b7c015efc87fbaa94a708fcf0cdd5af392ba20ba25 |
| harness-ports/bin/pc-lane.sh | 609 | +29/-1 | b48bceaab26d4c18ff188305afff1a7de3e37771d0729fcf71a20e80eedd410b |
| harness-ports/tests/test_lane_profile.sh | 961 | +304/-0 | 968e16ace076f7e1a816ed2fd490996be908689b2e7bf3ecb6fd00967c92710b |
| harness-ports/tests/test_pc_lane.sh | 798 | +63/-1 | 8856fbe21351a2a40b5027a607517d22fdecea1981652704b07663d04836286c |
| harness-ports/tests/test_pc_lane_dispatcher.sh | 591 | +16/-0 | 8144bfc4e1e704c93c565b88ae6a1c3854bde2e1f92d23869f8a927aaa000132 |
| scripts/pc_lane.sh | 629 | +3/-1 | 5dbfb535dcb3c99ac8a385b952561c5e72eb531f8975d1f0de641c67df801737 |
| upstream.lock.yaml | 384 | +32/-0 | 42c8a005004aa223a561761b005090588a3e3899b2a67a11f433a1ee31109280 |

## 3. Evidence per contract item

### Item 2: the lock entry (`upstream.lock.yaml:353-384`)
- The entry key is `lane_context_plugins.hermes-lcm-x`. A 6-line comment header sits at 354-359.
- Its fields:
  - source: https://github.com/electricsheephq/lcm-x
  - revision `601a9ccb3d5fefbe242a453e57ed2c8196bf33c3`
  - version 0.24.3; license MIT
  - committed `2026-09-28T11:20:45+09:00 (02:20:45Z): Merge pull request #577…`
  - names: plugin_identity.py:24-25 and plugin.yaml:1-2
  - role: "the H1 trial on one PC lane profile, beside a control lane; not production"
  - hermes_pins_tested_upstream: "none of ours". Upstream CI uses a stub ABC (ci.yml:59 "Stub hermes-agent ABC"). The nightly hosts are f97608f (0.21.5), evaOS adapter 2d10969 (0.21.2) and 6f7a799. Our lane runtime b3399c1 (0.21.1) and our proof runtime 527da60 are not among them (T1 §5 row 2).
  - runtime_imports: tiktoken 0.14.0, with the wheel name, the wheel and sdist digests, and the PyPI publish date.
  - absent_by_design: regex, requests, numpy and fastembed, each with a citation.
  - tokenizer: url, cache_file and digest.
  - adopted.
- **Verified** before the clone was deleted. `git rev-parse HEAD` gave 601a9cc…, porcelain 0. `plugin.yaml` reads `name: hermes-lcm-x` and `version: 0.24.3`. LICENSE reads "MIT License". plugin_identity.py:24-25 reads `PLUGIN_NAME = "hermes-lcm-x"` and `ENGINE_NAME = "lcm-x"`. The log line matches.
- I never installed LCM-X and never ran its code. I used git on it, read it and scanned it with AST.
- The lock's structural invariants stay (checked earlier): `parse_lock` gives 25 entries; 0 separator characters; the `hermes-agent` and `commit: b3399c1` lines each appear once.
- `tests/test_upstream_lock_lane_runtime.py` passes; it is in set 7ec9e6f92a8a.

### Item 3: `LANE_CONTEXT_ENGINE`
- **Where it is read.** `lane-profile.sh:20-34` reads it once at the top, as the script reads its other env knobs (`LANE_DONE_GATE` is read at :521).
  - `''` means off, `lcm-x` means on.
  - Any other value gives rc 64: `lane-profile: unknown LANE_CONTEXT_ENGINE (lcm-x, or unset): <value>`.
  - :811-812: create and verify check the paths before any clone or write. The paths must be absolute and one line, and `LCM_X_DEPS_DIR` must hold no `:`.
- **Off is byte-identical.** Check "LANE_CONTEXT_ENGINE empty writes the unset run's golden bytes (both base profiles, gate off and on), and no LCM file". Mutants M07, M08 and M09 are killed by it.
  - The only change on the off path is that `$ENGINE` is passed to the two heredocs and ignored there.
  - All 30 checks that existed at the PIN are unchanged and pass.
- **(a) The plugin link.** `lcm_x_install` is at :110-132 and verify (a) at :200-229.
  - The plugin sits at `<profile>/plugins/hermes-lcm-x` as a symlink to `LCM_X_DIR`. Hermes scans `<HERMES_HOME>/plugins/<dir>/plugin.yaml` (plugins_discovery.py:151). `hermes -p` makes the profile its HERMES_HOME.
  - `create` repoints a link that points elsewhere. It refuses a real directory in the link's place, a `plugins` symlink, and an `lcm-x.env` symlink.
  - verify checks that the link's target is exactly `LCM_X_DIR`, that `plugin.yaml` names `hermes-lcm-x`, that `git rev-parse HEAD` equals the lock's revision, that the clone is clean, and that no second LCM plugin (`hermes-lcm-x` or `hermes-lcm`) sits in `plugins/`.
  - The revision comes from the lock only (:186-199). Mutant M37 hard-codes the real revision and fails against the fixture lock.
- **(b) The config keys.**
  - The create rule is at :602-615 and the text edit at :749-763. `plugins.enabled` gains `hermes-lcm-x` and keeps its other entries; `context.engine` becomes `lcm-x`.
  - Citations at b3399c1:
    - plugins_discovery.py:213: the plugin loads only when `plugins.enabled` names it. `enabled is None or not names & enabled` means it is not loaded, and I read this code this session.
    - plugins_discovery.py:192: `plugins.disabled` wins.
    - agent_init.py:1746-1752: the engine is chosen from `context.engine`.
  - verify (b) is at :231-251, and verify_lane's expected config is at :458-469.
- **(c) The settings.** `lcm_x_settings` (:103-108) writes exactly five lines to `<profile>/lcm-x.env`.
  - The five lines:
    - `LCM_DISABLED_TOOLS` with 12 tools: lcm_grep, lcm_recall, lcm_load_session, lcm_describe, lcm_expand, lcm_expand_query, lcm_evidence_pack, lcm_compile_evidence, lcm_compute, lcm_query_state, lcm_retrieve, lcm_doctor.
    - `LCM_DATABASE_PATH=<profile>/lcm.db`
    - `LCM_EMBEDDINGS_ENABLED=false`
    - `TIKTOKEN_CACHE_DIR=<LCM_X_TIKTOKEN_DIR>`
    - `PYTHONPATH=<LCM_X_DEPS_DIR>`
  - `pc-lane.sh:465-485` gives them to the lane's hermes as environment; the launch line is `pc-lane.sh:488`. They never go into the profile `.env`, which Hermes loads with override=True (env_loader.py:349-350).
  - Verified this session: LCM-X reads `LCM_DISABLED_TOOLS` from os.environ only.
    - It is filtered from the registry (`__init__.py:549-554`) and from the engine schemas, and refused on call (`engine.py:4308-4320`).
    - The `lcm:` section of config.yaml supports only 4 keys (config.py `_SUPPORTED_LCM_CONFIG_YAML_KEYS`), and none of the five settings is among them.
  - The tokenizer file is `9b5ad71b2ce5302211f9c61530b329a4922fc6a4`, which is sha1 of the cl100k_base URL (tiktoken 0.14.0 load.py:35-58). Its sha256 is `223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7` (openai_public.py:75-79). verify refuses the file absent or altered (:278-283).
  - The coordinator's extra: tiktoken must import from `LCM_X_DEPS_DIR` under the lane's Python.
    - verify finds that Python from `HERMES_BIN`'s shebang, or from `LCM_X_PYTHON`. It refuses `-I` or `-E`.
    - It then runs a probe with `requests` and `blobfile` blocked. The probe imports tiktoken, loads cl100k_base and encodes text.
    - It refuses when the module file is not under `realpath(deps)` or when the version is not the lock's (:284-327).
- **Load-time versus lazy imports.**
  - With embeddings off, loading LCM-X needs only `yaml`, which is present in the venv and guarded (config.py:8-11).
  - tiktoken is lazy: tokens.py:39-42 imports it in a daemon thread at a session's first token count, and without it LCM-X falls back to a character estimate (tokens.py:92-111). It is supplied because condition c asks for accurate counts with no download.
  - regex, requests, numpy and fastembed stay absent, with the citations in the lock's `absent_by_design`.
  - tiktoken 0.14.0 imports `regex` lazily (core.py:398), and `_special_token_regex` falls back to `re` (core.py:432-436). I verified this in the sdist this session.
- **(d) Summaries.** verify (d) is at :329-357.
  - Route: LCM-X calls `call_llm(task="compression")` with no provider (escalation.py:303-340). With `auxiliary.compression` on auto, Hermes sends it to the main runtime, which is the lane's OmniRoute provider (auxiliary_client.py:4097-4168, 4195-4220).
  - Fallbacks: on an auth, payment, exhausted-429, connection, model-incompatible or malformed-response error, Hermes tries these in order (auxiliary_client.py:6835-6908, 3790-3822, 2882-2890):
    1. the task's `fallback_chain`;
    2. `fallback_providers` and `fallback_model`;
    3. the discovery chain (OpenRouter, Nous, a custom endpoint, the API-key providers).
  - verify refuses `fallback_providers`, `fallback_model`, a non-auto provider, and a `base_url`, `api_key` or `fallback_chain` under `auxiliary.compression`.
  - verify then prints one stderr note, names only. It lists the credential-shaped names in `.env` and in the runner's environment that the main route does not use, and `auth.json` if present. The test asserts that no value appears.
- **(e) Fail loud.** Every refusal is rc 64 with `lane-profile: lcm-x (<item>): <why>`. The tests assert each exact line.

### Item 4: pass-through
- `scripts/pc_lane.sh:346-348` adds `LANE_CONTEXT_ENGINE LCM_X_DIR LCM_X_DEPS_DIR LCM_X_TIKTOKEN_DIR` to the FWD loop, which forwards a variable only when it is set.
- `pc-lane.sh:450-454` validates the mode. It refuses an unknown value, and it refuses lcm-x together with a `HERMES_PROFILE` override.
- `pc-lane.sh:465-485` builds `env -u` for every inherited `LCM_*` except `LCM_X_*`. It adds the five lines, with `PYTHONPATH` first and any inherited value after it.
  - It refuses an unexpected line, and a count that is not 5.
  - When off, `LCM_ENV=()`, so the command is the pre-mode one.
- The helper gets the variables through the runner's environment, as it gets `LANE_DONE_GATE`.

### Item 6: test counts
- At the PIN: 30, 67 and 51 checks. With the patch: 69, 70 and 53.
- That is 44 new checks: 39, 3 and 2. Each has at least one named mutant.

### Item 7: docs
- `docs/HARNESS-PORTS.md`: env-table rows at 403-407.
- "### LCM-X lane mode (task #365, H1; off by default)" at 409-493 holds the mode and the five conditions with citations, the tools off and why, the summary route and the fallback ladder, what verify checks, the PC steps, and **NOT done**.

## 4. Gates

### Gate plan
Command: `stack.py gate paths=<8> mode=plan`, run with `--tree` set to the worktree and `--log-dir` set to scratch, so nothing was written to the shared `.jev`.
- Result: `run list 29 of union 30: pytest 22 · python3 2 · bash 5 · not run 1`, set=658832a06eaa (22 pytest files).
- The one not run is `tests/test_vendored_manifest.py`. The stack names a `-k` test for it instead.
- The union at HEAD the 13:3xZ live-state commit [coordinator: the lane cited its pre-push local id] lists the same 30 files as at the PIN.

### Results on the clean PIN worktree with the patch applied
Counts are pasted from `scripts/test_summary.sh`; `--basetemp` was under `/tmp/h1bt`, outside every work tree.

| What ran | Set | Result |
|---|---|---|
| 11 pytest files | d7fd1009207b | `1 failed, 745 passed in 289.11s (0:04:49)` (the failure is S0-11; see D4) |
| 6 pytest files | 4d556618121b | `358 passed, 1 skipped in 302.22s (0:05:02)` |
| 5 pytest files | 7ec9e6f92a8a | `574 passed in 138.66s (0:02:18)` |
| `test_vendored_manifest.py -k test_committed_manifest_matches_fresh_generation` | | `1 passed, 56 deselected in 3.45s` |
| `run-all.sh` | | `ALL SUITES PASSED` |

- The one skip is a LOUD SKIP: `test_qwen_jev.py` runs only in the PC's qwen-jev venv.
- The slopo runtime tests ran because I copied the gitignored `.slopo-runtime/model` in.
- `run-all.sh` suites:
  - lane_done_gate 19/0; bridge_token 9 OK
  - test_lane_profile.sh 69/0; test_pc_lane.sh 70/0; dispatcher 53/0; admission 22/0
  - context_mirrors 11/0; sync_skills 34/0
  - build-roles OK; the rest pass
- The build worktree gave the same results before the last test additions: `1 failed, 745 passed`, `925 passed, 8 skipped` (the 8 are 7 slopo skips without the model, plus qwen_jev), and `test_slopo.py` with the model gave `46 passed`.

### Other checks
- `git diff --check`: rc 0.
- 0 U+2028/U+2029 bytes in all 8 files.
- `scripts/ap_screen.py` gave 43 tells over 6 files. I reviewed the ones on my lines:
  - AF-AP-115 `shutil.which(hermes)`: this mirrors the launcher on purpose. It uses the same PATH as the hermes that pc-lane.sh runs, and it is not a trust anchor.
  - AF-AP-175 (two git calls): a residual TOCTOU between verify and load, which any static verify has.
  - AP-32: the digest is compared as the exact `sha256:<hex>` form the lock stores.
  - The other tells are on pre-existing lines.

## 5. Mutants
- Driver: `scratchpad/h1a/mutants.py`. Each row copies `harness-ports/`, `scripts/` and `upstream.lock.yaml` fresh.
  - The old text must occur exactly once, and the sha must change.
  - `bash -n` must pass, and every heredoc that parsed before must still parse.
  - The row's suite then runs from the copy. A kill counts only when the named check prints `[FAIL] <label>`.
  - `EXPECTED=56` is a literal.
- Final: `EXPECTED=56 KILLED=56 SURVIVED=0 INVALID=0 MISSING_OR_DOUBLED=0`, summarize rc 0.
- Controls:
  - Unmutated copy: tlp `69 passed, 0 failed`, tpl rc 0 fails 0, tpd `53 passed, 0 failed`.
  - Driver self-test with one row dropped: `ROWS 55 (unique 55) != EXPECTED 56: the table lost or doubled a row`, rc 3.
  - The heredoc check's negative control: `broken heredoc refused: heredoc 1 no longer parses`.
- **Reported both states.** The first full run gave 54 KILLED and 2 INVALID (M55, M56). That was a driver defect: `scripts/pc_lane.sh`'s only `<<'PY'` sits inside a remote bridge command string, and the unmutated file also failed my parser. I fixed the check to compare per heredoc against the original and re-ran all 56. The result is above.
- Mutant names and the checks that kill them:

| Mutant | Killing check |
|---|---|
| M01 rev-skip | (a) clone at another commit |
| M02 tok-absent-skip | (c) tokenizer absent |
| M03 digest-skip | (c) altered |
| M04 tool-list-drop (lcm_recall) | the C1 bytes against an independent 12-tool literal |
| M05 engine-skip | (b) engine absent |
| M06 unknown-accepted | unknown engine |
| M07 off-installs | off identity |
| M08 off-config | off identity |
| M09 default-on | off identity |
| M10 enabled-replaced | kept entries |
| M11 comment-dropped | kept entries |
| M12 env-rewritten | same inodes |
| M13 dirty-clone-skip | (a) clone with changes |
| M14 islink-skip | (a) plugin copy in the link's place |
| M15 install-dir-skip | create refuses a real directory |
| M16 second-plugin-skip | (a) second LCM plugin |
| M17 enabled-skip | (b) plugin missing from enabled |
| M18 disabled-skip | (b) plugin on the deny-list |
| M19 compression-skip | (b) compression off |
| M20 left-on-skip | (c) cross-session tool left on |
| M21 extra-line-accepted | (c) extra setting |
| M22 dotenv-shadow-skip | (c) LCM setting in .env |
| M23 deps-path-skip | (c) tiktoken only outside the deps dir |
| M24 import-fail-skip | (c) no tiktoken |
| M25 version-skip | (c) another tiktoken version |
| M26 IE-flag-skip | (c) -I/-E interpreter |
| M27 not-python-skip | (c) not a Python script |
| M28 env-shebang-kept | shebang derivation |
| M29 fallback-model-skip | (d) legacy fallback_model |
| M30 base-url-skip | (d) compression base_url |
| M31 provider-skip | (d) provider not auto |
| M32 lock-fail-open | no lock entry fails closed |
| M33 over-refuse | passes again when restored |
| M34 report-values | credential names, never values |
| M35 report-no-dotenv | credential names, never values |
| M36 relaunch-from-target | relaunch with the mode off |
| M37 revision-hardcoded | C1 |
| M38 abs-skip | paths before any write |
| M39 colon-skip | paths before any write |
| M40 early-paths-skip | paths before any write |
| M41 link-target-skip | (a) link to another clone |
| M42 repoint-skip | create repoints |
| M43 plugdir-verify-skip | (a) plugins symlink |
| M44 plugdir-install-skip | create writes nothing through a plugins symlink |
| M45 envlink-verify-skip | (c) lcm-x.env symlink |
| M46 envlink-install-skip | create refuses an lcm-x.env symlink |
| M47 env-dropped (pc-lane) | pass-through |
| M48 inherited-kept | pass-through |
| M49 pythonpath-no-prepend | pass-through |
| M50 always-on | off pass-through |
| M51 unknown-accepted | stops rc 64 |
| M52 override-allowed | stops rc 64 |
| M53 extra-line-passed | stops rc 64 |
| M54 count-skip | stops rc 64 |
| M55 fwd-drop (dispatcher) | the mode travels, quoted |
| M56 fwd-default-on | off carries no LCM variable |

## 6. Patch proof
1. I made a fresh `git worktree add --detach <scratch>/wt2 bef1e9ed119953132f879ec8e6b83687e6b6af6f`, with 0 porcelain lines.
2. `git apply --check`: rc 0. `git apply`: rc 0.
3. `git diff | cmp - patch` shows them byte-identical, and all 8 files' sha256 match the build worktree.
4. The tests in section 4 ran there.
5. The shared tree's HEAD moved to the 13:3xZ live-state commit [coordinator: the lane cited its pre-push local id] during the work. None of the 8 paths changed between the PIN and the 13:3xZ live-state commit [coordinator: the lane cited its pre-push local id] (`git diff --stat` is empty). `git apply --check` against the shared tree still gives rc 0, a read-only check.

## 7. The two launch commands
Run them one after the other, one long-context local lane at a time (D-061). The lane id is the brief basename plus PIN[:8], so the `lcmx-` copy gives a distinct lane, profile (`aflanelcmx…`) and `.lanes` directory.
```
cp tasks/briefs/<dir>/<TRIAL>.md tasks/briefs/<dir>/lcmx-<TRIAL>.md
MAX_POLLS=960 bash scripts/pc_lane.sh tasks/briefs/<dir>/<TRIAL>.md hermes code-implementer
# after the control lane has ended:
MAX_POLLS=960 LANE_CONTEXT_ENGINE=lcm-x bash scripts/pc_lane.sh tasks/briefs/<dir>/lcmx-<TRIAL>.md hermes code-implementer
```
- Leave the `LCM_X_*` variables unset in the sandbox. The PC defaults are `$HOME/lcm-x`, `$HOME/lcm-x-deps` and `$HOME/lcm-x-tiktoken`, and FWD sends a variable only when it is set.

## 8. PC steps, in order (idempotent)
These are the same lines as in the runbook section.
- The mode's code runs from `~/agent-factory` (`AF_REPO`), not from the lane tree. So step 1 comes first, after the landing push.
```
cd ~/agent-factory && git fetch --quiet origin claude/soundbox-kit-migration-iz1jwf && git merge --ff-only FETCH_HEAD
[ -d ~/lcm-x/.git ] || git clone --quiet https://github.com/electricsheephq/lcm-x ~/lcm-x
git -C ~/lcm-x -c advice.detachedHead=false checkout --quiet --detach 601a9ccb3d5fefbe242a453e57ed2c8196bf33c3
printf 'tiktoken==0.14.0 --hash=sha256:f5e7665f6624e052e5e7f6a36919ab69279decdc976d7b16b4fa15e1897d0513\n' > /tmp/lcm-x-deps.req
[ -f ~/lcm-x-deps/tiktoken-0.14.0.dist-info/METADATA ] || ~/venv-agent-factory/bin/python -m pip install --quiet \
  --no-deps --no-compile --target ~/lcm-x-deps --only-binary=:all: --platform manylinux_2_28_x86_64 \
  --python-version 3.11 --implementation cp --abi cp311 --require-hashes -r /tmp/lcm-x-deps.req
mkdir -p ~/lcm-x-tiktoken; T=~/lcm-x-tiktoken/9b5ad71b2ce5302211f9c61530b329a4922fc6a4
[ -f "$T" ] || { curl -fsSL -o "$T.tmp" https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken && mv "$T.tmp" "$T"; }
echo "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7  $T" | sha256sum -c -
LANE_CONTEXT_ENGINE=lcm-x bash harness-ports/bin/lane-profile.sh create h1-preflight \
  && bash harness-ports/bin/lane-profile.sh remove aflaneh1preflight
```
- The last line is the preflight. Create runs the full verify, which includes the real wheel's import, load and encode under the Hermes venv's Python with `requests` blocked.
- The pip step never touches the Hermes venv. `--target` holds only tiktoken. The only cp311 x86_64 glibc wheel on PyPI is the pinned manylinux_2_28 file, and it is selected by hash.

## 9. NOT done
- **Nothing ran on the PC.** There was no lcm-x clone, no pip install, no tokenizer download, no preflight, no launch and no load of LCM-X in Hermes.
- The real tiktoken wheel was never imported here. The sandbox fixtures use a labelled TEST DOUBLE.
- No proof exists that LCM-X loads on Hermes b3399c1: upstream CI builds against a stub ABC. verify is static. A load failure only logs a warning, and Hermes falls back to its built-in compressor (plugins_loader.py:283-289, 321; agent_init.py:1789-1792).
  - The post-run proof is two things together: rows for the lane's session in `<profile>/lcm.db`, and no such warning in the lane's log. That is the coordinator's H1b.
- The summary route was not checked live. That is the coordinator's egress watch.
- D1 is unresolved: no re-mint of S0-06 or S0-12, and no ledger regeneration.
- `scripts/pc_lane.sh` does not forward `LCM_X_PYTHON`. The runbook says so. If the PC's `hermes` is not a Python script with a plain shebang, the lcm-x lane cannot launch until one word is added to the FWD list.
- The codex-harness branch of pc-lane.sh ignores `LANE_CONTEXT_ENGINE`. The mode applies to Hermes only, and codex is not installed on the PC.
- verify does not read the Hermes checkout's project `.env` (cli.py:172-174, `override=False`, fill-only). That file cannot override the five settings, but it could fill other unset `LCM_*` keys, for example LCM_SUMMARY_MODEL or LCM_PROACTIVE_RECALL_ENABLED (default False).
- There are no ledger, tasklist or live-state edits. Those are the coordinator's.

## 10. DISCREPANCIES and deviations
- **D1 (BLOCKER for landing).**
  - With the patch, `python3 scripts/validate-ledger integrity --root . --ledger proofs/ledger.json` gives rc 1 with these lines:
    - `attestation-mismatch: S0-06 upstream.lock.yaml`
    - `attestation-mismatch: S0-12 upstream.lock.yaml`
    - `ledger-drift: S0-06 claimed PRESENT but INVALID`
    - `ledger-drift: S0-12 claimed PRESENT but INVALID`
  - It gives rc 0 at the PIN, and rc 0 with only the lock hunk reverted. So only the lock causes it.
  - CI job `ledger-integrity` (stage0-ci.yml:74-90) runs exactly this command, so the push would be red.
  - The owner signed `accepted/S0-06` and `accepted/S0-12` (D-107). A changed attested file voids an accepted tag (precedent INCIDENT-LOG.md:239).
  - The pytest union does not catch it.
  - Options:
    - (i) Re-mint S0-06 and S0-12, regenerate the ledger, and have the owner re-sign.
    - (ii) Get an owner ruling to put lane-only pins in a separate lock file. This changes brief item 2 and bears on standing rule 13.
  - The test hunk is NOT independent of the lock hunk: the lcm-x tests build their fixture lock from the real entry.
- **D2.** T1 counted 3 cross-session tools. My read of the PIN turns 12 off and leaves 3 on: `lcm_status`, `lcm_inspect` and `lcm_recent`, which reach the current session or conversation only. The runbook §7 lists them with citations.
- **D3.** The compaction note at `engine.py:6679-6694` still names lcm_grep, lcm_describe and lcm_expand, which are off. A call to one is refused. This is upstream behaviour; the trial measures its effect.
- **D4 (pre-existing, venue).**
  - `test_every_repo_file_a_checker_reads_is_attested[S0-11]` fails in any worktree under the scratchpad: `rubric-isolation-failure: observation-failed`.
  - The cause: `/tmp/claude-0` has mode 700, and the dropped uid 65534 cannot reach the scripts.
  - At the clean PIN: `1 failed in 1.73s`. With the patch at `/tmp/h1a-s011` (mode 755, since removed): `1 passed in 1.93s`.
- **D5 (adjacent, not fixed).** In off mode, lane-profile removes `fallback_providers` but not the legacy `fallback_model`, which Hermes reads (fallback_config.py:57-74). lcm-x verify refuses it.
- **D6 (adjacent, not fixed).** The header comment for `HERMES_PROFILE` in pc-lane.sh says the default is `agentfactory`. The real default is the per-lane clone.
- **D7 (deviations beyond the brief, flagged).**
  - Extra variables: `LCM_X_DEPS_DIR` and `LCM_X_TIKTOKEN_DIR` (forwarded), and `LCM_X_PYTHON` (not forwarded). FWD carries 4 names, not 2.
  - Extra checks beyond a to d:
    - compression off; a second LCM plugin
    - `-I`/`-E`; the lock entry missing
    - `LCM_*` names in `.env`
    - `plugins` and `lcm-x.env` as symlinks; the link target
    - relative paths and `:`; the runner's line count
  - In lcm-x mode the runner strips every inherited `LCM_*` except `LCM_X_*`.
  - `--no-deps` departs from tiktoken's own Requires-Dist (regex, requests).
- **D8.** On the PC, verify reads the profile `.env` for KEY NAMES only, never values, in the shape of Hermes's own scanner (env_loader.py:49-68). This is a read of a copy of the owner's secrets file, names only. I read no `.env` in the sandbox.
- **D9 (deviation, earlier in the session).** An early `git grep` in the shared partial clone `/home/user/nerdherderdani/hermes-agent` fetched blobs lazily and printed "Auto packing the repository in background".
  - HEAD (527da60) and the working tree were unchanged (0 porcelain lines), and no gc process was left.
  - The clone's object store may have gained objects or a pack.
  - All later Hermes reads came from my own b3399c1 clone, not from `git show` in that clone.
- **D10 (a design-phase reversal, both states).**
  - State 1: `regex==2026.9.10` is a runtime dependency, because tiktoken's metadata declares it.
  - State 2: it is not needed. tiktoken imports `regex` lazily (core.py:398) and `_special_token_regex` falls back to `re` (432-436). LCM-X's own uses are guarded (message_patterns.py:16-19; ingest_protection.py:434-440).
  - I resolved it from primary source before the lock entry existed. The PC preflight's probe settles it. If the probe fails, add regex to the deps directory and the lock.

## 11. Self-attack: how could a lane run without LCM-X, or with a cross-session tool on, and still pass verify?

**Without LCM-X:**
1. A runtime load failure: an import, the ABC or the engine's availability on b3399c1. Hermes warns and falls back. Static verify passes. Not closable statically. Mitigation: the post-run `lcm.db` rows plus the log check.
2. A relaunch without the mode. This is by design: the config is re-derived without the keys, and the plugin is not loaded because `plugins.enabled` does not name it (plugins_discovery.py:213).
3. The codex harness. The mode is ignored there (NOT done).
4. A hermes other than the one verify probed. Ruled out within pc-lane: the helper and the launch share one process environment and one PATH.

**With a cross-session tool on:**
1. `lcm-x.env` changes between verify and the launch. The runner refuses unexpected and missing lines. A same-bytes race remains as a residual TOCTOU on a lane-private file.
2. A later env write:
   - The profile `.env` (override=True) is checked for `LCM_*` names.
   - The project `.env` is fill-only, so it cannot replace a set value.
   - Bitwarden or 1Password hydration could set arbitrary names. This is not checked (residual).
3. A misclassified tool. The 3 tools left on come from a static read (inferred). Both registration paths and `handle_tool_call` honour the list, so a disabled tool is neither offered nor callable.

## 12. The three most likely ways this change is wrong
1. **The real tiktoken wheel needs `regex` or `requests` to import or encode on the PC.** Ruled out as far as the sandbox allows, by code reading (inferred). If I am wrong, the preflight fails loud and does not pass silently. The fix is one lock line plus the pip requirement.
2. **The PC's `hermes` is not a Python script with a plain shebang.** Then verify refuses (c), and `LCM_X_PYTHON` is not forwarded. The coordinator's probe named the venv Python. The shebang derivation is tested with `#!/usr/bin/env python3` and `#!<python> -I` fixtures (assumed for the PC). The preflight shows it at no cost.
3. **Off mode is not byte-identical for some source-profile shape.** Ruled out:
   - The off path's only change is an ignored argument.
   - The goldens are byte-compared for two base profiles, gate off and on.
   - M07, M08 and M09 are killed.
   - All 30 checks from the PIN pass.
   - A related risk in lcm-x mode only: an unusual `plugins:` or `context:` block layout, such as flow style. There the semantic guard refuses the write, so create fails loud and writes nothing.

## 13. Evidence tiers
- **Verified (run):**
  - the premise; the lock fields from the clone
  - the tokenizer name and hash from the tiktoken 0.14.0 source; the wheel digest from PyPI JSON
  - the Hermes and LCM-X citations, read at b3399c1 and 601a9cc
  - `LCM_DISABLED_TOOLS` is read from the environment only
  - every count in section 4; 56 of 56 mutants killed
  - the patch applies and matches byte for byte
  - D1 is caused only by the lock; D4 is caused by the venue
  - the union at HEAD is the same as at the PIN
- **Inferred:**
  - tiktoken loads without regex or requests
  - LCM-X loads on b3399c1
  - the classification of the 15 tools
- **Assumed:**
  - the PC's `hermes` shebang is Python
  - `~/venv-agent-factory` has pip
  - the PC clone is at `~/agent-factory`
  - the Hermes project `.env` holds no `LCM_*` names

## 14. Cleanup
- Both worktrees were removed and pruned; `git worktree list | grep -c h1a` gives 0. `/tmp/h1a-s011` was removed.
- The lcm-x and hermes clones, the tiktoken sdist and tarball, the mutant copies and `/tmp/h1bt` were deleted.
- No process of mine is running. The pytest processes still running belong to the scrub2r4 and vk2r2 lanes.
- The logs stay in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/h1a/`, including the driver `mutants.py`, the `mut-batch*.log` files and the `wt2-*.out` files.

S1 injections this segment were rated inline; none is pending.