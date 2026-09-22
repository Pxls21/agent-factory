# VERIFY-B67 — adversarial verification report

PIN: `22bd6f5f85a6bf992363c80b6cd71e81ac2bc3ff`

CONTRACT-INVALID: frozen item 6 requires the individual real-root rc-set mutant to fail at its own line. The checker’s independent `PASS:` assertion prevents that condition. Coordinator amendment is required before re-verification.

## Scope and evidence discipline

Verified only B6 (`T2:1813-1991` — `_privkey`) and B7 (`R:46-76` — `RUST_LOG=debug`; `T2:804-819` — `deferred`; `T2:1722-1745` — `PINNED_ENV_KEYS_S0_02`) on immutable production bytes at PIN. Scratch-only probes and archive mutations live under `../scratch`; no runner leg, relay, harness, secret, service, git mutation, or external action was run. `report-draft.md` and `tasks/briefs/s0-02-support/VERIFY-B67-report.md` are the only untracked worktree files.

Evidence levels: SOLID means directly reproduced through the named real CLI/checker/runner path; UNSURE means static-only or bounded by venue safety. The current production `proofs/S0-02/evidence` root is absent at this PIN, so its real-root check returns deferred (`rc=2`); historic partial-root behavior was not represented as current bytes.

## Item 1 — PREMISE

SOLID. Re-measured at the verifier worktree:

```text
$ git log --format='%h %s' 236bec7..22bd6f5 -- proofs/S0-02 tests/test_s0_02_buzz_authz.py
22bd6f5 S0-02 runner: B7 LANDS the env-set selection + the exact-pin preflight (items 2-3; the live capture stays NOT-READY — the partial evidence is recorded in the harvest patch, not landed)
c439580 S0-02 B6 LANDED (issue #3): the F3 pre-network key refusal EXECUTED through the real deliver_event.py against an owned loopback listener (connections == 0), paired with the connecting positive control; the shape-guard mutant that survived the old source-shape test now dies at the exact refusal text

$ git diff c439580^ c439580 -- tests/test_s0_02_buzz_authz.py | grep '^@@'
@@ -11,13 +11,16 @@ skip; only an unset venue (CI) skips, and it skips by declaration.
@@ -1810,3 +1813,171 @@ def test_privkey_normalises_then_refuses_before_any_network_action():

$ git diff 22bd6f5^ 22bd6f5 -- proofs/S0-02/tools/pc/run_s0_02_legs.sh tests/test_s0_02_buzz_authz.py | grep -E '^diff|^@@'
diff --git a/proofs/S0-02/tools/pc/run_s0_02_legs.sh b/proofs/S0-02/tools/pc/run_s0_02_legs.sh
@@ -46,21 +46,21 @@ say() { echo; echo "===== [S0-02] $* ====="; }
@@ -70,6 +70,7 @@ mkdir -p "$DEST"
diff --git a/tests/test_s0_02_buzz_authz.py b/tests/test_s0_02_buzz_authz.py
@@ -804,12 +804,16 @@ def test_deferred_when_the_evidence_root_is_absent(tmp_path):
@@ -1718,20 +1722,24 @@ def test_pc_runner_names_user2_for_the_not_allowlisted_leg():

$ sha256sum tests/test_s0_02_buzz_authz.py proofs/S0-02/tools/pc/run_s0_02_legs.sh proofs/S0-02/tools/pc/deliver_event.py
4444842b886ac7debf3bccceaba8cb55eae83e577ebbfb491bc0b3f147426dc6  tests/test_s0_02_buzz_authz.py
c092e8797ee7c42b06e578a2887b3905555fff65472c913effd039e4ff7123cb  proofs/S0-02/tools/pc/run_s0_02_legs.sh
a14c027b0da2f341cce8b37dfcce4efbd947fe49b1bc2bec5831f1cd5e00cf8a  proofs/S0-02/tools/pc/deliver_event.py
```

`git status --short` was empty before the report. All range, hunk, and identity premises match. Focused frozen-contract command, with the PC venue pair exported:

```text
$ python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/pre tests/test_s0_02_buzz_authz.py -k "cli_refuses or cli_with_a_valid_key or preflights_and_selects or not_a_passing_bundle_today"
....
4 passed in 1.15s
RC=0
```

Blocking predicate: no finding. The premise is neither contradictory nor unmeasurable.

## Code-intelligence record

`graft skeleton` maps D `_privkey` at `D:71-89`, `_nip98_header` at `D:92-103`, `_post` at `D:106-115`, `_normalise` at `D:118-162`, and `main` at `D:165-217`; it maps B6 helpers/tests at `T2:1848-1991` and B7 test at `T2:1725-1742`. `scripts/lane_context.sh` wrote `../scratch/B67-pack.md` (201 lines). Ripwire maps `_privkey` to `main` at `D:182`; subprocess test reachability is structurally outside its in-process graph. Graft maps `pc_launch.launch_env` at `proofs/S0-01/tools/pc/pc_launch.py:242-278`; its real `--help` exposes `--env-set {s0-01,s0-02}`. GitNexus resolves D `main` and `_privkey` but reports an index 439 commits behind HEAD; it cannot resolve shell `launch_leg` (`risk: UNKNOWN`). No tool output is treated as proof of shell reachability.

## Item 2 — B6 through an independent owned listener

SOLID. I wrote a scratch listener, separate from T2’s helper. It bound `127.0.0.1:0`, counted accepts, retained request bytes, supplied only HTTP 200 `{}`, and invoked the real `D` CLI with the T2 argv shape and `env={BUZZ_PRIVATE_KEY, PATH}`. The key was never placed in argv. Every refusal row had `connections=0` and `bytes=0`; the valid rows demonstrated listener power with one accepted 1,360-byte request.

| key case | rc | stderr first line | connections | bytes |
|---|---:|---|---:|---:|
| valid throwaway scalar | 0 | empty | 1 | 1360 |
| 63 hex | 1 | valid key shape | 0 | 0 |
| 65 hex | 1 | valid key shape | 0 | 0 |
| 64 chars, one `g` | 1 | valid key shape | 0 | 0 |
| `0x` + 62 hex | 1 | valid key shape | 0 | 0 |
| empty | 1 | not in the environment | 0 | 0 |
| whitespace only | 1 | not in the environment | 0 | 0 |
| valid uppercase | 0 | empty | 1 | 1360 |
| valid padded with spaces/newline | 0 | empty | 1 | 1360 |
| `0` ×64 | 1 | `Traceback (most recent call last):` | 0 | 0 |
| `f` ×64 | 1 | `Traceback (most recent call last):` | 0 | 0 |

Exact production command class: `/home/rocco/venv-agent-factory/bin/python proofs/S0-02/tools/pc/deliver_event.py --fixture pos-allowed --leg-dir <scratch>/leg --secret role.env --relay-http http://127.0.0.1:<owned-port> --t0 1700000000`, closed environment as above.

The malformed classes reject through D’s exact `SystemExit` at `D:78` (`os.environ.get("BUZZ_PRIVATE_KEY", "").strip().lower()`) and `D:84-88` (`if len(key) != 64`); empty/whitespace reject through `D:79-83`; valid uppercase/padded values prove `D:78` normalizes. Both scalar-out-of-range shapes pass D’s format check then produce a raw traceback from the `nv.sign_event` consumer at `nostr_verify.py:230-235` before `_post`; direct real-CLI probes identify the exception as `ValueError: invalid private key`, exit 1, zero connections. This is a meaningful robustness observation, but does not contradict B6’s frozen shape-only contract or its no-connection claim.

Blocking predicate for scalar traceback: contract mapping = none (D documents the consumer’s 64-lowercase-hex format only); canonical = yes; material = clean error quality only; discriminator = yes; task ownership = D, but all five clauses are not met. Classification: FOLLOW-UP, not blocker.

## Item 3 — side-effect ordering and evidence effect

SOLID. `D:179-182` creates `leg_dir` before calling `_privkey`; each malformed independent-listener run left the directory present with `files=[]`. I drove the frozen checker over a scratch normal-anchor evidence root (the real CLI check path, not a test helper) in two states; the final normal-anchor control returned the exact outputs below.

