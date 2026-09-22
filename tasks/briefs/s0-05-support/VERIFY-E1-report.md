# VERIFY-E1 — adversarial grade of lane E1 (S0-05 no-direct-egress)

PIN: `5c2392e` · venue: sandbox, uid 0, kernel `6.18.44-fc-v37`, `iptables v1.8.10 (nf_tables)`, `iproute2-6.1.0`,
`ip_forward=0` · graded 2026-09-22T06:12Z–06:45Z · adversarial-verifier (Opus 5).
Nothing committed, nothing staged, nothing pushed, no issue, no comment. `git status --porcelain` on the shared tree
was empty at 06:42:44Z (this report is the only new file; it was never `git add`ed).

**Why this lane graded in the sandbox.** `L:57` `[ "$(id -u)" = "0" ] || { echo "not-root"; return 1; }` makes every
library function root-only; the PC bridge user is uid 1000 and `sudo` there needs the owner's password, so the PC
local-Qwen verify route cannot host this brief. The live-unit legs are an OWNER-run step — items 9 and 14 give the
exact steps and the design answer for it.

**Re-pin measured, not assumed.** `git diff --stat 24e80e6 5c2392e -- proofs/S0-05 tests/test_s0_05_egress.py
spikes/selective-egress` → empty; the raw diff is **0 bytes**. The S0-05 boundary at `5c2392e` is byte-identical to the
original PIN. (The shared tree's HEAD moved `4cc3fe2` → `953ccfe` during this run — coordinator work on other files;
every measurement below is on a `git archive 5c2392e` copy under the session scratchpad.)

Aliases: `C` = `proofs/S0-05/check_egress.py` · `L` = `proofs/S0-05/netns_lib.sh` · `R` = `proofs/S0-05/run_canaries.sh`
· `T` = `tests/test_s0_05_egress.py` · `PC` = `proofs/S0-05/tools/pc/run_s0_05_units.sh` ·
`probe.sh` = `spikes/selective-egress/probe.sh`.

---

## Item 0 — the mechanical gates, pasted (2026-09-22T06:15:00Z)

```
report_lint (E1-report.md, five maps, --rev 5c2392e):
report_lint: 112 refs — OK 107, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 5 (at 5c2392e)
   the five UNRESOLVED are unmapped aliases: three probe.sh ranges (lines 50-58, 113-116, 26-32) and a host name twice

with --map probe.sh=spikes/selective-egress/probe.sh added:
report_lint: 112 refs — OK 108, NEAR 0, MISS 2, UNCHECKABLE 0, UNRESOLVED 2 (at 5c2392e)

ap_screen.py proofs/S0-05 proofs/S0-05/canaries          (06:15:02Z)
--- AP_SCREEN over 2 path(s): 3 hits over 2 files ---
AF-AP-72: 2   proofs/S0-05/canaries/connect_probe.py:48 (×2, one line)
AP-32: 1      proofs/S0-05/check_egress.py:171

ap_screen.py --tests tests/test_s0_05_egress.py
--- TEST_SCREEN over 1 path(s): 0 hits over 1 files ---

baseline suite, from the archive copy of the PIN (06:15:26Z):
98 passed in 4.02s      exit 0, `-rs` reports no skips
```

The amendment's numbers reproduce exactly. The two MISS under the `probe.sh` map are a lint-token convention, not a
wrong citation — see F21. The `AF-AP-72` row is classified by RUNNING in F20; `AP-32` is re-derived in item 3.

---

## Item 1 — D4: what the gate decides vs what routing decides

### 1a. The three bundle shapes, re-measured on THIS kernel (06:22:19Z–06:22:35Z)

Real `L`/`R`/`C` on a real namespace `s0-05-ve1-a1`, stand-in listeners on the veth host address started and killed by
pid. Namespace routes: `10.201.38.0/24 dev en257db5a5 proto kernel scope link src 10.201.38.2` — **no default route**.

| canary | gate ON | gate OFF | isolated (no veth) |
|---|---|---|---|
| C0 `10.201.38.1:12800` | rc 0, HTTP 200 | rc 0, HTTP 200 | rc 7 `Couldn't connect to server` |
| C1 api.openai.com | rc 6 `Could not resolve host` | rc 6 same | rc 6 same |
| C1 api.anthropic.com | rc 7 (`/etc/hosts` short-circuit, `resolved=160.79.104.10`) | rc 7 same | rc 7 same |
| C1 generativelanguage… | rc 6 `Could not resolve host` | rc 6 same | rc 6 same |
| C2/C3 ×3 | rc 7 `OSError [Errno 101] Network is unreachable` | **identical** | identical |
| C4 example.com port 443 | rc 7 `[Errno 101] Network is unreachable` | **identical** | identical |
| C5 `10.201.38.53:53` | rc 7 `PermissionError [Errno 1] Operation not permitted` | **rc 28 `TimeoutError timed out`** | rc 7 `[Errno 101]` |
| C6 `10.201.38.1:12801` | rc 28 `Timeout was reached` | **rc 0, HTTP 200** | rc 7 |
| counters | `0 -> 10` | `0 -> 0` | `0 -> 0` |
| checker | `PASS … 1 units, 11 canaries failed as required, positive controls 1/1` rc 0 | `egress-permitted: gate-disabled` rc 1 | `positive-control-failed: curl` rc 1 |

**D4 CONFIRMED verbatim.** Only C5 and C6 flip. C2/C3/C4 fail on ROUTING in both gate states. One precise correction:
C1 for openai/google fails rc 6 `Could not resolve host`, not `[Errno 101] Network is unreachable` as the report's D4
sentence says (F15). C1's outcome is the same in both gate states for a second reason: gate ON, the DNS query to the
blackhole resolver is dropped by the OUTPUT policy; gate OFF, it is unanswered. Either way rc 6, so C1 does not
discriminate either.

### 1b. The ROUTED variant, built here (06:23:33Z–06:25:13Z)

One change to the topology, nothing else: `ip netns exec <ns> ip route add default via <veth host ip>`. Safety: the host
has `ip_forward=0` (read before and after), plus a belt-and-braces `iptables -I FORWARD -i eh9e811e23 -j DROP` removed
in the trap; the "internet" is a second LOCAL listener on `198.51.100.7:443`. Nothing of this reached the world.

