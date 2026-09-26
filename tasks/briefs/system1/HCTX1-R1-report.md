# HCTX1-R1 report: refresh on relaunch (#316) and the repo root (#317)

Lane: code-implementer (sandbox, Opus 5.5). Brief: `tasks/briefs/system1/HCTX1-R1-brief.md`. PIN: origin 2a50a65.
Started: 2026-09-26 06:2xZ. Written incrementally; final checks in section 12.

**Status. DONE (sandbox tests green; not verified live).** `create` on an existing lane profile now rewrites its
`config.yaml` from the source by the new-clone rule, keeps every other file, refuses a non-directory or a profile with no
`config.yaml` by name, and a second `create` writes nothing. Both root sites use `../..`, and the test states the hook path
as a literal. Evidence: `lane profile: 30 passed, 0 failed` twice, `67 passed, 0 failed` twice, `ALL SUITES PASSED`; the PIN
helper is red on 7 checks; 12 of 12 named mutants killed. NOT run: the PC check (section 7; no PC bridge in this lane).
`pc-lane.sh` needs no change (section 8).

## 1. Premise re-measure (verified)

Measured 2026-09-26 06:2xZ in the sandbox tree. HEAD moved past the brief's authoring commit (coordinator commits only);
`git diff --stat 2a50a65 HEAD` over lane-profile.sh, test_lane_profile.sh, pc-lane.sh and test_pc_lane.sh prints nothing,
and `git status --short -- harness-ports/` prints nothing. The last commit to touch the two lane-profile files is
847d3eb (HCTX1, 2026-09-26T04:27:59Z).

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-60
2a50a65 I59-A round 1 home (task #312; held for the issue #5
$ grep -n -E '^create_lane|if \[ -e "\$target" \]; then|verify_lane "\$lane"|/\.\./\.\./\.\.' harness-ports/bin/lane-profile.sh
84:  verdict="$(python3 - "$target/config.yaml" "$lane" "$SOURCE/config.yaml" "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)" \
188:create_lane() {
194:  if [ -e "$target" ]; then
195:    verify_lane "$lane"
216:  python3 - "$target/config.yaml" "$lane" "${LANE_DONE_GATE:-0}" "$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)" \
453:  verify_lane "$lane"
$ grep -n -E 'lane-done-gate|\.\./\.\./\.\.' harness-ports/tests/test_lane_profile.sh | head -6
284:python3 - "$TMP/source-config.yaml" "$GATE_ON" "$(cd "$HERE/../../.." && pwd)" gateon <<'PY'
296:helper = f"{root}/harness-ports/bin/lane-done-gate.py"
333:    "lane-done-gate.py gate", "lane-done-gate.py changed"
$ ls harness-ports/bin/lane-done-gate.py
harness-ports/bin/lane-done-gate.py
$ bash harness-ports/tests/test_lane_profile.sh | tail -1; bash harness-ports/tests/test_pc_lane.sh | tail -1
lane profile: 24 passed, 0 failed
67 passed, 0 failed
```

Verdict: the premise block matches line for line (both exit codes 0). No CONTRACT-INVALID so far.

## 2. Grounding (06:3xZ)

- [verified, code] `pc-lane.sh:447` sets `LANE_PROFILE_HELPER` to the PC clone's copy of the helper, not the lane tree's;
  `AF_REPO` defaults to the clone (`pc-lane.sh:68`, `AF_REPO:=$HOME/agent-factory`).
  `pc-lane.sh:453` runs it as `create "$LANE_ID"` on every launch, and `pc-lane.sh:454` then runs `verify "$LANE_ID"`.
  It never removes a lane profile, and the lane id ends in the PIN's first 8 characters (`pc-lane.sh:85`, `LANE_ID`), so a
  relaunch at the same PIN reaches the existing-profile branch of `create`. It does not set `LANE_DONE_GATE`; the helper
  reads it from the environment.
- [verified, code] Hermes at the lane runtime pin b3399c1 (`upstream.lock.yaml` `lane_runtime`), `hermes_cli/profiles.py`:
  `create_profile` makes a real directory (`_bootstrap_profile_dir`), copies `config.yaml`, `.env` and `SOUL.md` with
  `shutil.copy2` (`_clone_file`), then `_migrate_profile_config_if_outdated` rewrites the copy only when its config version
  is below the latest. The helper's verify compares the lane config semantically with the SOURCE-derived expected config, so a
  lane that verifies was cut from a source equal to its clone's copy. Reading the SOURCE on a relaunch therefore applies the rule
  to the same input a new clone gets.
- [verified, code] A Hermes delete writes its tombstone OUTSIDE the profile directory (`profile_tombstone_path` =
  `<profiles>/<deleted dir>/<name>`, `hermes_constants.py` at b3399c1) and removes the directory.
- [verified, code] `lane-done-gate.py:20` finds the gate's own repo root as `parents[2]`, which is `../..` from `bin/`:
  the helper's `../../..` disagrees with the gate's own view.
- Impact: `node .gitnexus/run.cjs impact create_lane|verify_lane --direction upstream` returns "Target not found", risk
  UNKNOWN (bash functions are not indexed). A text search (`git grep -n -E '\b(create_lane|verify_lane)\b'`, run before my
  edit, so the lines below are PIN lines) finds callers only inside the helper, plus historical patch files under
  `tasks/briefs/pc/`:
  - `lane-profile.sh@2a50a65:195` `verify_lane "$lane"` (the existing-profile early return this change replaces);
  - `lane-profile.sh@2a50a65:453` `verify_lane "$lane"` (after a new clone's rewrite);
  - `lane-profile.sh@2a50a65:471` `create_lane "$VALUE"` and `lane-profile.sh@2a50a65:472` `verify_lane "$VALUE"`.
  The helper is run by `pc-lane.sh:453` (`LANE_PROFILE_HELPER`), and never by the plumbing suite:
  `test_pc_lane.sh:57` writes its own fake over `$REPO/harness-ports/bin/lane-profile.sh`.

## 3. Design (06:3xZ)

- `create` on an existing lane profile: refuse a target that is not a real directory ("profile not a directory <name>"; a
  symlink counts as not a directory, so the rewrite can never land in the directory it points to, which could be the base
  profile), refuse a directory with no `config.yaml` ("profile has no config.yaml <name>"), then run the SAME rewrite with the
  SOURCE's `config.yaml` as its input and the lane's `config.yaml` as its output, then verify. No clone call, no copy of
  `hooks`/`cron`, no touch of `.env`, `state.db` or anything else.
- The rewrite takes its input and output as two arguments. A new clone passes its own copy as both (unchanged behavior); a
  relaunch passes the source's file as input. A result byte-equal to the lane's current `config.yaml` is not written, so a
  second `create` is a true no-op (same bytes, same inode).
- Both root sites: `../../..` to `../..`. The test's expected hook path is `${HERE%/harness-ports/tests}` plus
  `/harness-ports/bin/lane-done-gate.py` (the test's own known place, no `..` arithmetic), and the file must exist.
- Rejected: always rewriting (a new inode on every relaunch while the contract asks for a no-op); reading the SOURCE on the
  new-clone path too (would drop a Hermes-side clone-time edit that the current path keeps; not asked); deleting and
  re-cloning an existing profile (loses `state.db`; the contract forbids a silent re-clone).

## 4. The change

`harness-ports/bin/lane-profile.sh` (the logical diff is `git diff -w`; the clone block is re-indented into an `else`):
- `lane-profile.sh:84` (`verdict=`, in `verify_lane`): the root is `../..` from `bin/` (was `../../..`).
- `lane-profile.sh:194` (`if [ -e "$target" ]`): an existing target now takes the refresh branch.
- `lane-profile.sh:199` refuses a target that is not a real directory (`profile not a directory`, `[ ! -L "$target" ]`).
- `lane-profile.sh:200` refuses a directory with no config (`profile has no config.yaml`).
- `lane-profile.sh:201` (`from="$SOURCE/config.yaml"`): a relaunch rewrites from the source's file.
- `lane-profile.sh:209` (`for component in hooks cron`) and `lane-profile.sh:214` (`from="$target/config.yaml"`): a new
  clone keeps its old path (clone, `hooks`/`cron` copy), and its own copy is the input.
- `lane-profile.sh:221` (`python3 - "$from"`): the rewrite takes its input and output as two arguments; its root is `../..`.
- `lane-profile.sh:232` (`src, path = Path(sys.argv[1])`) and `lane-profile.sh:263` (`src.read_text`): the text is read
  from the input; the other arguments shift by one.
- `lane-profile.sh:444-445` (`path.read_bytes()`): a result equal to the lane's current bytes exits 0 before any temp file.
- Not changed: `quadlet_context_length`, `verify_lane` (except its root), `remove_profile`, the rewrite's rules and guards,
  the base profile, `pc-lane.sh`.

`harness-ports/tests/test_lane_profile.sh`:
- `test_lane_profile.sh:12` sets `REPO_ROOT` from the test's own place (`${HERE%/harness-ports/tests}`, refused unless the
  suffix was there), and `test_lane_profile.sh:14` sets `GATE_PY` from it.
- `test_lane_profile.sh:289` (check #11, switch ON) builds its expected hooks from `"$REPO_ROOT"` (was the mirrored
  `$HERE/../../..` formula).
- `test_lane_profile.sh:327` (new #12) compares the two parsed hook commands with `python3 $GATE_PY record` and `gate`, and
  requires that `$GATE_PY` exists.
- New #25-#29 (before the base-hash check, now #30): relaunch of an old-style profile, the second-create no-op (switch OFF and
  ON), `.env` kept, a non-directory lane path (a file; a symlink to an old-style profile), a profile with no `config.yaml`.
- A first-draft defect in my own test, fixed before any gate: #26 grepped the config text for `lane-done-gate.py gate` and
  failed on a correct config, because PyYAML folds the long command at 80 columns (`command: python3 <root>/.../lane-done-gate.py`
  then `gate` on the next line; the value round-trips intact). The check now compares the parsed value
  (`test_lane_profile.sh:609`, `IG_GATE`).

## 5. Negative controls (06:4xZ; driver `nc.py` in scratch, pasted)

The NEW test runs in a scratch tree per variant (`<scratch>/nc/<name>/harness-ports/{bin,tests}`, deleted after the run): the
unmutated helper first (it must pass all 30), the PIN helper (`git show 2a50a65:harness-ports/bin/lane-profile.sh`), then 12
named mutants of the new helper, each an exact-string replacement with an asserted count. A kill is a FAILED check in a suite that
reached its summary line with 30 checks and ran in its own tree (the #12 because-line names that tree); anything else is INVALID
(AF-AP-223). The denominator is the literal EXPECTED=12.

```
== control (new helper 9b2aa7961970): rc=0 | lane profile: 30 passed, 0 failed | ran_in_own_tree=True
== PIN 2a50a65 (helper 8192cb678b8c): rc=1 | lane profile: 23 passed, 7 failed | RED | fails #11 #12 #25 #26 #27 #28 #29
== M1-root-both-3up (helper e8a75063a846): rc=1 | lane profile: 27 passed, 3 failed | KILLED | fails #11 #12 #26
== M2-root-create-3up (helper 17799a88494e): rc=1 | lane profile: 27 passed, 3 failed | KILLED | fails #11 #12 #26
== M3-root-verify-3up (helper fa7073735363): rc=1 | lane profile: 28 passed, 2 failed | KILLED | fails #11 #26
== M4-no-refresh (helper 1d0cc2e4d7e3): rc=1 | lane profile: 25 passed, 5 failed | KILLED | fails #25 #26 #27 #28 #29
== M5-refresh-in-place (helper 242a079874ed): rc=1 | lane profile: 27 passed, 3 failed | KILLED | fails #25 #26 #27
== M6-always-write (helper 13a40325305b): rc=1 | lane profile: 29 passed, 1 failed | KILLED | fails #26
== M7-no-dir-check (helper 5e977e478744): rc=1 | lane profile: 29 passed, 1 failed | KILLED | fails #28
== M8-follow-symlink (helper d52ff770091e): rc=1 | lane profile: 29 passed, 1 failed | KILLED | fails #28
== M9-no-config-check (helper 2bfc41a9cd85): rc=1 | lane profile: 29 passed, 1 failed | KILLED | fails #29
== M10-silent-reclone (helper 773cd7662d73): rc=1 | lane profile: 24 passed, 6 failed | KILLED | fails #3 #25 #26 #27 #28 #29
== M11-env-resync (helper f3385e9eed64): rc=1 | lane profile: 29 passed, 1 failed | KILLED | fails #27
== M12-refresh-ignores-switch (helper 211d36e9e697): rc=1 | lane profile: 29 passed, 1 failed | KILLED | fails #26
EXPECTED=12 RAN=12 KILLED=12 SURVIVED=0 INVALID=0
NC VERDICT: PASS
```
Check numbers (from the control run's order): #3 create reuses an existing verified profile; #11 switch ON (literal root);
#12 the done-gate hook path literal; #25 relaunch of an old-style profile; #26 the second-create no-op, OFF and ON; #27 `.env`
kept; #28 a non-directory lane path; #29 a profile with no `config.yaml`; #30 the base-profile hashes.

Mutants (each applied alone to the new helper):
- M1 both roots back to `../../..` (the PIN's formula, the mirrored-oracle case the old test passed); M2 the create root only;
  M3 the verify root only.
- M4 the PIN's existing-profile branch (verify, print, return); M5 the refresh reads the lane's own `config.yaml` (in place)
  instead of the source's; M6 the no-op skip removed (always write); M7 the directory check removed; M8 the symlink part of it
  removed; M9 the `config.yaml` check removed; M10 a silent re-clone (`rm -rf` the target first); M11 the refresh also re-copies
  the source `.env`; M12 the refresh ignores `LANE_DONE_GATE`.

Each new or changed check reds on the PIN or on a named mutant, and has a dedicated killer: #11 M1-M3, #12 M1 M2, #25 M4 M5
M10, #26 M6 M12, #27 M11, #28 M7 M8, #29 M9. One prediction of mine was wrong: I expected #27 to pass on the PIN and on M4. It
fails there as a cascade (the unrefreshed config makes verify stop at "context override missing" before the env check), so on
those two runs #27 is not independent evidence; M11 is its independent killer.

## 6. Gates (06:4xZ; pasted; final files: `lane-profile.sh` sha256 `9b2aa796197009da…`, `test_lane_profile.sh` sha256 `cfbed752380da49c…`)

Set: every test that names a changed path. `grep -l -r 'lane-profile' tests/ harness-ports/tests/` gives
`harness-ports/tests/test_pc_lane.sh` and `harness-ports/tests/test_lane_profile.sh`; `tests/test_shell_syntax.py` runs
`bash -n` over every tracked `.sh` file (`git ls-files`), so it reads both changed files as data. CI runs the lane-profile
suite through `run-all.sh` in `stage0-ci.yml`'s `harness-suites` job (ubuntu-latest, PyYAML installed).

The two suites, twice each (06:42:57Z to 06:43:31Z by `date -u`); verdict-lines sha = sha256 of the PASS/FAIL lines, identical
across the runs, so the verdicts repeat. `test_pc_lane.sh`'s `fd1529455606` is the value HCTX1 recorded: that suite's verdicts
did not move.
```
run1 test_lane_profile.sh   rc=0 | lane profile: 30 passed, 0 failed | verdict-lines sha 5a100792adce
run1 test_pc_lane.sh        rc=0 | 67 passed, 0 failed | verdict-lines sha fd1529455606
run2 test_lane_profile.sh   rc=0 | lane profile: 30 passed, 0 failed | verdict-lines sha 5a100792adce
run2 test_pc_lane.sh        rc=0 | 67 passed, 0 failed | verdict-lines sha fd1529455606
```
(The rc values above were printed by the run loop from each suite's own exit status, not from a pipe.)

`bash harness-ports/tests/run-all.sh`, once, 06:43:38Z to 06:45:05Z, rc 0:
```
test_codex_hook_adapter.py         7/7 passed
test_hermes_hook_adapter.py        6/6 passed
test_hermes_spool.py               9/9 passed
test_lane_done_gate.py             lane done gate: 19 passed, 0 failed
test_bridge_token_handling.py      test_bridge_token_handling: 9 checks passed — ALL OK
test_pc_bridge_exec.py             test_pc_bridge_exec: 8 checks passed
test_hermes_session_export.py      test_hermes_session_export: 15 checks passed
test_omniroute_local_builder.py    test_omniroute_local_builder: 24 checks passed
test_lane_profile.sh               lane profile: 30 passed, 0 failed
test_pc_lane.sh                    67 passed, 0 failed
test_pc_lane_dispatcher.sh         pc_lane dispatcher: 51 passed, 0 failed
test_pc_lane_admission.sh          22 passed, 0 failed
test_qwen_server.sh                qwen-server: 101 passed, 0 failed
test_qwen_matrix.py                test_qwen_matrix: 4 tests passed
test_qwen_matrix_sh.sh             qwen-matrix-sh: 19 passed, 0 failed
test_lane_context.sh               5 passed, 0 failed
test_context_mirrors.sh            11 passed, 0 failed
test_sync_skills.sh                34 passed, 0 failed
build-roles --check                OK: 3 role config layers match their sources
ALL SUITES PASSED
```
`bash scripts/test_summary.sh tests/test_shell_syntax.py -p no:cacheprovider --basetemp=<scratch>` (a one-file set), rc 0:
```
pytest-exit: 0
pytest-summary: 4 passed in 1.20s
```
(A first call passed an extra `-q`; with the script's own that made `-qq`, which prints no count line, so it was re-run without
it. Both runs exited 0.)

- `bash -n harness-ports/bin/lane-profile.sh`: rc 0; `bash -n harness-ports/tests/test_lane_profile.sh`: rc 0.
- `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>`: `0` for the helper, the test, this report and the scratch driver (last run in
  section 12).
- `python3 scripts/ap_screen.py` on both files: `14 hits over 2 files` (AF-AP-118: 12, AP-51: 2); on the PIN versions of both files:
  `13 hits over 2 files` (AF-AP-118: 12, AP-51: 1). The one new hit is AP-51 on check #26's name ("byte-identical"). AP-51 is
  the byte-identity claim tell for a dataclass field feeding an asdict sink; here the claim is about `config.yaml` bytes and is
  backed by a real `cmp -s`, so it is by design, as HCTX1 judged the same row on check #10. AF-AP-118 matches the
  `fallback_providers` strings in code whose job is to strip that chain (unchanged count).

Binding: the helper's sha256 prefix `9b2aa7961970` is the helper the driver ran as its control (section 5). The test file was
last written at 06:39:01Z and the driver read it at 06:40:40Z; independently of clocks, the only earlier 30-check draft failed
#26, and the driver aborts unless its control passes all 30. No edit to either file followed the gates.

## 7. The coordinator's PC check (commands only; NOT run here: no PC bridge in this lane, by rule) (06:5xZ)

Run after the landing and the PC clone's ff-sync, in one `scripts/pc.sh` call (a few seconds; a replay after a bridge timeout
stops at the existence guard). It creates a lane profile the old way (a plain Hermes clone), relaunches it through the new
helper, reads the per-model `context_length` through Hermes's own code (HCTX1 report section 6, only the profile name changed),
checks the done-gate root on the PC's layout, and removes the profile. It sends no model request, prints no key, reads no
`.env` (the helper's own verify compares `.env` hashes), and hashes the owner's `config.yaml` before and after.

```bash
cd ~/agent-factory && git log -1 --format='%h %s' | cut -c1-70   # expect the landing commit (the clone is ff-synced)
H=harness-ports/bin/lane-profile.sh; L=hctx1r1-pc-check; P=aflanehctx1r1pccheck; D="$HOME/.hermes/profiles/$P"
[ ! -e "$D" ] || { echo "stop: $D already exists"; exit 1; }
sha256sum "$HOME/.hermes/profiles/agentfactory/config.yaml" > /tmp/hctx1r1-base.sha
# 1. The old way: a plain Hermes clone (the chain kept, no lane header, no context block), then two planted files.
hermes profile create --clone-from agentfactory --no-alias "$P" >/dev/null; echo "plain clone rc=$?"
bash "$H" verify "$L"; echo "verify before rc=$?"     # expect rc 64 ("chain present", or "header missing or wrong: <missing>")
python3 -c 'import sqlite3, sys; c = sqlite3.connect(sys.argv[1]); c.execute("create table t (x)"); c.commit()' "$D/state.db"
printf 'pc-check marker\n' > "$D/pc-check-marker.txt"
keep() { (cd "$D" && find . -type f ! -path ./config.yaml ! -path ./.env -print0 | LC_ALL=C sort -z | xargs -0 sha256sum | sha256sum | cut -c1-16); }
K1="$(keep)"
# 2. The relaunch: create on the existing profile through the new helper, then verify, then a second create.
bash "$H" create "$L"; echo "create rc=$?"            # expect "aflanehctx1r1pccheck", rc 0, and NO stderr line
bash "$H" verify "$L"; echo "verify rc=$?"            # expect rc 0 and no output
echo "other files kept: $([ "$K1" = "$(keep)" ] && echo yes || echo NO)"   # state.db, the marker, skills, memories...
I1="$(stat -c %i "$D/config.yaml")"; bash "$H" create "$L" >/dev/null
echo "second create rc=$? inode_same=$([ "$(stat -c %i "$D/config.yaml")" = "$I1" ] && echo yes || echo NO)"
# 3. Hermes's own resolution of the per-model context_length (HCTX1 report section 6).
HERMES_HOME="$D" ~/.hermes/hermes-agent/venv/bin/python - <<'PY'
from hermes_cli.config import load_config, get_compatible_custom_providers, get_custom_provider_context_length
from hermes_cli.runtime_provider import resolve_runtime_provider
from agent.model_metadata import get_model_context_length
cfg = load_config()
cps = get_compatible_custom_providers(cfg)
for m in ("agentfactory-build-local", "agentfactory-verify-local", "qwen-local/qwen3.8-27b-local"):
    try:
        base = resolve_runtime_provider(requested=cfg["model"]["provider"], target_model=m)["base_url"]
    except Exception as exc:  # prints the class only, never a value
        base = cfg["model"]["base_url"]; print("runtime resolver:", type(exc).__name__, "-> model.base_url")
    ctx = get_custom_provider_context_length(model=m, base_url=base, custom_providers=cps)
    print(m, "| base_url", base, "| per-model", ctx, "| resolved", get_model_context_length(m, base_url=base, config_context_length=ctx))
