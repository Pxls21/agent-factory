# LIB1: the library skills leave the skill listing and stay usable (task #288, D-091 item 1)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/LIB1-report.md` (write it
incrementally from the start). PIN: 37f720a (origin). Evidence: AF-AP-221 in `docs/INCIDENT-LOG.md`; the S1A audit
(`docs/research/findings/system1-context/AUDIT-2026-09-25.md`, section 1's skill class table and row D13); D-091 in
`docs/08_DECISION_LOG.md`.

## WHY

The harness lists skills in a 30,000-character budget, alphabetically, and 356 skills copied verbatim from the owner's
sandbox-kit come first: 72 of 485 listed skills carry a description, and project skills the rules tell the agent to load
(`session-continuity`, `code-intel-trio`) are bare names (AF-AP-221). The owner (D-091): move them out of `.claude/skills/`,
"so long as the skills are still usable, you don't lose the skills anywhere." Two facts shape the move (premise below):
the 356 are not all library code, since the project's own rules call some of them by name (`bug-echo`, `luck`,
`trace-the-chain`, the six `gitnexus-*` guides whose paths CLAUDE.md prints, and others), and every one of the 356 is also
mirrored under `.agents/skills/` for the Codex and Hermes ports.

## CONTRACT

1. **Classify.** Split the 356 kit-verbatim skills into KEPT (the project names the skill: CLAUDE.md, AGENTS.md,
   `.hermes.md`, the situation table, `.agents/lane-skills/`, `harness-ports/hand-ported.txt`, any skill that is not
   kit-verbatim, a hook, a script or a test) and MOVED (the rest). A word match is not a reference: `design`, `brand` and
   `compiler` are skill names and ordinary words. Decide each hit by how it is used (backticks, a `/name` command, a
   `Skill` call, a path, "skill `x`"), and list every KEPT skill with one citation (file:line) and every hit you ruled
   out with its reason. Anything you cannot decide stays KEPT and is listed for the coordinator.
2. **Move.** Each MOVED skill directory goes from `.claude/skills/<name>/` to `.claude/skill-library/<name>/` and its
   mirror from `.agents/skills/<name>/` to `.agents/skill-library/<name>/`, bytes unchanged (prove it: the sha256 of
   every moved file before and after). Nothing is deleted. KEPT skills do not move.
3. **Reach.** A new first-party skill `.claude/skills/skill-library/SKILL.md` (and its mirror) is the index: its
   description tells the model when to reach for it (a specialist skill the project does not use every day: name the
   families the library holds), and its body lists every moved skill on one line: the name, its description's first
   sentence cut to about 120 characters, and the path to Read. Group it so a reader can scan it. Prove the index is
   complete (each moved skill appears once, each path exists) with a test that fails when a library skill is added or
   removed without the index.
4. **The tools follow.** Every tool that assumes the old layout changes with it, and nothing else: at least
   `harness-ports/bin/sync-skills.sh` (the library is mirrored and drift-checked too), `scripts/vendored_manifest.py`
   (the moved files stay classed kit-verbatim against the kit index at their new paths; regenerate
   `sandbox-kit/VENDORED-MANIFEST.md` and `sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv` the documented way), and the readers
   the premise lists wherever they treat `.claude/skills/` as vendored (a prefix list that excludes vendored code from a
   screen or a compiler must now exclude `.claude/skill-library/` too). Say for each reader what you checked and why it
   needed a change or not.
5. **Measure the listing.** The harness reads skills once per session, so the listing itself changes only next session.
   Measure the proxy now and say how you computed it: before and after, the skills in `.claude/skills/` in alphabetical
   order with the running size of name plus description, and which project skills fall inside the 30,000-character
   budget.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. The classification table (item 1) and the move's byte proof (item 2).
3. Tests: the index test (item 3) with a negative control; `harness-ports/tests/test_sync_skills.sh`;
   `tests/test_vendored_manifest.py` run ONE TEST AT A TIME with a fresh `--basetemp` each (the whole file copies about
   3.4 GB and this disk has 1.4G; env-tool-quirks has the recipe); the tests of every reader you changed;
   `harness-ports/tests/run-all.sh`. Counts pasted from `scripts/test_summary.sh`, each set with its set id.
4. `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write; pyflakes rc 0 on changed Python.
5. NOT-done and DISCREPANCIES.

## BOUNDARY

MOVE: the MOVED skill directories (item 2). CREATE: `.claude/skill-library/`, `.agents/skill-library/`, the index skill and
its mirror, the index test, your report. MODIFY: `harness-ports/bin/sync-skills.sh` and its test,
`scripts/vendored_manifest.py`, `tests/test_vendored_manifest.py` (class pins only), the two regenerated `sandbox-kit/`
files, and the readers item 4 requires (list each in the report before you change it). NEVER: a KEPT skill, CLAUDE.md,
AGENTS.md, `.hermes.md`, the situation hook or its table (another lane will change the hook), anything under `proofs/`.
Other lanes are live in this tree; `.lanes-live` lists their paths: touch none of them.

## STANDING RULES

No git writes in this tree (the moves are plain file moves; the coordinator commits them); no PC bridge; no outward-facing
action. The disk is shared (1.4G free): a move costs no space, but a clean worktree for the manifest regeneration costs
about 190 MB, and each `test_vendored_manifest.py` test copies about 75 MB: delete each basetemp before the next. Scratch in
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/lib1/`, deleted as you go. Test counts pasted from
`scripts/test_summary.sh`; stamps from `date -u`. Long commands in one foreground call; kill by pid, never by name.

