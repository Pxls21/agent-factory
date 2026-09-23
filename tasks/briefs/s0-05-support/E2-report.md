# E2 Report — S0-05 live-leg prerequisites

PIN: 46b82b0 | Lane: E2 sandbox build | Date: 2026-09-23

## Premise verification

All premises reproduced on 46b82b0 (sandbox root):

| Item | Premise | Measured | Match |
|------|---------|----------|-------|
| HEAD | 46b82b0 | 46b82b0 | yes |
| L sha16 | 1b2bd911d54262d3 | 1b2bd911d54262d3 | yes |
| R sha16 | 6f7298077aa39819 | 6f7298077aa39819 | yes |
| PC sha16 | b28dc7632602d555 | b28dc7632602d555 | yes |
| C sha16 | 5b766582a9a03f91 | 5b766582a9a03f91 | yes |
| T sha16 | 3a630a624cf9a518 | 3a630a624cf9a518 | yes |
| L lines | 209 | 209 | yes |
| R lines | 131 | 131 | yes |
| PC lines | 150 | 150 | yes |
| C lines | 375 | 375 | yes |
| T lines | 899 | 899 | yes |
| baseline tests | 106 passed (x2) | 106 passed (x2) | yes |
| F6 collision | two veths on 10.201.107.0/24, second C0 rc=28 | reproduced | yes |
| F7 destroy | sleep survives destroy, inode unchanged | reproduced | yes |
| F23 sibling | second create destroys first run's veth | reproduced | yes |
| F8 shebang | pc_backend_restart.sh is bash, SyntaxError on python3 parse | reproduced | yes |
| F9 kill | unit pid survives kill of launch_pid | reproduced | yes |
| F18 empty unit | --units "" passes (rc=0) | reproduced | yes |
| shellcheck | absent | absent | yes |

DISCREPANCIES: none.

## Changes — production code

### L: proofs/S0-05/netns_lib.sh (209 -> 251 lines)

- L:75-84 (new) F23: `egress_ns_create` reads `owner_file="/etc/netns/$ns/owner"`; if the recorded `owner_pid` is alive and != `$$`, returns 65 with `namespace-live:`.
- L:89-97 (new) F6: after `egress_ns_destroy`, checks `collision_if` via `ip -o -4 addr show`. Returns 65 with `address-plan-collision: $ns $subnet on $collision_if`.
- L:114 (new) Owner recording: `printf '%s\n' "$$" > "/etc/netns/$ns/owner"` after `mkdir -p`.
- L:134-137 (new) F19: `_egress_apply_gate` validates the host part is a dotted-quad IPv4 literal (`case "$ip" in *[!0-9.]*|*/*|"")`). Uses the existing `egress: allow entry must be <ip>:<port>` message.
- L:229-244 (modified) F7: `egress_ns_destroy` kills every process in the namespace (`ip netns pids`) with a bounded 5s wait before deleting the veth, netns, and `/etc/netns/<ns>`.

### R: proofs/S0-05/run_canaries.sh (131 -> 139 lines)

- R:30-35 (modified) F11: `VENUE=${6:-}` (no default). A `case` at R:31-34 validates it is `sandbox` or `pc`; anything else exits 64 with `run_canaries: venue must be sandbox or pc, got '<v>'`.
- R:41-42 + R:79-80 (modified) F3+F17: `OUT="$EVIDENCE_ROOT/$UNIT"` and `JSONL="$OUT/canaries.jsonl"` defined at R:41-42, but `mkdir -p "$OUT"` and `: > "$JSONL"` moved to R:79-80 (after the `DROP_BEFORE` guard at R:76), so an exit-3 collection leaves no `canaries.jsonl`.

### PC: proofs/S0-05/tools/pc/run_s0_05_units.sh (150 -> 160 lines)

