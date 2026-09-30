# LS-B12-R1: the builder's report of record (task #385)

> **Coordinator note (2026-09-30 10:0xZ).** The LS-B12 builder, resumed for the first repair under D-031, came home
> at 10:0xZ; its hand-back is saved verbatim below (harvest run s-20260930T100807Z-02af11: 943 assistant records,
> every one claude-opus-5-5, 0 refusal stops; hand-back sha256 prefix d796ad15c409). Checked at landing: the patch
> `tasks/briefs/labeling/LS-B12-R1.patch` has the reported sha256 (100457db9343...), `git apply --check` passes at
> HEAD, no commit since the PIN touches its files, and all seven applied files match the report's sha256 table. The
> coordinator read the production hunks: graft `ask [--in S] -- <text>`, GitNexus `query --repo . -- <text>`, cbm
> `--project=<slug> --query=<text>`; `search_text` itself is unchanged (its output is pinned byte-identical), so the
> GitNexus HIGH rating does not apply to an edit; the three callers rate UNKNOWN (dispatched through the
> `INSTRUMENT_FNS` table, which the index does not resolve). fix-echo reads unmapped on the JSON ranking
> `"ranking": "no instrument answered`, which JSON escaping keeps out of repo text and which render()'s skeleton
> keeps; a diff with nothing to echo reads ok with its reason. cbm reads unmapped on its JSON error's opening;
> `changes` gains a probe step (`--version`) that carries the launch marker. The landing ran the two chores the
> builder left (NOT done 1 and 2): `sync-skills.sh` and the manifest regeneration. Status: LANDED,
> GATED-PENDING-VERIFY.

---

## LS-B12-R1 report (task #385), written 2026-09-30 10:0xZ

**TL;DR:** All six items are done and verified. Patch: `/home/user/agent-factory/tasks/briefs/labeling/LS-B12-R1.patch`, sha256 `100457db934324bb298e74bc5cfd78948f7b1e50128a4913f1efeea447d46715`, 864 lines, 7 files (+466 −85). `git apply --check` passes at PIN 74285a5 (rc 0). Applying it in a PIN clone gives the worktree's 7 files byte for byte. No commit since the PIN touches these files, up to the main tree's HEAD d975495. Two landing chores are not mine: the `.agents` skill mirror sync and the vendored manifest rewrite (NOT done 1–2).

### NOT done (first-class)
1. **`.agents/skills/box-and-labels/SKILL.md` is not synced.** The brief says `.agents/` is not mine.
   - `sync-skills.sh --check`: the PIN clone reports "in sync (415 skills)"; the worktree reports "DRIFT (content differs): box-and-labels".
   - The pre-commit SKILL-SYNC gate blocks the landing commit until someone runs `bash harness-ports/bin/sync-skills.sh` and stages `.agents/skills`.
2. **`sandbox-kit/VENDORED-MANIFEST.md` is not rewritten.** `tests/test_vendored_manifest.py` (`1 files set=21e700b8344c`): `pytest-exit: 1`, `pytest-summary: 5 failed, 52 passed in 173.98s (0:02:53)`.
   - All five failures report `vendored manifest drift: line 21`. That is the `.claude/ (first-party)` row's digest, which my skill edit changes.
   - `vendored_manifest.py --check`: the PIN clone gives PASS; the worktree gives FAIL, line 21 only.
   - The fix is `python3 scripts/vendored_manifest.py --write` at landing, which is outside my boundary.
   - That run came before my last skill edit. The class is the same (one row digest).
3. **No commit and no detect-changes on a commit.** The main tree's GitNexus index is 16 commits behind HEAD, and my worktree had no index.
4. **ripwire and sentrux keep the bare `missing — run scripts/setup.sh` marker** (gate/graph, impact/ripwire, review/sentrux, review/ripwire).
   - They print names, paths and numbers only (table below), so file content cannot forge it.
   - A tracked path holding that text still could. None exists: `git ls-files | grep -cF` gives 0.
   - The wrappers are outside my boundary.
