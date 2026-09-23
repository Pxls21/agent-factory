# VERIFY-E3 — the targeted adversarial verify of S0-05's live-unit launch recipe (E3) and the collector's whole allow-set (E3-b) (task #165)

PIN: c269263 (origin head after the E3-b landing; the boundary below is byte-identical to HEAD, measured in the premise block).
LANE: verify-e3 (sandbox; agent `adversarial-verifier` on the D-054 pin, in the SHARED tree, no worktree isolation; ROOT is needed:
every namespace, veth, nat rule and sysctl test runs as uid 0). Honey `full`: line-bounded findings, evidence anchors, SOLID/UNSURE.
Do NOT spawn subagents. AUTHORIZATION: this is defensive testing of the owner's own egress containment (S0-05: a unit may reach only
its allowed destinations); every namespace, rule and listener you create is yours to destroy.

WHAT LANDED (both GATED-PENDING-VERIFY, rule 0f; graded so far only by their builders' tests and the coordinator's re-runs):
- E3 (task #153, ec56bb7, 2026-09-23 06:41Z): Part X (X1 the port digit bound, X2 the partial-state rollback + the reap set before
  create, X3 the atomic stale-claim takeover, X4 the real cleanup's owner check), Part A (CD1's launch recipe A1-A8: pins read from
  `proofs/S0-01/pins.py`, the recorded override and the checker's refusal of it, the scratch tree and its census, stdio pipes, the unit
  user, the environment from nothing, the pinned argv with three substitutions and the identity-file refusals, `unit-identity.json`
  and the checker's requirement, allow entries formed by the runner), Part D (D-051's relay reach: one DNAT rule + route_localnet,
  removed in the leg's teardown AND in cleanup). Contract: `tasks/briefs/s0-05-support/E3-brief.md`; report `E3-report.md`.
- E3-b (task #164, 76f439f, 2026-09-23 08:2xZ): G the one allow-entry rule in three places, A the collector's whole allow-set
  (validated 3→5→6 before any side effect), P the C0 record carries its path, C the positive control per allowed entry, R1 the
  measured health paths, R2 the preflight = the real C0 canary graded by the checker's `c0_proves`, R3 the whole list to the
  collector, R4 TERM/INT stop the runner (143/130) through one cleanup. Contract: `tasks/briefs/s0-05-support/E3-b-brief.md`; report
  `E3-b-report.md` (its §9 DISCREPANCIES and adjacent defects are inputs to your items, never conclusions).

BOUNDARY: CREATE `tasks/briefs/s0-05-support/VERIFY-E3-report.md` (write it incrementally from the start); nothing else. Mutants run
in scratch copies only (never a git restore in this shared tree; each mutant compiles — `bash -n` / `py_compile` — and collects,
AF-AP-78). Other sandbox agents work on disjoint files (`tasks/briefs/s0-02-support/`, `tasks/briefs/hermes-repin/`, and a private
worktree under `/tmp/wt-ci166`): never touch, run or revert them. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`,
`git commit` or `git push`. No outward-facing action. No PC or bridge use: the live leg is the coordinator's. Every namespace, veth,
nat rule, sysctl, claim, `/etc/netns` entry and process you create is destroyed by NAME or PID from your own record, never by
`pkill -f`; the census reads empty at the end (pasted). The sandbox has about 1.5 GB free (measured below): clean every scratch copy you make as you go.

CODE INTEL FIRST: `graft ask` before any grep for code questions; `scripts/lane_context.sh -q 'how does the S0-05 runner decide a
unit may launch' -s check_positive_control -s c0_proves -s egress_allow_entry_ok -s egress_ns_create -s cleanup -o /tmp/ve3/pack.md
proofs/S0-05/run_canaries.sh proofs/S0-05/check_egress.py proofs/S0-05/tools/pc/run_s0_05_units.sh proofs/S0-05/netns_lib.sh`.

## Items (attack the whole contract with NEW shapes, never the builders' cases; report EVERY observation, no severity filter)

1. PREMISE: re-run the premise commands below; stop CONTRACT-INVALID on a mismatch that changes this brief.
2. E3 Part X. X1: the port bound now lives in `egress_allow_entry_ok` (E3-b G) — the whole E3 X1 table through BOTH the library and
   `egress_ns_create`, plus shapes neither builder tried. X2: fault-inject at steps the builder did not (an address, a link,
   `/etc/netns`, the claim's owner record, the second gate rule) and paste the census after each; is the name in the reap set before
   create on every path? X3: race two creators on one stale claim at least 50 times; count winners and refusals. X4: the real
   `cleanup` against a namespace owned by another LIVE pid and by a dead one.
3. E3 Part A, line by line against CD1 (`tasks/briefs/s0-05-support/CD1-AMENDMENT.md`) and the E3 brief: A1 (pins from `pins.py` at
   run time; a pc-venue bundle carrying ANY `override` refused — try every key shape), A2 (the census paths from the pinned base; a
   tree change fails the leg), A3 (stdin held open for the window then closed; never `/dev/null`, never a regular file), A4 (uid 0
   refused; the default resolution), A5 (no inherited variable reaches a unit: plant sentinel names in the runner's environment,
   including names matching `pins.REDACTED_ENV_KEY_RE`), A6 (the argv's three substitutions and nothing else; each identity-file
   refusal text; S0-01's `.secrets/agent.env` refused by name), A7 (`unit-identity.json`: forge each field — a wrong digest, a wrong
   realpath, uid 0, a missing file — and read the checker's exact refusal), A8.
4. E3 Part D: the DNAT rule and `route_localnet` exist only for the pair's leg; are they removed after a leg that fails at EVERY step
   after the add (preflight, launch, identity, canaries) and after a stop (R4)? A second run's census; a nat rule naming a deleted
   interface; the negative control (rule absent → `unreachable`).
5. E3-b G: the one rule in three places (library, collector, checker). Build your own parity table (at least 40 rows the builder did
   not use: octet and port edges, whitespace, a trailing newline, signs, `0x`, Unicode digits of several scripts, fullwidth digits,
   an empty ip or port, extra colons, IPv6). Run it under `LC_ALL=C`, `C.UTF-8` and any other installed locale.
6. E3-b A: the order 3→5→6 and "before any arithmetic, namespace access, directory, file or canary" — prove the absence of side
   effects on EVERY refusal row with an instrument (a PATH shim that logs any `ip`/`iptables`/`curl` call, and the evidence root's
   state). Every refusal text exact. Paths: the 63-character bound, the character set, `//`, `/..`.
7. E3-b P and C: the C0 record's `path` is recorded; does anything ASSERT it (the checker, the runner)? If nothing does, can a C0 for
   the right ip:port on the wrong path pass the proof, and does that matter against the D-051/R1 contract? C: the exactly-once rule
   against duplicate entries IN gate.json `allowed` (does any phase refuse `["a","a"]` with one C0 for `a`?), a non-string entry (the
   E3-b report's measured `TypeError`), `rc: false` / `rc: 0.0` / `http_status: true` in a C0 record (the AF-AP-26 class; E3-b kept
   today's predicate by contract — is a refusal of the class in the contract or a follow-up?).
8. E3-b R1/R2: the preflight runs the REAL C0 canary under the canaries' scrub list read from `canaries/_emit.sh`, graded by the
   checker's own `c0_proves`. Attack the split between `not-2xx` and `unreachable`: 1xx, 3xx with and without a Location, 204, a 200
   after a redirect, curl rc ≠ 0 with a status, an empty record, two records, a malformed `_emit.sh`, a `check_egress.py` that fails
   to import. Does every path fail closed, and does the operator text name the right cause?
9. E3-b R3: the pair's gate.json `allowed` and the rule pin on a real two-entry run; C6's new default blocked port (the FIRST
   entry's port + 1) — can it collide with an allowed port or a real listener on the PC (3999 → 4000)?
10. E3-b R4: SIGTERM and SIGINT to the runner PID alone and to its process group, during each phase (create, preflight, launch, the
    canary window, teardown). Bash defers a trap while a foreground child runs: measure the stop latency; does a second signal during
    `cleanup` re-enter it? After every stop: exit 143/130, no units.json, no census file, no checker run, the census empty.
11. The declared limits (E3 and E3-b): is each true, and is each written where an operator reads it?
12. Mutation audit (scratch copies): re-run the builders' B1-B14 and X1-X4 on the final bytes (one row each), plus at least 12 NEW
    mutants of your own aimed at items 2-10. One row each: mutant · compiles · collected · killed-by (test id) / SURVIVED / EQUIVALENT
    with the reason. Before you count a kill, run the killing test on the UNMUTATED tree and paste that it passes (AF-AP-138).
13. The landing commit's anti-pattern screen flagged AF-AP-115 (a trust-boundary executable resolved from the caller's `PATH`)
    on lines E3-b added to the test file: is it a test-side resolution only, or does a production path resolve a binary from `PATH`
    (the runner's `SETPRIV_BIN`/`IP_BIN`/`PY_BIN` via `command -v`)? Then anything else you find.

## Verdict

Apply the blocking predicate (contract-mapped · reproduced through the real code path · materially effective · a concrete
discriminator · in the boundary of what landed) and return a GATE RECOMMENDATION: MERGE-READY / MERGE-READY-WITH-FOLLOWUPS /
NOT-READY / CONTRACT-INVALID. Every non-blocking finding is a follow-up row (the coordinator files it as a `verify-followup` issue,
D-034); the ONE focused repair (D-031) is keyed to S0-05 at this contract revision.

## Gates (paste every command with its output)

`mkdir -p /tmp/ve3/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider
--basetemp=/tmp/ve3/bt` twice as root (`rm -rf /tmp/ve3/bt` after each) · once as `nobody` (the namespace tests skip) · the census
(`ip netns list`, `ip -o link show type veth`, `iptables -t nat -S PREROUTING`, `ls /etc/netns`, `/run/s0-05-egress`,
`route_localnet`, no process of yours alive).

## Report (`tasks/briefs/s0-05-support/VERIFY-E3-report.md`)

PREMISE re-measured · each item with its evidence (commands and output pasted, file:line refs) · the mutant table · findings ranked,
each with the blocking predicate applied · the gate recommendation · NOT-done. Lint floor: `python3 scripts/report_lint.py
--min-refs 20 --map RC=proofs/S0-05/run_canaries.sh --map C=proofs/S0-05/check_egress.py --map PC=proofs/S0-05/tools/pc/run_s0_05_units.sh
--map L=proofs/S0-05/netns_lib.sh --map T=tests/test_s0_05_egress.py tasks/briefs/s0-05-support/VERIFY-E3-report.md --root .`;
apply its `fix:` hints for at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 08:30Z, sandbox @ c269263)

````
$ date -u
2026-09-23 08:30Z

$ git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
c269263

$ git diff origin/claude/soundbox-kit-migration-iz1jwf HEAD -- <the seven files> | wc -l; git status --porcelain -- <the seven files> | wc -l
0
0

$ for f in <the seven files>; do sha256 lines path; done
5241b539c50a98b8 175 proofs/S0-05/run_canaries.sh
d39bb7b2665c6413 511 proofs/S0-05/check_egress.py
d2837c4d073bf398 410 proofs/S0-05/netns_lib.sh
888e9f3ebf27fb2e 15 proofs/S0-05/canaries/c0_allowed_target.sh
6d313b8bef0c677e 36 proofs/S0-05/canaries/_emit.sh
07a274102b1abf2a 578 proofs/S0-05/tools/pc/run_s0_05_units.sh
3050c242f33d38ee 2999 tests/test_s0_05_egress.py

$ git log --format="%h %ad %s" --date=format:"%m-%d %H:%M" -3 -- proofs/S0-05 | cut -c1-110
76f439f 09-23 08:26 E3-b landed (GATED-PENDING-VERIFY): S0-05's collector takes the unit's whole allow-set, C0
ec56bb7 09-23 06:41 E3 landed (GATED-PENDING-VERIFY): the S0-05 live-unit launch recipe (Part X, CD1 A1-A8, th
6f2589d 09-23 03:47 S0-05 E2-R1 landed (GATED-PENDING-VERIFY): VERIFY-E2's seven blockers closed in the netns 

$ grep -n (the seams) netns_lib.sh
77:egress_allow_entry_ok() {
88:egress_ns_create() {
97:    egress_allow_entry_ok "$entry" || { echo "egress: allow entry must be <ip>:<port>, got '$entry'" >&2; return 64; }
405:egress_ns_destroy() {

$ grep -n (the seams) check_egress.py
99:# ASCII only: `[0-9]`, never `\d` (which matches every Unicode digit), and fullmatch, never `$` (which
101:_OCTET = r"(0|[1-9][0-9]{0,2})"
102:IPV4_PORT = re.compile(rf"{_OCTET}\.{_OCTET}\.{_OCTET}\.{_OCTET}:(0|[1-9][0-9]{{0,4}})")
206:def _split_ip_port(entry):
207:    match = IPV4_PORT.fullmatch(entry or "")
233:def read_gate(unit_dir, unit):
273:def c0_proves(record):
284:def check_positive_control(records, unit, allowed):
296:    if any(targets.count(entry) != 1 for entry in allowed):       # every allowed entry, exactly once
343:def check_runtime_and_rules(unit_dir, unit, gate):
470:        positives += check_positive_control(records, unit, gates[unit]["allowed"])

$ grep -n (the seams) run_canaries.sh
39:refuse() { printf 'run_canaries: %s\n' "$1" >&2; exit 64; }
40:PROBE_PATH_RE='^/[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._~/-]{0,63}$'
42:rest="${3-},"          # the appended comma keeps a leading, trailing or doubled one an EMPTY entry
47:    refuse "allowed entry '$entry' is not <ip>:<port>[/<path>]"
49:  for seen in "${ALLOWED[@]}"; do [ "$seen" != "$ipport" ] || refuse "allowed entry '$ipport' is listed twice"; done
54:  egress_allow_entry_ok "$BLOCKED" || refuse "blocked entry '$BLOCKED' is not <ip>:<port>"
57:  first_port=${ALLOWED[0]##*:}
58:  [ "$first_port" -lt 65535 ] || refuse "default blocked port 65536 is out of range; pass a blocked entry"
59:  BLOCKED="$(egress_ns_host_ip "$NS"):$((first_port + 1))"
61:for seen in "${ALLOWED[@]}"; do [ "$seen" != "$BLOCKED" ] || refuse "blocked entry '$BLOCKED' is in the allowed set"; done
117:  run_canary c0_allowed_target.sh "$UNIT" "${ALLOWED[$i]}" "${PROBE_PATHS[$i]}"
166:        "allowed": allowed.split(","), "rules_sha256": rules_sha}

$ grep -n (the seams) run_s0_05_units.sh
42:#     host end forwards <host ip>:<relay port> to the pinned relay on 127.0.0.1, and route_localnet=1
81:OMNI_PROBE_PATH=/api/health
82:RELAY_PROBE_PATH=/health
274:C0_SCRUB=(env)
277:_c0_preflight() {  # <ns> <unit> <ip:port> <path>
290:if isinstance(record, dict) and checker.c0_proves(record):
334:trap cleanup EXIT
335:trap 'exit 130' INT
336:trap 'exit 143' TERM
400:  # D-051: the pair reaches the pinned relay through ONE DNAT on its veth host end, for this leg only.
423:        echo "positive-control-not-2xx: $unit $probe HTTP ${verdict#not-2xx }" >&2
426:        echo "positive-control-unreachable: $unit $entry" >&2
428:        echo "  $(egress_ns_host_ip "$ns") (the veth host address) or 0.0.0.0; the relay's reach is D-051's DNAT." >&2
505:  for i in "${!allowed[@]}"; do entries="${entries:+$entries,}${allowed[$i]}${probe_paths[$i]}"; done
506:  bash "$P/run_canaries.sh" "$unit" "$ns" "$entries" "$EVIDENCE_ROOT" "" pc

$ bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py
1 files set=9f0502080347

$ the coordinator gate re-run on these bytes, 08:19-08:25Z (scratchpad e3b-grade/gates.log)
== root run 1
251 passed in 193.62s (0:03:13)
== root run 2
251 passed in 194.16s (0:03:14)
== nobody run
204 passed, 47 skipped in 6.50s
== bash -n
proofs/S0-05/run_canaries.sh rc=0

$ census now
netns: 0 | veth: 0 | nat PREROUTING: -P PREROUTING ACCEPT | /etc/netns: 0 | /run/s0-05-egress: 0

$ df -h /home/user | tail -1
/dev/vda        252G   36G  1.5G  96% /
````