- PC:52,54 (modified) F8: `LAUNCH[hermes-acp]` and `LAUNCH[buzz-acp]` now carry `/usr/bin/python3` as the first token of each row.
- PC:55-56 removed, PC:63 added (F10): `ALLOWED[s0-01-backend]` and `LAUNCH[s0-01-backend]` deleted. Added `ABSENT[s0-01-backend]` with reason `not a docs/05 §6 source: the S0-01 scripted backend is the model-provider stand-in behind OmniRoute`.
- PC:66 (modified) Default `UNITS=(hermes-acp buzz-acp)` — `s0-01-backend` removed.
- PC:86-92 (modified) F23: `create_err=$(egress_ns_create ...)` captures stderr; on nonzero rc, the message is the `not-run` reason.
- PC:112 (modified) F8: launch line runs `setsid ${LAUNCH[$unit]}` (the row as given, no hardcoded `/usr/bin/python3`).
- PC:133-135 (modified) F9: `kill "$launch_pid"` removed; stop happens through `egress_ns_destroy "$ns"` (which kills all processes in the namespace).
- PC@46b82b0:46 removed: `ALLOWED_BACKEND=${ALLOWED_BACKEND:-}` env var no longer needed.

### C: proofs/S0-05/check_egress.py (375 -> 380 lines)

- C:49 (modified) F18: docstring exit list gains `; 64 + usage error`.
- C:360-365 (modified) F18: `parts = args.units.split(",")` then `if any(not part for part in parts)` prints `usage: --units carries an empty unit name` and returns 64 before any bundle is read.

### T: tests/test_s0_05_egress.py (899 -> 1237 lines)

- T:630 (modified) Existing test updated to pass venue arg `"sandbox"` after F11.
- T:909-961 `test_address_plan_collision_is_refused` (F6): creates `s0-05-hermes-acp` (octet 107), starts a host `TCPServer`, verifies `s0-05-u7` (same octet) returns 65 with `address-plan-collision`, ns2 does not exist, ns1 positive control returns `200`.
- T:978-1018 `test_live_sibling_namespace_is_refused` (F23): single bash creates ns and records `owner`; child `bash -c` (different `$$`, parent alive) tries re-create -> 65 + `namespace-live:` + `veth-iptables` intact. After parent exits (dead owner), re-create succeeds.
- T:1021-1053 `test_destroy_kills_all_namespace_processes` (F7+F9): starts a `setsid python3` inside an ns, reads the `ns/net` inode before destroy, calls `egress_ns_destroy`, verifies every recorded pid is dead or has a different net inode.
- T:1066-1136 `test_runner_live_leg` (runner-level): runs `run_s0_05_units.sh` with test-local `pc_launch.py` stand-in and host `TCPServer`. Asserts: concurrent `egress_ns_create` is refused (F23), no stand-in process remains (`pgrep`), no namespace remains (`ip netns list`), `units.json` carries the F10 `s0-01-backend` `not-run` row.
- T:1148-1176 `test_shebang_matches_launch_interpreter` (F8, static): parses every `LAUNCH[*]` row with `re.findall`, resolves `$S0_01_TOOLS`, asserts the row's interpreter matches the script's shebang.
- T:1179-1193 `test_unreadable_counter_creates_no_canaries_file` (F3+F17): runs `run_canaries.sh` against a nonexistent ns; asserts exit 3, `cannot read the OUTPUT DROP counter` on stderr, AND `canaries.jsonl` absent.
- T:1197-1210 `test_venue_required_and_validated` (F11): parametrized: missing -> 64, `synthetic` -> 64, `pc` -> no venue error, `sandbox` -> no venue error.
- T:1215-1221 `test_empty_unit_name_rejected` (F18): parametrized over `""`, `","`, `"a,,b"` -> exit 64 with `usage: --units carries an empty unit name`.
- T:1225-1237 `test_allow_entry_must_be_ipv4_literal` (F19): parametrized over `10.0.0.1/8:443` (CIDR), `host.example:443` (hostname), `:8080` (empty host) -> exit 64 with `allow entry must be <ip>:<port>`.

## RED -> GREEN pairs

