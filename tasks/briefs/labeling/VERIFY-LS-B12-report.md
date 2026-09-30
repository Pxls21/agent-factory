# VERIFY-LS-B12: the verifier's report of record (task #385)

> **Coordinator note (2026-09-30 08:1xZ).** The verifier's hand-back, saved verbatim below (a sandbox adversarial-verifier;
> harvest run s-20260930T080948Z-f22695: 415 assistant records, every one claude-opus-5-5, 0 refusal stops; hand-back
> sha256 prefix 3698f669fe9e). Recommendation: NOT-READY on F-1 and F-2. The coordinator's gate: F-1 holds the gate
> and goes to a repair round (LS-B12-R1, the first repair under D-031's budget). F-2 (code-review-graph writes its own
> gitignored state into the tree, the landed `impact` alike) is D2's class and is folded into task #399, as the
> verifier offers. Checked here: `unmapped_if` is a substring test over a step's stdout and stderr
> (`scripts/stack.py` `execute()`), and jev_echo prints repo text (the diff's lines and the sites' snippets), so F-1's
> mechanism stands. The repair also takes F-8 (the same root), F-3 (a label passes its value to a tool as an option:
> D-111's class, whatever the file boundary) and a sweep of the other nine `unmapped_if` steps (three distinct texts)
> for the same class. F-4 (`changes` on a stale index) and the other follow-ups go to one GitHub issue (D-108 item 2;
> D-031 keeps the repair on the blocker's class).

---

## VERIFY-LS-B12
Written 2026-09-30 07:58:40Z

**Gate recommendation: NOT-READY.** Two findings meet every condition of D-034's predicate: F-1 and F-2. I reproduced both on the PIN tree (e2f4f08), so no unreproduced claim sits behind this verdict. F-2 is in D2's class: an instrument writes its own gitignored state into the tree. If the coordinator folds F-2 into task #399, as it did D2, then F-1 alone holds the gate. F-3 and F-9 fall partly under the brief's item-11 wording. Their fixes live outside LS-B12's files (condition 5), so I escalate them instead of blocking on them.

### Premise (item 1)
I ran `bash scripts/premise_block.sh` from /home/user/agent-factory at 06:36Z. The output matched the brief's block exactly (1,573 bytes each, empty diff). The contract is not invalid.

### Venue and instruments
- **Worktree:** `git -C /home/user/agent-factory -c core.hooksPath=/dev/null worktree add -q --detach <scratch>/vlsb12/wt e2f4f08`. I removed it at the end.
- **Isolated worlds, where a probe needed control:**
  - a tiny git repo with its own graft, GitNexus and code-review-graph indexes;
  - a private HOME with its own GitNexus registry and graft caches;
  - PATH farms for the missing-tool cases.
- **Write instruments:** every write claim used two instruments.
  - `strace -f -e trace=%file,%process,connect`, read by a parser that follows cwd across forks (`vlsb12/writes.py`).
  - `find -newer`, the contract's own method, over the tree, the HOME caches and /tmp.
- **Network:** I measured network behavior only under `unshare --net`.
- **Label runs:** every run used `--tree <W or the tiny repo>` and `--log-dir <scratch>/vlsb12/log`. I never touched the live `.jev/` and registered no hook.

### Reproduced, static only, skipped
- **Reproduced:** items 1 to 8 and 10; findings F-1 to F-18 and F-22 to F-24; the fix experiment in F-1.
- **Static only:** F-19 (item 9); F-21; and the mechanisms I cite from third-party code:
  - code-review-graph `graph.py` and `cli.py`;
  - graft `upkeep.js` and `cli.js`;
  - GitNexus `local-backend.js`;
  - `.gitnexus/run.cjs`.
- **Skipped:**
  - (a) jev_echo on a huge in-tree file that the path type allows, such as `.gitnexus/lbug` (about 2 GB). I did not design a bounded probe, so its memory use is not measured (F-25, UNVERIFIED).
  - (b) The main tree's real post-commit refresh and its 2 GB index were not raced, because that would write the shared tree. I raced `gitnexus analyze --force` in the tiny world instead (F-22).
  - (c) cbm with a fresh HOME was not re-run, to avoid cache-dir conflicts with the live VERIFY-K2-R4 lane. The builder's mmap test covers its text.

### Finding inventory

**F-1 · BLOCKER · reproduced (PIN tree twice, tiny world once).** `fix-echo` reports `unmapped — rg-and-graft unavailable` and exits 1 even when rg answered. It happens whenever the text `answered: none` appears anywhere in jev_echo's stdout.
- **Mechanism:**
  - `unmapped_if` is a plain substring test over stdout and stderr (`scripts/stack.py` `execute()`).
  - jev_echo prints the diff's removed and added lines verbatim (`defect (removed):`, `fix (added):`), and each site's snippet too.
  - I measured two routes. On the PIN tree, the echoed diff line carried the text. In the tiny world, a site snippet carried it (site `tests/test_echo_a.py:1`, `answered: rg-token, graft`, 7 sites).
  - The repo holds the text at `scripts/stacks.toml:722`, `tests/test_stack.py:2536` and `tests/test_jev_locate_echo.py:185`. So any fix to the jev packs, or to this label's own registry lines, trips it.
- **Contract mapping:**
  - LS-B12-brief.md lines 38–40: "a missing tool reads `unmapped`, never ok". Here "unmapped" is supposed to mean the tool is missing.
  - The verify brief, item 4.
  - This input class falsifies LS-B12-report.md:217: "Over- or under-matching `unmapped_if`: countered by paired positive and negative tests".
  - The catalog note covers "rg and graft missing, or a diff that removes no code line". It does not cover this case.
- **Canonical path:** `stack.py fix-echo` on the PIN tree. The box builds the same argv.
- **Material effect:** the status is false (the tools are present and answered with 2 sites). The run ends `exit 1 — required, not ok: sites`, and the Stop-hook feedback carries the same false line.
- **Discriminator:**
  - Controls `diff=8b940f8` and `diff=e2f4f08` read `sites · ok · rc 0` on the same tree.
  - A first probe whose only site held the text past the snippet window also read ok. So the trigger is the printed text, not the site.
  - My mutant x-fix-echo-uif-answered was KILLED. But no test puts the text into a site or an echoed line.
- **Reproduction** (W = a detached worktree at e2f4f08, L = a scratch log dir):
```
python3 - "$W" <<'EOF'
import sys, pathlib
w = pathlib.Path(sys.argv[1])
old = (w / "tests/test_jev_locate_echo.py").read_text().splitlines()[184]
bs = chr(92)
new = old.replace('"answered: none" in out', '"' + bs + 'nanswered: none' + bs + 'n" in out')
(w / "echo-probe.patch").write_text("--- a/tests/test_jev_locate_echo.py\n+++ b/tests/test_jev_locate_echo.py\n"
                                    "@@ -185,1 +185,1 @@\n-" + old + "\n+" + new + "\n")
EOF
( cd "$W" && python3 scripts/stack.py --tree "$W" --log-dir "$L" fix-echo diff=echo-probe.patch ); echo rc=$?
```
  - Output at 07:51Z (run s-20260930T075141Z-d934c8): `exit 1 — required, not ok: sites` and `## sites · unmapped — rg-and-graft unavailable`.
  - The body reads `answered: rg-token` and `fixed site: tests/test_jev_locate_echo.py:185-185`, with sites `scripts/stacks.toml:722` and `tests/test_stack.py:2536`. Then `rc=1`.
- **Suggested fix** (inside LS-B12's files; I measured it on a scratch clone at the PIN): add `"--json"` to the step's argv and set `unmapped_if = '"answered": []'`.
  - JSON escapes every quote inside repo text, so no snippet or echoed line can spell the key form.
  - `stack.py list` exits 0.
  - The F-1 probe then reads `sites · ok · rc 0` (exit 0).
  - A PATH with neither rg nor graft still reads `unmapped — rg-and-graft unavailable` (exit 1).
  - Cost: the print becomes one JSON line, and 5 pins in `tests/test_stack.py` change (`5 failed, 228 passed in 51.70s` on the clone):
    - the registry-and-catalog test;
    - the explain pins `[fix-echo]` and `[fix-echo-patch]`;
    - `test_fix_echo_reads_unmapped_when_neither_rg_nor_graft_answers`, which asserts the markdown line (the status itself still read unmapped);
    - `test_fix_echo_lists_the_other_site_when_rg_answers`.
  - A line-anchored text is not available. The loader refuses `unmapped_if = "\nanswered: none\n"` with `unmapped_if: a literal output text of one line` (rc 3).
  - Add a red test: a patch whose removed line holds the text must read ok.

**F-2 · BLOCKER (D2's class, can be folded into #399) · reproduced (PIN tree once, tiny world with warm and stale graphs).** `locate` writes in the repo tree through code-review-graph (crg), with a warm graph too.
- **What happens:**
  - When q holds an identifier, jev_locate runs `code-review-graph query callers_of <name>` (`jev_context.py:503–523`). It skips crg when graph.db is absent, so it never creates a graph.
  - crg's `query` is not in its `_read_only_db_cmds` (`cli.py:1688–1694`). So crg resolves its data dir with create=True and opens graph.db read-write in WAL mode (`graph.py:188–196`).
- **Measured on the PIN tree** with a copy of the main tree's graph (run s-20260930T073759Z-befe4e, q=`cap_lines cuts the print before the verdict line`, rc 0):
  - graph.db opened with O_CREAT (read-write);
  - `graph.db-wal` and `graph.db-shm` created, then unlinked;
  - `.code-review-graph/.gitignore` created (the copy lacked it);
  - `find -newer` lists `.code-review-graph` and `.code-review-graph/.gitignore`;
  - graph.db's sha256 was `ef52f527046078af` before and after.
- **Contract mapping:**
  - LS-B12-brief.md line 41: "Nothing written in the repo tree outside the run directory: measure each step (the files under the tree newer than a stamp file ...)".
  - Verify brief items 2 and 11.
  - The report's locate line (LS-B12-report.md:73, "Writes: the HOME cbm files. Also writes in the tree when the graph is stale (D2)") misses these writes. crg never answered in the builder's runs.
- **Canonical path:** `stack.py locate` on the PIN tree.
- **Material effect:** every identifier query changes the tree, and the contract's own `find -newer` check flags it.
  - On the main tree it would still list `.code-review-graph`. That tree's `.gitignore` already exists (since 2026-09-07; `*`, check-ignore line 3), and its graph.db is already WAL (header bytes 18–19 = 2, 2). So I found no lasting file and no content change.
  - A schema migration would write graph.db if the installed crg were newer than the graph (`graph.py:199–205`, `migrations.py:259–284`). I did not measure that.
- **Discriminator:**
  - A q with no identifier prints `not run — code-review-graph: no identifier in the question` and writes nothing there.
  - Mutant x-locate-no-crg removes the writes. Two explain pins kill it.
- **Reproduction:**
```
mkdir -p "$W/.code-review-graph" && cp /home/user/agent-factory/.code-review-graph/graph.db "$W/.code-review-graph/"   # 433 MB, read only on the source
touch "$L/stamp"
( cd "$W" && strace -f -qq -e trace=%file -o "$L/crg.trace" python3 scripts/stack.py --tree "$W" --log-dir "$L" locate "q=cap_lines cuts the print before the verdict line" )
grep -E 'code-review-graph/(graph\.db(-wal|-shm)?|\.gitignore)"' "$L/crg.trace" | grep -E 'O_CREAT|unlink'
find "$W/.code-review-graph" -newer "$L/stamp"
```
- **Suggested fix**, one of:
  - (a) Fold it into #399 with D2. Wave-1 `impact` runs the same crg queries (stacks.toml:299 and 305).
  - (b) Inside LS-B12's files: add `--instruments graft,gitnexus,cbm,rg,registry,quirks,git-log` to locate's argv and repin 2 explain tests. This loses the callers instrument.
  - (c) Outside LS-B12: a read-only reader in jev_context. crg's CLI opens GraphStore read-write for every command (`cli.py:1702–1730`).

**F-3 · FOLLOW-UP (escalate; D-111 class) · reproduced.** `locate` can pass q to graft, GitNexus and cbm as an option. This happens when q starts with whitespace and then a dash, or when a q over 300 characters has a flag as its first quoted token.
- **Mechanism:**
  - The runner's text type refuses a leading `-`.
  - But jev_context's `clean()` strips leading whitespace, and `search_text()` puts quoted tokens first.
  - The result goes to `graft ask <text>`, `node .gitnexus/run.cjs query <text> --repo .` and `codebase-memory-mcp cli search_graph ... --query <text>`, with no `--` before it.
- **Measured:**
  - q=` --help`:
    - graft printed its help (exit 0), and the pack reads `answered: graft, rg, registry, quirks, git-log`;
    - `gitnexus query --help` reads unmapped (non-JSON output).
  - q=` --dir=/tmp/vlsb12-probe-dir`: graft said "missing required argument 'query'" and GitNexus said "unknown option". No directory was created.
  - A realistic 338-character question with `--basetemp` in backticks made the search text `--basetemp ...`:
    - graft and GitNexus said "unknown option '--basetemp'";
    - cbm said "error: unknown flag --basetemp for this tool";
    - the same question with plain `basetemp` found 3 hits.
  - Through the box, `│ q:  --help` ran as q=' --help' (F-16, a9).
  - No extra program ran and nothing was written.
- **Bound:**
  - Only one element can be injected, because clean() joins everything into one.
  - All of `graft ask`'s options are read-only (-n, --source, --full, --in, --json, --no-graph-rank, --no-refresh, -h), and so are `gitnexus query`'s (-q, -r, --branch, -c, -g, -l, --content, -h).
  - I did not enumerate cbm's flags. I did not run cbm for this, to spare the shared daemon.
  - The effect is wrong or empty evidence, plus one false `answered` (graft's help text).
- **Contract mapping:** verify brief item 3; the runner's no-leading-`-` rule. This is not a frozen LS-B12 criterion. `find` (it passes q raw, leading space kept), `cbm` (F-12) and `fix-echo` are safe.
- **Reproduction:** `( cd "$W" && python3 scripts/stack.py --tree "$W" --log-dir "$L" locate "q= --help" )`
- **Suggested fix:** in jev_context.py, outside LS-B12. Either refuse a leading `-` after clean(), or pass `--` to graft and GitNexus before the query.

**F-4 · FOLLOW-UP · reproduced.** On a stale index with a real uncommitted change, `changes` reads `all · No changes detected.` (ok, rc 0, exit 0). Nothing in the run says the index is stale.
- **Measured:** in the tiny world, the index was at 425d1fe and HEAD at c02b332, with an uncommitted edit to `new_helper`, a function added after the index (run s-20260930T065706Z-c0365e).
- **Contract mapping:**
  - LS-B12-brief.md lines 27–29 require only the partial and truncated headlines. Those are met (F-14).
  - The only disclosure is the catalog note, and it is not in the run's output.
  - Item 5's question ("any run reads ok while the index is stale, with nothing that says so?") therefore gets the answer yes.
- **Suggested fix:** inside LS-B12's files, add a first step that compares the index's last commit with HEAD and headlines "index stale".

**F-5 · FOLLOW-UP (not reachable at the PIN in this container) · reproduced under the network cut.** `.gitnexus/run.cjs` falls back to `npx gitnexus@latest` when no `gitnexus` is on PATH.
- **Measured:**
  - With a PATH of node, npm and npx only, and the network cut: `## all · FAILED · rc 1 · 72.22 s`. npm said `request to https://registry.npmjs.org/gitnexus failed, reason: getaddrinfo EAI_AGAIN`, and strace saw 20 connect attempts. The run read FAILED, not unmapped, and npm wrote a log in HOME.
  - With a node-only PATH: unmapped, correctly (F-24).
- **Why it is not reachable here:** this container keeps `gitnexus` beside `node` in /opt/node22/bin, so the ladder's first rung always wins. `GITNEXUS_INVOCATION` is unset but would force the npx rung.
- **Risk elsewhere:** with the network up and gitnexus absent, the fallback would fetch and run an unpinned package (standing rule 13).
- **Contract mapping:** LS-B12-brief.md line 25 prescribes run.cjs, and wave-1 `impact` shares it.
- **Suggested fix:** call `gitnexus` directly (a contract amendment), or pin the fallback.

**F-6 · FOLLOW-UP · reproduced.** `why fn=<x>` falls back silently to the file's history when `git log -L` finds no function.
- **Measured:** `fn=Reader.read_all` (a class-qualified name the symbol type allows), `fn=parse_window:x` and `fn=no_such_fn` each read ok. Each prints the file's commits under the `git log -L` heading.
- **Regex use:** why.sh passes fn and the file's basename as regular expressions to `git log -L :<fn>:<file>` and to `grep -e`, so `.` matches any character.
- **Disclosure:** the report states the fallback (LS-B12-report.md:67); the output does not.
- **Suggested fix:** in why.sh, print a "no function" line and use `grep -F`.

**F-7 · FOLLOW-UP · reproduced.** `why`'s impact section has three problems.
- Without gitnexus on PATH, `why` reads ok and the section is silently absent. This is the builder's known adjacent defect.
- With two repos in the registry, it prints `risk None · ? direct callers · ? flows (index unavailable)`. An unknown symbol prints `risk UNKNOWN … (index unavailable)`.
- why.sh runs `gitnexus impact "$SYM"` with no `--repo`. So it reads whichever repo the registry picks and ignores `--tree`. The live registry holds only agent-factory.
- **Suggested fix:** in why.sh, derive `--repo` from the tree, and print a line when gitnexus is missing.

**F-8 · FOLLOW-UP · reproduced.** `fix-echo` reads `unmapped — rg-and-graft unavailable` (exit 1) on any diff with nothing to echo.
- **Measured cases:** a non-diff file, a `HEAD:path` blob, an in-tree symlink to a non-diff, and an add-only commit.
- The body says `nothing to echo: the diff removes no code line`, but the status blames the tools. The catalog note discloses this.
- A symlink out of the tree is refused (exit 2) with the path type's message.
- **Root:** the same as F-1. `answered: none` means "no instrument answered", not "rg and graft are absent".
- **Suggested fix:** give the nothing-to-echo case its own status text.

**F-9 · FOLLOW-UP (escalate to #399) · reproduced under the network cut.** Once a day, any label that calls graft (find, locate, fix-echo, ctx) starts graft's update check. That is a detached `node .../graft/dist/cli.js _update-check`, and it runs `npm view @nanonets/graft version`.
- **Measured** (tiny world, a private HOME whose update cache was stale; run s-20260930T073854Z-138f26):
  - HOME writes: `.graft/update-check.json` (a tmp file, then a rename, twice) and `.npm/_logs/2026-09-30T07_38_57_285Z-debug-0.log`;
  - one DNS attempt to 8.8.8.8:53, which got ENETUNREACH under the cut;
  - the child runs in its own session, so the runner's group kill cannot reach it.
- **Gate:** a 24-hour TTL (`upkeep.js:56`, `:105`). There is no environment opt-out (`upkeep.js:116–133`, called from the preAction hook at `cli.js:161–175`).
- **Production timing:** the real cache shows `checkedAt` 2026-09-29T11:06:11Z. So the first graft call after 2026-09-30T11:06:11Z, whether a label's or the coordinator's own, will run the check.
- **Contract mapping:**
  - LS-B12-brief.md line 42 allows HOME writes if they are reported. The report lists only cbm's.
  - Item 11 may count `npm view` as a command a label should not run.
- **Ownership:** the fix is outside LS-B12. The label only changes who triggers the check, and that it runs outside the permission checks (D-111).
- **Suggested fix:** fold it into #399 with D2, and correct the report's write list.

**INFO and remaining items (F-10 to F-25)**
- **F-10 (INFO; matches the builder's report line 54).** cbm's writes:
  - HOME `_config.db` opened read-write, and `logs/cbm-daemon.log` appended;
  - /tmp/cbm-daemon-0 lock and socket files created, then removed;
  - `find -newer` over the cache lists only the daemon log, so no project database changed.
  - Two daemons outlived their steps by about 5 and 6 s, then exited on their own.
  - `--tree` does not scope cbm: it always searches project home-user-agent-factory.
- **F-11 (INFO).** A cache-root conflict reads FAILED, which is right: the binary is present and returned an error.
  - Two of my cbm runs failed this way (`the active account daemon uses a different cache directory`) because of the VERIFY-K2-R4 lane's cbm.
  - My private-HOME cbm runs may have caused the same failure for that lane at about 06:59–07:00Z, 07:37–07:38Z and 07:40Z.
- **F-12 (INFO).** cbm's q is safe. Values with a leading space and `--project=`, and a JSON quote, were searched literally (91 results).
- **F-13 (INFO).** `changes` with a `base` is safe.
  - GitNexus passes base untrimmed, before `-U0`, with no `--` (`local-backend.js:631`). The runner refuses a leading `-`.
  - `' HEAD'` read FAILED, and so did a base that names a file. `HEAD@{1}` read ok. No option injection is possible.
- **F-14 (INFO).** Both headlines work as the contract asks:
  - a mode-only change gives `all · PARTIAL RESULT: ...`, FAILED rc 1, exit 1;
  - 1,005 symbols give `compare · LISTING CAPPED: ...`, ok rc 0.
  - Two of the builder's headline mutants die only by explain pins, but the behavior is real.
- **F-15 (FOLLOW-UP, the runner, outside LS-B12).** The runner echoes raw separators and bounds no path length.
  - U+2028 in q prints raw in the `params:` and `$` lines of the Stop-hook feedback (box b1, 2 occurrences).
  - A refused two-line value prints its raw newline (`stack: q=first line` / `second line refused: ...`, box a3).
  - CONTROL_RE covers headlines only.
  - The path type has no length bound: a 120 KB path gave FAILED rc 128 and `headers alone are over the cap`.
- **F-16 (INFO).** Through the box (LS-B10's World harness, a temp state dir):
  - a1 (locate body) ran rc 0.
  - a2 (cbm body) ran and read unmapped. This was by design: that PATH had no cbm.
  - a3 refused: `q=first line second line refused: a text holds no NUL and no newline`.
  - a4 refused: `repeated key 'q'; known keys: q, scope`.
  - a5 refused: `unknown key 'zz' for stack locate; known keys: q, scope`.
  - a6 refused: `malformed (the parameter line q: sets the body parameter of stack locate, which the body below ┄┄┄ sets too)`.
  - a7 refused: `malformed (a body below ┄┄┄, but stack changes names no body parameter ...)`.
  - a8 (changes compare) ran rc 0.
  - a9 ran q=' --help' (F-3).
  - b1 ran (F-15).
- **F-17 (INFO; FOLLOW-UP for #388).** The catalog and ratings behave as specified.
  - The catalog is 3,729 characters (3,766 bytes) and shows all 14 stacks, leaving 271 characters of room.
  - With a 15th typical one-note stack, it drops the last whole stack. It then prints `… 1 of 15 stacks not shown (this catalog stays under 4,000 characters)` at 3,838 characters. Task #388's two labels will therefore drop stacks.
  - Ratings are accepted for cbm, why, locate and fix-echo runs.
  - A rating for `changes` is refused (rc 2): `stack: rating: run s-20260930T073303Z-81d6f3 is a changes run, and only a rated stack takes ratings (cbm, ctx, echo, find, fix-echo, impact, locate, review, why)`. An unknown run id is refused too.
- **F-18 (INFO; one FOLLOW-UP).** Mutation (item 8):
  - Control first: `CONTROL-OK ... 233 passed in 52.64s`.
  - All 20 of the builder's mutants were KILLED, with the same verdicts as its results.txt.
  - Of my 5 extras, x-cbm-cap-lines-1 SURVIVED: no test reads cbm's cap_lines. x-fix-echo-notes-dropped, x-why-okrc-128, x-fix-echo-uif-answered and x-locate-no-crg were KILLED.
  - Five kills come only from the explain pins (argv text): changes-all-no-headline, changes-staged-takes-base, locate-scope-flag, x-why-okrc-128 and x-locate-no-crg.
- **F-19 (INFO, static).** The two AP tells from item 9:
  - AF-AP-115 is not real at `tests/test_stack.py` lines 2489, 2510, 2521, 2731, 2777, 2781, 2799 and 2833. These are skip guards, a byte oracle for the cbm binary, and PATH farms built from resolved paths. Each label run gets an explicit PATH.
  - AF-AP-175 is real in form at 2683 (and in wave 1 at 1254 and 1805). `git(ROOT, "rev-parse", "HEAD")` is read at a different moment from the label's own read. It gives a false red only if HEAD moves mid-test. The fix is to compare against the HEAD the label printed.
- **F-20 (INFO; which test is UNVERIFIED).** The gate itself wrote into its tree:
  - `graft/` (64 MB, 06:48:42Z in run 1, and again in run 2);
  - `.claude/hooks/__pycache__/`.
  - In the shared tree, the same test would refresh the live graft caches. I did not trace which test does it.
- **F-21 (UNVERIFIED).** GitNexus's partial and capped branches beyond the two I ran (F-14) are reviewed statically only (`local-backend.js:4225–4245`, `4400–4486`; `cli/detect-changes-format.js`; `cli/tool.js`).
- **F-22 (INFO).** Concurrency (item 2):
  - `changes` ran during `gitnexus analyze --force` at three offsets (0.5, 1.5 and 3 s), and each run was ok and correct.
  - Two concurrent `locate` runs on a stale graft graph were both ok.
- **F-23 (INFO).** With every code instrument missing, `locate` reads ok and `answered: registry, quirks, git-log`. The builder's claim that `answered: none` is unreachable (its NOT DONE 6) holds for this repo.
- **F-24 (INFO).** `why` and `changes` wrote nothing outside the run dir, under strace and find alike. `changes` with a node-only PATH reads unmapped from run.cjs's real text: `gitnexus runner: could not launch \`npx\``.
- **F-25 (UNVERIFIED).** See skipped item (a): jev_echo reading a huge in-tree file.

### Gates at the PIN (item 10)
- **Command** (in W, after an rg warm-up): `( cd $W && timeout 590 bash scripts/test_summary.sh tests/test_stack.py tests/test_session_hooks.py tests/test_search_intercept.py tests/test_ls_req.py --basetemp /tmp/vb12/g1 )`. Run 2 used `/tmp/vb12/g2`. Both basetemps were outside every work tree.
- **Set id:** `4 files set=d9c691f4f8de`, from `bash scripts/pc_suite.sh set-id -- <files>` in the premise block.
- **Run 1** (06:47:44–06:50:12Z): `pytest-summary: 463 passed in 147.73s (0:02:27)`, `pytest-exit: 0`.
- **Run 2** (07:41:55–07:44:17Z): `pytest-summary: 463 passed in 141.45s (0:02:21)`, `pytest-exit: 0`.

### Deviations (disclosed)
1. **A fetch in the shared repo.** The brief was not at the PIN, so I ran `git -C /home/user/agent-factory fetch -q origin` and then read the brief at origin 6d07538. That updated origin's refs in the shared repo, which is a git write beyond the worktree exception.
2. **A shared clone.** The builder's driver needs a clone, so I made a `git clone --shared --no-checkout` of the main repo into my scratch, detached at e2f4f08. It wrote nothing to the source, and I deleted it.
3. **Reads of the main tree and real HOME.** None of these is a secret file; all were read only:
   - a copy of the main tree's 433 MB graph.db, taken for F-2 (removed with W);
   - that tree's `.code-review-graph/` listing and graph.db's 100-byte header;
   - `/root/.graft/update-check.json` and `~/.gitnexus/registry.json`.
4. **cbm on the real HOME.** Some cbm runs used the real HOME, which touched the production cache as any cbm call does (F-10). F-11 discloses the possible conflicts with the K2-R4 lane.
5. **Denied mount.** The permission classifier denied a read-only bind mount of the main tree (`unshare --mount`). I did not retry it or work around it.
6. **Transcript read.** From my own transcript I read only text blocks and tool_use inputs, never a thinking block.
7. **Mutation driver.** `vlsb12/mutate_extra.py` reads the builder's driver text from `lsb12/mutate.py` (read only; a byte copy is at `vlsb12/mutate.py`). It re-points only the scratch root and runs the driver in memory. The builder's files are untouched.

### Cleanup
- W is removed (`git worktree remove --force`, rc 0; `git worktree list` has no vlsb12 entry).
- Deleted: the clone, the tiny worlds, the private HOME, the PATH farms, /tmp/vb12 and the raw strace files.
- No process of mine is alive: a check by comm finds no codebase-memory, graft or strace. The K2-R4 lane's processes were left alone.
- The shared tree's status holds nothing of mine.
- Evidence kept (1.4 MB) under /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vlsb12/:
  - F-1: `fe_repro_final.txt`, `fe_pin2.txt`, `fe_false.txt`, `fe_8b940f8.txt`, `fe_e2f4f08.txt`;
  - probe outputs: `m/crg_pin/`, `m/locate_stale_upd/`, `m/injhelp/`, `m/changes_stale_newfn/`, `m/changes_modeonly/`;
  - gates and mutants: `gate1.txt`, `gate2.txt`, `mutants/results.txt`;
  - catalog, ratings and box: `catalog.txt`, `catalog15.txt`, `rate.txt`, `boxprobe_feedback.txt`;
  - other: `npx.txt`, `nolaunch.txt`, `log/runs.jsonl`.