| | routed, gate ON | routed, gate OFF |
|---|---|---|
| C2/C3 ×3, C4 | rc 28 `TimeoutError timed out` | rc 28 (this host does not forward) |
| C5 | rc 7 `Operation not permitted` | rc 28 |
| C6 | rc 28 | rc 0 HTTP 200 |
| a LIVE off-/24 routable target `198.51.100.7:443` | rc 28, blocked | **rc 0 `connected`** |
| counters | `5 -> 55` | — |
| checker | **`PASS …` rc 0 — the routed bundle passes with ZERO checker changes** | `egress-permitted: gate-disabled` rc 1 |

**The D4 measurement, in three sentences.** In the shipped unrouted shape the gate decides only C5 and C6; C1–C4 are
decided by the absence of a route and produce the identical record whether the gate is on or off, so nothing in the
suite ties a model endpoint to the firewall. Adding a default route through the veth host end moves C2/C3/C4 onto the
firewall — they then fail because the OUTPUT policy eats the SYN — but the resulting signature is a 5-second `rc 28`
timeout, which is exactly what an unanswered route also produces, so routing alone still does not prove the gate was
the decider. The one leg that proves it is a target that would otherwise ANSWER: the routed namespace's `198.51.100.7:443`
listener flips rc 28 → rc 0 `connected` across the gate, which is C6's role lifted off the namespace's own /24 — so the
PC legs need the routed variant **plus a reachable stand-in at the model address** (or real NAT) before S0-05 can claim
anything about model endpoints.

---

## Item 2 — the gate-fired proof under attack (06:27:05Z–06:27:11Z)

* **The counter is namespace-and-window scoped, not canary-attributed.** With a stray, non-canary process inside the
  namespace sending UDP to an on-link blackhole while the REAL collector ran, the committed evidence read
  `gate-fired: curl OUTPUT policy DROP 0 -> 400010 packets` and the checker **PASSED** (`CHECK-STRAY-RC=0`). Baseline
  delta on the same shape is 10. `C:276` `if after <= before:` is the whole rule. See F2.
* **A wrapped counter is fail-CLOSED:** `before=4294967295 after=3` → `gate-inert: curl OUTPUT DROP counter did not
  advance (4294967295 -> 3)` rc 1. `before=after=7` → the same rc 1.
* **The minimum evidence is one packet:** `before=0 after=1` → `gate-fired … 0 -> 1 packets`, `PASS`, rc 0.
* **Both policies are read** — mutant `COUNTER-READS-DROP-ONLY` on `L:170` `egress_ns_drop_counter() {` re-run: CAUGHT by
  `T:680` `test_the_drop_counter_reads_both_policies`.

---

## Item 3 — the rules digest and the declared allow-list (A10) (06:37:07Z)

Cross-language hash reproduced on the real bundle — three independent computations, one value:

```
gate.json rules_sha256 (kernel side: `egress_ns_rules | sha256sum`)   = 3e4f78b8bf95a1a258ec37c3…
checker rules_digest(runtime.rules)                                    = 3e4f78b8bf95a1a258ec37c3…
checker rules_digest(expected_rules(gate.allowed))                     = 3e4f78b8bf95a1a258ec37c3…
```

* A **REORDERED** rule list (identical set, reversed) → `egress-rules-unpinned: curl recorded rules do not hash to the
  gate digest`, rc 1. **Not a false red in the production path**: `L:159` `egress_ns_rules()` pipes through
  `LC_ALL=C sort` and `C:157` `def expected_rules(allowed):` returns `sorted(lines)`, so both sides already canonicalise
  and a reordered list can only arrive by hand-editing. Making the comparison order-insensitive by set membership would
  open a hole — a DUPLICATED rule (measured: also rc 1 today) would then be masked. Leave it as it is.
* A **WIDENED** allow-list with a self-consistent digest and rule list → **PASS rc 0**. The digest pins the rules to the
  DECLARED allow-list, never to `docs/05_SECURITY.md` §6. The lane says this itself in its SELF-ATTACK 3; there is no
  checker parameter for an expected allow-list. F12.
* `AP-32` at `C:171` `return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()` — SAFE, and proven by the
  three-way equality above rather than argued.

---

## Item 4 — the denial vocabulary and the own-target rule (06:37:07Z)

| hostile record | verdict |
|---|---|
| pure proxy-shaped denial (D6a text verbatim) | rc 1 `denial-detail-foreign-target: curl C1 denial names 127.0.0.1, not api.openai.com` |
| detail names the PROXY first, then its own target | rc 1, same reason |
| **detail names its OWN target FIRST, then the proxy** | **rc 0 PASS** — F4 |
| LAN-proxy denial (`10.0.0.5 port 3128`) + a forged `"ip": "10.0.0.5"` | **rc 0 PASS** — F14 |
| the same LAN-proxy denial without the forged `ip` | rc 1 `denial-detail-foreign-target: curl C2 denial names 10.0.0.5` |
| `"resolved"` forged to `127.0.0.1` on every C1 | rc 0 PASS — the field is never read (F13) |
| the `/etc/hosts` short-circuit record as collected (D6b) | rc 0 PASS — correct, it names its own target |
| forged-loopback mutant `LOOPBACK-ALIAS-ACCEPTED` on `C:114` `if isinstance(candidate, str) and not candidate.startswith("127."):` | CAUGHT by `test_a_forged_loopback_ip_cannot_whitelist_a_proxy_denial` |

