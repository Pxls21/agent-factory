# VERIFY-S0-05 — the targeted verify of S0-05's mint, its A2'' census and the curl spelling (task #207)

PIN: ff7a671 (the post-push origin head). The shared tree's HEAD is later only by ledger-plane and brief commits; every S0-05 file is
byte-identical there (premise below). The three landings under test, oldest first: a840943 (A2''), 66cd9ed (the curl spelling),
ffff4b3 (the mint).
COMPONENTS: R = `proofs/S0-05/tools/pc/run_s0_05_units.sh` (the census, `_s0_01_census`); C = `proofs/S0-05/check_egress.py`;
T = `tests/test_s0_05_egress.py`; B = `proofs/S0-05/evidence/` (the owner's live bundle, 12 files); S = `proofs/S0-05/spec.json`;
M = `proofs/S0-05/result.json` + `proofs/ledger.json`. The commit messages of the three landings are INPUTS TO ATTACK, not truths.
LANE: verify-s0-05 (sandbox, uid 0: the A2'' tests need netns, veth and iptables; agent `adversarial-verifier` on the D-054 pin, in
the SHARED tree, no worktree isolation). Honey `full`: line-bounded findings, evidence anchors, SOLID/UNSURE. Do NOT spawn subagents.

WHY THIS LANE EXISTS: all three landings are GATED-PENDING-VERIFY (rule 0f). The coordinator wrote A2'' and the spelling fix itself and
must never self-accept them; the mint is the last of the nine execution proofs, and the owner's signed `accepted/S0-05` tag comes
next. That tag must not anchor a hollow green: a census that lets a changed S0-01 tree through, a checker that accepts a denial it
should refuse, or a mint whose attested inputs miss a file the proof reads.

CONTRACT (frozen), read in this order: the S0-05 block of `seeds/seed-stage0-v1.yaml` (from `- proof_id: S0-05`); D-055 in
`docs/08_DECISION_LOG.md` (the containment property the checker states); R's declared limits 1-8 (lines 36-70, limit 8 is A2''),
R's census comment above `_s0_01_census` and the three commit messages' stated claims; C's module docstring. A2'' in one sentence:
a changed regular file goes under `appended`, never `changed`, only when the same holders (pid and start time, each holding a
descriptor open for write on the path's own inode) hold it before the first unit and after the last, it only grew, every earlier
byte is unchanged, and its mode, uid and gid are the same; every other change fails the leg by name. The spelling in one sentence:
rc 7's allow-list gains exactly curl 8.10+'s generic "Could not connect to server", and the foreign-target binding (`CURL_CONNECT`)
applies to it exactly as to "Couldn't connect to server". KNOWN, filed: the open `verify-followup` + `stage0` issues on S0-05 (list
them with the GitHub tools you have read access to, or cite issue #39 and say you could not list the rest); cite, never re-file.

## Items (report EVERY observation; no severity filter; rank downstream)

1. PREMISE. Re-measure the block below on the shared tree (the identity table, the census line map, the checker's lines, the test
   names, the spec leg, the checker on B with and without `--units`, integrity, the set id). A mismatch that changes an item is
   CONTRACT-INVALID for that item; say which.
2. A2'', THE ALLOWANCE, by NEW shapes through the REAL census (drive `_s0_01_census snap|compare` as T's A2'' tests do, or
   through R end to end in its own session; never a re-implementation). Never the builder's shapes (a840943 names them). For each:
   the census output (`changed`, `appended`, the stderr line) and whether that is right under the contract:
   a. the holder truncates the file to zero and rewrites the same bytes plus more (the content equals an append): let through?
      Is that a hole, a declared limit, or harmless? Say which and why.
   b. an `O_RDWR` holder that rewrites one byte inside the old prefix and then appends;
   c. pid reuse: the holder exits and a new process gets the SAME pid with a different start time (drive `ns_last_pid` in a
      private pid namespace, or loop forks) and holds the file;
   d. the holder forks, the child keeps the descriptor, the parent exits; and the reverse (a child that held it exits);
   e. rename-replace: the holder keeps the OLD inode while a new file takes the path (the census must bind to the path's inode);
   f. a hard link: the holder writes the same inode through a path OUTSIDE the tree (readlink shows the outside path);
   g. a sparse extension (lseek past the end, then write) and an `fallocate` extension that adds zeros without a write;
   h. `fchmod`/`fchown` by the holder with no content change, and with an append;
   i. a bind mount of the markers tree in another mount namespace (the same device and inode seen through another path);
   j. a holder whose `/proc/<pid>/fd` link reads `… (deleted)`; a zombie holder; a holder that is a thread of a
      multi-threaded process (`/proc/<pid>/task/<tid>`);
   k. two holders where only one appends, and the case where the second holder closes its descriptor between the snaps;
   l. a busy host: time `holders()` over 2,000 processes with 50 descriptors each (or as close as the sandbox allows) and say
      whether its cost is bounded anywhere.
3. A2'', THE RECORD. On B's `s0-01-census.json`: is `relay.log` under `appended` with the holder the owner's run printed
   (`pid 53277 (buzz-relay)`), are `changed` and `appended` disjoint, is every other entry unchanged, and does anything
   downstream (C, the runner's final verdict, the ledger) read `appended` as more than information? A census JSON that the checker
   never reads is a fact to state, not a finding by itself.
4. THE SPELLING. (a) How C matches a detail (exact string, prefix, substring, regex): try near-misses of the new spelling (a
   suffix, a different case, "Could not connect to server" followed by a proxy phrase, a unicode apostrophe in the old spelling);
   (b) the foreign-target binding with the new spelling: IPv6 literals, hostnames against IP targets, a port mismatch, two
   `Failed to connect to` phrases in one detail; (c) read curl's `lib/strerror.c` at the tags `curl-8_5_0` and `curl-8_11_1`
   (static reading; a GitHub raw fetch is fine, never execute it) and list every other string in C's allow-list whose wording
   changed between those versions: each changed string is a live denial the checker would refuse on the PC (the class of
   AF-AP-168). If you cannot fetch the source, say so and list what you would check.
5. THE LIVE BUNDLE, RECOMPUTED. Derive every line of T's pinned `LIVE_OUTPUT` from B's files by hand (a short script of your own,
   never importing C): the NOT-run lines, the two unit identities against the pins C checks them with, the 22 failed canaries, the
   two positive controls, the DROP counters 0 -> 6. Then check B's internal consistency that C may not check: pids between
   `runtime.json`, `unit-identity.json` and `units.json`; namespace names; timestamps in order; the census window enclosing the
   unit runs; the launch logs against the rest. Every inconsistency C accepts is a finding.
6. HOSTILE COPIES, NEW SHAPES (never T's six): at least eight copies of B under `/tmp/vs05/`, each with ONE change, e.g. one
   canary line removed; one duplicated with another verdict; a third unit directory not in `--units`; `units.json` naming a unit
   `not-run` whose directory holds passing canaries; a DROP counter that goes backwards; a census with a `changed` entry; the
   census file missing; a positive control answered 2xx from a target outside the unit's allow-set; a canary line with an extra
   key. Paste C's first line and rc for each and say whether it should fail.
7. THE SPEC LEG AND THE MINT. In a static copy (`git archive ff7a671 | tar -x -C /tmp/vs05/tree`; never the shared tree, since
   the runner writes `result.json` and `ledger-gen` writes the ledger): run `python3 scripts/proof-runner run --proof S0-05
   --venue pc-bridge --root /tmp/vs05/tree`, then `validate-ledger integrity` and `ledger-gen` there, and diff the regenerated
   `result.json` against the committed one (the mint time differs; say what else does). List the committed `result.json`'s
   attested inputs and every file C and the spec leg READ (trace it; `strace -f -e trace=openat` is fine): a file read but not
   attested is a finding (it could change without invalidating the mint).
8. MUTANTS (new; never the builder's eight A2'' mutants): in scratch copies under `/tmp/vs05/mut/` only, at least ten, one per
   contract line, e.g.: holders compared by pid only; `w[:2]` made `w[:1]`; `head_sha256` over `size + 1` or `size - 1` bytes; the
   `S_ISREG` check dropped; `O_ACCMODE` made `O_WRONLY`; `bool(held) and` made `or`; the `"file"` type check dropped; the new
   spelling removed from C; the tuple match made a substring match; the `CURL_CONNECT` binding skipped for the new spelling; the
   spec leg's `--units` dropped. Each compiles (`bash -n`, the census heredoc compiles, `python -m py_compile`) and the suite
   collects (AF-AP-78); before you count a kill, run the killing test on the UNMUTATED copy and paste that it passes
   (AF-AP-138). A survivor is a finding: name the missing test.
9. GATES: T as root twice (each with its set id: `bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py`), counts equal;
   `bash -n` on R; C on B with `--units hermes-acp,buzz-acp` (rc and last line); `python -m pyflakes proofs/S0-05/check_egress.py
   tests/test_s0_05_egress.py`; `python3 scripts/no_laya_in_gates.py`; the final host census (no netns, no veth, the nat
   PREROUTING chain empty, `/etc/netns` empty, `/run/s0-05-egress` empty, `route_localnet` 0 everywhere) pasted at the end.

## Boundary

CREATE `tasks/briefs/s0-05-support/VERIFY-S0-05-report.md` (write it incrementally from the start); nothing else in the repository.
Every copy, mutant, shim and scratch tree lives under `/tmp/vs05/` and is removed at the end; every namespace, veth, rule and
`route_localnet` change you make is undone before you finish. The sandbox had 2.0 GB free at authoring: keep scratch copies small
(copy `proofs/S0-05/`, `tests/test_s0_05_egress.py` and what they import, not the whole tree, except item 7's archive, and delete
each when done). pytest: `-p no:cacheprovider --basetemp=/tmp/vs05/bt<n>` (create the parent first), removed after each run. The
coordinator commits ledger-plane files in this tree while you work (`todo/`, `docs/`, `wiki/`, `STATUS.md`, `tasks/briefs/pc/`,
`tasks/briefs/laya/`, `transcripts/`): never touch, run a writer against, or revert them. Never run `git stash`, `git checkout -- …`,
`git restore`, `git add`, `git commit`, `git worktree` or `git push`. No outward-facing action (read-only GitHub reads are fine); no
PC or bridge use (the live run was the owner's, with sudo).

AUTHORIZATION: defensive work on the owner's own system. The canaries, the namespaces and the census are the owner's own
egress-containment proof; probing them for holes (hostile evidence copies, a census fooled by a writer, a checker fooled by a
wording) is the point of the lane.

CODE INTEL FIRST: `graft ask` before any grep for code questions (graft indexes no definitions inside R's heredocs: say "unmapped —
graft ask unavailable" and read by line range); the pack:
`scripts/lane_context.sh -q 'how does the S0-05 census attribute a grown file and how does the checker grade a denial detail' -s holders -s appended -s DENIAL_DETAILS -o /tmp/vs05/pack.md proofs/S0-05/tools/pc/run_s0_05_units.sh proofs/S0-05/check_egress.py tests/test_s0_05_egress.py`.

PREDICATE: a finding blocks only if it is contract-mapped (A2'' as stated above and in limit 8, the spelling claim, the mint's
claims, or the seed's S0-05 acceptance), reproduced through the real census, checker or proof-runner, materially effective (a
changed S0-01 tree that passes, a denial accepted that should be refused or refused that is real, a mint that would survive a
change to an input it reads), with a concrete discriminator, and in-boundary (R, C, T, B, S, M). Everything else is a follow-up.
Emit ONE GATE RECOMMENDATION: `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`. The coordinator owns
the final gate.

Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/s0-05-support/VERIFY-S0-05-report.md --root .` (no `--map`
flags; cite full repo-relative paths); apply its `fix:` hints for at most three rounds, then paste and finish. The report ends with
DISCREPANCIES and NOT-done.

## PREMISE — MEASURED at authoring (2026-09-24 00:08Z, sandbox, uid 0; generated by `scripts/premise_block.sh`, every command echoed exactly as it ran)
```
$ date -u +%Y-%m-%dT%H:%M:%SZ; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf; git rev-parse --short HEAD; id -u
2026-09-24T00:08:59Z
ff7a671
374565e
0
$ git log --format='%h %s' -4 ff7a671 -- proofs/S0-05 tests/test_s0_05_egress.py | cut -c1-120
ffff4b3 S0-05 MINTED from the first live bundle (GATED-PENDING-VERIFY); S0-02 ACCEPTED (the owner's signed tag anchored)
66cd9ed S0-05 checker: curl 8.10+ spells the generic connect failure "Could not connect to server" (GATED-PENDING-VERIFY
a840943 S0-05 A2'' landed (GATED-PENDING-VERIFY, task #206): the S0-01 census lets through a pure append by a pre-leg wr
0e513df S0-05 checker docstring states D-055's containment property (task #179)
$ git diff --stat ff7a671 HEAD -- proofs tests/test_s0_05_egress.py scripts/proof-runner scripts/validate-ledger | wc -l
0
$ for f in proofs/S0-05/tools/pc/run_s0_05_units.sh proofs/S0-05/check_egress.py proofs/S0-05/spec.json proofs/S0-05/result.json tests/test_s0_05_egress.py; do echo "$(git rev-parse ff7a671:$f | cut -c1-12) $(git show ff7a671:$f | wc -l) $f"; done
7660ee2a7a8b 737 proofs/S0-05/tools/pc/run_s0_05_units.sh
1a284790f4ee 514 proofs/S0-05/check_egress.py
5463565b18cd 43 proofs/S0-05/spec.json
e14c2e90a659 134 proofs/S0-05/result.json
515bc23a2119 3762 tests/test_s0_05_egress.py
$ git ls-tree -r --name-only ff7a671 -- proofs/S0-05/evidence
proofs/S0-05/evidence/buzz-acp.launch.log
proofs/S0-05/evidence/buzz-acp/canaries.jsonl
proofs/S0-05/evidence/buzz-acp/gate.json
proofs/S0-05/evidence/buzz-acp/runtime.json
proofs/S0-05/evidence/buzz-acp/unit-identity.json
proofs/S0-05/evidence/hermes-acp.launch.log
proofs/S0-05/evidence/hermes-acp/canaries.jsonl
proofs/S0-05/evidence/hermes-acp/gate.json
proofs/S0-05/evidence/hermes-acp/runtime.json
proofs/S0-05/evidence/hermes-acp/unit-identity.json
proofs/S0-05/evidence/s0-01-census.json
proofs/S0-05/evidence/units.json
$ grep -n 'def holders\|def head_sha256\|def census\|def appended\|s0-01-tree-appended\|^_s0_01_census\|census_changed=\|^#  [78]\. ' proofs/S0-05/tools/pc/run_s0_05_units.sh
60:#  7. The S0-01 census (A2') compares each entry's type, mode, uid, gid and size, a regular file's
63:#  8. A2'' lets one change through that the census cannot attribute: a regular file that the same
247:_s0_01_census() {  # snap | compare <census file>
274:def holders():
305:def head_sha256(path, size):
324:def census():
355:def appended(rel):
376:    sys.stderr.write(f"s0-01-tree-appended: {os.path.join(markers, rel)} (held for write by {who}; not a change)\n")
690:census_changed=$(_s0_01_census compare "$EVIDENCE_ROOT/s0-01-census.json" 3<<<"$CENSUS_BEFORE") \
$ grep -n 'Could not connect to server\|^CURL_CONNECT\|^DENIAL_DETAILS' proofs/S0-05/check_egress.py
77:DENIAL_DETAILS = {
83:    # generic text "Could not connect to server": the PC's curl 8.11.1 (curl-8.11.1-6.fc42) printed
88:        "Couldn't connect to server", "Could not connect to server"),
107:CURL_CONNECT = re.compile(r"Failed to connect to (\S+) port (\d+)")
$ grep -n '^def test_the_newer_curl\|^def test_the_committed_live\|^def test_a_hostile_copy_of_the_live\|^def test_a2pp_' tests/test_s0_05_egress.py
355:def test_the_newer_curl_spelling_is_a_denial_when_it_names_its_own_target(tmp_path):
373:def test_the_newer_curl_spelling_behind_a_proxy_is_still_rejected(tmp_path):
584:def test_the_committed_live_root_needs_its_unit_list():
744:def test_the_committed_live_bundle_passes_with_every_line_pinned():
796:def test_a_hostile_copy_of_the_live_bundle_fails_by_name(tmp_path, mutate, first_line):
3615:def test_a2pp_a_log_its_holder_appends_during_the_leg_passes(e3dir):
3684:def test_a2pp_every_other_change_to_a_grown_file_still_fails_the_leg_by_name(e3dir):
3744:def test_a2pp_a_file_that_grows_while_the_census_reads_it_gets_one_consistent_record(e3dir):
$ python3 -c "import json; print([l['cmd'] for l in json.load(open('proofs/S0-05/spec.json'))['legs'] if 'proofs/S0-05/evidence' in l['cmd']])"
[['python3', 'proofs/S0-05/check_egress.py', 'proofs/S0-05/evidence', '--units', 'hermes-acp,buzz-acp']]
$ python3 proofs/S0-05/check_egress.py proofs/S0-05/evidence --units hermes-acp,buzz-acp; echo "rc=$?"
NOT run: memory-adapter — unit does not exist
NOT run: dream-foundry — unit does not exist
NOT run: ai-memory — unit does not exist
NOT run: pandaprobe — unit does not exist
NOT run: s0-01-backend — not a docs/05 §6 source: the S0-01 scripted backend is the model-provider stand-in behind OmniRoute
NOT run: harness-router — unit does not exist (conditional, not deployed in v1)
unit-identity: buzz-acp pid 930321 runs /home/rocco/s0-01-pinned/buzz/target/release/buzz-acp (sha256 a5a17ffc0c7e) as uid 1000
unit-identity: hermes-acp pid 929556 runs /home/rocco/s0-01-pinned/.venv-hermes/bin/hermes-acp (sha256 f90a0cc333fa) as uid 1000
recorded: buzz-acp C4 example.com:443 denied rc=7 — OSError [Errno 101] Network is unreachable
gate-fired: buzz-acp OUTPUT policy DROP 0 -> 6 packets
recorded: hermes-acp C4 example.com:443 denied rc=7 — OSError [Errno 101] Network is unreachable
gate-fired: hermes-acp OUTPUT policy DROP 0 -> 6 packets
PASS: S0-05 no-direct-egress - 2 units, 22 canaries failed as required, positive controls 2/2
rc=0
$ python3 proofs/S0-05/check_egress.py proofs/S0-05/evidence 2>&1 | head -2; echo "rc=${PIPESTATUS[0]}"
unit-missing: curl
exit 1 per contract
rc=1
$ python3 scripts/validate-ledger integrity --root . | grep -E 'S0-05|execution_proof'
S0-05 PRESENT
execution_proof numerator=9 denominator=9
$ curl --version | head -1
curl 8.5.0 (x86_64-pc-linux-gnu) libcurl/8.5.0 OpenSSL/3.0.13 zlib/1.3 brotli/1.1.0 zstd/1.5.5 libidn2/2.3.7 libpsl/0.21.2 (+libidn2/2.3.7) libssh/0.10.6/openssl/zlib nghttp2/1.59.0 librtmp/2.3 OpenLDAP/2.6.10
$ ip netns list | wc -l; df -h / | tail -1
0
/dev/vda        252G   36G  2.0G  95% /
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py
1 files set=9f0502080347
$ tail -2 /tmp/a2pp/full/run3.log
275 passed in 237.14s (0:03:57)
rc=0
```
The last line pair is the coordinator's full run of T as root at the mint (23:54Z-23:58Z, `--basetemp=/tmp/a2pp/full/bt3`), the
same set id. Not measured at authoring, and so written as questions above: whether any shape in item 2 is let through, whether any
other allow-list string changed wording in curl 8.10+, whether B is internally consistent beyond what C checks, whether the
attested inputs cover every file the leg reads, and whether any new mutant survives.
