# L5: the chat bug locator, `scripts/chat_find.py` (D-090; design L5)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/L5-report.md` (write it
incrementally from the start). PIN: 2ff48df (origin). Design: `docs/research/findings/system1-context/DESIGN-2026-09-25.md`
(L5). Evidence: `docs/research/findings/system1-context/AUDIT-2026-09-25.md` section 5 (the ground truth for five registry rows,
and what each existing tool can and cannot answer) and its producers `first_seen.py` and `locator_trial.py` in the same folder.

## WHY

The owner (D-090): a tool to ask where a bug popped up in the chat. The audit (section 5): for 4 of 5 registry rows no existing
tool placed the bug's first appearance. `jev_locate.py` reads the code graphs, the registry and git, never the transcripts;
`hiccup_scan.py` gives error clusters per day and per agent; `chat_tail.py` reads one transcript at a time;
`replay_transcript_edits.py` gives one file's edits without dates. The registry and the wiki need the first appearance: when,
where, and in which tool call.

## CONTRACT

1. **One command:** `python3 scripts/chat_find.py "<description or error text>"`, with options for a time window, the number of
   hits, JSON output, and the order (below). It searches every transcript (the main and subagent JSONL files under the session
   transcript roots; reuse the discovery and streaming code of `scripts/hiccup_scan.py` by import, never a copy) and reports
   the FIRST appearance overall and per transcript: the time, the transcript (main or subagent, agent id), the record index,
   the record kind (a tool result error, a tool input, assistant text, user text, a hook or system record), and the tool call
   around it (tool name and call id).
2. **Matching.** An error string matches after the normalization `hiccup_scan.py` already applies (numbers, ids, paths); a
   description matches lexically (a ranked token overlap such as BM25, standard library only). `--order jev` reranks the
   lexical top candidates through the local Laya server the way `scripts/jev_context.py`'s `jev_rank` does (D-074: Jev stays
   model-based), and falls back to lexical order LOUDLY (one line saying so) when the server does not answer.
3. **No transcript text by default.** The default output is counts, ids, times and positions only: transcripts hold secrets.
   An explicit option prints a short excerpt that passes `transcript_export.scrub` first, capped the way `hiccup_scan.py`
   caps its excerpts.
4. **The oracle.** The audit's ground truth (section 5.1, from record shapes, by `first_seen.py`) for AF-AP-154, 181, 183, 201
   and 209. Give `chat_find.py` each row's symptom in the registry row's own words, and separately its literal error string
   where one exists. Report, per row and per mode (error string, description, description with `--order jev`): the rank of the
   true first appearance, or why it was not found. Add five negative queries (symptoms that never happened here) and report
   their false hits.
5. **Bounded.** One scan over all transcripts streams the JSONL in bounded memory. Report the wall time and peak memory. An
   index cache under `.jev/` is allowed if the transcript size and mtime invalidate it.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Tests on fixture transcripts built at run time (JSONL: a tool result error, a refusal stop, a model switch, a hook record,
   a subagent file, an unparsable line): every output field pinned; the default output never contains a fake secret string
   placed in a fixture; the Jev fallback path; two runs give identical output.
3. The oracle table of contract item 4, run on the real transcripts, counts and positions only.
4. `bash scripts/test_summary.sh` on your tests, twice, with the set id; pyflakes rc 0;
   `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
5. NOT-done and DISCREPANCIES.

## BOUNDARY

CREATE: `scripts/chat_find.py`, `tests/test_chat_find.py`, your report. READ everything else. Reuse by import; where a function
you need is private or entangled, import what you can and report the rest; never edit another script. Other lanes hold this
tree: INSTALL1 (`scripts/setup.sh`, `harness-ports/bin/pc-setup.sh`, `upstream.lock.yaml`, `scripts/hooks/post-commit`,
`.gitignore`, new slopo files) and VERIFY-S1-L1 (read-only): touch none of their files. Scratch:
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/l5/`.

## STANDING RULES