PY
# 4. The repo root (#317) on the PC's layout: a relaunch with the switch ON names an existing gate file; then OFF again.
LANE_DONE_GATE=1 bash "$H" create "$L" >/dev/null; echo "gate-on relaunch rc=$?"
python3 - "$D/config.yaml" <<'PY'
import os, sys, yaml
hooks = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))["hooks"]
for command in (hooks["post_tool_call"][-1]["command"], hooks["pre_verify"][0]["command"]):
    _, path, verb = command.split()
    print(verb, path, "exists" if os.path.isfile(path) else "MISSING")
PY
bash "$H" create "$L" >/dev/null; echo "gate-off relaunch rc=$?"
# 5. Remove the profile; the owner's profile is unchanged.
bash "$H" remove "$P"; echo "remove rc=$?"; ls -d "$D" 2>&1 | tail -1   # expect: No such file or directory
sha256sum -c --quiet /tmp/hctx1r1-base.sha && echo "base config.yaml unchanged"; rm -f /tmp/hctx1r1-base.sha
```

Pass: step 1 verify rc 64 (the plain clone is really old-style); step 2 create prints only the name (a `lane-profile:
context_length 131072: ...` line would mean the quadlet was not read), verify rc 0, "other files kept: yes", "second create rc=0
inode_same=yes"; step 3 prints `per-model <MAX_LEN> | resolved <MAX_LEN>` for each model (131072 on HCTX1's premise; a
`per-model None` for `qwen-local/qwen3.8-27b-local` alone is HCTX1's open inference, its section 1c); step 4 prints `record` and
`gate` with `$HOME/agent-factory/harness-ports/bin/lane-done-gate.py exists`, and both relaunch rcs are 0; step 5 prints "No such
file or directory" and "base config.yaml unchanged". The hook line is parsed, never grepped: PyYAML folds that long command at 80
columns (section 4).

## 8. Does `pc-lane.sh` need a change for this to reach a relaunch? No.

- [verified, code] Every launch that passes the state guard runs the helper. The guard needs no non-empty report
  (`pc-lane.sh:102`, `-s "$REPORT"`) and no live pidfile (`pc-lane.sh:106`, `kill -0`).
  Then `pc-lane.sh:453` runs `create "$LANE_ID"` and `pc-lane.sh:454` runs `verify "$LANE_ID"`, through `LANE_PROFILE_HELPER`:
  the PC clone's working-tree copy, not the pinned lane tree's. The launcher fetches origin (`pc-lane.sh:177`, `fetch origin`) but never
  moves the clone's working tree, so the refresh reaches every relaunch once the PC clone is ff-synced to the landing, whatever
  PIN the brief carries.
- A lane that died at "lane profile create failed" (the D-1 symptom) has no report, so its relaunch reaches `create` and is
  refreshed. A lane that already produced a report is re-printed, never re-run (unchanged).
- `pc-lane.sh` does not set `LANE_DONE_GATE`; a relaunch adds or drops the gate hooks by the switch in the caller's
  environment at relaunch time, the same rule as a new clone.

## 9. Self-attack: the three likeliest ways this change is wrong

1. **The refresh writes a file it must not (the base profile, a live lane's config).** The old `create` never wrote an existing
   profile; this one does. Ruled out as far as the sandbox can: the target must be a real directory, not a symlink (#28 with a
   symlink to an old-style profile; M7 and M8 killed), so the write never lands in a linked directory; the base-hash check (#30)
   holds across every create in the suite, including the relaunch path; a live lane of the same id is refused before `create`
   runs (`pc-lane.sh:106`, `kill -0`); the write is atomic (temp file and `os.replace` inside the profile) and
   is skipped when the bytes are current (#26; M6 killed). Residual [inferred, not tested]: an operator who sets
   `HERMES_SOURCE_PROFILE` to the lane's own `aflane*` name makes the target the source; the helper does not refuse that, and a
   rewrite of a current profile is then a byte no-op.
2. **"The same rule a new clone gets" is false on the PC.** It holds only if a new clone's input equals the source's bytes.
   Ruled out in code at b3399c1 (section 2): the clone gets `config.yaml` by `shutil.copy2`, a migration runs only when the
   config version is outdated, and verify refuses any clone whose config differs semantically from the source's. #25 pins the
   refreshed bytes to a new clone's bytes (M5 killed; the fake Hermes byte-copies, like `copy2`). Residual [inferred]: a future
   Hermes that re-serializes `config.yaml` at clone time with no semantic change would make a new clone's bytes differ from a
   refreshed profile's; both would still verify. The PC check (section 7) measures the refresh on the real Hermes.
3. **The root is right only for the invocation `pc-lane.sh` uses.** `../..` is resolved from `${BASH_SOURCE[0]}`; a helper run
   through a symlink outside the repo would resolve a wrong root, as would every sibling script that spells the root the same way
   (`hook-shim.sh:31`, `sync-lane-skills.sh:7`, `mcp-server.sh:39`: each `/../.." && pwd`). `pc-lane.sh` runs the real path; the test pins the
   literal path and the file's existence (#12, and #26's gate leg), the gate file's own `parents[2]` agrees, and M1-M3 are
   killed. Section 7 step 4 measures it on the PC's layout.

