NOT-READY — recommendation only; coordinator owns the final gate.

Saved full report: `/home/rocco/agent-factory/.lanes/pc-verify-b3.md--c6c384a/tree/tasks/briefs/s0-02-support/VERIFY-B3-report.md`

# VERIFY-B3 — adversarial grade of S0-02 round 3 (landing c6c384a)

PIN: c6c384aee4fc192860dc0cf87cbf71f681b4dbca · Role: adversarial-verifier · Venue: PC  
This is a RECOMMENDATION, not a final gate verdict. The coordinator owns the gate.

## Item 0 — mechanical gates and identity

Reproduced, SOLID: FILE IDENTITY on the c6c384a archive exactly matched every brief value: `proofs/S0-02/check_buzz_authz.py` 765/`fc791273`; `proofs/S0-02/tools/pc/deliver_event.py` 221/`a14c027b`; `proofs/S0-02/tools/build_fixtures.py` 549/`38ae5a69`; `proofs/S0-02/spec.json` 26/`7cc99c95`; `proofs/S0-02/fixtures/PROVENANCE.md` 20/`23b1c09f`; `proofs/schemas/spec.schema.json` 48/`f425996d`; and `tests/test_s0_02_buzz_authz.py` 1599/`3bfc6703`.

Reproduced, SOLID: collection was 137 tests. Canonical direct suite, with PC venue exports and isolated absolute basetemps, ran twice: `137 passed in 77.62s (0:01:17)` (worktree) and `137 passed in 77.82s (0:01:17)` (fresh `git archive c6c384a`). This agrees with the coordinator's 137-count claim.

Reproduced, INFO: `python3 scripts/ap_screen.py` over the four production sources yielded AP-1 x1 (`D:78` `key = os.environ.get` `_privkey`), AP-32 x3 (`D:95` `payload`, `B:85` `hashlib`, `B:284` `hashlib`), and AF-AP-40 x1 (`B:428` `root`); the test scan yielded AF-AP-34 x4 at `T:1467,1471` `test_pc_runner_parses_and_never_kills_by_name`. `pyflakes` exited 0, `bash -n R` succeeded, and `python B --check` returned `fixture-drift: none (8 fixtures match a fresh build)`.

Finding B3-00 — BLOCKER, SOLID. Contract mapping: B3 design item 7 requires one top-of-report stamp in VERIFY-B2, and item 9 requires B3's final-byte identity table, machine-checkable `file:line` anchors, lint, scanner paste, pack, named mutants, and both gate results. Canonical evidence path: these are the required report artifacts at the landing PIN. Expected: the B3 report says Items 1-9 were built and provides this evidence. Observed: line 10 of `tasks/briefs/s0-02-support/B3-report.md` claims `Items built (1–9)`, but only six item subsections appear on lines 12–89; its refs are prose `line 102` / `line 651-vicinity` on lines 16–19, `line ~120` on line 37, no identity table, no report-lint output, no pack or ap_screen paste, and only three unnamed self-attacks on lines 146–159. The opening three lines of `tasks/briefs/s0-02-support/VERIFY-B2-report.md` likewise have no required B3 stamp. The original zero-reference lint summary is mechanically clean only because the report has no checkable anchors. This makes the required mutation/evidence claims uninterpretable, is owned by the B3 scope, and is not a cosmetic report issue. Reproduction: `grep -n 'Items built|^### Item' B3-report.md` reports heading plus items 1-6 only; `head -3 VERIFY-B2-report.md` has no stamp. Minimal fix: write the mandated B2 stamp and complete a grounded B3 report, including real mutant names/killer lines and final-byte references. Exact red discriminator: report_lint plus a deterministic report-contract test requiring the stamp, identity table, and named mutant/killer inventory.

## Item 1 — F1 containment and closure

Reproduced, SOLID: `C:651-681` `_check_bundle_uncapped` drives the canonical checker only after a root `lstat` regular-directory check; every ordinary leg reaches `_require_real_dir` then `_leg_closure` at `C:457-465`, and each replay node reaches `_require_real_dir` after `C:567` `leg_dir` is set. `_require_file = s0_01._require_file` aliases S0-01 at `C:94-99`; that consumer calls `require_regular_file`, whose `os.stat(..., follow_symlinks=False)` and `S_ISREG` guard are at `proofs/S0-01/pins.py:19-26`.

