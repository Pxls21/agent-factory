# VERIFY-B1 — adversarial grade of lane B1 (S0-02 Buzz authorization/freshness)

**PIN graded:** `088efef22b1eec2751166d5ffaabcffd8490b2b9`. All bytes read from a
`git archive 088efef` copy at `/tmp/.../scratchpad/vb1/`; every file:line below is at that PIN.
**Buzz source:** `/home/user/nerdherderdani/buzz` @ `1c8321cd08feb597f8bcff5195c21148fb3e98ed`
(re-derived by `git rev-parse HEAD`; matches `upstream.lock.yaml:18`). Read-only — every mutation
of it on a scratch copy at `scratchpad/buzzscratch/`.
**Venue:** sandbox, shared with other lanes' suites — **no timing claims anywhere in this report.**

## VERDICT: **NOT-READY** — 5 blocking findings, all small and local.

The machinery is genuinely good. The distinctness gate is real (I re-introduced both the AF-AP-63
tautology and the assert-then-count order and both died), the identity binding is tight (11 forgery
attempts, 11 caught), the freshness type-guard rejects the whole unusable class including NaN, and
every evidence read but one is S_ISREG-guarded — I could not make the checker hang. What fails is
narrower and sharper: **the report's headline discrepancy (D1/D2) is pinned by a source scan that
sees 3.6% of `lib.rs` and 10.8% of `relay.rs`, and a `verify_event` planted directly on the
channel-event path survives it green**; **the PC runner deletes the operator's `membership.json`
one line before it tests for it, so the revocation leg can never run**; and **the revocation
receipt's timestamp and channel are never read, so a removal recorded AFTER the rejected delivery
passes.** None of my verdict rests on anything I did not reproduce.

---

# FINDINGS (all, no severity filter)

## F1 — `_production_verify_sites` scans ~4-11% of each file; the D1/D2 headline gate is hollow. **BLOCKING. SOLID.**

**Where:** `tests/test_s0_02_buzz_authz.py:267`
```
cut = next((i for i, ln in enumerate(lines) if ln.strip() == "#[cfg(test)]"), len(lines))
```
**Expected** (the test's own docstring, `tests/test_s0_02_buzz_authz.py:279-280`): *"If a future
buzz-acp gains a verify on the channel-event path this test goes red, which is the point."*
**Observed:** it does not. Rust files in this tree carry **inline, mid-file** `#[cfg(test)]`
attributes, not just a trailing `mod tests`. Measured first-marker positions in the pinned tree:

| file | first `#[cfg(test)]` | total lines | scanned |
|---|---|---|---|
| `crates/buzz-acp/src/lib.rs` | 397 | 11013 | **3.6 %** |
| `crates/buzz-acp/src/relay.rs` | 736 | 6786 | **10.8 %** |
| `crates/buzz-acp/src/pool.rs` | 219 | 10639 | **2.1 %** |

The entire channel-event path lives beyond every cut: `record_event` relay.rs:1258, the duplicate
drop relay.rs:2387, the EVENT deserialise relay.rs:3775.

Whole-file verify sites in `buzz-acp/src`: `engram_fetch.rs:122, lib.rs:256, lib.rs:1574,
lib.rs:6082, pool.rs:3385, pool.rs:3495`. The derivation returns only `['engram_fetch.rs:122',
'lib.rs:256']`. **Three of the five entries in the test's `known` set
(`tests/test_s0_02_buzz_authz.py:282-288`) — `lib.rs:1574`, `pool.rs:3385`, `pool.rs:3495` — are
decorative: the derivation never produces them**, so `set(sites) - known` is empty by
under-collection, not by agreement.

**Failing input (reproduced):** on the scratch checkout, insert immediately after the pristine
`relay.rs:3779` (`)?;`, the close of the channel EVENT deserialise) — i.e. as the copy's new line 3780:
```rust
if buzz_core::verify_event(&event).is_err() { return; }
```
then `S0_02_BUZZ_SRC=<scratch> pytest tests/test_s0_02_buzz_authz.py -k no_signature_check`
→ **`1 passed`**. The mutant that adds exactly the check the test claims to detect **SURVIVES**.

**Also measured** (four plant forms, all inside the *scanned* prefix so the cut is not the confound):

| plant | result |
|---|---|
| (a) `verify_event` inside a `mod tests` placed BEFORE the marker | **falsely FLAGGED** (test goes red) |
| (b) helper `fn check(e) { buzz_core::verify_event(e) }` called on the channel path | detected |
| (c) `verify_event` inside a `/* */` block comment | **falsely FLAGGED** (test goes red) |
| (d) `use buzz_core::verify_event as v;` + `v(&event)` on the channel path | **MISSED** |

So the report's own statement of the limit (`B1-report.md:394-397`: *"a production verify call
placed inside a `mod tests` before that marker would be missed"*) is **backwards** — such a call is
falsely flagged, not missed — and it names the smallest of the three real limits.

**Substance check:** I independently scanned all `.rs` files whole and found no verify on the
channel path, so *the D1/D2 claim is TRUE*. It is the **gate** that is hollow, not the finding.

**Minimal fix** (`tests/test_s0_02_buzz_authz.py:255-273`): drop the prefix cut and exclude test
regions structurally instead — track brace depth from each `#[cfg(test)]` to the end of its block,
or (cheaper and sufficient) scan whole files and make `known` an exact-equality set:
```python
sites = _all_verify_sites()            # whole file, // lines dropped
assert set(sites) == KNOWN, f"verify sites changed: added {sorted(set(sites)-KNOWN)}, gone {sorted(KNOWN-set(sites))}"
```
with `KNOWN = {"engram_fetch.rs:122","lib.rs:256","lib.rs:1574","lib.rs:6082","pool.rs:3385","pool.rs:3495"}`.
Exact-equality also kills the decorative entries and catches the alias form only if the regex is
widened; add `"verify(" in line` or match `use .*verify_event` too.

**Exact red test:** `test_a_verify_on_the_channel_event_path_is_detected` — copy the pinned
`crates/buzz-acp/src/*.rs` to `tmp_path`, insert `if buzz_core::verify_event(&event).is_err() { return; }`
after `relay.rs:3779`, point `S0_02_BUZZ_SRC` at the copy, and assert
`test_buzz_acp_performs_no_signature_check_on_a_channel_event` raises. RED today.

---

## F2 — `run_s0_02_legs.sh` deletes the operator's `membership.json` one line before it tests for it: the revoked leg can NEVER run. **BLOCKING. SOLID.**

**Where:** `proofs/S0-02/tools/pc/run_s0_02_legs.sh:134-135` vs `:170`
```
134:  out=$DEST/$leg
135:  rm -rf "$out"
...
167:  <leg>/membership.json as {"removed":true,"removed_pubkey":"<hex>","channel":"<uuid>","at_epoch_s":N},
168:  then re-run this script with `revoked` as the only leg argument.
170:  [ -f "$out/membership.json" ] || { stop_leg; continue; }
```
**Expected:** the documented recovery — write `$DEST/revoked/membership.json`, re-run with
`revoked` — captures the leg. **Observed:** `rm -rf "$out"` at the top of every loop iteration
deletes `$DEST/revoked/` **including** the receipt the operator just wrote, so `:170` always tests
a path that cannot exist and the leg is skipped forever. Seed assertion 2 can never be captured by
this script as written.

**Failing input:** `mkdir -p $DEST/revoked && echo '{...}' > $DEST/revoked/membership.json &&
bash run_s0_02_legs.sh $DEST revoked` → prints the NOT-run message and `continue`s.

**Minimal fix:** take the receipt from outside `$out` and copy it in after the wipe:
```bash
MEMBERSHIP=${S0_02_MEMBERSHIP:-$DEST/revoked-membership.json}
...
revoked)
  [ -f "$MEMBERSHIP" ] || { cat >&2 <<'MSG' ... MSG
    stop_leg; continue; }
  mkdir -p "$out"; cp "$MEMBERSHIP" "$out/membership.json"
```
**Exact red test** (static, PC-free — the runner must not be executed in the sandbox):
```python
def test_revoked_membership_receipt_survives_the_leg_wipe():
    t = RUNNER.read_text()
    assert t.index('[ -f "$out/membership.json" ]') < t.index('rm -rf "$out"') \
        or "cp \"$MEMBERSHIP\"" in t, \
        'rm -rf "$out" deletes the operator receipt before the revoked arm tests for it'
```
RED today.

---

## F3 — the revoked leg's removal timestamp and channel are never read: a removal recorded AFTER the rejected delivery passes. **BLOCKING. SOLID.**

**Where:** `proofs/S0-02/check_buzz_authz.py:357-364` — the whole revoked block reads exactly two
keys, `removed_pubkey` and `removed`. `membership.json`'s `at_epoch_s` and `channel` (written by
the runner's own documented shape, `run_s0_02_legs.sh:167`, and present in the committed bundle at
`proofs/S0-02/fixtures/evidence-pass/legs/revoked/membership.json`) are never opened.