```text
$ check_buzz_authz.py <scratch>/evidence
# present but empty neg-unauthorized
failure_reason: neg-unauthorized: missing ['buzzacp.log', 'delivered-event.json', 'delivery.json', 'fixture.json', 't0.json', 'timeline.jsonl']
PRESENT_EMPTY_RC=1

# neg-unauthorized directory absent
failure_reason: neg-unauthorized: neg-unauthorized leg directory absent
ABSENT_RC=1
```

The checker distinguishes an empty created leg from an absent leg through `_leg_closure` at `check_buzz_authz.py:155-167` and `_check_leg` at `:457-464`. R’s `deliver()` at `R:125-130` invokes `exec /usr/bin/python3 "$DELIVER"` with the target leg directory; `set -euo pipefail` at `R:18` means D’s rc 1 stops the runner before `collect_leg()` at `R:113-123`. Thus a refused key can leave a half-made leg that fails differently from an absent one. The actual current PIN has no `proofs/S0-02/evidence` root: `check_buzz_authz.py proofs/S0-02/evidence` prints `deferred: S0-02 evidence not captured`, `rc=2`, so the historic partial-root message cannot be asserted as current repository state.

Classification: INFO. Contract mapping for B6 is only pre-network refusal; this side effect does not change `listener.count == 0`, and B7’s `test_real_evidence_root_is_not_a_passing_bundle_today` at `T2:807-816` admits either non-pass outcome. No qualifying blocker.

## Item 4 — positive-control binding strength

SOLID. Decoding the captured NIP-98 header from the independent listener gave:

| binding | independent capture | B6 T2 asserts? |
|---|---|---|
| request | `POST /events HTTP/1.1` | yes, `T2:1987` |
| URL `u` tag | `http://127.0.0.1:45499/events` | no |
| `method` tag | `POST` | no |
| `payload` tag | equals SHA-256 of exact request body: `c5fde7…2a94` | no |
| NIP-98 signature | `nv.verify_event(event) == (True, "valid")` | no |
| pubkey identity | `d63c0f10122673118b6b30b23d36ee4a55e7602769f85ec208db55c40acabb81` equals the derived throwaway-key pubkey | no |
| headers | Authorization Nostr and JSON Content-Type | yes, `T2:1988-1989` |

The CLI receipt written after the listener’s `{}` response was `{"accepted": false, "event_id": "6f456ab78abd760a21671d5b88c3fbe7744f900528832f12d3883ee4f9877c70", "event_id_echoed": false, "http_status": 200, "message": "{}"}`. `accepted` is bool and `event_id_echoed` is bool/false, consistent with the B3 producer type contract at `D:134-162`; `T2:1756-1775` and `T2:1779-1809` directly cover the normalizer’s typed behavior.

Classification: INFO. Suggested one-line hardening: decode the captured Authorization event and assert `u`, `method`, `payload`, signature validity, and derived-pubkey equality. It is not a frozen B6 criterion; the real CLI, request bytes, and positive connection were reproduced.

## Item 5 — mutation audit

SOLID for m1–m3, m5–m7. Each mutant was created from `git archive 22bd6f5` in a separate scratch tree, compiled (`py_compile` for D mutants) or syntax-checked (`bash -n` for R mutants), then collect-checked: m1/m2/m3/m5/m6/m7 each selected `1/151`, m4 selected `2/151`, all `--collect-only` rc 0. No production guard was mutated. m4 exposes a pairing gap, detailed below.

The unmutated production R preflight was also driven on two `S0_02_REPO=<scratch>` trees: one removed the `PINNED_ENV_KEYS_S0_02` `RUST_LOG` extension, and one commented the exact `PINNED_ENV_VALUES_S0_02` line. Both returned `rc=3`, printed `BLOCKER: pins.PINNED_ENV_KEYS_S0_02 / PINNED_ENV_VALUES_S0_02`, and left DEST absent. This is the canonical failed-preflight path in `R:52-68`; no launcher ran.

