# K2-RS: the builder's report of record (task #353, K2 RE-SCOPE, D-117)

> **Coordinator note (2026-09-30 14:2xZ).** The builder's hand-back, saved verbatim below (the K2 builder resumed, a
> sandbox code-implementer; harvest run s-20260930T141831Z-f0560b: 2,093 assistant records over the lane's life, every
> one claude-opus-5-5, 0 refusal stops; hand-back sha256 prefix 16ecf706966a). One edit to the verbatim text: its line
> on origin cites `d20e71f`, the coordinator's local id before the push rewrote it, now annotated in brackets with
> origin's ebc45c5. The landing: `tasks/briefs/jev-trim/K2-RS.patch` (sha256 db5904b4…) applies at HEAD, since no commit
> after the PIN 631dc86 touched its five files, and the five files match the builder's table (sha256 and line counts).
> Not landed: the registration patch (`K2-registration.patch`, unchanged). Registering the hook is the owner's call,
> after the verify; the builder's NOT done items 1, 2 and 4 are its steps (register, regenerate the manifest's
> `.claude/` row, build the code map and one file-pack build at HEAD first). Status: GATED-PENDING-VERIFY until
> VERIFY-K2-RS. For the verify: the builder rewrote its deliverable once after its own self-attack (a build in flight
> leaked P2; two builds could restore a byte-identical record), so the final bytes' marker record, `still()` and the
> record id are new and need a hostile pass. The graph sections stay in the pack file with no reader (item 3 gives
> their cost). The lane reports three top-level `cd` calls (the AF-AP-249 form) with no effect.

---

## K2-RS: K2 RE-SCOPE build (task #353, D-117, contract rev 5)

Written 2026-09-30 14:1xZ. PIN 631dc86.