**Expected:** the leg proves *"membership removal revokes access"* (seed:372), which requires the
removal to precede the delivery and to concern this channel.
**Observed (all reproduced against `evidence-pass`, rc=0 PASS in every row):**

| mutation of `legs/revoked/membership.json` | expected | observed |
|---|---|---|
| `at_epoch_s: 1788999999` (removal ~200 000 s AFTER `t0=1788800000`) | FAIL | **PASS** |
| `at_epoch_s` deleted entirely | FAIL | **PASS** |
| `channel` set to `00000000-0000-0000-0000-000000000000` | FAIL | **PASS** |
| `channel` deleted entirely | FAIL | **PASS** |
| file reduced to `{"removed":true,"removed_pubkey":"<hex>"}` | FAIL | **PASS** |
| file replaced by a hand-written blob that never touched the relay | FAIL | **PASS** |

(`removed:"true"` and `removed:1` ARE rejected — `is not True` is strict. Good.)

**Deeper consequence for D5:** the ONLY thing separating `revoked` from `neg-unauthorized` is an
**unauthenticated, operator-authored JSON file**. Nothing binds it to the relay: no HTTP status, no
response body, no post-removal member list. D5 calls this "separated STRUCTURALLY"; the structure
is a file the operator types.

**Minimal fix** (`check_buzz_authz.py:357-364`, additive):
```python
at = membership.get("at_epoch_s")
if not isinstance(at, int) or isinstance(at, bool):
    raise Failure(f"{leg}: membership.json at_epoch_s is not an int")
if at >= t0:                       # t0 from t0.json, already read in _check_freshness
    raise Failure(f"{leg}: the removal is recorded at {at}, at or after the delivery t0 {t0} — "
                  f"this cannot prove removal revoked access")
h = [t[1] for t in delivered["tags"] if t and t[0] == "h"]
if membership.get("channel") not in h:
    raise Failure(f"{leg}: membership.json channel {membership.get('channel')!r} is not the "
                  f"delivered event's channel {h}")
if not str(membership.get("http_status", "")).startswith("2"):
    raise Failure(f"{leg}: membership.json records no successful relay removal response")
```
and have the coordinator record the relay's actual removal response into the file.
**Exact red test:** `test_revoked_leg_removal_must_precede_the_delivery` — copy the pass bundle,
set `at_epoch_s = t0 + 1`, assert `Failure` containing `"at or after the delivery"`. RED today.

---

## F4 — the real evidence root's `buzzacp.log` is still gitignored: AF-AP-62 recurs the moment the PC legs are committed. **BLOCKING. SOLID.**

**Where:** `.gitignore:10` `*.log`; `.gitignore:13` `!proofs/*/fixtures/**/*.log`.
The re-include covers only paths under `proofs/<id>/fixtures/`. The checker **requires**
`buzzacp.log` in every leg (`check_buzz_authz.py:255`, `:345`), and the real root is
`proofs/S0-02/evidence/<leg>/buzzacp.log` — **not** under `fixtures/`.

