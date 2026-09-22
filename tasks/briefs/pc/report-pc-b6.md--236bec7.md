# B6 report — issue #3: S0-02's F3 pre-network key refusal EXECUTED through the real CLI

PIN 236bec7 · lane pc-b6.md · route agentfactory-build-local

## FILE IDENTITY

- `tests/test_s0_02_buzz_authz.py` — extended (new tests appended + 3 imports + 3 module helpers and 1 listener class).
- `tasks/briefs/s0-02-support/B6-report.md` — this report.
- Read-only contracts checked: `proofs/S0-02/spec.json` names the real checker legs; the S0-02 seed block classifies this as an execution proof and requires distinct negative reasons.
- Scratch only: `../scratch/b6/mirror/proofs/S0-02/tools/pc/deliver_event.py` (F3-KEY-SHAPE-BYPASS mutant copy).

## Item 1 — PREMISE: the F3-KEY-SHAPE-BYPASS mutant survives the current F3 test (reproduced on the PIN)

Mutant (scratch copy of the production file, `D:78` at PIN): the shape check

`if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):`

weakened to

`if len(key) != 64:  # F3-KEY-SHAPE-BYPASS (B6 scratch mutant): hex check weakened, message kept`

Refusal source weakened, refusal MESSAGE kept, so the source-shape assertions still find their strings.

Run in a scratch mirror tree (`cp -a proofs` + `cp -a tests`, only `DELIVER` repointed to the mutant file):

```text
$ python -m pytest -q -p no:cacheprovider --basetemp ../scratch/bt/mutantF3 \
    ../scratch/b6/mirror/tests/test_s0_02_buzz_authz.py::test_privkey_normalises_then_refuses_before_any_network_action
.                                                                        [100%]
1 passed in 0.16s
```

`1 passed` on the mutant. The current F3 test at `T@236bec7:1801` (`test_privkey_normalises_then_refuses_before_any_network_action`) is source-shape-only: `T@236bec7:1809-1812` asserts `BUZZ_PRIVATE_KEY` source text; nothing executes the CLI.

PREMISE REPRODUCED; proceed to the behavioural test. Sanity, production file, same test: `1 passed in 0.07s`.

## Items 2–5 — behavioural test, positive control, mutant kill, de-vacuous controls

### Behavioural test: production bytes green

The new `test_cli_refuses_a_malformed_key_before_any_connection` runs the real `deliver_event.py` subprocess through its real `main` (`D:165`) with a closed environment, `BUZZ_PRIVATE_KEY="z" * 64`, and `--relay-http` aimed at an owned `127.0.0.1:0` listener.

It asserts the source-named `SystemExit` rc (`1`) and exact stderr `BUZZ_PRIVATE_KEY` refusal from `D:85-88`. The `listener.count == 0` assertion is at `T:1934-1936`.

Paired with `test_cli_with_a_valid_key_reaches_the_owned_listener`: the same CLI receives a scalar from `_throwaway_secp256k1_key` at `T:1941-1950`, signs through the real consumer, POSTs `/events`, gets the owned listener's minimal HTTP 200, exits 0, and proves one accepted connection plus one observed `POST /events` with NIP-98 Authorization and JSON content at `T:1971-1981`. The listener's zero can therefore become one.

Focused production-byte run:

```text
$ python -m pytest -q -p no:cacheprovider --basetemp ../scratch/bt/focused2 \
    tests/test_s0_02_buzz_authz.py::test_privkey_normalises_then_refuses_before_any_network_action \
    tests/test_s0_02_buzz_authz.py::test_cli_refuses_a_malformed_key_before_any_connection \
    tests/test_s0_02_buzz_authz.py::test_cli_with_a_valid_key_reaches_the_owned_listener
...                                                                      [100%]
3 passed in 1.86s
```

Earlier initial new-test-only green before deterministic-key tightening: `2 passed in 0.67s`.

### Mutant kill

Final new refusal test against the same item-1 F3-KEY-SHAPE-BYPASS mutant:

