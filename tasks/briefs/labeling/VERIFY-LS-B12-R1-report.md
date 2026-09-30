# VERIFY-LS-B12-R1: the verifier's report of record (task #385)

> **Coordinator note (2026-09-30 12:1xZ).** The verifier's hand-back, saved verbatim below (the VERIFY-LS-B12 verifier
> resumed, a sandbox adversarial-verifier; harvest run s-20260930T120857Z-7fbeb0: 715 assistant records, every one
> claude-opus-5-5, 0 refusal stops, 2 compactions; hand-back sha256 prefix 5ef5d8cc0231). Recommendation:
> MERGE-READY-WITH-FOLLOWUPS. The coordinator's gate: accepted. F-1, F-3 and F-8 are closed, each reproduced through
> the real runner at the PIN 631dc86, and no finding meets D-034's whole predicate. R1-F3 (the new real-cbm test reads
> red while another codebase-memory daemon on a different cache is live; 1 of 3 gate runs) stays a FOLLOW-UP: CI does
> not run it (no binary), no frozen criterion covers isolation between lanes, and its class is the shared per-account
> daemon (round 1's F-11), not F-1's. R1-F1, R1-F2, R1-F3, R1-F4 and R1-F6 go to issue #89 (D-108 item 2), with the
> INFO items. The D-115 round table closes at two rounds: LS-B12 (NOT-READY: F-1, F-2) and LS-B12-R1
> (MERGE-READY-WITH-FOLLOWUPS). Task #385's scope is met (five labels in `scripts/stacks.toml`, listed in CLAUDE.md
> and in skill `box-and-labels`), so the task closes. F-2 stays with task #399; round 1's follow-ups stay in issue #88.
> The verifier's deviation 1 (a top-level `cd` to the main tree at about 11:57Z) moved nothing: a subagent's primary
> directory is already that tree.

---

## VERIFY-LS-B12-R1

Written 2026-09-30 12:07:07Z (from `date -u`). Verifier: the resumed VERIFY-LS-B12 lane (sandbox, Opus 5.5). PIN: origin 631dc86 ("LS-B12-R1 landed …"). Brief: `tasks/briefs/labeling/VERIFY-LS-B12-R1-brief.md` (origin 6c8cdcc).

**RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS.**
- F-1, F-3 and F-8 are closed. I reproduced each through the real runner at the PIN.
- No finding meets the whole D-034 predicate, so there is no blocker to classify.
- One gate run of three went red. The cause is a new real-binary test that fails whenever another cbm daemon on a different cache is live (R1-F3, reproduced). I grade it FOLLOW-UP, but it is the one item where the coordinator may read determinism differently.
- Two claims rest on others' measurements, not mine: cbm's result-row escaping (the builder's measurement plus its replay test) and the registry form (`gitnexus@latest`) of npx, pnpm dlx and bunx (inferred).

Tags used below: [R] reproduced, [S] static reading, [I] inferred.

### 1. Premise
- I ran `bash scripts/premise_block.sh < premise_cmds.txt` from the main tree twice: at the start (11:06Z) and again at report time (12:02Z, main HEAD 79b0dfc).
- Both runs matched the brief's block exactly (`diff` empty) [R]. Every item holds: no commit after the PIN touches the R1 files, the sha256 prefixes match, `unmapped_if` sits at 169/316/487/497/565/603/735, the catalog is `3769 14`, and the set id is `6 files set=b0ad308a6f97`.

### 2. Is F-1 closed? Yes.
**Removed-line route.** I used round 1's probe patch in W, the worktree at the PIN; its removed line holds `answered: none`.
- Result: `## sites · ok · rc 0`, exit 0, `{"answered": ["rg-token"], "chunks": 0, …}` (run s-20260930T111503Z-370da3) [R].

**Site-snippet route.** Tiny world T, `diff=HEAD`.
- Result: ok, exit 0; answered rg-token and graft; 7 chunks (s-20260930T111503Z-b355c9) [R].
- A site snippet holds both the old marker and the new one. The new one prints JSON-escaped: `\"ranking\": \"no instrument answered` [R].

**Missing tools.** A PATH farm with only python3 and git.
- Both T and W read `## sites · unmapped — rg-and-graft unavailable`, exit 1, `"answered": []`, with the NO_ANSWER ranking (s-20260930T111620Z-e0aaf4 and s-…fd94f7) [R].

**Attacks on the new marker `"ranking": "no instrument answered`:**
- **Repo text.** It reaches stdout only inside JSON strings, where every `"` is escaped.
  - Every dict key in the pack is fixed: top level answered/chunks/extra/head/notes/ranking/tail/tool/top; head: `defect (removed)`/diff/`fix (added)`; top[]: agreement/instruments/lexical/line/path/rank/score/snippet. I measured this on two packs [R].
  - The only structural `"ranking": "` is the top-level key [S].
- **A path.** Paths appear only inside JSON strings on stdout. A quote-heavy patch name and quote-heavy src paths printed escaped (s-20260930T111720Z-f34890) [R]. jev_echo's stderr line carries counts only [R].
- **A usage message: YES.** The caller's own `--diff` value reaches stderr raw.
  - `fix-echo 'diff=x"ranking": "no instrument answered'` makes jev_echo exit 64. Its stderr reads: `jev_echo: usage: --diff x"ranking": "no instrument answered is neither a patch file nor a commit git can show (rc 128: fatal: bad revision …)`.
  - The step reads `unmapped — rg-and-graft unavailable` instead of FAILED. Exit is 1 either way (s-20260930T111633Z-de80d7) [R]. This is R1-F1.
- **A traceback or exception message.** I found no route. The parsers catch their errors, and run_tool captures each tool's stderr into the JSON notes [S].
- **Skeleton and last fallback.** The step passes no `--budget`, so render runs at BUDGET_DEFAULT 6,000.
  - The worst missing-tools pack I could build (9 notes, quote-heavy names) is 3,175 characters. It has no skeleton and keeps the marker. Through the runner it reads unmapped, exit 1 [R].
  - The builder's "3,060 at most" is therefore an undercount (R1-F5), but its conclusion holds. My bound is below 4,000 [I].
  - So neither the skeleton nor `{"tool","truncated"}` is reachable at the step's budget. The skeleton keeps `ranking[:200]` [S]; mutants M13 and N7 prove a test pins it.

### 3. Is F-8 closed? Yes.
All four nothing-to-echo cases read ok, exit 0, with `answered: []` and the reason in the ranking [R]:
- `docs/notes.md`: "nothing to echo: the input holds no unified diff (no file header), so it names no anti-pattern (Jev not asked)" (s-20260930T111742Z-670c95).
- `HEAD:src/demo/core.py`: same text (s-…1b7469).
- In-tree symlink `link.md`: same text (s-20260930T111743Z-f32b3b).
- Add-only `HEAD~1`: "nothing to echo: the diff removes no code line, …" (s-…f1d676).

**NOT done 8 is accurate.**
- Setup: removed line `out = []`, rg present, graft missing.
- Result: `unmapped — rg-and-graft unavailable`, exit 1, NO_ANSWER ranking. The notes read "not run — rg-token: no distinctive token…", "not run — rg-shape: no removed line keeps 2 or more API names" and "unmapped — graft unavailable (not found: graft)" (s-20260930T111752Z-bb5d2f) [R].
- With graft present: ok, exit 0, answered graft, 6 chunks (s-…9baf4a) [R].
- Grade: the status is honest, because nothing could answer. Its reason names rg while rg is present, but the ranking and notes tell the truth. Wording FOLLOW-UP (R1-F6).

### 4. The sweep
**cbm**
- Not-indexed error: the real binary, real HOME, a project no store holds. rc 1, stdout empty, stderr `{"error":"project not found or not indexed",…}`. The marker matches [R].
- `cbm q='{"error":"project not found'` reads ok, exit 0, with rows. The text shows only in the runner's params and `$` lines, which the check does not read; cbm does not echo the query (s-20260930T111830Z-f5899e) [R].
- Row escaping (a result row cannot hold `{"error":"`): not re-measured with a crafted real index. It rests on the builder's measurement and the CBM_ROUTES replay test (R1-F7).

**changes**
- A changed heading that holds the old marker (`Section gitnexus runner: could not launch → docs/notes.md`): probe ok, all ok, exit 0 (s-20260930T111958Z-a2ac55) [R].
- A runner that cannot launch (node present, no gitnexus/npx/pnpm/bunx):
  - The probe reads `unmapped — gitnexus unavailable` (`gitnexus runner: could not launch \`npx\` — spawnSync npx ENOENT`).
  - The scope step reads `all · SKIPPED — its prerequisite step probe was unmapped`. Exit 1 (s-20260930T112005Z-51287e) [R].
- The probe launches and the scope step fails (a tree with no index): probe ok, `## all · FAILED · rc 1`, exit 1 (s-20260930T112014Z-ce6c45) [R]. That is the honest status.
- Under strace, a changes run made no connect calls and wrote only into the log and run dirs. `find -newer` over the tree and the private HOME was empty [R].

**ripwire and sentrux (NOT done 4)**
- ripwire's normal output holds names, paths and counts only: `root="<tree>"` and `p="…"` rows, no file content [R].
- Its error echoes the caller's value raw:
  - `review files='docs/missing — run scripts/setup.sh'` reads `## ripwire · unmapped — ripwire unavailable`.
  - The control `files=docs/no-such-file.py` reads `## ripwire · FAILED · rc 1`.
  - Both exit 1 (s-20260930T112155Z-452803 and s-…6cba5b) [R]. This is R1-F4.
- A tracked path holding the marker would forge it too. The builder concedes this, and the raw `p=` and `root=` fields support it [S]. I did not reproduce it with a file so named.
- `git ls-files | grep -cF` gives 0 at the PIN for each of the four markers [R].
- sentrux: I checked it only against the builder's table (rule keys, counts, `path:function (cc=N)`) [S].

### 5. Is F-3 closed? Yes.
**search_text is unchanged.**
- The body is identical to 74285a5 [R].
- The three cases give `--help`, `--dir=/tmp/vlsb12r1-probe-dir`, and `--basetemp` (for the 412-character question) [R].

**End to end through `locate` in T, with `strace -f` on execve [R]:**
- graft: `["graft","ask","--","--help"]`.
- GitNexus: `["node",".gitnexus/run.cjs","query","--repo",".","--","--help"]`, then the global `["gitnexus","query","--repo",".","--","--help"]`.
- cbm: `--project=<slug>` and `--query=--help`.
- The dir, long and plain cases take the same forms. Every run exits 0, answered graft, gitnexus, rg and git-log (plain adds crg), and no print holds usage text.

**Real cbm on the main index (real HOME, read-only) [R]:**
- `--query=--help` gives total 1.
- `--query=--dir=…` gives 575.
- `--query=--basetemp` gives 3, the same as plain `basetemp`.
- The old space form `--query --help` printed Usage.

**Box (the World harness, LS-B10 chat form) [R]:**
- a1 to a3 (locate, the three cases) and a4 (fix-echo on a diff) each read `ran rc=0`. No usage lines appear.

**The builder's table of other calls [S] agrees at the PIN:**
- gitnexus context: the `_IDENT` pattern starts `[A-Za-z_]`.
- crg callers_of: an identifier or a `/…::name`.
- rg `-e <pattern> --` and `--files … --`.
- `git log -S<tok>`: the token is attached.
- jev_echo `graft ask "code like: …"`.
- jev_echo refuses a dash-led `--diff` (:280).
- Two line numbers are off by one (R1-F8).

**NOT done 5, measured under `unshare --net`:**
- I used stand-in local packages whose bin prints its argv: `npx --yes <folder>`, `pnpm dlx file:<folder>` and a local bunx .bin.
- Each passed `["query","--repo",".","--","--help"]` through [R].
- run.cjs's real forms are `npx gitnexus@latest …`, `pnpm --allow-build=… dlx gitnexus@latest …` and `bunx gitnexus@latest …` [S]. The registry spec and the allow-build flags were not exercised [I].

**NOT done 6 holds.**
- `stack.py explain cbm q=-x` refuses: "begins with '-' (option injection)" [R].
- A real `--query ' --help'` search is literal: total 1, no Usage [R].

### 6. No regression
- Explain, 17 cases over the 14 stacks, the 74285a5 registry against the PIN's: identical except the two `changes` cases (the probe and `needs`) and `fix-echo` (`--json`) [R].
- `locate scope=src`, three questions: identical packs [R].
- fix-echo, old against new: the same answered sets and site paths. The old version read unmapped on T's commits (F-1); the new reads ok [R].
- `changes` all, unstaged and staged: identical scope output, plus the probe section [R].
- Catalog: 3,769 characters (3,806 bytes), 14 stacks, none dropped [R].

### 7. NOT done 1 to 8, and the four tells
1. Closed at landing. The `.claude` and `.agents` copies of box-and-labels are identical (3f49116282c3689a), and `sync-skills --check` reads in sync (415 skills) [R].
2. Closed at landing. `vendored_manifest.py --check` PASS (10 roots). The manifest test passes (item 9) [R].
3. Accurate; a process item. I did not run detect-changes on the landing: it would write the shared tree's index (R1-F11).
4. Accurate for file content. Incomplete: the caller's value forges it too (R1-F4).
5. Measured; it holds (item 5).
6. Holds [R].
7. Consistent: the 74285a5..631dc86 diff touches only the 8 R1 files [S, premise].
8. Accurate [R]; wording FOLLOW-UP (R1-F6).

Tells [S]; none is real:
- **AP-51, test_jev_context.py:815.** "byte-identical" is backed by `assert jc.search_text(question, toks) == text` against pinned texts.
- **AF-AP-115.** At :829 and at test_stack.py:2887, the guards are skipif for a missing binary, with a reason. The guarded tests ran here: 574 passed, 0 skipped. At test_stack.py:2805 and :2827, the PATH farms resolve real binaries with `shutil.which`; they are not an env config channel.
- **AF-AP-175, test_stack.py:3037 and :3039.** `"HEAD:scripts/fixed.py"` and `"HEAD~1"` are revisions in the test's own tmp repo, not the shared repo's history.

### 8. Mutation
**The builder's driver.**
- Setup: an unchanged copy, run against a `git clone --shared` at the PIN, with bytecode off and `__pycache__` cleared per mutant.
- `CONTROL rc=0 23 passed in 16.98s`, then 14 of 14 KILLED, each rc=1 with "N failed" [R].
- M13 was killed through a KeyError on the missing `ranking`, which is a real kill.
- The driver's criterion is loose (rc != 0), but no kill came from a collection error.

**My own 8.**
- Strict criterion: rc 1 with failures and no errors, over whole files.
- Controls: test_stack 242 passed; test_jev_locate_echo plus test_stack 283 passed; test_jev_context 61 passed.
- KILLED:
  - N1, the bare-words marker (3 failed);
  - N2, compact JSON separators (2);
  - N3, graft `--` after the text (5);
  - N4, GitNexus `--repo .` after the text (5);
  - N5, cbm's project in the space form (4);
  - N7, the skeleton ranking cut to [:10] (1);
  - N10, `--json` ignored (9).
- **SURVIVED: N6,** `if removed and not (answered and hits):`, 283 passed. No test pins "rg answered with zero other sites reads ok" (R1-F2). The behavior at the PIN is right (s-…370da3).

### 9. Gates
W is the detached worktree at 631dc86, clean. Set `6 files set=b0ad308a6f97`. Each call ran under `timeout 590`, with `--basetemp` under /tmp/vb12r1, outside every work tree.
- Run 1 (11:41:11 to 11:44:21Z): `pytest-summary: 574 passed in 190.05s (0:03:10)`, pytest-exit 0.
- Run 2 (11:44:28 to 11:47:35Z): `pytest-summary: 1 failed, 573 passed in 187.12s (0:03:07)`, pytest-exit 1.
  - Failed test: `test_cbms_unmapped_if_is_the_binarys_own_not_indexed_error`.
  - Message: "CBM could not start because the active account daemon uses a different cache directory (active cache edcaade2…; requested cache e68c0237…)".
- Run 3 (11:52:21 to 11:55:25Z), with no cbm process alive at its start: `pytest-summary: 574 passed in 184.23s (0:03:04)`, pytest-exit 0.
- Manifest (`1 files set=21e700b8344c`): `pytest-summary: 1 passed, 56 deselected in 1.73s`, pytest-exit 0.

**Run 2, reproduced on demand [R]:**
- The test alone: "1 passed in 4.84s".
- Beside a background real-HOME `cbm cli search_graph … 'stack runner'`: "1 failed in 1.78s", with the same message (11:49Z).

**Who held the daemon [I]:**
- The active cache edcaade2… is the real HOME's; the same id shows when my own real-HOME search is the active one.
- No command of mine ran cbm between 11:44 and 11:47Z.
- The post-commit log shows no re-index in that window.
- The K2 lane ran filepacks/codemap commands at 11:43 to 11:44Z (its transcript's tool_use inputs; counts only).
- The owner of the daemon is not proven.

### Finding inventory (no severity filter)
**R1-F1: FOLLOW-UP.** The caller's `diff=` value reaches jev_echo's usage message raw. A value holding the marker reads unmapped instead of FAILED (rc 64).
- Evidence: [R] s-20260930T111633Z-de80d7.
- Contract mapping: none. R1 item 1 covers repo text in the output; this is the caller's own argument.
- Canonical path: yes.
- Material effect: the status word and its reason are false; the exit code (1) is unchanged. It needs hypothetical misuse.
- Reproduction: the command above.
- Fix: print the argument with `json.dumps`/`repr` in jev_echo's usage messages, or make the runner check `unmapped_if` on stdout only, or only when rc is 0.

**R1-F2: FOLLOW-UP.** Mutant N6 survives: the case "rg answered, no other site" is not pinned.
- Evidence: [R] the mutant run.
- Contract mapping: none.
- Canonical path: n/a.
- Material effect: none at the PIN.
- Fix: add a test with rg present, graft missing, and a distinctive removed token that matches nothing else. It should read ok, exit 0.

**R1-F3: FOLLOW-UP (the coordinator's call).** The new real-cbm oracle test fails while any cbm daemon on another cache is live.
- Evidence: [R] run 2 plus the deterministic repro.
- The reverse is [I]: while the test's own private-cache daemon lives (about 2 to 5 s), another lane's real cbm call fails the same way. That is round 1's F-11 class.
- Contract mapping: item 9 asks for two runs, but no frozen criterion covers isolation between lanes. The brief names this class ("say so and go on").
- Canonical path: the test, not the production consumer.
- Material effect: sandbox gate determinism, 1 of 3 runs red. CI is unaffected (skipif; CI has no binary).
- Ownership: inside the boundary (tests/test_stack.py).
- Fix: skip, or retry once, on the exact text "active account daemon uses a different cache directory". Or search the no-such-project name on the ambient cache so no private daemon starts; the builder's docstring says a search writes nothing, which I did not measure.

**R1-F4: FOLLOW-UP.** NOT done 4 is wider than stated: the caller's `files=` value forges ripwire's bare marker (unmapped instead of FAILED). A tracked path could too.
- Evidence: [R] for the caller route, [S] for a tracked path.
- Contract mapping: R1 item 3 is about repo text, and its own framing puts names and paths outside that. No tracked path holds the marker.
- Material effect: the status word only; review exits 1 either way.
- Ownership: the wrappers and the runner, outside R1's files.
- Fix: the wrappers exit with a distinct code for a missing binary, and the runner maps that code, not a substring, to unmapped.

**R1-F5: INFO.** The builder's "3,060 at most" pack size is an undercount; 3,175 was measured [R]. The conclusion is unchanged.

**R1-F6: FOLLOW-UP (wording).** The reason "rg-and-graft unavailable" names rg when rg was present with nothing to search [R]. The ranking and notes are truthful.

**R1-F7: INFO / not reproduced.** cbm's row escaping rests on the builder's measurement and replay (M11 and M12 killed). I skipped a crafted real index on purpose (see Skipped).

**R1-F8: INFO.** In the builder's table, two line numbers are off by one: rg `--files` is at :563 and `git log -S` at :653 at the PIN [S]. No effect.

**R1-F9: INFO.** At about 11:23Z, three of my direct real-HOME cbm runs read a cache conflict with another daemon. A retry succeeded. I stopped nothing.

**R1-F10: INFO.** NOT done 5 pass-through holds with stand-ins [R]. The registry form is [I].

**R1-F11: INFO.** NOT done 3: detect-changes on the landing commit was not measured.

**R1-F12: INFO.** The four advisory tells are not real [S].

### The blocking predicate per finding (1 mapping, 2 canonical path, 3 material effect, 4 discriminator, 5 ownership)
| Finding | 1 | 2 | 3 | 4 | 5 | Result |
|---|---|---|---|---|---|---|
| R1-F1 | no | yes | no (exit unchanged; misuse) | yes | yes | not a blocker |
| R1-F2 | no | n/a | no | yes | yes | not a blocker |
| R1-F3 | no (no frozen isolation criterion) | test only | yes (gate determinism) | yes | yes | not a blocker unless the coordinator freezes determinism across lanes |
| R1-F4 | no | yes | no (exit unchanged) | yes | no | not a blocker |
| R1-F6 | no | yes | no | yes | yes | not a blocker |

The rest are INFO.

**Blocker classes: none.**
- If R1-F1 or R1-F4 were promoted, they belong to the SAME class as F-1 (a status decided by a substring of streams that carry outside text), but the text comes from the caller, not from repo content.
- If R1-F3 were promoted, its class is "another": a test coupled to a shared per-account daemon (the F-11 class). It is not F-1's class or F-3's.

### Skipped on purpose
- **A crafted real cbm index.** A private-cache daemon would break the other lanes' cbm calls while it lives.
- **The npm registry specs.** The network cut blocks them.
- **detect-changes or analyze on the shared tree.** Either would write the shared index.
- **A tracked file named with the ripwire marker.** The builder already concedes it, and my grade does not depend on it.
- **sentrux beyond the builder's table.**

### Deviations
1. **AF-AP-249 breach.** At about 11:57Z, one Bash call began with a top-level `cd /home/user/agent-factory` before a read-only grep over absolute paths. Nothing was written.
2. **A `git clone --shared` of the main repo in my scratch (mclone)** held the mutants, so no mutant touched W or the shared tree. It is deleted.
3. **Real-HOME cbm searches, read-only:** the main project, a no-such-project name, a space-led query, and one setsid background search started on purpose at 11:49Z to reproduce run 2. Each temporary daemon exited on its own; no codebase-memory process is alive.
4. **npx, pnpm and bunx stand-in runs** under `unshare --net`, in a private HOME, with local folders. They are deleted.
5. **Attribution reads.** To find who held the run-2 daemon, I read the K2 lane's transcript (tool_use inputs and timestamps only; I printed counts per minute), the post-commit re-index log tail, and the main tree's `git log`. For other processes I read only comm, cmdline and cwd.
6. **`stack.py explain` and `catalog` in the main tree.** Both run nothing. No new `.jev/stacks` entry appeared; only the System-1 hook's own files changed.

### Cleanup
- **Worktree.** Removed with hooks off (`git -c core.hooksPath=/dev/null worktree remove --force …/vlsb12r1/wt`). `git worktree list` has no vlsb12r1 entry.
- **Deleted:** mclone, tiny, tiny2, h, hn, fakepkg, bunproj, boxw, bt, farm_ngp, farm_pg, farm_rpg, old, and /tmp/vb12r1 with every basetemp in it.
- **Kept** (3 MB, all under /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vlsb12r1/): out/ (every probe print, gate1/2/3, gate_manifest, mut_*), m/, explain/, regr/, log/ (runs.jsonl), bin/ (the drivers), the premise files and a copy of the brief.
- **State checks.** No process of mine is alive. The shared tree's `git status --porcelain` has 0 lines. I made no commit, no fetch and no hook registration, and did not use the PC bridge. The builder's lane dir and the K2 worktree are untouched.
- **S1-RATE.** I wrote both S1-RATE lines as texts of their own (s1-8c7df48f, s1-df0c1c03).