**Reproduced:**
```
$ git check-ignore -v proofs/S0-02/evidence/pos-allowed/buzzacp.log
.gitignore:10:*.log	proofs/S0-02/evidence/pos-allowed/buzzacp.log
$ git check-ignore -v proofs/S0-02/fixtures/evidence-pass/legs/pos-allowed/buzzacp.log
(not ignored)
```
S0-01's committed evidence carries **zero** `.log` files (I checked: `git ls-tree -r 088efef --
proofs/S0-01/evidence | grep -c '\.log$'` → 0), so S0-02 is the first proof whose real evidence
needs one and nothing has caught this yet. On capture, `git add proofs/S0-02/evidence` silently
drops 7 logs and the coordinator's git-view gate goes red exactly as it did on `68fb454`.

**Minimal fix:** add `!proofs/*/evidence/**/*.log` beside line 13.
**Exact red test:**
```python
def test_the_real_evidence_root_log_is_not_gitignored():
    r = subprocess.run(["git","check-ignore","-v","proofs/S0-02/evidence/pos-allowed/buzzacp.log"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode != 0, r.stdout
```
RED today.

---

## F5 — the replay leg's second sub-leg sits inside a 120 s tolerance behind a 100 s wait window. **BLOCKING (live legs). SOLID from source; not runnable here.**

**Where:** `check_buzz_authz.py:98` `LEG_CLOCK_TOLERANCE_S = 120` ·
`run_s0_02_legs.sh:34` `TURN_WAIT_S=${S0_02_TURN_WAIT_S:-100}` ·
`run_s0_02_legs.sh:141-147` · `deliver_event.py:167,180-183`.

The second sub-leg is delivered with `--reuse "$out/first/delivered-event.json"`, so its
`created_at` is the FIRST delivery's `t0`, while its own `t0.json` records a **fresh**
`$(date +%s)` (`run_s0_02_legs.sh:124`). Between the two `deliver` calls sit
`wait_turn_window 1` (up to **100 s**) and `collect_leg` (two `cp`s of the timeline and log).
`_check_freshness` (`check_buzz_authz.py:214`) then requires `abs(age - 0) <= 120`.

**Failing input:** any run where the first turn takes more than ~118 s to appear — including every
run where it never appears and `wait_turn_window` burns the full window — yields
`neg-replayed/second: delivered created_at is <N>s from t0, outside the 120s tolerance for offset 0`.
Margin today: **20 s.** Reproduced in the sandbox by setting the second sub-leg's `t0` 121 s past
its `created_at` → `rc=1`, that exact message.

**A second, opposite constraint on the same pair:** buzz-relay's NIP-98 auth is replay-guarded on
the **auth event id** (`crates/buzz-auth/src/nip98_replay.rs` `nip98_replay_key`,
`crates/buzz-auth/src/error.rs:36` `"NIP-98 replay: event id already seen within window"`), and
`deliver_event.py:87-92` signs the auth event over `int(time.time())` + the body hash. The replay
leg posts **byte-identical bodies**; if both `deliver` calls land in the same wall-clock second the
auth events are byte-identical, the second POST is refused as a NIP-98 replay, and the leg fails
with an auth message instead of buzz-acp's duplicate drop. `wait_turn_window` returns on its FIRST
poll if the turn already landed, so a same-second pair is reachable.

**Minimal fix (both at once):** in `run_s0_02_legs.sh`, `sleep 1` before the second `deliver` and
pass the FIRST sub-leg's `t0` to it (`--t0 "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["t0_epoch_s"])' "$out/first/t0.json")"`),
so the reused event's age is measured against the clock it was signed against.
**Exact red test:** `test_the_replay_window_fits_inside_the_leg_clock_tolerance`:
```python
turn_wait = int(re.search(r"TURN_WAIT_S=\$\{S0_02_TURN_WAIT_S:-(\d+)\}", RUNNER.read_text()).group(1))
assert checker.LEG_CLOCK_TOLERANCE_S > turn_wait + 30, (turn_wait, checker.LEG_CLOCK_TOLERANCE_S)
```
RED today (120 vs 130).

---

## F6 — the pasted `report_lint … MISS 0` does not hold at the PIN: one reference is wrong. **SOLID.**

`B1-report.md:276` cites `` `if set(env) != expected_keys:` proofs/S0-01/tools/pc/pc_launch.py:268``.
At **088efef** and at the lane's own PIN **2ff0c31** that line is `pc_launch.py:167`; `:268` reads
`open(os.path.join(FD, "launch.exited"), "w").write(utc_now() + "\n")`. In the current dirty
worktree it is `:255`. Wrong in all three views.

Reproduced with the lane's exact map set against the PIN bytes:
```
MISS  report:276  proofs/S0-01/tools/pc/pc_launch.py:268  cited line reads:
      'open(os.path.join(FD, "launch.exited"), "w").write(utc_now() + "\n")'; tokens ['if set(env) != expected_keys:']
report_lint: 141 refs — OK 120, NEAR 0, MISS 1, UNCHECKABLE 20, UNRESOLVED 0
```
(the lane pasted `141 refs — OK 121 … MISS 0`.)
**Minimal fix:** change `:268` → `:167` in the report. **Red test:** the `report_lint.py` command
in Item 0 of the VERIFY brief, `--rev 088efef`, exit 1 today.

---

## F7 — the report's "every one of those thirteen is also cited elsewhere on an OK line" is false for 5 of the 9 distinct references. **SOLID.**

**Where:** `B1-report.md:502-507`. I re-ran the linter and cross-referenced every UNCHECKABLE ref
against the OK set:

| reference | also OK elsewhere? |
|---|---|
| `crates/buzz-acp/src/relay.rs:1262` | yes |
| `crates/buzz-relay/src/handlers/ingest.rs:2224` | yes |
| `crates/buzz-relay/src/handlers/ingest.rs:770` | yes |
| `crates/buzz-relay/src/api/bridge.rs:966` | yes |
| `seeds/seed-stage0-v1.yaml:375-380` | **never OK anywhere** |
| `docs/03_INTEGRATION_CONTRACTS.md:22` | **never OK anywhere** |
| `scripts/validate-ledger:275` | **never OK anywhere** |
| `tests/test_s0_02_buzz_authz.py:94` | **never OK anywhere** |
| `tests/test_s0_02_buzz_authz.py:276` | **never OK anywhere** |
| `tests/test_s0_02_buzz_authz.py:296` | **never OK anywhere** |
| `tests/test_s0_02_buzz_authz.py:870` | **never OK anywhere** |

**However — I checked all seven by hand and every one is SUBSTANTIVELY CORRECT**
(seed:376-380 = the four fixtures + `rule: four DISTINCT reasons required`;
docs/03:22 = *"Unauthorized, invalid, replayed, stale, and self-authored events produce none."*;
validate-ledger:275 = the `# Bind the recorded runs to the ATTESTED spec` comment heading the
cmd binding; tests:94 = `pytest.skip(`; :276/:296 = the two named tests; :870 = the AF-AP-34
docstring). So this is a false claim in the evidence audit, not a wrong pointer.
**Minimal fix:** replace the sentence with the true one — *"four of the nine are also cited on an
OK line; the other five were verified by hand and are listed with their content."*

---

## F8 — `test_relay_drift_window_matches_the_checker_constant` is a substring anchor on an outcome-classifying number: a 10× upstream change stays green. **SOLID.**

**Where:** `tests/test_s0_02_buzz_authz.py:311-314`
```python
line = src.read_text().splitlines()[2223]
assert f"MAX_TIMESTAMP_DRIFT_SECS: i64 = {checker.RELAY_DRIFT_WINDOW_S}" in line, line
```
The pinned line is `const MAX_TIMESTAMP_DRIFT_SECS: i64 = 900; // ±15 minutes`.
**Failing input:** upstream changes it to `= 9000`. `"…= 900" in "…= 9000; // …"` is **True** →
test green, `RELAY_DRIFT_WINDOW_S` wrong by 10×, and every stale-window judgement
(`check_buzz_authz.py:208`, `:219`) and the fixture-offset floor (`tests:165`) inherit the error.
This is class 5 (substring anchors), which the lane's sweep rated **SAFE** — it is not.
**Minimal fix:**
```python
m = re.search(r"MAX_TIMESTAMP_DRIFT_SECS: i64 = (\d+)\s*;", line)
assert m and int(m.group(1)) == checker.RELAY_DRIFT_WINDOW_S, line
```
**Exact red test:** point `S0_02_BUZZ_SRC` at a scratch checkout whose `ingest.rs:2224` reads
`= 9000` and assert the test fails. Green today.

*Positive note on the same chain:* the stale offset IS pinned relationally —
`tests:165` asserts `abs(offset) > checker.RELAY_DRIFT_WINDOW_S`, so `-86400` is not a bare
literal pinned by another bare literal. Only the source→constant link is weak.

---

## F9 — the DEBUG canary is a level-blind substring; it cannot establish what its own error message claims. **SOLID.**

**Where:** `check_buzz_authz.py:102` `DEBUG_LEVEL_CANARY = "startup watermark set to"`;
`:258-263` `if DEBUG_LEVEL_CANARY not in log_text: raise Failure(… "the leg was not captured at RUST_LOG=debug" …)`.
**Failing input (reproduced, rc=0 PASS):** replace the log's canary line with
`2026-09-08T00:00:00Z  INFO buzz_acp::relay: startup watermark set to 1788800000`.
The check passes, so the leg is treated as debug-captured while the log is INFO.
`test_debug_canary_line_exists_in_the_pinned_source` (tests:317-322) pins that the *source* emits
it via `debug!(`, which is good defence — but the *captured log* is never checked for a level.
**Minimal fix:** require the canary on a line carrying a DEBUG level token:
```python
if not any(re.search(r"\bDEBUG\b.*" + re.escape(DEBUG_LEVEL_CANARY), ln) for ln in log_text.splitlines()):
```
**Exact red test:** `test_a_canary_emitted_at_INFO_does_not_satisfy_the_debug_claim`. RED after the fix, green today.

### F9b — the canary blocks **all five** negative legs, not two. **SOLID, and it corrects NOT_DONE 3.**
`_observe_all` (`check_buzz_authz.py:245`) runs for **every** negative leg, and it raises on the
missing canary at `:258` *before* it scans the delivery message. The real S0-01 corpus log
(`/root/s0-01-realleg/golden/run-1/buzzacp.log`) contains **zero** occurrences of
`startup watermark set to` (verified: `grep -c` → 0). So with the S0-01 launcher's pinned env, the
three RELAY-decided legs and the revoked leg will *capture fine and then fail the checker* on the
canary, while the runner refuses only the two buzz-acp-decided legs (exit 3,
`run_s0_02_legs.sh:51-62`). Reproduced: removing the canary from `neg-unauthorized`'s log →
`failure_reason: neg-unauthorized: buzzacp.log lacks the debug-level canary`.
**Consequence for the coordinator:** the RUST_LOG seam blocks **6 of 7 legs**, not 2. The report's
NOT_DONE 3 understates the blast radius.
**Minimal fix:** demand the canary only for legs whose oracle row says `evidence == EV_BUZZACP_LOG`;
relay-decided legs need no buzz-acp log evidence at all.

---

## F10 — channel confusion is undetected: an observable planted in the wrong channel passes. **SOLID.**

**Where:** `check_buzz_authz.py:264-269` scans BOTH channels for ALL observables (correct, and
necessary for collapse detection) and `_check_named_observable` (`:283-292`) only asserts the
leg's own key is *present*. Nothing rejects an observable appearing where it cannot be produced.

Reproduced (both rc=0 PASS on `evidence-pass`):
* relay-only text `restricted: not a channel member` appended to `neg-unauthorized/buzzacp.log` —
  a physically impossible artefact (buzz-acp never sees a relay-rejected event);
* buzz-acp-only text `dropping duplicate event for channel` inserted into `neg-stale`'s
  `delivery.json` message.

**Related, same site:** a single leg carrying TWO oracle observables passes and *both* enter its
distinctness key (`_observed_key`, `:278-280`), so distinct **noise** makes keys more distinct.
A blanket rejection dressed with per-leg noise therefore stops being classified as
`blanket-rejection:` and degrades to a per-leg named-observable failure (still exit 1). I tried to
launder the committed blanket bundle this way and it **failed anyway** — on the `accepted`
cross-check (`:293-304`), which demands `accepted is True` for buzz-acp-decided legs. **That
cross-check is the thing that makes the laundering impossible; it earns its place.**

**Minimal fix:** after the distinctness compare, reject wrong-channel observables:
```python
for chan_text in found:
    chan, text = chan_text.split("::", 1)
    owner = next(r for r in oracle.ROWS if r["observable"] == text and r["leg"] == "negative")
    if chan != owner["evidence"]:
        raise Failure(f"{leg}: {text!r} appears in the {chan} channel, but {owner['fixture']}'s "
                      f"observable can only be produced in {owner['evidence']}")
```
(`revoked` and `neg-unauthorized` share a text and a channel, so pick by `evidence`, not fixture.)
**Exact red test:** `test_a_relay_observable_in_the_buzz_acp_log_fails_the_leg`. RED after fix.

---

## F11 — the evidence root has no closure check: extra or garbage leg directories are ignored. **SOLID.**

**Where:** `check_buzz_authz.py:104` `LEG_NAMES = ("pos-allowed",) + oracle.NEGATIVE_FIXTURES` —
a closed tuple. `check_bundle` (`:445`) iterates it; nothing enumerates the root.

Reproduced (both rc=0 PASS):
* copying `neg-stale/` to a sixth leg directory `neg-brand-new/`;
* creating `neg-forged/` containing only `fixture.json` with the bytes `not json`.

Answer to the brief's question — the gate requires **exactly the six named legs**; extra evidence
is not considered at all, so a stale leg from a previous capture, or a leg the runner produced that
the checker does not know about, is silently invisible.
**Minimal fix:**
```python
expected = set(LEG_NAMES)
actual = {p.name for p in root.iterdir() if p.is_dir()}
if actual - expected:
    raise Failure(f"bundle: unexpected leg directories {sorted(actual - expected)}")
```
**Exact red test:** `test_an_unknown_leg_directory_fails_the_bundle`. RED after fix.

---

## F12 — the stale branch of `_check_freshness` is one-sided: a t0 far in the future reads as "more stale". **SOLID.**

**Where:** `check_buzz_authz.py:206-212`
```python
if offset < 0:
    if age < RELAY_DRIFT_WINDOW_S:
        raise Failure(... "it is not stale")
```
No upper bound, and no check that the age matches the fixture's declared offset (the fresh branch
at `:214` does exactly that).
**Failing input (reproduced, rc=0 PASS):** `legs/neg-stale/t0.json` → `{"t0_epoch_s": 9999999999}`
(year 2286). Age becomes ~8.2×10⁹ s and the leg reads as a stronger stale proof.
**Minimal fix:** mirror the fresh branch —
```python
if abs(age - (-offset)) > LEG_CLOCK_TOLERANCE_S:
    raise Failure(f"{leg}: delivered created_at is {age}s from t0, outside the "
                  f"{LEG_CLOCK_TOLERANCE_S}s tolerance for offset {offset}")
if age <= RELAY_DRIFT_WINDOW_S:
    raise Failure(... "it is not stale")
```
**Exact red test:** `test_a_stale_leg_with_an_absurd_t0_fails`. RED after fix.

