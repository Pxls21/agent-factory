# VERIFY-S0-05 — report (task #207)

Lane: verify-s0-05 (sandbox, uid 0, shared tree, no worktree). PIN: ff7a671. Brief:
`tasks/briefs/s0-05-support/VERIFY-S0-05-brief.md`. Honey `full`. Written incrementally. COMPLETE: GATE RECOMMENDATION = MERGE-READY-WITH-FOLLOWUPS (below).

## 1. PREMISE — re-measured 2026-09-24T00:11Z (sandbox, uid 0)

```
$ date -u; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf; git rev-parse --short HEAD; id -u
2026-09-24T00:11:17Z
ff7a671
e5b9706            <- HEAD moved past the brief's 374565e: two ledger/brief commits (374565e J1-1-R3 brief, e5b9706 this brief)
0
$ git diff --stat ff7a671 HEAD -- proofs tests/test_s0_05_egress.py scripts/proof-runner scripts/validate-ledger | wc -l
0
identity (blob at ff7a671 == worktree hash-object, lines):
7660ee2a7a8b 737 proofs/S0-05/tools/pc/run_s0_05_units.sh
1a284790f4ee 514 proofs/S0-05/check_egress.py
5463565b18cd 43 proofs/S0-05/spec.json
e14c2e90a659 134 proofs/S0-05/result.json
515bc23a2119 3762 tests/test_s0_05_egress.py
all 12 files of proofs/S0-05/evidence/: blob == worktree ("same" x12); no untracked file in the directory (find: 12)
census line map: 60 (#7), 63 (#8), 247 _s0_01_census, 274 holders, 305 head_sha256, 324 census, 355 appended,
  376 s0-01-tree-appended, 690 census_changed=  -- identical to the brief
checker: 77 DENIAL_DETAILS, 83 comment, 88 the two spellings, 107 CURL_CONNECT -- identical
tests: 355, 373, 584, 744, 796, 3615, 3684, 3744 -- identical
spec leg: [['python3', 'proofs/S0-05/check_egress.py', 'proofs/S0-05/evidence', '--units', 'hermes-acp,buzz-acp']]
C on B --units hermes-acp,buzz-acp: the same 13 lines as the brief, last "PASS: S0-05 no-direct-egress - 2 units,
  22 canaries failed as required, positive controls 2/2", rc=0
C on B without --units: "unit-missing: curl" / "exit 1 per contract", rc=1
validate-ledger integrity: "S0-05 PRESENT", "execution_proof numerator=9 denominator=9", rc=0
curl 8.5.0 in the sandbox; ip netns list: 0; df /: 1.9G free (96%)
set id: "1 files set=9f0502080347"
```

Premise verdict: MATCHES on every measured line. The only drift is HEAD (e5b9706 vs 374565e), and no S0-05 file, test,
runner or validator changed across it. No item is CONTRACT-INVALID on premise grounds.


## Known, filed (cited, never re-filed)

Open `verify-followup` + `stage0` issues on S0-05, listed read-only 2026-09-24 00:2xZ: #13 (VERIFY-E1: F4 first-match-only
endpoint binding, F13 the `resolved` field is never read, F2/F12/F14), #16 (VERIFY-E1-R1), #29 (VERIFY-E2), #31
(VERIFY-E2-R1), #39 (VERIFY-E3: F17 reused evidence root, F18 PATH binaries, ...), #48 (VERIFY-E3-R1: SIGHUP; I3 snap
rc unchecked), #58 (AF-AP-168: record the curl version in runtime.json; it names this lane's item 4c).

## 4. THE SPELLING (66cd9ed) — reproduced through the real checker CLI

How C matches (static, check_egress.py lines 178-181 and 324): the vocabulary is a SUBSTRING test
(`fragment in record["detail"]`, keyed by rc); the endpoint binding is `re.search` of `CURL_CONNECT` (unanchored,
`:107`) and `CURL_RESOLVE` (end-anchored, `:108`), FIRST match only, and it compares the HOST only (`match.group(1)`),
never the port. Driver: `/tmp/vs05/h4/probe.py` (a copy of the committed
`proofs/S0-05/fixtures/evidence-mechanism-sandbox`, ONE record rewritten per run, the repo's
`proofs/S0-05/check_egress.py` run as a subprocess). Output, verbatim (label, rc, first line or PASS line):

