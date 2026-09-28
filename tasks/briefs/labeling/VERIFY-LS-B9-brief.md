# VERIFY-LS-B9: attack the stack runner, its nine stacks and the round-2 items (task #339, D-103, D-104)

Role: adversarial-verifier (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/labeling/VERIFY-LS-B9-report.md`
(write it incrementally). If the harness refuses a report-file write, return the rest of the report as the text of your
final message; never work around the refusal.

Authored 2026-09-28 19:4xZ by the coordinator.

The change under test: the LS-B9 lane's working-tree files in the main tree `/home/user/agent-factory` (untracked; their
sha256 prefixes are in the premise): `scripts/stack.py`, `scripts/stacks.toml`, `scripts/gate_files.py`,
`scripts/handback_extract.py`, `scripts/gate_union.py`, `scripts/lint_files.py`, `tests/test_stack.py`. Contract:
`tasks/briefs/labeling/LS-B9-brief.md`: CONTRACT items 1-8 (round 1) and the `## ROUND 2` section at its end (items 1-7,
sent to the lane by message and copied there verbatim). The builder's report: `tasks/briefs/labeling/LS-B9-report.md`
(round 1, then `## Round 2`); its claims, its 14 deviations and its findings D12-D32 are hypotheses. The owner's rulings
behind it: D-103 and D-104 (1) in `docs/08_DECISION_LOG.md` (labels name fixed tool stacks, so the tools run the right
way every time; ripwire and sentrux active and used in the stacks).

Why it matters: the stacks are how the coordinator, and later Jev, run the tools per label. A `gate` that prints a green
count while a test that names a changed path never ran mints a hollow green at every commit; a `harvest` that saves the
wrong text loses a report of record; a step that reads ok while its instrument is missing hides an unmapped area; `{tmp}`,
the kill and the cap can delete, leak or fill the disk.

Your copy: never write the main tree (except your report), its `.jev/`, its `.sentrux-runtime/` (the shared sentrux
baseline) or `/root/.claude/`. Make a scratch copy: `mkdir -p /tmp/vlsb9/repo && git -C /home/user/agent-factory archive
HEAD | tar -x -C /tmp/vlsb9/repo`, then copy the seven lane files on top (make it a git repository of its own if a test or
a stack needs one, as the builder's mutation driver did). Run stacks with `--tree`, `--log-dir` and, for sentrux,
`SENTRUX_RUNTIME_DIR` pointed into your scratch. A run against the main tree is allowed only with `--log-dir` in your
scratch, and only for `list`, `explain`, `premise` and `gate mode=plan`; say first what each instrument writes, and where.

## WHAT TO ATTACK (report every observation; no severity filter)

1. **The runner's argv discipline (contract items 3-5).** A parameter value never becomes a shell word or an option of the
   program it feeds: try `;`, `$(...)`, backticks, spaces, a leading `-` or `--` in each type (path, paths, text, word,
   symbol, choice, int), a comma inside a path, U+2028, full-width digits, U+017F, a NUL, a newline, and a path through a
   symlink out of the tree. Each type's rule and the deny list (item 4) against their bypasses (`..`, a symlink to
   `.pc-bridge.env`, `.git/` spellings, `/root/.claude/projects/` reached through `{transcript}` with a crafted agent id).
   Every refusal: exit 2 before any step runs, and no run recorded.
2. **`gate` completeness (the headline risk).** For a changed path, can the run list omit a pytest file that names the
   path (the project rule: `grep -l <path> tests/*.py`) or that ripwire links? Can the print read green while a listed
   test was left out (shell tests under `harness-ports/tests/` are listed, not run: is that said on every path)? `graph=yes`
   and ripwire's wide lists (the builder's D24: 105 tests for seven files): is the width bounded, capped or at least stated
   before `mode=run`? A deleted path (ripwire exits 1) with `graph=yes` and with `graph=no`. The comma join (`{paths,}`,
   deviation 1): measure ripwire's multi-file form yourself.
3. **A missing instrument never reads ok (round-2 item 3).** Every step that calls ripwire, sentrux, node (GitNexus),
   graft, code-review-graph or rg: with its binary missing, is the status `unmapped`, and does a required step fail the run?
   `unmapped_if` false positives (a real output that quotes the wrapper's sentence) and false negatives (a wrapper that
   fails another way and exits 0). The CI shape (no instrument, a non-root user): what the builder assumed against what you
   can reproduce.