*Everything else in this guard is strong and I could not break it:* `t0_epoch_s` missing, a string,
`True`, a float, and **NaN** are all rejected cleanly by `isinstance(t0, int) and not bool`
(`:202-203`) — the whole unusable class, not a bare `<= 0`.

### F12b — off-by-one against the pinned relay comparison. **SOLID, low.**
`crates/buzz-relay/src/handlers/ingest.rs:2227` is `if (event_ts - now).abs() > MAX_TIMESTAMP_DRIFT_SECS`
— **strictly greater**, so an event exactly 900 s adrift is **accepted** by the relay. The checker
calls `age == 900` stale (reproduced: age 899 → red "it is not stale"; age **900 → PASS**) and
fails a *fresh* leg at exactly 900 (`:219` `>=`). Fix: `if age <= RELAY_DRIFT_WINDOW_S` in the
stale branch (folded into F12's fix above). Never bites at the committed `-86400` offset.

### F12c — `check_buzz_authz.py:219-223` is dead code for every committed fixture. **SOLID, low.**
For `offset >= 0`, `abs(age) >= 900` is reachable only when `offset >= 780`; every fixture's offset
is `0` except `neg-stale`'s `-86400` (`build_fixtures.py:94,102,110,122,134,142,150`). The test that
claims to cover it, `test_a_fresh_leg_delivered_outside_the_window_fails` (tests:714-719), uses
`t0 - 5000` and therefore trips the **120 s tolerance** arm; its assertion string `"outside the"`
matches BOTH messages, so it cannot tell them apart. An emitted-but-unreachable check.
**Fix:** assert the distinguishing half of the message (`"120s tolerance"`), and either delete
the 900 arm or give a fixture a positive offset that reaches it.

---

## F13 — one evidence read bypasses `_require_file`; the lane's class-2 verdict says none does. **SOLID, low.**

**Where:** `check_buzz_authz.py:351` `log_text = (leg_dir / "buzzacp.log").read_text()`.
AST enumeration of every read in the checker (the oracle does no I/O at all):

| line | call | guarded? |
|---|---|---|
| 111 | `json.loads(path.read_text())` | yes — `_require_file` at :109 |
| 256 | `log_path.read_text()` | yes — `_require_file` at :255 |
| 346 | `log_path.read_text()` | yes — `_require_file` at :345 |
| **351** | `(leg_dir / "buzzacp.log").read_text()` | **NO** |
| 426, 429 | `.exists()` | deferral gate only; the read behind it is guarded |
| 436 | `root.is_dir()` | n/a |
| 442 | `.read_text()` | yes — `_require_file` |

Not exploitable today (`_observe_all` already guarded the same path at `:255`), so it is a TOCTOU
and a latent regression if `_observe_all` is ever made conditional. The lane's sweep class 2 states
*"Every evidence read goes through the imported S0-01 `_require_file`"* — false for `:351`.
**Fix:** `log_text = _require_file(leg_dir / "buzzacp.log", leg, "buzzacp.log").read_text()`.

**No hang exists today.** I planted FIFOs at `membership.json`, the synthetic `identities.json`,
a committed fixture, `buzzacp.log`, `delivered-event.json`, the evidence root and the
`--synthetic-root` directory, each under `timeout -s KILL 25`. Every one returned a named failure
in well under the cap (`… is not a regular file`); none produced `rc=137`. `membership.json` is
guarded even though it is **not** in the FIFO test's six-way parametrisation
(`tests:797-798` names `timeline.jsonl, delivery.json, buzzacp.log, fixture.json,
delivered-event.json, t0.json`) — add it as a seventh id.

### F13b — still no wall-clock cap (NOT_DONE 8 confirmed), and the fix is one line.
`check_buzz_authz.py` imports six names from S0-01 but not `_check_with_timeout`, which sits
directly above S0-01's own `check_bundle` and already handles the AF-AP-58 handler-leak ordering.
**Fix:**
```python
_check_with_timeout = s0_01._check_with_timeout
...
def main(argv):
    ...
    print(_check_with_timeout(90, check_bundle, root, anchors))
```

---

## F14 — the synthetic bundles model a DIFFERENT producer than the one that will make the real legs. **SOLID.**

`B1-report.md:396` claims *"`delivery.json` mirrors the real `/events` response"*. Measured:

| source | keys |
|---|---|
| committed bundles (`build_fixtures.py:359`) | `accepted, event_id, mention_pubkeys, message` |
| the lane's own producer (`deliver_event.py:117`) | `http_status, event_id, accepted, message` |
| the real S0-01 receipt `/root/s0-01-realleg/golden/run-1/mentions/owner.receipt.json` | `accepted, event_id, mention_pubkeys, message` |

The bundles mirror the S0-01 **mention** receipt, not what `deliver_event.py` writes. They carry
`mention_pubkeys` (which `deliver_event.py` never emits) and lack `http_status` (which it always
emits). The checker reads only the intersection, so both shapes pass — but **the committed evidence
never exercises the shape the real legs will carry**, which is precisely the AF-AP-42 residue S2
claims to have bounded.

**And `http_status` is recorded and never graded.** That matters because
`crates/buzz-relay/src/api/bridge.rs:985` returns `api_error(StatusCode::BAD_REQUEST, &msg)` for
every rejected event — so all four relay-decided legs come back **HTTP 400 with `{"error": msg}`**
(`crates/buzz-relay/src/api/mod.rs:22`), **not** the 200 `{"event_id","accepted","message"}` shape
at bridge.rs:964-968 that the bundles model. Two consequences:
1. `_normalise` (`deliver_event.py:117`) defaults `accepted: False` and only *then* looks for keys.
   For a 400 the relay never echoes `event_id`, so `receipt["event_id"]` stays the **locally
   computed** id — which makes `_check_delivery`'s equality (`check_buzz_authz.py:230`) a tautology
   on exactly the legs it matters for.
2. A transport failure that yields a non-JSON body is normalised to `accepted: false` with the raw
   body as `message` — indistinguishable in shape from a genuine rejection.

**Minimal fix:** grade `http_status` — `_check_delivery` should require `200` for accepted legs and
`400` for relay-decided ones, and `_normalise` should record `event_id_echoed: bool` so the checker
can say whether the relay confirmed the id. Rebuild the bundles from `_normalise`'s own shape
(import it in `build_fixtures.py`) so the fixture and the producer cannot drift.
**Exact red test:** `test_bundle_delivery_receipts_have_the_shape_deliver_event_writes`:
```python
assert set(json.loads(leg_delivery.read_text())) == {"http_status","event_id","accepted","message"}
```
RED today.

---

## F15 — three file:line claims inside the oracle's prose are wrong at the pinned commit, and no test pins them. **SOLID.**

`test_oracle_row_line_still_carries_its_pattern` (tests:233-245) pins only `src`/`line`/
`src_pattern`. The `discrepancy` and `note` strings carry their own references and nothing checks them.

| `proofs/S0-02/oracle/denial_table.py` | claim | at 1c8321cd |
|---|---|---|
| `:86` | *"ingest.rs:2242 rejects an event whose pubkey does not match the authenticated identity"* | :2242 is `let is_gift_wrap = kind_u32 == KIND_GIFT_WRAP;`. The check is **:2243**, the message **:2245**. The row's own `src`/`line` field is correct; only the prose is wrong. Also unstated: the check is `if event.pubkey != *auth.pubkey() && !is_gift_wrap` — **gift-wrap kinds are exempt** (irrelevant for kind 9, but the claim is absolute as written). |
| `:229` | *"`membership_dropped_since` (relay.rs:1176) tracks BACKPRESSURE drops"* | :1176 is a doc-comment line describing a **different** field (`subscribe_since`). `membership_dropped_since` is declared at **relay.rs:1150**. The backpressure claim itself is right (relay.rs:2329-2330). |
| `:226` | *"buzz-acp's own membership handling (lib.rs:3209, 'membership notification: unsubscribing from channel')"* | the quoted string is at **:3210**; :3209 is `subscribed_channel_ids.remove(&ch);`. |
| `:108-109` | *"Every **verify_event** call in the crate…: lib.rs:1574, lib.rs:256, engram_fetch.rs:122, pool.rs:3385, pool.rs:3495"* | four of the five are `event.verify()` method calls, not `buzz_core::verify_event(...)`. The *derivation* matches both, so the sites are right; the prose names the wrong API. |

**Minimal fix:** correct the four strings, and extend `test_oracle_row_line_still_carries_its_pattern`
to also lint every `file.rs:NNN` appearing inside `discrepancy`/`note`.
**Exact red test:** a parametrised `test_oracle_prose_references_resolve` that regex-extracts every
`\w+\.rs:(\d+)` from each row's prose and asserts the cited line contains the adjacent quoted token.
RED today on three rows.

*Everything the test DOES pin, I reproduced by `sed -n` on the pinned checkout: **all 20 rows of the
report's source table are OK**, and so are all five `src_pattern`s in the oracle module.*

---

## F16 — `required_negative_controls: 4` binds nothing. **SOLID.** (Direct answer to the brief's D4 question.)

`proofs/registry.yaml:13` records `"required_negative_controls": 4` for S0-02.
`scripts/validate-ledger:192-196` validates it only as *"an integer >= 1"*; `:251-252` requires
merely that at least ONE recorded run leg be named `negative`. `proofs/S0-02/spec.json` has two
legs (one positive, one negative) — the same shape as S0-01 (`required_negative_controls: 1`) and
S0-07. **A minted S0-02 artifact with a single negative leg will validate as `PRESENT`.**
So the seed's "four DISTINCT reasons" rule is enforced **only** inside the checker's distinctness
gate, never by the ledger. The report's D4 cites the registry field as if it bound; it does not,
and never did.
**Minimal fix (validate-ledger, not this lane):** count negative legs in the spec and require
`>= required_negative_controls`, or drop the field. **Red test:**
`test_spec_negative_leg_count_meets_the_registry_floor`. RED today for S0-02.

---

## F17 — `created_at` reaches the inbound filter-rule engine, so D8's absolute claim is too strong. **SOLID.**

D8 states *"Nothing in buzz-acp treats a sender's `created_at` as an authorization input"* and D3
says the subscription floor is the only `created_at`-driven inbound behaviour. I classified all 71
`created_at` occurrences in `crates/buzz-acp/src`:

| class | sites |
|---|---|
| subscription floor / `last_seen` state | relay.rs:1141, 1267, 2342 |
| membership-notification bookkeeping (incl. backpressure) | relay.rs:2302, 2319-2320, 2329-2330; lib.rs:3143 |
| **per-event REJECTION — observer CONTROL frames only** | lib.rs:1591-1592 (`OBSERVER_CONTROL_FRESHNESS_SECS`) |
| outbound: HTTP query paging cursor (`filter["until"]`) | relay.rs:534-543 |
| outbound: project-owner announcement signing (rejects >300 s future) | lib.rs:1643, 1731-1732, 1737 |
| batch ordering / prompt formatting | queue.rs:466, 1301-1303 |
| **exposed to the inbound RULE ENGINE as `timestamp`** | **filter.rs:37, 48, 259, 330 → lib.rs:600** |

`FilterContext.timestamp = event.created_at.as_secs()` (filter.rs:48), documented as a rule
variable (filter.rs:259) and bound into the evalexpr context at filter.rs:330; `filter::match_event`
is called from `AuthorizedNormalListenerEvent::match_subscription` (lib.rs:594-606) on the inbound
path, and a `None` result drops the event. **A configured subscription rule can therefore gate
inbound events on the sender's `created_at`.** Default config presumably does not — but the
premortem row 9 verdict ("comes out clean") should be stated as *"no default rule does; the
capability exists and is config-reachable"*.
**Minimal fix:** add a row to the oracle/D8 naming filter.rs:330, and a test asserting the shipped
`respond_to`/rule config contains no `timestamp` reference.

---

## F18 — the freshness discrepancy is pinned only as "no CONSTANT", while D3 claims "no RULE". **SOLID, medium.**

`test_buzz_acp_has_no_per_event_freshness_constant_for_channel_events` (tests:296-308) scans whole
files (good) but only for `const … FRESHNESS|MAX_AGE|STALE`. Reproduced:
* **M-C** — inserting `const CHANNEL_EVENT_FRESHNESS_SECS: i64 = 600;` into the scratch copy (as its
  new line 31) → **KILLED** (`1 failed`).
* **M-B** — adding an inline rule on the channel path with no constant,
  `if now.saturating_sub(event.created_at.as_u64()) > 600 { return Err(RelayError::Stale); }`
  inserted into the scratch copy after the pristine `relay.rs:3779` (`)?;`) → **SURVIVES** (`2 passed`).

The oracle's neg-stale `discrepancy` (`denial_table.py:154-167`) says *"NO per-event freshness
**rule** … exists"*; the gate proves only *no per-event freshness **constant** exists*.
**Minimal fix:** add a second assertion that no line in the channel-event region compares
`created_at` to a wall clock — or soften the oracle prose to "no per-event freshness constant".
**Exact red test:** the M-B plant above.

---

## F19 — the positive-turn nonce check is a plain substring over the whole params blob. **Low / by design, flagged.**

`check_buzz_authz.py:342-344` — `nonce not in _prompt_text(prompts[0])`, where `_prompt_text`
(`:131-134`) is `json.dumps(frame["params"], sort_keys=True)`.
**Failing input (reproduced, rc=0 PASS):** the prompt text becomes
`XX<nonce>YY`. The docstring at `:132-133` calls the tolerance deliberate (the nonce must be found
whichever content block carries it), and buzz-acp genuinely frames the prompt with surrounding
text, so a substring is the right shape. Naming it because the check therefore cannot distinguish
"the agent got THIS event's text" from "the agent got a superset containing it".
**If tightened:** require the nonce to sit on a JSON string boundary
(`f'"{nonce}"' in blob or re.search(rf'(?<![\w-]){re.escape(nonce)}(?![\w-])', blob)`).

---

## F20 — the 64-hex masking check false-reds on any non-pubkey digest. **Low.**

`check_buzz_authz.py:137-139` reuses S0-01's `_HEX64_ANYWHERE_RE = re.compile(r"[0-9a-fA-F]{64}")`.
**Failing input (reproduced, rc=1):** appending `config sha256=<64 hex>` to a leg's `buzzacp.log`
fails the leg with `contains unmasked 64-hex string`. A 63-hex near miss correctly passes.
The real corpus log carries **zero** 64-hex strings and masks the pubkey as `pubkey=<HEX>`
(verified in `/root/s0-01-realleg/golden/run-1/buzzacp.log`), so this does not bite today — but a
future buzz-acp that logs a config digest turns every leg red for the wrong reason. Inherited from
S0-01; recorded, not charged to this lane.

---

## F21 — the known-identity exclusion is a denylist over an evolving file. **Low.**

`check_buzz_authz.py:180` — `known = {v for k, v in identities.items() if k != "relay_url"}`.
The bundle's `identities.json` also carries `channel` (a UUID), which therefore lands in the pubkey
set. Harmless today; a new non-pubkey field in `identities.json` silently joins the "known
identities" the nonmember sender is compared against.
**Fix:** select positively — `{identities[k] for k in ("owner","agent","relay","user2") if k in identities}`.

---

## F22 — `test_pinned_tree_is_the_locked_commit` errors rather than asserting when the src is not a git repo. **Low.**

`tests:226-230` runs `git rev-parse HEAD` with `check=True`. Pointing `S0_02_BUZZ_SRC` at a plain
directory raises `CalledProcessError` (reproduced). **This is the right outcome for the PC
question in Item 10 — it FAILS, it never skips** — but the message is a traceback rather than a
named reason. Fix: `check=False` plus
`assert head.returncode == 0, f"{src} is not a git checkout"`.

---

# THE PC GATE (Item 14) — agreed

The one sanctioned bridge action, from a clean detached worktree of the PIN:
```
git worktree add -q --detach <tmp> 088efef && cp .pc-bridge.env <tmp>/
bash scripts/pc_suite.sh launch -n 8 -- tests/test_s0_02_buzz_authz.py
pc_suite: launched 20260908T043822Z-088efef on the PC — base 088efef22b1eec2751166d5ffaabcffd8490b2b9
          + patch 0B (sha e3b0c44298fc), set 'tests/test_s0_02_buzz_authz.py', -n 8
bash scripts/pc_suite.sh wait 20260908T043822Z-088efef
pytest-exit: 0
pytest-summary: 92 passed in 11.01s
```
Worktree removed (`git worktree remove --force`; `git worktree list` back to one entry).
The lane pasted `92 passed in 10.69s` on `20260908T035113Z-68fb454`. **I agree** — same count, same
exit, on the PIN with a zero-byte patch.

Sandbox baseline on the PIN copy, my own run: `92 passed`, `pytest-exit: 0`.

---

# WHAT THE LANE GOT RIGHT (reproduced, not taken on trust)

* **All 20 rows** of the report's source table reproduce by `sed -n` on the pinned checkout, and so
  do all five oracle `src_pattern`s and the `silent_drop_secondary` row.
* **The distinctness gate is real.** Re-introducing the AF-AP-63 tautology (`_observe_all` returns
  the oracle's own key) → **14 tests fail**. Re-introducing assert-then-count (named check moved
  before the distinctness compare) → **2 tests fail**
  (`test_blanket_bundle_is_a_blanket_rejection`, `test_spec_negative_leg_reason_is_the_exact_observed_line`).
  Trailing-period collapse → correctly reported as 5 legs → 4 observables. Blanket with one leg
  repaired → correctly reported as 5 legs → 2 observables, both keys named.
* **The identity binding held against 11 forgeries:** reordered tags, an extra tag, trailing
  whitespace in content, a different channel UUID in the `h` tag, a re-signed event, a tampered
  event with the id correctly recomputed (caught by the signature, `nv.event_id` IS recomputed at
  `:149`), the specimen key delivered on the owner leg **and** on the nonmember leg (the dedicated
  specimen check at `:185-189` is reachable and fires), cross-bundle anchors, real anchors on
  synthetic legs, and `--synthetic-root` in any position but first (`rc=64`). The parameter is
  genuinely closed and the anchors are bound to the bundle by fixture equality.
* **The replay leg:** a second turn, neither turning, two different ids with the correct sender, a
  symlinked and a hardlinked timeline — all caught. **A relay-side dedup (`accepted:false`) is
  correctly REJECTED as the replay proof** (`:300-304` demands the relay accepted the duplicate so
  buzz-acp is the decider). That is the right answer to the brief's question.
* **The positive leg:** nonce in a `session/cancel`, two prompts, two `session/new`, a receipt for
  a different id — all caught (WRONG-EVENT-ID-ACCEPTED reproduced).
* **`t0` hostile inputs:** missing, string, `True`, float, **NaN** — all rejected by name.
* **The signature IS deterministic by construction, not by luck** (Item 12): `sign_event` uses a
  fixed aux — `proofs/S0-01/tools/nostr_verify.py:251` `aux = b"\x00" * 32`, documented at `:225`
  *"Deterministic aux = 32 zero bytes"*. BIP-340 with fixed aux makes the signature a pure function
  of (seckey, msg), so `--check` byte-identity is structural.
* **AF-AP-40 ×2 classified by RUN, reproducing the lane's claim exactly:** every timeline deleted →
  `rc=2 deferred`; one timeline restored → `rc=1 neg-unauthorized: timeline.jsonl absent`; a single
  timeline deleted → `rc=1`; a whole leg dir deleted → `rc=1 leg directory absent`. A deferral can
  only withhold a verdict. The AF-AP-40 ×1 in `build_fixtures.py:394` is a builder rmtree guard, not
  a decision path — agreed.
* **`ap_screen` reproduces byte-for-byte:** `7 hits over 4 files — AF-AP-40: 3, AP-32: 3, AP-1: 1`;
  `--tests` → `AF-AP-34: 4` at `:870`, `:874` — all four on the enforcing test itself. Agreed.
* **The 16 `buzzacp.log` files are in the git view at the PIN** (`git ls-tree -r 088efef --
  proofs/S0-02 | grep -c buzzacp.log` → 16) **and in `git archive`** (16 on disk). The AF-AP-62
  re-include holds for the bundles. (It does not hold for the real evidence root — F4.)
* **Declared-input matrix A/B/C reproduced verbatim**: unset+no venue → declared skip at
  `tests:94`; venue set + default present → passes; declared-but-absent → **fails** at `tests:100`.
  Plus arm D (present but not the pinned commit) → fails, never skips.
* **`pc_launch.py:103` `shutil.rmtree(FD, ignore_errors=True)`** wipes the frame dir at every
  launch, so my two suspicions about the runner — stale `buzz-acp.exit` aborting leg 2, and
  cross-leg timeline contamination — are **unfounded**. I checked the mechanism rather than
  assuming it. Likewise the runner's `grep -c '"method":"session/prompt"'` (no space) **matches**
  the real tee's compact JSON (`/root/s0-01-realleg/golden/run-1/timeline.jsonl`) — 1 match; the
  spaced variant matches 0.
* **AF-AP-39 respected in `deliver_event.py`:** the key is read once from the environment
  (`:71-80`), threaded explicitly, never in argv; `--secret` carries only the file *name* into
  `t0.json` (`:182`). `_nip98_header` (`:83-94`) builds the `u`/`method`/`payload` tags the relay
  actually checks (`crates/buzz-auth/src/nip98.rs:19-23`); there is **no `expiration` tag** and none
  is needed — the relay enforces `TIMESTAMP_TOLERANCE_SECS = 60` on the auth event's `created_at`
  (`nip98.rs:32,77-83`).
* **AF-AP-34 respected:** `stop_leg` (`run_s0_02_legs.sh:81-93`) kills only the pid in its own
  pidfile after `readlink /proc/$pid/exe` matches `*buzz-acp*`, and refuses otherwise (`:89`). No
  `pkill`/`killall`/`pgrep` anywhere in the executable lines.
* **`wait_turn_window` is failure-aware** (`:102` returns 6 on `buzz-acp.exit`), and under `set -e`
  that aborts the run rather than reading a dead harness as "no turn, as expected".
* **`collect_leg` refuses an unmasked log** (`:114-117`) — a second, independent masking gate
  before the checker's.

**External command census of `run_s0_02_legs.sh`** (the lane brief required it; **the report does
not contain one — see F23 below**): `setsid`, `readlink`, `kill`, `grep` ×3, `cat` ×3, `cp` ×2,
`rm` ×4, `mkdir` ×2, `find`, `sort`, `sleep` ×3, `seq` ×2, `date`, `tail` ×2, `echo` ×11, and
`/usr/bin/python3` in three roles (the S0-01 launcher, `deliver_event.py`, and the one-liner in
`role_for`), plus the sourced `. "$SEC/$role.env"`. `deliver_event.py` spawns **no** subprocess at
all; its only external effect is `urllib.request.urlopen` to `<relay-http>/events` (`:174-175`).

## F23 — the required external-command list is missing from the report. **Low.**
Lane brief §5: *"every external call listed in the report"*. `B1-report.md` has no such list
(grep for `setsid|readlink|/usr/bin/python3|external command` finds only unrelated prose at :44,
:227, :230, :367). Fix: paste the census above into the report.

---

# MUTANT / ATTACK LEDGER — 60 runs (lane's 24 reviewed + 36 of mine executed)

Every one on a scratch copy; every pytest with an explicit `--basetemp` under my scratch dir;
`git status` on the shared tree untouched throughout.

**Survivors (green when they should be red) — 12:**
M-A channel-path `verify_event` · M-B inline freshness rule · plant (d) `use … as v` alias ·
two observables on one leg · relay text in `buzzacp.log` · buzz-acp text in `delivery.json` ·
sixth leg directory · garbage leg directory · `t0` in the far future on the stale leg ·
`age == 900` on the stale leg · removal `at_epoch_s` after the delivery (and deleted, and wrong
channel, and channel deleted, and a hand-written receipt) · nonce as a substring of a longer token ·
canary present at INFO.

**Killed / caught — 44**, including: the AF-AP-63 tautology (14 tests), the assert-then-count
reorder (2 tests), the freshness-const plant, trailing-period collapse, case-changed observable,
blanket-with-one-repaired, the laundered blanket (killed by the `accepted` cross-check), all five
`t0` type mutations, `p121` tolerance, the eleven identity forgeries, five replay mutations, four
positive-leg mutations, WRONG-EVENT-ID, 64-hex masking on two legs, canary removal,
`ignore_self=false`, `removed:"true"`, `removed:1`, a stale revoked event, and seven FIFO plants.

**False reds — 3:** plant (a) test-module verify, plant (c) block-comment verify, a non-pubkey
64-hex digest in the log.

**Not re-run:** the lane's FIFO-HANG mutant (it dies by blocking; the lane's `rc=137` is the honest
record and I saw no reason to burn a 90 s SIGKILL to reproduce a hang I can reason about from
`_require_file`'s `lstat`/`S_ISREG` at `check_acp_conformance.py:198`).

---

# ITEM-BY-ITEM: REPRODUCED / REVIEWED / SKIPPED

**Reproduced (ran it myself):** Item 0 (report_lint at the PIN in two modes + the 13-claim audit;
ap_screen prod and --tests; the 16-log git-view and archive count) · Item 1 (all 20 source rows by
`sed -n`; the coverage measurement; five source-tree mutants) · Item 2 (nine bundle mutations + two
checker mutants) · Item 3 (five `t0` type mutations, six window-edge values, the offset-derivation
chain) · Item 4 (eleven identity/anchor/arg attacks) · Item 5 (six replay attacks) · Item 6 (nine
membership attacks) · Item 7 (five positive-leg attacks) · Item 8 (nine masking/canary attacks) ·
Item 9 (AST read enumeration + seven FIFO plants) · Item 10 (matrix A/B/C/D) · Item 12 (the signer's
fixed aux, read from source) · Item 13 (the AF-AP-40 hits classified by RUN; four sweep-class
verdicts re-tested) · Item 14 (the PC gate) · Item 15 (60 mutants) · Item 16 (report_lint on this
report — see below).

**Reviewed statically (read, not executed):** Item 11 in full — `run_s0_02_legs.sh` and
`deliver_event.py` are READ-ONLY per the brief and I ran neither; F2, F5 and the NIP-98 replay
analysis are source reads cross-checked against `buzz-auth`/`buzz-relay` primary source. The lane's
24-row mutant table (I re-derived 2 of its rows independently and reproduced the three committed
exits it pastes). `validate-ledger`'s spec-binding logic (read; F16's conclusion follows from
`:192-196` and `:251-252`).

