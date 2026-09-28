# I59-F round 5: the three attested follow-ups before the one re-mint (tasks #335 and #344)

Role: the I59-F builder, resumed (sandbox code-implementer, Opus 5.5; the S0-05 tests need root, so this lane stays in the
sandbox). Authored 2026-09-28 22:1xZ by the coordinator. Work in your worktree `/home/user/i59-landing`, as in round 4.

VERIFY-I59-F round 4 returned **MERGE-READY-WITH-FOLLOWUPS** (`tasks/briefs/i59/VERIFY-I59-F-R4-report.md`): every round-1
finding closes, task #344 holds by an independent oracle, no blocker. Three follow-ups change attested files, so fixing them
after the re-mint would mean a second signature, and the owner asked for the fixes first and one re-mint (D-104 (3)). This
round folds them and one test gap. Everything round 4 built stays: every round-4 test and its 30 mutant rows keep passing and
dying, and the expected reds stay exactly F-11's one cause (the committed S0-05 evidence has no gid).

## CONTRACT (this round)

1. **R4-F1 (`proofs/S0-03/check_omniroute_roundtrip.py`, `tests/test_s0_03_omniroute.py`).** A mapping key that is not a
   string (an int, a bool, a null) under the provider block ends in a `failure_reason:` line that names the key's type and
   its path, never a traceback: refuse it in `_walk_node` before `is_credential_name` is called. Rows for an int, a bool and
   a null key: exit 1, the one line exactly, empty stderr, nothing of the value printed.
2. **R4-F3 (`proofs/S0-05/tools/pc/run_s0_05_units.sh`, `tests/test_s0_05_egress.py`).** The evidence walk's handback no
   longer costs quadratic time in depth. Round 4 checks the whole way up to the root at every climb (2.33 s, 11.18 s and
   24.04 s at 1,100, 2,200 and 3,300 levels, against round 3's 0.07 s to 0.15 s), and `cleanup` ignores INT and TERM, so a
   deep tree can hold the runner's exit for hours. Choose the mechanism (the verifier's options: check the whole chain every
   k climbs plus once at the end with an O(1) parent check at each climb; or cap the depth the walk enters and count what
   lies below; or a time budget that names what it leaves), keep round 1's B-3 tests passing unchanged (the 1,100-level tree
   handed back whole), keep round 4's three walk tests passing, measure 1,100, 2,200 and 3,300 levels, and state in R's
   comment what window your choice leaves (R4-F6's class). Do not change `cleanup`'s signal disposition.
3. **R4-F4 (`proofs/S0-05/check_egress.py`, `tests/test_s0_05_egress.py`).** CE grades the `groups` record when it is
   present (a list of non-negative ints, no 0, refused by name as `unit-identity-invalid: <unit> ...`), and bounds the uid
   and gid values above (at most 4294967294: 4294967295 is `(uid_t)-1`). Rows for `"groups": [0]`, `"groups": "junk"`, a
   gid and a uid of 4294967295 and of 4294967296, each with its exact line. The re-captured records carry `groups`, so the
   new evidence must pass: the synthetic-pass fixture with `"groups": []` passes.
4. **R4-F5 (`tests/test_s0_05_egress.py` only).** A row that bind-mounts a same-filesystem directory on a parent at the
   first climb: the stop line names a mount (`a mount appeared above ...`). It kills the verifier's surviving mutant
   V4-mount-by-st_dev-only.

Out of scope: R4-F2 (re-pinning T's `LIVE_OUTPUT` after the PC re-capture: the coordinator's landing step), F-5, R4-F6, R4-F8,
R4-F9 (`netns_lib.sh` is outside your boundary), R4-F10.

## EVIDENCE DEMANDS

1. Premise: re-run the block below with `bash scripts/premise_block.sh` from the main tree; stop and report CONTRACT-INVALID
   if a lane file's hash differs.
2. Each item: red on round 4's bytes first, then green; a named mutant its test kills (a FAILED line); for item 2 the timing
   table at 1,100, 2,200 and 3,300 levels.
3. Gates, twice each, pasted with set ids: the 12 files of round 4's gate list (your round-4 section), and
   `tests/test_attested_inputs.py`'s S0-01 to S0-05 rows; the expected reds named exactly (T's 8 on F-11's line;
   `validate-ledger integrity` naming the same five proofs, S0-01 to S0-05).
4. Host state after every S0-05 run: `ip netns list` empty and the iptables rule set as it was before you started.
5. NOT-done and DISCREPANCIES, first in the section.