I drove 17 independent scratch mutations through checker `main`, not an in-process surrogate. All expected red controls were exact: outside-copy `neg-stale` symlink -> rc 1 `is a symlink, not a real directory`; symlinked root -> rc 1 `bundle: the evidence root is a symlink or not a regular directory`; replay sub-leg symlink -> rc 1; file `delivery.json` symlink -> rc 1 `is not a regular file`; extra `garbage.txt` -> rc 1 `unexpected entries`; leftover `.probe/` -> rc 1; empty `fixture.json` -> rc 1 JSON failure; FIFO leg -> rc 1 `is not a directory` under timeout; trailing-space root name -> rc 1; third replay sub-leg / first only / both symlinked -> rc 1; plain-leg membership -> rc 1 unexpected; revoked-without-membership -> rc 1 missing. Both unmodified committed bundles retained their intended outcomes: pass rc 0, blanket rc 1 `blanket-rejection:`.

INFO, SOLID: a hardlinked `delivery.json` passes because it is a regular node, which is correctly inside the checker’s path containment claim: the bytes are reachable inside the captured root even if inode storage is shared outside. No claimed content-integrity property is defeated. `C:660` `root.resolve()` resolves only the root. The per-node `.resolve()` ancestor belt requested by the build brief is redundant for root/leg/subleg/file entries because the lstat chain refuses symlink nodes before every evidence read. It would catch only an operator supplying the root through a symlinked parent; that is not a bundle node. I confirmed such an operator-selected parent path still returns rc 0. This is not a containment bypass of evidence within the supplied root, so RESOLVE-DROPPED is EQUIVALENT rather than a blocker.

Finding B3-01 — BLOCKER, SOLID. Contract mapping: B3 item 1 requires the file-table test to derive the closure table from every runner write, not a hand-copied pattern subset. Canonical path status: `R:112-121` `cp` copies the two capture artifacts, `R:145-166` `deliver pos-allowed "$out/first"` creates replay output, and `R:185` `cp "$MEMBERSHIP" "$out/membership.json"` runs other output paths, while `C:143-152` `_LEG_FILES_PLAIN` enforces the resulting exact allowed set. Expected: `T:1373-1383` `test_closure_table_covers_all_producer_and_runner_writes` parses the runner and producer such that an added write it cannot see is red. Observed: it only searches literal declared names in `D` and three literal `cp` strings in R; it does not parse either program. Four scratch runner mutations each left that exact test green: `tee "$out/x-tee"`, heredoc `cat > "$out/x-heredoc"`, `python3 -c ...Path(...).write_text`, and `mv` into `$out/x-mv` all returned `1 passed`. Material effect: a future runner can write an evidence file that C will reject, making actual capture fail closure despite the claimed drift gate remaining green. It belongs in the B3 table/test scope. Minimal fix: a deliberately bounded parser/allowlist over every output write form the runner permits, or a structural runner contract that enumerates all final outputs and is exercised by an actual fake-output run. Exact red control: each four mutation above must make the table-drift test fail. The runner source did not change in B3, but this exact test and its B3 claim did.

## Item 2 — F2 producer receipt typing

Reproduced, SOLID: direct `D:118-162` `_normalise` calls always returned the five keys `accepted,event_id,event_id_echoed,http_status,message`. `"false"`, `"true"`, 0, 1, 1.0, and None became `accepted=False` with the named malformed-type reason; booleans retained their value; absent accepted, non-JSON, empty body, and JSON array retained false. Case/whitespace event-id echoes are retained but the consumer rejects them at `C:314-318` `delivery["event_id"]`; an id under another key is not an echo. A 2xx false and 4xx/5xx true are retained by normalisation, then refused by the canonical checker’s `accepted` / status consistency rules at `C:319-358`.

Reproduced, SOLID: replacing a positive leg receipt with producer-normalised `{accepted:"false",http_status:200}` while retaining the real event id caused canonical checker rc 1: `pos-allowed: buzz-acp decides this leg, so the relay must have ACCEPTED ... got False`. `D:204` `receipt = _normalise(...)` is the live writer; B writes its fixtures through `_normalise` at `B:391-393`; additional test mutations are test-only. `B --check` verified the eight committed fixtures are byte identical to a fresh producer-shaped build.

