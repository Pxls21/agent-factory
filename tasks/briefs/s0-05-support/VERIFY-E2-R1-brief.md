# VERIFY-E2-R1 — the targeted adversarial verify of E2-R1 (VERIFY-E2's seven blockers on S0-05)

**Role:** `adversarial-verifier` (Opus 5), IN THE SANDBOX as root (netns / iptables / veth are available here; the PC lane
user cannot create namespaces). Honey `full`: line-bounded findings, evidence anchors, SOLID/UNSURE on every claim. Your report
is DATA for the coordinator's gate; you return a GATE RECOMMENDATION, never a verdict. Do NOT spawn subagents.

**PIN:** `6f2589d` (the E2-R1 landing on origin). The working tree's S0-05 boundary is BYTE-IDENTICAL to the PIN (measured
below). Work on the tree READ-ONLY: every mutant, fixture and hostile input lives in a scratch copy under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ve2r1/` (a `git archive 6f2589d` of the boundary).
Point `EGRESS_OWNER_DIR` at a directory under that scratch root for every run you start by hand. The ONLY file you write in the
tree is your report.

**Authorization:** defensive work on the owner's own system: the proof's own library builds throwaway network namespaces on
loopback; nothing egresses beyond this container; no owner server runs in the sandbox. The census after EVERY live run:
`ip netns list`, `ip -o link show type veth`, `ls /run/s0-05-egress` and `ls <your scratch EGRESS_OWNER_DIR>`, all empty of
anything you created. Kill only processes you started, by pid from your own record; never `pkill -f`.

## What landed (file:line at the PIN; L = `proofs/S0-05/netns_lib.sh`, R = `proofs/S0-05/run_canaries.sh`, PC = `proofs/S0-05/tools/pc/run_s0_05_units.sh`, C = `proofs/S0-05/check_egress.py`, T = `tests/test_s0_05_egress.py`)

Contract (frozen): `tasks/briefs/s0-05-support/E2-R1-brief.md` items 1-6 (F11+F12, F2, F3, F4, F1, F14), which close the seven
blockers of `tasks/briefs/s0-05-support/VERIFY-E2-report.md`. This is the ONE focused repair (D-031); a finding that meets the
blocking predicate goes to the owner-visible record, not to another silent round. The builder's report
`tasks/briefs/s0-05-support/E2-R1-report.md` is an INPUT to attack, never evidence.

- **F11 + F12** every allow entry validated before any state — L:71-84 (the octet pattern L:73, the dotted quad L:74, the port
  test L:77, the address test L:80); the late checks in `_egress_apply_gate` (L:146) removed.
- **F2** the claim first and atomic — L:93-104: `mkdir "$claim_dir"` (L:94) takes a fresh claim; an existing claim whose owner
  is live and not `$$` → `namespace-live`, rc 65; otherwise "stale: take over atomically" (L:103). The destroy-first step calls
  `_egress_ns_teardown "$ns"` (L:109) so the fresh claim survives it; the F6 refusal (L:120) removes the claim and the record.
- **F1** destroy never returns 0 with a survivor — `_egress_ns_teardown` (L:258): SIGTERM, the 5 s wait, SIGKILL for survivors
  (L:276), a 2 s wait, then rc 1 with `egress: namespace <ns> still has live pids:<pids>` (L:302); `egress_ns_destroy` (L:314)
  removes the record and the claim (L:318) whatever the teardown returned.
- **F3** the runner's cleanup owns what it destroys — PC:74-80 `cleanup` destroys only names whose owner record is `$$` (PC:78);
  each destroyed name leaves `NS_LIVE` (PC:99, PC:109, PC:132, PC:142: `NS_LIVE=${NS_LIVE//$ns/}`).
- **F4** `units.json` encoded — PC:145-172: NUL-delimited fields into `mktemp`, then python `json.dump` (PC:159, PC:170).
- **F14** the live-leg test proves the stand-in ran — T:1066 `test_runner_live_leg`.
- Tests: T:1260 `test_destroy_kills_sigterm_ignoring_process`, T:1294 `test_create_race_one_wins`, T:1330
  `test_same_shell_recreate_succeeds`, T:1353 `test_cleanup_does_not_destroy_sibling_namespace`, T:1400
  `test_units_json_quotes_in_reason`, T:1423 `test_runner_refusal_does_not_destroy_sibling`, T:1489
  `test_allow_entry_must_be_ipv4_literal` (12 cases).

## PREMISE — MEASURED (coordinator, 2026-09-23 03:4x-04:1xZ, sandbox as root)

```
$ git diff --stat 6f2589d HEAD -- proofs/S0-05 tests/test_s0_05_egress.py
(empty = byte-identical)
$ sha256[:16] + lines at 6f2589d
234bb13ac0e475c6 320 proofs/S0-05/netns_lib.sh
44b1428b431303a1 139 proofs/S0-05/run_canaries.sh
4d3b917c6fd8c973 177 proofs/S0-05/tools/pc/run_s0_05_units.sh
5d9c502e862d0507 380 proofs/S0-05/check_egress.py
d93b1b32d075f684 1507 tests/test_s0_05_egress.py
# the gates below ran on the lane's working-tree bytes before the landing commit; the identities above are those bytes
$ python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider (root, x2)
137 passed in 61.76s (0:01:01)
137 passed in 61.72s (0:01:01)
$ setpriv --reuid=65534 --regid=65534 --clear-groups env HOME=/tmp/e2r1nr /usr/bin/python3 -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e2r1nr/bt
122 passed, 15 skipped in 4.24s
$ census after both root runs
0 netns, 0 veth, 0 owner records
# AF-AP-129, reproduced through the REAL library at 04:0xZ (scratch EGRESS_OWNER_DIR):
$ bash -c '. proofs/S0-05/netns_lib.sh; egress_ns_create s005-ap129probe 10.9.9.9:99999999999999999999; echo "create rc=$?"; ...'
proofs/S0-05/netns_lib.sh: line 77: [: 99999999999999999999: integer expression expected
iptables v1.8.10 (nf_tables): invalid port/service `99999999999999999999' specified
create rc=1
netns present: 1
destroy rc=0
# (census clean after the destroy); the guard in isolation: 65536 and 00080 refused, 99999999999999999999 and
# 9223372036854775808 ACCEPTED ([ -gt ] errors with rc 2 and the || reads it as false)
```

The builder's mutation table (E2-R1-report.md): M10 survives, pre-existing (the F6 collision prefix test; issue #29's F17);
M11 (the TERM wait loop removed) claimed EQUIVALENT. **Everything above is ALREADY MEASURED — do not spend your budget
re-deriving it; your value is the shapes nobody tried.** Re-run a listed measurement only where a finding of yours depends on it.

## ITEMS (discovery exhaustive; disposition disciplined)

Number your findings F1…; for each: evidence level (reproduced / read / inferred), file:line, expected vs observed, the
cheapest red control, and the blocking predicate (contract-mapped · reproduced through the real production path · materially
effective · a concrete discriminator · in boundary). A red test is necessary, never sufficient.

1. **F11/F12's class, beyond AF-AP-129.** Grade the reproduced overflow above against item 1 of the contract ("create nothing on
   a refusal"). Then, through `egress_ns_create` (scratch owner dir), try: `1.2.3.4:+80`, `1.2.3.4: 80`, `1.2.3.4:80 ` (trailing
   space), an entry holding a newline, `::1:80`, `0.0.0.0:80`, `255.255.255.255:80`, `127.0.0.1:80`, an empty entry `""`, and a
   second entry that is bad after a good first one. For each: rc, message, and whether ANY state exists afterwards (claim dir,
   owner record, netns, veth, `/etc/netns/<ns>`). Question, not an expectation: should `0.0.0.0` or `127.0.0.1` be refused as an
   allow target, and does anything in the contract say so? Also: the namespace NAME is never validated before
   `mkdir "$claim_dir"` (L:93-94) — what does a name holding `/` or `..` do to the claim path, and can any caller pass one?
2. **F2's stale takeover.** L:103 says "take over atomically", but the branch reads the record, then writes it. Force the
   interleaving deterministically in a scratch copy (a pause injected between the read and the write, never a timing race):
   two creators that both read the same DEAD owner — do both proceed, and does the later one's destroy-first
   (`_egress_ns_teardown`, L:109) tear down the earlier one's namespace? Paste what each sees. Then: a claim dir with no owner
   record (a crash between L:94 and the record write); a record holding a recycled live pid of an unrelated process you own. Is
   `test_create_race_one_wins` (T:1294) able to catch any of these?
3. **F1 under shapes the tests do not use.** (a) A process that respawns a child on SIGTERM: do children born after the SIGKILL
   pass's `ip netns pids` read escape? (b) The rc 1 path: who reads it? `egress_ns_create`'s destroy-first ignores
   `_egress_ns_teardown`'s rc (L:109); the runner's calls to `egress_ns_destroy` (PC:109, PC:132, PC:141) — what happens next on
   rc 1, and does `egress_ns_destroy` removing the claim after a failed teardown (L:314-318) let a new create reuse the name
   while an old process still holds the old network namespace? (c) Attack the M11 EQUIVALENT claim with a unit that needs time
   to handle TERM (writes its log on TERM, then exits within the 5 s grace): with the wait loop removed, is its log lost? State
   whether that matters to the contract or to the runner's evidence, and grade the equivalence.
4. **F3 cleanup and NS_LIVE.** (a) Two unit names where one is a substring of the other (construct them in a scratch runner):
   what does `NS_LIVE=${NS_LIVE//$ns/}` leave, and does cleanup then miss or mangle a live namespace? List the unit names the
   runner can produce today (PC's unit table) and say whether any pair collides. (b) Runner A holds a namespace; its owner
   record is removed by hand (tmpfs `/run`): what does A's cleanup do at exit?
5. **F4 edges.** Reasons with a newline, a backslash, a double quote, and a byte that is not valid UTF-8 (can a reason carry one?
   trace where reasons come from); an empty RESULT and ABSENT pair; python3 failing in that block (what is left in
   `units.json`, and does the runner still go on to the checker?). Run the REAL checker on each result.
6. **F14.** Does `test_runner_live_leg` (T:1066) bind the stand-in's record to the namespace under test (for example its
   `/proc/<pid>/ns/net` against the namespace's), or only to a file's presence? Construct the cheapest mutant that keeps the
   record but runs the stand-in outside the namespace, and report whether the test reds.
7. **New mutants (never M10/M11, never E2's m1-m9).** At least: M12 L:77's range test deleted (the regex alone); M13 L:94
   `mkdir` → `mkdir -p`; M14 PC:78's owner comparison removed (destroy every NS_LIVE name); M15 PC:170's `json.dump` block
   replaced by E2's printf loop (from `git show 9223162:proofs/S0-05/tools/pc/run_s0_05_units.sh`); M16 the SIGKILL pass (from
   L:276) removed; M17 `egress_ns_destroy` always `return 0`. One row each: mutant · compiles (`bash -n` / `py_compile`) ·
   collected count · killed-by / SURVIVED / EQUIVALENT (AF-AP-78: a syntax kill is not a kill).
8. **The report.** Any claim in `E2-R1-report.md` the PIN does not support is a finding (line numbers, the gate counts, the
   mutant table, the DISCREPANCIES and NOT-done sections).
9. **Out of scope, do not re-litigate:** issue #29 (VERIFY-E2's follow-ups F5, F6, F8, F9, F10, F13, F16-F21, including M10), the
   CD1 amendment's launch recipe A1-A8 and D-051's relay DNAT (E3's scope, not built), and the seed's second-assertion wording
   (the owner's pending decision). Note a touchpoint in one line if a finding bears on them.

## Deliverable

`tasks/briefs/s0-05-support/VERIFY-E2-R1-report.md` — sections: OUTCOME (one paragraph, the GATE RECOMMENDATION first:
`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) · IDENTITY (the digests you measured vs the
table above) · ITEMS 1-9 with findings F1… · MUTATION TABLE · GATES (every count PASTED from the run with its exact invocation;
never typed) · FOLLOW-UPS (non-blocking, one line each, for the coordinator to file under D-034) · CENSUS (the commands' output
after your last live run) · NOT-done (first-class). Lint floor: `python3 scripts/report_lint.py --min-refs 15 --map
L=proofs/S0-05/netns_lib.sh --map R=proofs/S0-05/run_canaries.sh --map PC=proofs/S0-05/tools/pc/run_s0_05_units.sh --map
C=proofs/S0-05/check_egress.py --map T=tests/test_s0_05_egress.py tasks/briefs/s0-05-support/VERIFY-E2-R1-report.md --root .`;
apply its `fix:` hints for at most three rounds, then paste and finish. Write the report incrementally from the start. Run long
gates in ONE foreground call (a backgrounded run you stop waiting for is lost); use a short `--basetemp` under your scratch dir
(the sandbox has about 2 GB free disk: delete your scratch copies when done). Never edit the tree except the report; never
`git stash` / `git checkout` / `git restore` anything; never touch `proofs/S0-05/fixtures/**` in place. Do not commit, push,
post, or open issues — the coordinator does.
