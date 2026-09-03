# Lane brief templates — the consistent, low-judgment steps offloaded to Hermes routes

Owner ask 2026-09-03: everything that must happen every time but needs no deep judgment runs on a
PC lane (cheap or free OmniRoute route); the coordinator authors briefs, keeps the seeds, gates,
and issues verdicts. Each template is dispatched with
`scripts/pc_lane.sh <filled-copy.md> hermes <role>` after `PIN:` is set to the origin tip and the
`{…}` slots are filled. Roles → default routes live in `harness-ports/bin/pc-lane.sh`
(PROVISIONAL until the probe table in `docs/WORKFLOW-OFFLOAD-MAP.md` pins them).

| Template | Role | When | Output |
|---|---|---|---|
| `wiki-curate.md` | curator | after every push that lands transcripts or a landed increment | `wiki/**` delta + proposals (patch home) |
| `bug-echo-sweep.md` | echo-sweeper | after every real defect fixed (build-loop step 5) | sweep table (report) |
| `code-search.md` | researcher | any "where/who/how does X" question before a brief | evidence table (report) |
| `run-contract.md` | contract-runner (sweep route) | after a build lane returns — the MECHANICAL half of verification: execute every contract item's literal command, report PASS/FAIL DATA | per-item table (report) |
| `verify-contract.md` | adversarial-verifier | in parallel with `run-contract.md` — the JUDGMENT half: attacks on scratch copies + spine read → RED tests (patch home) | findings + RED tests |

## Lane sizing and the incremental report (2026-09-03)

A single verify lane carrying C1–C16 + nine attacks + a spine read ran 167 model calls, compacted
its context four times, and died mid-stream with an EMPTY report; the grading came home only
through state.db forensics. Rules: (1) verification is TWO lanes — the mechanical contract run on
`agentfactory-sweep` and the adversarial attack/spine lane on `agentfactory-verify`; (2) a brief
names at most ~8 attacks or ~16 contract items; (3) every lane appends finished sections to
`$LANE_REPORT_DRAFT` (pc-lane.sh injects the rule and promotes the draft when the final report
is empty — marked PARTIAL, never a verdict).
