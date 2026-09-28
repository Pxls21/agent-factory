# VERIFY-I59-F report (task #335): the proof-code follow-ups, attacked before the owner's re-sign

Written 2026-09-28 17:0xZ onward by the sandbox verify lane (adversarial-verifier, Opus 5.5), incrementally. No
subagent, no PC bridge, no outward action, no git write outside `/tmp/vf-wt`.

STATUS: DONE (18:0xZ). Gate: MERGE-READY-WITH-FOLLOWUPS; see GATE and the pre-re-mint list at the end.

Aliases (patched bytes in `/tmp/vf-wt` unless written `alias@c9889ee:NN`):
C = `proofs/S0-03/check_omniroute_roundtrip.py`, T3 = `tests/test_s0_03_omniroute.py`,
R = `proofs/S0-05/tools/pc/run_s0_05_units.sh`, T = `tests/test_s0_05_egress.py`,
CC = `proofs/S0-04/check_compression.py`, T4 = `tests/test_s0_04_compression.py`,
GW = `tests/test_gpu_window.py`, W = `.github/workflows/stage0-ci.yml`, NL = `tests/test_no_laya_in_gates.py`,
CE = `proofs/S0-05/check_egress.py`.

## Premise (re-measured 17:0xZ)

- origin/claude/soundbox-kit-migration-iz1jwf = a1a639b; `git diff --stat c9889ee a1a639b -- proofs tests scripts
  harness-ports .github` is empty, so the copy's base is origin's bytes for those roots.
- `tasks/briefs/i59/I59-F.patch` sha256 `dc64a3f5853b48d8`, 9 `diff --git` lines; `git apply --check --stat`:
  `9 files changed, 1031 insertions(+), 65 deletions(-)`. Brief `591b7f0bf2c727df`, report `a9f1c311a608af25`.
- Copy: `/tmp/vf-wt`, a `git archive c9889ee proofs tests scripts harness-ports .github` (42,792,960 bytes), `git init`,
  one commit 013437b (`core.hooksPath=/dev/null`), then `git apply` of the patch. 54 MB with `.git`.
- The nine patched files equal the builder's final sha256 prefixes: 562465f01d356ada C, bffa82c76b574bcf T3,
  c00ce864603003c3 R, ffd90cb561100381 T, 542a13df94edabda CC, 85bac4b5c079eac6 T4, d0f1d1e6bbdc6411 GW,
  594fc5b0d0564392 W, df54c0b7b883d2d1 NL.
- c9889ee's bytes of all nine equal c32ac3f's (the I59-F PIN): 3dbf485fc95ca591 C, dc541933f0209d50 T3,
  b6780a867b67aceb R, cf0ba1cd5f359124 T, 033333c57e3c371e CC, 16f8e425dace7457 T4, 646a01f14c7abac0 GW,
  a76ac2136095c8a0 W, 64c6043337ec9362 NL. So "red on the PIN" means red on c9889ee's bytes.
- Host before (17:02:01Z): `ip netns list` 0 lines; iptables stable form (`iptables-save | grep -v '^#' | sed -E
  's/\[[0-9]+:[0-9]+\]$/[n:n]/' | sha256sum`) `0528d077bca3781a`; mount-point hash `2dd93d06015feb4d` (27 mounts);
  pre-existing `/tmp/e3-5t328okv` and `/tmp/e3-nw8nn6mk` (the builder's D8, not mine). Kernel 6.18.44, 4 CPUs,
  `ulimit -n` 20000, Python 3.11.15, uid 0.
- Disk: 1,498 MB free at start, 1,439 MB after the copy.

## Fresh gates (re-run here; pasted from `scripts/test_summary.sh`, private `--basetemp` under `/tmp/vf-bt`)

Set ids by `pc_suite.sh`'s own `set_id` formula (`printf '%s\n' <files> | sort | sha256sum | cut -c1-12`), computed
inline (I did not run `pc_suite.sh`); each equals the builder's.

| file | set | summary |
|---|---|---|
| T3 | `1 files set=696563f67d3c` | `pytest-summary: 213 passed in 40.26s` |
| T4 | `1 files set=2e5825a9019e` | `pytest-summary: 194 passed in 21.36s` |
| NL | `1 files set=e3695f80792b` | first run `pytest-summary: 3 failed, 118 passed in 13.31s`; all three `gate-file-missing: .claude/hooks/edit-snapshot.py` (my partial copy); after adding `.claude/hooks` from c9889ee: `pytest-summary: 121 passed in 14.23s` |
| GW | `1 files set=65a832bc5b21` | `pytest-summary: 32 passed in 77.17s (0:01:17)` |
| T | `1 files set=9f0502080347` | foreground 17:13:28Z-17:18:48Z: `pytest-summary: 337 passed in 319.45s (0:05:19)` |

Each count equals the builder's final gate (T3 213, T4 194, NL 121, GW 32, T 337). After T: `ip netns list` 0 lines,
iptables stable form `0528d077bca3781a`, mount hash `2dd93d06015feb4d`, no new `/tmp/e3-*`.

Paths added to the copy (each from c9889ee, each named): `.claude/hooks` (215,040 archive bytes, for NL's gate-file
list), and, for item 11 only, the attested inputs that live outside the five roots: `fixtures/s0-06/neg-unauthorized-tuple.json`,
`upstream.lock.yaml`, `docs/adr/0005-foundry-host.md`, `docs/adr/0006-gbrain-seam.md`, `LICENSE-DECISION.md`,
`SBOM.yaml`, `THIRD-PARTY-NOTICES.md`. They are committed in my scratch repository (37c62de) so the base worktree
`/tmp/vf-base` (`git worktree add --detach`, the base bytes) carries them too.

## Item 11: `validate-ledger integrity` names exactly the three mismatches the patch causes (VERIFIED)

- Base worktree (c9889ee bytes, same added paths): rc 0, `S0-01` to `S0-12` all `PRESENT`, `execution_proof
  numerator=9 denominator=9`.
- Patched copy: rc 1, exactly `attestation-mismatch: S0-03 proofs/S0-03/check_omniroute_roundtrip.py`,
  `attestation-mismatch: S0-04 proofs/S0-04/check_compression.py`, `attestation-mismatch: S0-05
  proofs/S0-05/tools/pc/run_s0_05_units.sh`, and nothing else (`execution_proof numerator=6 denominator=9`).
- Before the attested inputs were added, the copy also named S0-06, S0-09, S0-10 and S0-12 (`registry-schema: ...
  is not a regular file`): an artifact of the partial copy, gone once the seven files were present.

## Item 1: E-1 and A-2, hostile values through the real CLIs (VERIFIED)

Driver `/tmp/vf-scratch/e1_a2_driver.py` (scratch, deleted at the end): the fake is 12 letters alternating with marks
(`~^|+*!@%&=<>?;`, as T3 and T4 build theirs), built at run time; `leak_runs` counts case-folded 4-character runs of it
in stdout plus stderr. S0-03 rows edit the passing bundle's `hermes/profile.yaml` as text (so tags, aliases and escapes
are exact) and run the real `check_omniroute_roundtrip.py` with the spec's flags; S0-04 rows edit a copy of
`fixtures/evidence-pass` and run the real `check_compression.py`.

