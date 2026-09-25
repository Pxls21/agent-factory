# CTX1 report (D-089): CLAUDE.md shortened losslessly into skills; no GitNexus rewrite; no re-index without an update

Lane: code-implementer (sandbox, Opus 5.5). Started 2026-09-25 12:5xZ. PIN 715caaf. Local head at start 11242c6.
Status: DONE (14:0xZ). The gate recommendation is not this lane's. The CTX1 commit needs the coordinator steps in section 9 (a pin patch outside my boundary and a full manifest regeneration).

## 1. Premise re-measure (verified, 12:5xZ, local head 11242c6)

All rows match the brief's block. No mismatch.

```
$ wc -l -c CLAUDE.md AGENTS.md .hermes.md
   809  92730 CLAUDE.md
   419  32758 AGENTS.md
   523  45068 .hermes.md
$ git show 715caaf:CLAUDE.md | sha256sum | cut -c1-16   (and the working file)
6eae9de1c792c420 / 6eae9de1c792c420
$ grep -c '^## ' CLAUDE.md
17
boundary files vs PIN and vs working tree: all SAME (16 files incl. the five tests and the mirror test)
$ bash harness-ports/tests/test_context_mirrors.sh | tail -1
11 passed, 0 failed   (rc 0)
$ bash scripts/test_summary.sh <the five files>
pytest-summary: 233 passed in 64.13s (0:01:04)
$ bash scripts/pc_suite.sh set-id -- <the five files>
5 files set=bcfd3537c9e3
analyze call sites: scripts/hooks/post-commit:51, scripts/resume-heal.sh:21, harness-ports/bin/pc-setup.sh:107 and :125
analyze --help: --skip-agents-md and --no-stats both present
CLAUDE.md name counts: jev_context.py 6, hiccup_scan.py 6, jev_locate.py 1, search-intercept.py 6, graft-first-nag.py 2, gn_mcp.py 1, jev.py 1
```

## 2. Measurements that shaped the design (verified unless marked)

- Commit mix, last 400 first-parent commits (`git log --name-only`): 275 docs-only (Markdown or wiki/ todo/
  transcripts/ tasks/), 125 with other paths; of those 125, 28 touched only `.sha256` (skill bakes), 7 only `.json`,
  4 only `.sh`. So per-graph read-sets matter: no graph parses `.sha256`.
- Read-sets, generated from each tool's own source by `scratchpad/ctx1/gen_readsets.py` (not typed):
  graft 0.16.0 43 extensions (dist/graph/extract.js EXTENSIONS + generic.js + container.js; no `.sh`, no `.md`:
  its fingerprint holds 840 files, none `.sh`); gitnexus 1.6.10 41 extensions + 5 Ruby filenames
  (dist/_shared/language-detection.js EXTENSION_MAP); code-review-graph 2.3.8 62 extensions (parser.py
  EXTENSION_TO_LANGUAGE, lower-cased) + extension-less files (shebang probe); codebase-memory 236 extensions + 24
  filenames, case-sensitive, from the VENDORED source (sandbox-kit/codebase-memory-mcp/src/discover/language.c,
  version "dev"); the installed binary is 0.10.8 and its table could not be read (assumed equal).
- GitNexus ingests Markdown (dist/core/ingestion/markdown-processor.js) and codebase-memory reads `.md`; graft
  cards the probe scripts under `tasks/` (graft/tasks/briefs/...). The contract's docs plane re-indexes none of
  them, so those nodes lag until the next commit that re-indexes (the contract's choice; stated in the hook).
- `gitnexus analyze --skip-agents-md` skips only the AGENTS.md/CLAUDE.md upsert; the skill install still runs
  (dist/cli/ai-context.js:419-444). `--index-only` implies the skip too (dist/cli/analyze.js:1038-1039).
- Merges: plain `git diff-tree -r HEAD` lists nothing for a merge; `-m` lists the union of both parents' diffs
  (probed in a throwaway repo). The re-index list uses `--root -m`; the wiki marker keeps its own list unchanged.
- Automatic analyze call sites: post-commit:51, resume-heal.sh:21, pc-setup.sh:107 and :125 (all in boundary).
  Printed MANUAL suggestions without the flag, out of boundary: scripts/orient.sh:21 and
  harness-ports/bin/mcp-server.sh:65 (`npx gitnexus analyze`).

## 3. Progress log (verified as it happened)

- post-commit hook rewritten (per-graph read-sets, docs plane, `--skip-agents-md`, one decision line in
  `$T/post-commit-reindex.log`, `AF_POST_COMMIT_TMP` seam, PATH-first tool lookup with the old fixed paths as
  fallback). New test tests/test_post_commit_reindex.py: RED on the PIN's hook (13 failed, 1 passed: the scanner's own
  negative control), GREEN on the new hook (14 passed). The PIN hook for the red run had only its two fixed binary paths
  and its /tmp paths rewritten to the fakes (no real indexer launched).
