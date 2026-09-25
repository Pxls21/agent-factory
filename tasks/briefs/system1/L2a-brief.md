# L2a: the code-map cache, its builder and its reader (D-090, design L2; the hook wiring is L2b, after S1-L1-R1)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/L2a-report.md` (write it
incrementally from the start). PIN: c3a00b7 (origin). Design: `docs/research/findings/system1-context/DESIGN-2026-09-25.md`
(L2). Evidence: `docs/research/findings/system1-context/AUDIT-2026-09-25.md` (one instrument call costs 0.2-4.8 s, so no hook
can run the instruments synchronously; they run after commits and the hook reads a cache).

## WHY

The owner (D-090): before the agent acts, System 1 feeds it the code map from the quartet and the other tools, without the
agent having to ask. The codebase-memory hook that was meant to do part of this returned nothing for a week, because every
call paid a 2.6 s start over a 2 s deadline (AF-AP-220). The layer's answer: build the map in the background after each code
commit, and let the hook read a cache in milliseconds. This lane builds the cache and the reader; the hook that injects from
it is L2b, after S1-L1-R1 lands (that lane holds `.claude/hooks/system1-context.py`).

## CONTRACT

1. **Build.** `python3 scripts/codemap.py build <file>...` writes one pack per code file under `.jev/codemap/`, recording the
   file's git blob sha at build time. A pack holds: the file's symbols with their line spans; per symbol, its callers (a
   count and up to a few `file:line` names) and GitNexus's risk; the tests that cover the file (code-review-graph); and the
   registry rows the file's lines match (`scripts/ap_screen.py`). Scope: the project-code prefixes (`scripts/`, `src/`,
   `proofs/`, `spikes/`, `harness-ports/`); Python first; say what the other languages get. A missing instrument is named in
   the pack as missing, never filled with a guess (the NO STUBS rule).
2. **Batch the expensive call.** GitNexus impact costs about 1.9 s per symbol and a bare name is ambiguous (measured below), so
   one call per symbol is too slow for a file of 40 functions. Measure a batched form (one Cypher query per file, or
   `impact --file`) against the per-symbol form, and choose by the per-file cost; report the table.
3. **Read.** `python3 scripts/codemap.py lookup <file> --line N` and a Python function the hook will call return the entry for
   the symbol that encloses line N, in milliseconds, with `stale` true when the working file's blob differs from the pack's,
   and at most 1,500 bytes of text (the hook adds a label and a pointer inside its 2,048-byte budget). No pack: a miss, said
   as a miss. Also a demo command that takes a recorded Edit payload (`file_path`, `old_string`) and prints what L2b would
   inject: the line range of `old_string`, the enclosing symbol, the entry.
4. **Refresh after a commit.** `scripts/hooks/post-commit` refreshes the packs of the changed code files, niced, one refresh
   at a time, never blocking the commit, one log line per commit. The refresh must read graphs re-indexed for that commit:
   today the hook starts each graph's re-index in the background under a per-graph lock (`$T/graft-build.lock`,
   `$T/gitnexus-analyze.lock`, `$T/crg-build.lock`), so a refresh started beside them can win the race and read the old
   graph. Solve the ordering and prove it with a test in which the re-index is slow. Measure whether callers in OTHER files
   go stale enough to widen the refresh set, and say what you chose.
5. **A full build** for a fresh container (`codemap.py build --all`): measure files, wall time and bytes; propose (do not
   add) the `setup.sh` line.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Tests: the pack's fields; lookup inside a function, a method, at module level and past the end; the stale flag after an
   edit; a miss; the byte cap; the post-commit rule (a docs-only commit refreshes nothing; a code commit refreshes its files
   after their re-index); an absent instrument named as absent; two builds of one file on one index giving identical packs
   apart from times; a negative control that reds for each on a broken copy.