4. **`{tmp}`, the kill and the cap (round-2 items 4 and 6).** Mode 0700, outside every work tree, removed on success,
   failure and SIGINT, SIGTERM or SIGHUP; what a SIGKILL leaves; a pre-created or symlinked `/tmp/stack-<run id>` (is the
   name predictable; is it adopted?); the cap's kill of a live step and of its process group (a child that ignores SIGTERM;
   a grandchild that keeps writing); a truncated source never feeds a chain.
5. **`harvest` (round-2 item 7).** Run it on two finished lanes: this LS-B9 lane (`ac753871198ee8cfd`) and the scrubber
   repair (`a88c7c57f2fa2a96b`): does it save the right text each time (the hand-back, or the lane's longer report written
   before its last hand-back call)? Build synthetic transcripts for the edges: two hand-back calls, a long text after the
   last call, text blocks of 999 and 1000 characters, a tool_result holding a hand-back-shaped string, a user record, tags
   to neutralize. Show from the code, and with synthetic records only, that no path reads a `thinking` block's text.
6. **Ratings, records and the print (round-2 item 5; contract items 5-6).** Only rated stacks take ratings; a `--rate`
   that is refused never starts its run; the record's fields and its lock; the 9,000-character print cap; what the header
   states.
7. **`review` and sentrux (round-2 item 2).** Which baseline file does `scripts/sentrux_review.sh` read and write? Did the
   lane's 18:3xZ smoke run (its D30) change anything a later `compare` reads (the premise shows two `baseline.json` files)?
   What does `review mode=save` overwrite with no `SENTRUX_RUNTIME_DIR`? `lint_files.py` (deviation 4) against
   `lint_delta.py`'s rule on the same inputs.
8. **Mutation.** Reproduce at least six of the builder's 100 mutants as FAILED tests, one each for the gate union,
   `unmapped_if`, `{tmp}`, the cap, the rating refusal and the harvest extractor; add a mutant for each contract clause its
   set does not cover, and name the survivors.

## GATE

Apply the blocking predicate of skill `contract-gate` (contract-mapped, reproduced through the real code path, materially
effective, a concrete discriminator, in-boundary) and D-034 (a finding re-opens the build only if it is CORE-BLOCKING; the
rest become follow-ups). One recommendation: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS / NOT-READY / CONTRACT-INVALID, each
blocking finding with its reproduction command. Name separately anything that must hold before the stacks are wired into
CLAUDE.md, the output styles and the SessionStart catalog (the coordinator does that after your verdict).

## BOUNDARY

READ everything. WRITE only your report and scratch under `/tmp/vlsb9/` (removed at the end). No git writes in the main
tree. Never write the main tree's other files, its `.jev/`, `.sentrux-runtime/` or `/root/.claude/`.

## STANDING RULES

- No PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables. Never read a `thinking`
  block's content in any transcript.
- Other lanes are live: I59-F round 4 in the worktree `/home/user/i59-landing`, and VERIFY-SCRUB2-R1-R2 on the scrubber
  files of the main tree (`.lanes-live` lists them). Touch none of their files.
- Disk: 12,158 MB free at authoring. Scratch under 500 MB in all; one mutant tree at a time; a private `--basetemp` for
  every pytest run (`mkdir -p` its parent); never run the whole `tests/test_vendored_manifest.py` (a gate plan may list it;
  a whole-file run copies about 3.4 GB).
- Test counts are pasted from `scripts/test_summary.sh` with their set ids (`scripts/pc_suite.sh set-id -- <files>`).
  Stamps are substituted from `date -u`, never typed.
- Long commands in one foreground call, each under 10 minutes; kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short
  text of its own.

## PREMISE — MEASURED at authoring (2026-09-28 19:4xZ, the main tree at the pushed head; `bash scripts/premise_block.sh`)

