# VERIFY-K2 round 2 report (task #353)

> **Coordinator note (2026-09-29 16:0xZ):** extracted by `scripts/stack.py harvest` (run s-20260929T160439Z-21bec8; hand-back sha256 prefix 897bbddfd017, 32,876 characters). Served model: claude-opus-5-5 on all 419 assistant records, 0 refusal stops, 1 compaction. `report_lint`: 1 OK and 3 MISS, none of substance: `scripts/hooks/post-commit:170` is the right line (the `codemap.py refresh` command; the lint wants a token copied from it), `:172` is a line number inside `git apply`'s own error text, not a citation, and `tests/test_filepacks.py:1206` is a PIN line (the report says HEAD's lines are 3 lower). One local id: "Origin has since moved to 2f5481d" names the shared tree's local HEAD at the time; origin was at 15a326b, and the push rewrites 2f5481d. The gate recommendation is NOT-READY on B1, B2 and B3. The coordinator's disposition: B1 and B2 put untracked text in front of the model, core-blocking under D-034; B3 blocks landing the post-commit patch (CI would go red). K2 round 2 was D-031's one focused repair (after VERIFY-K2 round 1's F1), so a round 3 waits on the owner's word; the hook stays unregistered and the landed round-2 code stays inert.

## Round 2

Written 2026-09-29 from 2026-09-29T16:00:11Z (`date -u`).
This is VERIFY-K2 round 2 (task #353), by the fresh verifier (D-109). PIN: origin f605913 ("K2 round 2 landed (task #353; GATED-PENDING-VERIFY)…"). Brief: `/home/user/agent-factory/tasks/briefs/jev-trim/VERIFY-K2-R2-RESUME-brief.md`.

### Gate recommendation

**NOT-READY.** Three findings meet the whole blocking predicate: B1, B2 and B3.
- **B1:** a tracked file's code part shows an untracked file's function name and path. This happens on the healthy pipeline: the real patched post-commit hook, fresh graphs and a fresh build.
- **B2:** the blob check does not tie a code pack's symbols to its blob. When the build is stale and the symbol graph indexed other bytes, an untracked file's function name and a secret-shaped default argument reach the model.
- **B3:** if `K2-post-commit.patch` lands as delivered, 3 tests in `tests/test_filepacks.py` fail. CI runs that file.

All three reproduce at the PIN through the production code. One part is static only: that CI goes red on B3. I did not run CI. `.github/workflows/stage0-ci.yml:46` runs `python -m pytest tests/`, and the 3 tests have no skip marker.

B2's event order is arranged by the probe; every mechanism in it is production code. If the coordinator rules that order out of scope, B1 and B3 still block.

### Summary

- **What holds:**
  - F1's base shapes (probe_p6, with and without the patch).
  - F2: 0 of 40 stalls.
  - F3: linear, 300 ms at 3,000 pairs.
  - F4/F5: 60 right, 25 misses, 0 wrong.
  - Every mutation claim.
  - The registration patch: 137 passed, "installed 9" and the older-spelling test.
  - The manifest after regeneration: 57 of 57.
  - A quiet session start.
- **What fails:** B1, B2 and B3.
- **Test gaps:** 7 mutants survive all 50 of the builder's checks. One of them, `blob-fail-open`, guards the exact state the hook meets at registration: the live `.jev/filepacks` has no BLOBS.txt.

### 1. Premise

- At 13:21Z I re-ran every `$` line from `/home/user/agent-factory`. The output is byte-identical to the brief's block: the diff is empty and both files hash to sha256 4d8cbbc480a26960.
- Files: `…/vk2r2/premise_cmds.txt`, `premise_expected.txt`, `premise_actual.txt`.
- Origin has since moved to 2f5481d. Only one commit touched a K2 file: d414a85 ("CI run 1145 fix: the filepacks no-word-cap control sized for CI's faster runner…", 14:55:38Z).
  - In `tests/test_filepacks.py` it changes only `check_linear_parse` (3,000 to 6,000 pairs).
  - It also changes `.claude/skills/anti-hollow-green/SKILL.md` and `sandbox-kit/VENDORED-MANIFEST.md`.
  - Unchanged since the PIN: `filepacks.py`, `codemap.py`, both patches, the post-commit hook, the installer and both settings files.
- At the end of my run, `grep -c filepacks` still gave 0 in `.claude/settings.json`, `scripts/install_session_hooks.py` and `/home/user/.claude/settings.json` (rc 1).

### 2. Finding inventory (no severity filter)

Evidence levels: [R] reproduced by me; [S] static reading; [H] hypothesis, not reproduced.

**1. B1 — BLOCKER. Untracked callers reach the model through a tracked file's code part.** [R, 3 runs, the last one logged]

- **What happens:**
  - Setup: `scripts/alpha.py` is tracked. An untracked `scripts/caller_new.py` calls its `helper`, and a tracked `scripts/caller_trk.py` is the control.
  - A commit of an alpha change runs the real patched post-commit hook. The hook re-indexes graft, GitNexus and code-review-graph, refreshes the code map, and builds the file packs.
  - The pack's blob equals HEAD's, and every graph reads `fresh`.
  - An Edit in `helper` through REG_PRE then injects this line (`<UNT>` is the untracked file's function name, a canary made at run time):
    `callers 5 (2 in tests): <UNT> scripts/caller_new.py:4 · <TRK> scripts/caller_trk.py:4 · __init__ scripts/alpha.py:10 · +2 more`
  - A Read does not show the callers line.
  - The pack's `caller_files` also lists `scripts/caller_new.py` and `tests/test_new_u.py`.
- **Why:**
  - GitNexus indexes the working tree, untracked files included.
  - `_gitnexus` (codemap.py:446) writes the callers `sample` (:488). `_code_part` (filepacks.py:568) checks only the pack's own blob (:601). `edit_context` then renders the sample (codemap.py:844-846).
  - Nothing filters callers or tests through TRACKED.txt.
  - The builder listed this as unmeasured (NOT done 5; the residual of its self-attack 1).
- **Contract:** item 1 names this shape ("the callers sample naming an untracked caller"). D-034 applies.
- **Canonical path:** yes. The real patched hook, the real graphs and the real wrapper, at the PIN.
- **Material effect:** untracked text (a function name and a file path) is in front of the model.
- **Reproduction:** `VK2_WT=<detached worktree at f605913> python3 /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/probe_callers2.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2 real`. The output is in `logs/b1-callers-real.txt`.
- **Discriminator:** the same command with `fixed` (a scratch filter by TRACKED.txt), output in `logs/b1-callers-fix.txt`. The untracked name and path are gone, and the tracked caller and test remain.
- **Live exposure today:** the live code map's 233 packs name no untracked caller (`live_callers.py`). The hole is latent. It opens as soon as an untracked file in the tree calls tracked code.
- **Suggested fix:**
  - Keep only the callers and tests whose file TRACKED.txt lists. Do this in `_code_part`, or in the readers when a pack is handed to them.
  - Recount or drop the total. Under my scratch fix the line still reads "callers 5 (2 in tests)", so the count still includes the untracked caller.
  - Add a check through the real patched hook, and a mutant that removes the filter. `probe_callers2.py` can serve as the template.

**2. B2 — BLOCKER. The blob check does not tie a pack's symbols to its blob.** [R, 3 runs, the last one logged]

- **Shape (a), an untracked file:**
  1. Build the file packs. TRACKED.txt and BLOBS.txt list `scripts/gamma.py` with blob B0.
  2. Run `git rm --cached` on it and commit (c9). No file-pack build follows, as after a failed or stalled build.
  3. Write untracked text into the file: `def leak_<C>(token="<C>-arg")`.
  4. Run `graft build`.
  5. Restore the file's bytes to B0.
  6. Run the real `codemap.py refresh --commit c9 --lock-dir … --graphs graft --wait 8 --grace 2 -- scripts/gamma.py`.
  - The refresh logs "graphs not fresh in the packs: graft stale". It still writes a pack whose blob is B0 (equal to BLOBS.txt's) and whose symbols carry the canary.
  - REG_PRE then injects the canary, with no `code_skip`, on Edit (575 B), Read (454 B) and `cat` (454 B). The Edit line:
    `codemap scripts/gamma.py:2 — function leak_<C> L1-2 · def leak_<C>(token="<C>-arg")  [pack .jev/codemap/scripts/gamma.py.json]`
- **Shape (b), a tracked file** (the `sg-tracked` probe):
  - Append the canary to tracked alpha.py, run `graft build`, revert with `git checkout --`, then refresh. The Read shows the reverted edit's function name.
  - By D-034's letter this alone is not untracked text, so on its own I would rate it FOLLOW-UP.
  - It does falsify the builder's self-attack 1 ("a match means the pack describes a blob committed at that commit"). The same fix closes both shapes.
- **Why:**
  - The pack's `blob` is the hash of the working file at refresh time.
  - Its symbols come from `graft skeleton --json --no-refresh` (codemap.py:305), which answers from the bytes graft last indexed.
  - `wait_for_graphs` (codemap.py:222) treats this case as normal: "the refresh goes on with that graph marked stale in the packs".
  - The pack records it (`symbols_from`, `instruments.graft.graph == "stale"`), but `_code_part` never reads that mark.
- **Production preconditions for shape (a):**
  - TRACKED.txt and BLOBS.txt are older than the commit that untracked the file. This is the case the blob check exists for; the builder's own test docstring says "the blob check is the second guard, for a failed or stalled build".
  - The graph indexed other bytes than the refresh read. That happens after a skipped or failed re-index, or when the bytes change during the post-commit job while graft's MCP re-indexes on every query.
- **Contract:** item 1, "F1 is closed whatever the build did". D-034 applies.
- **Canonical path:** yes. It uses the real refresh CLI (the post-commit hook's command, `scripts/hooks/post-commit:170`, with shorter `--wait`/`--grace`), real graft and the real REG_PRE, at the PIN.
- **Material effect:** untracked text, including a secret-shaped default argument, is in front of the model.
- **Reproduction:** `VK2_WT=<worktree at f605913> python3 …/vk2r2/probe_f1b.py …/vk2r2 sg-untracked`. The output is in `logs/b2-sg-untracked-real.txt`.
- **Discriminator:** `VK_FIX=freshgraph` on the same command, output in `logs/b2-sg-untracked-fix.txt`: 0 canary bytes and `code_skip: stale-graph`.
- **Shape (b) evidence:** `probe_f1.py … sg-tracked`, reproduced before the compaction. Its output was not saved to a log.
- **Suggested fix:**
  - After the blob check (filepacks.py:601-602), withhold the code part when the pack's symbol-source graph is not `fresh`. My scratch fix is three lines and records `code_skip: stale-graph`.
  - Add a check for both shapes and a mutant that drops the clause.

**3. B3 — BLOCKER. The delivered post-commit patch fails its own tests once it lands.** [R]

- **Result** in a worktree at the PIN with both patches applied (wtreg): `1 files set=db64e610236b` / `pytest-exit: 1` / `pytest-summary: 3 failed, 126 passed in 109.56s (0:01:49)`.
- **Failing tests:**
  - `test_untracked_since_build_with_the_post_commit_patch[real]` and `[no-blob-check]`: `error: patch failed: scripts/hooks/post-commit:172` / `error: scripts/hooks/post-commit: patch does not apply` (tests/test_filepacks.py:1206).
  - `test_negative_control_the_hook_without_the_patch_runs_no_build`: `Failed: DID NOT RAISE AssertionError` (:1263).
- **Why:**
  - `hook_dir` (:1197) copies the repo's own `scripts/hooks/post-commit` (:1202) and runs `git apply` with the patch on it (:1204).
  - After landing, the hook already carries the patch, so the apply fails.
  - The "hook without the patch" is now the patched hook, so the negative control's build runs.
- **Contract:** item 6, "What else breaks". Also the repository's CI gate (AF-AP-126: `push_clean` refuses while the branch's CI is red).
- **Canonical path:** yes. The delivered patch file, applied with `git apply`, and the test file that CI runs. That CI runs it is static: stage0-ci.yml:46, and no skip marker on these tests.
- **Material effect:** CI goes red on landing, and pushes are refused until a fix lands.
- **Control:** the same file on the unpatched PIN passes: 58 + 71 = 129 passed (`logs/gate-p1.txt`, `logs/gate-p2.txt`).
- **At HEAD** [S]: d414a85 does not touch `hook_dir` or these tests, so B3 holds there too.
- **Suggested fix:**
  - Take the unpatched hook from a fixed commit (`git show f605913:scripts/hooks/post-commit`), or apply the patch only when the hook lacks the build step.
  - Keep the negative control on the unpatched bytes.
  - Run the whole file in a patched tree.

**4. FOLLOW-UP. Seven mutants survive all 50 of the builder's checks.** [R]

- **The seven:** `blob-fail-open`, `grep-long-value-dropped`, `grep-attached-ignored`, `frame-close-any`, `dq-sub-not-opened`, `grep-double-dash-dropped` and `files-max-off`.
- **Run:** `mutdrv3.py` with `VK_BUILDER_ONLY=1`, after a 60/60 control. Output: `logs/mut3-builderonly.txt`.
- **My killers** (all in `mutdrv3.py`): `n2_blobs_missing`, `n2_grep_long_value`, `n2_grep_attached`, `n2_script_paren`, `n3_dq_substitution`, `n3_grep_double_dash` and `n3_files_max`.
- **Builder checks still kill two:** `words-cap-2` and `sep-ends-ignored`.
- **Contract:** item 5.
- **Material effect:** test gaps, not a production defect. But `blob-fail-open` guards the registration state: the live `.jev/filepacks` is round 1's 7db59b9 build with no BLOBS.txt, and no builder test fixes today's behaviour there (every code part withheld).
- **Fix:** port the seven checks, with their mutants, into `tests/test_filepacks.py`.

**5. FOLLOW-UP and INFO. Survivors when graded on all 60 checks.** [R]

- **`pack-not-handed` (FOLLOW-UP):** the readers re-read the pack from disk instead of using the checked one.
  - Run in sequence, the two are the same. The builder's reason for handing over the pack is a swap between the check and the read, and no test covers that.
  - I did not try the swap, so the claim is UNVERIFIED.
- **`blob-field-optional` (INFO):** a pack without a `blob` field crashes closed. The exception is caught and nothing is injected.
- **`blob-kind-any` (INFO):** it differs only for a gitlink row, and the fixture has none.
- **Equivalent survivors (INFO):**
  - Round 1's four: `build-file-kept`, `clean-keeps-links`, `cd-dash-followed` and `commit-dedupe-dropped`.
  - `blobs-not-kept`: `_clean` runs just before BLOBS.txt is rewritten.

**6. FOLLOW-UP. The parser's remaining wrong files.** [R, strace oracle]

Every shape below was wrong at round 1 too, and each injects a tracked file's pack: a mislead, not a hole.
- **Heredoc under ssh with a command:** `ssh -o BatchMode=yes -o ConnectTimeout=1 nosuchhost.invalid bash -s <<'EOF' / cat scripts/a.py / EOF` gives the local scripts/a.py (NOT done 4). The builder's `ssh pc <<'EOF'` form is right.
- **cd scoped too wide:** `cd deploy | true; cat README.md`, `cd deploy & cat README.md` and `f() { cd deploy; }; cat README.md` give deploy/README.md, but bash reads README.md.
- **cd missed:** `command cd deploy; …` and `builtin cd deploy; …` give README.md, but bash reads deploy/README.md.
- **case patterns:** a `case` pattern's `)` inside `( )` or `$( )` is wrong in 3 forms (NOT done 4).
- **Commands that do not parse (3):** an unterminated quote, an unclosed `(`, a stray `)`. Each gives a file, but bash runs nothing.
- **Logs:** `logs/parser-c2-wt.txt`, `logs/parser-c3-wt.txt`.
- **Fix:** treat `|`, `&` and function bodies as scope ends for `cd`; accept the `command` and `builtin` prefixes; handle a heredoc after `ssh … <cmd>`.

**7. FOLLOW-UP. The code-map builder now depends on the System-1 hook (DISCREPANCY 10).** [R]

- `language()` is shared with `build_one` and now opens files through System-1's `open_regular`.
- With the System-1 hook missing or broken, a refresh whose set holds an extensionless file fails as a whole:
  - at the PIN: rc 1 and 0 packs;
  - at d812c9b: rc 0 and 2 packs.
- Item 2 asked whether the builder side is byte-identical. It is not: `language()` changed.
- The defs changed from d812c9b to the PIN are `_S1`, `_system1`, `_load_pack`, `edit_context`, `file_entry`, `language` and `lookup`. Everything else in the builder is unchanged.
- **Material effect:** availability only. The packs go stale and the blob check withholds them, so it fails closed.
- **Fix:** make the builder's `language()` fall back to a plain non-blocking open, or limit the failure to the one file.

**8. FOLLOW-UP. Stale documents.** [R]

- `docs/research/findings/jev-trim/D105-DESIGN-v1.md:281` still says "Not built: L2b" (round 1's F20; NOT done 6).
- B1 and B2 falsify line 8 of `tasks/briefs/jev-trim/K2-R2-report.md` ("F1: closed by the blob check") and its self-attack 1.
- Fix: update both in the landing commit.

**9. FOLLOW-UP (tooling, outside K2). `stack.py` writes the live `.jev/stacks/` even when run from a worktree.** [R]

- I ran `python3 scripts/stack.py gate … mode=plan` from my scratch worktree. It wrote `/home/user/agent-factory/.jev/stacks/s-20260929T141625Z-f7900b/` (8 entries) and appended 1 line to `.jev/stacks/runs.jsonl`.
- This is by design: it finds its log directory through git's common dir. I left both in place and made no further `stack.py` calls.
- The brief's list (`.jev/filepacks*`, `.jev/codemap`) was not touched. Your launch note said "the live `.jev/`", so I report the write here.
- Fix: an env override or a worktree-local log directory.

**10. INFO. F1's base shapes hold.** [R]

- `p6-real`: 0 canary bytes on Edit, Read and `cat`; 231 B of P2 lines; `code_skip=blob`.
- `p6-noblob` (the control): the canary shows on all three.
- `probe_p6b` through the real patched hook: TRACKED.txt and BLOBS.txt drop gamma, and 0 bytes are injected on all three.

**11. INFO. DISCREPANCY 8 confirmed.** [R] An uncommitted canary edit gives `code_skip=blob`. The code part returns after a commit and a build.

**12. INFO. BLOBS.txt shapes.** [R, `probe_blobs.py`]

- **Missing:** P2 lines only, `code_skip=blob`.
- **A symlink to a good copy, a FIFO or a directory:** the whole hook injects nothing. The OSError is logged (`except BaseException`, filepacks.py:793) and the call takes about 0.11 s, with no hang. This fails closed but silently: one local state change turns P1 off.
- **Edited to match a pack built from uncommitted bytes:** the code part and the canary show. This is trusted state, like round 1's P4b.

**13. INFO. A forged pack `blob` field is trusted.** [R, `logs/forge-pack-blob.txt`]

- Control: a pack built from edited bytes is withheld (`code_skip=blob`, 0 canary).
- The same pack with `blob` set to BLOBS.txt's value: the code part and the canary show.
- `.jev/codemap` is builder-written state, so this is by design. B2 shows that the builder itself writes the same kind of pack.

**14. INFO. F2 holds.** [R]

- FIFO race, N=40 per target:
  - Round-1 code: 14 of 40 and 13 of 40 stalls. Your round 1 measured 10 or 11; this is run-to-run drift.
  - Round 2: 0 of 40 and 0 of 40. Of the 40, 8 read STALE and 30 unreadable, so the race was exercised.
- `_load_pack`'s O_NOFOLLOW changes no real caller. Its callers are the codemap CLI and filepacks, and the live `.jev/codemap` holds 0 links.

**15. INFO. F3 holds; one quadratic path that predates round 2.** [R, and S for the history]

- Through the wrapper on a 1,709-pack build: 250, 1,000 and 3,000 `time cat` pairs take 133, 168 and 300 ms, and all are injected. The claim was 336 ms at 3,000.
- Round-1 code in process (the red control): 487 ms at 250 pairs, 7,736 ms at 1,000.
- The stopped verifier's 15 shapes grow about linearly: deep `$(` and `(` nesting, many frames, backticks in `$( )`, pushd chains, heredocs, ssh, unbalanced parens, eval, `grep -e` and quoted words.
- A deepening chain is quadratic through `_cd`'s normpath:
  - `cd a;`: 24 KB 146 ms, 96 KB 912 ms, 192 KB 3,208 ms.
  - `pushd a;`: 144 KB 1,245 ms, 288 KB 4,454 ms.
- `_cd` has the same normpath at d812c9b (:184-196), so this path is not new. I did not time it at round 1.

**16. INFO. F4/F5 hold.** [R]

- **The 85-case oracle:**
  - Round-1 code: 51 right, 7 wrong, 27 misses. Round 1's report said 50/7/28, so one case drifted.
  - Round 2: 60 right, 25 misses, 0 wrong, as claimed.
  - Every verdict change from round 1 to round 2 is an improvement.
- **New shapes:**
  - The stopped verifier's 50: 38 right, 9 wrong, 3 misses.
  - Its 4 `case` shapes: 3 wrong.
  - My 23: 22 right and 1 miss. The miss: `cd deploy && (cd .. && (cd deploy && cat README.md)) && cat ../README.md` loses `../README.md`.
- The wrong ones are listed in item 6.
- For execution only, the oracle replaced `ssh` and `scripts/pc.sh` words with `true`.

**17. INFO. The mutation claims reproduce.** [R]

- **Builder control** `-k "check_passes or no_reader_waits"`: `2 files set=bd8d7c79afbe` / `pytest-exit: 0` / `pytest-summary: 70 passed, 115 deselected in 201.71s (0:03:21)`.
- **Builder mutants** `-k "negative_control or every_"`: `pytest-summary: 102 passed, 83 deselected in 291.13s (0:04:51)`.
- **The 17 ported pairs** use round 1's anchors and replacements. Only two edits differ: the pack-to-path rename, and one delete turned into `if False`. The check bodies equal round 1's.
- **My grading** (`mutdrv3.py`, 60/60 control first):
  - Round 1's 31 mutants: 27 killed, 4 equivalent survivors.
  - The stopped verifier's 11: 10 killed.
  - My 15 new mutants: 12 killed.
  - `redirect-target-counted` needed a new anchor (`skip = r.end() == e`); `data-words` kills it.
- **The stopped verifier's seven interim kills all reproduce.** The name its output cut is `grep-attached-ignored`.

**18. INFO. The registration patch works, apart from B3.** [R]

- wtreg is the PIN plus both patches. The diff equals the patches byte for byte, and the patched hook's sha256 is fce110fe82d8b183.
- **Result:** `2 files set=2415789b9582` / `pytest-exit: 0` / `pytest-summary: 137 passed in 64.52s (0:01:04)`.
- **Controls:**
  - Remove the `filepacks_marker` merge rule: the new test fails with "an older filepacks spelling stayed".
  - Remove the `_fake_repo` stub: a JSONDecodeError.
  - Both files were restored byte-identical.
- **"installed 9" is right:** 9 distinct guarded scripts (8 at the PIN) and 12 commands (10 at the PIN). Only historical reports say "installed 8".
- **The rest of the 9-file gate union** (`9 files set=18b7a22259c0`):
  - `4 files set=1deaba4db93f`: 106 passed, 7 skipped. The skips are test_slopo's declared "no slopo venv".
  - `1 files set=65d0b153796b` (system1): 141 passed.
  - `1 files set=f34ec384f886` (codemap): 56 passed in 433.55s.
  - `1 files set=db64e610236b` (filepacks): 3 failed, 126 passed (B3).

**19. INFO. The vendored manifest.** [R]

- Before regeneration, `--check` fails with rc 1: drift on the `.claude/ (kit-adapted)` row.
- After `--write` in wtreg:
  - `--check` passes.
  - The row's hash moves from 214664b31ef9271d to cab4c825c03a84f9, with or without the ignored `.claude/hooks/__pycache__`.
  - `VENDORED-CLAUDE-CLASSES.tsv` is rewritten with no change.
- `tests/test_vendored_manifest.py` (`1 files set=21e700b8344c`): all 57 node ids pass. I ran them one at a time in a pytest loop, so each line is pytest's own `1 passed`, rc 0, not `test_summary.sh`.
- At HEAD the expected hash differs, because d414a85 changed a file under `.claude/`.

**20. INFO. Session start after registration.** [R for the reset; S for setup.sh and resume-heal.sh]

- `setup.sh:438` (the SessionStart hook runs it at every start and every compaction) and `resume-heal.sh:14` run the installer. So landing the patched installer *is* the registration; there is no separate step.
- At start, the `--reset` entry prunes markers idle for more than 7 days, logs one line and caches bytecode.
- It prints nothing and runs no build. Nothing else runs.

**21. INFO. Cost.** [R]

- **Latency:** 40 fresh-window Reads through REG_PRE, with bytecode cached: p50 129.1 ms, p95 163.9 ms, max 172.3 ms. All 40 injected; 39 had a code part. Round 1 was 119.0/144.1 ms. The System-1 command in the same loop: p50 107.1 ms, p95 128.2 ms.
- **Replay** of this session's transcript on the live root (1,729 packs at 15a326b; 141 windows):
  - Injections per window: median 30, p90 51, max 66.
  - Bytes per window: median 27,489, p90 49,409, max 65,781.
  - In-process entry time: p95 1.226 ms.
- **Stamps:** the wrapper adds 296 B per injection (a 26-character stamp line and a 269-character score request; measured on 5 files). That is about 8.9 KB per window at the median, 15.1 KB at p90 and 19.5 KB at the max. Each injection also asks for one `S1-RATE` line.

**22. INFO. pc.sh commands.** [R]

- 2,431 recorded main-loop Bash commands name `pc.sh`. Round-1 code injects `scripts/pc.sh`'s pack for 12 of them.
- Round 2 loses none of those and adds none.
- The stopped verifier's "2,511" came from a scope I did not reproduce.

**23. UNVERIFIED. F13 (round 1).** A pack's `@sha7` can go stale after `push_clean` rewrites commits. This stays static; I did not re-examine it.

### 3. Answers per contract item

1. **Is F1 closed whatever the build did? No.**
   - The base shapes hold (items 10-13).
   - B1 leaks through untracked callers even with a fresh build.
   - B2 leaks untracked text when the build is stale and the graph indexed other bytes.
2. **F2:** it holds (item 14).
   - The builder side is not byte-identical: `language()` changed (item 7).
   - O_NOFOLLOW changes no real caller.
3. **F3:** the parse is linear. There is no new quadratic path; one pre-existing path exists (item 15).
4. **F4/F5:** 60/25/0 reproduces. The new shapes give wrong files that all predate round 2 and name tracked files only (items 6 and 16).
5. **Mutation:**
   - The 17 checks kill the 17 mutants, and the anchors keep round 1's meaning.
   - The mutation set passes with its control run first.
   - Of the new mutants, 7 survive the builder's checks (item 4), and 3 survive all 60 checks (item 5).
6. **The registration patch:**
   - 137 passed, "installed 9" is right, and the older-spelling test is right (item 18).
   - What else breaks: 3 filepacks tests once the post-commit patch lands (B3), and the manifest until it is regenerated (item 19).
   - Session start: nothing harmful runs, but the landing itself registers the hook (item 20).
7. See §5.

### 4. Blocking predicate (D-034: a boundary hole that puts untracked text in front of the model is core-blocking)

- **B1:**
  - (1) Contract: yes. Item 1 names the callers shape; D-034 applies.
  - (2) Canonical path: yes. The real patched hook and REG_PRE at the PIN.
  - (3) Material: yes. Untracked text reaches the model.
  - (4) Discriminator: yes. `probe_callers2.py`, `real` against `fixed`.
  - (5) Ownership: yes. `_code_part` and the readers that round 2 changed.
  - **Result: BLOCKS.**
- **B2:**
  - (1) Contract: yes. Item 1, "whatever the build did"; D-034 applies.
  - (2) Canonical path: yes. The real refresh CLI, graft and REG_PRE. The event order is arranged.
  - (3) Material: yes. Untracked text, including a default argument.
  - (4) Discriminator: yes. `probe_f1b.py`, real against `VK_FIX=freshgraph`.
  - (5) Ownership: yes. `_code_part`.
  - **Result: BLOCKS.**
- **B3:**
  - (1) Contract: yes. Item 6, "what else breaks", and the CI gate (AF-AP-126).
  - (2) Canonical path: yes. The delivered patch and the test file CI runs; the CI run itself is static.
  - (3) Material: yes. CI goes red and pushes are refused.
  - (4) Discriminator: yes. The patched tree gives 3 failed; the PIN gives 129 passed.
  - (5) Ownership: yes. K2's test file and K2's patch.
  - **Result: BLOCKS.**
- **Everything else fails at least one condition:**
  - Items 4 and 5: test gaps, condition 3.
  - Item 6: misleads only, and it predates round 2 (conditions 3 and 5).
  - Item 7: fails closed, availability only (condition 3).
  - Items 8 and 9: documents and tooling outside the code.
  - Item 12's silent turn-off: fails closed.
  - Item 13: trusted state.
- No CONTRACT-DEFECT: every blocker falls inside the frozen items.

### 5. What must hold before registration (rewritten for round 2's bytes)

1. **Fix B1.** The code part carries only callers and tests that TRACKED.txt lists, and the total is recounted or dropped. Add a check through the real patched hook, with a tracked control and a mutant that removes the filter.
2. **Fix B2.** `_code_part` withholds the code part when the pack's symbol-source graph is not `fresh`. Add checks for the untracked shape and the tracked-revert shape, with a mutant.
3. **Fix B3.** `hook_dir` must know whether the hook already carries the patch, and the negative control must use the unpatched bytes from a fixed commit. Then `tests/test_filepacks.py` must give 0 failed in a tree with the post-commit patch applied.
4. **Port the seven verifier checks** from item 4, with their mutants. `n2_blobs_missing` matters most, because the live state has no BLOBS.txt.
5. **Land the post-commit patch before the registration or with it** (round 1's condition 1 stands). Before any session loads the hook, one post-commit build or one manual `filepacks.py build` must write BLOBS.txt at HEAD. Check that `BUILD.json`'s commit equals HEAD and that BLOBS.txt exists. Until then every code part is withheld: safe, but the trial measures nothing.
6. **Landing the patched installer and settings is the registration.** setup.sh runs the installer at every session start and compaction. Land them only after items 1-5 pass, under the owner's yes (D-108 turned the file-packs trial on).
7. **Regenerate the vendored manifest in the same commit** (`vendored_manifest.py --write`). Without it `--check` exits 1. Re-derive the `.claude/` row at landing: cab4c825c03a84f9 was right at the PIN only.
8. **Gate the patched tree:**
   - `tests/test_session_hooks.py` and `tests/test_search_intercept.py` (137 at the PIN);
   - `tests/test_filepacks.py` (0 failed after the B3 fix);
   - `tests/test_system1_context.py` (141);
   - `tests/test_codemap.py` (56);
   - `tests/test_vendored_manifest.py` (57);
   - the 4-file rest of the union (106 passed, 7 skipped).
9. **The owner accepts the cost:**
   - about 129 ms at p50 and 164 ms at p95 per Read, Edit, Write or Bash call;
   - at the median window, 27.5 KB of entries plus 8.9 KB of stamps, and about 30 `S1-RATE` lines;
   - at p90, 49.4 KB plus 15.1 KB, and 51 lines.
10. **Update the documents** in the landing commit: D105-DESIGN-v1.md:281, and the K2-R2 report's F1 line and self-attack 1.

### 6. Reproduced, static, skipped

- **Reproduced:** everything in §2 unless it is marked [S] or UNVERIFIED.
- **Static:**
  - that CI runs the B3 tests (stage0-ci.yml:46; no skip marker);
  - that B3 holds at HEAD;
  - setup.sh:438 and resume-heal.sh:14;
  - that the `_cd` quadratic predates round 2;
  - F13.
- **Skipped:**
  - Any PC run, by rule.
  - A full `tests/` run in the patched tree: I ran the 9-file union plus the manifest file.
  - Fuzzing the parser beyond 162 cases.
  - A swap test for `pack-not-handed`.
  - Timing round 1's `cd` chain, because round 1's quadratic word scan would dominate it.
  - The stopped verifier's exact 2,511-command scope.

### 7. Files, logs and hygiene

- **Code at the PIN:**
  - `/home/user/agent-factory/scripts/filepacks.py`: `Packs.blob` :483, `_code_part` :568, the blob check :601, `hook` :761 and :793, `_build` :955, the BLOBS.txt write :1037.
  - `/home/user/agent-factory/scripts/codemap.py`: `wait_for_graphs` :222, `_graft` :296 and :305, the callers sample :488, `build_one` :660, the pack fields :710, the callers line :844-846, `edit_context` :953, `file_entry` :987.
  - `/home/user/agent-factory/tests/test_filepacks.py`: `hook_dir` :1197-1206, the failing tests at :1256 and :1262. At HEAD these lines are 3 lower.
  - `/home/user/agent-factory/tasks/briefs/jev-trim/K2-post-commit.patch` and `K2-registration.patch`.
- **Scratch:** `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2r2/`
  - Probes: `probe_callers2.py`, `probe_f1.py`, `probe_f1b.py`, `probe_blobs.py`, `probe_forge.py`, `parser_r2.py`, `quad_cd.py`, `quad_ctl.py`, `mutdrv3.py`, `replay_r2.py`, `lat_r2b.py`, `stamp_cost.py`, `pcsh_regress.py`, `live_callers.py`.
  - Notes: `PROGRESS.md`. The applied diff: `reg-diff.txt`.
  - Logs in `logs/`:
    - blockers: `b1-callers-real.txt`, `b1-callers-fix.txt`, `b2-sg-untracked-real.txt`, `b2-sg-untracked-fix.txt`;
    - `forge-pack-blob.txt`;
    - registration gates: `reg-gate1.txt`, `reg-gate2.txt`, `reg-gate3a.txt`, `reg-gate3b.txt`, `reg-gate3c.txt`;
    - PIN gates: `gate-p1.txt` to `gate-p3.txt`;
    - mutation: `mut-control.txt`, `mut-run.txt`, `mut3-*.txt`;
    - parser: `parser-*.txt`, `v-*.txt`;
    - manifest: `man-*.txt`, `vm-run.txt`, `row-*.txt`;
    - `replay-r2-live.txt`.
- **To re-run:** each probe needs a detached worktree at f605913 (`git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add -q --detach <dir> f605913`), passed as `VK2_WT`. `mutdrv3.py` takes `VK_WT`, `VK_S`, and `VK_OLD=…/scratchpad/vk2`.
- **Hygiene:**
  - **Worktrees:** I removed all five (vk2/wt, vk2/wt1, vk2/wtg, vk2r2/wt, vk2r2/wtreg) with `worktree remove --force`, hooks off. `git worktree list` shows 0 entries under `scratchpad/vk2`. The other lanes' worktrees are untouched.
  - **Shared tree:** no git write except the worktree add and remove.
  - **Never written:** any `settings.json`, the installer, the live `.jev/filepacks*` and `.jev/codemap`. The one live `.jev` write is item 9.
  - **Processes:** none of mine is running (no process has a cwd under my scratch). A pytest under `/tmp/g1` belongs to another lane; I left it alone.
  - **Secrets:** none read. The canaries are random hex made at run time.
  - **Transcripts:** the replay and the pc.sh scan read `tool_use` inputs only and printed counts. No thinking block was read.
  - **Network:** no ssh ran and there was no PC bridge.
  - **Slips:** two read-only Bash calls started with a top-level `cd`, against your note. They had no effect.
  - **Reboots:** at 14:09:29Z and about 14:20:10Z they voided the parser run and the wtreg gate. I re-ran both, one file at a time, with `free -m` checked first.