```
baseline (unchanged copy)                    rc=0 | PASS: S0-05 no-direct-egress - 1 units, 11 canaries failed as required, positive controls 1/1
4a new spelling, own target                  rc=0 | PASS ...
4a suffix after new spelling                 rc=0 | PASS ...
4a lower case                                rc=1 | denial-detail-unrecognized: curl C1 curl: (7) Failed to connect to api.openai.com port 443 after 3 ms: could not connect to server
4a upper case                                rc=1 | denial-detail-unrecognized: curl C1 ... COULD NOT CONNECT TO SERVER
4a new spelling + proxy phrase (own host)    rc=0 | PASS ...      (detail: "Failed to connect to api.openai.com port 443 via 127.0.0.1 ...")
4a new spelling, bare (no endpoint)          rc=0 | PASS ...      (detail: "curl: (7) Could not connect to server")
4a proxy phrase then own target              rc=0 | PASS ...
4a unicode apostrophe old spelling           rc=1 | denial-detail-unrecognized: curl C1 ... Couldn’t connect to server
4a new spelling inside another word          rc=0 | PASS ...      ("Could not connect to server-side proxy")
4a new spelling with rc 6                    rc=1 | denial-detail-unrecognized: curl C1 curl: (6) ...
4a new spelling with rc 28                   rc=1 | denial-detail-unrecognized: curl C1 curl: (28) ...
4b ipv6 literal target, new spelling         rc=1 | denial-detail-foreign-target: curl C6 denial names 2001:db8::1, not [2001:db8::1]:443
4b hostname in detail, IP target             rc=1 | denial-detail-foreign-target: curl C6 denial names api.openai.com, not 10.201.136.1:12801
4b port mismatch (C6 own host, port 12800)   rc=0 | PASS ...      (target 10.201.136.1:12801; detail names port 12800)
4b port mismatch old spelling                rc=0 | PASS ...
4b two phrases: own then foreign proxy       rc=0 | PASS ...
4b two phrases: foreign then own             rc=1 | denial-detail-foreign-target: curl C1 denial names 127.0.0.1, not api.openai.com
4c rc28 'Connection timeout after N ms'      rc=1 | denial-detail-unrecognized: curl C6 curl: (28) Connection timeout after 5001 ms
4c rc28 PC text 'Connection timed out after' rc=0 | PASS ...
4c rc6 8.11 strerror bare                    rc=0 | PASS ...      ("Could not resolve hostname")
4c rc6 8.5 strerror bare                     rc=1 | denial-detail-unrecognized: curl C1 curl: (6) Couldn't resolve host name
4c rc6 failf own host                        rc=0 | PASS ...
4c rc6 failf foreign proxy host              rc=1 | denial-detail-foreign-target: curl C1 denial names proxy.example, not api.openai.com
```

The spelling claim holds: rc 7 gained exactly "Could not connect to server"; under every near-miss the new spelling
behaves exactly as the old one (the rc-6/rc-28 rows, the case rows, the port and two-phrase rows give the same verdict
with either spelling; checked for the port row explicitly). Case variants and a U+2019 apostrophe are refused (fail
closed). What passes with the new spelling passes with the old one too, so nothing below is a regression of 66cd9ed.

4c — curl's source, static reading (raw GitHub fetch into `/tmp/vs05/curlsrc/`, never executed): `lib/strerror.c` at
`curl-8_5_0` (1116 lines, sha256 243369f72ac3…) and `curl-8_11_1` (1112 lines, 6a3558126723…). Every changed string
literal, filtered to the CURLcode texts: CURLE_COULDNT_RESOLVE_PROXY "Couldn't resolve proxy name" -> "Could not resolve
proxy name" (rc 5, outside DENIAL_RCS: refused either way); CURLE_COULDNT_RESOLVE_HOST "Couldn't resolve host name" ->
"Could not resolve hostname" (rc 6); CURLE_COULDNT_CONNECT (rc 7, the fix); FTP/resume/file/cipher texts (no rc in
{6,7,28}). "Timeout was reached" (rc 28) is unchanged. So the only OTHER allow-list-relevant change is rc 6, and it is
harmless on the PC: 8.11.1's "Could not resolve hostname" contains the allow-listed "Could not resolve" (row "rc6 8.11
strerror bare" passes); it is 8.5.0's form that no rc-6 fragment matches (refused), and curl prints the failf text
"Could not resolve host: <name>" (`lib/hostip.c:1458` at 8.5.0, `:1483` at 8.11.1, unchanged) in its place anyway. The
failf texts the checker binds on are unchanged between the tags: "Failed to connect to %s port %u after %… ms: %s"
(`lib/connect.c:738` / `:744`, the hostname is the PROXY's when a proxy is set at both tags — the discriminator's premise
holds on 8.11.1, and no "via <proxy>" variant exists at either tag), "Connection timed out after %… milliseconds",
"Resolving timed out after", "Operation timed out after" (`lib/multi.c:1600-1617` / `:1688-1702`). Two version-sensitive
facts that are NOT string changes are findings F-4 and F-5 below.

## 2. A2'', THE ALLOWANCE — new shapes through R's own census

Driver (`/tmp/vs05/a2/lib.py`): it extracts run_s0_05_units.sh lines 247-380 at run time (134 lines,
sha256 3f02ca397d32…, equal to `sed -n '247,380p' … | sha256sum`; lines 247 and 380 asserted) and calls
`_s0_01_census snap` into a variable and `_s0_01_census compare <file> 3<<<"$snap"`, exactly as R:501 and R:690 do.
Each holder is a plain process (`/tmp/vs05/a2/puppet.py`, uid 65534 unless marked "root holder") that opens the file
ONCE before the snap and writes through that descriptor, the relay's shape. Tree owned by 65534, mode 0644. Output
(`/tmp/vs05/a2/shapes.out`), one line per shape: compare's result, then the verdict under the contract.