## BOUNDARY

The five files named in items 1-4 (`proofs/S0-03/check_omniroute_roundtrip.py`, `tests/test_s0_03_omniroute.py`,
`proofs/S0-05/tools/pc/run_s0_05_units.sh`, `proofs/S0-05/check_egress.py`, `tests/test_s0_05_egress.py`), in your
worktree, plus your report. Nothing else, and never the main tree.

## STANDING RULES

- Do NOT spawn subagents. No git writes, no PC bridge, no outward-facing action (no PR, comment, issue or publish).
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, GH_TOKEN, GITHUB_TOKEN. Test secrets are fakes built at run time.
- A private `--basetemp` outside every work tree for every pytest run (`mkdir -p` its parent); never run the whole
  `tests/test_vendored_manifest.py`. Counts pasted from `scripts/test_summary.sh` with set ids; stamps from `date -u`.
  Long commands in one foreground call each, under 10 minutes; kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text
  of its own.
- Append `## Round 5` to your report in the worktree (`tasks/briefs/i59/I59-F-report.md`); if the harness refuses the
  write, return the whole round-5 section as the text of your final hand-back message, in full.

## PREMISE — MEASURED at authoring (2026-09-28 22:1xZ, the main tree and the lane's worktree; `bash scripts/premise_block.sh`)

```
$ git -C /home/user/i59-landing log -1 --format='%h'
34d3af0
$ git -C /home/user/i59-landing status --porcelain | wc -l
16
$ sha256sum /home/user/i59-landing/proofs/S0-03/check_omniroute_roundtrip.py /home/user/i59-landing/proofs/S0-05/check_egress.py /home/user/i59-landing/proofs/S0-05/tools/pc/run_s0_05_units.sh /home/user/i59-landing/tests/test_s0_03_omniroute.py /home/user/i59-landing/tests/test_s0_05_egress.py | cut -c1-16,65- | sed 's#/home/user/i59-landing/##'
1e69424390142b44  proofs/S0-03/check_omniroute_roundtrip.py
383bbddc7b8140bc  proofs/S0-05/check_egress.py
5c4600661faeaf29  proofs/S0-05/tools/pc/run_s0_05_units.sh
9720944aa3e6da44  tests/test_s0_03_omniroute.py
aaca225c88805245  tests/test_s0_05_egress.py
$ grep -n 'def _walk_node\|def _walk_credentials\|is_credential_name(' /home/user/i59-landing/proofs/S0-03/check_omniroute_roundtrip.py | head -5
195:def is_credential_name(name: str) -> bool:
779:def _walk_credentials(node, path: str, _open=None):
794:def _walk_node(node, path: str, _open: set):
800:            if is_credential_name(key) and not key_is_allowed_env_name:
859:        if is_credential_name(name) and name not in ENV_CREDENTIAL_ALLOWLIST
$ grep -n 'def off_the_way\|stopped = off_the_way\|trap .* INT\|trap .*TERM' /home/user/i59-landing/proofs/S0-05/tools/pc/run_s0_05_units.sh | head -6
653:def off_the_way(fd, where):
717:            stopped = off_the_way(cur, where)
754:  trap '' INT TERM
766:# checker runs. (`trap cleanup EXIT INT TERM` ran cleanup on the signal and then CONTINUED, E3.)
776:trap 'trap "" INT TERM; exit 130' INT
777:trap 'trap "" INT TERM; exit 143' TERM
$ grep -n 'IDENTITY_KEYS\|"groups"\|refuse("gid 0")' /home/user/i59-landing/proofs/S0-05/check_egress.py | head -6
113:IDENTITY_KEYS = ("unit", "pid", "exe_realpath", "entrypoint_realpath", "entrypoint_sha256", "uid", "gid", "argv")
394:    if not isinstance(record, dict) or any(key not in record for key in IDENTITY_KEYS):
395:        refuse(f"unit-identity.json lacks one of {', '.join(IDENTITY_KEYS)}")
415:        refuse("gid 0")
$ sha256sum tasks/briefs/i59/I59-F.patch tasks/briefs/i59/VERIFY-I59-F-R4-report.md | cut -c1-16,65-
5cf9db295c98fddc  tasks/briefs/i59/I59-F.patch
be65de75d9c49032  tasks/briefs/i59/VERIFY-I59-F-R4-report.md
$ df -m / | tail -1
/dev/vda          258020 25920     12019  69% /
```