`C:116` `for pattern in (CURL_CONNECT, CURL_RESOLVE):` uses `.search()`, i.e. the FIRST match only — that is the
mechanism behind row 3. D6a and D6b both reproduce on this kernel; this sandbox's proxy is `HTTPS_PROXY` on `127.0.0.1`
(port differs from the lane's 40173 — it is ephemeral), and `/etc/hosts` still maps `api.anthropic.com` to
`160.79.104.10`.

---

## Item 5 — the positive control (06:37:07Z, 06:39:52Z, 06:40:37Z)

* The isolated bundle is red on it: `positive-control-failed: curl` (AF-AP-1 as designed), reproduced live.
* `C0 http_status` 200 → 204 passes (2xx), 302 → `positive-control-failed: curl`. Correct.
* **C0's target is NOT bound to `gate["allowed"]`** (F5): rewriting C0's target to `10.201.38.1:19999`, and even to
  api.openai.com port 443, keeps the bundle PASSING. `C:214` `def check_positive_control(records, unit):` reads only
  status/rc/`http_status`. Through `R` the two are equal by construction — `R:75` `run_canary c0_allowed_target.sh "$UNIT" "$ALLOWED"`
  passes the allowed target to C0 and `R:121` `gate = {"gate": gate_state, "mechanism": mechanism, "netns": ns, "unit": unit,`
  writes the same value into `gate.allowed` — so this is a checker-completeness gap, not a live exploit at the PIN.
* **The AF-AP-1 attack that DOES pass — F1, the blocker.** See below.

---

## Item 6 — the units manifest (06:37:07Z)

| input | verdict |
|---|---|
| `not-run` without a reason | rc 1 `units-manifest-invalid: x declared not-run without a reason` |
| `curl` present AND declared `not-run` | rc 1 `unit-declared-absent-but-present: curl` |
| `hermes-acp` declared `run` but missing | rc 1 `unit-missing: hermes-acp` |
| `units.json` a bare list | rc 1 `units-manifest-invalid: units.json must be {"units": [...]}` |
| `curl` declared `not-run` with a reason, its dir removed | rc 1 `no-units: no run unit in …` |
| `--units curl,hermes-acp`, only curl present | rc 1 `unit-missing: hermes-acp` |
| `--units ""` | rc 0 PASS — the required set is empty (F18) |

PASS-line numerator/denominator: mutant `PASS-RATIO-COUNTS-RECORDS` on `C:334` `positives += check_positive_control(records, unit)`
re-run → CAUGHT by `test_the_pass_line_counts_units_not_records`. **The declared-equivalent survivor is genuinely
equivalent and I did not write a killer:** `C:214` `def check_positive_control(records, unit):` either raises or returns
exactly 1, it is called once per unit in a loop with no `break`/`continue`, and `units` is built from a set of directory
names, so `positives == len(units)` holds unconditionally at the PASS line. AGREED.

---

## Item 7 — the library (06:39:08Z–06:39:11Z)

* **Destroys by NAME.** `L:203` `egress_ns_destroy() {` takes `$ns` and `L:207` `ip netns del "$ns" 2>/dev/null || true`;
  `PC:72` iterates `$NS_LIVE`. No `ip netns list | grep` anywhere; 0 `pgrep`/`pkill` hits across the whole proof.
* **Destroy with a LIVE process inside (F7).** `ip netns pids` showed pid 7654 in the namespace; `egress_ns_destroy`
  returned 0, `ip netns list` went empty, the veth and `/etc/netns/<ns>` were gone — **but the process was still alive
  and still in the old net namespace** (`net:[4026532283]` vs root `net:[4026531833]`). The namespace object survives,
  invisible to the census the lane's own test asserts on.
* **The blackhole resolver never collides with the allowed target**: `L:54` `egress_ns_resolver()` is `.53` of the
  namespace's own /24 while the target is the veth host `.1`. The mutant that collides them
  (`VE1-RESOLVER-COLLIDES-WITH-ALLOWED`) is CAUGHT by `test_library_derivations_are_deterministic_and_fit_ifnamsiz`.
* **The isolated control has no veth (D7)**: `mechanism: netns-no-veth`, `links in ns: lo` only. Reproduced.
* **Two concurrent namespaces CAN share a /24 (F6).** `L:44` `_egress_octet() {` and `L:47` `printf '%d\n' $(( n % 254 + 1 ))`
  give 254 buckets. Measured with a real colliding pair `s0-05-ve1-0` / `s0-05-ve1-264` (both → `10.201.115.1`): **both
  creates returned rc 0**, two interfaces carried the same address on the same /24, and a connect from the second
  namespace to that address timed out. Interface names stay unique (`eh72dc9c18` vs `eh72b74bd3`, 8 hex of sha256), and
  destroying the second namespace did NOT strip the first's address. The PC runner's three unit names are
  collision-free today (octets 107 / 219 / 153).

---

## Item 8 — the collector (06:39:08Z–06:39:11Z)

* **The proxy scrub covers all eight variables** in both layers — `R:42` `SCRUBBED="HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY http_proxy https_proxy all_proxy no_proxy"`
  and `proofs/S0-05/canaries/_emit.sh:11` `EGRESS_SCRUBBED_ENV="HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY http_proxy https_proxy all_proxy no_proxy"`.
  No test pins more than `HTTPS_PROXY`/`https_proxy` (`T:723` `test_the_canary_emitter_scrubs_the_proxy_environment`), so
  mutants that shorten either list SURVIVE — defence-in-depth, see F22.
* **Model hosts resolved OUTSIDE the namespace, a non-resolving host DEFERS**: a record with `status: not-run` drives
  `deferred: curl C2 not-run: resolve-failed: no A record from this venue`, rc 2. Never a fake denial.
* **`DROP_BEFORE` unreadable → exit 3 re-run**: `run_canaries.sh curl s0-05-ve1-no-such-ns …` → rc 3, stderr
  `run_canaries: cannot read the OUTPUT DROP counter of s0-05-ve1-no-such-ns`. But the guard's own red test does not
  discriminate it (F3), and the aborted run still leaves `<unit>/canaries.jsonl` behind (F17).
* **The census is `pgrep`-free**: 0 hits for `pgrep|pkill` across `proofs/S0-05`.

---

## Item 9 — the PC runner, READ only (never executed here)

Read at the PIN, every external call traced; three defects found statically.

* `PC:20` states the routed variant plainly: `#     internet is reachable and only the allow-list holds providers back, is NOT BUILT.` ✔
* `PC:99` carries `  # NOT VERIFIED: no S0-01 launch has ever been run inside a network namespace.` ✔
* External calls at the PIN: `egress_ns_capable`, `egress_ns_create`/`_destroy`/`_run`/`_host_ip` (`L`), `curl` (the
  preflight), `setsid /usr/bin/python3 …`, `seq`, `sleep`, `kill -0`, `bash …/run_canaries.sh`, `cat`,
  `python3 …/check_egress.py`, and the two S0-01 tools — **both of which exist at the PIN**
  (`proofs/S0-01/tools/pc/pc_launch.py` with `--leg`/`--model`, `proofs/S0-01/tools/pc/pc_backend_restart.sh`).
* The failure-aware bounded poll is real: `PC:111` `for _ in $(seq 1 30); do` with `kill -0 … || break` and a re-check
  after the loop. It waits for LIVENESS only, which the file says.
* Never kills by name: `PC:124` `[ -n "$launch_pid" ] && kill "$launch_pid" 2>/dev/null || true`. ✔
* **F8** — `PC:103` `egress_ns_run "$ns" setsid /usr/bin/python3 ${LAUNCH[$unit]} </dev/null \` runs every unit under
  `python3`, but `PC:56` `LAUNCH[s0-01-backend]="$S0_01_TOOLS/pc_backend_restart.sh"` is a **bash** script
  (`#!/usr/bin/env bash`). `python3 pc_backend_restart.sh` is a SyntaxError, the poll sees the process gone and the unit
  is recorded `not-run|launch exited within the settle window` — the backend unit can never be collected.
* **F9** — `setsid` + `$!`: the liveness check and the later `kill` track the wrapper, not necessarily the unit; a unit
  that outlives the `kill` keeps the namespace alive invisibly (F7).
* **F10** — the S0-01 scripted backend binds `--bind 127.0.0.1 --port 20201`. Launched inside a fresh namespace its
  loopback is the NAMESPACE's, so OmniRoute (in the host namespace) can no longer reach it: `s0-01-backend` is not
  containable in this design without a bind or DNAT change.
* **F11** — `R:30` `VENUE=${6:-sandbox}`: `PC:121` `bash "$P/run_canaries.sh" "$unit" "$ns" "$allowed" "$EVIDENCE_ROOT" "" pc` passes the venue explicitly, but any hand invocation with five arguments
  silently stamps a PC bundle `"venue": "sandbox"` — the one field the lane's SELF-ATTACK 3 relies on for "it ran there".
* **F23** — `PC:82` `ns="s0-05-$unit"` is a fixed name and `egress_ns_create` destroys first (`L:76` `egress_ns_destroy "$ns"`), so two concurrent
  runs of the runner tear down each other's namespaces.
* Units declared vs units that exist on the PC: `hermes-acp` and `buzz-acp` are launched as host processes by
  `pc_launch.py` (`subprocess.Popen(pins.PINNED_LAUNCH_ARGV…)`), so they CAN be launched inside a namespace; the Buzz
  relay stack itself runs under podman (PC-BRIDGE.md, the container and per-proof rows) in its own network namespace and is therefore a
  destination, not a containable unit; `s0-01-backend` is blocked by F8+F10. `memory-adapter`, `ai-memory`,
  `dream-foundry`, `pandaprobe`, `harness-router` are declared `not-run` with reasons and are never counted.

---

## Item 10 — the 18-class table re-scanned over the 34 files

The seven fixed defects, each graded by RUNNING:

| class | the fix | discriminating red test? |
|---|---|---|
| 1 / 18a — the `ip` alias floor at `C:114` `if isinstance(candidate, str) and not candidate.startswith("127."):` | present | YES — mutant CAUGHT by `test_a_forged_loopback_ip_cannot_whitelist_a_proxy_denial` |
| 3 — the test's positional `records(...)[0]` | present (`T:144` selects by canary id: `assert len(c0) == 1 and c0[0]["rc"] == 7`) | n/a (test-side) |
| 6 — `R:72` `[ -n "$DROP_BEFORE" ] \|\| { … exit 3; }` | present | **NO — F3**, the mutant that reverts it SURVIVES the whole suite |
| 9 — `PC:111` `for _ in $(seq 1 30); do` the failure-aware bounded poll | present | none (the PC runner is never executed — declared) |
| 15 — the PASS ratio | present | YES — CAUGHT |
| 18b — INCIDENT-LOG cited by ROW id | present (`L:13`, `C:22`, `C:44` all cite `AF-AP-1` / `AF-AP-24`, no line numbers) | n/a |
| 18c — the counter reads both policies | present | YES — CAUGHT |

Re-scan of the remaining classes over the 34 files: class 2 (all four reads go through `C:123` `def _require_regular(path, name):`),
class 5, class 7 (empty), class 8, class 11, class 12 (one trap, installed after `cleanup` is defined), class 13 (empty),
class 14, class 16, class 17 (the JSONL is truncated and owned) — I found nothing the lane missed in those. New
observations that belong to the classes: F11 (class 6, `R:30` `VENUE=${6:-sandbox}`), F17 (class 17/9 ordering,
`R:36` `OUT="$EVIDENCE_ROOT/$UNIT"` and `R:39` `: > "$JSONL"` run before the `R:72` `[ -n "$DROP_BEFORE" ] ||` guard), F19 (class 16, `_egress_apply_gate` validates the port but not the IP — `10.0.0.1/8:443` is accepted by
the library and backstopped by the checker's `IPV4_PORT`).

---

## Item 11 — the PC gate (the one carve-out), pasted

```
launch (06:41:59Z): 20260922T064159Z-5c2392e — base 5c2392e3de71e8482b6d5d061252bdfed2ed7192
                    + patch 0B (sha e3b0c44298fc), set 'tests/test_s0_05_egress.py' (1 files set=9f0502080347), -n 8
wait   (06:42:13Z): pytest-exit: 0
                    pytest-summary: 94 passed, 4 skipped in 1.24s
                    pytest-set: 1 files set=9f0502080347 — tests/test_s0_05_egress.py
```

A 0-byte patch: the PC ran EXACTLY the PIN's bytes. **AGREED with the checkpoint's `94 + 4 skipped`.** The four skips are
the four `@NEEDS_NETNS` tests and nothing else — `T:653` `def test_library_round_trip_leaves_no_namespace_behind():` and `T:680` `def test_the_drop_counter_reads_both_policies():`, `T:703` `test_the_isolated_control_has_no_veth_and_fails_its_positive_control`,
`T:723` `test_the_canary_emitter_scrubs_the_proxy_environment`; the gate is `T:93` `NEEDS_NETNS = pytest.mark.skipif(`
with the declared reason, and the PC lane user is uid 1000. The fifth conditional test, `T:579` `def test_the_collector_refuses_an_unreadable_drop_counter(tmp_path):`, is gated on `shutil.which("ip")` and RAN there.
The detached worktree was removed at 06:42:44Z and `git worktree list` shows only the shared tree. Nothing else on the
PC was touched.

---

## Item 12 — mutants: 37 run, 31 CAUGHT, 6 SURVIVED, 0 INVALID (06:30:09Z–06:32:15Z)

Every mutant on a scratch copy under the session scratchpad; each was compile/parse-checked before it counted
(`py_compile` / `bash -n`), so no AF-AP-78 SyntaxError "kills". The lane's 20 reproduce exactly: 19 CAUGHT with the same
killers the report names, 1 declared-equivalent survivor. My 17 add 12 CAUGHT and 5 survivors.

```
CAUGHT   GATE-OFF-ACCEPTED · GATE-CHECK-AFTER-CANARIES · POSITIVE-CONTROL-OPTIONAL · BARE-UNSHARE-ACCEPTED ·
         CANARY-SUCCESS-ACCEPTED · RULES-DIGEST-UNPINNED · RULES-DIGEST-RECORDED-UNBOUND · DNS-CANARY-DROPPED ·
         UNIT-SET-EMPTY-PASSES · DEFERRED-AS-PASS · FIFO-HANG · DETAIL-UNCHECKED-vocabulary ·
         DETAIL-UNCHECKED-foreign-target · GATE-INERT-ACCEPTED · NOT-RUN-UNIT-COUNTED · NETNS-LEAK ·
         LOOPBACK-ALIAS-ACCEPTED · PASS-RATIO-COUNTS-RECORDS · COUNTER-READS-DROP-ONLY ·
         VE1-IPV4-RANGE-UNCHECKED · VE1-NAN-ACCEPTED-IN-CANARIES · VE1-UNIT-FIELD-UNCHECKED · VE1-BOOL-IS-INT ·
         VE1-DECLARED-ABSENT-BUT-PRESENT-OK · VE1-REQUIRED-UNITS-IGNORED · VE1-RESOLVE-PATTERN-DROPPED ·
         VE1-C4-NOT-RECORDED · VE1-GATE-STATE-ALWAYS-ENABLED · VE1-MECHANISM-ALWAYS-VETH ·
         VE1-RESOLVER-COLLIDES-WITH-ALLOWED · VE1-EXPECTED-RULES-DROPS-FORWARD-POLICY
SURVIVED PASS-RATIO-TAUTOLOGY (the lane's declared equivalent — AGREED, proof in item 6)
         VE1-DROP-BEFORE-DEFAULTS-TO-ZERO            → F3, a real coverage hole
         VE1-OCTET-CONSTANT(ns-collision)            → F6, a real design weakness
         VE1-EMIT-SCRUB-LOSES-NO_PROXY-ALL_PROXY     → defence-in-depth (two scrub layers + the vocabulary rule)
         VE1-COLLECTOR-SCRUB-LOSES-NO_PROXY          → same
         VE1-CONNECT-PROBE-UNREACHABLE-SET-WIDENED   → near-equivalent: `_fail`'s fallthrough already returns 7
```

The brief's seven named extras are all covered: stray-counter (item 2), reordered rules (item 3), target-and-proxy
detail (item 4), forged `resolved` field (item 4), C0 to a non-allow-listed listener (item 5), namespace name collision
(item 7 + `VE1-OCTET-CONSTANT`), routed-variant sanity (item 1b).

---

## FINDING INVENTORY — no severity filter

### F1 — BLOCKER — a totally isolated namespace (the AF-AP-1 class) produces a PASSING bundle: `gate["mechanism"]` is required and never asserted

* **Evidence level:** reproduced, twice, through the real collector and the real checker at the PIN. SOLID.
* **Contract:** `seeds/seed-stage0-v1.yaml:434` — `fails with the exact denial reason (negative leg) — bare unshare is proven total-block`
  and `seeds/seed-stage0-v1.yaml:435` `and is NOT acceptable evidence'`;
  the lane brief's "Bare `unshare --net` is TOTAL isolation and is NOT acceptable evidence (AF-AP-1)"; `C:21` the
  checker's own docstring — `that is what bare `unshare --net` looks like (AF-AP-1,`; the report's A1 and D7.
* **file:line:** `C:78` `GATE_KEYS = ("gate", "mechanism", "netns", "unit", "allowed", "rules_sha256")` requires the key;
  `C:174` `def read_gate(unit_dir, unit):` checks presence only; nothing in `check()` ever reads its VALUE.
  `L:149` `egress_ns_mechanism() {` computes it truthfully and `R:114` `MECHANISM=$(egress_ns_mechanism "$NS")` records
  it, so the guard is emitted and never fires.
* **Expected vs observed.** Expected: a bundle whose namespace has no veth can never be S0-05 evidence. Observed, on a
  namespace created by the library's own `egress_ns_create_isolated` with the brief's literal `127.0.0.1:<port>` allowed
  form, the stand-in on the namespace's own loopback and one internal veth pair (both ends inside — still zero
  connectivity off the namespace):

  ```
  mechanism: netns-no-veth   gate: enabled   links in ns: lo ve1b@ve1a ve1a@ve1b
  veth pairs anywhere on the host: []
  gate-fired: curl OUTPUT policy DROP 0 -> 5 packets
  PASS: S0-05 no-direct-egress - 1 units, 11 canaries failed as required, positive controls 1/1     rc=0
  ```

  Without the internal pair the same bundle is stopped — but by `gate-inert` (counters `0 -> 0`), not by the positive
  control and not by the mechanism. So the AF-AP-1 defence today is the drop counter alone, and one on-link address
  inside the namespace defeats it.
* **Cheapest red control (a one-field patch of committed evidence):** copy
  `proofs/S0-05/fixtures/evidence-mechanism-sandbox`, set `gate.json` `"mechanism": "netns-no-veth"`, run the checker →
  **rc 0, `PASS …`** at the PIN.
* **Minimal fix (measured on a scratch copy, 06:44:50Z).** In `check()`, immediately after
  `C:334` `positives += check_positive_control(records, unit)`:

  ```python
  if gates[unit]["mechanism"] != "veth-iptables":
      raise Failure(f"total-isolation: {unit} mechanism="
                    f"{gates[unit]['mechanism']!r} is not selective egress")
  ```

  With it: the red control → `rc=1 total-isolation: curl mechanism='netns-no-veth' is not selective egress`; the live
  isolated bundle → the same; `evidence-mechanism-sandbox` rc 0, `evidence-synthetic-pass` rc 0 (2 units),
  `evidence-gate-off` rc 1 `egress-permitted: gate-disabled`, `evidence-bare-unshare` rc 1 `positive-control-failed: curl`
  (placing the check AFTER the positive control keeps `spec.json`'s declared `failure_reason` intact); the whole suite
  `98 passed in 4.05s`.
* **Predicate:** contract-mapped ✔ · reproduced through the production consumer and producer at the PIN ✔ · material
  (a PASS on evidence the seed declares inadmissible) ✔ · concrete discriminator, red control and corrected
  implementation both pasted ✔ · in-boundary (`check_egress.py` + one test) ✔.
* **Honest caveat:** the demonstrating topology is operator-supplied. The shipped scripts alone do not build it, and the
  PC runner's `PC:89` `if ! egress_ns_run "$ns" curl -sS --connect-timeout 5` preflight would abort a unit whose allowed
target is unreachable. What the finding falsifies is the
  CHECKER's claim to reject the class, not a live green on the PC today.

### F2 — FOLLOW-UP — `gate-fired` is namespace-and-window scoped, not attributed to any canary
`C:276` `if after <= before:` is the entire rule; a delta of 1 passes. A stray process inflated the recorded evidence to
`0 -> 400010` through the REAL collector and the checker still passed. A9's "the gate actually FIRED" is true; "the gate
blocked the canaries" is not proven. **Fix:** bracket each gate-decided canary individually (read the counter around C5
and C6 and record per-canary deltas), or add a dedicated `-A OUTPUT -d <blocked> -j DROP` rule with its own counter.
**Red test:** a bundle whose only gate-decided canary is deleted but whose delta is large must not pass.

### F3 — FOLLOW-UP — the class-6 `DROP_BEFORE` fix at `R:69` `DROP_BEFORE=$(egress_ns_drop_counter "$NS")` and `R:72` has no discriminating red test
Mutant `VE1-DROP-BEFORE-DEFAULTS-TO-ZERO` replaces `R:72` with `DROP_BEFORE=${DROP_BEFORE:-0}` and the whole suite stays
green (`98 passed`), because `T:579` `def test_the_collector_refuses_an_unreadable_drop_counter(tmp_path):` is satisfied
by the surviving twin guard at `R:107` `[ -n "$DROP_AFTER" ] ||`. The report's §6 claim that the six production defects were "all fixed in this
lane with a test each" does not hold for this one. Reachable in practice when the FIRST read fails and the second
succeeds (an `iptables` xtables-lock contention between the two reads on a busy PC). **Fix:** a test that stubs a
counter reader returning empty only on the first call, or assert the exact stderr string is produced by the
`R:72` `[ -n "$DROP_BEFORE" ] || { echo "run_canaries: cannot read the OUTPUT DROP counter of $NS" >&2; exit 3; }` site. **Red test:** run the collector with `egress_ns_drop_counter` shadowed to print nothing once.

### F4 — FOLLOW-UP — `_foreign_endpoint_in_detail` inspects only the FIRST regex match
`C:116` `for pattern in (CURL_CONNECT, CURL_RESOLVE):` calls `.search()`, so a detail that names its own target first and
a foreign endpoint second PASSES (measured). Amplified by `proofs/S0-05/canaries/_emit.sh:22` `"detail": " ".join(detail.split())[:300]}` — a 300-char
truncation can cut the foreign name off a long detail. Not reachable from a real `curl`/`connect_probe` diagnostic at the
PIN, so this is hardening of THE discriminator the report calls load-bearing. **Fix:** `finditer` over both patterns and
reject if ANY named endpoint is foreign. **Red test:** the two-endpoint detail above must exit 1.

### F5 — FOLLOW-UP — C0's target is not bound to the declared allow-list
`C:214` `def check_positive_control(records, unit):` never compares `record["target"]` with `gate["allowed"]`; C0 against
`10.201.38.1:19999` or api.openai.com port 443 passes. Seed A1 is "the unit CAN reach its allowed target"; the checker proves
"reached something with a 2xx". Bound by construction through `R`, so checker-completeness only. **Fix:** one condition in
`check_positive_control`. **Red test:** the rewritten-target bundle must exit 1.

### F6 — FOLLOW-UP — the address plan has 254 buckets; two namespaces can silently share a /24
`L:44` `_egress_octet() {` / `L:47` `printf '%d\n' $(( n % 254 + 1 ))`. Measured on a real colliding pair: both
`egress_ns_create` calls returned **0**, two host interfaces carried `10.201.115.1/24`, and a connect from the second
namespace to that address timed out — i.e. one unit's positive control breaks with no error anywhere. Three concurrent
units collide with p ≈ 1.2 %; the current PC triple is safe (107/219/153) but a renamed or added unit re-rolls it.
**Fix:** derive the octet from a registry/counter, or refuse to create when the /24 is already assigned
(`ip -4 addr show | grep -q "$host_ip/"` → return 1 with a named reason). **Red test:** create two colliding namespaces
and assert the second call fails loudly.

### F7 — FOLLOW-UP — `egress_ns_destroy` leaves a live namespace behind, invisible to the census
Measured: with a process inside, destroy returns 0, `ip netns list` is empty, the veth and `/etc/netns/<ns>` are gone,
and the process remains in `net:[4026532283]`. `L:207` `ip netns del "$ns" 2>/dev/null || true` only unlinks the name.
Every census in the report and in `test_library_round_trip_leaves_no_namespace_behind` is blind to it. **Fix:** before
destroying, read `ip netns pids "$ns"` and either refuse or kill those pids by pid; report the residue. **Red test:**
start a sleeper inside, destroy, assert `ip netns pids` is empty or that destroy returned non-zero.

### F8 — FOLLOW-UP — the PC runner launches a bash script under `python3`
`PC:103` `egress_ns_run "$ns" setsid /usr/bin/python3 ${LAUNCH[$unit]} </dev/null \` versus `PC:56`
`LAUNCH[s0-01-backend]="$S0_01_TOOLS/pc_backend_restart.sh"` (a `#!/usr/bin/env bash` script). The unit dies instantly and
is recorded `not-run`. **Fix:** launch through the file's own interpreter (`setsid "$@"` on an argv array, or `bash` for
`.sh`). **Red test:** none possible in the sandbox; a `bash -n`-level assertion that each `LAUNCH` value's extension
matches its interpreter would catch it.