- `--skip-agents-md` added at resume-heal.sh:21 and pc-setup.sh:107, :125.
- Quirk readers: jev_context.QUIRK_SOURCES / inst_quirks, hiccup_scan.QUIRK_SOURCES / load_candidates, jev_locate
  docstring; search-intercept's four anchors cite `.claude/skills/env-tool-quirks/SKILL.md`.
- Skills: new env-tool-quirks, pc-bridge-lanes, ouroboros-stdio (both trees, identical); extended build-loop,
  deep-work, session-continuity, code-intel-trio (the same block appended to both trees). All built by
  scratchpad/ctx1/assemble.py from the PIN's bytes by line number (no moved line retyped).
- Scratch CLAUDE.md: 500 lines, 44,613 bytes, 17 `## ` sections. Losslessness check on it: 727 of 727 found.
- FOUND (outside the boundary, LOUD): tests/test_vendored_manifest.py pins the `.claude/` first-party count (13, 13,
  14) and the first-party file list. The three new skills are first-party, so a clean checkout with CTX1 reads 16/16/17:
  proven on a `git archive HEAD` mirror (3 failed at :382, :450, :563); the prepared patch
  (scratchpad/ctx1/test_vendored_manifest.ctx1.patch) makes the pinned tests pass there (4 passed). The coordinator
  must apply it in the CTX1 commit (the pre-commit CLASS-PIN gate blocks otherwise).
- INCIDENT (mine, LOUD): a whole-file run of tests/test_vendored_manifest.py on a mirror filled the disk for a few
  seconds around 13:40:4x-13:40:5x UTC (each test copies ~75 MB; 1.1 GB basetemp). Any other lane's write in that
  window may have failed with `No space left on device`. I deleted my two basetemps (pytest-250, pytest-251) and the
  mirror: free space back to 2,361 MB. Baked as a quirk line in env-tool-quirks. The incident-log row is the
  coordinator's (docs/INCIDENT-LOG.md is outside my boundary).

## 4. Result (verified)

| | before (PIN 715caaf) | after |
|---|---|---|
| CLAUDE.md lines | 809 | 498 |
| CLAUDE.md bytes | 92,730 | 44,193 (-52.3%) |
| `## ` sections | 17 | 17 |
| AGENTS.md bytes | 32,758 | 32,641 (the counts line only) |
| `.hermes.md` | 45,068 | unchanged (it has no GitNexus block) |

CLAUDE.md was written twice (13:44:02 and 13:55:07 UTC), not once: the coordinator's mid-task constraint (the
"Load `<skill>` before/when <situation>" form) arrived after the first install. Both writes were single `cp` calls
of a scratch file that had passed the losslessness check and the mirror gate first.

Kept inline (the every-turn rules): the git branch and push rules with the CI gate; the NO STUBS section whole
(rule, sanctioned stubs, tactic index); the STANDING PROJECT RULES (hash unchanged: the mirror test passes); the
ground-truth reading order and onboarding map (its `wiki/` entry became a pointer); the honey paragraph, the prose
style, STAGE ROUTING, the routing table, the TIERS bullet (with its dated quirk marker, line 112 at the PIN), installed
tooling, escalation, SAFEGUARD-FLAG ROUTING, EXPLICIT `model=`, the orchestration paragraph with its standing
do-nots; COMPUTE PLACEMENT; the PC bridge paragraph; the GitNexus tier paragraph; no AskUserQuestion; no
manual-approval MCP tools; pipeline order; task tracking; the count and stamp rule (PIN line 572); the incident-log
rule; GRAFT FIRST and the code-intel diagnosis; "Project code lives under"; the GitNexus block minus its counts line.

## 5. The losslessness check (contract 1)

Tool: `tests/test_claude_md_lossless.py` (pytest, and a script: `python3 tests/test_claude_md_lossless.py [--new PATH]`).
Every non-empty PIN line, whitespace-normalized, must be a substring of the collapsed text of the current CLAUDE.md or
of a skill it names in backticks. Summary line on the installed file (pasted):

