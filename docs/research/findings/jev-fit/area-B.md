> Auditor B's design report, verbatim from its hand-back (2026-09-25; read-only audit at origin 934bc8a). The plan that
> synthesizes the three areas is `PLAN-2026-09-25.md` in this directory.

# JEV-FIT, area B: the build machinery (auditor B)

Base: origin 934bc8a, branch `claude/soundbox-kit-migration-iz1jwf`. Read-only: no files written, no git writes, no network, no bridge.

**Sources.**
- The area-B code, read at the lines cited.
- The 119 committed PC lane digests (`transcripts/pc/*.md`). I computed my counts from their headers, tool-result headings and `usage.json` tails, with the PC home path masked.
- The JEV-MAP and DATA-SESSION counts, reused where named.
- The registry rows in `docs/INCIDENT-LOG.md`.
- Transcripts were only counted. I discarded one phrase count over them, because it also counted the coordinator reading the dispatcher's own source.

## Answer first

1. **Most measured waste here is structural.** It sits in the vLLM KV cache, each lane's context size and the poll budget, and a plain rule fixes each. A forecast model adds nothing: brief size does not predict a lane's context (Pearson r = 0.11, n = 25 local lanes), and 24 of 25 local lanes average at least 57k prompt tokens per call.
2. **The best Jev fit is the Hermes lane stream on the PC.** An RWKV reader would sit beside each lane. It would be fed by a recorder that already exists but is switched off (`harness-ports/bin/lane-done-gate.py:145-179`; off by default at `harness-ports/bin/lane-profile.sh:116`). The second fit is Laya ranking registry rows in the verify context pack.
3. **KC-J1 draws the map.** The dispatcher, the runner and the commit, push and CI scripts are gate files (`scripts/gate_files.txt:6-31`), screened for Jev vocabulary (`scripts/no_laya_in_gates.py:66-68`). Rules may go into them; every Jev in area B lives outside them.

## 1. Integration points

### 1a. Where, when, what