### F9 — FOLLOW-UP — `setsid` + `$!` liveness in the PC runner
`PC:103`/`PC:124` `[ -n "$launch_pid" ] && kill "$launch_pid" 2>/dev/null || true` track the wrapper. If `setsid` forks,
`$!` dies immediately and a healthy unit is declared `not-run`; if it does not, the later `kill` may leave a grandchild
inside the namespace, which is exactly F7's invisible residue. **Fix:** `setsid --fork` plus a pidfile written by the
unit, or read `ip netns pids "$ns"` for liveness.

### F10 — FOLLOW-UP — the S0-01 scripted backend is not containable as designed
It binds `--bind 127.0.0.1 --port 20201`; inside a fresh namespace that loopback is the namespace's own, so OmniRoute in
the host namespace can no longer reach it. The `s0-01-backend` unit in `PC:55`-`PC:56` cannot be contained without a bind
change or a DNAT — the same class the file already names for OmniRoute at `PC:25` `# PREFLIGHT, not a workaround: if OmniRoute (or the Buzz relay) is bound to 127.0.0.1 on the PC,`.

### F11 — FOLLOW-UP — `R:30` `VENUE=${6:-sandbox}` can mislabel a PC bundle
A five-argument hand invocation on the PC stamps `"venue": "sandbox"`; the checker requires the key and never validates
it. This is the field the lane's SELF-ATTACK 3 relies on. **Fix:** make the venue required (`${6:?venue}`) or validate it
against a declared set. **Red test:** a bundle whose `runtime.json` venue is not in `{sandbox, pc, synthetic}` must exit 1.