```
$ git rev-parse --short HEAD
ca29894
$ git status --porcelain --untracked-files=all -- scripts/stack.py scripts/stacks.toml scripts/gate_files.py scripts/handback_extract.py scripts/gate_union.py scripts/lint_files.py tests/test_stack.py tasks/briefs/labeling/LS-B9-report.md
 M tasks/briefs/labeling/LS-B9-report.md
?? scripts/gate_files.py
?? scripts/gate_union.py
?? scripts/handback_extract.py
?? scripts/lint_files.py
?? scripts/stack.py
?? scripts/stacks.toml
?? tests/test_stack.py
$ sha256sum scripts/stack.py scripts/stacks.toml scripts/gate_files.py scripts/handback_extract.py scripts/gate_union.py scripts/lint_files.py tests/test_stack.py | cut -c1-16,65-
84d738b331127be0  scripts/stack.py
0b4eef56349bc5be  scripts/stacks.toml
b732d35f2c649045  scripts/gate_files.py
115416a0624bc59b  scripts/handback_extract.py
ed9de9247b58a31b  scripts/gate_union.py
546400ab9781e56f  scripts/lint_files.py
da6f1fb42b393a94  tests/test_stack.py
$ wc -l scripts/stack.py scripts/stacks.toml scripts/gate_files.py scripts/handback_extract.py scripts/gate_union.py scripts/lint_files.py tests/test_stack.py
  1293 scripts/stack.py
   447 scripts/stacks.toml
   130 scripts/gate_files.py
   145 scripts/handback_extract.py
   117 scripts/gate_union.py
    89 scripts/lint_files.py
  1624 tests/test_stack.py
  3845 total
$ command -v ripwire sentrux rg node graft code-review-graph
/root/.local/bin/ripwire
/root/.local/bin/sentrux
/usr/bin/rg
/opt/node22/bin/node
/opt/node22/bin/graft
$ find .sentrux-runtime -maxdepth 3 -name baseline.json -printf '%TY-%Tm-%Td %TH:%TM %p\n'
2026-09-28 18:34 .sentrux-runtime/tree/.sentrux/baseline.json
2026-09-07 22:57 .sentrux-runtime/baseline.json
$ python3 scripts/stack.py list
harvest  agent=<agent> [report=<path>]  — a finished lane: its served models and refusal stops, its SubagentHandback message (tags neutralized), the report linted and hashed
gate  paths=<paths> [mode=plan|run] [runs=1|2] [graph=yes|no]  — every test that names each path, united with the tests ripwire's call graph links to the change (graph=yes), the set id, and test_summary.sh runs times when mode=run
ctx  files=<paths> [q=<text>] [sym=<symbols>]  — the code-intel pack of files: graft skeletons and ask, GitNexus impact, code-review-graph, ripwire, the AP screen · rated
impact  sym=<symbol>  — the blast radius of one symbol from four instruments in parallel: GitNexus impact, code-review-graph callers and tests, ripwire edit-check · rated
find  q=<text>  — what the repo already holds on q: graft ask, the owner's rulings, the chat, the AF-AP registry rows · rated
premise  files=<paths>  — the premise facts of files: tracked or not, sha256, line count, the last commit that touched each
echo  pattern=<text> [roots=<paths>]  — the bug-echo sweep: the pattern in the six code roots, the incident log's lines, the AP screen over the files hit · rated
review  [files=<paths>] [mode=check|save|compare]  — a change's review: sentrux architecture health (check, save a baseline, compare with it), and for the files ripwire's test gate, the pyflakes delta and the AP screen · rated
ci  [branch=<text>]  — the branch's stage0-ci verdict through scripts/ci_gate.py: 0 passed, 75 not in yet, 1 red
$ mkdir -p /tmp/vlsb9-premise
$ bash scripts/test_summary.sh --basetemp=/tmp/vlsb9-premise/bt tests/test_stack.py | tail -1 | sed -E 's/ in [0-9.]+s.*//'
pytest-summary: 147 passed
$ rm -rf /tmp/vlsb9-premise
$ df -m / | tail -1
/dev/vda          258020 25781     12158  68% /
```

The builder's gates, quoted from its report (your item 8 re-runs what it needs): `1 files set=2ac01abb1067` `147 passed`
twice; `5 files set=2804489b9d6b` `431 passed` twice; the CI rehearsal `145 passed, 2 skipped`; mutants
`SET=r1 EXPECTED=52 KILLED=52` and `SET=r2 EXPECTED=48 KILLED=48`.
