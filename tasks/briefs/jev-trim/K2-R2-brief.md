# K2 round 2: close the stale-index hole, fix the parser's wrong files, deliver the registration as a patch (task #353, D-106)

Written 2026-09-29 from 07:4xZ (clock read at 07:41:41Z) by the coordinator, for the original K2 builder, resumed. ONE
focused repair (D-031). VERIFY-K2 (`tasks/briefs/jev-trim/VERIFY-K2-report.md`, READ in full) recommends
MERGE-READY-WITH-FOLLOWUPS on one condition. Its F1 is a boundary hole: when `TRACKED.txt` is older than the commit that
untracked a file, and the code map rebuilt that file's pack from the working copy, the untracked file's text reaches the
model. The post-commit patch narrows the window to a failed or stalled build; this round closes it outright, fixes the
parser defects the verifier measured, and hands the coordinator a registration patch proven in a worktree. The hook is
still NOT registered, and you never register it.

## Boundary

- MODIFY: `scripts/filepacks.py`, `tests/test_filepacks.py`, `scripts/codemap.py` (its READERS only: `_load_pack`, `lookup`,
  `file_entry`, `edit_context`, `language`; the builder side stays byte-for-byte as it is), `tests/test_codemap.py`,
  `tasks/briefs/jev-trim/K2-post-commit.patch` (only if it no longer applies).
- CREATE: `tasks/briefs/jev-trim/K2-registration.patch` (item 8).
- READ: the VERIFY-K2 report; the verifier's probes and state under
  `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2/` (reference only: port what you need
  into the repo's tests, since that directory does not survive a container reset); `.claude/hooks/system1-context.py`;
  `scripts/hook_context.py`; `scripts/install_session_hooks.py`; `tests/test_session_hooks.py`;
  `tests/test_search_intercept.py`; `.claude/settings.json`.
- NOT yours in the shared tree: `.claude/`, `scripts/install_session_hooks.py`, `tests/test_session_hooks.py`,
  `scripts/hooks/post-commit`, `/home/user/.claude/settings.json`, the live `.jev/`. The coordinator's commits and tool
  calls run the hooks from the shared tree while you work (orchestration 0p).

## Items (each with a test and a named mutant the test kills; a real run pasted where it applies)

1. **Premise.** Re-run the PREMISE block below. On a difference, stop and report CONTRACT-INVALID.
2. **F1, closed whatever the build did.** The build records each tracked file's blob id (from its one `ls-tree`) next to
   `TRACKED.txt`. The hook shows a code part only when the code-map pack's `blob` equals the file's blob at the build's
   commit; otherwise the P2 lines only. Port the verifier's `probe_p6.py` scenario (a file untracked after the last build,
   its code pack rebuilt from the working copy with a canary) as a test through the real wrapper: 0 canary bytes on Edit,
   Read and `cat`, with the patch absent and with it applied. Keep `TRACKED.txt`'s exact-line match and add the verifier's
   `tracked-suffix-match` check.
3. **F2, no stall on a swapped file.** codemap's five readers open with System-1's `open_regular` (O_NONBLOCK, then
   `fstat`, regular files only), so a FIFO swapped in between check and open is refused, not waited on. Port the
   verifier's `fifo-working-file-read` check (its stall bound: "the hook stalled past 15 s"). The code-map builder, the
   refresh and every existing codemap test stay as they are.
4. **F3, a linear parse.** `_args` collects each simple command's words in one pass (or caps the words it scans per
   position). Paste the timings for 250, 1,000 and 3,000 `time cat` pairs through the wrapper (the verifier's: 7,958 ms at
   1,000, the 55 s cap at 3,000) and add a check with a bound.