S0-03 (C), every row `rc=1`:

| row | stdout (or the traceback's last line) | leak runs |
|---|---|---|
| key_env plain, `!!str`, an alias of an anchored value | `key_env (str, 24 characters, sha256 91ec19e5) is not 'OMNIROUTE_API_KEY'` | 0 |
| key_env 80,000 characters | `key_env (str, 80000 characters, sha256 37dd29fd) ...` | 0 |
| key_env list, map value, map key, `!!set`, `!!binary`, 18-digit int, `!!float`, a lone surrogate (`\ud800`) | the shape of the repr (`list, 28 characters, ...`, `bytes, 27 ...`, `int, 18 ...`) | 0 |
| key_env custom tag `!vault`; `!!int` on a non-number | `hermes/profile.yaml is not valid YAML (ConstructorError)` / `(ValueError)` | 0 |
| api_mode plain; an alias of the anchored fake | `transport: profile api_mode (str, 24 characters, sha256 91ec19e5) is not in the permitted set` | 0 |
| compression header plain; a recursive map | `x-omniroute-compression (str, ...) is not 'off'` / `(dict, 45 characters, ...)` | 0 |
| api_mode a list or a map | no failure line; traceback `TypeError: unhashable type: 'list'` (687 bytes of stderr) | 0 |
| key_env `&r [*r, <fake>]` (a recursive alias) | no failure line; traceback `RecursionError: maximum recursion depth exceeded ...` (1,311 bytes) | 0 |
| a credential-named KEY holding the fake (`<fake>_TOKEN: x` under extra_headers) | `carries an inline credential under providers.s0-03-omniroute.extra_headers.<fake>_TOKEN` | 21 (D5: keys may print, accepted) |
| profile mode 0000, checker run as uid 65534 | `hermes/profile.yaml is not valid YAML (PermissionError)` | 0 |

S0-04 (CC):

| row | stdout | leak runs |
|---|---|---|
| `hermes-provider.json` is a JSON array `[<fake>]` | `failure_reason: config: unexpected-provider-fields: <fake>` (the value, whole) | 21 |
| an array `["provider", <fake>]` | the same line, the fake whole | 21 |
| a JSON string `<fake>` | `unexpected-provider-fields: &,*,+,;,=,>,?,F,G,...` (the value's sorted character set) | 0 |
| a JSON number | `malformed evidence: TypeError: 'int' object is not iterable` | 0 |
| an extra KEY named by the fake | `unexpected-provider-fields: <fake>` | 21 (a key: D5) |
| key_env int or list, base_url a map, api_mode a list | the shape, or `api-mode-absent` | 0 |
| api_mode `chat_completions` + U+200B; a Cyrillic `с` homoglyph; `openai_chat` | rc 0; `observation: config api_mode = str, 17 characters, sha256 bf771c36 ...` / `str, 16 ..., dab7059a` / `str, 11 ..., 33b4a9dd` | 0 |

Conclusions:
- E-1 holds for every value class tried: no value, no 4-character run, reaches stdout or stderr.
- A-2 has one residue (finding F-2 below): `check_config_leg` takes `set(provider)` before it checks that the provider
  block is an object, so an ARRAY top level prints its string elements whole as "unexpected fields", and a string top
  level prints its character set. The builder's A-2 table calls that message "field names (keys)". The real producer
  (`capture_leg.py` `provider_block`, which returns a dict of exactly the five allowed keys) cannot write either shape,
  so only a hand-made or tampered bundle reaches it.
- The shape is a leak for a low-entropy value (finding F-6): a brute force over the printed `sha256 <8 hex>` and length
  recovered a 6-digit code in 1.1 s and a 5-letter lowercase word in 14.6 s (one candidate each). The contract asks for
  exactly this shape ("a length and a short hash prefix"); it protects high-entropy keys, which is E-1's threat (a key
  pasted into a name field).
- Pre-existing, outside the diff: an unhashable api_mode and a recursive alias under the provider block end in a
  traceback (exit 1, no `failure_reason:` line, no value printed); S0-03's `_read_yaml` names a read error "not valid
  YAML (PermissionError)" (the C-1 class that I59-F fixed in S0-04's `capture_leg.py` only).

## Item 2: B-1 and A-4, hostile paths through the real runner (VERIFIED)

Driver `/tmp/vf-scratch/b1_a4_driver.py`: the real R, an environment built from nothing (PATH, HOME, LANG only), unit
`not-a-unit`; each row snapshots its scratch tree and `ip netns list` before and after.

| row | rc | the refusal (stderr's last line, abridged) | written | netns |
|---|---|---|---|---|
| B-1 a newline mid-path, as given | 73 | `$'/tmp/.../mid\ndir/evidence' holds a newline` | nothing | unchanged |
| B-1 a trailing newline, root not made yet | 73 | `$'/tmp/.../evidence\n' holds a newline` | nothing | unchanged |
| B-1 a leading newline, relative root | 73 | `$'\nrel-evidence' holds a newline` | nothing | unchanged |
| B-1 a link whose target holds a mid-path newline | 73 | `.../link-to-mid/evidence resolves to $'.../mid\ndir/evidence', which holds a newline` | nothing | unchanged |
| B-1 a chain of two links to it | 73 | the same, through `chain` | nothing | unchanged |
| B-1 a dangling link whose target ends in a newline | 73 | `.../dangling-nl resolves to $'.../ghost\n', which holds a newline` | nothing | unchanged |
| B-1 a newline that `..` drops mid-path | 73 | `$'.../x\ny/../../b1a4/evidence' holds a newline` | nothing | unchanged |
| B-1 under sudo (SUDO_UID/SUDO_GID set), the link row | 73 | as the link row | nothing | unchanged |
| A-4 a newline mid-path, as given | 73 | `S0_05_PAIR_IDENTITY refused: $'.../key\ndir/pair.env' holds a newline` | nothing | unchanged |
| A-4 a leading newline | 73 | `$'\n/tmp/.../pair.env' holds a newline` | nothing | unchanged |
| A-4 a dangling link whose target ends in a newline | 73 | `.../id-dangling resolves to $'.../ghost-key\n', which holds a newline` | nothing | unchanged |
| A-4 a link loop (readlink cannot resolve) | 1 | passes the early check, as designed; the run goes on (`_pair_identity` refuses it as `absent` when buzz-acp runs) | the root's `units.json`, census | unchanged |
| control: a carriage return in the root, no newline | 1 | not refused (the rule keys on `\n` only); the run goes on | the root | unchanged |

Every newline shape exits 73 before anything is written, and the message quotes each path with bash's own `%q`. Exit
73 is the only way out for them. No finding.

## Items 3 and 4: B-2 and B-3, R's own handback program (VERIFIED, with fault injection where named)

Driver `/tmp/vf-scratch/handback_driver.py`: the program is cut from R's bytes as T's `_handback_program()` cuts it,
and runs as `python3 -B - <root> 4242 4243` over trees owned by 65534:65534; a prefix injects a fault or a mover (the
method of T's `MOVE_BEFORE_THE_WAY_UP`). The census walks by descriptor and skips mount points.

| row | result |
|---|---|
| 3,000 levels, RLIMIT_NOFILE 1024 | `3002 entries ... now belong to 4242:4243`; census 3,002, none left |
| 1,100 levels, RLIMIT_NOFILE 16 | `1101 entries ...`; census 1,101, none left |
| a FIFO, a socket, a char and a block device node, two hard-link pairs, links in and out | 7 handed back, the 4 hard-link names left and named (`a hard link: 2 paths name it`), `4 left as they are`; no FIFO open blocked; `/etc/passwd` (a link's target) still 0:0 |
| libc without `statx` (injected: `CDLL` hides the symbol) | `nothing handed back: <root>: this libc has no statx`; nothing changed |
| statx without the mount-id bit (injected: the mask bit cleared) | `nothing handed back: <root>: statx gives no mount id on this kernel`; nothing changed |
| the mount-id bit missing for ONE child (the 4th statx call) | that entry left and named with `[Errno 95]`, counted (`1 left as they are`); the rest handed back |
| a bind mount (same filesystem) appears on `later` just before the walk opens it | `later (a mount point: another mount of this filesystem)`, counted; the file seen through the mount still 65534:65534 |
| a tmpfs appears on `d` while the walk reads `d` | the walk finished `d`'s child `b`, then STOPPED at the climb: `..` from `b` crosses into the new mount, so the identity check fails: `then it stopped: .../d/b moved while it ran`; `d/c` left unreached |
| a tmpfs appears on the parent `p` before the first climb | stopped the same way; `p/later` left unreached |
| `d` moves out of the root while the walk reads it | `outside/d/b` and `outside/d/c` now belong to 4242:4243: entries handed back OUTSIDE the root; then the climb from `d` stops |
| the ancestor `p` moves out while the walk is two levels below | the climbs from `x` and `child` still match (they moved with `p`), so the walk goes on inside `p` at its new place and hands back `outside/p/zz-decoy`; it stops only at `p`'s own climb |

Conclusions:
- B-2 and B-3's contract clauses hold: any depth, under 1024 descriptors (and 16), every entry counted; mount points,
  other filesystems and hard links left, named and counted; both fail-closed branches (no statx, no mount-id bit) are
  reachable by injection and hand back nothing. On this kernel neither fires without injection.
- The way-up check is sound for exactly what R's comment says ("the very directory it came down from"): it catches a
  moved child and a mount stacked on a parent (`..` traverses the new mount, measured). It does not keep the walk
  inside the root: a directory that moves out while the walk reads it, or an ANCESTOR that moves out, has its remaining
  entries handed back where they now are (finding F-4). The builder's self-attack 1 names the first case; the ancestor
  case is new. R's comment "It changes nothing outside the root" (pre-existing text above `_handback`) is false under a
  live mover.
- The builder's premise "no unit or canary is alive at a real handback" does not hold against a unit that leaves its
  namespace (finding F-5): a probe (my namespace `vf-probe`, deleted) ran `setpriv --reuid=65534 ... unshare -Urn sleep
  60` inside it; the sleep's netns became `net:[4026532316]` (vf-probe's is `net:[4026532263]`) and `ip netns pids
  vf-probe` listed nothing. `_egress_ns_teardown` kills only the pids `ip netns pids` lists (netns_lib.sh:352-370), so
  such a process outlives the teardown, is alive during the handback and can be the mover above. Unprivileged user
  namespaces are enabled here (`max_user_namespaces` 64313) and on stock Fedora (inferred for the PC). It gains no
  egress (its new namespace has only a loopback); what it can move is its own entries.
- The stop line says "moved while it ran" also when a mount appeared (no move): wording only.
- Process note: my first run of this driver left the row's bind mount in place for about a minute (Python's `ismount`
  is false for a same-filesystem bind mount); I unmounted it by name (`umount /tmp/vf-scratch/hb/mnt-ahead/later`) and
  the mount hash returned to `2dd93d06015feb4d` (27 mounts). The driver now reads `/proc/self/mountinfo`.

## Item 5: B-4 and A-1, every id form at every seam (VERIFIED through the real runner)

Scratch test `/tmp/vf-scratch/test_vf_ids.py` imports T's own helpers by path (`_runner_env`, `_listener`, `e3dir`,
`_census`), so each explicit row runs the real runner with a listener up: a leg past the check would reach its launch.
Run in the foreground with a private basetemp: `2 failed, 17 passed in 7.06s` (pytest's own summary line; this is a
scratch probe, not a gate); both failures are my assertions, read below.

| seam | value | rc | unit ran | evidence root | note |
|---|---|---|---|---|---|
| S0_05_UNIT_USER | `0:65534`, `65534:0`, `4294967295:65534`, `65534:4294967295`, `+1:1`, `1:1:1`, `' 65534:65534'`, full-width `６５５３４:６５５３４` | 64 each | no | not made | exact `UNIT_USER_REFUSED` line |
| S0_05_UNIT_USER | `65534:65534` + a trailing newline | 64 | no | not made | refused; my row failed only because the quoted value's newline splits the message over two lines |
| S0_05_UNIT_USER | `4294967294:4294967294` (the upper bound) | 1 | no | made | passes the check, as the contract says; `setpriv --init-groups` then finds no passwd entry and the leg is `not-run|launch exited within the settle window` |
| SUDO_UID:SUDO_GID | `00:1`, `+1:1`, `1:`, `'1 :1'`, Arabic-Indic `١:1` | 64 each | - | not made | `must be decimal ids` |
| SUDO_UID:SUDO_GID | `1:4294967295` | 64 | - | not made | `must be at most 4294967294` |
| SUDO_UID:SUDO_GID | `0:0`, `4294967294:4294967294` | 1 | - | made | allowed; the handback gives the root to that id |
| SUDO_UID:SUDO_GID | `:1` (SUDO_UID empty) | 1 | - | made, 0:0 | my row expected 64; R's gate is `[ -n "${SUDO_UID:-}" ]`, so an empty SUDO_UID means "not under sudo": no handback, as at the base. Pre-existing and not a sudo shape (sudo always sets both) |

Is there any way the stand-in runs as uid 0 or gid 0? Not through its ids: every explicit form outside [1, 4294967294]
exits 64 before anything is written or launched, a resolved uid 0 keeps A4's `not-run` row, a resolved gid 0 exits
64, and bash's `[1-9]` matched no non-ASCII digit under C and C.UTF-8 (the only locales installed here;
en_US.UTF-8 is absent, so the PC's locale is UNVERIFIED; netns_lib.sh's own rule X1 spells classes as explicit
lists for that reason, and R's new patterns use ranges). One channel stays open (finding F-7): the unit launches with
`setpriv ... --init-groups` (R:869, R:874), which takes supplementary groups from `/etc/group`, and A7 reads only the
Uid and Gid lines. In a private mount namespace (`unshare -m`, a copy of `/etc/group` with `root:x:0:nobody`
bind-mounted over it; the host file untouched, the mount gone with the namespace), `setpriv --reuid=65534
--regid=65534 --init-groups` gave `Uid: 65534 x4`, `Gid: 65534 x4`, `Groups: 0 65534`; the same with `--clear-groups`
gave `Groups:` empty. A7 would record 65534 and 65534 and pass. Needs a host whose unit user is listed in group 0.

## Item 6: the #331 shim and A-3 under the detached launch and under load (VERIFIED)

The launch form is VERIFY-I59-BCE's, `nohup bash -c '… & wait'`, whose background job measured `SigIgn:
0000000000000007` here (HUP, INT and QUIT ignored). The selection is VERIFY-I59-BCE's item-3 set, `-k 'x4_runner_cleanup
or e3b_r4 or e3r1_r1 or i59b_the_handback_runs_when_a_signal'`.

| tree | launch | result (pasted from `scripts/test_summary.sh`) |
|---|---|---|
| patched | nohup form | `pytest-summary: 15 passed, 322 deselected in 48.30s` |
| base (c9889ee's T and R) | nohup form | `pytest-summary: 4 failed, 11 passed, 282 deselected in 211.05s (0:03:31)`: `assert 1 == 130` (e3b_r4 SIGINT), `timed out waiting for cleanup's SIGTERM to reach the unit` (e3r1_r1_b), `assert 1 == 130` (i59b `[INT]`), `assert 1 == -1` (i59b `[HUP]`): the four VERIFY-I59-BCE named |
| patched | nohup form, 8 CPU hogs on 4 CPUs (started and killed by pid, 0 left), the set plus the I59-F runner-session tests (`i59f_the_handback_leaves`, `i59f_b3_the_handback_hands`, `i59f_a1_a_unit_user_in_range`) | `pytest-summary: 20 passed, 317 deselected in 92.00s (0:01:31)` |
| patched GW (`1 files set=65a832bc5b21`) | nohup form | `pytest-summary: 32 passed in 76.22s (0:01:16)` |

GW's tests send only SIGTERM and SIGINT (GW:292-577), so its three-signal reset covers what they send. D3 (the five
signals) is right: `subprocess` restores SIGPIPE and SIGXFSZ for the shim's interpreter, which ignores both again at
its startup, and `os.execvp` keeps an ignore, so only the shim can put them back. The shim resets dispositions, not
the blocked mask; no launcher here blocks INT, HUP or TERM (the tool shell's `SigBlk` is `0000000000010000`, SIGCHLD
only). No finding.

## Item 7: C-1, C-2, E-2, F2 (VERIFIED)

- The pins hold as mutants: C-X4 (C-1, the read inside the parse `try`) reds 4 of 4, C-X6 (C-2, 7 characters to stdout)
  22 of 22, E-X7 (E-2, 7 characters to stderr) 7 of 7, and my N7 (W's `-rfEs` changed to `-rfs`) reds NL's YH-3 and YH-4
  (item 8's table). W:46 and NL:873-874 carry the same string.
- `-rfEs` does what W's comment says, measured on a three-test file with this venue's `pytest 9.1.1`: `-q -rs` prints
  only `SKIPPED [1] ...`; `-q -rfEs` prints `FAILED ... - assert 1 == 2`, `ERROR ... - RuntimeError: setup fails` and
  `SKIPPED [1] ...`. CI installs `pytest` unpinned (W's Install step), so "CI's version" is whatever pip resolves on the
  day (only 9.1.1 measured here).
- D4 (E-2's `stderr == ""` added only where E-X7 lands and in the new rows, not to the ~60 other stdout-failure tests)
  was accepted by the coordinator in the round-2 message ("D4 stays as is"). No finding.

## Item 8: the mutation audit (VERIFIED)

Harness `/tmp/vf-scratch/mutate.py` (scratch): for each row, the unmutated baseline of its target set first (it must
pass whole), then one anchored replacement (the anchor must occur exactly once), `py_compile` or `bash -n` plus a
compile of every R heredoc, the target tests with a private `--basetemp`, then the file restored from a saved copy
and its sha256 checked. KILLED = at least one FAILED, no ERROR, and the collected count equal to the baseline's
(AF-AP-223). The counts below are pytest's own summary lines from the harness (scratch probes, not gates; every gate
count in this report comes from `scripts/test_summary.sh`). Every file ended at its patched hash (C 562465f01d356ada, CC 542a13df94edabda, R c00ce864603003c3, W
594fc5b0d0564392; `capture_leg.py` and CE unmodified per `git status`).

| row | clause | mutant | verdict | FAILED / collected |
|---|---|---|---|---|
| M-E1c | E-1 | key_env printed `!r` | KILLED | 1/6 |
| E-X7 | E-2 | 7 characters of the parse message to stderr | KILLED | 7/7 |
| X-A2-key | A-2 | key-env-not-a-name back to `_short` | KILLED | 2/13 |
| C-X4 | C-1 | `read_regular` inside the parse `try` | KILLED | 4/4 |
| C-X6 | C-2 | 7 characters of the message to stdout | KILLED | 22/22 |
| X-A1-range | A-1 | both `-gt 4294967294` bounds off | KILLED | 2/11 |
| X-B3-up | B-3 | no identity check on the way up | KILLED | 1/1 |
| X-B3-count | B-3 | the summary counts `min(len(left), 1)` | KILLED | 2/2 |
| X6 | B-6 | `if st.st_dev != dev:` becomes `if False:` | KILLED | 1/2 |
| X-R3-default-never | D-R2-3 | the resolved-gid check never fires | KILLED | 2/2 |
| X-R3-a7-no-compare | D-R2-3 | A7 never compares the gid with the wanted one | KILLED | 1/1 |
| X-B-pin-add | D-R2-2 | CC's copy gains `responses` | KILLED | 1/1 |
| N6 (new) | D-R2-2 pin, C's side | C's `PERMITTED_API_MODES` gains `responses` | KILLED | 1/1 |
| N7 (new) | F2 | W's `-rfEs` becomes `-rfs` | KILLED | 2/2 |
| **N1 (new)** | A-1 | only the UID's upper bound removed | **SURVIVED** | 0/11 |
| **N2 (new)** | A-1 | only the GID's upper bound removed | **SURVIVED** | 0/11 |
| **N3 (new)** | A-1 | the explicit pattern admits uid 0 | **SURVIVED** | 0/11 |
| **N4 (new)** | E-1 | C's `_shape` returns `repr(value)` for a non-string | **SURVIVED** | 0/6 |
| **N5 (new)** | A-2 | CC's `_shape` returns `repr(value)` for a non-string | **SURVIVED** | 0/13 |

Twelve of the builder's mutants reproduce as FAILED tests (A-1, A-2 and B-3 each covered). What the survivors let
through, measured through the real runner with the mutant applied (then restored):
- N1 with `S0_05_UNIT_USER=4294967296:65534`: `rc=1 unit_ran=True records=[(0, 65534)]`, the leg `not-run|unit identity
  not observed: uid 0`. The stand-in RAN AS ROOT and A7 refused only after the launch: round 1's A-1 hole, back, with
  every A-1 test green. The unmutated runner refuses the same value with exit 64. (With `4294967295:65534` the launch
  itself failed: `--init-groups` finds no passwd entry for 4294967295, while 4294967296 cuts to 0, which has one.)
- N2 with `65534:4294967296`: the leg went past the check; coreutils' `chown` refused the group and the writability
  probe failed (`not-run|unit scratch tree not writable`), so no unit ran here.
- N3 with `0:65534`: A4's row, `not-run|unit would run as root`: no unit ran, but the run did not exit 64 as A-1 says.
- N4 and N5: by construction a numeric or list value prints whole; no E-1 or A-2 row plants a non-string value.
The A-1 contract's own row list is symmetric (both ids bad at once), so these are gaps in the contract's rows, not in
the builder's delivery (findings F-3 and F-8).

## Item 9: D-R2-2 by route B and D-R2-3 (VERIFIED)

- The pin reads C as data and is not blind to a change on either side: X-B-pin-add (CC gains a mode) and N6 (C gains a
  mode) each red it. It reads the constant NAMED `PERMITTED_API_MODES`, not what C's `check_transport` compares
  against; they are the same constant today (C:801).
- A near name never prints as a known mode: `Chat_Completions` and `chat_completions ` (the builder's rows), plus
  `chat_completions` + U+200B and a Cyrillic `с` homoglyph (my rows, item 1) each print a shape. Membership is exact.
  A credential-shaped value never reaches the observation (`_screen_tree` fails the bundle first); any other value
  prints a shape.
- **The known set is the wrong vocabulary for S0-04's field (finding F-1).** CC observes `api_mode` of the CAPTURED
  provider block, and `capture_leg.py` fills it with `block.get("api_mode") or block.get("transport")` from the
  provider block of the live profile, whose key is `transport: openai_chat` (both committed configs:
  `proofs/S0-03/hermes/config.yaml:21`, `proofs/S0-04/hermes/config.yaml:26`). The committed real evidence
  `proofs/S0-04/evidence/config/hermes-provider.json` holds `"api_mode": "openai_chat"`. C's set is Hermes' MODEL-section
  vocabulary (`api_mode: chat_completions`). So on the evidence the owner signs, the patched checker prints
  `observation: config api_mode = str, 11 characters, sha256 33b4a9dd (RECORDED, not asserted - ADR 0002 deviation,
  owner task #35)` where the base printed `... api_mode = openai_chat ...` (both run here, rc 0). T4's name pin runs
  on `fixtures/evidence-pass`, whose provider block says `chat_completions`, so no test sees the real bundle's line.
  The minted `result.json` stores only `stdout_sha256`, so the re-mint absorbs the change; what changes is the line a
  reader sees. Round 3's premise ("a mode name is an enum the owner reads"; "chat_completions is the live
  transport") does not hold for the one real S0-04 bundle.
- D-R2-3: a resolved gid 0 exits 64 (X-R3-default-never kills 2 of 2), A7 records the Gid line and compares it as a
  number (X-R3-a7-no-compare kills), and the round-3 T rows pass in the gate.

## Item 10: the two questions

**(a) CE grades the uid of a unit-identity record, not its gid (D-R3-4).** CE:111 `IDENTITY_KEYS` has no `gid`, and
`check_unit_identity` refuses only `uid 0`. None of the four committed records carry a gid (the two evidence units
and both synthetic fixtures). Graded with a scratch CE that adds `gid` to the required keys and refuses a gid 0 (my
copy only, restored), through the spec's own legs:
- `proofs/S0-05/evidence --units hermes-acp,buzz-acp`: `PASS ... 2 units, 22 canaries` becomes `failure_reason:
  unit-identity-invalid: hermes-acp unit-identity.json lacks one of unit, pid, exe_realpath, entrypoint_realpath,
  entrypoint_sha256, uid, gid, argv`. The re-mint's positive leg would fail, so grading the gid needs a new PC capture
  with the round-3 runner first.
- `fixtures/evidence-synthetic-pass` fails the same way (it needs a gid), and `evidence-synthetic-uid0` then fails on
  the missing key instead of `uid 0` (it needs a gid too, or it stops testing the uid).
- `evidence-mechanism-sandbox`, `evidence-gate-off` and `evidence-bare-unshare` are unaffected.
Is it a gap in the containment claim? Not in the frozen one: seed S0-05's full-proof assertion is an egress
containment property (each unit reaches exactly its allow-list, every canary fails), and CE's A7 docstring promises
"a non-root user", which the uid carries. It is a gap in what the committed EVIDENCE can show about the root group:
CE cannot tell a gid-0 unit in a bundle from a runner older than round 3, and the committed bundle is such a bundle
(its units ran as uid 1000; their gid is unrecorded). New captures are protected at capture time by A7. A compatible
middle form (grade a gid when present, tolerate its absence) would pass today's evidence and grade every new one.

**(b) S0-04 records api_mode and does not assert it (D-B-2) against D-021.** No frozen criterion of this increment is
contradicted: seed S0-04 (`seeds/seed-stage0-v1.yaml:406-422`) names three compression assertions and no mode, and
I59-F's contract never asks S0-04 to assert one. Against D-021 / ADR 0002 as amended ("every proof asserts and records
the wire mode it observes"): S0-04's request legs DO assert their wire path, three times (request.json `path` equals
the fixture's, the URL path equals it, the upstream record's path equals it; the committed fixtures say `POST
/v1/chat/completions`). What it only records is Hermes' CONFIGURED provider transport, which is not observed on any
wire. Asserting that value against S0-03's set would fail the real evidence today (`openai_chat` is not in it), so an
assertion first needs an owner ruling on the vocabulary (the same root as F-1). Stale in any case (D-B-2, confirmed):
CC:365-367 still calls task #35 "the owner's open decision", and the observation text (CC:371) still says "ADR 0002
deviation", while `docs/08_DECISION_LOG.md:32` (D-021) and ADR 0002's "Amended: 2026-09-08" made chat_completions the
v1 transport.

## Red-green, static checks, adjacent gates and a dry-run re-mint (VERIFIED)

**Red on the base.** The patched T3, T4 and T copied into the base worktree `/tmp/vf-base` (base production bytes:
3dbf485fc95ca591 C, 033333c57e3c371e CC, b6780a867b67aceb R), each run through `scripts/test_summary.sh`:
- T3, the E-1 rows, the two changed pins and the E-2 test: `pytest-summary: 6 failed, 7 passed, 200 deselected in 4.99s`
  (the 4 E-1 rows and 2 pins fail; E-2's 7 rows pass on the base, the builder's D6).
- T4, every new or changed A-2, route-B, C-1 and C-2 test: `pytest-summary: 11 failed, 29 passed, 154 deselected in
  8.54s` (C-1 and C-2 pass on the base, D6).
- T, `-k 'i59f or test_runner_live_leg or test_a7_a_unit_not_matching or test_d_pair_leg or test_a4_a_root_unit_user'`,
  foreground 17:56:12Z-18:00:15Z: `pytest-summary: 40 failed, 5 passed, 292 deselected in 242.52s (0:04:02)`. The 40
  are every B-1, B-4, A-1, A-4, round-3, B-3 and bind-mount row plus the three round-3 record pins; the 5 that pass on
  the base are the controls (A-4's default-owner row, the A-1 positive control, the CE reader test, the shim helper
  test and B-6's tmpfs row).

**Static checks** (evidence demand 5, re-run): `bash -n` R rc 0; R's 5 heredocs compile; `pyflakes` over the 7 changed
Python files rc 0; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` prints 0 for all 9 changed files.

**Adjacent gates** (every test file that names a changed file, by `grep -l` over `tests/*.py` and
`harness-ports/tests/*`):

| file | set | summary |
|---|---|---|
| `test_edit_snapshot_ap_screen.py` | `1 files set=3d4383148bd3` | `pytest-summary: 197 passed in 0.51s` |
| `test_ci_gate.py` | `1 files set=080b86ac9b1a` | `pytest-summary: 117 passed in 18.91s` |
| `test_stage0_ci_workflow.py` | `1 files set=9aff003f97f7` | `pytest-summary: 12 passed in 0.16s` |
| `test_gpu_side_by_side.py` | `1 files set=9b506ab184e5` | `pytest-summary: 74 passed in 39.34s`, after adding `deploy`, `src`, the 22 `docs/*.md`, `docs/research/findings/jev-pipes/rwkv_sbs_probe.py`, `.../sbs-window.jobs` and `docs/research/findings/j2b-variants/rwkv7_g0.py` from c9889ee (each earlier run failed only on a missing file) |
| `test_decisions_no_model.py` | `1 files set=0f388f113582` | `pytest-summary: 1 failed, 3 passed in 62.91s (0:01:02)`: NOT clean here. Its J1 suite (which includes NL) ran `9 failed, 431 passed`, and all 9 are `test_decide_harvest.py`'s, which reads the PIN commit 434b727dfd2b from git history that a `git archive` copy does not have; NL passed inside that blocked run |

**A dry-run re-mint in my copy** (`python3 scripts/proof-runner run --proof <id> --venue sandbox --root .` for S0-03,
S0-04 and S0-05, then `validate-ledger integrity`): all three rc 0, then `S0-03 PRESENT`, `S0-04 PRESENT`, `S0-05
PRESENT` (rc 0); only the three `result.json` files changed. Leg by leg against the committed results:
- S0-03: only the attestation entry of C changed; the positive leg and all 4 negative legs are byte-identical in exit
  code, `stdout_sha256` and failure reason (the negative control still observes `failure_reason: blocked:
  credential_absent`).
- S0-04: the attestation entry of CC and the POSITIVE leg's `stdout_sha256` changed (the observation line, F-1); the
  negative leg is unchanged (`failure_reason: off: compression-header-missing`).
- S0-05: only the attestation entry of R changed; all 4 legs unchanged (CE is unchanged and the committed evidence
  carries no gid).

## Finding inventory (no severity filter)

**F-1. FOLLOW-UP, and a decision for the coordinator BEFORE the S0-04 re-mint: route B's known set is the wrong
vocabulary for the field S0-04 observes.**
- Evidence: VERIFIED. The real CC on the committed real evidence: base `observation: config api_mode = openai_chat
  (...)`, patched `observation: config api_mode = str, 11 characters, sha256 33b4a9dd (...)`; the dry-run re-mint
  changes exactly S0-04's positive `stdout_sha256`.
- Mechanism: `capture_leg.py:121` fills `api_mode` with `block.get("api_mode") or block.get("transport")` from the
  provider block; the live profile's provider key is `transport: openai_chat`. CC's `KNOWN_API_MODES` copies S0-03's
  model-section set `{chat_completions, codex_responses}`. T4's name pin runs on the synthetic `fixtures/evidence-pass`
  (`chat_completions`), never on the real bundle.
- Contract mapping: D-R2-2's letter holds (a name prints only for a member of C's set). Its premise ("a mode name is
  an enum the owner reads"; "chat_completions is the live transport") does not hold for the one real S0-04 bundle.
  A premise error in the round-3 ruling, not a builder defect.
- Canonical path: yes (the re-mint's own positive leg). Material effect: the line the owner reads for S0-04 no longer
  names the transport; nothing is falsified (the evidence file still holds `openai_chat`, and the hash is re-minted).
- Reproduction: `python3 proofs/S0-04/check_compression.py proofs/S0-04/evidence` in the patched tree and the base.
- Fix options: (a) accept the shape for the real bundle; (b) a new ruling that adds Hermes' provider transport names
  (`openai_chat`, and the Responses one) to CC's set with their own pinned source; (c) observe the model section's
  `api_mode` (a capture change and a re-capture). (b) and (c) change CC or the capture, so after the re-mint they
  force a second S0-04 signature.

**F-2. FOLLOW-UP (A-2 residue, defence in depth): a non-object provider block prints its values through
`unexpected-provider-fields`.**
- Evidence: VERIFIED through the real CLI: a JSON array `[<fake>]` prints `failure_reason: config:
  unexpected-provider-fields: <fake>` (21 leaked 4-character runs); a JSON string prints its sorted character set.
- Contract mapping: A-2's letter ("every CC message that prints a ... config value prints its shape"; keys may print):
  array elements are values. The builder's A-2 table calls CC:345's message "field names (keys)".
- Canonical path: the real checker, but only a hand-made or tampered bundle reaches it: the real producer
  (`capture_leg.py:102-124`) always writes an object of exactly the five allowed keys. Not material under the
  predicate (a forged bundle prints what its author wrote); CC's own `_redact` docstring does claim hostile bundles.
- Reproduction: item 1's rows `CC top-level-list` and `CC top-level-string`.
- Fix: in `check_config_leg`, before `set(provider)`: `if not isinstance(provider, dict): raise
  Failure(f"{CONFIG_LEG}: provider block is not a JSON object")`, with a T4 row. It touches CC (attested).

**F-3. FOLLOW-UP (test gap; T only, not attested, can land after the re-mint): A-1's rows never make ONE id bad.**
- Evidence: VERIFIED. Mutants N1 (only the uid bound removed), N2 (only the gid bound) and N3 (the explicit pattern
  admits uid 0) each pass all 11 A-1 tests. Under N1, `S0_05_UNIT_USER=4294967296:65534` ran the stand-in AS UID 0
  (`records=[(0, 65534)]`) and A7 refused only after the launch: round 1's hole. The unmutated runner refuses it with
  exit 64 (and every asymmetric value I tried, item 5).
- Contract mapping: none violated; A-1's frozen row list is symmetric and the builder delivered it. The gap is in the
  contract's rows.
- Fix: add `4294967296:65534`, `65534:4294967296`, `4294967295:65534`, `65534:4294967295`, `0:65534` and `65534:0` to
  T's `BAD_UNIT_USERS`.

**F-4. FOLLOW-UP (outside the contract): under a live mover the handback changes entries outside the root.**
- Evidence: VERIFIED by injection into R's own program: `d` moved out while the walk read it (its remaining entries
  handed back at their new place), and an ANCESTOR moved out while the walk was below it (the climbs still match, the
  walk goes on inside the moved ancestor and hands back an entry there).
- Contract mapping: none (B-3's clauses hold; the builder's self-attack 1 names the first case, not the second). R's
  comment above `_handback` (pre-existing) says "It changes nothing outside the root"; that is false under a mover.
- Material: needs a process alive during the handback (F-5); what can move is that process's own entries.
- Fix: correct the comment in the same change as any R fold, or re-check at each climb that the parent is still under
  the root; or remove the mover (F-5).

**F-5. FOLLOW-UP (pre-existing, outside the diff): a unit that leaves its namespace survives the teardown.**
- Evidence: VERIFIED by probe: a uid-65534 process that ran `unshare -Urn` inside my namespace `vf-probe` was in a
  new netns and `ip netns pids vf-probe` listed nothing; `_egress_ns_teardown` (netns_lib.sh:352-370) kills only
  listed pids. It falsifies the builder's premise "no unit or canary is alive at a real handback". It gains no egress.
- Fix: kill each unit's whole process tree (a cgroup or a session per unit), not only its netns members.

**F-6. INFO: the shape leaks a low-entropy value.** VERIFIED: from `str, n characters, sha256 <8 hex>` a brute force
recovered a 6-digit code in 1.1 s and a 5-letter word in 14.6 s. The contract asks for this shape; it protects
high-entropy keys (E-1's threat). Fix, if wanted: say so in `_shape`'s docstring.

**F-7. FOLLOW-UP (outside D-R2-3): supplementary group 0 is unobserved.** The unit launches with `setpriv
--init-groups` (R:869, R:874); A7 reads Uid and Gid only. VERIFIED mechanism (a private mount namespace, `/etc/group`
untouched): `Groups: 0 65534` with Uid and Gid 65534. Through the runner: INFERRED from A7's code. Needs a unit user
listed in group 0 on the host. Fix: A7 records the Groups line and refuses a 0, or the launch sets an explicit list.

**F-8. FOLLOW-UP (test gap; T3 and T4 only, can land after the re-mint): no E-1 or A-2 row plants a non-string
value.** VERIFIED: N4 (C's `_shape` prints a non-string whole) and N5 (CC's) survive. The code is right (item 1: an
18-digit int prints as `int, 18 characters, sha256 ...`). Fix: one int or list row in `PROFILE_VALUE_PATHS` and in
`CONFIG_VALUE_PATHS`.

**F-9. INFO (pre-existing).** C ends in a traceback (exit 1, no `failure_reason:` line, no value printed) on an
unhashable api_mode (`TypeError`) or a recursive alias under the provider block (`RecursionError`); C's `_read_yaml`
names a read error "not valid YAML (PermissionError)", the C-1 class I59-F fixed in S0-04's tool only.

**F-10. INFO, stale text (the builder's D-B-2, confirmed).** CC:365-367 calls task #35 "the owner's open decision" and
CC:371's pinned observation says "ADR 0002 deviation"; D-021 decided it on 2026-09-08. A fix touches CC (attested)
and T4's pin.

**F-11. INFO (question 10a).** CE grades uid only. Grading the gid now fails the committed evidence and both synthetic
fixtures on the missing key, so it needs a PC re-capture with the round-3 runner first; "grade when present" would not.

**F-12. INFO.** The walk's stop line says "moved while it ran" also when a mount appeared on a parent (no move).

**F-13. INFO.** R's new id patterns use `[1-9][0-9]` ranges; netns_lib.sh's rule X1 spells classes as explicit lists
so no locale can widen them. Under C and C.UTF-8 no non-ASCII digit matched; the PC's en_US.UTF-8 is UNVERIFIED. A
match would still fail closed later (`[ -gt ]` errors, then `chown` and `setpriv` refuse the id).

**F-14. INFO.** The explicit unit-user refusal quotes the value raw (not `%q`), so a value holding a newline splits
the message over two stderr lines (my trailing-newline row). Operator input only.

**F-15. INFO (process, mine).** My first handback-driver run left one bind mount for about a minute; unmounted by name,
the mount hash back to `2dd93d06015feb4d`.

**F-16. INFO.** `tests/test_decisions_no_model.py` cannot run clean from a `git archive` copy (its J1 suite reads a
PIN commit from history); NL passed inside it.

Builder-report accuracy: every gate count, hash and red I re-ran matched. Three statements do not hold as written:
the A-2 table's "field names (keys)" (F-2), self-attack 1's "the walk never climbs anywhere but home" (true, but home
can leave the root: F-4), and "no unit or canary is alive at a real handback" (F-5).

## What I reproduced, reviewed statically, and skipped

- Reproduced through the production path: the premise and hashes; the five gates and the five adjacent files; item
  11 on both trees; every item-1 row; every item-2 row; the handback rows (by injection where named); every id row;
  the signal selection in the detached launch on both trees and under 8 hogs; 19 mutants plus the survivors'
  effects; the red runs on the base; the static checks; the dry-run re-mint.
- Reviewed statically: A7's Groups gap through the runner (the setpriv mechanism was reproduced); CE's readers of
  `unit-identity.json` beyond CE itself (the builder's grep, not re-run); the PC's kernel, glibc and locale.
- Skipped, with reasons: the PC and real CI (no bridge in this lane, by rule); `tests/test_lane_gate.py` and the whole
  `tests/test_vendored_manifest.py` (the brief's disk rule); the builder's X-A3, X-S1, X-S2 and X-B4 mutants (the
  shim and GW were re-measured directly in item 6 and the gates; five-plus builder mutants were required and twelve
  were reproduced).

## Host state after (18:08:47Z)

`/tmp/vf-wt`, its base worktree `/tmp/vf-base` (removed with `git worktree remove`) and every `/tmp/vf-*` scratch
path are gone. `ip netns list` 0 lines; iptables stable form `0528d077bca3781a` (equal to before); mount hash
`2dd93d06015feb4d`, 27 mounts (equal to before); no uid-65534 process; `/tmp/e3-5t328okv` and `/tmp/e3-nw8nn6mk` are the
two that predate this lane. My probe namespace `vf-probe`, its process, the 8 CPU hogs and the one bind mount of F-15
were each destroyed by name or pid. I wrote nothing in the main tree but this report, and made no git write outside
my own copy. Disk: 1,446 MB free.

## GATE

Blocking predicate (skill `contract-gate`, D-031) with D-034's CORE-BLOCKING rule: no finding meets all five
conditions. F-1 is a premise error in the round-3 ruling (the letter of D-R2-2 holds); F-2 needs a bundle the real
producer cannot write; F-3 and F-8 are gaps in the contract's own rows, delivered as written; F-4, F-5 and F-7 lie
outside the frozen contract; the rest are INFO. The headline claims hold through the real path: no profile or config
value prints for any value class a real capture can hold, every newline root and identity path exits 73 with nothing
written, every id outside [1, 4294967294] exits 64 before anything runs, the handback walks any depth under 1024
descriptors, counts what it leaves and never descends a mount, and the signal tests pass in the detached launch.

**Recommendation: MERGE-READY-WITH-FOLLOWUPS** (not reproduced: the PC venue, meaning statx mount-id support on its
kernel, its locale's digit ranges and its unit user's groups, and real CI).

## Before the coordinator re-mints S0-03, S0-04 and S0-05

Must be DECIDED first (each changes an attested file, so after the re-mint it means a second signature):
1. **F-1, S0-04's observation vocabulary.** On the real bundle the re-minted S0-04 observes `str, 11 characters,
   sha256 33b4a9dd`, not `openai_chat`. Accept that, or rule a CC change (Hermes' transport names in the known set,
   with their own pin) and fold it before the re-mint.
2. **Which attested-file follow-ups to fold now:** F-2 (CC: refuse a non-object provider block), F-10 (CC's stale
   "open decision" and "ADR 0002 deviation" text, with T4's pin), F-4 (R's "changes nothing outside the root"
   comment), F-7 (R's A7 Groups line). F-11 (CE grading the gid) cannot fold before the re-mint without a new PC
   capture; if it is wanted, S0-05's re-mint waits for that capture.

Holds now (verified here):
3. The patch applies cleanly at origin (c9889ee equals a1a639b for proofs, tests, scripts, harness-ports and .github).
   `validate-ledger integrity` names exactly the S0-03, S0-04 and S0-05 attestation mismatches.
4. A dry-run re-mint in a scratch copy gives all three PRESENT. Every negative control's observed reason is unchanged.
   The only output that changes is S0-04's positive `stdout_sha256`, beside the three attestation hashes.
5. The S0-05 re-mint certifies uid only for the committed units: they were captured before round 3, their gid is
   unrecorded, and CE does not grade one (F-11). This is a fact for the owner's signature, not a blocker.

Can wait until after the re-mint (test files only, and no test file is an attested input of S0-03, S0-04 or S0-05):
6. F-3's asymmetric A-1 rows, which close the N1 survivor that let a uid-only regression run the unit as root, and
   F-8's non-string E-1 and A-2 rows.
