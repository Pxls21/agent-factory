# VERIFY-E2 — the adversarial verify of S0-05's live-leg prerequisites (E2 + the two coordinator touches)

**Role:** `adversarial-verifier` (Opus 5), IN THE SANDBOX as root (netns / iptables / veth are available here; the PC lane
user cannot create namespaces). Honey `full`: line-bounded findings, evidence anchors, SOLID/UNSURE on every claim. Your report
is DATA for the coordinator's gate; you return a GATE RECOMMENDATION, never a verdict. Do NOT spawn subagents.

**PIN:** `9223162` (the E2 landing on origin). The working tree is origin head `dc266b1`; the S0-05 boundary is BYTE-IDENTICAL
between the two (measured below). Work on the tree READ-ONLY: every mutant, fixture and hostile input lives in a scratch copy
under `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/ve2/` (a `git archive 9223162` of the
boundary). The ONLY file you write in the tree is your report.

**Authorization:** defensive work on the owner's own system — the proof's own library builds throwaway network namespaces on
loopback; nothing egresses beyond this container; no owner server runs in the sandbox. The census after EVERY live run:
`ip netns list`, `ip -o link show type veth`, `ls /run/s0-05-egress` — all empty of anything you created. Kill only processes
you started, by pid from your own record; never `pkill -f`.

## What landed (file:line at the PIN; L = `proofs/S0-05/netns_lib.sh`, R = `proofs/S0-05/run_canaries.sh`, PC = `proofs/S0-05/tools/pc/run_s0_05_units.sh`, C = `proofs/S0-05/check_egress.py`, T = `tests/test_s0_05_egress.py`)

Contract (frozen): `tasks/briefs/s0-05-support/E2-brief.md` items and mutants m1-m9 (its STATUS stamp names the coordinator's
correction to item 2), which close VERIFY-E1 F3, F6-F11, F17-F19, F23 (`tasks/briefs/s0-05-support/VERIFY-E1-report.md`). The
builder's report `tasks/briefs/s0-05-support/E2-report.md` is an INPUT to attack, never evidence.

- **F23** a live sibling refused — L:77-84: the owner record `$(egress_ns_owner_file "$ns")` read; alive (`kill -0`) and not
  `$$` → `namespace-live: <ns> owned by pid <p>`, rc 65. The record written at L:114, removed by destroy at L:257; its path is
  L:230-231 `EGRESS_OWNER_DIR=${EGRESS_OWNER_DIR:-/run/s0-05-egress}` + `egress_ns_owner_file` (COORDINATOR TOUCH 2 — the
  brief had put it in `/etc/netns/<ns>/`, which `ip netns exec` bind-mounts over /etc).
- **F6** an address-plan collision refused — L:87-97: after the destroy-first step, any host interface already holding
  `10.201.<octet>.` → `address-plan-collision: <ns> 10.201.<octet>.0/24 on <if>`, rc 65.
- **F7** destroy kills every process in the namespace — L:236-257: SIGTERM to each `ip netns pids`, a bounded wait of 50 × 0.1 s,
  then the veth and the namespace are deleted (no SIGKILL escalation).
- **F9** the runner stops a unit through the namespace — PC:134 `egress_ns_destroy "$ns"` (the `kill "$launch_pid"` removed).
- **F10** the S0-01 backend out of the contained set — PC:63 `ABSENT[s0-01-backend]` with the named reason; PC:66 default units.
- **F8** the interpreter inside each LAUNCH row — PC:52, PC:54; run as given at PC:111.
- **F3 + F17** no `canaries.jsonl` on the exit-3 path — R:77-80 (the output directory and the file are created only after the
  DROP_BEFORE guard at R:72-75).
- **F11** the venue required — R:30-35, `run_canaries: venue must be sandbox or pc, got '<v>'`, rc 64.
- **F18** an empty unit name refused — C:360-364, `usage: --units carries an empty unit name`, rc 64.
- **F19** the allow host a literal — L:133-137 (a character class `*[!0-9.]*|*/*|""` → rc 64).
- **COORDINATOR TOUCH 1** — PC:86: the `local create_err` line in the runner's top-level loop removed (bash printed
  `local: can only be used in a function` for every unit).
- Tests: T:909 `test_address_plan_collision_is_refused`, T:978 `test_live_sibling_namespace_is_refused`, T:1021
  `test_destroy_kills_all_namespace_processes`, T:1066 `test_runner_live_leg` (with the two stderr assertions of the touches),
  T:1154 `test_shebang_matches_launch_interpreter`, T:1185 `test_unreadable_counter_creates_no_canaries_file`, T:1203
  `test_venue_required_and_validated`, T:1221 `test_empty_unit_name_rejected`, T:1231 `test_allow_entry_must_be_ipv4_literal`.