3. The measurement table: per instrument and file, the batched choice, a typical commit's refresh, the full build, pack sizes,
   and lookup latency (p50 and p95 over 1,000 lookups).
4. `bash scripts/test_summary.sh` twice with the set id; pyflakes rc 0; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints
   0 for every file you write.
5. NOT-done and DISCREPANCIES.

## BOUNDARY

CREATE: `scripts/codemap.py`, `tests/test_codemap.py`, your report. MODIFY: `scripts/hooks/post-commit` (the refresh trigger
only). READ everything else. Other lanes are live in this tree: S1-L1-R1 (`.claude/hooks/system1-context.py`,
`.claude/hooks/system1-situations.json`, `tests/test_system1_context.py`, `scripts/install_session_hooks.py`,
`tests/test_session_hooks.py`) and SCRUB1 (`scripts/transcript_export.py`, `tests/test_transcript_export.py`, the Laya
dataset manifest): touch none of their files.

**LIVE-FILE RULE (AF-AP-222):** `scripts/hooks/post-commit` runs on every commit in this tree, the coordinator's included.
Write each new version in your scratch, `bash -n` it and test it in throwaway repositories there, then move it into place with
one `mv`; keep it valid bash at every moment. Keep the refresh niced, locked and in the background, so no commit waits on it.

## STANDING RULES

No git writes in this tree (throwaway repositories in your scratch are fine); no PC bridge; no outward-facing action. The disk
is shared (1.9G free): scratch under 150 MB in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/l2a/`,
deleted as you go; a short `--basetemp` there with its parent created first. The instruments' own indexes are shared: never
delete or rebuild them in the tree (build a scratch index if a test needs one). Test counts pasted from
`scripts/test_summary.sh`; stamps from `date -u`. Long commands in one foreground call; kill by pid, never by name.

## PREMISE — MEASURED at authoring (2026-09-25 18:2xZ)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf
c3a00b7 transcripts: scrubbed sandbox chat digests (2026-09-25)
$ timings on scripts/jev.py (the coordinator, one run each)
graft skeleton scripts/jev.py: rc=0 ms=501 bytes=2574
node .gitnexus/run.cjs impact rank --direction upstream --repo .: rc=0 ms=1946 bytes=2845 -> "status": "ambiguous", "Found 5 symbols matching rank" (disambiguate with -f/--file or -u/--uid)
/root/venv-crg/bin/code-review-graph query tests_for scripts/jev.py: rc=0 ms=298 bytes=417
python3 scripts/ap_screen.py scripts/jev.py: rc=0 ms=71 bytes=246
$ node .gitnexus/run.cjs --help | grep -E "impact|context|cypher"
  context [options] [name]                 360-degree view of a code symbol: callers, callees, processes
  impact [options] [target]                Blast radius analysis: what breaks if you change a symbol
  cypher [options] <query>                 Execute raw Cypher query against the knowledge graph
$ grep -n -E "flock -n 9|lock\" >/dev/null" scripts/hooks/post-commit   (the background re-index launchers)
123:      ) 9>"$T/graft-build.lock" >/dev/null 2>&1 & ;;
126:      ) 9>"$T/gitnexus-analyze.lock" >/dev/null 2>&1 & ;;
132:      ) 9>"$T/cbm-index.lock" >/dev/null 2>&1 & ;;
135:      ) 9>"$T/crg-build.lock" >/dev/null 2>&1 & ;;
$ git check-ignore -q .jev/codemap/x.json && echo ignored
ignored
$ ls scripts/codemap.py tests/test_codemap.py
'scripts/codemap.py': No such file or directory
'tests/test_codemap.py': No such file or directory
$ df -h / | awk "NR==2{print \$4}"
1.9G
```

A question for you, not a fact: GitNexus answers `impact` with risk `UNKNOWN` when it cannot resolve callers (dynamic calls,
plain-object attributes). What should the pack say for such a symbol so the agent reads it as "unresolved", never as "no
callers"?