## 10. NOT done

- NOT run: the PC check (section 7). No PC bridge in this lane, by rule. The refresh and the root are proven in the sandbox
  against the fake Hermes only.
- NOT done: no commit, no push, no registry edit (`docs/INCIDENT-LOG.md` is outside my boundary). AF-AP-226's row still reads
  "OPEN: task #317"; its fix shape (both sites, a literal expected path, a negative control) is what this lane did. No registry
  row for #316's class (a create-or-reuse step that only verifies an existing artifact, so a rule change strands it). A bounded
  read-only scan (`harness-ports/bin/*.sh`, `scripts/*.sh`, existence-test branches that verify or return) found one reuse
  branch, `jev-pruner-setup.sh:20` (`$JEV_ROOT/.git`), which re-pins after reuse, so 0 siblings. This is NOT a `/bug-echo`
  run.
- NOT changed: `harness-ports/bin/pc-lane.sh` (no change needed, section 8).
- NOT tested: a relaunch with the switch flipped (a gate-ON profile relaunched OFF drops the hooks; the reverse adds them). It
  runs the same shared rewrite as #10/#11, but no check pins the flip itself.
- NOT tested: the operator-misuse case in self-attack 1 (the source profile set to the lane's own name).

## 11. DISCREPANCIES, deviations, adjacent defects

Premise: no mismatch (section 1). HEAD moved past 2a50a65 by coordinator commits only; the files in scope are unchanged.

Deviations and design choices beyond the letter of the contract (each is tested):
- A symlinked lane path counts as "not a directory" (the contract names "not a directory"), even when it points to a directory:
  the refresh would otherwise write through the link (#28, M8).
- The second-create no-op is "not written at all" (same inode, no temp file), stronger than the contract's "byte-identical"
  (#26, M6).
- `.env` is kept, as the contract says, so a relaunch after the SOURCE's `.env` changed still fails with "env drift", exactly as
  before this change; the operator step stays `lane-profile.sh remove aflane<id>` (#27, M11).
- `hooks/` and `cron/` are not refreshed on a relaunch (the contract keeps "any other file or directory"): a source `hooks/`
  added after a lane was cut reaches new clones only. This is D-1's class for directories; not in the contract.
- Check #11 changed its oracle (the literal root in place of the mirrored formula); it fails on the PIN helper and on M1-M3.

Adjacent (found, NOT fixed):
- A-1 [inferred from the Hermes code at b3399c1, not run]: `_bootstrap_profile_dir` makes an empty `cron/` in every new profile
  (`_PROFILE_DIRS`), so the helper's cron copy (`lane-profile.sh:209`, `for component in hooks cron`) never fires under the real Hermes and lane
  profiles get no source cron jobs. The test's fake Hermes makes no `cron/`, so check #2's "copies hooks/cron" passes only
  against the fake (a fake that does not model the real clone's layout). Whether a lane should carry the owner's cron jobs is a
  design question (lanes run `hermes -z`, with no gateway).
- A-2 (observation): PyYAML folds the hook command at 80 columns in a lane config (valid YAML, the value is intact), so a text
  grep for the gate path misses it. My own first draft of #26 hit exactly this (section 4).
- HCTX1's A-2 is still open: `pc-lane.sh:24` and `pc-lane.sh:427` say "262k slot"; not mine.

## Appendix: the 12 mutants, exact (pasted from the scratch driver `nc.py`; each `(old, new, expected count)`, applied alone to the
new helper; the verdict rules are in section 5)

```python
ROOT_OK = '"${BASH_SOURCE[0]}")/../.." && pwd)"'
ROOT_3UP = '"${BASH_SOURCE[0]}")/../../.." && pwd)"'
CREATE_CALL = 'python3 - "$from" "$target/config.yaml" "$lane" "${LANE_DONE_GATE:-0}" "$(cd "$(dirname '
VERIFY_CALL = 'verdict="$(python3 - "$target/config.yaml" "$lane" "$SOURCE/config.yaml" "$(cd "$(dirname '
DIR_CHECK = '    [ -d "$target" ] && [ ! -L "$target" ] || fail "profile not a directory $name"\n'
CONF_CHECK = '    [ -f "$target/config.yaml" ] || fail "profile has no config.yaml $name"\n'
FROM_SOURCE = '    from="$SOURCE/config.yaml"\n'

MUTANTS = {
    "M1-root-both-3up": [(ROOT_OK, ROOT_3UP, 2)],
    "M2-root-create-3up": [(CREATE_CALL + ROOT_OK, CREATE_CALL + ROOT_3UP, 1)],
    "M3-root-verify-3up": [(VERIFY_CALL + ROOT_OK, VERIFY_CALL + ROOT_3UP, 1)],
    "M4-no-refresh": [(DIR_CHECK, '    verify_lane "$lane"; printf \'%s\\n\' "$name"; return 0\n', 1)],
    "M5-refresh-in-place": [(FROM_SOURCE, '    from="$target/config.yaml"\n', 1)],
    "M6-always-write": [('if path.read_bytes() == updated.encode("utf-8"):', "if False:", 1)],
    "M7-no-dir-check": [(DIR_CHECK, "", 1)],
    "M8-follow-symlink": [('[ -d "$target" ] && [ ! -L "$target" ] || fail', '[ -d "$target" ] || fail', 1)],
    "M9-no-config-check": [(CONF_CHECK, "", 1)],
    "M10-silent-reclone": [('  if [ -e "$target" ]; then\n', '  rm -rf "$target"\n  if [ -e "$target" ]; then\n', 1)],
    "M11-env-resync": [(FROM_SOURCE, '    from="$SOURCE/config.yaml"; cp "$SOURCE/.env" "$target/.env"\n', 1)],
    "M12-refresh-ignores-switch": [(FROM_SOURCE, '    from="$SOURCE/config.yaml"; LANE_DONE_GATE=0\n', 1)],
}
```

## 12. Final mechanical checks (06:5xZ)

```
report_lint: 41 refs — OK 41, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
harness-ports/bin/lane-profile.sh sha256 9b2aa796197009da… (as in section 6): bash -n rc 0
harness-ports/bin/lane-profile.sh: 0
harness-ports/tests/test_lane_profile.sh: 0
tasks/briefs/system1/HCTX1-R1-report.md: 0
```
The lint command: `python3 scripts/report_lint.py tasks/briefs/system1/HCTX1-R1-report.md --min-refs 20` with `--map` for
`lane-profile.sh`, `test_lane_profile.sh`, `pc-lane.sh`, `test_pc_lane.sh`, `hook-shim.sh`, `sync-lane-skills.sh`,
`mcp-server.sh`, `jev-pruner-setup.sh` and `lane-done-gate.py` (their repo paths); `lane-profile.sh@2a50a65:NN` refs are
checked at the PIN. Two lint rounds: the first found one MISS (a reference on the line before its token), fixed. The three
`0` lines are `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>`; the final message repeats the lint and the report's count
after this last write.

The shared tree at this point also holds changes I did not make and did not touch (`git status --short`): `proofs/registry.yaml`,
`scripts/validate-ledger`, `tests/test_validate_ledger.py`, untracked `tests/test_attested_inputs.py` (these read like the
I59-A patch's files), SYNTH1's `scripts/s1_synth.py` and `tests/test_s1_synth.py`, and VERIFY-I59-A's report. None is read by
the lane-profile or pc-lane suites. My changes: `harness-ports/bin/lane-profile.sh`, `harness-ports/tests/test_lane_profile.sh`
and this report.