5. **F4 and F5, the right file.** A `cd` inside `( … )` or `$( … )` stays inside it; `pushd` and `popd` are followed; the
   pattern argument of `grep`, `egrep` and `rg` is a pattern, not a file (unless `-f`); `bash -c '…'`, `sh -c "…"` and
   `eval` read their nested command (strip the unmatched closing quote System-1's code text keeps before `shlex.split`); a
   nested command under `ssh` or `scripts/pc.sh` runs on another host, so it injects nothing. Port the verifier's seven
   wrong-file shapes and the `bash -c` misses as checks.
6. **F14, the verifier's 17 checks.** Add each check its mutation run showed missing (its list under F14), each with its
   mutant. Keep every existing check.
7. **F12, the claims match the code.** Where a docstring or the report says a call "creates nothing" or a linked pack
   "gives nothing", make it say what the verifier measured (F6, F12).
8. **The registration, as a patch.** `tasks/briefs/jev-trim/K2-registration.patch` (`git diff` format against the files
   at the PIN) adds the two entries to `.claude/settings.json` (each last in its list), the two groups to
   `scripts/install_session_hooks.py` (`our_hooks` and the `merged` marker), and the test edits in
   `tests/test_session_hooks.py`: the builder's seven plus the verifier's eighth (`_fake_repo` writes a
   `scripts/filepacks.py` stub). Prove it in a clean worktree at the PIN with your round-2 files and the post-commit
   patch applied: `tests/test_session_hooks.py` and `tests/test_search_intercept.py` pass (the verifier's run: `2 files
   set=2415789b9582`, 136 passed), and paste `python3 scripts/vendored_manifest.py --check` (it is expected to fail on
   the `.claude/` row until the coordinator regenerates the manifest at landing; say so if it does).
9. **Gates**, each twice: `tests/test_codemap.py`, `tests/test_filepacks.py`, `tests/test_system1_context.py` in a
   clean detached worktree, `--basetemp` as a pytest ARGUMENT outside any work tree, counts pasted from
   `scripts/test_summary.sh` with the set id from `bash scripts/pc_suite.sh set-id -- <files>`; the mutation summary
   on your final bytes, the control first (AF-AP-223).

## Report

Return the whole report as your final message: the premise re-run; files with line counts and sha256; per item its
pasted evidence; the gates; the mutants; the registration patch's proof; NOT done, first-class; a DISCREPANCIES list;
your self-attack.

Standing rules: no git write in the shared tree (the coordinator commits); no outward action, no PC bridge, no subagent;
never read a secret file (`.pc-bridge.env`, any `*.env`, any key file), and build test secrets as fake strings at run
time; never run `scripts/install_session_hooks.py`, never touch `/home/user/.claude/settings.json`, anything under
`.claude/`, or the live `.jev/`; when you read transcripts, read only compaction boundaries and `tool_use` inputs, never
a thinking block, and print only counts, bytes and paths; a long gate in ONE foreground call; stamps from `date -u`;
cite commits by origin id or subject; stop any process you start before you report.

## PREMISE — MEASURED at authoring (2026-09-29, main tree; PIN origin d812c9b, the K2 landing)

Printed by `bash scripts/premise_block.sh` from the main tree before this brief's commit. The `[rc=1]` is grep's exit
code for three zero counts: the hook is registered nowhere. The verifier's scratch directory holds its probes; it does
not survive a container reset. Expected to differ: nothing.

```
$ git merge-base --is-ancestor d812c9b HEAD && echo d812c9b-is-an-ancestor-of-HEAD
d812c9b-is-an-ancestor-of-HEAD
$ git log -1 --format=%s -- scripts/filepacks.py | cut -c1-60
K2 landed (task #353; GATED-PENDING-VERIFY): file context pa
$ sha256sum scripts/filepacks.py tests/test_filepacks.py scripts/codemap.py tests/test_codemap.py tasks/briefs/jev-trim/K2-post-commit.patch tasks/briefs/jev-trim/VERIFY-K2-report.md | cut -c1-16,65-
46ee3aea2f1e428b  scripts/filepacks.py
20688549adc7c296  tests/test_filepacks.py
ea28c5add97fac24  scripts/codemap.py
a1b9fa4652c47181  tests/test_codemap.py
71ba4c2c0cec81ab  tasks/briefs/jev-trim/K2-post-commit.patch
9387fceacb47d9e0  tasks/briefs/jev-trim/VERIFY-K2-report.md
$ grep -n '^def _args\|^def _code_part\|^def entry\|^def build(\|    def tracked' scripts/filepacks.py
160:def _args(code, cmd, start):
256:    def tracked(self, rel):
331:def _code_part(rel, ti, root):
377:def entry(rel, tool_input, budget=PACK_BUDGET, *, packs=None, p2=True):
686:def build(root=ROOT, state=None, sha=None):
$ grep -n '^def _load_pack\|^def lookup\|^def file_entry\|^def edit_context\|^def language' scripts/codemap.py
81:def language(root: Path, rel: str) -> str | None:
865:def _load_pack(root, rel):
878:def lookup(path, line, end_line=None, root=None):
918:def edit_context(file_path, old_string, root=None, replace_all=False):
951:def file_entry(path, line=None, end_line=None, root=None):
$ grep -c 'filepacks' .claude/settings.json scripts/install_session_hooks.py /home/user/.claude/settings.json
.claude/settings.json:0
scripts/install_session_hooks.py:0
/home/user/.claude/settings.json:0
[rc=1]
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2/probe_p6.py /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2/mutdrv.py
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2/mutdrv.py
/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vk2/probe_p6.py
$ bash scripts/pc_suite.sh set-id -- tests/test_codemap.py tests/test_filepacks.py tests/test_system1_context.py | tail -1
3 files set=804c19143d13
```
