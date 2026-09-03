# BRIEF — curate the wiki from the newest transcripts (role: curator)
PIN: {PIN}

Boundary: `wiki/**` ONLY. No commits, no pushes, no subagents. First action: `pwd && git rev-parse HEAD` equals the PIN, tree clean.

Read, in this order: `wiki/CONTEXT.md` (how to use the wiki), `wiki/log.md` (find the last curation stamp: the newest line starting `curated:`), `todo/BUILD-TASKLIST.md` §0 and §2 (status truth), then every file under `transcripts/sandbox/` and `transcripts/pc/` whose name sorts after the stamp (all of them if there is no stamp), then `docs/INCIDENT-LOG.md` entries dated after the stamp.

Produce: (1) `wiki/topics/live-state.md` refreshed in its fixed six-section shape from the ledger and the transcripts (active lanes, in-flight runs, pending owner decisions, do-not-trust, clocks from `git log -1 --format='%h %cI'`); (2) topic articles updated ONLY where a transcript or incident records a decision, a defect, a NOT-built fact, or a renamed mechanism — cite the transcript file name in the article's Sources; (3) append to `wiki/log.md`: `curated: <UTC date> <PIN short> read=<comma-separated transcript file names>`; (4) a PROPOSALS list in your report (not in the wiki) for anything outside `wiki/`: skill lessons to bake (skill name + the sentence), registry rows, stale docs — each with file:line evidence.

Rules: the ledger wins over any transcript on status; never write a capability the sources do not prove; state NOT-built first-class; never a flat proof count; keep every existing link resolving (run the link check: `grep -rhoE '\]\([^)#]+' wiki | sed 's/](//' | sort -u | while read p; do [ -e "wiki/$p" ] || [ -e "$p" ] || echo "MISSING: $p"; done`). Report: files changed (one line each), the log line you appended, the proposals, the link check output, NOT-done.
