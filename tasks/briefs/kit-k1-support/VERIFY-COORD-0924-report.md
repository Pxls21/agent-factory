# VERIFY-COORD-0924 report

Lane: VERIFY-COORD-0924, sandbox adversarial-verifier, served model claude-opus-5-5 (the session's own model id; no refusal stop seen by this lane).
PIN: 8b2be817c2eb (local HEAD; e8692c2 + the brief only).
Started: 2026-09-24 11:42:50 UTC (`date -u`).

## 0. PREMISE re-measure (all MATCH)

```
$ for f in ...; do git rev-parse --short=12 HEAD:$f; done     (at 8b2be81)
9d49a8de0577 scripts/hook_context.py
9fdb4b6c1a72 scripts/install_session_hooks.py
b2a8bf7744d0 tests/test_session_hooks.py
ad968bc98b60 .claude/settings.json
071bb0cf6a29 tests/test_s0_01_frame_tee.py
57e41b13faa0 .claude/hooks/edit-snapshot.py
1ec171f90691 tests/test_edit_snapshot_ap_screen.py
3eb0b06249fe scripts/no_laya_in_gates.py
4c8688e3483a tests/test_no_laya_in_gates.py
$ git diff --stat HEAD -- <the nine files + setup.sh + resume-heal.sh>     -> empty (working tree == HEAD)
$ git diff --stat e8692c2 8b2be81   -> only tasks/briefs/kit-k1-support/VERIFY-COORD-0924-brief.md (84 insertions)
$ python3 scripts/install_session_hooks.py --check
session hooks: present in /home/user/.claude/settings.json
rc=0
$ pytest tests/test_session_hooks.py tests/test_edit_snapshot_ap_screen.py tests/test_no_laya_in_gates.py -q --basetemp /tmp/vc2/bt
309 passed in 12.27s
$ pytest tests/test_s0_01_frame_tee.py -q -k 'ProcStateAfterKill or kill' --basetemp /tmp/vc2b/bt
13 passed, 108 deselected in 8.54s
```

No landing is CONTRACT-INVALID on its premise.

## 1. L1: the five project hooks (live-harness evidence first)

### 1.1 Live reachability through the REAL harness (this lane's own tool calls, Claude Code 2.1.280)

This lane runs inside a `/home/user`-rooted session: its transcript is
`/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/subagents/agent-aa74deda0649c01d1.jsonl`
(`-home-user`, not `-home-user-agent-factory`), so only `/home/user/.claude/settings.json` can have fired.

- A Read of `scripts/no_laya_in_gates.py` drew `PostToolUse:Read hook additional context: READ CONTEXT · no_laya_in_gates.py — last 3 changes …`
  in this lane's context. Transcript record: `hook_success`, command
  `cd /home/user/agent-factory && python3 /home/user/agent-factory/scripts/hook_context.py PostToolUse -- python3 …/edit-snapshot.py`,
  exitCode 0, durationMs 108, then a `hook_additional_context` record.
- A Grep for `SIMPLE_TOKENS` under `scripts/` drew `PreToolUse:Grep hook additional context: GRAFT-FIRST …` (installed command, 56 ms).
- A Grep for `_proc_state_after_kill` under `tests/` drew nothing: `graft-first-nag.py` does not count `tests` as a code prefix
  (its `code_prefixes`), so this is the nag's own rule, not a wiring gap.
- One context block per call: no double fire.

Parent-session transcript census (read-only; hook attachment records after the 11:06Z install):
UserPromptSubmit x3 (installed `wiki-context.py` command, exit 0), PostToolUse:Edit x1 (wrapper, additionalContext delivered),
SessionStart:compact x1 at 11:24:15Z (installed `session-start.sh`, exit 0, 33,048 ms), Stop: `stop_hook_summary` records at
11:43:19Z and 11:45:21Z carry the retro checklist from `cd /home/user/agent-factory && bash …/turn-retro-gate.sh` (blocking,
once per new non-exempt HEAD: ab93ede, then 6b31bdf), and 11:45:37Z acked the wiki-only ee3c8c1 silently (`hookErrors: []`).
All five installed entries have fired live. VERIFIED.

### 1.2 What the harness does with hook output (read from the running binary, /opt/claude-code/bin/claude, 2.1.280)

- `case"hook_success": if(e.hookEvent!=="SessionStart"&&e.hookEvent!=="UserPromptSubmit"&&e.hookEvent!=="UserPromptExpansion")return[]; if(e.content==="")return[]; return[… "${e.hookName} hook success: ${e.content}"]`
  : plain stdout reaches the model ONLY for SessionStart / UserPromptSubmit. This confirms the landing's premise (PostToolUse /
  PreToolUse plain stdout is invisible) from primary source.
- `async function ene(e,r,n,{threshold:s=fpo,…}){if(e.length<=s)return e; … hook-${r}-${n} …}` with `,fpo=1e4`: every hook
  text over 10,000 chars (plain `hook_success` content AND `additionalContext`, both call sites read) is saved to a file and the
  model gets a `<persisted-output>` block with a 2 KB preview.
- Command hooks: `import{spawn as one}from"child_process"` and `one(Bn,[],{env:Hn,cwd:Sn,shell:Xr,…})` with `Xr = Xe ? Or : !0`
  (true off Windows): the command runs under `/bin/sh -c`, which is dash here (`/bin/sh -> dash`).
- Default command-hook timeout `Qt = e.timeout ? e.timeout*1000 : Ia`; the only numeric `Ia` binding is `var Ia=600000,nge=30000,…`
  in a hooks-adjacent module (INFERRED: minified names can repeat across modules).