| shape | census result | right under the contract? |
|---|---|---|
| ctl+ holder appends (control) | appended; stderr `s0-01-tree-appended: …relay.log (held for write by pid 7487 (python3); not a change)` | yes (the driver sees the allowance) |
| ctl- no holder, appended (control) | changed `[relay.log]`, writers `{}` | yes (the driver sees the refusal) |
| a1 holder truncates to 0, rewrites the same bytes + more | **appended** | let through; see F-6 |
| a3 holder truncates to 5, rewrites the same tail + more | **appended** | let through; see F-6 |
| a2 truncate to 0, byte 0 different, + more | changed | yes |
| b1 O_RDWR holder rewrites byte 0, then appends | changed | yes |
| b2 O_RDWR holder rewrites byte 0, restores it, appends | **appended** | let through; see F-6 |
| e1 rename-replace (old+more, same mode/owner); holder keeps the OLD inode | changed; writers.after `{}` | yes: the old-inode descriptor names a deleted file, so it is no holder of the path's inode |
| e2 rename-replace; the holder ALSO opens the NEW inode for write | **appended** | consistent: inode numbers are not compared (limit 7) and at each snap the same holder holds the path's own inode; INFO F-7 |
| e3 rotation relay.log -> relay.log.1, new relay.log | changed `[relay.log.1]`; writers.after `{relay.log.1: [holder]}` | yes |
| f1 the only holder writes the inode through a hard link OUTSIDE the tree | changed; writers `{}` both sides | fail closed (a false red against the contract's letter "a descriptor … on the path's own inode"); INFO F-8 |
| g1 sparse extension (lseek past the end + write) | appended | yes (it grew; every earlier byte kept) |
| g2 fallocate(mode 0) extension, no write | appended | yes (zero-filled growth) |
| g3 fallocate PUNCH_HOLE over the prefix + append | changed | yes (a prefix rewrite with no write() is caught) |
| g4 ftruncate to a larger size, no write | appended | yes |
| h1 fchmod 0600, no content change | changed | yes |
| h2 fchmod to the same mode + append | appended | yes |
| h3 fchmod 0600 + append | changed | yes |
| h4 fchown uid 65533 (root holder) + append | changed | yes |
| h5 fchmod 0600 then back to 0644 + append | **appended** | let through; see F-6 |
| h6 setuid bit only (root holder) + append | changed (mode 4644) | yes |
| k1 two holders; only A appends | appended; stderr names both pids | yes |
| k2 two holders; B closes its descriptor; A appends | changed; writers.after has A only | yes ("a holder gone") |

2a answer: let through, and harmless for what the census certifies. The census is a TWO-SNAPSHOT comparison (R:222-224,
limit 7): at the end, relay.log holds every byte it held before, in place, plus more, with the same holders, mode, uid and
gid. A truncation, a rewrite restored before the end (b2), or a mode changed and changed back (h5) is not observable to
it, and none of them leaves S0-01's tree different from a pure append. The overclaim is in words only (F-6).

2l: R:280-303 walks every numeric `/proc` entry and readlinks every descriptor, with no cap and no time limit, twice per
run (snap and compare). Measured (`/tmp/vs05/a2/timing.py`, R's snap on a one-file tree, three runs each): 110
processes / 633 descriptors: `0.040 0.033 0.033` s; plus one ordinary process holding 19,700 extra descriptors (this
sandbox's hard RLIMIT_NOFILE is 20,000, so 2,000 processes x 50 was not built; one process gives the same readlink
count): `0.158 0.103 0.092` s, about 3.5 µs per descriptor. 2,000 x 50 = 100,000 descriptors extrapolates to ~0.4 s per
call. Cost is linear and unbounded; at the PC's scale it is not a practical risk (INFO F-9).

NOT run in this lane (see NOT-done): 2c (pid reuse), 2d (fork shapes), 2i (another mount namespace), 2j (deleted,
zombie and thread holders), and a second-holder variant of 2f. No verdict is claimed for them. Static reading only
(UNVERIFIED): R:360 compares the before and after (pid, start time) lists exactly, so a holder that leaves or joins
between the snaps fails the leg whenever R:280-297 counts it (a descriptor under the tree, open for write, naming the
path's own inode).

## 3. A2'', THE RECORD (B's `s0-01-census.json`)

Read (no import of C): `changed` = `[]`; `appended` = `{relay.log}` only, disjoint from `changed`; `writers.before` ==
`writers.after` = `{backend-v2.log: [[53658, 481166, python3]], relay.log: [[53277, 477750, buzz-relay]]}`. relay.log:
before `{mode 0644, uid 1000, gid 1000, size 264326, sha256 711660…}`, after `{… size 265950, sha256 362b49…}` — same
mode/uid/gid/type, grew 264326 -> 265950. `pid 53277 (buzz-relay)` is the owner's printed holder. before and after have
the SAME 34043 entries and DIFFERENT digests: A2'' decided the one difference is a pure append. Every other entry is
unchanged (changed == []).

Does anything downstream READ `appended` as more than information? No. Traced every reader of `s0-01-census.json`
(`grep` over proofs/scripts): only R writes it (R:366-373) and prints stderr from `grown` (R:374-376); the leg's verdict
is `census_changed` = the `changed` paths on stdout (R:690-735), so a non-empty `appended` with an empty `changed`
does NOT fail the leg — which is the whole point of A2''. C never opens the file; the spec leg is
`check_egress.py proofs/S0-05/evidence --units hermes-acp,buzz-acp` and C reads only the per-unit bundles; `proof-runner`
and `ledger-gen` never read it; the mint only HASHES it (attestation `…8d70ce…`). So the census JSON is a fact for the
report and a fail-closed gate INSIDE the runner, read by nothing that grades the mint. SOLID.

## 5. THE LIVE BUNDLE, RECOMPUTED

Derived every line of T's `LIVE_OUTPUT` from B by hand (`/tmp/vs05/h5.py`, no import of C; the rule digest recomputed
independently with hashlib): `derived == pinned LIVE_OUTPUT: True`. The 6 NOT-run lines are `units.json`'s not-run
entries in file order; the two identity lines are buzz then hermes (sorted units), sha256 truncated to 12
(a5a17ffc0c7e, f90a0cc333fa); the two C4 `recorded` lines (`example.com:443 denied rc=7 — OSError [Errno 101] Network is
unreachable`); the DROP `0 -> 6` per unit; PASS `2 units, 22 canaries failed, positive controls 2/2`. The 22 is
independently counted: each unit has C1x3, C2x3, C3x3, C5x1, C6x1 = 11; 11x2 = 22. Positive controls: buzz C0 targets
`[relay, OmniRoute]` == its allow-list each once; hermes C0 `[OmniRoute]` == its allow-list (`/tmp/vs05/h5.py`).

Internal consistency C does NOT check, all confirmed (`/tmp/vs05/h5b.py`): every allowed ip:port has its INPUT --sport
and OUTPUT --dport ACCEPT rule; each unit's C5/C6 target octet is its own /24 (107 hermes, 219 buzz); both venues `pc`,
gate `enabled`, mechanism `veth-iptables`; hermes exe_realpath `/usr/bin/python3.13` == pins interpreter, entrypoint ==
`PINNED_AGENT_REALPATH`; buzz entrypoint == `PINNED_BUZZ_ACP_EXE_REALPATH`, argv relay `ws://10.201.219.1:3999` (the
runner's DNAT substitution of pins' `ws://127.0.0.1:3999`, D-051); census base `/home/rocco/s0-01-pinned` ==
`dirname(PINNED_HERMES_HOME)`. Timestamps in order (UTC): evidence stamp `20260923T234303Z` (23:43:03Z), hermes launch
23:43:04Z, buzz launch 23:43:41Z, buzz shutdown 23:44:28Z; the census window (before the first unit, after the last)
encloses both. buzz pid 930321 > hermes pid 929556 (launched later). No inconsistency found that C accepts. Two INFO
notes: the buzz pair's allow-set is `{relay, OmniRoute}` (docs/05 §6 lists relay + hermes-acp for buzz-acp; D-051/D-055
add OmniRoute because the pair launches hermes-acp as its child — a decided contract point, F-11); R:230's comment says
"33,864 entries" while the live tree has 34,043 (illustrative comment, F-12).

## 6. HOSTILE COPIES, NEW SHAPES (never T's six)

14 copies of B under `/tmp/vs05/h6/`, each ONE change, the real checker (`--units hermes-acp,buzz-acp`) on each
(`/tmp/vs05/h6/hostile.py`). Column [OK] = the verdict matches what the contract requires.

| copy | change | checker first line | rc | right? |
|---|---|---|---|---|
| 01 | all of hermes C3 removed | `canary-missing: hermes-acp C3` | 1 | yes (must fail) |
| 02 | a C2 duplicated with rc 0 | `egress-permitted: buzz-acp C2 api.openai.com:443` | 1 | yes |
| 03 | a third unit dir `rogue-acp` not in `--units` | `unit-identity-invalid: rogue-acp no pinned identity` | 1 | yes (a present dir defaults to a run unit) |
| 04 | hermes declared not-run, dir present | `unit-declared-absent-but-present: hermes-acp` | 1 | yes |
| 05 | a DROP counter backwards | `runtime-manifest-invalid: buzz-acp drop counters must be non-negative integers` | 1 | yes |
| 06 | census with a `changed` entry | PASS | 0 | yes (C never reads the census) |
| 07 | census file missing | PASS | 0 | yes (C never reads the census) |
| 08 | a C0 answered 2xx from a target OUTSIDE the allow-set | `positive-control-failed: hermes-acp` | 1 | yes |
| 09 | a canary line with an extra key | PASS | 0 | yes (extra keys allowed; RECORD_KEYS is a floor) |
| 10 | rules widened, digest left | `egress-rules-unpinned: hermes-acp recorded rules do not hash` | 1 | yes |
| 11 | allow-list widened self-consistent, NO matching C0 | `positive-control-failed: hermes-acp` | 1 | yes (C0 must be every allowed entry once) |
| 12 | identity uid 0 on a live claim | `unit-identity-invalid: hermes-acp uid 0` | 1 | yes |
| 13 | C6 rc 7 NEW spelling naming its own target | PASS | 0 | yes (a real gate denial; not T's six) |
| 14 | venue flipped to sandbox | PASS | 0 | yes (identity graded only for `pc`; still a real bundle) |

All 14 match the contract. One follow-up gap confirmed, already filed as **issue #13 F12** (NOT one of the three
landings under test): a FULLY self-consistent widening — gate.json `allowed` gains `10.201.107.1:9999`, the two matching
ACCEPT rules, a recomputed digest AND a matching C0 that "reaches" it — PASSES (`/tmp/vs05/h6/f12.py`: rc 0, PASS). The
allow-list is pinned to itself, never compared to docs/05 §6; there is no `--allowed`. This does not touch the committed
mint (its allow-lists are the real ones) and is out of this lane's boundary; cited, not re-filed.

## 7. THE SPEC LEG AND THE MINT

Static copy `git archive ff7a671 | tar -x -C /tmp/vs05/tree` (the shared tree is never touched). In it:
`proof-runner run --proof S0-05 --venue pc-bridge --root /tmp/vs05/tree` (rc 0); `validate-ledger integrity`
(S0-05 PRESENT, execution_proof 9/9, rc 0); `ledger-gen` then diff vs the committed `proofs/ledger.json` at ff7a671:
**0 diff lines**. Diff of the regenerated `result.json` vs the committed one (`/tmp/vs05/committed-result.json`):
ONLY `recorded_at`, the four runs' `started_at`/`finished_at`, and `digest` differ. `attestation` is byte-identical
(`attestation equal: True`); every `exit_code`, `stdout_sha256`, `stderr_sha256` and `failure_reason` is identical. The
digest is `canonical_digest(runs)` (proof-runner:220), and the runs carry the per-run timestamps, so a re-mint's digest
necessarily differs; with timestamps stripped, `committed runs == regenerated runs` is True. So the only thing that
changes on a re-mint is the wall clock — the mint is deterministic in substance.

Attested inputs vs files READ. `strace -f -e trace=openat` on the spec leg (`check_egress.py proofs/S0-05/evidence
--units hermes-acp,buzz-acp`, `/tmp/vs05/strace.log`): every REGULAR file it opens under proofs/ is attested — the 8
per-unit bundle files + `units.json` + `check_egress.py`. The two unattested opens are DIRECTORIES (`proofs/S0-05`,
`proofs/S0-05/evidence`, opendir for `iterdir`, not hashable; a NEW file added there is picked up by the attestation's
`rglob`, so hostile copy 03 is caught). **One file is READ but NOT attested by S0-05: `proofs/S0-01/pins.py`** — the
checker imports it for every pc-venue unit (`check_unit_identity` -> `pinned_identity` -> `_load_pins`, confirmed: the
leg opens `proofs/S0-01/__pycache__/pins.cpython-311.pyc`, and a traced `check()` calls `_load_pins` twice). Its
`PINNED_AGENT_*`/`PINNED_BUZZ_ACP_*` values determine the pc-venue verdict, yet `proofs/S0-01/pins.py` is absent from
S0-05's `attestation` (and from S0-03's — S0-03 imports the same reader; only S0-01 attests it). So the S0-05 mint
alone would survive a pins.py change that makes the committed `unit-identity.json` no longer match. This is F-1
(FOLLOW-UP), NOT a blocker: two backstops stop a false green reaching CI — (i) `proofs/S0-01/pins.py` IS attested by
S0-01's mint, so any pins change fails S0-01's integrity; (ii) CI runs `pytest tests/`, and both
`test_every_spec_leg_behaves_exactly_as_declared` and `test_the_committed_live_bundle_passes_with_every_line_pinned`
RE-EXECUTE the checker against the committed bundle with the live pins.py, so a drift goes red there. The gap is a
completeness gap in the shared attestation closure (`scripts/validate-ledger` `ATTESTATION_CLOSURE` + `proofs/<id>` rglob),
cross-proof, and outside R/C/T/B/S/M as a code change.