```text
F                                                                        [100%]
>           assert proc.stderr.decode("utf-8").strip() == REFUSE_TEXT, (
E               AssertionError: wrong refusal text: 'Traceback (most recent call last):\n  File "/home/rocco/agent-factory/.lanes/pc-b6.md--236bec7/scratch/b6/mirror/proofs/S0-02/tools/pc/deliver_event.py", line 221, in <module> ... File ".../deliver_event.py", line 194, in main\n    event = nv.sign_event(privke'
E                 - BUZZ_PRIVATE_KEY is not a valid key shape (exactly 64 lowercase hex characters, as nv.sign_event requires)
E                 + Traceback (most recent call last):
FAILED ../scratch/b6/mirror/tests/test_s0_02_buzz_authz.py::test_cli_refuses_a_malformed_key_before_any_connection
1 failed in 0.48s
```

The mutant is killed at `T:1932` by the exact `REFUSE_TEXT` assertion. It reaches the downstream `nv.sign_event` call at `D:194`, which raises a traceback rather than the clean `_privkey` `SystemExit` emitted at `D:85-88`. Exit code alone is intentionally insufficient because both paths return 1; stderr discriminates the refusal source. No production file changed.

### De-vacuous assertion flips (scratch copies only; every flip restored by construction)

Each row was a separate one-assert mutation over a scratch copy backed by the production `deliver_event.py`; each run selected only the owning test. Every run was red at its own assert, `rc=1`, exactly `1 failed`:

```text
flip refusal rc 1 -> 2:       AssertionError: rc=1 ...                 1 failed in 0.49s
flip exact stderr + "!":      AssertionError: wrong refusal text ...  1 failed in 0.46s
flip refusal count 0 -> 1:    AssertionError: count=0 ...              1 failed in 0.47s
flip positive rc 0 -> 1:      AssertionError: rc=0 stderr=''          1 failed in 0.79s
flip positive count 1 -> 0:   AssertionError: expected zero, saw 1    1 failed in 0.80s
flip request count 1 -> 2:    flip_preq.py:1977 AssertionError        1 failed in 0.90s
flip POST /events -> /WRONG:  AssertionError: POST /events HTTP/1.1   1 failed in 0.90s
flip Authorization present:   flip_pauth.py:1980 AssertionError       1 failed in 0.81s
flip Content-Type present:    flip_pctype.py:1981 AssertionError      1 failed in 0.80s
```

Evidence tier: VERIFIED by this session's real subprocess/listener executions. No inference is used for the connection claim; the paired control observed the request bytes.

## Final gates — final bytes

Timestamp: `2026-09-22T02:18:08Z`.

Two complete module runs on the final test-file bytes (SHA-256 below), xdist 4:

```text
$ python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/final5 tests/test_s0_02_buzz_authz.py
bringing up nodes...
bringing up nodes...

........................................................................ [ 47%]
........................................................................ [ 95%]
.......                                                                  [100%]
151 passed in 11.69s
```

```text
$ python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/final6 tests/test_s0_02_buzz_authz.py
bringing up nodes...
bringing up nodes...

........................................................................ [ 47%]
........................................................................ [ 95%]
.......                                                                  [100%]
151 passed in 11.65s
```

Static/screen/hash:

```text
$ python -m pyflakes tests/test_s0_02_buzz_authz.py
PYFLAKES_RC=0

$ python3 scripts/ap_screen.py --tests tests/test_s0_02_buzz_authz.py
--- TEST_SCREEN over 1 path(s): 11 hits over 1 files ---
AF-AP-80: 7
AF-AP-34: 4
    tests/test_s0_02_buzz_authz.py:1676: for word in ("pkill", "killall", "pgrep"):

$ sha256sum tests/test_s0_02_buzz_authz.py
1458321a186d7b63ab878118a94520174431438c179ee1e00c8a83bab4f7a962  tests/test_s0_02_buzz_authz.py
```

Screen classification: all 11 hits pre-exist this lane's hunk. The seven AF-AP-80 hits are older source-shape controls: `removal_line` at `T:720-721`, `DEBUG_LEVEL_CANARY` at `T:1034`, `_load_timeline_raw` at `T:1608-1641`, and `os.environ` at `T:1664`.

The four AF-AP-34 hits are the existing `pkill` process-safety test/docstring at `T:1672-1676`.

