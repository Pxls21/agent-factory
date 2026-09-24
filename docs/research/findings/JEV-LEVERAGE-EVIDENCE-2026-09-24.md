# JEV LEVERAGE RE-AUDIT — EVIDENCE (task #221, D-069 item 5)

| Field | Value |
|---|---|
| Date | 2026-09-24 UTC, commands run 11:10Z-11:55Z |
| Model | claude-opus-5-5 (sandbox evidence lane) |
| Repo HEAD read | start `9924dd2` (`git rev-parse --short HEAD`, 11:10:20Z). HEAD moved during the lane: to `200ed95` (the screen and its test, ledger, decision log, briefs, digest, live-state) and then to `ee3c8c1` (one CLAUDE.md line, `harness-ports/bin/mojev-stage.sh`, findings, briefs, ledger, live-state). Cells on changed files were re-read and name the HEAD. CLAUDE.md keeps 803 lines at both. |
| Transcript snapshot | `/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl`, first 651,687,566 bytes (size at 11:23:49Z; the file grows) |
| Marks | SOLID = primary source read or measured here. UNSURE = one document's claim, an inference, or my own judgment (named). |
| Instruments | graft `ask`/`skeleton`; `git grep`/`grep`; python module loads (bytecode off); stream parsers (E4.3). No bridge, network, subagent or commit. |

Evidence only: no proposals, no verdicts. Contradictions carry both sides. Short dates are 2026-09-DD.

## E1. What Jev is here

### E1.1 Laya and the loopback endpoint

| # | Cell | Value | Evidence | Mark |
|---|---|---|---|---|
| 1 | Model | HF `convaiinnovations/laya`, subfolder `typed-decisions`, revision `1c5edc17a7acd8701df6fc341c0d179f1c62c982` | `scripts/laya_systemone_server.py:30,63,208` (6406750, 09-23); `harness-ports/bin/laya-server.sh:15-16` (6406750) | SOLID |
| 2 | Encoder | `answerdotai/ModernBERT-large`: 28 layers, hidden 1024, `max_position_embeddings` 8192 | local snapshot `/root/hf-laya-probe/.../typed-decisions/rl_agent_config.json`, `encoder/config.json` | SOLID |
| 3 | Size | 421,293,830 parameters in 206 tensors, stored F16; `model.safetensors` 842,609,220 bytes; blob sha256 prefix `4fa56de72383a9d3` = `LAYA-PROBE-1.md:6` | safetensors header summed (python); `stat -L` | SOLID |
| 4 | Input window | config `max_len = 1024`, `head_max_len = 256`, `max_tokens_per_batch = 4096` | `rl_agent_config.json` | SOLID |
| 4a | Contradiction | "typed-decisions checkpoint (1024)" vs "Laya's 512-token window" | `docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md:16,26` (fb90a0d) vs `MOJEV-AUDIT-2026-09-24.md:18,58` (817509b) | quotes SOLID |
| 5 | Runtime | FP32 on CPU via `laya.load(...)`, `Agent.system_one` | `LAYA-PROBE-1.md:6` (8804c26) | SOLID |
| 6 | PC endpoint | user unit `laya-systemone`, `127.0.0.1:47411`, `--threads 8`, `--device auto` -> CPU (`auto: CUDA memory probe failed (out of memory)`); `Restart=on-failure`, `StartLimitBurst=3` | `laya-server.sh:10-16,36-46`; ledger `todo/BUILD-TASKLIST.md:171` | code SOLID; live state now unknown |
| 7 | Routes | `GET /health` -> 200 `{ok, snapshot, subfolder, calls, device, device_reason, revision}` / 503 `{ok:false, reason}`; `POST /v1/systemone`; other paths 404 | server `:161-172` | SOLID |
| 8 | Request | `{"model": <ignored>, "state": <str/dict/list>, "questions": {id: {"type": "noul"/"choice"/"score", "instructions", "criteria": {label: text} or [labels]}}}`; body 1 B-8 MiB (413 above; 400 empty, malformed, wrong shape); bearer not checked | server `:4-5,15-16,29,173-184`; caller `docs/research/findings/pijev-order-probe/order_probe.py:20-38` (25896e4); `tests/fixtures/decisions/probe/questions.json` (b67a813) | SOLID |
| 9 | Response | 200 `{"model", "answers": {id: {...}}, "usage": {"input_tokens","output_tokens"}, "latency_ms"}` (+ `"fan_out"`); a choice answer: `choice`, `probabilities`, `confidence`, `action.act_probability`; 500 model error, 502 ids differ, 503 not loaded | server `:130-144,185-200`; `PIJEV-ORDER-PROBE-1.md:36` | SOLID |
| 10 | Per-chunk fan-out | ids that all name `state.chunks` entries -> one model call per chunk; docstring: a batch answered 0.598 for three unlike chunks | server `:8-14,118-144` | code SOLID; 0.598 UNSURE |
| 11 | Concurrency, bind | one forward pass at a time (`State.lock`); a non-loopback host is refused (rc 64) | server `:189,213-215` | SOLID |
| 12 | Live PC unit (read 09-23) | loopback-only listener; uid `rocco`; HF offline flags set; no outbound sockets; `ExecStart` points into the ephemeral lane tree `.lanes/pc-jev-laya-pc.md--dd4c579/tree/` (AF-AP-122) | `tasks/briefs/pc-t90-support/VERIFY-T92-T90R3-PCJ1-report.md:283,291-294` (b91673e) | SOLID for that read |
| 13 | Latency (J0) | sandbox p50 259.67 / p95 357.76 / max 872.25 ms (n=1400, 4 pinned threads); PC p50 336.18 / p95 461.70 / max 510.41 ms; PC per-type p50 291.88 (d1) to 456.23 (b1.finding_kind); filed: sandbox SYNC-OK, PC ASYNC-ONLY | `LAYA-PROBE-1.md:21-37,54-70` | SOLID (filed) |
| 14 | Determinism (J0) | 3 identical digests `e39555ce...` per venue, the third from a fresh process; the same digest on both venues | `LAYA-PROBE-1.md:33-38,66-71` | SOLID (filed) |
| 15 | J0 fixture | 226 states, mean 107.3 tokens, 7 question types; its states name 84 distinct paths, 13 exist in the tree | `LAYA-PROBE-1.md:7`; python count | SOLID |
| 16 | Contradiction (latency) | audit spike ~1.0-1.25 s per question (512 input tokens per pair) vs J0 p50 260 / 336 ms (107-token states) | `JEV-LAYA-AUDIT-2026-09-22.md:25,108-127` vs row 13 | both SOLID as filed |
| 17 | PCJ1 smoke | PC and sandbox nouls identical `0.4177/0.6723/0.4843`; PC first request 25.3 s, second 0.94 s | ledger `:171` | UNSURE (ledger) |
| 18 | Sandbox route | loopback bind (row 12); the committed caller ran "on the PC as user rocco" (`PIJEV-ORDER-PROBE-1.md:7`), i.e. via `scripts/pc.sh` | rows 11-12 | "bridge only" UNSURE (no route probe) |
| 19 | Sandbox endpoint now | none: `/proc/net/tcp` has no port 0xB933 (80 rows); `pgrep -f 'laya_systemone_server[.]py'` rc 1; venv and HF cache exist under `/root`; 0 matches for `laya/47411/systemone/jev` in `setup.sh`, `resume-heal.sh`, `install_session_hooks.py`, `pc.sh`, `pc_bridge_exec.py` | commands 11:13Z | SOLID |
| 20 | Files naming 47411 | 28 (`grep -rln 47411 .`); code: server `:206`, `laya-server.sh:12`, `jev-pruner-setup.sh:9-10`, `order_probe.py:5`, parked `long-output.sh:24` | `grep -rn` | SOLID |

### E1.2 MoJev (`docs/research/findings/MOJEV-AUDIT-2026-09-24.md`, 817509b, a static reading)

| Cell | Value | Evidence | Mark |
|---|---|---|---|
| Kind, output | typed-decision scorer on the `system_one` shape; one softmax over the caller's candidates per question; no text (`output_tokens: 0`) | `:10-11,31` | SOLID (audit) |
| Size | Qwen3.5-0.8B base, 854,036,544 parameters; bf16 encoder, fp32 readout; 18 Gated DeltaNet + 6 full-attention layers | `:32-33` | SOLID (audit) |
| Window | trained at 16,384 tokens; no YaRN; no bound check; over-long state cut silently | `:12-14,34` | SOLID (audit) |
| Limits | dense mask 4*L^2 bytes (1.07 GB at 16k, 32.4 GB at 90k); <=16 candidates trained; order moves scores; 93.23% claim on own synthetic data, `verified: false`; no code domain | `:35-43,107-127` | SOLID (audit) |
| CPU speed | not measured; estimate "about a minute per 16k-token decision" | `:112-115` | UNSURE |
| In the tree | `git grep -i -l -E 'mojev/PackedScorer'` over scripts, src, tests, harness-ports, proofs, .claude/hooks: 0 at 9924dd2; 3 at ee3c8c1: the screen and its test (vocabulary, D-071, `docs/08_DECISION_LOG.md:82`) and `harness-ports/bin/mojev-stage.sh` (6b31bdf, 11:44Z: "clone the pinned code and download the pinned Hub files. Static only", `:2-3`). Owner yes to option B on the PC CPU: D-069 item 3 (`:80`) | commands | SOLID |

