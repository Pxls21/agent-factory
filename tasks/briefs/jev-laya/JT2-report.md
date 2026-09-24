# JT2 report: the Jev bug locator and the Jev-assisted bug-echo (tasks #227, #229; D-072 item 4)

Lane: JT2 build (sandbox, Opus 5.5). PIN: local HEAD db71586 on claude/soundbox-kit-migration-iz1jwf (shared tree, no
worktree). Brief: `tasks/briefs/jev-laya/JT2-brief.md`. Status: BUILT, gates green, NOT committed (the lane commits nothing); the default order DECIDED by the coordinator as D-077: `lexical`, Jev opt-in (section 17). Written as the lane went; the worker restarted at about 14:49Z and the lane resumed at 14:51Z (section 10).

## 0. Premise re-measured (2026-09-24 13:09Z, db71586)

Verdict: the premise HOLDS. One measured difference changes a parameter, not the design (P-3 below). No STOP.

```
$ date -u; git log --oneline -1
Thu Sep 24 13:09:33 UTC 2026
db71586 briefs: JT2 (the Jev bug locator and Jev-assisted bug-echo, #227/#229), JT3 (...), MOJEV-G0-S (...); D-072
$ grep -n -E '^def (health|ask|rank|classify)\b' scripts/jev.py
446:def health(**opts):
450:def ask(state, instructions, qtype="noul", criteria=None, **opts):
454:def rank(query, chunks, instructions=RANK_INSTRUCTIONS, **opts):
458:def classify(state, labels, instructions=CLASSIFY_INSTRUCTIONS, **opts):
$ timeout 60 graft ask "who calls merged in install_session_hooks" --in scripts    (rc=0 ms=1661 bytes=201)
graft ask — "who calls merged in install_session_hooks"  (structural)
callers / references of merged
- main  scripts/install_session_hooks.py:L83-L126  (calls) — def main(argv: list[str]) -> int
$ grep -n -E 'graft|run.cjs|code-review-graph|ripwire' scripts/lane_context.sh   (lines 61, 68, 75, 81: as the premise)
```

| # | premise item | measured now | holds? |
|---|---|---|---|
| P-1 | jev.py API `health/ask/rank/classify` at 446/450/454/458 | identical lines | yes |
| P-2 | graft ask answers the sample question in ~2.7 s, 201 bytes | 1,661 ms, 201 bytes, same caller | yes |
| P-3 | 8 chunks ranked in 3.4 s on the local server | 8 chunks 10.83 s; **48 chunks 62.65 s** (box load average 12 on 4 cores, other lanes live) | yes, slower |
| P-4 | chunks go as a LIST of {id, text}, one noul per chunk | jev.py `_build` (rank) and `_result` refuse a reply whose fan_out != chunk count | yes |
| P-5 | instrument CLI shapes in lane_context.sh and the skill | read and probed live (below) | yes |

P-3 consequence (a parameter, flagged): jev.py's default timeout is 30 s (`DEFAULT_TIMEOUT`, jev.py:60). A 48-chunk rank
took 62.65 s, so the library passes an explicit Jev timeout (default 240 s, `--jev-timeout`). Without it every full
48-chunk call would fail open as unranked.

Instrument probes (live, this session; the exact shapes the parsers read):