```
lossless: 727 non-empty PIN lines checked, 727 found (CLAUDE.md 388, deep-work 72, build-loop 66, code-intel-trio 63, env-tool-quirks 55, session-continuity 39, ouroboros-stdio 32, pc-bridge-lanes 12), 0 missing, 0 dropped as duplicates (none); 723 in context, 4 found only bare
bare 435: **The shell's cwd resets to `/home/user` after a container restart** — start every command chain
bare 441: **Podman on the PC refuses a SHORT image name with no TTY** (...)
bare 536: **Full text + war-story evidence: skill `build-loop` — load it before any code increment.**
bare 537: Model-agnostic, per increment, no skipping steps. The operative core:
PIN exact-duplicate lines: 1
  dup: | --- | --- |
```

- Duplicate list: NONE dropped. The PIN's only exact-duplicate line is the GitNexus tables' `| --- | --- |`, kept twice.
- The contract-4 changes are not exceptions: the removed counts line (PIN 768) and the pre-CTX1 ownership sentence
  (PIN 759-763) are kept verbatim as a marked history block at the end of `code-intel-trio`, so all 727 lines are found.
- The 4 bare-only lines are deliberate split points, each reviewed: 435 was reunited with its tail 439 (the PIN had
  split one sentence across three inserted quirk lines); 441 (podman) moved to pc-bridge-lanes while its neighbors
  moved to env-tool-quirks; 536 is the build-loop pointer kept here while 537 (the block's first line) moved.
- Every "found" label is an intended destination: no line was found only in an unrelated skill.
- Negative controls (pytest): a moved line cut from an in-memory copy of env-tool-quirks is reported missing at its PIN
  line; a synthetic set shows a missing line, a DROPPED entry and a coincidental short match ("it.") flagged bare.

## 6. Pointer lines: situation to skill (the coordinator's CTX1 table)

The 14 "CTX1 pointer" rows are mine, in the "Load `<skill>` before/when <situation>" form; each sentence starts a
physical line except line 285 (a map bullet: "`wiki/` — the continuity spine: load `session-continuity` when ...",
lowercase and mid-line; a router should match case-insensitively). The three new skills' descriptions use the same
situation phrases (one constant per phrase in scratchpad/ctx1/assemble.py). The "PIN pointer" rows are verbatim PIN text
in the form "skill `X` — load it ..."; the generator missed three of them because "load it" wraps: 144-145
(`orchestration`: before authoring any brief, dispatching agents, or pushing delegate work), 393-394 (`deep-work`: whenever
the triggers below fire) and 440-442 (`code-intel-trio`: before any Phase-1 grounding, impact analysis, dead-wiring hunt,
or DORMANT claim).

| CLAUDE.md line | skill | situation (verbatim) | kind |
|---|---|---|---|
| 77 | `pc-bridge-lanes` | before dispatching, re-attaching or harvesting a PC lane, or sizing lanes per route. | CTX1 pointer |
| 181 | `anti-hollow-green` | load when designing or reviewing ANY gate/oracle/test/guard):** 1. | PIN pointer (verbatim, `skill X — load it ...` form) |
| 285 | `session-continuity` | when updating `wiki/topics/live-state.md` or answering the retro gate (the per-commit freshness mandate, its hooks, the resume order). | CTX1 pointer |
| 304 | `env-tool-quirks` | before using an ops script (resume-heal, orient, relaunch-suite, pc_suite, why, replay_transcript_edits, lint_delta, verify-planning-repo, anchor_edit). | CTX1 pointer |
| 329 | `ouroboros-stdio` | before any Ouroboros interview round, fan-out submission, resume or seed generation (the stdio client `scripts/ooo_mcp.py` and its measured quirks). | CTX1 pointer |
| 348 | `env-tool-quirks` | before a background job, a `pgrep` or `pkill`, a commit, a push, an anchor edit, a test gate or pasted count, a proof regeneration, a `vendored_manifest.py --write` or a worktree-isolated Agent dispatch. | CTX1 pointer |
| 350 | `pc-bridge-lanes` | before a `pc.sh`, `pc_lane.sh` or `pc_suite.sh` call, or a PC-side sqlite, systemctl or podman command. | CTX1 pointer |
| 372 | `deep-work` | before starting a substantial new subsystem or authoring a research prompt (audit → research prompt → findings → council → Ouroboros interview → seed → task breakdown → hand-build). | CTX1 pointer |
| 379 | `build-loop` | before writing code (the four behavioral guidelines: think before coding, simplicity first, surgical changes, goal-driven execution; deep-mode governs on conflict). | CTX1 pointer |
| 384 | `build-loop` | load it before any code increment. | PIN pointer (verbatim, `skill X — load it ...` form) |
| 386 | `build-loop` | before any code increment, test or commit (its operative core moved there verbatim). | CTX1 pointer |
| 401 | `deep-work` | before a new subsystem, a gate, security or store spine change, a code review of a stretch, or any work where a wrong green is expensive (the phase index moved there verbatim). | CTX1 pointer |
| 409 | `build-loop` | before adding a decision path, an event or a span to a component (the five key rules). | CTX1 pointer |
| 413 | `session-continuity` | on EVERY resume from a compaction summary, BEFORE any resumed work or timeline claim** (fetch origin, compare the three clocks, re-read the PC bridge env). | CTX1 pointer |
| 445 | `code-intel-trio` | before any semantic code question, Phase-1 grounding, impact analysis, dead-wiring hunt or DORMANT claim, and when an MCP server fails to connect (the core reflexes; the CLI, not MCP, on every venue). | CTX1 pointer |
| 454 | `code-intel-trio` | before editing this block (its pre-CTX1 wording, verbatim). | CTX1 pointer |

