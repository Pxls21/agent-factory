# I59-B: S0-05's follow-ups: limit 8's words, two mutant gaps, and the runner's guard against writing into a clone (task #313, issue #59 batch)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/i59/I59-B-report.md` (write it
incrementally from the start). PIN: origin 7a050b6 (S0-05's files are unchanged since the verified mint ff7a671). Plan:
`tasks/issue59-batch-plan.md` (#313). Source findings: `tasks/briefs/s0-05-support/VERIFY-S0-05-report.md` (F-2, F-3, F-6;
section 2's shape table, section 8's mutants, its NOT-done) and AF-AP-169 in `docs/INCIDENT-LOG.md` (the entry of
2026-09-24 00:0xZ and the registry row). Below, R = `proofs/S0-05/tools/pc/run_s0_05_units.sh`, T = `tests/test_s0_05_egress.py`.

Why the sandbox: T's census and runner legs need root, iproute2 and iptables (`NEEDS_NETNS`, T:93-102). The sandbox has them;
the PC bridge user does not (sudo there needs the owner's password).

AUTHORIZATION AND LIMITS: first-party work on the owner's own egress-containment proof (S0-05). The runner creates network
namespaces, iptables rules and holder processes on the owner's machines to prove that a unit reaches only its allowed
services: defensive by nature. No real secret is read; no network beyond the loopback fixtures T already uses.

## WHY

The batch re-mints S0-05 once for all its attested changes, and the owner re-signs once.

- **F-6 (words).** Declared limit 8 describes an append by a holder, but the census is a two-snapshot comparison (limit 7):
  it admits any file whose end state equals a pure append by the same holders. The verifier's shapes a1 and a3 (truncate,
  rewrite the same bytes, then more), b2 (a byte rewritten and restored) and h5 (a mode changed and restored) pass as
  `appended`. Containment holds: none of them leaves S0-01's tree different from a pure append. The overclaim is in the prose.
- **F-2 (mutant M1 survives, fail-open).** `appended` compares holders by pid AND start time (R:360, `w[:2]`). With pid only
  (`w[:1]`), a new process that reuses a departed holder's pid passes as the same holder. No test reuses a pid.
- **F-3 (mutant M4 survives, fail-closed).** `holders()` counts O_WRONLY and O_RDWR descriptors (R:293). Without O_RDWR, an
  O_RDWR-only holder's pure append reads as `changed`. No test has an O_RDWR-only holder.
- **AF-AP-169.** On 2026-09-19 a sudo run of R was given an evidence root inside the owner's clone. The root-owned directory it
  left blocked `git merge --ff-only` five days later, and only sudo could clear it. The documented recipe already puts the
  root outside the clone (`tasks/briefs/s0-05-support/E3-report.md:406`); nothing enforces it.

## CONTRACT

1. **F-6.** R's declared limit 8 (the header, R:63-69) and the A2'' block's words (R:236-246) say what the census admits: a
   file the same holders held for write at both snapshots, whose end state equals a pure append, whatever happened between the
   snapshots (the truncate-and-rewrite, the restored byte and the restored mode are named as let through, and why that keeps
   containment). The census code (R:247-380) does not change. T's docstrings that quote limit 8 (T:3609, T:3621) agree.
2. **F-2.** A test in which the file's holder at the second snapshot has the pid of its holder at the first snapshot and a
   different start time; the census lists the file under `changed`, never `appended`. It kills M1 as a FAILED test.
   `compare` reads the first snapshot on fd 3 (R:690), so that snapshot is data a test may build; if you build it rather than
   make a real reuse, say how its shape matches a real reuse. A real reuse is the stronger proof where you can make one without
   the shapes item 6 keeps off the sandbox.
3. **F-3.** A test with a holder that opens the file O_RDWR only (never O_WRONLY) and only appends; the census lists it under
   `appended`. It kills M4 as a FAILED test.
4. **AF-AP-169, the runner's guard.**
   a. R refuses an evidence root that is inside any git work tree (the path, or its nearest existing ancestor, after resolving
      symbolic links), before it writes anything, with a named reason and an exit code of its own. The check holds when R runs
      as root on a clone another user owns. Measured at authoring (below): as root, git refuses such a clone with `detected
      dubious ownership` (rc 128), so a `git rev-parse` check that reads a failure as "not a work tree" fails open in exactly
      the sudo case.
   b. Run under sudo (EUID 0 with `SUDO_UID` and `SUDO_GID` set), R hands every entry under the evidence root to
      `SUDO_UID:SUDO_GID` before it exits, on every exit path its EXIT trap covers (R:476-499), so the invoking user can
      delete the whole evidence root without sudo. The handback changes nothing outside the evidence root: it follows no
      symbolic link, and it never changes a file that a path outside the root also names (a hard link; the unit user can make
      one in its scratch tree, R:599).
   c. Without sudo (a root run with no `SUDO_UID`, or a non-root run), R behaves as today.
5. **Nothing else changes:** the census's verdicts, the checker, the canaries, the committed evidence. Do NOT re-mint S0-05.
6. **The shapes the verifier could not run** (its NOT-done: 2c a pid reuse, 2i a bind mount of the markers tree in another
   mount namespace, 2j a deleted-descriptor, a zombie and a multi-threaded holder). Write ONE driver, in your scratch, that runs
   R's own census function (extracted from R at run time and checked by line count and sha256, as the verifier's driver did:
   its report, section 2) over a scratch tree: one line per shape with the census result and your verdict under the contract.
   Do NOT run the fork, thread or namespace shapes in the sandbox (the sandbox's classifier stopped the verifier's helper for
   them). The coordinator runs the driver on the PC, unprivileged (`unshare -r` where a namespace is needed): give the exact
   commands and the expected output per shape.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. Tests in T for items 1-4: for item 4, a normal case, a failure case and the security boundary (the owner's rule 14). A named
   mutant reds each as a FAILED test, never an error (AF-AP-223): M1 and M4 (the verifier's, section 8), the guard removed, a
   guard that asks `git rev-parse` and reads its failure as "outside", the handback removed, a handback that follows a
   symbolic link, and one that changes a hard-linked file.
3. `bash scripts/test_summary.sh tests/test_s0_05_egress.py` twice, pasted with its set id (the floor: 275 passed in about 232 s,
   set 9f0502080347); then once over every test file that names a changed file (`grep -l`, below: two files). After the
   gates, `ip netns list` shows no namespace of yours and `iptables-save | sha256sum` equals its value before your first run.
4. `bash -n` on R; pyflakes on every Python file you write; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` prints 0 for every file
   you write.
5. The item-6 driver: its path, the PC commands, the expected line per shape.
6. NOT-done and DISCREPANCIES; every deviation from this brief, loud.

## BOUNDARY

- MODIFY: R (items 1 and 4 only), T.
- CREATE: your report; the item-6 driver in your scratch (never committed).
- READ everything else. NEVER write `proofs/S0-05/result.json`, `proofs/S0-05/evidence/**`, `proofs/ledger.json`, or any
  other proof's files.

## STANDING RULES

- No git writes, no PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables.
- Every namespace, veth, rule and process a test creates is destroyed by name or pid from its own record (T's `finally`
  blocks do this); never `pkill -f`.
- Other lanes hold this tree: SCRUB2-R1 (`scripts/transcript_export.py`, `tests/test_transcript_export.py`, possibly
  `scripts/known_values_check.py`, `scripts/session_export.py` and their tests, its report) and I59-C
  (`proofs/S0-04/tools/pc/capture_leg.py`, `tests/test_s0_04_compression.py`, its report). Never touch their files.
- The disk is shared (about 1.8G free): scratch under 200 MB in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/i59b/`, deleted as you go; a short
  `--basetemp`; never run the whole `tests/test_vendored_manifest.py`.
- Test counts are pasted from `scripts/test_summary.sh`. Stamps are substituted from `date -u`, never typed.
- Run long commands in one foreground call, each under 10 minutes. Kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text of
  its own (under 200 characters; a note only for a 0).

## PREMISE — MEASURED at authoring (2026-09-26 08:1xZ, the sandbox tree, uid 0; HEAD's S0-05 files = origin 7a050b6's)

M1 and M4 survive the suite at ff7a671 (the verifier's section 8); R and T are byte-identical since, so they survive at HEAD.

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-60
7a050b6 VERIFY-I59-A report: three commit ids that the push 
$ git log --oneline ff7a671..HEAD -- proofs/S0-05/ tests/test_s0_05_egress.py | wc -l   (0 = S0-05 unchanged since the verified mint ff7a671)
0
$ grep -n -E 'limit [78]|EVIDENCE_ROOT=\$\{1|egress_ns_capable\)|^mkdir -p|^cleanup\(\)|^trap |O_WRONLY, os.O_RDWR|w\[:2\]|scratch=|census compare' proofs/S0-05/tools/pc/run_s0_05_units.sh | cut -c1-120
84:EVIDENCE_ROOT=${1:?usage: run_s0_05_units.sh <evidence-root> [unit...]}; shift || true
86:status=$(egress_ns_capable) || { echo "run_s0_05_units: cannot run here ($status)" >&2; exit 2; }
227:# compared (declared limit 7). `snap` prints the whole census, which the runner holds in memory only
246:# that describes one byte string. Declared limit 8 says what this cannot tell apart.
293:                if (flags & os.O_ACCMODE) not in (os.O_WRONLY, os.O_RDWR):
360:    return bool(held) and [w[:2] for w in writers["after"].get(rel, [])] == [w[:2] for w in held] \
468:mkdir -p "$EVIDENCE_ROOT"
476:cleanup() {
497:trap cleanup EXIT
498:trap 'trap "" INT TERM; exit 130' INT
499:trap 'trap "" INT TERM; exit 143' TERM
599:  scratch="$EVIDENCE_ROOT/$unit/scratch"
690:census_changed=$(_s0_01_census compare "$EVIDENCE_ROOT/s0-01-census.json" 3<<<"$CENSUS_BEFORE") \
$ grep -n -E '^def netns_capable|^NEEDS_NETNS|^def e3dir|^def _census_leg|^def test_a2pp|limit 8' tests/test_s0_05_egress.py | cut -c1-110
93:def netns_capable():
99:NEEDS_NETNS = pytest.mark.skipif(
1705:def e3dir():
3346:def _census_leg(e3dir, port, unit_code, serve=None):
3609:with open(os.path.join(M, "relay.log"), "a") as fh:     # declared limit 8: the unit's own append
3615:def test_a2pp_a_log_its_holder_appends_during_the_leg_passes(e3dir):
3621:    limit 8, pinned here so the prose cannot drift from the behaviour."""
3684:def test_a2pp_every_other_change_to_a_grown_file_still_fails_the_leg_by_name(e3dir):
3744:def test_a2pp_a_file_that_grows_while_the_census_reads_it_gets_one_consistent_record(e3dir):
$ grep -l -E 'run_s0_05_units|s0_05' tests/*.py | tr '\n' ' '
tests/test_edit_snapshot_ap_screen.py tests/test_s0_05_egress.py 
$ (as root) a repo owned by uid 65534: git -C <clone>/sub rev-parse --is-inside-work-tree; echo rc=$?
fatal: detected dubious ownership in repository at '<scratch>/clone'
rc=128
$ git config --global --get-all safe.directory | wc -l
0
$ bash scripts/test_summary.sh tests/test_s0_05_egress.py   (run by the coordinator this session, before this brief)
pytest-exit: 0
pytest-summary: 275 passed in 231.96s (0:03:51)
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py
1 files set=9f0502080347
```