| ID | Point | Seam (file:line) | Trigger | Input | Question (type: options) | Action |
|---|---|---|---|---|---|---|
| B1 | KV-budget admission | `scripts/pc_lane.sh:92-105` `_admit_verdict`; its PC probe `:231`; defer `:239-243` | first launch on a local route | vLLM KV use and waiting count; live local lanes | yes/no: will a request wait past the first-event limit? | defer with rc 75, as the disk and memory floors do; the coordinator waits or uses a sandbox agent (D-062) |
| B2 | Lane context diet | lane-profile hook block `harness-ports/bin/lane-profile.sh:207-215`; spool write `harness-ports/bin/hermes-hook-adapter.py:151-170`, drained at `pre_llm_call` `:179-195` (`harness-ports/hermes/config-snippet.yaml:137-139`) | `post_tool_call` on `skill_view`, `read_file` | skill name against `.lanes/<id>/brief.md`; result size | rule: skill not named by the brief? result of 20,000 characters or more? | one spooled line into the lane's next turn. Blocking in `pre_tool_call` stays the owner's call (`config-snippet.yaml:181-192`) |
| B3 | Lane progress watch | the recorder above, extended to every tool; a new PC watcher; the spool as in B2; the coordinator's heartbeat (not committed today) | each recorded fact | the lane's events (tool, command, exit code, edit paths, sizes); for RWKV, also the Hermes messages | choice: progressing / gate loop / premise research / harness stall / finished but running | spool one nudge; write `.lanes/<id>/watch.json` for the heartbeat; the coordinator decides a TERM (`harness-ports/bin/pc-lane.sh:119-127`) |
| B4 | Verify attack ranking | `scripts/lane_context.sh:62-63`, after the mechanical screen, calling `jev.rank` as `scripts/hiccup_scan.py:615-648` does; `run` fails open (`lane_context.sh:44-47`) | the pack for a verify brief; contract negotiation (`.claude/skills/contract-gate/SKILL.md:38-50`) | the file's diff hunks (`lane_context.sh:53`); the lexical top 16 of registry rows with no mechanical screen | score per row: does this change risk this row's failure? | print the top 3 as "attack first (advisory, unverified)" |
| B5 | Poll budget by route | `scripts/pc_lane.sh:143-144`; time-out `:428-432` | dispatch | route, role | rule: budget = the route's p90 lane span | fewer re-attaches; landings harvested on time |
| B6 | Lane end forecast (D24, D35) | the heartbeat, not `pc_lane.sh` (a gate file) | each heartbeat | heartbeat lines, `watch.json` | choice: report / draft only / FAILED | prepare the re-dispatch |
| B7 | Verifier early read (D27) | the verifier's stream (on the PC, B3's recorder; in the sandbox, SubagentStop, not registered) | each verifier event | the stream | choice: the 4 recommendation words | draft the repair brief early |
| B8 | Finding dedup across rounds (new) | beside `scripts/decide-harvest:662` `_finding_candidates`; the budget key `contract-gate/SKILL.md:66-72` | a repair-round verify report lands | one finding block; earlier rounds' findings on the same component | score per earlier finding: same defect? | mark "likely rediscovery of <id>"; the budget call stays the coordinator's |
| B9 | CI red before push (D21) | `scripts/push_clean.sh:88-89` calling `scripts/ci_gate.py`; derived tests at `lane_context.sh:88-89` | push | the outgoing range | rule: run the derived test set first | fewer red runs |
| B10 | Commit and push outcome (D18, D19) | `scripts/hooks/pre-commit:131-144`; `scripts/push_clean.sh:60-63` | commit, push | message text, `git status` | rule | none new: the gates already answer in seconds |
| B11 | PC hiccup families | `scripts/hiccup_scan.py:204-226` reads Claude Code JSONL only; the Jev column at `:615-648` | harvest | PC tool errors (needs the corpus in section 3) | choice: 15 families + UNCOVERED; rank for UNCOVERED | page rows for PC lanes |
| B12 | Report claim check | a helper beside `scripts/report_lint.py:75-109` (a gate file, `gate_files.txt:14`) | a lane report lands | one report line and the lines it cites | yes/no: do the cited lines support the claim? | flag for the verifier |
| B13 | Effort routing (new) | `scripts/pc_lane.sh:174-182`; the per-request path is not wired (`:281-283`) | dispatch | the brief | choice: medium / xhigh | set the lane's effort |

### 1b. Payoff, labels, model, size