## 7. Tests (verified; counts pasted)

```
$ bash scripts/pc_suite.sh set-id -- <9 files: the brief's five + test_post_commit_reindex.py, test_claude_md_lossless.py,
                                       test_hooks_worktree.py, test_shell_syntax.py>
9 files set=610b9e79ddda
run 1: pytest-summary: 265 passed in 96.35s (0:01:36)
run 2: pytest-summary: 265 passed in 96.79s (0:01:36)
$ bash scripts/pc_suite.sh set-id -- <the brief's five files>
5 files set=bcfd3537c9e3
pytest-summary: 237 passed in 63.63s (0:01:03)          (premise: 233; +2 in test_jev_context, +2 in test_search_intercept)
$ bash harness-ports/tests/test_context_mirrors.sh | tail -1
11 passed, 0 failed
$ python3 -m pyflakes <the 10 changed or new .py files>     rc 0
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <each of the 30 files written>        0 for every one
$ bash harness-ports/bin/sync-skills.sh --check     in sync (413 skills), 15 INTENTIONAL, rc 0
$ bash harness-ports/bin/sync-lane-skills.sh --check    in sync (25 skills)
$ bash harness-ports/tests/test_sync_skills.sh | tail -1    34 passed, 0 failed
```

Red first, each on the PIN's code (verified):
- tests/test_post_commit_reindex.py on the PIN hook: 13 failed, 1 passed (the passing one is the scanner's own negative
  control). Docs-only and non-read commits launched all four, analyze had no `--skip-agents-md`, and there was no log line.
- the two new jev_context tests on the PIN module: 2 failed (the skill quirk not found; no QUIRK_SOURCES).
- the hiccup candidates test on the PIN module: red (no QUIRK_SOURCES); the PIN's own hiccup tests against the new tree:
  2 failed ("no CLAUDE.md passage holds 'CLAUDE.md: an Agent dispatch with isolation "worktree" ...'";
  `assert 234 == (218 + 1)`).
- the two new search-intercept anchor tests on the PIN hook (SEARCH_INTERCEPT_UNDER_TEST): 2 failed (trailing-amp's anchor
  cites CLAUDE.md, which no longer holds the quote).
- tests/test_claude_md_lossless.py: red-green by its negative controls only (the real check has nothing to be red
  against before the move).

## 8. Files (verified)

