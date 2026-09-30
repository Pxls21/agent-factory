# VERIFY-K2-RS: the verifier's report of record, round 5 (task #353)

> **Coordinator note (2026-09-30 17:2xZ).** The VERIFY-K2 verifier, resumed for round 5 on the RE-SCOPE (D-117), came
> home at 17:2xZ; its hand-back is saved verbatim below (harvest run s-20260930T172542Z-1cf3b1: 1,224 assistant records
> over rounds 2 to 5, every one claude-opus-5-5, 0 refusal stops; hand-back sha256 prefix da92e60d30a3). The harness
> marked the hand-back as instruction-shaped (a settings-json pattern): it describes the registration patch's hook
> order, and nothing in it was acted on. Recommendation: MERGE-READY-WITH-FOLLOWUPS. The coordinator's gate:
> MERGE-READY-WITH-FOLLOWUPS; F3 (the `lookup` and `demo` CLIs) is read as a follow-up, not the core class, because
> D-117's condition (b) governs what the hook injects, and a CLI the model runs by its own choice reads bytes it could
> read from `.jev/codemap/` anyway. **D-115's round table:**
>
> | Round | Verify | Blocker |
> |---|---|---|
> | 1 | MERGE-READY-WITH-FOLLOWUPS on one condition | F1: a stale index let an untracked file's text through |
> | 2 | NOT-READY | B1: untracked callers through a tracked file's code part |
> | 3 | NOT-READY | R3-1 |
> | 4 | NOT-READY | R4-1, the same class; K2 went to the owner, who chose RE-SCOPE (D-117) |
> | 5 | MERGE-READY-WITH-FOLLOWUPS | none; F1 and F2 are untested clauses, closed by task #420 before registration |

## Round 5 (RE-SCOPE)

Written 2026-09-30 from Wed Sep 30 17:23:43 UTC 2026 (`date -u`). PIN: origin 2df97aa. Verifier: the resumed VERIFY-K2 verifier. The transcript shows `claude-opus-5-5` on all 271 assistant records since 15:40Z and 0 refusal stops.

**Recommendation: MERGE-READY-WITH-FOLLOWUPS.**
- No finding meets the whole D-034 blocking predicate. There is no core blocker.
- Through the real hook and the registration's command, I found no path where a byte HEAD's tree does not hold reaches the model. I tried every item-2 and item-3 shape and every write point of the new marker protocol. I also ran a hammer: 528 builds against 120 real-hook reads gave 0 canaries.
- The hook stays unregistered until the must-hold list (item 13) holds.
- One thing I did not reproduce decides one classification: F3, the `codemap.py lookup` and `demo` CLIs.
  - The CLIs do show an undone commit's symbols after a reset (reproduced).
  - They are not the injection path that D-117 (b) governs. The model reaches them only by running them itself, and the same bytes sit in `.jev/codemap/*.json`, which the model can `cat` anyway.
  - If the coordinator reads item 14's sentence as covering a dev CLI that the model runs itself, F3 is of the core class ("a byte HEAD's tree does not hold reaching the model"). By my reading it is a FOLLOW-UP.

Most important follow-up (F1): the frozen contract-3 clause "registry rows only when they are computed from the committed blob's lines" holds at the PIN, but no test protects it. A mutant that brings back round 4's working-copy source for the registry passes all 175 filepacks tests and all 63 codemap tests. Through the real hook, that mutant puts an uncommitted line's canary in front of the model. I recommend closing this before registration.

### 1. Premise
Identical. 14 commands; the expected and actual blocks both hash to 43d49dfdd5cf9ff5. No CONTRACT-INVALID.

