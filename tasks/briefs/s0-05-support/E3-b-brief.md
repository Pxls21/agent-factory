# E3-b — S0-05's collector records the unit's whole allow-set, C0 asks a path the real services answer, the preflight grades what the checker grades, and a stop stops the runner

PIN: 148e38d (origin head at authoring; the boundary below is byte-identical to HEAD, measured in the premise block).
LANE: s0-05-e3b (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation — `isolation: "worktree"` fails on
this tree; root is needed: every namespace test runs as uid 0). Honey `ultra` Lever-2: your report is DATA — files:lines, pasted
counts, discrepancies, NOT-done. Do NOT spawn subagents.

CONTRACT SOURCES (read them whole before you design): `tasks/briefs/s0-05-support/E3-brief.md` and `E3-report.md` (§9 DISCREPANCY 1
is item A below; the "Adjacent defects" under §9 are items A's input domain and R4; the "Unmeasured on the PC" line is now measured,
premise block) · `tasks/briefs/s0-05-support/CD1-AMENDMENT.md` (A8: every allow entry is formed from the namespace's host address and
a port) · `docs/08_DECISION_LOG.md` D-051 (the pair's allow-set is exactly {relay, OmniRoute}) · the checker's module docstring
(`proofs/S0-05/check_egress.py:1-60`: its phase order is part of the contract).

BOUNDARY (exact): MODIFY `proofs/S0-05/run_canaries.sh`, `proofs/S0-05/check_egress.py`, `proofs/S0-05/tools/pc/run_s0_05_units.sh`,
`proofs/S0-05/netns_lib.sh` (ONLY item G: the allow-entry rule moved into one function), `proofs/S0-05/canaries/c0_allowed_target.sh`
(ONLY item P: the record carries the path), `tests/test_s0_05_egress.py`; CREATE `tasks/briefs/s0-05-support/E3-b-report.md` (write it
incrementally from the start). Read anything. Do NOT modify the committed bundles under `proofs/S0-05/fixtures/` (measured: all seven
have one allowed entry and one C0 whose target equals it, so all seven stay valid under item C; a bundle you cannot keep valid is a
DISCREPANCY), `proofs/S0-05/spec.json`, any other canary or `_emit.sh`, anything under `proofs/S0-01/`, `scripts/`, `.github/`,
`.claude/`, `sandbox-kit/`, any hook or `pyproject.toml` (a line you cannot meet without one of them is a DISCREPANCY, never a silent
edit). Another sandbox agent may run in this tree on disjoint files (its report under `tasks/briefs/ci/`): never touch, run or revert
it. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or `git push` here. No outward-facing action of
any kind. No PC or bridge use: the live leg is the coordinator's after your landing. Every namespace, veth, nat rule, sysctl, claim,
`/etc/netns` entry and process you create is destroyed by NAME or PID from your own record, never by `pkill -f`; the census must read
empty at the end (pasted). The sandbox has about 1.9 GB free.

CODE INTEL FIRST: `graft ask` before any grep for code questions; `scripts/lane_context.sh -q '<question>' -s check_positive_control
-s expected_rules -s egress_ns_create -s cleanup -o /tmp/e3b/pack.md proofs/S0-05/run_canaries.sh proofs/S0-05/check_egress.py
proofs/S0-05/tools/pc/run_s0_05_units.sh proofs/S0-05/netns_lib.sh` gives you the quartet pack in one call.

This is defensive testing of the owner's own containment boundary (S0-05, "no direct egress"): the egress canaries, the namespace
gate, the health probes and the negative controls are the proof's instruments on the owner's own machines.

## Why

S0-05 is one of the two proofs still ABSENT. E3 landed the live-unit launch recipe (GATED-PENDING-VERIFY; VERIFY-E3 will grade E3 and
this lane together). The next step is the live leg on the PC, and each of these measured defects stops it:

1. **The collector records ONE allowed entry** (`run_canaries.sh:25`, `:130`). The pair has two (D-051), so the pair's bundle can
   never pass the rule pin: E3 measured `egress-rules-unpinned` on a real pair leg (E3 §9), and the digests differ below.
2. **C0 asks a path the real services refuse.** C0 sends `GET /v1/models` and the checker needs a 2xx. Measured on the PC: the real
   OmniRoute answers 401 there (it now requires a key) and the real relay answers 404. Both units would read
   `positive-control-failed` on the live leg. Both services answer 200 on a health path (`/api/health`, `/health`).
3. **The preflight passes what the checker fails.** `run_s0_05_units.sh:354` says it preflights "the exact predicate the proof
   consumes", but `:358` passes any HTTP answer (curl without `-f`, no status read). It would pass a 401 or 404, launch the unit, and
   the checker would then fail it.
4. **A stop does not stop.** `trap cleanup EXIT INT TERM` (`:283`) runs `cleanup` on SIGTERM and then CONTINUES; E3 measured the
   runner going on to its checker after SIGTERM.
5. **The collector does arithmetic on its raw input** (`run_canaries.sh:28-29`): an overflowing port wraps negative, a leading zero is
   read as octal, and a subscript that names a set variable runs a command substitution (measured below).
6. **Two grammars for one entry.** The library refuses non-ASCII digits and leading zeros; the checker's `IPV4_PORT` (`\d`, `:94`)
   accepts both (measured: it returns `('10.201.7.1', '٢٠١٢٨')`). Fail-closed today (the digest never matches), but it names the
   wrong class, and item C now compares C0 targets against these entries.

## The contract (coordinator, decided; do not re-litigate — a line you cannot meet is a DISCREPANCY with its measurement, never a silent change)

The E3 contract stands except where this brief amends it. Refusal texts below are exact.

**G — one allow-entry rule, three places.** `netns_lib.sh` gains `egress_allow_entry_ok <entry>`: a SILENT predicate (no output;
status 0 valid, 1 not) holding exactly the rule `egress_ns_create` applies today (`netns_lib.sh:79-89` at the PIN: a dotted quad of
four decimal octets 0-255 with no leading zero, a lone 0 allowed; a port 1-65535 with no leading zero and at most five digits, the
digit bound checked before any arithmetic). `egress_ns_create` calls it for every entry and keeps its text, status and ordering
byte-for-byte (`egress: allow entry must be <ip>:<port>, got '<entry>'`, status 64, before any namespace, veth, rule or record
work). The rule is ASCII-only under any locale. The checker's `_split_ip_port` (`check_egress.py:198`) accepts exactly the same set:
ASCII digits only, no leading-zero octet or port; its two refusal texts stay. A PARITY test drives one table of entries through the
bash predicate and `_split_ip_port` and asserts the same accept/refuse on every row. Rows at least: a valid entry, `0.0.0.0:1`,
`255.255.255.255:65535`, a leading-zero octet, a leading-zero port, octet 256, port 0, port 65536, a six-digit port, a 20-digit port,
Arabic-Indic digits in the port and in an octet (built in Python and passed as argv), a space, a tab, VT, FF and NL inside and at the
end (AF-AP-135's ASCII form), an empty string, a missing port, a trailing colon, an IPv6 literal, a hostname.

**A — the collector records the whole allow-set.** `run_canaries.sh <unit> <ns> <allowed> [evidence-root] [blocked ip:port] [venue]`:
`<allowed>` is a comma-separated list of ENTRIES; an ENTRY is `<ip>:<port>`, optionally followed by a probe path (item P). A single
entry without a path stays valid: the four existing call sites (T:634, T:863, T:1241, T:1255) keep working unchanged.
- Arguments are validated in the order 3, 5, 6; the first failure exits 64 with its text on stderr, BEFORE any arithmetic on an input,
  any namespace access, any directory or file creation and any canary. (A nonexistent namespace name discriminates this: a namespace
  access would produce the existing exit-3 drop-counter refusal instead.)
- `run_canaries: allowed entry '<entry>' is not <ip>:<port>[/<path>]` — an empty entry (an empty argument; a leading, trailing or
  doubled comma), an ip:port part that `egress_allow_entry_ok` refuses, or a path that item P refuses.
- `run_canaries: allowed entry '<ip>:<port>' is listed twice` — two entries with the same ip:port (the path is not part of identity).
- `run_canaries: blocked entry '<value>' is not <ip>:<port>` — an explicit argument 5 the predicate refuses (no path allowed there).
- `run_canaries: blocked entry '<ip>:<port>' is in the allowed set` — explicit or default.
- `run_canaries: default blocked port 65536 is out of range; pass a blocked entry` — the first entry's port is 65535.
- The default blocked entry is `<the namespace's host ip>:<the FIRST entry's port + 1>`, computed only after validation (the
  single-entry case keeps today's value).
- C0 runs once per entry, in the given order, with the entry's ip:port as its target and the entry's path.
- gate.json `allowed` = the entries' ip:port parts, in the given order, without paths. Nothing else in gate.json or runtime.json
  changes. The venue refusal and the two drop-counter refusals keep their texts.

**P — the probe path.** A PATH is `/` followed by at most 63 characters from `[A-Za-z0-9._~/-]` (ASCII only). An entry without a
path probes `/v1/models` (the canary's default today), passed explicitly. `c0_allowed_target.sh` adds `path=<path>` to its record —
the one change in that file (`emit_canary` keeps a non-integer value as a string, `_emit.sh:25-28`). The checker never grades `path`
(the seven committed bundles have none and stay valid); it is evidence a reader needs, because the target alone no longer says what
was asked.

**C — the checker's positive control is per entry.** `check_positive_control` (`check_egress.py:265`) takes the unit's
`gate["allowed"]` (PHASE 2's call site, `:444`, passes it). A unit proves its positive control only if its C0 records' targets contain
every allowed entry exactly once and nothing else, and every C0 record meets today's predicate (status `run`, rc 0, an int that is not
a bool, 2xx). Every failure keeps the exact one-line text `positive-control-failed: <unit>` (six parametrized cases pin it, T:261),
including the three new shapes: an allowed entry with no C0 record, a C0 target outside the allow-set, two C0 records for one target.
The phase order is unchanged; the PASS line's `positive controls N/M` keeps its meaning (units proven over units checked).

**R — the runner.**
- **R1 — the probe paths.** Every entry the runner forms carries its service's health path: OmniRoute `/api/health`, the relay
  `/health`, as two named constants in the runner with the measurement cited in a comment (the PC, 2026-09-23 06:57Z: OmniRoute
  `/api/health` 200 application/json, `/v1/models` 401; the relay `/health` 200 text/plain, `/v1/models` 404). `egress_ns_create`
  still receives exactly the ip:port entries, never a path.
- **R2 — the preflight grades what the checker grades.** An entry passes only if the request the collector will make for it (the same
  path, the proxy variables scrubbed, the canaries' connect and total timeouts) gets rc 0 and a 2xx. Preferred shape: run the real
  `canaries/c0_allowed_target.sh` inside the namespace with the canaries' scrubbed environment and grade its record with the checker's
  own predicate; a hand-written curl must match the request, the timeouts and the predicate exactly. No HTTP answer keeps today's texts
  (stderr `positive-control-unreachable: <unit> <ip:port>`; row `not-run|positive control unreachable: <ip:port> not reachable from
  <ns>` — T:2273 and T:2542 pin them). An HTTP answer outside 2xx: stderr `positive-control-not-2xx: <unit> <ip:port><path> HTTP
  <code>` and row `not-run|positive control not 2xx: <ip:port><path> answered HTTP <code> from <ns>`; the namespace is destroyed as
  today and no unit launches.
- **R3 — the collector gets the unit's whole entry list** (`:436`), comma-joined, in the runner's order (the pair: relay, then
  OmniRoute).
- **R4 — a stop stops.** `trap cleanup EXIT`, `trap 'exit 130' INT`, `trap 'exit 143' TERM` (`:283`). After SIGTERM the runner exits
  143 with `cleanup` run once; it starts no further unit leg, writes no units.json, and never runs the census comparison or the
  checker. SIGINT the same with 130.

**S — nothing else changes.** C1-C6, the gate-state and mechanism phases, the rule-digest check, units.json's shape, A1-A8, D-051's
DNAT and E3's X1-X4 stay as landed; an existing assertion may only become stricter.

**Declared limits** (in the runner header and the report): the two probe paths are facts about the services on the PC today; if one
changes, the preflight refuses with the named not-2xx reason (fail closed) and the fix is a one-line constant. A 2xx from a health path
proves that the unit's namespace reaches that ip:port; it does not prove the model API behind it would serve the unit (that is S0-03).

## Tests (`tests/test_s0_05_egress.py`; root-gated where they need namespaces, with the existing `NEEDS_NETNS` pattern)

Every item is written RED first against the PIN bytes (paste the RED run — the failures must be the PIN behaviour this brief measured,
not an import error), then GREEN. The existing 183 tests stay; a changed expectation names its item in a comment. At least:
- G: the parity table, every row through both implementations.
- A: every refusal text with exit 64 and no evidence directory; the injection row as argv built in Python (a port of the form
  `NS[$(touch <file>)]`: on the PIN the command RUNS, measured) with the file absent after; the overflow row; a two-entry run against
  a real namespace (root) whose gate.json `allowed` equals both entries in order, whose two C0 records come in order with their paths,
  and whose rules digest equals the checker's derivation (`check_runtime_and_rules` passes).
- P: the record's `path`; the stand-in's request log shows that path was asked.
- C: the three new shapes read `positive-control-failed: <unit>`; a two-entry bundle with both C0 records passes the positive control;
  the seven committed bundles keep their verdicts (the existing tests).
- R: the real pair leg (`test_d_pair_leg_reaches_the_relay_through_the_dnat`, stand-ins through the recorded override): gate.json
  `allowed` == [relay, OmniRoute], two C0 records, 2xx, paths `/health` and `/api/health`, the stand-ins' logs show those paths, and
  `check_positive_control` and `check_runtime_and_rules` pass on its bundle (paste the full checker's first line on that bundle and say
  what it is and why). A stand-in shaped like the real services (200 on its health path, 401 or 404 on `/v1/models`) passes the
  preflight and C0 — RED on the PIN, which asks `/v1/models`. A stand-in that answers 401 on the health path gives the not-2xx row, no
  unit launched, census clean. SIGTERM mid-leg: exit 143, `=== checker ===` never printed, census clean (E3's X4 case 1 made
  stricter). A two-unit run stopped during its first leg never creates the second unit's namespace.
- The stand-in `_listener` (T:1571) answers 200 on every path: give it a per-path status map (default 200) rather than a second
  listener.

## Mutants (scratch-copy restore only — never a git restore in this shared tree; each mutant compiles (`bash -n` / `py_compile`) and collects, AF-AP-78)

At least: B1 gate.json records only the first entry · B2 C0 only for the first entry · B3 the path not passed to C0 · B4 the collector's
validation removed (raw arithmetic back) · B5 the duplicate refusal removed · B6 the blocked-in-set refusal removed · B7 the checker's
"nothing else" half removed · B8 the checker's "every allowed entry" half removed · B9 the checker's grammar back to `\d` · B10 the
preflight back to any HTTP answer · B11 the trap back to `EXIT INT TERM` · B12 the runner passes only the OmniRoute entry (the PIN's
`:436`) · B13 C0's `path=` removed · B14 `egress_ns_create` stops calling the shared predicate for one condition (say which). One row
each: mutant · compiles · collected · killed-by (test id) / SURVIVED / EQUIVALENT with the reason. Before you count a kill, run the
killing test on the UNMUTATED tree and paste that it passes (AF-AP-138: an assertion that also fails on unmutated code proves nothing).

## Gates (paste verbatim, each with its invocation)

`mkdir -p /tmp/e3b/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider
--basetemp=/tmp/e3b/bt` twice as root (`rm -rf /tmp/e3b/bt` after each) · the same file once as `nobody` (the non-root venue; the
namespace tests skip, everything else passes): `rm -rf /tmp/e3bnr && mkdir -p /tmp/e3bnr && chmod 1777 /tmp/e3bnr && setpriv
--reuid=65534 --regid=65534 --clear-groups env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_s0_05_egress.py
-q -p no:cacheprovider --basetemp=/tmp/e3bnr/bt` · `bash -n` on the four shell files · `shellcheck` if present (say if absent) ·
`/root/venv-agent-factory/bin/python -m pyflakes proofs/S0-05/check_egress.py tests/test_s0_05_egress.py` · `python3
scripts/ap_screen.py proofs/S0-05/check_egress.py` and `python3 scripts/ap_screen.py --tests tests/test_s0_05_egress.py` · `python3
scripts/no_laya_in_gates.py` · the census, pasted: `ip netns list`, `ip -o link show type veth`, `iptables -t nat -S PREROUTING`,
`ls /etc/netns`, the owner dir, and no stand-in or listener pid of yours alive.

## Report (`tasks/briefs/s0-05-support/E3-b-report.md`)

PREMISE re-measured (item 1 of your work: re-run the premise commands below on the PIN and stop CONTRACT-INVALID on a mismatch that
changes the contract; the two bridge probes are the coordinator's — quote them, do not run them) · what changed per item (file:line
refs) · RED then GREEN (pasted) · the mutant table · gates (pasted) · the live-leg delta for the coordinator's operator recipe (the
entries with their paths, the new not-2xx row, what exit 143 means) · DISCREPANCIES · NOT-done (first-class: nothing here ran on the
PC). Lint floor: `python3 scripts/report_lint.py --min-refs 15 --map RC=proofs/S0-05/run_canaries.sh --map C=proofs/S0-05/check_egress.py
--map PC=proofs/S0-05/tools/pc/run_s0_05_units.sh --map L=proofs/S0-05/netns_lib.sh --map CAN=proofs/S0-05/canaries/c0_allowed_target.sh
--map T=tests/test_s0_05_egress.py tasks/briefs/s0-05-support/E3-b-report.md --root .`; apply its `fix:` hints for at most three
rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 06:5xZ, sandbox as root @ 148e38d)

````
# $SP below is the coordinator's scratchpad (/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad);
# re-run with any directory of your own.
$ date -u '+%Y-%m-%d %H:%MZ'
2026-09-23 06:58Z

$ git rev-parse origin/claude/soundbox-kit-migration-iz1jwf
148e38dc044d576e1f9b2c75e8f7602baaf6c653

$ git diff --stat origin/claude/soundbox-kit-migration-iz1jwf HEAD -- proofs/S0-05 tests/test_s0_05_egress.py | wc -l
0

$ for f in proofs/S0-05/run_canaries.sh proofs/S0-05/check_egress.py proofs/S0-05/tools/pc/run_s0_05_units.sh proofs/S0-05/canaries/c0_allowed_target.sh tests/test_s0_05_egress.py; do printf '%s %s %s\n' "$(sha256sum < $f | cut -c1-16)" "$(wc -l < $f)" "$f"; done
44b1428b431303a1 139 proofs/S0-05/run_canaries.sh
df3ad6fed3aa5067 485 proofs/S0-05/check_egress.py
ffb3453a17427a63 508 proofs/S0-05/tools/pc/run_s0_05_units.sh
2710a809b664ea7d 15 proofs/S0-05/canaries/c0_allowed_target.sh
87e6044a0567a15f 2550 tests/test_s0_05_egress.py

$ grep -n 'ALLOWED\|BLOCKED\|HOST_IP=\|VENUE=\|"allowed"\|mkdir -p\|^DROP_BEFORE\|run_canary c0' proofs/S0-05/run_canaries.sh
25:ALLOWED=${3:?allowed ip:port}
27:HOST_IP=$(egress_ns_host_ip "$NS")
28:ALLOWED_PORT=${ALLOWED##*:}
29:BLOCKED=${5:-"$HOST_IP:$((ALLOWED_PORT + 1))"}
30:VENUE=${6:-}
72:DROP_BEFORE=$(egress_ns_drop_counter "$NS")
79:mkdir -p "$OUT"
83:run_canary c0_allowed_target.sh "$UNIT" "$ALLOWED"
112:run_canary c6_blocked_local.sh "$UNIT" "$BLOCKED"
124:python3 - "$OUT" "$UNIT" "$NS" "$ALLOWED" "$RULES_SHA" "$DROP_BEFORE" "$DROP_AFTER" \
130:        "allowed": [allowed], "rules_sha256": rules_sha}

$ grep -n 'trap cleanup\|allowed=(\|run_canaries.sh\|PREFLIGHT\|/v1/models\|positive control unreachable\|check_egress.py" "' proofs/S0-05/tools/pc/run_s0_05_units.sh
12:# ONLY that unit's allowed destinations (A8), PREFLIGHT that each one answers from inside it, launch
49:# PREFLIGHT, not a workaround: a service bound only to 127.0.0.1 is unreachable from a namespace (a
53:# positive control unreachable: ...`; the script never falls back to a listener of its own.
283:trap cleanup EXIT INT TERM
329:  allowed=("$host_ip:$OMNI_PORT")
330:  [ "$unit" = buzz-acp ] && allowed=("$host_ip:${PIN[RELAY_PORT]}" "$host_ip:$OMNI_PORT")
354:  # PREFLIGHT the exact predicate the proof consumes (AF-AP-24): C0 to EVERY allowed destination,
358:    egress_ns_run "$ns" curl -sS --noproxy '*' --connect-timeout 5 -o /dev/null "http://$entry/v1/models" \
365:    RESULT[$unit]="not-run|positive control unreachable: $unreachable not reachable from $ns"
436:  bash "$P/run_canaries.sh" "$unit" "$ns" "$(egress_ns_host_ip "$ns"):$OMNI_PORT" "$EVIDENCE_ROOT" "" pc
508:python3 -B "$P/check_egress.py" "$EVIDENCE_ROOT" --units "$(IFS=,; echo "${UNITS[*]}")"

$ grep -n 'def expected_rules\|def check_positive_control\|egress-rules-unpinned\|positive-control-failed\|check_positive_control(' proofs/S0-05/check_egress.py
22:     row AF-AP-1 in docs/INCIDENT-LOG.md). Exit 1, `positive-control-failed: <unit>`.
208:def expected_rules(allowed):
265:def check_positive_control(records, unit):
271:        raise Failure(f"positive-control-failed: {unit}")
276:            raise Failure(f"positive-control-failed: {unit}")
333:        raise Failure(f"egress-rules-unpinned: {unit} recorded rules do not hash to the gate digest")
335:        raise Failure(f"egress-rules-unpinned: {unit} rules are not the pinned allow-list for {gate['allowed']}")
444:        positives += check_positive_control(records, unit)

$ grep -n 'emit_canary\|path=' proofs/S0-05/canaries/c0_allowed_target.sh
9:unit=${1:?unit} target=${2:?target} path=${3:-/v1/models}
15:emit_canary C0 "$unit" "$target" http-get "$rc" run "$detail" "http_status=$code"

$ grep -n 'run_canaries.sh"), "curl"' tests/test_s0_05_egress.py
634:        ["bash", str(PROOF / "run_canaries.sh"), "curl", "s0-05-e1-does-not-exist",
863:            ["bash", str(PROOF / "run_canaries.sh"), "curl", ns, f"127.0.0.1:{port}",
1241:        ["bash", str(PROOF / "run_canaries.sh"), "curl", "s0-05-e2-nonexistent-ns",
1255:    args = ["bash", str(PROOF / "run_canaries.sh"), "curl", "s0-05-e2-nonexistent-ns",

$ grep -n 'positive-control-failed: curl\|200 <= c0\[0\]\|egress-rules-unpinned\|def _listener' tests/test_s0_05_egress.py
261:    assert result.stdout.splitlines()[0] == "positive-control-failed: curl"
399:        "egress-rules-unpinned: curl recorded rules do not hash to the gate digest"
413:    assert result.stdout.splitlines()[0].startswith("egress-rules-unpinned: curl rules are not the pinned allow-list")
424:    assert result.stdout.splitlines()[0].startswith("egress-rules-unpinned: curl rules are not the pinned allow-list")
434:    assert result.stdout.splitlines()[0].startswith("egress-rules-unpinned: curl rules are not the pinned allow-list")
872:        assert len(c0) == 1 and c0[0]["rc"] == 0 and 200 <= c0[0]["http_status"] < 300
1571:def _listener(workdir, port, host="0.0.0.0", name="listener"):

$ python3 -c "import sys; sys.path.insert(0,'proofs/S0-05'); import check_egress as c; one=['10.201.219.1:20128']; two=['10.201.219.1:3999','10.201.219.1:20128']; a=c.rules_digest(c.expected_rules(one)); b=c.rules_digest(c.expected_rules(two)); print('digest(one entry) :', a[:16]); print('digest(two entries):', b[:16]); print('equal:', a==b)"
digest(one entry) : d251ea78bc708b35
digest(two entries): e086277caab22ed3
equal: False

$ python3 -c "import sys, inspect; sys.path.insert(0,'proofs/S0-05'); import check_egress as c; print('check_positive_control params:', list(inspect.signature(c.check_positive_control).parameters))"
check_positive_control params: ['records', 'unit']

$ for g in $(git ls-files 'proofs/S0-05/*gate.json'); do d=$(dirname $g); python3 -c "import json,sys; d=sys.argv[1]; al=json.load(open(d+'/gate.json'))['allowed']; t=[json.loads(l)['target'] for l in open(d+'/canaries.jsonl') if l.strip() and json.loads(l)['canary']=='C0']; print(d, 'allowed', al, 'C0 targets', t)" $d; done
proofs/S0-05/fixtures/evidence-bare-unshare/curl allowed ['10.201.136.1:12800'] C0 targets ['10.201.136.1:12800']
proofs/S0-05/fixtures/evidence-gate-off/curl allowed ['10.201.136.1:12800'] C0 targets ['10.201.136.1:12800']
proofs/S0-05/fixtures/evidence-mechanism-sandbox/curl allowed ['10.201.136.1:12800'] C0 targets ['10.201.136.1:12800']
proofs/S0-05/fixtures/evidence-synthetic-pass/curl allowed ['10.201.7.1:20128'] C0 targets ['10.201.7.1:20128']
proofs/S0-05/fixtures/evidence-synthetic-pass/hermes-acp allowed ['10.201.7.1:20128'] C0 targets ['10.201.7.1:20128']
proofs/S0-05/fixtures/evidence-synthetic-uid0/curl allowed ['10.201.7.1:20128'] C0 targets ['10.201.7.1:20128']
proofs/S0-05/fixtures/evidence-synthetic-uid0/hermes-acp allowed ['10.201.7.1:20128'] C0 targets ['10.201.7.1:20128']

$ bash -x proofs/S0-05/run_canaries.sh u s0-05-e3b-none 10.0.0.1:9223372036854775807 /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/e3b-ev '' x 2>&1 | grep -E '^\+ (ALLOWED_PORT|BLOCKED)='; echo "rc=${PIPESTATUS[0]}"
+ ALLOWED_PORT=9223372036854775807
+ BLOCKED=10.201.130.1:-9223372036854775808
rc=64

$ bash -c 'cleanup(){ echo cleanup-ran; }; trap cleanup EXIT INT TERM; kill -TERM $$; echo continued-after-TERM; exit 0'; echo rc=$?
cleanup-ran
continued-after-TERM
cleanup-ran
rc=0

# The REAL collector, bogus venue x (the arithmetic at line 29 runs before the venue check at 32-35):
$ bash proofs/S0-05/run_canaries.sh u s0-05-e3b-none '10.0.0.1:a[$(touch $SP/e3b-inj-proof)]' $SP/e3b-ev '' x
proofs/S0-05/run_canaries.sh: line 29: a: unbound variable
rc=1
the injected command did not run
no evidence dir
$ bash proofs/S0-05/run_canaries.sh u s0-05-e3b-none '10.0.0.1:NS[$(touch $SP/e3b-inj-proof)]' $SP/e3b-ev '' x
proofs/S0-05/run_canaries.sh: line 29: s0: unbound variable
rc=1
the injected command RAN
no evidence dir
$ bash proofs/S0-05/run_canaries.sh u s0-05-e3b-none '10.0.0.1:VENUE[$(touch $SP/e3b-inj-proof)]' $SP/e3b-ev '' x
proofs/S0-05/run_canaries.sh: line 29: VENUE: unbound variable
rc=1
the injected command did not run
no evidence dir

$ bash -c 'echo "\$((010 + 1)) = $((010 + 1))"; echo "\$((08 + 1)) = $((08 + 1))"'
$((010 + 1)) = 9
bash: line 1: 08: value too great for base (error token is "08")
rc=1

$ python3 - <<'EOF'   # the checker's grammar vs the library's, on Arabic-Indic digits for the port 20128
checker _split_ip_port: ('10.201.7.1', '٢٠١٢٨')
bash[C] library port regex (netns_lib.sh:83): no match
bash[C.UTF-8] library port regex (netns_lib.sh:83): no match

$ /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py --collect-only -q -p no:cacheprovider | tail -1
183 tests collected in 0.12s

$ grep -n 'port=${entry##\*:}\|\[1-9\]\[0-9\]{0,4}\|allow entry must be' proofs/S0-05/netns_lib.sh
82:    ip=${entry%:*}; port=${entry##*:}
83:    if ! [[ "$port" =~ ^[1-9][0-9]{0,4}$ ]] || [ "$port" -gt 65535 ]; then
84:      echo "egress: allow entry must be <ip>:<port>, got '$entry'" >&2; return 64
87:      echo "egress: allow entry must be <ip>:<port>, got '$entry'" >&2; return 64
200:    ip=${entry%:*}; port=${entry##*:}

$ grep -n '^IPV4_PORT\|def _split_ip_port\|is not <ipv4>:<port>\|is out of range' proofs/S0-05/check_egress.py
94:IPV4_PORT = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3}):(\d{1,5})$")
198:def _split_ip_port(entry):
201:        raise Failure(f"gate-manifest-invalid: allow entry {entry!r} is not <ipv4>:<port>")
204:        raise Failure(f"gate-manifest-invalid: allow entry {entry!r} is out of range")

$ sed -n '513,522p' tasks/briefs/s0-05-support/E3-report.md   # E3's own SIGTERM measurement on the real runner
Adjacent defects (outside the brief's items; reported, NOT fixed):
- `run_canaries.sh:29` does `$((ALLOWED_PORT + 1))` on the entry's port: overflow wraps and a subscript runs a command
  substitution (demo pasted in section 2). No production caller reaches it with an unvalidated entry.
- The runner's `trap cleanup EXIT INT TERM` (PC:283; the same line at the PIN) runs `cleanup` on SIGINT/SIGTERM and
  then CONTINUES. Measured with one real run:
  ```
  runner exit rc=1 1.2s after SIGTERM
  hermes-acp row after SIGTERM: launch exited within the settle window; see /tmp/e3-ej635r_7/evidence/hermes-acp.launch.lo
  the runner went on to its checker after SIGTERM: True
  ```

# The coordinator's read-only probes of the REAL services on the PC, from the host (the lane cannot re-run these: no bridge
# use in this lane; quote them). The bridge's `bind: warning` noise is stripped by the sed filter shown.
$ timeout 100 bash scripts/pc.sh 'for p in / /health /healthz /api/health /v1 /v1/models /api/v1/models; do for port in 20128 3999; do printf "%s%s -> " "$port" "$p"; curl -sS --noproxy "*" -m 5 -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:$port$p" 2>&1; done; done' 2>&1 | sed 's#[^ ]*bash-hook.bash: line [0-9]*: bind: warning: line editing not enabled##g' | head -20; date -u
20128/ -> 307
3999/ -> 200
20128/health -> 404
3999/health -> 200
20128/healthz -> 200
3999/healthz -> 404
20128/api/health -> 200
3999/api/health -> 404
20128/v1 -> 401
3999/v1 -> 404
20128/v1/models -> 401
3999/v1/models -> 404
20128/api/v1/models -> 401
3999/api/v1/models -> 404
Wed Sep 23 06:55:54 UTC 2026

$ timeout 100 bash scripts/pc.sh 'for u in 20128/api/health 20128/healthz 3999/health 3999/ 20128/v1/models 3999/v1/models; do printf "%s -> " "$u"; curl -sS --noproxy "*" -m 5 -o /dev/null -w "%{http_code} %{content_type} %{size_download}\n" "http://127.0.0.1:$u" 2>&1; done; curl -sS --noproxy "*" -m 5 http://127.0.0.1:3999/health 2>&1 | head -c 200; echo; curl -sS --noproxy "*" -m 5 http://127.0.0.1:20128/api/health 2>&1 | head -c 300; echo' 2>&1 | sed 's#[^ ]*bash-hook.bash: line [0-9]*: bind: warning: line editing not enabled##g' | head -20; date -u
20128/api/health -> 200 application/json 54
20128/healthz -> 200 text/plain; charset=utf-8 3
3999/health -> 200 text/plain; charset=utf-8 2
3999/ -> 200 application/json 617
20128/v1/models -> 401 application/json 121
3999/v1/models -> 404  0
ok
{"status":"ok","timestamp":"2026-09-23T06:57:20.670Z"}
Wed Sep 23 06:57:20 UTC 2026
# (20128 = OmniRoute, the runner's OMNI_PORT default, PC:66; 3999 = the relay, pins.PINNED_RELAY_URL ws://127.0.0.1:3999)
````