## PREMISE — MEASURED (coordinator, 2026-09-23 01:3x-01:5xZ, sandbox as root)

```
$ git diff --stat 9223162 dc266b1 -- proofs/S0-05 tests/test_s0_05_egress.py
(empty = byte-identical)
$ sha256[:16] + lines at 9223162
324ffdd9aa646531 258 proofs/S0-05/netns_lib.sh
44b1428b431303a1 139 proofs/S0-05/run_canaries.sh
24087a298ab1b9f9 159 proofs/S0-05/tools/pc/run_s0_05_units.sh
5d9c502e862d0507 380 proofs/S0-05/check_egress.py
ce86f3a2d9bb81c9 1243 tests/test_s0_05_egress.py
$ the lane's bytes (before the touches): python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider (x2)
122 passed in 51.02s
122 passed in 51.14s
$ the two new stderr assertions in test_runner_live_leg, run on the lane's bytes (RED)
E   AssertionError: /home/user/agent-factory/proofs/S0-05/tools/pc/run_s0_05_units.sh: line 86: local: can only be used in a function
E   AssertionError: Bind /etc/netns/s0-05-hermes-acp/owner -> /etc/owner failed: No such file or directory
$ after both touches (x2), then the census
122 passed in 51.30s
122 passed in 51.26s
netns=0 eh_links=0 owner_dir=0
$ bash -n (the three shell files): clean · pyflakes C and T: clean · no_laya_in_gates: 37 files scanned, clean
$ python3 scripts/ap_screen.py (L R PC C): AP-32 x3 (L:39, L:187, C:174 — the pre-existing hash calls)
$ python3 scripts/report_lint.py --min-refs 12 --map L=… --map R=… --map PC=… --map C=… --map T=… tasks/briefs/s0-05-support/E2-report.md
report_lint: 33 refs — OK 32, NEAR 1, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```

The lane's own mutation table (E2-report.md): m1-m9 all killed by the named tests. **Everything above is ALREADY MEASURED — do
not spend your budget re-deriving it; your value is the shapes nobody tried.** Re-run a listed measurement only where a finding
of yours depends on it.

## ITEMS (discovery exhaustive; disposition disciplined)

Number your findings F1…; for each: evidence level (reproduced / read / inferred), file:line, expected vs observed, the
cheapest red control, and the blocking predicate (contract-mapped · reproduced through the real production path · materially
effective · a concrete discriminator · in boundary). A red test is necessary, never sufficient.

1. **F7 under a process that ignores SIGTERM.** In a namespace made by `egress_ns_create`, start `trap '' TERM; sleep 300`
   inside it (by pid record), then `egress_ns_destroy`: does the process survive in an anonymous network namespace after the
   named one is deleted (`lsns -t net`, `/proc/<pid>/ns/net`)? How long does destroy take? Map to the contract ("destroy kills
   `ip netns pids`") and grade: does the runner's C0-C6 evidence stay sound when a unit outlives its namespace, and can a
   survivor hold the next run's F6/F23 state? Then kill your process by pid and prove the census clean.
2. **F23's liveness signal.** (a) A stale owner record whose pid was RECYCLED by an unrelated live process (simulate: write the
   pid of a live `sleep` you own into the record of a namespace that has no runner) → refused forever? Is there a recovery
   path short of deleting the record by hand, and does anything document it? (b) Two runners racing on the same name
   (both start inside the same second: `egress_ns_create` from two shells at once) — can both pass the check, destroy each
   other's namespace, and both record themselves? Paste what each sees. (c) `$$` inside `$( … )` (PC:86 runs the create in a
   command substitution): confirm the recorded pid is the runner's own and that a later create by the same runner passes.
   (d) The record lives on tmpfs `/run`: after the record is deleted by hand while the namespace lives, what does a sibling do?
3. **F6's reach.** The check reads host-side IPv4 addresses only (L:92-94). (a) A `10.201.<octet>.x` address on a non-veth
   interface (a dummy link you create) → refused? (b) The same /24 held only INSIDE another namespace (no host-side address) →
   missed? Is that reachable through the library (a half-torn-down run) or adversary-only? (c) The octet function
   `_egress_octet`: list the S0-05 unit names in use (PC:47-66 + the tests' names) and report any two that share an octet.
   (d) The refusal happens AFTER `egress_ns_destroy "$ns"` (L:85): state what an F6 refusal leaves behind, against the brief's
   "nothing left behind".
4. **The exit-3 paths of R.** F3+F17 moved the file creation after the DROP_BEFORE guard (R:72-80). The SECOND exit-3 path is
   DROP_AFTER (R:114-115), after every canary ran: what is on disk then (`canaries.jsonl` without `gate.json` /
   `runtime.json`), and what does the REAL checker say about that bundle? Question, not an expectation: is that a pass, a
   named refusal, or a traceback? Map to the brief's F3+F17 text.
5. **F19's class.** Through `_egress_apply_gate` (and the test's own entry point): `1..2:80`, `....:80`, `999.1.1.1:80`,
   `1.2.3:80`, `01.2.3.4:80`, `1.2.3.4.5:80` — paste the rc and the message for each. Which reach iptables (rc 1) instead of the
   named refusal (rc 64)? Grade against the brief's "IPv4 literal only".