### F12 — FOLLOW-UP — the allow-list is pinned to itself, never to `docs/05_SECURITY.md` §6
A widened allow-list with a self-consistent digest and rule list PASSES (measured). `C:283` `if rules_digest(expected_rules(gate["allowed"])) != gate["rules_sha256"]:`
closes the loop inside the bundle only, and
`C:352` `parser.add_argument("--units", default="curl",` is the only unit-side pin — there is no `--allowed`. **Fix:** an
`--allowed` argument (or a per-unit allow-list in `spec.json`) that the recorded `gate.allowed` must equal.

### F13 — INFO — the `resolved` field is recorded and never read
Forging it to `127.0.0.1` on every C1 changes no verdict. It is venue evidence (D6b), not a discriminator; say so, or
bind it (a C1 whose `resolved` is loopback while the target is a provider is a venue fact worth failing on).

### F14 — INFO — the `127.` floor at `C:114` is venue-specific
`if isinstance(candidate, str) and not candidate.startswith("127."):` assumes the ambient proxy is on loopback. A denial
naming a LAN proxy (`10.0.0.5 port 3128`) with a matching forged `ip` PASSES; without the forged `ip` it is caught. The
lane already says both venue facts must be re-measured on the PC (D6); this names the concrete consequence.

### F15 — INFO — the report's D4 sentence over-generalises
D4 says C1 "(for two of three hosts)" fails with `[Errno 101] Network is unreachable`. Measured here: C1 for
api.openai.com and generativelanguage.googleapis.com fails rc 6 `Could not resolve host`; only C2/C3/C4 carry `[Errno 101]`.
The conclusion D4 draws is unaffected.