- Stop loop guard: `let Mt=a.CLAUDE_CODE_STOP_HOOK_BLOCK_CAP??8; if(Mt>0&&Rt>Mt) …"A hook blocked the turn from ending … consecutive times — overriding and ending turn."`

### 1.3 PIN note

The coordinator pushed while this lane ran: `8b2be81` became `ae9add5` on origin (same tree `fc2b481b9cba`), and HEAD moved to
`f594ea3`. `git diff --stat 8b2be81 HEAD` over all eleven landing files is EMPTY, so every result below holds at both. The working
tree now also carries uncommitted edits outside the three landings (`.claude/hooks/wiki-context.py`, `tests/test_wiki_context_hook.py`,
`sandbox-kit/VENDORED-*`, `src/agent_factory/decisions/volatile.py`); none is graded here.

### 1.4 Scratch reproductions (copies of the PIN's scripts under /tmp/vc2; no install ever targeted /home/user/.claude)

Drivers: `/tmp/vc2/l1_install_driver.py`, `/tmp/vc2/l1_absent_driver.py`, `/tmp/vc2/l1_wrap_driver.py`, `/tmp/vc2/l1_mutants.py`.

Installer (`install_session_hooks.py` copied to scratch repo roots):
```
repo '/tmp/vc2/l1/plain/agent-factory'   install 1 -> 5 entries; install 2 'unchanged'; --check 0; --remove -> {}
repo '/tmp/vc2/l1/sp ace/agent-factory'  install 2 -> 'installed 5' again, entries {PostToolUse: 2, PreToolUse: 2, SessionStart: 2, Stop: 2, UserPromptSubmit: 2}
                                         --check (1, 'MISSING or stale'); --remove (0, 'unchanged') -> our entries stay
repo "/tmp/vc2/l1/q'uote/agent-factory"  same as the space case
mixed entry {"matcher":"Bash","hooks":[echo owner-logger, bash <marker>owner-custom.sh]} + a Notification entry naming the marker:
                                         install drops both whole (owner-logger lost); install+remove -> {} (not the original)
owner hand-edit of our Stop entry (timeout + an extra hook): re-install reverts both; --remove deletes the extra hook
{"hooks": {}} / {"hooks": {"Notification": []}} / {"hooks": null}  -> install+remove -> {}   (not equal to the original)
absent file -> install -> remove -> a file holding {}
{"hooks": "abc"} -> traceback rc 1, untouched;  {"hooks": {"Stop": "abc"}} -> rc 0, Stop becomes ["a","b","c",<ours>]
mode 600 uid 1000 -> after install: mode 644 uid 0 gid 0
symlinked target -> replaced by a regular file; the symlink's real file never gets the hooks
non-ASCII (U+2014) statusLine -> after install+remove: JSON-equal, bytes differ (indent 2, — escape)
foreign entry after ours -> --check 1 until a re-install moves ours to the end
24 concurrent installs -> valid JSON, foreign key kept, 1 entry per event, 0 stray .settings.*.tmp, 0 stderr lines
directory target -> REFUSED rc 1; 200,000-deep JSON -> RecursionError traceback rc 1, untouched
HOME=/tmp/vc2/l1/home, repo at $HOME/agent-factory, no --target, --check (writes nothing):
  'session hooks: MISSING or stale in /tmp/vc2/l1/home/.claude/settings.json'  = the USER-scope file
```

Installed command strings run exactly as the harness runs them (`/bin/sh -c`, dash), stdin = a plausible event payload:
```
repo root absent:   SessionStart / UserPromptSubmit / PostToolUse / PreToolUse / Stop  ->  rc 2 under /bin/sh ("cd: can't cd"),
                    rc 1 under /bin/bash
scripts/hook_context.py absent (origin/main LACKS it; a plain `git checkout main` of the shared tree is enough):
                    PostToolUse rc 2, PreToolUse rc 2 ("python3: can't open file ... [Errno 2]")
wrapped hook script absent (edit-snapshot.py / graft-first-nag.py): the wrapper passes the child's 2 through -> rc 2 / rc 2
wiki-context.py absent: UserPromptSubmit rc 2;  turn-retro-gate.sh absent: Stop rc 127;  python3 not on PATH: rc 127
```
In Claude Code, 2 is the BLOCKING code: PreToolUse -> the Grep is refused; UserPromptSubmit -> "UserPromptSubmit operation blocked
by hook" (the prompt is dropped); Stop -> the turn cannot end, until the cap of 8 consecutive blocks is hit; PostToolUse -> stderr
fed to the model after every Read/Edit/Write; SessionStart -> stderr to the user only.