| instrument | invocation (from lane_context.sh / code-intel-trio skill / the CLI's own --help) | measured |
|---|---|---|
| graft | `graft ask "<q>" [--in <path>]` | rc 0; two shapes: structural `- name  path:Lnn-Lmm  (calls) — sig` and lexical `N. name · kind` + `path:Lnn-Lmm` + signature |
| GitNexus query | `node .gitnexus/run.cjs query "<q>" --repo .` | rc 0, JSON `{processes, process_symbols, definitions[{filePath,startLine}]}`; 27.4 s cold, 8.0 s warm |
| GitNexus context | `node .gitnexus/run.cjs context <sym> --repo .` | rc 1 twice: `LadybugDB unavailable ... Another process may be rebuilding the index` (an analyze by pids 3268/4088, not this lane's) — the fail-open case, seen live. Result shape read from gitnexus dist `local-backend.js:3196-3530`: `{status:'found', symbol{filePath,startLine}, incoming{calls[{name,filePath,kind}]}}` or `{status:'ambiguous', candidates[{filePath,line}]}` or `{error}` |
| codebase-memory | `codebase-memory-mcp cli search_graph --project home-user-agent-factory --query "<q>"` | rc 0, 4.1 s; rows `qn label file a-b rank` |
| code-review-graph | `/root/venv-crg/bin/code-review-graph query callers_of <sym>` | rc 0, 0.5 s; a bare name gives `status: ambiguous` + candidates (fuzzy), a qualified `<abs path>::<name>` gives `status: ok` + results[{file_path,line_start}] |
| rg | `rg -n ... -- proofs spikes scripts src harness-ports tests` | /usr/bin/rg present |
| git pickaxe | `git log -S<tok> --oneline -5` | 0.4 s (recent match) to 17.1 s (full-history scan) |
| Jev | `jev.rank(q, chunks, venue="local")` on 127.0.0.1:47411 | health ok (cpu, revision 1c5edc17), rank as P-3 |

Two more measured facts that shape the design:

- **The Jev window.** `laya/common.py` `build_sequence` serializes the state as JSON (`{"query": ..., "chunk": ...}`,
  query first, the server's `_answer` at `scripts/laya_systemone_server.py:130-144`) and cuts the state from the RIGHT
  (`st[:room]`); `rl_agent_config.json` says `max_len` 1024, `head_max_len` 256. A long query (a 4,000-character trace)
  would push the chunk out of the window and every chunk would score the same: a silent hollow ranking. So the query
  sent to Jev is capped at its last 1,200 characters (`JEV_QUERY_CHARS`), pinned by a test.
- **The lint gate is blind to new files.** `scripts/lint_delta.py --base HEAD` lists files with
  `git diff --name-only HEAD` (lint_delta.py:73-80), which never names an untracked file, and every file of this lane is
  new. Staging them (`git add -N`) would touch the shared index, so the gate is run as the brief says AND the same
  pyflakes delta is run over this lane's files directly (section 6).

## 1. Design decisions (inside the pins; each a choice the brief left open)

| # | decision | why | rejected alternative |
|---|---|---|---|
| DD-1 | Jev is called with `venue="local"` (or `url=` in tests), never `auto` | `auto` falls back to the PC through the bridge (jev.py:363-364); this lane may make no bridge call (D-7) | `auto`: a bridge call whenever the local server is down |
| DD-2 | Jev timeout 240 s (`--jev-timeout`) | 48 chunks took 62.65 s under load; jev.py's 30 s default fails every full call | the 30 s default |
| DD-3 | the Jev query is the question's last 1,200 characters | the 1,024-token window above | the whole question (up to 4,000 characters) |
| DD-4 | each instrument has ONE 30 s budget shared by its calls; instruments run in parallel threads | D-1's "per-instrument timeout 30 s" read literally; the instrument phase stays near 30 s wall | 30 s per call (GitNexus query + 2 context calls could take 90 s) |
| DD-5 | a timed-out tool is killed with its whole process group | a grandchild holding the pipe would hang the read after a plain kill | `subprocess.run(timeout=)` |
| DD-6 | bare tool names resolve through the inherited PATH at call time; cbm and crg default to `$HOME/.local/bin/codebase-memory-mcp` and `$HOME/venv-crg/bin/code-review-graph`, resolved once | equals the brief's `/root/...` paths here and lane_context.sh:41's venue-neutral lookup; no `shutil.which` or PATH read (the AF-AP-115 screen) | the literal `/root/...` paths (then "PATH stripped" can never make them absent) |
| DD-7 | hits under vendored trees (`sandbox-kit/`, `graft/`, `.gitnexus/`, `.code-review-graph/`, `node_modules/`, `.claude/skills/`, `.agents/`) are dropped; `.claude/hooks/` is kept | GitNexus and cbm answers are dominated by `sandbox-kit/` (measured above; CLAUDE.md says the index is) | keeping them (they fill the top K) |
| DD-8 | record rows (registry rows, CLAUDE.md quirk segments, commits) never merge with each other and are not counted in "files to read" | two adjacent registry rows are two anti-patterns, not one site; summing 8 rows would put docs/INCIDENT-LOG.md first on every pack | D-2's merge applied to records too (**a deviation from D-2's letter, flagged**) |
| DD-9 | crg: a bare name that answers `ambiguous` is re-asked with the qualified names of the candidates whose name matches exactly (at most 2) | the skill: "Ambiguous names return a candidates list — re-run with the qualified_name"; lane_context.sh:78-81 | the bare name only (always ambiguous on this tree) |
| DD-10 | graft needs `graft/INDEX.md`, GitNexus `.gitnexus/run.cjs`, crg `.code-review-graph/graph.db`; else `unmapped` | lane_context.sh:75/77 and the skill's "check graft/INDEX.md exists before relying on it" | running them anyway (graft would build an index into the tree) |
| DD-11 | displayed text passes `transcript_export.scrub` first; without the scrubber, snippets are withheld | "never print a secret"; the same scrubber jev.py uses | printing raw repo lines |
| DD-12 | the pack holds no timing; wall time goes to one stderr line | D-4: deterministic for fixed inputs | a timing line in the pack |
| DD-13 | echo: the defect is the removed lines of hunks that remove code; the fix is the added lines of THOSE hunks | a fix commit also adds tests and screen rows that are not the fix | every added line of the commit |
| DD-14 | A3 input = the registry row's MECHANISM cell (the second cell), with the fixed files' paths, basenames and stems, the AF-AP id and commit ids removed | the first cell is the id (`AF-AP-1`), which holds no bug text; "the fix commit's own words removed" read as "no answer leak" (**an interpretation, flagged**) | the literal first cell; stripping every word of the fix commit's subject |
| DD-15 | a Jev ranking whose N>=2 scores are ALL equal is refused (`all N scores are equal (v): no signal ...`); the pack falls back to its base order with that reason | VERIFY-JT1 F-24 (a query over the window cuts every chunk, fan_out intact); the query bound prevents it for the text measured (section 10), this catches the rest | trusting `fan_out` alone (it cannot see the cut) |
| DD-16 | every tool output is split on `\n` only (`lines_of`), never `str.splitlines()` | JT3's finding in parse_rg (AF-AP-132's class): a form feed inside a matched line cut its snippet and could forge a hit | splitlines() |

## 2. The coordinator's 13:3xZ note (a mid-task course correction), and what changed

The note: J2 measured Jev's per-chunk noul ranking below random on a close cousin of this task (100 incident headings
against 184 registry rows: lexical overlap put the right row first 59%, Jev's rerank of the lexical top 16 5%). Three
rules followed, all adopted:

1. A3 reports Jev, unranked and lexical-only. Done: five columns (below), from ONE instrument pass and ONE Jev call.
2. The pack's DEFAULT order is whichever wins A3 on the committed case list; Jev stays behind `--order jev` if it loses.
   Done: `--order unranked|lexical|jev` on both tools; `jev_context.DEFAULT_ORDER` was first set by the A3 rule
   (section 4), then to `lexical` by the coordinator's D-077 (section 17).
3. A Jev score never DROPS an item the base order keeps within the budget (KC-J5): it may reorder, never replace. Done:
   `jev_context.select()` shows exactly the base order's top k items and top n files at every fit level and only
   reorders them; Jev scores the base's top 12 first, then the lexical pre-filter (at most 48). Pinned by
   `test_jev_reorders_the_base_selection_and_never_drops_an_item` (de-vacuoused: the pure order would drop the whole
   base top 5 there) and, at the command line, `test_jev_order_reorders_but_never_drops_the_base_selection` and
   `test_echo_jev_order_keeps_the_base_selection` (`--top 1`: the base's item, whatever Jev prefers).

Consequence for D-3's pure Jev order (`order_ranked`): it stays in the library as the MEASURE of Jev's signal (A3's
`jev` column), never as a pack order. A protected reorder of the 10 displayed files can still move a target into the top
5, so the `jev>unranked` and `jev>lexical` columns are not identical to their bases by construction.

## 3. A3 pre-registration: the case list, committed by digest BEFORE the run

```
$ python3 docs/research/findings/jev-locate-bench/bench.py select
cases.json: 20 cases of 50 eligible ids; sha256 2beba775ccad61b3e6131733352f37edaa8793bf77f1580f30358aba5c85960a
$ sha256sum docs/research/findings/jev-locate-bench/cases.json
2beba775ccad61b3e6131733352f37edaa8793bf77f1580f30358aba5c85960a  docs/research/findings/jev-locate-bench/cases.json
```

Written by 2026-09-24 13:52:10Z (`date -u` at this report append), before any `bench.py run`. The rule, the orderings, the metrics and the decision rule are in
`bench.py`'s docstring, fixed before the run:

- Cases: a commit in `git log db71586` naming exactly ONE AF-AP id, touching 1-2 production files (code under proofs/
  spikes/ scripts/ src/ harness-ports/, not a test or fixture) that exist at db71586, with a registry row at db71586;
  the earliest such commit per id; 20 of the 50 eligible ids, evenly spaced by id number.
- Input: the row's mechanism cell with every AF-AP id, commit id and target path/basename/stem removed (DD-14). Three
  cases lost a leak: AF-AP-70 (`AF-AP-30`), AF-AP-76 (`AF-AP-73`), AF-AP-148 (`scripts/no_laya_in_gates.py`).
- Metrics: recall@5 (targets in the top 5 files / targets), hit@5, MRR@10.
- Decision rule: the default is the highest mean recall@5 among {unranked, lexical, jev>unranked, jev>lexical}; ties by
  mean MRR@10; a remaining tie goes to the order that does not call Jev. The pure `jev` column is reported, never chosen.
- Caveat: the tree searched is HEAD plus the shared tree's uncommitted edits, where every fix is already in.

| id | commit | targets |
|---|---|---|
| AF-AP-1 | db72e4b | spikes/selective-egress/probe.sh |
| AF-AP-18 | a9498cb | scripts/validate-ledger |
| AF-AP-29 | 8b48bf7 | proofs/S0-11/check_eval_hardening.py |
| AF-AP-36 | ec93bd2 | proofs/S0-04/tools/pc/run_s0_04_legs.sh |
| AF-AP-38 | 1428c0b | proofs/S0-04/check_compression.py |
| AF-AP-47 | 66cd9ed | proofs/S0-05/check_egress.py |
| AF-AP-53 | 736bb94 | proofs/S0-01/tools/frame_tee.py |
| AF-AP-57 | b4257f8 | proofs/S0-01/tools/acp_probe.py |
| AF-AP-60 | c091de1 | proofs/S0-01/tools/scripted_backend.py |
| AF-AP-66 | 9c3944d | scripts/validate-ledger |
| AF-AP-70 | fe2dc3b | proofs/S0-01/tools/acp_probe.py |
| AF-AP-76 | 4313a3b | harness-ports/bin/build-roles.py |
| AF-AP-80 | 07c1312 | scripts/fubuki_pin_sync.sh |
| AF-AP-88 | f9fc2b1 | harness-ports/bin/qwen-matrix.sh, harness-ports/bin/qwen_matrix.py |
| AF-AP-90 | 2d21fd0 | harness-ports/bin/qwen_matrix.py |
| AF-AP-104 | d0d1ab2 | proofs/S0-03/check_omniroute_roundtrip.py, proofs/S0-03/tools/pc/collect_leg.sh |
| AF-AP-126 | 010d1bc | scripts/ci_gate.py, scripts/push_clean.sh |
| AF-AP-132 | ea18960 | scripts/ap_screen.py, scripts/report_lint.py |
| AF-AP-148 | 0e7b6c3 | scripts/no_laya_in_gates.py |
| AF-AP-164 | a81c034 | scripts/premise_block.sh |

## 4. A3 results (the run: 13:52Z-14:25Z, Jev answered 20 of 20 cases)

The case list's digest above was unchanged at the run's end (`sha256sum`: 2beba775...85960a). Raw rows:
`docs/research/findings/jev-locate-bench/results.jsonl`; table: `results.md` (both written by `bench.py`).

```
$ python3 docs/research/findings/jev-locate-bench/bench.py report      (results.md, Summary)
| order | cases | mean recall@5 | hit@5 | mean MRR@10 |
|---|---|---|---|---|
| unranked | 20 | 0.125 | 4 | 0.120 |
| lexical | 20 | 0.250 | 6 | 0.210 |
| jev | 20 | 0.200 | 5 | 0.119 |
| jev>unranked | 20 | 0.200 | 5 | 0.108 |
| jev>lexical | 20 | 0.300 | 7 | 0.122 |

Decision rule winner: **jev>lexical** (mean recall@5 0.300, MRR@10 0.122).
```

Recall at 5, Jev-ranked (`jev`, D-3 as pinned) against unranked (D-3's fallback): **0.200 vs 0.125** (5 vs 4 cases with a
target in the top 5); lexical-only 0.250 (6 cases).

Forensic pass (a scratch script over the saved chunks and scores; no new instrument or Jev call):

```
instrument ceiling (targets found anywhere, mean over cases): 0.575; cases with any target found: 13 of 20
MRR@10 wins/losses vs base: jev>lexical vs lexical: 1 up, 4 down, jev>unranked vs unranked: 2 up, 2 down, jev vs lexical: 1 up, 6 down
AF-AP-38 lexical top10: [..., 'proofs/S0-04/check_compression.py' at rank 6, ...]   jev>lexical: the same file at rank 5
target ranks, lexical -> jev>lexical: AF-AP-104 1->3, AF-AP-132 1->4, AF-AP-164 2->5, AF-AP-66 3->4, AF-AP-53 5->5, AF-AP-38 6->5
```

Reading (verified from the rows above; the interpretation is mine):

- **The decision rule picks jev>lexical, on ONE case.** Its recall@5 lead over lexical (7 vs 6 hits) is AF-AP-38 moving
  from rank 6 to rank 5, across the boundary. On the finer metric Jev HURTS: MRR@10 falls from 0.210 (lexical) to 0.122,
  and of the 5 cases where Jev changed a target's rank it moved 4 down. The pure Jev order moved 6 of 7 down. This agrees
  with J2's finding (Jev scores the chunk, not its fit to the query).
- **D-3's pinned fallback order (agreement first) is the weakest non-Jev order**: 0.125 vs lexical's 0.250. Instrument
  agreement favors generic sites that several instruments return for any question (cbm and graft on test functions).
- **The instruments bound everything**: in 7 of 20 cases no instrument returned the target file at all; the best any
  order could reach is 0.575. The inputs are anti-pattern CLASS descriptions, not bug reports; a trace or a failing
  test names far more (A1).
- n = 20: none of the differences between the orders is statistically meaningful. The 5-point recall gaps are 1-2 cases.

**Superseded by D-077 (section 17): the default is now `lexical`.** The paragraph below is the record of what the
rule set at the time. The default, set by the pre-registered rule and NOT changed after seeing the data: `DEFAULT_ORDER = "jev"` with
`JEV_BASE = "lexical"` (Jev reorders the lexical order's selection and never drops from it, KC-J5). When Jev does not
answer, the pack falls back to that base, lexical, with the `Jev unavailable: <reason> (unranked)` line. **Two flags for
the coordinator's decision (DECIDED since: D-077, section 17):** (1) the rule's winner rests on one boundary case while MRR says Jev degrades the
ranking, and every Jev pack costs 36-165 s on this box (the `jev_s` column of results.jsonl) against 5-28 s for the
instruments; `--order lexical` gives 0.250 / MRR 0.210 with no Jev call. My recommendation: make `lexical` the default and
keep `--order jev` behind the flag; I did not, because the rule was fixed before the run. (2) The Jev-down fallback is now
lexical, not D-3's agreement-first order: a deviation from D-3's letter, forced by making the base the better non-Jev order
(rule 2 of the note); D-3's order stays available as `--order unranked`.

## 5. A1: jev_locate live on three real questions (the default then: jev over the lexical base; 14:28Z-14:40Z)

Each run: the real instruments on the shared tree, the local Jev server (127.0.0.1:47411) through jev.py. The wall
time is the tool's own stderr line. A lexical run of the same question follows each for comparison (no Jev call).

**Q1, an error line from docs/INCIDENT-LOG.md (AF-AP-113's second instance).**

```
$ python3 scripts/jev_locate.py "python3: can't open file '//scripts/pc_bridge_exec.py': [Errno 2] No such file or directory"
jev_locate: 88 hits, 76 chunks, 48 ranked by Jev, 7 of 8 instruments answered, wall 43.1 s
ranking: Jev reorders the lexical order's selection (KC-J5: it never drops an item); 48 of 76 chunks scored, one noul each
answered: graft, gitnexus, cbm, rg, registry, quirks, git-log
1. 0.548 graft scripts/pc_bridge_exec.py — 1. pc_bridge_exec.py · file [symbol] scripts/pc_bridge_exec.py
2. 0.503 rg harness-ports/tests/test_pc_bridge_exec.py:13 — HELPER = ROOT / "scripts" / "pc_bridge_exec.py"
3. 0.463 rg scripts/pc_lane.sh:163 — # The envelope unwrapping lives in scripts/pc_bridge_exec.py (tested by | # harness-ports/tests/test_pc_bridge_exec.py). Bit 2026-0
4. 0.423 registry docs/INCIDENT-LOG.md:478 — | AF-AP-15 | a transport reply cap silently truncates a payload and the received TAIL looks like a valid file | any bridge 
5. 0.416 rg harness-ports/tests/test_bridge_token_handling.py:1 — """The bridge token never reaches argv or the filesystem: scripts/pc_bridge_exec.py hands it to | proo
... files to read:
1. scripts/pc_bridge_exec.py:0 — sum 1.745 (4 chunks: cbm, graft, rg)
2. harness-ports/tests/test_pc_bridge_exec.py:1 — sum 1.539 (5 chunks: cbm, rg)
3. scripts/no_laya_in_gates.py:115 — sum 1.433 (6 chunks: cbm, gitnexus, graft)
4. tests/test_jev_context.py:125 — sum 0.810 (4 chunks: gitnexus, rg)
5. harness-ports/tests/test_bridge_token_handling.py:1 — sum 0.784 (2 chunks: gitnexus, rg)
--- the same question, --order lexical:
jev_locate: 88 hits, 76 chunks, 0 ranked by Jev, 7 of 8 instruments answered, wall 8.5 s
1. a1 l4 quirks CLAUDE.md:423 — hermes <role>` with the bridge env exported first — NEVER from a manual copy with `P
2. a1 l4 rg scripts/pc_fetch.sh:18 — bridge() { python3 "$ROOT/scripts/pc_bridge_exec.py" "$1"; }
3. a1 l4 rg scripts/pc_lane.sh:163 — # The envelope unwrapping lives in scripts/pc_bridge_exec.py (tested by | # harne
4. a1 l3 registry docs/INCIDENT-LOG.md:478 — | AF-AP-15 | a transport reply cap silently truncates a payload and the r
5. a1 l3 git-log commit 764e516 — 764e516 jev: JT1 lands - scripts/jev.py, scripts/jev_local.sh, scripts/hiccup_scan.p
```

Reading: the cause is `scripts/pc_lane.sh:163` (`python3 "$ROOT/scripts/pc_bridge_exec.py"` with ROOT=/ after the
self-copy re-exec) and the record that names this exact error is the quirk at `CLAUDE.md:423`. Both are in the pack.
Lexical puts the quirk at 1 and pc_lane.sh:163 at 3 in 8.5 s; Jev moved the quirk from 1 to 9 and took 43.1 s. Items 6-12 of the Jev pack:

```
6. 0.411 git-log commit f601035 — f601035 findings: the Jev leverage re-audit (task #221) - evidence and synthesis; the task DB holds open tasks onl
7. 0.391 rg scripts/pc_fetch.sh:18 — bridge() { python3 "$ROOT/scripts/pc_bridge_exec.py" "$1"; }
8. 0.368 gitnexus+rg harness-ports/tests/test_bridge_token_handling.py:9 — Variable SRC | SRC = (ROOT / "scripts" / "pc_bridge_exec.py").read_text()
9. 0.357 quirks CLAUDE.md:423 — hermes <role>` with the bridge env exported first — NEVER from a manual copy with `PC_LANE_ORIG` set: the self-cop
10. 0.322 rg scripts/jev.py:348 — raise Unavailable("scripts/pc_bridge_exec.py did not import")
11. 0.305 git-log commit 764e516 — 764e516 jev: JT1 lands - scripts/jev.py, scripts/jev_local.sh, scripts/hiccup_scan.py and docs/HICCUPS.md (task #
12. 0.271 rg harness-ports/tests/test_pc_bridge_exec.py:1 — """scripts/pc_bridge_exec.py unwraps the bridge envelope: remote stdout -> stdout, remot
```

**Q2, a failing test's output (the long-basetemp gpg failure, CLAUDE.md's tests/test_proof_status.py quirk).**

```
$ python3 scripts/jev_locate.py --from-file q2.txt    # q2.txt:
FAILED tests/test_proof_status.py::test_anchor_without_the_committed_owner_key_is_refused - subprocess.CalledProcessError: Command '['gpg', '--batch', '--quick-generate-key', 'owner <owner@example.inv
jev_locate: 127 hits, 104 chunks, 48 ranked by Jev, 8 of 8 instruments answered, wall 146.1 s
ranking: Jev reorders the lexical order's selection (KC-J5: it never drops an item); 48 of 104 chunks scored, one noul each
answered: graft, gitnexus, cbm, crg, rg, registry, quirks, git-log
1. 0.553 cbm tests/test_proof_status.py:338 — Function tests.test_proof_status.<opaque-redacted>
2. 0.541 cbm tests/test_proof_status.py:298 — Function tests.test_proof_status.<opaque-redacted>
3. 0.529 git-log commit ec8ce8f — ec8ce8f CLAUDE.md quirk: tests/test_proof_status.py needs a SHORT --basetemp (the scratchpad path exceeds gpg-agent's Unix-socket leng
4. 0.503 rg tests/test_proof_status.py:255 — ["gpg", "--batch", "--quiet", "--pinentry-mode", "loopback", "--passphrase", "", | "--quick-generate-key", f"{name} <{name}
5. 0.496 rg tests/test_governance_review.py:56 — ["gpg", "--batch", "--quiet", "--pinentry-mode", "loopback", "--passphrase", "", | "--quick-generate-key", f"{name} <{n
... files to read:
1. tests/test_proof_status.py:255 — sum 4.123 (29 chunks: cbm, gitnexus, graft, rg)
2. tests/test_governance_review.py:56 — sum 1.649 (8 chunks: cbm, gitnexus, graft, rg)
3. tests/test_verify_command.py:159 — sum 1.609 (6 chunks: cbm)
4. scripts/check-proof-status.py:149 — sum 1.567 (4 chunks: gitnexus, graft, rg)
5. tests/test_ci_gate.py:55 — sum 1.077 (3 chunks: rg)
## unmapped and not run
- unmapped — gitnexus context CalledProcessError unavailable (rc 1: "error": "Symbol 'CalledProcessError' not found")
--- the same question, --order lexical:
jev_locate: 127 hits, 104 chunks, 0 ranked by Jev, 8 of 8 instruments answered, wall 17.0 s
1. a1 l11 rg tests/test_proof_status.py:255 — ["gpg", "--batch", "--quiet", "--pinentry-mode", "loopback", "--passphra
2. a1 l9 rg tests/test_governance_review.py:56 — ["gpg", "--batch", "--quiet", "--pinentry-mode", "loopback", "--passp
3. a1 l8 git-log commit ec8ce8f — ec8ce8f CLAUDE.md quirk: tests/test_proof_status.py needs a SHORT --basetemp (the sc
4. a2 l8 gitnexus+rg tests/test_jev_context.py:293 — Variable TRACE | tests/test_proof_status.py:192: FileNotFoundErro
5. a4 l8 cbm+gitnexus+graft+rg tests/test_proof_status.py:348 — Function tests.test_proof_status.<opaque-redacted> | F
```

Reading: the answer is the commit that added the quirk (ec8ce8f, "tests/test_proof_status.py needs a SHORT
--basetemp"): rank 3 in both orders, found by git log -S. The quirk line itself carries no `bit 2026-` marker, so the
quirks instrument cannot see it (a limit of D-1's marker rule). The unmapped line above (gitnexus context of a class
name the index lacks, rc 1) was a mislabel: an answer, not an outage. Fixed after this run in `inst_gitnexus` and
pinned by `test_gitnexus_context_not_found_is_an_answer_but_a_lock_is_unmapped`.

**Q3, a "where is X decided" question.**

```
$ python3 scripts/jev_locate.py "where does push_clean decide to refuse a push while the branch's last CI run is red"
jev_locate: 104 hits, 95 chunks, 48 ranked by Jev, 8 of 8 instruments answered, wall 50.8 s
ranking: Jev reorders the lexical order's selection (KC-J5: it never drops an item); 48 of 95 chunks scored, one noul each
answered: graft, gitnexus, cbm, crg, rg, registry, quirks, git-log
1. 0.576 registry docs/INCIDENT-LOG.md:650 — | AF-AP-187 | STATE KEYED BY A COMMIT SHA ACROSS A HISTORY REWRITE — the retro gate's acked sentinel held a short SHA; `p
2. 0.566 git-log commit 855370a — 855370a hooks: the retro gate maps its acked commit to the rewritten twin after push_clean (same tree, same subject), so a push no lon
3. 0.519 quirks CLAUDE.md:420 — push_clean REWRITES the unpushed range, so a lane brief's `PIN:` is the POST-PUSH SHA — read it from `git log origin/<branch>` AFTER t
4. 0.507 cbm tests/test_ci_gate.py:759 — Function tests.test_ci_gate.<opaque-redacted>
5. 0.503 cbm tests/test_ci_gate.py:785 — Function tests.test_ci_gate.<opaque-redacted>
... files to read:
1. tests/test_ci_gate.py:180 — sum 9.659 (28 chunks: cbm, gitnexus, rg)
2. scripts/push_clean.sh:2 — sum 1.183 (3 chunks: rg)
3. scripts/hooks/pre-push:18 — sum 0.903 (2 chunks: rg)
4. scripts/ci_gate.py:6 — sum 0.500 (4 chunks: gitnexus, graft, rg)
5. scripts/premise_block.sh:5 — sum 0.485 (1 chunk: rg)
```

Reading: the decision lives in `scripts/ci_gate.py` (the verdict) called from `scripts/push_clean.sh` (the refusal):
files 2 and 4 of the list; the top items are neighbours (AF-AP-187 is about push_clean's rewrite, not its CI gate).

## 6. A2: fail-open, live (14:4xZ)

PATH names an EMPTY directory and HOME an empty one (`env -i PATH=<empty dir> HOME=<empty dir>`): an empty PATH
string would search the current directory, and no PATH at all falls back to os.defpath (/bin:/usr/bin, where git and
rg live), so neither is "stripped" (both measured while writing the A2 test). Jev down = a closed loopback port pinned
with --jev-url (the real server is never stopped).

```
# (1) the real repo, every tool stripped, --order lexical: the six subprocess instruments are unmapped by name; the
#     two in-process record readers (registry, quirks) still answer, as they need no binary
jev_locate: 13 hits, 13 chunks, 0 ranked by Jev, 2 of 8 instruments answered, wall 0.1 s
ranking: lexical order (lexical overlap), Jev not asked
answered: registry, quirks
## unmapped and not run
- unmapped — graft unavailable (not found: graft)
- unmapped — gitnexus query unavailable (not found: node)
- unmapped — gitnexus context open_socket unavailable (not found: node)
- unmapped — codebase-memory unavailable (not found: codebase-memory-mcp)
- unmapped — code-review-graph callers_of open_socket unavailable (not found: code-review-graph)
- unmapped — rg -F open_socket unavailable (not found: rg)
- unmapped — rg -F OSError unavailable (not found: rg)
- unmapped — git-log -Sopen_socket unavailable (not found: git)
- unmapped — git-log -SOSError unavailable (not found: git)
# (2) an empty root, every tool stripped, --order jev with a closed port: rc 0, a pack of unmapped lines only
rc=0 chars=837
jev_locate: 0 hits, 0 chunks, 0 ranked by Jev, 0 of 8 instruments answered, wall 0.0 s
# jev locate
question: open_socket fails with OSError when the socket path is too long
Jev not asked: no chunks to rank (unranked)
answered: none
## top 0 of 0 (score, instruments, where, snippet)
## files to read (0 of 0)
## unmapped and not run
- unmapped — graft unavailable (graft/INDEX.md absent)
- unmapped — gitnexus unavailable (.gitnexus/run.cjs absent)
- unmapped — codebase-memory unavailable (not found: codebase-memory-mcp)
- unmapped — code-review-graph unavailable (.code-review-graph/graph.db absent)
- unmapped — rg unavailable (no code directory under the root)
- unmapped — registry unavailable (docs/INCIDENT-LOG.md absent)
- unmapped — quirks unavailable (CLAUDE.md absent)
- unmapped — git-log -Sopen_socket unavailable (not found: git)
- unmapped — git-log -SOSError unavailable (not found: git)
# (3) Jev down on the real repo and instruments (--order jev --jev-url http://127.0.0.1:41159, closed): the base order
jev_locate: 182 hits, 154 chunks, 0 ranked by Jev, 8 of 8 instruments answered, wall 10.6 s
Jev unavailable: call 1 of 6: url: connection refused (unranked)
answered: graft, gitnexus, cbm, crg, rg, registry, quirks, git-log
1. a2 l7 gitnexus+rg tests/test_jev_locate_echo.py:122 — Variable QUESTION | QUESTION = "open_socket fails with OSErro
2. a2 l5 gitnexus+rg tests/test_jev_locate_echo.py:115 — Variable LOCATE_FILES | "scripts/net.py": "def open_socket(pa
3. a1 l4 registry docs/INCIDENT-LOG.md:546 — | AF-AP-82 | a FIXTURE that fails BEFORE the instrument — a test's setu
```

Tests: `test_every_instrument_absent_is_a_pack_of_unmapped_lines_and_exit_0` (a root WITH every index marker, so each
instrument fails for its missing binary alone: the exact eleven lines), `test_jev_down_gives_the_unranked_pack_with_its_reason`
(the same items as `--order lexical`), `test_jev_down_is_a_reason_not_an_exception`, `test_a_failed_batch_fails_the_whole_ranking`.

## 7. A4: jev_echo on two real fix commits (14:4xZ-14:5xZ; the default then: jev over the lexical base)

**de06db6, the AF-AP-181 race fix** (`python3 scripts/jev_echo.py --diff de06db6`):

```
jev_echo: 18 removed lines, 120 candidate sites, 48 ranked by Jev, wall 284.6 s
ranking: Jev reorders the lexical order's selection (KC-J5: it never drops an item); 48 of 120 candidate sites scored, one noul each; question: Does this code show the same defect as the one fixed?
answered: rg-token, rg-shape, graft
fixed site: tests/test_s0_01_frame_tee.py:2999-3008, tests/test_s0_01_frame_tee.py:3340-3349
## top 10 of 120 (score, instruments, where, snippet)
1. 0.604 rg-shape+rg-token tests/test_jev_locate_echo.py:280 — def state_{n}(pid): if os.path.exists("/proc/%d/stat" % pid): try: fields = open("/proc/%d/stat" % pid).read().split() return fields[2]
1. 0.604 rg-shape+rg-token tests/test_jev_locate_echo.py:280 — def state_{n}(pid): if os.path.exists("/proc/%d/stat" % pid): try: fields = open("/proc/%d/stat" % pid).read()
2. 0.593 rg-token tests/test_s0_01_frame_tee.py:3326 — # Confirm agent is alive (AF-AP-45: check /proc/stat state, not just path) stat_path = "/proc/%d/stat" % agent_pid ass
3. 0.589 rg-shape+rg-token tests/test_s0_01_frame_tee.py:159 — if "time.sleep" not in cmdline: # Empty cmdline on a zombie = our grandchild, already dead try: st = open("/pr
4. 0.586 rg-shape+rg-token tests/test_s0_01_frame_tee.py:175 — deadline_gc = time.monotonic() + 2 while time.monotonic() < deadline_gc: try: st = open("/proc/%d/stat" % gc_p
5. 0.580 rg-token tests/test_jev_locate_echo.py:293 — def state_a(pid): try: with open("/proc/%d/stat" % pid) as fh: return fh.read().split()[2] except OSError: return "gone
6. 0.562 rg-shape+rg-token tests/test_edit_snapshot_ap_screen.py:273 — def <opaque-redacted>(self): # VERIFY-B5e F15: the state-aware form (exists on /proc/<pid>/stat, field
7. 0.553 rg-token tests/test_jev_context.py:533 — def _proc_state(pid): """One read (AF-AP-181's fixed form): the state letter, or "gone".""" try: with open("/proc/%d/stat" 
8. 0.545 rg-token scripts/mojev_probe.py:285 — try: lines = (Path(pin) / rel).read_text(encoding="utf-8").split("\n") # not splitlines(): AF-AP-132 found = lines[line - 1].s
9. 0.538 rg-token tests/test_jev_client.py:547 — def _alive(pid): try: with open("/proc/%d/stat" % pid) as fh: return fh.read().rsplit(")", 1)[1].split()[0] != "Z" except OS
10. 0.499 rg-shape tests/test_s0_01_frame_tee.py:183 — time.sleep(0.1) gone = True try: st = open("/proc/%d/stat" % gc_pid).read().split() if len(st) >= 3 and st[2] != "Z": 
--- the same, --order unranked:
jev_echo: 18 removed lines, 120 candidate sites, 0 ranked by Jev, wall 1.9 s
1. a2 l14 rg-shape+rg-token tests/test_jev_locate_echo.py:280 — def state_{n}(pid): if os.path.exists("/proc
2. a2 l12 rg-shape+rg-token tests/test_s0_01_frame_tee.py:159 — if "time.sleep" not in cmdline: # Empty cmdl
3. a2 l11 rg-shape+rg-token tests/test_s0_01_frame_tee.py:175 — deadline_gc = time.monotonic() + 2 while tim
4. a2 l10 rg-shape+rg-token tests/test_edit_snapshot_ap_screen.py:273 — def <opaque-redacted>(self): # VERIF
5. a2 l8 rg-shape+rg-token tests/test_jev_locate_echo.py:344 — assert echo_sites(out) == ["scripts/b.py:5"] 
6. a1 l15 rg-token tests/test_s0_01_frame_tee.py:3326 — # Confirm agent is alive (AF-AP-45: check /proc/stat
7. a1 l13 rg-token tests/test_jev_locate_echo.py:293 — def state_a(pid): try: with open("/proc/%d/stat" % pi
8. a1 l11 rg-token tests/test_jev_context.py:533 — def _proc_state(pid): """One read (AF-AP-181's fixed form
9. a1 l11 rg-shape tests/test_s0_01_frame_tee.py:183 — time.sleep(0.1) gone = True try: st = open("/proc/%d/
10. a1 l9 rg-token scripts/mojev_probe.py:285 — try: lines = (Path(pin) / rel).read_text(encoding="utf-8").s
```

My reading (the BUG/WATCH/OK call the tool leaves to the model), against AF-AP-181's shape (a fallback its own assert
rejects), after reading each site in the file:

| rank | site | call | why |
|---|---|---|---|
| 1 | tests/test_jev_locate_echo.py:280 | OK (planted) | THIS lane's echo fixture: the defect as a string template the test writes into a fixture repo. A true textual echo, not live code: the shared tree now holds this lane's files |
| 2 | tests/test_s0_01_frame_tee.py:3326 | WATCH | `assert os.path.exists(stat_path)` then `open(stat_path)` on an agent expected ALIVE: the same exists-then-read race, but no fallback; an agent reaped in that window fails with FileNotFoundError instead of "agent not alive" (a misleading failure, not a false pass) |
| 3 | tests/test_s0_01_frame_tee.py:159 | OK | the fixed form: `except ...: st = "gone"` and `assert st in ("Z", "gone")` accepts the fallback |
| 4 | tests/test_s0_01_frame_tee.py:175 | OK | a polling loop that breaks on the exception; the final check at :183 keeps `gone = True` on the exception |
| 5 | tests/test_jev_locate_echo.py:293 | OK (planted) | this lane's fixture of the FIXED form |
| 6 | tests/test_edit_snapshot_ap_screen.py:273 | OK | a screen test's string literal (the state-aware form must not fire) |
| 7 | tests/test_jev_context.py:533 | OK | this lane's one-read helper (the fixed form) |
| 8 | scripts/mojev_probe.py:285 | OK | unrelated (`read_text().split`) |
| 9 | tests/test_jev_client.py:547 | OK | one read, `except OSError: return False` |
| 10 | tests/test_s0_01_frame_tee.py:183 | OK | `gone = True` stays on the exception: the fallback is accepted |

True echoes of AF-AP-181 in live code: none found (the fix commit caught both instances); one WATCH (rank 2).
Jev's order and the unranked order hold the same sites; Jev took 284.6 s for it, the unranked order 1.9 s.

**The AF-AP-184 guard** (40543ab's guard hunk only: `git show --format= 40543ab -- scripts/install_session_hooks.py`
kept to the hunk `@@ -32,17 +33,26 @@`; the file's other three hunks are F-L1-1 and F-L1-5, not AF-AP-184;
the patch file sha256 d83d0032f143ea26b3db69aff2a6d0f21e82ec6364299469f4b5284f552adf08):

```
jev_echo: 9 removed lines, 3 candidate sites, 3 ranked by Jev, wall 13.1 s
ranking: Jev reorders the lexical order's selection (KC-J5: it never drops an item); 3 of 3 candidate sites scored, one noul each; question: Does this code show the same defect as the one fixed?
answered: rg-token, graft
fixed site: scripts/install_session_hooks.py:33-58
## top 3 of 3 (score, instruments, where, snippet)
1. 0.509 graft scripts/jev_context.py:157 — _KIND_RANK = {"quoted": 0, "ident": 1, "error": 2, "flag": 3, "fileref": 4, "word": 5} def _code_like(ident): body = ident.strip("_") return len(ident) >=
1. 0.509 graft scripts/jev_context.py:157 — _KIND_RANK = {"quoted": 0, "ident": 1, "error": 2, "flag": 3, "fileref": 4, "word": 5} def _code_like(ident): body = ident.strip(
2. 0.507 graft scripts/hook_context.py — 4. hook_context.py · file [symbol] scripts/hook_context.py
3. 0.501 graft scripts/verify_command.py:178 — return bare def is_verify( command: str, patterns: Optional[List[str]] = None ) -> bool: """Whether *command* is a test/build/
## unmapped and not run
- not run — rg-shape: no removed line keeps 2 or more API names
echo tokens: [the six removed f-string literals, e.g. '"{cd}python3 {r}/.claude/hooks/wiki-context.py"', '"cd {r} && "']; shapes: []
```

My reading: none of the three is an echo (graft's lexical neighbours of the snippet). The tool MISSED the real
candidates. A manual sweep (`rg` for hook commands built as `python3 <helper>` / `cd ... && python3`) finds
`harness-ports/bin/lane-profile.sh:65,68,154,158,216,220,240,244`: Hermes lane-profile hooks registered as
`python3 {helper} record|gate` with no existence guard. **WATCH** (not verified): whether they bite depends on how
Hermes treats a hook's exit 2 (python's can't-open code); an adjacent finding for the coordinator, outside this
boundary. Why the tool missed them: the defect is a MISSING guard written in site-specific string literals, so the
removed-only tokens exist nowhere else and no removed line keeps two API names for a shape (NOT-done item 3, section 12).

## 8. A5: budget and size

- `render()` tries shorter snippets, then fewer items and files; a markdown pack that still does not fit is cut with
  a marker line, a JSON pack falls back to its skeleton; `clamp_budget()` clamps any request over 9,000 (with a note
  line in the pack) and the CLIs refuse a budget under 1,000 (rc 64).
- `test_a_pack_never_exceeds_its_budget_or_the_hard_cap[False|True]`: 5,000 hits of 400-character texts on 80-character
  directory paths, 12 notes of 300 characters, a 4,000-character question, a 900-character extra line; markdown AND
  JSON at budgets 1,000 / 1,500 / 3,000 / 6,000 / 9,000 (the clamped 50,000) all fit, and every JSON pack parses.
  De-vacuoused: the uncut first layout is itself over 9,000 characters (`_md(pack, 240, 48, 10)`).
- `test_oversized_output_stays_under_the_hard_cap` (the command line): 40 files x 60 matching lines; `--budget 99999`
  gives a pack of at most 9,000 characters with the clamp note; the default gives at most 6,000; de-vacuoused: the
  capped pack is over 6,000, so the default one was cut.
- A defect in my own first version of both fixtures, found by A6: their "oversized" texts were 300-400-character
  runs of one letter, which the scrubber collapses to `<opaque-redacted>`, so the command-line pack was never cut
  and mutant M3 survived that test. Both fixtures now use spaced words (the kill table below is the rerun).

## 9. A6: mutants on scratch copies (`$SCRATCH/mutants.py`: a fresh copy of the 12 files per mutant, the anchor
asserted unique, the mutated module compiled, pytest must end rc 1 with no collection error, AF-AP-78)

```
baseline (unmutated scratch copy): rc=0 65 passed in 9.63s
M1 drop the ranking: rc=1 5 failed, 60 passed in 9.92s
   expected red: ['test_the_pure_jev_order_follows_the_scores', 'test_the_reorder_inside_the_selection_follows_the_scores', 'test_jev_order_reorders_but_never_drops_the_base_selection', 'test_echo_jev_order_keeps_the_base_selection']
   all red: ['test_echo_jev_order_keeps_the_base_selection', 'test_jev_order_reorders_but_never_drops_the_base_selection', 'test_jev_reorders_the_base_selection_and_never_drops_an_item', 'test_the_pure_jev_order_follows_the_scores', 'test_the_reorder_inside_the_selection_follows_the_scores']
   KILLED=True
   bench.py rescore under M1 (the saved rows, the mutated library):
| order | cases | mean recall@5 | hit@5 | mean MRR@10 |
|---|---|---|---|---|
| unranked | 20 | 0.125 | 4 | 0.120 |
| lexical | 20 | 0.250 | 6 | 0.210 |
| jev | 20 | 0.125 | 4 | 0.120 |
| jev>unranked | 20 | 0.125 | 4 | 0.120 |
| jev>lexical | 20 | 0.250 | 6 | 0.210 |

Decision rule winner: **lexical** (mean recall@5 0.250, MRR@10 0.210).

M2 drop the same-site merge: rc=1 9 failed, 56 passed in 10.13s
   expected red: ['test_same_path_within_five_lines_merges_and_keeps_every_instrument']
   all red: ['test_a_merged_chunk_text_is_capped_at_400', 'test_echo_finds_the_unfixed_sibling_and_not_the_fixed_site', 'test_echo_jev_order_keeps_the_base_selection', 'test_echo_reads_a_patch_file_and_jev_down_is_unranked', 'test_jev_down_gives_the_unranked_pack_with_its_reason', 'test_jev_order_reorders_but_never_drops_the_base_selection', 'test_json_pack_is_valid_and_under_budget', 'test_locate_finds_the_files_and_records', 'test_same_path_within_five_lines_merges_and_keeps_every_instrument']
   KILLED=True
M3 exceed the budget: rc=1 3 failed, 62 passed in 9.32s
   expected red: ['test_a_pack_never_exceeds_its_budget_or_the_hard_cap', 'test_oversized_output_stays_under_the_hard_cap']
   all red: ['test_a_pack_never_exceeds_its_budget_or_the_hard_cap', 'test_oversized_output_stays_under_the_hard_cap']
   KILLED=True
```

| mutant | edit (scripts/jev_context.py) | named tests red | killed |
|---|---|---|---|
| M1 drop the ranking | `order_ranked` sorts by the unranked key; `reorder` returns its input; the files key of the `jev` order drops the Jev sum | test_the_pure_jev_order_follows_the_scores, test_the_reorder_inside_the_selection_follows_the_scores, test_jev_order_reorders_but_never_drops_the_base_selection, test_echo_jev_order_keeps_the_base_selection (+ test_jev_reorders_the_base_selection_and_never_drops_an_item) | yes: 5 failed; `bench.py rescore` under M1 shows every ranked column equal to its base (jev = unranked 0.125, jev>lexical = lexical 0.250) |
| M2 drop the same-site merge | the merge condition becomes `if False:` | test_same_path_within_five_lines_merges_and_keeps_every_instrument (+ 8 more: the echo and locate end-to-end tests) | yes: 9 failed |
| M3 exceed the budget | `render` returns its first (largest) layout without the budget check | test_a_pack_never_exceeds_its_budget_or_the_hard_cap (both parameters), test_oversized_output_stays_under_the_hard_cap | yes: 3 failed |

History, not hidden: the FIRST mutation run (same driver) had M1 without its third edit (the `jev` column still read
0.200 under it: the files key sorts by the summed score on its own) and M3 NOT killed at the command line (the
fixture defect above); both fixed, then this rerun.


## 10. The resume (worker restart at about 14:49Z) and the two notes it carried

State at the resume (14:51Z, HEAD ee44b41 by then: other lanes' commits; this lane's files as left):

```
results.jsonl: 20 lines, all parse (last id AF-AP-164); no partial line; the run had ended at 14:25Z
2beba775ccad61b3e6131733352f37edaa8793bf77f1580f30358aba5c85960a  docs/research/findings/jev-locate-bench/cases.json
52f1ac186514d8efd41660f267902ec717978d53fb613b383fc8f6cc2d497b66  docs/research/findings/jev-locate-bench/results.jsonl
```

The lane had finished A1-A6 and the first gate pass (65 passed twice, lint rc 0, no_laya rc 0); what follows is new work.

**Note 1, JT3: `splitlines()` cuts a matched line at a form feed; the same flaw sat in `parse_rg` (AF-AP-132's class).**
A sweep of this lane's files found six sites in `scripts/jev_context.py`: run_tool's reason line, parse_graft,
parse_cbm, parse_rg, inst_rg's `--files` list and inst_gitlog. All six now use `lines_of()` (split on `\n` only, DD-16).
The two CLI docstring reads (`__doc__.splitlines()[0]`, this lane's own text) and the tests' helper that splits the
pack's own output (`clean()` already turned every such character into a space) were left as they are.
Tests, red then green: `test_rg_keeps_a_matched_line_whole_across_a_line_separator` over five characters
(FF, VT, FS, NEL, LS, built with `chr()`), `test_graft_keeps_an_entry_whole_across_a_form_feed`,
`test_git_log_keeps_a_subject_whole_across_a_form_feed`. On a scratch copy with `lines_of` restored to `splitlines()`:
7 failed, for the exact reasons (`('scripts/a.py', 12, 'x = 1') != ('scripts/a.py', 12, 'x = 1 scripts/evil.py:99:y')`
plus `Left contains one more item`; `['git:abc1234', 'git:deadbee'] == ['git:abc1234']`); on the fix: 7 passed.
Effect on the results already reported: none. Three files in the searched `tests/` tree hold such characters
(tests/test_report_lint.py:118, tests/test_ap_screen.py:89, tests/test_decide_harvest.py:777-839). 13 of the 20 A3
cases hold a chunk from one of them, but every rg-found line among those is another line (the chunk tables in
results.jsonl), and the defect only cut the text of a line rg printed.

**Note 2, VERIFY-JT1 F-24: a long query fills the 1,024-token window and every chunk scores the same.** This lane had
bounded the query (1,200 characters, DD-3) from the start; the bound had not been measured in TOKENS. Measured now with
the model's own tokenizer (a dereferenced scratch copy of the snapshot's `tokenizer/`, with laya's own config fix-up
applied to the copy only; the server's files were not touched) and laya's own `build_sequence`, on this lane's real
query shapes after jev.py's scrub-then-cap, against the 12 longest real chunk texts (a live `collect()` of A1 Q2 and the
de06db6 echo candidates):

```
trace_tail               query  1087 chars  344 tok | worst state with a top-6 chunk:  573 tok, room 987, chunk whole: True
a1_q2                    query   228 chars   76 tok | worst state with a top-6 chunk:  282 tok, room 987, chunk whole: True
a3_longest               query   933 chars  241 tok | worst state with a top-6 chunk:  447 tok, room 987, chunk whole: True
echo_de06db6             query  1013 chars  360 tok | worst state with a top-6 chunk:  587 tok, room 986, chunk whole: True
echo_af_ap_184           query  1144 chars  436 tok | worst state with a top-6 chunk:  668 tok, room 986, chunk whole: True
adversarial_short_shas   query  1200 chars  728 tok | worst state with a top-6 chunk:  935 tok, room 987, chunk whole: True
WORST: ('adversarial_short_shas', 1200, 728, 485, 935, 987, True)
trace-like query of 1200 chars + the longest chunk: 597 state tokens (room 987) whole=True
trace-like query of 1600 chars + the longest chunk: 721 state tokens (room 987) whole=True
trace-like query of 2000 chars + the longest chunk: 865 state tokens (room 987) whole=True
trace-like query of 2400 chars + the longest chunk: 1000 state tokens (room 987) whole=False
```

Reading: at 1,200 characters every real shape keeps the longest real chunk whole with room to spare (worst real: 668 of
986 tokens); a trace-like query would cut the chunk only at about 2,400 characters. The adversarial run of short commit
ids still fits, with 52 tokens to spare. So the bound stands, and F-24's second recommendation is added as the safety
net for text that tokenizes worse (DD-15): a ranking whose N>=2 scores are all equal is refused, and the pack falls back
to its base order with `Jev unavailable: all N scores are equal (v): no signal (a query over the window cuts every
chunk) (unranked)`. Tests: `test_all_equal_scores_are_no_ranking` (with a spread-of-scores negative control and the
one-chunk case), `test_a_signal_free_jev_gives_the_base_pack_with_its_reason` (the command line),
`test_the_query_bound_leaves_room_for_a_chunk` (pins 1,200 and the 400-character chunk cap it was measured with).
The results already reported were not affected: every A3 ranking had a spread.

```
A3 cases: 20; distinct scores per case 30-48 of 30-48 scored; spread (max-min) 0.1260-0.4729; all-equal cases: 0
```

**The kill table after both fixes** (the same driver, a fresh scratch copy per mutant, two mutants added for this
resume's changes):

```
baseline (unmutated scratch copy): rc=0 75 passed in 10.43s
M1 drop the ranking: rc=1 5 failed, 70 passed in 10.34s
   expected red: ['test_the_pure_jev_order_follows_the_scores', 'test_the_reorder_inside_the_selection_follows_the_scores', 'test_jev_order_reorders_but_never_drops_the_base_selection', 'test_echo_jev_order_keeps_the_base_selection']
   all red: ['test_echo_jev_order_keeps_the_base_selection', 'test_jev_order_reorders_but_never_drops_the_base_selection', 'test_jev_reorders_the_base_selection_and_never_drops_an_item', 'test_the_pure_jev_order_follows_the_scores', 'test_the_reorder_inside_the_selection_follows_the_scores']
   KILLED=True
   bench.py rescore under M1 (the saved rows, the mutated library):

Decision rule winner: **lexical** (mean recall@5 0.250, MRR@10 0.210).

M2 drop the same-site merge: rc=1 9 failed, 66 passed in 10.44s
   expected red: ['test_same_path_within_five_lines_merges_and_keeps_every_instrument']
   all red: ['test_a_merged_chunk_text_is_capped_at_400', 'test_echo_finds_the_unfixed_sibling_and_not_the_fixed_site', 'test_echo_jev_order_keeps_the_base_selection', 'test_echo_reads_a_patch_file_and_jev_down_is_unranked', 'test_jev_down_gives_the_unranked_pack_with_its_reason', 'test_jev_order_reorders_but_never_drops_the_base_selection', 'test_json_pack_is_valid_and_under_budget', 'test_locate_finds_the_files_and_records', 'test_same_path_within_five_lines_merges_and_keeps_every_instrument']
   KILLED=True
M3 exceed the budget: rc=1 3 failed, 72 passed in 10.09s
   expected red: ['test_a_pack_never_exceeds_its_budget_or_the_hard_cap', 'test_oversized_output_stays_under_the_hard_cap']
   all red: ['test_a_pack_never_exceeds_its_budget_or_the_hard_cap', 'test_oversized_output_stays_under_the_hard_cap']
   KILLED=True
M4 drop the equal-scores guard: rc=1 2 failed, 73 passed in 10.34s
   expected red: ['test_all_equal_scores_are_no_ranking', 'test_a_signal_free_jev_gives_the_base_pack_with_its_reason']
   all red: ['test_a_signal_free_jev_gives_the_base_pack_with_its_reason', 'test_all_equal_scores_are_no_ranking']
   KILLED=True
M5 split on every line separator: rc=1 7 failed, 68 passed in 10.42s
   expected red: ['test_rg_keeps_a_matched_line_whole_across_a_line_separator', 'test_graft_keeps_an_entry_whole_across_a_form_feed', 'test_git_log_keeps_a_subject_whole_across_a_form_feed']
   all red: ['test_git_log_keeps_a_subject_whole_across_a_form_feed', 'test_graft_keeps_an_entry_whole_across_a_form_feed', 'test_rg_keeps_a_matched_line_whole_across_a_line_separator']
   KILLED=True
```

| mutant | edit | named tests red | killed |
|---|---|---|---|
| M1 drop the ranking | as section 9 | the four named + test_jev_reorders_the_base_selection_and_never_drops_an_item | yes, 5 failed |
| M2 drop the same-site merge | as section 9 | test_same_path_within_five_lines_merges_and_keeps_every_instrument + 8 end-to-end | yes, 9 failed |
| M3 exceed the budget | as section 9 | test_a_pack_never_exceeds_its_budget_or_the_hard_cap, test_oversized_output_stays_under_the_hard_cap | yes, 3 failed |
| M4 drop the equal-scores guard | its `if` becomes `if False:` | test_all_equal_scores_are_no_ranking, test_a_signal_free_jev_gives_the_base_pack_with_its_reason | yes, 2 failed |
| M5 split on every line separator | `lines_of` returns `text.splitlines()` | the rg test (5 parameters), the graft and the git-log tests | yes, 7 failed |

The driver is in this lane's scratchpad, not in the boundary; its exact edits (each anchor asserted to occur once,
applied to a fresh copy of the 12 files, the module compiled, pytest from the copy):

```python
MUTANTS = {
    "M1 drop the ranking": [(LIB,
        '    return sorted(chunks, key=lambda c: (0 if c["id"] in scores else 1, -scores.get(c["id"], 0.0)) + unranked_key(c))',
        '    return sorted(chunks, key=unranked_key)'),
        (LIB, '    pos = {id(x): i for i, x in enumerate(items)}\n', '    return list(items)\n    pos = {}\n'),
        (LIB, '        key = lambda f: (-round(f["score"], 9), -f["agreement"], -f["lexical"], f["path"])',
              '        key = lambda f: (-f["agreement"], -f["lexical"], f["path"])')],
    "M2 drop the same-site merge": [(LIB,
        'if cur is not None and h["path"] == cur["path"] and h["line"] - cur["line"] <= MERGE_LINES:', 'if False:')],
    "M3 exceed the budget": [(LIB, '        if len(text) <= budget:\n            return text', '        return text')],
    "M4 drop the equal-scores guard": [(LIB, '    if len(scores) >= 2 and len(set(scores.values())) == 1:',
                                         '    if False:')],
    "M5 split on every line separator": [(LIB, '    return text.split("\\n")\n', '    return text.splitlines()\n')],
}
```

**The final code, live once more** (A1 Q2 at 14:59Z, the local server): the same top 5 as at 14:32Z, and the gitnexus
mislabel of section 5 gone.

```
jev_locate: 127 hits, 104 chunks, 48 ranked by Jev, 8 of 8 instruments answered, wall 48.6 s
1. 0.553 cbm tests/test_proof_status.py:338 — Function tests.test_proof_status.<opaque-redacted>
2. 0.541 cbm tests/test_proof_status.py:298 — Function tests.test_proof_status.<opaque-redacted>
3. 0.529 git-log commit ec8ce8f — ec8ce8f CLAUDE.md quirk: tests/test_proof_status.py needs a SHORT --basetemp (the scratchpad path exceeds gpg-agent's Unix-socket length limit → nine false reds 2026-09-14); a regenerated minted result after an accepted tag fails three c...
4. 0.503 rg tests/test_proof_status.py:255 — ["gpg", "--batch", "--quiet", "--pinentry-mode", "loopback", "--passphrase", "", | "--quick-generate-key", f"{name} <{name}@example.invalid>", "ed25519", "sign", "0"], | listing = subprocess.run(["gpg", "--batch", "--with-colons", "--lis...
5. 0.496 rg tests/test_governance_review.py:56 — ["gpg", "--batch", "--quiet", "--pinentry-mode", "loopback", "--passphrase", "", | "--quick-generate-key", f"{name} <{name}@example.invalid>", "ed25519", "sign", "0"], | listing = subprocess.run(["gpg", "--batch", "--with-colons", "--lis...
## unmapped and not run
- (none)
$ diff a1q2.md a1q2_final.md      # 14:32Z pack vs 14:59Z pack, the same question and endpoint
13c13
< 8. 0.480 gitnexus+rg tests/test_jev_context.py:293 — Variable TRACE | tests/test_proof_status.py:192: FileNotFoundError: `gpg --quick-generate-key` failed; see parse_pc_reply and os.path.exists'''
---
> 8. 0.477 gitnexus+rg tests/test_jev_context.py:347 — Variable TRACE | tests/test_proof_status.py:192: FileNotFoundError: `gpg --quick-generate-key` failed; see parse_pc_reply and os.path.exists'''
17c17
< 12. 0.279 rg tests/test_jev_context.py:301 — ("quoted", "gpg --quick-generate-key", None), | ("error", "FileNotFoundError", None), ("flag", "--quick-generate-key", None),
---
> 12. 0.280 rg tests/test_jev_context.py:355 — ("quoted", "gpg --quick-generate-key", None), | ("error", "FileNotFoundError", None), ("flag", "--quick-generate-key", None),
21c21
< 3. tests/test_verify_command.py:159 — sum 1.609 (6 chunks: cbm)
---
> 3. tests/test_verify_command.py:159 — sum 1.609 (5 chunks: cbm)
26c26
< 8. tests/test_jev_context.py:293 — sum 0.759 (3 chunks: gitnexus, rg)
---
> 8. tests/test_jev_context.py:347 — sum 0.757 (4 chunks: cbm, gitnexus, rg)
30c30
< - unmapped — gitnexus context CalledProcessError unavailable (rc 1: "error": "Symbol 'CalledProcessError' not found")
---
> - (none)
```

Every difference has a cause outside Jev: this lane's test file grew between the runs (its fixture moved from line 293 to
347), the chunk text sent to Jev carries `path:line` so the moved chunk's score moved (0.480 to 0.477), cbm's index
refreshed (6 to 5 chunks), and the mislabel is fixed. Every unchanged chunk got the identical score: Jev is
deterministic for identical input here.

## 11. Gates (15:00Z, the final code)

```
$ python -m pytest tests/test_jev_context.py tests/test_jev_locate_echo.py -q --basetemp /tmp/jt2/bt    (twice; parent made first)
run 1 rc=0: 75 passed in 12.27s
run 2 rc=0: 75 passed in 12.03s
2 files set=dc3e2b7404ab        (the pc_suite.sh set-id formula, computed locally)
$ python3 scripts/lint_delta.py --base HEAD
lint_delta (worktree vs HEAD): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed
rc=0
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean
rc=0
```

The lint gate's "2 .py changed" are another lane's tracked files (scripts/install_session_hooks.py,
tests/test_session_hooks.py); it cannot see this lane's six untracked files (lint_delta.py:73-80; CLAUDE.md now says so,
JT1 DISC-1). The same `_flakes` delta, run on this lane's files directly: 0 NEW hits in each of scripts/jev_context.py,
scripts/jev_locate.py, scripts/jev_echo.py, tests/test_jev_context.py, tests/test_jev_locate_echo.py,
docs/research/findings/jev-locate-bench/bench.py. The AP screen's tells on those files (advisory), each read: AF-AP-115
(`shutil.which("rg")` in a test's skip marker, not a trust anchor), AF-AP-175 (`HEAD` named once per process: bench.py's
`rev-parse --short HEAD` records the tree, the tests' `git show HEAD` reads a throwaway fixture repo), AP-32 (bench.py
hashes exactly the bytes it writes: its printed sha256 equals `sha256sum cases.json`). Line-separator bytes: 0 in every
file this lane wrote (`LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`). `no_laya_in_gates`: none of this lane's paths is in
`scripts/gate_files.txt` or under its three structural globs, so no gate imports or runs these tools (KC-J1).

## 12. NOT done (first-class)

1. **Nothing is committed** (the brief: do not commit). The coordinator commits the boundary. `cases.json` must be
   committed byte for byte (its sha256 2beba775...85960a is the pre-registration), with `results.jsonl` (52f1ac18...).
2. **RESOLVED (D-077, section 17): the default order.** The rule's pick (jev over the lexical base) was overridden by
   the coordinator; the default is `lexical` and Jev is opt-in.
3. **The echo misses defects that are a MISSING guard.** A4's AF-AP-184 run found no true echo and missed the real
   candidates (section 7): the removed lines were site-specific string literals, and no removed line kept two API names
   for a shape. Not built: a candidate source for "the fix ADDED a guard; where is the same call WITHOUT it".
4. **A3 measured anti-pattern CLASS descriptions, not bug reports.** n = 20, no significance test; the instruments'
   ceiling is 0.575 (7 of 20 targets never returned by any instrument). A benchmark on real error traces and failing-test
   outputs (the tool's intended input) is not done.
5. **The searched tree moved during A3** (section 13, X-8). Not frozen: the shared tree is live.
6. **"The two most distinctive tokens" for git log -S** is a heuristic (kind, then length), not a measured rarity.
7. **The quirks instrument sees only lines with the `bit 2026-` marker** (D-1). Unmarked quirks are invisible to it;
   A1 Q2's answer (the test_proof_status basetemp quirk) was found through git log -S instead.
8. **GitNexus `context` runs for at most 2 identifiers per question** (the shared 30 s budget, DD-4); not measured
   whether more would help.
9. **No structured telemetry events.** The tools print one stderr summary line; the pack itself carries every reason
   (the ranking line, the unmapped lines). No JSON event stream.
10. **No registry row for the two defects found in this lane's own code** (the splitlines class is AF-AP-132's; the
    GitNexus "rc 1 with an answer" mislabel is a new shape, section 15 item 3): docs/INCIDENT-LOG.md is outside the
    boundary. Reported for the coordinator's bug-echo.
11. **Live Jev runs wrote lines to jev.py's call log** (`.jev/calls.jsonl`, gitignored), as JT1's D-6 designs; every
    test passes `log=False` or `--no-jev-log`.

## 13. Discrepancies and deviations (flagged)

| # | item | the brief | this lane | why |
|---|---|---|---|---|
| X-1 | D-2 merge | same-path hits within 5 lines merge | code hits merge; record rows (registry, quirks, commits) stay one row each and are not files to read (DD-8) | two adjacent registry rows are two anti-patterns; summing 8 rows would put docs/INCIDENT-LOG.md first on every pack |
| X-2 | D-3 fallback | Jev down: "ordered by instrument agreement then lexical score" | Jev down or signal-free: the base order of the default, now LEXICAL; D-3's agreement-first order stays as `--order unranked` | the coordinator's rule 2 made the base the stronger non-Jev order; A3: agreement-first 0.125 vs lexical 0.250 |
| X-3 | D-3 ranking | Jev ranks the chunks | Jev may only REORDER the base order's selection (KC-J5); the pure Jev order is kept as A3's `jev` column only | the coordinator's rule 3 |
| X-4 | A3 input | "the registry row's first cell" | the mechanism cell (the second) with answer leaks removed (DD-14) | the first cell is the id |
| X-5 | A2 | "PATH stripped" | PATH = an empty directory AND HOME = an empty directory | cbm and crg live under HOME (DD-6); an empty PATH string searches the current directory and no PATH at all falls back to os.defpath (/bin:/usr/bin) |
| X-6 | D-1 timeout | 30 s per instrument | one 30 s budget per instrument, shared by its calls; Jev 240 s (DD-2, DD-4) | measured (P-3) |
| X-7 | PIN | db71586 | db71586 is not on origin: push_clean rewrote it into db34178 (the same tree 8bc6616f); `bench.py select --pin db34178` reproduces the identical 20 cases (only the file's "pin" field differs) | CLAUDE.md's PIN rule |
| X-8 | A3 tree | "the tree is HEAD" | cases 1-12 ran at cb131aa (20-27 dirty paths), cases 13-20 at 18ba7ed (18 dirty paths): other lanes' commits landed mid-run | the shared live tree; the rows record head and dirty count |
| X-9 | lint gate | `lint_delta.py --base HEAD` with no new hit | passes, but cannot see untracked files; the same delta run on the 6 files directly: 0 new | lint_delta.py:73-80 |
| X-10 | A4 | "the AF-AP-184 guard in 40543ab's parent chain" | 40543ab itself holds the guard; the echo ran on its guard hunk only (patch sha256 d83d0032...) | the other three hunks of the file are F-L1-1 and F-L1-5 |
| X-11 | premise P-3 | 8 chunks in 3.4 s | 10.8 s (8 chunks), 62.7 s (48) under load | the box, not the design |
| X-12 | DD-15, DD-16 | not in the brief | added at the resume on the coordinator's notes (F-24, JT3) | the notes |
| X-13 | Jev calls | at most 48 chunks per call | at most 48 per question, in calls of 8, all or nothing (within the pin) | the server answers under one lock and is shared with other lanes; each chunk is its own model call, so a batch changes no score |

## 14. Self-attack: the three most likely ways this change is wrong

1. **The A3 verdict rests on too little.** The winning order leads by ONE boundary case, n = 20, and MRR@10 says the
   opposite. NOT ruled out; stated as the open decision. What is ruled out is a wrong number: the rule was fixed before
   the run, the per-case ranks are in section 4, and `bench.py rescore` reproduces every column from the saved chunks
   and scores with the final library (checked after the last code change).
2. **A Jev score drops an item the base keeps, or a signal-free ranking is shown as a ranking.** Ruled out for the
   first by `select()` (every fit level shows the base order's top k, reordered) and its tests: the de-vacuoused unit
   test (the pure order would drop the whole base top 5), the two `--top 1` command-line tests (M1 kills all three).
   Ruled out for the second by the token measurement (worst real 668 of 986 tokens) plus DD-15 (M4 kills its tests), and
   every A3 ranking had a spread of 0.126 or more. Residual: a PARTIAL cut of a chunk's tail is not detected (the
   scores still differ); the measurement shows the real chunks fit whole.
3. **The parsers read an instrument wrong and the pack looks mapped.** Each parser is pinned on a live capture (two
   built from a live shape, marked so), the graft parser keeps only sites that exist, vendored paths are dropped, and a
   non-JSON or failed reply is an `unmapped` line, never an empty answer (A2, the exact eleven lines). Found and fixed on
   the way: the GitNexus "not found" reply mislabeled as an outage (section 5), the callers' missing `kind`, and the
   splitlines cut (section 10). Residual: an instrument version that changes its output shape gives an empty or
   unmapped instrument, not a crash (`_safe`), and A2's test pins the unmapped path.

## 15. Adjacent findings (outside the boundary; not fixed)

1. **WATCH, harness-ports/bin/lane-profile.sh:65,68,154,158,216,220,240,244**: Hermes lane-profile hooks registered as
   `python3 {helper} record|gate` with no existence guard, AF-AP-184's shape IF Hermes reads a hook's exit 2 as blocking
   (not verified; python's can't-open code is 2).
2. **WATCH, tests/test_s0_01_frame_tee.py:3326**: `assert os.path.exists(stat_path)` then `open(stat_path)` on an agent
   expected alive; if the agent is reaped in between, the test fails with FileNotFoundError instead of "agent not
   alive" (a misleading failure, not a false pass).
3. **INFO, measured: GitNexus answers "not found" with rc 1.** `node .gitnexus/run.cjs impact zzq_no_such_symbol_xyz
   --direction upstream --repo .` exits 1 with `{"error": "Target 'zzq_no_such_symbol_xyz' not found", ...,
   "impactedCount": 0, "risk": "UNKNOWN"}` on stdout; `context` does the same. `scripts/lane_context.sh`'s `run()`
   (lines 44-47) reads any non-zero rc as `unmapped — gitnexus impact unavailable or failed (rc 1): }`: an answer
   (the symbol is not in the index, typical for a lane's new def) labeled as an outage, its reason lost to `tail -1`.
   This lane fixed the same shape in its own `inst_gitnexus` (section 5). A registry candidate.
4. **INFO**: VERIFY-JT1's F-25 (the scrubber turns 40+ character identifiers into `<opaque-redacted>`) shows in this
   lane's packs: long test names read `tests.test_proof_status.<opaque-redacted>`, and Jev sees the same.
5. **INFO**: D-1's `bit 2026-` marker misses unmarked CLAUDE.md quirks (NOT-done item 7).

## 16. Evidence tiers

- **Verified** (a command this session, output pasted above): the premise (P-1 to P-5); A1 (three live packs, and Q2
  once more on the final code); A2 (three live runs and the tests); A3 (the digest before the run, the table, the
  forensic pass, `rescore` on the final library); A4 (two live echoes); A5 and A6 (the tests; five mutants killed, the
  unmutated baseline 75 passed); the gates; the token measurement; the splitlines red-green.
- **Inferred**: the A4 BUG/WATCH/OK readings (my reading of each site); "Jev degrades the ranking" (MRR@10 on n = 20);
  the lane-profile.sh WATCH (Hermes's exit-2 semantics not read).
- **Assumed**: the laya package in /root/venv-laya-probe is the code the running server uses (the server runs that
  venv's python, pid 30467; not proven further); the server reads the snapshot's `rl_agent_config.json` (its health
  names the same revision 1c5edc17).

## 17. D-077: the default order is `lexical` (the coordinator's decision, 15:0xZ); Jev is opt-in

**The decision.** The pack's default is `lexical`, in both tools. The Jev orders stay available behind `--order jev`,
opt-in: Jev reorders the lexical order's selection and never drops from it (KC-J5).

**The rule's own pick.** The rule I fixed before the A3 run chose `jev>lexical`, Jev reordering the lexical order:
mean recall@5 0.300 against 0.250 for plain lexical (section 4).

**Why it was overridden** (the coordinator's reasons, recorded as D-077):
- The lead is ONE case of 20 crossing the rank-5 line (AF-AP-38, rank 6 to rank 5).
- MRR@10 reverses it: 0.122 for `jev>lexical` against 0.210 for lexical; where Jev moved a target, it moved it down in
  4 of 5 cases.
- Cost: a Jev pack took 36-165 s on this box against 5-28 s for the instruments alone.
- D-074: a model becomes the default only when it beats the plain order; this run does not show that. The bench
  reruns when a better model exists (`bench.py run` on a fresh results file; `rescore` recomputes every column).

The live packs agree that the per-question picture is mixed. On A1 Q1 lexical put the quirk that names the error first
and Jev moved it to 9th (section 5). On A1 Q3 the file that decides the CI verdict, `scripts/ci_gate.py`, is 8th in the
lexical files list and was 4th under the Jev reorder; both are inside the 10 shown, the same set (KC-J5).

**What changed (this lane's boundary only):**
- `scripts/jev_context.py`: `DEFAULT_ORDER = "lexical"` (was `"jev"`); its comment now records D-077 and the numbers.
  `JEV_BASE` stays `"lexical"`: it is both the selection `--order jev` reorders and the order when Jev is down or
  signal-free.
- `scripts/jev_locate.py`, `scripts/jev_echo.py`: the `--order` help names D-077. Both docstrings are corrected: they
  still listed the `--no-jev` flag that `--order` replaced at 13:3xZ, and said Jev ranks or scores unconditionally.
- Tests pinning the default (new):
  - `test_the_default_order_is_lexical_and_jev_reorders_lexical` (the constants);
  - `test_the_default_order_is_lexical_and_never_asks_jev` (jev_locate);
  - `test_the_echo_default_order_is_lexical_and_never_asks_jev` (jev_echo).
  Each command-line test runs with no `--order` and a Jev double named by `--jev-url`. It asserts the double received
  zero requests, that the ranking line is `ranking: lexical order (lexical overlap), Jev not asked`, and that the pack
  is byte-identical to `--order lexical`. The negative control: the same double IS asked under `--order jev`.
- Tests kept, unchanged: `--order jev` still works and never drops an item
  (`test_jev_order_reorders_but_never_drops_the_base_selection`, `test_echo_jev_order_keeps_the_base_selection`,
  `test_jev_reorders_the_base_selection_and_never_drops_an_item`).

**Mutants re-run (15:08Z-15:10Z):** the same driver, all six. M6 is new: it flips the default back to `jev`.
M1 (drop the ranking) is the other mutant that touches the default's machinery.

```
baseline (unmutated scratch copy): rc=0 78 passed in 14.80s
M1 drop the ranking: rc=1 5 failed, 73 passed in 13.43s
   expected red: ['test_the_pure_jev_order_follows_the_scores', 'test_the_reorder_inside_the_selection_follows_the_scores', 'test_jev_order_reorders_but_never_drops_the_base_selection', 'test_echo_jev_order_keeps_the_base_selection']
   all red: ['test_echo_jev_order_keeps_the_base_selection', 'test_jev_order_reorders_but_never_drops_the_base_selection', 'test_jev_reorders_the_base_selection_and_never_drops_an_item', 'test_the_pure_jev_order_follows_the_scores', 'test_the_reorder_inside_the_selection_follows_the_scores']
   KILLED=True
   bench.py rescore under M1 (the saved rows, the mutated library):

Decision rule winner: **lexical** (mean recall@5 0.250, MRR@10 0.210).

M2 drop the same-site merge: rc=1 10 failed, 68 passed in 12.08s
   expected red: ['test_same_path_within_five_lines_merges_and_keeps_every_instrument']
   all red: ['test_a_merged_chunk_text_is_capped_at_400', 'test_echo_finds_the_unfixed_sibling_and_not_the_fixed_site', 'test_echo_jev_order_keeps_the_base_selection', 'test_echo_reads_a_patch_file_and_jev_down_is_unranked', 'test_jev_down_gives_the_unranked_pack_with_its_reason', 'test_jev_order_reorders_but_never_drops_the_base_selection', 'test_json_pack_is_valid_and_under_budget', 'test_locate_finds_the_files_and_records', 'test_same_path_within_five_lines_merges_and_keeps_every_instrument', 'test_the_echo_default_order_is_lexical_and_never_asks_jev']
   KILLED=True
M3 exceed the budget: rc=1 3 failed, 75 passed in 11.93s
   expected red: ['test_a_pack_never_exceeds_its_budget_or_the_hard_cap', 'test_oversized_output_stays_under_the_hard_cap']
   all red: ['test_a_pack_never_exceeds_its_budget_or_the_hard_cap', 'test_oversized_output_stays_under_the_hard_cap']
   KILLED=True
M4 drop the equal-scores guard: rc=1 2 failed, 76 passed in 12.56s
   expected red: ['test_all_equal_scores_are_no_ranking', 'test_a_signal_free_jev_gives_the_base_pack_with_its_reason']
   all red: ['test_a_signal_free_jev_gives_the_base_pack_with_its_reason', 'test_all_equal_scores_are_no_ranking']
   KILLED=True
M5 split on every line separator: rc=1 7 failed, 71 passed in 12.42s
   expected red: ['test_rg_keeps_a_matched_line_whole_across_a_line_separator', 'test_graft_keeps_an_entry_whole_across_a_form_feed', 'test_git_log_keeps_a_subject_whole_across_a_form_feed']
   all red: ['test_git_log_keeps_a_subject_whole_across_a_form_feed', 'test_graft_keeps_an_entry_whole_across_a_form_feed', 'test_rg_keeps_a_matched_line_whole_across_a_line_separator']
   KILLED=True
M6 the default back to jev: rc=1 3 failed, 75 passed in 11.79s
   expected red: ['test_the_default_order_is_lexical_and_jev_reorders_lexical', 'test_the_default_order_is_lexical_and_never_asks_jev', 'test_the_echo_default_order_is_lexical_and_never_asks_jev']
   all red: ['test_the_default_order_is_lexical_and_jev_reorders_lexical', 'test_the_default_order_is_lexical_and_never_asks_jev', 'test_the_echo_default_order_is_lexical_and_never_asks_jev']
   KILLED=True
```

M6 is red for the exact reason: under a Jev default the double received a real request (`assert [{'model': 'laya',
'state': {'query': 'open_socket fails ...'...}] == []`, and the same for the echo), and the constant pin reads
`('jev', 'lexical') == ('lexical', 'lexical')`.

**Gates, each run twice (15:10Z, the D-077 code):**

```
$ python -m pytest tests/test_jev_context.py tests/test_jev_locate_echo.py -q --basetemp /tmp/jt2/bt    (parent made first)
pytest run 1 rc=0: 78 passed in 12.01s
pytest run 2 rc=0: 78 passed in 12.38s
$ python3 scripts/lint_delta.py --base HEAD
lint_delta run 1 rc=0: lint_delta (worktree vs HEAD): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed
lint_delta run 2 rc=0: lint_delta (worktree vs HEAD): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates run 1 rc=0: no_laya_in_gates: 40 files scanned, clean
no_laya_in_gates run 2 rc=0: no_laya_in_gates: 40 files scanned, clean
lint_delta's _flakes delta over this lane's 6 untracked .py files: 0 NEW hit(s)
```

The test set grew from 75 to 78: the three default pins. The lint gate's "2 .py changed" are still another lane's
tracked files (section 11); the direct delta covers this lane's files.

**Live, the new default** (A1 Q3 with no `--order`, 15:1xZ, the real instruments):

```
jev_locate: 104 hits, 95 chunks, 0 ranked by Jev, 8 of 8 instruments answered, wall 8.9 s
ranking: lexical order (lexical overlap), Jev not asked
answered: graft, gitnexus, cbm, crg, rg, registry, quirks, git-log
1. a1 l3 quirks CLAUDE.md:418 — message; bit 2026-09-07 after the last lane landed) — once no lane is live, push the clean tree wi
2. a1 l3 quirks CLAUDE.md:420 — push_clean REWRITES the unpushed range, so a lane brief's `PIN:` is the POST-PUSH SHA — read it fr
3. a1 l3 rg scripts/push_clean.sh:2 — # push_clean.sh — the sanctioned push sequence (branch = PUSH_BRANCH or the current branch).
4. a2 l3 cbm+rg tests/test_ci_gate.py:180 — Function tests.test_ci_gate.<opaque-redacted> | def <opaque-redacted>(repo, tmp_path, 
5. a1 l3 cbm tests/test_ci_gate.py:759 — Function tests.test_ci_gate.<opaque-redacted>
```