## PREMISE — MEASURED at authoring (2026-09-25 20:1xZ, /home/user/agent-factory; every file named is unchanged from the PIN)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf
37f720a SLOPO2 brief (task #285, D-091 item 5): a launcher that runs slopo with a pruning walker in 
$ awk the class table: SKILL.md files under skills/<name>/ by class (sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv)
      1 copy:sandbox-kit/council-of-high-intelligence/
     14 copy:sandbox-kit/honey-for-devs/
      6 first-party
      8 kit-adapted
    356 kit-verbatim
     22 vendored:aegis
      5 vendored:prism
      1 vendored:typesafe
$ ls .claude/skills | wc -l; ls -d .claude/skills/*/ | wc -l; ls .agents/skills | wc -l
417
413
413
$ the 356 kit-verbatim skill names that .agents/skills also holds
356
$ du -sc the 356 dirs (1 KiB blocks)
49668	total
$ for each of the 356: grep -l -w -F <name> CLAUDE.md AGENTS.md .hermes.md .claude/hooks/system1-situations.json <the 57 non-kit-verbatim SKILL.md files>   (a word match: common words are false positives the lane must sort out)
brand(2) bug-echo(6) compiler(3) credentials(8) design(30) empirical-validation(4) gitnexus-cli(2) gitnexus-debugging(2) gitnexus-exploring(2) gitnexus-guide(2) gitnexus-impact-analysis(2) gitnexus-refactoring(2) guidance(7) long-context(2) luck(5) performance(3) phoenix(1) premortem-roast(4) pymoo(1) redesign(3) root-cause-debugging(3) rwkv(2) thermo-nuclear-review(5) trace-the-chain(4) transformers(1) vendor-first(4) vllm(3) 
$ ls .agents/lane-skills   (the PC lanes' skill set, harness-ports/bin/sync-lane-skills.sh)
adversarial-review anti-hollow-green bug-echo build-loop code-intel-trio contract-gate deep-work empirical-validation gitnexus-cli gitnexus-debugging gitnexus-exploring gitnexus-guide gitnexus-impact-analysis gitnexus-refactoring honey honey-compress honey-review luck orchestration premortem-roast root-cause-debugging session-continuity thermo-nuclear-review trace-the-chain vendor-first
$ cat harness-ports/hand-ported.txt
adversarial-review anti-hollow-green bug-echo build-loop code-intel-trio contract-gate deep-work empirical-validation luck orchestration premortem-roast root-cause-debugging session-continuity thermo-nuclear-review trace-the-chain
$ the skills the situation table routes (.claude/hooks/system1-situations.json)
['anti-hollow-green', 'build-loop', 'code-intel-trio', 'contract-gate', 'deep-work', 'env-tool-quirks', 'orchestration', 'ouroboros-stdio', 'pc-bridge-lanes', 'session-continuity']
$ code and tests that name .claude/skills or .agents/skills
scripts/setup.sh scripts/lint_delta.py scripts/hiccup_scan.py scripts/skill_bake_finish.sh scripts/jev_context.py harness-ports/tests/test_sync_skills.sh harness-ports/bin/sync-lane-skills.sh harness-ports/bin/sync-skills.sh .claude/hooks/search-intercept.py .claude/hooks/system1-context.py .claude/hooks/turn-retro-gate.sh tests/test_hooks_worktree.py tests/test_system1_context.py tests/test_vendored_manifest.py tests/test_skill_bake_finish.py tests/test_search_intercept.py tests/test_codemap.py tests/test_claude_md_lossless.py tests/test_hiccup_scan.py tests/test_jev_context.py
$ grep -n -E 'gitnexus-[a-z-]+/SKILL.md' CLAUDE.md | head -3   (CLAUDE.md's GitNexus table points at paths)
491:| Understand architecture / "How does X work?" | `.claude/skills/gitnexus-exploring/SKILL.md` |
492:| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus-impact-analysis/SKILL.md` |
493:| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus-debugging/SKILL.md` |
$ df -h / | awk 'NR==2{print $4}'
1.4G
```

Two questions for you, not facts: (1) Do the Codex and Hermes ports read `.agents/skills/` as a listing too (so the move
helps them the same way), or only by path? (2) This session's harness listed the skills at its start; will a subagent
dispatched after the move see the old listing or the new one? Answer from what you can measure, and say which it is.