**Deliberately skipped, and why:** every live leg (no relay, no key material in the sandbox; and
the brief forbids touching the owner's relay) · `run_s0_02_legs.sh` and `deliver_event.py`
execution (brief: READ, never run) · re-running FIFO-HANG (it hangs by design) · any timing claim
(the sandbox is shared — I saw other lanes' `n5i` and `d5m` pytest processes throughout) ·
minting or touching `proofs/ledger.json`, `registry.yaml`, `result.json` (nothing minted by this
lane; the AF-AP-56 attested-input gate does not fire).

---

# SHARED-TREE HYGIENE & PROCESS CENSUS

**Git on the shared tree: read-only throughout.** Only `git archive`, `git show`, `git log`,
`git ls-tree`, `git rev-parse`, `git check-ignore`, `git status --porcelain`, `git worktree
add --detach` / `remove --force`. **No** stash / checkout / restore / reset / add / commit / push.
The tree's uncommitted set (13 modified `proofs/S0-01/*` + `tests/*` files and 6 untracked paths
belonging to other lanes) is byte-identical to what it was when I started; I never wrote inside
`/home/user/agent-factory`. The shared HEAD moved from `e27eaaa` to `1c8ec05` during my session
(another lane committed) — irrelevant, since every byte I graded came from `git archive 088efef`.
The detached worktree I created for the PC gate was removed; `git worktree list` shows the single
main entry.

**Everything I wrote lives under** `/tmp/claude-0/.../scratchpad/`: `vb1/` (the PIN archive),
`buzzscratch/` (the buzz source copy), `atk/` (≈45 bundle copies), `mut/` (two checker mutants),
`bt/` (every pytest `--basetemp`), `wt-dQM4` (removed).

**Process census.** Every run was foreground under `timeout -s KILL`. **I started no background
process and I killed nothing — no `kill`, no `pkill`, no `pgrep`, not once.** Two `timeout`-wrapped
pytest runs exceeded no cap. At close, `ps -eo pid,ppid,etimes,args` shows the only live pytest
processes are other lanes' (`pids 26461/26462` under `scratchpad/n5i/…`, `26505/26513/26515` under
`scratchpad/d5m/…`) — visible, untouched, left alone. **No process of mine is running.**

