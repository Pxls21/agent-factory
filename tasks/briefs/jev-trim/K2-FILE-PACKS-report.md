> Coordinator note (2026-09-29 05:5xZ): the report of record, extracted by `scripts/stack.py harvest` (run s-20260929T055730Z-2d67ea). Served model: claude-opus-5-5 on all 307 assistant records, 0 refusal stops, 2 tool-error clusters. `report_lint`: 10 refs, all OK. Local ids: none cited. The five files' sha256 prefixes match the report's table. The coordinator lands the five files as GATED-PENDING-VERIFY; the registration and the post-commit patch wait for an independent verify (VERIFY-K2).

# K2 (task #353, D-106): file packs — lane report

K2 is built and tested. It is not registered, not committed, and the post-commit patch is not applied: all three are your landing steps.

- **Status:** DONE, GATED-PENDING-VERIFY. The tests pass on the final bytes, twice.
- **Clock at hand-back:** Tue Sep 29 05:52:59 UTC 2026 (05:5xZ).
- **Lane:** sandbox, Opus 5.5. No subagent, no PC bridge, no outward action, no git write in the shared tree.
- **Evidence tiers:** every number below is verified (pasted from a command run on the final bytes) unless marked inferred.
- **Citations:** `report_lint: 10 refs — OK 10, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## NOT done (first-class)

1. **Registration is not added.** The exact entries are under "Registration" below. Adding them forces edits in `tests/test_session_hooks.py` (listed there) and a regeneration of the vendored manifest, because `.claude/settings.json` sits under `.claude/`.
2. **The post-commit patch is not applied** to `scripts/hooks/post-commit` in the shared tree, as the brief's amendment says. It is proven on a clone (item 5).
3. **The design's P2 source "its open issues" is not built** (D105-DESIGN-v1.md §10.3). The brief's source list is exact and leaves it out.
4. **AF-AP-70 is open for the code-map reads.** This is a check-then-open race:
   - `_code_part` checks the code pack and the working file by name (`scripts/filepacks.py:342`, `S_ISREG`).
   - codemap's existing readers then reopen them by name: `_load_pack` (`scripts/codemap.py:865`) reads with `read_text` (`scripts/codemap.py:868`), and `lookup` reads the working file.
   - A FIFO or link swapped in between the check and the reopen stalls the hook until the wrapper's 55 s timeout. A FIFO or link planted before the call is refused.
   - My own reads go through System-1's `read_regular` and are safe. Closing this needs `_load_pack` to open the way System-1's `open_regular` does, which changes existing codemap code outside my additive boundary.
5. **Two defects in my own work are not registered.** I found and fixed both before the gates. `docs/INCIDENT-LOG.md` is outside my boundary; they are candidates for you (DISCREPANCIES 13 and 14).
6. **The ripwire call-graph union (51 test files for the .py paths) was listed, not run.** It goes beyond the brief's gate rule.
7. **Latency: only one optimization.** I deferred the `subprocess` import. Once registered, the hook costs about 100 ms per Read, Edit, Write and Bash call through the wrapper (item 7).

## Premise re-run (item 1): no difference

I ran `bash scripts/premise_block.sh` from the main tree at 04:27:19Z, with HEAD at c74e0fb (origin's tip then). Every line equals the brief's, including the demo's 603 bytes:
```
$ git merge-base --is-ancestor 3cd69de HEAD && echo 3cd69de-is-an-ancestor-of-HEAD
3cd69de-is-an-ancestor-of-HEAD
$ sha256sum .claude/hooks/system1-context.py scripts/codemap.py scripts/hook_context.py scripts/hooks/post-commit tasks/briefs/jev-trim/k2_authoring_probe.py | cut -c1-16,65-
df094d99240380bc  .claude/hooks/system1-context.py
f77c79f914348600  scripts/codemap.py
1f4912ce9389185d  scripts/hook_context.py
23c605f1ec16c1d6  scripts/hooks/post-commit
10ec956aea6b79a0  tasks/briefs/jev-trim/k2_authoring_probe.py
$ grep -n '^TOOL_BUDGET\|^TOOLS = \|^def shell_code\|^def command_positions\|^def plan_tool\|^def window_id\|^def open_regular\|^class WindowLock\|^def reset\|^def main' .claude/hooks/system1-context.py
63:TOOL_BUDGET = 2048
77:TOOLS = ("Write", "Edit", "Bash")
181:def command_positions(cmd):
357:def shell_code(cmd):
568:def plan_tool(payload, table, seen, budget=TOOL_BUDGET):
868:def window_id(payload):
875:def open_regular(path, flags, follow=False):
936:class WindowLockTimeout(TimeoutError):
940:class WindowLock:
990:def reset(payload, state, now):
1014:def main(argv):
$ grep -n '^PACK_DIR\|^def pack_path\|^def lookup\|^def edit_context\|^def _load_pack' scripts/codemap.py
39:PACK_DIR = Path(".jev") / "codemap"
118:def pack_path(root: Path, rel: str) -> Path:
865:def _load_pack(root, rel):
878:def lookup(path, line, end_line=None, root=None):
918:def edit_context(file_path, old_string, root=None, replace_all=False):
$ grep -n 'codemap refresh' scripts/hooks/post-commit | cut -c1-100
165:printf '%s %s codemap refresh %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$(git rev-parse --short HE
$ grep -n '"matcher"' .claude/settings.json
51:        "matcher": "Edit|Write|Read",
99:        "matcher": "Grep|Bash",
108:        "matcher": "Write|Edit|Bash",
$ ls scripts/filepacks.py tests/test_filepacks.py .jev/filepacks 2>&1 | cut -c1-90
ls: cannot access 'scripts/filepacks.py': No such file or directory
ls: cannot access 'tests/test_filepacks.py': No such file or directory
ls: cannot access '.jev/filepacks': No such file or directory
$ python3 tasks/briefs/jev-trim/k2_authoring_probe.py --transcript /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl --bytes 792000000 --rev 3cd69de
A windows=141 bytes=792000000
A files per window, Read/Edit/Write: median 5 p90 13 max 25
A files per window, reader Bash: median 32 p90 58 max 93
A files per window, the union: median 32 p90 60 max 93
A share of the union seen only through reader Bash: 0.834
A files per reader call: median 1 p90 3 max 23 calls 6003
B source ledger: lines 1749 bytes 1304869
B source decisions: lines 144 bytes 136355
B source incidents: lines 866 bytes 694738
B source skills: lines 2796 bytes 300265
B code files 1174
B lines naming a file, ledger: median 0.0 p90 2 max 29 none 0.79
B lines naming a file, decisions: median 0.0 p90 0 max 3 none 0.98
B lines naming a file, incidents: median 0.0 p90 1 max 30 none 0.85
B lines naming a file, skills: median 0.0 p90 0 max 12 none 0.93
$ printf '{"tool_name":"Edit","tool_input":{"file_path":"%s/scripts/stack.py","old_string":"def cmd_run("}}' "$PWD" > /tmp/k2-premise-edit.json && python3 scripts/codemap.py demo /tmp/k2-premise-edit.json | sed -n '2p;3p'
enclosing: cmd_run
--- the entry L2b would inject (603 bytes) ---
```
- **HEAD moved since the re-run.** It is now 7db59b9, after your commits 81ef2a9, aa85f5e and the VERIFY-LS-B9 round-4 report (push_clean rewrote that one from 02a9276).
- **No premise file changed.** At HEAD: `scripts/codemap.py` is f77c79f914348600 and `scripts/hooks/post-commit` is 23c605f1ec16c1d6. The last commit to touch either is L2a (22b34e6).
- **One temp file:** the premise command rewrote `/tmp/k2-premise-edit.json` with the same bytes. I left it in place.

## Files (final bytes; the gates ran on exactly these)

| file | lines | sha256 | change |
|---|---|---|---|
| `scripts/filepacks.py` | 918 | 46ee3aea2f1e428bd965dbd8ebd73bd0c8cc35d4f0d92da8609040c9bd239ec6 | CREATE |
| `tests/test_filepacks.py` | 887 | 20688549adc7c29683fd7b29b8065e236d32cf0c8ed50c6da4da80ff65286e78 | CREATE |
| `tasks/briefs/jev-trim/K2-post-commit.patch` | 26 | 71ba4c2c0cec81abd5d672d7f89d246a39a11cf0a530523b00d48e15affe9ef1 | CREATE |
| `scripts/codemap.py` | 1115 | ea28c5add97fac240cbed841ab0e4fb4c8469c1a198552ee04a11d4c9b055823 | MODIFY: 60 lines added, none removed (`@@ -947,0 +948,60 @@`): `FILE_SYMBOLS` and `file_entry` (`scripts/codemap.py:951`) |
| `tests/test_codemap.py` | 846 | a1b9fa4652c471819300708c05c510687d8e92e4336b5c2973e92db5c66328cb | MODIFY: +44 −1 (`check_file_entry` at `tests/test_codemap.py:401`, its `LOOKUP_CHECKS` entry on the one changed line, 3 mutants) |

**Written outside git** (gitignored `.jev`):
- `.jev/filepacks/`: 1,691 packs, `TRACKED.txt` and `BUILD.json`, built at 7db59b9
- `.jev/filepacks.lock`
- `.jev/pycache/` (the System-1 hook's bytecode cache)
- two gate-plan run directories, `.jev/stacks/s-20260929T052237Z-77103d` and `.jev/stacks/s-20260929T052255Z-3c120d`

**Left behind:** no process of mine is running, and no worktree, clone or temp directory of mine remains.

**Evidence logs:** `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k2-lane-353/logs/`, plus `replay-final2.txt` beside it.

## Items

### Item 2, P2: the builder (`filepacks.py build`)

- **HEAD is resolved once**, with `git rev-parse --verify HEAD^{commit}` (`scripts/filepacks.py:704`).
  - The SHA is threaded to `ls-tree -r -z`, to one `git cat-file --batch` for every source (`_blobs`, `scripts/filepacks.py:713`), and to both `git log` calls.
  - The test builds at an older SHA while HEAD has moved on (check `build-sha-threaded`, mutant `reads-at-head`).
- **One regex pass per source**, never one search per file.
  - A token is a maximal run of path characters that holds a `.` or a `/`.
  - It counts when it is a tracked path as written, or after dropping a trailing `.`, the repo's absolute prefix or `./`.
  - So `scripts/stack.py` never matches inside `scripts/stack.py.json` or `x/scripts/stack.py` (mutants `suffix-match` and `extension-strip`).
- **What each mention keeps:**
  - the source and the line number;
  - the registry id on a registry row (`D-NNN`, `AF-AP-NNN`);
  - the ledger line's bold headline, at most 160 characters;
  - a snippet of at most 240 characters around the first mention in the line.
- **What each pack keeps:**
  - the newest 3 mentions per source (the highest line numbers);
  - the newest 3 briefs, by each brief's last commit;
  - the newest 3 of the last 400 commits;
  - per-group counts.
- **How packs are written:**
  - atomically (temp file, then rename, mode 0600), and only when the bytes change;
  - a pack whose file has nothing any more is removed, along with stray temp files and links;
  - `TRACKED.txt` and `BUILD.json` are written last;
  - one build runs at a time (a flock in the state directory).

Two runs on this tree, final code, HEAD 7db59b9:
```
filepacks build: 7db59b9 1691 packs (51 written, 0 removed, 0 failed) of 9944 tracked files in 2565 ms
filepacks build: 7db59b9 1691 packs (0 written, 0 removed, 0 failed) of 9944 tracked files in 2586 ms
{"commit": "7db59b95dec54470867d97509a37e9a6acaa9bec", "failed": 0, "files": 1691, "missing": [], "ms": 2586, "removed": 0, "schema": 1, "tracked": 9944, "written": 0}
```
An earlier pair at 02a9276, before a small code edit: 2722 ms (1,691 written) and 2692 ms (0 written).

### Item 3: the reader, `entry(rel, tool_input, budget)`

- **For a code file with a code-map pack, the code part comes first:**
  - **Edit:** `codemap.edit_context`. Its symbol becomes the window key.
  - **Read with `offset` and `limit`:** `codemap.lookup` over the range. When no single symbol holds the range, the new file-level reader runs over the range and lists the symbols in it.
  - **Anything else:** the new `codemap.file_entry`. It shows the symbol count, the first 8 top-level symbols with their spans, the tests, the registry rows and the instruments.
- **Then the pack's lines:**
  - a head line with the counts, the pack path and the build's commit;
  - then mentions, taken in turn from ledger, incidents, decisions, briefs, skills and commits.
  - The whole entry is cut on a line boundary within the budget.
- **Stale code never passes as fresh.** A stale code part goes out only with the code map's own mark, "STALE: the file changed" (`STALE_MARK`, `scripts/filepacks.py:398`). If the mark does not fit, nothing is shown.

Measured in process by the replay over the recorded payloads:
```
entry ms: p50 0.216 p95 0.809 max 6.241 over 5438 entries
```
The aim was p95 under 5 ms; it is met.

### Item 4, P1: the hook (`hook`, `hook --reset`)

- **Triggers:**
  - Read, Edit and Write of a tracked file.
  - Bash: the arguments of a reader word (the 14 names) at a command position in the System-1 parser's shell code.
    - Arguments are read from the original text at the same offsets, with quotes removed.
    - Redirection operators and their targets are skipped.
    - A `cd` at a command position moves the directory that later relative paths resolve against.
- **Once per window:**
  - The keys are `file:<rel>` (Read, Write, Bash) and `sym:<rel>:<symbol>` (Edit).
  - They live in `<state>/filepacks-seen/<window>.json`, under System-1's `WindowLock` (`scripts/filepacks.py:532`).
  - The reset keeps System-1's semantics on that directory.
- **Budgets:** 1,200 bytes per file, 2 files per call, 64 files per window.
- **Off switch:** `filepacks-off`. A dangling link counts, and the reset still runs.
- **Fail quiet:** exit 0 with empty stdout, and one record in `filepacks.jsonl`.
- **Boundary:** only files tracked at the last build (`TRACKED.txt`). A path outside the root, a `..` component, an untracked file, or a pack reached through a link gives nothing.
- **No side effects without a reason:** a call that names no tracked file, or comes before the first build, logs nothing and creates nothing.
- **Imported from System-1, never copied:** `shell_code`, `command_positions`, `window_id`, `WindowLock`, `open_regular`, `read_regular`, `read_stdin`, `load_seen`, `write_json_atomic`, `MARKER_MAX_AGE_S` and `LOG_MAX_BYTES`.
- **Bytecode:** the System-1 module's cache goes to `<state>/pycache` (`sys.pycache_prefix`, `scripts/filepacks.py:115`), never under `.claude/` (check `no-pyc-in-claude`).
- **Live example on this tree,** through the real wrapper, one Bash line: `cd … && sed -n 1,40p scripts/pc_lane.sh | head -3; echo "cat scripts/stack.py"; git add scripts/stack.py`. It injected `scripts/pc_lane.sh` only. The repeat logged `{"key": "file:scripts/pc_lane.sh", "why": "duplicate"}`.

### Item 5: the post-commit refresh, as a patch (proven on a clone)

**The patch.** `tasks/briefs/jev-trim/K2-post-commit.patch` is a `git diff` against the hook at the premise's sha256 (blob 09b3b0b, mode 100755).
- It adds one section after the code-map refresh.
- The section writes one log line per commit, then starts `( flock 7; cd "$REPO_ROOT" && nice -n 19 ionice -c 3 python3 scripts/filepacks.py build ) 7>"$T/filepacks-build.lock" >>"$T/filepacks-build.log" 2>&1 </dev/null &`.
- It contains no `jev` token (the never-a-gate screen refuses that token in a gate file).

**The proof.** In a `git clone --shared --no-tags` of this repo at 02a9276, with only the patched hook as `core.hooksPath` and `AF_POST_COMMIT_TMP` pointed at scratch:
```
23c605f1ec16c1d6                       (the clone's hook before)
apply --check: ok
apply: ok
fce110fe82d8b183 / fce110fe82d8b183    (the clone's patched hook = my throwaway copy)
no_laya_in_gates: 41 files scanned, clean
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---
commit rc=0 at 05:15:38        (a docs-only commit)
2026-09-29T05:15:38Z cd0259d filepacks build launched
filepacks build: cd0259d 1681 packs (1681 written, 0 removed, 0 failed) of 9945 tracked files in 2673 ms
2026-09-29T05:15:38Z cd0259d re-index none: all 1 changed paths are Markdown or under wiki/, todo/, transcripts/, tasks/
2026-09-29T05:15:38Z cd0259d codemap refresh none: no changed path under scripts/, src/, proofs/, spikes/, harness-ports/ (outside the docs plane) or tests/*.py
2026-09-29T05:15:38Z cd0259d slopo sync none: slopo reads none of the changed paths
```

**Two more properties, in the same clone:**
- **A burst of two commits, 155 ms apart:** both commits returned at once, and the two builds ran one after the other. Each build resolved HEAD (1bccf7b) when it started; the first wrote 9 packs and the second 0.
- **A builder that dies:** the commit still returned `commit with a broken builder rc=0`. The log's last two lines are `… 484043e filepacks build launched` and `a broken builder`.

### Item 6: the dry run (`filepacks.py replay --transcript PATH --bytes N`)

- It reads only compaction boundaries and `tool_use` inputs, and leaves sidechain records out.
- It keeps the seen keys in memory, never in the live markers.
- It prints only counts, bytes and milliseconds.

At the premise's cap, on the final packs. Each entry reads `window:calls/injections/bytes`:
```
0:177/30/23615 1:260/48/42313 2:163/32/28150 3:27/12/10181 4:38/8/7761 5:27/7/6903 6:28/6/5764
7:31/5/5308 8:23/7/7034 9:41/10/8433 10:30/6/6853 11:15/3/3287 12:56/8/6724 13:27/7/7432
14:53/17/10950 15:44/10/8029 16:49/10/5375 17:53/16/9541 18:21/17/11586 19:37/15/9128 20:50/5/5137
21:168/22/20154 22:203/25/21307 23:143/21/20765 24:216/36/31081 25:174/23/18604 26:188/37/36693 27:292/48/43093
28:142/50/44063 29:153/46/37171 30:87/49/39338 31:149/43/37533 32:205/35/27001 33:122/29/24531 34:193/40/35430
35:236/29/21964 36:205/36/31928 37:177/45/34750 38:166/37/31533 39:129/35/24751 40:156/24/23685 41:132/38/33906
42:140/44/34957 43:175/63/48851 44:135/59/49291 45:139/27/21709 46:110/19/12934 47:125/16/11396 48:113/7/6979
49:75/4/3704 50:99/24/22483 51:90/29/24165 52:115/24/21284 53:69/9/9418 54:103/9/6334 55:127/12/7476
56:88/10/10619 57:86/15/14193 58:97/14/13340 59:103/23/19335 60:79/12/10467 61:105/8/7192 62:97/18/14346
63:109/21/20408 64:99/14/12122 65:123/19/15852 66:73/23/16919 67:180/33/31571 68:132/25/24303 69:104/35/31554
70:138/33/27529 71:156/45/41322 72:150/34/31719 73:122/40/35873 74:138/29/25601 75:131/27/24820 76:118/22/19459
77:133/28/25281 78:116/34/31087 79:154/36/32895 80:113/27/26177 81:131/32/29820 82:130/42/40282 83:119/27/28390
84:120/42/37904 85:117/41/37106 86:148/39/35674 87:118/27/27559 88:135/28/24771 89:151/25/23306 90:143/35/32029
91:125/34/28681 92:142/32/29251 93:135/45/39212 94:136/31/25969 95:138/34/31064 96:126/36/28216 97:120/27/23648
98:111/19/14957 99:138/38/28820 100:138/48/40049 101:148/33/29085 102:143/34/31928 103:121/26/20898 104:129/29/21165
105:143/28/25695 106:153/30/27422 107:144/35/30859 108:141/19/17879 109:153/22/21205 110:138/27/22623 111:115/27/23984
112:105/31/26621 113:122/29/27173 114:145/39/38142 115:133/32/30099 116:134/21/19678 117:117/30/29251 118:140/33/33750
119:126/38/35130 120:264/64/56593 121:229/62/53053 122:279/55/48079 123:279/47/40466 124:257/45/42931 125:313/54/48213
126:179/43/41712 127:245/63/58499 128:244/59/56434 129:307/65/64070 130:336/60/58825 131:329/66/65584 132:292/59/59546
133:265/57/56102 134:318/60/55901 135:279/33/32907 136:255/52/50091 137:227/51/51626 138:254/50/48200 139:271/51/50871
140:38/14/14748
injections per window: median 30 p90 52 max 66 (windows 141)
bytes per window: median 27001 p90 48851 max 65584 (windows 141)
```
Windows with more than 64 injections carry extra Edit symbol entries; the 64 cap counts files.

### Item 7: tests

`tests/test_filepacks.py` has 25 checks.
- Each check runs through the real wrapper, using the exact registration command strings.
- Each runs on a fresh throwaway git repo with a fixed commit clock.
- State lives only in temp directories.
- The oracles are the fixture's own construction, Python's `ast`, and git.

| check | named mutants (all killed for the named reason) |
|---|---|
| normal: edit-once-per-symbol | edit-key-per-file, no-seen |
| normal: read-range | range-ignored |
| normal: bash-readers (`sed -n 1,40p`, all 14 readers, a `cd`) | no-sed, no-cd |
| normal: reset (startup, compact, resume, clear; a subagent window) | reset-noop |
| normal: doc-pack-lines (a tracked document gets exactly its pack lines) | doc-without-pack-lines |
| builder: build-lines (newest 3, whole-path boundary, ids, headline, snippet) | suffix-match, extension-strip, oldest-lines-first, keep-all, no-registry-id, headline-uncapped, snippet-at-line-start |
| builder: build-briefs-commits | briefs-oldest-first, commits-oldest-first |
| builder: build-sha-threaded (AF-AP-175) | reads-at-head |
| builder: build-removes | keeps-stale-packs |
| builder: build-meta (BUILD.json, TRACKED.txt, no temp file, idempotent) | temp-left, rewrites-every-pack |
| failure: budget-cut (every budget: whole lines, bytes not characters) | cut-mid-line, chars-not-bytes |
| failure: older-p2-stale-code (an older P2 pack is still read; STALE kept or nothing, incl. a symbol named `STALE_beta`) | stale-passes, stale-word-only |
| failure: corrupt (a P2 pack and a code pack; the other file still goes) | corrupt-code-pack-ignored, corrupt-as-no-pack |
| failure: missing-state (nothing is created) | state-created |
| failure: lock-held | no-lock |
| failure: empty-fields (no file_path, empty command, non-object input, empty stdin, …) | no-dict-check |
| security: untracked (packs planted in both stores) | untracked-allowed |
| security: outside-root (`/etc/passwd`, `../x`, a `..` that resolves inside, `<root>Xscripts/...`) | dotdot-allowed, root-prefix-without-slash |
| security: links (a linked pack, a linked code pack, a linked parent directory) | linked-parent-followed |
| security: data-words (`echo "cat x"`, a heredoc body, `git add`, a comment, `python3 x`, a commit message, `<<<`, a redirect target) | data-words-read |
| call-and-window-max | call-max-3, window-max-off |
| kill-switch | off-switch-file-only |
| no-input-in-state (canaries) | input-logged |
| no-pyc-in-claude | pyc-beside-hook |
| replay (a sidechain record left out, a cut line not parsed, counts only) | sidechain-counted |

**Plain tests:**
- every mutant's anchor is unique, and every mutant compiles;
- the installer spelling reaches the model form;
- a drift guard: the planted code pack has the same fields as one written by the real `codemap.build_one`;
- a guard on entry speed.

**`tests/test_codemap.py`:** `check_file_entry` runs on packs built by the real instruments, and its oracle is the file's AST. Its mutants are file-entry-nested, file-entry-enclosed-only and file-entry-never-stale.

**Latency through the real wrapper** (`python3 scripts/hook_context.py PreToolUse -- python3 scripts/filepacks.py hook`), over 300 recorded payloads spread across the transcript, on a temp copy of the packs:
```
wrapper ms: p50 100.8 p95 125.7 max 160.5 over 300 calls (135 injected)
```
For comparison (inferred: a median of 13 samples each, same box): the System-1 hook through its wrapper takes 90.4 ms, and `python3 -c pass` takes 17.0 ms.

### Item 8: gates

**The gate set.** `python3 scripts/stack.py gate paths=<my 5 paths> mode=plan` listed `tests/test_codemap.py` and `tests/test_filepacks.py` (gate_files).
- Its graph step failed only on the new patch path: `ripwire: … 'tasks/briefs/jev-trim/K2-post-commit.patch' matches no indexed file`.
- The gate set is those two files plus `tests/test_system1_context.py`.
- `bash scripts/pc_suite.sh set-id -- tests/test_codemap.py tests/test_filepacks.py tests/test_system1_context.py` gives `3 files set=804c19143d13`.

**How it ran.** In a clean detached worktree at 7db59b9, holding exactly my 5 files (sha256 checked). I ran `bash scripts/test_summary.sh <the 3 files> --basetemp=<outside any work tree>`, one foreground call per run:
```
run 1: pytest-exit: 0 / pytest-summary: 255 passed in 350.09s (0:05:50)   (set 804c19143d13)
run 2: pytest-exit: 0 / pytest-summary: 255 passed in 348.63s (0:05:48)   (set 804c19143d13)
```

**An extra landing check, beyond the brief.** I applied the patch in the same worktree (hook sha fce110fe82d8b183). Then I ran every test that names `scripts/hooks/post-commit`, plus the never-a-gate screen's test: `5 files set=61956722b30e` (tests/test_codemap.py tests/test_post_commit_reindex.py tests/test_shell_syntax.py tests/test_slopo.py tests/test_no_laya_in_gates.py).
```
pytest-exit: 0 / pytest-summary: 223 passed, 7 skipped in 403.92s (0:06:43)
```
The 7 skips are the declared model-dependent slopo tests ("no slopo venv or no model under .slopo-runtime/model"): a worktree holds no model. They are the same 7 skips the L2a landing recorded.

## Mutation summary (final bytes, in the gate worktree)

```
64 passed, 50 deselected in 152.79s (0:02:32)
filepacks: killed 40 of 40 mutant tests
codemap: killed 15 of 15 mutant tests
```
- **How a kill counts:** each one is `pytest.raises(AssertionError, match=<the named failure>)`. A mutant killed for any other reason makes its test fail; two of mine did that during the build, and I reordered their assertions.
- **No INVALID mutant:** every anchor occurs once and every mutant compiles (`test_every_check_has_a_mutant_and_every_mutant_compiles`).
- **The codemap count** is the 12 existing mutants plus my 3.

## Registration (you add it at landing, after the LS-B9 verifier is done with the installer)

**Repo `.claude/settings.json`:** append one group to `hooks.PreToolUse` and one to `hooks.SessionStart`. Put each last in its list, so the existing positional asserts keep their indexes.
```json
{"matcher": "Read|Edit|Write|Bash", "hooks": [{"type": "command", "command": "[ -f $CLAUDE_PROJECT_DIR/scripts/filepacks.py ] && [ -f $CLAUDE_PROJECT_DIR/scripts/hook_context.py ] || exit 0; python3 $CLAUDE_PROJECT_DIR/scripts/hook_context.py PreToolUse -- python3 $CLAUDE_PROJECT_DIR/scripts/filepacks.py hook"}]}
```
```json
{"hooks": [{"type": "command", "command": "[ -f $CLAUDE_PROJECT_DIR/scripts/filepacks.py ] || exit 0; python3 $CLAUDE_PROJECT_DIR/scripts/filepacks.py hook --reset"}]}
```
- These two strings are `REG_PRE` and `REG_RESET` in `tests/test_filepacks.py`, and every check runs them.
- **The reset has no `timeout`.** `tests/test_session_hooks.py` requires that no hook except task_sync carries one, and the reset's stdin read is already bounded at 2 s.

**`scripts/install_session_hooks.py`**, in `our_hooks(root)`. `test_the_installer_spelling_reaches_the_model_form` runs exactly these commands:
```python
    filepacks = {"matcher": "Read|Edit|Write|Bash", "hooks": [{"type": "command", "command": guarded(
        "scripts/filepacks.py", f"{wrap} PreToolUse -- python3 {r}/scripts/filepacks.py hook", True)}]}
    filepacks_reset = {"hooks": [{"type": "command", "command": guarded(
        "scripts/filepacks.py", f"python3 {r}/scripts/filepacks.py hook --reset")}]}
    # SessionStart: [..., task_sync("session-start"), catalog, filepacks_reset]
    # PreToolUse:   [<Grep|Bash group>, <Write|Edit|Bash group>, filepacks]
```
In `merged()`, add `filepacks_marker = f"{shlex.quote(str(root))}/scripts/filepacks.py"` and OR it into the `ours` lambda beside `sync_marker` and `catalog_marker`. Then an older spelling is recognized and replaced instead of duplicated.

**Edits this forces in `tests/test_session_hooks.py`** (not my file; I only read it):
- per-event counts: PreToolUse 2→3, SessionStart 3→4;
- the assert that every command holds MARKER, SYNC or CATALOG (add the filepacks path);
- the PreToolUse matcher list (add `"Read|Edit|Write|Bash"`);
- `len(cmds) == 10` → 12;
- the wrapped-event list (one more `PreToolUse`);
- `== 11` → 13;
- `len(others) == 7` → 9;
- `"installed 8"`: check how the installer counts before changing it.

Then regenerate the vendored manifest.

## DISCREPANCIES

1. **Design vs brief, sources:** §10.3 P2 lists "its open issues"; the brief's exact list does not. I did not build it.
2. **Design vs brief, triggers:** §10.3 P1 names only the first Read, Edit or Write. The brief adds Bash readers (83.4% of touched files, measured). I followed the brief.
3. **BUILD.json and TRACKED.txt:**
   - `BUILD.json` holds more than the brief lists: `tracked`, `written`, `removed`, `failed` and `missing`.
   - A new `TRACKED.txt` sits beside it. It is a plain path list that the hook checks by substring, and it is the hook's tracked-file boundary.
   - I kept it separate because a `BUILD.json` holding all 9,944 paths cost 1.88 ms per read.
4. **A second `git log`:** one extra `git log --name-only <sha> -- tasks/briefs/` over the whole history dates each brief (0.57 s measured). The brief's "ONE git log call" covers the commit subjects and does not say how to find a brief's last commit.
5. **"Newest 3 per source":** I treat each of the nine skill files as its own source, since line numbers only compare within one file. The probe grouped them as one source.
6. **"At most 2 files per call (the first named)":** I read it as the first two named files that inject. A file already seen, or with no pack, takes no slot.
7. **Read with offset and limit:** when `lookup` finds no single enclosing symbol (status `module`), the file-level reader over the range lists the symbols in it. This delivers the brief's "shows the symbols in range", which `lookup` alone cannot give.
8. **Edits:**
   - An Edit that cannot be placed (not in the file as it is now, or ambiguous) gets the file's entry, keyed `file:<rel>`.
   - An Edit also marks `file:<rel>`, so the pack's lines go once per file per window. A later Read of the same file injects nothing.
9. **A root file named `BUILD`:** a tracked root-level file with that name would get no pack, since its pack path would be `BUILD.json`. None exists (measured).
10. **Overlap with edit-snapshot:** the hook's commit lines duplicate the edit-snapshot PostToolUse hook, which already injects a file's last commit subjects on every Read, Edit and Write. I put commits last in the rotation; you may want to drop them for those three tools.
11. **The code part often uses most of the 1,200 bytes.**
    - A symbol entry runs 600 to 800 bytes, leaving room for the pack's head line and about one mention line.
    - Measured on `scripts/stack.py` `cmd_run`: 7 code lines and the pack's head line fit; 7 lines were cut.
12. **`scripts/codemap.py` was written twice**, not "in one step" as the brief says.
    - Each write was one atomic rename of a scratch-proven file, so a partial file never existed on disk.
    - The second write was the fix for item 13.
13. **Defect found and fixed in my work (registry candidate): duplicated mutant anchors.**
    - My first `file_entry` repeated two statements verbatim that are existing mutant anchors in `tests/test_codemap.py` (`never-stale`, `miss-as-module`).
    - Those two negative-control tests would then have failed with "the mutation anchor must occur exactly once". I counted every anchor (both were at 2) and rewrote the two statements; all 12 existing anchors now occur once.
    - **The class:** an additive edit to a file whose tests mutate it by exact text can duplicate an anchor.
    - **Why it matters:** uniqueness is only checked when the instruments are installed (`needs_tools`), so on CI such a break would go unseen.
    - A static anchor-uniqueness test would guard it. I did not add one: it falls outside "only for the new reader".
14. **Defect found and fixed in my work (registry candidate): a word-based stale guard.**
    - My first stale guard looked for the bare word `STALE`. A symbol or path containing that word in the head line would have let a stale code part pass as fresh.
    - It now matches the code map's mark text.
    - The test case (`STALE_beta`) and a mutant (`stale-word-only`) cover it.
15. **The ripwire union** for the .py paths is 51 test files (broad links through the code map). It is not the brief's gate rule, and I did not run it.

## Self-attack: the three most likely ways this is wrong

1. **The path matcher assigns mentions to the wrong files.**
   - **Misses:** mentions by bare file name ("codemap.py") and absolute paths into other trees (worktrees, `/tmp/...`) never count.
   - **Over-matches:** root-level names in prose (`CLAUDE.md`) count wherever they appear as a whole token. That is correct under the rule, but noisy.
   - **Ruled out:** faults in the rule itself, by the whole-path-boundary fixture lines and the two boundary mutants.
   - **Not ruled out:** whether bare-name mentions carry context you want. They are left out by design; the design choice is stated here.
2. **The Bash reading assigns files to the wrong command.**
   - A grep pattern that is itself a tracked path counts as a touch.
   - A `cd` inside a subshell or `$(…)` carries over to later commands. That causes a miss, or points at a file in the wrong tree when the cwd was outside the repo.
   - **Ruled out for quoted and heredoc text:** the System-1 parser is used (the data-words check and its mutant).
   - **Plausibility check:** the replay gives a median of 30 injections per window, against the probe's median of 32 touched files per window.
3. **The injection misleads.**
   - **Stale code:** guarded; the STALE mark is kept or nothing is shown, and both mark forms are tested.
   - **An older P2 pack:** it is shown with its build commit (`@sha7`) but not flagged as behind HEAD, since the brief says to still read it. That `@sha7` can be a local id that push_clean later rewrites; the next post-commit build refreshes it.
   - **Planted code packs in the tests could drift from the real format.** Covered by the drift guard (field sets compared against the real `build_one`) and by `check_file_entry` on packs from the real instruments.

Also open: the AF-AP-70 race (NOT done item 4), and the cost of about 100 ms per call once registered (item 7).