### F16 — INFO — the report's §6 class-10 row undercounts the root-gated tests
It says 3; there are 4 `@NEEDS_NETNS` tests — `T:653` `def test_library_round_trip_leaves_no_namespace_behind():`, `T:680` `def test_the_drop_counter_reads_both_policies():`, `T:703` `def test_the_isolated_control_has_no_veth_and_fails_its_positive_control():` and `T:723` `def test_the_canary_emitter_scrubs_the_proxy_environment():` — which is exactly the PC's 4 skips.

### F17 — INFO — an exit-3 collection leaves an empty `<unit>/canaries.jsonl` behind
`R:36` `OUT="$EVIDENCE_ROOT/$UNIT"` and `R:39` `: > "$JSONL"` run before the `R:72` `[ -n "$DROP_BEFORE" ] ||` guard. Fail-closed at the checker
(`evidence-missing: curl gate.json absent at …`, rc 1), so this is hygiene — the same shape as the class-18c incident.
**Fix:** read the counter before creating the directory.

### F18 — INFO — `--units ""` empties the required-unit set
`check_egress.py <root> --units ""` passes with whatever single unit happens to be present. `spec.json` never passes it,
so it is a CLI surface only. **Fix:** reject an empty `--units`.

### F19 — INFO — `_egress_apply_gate` validates the port but not the IP
`10.0.0.1/8:443` is accepted by the library (the case pattern only rejects a non-numeric port) and would install an
`-d 10.0.0.1/8` ACCEPT. The checker's `IPV4_PORT` regex backstops it (`gate-manifest-invalid`), so it is fail-closed end
to end; the library should still reject it at the source.