INFO: a malformed accepted response carrying an upstream `message` overwrites the normaliser’s malformed reason at `D:154-159` `message`. Accepted remains false, so this does not reopen F2 or prevent the consumer refusal; preserving both messages is optional diagnostic hardening.

## Item 3 — F3 key normalisation and ordering

Reproduced, SOLID: direct `_privkey` calls at `D:71-89` rejected spaces-only and tab/newline-only after normalization; accepted wrapped valid and uppercase hex (lowercased intentionally); rejected 63/65 chars, inner-space, and 0x forms. No throwaway key was printed. A listener socket owned by the probe saw zero connections when the CLI was given whitespace-only input and an otherwise reachable relay URL: `invalid-key rc=1 ... listener-connections=0`. That behaviourally proves refusal before `_post` at `D:203`, beyond the source-order mirror at `T:1588-1600`.

## Item 4 — F4 documented scanner limit

Reproduced, SOLID: `T:563-618` explicitly defines and pins the direct same-expression class. Its three-statement control is not caught. The direct helper form evades; direct `saturating_sub`, `Duration`, reversed comparison, 9000/900 constants and a direct match-arm are caught. A bound-now declaration on a prior statement naturally evades by itself, while a following direct `now.duration_since(event.created_at)` line is caught. This matches the narrowed B3 report wording at `B3-report.md:58-63`; no broad dataflow claim is now made. This is an honest documented limitation, not a blocker.

## Item 5 — F4/F5 drift and tolerance bounds

Finding B3-02 — BLOCKER, SOLID. Contract mapping: B3 design item 6 requires an assertion `REPLAY_CLOCK_TOLERANCE_S + LEG_CLOCK_TOLERANCE_S < RELAY_DRIFT_WINDOW_S` and a runner-gap assertion `<= REPLAY_CLOCK_TOLERANCE_S`; VERIFY-B3 item 5 expressly requires the named TOLERANCE-9000 mutant to die. Canonical production path: replay tolerance controls C freshness at `C:256-295`; the runner’s default replay wait is 100 s at `R:34` and reuse passes first t0 at `R:145-156`. Expected: both relations are tested. Observed: no such test exists. Changing `C:127` from 150 to 9000 left all 137 tests green (`137 passed in 78.47s`); a 151-second second-replay t0 mutation then passes the mutant but correctly fails the PIN at `C:280-283` with `outside the 150s tolerance`. Changing R's default wait from 100 to 151 also left all 137 tests green (`137 passed in 78.20s`). This falsifies the claimed bounded replay timing assurance and belongs wholly in B3. Minimal fix: add the two literal relationship assertions and mutation tests. Exact red controls: the 9000 and 151 mutants above.

Reproduced, INFO: `T:643-648` parses only a literal `i64 = digits;` upstream constant. On scratch source text it refuses u64, underscores, and expressions; it accepts the first literal in duplicate declarations and comments, so a commented or duplicate wrong first value fails the assertion rather than passing a wrong value. It is an availability/false-red limitation, not a false-green on the current pinned source. Replay behaviour itself matched the local policy: second at 149 s passed, 151 s failed; first at 149/151 s failed with its 120-s limit; second 151 s earlier also failed.

## Item 6 — removal receipt label and trust boundary

Reproduced, SOLID: `C:512-556` checks that a revoked receipt names the actual sender/channel, records `removed is True`, integer `at_epoch_s < t0`, and an integer 2xx HTTP status, then appends the explicit unauthenticated label. Eight canonical scratch cases were all red: empty receipt -> invalid JSON; `{}` -> sender mismatch; symlink -> regular-file guard; bool time -> not int; equal and one-second-after time -> ordering failure; wrong sender and wrong channel -> their named binding failures. The committed label appears in checker output at `C:547-556`, fallback output at `C:717-724`, spec under the named key at `spec.json:3-5`, and provenance at `fixtures/PROVENANCE.md:15-20`. The trust boundary is exactly those unauthenticated coordinator-provided bytes: the checker verifies structure, identity/binding, ordering, and claimed 2xx, but cannot verify the actual relay membership transition or observe post-removal state.

