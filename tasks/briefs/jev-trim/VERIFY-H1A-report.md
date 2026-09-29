> **Coordinator note (2026-09-29 18:1xZ):** extracted by `scripts/stack.py harvest` (run s-20260929T180827Z-9b83a0; hand-back sha256 prefix bd517d6d802e, 25,780 characters). Served model: claude-opus-5-5 on all 512 assistant records, 0 refusal stops, 1 compaction, 2 tool errors. `report_lint`: 1 OK; no local ids. The lane wrote no report file (its system prompt forbids one) and used the brief's fallback: this file is its hand-back, verbatim. The gate recommendation is MERGE-READY-WITH-FOLLOWUPS. The coordinator's rulings: (1) H1a (42a4a1d) stands as landed, verified in the sandbox with follow-ups; the lcm-x mode stays opt-in, and no lane runs it until H1b proves the load and run-time behaviour on the PC (section 5 below is H1b's checklist). (2) No finding blocks (D-034): F1 to F7 need a hostile or malformed source profile, `.env`, plugins directory or Hermes scope on the owner's PC, which H1b checks against the real files (the `.env` by names only); F8 and F12 are off the canonical path; F9 fails closed without a named reason. The follow-ups (F1 to F10, F12, F13, F17, F18, F20, F23) are GitHub issue #85. (3) F21: the S0-11 union failure is the venue (a worktree under the root-only `/tmp/claude-0`, which the check's dropped uid cannot enter); H1a's landing gate ran in the main tree. (4) The third restart the lane found (`uptime -s` 14:36:27) is in the incident log.

# VERIFY-H1a report: task #365 (the LCM-X lane mode and the D-110 lock move)

**Recommendation: MERGE-READY-WITH-FOLLOWUPS.** No finding meets all five conditions of the blocking predicate. Two things this verdict depends on were not reproduced:
1. **Hermes and LCM-X at run time.** I read Hermes b3399c1 and LCM-X 601a9cc but did not run them, as the rules require. H1b must prove their load and run-time behaviour on the PC.
2. **The 8-file pytest union.** It did not pass here: 1 failed, 956 passed. The failing test is S0-11, and the cause is where my worktree lives, not H1a (F21).

- **PIN:** origin 42a4a1d, "H1a landed (task #365; GATED-PENDING-VERIFY): the LCM-X lane mode, its pins in pc-lane.lock.yaml (D-110)".
- **Parent:** origin 77e5a16, the D-110 commit.
- **Start and end:** 16:37:57Z to 2026-09-29T18:04:07Z, both from `date -u`.
- **Lane model:** claude-opus-5-5, per my system prompt. The harvest counts the served models.
- **Report file:** I did not write `tasks/briefs/jev-trim/VERIFY-H1A-report.md`. My system prompt forbids report files, so I used the brief's fallback: this message is the whole report.
- **What I wrote:** only scratch files under `$S=/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vh1a/`.
- **Shared tree:** `git status --porcelain` is empty. The one expected record is the stack run under `.jev/stacks/s-20260929T170047Z-fdac0f/`.
- **S1 ratings:** written inline for s1-252526be, s1-af0168a4, s1-e546304b, s1-d071169f, s1-148371f7 and s1-bfc7cd07. None is pending.

## 1. Premise and gates

**Premise.** Every `$` line matched: 70/70/53, set=f7d8d61400d8, ledger integrity rc 0, and every hash. So there is no CONTRACT-INVALID.

**Gates at the PIN, in my worktree.** Counts are pasted from each suite's last line or from `scripts/test_summary.sh`.
- `test_lane_profile.sh`: `lane profile: 70 passed, 0 failed`
- `test_pc_lane.sh`: `70 passed, 0 failed`
- `test_pc_lane_dispatcher.sh`: `pc_lane dispatcher: 53 passed, 0 failed`
- `bash harness-ports/tests/run-all.sh`: rc 0, `ALL SUITES PASSED`. That includes test_pc_lane_admission `22 passed, 0 failed`, test_context_mirrors `11 passed, 0 failed`, test_lane_done_gate `lane done gate: 19 passed, 0 failed` and test_bridge_token_handling `9 checks passed — ALL OK`.
- `stack.py gate paths=<the eight paths> mode=plan`: run s-20260929T170047Z-fdac0f listed 13 files: 6 pytest (`6 files set=69b3cbbe4119`), 2 python3 and 5 bash. The python3 and bash files all ran inside run-all.sh.
- **Pytest union** (the 6 files plus `tests/test_shell_syntax.py` and `tests/test_attested_inputs.py`, set=f7d8d61400d8): `pytest-summary: 1 failed, 956 passed in 184.07s (0:03:04)`, pytest-exit 1. The one failure is `test_every_repo_file_a_checker_reads_is_attested[S0-11]` (F21).
- `tests/test_vendored_manifest.py`, the two named tests only: `pytest-summary: 2 passed, 55 deselected in 6.52s`.
- **Mutation driver control.** I ran a byte copy of `h1a-r1/mutants.py` (sha256 dcbad97edf85debf…). Its `validate` mode read `58 of 58 rows anchor once`. Its `control` mode read:
  - tlp: rc 0, fails 0, `lane profile: 70 passed, 0 failed`
  - tpl: rc 0, fails 0
  - tpd: rc 0, fails 0, `pc_lane dispatcher: 53 passed, 0 failed`

**Reboots.** `uptime -s` reads 2026-09-29 14:36:27. That is before my start, so no reboot happened during my runs and no run is void. The time is later than the two reboots the brief names, so the VM probably rebooted a third time before this lane was dispatched. This is for the incident log.

## 2. Finding inventory (no severity filter)

Field names: *Ev* is the evidence level. *Map* is the contract mapping. *Canon* is the canonical-path status. *Effect* is the material effect. *Repro* is the reproduction. *Fix* is the suggested fix.

Log and script paths are under `$S/logs/` and `$S/diff/`. The scripts expect the PIN worktree at `$S/pin` (recreate it in section 7).

### Conditions (item 3)

**F1. FOLLOW-UP. Condition (b) misses "compression off" values that are not booleans.**
- The helper refuses only `compression.enabled is False` (lane-profile.sh:251).
- Hermes reads the flag as `str(cfg.get("enabled", True)).lower() in {"true","1","yes"}` (agent/agent_init.py:352-354, used at 1461).
- A source profile with `enabled: "off"`, `null` or `0` passes both create and verify with rc 0 (`logs/sources.log` S1-S3). Hermes would then never call the engine. The same holds for "on", "False" and 1.0.
- *Ev:* the helper side is reproduced through the real create and verify. The Hermes side is a static read.
- *Map:* item 3 (b), and the builder's own claim that (b) means "compression is not off".
- *Effect:* only if the owner's source profile uses such a spelling. Plain YAML `off`, `no` or `false` parse to boolean False and are refused.
- *Fix:* mirror `_cfg_flag` when `compression` is a mapping.

**F2. FOLLOW-UP. The clean-clone check in (a) has blind spots.**
- The check is `git status --porcelain --untracked-files=all`. It does not see:
  - skip-worktree files
  - assume-unchanged files
  - `.git/info/exclude` entries
  - an inherited `GIT_DIR`
- With changed code under each of these, verify passes (`logs/shapes.log` A6-A9, rc 0). Hermes would load the changed code.
- Neither pc-lane.sh nor scripts/pc_lane.sh sets any `GIT_*` variable. The precondition is tampering with the owner's `~/lcm-x`.
- *Fix:* run git with `GIT_DIR`, `GIT_WORK_TREE` and `GIT_INDEX_FILE` unset. Refuse any `git ls-files -v` tag other than `H`. Optionally compare the content hash of each tracked file with `ls-tree`.

**F3. FOLLOW-UP. The second-plugin check reads only `plugins/<child>/plugin.yaml`.**
- Hermes b3399c1 also accepts `plugin.yml`, `plugin.json` and category-nested `<cat>/<name>/` plugin directories.
- A second manifest named `hermes-lcm-x` in any of those forms passes verify (`logs/shapes.log` B2-B4, rc 0).
- From a static read of Hermes's discovery, it could shadow or pre-empt the pinned clone: the later winner by key takes the slot, and the first `register_context_engine` wins.
- The precondition is a second plugin placed in the lane profile.
- *Fix:* refuse any `plugins/` entry except the link, or scan every manifest form Hermes accepts.

**F4. FOLLOW-UP. The `.env` shadow scanner in (c) misses spellings that python-dotenv 1.2.2 accepts.**
- Three spellings pass create and verify with rc 0: `'LCM_DISABLED_TOOLS'=`, `export<TAB>LCM_DISABLED_TOOLS=`, and a first line that starts with a BOM.
- The real python-dotenv 1.2.2 wheel sets `LCM_DISABLED_TOOLS` for all three (`logs/dotenv_shapes.log`).
- Hermes loads the profile `.env` with `override=True`. That value would replace the lane's setting; an empty value turns all 12 tools on.
- The precondition is an `LCM_*` key in the owner's secrets file in one of these spellings.
- *Fix:* read the names with dotenv's own parser (names only).

**F5. FOLLOW-UP / UNVERIFIED (static). Verify cannot see three Hermes inputs:**
- The managed scope: `/etc/hermes` or `$HERMES_MANAGED_DIR`. Its `config.yaml` is deep-merged on top, and its `.env` is applied last with override. LCM-X reads every `LCM_*` variable, including `LCM_OLLAMA_BASE_URL` and the embedding provider.
- `HERMES_SAFE_MODE=1`, which skips plugin discovery.
- `HERMES_ENABLE_PROJECT_PLUGINS`.

*Fix:* refuse these in verify, or make each a mandatory H1b check.

**F6. FOLLOW-UP (static on the Hermes side). The `plugins.enabled` shape differs between verify and Hermes.**
- Hermes reads `set(enabled)` inside `except Exception: return None` (plugins_discovery.py:90-98).
- A list with a mapping entry therefore makes Hermes enable nothing, while verify's `hermes-lcm-x in enabled` still passes.
- The precondition is a malformed source profile.
- *Fix:* require a list of strings.

**F7. INFO. `${VAR}` in `plugins.disabled`.**
- A source with `disabled: ["${LCMOFF}"]` passes create and verify (`logs/sources.log` S5). Hermes expands `${VAR}` in config strings, so it could disable the plugin.
- The precondition is hypothetical.

**F8. FOLLOW-UP. The "expected bytes" check of lcm-x.env reads in text mode.**
- lane-profile.sh:259 opens the file with universal newlines, so a CRLF lcm-x.env passes verify with rc 0 (`logs/mv_disc.log`, MV5 block, PIN line).
- pc-lane.sh:476-483 would then export each value with a trailing CR.
- This is not reachable on the canonical path. pc-lane.sh runs `create` first, and `create` rewrites any lcm-x.env whose bytes differ (`cmp -s`, lane-profile.sh:127). The same log line shows "PIN create lk heals it".
- *Fix:* compare `open(path, "rb")` with `settings.encode()`. Refuse `\r` in pc-lane.sh.

### The lock (item 2)

**F9. FOLLOW-UP. Three malformed lock shapes fail closed, but without a named reason.**
- A missing `tokenizer.url` is read outside the `try` (line 198). A missing tiktoken entry or version is read at line 327, after the probe has run.
- These give a traceback and `lane-profile: lcm-x: verify failed`, rc 64 (`logs/lock_variants.log` L9c, L8c, L8d).
- A `digest` in the wrong form reads as "(c) … is altered" (L9f, L9g).
- Duplicate YAML keys are accepted, and the last one wins (L11).
- All 22 malformed shapes, including absent, empty, not YAML and a YAML list, exit rc 64.
- *Fix:* read and validate every field inside the `try`. The digest must match `^sha256:[0-9a-f]{64}$`, and the version must be a string.

**F19. INFO. Second copies of the pins exist, but no check reads them.**
- docs/HARNESS-PORTS.md's `sha256sum -c` install line carries the digest.
- The suite's fixture anchors carry the revision and the digest, with a count of 1 asserted.
- A re-pin fails loudly, never silently.

### The off path (item 1)

**F12. INFO / FOLLOW-UP. Off mode now needs `HOME` in one case.**
- lane-profile.sh:29-31 sets the defaults for `LCM_X_DIR`, `LCM_X_DEPS_DIR` and `LCM_X_TIKTOKEN_DIR` from `$HOME` in every mode, under `set -u`.
- With `HOME` unset and `HERMES_PROFILES_DIR` set, an off-mode create, verify or remove now exits rc 1 (`HOME: unbound variable`). The parent exits rc 0.
- This is not canonical. The dispatcher expands `$HOME` on the PC side (scripts/pc_lane.sh:142), and pc-lane.sh:70-71 and 592 need `HOME` unless `AF_REPO`, `AF_VENV` and `HERMES_STATE_DB` are all set.
- *Fix:* set the defaults only in lcm-x mode.

### Secrets (item 5)

**F13. INFO. Two echoes appear, but only in hostile shapes.**
- An lcm-x.env line without `=` is echoed, up to 40 characters.
- A hostile module in `LCM_X_DEPS_DIR` can print into the probe's stderr, and that reaches the refusal (`logs/secrets.log`: 7 fake values, 2 hits, both from these shapes).
- The ordinary pass and failure paths leak nothing. The (d) note prints names only, and the e2e leak check found none.
- *Fix:* echo only the key, and print only the probe's exception type.

### Parser, relaunch and route notes

**F14. INFO. Verify's YAML parser and Hermes's agree on the lcm-x keys, except once, in the safe direction.**
- Verify uses the pure SafeLoader; this sandbox has PyYAML 6.0.1 without libyaml. Hermes uses CSafeLoader from the pinned PyYAML 6.0.3 (utils.py:389).
- 22 of 23 hostile shapes read the lcm-x keys the same way (`logs/yaml_parity.log`).
- The exception is a tab after a colon: the pure loader raises and verify refuses, while libyaml accepts. That is the fail-closed direction.

**F15. INFO. Leftovers are inert.**
- An off relaunch after lcm-x keeps the link and lcm-x.env, but the config has no plugins or context key (`logs/e2e.log`).
- A refused lcm-x create leaves the profile on disk, and pc-lane.sh stops before hermes. The design is the same in off mode.

**F16. INFO. Some source layouts fail closed with a traceback instead of a reason.**
- An lcm-x create from an anchored plugins block that is aliased elsewhere fails with a ComposerError (`logs/sources.log` S7, rc 64).
- A flow-style `model:` fails in both the parent and the PIN; this predates H1a.

**F22. INFO. Hermes's discovery chain remains after the three chains verify refuses.**
- Verify reports the credential names it can reach, never the values.
- This already applies to the built-in compressor. H1b's egress watch covers it.

**F23. INFO (item 6). `LCM_X_PYTHON` is not forwarded, and the failure is loud.**
- When the PC's hermes is a bash wrapper, the lane stops with rc 64: `lane-profile: lcm-x (c): HERMES_BIN is not a Python script, so its interpreter is unknown; set LCM_X_PYTHON`, then `pc-lane: lane profile create failed`.
- With `LCM_X_PYTHON` set on the PC side, the lane runs (`logs/e2e.log`).
- HARNESS-PORTS.md §12 says `~/.local/bin/hermes` resolves to the venv console script, and verify follows symlinks.

### Adjacent items (item 7)

**F17. FOLLOW-UP (D5). Off mode keeps a legacy `fallback_model`.**
- This is a possible way off OmniRoute (standing rule 3), and it predates H1a.
- Fixing it would change off-mode output, so it gets its own issue. The lcm-x verify already refuses it.

**F18. FOLLOW-UP (D6). A stale comment.**
- pc-lane.sh:20 still says "HERMES_PROFILE lane profile default: agentfactory (dedicated; never the owner default)".
- The comment was already stale before H1a; the diff does not change it.

### Mutation gaps and test noise (item 8, item 9)

**F10. FOLLOW-UP. 15 of my 18 new mutants survive all three suites** (70/0, 70/0, 53/0). For each survivor below, the PIN code behaves correctly (my discriminators). What is missing is a suite check. Section 3 lists them. Each discriminator should become a suite check:
- F10a: the lock `except` scope (MV1b).
- F10b: off-mode bytes for sources that already have plugins or context blocks (MV2, MV3).
- F10c: `auxiliary.compression.fallback_chain` and `api_key` in (d) (MV11a, MV11b).
- F10d: git failure in (a) (MV6).
- F10e: the manifest-name check (MV9).
- F10f: a newline in a path (MV13).
- F10g: a byte golden for an lcm-x create over plugins or context blocks (MV20).
- F10h: pc-lane.sh's default profiles directory (MV21).

**F11. INFO. Five mutants are equivalent or nearly so on the production path.**
- MV1a still fails closed, but with a traceback.
- MV4 and MV8 change only the message.
- MV5: CRLF passes both the PIN and the mutant (F8), so only line order differs.
- MV14: verify_lane's `chain present` still refuses.

**F20. INFO, outside scope. Test noise predates H1a.**
- test_pc_lane.sh:305 wraps `reset after 5m` in backticks inside a double-quoted message, so the suite runs the curses `reset` command. That is why the curses usage text appears in the logs.
- The same line is in the parent.

**F21. INFO. The S0-11 union failure comes from the venue, not from H1a.**
- The failure reads `rubric-isolation-failure: observation-failed`.
- The mechanism is re-derived from source and the observed permission bits:
  - check_eval_hardening.py (lines 225-268) drops the child process to a non-root uid.
  - My worktree sits under `/tmp/claude-0`, which is `drwx------ root`, so that uid cannot enter it.
  - The child therefore never signals ready.
- S0-11 attests no H1a path. It was not reproduced green here, so the coordinator's claim of 957 passed is unverified by me.

**Driver note (INFO).** M32 and M32b are the same text mutation scored against two labels, so the 58 rows hold 57 distinct mutants. The driver also runs the suites with the caller's whole environment (`PYTHONPATH=.` was inherited here); the control stayed green.

## 3. Mutation (item 8)

**Reproduced:** 12 of the 58 existing mutants, each KILLED by its named `[FAIL]` check through the real suites (`logs/mut-existing.log`):
- M01-rev-skip
- M03-digest-skip
- M08-off-config (23 checks fail)
- M19-compression-skip
- M22-dotenv-shadow-skip
- M29-fallback-model-skip
- M32b-lock-file-fail-open (both lock checks fail)
- M40-old-lock-path (31 checks fail)
- M47-env-dropped (tpl)
- M48-inherited-kept (tpl)
- M55-fwd-drop (tpd)
- M56-fwd-default-on (tpd)

**New mutants:** 18, one for each clause the set leaves out (`logs/mut-new.log`). Three were killed: MV16 (`verify_lcm_x` unwired), MV17 (the verify_lane lcm-x rule turned off) and MV18 (the `added` keys dropped). The other 15 survived. Each row gives the change, then the discriminator that tells it from the PIN.

| Mutant | Change | PIN | Mutant |
|---|---|---|---|
| MV1a | lock `except (OSError, KeyError)` | L2, L3, L4, L8b, L9b: rc 64, named | rc 64, traceback |
| MV1b | the same, then `except Exception: SystemExit(0)` | rc 64 | **rc 0 (fails open)** |
| MV2 | lcm-x rule applied when the source has `^plugins:` | off create rc 0 | rc 64 (`off_src.log`; the differential's afanchor steps go rc 0 to 64) |
| MV3 | off mode re-emits blocks when plugins and context exist | afind g0 sha efa8a2634a4d, afboth g0 08c2d8d83c9c, equal to the parent | rc 0 with different bytes (9e4c2f26af7e, c10d3c095d4d); my 87-step differential also missed it (0 of 87 steps differ) |
| MV6 | ignores git failures | corrupt index plus changed file: rc 64 `git status in LCM_X_DIR failed (rc 128)` | **rc 0** |
| MV9 | no manifest-name check | skip-worktree `plugin.yaml` naming hermes-lcm-y: rc 64 | **rc 0** |
| MV11a, MV11b | drop `fallback_chain` or `api_key` from (d) | create rc 64 `(d): auxiliary.compression.<key> is set` | **rc 0** |
| MV13 | no newline check | rc 64 before any write | rc 64 after writing the profile, with a traceback |
| MV20 | re-emit inserts instead of replacing | 1 top-level `plugins:` and 1 `context:` | 2 and 2; verify rc 0 (Hermes takes the last key) |
| MV21 | pc-lane.sh default profile path | rc 0 with `HERMES_PROFILES_DIR` unset | rc 64 `cannot read …/.hermes/profile/…/lcm-x.env` |
| MV4, MV5, MV8, MV14 | the equivalents in F11 | | |

## 4. Items 1 to 9: what the evidence shows

1. **Off is unchanged.**
   - Across 87 differential steps, the unset, empty and hostile `LCM_X_*` runs at the PIN are byte-identical to each other. They are also identical to the parent once traceback line numbers are normalized.
   - The 87 steps cover 8 sources × gate unset, 0 and 1, plus re-derive, leftover, tamper, remove and usage errors.
   - Two more layouts (afind and afboth, gate 0 and 1, create and verify) are byte-identical between the parent and the PIN (`logs/off_src.log`).
   - pc-lane.sh's four off scenarios give identical transcripts (argv, environment, stderr, lane files; sha 80d4dd35465b5356).
   - The one exception is off-canonical: F12.
2. **The lock move.**
   - The only readers of pc-lane.lock.yaml are lane-profile.sh (the lock reader at lines 187-195) and test_lane_profile.sh. No proof, no `check_pin_diff` and no vendored-manifest check reads it.
   - `upstream.lock.yaml` has no diff between the parent and the PIN (`git diff --quiet` rc 0).
   - The ledger integrity check reads rc 0.
   - Every lock variant fails closed (F9 for the details).
   - Every field in the lock matches my own LCM-X clone: revision, the commit time and subject, MIT, 0.24.3, `plugin_identity.py:24-25`, and the CI stub.
   - Every tiktoken field matches PyPI and the sdist: the wheel and sdist digests, the only cp311 wheel, not yanked.
3. **Conditions a to d, and e.**
   - Correctly refused:
     - a link that points elsewhere
     - a second clone at the same commit
     - untracked or modified files
     - a flat `plugin.yaml` duplicate
     - edits after create (the whole-config equality check catches them)
     - duplicate context keys
     - `provider` other than auto, `base_url`, `fallback_model`
   - (e) holds in e2e: the store is at `<profile>/lcm.db`, `LCM_EMBEDDINGS_ENABLED=false`, and `TIKTOKEN_CACHE_DIR` plus a blocked-requests probe prevent a download.
   - Static reads, clean:
     - the compat scan found 0 hits (its positive control fired)
     - `__deepcopy__` is present
     - LCM-X reads only four routing-free `lcm:` keys
     - LCM-X's summary path calls `call_llm(task="compression")` with no provider
   - Gaps: F1 to F8.
4. **Tokenizer and runtime import.**
   - The real tiktoken 0.14.0 wheel, installed by the runbook's command, and the real `cl100k_base` file pass the real verify: create and verify rc 0 on Python 3.11.15 and glibc 2.39. The probe got 4 tokens, loaded the file under deps, and found no `regex`.
   - With an empty cache, the probe fails on the blocked `requests`, with no download.
   - With an altered copy, tiktoken deletes the file and the probe fails.
   - The digest form is exact: `sha256:<hex>` (AP-32).
   - Only H1b can prove the rest: the venv Python and ABI, the PC paths, the real shebang, whether `requests` is importable at run time, and the actual load (section 5).
5. **Secrets:** see F13.
6. **The pass-through.**
   - End to end through both real scripts, hermes gets exactly the 5 settings.
   - The inherited `LCM_SUMMARY_MODEL` and an empty `LCM_DISABLED_TOOLS` are removed. `LCM_X_*` is kept. `PYTHONPATH` is `deps:/inherited`.
   - The default profiles directory also works end to end (`logs/e2e_default.log`).
   - Without the opt-in, the dispatcher carries no LCM variable (M56 is killed).
   - For `LCM_X_PYTHON`, see F23.
7. **D5 and D6:** both follow-ups (F17, F18).
8. **Mutation:** section 3.
9. **Gates:** section 1.

## 5. What H1b must prove on the PC before the first lcm-x launch

1. **The clone.** `~/lcm-x` is at 601a9ccb3d5fefbe242a453e57ed2c8196bf33c3. Its status is clean, `git ls-files -v` shows only `H` tags, and the lane's environment has no `GIT_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` (F2).
2. **The wheel and tokenizer.**
   - The wheel is installed with `--require-hashes` (sha256:f5e7665f…) into `LCM_X_DEPS_DIR`, for the Hermes venv's Python 3.11.
   - The tokenizer file at `LCM_X_TIKTOKEN_DIR/9b5ad71b2ce5302211f9c61530b329a4922fc6a4` has sha256 223921b7….
   - Record whether `requests` is importable in the Hermes venv. If it is, a cache miss at run time would download.
3. **The preflight.** Run the preflight create with the real `HERMES_BIN`. Record `readlink -f $(command -v hermes)` and its first line. If that is not a plain Python shebang, set `LCM_X_PYTHON` on the PC side, because it is not forwarded (F23).
4. **The Hermes environment.**
   - `/etc/hermes` holds no `config.yaml` or `.env`.
   - `HERMES_MANAGED_DIR`, `HERMES_SAFE_MODE` and `HERMES_ENABLE_PROJECT_PLUGINS` are unset in the lane (F5).
   - `HERMES_HOME` is unset or `~/.hermes`, so the helper, pc-lane.sh and `hermes -p` resolve the same profiles directory.
5. **The source profile's values.**
   - `compression.enabled` is truthy by `_cfg_flag` (true, 1 or yes) (F1).
   - There is no `fallback_model`.
   - `auxiliary.compression` has no provider other than auto, and no `base_url`, `api_key` or `fallback_chain`.
   - `plugins.enabled` is a list of strings (F6).
   - `plugins.disabled` holds no `${…}` (F7).
6. **The source `.env`.** Scan it for names only, with dotenv's own parser, for any `LCM_*` or `TIKTOKEN_CACHE_DIR` in any spelling (F4). Never read its values.
7. **The plugins directory.** The lane profile holds exactly one manifest for `hermes-lcm-x`, and its path resolves to `~/lcm-x`. There is no `plugin.yml`, `plugin.json` or nested copy (F3).
8. **The launch log.** It shows the plugin registering context engine `lcm-x` and "Using context engine: lcm-x". It shows no "not loaded", no fallback to the compressor, and no compat warning.
9. **The tools.** The 12 tools are absent from the lane's tool list.
10. **The store.** `<profile>/lcm.db` holds summary (compaction) rows for the lane's session, not only ingestion rows. A compaction must actually run.
11. **Egress.** An egress watch shows every compression call going to OmniRoute (127.0.0.1:20128) only. There is no discovery-chain call and no fetch from openaipublic.
12. **Off on the PC.** One off-mode lane's config bytes equal what the parent helper writes for the same source.

## 6. What I reproduced, what I read statically, and what I skipped

**Reproduced** through the real scripts at the PIN:
- every gate
- the item 1 and 2 differentials
- the lock variants
- the (a) to (d) shapes and sources
- the dotenv spellings, with the real python-dotenv 1.2.2
- the real tiktoken wheel and tokenizer
- the secrets paths
- the e2e runs (the real pc-lane.sh and the real helper, with a labelled fake hermes)
- 12 existing mutants and 18 new ones, plus their discriminators
- the YAML parser parity, with the real PyYAML 6.0.3 wheel

**Read statically only:** everything inside Hermes and LCM-X (run-time load, `_cfg_flag`, discovery, the managed scope, routing), and the S0-11 mechanism.

**Skipped, and why:**
- the whole of `test_vendored_manifest.py` (the brief forbids it)
- anything on the PC (no bridge, by rule)
- running Hermes or LCM-X code (by rule)
- the 12-tool classification, which I reviewed but did not re-derive

## 7. Evidence and cleanup

**Kept** (360 KB under `$S`):
- the logs in `$S/logs/`
- the drivers in `$S/diff/`: `diff_lp.sh`, `diff_pl.sh`, `lcmfx_lib.sh`, `lock_variants(_m).sh`, `shapes.sh`, `sources.sh`, `dotenv_shapes.sh`, `secrets.sh`, `e2e.sh`, `e2e_default.sh`, `off_src.sh`, `mv_disc.sh`, `realwheel.sh`, `compat_scan.py`
- `$S/mut/vrun.py`, which holds the MV rows and reuses the driver's plumbing

**Removed:** the worktree (`git worktree list` shows 0 vh1a entries), the clones, the wheels, the fixtures and the transcripts. No process of mine is running.

**To re-run:**
1. `git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add -q --detach $S/pin 42a4a1dd93b13a6e19554cb19799d6fcd6f2fb38`
2. `mkdir -p $S/parent && git -C /home/user/agent-factory archive 42a4a1d~1 harness-ports scripts upstream.lock.yaml | tar -x -C $S/parent`
3. `mkdir -p $S/mut/v && python3 $S/mut/vrun.py $S/pin $S/mut/out emit <MV id> $S/mut/v/<MV id>.sh` (MV21 goes to `MV21-pc-lane.sh`)
4. `python3 $S/mut/vrun.py $S/pin $S/mut/out run <ids>` for the suite verdicts.
5. Then any of the drivers above.