### F20 — INFO — the `AF-AP-72` screen hit is SAFE, classified by running
`proofs/S0-05/canaries/connect_probe.py:48` `mode, ip, port, timeout = argv[0], argv[1], int(argv[2]), float(argv[3])`. Measured: a non-numeric port or
timeout raises `ValueError`, the probe exits **1** with an EMPTY stdout detail; too few args or an unknown mode exits
**9**. Both go through the real checker as `denial-rc-unrecognized: curl C2 rc=1` / `rc=9`, rc 1 — the collector can
never read a crashed probe as a denial. In the shipped path both values are literals, so the hit is unreachable anyway.

### F21 — INFO — the two `probe.sh` MISSes are a lint-token convention, not wrong citations
`report_lint` wants a backticked identifier from the cited line on the same report line; the E1 report's lines 100 and 103
carry identifiers from `netns_lib.sh` instead. The citations themselves are right. `probe.sh:50` `ip netns exec "$NS" iptables -P OUTPUT DROP` opens the rule block that
`_egress_apply_gate` lifts. `probe.sh:26` `cleanup() {` opens the five-line trap body (through its closing brace on line
31) that `egress_ns_destroy` lifts.

### F22 — INFO — three of the six mutation survivors are equivalent or defence-in-depth
`PASS-RATIO-TAUTOLOGY` is a proved equivalent (item 6). The two scrub-list mutants survive because the scrub exists in
TWO layers — `R:42` `SCRUBBED="HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY http_proxy https_proxy all_proxy no_proxy"` and
`proofs/S0-05/canaries/_emit.sh:11` `EGRESS_SCRUBBED_ENV="HTTP_PROXY HTTPS_PROXY ALL_PROXY NO_PROXY http_proxy https_proxy all_proxy no_proxy"`
— and `C:101` `def _foreign_endpoint_in_detail(record):` rejects a proxy-shaped denial even
with no scrub at all. `VE1-CONNECT-PROBE-UNREACHABLE-SET-WIDENED` survives because `_fail`'s unclassified fallthrough
already returns 7. The test gap worth closing is narrow: `T:723` `def test_the_canary_emitter_scrubs_the_proxy_environment():` pins only two of the eight proxy variables.

### F23 — INFO — two concurrent PC-runner invocations tear down each other's namespaces
`PC:82` `ns="s0-05-$unit"` is a fixed name and `L:76` `egress_ns_destroy "$ns"` runs first inside `egress_ns_create`.

### F24 — INFO — the reorder question, answered
An order-insensitive comparison is unnecessary (both sides already canonicalise by sorting) and would be a regression
(a duplicated rule, today an `egress-rules-unpinned` red, would be masked by set equality). Keep the digest as it is.

---

## What I reproduced, reviewed, and deliberately skipped