### E1.3 jev-pruner and jevcache

| Cell | Value | Evidence | Mark |
|---|---|---|---|
| jev-pruner | plugin `fast-jev-output` @ 47d017c: a `tool.call` function hook on Bash; under 10,000 estimated tokens the result passes; over it, per-chunk noul scores pick the chunks kept and the output is archived behind a footer; any error -> `hook_error`, result unchanged (fail open) | `/root/.claude/plugins/cache/fast-jev-output/fast-jev-output/0.1.0/hooks/fast-jev-output.ts:153-181,280-283`, `src/output.ts:7,259-263` | SOLID |
| Sandbox wiring | `/root/.claude/settings.json`: `enabledPlugins` has `fast-jev-output@fast-jev-output` (+ `aegis@aegis-dev`, `honey@greenpt`); `env` has `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS`; `pluginConfigs` has the plugin key (values not printed) | python key read | SOLID |
| Sandbox engagement | endpoint down (E1.1 row 19); no `.claude/fast-jev-output` archive dir under `/home/user/agent-factory`, `/home/user`, `/root`; snapshot: 0 real pruner footers (8 are the literal `<path>` placeholder in 09-22 audit text, 2 the `${path}` source template; E4.3 side script) | `ls`; E4.3 | count SOLID; "never engaged" UNSURE |
| Hermes lanes | `harness-ports/bin/pc-lane.sh`: 0 matches for `jev/laya/prun/systemone/typesafe`; `git log -S JEV_PRUNER_RUN` / `-S jev` on it: no commit | commands | SOLID |
| Decision | D-053: PARKED for Hermes lanes. Measured: it engages only after its own Codex PreToolUse hook writes `~/.cache/jev-pruner/codex/<id>.json`, which Hermes never does; 20,000 lines came back whole, `calls` unchanged (AF-AP-121); also a fixed 30 s deadline vs up to 25,000 state tokens on CPU | `docs/08_DECISION_LOG.md:64`; ledger `:171` | SOLID |
| PC tooling | `harness-ports/bin/jev-pruner-setup.sh` (6406750): clone @ 47d017c, patch the Codex client to read `JEV_BASE_URL` (`:34-59`), build, smoke | file | SOLID |
| jevcache | `hyperspaceai/jevcache` @ a211d13: README only, no source, no LICENSE, no checksum, a `curl | sh` binary; replaced by the first-party ledger (D-041 = J1); `command -v jevcache`: none | `JEV-LAYA-AUDIT-2026-09-22.md:52`; `docs/08_DECISION_LOG.md:52` | SOLID |

### E1.4 The never-a-gate mechanics (KC-J1)

| Cell | Value | Evidence | Mark |
|---|---|---|---|
| KC-J1 | absorbing barrier: `laya`, `systemone`, `system_one`, `decide ask`, `sieve`, `jev` in a gate-defining file, or a Laya value reachable from a gate/merge/lint/commit/push/proof predicate, pulls the layer | `docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md:45` (ec50851, 09-22) | SOLID |
| KC-J1b | a Laya score is never the sole evidence for an AF-AP row or a verifier per-finding class | `:46` | SOLID |
| Screen | `scripts/no_laya_in_gates.py` (1460 lines at 200ed95): rc 0 clean, 3 violation, 4 completeness, 64 usage | `:4-10` | SOLID |
| Vocabulary, 200ed95 | `SIMPLE_TOKENS` (`:65`): decide-harvest, decide_harvest, jev, jevcache, laya, laya-decide, mojev, packedscorer, sieve, sieve-run, system-one, system_one, systemone; whole maximal runs of `[A-Za-z0-9_-]`, case-insensitive (`:1172,1185`); `DOTTED_TOKENS` (`:73`): agent_factory.decisions, decisions.ledger, decisions.canonical, decisions.jsonl; `.py` import check (`:1176`). At 9924dd2 the same without `mojev`, `packedscorer` (added by 200ed95, D-071) | python module load, both HEADs | SOLID |
| Measured misses | `_check_line` returns `[]` for `jev-pruner`, `JEV_PRUNER_RUN`, `JEV_BASE_URL`, `fast-jev-output`, `127.0.0.1:47411`, `laya-server.sh`, `laya_systemone_server.py`, `pijev`, `canny`, `winnow`, `typesafe`, `noul`, `ap-hawk`, `drift-hawk`, `decide ask`, `system one`; hits: `jev pruner` -> jev, `/v1/systemone` -> systemone | python, 200ed95 | SOLID |
| Contradiction | KC-J1 lists `decide ask`; the screen has no `decide`/`ask` token (`'decide ask'` -> `[]`) | rows above | SOLID |
| Listed files | `scripts/gate_files.txt` (0e7b6c3): 3 git hooks, 2 workflows, 16 gate scripts, `pc-lane.sh`, 13 proof checkers, 4 modules, `edit-snapshot.py` | `:5-53` | SOLID |
| Include edges | `source`/`.` only via `ALLOWED_SOURCES` (`:97`); imports to stdlib, `EXTERNAL_MODULES` (`:87`) or listed files (`:12-27`). Not followed (declared): EXEC edges, "17 literal exec edges ... reach 15 repo scripts, 9 of them unlisted" (`:31`) | docstring | SOLID |
| Wiring | `scripts/hooks/pre-commit:127` runs it `--staged` (8d50443) | file | SOLID |

## E2. The existing Jev roadmap and its state