Modified: CLAUDE.md (+42 -353), AGENTS.md (-2: the counts line and its blank), scripts/hooks/post-commit (+103 -25),
scripts/resume-heal.sh:21, harness-ports/bin/pc-setup.sh:107 and :125 (the flag), scripts/jev_context.py (+24 -8:
QUIRK_SOURCES and inst_quirks), scripts/hiccup_scan.py (+17 -12: QUIRK_SOURCES and load_candidates, CLAUDE_MD removed),
scripts/jev_locate.py (docstring), .claude/hooks/search-intercept.py (+12 -8: QUIRK_SKILL, the four anchors, a
docstring), tests/test_jev_context.py (+27), tests/test_hiccup_scan.py (+17 -6), tests/test_search_intercept.py
(+35 -1), tests/test_hooks_worktree.py (+3 -1: AF_POST_COMMIT_TMP, so its commits stop writing the real /tmp log);
.claude/skills/{build-loop,deep-work,session-continuity,code-intel-trio}/SKILL.md and their .agents ports (the moved
block appended identically in both trees; the .claude descriptions of build-loop and deep-work fixed where the move made
"CLAUDE.md carries the condensed steps/phase index" false, plus build-loop's body lines 8-9; session-continuity and
code-intel-trio descriptions gained the moved situations in both trees; the .agents build-loop/deep-work descriptions
say "the project instructions file", still true, left alone).
Created: .claude/skills/{env-tool-quirks,pc-bridge-lanes,ouroboros-stdio}/SKILL.md and identical .agents copies;
tests/test_post_commit_reindex.py (189 lines); tests/test_claude_md_lossless.py (154 lines); this report.
Written by the bake tail (`bash scripts/skill_bake_finish.sh build-loop deep-work session-continuity code-intel-trio
env-tool-quirks pc-bridge-lanes ouroboros-stdio`, rc 0, 14 paths listed): .agents/lane-skills/{build-loop,
code-intel-trio,deep-work,session-continuity}/SKILL.md, the 8 skill files above, harness-ports/hand-ported.sha256,
sandbox-kit/VENDORED-MANIFEST.md.

## 9. NOT done, and what the CTX1 commit needs (LOUD)

1. **tests/test_vendored_manifest.py pins go red with the three new skills (outside my boundary).** The file pins the
   `.claude/` first-party count (13 at :382, :386, :450; 14 at :563) and the first-party list. The new skills are
   first-party, so a clean checkout reads 16/16/16/17. Proven on a `git archive HEAD` mirror with my `.claude/` files:
   HEAD's test failed 3 at :382, :450, :563; the patched test passed all 4 selected. The patch
   (scratchpad/ctx1/test_vendored_manifest.ctx1.patch):

```diff
--- a/tests/test_vendored_manifest.py	2026-09-25 06:08:13.128047069 +0000
+++ b/tests/test_vendored_manifest.py	2026-09-25 13:41:48.058100914 +0000
@@ -379,11 +379,13 @@
     # llm-wiki-compiler + 4 output-styles), 61 declared-set members (47 aegis + 12 prism
     # + 2 typesafe), and a 12-file remainder. The 129 pin is replaced by K1-h counts.
     # 12 -> 13 on 2026-09-24 (JT3 lands, tasks #228/#225): hooks/search-intercept.py is first-party (no kit counterpart).
-    assert manifest_row(manifest, ".claude/ (first-party)").split(" | ")[6:8] == ["13", "0"]
+    # 13 -> 16 on 2026-09-25 (CTX1, D-089): the three skills CLAUDE.md's text moved into (env-tool-quirks,
+    # ouroboros-stdio, pc-bridge-lanes) are first-party (no kit counterpart, no declared set).
+    assert manifest_row(manifest, ".claude/ (first-party)").split(" | ")[6:8] == ["16", "0"]
     assert [path for path, klass in classes.items() if klass == "kit-adapted"] == ADAPTED_PATHS
     assert sum(klass == "kit-verbatim" for klass in classes.values()) == 2955
     assert sum(klass == "kit-adapted" for klass in classes.values()) == 17
-    assert sum(klass == "first-party" for klass in classes.values()) == 13
+    assert sum(klass == "first-party" for klass in classes.values()) == 16
 
 
 # K1-h: the 12-file remainder of `.claude/ (first-party)` at the PIN. The three
@@ -401,6 +403,9 @@
     "skills/PROVENANCE-PRISM.md",
     "skills/PROVENANCE-TYPESAFE.md",
     "skills/codebase-memory/SKILL.md",
+    "skills/env-tool-quirks/SKILL.md",
+    "skills/ouroboros-stdio/SKILL.md",
+    "skills/pc-bridge-lanes/SKILL.md",
     "skills/session-start-hook/SKILL.md",
     "skills/wiki-compiler/SKILL.md",
 ]
@@ -408,7 +413,7 @@
 # The three PROVENANCE-*.md files are the only first-party files OUTSIDE a
 # declared set prefix and outside the copy rule; everything else under the
 # set prefixes is a set member, everything byte-identical to a kit root is a
-# copy, and the 13 above are the remainder (12 at K1-h, plus JT3's hook).
+# copy, and the 16 above are the remainder (12 at K1-h, plus JT3's hook, plus CTX1's three skills).
 K1H_SET_REMAINDER_PATHS = {
     "skills/PROVENANCE-AEGIS.md",
     "skills/PROVENANCE-PRISM.md",
@@ -437,7 +442,7 @@
 
 
 def test_k1h_claude_classification_and_remainder(tmp_path: Path) -> None:
-    """The K1-h class table: 13 first-party (the named remainder; 12 at K1-h plus JT3's hook), 61 set
+    """The K1-h class table: 16 first-party (the named remainder; 12 at K1-h, JT3's hook, CTX1's 3 skills), 61 set
     members (47 aegis + 12 prism + 2 typesafe), 56 copies (20 + 19 + 13 + 4),
     and kit-verbatim 2955 / kit-adapted 17 (D-054, D-065, AF-AP-182). The 129-pin test
     above carries the manifest row; this test carries the per-class split."""
@@ -447,7 +452,7 @@
     classes = class_rows(root / module.CLASSES_PATH)
     counts = k1h_class_counts(classes)
 
-    assert counts.get("first-party", 0) == 13
+    assert counts.get("first-party", 0) == 16
     assert counts.get("vendored:aegis", 0) == 47
     assert counts.get("vendored:prism", 0) == 12
     assert counts.get("vendored:typesafe", 0) == 2
@@ -560,7 +565,7 @@
     assert classes["agents/hive-builder.md"] == "first-party"
     counts = k1h_class_counts(classes)
     assert counts.get("copy:sandbox-kit/honey-for-devs/", 0) == 18
-    assert counts.get("first-party", 0) == 14   # the 13-file remainder (JT3's hook since 2026-09-24) plus the changed copy
+    assert counts.get("first-party", 0) == 17   # the 16-file remainder (CTX1's skills since 2026-09-25) plus the changed copy
 
 
 def test_k1h_ambiguous_copy_blob_is_refused_by_name(tmp_path: Path) -> None:
```