6. **F11 and F18 edges.** R with venue `PC`, `pc ` (trailing space), `sandbox\n`; C with `--units ' curl'`, `--units curl,`,
   `--units ,`, `--units` omitted. Paste rc and first line each; which are refused by name and which pass into later code?
7. **F8 on the real tool.** The LAUNCH rows name `/usr/bin/python3`; read the first line of the REAL
   `proofs/S0-01/tools/pc/pc_launch.py` and state what interpreter its shebang selects on each venue. Does
   `test_shebang_matches_launch_interpreter` (T:1154) compare against the real file or a stand-in? Is it paired with a
   behavioral control (AF-AP-80)?
8. **The coordinator touches.** (a) Touch 1: is any other `local` left at top level in PC or R (a function-scope scan of both
   files)? (b) Touch 2: the record directory is created by root with the default umask; a pre-existing
   `/run/s0-05-egress/<ns>.owner` that is a SYMLINK — does `printf … >` (L:114) follow it? Reproduce ONLY inside a scratch
   `EGRESS_OWNER_DIR` pointing at your scratch dir with the symlink aimed at another scratch file (never a system file), and
   grade who could plant such a link on each venue. (c) Does anything still write into `/etc/netns/<ns>/` besides
   `resolv.conf`? Run a live canary pass and grep its stderr for `Bind /etc/netns`.
9. **New mutants (never m1-m9).** At least: M10 the F6 awk `index($4, pfx) == 1` → `> 0` (a `110.201.x.` address would then
   collide — construct it); M11 destroy without the wait loop (L:244-253 removed) — does any test red?; M12 the F23 check using
   `[ -d /proc/$owner_pid ]` in place of `kill -0`; M13 C:361-364 checking only `parts[0]`; M14 R's venue case widened with
   `*)` accepting empty; M15 `egress_ns_owner_file` pointing back into `/etc/netns/<ns>/` (the touch-2 control must catch it —
   paste which test). One row each: mutant · compiles (`bash -n` / `py_compile`) · collected count · killed-by / SURVIVED /
   EQUIVALENT (AF-AP-78: a syntax kill is not a kill).
10. **The report.** `E2-report.md`'s DISCREPANCIES says "None" and NOT-done lists shellcheck: any claim in its tables the PIN does
    not support is a finding (its F-row line numbers moved by the touches; say which).
11. **Out of scope, do not re-litigate:** VERIFY-E1 F2, F4, F5, F12-F16, F20-F22, F24 (issue #13's remainder), and the seed's
    second-assertion wording (the owner's pending decision). Note a touchpoint in one line if a finding bears on them.

## Deliverable

`tasks/briefs/s0-05-support/VERIFY-E2-report.md` — sections: OUTCOME (one paragraph, the GATE RECOMMENDATION first:
`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) · IDENTITY (the digests you measured vs the table
above) · ITEMS 1-11 with findings F1… · MUTATION TABLE · GATES (every count PASTED from the run with its exact invocation; never
typed) · FOLLOW-UPS (non-blocking, one line each, for the coordinator to file under D-034) · CENSUS (the three commands' output
after your last live run) · NOT-done (first-class). Lint floor: `python3 scripts/report_lint.py --min-refs 15 --map
L=proofs/S0-05/netns_lib.sh --map R=proofs/S0-05/run_canaries.sh --map PC=proofs/S0-05/tools/pc/run_s0_05_units.sh --map
C=proofs/S0-05/check_egress.py --map T=tests/test_s0_05_egress.py tasks/briefs/s0-05-support/VERIFY-E2-report.md --root .`;
apply its `fix:` hints for at most three rounds, then paste and finish. Run long gates in ONE foreground call (a backgrounded run
you stop waiting for is lost); use a short `--basetemp` under your scratch dir. Never edit the tree except the report; never
`git stash` / `git checkout` anything; never touch `proofs/S0-05/fixtures/**` in place. Do not commit, push, post, or open
issues — the coordinator does.