The B6 hunk starts with `B6` at `T:1818`; none of the 11 screen hits occurs in it.

RUN: PRE-EXISTING / NOT INTRODUCED.

Code-intel pack: `../scratch/b6/B6-pack.md` (211 lines). Graft mapped the two new tests and helpers at `T:1840-1983`; ripwire found `_OwnedListener` reached by exactly those two tests.

GitNexus and code-review-graph were unmapped for new uncommitted symbols because their clone indexes do not contain the lane diff. Ripwire `test-gate` over this large historical test module reported broad name-resolution spill (`impacted=82`, `tests=8`, `untested=7`, rc 4); it is advisory and does not override the brief's explicit module gate, which passed twice.

## Boundary

```text
$ git status --porcelain
 M tests/test_s0_02_buzz_authz.py
?? tasks/briefs/s0-02-support/B6-report.md

$ git diff --quiet 236bec7 -- proofs/
PROOFS_DIFF_QUIET_RC=0
```

Exactly the two allowed files are present. `proofs/S0-02/**` remains byte-identical to PIN. No relay delivery, no network beyond the owned loopback listener, no git write, no outward action.

## DISCREPANCIES

- The brief says a well-formed key “generated in-test.” I used a deterministic SHA-256-derived, range-reduced test-only secp256k1 scalar instead of runtime randomness. This preserves the throwaway/no-real-key property while making the test bitwise deterministic; the producer is `_throwaway_secp256k1_key` at `T:1941-1950`.
- The initial `lane_context.sh` call passed multiple symbols after one `-s`; it treated trailing symbols as files and returned rc 64. Correct repeated `-s` invocation wrote the 211-line pack.
- GitNexus `impact` / `detect-changes` against the clone index cannot see this detached lane's uncommitted symbols/diff (`risk: UNKNOWN` / `No changes detected`). The required lane pack records this explicitly; graft + ripwire map the live working-tree hunk.
- Item 4's mutant failure discriminates on exact stderr, not exit code: the clean `_privkey` `SystemExit(str)` and the downstream `ValueError` traceback both exit 1. This is why the test asserts all three dimensions but the named mutant dies at `T:1932` on `REFUSE_TEXT`.
- Final `report_lint --min-refs 10`: `report_lint: 28 refs — OK 24, NEAR 0, MISS 0, UNCHECKABLE 4, UNRESOLVED 0 (worktree)` (round 2; floor met).

## NOT-done

- No production change. The existing production behavior was correct; this increment hardens its behavioral proof only.
- No real relay, real key, external network, proof mint, ledger edit, commit, push, or acceptance.
- Independent adversarial verification is NOT done by this build lane. This report is a proposal until the sandbox-side adversarial-verifier grades it.

## Self-attack

1. The zero could be tautological because the listener cannot observe connections. Ruled out: `test_cli_with_a_valid_key_reaches_the_owned_listener` at `T:1953` records one `POST /events` at `T:1973-1981`; count flip red at its own assert.
2. The test could import a helper instead of executing the real CLI. Ruled out: `_run_deliver_cli` at `T:1893` invokes `sys.executable` and `DELIVER` at `T:1899`, full production argv, and `env=env` at `T:1906`. The mutant traceback reaches `nv.sign_event(privkey` at `D:194`.
3. A downstream signer refusal could masquerade as the requested `_privkey` refusal. Ruled out: `REFUSE_TEXT` equality at `T:1932-1933` kills the weakened guard even though both paths exit 1; item 1 proves the old shape-only test did not distinguish them.

## GATE RECOMMENDATION

MERGE-READY as a build-lane proposal: premise reproduced; behavioral negative + paired positive control execute the real CLI; named shape-guard mutant killed; every new assertion de-vacuoused; 151 tests pass twice on identical final bytes; pyflakes rc 0; boundary exact; production untouched.

The coordinator and sandbox adversarial-verifier retain the verdict.

Retro: nothing to bake. The only tooling discrepancy (repeat `-s` for each lane-context symbol) is already explicit in this report; no project defect was found or fixed beyond the brief's known test-strength gap, so no new bug-echo or incident row is warranted.

Graft token savings this turn: approximately 4,338 tokens.