2. **The manifest from the bake tail is incomplete for this commit.** `skill_bake_finish.sh` lists changed files with
   `--untracked-files=no` and only under the skill trees, so its clean worktree held neither the three untracked new
   skills nor `.claude/hooks/search-intercept.py`. Its VENDORED-MANIFEST.md is therefore wrong for the CTX1 tree, and the
   class file was left unchanged. In the main tree `python3 scripts/vendored_manifest.py --check` fails today:
   first-party 13 committed vs 18 generated (my 3 new skills plus 2 ignored files under `.claude/fast-jev-output/`, the
   task #232 quirk). The commit steps: (a) stage everything, including the six new skill dirs; (b) apply the patch
   above; (c) regenerate VENDORED-MANIFEST.md and VENDORED-CLAUDE-CLASSES.tsv from the full CTX1 tree with no ignored
   files, either with `.claude/fast-jev-output/` moved aside for `python3 scripts/vendored_manifest.py --write` then
   `--check` in the main tree, or in a clean worktree holding every staged change; (d) keep
   `.claude/fast-jev-output/` aside during the commit too, because the pre-commit CLASS-PIN gate runs the pinned tests
   on the working tree; (e) commit with SKIP_MANIFEST_CHECK=1, as the bake's own instruction says.
3. **Incident, mine:** a whole-file run of tests/test_vendored_manifest.py on my mirror filled the disk for a few
   seconds around 13:40:4x-13:40:5x UTC (each of its 57 tests copies about 75 MB into pytest's tmp_path; 1.1 GB in one
   basetemp). Any other writer on the box in that window may have failed with `No space left on device`. I deleted
   my basetemps (pytest-250, pytest-251) and the mirror; free space went back to 2,361 MB. Baked as a quirk line
   (dated) at the end of env-tool-quirks. The docs/INCIDENT-LOG.md row is the coordinator's (outside my boundary).
4. Not changed, outside the boundary; each still names or runs the old way:
   - scripts/orient.sh:21 and harness-ports/bin/mcp-server.sh:65 print a manual `npx gitnexus analyze` with no flag;
   - code-intel-trio's own fresh-container recipe (line 74) runs `npx --yes gitnexus@1.6.7 analyze .` with no flag. I
     left it because I could not verify offline that 1.6.7 accepts `--skip-agents-md` (1.6.10 does);
   - harness-ports/lane-skills.txt does not list the new skills, so PC lanes don't get them;
   - .wiki-compiler.json excludes `.claude/`, so the moved text leaves the wiki compiler's inputs;
   - cosmetic stale citations: scripts/setup.sh:50 ("CLAUDE.md quirks", now ouroboros-stdio), scripts/jev.py:80
     (bridge stderr, now pc-bridge-lanes), scripts/hiccup_families.tsv's `CLAUDE.md:` rule labels (the test now finds
     their phrases in CLAUDE.md or the skills it names).