Finding B3-03 — BLOCKER, SOLID. Contract mapping: B3 item 5 promises the same label is pinned in checker output, `limits.removal_receipt`, and provenance; VERIFY-B3 item 6 requires one-of-two-occurrences mutation testing. Canonical path: real revoked output uses the per-leg label, but the checker also exposes fallback label `C:717-720`. Expected: each occurrence is bound by a test. Observed: a scratch mutation of only the fallback second occurrence left both published label tests green (`2 passed`); `T:691-710` only runs a revoked bundle (thus `removal_note` is non-None) and checks substring presence in a named spec key/provenance. Mutating the per-leg occurrence, spec, or provenance individually instead killed one test (`1 failed, 1 passed`), so the survivor is exact and bounded. Material effect: a future no-receipt / structurally changed path can print an altered or unlabelled fallback while the claimed “checker output is labelled” gate remains green. Minimal fix: remove the unreachable/undesired fallback, or directly test its exact full sentence. Exact red control: `LABEL-FALLBACK-DROPPED` must fail. Note schema open keys at `spec.schema.json:10-12` are not themselves a defect because `T:702-710` binds the required `removal_receipt` key.

## Item 7 — omitted B3 brief items

Reproduced, SOLID: items 7–9 are NOT done in `B3-report.md`: no B2 stamp, no named mutation table/killer lines, no identity table/lint/ap-screen/pack, yet `B3-report.md:10` says “Items built (1–9)” over six subsections. This is the separate report-contract blocker B3-00, not merely an informational omission.

## Item 8 — attested regeneration and S0-11 state

Reproduced, SOLID: `python scripts/validate-ledger integrity --root .` reported PRESENT exactly for S0-07, S0-09, S0-10, S0-11, S0-12 and returned 0; `python scripts/ledger-gen --root .` followed by `git diff --exit-code proofs/ledger.json` was clean. `check-proof-status.py` returned rc 1 with only `S0-11: the committed tag object ... is not the object the ref accepted/S0-11 names`. The direct ref object was `7b250da1...`, whereas `git hash-object` of the committed tag file was `b74ee186...`.

Finding B3-04 — FOLLOW-UP, SOLID. `tests/test_proof_status.py` returned `4 failed, 28 passed in 6.17s`, not the brief’s anticipated three re-acceptance class. Two current-tree failures are the S0-11 committed-tag/ref disagreement; the non-git fixture expects a git-repository error but now receives the missing owner-key error. This is outside B3’s component scope and arose in the coordinator’s attested regeneration/status machinery. It is reportable to the coordinator, not a B3 repair loop. The S0-02 suite itself remained 137 green.

## Item 9 — mutation inventory

Reproduced mutation results. All mutations were scratch copies:

| mutant | result / killer |
| --- | --- |
| LEG-SYMLINK | KILLED: canonical rc 1 `neg-stale ... is a symlink` |
| ROOT-SYMLINK | KILLED: canonical rc 1 `bundle ... is a symlink` |
| LEG-EXTRA-FILE | KILLED: canonical rc 1 `unexpected entries ['garbage.txt']` |
| ACCEPTED-TRUTHINESS | KILLED by `T:1555-1585`; string false normalizes to accepted false |
| KEY-WHITESPACE | KILLED behaviorally: CLI rc 1, listener connections 0 |
| RESOLVE-DROPPED | EQUIVALENT: lstat root/leg/subleg/file chain rejects node symlinks; only an operator-selected parent symlink remains |
| LSTAT-TO-ISDIR | KILLED by `T:1323-1352` and canonical B2 outside-leg symlink rc 1 |
| TYPE-TO-ISINSTANCE-INT | KILLED by `T:1555-1585` direct `0/1` receipt cases and `T:1210-1222` bool status case |
| TOLERANCE-9000 | SURVIVED: all 137 green; canonical second-t0 +151 passes under mutant |
| RUNNER-GAP-151 | SURVIVED: all 137 green after R default 100 -> 151 |
| LABEL-DROPPED (per-leg) | KILLED: one test failure under checker-only label change |
| LABEL-FALLBACK-DROPPED | SURVIVED: fallback-only alteration -> `2 passed` |
| RUNNER-TEE-UNSEEN | SURVIVED: `T:1373` -> `1 passed` |
| RUNNER-HEREDOC-UNSEEN | SURVIVED: `T:1373` -> `1 passed` |
| RUNNER-PYTHON-UNSEEN | SURVIVED: `T:1373` -> `1 passed` |
| RUNNER-MV-UNSEEN | SURVIVED: `T:1373` -> `1 passed` |