**Reproduced (real scripts, real namespaces, real checker, at the PIN):** the three bundle shapes and D4 · the routed
variant · the gate-fired counter attacks · the cross-language digest · the whole denial-vocabulary battery · the
positive-control attacks · the units-manifest battery · destroy-with-a-live-process · the /24 collision · the collector's
exit-3 guard · the not-run DEFER · 37 mutants · the F1 blocker and its fix · the PC pytest gate.
**Reviewed statically only:** `PC` `run_s0_05_units.sh` in full (never executed — F8, F9, F10, F11, F23 are static
findings against a file the lane itself declares NOT run), and the S0-01 launch targets it calls.
**Deliberately skipped:** any live unit on the PC (no bridge action beyond the sanctioned pytest gate); `runsc`/gVisor
interaction (out of boundary, already declared NOT run by the lane); IPv6 (the lane declares the mechanism IPv4-only and
`test_a_malformed_allow_entry_is_rejected` pins it); re-verification of `report_lint.py`/`ap_screen.py` themselves (report
machinery, unchanged by this increment).

## Shared-tree hygiene and the exit census (2026-09-22T06:45Z)

Every mutant and every bundle lived under the session scratchpad; the shared tree was never `git add`ed, stashed,
checked out or committed, and `git status --porcelain` was empty. Namespaces created here were named `s0-05-ve1-*` and
destroyed BY NAME in traps; one `s0-05-e1-4adac109` left by the lane's own test under the `NETNS-LEAK` mutant (whose
point is a no-op destroy) was removed by exact name at 06:33:07Z. All listeners were killed by pid; no `pkill -f` was
used. The host `FORWARD` rule added for the routed variant was removed (`-P FORWARD ACCEPT`, no rules).

---

## Item 14 — the design answer

**Three sentences, from the D4 measurement.** With the shipped unrouted mechanism the seed's second assertion is
provable only in the weak sense "the contained unit has exactly one reachable destination": every model-endpoint canary
fails because the namespace has no route off its own /24, and it produces the byte-identical record with the gate on and
with the gate flushed, so it carries no information about the firewall at all. The routed variant moves C1–C4 onto the
firewall — measured here: with a default route through the veth host end the OUTPUT policy eats the SYN and C2/C3/C4
fail as `rc 28 TimeoutError timed out`, and the resulting bundle PASSES the checker with zero checker changes — but a
dropped SYN and an unanswered route both read as `rc 28`, so routing alone still does not discriminate; the only leg that
does is a destination that WOULD answer, which is what the routed `198.51.100.7:443` listener demonstrated by flipping
`rc 28` → `rc 0 connected` across the gate. **So:** the seed does not need the routed variant to support a CONTAINMENT
claim (one reachable destination is strictly stronger than a firewall rule), but it does need the routed variant PLUS an
answering stand-in at the model address before any claim of the form "the iptables gate blocks api.openai.com" is
evidence — the cheapest honest resolution is to keep this mechanism and state the seed's second assertion as the
containment property the evidence supports, adding the routed+stand-in leg only if the model-endpoint-specific wording
is wanted.

### The exact PC steps for the live-unit legs (owner-run; not run here)

1. `sudo` as the owner; confirm `id -u` is 0 for the run (the library refuses otherwise — `L:57`).
2. Fix F8 first (`PC:103` must not run `pc_backend_restart.sh` under `python3`) and decide F10 (the scripted backend
   binds `127.0.0.1:20201`; either drop `s0-01-backend` from `UNITS` or rebind it on the veth host address).
3. Read OmniRoute's bind address. If it is `127.0.0.1:20128`, no namespace can reach it: either rebind on the veth host
   address that `egress_ns_host_ip s0-05-hermes-acp` prints (`10.201.107.1`), or add a host-side DNAT for it. The
   runner already aborts with `positive-control-unreachable` and names both fixes — do not stub it.
4. Export the allow-lists from the docs/05 §6 row per unit: `ALLOWED_HERMES=<omniroute address and port 20128>`,
   `ALLOWED_BUZZACP=<relay ip:port>`; leave `ALLOWED_BACKEND` unset if F10 is deferred (the unit is then recorded
   `not-run` with its reason, never a green).
5. Check the three /24s are free on the PC before the run (F6): `ip -4 addr show | grep -E '10\.201\.(107|219|153)\.'`
   must be empty — podman and the relay stack own other ranges, but verify rather than assume.
6. `bash proofs/S0-05/tools/pc/run_s0_05_units.sh /home/rocco/s0-05-evidence hermes-acp buzz-acp` from the repo root on
   the PC, in ONE foreground call; it prints `units.json` and runs the checker itself.
7. Afterwards: `ip netns list`, `ip -o link show type veth`, `ls -A /etc/netns` and `ip netns pids s0-05-<unit>` for each
   unit (F7 — the last one is the census the lane's own test cannot see).
8. Re-measure the two venue facts on the PC before believing any denial: the ambient proxy variables and `/etc/hosts`
   (D6a/D6b are sandbox facts, not PC facts).

---

## Item 13 — discipline, the lint on THIS report, and the exit census (2026-09-22T06:51Z)

Every `file:line` above was read with `sed -n` on a `git archive 5c2392e` copy. `report_lint.py` on this report, the
five brief maps plus the `probe.sh` map, at `--rev 5c2392e`, after a bounded three-round fix pass:

```
report_lint: 104 refs — OK 102, NEAR 0, MISS 0, UNCHECKABLE 2, UNRESOLVED 0 (at 5c2392e)
```

**MISS 0.** The two UNCHECKABLE are the two lines of verbatim `ap_screen.py` output pasted inside the item-0 fenced
block — tool output, not claims of mine, so they carry no claim token by construction.

Exit census, pasted:

```
$ ip netns list            -> (no output)
$ ip link show type veth   -> (no output)
$ ls -A /etc/netns         -> (no output)
$ ss -ltnp | grep -E '12800|12801|198\.51\.100'   -> (no output)
$ ps -eo pid,args | grep -F 'srv.py'                -> (no output)
$ iptables -S FORWARD      -> -P FORWARD ACCEPT        (my routed-variant rule removed)
$ ip -4 addr show | grep -c '198.51.100.7'           -> 0
$ git status --porcelain   -> ?? tasks/briefs/s0-05-support/VERIFY-E1-report.md   (this file, untracked, never staged)
```

---

## BLOCKING SET

**F1** — `check_egress.py` requires `gate["mechanism"]` and never asserts it, so a totally isolated namespace (the
AF-AP-1 class the seed declares inadmissible) produces a PASSING S0-05 bundle. Reproduced through the real collector and
the real checker at the PIN; red control = a one-field patch of a committed fixture; corrected implementation measured
(all four spec legs and all 98 tests still green).

Everything else in the inventory (F2–F24) is non-blocking residue for the coordinator to file as `verify-followup`.

GATE RECOMMENDATION: NOT-READY