**`report_lint` on this report** (Item 16) — run with
`--map C=proofs/S0-02/check_buzz_authz.py --map T=tests/test_s0_02_buzz_authz.py
--map O=proofs/S0-02/oracle/denial_table.py --map B=proofs/S0-02/tools/build_fixtures.py`
plus the seven buzz maps: see the trailing line the coordinator can re-run; every `file:line` above
was obtained by `sed -n`/`grep -n` on the PIN bytes or on the pinned checkout, never typed from
memory.

---

# VERDICT

**NOT-READY.** The verdict does not depend on anything I failed to reproduce: F1, F3, F4, F6-F21
were all executed in this session; **F2 and F5 are static reads of PC-only files I was forbidden to
run**, and I say so explicitly — F2 is a two-line control-flow fact (`rm -rf "$out"` at :135
precedes the `[ -f "$out/membership.json" ]` test at :170) and F5 is an arithmetic fact about two
committed constants, so neither needs execution to stand; but neither has been observed live.

## Blocking set (5)

| # | finding | why it blocks |
|---|---|---|
| **F1** | `_production_verify_sites` sees 3.6-10.8 % of each file; a channel-path `verify_event` survives green | the report's HEADLINE finding (D1/D2) is unpinned; the claim is true, the gate is hollow |
| **F2** | the runner deletes the operator's `membership.json` before testing for it | seed **assertion 2** cannot be captured at all |
| **F3** | the removal receipt's `at_epoch_s` and `channel` are never read | a removal recorded AFTER the delivery passes; assertion 2's meaning is not gated |
| **F4** | `.gitignore` re-include misses `proofs/*/evidence/**/*.log` | AF-AP-62 recurs the moment the real legs are committed; the git-view gate goes red |
| **F5** | `LEG_CLOCK_TOLERANCE_S` 120 vs `TURN_WAIT_S` 100 (+ the NIP-98 same-second replay guard) | the replay leg's second sub-leg fails freshness on any slow turn |