## 8. MUTANTS (new; never the builder's eight)

Scratch copy `/tmp/vs05/mut/` (proofs + tests + scripts). Killer pool proven green on the UNMUTATED copy first
(prior step: the 9 A2''/spelling/spec tests, `9 passed in 8.73s`, host netns 0 after). Each mutant: one edit, then
`bash -n` + an `ast.parse` of the census heredoc (R) or `py_compile` (C) or `json.load` (S), then `pytest --co`
collects, then its killer subset (AF-AP-78 + AF-AP-138 guards). Driver `/tmp/vs05/mut/driver.py`. Real tree verified
untouched after (three S0-05 blobs identical, `git status` clean). Result: **7 KILLED, 4 SURVIVED**.

| mutant | line | killed? | killer / classification |
|---|---|---|---|
| M2 head_sha256 over size-1 | R:363 | KILLED | test_a2pp_a_log_… + a_file_that_grows (2 failed) |
| M3 head_sha256 over size+1 | R:363 | KILLED | same (2 failed) |
| M5 `bool(held) and` -> `or` | R:360 | KILLED | test_e3r1_r2_each_in_place_write + a2pp_every_other (2 failed) |
| M8 holders equality -> subset | R:360 | KILLED | test_a2pp_every_other (1 failed) |
| M9 new spelling removed | C:88 | KILLED | test_the_newer_curl_spelling_is_a_denial (1 failed) |
| M10 foreign-target check neutered | C:163 | KILLED | test_proxy_shaped_denial + newer_curl_behind_proxy (2 failed) |
| M11 spec leg `--units` dropped | S | KILLED | test_every_spec_leg_behaves_exactly_as_declared (1 failed) |
| M1 holders compared by pid only (`w[:2]`->`w[:1]`) | R:360 | **SURVIVED** | F-2: missing pid-reuse discriminator (item 2c) |
| M4 `O_RDWR` dropped from holders | R:293 | **SURVIVED** | F-3: missing O_RDWR-only-holder test (fail-closed) |
| M6 `"file"` type check dropped in appended | R:361 | SURVIVED | EQUIVALENT (defence-in-depth) |
| M7 `S_ISREG` dropped in holders | R:296 | SURVIVED | EQUIVALENT (defence-in-depth) |

