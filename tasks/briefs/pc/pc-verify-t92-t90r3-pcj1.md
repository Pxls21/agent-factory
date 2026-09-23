# VERIFY-T92-T90R3-PCJ1 — the batched independent adversarial verify of T92 (the per-lane cloned Hermes profile, D-048), T90-R3 (the RESUME probe's PC-side `$HOME` expansion) and PCJ1's endpoint half (the Laya System One unit), on the PC

PIN: 433d15e (origin; the T92 landing — the code under test. T90-R3 landed in 879c6f9 and PCJ1's endpoint half was graded in 6406750; every boundary file below is byte-identical to 433d15e — the identity table in the premise block. Your worktree starts at the later commit that carries this brief; re-measure the identities there first.)
LANE: pc-verify-t92-t90r3-pcj1
ROLE: adversarial-verifier — the STRICT local route (`HERMES_MODEL=qwen-local/qwen3.8-27b-local`). The contract-gate predicate (D-031): a finding BLOCKS only if contract-mapped · reproduced through the real production path · materially effective · a concrete discriminator · in boundary. Emit ONE GATE RECOMMENDATION PER COMPONENT (`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`) — (A) T92, (B) T90-R3, (C) PCJ1-endpoint — never a verdict; the coordinator owns the gate.
YOU ARE T92'S FIRST PRODUCTION LANE: the PC clone was fast-forwarded to 433d15e before this launch, so the runner that started you cloned your own profile `aflane<your lane id, normalized>` without `fallback_providers` and tags your OmniRoute calls with your lane id. Your own lane is live evidence for item A2 — and it is LIVE: never remove, edit or re-create your own profile.

COMPONENTS + CONTRACTS (frozen; the builders' reports are INPUTS to attack, never evidence):
- (A) T92 — contract `tasks/briefs/pc/pc-t92.md` (build steps 0-5, the gates, mutants m1-m4) + D-048 in `docs/08_DECISION_LOG.md` (the per-lane clone WITHOUT `fallback_providers`, `x-omniroute-session-id` = the lane id, the owner's `agentfactory` profile untouched, a local error fails LOUD). Code: `harness-ports/bin/lane-profile.sh` (NEW, 209 lines), `harness-ports/bin/pc-lane.sh:429-444` + `:511-517`, `scripts/pc_lane.sh:436` onward through the mix lines at `:563`/`:565` (the harvest), `harness-ports/tests/test_lane_profile.sh`, the T92 checks in `harness-ports/tests/test_pc_lane.sh` and `harness-ports/tests/test_pc_lane_dispatcher.sh`. Builder report `tasks/briefs/pc-t90-support/T92-report.md`.
- (B) T90-R3 — contract: VERIFY-T90-R2 F1 (`tasks/briefs/pc-t90-support/VERIFY-T90-R2-report.md`, §F1: a literal `$HOME/agent-factory` lane dir decoded as DATA on the PC never expanded, so a live re-attach read FIRST) + the ledger note `T90-R3 LANDED 2026-09-22 22:0xZ` in `todo/BUILD-TASKLIST.md`. Code: the one clause in the probe at `scripts/pc_lane.sh:211` + the check at `harness-ports/tests/test_pc_lane_dispatcher.sh:316-333`.
- (C) PCJ1 endpoint half — contract `tasks/briefs/pc/pc-jev-laya-pc.md` build steps 1-3 and 7 ONLY + the ledger note `PCJ1 GRADED 2026-09-23 00:1xZ`. Code: `scripts/laya_systemone_server.py`, `tests/test_laya_systemone_server.py`, `harness-ports/bin/laya-server.sh`, the live user unit `laya-systemone.service`. Builder report `tasks/briefs/jev-laya/PCJ1-report.md`. OUT OF SCOPE (the pruner half is PARKED, an owner decision is pending): steps 4-6, `harness-ports/bin/jev-pruner-setup.sh`, anything under `tasks/briefs/jev-laya/parked/`, `~/jev-plugins/` — never run, grade or touch them.

BUDGET: a targeted verify of three landings — scope = the named hunks, their controls and their blast radius on the live dispatch path. Discovery exhaustive inside that scope; no second full sweep of the dispatcher or the runner.

AUTHORIZATION + DO-NOTS (read before any command):
- This is the owner's PC. User-scope only; no sudo. NEVER stop, restart, reload, re-enable, reinstall or edit the `laya-systemone` unit or its unit file, OmniRoute, the vLLM `qwen` container, Ollama, the Buzz relay, or any other server. The Laya endpoint takes reads (`/health`) and single POSTs only; its `calls` counter is a LIVE counter (the coordinator may send requests too), never a premise to match.
- NEVER edit, delete or rename `~/.hermes/profiles/agentfactory/` (read and clone only) or any live lane's profile (the name in a live lane's `.lanes/<id>/profile.txt` — yours included). The ONE profile you may create is a throwaway from lane id `vt132probe<epoch>` (profile `aflanevt132probe<epoch>`), removed by you through `lane-profile.sh remove`; paste `ls ~/.hermes/profiles` before and after.
- NEVER print, cat, grep, diff, head or paste any `.env` content (AF-AP-39): `sha256sum` and `stat -c '%a %U %s'` only. Read a `config.yaml` ONLY through a python yaml parse that prints the keys you name (`fallback_providers` presence, `model.default_headers`, the top-level key set) — never the whole file; a key or credential VALUE never reaches your report.
- Guard probes on `lane-profile.sh remove` run ONLY against a FAKE `HERMES_BIN` (a recorder script that logs its argv and exits 0) and a scratch `HERMES_PROFILES_DIR` — never the real Hermes with any name except your own throwaway.
- call_logs and every Hermes `state.db`: read-only (`sqlite3 -readonly 'file:<db>?mode=ro'`, the SQL in a script file — never inline double quotes, CLAUDE.md), and print only the columns you name.
- Read-only on the lane tree except your report; every mutant and fixture in a scratch copy under `$HOME/tmp-vt132/` (NEVER the PC's tmpfs `/tmp` for trees or basetemps, AF-AP-112); never signal a lane pid (liveness through `/proc` only); kill every process you start BY PID FROM ITS PIDFILE (never `pkill -f`); never commit, push, or touch the ledger, the wiki or any brief. One `terminal` call stays under 420 s.

## Items (each with pasted output; SOLID/UNSURE per observation)

### (A) T92
A1. **Reproduce the landing gates at your worktree** (identities first): `bash harness-ports/tests/test_lane_profile.sh` twice, `bash harness-ports/tests/test_pc_lane_dispatcher.sh` twice (counts bitwise), `bash harness-ports/tests/test_pc_lane.sh` once (alone in its call), `bash harness-ports/tests/run-all.sh` if it fits one call (else say so), `bash -n` on the four shell files, `python3 scripts/no_laya_in_gates.py`. Your lane runs with `HERMES_PROFILE` EXPORTED by the runner (`pc-lane.sh:443`): run `test_lane_profile.sh` and `test_pc_lane.sh` once more under `env -u HERMES_PROFILE` — do the counts agree with the exported run? (`test_pc_lane.sh:18` and `test_pc_lane_dispatcher.sh:8` unset it; `test_lane_profile.sh:7` does not list it — does it need to?)
A2. **Your own lane, read-only:** `cat <your lane dir>/profile.txt`; `bash harness-ports/bin/lane-profile.sh verify <your lane id>` → rc; your profile's config through the yaml parse: `'fallback_providers' in cfg`, `cfg['model']['default_headers']`, the top-level key-set difference against `agentfactory`'s (exactly `{fallback_providers}` removed, nothing added?); `.env` sha equality + `stat -c '%a %U %s'` of both `.env` files; `hooks/` and `cron` present? Then call_logs for YOUR window: rows with `session_tag = '<your lane id>'` by `requested_model × provider × status` with min/max timestamp; rows in your window with `requested_model LIKE 'codex/%'` whose tag is yours (the chain is gone: 0?); how many raw-id rows in your window carry a `conv_…` tag (other, pre-T92 lanes). Any non-200 status in your own rows: what did Hermes and the runner do with it (your lane dir's `lane.log`, the attempt count)?
A3. **The retry-loop branch** (measured by the coordinator, ungraded): the T92 block `pc-lane.sh:429-444` sits INSIDE the attempt loop (`while :; do` :312 … `done` :490), and `:443` exports `HERMES_PROFILE`. On attempt ≥ 2, does the `-n "${HERMES_PROFILE:-}"` branch at :434 run instead — logging `pc-lane: profile override <the lane's own profile>` and skipping `verify`? Reproduce through `test_pc_lane.sh`'s fake-Hermes pattern in a scratch copy (a fake that answers `API call failed after 3 retries: HTTP 503` on attempt 1 and a report on attempt 2, `LANE_CAPACITY_BACKOFF=0`, a fake lane-profile helper that logs each call) and paste both attempts' stderr lines and the helper's call log. Then grade it: the T92 brief step 2 says "run `lane-profile.sh create` and `verify`, then launch" — per launch or per attempt? Does any consumer (the dispatcher's harvest, the monitor greps, a reader of `lane.log`) treat `profile override` as an operator action?
A4. **`lane-profile.sh` shapes** — a scratch fake-Hermes harness in the shape of `test_lane_profile.sh:37-56`, never the real profiles dir:
  (a) **The surviving mutant** (coordinator, measured below): delete the `aflane*[!a-z0-9]*|aflane)` arm at `:195` → the suite stays `9 passed, 0 failed` (the suite tests only `remove agentfactory` and one valid name, `:141-149`). Is the arm load-bearing? Through the RECORDER fake with the arm deleted, which of these reach `hermes profile delete`: `aflane`, `aflane/../agentfactory`, `aflane..`, `aflaneX`, `aflane x`, `aflane*`? Then READ — never run — the installed Hermes profile-delete path (the `hermes` wrapper names its venv; find the delete implementation and the name validation it applies, if any, and paste the lines): does real Hermes refuse a non-alphanumeric name itself, or join it into a path? That decides whether the missing test hides a traversal to the owner's profile or a redundant guard.
  (b) **A half-created profile**: the clone exists but the config rewrite never ran (pre-create the target with the source config) → `create` → rc and message; since nothing in the repository calls `remove` (measured below), what recovers a lane id stuck this way?
  (c) **The source `.env` changes after a lane profile exists** (a key rotation) → `create` for the same lane id (a relaunch or resume) → rc and message; the same recovery question.
  (d) **Header shapes in the source**: `default_headers: {}` (flow style) and a block `default_headers:` that already carries another header → what does `create` write (paste the resulting `model:` block), does `verify` pass, and would Hermes's own config loader read the same header? (A duplicate `default_headers` key parses as the LAST under PyYAML's `safe_load` — name the loader Hermes uses and what it does on a duplicate key.)
  (e) **YAML-hostile lane ids** (`a: b`, `#x`, `'q'`, a leading `-`, a trailing space): `create` writes a valid scalar and `verify` passes? Say whether the dispatcher can produce such an id (lane ids are `<brief file name>--<sha7>`).
  (f) **Name collisions**: two lane ids that differ only in non-alphanumerics (`pc-t9-2.md--abc1234` vs `pc-t92.md--abc1234`) → the second `create` finds the first profile, `verify` fails on the header → refused? The 40-character cut at `:20`: measured below, 0 of the 109 current PC briefs lose a pin-suffix character — grade it as a latent limit or not.
  (g) **Secret copies**: every lane profile holds a full copy of the owner's `.env` and nothing removes a lane profile after its lane. Count the `aflane*` profiles at your start and at your end (names only) and `stat -c '%a %U %s'` each `.env` (mode, owner, size — never content). Is the mode 0600 like the source's? Grade against D-048 and the T92 brief ("disposable clones"): a follow-up or a blocker?
A5. **The live lifecycle, once, with the REAL Hermes**: `ls ~/.hermes/profiles` → `bash harness-ports/bin/lane-profile.sh create vt132probe<epoch>` → `verify` rc 0 → the top-level key-set diff against the source (through the yaml parse) → `bash harness-ports/bin/lane-profile.sh remove aflanevt132probe<epoch>` → gone → `ls ~/.hermes/profiles` equal to the first listing. No `hermes -z` call: your own lane's rows (A2) are the live tag proof.
A6. **The harvest's provider-mix SQL** (`scripts/pc_lane.sh:474-535`) against the REAL call_logs, read-only: copy the heredoc into a scratch script, substitute the variables by hand with (i) your own lane id and window, (ii) `t92live879c6f9` and the window `2026-09-23T00:46:00Z`..`2026-09-23T00:48:00Z` (the T92 lane's live proof: 2 tagged rows); paste the final SQL and its output.
  (a) Do `tagged_lane=1` and the MIX counts equal the rows A2 found?
  (b) MEASURED BY THE COORDINATOR (read-only, ungraded — the block below): over the last 24 h, on the `hermes` key, `requested_model = 'qwen-local/qwen3.8-27b-local'` had 2652 rows; `session_tag IS NULL OR ''` matched 0; `session_tag LIKE 'conv_%'` matched 2650. The `untagged_raw` aggregate (`:486-494`, printed as `untagged-raw-rows=N` at `:553`/`:563`/`:565`) keys on NULL/empty — a shape OmniRoute did not write once in 24 h. Reproduce on your own window, then grade against the T92 brief step 3 ("a second aggregate counts the window's raw-id rows WITHOUT the tag as `untagged-raw-rows=N` (the pre-T92 blindness stays visible)"): is a counter that reads 0 beside thousands of `conv_` rows a hollow counter under that contract? Paste the predicate that would count them.
  (c) Observation: the bounds are `%FT%TZ` (no fraction) and the column is `…T01:17:40.147Z`; as strings, `'.' < 'Z'`, so a row inside the launch second sorts BELOW the lower bound. Material or not?
  (d) The combo path (`MIX_IS_COMBO=1`) keeps the window caveat — confirm unchanged; not re-litigated.
A7. **Blast radius of per-lane state**: a T92 lane's Hermes session lives in `~/.hermes/profiles/aflane<id>/state.db`, no longer in the shared `agentfactory/state.db`. Measured below: no script reads the shared db; `CLAUDE.md` tells the coordinator to key lanes by `sessions.cwd` in the shared db. Confirm: your own session is in your profile's `state.db` and absent from the shared one (count rows by `cwd LIKE '%<your lane id>%'` in both, read-only). Then the T93-R1 interaction: `scripts/t93r1_apply_profile.sh` (OWNER-RUN, not yet applied) appends a `custom_providers:` block to the `agentfactory` config. New lanes clone the current config; a REUSED profile (a resumed lane id) keeps its clone-time config, and `verify` compares only `.env`, never the config against the source. State what a lane resumed across the owner's T93-R1 change would run with.

### (B) T90-R3
B1. **Reproduce the red/green pair**: at your worktree, `test_pc_lane_dispatcher.sh` shows `[PASS] the literal default $HOME lane path is normalized PC-side: …` (A1). Then the discriminating mutant in a scratch copy: replace the clause `case \"\$d\" in '\$HOME'/*) … esac` on `:211` with the no-op `:` — the coordinator ran it (below): `38 passed, 1 failed`, the one FAIL being exactly that check. Re-run it and paste. (Deleting the clause outright leaves `; ;` in the remote command — a SYNTAX kill that reds five checks; the coordinator ran that too. A syntax kill proves nothing about behaviour — AF-AP-78's shape in shell — so the no-op form is the discriminator.)
B2. **The probe's PC-side command, run LOCALLY on this host** (you are on the PC): extract the string handed to `bridge` on `:211` (after the base64 decode) and run it with `d` set to each shape, read-only (it reads the pidfile, `/proc` and `stat`): (a) the LITERAL `$HOME/agent-factory/.lanes/<a live lane id>` (B9 or J1-1 below) → RESUME; (b) the same path expanded → RESUME; (c) `$HOMEX/agent-factory/.lanes/<id>`; (d) `/x/$HOME/…`; (e) `${HOME}/agent-factory/.lanes/<id>` (braces); (f) `$HOME` alone; (g) `~/agent-factory/.lanes/<id>`; (h) a lane dir whose later path segment contains `$HOME` — paste the state per shape, and say which shapes a real dispatch can produce (the default is set at `:142`; an operator may override `PC_AF_REPO`).
B3. **The first production reads** (the coordinator's, sandbox, 2026-09-23 ~01:0xZ, monitor lines pasted below): the re-attach of B9 and J1-1 through the real bridge printed `premise gate skipped — a resume of …` for both. From the PC side, read-only: are those two pidfiles live (`/proc/<pid>` exists — never `kill`), and do their `readlink /proc/<pid>/cwd` and argv match the binding rule the probe applies?
B4. **The side effect** (issue #23, not re-litigated): the PC runner's duplicate-start guard truncates the live lane's `launch.log`. Size and mtime only (never content) of B9's and J1-1's `launch.log`: did the 01:0xZ re-attach truncate them?

### (C) PCJ1 endpoint half
C1. **Reproduce**: `~/venv-laya/bin/python -m pytest tests/test_laya_systemone_server.py -q -p no:cacheprovider --basetemp=$HOME/tmp-vt132/bt1` twice (`mkdir -p $HOME/tmp-vt132` first) and once with `/home/rocco/venv-agent-factory/bin/python` (the tests must not need torch); `bash -n harness-ports/bin/laya-server.sh`; `python3 scripts/ap_screen.py --tests scripts/laya_systemone_server.py tests/test_laya_systemone_server.py` (the flag BEFORE the paths).
C2. **The live endpoint, reads and single requests only**: `harness-ports/bin/laya-server.sh status` and `health`; the PCJ1 brief's smoke batch (its §"The smoke batch", identical bytes) POSTed twice → the three nouls + `fan_out` + `latency_ms`: bitwise-identical answers across the two, and equal to the sandbox reference `{c1: 0.4177, c2: 0.6723, c3: 0.4843}`? `/health` `calls` before and after: +2?
C3. **The HTTP status paths** — the landed tests cover none of them (5 test functions, listed below). One request each against the LIVE endpoint, paste code + body: 404 (`GET /x`, `POST /x`); 400 (content-length 0; malformed JSON; `{}`; `questions: {}`; one question with `type: "bogus"`); 413 (a `Content-Length` above 8 MiB with a short body — `MAX_BODY = 8 * 1024 * 1024` at `:29`; refused on the header, before any read? confirm no hang); a NON-INTEGER `Content-Length: abc` and a NEGATIVE one (`-1`) through a raw socket — `:173` calls `int(...)` unguarded: what does the client get, and does the server still answer the next `/health`? Then the 503/500/502 branches (`:164-165`, `:185-186`, `:195`, `:198`): which are REACHABLE in production? (`main()` returns 3 on a load failure BEFORE it serves, `:216-221` — can `State.agent is None` ever be served?) State each as reachable / unreachable-by-construction.
C4. **The non-loopback refusal** (`:213-215`) runs BEFORE the model load: `~/venv-laya/bin/python scripts/laya_systemone_server.py --host 0.0.0.0 --port <a free port>` → rc 64 + the exact line within a second, and `ss -ltn | grep <port>` empty; the same for a LAN address of this host. `--host localhost` passes the check and would LOAD THE MODEL — do NOT run it; say what `getent hosts localhost` returns here.
C5. **AF-AP-122** (the coordinator's registry row): the unit's ExecStart runs the server from the EPHEMERAL lane worktree `…/.lanes/pc-jev-laya-pc.md--dd4c579/tree/scripts/laya_systemone_server.py`, while `laya-server.sh:5-6` defaults to `$HOME/agent-factory/scripts/…` (measured below). Root-cause which invocation wrote it: read the PCJ1 lane's own commands, read-only, from the SHARED `~/.hermes/profiles/agentfactory/state.db` (that lane predates T92): its sessions by `cwd LIKE '%pc-jev-laya-pc.md--dd4c579%'`, the tool calls whose text contains `laya-server.sh` with `start` or `install`, and any `LAYA_REPO=` / `LAYA_SCRIPT=` — print only those command strings, cut to 300 characters. What happens on the next restart if that tree is removed (`Restart=on-failure`, `StartLimitBurst=3` — read, do NOT restart)? Does anything in `harness-ports/` or `scripts/` remove lane trees (grep)? Grade against the PCJ1 contract, which specified `ExecStart=<venv python> /home/rocco/agent-factory/scripts/laya_systemone_server.py …`. The repair (install refusing a `.lanes/` path + a reinstall from the main clone) is the coordinator's — never run it.
C6. **The unit's other properties, read-only**: the listener is `127.0.0.1:47411` only (`ss -ltnp`); the process uid; `HF_HUB_OFFLINE` and `TRANSFORMERS_OFFLINE` in its environment (`/proc/<pid>/environ` — print ONLY those two names and their values, never the rest); no outbound connection held by the pid (`ss -tnp`); the `StandardOutput=append:` log path and the lines of it containing `"event": "ready"` only.

### Common
D1. `python3 scripts/report_lint.py --min-refs 12 tasks/briefs/pc-t90-support/T92-report.md --root .` and the same on `tasks/briefs/jev-laya/PCJ1-report.md`; `python3 scripts/ap_screen.py --tests harness-ports/bin/lane-profile.sh harness-ports/bin/pc-lane.sh scripts/pc_lane.sh harness-ports/tests/test_lane_profile.sh` — each hit pre-existing or new?

## Report (`tasks/briefs/pc-t90-support/VERIFY-T92-T90R3-PCJ1-report.md`)
DATA, not prose, one section per component: the reproduction table (claim → instrument → observed → SOLID/UNSURE), the shape tables (A4 a-g, B2 a-h, C3), the predicate table (every finding against the five blocking conjuncts), then that component's GATE RECOMMENDATION. A shape you could not run is `NOT run: <reason>`, never omitted. `python3 scripts/report_lint.py --min-refs 15 <your report> --root .` (≤ 3 fix rounds, then paste and finish).

## PREMISE — MEASURED at authoring (2026-09-23T01:24:21Z; sandbox @ 433d15e + the PC over the bridge, read-only)
```
$ for f in <boundary>; do sha256(git show 433d15e:$f)[:16]; lines; done
6f3deca6338bbeb5 209 harness-ports/bin/lane-profile.sh
160d2ce0b22b4cee 529 harness-ports/bin/pc-lane.sh
516c48acff3cd281 609 scripts/pc_lane.sh
8321d44a46dd3645 152 harness-ports/tests/test_lane_profile.sh
9b52bf810860cc32 641 harness-ports/tests/test_pc_lane.sh
b842d66f6c1f53e9 452 harness-ports/tests/test_pc_lane_dispatcher.sh
cba055a9dc33de21 231 scripts/laya_systemone_server.py
f628ce5adb9d3eaa 117 tests/test_laya_systemone_server.py
cd07b0b5b53355b4 155 harness-ports/bin/laya-server.sh
$ git diff --quiet 433d15e -- harness-ports scripts/pc_lane.sh scripts/laya_systemone_server.py tests/test_laya_systemone_server.py && echo …
tree == 433d15e on the boundary
$ bash harness-ports/tests/test_lane_profile.sh | tail -1
lane profile: 9 passed, 0 failed
$ bash harness-ports/tests/test_pc_lane_dispatcher.sh | tail -1
pc_lane dispatcher: 39 passed, 0 failed
$ /root/venv-agent-factory/bin/python -m pytest tests/test_laya_systemone_server.py -q -p no:cacheprovider --basetemp=/tmp/v132/bt | tail -1
16 passed in 0.03s
$ grep -n '^def test_' tests/test_laya_systemone_server.py
40:def test_pick_device_matrix(requested, cuda_available, free_bytes, expected):
44:def test_chunk_map_accepts_only_a_complete_chunk_list():
67:def test_answer_fans_out_each_named_chunk_without_reusing_batch_state(monkeypatch):
100:def test_answer_falls_back_once_for_a_question_without_a_matching_chunk(monkeypatch):
112:def test_revision_guard_refuses_a_different_snapshot(tmp_path):
(the coordinator's landing grade, sandbox: test_pc_lane.sh `60 passed, 0 failed`; run-all.sh ALL SUITES PASSED)

$ grep -n 'LANE_PROFILE_HELPER=\|profile override\|lane profile create failed\|export HERMES_PROFILE=\|^while :; do\|^done$\|^attempt=0' harness-ports/bin/pc-lane.sh
142:done
215:done
311:attempt=0
312:while :; do
433:  LANE_PROFILE_HELPER="$AF_REPO/harness-ports/bin/lane-profile.sh"
436:    echo "pc-lane: profile override $LANE_PROFILE" >&2
439:    LANE_PROFILE="$("$LANE_PROFILE_HELPER" create "$LANE_ID")" || die "lane profile create failed"
443:  export HERMES_PROFILE="$LANE_PROFILE"
490:done
$ grep -n "session_tag = '\$MIX_LANE_SQL'\|untagged_raw AS\|session_tag IS NULL OR session_tag = ''\|untagged-raw-rows" scripts/pc_lane.sh
483:    AND session_tag = '$MIX_LANE_SQL'
486:), untagged_raw AS (
491:    AND (session_tag IS NULL OR session_tag = '')
553:    echo "pc_lane: provider-mix: no tagged/combo call_logs rows in the window (db=$MIX_DB) | untagged-raw-rows=$MIX_UNTAGGED" >&2
$ sed -n '142p;210p' scripts/pc_lane.sh; the T90-R3 clause on :211
: "${PC_AF_REPO:=\$HOME/agent-factory}"   # expanded PC-side, not here
_PREMISE_LANE_DIR="$PC_AF_REPO/.lanes/$LANE_ID"
case \"\$d\" in '\$HOME'/*) d=\"\$HOME/\${d#'\$HOME'/}\";; esac

$ (scratch copy @433d15e) the :211 clause replaced by ':' — bash -n OK; test_pc_lane_dispatcher.sh
[FAIL] the literal default $HOME lane path is normalized PC-side: a live token-bound pid is RESUME and ships
pc_lane dispatcher: 38 passed, 1 failed
$ (scratch copy @433d15e) the :211 clause DELETED (leaves '; ;' — a syntax kill)
[FAIL] a sibling suffix id is FIRST and refused with no ship write
[FAIL] an argv mention alone is FIRST and refused with no ship write
[FAIL] an argv token equal to the lane dir is RESUME and ships
[FAIL] a live pid bound to this lane returns RESUME with its launch epoch and ships
[FAIL] the literal default $HOME lane path is normalized PC-side: a live token-bound pid is RESUME and ships
pc_lane dispatcher: 34 passed, 5 failed
$ (scratch copy @433d15e) lane-profile.sh:195 'aflane*[!a-z0-9]*|aflane) fail …' deleted — bash -n OK; test_lane_profile.sh
lane profile: 9 passed, 0 failed
$ grep -n 'remove' harness-ports/tests/test_lane_profile.sh
141:REFUSE_OUT="$(bash "$HELPER" remove agentfactory 2>&1)"; REFUSE_RC=$?
144:check "remove refuses a profile without the aflane prefix before the Hermes CLI" $? \
147:REMOVE_OUT="$(bash "$HELPER" remove "$NAME1" 2>&1)"; REMOVE_RC=$?
149:check "remove confirms and deletes an aflane profile" $? \
$ grep -rn 'lane-profile.sh.* remove\|LANE_PROFILE_HELPER" remove\|remove_profile' harness-ports scripts .claude (tests excluded)
harness-ports/bin/lane-profile.sh:192:remove_profile() {
harness-ports/bin/lane-profile.sh:207:  remove) remove_profile "$VALUE";;
$ grep -rln 'agentfactory/state\.db' scripts harness-ports .claude docs CLAUDE.md
docs/INCIDENT-LOG.md
docs/research/prompts/RESEARCH-PROMPT-2.md
CLAUDE.md
$ for b in tasks/briefs/pc/pc-*.md: alnum(lower(name)) + 7 > 40 ?
briefs total: 109 / over: 0   (this brief: 22 alnum characters)
$ grep -n 'CAPACITY_RX=\|PERSIST_RX=' harness-ports/bin/pc-lane.sh
269:CAPACITY_RX='^API call failed after [0-9]+ retries: '
305:PERSIST_RX='^(⚠️ )?No reply: '

$ (PC) sqlite3 -readonly call_logs, the hermes key
shape_3h                 conv_ 409 · other 2   (the 2 = the T92 live proof's tag)
raw_24h_null_or_empty    0
raw_24h_conv             2650
raw_24h_all              2652
other_tags_24h           t92live879c6f9  2  2026-09-23T00:47:11.045Z  2026-09-23T00:47:13.306Z
t92live rows             qwen-local/qwen3.8-27b-local · openai-compatible-chat-98fcb302-… · 200 00:47:11.045Z · 499 00:47:13.306Z
ts_sample                2026-09-23T01:17:40.147Z
raw_status_6h            200 303 · 499 12 · 504 23          (qwen-local/qwen3.8-27b-local)
cloud_6h                 codex/gpt-5.6-sol-xhigh 200 314, 499 2, 502 2 · codex/gpt-5.6-terra-ultra 200 85 · codex/gpt-5.5-xhigh 200 79, 499 2
   (the fallback chain's models; the hermes key is shared with the owner's own sessions, so these rows are NOT all lanes')
$ (PC) ls ~/.hermes/profiles/ ; git -C ~/agent-factory log -1 --format='%h %s'
agentfactory
433d15e7 T92 landed (GATED-PENDING-VERIFY): per-lane cloned Hermes profiles with…
$ (PC) curl -s http://127.0.0.1:47411/health     (calls is a LIVE counter)
{"ok": true, "snapshot": "/home/rocco/hf-laya/hub/models--convaiinnovations--laya/snapshots/1c5edc17a7acd8701df6fc341c0d179f1c62c982", "subfolder": "typed-decisions", "calls": 10, "device": "cpu", "device_reason": "auto: CUDA memory probe failed (CUDA error: out of memory); using CPU", "revision": "1c5edc17a7acd8701df6fc341c0d179f1c62c982"}
$ (PC) systemctl --user is-active laya-systemone.service; systemctl --user cat … | grep ExecStart/Restart/StartLimit/StandardOutput
active
StartLimitIntervalSec=300
StartLimitBurst=3
ExecStart=/home/rocco/venv-laya/bin/python /home/rocco/agent-factory/.lanes/pc-jev-laya-pc.md--dd4c579/tree/scripts/laya_systemone_server.py --device auto --port 47411 --hf-home /home/rocco/hf-laya --threads 8 --revision 1c5edc17a7acd8701df6fc341c0d179f1c62c982 --subfolder typed-decisions
Restart=on-failure
RestartSec=5
StandardOutput=append:/home/rocco/laya-server/server.log
$ (PC) ss -ltn | grep 47411
LISTEN 0      5                        127.0.0.1:47411      0.0.0.0:*
$ (PC) sha256sum <lane-tree server> | cut -c1-16; sha256sum ~/agent-factory/scripts/laya_systemone_server.py | cut -c1-16
cba055a9dc33de21
cba055a9dc33de21
$ sed -n '5,6p' harness-ports/bin/laya-server.sh
LAYA_REPO="${LAYA_REPO:-$HOME/agent-factory}"
LAYA_SCRIPT="${LAYA_SCRIPT:-$LAYA_REPO/scripts/laya_systemone_server.py}"
$ (PC) the two live lanes' pidfiles
pc-b9.md--71463f3 pid=2503514 alive=y
pc-j1-1.md--330803c pid=2967965 alive=y
$ (sandbox monitor, the 01:0xZ re-attach through the real bridge)
[lane-b9] pc_lane: premise gate skipped — a resume of pc-b9.md--71463f3
[lane-j11] pc_lane: premise gate skipped — a resume of pc-j1-1.md--330803c
```