| mutant | result / killer | assertion or behavioral discriminator | classification |
|---|---|---|---|
| m1 D length-only shape check | KILLED, `1 failed` | exact `REFUSE_TEXT` at `T2:1940`; signer traceback differs | SOLID |
| m2 scratch calls `_privkey` after POST (temporary valid signing key) | KILLED, `1 failed` | `assert listener.count == 0` at `T2:1942` sees `count=1` | SOLID behavioral kill |
| m3 return empty instead of `SystemExit` | KILLED, `1 failed` | `REFUSE_TEXT` equality at `T2:1940`; downstream traceback | SOLID |
| m4 remove `.strip()` | B6 CLI tests SURVIVE: `2 passed`; old in-process source scan dies at `T2:1823` (`strip().lower()`) | independent mutated-CLI probe: whitespace changes from empty-refusal to shape-refusal; padded valid changes from POST to shape-refusal | FOLLOW-UP AF-AP-80 pairing gap |
| m5 R `grep -Fqx` → `grep -Fq`, pins only commented line | static source pin KILLED, `T2:1735` (`grep -Fqx`); behavioral scratch run wrongly passes preflight (`rc=99` safe stop, no DEST) | text mirror only; no behavioral preflight test owns this | FOLLOW-UP AF-AP-80 pairing gap |
| m6 move preflight below `mkdir -p` | static source pin KILLED, `T2:1731` (`exit 3`); behavioral mutated pins run has `rc=3`, `dest=True` | no test asserts no DEST on refused pins | FOLLOW-UP AF-AP-80 pairing gap |
| m7 drop `--env-set s0-02` | KILLED, `1 failed` | `assert '--env-set s0-02' in launch` at `T2:1742` | SOLID source pin |

Verifier output summary:

```text
m1: 1 failed, 150 deselected in 0.46s — `assert proc.stderr.decode("utf-8").strip() == REFUSE_TEXT` at T2:1940
m2: 1 failed, 150 deselected in 0.82s — `assert listener.count == 0` at T2:1942 sees count=1
m3: 1 failed, 150 deselected in 0.47s — `REFUSE_TEXT` at T2:1940
m4: 2 passed, 149 deselected in 0.96s (CLI-only); source test 1 failed at T2:1823 (`strip().lower()`)
m5: 1 failed, 150 deselected in 0.22s — `grep -Fqx` at T2:1735; behavioral safe-stop rc=99, DEST=false
m6: 1 failed, 150 deselected in 0.22s — `exit 3` at T2:1731; behavioral rc=3, DEST=true
m7: 1 failed, 150 deselected in 0.21s — `--env-set s0-02` at T2:1742
```

m4 canonical distinction is real, not inferred: the mutation leaves malformed-shape B6 coverage green but changes whitespace-only stderr from `not in the environment` to `valid key shape`, and padded valid from a connecting POST to refusal. This behavior lies in B6’s actual CLI input domain. m5/m6 were safety-tested only with a failed preflight / safe stop; no runner leg was launched.

Blocking predicate for m4/m5/m6 gaps: contract mapping = no explicit frozen requirement for those exact behavioral controls; canonical = yes; material = test-strength, not current production output; discriminator = yes; ownership = current test/runner component. They do not satisfy the full predicate. FOLLOW-UPs, not blockers.

## Item 6 — de-vacuous controls

CONTRACT-INVALID finding. I ran a final function-bounded scratch audit: every mutation compiled, collected exactly `1/151`, and changed one assertion only inside its owning test. The B6 assertions and B7 source/branch assertions red at their owning lines. The frozen literal requirement for the B7 `rc-set` mutation cannot red at its own line on the unmodified current checker path: it survives on absent/partial failure states (`rc=2`/`rc=1`), and a real checker success (`rc=0`) is caught instead by the independent retained `PASS:` assertion at `T2:812`. The test remains fail-closed, but the brief explicitly requires this mutation to red at its own line; that requirement is unmeasurable as stated.