## Cheapest path (one increment, ~90 lines total, no redesign)

1. **F4** — one line in `.gitignore` + the `git check-ignore` red test. (2 min; do it first, it
   gates every later capture.)
2. **F2** — move the membership receipt outside `$out` and `cp` it in after the wipe; the static
   ordering test. (10 min.)
3. **F5** — `sleep 1` + thread the first sub-leg's `t0` into the second `deliver`; the
   constant-relation test. (10 min.)
4. **F3** — the four added assertions in `check_buzz_authz.py:357-364` + three red tests; have the
   coordinator record the relay's removal response into `membership.json`. (20 min.)
5. **F1** — replace the prefix cut with whole-file scanning + exact-equality `known`, and widen the
   regex to the alias form; the channel-path plant as the red test. (25 min.)
6. Then the cheap non-blockers in one sweep: **F8** (parse the integer), **F9** (level-aware
   canary + demand it only for buzz-acp-decided legs), **F12** (mirror the tolerance arm into the
   stale branch, `<=` at the boundary), **F13/F13b** (guard `:351`, adopt `_check_with_timeout`),
   **F11** (root closure), **F10** (wrong-channel rejection), **F6/F7/F15/F23** (report and oracle
   prose corrections). (~45 min.)
7. **F16** is a `validate-ledger` matter, not this lane's — raise it as its own task.

