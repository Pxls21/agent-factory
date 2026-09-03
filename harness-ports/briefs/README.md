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
| `verify-contract.md` | adversarial-verifier | after a build lane returns (contract-gate step 3) | PASS/FAIL per contract item + RED tests (patch home) |