**TL;DR:** The deliverable is `/home/user/agent-factory/tasks/briefs/jev-trim/K2-RS.patch`.
- sha256 `db5904b424f55c6250ba1cb9c34aa6730e13e06e91d30e6946272531afbaf39b`, 2892 lines, 5 files (998+, 1142-).
- `git apply --check` at a clean PIN worktree: rc=0.
- Every gate is green and all 9 driver mutants are KILLED (the brief's 6 plus 3 more).
- **LOUD: the deliverable was rewritten once before this hand-back.** My self-attack found two holes in the first version (cc1e97de…, 2745 lines, never handed back) and one isolation defect in my own new test. All three were reproduced red, fixed and proven green. Both states are below.

### Premise
- `bash scripts/premise_block.sh` from the main tree gave IDENTICAL output, sha256 7e20599b86def1bf, at 11:0xZ, at 13:1xZ and at 13:5xZ.
- Origin moved to d20e71f [coordinator: the pre-push id of origin ebc45c5] during the lane. `git log 631dc86..HEAD -- <boundary + hook/installer files>` is empty.
- The brief's set ids were recomputed locally with pc_suite's own `set_id` formula (no bridge). They match: db64e610236b, 395f8af3a0ce, 2415789b9582.

### Evidence per contract item ([V] verified, [I] inferred, [A] assumed)

**Item 2, condition (a): symbols from the committed blob [V]**
- How it works: `codemap._committed` (codemap.py:685) runs one `git cat-file --batch` on the blob that BLOBS.txt names. `_ast_symbols(data)` (:590) parses it, and the pack records `symbols_from: "ast"` (:768). Other languages get no symbols.
- The reader drops a code part whose symbols did not come from ast (filepacks.py:671, skip `symbols`).
- Tests:
  - checks committed-symbols (in both files) and untracked-file;
  - `test_a_shell_file_gets_no_symbols`;
  - `test_graft_symbols_never_reach_a_pack_with_the_real_code_map_refresh[real|symbols-from-graft]`;
  - `test_untracked_since_build_with_the_real_code_map_refresh[real|pack-of-the-working-copy]`;
  - legacy-symbols.
- Driver: the mutants symbols-from-working-copy and symbols-from-graft are KILLED.

**Item 3: the callers-and-tests surface is gone [V]**
- No caller, test, callers total, risk line or impacted count reaches the model.
- What stays: the symbol entry; registry rows (`_screened`, filepacks.py:624, shows a row only when both screen blobs equal BLOBS.txt's); P2.
- Checks no-graph-text and no-graph-lines. Driver mutant caller-line-restored is KILLED.
- **Kept, but no reader shows them:**
  - What: the graft, GitNexus and crg sections in the pack file, `caller_files` (read only by `widen`, codemap.py:841), `_moved`, `_join`, `widen`, `wait_for_graphs`.
  - Why: they are L2a's refresh contract with the hook.
  - Cost, from the post-commit refresh log (74 runs): wait median 101 s, p95 295 s, max 546 s. Build median 3.5 s, p95 119.7 s. Wait+build median 113.1 s, p95 379.3 s. An AST-only build takes 0.40 s for 133 files.
  - Effect: after a commit changes a file, its code part is withheld for that long (skip `blob`).

**Item 4, condition (b): nothing unless the build's tree is HEAD's [V]**
- The tree check:
  - `Packs.current()` (filepacks.py:538) compares BUILD.json's `tree` (it must match OBJECT_RX) with `git rev-parse --verify -q HEAD^{tree}` (`_rev`, :553, HEAD_TIMEOUT=2, resolved once per call).
  - It runs before both parts (:709).
  - Trees, not commits. An unresolvable HEAD gives nothing (head-unresolved).
- New this round (the self-attack fix):
  - `_build` first replaces BUILD.json with `{"building": true}`, which names no tree (:1099). This happens before `_clean` and before any pack write (:1101).
  - The final record carries `"id": os.urandom(8).hex()` (:1121).
  - `Packs.still()` (:524) re-reads BUILD.json after both parts. `entry` drops everything if the bytes changed (:717).
- Hook cost: 50 calls each, interleaved, through the registration's command (sh, then hook_context.py, then `filepacks.py hook`), a Read of scripts/codemap.py, final bytes:

| | wall ms median / p95 | hook ms median / p95 | bytes injected |
|---|---|---|---|
| mine | 99.6 / 116.7 | 14.4 / 18.9 | 1098 |
| PIN | 91.9 / 115.4 | 7.5 / 10.5 | 1182 |

- The tree check alone (a git subprocess) is 2.3 / 3.0 ms.
- In process: the check is 2.37 / 2.80 ms. Check + touched + plan is 4.30 / 5.55 ms, against 1.38 / 1.54 at the PIN.
- Caveat: in the cost env the PIN's code map built 0 symbols (graft not on the restricted PATH). Its 1182 bytes are graph lines, not symbols.

**Item 5: class tests through the both-patches tree's real hook [V]**
- `test_a_reset_shows_nothing_through_the_real_hook[real|tree-check-off]` (test_filepacks.py:2087; `reset_scenario` :2002) uses the real patched post-commit hook and the registration's command spelling.
- Canaries: a new def in alpha, a new file rst.py, and a ledger line naming beta (the P2 shape).
- After `reset --mixed` and after `reset --soft`: 0 bytes, and every record says `tree`.
- Leak control (tree-check-off): every canary, P2 included, reaches the model after each reset.
- A same-tree move (`commit-tree` + `update-ref`) keeps the packs.
- (a): uncommitted and untracked symbols never show; the control shows a committed symbol does (above).
- The round 1–4 checks still in the file (58 of today's 68) pass. The removed ones are listed below.

**Item 7: mutants [V]**
- Driver method: control first (11 passed in 54.46 s), bytecode off, `__pycache__` cleared per mutant, each anchor found exactly once and compiled. A kill counts only on the named `E` line.
- All 9 KILLED on the final bytes:
  - tree-check-off
  - commits-not-trees
  - symbols-from-working-copy
  - symbols-from-graft
  - caller-line-restored
  - p2-outside-the-check
  - no-building-marker
  - record-not-rechecked
  - record-without-id
- In-test: 90 MUTANTS and 2 CM_MUTANTS across 68 checks, each killed with its message. `test_every_check_has_a_mutant_and_every_mutant_compiles` is green.

**§7 items**
- Items 1 and 2: see contract items 5 and 2 above.
- Item 4: the tests line is gone, so no "none found" can show.
- Item 5: no graph note or graph state is rendered.
- Item 6: the post-commit patch comment is updated (the build records commit and tree; the hook shows nothing while HEAD's tree differs; the patch lands with or before the registration; one build at HEAD first). The hook commands are unchanged; the patched hook's blob is 004992c. This round's record changes (the marker and the id) leave the comment accurate, so I did not re-edit it.
- Item 8: the registration patch is unchanged (1dc53684…). `hook_count(our_hooks)` = 15 (ls_req 3, filepacks 2); the PIN's is 13. NOT registered.
- Items 7, 10 and 11 are yours and the owner's.

### Files (PIN, then final; all in the patch except the registration patch, which is unchanged)

| File | PIN sha, lines | Final sha256, lines | Lines over 120 (PIN → final) |
|---|---|---|---|
| scripts/filepacks.py | 31606f07fa64c948, 1226 | be82ab16c83a1402fe89f1ec9ed81f6988bd0dfc4e798cae89828f33f87be0ba, 1260 | 5 → 5 |
| scripts/codemap.py | e1a56e0b0cf8e8ed, 1271 | 15f41cb1400f34f273260bb0a06c79e3ab44b2c7803731eae2c340b314607bde, 1142 | 5 → 5 |
| tests/test_filepacks.py | 32d3bcd4e7935ed7, 2181 | 0ae34b5c13aaa7d6bb2493cc71111b2f428978c5d6a9407b4deb98baf1e7f5a4, 2176 | 23 → 22 |
| tests/test_codemap.py | d8002fbbeb8217ae, 1097 | 08e48d868a92cedb6241004e503745691a40befc7c939c4f70c796b299aa1610, 1050 | 8 → 7 |
| tasks/briefs/jev-trim/K2-post-commit.patch | 71ba4c2c0cec81ab, 26 | 3fe1a775b7203205858304c65855c96fbea4a248ddf581c0bb61f99f67d664b3, 29 | — |
| tasks/briefs/jev-trim/K2-registration.patch | 1dc53684…e532e, 298 | unchanged | — |

- pyflakes: clean on all four .py files.
- GitNexus impact: `_build` LOW (3 impacted), `entry` LOW (4). `Packs.record` and `Packs.still` do not resolve (UNKNOWN, 0), so I confirmed by text search: `record()` is called only in filepacks.py (still, commit, current) and `still()` only at :717. No other script reads BUILD.json.
- Copies of the final files: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k2-lane-353/rs/final2/`.

### Gates (pasted from scripts/test_summary.sh; `--basetemp` under the scratch dir, outside every work tree)
- **test_filepacks, `1 files set=db64e610236b`, final bytes:**
  - "175 passed in 174.10s (0:02:54)"
  - "175 passed in 180.71s (0:03:00)"
  - On the bytes before the cbm test fix: "175 passed in 136.21s (0:02:16)", "175 passed in 144.75s (0:02:24)".
- **codemap + system1, `2 files set=395f8af3a0ce`:** "204 passed in 297.51s (0:04:57)". This ran on the final filepacks.py, codemap.py and test_codemap.py; test_filepacks.py is not in this set.
- **Both-patches tree (PIN + db5904b4 + both patches; its K2-RS part hashes to db5904b4):**
  - session_hooks + search_intercept, `2 files set=2415789b9582`: "144 passed in 56.72s".
  - Manifest `-k test_committed_manifest_matches_fresh_generation`: "1 failed, 56 deselected in 1.41s". This is the expected drift: line 20, `.claude/ (kit-adapted)`, committed aab0f94a… against generated 9a712fa7…, caused by the registration patch's `.claude/settings.json`. Without the registration it passed ("1 passed, 56 deselected in 2.46s", measured before the fix; the fix touches no manifest path [I]).
  - test_filepacks: "175 passed in 175.28s (0:02:55)" (final bytes).
  - codemap + system1: "204 passed in 304.43s (0:05:04)".
- **Collected tests:** test_filepacks 188 → 175; test_codemap 68 → 63.

### Found and fixed after the first deliverable (both states)
1. **A build in flight leaked P2 [V].**
   - Before: `_build` wrote the packs before BLOBS, TRACKED and BUILD.json, and packs carry no build id. While a build of Y ran after a reset back to N's tree, the record still said N, so Y's lines showed.
   - Reproduced red on cc1e97de: build-in-flight failed with "a byte HEAD's tree does not hold reached the model (a build in flight): 'filepack scripts/beta.py @5aefb62: ledger 1 · commits 1 …'" (the canary was in the ledger line). record-rechecked leaked the code part.
   - Fixed by the marker record and `still()`. It also makes a crashed build fail closed.
   - The cost: the hook shows nothing while any build runs (about 2.6 s at idle priority).
2. **ABA [V].** Two builds between the reader's two record reads (another commit, then the same commit again) could restore byte-identical records (same commit, counts and integer ms). Fixed by the random id. Check record-rebuilt holds the module's clock at 0 ms and runs both builds around the P2 read. Its controls prove the part read held the canary and that the records differ only in the id. Mutant record-without-id is KILLED.
3. **AF-AP-251 in my own reset test [V].**
   - Before: the real post-commit hook's cbm index met your daemon. The fixture's cbm-index.log said "CBM could not start because the active account daemon uses a different cache directory". The hook tolerates this, so the test was green.
   - Fixed with a private short `CBM_RUNTIME_DIR` (mkdtemp under /tmp, removed in `finally`) and a guard on the log.
   - Red without the private dir (the guard's message), green with it.

### Removed tests, by name (collect-only diff, PIN against final)
- **test_filepacks checks:** blob-tie, caller-files-missing, caller-path-newline, not-indexed, older-p2-stale-code, same-file-stale, sourceless-symbols, stale-symbol-graph, tail-path-caller, tests-graph, untracked-callers.
- **test_filepacks tests:**
  - test_negative_control_the_code_map_without_its_left_out_total
  - test_stale_symbol_graph_with_the_real_code_map_refresh[tracked-real|tracked-stale-symbol-graph-shown|untracked-real|untracked-stale-symbol-graph-shown]
  - test_untracked_since_build_with_the_real_code_map_refresh[no-blob-check]
  - test_untracked_text_never_reaches_a_pack_through_the_real_hook[real|blob-tie-off]
- **test_filepacks mutants (26):** blob-key-substring, blob-tie-by-path, blob-tie-off, blobs-newline-unguarded, caller-files-ignored, callers-by-crg, callers-total-always-dropped, callers-total-kept, clause-not-indexed-passes, committed-filter-uncalled, files-not-list-ok, fresh-unless-stale, indexed-hash-skipped, keep-rel-any-graph, legacy-pack-trusted, missing-blob-accepted, same-file-names-from-stale-graphs, sourceless-symbols-shown, stale-gitnexus-total-stands, stale-symbol-graph-shown, symbol-graph-always-graft, tests-by-gitnexus, tests-rel-unfiltered, total-kept-on-drop, untracked-callers-kept, untracked-tests-kept.
- **test_codemap:** checks provenance, provenance-record-lies, provenance-same-file; test_shell_file_gets_crg_symbols_and_says_what_is_not_parsed (replaced by test_a_shell_file_gets_no_symbols).
- **test_codemap mutants (10):** builder-callers-unfiltered, builder-indexed-hash-skipped, builder-missing-blob-accepted, builder-names-unchecked, builder-path-not-blob, builder-same-file-fresh-ignored, builder-tests-unfiltered, builder-total-kept-on-drop, builder-working-bytes, unknown-read-as-none.

### NOT done
1. Not registered. Registering is yours.
2. The vendored-manifest regeneration for the registration's `.claude/settings.json` is yours.
3. The graph sections are kept, not removed (cost above).
4. Before registration: run `codemap.py build --all` (packs need `symbols_from: "ast"`) and then one `filepacks.py build` at HEAD (BUILD.json needs a tree and an id). Until then the hook shows nothing.
5. `_rev` does not scrub `GIT_DIR`, `GIT_WORK_TREE` or `GIT_INDEX_FILE` [A: the harness sets none].
6. The CLI dev tools `codemap.py lookup` and `demo` are not checked against (a) or (b).
7. §7 items 7, 10 and 11.

### DISCREPANCIES
1. The deliverable was rewritten (cc1e97de, then db5904b4), as above.
2. Your note said my gate files should not meet the cbm daemon. My reset test did, through the real hook's background cbm index. It is fixed.
3. Three top-level `cd` breaches (AF-AP-249 form). None had an effect, but the form is forbidden:
   - 12:0xZ: `cd $S5/wt 2>/dev/null;`
   - 12:3xZ: `cd /tmp 2>/dev/null; true`
   - 14:1xZ: `cd /home/user/agent-factory 2>/dev/null;` before the GitNexus subshell.
4. `stack.py gate mode=plan` (run in my worktree) logged, by design, into the MAIN tree's `.jev/stacks/s-20260930T122358Z-0e3222/` (7 files) and one runs.jsonl line. I did not delete them.
5. Driver history: runs 1–3 were invalid because of parser bugs (pytest 9 prints `FAILED <node>` with no message; long names get a 2-underscore header; the aggregate compare was wrong). Run 4 was the pre-fix 6/6. The final runs are 9/9.
6. The worker restart at about 12:57Z killed gate 1b (exit 137). I re-ran it.

### Self-attack: how could a pack still show a byte HEAD's tree does not hold?
- **Closed:** a build in flight, and ABA (above).
- **Residuals:**
  - HEAD moves after the check but before the model reads the output. This is inherent to a hook.
  - `GIT_*` variables in the environment could steer the check [A].
  - `.jev` is the trust root: anyone who can write the state can plant a record (by design, F6).
  - Object-id or 64-bit id collisions [A].
  - After a same-tree move, P2's commit subjects and its @sha come from the build's history. They are history, not tree bytes (by design: trees, not commits).
  - Edit placement uses working-copy line numbers, so it can pick the wrong committed symbol. It never shows uncommitted bytes.
- **The three likeliest ways my change is wrong, and how I ruled each out:**
  - **Tests green without the real hook:** the class tests run through the real patched hook and the registration command, with leak controls that show every canary.
  - **Kills for the wrong reason:** the control ran first, the parser has its own control, every anchor occurs exactly once and compiles, and kills match on the named `E` line.
  - **The fix is racy:** the marker is the first write, before any pack change; `still()` runs after both parts and before any output; in-process tests land a build at each point in between; the id closes ABA.

### Cleanup and rules
- Every worktree is removed (wt, wtmut, wtpin, wtboth, wt2, wtmut2). The `/proc` scan shows only pid 32217 (your cbm daemon; not mine; untouched). No `/tmp/cbmr.*` left.
- No hook registered. No outward action. No PC bridge. No secret read.
- The shared tree shows only `?? tasks/briefs/jev-trim/K2-RS.patch`.
- S1-RATE given: s1-fcbe35aa.
- Scratch log: `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k2-lane-353/rs/PROGRESS.md`, with logs under `logs/`.