```text
$ /home/rocco/venv-agent-factory/bin/python ../scratch/b67_exact_assertion_audit.py
EXACT_ASSERTION_AUDIT_RC=0
b6-refusal-rc: collect=1/151 rc=1; `assert proc.returncode == REFUSE_RC` T2:1938 AssertionError; 1 failed
b6-refusal-text: collect=1/151 rc=1; `assert proc.stderr.decode("utf-8").strip() == REFUSE_TEXT` T2:1940 AssertionError; 1 failed
b6-refusal-count: collect=1/151 rc=1; `assert listener.count == 0` T2:1942 AssertionError; 1 failed
b6-key-shape: collect=1/151 rc=1; `assert len(privkey) == 64` T2:1970 AssertionError; 1 failed
b6-positive-rc: collect=1/151 rc=1; `assert proc.returncode == 0` T2:1979 AssertionError; 1 failed
b6-positive-count: collect=1/151 rc=1; `assert listener.count == 1` T2:1981 AssertionError; 1 failed
b6-request-count: collect=1/151 rc=1; `assert len(listener.requests) == 1` T2:1985 AssertionError; 1 failed
b6-post-line: collect=1/151 rc=1; `assert req.startswith("POST /events HTTP/1.1")` T2:1987 AssertionError; 1 failed
b6-authorization: collect=1/151 rc=1; `assert "Authorization:" in req` T2:1988 AssertionError; 1 failed
b6-content-type: collect=1/151 rc=1; `assert "Content-Type: application/json" in req` T2:1989 AssertionError; 1 failed
b7-real-rc-strict: collect=1/151 rc=1; `assert proc.returncode in (1, 2)` T2:811 AssertionError; 1 failed
b7-real-pass-text: collect=1/151 rc=1; `assert "PASS:" not in proc.stdout` T2:812 AssertionError; 1 failed
b7-real-absent-text: collect=1/151 rc=1; `assert "deferred: S0-02 evidence not captured" in proc.stdout` T2:816 AssertionError; 1 failed
b7-real-partial-text: collect=1/151 rc=1; `assert "leg directory absent" in proc.stdout` T2:814 AssertionError; 1 failed
b7-preflight-blocker: collect=1/151 rc=1; `assert "exit 3" in preflight` T2:1731 AssertionError; 1 failed
b7-preflight-key-name: collect=1/151 rc=1; `assert "PINNED_ENV_KEYS_S0_02" in preflight` T2:1732 AssertionError; 1 failed
b7-preflight-value-name: collect=1/151 rc=1; `assert "PINNED_ENV_VALUES_S0_02" in preflight` T2:1733 AssertionError; 1 failed
b7-preflight-grep-e: collect=1/151 rc=1; `assert "grep -Eq '^PINNED_ENV_KEYS_S0_02" in preflight` T2:1734 AssertionError; 1 failed
b7-preflight-grep-fx: collect=1/151 rc=1; `assert "grep -Fqx 'PINNED_ENV_VALUES_S0_02" in preflight` T2:1735 AssertionError; 1 failed
b7-pins-key-definition: collect=1/151 rc=1; `assert 'PINNED_ENV_KEYS_S0_02 = PINNED_ENV_KEYS | frozenset({"RUST_LOG"})' in pins` T2:1738 AssertionError; 1 failed
b7-pins-value-definition: collect=1/151 rc=1; `assert 'PINNED_ENV_VALUES_S0_02 = {"RUST_LOG": "debug"}' in pins` T2:1739 AssertionError; 1 failed
b7-launch-env-set: collect=1/151 rc=1; `assert '--env-set s0-02' in launch` T2:1742 AssertionError; 1 failed
rc-set-broadened-absent: collect=1/151 pytest_rc=0; checker_rc=2; deferred: S0-02 evidence not captured
rc-set-broadened-partial: collect=1/151 pytest_rc=0; checker_rc=1; neg-unauthorized leg directory absent
rc-set-broadened-pass: collect=1/151 pytest_rc=1; checker_rc=0; `assert "PASS:" not in proc.stdout` T2:812 AssertionError; 1 failed
```

The brief-named literal controls were also executed exactly as stated:

```text
REFUSE_TEXT altered by one character: rc=1; `assert proc.stderr.decode("utf-8").strip() == REFUSE_TEXT` T2:1940 AssertionError; 1 failed
REFUSE_RC 1→0: rc=1; `assert proc.returncode == REFUSE_RC` T2:1938 AssertionError; 1 failed
refusal count 0→1: rc=1; `assert listener.count == 0` T2:1942 AssertionError; 1 failed
positive count 1→0: rc=1; `assert listener.count == 1` T2:1981 AssertionError; 1 failed
launch-string pin altered: rc=1; `assert '--env-set s0-02' in launch` T2:1742 AssertionError; 1 failed
rc-set (1,2)→(0,1,2), absent root: rc=0; 1 passed, 150 deselected
```

The `rc-set` mutant remains green on all valid failure states because it still accepts `rc=1` and `rc=2`, and output has no `PASS:`. On a successful current checker, the separate output assertion kills first. This is `CONTRACT-INVALID`, not a code defect or a repair order. Contract mapping = literal item 6; checker CLI semantics = reproduced through unmodified checker bytes on a scratch normal-anchor input, not live evidence; material production effect = none; discriminator = yes; task ownership = coordinator contract amendment. Do not weaken `PASS:` or invent a fake checker response. A new contract can ask for the AND gate to red on a successful root, or can isolate the return-code arm by an approved deterministic seam.

## Item 7 — gates on PIN bytes

SOLID.

```text
$ python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/v1 tests/test_s0_02_buzz_authz.py
151 passed in 11.36s

$ python -m pytest -n 4 -q -p no:cacheprovider --basetemp ../scratch/bt/v2 tests/test_s0_02_buzz_authz.py
151 passed in 11.16s

$ scripts/test_summary.sh tests/test_s0_02_buzz_authz.py
151 passed in 40.19s
pytest-exit: 0
pytest-summary: 151 passed in 40.19s

$ python -m pyflakes tests/test_s0_02_buzz_authz.py proofs/S0-02/tools/pc/deliver_event.py
PYFLAKES_RC=0

$ bash -n proofs/S0-02/tools/pc/run_s0_02_legs.sh
BASH_N_RC=0

$ python3 scripts/ap_screen.py proofs/S0-02/tools/pc/run_s0_02_legs.sh
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---

$ python3 scripts/ap_screen.py --tests tests/test_s0_02_buzz_authz.py
--- TEST_SCREEN over 1 path(s): 11 hits over 1 files ---
AF-AP-80: 7
AF-AP-34: 4
```

The 11 test-screen hits are exactly pre-existing: AF-AP-80 at `T2:720-721` (`removal_line`), `T2:1038` (`DEBUG_LEVEL_CANARY`), `T2:1612-1613` (`_load_timeline_raw = s0_01._load_timeline_raw`), `T2:1645` (`_load_timeline_raw(leg_dir, leg)`), `T2:1668` (`os.environ`); AF-AP-34 at `T2:1676` (`pkill/killall/name match`) and `T2:1680` (`for word in ("pkill", "killall", "pgrep")`) (duplicated screen rows). None is within the B6/B7 hunks. `git diff --check` returned 0. No selected test skipped in the two direct xdist module runs.

## Item 8 — bounded hunk sweep and finding inventory

1. FOLLOW-UP — D scalar range failures are raw tracebacks. SOLID at `D:84-89` (`if len(key) != 64`), `D:194` (`nv.sign_event(privkey`), and consumer `nostr_verify.py:230-235`; canonical real CLI with `0`×64 and `f`×64 exits 1 before connection but emits traceback. No exact B6 range-contract mapping, so not blocker. Suggested fix: turn the consumer’s `ValueError("invalid private key")` into a named clean CLI refusal while retaining zero network action.

2. FOLLOW-UP — B6 normalization is only source-tested, not CLI-tested. SOLID: m4 causes whitespace/padded inputs to change actual CLI behavior while `test_cli_refuses...` and `test_cli_with...` remain green; only `T2:1823` (`strip().lower()`) source string detects it. Suggested fix: add whitespace-only and padded-valid rows to the B6 subprocess listener test.

3. FOLLOW-UP — B7 exact-values preflight test is a source mirror. SOLID: m5 accepts a scratch pins file containing only the commented exact values line; `T2:1735` (`grep -Fqx`) catches source text, but no behavioral test drives `S0_02_REPO=<scratch>` failed preflight. Suggested fix: scratch-only behavioral negative that asserts `rc=3`, BLOCKER text, and no DEST.

