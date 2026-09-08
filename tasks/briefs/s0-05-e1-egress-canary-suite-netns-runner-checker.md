# Lane E1 — S0-05 no-direct-egress: the canary suite, the selective netns as a library, the unit runner, the checker (sandbox Opus 4.6 `code-implementer`)

PIN: (HEAD at dispatch — the commit carrying this brief; the report header says "PIN: `<sha>`".)

**Why:** the mechanism is PROVEN (spike `selective-egress`, POSITIVE: a veth pair + iptables default-DROP in a dedicated netns lets a unit
reach a local OmniRoute listener while a model endpoint fails — `spikes/selective-egress/probe.sh`, `result.json`), the full proof does
not exist (no `proofs/S0-05/`, ledger ABSENT). The seed (`seeds/seed-stage0-v1.yaml:423-441`): "network canaries FAIL from every
non-OmniRoute unit, and each canary first proves its positive control (the unit CAN reach its allowed target)"; negative control: the
egress gate switched off ⇒ the suite goes RED with `egress-permitted: gate-disabled`. docs/05 §6's table (source → allowed destinations)
is what the canaries encode. Bare `unshare --net` is TOTAL isolation and is NOT acceptable evidence (AF-AP-1).
**Inputs:** `tasks/briefs/stage0-parallel-support/material-S0-05.md` (whole; §6.3 the spike's script verbatim, §6.4 what it did NOT test,
§7.1 the AF-AP rows) · `spikes/selective-egress/probe.sh` + `result.json` (the mechanism to LIFT into a library, never re-derive) ·
`docs/05_SECURITY.md:74-85` (the table) · `docs/02_COMPONENT_AUDIT.md:56` ("OmniRoute is sole MODEL API egress, not automatically sole
web/tool egress" — the canaries target MODEL endpoints and the general internet separately, and the report says which the gate blocks) ·
the exemplar specs · `proofs/S0-01/tools/pc/` (how units are launched on the PC — the future live-unit legs).
**Scope (all NEW + one test + your report):** `proofs/S0-05/netns_lib.sh` (the spike's mechanism as functions: `egress_ns_create <ns>
<allow-ip:port>...`, `egress_ns_run <ns> <cmd…>`, `egress_ns_destroy <ns>`, `egress_gate_off <ns>` — the NEGATIVE control's switch) ·
`proofs/S0-05/canaries/*.sh` (observation-only, one JSON line each) · `proofs/S0-05/run_canaries.sh <unit-name> <ns> <allowed-target>`
· `proofs/S0-05/check_egress.py` · `proofs/S0-05/spec.json` · `proofs/S0-05/fixtures/` (a synthetic PASSING bundle; the gate-off bundle;
a bare-unshare bundle) · `proofs/S0-05/tools/pc/run_s0_05_units.sh` (PC-side, the live units) · `tests/test_s0_05_egress.py` · report
`tasks/briefs/s0-05-support/E1-report.md`. Shared-tree rules as every lane (never git stash/checkout/restore/reset/add/commit/push; gates
from a `git archive <PIN>` copy under /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/e1/ + your files;
explicit `--basetemp`; NEVER background a run and stop; no outward actions; NO PC bridge; never print credentials). The sandbox runs as
root and the spike's netns mechanism WORKS here (the spike ran here) — your gates exercise the REAL netns with `curl` as the unit; every
netns you create is destroyed by name in a `trap` and listed in the process/netns census (`ip netns list` empty of yours at the end);
network beyond localhost is forbidden to you EXCEPT the canaries' connection attempts, which must FAIL — a canary that succeeds in
reaching a model endpoint from the sandbox is a finding, not a violation, but never send a request body to a real provider (TCP
connect / TLS handshake only, `--connect-timeout 5`).

## Design (pinned — build it, do not redesign it)
1. **`netns_lib.sh`** lifts `spikes/selective-egress/probe.sh` verbatim where it can (cite the spike's lines per function): a dedicated
   netns with a veth pair, default-DROP OUTPUT/FORWARD, an ACCEPT for the allowed OmniRoute target(s) (ip:port) and loopback, DNS BLOCKED
   inside the netns (docs/05:21 "DNS/connection canaries" — the canary asserts DNS resolution FAILS for model hosts); `egress_gate_off`
   flushes the DROP rules (the mutation the seed names) and stamps `gate: disabled` into the run's `gate.json`; idempotent; every rule
   listed in the report. Rejected: bare `unshare --net` (AF-AP-1, total block — the positive control could never pass).
2. **Canaries** (observation-only JSON lines: `{"canary": "C3", "target": "api.openai.com:443", "kind": "tcp-connect", "rc": 7, "detail":
   "curl: (7) …"}`): C0 positive control — TCP connect + `GET /v1/models` to the allowed OmniRoute target (rc 0, HTTP status); C1 DNS
   resolution of `api.openai.com`, `api.anthropic.com`, `generativelanguage.googleapis.com` (must FAIL inside the netns); C2 TCP connect
   to a hard-coded model IP:443 you resolve OUTSIDE the netns at run time and pass in (must FAIL, rc 7 or 28 — record which); C3 HTTPS
   handshake to the same (fail); C4 a non-model internet target (`example.com:443`) — RECORDED (docs/02:56: not necessarily blocked by the
   MODEL gate; the report states what the mechanism does); C5 UDP 53 to a public resolver (fail). Each canary prints the exact curl/`ss`
   diagnostic — the checker maps `rc` + detail to the reason vocabulary.
3. **`run_canaries.sh <unit> <ns> <allowed>`** runs C0-C5 INSIDE the netns as the unit (`egress_ns_run`), writes
   `evidence/<unit>/canaries.jsonl` + `gate.json` (`{"gate": "enabled"|"disabled", "rules_sha256": …, "netns": …}`) + `runtime.json`
   (kernel, iptables version, the exact rule list).
4. **`check_egress.py <evidence-root>`** — per unit dir: `gate.json` present and `gate == enabled` (a `disabled` gate ⇒ exit 1
   `egress-permitted: gate-disabled` — the seed's exact reason; the checker FAILS BEFORE looking at canaries, so a disabled gate can never
   pass by luck); C0 rc 0 AND an HTTP status (the positive control PROVES reachability — a unit whose C0 failed ⇒ `positive-control-failed:
   <unit>`, never a pass); C1/C2/C3/C5 each FAILED with an rc in the denial set {6, 7, 28} and a detail matching the netns mechanism
   (`Could not resolve` / `Connection refused` / `timed out`) — any success ⇒ `egress-permitted: <unit> <canary> <target>`; C4 recorded;
   the rule-list sha in `gate.json` equals the sha of the rules the checker expects (a pinned rule digest per allowed target — the
   mechanism cannot be silently weakened); ≥ 1 unit; every unit in the required set (a `--units` list; default the mechanism unit `curl`)
   present. Absent root ⇒ `deferred:` exit 2. S_ISREG rule. PASS line `PASS: S0-05 no-direct-egress - N units, M canaries failed as required,
   positive controls N/N`.
5. **`spec.json`**: positive `check_egress.py proofs/S0-05/evidence` (expect 0); negative `check_egress.py proofs/S0-05/fixtures/evidence-gate-off`
   (expect 1 + `failure_reason: egress-permitted: gate-disabled`); a second negative `fixtures/evidence-bare-unshare` (C0 failed ⇒
   `positive-control-failed: curl`) — the AF-AP-1 class as a committed control.
6. **The sandbox MECHANISM run is yours**: `run_canaries.sh curl <ns> 127.0.0.1:<port>` against a local stand-in listener (a stdlib HTTP
   server you start by pid) with the gate ON ⇒ the checker PASSES on that bundle (paste it — this is the mechanism leg re-proven on the
   PIN); the gate OFF ⇒ `egress-permitted: gate-disabled`; bare unshare ⇒ `positive-control-failed`. Commit the gate-on sandbox bundle
   as `fixtures/evidence-mechanism-sandbox/` with its `runtime.json` (venue `sandbox`) — it is EVIDENCE of the mechanism, labelled
   "mechanism proven, containment unproven" as the seed's label says.
7. **`tools/pc/run_s0_05_units.sh`** (NOT run here): for each LIVE unit the plan names and that exists on the PC — `buzz-acp`, `hermes-acp`
   (the S0-01 launch path), the S0-01 scripted backend as an "other unit" — create the netns with the unit's allowed target from docs/05 §6
   (buzz-acp: the relay + the local hermes-acp; Hermes: OmniRoute :20128), launch the unit INSIDE it via the S0-01 tools, run the canaries as
   that unit, collect; units not yet runnable (memory adapter, ai-memory, dream/foundry) are listed as `NOT run: unit does not exist` in
   the evidence's `units.json` and in the report — the checker treats a declared-absent unit as NOT counted, never as passed.
8. **Tests**: the checker over the synthetic passing bundle and both negatives; every canary success mutated in ⇒ the named failure; a
   gate-off bundle with all canaries failing ⇒ still `gate-disabled` (the gate check is first); the rules digest mismatch; the missing
   positive control; the FIFO read; `deferred:`; `netns_lib.sh` functions under `bash -n` and a real create/run/destroy round trip with
   the census (needs root — the sandbox has it; skip DECLARED when not root). Preflight the 18 classes.
9. **Report discipline** as every lane: report_lint MISS 0, ap_screen classified, file:line by grep, counts pasted twice, pyflakes +
   bash -n, the netns + process census (zero of yours remain).

## Mutants (≥ 12): GATE-OFF-ACCEPTED · GATE-CHECK-AFTER-CANARIES · POSITIVE-CONTROL-OPTIONAL · CANARY-SUCCESS-ACCEPTED · RULES-DIGEST-UNPINNED ·
DNS-CANARY-DROPPED · UNIT-SET-EMPTY-PASSES · BARE-UNSHARE-ACCEPTED · DEFERRED-AS-PASS · FIFO-HANG · DETAIL-UNCHECKED (rc 7 with a detail from
a different mechanism) · NETNS-LEAK (the trap removed → the census test fails).

## Report shape
FILE IDENTITY · DONE (assertion → canary → checker rule → test; the sandbox mechanism bundle's PASS line pasted) · mutants · NOT_DONE (the
live-unit legs on the PC; units that do not exist yet) · DISCREPANCIES (mechanism vs full-proof classification; what the gate blocks beyond
model endpoints) · SELF-ATTACK.