| Item | Status text (file:line) | Files that exist | Absent (command) | Mark |
|---|---|---|---|---|
| #115 ap-hawk | ledger `:150`: "the AP-HAWK ... -> D-046 PROPOSED ... Measured: 28 of 116 rows have a mechanical screen signature ... labels = 56 incident entries naming their row + 202 report mentions of 47 rows. Disposition: advisory injection only (KC-J1), two-stage"; D-048 (`docs/08_DECISION_LOG.md:59`): first inference point after J0/J2 | `ap.violates_row` schema `src/agent_factory/decisions/volatile.py:276-287` (fdac751), `scripts/decide-harvest:26`; 121 harvested rows | #115 not in the ledger (`grep -n -E '#115\b'`: 0); hawk code: `git grep -i -l hawk` over scripts, src, tests, harness-ports, proofs, .claude/hooks: 0 | SOLID |
| #116 drift-hawk | ledger `:151`: "the DRIFT-HAWK ... -> D-047 PROPOSED ... `wf.drift` added to J1's harvest as a capture type; advisory only"; D-048: second | `wf.drift` schema `volatile.py:288-`; `decide-harvest:32`; 3 harvested rows | #116 not in the ledger; hawk code 0 | SOLID |
| #133 pijev | ledger `:178`: "PIJEV MEASURED ON LAYA (D-050) ... tasks #132 / #133"; D-050 (`:61`): permutation averaging is a scored arm of J2, its core to be ported | `docs/research/findings/PIJEV-ORDER-PROBE-1.md`, `pijev-order-probe/order_probe.py` (25896e4) | port: `git grep -i -l -E 'pijev/permutation.averag/label-aligned mean'` over code dirs: 0; J2 files: 0 | SOLID |
| #195 dream triage | ledger `:1357`: "D-058 RECORDED ... (task #195 created, pending)"; D-058 (`:69`) PROPOSED: "NOT built; nothing is scheduled before Stage 5" | `docs/11_DREAM_PHASE.md:99` (section 9) | `dp.*` types in src/scripts: 0; `dream` in .py: only `tests/test_s0_05_egress.py:729` "NOT run: dream-foundry — unit does not exist" | SOLID |
| Canny C1 (#147, #149, #159, #160) | ledger `:201` C1 LANDED (GATED-PENDING-VERIFY); `:212` C1-R1 LANDED; `:217` "VERIFY-C1-R1 HOME — MERGE-READY-WITH-FOLLOWUPS; the coordinator's gate GOOD-STATE (task #160 closed; issue #33)"; D-052 (`:63`): port the deterministic core, "No Jev in either" | `scripts/verify_command.py` (0e1deb2), `tests/test_verify_command.py` | — | SOLID |
| Canny C2 (#148) | brief: "in progress". Ledger `:1379`: "C2 LANDED (task #148, the lane done-gate; GATED-PENDING-VERIFY, switched OFF)"; "C1's classifier recognises 0 of the 109 witnessed lane commands"; `:1382`: VERIFY-C2 on `gemini-3.1-pro-low` only, "mutants were reasoned, not executed, so C2 STAYS GATED-PENDING-VERIFY" | `harness-ports/bin/lane-done-gate.py`, `harness-ports/tests/test_lane_done_gate.py` (3a45568); `lane-profile.sh:116` reads `LANE_DONE_GATE`, default 0 | neither dispatcher sets `LANE_DONE_GATE` (`grep`: 0) | SOLID; brief and ledger differ |
| J0 (#123) | commit 8804c26: "J0 done (ASYNC-ONLY and DETERMINISTIC on the PC; task #123 closed)" | `scripts/laya_probe.py`, `LAYA-PROBE-1.md` + JSON | — | SOLID |
| J1-0 to J1-5 | `tasks/laya-j1-breakdown.md:4` (2c09db3): "J1-0 VERIFIED (J1-0-R6), J1-2 GOOD-STATE (D-034), J1-3 VERIFIED (J1-3-R1), J1-4 and J1-5 VERIFIED (VERIFY-J1-45 ...). J1-1 NOT-READY: its redaction pass waits for the owner's redesign decision (D-068, task #198)". At 200ed95: D-070 (`:81`) span-union redesign, J1-1-R4 dispatched, task #223 `jev-leak-hunter` (ledger `:1430-1431`) | J1 table below | — | SOLID |
| PCJ1 (#124) | ledger `:164` dispatched; `:171` "THE ENDPOINT HALF LANDED, GATED-PENDING-VERIFY; THE PRUNER HALF NOT WIRED, BLOCKED ON AN OWNER DECISION"; `:1364` "T92 AND PCJ1 ACCEPTED WITH FOLLOW-UPS"; D-053 parks the pruner | server, `laya-server.sh`, `jev-pruner-setup.sh`, `tests/test_laya_systemone_server.py`, `tasks/briefs/jev-laya/PCJ1-report.md`, `tasks/briefs/jev-laya/parked/` | pruner wiring in `pc-lane.sh`: 0 | SOLID |

**J1, the decision ledger**

| Cell | Value | Evidence | Mark |
|---|---|---|---|
| Row | `calibration_state, checkpoint_digest, incumbent_answer, producer, question_id, row_digest, row_id, source_ref{kind,path,source_digest,locator}, state, state_digest`; each row an INCUMBENT decision (`calibration_state="incumbent"`, `checkpoint_digest="none"`); append-only JSONL, one writer; source kinds transcript_jsonl, lane_report, verify_report, incident_log, registry | `src/agent_factory/decisions/ledger.py:1-6,46-67` (f0e431f) | SOLID |
| Types (7) | ap.violates_row, b1.finding_kind, b1.finding_sev, b2.hit_role, d1.bug_echo_scores, v1.finding_class, wf.drift | `scripts/decide-harvest:25-33` (0d62801); `volatile.py:244-300` | SOLID |
| Grammars | incident log -> ap.violates_row (`decide-harvest:332-360`); verify reports -> v1.finding_class via `BULLET_FINDING_RE` BLOCKER/FOLLOW-UP/INFO/UNVERIFIED/CONTRACT-DEFECT/KNOWN (`:45-48,400-510`); lane reports -> wf.drift via `BOUNDARY_RE` (`:49-53`), d1 rating tables (`:511-609`); transcripts -> b2.hit_role (hive-scout), b1.* (hive-reviewer) (`:627-768`) | `grep -n '^def '` (no .py suffix, graft skips it) | SOLID |
| Latest real harvest | "harvest: 235 rows, per question type: ap.violates_row=121, b1.finding_kind=0, b1.finding_sev=0, b2.hit_role=0, d1.bug_echo_scores=0, v1.finding_class=111, wf.drift=3"; "refused: 39 records"; "yield below KC-J7's 200 for every type" | `tasks/briefs/laya/J1-3-R1-report.md:1,501` | SOLID |
| Committed rows | none: no ledger JSONL in `git ls-files`; `find` over the repo, `/root`, `/tmp` (depth 6): only pytest temp ledgers `/tmp/j12m*`, `/tmp/j12n5*` | commands | SOLID |
| Consumers | only non-test importer: `scripts/decide-harvest:21-22` (`git grep agent_factory.decisions -- ':!tests/' ':!*.md'`); graft "callers of make_row" / "callers of append": tests only; nothing in scripts, harness-ports, .claude/hooks, .github runs `decide-harvest`; ledger `:1420`: "the ledger has no consumer; `scripts/decide-harvest` runs only by hand" | graft + git grep | SOLID |

## E3. System-1 decision inventory

File dates (last commit): contract-gate 4313a3b 09-16; build-loop, deep-work b318135 09-24; orchestration, evidence-gatherer.md f83aa36 09-24; adversarial-review, code-intel-trio 55ed79e 09-17; session-continuity 06b1d24 09-03; anti-hollow-green bfe66ec 09-24; bug-echo 3c0d49e 09-02; wiki-compiler 85433db 09-03; adversarial-verifier.md 6914400 09-23; wiki-context.py, session-start.sh 3c0d49e 09-02; graft-first-nag.py d201f8a 09-15; turn-retro-gate.sh 1e8ecee 09-03; edit-snapshot.py de06db6 09-24; report_lint.py, ap_screen.py ea18960 09-23; lane_context.sh 838c188 09-15; ci_gate.py, stage0-ci.yml, push_clean.sh 5689d9f 09-23; verify_command.py 0e1deb2 09-23; lane-done-gate.py 3a45568 09-23; decide-harvest 0d62801 09-24; pc_lane.sh, pc-lane.sh 1a94bbb 09-23; chat_tail.py, orient.sh b3ef7da 09-03; transcript_export.py 5415c2a 09-23; lint_delta.py 097b0e3 09-03; stamp_check.py 8d50443 09-23; lane-skills.txt f2e94ee 09-03; CLAUDE.md a12e672 09-24. Skill paths are `.claude/skills/<name>/SKILL.md`; hooks `.claude/hooks/`. Locations and texts SOLID; a label source marked "partial" is UNSURE.

| # | Location | Decision | Inputs | Output | Mechanism | Real label source |
|---|---|---|---|---|---|---|
| S1 | contract-gate `:114-121`; build-loop `:11-20` | route the verify apparatus by change class | diff | 3-way | model judgment | none found |
| S2 | contract-gate `:56-66`; `.claude/agents/adversarial-verifier.md:12,43,80-88` | blocking predicate met; finding class | finding, contract, repro | k-way BLOCKER/FOLLOW-UP/INFO/UNVERIFIED/CONTRACT-DEFECT | model judgment | 89 `VERIFY-*-report.md` + 30 `report-pc-verify-*`; harvested v1.finding_class 111 |
| S3 | contract-gate `:109-112`; adversarial-verifier.md `:94-95` | gate recommendation | findings | 4-way | model judgment; coordinator decides | reports (mentions: NOT-READY 108 in 73 files, -WITH-FOLLOWUPS 93 in 55, CONTRACT-INVALID 71 in 37); ledger grades |
| S4 | contract-gate `:59-66` | may a second repair run | outcome, budget key | binary | rule + authorization | D-056, D-057, D-059, D-063, D-067, D-068 |
| S5 | adversarial-review `:26-28` | verdict; tag | diff, repros | 2-way; 3-way [BLOCKER]/[SHOULD-FIX]/[NIT] | model judgment | as S2/S3 |
| S6 | build-loop `:166-170` | failure: which rung first | failure, trace | ordered pick | model judgment | none |
| S7 | build-loop `:198-204`; deep-work `:193` | real defect (then bug-echo + registry row) | defect | binary | model judgment | 181 AF-AP rows, 191 dated incident entries |
| S8 | deep-work `:14-42` | evidence admissible | claim, source | binary | model judgment | none |
| S9 | deep-work `:46` | exists vs wired | call graph | binary | instruments + judgment | none |
| S10 | deep-work `:83-87` | cheapest order-changing probe | candidates | pick-1 | model judgment | none |
| S11 | deep-work `:129` | follow or suppress a mid-build failure | failure | binary | model judgment | none |
| S12 | deep-work `:234`; orchestration `:245-254` | accept a finding / a delegate refusal | finding, repro | binary | model judgment | reports + ledger (partial) |
| S13 | deep-work `:284-303`; turn-retro-gate.sh `:47-53` | lesson? which skill | the batch | binary + 6-way route | model judgment | later commits to skills (partial) |
| S14 | deep-work `:373-381` | probe live; box contended | ps, loadavg | binary | rule of thumb | none |
| S15 | orchestration `:106-111` | verify partial (low-tier fallback, reasoned mutants) | served mix, report | binary | judgment + model count | ledger `:1382` (one instance) |
| S16 | orchestration `:258-303,428-437` | lane alive / dead / progressing | pid, mtime, heartbeat | 3-way | rule + judgment | AF-AP-45, -87, -171 (partial) |
| S17 | orchestration `:305-307` | which model a lane ran on | OmniRoute `call_logs`, `message.model` | extraction | query | `call_logs` on the PC; transcript fields |
| S18 | orchestration `:310` | boundary holds a listed gate file | boundary, gate_files.txt | binary | lookup | gate_files.txt |
| S19 | orchestration `:189-207` | read the decision off a table; ambiguous escalates | table | lookup | structure | none |
| S20 | session-continuity `:36-52` | fresh / stale summary / rollback / sibling session | three clocks | 4-way | judgment on dates | rollback incident entries (partial) |
| S21 | code-intel-trio `:18,24,84-86` | which instrument; DORMANT needs two | question kind | k-way; binary | table + judgment | none |
| S22 | anti-hollow-green `:14,58,148` | negative control present; mutants survive; claimed part ran | gate, tests | binary each | judgment + mutation runs | kill tables in reports (partial) |
| S23 | bug-echo `:172-198` | response shape by candidate count | count | k-way | count bands | none |
| S24 | bug-echo `:201-221,575` | offer to tighten the pattern | count | binary | threshold >= 25 | none |
| S25 | bug-echo `:274,317` | site class BUG/WATCH/OK/REVIEW | site, pattern | 4-way | model judgment | none (`.agents/research/` absent; d1 rows 0) |
| S26 | bug-echo `:40,388-415` | Urgency, Risk of Fixing, Risk of Not Fixing, ROI, Blast Radius, Fix Effort | a BUG | 6 scores | model judgment | d1.bug_echo_scores 0 rows |
| S27 | wiki-compiler `:78-94` | topics per file; time-sensitive vs stable | content, prior topics | multi-label + binary | model judgment | `wiki/.compile-state.json` (12 topics, 09-03) |
| S28 | `.claude/agents/evidence-gatherer.md:29` | SOLID vs UNSURE | the row | binary | model judgment | none |
| H1 | wiki-context.py `:30-32,58-74` | pages to inject per prompt | prompt tokens (>=3 chars, 44 stopwords), headings, stems, text | ranking -> top 3, one 12-line excerpt each | 3 x heading + 2 x stem overlap, +0.1 x text if > 0 | none found |
| H2 | wiki-context.py `:45-48` | inject live-state | — | first 40 lines, always | fixed | — |
| H3 | wiki-context.py `:55-56` | candidates: INCIDENT-LOG.md + `.agents/research/*bug-echo*.md` | — | set | glob | `.agents/research/` absent: glob matches 0 |
| H4 | graft-first-nag.py `:31-41` | nag a Grep call | pattern, path, glob, type | binary | regex + path prefixes | none (70 Grep calls, unlabelled) |
| H5 | turn-retro-gate.sh `:15-39` | fire the retro | HEAD vs sentinel, subjects, paths | binary | rule + exemptions | git history |
| H6 | turn-retro-gate.sh `:47-53` | 5 items: wiki, bug-echo/registry/screen, skill, tooling, luck | the batch | 5 binary | model judgment | commits to wiki/, INCIDENT-LOG.md, skills (partial) |
| H7 | edit-snapshot.py `:567` | screen this edit | path | binary | `.py`, not `sandbox-kit/` | — |
| H8 | edit-snapshot.py `:122` AP_SCREEN (46), `:351` TEST_SCREEN (16), `:482` | anti-pattern tells in a hunk | hunk | multi-label | regex | 44 of 181 AF-AP ids screened (E4.1) |
| H9 | session-start.sh `:13-15,33-43` | what to inject at start | env, files | `head -60` live-state + `orient.sh | head -80` | fixed | — |
| P1 | `scripts/report_lint.py:64-109` | a `file:line` claim true | claim tokens, lines +/- tolerance | 4-way OK/NEAR/MISS/UNCHECKABLE | token match | verifier-found bad refs (`:3-5`: CK10 13; CK11 17 of 35; D5i 11 of 22; B5g 6 of 8) |
| P2 | `scripts/ap_screen.py:25-29,43` | H8 over whole files | files | multi-label | the hook's lists | as H8 |
| P3 | `scripts/lane_context.sh:60-89` | lane code context | files, question, symbols | extraction cut by `head -80/-60/-12` | fixed truncation, no ranking | none |
| P4 | `scripts/ci_gate.py:234-263` | push allowed | Actions runs, ancestry, paths | 4-way rc 0/1/75/2 | deterministic | CI runs (outside the repo) |
| P5 | `ci_gate.py:10,220-226`; `.github/workflows/stage0-ci.yml:5-14` | push is transcripts-only | changed paths | binary | prefix `transcripts/` | CI history |
| P6 | `scripts/verify_command.py:178-236` | a command counts as a passing check | command | binary | shell segments + regex | its tests; ledger `:1379`: 0 of 109 lane commands recognised |
| P7 | `harness-ports/bin/lane-done-gate.py:85-97,207-226,229-292` | nudge: code changed after the last check | edit/check facts | binary | rules; OFF (`lane-profile.sh:116`) | none (never on) |
| P8 | `scripts/decide-harvest:332-768` | incumbent decisions -> J1 rows | incident log, reports, transcripts | extraction, 7 types | strict grammars | these are the extraction paths |
| P9 | `scripts/pc_lane.sh:92-106` | admit or defer a lane | disk, PC memory, PC disk | binary; admits on an unreachable probe (`:100-101`) | thresholds | admission lines (partial) |
| P10 | `pc_lane.sh:174-177,464-471` | route and effort by role | role, `HERMES_MODEL`, `HERMES_REASONING` | k-way | fixed table | served-mix lines |
| P11 | `pc_lane.sh:193` | premise block present | brief | binary | awk | — |
| P12 | `harness-ports/bin/pc-lane.sh:283-319` | classify a lane's output | first non-empty line | 5-way capacity / quota / safety / persistence / report | `CAPACITY_RX`, `QUOTA_RX`, `SAFETY_RX`, `PERSIST_RX` | `tasks/briefs/pc/report-*.md`; AF-AP-67 |
| P13 | `scripts/chat_tail.py:30-128` | last N user turns + hour histogram | transcript | extraction | rules | — |
| P14 | `scripts/orient.sh:27,45,56` | which transcript; which areas | newest JSONL in `-home-user-agent-factory/` (1,583,665 bytes, mtime 09-22T16:48Z; the live one is under `-home-user/`); commit words | pick + frequency rank | fixed | — |
| P15 | `scripts/transcript_export.py:48,56` | spans to scrub | text | binary per span | `SECRET_PATTERNS` regex | per-class secret tests |
| P16 | `scripts/lint_delta.py:116-158` | new pyflakes hits / AP tells | staged diff | binary | pyflakes + regex | — |
| P17 | `scripts/stamp_check.py:61-105` | stamp later than the clock | staged lines | binary | rule | — |
| P18 | `scripts/push_clean.sh:100-106` | model-id trailers | commit bodies | binary | grep | — |
| P19 | `scripts/no_laya_in_gates.py:1185` (200ed95) | Jev vocabulary in a gate file | text | binary per line | closed list | test fixtures |
| P20 | `harness-ports/lane-skills.txt` | skills a lane loads | curated list | subset | fixed | — |
| C1 | `CLAUDE.md:80-104,135-138` | model and venue per stage | stage | k-way: plan Fable; explore Opus 5.5; verify local Qwen (Opus 5.5 fallback); build Hermes on PC (code-implementer fallback); sweeps Haiku | table + judgment | served-model lines; `message.model` (E4.3) |
| C2 | `CLAUDE.md:122-124` | escalate a tier (spine/gate/security, failed review, cross-file) | paths, history | binary | judgment; "spine" in no script (`git grep -i '\bspine\b' -- scripts harness-ports/bin .claude/hooks`: 0) | none |
| C3 | `CLAUDE.md:79,423` | lane count; overflow route | capacity, KV, cloud status | count + route | rulings + measurements | refusal lines; AF-AP-146 |
| C4 | `CLAUDE.md:127-134` | vocabulary class off Fable after a safeguard flag | flag | binary + route | rule | incident log |
| C5 | `CLAUDE.md:64-70` | chat format by content | message | 3-way | judgment | none |
| C6 | `CLAUDE.md:46` + table | honey mode per role | role | 3-way | table | none |
| C7 | `CLAUDE.md:227-256` | ground-truth doc | question | ordered pick | fixed order | — |
| C8 | `CLAUDE.md:405` | a quirk to write down | event | binary | judgment | 17 "bit" markers at ee3c8c1 (E4.2) |
| C9 | `CLAUDE.md:563-565` | status class; ledger denominator | outcome | 3-way; 4-way | judgment | ledger lines |
| C10 | `CLAUDE.md:574-576` | invoke deep-work | task | binary | judgment | none |
| C11 | `CLAUDE.md:681-688` | graft or grep | question | binary | judgment + H4 | none |
| C12 | `CLAUDE.md:743-744` | DORMANT needs two instruments | claim | binary | rule | none |
| C13 | "is a push transcripts-only" | not a CLAUDE.md line (`git grep -i -E 'transcripts?[- ]only'`: 17 files, none CLAUDE.md); lives in P5 | — | — | — | — |

## E4. Hiccup and quirk corpus

### E4.1 ANTI-PATTERN REGISTRY (`docs/INCIDENT-LOG.md`, 9924dd2)

- 181 rows, `AF-AP-1` to `AF-AP-181`, no gap, no duplicate (python over `^\| *AF-AP-\d+ *\|`). Cells per row vary (5: 142, 4: 24, 3: 6, 6-9: 9), so status is not tallied.
- Screens (python load of `edit-snapshot.py`, de06db6): AP_SCREEN 46 entries = 31 AF-AP ids + 15 inherited `AP-*`; TEST_SCREEN 16 = 14 AF-AP + 2 inherited; AF-AP-139 in both. AF-AP ids with a screen: 44 of 181; without: 137. `ap_screen.py` reuses the lists (`:25-29`), no rules of its own. Ledger `:150` (09-22) said "28 of 116".
- Classes are mine, set after reading all 181 mechanism cells; one per row; single rater, so each assignment is UNSURE. Ambiguous (second class): 21 (A), 47 (I), 79 (F), 90 (J), 116 (A), 121 (G), 128 (G), 146 (J), 147 (A), 152 (F), 154 (G), 180 (I).

| Class | Rows | Screened | Unscreened | Examples | All ids |
|---|---|---|---|---|---|
| A hollow green / weak oracle | 55 | 11 | 44 | 36 mint before mutants; 170 MERGE-READY over un-run items | 1,2,10,12,13,14,18,20,22,24,28,29,31,36,38,40,42,48,52,57,59,60,63,64,65,66,71,74,78,80,83,84,85,96,99,100,101,107,109,114,121,128,133,138,139,151,156,158,160,162,166,170,173,174,179 |
| B stale / unverified premise | 15 | 2 | 13 | 37 hand-typed counts; 172 hook registered where the harness does not look | 4,6,32,37,73,102,111,113,118,123,131,146,154,164,172 |
| C race / TOCTOU / ordering / stale state | 17 | 6 | 11 | 70 classify-then-open; 148 hook runs gate code a lane edits | 21,43,46,53,55,58,70,79,94,105,106,140,147,148,167,175,181 |
| D shell / quoting / encoding | 11 | 2 | 9 | 89 remote `$(...)` expanded locally; 163 relative path after `cd` | 5,75,86,89,93,108,119,129,132,134,163 |
| E secret handling / redaction | 9 | 5 | 4 | 35 keyed on the value; 127 bound before redaction | 7,35,39,95,127,149,152,157,161 |
| F parser / guard / contract shape | 25 | 8 | 17 | 25 regex where a parser is needed; 120 closure stops at the file | 23,25,26,41,47,49,50,51,61,72,88,115,116,120,135,136,137,143,144,153,159,165,176,177,178 |
| G tooling / environment / venue | 25 | 4 | 21 | 92 `pc.sh` re-run past 120 s; 104 sqlite misses WAL rows | 8,11,15,44,54,62,69,77,81,82,90,91,92,97,98,103,104,112,117,125,130,141,142,168,169 |
| H process lifecycle / liveness | 8 | 6 | 2 | 34 kill by name; 171 heartbeat reads only liveness | 33,34,45,68,87,110,145,171 |
| I coordination / lane process | 13 | 0 | 13 | 3 uncommitted work at dispatch; 126 CI run not read | 3,9,16,27,30,56,67,76,122,124,126,150,155 |
| J context / compaction | 3 | 0 | 3 | 17 compaction prunes role text; 180 reply echoes injected context | 17,19,180 |
| Total | 181 | 44 | 137 | | |

Screened ids: A 12,36,38,40,48,57,59,60,71,80,139 · B 37,118 · C 43,55,58,70,175,181 · D 89,132 · E 35,39,127,149,152 · F 25,41,61,72,115,144,159,177 · G 11,44,117,141 · H 33,34,45,87,110,145.

### E4.2 CLAUDE.md quirk markers (a12e672 to 200ed95; re-read at ee3c8c1)

`grep -c 'bit 2026-' CLAUDE.md` -> 13 lines; `grep -o 'bit 2026-[0-9-]*' CLAUDE.md | wc -l` -> 15; `grep -o -E '\bbit (2026-[0-9-]+|twice|live|once|three times)' CLAUDE.md | wc -l` -> 16 at 200ed95 (15 dated + "bit twice 2026-09-08"), 17 at ee3c8c1 (6b31bdf adds "bit twice 2026-09-24" on line 335: an `anchor_edit` `@file` TEXT ending in a newline inserts an extra blank line; class G). Classes use E4.1's letters (my assignment, UNSURE). Totals at ee3c8c1: G 12, D 3, B 1, H 1.

| Line | Date | Quirk | Class |
|---|---|---|---|
| 112 | 09-23 | agent definitions read once per session (AF-AP-131) | G |
| 335 | 09-08 | `anchor_edit.py`: mutation and commit never share a call | G |
| 335 | 09-22 | `anchor_edit.py`: a value starting with `@` is a file path | D |
| 335 | 09-22 | `anchor_edit.py`: an `@file` OLD carries the trailing newline | G |
| 335 | 09-24 (twice; ee3c8c1 only) | `anchor_edit.py`: an `@file` TEXT ending in a newline inserts an extra blank line | G |
| 417 | 09-03 | `push_clean.sh` refuses a dirty tree | G |
| 418 | 09-07 | `--lanes-live` with an empty list refuses silently | G |
| 420 | 09-21 | a PIN must be the post-push SHA | B |
| 421 | 09-21 | a trailing `&` backgrounds the whole `&&` list | D |
| 423 | 09-22 | `pc_lane.sh` from a manual copy: `ROOT` becomes `/` | G |
| 432 | 09-16 | `pc.sh` over 120 s is cut and re-run (AF-AP-92) | G |
| 433 | 09-22 | bridge stderr lands on the data line | G |
| 434 | 09-14 | sqlite over the bridge: double quotes make an identifier | D |
| 434 | 09-22 | a resumed lane is a newer session with fewer messages | H |
| 438 | 09-23 | worktree-isolated Agent dispatch fails here | G |
| 441 | 09-14 | pytest `--basetemp` parent must exist | G |
| 455 | 09-06 | a worktree's `.git` is a file | G |

### E4.3 This session's transcript (streamed line by line; never read whole)

Method: each script streams the first 651,687,566 bytes (fixed offset), `json.loads` per line; 8 lines (27,321 bytes) do not parse and are skipped, 6 of them hold tool results. Output: counts, names, sizes, times, first-line error classes with `KEY=value`, URLs, long tokens and digits removed. Exploratory runs gave identical numbers and are not pasted.

Main script `jev_e4e5.py`:

```python
#!/usr/bin/env python3
"""E4/E5 evidence from one Claude Code transcript JSONL, streamed line by line up to a fixed byte offset.
Prints counts, type/tool names, sizes, times and SCRUBBED first-line error classes only; never result content.
usage: jev_e4e5.py <transcript.jsonl> <byte_limit>"""
import collections as C, json, re, statistics as S, sys

SCRUB = [(re.compile(r"[A-Za-z_][A-Za-z0-9_]*=\S+"), "KEY=<v>"), (re.compile(r"[a-z][a-z0-9+.-]*://\S+", re.I), "<url>"),
         (re.compile(r"\b[A-Za-z0-9_\-]{24,}\b"), "<tok>"), (re.compile(r"(?i)(bearer|token|key|secret|password)\s*[:=]?\s*\S+"), r"\1 <v>")]
CD = re.compile(r"^\s*cd\s+\S+\s*(&&|;)\s*")


def scrub(s, digits=False):
    for rx, rep in SCRUB:
        s = rx.sub(rep, s)
    return re.sub(r"\d+", "N", s) if digits else s


def num(v):
    return v if isinstance(v, int) and not isinstance(v, bool) else 0


def res(content):  # (first text part, UTF-8 bytes the model receives; images by base64 length)
    if isinstance(content, str):
        return content, len(content.encode("utf-8", "replace"))
    first, tot = None, 0
    for p in content if isinstance(content, list) else []:
        if isinstance(p, dict) and p.get("type") == "text":
            t = p.get("text") or ""
            tot += len(t.encode("utf-8", "replace"))
            first = t if first is None else first
        elif isinstance(p, dict) and p.get("type") == "image":
            tot += len((p.get("source") or {}).get("data") or "")
    return first or "", tot


def label(inp):
    for k in ("command", "file_path", "path", "pattern", "description", "query", "url", "prompt", "skill"):
        v = inp.get(k) if isinstance(inp, dict) else None
        if isinstance(v, str) and v:
            while k == "command" and CD.match(v):
                v = CD.sub("", v, count=1)
            return scrub(v.replace("\n", " "))[:40]
    return ""


path, limit = sys.argv[1], int(sys.argv[2])
bt, ab, an, calls, rn, rb, re_, ec, codes, days, fb = (C.Counter() for _ in range(11))
use, big, req, items, pre, trig, hk = {}, [], {}, [], [], C.Counter(), C.defaultdict(list)
stop = {"n": 0, "err": 0, "prevent": 0, "scripts": C.Counter()}
nb = nl = 0
with open(path, "rb") as f:
    for raw in f:
        if nb + len(raw) > limit:
            break
        nb += len(raw); nl += 1
        try:
            r = json.loads(raw)
        except ValueError:
            bt["<unparsable>"] += len(raw); continue
        t, ts = r.get("type"), (r.get("timestamp") or "")
        bt[t] += len(raw)
        if ts:
            days[ts[:10]] += 1
        m = r.get("message") if isinstance(r.get("message"), dict) else {}
        c = m.get("content")
        if t == "attachment":
            a = r.get("attachment") if isinstance(r.get("attachment"), dict) else {}
            k = a.get("type"); ab[k] += len(raw); an[k] += 1
            if k == "task_reminder" and isinstance(a.get("itemCount"), int):
                items.append(a["itemCount"])
            if isinstance(k, str) and k.startswith("hook_"):
                hk[(k, a.get("hookName") or "?")].append(ts[:16])
        elif t == "system" and r.get("subtype") == "compact_boundary":
            md = r.get("compactMetadata") if isinstance(r.get("compactMetadata"), dict) else {}
            if num(md.get("preTokens")):
                pre.append(md["preTokens"])
            trig[md.get("trigger")] += 1
        elif t == "system" and r.get("subtype") == "stop_hook_summary":
            stop["n"] += 1
            stop["err"] += isinstance(r.get("hookErrors"), list) and len(r["hookErrors"]) > 0
            stop["prevent"] += r.get("preventedContinuation") is True
            for h in r.get("hookInfos") or []:
                stop["scripts"][str((h or {}).get("command") or "").rsplit("/", 1)[-1]] += 1
        elif t == "assistant" and isinstance(c, list):
            if r.get("requestId") and isinstance(m.get("usage"), dict):
                u = m["usage"]
                req[r["requestId"]] = (m.get("model"), num(u.get("input_tokens")), num(u.get("cache_creation_input_tokens")),
                                       num(u.get("cache_read_input_tokens")), num(u.get("output_tokens")))
            for b in c:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    calls[b.get("name")] += 1
                    use[b.get("id")] = (b.get("name"), label(b.get("input")), ts[:10])
        elif t == "user" and isinstance(c, str) and c.startswith("Stop hook feedback:"):
            ln = c.splitlines()
            fb[scrub(ln[1] if len(ln) > 1 else "", True)[:50]] += 1
        elif t == "user" and isinstance(c, list):
            for b in c:
                if not (isinstance(b, dict) and b.get("type") == "tool_result"):
                    continue
                name, lab, day = use.get(b.get("tool_use_id"), ("<unmatched>", "", ts[:10]))
                text, size = res(b.get("content"))
                rn[name] += 1; rb[name] += size
                big.append((size, name, lab, day))
                if len(big) > 300:
                    big.sort(reverse=True); del big[15:]
                if b.get("is_error") is True:
                    re_[name] += 1
                    l1 = (text.splitlines() or [""])[0]
                    mm = re.match(r"Exit code (\d+)", l1)
                    if mm:
                        codes[int(mm.group(1))] += 1
                    ec[(name, scrub(l1, True)[:60])] += 1
tb = sum(rb.values()); big.sort(reverse=True)
print("[file] bytes_parsed=%d lines=%d days=%d (%s..%s)" % (nb, nl, len(days), min(days), max(days)))
print("[bytes by record type]", ", ".join("%s=%d (%.1f%%)" % (k, v, 100.0 * v / nb) for k, v in bt.most_common(6)))
print("[attachment record bytes by type, top 9]")
for k, v in ab.most_common(9):
    print(" %s n=%d bytes=%d (%.1f%%) avg=%d" % (k, an[k], v, 100.0 * v / nb, v // an[k]))
print("[reminders] silent_turn_reminder=%d task_reminder=%d task_status=%d batching_reminder_sent=%d total_tokens_reminder=%d"
      % (an["silent_turn_reminder"], an["task_reminder"], an["task_status"], an["batching_reminder_sent"], an["total_tokens_reminder"]))
print("   task_reminder itemCount min/median/max = %d/%d/%d" % (min(items), S.median(items), max(items)))
print("[stop hook] summaries=%d with_hookErrors=%d preventedContinuation=%d scripts=%s" % (stop["n"], stop["err"], stop["prevent"], dict(stop["scripts"])))
print("   'Stop hook feedback' user messages=%d classes=%s" % (sum(fb.values()), fb.most_common(4)))
print("[compactions] %d triggers=%s preTokens min/median/max=%d/%d/%d" % (sum(trig.values()), dict(trig), min(pre), S.median(pre), max(pre)))
print("[hook attachments] " + "; ".join("%s %s n=%d %s..%s" % (k[0], k[1], len(v), min(v), max(v)) for k, v in sorted(hk.items())))
print("[tool calls] total=%d" % sum(calls.values()))
print("   " + ", ".join("%s=%d" % kv for kv in calls.most_common()))
print("[tool results] total=%d errors=%d bytes=%d unmatched=%d" % (sum(rn.values()), sum(re_.values()), tb, rn["<unmatched>"]))
for k in sorted(rb, key=lambda x: -rb[x]):
    print(" %s n=%d err=%d bytes=%d (%.1f%%) avg=%d" % (k, rn[k], re_[k], rb[k], 100.0 * rb[k] / max(tb, 1), rb[k] // max(rn[k], 1)))
print("[error classes] distinct=%d; exit codes=%s" % (len(ec), sorted(codes.items(), key=lambda x: -x[1])))
for (tool, cls), n in ec.most_common(14):
    print(" %d %s %r" % (n, tool, cls))
print("[15 largest tool results] (bytes, tool, first 40 chars of command/path, day)")
for s, n, l, d in big[:15]:
    print(" %d %s %r %s" % (s, n, l, d))
ctx = sorted(a + b + c for (_, a, b, c, _) in req.values())
print("[API requests] distinct requestId=%d context tokens/request median=%d p90=%d max=%d sum=%d; cache_read=%d output=%d"
      % (len(req), S.median(ctx), ctx[int(0.9 * len(ctx))], ctx[-1], sum(ctx), sum(v[3] for v in req.values()), sum(v[4] for v in req.values())))
print("   served model per request:", C.Counter(v[0] for v in req.values()).most_common())
```

`python3 jev_e4e5.py /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl 651687566` (6.9 s):

```text
[file] bytes_parsed=651687566 lines=114378 days=17 (2026-09-02..2026-09-24)
[bytes by record type] attachment=395650128 (60.7%), assistant=141934872 (21.8%), user=101257382 (15.5%), queue-operation=7889060 (1.2%), last-prompt=2168204 (0.3%), system=768791 (0.1%)
[attachment record bytes by type, top 9]
 task_reminder n=1739 bytes=289208111 (44.4%) avg=166307
 nested_memory n=114 bytes=22248095 (3.4%) avg=195158
 instructions n=118 bytes=19026100 (2.9%) avg=161238
 prompt_snapshot n=165 bytes=18692666 (2.9%) avg=113288
 total_tokens_reminder n=14351 bytes=8276407 (1.3%) avg=576
 queued_command n=884 bytes=5990514 (0.9%) avg=6776
 skill_listing n=189 bytes=5808114 (0.9%) avg=30730
 invoked_skills n=68 bytes=4953288 (0.8%) avg=72842
 deferred_tools_record n=98 bytes=4172084 (0.6%) avg=42572
[reminders] silent_turn_reminder=1064 task_reminder=1739 task_status=176 batching_reminder_sent=4947 total_tokens_reminder=14351
   task_reminder itemCount min/median/max = 0/76/222
[stop hook] summaries=856 with_hookErrors=195 preventedContinuation=0 scripts={'stop-hook-git-check.sh': 856}
   'Stop hook feedback' user messages=197 classes=[('[~/.claude/stop-hook-git-check.sh]: There are unco', 137), ('[~/.claude/stop-hook-git-check.sh]: There are untr', 49), ('[~/.claude/stop-hook-git-check.sh]: There are N un', 11)]
[compactions] 118 triggers={'auto': 118} preTokens min/median/max=144106/786089/802058
[hook attachments] hook_additional_context PostToolUse:Bash n=2 2026-09-24T11:02..2026-09-24T11:02; hook_additional_context PostToolUse:Read n=18 2026-09-15T21:02..2026-09-24T11:06; hook_additional_context PreToolUse:Glob n=1 2026-09-24T11:02..2026-09-24T11:02; hook_additional_context PreToolUse:Grep n=1 2026-09-18T09:49..2026-09-18T09:49; hook_additional_context SessionStart n=54 2026-09-03T21:06..2026-09-24T10:18; hook_success PostToolUse:Bash n=10 2026-09-24T11:02..2026-09-24T11:06; hook_success PostToolUse:Read n=19 2026-09-02T21:38..2026-09-24T11:06; hook_success PreToolUse:Glob n=1 2026-09-24T11:02..2026-09-24T11:02; hook_success PreToolUse:Grep n=1 2026-09-18T09:49..2026-09-18T09:49; hook_success SessionStart:compact n=51 2026-09-03T21:12..2026-09-24T10:18; hook_success SessionStart:resume n=5 2026-09-03T21:06..2026-09-18T17:59; hook_system_message PostToolUse:Read n=1 2026-09-02T21:38..2026-09-02T21:38; hook_system_message SessionStart:resume n=2 2026-09-15T06:56..2026-09-18T17:59
[tool calls] total=16736
   Bash=12939, TaskUpdate=825, Edit=618, Read=500, Write=433, ToolSearch=248, Agent=231, TaskCreate=222, Monitor=153, mcp__github__actions_list=86, mcp__github__issue_write=71, Grep=70, SendMessage=55, TaskStop=45, mcp__github__get_job_logs=39, TaskGet=29, mcp__github__issue_read=21, Glob=19, mcp__github__add_issue_comment=19, WebFetch=17, SendUserFile=11, TaskList=11, Skill=10, mcp__Claude_Code_Remote__add_repo=10, mcp__github__list_issues=10, mcp__github__actions_get=8, mcp__github__search_issues=7, Workflow=6, WebSearch=4, mcp__github__actions_run_trigger=3, mcp__github__list_pull_requests=2, mcp__Claude_Code_Remote__list_repos=2, mcp__codebase-memory-mcp__index_repository=2, mcp__github__create_pull_request=1, mcp__github__merge_pull_request=1, mcp__Claude_Code_Remote__register_repo_root=1, mcp__github__pull_request_read=1, mcp__gitnexus__detect_changes=1, mcp__codebase-memory-mcp__list_projects=1, mcp__github__get_me=1, mcp__github__get_label=1, AskUserQuestion=1, ListAgents=1
[tool results] total=16730 errors=239 bytes=26299166 unmatched=1
 Bash n=12934 err=204 bytes=21011113 (79.9%) avg=1624
 Read n=500 err=2 bytes=2738367 (10.4%) avg=5476
 mcp__github__actions_list n=86 err=1 bytes=734988 (2.8%) avg=8546
 TaskList n=11 err=0 bytes=388645 (1.5%) avg=35331
 mcp__github__get_job_logs n=39 err=3 bytes=350937 (1.3%) avg=8998
 Agent n=230 err=0 bytes=234151 (0.9%) avg=1018
 Grep n=70 err=2 bytes=145975 (0.6%) avg=2085
 Edit n=618 err=11 bytes=101899 (0.4%) avg=164
 mcp__github__issue_read n=21 err=0 bytes=96824 (0.4%) avg=4610
 Write n=433 err=0 bytes=74950 (0.3%) avg=173
 TaskStop n=45 err=1 bytes=63562 (0.2%) avg=1412
 Monitor n=153 err=2 bytes=46743 (0.2%) avg=305
 mcp__github__list_issues n=10 err=0 bytes=43086 (0.2%) avg=4308
 TaskCreate n=222 err=0 bytes=42111 (0.2%) avg=189
 mcp__Claude_Code_Remote__add_repo n=10 err=0 bytes=36227 (0.1%) avg=3622
 mcp__github__actions_get n=8 err=1 bytes=29287 (0.1%) avg=3660
 TaskGet n=29 err=1 bytes=26695 (0.1%) avg=920
 TaskUpdate n=825 err=3 bytes=25288 (0.1%) avg=30
 WebFetch n=17 err=0 bytes=24217 (0.1%) avg=1424
 mcp__github__search_issues n=7 err=0 bytes=19851 (0.1%) avg=2835
 WebSearch n=4 err=0 bytes=12461 (0.0%) avg=3115
 SendMessage n=55 err=0 bytes=9283 (0.0%) avg=168
 mcp__Claude_Code_Remote__list_repos n=2 err=0 bytes=8595 (0.0%) avg=4297
 mcp__gitnexus__detect_changes n=1 err=0 bytes=7279 (0.0%) avg=7279
 Workflow n=6 err=1 bytes=6800 (0.0%) avg=1133
 mcp__github__issue_write n=71 err=0 bytes=5458 (0.0%) avg=76
 mcp__github__pull_request_read n=1 err=0 bytes=5001 (0.0%) avg=5001
 mcp__codebase-memory-mcp__index_repository n=2 err=1 bytes=1930 (0.0%) avg=965
 mcp__github__add_issue_comment n=19 err=0 bytes=1912 (0.0%) avg=100
 SendUserFile n=11 err=0 bytes=1698 (0.0%) avg=154
 Glob n=19 err=2 bytes=1500 (0.0%) avg=78
 mcp__github__actions_run_trigger n=3 err=3 bytes=492 (0.0%) avg=164
 ListAgents n=1 err=0 bytes=319 (0.0%) avg=319
 mcp__github__get_me n=1 err=0 bytes=293 (0.0%) avg=293
 mcp__Claude_Code_Remote__register_repo_root n=1 err=0 bytes=292 (0.0%) avg=292
 Skill n=10 err=0 bytes=279 (0.0%) avg=27
 AskUserQuestion n=1 err=0 bytes=263 (0.0%) avg=263
 mcp__codebase-memory-mcp__list_projects n=1 err=0 bytes=151 (0.0%) avg=151
 mcp__github__merge_pull_request n=1 err=0 bytes=109 (0.0%) avg=109
 mcp__github__create_pull_request n=1 err=0 bytes=74 (0.0%) avg=74
 mcp__github__get_label n=1 err=1 bytes=57 (0.0%) avg=57
 mcp__github__list_pull_requests n=2 err=0 bytes=4 (0.0%) avg=2
 ToolSearch n=247 err=0 bytes=0 (0.0%) avg=0
 <unmatched> n=1 err=0 bytes=0 (0.0%) avg=0
[error classes] distinct=36; exit codes=[(1, 76), (2, 33), (143, 20), (128, 8), (144, 6), (127, 5), (124, 1)]
 149 Bash 'Exit code N'
 23 Bash 'Permission for this action was denied by the Claude Code aut'
 10 Edit '<tool_use_error>String to replace not found in file.'
 7 Bash '<tool_use_error>Blocked: sleep N followed by: cat /tmp/claud'
 4 Bash '<tool_use_error>Blocked: sleep N followed by: cd /home/user/'
 3 mcp__github__get_job_logs 'failed to get job logs: failed to download log content for j'
 3 TaskUpdate '<tool_use_error>InputValidationError: TaskUpdate failed due '
 3 mcp__github__actions_run_trigger 'failed to cancel workflow run: POST <url> N Resource not acc'
 2 Bash "The user doesn't want to proceed with this tool use. The too"
 2 Bash '<tool_use_error>InputValidationError: ['
 2 Bash '<tool_use_error>Blocked: sleep N followed by: KEY <v> grep -'
 2 Bash '<tool_use_error>Blocked: sleep N followed by: bash scripts/p'
 2 Grep 'Ripgrep search timed out after N seconds. The search may hav'
 2 Glob 'Ripgrep search timed out after N seconds. The search may hav'
[15 largest tool results] (bytes, tool, first 40 chars of command/path, day)
 49004 Read '/home/user/agent-factory/proofs/S0-03/<t' 2026-09-18
 48681 TaskList '' 2026-09-24
 48581 TaskList '' 2026-09-24
 47691 Read '/home/user/agent-factory/todo/BUILD-TASK' 2026-09-18
 47671 TaskList '' 2026-09-23
 46553 TaskList '' 2026-09-23
 45761 TaskList '' 2026-09-23
 41961 Read '/home/user/agent-factory/CLAUDE.md' 2026-09-02
 41513 Read '/home/user/agent-factory/.claude/skills/' 2026-09-16
 40205 TaskList '' 2026-09-22
 39312 Read '/home/user/agent-factory/docs/research/f' 2026-09-24
 39277 mcp__github__get_job_logs '' 2026-09-06
 37628 mcp__github__actions_list '' 2026-09-23
 37191 Read '/home/user/agent-factory/docs/INCIDENT-L' 2026-09-16
 35804 Read '/home/user/agent-factory/docs/research/f' 2026-09-24
[API requests] distinct requestId=15095 context tokens/request median=457469 p90=720193 max=795650 sum=6821010257; cache_read=6711006256 output=23779954
   served model per request: [('claude-fable-5-1', 5901), ('claude-opus-5-5', 5702), ('claude-opus-4-8', 2771), ('claude-opus-4-6', 532), ('claude-fable-5', 147), ('<synthetic>', 42)]
```

Side script `jev_e5_side.py` (same arguments):

```python
import collections as C, json, os, re, sys
path, limit = sys.argv[1], int(sys.argv[2])
nb, bad_tr, parts, pbytes, foot, tr, fam, rem, hcmd = 0, 0, C.Counter(), C.Counter(), C.Counter(), C.Counter(), C.Counter(), C.Counter(), C.Counter()
FOOT = re.compile(rb"\[fast-jev-output full output: (.{0,12})")
FAM = [("Exit code", "exit code N"), ("Blocked: sleep", "harness blocked a foreground sleep"), ("Permission for this action was denied", "auto-mode denial"),
       ("InputValidationError", "input validation"), ("String to replace not found", "edit anchor"), ("File has not been read", "edit anchor"),
       ("Ripgrep search timed out", "ripgrep timeout"), ("doesn't want to proceed", "user declined")]
with open(path, "rb") as f:
    for raw in f:
        if nb + len(raw) > limit:
            break
        nb += len(raw)
        for m in FOOT.finditer(raw):
            g = m.group(1)
            foot["template ${path}/escaped" if g[:1] in (b"$", b"\\") else "placeholder <path>" if g.startswith(b"<path>") else "real path"] += 1
        try:
            r = json.loads(raw)
        except ValueError:
            bad_tr += b'"tool_result"' in raw
            continue
        c = (r.get("message") or {}).get("content") if isinstance(r.get("message"), dict) else None
        if isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    if b.get("is_error") is True:
                        cont = b.get("content")
                        txt = cont if isinstance(cont, str) else next((p.get("text", "") for p in cont or [] if isinstance(p, dict) and p.get("type") == "text"), "")
                        l1 = (txt.splitlines() or [""])[0]
                        fam[next((n for k, n in FAM if k in l1), "other (GitHub MCP/API and misc)")] += 1
                    if isinstance(b.get("content"), list):
                        for p in b["content"]:
                            if isinstance(p, dict):
                                parts[p.get("type")] += 1
                                pbytes[p.get("type")] += len(json.dumps(p).encode())
        a = r.get("attachment") if r.get("type") == "attachment" and isinstance(r.get("attachment"), dict) else None
        if a and a.get("type") == "task_reminder":
            tr["n"] += 1
            tr["has_rendered"] += isinstance(r.get("rendered"), str)
            tr["content_json_bytes"] += len(json.dumps(a.get("content"), ensure_ascii=False).encode())
        if a and a.get("type") == "silent_turn_reminder" and isinstance(a.get("text"), str):
            rem[a["text"][:60]] += 1
        if a and a.get("type") == "hook_success" and isinstance(a.get("command"), str):
            hcmd[(a.get("hookName"), ",".join(os.path.basename(t).strip("\"';") for t in a["command"].split() if "/" in t)[:40])] += 1
print("bytes_parsed", nb)
print("unparsable lines holding a tool_result:", bad_tr)
print("tool_result list-part types:", parts.most_common(), "json bytes:", pbytes.most_common())
print("pruner footer strings:", dict(foot))
print("task_reminder:", dict(tr))
print("error families:", fam.most_common())
print("silent_turn_reminder template(s):", rem.most_common(2))
print("hook_success (hookName, command path basenames):", hcmd.most_common(10))
```

```text
bytes_parsed 651687566
unparsable lines holding a tool_result: 6
tool_result list-part types: [('text', 566), ('tool_reference', 510)] json bytes: [('text', 1683753), ('tool_reference', 29379)]
pruner footer strings: {'placeholder <path>': 8, 'template ${path}/escaped': 2}
task_reminder: {'n': 1739, 'has_rendered': 0, 'content_json_bytes': 238040875}
error families: [('exit code N', 149), ('harness blocked a foreground sleep', 28), ('auto-mode denial', 23), ('other (GitHub MCP/API and misc)', 14), ('edit anchor', 11), ('input validation', 8), ('ripgrep timeout', 4), ('user declined', 2)]
silent_turn_reminder template(s): [("The user hasn't heard from you in a while — say in a few wor", 1064)]
hook_success (hookName, command path basenames): [(('SessionStart:compact', 'run-hook.cmd'), 40), (('PostToolUse:Read', 'cbm-code-discovery-gate'), 18), (('SessionStart:compact', 'cbm-session-reminder'), 11), (('PostToolUse:Bash', 'hook-probe-post.log'), 8), (('SessionStart:resume', 'cbm-session-reminder'), 5), (('PostToolUse:Bash', 'hook-probe-post.log,settings.json)"}}'), 2), (('PreToolUse:Grep', 'cbm-code-discovery-gate'), 1), (('PreToolUse:Glob', 'hook-probe-pre.log'), 1), (('PostToolUse:Read', 'agent-factory,hook_context.py,edit-snaps'), 1)]
```

Read off the outputs (all SOLID; error families are my grouping):

| Cell | Value |
|---|---|
| Size, span | 651,687,566 bytes parsed (653,854,082 at 11:28Z, growing); 114,378 lines; 17 active days, 09-02 to 09-24; 16,736 tool calls, Bash 12,939 (77.3%) |
| Errors | 239 of 16,730 results: exit code N 149 (rc 1: 76, 2: 33, 143: 20, 128: 8, 144: 6, 127: 5, 124: 1); harness block of a foreground sleep 28; auto-mode denial 23; GitHub MCP/API and misc 14; edit anchor 11; input validation 8; ripgrep timeout 4; user declined 2 |
| Reminders | "hasn't heard from you" = `silent_turn_reminder` 1,064; Stop-hook feedback 197 messages, all from `~/.claude/stop-hook-git-check.sh` (uncommitted 137, untracked 49, other 11), 856 Stop summaries, none with a project hook; task tools: `task_reminder` 1,739 (itemCount median 76), `task_status` 176 |
| Compactions | 118, all auto; tokens before compaction median 786,089 (min 144,106, max 802,058) |
| Hooks that ran | `run-hook.cmd` 40, `cbm-code-discovery-gate` 19, `cbm-session-reminder` 16, probe hooks 11 (09-24 11:02Z), `hook_context.py` wrapping edit-snapshot 1 (11:06Z); this lane's own session got edit-snapshot context on each scratch Write |

## E5. Context-cost evidence (from E4.3)

| Cell | Value | Mark |
|---|---|---|
| Tool-result bytes the model receives (text + image parts) | 26,299,166 over 16,730 results: Bash 21,011,113 (79.9%, avg 1,624); Read 2,738,367 (10.4%, avg 5,476); `actions_list` 734,988 (2.8%); TaskList 388,645 (1.5%, 11 results, avg 35,331); `get_job_logs` 350,937 (1.3%); Agent 234,151 (0.9%) | SOLID |
| 15 largest | 7 Read (35,804-49,004 bytes), 6 TaskList (40,205-48,681), `get_job_logs` 39,277, `actions_list` 37,628; no Bash result | SOLID |
| Context per API request | 15,095 requests: median 457,469 tokens, p90 720,193, max 795,650; sum 6,821,010,257 (cache reads 6,711,006,256); output 23,779,954 | SOLID |
| Transcript bytes | attachments 60.7% of the file; `task_reminder` 289,208,111 bytes (44.4%; avg 166,307; content 238,040,875 JSON bytes; no `rendered` field). The in-context share of an attachment is not in the file | count SOLID; share unknown |
| Not measured | ToolSearch results: 510 `tool_reference` parts (29,379 JSON bytes) expanded by the harness outside the file; 6 unparsable result lines (16,736 calls vs 16,730 results) | gaps |
| Prior claim | 09-22, a 35.3 MB transcript: "tool results 16.5 MB = 46.9%" | `JEV-LAYA-AUDIT-2026-09-22.md:88-96`; UNSURE (other base) |

## E6. What gets copied to production

The one committed statement: "The first Agent Factory team mirrors this map one-to-one: a coordinator ..., builders ..., verifiers ..., researchers ..., curators ..., and the mechanical plane (hooks, validators, transcript sync)" (`docs/WORKFLOW-OFFLOAD-MAP.md:131-141`, 66265c4, 09-05; NOT built: `:160-170`).

| Path (tracked files, last commit) | Holds | E3 rows |
|---|---|---|
| `.claude/skills/` (3,051; bfe66ec) | SKILL.md classes (`sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv`, f83aa36): 8 kit-adapted (the S-row skills minus bug-echo and wiki-compiler), 3 first-party (codebase-memory, session-start-hook, wiki-compiler), 356 kit-verbatim (incl. bug-echo), 28 vendored, 15 copies | S1-S27 |
| `.agents/skills/` (3,047), `.agents/lane-skills/` | Codex/Hermes mirrors (`sync-skills.sh`, `sync-lane-skills.sh`; list `harness-ports/lane-skills.txt`) | S rows, P20 |
| `.claude/agents/` (27; f83aa36) | agent definitions | S2, S3, S28 |
| `.claude/hooks/` (5; de06db6) | edit-snapshot, graft-first-nag, session-start, turn-retro-gate, wiki-context | H1-H9 |
| `.claude/settings.json`, `scripts/install_session_hooks.py`, `scripts/hook_context.py` (a12e672) | hook registration, `/home/user` copy, text -> additionalContext | H1-H9 firing |
| `scripts/` (52; a12e672), `scripts/hooks/` (3; 8d50443) | gates, harvest, dispatch; pre-commit: lint_delta `:16`, mirror `:78-81`, stamp `:118`, screen `:127` | P1-P6, P8-P11, P13-P19 |
| `harness-ports/bin/` (21; 3a45568) | lane runner, lane profile, done-gate, Hermes/Codex hook adapters, Laya and pruner setup | P7, P12 |
| `harness-ports/roles/` (7; 4313a3b), `.codex/` (4) | 7 lane role bodies; Codex TOMLs | role behavior |
| `harness-ports/hermes/config-snippet.yaml` (569914b) | Hermes hook map (`:109-116,129-183`): session-start -> on_session_start (observer); wiki-context -> pre_llm_call; edit-snapshot, graft-first-nag -> post_tool_call (spooled); turn-retro-gate -> pre_verify, commented out; merged ADD-ONLY by `hermes-config-merge.py` | H1, H4, H5, H8, H9 in lanes |
| `AGENTS.md` (092b4fa), `.hermes.md` (c7929c5), `CLAUDE.md` (a12e672) | instruction files | C1-C13 |
| `.github/workflows/stage0-ci.yml` (5689d9f) | CI + transcripts-only filter | P5 |
| `harness-ports/adapters` | ABSENT (`ls`); adapters are in `harness-ports/bin/` (`hermes-hook-adapter.py`, `codex-hook-adapter.py`, `hook-shim.sh`) | — |

## Cells not filled

| Gap | Why | Command |
|---|---|---|
| The PC Laya unit now (listening, ExecStart, calls) | PC state; no bridge in this brief | last read `VERIFY-T92-T90R3-PCJ1-report.md:283-294` (09-23) |
| Whether PC lane profiles carry the Hermes hook snippet | PC state | not run |
| In-context size of attachments; ToolSearch result size; 6 results in unparsable lines | records, not rendered context; harness-expanded parts; `json.loads` fails | side script |
| MoJev latency and memory on our CPU | Gate 0 not run | `MOJEV-AUDIT:112-115` |
| #115, #116 in the ledger | absent | `grep -n -E '#115\b|#116\b' todo/BUILD-TASKLIST.md`: 0 |
| A committed heartbeat script (orchestration `:301`; CLAUDE.md `:423` "vllm wait>0 with kv>=0.75") | absent | `git ls-files | grep -i heartbeat`: 0; `grep -rln -E 'heartbeat|kv>=' scripts harness-ports/bin`: 0 |
| Label sources for H1, H4, S25, S26 | none found | `.agents/research/` absent; d1 rows 0 |
| Registry and quirk classes | single rater | E4.1, E4.2 |