### 2. Condition (a), symbols from the committed blob [reproduced]
Method: the real `codemap.py build` (the PIN's copy, in the fixture), then the real `filepacks.py build`, then the real hook through REG_PRE. Probes p2a, p2b, p2c.

No symbol, name or line from bytes other than the committed blob reached the model in any shape:

| Shape | Result |
|---|---|
| Uncommitted defs (canaries) in the middle and at the end, then rebuilt | Pack = HEAD's blob (`symbols_from: "ast"`). Every Edit, Read range, Read and cat showed only committed symbols, with STALE. |
| Untracked file | "untracked", no pack, nothing shown |
| Committed symlink | Pack of the link's own 8-byte blob; the reader gives no code part for a link working file (also retargeted, and a tracked file replaced by a link) |
| Gitlink | In TRACKED, not in BLOBS; P2 only |
| Rename, committed | New path built, old path nothing |
| Rename, staged only | Untracked, nothing |
| Missing loose object | cat-file answers "HEAD:scripts/gamma.py missing" rc 0; parsed as missing; pack removed; beta in the same batch still built |
| Spaces, non-ASCII paths | Built and shown correctly |
| Newline path | Not in TRACKED; `_committed` skips it; nothing shown |
| Latin-1 with a coding line, BOM, CRLF, CR-only, invalid UTF-8, 250 nested parens, 98 nested defs | Committed-derived output only (cosmetics in F12) |
| 20,000 defs | 3.5 MB pack; hook 109–131 ms |
| Legacy pack claiming "ast" | Can only be forged: no earlier codemap.py (6 revisions back) writes "ast". Round 4 wrote graft, code-review-graph or None. |

Found: F5 (a MemoryError aborts the whole build), F6 ("0 symbols" for an unparseable blob), F11, F12.

### 3. Condition (b), the tree check [reproduced, p3]
Nothing is shown (`tree`) after:
- `reset --hard`, and a checkout or detached HEAD on another tree;
- amend with another tree;
- a git that fails (exit 128);
- a git that hangs 3 s: timed out at 2 s, about 2.1 s per hook call;
- BUILD.json missing, not JSON, a list, `tree` an int, uppercase, 39 characters, or with a newline, the marker, a link or a FIFO (no hang).

Shown, and consistently HEAD's tree:
- a detached HEAD at the build;
- stash and stash pop;
- a merge or rebase stopped half-way (HEAD = the built main2; the code part carries STALE);
- a second worktree, decided by its own HEAD;
- a git that answers in 1.5 s;
- a same-tree branch, and amend with the same tree.

Unborn HEAD: covered by the head-unresolved check (green), plus F2.

Environment variables:
- GIT_WORK_TREE alone, GIT_INDEX_FILE and GIT_COMMON_DIR: nothing shown.
- GIT_DIR pointing at a clone whose HEAD is on the build's tree shows the packs while this repo's HEAD was reset. This is F4 (NOT done 5).

By-design residuals:
- The same-tree move shows P2's commit lines and `@sha` from the build's history. Reproduced: HEAD aff175b showed "commit 6610dcb …: canaries bdf9882e974", a commit its history lacks.
  - Harmless for push_clean: it strips trailers only, so the subjects stay the same.
  - D-117 accepts it ("trees, not commits"), and the builder's Self-attack states it.
  - The module docstring overstates it (F9). The owner reads it only if the coordinator carries it.
- HEAD moving after the check is inherent to any hook. The builder's report states it; the docstring does not.

### 4. The marker, `still()` and the id [reproduced, p4 and p4cost]
- **A build in flight, through the real hook** (a build of C_new while HEAD is on C8's tree): the hook showed 0 bytes (`tree`) after each of the 7 writes (marker, 3 packs, BLOBS, TRACKED, final record). Before the build it showed C8's packs.
- **The reverse interleave** (in process: the reader reads the record, then a build runs to write N, then the reader reads its parts and rechecks): for N = 1 to 7, a full build, and ABA (two builds), every result was `tree`, with no canary.
- **A crash after the marker** (the BLOBS write fails and leaves a temp):
  - BUILD.json stays the marker, and the hook is dark until the next successful build (the next commit's post-commit build, or a manual one).
  - That build removed the temp and restored the output.
- **Two builds at once:** the second waits on `state/filepacks.lock` (still blocked after 2 s, then rc 0).
- **BUILD.json read while it is replaced:** the hammer (528 builds, 120 reads) gave 0 canaries. 90 of the 120 reads showed nothing; 30 showed C8's packs.
- **`still()`:** it compares the full bytes after both parts (:717). Mutants still-tree-only, constant-id and still-before-p2 are KILLED.
- **Cost on the real tree, at nice 19 / ionice idle:**

  | Build | Total | Marker to final record |
  |---|---|---|
  | Incremental | 2.0–2.3 s | 0.1 s |
  | First | 3.3 s | 1.1 s |

  After a commit the hook is dark for the whole build, since HEAD's tree changes at the commit. That is about 2–3 s per commit, or about 25 s an hour at 10 commits an hour.
- The larger cost is F7: a changed file's code part is withheld for the code-map refresh.

### 5. The surface is gone [reproduced, p5]
- **Canary in every unrendered field:** I planted a canary in every field no reader renders: every graph section, the ap_screen status and note, `caller_files`, `tests`, `timing`, `built_at`, `commit`, `sha256`, symbols' `name` and `gitnexus`, extra keys on symbols and registry rows, and a top-level key. The screens stayed valid, so the rows still showed.
  - Hook touches: none of the canary reached the model on an Edit in a symbol, an Edit at module level, an Edit in a registry row's function, a Read range, a whole Read, or cat.
  - CLIs: none of it appeared in `lookup` (text and `--json`) or `demo` (text and `--json`).
- **Error strings** are fixed words (link, unreadable, corrupt, gone). They are logged only; the hook always exits 0 and prints only entries.
- **Other readers:** only codemap.py and filepacks.py read the pack dirs. No stack, jev_locate or hook reads them.
- **The builder's cost figures:** checked on /tmp/codemap-refresh.log, read only. There are 78 "done" lines; 74 built something (the builder's "74 runs").

  | Figure | Builder | Log |
  |---|---|---|
  | Wait median | 101 s | 101 s |
  | Wait p95 | 295 s | 295 s |
  | Wait max | 546 s | 546 s |
  | Wait+build p95 | 379.3 s | 379.3 s |
  | Wait+build median | 113.1 s | 114.1 s |
  | Build median | 3.5 s | 3.9 s |
  | Build p95 | 119.7 s | 136.0 s (119.7 is the 4th largest) |

  Four of seven match exactly; the magnitude holds (F8).

### 6. The class tests and their controls [reproduced plus static]
- **The real hook:** `reset_scenario` copies the tree's own post-commit hook and applies K2-post-commit.patch (`hook_dir`), and real `git commit` runs it.
- **The registration's command:** REG_PRE and REG_RESET equal the registration patch's PreToolUse and SessionStart commands. I checked by string equality against the both-patches tree's `.claude/settings.json`.
- **The leak control** `tree-check-off` removes only the tree gate; `still()` stays. It fails for the tree check's reason: the builder's kill line is the leak assertion.
- **The AF-AP-251 fix is complete:**
  - The test uses a private HOME and a private `CBM_RUNTIME_DIR` (mkdtemp under /tmp, removed in `finally`), plus a log guard.
  - I watched one [real] run. It started 16 cbm-side processes (4 each of the cli index, the `--cbm-daemon-internal` daemon, the index worker and the code-map refresh). All had their cwd under the fixture and all were gone before the test ended. The pre-existing pids 20175, 32144 and 32217 were untouched, and no /tmp/cbmr.* was left.
  - The other real-hook test (`patched_scenario`) commits Markdown only, which launches no graph (`docs_plane`).
  - The real-refresh tests call codemap.py directly; cbm is not in that path.
  - test_codemap's real-hook commits put a fake codebase-memory-mcp first on PATH.

### 7. The removed tests
Every removed check, test and mutant falls into one of two groups:
- It tested the removed surface: callers, tests, totals, provenance, graph freshness, UNKNOWN risk.
- It tested a behaviour D-117 reversed. `older-p2-stale-code` expected P2 to show after a new commit; now nothing shows until the build, and the tree-gate mutants cover that.

The concerns that still apply keep a killer:
- Packs.blob's `"\n%s\t"` key: `blobs-suffix-match` → blobs-exact-path. This is the same mutation as the removed blob-key-substring.
- The blob tie: my blob-check-off is killed by blobs-missing and late-code-pack.
- Newline paths: no-nul-newline-guard → nul-newline.
- Legacy symbol sources: legacy-symbols-shown.
- A missing or untracked blob: the codemap untracked-file check (probe A8 reproduced the missing path).

No still-applicable concern lost its test. The gap in F1 is a property that is NEW in the re-scope and never had a test. At round 4 (e2f4f08:780/820) the registry was screened from the working copy.

### 8. Mutation [reproduced]
Method: control first, bytecode off, `__pycache__` cleared per mutant, each file restored and its sha checked.

**The builder's driver:** control 11 passed in 53.67 s; 9 of 9 KILLED.

**My new mutants** (driver mutdrv5.py; control "133 passed in 325.35s"):

| Mutant | Verdict | Killer or note |
|---|---|---|
| still-tree-only | KILLED | record-rebuilt |
| timeout-read-as-current | KILLED | head-unresolved |
| head-not-tree (`HEAD` for `HEAD^{tree}`) | KILLED | 50 checks |
| constant-id | KILLED | record-rebuilt |
| still-before-p2 | KILLED | record-rebuilt, record-rechecked |
| blob-check-off | KILLED | blobs-missing, late-code-pack |
| timeout-60 | KILLED | head-unresolved: "the hook stalled past 25 s" |
| screen-records-head-blob | KILLED | pack-fields, drift test |
| lines-from-working-copy | KILLED | by a formula artifact; not a clean discriminator |
| marker-after-clean | SURVIVED | Equivalent: `_clean` only removes |
| object-rx-dropped | SURVIVED | Equivalent: `_rev` returns only OBJECT_RX ids or None |
| current-none-equals-none | SURVIVED | F2 |
| registry-from-working-text | SURVIVED | 66 selected, then all 175 of test_filepacks; F1 |

**Round-4 mutants that still apply**, on the both-patches tree: control 5 passed; 7 of 7 KILLED (preimage-unchecked, 4 reg-*, 2 settings-*). The other round-4 mutants target removed code (anchor count 0). The exception is committed-misaligned: its anchor exists, but `_committed` now gets one path per call, so it is equivalent and I did not run it.

### 9. The screen's tells: none is real in production
- **AF-AP-175** (3 in production; 45 are fixture git calls in tests):
  - filepacks.py:543, the tree check's own call: not real. HEAD is named once per hook call, the reader reads no git object after it, and the check must read the live HEAD.
  - filepacks.py:1034: not real. HEAD is resolved once and `sha` is threaded to tree, ls-tree, `_blobs` and `_log`.
  - codemap.py:681: not real. It runs once per `build()` and is threaded to `_committed`.
- **AF-AP-40** (5 in production): filepacks.py:804 and :846; codemap.py:724, :735 and :839. None gates a required artifact. At 724/735, exists-then-unlink can crash a manual build that races a refresh; that fails closed.
- **AP-32** (3 in production):
  - filepacks.py:782 hashes exactly the text injected.
  - codemap.py:147 and :710 feed only graph sections, which have no reader.
  - The reader's tie uses git's SHA-1 blob form, the same form ls-tree prints (see F13 for sha256 repos).
- **AF-AP-115** (1): codemap.py:284 `_which` for graft, gitnexus and crg, whose output reaches no reader now.
- **AP-1** (1): filepacks.py:1233 `AF_FILEPACKS_STATE`, read once in main() and threaded. It is a documented seam.
- **AF-AP-72** (3):
  - filepacks.py:903 and :908 take `int()` of git's own cat-file size field.
  - codemap.py:219 parses /proc/locks inside try/except ValueError.

### 10. NOT done 6
The model can reach `lookup` and `demo`, but only through Bash, by its own choice. No skill, CLAUDE.md, stacks.toml entry or hook routes it there; only codemap.py's usage text and old briefs name them.

They do show bytes HEAD's tree does not hold:
- After `reset --mixed`: `lookup scripts/alpha.py --line 24` gives "function leak_cl3845196673 L24-25 · def leak_cl3845196673(token='cl3845196673')" with no STALE mark, because the working file equals the pack's blob. `demo` shows the same.
- After `reset --hard` the same symbol shows, marked STALE.
- At both moments the hook injected 0 bytes.

See F3.

### 11. The two patches
- Both apply in a clean worktree at the PIN.
- `2 files set=2415789b9582` → "pytest-summary: 144 passed in 53.21s".
- `hook_count(our_hooks)` = 15: ls_req 3, filepacks 2.
- Order:
  - SessionStart: session-start.sh, task_sync, stack catalog [startup|resume|compact], **filepacks reset**, ls_req. The reset comes before the chat form.
  - PreToolUse: search-intercept [Grep|Bash], system1-context [Write|Edit|Bash], **filepacks [Read|Edit|Write|Bash]**, last.
- Manifest `-k test_committed_manifest_matches_fresh_generation`: `1 files set=21e700b8344c` → "pytest-summary: 1 failed, 56 deselected in 1.33s". The failure is on line 20, `.claude/ (kit-adapted)`: committed f0acf40e… against generated 1b63d45d…. This is expected. The builder's aab0f94a…/9a712fa7… were measured at its own base.

### 12. Gates at the PIN (my worktree; `--basetemp` outside every work tree)
- `1 files set=db64e610236b` → "pytest-summary: 175 passed in 168.48s (0:02:48)".
- `1 files set=db64e610236b` → "pytest-summary: 175 passed in 172.56s (0:02:52)".
- `2 files set=395f8af3a0ce` → "pytest-summary: 204 passed in 297.20s (0:04:57)".

### 13. What must hold before registration
1. K2-post-commit.patch lands with or before the registration. Without it, the first commit leaves the hook dark until a manual build.
2. K2-registration.patch is applied (15 hooks, the order above), and the vendored manifest's `.claude/` row is regenerated at the landing base.
3. At HEAD, in this order:
   - `python3 scripts/codemap.py build --all`. The live code packs lack `symbols_from: "ast"` until then. On the real tree it gave 234 packs in 4.6 s, rc 0, with no crash (all 261 committed .py files parse).
   - Then one `python3 scripts/filepacks.py build`. It gave 1756 packs in 2.4 s, and BUILD.json carries a tree and an id.
   - A smoke of the registration's command in my worktree then showed committed AST symbols, registry rows and P2.
4. Recommended, though not blocking by the predicate:
   - F1's check and mutant (the registry's committed-lines source, a frozen contract-3 clause).
   - F2's case added to head-unresolved.
5. Owner decisions: F3 (gate or label the CLIs) and F4 (scrub GIT_* in `_rev`).
6. The owner-facing residual sentence (F9), and the kill switch `<state>/filepacks-off`.

### 14. Gate
MERGE-READY-WITH-FOLLOWUPS: no finding meets all five predicate conditions. Blockers: none. The recommendation depends on one reading I did not reproduce as injection: F3's CLIs.

### Finding inventory (no severity filter)
Reproduction scripts are under `<SR>` = /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2rs.
- Each probe needs a clean worktree at the PIN: `git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add -q --detach <SR>/wt 2df97aa`.
- Then run `( cd <SR>/probes && python3 <probe> )`.
- Logs are in `<SR>/logs/`.

1. **F1 FOLLOW-UP — the registry's committed source has no test.** [V]
   - Contract: K2-RS contract item 3.
   - Canonical path: the production code is correct. With the PIN's code, the canary stayed out.
   - With the mutant, the real hook injected "registry rows here 1: AF-AP-175 :6 leak = "rg4a36fc275f" + "HEAD" — …".
   - Material effect at the PIN: none. A regression would pass all 238 tests of the two files.
   - Reproduce: `p8disc_b.py`, and `mutdrv5.py registry-from-working-text-fullfp` (175 passed).
   - Fix: a check with the real builder, the committed screen, and an uncommitted line the screen hits, with the Edit placed on that line; plus a mutant for it.
2. **F2 FOLLOW-UP — `isinstance(want, str)` in `current()` (:544) is untested.** [V]
   - A record with no tree and a failing git: the PIN shows 0 bytes; the mutant shows 907 bytes.
   - Contract item 4 holds at the PIN.
   - Reproduce: `p8disc.py`.
   - Fix: add this case to head-unresolved.
3. **F3 FOLLOW-UP — NOT done 6.** Class: a byte HEAD's tree does not hold, through a dev CLI the model runs itself; not injection. [V]
   - The CLIs show an undone commit's symbols (item 10). codemap.py's docstring says `demo` shows "what L2b would inject", which is false after a reset.
   - Reproduce: `p5.py`.
   - Fix: apply `Packs.current()` plus the BLOBS and `symbols_from` checks in lookup and demo, or print a first line that says the output is not HEAD's tree.
4. **F4 FOLLOW-UP / UNVERIFIED on the canonical path — GIT_DIR.** [V in the fixture]
   - With GIT_DIR pointing at a same-tree clone, packs are shown while this repo's HEAD was reset.
   - This harness sets no GIT_DIR: 0 of 5 claude processes carry the name, and the Bash env has none.
   - Reproduce: `p3.py`.
   - Fix: remove GIT_DIR, GIT_WORK_TREE, GIT_COMMON_DIR and GIT_INDEX_FILE from `_rev`'s env.
5. **F5 FOLLOW-UP — ANOTHER class (availability, fails closed). `_ast_starts` (codemap.py:624-628) lets MemoryError escape.** [V]
   - A committed 200,000-deep unary chain makes `codemap.py build` exit 1. Later files get no pack; `build --all` gave 0 packs.
   - This is latent: no file at the PIN triggers it.
   - Reproduce: `p2c.py` (A9).
   - Fix: catch RecursionError and MemoryError there, or drop the function (only unshown `_moved` uses it). Add a per-file try in `build()`.
6. **F6 FOLLOW-UP — ANOTHER class (a false statement).** [V]
   - For an unparseable blob (and for every non-Python code file) the text says "0 symbols, 0 at top level".
   - Reproduce: `p2a.py`.
   - Fix: record the parse failure and say "no symbols: the committed blob does not parse" or "no symbols for <language>".
7. **F7 FOLLOW-UP — cost.** [V on the log]
   - The refresh waits on graph re-indexes (wait+build median 114.1 s, p95 379.3 s) before an AST-only build that takes seconds. Meanwhile, the files a commit changed get no code part, and those are the files the model is most likely to touch next.
   - Fix: build the AST part at once and refresh the graph sections later, or drop them.
8. **F8 INFO — three of the builder's seven cost figures differ slightly** (item 5). [V]
9. **F9 FOLLOW-UP — prose.** [V]
   - filepacks.py:28 says "Every byte shown is committed text of HEAD's tree". P2's commit lines are the build's history, which after a same-tree move can hold commits HEAD's history lacks. Reproduced in `p3.py`.
   - Fix: one sentence.
10. **F10 INFO — the trust root.** A forged record with a tree and `"building": true` shows; a forged pack claiming "ast" shows (the state is trusted, F6 by design). The real marker never names a tree. [V]
11. **F11 INFO — Edit placement uses working-copy line numbers.** An edit in an uncommitted def was named as the committed `Box.__init__`, with STALE. These are numbers, not bytes; the builder states it. [V]
12. **F12 INFO — cosmetics.** [V]
    - A BOM stays in line 1's signature.
    - A latin-1 signature shows U+FFFD while the name is right.
    - A CR-only file counts 1 line, so `lookup` says past-end and an Edit in `b` is placed in `a`.
13. **F13 INFO — sha256 repos.** `blob_sha` is SHA-1 (codemap.py:140), so in a sha256 repository every code part would be skipped (fails closed). This repo is sha1. [S]
14. **F14 INFO — two equivalent mutants** (item 8). [V]
15. **F15 INFO — a crash after the marker leaves the hook dark until the next build.** No SessionStart build recovers it. [V]
16. **F16 INFO — the dark window per commit** is about the whole build: 2–3 s. [V]
17. **F17 INFO — a stale dated finding.** docs/research/findings/jev-trim/D105-DESIGN-v1.md:281 still says "round 3 repairs them". [S]
18. **F18 INFO — the refresh's `--commit` only labels the log line.** `build()` uses HEAD as it is when the build starts, which after a wait of up to 1200 s may be a later commit. The packs stay correct; the log line names the old commit. [S]
19. **F19 INFO, hygiene, mine — AF-AP-249 form.** Six of my round-5 Bash calls used a top-level `cd`: 16:31:24, 16:32:28, 16:32:35, 16:36:19, 17:05:31 and 17:18:49 UTC. Each was `cd /tmp` or `cd <SR>/probes`, before read-only greps or probes. None wrote to git or the shared tree. Counted from my transcript's tool_use inputs: 146 Bash calls since 15:40Z.

### Reproduced, static, skipped
- **Reproduced:** items 1, 2, 3, 4, 5, 6 (monitor), 8, 10, 11, 12; the must-hold sequence and the smoke; hook_count and the order.
- **Static:**
  - the hook's exit paths (always 0);
  - the post-commit's `docs_plane` rule;
  - F13, F17, F18;
  - the post-commit hook's per-pick runs during a rebase (not run with hooks on);
  - shared /tmp locks across worktrees (pre-existing L2a behaviour).
- **Skipped:**
  - re-measuring the builder's 50-call hook cost (not in this brief);
  - GIT_DIR through a real harness launch;
  - a real submodule;
  - the whole manifest test file (forbidden);
  - reading the parent session's transcript (it is not mine).

### Hygiene
- **Worktrees:** wt, wtmut and wtboth were removed with hooks off; `git worktree list` shows none of mine.
- **Processes:** no process has a cwd or cmdline under vk2rs; no /tmp/cbmr.* is left; pid 32217 is untouched and alive.
- **Registration:** `grep -c filepacks` on `.claude/settings.json`, `scripts/install_session_hooks.py` and `/home/user/.claude/settings.json` gives 0, 0, 0.
- **Shared tree:** no git write. Its current dirty set (jev_relay files, the ledger, the logs, live-state) is not mine.
- **Environment reads:** I never read a secret file. From /proc/<pid>/environ I printed only a count of the variable name GIT_DIR, never values. I printed the GIT_CONFIG_KEY_* names only.
- **Rules:** no outward action, no PC bridge, no subagent, no stack.py run.
- **S1-RATE given this round:** s1-04b5d2ca, s1-4785fd86, s1-ee188dcc, s1-e523273f, s1-3d087907.
- **Scratch kept:** `<SR>/probes`, `<SR>/logs`, `<SR>/mutdrv5.py`, `<SR>/mutdrv_r4b.py`, `<SR>/PROGRESS.md`.