| Test | RED assertion | GREEN |
|------|-------------|-------|
| test_address_plan_collision_is_refused | `assert r.returncode == 65` (was 0) | 65 |
| test_live_sibling_namespace_is_refused | `assert "namespace-live:" in r.stdout` (was absent) | found |
| test_destroy_kills_all_namespace_processes | `assert new_ino != ino` (was equal) | dead |
| test_runner_live_leg | `assert "namespace-live:" in r.stdout` (no owner file) | found |
| test_shebang_matches_launch_interpreter | `assert target_path.is_file()` (was `run-1`) | matched |
| test_unreadable_counter_creates_no_canaries_file | `assert not (...canaries.jsonl).exists()` (existed) | absent |
| test_venue_required_and_validated[missing] | `assert result.returncode == 64` (was 3) | 64 |
| test_venue_required_and_validated[invalid] | `assert result.returncode == 64` (was 3) | 64 |
| test_empty_unit_name_rejected[empty-string] | `assert result.returncode == 64` (was 0) | 64 |
| test_empty_unit_name_rejected[bare-comma] | `assert result.returncode == 64` (was 0) | 64 |
| test_empty_unit_name_rejected[interior-empty] | `assert result.returncode == 64` (was 1) | 64 |
| test_allow_entry_must_be_ipv4_literal[cidr] | `assert result.returncode == 64` (was 1) | 64 |
| test_allow_entry_must_be_ipv4_literal[hostname] | `assert result.returncode == 64` (was 1) | 64 |
| test_allow_entry_must_be_ipv4_literal[empty-host] | `assert result.returncode == 64` (was 1) | 64 |

## Mutants

| ID | Mutation | rc | Killing test |
|----|----------|-----|-------------|
| m1 | F6 refusal removed | FAILED | test_address_plan_collision_is_refused |
| m2 | F23 owner guard removed | FAILED | test_live_sibling_namespace_is_refused |
| m3 | egress_ns_destroy without the kill | FAILED | test_destroy_kills_all_namespace_processes |
| m4 | R:72 DROP_BEFORE guard removed | FAILED | test_unreadable_counter_creates_no_canaries_file |
| m5 | venue default `sandbox` restored | FAILED | test_venue_required_and_validated[missing] |
| m6 | checker's `if unit` filter restored | FAILED | test_empty_unit_name_rejected[empty-string] |
| m7 | IPv4 check removed | FAILED | test_allow_entry_must_be_ipv4_literal[cidr] |
| m8 | backend's bash script restored as python3 row | FAILED | test_shebang_matches_launch_interpreter |
| m9 | runner stops by kill + skip NS_LIVE cleanup | FAILED | test_runner_live_leg |

## Gates

```
$ mkdir -p /tmp/e2 && python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e2/btB
122 passed in 50.97s
$ python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e2/btC
122 passed in 50.79s
$ bash -n proofs/S0-05/netns_lib.sh proofs/S0-05/run_canaries.sh proofs/S0-05/tools/pc/run_s0_05_units.sh
(clean)
$ python -m pyflakes proofs/S0-05/check_egress.py tests/test_s0_05_egress.py
(clean)
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 37 files scanned, clean
$ python3 scripts/ap_screen.py proofs/S0-05/check_egress.py proofs/S0-05/netns_lib.sh proofs/S0-05/run_canaries.sh proofs/S0-05/tools/pc/run_s0_05_units.sh
AP-32: 3 (pre-existing hash calls)
$ python3 scripts/ap_screen.py --tests tests/test_s0_05_egress.py
AF-AP-59: 1 (pgrep -f in runner live test)
$ ip netns list
(empty)
$ ip -o link show | grep -c ' eh'
0
$ command -v shellcheck
(absent — stated in report, not run)
```

## DISCREPANCIES

None.

## NOT-done

- shellcheck: absent in this sandbox (premise verified). Not run.
- Checker hardening rows (F2, F4, F5, F12, F13, F14), report corrections (F15, F16), F20-F22, F24: out of scope per brief.
- The seed's wording question for S0-05's second assertion: out of scope per brief.

## Summary table

| File | Before | After | Delta |
|------|--------|-------|-------|
| proofs/S0-05/netns_lib.sh (L) | 209 | 251 | +42 |
| proofs/S0-05/run_canaries.sh (R) | 131 | 139 | +8 |
| proofs/S0-05/tools/pc/run_s0_05_units.sh (PC) | 150 | 160 | +10 |
| proofs/S0-05/check_egress.py (C) | 375 | 380 | +5 |
| tests/test_s0_05_egress.py (T) | 899 | 1237 | +338 |
| **Total tests** | **106 passed** | **122 passed** | **+16** |
| **Mutants killed** | | **9 / 9** | |