5. Pre-existing, not fixed: tests/test_hooks_worktree.py runs the REAL post-commit hook with the real PATH. Its
   `scripts/tool.py` commit launches the real graft, gitnexus, cbm and crg against a throwaway repo. That was all four
   commits at the PIN and is now one, and my one-line change keeps its log and locks out of /tmp. One such run by
   another lane at 13:23:50 wrote 4 lines into the real /tmp/post-commit-reindex.log before that change. The
   anti-hollow-green and deep-work frontmatters fail strict YAML at HEAD (`any project: ...`); my six skill
   frontmatters parse.
6. No drift test re-derives the four read-sets from the installed tools; a tool upgrade that adds a language needs the
   hook's set widened by hand (the hook header says so). The wiki live-state and the ledger are the coordinator's.

## 10. The brief's question: the five other files that name CLAUDE.md

- scripts/setup.sh: :13 (setup.sh is the toolchain source of truth, still said) and :97/:118 (the honey rules: the
  honey paragraph stayed) remain true; :50 "(CLAUDE.md quirks)" now reaches the Ouroboros quirk through a pointer.
- scripts/push_clean.sh:89: the "banner churn" hint is rarely needed now (no automatic rewrite); untouched, harmless.
- scripts/push_when_green.sh: its banner guard keys on the gitnexus start/end markers, which are unchanged; it still
  works and should seldom fire.
- .claude/hooks/graft-first-nag.py: :28 and :43 cite the code-intel section's "Project code lives under" and GRAFT
  FIRST. Both stayed in CLAUDE.md on purpose, so both citations hold.
- scripts/gn_mcp.py:14 "(see CLAUDE.md)": the GitNexus tier paragraph stayed, so it resolves. Its "native MCP first"
  already contradicted the 2026-09-07 CLI ruling before CTX1; that ruling now lives in code-intel-trio.

## 11. Self-attack (the three likeliest ways this is wrong)

1. A rule needed on most turns now sits behind a pointer that never loads; the coordinator measured 12 Skill loads.
   Ruled out as far as the brief allows: the every-turn rules the coordinator named are inline, and every pointer names
   its situation. Residual: loading depends on the planned router hook (not built).
2. A per-graph read-set misses a file a graph reads, so its index goes stale after such a commit. Ruled out: the sets
   are generated from each tool's source, not typed, and the tests pin the per-graph outcomes (.sh, .json,
   extension-less, Makefile, Rakefile, .C, .sha256, .txt/.tsv, merge). Residual: the cbm set comes from the vendored
   source, not the installed 0.10.8 binary; GitNexus File nodes for unparsed files, and the docs plane (Markdown,
   tasks/ probes), wait for the next re-indexing commit, which the contract accepts.
3. The losslessness check passes a lossy move, because a substring match over whole files can hit a short line by
   chance. Ruled out: 723 of 727 lines sit next to a PIN neighbor in the same file, and the 4 bare-only lines are
   listed and explained. Every found label is an intended destination. A negative control cuts a real moved line and is
   caught.

## 12. Evidence tiers

- Verified (this session, primary source or run): every count, size, hash, test result, red run and file list above;
  the read-sets (generated from sources); the analyze flag behavior (read in dist/cli/ai-context.js and analyze.js);
  the pin failures and the patch (mirror runs); the bake tail's output and exit code; the disk incident's timing.
- Inferred: the fast-jev-output files account for 2 of the 18 first-party count (listed by `git status --ignored`, not
  isolated by a run); Hermes and Codex read the new skills as the harness does.
- Assumed: the installed codebase-memory 0.10.8 reads the vendored table's extensions; `--skip-agents-md` exists in
  gitnexus 1.6.7 (not relied on: I left that recipe alone).