`hook_context.py` (the PIN's file, run directly):
```
A1 non-UTF-8 stdout, exit 0          -> additionalContext 'ok �� end' (JSON must be Unicode; fine)
A2 non-UTF-8 stdout+stderr, exit 2   -> rc 2, stdout b'out \xef\xbf\xbd\n', stderr b'err \xef\xbf\xbd\n' (bytes CHANGED)
A3 printf 'a\n\n\n'                  -> additionalContext 'a' (contract: 'a\n\n', only the FINAL newline removed)
A4 whitespace-only output, exit 0    -> nothing printed
A5 25,000,000-char output            -> rc 0 in 0.4 s, all of it in additionalContext (the harness then keeps a 2 KB preview)
A6 stderr text with exit 0           -> stderr dropped, stdout wrapped
A7 hook exits 0 but a background child keeps stdout open -> rc 0 after 55.1 s, NO output,
   stderr "hook_context: sh did not run: ... timed out after 55 seconds" (it did run; its 'real-output' is lost)
A8 PYTHONIOENCODING=ascii, exit 2 with a non-ASCII stdout char -> rc 1 (UnicodeEncodeError traceback): blocking 2 became 1
   (unreachable here: the running claude process sets no LANG/LC_*/PYTHONIOENCODING, so Python runs in UTF-8 mode)
A9 child killed by SIGKILL           -> rc 247
A10 exit 1 with output               -> passed through unchanged
A11 8 MB stdin to a child that never reads -> rc 0 in 0.1 s
A12 CRLF output                      -> 'line\r'
A15 child printing its own hook JSON (a deny) -> wrapped as text; permissionDecision gone
```

Mutation audit of `tests/test_session_hooks.py` (13 tests; each mutant on its own `git archive 8b2be81` copy):
```
BASELINE: 13 passed
KILLED   W1 non-zero exit swallowed / W2 empty output wrapped / W4 OSError not caught / W5 final newline kept / W6 stderr dropped
KILLED   I5 SessionStart wiring dropped / I7 empty event lists kept / I8 marker never matches / I9 --check always passes
SURVIVED W3 hookEventName hardcoded "PostToolUse"   (the harness THROWS on it: `if(h&&e.hookSpecificOutput.hookEventName!==h)throw
         Error("Hook returned incorrect event name ...")`, so the graft nag would vanish with 13 tests green)
SURVIVED W7 timeout 55 -> 0.5 s
SURVIVED I1 installed commands lose their `cd`   (load-bearing: from cwd /home/user the PostToolUse Read command then prints
         NOTHING; with the cd it prints the READ CONTEXT block, measured on the real hook scripts)
SURVIVED I2 SessionStart loses `CLAUDE_PROJECT_DIR=<repo>`   (load-bearing: the harness sets CLAUDE_PROJECT_DIR to the session
         root, and session-start.sh then runs `cd "${CLAUDE_PROJECT_DIR:-.}"`, finds no scripts/setup.sh, no live-state, no orient,
         and exits 0: 'setup done in 0s', measured)
SURVIVED I3 mode left at 0600 / I4 Stop run by sh / I6 non-atomic write
```
`test_installed_commands_run_through_a_shell` runs only the PreToolUse and UserPromptSubmit strings, the two that do not depend on
the working directory, so the load-bearing parts of the installed strings (the `cd`, the SessionStart override) are untested.

Adapters (contract bullet 3), run as `run-all.sh` runs them: `test_codex_hook_adapter.py 7/7 passed`,
`test_hermes_hook_adapter.py 6/6 passed`, `test_hermes_spool.py 9/9 passed` (all rc 0). A plain `pytest` over these files
collects NOTHING (`no tests ran`, rc 5): they are scripts, not pytest modules.

### 1.5 L1 finding inventory

| id | class | finding | evidence | contract / path / material / discriminator / boundary | suggested fix |
|---|---|---|---|---|---|
| F-L1-1 | FOLLOW-UP (top) | Ownership marker `f"{root}/.claude/hooks/"` is the UNQUOTED path; the commands embed `shlex.quote(root)`. For a repo path that needs quoting (space, quote) the installer never recognizes its own entries: every run appends 5 more, `--check` always 1, `--remove` answers `unchanged` and removes nothing (the owner's opt-out is dead). | reproduced (scratch copy at `/tmp/vc2/l1/sp ace/`, `q'uote/`) | contract YES (no-op / --check / --remove); production script YES, deployed path NO (`/home/user/agent-factory` needs no quoting: `shlex.quote` returns it as is); material: none at the deployed path; discriminator YES; in boundary YES | build the marker from the same quoted text the commands use (`f"{shlex.quote(str(root))}/.claude/hooks/"` matches both forms), plus a test whose repo root holds a space |
| F-L1-2 | FOLLOW-UP (top) | A broken registration BLOCKS. The harness runs hooks with `/bin/sh -c` (dash here): with the repo absent every installed command exits 2; with `scripts/hook_context.py` absent (`origin/main` lacks it, so `git checkout main` of the shared tree suffices) PreToolUse and PostToolUse exit 2 (python's can't-open code), and the wrapper passes a missing hook script's 2 through. 2 is the blocking code: every Grep refused, every prompt dropped (wiki-context.py absent), Stop blocked up to 8 times per turn. | reproduced through the installed strings under `/bin/sh -c` on a scratch root; harness semantics read from the 2.1.280 binary | contract PARTIAL (the wrapper's own words: "a broken registration never blocks"); exact live path NO (needs a tree without the scripts); material: none in the current state, severe when triggered; discriminator YES (rc 2 vs 0); in boundary YES | start each installed command with a guard that exits 0 when its script is missing (e.g. `[ -f <script> ] || exit 0; cd <r> && …`), and have `hook_context.py` treat a missing script path as "cannot run" |
| F-L1-3 | FOLLOW-UP | The harness keeps any hook text over 10,000 chars (`fpo=1e4`, both plain stdout and additionalContext) as a file plus a 2 KB preview. The installed SessionStart printed 18,836 chars at the 11:24Z compaction: the model got a 2,216-char `<persisted-output>` preview of setup-log noise; the wiki live-state block (char 3,794 onward), the hook's stated purpose, never reached it. UserPromptSubmit (wiki-context.py) went over the threshold in 2 of 3 live runs (10,714 / 10,657 chars). A sibling shape of AF-AP-172 ("fires, but the model does not see it"). | reproduced from the live transcript records; threshold from the binary | contract: not a frozen L1 criterion; path YES (live); material YES for continuity; discriminator YES (content length); boundary NO (session-start.sh / wiki-context.py are not L1 files) | print the live-state first and send setup's log to a file (keep SessionStart under 10,000 chars); cap wiki-context output; add the persist-threshold shape to the AF-AP-172 row |
| F-L1-4 | FOLLOW-UP | Test gaps: surviving mutants W3, I1, I2 are load-bearing (see 1.4); W7, I3, I4, I6 also survive. | mutation audit | test-only | assert `hookEventName == "PreToolUse"` in the graft-nag test; run the installed PostToolUse string from a non-repo cwd and assert READ CONTEXT; assert the SessionStart string sets CLAUDE_PROJECT_DIR (or run session-start.sh with CLAUDE_CODE_REMOTE unset) |
| F-L1-5 | FOLLOW-UP | The atomic replace resets the file to 0644 and to the caller's uid/gid (600 uid 1000 -> 644 uid 0). A settings file can carry an `env` block with tokens; on a multi-user host this widens it to world-readable and leaves the owner unable to write it. Single-user root sandbox: no exposure today. | reproduced | contract: the brief lists mode/ownership as a suspicion; material: none here | copy the existing file's mode and owner onto the temp file before `os.replace` |
| F-L1-6 | FOLLOW-UP | The default target is `<repo parent>/.claude/settings.json`; for a clone directly under `$HOME` (the PC clone is `$HOME/agent-factory`, `scripts/pc_lane.sh:142`) that is the USER-scope file, so a run there registers the five hooks for every Claude Code session of that user and double-fires in repo-rooted sessions (the case the commit message itself rejected). No PC invoker exists today (`pc-setup.sh` does not call it). | computed with `--check` under a scratch HOME (no write) | not a frozen criterion; latent | refuse the default target when it equals `Path.home()/".claude"/"settings.json"` unless `--target` is given |
| F-L1-7 | INFO | Merge rule edges: an entry that mixes a foreign hook with an ours-marked hook is dropped whole on install and on remove (the foreign `echo owner-logger` is lost); owner hand-edits inside our entries are reverted by every session start (setup.sh re-runs the installer). The contract's rule defines such entries as ours; the collateral foreign hook is the only real loss. None exists in the live file. | reproduced | contract: arguably "keeps every other key and entry" | split mixed entries hook by hook instead of dropping the entry |
| F-L1-8 | INFO | `--remove` is exact at the JSON-value level only for non-empty content: `{"hooks": {}}`, empty event lists and `"hooks": null` come back as `{}`; an absent file comes back as `{}`; bytes are re-serialized (indent 2, `\u` escapes). The coordinator's own test compares JSON values. | reproduced | trivial | none needed, or restore absent/empty containers |
| F-L1-9 | INFO | Malformed `hooks` values: `"abc"` crashes with a traceback (rc 1, untouched, no REFUSED line); `{"Stop": "abc"}` is rewritten as `["a","b","c",<ours>]` with rc 0 and "installed 5". | reproduced | garbage in | refuse any `hooks` value or event value of the wrong type |
| F-L1-10 | INFO | `hook_context.py` letter-of-contract deviations with no material effect on the two wrapped hooks: non-zero-exit bytes are re-encoded (A2), all trailing newlines are stripped (A3), whitespace-only output is dropped (A4), a signal death returns 247 (A9), CRLF leaves `\r` (A12). | reproduced | contract letter only | write `proc.stdout`/`proc.stderr` bytes through `sys.stdout.buffer`; `out[:-1] if out.endswith("\n")` |
| F-L1-11 | INFO | Timeout path: a hook whose background child holds stdout stalls each call 55 s and loses all output, reported as "did not run" (A7). The 55 s constant assumes "Claude Code's 60 s default hook timeout"; the 2.1.280 binary's command-hook default reads as 600 s (`var Ia=600000`, INFERRED). edit-snapshot's Edit branch can reach 56 s if all seven 8 s probes time out. Neither wrapped hook backgrounds a child. | reproduced (A7); static (the rest) | none | report "timed out" rather than "did not run"; keep what was read |
| F-L1-12 | INFO | A8: under a non-UTF-8 stdout encoding a blocking exit 2 with non-ASCII stdout becomes 1. Unreachable in this deployment (the claude process sets no locale variables; Python runs in UTF-8 mode). | reproduced with PYTHONIOENCODING=ascii | none here | the byte-passthrough fix in F-L1-10 removes it |
| F-L1-13 | INFO | Wrapping a hook that prints its own hook JSON (a deny) neutralizes the decision (A15); `EVENTS` omits Stop, so wrapping the retro gate would disable it silently (usage error, exit 0). Neither is wired today. | reproduced | none | a comment: never wrap a JSON-speaking or blocking hook |
| F-L1-14 | INFO | Unchanged hook scripts now active in `/home/user` sessions: edit-snapshot screens `.py` files anywhere on disk (it fired on this lane's /tmp drivers); graft-first-nag ignores `tests/` paths; session-start.sh appends one `export PYTHONPATH="."` to CLAUDE_ENV_FILE per run (5 lines now) and re-runs setup.sh at every compaction (33 s wait, re-registers the ouroboros MCP server in /root/.claude.json each time); the retro gate re-fires on a retro commit that touches CLAUDE.md (6b31bdf). | observed live | none | none required |
| F-L1-15 | INFO (positive) | All five installed entries fired live; the two wrapped hooks' additionalContext reached this model; one block per call; the harness's plain-stdout rule confirmed from the binary; happy-path idempotence, `--check`, `--remove`; 24 concurrent installs consistent; adapters 7/7, 6/6, 9/9; premise 309 passed. | reproduced | | |

### 1.6 L1 gate recommendation: MERGE-READY-WITH-FOLLOWUPS

No finding meets the WHOLE blocking predicate at the PIN. F-L1-1 and F-L1-2 are contract-mapped (fully and partly), in-boundary
and have exact discriminators, but neither reproduces through the deployed path in its current state: the deployed repo path needs no
shell quoting, and the scripts are present. They are the two follow-ups to do first. F-L1-2's trigger is realistic (`git checkout main`
of the shared tree while the session-root settings stay in place), and its effect is severe (every Grep refused, and with
wiki-context.py absent every prompt dropped), so it deserves the next repair slot. F-L1-3 is material but lies outside L1's files.

## 2. L2: the AF-AP-181 race fix and its screen row (commit de06db6)

### 2.1 Reproductions

Driver `/tmp/vc2/l2_driver.py` (the helper exec'd from the PIN's file; the row loaded from the PIN's hook; "through the hook" = the
real `edit-snapshot.py` run on an Edit payload whose path holds `/tests/`, its TEST_SCREEN branch).

Red-green of the race mechanism (`os.path.exists` forced True, `open` raising ENOENT for pid 424242):
```
pre-fix logic (de06db6^, verbatim) under the lost read: AssertionError: agent child pid 424242 state gone, expected Z or gone
fixed helper under the lost read: 'gone' | site assert passes: True
```
That is CI run #1026's failure message, reproduced deterministically, and its fix.

Helper under hostile reads:
```
open raises PermissionError(EACCES) -> 'gone'     open raises OSError(EMFILE) -> 'gone'     open raises OSError(EIO) -> 'gone'
stat text ''                 -> '?'               '123 (x) \n'        -> '?'                '123 no-paren S 1\n' -> '123'
'123 (sp ace) X 1 1\n'       -> 'X'               '123 (a)b) Z 1\n'   -> 'Z'  (after the LAST paren, as contracted)
non-UTF-8 comm               -> UnicodeDecodeError (not an OSError, not caught)
```

The row over the tree (`git ls-tree -r 8b2be81`, every `.py`):
```
tracked .py files scanned: 1403 (of which outside sandbox-kit/ and .claude/: 710); hits: []
pre-fix tests/test_s0_01_frame_tee.py hits at lines: [2990, 3336]      (exactly the two pre-fix sites)
```

The row through the real hook:
```
fires: CI-1026 shape                                 FIRE      window: 1 line between                FIRE
window: 2 lines between                              FIRE      window: 3 lines between               quiet
quiet: fixed membership in ("Z", "gone")             quiet     quiet: same literal, other quote      quiet
MISS  trailing comment on the fallback line          quiet     MISS  annotated fallback (s: str = …) quiet
MISS  attribute target (self.state = "gone")         quiet     MISS  reversed comparison ("Z" == s)  quiet
MISS  membership that excludes the fallback          quiet     MISS  unittest assertEqual(s, "Z")    quiet
MISS  None fallback                                  quiet     MISS  one-line `except OSError: s = …` quiet
MISS  fallback literal holding an apostrophe         quiet     MISS  bytes literal                   quiet
MISS  CRLF hunk                                      quiet     MISS  a log line before the fallback  quiet
MISS  cross-function: s = _proc_state_after_kill(pid); assert s == "Z"                               quiet
MISS  assert-only hunk (an Edit that narrows the fixed assert back)                                  quiet
FP    fallback branch `return`s before the assert    FIRE      FP    fallback branch `continue`s     FIRE
FP    exception-to-sentinel idiom (except ValueError: got = "raised"; assert got == "ok")            FIRE
regex cost: 2,640,023-char hostile hunk 0.03 s; 4,140,000 chars of bare `except` lines 0.01 s
```
Test files outside a `/tests/` directory (where TEST_SCREEN never applies): only two vendored skill scripts under `.agents/skills/`.

Fresh gate on the real tree: `pytest tests/test_s0_01_frame_tee.py` -> `121 passed in 166.37s (0:02:46)`.

Mutation audit (`/tmp/vc2/l2_mutants.py`; each mutant on its own `git archive 8b2be81` copy; helper selection = the five new tests +
both site tests, row selection = `TestAFAP181` + the L1 real-hook test):
```
BASELINE helper sel: 7 passed, 114 deselected      BASELINE row sel: 5 passed, 171 deselected
KILLED   H1 state after the FIRST paren / H2 only ENOENT counts as gone / H3 a failed read reads Z
KILLED   H4 exists() check before the read / H5 whitespace field [2] (the old parsing)
SURVIVED S1 site 1 narrowed back to == "Z": 7 passed        SURVIVED S2 site 2 narrowed back to == "Z": 7 passed
KILLED   R1 no different-literal lookahead / R2 no lines allowed between / R5 "==" or "in" / R6 row id removed (collection error)
SURVIVED R3 window widened to 50 lines / R4 the assert may name any variable
```
Suggested narrower except `(FileNotFoundError, ProcessLookupError)` on a scratch copy: `7 passed, 114 deselected`, and EACCES then
raises PermissionError (fails loudly).

Bug-echo sweep of every tracked `.py` that reads `/proc/<pid>/stat`: the frame_tee gc-pid helper accepts `st in ("Z", "gone")`;
`_gone_or_zombie` in `test_s0_01_audit_cp5_controls.py:66` and `test_s0_01_pc_post_scan.py:117` read once, after the last paren, and
treat OSError as gone; `_proc_identity` in `test_s0_05_egress.py` reads a process expected alive. No unexploded AF-AP-181 sibling.
No test in the tree reaps process-wide (`waitpid(-1`, `os.wait()`, SIGCHLD: 0 hits), so the new zombie test cannot be robbed.

### 2.2 L2 finding inventory

| id | class | finding | evidence | contract / path / material / discriminator / boundary | suggested fix |
|---|---|---|---|---|---|
| F-L2-1 | FOLLOW-UP (top) | The exact CI-1026 regression is unguarded. Narrowing either site back to `== "Z"` (mutants S1, S2) keeps every test green, and the row cannot see it: the fallback now lives inside the helper (the cross-function MISS). The race only shows up as a rare CI red. | mutation audit + the row table | contract: the sites comply at the PIN; no criterion requires a pin; in boundary | a deterministic test that runs each site's final check under an injected lost read (exists True, open ENOENT), e.g. one `_assert_gone_or_zombie(pid, msg)` helper used by both sites and tested under the race; or a structural test pinning `in ("Z", "gone")` at both sites |
| F-L2-2 | FOLLOW-UP | The helper maps EVERY OSError to "gone" (EACCES, EMFILE, EIO measured), which is wider than the contracted ENOENT/ESRCH. In a test whose point is "SIGTERM killed the agent", an unrelated read failure (an fd leak, say) now reads as "the agent is dead" and passes; the pre-fix code failed loudly on the same error. | reproduced | contract: names ENOENT/ESRCH only; latent (the test's own children are readable); in boundary | `except (FileNotFoundError, ProcessLookupError): return "gone"`: keeps all 7 tests green (measured) |
| F-L2-3 | FOLLOW-UP | Row coverage (asked by the brief): 14 same-class shapes pass quiet, among them the natural ones: a trailing `# comment` on the fallback line, a log line before the fallback, the cross-function helper call, an assert-only Edit hunk. | reproduced through the real hook | advisory row ("TELLS, not verdicts") | allow a trailing comment and preceding statements in the except body; add a row for `_proc_state_after_kill(...)` followed by `== "Z"` |
| F-L2-4 | INFO | Legitimate shapes the row flags (asked by the brief): a fallback branch that `return`s or `continue`s before the assert (the assert can never see the fallback), and the exception-to-sentinel idiom. | reproduced through the real hook | advisory noise | none needed |
| F-L2-5 | INFO | Wording: the brief says "within two lines", the commit and registry say "within three lines". The regex allows 0-2 intermediate lines (fires at 2, quiet at 3, measured): both wordings fit. No test pins the upper bound (R3 survives) or the same-name back-reference (R4 survives). | measured | none | one boundary test at 3 lines, one different-name test |
| F-L2-6 | INFO | Helper residuals: state `X` (EXIT_DEAD) is returned as is and fails the site assert (a transient window the old code had too); an empty read gives `?`; a non-UTF-8 comm raises UnicodeDecodeError (unreachable: the test's children have ASCII names); pid reuse after the reap could read a foreign process (the file's own gc-pid docstring measures that window as unreachable). | reproduced (inputs) | flaky-red direction only | accept `X` with Z and gone, if wanted |
| F-L2-7 | INFO | The same file keeps the exists-then-read pair with whitespace `split()[2]` parsing in both wait loops and in site 2's pre-SIGTERM liveness check (PIN lines 3323-3328). The loops only choose an early exit; the pre-check expects a live agent. Not the CI race and not one of the contract's two call sites. | static | none | reuse the helper there too |
| F-L2-8 | INFO (positive) | Red-green reproduced with CI #1026's exact message; the row hits exactly the two pre-fix sites and nothing else in 1,403 tracked `.py` files; fire and quiet behave as contracted through the real hook; linear-time regex; no sibling in the tree; full file 121 passed; helper mutants H1-H5 and row mutants R1, R2, R5, R6 killed. | reproduced | | |

### 2.3 L2 gate recommendation: MERGE-READY-WITH-FOLLOWUPS

Every contract item holds at the PIN. The helper reads once (H4 is killed), maps ENOENT and ESRCH to "gone", and takes the state
after the last `)`. Both sites accept exactly `("Z", "gone")`. The row fires on the contracted shape and stays quiet on the fixed
shape. The brief asked for a shape of the same class the row misses and a legitimate shape it flags; both are listed (F-L2-3,
F-L2-4). The row is advisory, so these are follow-ups, not blockers. The one follow-up with real weight is F-L2-1: the regression this
commit fixes has no deterministic guard.

## 3. L3: `mojev` and `packedscorer` in the never-a-gate screen (commit 200ed95, D-071)

### 3.1 Reproductions (driver `/tmp/vc2/l3_driver.py`; every result from the REAL `scripts/no_laya_in_gates.py`, byte-equal to the PIN)

```
the live tree:  PIN (git archive 8b2be81, --root)   (0, 'no_laya_in_gates: 40 files scanned, clean')
                working tree (default root)          (0, 'no_laya_in_gates: 40 files scanned, clean')
                the repo's index (--staged)          (0, 'no_laya_in_gates: 40 files scanned, clean')
positives:      shell hook, MoJev in a comment                    (3, 'scripts/hooks/pre-commit:2:mojev')
                shell hook, mojev serve MoLeMo-Lab/mojev --port … (3, 'scripts/hooks/pre-commit:2:mojev')   one line per token per line
                shell hook, $MOJEV and ${MOJEV}                   (3, 'scripts/hooks/pre-commit:2:mojev')
                workflow run: block, `mojev eval metrics …`       (3, '.github/workflows/x.yml:8:mojev')
                .py checker, "PackedScorer" in a string           (3, 'proofs/S0-01/check_x.py:1:packedscorer')
                .py checker, "# MOJEV PACKEDSCORER"               (3, '…check_x.py:1:mojev\n…check_x.py:1:packedscorer')
                .py checker, from mojev.modeling import PackedScorer   (4, stderr 'gate-file-import-unresolved: proofs/S0-01/check_x.py:1 imports mojev.modeling')
                .py checker, try: import mojev / except ImportError    (4, stderr 'gate-file-import-unresolved: proofs/S0-01/check_x.py:2 imports mojev')
pre-commit path (--staged, scratch git repo): staged hook with PackedScorer -> (3, 'scripts/hooks/pre-commit:2:packedscorer');
                worktree cleaned, index still holding it -> (3, same line): it reads the index, as the hook needs
line numbers:   form feed before the token line  -> screen line 4, grep -n line 3;  FF inside an earlier line -> 4 vs 3;
                U+2028 inside an earlier line   -> 4 vs 3;  CRLF -> 3 vs 3.  No listed gate file (all 40 checked) holds any
                splitlines-only break today.
lookalikes:     Cyrillic o in mojev -> (3, ':2:jev');  Cyrillic o in packedscorer, a zero-width space or a soft hyphen in mojev -> rc 0
```

MoJev's OWN spellings (the brief's question; sources: `docs/research/findings/jev-audit/mojev-evidence.md` rows 1.6, 4.2, 6.3,
7.11 and 10.5, all read from the MoJev clone at a74d58c), each as one line of a listed shell hook:
```
PASSES rc=0  env var its code reads (7.11)              export MOJEV_DEVICE=cpu
PASSES rc=0  env var its code reads (7.11)              test -n "$MOJEV_SOURCE" || exit 1
PASSES rc=0  env var its browser build reads (7.11)     MOJEV_NODE_MODULES=/opt/nm node build.mjs
PASSES rc=0  model name its server returns (6.3)        curl -s localhost:8000/v1/models | grep -q mojev-latest
PASSES rc=0  its config model_type (1.6)                grep -q '"model_type": "mojev-scorer"' config.json
PASSES rc=0  its config class (1.6)                     … # PackedScorerConfig
PASSES rc=0  its dataset, BOTH runs pass (4.2)          hf download MoLeMo-Lab/mojev-mix --repo-type dataset --local-dir data/mix
PASSES rc=0  its browser cache name                     echo mojev-browser-v1
PASSES rc=0  its own test file                          pytest tests/test_mojev.py
PASSES rc=0  Open-Jev / openjev (10.5)                  python3 openjev.py --state Open-Jev
PASSES rc=0  (contract: clean by design)                echo mojev_probe packedscorer_test
```
Row 10.5 applied the rule by reading ("the screen was NOT run"); these are the same verdicts, now from running the screen.

Tests and mutation audit (`/tmp/vc2/l3_mutants.py`, each mutant on its own `git archive 8b2be81` copy):
```
real tree: pytest tests/test_no_laya_in_gates.py -> 121 passed in 9.66s
scratch baseline: 1 failed, 120 passed (test_planted_violation_in_real_gate_path: the archive omitted tests/fixtures/decisions/,
  "gate-file-missing: …/tests/fixtures/decisions/gate_violation/scripts/gate_files.txt"; an artifact of the copy, so every
  mutant line below is read net of that one test)
KILLED   T1 mojev removed             (+ test_mojev_vocabulary_fires, test_simple_tokens_locked)
KILLED   T2 packedscorer removed      (+ test_mojev_vocabulary_fires, test_simple_tokens_locked)
KILLED   T3 mojev-mix added           (+ test_simple_tokens_locked: the lock names the whole list)
KILLED   T4 case folding dropped      (+ test_identifier_boundary, test_mojev_vocabulary_fires)
KILLED   T5 substring, not whole run  (+ test_live_tree_clean, test_identifier_boundary, test_mojev_vocabulary_fires, test_live_tree_clean_staged)
SURVIVED T6 run class gains '.'       (not an L3 property)
```

### 3.2 L3 finding inventory

| id | class | finding | evidence | contract / path / material / discriminator / boundary | suggested fix |
|---|---|---|---|---|---|
| F-L3-1 | FOLLOW-UP (top; the brief's explicit question) | Spellings MoJev's own code, server and data use pass a listed gate file unflagged: the env vars `MOJEV_SOURCE`, `MOJEV_DEVICE`, `MOJEV_NODE_MODULES`; the served model name `mojev-latest`; the config `model_type` `mojev-scorer` and class `PackedScorerConfig`; the dataset id `MoLeMo-Lab/mojev-mix` (neither run fires); `test_mojev`, `mojev-browser-v1`, `Open-Jev`/`openjev`. The env vars and the model name are the strings a shell or config integration would most likely carry. | reproduced through the real script | contract: "longer runs stay clean" makes these clean BY DESIGN, so not a violation; a completeness gap against KC-J1's intent; in boundary | add the upstream identifiers as SIMPLE_TOKENS (`mojev_source`, `mojev_device`, `mojev_node_modules`, `mojev-latest`, `mojev-scorer`, `packedscorerconfig`, `mojev-mix`, `molemo-lab`) and update the lock test; a prefix rule is the alternative, but it would also catch our own `mojev_probe` / `mojev-stage`, which the contract keeps clean |
| F-L3-2 | INFO | A `.py` gate file that IMPORTS mojev is refused with exit 4 `gate-file-import-unresolved`, and the `path:line:mojev` line never prints (the include-edge check returns before the scan). The barrier holds (non-zero), but the refusal names an import, not the vocabulary. `_flagged_by_vocabulary` routes only `agent_factory.decisions` imports to the vocabulary report. This predates L3 and applies to every simple token (`import laya` too). | reproduced | letter of "the exact path:line:token line" only; no hole | route imports whose first component is a simple token to the vocabulary report |
| F-L3-3 | INFO | Line numbers come from `str.splitlines()`, which also breaks at FF, VT, FS/GS/RS, NEL and U+2028/2029: one such character before the token puts the reported line one past `grep -n`. Latent (no listed gate file holds one); predates L3. | reproduced | message only | `content.split("\n")` |
| F-L3-4 | INFO | Lookalike spellings pass (Cyrillic o in packedscorer; a zero-width space or soft hyphen in mojev). Deliberate obfuscation is outside a vocabulary tripwire's job. | reproduced | hypothetical misuse | none |
| F-L3-5 | INFO | `test_mojev_vocabulary_fires` exercises only a shell hook; the scan is file-type-blind (measured in 3.1), so this is a test-breadth note, not a behavior gap. | static + 3.1 | none | optional .py and .yml cases |
| F-L3-6 | INFO (positive) | Live tree clean at the PIN, in the working tree and in the index; exact lines in every gate-file type for text occurrences; the pre-commit `--staged` path fires and reads the index; the longer runs stay clean; case-insensitive; 121 passed; mutants T1-T5 killed; the lock names the whole list. | reproduced | | |

### 3.3 L3 gate recommendation: MERGE-READY-WITH-FOLLOWUPS

Every contract item holds at the PIN. Both tokens fire in any case as whole runs, with the exact line in every gate-file type the
scan reads as text. The longer runs stay clean. The live tree is clean. The lock names the whole list. Asked directly: yes, several
spellings MoJev's own code, server and dataset use still pass a gate file (F-L3-1). The frozen contract makes longer runs clean by
design, so this is a follow-up: add the upstream identifiers now, while no MoJev code is near a gate.

## 4. Summary

| landing | recommendation | blocking findings | top follow-ups |
|---|---|---|---|
| L1 hooks (a12e672) | MERGE-READY-WITH-FOLLOWUPS | none | F-L1-2 a broken registration BLOCKS (dash `cd` exit 2; python can't-open exit 2; `git checkout main` is enough to block every Grep); F-L1-1 a repo path needing shell quoting breaks idempotence, `--check` and `--remove`; F-L1-4 load-bearing test gaps (the `cd`, the SessionStart override, the event name); F-L1-3 the harness's 10,000-char persist threshold hides the SessionStart live-state (outside L1's files) |
| L2 AF-AP-181 (de06db6) | MERGE-READY-WITH-FOLLOWUPS | none | F-L2-1 the CI-1026 regression itself has no deterministic guard; F-L2-2 the helper reads every OSError as "gone"; F-L2-3 fourteen same-class shapes the row misses |
| L3 D-071 (200ed95) | MERGE-READY-WITH-FOLLOWUPS | none | F-L3-1 MoJev's env vars, model name, config class and dataset id pass the screen |

F-L1-1 note for the coordinator: it meets every predicate item except material effect at the deployed path (the deployed repo path
needs no quoting). If the coordinator reads the brief's listed suspicions as in-contract environments, F-L1-1 is the one finding
that would block.

## 5. What was reproduced, what was read statically, what was skipped

Reproduced (commands in this session): the premise (hashes, `--check`, 309 passed, 13 passed); every installer shape in 1.4 on
scratch copies; the five installed strings under `/bin/sh -c` and `/bin/bash -c`; every wrapper shape A1-A15; the L1, L2 and L3
mutation audits; the L2 red-green; the row over 1,403 tracked `.py` files and through the real hook; every L3 screen result; the full
`tests/test_s0_01_frame_tee.py` (121 passed in 166.37s) and `tests/test_no_laya_in_gates.py` (121 passed in 9.66s); the adapter
scripts (7/7, 6/6, 9/9); `scripts/vendored_manifest.py --check` at 8b2be81 on a sparse `--shared` clone
(`PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots`); the live firing of all five installed hooks (this lane's own
Read and Grep, plus the parent transcript's records).

Read statically (primary source, not executed): the harness semantics in 1.2 (the 2.1.280 binary: the plain-stdout rule, `fpo=1e4`,
`shell:!0` with `child_process.spawn`, the event-name check, the Stop cap of 8, "UserPromptSubmit operation blocked by hook"); the
default command-hook timeout `Ia=600000` is INFERRED (minified name).

Skipped, with reasons: the repo-absent case through the live harness (it would need the real repo moved or a real hook script
deleted; reproduced instead through the exact installed strings under the harness's own shell); any write to
`/home/user/.claude/settings.json` (forbidden; only the brief's own read-only `--check` touched it); `harness-ports/tests/run-all.sh`
beyond the three adapter scripts (bullet 3 names only the adapters); the full `pytest proofs/ spikes/ tests/` suite (not in any
landing's contract; the three touched test files ran in full); `tests/test_decisions_*` and `src/agent_factory/decisions/volatile.py`
(another agent's files). No subagent, no commit, no push, no outward action. Scratch space: `/tmp/vc2` (drivers kept; copies deleted).
The sandbox disk was at 99 % (715 MB free) mid-run; deleting this lane's own mutant copies brought it back to 1.7 GB free.

Served model: `claude-opus-5-5` on 283 of 283 assistant records of this lane's transcript; no `"stop_reason":"refusal"`.
Finished: 2026-09-24 12:2xZ.
