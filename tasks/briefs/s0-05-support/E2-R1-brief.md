# E2-R1 — the ONE focused repair (D-031) of VERIFY-E2's seven blockers on S0-05 (sandbox, root + netns)

PIN: 280d3df (origin head; the S0-05 boundary is byte-identical to VERIFY-E2's PIN 9223162, measured below).
LANE: e2-r1 — a sandbox `code-implementer` in the SHARED tree (no worktree isolation: it cannot work on this tree, CLAUDE.md). You have root, network namespaces, iptables and veth here; the PC is not yours to touch.
AUTHORIZATION: this is defensive security work on the owner's own system: egress-policy canaries, network namespaces and iptables rules that PROVE a unit cannot reach anything but its allowed destination.
BOUNDARY (exact; nothing else): MODIFY `proofs/S0-05/netns_lib.sh`, MODIFY `proofs/S0-05/tools/pc/run_s0_05_units.sh`, MODIFY `tests/test_s0_05_egress.py`, NEW `tasks/briefs/s0-05-support/E2-R1-report.md`. Read anything; write nothing else. Do NOT commit, push, open PRs or comment anywhere; leave every change uncommitted in the tree and end with the report.
CONTRACT: the seven BLOCKING findings of `tasks/briefs/s0-05-support/VERIFY-E2-report.md` — F1 (:85), F2 (:160), F3 (:174), F4 (:208), F11 (:358), F12 (:381), F14 (:437) — with that report's reproductions as your red controls, over the E2 contract `tasks/briefs/s0-05-support/E2-brief.md` and the seed's S0-05 block (`seeds/seed-stage0-v1.yaml:423`).
NOT IN SCOPE: CD1 (the `LAUNCH` rows stay exactly as they are; a contract amendment is pending, task #142 — never run `pc_launch.py`, never read or write anything under `proofs/S0-01/` or an `S0_01_*` home); the non-blocking follow-ups F5, F6, F8, F9, F10, F13, F16-F21, unless a blocker's repair covers one by construction (say so, row by row).

## The repair (the required behavior; the design of the code is yours)
1. **F11 + F12 — validate first, create nothing on a refusal.** `egress_ns_create` validates EVERY allow entry before any namespace, veth, rule, owner record or `/etc/netns/<ns>` work: `<ip>:<port>`, the ip a dotted quad of four decimal octets 0-255 with no leading zero (a lone `0` is fine), the port 1-65535 decimal with no leading zero. Any violation returns 64 with the existing line `egress: allow entry must be <ip>:<port>, got '<entry>'` and leaves nothing behind. The three `test_allow_entry_must_be_ipv4_literal` cases then pass as NON-ROOT with no `NEEDS_NETNS` mark and no skip (that is the F12 repair: CI's `tests` job runs non-root). New cases: `1..2:80`, `....:80`, `999.1.1.1:80`, `1.2.3.4.5:80`, `1.2.3:80`, `010.0.0.1:80`, `1.2.3.4:0`, `1.2.3.4:65536`, `1.2.3.4:080` → rc 64 and the exact line; as root, a census after each refusal shows no namespace, no veth, no owner record.
2. **F2 — the owner claim is first and atomic.** Before destroy-first and before creation, the creator claims the name with an atomic primitive (a `mkdir` of a per-name claim path, a noclobber write, or equivalent) that records `$$`. A claim held by a live pid other than `$$` → the existing named refusal (`namespace-live`, rc 65); a stale claim (dead pid) is taken over atomically. Destroy-first and creation run only while holding the claim. Make the verifier's pause-injection control (report :160-173) a deterministic test: two creates on one name → exactly one returns 0, the other returns the named refusal, and the winner's namespace, processes and owner record are intact.
3. **F3 — the runner's cleanup owns what it destroys.** `cleanup` destroys only namespaces this runner created and still owns (the claim's pid is `$$`); the loop's own destroys prune `NS_LIVE`. Test: two real runners, A exits while B is mid-leg → B's namespace, canary process and owner record survive A's exit (the report's two-runner reproduction, made deterministic). This test must also kill M20.
4. **F4 — `units.json` is encoded, never printed.** Write it through a JSON encoder (python3 `json.dumps` or `jq`), never `printf` with raw strings. Test: a reason carrying `"`, `\` and a newline → `check_egress.py` parses `units.json` and the reason equals the input exactly. That test must also kill M21 (it READS the reason).
5. **F1 — destroy never returns 0 with a survivor.** `egress_ns_destroy` sends SIGTERM, waits within its bound, then SIGKILLs every survivor, waits again, and if any process is still in the namespace prints `egress: namespace <ns> still has live pids: <pids>` and returns non-zero. Tests: a SIGTERM-ignoring process (`trap '' TERM`) is gone AT RETURN, killed by the escalation; the report's D-M11 differential (a 1-second slow exit is gone at return) kills M11.
6. **F14 — the runner live test proves the stand-in ran.** The test's stand-in (under `tmp_path`, never under `proofs/`) records its pid and argv; the test asserts the record exists, that the argv equals the `LAUNCH` row as given (kills M16: a bash-wrapped launch never runs the stand-in), and that the stand-in is dead after its unit's leg and before the next unit's leg (kills M17, the brief's m9: `kill "$launch_pid"` alone leaves it alive).

## Evidence demands (paste every output; counts from the run, never typed)
1. **Premise first:** re-measure the identity table below; then reproduce, at the PIN bytes, the verifier's red control for each of the seven blockers (its commands are in the report at the lines above). A blocker you cannot reproduce: STOP and report it; do not repair what you could not see.
2. **Red → green per blocker:** each new test fails on the PIN bytes for the named reason and passes after your change; paste both.
3. **Gates:** as root, `mkdir -p /tmp/e2r1 && /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e2r1/bt` TWICE (`rm -rf /tmp/e2r1/bt` between; counts bitwise); as non-root, `mkdir -p /tmp/e2r1nr && chmod 777 /tmp/e2r1nr && setpriv --reuid=65534 --regid=65534 --clear-groups env HOME=/tmp/e2r1nr /usr/bin/python3 -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e2r1nr/bt` → `0 failed` (the root venv is unreadable to `nobody`; the system python3 carries pytest 9.1.1); `bash -n` on both scripts; `/root/venv-agent-factory/bin/python -m pyflakes tests/test_s0_05_egress.py`; `python3 scripts/ap_screen.py --tests tests/test_s0_05_egress.py` (every hit graded); `python3 scripts/no_laya_in_gates.py` (rc 0).
4. **Mutants** (AF-AP-78: each in a SCRATCH COPY under `/tmp/e2r1mut/`, never in the shared tree; compile rc and the collected count pasted per row; a syntax kill is INVALID, never "killed"; the killing test NAMED): the verifier's M10, M11, M16, M17, M20, M21, M22 re-run on your bytes, plus one per repair — drop the up-front validation (the non-root F19 cases red), move the claim after creation (the race test red), drop the ownership check in `cleanup` (the two-runner test red), `printf` instead of the encoder (the quote test red), drop the SIGKILL escalation (the TERM-ignoring test red). A survivor is a finding or a proven equivalent, stated.
5. **Census:** at the end `ip netns list` empty, `ip -o link show type veth` empty, `/run/s0-05-egress` empty or absent; every process you started killed BY PID (never `pkill -f`).
6. **Report** `tasks/briefs/s0-05-support/E2-R1-report.md`, DATA not prose: files:lines per repair, the red → green pairs, the gate outputs, the mutant table, the census, DISCREPANCIES (anything in this brief the tree contradicts), NOT-done. `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/s0-05-support/E2-R1-report.md --root .` with NO `--map` flags: cite full repo-relative paths (at most three fix rounds, then paste and finish).

## Do-nots
Do NOT spawn subagents. Touch only the boundary; report adjacent defects, never fix them. Never skip, xfail or quarantine a test to get green, and never mark a test root-only to hide a non-root failure. Never run `git stash`, `git checkout -- <file>` or `git restore` in the shared tree: other work is live in it (the coordinator commits through `scripts/safe_commit.sh`). Never copy the repository tree (about 2 GB of disk is free); scratch copies hold only the files a mutant needs, removed at the end. Never touch the PC, the bridge, or any server. A long gate runs in ONE foreground call.

## PREMISE — MEASURED at authoring (sandbox @ 280d3df)
```
$ date -u; git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-60
2026-09-23T02:59:30Z
280d3df transcripts: scrubbed sandbox chat digests (2026-09-
$ for f in <boundary + readers>; do sha256(git show 280d3df:$f)[:16]; lines; done
324ffdd9aa646531   258 proofs/S0-05/netns_lib.sh
24087a298ab1b9f9   159 proofs/S0-05/tools/pc/run_s0_05_units.sh
ce86f3a2d9bb81c9  1243 tests/test_s0_05_egress.py
44b1428b431303a1   139 proofs/S0-05/run_canaries.sh
5d9c502e862d0507   380 proofs/S0-05/check_egress.py
$ git diff --stat 9223162 280d3df -- proofs/S0-05 tests/test_s0_05_egress.py   (empty = the VERIFY-E2 PIN bytes)
$ ls proofs/S0-05/result.json 2>&1   (not minted: no attested-input re-mint)
ls: cannot access 'proofs/S0-05/result.json': No such file or directory
$ grep -n -E '^egress_ns_[a-z_]+\(\)|iptables -P|F19|owner_file|egress_ns_owner|kill -0|remaining|TERM|KILL' proofs/S0-05/netns_lib.sh | cut -c1-140
41:egress_ns_host_if() { printf 'eh%s\n' "$(_egress_hash "$1")"; }
42:egress_ns_if()      { printf 'en%s\n' "$(_egress_hash "$1")"; }
49:egress_ns_host_ip() { printf '10.201.%s.1\n' "$(_egress_octet "$1")"; }
50:egress_ns_ip()      { printf '10.201.%s.2\n' "$(_egress_octet "$1")"; }
54:egress_ns_resolver() { printf '10.201.%s.53\n' "$(_egress_octet "$1")"; }
56:egress_ns_capable() {
66:egress_ns_create() {
77:  local owner_file; owner_file=$(egress_ns_owner_file "$ns")
78:  if [ -f "$owner_file" ]; then
80:    owner_pid=$(cat "$owner_file" 2>/dev/null)
81:    if [ -n "$owner_pid" ] && [ "$owner_pid" != "$$" ] && kill -0 "$owner_pid" 2>/dev/null; then
114:  mkdir -p "$EGRESS_OWNER_DIR" && printf '%s\n' "$$" > "$(egress_ns_owner_file "$ns")"
127:    ip netns exec "$ns" iptables -P "$chain" DROP || return 1
134:    # F19: the host part must be a dotted-quad IPv4 literal (not CIDR, not hostname, not empty).
150:egress_ns_create_isolated() {
166:egress_ns_gate_state() {
175:egress_ns_mechanism() {
183:egress_ns_run() { local ns=$1; shift; ip netns exec "$ns" "$@"; }
185:egress_ns_rules() { ip netns exec "$1" iptables -S | sed 's/[[:space:]]\+/ /g; s/[[:space:]]*$//' | LC_ALL=C sort; }
196:egress_ns_drop_counter() {
211:    ip netns exec "$ns" iptables -P "$chain" ACCEPT || return 1
231:egress_ns_owner_file() { printf '%s/%s.owner\n' "$EGRESS_OWNER_DIR" "$1"; }
236:egress_ns_destroy() {
244:  local remaining=50  # 50 * 0.1s = 5s
245:  while [ $remaining -gt 0 ]; do
248:      kill -0 "$pid" 2>/dev/null && alive=1 && break
252:    remaining=$((remaining - 1))
257:  rm -f "$(egress_ns_owner_file "$ns")"
$ grep -n -E '^cleanup|NS_LIVE|trap |LAUNCH\[|egress_ns_destroy|printf .*unit|units.json' proofs/S0-05/tools/pc/run_s0_05_units.sh | cut -c1-140
13:# Units that cannot run are declared in units.json as `not-run` with their reason — check_egress.py
52:LAUNCH[hermes-acp]="/usr/bin/python3 $S0_01_TOOLS/pc_launch.py --leg run-1 --model s0-01-pong"
54:LAUNCH[buzz-acp]="/usr/bin/python3 $S0_01_TOOLS/pc_launch.py --leg run-1 --model s0-01-pong"
72:NS_LIVE=""
73:cleanup() { for ns in $NS_LIVE; do egress_ns_destroy "$ns"; done; }
74:trap cleanup EXIT INT TERM
92:  NS_LIVE="$NS_LIVE $ns"
102:    egress_ns_destroy "$ns"; continue
108:  if [ -n "${LAUNCH[$unit]:-}" ]; then
111:    egress_ns_run "$ns" setsid ${LAUNCH[$unit]} </dev/null \
125:      egress_ns_destroy "$ns"; continue
132:  # F9: stop the unit through the namespace (egress_ns_destroy kills all processes inside),
134:  egress_ns_destroy "$ns"
137:# units.json: every unit the plan names, run or NOT, with its reason.
139:  printf '{\n  "units": [\n'
145:      printf '    {"unit": "%s", "status": "run", "note": "%s"}' "$unit" "$why"
147:      printf '    {"unit": "%s", "status": "not-run", "reason": "%s"}' "$unit" "$why"
152:    printf '    {"unit": "%s", "status": "not-run", "reason": "%s"}' "$unit" "${ABSENT[$unit]}"
155:} > "$EVIDENCE_ROOT/units.json"
157:echo "=== units.json ==="; cat "$EVIDENCE_ROOT/units.json"
$ grep -n -E '^def test_(allow_entry|runner_live|live_sibling|destroy|owner|create)' tests/test_s0_05_egress.py
978:def test_live_sibling_namespace_is_refused():
1021:def test_destroy_kills_all_namespace_processes():
1066:def test_runner_live_leg(tmp_path):
1231:def test_allow_entry_must_be_ipv4_literal(entry):
$ grep -c '^def test_' tests/test_s0_05_egress.py
64
$ mkdir -p /tmp/e2r1/p && python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e2r1/p/bt | tail -1   (root, sandbox)
122 passed in 53.00s
$ mkdir -p /tmp/e2r1nr && chmod 777 /tmp/e2r1nr && setpriv --reuid=65534 --regid=65534 --clear-groups env HOME=/tmp/e2r1nr python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e2r1nr/bt | tail -1   (non-root)
env: '/root/venv-agent-factory/bin/python': Permission denied
$ ip netns list; ip -o link show type veth | wc -l   (census after)
0
$ setpriv --reuid=65534 --regid=65534 --clear-groups env HOME=/tmp/e2r1nr /usr/bin/python3 -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e2r1nr/bt | tail -1   (non-root)
3 failed, 110 passed, 9 skipped in 4.50s
FAILED tests/test_s0_05_egress.py::test_allow_entry_must_be_ipv4_literal[cidr]
FAILED tests/test_s0_05_egress.py::test_allow_entry_must_be_ipv4_literal[hostname]
FAILED tests/test_s0_05_egress.py::test_allow_entry_must_be_ipv4_literal[empty-host]
```