5. **Not measured:** whether npx, pnpm dlx or bunx pass the `--` through for `gitnexus query --repo . -- <text>`. This box launches the global gitnexus. Tier: inferred.
6. **The cbm label's own argv is unchanged** (`--project home-user-agent-factory --query {q}`).
   - The runner's text type refuses a leading `-` (REFUSALS_385 cbm-dash).
   - Measured: cbm reads a space-led value such as `--query " --help"` as a literal search.
   - Only jev_context's `inst_cbm` moved to the `=` form.
7. **Untouched:** F-2 and F-9 (task #399), and the issue #88 items (F-4, the F-5 npx@latest path, and the rest).
8. **Semantics kept from the PIN:** `rg-and-graft unavailable` also covers "rg present but nothing to search (no distinctive token, no shape) and graft unmapped".

### Premise
The 12 premise commands were re-run in the main tree at HEAD 3223b98 with bytecode off. Result: **PREMISE IDENTICAL**. PIN sha prefixes:
- stacks.toml 07a3bc500c25927d
- jev_echo.py b03edb82eaf07ec3
- jev_context.py 9ccd68ae3a832371
- jev_locate.py 93441f4e45018817
- stack.py ef819f69430d7459
- test_stack.py 4190d5e59d8281fd
- test_jev_context.py c2816f7bf978692a
- test_jev_locate_echo.py 2c9e34b92c6c3525

The nine `unmapped_if` line numbers in the brief held at the PIN.

### GitNexus impact, pasted
- `search_text`: risk HIGH, impactedCount 3, direct 3 (inst_cbm, inst_gitnexus, inst_graft), processes_affected 3, modules_affected 1, epistemic exact. **Not edited**; its output stays byte-identical (a regression test pins it).
- `inst_graft`, `inst_gitnexus`, `inst_cbm`: risk UNKNOWN, impactedCount 0, "No callers resolved". A text search confirms the callers: `INSTRUMENT_FNS` (jev_context.py:664, which is jev_locate's eight instruments) and tests/test_jev_context.py:259 and :261.
- jev_echo `main`: LOW, 1 direct (its file). The index is 16 commits behind.
- `build_pack` and `render`: not edited.

### Item 1 (F-1): fix-echo's status never depends on repo text
**Design.**
- stacks.toml, fix-echo: `--json` added to the argv; `unmapped_if = '"ranking": "no instrument answered'`.
- jev_echo.py: new `NO_ANSWER` ranking, written only when the diff removes code lines and no instrument answered.

**Why this beats the verifier's `"answered": []`:**
- When a JSON pack is over budget, render()'s skeleton keeps only `tool`, `truncated`, `ranking` and `notes`. It drops `answered`, so a skeleton would read a hollow ok. The skeleton keeps the ranking.
- JSON escapes every quote inside a string, and every key in the pack is fixed. So repo text cannot write `"ranking": "`.
- `git grep` finds the structural text only in stacks.toml and the tests, not in any script source line, so a traceback cannot carry it either.

**Red at the PIN** (real runner, real jev_echo, a tree of its own):
- (a) A removed line forges both markers (the old `answered: none` and the new one): the PIN read `## sites · unmapped — rg-and-graft unavailable`, exit 1. Now: ok, exit 0.
- (b) A site's snippet holds both markers: same PIN failure. Now: ok, and the print shows them escaped.
- (c) Neither rg nor graft on PATH, with a real removed line: unmapped, exit 1, and the ranking is exact. At the PIN (c) already read unmapped; its new JSON assertions fail there with a JSONDecodeError because the PIN prints markdown. So (c) is a guard, not an F-1 red.

**The skeleton question: no.**
- A missing-tools pack is bounded near 4,100 characters by jev_echo's own cuts: head values at 300, the fixed-site line at 400, the token at 40 in each note; the rest is fixed text.
- Measured 2026-09-30: the heaviest pack I built (20 sites, 40-quote tokens, quote and backslash lines, a quoted patch path, 9 notes) is **3,060** characters at budget 9,000. It is identical at 6,000, so no skeleton.
- At BUDGET_MIN (1,000) it falls to the skeleton: 682 characters, same ranking, marker present.
- Pinned by `test_a_no_answer_pack_keeps_its_ranking_at_the_default_budget_and_in_the_skeleton`. At the PIN it is red: the ranking there is `ranking: lexical order (lexical overlap), Jev not asked`.

**Live:** `fix-echo diff=8b940f8` gives exit 0, answered rg-token, rg-shape, graft.

**Trade-off:** the fix-echo print is now one JSON line.

### Item 2 (F-8): nothing to echo reads ok and says why
- The ranking is `nothing to echo: <why>, so it names no anti-pattern (Jev not asked)`.
- The why is `the input holds no unified diff (no file header)` when no file section parses, else `the diff removes no code line`.
- No marker, so the status is ok, exit 0. The change is +9 lines in jev_echo.
- The test covers the verifier's four cases: `notes.md`, `HEAD:scripts/fixed.py`, the symlink `link.md` → notes.md, and the add-only `HEAD~1`. All four give ok, exit 0, the exact ranking, and empty answered, top and notes.
- At the PIN all four read unmapped, exit 1.
- Live: `fix-echo diff=scripts/stacks.toml` gives exit 0 with the "holds no unified diff" ranking.

### Item 3: sweep of the other nine `unmapped_if` steps
| Step (PIN line) | Repo text on stdout/stderr? | Evidence | Action |
|---|---|---|---|
| gate/graph 169 | names and paths only | ripwire test-gate on my worktree: fixed comment plus `<t p= run=>` and `<u sym= p= l= ccx=>` rows | none; residual in NOT done 4 |
| impact/ripwire 316 | names, paths, counts | edit-check on build_pack: `<edit-check sym= p= status= defs= callers=…><c n= p=/>`; parameter counts, never signatures | none; same residual |
| review/sentrux 487 | rule keys, counts, `path:function (cc=N)` | `sentrux_review.sh check` on my worktree: 120 lines; rules.toml defines no layer names | none; same residual |
| review/ripwire 497 | as gate/graph | as gate/graph | none |
| cbm/search 562 | **file content**: a Route node's string literal, verbatim with its spaces | tiny tree, private HOME: `"__route__ANY__/project not found or not indexed" Route` on stdout; the PIN label read unmapped on it (red test) | **fixed**: `unmapped_if = '{"error":"project not found'` |
| changes all/staged/unstaged/compare 597/607/617/627 | **file content**: markdown headings verbatim, as `Section <heading> → <file>` | tiny GitNexus world: the PIN `changes` read `unmapped — gitnexus unavailable`, exit 1, on a heading holding the text | **fixed**: a probe step (below) |

**Why cbm's new marker is safe.**
- The real not-indexed error is JSON on stderr (rc 1). A result row cannot hold `{"error":"`.
- Measured: a name or path with a space is printed quoted, with its quotes escaped. A path holding the whole fragment printed as `"{\"error\":\"project …`.
- Headings become Sections with spaces turned to dashes.
- A route's `{…}` part becomes `{}`.
- The marker also matches the binary's other literal, `{"error":"project not found"}`.

**The changes probe.**
- A new probe step: `node .gitnexus/run.cjs --version` (0.17–0.19 s, prints only the version) carries the unmapped_if.
- The scope steps moved to group 2, take `needs = ["probe"]`, and carry no unmapped_if.
- The print gains a probe section.

**Real-tool tests:**
- `test_changes_reads_ok_when_a_changed_heading_holds_the_launch_failure_text`: a real `gitnexus analyze`, offline (private HOME, `GITNEXUS_LBUG_EXTENSION_INSTALL=never`). Red at the PIN.
- `test_cbms_unmapped_if_is_the_binarys_own_not_indexed_error`: runs the real binary against a project name no store holds. It replaces the mmap oracle, because the JSON is built at run time and the binary does not hold `{"error":"project not found or not indexed"` literally.
- `test_cbm_reads_ok_when_a_result_quotes_the_not_indexed_text`: replays a captured real route row. Red at the PIN.
- `test_cbm_reads_unmapped_on_the_not_indexed_error`: its control.

**Live:** `changes` on the main tree, read-only: probe ok, all ok, exit 0. `cbm q=stack runner`: ok, exit 0.

### Item 4 (F-3): no search text reaches a tool as an option
| Call | Can a leading `-` reach it as an option? | Evidence |
|---|---|---|
| graft `ask <search_text>` (:456) | **yes at the PIN**; now `ask [--in S] -- <text>` | measured: `graft ask --in scripts -- --help` runs a literal search; the PIN order prints `Usage: graft ask [options] <query> [dir]` |
| gitnexus `query <search_text>` (:469) | **yes at the PIN** (usage printed); now `query --repo . -- <text>` | real index: JSON answer, in a test (red at the PIN: `unmapped — gitnexus query unavailable (non-JSON output)`) |
| cbm `--query <search_text>` (:494) | **yes at the PIN** (measured: `--query --label=Route` lists routes); now `--project=<slug> --query=<text>` | measured: `--query=--label=Route` is a literal search; `--query=stack runner` matches the plain form |
| gitnexus `context <sym>` (:478) | no | the name comes from `identifiers()`, whose `_IDENT` regex starts with `[A-Za-z_]` |
| crg `query callers_of <name>` (:514) | no | an identifier, or crg's absolute qualified name `/…::name` |
| rg `-e <pattern> -- <dirs>` (:536) | no | the pattern follows `-e`; the dirs follow `--` |
| rg `--files -- <dirs>` (:562) | no | the dirs follow `--` |
| git `log -S<tok>` (:652) | no | one attached argument |
| graft `--in <scope>` | no | a dash-led value is read as the value (measured `--in -probe`); locate's scope is a path, which refuses `-` |
| jev_echo graft `ask "code like: …"` (:235) | no | the text starts with `code like: ` |
| jev_echo `git show … <arg> --` (:277) | no | a dash-led arg is refused (usage error, exit 64) |
| cbm label `--query {q}` (stacks.toml) | no | refused by the runner's text type; a space-led value is literal (measured) |

- **search_text is byte-identical.** `test_a_plain_question_reaches_each_tool_with_its_search_text_unchanged` pins three plain questions to their PIN texts, and checks each tool gets the text whole.
- **Argv-recording tests per tool:** 3 verifier cases each for graft, gitnexus and cbm, plus graft with a scope. All red at the PIN, for example `[['ask', '--help']] == [['ask', '--', '--help']]` failing.
- **Live chain:** `locate "q= --help"` on the worktree gives exit 0; graft, rg, registry, quirks and git-log answered; no `Usage:` in the output.

### Item 5: catalog and listings
- fix-echo's note is now: "`fix-echo` prints JSON; it reads unmapped when no instrument answered (rg and graft missing); a diff with nothing to echo reads ok, its ranking says why." Updated in stacks.toml and in the test's NOTES pin.
- **Catalog: 3,769 characters with all 14 stacks** (3,729 at the PIN).
- box-and-labels skill: the fix-echo sentence is corrected. Also the `changes` clause, which said "runs one step per scope"; it now reads "runs a probe (the runner's `--version`, unmapped where GitNexus cannot launch), then one step per scope" (see DISCREPANCIES 3).

### Item 6: mutants
The driver control ran first: 23 passed. Each mutant was applied once in place, with `__pycache__` cleared, bytecode off, a fresh basetemp, then restored and hash-checked. **All 14 were killed:**
- M1 argv without `--json`
- M2 the old unmapped_if
- M3 NO_ANSWER reworded
- M4 F-8 reverted (the no-answer ranking also used for removed = [])
- M5 F-8's why reverted to one text: 3 failed, 1 passed (the add-only case is unchanged by design)
- M6 graft without `--`
- M7 gitnexus without `--` (the real test also fails)
- M8 cbm in the space form
- M9 a changes scope step given back its unmapped_if (the real heading test)
- M10 the probe without its unmapped_if
- M11 cbm's old unmapped_if
- M12 a cbm marker with a space (the step reads FAILED)
- M13 the skeleton without its ranking (KeyError)
- M14 a scope step without `needs`

### Gates
All runs were in the worktree, with `--basetemp` outside every work tree. Counts are pasted from `scripts/test_summary.sh`.
- **Six files** (`6 files set=b0ad308a6f97`):
  - run 1: `pytest-exit: 0`, `pytest-summary: 574 passed in 195.20s (0:03:15)`
  - run 2: `pytest-exit: 0`, `pytest-summary: 574 passed in 191.19s (0:03:11)`
- **Every other test that names a changed file:** `stack.py gate … mode=plan graph=no` plans `5 files set=b421c90df91b`. All five are inside the six. The planner missed tests/test_vendored_manifest.py, which names the skill without its `.claude/` prefix; I ran it (NOT done 2).
- **Skill readers** (`3 files set=c37aa4860b67`), on the final skill text: `152 passed in 38.23s` and `152 passed in 40.42s`. Before the last skill edit: 39.41 s and 39.98 s.
- **`harness-ports/tests/test_context_mirrors.sh`:** `11 passed, 0 failed` in all four runs.
- **pyflakes** on the 5 .py files: 0 findings at the PIN, 0 after.

### Files (final)
| File | Lines (PIN → final) | sha256 |
|---|---|---|
| scripts/stacks.toml | 723 → 736 | 6805bdf1539c93e2cb43caffec615cd1e3594da8e8f79cf9b76ac3ca9fed9bc2 |
| scripts/jev_echo.py | 341 → 350 | be644c8f7f8568ea45c1ad265accc39d6d2b4ffa880a2a6a926a61de3061b9ba |
| scripts/jev_context.py | 978 → 979 | 36130ab90683ae356cab34e7c83f0814b13e9a668908d93e39e1d910664ec23e |
| tests/test_stack.py | 2898 → 3088 | 45e605b334b96aa4a83c0d1565e2ae761fc2a7997eaad7ac812c83069aba3e66 |
| tests/test_jev_context.py | 725 → 847 | 593ea3bcf688b6b2428f1ebd9aa429f6d85a659ca35edecaa15550e0c63ce9e7 |
| tests/test_jev_locate_echo.py | 655 → 699 | 2bf6399ff5d98281a7812b7b01b21f4a22aa979dec6a80bb2dbe46a057eb7feb |
| .claude/skills/box-and-labels/SKILL.md | 91 → 93 | 3f49116282c3689a2d897a0c59a20a7753c6677dac1c48e38465d27a35d0af84 |

test_stack.py also drops its `mmap` import, whose only user was the replaced oracle.

### Writes outside run directories
- **Shared tree:** `tasks/briefs/labeling/LS-B12-R1.patch` (untracked; the one allowed write).
- **Main repo `.git`:**
  - My worktree was registered with hooks off, then removed at 10:04Z with hooks off. `git worktree list` no longer lists it.
  - The PIN clone was `--shared` (alternates only). It is deleted.
- **codebase-memory:**
  - `~/.cache/codebase-memory-mcp/logs/cbm-daemon.log` (shared) was appended by the temporary daemons of my cbm and locate smoke runs; last write 10:01:22Z. The shared store was only searched.
  - `/tmp/cbm-daemon-0/` is the shared socket directory. Two private homes used the same socket name, so a private-HOME call can reach a shared daemon. The oracle test therefore uses a project name no store holds.
  - Every temporary daemon exited on its own. None are alive now.
- **graft:**
  - `~/.graft/telemetry.json` was last written at 09:08:27Z. That is before this segment's first command; the writer is either my pre-compaction probes or the session hook (inferred).
  - `~/.graft/update-check.json` is unchanged (checkedAt 2026-09-29T11:06:11Z). No update check and no `npm view` ran; my last graft call was around 10:04Z (F-9).
  - The fix-echo smoke refreshed `graft/.cache/` and `graft/.graph/wiring.json` inside my worktree (the D2 class).
- **gitnexus:**
  - Private HOMEs only; `~/.gitnexus/registry.json` is unchanged since 06:10:55Z.
  - The first tiny world's analyze (09:06Z) most likely downloaded LadybugDB's fts extension (2.2 MB) into its private home (inferred from analyze's install policy). Every later world and every test sets `GITNEXUS_LBUG_EXTENSION_INSTALL=never`.
  - Tests that index write `.gitnexus/` and `.claude/` into their own tmp trees.
- **Inside my worktree, now removed:** `scripts/__pycache__/jev_context.cpython-311.pyc` (the tests' jev_echo subprocess environment has no PYTHONDONTWRITEBYTECODE; D3 class) and `.sentrux-runtime/`.
- **Scratch:** the text logs are kept (360K) at `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/lsb12r1-lane/`. That includes mutants.py and the red and gate logs. The worlds and the clone are deleted.
- **Processes:** none of mine alive (cbm 0, pytest 0, stack.py 0).

### DISCREPANCIES
1. **Scratch collision (before compaction).** My first `worktree add` targeted the coordinator's `…/scratchpad/lsb12r1/wt`. It failed because the path already existed. I had written brief.md, premise_expected.txt, premise_cmds.txt and premise_actual.txt into that directory; I moved those four files to `…/lsb12r1-lane/`. None of the coordinator's files were touched.
2. **Six-file gate run 1 ran in the background**, because my Bash call had no tool timeout. It ran to its end and I waited on it with a Monitor. Run 2 ran in one foreground call.
3. **Two skill sentences changed, not one.** The `changes` clause stated the step layout, which R1 changed.
4. **Design choices** under the brief's "or a better one":
   - The fix-echo marker is the JSON ranking, not `"answered": []` (the skeleton reason above).
   - changes gets a probe step, because detect-changes has no JSON mode.
   - cbm's marker is the JSON error's opening, which covers both error literals.
5. **The set id is a hash of file names** (`pc_suite.sh set_id`), so "re-collect on the PIN" gives b0ad308a6f97 by construction. I did not take the PIN's own test count for the six files.
6. **Test (c) is not an F-1 red** at the PIN (see Item 1).

### Self-attack
1. **Can a label still read ok when its tool is missing?**
   - For fix-echo, only if the marker were lost. That needs render()'s last fallback, `{"tool","truncated"}`. It is unreachable: the label passes no budget (so 6,000), the pack peaks near 4,100 (measured 3,060), and even at BUDGET_MIN the skeleton (682 characters) keeps the ranking. Tested; mutant M13 killed.
   - For changes, a scope-step failure after a good probe reads FAILED, never ok.
   - For cbm, a missing binary is unmapped by the runner's own check. A changed error wording reads FAILED; the real-binary oracle test catches it.
2. **Can a label read unmapped when its tool answered?**
   - fix-echo: tests (a) and (b) forge both markers into repo text.
   - cbm: the escaping is measured and there is a replay test.
   - changes: a real-index heading test.
   - The residual is a tracked path for ripwire and sentrux (NOT done 4).
3. **Can a tool be handed an option?**
   - Every jev_context and jev_echo call is in the table above. Each of the three fixed calls is measured on the real tool and tested per tool; mutants M6–M8 were killed.
   - The residual is untested `--` pass-through under npx, pnpm dlx and bunx (NOT done 5).

**Evidence tiers.** Verified: everything with a pasted count, test or measurement above. Inferred: the npx pass-through, the fts download, and the telemetry.json writer. Assumed: none.