4. FOLLOW-UP — B7 preflight ordering is only source-tested. SOLID: m6 creates DEST before failing mutated pins; test fails only because its source extraction no longer sees the preflight at `T2:1731` (`exit 3`). Suggested fix: same behavioral negative asserts DEST absent.

5. CONTRACT-INVALID — B7 real-root rc-set requirement cannot be satisfied literally on the exact frozen path. SOLID at `T2:807-816` (`test_real_evidence_root_is_not_a_passing_bundle_today`): broadening the rc set survives all permitted failure states and is killed only by the separate `PASS:` assertion on success. The code is fail-closed; the criterion that this individual mutation red is unmeasurable without an approved isolated seam. No code repair is authorized.

6. INFO — current repository state differs from B7 author report’s partial-root observation. SOLID: current `proofs/S0-02/evidence` is absent and real checker exits 2. The historic partial capture is only in tracked diagnostic patch `tasks/briefs/pc/patch-pc-b7.md--c439580.diff`, not active proof input. No claim in the landed code is false.

No BLOCKER. No CONTRACT-DEFECT. No stale comment in the examined B6/B7 hunks contradicted their current behavior.

## DISCREPANCIES

- Brief says B7 checker output on the partial root was `neg-unauthorized leg directory absent`; current PIN lacks `proofs/S0-02/evidence`, so direct checker output is `deferred: S0-02 evidence not captured`, `rc=2`. The historic partial data is diagnostic patch content, not current input.
- The brief’s item-6 required the real-root rc-set `(1,2) → (0,1,2)` mutation to red. It survives every failure state the original assertion permits and, on success, reds only at independent `T2:812` (`PASS:`). This makes the literal individual-mutation requirement CONTRACT-INVALID; no test or checker was weakened.
- `graft` has no shell definitions indexed for R; GitNexus index is 439 commits stale and does not resolve `launch_leg`. This is tooling coverage, not a code claim.
- Terminal output rendered the authorization-row collection fragment as literal `***` (`b6-authorization: *** rc=1`). The scratch audit itself asserts collection `1/151`; no private key is printed. This safeguard-shaped artifact is reported verbatim.
- Final artifact lint: `report_lint: 85 refs — OK 85, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`; the bounded report-lint floor is met.
- Final tree hygiene: `git diff --name-only 22bd6f5` was empty; `git status --short` showed only the two untracked verifier-report copies; the three contract SHA-256 identities still match item 1.

## NOT-done

- No live S0-02 capture, proof mint, runner positive preflight/launch, or relay delivery. These are expressly out of scope and a positive preflight would launch the isolated harness.
- No behavioral B7 positive arm repeated; B7 report is cited only as predecessor evidence, not independently adopted.
- No production code, test, ledger, secret, or production artifact was changed; only the two untracked verifier-report copies were written.
- FOLLOW-UP issues 1–4 should be filed as `verify-followup` under D-034; they do not authorize an unbounded repair wave.
- Item 6 is CONTRACT-INVALID and requires coordinator contract amendment before a new verification round; no repair was attempted.

## GATE RECOMMENDATION

`CONTRACT-INVALID` — the frozen item-6 requirement that the individual real-root `rc-set` mutant `(1,2) → (0,1,2)` red is unmeasurable on the exact current checker path. It survives every original permitted failure state and is caught only by the separate `PASS:` assertion on success. Direct deterministic evidence otherwise verifies the premise, B6 real-CLI negative/positive network behavior, B6 behavioral m1/m2/m3 kills, B7 corrected-byte failed-preflight-before-DEST behavior, both full T2 xdist gates (151 passed twice), and static/screen gates. Coordinator must amend the criterion before re-verification; it owns the final decision. The three source-to-behavior test-strength follow-ups and scalar clean-error follow-up remain non-blocking.

Retro: observed AF-AP-80 pairings (source mirror without canonical behavioral negative) in m4/m5/m6. Coordinator should record these as follow-ups; no shared skill was changed by this lane.

Graft token savings this turn: approximately 39,695.
