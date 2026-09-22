# T90-R2 — the ONE focused repair of VERIFY-T90's two blockers on the lane dispatcher (D-031)

PIN: 435b057 (the post-push SHA of the VERIFY-T90 harvest commit; `scripts/pc_lane.sh` sha256[:16] 309d5cabe68ab150, byte-identical to c49880c)
LANE: pc-t90-r2
ROLE: code-implementer (build) — the STRICT local route: `HERMES_MODEL=qwen-local/qwen3.8-27b-local` (D-039(a) + D-042(2); a raw id routes without a combo, so OmniRoute's universal handoff cannot fire on this lane)
COMPONENT: `scripts/pc_lane.sh` (D, the sandbox dispatcher) + `harness-ports/tests/test_pc_lane_dispatcher.sh` (its tests) — NOTHING ELSE. The PC-side runner `harness-ports/bin/pc-lane.sh` is OUT of boundary.
CONTRACT REVISION: VERIFY-T90 report at `tasks/briefs/pc-t90-support/VERIFY-T90-report.md` (frozen: F1 + F3 are the blockers; F2/F4/F5/F6/F7 are issue #20 and NOT this lane's).
BUDGET: one repair round. Anything outside F1/F3 is reported as NOT-done, never built.

## What VERIFY-T90 proved (the two blockers, both reproduced by the coordinator 2026-09-22 15:28Z)

**F1 — the RESUME probe binds a live pid to THIS lane by a SUBSTRING match.** `scripts/pc_lane.sh:205` ships one remote command whose binding is
`case "$c" in "$d"|"$d"/*) b=1;; *) case "$n" in *"$d"*) b=1;; *) b=0;; esac;; esac`
where `$c` = the pid's cwd and `$n` = its cmdline joined by spaces. Two shapes pass that must be FIRST:
1. a SIBLING lane whose id is this id plus one byte (`<repo>/.lanes/b.md--aabbccddX` for lane `b.md--aabbccdd`): its argv contains the sibling path, which CONTAINS this lane's path as a substring → RESUME → the premise gate is skipped and a bad-premise brief SHIPS (`rc=75 ship=1 launch=1`);
2. ANY live process whose argv merely names this lane directory (cwd elsewhere) → RESUME the same way (the T91 pgrep false-binding class).
Coordinator reproduction (scratch dir, pidfile-bound sibling `bash -c 'echo $$ > "$1/sib.pid"; sleep 600; true' <sibling-dir> <sibling-dir>`, cwd = the sibling dir): the PIN's binding returned `b=1`; cwd containment alone returned `b2=0`; argv TOKEN equality returned `t=0`.

**F3 — the self-copy guard trusts an inherited `PC_LANE_SELF_COPY`.** `scripts/pc_lane.sh:52-53` skips the private copy whenever the variable is non-empty. With `PC_LANE_SELF_COPY=/scratch/caller-sentinel` in the environment, the ORIGINAL lazily-read file runs (the whole point of the copy defeated) and the EXIT trap (`:74`, `rm -f "${PC_LANE_SELF_COPY:-}"`) DELETES the caller's path. Verifier discriminator: `n2.sh caller_self_copy_sentinel` → `rc=64 bridge=1 sentinel_exists=NO`.

## The repair (exactly this, nothing wider)

### R-F1 — structural binding
Replace the substring binding with two exact tests, either sufficient:
- cwd containment: `case "$c" in "$d"|"$d"/*) b=1;; esac` (unchanged), AND/OR
- argv TOKEN equality: an argv ELEMENT (split on NUL, never on spaces) equal to `$d`, or equal to `$d/brief.md` (the lane's own brief path inside its dir) — never `*"$d"*`.
Read the cmdline NUL-separated (`tr '\0' '\n' < /proc/$p/cmdline` and compare line by line, or a `while IFS= read -r -d ''` loop) so a path with spaces is one token. Keep every other refusal in the probe as it is (absent/non-numeric/dead pid, unreadable stat → FIRST; only `RESUME <digits>` accepted by the caller). A sibling suffix id and an argv mention must now yield FIRST; a real resumed lane (cwd inside `$d`, or argv token `$d`/`$d/brief.md`) must still yield RESUME.

### R-F3 — the copy is recognized only when `$0` IS the copy
The guard trusts no inherited variable. Shape:
```
if [ -n "${PC_LANE_SELF_COPY:-}" ] && [ "$0" = "$PC_LANE_SELF_COPY" ] && [ -n "${PC_LANE_ORIG:-}" ]; then
  : # running from our own private copy
else
  unset PC_LANE_SELF_COPY PC_LANE_ORIG   # an inherited value never skips the copy
  … existing mktemp + cp + exec path, unchanged (rc 64 on mktemp/cp failure) …
fi
trap 'rm -f "$0"' EXIT        # only when $0 is the copy — never a caller-supplied path
```
The EXIT trap must remove ONLY the process's own copy (`$0` after the exec), never a value read from the environment. An inherited `PC_LANE_SELF_COPY=/scratch/caller-sentinel` must (a) not skip the copy, (b) leave the sentinel in place, (c) refuse the bad-premise brief through the normal path with rc 64.

### Tests (in `harness-ports/tests/test_pc_lane_dispatcher.sh`, through the fake bridge only)
Add, each RED before the repair and GREEN after (paste both runs):
1. `sibling suffix id is FIRST` — a scratch lane dir `<X>` and a live process (pidfile-bound, started with `setsid nohup bash -c 'echo $$ > "$1/sib.pid"; sleep 300; true' "<X>X" "<X>X"` from cwd `<X>X`) whose pid is written to `<X>/lane.pid`; the probe (run through the fake bridge that executes the quoted probe locally, as the verifier's second harness did) must print FIRST and the dispatcher must refuse the bad-premise brief with rc 64, ship=0.
2. `argv mention alone is FIRST` — a live process with cwd `/tmp`-like scratch and the lane dir only as an argument → FIRST, rc 64, ship=0.
3. `argv token equal to the lane dir is RESUME` — the positive control: a live process whose argv element IS `<X>` (cwd elsewhere) → RESUME, and the existing bound-live control (cwd inside `<X>`) stays green.
4. `inherited PC_LANE_SELF_COPY does not skip the copy and is not deleted` — run D with `PC_LANE_SELF_COPY=<scratch>/caller-sentinel` (an existing file) on a bad-premise brief: rc 64, the sentinel EXISTS afterwards, the bridge probe count is what the normal path makes, and stderr shows the private-copy path is a `pc_lane.sh.XXXXXX` mktemp file (not the sentinel).
5. `the EXIT trap removes only $0` — after a normal run, the mktemp copy is gone and any other path named in the environment is untouched.
Kill the processes you start BY PID FROM THE PIDFILE (never `pkill -f`/`pgrep -f` with the target's text in the same command line — the coordinator's shell died of exactly that at 15:3xZ, rc 144).

### Gates (paste verbatim)
- `bash harness-ports/tests/test_pc_lane_dispatcher.sh` twice (the RESULT lines + counts, bitwise-identical); `bash -n scripts/pc_lane.sh`.
- Mutants, each re-run in place with a scratch-copy restore and the killing test named: (m1) restore the substring binding `*"$d"*`; (m2) drop the argv token test; (m3) drop the `[ "$0" = "$PC_LANE_SELF_COPY" ]` conjunct; (m4) restore the trap to `${PC_LANE_SELF_COPY:-}`; (m5) split the cmdline on spaces instead of NUL. Paste each run's failing test name.
- `harness-ports/tests/run-all.sh` if it runs under the 420 s cap per call (else the dispatcher test file alone, stated).
- `python3 scripts/report_lint.py --min-refs 10 <your report>`; `python3 scripts/ap_screen.py scripts/pc_lane.sh --tests harness-ports/tests/test_pc_lane_dispatcher.sh` (paste the hit table; a pre-existing hit is stated as such with its PIN line).

## Report (`tasks/briefs/pc-t90-support/T90-R2-report.md`)
DATA, not prose: files:lines changed; the RED→GREEN pairs for tests 1-5 pasted; the five mutant rows; the two gate runs; DISCREPANCIES / NOT-done (F2/F4/F5/F6/F7 are NOT this lane's — say so). No claim without its pasted output. Never touch `harness-ports/bin/pc-lane.sh`, the ledger, the wiki, or any brief.

## PREMISE — MEASURED at authoring (2026-09-22 15:3xZ, sandbox clone @ 435b057 — both boundary files byte-identical to c49880c: `git diff --stat c49880c 435b057 -- scripts/pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh` prints nothing; re-verify at the PIN before editing)
```
$ grep -oF 'case \"\$n\" in *\"\$d\"*) b=1;;' scripts/pc_lane.sh | head -1
case \"\$n\" in *\"\$d\"*) b=1;;
$ grep -cF 'in *\"\$d\"*)' scripts/pc_lane.sh
1
(the substring binding is present exactly once, inside the quoted bridge command at :205)
$ sed -n '52,53p' scripts/pc_lane.sh
PC_LANE_SELF_COPY="${PC_LANE_SELF_COPY:-}"
if [ -z "$PC_LANE_SELF_COPY" ]; then
$ sed -n '74p' scripts/pc_lane.sh
trap 'rm -f "${PC_LANE_SELF_COPY:-}"' EXIT
$ grep -c 'check "' harness-ports/tests/test_pc_lane_dispatcher.sh
24
$ wc -l scripts/pc_lane.sh harness-ports/tests/test_pc_lane_dispatcher.sh
 555 scripts/pc_lane.sh
 303 harness-ports/tests/test_pc_lane_dispatcher.sh
```
Coordinator reproduction of F1 (2026-09-22 15:28:43Z, scratch dir): `PIN probe binding for the SUFFIX sibling (contract expects FIRST=0): b=1` · `cwd-containment-only binding: b2=0` · `argv TOKEN-equality binding: t=0`.