The unperformed “B2 20 rows” reconstruction cannot be claimed: B3-report has no named list or killer lines from which to reproduce it, and B3 item 8 was not completed. This is covered by blocking report finding B3-00 rather than inventing 20 results.

## Item 10 — bounded 18-class / evidence-read rescan

Reproduced, INFO: in C, AST/literal scan found field-literal equality branches at `C:248`, `C:386`, `C:443`; the first has a raising consequence and the other two select required channel policy followed by checks, so no fail-open `if <field> == <literal>` branch was found. Evidence byte reads are regular-file guarded through `_read_json` at `C:170-175` (fixture, delivered event, t0, delivery, membership); direct log reads are guarded at `C:379-380`, `C:499-500`, and `C:506`; identities at `C:664-666` is guarded. `_load_timeline_raw` is the S0-01 guarded reader aliased at `C:96-99`. I found no C evidence `read_text`, `open`, or `json.load` bypassing the regular-file guard. D/B/R reads are producer/build-time inputs, not checker evidence reads; D's `fixture_path` and `--reuse` at `D:178-184`, B construction reads at `B:89,417,499,503,535`, and R role/replay helper opens at `R:132,153` are not an S0-02 checker bypass.

## Item 11 — discipline, process census, and gaps

Reproduced: no background jobs started, no live relay delivery, membership write, role-key read, PC service action, or process kill occurred. All scratch probes were foreground and self-terminated; FIFO was canonical and bounded. Skipped as forbidden: live eight-leg capture and membership removal. The S0-11 owner re-sign remains owner/coordinator-only.

DISCREPANCIES: `tests/test_proof_status.py` measured `4 failed, 28 passed`, not the brief’s expected three committed-state failures. `check-proof-status.py` has no `--root` option despite the brief’s command spelling; direct invocation returned the exact S0-11 tag/ref mismatch above. `strace` was unavailable to this unprivileged lane (`Permission denied`), so the permitted owned listener was used for F3 network-order evidence. `report_lint` final third bounded round: `report_lint: 67 refs — OK 25, NEAR 0, MISS 13, UNCHECKABLE 23, UNRESOLVED 6 (at c6c384a)` (rc 1). Per the bounded instruction, these remaining heuristic misses/unresolved report references are reported, not chased further.

## Item 12 — design state

The synthetic bundles use the producer normaliser end-to-end for receipt shape (`B:391-393`, `D:118-162`) and test checker policy only. They do not prove a live relay HTTP exchange, Buzz membership transition, ACP launch, or turn reachability. A live eight-leg capture must record: RUST_LOG=debug through P5c’s `--env-set s0-02` seam for buzz-acp denial observables; owner-provided role keys without exposing them; and the owner/coordinator’s real membership removal plus receipt for revoked. Those are coordinator/owner operations, not this lane’s. Round 4 must repair B3-00 through B3-03 with red discriminators, then undergo a fresh sandbox-side independent grade; the live capture remains a separate readiness prerequisite.

## Finding inventory and recommendation

1. B3-00 — BLOCKER / SOLID: B3 report discipline items 7–9 omitted while claimed; canonical required artifact lacks evidence. Fix report/stamp and grounded named mutation inventory.

2. B3-01 — BLOCKER / SOLID: table-drift test does not parse/cover actual runner writes; four write forms survive. Fix structural runner-output gate.

3. B3-02 — BLOCKER / SOLID: tolerance and runner-gap relations absent; TOLERANCE-9000 and gap-151 survive. Add relation assertions and red mutants.

4. B3-03 — BLOCKER / SOLID: checker fallback label is unbound; exact fallback-only mutant survives. Remove or test fallback.

5. B3-04 — FOLLOW-UP / SOLID: coordinator’s S0-11 re-acceptance/tag state has four proof-status test failures, outside B3 scope.

6. INFO: F1 containment, F2 typing, F3 pre-network refusal, and F4 narrow scanner limit reproduced as described; no runtime containment bypass found.

GATE RECOMMENDATION: NOT-READY — B3-00, B3-01, B3-02, and B3-03 each satisfy the full blocking predicate: frozen B3 criterion, current canonical path, material evidence/gate effect, deterministic survivor/red control, and B3 ownership. This is a recommendation from the PC single-model verifier; final gate decision and independent adversarial grade belong to the coordinator.