No git writes; no PC bridge; no outward-facing action. Transcripts hold secrets: print and store counts, ids, times and
positions only; never search transcripts for keys, tokens or passwords. Test secrets are fake strings built at run time. The
local Laya server is shared: a few rerank calls, never a restart. The disk is shared (2.0G free; INSTALL1 must keep 1 GB): keep
your scratch under 100 MB and delete it as you go.

## PREMISE — MEASURED at authoring (2026-09-25 16:3xZ)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf
2ff48df AF-AP-220 addendum: the codebase-memory Read hook is silent by design for a file the graph covers ("Po
$ git log --format=%h --grep='^S1-L1 landed' -n 1 origin/claude/soundbox-kit-migration-iz1jwf
6195b77
$ df -h / | awk 'NR==2{print $4}'
2.0G
$ ls docs/research/findings/system1-context/first_seen.py docs/research/findings/system1-context/locator_trial.py
docs/research/findings/system1-context/first_seen.py
docs/research/findings/system1-context/locator_trial.py
$ the ground truth (AUDIT section 5.1, first_seen.py; the first appearance of each row)
## AF-AP-154: 6 hits
  first: 2026-09-02T22:30:03.520Z | main | -home-user | bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl | 913 | refusal: claude-fable-5 -> claude-fable-5-1
## AF-AP-181: 1 hits
  first: 2026-09-24T10:49:55.013Z | main | -home-user | bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl | 113774 | tool_result
## AF-AP-183: 10 hits
  first: 2026-09-22T16:45:55.073Z | main | -home-user-agent-factory | bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl | 219 | hook_success:SessionStart stdout=42298 content=22
## AF-AP-201: 4 hits
  first: 2026-09-24T23:45:38.061Z | main | -home-user | bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl | 126517 | tool_result
## AF-AP-209: 4 hits
  first: 2026-09-25T06:03:40.206Z | subagent | -home-user | agent-a7c113e7a3e1d35cb.jsonl | 708 | tool_result
$ grep -n -E "^(ORDERS|DEFAULT_ORDER) =|^def jev_rank" scripts/jev_context.py
75:ORDERS = ("unranked", "lexical", "jev")
81:DEFAULT_ORDER = "lexical"
805:def jev_rank(query, chunks, instructions=None, url=None, timeout=JEV_TIMEOUT, log=True, protect=()):
$ grep -n -E "^DEFAULT_PROJECT_DIR|^def (cluster_key|excerpt|result_text|canon_ts)" scripts/hiccup_scan.py
51:DEFAULT_PROJECT_DIR = "/root/.claude/projects/-home-user"
87:def excerpt(text):
103:def cluster_key(text):
153:def canon_ts(ts):
171:def result_text(content):
$ grep -n "^def scrub" scripts/transcript_export.py
85:def scrub(text: str) -> str:
$ ls /root/.claude/projects/-home-user/*.jsonl | wc -l; ls /root/.claude/projects/-home-user/*/subagents/*.jsonl | wc -l
1
288
$ grep -n "^LOCAL_URL" scripts/jev.py; ps -o pid,cmd -p 5187 | tail -1
64:LOCAL_URL = "http://127.0.0.1:47411"
 5187 /root/venv-laya-probe/bin/python scripts/laya_systemone_server.py --threads 2 --device cpu
$ ls scripts/chat_find.py tests/test_chat_find.py
'scripts/chat_find.py': No such file or directory
'tests/test_chat_find.py': No such file or directory
$ ls /root/.claude/projects/; ls /root/.claude/projects/-home-user-agent-factory/*.jsonl | wc -l; ls /root/.claude/projects/-home-user-agent-factory/*/subagents/*.jsonl | wc -l
-home-user
-home-user-agent-factory
1
0
   <- AF-AP-183 first appears under -home-user-agent-factory, outside hiccup_scan.py DEFAULT_PROJECT_DIR: search both roots
```

A question for you, not a fact: the audit's ground truth keys on record SHAPES (a refusal stop, a hook record with a large
stdout). A text query finds words. For which of the five rows can a text query reach the shape at all, and what would a
`--shape` mode need?