Survivor analysis:
- **M1 (pid-only) — F-2, FOLLOW-UP.** The shipped `appended` compares `w[:2]` = `[pid, start time]`, matching the
  contract ("the same processes (pid and start time)"). The mutant drops start time, so a pid-reuse case (the original
  holder exits and a NEW process reuses the pid and holds the file) would pass as `appended` when the contract requires
  `changed`. No committed test exercises pid reuse (this lane's unrun item 2c). Direction: fail-OPEN, so a regression to
  pid-only could mint a false green. The SHIPPED code is correct; the gap is a missing regression test. Fix: a test that
  reuses a pid across the census window and expects `changed`.
- **M4 (O_RDWR dropped) — F-3, FOLLOW-UP.** `holders()` counts O_WRONLY and O_RDWR (contract: "O_WRONLY or O_RDWR in its
  fdinfo"). Dropping O_RDWR means an O_RDWR-only holder is not seen, so its pure append is mislabeled `changed` — fail
  CLOSED (a false red, never a false green; the real relay holds O_WRONLY, unaffected). No committed test uses an
  O_RDWR-only holder (my item-2 b1/b2 probes did, but they are not committed tests). Fix: a committed O_RDWR-holder-appends test.
- **M6 and M7 — EQUIVALENT, no missing test.** `holders()` records a holder only when `stat.S_ISREG(named)` (R:296,
  intact under M6) and `head_sha256` returns a digest only for a regular file (R:312, intact under M6); `appended`'s
  `type=="file"` guard (intact under M7) blocks a non-regular entry. So for M7 the S_ISREG in holders is redundant given
  appended's type guard, and for M6 the type guard is redundant given holders()+head_sha256 — neither can make a
  non-regular or type-changed entry pass as `appended`. The builder's own comment (R:357-358) states the type test "only
  guards the record's keys". Provable equivalents, consistent with prior lanes' equivalent-survivor calls (#31 F9).

None of the four survivors is a blocker: the shipped bytes are correct in all four (two are equivalents, two are
missing-test coverage gaps where the production code meets the contract). F-2 and F-3 are FOLLOW-UPs.

## 9. GATES (all pasted verbatim)

```
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py
1 files set=9f0502080347
$ python3 -m pytest -p no:cacheprovider --basetemp=/tmp/vs05/bt9a tests/test_s0_05_egress.py -q   (run 1, as root uid 0)
275 passed in 242.95s (0:04:02)     host netns after: 0
$ python3 -m pytest -p no:cacheprovider --basetemp=/tmp/vs05/bt9b tests/test_s0_05_egress.py -q   (run 2, as root uid 0)
275 passed in 236.07s (0:03:56)     host netns after: 0     -> counts EQUAL, set id 9f0502080347
$ bash -n proofs/S0-05/tools/pc/run_s0_05_units.sh                       -> rc 0
$ python3 proofs/S0-05/check_egress.py proofs/S0-05/evidence --units hermes-acp,buzz-acp
PASS: S0-05 no-direct-egress - 2 units, 22 canaries failed as required, positive controls 2/2   rc 0
$ python3 -m pyflakes proofs/S0-05/check_egress.py tests/test_s0_05_egress.py   -> rc 0 (clean)
$ python3 scripts/no_laya_in_gates.py   -> no_laya_in_gates: 40 files scanned, clean  rc 0
```

FINAL HOST CENSUS (pasted):
```
netns: 0 -> []
veth pairs: 0
nat PREROUTING: -P PREROUTING ACCEPT      (chain empty of rules)
/etc/netns: []   (empty)
/run/s0-05-egress: []   (empty)
route_localnet: all zero (nothing nonzero across /proc/sys/net/ipv4/conf/*/route_localnet)
leftover puppet.py helper procs: 0
```

## FINDING INVENTORY (no severity filter)

- **F-1 (FOLLOW-UP, SOLID).** `proofs/S0-01/pins.py` is READ by the S0-05 leg (live identity check, confirmed via
  strace/pyc + a traced `_load_pins`x2) but is NOT in S0-05's `attestation` (nor S0-03's; only S0-01 attests it).
  Contract map: the mint's implicit "these inputs determine the verdict". Canonical path: reproduced in the ff7a671
  archive. Material effect: the S0-05 mint alone survives a pins.py change; but two backstops stop a false green at CI
  (S0-01's own attestation fails on any pins change; pytest re-executes the checker against the committed bundle with
  live pins). Discriminator: add pins.py to S0-05's attestation and it fails integrity on a pins change. Fix: extend the
  attestation closure to the imported pins, or document the cross-proof backstop. Out of R/C/T/B/S/M as a code change
  (`scripts/validate-ledger`), cross-proof.
- **F-2 (FOLLOW-UP, SOLID).** Mutant M1 survives: the census `appended` holder comparison (R:360, `w[:2]`) has no
  pid-reuse regression test, so a regression to pid-only would go uncaught. Fail-open direction. Shipped code is
  correct. Fix: a committed pid-reuse discriminator (this lane's unrun item 2c). Related to issue #39/#31 mutation rows.
- **F-3 (FOLLOW-UP, SOLID).** Mutant M4 survives: no committed test uses an O_RDWR-only holder, so the O_RDWR branch of
  `holders()` (R:293) is uncovered. Fail-closed direction (only false reds). Fix: a committed O_RDWR-holder-appends test.
- **F-4 (INFO, SOLID).** Static curl reading (item 4c): the only rc-in-{6,7,28} allow-list wording change between
  curl-8_5_0 and curl-8_11_1 besides rc 7's fix is rc 6 (`Couldn't resolve host name` -> `Could not resolve hostname`),
  and it is harmless on the PC — 8.11.1's form contains the allow-listed "Could not resolve", and curl prints the failf
  "Could not resolve host: <name>" (unchanged) for a real resolve failure. Recorded so the curl-version follow-up
  (issue #58) has the exhaustive list.
- **F-5 (INFO, SOLID).** The foreign-target discriminator's premise (`Failed to connect to %s`'s `%s` is the PROXY host
  when a proxy is set) holds on curl 8.11.1: `lib/connect.c` selects `http_proxy.host.name` at both tags, and no
  "via <proxy>" wording exists at either tag. So the proxy-shaped-denial rejection survives the PC's curl.
- **F-6 (FOLLOW-UP, SOLID).** Item 2a/2b/2h: R's census (a two-snapshot comparison, limit 7) lets through a
  truncate-and-rewrite-same-bytes-plus-more (a1/a3), a rewrite reverted before the end (b2), and a mode changed and
  restored (h5) — the words "declared limit 8" describe an append by a HOLDER, but the mechanism actually admits any
  end-state that equals a pure append regardless of the path taken between the snaps. Harmless: none of these leaves
  S0-01's tree different from a pure append, so the containment property is intact; the overclaim is in the prose. Fix:
  widen limit 8's wording, or (defence-in-depth) record the file's own O_APPEND flag. In-boundary (R comment).
- **F-7 (INFO, SOLID).** Item 2e2: a holder that keeps the OLD inode AND opens the NEW inode after a rename-replace is
  listed `appended` (inode numbers are not compared, limit 7). Consistent with the contract; noted.
- **F-8 (INFO, SOLID).** Item 2f: a file whose ONLY writer holds it through a hard link OUTSIDE the tree is recorded
  with no holder, so its append fails the leg (fail-closed false red). Consistent with the contract's wording ("a
  descriptor open for write on the path's own inode"); the census binds the holder to a path UNDER `.markers`.
- **F-9 (INFO, SOLID).** Item 2l: `holders()` walks all of `/proc` twice per leg with no cost bound (~3.5 µs per
  descriptor measured; ~0.4 s at 100k descriptors). Linear, unbounded, not a practical risk at the PC's scale.
- **F-10 (INFO/UNVERIFIED).** Issue #13 F12 reproduced live (`/tmp/vs05/h6/f12.py`): a fully self-consistent widened
  allow-list (gate + rules + digest + matching C0) PASSES; the allow-list is pinned to itself, never to docs/05 §6.
  Already filed (#13 F12); out of this lane's three landings (the mint's allow-lists are the real ones). Cited, not re-filed.
- **F-11 (INFO, SOLID).** The buzz pair's allow-set is `{relay, OmniRoute}` while docs/05 §6 lists "relay and hermes-acp"
  for buzz-acp; D-051/D-055 decided this (the pair launches hermes-acp as its child, which needs OmniRoute). A decided
  contract point, not a hole.
- **F-12 (INFO, SOLID).** R:230's comment says the PC tree has "33,864 entries"; the committed live census has 34,043.
  Illustrative comment drift, no behavior.

## Items reproduced vs reviewed vs skipped

Reproduced through the REAL production path: item 1 (premise), item 2 shapes a/b/d(partial via holder set)/e/f/g/h/k
through R's own census function (byte-identical extract), item 3 (B's census read), item 4 (spelling near-misses through
the checker CLI + curl source static reading), item 5 (LIVE_OUTPUT re-derived by hand + consistency), item 6 (14 hostile
copies through the checker), item 7 (proof-runner/ledger-gen/integrity in a ff7a671 archive + strace), item 8 (11
mutants with compile+collect+baseline guards), item 9 (two full T runs + gates + host census). Reviewed statically only:
curl's `lib/*.c` (fetched, never executed), and R:360's exact (pid,start) comparison for the unrun pid-reuse case.
Deliberately SKIPPED (see NOT-done): item 2c (pid reuse), 2i (bind mount in another mount namespace), 2j (deleted /
zombie / thread holders), and the safety-stopped fork/thread/namespace holder shapes.

## GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS

No finding meets the whole blocking predicate. The three landings under test hold: A2'' attributes a pure append
correctly and fails every other change by name (item 2, 7-of-11 mutants killed, the 4 survivors are 2 equivalents + 2
non-blocking coverage gaps); the curl spelling gained exactly "Could not connect to server" with the target binding
intact on 8.11.1 (item 4, F-4/F-5); the mint is deterministic in substance and every proof-local file it reads is
attested (item 7). Follow-ups: F-1 (pins.py unattested by S0-05, backstopped), F-2/F-3 (two mutant-coverage gaps), F-6
(limit-8 wording). This recommendation does not depend on anything unreproduced; the coordinator owns the final gate.

## DISCREPANCIES (report vs brief premise)

- HEAD advanced during the lane from 374565e (brief) through e5b9706 to 700e7d3 (ledger/brief commits only); NO S0-05
  file, test, runner or validator changed across it (`git diff --stat ff7a671 HEAD -- proofs tests/… = 0 lines`). Every
  premise measurement matched. The pack header reads 700e7d3+dirty (the report file is the only working-tree change).
- Sandbox free disk fell from 2.0 GB (brief) to ~1.5 GB during the mutant/archive work; all scratch removed at the end.

## NOT-done (with reason)

- Item 2c (pid reuse), 2i (bind mount of the markers tree in another mount namespace), 2j (deleted-fd / zombie /
  multi-threaded holder): a first attempt to drive fork/thread/namespace holder shapes through a remote-controlled
  helper was halted by the environment's safety classifier mid-run; I did not reproduce that line of work. The narrowed
  holder helper (plain file syscalls) covered a/b/d-partial/e/f/g/h/k. These three shapes are UNVERIFIED; F-2 (the M1
  survivor) is the pid-reuse gap surfaced by the mutant path instead.
- No PC or bridge use (no banner this session; the live bundle was the owner's run). R's live legs were not executed on
  the PC; R's census function was exercised in the sandbox as R calls it.
- `git` mutating commands, subagents and outward-facing actions: none used (read-only GitHub issue reads only).

## Line-checked citations (one ref per line)

- `proofs/S0-05/check_egress.py:77` defines `DENIAL_DETAILS`, the rc-keyed denial vocabulary.
- `proofs/S0-05/check_egress.py:88` adds `Could not connect to server` beside the old spelling (rc 7).
- `proofs/S0-05/check_egress.py:107` compiles `CURL_CONNECT` on `Failed to connect to`.
- `proofs/S0-05/check_egress.py:163` is `def _foreign_endpoint_in_detail`, the discriminator.
- `proofs/S0-05/check_egress.py:324` tests `fragment in record["detail"]` per rc (SUBSTRING).
- `proofs/S0-05/check_egress.py:363` binds `expected_rules` to the gate `rules_sha256`.
- `proofs/S0-05/tools/pc/run_s0_05_units.sh:274` is `def holders`, the write-holder scan.
- `proofs/S0-05/tools/pc/run_s0_05_units.sh:293` gates on `os.O_ACCMODE` in `O_WRONLY`/O_RDWR.
- `proofs/S0-05/tools/pc/run_s0_05_units.sh:296` requires `S_ISREG` and the same dev/ino.
- `proofs/S0-05/tools/pc/run_s0_05_units.sh:305` is `def head_sha256`, the prefix digest.
- `proofs/S0-05/tools/pc/run_s0_05_units.sh:355` is `def appended`, the A2'' allowance.
- `proofs/S0-05/tools/pc/run_s0_05_units.sh:360` compares `writers["after"]` holders `w[:2]`.
- `proofs/S0-05/tools/pc/run_s0_05_units.sh:363` checks `head_sha256` against `was["sha256"]`.
- `proofs/S0-05/tools/pc/run_s0_05_units.sh:376` writes `s0-01-tree-appended` on stderr.
- `proofs/S0-05/tools/pc/run_s0_05_units.sh:690` runs `census_changed` at the leg's end.
- `tests/test_s0_05_egress.py:355` is `def test_the_newer_curl_spelling_is_a_denial_when_it_names_its_own_target`.
- `tests/test_s0_05_egress.py:744` is `def test_the_committed_live_bundle_passes_with_every_line_pinned`.
- `tests/test_s0_05_egress.py:3615` is `def test_a2pp_a_log_its_holder_appends_during_the_leg_passes`.
- `tests/test_s0_05_egress.py:3684` is `def test_a2pp_every_other_change_to_a_grown_file_still_fails_the_leg_by_name`.
- `proofs/S0-05/check_egress.py:483` builds the `PASS: S0-05 no-direct-egress` line over `len(units)`.