Re-run after: `bash scripts/lane_gate.sh -r 088efef -f "<the touched files>" -t
"tests/test_s0_02_buzz_authz.py" -n 2`, then the PC gate above.

## Exact PC steps for the coordinator's live legs

**Do not run anything until F2, F4 and F5 have landed** — as it stands the revoked leg is
unreachable, the captured logs will be gitignored, and the replay leg is a coin flip.

Three prerequisites, in order:

1. **The RUST_LOG seam (blocks 6 of 7 legs, not 2 — F9b).**
   `proofs/S0-01/pins.py:44` defines `PINNED_ENV_KEYS` as a closed frozenset and
   `proofs/S0-01/tools/pc/pc_launch.py:167` refuses any drift from it
   (`if set(env) != expected_keys:` — note **:167**, not the report's :268). Add `"RUST_LOG"` to
   `PINNED_ENV_KEYS`, pass `RUST_LOG=debug` (or `buzz_acp=debug`), and re-mint every S0-01 artifact
   the AF-AP-56 attested-input rule covers — `pins.py` is S0-01 tooling. The runner's preflight
   (`run_s0_02_legs.sh:51`) greps `pins.py` for `"RUST_LOG"` and exits 3 until then; `tests:879-885`
   is the matching tripwire (note it greps the whole file text, so even a comment mentioning
   `"RUST_LOG"` would satisfy it — tighten to the `PINNED_ENV_KEYS` block).
   **Sequence with lane A5k:** S0-02 imports six names from S0-01 **by path**, so any rename or
   move breaks the checker at import time (an `AttributeError` traceback, not a `failure_reason:`):
   * from `proofs/S0-01/check_acp_conformance.py` — `Failure`, `Deferred`, `_require_file`,
     `_require_dir`, `_load_timeline_raw`, `_HEX64_ANYWHERE_RE` (`check_buzz_authz.py:86-91`);
   * from `proofs/S0-01/tools/nostr_verify.py` — `event_id`, `verify_event`, `sign_event`
     (`check_buzz_authz.py:149,156`; `build_fixtures.py:181,187,275,345,378`;
     `deliver_event.py:87,161,166`);
   * `proofs/S0-01/fixtures/identities.json` — keys `owner`, `agent`, `relay`, `user2` (+ the
     `!= "relay_url"` exclusion at `check_buzz_authz.py:180`);
   * `proofs/S0-01/pins.py` — read as **text** only, by `tests:883`.
   If VERIFY-CK12's recommendation lands and `_require_file` moves into `pins.py`, S0-02 needs the
   matching one-line rebind **and** the two literal source assertions at `tests:814-815` updated in
   the same increment. **Land A5k first, then S0-02's rebind, then capture.**

2. **The relay membership write (owner/coordinator operation, never a lane's).** Remove the owner
   pubkey from the NIP-29 group on the isolated S0-01 relay stack, **capture the relay's actual
   response**, and write it where F2's fix expects it — e.g.
   `$DEST/revoked-membership.json` as
   `{"removed":true,"removed_pubkey":"<owner hex>","channel":"73701f66-6e12-42ff-b561-7d36db1ad91b",
   "at_epoch_s":<epoch, strictly before delivery>,"http_status":<the relay's status>}`.
   Then re-add the owner afterwards. Key rotation stays `NOT run` (not on the pinned relay's REST
   surface).

3. **The role keys.** `deliver_event.py` requires `BUZZ_PRIVATE_KEY` **in the environment**
   (`:74`) — sourced by the runner from `$PINNED/.secrets/<role>.env` (`run_s0_02_legs.sh:122`),
   never in argv. Roles needed: `owner` (pos-allowed, neg-bad-signature, neg-replayed, neg-stale,
   revoked) and `nonmember` (neg-unauthorized) — the runner reads each from the fixture's
   `signer.role` (`:127-130`), so a `.secrets/nonmember.env` must exist on the PC.

Then, on the PC only:
```
bash proofs/S0-02/tools/pc/run_s0_02_legs.sh <repo>/proofs/S0-02/evidence \
     pos-allowed neg-unauthorized neg-bad-signature neg-replayed neg-stale neg-self-authored
# then, after the membership removal:
bash proofs/S0-02/tools/pc/run_s0_02_legs.sh <repo>/proofs/S0-02/evidence revoked
python3 proofs/S0-02/check_buzz_authz.py proofs/S0-02/evidence      # expect rc 0
```
Expect `respond_to=owner-only` and `ignore_self=true` in the startup line (both confirmed in the
real corpus) — the `neg-self-authored` leg depends on the second.

**One design recommendation for the coordinator (Item 17), from what I measured:** the seed's
`denied: sender-not-in-allowlist` is currently proven by a **non-member** key, which buzz-relay
rejects — so the component S0-02 names never sees it, and buzz-acp's own author-gate line
(`lib.rs:550`) stays unreachable. `crates/buzz-acp/src/lib.rs:389` shows `RespondTo::OwnerOnly`
denies any author who is not the owner-or-sibling, and `proofs/S0-01/fixtures/identities.json`
already carries `user2`. **A `neg-not-allowlisted` leg signed by `user2` — a channel MEMBER the
relay accepts and buzz-acp then drops — would make the allowlist reason a genuine buzz-acp
decision, give a sixth distinct observable, and restore the seed's framing without amending it.**
The oracle already names this as the fixture not built (`denial_table.py:80-83`). It is the single
highest-value addition to this proof and it costs one fixture plus one leg.

On the seed wording: with that leg added, the seed's *"buzz-acp rejects…"* framing holds for
replay, self-authored and not-allowlisted, and needs no amendment for those three. For **signature**
and **freshness** it does not hold at `1c8321cd` and no fixture can make it hold — those two blocks
should read *"the Buzz ingress (buzz-relay at publish) rejects…"*, with `docs/03 §1`'s five-class
list unchanged.


---

## report_lint on THIS report (Item 16)

```
report_lint: 110 refs — OK 30, NEAR 2, MISS 42, UNCHECKABLE 36, UNRESOLVED 0 (worktree, PIN bytes)
```
**I inspected all 42 MISSes and all 2 NEARs by hand: none is a wrong reference.** Every one is the
linter's documented heuristic limit — a report line that cites a location and then states, in
words, something the cited *line* does not contain verbatim (`report_lint.py:16-20`: *"the report
line carries no claim token to test against"* / *"the cited lines contain none of the claim
tokens"*). The recurring shapes:
* the six whole-file verify sites (report:45-49, :85) — every cited line really does hold a
  `verify_event(` or `.verify()` call; the claim tokens are `KNOWN`, `buzz-acp/src`, `EVENT`;
* the two references to `proofs/S0-01/tools/pc/pc_launch.py:268` (report:257, :264) — these are me
  **quoting the lane's wrong reference** in F6; the MISS is the finding;
* the two deliberate NEARs (report:552 `relay.rs:1176`, report:591 `relay.rs:1141`) — F15's point
  is precisely that the cited line documents a *different* field;
* claims about a checker branch stated in prose (report:226 `:214`, :314 `:208`, :363 `:264-269`,
  :451 `:219-223`, :527 `:230`) — each cited line is correct; I re-read all five by `sed -n`.

The run:
```
scripts/report_lint.py <this report> --root <git archive 088efef copy>   --map C=proofs/S0-02/check_buzz_authz.py --map T=tests/test_s0_02_buzz_authz.py   --map O=proofs/S0-02/oracle/denial_table.py --map B=proofs/S0-02/tools/build_fixtures.py   --map crates/buzz-acp/src/{lib,relay,filter,queue,engram_fetch,pool}.rs=<buzz>/...   --map crates/buzz-relay/src/handlers/ingest.rs=<buzz>/...   --map crates/buzz-relay/src/api/{bridge,mod}.rs=<buzz>/...   --map crates/buzz-auth/src/{nip98,error}.rs=<buzz>/...   --map crates/buzz-core/src/error.rs=<buzz>/...
```

## Scratch cleanup
`vb1/`, `buzzscratch/`, `atk/`, `mut/`, `bt/`, `lintaudit.py`, `resign*.py`, `pvs.py` deleted at
close; the PC worktree removed. Only this report remains under `wf-results-r5/`.