| ID | Payoff (count, source) | Labels (recorded answer) | Rule it must beat | Model fit | Build |
|---|---|---|---|---|---|
| B1 | 4 starved local lanes (AF-AP-146, three on 2026-09-23; J1-3-R1, INCIDENT-LOG:74). vLLM showed 76 preemptions at kv 0.93 (INCIDENT-LOG:163); re-prefill GPU time unmeasured. The 10-minute heartbeat saw `wait>0` with `kv>=0.75` 0 times (JEV-MAP D25). At least 11 attempts lost in the 7 resumed local lanes (digests) | vLLM waits and call_logs 504s in the window | admit by count, at most 2 | a rule is enough (see answer 1); KV holds 222,822 tokens | small (task #180; unit test point `admit-check`, `:126-134`) |
| B2 | Since 2026-09-04: 286 `skill_view` calls returned 4.31 M characters in 45 of 108 lanes (local route: 64 calls, 1.04 M, 14 lanes). `read_file` results of 20k or more: local 56 (1.50 M characters, 31 of 53 lanes); cloud 183 (6.75 M). The effect on KV is unmeasured | none needed | none | a rule is enough | small |
| B3 | About 3.8 recorded local lane-hours, out of 132.8 measured: N5k 47 min (`pc-lane.sh:246-250`); its xhigh arm 60+ min and 130k output tokens (`:252-255`); J1-1-R3 about 2 h, 80 API calls, 0 edits (INCIDENT-LOG:72). At risk: 22 of 71 build lanes and 10 of 48 verify lanes ran 60+ calls with no edit; 41 of 71 build lanes had 3+ identical (tool, result size) results in a row; 14 of 119 digests show a premise that did not reproduce | `usage.json` flags (117 of 119 digests); FAILED markers; coordinator TERMs; the verifier's word on the lane's work; the rule's flags with the coordinator's response; Qwen labels on windows | AF-AP-171 (no edit and no report growth for 30 min), OR 3+ identical results in a row | RWKV stream reader on the PC CPU (one result per 39 s per local lane; CPU speed unmeasured) | medium for the rule path; large for RWKV |
| B4 | 57 NOT-READY of 93 recommendations (JEV-MAP D27); 40 of 257 dispatches name a repair round (R23); my partial parse finds 6 of 31 BLOCKERs citing a registry row. Rounds saved: unmeasured | DSV2 ap rows (D-085: cited = true, uncited lexical top 16 = false, held out by incident) | lexical order (J2: 26 of 49 top-1) | Laya per block (rank) | small, once a checkpoint beats lexical |
| B5 | 34 lanes timed out the 60-minute poll (R24). Lane span: local median 111 min, p90 280; cloud 55 and 130 (digests). A landing sat unharvested for an hour (INCIDENT-LOG:218) | none | none | a rule is enough | tiny |
| B6 | report 45, patch 43, timed out 34, premise gate 8 (R24); `usage.json` failed 1 of 117 | runner markers | B3's rule | RWKV, after B3 | large |
| B7 | 57 / 22 / 4 / 2, plus 8 with no word; red runs do not separate the classes (D27) | the recommendation word | majority class, 57 of 85 | RWKV | medium; payoff unmeasured |
| B8 | 28 repair-round reports; 9 carry 110 cross-round references; RP-30b ran seven rounds (`contract-gate/SKILL.md:76-78`) | those references | same anchor and token overlap | Laya rank | small; labels thin |
| B9 | 64 failures in 131 stage0-ci runs seen (R19). The recorded causes are deterministic and now blocked at commit (`scripts/hooks/pre-commit:42-83`). No separation at n = 43 (JEV-MAP 2.7) | none | none | a rule is enough; a gate file in any case | small |
| B10 | 67 commit blocks; the command text decides 8 of 10 future-stamp blocks; 14 of 14 dirty-tree refusals are visible beforehand (JEV-MAP 2.4, 2.6) | none | none | a rule is enough | none |
| B11 | 29,211 PC tool results carry no outcome (DATA-SESSION 6.1); UNCOVERED is 39 of 900 sandbox errors (R3) | the family map | the family map | rule, plus the Laya column already built | small, with the corpus |
| B12 | Before the lint existed: wrong line references CK10 13, CK11 17 of 35, D5i 11 of 22, B5g 6 of 8 (`report_lint.py:4-6`) | none typed | `report_lint`'s token match | Laya per block | small; unmeasured |
| B13 | medium gives about 95% of xhigh's substance at 1/2 to 1/7 of the thinking (one A/B pair, `pc-lane.sh:423-424`) | one pair | the role default | Laya | medium; unmeasured |

## 2. Ranked top five (payoff against build size)

| Rank | Point | Fit | Build | Why |
|---|---|---|---|---|
| 1 | B1 KV-budget admission | rule | small | protects every local lane; 4 starvations and 76 preemptions recorded; the 10-minute heartbeat cannot see the 80-100 s wait |
| 2 | B2 context diet | rule | small | 4.31 M characters of skill loads since 09-04, plus large reads; smaller lanes let B1 admit more |
| 3 | B3 lane progress watch | rule now, RWKV next | medium, then large | the largest recorded GPU waste (about 3.8 h); 32 lanes at risk; the one stream where a stream reader beats both Laya and rules |
| 4 | B5 poll budget | rule | tiny | 34 re-attaches and delayed harvests |
| 5 | B4 verify attack ranking | Laya rank | small (needs a checkpoint) | the verify round is the costliest loop; labels exist |

**B1.** Fold vLLM's metrics read into the same bridge call as `free -m; df` (`pc_lane.sh:231`). Defer when live local lanes × 90k + 90k > 0.9 × 222,822, or when any request is waiting. The median local lane averages 86-89k prompt tokens per call and p90 is 135-139k, which is why two lanes fit and a third starves. Qwen teacher jobs are tenants of the same budget, and they call vLLM directly (D-082). Like the other probes, an unreadable KV fails open (`:100-102`).

**B2.** The runner tells every lane not to call `skill_view` unless the brief names the skill (`pc-lane.sh:243`), but only in the prompt. A rule at the hook enforces it as a one-turn-late nudge, the same path the edit snapshot uses.

**B3.** Build the rule path first:
- split the recorder from its `pre_verify` nudge (both sit behind one switch, `lane-profile.sh:127`);
- forward the switch, which is missing from `pc_lane.sh:346`;
- commit the heartbeat with AF-AP-171's progress fields.

Its flags, plus the coordinator's response to each (stop or let run), become the labels. The RWKV reader then keeps one saved state per lane and asks the class question from a copy after each fact. Laya's 1,024-token window sees only the last few events. The watcher runs outside the 20 s hook timeout; the hook only appends a fact. It must run on CPU: vLLM holds about 95% of the 3090 (AF-AP-201), and running beside it is unmeasured.

**B5.** Set the poll budget to the route's p90 lane span (local about 280 min).

**B4.** Ships as a pack section only after a Laya checkpoint beats the lexical order on the held-out DSV2 ap rows.

## 3. Shared infrastructure area B needs

1. **The lane fact recorder, on for every lane.** It is `lane-done-gate.py record`, with its matcher extended to all tools and result sizes. It already parses each exit code (`:110-125`) and writes a 0600 file in the PC temp directory (`:54-58`).
2. **PC Jev services.** The Laya CPU service exists (`harness-ports/bin/laya-server.sh`, 127.0.0.1:47411, 8 threads) but answered 2 calls in 16 h (JEV-LEVERAGE §1). An RWKV stream-state server is not built. It needs per-stream saved state, append, and ask-from-copy. Measure its CPU speed before anything depends on it. Never probe vLLM with options that allocate per prompt token (AF-AP-201).
3. **A label log.** The J1 ledger exists (`src/agent_factory/decisions/ledger.py:335` `make_row`, `:432` `append`), but its question set is closed (`scripts/decide-harvest:25-33`). New question ids (lane progress, lane end, attack row, same finding) need schema entries in `volatile.py`. Join them with `.jev/calls.jsonl`.
4. **A PC-only corpus.** Run `hermes-session-export.py` with `tool_body_cap > 0` (`:44-46`). It scrubs, then caps (`:36-41`); the output stays on the PC and is never committed. This fills the 29,211 unlabeled results.
5. **A committed heartbeat** that reads `watch.json`. It is not a gate file.

Secrets: the lane streams never leave the PC, and `watch.json` holds only classes and counts. `jev.rank` scrubs, then caps, everything it sends. System 1 calls go to local servers directly (D-082).

## 4. Carry-over to the agent factory

The factory's runtime is Hermes on the PC (standing rule 1). Every area-B Jev seam is therefore a Hermes seam: the `post_tool_call` observer and the spool into `pre_llm_call`, the advisory path JEV-MAP names for the factory (D33, D35). The recorder, the diet rule and the lane watch carry over as they are: a factory agent session is a lane with another brief. The same typed questions and labels apply, which is the "3 birds, 1 stone" of D-084. KV-budget admission becomes the factory's admission control for local model servers. Attack ranking and finding dedup fit the improvement plane as advisory triage for JIT and AlphaEval reviewers, never inside the promotion gate. No Jev value enters the fail-closed `pre_tool_call` (standing rule 9, KC-J1).

## 5. Unmeasured

- RWKV speed on the PC CPU, and running it beside vLLM.
- The GPU time lost to the 76 preemptions.
- How many of the 32 at-risk lanes were really wasting time (per-window labels do not exist yet).
- Rounds B4 or B8 would save.
- My BLOCKER parse covers only 27 of 133 reports.
- Lane spans come from each lane's final session only; the digests' timestamps are not monotonic, so I used first to last.
- Every digest-derived count is a floor, because lost attempts leave no digest.

### Critical Files for Implementation
- /home/user/agent-factory/scripts/pc_lane.sh
- /home/user/agent-factory/harness-ports/bin/lane-done-gate.py
- /home/user/agent-factory/harness-ports/bin/lane-profile.sh
- /home/user/agent-factory/harness-ports/bin/hermes-hook-adapter.py
- /home/user/agent-factory/scripts/lane_context.sh